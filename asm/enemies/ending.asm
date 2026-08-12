WRTVDP: equ 00047h
LDIRVM: equ 0005Ch
CHGMOD: equ 0005Fh
GTSTCK: equ 000D5h
RDVDP:  equ 0013Eh
KILBUF: equ 00156h
SPRATR: equ 01B00h
SPRPAT: equ 03800h
RG1SAV: equ 0F3E0h       ; VDPレジスタ退避アドレス
STATFL: equ 0F3E7h
WRTVRM: equ 0004Dh       ; VRAMへ1バイト書き込み (A=値, HL=VRAMアドレス)
JIFFY:  equ 0FC9Eh
H_TIMI: equ 0FD9Fh
RG8SAV: equ 0FFE7h

    org 04000h
rom_header:
    db "AB"             ; ROMの識別ID (04000h)
    dw init             ; 電源ON時に実行するアドレス (04002h)
    dw 0, 0, 0, 0, 0    ; 残りのヘッダ領域を0で埋める

;WORK_START_0xbb80: equ 0xbb80
; 仮想 VRAM 64 x 24 0xc000 - 0xc600 文字列や基本的な画面設定に使う
; 文字列描画 0,0 "TOP 000000000  SCORE 000000000 STAGE  1"
VIRTUAL_VRAM_0c000h_0x0:	equ 0xc000
; ゲーム中のキャラ描画は編みかけの色だけ変えて描画するのでこちらを用いる
; 仮想 VRAM ATTR 64 x 24 0xc1cc - 0xc7cc
;VIRTUAL_ATTR_CLEAR_BYTE_0c1cch_12x7_ATTR_0x1:	equ 0xc1cc
VIRTUAL_VRAM_0c359h_25x13_ATTR_13x7:	equ 0xc359
VIRTUAL_VRAM_0c3dch_28x15_ATTR_16x9:	equ 0xc3dc
VIRTUAL_VRAM_0c3ddh_29x15_ATTR_17x9:	equ 0xc3dd
VIRTUAL_VRAM_0c419h_25x16_ATTR_13x10:	equ 0xc419
; dom_eye pos
VIRTUAL_VRAM_ATTR_30x10_DOM_EYE:	equ 0xc42a
; 文字列描画 16,11 "ステージ名"
VIRTUAL_VRAM_0c45ch_28x17_ATTR_16x11:	equ 0xc45c
VIRTUAL_VRAM_0c45dh_29x17_ATTR_17x11:	equ 0xc45d
VIRTUAL_VRAM_ATTR_29x11_DOM_EYE:	equ 0xc469
VIRTUAL_VRAM_ATTR_31x11_DOM_EYE:	equ 0xc46b
VIRTUAL_VRAM_0c78ch_12x30_ATTR_0x24:	equ 0xc78c
VIRTUAL_VRAM_0c78eh_14x30_ATTR_2x24:	equ 0xc78e
VIRTUAL_VRAM_0c7b4h_52x30_ATTR_40x24:	equ 0xc7b4

IPL_ROM_WORK_01009h:        equ JIFFY
;IPL_ROM_WORK_010f0h:       equ 010f0h
VIRTUAL_ATTR_CLEAR_BYTE_0c1cch_12x7_ATTR_0x1:equ 0xc1cc
DAMAGE_WORK_0cc52h:         equ 0cc52h
DAMAGE_WORK_0cc56h:         equ 0cc56h
STAGE_BOSS_START_0ce5bh:    equ 0ce5bh
PLAYER_POS_Y:               equ 0xcc5c
PLAYER_POS_X:               equ 0xcc5d
FRAME_CNT_0cc68h:           equ 0cc68h
ending_spj_ptr:             equ 0c000h
ending_script_ptr:          equ 0c002h
h_timi_old:                 equ 0c004h
copy_flg:                   equ 0c009h
;; game.asm
; 通常ゲームシーン
init:
    ; RSLREGで現在実行中のスロットを取得
    call	0x0138 ; RSLREG
	; ENASLTで8000hページへ割り当てる。
    ld		b,a
	srl		a
	srl		a
	ld		hl, 0x8000
	call	0x0024 ; ENASLT

    ; SCREEN 2 の設定
    ld a, 2
    call CHGMOD
    ld  a,(RG8SAV)   ; BIOSのVDPレジスタ保存領域
    or  00000010b    ; bit1をセット
    ld  (RG8SAV),a
    out (099h),a
    ld  a,8+128
    out (099h),a

    call bg_pattern_table_init
    call bg_color_table_init
    ld a,013h
    ;call bg_field_init
    ld a,18
    ld (PLAYER_POS_Y),a
    ld a,30
    ld (PLAYER_POS_X),a

	;; 割り込みフック処理
	; 割り込み禁止
	di
	; h_timi から h_timi_old に5バイトコピー
	ld		hl, H_TIMI
	ld		de, h_timi_old
	ld		bc, 5
	ldir
	; h_timi_rep から h_timi に3バイトコピー
	ld		hl, h_timi_rep
	ld		de, H_TIMI
	ld		bc, 3
	ldir
	; 割り込み許可
	ei

    jp main

