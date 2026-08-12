import pygame
import sys
from rtype_logo import LOGO_DATA

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 256, 192
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("R-TYPE 32x32 Easing Controlled Logo")

BLACK, WHITE = (0, 0, 0), (255, 255, 255)

# --- 📈 イージング数式の定義マニュアル ---
# すべて「0.0（開始）」から「1.0（終了）」の時間を入力すると、「0.0〜1.0」の進行度を返す関数です。
class Easing:
    @staticmethod
    def linear(t):
        return t

    @staticmethod
    def ease_out_quad(t):
        """だんだん減速（滑らかに止まる）"""
        return 1 - (1 - t) * (1 - t)

    @staticmethod
    def ease_out_bounce(t):
        """ガシャン！とぶつかってリアルに弾む（R-TYPEの重厚感に最適）"""
        n1 = 7.5625
        d1 = 2.75
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375


class LogoChar:
    def __init__(self, matrix, index):
        X_OFFSETS = [0, 30, 60, 100, 140, 180]
        self.offset_x = X_OFFSETS[index]
        self.x, self.y = 0.0, 0.0
        # フェーズ開始時の座標を記憶する変数
        self.start_x, self.start_y = 0.0, 0.0
        self.image = self._create_image(matrix)

    def _create_image(self, matrix):
        surf = pygame.Surface((32, 32))
        surf.fill(BLACK)
        surf.set_colorkey(BLACK)
        for y in range(16):
            for x in range(16):
                if matrix[y][x] == 1:
                    pygame.draw.rect(surf, WHITE, (x * 2, y * 2, 2, 2))
        return surf

    def save_current_position(self):
        """フェーズ切り替え時に、現在の位置を「スタート地点」としてロックする"""
        self.start_x = self.x
        self.start_y = self.y

    def draw(self, surface):
        surface.blit(self.image, (int(self.x), int(self.y)))


class LogoAnimator:
    def __init__(self):
        self.chars = [LogoChar(matrix, i) for i, matrix in enumerate(LOGO_DATA)]
        self.phase = 0
        self.cnt = 0
        
        # 初期座標を設定
        for c in self.chars:
            c.x, c.y = 256.0, 60.0
            c.save_current_position()

        # ★ イージング関数を名前（文字列）で呼び出せるようにマッピング
        self.easing_functions = {
            "linear": Easing.linear,
            "ease_out": Easing.ease_out_quad,
            "bounce": Easing.ease_out_bounce
        }

        # ★ 演出スケジュール（時間、目的地、そして【イージングの種類】を指定！）
        self.SEQUENCE = [
            {"duration": 45, "easing": "linear",   "expand": 0.0, "base_x": 24, "base_y": 60},  # P1: 等速で画面内へスライド
            {"duration": 32, "easing": "ease_out", "expand": 1.0, "base_x": 24, "base_y": 60},  # P2: 滑らかに減速しながら横展開
            {"duration": 40, "easing": "bounce",   "expand": 1.0, "base_x": 24, "base_y": 104}, # P3: ガシャン！と下に落ちてバウンド
            {"duration": 60, "easing": "linear",   "expand": 1.0, "base_x": 24, "base_y": 104}, # P4: 静止
            {"duration": 10, "easing": "linear",   "expand": 4.0, "base_x": -100, "base_y": 192}, # P4: 静止
        ]

    def update(self):
        current_seq = self.SEQUENCE[self.phase]
        duration = current_seq["duration"]
        
        # 1. 時間の割合 (0.0 〜 1.0) を計算
        time_ratio = self.cnt / duration
        if time_ratio > 1.0: time_ratio = 1.0

        # 2. 指定された種類のイージング関数をデータから取得して、進行度(t)を計算
        easing_key = current_seq["easing"]
        easing_func = self.easing_functions[easing_key]
        t = easing_func(time_ratio)  # 0.0〜1.0 の形に変形される

        # 3. 最終的な目的地
        target_expand = current_seq["expand"]
        target_base_x = current_seq["base_x"]
        target_base_y = current_seq["base_y"]

        # 4. 各文字の座標を「開始地点から目的地の間」で補間計算（ラープ公式）
        for c in self.chars:
            dest_x = target_base_x + (c.offset_x * target_expand)
            dest_y = target_base_y
            
            # 【公式】 現在地 = 開始地 + (目的地 - 開始地) * イージング進行度
            c.x = c.start_x + (dest_x - c.start_x) * t
            c.y = c.start_y + (dest_y - c.start_y) * t

        # 時間進行とフェーズ切り替え
        self.cnt += 1
        if self.cnt > duration:
            self.cnt = 0
            self.phase += 1
            
            # ★ 全フェーズが終了したら、最初のフェーズ(0)に戻し、位置も一瞬でリセットする
            if self.phase >= len(self.SEQUENCE):
                self.phase = 0
                for c in self.chars:
                    c.x, c.y = 256.0, 60.0  # 最初の初期位置（画面右外）へワープ
                    c.save_current_position()
            else:
                # 通常のフェーズ切り替え時は、今の位置を次のスタート地点にする
                for c in self.chars:
                    c.save_current_position()

    def draw(self, screen):
        for c in self.chars:
            c.draw(screen)


def main():
    clock = pygame.time.Clock()
    animator = LogoAnimator()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        animator.update()
        
        screen.fill(BLACK)
        animator.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
