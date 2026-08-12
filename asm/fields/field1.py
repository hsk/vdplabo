import pygame
import sys

pygame.init()

# 画面サイズを取得（全画面にするなら display.Info を使う）
screen_width, screen_height = 256, 192
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Checkerboard with Perspective")

# 色
colors = [(0, 192, 0), (128, 255, 128)]  # 白とグレー

def draw_checkerboard(scroll_x, horizon_y, scroll_z):
    # 4x4ドットを1セルとして扱う
    size = 4
    # 画面全体をセル単位で走査
    for y in range(0, screen_height, size):
        for x in range(0, screen_width, size):
            # 地平線そのものはゼロ除算になるので描画しない
            if y == horizon_y - size: continue
            if y < horizon_y - size:
                # 地平線より上側
                # distance_from_horizon は地平線からの距離
                # horizon_distance は遠近計算の基準距離
                horizon_distance = horizon_y
                distance_from_horizon = horizon_distance - y
            else:
                # 地平線より下側
                # 同じ計算式が使えるように上下反転して扱う
                horizon_distance = (192 - 4 - horizon_y + 8)
                distance_from_horizon = horizon_distance - (192 - y)
            # perspective_scale は遠近による拡大率
            perspective_scale = distance_from_horizon / horizon_distance * 64
            # 画面上のY座標から地面上の奥行き座標 ground_z を逆算
            # 地平線に近いほど遠方になる
            ground_z = 2 * 256 * horizon_distance / distance_from_horizon
            # 画面X座標を地面上の横座標 ground_x へ変換
            # 遠方では圧縮され、手前では広がる
            ground_x = ((x - 128) * 2) / perspective_scale
            # ground_x から横方向のマス番号を求める
            checker_color = int(scroll_x / 8 + ground_x + 1000) & 1
            # ground_z から奥行き方向のマス番号を求める
            checker_color ^= int((ground_z + scroll_z) / 256) & 1
            # 2色のチェッカーボードを描画
            pygame.draw.rect(screen,colors[checker_color],(x, y, size, size))

# メインループ
clock = pygame.time.Clock()
z = 0
y = 192/2
x = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    keys=pygame.key.get_pressed()
    if keys[pygame.K_UP]: y -= 8
    if keys[pygame.K_DOWN]: y += 8
    if keys[pygame.K_LEFT]: x -= 1
    if keys[pygame.K_RIGHT]: x += 1
    x = x % 16
    y = max(64, min(192-32, y))
    screen.fill((0, 0, 0))
    draw_checkerboard(x,y,z)
    z += 64
    if z >= 512: z = 0
    pygame.display.flip()
    clock.tick(15)