h_timi_rep:
	jp		h_timi_new

bg_pattern_table_init:
    ; SCREEN2 のパターンテーブル先頭へアミアミを配置
    ld hl, 00000h
    ld b, 3
    bg_pattern_table_init_loop1:
        push bc
        ld b, 0;64*8/2
        di
        ; 転送アドレス設定
        ld a,l
        out (099h),a
        ld a,0x40
        or h
        out (099h),a
        ;      12345678
        ld a, 010101010b
        bg_pattern_table_init_loop2:
            cpl
            out (98h),a
            cpl
            out (98h),a
            cpl
            out (98h),a
            cpl
            out (98h),a
            djnz bg_pattern_table_init_loop2
        ei
        ; ３つに分かれてる次のパターンテーブルの先頭に移動
        ld bc, 256*8
        add hl, bc
        pop bc
        djnz bg_pattern_table_init_loop1
    ret
          ;0 1 2 3 4 5  6  7
          ;黒青赤紫緑空黄白
colors: db 1,4,8,13,2,7,10,15
bg_color_table_init:
    ; SCREEN2 のカラーテーブルへ配置
    ld hl, 02000h
    ld b, 3

    bg_color_table_init_loop1:
        push bc
        push hl
        ld b, 8
        ld c, 0
        bg_color_table_init_loop2:
            push bc
            push hl
            ld b, 8
            di
            ; 転送アドレス設定
            ld a,l
            out (099h),a
            ld a,0x40
            or h
            out (099h),a
            bg_color_table_init_loop3:
                push bc
                ld a, c
                ld hl,colors
                ld e,a
                ld d,0
                add hl,de
                ld a,(hl)
                ld c, a
                ld a, 8
                sub b
                ld hl,colors
                ld e,a
                ld d,0
                add hl,de
                ld a,(hl)
                add a,a
                add a,a
                add a,a
                add a,a
                add a,c
                ld c,098h
                out (c),a
                out (c),a
                out (c),a
                out (c),a
                out (c),a
                out (c),a
                out (c),a
                out (c),a
                pop bc
                djnz bg_color_table_init_loop3
            ei
            pop hl
            ld bc,8*16
            add hl,bc
            pop bc
            inc c
            djnz bg_color_table_init_loop2
        pop hl
        ; ３つに分かれてる次のパターンテーブルの先頭に移動
        ld bc, 256*8
        add hl, bc
        pop bc
        djnz bg_color_table_init_loop1
    ret

;; ending_script.asm
ENDING_SCRIPT_WORK_0ce69h:	equ 0xce69
ENDING_SCRIPT_WORK_0ce6ah:	equ 0xce6a
main:
    ;ld a,013h
    ;call bg_pre_draw
    ;call bg_draw
    ;call draw_raster_attr      ; 仮想VRAM属性にラスタ属性を描画
    ;call player_draw
    ;call player_move
    ;call wait_vsync
    ;call copy_vram_attr        ; VRAM属性を仮想VRAM属性から転送
    ;jp main
