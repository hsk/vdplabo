# SCREEN12 — 純YJKモードのデコード(openMSX実装)

対応: [v9958_screen12.md](../stage1/docs/v9958_screen12.md)

## モード判定

`src/video/DisplayMode.hh`(YJK/YAEフラグのエンコード。R#25のbit3=YJK, bit4=YAEを、モードバイトのbit5(YJK)/bit6(YAE)に詰め替えている):

```cpp
static constexpr uint8_t YJK = 0x20;
static constexpr uint8_t YAE = 0x40;
```

`src/video/BitmapConverter.cc` の `convertLinePlanar()`(GRAPHIC6/7いずれも、YJKのみ立っていてYAEが立っていない場合が「SCREEN12」):

```cpp
case DisplayMode::GRAPHIC6 | DisplayMode::YJK: // screen 12
case DisplayMode::GRAPHIC7 | DisplayMode::YJK:
    renderYJK(subspan<256>(buf), vramPtr0, vramPtr1);
    break;
```

## ピクセルデコード本体

`src/video/BitmapConverter.cc` `renderYJK()`:

```cpp
void BitmapConverter::renderYJK(
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
            int y = narrow<int>(p[n] >> 3);
            auto [r, g, b] = yjk2rgb(y, j, k);
            int col = (r << 10) + (g << 5) + b;
            pixelPtr[4 * i + n] = palette32768[col];
        }
    }
}
```

4バイト(`vramPtr0`/`vramPtr1`の各2バイトずつ、プレーナ配置)から4ピクセル分の (Y, J, K) を取り出す形。各バイトの上位5bit(`>> 3`)がYで4ピクセル分それぞれ独立、下位3bitとその隣のバイトの下位2bit(符号拡張つき)を組み合わせてJ, Kを1組だけ算出し、4ピクセルで共有する。

## YJK→RGB変換

同ファイルの `yjk2rgb()`(ファイル内 static 関数):

```cpp
static constexpr std::tuple<int, int, int> yjk2rgb(int y, int j, int k)
{
    // Note the formula for 'blue' differs from the 'traditional' formula
    // (e.g. as specified in the V9958 datasheet) in the rounding behavior.
    // Confirmed on real turbor machine. For details see:
    //    https://github.com/openMSX/openMSX/issues/1394
    //    https://twitter.com/mdpc___/status/1480432007180341251?s=20
    int r = std::clamp(y + j,                       0, 31);
    int g = std::clamp(y + k,                       0, 31);
    int b = std::clamp((5 * y - 2 * j - k + 2) / 4, 0, 31);
    return {r, g, b};
}
```

コメントの通り、B成分の式はV9958データシート記載の式と丸め方が異なり、実機(turbo R)で確認した値に合わせてあるとのこと。素朴な `(5y - 2j - k) / 4` ではなく `+2` の補正が入っている点に注意。
