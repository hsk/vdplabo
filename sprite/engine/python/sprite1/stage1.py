# ----------------------------------------
# V9918 / TMS9918A Sprite emulator
# ----------------------------------------
import pygame
import sys
import random
class V9918:
    SCREEN_WIDTH  = 256
    SCREEN_HEIGHT = 192
    SPRITE_COUNT = 32
    SPRITE_PATTERN_COUNT = 256
    # openMSX(C-BIOS MSX2, SDLGL-PPレンダラ)で実際に描画された色を
    # sprite/test/asm/probe_palette.asm で実測した値。データシート値の
    # 近似ではなく実機(openMSX)の出力に合わせている。
    PALETTE = [
        (0, 0, 0),         # 0 Transparent
        (0, 0, 0),         # 1 Black
        (43, 221, 43),     # 2 Medium green
        (118, 255, 118),   # 3 Light green
        (43, 43, 255),     # 4 Dark blue
        (81, 118, 255),    # 5 Light blue
        (187, 43, 43),     # 6 Dark red
        (81, 221, 255),    # 7 Cyan
        (255, 43, 43),     # 8 Medium red
        (255, 118, 118),   # 9 Light red
        (221, 221, 43),    # 10 Dark yellow
        (221, 221, 153),   # 11 Light yellow
        (43, 153, 43),     # 12 Dark green
        (221, 81, 187),    # 13 Magenta
        (187, 187, 187),   # 14 Gray
        (255, 255, 255),   # 15 White
    ]
    def __init__(self):
        # Sprite attribute table
        self.sprites = []
        for i in range(self.SPRITE_COUNT):
            self.sprites.append({
                "x": 0,
                "y": 0,
                "pattern": 0,
                "color": 0
            })
        self.sprite_patterns = [[0] * 8 for _ in range(self.SPRITE_PATTERN_COUNT)]
        self.sprite_mag = False
        self.sprite_size16 = False
    def set_sprite_pattern(self, ch, data):
        for i in range(8):
            self.sprite_patterns[ch][i] = data[i]
    def set_sprite_pattern16x16(self, ch, data):
        base = ch & 0xFC
        p = [[],[],[],[]]
        for y in range(16):
            row = data[y]
            p[0+(y//8)*2].append((row >> 8) & 0xFF)
            p[1+(y//8)*2].append(row & 0xFF)
        for i in range(4):
            self.set_sprite_pattern(base + i, p[i])
    def set_sprite(self, no, x, y, pattern, color):
        self.sprites[no]["x"] = x
        self.sprites[no]["y"] = y
        self.sprites[no]["pattern"] = pattern
        self.sprites[no]["color"] = color
    def render(self, surface):
        self._surface = surface
        surface.fill(self.PALETTE[4])  # BIOSデフォルト(BAKCLR=4, 青)。stage1は背景色レジスタ未対応。
        for spr in reversed(self.sprites):
            color = self.PALETTE[spr["color"]]
            blocks = [(0, 0, spr["pattern"])]
            if self.sprite_size16:
                spr_ptn = spr["pattern"] & 0xFC
                blocks = [
                    (0, 0, spr_ptn + 0),
                    (8, 0, spr_ptn + 1),
                    (0, 8, spr_ptn + 2),
                    (8, 8, spr_ptn + 3),
                ]
            for bx, by, pat_no in blocks:
                pattern = self.sprite_patterns[pat_no]
                for py in range(8):
                    bits = pattern[py]
                    for px in range(8):
                        if bits & (0x80 >> px):
                            if self.sprite_mag:
                                x = spr["x"] + (bx + px) * 2
                                y = spr["y"] + (by + py) * 2
                                for oy in range(2):
                                    for ox in range(2):
                                        sx = x + ox
                                        sy = y + oy
                                        if 0 <= sx < self.SCREEN_WIDTH and 0 <= sy < self.SCREEN_HEIGHT:
                                            surface.set_at((sx, sy), color)
                            else:
                                x = spr["x"] + bx + px
                                y = spr["y"] + by + py
                                if 0 <= x < self.SCREEN_WIDTH and 0 <= y < self.SCREEN_HEIGHT:
                                    surface.set_at((x, y), color)
    def get_at(self, x, y):
        """直前のrender()で使われたsurfaceの(x, y)のRGB値を返す。"""
        return self._surface.get_at((x, y))[:3]
if __name__ == "__main__":
    vdp = V9918()
    def machine(rom):
        rom.init()
        pygame.init()
        SCALE = 3
        window = pygame.display.set_mode(
            (vdp.SCREEN_WIDTH * SCALE, vdp.SCREEN_HEIGHT * SCALE)
        )
        pygame.display.set_caption("V9918 Sprite Emulator")
        screen = pygame.Surface((vdp.SCREEN_WIDTH, vdp.SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        frame = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            rom.run(frame)
            vdp.render(screen)
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
            # Sprite 0 pattern
            vdp.set_sprite_pattern(0, [
                0b00111100,
                0b01111110,
                0b11111111,
                0b11011011,
                0b11111111,
                0b01111110,
                0b00111100,
                0b00011000,
            ])
            # Sprite 1 pattern
            vdp.set_sprite_pattern(1, [
                0b00011000,
                0b00111100,
                0b01111110,
                0b11111111,
                0b01111110,
                0b00111100,
                0b00011000,
                0b00000000,
            ])
            # 16x16 sprite patterns
            vdp.set_sprite_pattern16x16(4,[
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
            ])
            # Another 16x16 sprite pattern
            vdp.set_sprite_pattern16x16(8,[
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
            ])
            self.sps = [{} for _ in range(32)]
            # Create sprites
            for i,s in enumerate(self.sps):
                s["x"] = 16 + i * 6
                s["y"] = 40 + (i % 2) * 40
                s["color"] = (i % 14) + 2
                s["dx"] = random.randint(-20,20)/10.0
                s["dy"] = random.randint(-20,20)/10.0
            self.mode = 3
        def run(self,frame):
            if frame % 180 == 0:
                self.mode = (self.mode + 1) & 3
                vdp.sprite_size16 = self.mode >= 2
                vdp.sprite_mag = (self.mode % 2) == 1
            size = 16 if vdp.sprite_size16 else 8
            size = size * 2 if vdp.sprite_mag else size
            if frame % 180 == 0:
                for i, s in enumerate(self.sps):
                    if s["x"] >= 256 - size: s["x"] = 256 - size - 1
                    if s["y"] >= 192 - size: s["y"] = 192 - size - 1
                    if vdp.sprite_size16:
                        s["pattern"] = ((i % 2) + 1) * 4
                    else:
                        s["pattern"] = i % 2
            for i, s in enumerate(self.sps):
                s["x"] += s["dx"]
                s["y"] += s["dy"]
                if not (0 < s["x"] < 256 - size): s["dx"] = -s["dx"]
                if not (0 < s["y"] < 192 - size): s["dy"] = -s["dy"]
                vdp.set_sprite(i, int(s["x"]), int(s["y"]), s["pattern"], s["color"])
    machine(ROM())
