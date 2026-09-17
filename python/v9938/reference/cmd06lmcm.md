# LMCM — openMSX実装抜粋

対応: [v9938_cmd06lmcm.md](../stage1/docs/v9938_cmd06lmcm.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/VDPCmdEngine.cc` L1240-1289

Logical move VRAM -> CPU。1ピクセルずつVRAMを読み、COLレジスタにセットしてCPUに転送(`transfer`/`TR`ステータス)する。

```cpp
/** Logical move VRAM -> CPU.
  */
template<typename Mode>
void VDPCmdEngine::startLmcm(EmuTime time)
{
	vram.cmdReadWindow.setMask(0x3FFFF, ~0u << 18, time);
	vram.cmdWriteWindow.disable(time);
	NY &= 1023;
	unsigned tmpNX = clipNX_1_pixel<Mode>(SX, NX, ARG);
	ASX = SX;
	ANX = tmpNX;
	transfer = true;
	status |= TR;
	nextAccessSlot(time);
	setStatusChangeTime(EmuTime::zero());
}

template<typename Mode>
void VDPCmdEngine::executeLmcm(EmuTime limit)
{
	if (!transfer) return;
	if (engineTime >= limit) [[unlikely]] return;

	NY &= 1023;
	unsigned tmpNX = clipNX_1_pixel<Mode>(SX, NX, ARG);
	unsigned tmpNY = clipNY_1(SY, NY, ARG);
	int TX = (ARG & DIX) ? -1 : 1;
	int TY = (ARG & DIY) ? -1 : 1;
	ANX = clipNX_1_pixel<Mode>(ASX, ANX, ARG);
	bool srcExt  = (ARG & MXS) != 0;

	// TODO we should (most likely) perform the actual read earlier and
	//  buffer it, and on a CPU-IO-read start the next read (just like how
	//  regular reading from VRAM works).
	if (bool doPoint = !srcExt || hasExtendedVRAM; doPoint) [[likely]] {
		COL = Mode::point(vram, ASX, SY, srcExt);
	} else {
		COL = 0xFF;
	}
	transfer = false;
	ASX += TX; --ANX;
	if (ANX == 0) {
		SY += TY; --NY;
		ASX = SX; ANX = tmpNX;
		if (--tmpNY == 0) {
			commandDone(engineTime);
		}
	}
	nextAccessSlot(limit); // TODO
}
```
