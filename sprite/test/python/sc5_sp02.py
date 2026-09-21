"""sc5_sp02.asm と同じ「9個のスプライトのY座標を-8〜8で増減させ、
1ラインの表示制限(9個目以降がオーバーフロー)に達すると10個目の診断用スプライトの
X座標にオーバーフローしたスプライト番号が設定され、色も赤くなる」デモを
V9938スプライトモード2(stage4)で再現し、expected動画と比較するテスト。

engine/python/sprite2/stage4.py (V9938 Sprite Mode 2 スキャンライン描画)を使う。

参照:
- ソース: ../asm/sc5_sp02.asm

実行方法:
    python sc5_sp02.py                 # 自動テストのみ実行
    python sc5_sp02.py --show          # pygameウィンドウで目視確認(ループ再生)
    python sc5_sp02.py --update-expected # ../expected/sc5_sp02.webm を再生成
"""
from collections import deque
import pathlib
import sys

from test_support import assert_matches_expected_video, render_and_write_expected, main  # noqa: E402


def add_sprite2_engine_path(caller_file: str) -> None:
    engine_dir = pathlib.Path(caller_file).resolve().parents[2] / "engine" / "python" / "sprite2"
    if str(engine_dir) not in sys.path:
        sys.path.insert(0, str(engine_dir))


add_sprite2_engine_path(__file__)

from stage4 import V9938  # noqa: E402

# sc5_sp02.asm の sprite_init と同じパラメータ
TEST_COUNT = 9
X = [100 + i * 16 for i in range(TEST_COUNT)]
Y_BASE = 100
C_MIN, C_MAX = -8, 8  # c は -8..8 の17値をループする
PERIOD = C_MAX - C_MIN + 1

# 診断用スプライト(10個目, index=9)
DIAG_INDEX = 9
DIAG_Y = 0
DIAG_PATTERN = 0
DIAG_COLOR_OVERFLOW = 8   # 赤
DIAG_COLOR_NORMAL = 15    # 白

# VRAMのパターンネームテーブルを255で埋める = 無地の8x8正方形
SPRITE_PATTERN = [0b11111111] * 8

WAIT_FRAMES = 5  # 5フレーム待ち
STATE_COUNT = PERIOD  # ちょうど1周期分の状態数(c=-8..8)

DIAG_STATUS_LAG = 2


def build_vdp() -> V9938:
    vdp = V9938()
    vdp.set_sprite_pattern(0, SPRITE_PATTERN)
    # sc5_sp02.asm は CHGMOD実行直後にWRTVDPでVDPレジスタ7を直接
    # 4(濃い青)から5(薄い青)へ書き換えている。このタイミングでのR#7書き換えは
    # 実機/C-BIOS上では枠(border)にしか効かず、画面内の背景色(CHGMOD時に
    # VRAMへ焼き込まれたBIOSデフォルトの4)はそのまま変わらない
    # (V9938.set_backdrop_colorのdocstring、sc1_sp01.pyのbuild_vdpと同じ)。
    vdp.set_backdrop_color(5)
    # スプライト拡大
    vdp.set_sprite_mag(True)
    # sc5_sp02.asm の color_init 相当:
    # d = 2 から 10 まで
    # 各スプライトの8バイトカラーテーブル:
    #   2 bytes: color d
    #   4 bytes: color d + 1
    #   2 bytes: color d
    for d in range(2, 11):
        i = d - 2  # 0-indexed sprite index (d=2 -> i=0, ..., d=10 -> i=8)
        colors = [d, d] + [d + 1] * 4 + [d, d]
        vdp.set_sprite_color(i, colors)
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
    """1つの永続的なvdpでc=start_cから順に状態を進めるコア処理。"""

    def __init__(self, start_c: int = C_MIN):
        self.vdp = build_vdp()
        self.c = start_c

        prev_c = self.c
        for _ in range(DIAG_STATUS_LAG):
            prev_c = _prev_c(prev_c)
        for i, y in enumerate(sprite_y_values(prev_c)):
            self.vdp.set_sprite(i, X[i], y, 0, 0)  # color is in color table, set color byte to 0 in SAT
        # DIAG_INDEX: y=0, x=index (0 initially), pattern=0, color=normal/overflow
        self.vdp.set_sprite(DIAG_INDEX, 0, DIAG_Y, DIAG_PATTERN, 0)
        self._5s_log = deque([(False, 31)] * DIAG_STATUS_LAG, maxlen=DIAG_STATUS_LAG)

    def step(self):
        self._5s_log.append((self.vdp.get_5s(), self.vdp.get_5s_index()))
        overflow, index = self._5s_log[0]
        diag_color = DIAG_COLOR_OVERFLOW if overflow else DIAG_COLOR_NORMAL

        for i, y in enumerate(sprite_y_values(self.c)):
            self.vdp.set_sprite(i, X[i], y, 0, 0)
        # sc5_sp02.asm では DIAG_INDEX の x に STATFL の下位5ビット(5S index)が設定される
        self.vdp.set_sprite(DIAG_INDEX, index, DIAG_Y, DIAG_PATTERN, diag_color)

        self.c = _next_c(self.c)
        return overflow, index


def test_c_cycles_through_17_values():
    values = []
    c = C_MIN
    for _ in range(PERIOD + 1):
        values.append(c)
        c = _next_c(c)
    assert values == list(range(C_MIN, C_MAX + 1)) + [C_MIN]


START_C = C_MIN + 1


def test_matches_expected_video():
    assert_matches_expected_video(Simulation, STATE_COUNT, __file__, wait_frames=WAIT_FRAMES, start_c=START_C)


def update_expected():
    render_and_write_expected(Simulation, STATE_COUNT, __file__, wait_frames=WAIT_FRAMES, start_c=START_C)


if __name__ == "__main__":
    main(globals(), Simulation, "sc5_sp02", update_expected=update_expected,
         wait_frames=WAIT_FRAMES, start_c=C_MIN)
