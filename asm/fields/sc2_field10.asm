; MSX カセットROM SCREEN 2 スプライト1つ
; --- MSX BIOSのアドレス定義 ---
CLS:    equ 00042h           ; 画面消去（背景色で塗りつぶし）BIOS
WRTVDP: equ 00047h       ; VDPレジスタ書き込み (B=レジスタ, C=値)
CHGMOD: equ 0005Fh       ; 画面モード変更 (Aレジスタでモード指定)
FILVRM: equ 00056h       ; VRAM を一定値で埋める (A=値, BC=サイズ, HL=VRAM宛先)
LDIRVM: equ 0005Ch       ; メモリからVRAMへ一括転送 (BC=サイズ, DE=VRAM宛先, HL=メモリ元)
WRTVRM: equ 0004Dh       ; VRAMへ1バイト書き込み (A=値, HL=VRAMアドレス)
GTSTCK: equ 000D5h
SNSMAT: equ 00141h
KILBUF: equ 00156h
SPRATR: equ 01B00h       ; VRAMのスプライト属性テーブル起点アドレス
SPRPAT: equ 03800h       ; VRAMのパターンジェネレータ起点アドレス
RG1SAV: equ 0F3E0h       ; VDPレジスタ退避アドレス
JIFFY:  equ 0FC9Eh
FORCLR: equ 0F3E9h  ; 前景色ワークエリア
BAKCLR: equ 0F3EAh  ; 背景色ワークエリア
BDRCLR: equ 0F3EBh  ; 周辺色ワークエリア
CHGCLR: equ 00062h  ; 画面色変更BIOSアドレス

ZSTEP: equ 16
; --- ROMヘッダ ---
    org 04000h          ; カセットROMはページ2(04000h)に配置
rom_header:
    db "AB"             ; ROMの識別ID (04000h)
    dw init             ; 電源ON時に実行するアドレス (04002h)
    dw 0, 0, 0, 0, 0    ; 残りのヘッダ領域を0で埋める
; --- メインプログラム ---
init:
    ld      a, 5
    ld      (BDRCLR), a
    call    CHGCLR
    ; SCREEN 2 の設定
    ld a, 2
    call CHGMOD
    call SetColorPalleteMSX1
    call player_init
    call bg_init
main:
    ;jp main
    call player_move
    call bg_pre_draw
    call vsync_wait
    call bg_draw
    call bg_pattern_name_table_draw
    jp main             ; 画面を維持するため無限ループ

player_init:
    ld hl,player_y
    ld (hl),10
    ld hl,ceil_y4
    ld (hl),20*4
    ld hl,scroll_x
    ld (hl),0
    ret
player_move:
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
        ld c, a
        ld a, (hl)
        cp 0
        ld a, c
        jr z, end_up
        dec (hl)        ; 8,1,2 でdec
    end_up:
    ; 下チェック
    cp 4
    jr c, end_down      ; 4未満なら飛ぶ
    cp 7
    jr nc, end_down     ; 7以上なら飛ぶ
        ld c, a
        ld a, (hl)
        cp 19
        ld a, c
        jr nc, end_down
        inc (hl)        ; 4,5,6 でinc
    end_down:

    ld hl, scroll_x
    ; 右チェック
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
    ; 天井の移動
    ld hl,ceil_y4
    ld  a,5
    call SNSMAT
    ld c,a
    bit 7,c    ; Z
    jr  nz,not_z
        ld a, (hl)
        cp (24-4)*4
        jr nc, not_z
            inc (hl)
    not_z:
    bit 5,c    ; X
    jr  nz,not_x
        ld a, (hl)
        cp 0
        jr z,not_x
            dec (hl)
    not_x:

    ; プレイヤーのZ移動
    ld hl, player_z
    inc (hl)
    ret

bg_init:
    call bg_pattern_table_init
    ;call bg_pattern_name_table_init
    call bg_stripe_color_table1_init
    call stg_init
    ret
bg_stripe_color_table1_init:
    ; 転送先アドレス
    ld hl,stripe_color_table1
    ld c,2
    tr2:
        ; 転送元アドレス
        ld de,stripe_color_table
        ld b,4
        tr:
            ld a,(de)
            inc de
            ld (hl),a
            inc hl
            ld (hl),a
            inc hl
            ld (hl),a
            inc hl
            ld (hl),a
            inc hl
            djnz tr
        dec c
        jr nz,tr2
    
    ; カラーテーブルをstripe_table_1の値をもとにstripe_color_tableを引いた値を設定する192ライン分設定する
    ld a,(stripe_color_table+4)
    ld (stripe_color_table2+16),a
    ret
