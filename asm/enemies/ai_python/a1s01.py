IX_TYPE = 0
IX_Z = 3
IX_Y = 4
IX_X = 5
IX_STATE = 0x10
def dec(v,n=1):
    return (v - n) & 0xFF
def inc(v,n=1):
    return (v + n) & 0xFF

# ------------------------------------------------------
# 敵AI処理1 01
def A1S01(ix):
    if ix[IX_STATE] != 0: # (ix+0x10)
        ix[IX_Y] = dec(ix[IX_Y]) # dec (ix+0x04)
        if ix[IX_Y] < 0x80: return # ret p # Z80のDEC後のSフラグ判定
        ix[IX_TYPE] = 0 # 敵削除
        return
    ix[IX_Z] = dec(ix[IX_Z])
    if ix[IX_Z] >= 4: return # cp 4
    ix[IX_STATE] = inc(ix[IX_STATE]) # inc (ix+0x10)

ix = bytearray(0x11)
ix[IX_TYPE] = 1
ix[IX_Z] = 32
ix[IX_Y] = 17
while ix[IX_TYPE] != 0:
    A1S01(ix)
    print(f"{list(ix)}")
