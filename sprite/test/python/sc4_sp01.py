"""sc4_sp01.asm と同じ「9個のスプライトのY座標を-8〜8で増減させ、
1ラインの表示制限(9個目以降がオーバーフロー)に達すると10個目の診断用スプライトが
赤くなる」デモをV9938スプライトモード2(stage4)で再現し、
expected動画と比較するテスト。

engine/python/sprite2/stage4.py (V9938 Sprite Mode 2 スキャンライン描画)を使う。

参照:
- ソース: ../asm/sc4_sp01.asm

実行方法:
    python sc4_sp01.py                 # 自動テストのみ実行
    python sc4_sp01.py --show          # pygameウィンドウで目視確認(ループ再生)
    python sc4_sp01.py --update-expected # ../expected/sc4_sp01.webm を再生成
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

# sc4_sp01.asm の sprite_init と同じパラメータ
TEST_COUNT = 9
X = [100 + i * 16 for i in range(TEST_COUNT)]
# sc4_sp01.asm では color_init で d=1..10 の色が各スプライトに設定される (SATの4バイト目の色)
# color_init: ld a, d ... color_init
COLOR = [d for d in range(1, TEST_COUNT + 1)]
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
    # sc4_sp01.asm は SCREEN4(GRAPHIC3)。SCREEN5-8と違いR#9のLNビットが立たず
    # 192ライン表示のまま(stage4.V9938のクラスコメント参照)。
    vdp = V9938(screen_height=192)
    vdp.set_sprite_pattern(0, SPRITE_PATTERN)
    # sc4_sp01.asm は CHGMOD実行直後にWRTVDPでVDPレジスタ7を直接
    # 4(濃い青)から5(薄い青)へ書き換えている。このタイミングでのR#7書き換えは
    # 実機/C-BIOS上では枠(border)にしか効かず、画面内の背景色(CHGMOD時に
    # VRAMへ焼き込まれたBIOSデフォルトの4)はそのまま変わらない
    # (V9938.set_backdrop_colorのdocstring、sc1_sp01.pyのbuild_vdpと同じ)。
    vdp.set_backdrop_color(5)
    # スプライト拡大
    vdp.set_sprite_mag(True)
    # 各スプライトの色を設定 (Sprite Mode 2 ではカラーテーブルに設定する)
    # asm側: SPRATR - 0200h がカラーテーブル位置 (SAT - 512)
    for i, c in enumerate(COLOR):
        vdp.set_sprite_color(i, [c] * 8)
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
            self.vdp.set_sprite(i, X[i], y, 0, COLOR[i])
        self.vdp.set_sprite(DIAG_INDEX, 0, 208, 0, 0)
        self.vdp.set_sprite(DIAG_INDEX+1, 0, 216, 0, 0)

    def step(self):
        overflow, index = (self.vdp.get_5s(), self.vdp.get_5s_index())
        diag_color = DIAG_COLOR_OVERFLOW if overflow else DIAG_COLOR_NORMAL

        for i, y in enumerate(sprite_y_values(self.c)):
            self.vdp.set_sprite(i, X[i], y, 0, COLOR[i])
        self.vdp.set_sprite(DIAG_INDEX, index, DIAG_Y, 0, 0)
        self.vdp.set_sprite_color(DIAG_INDEX, [diag_color] * 8)

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
    main(globals(), Simulation, "sc4_sp01", update_expected=update_expected,
         wait_frames=WAIT_FRAMES, start_c=START_C)