bg_pattern_table_init:
    ; SCREEN2 のパターンテーブル先頭へアミアミを配置
    ld hl, 00000h
    ld b, 3
    send_pattern_table_loop:
        push bc
        ld b, 64/2
        send_pattern_table:
            ;      12345678
            ld a, 010101010b
            call WRTVRM
            inc hl
            ;      12345678
            ld a, 001010101b
            call WRTVRM
            inc hl
            djnz send_pattern_table
        ; ３つに分かれてる次のパターンテーブルの先頭に移動
        ld bc, 256*8 - 64
        add hl, bc
        pop bc
        djnz send_pattern_table_loop
    ret
fill32:
    exx
    ld c,0x98
    ld (hl),a
    ld d, h
    ld e, l
    inc de
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi

    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi

    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi

    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ;ldi
    ld hl,32
    add hl,de
    exx
    ret


fill32a:
    exx
    ld c,0x98

fill32start:
    ldi ; 2バイト
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi

    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi

    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi

    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi
    ldi

    ld bc,32
    add hl,bc
    ex de,hl
    add hl,bc
    ex de,hl
    exx
    ret
bg_pattern_name_table_draw:
    ld hl,player_y
    inc (hl)
    ; スプライトパターンネームテーブルを設定し全画面を埋める。
    ; SCREEN2 パターンネームテーブル($1800-$1AFF)

    ; 座標計算
    ; `sky_height` は `player_y` と `ceil_y` の小さい方を用います。
    ; sky_height = min(player_y, ceil_y)
    ld a,(player_y)
    ld b, a
    ld a,(ceil_y4)
    srl a ; ceil_y*4/2
    srl a ; ceil_y*4/4 = ceil_y
    cp b
    jr c, no_b
        ld a, b
    no_b:
    ld (sky_height), a

    ; 天井の高さは `sky_height` から求めます。
    ; ceil_height = player_y - sky_height
    ld a,(sky_height)
    ld b,a
    ld a,(player_y)
    sub b
    ld (ceil_height), a

    ; 描画開始位置指定
    exx
    ld hl,virtual_vram+16
    exx
    ; 天井描画
    ; 描画回数はceil_height
    ld a, (ceil_height)
    cp 0
    jp z, fill_sky
        ld b, a
        xor a ; 描画データは0から始まる
        ceil_name_table_y:
            and 7
            call fill32
            inc a
            djnz ceil_name_table_y
    fill_sky:
    ld a,(sky_height)
    cp 0
    jp z, fill_field
        exx
        ex de,hl
            ; bg_start=20-sky_height
            ld a,(sky_height)
            ld c,a
            ld a,20
            sub c
            ld h,0
            ld l,a
            add hl,hl
            add hl,hl
            add hl,hl
            add hl,hl
            add hl,hl
            add hl,hl

            ld a,(scroll_x)
            and 31
            add l
            ld l,a
            ld bc,stg02_name_data
            add hl,bc
        ;ex de,hl
        exx
        ld a,(sky_height)
        ld b, a
        ; 空描画
        ld a,8
        fill_sky_name_table_y:
            call fill32a
            djnz fill_sky_name_table_y
        exx
        ex de,hl
        exx
    fill_field:
    ; 地面描画
    ld a,(player_y)
    ld c, a
    ld b, a              ; 開始一位置ずらす
    ld a, 24
    sub b
    ld b, a
    ld a, c
    exx
            ld c,0x98
    exx
    fill_name_table_y:
        and 7
        call fill32
        inc a
        djnz fill_name_table_y
    ld hl,player_y
    dec (hl)
    ; まとめて転送
    call virtual_vram_to_vram
    ret

virtual_vram_to_vram:
    di
    ; 転送アドレス設定
    xor a
    out (099h),a
    ld a,040h+8*3; 8x3=24ライン分
    out (099h),a
    ; VRAM ATTR 転送ループ
	ld hl,virtual_vram+16
    ld de,32
    ld c,098h
	ld b,24
    gf9_clear_vram_loop:
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop

        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop

        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop

        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        add hl,de; バッファの幅が64個なのでずらす
        dec b
        jp nz, gf9_clear_vram_loop
    ei
	ret

bg_pre_draw:
    ; player_z に応じた色テーブルを生成
    ; stripe_color_table2[i] = stripe_color_table[(i + player_z) & (ZSTEP-1)]
    ld a,(player_z)
    and ZSTEP-1
    ld e,a
    ld d,0
    ld hl,stripe_color_table1
    add hl,de
    ld de, stripe_color_table2
    ld bc,ZSTEP ; 16番目の地平線の色も加える。
    ldir
    ret
