# スプライトモード2 — openMSX実装抜粋

対応: [v9938_sprite2.md](../stage1/docs/v9938_sprite2.md)

出典: [buppu3/openMSX](https://github.com/buppu3/openMSX) `master` ブランチ(本家openMSXと同一、commit `9aab6544`)
`src/video/SpriteChecker.cc` L245-481(`checkSprites1`=MSX1スプライトモード1と対になる、V9938以降のモード2実装)

MSX1のモード1(`checkSprites1`)との主な違い:
- カラーテーブルからスプライト単位・ライン単位で色を1バイト読む(`colorAttrib`。上位ビットにCC/IC、下位4bitが色)
- CCビット(colorAttrib & 0x60 の一部)が立つ場合は直前のスプライトの色とOR合成、衝突判定からも除外
- 512色パレット・プラナー配置対応のため、通常VRAM用/プラナーVRAM用の2経路(`planar`分岐)を持つ
- 9枚目スプライト検出(`ninthSpriteNum`)や衝突判定(`can0collide`)はモード1と共通ロジック

```cpp
inline void SpriteChecker::checkSprites2(int minLine, int maxLine)
{
	// Calculate display line.
	int displayDelta = vdp.getVerticalScroll() - vdp.getLineZero();

	// Get sprites for this line and detect 5th sprite if any.
	bool limitSprites = limitSpritesSetting.getBoolean();
	int size = vdp.getSpriteSize();
	bool mag = vdp.isSpriteMag();
	int magSize = (mag + 1) * size;
	int patternIndexMask = (size == 16) ? 0xFC : 0xFF;
	int ninthSpriteNum  = -1;  // no 9th sprite detected yet
	int ninthSpriteLine = 999; // larger than any possible valid line

	// Because it gave a measurable performance boost, we duplicated the
	// code for planar and non-planar modes.
	int sprite = 0;
	if (planar) {
		auto [attributePtr0, attributePtr1] =
			vram.spriteAttribTable.getReadAreaPlanar<32 * 4>(512);
		for (/**/; sprite < 32; ++sprite) {
			int y = attributePtr0[2 * sprite + 0];
			if (y == 216) break;

			for (int line = minLine; line < maxLine; ++line) {
				int displayLine = line + displayDelta;
				int spriteLine = (displayLine - y) & 0xFF;
				if (spriteLine >= magSize) {
					line += 256 - spriteLine - 1;
					continue;
				}

				auto visibleIndex = spriteCount[line];
				if (visibleIndex == 8) {
					if (line < ninthSpriteLine) {
						ninthSpriteLine = line;
						ninthSpriteNum = sprite;
					}
					if (limitSprites) continue;
				}

				if (mag) spriteLine /= 2;
				unsigned colorIndex = (~0u << 10) | (sprite * 16 + spriteLine);
				uint8_t colorAttrib =
					vram.spriteAttribTable.readPlanar(colorIndex);

				SpriteInfo& sip = spriteBuffer[line][visibleIndex];
				int patternIndex = attributePtr0[2 * sprite + 1] & patternIndexMask;
				sip.pattern = calculatePatternPlanar(patternIndex, spriteLine);
				sip.x = attributePtr1[2 * sprite + 0];
				if (colorAttrib & 0x80) sip.x -= 32;
				sip.colorAttrib = colorAttrib;

				spriteBuffer[line][visibleIndex + 1].colorAttrib = 0;
				spriteCount[line] = visibleIndex + 1;
			}
		}
	} else {
		// ...non-planar版は同ロジック(vram.spriteAttribTable.readNP()を使用)
	}

	// Update status register.
	uint8_t status = vdp.getStatusReg0();
	if (ninthSpriteNum != -1) {
		if ((status & 0xC0) == 0) {
			status = uint8_t(0x40 | (status & 0x20) | ninthSpriteNum);
		}
	}
	if (~status & 0x40) {
		status = (status & 0x20) | uint8_t(std::min(sprite, 31));
	}
	vdp.setSpriteStatus(status);

	if (vdp.getStatusReg0() & 0x20) return;

	// 衝突判定: 最大8枚・42ペアを総当たりでチェック
	bool can0collide = vdp.canSpriteColor0Collide();
	for (auto line : xrange(minLine, maxLine)) {
		int minXCollision = 999;
		std::span<SpriteInfo, 32 + 1> visibleSprites = spriteBuffer[line];
		for (int i = std::min<int>(8, spriteCount[line]); --i >= 1; /**/) {
			auto colorAttrib1 = visibleSprites[i].colorAttrib;
			if (!can0collide && ((colorAttrib1 & 0xf) == 0)) continue;
			if (colorAttrib1 & 0x60) continue; // CCまたはICは衝突しない

			int x_i = visibleSprites[i].x;
			SpritePattern pattern_i = visibleSprites[i].pattern;
			for (int j = i; --j >= 0; /**/) {
				auto colorAttrib2 = visibleSprites[j].colorAttrib;
				if (!can0collide && ((colorAttrib2 & 0xf) == 0)) continue;
				if (colorAttrib2 & 0x60) continue;

				int x_j = visibleSprites[j].x;
				int dist = x_j - x_i;
				if ((-magSize < dist) && (dist < magSize)) {
					SpritePattern pattern_j = visibleSprites[j].pattern;
					if (dist < 0) pattern_j <<= -dist; else pattern_j >>= dist;
					SpritePattern colPat = pattern_i & pattern_j;
					if (x_i < 0) colPat &= (1 << (32 + x_i)) - 1;
					if (colPat) {
						int xCollision = x_i + std::countl_zero(colPat);
						minXCollision = std::min(minXCollision, xCollision);
					}
				}
			}
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
