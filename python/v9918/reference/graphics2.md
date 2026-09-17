# Graphics2(SCREEN2)描画 — `CharacterConverter::renderGraphic2`

出典: `src/video/CharacterConverter.cc` 275-317行目付近

```cpp
void CharacterConverter::renderGraphic2(std::span<Pixel, 256> buf, int line) const
{
	int quarter8 = (((line / 8) * 32) & ~0xFF) * 8;
	int line7 = line & 7;
	int scroll = vdp.getHorizontalScrollHigh();
	auto namePtr = getNamePtr(line, scroll);

	Pixel* __restrict pixelPtr = buf.data();
	if (vram.colorTable  .isContinuous((8 * 256) - 1) &&
	    vram.patternTable.isContinuous((8 * 256) - 1) &&
	    ((scroll & 0x1f) == 0)) {
		// Both color and pattern table can be accessed contiguously
		// (no mirroring) and there's no v9958 horizontal scrolling.
		// This is very common, so make an optimized version for this.
		auto patternArea = vram.patternTable.getReadArea<256 * 8>(quarter8);
		auto colorArea   = vram.colorTable  .getReadArea<256 * 8>(quarter8);
		for (auto n : xrange(32)) {
			auto charCode8 = namePtr[n] * 8;
			auto pattern = patternArea[line7 + charCode8];
			auto color   = colorArea  [line7 + charCode8];
			Pixel fg = palFg[color >> 4];
			Pixel bg = palFg[color & 0x0F];
			draw8(pixelPtr, fg, bg, pattern);
		}
	} else {
		// Slower variant, also works when:
		// - there is mirroring in the color table
		// - there is mirroring in the pattern table (TMS9929)
		// - V9958 horizontal scroll feature is used
		unsigned baseLine = (~0u << 13) | quarter8 | line7;
		repeat(32, [&] {
			unsigned charCode8 = namePtr[scroll & 0x1F] * 8;
			unsigned index = charCode8 | baseLine;
			auto pattern = vram.patternTable.readNP(index);
			auto color   = vram.colorTable  .readNP(index);
			Pixel fg = palFg[color >> 4];
			Pixel bg = palFg[color & 0x0F];
			draw8(pixelPtr, fg, bg, pattern);
			if (!(++scroll & 0x1F)) namePtr = getNamePtr(line, scroll);
		});
	}
}
```

## 読み方

- Graphics1との最大の違いは、パターンテーブル/カラーテーブルが「画面の上・中・下の3分割(quarter)」を持つ点。`quarter8 = (((line / 8) * 32) & ~0xFF) * 8` が現在ラインがどのquarterに属するかを算出し、テーブル参照のベースアドレスに加算している。`v9918_graphics2.md`の「パターンネームテーブルは画面の上、中、下で3つに分かれており…8×256×3=6144バイト」という説明そのもの。
- カラーテーブルもパターンテーブルと同じ構造(quarterごとに8×256=2048バイト、キャラクタ1つにつき8バイト=1ラインごとに1バイト)で、`color >> 4` / `color & 0x0F` が各ラインの前景色/背景色。`v9918_graphics2.md`の「色属性テーブルが1パターンあたり8バイトあり各ラインごとに二色」に対応。
- 実装は「高速パス」(テーブルがミラーリングなしで連続配置、かつスクロール0)と「低速パス」(ミラーリングやV9958スクロールがある場合)の2通りに分岐しているが、ロジック自体は同じ。V9918の理解には高速パスだけ追えば十分。
- ネームテーブル(`getNamePtr`)はGraphics1と共通のヘルパを使う(32×24、768バイト)。