bg_draw:
    ; スプライトテーブルのアドレスを取得してhlに入れる
    ld hl, player_y
    ld a,(hl)
    add a,a
    ld de, stripe_tables
    ld h,0
    ld l,a
    add hl, de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ex de, hl

    ; SCREEN2 カラーテーブル ($2000-$37FF) 設定
    ; stripe_table の値(0-4)を stripe_color_table2 で色コードへ変換
    ; 各ラインの色を8バイト分書き込む
    ld c,020h + 040h ; 02000h の上位バイトに転送用の040hを加えるc下位バイトは0
    ld b, 3 ; スクリーン2,4は3つに分かれてるので３回ループ
    color_table_loop:
        ; VDP VRAM書き込みアドレスを $2000 に設定
        push bc ; bc は push して
        ld b, 64/2 ; b はループに使う
        xor a
        di
        ld (stack_pos),sp ; スタックを用いた転送をするためにスタックポインタ保存
        ld sp,hl ; ストライプカラーテーブル位置をスタックポインタに設定
        out (099h),a
        ld a,c
        out (099h),a
        color_table_y:
            pop de ; pop して２バイト読み込みかつポインタを進める
            ; 1バイト目転送
            ld a,e
            ld hl, stripe_color_table2
            add a,l
            ld l,a
            jr nc, no_add
                inc h
            no_add:
            ld a, (hl)
            out (098h),a
            ; 2バイト目転送
            ld a,d
            ld hl, stripe_color_table2
            add a,l
            ld l,a
            jr nc, no_add2
                inc h
            no_add2:
            ld a, (hl)
            out (098h),a
            djnz color_table_y
        ; スタックポインタをhlに入れる
        ld (stack_pos2),sp
        ld hl,(stack_pos2)
        ; スタックポインタを復帰する
        ld sp,(stack_pos)
        ei

        pop bc

        ld a, 8 ; 転送先アドレスを 0800h 進める
        add a, c
        ld c, a
        djnz color_table_loop
    ret
stg_init:
    ld hl, stg02_pattern_data
    ld de, 0x40;8*8
    ld b, 192;24*8
    call stg_pattern_table_init
    ld hl, stg02_color_data
    ld de, 0x2000+8*8
    ld b, 24*8
    call stg_pattern_table_init
    ret
stg_pattern_table_init:
    ; SCREEN2 のパターンテーブルへデータ設定
    ld c, 3
    di
    stg_pattern_table_init_loop1:
        push hl
        push bc
        ld a,0x40
        out (099h),a
        ld a,d
        add 0x40
        out (099h),a
        ld c, 098h
        loopa:
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        nop
        nop
        outi
        jr nz,loopa
        ex de,hl
        ld bc,0800h
        add hl,bc
        ex de,hl
        pop bc
        pop hl
        dec c
        jp nz, stg_pattern_table_init_loop1
    ei
    ret

vsync_wait:
    ; VSYNC
    ld hl, JIFFY
    ld a, (hl)
    vsync:
        cp (hl)
        jr z, vsync
    ret


stripe_table_1: ; y = 8
    db 0,2,4,7,10,14,3,8,16,10,0,6,13,5,13,6
    db 0,9,3,14,8,3,15,10,6,2,14,10,7,3,0,13
    db 10,7,5,2,0,13,11,9,6,4,2,0,14,13,11,9
    db 8,6,4,3,1,0,15,13,12,11,9,8,7,6,5,4
    db 3,2,1,0,15,14,13,12,11,10,9,9,8,7,6,6
    db 5,4,3,3,2,1,1,0,0,15,14,14,13,13,12,11
    db 11,10,10,9,9,8,8,7,7,7,6,6,5,5,4,4
    db 4,3,3,2,2,2,1,1,0,0,0,15,15,15,14,14
    db 14,13,13,13,12,12,12,12,11,11,11,10,10,10,10,9
    db 9,9,9,8,8,8,8,7,7,7,7,6,6,6,6,6
    db 5,5,5,5,4,4,4,4,4,3,3,3,3,3,3,2
    db 2,2,2,2,1,1,1,1,1,1,0,0,0,0,0,0

stripe_table_2: ; y = 16
    db 0,1,2,4,6,8,10,12,15,2,5,9,14,3,9,1
    db 16,6,12,2,9,1,9,2,11,5,15,10,4,15,11,6
    db 2,14,10,6,3,0,12,9,6,4,1,14,12,9,7,5
    db 3,1,15,13,11,9,8,6,4,3,1,0,14,13,12,10
    db 9,8,7,5,4,3,2,1,0,15,14,13,12,11,10,9
    db 9,8,7,6,5,5,4,3,2,2,1,0,0,15,14,14
    db 13,13,12,12,11,10,10,9,9,8,8,7,7,6,6,5
    db 5,5,4,4,3,3,2,2,2,1,1,0,0,0,15,15
    db 15,14,14,14,13,13,13,12,12,12,11,11,11,11,10,10
    db 10,9,9,9,9,8,8,8,8,7,7,7,7,6,6,6
    db 6,5,5,5,5,5,4,4,4,4,3,3,3,3,3,2
    db 2,2,2,2,2,1,1,1,1,1,0,0,0,0,0,0

