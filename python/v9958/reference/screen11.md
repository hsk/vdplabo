# SCREEN11 — YJK/RGB混在モードのデコード(openMSX実装)

対応: [v9958_screen11.md](../stage1/docs/v9958_screen11.md)

## モード判定

`src/video/BitmapConverter.cc` の `convertLinePlanar()`(GRAPHIC6/7いずれも、YJKとYAEの両方が立っている場合が「SCREEN11」):

```cpp
case DisplayMode::GRAPHIC6 | DisplayMode::YJK | DisplayMode::YAE: // screen 11
case DisplayMode::GRAPHIC7 | DisplayMode::YJK | DisplayMode::YAE:
    renderYAE(subspan<256>(buf), vramPtr0, vramPtr1);
    break;
```

## ピクセルデコード本体

`src/video/BitmapConverter.cc` `renderYAE()`:

```cpp
void BitmapConverter::renderYAE(
        std::span<Pixel, 256> buf,
        std::span<const uint8_t, 128> vramPtr0,
        std::span<const uint8_t, 128> vramPtr1) const
{
    Pixel* __restrict pixelPtr = buf.data();
    for (auto i : xrange(64)) {
        std::array<unsigned, 4> p = {
            vramPtr0[2 * i + 0],
            vramPtr1[2 * i + 0],
            vramPtr0[2 * i + 1],
            vramPtr1[2 * i + 1],
        };
        int j = narrow<int>((p[2] & 7) + ((p[3] & 3) << 3)) - narrow<int>((p[3] & 4) << 3);
        int k = narrow<int>((p[0] & 7) + ((p[1] & 3) << 3)) - narrow<int>((p[1] & 4) << 3);

        for (auto n : xrange(4)) {
            Pixel pix;
            if (p[n] & 0x08) {
                // YAE
                pix = palette16[p[n] >> 4];
            } else {
                // YJK
                int y = narrow<int>(p[n] >> 3);
                auto [r, g, b] = yjk2rgb(y, j, k);
                pix = palette32768[(r << 10) + (g << 5) + b];
            }
            pixelPtr[4 * i + n] = pix;
        }
    }
}
```

`renderYJK()`([screen12.md](screen12.md))とJ/Kの取り出し方は全く同じ。違いは各ピクセルのバイトのbit3(`0x08`)を見て、

- bit3が立っている → そのピクセルは「YJKではなくパレット直接参照」("YAE" = 通常の16色パレットの上位4bit(`p[n] >> 4`)を色番号として使う)
- bit3が立っていない → SCREEN12と同じYJK→RGB変換

をピクセル単位(4ピクセル中1つずつ)で切り替えている。この「一部ピクセルだけ16色パレットに逃がせる」分、YJK専用のSCREEN12(19,268色相当)よりSCREEN11(12,499色相当)の方が理論上の同時発色数が少ない代わりに、輪郭など特定色を正確に出したい部分に地の16色パレットを混ぜられる。

`yjk2rgb()`の定義は[screen12.md](screen12.md)を参照(同一ファイル内で共有)。
