# ----------------------------------------
# V9918 / TMS9918A emulator
# ----------------------------------------
import pygame
import sys
import random
class V9918:
    SCREEN_WIDTH  = 256
    SCREEN_HEIGHT = 192
    # Graphics 1:
    # 32 x 24 characters
    COLS = 32
    COLS_TEXT1 = 40
    CHAR_W = 6
    CHAR_H = 8
    ROWS = 24
    ROWS_MC = 6
    SPRITE_COUNT = 32
    SPRITE_PATTERN_COUNT = 256
    # VRAM sizes
    PATTERN_COUNT = 768
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
        self.name_table = [0] * (self.COLS_TEXT1 * self.ROWS)
        self.pattern_table = [[0] * 8 for _ in range(self.PATTERN_COUNT)]
        self.color_table = [[0xF1] * 8 for _ in range(self.PATTERN_COUNT)]
        self.init_sprites()
    def set_mode(self, mode):
        self.mode = mode
        self.ROWS = 24
        self.COLS = 32
        if mode == "text1":
            self.COLS = self.COLS_TEXT1
        if mode == "mc":
            self.ROWS = self.ROWS_MC

    def set_pattern(self, ch, data):
        for i in range(8):
            self.pattern_table[ch][i] = data[i]
    def put_char(self, x, y, ch):
        self.name_table[y * self.COLS + x] = ch
    def set_color(self, ch, color, line=0):
        self.color_table[ch][line] = color
    def render_graphics1(self, surface):
        for cy in range(self.ROWS):
            for cx in range(self.COLS):
                char_no = self.name_table[cy * self.COLS + cx]
                pattern = self.pattern_table[char_no]
                color   = self.color_table[char_no][0]
                fg = (color >> 4) & 0x0F
                bg = color & 0x0F
                fg_color = self.PALETTE[fg]
                bg_color = self.PALETTE[bg]
                for py in range(8):
                    bits = pattern[py]
                    for px in range(8):
                        mask = 0x80 >> px
                        if bits & mask:
                            c = fg_color
                        else:
                            c = bg_color
                        x = cx * 8 + px
                        y = cy * 8 + py
                        surface.set_at((x, y), c)
    def render_graphics2(self, surface):
        for cy in range(self.ROWS):
            for cx in range(self.COLS):
                # Graphics2 bank selection
                bank = cy // 8
                base_char = self.name_table[cy * self.COLS + cx]
                char_no = base_char + (bank * 256)
                pattern = self.pattern_table[char_no]
                for py in range(8):
                    color = self.color_table[char_no][py]
                    fg = (color >> 4) & 0x0F
                    bg = color & 0x0F
                    fg_color = self.PALETTE[fg]
                    bg_color = self.PALETTE[bg]
                    bits = pattern[py]
                    for px in range(8):
                        mask = 0x80 >> px
                        if bits & mask:
                            c = fg_color
                        else:
                            c = bg_color
                        x = cx * 8 + px
                        y = cy * 8 + py
                        surface.set_at((x, y), c)
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
    def render_text1(self, surface):
        bg_color = self.PALETTE[self.text_bg]
        fg_color = self.PALETTE[self.text_fg]
        surface.fill(bg_color)
        for cy in range(self.ROWS):
            for cx in range(self.COLS):
                index = cy * self.COLS + cx
                char_no = self.name_table[index]
                pattern = self.pattern_table[char_no]
                for py in range(8):
                    bits = pattern[py]
                    # Text1 uses only 6 pixels width
                    for px in range(6):
                        mask = 0x80 >> px
                        if bits & mask:
                            x = cx * self.CHAR_W + px + 8
                            y = cy * self.CHAR_H + py
                            if 0 <= x < self.SCREEN_WIDTH and 0 <= y < self.SCREEN_HEIGHT:
                                surface.set_at((x, y), fg_color)

    def init_sprites(self):
        # Sprite attribute table
        self.sprites = []
        for i in range(self.SPRITE_COUNT):
            self.sprites.append({
                "x": 0,
                "y": 0,
                "pattern": 0,
                "color": 15,
                "enable": False,
            })
        # Global sprite mode flags
        self.sprite_mag = False
        self.sprite_size16 = False
        # Sprite pattern generator table
        self.sprite_patterns = [[0] * 8 for _ in range(self.SPRITE_PATTERN_COUNT)]
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
        self.sprites[no]["enable"] = True
    def render_sprite1(self, surface):
        surface.fill((0, 0, 0))
        for spr in self.sprites:
            if not spr["enable"]:
                continue
            color = self.PALETTE[spr["color"]]
            blocks = [(0, 0, spr["pattern"])]
            if self.sprite_size16:
                base = spr["pattern"] & 0xFC
                blocks = [
                    (0, 0, base + 0),
                    (8, 0, base + 1),
                    (0, 8, base + 2),
                    (8, 8, base + 3),
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

    def render(self, surface):
        match self.mode:
            case "graphics1": return self.render_graphics1(surface)
            case "graphics2": return self.render_graphics2(surface)
            case "mc": return self.render_mc(surface)
            case "text1": return self.render_text1(surface)
            case "sprite1": return self.render_sprite1(surface)
if __name__ == "__main__":
    vdp = V9918()
    def machine(rom):
        rom.init()
        pygame.init()
        SCALE = 3
        window = pygame.display.set_mode(
            (vdp.SCREEN_WIDTH * SCALE, vdp.SCREEN_HEIGHT * SCALE)
        )
        pygame.display.set_caption("V9918 Emulator")
        screen = pygame.Surface((vdp.SCREEN_WIDTH, vdp.SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        frame = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return
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

    class ROMG1:
        def init(self):
            vdp.set_mode("graphics1")
            # Space
            vdp.set_pattern(0, [
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000,
            ])
            # Block
            vdp.set_pattern(1, [
                0b11111111,
                0b11111111,
                0b11111111,
                0b11111111,
                0b11111111,
                0b11111111,
                0b11111111,
                0b11111111,
            ])
            # Smile
            vdp.set_pattern(2, [
                0b00111100,
                0b01000010,
                0b10100101,
                0b10000001,
                0b10100101,
                0b10011001,
                0b01000010,
                0b00111100,
            ])
            # Checker
            vdp.set_pattern(3, [
                0b10101010,
                0b01010101,
                0b10101010,
                0b01010101,
                0b10101010,
                0b01010101,
                0b10101010,
                0b01010101,
            ])
            # Fill screen
            for y in range(vdp.ROWS):
                for x in range(vdp.COLS):
                    ch = (x + y) % 4
                    vdp.put_char(x, y, ch)
            # Colors
            vdp.set_color(0, 0xF1)
            vdp.set_color(1, 0x41)
            vdp.set_color(2, 0xE1)
            vdp.set_color(3, 0x71)
        def run(self,frame):
            # Simple animation
            if frame % 30 == 0:
                for i in range(len(vdp.name_table)):
                    vdp.name_table[i] = (vdp.name_table[i] + 1) % 4
    class ROMG2:
        def init(self):
            vdp.set_mode("graphics2")
            for j in range(3):
                # Space
                vdp.set_pattern(j*256+0, [
                    0b00000000,
                    0b00000000,
                    0b00000000,
                    0b00000000,
                    0b00000000,
                    0b00000000,
                    0b00000000,
                    0b00000000,
                ])
                # Block
                vdp.set_pattern(j*256+1, [
                    0b11111111,
                    0b11111111,
                    0b11111111,
                    0b11111111,
                    0b11111111,
                    0b11111111,
                    0b11111111,
                    0b11111111,
                ])
                # Smile
                vdp.set_pattern(j*256+2, [
                    0b00111100,
                    0b01000010,
                    0b10100101,
                    0b10000001,
                    0b10100101,
                    0b10011001,
                    0b01000010,
                    0b00111100,
                ])
                # Checker
                vdp.set_pattern(j*256+3, [
                    0b10101010,
                    0b01010101,
                    0b10101010,
                    0b01010101,
                    0b10101010,
                    0b01010101,
                    0b10101010,
                    0b01010101,
                ])
            # Fill screen
            for y in range(vdp.ROWS):
                for x in range(vdp.COLS):
                    ch = (x + y) % 4
                    vdp.put_char(x, y, ch)
            # Graphics2 colors (per line)
            for j in range(3):
                for i in range(8):
                    vdp.set_color(j*256+0, 0xF0+j+1, i)
                    vdp.set_color(j*256+1, 0x40+j+1, i)
                    vdp.set_color(j*256+2, 0xE0+j+1, i)
                    vdp.set_color(j*256+3, 0x70+j+1, i)
        def run(self,frame):
            # Simple animation
            if frame % 30 == 0:
                for i in range(len(vdp.name_table)):
                    vdp.name_table[i] = (vdp.name_table[i] + 1) % 4
    class ROMMC:
        def init(self):
            vdp.set_mode("mc")
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
    class ROMTEXT1:
        def init(self):
            vdp.set_mode("text1")
            # Space
            vdp.set_pattern(0, [
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000,
            ])
            # Block
            vdp.set_pattern(1, [
                0b11111100,
                0b11111100,
                0b11111100,
                0b11111100,
                0b11111100,
                0b11111100,
                0b11111100,
                0b11111100,
            ])
            # Smile
            vdp.set_pattern(2, [
                0b00111000,
                0b01000100,
                0b10101100,
                0b10000100,
                0b10101100,
                0b10010100,
                0b01000100,
                0b00111000,
            ])
            # Checker
            vdp.set_pattern(3, [
                0b10101000,
                0b01010100,
                0b10101000,
                0b01010100,
                0b10101000,
                0b01010100,
                0b10101000,
                0b01010100,
            ])
            # Fill screen
            for y in range(vdp.ROWS):
                for x in range(vdp.COLS):
                    ch = (x + y) % 4
                    vdp.put_char(x, y, ch)
            # Colors
            vdp.set_color(0, 0xF1)
            vdp.set_color(1, 0x41)
            vdp.set_color(2, 0xE1)
            vdp.set_color(3, 0x71)
            # Text mode colors
            vdp.text_fg = 15
            vdp.text_bg = 4
        def run(self,frame):
            return
            # Simple animation
            if frame % 30 == 0:
                for i in range(len(vdp.name_table)):
                    vdp.name_table[i] = (vdp.name_table[i] + 1) % 4
    class ROMSP1:
        def init(self):
            vdp.set_mode("sprite1")
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
            base_size = 16 if vdp.sprite_size16 else 8
            size = base_size * 2 if vdp.sprite_mag else base_size
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

    while True:
        machine(ROMG1())
        machine(ROMG2())
        machine(ROMMC())
        machine(ROMTEXT1())
        machine(ROMSP1())
