; ------------------------------------------------------
; 敵AI処理11 0C
A1S0C:
AS17: ; スケグ3
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s0c_cont4
    jp z,a1s0c_cont1
                            ; if (ix[IX_STATE] >= 2) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
        ld a,(ix+IX_X)
        cp 040h
        jp nc,a1s0f_ret         ; if (ix[IX_X] >= 0x40) return delete_enemy()
        inc (ix+IX_Z)           ; ix[IX_Z] = inc(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 01fh
        ret c                   ; if (ix[IX_Z] < 0x1f) return
        jp a1s0f_ret            ; return delete_enemy()
    a1s0c_cont1:            ; } else if (ix[IX_STATE] == 1) {
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X])
        ld a,(ix+IX_X)
        cp 00bh
        jp nc,a1s0c_cont2       ; if (ix[IX_X] < 0xb) {
            ld (ix+IX_STATE),002h   ; ix[IX_STATE] = 2
            jp CallGF1B             ; return CallGF1B()
        a1s0c_cont2:            ; }
        dec (ix+011h)           ; ix[0x11] = dec(ix[0x11])
        bit 0,(ix+011h)
        jp z,a1s0c_cont3        
            inc (ix+IX_Z)       ; if (ix[0x11]&1) ix[IX_Z] = inc(ix[IX_Z])
        a1s0c_cont3:
        dec (ix+IX_Y)           ; ix[IX_Y] = max(0,ix[IX_Y]-1)
        ret p
        ld (ix+IX_Y),000h
        ret                     ; return
    a1s0c_cont4:            ; }
    dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X])
    dec (ix+011h)           ; ix[0x11] = dec(ix[0x11])
    bit 0,(ix+011h)
    jp z,a1s0c_cont5        ; if (ix[0x11]&1) {
        ld a,(ix+IX_Z)
        cp 003h
        jp c,a1s0c_cont5
            dec (ix+IX_Z)       ; if (ix[IX_Z] >= 3) ix[IX_Z] = dec(ix[IX_Z])
    a1s0c_cont5:            ; }
    inc (ix+IX_Y)           ; ix[IX_Y] = inc(ix[IX_Y])
    ld a,(ix+IX_Y)
    cp 017h
    ret c                   ; if (ix[IX_Y] < 0x17) return
    ld (ix+IX_STATE),001h   ; ix[IX_STATE] = 1
    ret                     ; return
; ------------------------------------------------------
; 敵AI処理12 0D
AS25: ; ジェット21
AS27: ; ジェット23
A1S0D:
    ld a,(ix+IX_Z)          ; old_z = ix[IX_Z]
    cp 003h
    jp c,a1s0d_cont1        ; if (ix[IX_Z] >= 3) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        cp 00bh
        jp z,CallGF1B           ; if (old_z == 0x0b) return CallGF1B()
    a1s0d_cont1:            ; }
    dec (ix+011h)           ; ix[0x11] = dec(ix[0x11])
    bit 0,(ix+011h)
    jp z,a1s0d_cont2   
        dec (ix+IX_X)       ; if (ix[0x11]&1) ix[IX_X] = dec(ix[IX_X])
    a1s0d_cont2:            
    dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X])
    ret p                   ; if (is_plus(ix[IX_X])) return
    ld (ix+IX_TYPE),000h    ; delete_enemy()
    ret
; ------------------------------------------------------
; 敵AI処理13 0E
AS26: ; ジェット22
AS28: ; ジェット24
A1S0E:
    ld a,(ix+IX_Z)
    cp 003h
    jp c,a1s0e_cont1        ; if (ix[IX_Z] >= 3) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 00bh
        jp z,CallGF1B           ; if (ix[IX_Z] == 0x0b) return CallGF1B()
    a1s0e_cont1:            ; }
    dec (ix+011h)           ; ix[0x11] = dec(ix[0x11])
    bit 0,(ix+011h)
    jp z,a1s0e_cont2       
        inc (ix+IX_X)       ; if (ix[0x11]&1) ix[IX_X] = inc(ix[IX_X])
    a1s0e_cont2:           
    inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
    ld a,(ix+IX_X)
    cp 032h
    ret c                   ; if (ix[IX_X] < 0x32) return
    ld (ix+IX_TYPE),000h    ; delete_enemy()
    ret
