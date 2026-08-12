// SDL2 Fixed-Point Keyframe Animation Sample (C++)
// build:
// g++ keyframe.cpp `sdl2-config --cflags --libs` && ./a.out
#include <SDL.h>
#include <array>
#include <vector>
#include <cstdint>

constexpr int SCREEN_W=256;
constexpr int SCREEN_H=192;
constexpr int FP_SHIFT=7;

using fixed=int16_t;

static inline fixed int_to_fp(int v){ return (v-24)<<FP_SHIFT; }
static inline int fp_to_int(fixed v){ return (v>>FP_SHIFT)+24; }
static inline fixed lerp_fp(fixed a,fixed b,uint8_t t){ return a+(((b-a)*t)>>8); }

struct Keyframe {
    uint16_t frame=0;
    fixed x=0;
    fixed y=0;
};

const uint16_t LOGO_DATA[6][16] = {
    {
        0b0111111111111000,
        0b1111111111111110,
        0b1100000000011110,
        0b1101111111110111,
        0b1101000000011101,
        0b1101000000001101,
        0b1101000000011101,
        0b1101011111111010,
        0b1101111111110010,
        0b1101111110001100,
        0b1101101111110000,
        0b1101011011111000,
        0b1101001110111110,
        0b1101000011101101,
        0b1001000000111001,
        0b0110000000001110
    },
    {
        0b0000000000000000,
        0b0000000000000000,
        0b0000000000000000,
        0b0000000000000000,
        0b0000000110000000,
        0b0000011111100000,
        0b0000011111100000,
        0b0000111100010000,
        0b0000111011010000,
        0b0000011010100000,
        0b0000011001100000,
        0b0000000110000000,
        0b0000000000000000,
        0b0000000000000000,
        0b0000000000000000,
        0b0000000000000000
    },
    {
        0b0111111111111110,
        0b1111111111111101,
        0b1000001100000001,
        0b0111111101111110,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001001000000,
        0b0000000110000000,
    },
    {
        0b0110000000000110,
        0b1111000000001101,
        0b1111100000011101,
        0b0101110000111010,
        0b0010111001110100,
        0b0001011111101000,
        0b0000101111010000,
        0b0000011110100000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001101000000,
        0b0000001001000000,
        0b0000000110000000
    },
    {
        0b0111111111111000,
        0b1111111111111110,
        0b1100000000011010,
        0b1101111111101101,
        0b1101000000011101,
        0b1101000000001101,
        0b1101000000011101,
        0b1111111111111010,
        0b1111111111110010,
        0b1100000000001100,
        0b1101111111110000,
        0b1101000000000000,
        0b1101000000000000,
        0b1101000000000000,
        0b1001000000000000,
        0b0110000000000000
    },
    {
        0b0111111111111110,
        0b1111111111111101,
        0b1100000000000001,
        0b1101111111111110,
        0b1101000000000000,
        0b1101000000000000,
        0b1111111111100000,
        0b1111111111010000,
        0b1100000000010000,
        0b1101111111100000,
        0b1101000000000000,
        0b1101000000000000,
        0b1111111111111110,
        0b1111111111111101,
        0b1000000000000001,
        0b0111111111111110,
    }
};

