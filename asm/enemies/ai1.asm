FRAME_CNT_0cc68h:           equ 0cc68h
GAME_STAGE:                 equ 0xcc62
ENEMIES:                    equ 0xcc79
PLAYER_POS_Y:               equ 0xcc5c
PLAYER_POS_X:               equ 0xcc5d
IX_TYPE:        equ 0
IX_ZOOMY:       equ 1
IX_ZOOMX:       equ 2
IX_Z:           equ 3
IX_Y:           equ 4
IX_X:           equ 5
IX_ANIM:        equ 6
IX_SPAWN_WAIT:  equ 7  ; 128以上の時ウェイトがかかる
IX_NO_COL_SHOT: equ 008h ; ショットと当たらない 敵弾や爆発など
IX_MINI:        equ 009h ; 1で通常 0で倍サイズ
IX_BULLET_TYPE: equ 00ah
IX_AI:          equ 00bh
IX_NOSOUND:     equ 00ch ; ショットとぶつかるけど音がならずやられない todo
IX_SPAWN_FRAME: equ 00dh
IX_SHADOW:      equ 00eh
IX_ZOOM_SHADOW: equ 00fh
IX_STATE:       equ 010h
IX_ABS_DX:      equ 010h ; abs(dx)
IX_ABS_DY:      equ 011h ; abs(dy)
IX_LIFE:        equ 012h ; 寿命
IX_SIGNX:       equ 013h ; x方向符号(-1/0/+1)
IX_SIGNY:       equ 014h ; y方向符号(-1/0/+1)
IX_BRE:         equ 015h ; Bresenham誤差項
IX_BRE_WORK:    equ 016h ; Bresenham作業値
IX_MAJOR_AXIS:  equ 017h ; max(|dx|,|dy|)

    org 100h
CallGF: ret
; --------------------------------------------------------------------------
; アクティブスプライト検索
; スプライト領域で次の空いているスロットを探す
; ref gf1b gf19
EFSub5_find_empty_enemy_slot:
    ld iy,ENEMIES
    ld b,010h
    ld de,00018h
ef_sub5_loop:
    ld a,(iy+IX_TYPE)
    or a
    ret z
    add iy,de
    djnz ef_sub5_loop
    scf
    ret

