"""フレーム列をロスレスmp4として保存/比較するための共通ユーティリティ。

pythonエンジンのテストだけでなく、将来openMSXや自作エミュレータが吐き出す
フレーム列(生RGBバイト列)も同じ形式で扱えるようにするための土台。

mp4のコンテナはそのままにしつつ完全な可逆性が欲しいので、色空間変換のない
`libx264rgb`(RGBのままH.264で符号化)を使う。通常のyuv420p/yuv444pは
`-crf 0`でもRGB→YUV変換の丸め誤差でビット完全一致しないため使わない
(実測して確認済み)。

QuickTimeなど一部プレイヤーはこの4:4:4 RGBプロファイルをネイティブ再生
できない場合がある(VLC/IINA/ffplayなら確実に再生できる)。
"""
import subprocess
from pathlib import Path
from typing import List

FPS = 60


def _run_ffmpeg(args: List[str], input_bytes: bytes = None) -> bytes:
    proc = subprocess.run(
        ["ffmpeg", "-y", *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        tail = proc.stderr.decode(errors="replace")[-2000:]
        raise RuntimeError(f"ffmpeg failed (args={args}):\n{tail}")
    return proc.stdout


def surface_to_rgb(surface) -> bytes:
    import pygame

    return pygame.image.tostring(surface, "RGB")


def save_mp4(frames_rgb: List[bytes], width: int, height: int, path: Path, fps: int = FPS) -> None:
    """RGB24の生フレーム列を可逆mp4として保存する。"""
    raw = b"".join(frames_rgb)
    _run_ffmpeg(
        [
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(fps),
            "-i", "-",
            "-c:v", "libx264rgb", "-crf", "0",
            str(path),
        ],
        input_bytes=raw,
    )


def load_mp4(path: Path, width: int, height: int) -> List[bytes]:
    """mp4を読み込みRGB24の生フレーム列に戻す。"""
    raw = _run_ffmpeg(["-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    frame_size = width * height * 3
    if len(raw) % frame_size != 0:
        raise ValueError(f"unexpected raw video size: {len(raw)} is not a multiple of {frame_size}")
    return [raw[i:i + frame_size] for i in range(0, len(raw), frame_size)]


def probe_size(path: Path) -> "tuple[int, int]":
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path),
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if out.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {out.stderr.decode(errors='replace')}")
    width_str, height_str = out.stdout.decode().strip().split(",")
    return int(width_str), int(height_str)


def upscale_nearest(frame: bytes, width: int, height: int, factor: int) -> bytes:
    """見た目確認用: ニアレストネイバーで整数倍に拡大する(補間なし=くっきり)。"""
    row_bytes = width * 3
    rows = []
    for y in range(height):
        row = frame[y * row_bytes:(y + 1) * row_bytes]
        rows.append(b"".join(row[i:i + 3] * factor for i in range(0, row_bytes, 3)))
    return b"".join(row for row in rows for _ in range(factor))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "golden mp4(比較用の等倍サイズ)をニアレストネイバーで拡大し、"
            "見やすい別ファイルとして書き出す(golden自体は変更しない)"
        )
    )
    parser.add_argument("input", type=Path, help="変換元のmp4 (例: goldens/sc1_sp06.mp4)")
    parser.add_argument("-o", "--output", type=Path, default=None, help="出力先 (省略時は <input>_view.mp4)")
    parser.add_argument("--scale", type=int, default=4, help="拡大倍率 (デフォルト4倍)")
    parser.add_argument("--open", action="store_true", help="生成後にデフォルトプレイヤーで開く")
    args = parser.parse_args()

    width, height = probe_size(args.input)
    frames = load_mp4(args.input, width, height)
    scaled = [upscale_nearest(f, width, height, args.scale) for f in frames]
    output = args.output or args.input.with_name(args.input.stem + "_view.mp4")
    save_mp4(scaled, width * args.scale, height * args.scale, output)
    print(f"wrote {output} ({width * args.scale}x{height * args.scale}, {len(scaled)} frames)")
    if args.open:
        subprocess.run(["open", str(output)])
