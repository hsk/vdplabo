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
            di                   ; 割り込み禁止
            ; 1. パレットレジスタのインデックス指定 (R#16)
            ; パレット設定
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

    ld d, 8
    ; sprite color
    ld hl, SPRATR - 0200h
color_init:
    ld bc, 8
    ld a, d
    push de
    call BIGFIL
    ld de, 16
    add hl, de
    pop de
    inc d
    ld a, 8 + 8
    cp d
    jr nz, color_init
    ; スプライト設定
    ld hl, sprites
    ld a, 100
    ld bc, 0a01h
sprite_init:
    ld (hl), 100    ; y
    inc hl
    ld (hl), a      ; x
    add a, 16
    inc hl
    ld (hl), 0      ; pattern
    inc hl
    ld (hl), 0
    inc hl
    djnz sprite_init
    ld (hl), 208
    ld c, -8        ; Y増分
main:
    ld a, 100       ; y座標
    ld b, 8         ; ループ値
    ld hl, sprites
    sprite_move:
        ld (hl), a  ; y座標設定
        add a, c
        inc hl
        inc hl
        inc hl
        inc hl
    djnz sprite_move
    inc c
    ld a, 9
    cp c
    jr nz, end_sprite_move
        ld c, -8
    end_sprite_move:

    push bc
    ld b, 5
    loop2:
        ; VSYNC
        ld hl, JIFFY
        ld a, (hl)
        vsync:
            cp (hl)
            jr z, vsync
        djnz loop2
    ; sprites 更新
    ld hl, sprites
    ld de, SPRATR
    ld bc, 4 * 9
    call LDIRVM
    pop bc
	jp main
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

# SCREEN 5 のパレットを変更する

このサンプルでは SCREEN 5 のパレットを変更し、スプライトの表示色がどのように決まるのかを確認します。

ソースコード: [sc5_sp03.asm](../sprite2/sc5_sp03.asm)

後のサンプルではスプライトを重ねて表示する実験を行います。

その準備として、このサンプルではまずパレットと色番号の関係を確認します。

---

## このサンプルで学べること

- SCREEN 5 のパレット設定
- 色番号と実際の表示色の関係
- VDP レジスタ 16 の役割
- パレットデータの書き込み方法
- SCREEN 5 のスプライトカラーテーブル

---

## SCREEN 5 の初期化

まず SCREEN 5 へ切り替えます。

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

これによりスプライトは拡大表示されます。

---

## スプライトパターンの作成

パターンジェネレータには塗りつぶしパターンを登録しています。

```asm
ld hl, SPRPAT
ld bc, 8
ld a, 255
call BIGFIL
```

全ビットを 1 にしているため、四角形のスプライトになります。

---

## パレットの設定

このサンプルの中心となる処理です。

```asm
ld hl, palette_table
ld d, 8
```

パレット番号 8 ～ 15 を初期化しています。

各色について

```asm
ld a, d
out (VDP_PORT1), a
ld a, 0x80 + 16
out (VDP_PORT1), a
```

を実行し、VDP レジスタ 16 にパレット番号を設定します。

その後、

```asm
ld a, (hl)
out (VDP_PORT2), a
inc hl
ld a, (hl)
out (VDP_PORT2), a
```

でパレットデータを書き込みます。

---

## パレットデータの形式

MSX2 のパレットは 2 バイトで 1 色を表します。

```text
RB
G
```

- 上位バイト : 赤と青
- 下位バイト : 緑

という構成になっています。

このサンプルでは次のような色を設定しています。

| パレット | 色 |
|----------|----|
| 8  | 黒 |
| 9  | 青 |
| 10 | 緑 |
| 11 | シアン |
| 12 | 赤 |
| 13 | マゼンタ |
| 14 | 黄 |
| 15 | 白 |

---

## なぜ OTIR を使っていないのか

後続のサンプルでは `OTIR` を使ってパレットデータをまとめて転送します。

しかし、このサンプルでは 1 色ずつ設定しています。

```asm
out (VDP_PORT2), a
out (VDP_PORT2), a
```

とすることで、

```text
パレット番号指定
↓
上位バイト書き込み
↓
下位バイト書き込み
```

という処理の流れを理解しやすくしています。

パレットアクセスの仕組みを確認するための学習用サンプルです。

---

## スプライトカラーの設定

スプライトカラーテーブルには色番号 8 ～ 15 を設定しています。

```asm
ld d, 8
```

以降、スプライトごとに

```asm
inc d
```

を行うため、それぞれ異なる色で表示されます。

---

## スプライトの配置

8 個のスプライトを横方向へ並べています。

```asm
add a, 16
```

で X 座標を増やしながら配置しています。

また、メインループでは Y 座標を周期的に変化させています。

```asm
ld c, -8
```

から始まり、各スプライトが階段状に並ぶようになっています。

---

## 実行結果

画面上には 8 個のスプライトが表示されます。

```text
■ ■ ■ ■ ■ ■ ■ ■
```

各スプライトは色番号 8 ～ 15 を使用しているため、異なる色で表示されます。

また、時間とともに縦方向の並び方が変化します。

---

## このサンプルの位置付け

このサンプルは単なる色変更の実験ではありません。

後に行うスプライト重ね合わせ実験のために、

```text
色番号
↓
パレット
↓
実際の色
```

という関係を確認するための下準備です。

まずはパレットの仕組みを理解し、その後のサンプルで重ね合わせや色の見え方を確認していきます。
