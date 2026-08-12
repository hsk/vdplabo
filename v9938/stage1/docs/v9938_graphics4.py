# ----------------------------------------
# V9938 SCREEN 5 / Graphics 4 emulator
# ----------------------------------------
import pygame
import sys
import random
class V9938:
    SCREEN_WIDTH  = 256
    SCREEN_HEIGHT = 192
    def __init__(self):
        # SCREEN5 VRAM
        # 256x192
        # 4bit packed pixels
        # 2 pixels per byte
        self.vram = bytearray((self.SCREEN_WIDTH * self.SCREEN_HEIGHT) // 2)
        # V9938 palette
        # 16 colors from 3bit RGB (0-7)
        self.palette = [(0,0,0)] * 16
    def set_palette(self, index, r, g, b):
        # Convert 3bit RGB to 0-255
        rr = int((r / 7.0) * 255)
        gg = int((g / 7.0) * 255)
        bb = int((b / 7.0) * 255)
        self.palette[index & 15] = (rr, gg, bb)
    def pset(self, x, y, color):
        if not (0 <= x < self.SCREEN_WIDTH):
            return
        if not (0 <= y < self.SCREEN_HEIGHT):
            return
        addr = y * (self.SCREEN_WIDTH // 2) + (x // 2)
        old = self.vram[addr]
        if (x & 1) == 0:
            old &= 0x0F
            old |= (color & 0x0F) << 4
        else:
            old &= 0xF0
            old |= color & 0x0F
        self.vram[addr] = old
    def render_screen5(self, surface):
        addr = 0
        for y in range(self.SCREEN_HEIGHT):
            for x in range(0, self.SCREEN_WIDTH, 2):
                value = self.vram[addr]
                addr += 1
                left  = (value >> 4) & 0x0F
                right = value & 0x0F
                surface.set_at((x + 0, y), self.palette[left])
                surface.set_at((x + 1, y), self.palette[right])
if __name__ == "__main__":
    vdp = V9938()
    def machine(rom):
        rom.init()
        pygame.init()
        SCALE = 3
        window = pygame.display.set_mode(
            (vdp.SCREEN_WIDTH * SCALE, vdp.SCREEN_HEIGHT * SCALE)
        )
        pygame.display.set_caption("V9938 SCREEN 5 Emulator")
        screen = pygame.Surface((vdp.SCREEN_WIDTH, vdp.SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        frame = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            rom.run(frame)
            vdp.render_screen5(screen)
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
            # V9938 3bit RGB palette
            vdp.set_palette(0, 0,0,0)
            vdp.set_palette(1, 0,0,7)
            vdp.set_palette(2, 0,7,0)
            vdp.set_palette(3, 0,7,7)
            vdp.set_palette(4, 7,0,0)
            vdp.set_palette(5, 7,0,7)
            vdp.set_palette(6, 7,3,0)
            vdp.set_palette(7, 7,7,7)
            vdp.set_palette(8, 3,3,3)
            vdp.set_palette(9, 3,3,7)
            vdp.set_palette(10, 3,7,3)
            vdp.set_palette(11, 3,7,7)
            vdp.set_palette(12, 7,3,3)
            vdp.set_palette(13, 7,3,7)
            vdp.set_palette(14, 7,7,3)
            vdp.set_palette(15, 7,7,7)
        def run(self,frame):
                # Simple VRAM animation
                for y in range(vdp.SCREEN_HEIGHT):
                    c = (((y-frame) // 12)) & 15
                    for x in range(vdp.SCREEN_WIDTH):
                        if y < 16 or vdp.SCREEN_HEIGHT-16 <= y:
                            c = random.randint(0,15)
                        vdp.pset(x, y, (c + (x // 32)) & 15)
    machine(ROM())
