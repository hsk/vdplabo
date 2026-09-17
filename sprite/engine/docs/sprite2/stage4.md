# sprite2/stage4 について

Phase 4: レジスタ駆動。実装済み。

- [x] sprite size register
- [x] magnify register
- [x] table base register (R#5, R#6, R#11)
- [x] status register (5S, collision, 5th sprite#)
- [x] EC bit
- [x] SPD(スプライト非表示)ビット

## sprite1/stage4との違い

- sprite1(V9918)はSATアドレスをR#5だけで表せたが、sprite2(V9938)は
  VRAMが最大128KBまで拡張されているため、R#5(下位)とR#11(上位)の
  2レジスタでSATアドレスを構成する。
- スプライトカラーテーブルの先頭アドレスは専用レジスタを持たず、
  SATアドレスの値から自動的に(512を引いた値に)決まる。sprite1には
  このテーブル自体が存在しない。
- R#8のSPD(スプライト全体の非表示)ビットはsprite2固有(sprite1の
  資料には記載がない)。
- sprite size register(SI)・magnify register(MAG)・EC bit・
  Status register 0(F/5S/C/5th sprite#)の構成自体はsprite1/stage4と同じ。

## 参考資料

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                                      |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------- |
| R#5  | A14 | A13 | A12 | A11 | A10 | A9  |   1 |   1 | Sprite attribute table base address register low     |
| R#6  | 0   |   0 | A16 | A15 | A14 | A13 | A12 | A11 | Sprite pattern generator table base address register |
| R#11 |   0 |   0 |   0 |   0 |   0 |   0 | A16 | A15 | Sprite attribute table base address register high    |

## スプライトアトリビュートテーブルの先頭アドレス

https://ngs.no.coocan.jp/doc/wiki.cgi/datapack?page=6%BE%CF+%A5%B9%A5%D7%A5%E9%A5%A4%A5%C8#p8

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- |
| R#5  | A14 | A13 | A12 | A11 | A10 |  A9 |   1 |   1 |
| R#11 |   0 |   0 |   0 |   0 |   0 |   0 | A16 | A15 |

R#5 A9ビットは必ず1に設定します。

    def getSpriteAttributeTableM1():
        addr = self.reg[11] & 0b00000011
        addr <<= 15
        addr |= (self.reg[5] & 0b11111100) << 7
        return addr

- スプライトカラーテーブルの先頭アドレス
  - スプライトアトリビュートテーブルの先頭アドレスの値から512を引いた値に自動的にセットされます。

## スプライトパターンジェネレータテーブルの先頭アドレス

https://ngs.no.coocan.jp/doc/wiki.cgi/datapack?page=6%BE%CF+%A5%B9%A5%D7%A5%E9%A5%A4%A5%C8#p4

スプライトパターンジェネレータテーブルの先頭アドレスはR#6(Sprite pattern genetator table base address register)で指定します。

    def getSpriteGeneratorTable():
        addr = self.reg[6] & 0b00111111
        addr <<= 11
        return addr

## スプライト表示フラグ

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- |
| R#8  |   - |   - |   - |   - |   - |   - | SPD |   - |

SPD=1 スプライトを表示しない SPD=0 表示する

## Status register 0

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                        |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------------- |
|  S#0 |   F | `5S`|  `C`|`5S4`|`5S3`|`5S2`|`5S1`|`5S0`|`Status register 0      |

- F 垂直帰線割り込みフラグ
    S#0を読み出すとリセットされる
- 5S 第5スプライトフラグ
    1水平線上にスプライトが5個(GRAPHIC3～GRAPHIC7モードは9個)並ぶとリセットされる
- C 衝突フラグ
    スプライトが衝突するとセットされる
- 5th sprite# (5S4-5S0) 第5(第9)スプライトの番号がセットされる
