"""sc5_sp04.asm と同じ「2個のスプライトを重ねてColor Code(CC)ビットで
OR合成し、3色を表示する」デモをV9938スプライトモード2(stage4)で再現し、
expected動画と比較するテスト。

engine/python/sprite2/stage4.py (V9938 Sprite Mode 2 スキャンライン描画)を使う。

参照:
- ソース: ../asm/sc5_sp04.asm
- 解説:   ../docs/sc5_sp04.md

sc5_sp04.asmの色設定には実機の仕様に依存した一見不可解な挙動がある:

    ld a, 8 + 1
    ld hl, SPRATR - 0200h        ; カラーテーブル先頭 = スプライト0番の色
    ld bc, 8
    call BIGFIL
    ; 2個目の色
    ld a, 8 + 4 + 0x40
    ld hl, SPRATR - 0200h + 16   ; +16バイト先 = 一見スプライト2番の色に見える
    ld bc, 8
    call BIGFIL

コメントは「2個目の色」だが、オフセットは+8ではなく+16。これは実機の
V9938スプライトモード2のカラーテーブルが、8x8/16x16のサイズ設定に関わらず
1スプライトあたり常に16バイト固定でストライドする仕様のため
(16x16時の16ライン分を格納できるよう確保されており、8x8時は先頭8バイトだけが
使われる)。つまり+16は実際にはスプライト1番(2個目、SATの2番目のエントリ)の
色を指しており、コメントの意図通り正しく2個目のスプライトの色になる
(../expected/sc5_sp04_openmsx.webm を実測して確認済み。
engine側のget_sprite_color_table/set_sprite_colorもこのストライド16バイトで
実装している)。

このテストはさらにパレット(VDPレジスタ16)の書き換えにも依存する。
BIOSデフォルトのパレット0-7はそのままに、8-15だけをpalette_tableの内容
(黒/青/緑/シアン/赤/マゼンタ/黄/白)へ差し替える。スプライトの色番号は
9(=8+1, 青)と12(=8+4, 赤)で、CCビットにより重なった部分は
9 OR 12 = 13(マゼンタ)になる。

実行方法:
    python sc5_sp04.py                 # 自動テストのみ実行
    python sc5_sp04.py --show          # pygameウィンドウで目視確認
    python sc5_sp04.py --update-expected # ../expected/sc5_sp04.webm を再生成
"""
import pathlib
import sys

from test_support import assert_matches_expected_video, render_and_write_expected, render_frame, main  # noqa: E402


def add_sprite2_engine_path(caller_file: str) -> None:
    engine_dir = pathlib.Path(caller_file).resolve().parents[2] / "engine" / "python" / "sprite2"
    if str(engine_dir) not in sys.path:
        sys.path.insert(0, str(engine_dir))


add_sprite2_engine_path(__file__)

from stage4 import V9938  # noqa: E402

# sc5_sp04.asm の palette_table と同じ(パレット番号8-15、R,G,Bは0-7の3bit値)。
# RB 1バイト(上位nibble=R, 下位nibble=B) + G 1バイト(下位nibble=G)を
# (R, G, B)のタプルへ分解してある。
PALETTE_TABLE = {
    8:  (0, 0, 0),   # 黒
    9:  (0, 0, 7),   # 青
    10: (0, 7, 0),   # 緑
    11: (0, 7, 7),   # シアン
    12: (7, 0, 0),   # 赤
    13: (7, 0, 7),   # マゼンタ
    14: (7, 7, 0),   # 黄
    15: (7, 7, 7),   # 白
}

# sc5_sp04.asm の sprite_attr_data と同じ (Y, X, パターン, 色/補足バイトは0)
SPRITE0_X, SPRITE0_Y = 100, 100
SPRITE1_X, SPRITE1_Y = 108, 100
SPRITE_PATTERN_NO = 0

# sprite color: 1個目は 8+1、2個目は 8+4+CC(0x40)
COLOR_CC_BIT = 0x40
SPRITE0_COLOR = 8 + 1
SPRITE1_COLOR = 8 + 4 + COLOR_CC_BIT

# 全ビット1 = 塗りつぶしの8x8正方形
SPRITE_PATTERN = [0b11111111] * 8

# stage4はスプライト属性のYをそのまま使わず、実機のV9918/V9938と同じく
# 表示上のY座標は (属性のY + 1) になる。X側にはこのオフセットは無い。
DISPLAY_Y = SPRITE0_Y + 1


