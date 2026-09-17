# Graphic7 (SCREEN8) — openMSX実装抜粋

対応: [v9938_graphics7.md](../stage1/docs/v9938_graphics7.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/DisplayMode.hh` L38 (`GRAPHIC7 = 0x1C`), `src/video/BitmapConverter.cc` L205-215

256x212、1バイト=1ピクセル(8bit、256色固定パレット `palette256`)。プレーナ配置(vramPtr0/vramPtr1が交互列)。Graphic4/5/6のような事前計算パレットテーブルは使わず、1バイト1ピクセルなので単純にインデックス参照するだけ。

```cpp
void BitmapConverter::renderGraphic7(
	std::span<Pixel, 256> buf,
	std::span<const uint8_t, 128> vramPtr0,
	std::span<const uint8_t, 128> vramPtr1) const
{
	Pixel* __restrict pixelPtr = buf.data();
	for (auto i : xrange(128)) {
		pixelPtr[2 * i + 0] = palette256[vramPtr0[i]];
		pixelPtr[2 * i + 1] = palette256[vramPtr1[i]];
	}
}
```
