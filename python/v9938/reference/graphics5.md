# Graphic5 (SCREEN6) — openMSX実装抜粋

対応: [v9938_graphics5.md](../stage1/docs/v9938_graphics5.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/DisplayMode.hh` L36 (`GRAPHIC5 = 0x10`), `src/video/BitmapConverter.cc` L145-157

512x212、1バイトに4ピクセル(2bit/pixel)。2bit値は奇数/偶数ピクセルで別パレット参照(`palette16[0+...]` と `palette16[16+...]`)になっている点がGraphic4/6と異なる特徴。

```cpp
void BitmapConverter::renderGraphic5(
	std::span<Pixel, 512> buf,
	std::span<const uint8_t, 128> vramPtr0) const
{
	Pixel* __restrict pixelPtr = buf.data();
	for (auto i : xrange(128)) {
		unsigned data = vramPtr0[i];
		pixelPtr[4 * i + 0] = palette16[ 0 +  (data >> 6)     ];
		pixelPtr[4 * i + 1] = palette16[16 + ((data >> 4) & 3)];
		pixelPtr[4 * i + 2] = palette16[ 0 + ((data >> 2) & 3)];
		pixelPtr[4 * i + 3] = palette16[16 + ((data >> 0) & 3)];
	}
}
```
