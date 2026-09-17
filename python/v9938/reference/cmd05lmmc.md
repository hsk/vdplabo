# LMMC — openMSX実装抜粋

対応: [v9938_cmd05lmmc.md](../stage1/docs/v9938_cmd05lmmc.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/VDPCmdEngine.cc` L1291-1350

Logical move CPU -> VRAM。CPUがCOLレジスタに1ピクセル分書き込むたびに`transfer`が立ち、LogOpを適用してVRAMへ1ピクセルずつ書き込む。`transfer = true`にしない特殊な理由がコメントに書かれている(bug#1014対策)。

```cpp
/** Logical move CPU -> VRAM.
  */
template<typename Mode>
void VDPCmdEngine::startLmmc(EmuTime time)
{
	vram.cmdReadWindow.disable(time);
	vram.cmdWriteWindow.setMask(0x3FFFF, ~0u << 18, time);
	NY &= 1023;
	unsigned tmpNX = clipNX_1_pixel<Mode>(DX, NX, ARG);
	ADX = DX;
	ANX = tmpNX;
	setStatusChangeTime(EmuTime::zero());
	// do not set 'transfer = true', this fixes bug#1014
	// Baltak Rampage: characters in greetings part are one pixel offset
	status |= TR;
	nextAccessSlot(time);
}

template<typename Mode, typename LogOp>
void VDPCmdEngine::executeLmmc(EmuTime limit)
{
	NY &= 1023;
	unsigned tmpNX = clipNX_1_pixel<Mode>(DX, NX, ARG);
	unsigned tmpNY = clipNY_1(DY, NY, ARG);
	int TX = (ARG & DIX) ? -1 : 1;
	int TY = (ARG & DIY) ? -1 : 1;
	ANX = clipNX_1_pixel<Mode>(ADX, ANX, ARG);
	bool dstExt = (ARG & MXD) != 0;
	bool doPset  = !dstExt || hasExtendedVRAM;

	if (transfer) {
		uint8_t col = COL & Mode::COLOR_MASK;
		// TODO: timing is inaccurate, this executes the read and write
		//  in the same access slot. Instead we should
		//    - wait for a byte
		//    - in next access slot read
		//    - in next access slot write
		if (doPset) [[likely]] {
			unsigned addr = Mode::addressOf(ADX, DY, dstExt);
			tmpDst = vram.cmdWriteWindow.readNP(addr);
			Mode::pset(limit, vram, ADX, addr,
			           tmpDst, col, LogOp());
		}
		// Execution is emulated as instantaneous, so don't bother
		// with the timing.
		// Note: Correct timing would require currentTime to be set
		//       to the moment transfer becomes true.
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
