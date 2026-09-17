# reference — openMSXの実装から見るV9918(TMS9918A系)固有コード

[buppu3/openMSX](https://github.com/buppu3/openMSX) の `master` ブランチ(= V9968非対応の素の状態。本家 [openMSX/openMSX](https://github.com/openMSX/openMSX) と同一内容、commit `9aab65445144dacf7488afa080bba8eeed2a9233`, 2025-12-07)から、TMS9918A/TMS9928A系(このプロジェクトでの呼称「V9918」= MSX1のVDP)固有のコードを抜粋したもの。

V9918はopenMSXにとって「本家がもとから持つ標準実装」であり、buppu3 fork独自の差分ではない([python/v9968/reference](../../v9968/reference)のV9968 diffとは性質が違う点に注意)。

openMSXは `VDP::isMSX1VDP()` (`src/video/VDP.hh`)でMSX1系チップかどうかを判定し、Graphics1/2/マルチカラー/Text1/スプライトモード1などMSX1由来の描画パスを共通クラス内のswitch/if分岐で実装している。ここではその分岐を辿って、各トピックごとに該当コードを抜き出した。

## トピック

| ファイル | 内容 | 対応する既存ドキュメント |
| --- | --- | --- |
| [overview.md](overview.md) | VDPバージョン判定・MSX1固定パレット生成 | [stage1/docs/v9918.md](../stage1/docs/v9918.md) |
| [graphics1.md](graphics1.md) | Graphics1(SCREEN1)描画 `CharacterConverter::renderGraphic1` | [stage1/docs/v9918_graphics1.md](../stage1/docs/v9918_graphics1.md) |
| [graphics2.md](graphics2.md) | Graphics2(SCREEN2)描画 `CharacterConverter::renderGraphic2` | [stage1/docs/v9918_graphics2.md](../stage1/docs/v9918_graphics2.md) |
| [graphicsmc.md](graphicsmc.md) | マルチカラー(SCREEN3)描画 `CharacterConverter::renderMulti` | [stage1/docs/v9918_graphicsmc.md](../stage1/docs/v9918_graphicsmc.md) |
| [text1.md](text1.md) | Text1(SCREEN0 width40)描画 `CharacterConverter::renderText1` | [stage1/docs/v9918_text1.md](../stage1/docs/v9918_text1.md) |
| [sprite1.md](sprite1.md) | スプライトモード1のチェック・描画 `SpriteChecker::checkSprites1` / `SpriteConverter::drawMode1` | [stage1/docs/v9918_sprite1.md](../stage1/docs/v9918_sprite1.md) |

## 注記

- Graphics1/2/マルチカラー/Text1の描画コード自体はV9938/V9958でも(後方互換モードとして)再利用される共通実装。「MSX1専用」に絞ると`TEXT1Q`/`MULTIQ`(TMSxxxx専用のバグ的モード)や`renderBogus`程度しか残らないため、ここでは「この project が v9918 として研究している機能」を基準にトピックを選んでいる。
- スプライトモード1(`drawMode1`)は他モードと明確に分離された実装で、V9938/V9958でもGraphics1/2/マルチカラー/Text1と組み合わせて使われる。
- コードは理解に必要な範囲を抜粋したもので、全文はopenMSXのソース(`src/video/CharacterConverter.cc`, `src/video/SpriteChecker.cc`, `src/video/SpriteConverter.hh`, `src/video/VDP.cc`, `src/video/VDP.hh`, `src/video/DisplayMode.hh`)を参照。
