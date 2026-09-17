"""sc1_sp05.asm と同じ「9個のスプライトのY座標を-8〜8で増減させ、
1ラインの表示制限(5個以上)に達すると10個目の診断用スプライトが
赤くなる」デモをエンジンで再現し、golden動画と比較するテスト。

engine/python/sprite1/stage4.py (レジスタ駆動・スキャンライン描画)を使う。
5th sprite(スプライトオーバー)判定は実機のVDPと同じくstage4エンジン
自身が計算するので、このテストはその計算結果をそのまま信頼して
「asmと同じ手順でスプライト配置とSTATFL読み取りを再現できているか」
だけを検証する。

## 実機のタイミングについて(重要な近似)

実機では main_loop の1周ごとに:
1. sprites_move で9個のテスト用スプライトのY座標を更新(RAM上のみ)
2. debug_sprite_status で STATFL(前回VRAMに転送された配置に対する
   VDPの判定結果)を読み、10個目の診断用スプライトへ反映
3. sprites_update でRAM→VRAMへ転送(ここで初めて画面に反映される)

つまり診断用スプライトは常に「1つ前の周で表示されていた配置」に対する
判定結果を表示する1周分の遅延がある。このテストも同じ遅延をモデル化する。

ただし実機の一番最初のフレーム(cold boot直後)は、その「1つ前の配置」が
BIOS起動時のVRAM残留内容に依存し未定義になる。本テストはその起動直後の
過渡状態は対象にせず、「ループが十分回った後の定常状態」を前提とする
近似として、周期(17周: c=-8〜8)の最後(c=8)の配置を1周目の「前回」として
扱う。

参照:
- ソース: ../asm/sc1_sp05.asm
- 解説:   ../docs/sc1_sp05.md

実行方法:
    python sc1_sp05.py                 # 自動テストのみ実行
    python sc1_sp05.py --show          # pygameウィンドウで目視確認(ループ再生)
    python sc1_sp05.py --update-golden # ../expected/sc1_sp05.webm を再生成
"""
import pathlib
import sys

_ENGINE_SPRITE1 = pathlib.Path(__file__).resolve().parents[2] / "engine" / "python" / "sprite1"
if str(_ENGINE_SPRITE1) not in sys.path:
    sys.path.insert(0, str(_ENGINE_SPRITE1))

from stage4 import V9918  # noqa: E402
from video_golden import save_video, load_video, surface_to_rgb, upscale_nearest, downscale_nearest  # noqa: E402

GOLDEN_PATH = pathlib.Path(__file__).resolve().parents[1] / "expected" / "sc1_sp05.webm"

VIEW_SCALE = 4
GOLDEN_WIDTH = V9918.SCREEN_WIDTH * VIEW_SCALE
GOLDEN_HEIGHT = V9918.SCREEN_HEIGHT * VIEW_SCALE

# sc1_sp05.asm の sprite_init と同じパラメータ
TEST_COUNT = 9
X = [100 + i * 16 for i in range(TEST_COUNT)]
COLOR = [5 + i for i in range(TEST_COUNT)]
Y_BASE = 100
C_MIN, C_MAX = -8, 8  # c は -8..8 の17値をループする
PERIOD = C_MAX - C_MIN + 1

# 診断用スプライト(10個目, index=9)
DIAG_INDEX = 9
DIAG_Y = 0
DIAG_PATTERN = 0
DIAG_COLOR_OVERFLOW = 8   # 赤
DIAG_COLOR_NORMAL = 15    # 白

# FILVRM でパターン0の8バイトを255で埋める = 無地の8x8正方形
SPRITE_PATTERN = [0b11111111] * 8

WAIT_FRAMES = 5  # wait_5frame と同じ: 1つの配置が画面に留まるVSYNC数
STATE_COUNT = PERIOD  # ちょうど1周期分の状態数(c=-8..8)
FRAME_COUNT = STATE_COUNT * WAIT_FRAMES


def build_vdp() -> V9918:
    vdp = V9918()
    vdp.set_sprite_pattern(0, SPRITE_PATTERN)
    vdp.set_sprite_mag(True)
    return vdp


def sprite_y_values(c: int):
    """sprites_move と同じ: Y[i] = 100 + i*c (0-indexed, i=0..8)。"""
    return [Y_BASE + i * c for i in range(TEST_COUNT)]