; ------------------------------------------------------
; 敵AI処理14 0F
; state 0:
;     X += 1
;     X >= 0x28 で state 1
; state 1:
;     timer奇数フレーム:
;         Y += 2
;         Z -= 1
;     X -= 2
;     Xが負になったら削除
; 多分「画面右から現れて左上に逃げる」
A1S0F:
AS02: ; ムカデンス2
    ld a,(ix+IX_STATE)      
    or a
    jp nz,a1s0f_cont1       ; if (ix[IX_STATE] == 0) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X])
        ld a,(ix+IX_X)         
        cp 028h
        ret c                   ; if (ix[IX_X] < 0x28) return
        inc (ix+IX_STATE)       ; ix[IX_STATE] = inc(ix[IX_STATE])
        ret                     ; return
    a1s0f_cont1:            ; }
    dec (ix+011h)           ; ix[0x11] = dec(ix[0x11])
    bit 0,(ix+011h)
    jp z,a1s0f_cont2
                            ; if (ix[0x11]&1) {
        inc (ix+IX_Y)           ; ix[IX_Y] = inc(ix[IX_Y],2)
        inc (ix+IX_Y)
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        jp m,a1s0f_ret          ; if (is_minus(ix[IX_Z])) return delete_enemy()
    a1s0f_cont2:            ; }
        dec (ix+IX_X)       ; ix[IX_X] = dec(ix[IX_X],2)
        dec (ix+IX_X)
        ret p               ; if (!is_minus(ix[IX_X])) return
    a1s0f_ret:
    ld (ix+IX_TYPE),000h    ; return delete_enemy()
    ret
; ------------------------------------------------------
; 敵AI処理15 10
A1S10:
AS03: ; ムカデンス3
    inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X],2)
    inc (ix+IX_X)
    ld a,(ix+IX_X)
    cp 03eh
    jp c,a1s10_cont1        
        dec (ix+IX_X)       ; if (ix[IX_X] >= 0x3e) ix[IX_X] = dec(ix[IX_X],2)
        dec (ix+IX_X)
    a1s10_cont1:            
    inc (ix+IX_Z)           ; ix[IX_Z] = inc(ix[IX_Z])
    ld a,(ix+IX_Z)
    cp 01eh
    jp nc,a1s0f_ret         ; if (ix[IX_Z] >= 0x1e) return delete_enemy()
    cp 00ch
    ret nz
    jp CallGF1B             ; if (ix[IX_Z] == 0x0c) CallGF1B()
                            ; return
; ------------------------------------------------------
; 敵AI処理16 11
; if ix[IX_X] >= 3: ix[IX_X] -= 2 をして a1s10_cont1 にジャンプ
A1S11:
AS04: ; ムカデンス4
    dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X],2)
    dec (ix+IX_X)
    ld a,(ix+IX_X)
    cp 003h
    jp nc,a1s11_cont1       
        inc (ix+IX_X)       ; if (ix[IX_X] < 3) ix[IX_X] = inc(ix[IX_X],2)
        inc (ix+IX_X)
    a1s11_cont1:           
    jp a1s10_cont1          ; goto a1s10_cont1
