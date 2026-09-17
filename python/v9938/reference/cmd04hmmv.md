# HMMV — openMSX実装抜粋

対応: [v9938_cmd04hmmv.md](../stage1/docs/v9938_cmd04hmmv.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/VDPCmdEngine.cc` L1352-1454

High-speed move VDP -> VRAM。COLレジスタの値をバイト単位で矩形に塗りつぶす(論理演算なし)。

```cpp
/** High-speed move VDP -> VRAM.
  */
template<typename Mode>
void VDPCmdEngine::startHmmv(EmuTime time)
{
	vram.cmdReadWindow.disable(time);
	vram.cmdWriteWindow.setMask(0x3FFFF, ~0u << 18, time);
	NY &= 1023;
	unsigned tmpNX = clipNX_1_byte<Mode>(DX, NX, ARG);
	unsigned tmpNY = clipNY_1(DY, NY, ARG);
	ADX = DX;
	ANX = tmpNX;
	nextAccessSlot(time);
	calcFinishTime(tmpNX, tmpNY, 48);
}

template<typename Mode>
void VDPCmdEngine::executeHmmv(EmuTime limit)
{
	NY &= 1023;
	unsigned tmpNX = clipNX_1_byte<Mode>(DX, NX, ARG);
	unsigned tmpNY = clipNY_1(DY, NY, ARG);
	int TX = (ARG & DIX)
		? -Mode::PIXELS_PER_BYTE : Mode::PIXELS_PER_BYTE;
	int TY = (ARG & DIY) ? -1 : 1;
	ANX = clipNX_1_byte<Mode>(
		ADX, ANX << Mode::PIXELS_PER_BYTE_SHIFT, ARG);
	bool dstExt = (ARG & MXD) != 0;
	bool doPset = !dstExt || hasExtendedVRAM;
	auto calculator = getSlotCalculator(limit);

	while (!calculator.limitReached()) {
		if (doPset) [[likely]] {
			vram.cmdWrite(Mode::addressOf(ADX, DY, dstExt),
			              COL, calculator.getTime());
		}
		ADX += TX;
		Delta delta = Delta::D48;
		if (--ANX == 0) {
			delta = Delta::D104; // 48 + 56;
			DY += TY; --NY;
			ADX = DX; ANX = tmpNX;
			if (--tmpNY == 0) {
				commandDone(calculator.getTime());
				break;
			}
		}
		calculator.next(delta);
	}
	engineTime = calculator.getTime();
	calcFinishTime(tmpNX, tmpNY, 48);
}
```
