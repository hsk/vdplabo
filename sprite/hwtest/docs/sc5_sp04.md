; MSX2 カセットROM SCREEN5 sprite demo
RDVDP  equ 0013Eh
WRTVDP equ 00047h
LDIRVM equ 0005Ch
CHGMOD equ 0005Fh
GTSTCK equ 000D5h
KILBUF equ 00156h
BIGFIL equ 0016BH       ; VRAM を一定値で埋める (A=値, BC=サイズ, HL=VRAM宛先)
SPRATR equ 07600h
SPRPAT equ 07800h
RG1SAV equ 0F3E0h       ; VDPレジスタ退避アドレス
STATFL equ 0F3E7h
JIFFY  equ 0FC9Eh
sprites equ 0C000h
VDP_PORT1 equ 099h           ; アドレス/レジスタ書き込みポート
VDP_PORT2 equ 09Ah           ; カラーデータ出力ポート

    org 04000h
rom_header:
    db "AB"
    dw init
    dw 0, 0, 0, 0, 0
init:
    ; screen 5
    ld a, 5
    call CHGMOD
    ld a,(RG1SAV)
    or 00000001b    ; sprite magnify ON
    ld b, a
    ld c, 1
    call WRTVDP
    ; sprite pattern
    ld hl, SPRPAT
    ld bc, 8
    ld a, 255
    call BIGFIL

    ld hl, palette_table
    ld d, 8
    palette_init:
            di                      ; 割り込み禁止
            ; パレット設定
            ; パレットレジスタのインデックス指定 (R#16)
            ld      a, d
            out     (VDP_PORT1), a
            ld      a, 0x80 + 16
            out     (VDP_PORT1), a
            ld      a, (hl)         ; RB

            out     (VDP_PORT2), a
            inc     hl
            ld      a, (hl)         ; G
            out     (VDP_PORT2), a
            ei                      ; 割り込み許可

            inc     hl
            inc d
            ld a, 8 + 8
            cp d
            jr nz, palette_init

    ; sprite color
    ld a, 8 + 1
    ld hl, SPRATR - 0200h
    ld bc, 8
    call BIGFIL
    ; 2個目の色
    ld a, 8 + 4 + 0x40
    ld hl, SPRATR - 0200h + 16
    ld bc, 8
    call BIGFIL
    ; スプライト属性(座標)をVRAMへ転送
    ld bc, 4 * 2                ; 4*3バイト (Y, X, パターン, 補足)
    ld de, SPRATR               ; VRAMのスプライト属性テーブル起点アドレス
    ld hl, sprite_attr_data     ; 転送元
    call LDIRVM
main:
	jp main
sprite_attr_data:
    ; Y座標,X座標,パターン,色
    db  100,  100,       0,0 ; 0番
    db  100,  108,       0,0 ; 1番
palette_table:
    ;   RB   G
    db 000h, 00h    ;  8
    db 007h, 00h    ;  9
    db 000h, 07h    ; 10
    db 007h, 07h    ; 11
    db 070h, 00h    ; 12
    db 077h, 00h    ; 13
    db 070h, 07h    ; 14
    db 077h, 07h    ; 15
end:
    ds 08000h - $, 0

# SCREEN 5 でスプライトを重ねて 3 色表示する

このサンプルでは SCREEN 5 上で 2 個のスプライトを重ね合わせ、カラーコード機能による色合成を確認します。

ソースコード: [sc5_sp04.asm](../sprite2/sc5_sp04.asm)

前のサンプルではパレットの設定方法を確認しました。

このサンプルでは色の異なるスプライトを重ねて表示し、2 枚のスプライトから 3 色以上を表現できることを確認します。

---

## このサンプルで学べること

- SCREEN 5 のパレット設定
- カラーコードビット (0x40)
- スプライトの OR 合成
- 2 枚のスプライトによる多色表示
- 色番号とパレットの関係

---

## SCREEN 5 の初期化

まず SCREEN 5 に切り替えます。

```asm
ld a, 5
call CHGMOD
```

続いてスプライト拡大を有効にします。

```asm
ld a,(RG1SAV)
or 00000001b
call WRTVDP
```

このサンプルでは拡大スプライトを使用します。

---

## スプライトパターンの作成

パターンゲネレータには塗りつぶしパターンを登録しています。

```asm
ld hl, SPRPAT
ld bc, 8
ld a, 255
call BIGFIL
```

全ビットを 1 にしているため、表示されるスプライトは単純な四角形になります。

---

## パレットの設定

パレット 8 ～ 15 を初期化しています。

```asm
ld hl, palette_table
ld d, 8
```

各パレットエントリに RGB 情報を書き込み、色番号ごとの表示色を設定します。

この部分は前のサンプルとほぼ同じです。

---

## スプライトカラーの設定

スプライトカラーテーブルには異なる色番号を設定しています。

1 個目のスプライトには

```asm
ld a, 8 + 1
```

を設定しています。

2 個目のスプライトには

```asm
ld a, 8 + 4 + 0x40
```

を設定しています。

2 個目のスプライトは Color Code ビットを有効にしているため、重なった部分で色合成が行われます。

---

## Color Code ビット

2 個目のスプライトでは色番号に 0x40 を加えています。

```asm
ld a, 8 + 4 + 0x40
```

このビットを有効にすると、重なったスプライト同士の色が OR 合成されます。

そのため単色スプライトを重ねるだけで、多色スプライトのような表現が可能になります。

---

## スプライト属性テーブル

スプライト属性は次のデータを VRAM へ転送しています。

```text
Y座標  X座標  パターン
100    100    0
100    108    0
```

実際の定義は次のようになっています。

```asm
db 100,100,0,0
db 100,108,0,0
```

X 座標を 8 ドットずらしているため、2 つのスプライトは部分的に重なります。

---

## 属性テーブルの転送

作成した属性データは `LDIRVM` を利用して VRAM へ転送しています。

```asm
ld de, SPRATR
ld hl, sprite_attr_data
call LDIRVM
```

これによりスプライト属性テーブルが初期化されます。

---

## 実行結果

画面中央付近に 2 個のスプライトが表示されます。

```text
　　■□■
```

左側は 1 枚目のスプライトの色、右側は 2 枚目のスプライトの色です。

中央の重なった部分では OR 合成が行われます。

その結果、

```text
色A
色B
色A OR 色B
```

の 3 色が表示されます。

この機能を利用すると、複数のスプライトを重ねて色数を増やすことができます。

---

## このサンプルの位置付け

このサンプルは SCREEN 5 の Color Code 機能を最小構成で確認するための実験です。

```text
パレット
↓
スプライトカラー
↓
Color Code
↓
OR 合成
```

という流れを学ぶためのサンプルになっています。

後続のサンプルでは、さらに多くのスプライトを重ねた場合の挙動を確認していきます。
