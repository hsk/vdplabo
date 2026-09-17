# YMMM — openMSX実装抜粋

対応: [v9938_cmd02ymmm.md](../stage1/docs/v9938_cmd02ymmm.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/VDPCmdEngine.cc` L1592-1718

High-speed move VRAM -> VRAM (Y方向のみ)。X座標は読み書き共通(ADX)で、Y方向だけSY/DYが独立に進む。1ライン丸ごとコピーするような用途向け。

```cpp
/** High-speed move VRAM -> VRAM (Y direction only).
  */
template<typename Mode>
void VDPCmdEngine::startYmmm(EmuTime time)
{
	vram.cmdReadWindow .setMask(0x3FFFF, ~0u << 18, time);
	vram.cmdWriteWindow.setMask(0x3FFFF, ~0u << 18, time);
	NY &= 1023;
	unsigned tmpNX = clipNX_1_byte<Mode>(DX, 512, ARG);
		// large enough so that it gets clipped
	unsigned tmpNY = clipNY_2(SY, DY, NY, ARG);
	ADX = DX;
	ANX = tmpNX;
	nextAccessSlot(time);
	calcFinishTime(tmpNX, tmpNY, 24 + 40);
	phase = 0;
}

template<typename Mode>
void VDPCmdEngine::executeYmmm(EmuTime limit)
{
	NY &= 1023;
	unsigned tmpNX = clipNX_1_byte<Mode>(DX, 512, ARG);
		// large enough so that it gets clipped
	unsigned tmpNY = clipNY_2(SY, DY, NY, ARG);
	int TX = (ARG & DIX)
		? -Mode::PIXELS_PER_BYTE : Mode::PIXELS_PER_BYTE;
	int TY = (ARG & DIY) ? -1 : 1;
	ANX = clipNX_1_byte<Mode>(ADX, 512, ARG);

	// TODO does this use MXD for both read and write?
	//  it says so in the datasheet, but it seems illogical
	//  OTOH YMMM also uses DX for both read and write
	bool dstExt = (ARG & MXD) != 0;
	bool doPset  = !dstExt || hasExtendedVRAM;
	auto calculator = getSlotCalculator(limit);

	switch (phase) {
	case 0:
loop:		if (calculator.limitReached()) [[unlikely]] { phase = 0; break; }
		if (doPset) [[likely]] {
			tmpSrc = vram.cmdReadWindow.readNP(
			       Mode::addressOf(ADX, SY, dstExt));
		}
		calculator.next(Delta::D24);
		[[fallthrough]];
	case 1:
		if (calculator.limitReached()) [[unlikely]] { phase = 1; break; }
		if (doPset) [[likely]] {
			vram.cmdWrite(Mode::addressOf(ADX, DY, dstExt),
			              tmpSrc, calculator.getTime());
		}
		ADX += TX;
		if (--ANX == 0) {
			// note: going to the next line does not take extra time
			SY += TY; DY += TY; --NY;
			ADX = DX; ANX = tmpNX;
			if (--tmpNY == 0) {
				commandDone(calculator.getTime());
				break;
			}
		}
		calculator.next(Delta::D40);
		goto loop;
	default:
		UNREACHABLE;
	}
	engineTime = calculator.getTime();
	calcFinishTime(tmpNX, tmpNY, 24 + 40);
}
```
