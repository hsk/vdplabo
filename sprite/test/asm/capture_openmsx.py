"""openMSXでROMを実行し、結果をロスレス録画(ZMBV)してmp4/webm変換用の
生フレーム列に変換するツール。

使い方:
    python capture_openmsx.py rom/sc1_sp01.rom --settle 0.2 --duration 1

仕組み:
- openMSXは `-control stdio` で自動操作すると、実際にはウィンドウを
  作らずヘッドレス的に動いてしまい、`screenshot`/`record`コマンドが
  実行できたと返してきても中身が不定(ノイズ)になる/ファイルが
  作られないという問題がある(実測して確認済み)。
- 代わりに、`-script`に渡すTclスクリプトの中でrecord開始・終了・キー入力・
  終了処理を全部あらかじめスケジュールしておく方式なら、ウィンドウが
  正常に(通常起動と同じく)作られ、正しく録画できる。
- スケジューリングには`after frame <command>`(実際のVDPフレーム描画に
  同期して毎フレーム発火する)を使い、`__frame`というグローバル変数で
  フレーム番号を自前でカウントしながら、そのフレームに割り当てられた
  コマンドを`switch`で発火する(build_frame_tick_script参照)。
  当初は`after time <seconds> ...`(エミュレート時間ベース、壁時計に
  依存せず決定論的)を使っていたが、frame番号→秒への変換
  (frame/fps)がROM側メインループの実行位相のどこに当たるかは保証
  されず、player_moveがwait_vsyncの直前で呼ばれるROM(sc1_sp04.asm)で
  実測したところ、キーのpressとreleaseで「今回のGTSTCK呼び出しに
  間に合うか、次回に持ち越されるか」がズレて非対称な挙動になった
  (../input/README.md参照)。`after frame`はVDPフレームそのものに
  同期するため、この位相ズレが起きない。
  唯一の例外はinitに到達しなかった場合の保険(`after 20000 exit`、
  サブコマンド無しの素のフォーム=`after realtime`相当)で、これは
  実プロセスがハングしないための実時間タイムアウトなので意図的に
  壁時計ベースのままにしてある。
- openMSXの`record`はZMBV(Zip Motion Blocks Video)というロスレスコーデックで
  AVIに録画する。ffmpegがZMBVのデコーダを内蔵しているのでそのまま読める。
- 録画される画面は320x240(実測ではSCREEN5でも同じ320x240になる)。
  以前は可視領域256x192だけを中央寄せと仮定してクロップしていたが、
  SCREEN5以降は可視領域が256x212/512x212など可変な上、枠色(BDRCLR)自体も
  テスト対象にしたいため、今はクロップせず320x240のまま比較に使う
  (`BORDER_X=32, BORDER_Y=24`はpython側エンジンが可視領域を貼る位置の
  オフセットとして`probe_palette.py`向けの後方互換クロップ関数でのみ使う)。

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

キー入力の自動化について:
- `../input/<romのファイル名(拡張子抜き)>.json` が存在すれば自動的に読み込み、
  録画開始(settle_frames)を起点にキー入力をスケジュールする(明示的に
  `--input`を渡した場合はそちらを優先)。フォーマットは../input/README.md参照。
- 実体はrecord start/stopと同じ`after frame`のフレームカウント方式で
  `keymatrixdown`/`keymatrixup`をスケジュールしているので、
  決定論的な再現性はrecordと同じ。
"""
import argparse
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "input"))
from input_script import load_input_script, to_tcl_commands, duration_seconds  # noqa: E402

DEFAULT_DURATION = 2.0
FPS = 60

OPENMSX_WIDTH = 320
OPENMSX_HEIGHT = 240
BORDER_X = (OPENMSX_WIDTH - 256) // 2  # 32
BORDER_Y = (OPENMSX_HEIGHT - 192) // 2  # 24

INPUT_DIR = pathlib.Path(__file__).resolve().parents[1] / "input"


def compute_init_address(rom: pathlib.Path) -> int:
    """ROMヘッダ(org 4000h, db "AB", dw init, ...)からinitの実アドレスを求める。"""
    data = rom.read_bytes()
    if data[0:2] != b"AB":
        raise ValueError(f"{rom}: カートリッジヘッダ('AB')が見つからない")
    return data[2] | (data[3] << 8)


def default_input_path(rom: pathlib.Path) -> pathlib.Path:
    """rom名から../input/<rom名>.jsonのパスを返す(存在するとは限らない)。"""
    return INPUT_DIR / f"{rom.stem}.json"


