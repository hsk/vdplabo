# ----------------------------------------
# V9918 / TMS9918A Multicolor mode emulator (Fixed)
# ----------------------------------------
import pygame
import sys
import random

class V9918:
    SCREEN_WIDTH  = 256
    SCREEN_HEIGHT = 192
    COLS = 32
    ROWS_MC = 6
    PATTERN_COUNT = 256
    PALETTE = [
        (0, 0, 0),         # 0 Transparent / black
        (0, 0, 0),         # 1 Black
        (33, 200, 66),     # 2 Medium green
        (94, 220, 120),    # 3 Light green
        (84, 85, 237),     # 4 Dark blue
        (125, 118, 252),   # 5 Light blue
        (212, 82, 77),     # 6 Dark red
        (66, 235, 245),    # 7 Cyan
        (252, 85, 84),     # 8 Medium red
        (255, 121, 120),   # 9 Light red
        (212, 193, 84),    # 10 Dark yellow
        (230, 206, 128),   # 11 Light yellow
        (33, 176, 59),     # 12 Dark green
        (201, 91, 186),    # 13 Magenta
        (204, 204, 204),   # 14 Gray
        (255, 255, 255),   # 15 White
    ]
    def __init__(self):
        self.name_table = [0] * (self.COLS * self.ROWS_MC)
        self.pattern_table = [[0] * 8 for _ in range(self.PATTERN_COUNT)]
    def set_pixel(self, x, y, col):
        cy = y // 8
        cx = x // 2
        pattern = self.pattern_table[cy*32+cx]
        px = x & 1
        py = y & 7
        if px == 0:
            pattern[py] = col | (pattern[py] & 0xF0)
        else:
            pattern[py] = (col << 4) | (pattern[py] & 0x0F)
    def set_pattern(self, ch, data):
        for i in range(8):
            self.pattern_table[ch][i] = data[i]
    def render_mc(self, surface):
        for cy in range(self.ROWS_MC):
            for cx in range(self.COLS):
                ptn_no = self.name_table[cy * self.COLS + cx]
                pattern = self.pattern_table[ptn_no]
                x = cx * 8
                y = cy * 8 * 4
                for py in range(8):
                    bits = pattern[py]
                    pygame.draw.rect(surface, self.PALETTE[bits&0xf], (x,y+py*4,4,4))
                    pygame.draw.rect(surface, self.PALETTE[(bits>>4)&0xf], (x+4,y+py*4,4,4))
if __name__ == "__main__":
    vdp = V9918()
    def machine(rom):
        rom.init()
        pygame.init()
        SCALE = 3
        window = pygame.display.set_mode(
            (vdp.SCREEN_WIDTH * SCALE, vdp.SCREEN_HEIGHT * SCALE)
        )
        pygame.display.set_caption("V9918 Multicolor Mode Emulator (4x4 Pixel Fixed)")
        screen = pygame.Surface((vdp.SCREEN_WIDTH, vdp.SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        frame = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            rom.run(frame)
            vdp.render_mc(screen)
            scaled = pygame.transform.scale(
                screen,
                (vdp.SCREEN_WIDTH * SCALE, vdp.SCREEN_HEIGHT * SCALE)
            )
            window.blit(scaled, (0, 0))
            pygame.display.flip()
            frame += 1
            clock.tick(60)
    class ROM:
        def init(self):
            for i in range(32*6):
                vdp.name_table[i] = i
            self.clear()
        def clear(self):
            for i in range(32*6):
                vdp.set_pattern(i, [
                    0x00,
                    0x00,
                    0x00,
                    0x00,
                    0x00,
                    0x00,
                    0x00,
                    0x00,
                ])
        def fillRect(self,x,y,w,h,col):
            for yy in range(y,y+h):
                for xx in range(x,x+w):
                    vdp.set_pixel(xx,yy,col)
        def run(self,frame):
            x = frame % 64
            y = (frame // 64) % 48
            vdp.set_pixel(x,y,0xf)
            x = random.randint(0,63)
            y = random.randint(0,47)
            w = random.randint(x+1,64)-x
            h = random.randint(y+1,48)-y
            self.fillRect(x,y,w,h,random.randint(2,14))
    machine(ROM())
