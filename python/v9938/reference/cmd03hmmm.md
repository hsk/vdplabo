# HMMM — openMSX実装抜粋

対応: [v9938_cmd03hmmm.md](../stage1/docs/v9938_cmd03hmmm.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/VDPCmdEngine.cc` L1456-1590

High-speed move VRAM -> VRAM。論理演算(LogOp)なしでバイト単位のブロック転送を行う。読み出し→書き込みの2フェーズをphase 0/1で回す。

```cpp
/** High-speed move VRAM -> VRAM.
  */
template<typename Mode>
void VDPCmdEngine::startHmmm(EmuTime time)
{
	vram.cmdReadWindow .setMask(0x3FFFF, ~0u << 18, time);
	vram.cmdWriteWindow.setMask(0x3FFFF, ~0u << 18, time);
	NY &= 1023;
	unsigned tmpNX = clipNX_2_byte<Mode>(SX, DX, NX, ARG);
	unsigned tmpNY = clipNY_2(SY, DY, NY, ARG);
	ASX = SX;
	ADX = DX;
	ANX = tmpNX;
	nextAccessSlot(time);
	calcFinishTime(tmpNX, tmpNY, 24 + 64);
	phase = 0;
}

template<typename Mode>
void VDPCmdEngine::executeHmmm(EmuTime limit)
{
	NY &= 1023;
	unsigned tmpNX = clipNX_2_byte<Mode>(SX, DX, NX, ARG);
	unsigned tmpNY = clipNY_2(SY, DY, NY, ARG);
	int TX = (ARG & DIX)
	       ? -Mode::PIXELS_PER_BYTE : Mode::PIXELS_PER_BYTE;
	int TY = (ARG & DIY) ? -1 : 1;
	ANX = clipNX_2_byte<Mode>(
		ASX, ADX, ANX << Mode::PIXELS_PER_BYTE_SHIFT, ARG);
	bool srcExt  = (ARG & MXS) != 0;
	bool dstExt  = (ARG & MXD) != 0;
	bool doPoint = !srcExt || hasExtendedVRAM;
	bool doPset  = !dstExt || hasExtendedVRAM;
	auto calculator = getSlotCalculator(limit);

	switch (phase) {
	case 0:
loop:		if (calculator.limitReached()) [[unlikely]] { phase = 0; break; }
		if (doPoint) [[likely]] {
			tmpSrc = vram.cmdReadWindow.readNP(Mode::addressOf(ASX, SY, srcExt));
		} else {
			tmpSrc = 0xFF;
		}
		calculator.next(Delta::D24);
		[[fallthrough]];
	case 1: {
		if (calculator.limitReached()) [[unlikely]] { phase = 1; break; }
		if (doPset) [[likely]] {
			vram.cmdWrite(Mode::addressOf(ADX, DY, dstExt),
			              tmpSrc, calculator.getTime());
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
		calculator.next(delta);
		goto loop;
	}
	default:
		UNREACHABLE;
	}
	engineTime = calculator.getTime();
	calcFinishTime(tmpNX, tmpNY, 24 + 64);
}
```
