## 3. sprite1/stage3 について

ステージ3ではVRAMを用いて実装します。

スプライトに関連するVRAMのアドレスはスプライトパターンテーブルとスプライトアトリビュートテーブルがあります。
これらのアドレスをここでは可変にして初期値は以下のようにすることで動作するように修正します。

- スプライトパターンテーブル &H1B00
- スプライトアトリビュートテーブル &H3800

の２つがあります。

## renderSpritesMode1 の機能一覧

SCREEN1(Graphics1)向けに、VRAM上のSAT/SGTを参照するscanlineレンダラーとして
以下を実装済み: 8x8/16x16スプライト、2倍拡大(縦横とも)、パレットカラー描画、
1ライン4スプライト制限、5th Sprite(5S)フラグとその番号保持、スプライト衝突判定
(collision flag)、スプライト優先順位管理(先着優先描画)、16x16時のpattern番号
下位2bit無視と上下分割描画、Y=208終端、Early Clock(EC/X-32)、負のX座標対応、
color 0 transparent、VRAM直接参照描画。

### 未実装

- スプライト制限解除モード(renderLimitOverSprites)

### 対象外

- 半横幅描画(MSX2_DISPLAY_HALF_HORIZONTAL) — スプライトモード1の対象外
