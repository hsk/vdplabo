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
    jp main
main:
    ; スプライト移動の初期値
    ld c, -8    ; Y増分 -8から8の範囲で変化する
main_loop:
    call sprites_move
    call debug_sprite_status
    push bc
    call wait_5frame
    call sprites_update
    pop bc
    jp main_loop
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
pattern_name_table_init:
    ; VRAMのパターンネームテーブルを255で埋める
    ld hl, SPRPAT
    ld bc, 8
    ld a, 255
    call FILVRM
    ret
sprite_init:
    ; スプライト設定
    ld hl, sprites
    ld a, 100
    ld bc, 0a05h
    sprite_init_loop:
        ld (hl), 100    ; y
        inc hl
        ld (hl), a      ; x
        add a, 16
        inc hl
        ld (hl), 0  ; pattern
        inc hl
        ld (hl), c  ; color
        inc c
        inc hl
        djnz sprite_init_loop
    ; 最後は消しておく
    ld (hl), 208
    ret
sprites_move:
    ; 16ドットずつずらしてスプライトを９個描画
    ld a, 100   ; y座標
    ld b, 9     ; ループ値
    ld hl, sprites
    sprite_move_loop:
        ld (hl), a ; y座標設定
        add a, c
        inc hl
        inc hl
        inc hl
        inc hl
    djnz sprite_move_loop
    ; c が 9 になったら -8 に戻す
    inc c
    ld a, 9
    cp c
    ret nz
        ld c, -8
    ret
debug_sprite_status:
    ; ステータスレジスタからスプライトの消えた位置を取得してスプライト位置に反映
    ld (hl), 0     ; y
    inc hl         ; x
    ld de, STATFL ; ステータスレジスタ
    ld a, (de)
    and 011111b
    ld (hl), a
    inc hl
    inc hl
    ; 消えたフラグを取得して色を変える
    ld a, (de)
    and 01000000b
    jr z, set_no_del_color
        ld a, 8
        jr set_del_color_end
    set_no_del_color:
        ld a, 15
    set_del_color_end:
    ld (hl), a
    ret
sprites_update:
    ; sprites 更新
    ld de, SPRATR
    ld hl, sprites
    ld bc, 4 * 10
    call LDIRVM
    ret

wait_5frame:
    ; 5フレーム待ち
    ld b, 5
    loop2:
        call wait_vsync
        djnz loop2
    ret
wait_vsync:
    ; VSYNC
    ld hl, JIFFY
    ld a, (hl)
    vsync:
        cp (hl)
        jr z, vsync
    ret
end:
    ds 08000h - $, 0