def build_frame_tick_script(events: list, exit_frame: int) -> str:
    """[(frame, openMSXのTclコマンド), ...] から、`after frame`でフレームを
    1つずつ数えながら該当フレームでコマンドを発火するTclスクリプト片を返す。

    `after frame <command>`は実際のVDPフレーム描画そのものに同期して毎フレーム
    発火するため、`__frame`というグローバル変数で自前のフレームカウンタを
    進めながら、そのフレームに割り当てられたコマンド(複数あれば`; `で連結)を
    `switch`で発火する。exit_frameを超えたら`after frame`の再登録をやめる
    (それ以降は`exit`コマンド自体がプロセスを終了させるので実害は無いが、
    念のための後始末)。
    """
    by_frame = {}
    for frame, cmd in events:
        by_frame.setdefault(frame, []).append(cmd)
    lines = ["proc __tick {} {", "    global __frame", "    switch -- $__frame {"]
    for frame in sorted(by_frame):
        lines.append(f"        {frame} {{ {'; '.join(by_frame[frame])} }}")
    lines.append("    }")
    lines.append("    incr __frame")
    lines.append(f"    if {{$__frame <= {exit_frame}}} {{ after frame __tick }}")
    lines.append("}")
    lines.append("set __frame 0")
    lines.append("after frame __tick")
    return "\n".join(lines)


RECORD_SCALE_FLAGS = {1: "", 2: " -doublesize", 3: " -triplesize"}


def run_capture(rom: pathlib.Path, out_avi: pathlib.Path, settle: float = 0.2, duration: float = 1.0,
                 timeout: float = None, input_path: pathlib.Path = None,
                 settle_frames: int = None, duration_frames: int = None, record_scale: int = 1):
    """openMSXでromを実行し、initに到達してからsettle秒後~duration秒間を録画してout_aviに保存する。

    record_scaleはopenMSXの`record start`が対応する1(等倍, 320x240)/
    2(-doublesize, 640x480)/3(-triplesize, 960x720)のいずれか。
    ソフトウェアでのニアレストネイバー拡大と完全にビット一致することを
    実測で確認済み(SCREEN1の256ドット幅モードの場合)だが、SCREEN6/7の
    512ドット幅モードでは`-doublesize`が等倍録画の単純な2倍拡大ではなく、
    内部でその幅を落とさず捉えた結果になる可能性があるため
    (512ドットが等倍の320幅raw録画では潰れてしまう一方、-doublesizeの
    640幅ならちょうど収まる)、常にopenMSX側の該当フラグを使う。

    input_pathを指定した場合(省略時はdefault_input_path(rom)が存在すればそれを使う)、
    そのinput script(../input/README.md参照)のキー入力を録画開始(settle_frames)を
    起点にスケジュールする。

    settle_frames/duration_framesを指定すると、settle/duration(秒)からの
    round()計算を経由せずフレーム数をそのまま使う(秒指定だと期待値の
    フレーム数にちょうど合わせるのに半端な小数(例: 139/60秒)が必要になり
    扱いにくいため)。
    """
    init_addr = compute_init_address(rom)
    settle_frames = round(settle * FPS) if settle_frames is None else settle_frames
    stop_frames = settle_frames + (round(duration * FPS) if duration_frames is None else duration_frames)
    exit_frames = stop_frames + 30  # 0.5秒相当の余裕

    if input_path is None:
        input_path = default_input_path(rom)
        if not input_path.exists():
            input_path = None

    if record_scale not in RECORD_SCALE_FLAGS:
        raise ValueError(f"record_scale must be one of {sorted(RECORD_SCALE_FLAGS)}, got {record_scale}")
    record_flag = RECORD_SCALE_FLAGS[record_scale]
    events = [
        (settle_frames, f"record start{record_flag} {out_avi}"),
        (stop_frames, "record stop"),
        (exit_frames, "exit"),
    ]
    if input_path is not None:
        script = load_input_script(input_path)
        # -2: `after frame`はそのフレームの描画が完了した後(execVSync)に発火する。
        # ゲーム側の割り込み/SNSMATでのキー読み取り(execVScan)はその前に来るため、
        # frame Nのつもりで`after frame`から送ったコマンドは、そのフレームの
        # 読み取りにはもう間に合わず、次のフレーム(N+1)から効くことになる
        # (実測で確認済み)。input scriptの"frame N"を録画のフレームNそのものに
        # 反映させたいので、実測でさらに1フレーム早める必要があった(合計2)。
        events += [(max(0, settle_frames + frame - 2), cmd) for frame, cmd in to_tcl_commands(script)]

    tick_script = build_frame_tick_script(events, exit_frame=exit_frames + 5)
    indented = tick_script.replace("\n", "\n    ")

    script_text = (
        f"set maxframeskip 0\n"  # 録画中の負荷でフレームがスキップされると、
        # 録画されたフレーム数と実際のZ80/VDPフレーム数(＝input scriptの
        # frame番号)がズレる(実測で発覚。デフォルトはmaxframeskip=3で、
        # 録画のオーバーヘッドで実際に2フレームに1回しか描画されない
        # ことがあった)。0にして必ず毎フレーム描画・録画させる。
        f"debug set_bp {init_addr:#06x} 1 {{\n"
        f"    {indented}\n"
        f"}}\n"
        f"after 20000 exit\n"  # initに到達しなかった場合の保険(意図的に実時間のまま)
    )
    with open("out.tcl", "w") as f:
        f.write(script_text)

    with tempfile.NamedTemporaryFile("w", suffix=".tcl", delete=False) as f:
        f.write(script_text)
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


