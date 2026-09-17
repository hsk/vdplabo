# SCREEN10 — openMSXでは未実装

対応: [v9958_screen10.md](../stage1/docs/v9958_screen10.md)

## 結論

`src/video/BitmapConverter.cc` を見る限り、**SCREEN10(Graphic4/5ベース + YJK)はopenMSXでは描画ロジックが実装されていない**。`convertLine()`/`convertLinePlanar()`のswitch文に明示的なTODOコメント付きでケースが列挙されているが、実際には「ボーガス(不正)モード」として扱われ、`renderBogus()`が呼ばれる。

```cpp
void BitmapConverter::convertLine(std::span<Pixel> buf, std::span<const uint8_t, 128> vramPtr)
{
    switch (mode.getByte()) {
    case DisplayMode::GRAPHIC4: // screen 5
    case DisplayMode::GRAPHIC4 | DisplayMode::YAE:
        renderGraphic4(subspan<256>(buf), vramPtr);
        break;
    case DisplayMode::GRAPHIC5: // screen 6
    case DisplayMode::GRAPHIC5 | DisplayMode::YAE:
        renderGraphic5(subspan<512>(buf), vramPtr);
        break;
    // These are handled in convertLinePlanar().
    case DisplayMode::GRAPHIC6:
    case DisplayMode::GRAPHIC7:
    case DisplayMode::GRAPHIC6 |                    DisplayMode::YAE:
    case DisplayMode::GRAPHIC7 |                    DisplayMode::YAE:
    case DisplayMode::GRAPHIC6 | DisplayMode::YJK:
    case DisplayMode::GRAPHIC7 | DisplayMode::YJK:
    case DisplayMode::GRAPHIC6 | DisplayMode::YJK | DisplayMode::YAE:
    case DisplayMode::GRAPHIC7 | DisplayMode::YJK | DisplayMode::YAE:
        UNREACHABLE; break;
    // TODO: Support YJK on modes other than Graphic 6/7.
    case DisplayMode::GRAPHIC4 | DisplayMode::YJK:
    case DisplayMode::GRAPHIC5 | DisplayMode::YJK:
    case DisplayMode::GRAPHIC4 | DisplayMode::YJK | DisplayMode::YAE:
    case DisplayMode::GRAPHIC5 | DisplayMode::YJK | DisplayMode::YAE:
    default:
        renderBogus(subspan<256>(buf));
        break;
    }
}
```

`GRAPHIC4 | YJK` / `GRAPHIC5 | YJK` / `GRAPHIC4 | YJK | YAE` / `GRAPHIC5 | YJK | YAE` の4パターンがすべて「TODO: Support YJK on modes other than Graphic 6/7.」というコメントの下、`default:` 節の `renderBogus()` に落ちている。

## renderBogus() の中身

```cpp
void BitmapConverter::renderBogus(std::span<Pixel, 256> buf) const
{
    // Verified on real V9958: all bogus modes behave like this, always
    // show palette color 15.
    // When this is in effect, the VRAM is not refreshed anymore, but that
    // is not emulated.
    std::ranges::fill(buf, palette16[15]);
}
```

コメントによれば、これは実機のV9958でも確認された挙動で、SCREEN10相当のモードでは常にパレット色15で塗りつぶされる(実機ではVRAMリフレッシュも止まるが、そこまではエミュレートされていない)。

## このプロジェクトの既存メモとの整合性について

[v9958.md](../stage1/docs/v9958.md)には「SCREEN10はSCREEN5の拡張版」という記述があり、`GRAPHIC4`(Screen5)ベース + YJK という理解と一致する。ただしopenMSX側はこの組み合わせを「未対応/実機でも事実上使えないモード」として扱っている点は、Python実装を作る際に踏まえておく価値がある(実機のSCREEN10が本当にこの通りかは要出典確認)。
