# ----------------------------------------
# V9918 / TMS9918A Graphics 2 mode emulator
# ----------------------------------------
import pygame
import sys
class V9918:
    SCREEN_WIDTH  = 256
    SCREEN_HEIGHT = 192
    # Graphics 2:
    # 32 x 24 characters
    # 3 pattern banks (768 patterns)
    COLS = 32
    ROWS = 24
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
        self.name_table = [0] * (self.COLS * self.ROWS)
        self.pattern_table = [[0] * 8 for _ in range(self.PATTERN_COUNT)]
        # Graphics2 color table
        # 8 lines per character
        self.color_table = [[0xF1] * 8 for _ in range(self.PATTERN_COUNT)]
    def set_pattern(self, ch, data):
        for i in range(8):
            self.pattern_table[ch][i] = data[i]
    def put_char(self, x, y, ch):
        self.name_table[y * self.COLS + x] = ch
    def set_color(self, ch, line, color):
        self.color_table[ch][line] = color
    def render_graphics2(self, surface):
        for y in range(self.SCREEN_HEIGHT):
            self.render_line_graphics2(surface, y)
    def render_line_graphics2(self, surface, y):
        cy = y // 8
        py = y % 8
        for cx in range(self.COLS):
            # Graphics2 bank selection
            bank = cy // 8
            base_char = self.name_table[cy * self.COLS + cx]
            char_no = base_char + (bank * 256)
            pattern = self.pattern_table[char_no]
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
if __name__ == "__main__":
    vdp = V9918()
    def machine(rom):
        rom.init()
        pygame.init()
        SCALE = 3
        window = pygame.display.set_mode(
            (vdp.SCREEN_WIDTH * SCALE, vdp.SCREEN_HEIGHT * SCALE)
        )
        pygame.display.set_caption("V9918 Graphics 2 Emulator")
        screen = pygame.Surface((vdp.SCREEN_WIDTH, vdp.SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        frame = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            rom.run(frame)
            vdp.render_graphics2(screen)
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
                    vdp.set_color(j*256+0, i, 0xF0+j+1)
                    vdp.set_color(j*256+1, i, 0x40+j+1)
                    vdp.set_color(j*256+2, i, 0xE0+j+1)
                    vdp.set_color(j*256+3, i, 0x70+j+1)
        def run(self,frame):
            # Simple animation
            if frame % 30 == 0:
                for i in range(len(vdp.name_table)):
                    vdp.name_table[i] = (vdp.name_table[i] + 1) % 4
    machine(ROM())
