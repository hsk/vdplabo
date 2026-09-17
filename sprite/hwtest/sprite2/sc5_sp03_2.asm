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
    ld a, (RG1SAV)
    or 00000001b ; sprite magnify
    ld b, a
    ld c, 1
    call WRTVDP
    ; sprite pattern
    ld hl, SPRPAT
    ld bc, 8
    ld a, 255
    call BIGFIL
    ; パレット設定
    di
        ; パレット番号設定
        ld      a, 8            ; VDPレジスタに書き込むデータ
        out     (VDP_PORT1), a 
        ld      a, 0x80 + 16    ; R#16
        out     (VDP_PORT1), a
        ; パレットデータを16個VDP_PORT2に転送
        ld hl, palette_table
        ld b, 16
        ld c, VDP_PORT2
        otir
    ei ; 割り込み許可
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
