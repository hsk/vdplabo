IPL_ROM_WORK_01010h:	equ 0x1010
IPL_ROM_WORK_01038h:	equ 0x1038
IPL_ROM_WORK_01039h:	equ 0x1039
AI_TIMER_0cc3fh:            equ 0xcc3f
FIELD_OBJ_SCRIPT_0cc40h:    equ 0xcc40
KEY_COUNTER:                equ 0xcc42
GAME_STAGE:                 equ 0xcc62
CEIL_STATE:                 equ 0xcc50
ENEMIES:                    equ 0xcc79
INPUT_MODE_WORK:            equ 0xcc57
ENEMY_SPAWN_SCRIPT_0cc77h:	equ 0xcc77
STAGE_BOSS_START_0ce5bh:    equ 0xce5b

    org 0

; --------------------------------------------------------------------------
; 地上物スクリプト初期化
GF0B_InitFieldObjScript:
    ld a,(GAME_STAGE)           ; a = stage
    dec a                       ; a = stage-1
    add a,a                     ; a = (stage-1)*2
    ld e,a                      ; e = (stage-1)*2
    ld d,000h                   ; de = (stage-1)*2
    ld hl,gfb_field_obj_scripts ; hl = gfb_field_obj_scripts
    add hl,de                   ; hl = gfb_field_obj_scripts + (stage-1)*2
    ld e,(hl)                   ; de = gfb_field_obj_scripts[stage-1]
    inc hl
    ld d,(hl)
    ld (FIELD_OBJ_SCRIPT_0cc40h),de ; FIELD_OBJ_SCRIPT_0cc40h[0] = de
    ret
; --------------------------------------------------------------------------
; 地上物スクリプトテーブル
gfb_field_obj_scripts:
gfb_field_obj_scripts_start:
    dw fos01,fos02,fos03,fos04,fos01,fos06,fos07,fos08,fos09,fos10,fos11,fos01,fos13,fos14,fos15,fos16,fos17,fos01
CEN: equ 063h ; 天井終わりコマンド
FEND: equ 0xff ; スクリプト終了コマンド
; --------------------------------------------------------------------------
fos01: ; 18,10,1 浮遊岩,草,木,
    db 18, 0, 18,10, 18, 0, 18, 0, 18, 0, 18,10, 18, 0, 18, 0
    db 18,10, 18, 0, 18, 1, 18, 1, 18, 1, 18, 1, 18, 1, 18, 1
    db 18, 1, 18, 1,  0, 0,  0, 0, FEND

fos02: ; 30,10,17,2,3,28 IDA,枯木,柱,岩
    db 30,10, 30, 0, 30,10,  0,17, 30, 0
    db  2, 0,  2,10,  2, 0,  2,17,  2, 0
    db  3,10,  2, 0,  2,10, 30,28, 30,17
    db  3,10,  3, 0,  3, 0,  0, 0,  0, 0, FEND
fos03: ; 13,8,19,20,29
    db 13, 0, 13, 8, 13,19, 13,20, 13, 0, 13, 8, 13,19
    db 13,20, 13, 0, 13, 8, 13,19, 13,20, 13, 0, 13, 8
    db 13,19, 13,20, 29, 0, 29, 0, 29, 0,  0, 0, FEND
fos04: ; 5,21,14,22,23,CEN
    db  5, 0, 21,14, 22, 0,  5, 0, 21,15, 22, 0,  5, 0
    db 21,14, 22, 0,  5, 0, 21,23, 22, 0,  5, 0, 21, 0
    db 22,14,  5, 0, CEN,0,  0, 0, FEND
fos06: ; 31,10,7,27,20
    db 31,10,  7, 0, 27,20,  0,20,  0,10,  7, 0,  7, 0
    db  7,10,  0,20,  0,10,  7,20,  7, 0,  7, 0,  7,10
    db 31, 0, 31,10, 31,20,  7,10,  0, 0,  0, 0, FEND
fos07: ; 25,11,9,28
    db 25, 0, 25,11, 25, 9,  0, 9,  0,25, 25, 0,  0, 9
    db 28,11, 25,11, 25, 9,  0,25, 11, 9, 28,25,  0,11
    db 28, 0, 28, 0, 28,11, 28,25,  0, 0,  0, 0, FEND
