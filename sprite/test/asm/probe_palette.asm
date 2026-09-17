; パレット実測用の診断ROM。色1〜15のスプライトを別々のラインに1個ずつ並べる。
WRTVDP equ 00047h
CHGMOD equ 0005Fh
LDIRVM equ 0005Ch
SPRATR equ 01B00h
SPRPAT equ 03800h
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
    ld bc, 4 * 15
    call LDIRVM
main:
    jr main
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
    ; Y, X, パターン, 色 (色1〜15を別ラインに1個ずつ)
    db 8+11*0,  100, 0, 1
    db 8+11*1,  100, 0, 2
    db 8+11*2,  100, 0, 3
    db 8+11*3,  100, 0, 4
    db 8+11*4,  100, 0, 5
    db 8+11*5,  100, 0, 6
    db 8+11*6,  100, 0, 7
    db 8+11*7,  100, 0, 8
    db 8+11*8,  100, 0, 9
    db 8+11*9,  100, 0, 10
    db 8+11*10, 100, 0, 11
    db 8+11*11, 100, 0, 12
    db 8+11*12, 100, 0, 13
    db 8+11*13, 100, 0, 14
    db 8+11*14, 100, 0, 15
end:
    ds 08000h - $, 0
