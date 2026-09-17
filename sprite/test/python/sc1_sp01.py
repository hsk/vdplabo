"""sc1_sp01.asm と同じVRAM設定をエンジンで再現し、描画結果を検証するテスト。

engine/python/sprite1/stage4.py (レジスタ駆動・スキャンライン描画で
実機に近い挙動)を使用する。stage4は表示上のY座標が
(スプライト属性のY + 1)になる実機通りの仕様なので、DISPLAY_Y定数で
その分のオフセットを吸収している。

PALETTEと背景色(R#7)はopenMSXで実測した値を使っており、
../expected/sc1_sp01_openmsx.webm (実機キャプチャ)とビット完全一致する
ことを目指している(../asm/probe_palette.py 参照)。

参照:
- ソース: ../asm/sc1_sp01.asm
- 解説:   ../docs/sc1_sp01.md

実行方法:
    python sc1_sp01.py                 # 自動テストのみ実行
    python sc1_sp01.py --show          # pygameウィンドウで目視確認
    python sc1_sp01.py --update-expected # ../expected/sc1_sp01.webm を再生成
"""
from test_support import add_engine_path, assert_matches_expected_video, render_and_write_expected, render_frame, main  # noqa: E402

add_engine_path(__file__)

from stage4 import V9918  # noqa: E402

# sc1_sp01.asm の sprite_pattern_data と同じ8バイト
SPRITE_PATTERN = [
    0b00111100,
    0b01111110,
    0b11111111,
    0b11111111,
    0b11111111,
    0b11111111,
    0b01111110,
    0b00111100,
]

# sc1_sp01.asm の sprite_attr_data と同じ (Y, X, パターン, 色)
SPRITE_X = 100
SPRITE_Y = 100
SPRITE_PATTERN_NO = 0
SPRITE_COLOR = 15  # 白

# stage4はスプライト属性のYをそのまま使わず、実機のV9918と同じく
# 表示上のY座標は (属性のY + 1) になる。X側にはこのオフセットは無い。
DISPLAY_Y = SPRITE_Y + 1


def build_vdp() -> V9918:
    """sc1_sp01.asm の init 相当のセットアップを行う。

    screen_init 自体は WRTVDP を呼ばずに ret しているが、
    次の pattern_name_table_init の先頭が call WRTVDP になっており、
    ret/call はBCレジスタを壊さないため screen_init が用意した
    B(拡大ビット付きの値)・C(VDPレジスタ1番)がそのまま使われる。
    つまり実機ではスプライト拡大(sprite_mag)は有効になる。
    """
    vdp = V9918()
    vdp.set_sprite_pattern(SPRITE_PATTERN_NO, SPRITE_PATTERN)
    vdp.set_sprite(0, SPRITE_X, SPRITE_Y, SPRITE_PATTERN_NO, SPRITE_COLOR)
    vdp.set_sprite_mag(True)
    # sc1_sp01.asm はVDPレジスタ7(背景色)を書き換えていないため、
    # BIOSのデフォルト値(BAKCLR=4, 青)がそのまま背景色として残る
    # (V9918のコンストラクタ自体がBIOSデフォルトの4で初期化するので、
    # ここで明示的に呼ぶ必要は無い)。
    return vdp


class Simulation:
    """静止画なので状態遷移は無いが、他のテストファイルと同じ
    step()インターフェースに合わせてある(test_support.render_expected_frames
    がSimulationクラスだけ渡せば動くようにするため)。surfaceの作成・renderの
    呼び出しは呼び出し側(test_support)の責務なのでここでは持たない。
    """

    def __init__(self):
        self.vdp = build_vdp()

    def step(self):
        pass


def test_magnify_is_applied():
    vdp = build_vdp()
    assert vdp.get_sprite_mag() is True


# BIOSデフォルト(BAKCLR=4, 青)。openMSXで実測した値(PALETTE[4]と同じ)。
BACKGROUND_COLOR = V9918.PALETTE[4]


def test_background_is_blue():
    assert render_frame(Simulation).vdp.get_at(0, 0) == BACKGROUND_COLOR


def test_sprite_top_left_corner_is_background():
    # 拡大時、画面上のオフセット(0,0)はパターン(row0,col0)に対応する。
    # 1行目のパターン 00111100 の左端(col0)はビットが立っていない
    assert render_frame(Simulation).vdp.get_at(SPRITE_X, DISPLAY_Y) == BACKGROUND_COLOR


def test_sprite_center_is_white():
    # 拡大時、画面上のオフセット(4,4)はパターン(row2,col2)に対応する。
    # 3行目のパターン 11111111 は全ビット立っている
    assert render_frame(Simulation).vdp.get_at(SPRITE_X + 4, DISPLAY_Y + 4) == (255, 255, 255)


def test_sprite_top_edge_is_white():
    # 拡大時、画面上のオフセット(4,0)はパターン(row0,col2)に対応する。
    # 1行目のパターン 00111100 の3ビット目(0-indexed col=2)はビットが立っている
    assert render_frame(Simulation).vdp.get_at(SPRITE_X + 4, DISPLAY_Y) == (255, 255, 255)


def test_magnified_footprint_extends_beyond_8x8():
    # 拡大により footprint は 16x16 になる。オフセット(12,12)は
    # 非拡大の8x8スプライトなら絶対に届かない範囲で、
    # パターン(row6,col6)=01111110のcol6ビットが立っているため白になるはず。
    # これが白ければ拡大が実際に効いている証拠になる。
    assert render_frame(Simulation).vdp.get_at(SPRITE_X + 12, DISPLAY_Y + 12) == (255, 255, 255)


def test_matches_expected_video():
    assert_matches_expected_video(Simulation, 1, __file__)


def update_expected():
    render_and_write_expected(Simulation, 1, __file__)


if __name__ == "__main__":
    main(globals(), Simulation, "sc1_sp01", update_expected=update_expected)
