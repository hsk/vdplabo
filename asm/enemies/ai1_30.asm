; ------------------------------------------------------
; 敵AI処理30 22
; if state == 0: goto A1S21_state0
; elif state in (1, 4): goto A1S21_state1
; elif state in (2, 5): goto A1S21_state2
; elif state == 3:
;     x -= 3; z -= 1
;     if z >= 8: return
;     state += 1
; else:   # state >= 6
;     z -= 1
;     if is_minus(z): return delete_enemy()
;     x += 1
A1S22:
AS45: ; ドム黒2 3体
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s21_cont1        ; if (ix[IX_STATE] == 0) goto a1s21_cont1
    jp z,a1s21_cont2        ; if (ix[IX_STATE] == 1) goto a1s21_cont2
    sub 002h
    jp m,a1s21_cont3        ; if (ix[IX_STATE] == 2) goto a1s21_cont3
    jp z,a1s22_cont1        ; ix[IX_STATE] == 3 で a1s22_cont1
    sub 002h
    jp m,a1s21_cont2        ; if (ix[IX_STATE] == 4) goto a1s21_cont2
    jp z,a1s21_cont3        ; if (ix[IX_STATE] == 5) goto a1s21_cont3
                            ; if (ix[IX_STATE] >= 6) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        jp m,a1s0f_ret          ; if (is_minus(ix[IX_Z])) return delete_enemy()
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
        ret                     ; return
    a1s22_cont1:            ; } else if (ix[IX_STATE] == 3) {
    dec (ix+IX_X)               ; ix[IX_X] = dec(ix[IX_X],3)
    dec (ix+IX_X)
    dec (ix+IX_X)
    dec (ix+IX_Z)               ; ix[IX_Z] = dec(ix[IX_Z])
    ld a,(ix+IX_Z)
    cp 008h
    ret nc                      ; if (ix[IX_Z] >= 8) return
    inc (ix+IX_STATE)           ; ix[IX_STATE] = inc(ix[IX_STATE])
    ret                         ; return
                            ; }
; ------------------------------------------------------
; 敵AI処理31 23
; if state == 0:
;     x += 2
;     if (x & 7) == 0: z += 1
;     if x >= 0x28: state = 1
; elif state == 1:
;     state = 2
;     CallGF1B()
; else:
;     z += 1
;     if z >= 0x1e: delete_enemy()
A1S23:
AS46: ; ドム青1 1体
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s23_cont3
    jp z,a1s23_cont2
    a1s23_cont1:
                            ; if (ix[IX_STATE] >= 2) {
        inc (ix+IX_Z)           ; ix[IX_Z] = inc(ix[IX_Z]) 
        ld a,(ix+IX_Z)
        cp 01eh
        jp nc,a1s0f_ret         ; if (ix[IX_Z] >= 0x1e) return delete_enemy()
        ret                     ; return
    a1s23_cont2:            ; } if (ix[IX_STATE] == 1) {
        ld (ix+IX_STATE),2      ; ix[IX_STATE] = 2
        jp CallGF1B             ; return CallGF1B()
    a1s23_cont3:            ; } // ix[IX_STATE] == 0
    inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X],2)
    inc (ix+IX_X)
    ld a,(ix+IX_X)
    and 007h
    jp nz,a1s23_cont4       ; if ((ix[IX_X]&7) == 0) {
        inc (ix+IX_Z)           ; ix[IX_Z] = inc(ix[IX_Z])
    a1s23_cont4:            ; }
    ld a,(ix+IX_X)
    cp 028h
    ret c                   ; if (ix[IX_X] < 0x28) return
    ld (ix+IX_STATE),001h   ; ix[IX_STATE} = 1
    ret                     ; return
; ------------------------------------------------------
; 敵AI処理32 24
; if state == 0:
;     x -= 2
;     if (x & 7) == 0: z += 1
;     if x < 0x11: state = 1
; elif state == 1:
;     state = 2
;     return CallGF1B()
; else:
;     z += 1
;     if z >= 0x1e: return delete_enemy()
A1S24:
AS47: ; ドム青2 1体
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s24_cont1
                            ; if (ix[IX_STATE] != 0) {
        jp nz,a1s23_cont1       ; if (ix[IX_STATE] != 1) goto a1s23_cont1
        jp z, a1s23_cont2       ; if (ix[IX_STATE] == 1) goto a1s23_cont2
    a1s24_cont1:            ; } // ix[IX_STATE] == 0
    dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X],2)
    dec (ix+IX_X)
    ld a,(ix+IX_X)
    and 007h
    jp nz,a1s24_cont2       ; if ((ix[IX_X]&7) == 0) {
        inc (ix+IX_Z)           ; ix[IX_Z] = inc(ix[IX_Z])
    a1s24_cont2:            ; }
    ld a,(ix+IX_X)
    cp 011h
    ret nc                  ; if (ix[IX_X] >= 0x11) return
    ld (ix+IX_STATE),001h   ; ix[IX_STATE] = 1
    ret
