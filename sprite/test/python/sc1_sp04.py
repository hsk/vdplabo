"""sc1_sp04.asm(左右キーでプレイヤーのスプライトを動かし、他の2枚の
スプライトに重なるとハードウェアの衝突判定(STATFLのCビット)でスプライト
の色が変わる)をエンジンで再現し、実機キャプチャと比較するテスト。

sc1_sp04.asmの現在の構造:
- player_move(キー読み取り+player_x更新)はメインループではなく
  H.TIMIフック(割り込みハンドラ)の中で実行される(理由は下記)
- メインループはwait_vsync(H.TIMIが立てるvintフラグを待つ) ->
  player_draw -> player_collision の繰り返し
- Simulation.step()はメインループ1周に対応する(呼び出し側がstep()の
  たびにvdp.render(surface)を呼ぶ想定は他のテストファイルと同じ)

移動速度について: キーが押されている間、毎フレーム1pxずつ動く(押下から
1フレーム後に動き出す)。これは今のsc1_sp04.asmの実測値そのままで、
バグも謎の遅延も無い、素直な速度。

(過去の履歴・調査メモ: ここまで来るのにかなり遠回りをした)
1. 当初は「押しっぱなしでも2フレームに1回しか動かない」謎の挙動があった。
   GTSTCK/SNSMAT/openMSXの割り込み頻度/wait_vsyncの実装(JIFFYポーリング
   /HALT)を順に疑って実測で潰したが、実際は player_move の末尾にretが
   無く、wait_vsyncへそのままフォールスルーして1周につき実質2回vsync
   待ちをしていた、という単純なコードのバグだった。
2. retを直したら1px/frameになったが、今度は起動後frame44あたりから
   周期的なジッターが発生した。これはC-BIOSの割り込みハンドラが
   「3割り込みおきにキーボードの背後スキャン(key_in)を行う」仕様に
   由来していた。SCNCNT(F3F6h)の初期値がちょうどframe44あたりで0に
   達し、そこから3フレームごとにkey_inが呼ばれ続けることで、メイン
   ループ側でSNSMATを呼ぶ形の実装ではぎりぎりだったタイミング予算が
   崩れ続けていた。
3. 最終的な解決策は、player_move自体をH.TIMIフック(../../../asm/int.asm
   と同じ手法。BIOSのkeyintがH_TIMIを呼ぶのはkey_inより前なので、
   ここでキーを読めばkey_inの余分なコストの影響を受けない)の中に移す
   ことだった。これで完全に安定した1px/frameになった。
詳しい実測ログは../asm/README.mdを参照。

キー入力は ../input/sc1_sp04.json (LEFT/RIGHTキーでsprite1・sprite2の
両方と重なるように往復させるスクリプト)を使い、同じinput scriptで
Python版エンジン自身が生成した../expected/sc1_sp04.webmとフレームごとに
ピクセル単位で比較する(他のsc1_sp*テストと同じ回帰テスト方式)。
実機キャプチャ../expected/sc1_sp04_openmsx.webmは自動テストには
組み込まず、実機との突き合わせ用の参考ファイルとして別途保持する。

実行方法:
    python sc1_sp04.py                  # 自動テストのみ実行
    python sc1_sp04.py --replay         # pygameウィンドウでinput scriptを再生
    python sc1_sp04.py --show           # pygameウィンドウでキーボード操作(矢印キー)
"""
import collections
import pathlib
import sys

from test_support import (  # noqa: E402
    add_engine_path, expected_path_for, compare_to_expected, write_expected, make_surface, main,
    SCREEN_WIDTH, SCREEN_HEIGHT, EXPECTED_SCALE,
)
from video_expected import surface_to_rgb  # noqa: E402

add_engine_path(__file__)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "input"))

from stage4 import V9918  # noqa: E402
from input_script import load_input_script, events_by_frame, duration_seconds  # noqa: E402

VIEW_SCALE = EXPECTED_SCALE

# sc1_sp04.asm の sprite_pattern_data と同じ8バイト
# (asmは9桁の2進数リテラル(例: 000011000b)で書かれているが、
# z80asmはdbを8bit切り詰めで解釈するので先頭桁は無視してよい)
SPRITE_PATTERN = [0x18, 0x3C, 0x7E, 0xDB, 0xFF, 0x24, 0x5A, 0xA2]

PLAYER_Y = 115
PLAYER_X_INIT = 100
SPRITE1 = {"x": 100, "y": 100, "color": 14}
SPRITE2 = {"x": 40, "y": 100, "color": 11}
COLOR_NORMAL = 15      # 白
COLOR_COLLISION = 6    # 濃い赤

INPUT_SCRIPT_PATH = pathlib.Path(__file__).resolve().parents[1] / "input" / "sc1_sp04.json"


