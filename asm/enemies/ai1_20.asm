; ------------------------------------------------------
; 敵AI処理20 16 17
; z--
; if z < 0: delete
; if z >= 0x12: return
; if z == 0x0c: CallGF1B()
; if 6 <= z < 0x0c: y += 2
; else: y -= 2
; Z=17〜12 : Y下降
; Z=11〜6  : Y上昇
; Z=5〜0   : Y下降
A1S16:
AS09: ; ムカデンス9
AS10: ; ムカデンス10
    dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
    jp m,a1s0f_ret          ; if (is_minus(ix[IX_Z])) return delete_enemy()
    ld a,(ix+IX_Z)
    cp 012h
    ret nc                  ; if (ix[IX_Z] >= 0x12) return
    cp 00ch
    jp z,CallGF1B           ; if (ix[IX_Z] == 0x0c) return CallGF1B()
    jp nc,a1s16_cont1
                            ; if (ix[IX_Z] < 0x0c) {
        cp 006h
        jp c,a1s16_cont1
                                ; if (ix[IX_Z] >= 6) {
            inc (ix+IX_Y)           ; ix[IX_Y] = inc(ix[IX_Y],2)
            inc (ix+IX_Y)
            ret                     ; return
                                ; }
    a1s16_cont1:            ; }
    dec (ix+IX_Y)           ; ix[IX_Y] = dec(ix[IX_Y],2)
    dec (ix+IX_Y)
    ret
; ------------------------------------------------------
; 敵AI処理21 18 19
; if x > 0x1a: x -= 1
; elif x < 0x1a: x += 1
; timer -= 1
; if (timer & 1) == 0: return
; z -= 1
; if is_minus(z): delete_enemy()
; if z != 0x14: return
; return CallGF1B()
; - Xを常に0x1Aへ寄せる
; - 奇数フレームだけZを進める
; - Z==0x14でイベント発生
; - Z<0で削除
A1S18:
AS11: ; ムカデンス11
AS12: ; ムカデンス12
    ld a,(ix+IX_X)
    cp 01ah
    jp z,a1s18_cont2        ; ix[IX_X] == 0x1a なら a1s18_cont2
    jp c,a1s18_cont1        ; ix[IX_X] < 0x1a なら a1s18_cont1
                            ; if (ix[IX_X] > 0x1a) {
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X])
        jp a1s18_cont2
    a1s18_cont1:            ; } else if (ix[IX_X] < 0x1a) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
    a1s18_cont2:            ; }
    dec (ix+011h)           ; ix[0x11] = dec(ix[0x11])
    bit 0,(ix+011h)
    ret z                   ; if ((ix[0x11]&1)==0) return
    dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
    jp m,a1s0f_ret          ; if (is_minus(ix[IX_Z])) return delete_enemy()
    ld a,(ix+IX_Z)
    cp 014h
    ret nz                  ; if (ix[IX_Z] != 0x14) return
    jp CallGF1B             ; return CallGF1B()
