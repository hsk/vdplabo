; 5th sprite(スプライトオーバー)のインデックス値を検証するための診断ROM。
; 9個のスプライトを全部同じYに並べ、STATFLを画面に表示し続ける。
WRTVDP equ 00047h
CHGMOD equ 0005Fh
LDIRVM equ 0005Ch
SPRATR equ 01B00h
SPRPAT equ 03800h
STATFL equ 0F3E7h
JIFFY  equ 0FC9Eh
    org 04000h
rom_header:
    db "AB"
    dw init
    dw 0, 0, 0, 0, 0
init:
    ld a, 1
    call CHGMOD
    ld de, SPRPAT
    ld hl, sprite_pattern_data
    ld bc, 8
    call LDIRVM
    ld de, SPRATR
    ld hl, sprite_attr_data
    ld bc, 4 * 10
    call LDIRVM
loop:
    call wait_vsync
    ; 診断用: STATFLの下位5bitをX座標、bit6の状態を色として
    ; 10個目のスプライト(index9)に反映し続ける
    ld a, (STATFL)
    ld (diag_color), a
    and 011111b
    ld hl, SPRATR + 9*4 + 1  ; 10個目のX座標
    ld (hl), a
    ld a, (diag_color)
    and 01000000b
    jr z, no_over
        ld a, 8
        jr set_color
    no_over:
        ld a, 15
    set_color:
    ld hl, SPRATR + 9*4 + 3  ; 10個目の色
    ld (hl), a
    jr loop
wait_vsync:
    ld hl, JIFFY
    ld a, (hl)
    vsync:
        cp (hl)
        jr z, vsync
    ret
diag_color: db 0
sprite_pattern_data:
    db 011111111b
    db 011111111b
    db 011111111b
    db 011111111b
    db 011111111b
    db 011111111b
    db 011111111b
    db 011111111b
sprite_attr_data:
    ; index0-8: 9個を全部同じYに並べる。index9: 診断用(Y=0)
    db 100, 100, 0, 5
    db 100, 116, 0, 6
    db 100, 132, 0, 7
    db 100, 148, 0, 8
    db 100, 164, 0, 9
    db 100, 180, 0, 10
    db 100, 196, 0, 11
    db 100, 212, 0, 12
    db 100, 228, 0, 13
    db 0,   0,   0, 15
end:
    ds 08000h - $, 0
