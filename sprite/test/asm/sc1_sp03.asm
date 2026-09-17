; MSX カセットROM SCREEN1 sprite demo
WRTVDP equ 00047h
LDIRVM equ 0005Ch
CHGMOD equ 0005Fh
GTSTCK equ 000D5h
KILBUF equ 00156h
SPRATR equ 01B00h
SPRPAT equ 03800h
RG1SAV equ 0F3E0h       ; VDPレジスタ退避アドレス
JIFFY  equ 0FC9Eh
    org 04000h
rom_header:
    db "AB"
    dw init
    dw 0, 0, 0, 0, 0
player_x equ 0C000h
init:
    call screen_init
    call pattern_name_table_init
    call sprite_attribute_table_init
    call player_init
    jp main
main:
    call player_move
    call vsync_wait
    call player_draw
    jr main
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
    ld de, SPRPAT
    ld hl, sprite_pattern_data
    ld bc, 8
    call LDIRVM
    ret
sprite_attribute_table_init:
    ; VRAMへスプライト属性を転送
    ld de, SPRATR
    ld hl, sprite_attr_data
    ld bc, 12
    call LDIRVM
    ret
player_init
    ; プレイヤーX座標
    ld hl, player_x
    ld (hl), 100
    ret
player_move:
    ; キー入力
    call KILBUF
    xor a
    call GTSTCK
    ; 右チェック
    ld hl, player_x
    cp 2
    jr c, end_right     ; 2未満なら飛ぶ
    cp 5
    jr nc, end_right    ; 5以上なら飛ぶ
        inc (hl)        ; 2,3,4 でinc
    end_right:
    ; 左チェック
    cp 6
    jr c, end_left
    cp 9
    jr nc, end_left
        dec (hl) ; 6,7,8でdec
    end_left:
    ret
player_draw:
    ; sprite0 X更新
    ld de, SPRATR + 1
    ld hl, player_x
    ld bc, 1
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
sprite_attr_data:
    db 100, 100, 0, 15 ; sprite0 (player)
    db 100, 160, 0, 14 ; sprite1
    db 100,  40, 0, 11 ; sprite2
sprite_pattern_data:
    db 000011000b
    db 000111100b
    db 001111110b
    db 011011011b
    db 011111111b
    db 000100100b
    db 001011010b
    db 010100101b
end:
    ds 08000h - $, 0
