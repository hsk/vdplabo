; MSX カセットROM SCREEN1 sprite demo
RDVDP  equ 0013Eh
WRTVDP equ 00047h
FILVRM equ 00056h       ; VRAM を一定値で埋める (A=値, BC=サイズ, HL=VRAM宛先)
LDIRVM equ 0005Ch
CHGMOD equ 0005Fh
GTSTCK equ 000D5h
KILBUF equ 00156h
SPRATR equ 01B00h
SPRPAT equ 03800h
RG1SAV equ 0F3E0h       ; VDPレジスタ退避アドレス
STATFL equ 0F3E7h
JIFFY  equ 0FC9Eh
sprites equ 0C000h
    org 04000h
rom_header:
    db "AB"
    dw init
    dw 0, 0, 0, 0, 0
init:
    ; screen 1
    ld a, 1
    call CHGMOD
    ; スプライト拡大
    ld a, (RG1SAV)
    or 000000001b   ; sprite magnify
    ld b, a
    ld c, 1
    call WRTVDP

    ; VRAMへパターンネームテーブルを転送
    ld de, SPRPAT               ; VRAMのパターンジェネレータ起点アドレス
    ld hl, sprite_pattern_data  ; 転送元
    ld bc, 8*4                  ; 転送サイズ (8*4バイト)
    call LDIRVM

    ; スプライト設定
    ld hl, sprites
    ld a, 88
    ld bc, 0400h
sprite_init:
    ld (hl), -17    ; y
    inc hl
    ld (hl), a      ; x
    add a, 24
    inc hl
    ld (hl), c  ; pattern
    inc c
    inc hl
    ld (hl), 5  ; color
    inc hl
    djnz sprite_init
    ; 最後は消しておく
    ld (hl), 208
    call wait_vsync
    ; sprites 更新
    ld de, SPRATR
    ld hl, sprites
    ld bc, 4 * 4
    call LDIRVM
    ; 1秒待ち
    ld b, 60
    loop1:
        call wait_vsync
        djnz loop1

    ; スプライト移動の初期値
    ld c, 0    ; frame値
main:
    inc c
    jp z, end_loop
    ld b, 4     ; ループ値
    ld hl, sprites ; y座標の値のアドレス
    ld de, start_delay
    sprite_move:
        ld a, (de) ; スタート値を取得
        inc de
        cp 200
        jr nc, go
        cp c
        jr nc, next
            go:
            ld a,(hl)
            add a,4
            cp 200
            jr nc, go2
            cp 88
            jr nc, next
            go2:
            ld (hl),a
        next:
        inc hl
        inc hl
        inc hl
        inc hl
        djnz sprite_move
    call wait_vsync
    push bc
    ; sprites 更新
    ld de, SPRATR
    ld hl, sprites
    ld bc, 4 * 4
    call LDIRVM
    pop bc
    jp main
end_loop:
    ; 1秒待ち
    ld b, 60
    loop3:
        call wait_vsync
        djnz loop3
    jp init

wait_vsync:
    ; VSYNC
    ld hl, JIFFY
    ld a, (hl)
    vsync:
        cp (hl)
        jr z, vsync
    ret
start_delay:
    db 0, 12, 24, 36    ; 出現する時間差（フレーム数）

sprite_pattern_data:
    ; T
    db 011111111b
    db 000011000b
    db 000011000b
    db 000011000b
    db 000011000b
    db 000011000b
    db 000011000b
    db 000011000b
    ; Y
    db 010000001b
    db 011000011b
    db 001100110b
    db 000111100b
    db 000011000b
    db 000011000b
    db 000011000b
    db 000011000b
    ; P
    db 011111110b
    db 011000011b
    db 011000011b
    db 011111110b
    db 011000000b
    db 011000000b
    db 011000000b
    db 011000000b
    ; E
    db 011111111b
    db 011000000b
    db 011000000b
    db 011111100b
    db 011000000b
    db 011000000b
    db 011000000b
    db 011111111b
end:
    ds 08000h - $, 0

# SCREEN 1 でスプライトを使ったタイトルアニメーションを作る

このサンプルは、これまでの動作確認用プログラムとは少し異なり、スプライト機能を利用した応用例です。

ソースコード: [sc1_sp06.asm](../sprite1/sc1_sp06.asm)

4 個のスプライトを時間差で画面上から落下させ、最終的に「TYPE」という文字を表示します。

---

## このサンプルの目的

これまでのサンプルでは、

- スプライト表示
- 移動
- 衝突判定
- スプライトオーバー

などの機能を個別に確認してきました。

このサンプルでは、それらの知識を利用して簡単なタイトルアニメーションを作成しています。

---

## 表示される文字

4 個のスプライトにはそれぞれ別のパターンが登録されています。

| パターン  | 文字 |
|-----------|------|
| 0         | T    |
| 1         | Y    |
| 2         | P    |
| 3         | E    |

VRAM には 4 個分のスプライトパターンが登録されます。

```text
T  Y  P  E
```

---

## 初期状態

スプライトは画面外から開始します。

```asm
ld (hl), -17
```

Y座標を -17 に設定しているため、最初は表示されません。

X座標は一定間隔で配置されます。

```asm
add a, 24
```

そのため最終的には横一列に並びます。

---

## 時間差で出現させる

このサンプルの特徴は、各スプライトに開始時間を設定していることです。

```asm
start_delay:
    db 0, 12, 24, 36
```

| 文字 | 開始フレーム |
|------|--------------|
| T    | 0            |
| Y    | 12           |
| P    | 24           |
| E    | 36           |

フレームカウンタと比較し、指定時間になったスプライトだけを移動させています。

その結果、文字が順番に現れるように見えます。

---

## 落下アニメーション

移動開始後は毎フレーム Y座標を増加させます。

```asm
add a, 4
```

4 ドットずつ下へ移動するため、比較的高速に落下します。

目標位置は Y=88 です。

```asm
cp 88
jr nc, next
```

到達すると移動を停止します。

---

## スプライト更新

各フレームごとに RAM 上のスプライト属性を VRAM へ転送します。

```asm
ld de, SPRATR
ld hl, sprites
ld bc, 4 * 4
call LDIRVM
```

4 個のスプライトをまとめて更新しています。

---

## アニメーション終了

フレームカウンタは C レジスタで管理されています。

```asm
inc c
jp z, end_loop
```

255 フレーム経過すると終了処理へ移動します。

終了後は約 1 秒待機し、再び最初から再生します。

そのためタイトルデモのように繰り返し表示されます。

---

## 実行結果

開始直後:

```text
(画面外)
```

途中:

```text
T

    Y

        P
```

完成時:

```text
T Y P E
```

各文字が順番に落下し、最終的に横一列に並びます。

---

## このサンプルで学べること

- スプライトを文字として利用する方法
- フレームカウンタを利用した時間差演出
- スプライトによる簡単なタイトルアニメーション
- RAM 上で属性を管理して一括転送する方法

これまでのテストプログラムとは異なり、実際のゲームやデモ画面で利用できる演出例になっています。
