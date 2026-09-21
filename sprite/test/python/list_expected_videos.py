"""../expected/以下の*.webmを全部調べて、解像度とフレーム数を一覧表示する。

スケール(EXPECTED_SCALE)やキャプチャ方式を変更するたびに、どのファイルが
まだ更新されていないか(古い解像度のまま残っていないか)を素早く確認する
ための診断ツール。

使い方:
    python list_expected_videos.py
"""
import pathlib
import subprocess

EXPECTED_DIR = pathlib.Path(__file__).resolve().parents[1] / "expected"


def probe(path: pathlib.Path) -> tuple:
    """ffprobeで(width, height, フレーム数)を調べる。"""
    proc = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-count_frames",
            "-show_entries", "stream=width,height,nb_read_frames",
            "-of", "csv=p=0", str(path),
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {proc.stderr}")
    width, height, frames = proc.stdout.strip().split(",")
    return int(width), int(height), int(frames)


def main() -> None:
    files = sorted(EXPECTED_DIR.glob("*.webm"))
    if not files:
        print(f"{EXPECTED_DIR} に.webmが見つかりません")
        return

    rows = []
    for path in files:
        try:
            width, height, frames = probe(path)
            rows.append((path.name, f"{width}x{height}", str(frames), ""))
        except Exception as e:  # noqa: BLE001
            rows.append((path.name, "?", "?", str(e)))

    name_w = max(len(r[0]) for r in rows)
    res_w = max(len(r[1]) for r in rows)
    frames_w = max(len(r[2]) for r in rows)
    for name, res, frames, err in rows:
        line = f"{name:<{name_w}}  {res:>{res_w}}  {frames:>{frames_w}}frames"
        if err:
            line += f"  ERROR: {err}"
        print(line)


if __name__ == "__main__":
    main()
