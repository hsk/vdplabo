import pygame
import sys
W,H = 256, 192

# 4色
colors = [
    (0, 240, 0),
    (0, 255, 0),
    (128,255,128),
    (0, 255, 0),
]

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()
    offset = 0
    speed = 2  # 1フレームごとの移動量
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill((0, 0, 0))
        cycle = 8 * len(colors)
        y = -cycle + offset
        while y < H:
            for c in colors:
                pygame.draw.rect(screen, c, (0, y, W, 8))
                y += 8
        offset += speed
        if offset >= cycle: offset -= cycle
        pygame.display.flip()
        clock.tick(60)

main()
