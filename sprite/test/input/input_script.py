"""openMSX / Python版エンジン / C++(SDL2)版エンジンを同じキー入力シーケンスで
駆動するための、フレーム番号ベースの共通JSON形式(input script)を読み書きする。

フォーマット:
    {
      "fps": 60,
      "events": [
        {"frame": 0,  "key": "RIGHT", "action": "down"},
        {"frame": 3,  "key": "RIGHT", "action": "up"},
        {"frame": 6,  "key": "LEFT",  "action": "down"},
        {"frame": 9,  "key": "LEFT",  "action": "up"}
      ]
    }

- frame は0始まりのフレーム番号。fps(省略時60)はopenMSX向けにms換算する際に
  使うだけで、Python/C++側は自分のメインループが同じfpsで回っている前提で
  フレーム番号をそのまま突き合わせる(sprite/test/python/test_support.pyの
  show_windowも sprite/engine/sdl2/*/stage*.cpp のメインループも60fps固定)。
- key はMSXの論理キー名。KEY_MATRIX参照。
- action は "down"(押す) / "up"(離す)。

KEY_MATRIXの(row, col)はopenMSXの src/input/Keyboard.cc にあるキーマトリクス表
(international配列、`keymatrixdown/up <row> <col>` が直接読む生のマトリクス)
そのもの。C-BIOS(このプロジェクトが使う実行環境)はこの配列を使う。
row 9-11(テンキー/YES・NO)は機種によって存在しないため補助的な扱い。
"""
import dataclasses
import json
import pathlib

# (row, col) はopenMSXのキーマトリクス(src/input/Keyboard.cc)そのまま。
# col は該当行のbit位置(0-7)に対応する。
KEY_MATRIX = {
    # row 0: 数字
    "0": (0, 0), "1": (0, 1), "2": (0, 2), "3": (0, 3),
    "4": (0, 4), "5": (0, 5), "6": (0, 6), "7": (0, 7),
    # row 1: 数字続き・記号
    "8": (1, 0), "9": (1, 1), "MINUS": (1, 2), "EQUALS": (1, 3),
    "BACKSLASH": (1, 4), "LBRACKET": (1, 5), "RBRACKET": (1, 6), "SEMICOLON": (1, 7),
    # row 2: 記号・A/B
    "QUOTE": (2, 0), "BACKQUOTE": (2, 1), "COMMA": (2, 2), "PERIOD": (2, 3),
    "SLASH": (2, 4), "ACCENT": (2, 5), "A": (2, 6), "B": (2, 7),
    # row 3: C-J
    "C": (3, 0), "D": (3, 1), "E": (3, 2), "F": (3, 3),
    "G": (3, 4), "H": (3, 5), "I": (3, 6), "J": (3, 7),
    # row 4: K-R
    "K": (4, 0), "L": (4, 1), "M": (4, 2), "N": (4, 3),
    "O": (4, 4), "P": (4, 5), "Q": (4, 6), "R": (4, 7),
    # row 5: S-Z
    "S": (5, 0), "T": (5, 1), "U": (5, 2), "V": (5, 3),
    "W": (5, 4), "X": (5, 5), "Y": (5, 6), "Z": (5, 7),
    # row 6: 修飾キー・F1-F3
    "SHIFT": (6, 0), "CTRL": (6, 1), "GRAPH": (6, 2), "CAPS": (6, 3),
    "CODE": (6, 4), "F1": (6, 5), "F2": (6, 6), "F3": (6, 7),
    # row 7: F4/F5・制御キー
    "F4": (7, 0), "F5": (7, 1), "ESC": (7, 2), "TAB": (7, 3),
    "STOP": (7, 4), "BS": (7, 5), "SELECT": (7, 6), "RETURN": (7, 7),
    # row 8: SPACE・カーソルキー(GTSTCK stick=0が読むのはここ)
    "SPACE": (8, 0), "HOME": (8, 1), "INS": (8, 2), "DEL": (8, 3),
    "LEFT": (8, 4), "UP": (8, 5), "DOWN": (8, 6), "RIGHT": (8, 7),
    # row 9-10: テンキー(機種依存)
    "KP_MULT": (9, 0), "KP_PLUS": (9, 1), "KP_DIV": (9, 2), "KP_0": (9, 3),
    "KP_1": (9, 4), "KP_2": (9, 5), "KP_3": (9, 6), "KP_4": (9, 7),
    "KP_5": (10, 0), "KP_6": (10, 1), "KP_7": (10, 2), "KP_8": (10, 3),
    "KP_9": (10, 4), "KP_MINUS": (10, 5), "KP_COMMA": (10, 6), "KP_PERIOD": (10, 7),
    # row 11: YES/NO(機種依存)
    "YES": (11, 1), "NO": (11, 3),
}