struct Animation {
    SDL_Texture* texture=nullptr;
    std::vector<Keyframe> keys;
    fixed x=0;
    fixed y=0;
    bool finished=false;
    Animation(SDL_Renderer* renderer,uint8_t i,uint8_t r,uint8_t g,uint8_t b) {
        SDL_Surface* surf=SDL_CreateRGBSurface(0,16,16,32,0,0,0,0);
        uint32_t bg=SDL_MapRGBA(surf->format,0,0,0,0);
        uint32_t fg=SDL_MapRGB(surf->format,r,g,b);
        SDL_FillRect(surf,nullptr,bg);
        SDL_LockSurface(surf);
        uint32_t* pixels=(uint32_t*)surf->pixels;
        for(int y=0;y<16;y++){
            uint16_t line=LOGO_DATA[i][y];
            for(int x=0;x<16;x++)
                if(line&(0x8000>>x))
                    pixels[y*16+x]=fg;
        }
        SDL_UnlockSurface(surf);
        SDL_SetColorKey(surf,SDL_TRUE,bg);
        texture=SDL_CreateTextureFromSurface(renderer,surf);
        SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_BLEND);
        SDL_FreeSurface(surf);
    }
    Animation& addKey(const Keyframe &k){
        keys.push_back(k);
        return *this;
    }
    void update(uint16_t frame){
        if(keys.size()<2) return;
        for(size_t i=0;i<keys.size()-1;i++) {
            Keyframe& k0=keys[i];
            Keyframe& k1=keys[i+1];
            if(frame==k1.frame){
                x=k1.x;
                y=k1.y;
                return;
            }
            if(k0.frame<=frame && frame<k1.frame) {
                uint16_t span=k1.frame-k0.frame;
                uint16_t local=frame-k0.frame;
                uint8_t t=(local<<8)/span;
                x=lerp_fp(k0.x,k1.x,t);
                y=lerp_fp(k0.y,k1.y,t);
                return;
            }
        }
        Keyframe& last=keys.back();
        x=last.x;
        y=last.y;
        finished=true;
    }
    void draw(SDL_Renderer* renderer) const {
        SDL_Rect dst={fp_to_int(x),fp_to_int(y),32,32};
        SDL_RenderCopy(renderer,texture,nullptr,&dst);
    }
    void destroy(){
        if(texture)
            SDL_DestroyTexture(texture);
        texture=nullptr;
    }
};

class App {
public:
    SDL_Window* window=nullptr;
    SDL_Renderer* renderer=nullptr;
    std::vector<Animation> anims;
    bool running=true;
    uint16_t frame=0;
    bool init(){
        if(SDL_Init(SDL_INIT_VIDEO)!=0)
            return false;
        window=SDL_CreateWindow(
            "Keyframe Animation",
            SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED,
            SCREEN_W,SCREEN_H,
            0);
        renderer=SDL_CreateRenderer(
            window,
            -1,
            SDL_RENDERER_ACCELERATED|SDL_RENDERER_PRESENTVSYNC);
        return renderer!=nullptr;
    }
    void setup(){
        int x = 24;
        int x2 = x;
        for (int i=0;i<6;i++) {
            int w = 32+8;
            anims.push_back(Animation(renderer,i,80,160,255)
                .addKey({0,int_to_fp(256),int_to_fp(10)})
                .addKey({30,int_to_fp(x),int_to_fp(10)})
                .addKey({60,int_to_fp(x2),int_to_fp(10)})
                .addKey({120,int_to_fp(x2),int_to_fp(100)})
            );
            if (i <= 1) w = 20+8;
            x2 += w;
        }
    }
    void update(){
        for(auto& anim:anims)
            if(anim.texture)
                anim.update(frame);
    }
    void draw(){
        SDL_SetRenderDrawColor(renderer,0,0,0,255);
        SDL_RenderClear(renderer);
        for(const auto& anim:anims)
            if(anim.texture) anim.draw(renderer);
        SDL_RenderPresent(renderer);
    }
    void loop(){
        while(running){
            SDL_Event e;
            while(SDL_PollEvent(&e))
                if(e.type==SDL_QUIT) running=false;
            update();
            draw();
            frame++;
        }
    }
    void shutdown(){
        for(auto& anim:anims) anim.destroy();
        SDL_DestroyRenderer(renderer);
        SDL_DestroyWindow(window);
        SDL_Quit();
    }
};

int main(int argc,char** argv){
    App app;
    if(!app.init()) return 1;
    app.setup();
    app.loop();
    app.shutdown();
    return 0;
}