; 敵弾発射処理
CallGF1B:
GF1B:
    ; ----------------------------------------------------------------------
    ; 敵弾スロット確保
    ; ----------------------------------------------------------------------
    call EFSub5_find_empty_enemy_slot
    ret c
    ; ----------------------------------------------------------------------
    ; 敵弾基本情報初期化
    ; 発射元の座標・種類・AI番号を設定
    ; ----------------------------------------------------------------------
    ld a,(ix+IX_BULLET_TYPE)
    ld (iy+IX_TYPE),a       ; iy[IX_TYPE] = ix[IX_BULLET_TYPE]
    ld l,(ix+IX_Y)
    ld h,(ix+IX_X)
    ld (iy+IX_Y),l          ; iy[IX_Y] = ix[IX_Y]
    ld (iy+IX_X),h          ; iy[IX_X] = ix[IX_X]
    ld a,(ix+IX_Z)
    ld (iy+IX_Z),a          ; iy[IX_Z] = ix[IX_Z]
    ld (iy+IX_ANIM),000h    ; iy[IX_ANIM]=0x00
    ld (iy+IX_SPAWN_WAIT),0 ; iy[IX_SPAWN_WAIT]=0x00
    ld (iy+IX_NO_COL_SHOT),1; iy[IX_NO_COL_SHOT]=0x01
    ld (iy+IX_MINI),001h    ; iy[IX_MINI]=0x01
    ld (iy+IX_AI),030h      ; iy[IX_AI]=0x30 ; 敵弾処理
    ld (iy+IX_SHADOW),001h  ; iy[IX_SHADOW]=0x01
    ; ----------------------------------------------------------------------
    ; 出現パターン設定
    ; 敵弾タイプからスポーンフレームを決定
    ; ----------------------------------------------------------------------
    ld a,(ix+IX_BULLET_TYPE)
    ld e,a
    ld d,000h
    ld hl,gf1b_enemy_spawn_type_tbl
    add hl,de
    ld a,(hl)
    ld (iy+IX_SPAWN_FRAME),a; iy[IX_SPAWN_FRAME] = gf1b_enemy_spawn_type_tbl[ix[IX_BULLET_TYPE]]
    ; ----------------------------------------------------------------------
    ; プレイヤー照準位置取得
    ; target = (PLAYER_POSY-1, PLAYER_POSX-3)
    ; ----------------------------------------------------------------------
    ld hl,(PLAYER_POS_Y) ; h = PLAYER_POSX; l = PLAYER_POSY
    dec l                ; l = PLAYER_POSY - 1
    dec h                ; h = PLAYER_POSX - 1
    dec h                ; h = PLAYER_POSX - 2
    dec h                ; h = PLAYER_POSX - 3
    ; ----------------------------------------------------------------------
    ; X方向距離と移動符号計算
    ; dx = target_x - enemy_x
    ; ----------------------------------------------------------------------
    ld a,h                  ; a = PLAYER_POSX - 3
    sub (ix+IX_X)           ; a = PLAYER_POSX - 3 - ix[IX_X]
    ld c,000h               ; c = 0
    jp z,gf1b_cont1         ; a==0ならそのまま
        ld c,001h               ; c = 1
        jp nc,gf1b_cont1        ; a>=0なら絶対値計算不要
            ld a,(ix+IX_X)          ; a = ix[IX_X]
            sub h                   ; a = ix[IX_X] - (PLAYER_POSX - 3)
            ld c,0ffh               ; c = -1
    gf1b_cont1:             ; a = abs(PLAYER_POSX - 3 - ix[IX_X]); c = Y方向符号(-1/0/+1)
    ld (iy+IX_ABS_DX),a     ; iy[IX_ABS_DX] = abs(PLAYER_POSX - 3 - ix[IX_X])
    ld (iy+IX_SIGNX),c      ; iy[IX_SIGNX] = X方向符号(-1/0/+1)
    ; ----------------------------------------------------------------------
    ; Y方向距離と移動符号計算
    ; dy = target_y - enemy_y
    ; ----------------------------------------------------------------------
    ld a,l                  ; a = PLAYER_POSY - 1
    sub (ix+IX_Y)           ; a = PLAYER_POSY - 1 - ix[IX_Y]
    ld c,000h               ; c = 0
    jp z,gf1b_cont2         ; a==0ならそのまま
        ld c,001h               ; c = 1
        jp nc,gf1b_cont2        ; a>=0なら絶対値計算不要
            ld a,(ix+IX_Y)          ; a = ix[IX_Y]
            sub l                   ; a = ix[IX_Y] - (PLAYER_POSY - 1)
            ld c,0ffh               ; c = -1
    gf1b_cont2:             ; a = abs(PLAYER_POSY - 1 - ix[IX_Y])
    ld (iy+IX_ABS_DY),a     ; iy[IX_ABS_DY] = abs(PLAYER_POSY - 1 - ix[IX_Y])
    ld (iy+IX_SIGNY),c      ; iy[IX_SIGNY] = Y方向符号(-1/0/+1)
    ; ----------------------------------------------------------------------
    ; 寿命・距離パラメータ設定
    ; ----------------------------------------------------------------------
    ld a,(ix+IX_Z)          ; a = ix[IX_Z] ; 寿命/距離パラメータ?
    ld (iy+IX_LIFE),a       ; iy[IX_LIFE] = ix[IX_Z]
    ; ----------------------------------------------------------------------
    ; Bresenham移動パラメータ生成
    ; IX_MAJOR_AXIS = max(dx,dy)
    ; IX_BRE = 誤差項初期値(max(dx,dy)/2)
    ; ----------------------------------------------------------------------
    ld c,(iy+IX_ABS_DX)     ; c = iy[IX_ABS_DY]
    ld a,c                  ; a = iy[IX_ABS_DY]
    sub (iy+IX_ABS_DY)      ; a = iy[IX_ABS_DY] - iy[IX_ABS_DY]
    jp nc,gf1b_cont3        ; iy[IX_ABS_DY]>=iy[IX_ABS_DY]
        ld c,(iy+IX_ABS_DY)     ; c = iy[IX_ABS_DY]
    gf1b_cont3:             ; c = max(iy[IX_ABS_DY],iy[IX_ABS_DY])
    ld (iy+IX_MAJOR_AXIS),c ; iy[IX_MAJOR_AXIS] = max(iy[IX_ABS_DY],iy[IX_ABS_DY])
    sra c                   ; c = iy[IX_MAJOR_AXIS]/2
    ld (iy+IX_BRE),c        ; iy[IX_BRE] = iy[IX_MAJOR_AXIS]/2
    ; ----------------------------------------------------------------------
    ; スポーンフレーム補正
    ; 距離と寿命から出現タイミングを調整
    ; ----------------------------------------------------------------------
    ld c,(iy+IX_MAJOR_AXIS) ; c = iy[IX_MAJOR_AXIS]
    ld a,(iy+IX_LIFE)       ; a = ix[IX_Z]
    cp c                    ; ix[IX_Z] と iy[IX_MAJOR_AXIS] を比較
    jp nc,gf1b_cont5        ; ix[IX_Z] >= iy[IX_MAJOR_AXIS]
        ld c,(iy+IX_LIFE)       ; c = ix[IX_Z]
        dec (iy+IX_SPAWN_FRAME) ; iy[IX_SPAWN_FRAME]=iy[IX_SPAWN_FRAME]-1 ; スポーンタイプ減少
        jp p,gf1b_cont4         ; 0以上なら維持
            ld (iy+IX_SPAWN_FRAME),0; 下限0
        gf1b_cont4:             ; iy[IX_SPAWN_FRAME]=max(0,iy[IX_SPAWN_FRAME]-1)
        sra c                   ; c = ix[IX_Z]/2
        ld (iy+IX_BRE_WORK),c   ; iy[IX_BRE_WORK] = ix[IX_Z]/2
        ld a,(ix+IX_MAJOR_AXIS) ; a = ix[IX_MAJOR_AXIS]
        cp 014h                 ; 20と比較
        ret c                   ; if (ix[IX_MAJOR_AXIS] < 20) return
        ; iy[IX_SPAWN_FRAME]=max(0,iy[IX_SPAWN_FRAME]-1)
        dec (iy+IX_SPAWN_FRAME)
        ret p
        ld (iy+IX_SPAWN_FRAME),000h
        ret
    ; ----------------------------------------------------------------------
    ; 長距離弾補正
    ; スポーンフレームを最大5まで増加
    ; ----------------------------------------------------------------------
    gf1b_cont5:
    sra c                       ; c = max(abs(PLAYER_POS_Y - 3 - ix[IX_X]),abs(PLAYER_POS_X - 1 - ix[IX_Y]))/2
    ld (iy+IX_BRE_WORK),c       ; iy[IX_BRE_WORK] = max(abs(PLAYER_POS_Y - 3 - ix[IX_X]),abs(PLAYER_POS_X - 1 - ix[IX_Y]))/2
    ; iy[IX_SPAWN_FRAME] = min(iy[IX_SPAWN_FRAME]+1,5)
    inc (iy+IX_SPAWN_FRAME)
    ld a,(iy+IX_SPAWN_FRAME)
    cp 006h
    ret c
    ld (iy+IX_SPAWN_FRAME),005h
    ret
    ; --------------------------------------------------------------------------
    ; ix[IX_BULLET_TYPE]から出現敵タイプを求める
    gf1b_enemy_spawn_type_tbl: db 0,0,0,4,4,2,4,4,3,5

