import pygame
import sys

pygame.init()

# 画面サイズを取得（全画面にするなら display.Info を使う）
screen_width, screen_height = 256, 192
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Stripe with Perspective")

# 色
colors = [(0, 224, 0), (0, 255, 0), (128, 255, 128),(0, 255, 0)]  # 白とグレー

def draw_stripe(horizon_y, scroll_z):
    # 画面全体をセル単位で走査
    for y in range(0, screen_height):
        # 地平線そのものはゼロ除算になるので描画しない
        if y == horizon_y: continue
        if y < horizon_y:
            # 地平線より上側
            # distance_from_horizon は地平線からの距離
            # horizon_distance は遠近計算の基準距離
            horizon_distance = horizon_y
            distance_from_horizon = horizon_distance - y
        else:
            # 地平線より下側
            # 同じ計算式が使えるように上下反転して扱う
            horizon_distance = (screen_height - horizon_y)
            distance_from_horizon = horizon_distance - (screen_height - y)
        # 画面上のY座標から地面上の奥行き座標 ground_z を逆算
        # 地平線に近いほど遠方になる
        ground_z = 8 * horizon_distance / distance_from_horizon
        # ground_z から奥行き方向の色を求める
        color = int(ground_z + scroll_z) & 3
        # １ライン分のストライプを描画
        pygame.draw.rect(screen,colors[color],(0, y, screen_width, 1))
# メインループ
clock = pygame.time.Clock()
z = 0
y = 192/2

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    keys=pygame.key.get_pressed()
    if keys[pygame.K_UP]: y -= 8
    if keys[pygame.K_DOWN]: y += 8
    if keys[pygame.K_z]: z += 1
    y = max(8, min(192-32, y))
    z = z & 7
    screen.fill((0, 0, 0))
    draw_stripe(y,z)
    pygame.display.flip()
    clock.tick(15)
