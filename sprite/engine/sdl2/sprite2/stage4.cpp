// ----------------------------------------
// V9938 Sprite Mode 2 emulator (SDL2)
// ----------------------------------------
// stage4.hpp の V9938 クラスを読み込んで動かすだけの薄いドライバ。
// ROM クラスは stage1〜3 と同じ内容(29個のスプライトが跳ね回りつつ、
// CCビットを立てた3個のスプライトが重なり合う「ベン図」デモ)。
// レジスタ経由のアクセサを使う点だけが異なる。
#include "stage4.hpp"

#include <SDL.h>

#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <vector>

namespace {

constexpr int kScale = 3;
constexpr int kBounceCount = 29;

double random_range(double lo, double hi) {
    return lo + (hi - lo) * (std::rand() / static_cast<double>(RAND_MAX));
}

class ROM {
public:
    explicit ROM(V9938& vdp) : vdp_(vdp) {}

    void init() {
        vdp_.set_sprite_pattern(0, {
            0b00111100,
            0b01111110,
            0b11111111,
            0b11011011,
            0b11111111,
            0b01111110,
            0b00111100,
            0b00011000,
        });
        vdp_.set_sprite_pattern(1, {
            0b00011000,
            0b00111100,
            0b01111110,
            0b11111111,
            0b01111110,
            0b00111100,
            0b00011000,
            0b00000000,
        });
        vdp_.set_sprite_pattern16x16(4, {
            0b0001111111111000,
            0b0011111111111100,
            0b0110111100001110,
            0b0100111011110110,
            0b1110110111111011,
            0b1110110111111011,
            0b1110110111111111,
            0b1110110000001111,
            0b1110110111110111,
            0b1110110111111011,
            0b1110110111111011,
            0b1110110111111011,
            0b0110111011110110,
            0b0110111100001110,
            0b0011111111111100,
            0b0001111111111000,
        });
        vdp_.set_sprite_pattern16x16(8, {
            0b0000000110000000,
            0b0000001111000000,
            0b0000011111100000,
            0b0000111111110000,
            0b0001111111111000,
            0b0011111111111100,
            0b0111111111111110,
            0b1111111111111111,
            0b1111111111111111,
            0b0111111111111110,
            0b0011111111111100,
            0b0001111111111000,
            0b0000111111110000,
            0b0000011111100000,
            0b0000001111000000,
            0b0000000110000000,
        });
        // 重ね合わせデモ用の8x8塗りつぶし円パターン(ベン図らしく丸にする)
        vdp_.set_sprite_pattern(2, {
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b11111111,
            0b11111111,
            0b01111110,
            0b00111100,
        });

        for (int i = 0; i < kBounceCount; i++) {
            Sprite& s = sprites_[i];
            s.x = 16 + i * 6;
            s.y = 40 + (i % 2) * 40;
            s.color = (i % 14) + 2;
            s.dx = random_range(-2.0, 2.0);
            s.dy = random_range(-2.0, 2.0);
            vdp_.set_sprite_color(i, fill8(static_cast<uint8_t>(s.color)));
        }
        // 残り3枚(29,30,31番)はCCビットを立てた重ね合わせデモ用に固定で使う。
        venn_[0] = {29, 0.0, 2};                    // Medium green
        venn_[1] = {30, 2.0 * M_PI / 3.0, 4};        // Dark blue
        venn_[2] = {31, 4.0 * M_PI / 3.0, 8};        // Medium red
        for (auto& v : venn_) {
            vdp_.set_sprite_color(v.index, fill8(static_cast<uint8_t>(v.color | 0x40)));
        }
        mode_ = 3;
    }

