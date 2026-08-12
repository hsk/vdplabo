WRTVDP equ 00047h       ; VDPレジスタ書き込み (B=レジスタ, C=値)
CHGMOD equ 0005Fh       ; 画面モード変更 (Aレジスタでモード指定)
LDIRVM equ 0005Ch       ; メモリからVRAMへ一括転送 (BC=サイズ, DE=VRAM宛先, HL=メモリ元)
SPRATR equ 01B00h       ; VRAMのスプライト属性テーブル起点アドレス
SPRPAT equ 03800h       ; VRAMのパターンジェネレータ起点アドレス
RG1SAV equ 0F3E0h       ; VDPレジスタ退避アドレス
JIFFY  equ 0FC9Eh
sprites equ 0C000h
seed equ 0C100h
    org 04000h          ; カセットROMはページ2(04000h)に配置
rom_header:
    db "AB"             ; ROMの識別ID (04000h)
    dw init             ; 電源ON時に実行するアドレス (04002h)
    dw 0, 0, 0, 0, 0    ; 残りのヘッダ領域を0で埋める
init:
    ; SCREEN 1 の設定
    ld a, 1
    call CHGMOD
    ; スプライト拡大
    ld a, (RG1SAV)
    or 000000011b   ; sprite magnify
    ld b, a         ; 設定データ
    ld c, 1         ; ポートNo.
    call WRTVDP
    ; VRAMへパターンネームテーブル8x8スプライトパターン２個分を転送
    ld de, SPRPAT               ; VRAMのパターンジェネレータ起点アドレス
    ld hl, sprite_pattern_data1 ; 転送元
    ld bc, 8*2                  ; 転送サイズ (8*2バイト)
    call LDIRVM
    ; 16x16 sprite patterns
    ; まず spritesテーブルにパターンデータを転送
    ld de, sprites
    ld hl, sprite_pattern_data2  ; 転送元
    ld bc, 2
    loop1:
        push bc
        ld bc, 16
        loop2:
            inc hl
            ldi
            jp      pe,loop2
        ld bc, -33
        add hl, bc
        ld bc, 16
        loop3:
            inc hl
            ldi
            jp      pe,loop3
        inc hl
        pop bc
        djnz loop1
    ; 次に spritesテーブルから VRAMのパターンジェネレータへ転送
    ld de, SPRPAT + 8*4         ; VRAMのパターンジェネレータ起点アドレス
    ld hl, sprites              ; 転送元
    ld bc, 8*4*2                ; 転送サイズ (8*4*2バイト)
    call LDIRVM

    ; スプライトRAMの初期化
    ld b, 32
    ld c, 0
    ld hl, sprites
    loop4:
        ; s["dx"] = random.randint(-32,32)/16.0
        ; s["dy"] = random.randint(-32,32)/16.0
        ; s["dx"] = random.randint(0,64)/16.0 - 1
        ; s["dy"] = random.randint(0,64)/16.0 - 1
        push bc
        ld b, 2
        loop5:
            push hl
            call random
            ld a, h
            ld c, l
            pop hl
            and 1
            jr z, dx_positive
                ; dx negative
                xor a
                dec a
                jr dx_done
            dx_positive:
                xor a
            dx_done:
            ld (hl), a
            inc hl
            ld (hl), c
            inc hl
            djnz loop5
        pop bc
        xor a
        ld (hl), a
        inc hl
        xor a
        ld (hl), a
        inc hl
        ; s["y"] = 40 + (i % 2) * 40
        ld a, b
        and 1
        ld a, 40
        jr z, even
            ld a, 80
        even:
        ld (hl),a
        inc hl
        ; s["x"] = 16 + i * 6
        ld a, b
        add a,a
        add a,a
        ld (hl), a
        inc hl
        ; s["pattern"] = i
        ld a, b
        and 1
        add a,a
        add a,a
        add a,4
        ld (hl), a
        inc hl
        ; s["color"] = (i % 14) + 2
        ld a, c
        inc a
        inc a
        and 0x0f
        ld (hl), a
        inc hl
        inc c
        cp 14
        jr nz, end_reset
            ld c, 0
        end_reset:

        djnz loop4
;    self.mode = 3
main:
    ; VRAMへスプライト属性(座標)を転送
    ;ld de, SPRATR               ; VRAMのスプライト属性テーブル起点アドレス
    ;ld hl, sprites     ; 転送元
    ;ld bc, 32*4                  ; 4バイト (Y, X, パターン, 補足)
    ;call LDIRVM
    ; VSYNC
    ld hl, JIFFY
    ld a, (hl)
    vsync:
        cp (hl)
        jr z, vsync
    call update_vram
    ld ix, sprites
    ld b, 32
    spmove_loop:
        call spmove
        ld de,4+6
        add ix, de
    djnz spmove_loop
    jp main

