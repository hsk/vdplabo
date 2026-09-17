# Graphic4 (SCREEN5) — openMSX実装抜粋

対応: [v9938_graphics4.md](../stage1/docs/v9938_graphics4.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/DisplayMode.hh` L35 (`GRAPHIC4 = 0x0C`), `src/video/BitmapConverter.cc` L108-143

256x212、1バイトに2ピクセル(4bit/pixel = 16色)のノンプラナー配置。`dPalette`(16色パレットを2ピクセル分1テーブルにまとめた事前計算テーブル)を使い、8ピクセルずつまとめて変換している。

```cpp
void BitmapConverter::renderGraphic4(
	std::span<Pixel, 256> buf,
	std::span<const uint8_t, 128> vramPtr0)
{
	if (!dPaletteValid) [[unlikely]] {
		calcDPalette();
	}

	Pixel* __restrict pixelPtr = buf.data();
	      auto* out = std::bit_cast<DPixel*>(pixelPtr);
	const auto* in  = std::bit_cast<const unsigned*>(vramPtr0.data());
	for (auto i : xrange(256 / 8)) {
		// 8 pixels per iteration
		unsigned data = in[i];
		if constexpr (Endian::BIG) {
			out[4 * i + 0] = dPalette[(data >> 24) & 0xFF];
			out[4 * i + 1] = dPalette[(data >> 16) & 0xFF];
			out[4 * i + 2] = dPalette[(data >>  8) & 0xFF];
			out[4 * i + 3] = dPalette[(data >>  0) & 0xFF];
		} else {
			out[4 * i + 0] = dPalette[(data >>  0) & 0xFF];
			out[4 * i + 1] = dPalette[(data >>  8) & 0xFF];
			out[4 * i + 2] = dPalette[(data >> 16) & 0xFF];
			out[4 * i + 3] = dPalette[(data >> 24) & 0xFF];
		}
	}
}
```
