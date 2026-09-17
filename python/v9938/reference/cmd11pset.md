# PSET — openMSX実装抜粋

対応: [v9938_cmd11pset.md](../stage1/docs/v9938_cmd11pset.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/VDPCmdEngine.cc` L780-817

1点描画。DX,DYへCOLの色をLogOp経由で書く、最も単純なコマンド。phase 0で読み、phase 1で書く2段構成。

```cpp
/** Pset
  */
void VDPCmdEngine::startPset(EmuTime time)
{
	vram.cmdReadWindow.disable(time);
	vram.cmdWriteWindow.setMask(0x3FFFF, ~0u << 18, time);
	nextAccessSlot(time);
	setStatusChangeTime(EmuTime::zero()); // will finish soon
	phase = 0;
}

template<typename Mode, typename LogOp>
void VDPCmdEngine::executePset(EmuTime limit)
{
	bool dstExt = (ARG & MXD) != 0;
	bool doPset = !dstExt || hasExtendedVRAM;
	unsigned addr = Mode::addressOf(DX, DY, dstExt);

	switch (phase) {
	case 0:
		if (engineTime >= limit) [[unlikely]] { phase = 0; break; }
		if (doPset) [[likely]] {
			tmpDst = vram.cmdWriteWindow.readNP(addr);
		}
		nextAccessSlot(Delta::D24); // TODO
		[[fallthrough]];
	case 1:
		if (engineTime >= limit) [[unlikely]] { phase = 1; break; }
		if (doPset) [[likely]] {
			uint8_t col = COL & Mode::COLOR_MASK;
			Mode::pset(engineTime, vram, DX, addr, tmpDst, col, LogOp());
		}
		commandDone(engineTime);
		break;
	default:
		UNREACHABLE;
	}
}
```
