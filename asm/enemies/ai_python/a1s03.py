# ------------------------------------------------------
# 敵AI処理3 03
def A1S03(ix):
    state = ix[0x10] - 1
    if state < 0:
        ix[5] += 1
        ix[3] -= 1
        if ix[3] >= 0: return
        ix[0] = 0  # enemy delete
        return CallGF1B()
    if state == 0:
        ix[5] -= 2
        if ix[5] >= 5: return
        ix[0x10] = 2
        return CallGF1B()
    ix[3] -= 1
    if ix[3] < 0:
        ix[0] = 0
        return
    ix[5] += 2
    if ix[5] < 60: return
    ix[0] = 0
def CallGF1B():
    pass
