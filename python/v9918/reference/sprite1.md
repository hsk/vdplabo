# スプライトモード1 — `SpriteChecker::checkSprites1` / `SpriteConverter::drawMode1`

openMSXのスプライト処理は「毎ライン、どのスプライトが見えるか・衝突したかを判定するフェーズ(`SpriteChecker`)」と「実際にピクセルへ描くフェーズ(`SpriteConverter`)」に分かれている。V9918のスプライトモード1はどちらも専用の関数(`checkSprites1` / `drawMode1`)を持つ。

## 判定フェーズ — `SpriteChecker::checkSprites1`

出典: `src/video/SpriteChecker.cc` 87-176行目付近(コメントは元コードのまま)

```cpp
inline void SpriteChecker::checkSprites1(int minLine, int maxLine)
{
	// Calculate display line.
	int displayDelta = vdp.getVerticalScroll() - vdp.getLineZero();

	// Get sprites for this line and detect 5th sprite if any.
	bool limitSprites = limitSpritesSetting.getBoolean();
	int size = vdp.getSpriteSize();
	bool mag = vdp.isSpriteMag();
	int magSize = (mag + 1) * size;
	auto attributePtr = vram.spriteAttribTable.getReadArea<32 * 4>(0);
	uint8_t patternIndexMask = size == 16 ? 0xFC : 0xFF;
	int fifthSpriteNum  = -1;  // no 5th sprite detected yet
	int fifthSpriteLine = 999; // larger than any possible valid line

	int sprite = 0;
	for (/**/; sprite < 32; ++sprite) {
		int y = attributePtr[4 * sprite + 0];
		if (y == 208) break; // y=208 は「以降のスプライトは全部非表示」の終端マーカー

		for (int line = minLine; line < maxLine; ++line) {
			int displayLine = line + displayDelta;
			int spriteLine = (displayLine - y) & 0xFF;
			if (spriteLine >= magSize) {
				line += 256 - spriteLine - 1; // 見えないラインはスキップ
				continue;
			}

			auto visibleIndex = spriteCount[line];
			if (visibleIndex == 4) {
				// 5th sprite: このラインでは5枚目以降は原則描画しない
				if (line < fifthSpriteLine) {
					fifthSpriteLine = line;
					fifthSpriteNum = sprite;
				}
				if (limitSprites) continue;
			}

			SpriteInfo& sip = spriteBuffer[line][visibleIndex];
			int patternIndex = attributePtr[4 * sprite + 2] & patternIndexMask;
			if (mag) spriteLine /= 2;
			sip.pattern = calculatePatternNP(patternIndex, spriteLine);
			sip.x = attributePtr[4 * sprite + 1];
			uint8_t colorAttrib = attributePtr[4 * sprite + 3];
			if (colorAttrib & 0x80) sip.x -= 32; // EC(早期クロック)ビット
			sip.colorAttrib = colorAttrib;

			spriteCount[line] = visibleIndex + 1;
		}
	}

	// ステータスレジスタ(S#0)の更新: 5th sprite番号
	uint8_t status = vdp.getStatusReg0();
	if (fifthSpriteNum != -1) {
		if ((status & 0xC0) == 0) {
			status = uint8_t(0x40 | (status & 0x20) | fifthSpriteNum);
		}
	}
	if (~status & 0x40) {
		status = (status & 0x20) | uint8_t(std::min(sprite, 31));
	}
	vdp.setSpriteStatus(status);

	if (vdp.getStatusReg0() & 0x20) return; // 既に衝突検出済みなら省略可

	// 衝突判定(全ペア総当たり、最大4枚なので最大6ペア)
	bool can0collide = vdp.canSpriteColor0Collide();
	for (auto line : xrange(minLine, maxLine)) {
		int minXCollision = 999;
		for (int i = std::min<int>(4, spriteCount[line]); --i >= 1; /**/) {
			auto color1 = spriteBuffer[line][i].colorAttrib & 0xf;
			if (!can0collide && (color1 == 0)) continue;
			// ...(iとjの全ペアでパターンの重なりをビットANDでチェック)
		}
		if (minXCollision < 256) {
			vdp.setSpriteStatus(vdp.getStatusReg0() | 0x20);
			collisionX = minXCollision + 12;
			collisionY = line - vdp.getLineZero() + 8;
			return;
		}
	}
}
```

## 読み方(判定フェーズ)

- 32枚のスプライト属性テーブル(SAT、`spriteAttribTable`、4バイト×32=128バイト)を先頭から走査し、Y座標が`208`のスプライトで打ち切る(`v9918_sprite1.md`のPhase4で挙げている「Y=208終端」に相当)。
- 1ラインに描画できるのは最大4枚。5枚目以降を検出したら「5th sprite」フラグをステータスレジスタに記録する(Phase2/Phase4の「5th sprite」「1ライン4枚制限」)。
- 衝突判定(collision)はスプライトのパターンをビットANDして重なりを検出する総当たり方式。`色0のスプライトが衝突するか`は`canSpriteColor0Collide()`(チップ個体差がある、[python/v9968のような研究ではなく]実機挙動の細かい違い)。
- 実装はライン単位ではなく「スプライトごとに、見える範囲のラインだけループ」という順序(コメント参照)で、pythonの素朴な「1ラインごとに32枚走査」とは順序が逆だが、結果は同じ。

## 描画フェーズ — `SpriteConverter::drawMode1`

出典: `src/video/SpriteConverter.hh` 92-132行目

```cpp
void drawMode1(int absLine, int minX, int maxX, std::span<Pixel> pixelPtr) const
{
	auto visibleSprites = spriteChecker.getSprites(absLine);
	if (visibleSprites.empty()) return;

	// Render using overdraw.
	for (const auto& si : std::views::reverse(visibleSprites)) {
		Pixel colIndex = si.colorAttrib & 0x0F;
		// Don't draw transparent sprites in sprite mode 1.
		if (colIndex == 0 && transparency) continue;
		Pixel color = palette[colIndex];
		SpriteChecker::SpritePattern pattern = si.pattern;
		int x = si.x;
		if (!clipPattern(x, pattern, minX, maxX)) continue;
		Pixel* p = &pixelPtr[x];
		while (pattern) {
			if (pattern & 0x8000'0000) {
				*p = color;
			}
			pattern <<= 1;
			p++;
		}
	}
}
```

## 読み方(描画フェーズ)

- `std::views::reverse(visibleSprites)` — スプライト番号の**大きい方から**描画する。つまり番号の小さいスプライトほど手前(オーバードローで上書きされない)。SATの並び順=優先順位、という仕様がそのままコードの反復順に出ている。
- 色0(`colIndex == 0`)は`transparency`(R#8のTPビット)が有効なら描画しない。`v9918_sprite1.md`のPhase1に「color 0 transparent」とある通り。
- `pattern`は32bit値で、16x16スプライトなら上位16bitがそのまま16x16パターン(`pattern & 0x8000'0000`のビットを1ドットずつ左シフトしながら判定)。マグニファイ(拡大)は`SpriteChecker`側であらかじめ`doublePattern()`してビットパターンを2倍に引き伸ばしてから渡している(`calculatePatternNP`参照、`SpriteChecker.cc` 45-54行目)。
- 「当たり判定や、ラインごとの表示制限はありません」というpython実装の現状(Phase1)に対し、openMSX実装では判定フェーズ(`checkSprites1`)で4枚制限・5th sprite・衝突を全て処理してから、描画フェーズ(`drawMode1`)は単純に「もう確定した`visibleSprites`を描くだけ」という役割分担になっている。
