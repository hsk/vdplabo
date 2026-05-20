
# レジスタ

　ここでは、VDPを制御するコントロールレジスタ、ステータスレジスタについて説明します。

|      |     7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                                      |
| ---- | ----- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------- |
| R#0  |   0   | `0` | `0` | `0` | `0` | `0` |  M3 | `EV`| Mode register 0                                      |
| R#1  |`4/16K`|  BL | IE0 |  M1 |  M2 |   0 |  SI | MAG | Mode register 1                                      |
| R#2  |   0   | `0` | `0` | `0` | A13 | A12 | A11 | A10 | Pattern name table base address register             |
| R#3  | A13   | A12 | A11 | A10 | A9  | A8  | A7  | A6  | Color table base address register                    |
| R#4  |   0   |   0 | `0` | `0` | `0` | A13 | A12 | A11 | Pattern generator table base address register        |
| R#5  | `0`   | A13 | A12 | A11 | A10 | A9  | A8  | A7  | Sprite attribute table base address register.        |
| R#6  | 0     |   0 | `0` | `0` | `0` | A13 | A12 | A11 | Sprite pattern generator table base address register |
| R#7  | TC3   | TC2 | TC1 | TC0 | BD3 | BD2 | BD1 | BD0 | Text color/Back drop color register                  |

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                        |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------------- |
|  S#0 |   F |  5S |   C | 5S4 | 5S3 | 5S2 | 5S1 | 5S0 | Status register 0      |

## 1 コントロールレジスタ#0～#7

|      |     7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                                      |
| ---- | ----- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------- |
| R#0  |   0   | `0` | `0` | `0` | `0` | `0` |  M3 | `EV`| Mode register 0                                      |
| R#1  |`4/16K`|  BL | IE0 |  M1 |  M2 |   0 |  SI | MAG | Mode register 1                                      |
| R#2  |   0   | `0` | `0` | `0` | A13 | A12 | A11 | A10 | Pattern name table base address register             |
| R#3  | A13   | A12 | A11 | A10 | A9  | A8  | A7  | A6  | Color table base address register                    |
| R#4  |   0   |   0 | `0` | `0` | `0` | A13 | A12 | A11 | Pattern generator table base address register        |
| R#5  | `0`   | A13 | A12 | A11 | A10 | A9  | A8  | A7  | Sprite attribute table base address register.        |
| R#6  | 0     |   0 | `0` | `0` | `0` | A13 | A12 | A11 | Sprite pattern generator table base address register |
| R#7  | TC3   | TC2 | TC1 | TC0 | BD3 | BD2 | BD1 | BD0 | Text color/Back drop color register                  |

### 1.1 モードレジスタ

　モードレジスタは各種動作モードを設定するレジスタで、コントロールレジスタ#0、#1、#8、#9に配置されています。

#### Mode register 0

|      |     7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                                      |
| ---- | ----- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------- |
| R#0  |   0   | `0` | `0` | `0` | `0` | `0` |  M3 | `EV`| Mode register 0                                      |

- M3 表示モードの設定に使用する
- EV 外部ビデオ信号 1=外部 0=内部

#### Mode register 1

|      |     7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                                      |
| ---- | ----- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------- |
| R#1  |`4/16K`|  BL | IE0 |  M1 |  M2 |   0 |  SI | MAG | Mode register 1                                      |

- 4/16K 4K/16KByteメモリ選択 1=16K 0=4K
- BL 1=画面表示、0=画面非表示
- IE0 Interrupt Enable0(1のとき、垂直帰線による割り込みを可能にする)
- M1 表示モードの設定に使用する
- M2 表示モードの設定に使用する
- SI スプライトのサイズ　1=16×16、0=8×8
- MAG スプライトの拡大　1=拡大する、0=拡大しない

### 1.2 テーブルベースアドレスレジスタ

　V9918に対してVRAM上の各テーブルの先頭アドレスを宣言するためのレジスタ群です。
　表示モードによっては、設定できるデータの値に制限(実際のアドレスと異なる場合)があるので注意して下さい。詳しくは、各表示モードの解説を参照して下さい。

#### Pattern name table base address register

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                          |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------- |
| R#2  |   0 | A16 | A15 | A14 | A13 | A12 | A11 | A10 | Pattern name table base address register |

#### Color table base address register

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                   |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | --------------------------------- |
| R#3  | A13 | A12 | A11 | A10 | A9  | A8  | A7  | A6  | Color table base address register |

#### Pattern generator table base address register

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                               |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | --------------------------------------------- |
| R#4  |   0 |   0 | `0` | `0` | `0` | A13 | A12 | A11 | Pattern generator table base address register |

#### Sprite attribute table base address register

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                              |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------------------- |
| R#5  | `0` | A13 | A12 | A11 | A10 | A9  | A8  | A7  | Sprite attribute table base address register |

#### Sprite pattern generator table base address register

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                                      |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------- |
| R#6  | 0   |   0 | `0` | `0` | `0` | A13 | A12 | A11 | Sprite pattern generator table base address register |

### 1.3 カラーレジスタ

　V9918の表示色を制御するためのレジスタ群です。

#### Text color/Back drop color register

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                                                              |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------------------------------ |
| R#7  | TC3 | TC2 | TC1 | TC0 | BD3 | BD2 | BD1 | BD0 | Text color/Back drop color register |

- TC3～TC0 TEXT1モードにおけるテキストの色を指定
- BD3～BD0 バックドロップの色を指定

## 2 ステータスレジスタ#0(Read only)

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                        |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------------- |
|  S#0 |   F |  5S |   C | 5S4 | 5S3 | 5S2 | 5S1 | 5S0 | Status register 0      |

　V9918の状態を読み出すための、読み出し専用のレジスタです。

### Status register 0

|      |   7 |   6 |   5 |   4 |   3 |   2 |   1 |   0 |                        |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | ---------------------- |
|  S#0 |   F |  5S |   C | 5S4 | 5S3 | 5S2 | 5S1 | 5S0 | Status register 0      |

- F 垂直帰線割り込みフラグ
    S#0を読み出すとリセットされる
- 5S 第5スプライトフラグ
    1水平線上にスプライトが5個(GRAPHIC3～GRAPHIC7モードは9個)並ぶとリセットされる
- C 衝突フラグ
    スプライトが衝突するとセットされる
- 5th sprite# (5S4-5S0) 第5(第9)スプライトの番号がセットされる