def build_vdp() -> V9918:
    vdp = V9918()
    vdp.set_sprite_pattern(0, SPRITE_PATTERN)
    vdp.set_sprite_mag(True)  # screen_initが R#1 に or 1 する(スプライト拡大)
    vdp.set_sprite(1, SPRITE1["x"], SPRITE1["y"], 0, SPRITE1["color"])
    vdp.set_sprite(2, SPRITE2["x"], SPRITE2["y"], 0, SPRITE2["color"])
    # sc1_sp04.asm は border_color_init で、CHGMOD実行後にWRTVDPで
    # VDPレジスタ7を直接4(濃い青)から5(薄い青)へ書き換えている。
    # このタイミングでのR#7書き換えは実機/C-BIOS上では枠(border)にしか
    # 効かず、画面内の背景色(CHGMOD時にカラーテーブルへ焼き込まれた
    # BIOSデフォルトの4)はそのまま変わらない(V9918.set_backdrop_colorの
    # docstring、sc1_sp01.pyのbuild_vdpと同じ)。
    vdp.set_backdrop_color(5)
    return vdp


COLOR_LAG = 1  # 実測値(STATFL経由の1フレーム遅延+render()のタイミング分)


class Simulation:
    """sc1_sp04.asmのmain loop(wait_vsync -> player_draw -> player_collision。
    player_move自体はH.TIMIフック内で毎割り込み実行される、詳細はファイル
    先頭のdocstring参照)を1step()=1周として再現する状態機械。

    キー入力はkey_up/down/left/rightで表現し、set_key()で外から(JSON再生
    でもライブキーボードでも)更新する。押されている間、毎step()で
    1pxずつ増減する(1フレームの反応遅延はイベント適用のタイミング
    (render_with_input参照)で自然に再現される)。

    衝突色の反映遅延(COLOR_LAG)について: STATFLは1フレーム遅延した
    衝突結果を持つ。実測ではCOLOR_LAG=1フレーム前のrender()結果を見て
    今回の色を決めると実機キャプチャに一致する。呼び出し側はrender()の
    たびにafter_render()を呼ぶこと(render_with_input参照)。
    """

    def __init__(self):
        self.vdp = build_vdp()
        self.player_x = PLAYER_X_INIT
        self.color = COLOR_NORMAL
        self.key_up = self.key_down = self.key_left = self.key_right = False
        # after_render()のたびにget_collision()を追記(--show/--replayが
        # 無限ループで動き続けても無制限に伸びないようmaxlenで打ち切る)
        self._collision_log = collections.deque(maxlen=COLOR_LAG)
        self.vdp.set_sprite(0, self.player_x, PLAYER_Y, 0, self.color)

    def after_render(self) -> None:
        """呼び出し側がvdp.render(surface)の直後に毎回呼ぶこと。"""
        self._collision_log.append(self.vdp.get_collision())

    def set_key(self, key: str, pressed: bool) -> None:
        if key == "LEFT":
            self.key_left = pressed
        elif key == "RIGHT":
            self.key_right = pressed
        elif key == "UP":
            self.key_up = pressed
        elif key == "DOWN":
            self.key_down = pressed

    def step(self) -> None:
        # player_move(H.TIMIフック内相当): SNSMATの行8を直接見るのと同じ
        # 意味で、bit7=RIGHT, bit4=LEFTを直接チェックする(GTSTCKのスティック
        # 方向コードは経由しない、実際のasmと同じ)。押されている間、毎step()
        # で1pxずつ動く(反応遅延はイベント適用側のCAPTURE_FRAME_OFFSETで
        # 吸収する。ここでは遅延を持たせない)。
        if self.key_right:
            self.player_x = (self.player_x + 1) & 0xFF
        elif self.key_left:
            self.player_x = (self.player_x - 1) & 0xFF

        # player_draw: 前回のplayer_collisionが決めた色で描画
        self.vdp.set_sprite(0, self.player_x, PLAYER_Y, 0, self.color)

        # player_collision: COLOR_LAG(実測1)フレーム前のrender()結果を見て
        # 次回の描画色を決める(クラスdocstring参照)。dequeがまだ
        # maxlenに達していない(起動直後)場合は衝突なし扱い。
        log = self._collision_log
        collided = log[0] if len(log) == log.maxlen else False
        self.color = COLOR_COLLISION if collided else COLOR_NORMAL


CAPTURE_FRAME_OFFSET = 1  # 実測値。理由は下記
# ../asm/capture_openmsx.py のrun_capture()は、openMSXの`after frame`が
# 「そのフレームの描画が終わった後」に発火する分の補正として、input
# scriptのイベントを2フレーム早めてスケジュールしている(実測)。
# Python側にはそのopenMSX固有の遅延は無いので、同じ「フレームNの入力を
# 映像のフレームN(1始まり)に反映させる」という結果に合わせるには、
# ここでは1フレームだけ早めればよい(実測値。詳細はsc1_sp04.pyの
# gitログ・../asm/README.md参照)。


