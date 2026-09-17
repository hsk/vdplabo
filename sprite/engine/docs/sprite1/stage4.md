# sprite1/stage4 について

スプライトの機能をレジスタを通して動かせるようにします。
関連するレジスタは参考資料にまとめてありますので参考にしてください。

## 実装した機能

- [x] sprite size register (SI)
- [x] magnify register (MAG)
- [x] table base register (R#5, R#6)
- [x] status register (5S, collision flag, 5th sprite#)
- [x] EC bit
- [x] collision flag
- [x] 5S flag
- [x] R#7 (Text color/Back drop color register, 背景色のみ。テキスト色は未対応)

`set_backdrop_color()`/`get_backdrop_color()`でR#7の下位4bit(BD3-BD0)を
設定/取得し、render_sprite1がその色で背景を塗りつぶす。デフォルトは0
(黒)で、実機のBIOSデフォルト(BAKCLR=4, 青)を再現したい場合は
呼び出し側で明示的に`set_backdrop_color(4)`する必要がある
(asmがR#7を書き換えていなければBIOSデフォルトが残る、という前提を
呼び出し側のテストコードで再現する)。

### パレットについて

PALETTEの値は、データシート由来の近似値ではなく
[sprite/test/asm/probe_palette.asm](../../../test/asm/probe_palette.asm)を
使ってopenMSX(C-BIOS MSX2, SDLGL-PPレンダラ)で実際に描画された色を
実測した値に置き換えている。VDPパレットレジスタの生値(R/G/B各3bit)を
そのまま線形スケールしても実測値と一致しなかった(非線形なDAC特性の
ためと思われる)ため、実測を採用した。

### 既知の問題

- スプライトアトリビュートテーブルのアドレス計算が、本来読むべきR#5ではなく
  R#6を参照してしまっている(実装時の取り違え)。読み書きどちらも同じ
  この関数を通すため実害はないが、実機のレジスタ計算式としては誤り。

## 参考資料

### スプライト関連のレジスタ

|      |     7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                                      |
| ---- | ----- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------- |
| R#1  |`4/16K`| `BL`|`IE0`|  M1 |  M2 |   0 | `SI`|`MAG`| Mode register 1                                      |
| R#5  |     0 |`A13`|`A12`|`A11`|`A10`|`A9` |`A8` |`A7` | Sprite attribute table base address register         |
| R#6  |     0 |   0 |   0 |   0 |   0 |`A13`|`A12`|`A11`| Sprite pattern generator table base address register |
| R#7  |   TC3 | TC2 | TC1 | TC0 |`BD3`|`BD2`|`BD1`|`BD0`| Text color/Back drop color register                  |

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                        |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------------- |
|  S#0 |   F | `5S`|  `C`|`5S4`|`5S3`|`5S2`|`5S1`|`5S0`|`Status register 0      |

#### Mode register 1

|      |     7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                                      |
| ---- | ----- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------- |
| R#1  |`4/16K`| `BL`|`IE0`|  M1 |  M2 |   0 | `SI`|`MAG`| Mode register 1                                      |

- 4/16K 4K/16KByteメモリ選択 1=16K 0=4K
- BL 1=画面表示、0=画面非表示
- IE0 Interrupt Enable0(1のとき、垂直帰線による割り込みを可能にする)
- SI スプライトのサイズ　1=16×16、0=8×8
- MAG スプライトの拡大　1=拡大する、0=拡大しない

#### Sprite attribute table base address register

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                              |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------------------- |
| R#5  |   0 |`A13`|`A12`|`A11`|`A10`|`A9` |`A8` |`A7` | Sprite attribute table base address register |

#### Sprite pattern generator table base address register

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                                      |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------- |
| R#6  | 0   |   0 |   0 |   0 |   0 |`A13`|`A12`|`A11`| Sprite pattern generator table base address register |

#### Text color/Back drop color register

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                                              |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------------------ |
| R#7  | TC3 | TC2 | TC1 | TC0 |`BD3`|`BD2`|`BD1`|`BD0`| Text color/Back drop color register |

- BD3～BD0 バックドロップの色を指定

#### Status register 0

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
    オーバーが発生しなかった場合は32枚(0〜31)を全て走査し終えた状態になり、
    31が入る(openMSXで実測して確認)。0にリセットされるわけではない