; ------------------------------------------------------
; 敵AI処理33 25 26
; if state == 0:
;     z -= 1
;     if z >= 9: return
;     state = 1
;     return CallGF1B()
; elif state == 1:
;     y -= 2
;     if y >= 7: return
;     state = 2
;     return CallGF1B()
; else:
;     z += 1
;     if z < 0x1e: return
;     return delete_enemy()
A1S25:
AS48: ; ドム青3 1体
AS49: ; ドム青4
AS51: ; ドム青6
AS52: ; ドム青7
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s25_cont2
    jp z,a1s25_cont1
                            ; if (ix[IX_STATE] >= 2) {
        inc (ix+IX_Z)           ; ix[IX_Z] = inc(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 01eh
        ret c                   ; if (ix[IX_Z] < 0x1e) return
        ld (ix+IX_TYPE),0       ; return delete_enemy()
        ret
    a1s25_cont1:            ; } else if (ix[IX_STATE] == 1) {
        dec (ix+IX_Y)           ; ix[IX_Y] = dec(ix[IX_Y],2)
        dec (ix+IX_Y)
        ld a,(ix+IX_Y)
        cp 007h
        ret nc                  ; if (ix[IX_Y] >= 7) return
        ld (ix+IX_STATE),2      ; ix[IX_STATE] = 2
        jp CallGF1B             ; return CallGF1B()
    a1s25_cont2:            ; } // ix[IX_STATE] == 0
        dec (ix+IX_Z)       ; ix[IX_Z] = dec(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 009h
        ret nc              ; if (ix[IX_Z] >= 9) return
        ld (ix+IX_STATE),1  ; ix[IX_STATE] = 1
        jp CallGF1B         ; return CallGF1B()
; ------------------------------------------------------
; 敵AI処理34 27
; if ix[IX_Z] == 0x0c: CallGF1B()
; ix[IX_Z] = dec(ix[IX_Z])
; if is_minus(ix[IX_Z]): return delete_enemy()
; if ix[IX_Z] != 10: return
; return A1S0F()
A1S27:
AS50: ; ドム青5
    ld a,(ix+IX_Z)
    cp 00ch
    call z,CallGF1B         ; if (ix[IX_Z] == 0xc) CallGF1B()
    dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
    jp m,a1s0f_ret          ; if (is_minus(ix[IX_Z])) return delete_enemy()
    ld a,(ix+IX_Z)
    cp 00ah
    ret nz                  ; if (ix[IX_Z] != 10) return
    jp A1S0F                ; return A1S0F() 
; ------------------------------------------------------
; 敵AI処理35 28
; if state == 0:
;     y -= 1
;     if y >= 0: return
;     y = 0; state = 1
;     return CallGF1B()
; elif state == 1:
;     y += 2
;     if y < 0x14: return
;     state = 2
; else:
;     z -= 1
;     if z >= 0: return
;     return delete_enemy()
A1S28:
AS01: ; ムカデンス1
AS54: ; アイダ9
AS55: ; キノコ雲1
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s28_cont2
    jp z,a1s28_cont1
                            ; if (ix[IX_STATE] >= 2) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        ret p                   ; if (!is_minus(ix[IX_Z])) return
        ld (ix+IX_TYPE),0       ; return delete_enemy()
        ret
    a1s28_cont1:            ; } else if (ix[IX_STATE] == 1) {
        inc (ix+IX_Y)           ; ix[IX_Y] = inc(ix[IX_Y],2)
        inc (ix+IX_Y)
        ld a,(ix+IX_Y)
        cp 014h
        ret c                   ; if (ix[IX_Y] < 0x14) return
        ld (ix+IX_STATE),2      ; ix[IX_STATE] = 2
        ret                     ; return
    a1s28_cont2:            ; } // ix[IX_STATE] == 0
        dec (ix+IX_Y)       ; ix[IX_Y] = dec(ix[IX_Y])
        ret p               ; if (!is_minus(ix[IX_Y])) return
        inc (ix+IX_Y)       ; ix[IX_Y] = inc(ix[IX_Y])
        ld (ix+IX_STATE),1  ; ix[IX_STATE] = 1
        jp CallGF1B         ; return CallGF1B()
; ------------------------------------------------------
; 敵AI処理36 29
; if state >= 2:
;     x += 1; z -= 1
;     if z < 0: return delete_enemy()
; elif state == 0:
;     x += 1; z += 1
;     if z >= 0x10: state += 1
; elif state == 1:
;     x -= 1
;     if x < 8: state += 1
A1S29:
AS14: ; ムカデンス14 3体
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s29_cont1
    jp z,a1s29_cont2
                            ; if (ix[IX_STATE] >= 2) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        ret p                   ; if (!is_minus(ix[IX_Z])) return
        jp a1s0f_ret            ; return delete_enemy()
    a1s29_cont1:            ; } else if (ix[IX_STATE] == 0) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
        inc (ix+IX_Z)           ; ix[IX_Z] = inc(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 010h
        ret c                   ; if (ix[IX_Z] < 0x10) return
        inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
        ret                     ; return
    a1s29_cont2:            ; } // ix[IX_STATE] == 1
    dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X])
    ld a,(ix+IX_X)
    cp 008h
    ret nc                  ; if (ix[IX_X] >= 8) return
    inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
    ret
