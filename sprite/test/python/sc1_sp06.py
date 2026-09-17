"""sc1_sp06.asm と同じ落下アニメーションをエンジンで再現し、
録画したwebm(expected)とピクセル単位で比較するテスト。

expectedファイルは見やすさのためニアレストネイバーで4倍(1024x768)に
拡大して保存するが、比較は実寸(256x192)に間引き戻してから行う
(拡大は劣化しない操作なので、間引けば元のピクセル値と完全に一致する)。

VP9の`gbrp`(RGBのまま符号化)を使っているのでビット完全一致かつ
輪郭ににじみも出ない([video_expected.py](video_expected.py)参照)。

参照:
- ソース: ../asm/sc1_sp06.asm
- 解説:   ../docs/sc1_sp06.md

実行方法:
    python sc1_sp06.py                 # 自動テストのみ実行
    python sc1_sp06.py --show          # pygameウィンドウで目視確認(等倍速ループ)
    python sc1_sp06.py --update-expected # ../expected/sc1_sp06.webm を再生成
"""
import sys

from test_support import add_engine_path, expected_path_for, render_expected_frames, compare_to_expected, write_expected, main  # noqa: E402

add_engine_path(__file__)

from stage1 import V9918  # noqa: E402

EXPECTED_PATH = expected_path_for(__file__, "sc1_sp06.webm")
VIEW_SCALE = 4

# sc1_sp06.asm の sprite_pattern_data と同じ (T, Y, P, E)
SPRITE_PATTERNS = [
    [0b11111111, 0b00011000, 0b00011000, 0b00011000, 0b00011000, 0b00011000, 0b00011000, 0b00011000],  # T
    [0b10000001, 0b11000011, 0b01100110, 0b00111100, 0b00011000, 0b00011000, 0b00011000, 0b00011000],  # Y
    [0b11111110, 0b11000011, 0b11000011, 0b11111110, 0b11000000, 0b11000000, 0b11000000, 0b11000000],  # P
    [0b11111111, 0b11000000, 0b11000000, 0b11111100, 0b11000000, 0b11000000, 0b11000000, 0b11111111],  # E
]

# sc1_sp06.asm の sprite_init / sprites_move と同じパラメータ
START_X = [88 + 24 * i for i in range(4)]
START_Y = -17
TARGET_Y = 88
STEP = 4
START_DELAY = [0, 12, 24, 36]
COLOR = 5

FRAME_COUNT = 90  # 全スプライトが静止するまで(c=62)を収める


def build_vdp() -> V9918:
    vdp = V9918()
    for i, pattern in enumerate(SPRITE_PATTERNS):
        vdp.set_sprite_pattern(i, pattern)
    return vdp


class SpriteState:
    """sc1_sp06.asm の sprites_move と同じロジックでYを更新する。"""

    def __init__(self):
        self.y = [START_Y] * 4

    def advance(self, frame_counter: int):
        # asm: main は `inc c` してから sprites_move を呼ぶので、
        # frame_counter には 1始まりの「加算後のc」を渡す
        for i in range(4):
            if START_DELAY[i] >= frame_counter:
                continue  # まだ開始時刻に達していない
            candidate = self.y[i] + STEP
            if candidate >= TARGET_Y:
                continue  # 目標位置を超える更新は行わない(そこで静止)
            self.y[i] = candidate


class Simulation:
    """1回目のstep()は「sprite_init直後、まだ動く前」の初期状態を描画し、
    2回目以降はsprites_moveと同じロジックでYを1フレーム進めてから描画する。
    (実機のframe_counterはstep()の呼び出し回数-1に対応する)
    """

    def __init__(self):
        import pygame

        pygame.init()
        self.vdp = build_vdp()
        self.state = SpriteState()
        self.surface = pygame.Surface((V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT))
        self._counter = 0

    def step(self):
        if self._counter > 0:
            self.state.advance(self._counter)
        for i in range(4):
            self.vdp.set_sprite(i, START_X[i], self.state.y[i], i, COLOR)
        self.vdp.render_sprite1(self.surface)
        self._counter += 1


def test_all_sprites_settle_at_target_y():
    state = SpriteState()
    for c in range(1, FRAME_COUNT):
        state.advance(c)
    assert state.y == [87, 87, 87, 87]


def test_sprites_start_offscreen():
    state = SpriteState()
    assert state.y == [START_Y] * 4


def test_matches_expected_video():
    actual = render_expected_frames(Simulation, count=FRAME_COUNT)
    compare_to_expected(actual, EXPECTED_PATH, V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT, VIEW_SCALE, __file__)


def show_window():
    """目視確認用: pygameウィンドウでアニメーションを等倍速でループ再生する。"""
    import pygame

    sim = Simulation()
    scale = 3
    window = pygame.display.set_mode(
        (V9918.SCREEN_WIDTH * scale, V9918.SCREEN_HEIGHT * scale)
    )
    pygame.display.set_caption("sc1_sp06")
    clock = pygame.time.Clock()
    cycle_len = 300  # 255フレーム + 1秒待ち相当のループ間隔
    frame = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if frame % cycle_len == 0:
            sim = Simulation()
        sim.step()
        scaled = pygame.transform.scale(
            sim.surface, (V9918.SCREEN_WIDTH * scale, V9918.SCREEN_HEIGHT * scale)
        )
        window.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        frame += 1


def update_expected():
    frames = render_expected_frames(Simulation, count=FRAME_COUNT)
    write_expected(frames, EXPECTED_PATH, V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT, VIEW_SCALE)


if __name__ == "__main__":
    main(globals(), show_window, update_expected)
