"""openMSXでROMを実行し、結果をロスレス録画(ZMBV)してmp4/webm変換用の
生フレーム列に変換するツール。

使い方:
    python capture_openmsx.py rom/sc1_sp01.rom --settle 0.2 --duration 1

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

起動ロゴのスキップについて:
- 以前は実時間の`--boot-wait`(何秒待つか)で決め打ちしていたが、
  ホストの負荷次第でエミュレーション速度が実時間からズレるため、
  同じ待ち秒数でもロゴが終わっていたり終わっていなかったりするブレがあった。
- 今はROMヘッダの`dw init`(オフセット2-3バイト、リトルエンディアン)から
  カートリッジの`init`アドレスを直接計算し、openMSXのデバッガで
  そのアドレスにブレークポイントを張ることで「実行が本当にinitへ
  到達した瞬間」を検出する。これはエミュレート内部の時間/フレーム数に
  基づくため完全に決定論的(実測で複数回とも寸分違わず同じフレームで
  ヒットすることを確認済み)。ブレークポイントヒットから`--settle`秒
  (デフォルト0.2秒、init自体の実行は一瞬なので短くて良い)待ってから
  録画を開始する
- ブレークポイントのコールバック内で使う`puts`は画面内コンソールにしか
  出力されずOSの標準出力には流れないため、ログを取りたい場合はTclの
  `open`/`puts`/`close`でファイルに直接書き込む必要がある(ハマりポイント)
"""
import argparse
import pathlib
import subprocess
import tempfile

OPENMSX_WIDTH = 320
OPENMSX_HEIGHT = 240
BORDER_X = (OPENMSX_WIDTH - 256) // 2  # 32
BORDER_Y = (OPENMSX_HEIGHT - 192) // 2  # 24


def compute_init_address(rom: pathlib.Path) -> int:
    """ROMヘッダ(org 4000h, db "AB", dw init, ...)からinitの実アドレスを求める。"""
    data = rom.read_bytes()
    if data[0:2] != b"AB":
        raise ValueError(f"{rom}: カートリッジヘッダ('AB')が見つからない")
    return data[2] | (data[3] << 8)


def run_capture(rom: pathlib.Path, out_avi: pathlib.Path, settle: float = 0.2, duration: float = 1.0,
                 timeout: float = None):
    """openMSXでromを実行し、initに到達してからsettle秒後~duration秒間を録画してout_aviに保存する。"""
    init_addr = compute_init_address(rom)
    settle_ms = int(settle * 1000)
    stop_ms = settle_ms + int(duration * 1000)
    exit_ms = stop_ms + 500
    script = (
        f"debug set_bp {init_addr:#06x} 1 {{\n"
        f"    after {settle_ms} record start {out_avi}\n"
        f"    after {stop_ms} record stop\n"
        f"    after {exit_ms} exit\n"
        f"}}\n"
        f"after 20000 exit\n"  # initに到達しなかった場合の保険
    )
    with tempfile.NamedTemporaryFile("w", suffix=".tcl", delete=False) as f:
        f.write(script)
        script_path = f.name

    if timeout is None:
        timeout = settle + duration + 25  # 保険の20秒 + 余裕

    proc = subprocess.run(
        ["openmsx", "-cart", str(rom), "-script", script_path],
        capture_output=True, text=True, timeout=timeout,
    )
    if not out_avi.exists():
        raise RuntimeError(
            f"openmsx did not produce {out_avi} (initアドレス0x{init_addr:04X}に到達しなかった可能性)\n"
            f"stdout={proc.stdout}\nstderr={proc.stderr}"
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


def capture_to_webm(rom: pathlib.Path, out_webm: pathlib.Path, settle: float = 0.2, duration: float = 2.0,
                     scale: int = 4) -> int:
    """録画(avi)→クロップ→ニアレストネイバー拡大→webm保存までを一括で行う。

    中間のaviは一時ファイルとして扱い、最後に破棄する。戻り値はフレーム数。
    """
    import sys

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "python"))
    from video_expected import save_video, upscale_nearest  # noqa: E402

    with tempfile.TemporaryDirectory() as tmp:
        avi_path = pathlib.Path(tmp) / "capture.avi"
        run_capture(rom, avi_path, settle, duration)
        frames = avi_to_cropped_rgb_frames(avi_path)

    scaled = [upscale_nearest(f, 256, 192, scale) for f in frames]
    out_webm.parent.mkdir(parents=True, exist_ok=True)
    save_video(scaled, 256 * scale, 192 * scale, out_webm)
    return len(frames)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("rom", type=pathlib.Path)
    parser.add_argument("-o", "--output", type=pathlib.Path, default=None,
                         help="出力先。拡張子が.webmならクロップ+4倍拡大まで済ませたwebmを直接書き出す"
                              "(省略時は<rom>.avi、生のaviのまま保存)")
    parser.add_argument("--settle", type=float, default=0.2, help="initブレークポイント到達後、録画開始までの待ち秒数")
    parser.add_argument("--duration", type=float, default=2.0, help="録画する秒数")
    parser.add_argument("--scale", type=int, default=4, help="webm出力時のニアレストネイバー拡大倍率")
    args = parser.parse_args()

    output = args.output or args.rom.with_suffix(".avi")
    if output.suffix == ".webm":
        n = capture_to_webm(args.rom, output, args.settle, args.duration, args.scale)
        print(f"wrote {output} ({n} frames)")
    else:
        run_capture(args.rom, output, args.settle, args.duration)
        print(f"wrote {output}")
