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
        self.vram = bytearray(16 * 1024)
        self.reg = bytearray(8)
        self.stat = bytearray(1)
        self.set_sprite_pattern_table(0x1b00)
        self.set_sprite_attribute_table(0x3800)
        # Global sprite mode flags
        self.set_sprite_mag(False)
        self.set_sprite_size16(False)
        self.set_5s(False)
        self.set_5s_index(0)
        self.set_collision(False)
    def set_sprite_pattern_table(self, addr):
        self.reg[6] = (addr >> 11) & 3
    def get_sprite_pattern_table(self):
        return (self.reg[6] & 3) << 11
    def set_sprite_attribute_table(self, addr):
        self.reg[5] = (addr >> 7) & 63
    def get_sprite_attribute_table(self):
        return (self.reg[6] & 63) << 7
    def set_sprite_mag(self, value):
        self.reg[1] &= ~1
        self.reg[1] |= 1 if value else 0
    def get_sprite_mag(self):
        return (self.reg[1] & 1) != 0
    def set_sprite_size16(self, value):
        self.reg[1] &= ~2
        self.reg[1] |= 2 if value else 0
    def get_sprite_size16(self):
        return (self.reg[1] & 2) != 0
    def set_collision(self, value):
        self.stat[0] &= ~(1<<5)
        self.stat[0] |= (1<<5) if value else 0
    def get_collision(self):
        return (self.stat[0] & (1<<5)) != 0
    def set_5s(self, value):
        self.stat[0] &= ~(1<<6)
        self.stat[0] |= (1<<6) if value else 0
    def get_5s(self):
        return (self.stat[0] & (1<<6)) != 0
    def set_5s_index(self, value):
        self.stat[0] &= ~(31)
        self.stat[0] |= value & 31
    def get_5s_index(self):
        return self.stat[0] & 31
    def set_sprite_pattern(self, ch, data):
        addr = self.get_sprite_pattern_table() + ch * 8
        for i in range(8):
            self.vram[addr] = data[i]
            addr += 1
    def set_sprite_pattern16x16(self, ch, data):
        base = ch & 0xFC
        p = [[],[],[],[]]
        for y in range(16):
            row = data[y]
            p[0+(y//8)*2].append((row >> 8) & 0xFF)
            p[1+(y//8)*2].append(row & 0xFF)
        for i in range(4):
            self.set_sprite_pattern(base + i, p[i])
    def set_sprite(self, no, x, y, pattern, color, ec = False):
        addr = self.get_sprite_attribute_table() + no * 4
        self.vram[addr + 0] = y & 0xff
        self.vram[addr + 1] = x & 0xff
        self.vram[addr + 2] = pattern & 0xff
        self.vram[addr + 3] = (color | (128 if ec else 0)) & 0xff
    def render_sprite1(self, surface):
        surface.fill((0, 0, 0))
        self.set_5s(False)
        self.set_5s_index(0)
        for y in range(self.SCREEN_HEIGHT):
            self.render_line_sprites(surface, y)
    def render_line_sprites(self, surface, y):
        sprites_on_line = 0
        draw_log = [0] * self.SCREEN_WIDTH
        attr_addr = self.get_sprite_attribute_table()
        for i in range(32):
            spr_y = self.vram[attr_addr + 0]
            x = self.vram[attr_addr + 1]
            spr_ptn = self.vram[attr_addr + 2]
            color_byte = self.vram[attr_addr + 3]
            attr_addr += 4
            if spr_y == 208: return
            spr_y = (spr_y + 1) & 255
            color_index = color_byte & 0x0F
            if color_index == 0: continue
            color = self.PALETTE[color_index]
            if color_byte & 0x80: x -= 32
            size = 16 if self.get_sprite_size16() else 8
            mag = 2 if self.get_sprite_mag() else 1
            size = size * mag
            if not (spr_y <= y < spr_y + size): continue
            sprites_on_line += 1
            if sprites_on_line > 4:
                self.set_5s(True)
                self.set_5s_index(i)
                return
            py = y - spr_y
            if mag == 2: py >>= 1
            if self.get_sprite_size16():
                spr_ptn = spr_ptn & 0xFC
                if py >= 8:
                    spr_ptn += 2
                    py -= 8
                blocks = [spr_ptn, spr_ptn + 1]
            else:
                blocks = [spr_ptn]
            for pat_no in blocks:
                bits = self.vram[self.get_sprite_pattern_table() + (pat_no * 8) + py]
                for px in range(8):
                    for _ in range(mag):
                        if 0 <= x < self.SCREEN_WIDTH and bits & (0x80 >> px):
                            if draw_log[x] == 0:
                                draw_log[x] = color_index
                                surface.set_at((x, y), color)
                            else:
                                self.set_collision(True)
                        x += 1
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
            vdp.render_sprite1(screen)
            # Debug output for sprite status
            if vdp.get_collision():
                print("SPRITE COLLISION")
            if vdp.get_5s():
                print(f"SPRITE OVERFLOW: 5th sprite={vdp.get_5s_index()}")
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
                vdp.set_sprite_size16(self.mode >= 2)
                vdp.set_sprite_mag((self.mode % 2) == 1)
            size = 16 if vdp.get_sprite_size16() else 8
            size = size * 2 if vdp.get_sprite_mag() else size
            if frame % 180 == 0:
                for i, s in enumerate(self.sps):
                    if s["x"] >= 256 - size: s["x"] = 256 - size - 1
                    if s["y"] >= 192 - size: s["y"] = 192 - size - 1
                    if vdp.get_sprite_size16():
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