    void run(int frame) {
        if (frame % 180 == 0) {
            mode_ = (mode_ + 1) & 3;
            vdp_.set_sprite_size16(mode_ >= 2);
            vdp_.set_sprite_mag((mode_ % 2) == 1);
        }
        int size = vdp_.get_sprite_size16() ? 16 : 8;
        size = vdp_.get_sprite_mag() ? size * 2 : size;

        if (frame % 180 == 0) {
            for (int i = 0; i < kBounceCount; i++) {
                Sprite& s = sprites_[i];
                if (s.x >= V9938::SCREEN_WIDTH - size) s.x = V9938::SCREEN_WIDTH - size - 1;
                if (s.y >= V9938::SCREEN_HEIGHT - size) s.y = V9938::SCREEN_HEIGHT - size - 1;
                s.pattern = vdp_.get_sprite_size16() ? ((i % 2) + 1) * 4 : (i % 2);
            }
        }

        int venn_pattern = vdp_.get_sprite_size16() ? 8 : 2;
        double radius = 4.0 + 4.0 * std::sin(frame * 0.02);
        for (auto& v : venn_) {
            double angle = v.phase + frame * 0.03;
            double vx = venn_center_x_ + radius * std::cos(angle);
            double vy = venn_center_y_ + radius * std::sin(angle);
            vdp_.set_sprite(v.index, static_cast<int>(vx), static_cast<int>(vy), venn_pattern, v.color);
        }

        for (int i = 0; i < kBounceCount; i++) {
            Sprite& s = sprites_[i];
            s.x += s.dx;
            s.y += s.dy;
            if (!(s.x > 0 && s.x < V9938::SCREEN_WIDTH - size)) s.dx = -s.dx;
            if (!(s.y > 0 && s.y < V9938::SCREEN_HEIGHT - size)) s.dy = -s.dy;
            vdp_.set_sprite(i, static_cast<int>(s.x), static_cast<int>(s.y), s.pattern, s.color);
        }
    }

private:
    struct Sprite {
        double x = 0;
        double y = 0;
        int pattern = 0;
        int color = 0;
        double dx = 0;
        double dy = 0;
    };

    struct Venn {
        int index = 0;
        double phase = 0;
        int color = 0;
    };

    static std::array<uint8_t, 8> fill8(uint8_t value) {
        std::array<uint8_t, 8> a;
        a.fill(value);
        return a;
    }

    V9938& vdp_;
    std::array<Sprite, kBounceCount> sprites_{};
    std::array<Venn, 3> venn_{};
    const double venn_center_x_ = 24;
    const double venn_center_y_ = 20;
    int mode_ = 0;
};

}  // namespace

int main() {
    std::srand(static_cast<unsigned>(std::time(nullptr)));

    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        SDL_Log("SDL_Init failed: %s", SDL_GetError());
        return 1;
    }

    SDL_Window* window = SDL_CreateWindow(
        "V9938 Sprite Emulator",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        V9938::SCREEN_WIDTH * kScale, V9938::SCREEN_HEIGHT * kScale,
        SDL_WINDOW_SHOWN);
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    SDL_Texture* texture = SDL_CreateTexture(
        renderer, SDL_PIXELFORMAT_RGB888, SDL_TEXTUREACCESS_STREAMING,
        V9938::SCREEN_WIDTH, V9938::SCREEN_HEIGHT);

    V9938 vdp;
    ROM rom(vdp);
    rom.init();

    std::vector<uint32_t> framebuffer(V9938::SCREEN_WIDTH * V9938::SCREEN_HEIGHT);

    int frame = 0;
    bool running = true;
    while (running) {
        Uint32 frame_start = SDL_GetTicks();

        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) running = false;
        }

        rom.run(frame);
        vdp.render_sprite2(framebuffer.data());
        if (vdp.get_collision()) {
            std::printf("SPRITE COLLISION\n");
        }
        if (vdp.get_5s()) {
            std::printf("SPRITE OVERFLOW: 9th sprite=%d\n", vdp.get_5s_index());
        }

        SDL_UpdateTexture(texture, nullptr, framebuffer.data(),
                           V9938::SCREEN_WIDTH * static_cast<int>(sizeof(uint32_t)));
        SDL_RenderClear(renderer);
        SDL_RenderCopy(renderer, texture, nullptr, nullptr);
        SDL_RenderPresent(renderer);

        frame++;

        constexpr Uint32 kFrameDelayMs = 1000 / 60;
        Uint32 elapsed = SDL_GetTicks() - frame_start;
        if (elapsed < kFrameDelayMs) SDL_Delay(kFrameDelayMs - elapsed);
    }

    SDL_DestroyTexture(texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