EndingScriptScene:
    ld hl,spj01_tree1_l4000h
    ld (ending_spj_ptr),hl
    ; エンディングスクリプト初期化
    ld hl,ending_script_data
    ld (ending_script_ptr),hl
    ; -------------------------------------
    ; ゼロクリア 49バイト
    ld hl,ENDING_SCRIPT_WORK_0ce69h
    ld de,ENDING_SCRIPT_WORK_0ce6ah
    ld bc,00030h
    ld (hl),b
    ; hl → de に、bc バイト転送
    ldir
    ending_loop1:
        ld b,12
        ending_loop2:
            push bc
            ;call API02_f1_f2_pause_key_check    ; F1,F2,ポーズ処理
            ;call API01_update_raster_field_attrs; 地面ラスタ属性更新
            call API09_ending_sprites_move_left   ; ※スプライトを横に移動させる
            call wait_copy
            call CallEF04_draw_raster_attr      ; 仮想VRAM属性にラスタ属性を描画
            ;call CallGF01_player_move           ; プレイヤー移動
            ;call CallGF16_calc_view_scrolly_from_player_y   ; ViewScrollYをPlayerYから計算
            ;call CallEF09_draw_bg2line          ; 背景２ライン描画
            ;call CallEF0B0C                             ; 高速ステージ専用描画あり描画
            call API08_ending_sprites_draw_vvram  ; ※全敵スプライト表示
            ;call CallEF06_draw_player_num               ; プレイヤー数表示
            call CallGF09_copy_vram_attr                ; VRAM属性を仮想VRAM属性から転送
            ;call API21_check_break_key                  ; BREAK キーが押されてたらジャンプ
            ;jp z,title_init
            pop bc
            djnz ending_loop2 ; b を1引いて0以外でジャンプ
            ; -------------------
        ; 12 フレームごとにエンディングスクリプト実行
        ld iy,(ending_script_ptr)
        call API0A_exec_ending_script ; ※エンディングスプライト実行
        inc iy
        ld (ending_script_ptr),iy
        ld a,(iy+0)
        or a
        jp p,ending_loop1 ; 値がプラスのうちはループ
    ; ------------------------------
    ; 文字列描画 7,12 "1988 PROGRAM BY K.FURUHATA"
    ;ld hl,00c07h
    ;ld (IPL_ROM_STRING_POSISION_01171h),hl
    ;ld de,copy_txt
    ;rst 18h
    ; ------------------------------
    ; 文字列描画 7,14 "GAME CHECKED BY H.MIYAUCHI"
    ;ld hl,00e07h
    ;ld (IPL_ROM_STRING_POSISION_01171h),hl
    ;ld de,game_check_txt
    ;rst 18h
    ; ------------------------------
    ; 文字列描画 7,12 "1988 PROGRAM BY K.FURUHATA" のアトリビュート
    ;ld hl,VRAM_ATTR_0d9e7h_7x12
    ;ld de,VRAM_ATTR_0d9e8h_8x12
    ;ld bc,00019h
    ;ld (hl),070h
    ;; hl → de に、bc バイト転送
    ;ldir
    ;; -------------------------------------
    ;; "GAME CHECKED BY H.MIYAUCHI" のアトリビュート
    ;ld hl,VRAM_ATTR_0da37h_7x14
    ;ld de,VRAM_ATTR_0da38h_8x14
    ;ld bc,00019h
    ;ld (hl),070h
    ;; hl → de に、bc バイト転送
    ;ldir
    ;; -------------------------------------
    ;di
    ;    call BELL
    ;    ld a,014h
    ;    ; -----------------
    ;    ending_loop3:
    ;        cpi
    ;        jp pe,ending_loop3
    ;        dec a
    ;        jr nz,ending_loop3
    ;    ; -----------------
    ;ei
    ;call BELL
    ;call BELL
    ;jp title_init
    jp EndingScriptScene

;copy_txt:       "1988 PROGRAM BY K.FURUHATA",0dh
;game_check_txt: "GAME CHECKED BY H.MIYAUCHI",0dh
;ending_spj_ptr:     dw 00000h
ending_script_data:
    ;  1, 2, 3, 4, 5, 6, 7, 8, 9
    db 1, 1, 1, 1, 1, 1, 1, 1, 1 ; ツリーな部分が 9 個
    ;  1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24
    db 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ; 雑魚24個
    db 1 ; マンモス
    db 0, 0, 0, 0, 0, 0 ; IDAや爆発、トモス 6個
    ;  1, 2, 3, 4, 5, 6, 7, 8, 9,10
    db 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ; DOM 10体
    db 0 ; 草
    db 1, 1, 1, 1 ; やし、タワー4つ
    ;  1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18,19,20,21,22
    db 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ; ビーン、ボス
    db 1, 1 ; wiwi jambo
    db 0 ; ルーパー
    db 1 ; wiwi jambo
    ;  1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31
    db 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    db 1, 1    ; 氷の柱とドム
    db 0, 0    ; 岩2個
    db 1       ; 機械の柱
    db 9, 9, 9, 9, 9, 9, 9, 9  ; 消す
    db -1               ; 終了
