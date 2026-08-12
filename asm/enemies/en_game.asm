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

;; game.asm
; 通常ゲームシーン
init:
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
    call bg_field_init
    ld a,18
    ld (PLAYER_POS_Y),a
    ld a,30
    ld (PLAYER_POS_X),a

main:
    ld a,013h
    call bg_pre_draw
    call bg_draw
    call draw_raster_attr      ; 仮想VRAM属性にラスタ属性を描画
    call player_draw
    call player_move
    call wait_vsync
    call copy_vram_attr        ; VRAM属性を仮想VRAM属性から転送
    jp main
wait_vsync:
    ; VSYNC
    ld hl, JIFFY
    ld a, (hl)
    vsync:
        cp (hl)
        jr z, vsync
    ret

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

GameScene:
    ;ld sp,IPL_ROM_WORK_010f0h               ; スタック設定
    ;ld de,00001h                            ; 1点追加
    ;call CallGF15_add_score
    ;call CallControllGameProgress           ; ゲームの進捗管理(場合によってはボス開始を設定する)
    ;call CallGF01_player_move               ; プレイヤー移動
    ;call CallGF02_shots_update              ; ショット更新
    ;call CallGF1C_shots_collision           ; ショット当たり判定
    ;call CallGF02_shots_update              ; ショット更新
    ;call CallGF1C_shots_collision           ; ショット当たり判定
    ;call CallGF02_shots_update              ; ショット更新
    ;call CallGF1C_shots_collision           ; ショット当たり判定
    ;call CallGF03_shot_input                ; ショット入力
    ;call API01_update_raster_field_attrs    ; 地面ラスタ属性更新
    ;call CallGF16_calc_view_scrolly_from_player_y       ; ViewScrollYをPlayerYから計算
    ;call API06_stage_specific_change_raster_field_attr  ; ステージ毎のラスタ地面属性変更
    call CallGF01_player_move               ; プレイヤー移動
    ld a,006h
    ld (FRAME_CNT_0cc68h),a ; フレームループ a がカウンタ
    game_frame_loop:
        ; call CallGF1C_shots_collision           ; ショット当たり判定
        ; call CallGF1D_player_collision_enemies  ; プレイヤーと敵の当たり判定
        ; call API05_process_damage_and_gameover
        ; call CallAI1_update_enemies             ; 敵アップデート
        ld a, (FRAME_CNT_0cc68h)
        dec a
        ld (FRAME_CNT_0cc68h),a ; フレームカウントダウン
        jp p,game_frame_loop
    ; 描画計算 ----------------------------
    ;call API04_SetViewScrollYTo6        ; 縦のスクロール値を6に設定
    ;call CallGF05_enemies_zoom          ; 敵ズーム enemy.zoomx = (enemy.x-32) * (sprite_zoom_parameters[enemy.z] + 3) / 16+32
    ;call CallGF06_enemy_scrolly         ; 敵キャラのY座標調整
    ;call CallGF01_player_move           ; プレイヤー移動
    ;call CallGF18_enemy_sprite_scrollx  ; プレイヤー位置により敵横移動
    ;call CallGF2A_scrollx               ; スクロールX
    ;call CallGF0E_update_ceil_and_ceil_raster_attr    ; キーボード入力チェック付き天井ラスタ属性更新
    ; 仮想画面描画 ------------------------
    call CallEF04_draw_raster_attr      ; 仮想VRAM属性にラスタ属性を描画
    ;call CallEF0B0C                     ; 高速ステージ専用処理あり処理
    ;call CallEF09_draw_bg2line_when_not_highspeed_stage     ; 高速ステージ以外で背景２ライン描画
    ;call API20_UpdateScrollAndEnemyPlacementAndDrawCastle   ; スクロール更新と敵配置チェック+ステージ06での城描画
    ;call CallEF01_draw_enemies_shadow_and_player_shadow     ; 敵の影とプレイヤーの影描画
    ;call CallEF07_DrawSprites           ; 敵スプライト描画
    ;call CallGF03_shot_input            ; ショット入力
    ;call CallEF02_shot_draw             ; ショット描画
    call CallEF03_player_draw           ; 条件付きプレイヤー画像の変更と描画
    ;call CallEF06_draw_player_num       ; プレイヤー数表示
    ;call CallGF26_draw_stage_name       ; ステージ名表示
    ; 実画面描画 ------------------------
    call CallGF09_copy_vram_attr        ; VRAM属性を仮想VRAM属性から転送
    ; 事後処理 ------------------------
    ;call API02_f1_f2_pause_key_check    ; F1,F2,ポーズ処理
    ; ボス開始判定
    ;ld a,(STAGE_BOSS_START_0ce5bh)
    ;or a
    ;jp nz,GameStageBossScene
    ; BREAK キーが押されていなかったらジャンプ
    ;call API21_check_break_key
    ;jp nz,GameScene
    ;jp GameStageBossScene
    jp GameScene