enemy_ai_flag: db 0aah
; --------------------------------------------------------------------------
; 敵アップデート
; 1. 指定フレームに達している
; 2. 敵が有効
; 3. ウェイトタイマー完了（bit7=1）
; 4. AI状態番号が 0x31 未満
; の条件を満たす敵スプライトを見つけて、(ix+IX_AI)によってジャンプして処理する
AI1_update_enemies:
    ld hl,enemy_ai_flag
    rlc (hl)
    ret c
    ld ix,ENEMIES
    ld b,010h
    ld de,00018h
    ai1_loop1:
        exx ; BC DE HL 裏レジスタと交換 VVVVVVVVVVV
            ld a,(FRAME_CNT_0cc68h)
            cp (ix+IX_SPAWN_FRAME)
            jp c,ai1_next   ; if (FRAME_CNT_0cc68h < ix[IX_SPAWN_FRAME]) ならとばす
                ld a,(ix+IX_TYPE)
                or a
                jp z,ai1_next ; ix[IX_TYPE] がゼロならとばす
                    bit 7,(ix+IX_SPAWN_WAIT)
                    jp nz,ai1_cont1 ; マイナスならとぶ
                        ; プラスなら出現待ちウェイト
                        dec (ix+IX_SPAWN_WAIT)
                        jp ai1_next
                    ai1_cont1:
                    ; 敵AI状態チェック (ix+IX_AI)が31未満
                    ld a,(ix+IX_AI)
                    cp 031h
                    jp nc,ai1_next
                        ; AIジャンプ要件を満たした
                        dec a
                        add a,a
                        ld e,a
                        ; AIジャンプ準備
                        ld d,000h
                        ; AIジャンプ実行
                        ld hl,ai1_a1_sub_tbl
                        add hl,de
                        ld e,(hl)
                        inc hl
                        ld d,(hl)
                        ex de,hl
                        ld de,ai1_next
                        push de
                        jp (hl)     ; call ai1_a1_sub_tbl[ix[IX_AI-1]]()
        ai1_next:; 敵AIループ継続点
        exx ; BC DE HL 裏レジスタと交換 AAAAAAAAAAA
        add ix,de
        djnz ai1_loop1
    ret
    ai1_a1_sub_tbl:
        ;     01    02    03    04    05    06    07    08    09    0a    0b    0c    0d    0e    0f    10
        dw A1S01,A1S02,A1S03,A1S04,A1S05,A1S06,A1S07,A1S08,A1S08,A1S0A,A1S0B,A1S0C,A1S0D,A1S0E,A1S0F,A1S10
        ;     11    12    13    14    15    16    17    18    19    1a    1b    1c    1d    1e    1f    20
        dw A1S11,A1S12,A1S13,A1S14,A1S14,A1S16,A1S16,A1S18,A1S18,A1S1A,A1S1B,A1S1C,A1S1D,A1S1E,A1S1F,A1S20
        ;     21    22    23    24    25    26    27    28    29    2a    2b    2c    2d    2e    2f    30
        dw A1S21,A1S22,A1S23,A1S24,A1S25,A1S25,A1S27,A1S28,A1S29,A1S2A,A1S2B,A1S2A,A1S2A,A1S2E,A1S2F,A1S30
        ;     31    32    33    34    35    36
        dw A1S2F,A1S2F,A1S2F,A1S2F,A1S2F,A1S2F

    include "ai1_00.asm"
    include "ai1_10.asm"
    include "ai1_20.asm"
    include "ai1_30.asm"
    include "ai1_40.asm"
