// ----------------------------------------
// V9938 Sprite Mode 2 emulator
// ----------------------------------------
// SDLに依存しないエンジン本体。stage2.cpp から利用する。
// python/sprite2/stage2.py のC++移植版。Phase 2の完成形:
// 1ライン8枚制限・9th sprite・衝突判定・Y=208終端に加えて、
// sprite1にはないsprite color table(行ごとの色)+CCビットのOR重ね合わせを
// scanline単位で行う。
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
    static constexpr int SPRITE_LIMIT = 8;

    // color: 下位4bitは未使用、bit7がEarly Clock(EC)フラグ。
    // 実際の色・CCビットはsprite color tableから行ごとに取得する。
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
    bool sprite_9s = false;
    int sprite_9s_index = 0;
    bool sprite_collision = false;

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

    void set_sprite(int no, int x, int y, int pattern, int color, bool ec = false) {
        sprites_[no] = Sprite{x, y, pattern, (color | (ec ? 128 : 0)) & 0xff};
    }

    // framebuffer: SCREEN_WIDTH * SCREEN_HEIGHT 個。1pixel = 0x00RRGGBB
    void render_sprite2(uint32_t* framebuffer) {
        std::fill(framebuffer, framebuffer + SCREEN_WIDTH * SCREEN_HEIGHT, PALETTE[1]);
        sprite_9s = false;
        sprite_9s_index = 0;
        sprite_collision = false;
        for (int y = 0; y < SCREEN_HEIGHT; y++) render_line_sprites(framebuffer, y);
    }

private:
    void render_line_sprites(uint32_t* framebuffer, int y) {
        int sprites_on_line = 0;
        std::array<int, SCREEN_WIDTH> draw_log{};
        int mag = sprite_mag ? 2 : 1;
        int size = (sprite_size16 ? 16 : 8) * mag;
        for (int i = 0; i < SPRITE_COUNT; i++) {
            const Sprite& spr = sprites_[i];
            if (spr.y == 208) return;  // Y=208はスプライトテーブルの終端
            if (!(spr.y <= y && y < spr.y + size)) continue;
            sprites_on_line++;
            if (sprites_on_line > SPRITE_LIMIT) {
                sprite_9s = true;
                sprite_9s_index = i;
                return;
            }

            int py = y - spr.y;
            if (mag == 2) py >>= 1;

            std::array<int, 2> blocks;
            int block_count;
            if (sprite_size16) {
                int spr_ptn = spr.pattern & 0xFC;
                if (py >= 8) {
                    spr_ptn += 2;
                    py -= 8;
                }
                blocks = {spr_ptn, spr_ptn + 1};
                block_count = 2;
            } else {
                blocks[0] = spr.pattern;
                block_count = 1;
            }

            uint8_t color_byte = sprite_color_table_[i * 8 + py];
            bool cc_bit = (color_byte & 0x40) != 0;
            int color_index = color_byte & 0x0F;
            if (color_index == 0) continue;  // 透明色はスキップ
            uint32_t color = PALETTE[color_index];

            int x = spr.x;
            if (spr.color & 0x80) x -= 32;  // Early Clock

            for (int b = 0; b < block_count; b++) {
                uint8_t bits = sprite_patterns_[blocks[b]][py];
                for (int px = 0; px < 8; px++) {
                    for (int m = 0; m < mag; m++) {
                        if (x >= 0 && x < SCREEN_WIDTH && (bits & (0x80 >> px))) {
                            if (draw_log[x] == 0) {
                                draw_log[x] = color_index;
                                framebuffer[y * SCREEN_WIDTH + x] = color;
                            } else {
                                sprite_collision = true;
                                if (cc_bit) {
                                    draw_log[x] |= color_index;
                                    framebuffer[y * SCREEN_WIDTH + x] = PALETTE[draw_log[x]];
                                }
                            }
                        }
                        x++;
                    }
                }
            }
        }
    }

    std::array<Sprite, SPRITE_COUNT> sprites_{};
    std::array<std::array<uint8_t, 8>, SPRITE_PATTERN_COUNT> sprite_patterns_{};
    std::array<uint8_t, SPRITE_PATTERN_COUNT * 8> sprite_color_table_{};
};