; --------------------------------------------------------------------------
; プレイヤー移動処理
; カーソルキー入力をしてプレイヤー位置を移動します
; プレイヤーの左上の座標になってる
; x: 12 〜 48 y: 7 〜 25
; PLAYER_POS_Yのhlのlにy hにxが入る
; 表示範囲は12x7-52x31
;CallGF01_player_move_mz70:
;GF01_player_move_mz70:
;    ; カーソルキー入力
;    ld a,007h
;    ld (KEY_OUT_PORT),a
;    ld a,(KEY_IN_PORT)
;    ld hl,(PLAYER_POS_Y)
;    ld b,a
;    ld a,l
;    ; 上キーチェック
;    bit 5,b
;    jp nz,gf1_1
;        ; 7 ならジャンプ
;        cp 007h
;        jp z,gf1_1
;            dec l
;    ; 下キーチェック
;    bit 4,b
;    jp nz,gf1_2
;        cp 019h
;        jp z,gf1_2
;            inc l
;    ld a,h
;    ; 左キーチェック
;    bit 2,b
;    jp nz,gf1_3
;        cp 00ch
;        jp z,gf1_3
;            dec h
;    ; 右キーチェック
;    bit 3,b
;    jp nz,gf1_4
;        cp 030h
;        jp z,gf1_4
;            inc h
;    ld (PLAYER_POS_Y),hl
;    ret

; --------------------------------------------------------------------------
; プレイヤー移動処理
; カーソルキー入力をしてプレイヤー位置を移動します
; プレイヤーの左上の座標になってる
; x: 12 〜 48 y: 7 〜 25
; PLAYER_POS_Yのhlのlにy hにxが入る
; 表示範囲は12x7-52x31
CallGF01_player_move:
GF01_player_move:
player_move:
    ; キー入力
    call KILBUF
    xor a
    call GTSTCK
    ld c,a
    ; カーソルキー入力
    ld hl,(PLAYER_POS_Y)
    ; 上チェック
    cp 0
    jr z, gf1_2        ; 0なら飛ぶ
    cp 3
    jr c, gf1_1            ; 1か2なら飛ぶ
    cp 8
    jr nz, gf1_2       ; 8でないなら飛ぶ
    gf1_1:
        ld a,l
        cp 007h
        jr z,gf1_3
            dec l
    gf1_2:
    ; 下チェック
    cp 4
    jr c, gf1_3      ; 4未満なら飛ぶ
    cp 7
    jr nc, gf1_3     ; 7以上なら飛ぶ
        ld a, l
        cp 019h
        jr nc, gf1_3
            inc l
    gf1_3:
    ld a, c
    ; 左チェック
    cp 6
    jr c, gf1_4
    cp 9
    jr nc, gf1_4
        ld a,h
        cp 00ch + 4
        jp z,gf1_5
            dec h
    gf1_4:
    ; 右チェック
    cp 2
    jr c, gf1_5     ; 2未満なら飛ぶ
    cp 5
    jr nc, gf1_5    ; 5以上なら飛ぶ
        ld a,h
        cp 030h-4
        jp z,gf1_4
            inc h
    gf1_5:
    ld (PLAYER_POS_Y),hl
    ret

