import pygame
import sys

# --- 📐 画面とスプライトのサイズ設定 ---
WIDTH = 256
HEIGHT = 192

def main():
    # 初期化
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TYPE")
    clock = pygame.time.Clock()
    # スプライト作成
    sprites = [create_sprite(FONTS[i]) for i in range(4)]
    frame = 0
    # --- 🔄 メインループ ---
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill((0, 0, 0)) # 完全な黒背景
        # 各スプライトの更新と描画
        for i in range(4):
            if frame >= start_delay[i]:
                # 定位置まで上から高速スライドイン
                if current_y[i] < 88:
                    current_y[i] += 4  # 画面サイズに合わせて速度を調整
        for i in range(4):
            screen.blit(sprites[i], (target_x[i], current_y[i]))
        pygame.display.flip()
        clock.tick(60)
        frame += 1

# --- 📦 単色スプライトの生成 ---
def create_sprite(matrix):
    surf = pygame.Surface((8, 8), pygame.SRCALPHA)
    for y in range(8):
        for x in range(8):
            if matrix[y] & (1 << (7-x)):
                surf.set_at((x, y), (0, 180, 255))
    # 2倍に拡大
    return pygame.transform.scale(surf, (16, 16))


# 各文字の固定X座標を計算
target_x = [
    88 + 24 * 0,
    88 + 24 * 1,
    88 + 24 * 2,
    88 + 24 * 3
]

# アニメーション用（初期位置は画面の上外）
current_y = [-16, -16, -16, -16]
start_delay = [60+0, 60+12, 60+24, 60+36] # 出現する時間差（フレーム数）

# --- 🎨 8x8 ドットフォント定義 ---
FONTS = [
    [
        0b11111111,
        0b00011000,
        0b00011000,
        0b00011000,
        0b00011000,
        0b00011000,
        0b00011000,
        0b00011000
    ],
    [
        0b10000001,
        0b11000011,
        0b01100110,
        0b00111100,
        0b00011000,
        0b00011000,
        0b00011000,
        0b00011000
    ],
    [
        0b11111110,
        0b11000011,
        0b11000011,
        0b11111110,
        0b11000000,
        0b11000000,
        0b11000000,
        0b11000000
    ],
    [
        0b11111111,
        0b11000000,
        0b11000000,
        0b11111100,
        0b11000000,
        0b11000000,
        0b11000000,
        0b11111111
    ]
]

main()
