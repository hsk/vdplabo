// ----------------------------------------
// V9918 / TMS9918A Sprite emulator (SDL2)
// ----------------------------------------
// stage1.hpp の V9918 クラスを読み込んで動かすだけの薄いドライバ。
// ROM クラスが python 版の ROM クラスと同じ内容(32個のスプライトを
// 跳ね回らせつつ、8x8/16x16・等倍/拡大を順番に切り替える)を再現する。
#include "stage1.hpp"

#include <SDL.h>

#include <array>
#include <cstdlib>
#include <ctime>
#include <vector>

namespace {

constexpr int kScale = 3;

double random_range(double lo, double hi) {
    return lo + (hi - lo) * (std::rand() / static_cast<double>(RAND_MAX));
}

class ROM {
public:
    explicit ROM(V9918& vdp) : vdp_(vdp) {}

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
        // 16x16 sprite patterns
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
        // Another 16x16 sprite pattern
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

        for (int i = 0; i < kSpriteCount; i++) {
            Sprite& s = sprites_[i];
            s.x = 16 + i * 6;
            s.y = 40 + (i % 2) * 40;
            s.color = (i % 14) + 2;
            s.dx = random_range(-2.0, 2.0);
            s.dy = random_range(-2.0, 2.0);
        }
        mode_ = 3;
    }

    void run(int frame) {
        if (frame % 180 == 0) {
            mode_ = (mode_ + 1) & 3;
            vdp_.sprite_size16 = mode_ >= 2;
            vdp_.sprite_mag = (mode_ % 2) == 1;
        }
        int size = vdp_.sprite_size16 ? 16 : 8;
        size = vdp_.sprite_mag ? size * 2 : size;

        if (frame % 180 == 0) {
            for (int i = 0; i < kSpriteCount; i++) {
                Sprite& s = sprites_[i];
                if (s.x >= V9918::SCREEN_WIDTH - size) s.x = V9918::SCREEN_WIDTH - size - 1;
                if (s.y >= V9918::SCREEN_HEIGHT - size) s.y = V9918::SCREEN_HEIGHT - size - 1;
                s.pattern = vdp_.sprite_size16 ? ((i % 2) + 1) * 4 : (i % 2);
            }
        }
        for (int i = 0; i < kSpriteCount; i++) {
            Sprite& s = sprites_[i];
            s.x += s.dx;
            s.y += s.dy;
            if (!(s.x > 0 && s.x < V9918::SCREEN_WIDTH - size)) s.dx = -s.dx;
            if (!(s.y > 0 && s.y < V9918::SCREEN_HEIGHT - size)) s.dy = -s.dy;
            vdp_.set_sprite(i, static_cast<int>(s.x), static_cast<int>(s.y), s.pattern, s.color);
        }
    }

private:
    static constexpr int kSpriteCount = V9918::SPRITE_COUNT;

    struct Sprite {
        double x = 0;
        double y = 0;
        int pattern = 0;
        int color = 0;
        double dx = 0;
        double dy = 0;
    };

    V9918& vdp_;
    std::array<Sprite, kSpriteCount> sprites_{};
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
        "V9918 Sprite Emulator",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        V9918::SCREEN_WIDTH * kScale, V9918::SCREEN_HEIGHT * kScale,
        SDL_WINDOW_SHOWN);
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    SDL_Texture* texture = SDL_CreateTexture(
        renderer, SDL_PIXELFORMAT_RGB888, SDL_TEXTUREACCESS_STREAMING,
        V9918::SCREEN_WIDTH, V9918::SCREEN_HEIGHT);

    V9918 vdp;
    ROM rom(vdp);
    rom.init();

    std::vector<uint32_t> framebuffer(V9918::SCREEN_WIDTH * V9918::SCREEN_HEIGHT);

    int frame = 0;
    bool running = true;
    while (running) {
        Uint32 frame_start = SDL_GetTicks();

        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) running = false;
        }

        rom.run(frame);
        vdp.render_sprite1(framebuffer.data());

        SDL_UpdateTexture(texture, nullptr, framebuffer.data(),
                           V9918::SCREEN_WIDTH * static_cast<int>(sizeof(uint32_t)));
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
