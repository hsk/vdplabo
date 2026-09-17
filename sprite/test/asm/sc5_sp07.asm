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
BCLR:    equ $F3E9           ; 背景色/周辺色のワークエリア
CHGCLR:  equ $0062           ; 色変更BIOSコール
    org 04000h
rom_header:
    db "AB"
    dw init
    dw 0, 0, 0, 0, 0
init:
    call screen_init
    call sprite_pattern_table_init
    call sprite_color_table_init
    call sprites_init
    call sprite_attribute_table_send_vram
    jp main
main:
    call sprites_move
    call vsync_wait
    call sprite_attribute_table_send_vram
    jp main
screen_init:
    ; 背景色設定 (例: 背景1、周辺15)
    ld      a, 0x1f
    ld      (BCLR), a
    call    CHGCLR
    ; screen 5
    ld a, 5
    call CHGMOD
    ; sprite magnify ON 16x16
    ld a, (RG1SAV)
    or 000000011b   ; sprite magnify 16x16
    ld b, a
    ld c, 1
    call WRTVDP
    ret
sprite_pattern_table_init:
    ld hl, SPRPAT+8*4*0
    ld bc, 8*4
    ld a, 001010101b
    call BIGFIL
    ld hl, SPRPAT+8*4*1
    ld bc, 8*4
    ld a, 000110011b
    call BIGFIL
    ld hl, SPRPAT+8*4*2
    ld bc, 8*4
    ld a, 000001111b
    call BIGFIL
    ld hl, SPRPAT+8*4*3
    ld bc, 8*2
    ld a, 000000000b
    call BIGFIL
    ld hl, SPRPAT+8*4*3+8*2
    ld bc, 8*2
    ld a, 011111111b
    call BIGFIL
    ret
sprite_color_table_init:
    ; カラーテーブル初期化
    ; sprite 1個目 color 通常色
    ld hl, SPRATR - 0200h + 16 * 0
    ld a, 1
    ld bc, 16
    call BIGFIL
    ; sprite 2個目 color 優先順位なし色(ORで色重ねる)
    ld hl, SPRATR - 0200h + 16 * 1
    ld a, 2 + 0x40  ; 0x40はスプライトの優先順位なしビット
    ld bc, 16
    call BIGFIL
    ; sprite 3個目 color 優先順位なし色(ORで色重ねる)
    ld hl, SPRATR - 0200h + 16 * 2
    ld a, 4 + 0x40  ; 0x40はスプライトの優先順位なしビット
    ld bc, 16
    call BIGFIL
    ; sprite 4個目 color 優先順位なし色(ORで色重ねる)
    ld hl, SPRATR - 0200h + 16 * 3
    ld a, 8 + 0x40  ; 0x40はスプライトの優先順位なしビット
    ld bc, 16
    call BIGFIL
    ret
sprites_init:
    ld d,100 ; x
    ld e,0 ; pattern
    ld b,4
    ld hl,sprites
    sprites_init_loop:
        ld (hl),100 ; y
        inc hl
        ld a,d
        ld (hl),a ; x
        ;add a,32
        ;ld d, a
        inc hl
        ld a,e
        ld (hl),a   ; color(未使用)
        inc hl
        ld (hl),a   ; pattern(未使用)
        inc hl
        add a,4
        ld e,a
        djnz sprites_init_loop
    ret
sprites_move:
    ld b,4
    ld hl,sprites
    sprites_move_loop:
        inc hl
        inc (hl) ; x
        inc hl
        inc hl
        inc hl
        djnz sprites_move_loop
    ret
sprite_attribute_table_send_vram:
    ; VRAMへスプライト属性(座標)を転送
    ld de, SPRATR               ; VRAMのスプライト属性テーブル起点アドレス
    ld hl, sprites              ; 転送元
    ld bc, 4 * 4                ; 4*4バイト (Y, X, パターン, 補足)
    call LDIRVM
    ret
vsync_wait:
    ; VSYNC
    ld hl, JIFFY
    ld a, (hl)
    vsync:
        cp (hl)
        jr z, vsync
    ret
end:
    ds 08000h - $, 0
