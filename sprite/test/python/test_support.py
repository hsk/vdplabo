"""sc1_sp01.py / sc1_sp05.py / sc1_sp06.py で共通のテスト基盤。

VDP/エンジンのロジックには一切関与しない(そちらは各テストファイル自身の
責務)。webmの読み書き自体は video_expected.py の責務で、このモジュールは
その上に乗る「テストファイルの土台(sys.path設定・比較・保存・実行)」を
まとめたもの。

各テストファイルのSimulationクラスは self.vdp と状態だけを持つ純粋な
状態機械で、surfaceの作成・vdp.render(surface)の呼び出し・表示ペースの
間引きはすべてここ(呼び出し元)が担当する。

SCREEN_WIDTH/HEIGHTはopenMSXの生キャプチャに合わせたキャンバス全体
(320x240, 可視領域256x192の周囲に枠が付いた状態)。可視領域だけを
決め打ちでクロップせず枠込みで比較することで、SCREEN5以降の可変な
可視領域(256x212など)や枠色(BDRCLR)の違いも同じ比較ロジックで
扱える(sprite1/sprite2エンジン側のCANVAS_WIDTH/HEIGHTと合わせてある。
engine/python/sprite{1,2}/stage4.py参照)。
"""
import pathlib
import sys

from video_expected import load_video, save_video, downscale_nearest, upscale_nearest, surface_to_rgb

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240

# expected webm保存時のニアレストネイバー拡大倍率(全テストファイル共通)。
# ../asm/capture_openmsx.pyの--scaleのデフォルトもこれに合わせてある。
# 3倍も検討したが、SCREEN6/7(512ドット幅モード)を将来サポートすると
# 320x240キャンバスの2倍(640)がその実解像度と一致しキリが良いため、
# 2倍(640x480)にしている。
EXPECTED_SCALE = 2

# ../asm/capture_openmsx.pyのデフォルト録画秒数(DEFAULT_DURATION=2.0) x FPS(60)。
# sc1_sp01のような静止画面テストはcount=1(1フレームのみ)で足りるが、それだと
# 実機キャプチャ(最低この秒数だけ録画される。../asm/README.md参照)とフレーム数が
# 合わず../asm/compare_webm.pyでの比較ができない。そのためrender_expected_frames
# 側で末尾フレームを複製してこの長さまで底上げする。
MIN_EXPECTED_FRAMES = 120


def add_engine_path(caller_file: str) -> None:
    """呼び出し元ファイルから見た engine/python/sprite1 をsys.pathに追加する。"""
    engine_dir = pathlib.Path(caller_file).resolve().parents[2] / "engine" / "python" / "sprite1"
    if str(engine_dir) not in sys.path:
        sys.path.insert(0, str(engine_dir))


def expected_path_for(caller_file: str, name: str) -> pathlib.Path:
    """呼び出し元ファイルから見た ../expected/<name> のパスを返す。

    test/expected/ はpython実装専用ではなく、将来asm(openMSX)のテストなど
    別の実装からも同じ正解データとして参照できる共有の置き場所。
    """
    return pathlib.Path(caller_file).resolve().parents[1] / "expected" / name


def make_surface(width: int, height: int):
    """pygame.init()した上でpygame.Surface((width, height))を返す。

    各テストファイルのSimulation.__init__がpygameを直接importしなくて
    済むようにするためのラッパー(pygameへの依存をtest_supportに閉じ込める)。
    """
    import pygame

    pygame.init()
    return pygame.Surface((width, height))


def render_frame(simulation_cls, count: int = 1, **kwargs):
    """simulation_cls(**kwargs)を作り、countステップ進めてrenderしたsimを返す。

    呼び出し側は sim.vdp.get_at(x, y) でピクセルを確認できる
    (Simulationはsurfaceを持たないので、pygame.Surfaceを直接触る必要が無い)。
    1フレームだけ見てassertする単発テストの本体を1行で書けるようにするため。
    """
    sim = simulation_cls(**kwargs)
    surface = make_surface(SCREEN_WIDTH, SCREEN_HEIGHT)
    sim.vdp.render(surface)  # 初期状態をrenderしておく(前回状態への依存に対応)
    for _ in range(count):
        sim.step()
        sim.vdp.render(surface)
    return sim


