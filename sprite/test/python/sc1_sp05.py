"""sc1_sp05.asm と同じ「9個のスプライトのY座標を-8〜8で増減させ、
1ラインの表示制限(5個以上)に達すると10個目の診断用スプライトが
赤くなる」デモをエンジンで再現し、expected動画と比較するテスト。

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

ソースコード上は「1つ前の周で表示されていた配置」に対する判定結果に
見えるが、実機キャプチャと突き合わせた実測では2周分(DIAG_STATUS_LAG)の
遅延があった。stage4エンジンのrender()はrender()を呼ぶたびに全スプライトを
スキャンして5Sフラグを再計算する(実機のSTATFLのように「読むまで保持」
される訳ではない)ため、素朴に「直前のrender()の結果」を使うだけでは
実機の遅延を1周分再現しきれない。このテストはこの実測値(2周)を
モデル化する。

main_loop は無限ループでc=-8..8(17状態)を繰り返すだけなので、定常状態
(cold boot直後の最初の1回を除く)では「1つ前の状態」は必ず周期内の
1つ前の値になる。これは近似ではなく、ループが回り続けている限り厳密に
成り立つ関係なので、どの位相(どのcの値)から録画を始めても正しく
フレーム列を再構成できる(Simulation の start_c 引数)。

PALETTEと背景色(R#7)はopenMSXで実測した値を使っており、
../expected/sc1_sp05_openmsx.webm (実機キャプチャ)と位相さえ合わせれば
ビット完全一致することを目指している。

参照:
- ソース: ../asm/sc1_sp05.asm
- 解説:   ../docs/sc1_sp05.md

実行方法:
    python sc1_sp05.py                 # 自動テストのみ実行
    python sc1_sp05.py --show          # pygameウィンドウで目視確認(ループ再生)
    python sc1_sp05.py --update-expected # ../expected/sc1_sp05.webm を再生成
"""
from collections import deque

from test_support import add_engine_path, assert_matches_expected_video, render_and_write_expected, main  # noqa: E402

add_engine_path(__file__)

from stage4 import V9918  # noqa: E402

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

# 診断スプライトの5S判定(get_5s/get_5s_index)は、設計上「1つ前の周に
# 表示されていた配置」を反映する(main_loopのコメント参照)はずだったが、
# 実機キャプチャと突き合わせたところ、実際には2周分遅れて反映されていた
# (実測値。c=-2で赤くなるのはPython版の予測ではframe26だが、実機は
# frame31。ちょうどWAIT_FRAMES分=1周分だけ実機の方が遅い)。
# stage4.render()はrender()呼び出しごとに全32スプライトを毎回スキャンして
# 5Sフラグを再計算する(実機のSTATFLのように「読むまで保持」ではない)ため、
# 単純に「直前のrender()の結果を使う」だけでは1周分足りなかったと考えられる。
DIAG_STATUS_LAG = 2


