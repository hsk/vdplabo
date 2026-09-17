# reference — openMSX実装からのV9938固有コード抜粋

V9938は[buppu3/openMSX](https://github.com/buppu3/openMSX)独自の追加ではなく、本家[openMSX/openMSX](https://github.com/openMSX/openMSX)がもとから完全実装している標準チップ(buppu3 forkの`master`ブランチ == 本家と同一、commit `9aab65445144dacf7488afa080bba8eeed2a9233`)。

そのため「フォークとの差分」ではなく、openMSXの共有VDPソース([src/video/VDPCmdEngine.cc](https://github.com/buppu3/openMSX/blob/master/src/video/VDPCmdEngine.cc) など、TMS9918/V9938/V9958全チップ分の処理が1つのファイルに同居している)から、`!isMSX1VDP()`(MSX1では使えない)かつ`!hasYJK()`(V9958専用ではない = V9938でも動く)の条件で分岐しているコードを人力で抜粋したもの。V9958固有(YJK/YAE)の部分は[../../v9958/reference](../../v9958/reference)側に置く想定。

[python/v9938/stage1/docs/](../stage1/docs/)の各トピックに1:1対応させている。

## VDPコマンド(12種)

| コマンド | ドキュメント | 実装 |
| --- | --- | --- |
| HMMC | [v9938_cmd01hmmc.md](../stage1/docs/v9938_cmd01hmmc.md) | [cmd01hmmc.md](cmd01hmmc.md) |
| YMMM | [v9938_cmd02ymmm.md](../stage1/docs/v9938_cmd02ymmm.md) | [cmd02ymmm.md](cmd02ymmm.md) |
| HMMM | [v9938_cmd03hmmm.md](../stage1/docs/v9938_cmd03hmmm.md) | [cmd03hmmm.md](cmd03hmmm.md) |
| HMMV | [v9938_cmd04hmmv.md](../stage1/docs/v9938_cmd04hmmv.md) | [cmd04hmmv.md](cmd04hmmv.md) |
| LMMC | [v9938_cmd05lmmc.md](../stage1/docs/v9938_cmd05lmmc.md) | [cmd05lmmc.md](cmd05lmmc.md) |
| LMCM | [v9938_cmd06lmcm.md](../stage1/docs/v9938_cmd06lmcm.md) | [cmd06lmcm.md](cmd06lmcm.md) |
| LMMM | [v9938_cmd07lmmm.md](../stage1/docs/v9938_cmd07lmmm.md) | [cmd07lmmm.md](cmd07lmmm.md) |
| LMMV | [v9938_cmd08lmmv.md](../stage1/docs/v9938_cmd08lmmv.md) | [cmd08lmmv.md](cmd08lmmv.md) |
| LINE | [v9938_cmd09line.md](../stage1/docs/v9938_cmd09line.md) | [cmd09line.md](cmd09line.md) |
| SRCH | [v9938_cmd10srch.md](../stage1/docs/v9938_cmd10srch.md) | [cmd10srch.md](cmd10srch.md) |
| PSET | [v9938_cmd11pset.md](../stage1/docs/v9938_cmd11pset.md) | [cmd11pset.md](cmd11pset.md) |
| POINT | [v9938_cmd12point.md](../stage1/docs/v9938_cmd12point.md) | [cmd12point.md](cmd12point.md) |

出典はすべて`src/video/VDPCmdEngine.cc`の`start*`/`execute*`関数ペア(L756-1771)。

## 画面モード・スプライト

| トピック | ドキュメント | 実装 |
| --- | --- | --- |
| Graphic3 (SCREEN4) | [v9938_graphics3.md](../stage1/docs/v9938_graphics3.md) | [graphics3.md](graphics3.md) |
| Graphic4 (SCREEN5) | [v9938_graphics4.md](../stage1/docs/v9938_graphics4.md) | [graphics4.md](graphics4.md) |
| Graphic5 (SCREEN6) | [v9938_graphics5.md](../stage1/docs/v9938_graphics5.md) | [graphics5.md](graphics5.md) |
| Graphic6 (SCREEN7) | [v9938_graphics6.md](../stage1/docs/v9938_graphics6.md) | [graphics6.md](graphics6.md) |
| Graphic7 (SCREEN8) | [v9938_graphics7.md](../stage1/docs/v9938_graphics7.md) | [graphics7.md](graphics7.md) |
| スプライトモード2 | [v9938_sprite2.md](../stage1/docs/v9938_sprite2.md) | [sprite2.md](sprite2.md) |

出典: `src/video/DisplayMode.hh`(モード定数)、`src/video/BitmapConverter.cc`(Graphic4-7描画)、`src/video/CharacterConverter.cc`(Graphic3描画)、`src/video/SpriteChecker.cc`(スプライトモード2判定)。

## 注記

- コードは要点を絞った抜粋であり、全文ではない。行番号は上記コミット時点のもの。
- タイミング(アクセススロット計算)まで含めた正確な移植が必要な場合は、`VDPAccessSlots.cc`・`VDP.hh`のクロック計算部分も別途参照が必要。
