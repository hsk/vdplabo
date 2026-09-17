# LMMM — openMSX実装抜粋

対応: [v9938_cmd07lmmm.md](../stage1/docs/v9938_cmd07lmmm.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/VDPCmdEngine.cc` L1091-1238

Logical move VRAM -> VRAM。SX/SYからNX/NY分読み込み、LogOpを適用してDX/DYへピクセル単位でコピーする(HMMMのバイト単位版に対しこちらはピクセル単位)。

```cpp
/** Logical move VRAM -> VRAM.
  */
template<typename Mode>
void VDPCmdEngine::startLmmm(EmuTime time)
{
	vram.cmdReadWindow .setMask(0x3FFFF, ~0u << 18, time);
	vram.cmdWriteWindow.setMask(0x3FFFF, ~0u << 18, time);
	NY &= 1023;
	unsigned tmpNX = clipNX_2_pixel<Mode>(SX, DX, NX, ARG);
	unsigned tmpNY = clipNY_2(SY, DY, NY, ARG);
	ASX = SX;
	ADX = DX;
	ANX = tmpNX;
	nextAccessSlot(time);
	calcFinishTime(tmpNX, tmpNY, 64 + 32 + 24);
	phase = 0;
}

template<typename Mode, typename LogOp>
void VDPCmdEngine::executeLmmm(EmuTime limit)
{
	NY &= 1023;
	unsigned tmpNX = clipNX_2_pixel<Mode>(SX, DX, NX, ARG);
	unsigned tmpNY = clipNY_2(SY, DY, NY, ARG);
	int TX = (ARG & DIX) ? -1 : 1;
	int TY = (ARG & DIY) ? -1 : 1;
	ANX = clipNX_2_pixel<Mode>(ASX, ADX, ANX, ARG);
	bool srcExt  = (ARG & MXS) != 0;
	bool dstExt  = (ARG & MXD) != 0;
	bool doPoint = !srcExt || hasExtendedVRAM;
	bool doPset  = !dstExt || hasExtendedVRAM;
	unsigned dstAddr = Mode::addressOf(ADX, DY, dstExt);
	auto calculator = getSlotCalculator(limit);

	switch (phase) {
	case 0:
loop:		if (calculator.limitReached()) [[unlikely]] { phase = 0; break; }
		if (doPoint) [[likely]] {
		       tmpSrc = Mode::point(vram, ASX, SY, srcExt);
		} else {
		       tmpSrc = 0xFF;
		}
		calculator.next(Delta::D32);
		[[fallthrough]];
	case 1:
		if (calculator.limitReached()) [[unlikely]] { phase = 1; break; }
		if (doPset) [[likely]] {
			tmpDst = vram.cmdWriteWindow.readNP(dstAddr);
		}
		calculator.next(Delta::D24);
		[[fallthrough]];
	case 2: {
		if (calculator.limitReached()) [[unlikely]] { phase = 2; break; }
		if (doPset) [[likely]] {
			Mode::pset(calculator.getTime(), vram, ADX, dstAddr,
			           tmpDst, tmpSrc, LogOp());
		}
		ASX += TX; ADX += TX;
		Delta delta = Delta::D64;
		if (--ANX == 0) {
			delta = Delta::D128; // 64 + 64
			SY += TY; DY += TY; --NY;
			ASX = SX; ADX = DX; ANX = tmpNX;
			if (--tmpNY == 0) {
				commandDone(calculator.getTime());
				break;
			}
		}
		dstAddr = Mode::addressOf(ADX, DY, dstExt);
		calculator.next(delta);
		goto loop;
	}
	default:
		UNREACHABLE;
	}
	engineTime = calculator.getTime();
	this->calcFinishTime(tmpNX, tmpNY, 64 + 32 + 24);
}
```