stripe_table_3: ; y = 24
    db 0,0,2,3,4,5,6,8,10,11,13,15,1,4,7,10
    db 13,1,5,10,15,5,13,6,16,2,8,14,5,13,5,14
    db 7,1,11,5,0,11,6,2,14,10,6,2,15,12,8,5
    db 3,0,13,11,8,6,4,1,15,13,11,9,8,6,4,3
    db 1,15,14,13,11,10,8,7,6,5,4,2,1,0,15,14
    db 13,12,11,10,9,8,8,7,6,5,4,4,3,2,1,1
    db 0,15,15,14,13,13,12,12,11,10,10,9,9,8,8,7
    db 7,6,6,5,5,4,4,3,3,3,2,2,1,1,0,0
    db 0,15,15,15,14,14,14,13,13,12,12,12,12,11,11,11
    db 10,10,10,9,9,9,9,8,8,8,7,7,7,7,6,6
    db 6,6,5,5,5,5,5,4,4,4,4,3,3,3,3,3
    db 2,2,2,2,2,1,1,1,1,1,1,0,0,0,0,0

stripe_table_4: ; y = 32
    db 0,0,1,2,3,4,5,6,7,8,9,11,12,14,15,1
    db 3,5,7,10,12,15,2,6,10,14,3,8,15,6,14,8
    db 16,14,4,10,1,8,1,9,3,12,6,1,12,7,2,14
    db 9,5,2,14,11,7,4,1,14,12,9,7,4,2,0,14
    db 12,10,8,6,4,2,1,15,14,12,11,9,8,7,5,4
    db 3,2,1,15,14,13,12,11,10,9,8,7,7,6,5,4
    db 3,3,2,1,0,0,15,14,14,13,12,12,11,10,10,9
    db 9,8,8,7,6,6,5,5,4,4,4,3,3,2,2,1
    db 1,0,0,0,15,15,14,14,14,13,13,13,12,12,12,11
    db 11,11,10,10,10,9,9,9,9,8,8,8,7,7,7,7
    db 6,6,6,6,5,5,5,5,4,4,4,4,3,3,3,3
    db 3,2,2,2,2,2,1,1,1,1,1,0,0,0,0,0

stripe_table_5: ; y = 40
    db 0,0,1,2,2,3,4,5,5,6,7,8,9,10,12,13
    db 14,0,1,3,4,6,8,10,12,14,1,4,7,10,13,1
    db 6,10,0,6,13,5,14,8,16,10,15,5,12,4,12,5
    db 14,8,2,12,7,2,13,9,5,1,13,10,6,3,0,13
    db 10,8,5,3,0,14,12,10,8,6,4,2,1,15,13,12
    db 10,9,7,6,5,3,2,1,0,15,13,12,11,10,9,8
    db 7,6,6,5,4,3,2,1,1,0,15,14,14,13,12,12
    db 11,10,10,9,9,8,7,7,6,6,5,5,4,4,3,3
    db 2,2,1,1,0,0,0,15,15,14,14,14,13,13,12,12
    db 12,11,11,11,10,10,10,9,9,9,9,8,8,8,7,7
    db 7,6,6,6,6,5,5,5,5,4,4,4,4,3,3,3
    db 3,3,2,2,2,2,1,1,1,1,1,0,0,0,0,0

stripe_table_6: ; y = 48
    db 0,0,1,1,2,2,3,4,4,5,6,7,8,8,9,10
    db 11,12,13,14,0,1,2,4,5,7,8,10,12,14,0,2
    db 5,7,10,13,0,4,8,12,1,6,12,2,10,2,11,7
    db 16,6,11,1,7,15,7,0,9,3,13,7,2,13,9,4
    db 0,12,9,5,2,15,12,9,6,3,1,15,12,10,8,6
    db 4,2,0,15,13,11,10,8,7,5,4,3,1,0,15,14
    db 12,11,10,9,8,7,6,5,4,3,3,2,1,0,15,15
    db 14,13,12,12,11,10,10,9,8,8,7,7,6,6,5,4
    db 4,3,3,2,2,1,1,0,0,0,15,15,14,14,13,13
    db 13,12,12,12,11,11,10,10,10,9,9,9,8,8,8,8
    db 7,7,7,6,6,6,6,5,5,5,4,4,4,4,3,3
    db 3,3,2,2,2,2,2,1,1,1,1,1,0,0,0,0

