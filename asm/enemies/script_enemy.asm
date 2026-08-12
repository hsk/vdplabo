; --------------------------------------------------------------------------
; 敵出現スクリプト初期化
; ENEMY_SPAWN_SCRIPT_0cc77h = gf20_escript_tbl[(stage - 1)]
GF20_InitEnemySpawnScript:
    ld a,(GAME_STAGE)   ; a = stage
    dec a               ; a = stage - 1
    add a,a             ; a = (stage - 1) * 2
    ld e,a              ; e = (stage - 1) * 2
    ld d,000h           ; de = (stage - 1) * 2
    ld hl,gf20_enemy_spawn_scripts ; hl = gf20_escript_tbl
    add hl,de           ; hl = gf20_escript_tbl + (stage - 1) * 2
    ; de = gf20_escript_tbl[(stage - 1)]
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld (ENEMY_SPAWN_SCRIPT_0cc77h),de ; ENEMY_SPAWN_SCRIPT_0cc77h = gf20_escript_tbl[(stage - 1)]
    ret
; --------------------------------------------------------------------------
gf20_enemy_spawn_scripts:
gf20_enemy_spawn_scripts_start:
    dw escript1,escript2,escript3,escript4,escript_bonus,escript6,escript7
    dw escript8,escript9,escript10,escript11,escript_bonus,escript13
    dw escript14,escript15,escript16,escript17,escript_bonus
; --------------------------------------------------------------------------
; 空スプライト検索
; 見つかったら ixにアドレスが入り、見つからなかったらキャリーフラグが立つ
; b,de,af が破壊
GF22_findEmptyEnemySprite:
    ; find_first_active_sprite
    ld b,010h
    ld de,00018h
    ld ix,ENEMIES
    gf22_loop1:
        ld a,(ix+000h)
        or a
        ret z
        add ix,de
        djnz gf22_loop1
    scf
    ret
