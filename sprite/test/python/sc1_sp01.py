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
import pathlib
import sys

_ENGINE_SPRITE1 = pathlib.Path(__file__).resolve().parents[2] / "engine" / "python" / "sprite1"
if str(_ENGINE_SPRITE1) not in sys.path:
    sys.path.insert(0, str(_ENGINE_SPRITE1))

from stage4 import V9918  # noqa: E402
from video_golden import save_video, load_video, surface_to_rgb, upscale_nearest, downscale_nearest  # noqa: E402

# test/expected/ はpython実装専用ではなく、将来asm(openMSX)のテストなど
# 別の実装からも同じ正解データとして参照できる共有の置き場所
GOLDEN_PATH = pathlib.Path(__file__).resolve().parents[1] / "expected" / "sc1_sp01.webm"
VIEW_SCALE = 4
GOLDEN_WIDTH = V9918.SCREEN_WIDTH * VIEW_SCALE
GOLDEN_HEIGHT = V9918.SCREEN_HEIGHT * VIEW_SCALE

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
    # BIOSのデフォルト値(BAKCLR=4, 青)がそのまま背景色として残る。
    vdp.set_backdrop_color(4)
    return vdp


def render(vdp: V9918):
    import pygame
    pygame.init()
    surface = pygame.Surface((V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT))
    vdp.render_sprite1(surface)
    return surface


def test_magnify_is_applied():
    vdp = build_vdp()
    assert vdp.get_sprite_mag() is True


# BIOSデフォルト(BAKCLR=4, 青)。openMSXで実測した値(PALETTE[4]と同じ)。
BACKGROUND_COLOR = V9918.PALETTE[4]


def test_background_is_blue():
    surface = render(build_vdp())
    assert surface.get_at((0, 0))[:3] == BACKGROUND_COLOR


def test_sprite_top_left_corner_is_background():
    # 拡大時、画面上のオフセット(0,0)はパターン(row0,col0)に対応する。
    # 1行目のパターン 00111100 の左端(col0)はビットが立っていない
    surface = render(build_vdp())
    assert surface.get_at((SPRITE_X, DISPLAY_Y))[:3] == BACKGROUND_COLOR


def test_sprite_center_is_white():
    # 拡大時、画面上のオフセット(4,4)はパターン(row2,col2)に対応する。
    # 3行目のパターン 11111111 は全ビット立っている
    surface = render(build_vdp())
    assert surface.get_at((SPRITE_X + 4, DISPLAY_Y + 4))[:3] == (255, 255, 255)


def test_sprite_top_edge_is_white():
    # 拡大時、画面上のオフセット(4,0)はパターン(row0,col2)に対応する。
    # 1行目のパターン 00111100 の3ビット目(0-indexed col=2)はビットが立っている
    surface = render(build_vdp())
    assert surface.get_at((SPRITE_X + 4, DISPLAY_Y))[:3] == (255, 255, 255)


def test_magnified_footprint_extends_beyond_8x8():
    # 拡大により footprint は 16x16 になる。オフセット(12,12)は
    # 非拡大の8x8スプライトなら絶対に届かない範囲で、
    # パターン(row6,col6)=01111110のcol6ビットが立っているため白になるはず。
    # これが白ければ拡大が実際に効いている証拠になる。
    surface = render(build_vdp())
    assert surface.get_at((SPRITE_X + 12, DISPLAY_Y + 12))[:3] == (255, 255, 255)


def test_matches_golden_video():
    if not GOLDEN_PATH.exists():
        raise AssertionError(
            f"golden not found: {GOLDEN_PATH} "
            "(run `python sc1_sp01.py --update-expected` once to create it)"
        )
    actual = surface_to_rgb(render(build_vdp()))  # 実寸(256x192)のまま比較する
    golden_frames = load_video(GOLDEN_PATH, GOLDEN_WIDTH, GOLDEN_HEIGHT)
    assert len(golden_frames) == 1, f"golden should have exactly 1 frame, got {len(golden_frames)}"
    expected = downscale_nearest(golden_frames[0], V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT, VIEW_SCALE)
    assert actual == expected, "frame differs from golden"


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


def show_window():
    """目視確認用: pygameウィンドウにスプライトを表示する。"""
    import pygame

    pygame.init()
    vdp = build_vdp()
    scale = 3
    window = pygame.display.set_mode(
        (V9918.SCREEN_WIDTH * scale, V9918.SCREEN_HEIGHT * scale)
    )
    pygame.display.set_caption("sc1_sp01")
    screen = pygame.Surface((V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        vdp.render_sprite1(screen)
        scaled = pygame.transform.scale(
            screen, (V9918.SCREEN_WIDTH * scale, V9918.SCREEN_HEIGHT * scale)
        )
        window.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(60)


def update_expected():
    frame = surface_to_rgb(render(build_vdp()))
    scaled = upscale_nearest(frame, V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT, VIEW_SCALE)
    GOLDEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_video([scaled], GOLDEN_WIDTH, GOLDEN_HEIGHT, GOLDEN_PATH)
    print(f"wrote {GOLDEN_PATH} ({GOLDEN_WIDTH}x{GOLDEN_HEIGHT}, 1 frame)")


if __name__ == "__main__":
    if "--show" in sys.argv:
        show_window()
    elif "--update-expected" in sys.argv:
        update_expected()
    else:
        sys.exit(0 if _run_all_tests() else 1)
