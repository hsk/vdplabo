"""openMSXで probe_palette.rom を実行し、16色パレットの実際のRGB値を
実測してPythonの PALETTE リスト形式で出力するツール。

パレットはエミュレータ(や設定・レンダラ)によって変わりうるので、
engine/python/sprite1/stage1.py・stage4.py のPALETTE定数が古くなったら
このスクリプトで再実測して更新する。

使い方:
    make probe_palette              # rom/probe_palette.rom をビルド
    python probe_palette.py rom/probe_palette.rom
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from capture_openmsx import run_capture, avi_to_cropped_rgb_frames  # noqa: E402

# probe_palette.asm のスプライト配置と対応させる
# (Y, X, パターン, 色) の色=1..15 を Y=8+11*i の位置に1個ずつ配置している
COLOR_NAMES = [
    "Transparent", "Black", "Medium green", "Light green", "Dark blue",
    "Light blue", "Dark red", "Cyan", "Medium red", "Light red",
    "Dark yellow", "Light yellow", "Dark green", "Magenta", "Gray", "White",
]


def probe(rom: pathlib.Path):
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        avi_path = pathlib.Path(tmp) / "probe.avi"
        run_capture(rom, avi_path, settle=0.2, duration=0.2)
        frames = avi_to_cropped_rgb_frames(avi_path)
    frame = frames[-1]
    width = 256

    def px(x, y):
        i = (y * width + x) * 3
        return frame[i], frame[i + 1], frame[i + 2]

    # index 0(Transparent)はスプライトとして描画されないので実測できない
    colors = [(0, 0, 0)]
    # probe_palette.asm は色1〜15のスプライトを Y=8+11*i (i=0..14) に配置している
    for i in range(15):
        y = 8 + 11 * i + 4
        colors.append(px(104, y))
    return colors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("rom", type=pathlib.Path, nargs="?", default=pathlib.Path("rom/probe_palette.rom"))
    args = parser.parse_args()

    if not args.rom.exists():
        sys.exit(f"{args.rom} が見つかりません。先に `make probe_palette` でビルドしてください。")

    colors = probe(args.rom)
    print("PALETTE = [")
    for i, (color, name) in enumerate(zip(colors, COLOR_NAMES)):
        print(f"    {color!r},{' ' * (20 - len(repr(color)))}# {i} {name}")
    print("]")