stripe_table_7: ; y = 56
    db 0,0,0,1,1,2,3,3,4,4,5,6,6,7,8,8
    db 9,10,11,12,13,14,15,0,1,2,3,4,6,7,9,10
    db 12,13,15,1,3,5,8,10,13,15,2,6,9,13,1,6
    db 11,0,7,13,5,14,8,3,16,1,6,12,2,10,2,10
    db 4,13,8,2,13,8,4,15,11,7,4,0,13,10,7,4
    db 2,15,13,10,8,6,4,2,0,14,12,11,9,7,6,4
    db 3,2,0,15,14,13,11,10,9,8,7,6,5,4,3,2
    db 1,0,0,15,14,13,13,12,11,10,10,9,8,8,7,6
    db 6,5,5,4,4,3,3,2,1,1,1,0,0,15,15,14
    db 14,13,13,13,12,12,11,11,11,10,10,9,9,9,8,8
    db 8,7,7,7,7,6,6,6,5,5,5,4,4,4,4,3
    db 3,3,3,2,2,2,2,1,1,1,1,1,0,0,0,0

stripe_table_8: ; y = 64
    db 0,0,0,1,1,2,2,3,3,4,4,5,5,6,7,7
    db 8,9,9,10,11,11,12,13,14,15,0,1,2,3,4,5
    db 6,7,9,10,12,13,15,0,2,4,6,8,10,12,15,1
    db 4,7,11,14,2,6,10,15,4,10,1,8,0,9,3,15
    db 16,12,0,6,13,4,12,5,14,8,2,13,8,3,14,10
    db 6,2,15,12,8,5,2,0,13,11,8,6,4,2,0,14
    db 12,10,8,7,5,4,2,1,15,14,13,11,10,9,8,7
    db 6,5,4,3,2,1,0,15,14,13,13,12,11,10,10,9
    db 8,8,7,6,6,5,4,4,3,3,2,2,1,1,0,0
    db 15,15,14,14,13,13,12,12,11,11,11,10,10,10,9,9
    db 8,8,8,7,7,7,6,6,6,5,5,5,5,4,4,4
    db 3,3,3,3,2,2,2,2,1,1,1,1,0,0,0,0

stripe_table_9: ; y = 72
    db 0,0,0,1,1,1,2,2,3,3,4,4,5,5,6,6
    db 7,7,8,9,9,10,11,11,12,13,13,14,15,0,1,2
    db 3,3,4,6,7,8,9,10,11,13,14,0,1,3,4,6
    db 8,10,12,14,1,3,6,9,12,15,2,6,10,14,3,8
    db 13,3,10,1,10,3,13,9,16,6,11,0,7,14,6,15
    db 8,2,12,7,2,13,9,5,1,13,10,6,3,0,14,11
    db 8,6,4,1,15,13,11,9,8,6,4,3,1,0,14,13
    db 12,10,9,8,7,5,4,3,2,1,0,15,15,14,13,12
    db 11,10,10,9,8,7,7,6,5,5,4,3,3,2,2,1
    db 1,0,15,15,14,14,13,13,13,12,12,11,11,10,10,10
    db 9,9,8,8,8,7,7,7,6,6,6,5,5,5,4,4
    db 4,3,3,3,3,2,2,2,1,1,1,1,0,0,0,0

stripe_table_10: ; y = 80
    db 0,0,0,1,1,1,2,2,2,3,3,4,4,5,5,6
    db 6,7,7,8,8,9,9,10,10,11,12,12,13,14,14,15
    db 0,1,1,2,3,4,5,6,7,8,9,10,11,13,14,15
    db 1,2,3,5,7,8,10,12,14,0,2,5,7,10,12,15
    db 3,6,9,13,1,6,11,0,6,12,3,10,3,12,6,2
    db 16,0,4,10,1,8,0,9,2,12,6,1,12,8,3,15
    db 11,8,4,1,14,11,8,6,3,1,15,13,11,9,7,5
    db 3,2,0,14,13,12,10,9,8,6,5,4,3,2,1,0
    db 15,14,13,12,11,10,9,9,8,7,6,6,5,4,4,3
    db 2,2,1,1,0,15,15,14,14,13,13,12,12,11,11,10
    db 10,10,9,9,8,8,8,7,7,6,6,6,5,5,5,4
    db 4,4,3,3,3,2,2,2,2,1,1,1,1,0,0,0