; ------------------------------------------------------
; 敵AI処理22 1A
; state 0: Y += 2; Y >= 0x14 → state 1
; state 1: Z--; timer--; timer<0 → timer=6, state 2
; state 2: X--; X<0 → state 3 + CallGF1B
; state 3: Y--; Y<0 → state 4 + CallGF1B
; state 4: Y += 2; Y >= 0x14 → state 5
; state 5: Z--; timer--; timer<0 → timer=6, state 6
; state 6: X++; X >= 0x1a → state 7
; state 7: Y--; Y<0 → state 8 + CallGF1B
; state 8: Y += 2; Y >= 0x14 → state 9
; state >= 9: Z--; Z<0 → delete
A1S1A:
AS13: ; ムカデンス13
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s1a_cont2        ; # ix[IX_STATE] == 0 で a1s1a_cont2
    jp z,a1s1a_cont3        ; # ix[IX_STATE] == 1 で a1s1a_cont3
    sub 002h
    jp m,a1s1a_cont4        ; # ix[IX_STATE] == 2 で a1s1a_cont4
    jp z,a1s1a_cont1        ; # ix[IX_STATE] == 3 で a1s1a_cont1
    sub 002h
    jp m,a1s1a_cont2        ; # ix[IX_STATE] == 4 で a1s1a_cont2
    jp z,a1s1a_cont3        ; # ix[IX_STATE] == 5 で a1s1a_cont3
    sub 002h
    jp m,a1s1a_cont5        ; # ix[IX_STATE] == 6 で a1s1a_cont5
    jp z,a1s1a_cont1        ; # ix[IX_STATE] == 7 で a1s1a_cont1
    dec a
    jp z,a1s1a_cont2        ; # ix[IX_STATE] == 8 で a1s1a_cont2
                            ; if (ix[IX_STATE] > 8) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        ret p                   ; if (!is_minus(ix[IX_Z])) return
        ld (ix+IX_TYPE),000h    ; return delete_enemy()
        ret
    a1s1a_cont1:            ; } if (ix[IX_STATE] == 3 || ix[IX_STATE] == 7) {
        dec (ix+IX_Y)           ; ix[IX_Y] = dec(ix[IX_Y])
        ret p                   ; if (!is_minus(ix[IX_Y])) return
        inc (ix+IX_Y)           ; ix[IX_Y] = inc(ix[IX_Y])
        inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
        jp CallGF1B             ; return CallGF1B()
    a1s1a_cont2:            ; } if (ix[IX_STATE] == 0 || ix[IX_STATE] == 4 || ix[IX_STATE] == 8) {
        inc (ix+IX_Y)           ; ix[IX_Y] = inc(ix[IX_Y],2)
        inc (ix+IX_Y)
        ld a,(ix+IX_Y)
        cp 014h
        ret c                   ; if (ix[IX_Y] < 0x14) return
        inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
        ret                     ; return
    a1s1a_cont3:            ; } if (ix[IX_STATE] == 1 || ix[IX_STATE] == 5) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        dec (ix+011h)           ; ix[0x11] = dec(ix[0x11])
        ret p                   ; if (!is_minus(ix[0x11])) return
        ld (ix+011h),006h       ; ix[0x11] = 6
        inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
        ret                     ; return
    a1s1a_cont4:            ; } if (ix[IX_STATE] == 2) {
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X])
        ret p                   ; if (!is_minus(ix[IX_X])) return
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
        inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
        ret                     ; return
    a1s1a_cont5:            ; } if (ix[IX_STATE] == 6) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
        ld a,(ix+IX_X)
        cp 01ah
        ret c                   ; if (ix[IX_X] < 0x1a) return
        ld (ix+IX_STATE),007h   ; ix[IX_STATE] = 7
        ret                     ; return
                            ; }
; ------------------------------------------------------
; 敵AI処理23 1B
; if state == 0:
;     z -= 1
;     if z >= 10: return
;     state = 1
;     return CallGF1B()
; else:
;     x -= 2; z -= 1
;     if not is_minus(z): return
;     delete_enemy()
A1S1B:
AS36: ; ドム緑1
    ld a,(ix+IX_STATE)      ; a = ix[IX_STATE]
    or a
    jp nz,a1s1b_cont2
                            ; if (ix[IX_STATE] == 0) {
    a1s1b_cont1:
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 00ah
        ret nc                  ; if (ix[IX_Z] >= 10) return
        ld (ix+IX_STATE),001h   ; ix[IX_STATE] = 1
        jp CallGF1B             ; return CallGF1B()
    a1s1b_cont2:            ; }
    dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X],2)
    dec (ix+IX_X)
    dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
    ret p                   ; if (!is_minus(ix[IX_Z])) return
    ld (ix+IX_TYPE),000h    ; return delete_enemy()
    ret
; ------------------------------------------------------
; 敵AI処理24 1C
; A1S1B と対になっている処理
; if ix[IX_STATE] == 0: goto A1S1B_state0
; ix[IX_X] = inc(ix[IX_X], 2)
; ix[IX_Z] = dec(ix[IX_Z])
; if not is_minus(ix[IX_Z]): return
; return delete_enemy()
A1S1C:
AS37: ; ドム緑2
    ld a,(ix+IX_STATE)      ; a = ix[IX_STATE]
    or a
    jp z,a1s1b_cont1        ; if (ix[IX_STATE] == 0) goto a1s1b_cont1
    inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X],2)
    inc (ix+IX_X)
    dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
    ret p                   ; if(!is_minus(ix[IX_Z])) return
    ld (ix+IX_TYPE),000h    ; return delete_enemy()
    ret