fos08: ; 2,20,28,17,12,10,3
    db  2,20,  2,28,  2,17,  2,12,  0,17,  0,10, 20,12
    db  3, 0,  3, 0,  3,20,  3,20,  3,12,  3, 0,  3,12
    db  3,12,  3, 0,  3,20,  3,20,  0, 0,  0, 0, FEND
fos09: ; 5,14,21,20,15,23,CEN
    db  5,14, 21, 0, 20,15,  5, 0, 21,14, 20, 0,  5,23
    db 21, 0, 20, 0,  5, 0, 21,14, 20, 0,  5,15, 21, 0
    db 20,14,  5, 0, 21,23, 20, 0,  5, 0, CEN,0,  0, 0, FEND
fos10: ; 13,8,19,20,8,16,21
    db 13, 8, 13,19, 13,20, 13, 8, 13,19, 13,20, 13,16
    db 13,16, 13, 8, 13,19, 13,20, 13, 8, 13,19, 13,16
    db 13,16,  0, 8,  0,20,  0,21,  0, 0,  0, 0, FEND
fos11: ; 16,26
    db  0,16,  0,16,  0,16,  0,16,  0,16,  0,16,  0,16
    db  0,16, 26,16,  0,16,  0,16, 26,16, 26,16, 26,16
    db  0,16, 26,16,  0,16, 26,16,  0, 0,  0, 0, FEND
fos13: ; 1,16,10,21 木
    db  1, 0,  1, 0,  1, 0,  1, 0,  1, 0,  0,16,  0,16
    db 10, 0,  0, 0, 21, 0, 21, 0, 21, 0, 21,10, 21, 0
    db 21, 0, 21, 0, 21, 0, 21, 0,  0, 0,  0, 0, FEND
fos14: ; 5,14,21,15,20,24,23,CEN
    db  5,14, 21,15, 20,24,  5,15, 21,24, 20,23,  5, 0
    db 21, 0, 20,24,  5,15, 21, 0, 20,24,  5,23, 21,24
    db 20,15,  5,14, 21, 0, 20, 0, CEN,0,  0, 0, FEND
fos15: ; 4,10,30,2
    db  4,10,  4, 0,  4, 0,  4,10,  0,30, 10,30,  4, 0
    db  4, 0,  2, 0,  2, 0,  2,10,  2, 0,  2,10,  4, 0
    db  4, 0,  4,10,  4, 0,  4, 0,  0, 0,  0, 0, FEND
fos16: ; 20,7,31
    db 20, 0, 20, 0, 20, 7, 20, 7, 20, 7, 20, 0, 20, 0
    db 20, 7, 20, 7, 20, 7,  0, 0, 20, 7, 20, 7,  0, 7
    db 20, 7, 20, 7, 20,31, 20,31,  0,31,  0,31, FEND
fos17: ; 5,14,20,7,31,27
    db  5,14,  5, 0,  5, 0,  5, 0,  5, 0,  5,14,  5,20
    db  0,20,  0,14,  5, 0,  7, 0, 31,14, 31, 0, 31, 0
    db 31, 0, 31,20,  0,20, 27,20, 27,20, 27,20,  0, 0, FEND

