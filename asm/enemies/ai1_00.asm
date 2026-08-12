; ------------------------------------------------------
; 敵AI処理1 01 進んできて、上に上昇して0になったら消える。多分ムカデンス
A1S01:
AS19: ; アイダ1
AS53: ; アイダ8
    ld a,(ix+IX_STATE)
    or a
    jp z,a1s01_cont1
                            ; if (a != 0) {
        dec (ix+IX_Y)           ; ix[IX_Y] = dec(ix[IX_Y])
        ret p                   ; if (!is_minus(ix[IX_Y])) return
        ld (ix+IX_TYPE),000h    ; return delete_enemy()
        ret
    a1s01_cont1:            ; }
    dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
    ld a,(ix+IX_Z)
    cp 004h
    ret nc                  ; if (ix[IX_Z] >= 4) return
    inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
    ret
; ------------------------------------------------------
; 敵AI処理2 02
A1S02:
AS18: ; カナリー1
AS24: ; ジェット11
    ld a,(ix+IX_STATE)
    or a
    jp z,a1s02_cont1
                            ; if (ix[IX_STATE]!=0) {
        dec (ix+IX_Y)           ; ix[IX_Y] = dec(ix[IX_Y])
        ret p                   ; if (!is_minus(ix[IX_Y])) return
        ld (ix+IX_TYPE),000h    ;  return delete_enemy()
        ret
    a1s02_cont1:            ; }
    dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
    ld a,(ix+IX_Z)
    cp 008h
    ret nc                  ; if (ix[IX_Z]>=8) return
    inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
    jp CallGF1B             ; return CallGF1B()
; ------------------------------------------------------
; 敵AI処理3 03
A1S03:
AS22: ; パーコメン1
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s03_cont2
    jp z,a1s03_cont1
                            ; if (ix[IX_STATE] > 1) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        jp m,a1s0f_ret          ; if (ix[IX_Z] < 0) return delete_enemy()
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X],2)
        inc (ix+IX_X)
        ld a,(ix+IX_X)
        cp 03ch
        ret c                   ; if (ix[IX_X] < 0x3c) return
        ld (ix+IX_TYPE),000h    ; return delete_enemy()
        ret
    a1s03_cont1:            ; } else if (ix[IX_STATE] == 1) {
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X],2)
        dec (ix+IX_X)
        ld a,(ix+IX_X)
        cp 005h
        ret nc                  ; if (ix[IX_X] >= 5) return
        ld (ix+IX_STATE),002h   ; ix[IX_STATE] = 2
        jp CallGF1B             ; return CallGF1B()
    a1s03_cont2:            ; } // ix[IX_STATE] == 0
    inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
    dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
    ld a,(ix+IX_Z)
    cp 00ah
    ret nc                  ; if (ix[IX_Z] >= 10) return
    ld (ix+IX_STATE),001h   ; ix[IX_STATE] = 1
    jp CallGF1B             ; return CallGF1B()
; ------------------------------------------------------
; 敵AI処理4 04
A1S04:
AS23: ; パーコメン2
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s04_cont1
    jp z,a1s04_cont2
                            ; if (ix[IX_STATE] > 1) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X],2)
        inc (ix+IX_X)
        ld a,(ix+IX_X)
        cp 03ch
        ret c                   ; if (ix[IX_X] < 60) return
        jp a1s0f_ret            ; return delete_enemy()
    a1s04_cont1:            ; } else if (ix[IX_STATE] < 1) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X],2)
        inc (ix+IX_X)
        ld a,(ix+IX_X)
        cp 028h
        ret c                   ; if (ix[IX_X] < 40) return
        ld (ix+IX_STATE),001h   ; ix[IX_STATE] = 1
        ret                     ; return
    a1s04_cont2:            ; } else if (ix[IX_STATE] == 1) {
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X])
        jp m,a1s04_cont3
                                ; if (!is_minus(ix[IX_X])) {
            dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
            ld a,(ix+IX_Z)
            cp 003h
            ret nc                  ; if (ix[IX_Z] >= 3) return
        a1s04_cont3:            ; }
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
        ld (ix+IX_STATE),002h   ; ix[IX_STATE] = 2
        ret
                            ; }
