# v9918_graphics1.py について

グラフィックスモード1の簡易的リファレンス実装です。
パレットは固定で、PCGは256個あり色はPCG単位で2色1バイトで指定できます。
各PCGは8バイトで構成されていて、パターンネームテーブルといいます。8x256=2048バイトの領域です。
ネームテーブルは32x24の768バイトで構成され256x192ドットの画面を表示できます。

このステージでは1ラインごとに描画します。

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

さらに最適化をして無駄な計算がないようにしました。

```
    def render_line_graphics1(self, surface, y):
        x = 0
        name = (y // 8) * self.COLS
        py = y % 8
        for _ in range(self.COLS):
            char_no  = self.name_table[name]
            name += 1
            bits     = self.pattern_table[char_no][py]
            color    = self.color_table[char_no]
            fg_color = self.PALETTE[(color >> 4) & 0x0F]
            bg_color = self.PALETTE[color & 0x0F]
            for px in range(8):
                c = fg_color if bits & (0x80 >> px) else bg_color
                surface.set_at((x, y), c)
                x += 1
```
