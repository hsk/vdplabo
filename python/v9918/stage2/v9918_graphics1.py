# ----------------------------------------
# V9918 / TMS9918A Graphics 1 mode emulator
# ----------------------------------------
import pygame
import sys
class V9918:
    SCREEN_WIDTH  = 256
    SCREEN_HEIGHT = 192
    # Graphics 1:
    # 32 x 24 characters
    COLS = 32
    ROWS = 24
    # VRAM sizes
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
        self.name_table = [0] * (self.COLS * self.ROWS)
        self.pattern_table = [[0] * 8 for _ in range(self.PATTERN_COUNT)]
        self.color_table = [0xF1] * self.PATTERN_COUNT
    def set_pattern(self, ch, data):
        for i in range(8):
            self.pattern_table[ch][i] = data[i]
    def put_char(self, x, y, ch):
        self.name_table[y * self.COLS + x] = ch
    def set_color(self, ch, color):
        self.color_table[ch] = color
    def render_graphics1(self, surface):
        for y in range(self.SCREEN_HEIGHT):
            self.render_line_graphics1(surface, y)
    def render_line_graphics1(self, surface, y):
        x = 0
        name = (y // 8) * self.COLS
        py = y % 8
        for _ in range(self.COLS):
            char_no  = self.name_table[name]
            name += 1
            bits     = self.pattern_table[char_no][py]
            color    = self.color_table[char_no]
            fg_color = self.PALETTE[(color >> 4) & 0x0F]
            bg_color = self.PALETTE[color & 0x0F]
            for px in range(8):
                c = fg_color if bits & (0x80 >> px) else bg_color
                surface.set_at((x, y), c)
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
        pygame.display.set_caption("V9918 Graphics 1 Emulator")
        screen = pygame.Surface((vdp.SCREEN_WIDTH, vdp.SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        frame = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            rom.run(frame)
            vdp.render_graphics1(screen)
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

    machine(ROM())