; --------------------------------------------------------------------------
; プレイヤーの変更と描画
CallEF03_player_draw:           ; プレイヤー画像の変更と描画
EF03_player_draw:
player_draw:
    ;ld hl,IPL_ROM_WORK_01009h
    ;inc (hl)
    ;ld a,(hl)
    ;and 003h
    ;ld l,a
    ;ld h,000h
    ;ld de,spj_player_red_lamp_data
    ;add hl,de
    ;ld a,(hl)
    ;ld (spj_player_rp_red_lamp),a
    ;ld a,(DAMAGE_WORK_0cc56h)
    ;dec a
    ;jp m,ef3_cont1
    ;    ld (DAMAGE_WORK_0cc56h),a
    ;    ; player.y = 19 にする
    ;    ld a,019h
    ;    ld (PLAYER_POS_Y),a
    ;ef3_cont1:
    ; 入力タイマーチェック
    ;ld hl,DAMAGE_WORK_0cc52h
    ;bit 7,(hl)
    ;jp nz,ef3_cont2
    ;    dec (hl)
    ;    bit 0,(hl)
    ;    ret z
    ;ef3_cont2:
    ; プレイヤー画像初期化
    ; プレイヤーの足の書き換えをリセット
    ;ld ix,spj_player_rp2_leg
    ;ld (ix+000h),005h
    ;ld (ix+002h),005h
    ;ld (ix+004h),022h
    ;ld (ix+006h),022h
    ; 地面に接しているか判定
    ;ld a,(PLAYER_POS_Y)
    ;cp 019h
    ; 接してなければ足パタしない
    ;jp c,ef3_cont4
    ;ef3_rp:
    ;; 接してなければ足パタカウンタ書き換え
    ;ld a,000h
    ;inc a
    ;and 003h
    ;ld (ef3_rp+1),a
    ;; 足パタパターン判定
    ;cp 002h
    ;jp c,ef3_cont3
    ;    ; プレイヤー足パタ1
    ;    ld (ix+002h),022h
    ;    ld (ix+006h),0ffh
    ;    jp ef3_cont4
    ;ef3_cont3:
    ;    ; プレイヤー足パタ2
    ;    ld (ix+000h),022h
    ;    ld (ix+004h),0ffh
    ;ef3_cont4:
    ; プレイヤー描画準備
    ld hl,(PLAYER_POS_Y)
    ld de,spj_player
    ld bc,00406h
    ; プレイヤー描画
    jp Ef2_sub1_draw_vram_attr
; --------------------------------------------------------------------------
; プレイヤースプライトデータ 4x6 = 24bytes
spj_player:
    db 0ffh,066h,0ffh,0ffh
    db 022h,022h,022h,022h
    db 022h,005h,022h
spj_player_rp_red_lamp:
    db 000h
    db 055h,055h,055h,0ffh
spj_player_rp2_leg:
    db 005h,0ffh,005h,0ffh
    db 022h,0ffh,022h,0ffh
; --------------------------------------------------------------------------
; プレイヤーの赤黒明滅データ
spj_player_red_lamp_data:
    db 000h,002h,022h,002h

