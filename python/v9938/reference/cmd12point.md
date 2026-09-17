# POINT — openMSX実装抜粋

対応: [v9938_cmd12point.md](../stage1/docs/v9938_cmd12point.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/VDPCmdEngine.cc` L756-778

1点読み取り。SX,SYの色をCOLレジスタへ読み込むだけの最も単純なコマンド。書き込みは行わない。

```cpp
/** Point
  */
void VDPCmdEngine::startPoint(EmuTime time)
{
	vram.cmdReadWindow.setMask(0x3FFFF, ~0u << 18, time);
	vram.cmdWriteWindow.disable(time);
	nextAccessSlot(time);
	setStatusChangeTime(EmuTime::zero()); // will finish soon
}

template<typename Mode>
void VDPCmdEngine::executePoint(EmuTime limit)
{
	if (engineTime >= limit) [[unlikely]] return;

	bool srcExt  = (ARG & MXS) != 0;
	if (bool doPoint = !srcExt || hasExtendedVRAM; doPoint) [[likely]] {
		COL = Mode::point(vram, SX, SY, srcExt);
	} else {
		COL = 0xFF;
	}
	commandDone(engineTime);
}
```