; --------------------------------------------------------------------------
; todo 名前をつける
; todo 敵スクリプトが動く流れを書く
; **敵出現パターンのデータ転送:**
; *   難易度（`INPUT_MODE_WORK`）やゲームの状態に応じて、`enemy_spawn_pattern_table`（0x9CF0等）からスプライトワークエリア（`ENEMIES`）へ、敵の初期データ（種類、位置、パラメータ等）を `LDIR` 命令でコピーしています。
; **入力バッファの空き確認 (`API1B`):**
; *   スプライトワークエリア（0xCC79〜）をスキャンし、新しい敵を出現させるための空きスロットがあるか確認します。
; **サウンドエフェクトの再生管理 (`API1C`):**
; *   敵が出現する際や特定のタイミングで、サウンド効果音の再生処理（`API1C_handle_ses`）を呼び出しています。
; **ワークポインタの更新:**
; *   `DAMAGE_WORK_0cc40h` というポインタを更新し、次に読み込むべき敵出現データの位置を管理しています。
API1F_ControllGameProgress:
    ; 大体5回に1回動かす
    ld hl,KEY_COUNTER
    dec (hl)
    ret p
    ld (hl),005h ; リセット5回

    ld hl,AI_TIMER_0cc3fh
    dec (hl)
    jp m,api1f_cont1
        ; 4回に3回くらいはこっち
        ld iy,(FIELD_OBJ_SCRIPT_0cc40h)
        jp api1f_cont2
    api1f_cont1:
        ; 4回くらいに1回動かす
        ld (hl),004h
        ; 敵出現スクリプトを動かす
        ; GF24_runEnemySpawnScript
        ;ld a,024h
        ;call CallGF
        call GF24_runEnemySpawnScript
        ; スクリプトを２回進める
        ld hl,(FIELD_OBJ_SCRIPT_0cc40h)
        ld iy,(FIELD_OBJ_SCRIPT_0cc40h) ; 読んでおく
        inc hl
        inc hl
        ld (FIELD_OBJ_SCRIPT_0cc40h),hl
        ld a,(iy+000h)
        cp CEN ; 天井終了チェック
        jp nz,api1f_cont2
            ; 天井状態終了
            ld a,002h
            ld (CEIL_STATE),a
            ret
    api1f_cont2:
    ; 天井の移動がなければ動く
    ; 空スプライトを検索
    call API1B_search_empty_sprite ; 見つからなかったらキャリーフラグが立つ
    ret c ; 見つからなかったら抜ける
    ; 見つかった
    ld a,(iy+000h) ; 敵出現番号
    or a
    jp p,api1f_cont3 ; スクリプト終端ffならボス開始
        ; ボス開始
        ld a,001h
        ld (STAGE_BOSS_START_0ce5bh),a
        ret
    api1f_cont3: ; 通常敵の出現チェック
    dec a
    ret m ; 00なら無効
    cp 020h
    ret nc ; 21h以上は無効
    ; 出現させて
    ld c,001h
    call Api1f_sub1_enemy_spawn_pattern_data
    call API1B_search_empty_sprite
    ret c
    ; スプライトないと戻すとかかな。
    ld a,(iy+001h)
    dec a
    ret m
    cp 020h
    ret nc
; --------------------------------------------------------------------------
; 地上物出現パターン定義（難度別）
; 地上物の出現順序や種類をゲーム難度に応じて制御
; --------------------------------------------------------------------------
; 地上物出現パターンから地上物ワークを初期化
;
; 入力:
;   A = (スクリプト-1) (0～31) スクリプトは1から32
;   C = 出現属性 (0=通常, 非0=特殊)
;   IX = 初期化対象の地上物ワーク
;
; 処理:
;   - 地上物番号を設定
;   - enemy_spawn_pattern_table_1 のテンプレートをコピー
;   - 出現Y座標をテーブルから設定
;   - 難易度を保存
;   - 追加属性を設定
;   - 出現属性に応じた値を(ix+7)へ設定
; --------------------------------------------------------------------------
Api1f_sub1_enemy_spawn_pattern_data:
    ; 出現番号を保存
    ld e,a ; e = (スクリプト-1)
    ; 内部地上物番号へ変換して設定
    add a,017h ; a = (スクリプト-1)+23がタイプ番号になるっぽい
    ld (ix+000h),a
    ld d,0
    ld a,e     ; a = (スクリプト-1)
    add a,a    ; a = (スクリプト-1)*2
    ld e,a     ; e = (スクリプト-1)*2
    ; テンプレートデータへのポインタ取得
    ld hl,enemy_spawn_pattern_table_1 ; hl = enemy_spawn_pattern_table_1
    add hl,de ; hl = enemy_spawn_pattern_table_1+(スクリプト-1)*2
    ld e,(hl) ; de = enemy_spawn_pattern_table_1[(スクリプト-1)]
    inc hl
    ld d,(hl)
    ex de,hl  ; hl = enemy_spawn_pattern_table_1[(スクリプト-1)]
    ; 出現属性に応じて(ix+7)へ設定する値を決定
    ld a,c
    or a
    ld a,0ffh
    jp z,api1f_sub1_cont1
        ld a,004h
    api1f_sub1_cont1:
    ; 自己書き換えで後段の即値を変更
    ld (api1f_sub1_rp1+1),a
    push ix
    pop de
    inc de
    inc de
    inc de
    inc de
    ; enemy_spawn_pattern_table_1[(スクリプト-1)]から9バイトをix[4]以降にコピー
    ; IX+4以降へテンプレート9バイトをコピー
    ld bc,00009h
    ; hl → de に、bc バイト転送
    ldir
    ; --------------------
    ; Z座標を31に設定
    ld (ix+003h),31
    ; --------------------
    ; X座標設定
    ; 出現位置xテーブルのインデックスを8->15->0->15->0->15と循環更新
    api1f_sub1_rp2:
    ld a,8
    inc a
    and 15
    ld (api1f_sub1_rp2+1),a
    ld e,a
    ld d,0
    ; x座標テーブル参照
    ld hl,enemy_spawn_pattern_table_2
    add hl,de
    ld a,(hl)
    ld (ix+005h),a
    ; --------------------
    ; 難易度を保存
    ld a,(INPUT_MODE_WORK)
    ld (ix+00dh),a
    ; --------------------
    ; 種別ごとの追加属性を設定
    ld a,(ix+000h)
    sub 017h
    ld e,a
    ld hl,enemy_spawn_pattern_table_3
    add hl,de
    ld a,(hl)
    ld (ix+00eh),a ; 0か1か30か3っぽい
    ; --------------------
    ; 出現属性値を書き込む(自己書き換え対象)
    api1f_sub1_rp1:
    ld a,0ffh
    ld (ix+007h),a ; 255 か 4
    ; 追加情報の追加
    push iy
    call API1C_handle_ses
    pop iy
    ret