def build_vdp() -> V9938:
    """sc5_sp04.asm の init 相当のセットアップを行う。"""
    vdp = V9938()
    # sc5_sp04.asm は CHGMOD実行直後にWRTVDPでVDPレジスタ7を直接
    # 4(濃い青)から5(薄い青)へ書き換えている。このタイミングでのR#7書き換えは
    # 実機/C-BIOS上では枠(border)にしか効かず、画面内の背景色(CHGMOD時に
    # VRAMへ焼き込まれたBIOSデフォルトの4)はそのまま変わらない
    # (V9938.set_backdrop_colorのdocstring、sc5_sp01.pyのbuild_vdpと同じ)。
    vdp.set_backdrop_color(5)
    # スプライト拡大
    vdp.set_sprite_mag(True)
    # sprite pattern: SPRPATに8バイト(パターン0番)だけBIGFILしている
    vdp.set_sprite_pattern(SPRITE_PATTERN_NO, SPRITE_PATTERN)
    # palette_init: パレット8-15をpalette_tableの内容へ書き換える
    for index, (r, g, b) in PALETTE_TABLE.items():
        vdp.set_palette(index, r, g, b)
    # sprite color: 1個目(スプライト0番)の8バイトカラー領域をSPRITE0_COLORで埋める
    vdp.set_sprite_color(0, [SPRITE0_COLOR] * 8)
    # 「2個目の色」はオフセット+16バイト(カラーテーブルのストライドは16バイト
    # 固定なので、実際にスプライト1番の色になる。ファイル先頭docstring参照)。
    vdp.set_sprite_color(1, [SPRITE1_COLOR] * 8)
    # sprite_attr_data をVRAMへ転送(LDIRVM相当)
    vdp.set_sprite(0, SPRITE0_X, SPRITE0_Y, SPRITE_PATTERN_NO, 0)
    vdp.set_sprite(1, SPRITE1_X, SPRITE1_Y, SPRITE_PATTERN_NO, 0)
    return vdp


class Simulation:
    """静止画なので状態遷移は無いが、他のテストファイルと同じ
    step()インターフェースに合わせてある(test_support.render_expected_frames
    がSimulationクラスだけ渡せば動くようにするため)。
    """

    def __init__(self):
        self.vdp = build_vdp()

    def step(self):
        pass


def test_magnify_is_applied():
    vdp = build_vdp()
    assert vdp.get_sprite_mag() is True


# 画面内(可視領域)の背景色。BIOSデフォルトのまま(BAKCLR=4, 濃い青)。
BACKGROUND_COLOR = V9938.PALETTE[4]
# CHGMOD後にWRTVDPで書き換えた枠(border)の色(5, 薄い青)。
BORDER_COLOR = V9938.PALETTE[5]
# palette_tableで書き換えた後の色(index -> RGB)。RGB_LEVELSの端点(0/7)しか
# 使っていないため、素のRGB値で直接書ける。
BLUE = (0, 0, 255)
RED = (255, 0, 0)
MAGENTA = (255, 0, 255)


def test_background_is_default_blue():
    assert render_frame(Simulation).vdp.get_at(0, 0) == BACKGROUND_COLOR


def test_border_is_light_blue():
    assert render_frame(Simulation).vdp.get_at(-10, -10) == BORDER_COLOR


def test_sprite0_only_area_is_blue():
    # 拡大後のsprite0は画面上x=100-115、sprite1はx=108-123。
    # x=104はsprite0だけが描く領域(重なっていない)。
    assert render_frame(Simulation).vdp.get_at(SPRITE0_X + 4, DISPLAY_Y + 4) == BLUE


def test_sprite1_only_area_is_red():
    # x=120はsprite1だけが描く領域(重なっていない)。
    assert render_frame(Simulation).vdp.get_at(SPRITE1_X + 12, DISPLAY_Y + 4) == RED


def test_overlap_area_is_magenta_via_color_code_or():
    # x=108-115はsprite0とsprite1が重なる領域。sprite1のColor Codeビットにより
    # 色9(青)と色12(赤)がOR合成され、色13(マゼンタ)になる。
    assert render_frame(Simulation).vdp.get_at(SPRITE1_X, DISPLAY_Y + 4) == MAGENTA


def test_matches_expected_video():
    assert_matches_expected_video(Simulation, 1, __file__)


def update_expected():
    render_and_write_expected(Simulation, 1, __file__)


if __name__ == "__main__":
    main(globals(), Simulation, "sc5_sp04", update_expected=update_expected)
