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
from test_support import add_engine_path, assert_matches_expected_video, render_and_write_expected, main  # noqa: E402

add_engine_path(__file__)

from stage4 import V9918  # noqa: E402

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

# sc1_sp06.asmのinitはsprite_init直後にwait_1sec(60VSYNC)で1秒静止してから
# main_loopに入る(録画開始タイミングの半端なズレではなく、ROM側の意図的な
# 演出なので、キャプチャ側で読み飛ばすのではなくこちらで同じ待ちを
# モデル化する)。実機キャプチャと突き合わせた実測では、このLEAD_IN_FRAMES
# 分だけ静止させた後の最初のstep()でスプライトが画面上に現れ始める
# (frame51目。単純にwait_1secの60を使うと合わず、49が実測値)。
LEAD_IN_FRAMES = 49
FRAME_COUNT = LEAD_IN_FRAMES + 90  # 静止区間 + 全スプライトが静止するまで(c=62)を収める


def build_vdp() -> V9918:
    vdp = V9918()
    for i, pattern in enumerate(SPRITE_PATTERNS):
        vdp.set_sprite_pattern(i, pattern)
    # sc1_sp06.asmのscreen_initもsprite_mag(拡大)ビットを立てている
    vdp.set_sprite_mag(True)
    # sc1_sp06.asm は screen_init 直後に border_color_init を呼び、
    # CHGMOD実行後にWRTVDPでVDPレジスタ7を直接4(濃い青)から5(薄い青)へ
    # 書き換えている。このタイミングでのR#7書き換えは実機/C-BIOS上では
    # 枠(border)にしか効かず、画面内の背景色(CHGMOD時にカラーテーブルへ
    # 焼き込まれたBIOSデフォルトの4)はそのまま変わらない
    # (V9918.set_backdrop_colorのdocstring、sc1_sp01.pyのbuild_vdpと同じ)。
    vdp.set_backdrop_color(5)
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
    """最初のLEAD_IN_FRAMES+1回のstep()は「sprite_init直後、wait_1secで
    静止している間」の初期状態を保ち、それ以降はsprites_moveと同じ
    ロジックでYを1フレーム進める。
    (実機のframe_counterはLEAD_IN_FRAMES分を引いたstep()の呼び出し回数-1
    に対応する)

    vdpと状態だけを持つ状態機械で、surfaceの作成・vdp.render(surface)の
    呼び出しは呼び出し側(test_support)の責務。
    """

    def __init__(self):
        self.vdp = build_vdp()
        self.state = SpriteState()
        self._counter = 0

    def step(self):
        if self._counter > LEAD_IN_FRAMES:
            self.state.advance(self._counter - LEAD_IN_FRAMES)
        for i in range(4):
            self.vdp.set_sprite(i, START_X[i], self.state.y[i], i, COLOR)
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
    assert_matches_expected_video(Simulation, FRAME_COUNT, __file__)


def update_expected():
    render_and_write_expected(Simulation, FRAME_COUNT, __file__)


# sc1_sp06.asmはwait_vsyncのみで毎フレームsprites_moveするので、
# --show もwait_framesデフォルト(1)のまま毎フレームstep()すればよい。
# FRAME_COUNT分で静止したあと、少し見せてからループを再開する。
SHOW_CYCLE_FRAMES = FRAME_COUNT + 210


if __name__ == "__main__":
    main(globals(), Simulation, "sc1_sp06",
         update_expected=update_expected, cycle_frames=SHOW_CYCLE_FRAMES)
