"""sc1_sp01.py / sc1_sp05.py / sc1_sp06.py で共通のテスト基盤。

VDP/エンジンのロジックには一切関与しない(そちらは各テストファイル自身の
責務)。webmの読み書き自体は video_expected.py の責務で、このモジュールは
その上に乗る「テストファイルの土台(sys.path設定・比較・保存・実行)」を
まとめたもの。
"""
import pathlib
import sys

from video_expected import load_video, save_video, downscale_nearest, upscale_nearest, surface_to_rgb


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


def render_expected_frames(simulation_cls, count: int, wait_frames: int = 1, **kwargs):
    """Simulationクラス(step()を呼ぶたびに.surfaceが更新されるもの)を渡すだけで、
    countステップ分進めたフレーム列を作る。各フレームはwait_frames回複製する
    (実機で同じ表示がwait_frames VSYNCぶん続く場合に使う。デフォルト1は
    毎フレーム更新するケース)。

    kwargsはそのままsimulation_cls(**kwargs)に渡す(例: start_c=...)。
    """
    sim = simulation_cls(**kwargs)
    frames = []
    for _ in range(count):
        sim.step()
        frames.extend([surface_to_rgb(sim.surface)] * wait_frames)
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


def write_expected(frames, expected_path: pathlib.Path, width: int, height: int, scale: int) -> None:
    """実寸のフレーム列をscale倍に拡大してexpected webmとして保存する。"""
    scaled = [upscale_nearest(f, width, height, scale) for f in frames]
    expected_path.parent.mkdir(parents=True, exist_ok=True)
    save_video(scaled, width * scale, height * scale, expected_path)
    print(f"wrote {expected_path} ({width * scale}x{height * scale}, {len(scaled)} frames)")


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


def main(namespace: dict, show_window=None, update_expected=None) -> None:
    """--show / --update-expected / (指定なし=テスト実行) のCLIディスパッチ。

    update_expected() は test_ で始まらないため run_all_tests には含まれず、
    --update-expected を指定した時だけ呼ばれる(意図的)。
    """
    if "--show" in sys.argv and show_window is not None:
        show_window()
    elif "--update-expected" in sys.argv and update_expected is not None:
        update_expected()
    else:
        sys.exit(0 if run_all_tests(namespace) else 1)
