# Graphic3 (SCREEN4) — openMSX実装抜粋

対応: [v9938_graphics3.md](../stage1/docs/v9938_graphics3.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/DisplayMode.hh` L33 (`GRAPHIC3 = 0x08`), `src/video/CharacterConverter.cc` L36-84

Graphic3(screen4)はビットマップモードではなく、キャラクタ(パターン+カラーテーブル)ベースのGraphic2(screen2)にスプライトモード2を組み合わせたモード。レンダリング自体はGraphic2用の`renderGraphic2`をそのまま流用しており(コメントに `// graphic3, actually` とある)、Graphic2との違いはVDP側のスプライト回路(sprite2.md参照)とレジスタ解釈だけ。

```cpp
void CharacterConverter::convertLine(std::span<Pixel> buf, int line) const
{
	// TODO: Support YJK on modes other than Graphic 6/7.
	switch (modeBase) {
	case DisplayMode::GRAPHIC1:   // screen 1
		renderGraphic1(subspan<256>(buf), line);
		break;
	case DisplayMode::TEXT1:      // screen 0, width 40
		renderText1(subspan<256>(buf), line);
		break;
	case DisplayMode::MULTICOLOR: // screen 3
		renderMulti(subspan<256>(buf), line);
		break;
	case DisplayMode::GRAPHIC2:   // screen 2
		renderGraphic2(subspan<256>(buf), line);
		break;
	case DisplayMode::GRAPHIC3:   // screen 4
		renderGraphic2(subspan<256>(buf), line); // graphic3, actually
		break;
	case  DisplayMode::TEXT2:     // screen 0, width 80
		renderText2(subspan<512>(buf), line);
		break;
	// ...(以下MSX1専用モード)
	}
}
```
