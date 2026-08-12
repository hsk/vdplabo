    org 0100h
; 敵データ 0xcc79 - 0xcdf0
ENEMIES:    equ 0xcc79
; ENEMIES[1]
ENEMIES_1:    equ 0xcc7a
; ENEMIES[4]
ENEMIES_4:    equ 0xcc7d
; ENEMIES[5]
ENEMIES_5:    equ 0xcc7e
; ENEMIES[7]
IX_TYPE:        equ 0
IX_Z:           equ 3
IX_Y:           equ 4
IX_X:           equ 5
IX_ANIM:        equ 6
IX_SPAWN_WAIT:  equ 7  ; 128以上の時ウェイトがかかる
IX_BULLET_TYPE: equ 00ah
IX_AI:          equ 00bh
IX_SPAWN_FRAME: equ 00dh
IX_STATE:       equ 010h

; --------------------------------------------------------------------------
; 8ビット乗算・倍数計算（イテレーティブ）
; hl = h * e * 16
; call for gf5, gf6
; f,b,hl,deを破壊
; a,c,ix,iy,裏bc,裏de,裏hlは変化なし
Gf5_sub1_multiply_8bit_iterative:
    ld d,000h
    ld l,d
    ld b,008h
    ; 乗算ループ
    multiply_loop:
        add hl,hl
        jp nc,next_multiply_step
            add hl,de
        ; 次の乗算ステップ
        next_multiply_step:
            djnz multiply_loop
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ret
; --------------------------------------------------------------------------
; 敵全体をズーム
; iy,ix,b,de,裏b,裏de,裏hl を破壊
; cと裏cは変化しない
; 自己書き換え２箇所
; 以下の計算を表示されている敵全体について計算します
; enemy.zoomx = (enemy.x-32) * (sprite_zoom_parameters[enemy.z] + 3) / 16+32
GF05_enemies_zoom:
    ld iy,sprite_zoom_parameters
    ld ix,ENEMIES
    ld b,010h    ; 敵は全部で16体
    ld de,00018h ; 敵一体のサイズ
    ; ----------
    ; ループ1
    gf5_loop1:
        ; BC DE HL 裏レジスタと交換 VVVVVVVVVVV
        exx            ;b0db    d9        .
        ; 可視チェック
        ld a,(ix+IX_TYPE) ; enemy.visible
        or a
        jp z,gf5_cont1 ; 0なら飛ぶ
            ; -------------------------
            ; e = zoom係数 + 3
            ld a,(ix+IX_Z) ; a = enemy.z
            ld (gf5_rp1+2),a
            ; ズームテーブルから倍率パラメータ取得
            gf5_rp1:
            ld a,(iy+01dh) ; a = sprite_zoom_parameters[enemy.z]
            add a,003h     ; a = sprite_zoom_parameters[enemy.z] + 3
            ld e,a         ; e = sprite_zoom_parameters[enemy.z] + 3
            ; -------------------------
            ld a,(ix+IX_X) ; a = enemy.x
            sub 020h       ; a = enemy.x-32
            ld h,a         ; h = enemy.x-32
            ; -------------------------
            ; a = h * e / 16 (hは符号付き)の計算
            ld a,000h ; a = 0
            jp nc,gf5_cont2
                ; hがマイナス
                ld a,h ; a = h
                neg    ; a = -h
                ld h,a        ; h = -h
                ld a,044h     ; a = 44h (NEG)
            ; 可視パラメータ格納
            gf5_cont2:
            ld (gf5_rp2+1),a ; 自己書き換え
            call Gf5_sub1_multiply_8bit_iterative ; hl = h * e * 16 (符号なし)
            ld a,h ; a = h * e / 16 (符号なし)
            gf5_rp2:
            neg            ; ed 44: neg     ed 00: 未定義NOP
            ; -------------------------
            ; 画面中央(32)を基準にオフセットを加算してX座標化
            add a,020h; a = h * e / 16+32
            ld (ix+002h),a ; enemy.zoomx = (enemy.x-32) * (sprite_zoom_parameters[enemy.z] + 3) / 16+32
        gf5_cont1:
        ; 次の敵
        ; BC DE HL 裏レジスタと交換 AAAAAAAAAAA
        exx
        add ix,de
        djnz gf5_loop1
        ; ループ1
        ; ----------
    ret

