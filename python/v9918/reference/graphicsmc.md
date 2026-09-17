# マルチカラー(SCREEN3)描画 — `CharacterConverter::renderMulti`

出典: `src/video/CharacterConverter.cc` 318-343行目付近

```cpp
void CharacterConverter::renderMultiHelper(
	Pixel* __restrict pixelPtr, int line,
	unsigned mask, unsigned patternQuarter) const
{
	unsigned baseLine = mask | ((line / 4) & 7);
	unsigned scroll = vdp.getHorizontalScrollHigh();
	auto namePtr = getNamePtr(line, scroll);
	repeat(32, [&] {
		unsigned patternNr = patternQuarter | namePtr[scroll & 0x1F];
		unsigned color = vram.patternTable.readNP((patternNr * 8) | baseLine);
		Pixel cl = palFg[color >> 4];
		Pixel cr = palFg[color & 0x0F];
		pixelPtr[0] = cl; pixelPtr[1] = cl;
		pixelPtr[2] = cl; pixelPtr[3] = cl;
		pixelPtr[4] = cr; pixelPtr[5] = cr;
		pixelPtr[6] = cr; pixelPtr[7] = cr;
		pixelPtr += 8;
		if (!(++scroll & 0x1F)) namePtr = getNamePtr(line, scroll);
	});
}
void CharacterConverter::renderMulti(std::span<Pixel, 256> buf, int line) const
{
	unsigned mask = (~0u << 11);
	renderMultiHelper(buf.data(), line, mask, 0);
}
```

(`renderMultiQ`はTMSxxxx専用のバグ的拡張モードで、`mask = (~0u << 13)`と`patternQuarter`が異なるだけの同じヘルパ呼び出し。MSX1でもV9938以降でも通常使われないため割愛。)

## 読み方

- Graphics1と同じネームテーブル(32×24)・パターンテーブル配置(1キャラ8バイト)を再利用しているのがポイント。`v9918_graphicsmc.md`の「マルチカラーモードはgraphics1モードのネームテーブルと共通な仕様」がそのままコードに表れている。
- `patternTable.readNP((patternNr * 8) | baseLine)` で読む1バイトの上位4bit/下位4bitがそれぞれ左半分/右半分4×4ドットの色(`cl`/`cr`)。`v9918_graphicsmc.md`の「PCG単位で2x8=16色指定」に対応 — 1キャラ(PCG)は8バイトあり、各バイトが2色(高々16色のパレットの中の2色)を指定するので、1PCGあたり最大16通りの色使いができる。
- `baseLine = mask | ((line / 4) & 7)` — 1キャラの縦8バイトのうち、4ライン単位で1バイトを共有する(`line / 4`)。1バイトが縦4ライン×横8ドット(左右2分割で4ドットずつ)を表すため、実際の解像度は64×48相当になる。`v9918_graphicsmc.md`の「4x4ドットを1ピクセルとして64x48のグラフィックス表示」はこの`line/4`と`cl`/`cr`の2分割から導かれる。
- 1キャラの高さ8バイトを「1x8キャラの縦長で1つ」として32×6=192個で1画面、という`v9918_graphicsmc.md`の説明も、ネームテーブルの32×24構成のうち縦方向を4倍圧縮(24÷4=6)して読み替えたもの。
