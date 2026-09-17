// ----------------------------------------
// V9918 / TMS9918A Sprite emulator
// ----------------------------------------
// SDLに依存しないエンジン本体。stage4.cpp から利用する。
// python/sprite1/stage4.py のC++移植版。Phase 4: レジスタ駆動。
// テーブルアドレスやスプライトサイズ/拡大、ステータス(衝突・5th sprite)を
// すべてVDPレジスタ/ステータスレジスタ経由でアクセスする。
#pragma once

#include <algorithm>
#include <array>
#include <cstdint>
#include <vector>

inline constexpr uint32_t rgb(uint8_t r, uint8_t g, uint8_t b) {
    return (static_cast<uint32_t>(r) << 16) | (static_cast<uint32_t>(g) << 8) | b;
}

class V9918 {
public:
    static constexpr int SCREEN_WIDTH = 256;
    static constexpr int SCREEN_HEIGHT = 192;
    static constexpr int SPRITE_COUNT = 32;
    static constexpr int SPRITE_PATTERN_COUNT = 256;
    static constexpr int VRAM_SIZE = 16 * 1024;

    static constexpr uint32_t PALETTE[16] = {
        rgb(0, 0, 0),        // 0 Transparent / black
        rgb(0, 0, 0),        // 1 Black
        rgb(33, 200, 66),    // 2 Medium green
        rgb(94, 220, 120),   // 3 Light green
        rgb(84, 85, 237),    // 4 Dark blue
        rgb(125, 118, 252),  // 5 Light blue
        rgb(212, 82, 77),    // 6 Dark red
        rgb(66, 235, 245),   // 7 Cyan
        rgb(252, 85, 84),    // 8 Medium red
        rgb(255, 121, 120),  // 9 Light red
        rgb(212, 193, 84),   // 10 Dark yellow
        rgb(230, 206, 128),  // 11 Light yellow
        rgb(33, 176, 59),    // 12 Dark green
        rgb(201, 91, 186),   // 13 Magenta
        rgb(204, 204, 204),  // 14 Gray
        rgb(255, 255, 255),  // 15 White
    };

    V9918() : vram_(VRAM_SIZE, 0), reg_{}, stat_(0) {
        set_sprite_pattern_table(0x1b00);
        set_sprite_attribute_table(0x3800);
        set_sprite_mag(false);
        set_sprite_size16(false);
        set_5s(false);
        set_5s_index(0);
        set_collision(false);
    }

    void set_sprite_pattern_table(int addr) { reg_[6] = static_cast<uint8_t>((addr >> 11) & 3); }
    int get_sprite_pattern_table() const { return (reg_[6] & 3) << 11; }

    void set_sprite_attribute_table(int addr) { reg_[5] = static_cast<uint8_t>((addr >> 7) & 63); }
    // python版のreg[5]/reg[6]の取り違えバグをそのまま踏襲する(意図的な移植)。
    int get_sprite_attribute_table() const { return (reg_[6] & 63) << 7; }

    void set_sprite_mag(bool value) {
        reg_[1] = static_cast<uint8_t>((reg_[1] & ~1) | (value ? 1 : 0));
    }
    bool get_sprite_mag() const { return (reg_[1] & 1) != 0; }

    void set_sprite_size16(bool value) {
        reg_[1] = static_cast<uint8_t>((reg_[1] & ~2) | (value ? 2 : 0));
    }
    bool get_sprite_size16() const { return (reg_[1] & 2) != 0; }

    void set_collision(bool value) {
        stat_ = static_cast<uint8_t>((stat_ & ~(1 << 5)) | (value ? (1 << 5) : 0));
    }
    bool get_collision() const { return (stat_ & (1 << 5)) != 0; }

    void set_5s(bool value) {
        stat_ = static_cast<uint8_t>((stat_ & ~(1 << 6)) | (value ? (1 << 6) : 0));
    }
    bool get_5s() const { return (stat_ & (1 << 6)) != 0; }

    void set_5s_index(int value) {
        stat_ = static_cast<uint8_t>((stat_ & ~31) | (value & 31));
    }
    int get_5s_index() const { return stat_ & 31; }

    void set_sprite_pattern(int ch, const std::array<uint8_t, 8>& data) {
        int addr = get_sprite_pattern_table() + ch * 8;
        for (int i = 0; i < 8; i++) vram_[addr + i] = data[i];
    }

