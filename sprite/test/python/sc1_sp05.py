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


class Simulation:
    """1つの永続的なvdpでc=start_cから順に状態を進めるコア処理。

    render_frames() (goldenの生成/比較) と show_window() (目視確認) は
    どちらもこのクラスを共有する。ロジックを2箇所に重複させると片方だけ
    直し忘れる/ズレるということが起きるため、状態遷移はここ1箇所に
    まとめている。ヘッドレスのテストからも同じ`step()`を呼べる。

    main_loop は無限ループでc=-8..8を繰り返すだけなので、周期内であれば
    どのcから始めても「1つ前の状態」は必ず (c-1) (wrap込み) になる
    (cold boot直後の最初の1回だけは前回が未定義になるが、そこは対象外)。
    start_c を変えることで、実機キャプチャがどの位相から始まっていても
    同じ位相から状態列を生成し直せる。
    """

    def __init__(self, start_c: int = C_MIN):
        import pygame

        pygame.init()
        self.vdp = build_vdp()
        self.surface = pygame.Surface((V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT))
        self.c = start_c

        # 定常状態の初期化: 1つ前の周(c-1)の配置を同じvdpで実際に描画しておき、
        # そのときの5S状態を「前回の結果」として引き継がせる
        # (実機は動き続けている1つのVDPなので、毎回作り直したりはしない)
        for i, y in enumerate(sprite_y_values(_prev_c(self.c))):
            self.vdp.set_sprite(i, X[i], y, 0, COLOR[i])
        self.vdp.set_sprite(DIAG_INDEX, 0, 208, 0, 0)
        self.vdp.render_sprite1(self.surface)

    def step(self):
        """次の状態を描画してself.surfaceを更新し、(overflow, index)を返す。

        overflow/indexは今描画したsurfaceに表示されている診断用スプライトの
        値(＝1つ前の配置に対する判定結果)。
        """
        # このvdpが「直前の描画」で記録した5S状態を読む(実機のSTATFL相当)
        overflow, index = self.vdp.get_5s(), self.vdp.get_5s_index()
        diag_color = DIAG_COLOR_OVERFLOW if overflow else DIAG_COLOR_NORMAL

        for i, y in enumerate(sprite_y_values(self.c)):
            self.vdp.set_sprite(i, X[i], y, 0, COLOR[i])
        self.vdp.set_sprite(DIAG_INDEX, index, DIAG_Y, DIAG_PATTERN, diag_color)

        self.vdp.render_sprite1(self.surface)  # 今回の配置の5S状態が新しく記録される
        self.c = _next_c(self.c)
        return overflow, index


def render_frames(state_count: int = STATE_COUNT, start_c: int = C_MIN):
    """各状態を wait_5frame と同じく WAIT_FRAMES 回複製して、
    実機の表示時間(1状態=5 VSYNC)に合わせたフレーム列を返す。
    """
    sim = Simulation(start_c)
    frames = []
    for _ in range(state_count):
        sim.step()
        frame = surface_to_rgb(sim.surface)
        frames.extend([frame] * WAIT_FRAMES)
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


_shared_trace = None  # テスト全体でSimulationを1つだけ作って使い回すためのキャッシュ


def _get_shared_trace():
    """C_MINから順番に1周期分描画していき、各cについて
    「そのcを描画した直後の表示フレーム」を記録する。
    Simulationのインスタンスはこの1回のwalkでしか作らない。
    """
    global _shared_trace
    if _shared_trace is None:
        sim = Simulation(start_c=C_MIN)
        trace = {}
        for _ in range(STATE_COUNT):
            c_used = sim.c  # このstep()でちょうど描画されるcの値
            sim.step()
            trace[c_used] = surface_to_rgb(sim.surface)
        _shared_trace = trace
    return _shared_trace


def test_matches_golden_video():
    if not GOLDEN_PATH.exists():
        raise AssertionError(
            f"golden not found: {GOLDEN_PATH} "
            "(run `python sc1_sp05.py --update-golden` once to create it)"
        )
    trace = _get_shared_trace()
    actual = []
    c = C_MIN
    for _ in range(STATE_COUNT):
        actual.extend([trace[c]] * WAIT_FRAMES)
        c = _next_c(c)

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

    sim = Simulation(C_MIN)
    scale = 3
    window = pygame.display.set_mode(
        (V9918.SCREEN_WIDTH * scale, V9918.SCREEN_HEIGHT * scale)
    )
    pygame.display.set_caption("sc1_sp05")
    clock = pygame.time.Clock()

    frame = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # wait_5frame と同じく、WAIT_FRAMES(5)フレームに1回だけ状態を更新する。
        # 描画とタイマー自体は実機と同じ60FPSのまま回す。
        if frame % WAIT_FRAMES == 0:
            sim.step()

        scaled = pygame.transform.scale(
            sim.surface, (V9918.SCREEN_WIDTH * scale, V9918.SCREEN_HEIGHT * scale)
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