;ending_script_ptr:  dw 00000h

CallEF04_draw_raster_attr:       ; 仮想VRAM属性にラスタ属性を描画
EF04_draw_raster_attr:
draw_raster_attr:
    ld hl,VIRTUAL_ATTR_CLEAR_BYTE_0c1cch_12x7_ATTR_0x1+4
    ld b,24
    ld a,8
    ef4_loop:
        push bc
        ld (hl),a
        inc a
        and 7
        or 8
        ld d,h
        ld e,l
        inc de
        ld bc,31
        ldir ; (de)<-(hl)
        ld bc,33
        add hl,bc
        pop bc
        djnz ef4_loop
    ret

; --------------------------------------------------------------------------
; エンディング専用処理
API08_ending_sprites_draw_vvram:
    ld ix, ENDING_SCRIPT_WORK_0ce69h
    ld b,8
    api08_loop1: ; 敵描画ループ 8回
        push bc
        ld a,(ix+0)
        or a
        jr z,api08_cont1 ; 種別が0以外なら描画
            ; 仮想VRAMへのデータ転送 -----------------------
            ld b,11     ; 幅
            ld l,(ix+1) ; 転送先 Y座標
            ld h,(ix+2) ; 転送先 X座標
            ld c,(ix+3) ; 高さ
            ld e,(ix+4) ; de: 転送元アドレス
            ld d,(ix+5)
            call CallGF0F_draw_vvram
        api08_cont1:
        pop bc
        ld de,6 ; 次の敵スプライト
        add ix,de
        djnz api08_loop1 ; b を1引いて0以外ならジャンプ
    ret

; --------------------------------------------------------------------------
; すべてのエネミースプライト位置を更新
; - X座標をデクリメント（画面左にスクロール）、マイナスになるとスプライトを無効化
; エンディング用のスプライトを左に移動
API09_ending_sprites_move_left:
    ld hl,ENDING_SCRIPT_WORK_0ce69h
    ld b,4
    ld de,0x0006
    ; X座標復号ループ
    api09_loop1:
        ld a,(hl)
        or a
        jp z,api09_cont1 ; タイプが0なら飛ばす
            inc hl
            inc hl
            dec (hl) ; x座標を減らす
            ld a,(hl)
            dec hl
            dec hl
            cp 16-11
            jp nz,api09_cont1
                ld (hl),d ; マイナス値なら消す(dは必ずゼロ)
        ; 次のスプライトX復号
        api09_cont1:
        add hl,de
        ; b を1引いて0ならジャンプしない
        djnz api09_loop1
    ret

; --------------------------------------------------------------------------
; 空きエンディングスプライトスロット検索
; エンディング専用処理
Api0a_sub1_find_empty_ending_sprite:
    ld ix,ENDING_SCRIPT_WORK_0ce69h
    ld de,6
    ld b,4
    ; アクティブスプライト検索ループ
    api0a_sub1_loop1:
        ld a,(ix+0)
        or a
        ret z
        add ix,de
        ; b を1引いて0ならジャンプしない
        djnz api0a_sub1_loop1
    scf
    ret
