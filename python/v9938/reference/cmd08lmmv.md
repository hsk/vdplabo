# LMMV — openMSX実装抜粋

対応: [v9938_cmd08lmmv.md](../stage1/docs/v9938_cmd08lmmv.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/VDPCmdEngine.cc` L967-1089

Logical move VDP -> VRAM。COLレジスタの色をLogOpを介して矩形にピクセル単位で塗る(HMMVのピクセル単位・論理演算あり版)。

```cpp
/** Logical move VDP -> VRAM.
  */
template<typename Mode>
void VDPCmdEngine::startLmmv(EmuTime time)
{
	vram.cmdReadWindow.disable(time);
	vram.cmdWriteWindow.setMask(0x3FFFF, ~0u << 18, time);
	NY &= 1023;
	unsigned tmpNX = clipNX_1_pixel<Mode>(DX, NX, ARG);
	unsigned tmpNY = clipNY_1(DY, NY, ARG);
	ADX = DX;
	ANX = tmpNX;
	nextAccessSlot(time);
	calcFinishTime(tmpNX, tmpNY, 72 + 24);
	phase = 0;
}

template<typename Mode, typename LogOp>
void VDPCmdEngine::executeLmmv(EmuTime limit)
{
	NY &= 1023;
	unsigned tmpNX = clipNX_1_pixel<Mode>(DX, NX, ARG);
	unsigned tmpNY = clipNY_1(DY, NY, ARG);
	int TX = (ARG & DIX) ? -1 : 1;
	int TY = (ARG & DIY) ? -1 : 1;
	ANX = clipNX_1_pixel<Mode>(ADX, ANX, ARG);
	uint8_t CL = COL & Mode::COLOR_MASK;
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
		ADX += TX;
		Delta delta = Delta::D72;
		if (--ANX == 0) {
			delta = Delta::D136; // 72 + 64;
			DY += TY; --NY;
			ADX = DX; ANX = tmpNX;
			if (--tmpNY == 0) {
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
	this->calcFinishTime(tmpNX, tmpNY, 72 + 24);
}
```
