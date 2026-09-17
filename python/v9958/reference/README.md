# reference — openMSXのV9958実装からのコード抜粋

[stage1](../stage1)のドキュメントに対応する形で、openMSXの実ソースからV9958固有(V9938に対する差分)のロジックを抜粋したもの。

- 取得元: [buppu3/openMSX](https://github.com/buppu3/openMSX) の `master` ブランチ(V9968改造前のベース。本家 [openMSX/openMSX](https://github.com/openMSX/openMSX) の実装とほぼ同一)
- コミット: `9aab65445144dacf7488afa080bba8eeed2a9233`
- 抽出方針: `hasYJK()`(`src/video/VDP.hh`、`(version & VM_YJK) != 0`)で分岐しているコード、およびそれに伴うYJK/YAEモードのピクセルデコード処理のみを対象とし、V9938のコマンドエンジン本体などV9958固有でない部分は含めない。

## 内容

| ファイル | 対応する既存ドキュメント | 内容 |
| --- | --- | --- |
| [screen12.md](screen12.md) | [v9958_screen12.md](../stage1/docs/v9958_screen12.md) | `renderYJK` — 純YJK(19,268色相当)のピクセルデコード |
| [screen11.md](screen11.md) | [v9958_screen11.md](../stage1/docs/v9958_screen11.md) | `renderYAE` — YJK/RGB混在(12,499色相当)のピクセルデコード |
| [screen10.md](screen10.md) | [v9958_screen10.md](../stage1/docs/v9958_screen10.md) | **openMSXでは未実装**であることが判明。理由と該当コードのメモ |
| [overview.md](overview.md) | [v9958.md](../stage1/docs/v9958.md) | YJK/YAE以外のV9958固有機能(非Graphicモードでのコマンド実行、ボーダーマスク、水平位置調整) |

## 重要な発見

`src/video/BitmapConverter.cc` の`switch`文とTODOコメントから、**SCREEN10(Graphic4/5ベース + YJK)はopenMSXでは未実装**で、実機のバグ的動作(`renderBogus` = 常にパレット色15で塗りつぶし)として扱われていることが分かった。詳細は[screen10.md](screen10.md)を参照。