spmove:
    ; move x
    ld d, (ix+0)    ; dxh
    ld e, (ix+1)    ; dxl
    ld l, (ix+4)    ; xl
    ld h, (ix+7)    ; xh
    and a
    adc hl, de
    ld a,h
    ld (ix+4), l    ; xl
    ld (ix+7), h    ; xh
    ld      de,0e000h
    and     a
    sbc     hl,de
    jr      c,not_overx
        inc a
        jr nz, not_255x
            ld (ix+4), a    ; xl
            ld (ix+7), a    ; xh
        not_255x:
        ld d, (ix+0)    ; dxh
        ld e, (ix+1)    ; dxl
        and     a        ; Carry=0
        sbc     hl,hl    ; HL=0
        sbc     hl,de    ; HL=-DE
        ex de,hl          ; HL=DE, DE=-DE
        ld (ix+0),d    ; dxh
        ld (ix+1),e    ; dxl
    not_overx:

    ; move y
    ld d, (ix+2)    ; dxh
    ld e, (ix+3)    ; dxl
    ld l, (ix+5)    ; xl
    ld h, (ix+6)    ; xh
    and a
    adc hl, de
    ld a,h
    ld (ix+5), l    ; xl
    ld (ix+6), h    ; xh
    ld      de,0a000h
    and     a
    sbc     hl,de
    jr      c,not_overy
        inc a
        jr nz, not_255y
            ld (ix+5), a    ; xl
            ld (ix+6), a    ; xh
        not_255y:
        ld d, (ix+2)    ; dxh
        ld e, (ix+3)    ; dxl
        and     a        ; Carry=0
        sbc     hl,hl    ; HL=0
        sbc     hl,de    ; HL=-DE
        ex de,hl          ; HL=DE, DE=-DE
        ld (ix+2),d    ; dxh
        ld (ix+3),e    ; dxl
    not_overy:
    ret
; --- 📦 5バイト構造を正しい4バイトにしてVRAM（SPRATR）へ送る関数 ---
update_vram:
    ld hl, sprites
    ld de, SPRATR
    ld b, 32        ; 32スプライト分
vram_loop:
    push bc
        ld bc, 4
        push bc
            add hl, bc      ; 4バイト分進む
            inc hl          ; 5バイト分進む
            inc hl          ; 6バイト分進む
            push de
            push hl
            call LDIRVM     ; HLが4進み、DE（VRAMアドレス）も4進むことはない
            pop hl
            pop de
        pop bc
        add hl, bc
        inc de
        inc de
        inc de
        inc de
    pop bc
    djnz vram_loop
    ret

random:
    ld hl, (seed)
    ld d, h
    ld e, l
    add hl, hl ; seed * 2
    add hl, hl ; seed * 4
    add hl, hl ; seed * 8
    add hl, hl ; seed * 16
    sbc hl, de ; seed * 15
    add hl, hl ; seed * 30
    add hl, hl ; seed * 60
    sbc hl, de ; seed * 59
    add hl, hl ; seed * 118
    sbc hl, de ; seed * 117
    ld de, 07321h
    add hl, de; seed * 118 + 13452
    ld (seed), hl
    ret

sprite_pattern_data1:
    db 000111100b
    db 001111110b
    db 011111111b
    db 011011011b
    db 011111111b
    db 001111110b
    db 000111100b
    db 000011000b
    ; 2
    db 000011000b
    db 000111100b
    db 001111110b
    db 011111111b
    db 001111110b
    db 000111100b
    db 000011000b
    db 000000000b
sprite_pattern_data2:
    dw 00000111111110000b
    dw 00011111111111100b
    dw 00110111100001110b
    dw 00100111011110110b
    dw 01110110111111011b
    dw 01110110111111011b
    dw 01110110111111111b
    dw 01110110000001111b
    dw 01110110111110111b
    dw 01110110111111011b
    dw 01110110111111011b
    dw 01110110111111011b
    dw 00110111011110110b
    dw 00110111100001110b
    dw 00011111111111100b
    dw 00000111111110000b
    ; 4
    dw 00000000110000000b
    dw 00000001111000000b
    dw 00000011111100000b
    dw 00000111111110000b
    dw 00001111111111000b
    dw 00011111111111100b
    dw 00111111111111110b
    dw 01111111111111111b
    dw 01111111111111111b
    dw 00111111111111110b
    dw 00011111111111100b
    dw 00001111111111000b
    dw 00000111111110000b
    dw 00000011111100000b
    dw 00000001111000000b
    dw 00000000110000000b
end:
    ; ROMサイズを16KB（最小サイズ）に合わせるためのパディング
    ds 08000h - $, 0