def render_expected_frames(simulation_cls, count: int, wait_frames: int = 1, **kwargs):
    """Simulationクラス(vdp/状態を持つだけの状態機械)を渡すだけで、countステップ分
    進めたフレーム列を作る。各フレームはwait_frames回複製する(実機で同じ表示が
    wait_frames VSYNCぶん続く場合に使う。デフォルト1は毎フレーム更新するケース)。

    kwargsはそのままsimulation_cls(**kwargs)に渡す(例: start_c=...)。

    surfaceの作成・vdp.render(surface)の呼び出しはここが行う
    (Simulation側の責務ではない)。

    結果がMIN_EXPECTED_FRAMES未満なら、末尾フレームの複製ではなく
    step()を継続してそこまで底上げする(sc1_sp05/06のような周期的な
    アニメーションでは、実機は録画中も動き続けるため、最後のフレームで
    静止させると実機キャプチャと食い違う。sc1_sp01のような静止画面
    テストではstep()が状態を変えないので、結果的に複製と同じになる)。
    """
    sim = simulation_cls(**kwargs)
    surface = make_surface(SCREEN_WIDTH, SCREEN_HEIGHT)
    sim.vdp.render(surface)  # 初期状態をrenderしておく(前回状態への依存に対応)
    frames = []
    target = max(count * wait_frames, MIN_EXPECTED_FRAMES)
    while len(frames) < target:
        sim.step()
        sim.vdp.render(surface)
        frames.extend([surface_to_rgb(surface)] * wait_frames)
    return frames


def compare_to_expected(actual_frames, expected_path: pathlib.Path, width: int, height: int,
                         scale: int, caller_file: str) -> None:
    """実寸(width x height)のフレーム列を、scale倍で保存されたexpected webmと比較する。

    不一致ならAssertionErrorを投げる。
    """
    if not expected_path.exists():
        name = pathlib.Path(caller_file).name
        raise AssertionError(
            f"expected not found: {expected_path} "
            f"(run `python {name} --update-expected` once to create it)"
        )
    raw_frames = load_video(expected_path, width * scale, height * scale)
    expected_frames = [downscale_nearest(f, width, height, scale) for f in raw_frames]
    assert len(actual_frames) == len(expected_frames), (
        f"frame count mismatch: actual={len(actual_frames)} expected={len(expected_frames)}"
    )
    for i, (a, e) in enumerate(zip(actual_frames, expected_frames)):
        assert a == e, f"frame {i} differs from expected"


def assert_matches_expected_video(simulation_cls, count: int, caller_file: str, scale: int = EXPECTED_SCALE,
                                   wait_frames: int = 1, **kwargs) -> None:
    """render_expected_frames + compare_to_expected をまとめたもの。
    test_matches_expected_video() の本体を1行で書けるようにするため。

    expected_pathはcaller_file(通常は__file__)のファイル名から
    ../expected/<モジュール名>.webm として自動的に決まる(全テストファイルが
    その命名規則に従っているため)。width/heightも渡す必要は無い
    (render_expected_frames参照)。scaleは省略時EXPECTED_SCALE(全テストファイル共通の値)。
    """
    caller_path = pathlib.Path(caller_file)
    expected_path = expected_path_for(caller_file, caller_path.stem + ".webm")
    actual = render_expected_frames(simulation_cls, count, wait_frames=wait_frames, **kwargs)
    compare_to_expected(actual, expected_path, SCREEN_WIDTH, SCREEN_HEIGHT, scale, caller_file)


def write_expected(frames, expected_path: pathlib.Path, width: int, height: int, scale: int) -> None:
    """実寸のフレーム列をscale倍に拡大してexpected webmとして保存する。"""
    scaled = [upscale_nearest(f, width, height, scale) for f in frames]
    expected_path.parent.mkdir(parents=True, exist_ok=True)
    save_video(scaled, width * scale, height * scale, expected_path)
    print(f"wrote {expected_path} ({width * scale}x{height * scale}, {len(scaled)} frames)")