stripe_table_11: ; y = 88
    db 0,0,0,0,1,1,1,2,2,3,3,3,4,4,5,5
    db 5,6,6,7,7,8,8,9,9,10,10,11,11,12,13,13
    db 14,15,15,0,1,1,2,3,4,5,5,6,7,8,9,10
    db 11,12,14,15,0,1,3,4,5,7,8,10,12,14,0,2
    db 4,6,8,11,13,0,3,6,9,13,0,4,9,13,2,8
    db 14,4,11,3,11,4,15,11,16,9,14,3,10,1,9,2
    db 12,6,0,11,6,1,13,9,6,2,15,12,9,6,3,1
    db 14,12,10,8,6,4,2,0,15,13,12,10,9,7,6,5
    db 4,2,1,0,15,14,13,12,11,10,9,9,8,7,6,5
    db 5,4,3,3,2,1,1,0,15,15,14,14,13,13,12,12
    db 11,11,10,10,9,9,8,8,7,7,7,6,6,5,5,5
    db 4,4,4,3,3,3,2,2,2,1,1,1,1,0,0,0

stripe_table_12: ; y = 96
    db 0,0,0,0,1,1,1,2,2,2,3,3,3,4,4,4
    db 5,5,6,6,6,7,7,8,8,9,9,10,10,11,11,12
    db 12,13,13,14,15,15,0,1,1,2,3,3,4,5,6,7
    db 8,8,9,10,11,12,13,14,0,1,2,3,4,6,7,9
    db 10,12,13,15,1,3,5,7,9,11,14,0,3,6,9,12
    db 0,3,7,11,0,4,9,15,5,11,2,10,3,12,7,2
    db 16,2,7,12,3,10,2,11,5,15,9,4,0,11,7,3
    db 0,12,9,6,3,0,14,11,9,7,5,3,1,15,13,12
    db 10,9,7,6,4,3,2,1,0,14,13,12,11,10,9,8
    db 8,7,6,5,4,3,3,2,1,1,0,15,15,14,13,13
    db 12,12,11,11,10,10,9,9,8,8,7,7,6,6,6,5
    db 5,4,4,4,3,3,3,2,2,2,1,1,1,0,0,0

stripe_table_13: ; y = 104
    db 0,0,0,0,1,1,1,1,2,2,2,3,3,3,4,4
    db 4,5,5,5,6,6,7,7,7,8,8,9,9,10,10,11
    db 11,12,12,13,13,14,14,15,15,0,1,1,2,3,3,4
    db 5,5,6,7,8,9,9,10,11,12,13,14,15,0,1,2
    db 4,5,6,7,9,10,12,13,15,0,2,4,6,8,10,12
    db 14,1,3,6,9,12,15,2,6,9,13,1,6,11,0,6
    db 12,2,9,1,10,3,14,9,16,11,15,4,11,3,11,4
    db 13,8,2,13,9,4,0,13,9,6,3,0,13,11,8,6
    db 4,2,0,14,12,10,8,7,5,4,3,1,0,15,14,12
    db 11,10,9,8,7,6,5,5,4,3,2,1,1,0,15,15
    db 14,13,13,12,11,11,10,10,9,9,8,8,7,7,6,6
    db 5,5,5,4,4,3,3,3,2,2,1,1,1,0,0,0

stripe_table_14: ; y = 112
    db 0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,4
    db 4,4,5,5,5,6,6,6,7,7,8,8,8,9,9,10
    db 10,10,11,11,12,12,13,13,14,14,15,15,0,1,1,2
    db 2,3,4,4,5,6,6,7,8,9,9,10,11,12,13,14
    db 15,0,1,2,3,4,5,6,8,9,10,12,13,14,0,2
    db 3,5,7,9,11,13,15,1,3,6,8,11,14,1,4,8
    db 11,15,3,8,12,1,6,12,2,9,0,8,1,10,4,0
    db 16,2,6,12,3,10,3,12,6,0,11,6,1,13,9,6
    db 3,15,12,10,7,5,2,0,14,12,10,8,7,5,3,2
    db 1,15,14,13,11,10,9,8,7,6,5,4,3,2,1,1
    db 0,15,14,14,13,12,12,11,10,10,9,9,8,8,7,7
    db 6,6,5,5,4,4,3,3,2,2,2,1,1,1,0,0

stripe_table_15: ; y = 120
    db 0,0,0,0,0,1,1,1,1,2,2,2,3,3,3,3
    db 4,4,4,5,5,5,6,6,6,7,7,7,8,8,8,9
    db 9,10,10,10,11,11,12,12,13,13,13,14,14,15,15,0
    db 1,1,2,2,3,3,4,5,5,6,7,7,8,9,10,10
    db 11,12,13,14,15,15,0,1,2,3,4,5,7,8,9,10
    db 12,13,14,0,1,3,4,6,8,9,11,13,15,1,4,6
    db 8,11,14,0,3,6,10,13,1,5,9,13,2,7,12,2
    db 8,15,6,14,7,0,11,6,16,9,13,3,10,1,10,3
    db 13,8,3,14,10,6,2,15,12,9,6,3,1,14,12,10
    db 8,6,4,3,1,0,14,13,11,10,9,8,7,6,4,3
    db 3,2,1,0,15,14,13,13,12,11,11,10,9,9,8,7
    db 7,6,6,5,5,4,4,3,3,2,2,1,1,1,0,0

