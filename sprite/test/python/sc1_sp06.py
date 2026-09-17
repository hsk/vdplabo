"""sc1_sp06.asm と同じ落下アニメーションをエンジンで再現し、
録画したwebm(golden)とピクセル単位で比較するテスト。

goldenファイルは見やすさのためニアレストネイバーで4倍(1024x768)に
拡大して保存するが、比較は実寸(256x192)に間引き戻してから行う
(拡大は劣化しない操作なので、間引けば元のピクセル値と完全に一致する)。

VP9の`gbrp`(RGBのまま符号化)を使っているのでビット完全一致かつ
輪郭ににじみも出ない([video_golden.py](video_golden.py)参照)。

参照:
- ソース: ../asm/sc1_sp06.asm
- 解説:   ../docs/sc1_sp06.md

実行方法:
    python sc1_sp06.py                 # 自動テストのみ実行
    python sc1_sp06.py --show          # pygameウィンドウで目視確認(等倍速ループ)
    python sc1_sp06.py --update-golden # ../expected/sc1_sp06.webm を再生成
"""
import pathlib
import sys

_ENGINE_SPRITE1 = pathlib.Path(__file__).resolve().parents[2] / "engine" / "python" / "sprite1"
if str(_ENGINE_SPRITE1) not in sys.path:
    sys.path.insert(0, str(_ENGINE_SPRITE1))

from stage1 import V9918  # noqa: E402
from video_golden import save_video, load_video, surface_to_rgb, upscale_nearest, downscale_nearest  # noqa: E402

# test/expected/ はpython実装専用ではなく、将来asm(openMSX)のテストなど
# 別の実装からも同じ正解データとして参照できる共有の置き場所
GOLDEN_PATH = pathlib.Path(__file__).resolve().parents[1] / "expected" / "sc1_sp06.webm"

# goldenは見やすさのため実寸(256x192)ではなくニアレストネイバーで
# 4倍に拡大して保存する(ドット絵なので拡大しても劣化しない)
VIEW_SCALE = 4
GOLDEN_WIDTH = V9918.SCREEN_WIDTH * VIEW_SCALE
GOLDEN_HEIGHT = V9918.SCREEN_HEIGHT * VIEW_SCALE

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


def render_frames(count: int = FRAME_COUNT):
    import pygame

    pygame.init()
    vdp = build_vdp()
    state = SpriteState()
    surface = pygame.Surface((V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT))
    frames = []

    def draw():
        for i in range(4):
            vdp.set_sprite(i, START_X[i], state.y[i], i, COLOR)
        vdp.render_sprite1(surface)
        frames.append(surface_to_rgb(surface))

    draw()  # frame 0: sprite_init直後、まだ動く前の初期状態
    for c in range(1, count):
        state.advance(c)
        draw()
    return frames


def render_frames_scaled(count: int = FRAME_COUNT):
    """golden保存用: 実寸フレームをVIEW_SCALE倍にしたもの。"""
    return [
        upscale_nearest(f, V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT, VIEW_SCALE)
        for f in render_frames(count)
    ]


def test_all_sprites_settle_at_target_y():
    state = SpriteState()
    for c in range(1, FRAME_COUNT):
        state.advance(c)
    assert state.y == [87, 87, 87, 87]


def test_sprites_start_offscreen():
    state = SpriteState()
    assert state.y == [START_Y] * 4


def test_matches_golden_video():
    if not GOLDEN_PATH.exists():
        raise AssertionError(
            f"golden not found: {GOLDEN_PATH} "
            "(run `python sc1_sp06.py --update-golden` once to create it)"
        )
    actual = render_frames()  # 実寸(256x192)のまま比較する
    golden_frames = load_video(GOLDEN_PATH, GOLDEN_WIDTH, GOLDEN_HEIGHT)
    expected = [
        downscale_nearest(f, V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT, VIEW_SCALE)
        for f in golden_frames
    ]
    assert len(actual) == len(expected), (
        f"frame count mismatch: actual={len(actual)} expected={len(expected)}"
    )
    for i, (a, e) in enumerate(zip(actual, expected)):
        assert a == e, f"frame {i} differs from golden"


def _run_all_tests():
    ok = True
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {name}")
            except AssertionError as e:
                ok = False
                print(f"FAIL {name}: {e}")
    return ok


def update_golden():
    frames = render_frames_scaled()
    GOLDEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_video(frames, GOLDEN_WIDTH, GOLDEN_HEIGHT, GOLDEN_PATH)
    print(f"wrote {GOLDEN_PATH} ({GOLDEN_WIDTH}x{GOLDEN_HEIGHT}, {len(frames)} frames)")


def show_window():
    """目視確認用: pygameウィンドウでアニメーションを等倍速でループ再生する。"""
    import pygame

    pygame.init()
    vdp = build_vdp()
    state = SpriteState()
    scale = 3
    window = pygame.display.set_mode(
        (V9918.SCREEN_WIDTH * scale, V9918.SCREEN_HEIGHT * scale)
    )
    pygame.display.set_caption("sc1_sp06")
    screen = pygame.Surface((V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    cycle_len = 300  # 255フレーム + 1秒待ち相当のループ間隔
    frame = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        cycle_frame = frame % cycle_len
        if cycle_frame == 0:
            state = SpriteState()
        else:
            state.advance(cycle_frame)
        for i in range(4):
            vdp.set_sprite(i, START_X[i], state.y[i], i, COLOR)
        vdp.render_sprite1(screen)
        scaled = pygame.transform.scale(
            screen, (V9918.SCREEN_WIDTH * scale, V9918.SCREEN_HEIGHT * scale)
        )
        window.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        frame += 1


if __name__ == "__main__":
    if "--show" in sys.argv:
        show_window()
    elif "--update-golden" in sys.argv:
        update_golden()
    else:
        sys.exit(0 if _run_all_tests() else 1)
