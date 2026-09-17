"""sc1_sp01.asm と同じVRAM設定をエンジンで再現し、描画結果を検証するテスト。

参照:
- ソース: ../asm/sc1_sp01.asm
- 解説:   ../docs/sc1_sp01.md

実行方法:
    python sc1_sp01.py          # 自動テストのみ実行
    python sc1_sp01.py --show   # pygameウィンドウで目視確認
"""
import pathlib
import sys

_ENGINE_SPRITE1 = pathlib.Path(__file__).resolve().parents[2] / "engine" / "python" / "sprite1"
if str(_ENGINE_SPRITE1) not in sys.path:
    sys.path.insert(0, str(_ENGINE_SPRITE1))

from stage1 import V9918  # noqa: E402

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


def build_vdp() -> V9918:
    """sc1_sp01.asm の init 相当のセットアップを行う。

    screen_init は WRTVDP を呼ばずに ret しているため、
    実機と同じくスプライト拡大(sprite_mag)は有効にならない。
    """
    vdp = V9918()
    vdp.set_sprite_pattern(SPRITE_PATTERN_NO, SPRITE_PATTERN)
    vdp.set_sprite(0, SPRITE_X, SPRITE_Y, SPRITE_PATTERN_NO, SPRITE_COLOR)
    return vdp


def render(vdp: V9918):
    import pygame
    pygame.init()
    surface = pygame.Surface((V9918.SCREEN_WIDTH, V9918.SCREEN_HEIGHT))
    vdp.render_sprite1(surface)
    return surface


def test_magnify_is_not_applied():
    vdp = build_vdp()
    assert vdp.sprite_mag is False


def test_background_is_black():
    surface = render(build_vdp())
    assert surface.get_at((0, 0))[:3] == (0, 0, 0)


def test_sprite_top_left_corner_is_background():
    # 1行目のパターン 00111100 の左上2ドットはビットが立っていない
    surface = render(build_vdp())
    assert surface.get_at((SPRITE_X, SPRITE_Y))[:3] == (0, 0, 0)


def test_sprite_center_is_white():
    surface = render(build_vdp())
    assert surface.get_at((SPRITE_X + 4, SPRITE_Y + 4))[:3] == (255, 255, 255)


def test_sprite_left_edge_pixel_is_white():
    # 1行目のパターン 00111100 の3ドット目(0-indexed col=2)はビットが立っている
    surface = render(build_vdp())
    assert surface.get_at((SPRITE_X + 2, SPRITE_Y))[:3] == (255, 255, 255)


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


if __name__ == "__main__":
    if "--show" in sys.argv:
        show_window()
    else:
        sys.exit(0 if _run_all_tests() else 1)