; ------------------------------------------------------
; 敵AI処理25 1D
; state 0: Z--; Z<0x0f → state=1, timer=8, CallGF1B()
; state 1: timer--; timer<0 → state=2
; state 2: X-=2; X<6 → state=3, timer=8, CallGF1B()
; state 3: timer--; timer<0 → state=4
; state>=4: X+=2; Z--; Z<0 → delete
A1S1D:
AS38: ; ドム緑3
AS40: ; ドム赤1
    ld a,(ix+IX_STATE)      ; a = ix[IX_STATE]
    dec a                   ; a = ix[IX_STATE]-1
    jp m,a1s1d_cont1        ; ix[IX_STATE] == 0 で a1s1d_cont1
    jp z,a1s1d_cont3        ; ix[IX_STATE] == 1 で a1s1d_cont3
    dec a
    jp z,a1s1d_cont2        ; ix[IX_STATE] == 2 で a1s1d_cont2
    dec a
    jp z,a1s1d_cont3        ; ix[IX_STATE] == 3 で a1s1d_cont3
                            ; if (ix[IX_STATE] > 3) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X],2)
        inc (ix+IX_X)
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        ret p                   ; if (!is_minus(ix[IX_Z])) return
        ld (ix+IX_TYPE),000h    ; return delete_enemy()
        ret
    a1s1d_cont1:            ; } else if (ix[IX_STATE] == 0) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 00fh
        ret nc                  ; if (ix[IX_Z] >= 0xf) return
        ld (ix+IX_STATE),001h   ; ix[IX_STATE] = 1
        ld (ix+011h),008h       ; ix[0x11] = 8
        jp CallGF1B             ; return CallGF1B()
    a1s1d_cont2:            ; } else if (ix[IX_STATE] == 2) {
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X],2)
        dec (ix+IX_X)
        ld a,(ix+IX_X)
        cp 006h
        ret nc                  ; if (ix[IX_X] >= 6) return
        ld (ix+IX_STATE),003h   ; ix[IX_STATE] = 3
        ld (ix+011h),008h       ; ix[0x11] = 8
        jp CallGF1B             ; return CallGF1B()
    a1s1d_cont3:            ; } else if (ix[IX_STATE] == 1 || ix[IX_STATE] == 3) {
        dec (ix+011h)           ; ix[0x11] = dec(ix[0x11])
        ret p                   ; if (!is_minus(ix[0x11])) return
        inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
        ret                     ; return
                            ; }
; ------------------------------------------------------
; 敵AI処理26 1E
; A1S1D の左右反転版
; if state == 0: return A1S1D_state0()
; elif state == 1: return A1S1D_state1()
; elif state == 2:
;     x += 2
;     if x < 0x2d: return
;     state = 3; timer = 8
;     return CallGF1B()
; elif state == 3: return A1S1D_state1()
; else:
;     x -= 2; z -= 1
;     if not is_minus(z): return
;     return delete_enemy()
A1S1E:
AS39: ; ドム緑4
AS41: ; ドム赤2
    ld a,(ix+IX_STATE)      ; a = ix[IX_STATE]
    dec a                   ; a = ix[IX_STATE]-1
    jp m,a1s1d_cont1        ; if (ix[IX_STATE] == 0) goto a1s1d_cont1
    jp z,a1s1d_cont3        ; if (ix[IX_STATE] == 1) goto a1s1d_cont3
    dec a
    jp z,a1s1e_cont1        ; ix[IX_STATE] == 2 で a1s1e_cont1
    dec a
    jp z,a1s1d_cont3        ; if (ix[IX_STATE] == 3) goto a1s1d_cont3
                            ; if (ix[IX_STATE] >= 4) {
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X],2)
        dec (ix+IX_X)
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        ret p                   ; if (!is_minus(ix[IX_Z])) return
        ld (ix+IX_TYPE),000h    ; return delete_enemy()
        ret
    a1s1e_cont1:            ; } if (ix[IX_STATE] == 2) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X],2)
        inc (ix+IX_X)
        ld a,(ix+IX_X)
        cp 02dh
        ret c                   ; if (ix[IX_X] < 0x2d) return
        ld (ix+IX_STATE),003h   ; ix[IX_STATE] = 3
        ld (ix+011h),008h       ; ix[0x11] = 8
        jp CallGF1B             ; return CallGF1B()
                            ; }