; ------------------------------------------------------
; 敵AI処理17 12
A1S12:
AS05: ; ムカデンス5
    ld a,(ix+IX_STATE)      
    dec a                   
    jp m,a1s12_cont1
    jp z,a1s12_cont3
                            ; if (ix[IX_STATE] >= 2) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        jp m,a1s0f_ret          ; if (is_minus(ix[IX_Z])) return delete_enemy()
        dec (ix+IX_X)           ; ix[IX_X] = dec(ix[IX_X],2)
        dec (ix+IX_X)
        jp m,a1s0f_ret          ; if (is_minus(ix[IX_X])) return delete_enemy()
        ret                     ; return
    a1s12_cont1:            ; } else if (ix[IX_STATE] == 1) {
        dec (ix+IX_X)           
        dec (ix+IX_X)
        jp p,a1s12_cont2        
            ld (ix+IX_X),000h   
        a1s12_cont2:            ; ix[IX_X] = max(dec(ix[IX_X],2),0)
        inc (ix+IX_Z)           ; ix[IX_Z] = inc(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 00fh
        ret c                   ; if (ix[IX_Z] < 0xf) return
        ld (ix+IX_STATE),001h   ; ix[IX_STATE] = 1
        ret                     ; return
    a1s12_cont3:            ; }
                            ; // ix[IX_STATE] == 0
        inc (ix+IX_X)       ; ix[IX_X] = inc(ix[IX_X],2)
        inc (ix+IX_X)
        ld a,(ix+IX_X)
        cp 038h
        ret c               ; if (ix[IX_X] < 0x38) return
        ld (ix+IX_STATE),2  ; ix[IX_STATE] = 2
        ret
; ------------------------------------------------------
; 敵AI処理18 13
; if state == 0:
;     X -= 2
;     if X < 0: X = 0; state = 2
; elif state == 1:
;     X = min(X+2, 0x3c); Z += 1
;     if Z >= 0x0f: state = 1
; else:
;     Z -= 1
;     if Z < 0: delete_enemy()
;     X += 2
A1S13:
AS06: ; ムカデンス6
    ld a,(ix+IX_STATE)
    dec a
    jp m,a1s13_cont1
    jp z,a1s13_cont3
                            ; if (ix[IX_STATE] >= 2) {
        dec (ix+IX_Z)           ; ix[IX_Z] = dec(ix[IX_Z])
        jp m,a1s0f_ret          ; if (is_minus(ix[IX_Z])) return delete_enemy()
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X],2)
        inc (ix+IX_X)
        ret                     ; return
    a1s13_cont1:            ; } else if (ix[IX_STATE] == 1) {
        inc (ix+IX_X)           ; ix[IX_X] = inc(ix[IX_X],2)
        inc (ix+IX_X)
        ld a,(ix+IX_X)
        cp 03ch
        jp c,a1s13_cont2        
            ld (ix+IX_X),03ch   ; if (ix[IX_X] >= 0x3c) ix[IX_X] = 0x3c
        a1s13_cont2:            
        inc (ix+IX_Z)           ; ix[IX_Z] = inc(ix[IX_Z])
        ld a,(ix+IX_Z)
        cp 00fh
        ret c                   ; if (ix[IX_Z] < 0xf) return
        ld (ix+IX_STATE),001h   ; ix[IX_STATE] = 1
        ret                     ; return
    a1s13_cont3:            ; }
        dec (ix+IX_X)       ; ix[IX_X] = dec(ix[IX_X],2)
        dec (ix+IX_X)
        ret p               ; if(!is_minus(ix[IX_X])) return
        ld (ix+IX_X),000h   ; ix[IX_X] = 0
        ld (ix+IX_STATE),2  ; ix[IX_STATE] = 2
        ret
        dec (ix+011h)       ; unreachable 到達できないのでスルー
        ret p
        ld (ix+011h),007h
        ret
; ------------------------------------------------------
; 敵AI処理19 14 15
; ix[IX_Z] = inc(ix[IX_Z])
; if ix[IX_Z] >= 0x1f: return delete_enemy()
; if ix[IX_Z] < 4: return
; if ix[IX_Z] == 0x0d: return CallGF1B()
; if ix[IX_Z] >= 0x0d: return
; if ix[IX_Z] >= 8: ix[IX_Y] = inc(ix[IX_Y], 2); return
; ix[IX_Y] = dec(ix[IX_Y], 2)
; Z=0〜3     : 何もしない
; Z=4〜7     : Yを上へ移動
; Z=8〜12    : Yを下へ移動
; Z=13       : CallGF1B
; Z=14〜30   : その場で待つ
; Z>=31      : 削除
A1S14:
AS07: ; ムカデンス7
AS08: ; ムカデンス8
    inc (ix+IX_Z)       ; ix[IX_Z] = inc(ix[IX_Z])
    ld a,(ix+IX_Z)
    cp 01fh
    jp nc,a1s0f_ret     ; if (ix[IX_Z] >= 0x1f) return delete_enemy()
    cp 004h
    ret c               ; if (ix[IX_Z] < 4) return
    cp 00dh
    jp z,CallGF1B       ; if (ix[IX_Z] == 0xd) return CallGF1B()
    ret nc              ; if (ix[IX_Z] >= 0xd) return
    cp 008h
    jp c,a1s14_cont1
                        ; if (ix[IX_Z] >= 8) {
        inc (ix+IX_Y)       ; ix[IX_Y] = inc(ix[IX_Y],2)
        inc (ix+IX_Y)
        ret                 ; return
    a1s14_cont1:        ; }
    dec (ix+IX_Y)       ; ix[IX_Y] = dec(ix[IX_Y],2)
    dec (ix+IX_Y)
    ret