ACTIONS = ("down", "up")


@dataclasses.dataclass(frozen=True)
class Event:
    frame: int
    key: str
    action: str

    @property
    def row_col(self) -> tuple:
        return KEY_MATRIX[self.key]


@dataclasses.dataclass(frozen=True)
class InputScript:
    fps: int
    events: list  # list[Event], frame昇順


def load_input_script(path) -> InputScript:
    """JSONファイルを読み、フレーム昇順に並んだInputScriptを返す。

    キー名・action・frameの妥当性はここで検証する(不正な値は即エラー)。
    """
    data = json.loads(pathlib.Path(path).read_text())
    fps = data.get("fps", 60)
    events = []
    for i, raw in enumerate(data.get("events", [])):
        frame = raw["frame"]
        key = raw["key"]
        action = raw["action"]
        if not isinstance(frame, int) or frame < 0:
            raise ValueError(f"events[{i}]: frame must be a non-negative int, got {frame!r}")
        if key not in KEY_MATRIX:
            raise ValueError(f"events[{i}]: unknown key {key!r} (see KEY_MATRIX)")
        if action not in ACTIONS:
            raise ValueError(f"events[{i}]: action must be one of {ACTIONS}, got {action!r}")
        events.append(Event(frame, key, action))
    events.sort(key=lambda e: e.frame)
    return InputScript(fps, events)


def duration_seconds(script: InputScript, margin: float = 0.5) -> float:
    """最後のイベントのframeをfpsで秒に変換し、marginを足したものを返す。

    capture_openmsx.pyが--durationを省略された時に「input scriptを
    最後まで再生しきれる録画時間」を自動で見積もるために使う。
    """
    if not script.events:
        return 0.0
    last_frame = script.events[-1].frame
    return last_frame / script.fps + margin


def events_by_frame(script: InputScript) -> dict:
    """{frame: [Event, ...]} にまとめる。Python/pygameエンジン側で
    フレームループの中から `for e in events_by_frame.get(frame, []): ...`
    のように毎フレーム引く用途を想定。
    """
    result = {}
    for e in script.events:
        result.setdefault(e.frame, []).append(e)
    return result


def to_tcl_commands(script: InputScript) -> list:
    """[(frame, openMSXのTclコマンド文字列), ...] を返す(frame昇順)。

    `after time <seconds> ...`(エミュレート時間ベース、壁時計に依存せず
    決定論的)でも、frame番号→秒への変換(frame/fps)がROM側メインループの
    実行位相のどこに当たるかは保証されない。player_moveがwait_vsyncの
    直前で呼ばれるROM(sc1_sp04.asm)で実測したところ、pressとreleaseで
    「今回のGTSTCK呼び出しに間に合うか、次回に持ち越されるか」が
    ズレて非対称な挙動になった(../asm/README.md参照)。
    `after frame`(実際のVDPフレーム描画そのものに同期して毎フレーム
    発火する)でフレームを1つずつ数える方式ならこのズレが起きないため、
    capture_openmsx.pyのbuild_frame_tick_script()はこちらを使う。

    第2引数はopenMSX側(src/input/Keyboard.cc の KeyMatrixDownCmd/UpCmd)の
    仕様上、ビット位置ではなく8bitのビットマスクなので、1 << col に変換する
    (`keymatrixdown <row> <col>` のようにcolをそのまま渡すのは誤り。
    実測で気付いた: col=4のつもりが実際にはbit2のキーを押していた)。
    """
    out = []
    for e in script.events:
        row, col = e.row_col
        mask = 1 << col
        cmd = "keymatrixdown" if e.action == "down" else "keymatrixup"
        out.append((e.frame, f"{cmd} {row} {mask}"))
    return out
