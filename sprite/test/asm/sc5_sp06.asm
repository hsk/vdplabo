; MSX2 カセットROM SCREEN5 sprite demo
CLS    equ 00042h           ; 画面消去（背景色で塗りつぶし）BIOS
CHGCLR equ 00062h           ; 画面の色を変更するBIOS
RDVDP  equ 0013Eh
WRTVDP equ 00047h
LDIRVM equ 0005Ch
CHGMOD equ 0005Fh
GTSTCK equ 000D5h
SNSMAT equ 00141h
KILBUF equ 00156h
BIGFIL equ 0016BH           ; VRAM を一定値で埋める (A=値, BC=サイズ, HL=VRAM宛先)
SPRATR equ 07600h
SPRPAT equ 07800h
BAKCLR equ 0F3EAh           ; 背景色のワークエリア
RG1SAV equ 0F3E0h           ; VDPレジスタ退避アドレス
STATFL equ 0F3E7h
BDRCLR equ 0F3EBh           ; 周辺色（ボーダー）のワークエリアアドレス
JIFFY  equ 0FC9Eh
SCRMOD equ 0FCAFh           ; 現在のスクリーンモードが格納されているワークエリア
VDP_PORT1 equ 099h          ; アドレス/レジスタ書き込みポート
VDP_PORT2 equ 09Ah          ; カラーデータ出力ポート
player_flg equ 0C000h
player_y equ 0C001h
player_x equ 0C002h
player_y2 equ 0C003h
player_x2 equ 0C004h
    org 04000h
rom_header:
    db "AB"
    dw init
    dw 0, 0, 0, 0, 0
init:
    ; screen 5
    ld a, 8             ; パレット番号 0
    ld (BDRCLR), a      ; ワークエリアへ保存
    ld (BAKCLR), a
    ld a, 5
    call CHGMOD
    ld a, (RG1SAV)
    or 00000001b    ; sprite magnify ON
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
        ld      a, 0                ; VDPレジスタに書き込むデータ
        out     (VDP_PORT1), a 
        ld      a, 0x80 + 16        ; R#16
        out     (VDP_PORT1), a
        ; パレットデータを16個VDP_PORT2に転送
        ld hl, palette_table
        ld b, 32
        ld c, VDP_PORT2
        otir
    ei ; 割り込み許可
    ; sprite color
    ; 1個目
    ld a, 0x00 + 8 + 1
    ld hl, SPRATR - 0200h + 16 * 0
    ld bc, 8
    call BIGFIL
    ; 2個目
    ld a, 0x40 + 8 + 2
    ld hl, SPRATR - 0200h + 16 * 1
    ld bc, 8
    call BIGFIL
    ; 3個目
    ld a, 0x00 + 2
    ld hl, SPRATR - 0200h + 16 * 2
    ld bc, 8
    call BIGFIL
    ; 4個目
    ld a, 0x40 + 4
    ld hl, SPRATR - 0200h + 16 * 3
    ld bc, 8
    call BIGFIL
    ; 5個目
    ld a, 0x00 + 8 + 2
    ld hl, SPRATR - 0200h + 16 * 4
    ld bc, 8
    call BIGFIL
    ; 6個目
    ld a, 0x40 + 8 + 1
    ld hl, SPRATR - 0200h + 16 * 5
    ld bc, 8
    call BIGFIL
    ; スプライト属性(座標)をVRAMへ転送
    ld bc, 4 * 6                ; 4*3バイト (Y, X, パターン, 補足)
    ld de, SPRATR               ; VRAMのスプライト属性テーブル起点アドレス
    ld hl, sprite_attr_data     ; 転送元
    call LDIRVM
    ; プレイヤーX座標
    ld hl, player_flg
    ld (hl), 0
    inc hl
    ld (hl), 80
    inc hl
    ld (hl), 80
main:
    ; キー入力
    call KILBUF
    xor a
    call GTSTCK
    ; 上チェック
    ld hl, player_y
    cp 0
    jr z, end_up        ; 0なら飛ぶ
    cp 3
    jr c, up            ; 1か2なら飛ぶ
    cp 8
    jr nz, end_up       ; 8でないなら飛ぶ
    up:
        dec (hl)        ; 8,1,2 でdec
    end_up:
    ; 下チェック
    cp 4
    jr c, end_down      ; 4未満なら飛ぶ
    cp 7
    jr nc, end_down     ; 7以上なら飛ぶ
        inc (hl)        ; 4,5,6 でinc
    end_down:
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
        dec (hl)        ; 6,7,8でdec
    end_left:
    ld a,8
    ; スペースキーチェック
    call SNSMAT
    bit 0,a
    jr nz, space_end
        ld hl, player_flg
        ld a, (hl)
        xor 1
        ld (hl), a
    space_end:
    ; VSYNC
	ld hl, JIFFY
	ld a, (hl)
    vsync:
        cp (hl)
		jr z, vsync
    ; sprite2 X, Y更新
    ld hl, player_y
    ld de, SPRATR + 4 * 2
    ld bc, 2
    call LDIRVM
    ; sprite3 X, Y更新
    ; y座標
    ld de, player_y2
    ld hl, player_flg
    ld c, (hl)
    inc hl
    ld a, c
    cp 0
    ld a, (hl)
    jr z, no_move2
        add a, 8
    no_move2:
    ld (de), a
    ; x座標
    inc hl
    inc de
    ld a, (hl)
    add a, 8
    ld (de), a
    ; 転送
    inc hl
    ld de, SPRATR + 4 * 3
    ld bc, 2
    call LDIRVM
	jp main
sprite_attr_data:
    ; Y座標,X座標,パターン, 色
    db  100,  100,       0, 0   ; 0番
    db  106,  108,       0, 0   ; 1番
    db   80,   80,       0, 0   ; 2番
    db   88,   88,       0, 0   ; 3番
    db  132,  100,       0, 0   ; 4番
    db  140,  108,       0, 0   ; 5番
palette_table:
    ;   RB   G
    db 033h, 03h    ;  0
    db 037h, 03h    ;  1
    db 033h, 07h    ;  2
    db 037h, 07h    ;  3 
    db 073h, 03h    ;  4
    db 077h, 03h    ;  5
    db 073h, 07h    ;  6
    db 077h, 07h    ;  7
    db 000h, 00h    ;  8
    db 007h, 00h    ;  9
    db 000h, 05h    ; 10
    db 007h, 05h    ; 11
    db 070h, 00h    ; 12
    db 077h, 00h    ; 13
    db 070h, 05h    ; 14
    db 077h, 05h    ; 15
end:
    ds 08000h - $, 0