stripe_table_16: ; y = 128
    db 0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3
    db 3,4,4,4,5,5,5,5,6,6,6,7,7,7,8,8
    db 8,9,9,10,10,10,11,11,11,12,12,13,13,14,14,15
    db 15,0,0,1,1,2,2,3,3,4,4,5,6,6,7,8
    db 8,9,10,10,11,12,13,13,14,15,0,1,2,3,4,5
    db 6,7,8,9,10,11,13,14,15,1,2,4,5,7,8,10
    db 12,14,0,2,4,6,8,11,13,0,2,5,8,12,15,2
    db 6,10,14,3,8,13,2,8,14,5,12,4,13,6,0,12
    db 16,15,3,9,0,8,1,10,4,15,10,6,2,14,11,7
    db 4,1,15,12,10,8,6,4,2,0,15,13,12,10,9,7
    db 6,5,4,3,2,1,0,15,14,13,12,11,11,10,9,9
    db 8,7,7,6,5,5,4,4,3,3,2,2,1,1,0,0

stripe_table_17: ; y = 136
    db 0,0,0,0,0,1,1,1,1,1,2,2,2,2,3,3
    db 3,3,4,4,4,4,5,5,5,6,6,6,7,7,7,7
    db 8,8,8,9,9,9,10,10,11,11,11,12,12,13,13,13
    db 14,14,15,15,0,0,1,1,1,2,3,3,4,4,5,5
    db 6,6,7,8,8,9,10,10,11,12,13,13,14,15,0,0
    db 1,2,3,4,5,6,7,8,9,10,11,13,14,15,0,2
    db 3,4,6,7,9,11,12,14,0,2,4,6,8,10,13,15
    db 2,4,7,10,13,0,4,7,11,15,4,8,13,2,8,13
    db 4,10,2,10,2,12,6,1,16,3,8,14,5,13,7,0
    db 11,6,1,13,9,6,2,15,13,10,8,5,3,1,15,13
    db 12,10,9,7,6,4,3,2,1,0,15,14,13,12,11,10
    db 9,8,8,7,6,6,5,4,4,3,3,2,1,1,0,0

stripe_table_18: ; y = 144
    db 0,0,0,0,0,1,1,1,1,1,2,2,2,2,2,3
    db 3,3,3,4,4,4,4,5,5,5,6,6,6,6,7,7
    db 7,8,8,8,8,9,9,9,10,10,10,11,11,12,12,12
    db 13,13,13,14,14,15,15,0,0,0,1,1,2,2,3,3
    db 4,4,5,6,6,7,7,8,8,9,10,10,11,12,12,13
    db 14,15,15,0,1,2,3,3,4,5,6,7,8,9,10,11
    db 12,14,15,0,1,3,4,5,7,8,10,11,13,15,0,2
    db 4,6,8,10,12,15,1,3,6,9,12,15,2,5,9,12
    db 0,4,9,13,2,7,13,3,9,0,7,15,7,1,11,6
    db 16,7,11,2,10,2,12,6,1,12,8,4,0,13,10,7
    db 5,2,0,14,12,10,8,7,5,4,2,1,0,14,13,12
    db 11,10,9,8,8,7,6,5,4,4,3,2,2,1,1,0

stripe_table_19: ; y = 152
    db 0,0,0,0,0,0,1,1,1,1,1,2,2,2,2,3
    db 3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6
    db 7,7,7,8,8,8,9,9,9,9,10,10,10,11,11,11
    db 12,12,12,13,13,14,14,14,15,15,0,0,0,1,1,2
    db 2,3,3,4,4,5,5,6,6,7,7,8,9,9,10,10
    db 11,12,12,13,14,14,15,0,1,1,2,3,4,5,6,6
    db 7,8,9,10,11,12,13,15,0,1,2,3,5,6,7,9
    db 10,12,13,15,1,2,4,6,8,10,12,14,0,3,5,8
    db 10,13,0,3,6,10,13,1,5,9,13,2,7,12,2,8
    db 14,5,12,4,12,5,15,10,16,8,14,5,13,6,0,10
    db 6,1,13,10,7,4,1,14,12,10,8,6,4,3,1,0
    db 14,13,12,10,9,8,7,6,5,5,4,3,2,2,1,0

