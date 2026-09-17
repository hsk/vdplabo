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

つまり診断用スプライトは常に「1つ前の周で表示されていた配置」に対する
判定結果を表示する1周分の遅延がある。このテストも同じ遅延をモデル化する。

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
import sys

from test_support import add_engine_path, expected_path_for, render_expected_frames, compare_to_expected, write_expected, main  # noqa: E402

add_engine_path(__file__)

from stage4 import V9918  # noqa: E402

EXPECTED_PATH = expected_path_for(__file__, "sc1_sp05.webm")
VIEW_SCALE = 4

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


def test_matches_expected_video():
    # 1周期分(17状態 x WAIT_FRAMES)を実際にSimulationで描画し、
    # 保存済みのexpected動画(../expected/sc1_sp05.webm)とフレームごとに
    # ピクセル単位で完全一致するか比較する。スプライトの位置・色・
    # 背景色・スプライトオーバー時の診断表示(赤/白と番号)まで、
    # 見た目に関わる部分をまとめて検証する本命のテスト。
    actual = render_expected_frames(Simulation, count=STATE_COUNT, wait_frames=WAIT_FRAMES, start_c=C_MIN)
    compare_to_expected(actual, EXPECTED_PATH, V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT, VIEW_SCALE, __file__)


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


def update_expected():
    frames = render_expected_frames(Simulation, count=STATE_COUNT, wait_frames=WAIT_FRAMES, start_c=C_MIN)
    write_expected(frames, EXPECTED_PATH, V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT, VIEW_SCALE)


if __name__ == "__main__":
    main(globals(), show_window, update_expected)
