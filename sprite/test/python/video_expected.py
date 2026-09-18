"""フレーム列をロスレスwebm(VP9)として保存/比較するための共通ユーティリティ。

pythonエンジンのテストだけでなく、将来openMSXや自作エミュレータが吐き出す
フレーム列(生RGBバイト列)も同じ形式で扱えるようにするための土台。

完全な可逆性(ビット完全一致)と、輪郭ににじみ(クロマブリーディング)が
出ないことを両立するため、色空間変換のない`libvpx-vp9`の`gbrp`
(RGBそのまま、YUVに変換しない)ピクセルフォーマットを使う。
通常のyuv420p/yuv444pは`-lossless 1`でもRGB→YUV変換の丸め誤差で
輪郭ににじみが出てビット完全一致しないため使わない(実測して確認済み)。

VP9の`gbrp`は正式仕様の"Profile 1"で、Chrome/Firefox/Edgeは
(ハードウェアが非対応でも)自前のソフトウェアデコーダ(libvpx)で
再生できる。H.264の4:4:4 RGBプロファイルよりブラウザ対応は良いはずだが、
QuickTime Playerはwebm自体に非対応(VLC/IINA/ffplayなら再生可)。
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


def save_video(frames_rgb: List[bytes], width: int, height: int, path: Path, fps: int = FPS) -> None:
    """RGB24の生フレーム列を可逆webm(VP9, gbrp)として保存する。

    `-threads 1 -row-mt 0`で常にシングルスレッドエンコードに固定している。
    libvpx-vp9はスレッド数を変えるとエンコード結果のバイト列が変わる
    (実測して確認済み。デコードした画素は変わらないので可逆性自体には
    影響しないが、バイト列が変わるとファイルの単純なバイナリ比較による
    高速な一致判定ができなくなる)。
    """
    raw = b"".join(frames_rgb)
    _run_ffmpeg(
        [
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(fps),
            "-i", "-",
            "-c:v", "libvpx-vp9", "-lossless", "1", "-pix_fmt", "gbrp",
            "-threads", "1", "-row-mt", "0",
            str(path),
        ],
        input_bytes=raw,
    )


def load_video(path: Path, width: int, height: int) -> List[bytes]:
    """webmを読み込みRGB24の生フレーム列に戻す。"""
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


def downscale_nearest(frame: bytes, width: int, height: int, factor: int) -> bytes:
    """upscale_nearestの逆操作。等間隔に間引いて実寸へ戻す。

    upscale_nearestは各ピクセルをfactor x factor個に複製しているだけなので、
    先頭のピクセルだけを拾えば劣化なく元の値を復元できる。
    (width, height)は間引いた後の実寸を指定する。
    """
    src_row_bytes = width * factor * 3
    rows = []
    for y in range(height):
        src_row = frame[y * factor * src_row_bytes: y * factor * src_row_bytes + src_row_bytes]
        rows.append(b"".join(src_row[x * factor * 3: x * factor * 3 + 3] for x in range(width)))
    return b"".join(rows)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "webmをニアレストネイバーでさらに拡大し、"
            "見やすい別ファイルとして書き出す(入力ファイル自体は変更しない)"
        )
    )
    parser.add_argument("input", type=Path, help="変換元のwebm (例: ../expected/sc1_sp06.webm)")
    parser.add_argument("-o", "--output", type=Path, default=None, help="出力先 (省略時は <input>_view.webm)")
    parser.add_argument("--scale", type=int, default=4, help="拡大倍率 (デフォルト4倍)")
    parser.add_argument("--open", action="store_true", help="生成後にデフォルトプレイヤーで開く")
    args = parser.parse_args()

    width, height = probe_size(args.input)
    frames = load_video(args.input, width, height)
    scaled = [upscale_nearest(f, width, height, args.scale) for f in frames]
    output = args.output or args.input.with_name(args.input.stem + "_view.webm")
    save_video(scaled, width * args.scale, height * args.scale, output)
    print(f"wrote {output} ({width * args.scale}x{height * args.scale}, {len(scaled)} frames)")
    if args.open:
        subprocess.run(["open", str(output)])