def avi_to_rgb_frames(avi_path: pathlib.Path, width: int = OPENMSX_WIDTH, height: int = OPENMSX_HEIGHT):
    """録画したavi(320x240, 枠付き)をクロップせず生RGBフレーム列に変換する。"""
    proc = subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(avi_path),
            "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg convert failed: {proc.stderr.decode(errors='replace')[-1500:]}")
    frame_size = width * height * 3
    raw = proc.stdout
    if len(raw) % frame_size != 0:
        raise ValueError(f"unexpected size {len(raw)} (not a multiple of {frame_size})")
    return [raw[i:i + frame_size] for i in range(0, len(raw), frame_size)]


def avi_to_cropped_rgb_frames(avi_path: pathlib.Path, width: int = 256, height: int = 192,
                               x: int = BORDER_X, y: int = BORDER_Y):
    """avi_to_rgb_framesを可視領域(デフォルト256x192)にクロップする後方互換版。

    probe_palette.pyのようにスプライト1個分の座標を直接pxで拾うだけの
    用途では、クロップ済みの方が座標計算が単純なため残してある。
    """
    crop = f"crop={width}:{height}:{x}:{y}"
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
    frame_size = width * height * 3
    raw = proc.stdout
    if len(raw) % frame_size != 0:
        raise ValueError(f"unexpected size {len(raw)} (not a multiple of {frame_size})")
    return [raw[i:i + frame_size] for i in range(0, len(raw), frame_size)]


def capture_to_webm(rom: pathlib.Path, out_webm: pathlib.Path, settle: float = 0.2, duration: float = 2.0,
                     scale: int = 2, input_path: pathlib.Path = None,
                     settle_frames: int = None, duration_frames: int = None) -> int:
    """録画(openMSX側で直接scale倍のaviを録画)→webm保存までを一括で行う。

    ソフトウェアでの拡大は行わず、openMSXの`record start`自体にscaleを
    渡す(run_captureのrecord_scale参照)。中間のaviは一時ファイルとして
    扱い、最後に破棄する。戻り値はフレーム数。settle_frames/duration_frames
    はrun_capture参照。
    """
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "python"))
    from video_expected import save_video  # noqa: E402

    with tempfile.TemporaryDirectory() as tmp:
        avi_path = pathlib.Path(tmp) / "capture.avi"
        run_capture(rom, avi_path, settle, duration, input_path=input_path,
                    settle_frames=settle_frames, duration_frames=duration_frames, record_scale=scale)
        frames = avi_to_rgb_frames(avi_path, OPENMSX_WIDTH * scale, OPENMSX_HEIGHT * scale)

    out_webm.parent.mkdir(parents=True, exist_ok=True)
    save_video(frames, OPENMSX_WIDTH * scale, OPENMSX_HEIGHT * scale, out_webm)
    return len(frames)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("rom", type=pathlib.Path)
    parser.add_argument("-o", "--output", type=pathlib.Path, default=None,
                         help="出力先。拡張子が.webmなら320x240のまま2倍拡大まで済ませたwebmを直接書き出す"
                              "(省略時は<rom>.avi、生のaviのまま保存)")
    parser.add_argument("--settle", type=float, default=0.2, help="initブレークポイント到達後、録画開始までの待ち秒数")
    parser.add_argument("--settle-frames", type=int, default=None,
                         help="--settleをフレーム数で指定する版(指定時は--settleより優先)。"
                              "期待値のフレーム数にちょうど合わせたい時に使う")
    parser.add_argument("--duration", type=float, default=None,
                         help=f"録画する秒数(省略時は{DEFAULT_DURATION}。ただしinput scriptを使う場合は"
                              "そのスクリプトを最後まで再生しきれる秒数を自動計算する)")
    parser.add_argument("--duration-frames", type=int, default=None,
                         help="--durationをフレーム数で指定する版(指定時は--duration/自動計算より優先)")
    parser.add_argument("--scale", type=int, default=2, help="webm出力時のニアレストネイバー拡大倍率")
    parser.add_argument("--input", type=pathlib.Path, default=None,
                         help="キー入力スクリプト(JSON、../input/README.md参照)。"
                              "省略時は../input/<rom名>.jsonが存在すれば自動的に使う")
    args = parser.parse_args()

    input_path = args.input if args.input is not None else default_input_path(args.rom)
    if not input_path.exists():
        input_path = None

    duration = args.duration
    if duration is None:
        duration = DEFAULT_DURATION
        if input_path is not None:
            duration = max(duration, duration_seconds(load_input_script(input_path)))

    output = args.output or args.rom.with_suffix(".avi")
    if output.suffix == ".webm":
        n = capture_to_webm(args.rom, output, args.settle, duration, args.scale, input_path=input_path,
                             settle_frames=args.settle_frames, duration_frames=args.duration_frames)
        print(f"wrote {output} ({n} frames)")
    else:
        run_capture(args.rom, output, args.settle, duration, input_path=input_path,
                     settle_frames=args.settle_frames, duration_frames=args.duration_frames)
        print(f"wrote {output}")