; ------------------------------------------------------
; 敵AI処理27 1F
; A1S1D()
; if ix[IX_STATE] != 2:
;     ix[IX_Y] = 16
;     return
; ix[0x14] -= 1
; if (ix[0x14] & 0x0f) >= 8: ix[IX_Y] = max(ix[IX_Y] - 2, 0)
; else:                      ix[IX_Y] = min(ix[IX_Y] + 2, 16)
A1S1F:
AS42: ; ドム赤3
    call A1S1D              ; A1S1D()
    ld a,(ix+IX_STATE)
    sub 002h
    jp z,a1s1f_cont1
                            ; if (ix[IX_STATE] != 2) {
        ld (ix+IX_Y),010h       ; ix[IX_Y] = 16
        ret                     ; return
    a1s1f_cont1:            ; }
    dec (ix+014h)           ; ix[0x14] = dec(ix[0x14])
    ld a,(ix+014h)
    and 00fh
    cp 008h
    jp c,a1s1f_cont2        ; if ((ix[0x14]&0xf) >= 8) {
        dec (ix+IX_Y)           ; ix[IX_Y] = dec(ix[IX_Y],2)
        dec (ix+IX_Y)
        ret p                   ; if (!is_minus(ix[IX_Y])) return
        ld (ix+IX_Y),000h       ; ix[IX_Y] = 0
        ret                     ; return
    a1s1f_cont2:            ; }
    inc (ix+IX_Y)           ; ix[IX_Y] = inc(ix[IX_Y],2)
    inc (ix+IX_Y)
    ld a,(ix+IX_Y)
    cp 010h
    ret c                   ; if (ix[IX_Y] < 16) return
    ld (ix+IX_Y),010h       ; ix[IX_Y] = 16
    ret                     ; return
; ------------------------------------------------------
; 敵AI処理28 20
; A1S1E()
; if ix[IX_STATE] == 2: goto a1s1f_cont1
; ix[IX_Y] = 16
A1S20:
AS43: ; ドム赤4
    call A1S1E              ; A1S1E()
    ld a,(ix+IX_STATE)
    sub 002h
    jp z,a1s1f_cont1        ; if (ix[IX_STATE] == 2) goto a1s1f_cont1
    ld (ix+IX_Y),010h       ; ix[IX_Y] = 16
    ret                     ; return
; ------------------------------------------------------
; 敵AI処理29 21
; if state == 0:
;     z -= 1
;     if z < 0x0f: state += 1
; elif state in (1, 4):
;     y -= 1
;     if y < 0:
;         y = 0; state += 1
;         return CallGF1B()
; elif state in (2, 5):
;     y += 1
;     if y >= 15: state += 1
; elif state == 3:
;     x += 3; z -= 1
;     if z < 8: state += 1
; else:   # state >= 6
;     z -= 1
;     if z < 0: delete_enemy()
;     x -= 1
A1S21:
AS44: ; ドム黒1
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s21_cont1        ; ix[IX_STATE] == 0 で a1s21_cont1
    jp z,a1s21_cont2        ; ix[IX_STATE] == 1 で a1s21_cont2
    sub 002h
    jp m,a1s21_cont3        ; ix[IX_STATE] == 2 で a1s21_cont3
    jp z,a1s21_cont4        ; ix[IX_STATE] == 3 で a1s21_cont4
    sub 002h
    jp m,a1s21_cont2        ; ix[IX_STATE] == 4 で a1s21_cont2
    jp z,a1s21_cont3        ; ix[IX_STATE] == 5 で a1s21_cont3
                            ; if (ix[IX_STATE] >= 6) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        jp m,a1s0f_ret          ; if (is_minus(ix[IX_Z])) return delete_enemy()
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X])
        ret                     ; return
    a1s21_cont1:            ; } else if (ix[IX_STATE] == 0) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 00fh
        ret nc                  ; if (ix[IX_Z] >= 0xf) return
        inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
        ret                     ; return
    a1s21_cont2:            ; } else if (ix[IX_STATE] == 1 || ix[IX_STATE] == 4) {
        dec (ix+IX_Y)           ; ix[IX_Y] = dec(ix[IX_Y])
        ret p                   ; if (!is_minus(ix[IX_Y])) return
        ld (ix+IX_Y),000h       ; ix[IX_Y] = 0
        inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
        jp CallGF1B             ; return CallGF1B()
    a1s21_cont3:            ; } else if (ix[IX_STATE] == 2 || ix[IX_STATE] == 5) {
        inc (ix+IX_Y)           ; ix[IX_Y] = inc(ix[IX_Y])
        ld a,(ix+IX_Y)
        cp 00fh
        ret c                   ; if (ix[IX_Y] < 15) return
        inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
        ret                     ; return
    a1s21_cont4:            ; } else if (ix[IX_STATE] == 3) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X],3)
        inc (ix+IX_X)
        inc (ix+IX_X)
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 008h
        ret nc                  ; if (ix[IX_Z] >= 8) return
        inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
        ret                     ; return
                            ; }
