# Text1(SCREEN0 幅40)描画 — `CharacterConverter::renderText1`

出典: `src/video/CharacterConverter.cc` 142-161行目付近

```cpp
void CharacterConverter::renderText1(std::span<Pixel, 256> buf, int line) const
{
	Pixel fg = palFg[vdp.getForegroundColor()];
	Pixel bg = palFg[vdp.getBackgroundColor()];

	// 8 * 256 is small enough to always be contiguous
	auto patternArea = vram.patternTable.getReadArea<256 * 8>(0);
	auto l = (line + vdp.getVerticalScroll()) & 7;

	// Note: Because line width is not a power of two, reading an entire line
	//       from a VRAM pointer returned by readArea will not wrap the index
	//       correctly. Therefore we read one character at a time.
	unsigned nameStart = (line / 8) * 40;
	unsigned nameEnd = nameStart + 40;
	Pixel* __restrict pixelPtr = buf.data();
	for (auto name : xrange(nameStart, nameEnd)) {
		unsigned charCode = vram.nameTable.readNP((name + 0xC00) | (~0u << 12));
		auto pattern = patternArea[l + charCode * 8];
		draw6(pixelPtr, fg, bg, pattern);
	}
}
```

## 読み方

- Graphics系と違い、Text1にはカラーテーブルが無く、前景色/背景色はレジスタ由来の固定値(`vdp.getForegroundColor()` / `getBackgroundColor()`、VDPレジスタ7番)を画面全体で共有する。`v9918_text1.md`の「パレットは固定で、色は2色で指定」に対応(ここでの「固定」は画面全体で2色固定、という意味)。
- ネームテーブルは1行40文字(`nameStart`〜`nameEnd`)、Graphics系の32文字より横に長いのがText1の特徴(SCREEN0)。
- `draw6` はGraphics系の`draw8`と違い6ドット分だけ展開するヘルパ — Text1の1キャラは8×8ドットのパターンのうち左6ドットだけを使う(文字間の2ドットは常に背景色)仕様。
- `vdp.getVerticalScroll()` はY方向スクロールレジスタ(R#23)。MSX1でも実装されている数少ないスクロール機能で、パターン読み出し位置`l`に加算されている。
- パターンテーブルの構造(256キャラ×8バイト)はGraphics1と共通。