; --------------------------------------------------------------------------
enemy_spawn_pattern_table_3:
    ;  1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    db 0,0,0,0,0,0,0,0,0, 1, 0, 0, 0, 1, 0
    ; 16,17,18,19,20,21,22,23,24,25,26,27,28,29
    db 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0
enemy_spawn_pattern_table_2: ; x座標の出現位置テーブル
    ;   1,2, 3, 4, 5,6, 7, 8, 9,10,11,12,13,14,15,16,; 未使用 17,18
    db 30,3,40,10,20,0,50,24,42,35,15, 1,59,47,19, 0,          0, 0
enemy_spawn_pattern_table_1:
    ;   1 01, 2 02, 3 03, 4 04, 5 05, 6 06, 7 07, 8 08, 9 09,10 0a
    dw esp01,esp01,esp02,esp02,esp02,esp02,esp02,esp02,esp03,esp04
    ;  11 0b,12 0c,13 0d,14 0e,15 0f,16 10,17 11,18 12,19 13,20 14
    dw esp05,esp05,esp05,esp06,esp07,esp05,esp05,esp05,esp02,esp02
    ; ,21 15,22 16,23 17,24 18,25 19,26 1a,27 1b,28 1c,29 1d,30 1e
    dw esp02,esp02,esp07,esp06,esp04,esp02,esp02,esp02,esp05,esp05
    ;  31 1f
    dw esp02

; 敵スプライト初期データテーブル
; (ix+0) 敵タイプ
; (ix+1) zoom_Y
; (ix+2) zoom_X
; (ix+3) Z
; (ix+4) world_y
; (ix+5) world_x
; (ix+6) frame
; (ix+7) 編隊No?
; (ix+8) move_type
; (ix+9) draw_size_flag
; (ix+10) work
; (ix+11) AINOÅ
; (ix+12) work
; +D  difficulty
; +E  enemy_attribute

;         4:Y座標,5:X座標,6:anino,7:編隊No,8:動作No,9:x2,10:work,11:AINO,12:work
esp01: db      11,      0,      0,      -1,       0,   0,      0,     46,        0
esp02: db      11,      0,      0,      -1,       2,   0,      0,     46,        0
esp03: db      15,      0,      0,      -1,       0,   0,      0,     46,        0
esp04: db       7,      0,      0,      -1,       0,   1,      0,     46,        0
esp05: db      21,      0,      0,      -1,       0,   1,      0,     46,        0
esp06: db      11,      0,      0,      -1,       2,   1,      0,     46,        0
esp07: db      21,      0,      0,      -1,       2,   1,      0,     46,        0

; --------------------------------------------------------------------------
; 追加情報の追加
API1C_handle_ses:
    ld (IPL_ROM_WORK_01010h),ix
    ld a,(ix+000h)
    sub 017h
    cp 020h
    ret nc
    add a,a
    ld e,a
    ld d,000h
    ld hl,api1c_se_table
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ex de,hl
    jp (hl)

