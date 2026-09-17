# HMMC — openMSX実装抜粋

対応: [v9938_cmd01hmmc.md](../stage1/docs/v9938_cmd01hmmc.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/VDPCmdEngine.cc` L1720-1771

High-speed move CPU -> VRAM。COLレジスタではなくCPUからのデータ転送(`transfer`フラグ)で1バイトずつVRAMに書き込む。`startHmmc`でNX/NYのクリップとADX/ANXの初期化、`executeHmmc`は`transfer`が立っている間だけ1バイト書いて次のアクセススロットへ進む。

```cpp
/** High-speed move CPU -> VRAM.
  */
template<typename Mode>
void VDPCmdEngine::startHmmc(EmuTime time)
{
	vram.cmdReadWindow.disable(time);
	vram.cmdWriteWindow.setMask(0x3FFFF, ~0u << 18, time);
	NY &= 1023;
	unsigned tmpNX = clipNX_1_byte<Mode>(DX, NX, ARG);
	ADX = DX;
	ANX = tmpNX;
	setStatusChangeTime(EmuTime::zero());
	// do not set 'transfer = true', see startLmmc()
	status |= TR;
	nextAccessSlot(time);
}

template<typename Mode>
void VDPCmdEngine::executeHmmc(EmuTime limit)
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

	if (transfer) {
		// TODO: timing is inaccurate. We should
		//  - wait for a byte
		//  - on the next access slot write that byte
		if (doPset) [[likely]] {
			vram.cmdWrite(Mode::addressOf(ADX, DY, dstExt),
			              COL, limit);
		}
		transfer = false;

		ADX += TX; --ANX;
		if (ANX == 0) {
			DY += TY; --NY;
			ADX = DX; ANX = tmpNX;
			if (--tmpNY == 0) {
				commandDone(limit);
			}
		}
	}
	nextAccessSlot(limit); // inaccurate, but avoid assert
}
```
