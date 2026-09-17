"""sc1_sp05.asm と同じ「9個のスプライトのY座標を-8〜8で増減させ、
1ラインの表示制限(5個以上)に達すると10個目の診断用スプライトが
赤くなる」デモをエンジンで再現し、golden動画と比較するテスト。

engine/python/sprite1/stage4.py (レジスタ駆動・スキャンライン描画)を使う。
5th sprite(スプライトオーバー)判定は実機のVDPと同じくstage4エンジン
自身が計算するので、このテストはその計算結果をそのまま信頼して
「asmと同じ手順でスプライト配置とSTATFL読み取りを再現できているか」
だけを検証する。

## 実機のタイミングについて

実機では main_loop の1周ごとに:
1. sprites_move で9個のテスト用スプライトのY座標を更新(RAM上のみ)
2. debug_sprite_status で STATFL(前回VRAMに転送された配置に対する
   VDPの判定結果)を読み、10個目の診断用スプライトへ反映
3. sprites_update でRAM→VRAMへ転送(ここで初めて画面に反映される)

つまり診断用スプライトは常に「1つ前の周で表示されていた配置」に対する
判定結果を表示する1周分の遅延がある。このテストも同じ遅延をモデル化する。

main_loop は無限ループでc=-8..8(17状態)を繰り返すだけなので、定常状態
(cold boot直後の最初の1回を除く)では「1つ前の状態」は必ず周期内の
1つ前の値になる。これは近似ではなく、ループが回り続けている限り厳密に
成り立つ関係なので、どの位相(どのcの値)から録画を始めても正しく
フレーム列を再構成できる(render_frames の start_c 引数)。

PALETTEと背景色(R#7)はopenMSXで実測した値を使っており、
../expected/sc1_sp05_openmsx.webm (実機キャプチャ)と位相さえ合わせれば
ビット完全一致することを目指している。

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
    # sc1_sp05.asm もVDPレジスタ7(背景色)を書き換えていないため、
    # BIOSのデフォルト値(BAKCLR=4, 青)がそのまま背景色として残る。
    vdp.set_backdrop_color(4)
    return vdp


def sprite_y_values(c: int):
    """sprites_move と同じ: Y[i] = 100 + i*c (0-indexed, i=0..8)。"""
    return [Y_BASE + i * c for i in range(TEST_COUNT)]


def _next_c(c: int) -> int:
    c += 1
    return C_MIN if c == C_MAX + 1 else c


def _prev_c(c: int) -> int:
    c -= 1
    return C_MAX if c == C_MIN - 1 else c


def render_frames(state_count: int = STATE_COUNT, start_c: int = C_MIN):
    """各状態を wait_5frame と同じく WAIT_FRAMES 回複製して、
    実機の表示時間(1状態=5 VSYNC)に合わせたフレーム列を返す。

    main_loop は無限ループでc=-8..8を繰り返すだけなので、周期内であれば
    どのcから始めても「1つ前の状態」は必ず (c-1) (wrap込み) になる
    (cold boot直後の最初の1回だけは前回が未定義になるが、そこは対象外)。
    start_c を変えることで、実機キャプチャがどの位相から始まっていても
    同じ位相からフレーム列を生成し直せる。
    """
    import pygame

    pygame.init()
    vdp = build_vdp()
    surface = pygame.Surface((V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT))
    frames = []

    c = start_c

    # 定常状態の初期化: 1つ前の周(c-1)の配置を同じvdpで実際に描画しておき、
    # そのときの5S状態を「前回の結果」として引き継がせる
    # (実機は動き続けている1つのVDPなので、毎回作り直したりはしない)
    for i, y in enumerate(sprite_y_values(_prev_c(c))):
        vdp.set_sprite(i, X[i], y, 0, COLOR[i])
    vdp.set_sprite(DIAG_INDEX, 0, 208, 0, 0)
    vdp.render_sprite1(surface)

    for _ in range(state_count):
        # このvdpが「直前の描画」で記録した5S状態を読む(実機のSTATFL相当)
        overflow, index = vdp.get_5s(), vdp.get_5s_index()
        diag_color = DIAG_COLOR_OVERFLOW if overflow else DIAG_COLOR_NORMAL

        for i, y in enumerate(sprite_y_values(c)):
            vdp.set_sprite(i, X[i], y, 0, COLOR[i])
        vdp.set_sprite(DIAG_INDEX, index, DIAG_Y, DIAG_PATTERN, diag_color)

        vdp.render_sprite1(surface)  # ここで今回の配置の5S状態が新しく記録される
        frame = surface_to_rgb(surface)
        frames.extend([frame] * WAIT_FRAMES)

        c = _next_c(c)
    return frames


def render_frames_scaled(state_count: int = STATE_COUNT, start_c: int = C_MIN):
    return [
        upscale_nearest(f, V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT, VIEW_SCALE)
        for f in render_frames(state_count, start_c)
    ]


def test_c_cycles_through_17_values():
    values = []
    c = C_MIN
    for _ in range(PERIOD + 1):
        values.append(c)
        c = _next_c(c)
    assert values == list(range(C_MIN, C_MAX + 1)) + [C_MIN]


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
    for i, y in enumerate(sprite_y_values(_prev_c(c))):
        vdp.set_sprite(i, X[i], y, 0, COLOR[i])
    vdp.set_sprite(DIAG_INDEX, 0, 208, 0, 0)
    vdp.render_sprite1(screen)

    frame = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # wait_5frame と同じく、WAIT_FRAMES(5)フレームに1回だけ状態を更新する。
        # 描画とタイマー自体は実機と同じ60FPSのまま回す。
        if frame % WAIT_FRAMES == 0:
            overflow, index = vdp.get_5s(), vdp.get_5s_index()
            diag_color = DIAG_COLOR_OVERFLOW if overflow else DIAG_COLOR_NORMAL

            for i, y in enumerate(sprite_y_values(c)):
                vdp.set_sprite(i, X[i], y, 0, COLOR[i])
            vdp.set_sprite(DIAG_INDEX, index, DIAG_Y, DIAG_PATTERN, diag_color)

            vdp.render_sprite1(screen)
            c = _next_c(c)

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
