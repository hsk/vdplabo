    inline void renderSprites(int lineNumber, unsigned short* renderPosition, bool rendering)
    {
        static const unsigned char bit[8] = {
            0b10000000,
            0b01000000,
            0b00100000,
            0b00010000,
            0b00001000,
            0b00000100,
            0b00000010,
            0b00000001};
        bool si = this->ctx->reg[1] & 0b00000010;
        bool mag = this->ctx->reg[1] & 0b00000001;
        int sn = 0;
        int tsn = 0;
        unsigned char dlog[256];
        unsigned char wlog[256];
        memset(dlog, 0, sizeof(dlog));
        memset(wlog, 0, sizeof(wlog));
        bool limitOver = false;
        for (int i = 0; i < 32; i++) {
            int cur = ac.sa + i * 4;
            unsigned char y = this->ctx->ram[cur++];
            if (208 == y) break;
            int x = this->ctx->ram[cur++];
            unsigned char ptn = this->ctx->ram[cur++];
            unsigned char col = this->ctx->ram[cur++];
            if (col & 0x80) x -= 32;
            col &= 0b00001111;
            y++;
            if (mag) {
                if (si) {
                    // 16x16 x 2
                    if (y <= lineNumber && lineNumber < y + 32) {
                        sn++;
                        if (!col) tsn++;
                        if (5 == sn) {
                            this->ctx->stat &= 0b11100000;
                            this->ctx->stat |= 0b01000000 | i;
                            if (4 <= tsn) break;
                            limitOver = true;
                        } else if (sn < 5) {
                            this->ctx->stat &= 0b11100000;
                            this->ctx->stat |= i;
                        }
                        int pixelLine = lineNumber - y;
                        cur = ac.sg + (ptn & 252) * 8 + pixelLine % 16 / 2 + (pixelLine < 16 ? 0 : 8);
                        bool overflow = false;
                        for (int j = 0; !overflow && j < 16; j++, x++) {
                            if (x < 0) continue;
                            if (wlog[x] && !limitOver) {
                                this->ctx->stat |= 0b00100000;
                            }
                            if (0 == dlog[x]) {
                                if (this->ctx->ram[cur] & bit[j / 2]) {
                                    if (col && rendering) renderPosition[x] = this->palette[col];
                                    dlog[x] = col;
                                    wlog[x] = 1;
                                }
                            }
                            overflow = x == 0xFF;
                        }
                        cur += 16;
                        for (int j = 0; !overflow && j < 16; j++, x++) {
                            if (x < 0) continue;
                            if (wlog[x] && !limitOver) {
                                this->ctx->stat |= 0b00100000;
                            }
                            if (0 == dlog[x]) {
                                if (this->ctx->ram[cur] & bit[j / 2]) {
                                    if (col && rendering) renderPosition[x] = this->palette[col];
                                    dlog[x] = col;
                                    wlog[x] = 1;
                                }
                            }
                            overflow = x == 0xFF;
                        }
                    }
                } else {
                    // 8x8 x 2
                    if (y <= lineNumber && lineNumber < y + 16) {
                        sn++;
                        if (!col) tsn++;
                        if (5 == sn) {
                            this->ctx->stat &= 0b11100000;
                            this->ctx->stat |= 0b01000000 | i;
                            if (4 <= tsn) break;
                            limitOver = true;
                        } else if (sn < 5) {
                            this->ctx->stat &= 0b11100000;
                            this->ctx->stat |= i;
                        }
                        cur = ac.sg + ptn * 8 + lineNumber % 8;
                        bool overflow = false;
                        for (int j = 0; !overflow && j < 16; j++, x++) {
                            if (x < 0) continue;
                            if (wlog[x] && !limitOver) {
                                this->ctx->stat |= 0b00100000;
                            }
                            if (0 == dlog[x]) {
                                if (this->ctx->ram[cur] & bit[j / 2]) {
                                    if (col && rendering) renderPosition[x] = this->palette[col];
                                    dlog[x] = col;
                                    wlog[x] = 1;
                                }
                            }
                            overflow = x == 0xFF;
                        }
                    }
                }
            } else {
                if (si) {
                    // 16x16 x 1
                    if (y <= lineNumber && lineNumber < y + 16) {
                        sn++;
                        if (!col) tsn++;
                        if (5 == sn) {
                            this->ctx->stat &= 0b11100000;
                            this->ctx->stat |= 0b01000000 | i;
                            if (4 <= tsn) break;
                            limitOver = true;
                        } else if (sn < 5) {
                            this->ctx->stat &= 0b11100000;
                            this->ctx->stat |= i;
                        }
                        int pixelLine = lineNumber - y;
                        cur = ac.sg + (ptn & 252) * 8 + pixelLine % 8 + (pixelLine < 8 ? 0 : 8);
                        bool overflow = false;
                        for (int j = 0; !overflow && j < 8; j++, x++) {
                            if (x < 0) continue;
                            if (wlog[x] && !limitOver) {
                                this->ctx->stat |= 0b00100000;
                            }
                            if (0 == dlog[x]) {
                                if (this->ctx->ram[cur] & bit[j]) {
                                    if (col && rendering) renderPosition[x] = this->palette[col];
                                    dlog[x] = col;
                                    wlog[x] = 1;
                                }
                            }
                            overflow = x == 0xFF;
                        }
                        cur += 16;
                        for (int j = 0; !overflow && j < 8; j++, x++) {
                            if (x < 0) continue;
                            if (wlog[x] && !limitOver) {
                                this->ctx->stat |= 0b00100000;
                            }
                            if (0 == dlog[x]) {
                                if (this->ctx->ram[cur] & bit[j]) {
                                    if (col && rendering) renderPosition[x] = this->palette[col];
                                    dlog[x] = col;
                                    wlog[x] = 1;
                                }
                            }
                            overflow = x == 0xFF;
                        }
                    }
                } else {
                    // 8x8 x 1
                    if (y <= lineNumber && lineNumber < y + 8) {
                        sn++;
                        if (!col) tsn++;
                        if (5 == sn) {
                            this->ctx->stat &= 0b11100000;
                            this->ctx->stat |= 0b01000000 | i;
                            if (4 <= tsn) break;
                            limitOver = true;
                        } else if (sn < 5) {
                            this->ctx->stat &= 0b11100000;
                            this->ctx->stat |= i;
                        }
                        cur = ac.sg + ptn * 8 + lineNumber % 8;
                        bool overflow = false;
                        for (int j = 0; !overflow && j < 8; j++, x++) {
                            if (x < 0) continue;
                            if (wlog[x] && !limitOver) {
                                this->ctx->stat |= 0b00100000;
                            }
                            if (0 == dlog[x]) {
                                if (this->ctx->ram[cur] & bit[j]) {
                                    if (col && rendering) renderPosition[x] = this->palette[col];
                                    dlog[x] = col;
                                    wlog[x] = 1;
                                }
                            }
                            overflow = x == 0xFF;
                        }
                    }
                }
            }
        }
    }