; --------------------------------------------------------------------------
; GF24: 敵出現スクリプト実行
;   - 0cc77h が指す敵配置テーブルからデータを読み出し、敵を生成する
;   - 1フレームにつき2バイト（2エントリ）ずつ処理を進める
; --------------------------------------------------------------------------
GF24_runEnemySpawnScript:
    ld iy,(ENEMY_SPAWN_SCRIPT_0cc77h)   ; 敵出現スクリプトをiyに設定
    call Gf24_sub1_run1EnemySpawnScript ; 1つ目のデータ処理（敵出現判定）
    inc iy
    call Gf24_sub1_run1EnemySpawnScript ; 2つ目のデータ処理（敵出現判定）
    inc iy
    ld (ENEMY_SPAWN_SCRIPT_0cc77h),iy   ; 敵出現スクリプトを保存
    ret
    ; --------------------------------------------------------------------------
    ; 敵Y位置更新ルーチン: IY+0の敵タイプ値からアニメーションパターン数を読み、
    ; 指定回数だけアニメーションループを実行してXY座標を更新する
    Gf24_sub1_run1EnemySpawnScript:
        ld a,(iy+000h)
        dec a
        ; 出現なしなら終了
        ret m                   ; if (iy[0] == 0) return
        ; 敵出現数を読み込み
        ld e,a
        ld d,000h
        ld hl,gf24_sub1_enemy_spawn_cnt_tbl
        add hl,de
        ld a,(hl)               
        ld (gf24_enemy_spawn_cnt),a ; gf24_enemy_spawn_cnt = gf24_sub1_enemy_spawn_cnt_tbl[iy[0]-1]
        ; 敵出現ループ(出現数分のループ)
        gf24_sub1_loop1:
            call GF22_findEmptyEnemySprite ; 空スプライト検索
            ret c
            ; 空なスプライトが見つかった
            call Gf24_sub2_setup_sprite_no_and_base_info; 敵番号と基本データを設定
            call Gf24_sub3_copy_enemy_data_to_sprite    ; 敵データテーブルからスプライトに設定
            call Gf24_sub4_call_init_function           ; 敵初期化関数呼び出し
            call Gf24_sub5_dispatch_SoundInit           ; 敵出現番号によって SoundUpdate2

            ld a,(gf24_enemy_spawn_cnt)                 ; gf24_enemy_spawn_cnt カウントダウン
            dec a
            ld (gf24_enemy_spawn_cnt),a
            jp nz,gf24_sub1_loop1
        ret
    ; --------------------------------------------------------------------------
    gf24_enemy_spawn_cnt:
        nop
    ; --------------------------------------------------------------------------
    ; 敵出現番号に基づいてSoundInitを実行
    Gf24_sub5_dispatch_SoundInit:
        ret
    ; --------------------------------------------------------------------------
    ; 敵データテーブルからスプライトに設定
    Gf24_sub3_copy_enemy_data_to_sprite:
        ld a,(iy+000h)                  ; a=敵出現番号
        dec a                           ; a=敵出現番号-1
        add a,a                         ; a=(敵出現番号-1)*2
        ld e,a                          ; e=(敵出現番号-1)*2
        ld d,000h                       ; de=(敵出現番号-1)*2
        ld hl,gf24_sub3_enemy_data_tbl  ; hl = gf24_sub3_enemy_data_tbl
        add hl,de                       ; hl = gf24_sub3_enemy_data_tbl + (敵出現番号-1)*2
        ld e,(hl)                       ; de = gf24_sub3_enemy_data_tbl[敵出現番号-1]
        inc hl
        ld d,(hl)
        ex de,hl                        ; hl = gf24_sub3_enemy_data_tbl[敵出現番号-1]
        ld de,gf24_sub3_enemy_setpos    ; de = gf24_sub3_enemy_setpos
        ld b,007h                       ; b = 7
        ; --------------
        ; hl = gf24_sub3_enemy_data_tbl[敵出現番号-1]
        ; de = gf24_sub3_enemy_setpos
        ; b = 7
        gf24_sub3_loop1:
            ; スプライトの設定位置を取得、設定
            ld a,(de)
            ld (gf24_sub3_rp1+2),a
            ld a,(hl)                   ; 設定データ読み込み
            gf24_sub3_rp1:
            ld (ix+00dh),a              ; 設定データを設定位置に設定
            ld a,(gf24_enemy_spawn_cnt) ; a=出現連番
            ld c,a                      ; c=出現連番
            ld a,003h                   ; a=3
            sub c                       ; a=3-出現連番
            add a,a                     ; a=(3-出現連番)*2
            add a,a                     ; a=(3-出現連番)*4
            add a,a                     ; a=(3-出現連番)*8
            dec a                       ; a=(3-出現連番)*2-1
            ld (ix+007h),a              ; 7番目に (3-出現連番)*2-1 を設定
            inc de                      ; ポインタを１つ進める
            inc hl
            djnz gf24_sub3_loop1
        ret
    ; --------------------------------------------------------------------------
    gf24_sub3_enemy_setpos:
    gf24_sub3_enemy_setpos_start:
        db 003h,004h,005h,006h,00ah,00bh
    gf24_sub3_enemy_setpos_last:
        db 00dh
    ; --------------------------------------------------------------------------
    ; 敵番号と基本データを設定
    Gf24_sub2_setup_sprite_no_and_base_info:
        ; 敵出現番号取得
        ld a,(iy+000h)
        dec a
        ; 敵番号テーブルを引く
        ld e,a
        ld d,000h
        ld hl,gf24_sub2_enemy_no_tbl
        add hl,de
        ld a,(hl)
        ; 敵番号をスプライトに設定
        ld (ix+000h),a                  ; ix[IX_TYPE] = gf24_sub2_enemy_no_tbl[iy[0]-1]
        ; スプライトの各フィールドを初期化
        ld (ix+008h),000h
        ; ----------
        ; 敵出現番号がenemy_spawn_no < 0x24 なら 009hに1セットそれ以外は0
        ld a,(iy+000h)
        cp 024h
        ld a,000h
        adc a,000h
        ld (ix+009h),a  ; ix[9] = 1 if enemy_spawn_no < 0x24 else 0
        ; ----------
        ld (ix+00ch),000h
        ld (ix+00eh),001h
        ld (ix+010h),000h
        ld (ix+011h),000h
        ld (ix+012h),000h
        ld (ix+013h),000h
        ld (ix+014h),000h
        ret
    ; --------------------------------------------------------------------------
    ; 出現用関数呼び出し
    Gf24_sub4_call_init_function:
        ; 敵出現番号取得
        ld a,(iy+000h)
        dec a
        add a,a
        ld e,a
        ld d,000h
        ld hl,gf24_sub4_data
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ex de,hl
        jp (hl)
    ; --------------------------------------------------------------------------
    ; 出現連番により 1: 0xff 2: 0x04 3:0x08を(ix+7)に設定
    es1:
        ; 出現連番により 1: 0xff 2: 0x04 3:0x08を(ix+7)に設定
        ld a,(gf24_enemy_spawn_cnt)
        ld (ix+007h),0ffh
        dec a
        ret z
        ld (ix+007h),004h
        dec a
        ret z
        ld (ix+007h),008h
        ret
    ; --------------------------------------------------------------------------
    ; 出現連番により 1: 0x9 2: 0x1a 3:0x28を(ix+5)に設定
    es2:
        ; 出現連番により 1: 0x9 2: 0x1a 3:0x28を(ix+5)に設定
        ld a,(gf24_enemy_spawn_cnt)
        ld (ix+005h),009h
        dec a
        ret z
        ld (ix+005h),01ah
        dec a
        ret z
        ld (ix+005h),028h
    ; --------------------------------------------------------------------------
    ; 何もなし
    es0:
        ret
    ; --------------------------------------------------------------------------
    ; (ix+5) = (10から41)のランダム値
    ; (ix+7) = 出現連番*2
    es4:
        ; プログラムのCPUを実行するごとに変わるレジスタ値がrでそれをaに設定
        ld a,r                      ; a = rnd
        and 01fh                    ; a = rnd & 31
        add a,00ah                  ; a = (rnd & 31) + 10
        ld (ix+005h),a              ; (ix+5)= (rnd & 31) + 10  = (10から41)のランダム値
        ld a,(gf24_enemy_spawn_cnt) ; a = 出現連番
        add a,a                     ; a = 出現連番*2
        add a,a                     ; a = 出現連番*4
        ld (ix+007h),a              ; (ix+7) = 出現連番*2
        ret
    ; --------------------------------------------------------------------------
    ; 出現連番により 1: 0x1a 2: 0xc 3:0x26を(ix+5)に設定
    es5:
        ld a,(gf24_enemy_spawn_cnt)
        ld (ix+005h),01ah
        dec a
        ret z
        ld (ix+005h),00ch
        dec a
        ret z
        ld (ix+005h),026h
        ret
    ; --------------------------------------------------------------------------
    ; (ix+7) = 出現連番*12
    es6:
        ld a,(gf24_enemy_spawn_cnt) ; a = 出現連番
        add a,a                     ; a = 出現連番*2
        add a,a                     ; a = 出現連番*4
        ld c,a                      ; c = 出現連番*4
        add a,a                     ; a = 出現連番*8
        add a,c                     ; a = 出現連番*12
        ld (ix+007h),a              ; (ix+7) = 出現連番*12
        ret
    ; --------------------------------------------------------------------------
    ; 出現連番1: (ix+7)=0xff;(ix+4)=0x14;(ix+5)=0x28
    ; 出現連番2: (ix+7)=0xff;(ix+4)=0x14;(ix+5)=0x03
    ; 出現連番3: (ix+7)=0xff;(ix+4)=0x0a;(ix+5)=0x32
    es7:
        ; a = 出現連番
        ld a,(gf24_enemy_spawn_cnt)
        ld (ix+007h),0ffh
        ld (ix+004h),014h
        ld (ix+005h),028h
        dec a
        ret z
        ld (ix+005h),03ch
        dec a
        ret z
        ld (ix+004h),00ah
        ld (ix+005h),032h
        ret
    ; --------------------------------------------------------------------------
    ; 出現連番1: (ix+7)=0xff;(ix+4)=0x14;(ix+5)=0x00
    ; 出現連番2: (ix+7)=0xff;(ix+4)=0x14;(ix+5)=0x14
    ; 出現連番3: (ix+7)=0xff;(ix+4)=0x0a;(ix+5)=0x0a
    es8:
        ld a,(gf24_enemy_spawn_cnt); a = 出現連番
        ld (ix+007h),0ffh
        ld (ix+004h),014h
        ld (ix+005h),000h
        dec a
        ret z
        ld (ix+005h),014h
        dec a
        ret z
        ld (ix+004h),00ah
        ld (ix+005h),00ah
        ret
    ; --------------------------------------------------------------------------
    ; 出現連番1: (ix+7)=0xff;(ix+4)=0x0f;(ix+5)=0x0e
    ; 出現連番2: (ix+7)=0xff;(ix+4)=0x0f;(ix+5)=0x26
    ; 出現連番3: (ix+7)=0xff;(ix+4)=0x03;(ix+5)=0x1a
    es9:
        ld a,(gf24_enemy_spawn_cnt)    ; a = 出現連番
        ld (ix+007h),0ffh
        ld (ix+004h),00fh
        ld (ix+005h),00eh
        dec a
        ret z
        ld (ix+005h),026h
        dec a
        ret z
        ld (ix+004h),003h
        ld (ix+005h),01ah
        ret
    ; --------------------------------------------------------------------------
    ; 敵番号テーブル(1度に２回呼ばれる)
    escript1: db 2,0,0,0,1,0,0,0,0,0,4,0,3,0,35,0,0,0,0,0,6,0,0,0,5,6,0,0,35,0,0,0,0,0,0,0,0,0,0,0
    escript2: db 17,0,16,0,0,19,0,0,15,0,30,33,0,0,0,0,17,0,16,0,19,0,0,0,0,0,0,0,29,32,0,0,0,0,0,0,0,0,0,0
    escript3: db 21,0,8,0,3,0,0,0,9,0,10,0,0,0,21,0,4,0,0,0,18,0,0,0,21,0,18,0,0,0,18,0,20,0,20,0,0,0,0,0
    escript4: db 0,0,0,0,0,0,3,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,5,6,0,0,0,0,0,0,0,0
    escript6: db 22,0,24,0,25,0,25,0,24,0,25,0,38,39,0,0,24,0,24,0,25,0,26,0,25,0,26,0,0,0,22,39,0,0,42,0,0,0,0,0
    escript7: db 23,0,13,0,0,0,44,0,44,0,0,0,12,0,35,0,0,0,0,0,38,39,0,0,11,0,13,0,45,0,38,0,0,0,43,0,0,0,0,0
    escript8: db 31,34,0,0,0,0,13,0,13,0,0,0,39,44,0,0,35,0,0,0,0,0,29,32,13,0,0,0,39,0,0,0,41,0,47,0,0,0,0,0
    escript9: db 0,0,0,0,0,0,4,0,0,0,0,0,0,0,7,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,5,6,0,0,0,0,0,0,0,0
    escript10: db 0,0,26,0,7,0,8,0,1,0,0,0,3,4,25,0,26,0,0,0,21,0,7,8,0,0,7,8,21,0,0,0,26,0,25,0,0,0,0,0
    escript11: db 38,0,44,0,0,0,49,0,37,0,36,0,48,0,0,0,45,0,42,43,0,0,44,0,40,41,46,0,50,0,42,43,40,41,47,0,0,0,0,0
    escript13: db 0,0,28,0,27,0,0,0,10,0,9,0,0,0,24,0,0,0,0,0,0,0,4,51,0,0,43,0,0,0,41,0,43,0,0,0,0,0,0,0
    escript14: db 0,0,0,0,0,0,4,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,5,6,0,0,0,0,0,0,0,0
    escript15: db 35,0,0,0,0,0,13,0,13,0,0,0,43,0,52,0,0,0,29,32,41,0,0,0,29,32,43,0,0,0,43,0,43,0,0,0,0,0,0,0
    escript16: db 39,0,38,0,49,0,47,0,36,37,48,0,42,43,45,0,40,41,50,0,44,0,45,0,42,0,41,0,43,0,43,0,42,43,40,41,0,0,0,0
    escript17: db 0,0,31,34,0,0,13,0,13,0,0,0,43,0,0,0,50,0,40,0,0,0,30,33,0,0,43,0,46,0,0,0,40,0,0,0,0,0,0,0
    escript_bonus: db 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    ; --------------------------------------------------------------------------
    ; 敵出現数テーブル
    gf24_sub1_enemy_spawn_cnt_tbl:
        ;  1,2,3,4,5,6,7,8,9,10
        db 3,3,3,3,3,3,3,3,3,3 ;  1-10
        db 3,3,3,3,3,3,3,3,4,7 ; 11-20
        db 7,3,3,3,3,3,3,3,1,2 ; 21-30
        db 3,1,2,3,3,1,1,1,1,1 ; 31-40
        db 1,1,1,3,3,1,1,1,1,3 ; 41-50
        db 1,1,4,1,1,1,1,1,1,1 ; 51-60
        db 1,1,1,1,1           ; 61-65
    ; 敵番号テーブル
    gf24_sub2_enemy_no_tbl:
        ;   1, 2, 3, 4, 5, 6, 7, 8, 9,10
        db 10,10,10,10,10,10,10,10,10,10 ;  1-10
        db 10,10,10,10,11,11,11,12,17,13 ; 11-20
        db 13,14,14,15,16,16,16,16,17,17 ; 21-30
        db 17,17,17,17,18,19,19,19,19,20 ; 31-40
        db 20,20,20,21,21,22,22,22,22,22 ; 41-50
        db 22,22,17,17, 1, 1, 1, 1, 1, 1 ; 51-60
    ; --------------------------------------------------------------------------
    gf24_sub4_data:
        ;       0,  1,  2,  3,  4,  5,  6,  7
    es_01: dw es2,es0,es0,es0,es0,es0,es0,es0
    es_09: dw es0,es0,es0,es0,es0,es0,es0,es0
    es_11: dw es0,es5,es6,es4,es4,es0,es0,es2
    es_19: dw es0,es0,es7,es8,es1,es1,es1,es1
    es_21: dw es1,es1,es9,es0,es0,es0,es0,es0
    es_29: dw es0,es0,es0,es0,es0,es0,es0,es0
    es_31: dw es0,es9,es0,es0,es0,es0,es0,es0
    es_39: dw es0,es0,es0,es0,es0,es0,es0,es0
    es_41: dw es0,es0,es0,es0,es0,es0,es0,es0
    es_49: dw es0,es0,es0,es0,es0
    gf24_sub3_enemy_data_tbl:
        dw ed01,ed02,ed03,ed04,ed05,ed06,ed07,ed08,ed09,ed10 ;  1-10
        dw ed11,ed12,ed13,ed14,ed15,ed16,ed17,ed18,ed19,ed20 ; 11-20
        dw ed21,ed22,ed23,ed24,ed25,ed26,ed27,ed28,ed29,ed30 ; 21-30
        dw ed31,ed32,ed33,ed34,ed35,ed36,ed37,ed38,ed39,ed40 ; 31-40
        dw ed41,ed42,ed43,ed44,ed45,ed46,ed47,ed48,ed49,ed50 ; 41-50
        dw ed51,ed52,ed53,ed01,ed01                          ; 51-55
    ; --------------------------------------------------------------------------
        ;                             AINO,
        ;       3,   4,   5,   6,00ah,00bh,00dh    ; 設定位置
    ed01: db 00eh,014h,020h,000h,009h,028h,003h ; ムカデンス 1,アイダ9,キノコ雲1
    ed02: db 009h,000h,000h,000h,009h,00fh,003h ; ムカデンス 2
    ed03: db 002h,010h,003h,000h,009h,010h,003h ; ムカデンス 3
    ed04: db 002h,010h,035h,000h,009h,011h,003h ; ムカデンス 4
    ed05: db 002h,010h,03fh,000h,009h,012h,003h ; ムカデンス 5
    ed06: db 002h,010h,003h,000h,009h,013h,003h ; ムカデンス 6
    ed07: db 002h,010h,004h,000h,009h,014h,003h ; ムカデンス 7
    ed08: db 002h,010h,030h,000h,009h,015h,003h ; ムカデンス 8
    ed09: db 01bh,014h,00dh,000h,009h,016h,003h ; ムカデンス 9
    ed10: db 01bh,014h,031h,000h,009h,017h,003h ; ムカデンス 10
    ed11: db 016h,014h,000h,000h,009h,018h,003h ; ムカデンス 11
    ed12: db 016h,014h,039h,000h,009h,019h,003h ; ムカデンス 12
    ed13: db 012h,000h,028h,000h,009h,01ah,003h ; ムカデンス 13
    ed14: db 002h,010h,000h,000h,009h,029h,003h ; ムカデンス 14
    ed15: db 010h,000h,000h,000h,009h,00ah,003h ; スケグ1
    ed16: db 006h,003h,000h,000h,009h,00bh,003h ; スケグ2
    ed17: db 006h,003h,030h,000h,009h,00ch,003h ; スケグ3
    ed18: db 01bh,00dh,020h,000h,003h,002h,003h ; カナリー1
    ed19: db 01bh,015h,01ah,000h,000h,001h,004h ; アイダ1
    ed20: db 01bh,00fh,020h,000h,000h,006h,003h ; ルーパー1
    ed21: db 01bh,00bh,020h,000h,000h,007h,003h ; ルーパー2
    ed22: db 01bh,00bh,028h,000h,009h,003h,003h ; パーコメン1
    ed23: db 013h,00bh,000h,000h,009h,004h,003h ; パーコメン2
    ed24: db 01bh,00fh,020h,000h,008h,002h,003h ; ジェット11
    ed25: db 01bh,010h,03ch,000h,007h,00dh,005h ; ジェット21
    ed26: db 01bh,010h,000h,001h,007h,00eh,005h ; ジェット22
    ed27: db 01bh,00ch,040h,000h,007h,00dh,005h ; ジェット23
    ed28: db 01bh,00ch,000h,001h,007h,00eh,005h ; ジェット24
    ed29: db 01bh,00ch,01eh,000h,003h,008h,005h ; アイダ2
    ed30: db 01bh,00ch,01eh,000h,003h,008h,005h ; アイダ3
    ed31: db 01bh,00ch,01eh,000h,003h,008h,005h ; アイダ4
    ed32: db 01bh,00ch,00eh,001h,003h,009h,005h ; アイダ5
    ed33: db 01bh,00ch,00eh,001h,003h,009h,005h ; アイダ6
    ed34: db 01bh,00ch,00eh,001h,003h,009h,005h ; アイダ7
    ed35: db 01bh,00bh,020h,003h,009h,005h,003h ; トモス1
    ed36: db 01bh,010h,028h,000h,004h,01bh,005h ; ドム緑1
    ed37: db 01bh,010h,00dh,001h,004h,01ch,005h ; ドム緑2
    ed38: db 01bh,010h,028h,001h,004h,01dh,005h ; ドム緑3
    ed39: db 01bh,010h,00dh,000h,004h,01eh,005h ; ドム緑4
    ed40: db 01bh,010h,028h,001h,005h,01dh,005h ; ドム赤1
    ed41: db 01bh,010h,00dh,000h,005h,01eh,005h ; ドム赤2
    ed42: db 01bh,010h,028h,001h,005h,01fh,005h ; ドム赤3
    ed43: db 01bh,010h,00dh,000h,005h,020h,005h ; ドム赤4
    ed44: db 01bh,010h,005h,000h,006h,021h,003h ; ドム黒1
    ed45: db 01bh,010h,032h,001h,006h,022h,003h ; ドム黒2
    ed46: db 002h,00ah,005h,003h,007h,023h,003h ; ドム青1
    ed47: db 002h,00ah,032h,003h,007h,024h,003h ; ドム青2
    ed48: db 01bh,010h,00fh,001h,007h,025h,003h ; ドム青3
    ed49: db 01bh,010h,027h,000h,007h,026h,003h ; ドム青4
    ed50: db 01bh,00ch,020h,002h,007h,027h,003h ; ドム青5
    ed51: db 01bh,010h,005h,000h,007h,025h,003h ; ドム青6
    ed52: db 01bh,010h,032h,000h,007h,026h,003h ; ドム青7
    ed53: db 01bh,015h,01ah,000h,000h,001h,004h ; アイダ8