; --------------------------------------------------------------------------
; 敵キャラのY座標調整
; vy = 27 - VIEW_SCROLLY[0]
; enemy.zoomy = (vy - enemy.y) * sprite_zoom_parameters[enemy.z] / 16 + vy
; enemy.zoom_shadow = (30-vy)*sprite_zoom_parameters[enemy.z]/16 + vy
VIEW_SCROLLY:    equ 0xcc66
GF06_enemy_scrolly:
    ld a,(VIEW_SCROLLY)             ; a = VIEW_SCROLLY[0]
    ld c,a                          ; c = VIEW_SCROLLY[0]
    ld a,01bh                       ; a = 27
    sub c                           ; a = 27 - VIEW_SCROLLY[0] = vy
    ; rp に vy を反映
    ld (gf6_rp0+1),a
    ld (gf6_rp2+1),a
    ld (gf6_rp3+1),a
    ld (gf6_rp4+1),a
    ;
    ld iy,sprite_zoom_parameters    ; iy = sprite_zoom_parameters
    ld ix,ENEMIES                   ; ix = ENEMIES
    ld b,010h                       ; b = 16
    ld de,00018h                    ; de = 0x0018 スプライトサイズ
    gf6_loop1:
        exx ; BC DE HL 裏レジスタと交換 VVVVVVVVVVV
        ld a,(ix+IX_TYPE)
        or a
        jp z,gf6_cont1 ; スプライトタイプが0ならスキップ
            ld a,(ix+IX_Y) ; a = ix[IX_Y]
            gf6_rp0:
            sub 015h       ; a = ix[IX_Y] - vy
            ld h,a         ; h = ix[IX_Y] - vy
            ld a,000h      ; a = 0 (nop)
            jp nc,gf6_cont2
                ld a,h           ; a = ix[IX_Y] - vy
                neg              ; a = vy - ix[IX_Y]
                ld h,a           ; h = vy - ix[IX_Y]
                ld a,044h        ; a = 0x44 (neg)
            gf6_cont2:
            ld (gf6_rp5+1),a ; 符号反転コードの自己書き換え nop or neg
            ld a,(ix+IX_Z)
            ld (gf6_rp6+2),a ; ix[IX_Z] で自己書き換え
            gf6_rp6:
            ld e,(iy+01dh)   ; e = iy[ix[IX_Z]]
            ld a,e           ; a = iy[ix[IX_Z]]
            ld (gf6_rp7+1),a ; iy[ix[IX_Z]] で自己書き換え
            call Gf5_sub1_multiply_8bit_iterative
            ld a,h              ; a = abs(vy - ix[IX_Y]) * iy[ix[IX_Z]] / 16 (符号なし)
            gf6_rp5: neg        ; a = (vy - ix[IX_Y]) * iy[ix[IX_Z]] / 16; 符号あり
            gf6_rp2: add a,015h ; a = (vy - ix[IX_Y]) * iy[ix[IX_Z]] / 16 + vy
            ld (ix+001h),a      ; enemy.zoomy = ix[1] = (vy - ix[IX_Y]) * iy[ix[IX_Z]] / 16 + vy
            ld a,01eh           ; a = 30
            gf6_rp4:
            sub 015h            ; a = 30 - vy
            ld h,a              ; h = 30 - vy
            gf6_rp7:
            ld e,001h           ; e = iy[ix[IX_Z]]
            call Gf5_sub1_multiply_8bit_iterative ; hl = (30-vy)*iy[ix[IX_Z]]*16
            ld a,h              ; a = (30-vy)*iy[ix[IX_Z]]/16
            gf6_rp3:
            add a,015h          ; a = (30-vy)*iy[ix[IX_Z]]/16 + vy
            ld (ix+00fh),a      ; enemy.zoom_shadow = ix[15] = (30-vy)*iy[ix[IX_Z]]/16 + vy
        gf6_cont1:
        exx ; BC DE HL 裏レジスタと交換 AAAAAAAAAAA
        add ix,de        ; 次の敵
        djnz gf6_loop1
    ret

; --------------------------------------------------------------------------
; スプライト描画用のズーミングパラメータテーブル
; ref gf05 gf2b gf06
sprite_zoom_parameters:
    db 16,16,14,14, 13,13,11,11,  9, 9, 8, 8,  6, 6, 6, 6
    db  5, 5, 5, 5,  3, 3, 3, 3,  2, 2, 2, 2,  1, 1, 1, 1
    db  1, 1, 1, 1,  1, 1, 1, 1

PLAYER_POS_X: equ 0xcc5d

; プレイヤー位置により敵横移動
GF18_enemy_sprite_scrollx:
    ld a,(PLAYER_POS_X)     ; a = player.x
    sub 00ch                ; a = player.x - 12
    sra a                   ; a = (player.x - 12)/2
    sra a                   ; a = (player.x - 12)/4
    ld e,a                  ; e = (player.x - 12)/4
    ld d,000h               ; de = (player.x - 12)/4
    ld hl,gf18_scrollx_tbl  ; hl = gf18_enemy_spawn_tbl
    add hl,de               ; hl = gf18_enemy_spawn_tbl + (player.x - 12)/4
    ld c,(hl)               ; c = gf18_enemy_spawn_tbl[(player.x - 12)/4]
    ld ix,ENEMIES           ; ix = ENEMIES
    ld b,010h               ; b = 16
    ld de,00018h            ; de = 24; d = 0; e = 24
    ld hl,ENEMIES_5         ; hl = ENEMIES_5
    gf18_loop1:
        ; スプライトチェック
        ld a,(ix+IX_TYPE)
        cp 017h
        jp c,gf18_cont1 ; タイプ < 17 ならジャンプ
            ; 17 <= タイプ の時はcを加える
            ld a,(hl)
            add a,c
            ld (hl),a
            jp p,gf18_cont1      ; 加えた結果がプラスならジャンプ
                ld (hl),d        ; 加えた結果マイナスなら 0 にする
        gf18_cont1: ; 次の敵パターン更新2
        add hl,de
        add ix,de
        djnz gf18_loop1
    ret