; ------------------------------------------------------
; 敵AI処理5 05
A1S05:
AS35: ; トモス1
    ld (ix+00ch),000h  ; ix[0x0c]=0;
    ld a,(ix+IX_STATE) ; 状態番号
    add a,a            ; ×2 (dwテーブルなので2バイト単位)
    ld e,a
    ld d,000h
    ld hl,a1s05_tbl
    add hl,de          ; HL = &a1s05_tbl[ix[IX_STATE]]
    ld e,(hl)          ; ジャンプ先アドレス取得
    inc hl
    ld d,(hl)
    ex de,hl
    jp (hl)            ; a1s05_tbl[ix[IX_STATE]]() 間接ジャンプ
    ; --------------------------------------------------------------------------
    a1s05_tbl:
        ;         0        1        2        3        4        5        6        7
        dw A1S05F00,A1S05F01,A1S05F02,A1S05F03,A1S05F04,A1S05F03,A1S05F01,A1S05F02
        ;         8        9       10       11       12       13       14       15
        dw A1S05F03,A1S05F04,A1S05F03,A1S05F01,A1S05F02,A1S05F03,A1S05F04,A1S05F15
    ; --------------------------------------------------------------------------
    A1S05F01:
        rlc (ix+012h)          ; carry,ix[0x12] = rol(ix[0x12],1)
        ret c                  ; if (carry) return
        dec (ix+IX_ANIM)       ; ix[IX_ANIM] = dec(ix[IX_ANIM])
        ret nz                 ; if (ix[IX_ANIM] != 0) return
        inc (ix+IX_STATE)      ; ix[IX_STATE] = inc(ix[IX_STATE])
        ld (ix+011h),004h      ; ix[0x11] = 4
        ret                    ; return
    ; --------------------------------------------------------------------------
    A1S05F02:
        ld (ix+008h),000h      ; ix[0x08] = 0
        dec (ix+011h)          ; ix[0x11] = dec(ix[0x11])
        ret p                  ; if (ix[0x11] >= 0) return
        inc (ix+IX_STATE)      ; ix[IX_STATE] = inc(ix[IX_STATE])
        ld (ix+011h),00bh      ; ix[0x11] = 11
        jp CallGF1B            ; GF1B(); return
    ; --------------------------------------------------------------------------
    A1S05F04:
        ld (ix+008h),002h      ; ix[0x08] = 2
        rlc (ix+012h)          ; carry,ix[0x12] = rol(ix[0x12],1)
        ret c                  ; if (carry) return
        inc (ix+IX_ANIM)       ; ix[IX_ANIM] = inc(ix[IX_ANIM])
        ld a,(ix+IX_ANIM)
        cp 003h
        ret c                  ; if (ix[IX_ANIM] < 3) return
        inc (ix+IX_STATE)      ; ix[IX_STATE] = inc(ix[IX_STATE])
        ld (ix+011h),010h      ; ix[0x11] = 16
        ret                    ; return
    ; --------------------------------------------------------------------------
    ; 状態4,6,9,b,e 共通
    A1S05F03:
        dec (ix+011h)          ; ix[0x11] = dec(ix[0x11])
        ret p                  ; if (!is_minus(ix[0x11])) return
        inc (ix+IX_STATE)      ; ix[IX_STATE] = inc(ix[IX_STATE])
        ret                    ; return
    ; --------------------------------------------------------------------------
    ; 状態1 初期待機
    A1S05F00:
        ld (ix+008h),002h       ; ix[0x08] = 2
        ld c,008h
        ld a,(GAME_STAGE)
        cp 007h
        jp c,a1s05f01_cont1
            ld c,006h
        a1s05f01_cont1:         ; if (GAME_STAGE >= 7) c = 6 else c = 8
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp c
        ret nc                  ; if (ix[IX_Z] >= c) return
        ld (ix+012h),0eeh       ; ix[0x12] = 0xEE
        ld (ix+IX_STATE),001h   ; ix[IX_STATE] = 1
        ret                     ; return
    ; --------------------------------------------------------------------------
    ; 状態15 終了フェーズ
    A1S05F15:
        inc (ix+IX_Z)          ; ix[IX_Z] = inc(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 01fh
        ret c                  ; if (ix[IX_Z] < 31) return
        ld (ix+IX_TYPE),000h   ; return delete_enemy()
        ret

; ------------------------------------------------------
; 敵AI処理6 06
; 「上下にフラフラしながら最後は上へ抜けていく敵」
A1S06:
AS20: ; ルーパー1
; ix[IX_Z] = dec(ix[IX_Z])
; if (ix[IX_Z] < 0) return delete_enemy()
; if (ix[IX_Z] < 6) {
;     ix[IX_Y] = dec(ix[IX_Y],2)
;     if (ix[IX_Y] < 0) ix[IX_Y] = inc(ix[IX_Y])
; }
; else {
;     ix[IX_STATE] = dec(ix[IX_STATE]);
; 
;     if ((ix[IX_STATE] & 0x0f) >= 8) {
;         ix[IX_Y] = dec(ix[IX_Y],2)
;         if (ix[IX_Y] >= 17) ix[IX_Y] = dec(ix[IX_Y])
;     }
;     else {
;         ix[IX_Y] = dec(ix[IX_Y],2);
;         if (ix[IX_Y] < 0)
;             ix[IX_Y] = inc(ix[IX_Y]);
;     }
; }
    dec (ix+IX_Z)             ; ix[IX_Z] = dec(ix[IX_Z])
    jp m,a1s0f_ret            ; if (ix[IX_Z] < 0) return delete_enemy()
    ld a,(ix+IX_Z)
    cp 006h
    jp c,a1s06_cont1          ; if (ix[IX_Z] < 6) goto cont1
        dec (ix+IX_STATE)     ; ix[IX_STATE] = dec(ix[IX_STATE])
        ld a,(ix+IX_STATE)
        and 00fh
        cp 008h
        jp nc,a1s06_cont2     ; if ((ix[IX_STATE] & 0x0f) >= 8) goto cont2
    a1s06_cont1:
        dec (ix+IX_Y)             ; ix[IX_Y] = dec(ix[IX_Y],2)
        dec (ix+IX_Y)
        ret p                     ; if (ix[IX_Y] >= 0) return
        inc (ix+IX_Y)             ; ix[IX_Y] = -1
        ret
    a1s06_cont2:
        inc (ix+IX_Y)             ; ix[IX_Y] = inc(ix[IX_Y],2)
        inc (ix+IX_Y)
        ld a,(ix+IX_Y)
        cp 011h
        ret c                     ; if (ix[IX_Y] < 17) return
        dec (ix+IX_Y)             ; ix[IX_Y] = 16
        ret
; ------------------------------------------------------
; 敵AI処理7 07
A1S07:
AS21: ; ルーパー2
    dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
    jp m,a1s0f_ret          ; if (ix[IX_Z] < 0) return delete_enemy()
    dec (ix+IX_STATE)       ; ix[IX_STATE] = dec(ix[IX_STATE])
    ld a,(ix+IX_STATE)
    and 00fh
    cp 008h
    jp nc,a1s07_cont1       ; if ((ix[IX_STATE] & 0x0f) >= 8) {
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X],2)
        dec (ix+IX_X)
        ret                     ; return
    a1s07_cont1:            ; }
        inc (ix+IX_X)       ; ix[IX_X] = inc(ix[IX_X],2)
        inc (ix+IX_X)
        ret                 ; return