; --------------------------------------------------------------------------
; VRAM ATTR 描画
Ef2_sub1_draw_vram_attr:
    ld a,040h
    sub b
    exx
    ld e,a
    exx
    push de; 11T
    ld e,h
    ld d,000h
    ld h,d
    ld a,l
    add a,a
    add a,a
    add a,a
    ld l,a
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,de
    ld de,VIRTUAL_VRAM_0c000h_0x0
    add hl,de
    pop de ; 11T
    ; ループ1
    ef2_sub1_loop1:
        push bc
        ; VRAM転送内部
        ef2_sub1_loop2:
            ld a,(de)
            inc de
            or a
            jp m,ef2_sub1_cont1
                ld (hl),a
            ; 次のVRAM転送
            ef2_sub1_cont1:
            inc l
            ; b を1引いて0ならジャンプしない
            djnz ef2_sub1_loop2
        exx
        ld a,e
        exx
        ld c,a
        add hl,bc
        pop bc
        dec c
        jp nz,ef2_sub1_loop1
    ret

; --------------------------------------------------------------------------
; VRAM属性を仮想VRAM属性から転送
; (0,0)-(32,24)の範囲のVRAM属性を転送して表示します。
CallGF09_copy_vram_attr:        ; VRAM属性を仮想VRAM属性から転送
GF09_copy_vram_attr:
copy_vram_attr:
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
	ret









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
    include "bg_field.asm"
; -------------------------------------------
; stub functions
GameStageBossScene: jr GameStageBossScene
CallGF15_add_score: ret
CallControllGameProgress: ret           ; ゲームの進捗管理(場合によってはボス開始を設定する)
;CallGF01_player_move: ret               ; プレイヤー移動
CallGF02_shots_update: ret              ; ショット更新
CallGF1C_shots_collision: ret           ; ショット当たり判定
CallGF03_shot_input: ret                ; ショット入力
API01_update_raster_field_attrs: ret    ; 地面ラスタ属性更新
CallGF16_calc_view_scrolly_from_player_y: ret       ; ViewScrollYをPlayerYから計算
API06_stage_specific_change_raster_field_attr: ret  ; ステージ毎のラスタ地面属性変更
CallGF1D_player_collision_enemies: ret  ; プレイヤーと敵の当たり判定
API05_process_damage_and_gameover: ret
CallAI1_update_enemies: ret             ; 敵アップデート
API04_SetViewScrollYTo6: ret        ; 縦のスクロール値を6に設定
CallGF05_enemies_zoom: ret          ; 敵ズーム enemy.zoomx = (enemy.x-32) * (sprite_zoom_parameters[enemy.z] + 3) / 16+32
CallGF06_enemy_scrolly: ret         ; 敵キャラのY座標調整
CallGF18_enemy_sprite_scrollx: ret  ; プレイヤー位置により敵横移動
CallGF2A_scrollx: ret               ; スクロールX
CallGF0E_update_ceil_and_ceil_raster_attr: ret    ; キーボード入力チェック付き天井ラスタ属性更新
;CallEF04_draw_raster_attr: ret      ; 仮想VRAM属性にラスタ属性を描画
CallEF0B0C: ret                     ; 高速ステージ専用処理あり処理
CallEF09_draw_bg2line_when_not_highspeed_stage: ret     ; 高速ステージ以外で背景２ライン描画
API20_UpdateScrollAndEnemyPlacementAndDrawCastle: ret   ; スクロール更新と敵配置チェック+ステージ06での城描画
CallEF01_draw_enemies_shadow_and_player_shadow: ret     ; 敵の影とプレイヤーの影描画
CallEF07_DrawSprites: ret           ; 敵スプライト描画
CallEF02_shot_draw: ret             ; ショット描画
;CallEF03_player_draw: ret           ; 条件付きプレイヤー画像の変更と描画
CallEF06_draw_player_num: ret       ; プレイヤー数表示
CallGF26_draw_stage_name: ret       ; ステージ名表示
;CallGF09_copy_vram_attr: ret        ; VRAM属性を仮想VRAM属性から転送
API02_f1_f2_pause_key_check: ret    ; F1,F2,ポーズ処理
API21_check_break_key: ret

end:
    ; ROMサイズを16KB（最小サイズ）に合わせるためのパディング
    ds 08000h - $, 0