stripe_table_20: ; y = 160
    db 0,0,0,0,0,0,1,1,1,1,1,2,2,2,2,2
    db 3,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6
    db 6,7,7,7,7,8,8,8,9,9,9,9,10,10,10,11
    db 11,11,12,12,12,13,13,13,14,14,14,15,15,0,0,0
    db 1,1,2,2,3,3,4,4,4,5,5,6,6,7,8,8
    db 9,9,10,10,11,12,12,13,14,14,15,0,0,1,2,3
    db 3,4,5,6,7,7,8,9,10,11,12,13,14,15,1,2
    db 3,4,5,7,8,9,11,12,14,15,1,2,4,6,8,10
    db 12,14,0,2,4,7,9,12,14,1,4,7,11,14,2,5
    db 9,14,2,7,12,1,6,12,3,9,1,8,1,10,4,14
    db 16,8,14,6,15,8,3,14,10,6,2,15,12,10,7,5
    db 3,1,15,14,12,11,9,8,7,6,5,4,3,2,1,0

stripe_tables:
    dw stripe_table_1
    dw stripe_table_2
    dw stripe_table_3
    dw stripe_table_4
    dw stripe_table_5
    dw stripe_table_6
    dw stripe_table_7
    dw stripe_table_8
    dw stripe_table_9
    dw stripe_table_10
    dw stripe_table_11
    dw stripe_table_12
    dw stripe_table_13
    dw stripe_table_14
    dw stripe_table_15
    dw stripe_table_16
    dw stripe_table_17
    dw stripe_table_18
    dw stripe_table_19
    dw stripe_table_20

stripe_color_table:
;    db 033h, 023h, 022h, 023h, 000h
;    db 033h, 0f3h, 0ffh, 0f3h, 000h
;    db 032h, 033h, 0f3h, 033h, 000h
;    db 022h, 032h, 033h, 032h, 000h
;    db 02ch, 022h, 032h, 022h, 000h
;    db 0cch, 02ch, 022h, 02ch, 000h
;    db 0c1h, 0cch, 02ch, 0cch, 000h
;    db 011h, 0c1h, 0cch, 0c1h, 000h
;    db 011h, 011h, 0c1h, 011h, 000h
;    db 011h, 011h, 011h, 011h, 000h
field1: db $AA,$BB,$AA,$A6

include "res/stg02.asm"

; BIOSルーチン(SUB-ROM用)
EXTROM:equ $015F ; SUB-ROMインタースロットコール
SETPLT:equ $014D ; カラーパレットの設定

; MSXのバージョン情報
MSX1FLG:equ $002D ; 0であればMSX1と判定する

;-------------------------------------------
; 画面カラーパレットの初期化
;-------------------------------------------

SetColorPalleteMSX1:
    ld a, (MSX1FLG)
    or a
    ret z ; MSX1FLGが0であればMSX1と判定
    ; MSX1FLGが0でなければカラーパレットを変更する
    ld hl, ColorPalleteData
    ld b, 15 ; 15色
    ld c, 0
    ColorPalleteSetLoop:
        ld d, c
        ld a, (hl)
        inc hl
        ld e, (hl)
        inc hl
        ; カラーパレット書き込みルーチン呼び出し
        ; SETPLTはSUB-ROMに格納されてあるため
        ; EXTROM経由で呼び出しを行う
        ld ix, SETPLT
        call EXTROM
        ; インタースロットコール時に
        ; InterruptがDisableになることがあるらしく
        ; 明示的にEnableにする
        ei
        inc c
        ld a, c
        cp b
        jp nz, ColorPalleteSetLoop
    ret

ColorPalleteData:

    db $00, $00 ; Color 0
    db $00, $00 ; Color 1
    db $32, $05 ; Color 2
    db $43, $06 ; Color 3
    db $26, $02 ; Color 4
    db $37, $03 ; Color 5
    db $52, $03 ; Color 6
    db $47, $06 ; Color 7
    db $62, $03 ; Color 8
    db $73, $04 ; Color 9
    db $52, $05 ; Color A
    db $64, $06 ; Color B
    db $22, $05 ; Color C
    db $55, $03 ; Color D
    db $55, $05 ; Color E
    db $77, $07 ; Color F

end:
    org 0c000h
player_z: ds 1
player_y: ds 1
scroll_x: ds 1
ceil_y4: ds 1
sky_height: ds 1
ceil_height: ds 1
stack_pos: ds 2
stack_pos2: ds 2
stripe_color_table1: ds 020h ; 4バイトずつ４色が２回で32バイトあるテーブルでzの値からまとめてコピって使える
stripe_color_table2: ds 011h ; Z座標を加えたカラーテーブル
virtual_vram: ds 64*24       ; 仮想VRAM

RAM_SIZE: equ $-0c000h

    ; ROMサイズを16KB（最小サイズ）に合わせるためのパディング
    ds 08000h-end-RAM_SIZE,0
