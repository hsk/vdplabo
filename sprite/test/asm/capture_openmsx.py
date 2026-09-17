"""openMSXでROMを実行し、結果をロスレス録画(ZMBV)してmp4/webm変換用の
生フレーム列に変換するツール。

使い方:
    python capture_openmsx.py rom/sc1_sp01.rom --boot-wait 5 --duration 1

仕組み:
- openMSXは `-control stdio` で自動操作すると、実際にはウィンドウを
  作らずヘッドレス的に動いてしまい、`screenshot`/`record`コマンドが
  実行できたと返してきても中身が不定(ノイズ)になる/ファイルが
  作られないという問題がある(実測して確認済み)。
- 代わりに、`-script`に渡すTclスクリプトの中で`after <ms> ...`を使い、
  録画の開始・終了・終了処理を全部あらかじめスケジュールしておく方式なら
  ウィンドウが正常に(通常起動と同じく)作られ、正しく録画できる。
  ただし`after`の遅延コマンドは `{...}` で1引数にまとめず、
  スペース区切りの複数引数のまま渡すこと
  (`after 3000 record start foo.avi` はOK、
   `after 3000 {record start foo.avi}` は "invalid command name" になる)。
- openMSXの`record`はZMBV(Zip Motion Blocks Video)というロスレスコーデックで
  AVIに録画する。ffmpegがZMBVのデコーダを内蔵しているのでそのまま読める。
- 録画される画面は320x240で、実際の可視領域256x192の周囲にボーダー
  (枠)が付いた状態。中央寄せと仮定して単純にクロップする
  (BORDER_X=32, BORDER_Y=24)。
"""
import argparse
import pathlib
import subprocess
import sys
import tempfile

OPENMSX_WIDTH = 320
OPENMSX_HEIGHT = 240
BORDER_X = (OPENMSX_WIDTH - 256) // 2  # 32
BORDER_Y = (OPENMSX_HEIGHT - 192) // 2  # 24


def run_capture(rom: pathlib.Path, out_avi: pathlib.Path, boot_wait: float, duration: float, timeout: float = None):
    """openMSXでromを実行し、boot_wait秒後からduration秒間を録画してout_aviに保存する。"""
    boot_ms = int(boot_wait * 1000)
    stop_ms = int((boot_wait + duration) * 1000)
    exit_ms = stop_ms + 500
    script = (
        f"after {boot_ms} record start {out_avi}\n"
        f"after {stop_ms} record stop\n"
        f"after {exit_ms} exit\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".tcl", delete=False) as f:
        f.write(script)
        script_path = f.name

    if timeout is None:
        timeout = boot_wait + duration + 10

    proc = subprocess.run(
        ["openmsx", "-cart", str(rom), "-script", script_path],
        capture_output=True, text=True, timeout=timeout,
    )
    if not out_avi.exists():
        raise RuntimeError(
            f"openmsx did not produce {out_avi}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )


def avi_to_cropped_rgb_frames(avi_path: pathlib.Path):
    """録画したavi(320x240, 枠付き)を256x192(可視領域のみ)の生RGBフレーム列に変換する。"""
    crop = f"crop={256}:{192}:{BORDER_X}:{BORDER_Y}"
    proc = subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(avi_path),
            "-vf", crop, "-an",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg crop failed: {proc.stderr.decode(errors='replace')[-1500:]}")
    frame_size = 256 * 192 * 3
    raw = proc.stdout
    if len(raw) % frame_size != 0:
        raise ValueError(f"unexpected size {len(raw)} (not a multiple of {frame_size})")
    return [raw[i:i + frame_size] for i in range(0, len(raw), frame_size)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=pathlib.Path)
    parser.add_argument("-o", "--output", type=pathlib.Path, default=None, help="出力先avi (省略時は<rom>.avi)")
    parser.add_argument("--boot-wait", type=float, default=5.0, help="録画開始までの待ち秒数(起動ロゴをスキップする分)")
    parser.add_argument("--duration", type=float, default=1.0, help="録画する秒数")
    args = parser.parse_args()

    output = args.output or args.rom.with_suffix(".avi")
    run_capture(args.rom, output, args.boot_wait, args.duration)
    print(f"wrote {output}")
