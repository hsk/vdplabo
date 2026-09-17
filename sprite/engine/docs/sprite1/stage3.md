## 3. sprite1/stage3 について

ステージ3ではVRAMを用いて実装します。

スプライトに関連するVRAMのアドレスはスプライトパターンテーブルとスプライトアトリビュートテーブルがあります。
これらのアドレスをここでは可変にして初期値は以下のようにすることで動作するように修正します。

- スプライトパターンテーブル &H1B00
- スプライトアトリビュートテーブル &H3800

の２つがあります。

## renderSpritesMode1 の機能一覧

- [x] SCREEN1(Graphics1) 向けスプライト描画
- [x] スキャンライン単位描画
- [x] 8x8 スプライト対応
- [x] 16x16 スプライト対応
- [x] スプライト2倍拡大対応
- [x] Sprite Attribute Table(SAT) 対応
- [x] Sprite Generator Table(SGT) 対応
- [x] Y=208 終端対応
- [x] Early Clock(EC/X-32) 対応
- [x] color 0 transparent 対応
- [x] パレットカラー描画
- [x] 横2倍描画対応
- [x] 1ライン4スプライト制限
- [x] 5th Sprite(5S) フラグ対応
- [x] 5th Sprite番号保持
- [ ] スプライト制限解除モード(renderLimitOverSprites)
- [x] スプライト衝突判定(collision)
    - [x] collision flag 設定
- [x] スプライト優先順位管理
- [x] 先着スプライト優先描画
- [x] 16x16時の pattern 番号下位2bit無視
- [x] 16x16 上下分割描画
- [x] 負のX座標対応
- [x] VRAM直接参照描画

### 対象外

- 半横幅描画(MSX2_DISPLAY_HALF_HORIZONTAL) — スプライトモード1の対象外