; --------------------------------------------------------------------------
; ref gf18 gf2a
gf18_scrollx_tbl:
    db 2,1,1,0,0,0,0,-1,-1,-2

; --------------------------------------------------------------------------
; 敵スプライト描画
; 敵スプライトワークをループして座標変換し描画を行う
EF07_draw_enemies_sprite:
    ; Zでループ
    ld a,01fh
    ; 自己書き換えでループ内で1f (31)を設定するように修正
    ld (ef7_rp_z+1),a
    ; ------------
    ; ループ1 Zループ
    ef7_loop1:
        ; スプライトスキャンループ
        ld ix,ENEMIES
        ld b,010h
        ; ------------
        ; ループ2
        ef7_loop2:
            ; スプライトアクティブチェック
            push bc
            ef7_rp_z:
            ld a,014h
            cp (ix+IX_Z); スプライトのz座標と比較
            jp nz,ef7_cont2
            bit 7,(ix+007h); フラグチェック
            jp z,ef7_cont2
            ld a,(ix+IX_TYPE); 生きてるスプライトチェック
            dec a
            jp m,ef7_cont2
                ; 発見 hl = ix[IX_TYPE] * 8
                ld l,a
                ld h,000h
                add hl,hl
                add hl,hl
                add hl,hl
                ; de = (ix[IX_ANIM]&3)*2
                ld a,(ix+IX_ANIM)
                and 003h
                add a,a
                ld e,a
                ld d,000h
                ; hl = ix[IX_TYPE] * 8 + (ix[IX_ANIM]&3)*2
                add hl,de
                ; de = ef7_sp00_start
                ld de,ef7_sp00_start
                ; hl = ef7_sp00_start + ix[IX_TYPE] * 8 + (ix[IX_ANIM]&3)*2
                add hl,de
                ; de = ef7_sp00_start[ix[IX_TYPE] * 4 + (ix[IX_ANIM]&3)]
                ld e,(hl)
                inc hl
                ld d,(hl)
                ; l = x ; h = y
                ld l,(ix+001h)
                ld h,(ix+002h)
                ; スプライトパターンパラメータを取得
                call EFSub3_get_sprite_pattern_parameters
                ld bc,00b14h
                ld a,(ix+009h)
                or a
                jp z,ef7_cont1
                    ld c,00ah
                cont1:
                ; 仮装画面描画
                ; l = x (0-31), h = y (0-52), b = 幅 c = 高さ, de = 転送元アドレス
                call EFSub1_draw_vvram
                cont2:
            ; 次のスプライトスキャン
            ld de,00018h
            add ix,de
            pop bc
            djnz ef7_loop2; b を1引いて0ならジャンプしない ; ループ2
        ; 設定値を１つ減らす
        ld a,(ef7_rp_z+1)
        dec a
        ld (ef7_rp_z+1),a
        jp nz,ef7_loop1 ; ループ1
    ret

; --------------------------------------------------------------------------
; スプライトパターンテーブルから描画パラメータを取得
; 敵タイプ（IX+03h）からパターン情報を取得し、0cc5a,0cc58に設定
; スクリーン座標変換用のパラメータを準備
; gef0a gef7 から呼ばれる
EFSub3_get_sprite_pattern_parameters:
	push de			
	push hl			
	ld a,(ix+003h)		
	sra a			
	add a,a			
	ld e,a			
	ld d,000h		
	ld hl,sprite_ptn_param_tbl	
	add hl,de		
	ld a,(hl)		
	ld (DAMAGE_WORK_0cc5ah),a	
	ld (ef_sub2_rp2+1),a	
	inc hl			
	ld a,(hl)		
	ld (DAMAGE_WORK_0cc58h),a	
	ld (ef_sub2_rp1+1),a	
	pop hl			
	pop de			
	ret			
; --------------------------------------------------------------------------
sprite_ptn_param_tbl:
    ;   1, 2, 3, 4, 5, 6, 7, 8, 9,10
	db  1, 1, 2, 3, 3, 5, 4, 7, 5, 9
    db  6,11, 7,13, 7,14, 8,15, 8,16
    db  9,17, 9,18,10,19,10,19,11,20
    db 11,20,11,20,11,20


end:
    ; ROMサイズを16KB（最小サイズ）に合わせるためのパディング
    ds 08000h - $, 0
