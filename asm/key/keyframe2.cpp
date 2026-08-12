// SDL2 Fixed-Point Keyframe Animation Sample (C++)
// build:
// g++ keyframe.cpp `sdl2-config --cflags --libs` && ./a.out
#include <SDL.h>
#include <array>
#include <vector>
#include <cstdint>

#define SCREEN_W 256
#define SCREEN_H 192
#define FP_SHIFT 7
#define fixed int16_t
#define int_to_fp(v) (fixed)(((v)-24)<<FP_SHIFT)
#define fp_to_int(v) (int)(((v)>>FP_SHIFT)+24)
#define lerp_fp(a,b,t) ((a)+((((b)-(a))*(t))>>8))

typedef struct Keyframe {
    uint16_t frame;
    fixed x;
    fixed y;
} Keyframe;

typedef struct Animation {
    SDL_Texture* texture;
    Keyframe keys[4];
    fixed x;
    fixed y;
    bool finished;
} Animation;

typedef struct App {
    SDL_Window* window;
    SDL_Renderer* renderer;
    Animation anims[6];
    bool running;
    uint16_t frame;
} App;

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

SDL_Texture* new_logo(SDL_Renderer* renderer,uint8_t i,uint8_t r,uint8_t g,uint8_t b) {
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
    SDL_Texture* texture=SDL_CreateTextureFromSurface(renderer,surf);
    SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_BLEND);
    SDL_FreeSurface(surf);
    return texture;
}

void anim_update(Animation* anim, uint16_t frame){
    for(size_t i=0;i<4-1;i++) {
        Keyframe* k0=&anim->keys[i];
        Keyframe* k1=&anim->keys[i+1];
        if(frame==k1->frame){
            anim->x=k1->x;
            anim->y=k1->y;
            return;
        }
        if(k0->frame<=frame && frame<k1->frame) {
            uint16_t span=k1->frame-k0->frame;
            uint16_t local=frame-k0->frame;
            uint8_t t=(local<<8)/span;
            anim->x=lerp_fp(k0->x,k1->x,t);
            anim->y=lerp_fp(k0->y,k1->y,t);
            return;
        }
    }
    Keyframe* last=&anim->keys[3];
    anim->x=last->x;
    anim->y=last->y;
    anim->finished=true;
}
void anim_draw(Animation* anim, SDL_Renderer* renderer) {
    SDL_Rect dst={fp_to_int(anim->x),fp_to_int(anim->y),32,32};
    SDL_RenderCopy(renderer,anim->texture,nullptr,&dst);
}
void anim_destroy(Animation* anim){
    if(anim->texture)
    SDL_DestroyTexture(anim->texture);
    anim->texture=nullptr;
}

bool app_init(App* app) {
    if(SDL_Init(SDL_INIT_VIDEO)!=0)
        return false;
    app->window=SDL_CreateWindow(
        "Keyframe Animation",
        SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED,
        SCREEN_W,SCREEN_H,
        0);
    app->renderer=SDL_CreateRenderer(
        app->window,
        -1,
        SDL_RENDERER_ACCELERATED|SDL_RENDERER_PRESENTVSYNC);
    return app->renderer!=nullptr;
}
void app_setup(App* app){
    int x = 24;
    int x2 = x;
    for (int i=0;i<6;i++) {
        int w = 40;
        app->anims[i].finished=false;
        app->anims[i].texture = new_logo(app->renderer,i,80,160,255);
        app->anims[i].keys[0]={0, int_to_fp(256),int_to_fp( 24)};
        app->anims[i].keys[1]={30,int_to_fp(  x),int_to_fp( 24)};
        app->anims[i].keys[2]={60,int_to_fp( x2),int_to_fp( 24)};
        app->anims[i].keys[3]={90,int_to_fp( x2),int_to_fp(100)};
        if (i <= 1) w = 28;
        x2 += w;
    }
}
void app_update(App* app){
    for (int i=0;i<6;i++)
        if(app->anims[i].texture)
            anim_update(&app->anims[i], app->frame);
}
void app_draw(App* app){
    SDL_SetRenderDrawColor(app->renderer,0,0,0,255);
    SDL_RenderClear(app->renderer);
    for(int i=0;i<6;i++) anim_draw(&app->anims[i], app->renderer);
    SDL_RenderPresent(app->renderer);
}
void app_loop(App* app){
    app->running=true;
    app->frame=0;
    while(app->running){
        SDL_Event e;
        while(SDL_PollEvent(&e))
            if(e.type==SDL_QUIT) app->running=false;
        app_update(app);
        app_draw(app);
        app->frame++;
    }
}
void app_shutdown(App* app){
    for(int i=0;i<6;i++) anim_destroy(&app->anims[i]);
    SDL_DestroyRenderer(app->renderer);
    SDL_DestroyWindow(app->window);
    SDL_Quit();
}
int main(int argc,char** argv){
    App app;
    if(!app_init(&app)) return 1;
    app_setup(&app);
    app_loop(&app);
    app_shutdown(&app);
    return 0;
}
