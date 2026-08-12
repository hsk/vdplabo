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
    org 04000h
rom_header:
    db "AB"
    dw init
    dw 0, 0, 0, 0, 0
init:
    ; screen 5
    ld a, 5
    call CHGMOD
    ; スプライト拡大
    ld a, (RG1SAV)
    or 000000001b   ; sprite magnify
    ld b, a
    ld c, 1
    call WRTVDP
    ; VRAMのパターンネームテーブルを255で埋める
    ld hl, SPRPAT
    ld bc, 8
    ld a, 255
    call BIGFIL

    ld d, 1
    ; sprite color
    ld hl, SPRATR-0200h
color_init:
    ld bc, 8
    ld a, d
    push de
    call BIGFIL
    ld de, 16
    add hl, de
    pop de
    inc d
    ld a, 10 + 1
    cp d
    jr nz, color_init
    ; スプライト設定
    ld hl, sprites
    ld a, 100
    ld b, 0ah
sprite_init:
    ld (hl), 100    ; y
    inc hl
    ld (hl), a      ; x
    add a, 16
    inc hl
    ld (hl), 0  ; pattern
    inc hl
    ld (hl), 0
    inc hl
    djnz sprite_init
    ; 最後は消しておく
    ld (hl), 208
    ; スプライト移動の初期値
    ld c, -8    ; Y増分 -8から8の範囲で変化する
main:
    ; 16ドットずつずらしてスプライトを９個描画
    ld a, 100   ; y座標
    ld b, 9     ; ループ値
    ld hl, sprites
    sprite_move:
        ld (hl), a ; y座標設定
        add a, c
        inc hl
        inc hl
        inc hl
        inc hl
    djnz sprite_move
    ; c が 9 になったら -8 に戻す
    inc c
    ld a, 9
    cp c
    jr nz, end_sprite_move
        ld c, -8
    end_sprite_move:
    ; ステータスレジスタからスプライトの消えた位置を取得してスプライト位置に反映
    ld (hl), 0     ; y
    inc hl         ; x
    ld de, STATFL ; ステータスレジスタ
    ld a, (de)
    and 011111b
    ld (hl), a
    ; 消えたフラグを取得して色を変える
    ld a, (de)
    and 01000000b
    jr z, set_no_del_color
        ld a, 8
        jr set_del_color_end
    set_no_del_color:
        ld a, 15
    set_del_color_end:
    push bc
    ld hl, SPRATR - 0200h + 9*16
    ld bc, 8
    call BIGFIL
    pop bc
    ; 5フレーム待ち
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
    ld de, SPRATR
    ld hl, sprites
    ld bc, 4 * 10
    call LDIRVM
    pop bc
	jp main
end:
    ds 08000h - $, 0
