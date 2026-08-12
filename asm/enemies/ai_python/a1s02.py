IX_TYPE = 0
IX_Z = 3
IX_Y = 4
IX_X = 5
IX_STATE = 0x10

def dec(v,n=1):
    return (v - n) & 0xFF
def inc(v,n=1):
    return (v + n) & 0xFF
def CallGF1B(ix):
    # todo: EFSub5_find_empty_enemy_slot() を実装
    iy = bytearray(0x18)
    GF1B(ix, iy)


ENEMIES = [bytearray(0x18) for _ in range(0x18)]
# --------------------------------------------------------------------------
# アクティブスプライト検索
# スプライト領域で次の空いているスロットを探す
# ref gf1b gf19
def EFSub5_find_empty_enemy_slot():
    for iy in ENEMIES:
        if iy[IX_TYPE] == 0: return iy
    return None

PLAYER_POS_Y = 30

def GF1B(ix, iy):
    iy = EFSub5_find_empty_enemy_slot()
    if iy == None: return
    iy[IX_TYPE] = ix[0x0A]
    iy[IX_Y] = ix[IX_Y]
    iy[IX_X] = ix[IX_X]
    iy[IX_Z] = ix[IX_Z]
    iy[0x06] = 0
    iy[0x07] = 0
    iy[0x08] = 1
    iy[0x09] = 1
    iy[0x0B] = 0x30
    iy[0x0E] = 1
    gf1b_enemy_spawn_type_tbl = [0,0,0,4,4,2,4,4,3,5]
    iy[0x0D] = gf1b_enemy_spawn_type_tbl[ix[0x0A]]

    ld hl,(PLAYER_POS_Y)
    dec l
    dec h
    dec h
    dec h
    ld a,h
    sub (ix+005h)
    ld c,000h
    jp z,gf1b_cont1
        ld c,001h
        jp nc,gf1b_cont1
            ld a,(ix+005h)
            sub h
            ld c,0ffh
    gf1b_cont1:
    return iy

# ------------------------------------------------------
# 敵AI処理2 02
def A1S02(ix):
    if ix[IX_STATE] != 0:
        ix[IX_Y] = dec(ix[IX_Y])
        if ix[IX_Y] < 0x80: return
        ix[IX_TYPE] = 0 # 削除
        return
    ix[IX_Z] = dec(ix[IX_Z])
    if ix[IX_Z] >= 8: return
    ix[IX_STATE] = inc(ix[IX_STATE])
    CallGF1B(ix)
ix = bytearray(0x11)
ix[IX_TYPE] = 1
ix[IX_Z] = 32
while ix[IX_TYPE] != 0:
    A1S02(ix)
    print(f"{list(ix)}")
