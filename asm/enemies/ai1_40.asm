; ------------------------------------------------------
; 敵AI処理40 2F 31 32 33 34 35 36
A1S2F:
    jp GF23                     ; return GF23()
; ------------------------------------------------------
; 敵AI処理41 30 敵弾処理
A1S30:
    jp GF1A                     ; return GF1A()
;-------------------------------------------------------
;z -= 1
;if flag9 & 1: y = min(y + 3, 0x14)
;state = rlc(state)
;if (state&1): return
;timer--
;if timer < 0: delete_enemy()
GF23:
    dec (ix+IX_Z)               ; ix[IX_Z] = dec(ix[IX_Z])
    jp m,Gf1asub1_remove_sprite ; if (is_minus(ix[IX_Z])) return delete_enemy()
    bit 0,(ix+IX_MINI)
    jp z,gf23_cont1
                                 ; if (ix[9]&1) {
        ld a,(ix+IX_Y)
        cp 014h
        jp nc,gf23_cont1
                                    ; if (ix[IX_Y] < 0x14) {
            add a,003h
            ld (ix+IX_Y),a              ; ix[IX_Y] = inc(ix[IX_Y],3)
            cp 014h
            ret c                       ; if (ix[IX_Y] < 0x14) return
            ld (ix+IX_Y),014h           ; ix[IX_Y] = 0x14
            ret                         ; return
                                    ; }
    gf23_cont1:                 ; }
    rlc (ix+IX_STATE)           ; carry,ix[IX_STATE] = rlc(ix[IX_STATE])
    ret c                       ; if (carry) return
    dec (ix+IX_ANIM)            ; ix[IX_ANIM] = dec(ix[IX_ANIM])
    ret p                       ; if (!is_minus(ix[IX_ANIM])) return
    ld (ix+IX_TYPE),000h        ; return delete_enemy()
    ret

; 敵弾処理
GF1A:
;timer -= 1
;if timer < 0: timer = 3
;if z <= 0: return delete_enemy()
;if speed2 >= speed1:
;    update_enemy_movement_vector();frac += speed1
;    if frac >= speed2: frac -= speed2;z -= 1
; else:
;     z -= 1; frac += speed2
;     if frac < speed1: return
;     frac -= speed1
;     return update_enemy_movement_vector()
    dec (ix+IX_ANIM)            ; ix[IX_ANIM] = dec(ix[IX_ANIM])
    jp p,gf1a_cont1
                                ; if (is_minus(ix[IX_ANIM])) {
        ld (ix+IX_ANIM),003h        ; ix[IX_ANIM] = 3
    gf1a_cont1:                 ; }
    ld a,(ix+IX_Z)
    or a
    jp z,Gf1asub1_remove_sprite ; if (ix[IX_Z]==0 || is_minus(ix[IX_Z])) return delete_enemy()
    jp m,Gf1asub1_remove_sprite
    ld a,(ix+IX_MAJOR_AXIS)
    cp (ix+IX_LIFE)
    jp c,gf1a_cont2
                                 ; if (ix[IX_MAJOR_AXIS] >= ix[IX_LIFE]) {
        call Gf1asub1_update_enemy_movement_vector ; Gf1asub1_update_enemy_movement_vector()
        ld a,(ix+IX_BRE_WORK)
        add a,(ix+IX_LIFE)
        ld (ix+IX_BRE_WORK),a       ; ix[IX_BRE_WORK] = inc(ix[IX_BRE_WORK],ix[IX_LIFE])
        sub (ix+IX_MAJOR_AXIS)
        ret c                       ; if (ix[IX_BRE_WORK] < ix[IX_MAJOR_AXIS]) return
        ld (ix+IX_BRE_WORK),a       ; ix[IX_BRE_WORK] = dec(ix[IX_BRE_WORK],ix[IX_MAJOR_AXIS])
        dec (ix+IX_Z)               ; ix[IX_Z] = dec(ix[IX_Z])
        ret                         ; return
    gf1a_cont2:                 ; }
    dec (ix+IX_Z)               ; ix[IX_Z] = dec(ix[IX_Z])
    ld a,(ix+IX_BRE_WORK)
    add a,(ix+IX_MAJOR_AXIS)
    ld (ix+IX_BRE_WORK),a       ; ix[IX_BRE_WORK] = inc(ix[IX_BRE_WORK],ix[IX_MAJOR_AXIS])
    sub (ix+IX_LIFE)
    ret c                       ; if (ix[IX_BRE_WORK] < ix[IX_LIFE]) return
    ld (ix+IX_BRE_WORK),a       ; ix[IX_BRE_WORK] = dec(ix[IX_BRE_WORK],ix[IX_LIFE])
    ; --------------------------------------------------------------------------
    ; 敵のベクトル移動・座標更新
    ; 速度ベクトルに基づいて敵座標を更新
    ; 敵弾（または短寿命エフェクト）の処理だと思われる
    Gf1asub1_update_enemy_movement_vector:
        ; # Bresenham風ベクトル移動
        ; if dy >= dx:
        ;     x += vx; frac += dx
        ;     if frac >= dy: frac -= dy; y += vy
        ; else:
        ;     y += vy; frac += dy
        ;     if frac >= dx: frac -= dx; x += vx
        ld a,(ix+IX_ABS_DX)
        cp (ix+IX_ABS_DY)
        jp c,Gf1asub1_enemy_x_velocity_update
                                ; if (ix[IX_ABS_DX] >= ix[IX_ABS_DY]) {
            ld a,(ix+IX_X)
            add a,(ix+IX_SIGNX)
            ld (ix+IX_X),a          ; ix[IX_X] = inc(ix[IX_X],ix[IX_SIGNX])
            ld a,(ix+IX_BRE)
            add a,(ix+IX_ABS_DY)
            ld (ix+IX_BRE),a        ; ix[IX_BRE] = inc(ix[IX_BRE],ix[IX_ABS_DY])
            sub (ix+IX_ABS_DX)
            ret c                   ; if(ix[IX_BRE] < ix[IX_ABS_DX]) return
            ld (ix+IX_BRE),a        ; ix[IX_BRE] = dec(ix[IX_BRE],ix[IX_ABS_DX])
            ld a,(ix+IX_Y)
            add a,(ix+IX_SIGNY)
            ld (ix+IX_Y),a          ; ix[IX_Y] = inc(ix[IX_Y],ix[IX_SIGNY])
            ret                     ; return
                                ; }
        ; 敵X速度更新
        Gf1asub1_enemy_x_velocity_update: ; // ix[IX_ABS_DX] < ix[IX_ABS_DY]
        ld a,(ix+IX_Y)
        add a,(ix+IX_SIGNY)
        ld (ix+IX_Y),a          ; ix[IX_Y] = inc(ix[IX_Y],ix[IX_SIGNY])
        ld a,(ix+IX_BRE)
        add a,(ix+IX_ABS_DX)     
        ld (ix+IX_BRE),a        ; ix[IX_BRE] = inc(ix[IX_BRE],ix[IX_ABS_DX])
        sub (ix+IX_ABS_DY)
        ret c                   ; if(ix[IX_BRE] < ix[IX_ABS_DX]) return
        ld (ix+IX_BRE),a        ; ix[IX_BRE] = dec(ix[IX_BRE],ix[IX_ABS_DX])
        ld a,(ix+IX_X)
        add a,(ix+IX_SIGNX)
        ld (ix+IX_X),a          ; ix[IX_X] = inc(ix[IX_X],ix[IX_SIGNX])
        ret
; 敵を削除
Gf1asub1_remove_sprite:
    ld (ix+IX_TYPE),000h ; delete_enemy()
    ret