def render_and_write_expected(simulation_cls, count: int, caller_file: str, scale: int = EXPECTED_SCALE,
                               wait_frames: int = 1, **kwargs) -> None:
    """render_expected_frames + write_expected をまとめたもの。
    update_expected() の本体を1行で書けるようにするため。

    expected_path/width/height/scaleの決め方はassert_matches_expected_videoと同じ。
    """
    caller_path = pathlib.Path(caller_file)
    expected_path = expected_path_for(caller_file, caller_path.stem + ".webm")
    frames = render_expected_frames(simulation_cls, count, wait_frames=wait_frames, **kwargs)
    write_expected(frames, expected_path, SCREEN_WIDTH, SCREEN_HEIGHT, scale)


def run_all_tests(namespace: dict) -> bool:
    """namespace(通常はglobals())から test_ で始まる関数だけを拾って実行する。"""
    ok = True
    for name, fn in sorted(namespace.items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {name}")
            except AssertionError as e:
                ok = False
                print(f"FAIL {name}: {e}")
    return ok


def show_window(title: str, simulation_cls, scale: int = 3, wait_frames: int = 1,
                 cycle_frames: int = None, **kwargs) -> None:
    """目視確認用: pygameウィンドウにSimulationを表示する。

    描画・タイマーは実機と同じ60FPSで回すが、sim.step()はwait_framesフレームに
    1回だけ呼ぶ(実機の音楽ルーチンなどの都合でゲームロジックが複数VSYNCに
    1回しか進まない場合、例えばsc1_sp05のwait_5frameに合わせるため。
    デフォルト1は毎フレーム進めるケース)。surfaceの作成・vdp.render(surface)の
    呼び出しもここが行う(Simulation側はvdpと状態だけを持つ)。

    cycle_framesを指定すると、そのフレーム数が経過するたびにsimulation_cls
    (**kwargs)でSimulationを作り直してループ再生する(アニメーションが
    終わったら最初から、というデモ向け)。省略時はSimulationを1つ作ったまま
    回し続ける(状態が自前でループする/静止画のデモ向け)。
    """
    import pygame

    sim = simulation_cls(**kwargs)
    surface = make_surface(SCREEN_WIDTH, SCREEN_HEIGHT)
    sim.vdp.render(surface)
    window = pygame.display.set_mode((SCREEN_WIDTH * scale, SCREEN_HEIGHT * scale))
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()

    frame = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if cycle_frames is not None and frame % cycle_frames == 0:
            sim = simulation_cls(**kwargs)
            sim.vdp.render(surface)
        if frame % wait_frames == 0:
            sim.step()
            sim.vdp.render(surface)

        scaled = pygame.transform.scale(surface, (SCREEN_WIDTH * scale, SCREEN_HEIGHT * scale))
        window.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(60)

        frame += 1


def main(namespace: dict, simulation_cls=None, window_title: str = None,
          update_expected=None, wait_frames: int = 1, cycle_frames: int = None,
          **sim_kwargs) -> None:
    """--show / --update-expected / (指定なし=テスト実行) のCLIディスパッチ。

    --show 時は show_window(window_title, simulation_cls, ...) をそのまま呼ぶ。
    simulation_cls/window_title は --show を使うテストファイルでは必須
    (呼び出し元がSimulation/ウィンドウ名を知っているため、ここでは検証しない)。

    update_expected() は test_ で始まらないため run_all_tests には含まれず、
    --update-expected を指定した時だけ呼ばれる(意図的)。
    """
    if "--show" in sys.argv:
        show_window(window_title, simulation_cls, wait_frames=wait_frames,
                    cycle_frames=cycle_frames, **sim_kwargs)
    elif "--update-expected" in sys.argv and update_expected is not None:
        update_expected()
    else:
        sys.exit(0 if run_all_tests(namespace) else 1)