et1: ; 1,2,3,4,5,6,7,8,9,10,11,12,13,16,17,18,19,20,21,22,25
    ret
api1c_se_table:
     ;   1,  2,  3,  4,  5,  6,  7,  8,  9, 10
    dw et1,et1,et1,et1,et1,et1,et1,et1,et1,et1
     ;  11, 12, 13, 14, 15, 16, 17, 18, 19, 20
    dw et1,et1,et1,et6,et6,et1,et1,et1,et1,et1
     ;  21, 22, 23, 24, 25, 26, 27, 28, 29, 30
    dw et1,et1,et6,et6,et1,et7,et8,et2,et3,et4
     ;  31
    dw et5
et2: ; 28
    ld (ix+000h),032h
    ret
et3: ; 29
    ld (ix+000h),033h
    ret
et4: ; 30
    ld (ix+000h),034h
    ret
et5: ; 31
    ld (ix+000h),035h
    ret
et6: ; 14,15,23,24
    ld b,001h
    ld (ix+007h),0ffh
    et6_loop1:
        push bc
        call API1B_search_empty_sprite
        jp c,et6_cont2
            push ix
            pop de
            ld hl,(IPL_ROM_WORK_01010h)
            ld bc,00018h
            ldir
            ld a,r
            and 00fh
            sub 007h
            add a,(ix+005h)
            ld (ix+005h),a
            ld a,r
            and 00fh
            add a,005h
            ld (ix+007h),a
            pop bc
            djnz et6_loop1
    ret
    et6_cont2:
    pop bc
    ret
et7: ; 26
    ld (ix+000h),01ch
    jp et8_cont1
et8: ; 27
    ld (ix+000h),035h
    et8_cont1:
    ld a,01eh
    ld (KEY_COUNTER),a
    xor a
    ld (AI_TIMER_0cc3fh),a
    ld b,002h
    ld (ix+007h),0ffh
    ld iy,et8_data_start
    et8_loop2:
        push bc
        call API1B_search_empty_sprite
        jp c,et8_cont3
        push ix
        pop de
        ld hl,(IPL_ROM_WORK_01010h)
        ld bc,00018h
        ldir
        ld a,(iy+000h)
        inc iy
        add a,(ix+005h)
        ld (ix+005h),a
        pop bc
        djnz et8_loop2
    ret
    et8_cont3:
    pop bc
    ret
; --------------------------------------------------------------------------
et8_data_start:
    db 00bh,016h,021h,02ch,041h,033h,00dh,020h,04ch,044h,020h,041h,02ch,034h
    db 034h,00dh,020h,04ch,044h,020h,028h,054h,045h,04bh,049h,042h,046h,029h
    db 02ch,041h,00dh,020h,04ch,044h,020h,028h,032h,034h,02ah,034h,02bh,054h
    db 045h,04bh,049h,042h,046h,029h,02ch,041h,00dh,020h,058h,04fh,052h,020h
    db 041h,00dh,020h,04ch,044h,020h,028h,038h,02bh,054h,045h,04bh,049h,042h
    db 046h,029h,02ch,041h,00dh,020h,04ch,044h,020h,028h,032h,034h,02ah,034h
    db 02bh,038h,02bh,054h,045h,04bh,049h,042h,046h,029h,02ch,041h,00dh,020h
    db 052h,045h,054h,00dh,048h,041h,054h,042h,04ch,031h,00dh,020h,044h,042h
    db 020h,034h,035h,03ah,030h,03ah,030h,03ah,032h,035h,03ah,031h,03ah,032h
    db 036h,03ah,030h,03ah,030h,00dh,020h,044h,042h,020h,032h,03ah,031h,03ah
    db 033h,03ah,034h,032h,03ah,037h,03ah,032h,03ah,031h,03ah,030h,00dh

; 空スプライト検索
; 見つかったら ixにアドレスが入り、見つからなかったらキャリーフラグが立つ
; af が破壊 bc deは変わらない
API1B_search_empty_sprite:
    push bc
    push de
        ld ix,ENEMIES
        ld de,00018h
        ld b,010h
        api1b_loop:
            ld a,(ix+000h)
            or a
            jp z,api1b_cont
            add ix,de
            djnz api1b_loop
        scf
        api1b_cont:
    pop de
    pop bc
    ret

    include "script_enemy.asm"