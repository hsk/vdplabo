import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
#pygame.init()
img = pygame.image.load("field.png")
w, h = img.get_size()
tiles_x = w // 8
tiles_y = h // 8
for tx in range(tiles_x):
    values = []
    for ty in range(tiles_y):
        x = tx * 8
        y = ty * 8
        idx0 = img.get_at_mapped((x + 0, y + 0))
        idx1 = img.get_at_mapped((x + 1, y + 0))
        value = ((idx0 & 0x0F) << 4) | (idx1 & 0x0F)
        values.append(f"${value:02X}")
    print(f"field{tx}: db " + ",".join(values))
