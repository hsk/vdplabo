# Graphic6 (SCREEN7) — openMSX実装抜粋

対応: [v9938_graphics6.md](../stage1/docs/v9938_graphics6.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/DisplayMode.hh` L37 (`GRAPHIC6 = 0x14`), `src/video/BitmapConverter.cc` L159-203

512x212、4bit/pixel(16色)だがVRAMがプレーナ配置(偶数/奇数ピクセルが別プレーン`vramPtr0`/`vramPtr1`)になる点がGraphic4と異なる。`convertLinePlanar`経由で呼ばれる。

```cpp
void BitmapConverter::renderGraphic6(
	std::span<Pixel, 512> buf,
	std::span<const uint8_t, 128> vramPtr0,
	std::span<const uint8_t, 128> vramPtr1)
{
	Pixel* __restrict pixelPtr = buf.data();
	if (!dPaletteValid) [[unlikely]] {
		calcDPalette();
	}
	      auto* out = std::bit_cast<DPixel*>(pixelPtr);
	const auto* in0 = std::bit_cast<const unsigned*>(vramPtr0.data());
	const auto* in1 = std::bit_cast<const unsigned*>(vramPtr1.data());
	for (auto i : xrange(512 / 16)) {
		// 16 pixels per iteration
		unsigned data0 = in0[i];
		unsigned data1 = in1[i];
		if constexpr (Endian::BIG) {
			out[8 * i + 0] = dPalette[(data0 >> 24) & 0xFF];
			out[8 * i + 1] = dPalette[(data1 >> 24) & 0xFF];
			out[8 * i + 2] = dPalette[(data0 >> 16) & 0xFF];
			out[8 * i + 3] = dPalette[(data1 >> 16) & 0xFF];
			out[8 * i + 4] = dPalette[(data0 >>  8) & 0xFF];
			out[8 * i + 5] = dPalette[(data1 >>  8) & 0xFF];
			out[8 * i + 6] = dPalette[(data0 >>  0) & 0xFF];
			out[8 * i + 7] = dPalette[(data1 >>  0) & 0xFF];
		} else {
			out[8 * i + 0] = dPalette[(data0 >>  0) & 0xFF];
			out[8 * i + 1] = dPalette[(data1 >>  0) & 0xFF];
			out[8 * i + 2] = dPalette[(data0 >>  8) & 0xFF];
			out[8 * i + 3] = dPalette[(data1 >>  8) & 0xFF];
			out[8 * i + 4] = dPalette[(data0 >> 16) & 0xFF];
			out[8 * i + 5] = dPalette[(data1 >> 16) & 0xFF];
			out[8 * i + 6] = dPalette[(data0 >> 24) & 0xFF];
			out[8 * i + 7] = dPalette[(data1 >> 24) & 0xFF];
		}
	}
}
```