; ------------------------------------------------------
; 敵AI処理37 2A 2C 2D
A1S2A:
    ret                     ; return
; ------------------------------------------------------
; 敵AI処理38 2B
; if state != 0:
;     y -= 1
;     if y >= 0: return
;     delete_enemy()
;     return
; z -= 2
; if z < 4:
;     state += 1
;     return CallGF1B()
; if x == 0x1a: return ; ホーミング
; if x >= 0x1a: x -= 1
; else:         x += 1
A1S2B:
    ld a,(ix+IX_STATE)
    or a
    jp z,a1s2b_cont1
                            ; if (ix[IX_STATE] != 0) {
        dec (ix+IX_Y)           ; ix[IX_Y] = dec(ix[IX_Y])
        ret p                   ; if (!is_minus(ix[IX_Y])) return
        ld (ix+IX_TYPE),0       ; delete_enemy()
        ret                     ; return
    a1s2b_cont1:            ; } // ix[IX_STATE] == 0
    dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z],2)
    dec (ix+IX_Z)
    ld a,(ix+IX_Z)
    cp 004h
    jp nc,a1s2b_cont2
                           ; if (ix[IX_Z] < 4) {
        inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
        jp CallGF1B             ; return CallGF1B()
    a1s2b_cont2:            ; }
    ld a,(ix+IX_X)
    cp 01ah
    ret z                   ; if (ix[IX_X] == 0x1a) return
    jp c,a1s2b_cont3        ; if (ix[IX_X] >= 0x1a) {
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X])
        ret                     ; return
    a1s2b_cont3:            ; }
    inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
    ret
; ------------------------------------------------------
; 敵AI処理39 2E
; if GAME_STAGE != 15:
;     ix[IX_ANIM] ^= 1
;     z -= 1
;     if z < 0: delete_enemy()
; else:
;     if type != 0x20: goto normal_processing
;     z -= 1
;     if z < 0: delete_enemy()
;     state -= 1
;     if (state & 0x1f) >= 16:
;         y -= 2
;         if y < 0: y = 0
;     else:
;         y += 2
;         if y >= 0x13: y = 0x13
A1S2E:
; 地上物なはず
    ld a,(GAME_STAGE)       ; a = GAME_STAGE
    cp 00fh
    jr z,a1s2e_cont1
                            ; if (GAME_STAGE!=15) {
        ld a,(ix+IX_ANIM)
        xor 001h
        ld (ix+IX_ANIM),a           ; ix[IX_ANIM] = ix[IX_ANIM] ^ 1
        a1s2e_ret:
            dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
            ret p                   ; if (!is_minus(ix[IX_Z])) return
            ld (ix+IX_TYPE),0       ; delete_enemy()
            ret                     ; return
    a1s2e_cont1:            ; } // GAME_STAGE == 15
    ld a,(ix+IX_TYPE)
    cp 020h
    jp nz,a1s2e_ret         ; if (ix[IX_TYPE] != 0x20) goto a1s2e_ret
    dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
    jp m,a1s0f_ret          ; if (is_minus(ix[IX_Z])) return delete_enemy()
    dec (ix+IX_STATE)       ; ix[IX_STATE] = dec(ix[IX_STATE])
    ld a,(ix+IX_STATE)
    and 01fh
    cp 010h
    jr c,a1s2e_cont2        ; if((ix[IX_STATE] & 0x1f) >= 0x10) {
        dec (ix+IX_Y)           ; ix[IX_Y] = dec(ix[IX_Y],2)
        dec (ix+IX_Y)
        ret p                   ; if (!is_minus(ix[IX_Y])) return
        ld (ix+IX_Y),000h       ; ix[IX_Y] = 0
        ret                     ; return
    a1s2e_cont2:            ; }
    inc (ix+IX_Y)           ; ix[IX_Y] = inc(ix[IX_Y],2)
    inc (ix+IX_Y)
    ld a,(ix+IX_Y)
    cp 013h
    ret c                   ; if (ix[IX_Y] < 0x13) return
    ld (ix+IX_Y),013h       ; ix[IX_Y] = 0x13
    ret                     ; return