def evaluate_overflow(y_values):
    """9個のテスト用スプライトのY配置から、そのフレームでVDPが記録する
    スプライトオーバー(5S)フラグと消えたスプライト番号を計算する
    (実機のSTATFLに相当)。

    診断用スプライト自身(Y=0)がライン0近辺の判定に与える影響は、
    テスト用スプライトのY範囲(36〜164程度)と重ならないため無視している。
    """
    import pygame

    pygame.init()
    vdp = V9918()
    vdp.set_sprite_pattern(0, SPRITE_PATTERN)
    vdp.set_sprite_mag(True)
    for i, y in enumerate(y_values):
        vdp.set_sprite(i, X[i], y, 0, COLOR[i])
    vdp.set_sprite(DIAG_INDEX, 0, 208, 0, 0)  # Y=208 で打ち切り、9枚だけを評価する
    surface = pygame.Surface((V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT))
    vdp.render_sprite1(surface)
    return vdp.get_5s(), vdp.get_5s_index()


def render_frames(state_count: int = STATE_COUNT):
    """各状態を wait_5frame と同じく WAIT_FRAMES 回複製して、
    実機の表示時間(1状態=5 VSYNC)に合わせたフレーム列を返す。
    """
    import pygame

    pygame.init()
    vdp = build_vdp()
    surface = pygame.Surface((V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT))
    frames = []

    c = C_MIN
    prev_y_values = None
    for _ in range(state_count):
        y_values = sprite_y_values(c)

        if prev_y_values is None:
            # 定常状態の近似: 1周前(c=C_MAX)の配置を「前回」とみなす
            overflow, index = evaluate_overflow(sprite_y_values(C_MAX))
        else:
            overflow, index = evaluate_overflow(prev_y_values)

        for i, y in enumerate(y_values):
            vdp.set_sprite(i, X[i], y, 0, COLOR[i])
        diag_color = DIAG_COLOR_OVERFLOW if overflow else DIAG_COLOR_NORMAL
        vdp.set_sprite(DIAG_INDEX, index, DIAG_Y, DIAG_PATTERN, diag_color)

        vdp.render_sprite1(surface)
        frame = surface_to_rgb(surface)
        frames.extend([frame] * WAIT_FRAMES)

        prev_y_values = y_values
        c += 1
        if c == C_MAX + 1:
            c = C_MIN
    return frames


def render_frames_scaled(state_count: int = STATE_COUNT):
    return [
        upscale_nearest(f, V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT, VIEW_SCALE)
        for f in render_frames(state_count)
    ]


def test_c_cycles_through_17_values():
    values = []
    c = C_MIN
    for _ in range(PERIOD + 1):
        values.append(c)
        c += 1
        if c == C_MAX + 1:
            c = C_MIN
    assert values == list(range(C_MIN, C_MAX + 1)) + [C_MIN]


def test_overflow_triggers_when_all_sprites_align():
    # c=0 だと9枚全部がY=100に重なるので、5枚目(index=4)でオーバーするはず
    overflow, index = evaluate_overflow(sprite_y_values(0))
    assert overflow is True
    assert index == 4


def test_no_overflow_when_widely_spaced():
    # c=8 なら間隔が広く、5枚以上が同一ラインに重なることはないはず
    overflow, index = evaluate_overflow(sprite_y_values(8))
    assert overflow is False
    assert index == 0


def test_matches_golden_video():
    if not GOLDEN_PATH.exists():
        raise AssertionError(
            f"golden not found: {GOLDEN_PATH} "
            "(run `python sc1_sp05.py --update-golden` once to create it)"
        )
    actual = render_frames()
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
    """目視確認用: pygameウィンドウでループ再生する。"""
    import pygame

    pygame.init()
    vdp = build_vdp()
    scale = 3
    window = pygame.display.set_mode(
        (V9918.SCREEN_WIDTH * scale, V9918.SCREEN_HEIGHT * scale)
    )
    pygame.display.set_caption("sc1_sp05")
    screen = pygame.Surface((V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    c = C_MIN
    prev_y_values = sprite_y_values(C_MAX)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        y_values = sprite_y_values(c)
        overflow, index = evaluate_overflow(prev_y_values)
        for i, y in enumerate(y_values):
            vdp.set_sprite(i, X[i], y, 0, COLOR[i])
        diag_color = DIAG_COLOR_OVERFLOW if overflow else DIAG_COLOR_NORMAL
        vdp.set_sprite(DIAG_INDEX, index, DIAG_Y, DIAG_PATTERN, diag_color)

        vdp.render_sprite1(screen)
        scaled = pygame.transform.scale(
            screen, (V9918.SCREEN_WIDTH * scale, V9918.SCREEN_HEIGHT * scale)
        )
        window.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(12)  # 5フレーム待ちの雰囲気に合わせてゆっくり再生

        prev_y_values = y_values
        c += 1
        if c == C_MAX + 1:
            c = C_MIN


if __name__ == "__main__":
    if "--show" in sys.argv:
        show_window()
    elif "--update-golden" in sys.argv:
        update_golden()
    else:
        sys.exit(0 if _run_all_tests() else 1)
