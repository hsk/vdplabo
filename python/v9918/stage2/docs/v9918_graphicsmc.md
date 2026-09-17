# v9918_graphicsmc.py について

マルチカラーモードの簡易的リファレンス実装です。
4x4ドットを1ピクセルとして64x48のグラフィックス表示ができます。
パレットは固定で、PCGは256個あり色はPCG単位で2x8=16色指定できます。
マルチカラーモードはgraphics1モードのネームテーブルと共通な仕様で作れるように設計されています。
PCGは1x8キャラの縦長で１つとなり、32x6=192個のPCGで1画面を構成します。
各PCGは8バイトで構成されており、グラフィックス１モードと共通です。

このステージでは1ラインごとに描画します。

```python
    def render_graphicsmc(self, surface):
        for cy in range(self.ROWS):
            for cx in range(self.COLS):
```

を以下のように書き換えただけで難しいことは何もありません。

```python
    def render_graphics1(self, surface):
        for cy in range(self.ROWS):
            for cx in range(self.COLS):
```

を以下のように書き換え

```python
    def render_graphics1(self, surface):
        for y in range(self.SCREEN_HEIGHT):
            self.render_line_graphics1(surface, y)
    def render_line_graphics1(self, surface, y):
        cy = y // 8
        py = y % 8
```

pyのこのループを消します:

```
    for py in range(8):
```

グラフィックスモードやテキストモードは基本的に簡単な書き換えで済みます。