    // data: 16行 x 16bit (MSBが左端のピクセル)
    void set_sprite_pattern16x16(int ch, const std::array<uint16_t, 16>& data) {
        int base = ch & 0xFC;
        std::array<std::array<uint8_t, 8>, 4> p{};
        std::array<int, 4> idx{0, 0, 0, 0};
        for (int y = 0; y < 16; y++) {
            uint16_t row = data[y];
            int block = (y / 8) * 2;
            p[block][idx[block]++] = static_cast<uint8_t>((row >> 8) & 0xFF);
            p[block + 1][idx[block + 1]++] = static_cast<uint8_t>(row & 0xFF);
        }
        for (int i = 0; i < 4; i++) set_sprite_pattern(base + i, p[i]);
    }

    void set_sprite(int no, int x, int y, int pattern, int color, bool ec = false) {
        int addr = get_sprite_attribute_table() + no * 4;
        vram_[addr + 0] = static_cast<uint8_t>(y & 0xff);
        vram_[addr + 1] = static_cast<uint8_t>(x & 0xff);
        vram_[addr + 2] = static_cast<uint8_t>(pattern & 0xff);
        vram_[addr + 3] = static_cast<uint8_t>((color | (ec ? 128 : 0)) & 0xff);
    }

    // framebuffer: SCREEN_WIDTH * SCREEN_HEIGHT 個。1pixel = 0x00RRGGBB
    void render_sprite1(uint32_t* framebuffer) {
        std::fill(framebuffer, framebuffer + SCREEN_WIDTH * SCREEN_HEIGHT, PALETTE[1]);
        set_5s(false);
        set_5s_index(0);
        for (int y = 0; y < SCREEN_HEIGHT; y++) render_line_sprites(framebuffer, y);
    }

private:
    void render_line_sprites(uint32_t* framebuffer, int y) {
        int sprites_on_line = 0;
        std::array<int, SCREEN_WIDTH> draw_log{};
        int attr_addr = get_sprite_attribute_table();
        for (int i = 0; i < SPRITE_COUNT; i++) {
            int spr_y = vram_[attr_addr + 0];
            int x = vram_[attr_addr + 1];
            int spr_ptn = vram_[attr_addr + 2];
            int color_byte = vram_[attr_addr + 3];
            attr_addr += 4;

            if (spr_y == 208) return;  // Y=208はスプライトテーブルの終端
            spr_y = (spr_y + 1) & 255;  // 属性テーブル上のYは実際の表示位置の-1

            int color_index = color_byte & 0x0F;
            if (color_index == 0) continue;  // 透明色はスキップ
            uint32_t color = PALETTE[color_index];
            if (color_byte & 0x80) x -= 32;  // Early Clock

            int mag = get_sprite_mag() ? 2 : 1;
            int size = (get_sprite_size16() ? 16 : 8) * mag;
            if (!(spr_y <= y && y < spr_y + size)) continue;
            sprites_on_line++;
            if (sprites_on_line > 4) {
                set_5s(true);
                set_5s_index(i);
                return;
            }

            int py = y - spr_y;
            if (mag == 2) py >>= 1;

            std::array<int, 2> blocks;
            int block_count;
            if (get_sprite_size16()) {
                spr_ptn &= 0xFC;
                if (py >= 8) {
                    spr_ptn += 2;
                    py -= 8;
                }
                blocks = {spr_ptn, spr_ptn + 1};
                block_count = 2;
            } else {
                blocks[0] = spr_ptn;
                block_count = 1;
            }

            for (int b = 0; b < block_count; b++) {
                uint8_t bits = vram_[get_sprite_pattern_table() + blocks[b] * 8 + py];
                for (int px = 0; px < 8; px++) {
                    for (int m = 0; m < mag; m++) {
                        if (x >= 0 && x < SCREEN_WIDTH && (bits & (0x80 >> px))) {
                            if (draw_log[x] == 0) {
                                draw_log[x] = color_index;
                                framebuffer[y * SCREEN_WIDTH + x] = color;
                            } else {
                                set_collision(true);
                            }
                        }
                        x++;
                    }
                }
            }
        }
    }

    std::vector<uint8_t> vram_;
    std::array<uint8_t, 8> reg_;
    uint8_t stat_;
};