; ------------------------------------------------------
; 敵AI処理8 08 09
A1S08:
AS29: ; アイダ2
AS30: ; アイダ3
AS31: ; アイダ4
AS32: ; アイダ5
AS33: ; アイダ6
AS34: ; アイダ7
    ld (ix+008h),000h           ; ix[0x08] = 0
    ld (ix+00ch),000h           ; ix[0x0c] = 0
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s08_cont2            ; ix[IX_STATE] == 0 ならジャンプ
        jp nz,a1s08_cont1       ; ix[IX_STATE] >= 2 ならジャンプ
                                ; if (ix[IX_STATE]==1) {
            call A1s08_sub1         ; A1s08_sub1()
            inc (ix+013h)           ; ix[0x13] = inc(ix[0x13])
            ld a,(ix+013h)
            and 007h
            jp z,CallGF1B           ; if ((ix[0x13] & 7) == 0) return GF1B()
            inc (ix+011h)           ; ix[0x11] = inc(ix[0x11])
            dec (ix+014h)           ; ix[0x14] = dec(ix[0x14])
            ret p                   ; if (!is_minus(ix[0x14])) return
            ld (ix+IX_STATE),002h   ; ix[IX_STATE] = 2
            ret                     ; return
        a1s08_cont1:            ; } else if (ix[IX_STATE]>=2) {
        inc (ix+IX_Z)               ; ix[IX_Z] = inc(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 01fh
        ret c                       ; if (ix[IX_Z] < 31) return
        ld (ix+IX_TYPE),000h        ; return delete_enemy()
        ret
    a1s08_cont2:                ; } // ix[IX_STATE] == 0
    dec (ix+IX_Z)               ; ix[IX_Z] = dec(ix[IX_Z])
    ld a,(ix+IX_Z)
    cp 00ch
    ret nc                      ; if (ix[IX_Z] >= 12) return
    ld (ix+IX_STATE),001h       ; ix[IX_STATE] = 1
    ld (ix+013h),000h           ; ix[0x13] = 0
    ld (ix+014h),020h           ; ix[0x14] = 32
    ld (ix+011h),018h           ; ix[0x11] = 24
    ld a,(ix+IX_ANIM)
    or a
    ret nz                      ; if (ix[IX_ANIM] != 0) return
    ld (ix+011h),008h           ; ix[0x11] = 8
    ret                         ; return
    ; ------------------------------------------------------
    A1s08_sub1:
        ld a,(ix+011h)
        call A1s08_sub2         ; de = A1s08_sub2(ix[0x11])
        ld a,d
        add a,016h
        ld (ix+IX_X),a          ; ix[IX_X]=d+0x16
        ld a,e
        add a,007h
        ld (ix+IX_Y),a          ; ix[IX_Y] = e + 7
        ret                     ; return
    ; ------------------------------------------------------
    A1s08_sub2:
        and 01fh                
        add a,a                 
        ld e,a                  
        ld d,000h               
        ld hl,a1s08_sub2_tbl    
        add hl,de               
        ld e,(hl)
        inc hl
        ld d,(hl)               ; de = a1s08_sub2_tbl[a & 31]
        ret
    ; ------------------------------------------------------
    a1s08_sub2_tbl:
    a1s08_sub2_tbl_start:
        dw 000f9h,001fah,002fbh,003fch,004fdh,005feh,006ffh,00700h,00601h,00502h
        dw 00403h,00304h,00205h,00106h,00007h,00007h,00007h,0ff06h,0fe05h,0fd04h
        dw 0fc03h,0fb02h,0fa01h,0f900h,0faffh,0fbfeh,0fcfdh,0fdfch,0fefbh,0fffah
        dw 000f9h,000f9h,00000h,00000h,00000h,00000h
; ------------------------------------------------------
; 敵AI処理9 0A
A1S0A:
AS15: ; スケグ1
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s0a_cont3
    jp z,a1s0a_cont1
                            ; if (ix[IX_STATE] >= 2) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        jp m,a1s0f_ret          ; if(ix[IX_Z] < 0) return delete_enemy()
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X],2)
        dec (ix+IX_X)
        dec (ix+IX_Y)           ; ix[IX_Y] = dec(ix[IX_Y])
        ret                     ; return
    a1s0a_cont1:            ; } else if (ix[IX_STATE] == 1) {
        dec (ix+011h)           ; ix[0x11] = dec(ix[0x11])
        bit 0,(ix+011h)     
        jp z,a1s0a_cont2    
            dec (ix+IX_Z)       ; if (ix[0x11]&1) ix[IX_Z] = dec(ix[IX_Z])
        a1s0a_cont2:
        inc (ix+IX_Y)           ; ix[IX_Y] = inc(ix[IX_Y],2)
        inc (ix+IX_Y)
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X],2)
        dec (ix+IX_X)       
        ld a,(ix+IX_Y)
        cp 012h
        ret c                   ; if (ix[IX_Y] < 0x12) return
        ld (ix+IX_STATE),2      ; ix[IX_STATE] = 2
        ret                     ; return
    a1s0a_cont3:            ; } else if (ix[IX_STATE]<= 0) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X],2)
        inc (ix+IX_X)
        ld a,(ix+IX_X)
        cp 032h
        ret c                   ; if (ix[IX_X] < 0x32) return
        ld (ix+IX_STATE),001h   ; ix[IX_STATE] = 1
        ret                 ; }
