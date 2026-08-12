;; ending.asm

    ;; --------------------------------------------------------------------------
    ;; エンディングシーン
    ;EndingScene:
    ;    call CallSoundInit          ; サウンド初期化
    ;    ld sp,IPL_ROM_WORK_010f0h   ; スタック設定
    ;    call CallEF11
    ;    ld a,1
    ;    ld (api22_taget_camera_angle),a
    ;    ; エンディングシーケンス
    ;    call Ending_init_sub1_staff_roll
    ;    call Ending_init_sub2_load_staff_roll_data
    ;    call Ending_init_sub1_staff_roll
    ;    jp EndingScriptScene
    ;; =====================================================
    ;; ゲーム終了時の処理（エンディングスタッフロール）
    ;Ending_init_sub1_staff_roll:
    ;    call API25_player_move_top_center               ; 画面中央下にプレイヤーを移動
    ;    call CallGF16_calc_view_scrolly_from_player_y   ; ViewScrollYをPlayerYから計算
    ;    call API01_update_raster_field_attrs            ; 地面ラスタ属性更新
    ;    call API06_stage_specific_change_raster_field_attr  ; ステージ毎のラスタ地面属性変更
    ;    ld a,006h
    ;    ld (FRAME_CNT_0cc68h),a
    ;    ending_frame_loop:
    ;        call API04_SetViewScrollYTo6        ; 縦のスクロール値を6に設定
    ;        call CallGF05_enemies_zoom          ; 敵ズーム enemy.zoomx = (enemy.x-32) * (sprite_zoom_parameters[enemy.z] + 3) / 16+32
    ;        call CallGF06_enemy_scrolly         ; 敵キャラのY座標調整
    ;        call CallEF10_ending_bonus1         ; エンディング、ボーナス共通処理1
    ;        ld a,(FRAME_CNT_0cc68h)             ; フレームカウントダウン
    ;        dec a
    ;        ld (FRAME_CNT_0cc68h),a
    ;        jp p,ending_frame_loop
    ;    call CallGF2A_scrollx               ; スクロールX
    ;    call CallEF04_draw_raster_attr      ; 仮想VRAM属性にラスタ属性を描画
    ;    call CallEF0B0C                     ; 高速ステージ専用描画あり描画
    ;    call CallEF09_draw_bg2line          ; 背景２ライン描画
    ;    call API20_UpdateScrollAndEnemyPlacementAndDrawCastle   ; スクロール更新と敵配置チェック+ステージ06での城描画
    ;    call CallEF01_draw_enemies_shadow_and_player_shadow     ; 敵の影とプレイヤーの影描画
    ;    call CallEF0E_ending_bonus2         ; エンディング、ボーナス共通処理2
    ;    call CallEF03_player_draw           ; 条件付きプレイヤー画像の変更と描画
    ;    call CallEF06_draw_player_num       ; プレイヤー数表示
    ;    call CallGF09_copy_vram_attr        ; VRAM属性を仮想VRAM属性から転送
    ;    call API02_f1_f2_pause_key_check    ; F1,F2,ポーズ処理
    ;    ld bc,008aeh
    ;    _ending_staff_roll_loop2:
    ;        cpi
    ;    jp pe,_ending_staff_roll_loop2
    ;    call API03_exists_enemies           ; 敵存在判定
    ;    jp nz,Ending_init_sub1_staff_roll
    ;    ret
    ;; --------------------------------------------------------------------------
    ;; エンディング画面スタッフロール情報初期化
    ;; スタッフロール用データ（l20e3h）をスプライトワークエリア（0cc79h）にコピー
    ;; - 0x0090（144）バイトを転送してスタッフロール表示準備
    ;Ending_init_sub2_load_staff_roll_data:
    ;	; -------------------------------------
    ;	ld hl,staff_roll_data	;20d7	21 e3 20	! .
    ;	ld de,ENEMIES		;20da	11 79 cc	. y .
    ;	ld bc,STAFF_ROLL_DATA_SIZE	;20dd	01 90 00	. . .
    ;	; hl → de に、bc バイト転送
    ;	ldir			;20e0	ed b0		. .
    ;	; -------------------------------------
    ;	ret			;20e2	c9		.
    ;; --------------------------------------------------------------------------
    ;; スタッフロール表示用データテーブル
    ;; スプライト制御パラメータとダミーコード群
    ;staff_roll_data:
    ;	defb 00ah,000h,000h,01eh,008h,011h,000h,000h,000h,001h,000h,005h,000h,002h,000h,000h,078h,000h,000h,000h,000h,000h,000h,000h,00bh,000h,000h,01eh    ;20e3		"................x..........."
    ;	defb 008h,01bh,000h,000h,000h,001h,000h,005h,000h,002h,000h,000h,078h,000h,000h,000h,000h,000h,000h,000h,00ch,000h,000h,01eh,008h,027h,000h,000h,000h,001h,000h,005h,000h,002h    ;20ff		"............x............'........"
    ;	defb 000h,000h,078h,000h,000h,000h,000h,000h,000h,000h,00ch,000h,000h,01eh,014h,011h,000h,000h,000h,001h,000h,005h,000h,002h,000h,000h,078h,000h,000h,000h,000h,000h,000h,000h,00dh,000h,000h,01eh,014h,01bh,000h,000h,000h,001h,000h,005h,000h,002h,000h,000h,078h,000h,000h,000h,000h,000h,000h,000h,00eh,000h,000h,01eh,014h,027h,000h,000h,000h,001h,000h,005h,000h,002h,000h,000h,078h,000h,000h,000h,000h,000h,000h,000h,000h,000h,000h,000h,000h,000h,000h,000h,000h,000h    ;2121		"..x.......................x.......................x............'..........x................."
; spj.asm