def build_vdp() -> V9918:
    vdp = V9918()
    vdp.set_sprite_pattern(0, SPRITE_PATTERN)
    vdp.set_sprite_mag(True)
    # sc1_sp05.asm は border_color_init で、CHGMOD実行後にWRTVDPで
    # VDPレジスタ7を直接4(濃い青)から5(薄い青)へ書き換えている。
    # このタイミングでのR#7書き換えは実機/C-BIOS上では枠(border)にしか
    # 効かず、画面内の背景色(CHGMOD時にカラーテーブルへ焼き込まれた
    # BIOSデフォルトの4)はそのまま変わらない(V9918.set_backdrop_colorの
    # docstring、sc1_sp01.pyのbuild_vdpと同じ)。
    vdp.set_backdrop_color(5)
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

    main_loop は無限ループでc=-8..8を繰り返すだけなので、周期内であれば
    どのcから始めても「1つ前の状態」は必ず (c-1) (wrap込み) になる
    (cold boot直後の最初の1回だけは前回が未定義になるが、そこは対象外)。
    start_c を変えることで、実機キャプチャがどの位相から始まっていても
    同じ位相から状態列を生成し直せる。

    vdpと状態(c)だけを持つ状態機械で、surfaceの作成・vdp.render(surface)の
    呼び出しは呼び出し側(test_support)の責務。そのためstep()は5S判定に
    使う「前回のrender()結果」に依存する(呼び出し側は構築直後に一度
    render()してから、step()のたびにrender()し直す想定)。
    """

    def __init__(self, start_c: int = C_MIN):
        self.vdp = build_vdp()
        self.c = start_c

        # 定常状態の初期化: DIAG_STATUS_LAG周前の配置をVRAMに書いておく。
        # 呼び出し側がこの直後に一度render()することで、そのときの5S状態が
        # 「DIAG_STATUS_LAG周前の結果」の1つとして最初のstep()に引き継がれる
        # (実機は動き続けている1つのVDPなので、毎回作り直したりはしない)。
        prev_c = self.c
        for _ in range(DIAG_STATUS_LAG):
            prev_c = _prev_c(prev_c)
        for i, y in enumerate(sprite_y_values(prev_c)):
            self.vdp.set_sprite(i, X[i], y, 0, COLOR[i])
        self.vdp.set_sprite(DIAG_INDEX, 0, 208, 0, 0)
        # DIAG_STATUS_LAG回分の初期履歴("overflowなし")を積んでおく
        self._5s_log = deque([(False, 31)] * DIAG_STATUS_LAG, maxlen=DIAG_STATUS_LAG)

    def step(self):
        """次の状態のVRAM/レジスタを更新する(overflow, index)を返す。

        overflow/indexはDIAG_STATUS_LAG周前のrender()で記録された5S状態。
        呼び出し側はstep()のたびにrender()し直すことで、そのつどの5S状態が
        ログに積まれ、DIAG_STATUS_LAG周後のstep()で読めるようになる。
        """
        # このvdpが直近のrender()で記録した5S状態をログに積み、
        # DIAG_STATUS_LAG周前の値を取り出す(実機のSTATFL相当)
        self._5s_log.append((self.vdp.get_5s(), self.vdp.get_5s_index()))
        overflow, index = self._5s_log[0]
        diag_color = DIAG_COLOR_OVERFLOW if overflow else DIAG_COLOR_NORMAL

        for i, y in enumerate(sprite_y_values(self.c)):
            self.vdp.set_sprite(i, X[i], y, 0, COLOR[i])
        self.vdp.set_sprite(DIAG_INDEX, index, DIAG_Y, DIAG_PATTERN, diag_color)

        self.c = _next_c(self.c)
        return overflow, index


def test_c_cycles_through_17_values():
    # VDP/Simulationは一切使わない純粋なロジックテスト。_next_c()が
    # C_MIN(-8)からC_MAX(8)まで17値を順に進み、その次でまたC_MINに
    # 折り返すことだけを確認する。
    values = []
    c = C_MIN
    for _ in range(PERIOD + 1):
        values.append(c)
        c = _next_c(c)
    assert values == list(range(C_MIN, C_MAX + 1)) + [C_MIN]


# ../asm/Makefileの`make capture_sc1_sp05`/`cap_test_sc1_sp05`は
# --settle 0.166667(10フレーム)でopenMSXの録画を開始するよう固定している
# (デフォルトの0.2秒=12フレームだと、このROMのWAIT_FRAMES=5周期の境界と
# 噛み合わず、録画開始が状態の途中になってしまうため。実測でc=C_MIN+1の
# 状態(2番目の周回)の開始ちょうどに来ることを確認済み)。start_cはその
# 録画開始位置に合わせている。
START_C = C_MIN + 1


def test_matches_expected_video():
    # 1周期分(17状態 x WAIT_FRAMES)を実際にSimulationで描画し、
    # 保存済みのexpected動画(../expected/sc1_sp05.webm)とフレームごとに
    # ピクセル単位で完全一致するか比較する。スプライトの位置・色・
    # 背景色・スプライトオーバー時の診断表示(赤/白と番号)まで、
    # 見た目に関わる部分をまとめて検証する本命のテスト。
    assert_matches_expected_video(Simulation, STATE_COUNT, __file__, wait_frames=WAIT_FRAMES, start_c=START_C)


def update_expected():
    render_and_write_expected(Simulation, STATE_COUNT, __file__, wait_frames=WAIT_FRAMES, start_c=START_C)


if __name__ == "__main__":
    # --show は60FPSで描画するが、wait_5frameと同じくstep()はWAIT_FRAMES
    # フレームに1回だけ呼ぶ(test_support.show_windowのwait_frames)。
    main(globals(), Simulation, "sc1_sp05", update_expected=update_expected,
         wait_frames=WAIT_FRAMES, start_c=C_MIN)