; ------------------------------------------------------
; 敵AI処理10 0B
A1S0B:
AS16: ; スケグ2
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s0b_cont6
    jp z,a1s0b_cont3
                            ; if (ix[IX_STATE] >= 2) {
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X])
        jp m,a1s0f_ret          ; if (is_minus(ix[IX_X])) return delete_enemy()
        inc (ix+IX_Z)           ; ix[IX_Z] = inc(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 01fh
        ret c                   ; if (ix[IX_Z] < 0x1f) return
        jp a1s0f_ret            ; return delete_enemy()
    a1s0b_cont3:            ; } if (ix[IX_STATE] == 1) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
        dec (ix+011h)           ; ix[0x11] = dec(ix[0x11])
        bit 0,(ix+011h)
        jp z,a1s0b_cont4
            inc (ix+IX_Z)       ; if (ix[0x11]&1) ix[IX_Z] = inc(ix[IX_Z])
        a1s0b_cont4:
        dec (ix+IX_Y)           ; ix[IX_Y] = dec(ix[IX_Y])
        jp p,a1s0b_cont5
            ld (ix+IX_Y),000h   ; if (is_minus(ix[IX_Y])) ix[IX_Y] = 0
        a1s0b_cont5:
        ld a,(ix+IX_X)
        cp 035h
        ret c                   ; if (ix[IX_X] < 0x35) return
        ld (ix+IX_STATE),002h   ; ix[IX_STATE] = 2
        jp CallGF1B             ; return CallGF1B()
    a1s0b_cont6:            ; }
    inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
    dec (ix+011h)           ; ix[0x11] = dec(ix[0x11])
    bit 0,(ix+011h)
    jp z,a1s0b_cont7
                            ; if((ix[0x11]&1) == 1) {
        ld a,(ix+IX_Z)
        cp 003h
        jp c,a1s0b_cont7        ; if (ix[IX_Z] >= 3) ix[IX_Z] = dec(ix[IX_Z])
            dec (ix+IX_Z)
    a1s0b_cont7:            ; }
    inc (ix+IX_Y)           ; ix[IX_Y] = inc(ix[IX_Y])
    ld a,(ix+IX_Y)
    cp 017h
    ret c                   ; if (ix[IX_Y] < 0x17) return
    ld (ix+IX_STATE),001h   ; ix[IX_STATE] = 1
    ret                     ; return