; --------------------------------------------------------------------------
; 新しいエンディングスプライトを作成し初期化
; - 空きエンディングスプライト位置をもとにデータを埋め選ぶ
; エンディング専用処理
API0A_exec_ending_script:
    call Api0a_sub1_find_empty_ending_sprite    ; 空スプライトを検索
    ret c ; ないなら帰る
    ; スプライト初期化
    ld (ix+0),1
    ld (ix+1),13
    ld (ix+2),48
    ld hl,(ending_spj_ptr)
    ld (ix+4),l
    ld (ix+5),h
    ld (ix+3), 10 ; iy[0]が0なら10
    ld a,(iy+0)
    cp 9
    jp z,api0a_cont2 ; iy[0] が9なら消す
        ld de, 10*11
        or a
        jp z,api0a_cont1; iy[0] が0ならそのままde = 10*11
            ; iy[0] が 0 以外なら
            ld (ix+3), 10*2
            ld de, 10*11*2
            ld (ix+1), 10   ; y座標かな？ちょっと上
        api0a_cont1:
        ; 敵データポインタ更新
        add hl,de
        ld (ending_spj_ptr),hl
        ret
    api0a_cont2:; iy[0] が9なら消す
    ; 敵削除
    ld (ix+0),000h
    ret


; --------------------------------------------------------------------------
; 仮想VRAMへのデータ転送
; de: 転送元アドレス b: 幅 c: 高さ
; h: 転送先 X座標 l: 転送先 Y座標
CallGF0F_draw_vvram:
GF0F_draw_vvram:
    ld a,040h       ; a = 0x40
    sub b           ; a = 0x40 - b
    
    ex af,af'
    ;ld (gff_rp+1),a ; gff_rp[1]=0x40-b
    push de
        ld e,h      ; e = h
        ld d,000h   ; de = h
        ld h,d      ; h = 0
        ld a,l      ; a = l
        add a,a     ; a = l * 2
        add a,a     ; a = l * 4
        add a,a     ; a = l * 8
        ld l,a      ; l = l * 8; hl = l * 8
        add hl,hl   ; hl = l * 16
        add hl,hl   ; hl = l * 32
        add hl,hl   ; hl = l * 64
        add hl,de   ; hl = l * 64 + h
        ld de,VIRTUAL_VRAM_0c000h_0x0
                    ; de = VIRTUAL_VRAM_0c000h_0x0
        add hl,de   ; hl = VIRTUAL_VRAM_0c000h_0x0 + l * 64 + h
    pop de
    gff_loop1:; ループ1
        push bc
            gff_loop2:; ループ2
                ld a,(de)       ; a = de[0]
                or a
                jp m,gff_cont2  ; マイナス値なら転送なし
                    ld (hl),a   ; 仮想VRAMに転送
                gff_cont2:
                inc de          ; 転送元アドレスインクリメント
                inc l           ; 転送先アドレスインクリメント
                djnz gff_loop2
            ;gff_rp:
            ;ld c,03bh
            ex af,af'
            ld c,a
            ex af,af'
            add hl,bc
        pop bc
        dec c
        jp nz,gff_loop1
    ret

; --------------------------------------------------------------------------
; VRAM属性を仮想VRAM属性から転送
; (0,0)-(32,24)の範囲のVRAM属性を転送して表示します。
CallGF09_copy_vram_attr:        ; VRAM属性を仮想VRAM属性から転送
GF09_copy_vram_attr:
copy_vram_attr:
	ld hl,copy_flg
    ld a,1
    ld (hl),a
	loop1:
		cp (hl)
		jr z,loop1
	ret
wait_copy:
	ld hl,copy_flg
    xor a
	loop2:
		cp (hl)
		jr nz,loop2
	ret

h_timi_new:
    ld a,(copy_flg)
    or a
    ret z
    xor a
    ld (copy_flg),a
    
    exx
    ld hl,VIRTUAL_ATTR_CLEAR_BYTE_0c1cch_12x7_ATTR_0x1+4
    ld de,01800h
    ; 8x3=24ライン分
    exx
    ld b,24
    ; VRAM ATTR クリアループ
    gf9_clear_vram_loop:
        exx
        di
        ; 転送アドレス設定
        ld a,e
        out (099h),a
        ld a,d
        or 040h
        out (099h),a
        ld c,098h
        ld b,32
        otir
        ei
        ; バッファの幅が64個なのでずらす
        ld c,020h
        add hl,bc
        ex de,hl
        add hl,bc
        ex de,hl
        exx
        djnz gf9_clear_vram_loop
    jp h_timi_old

    include "spj.asm"

    ; ROMサイズを32KB（最小サイズ）に合わせるためのパディング
    ds 0C000h-$,0
