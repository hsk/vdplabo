"""sc5_sp05.asm と同じ「3個のスプライトを重ねてColor Code(CC)ビットでOR合成し、
7色+透明を表示する」デモをV9938スプライトモード2(stage4)で再現し、
expected動画と比較するテスト。

engine/python/sprite2/stage4.py (V9938 Sprite Mode 2 スキャンライン描画)を使う。

参照:
- ソース: ../asm/sc5_sp05.asm
- 解説:   ../docs/sc5_sp05.md (背景色/CCの単独表示可否についてはopenMSX実機
  キャプチャの実測の方を優先している。以下のdocstring参照)

## 背景色・枠色について

sc5_sp05.asmはCHGMOD実行"前"にワークエリアFORCLR/BAKCLR/BDRCLRへ
15/1/5を書き込み、CHGCLRを呼んでからCHGMODでSCREEN5へ切り替えている
(sc5_sp01〜04のようなCHGMOD後のWRTVDP直書きではない)。実機ではCHGMOD
実行時にBAKCLRワークエリアの値が画面内背景として焼き込まれる
(V9938.set_backdrop_colorのdocstring参照)ため、この順序でBAKCLR=1を
仕込むと画面内背景がBIOSデフォルトの4ではなく1(黒)になる。同様に
枠色もBDRCLR=5がCHGMOD時に反映される。実機キャプチャ
(../expected/sc5_sp05_openmsx.webm)で背景が黒(0,0,0)・枠が薄い青
(81,118,255、デフォルトパレット5番)になっていることを実測して確認済み。

## Color Codeビットの「そのラインに前のスプライトが無いと表示されない」仕様

sc5_sp04.asmでは2枚のスプライトのY座標が完全に一致していたため気づけなかったが、
sc5_sp05.asmは3枚のY座標がずらしてあり(0番:100, 1番:106, 2番:94)、
CCビットが立ったスプライト(1番・2番)が「他のスプライトと重ならない
単独範囲」を持つ。実機キャプチャを実測すると、

- 2番(Y=94, 最も上)が単独で乗るライン(0番も1番もまだ登場していないY)は
  完全に非表示(背景色のまま)
- 2番が0番と同じライン(Xは重ならなくてもよい)に乗ると、2番はそのライン全体で
  自分の色(赤)がソロ表示される
- 1番(Y=106, 最も下)が単独で乗るライン(0番が既に終わっている・2番も
  終わっているY)も完全に非表示

という結果になる。つまりCCビット付きスプライトは、「同じライン上に
(Xの重なりは問わず)自分より小さいindexのスプライトが存在するかどうか」で
そのライン全体の表示可否が決まる、という実機のColor Code仕様がある
(engine/python/sprite2/stage4.py render_line_sprites の has_prior_sprite 参照。
このテストを追加する過程でこの仕様の欠落に気づき、エンジン側を修正した)。

実行方法:
    python sc5_sp05.py                 # 自動テストのみ実行
    python sc5_sp05.py --show          # pygameウィンドウで目視確認
    python sc5_sp05.py --update-expected # ../expected/sc5_sp05.webm を再生成
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

# sc5_sp05.asm の palette_table と同じ(sc5_sp04.asmと同じ値)。
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

# CHGMOD前にワークエリアへ書き込む色(FORCLR/BAKCLR/BDRCLR)。
FORCLR = 15
BAKCLR = 1
BDRCLR = 5

# sc5_sp05.asm の sprite_attr_data と同じ (Y, X, パターン=0, 補足バイト=0)
SPRITE0_X, SPRITE0_Y = 100, 100
SPRITE1_X, SPRITE1_Y = 108, 106
SPRITE2_X, SPRITE2_Y = 108, 100 - 6  # 94
SPRITE_PATTERN_NO = 0

COLOR_CC_BIT = 0x40
SPRITE0_COLOR = 8 + 1                  # 9  青、通常色(CCなし)
SPRITE1_COLOR = 8 + 2 + COLOR_CC_BIT   # 0x4A  緑、CCあり
SPRITE2_COLOR = 8 + 4 + COLOR_CC_BIT   # 0x4C  赤、CCあり

# 全ビット1 = 塗りつぶしの8x8正方形
SPRITE_PATTERN = [0b11111111] * 8

# stage4はスプライト属性のYをそのまま使わず、実機のV9918/V9938と同じく
# 表示上のY座標は (属性のY + 1) になる。X側にはこのオフセットは無い。
DISPLAY_Y0 = SPRITE0_Y + 1
DISPLAY_Y1 = SPRITE1_Y + 1
DISPLAY_Y2 = SPRITE2_Y + 1


def build_vdp() -> V9938:
    """sc5_sp05.asm の init 相当のセットアップを行う。"""
    vdp = V9938()
    # FORCLR/BAKCLR/BDRCLRワークエリア + CHGCLR + CHGMODの効果
    # (ファイル先頭docstring参照)。
    vdp.set_screen_background_color(BAKCLR)
    vdp.set_backdrop_color(BDRCLR)
    # スプライト拡大
    vdp.set_sprite_mag(True)
    # sprite pattern: SPRPATに8バイト(パターン0番)だけBIGFILしている
    vdp.set_sprite_pattern(SPRITE_PATTERN_NO, SPRITE_PATTERN)
    # palette_init: パレット8-15をpalette_tableの内容へ書き換える
    for index, (r, g, b) in PALETTE_TABLE.items():
        vdp.set_palette(index, r, g, b)
    # sprite color: 1〜3個目それぞれのカラーテーブル領域(16バイトストライド)を
    # 埋める。sc5_sp04.asmと違い、このROMは 0/16*1/16*2 と素直にindex通りの
    # オフセットを使っているため、set_sprite_colorへそのまま渡せば良い。
    vdp.set_sprite_color(0, [SPRITE0_COLOR] * 8)
    vdp.set_sprite_color(1, [SPRITE1_COLOR] * 8)
    vdp.set_sprite_color(2, [SPRITE2_COLOR] * 8)
    # sprite_attr_data をVRAMへ転送(LDIRVM相当)
    vdp.set_sprite(0, SPRITE0_X, SPRITE0_Y, SPRITE_PATTERN_NO, 0)
    vdp.set_sprite(1, SPRITE1_X, SPRITE1_Y, SPRITE_PATTERN_NO, 0)
    vdp.set_sprite(2, SPRITE2_X, SPRITE2_Y, SPRITE_PATTERN_NO, 0)
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


# BAKCLR=1(黒)がCHGMOD時に画面内背景へ焼き込まれる。
BACKGROUND_COLOR = V9938.PALETTE[BAKCLR]
# BDRCLR=5(薄い青)がCHGMOD時に枠へ反映される。
BORDER_COLOR = V9938.PALETTE[BDRCLR]

BLUE = (0, 0, 255)     # 色9
GREEN = (0, 255, 0)    # 色10
RED = (255, 0, 0)      # 色12
CYAN = (0, 255, 255)   # 9 OR 10
MAGENTA = (255, 0, 255)  # 9 OR 12
YELLOW = (255, 255, 0)   # 10 OR 12
WHITE = (255, 255, 255)  # 9 OR 10 OR 12


def test_background_is_black():
    assert render_frame(Simulation).vdp.get_at(0, 0) == BACKGROUND_COLOR


def test_border_is_light_blue():
    assert render_frame(Simulation).vdp.get_at(-10, -10) == BORDER_COLOR


def test_sprite0_only_area_is_blue():
    # sprite0(x100-115,y101-116)だけの領域。
    assert render_frame(Simulation).vdp.get_at(SPRITE0_X + 2, DISPLAY_Y0 + 2) == BLUE


def test_sprite0_and_sprite2_overlap_is_magenta():
    # sprite0(青,9)とsprite2(赤,12)が重なる領域(x108-115, y101-106): 9 OR 12 = 13
    assert render_frame(Simulation).vdp.get_at(SPRITE2_X, DISPLAY_Y0 + 2) == MAGENTA


def test_all_three_overlap_is_white():
    # sprite0・sprite1・sprite2すべてが重なる領域(x108-115, y107-110): 9 OR 10 OR 12 = 15
    assert render_frame(Simulation).vdp.get_at(SPRITE1_X, DISPLAY_Y1 + 1) == WHITE


def test_sprite1_and_sprite2_overlap_without_sprite0_is_yellow():
    # sprite1(緑,10)とsprite2(赤,12)が重なるがsprite0(x100-115)は届かない
    # 領域(x116-123, y107-110): 10 OR 12 = 14
    assert render_frame(Simulation).vdp.get_at(SPRITE1_X + 8, DISPLAY_Y1 + 1) == YELLOW


def test_sprite0_and_sprite1_overlap_without_sprite2_is_cyan():
    # sprite2は既に終わっている(y>110)が、sprite0とsprite1が重なる
    # 領域(x108-115, y111-116): 9 OR 10 = 11
    assert render_frame(Simulation).vdp.get_at(SPRITE1_X, DISPLAY_Y0 + 12) == CYAN


def test_sprite1_solo_is_visible_when_sprite0_shares_the_line():
    # sprite0がまだ同じラインに乗っている間(y111-116)のsprite1単独領域
    # (x116-123)は、Xが重ならなくてもソロ表示される。
    assert render_frame(Simulation).vdp.get_at(SPRITE1_X + 8, DISPLAY_Y0 + 12) == GREEN


def test_sprite2_solo_is_hidden_before_sprite0_starts():
    # sprite2(y95-110)がsprite0(y101-)より前に始まる範囲(y95-100)では、
    # 同じライン上に自分より小さいindexのスプライトが1つも無いため、
    # CCビットにより単独でも一切表示されない(実機仕様。ファイル先頭docstring参照)。
    assert render_frame(Simulation).vdp.get_at(SPRITE2_X + 4, DISPLAY_Y2 + 2) == BACKGROUND_COLOR


def test_sprite1_solo_is_hidden_after_sprite0_ends():
    # sprite1(y107-122)がsprite0(-116)より後まで続く範囲(y117-122)では、
    # 同じライン上に自分より小さいindexのスプライトが無いため、
    # CCビットにより単独でも一切表示されない。
    assert render_frame(Simulation).vdp.get_at(SPRITE1_X + 8, DISPLAY_Y1 + 12) == BACKGROUND_COLOR


def test_matches_expected_video():
    assert_matches_expected_video(Simulation, 1, __file__)


def update_expected():
    render_and_write_expected(Simulation, 1, __file__)


if __name__ == "__main__":
    main(globals(), Simulation, "sc5_sp05", update_expected=update_expected)
