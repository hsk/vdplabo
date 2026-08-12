# スプライト研究 実機サンプルプログラム

このサンプル集の目的は MSX の VDP の動作を確認するための実験プログラム集です。
エミュレータ実装時の検証をしやすいように作ってあります。

## TODO

- [ ] 何も描画されていないラインのORスプライトは表示しない
- [ ] OR用のスプライトがある上に通常スプライトを描画してもORが取られる
  - どんな時かというと、、、？
- [ ] 重ね合わせについて考える
- [ ] 重ね合わせについて実装し対応する
- [ ] tinymsxなどで動かす
- [ ] 参考のベーシックプログラムにダブりがないかチェックする

- スプライト
  - [ ] 8x8
  - [ ] 16x16
  - [ ] 拡大
  - [ ] Early Clock
  - [ ] カラー
  - [ ] オーバー
  - [ ] 衝突
- VRAM
  - [ ] 属性テーブル移動
  - [ ] パターンテーブル移動
  - [ ] ネームテーブル移動
- VDP
  - [ ] STATFL
  - [ ] VDPステータスレジスタ
  - [ ] 割り込み
- BIOS非依存
  - [ ] WRTVRM
  - [ ] LDIRVM
  - [ ] SETWRT
  - [ ] OUTI転送

## BASIC で色々テスト

- [x] [basic/sc1_sp01.bas](basic/sc1_sp01.bas) 8x8の3つのスプライトを表示するプログラム
- [x] [basic/sc1_sp02.bas](basic/sc1_sp02.bas) 当たり判定チェック
- [x] [basic/sc1_sp03.bas](basic/sc1_sp03.bas) スプライト個数制限チェック4個
- [x] [basic/sc5_sp01.bas](basic/sc5_sp01.bas) スプライト個数制限チェック8個
- [x] [basic/sc5_sp02.bas](basic/sc5_sp02.bas) ラインごと色付け
- [x] [basic/sc5_sp03.bas](basic/sc5_sp03.bas) パレット指定
- [x] [basic/sc5_sp04.bas](basic/sc5_sp04.bas)  スプライト２枚重ね合わせ
  - 何も表示されてないラインは描画されない所を気をつけないといけない。
- [x] [basic/sc5_sp05.bas](basic/sc5_sp05.bas) スプライト３枚重ね合わせ
  - ３枚重ねもできますが、何もないラインはやはり描画されない。
- [x] [basic/sc5_sp06.bas](basic/sc5_sp06.bas) スプライト２枚重ね合わせの重ね合わせ
- [x] [basic/sc5_sp07.bas](basic/sc5_sp07.bas) スプライトがチラチラする
  - vpokeを使うと速い

## アセンブラでROMカートリッジのテスト

CBIOSさえあればディスクやBASICのROMがなくても動くので便利
インクルードやライブラリの使用もなくワンソースで動くと密結合になるけど便利かな

- [x] [sc1_sp01.asm](../sprite1/sc1_sp01.asm) 8x8のスプライトを表示 ([解説](sc1_sp01.md))
- [x] [sc1_sp02.asm](../sprite1/sc1_sp01.asm) 8x8の3つのスプライトを表示 ([解説](sc1_sp02.md))
- [x] [sc1_sp03.asm](../sprite1/sc1_sp01.asm) 動かす ([解説](sc1_sp03.md))
- [x] [sc1_sp04.asm](../sprite1/sc1_sp01.asm) 衝突判定 ([解説](sc1_sp04.md))
  - 参考 [ステータスレジスタ0](#status-register-0)
- 5th sprite# (5S4-5S0) 第5(第9)スプライトの番号がセットされる
- [x] [sc1_sp05.asm](../sprite1/sc1_sp05.asm) スプライト個数制限チェック4個 ([解説](sc1_sp05.md))
  - 参考 [basic/sc1_sp03.bas](basic/sc1_sp03.bas)
- [x] [sc1_sp06.asm](../sprite2/sc1_sp06.asm) 一定速度落下アニメーション ([解説](sc1_sp06.md))
- [x] [sc1_sp07.asm](../sprite2/sc1_sp07.asm) 減速付きの落下アニメーション ([解説](sc1_sp07.md))
- [x] [sc1_sp08.asm](../sprite2/sc1_sp08.asm) 大量のスプライトを飛び回らせる ([解説](sc1_sp08.md))
- [x] [sc5_sp01.asm](../sprite2/sc5_sp01.asm) スプライト個数制限チェック8個 ([解説](sc5_sp01.md))
- [x] [sc5_sp02.asm](../sprite2/sc5_sp02.asm) ラインごと色付け ([解説](sc5_sp02.md))
  - 参考 [basic/sc5_sp02.bas](basic/sc5_sp02.bas)
- [x] [sc5_sp03.asm](../sprite2/sc5_sp03.asm) パレット指定 ([解説](sc5_sp03.md))
  - 参考 [basic/sc5_sp03.bas](basic/sc5_sp03.bas)
- [x] [sc5_sp03_2.asm](../sprite2/sc5_sp03_2.asm) パレット指定(OTIR高速転送版) ([解説](sc5_sp03_2.md))
  - 参考 [basic/sc5_sp03_2.bas](basic/sc5_sp03_2.bas)
- [x] [sc5_sp04.asm](../sprite2/sc5_sp04.asm) スプライト2枚重ね合わせ ([解説](sc5_sp04.md))
  - 参考 [basic/asm_sc1_sp04.bas](basic/asm_sc1_sp04.bas)
- [x] [sc5_sp05.asm](../sprite2/sc5_sp05.asm) スプライトオーバー情報の可視化 ([解説](sc5_sp05.md))

## 参考

### Status register 0

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                        |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------------- |
|  S#0 |   F | `5S`|  `C`|`5S4`|`5S3`|`5S2`|`5S1`|`5S0`| Status register 0      |

- F 垂直帰線割り込みフラグ
  S#0を読み出すとリセットされる
- 5S 第5スプライトフラグ
  1水平線上にスプライトが5個(GRAPHIC3～GRAPHIC7モードは9個)並ぶとリセットされる
- C 衝突フラグ
  スプライトが衝突するとセットされる
