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
