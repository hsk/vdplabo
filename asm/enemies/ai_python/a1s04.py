def A1S04(ix):
    state = ix[0x10] - 1
    if state < 0:
        ix[5] += 2
        if ix[5] < 40: return
        ix[0x10] = 1
        return
    if state == 0:
        # a1s04_cont2 (state == 1)
        ix[5] -= 1
        if ix[5] < 0:
            ix[3] -= 1
            if ix[3] >= 3:
                return
        ix[5] += 1
        ix[0x10] = 2
        return
    # state > 1
    ix[5] += 2
    if ix[5] < 60: return
    ix[0] = 0  # enemy delete
