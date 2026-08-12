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
    call screen_init
    call pattern_name_table_init
    call sprite_init
    call wait_vsync
    call sprites_update
    call wait_1sec
    ; スプライト移動の初期値
    ld c, 0    ; frame値
    call main
    jr init
main:
    inc c
    jp z, end_loop
    call sprites_move
    call wait_vsync
    push bc
    call sprites_update
    pop bc
    jp main
end_loop:
    call wait_1sec
    ret
screen_init:
    ; screen 1
    ld a, 1
    call CHGMOD
    ; スプライト拡大
    ld a, (RG1SAV)
    or 000000001b   ; sprite magnify
    ld b, a
    ld c, 1
    call WRTVDP
    ret
pattern_name_table_init:
    ; VRAMへパターンネームテーブルを転送
    ld de, SPRPAT               ; VRAMのパターンジェネレータ起点アドレス
    ld hl, sprite_pattern_data  ; 転送元
    ld bc, 8*4                  ; 転送サイズ (8*4バイト)
    call LDIRVM
    ret
sprite_init:
    ; スプライト設定
    ld hl, sprites
    ld a, 88
    ld bc, 0400h
    sprite_init_loop:
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
        djnz sprite_init_loop
    ; 最後は消しておく
    ld (hl), 208
    ret

sprites_update:
    ; sprites 更新
    ld de, SPRATR
    ld hl, sprites
    ld bc, 4 * 4
    call LDIRVM
    ret
wait_1sec:
    ; 1秒待ち
    ld b, 60
    loop1:
        call wait_vsync
        djnz loop1
    ret

sprites_move:
    ld b, 4     ; ループ値
    ld hl, sprites ; y座標の値のアドレス
    ld de, start_delay
    sprite_move_loop:
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
        djnz sprite_move_loop
    ret
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
