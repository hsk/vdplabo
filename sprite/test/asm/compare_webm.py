"""2つのwebm(ロスレスVP9)を比較するツール。

../expected/<name>.webm(Python版エンジンが生成した期待値)と
../expected/<name>_openmsx.webm(openMSX実機キャプチャ)が一致しているかを
確認するために使う。解像度・フレーム数が異なる場合もエラーとして報告する。

まずVP9ビットストリームのバイナリ比較(デコード不要で高速)を試み、
一致すればそれで確定する。両方とも`video_expected.save_video`が
`-threads 1`固定でエンコードしている前提なら通常はここで一致する。
バイト列が違った場合のみ、デコードしてピクセル単位で比較する
フォールバックに進む(遅いがlibvpxのバージョン等の環境差に依存しない)。

使い方:
    python3 compare_webm.py ../expected/sc1_sp04.webm ../expected/sc1_sp04_openmsx.webm

Makefileからは `make test_sc1_sp04` で実行できる。
"""
import argparse
import pathlib
import struct
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "python"))
from video_expected import load_video  # noqa: E402


def probe_size(path: pathlib.Path) -> tuple:
    """ffprobeでwebmの(width, height)を調べる。"""
    proc = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", str(path),
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {proc.stderr}")
    width, height = proc.stdout.strip().split("x")
    return int(width), int(height)


def extract_vp9_bitstream(path: pathlib.Path) -> bytes:
    """webmコンテナからVP9の符号化データそのものをIVFとして取り出す(再デコードなし)。

    webm(Matroska)コンテナ自体は書き出すたびにランダムなSegmentUIDが
    埋め込まれるため、webmファイルをそのままバイト比較しても一致しない
    (実測して確認済み)。`-c copy`でVP9ペイロードだけをIVFに移し替えれば、
    コンテナのランダム性を排除してコーデックのバイト列だけを比較できる。
    """
    proc = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(path), "-c", "copy", "-f", "ivf", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg -c copy failed for {path}: {proc.stderr.decode(errors='replace')}")
    return proc.stdout


def ivf_frame_count(ivf: bytes) -> int:
    """IVF本体のフレームチャンクを実際に走査して数える。

    ffmpegはパイプ(seek不可)にIVFを書き出す時、ヘッダのフレーム数欄
    (オフセット24)を0xFFFFFFFF(不明)のまま埋め戻さない(実測して確認済み)。
    ヘッダの値は当てにできないので、32バイト固定ヘッダの後に続く
    [4バイトサイズLE + 8バイトタイムスタンプ + サイズ分のペイロード]を
    末尾まで実際に辿って個数を数える。
    """
    pos = 32
    count = 0
    while pos < len(ivf):
        frame_size = struct.unpack_from("<I", ivf, pos)[0]
        pos += 12 + frame_size
        count += 1
    return count


def compare_webm(path_a: pathlib.Path, path_b: pathlib.Path) -> bool:
    """一致していればTrueを返し、一致していれば/していなければ理由を標準出力に書く。

    まずVP9ビットストリームのバイナリ比較(再デコード不要で高速)を試み、
    一致すればそれで確定させる。バイト列が違う場合(エンコード時の
    スレッド数やlibvpxのバージョンが違う環境など)のみ、フォールバックとして
    デコードしてピクセル単位で比較する(遅いが環境に依存しない)。
    """
    for path in (path_a, path_b):
        if not path.exists():
            print(f"NG {path} が見つからない")
            return False

    bitstream_a = extract_vp9_bitstream(path_a)
    bitstream_b = extract_vp9_bitstream(path_b)
    if bitstream_a == bitstream_b:
        n = ivf_frame_count(bitstream_a)
        print(f"OK {path_a.name} == {path_b.name} ({n} frames, VP9ビットストリームが完全一致・バイナリ比較)")
        return True

    size_a = probe_size(path_a)
    size_b = probe_size(path_b)
    if size_a != size_b:
        print(f"NG 解像度が違う: {path_a.name}={size_a[0]}x{size_a[1]} {path_b.name}={size_b[0]}x{size_b[1]}")
        return False

    width, height = size_a
    frames_a = load_video(path_a, width, height)
    frames_b = load_video(path_b, width, height)

    if len(frames_a) != len(frames_b):
        print(f"NG フレーム数が違う: {path_a.name}={len(frames_a)} {path_b.name}={len(frames_b)}")
        return False

    for i, (a, b) in enumerate(zip(frames_a, frames_b)):
        if a != b:
            diff_bytes = sum(1 for x, y in zip(a, b) if x != y)
            print(f"NG frame {i+1} が一致しない ({diff_bytes}/{len(a)} bytes differ)")
            return False

    print(f"OK {path_a.name} == {path_b.name} ({len(frames_a)} frames, {width}x{height})")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video_a", type=pathlib.Path)
    parser.add_argument("video_b", type=pathlib.Path)
    args = parser.parse_args()

    ok = compare_webm(args.video_a, args.video_b)
    sys.exit(0 if ok else 1)
