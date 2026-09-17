# LINE — openMSX実装抜粋

対応: [v9938_cmd09line.md](../stage1/docs/v9938_cmd09line.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/VDPCmdEngine.cc` L867-964

線分描画(DDA/ブレゼンハム風)。ARGのMAJビットでX/Y主軸方向を切り替え、ASXが誤差蓄積用のカウンタ。実機の挙動(end-test の順序など)についての注記コメントが詳しい。

```cpp
/** Draw a line.
  */
void VDPCmdEngine::startLine(EmuTime time)
{
	vram.cmdReadWindow.disable(time);
	vram.cmdWriteWindow.setMask(0x3FFFF, ~0u << 18, time);
	NY &= 1023;
	ASX = ((NX - 1) >> 1);
	ADX = DX;
	ANX = 0;
	nextAccessSlot(time);
	setStatusChangeTime(EmuTime::zero()); // TODO can still be optimized
	phase = 0;
}

template<typename Mode, typename LogOp>
void VDPCmdEngine::executeLine(EmuTime limit)
{
	// See doc/line-speed.txt for some background info on the timing.
	uint8_t CL = COL & Mode::COLOR_MASK;
	int TX = (ARG & DIX) ? -1 : 1;
	int TY = (ARG & DIY) ? -1 : 1;
	bool dstExt = (ARG & MXD) != 0;
	bool doPset = !dstExt || hasExtendedVRAM;
	unsigned addr = Mode::addressOf(ADX, DY, dstExt);
	auto calculator = getSlotCalculator(limit);

	switch (phase) {
	case 0:
loop:		if (calculator.limitReached()) [[unlikely]] { phase = 0; break; }
		if (doPset) [[likely]] {
			tmpDst = vram.cmdWriteWindow.readNP(addr);
		}
		calculator.next(Delta::D24);
		[[fallthrough]];
	case 1: {
		if (calculator.limitReached()) [[unlikely]] { phase = 1; break; }
		if (doPset) [[likely]] {
			Mode::pset(calculator.getTime(), vram, ADX, addr,
			           tmpDst, CL, LogOp());
		}

		Delta delta = Delta::D88;
		if ((ARG & MAJ) == 0) {
			// X-Axis is major direction.
			ADX += TX;
			// confirmed on real HW:
			//  - end-test happens before DY += TY
			//  - (ADX & PPL) test only happens after first pixel
			//    is drawn. And it does test with 'AND' (not with ==)
			if (ANX++ == NX || (ADX & Mode::PIXELS_PER_LINE)) {
				commandDone(calculator.getTime());
				break;
			}
			if (ASX < NY) {
				ASX += NX;
				DY += TY;
				delta = Delta::D120; // 88 + 32
				// Advancing above the top border stops the command, but
				// advancing below the bottom border wraps to the top.
				// Same for the block commands, but those handle it via
				// clipNY_1() and clipNY_2().
				if ((TY < 0) && (int(DY) < 0)) {
					commandDone(calculator.getTime());
					break;
				}
			}
			ASX -= NY;
			ASX &= 1023; // mask to 10 bits range
		} else {
			// Y-Axis is major direction.
			// confirmed on real HW: DY += TY happens before end-test
			DY += TY;
			if ((TY < 0) && (int(DY) < 0)) { // see comment above
				commandDone(calculator.getTime());
				break;
			}
			if (ASX < NY) {
				ASX += NX;
				ADX += TX;
				delta = Delta::D120; // 88 + 32
			}
			ASX -= NY;
			ASX &= 1023; // mask to 10 bits range
			if (ANX++ == NX || (ADX & Mode::PIXELS_PER_LINE)) {
				commandDone(calculator.getTime());
				break;
			}
		}
		addr = Mode::addressOf(ADX, DY, dstExt);
		calculator.next(delta);
		goto loop;
	}
	default:
		UNREACHABLE;
	}
	engineTime = calculator.getTime();
}
```