def render_with_input(simulation_cls, input_script_path, frame_count, **kwargs):
    """input scriptを再生しながらsimulation_clsをframe_count回step()させ、
    各フレームのRGBを返す(1フレーム=1step、wait_frames無し)。

    test_support.render_expected_framesのキー入力版(Simulationに
    set_key()がある前提)。events_by_frame[i]のイベントは「step(i)を
    呼ぶCAPTURE_FRAME_OFFSETフレーム前に」適用する(../asm/capture_openmsx.py
    のrun_capture()と同じ補正。理由はCAPTURE_FRAME_OFFSETの定義部分参照)。
    """
    script = load_input_script(input_script_path)
    by_frame = events_by_frame(script)

    sim = simulation_cls(**kwargs)
    surface = make_surface(SCREEN_WIDTH, SCREEN_HEIGHT)
    sim.vdp.render(surface)  # 初期状態をrenderしておく(前回状態への依存に対応)
    sim.after_render()
    frames = []
    for i in range(frame_count):
        for e in by_frame.get(i + CAPTURE_FRAME_OFFSET, []):
            sim.set_key(e.key, e.action == "down")
        sim.step()
        sim.vdp.render(surface)
        sim.after_render()
        frames.append(surface_to_rgb(surface))
    return frames


def _expected_frame_count(expected_path: pathlib.Path) -> int:
    from video_expected import load_video

    raw = load_video(expected_path, SCREEN_WIDTH * VIEW_SCALE, SCREEN_HEIGHT * VIEW_SCALE)
    return len(raw)


def test_matches_expected_video():
    expected_path = expected_path_for(__file__, "sc1_sp04.webm")
    frame_count = _expected_frame_count(expected_path)
    actual = render_with_input(Simulation, INPUT_SCRIPT_PATH, frame_count)
    compare_to_expected(actual, expected_path, SCREEN_WIDTH, SCREEN_HEIGHT, VIEW_SCALE, __file__)


def update_expected() -> None:
    """../input/sc1_sp04.json(INPUT_SCRIPT_PATH)で駆動したPython版エンジンの
    描画結果を../expected/sc1_sp04.webmとして書き出す(openMSX実機は使わない。
    test_matches_expected_video()もこのファイルと比較する。実機キャプチャの
    ../expected/sc1_sp04_openmsx.webmは自動テストには使わず、実機との
    突き合わせ用に別途手動で見比べる参考ファイルとして残す)。

    フレーム数はinput scriptの最後のイベントから
    duration_seconds()(../input/input_script.py)と同じ余裕を持たせて決める。
    """
    frame_count = round(duration_seconds(load_input_script(INPUT_SCRIPT_PATH)) * 60)
    frames = render_with_input(Simulation, INPUT_SCRIPT_PATH, frame_count)
    expected_path = expected_path_for(__file__, "sc1_sp04.webm")
    write_expected(frames, expected_path, SCREEN_WIDTH, SCREEN_HEIGHT, VIEW_SCALE)


def show_replay() -> None:
    """pygameウィンドウでinput scriptの再生を目視確認する(60FPS)。"""
    import pygame

    script = load_input_script(INPUT_SCRIPT_PATH)
    by_frame = events_by_frame(script)
    last_frame = script.events[-1].frame if script.events else 0

    sim = Simulation()
    surface = make_surface(SCREEN_WIDTH, SCREEN_HEIGHT)
    sim.vdp.render(surface)
    sim.after_render()
    window = pygame.display.set_mode((SCREEN_WIDTH * 3, SCREEN_HEIGHT * 3))
    pygame.display.set_caption("sc1_sp04 --replay")
    clock = pygame.time.Clock()

    frame = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        for e in by_frame.get(frame % (last_frame + 1), []):
            sim.set_key(e.key, e.action == "down")
        sim.step()
        sim.vdp.render(surface)
        sim.after_render()
        scaled = pygame.transform.scale(surface, (SCREEN_WIDTH * 3, SCREEN_HEIGHT * 3))
        window.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        frame += 1


def show_live() -> None:
    """pygameウィンドウで矢印キーによるライブ操作を確認する(60FPS)。"""
    import pygame

    key_map = {pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT", pygame.K_UP: "UP", pygame.K_DOWN: "DOWN"}

    sim = Simulation()
    surface = make_surface(SCREEN_WIDTH, SCREEN_HEIGHT)
    sim.vdp.render(surface)
    sim.after_render()
    window = pygame.display.set_mode((SCREEN_WIDTH * 3, SCREEN_HEIGHT * 3))
    pygame.display.set_caption("sc1_sp04 --show (矢印キーで操作)")
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP) and event.key in key_map:
                sim.set_key(key_map[event.key], event.type == pygame.KEYDOWN)
        sim.step()
        sim.vdp.render(surface)
        sim.after_render()
        scaled = pygame.transform.scale(surface, (SCREEN_WIDTH * 3, SCREEN_HEIGHT * 3))
        window.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    if "--replay" in sys.argv:
        show_replay()
    elif "--show" in sys.argv:
        show_live()
    else:
        main(globals(),update_expected=update_expected,cycle_frames=354)
