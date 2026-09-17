# SRCH — openMSX実装抜粋

対応: [v9938_cmd10srch.md](../stage1/docs/v9938_cmd10srch.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/VDPCmdEngine.cc` L819-865

指定色のドット探索。COLと一致(またはARGのEQビットで不一致)する最初のピクセルを見つけたらBDフラグを立てて終了。ライン端に達したらBDを立てずに終了する。

```cpp
/** Search a dot.
  */
void VDPCmdEngine::startSrch(EmuTime time)
{
	vram.cmdReadWindow.setMask(0x3FFFF, ~0u << 18, time);
	vram.cmdWriteWindow.disable(time);
	ASX = SX;
	nextAccessSlot(time);
	setStatusChangeTime(EmuTime::zero()); // we can find it any moment
}

template<typename Mode>
void VDPCmdEngine::executeSrch(EmuTime limit)
{
	uint8_t CL = COL & Mode::COLOR_MASK;
	int TX = (ARG & DIX) ? -1 : 1;
	bool AEQ = (ARG & EQ) != 0; // TODO: Do we look for "==" or "!="?

	// TODO use MXS or MXD here?
	//  datasheet says MXD but MXS seems more logical
	bool srcExt  = (ARG & MXS) != 0;
	bool doPoint = !srcExt || hasExtendedVRAM;
	auto calculator = getSlotCalculator(limit);

	while (!calculator.limitReached()) {
		auto p = [&] -> uint8_t {
			if (doPoint) [[likely]] {
				return Mode::point(vram, ASX, SY, srcExt);
			} else {
				return 0xFF;
			}
		}();
		if ((p == CL) ^ AEQ) {
			status |= BD; // border detected
			commandDone(calculator.getTime());
			break;
		}
		ASX += TX;
		if (ASX & Mode::PIXELS_PER_LINE) {
			// this does NOT reset the BD flag!
			commandDone(calculator.getTime());
			break;
		}
		calculator.next(Delta::D88); // TODO
	}
	engineTime = calculator.getTime();
}
```
