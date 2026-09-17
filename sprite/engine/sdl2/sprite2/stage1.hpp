// ----------------------------------------
// V9938 Sprite Mode 2 emulator
// ----------------------------------------
// SDLに依存しないエンジン本体。stage1.cpp から利用する。
// python/sprite2/stage1.py と同じ設計(Phase 1: 全画面描画)のC++移植版。
// sprite1にはない sprite color table(行ごとの色指定) と
// CCビットによる重ね合わせ(OR)を持つ。
#pragma once

#include <algorithm>
#include <array>
#include <cstdint>

inline constexpr uint32_t rgb(uint8_t r, uint8_t g, uint8_t b) {
    return (static_cast<uint32_t>(r) << 16) | (static_cast<uint32_t>(g) << 8) | b;
}

class V9938 {
public:
    static constexpr int SCREEN_WIDTH = 256;
    static constexpr int SCREEN_HEIGHT = 192;
    static constexpr int SPRITE_COUNT = 32;
    static constexpr int SPRITE_PATTERN_COUNT = 256;

    struct Sprite {
        int x = 0;
        int y = 0;
        int pattern = 0;
        int color = 0;
    };

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

    bool sprite_mag = false;
    bool sprite_size16 = false;

    V9938() {
        for (auto& row : sprite_color_table_) row = 15;
    }

    void set_sprite_pattern(int ch, const std::array<uint8_t, 8>& data) {
        sprite_patterns_[ch] = data;
    }

    void set_sprite_color(int ch, const std::array<uint8_t, 8>& colors) {
        for (int i = 0; i < 8; i++) sprite_color_table_[ch * 8 + i] = colors[i];
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

    void set_sprite(int no, int x, int y, int pattern, int color) {
        sprites_[no] = Sprite{x, y, pattern, color};
    }

    // framebuffer: SCREEN_WIDTH * SCREEN_HEIGHT 個。1pixel = 0x00RRGGBB
    void render_sprite2(uint32_t* framebuffer) const {
        std::fill(framebuffer, framebuffer + SCREEN_WIDTH * SCREEN_HEIGHT, PALETTE[1]);
        std::array<uint8_t, SCREEN_WIDTH * SCREEN_HEIGHT> draw_buffer{};

        for (int i = 0; i < SPRITE_COUNT; i++) {
            const Sprite& spr = sprites_[i];

            struct Block { int bx, by, pat; };
            std::array<Block, 4> blocks;
            int block_count;
            if (sprite_size16) {
                int base = spr.pattern & 0xFC;
                blocks = {Block{0, 0, base + 0}, Block{8, 0, base + 1},
                          Block{0, 8, base + 2}, Block{8, 8, base + 3}};
                block_count = 4;
            } else {
                blocks[0] = Block{0, 0, spr.pattern};
                block_count = 1;
            }

            for (int b = 0; b < block_count; b++) {
                const auto& pattern = sprite_patterns_[blocks[b].pat];
                for (int py = 0; py < 8; py++) {
                    uint8_t bits = pattern[py];
                    uint8_t color_byte = sprite_color_table_[i * 8 + py];
                    bool cc_bit = (color_byte & 0x40) != 0;
                    int color_index = color_byte & 0x0F;
                    uint32_t color = PALETTE[color_index];
                    for (int px = 0; px < 8; px++) {
                        if (!(bits & (0x80 >> px))) continue;
                        if (sprite_mag) {
                            int x = spr.x + (blocks[b].bx + px) * 2;
                            int y = spr.y + (blocks[b].by + py) * 2;
                            for (int oy = 0; oy < 2; oy++) {
                                for (int ox = 0; ox < 2; ox++) {
                                    put_pixel(framebuffer, draw_buffer, x + ox, y + oy, color_index, color, cc_bit);
                                }
                            }
                        } else {
                            int x = spr.x + blocks[b].bx + px;
                            int y = spr.y + blocks[b].by + py;
                            put_pixel(framebuffer, draw_buffer, x, y, color_index, color, cc_bit);
                        }
                    }
                }
            }
        }
    }

private:
    static void put_pixel(uint32_t* framebuffer, std::array<uint8_t, SCREEN_WIDTH * SCREEN_HEIGHT>& draw_buffer,
                           int x, int y, int color_index, uint32_t color, bool cc_bit) {
        if (x < 0 || x >= SCREEN_WIDTH || y < 0 || y >= SCREEN_HEIGHT) return;
        int idx = y * SCREEN_WIDTH + x;
        if (draw_buffer[idx] == 0) {
            draw_buffer[idx] = static_cast<uint8_t>(color_index);
            framebuffer[idx] = color;
        } else if (cc_bit) {
            draw_buffer[idx] |= static_cast<uint8_t>(color_index);
            framebuffer[idx] = PALETTE[draw_buffer[idx]];
        }
    }

    std::array<Sprite, SPRITE_COUNT> sprites_{};
    std::array<std::array<uint8_t, 8>, SPRITE_PATTERN_COUNT> sprite_patterns_{};
    std::array<uint8_t, SPRITE_PATTERN_COUNT * 8> sprite_color_table_{};
};
