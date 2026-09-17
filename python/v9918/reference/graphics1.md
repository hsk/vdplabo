# Graphics1(SCREEN1)描画 — `CharacterConverter::renderGraphic1`

出典: `src/video/CharacterConverter.cc` 255-271行目付近

呼び出し元の分岐(同ファイル 42-80行目、`convertLine`):

```cpp
switch (modeBase) {
case DisplayMode::GRAPHIC1:   // screen 1
	renderGraphic1(subspan<256>(buf), line);
	break;
```

本体:

```cpp
void CharacterConverter::renderGraphic1(std::span<Pixel, 256> buf, int line) const
{
	auto patternArea = vram.patternTable.getReadArea<256 * 8>(0);
	auto l = line & 7;
	auto colorArea = vram.colorTable.getReadArea<256 / 8>(0);

	int scroll = vdp.getHorizontalScrollHigh();
	auto namePtr = getNamePtr(line, scroll);
	Pixel* __restrict pixelPtr = buf.data();
	repeat(32, [&] {
		auto charCode = namePtr[scroll & 0x1F];
		auto pattern = patternArea[l + charCode * 8];
		auto color = colorArea[charCode / 8];
		Pixel fg = palFg[color >> 4];
		Pixel bg = palFg[color & 0x0F];
		draw8(pixelPtr, fg, bg, pattern);
		if (!(++scroll & 0x1F)) namePtr = getNamePtr(line, scroll);
	});
}
```

対応する名前テーブル取得(共通ヘルパ):

```cpp
std::span<const uint8_t, 32> CharacterConverter::getNamePtr(int line, int scroll) const
{
	// no need to test whether multi-page scrolling is enabled,
	// indexMask in the nameTable already takes care of it
	return vram.nameTable.getReadArea<32>(
		((line / 8) * 32) | ((scroll & 0x20) ? 0x8000 : 0));
}
```

## 読み方

- `line & 7` — パターン内のライン(0〜7)。8ラインで1キャラクタ。
- 32キャラクタ分を1行のループ(`repeat(32, ...)`)で処理。`namePtr[scroll & 0x1F]`がネームテーブルから読んだキャラクタコード。
- `patternArea[l + charCode * 8]` — パターンテーブルは「キャラクタコード×8バイト」の配置。`v9918_graphics1.md`が言う「256個のPCG、8バイト構成、8×256=2048バイト」と一致。
- `colorArea[charCode / 8]` — カラーテーブルは8キャラクタ単位(1バイトで前景/背景色を1組指定)で、`v9918_graphics1.md`の「PCG単位で2色1バイト」に対応(8キャラ=1グループがcolorTableの1バイトを共有)。
- `color >> 4` / `color & 0x0F` が前景色/背景色のパレットインデックス。
- `draw8` は8ドット分(pattern の各ビット)をfg/bgに展開するヘルパ(同ファイル内、他の描画関数と共通)。
- `scroll`(`getHorizontalScrollHigh()`)はV9958のみ意味を持つ水平スクロール。MSX1では常に0なので実質無視してよい — pythonリファレンス実装がスクロールを持たないのはこのため。
