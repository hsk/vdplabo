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

FORCLR: EQU 0F3E9H  ; 前景色ワークエリア
BAKCLR: EQU 0F3EAH  ; 背景色ワークエリア
BDRCLR: EQU 0F3EBH  ; 周辺色ワークエリア
CHGCLR: EQU 0062H   ; 画面色変更BIOSアドレス


    org 04000h
rom_header:
    db "AB"
    dw init
    dw 0, 0, 0, 0, 0
init:
    LD A, 15
    LD (FORCLR), A
    LD A, 1
    LD (BAKCLR), A
    LD A, 0
    LD (BDRCLR), A
    CALL CHGCLR
    ; screen 5
    ld a, 5
    call CHGMOD
    ; 値をワークエリアに書き込む
    ; sprite magnify ON
    ld a, (RG1SAV)
    or 00000001b
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
            ; パレットデータ出力
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
    ; sprite 1個目 color 通常色
    ld hl, SPRATR - 0200h
    ld a, 8 + 1
    ld bc, 8
    call BIGFIL
    ; sprite 2個目 color 優先順位なし色(ORで色重ねる)
    ld hl, SPRATR - 0200h + 16
    ld a, 8 + 2 + 0x40  ; 0x40はスプライトの優先順位なしビット
    ld bc, 8
    call BIGFIL
    ; sprite 3個目 color 優先順位なし色(ORで色重ねる)
    ld hl, SPRATR - 0200h + 16 * 2
    ld a, 8 + 4 + 0x40  ; 0x40はスプライトの優先順位なしビット
    ld bc, 8
    call BIGFIL
    ; VRAMへスプライト属性(座標)を転送
    ld de, SPRATR               ; VRAMのスプライト属性テーブル起点アドレス
    ld hl, sprite_attr_data     ; 転送元
    ld bc, 4 * 3                ; 4*3バイト (Y, X, パターン, 補足)
    call LDIRVM
main:
	jp main
sprite_attr_data:
    ; Y座標,   X座標,パターン, 色
    db  100,     100,       0, 0    ; 0番
    db  106,     108,       0, 0    ; 1番
    db  100 - 6, 108,       0, 0    ; 2番
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
