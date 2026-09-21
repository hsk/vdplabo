"""sc1_sp08.asm(32個のスプライトが固定小数点演算で画面内を跳ね回るデモ)を
エンジンで再現し、録画したwebm(expected)とピクセル単位で比較するテスト。

これまでのsc1_sp01/04/05/06と違い、このROMは初期速度を乱数(自前のLCG)で
決めるため、Python側でも同じ乱数列を再現する必要がある。以下はすべて
openMSXのデバッガでROM実行中のRAM/VRAMを直接読み、実機の値と1バイトも
違わないことを確認した上でPythonに移植したものである。

## 乱数(random:)の移植

```asm
random:
    ld hl, (seed)
    ld d, h
    ld e, l
    add hl, hl ; seed * 2
    add hl, hl ; seed * 4
    add hl, hl ; seed * 8
    add hl, hl ; seed * 16
    sbc hl, de ; seed * 15 ...のつもりだが、直前のadd hl,hlが立てたキャリーを
                 sbc hl,deがそのまま消費するため、実際の値は「(2乗算4回の
                 キャリーを含めた)15倍」ではなく、キャリー伝播込みの値になる
    add hl, hl
    add hl, hl
    sbc hl, de
    add hl, hl
    sbc hl, de
    ld de, 07321h
    add hl, de
    ld (seed), hl
    ret
```

`add hl,hl`はキャリーを消費しない(ADDであってADCではない)が、直後の
`sbc hl,de`は必ずキャリーを消費するため、コメントの「15倍」等はキャリーを
無視した近似でしかない。正しく移植するには各`add hl,hl`が生成するキャリーを
明示的に次の`sbc hl,de`まで伝播させる必要がある(`random_step`参照)。

## 初期化(loop4)とseed変数のアドレス衝突バグ

`seed equ 0C100h`は`sprites equ 0C000h`から見てオフセット0x100(=256)。
一方スプライト1個のレコードは10バイトなので、25番目のスプライト
(0-indexedでidx=25、`sprites+250`)のYH/XHフィールド(レコード内オフセット
+6/+7)がちょうど`sprites+256`/`sprites+257`、つまり`seed`の2バイトと
物理的に重なる。

`loop4`はこの10バイトレコードを`sprites`から順にidx=0,1,2,...と埋めていく
ため、idx=25のY/X座標を書き込んだ直後から、idx=26以降の`call random`が
「idx25のY/X座標だったバイト列」を新しいseedとして読み書きし続けることに
なる。これはROM側の意図しないバグだが、実機で確認済みの実際の挙動なので
そのまま再現する(`init_sprites`参照。素直にPythonの変数でseedを持つのでは
なくRAM相当のbytearrayに読み書きすることで、この衝突が自然に再現される)。

またloop4に入る直前の`seed`の初期値は、openMSXのデバッガで実測すると
`0`だった(電源投入直後のRAMがC-BIOS/openMSXの初期化で0クリアされている
ため)。したがって`init_sprites`は`seed=0`から計算を始めればよく、
ハードコードしたRAMダンプを埋め込む必要はない。

## フレームと録画の対応(LEAD_IN_STEPS)

このROMはsc1_sp06のような明示的な`wait_1sec`を挟まないが、`init`から
`main`ループに実際に入るまでのセットアップ(パターン転送・32スプライト分の
乱数初期化)にも数フレーム分のCPU時間がかかる。openMSXのデバッガで
`main:`到達ごとにBIOSのJIFFYカウンタ(0FC9Eh)を読み、`../asm/capture_openmsx.py`
の`--settle`(既定0.2秒=12フレーム)が使う`after frame`のフレームカウンタと
突き合わせたところ、録画1枚目のフレームは「`init_sprites()`の状態を
S0として5回`advance_sprites`した状態」(=S5)に一致することが実測できた
(`LEAD_IN_STEPS`)。

## 実機キャプチャとの完全一致(ROM側のVSYNC同期の修正について)

このロジック(乱数・初期化・spmoveの固定小数点移動と反射)は実機のRAM
ダンプと1バイトも違わずビット完全一致することを確認済みだが、当初は
録画(../expected/sc1_sp08_openmsx.webm)との比較で120フレーム中29フレーム
にごく僅かなピクセルの食い違いがあった。原因はこのシミュレーションや
描画側ではなく、**ROM(sc1_sp08.asm)側の実際のタイミング競合**だった。
旧版はBIOSのJIFFYを直接ポーリングしてVSYNCを検出し、mainループの中で
`update_vram`(32スプライト分をLDIRVMで4バイトずつ、計32回に分けて転送)を
呼んでいたため、VDPが実際に画面を走査するタイミングとCPUの転送完了が
毎フレーム僅かにズレることがあった。

これをH.TIMIフック(割り込みそのものに同期してVSYNCを検出する方式、
sc1_sp04.asmと同じ手法)に変更し、さらに`update_vram`自体もLDIRVMを32回
呼ぶのではなくVRAM書き込みアドレスを一度だけ設定してポート98hへ直接
128バイトを連続出力する方式に高速化した上で割り込みハンドラ内から呼ぶ
ように変更したところ、録画し直した実機キャプチャと120フレーム全てが
ビット完全一致するようになった(`test_matches_openmsx_capture`で検証)。

参照:
- ソース: ../asm/sc1_sp08.asm
- 解説:   ../docs/sc1_sp08.md

実行方法:
    python sc1_sp08.py                 # 自動テストのみ実行
    python sc1_sp08.py --show          # pygameウィンドウで目視確認
    python sc1_sp08.py --update-expected # ../expected/sc1_sp08.webm を再生成
"""
from test_support import (  # noqa: E402
    add_engine_path, assert_matches_expected_video, compare_to_expected, expected_path_for,
    render_and_write_expected, render_expected_frames, main, SCREEN_WIDTH, SCREEN_HEIGHT, EXPECTED_SCALE,
)

add_engine_path(__file__)

from stage4 import V9918  # noqa: E402

SPRITE_COUNT = 32

# sc1_sp08.asm の sprite_pattern_data1 (8x8, パターン0/1)
PATTERN_8X8 = [
    [0b00111100, 0b01111110, 0b11111111, 0b11011011, 0b11111111, 0b01111110, 0b00111100, 0b00011000],
    [0b00011000, 0b00111100, 0b01111110, 0b11111111, 0b01111110, 0b00111100, 0b00011000, 0b00000000],
]

# sc1_sp08.asm の sprite_pattern_data2 (16x16, パターン4/8)。各行は本来16ビット
# だが、asm側の2進数リテラルには先頭に冗長な0が1桁多く付いている(17桁)。
# 値には影響しないため、変換時に下位16ビットだけを取り出す(& 0xFFFF)。
PATTERN_16X16_ROWS = [
    [
        "00000111111110000", "00011111111111100", "00110111100001110", "00100111011110110",
        "01110110111111011", "01110110111111011", "01110110111111111", "01110110000001111",
        "01110110111110111", "01110110111111011", "01110110111111011", "01110110111111011",
        "00110111011110110", "00110111100001110", "00011111111111100", "00000111111110000",
    ],
    [
        "00000000110000000", "00000001111000000", "00000011111100000", "00000111111110000",
        "00001111111111000", "00011111111111100", "00111111111111110", "01111111111111111",
        "01111111111111111", "00111111111111110", "00011111111111100", "00001111111111000",
        "00000111111110000", "00000011111100000", "00000001111000000", "00000000110000000",
    ],
]


def build_vdp() -> V9918:
    vdp = V9918()
    # sc1_sp08.asm は CHGMOD実行直後にWRTVDPでVDPレジスタ7を直接
    # 4(濃い青)から5(薄い青)へ書き換えている。このタイミングでのR#7書き換えは
    # 実機/C-BIOS上では枠(border)にしか効かず、画面内の背景色(CHGMOD時に
    # カラーテーブルへ焼き込まれたBIOSデフォルトの4)はそのまま変わらない
    # (V9918.set_backdrop_colorのdocstring、sc1_sp01.pyのbuild_vdpと同じ)。
    vdp.set_backdrop_color(5)
    # sc1_sp08.asmのinitはR#1のSI(size)とMAGの両ビットを立てている(16x16拡大)
    vdp.set_sprite_size16(True)
    vdp.set_sprite_mag(True)
    for ch, data in enumerate(PATTERN_8X8):
        vdp.set_sprite_pattern(ch, data)
    for icon_index, rows in enumerate(PATTERN_16X16_ROWS):
        ch = 4 + icon_index * 4
        vdp.set_sprite_pattern16x16(ch, [int(row, 2) & 0xFFFF for row in rows])
    return vdp


def random_step(seed: int) -> int:
    """sc1_sp08.asm の random: と同じLCG。add hl,hlのキャリーをsbc hl,deへ
    明示的に伝播させる(モジュールdocstring参照)。1ステップで(seed, seed)を
    (新しいseed, h/lへの分解)へ更新するので、呼び出し側でh/lを取り出す。
    """
    def add_hl_hl(hl):
        return (hl * 2) & 0xFFFF, 1 if hl & 0x8000 else 0

    def sbc_hl_de(hl, de, carry_in):
        total = hl - de - carry_in
        return (total & 0xFFFF, 1) if total < 0 else (total, 0)

    hl = seed
    de = seed
    hl, c1 = add_hl_hl(hl)
    hl, c2 = add_hl_hl(hl)
    hl, c3 = add_hl_hl(hl)
    hl, c4 = add_hl_hl(hl)
    hl, _ = sbc_hl_de(hl, de, c4)
    hl, c6 = add_hl_hl(hl)
    hl, c7 = add_hl_hl(hl)
    hl, _ = sbc_hl_de(hl, de, c7)
    hl, c9 = add_hl_hl(hl)
    hl, _ = sbc_hl_de(hl, de, c9)
    return (hl + 0x7321) & 0xFFFF


FIELDS = ('dxh', 'dxl', 'dyh', 'dyl', 'xl', 'yl', 'yh', 'xh', 'pat', 'col')
SEED_OFFSET = 0x100  # seed(0C100h) - sprites(0C000h)


def init_sprites():
    """sc1_sp08.asm の loop4 と同じ手順で32スプライト分の初期状態を作る。

    sprites RAM(320バイト)相当のbytearrayに直接読み書きすることで、
    idx=25のY/X座標書き込みがseed(オフセット0x100)と衝突するバグを
    モジュールdocstring通りに自然に再現する。
    """
    ram = bytearray(SPRITE_COUNT * 10)

    def call_random():
        seed = ram[SEED_OFFSET] | (ram[SEED_OFFSET + 1] << 8)
        seed = random_step(seed)
        ram[SEED_OFFSET] = seed & 0xFF
        ram[SEED_OFFSET + 1] = (seed >> 8) & 0xFF
        return (seed >> 8) & 0xFF, seed & 0xFF  # h, l

    ptr = 0
    b = SPRITE_COUNT
    c = 0
    for _ in range(SPRITE_COUNT):
        b_at_entry, c_at_entry = b, c
        for _axis in range(2):  # dx, dy
            h, l = call_random()
            ram[ptr] = 0xFF if (h & 1) else 0x00  # 符号(奇数なら負)
            ptr += 1
            ram[ptr] = l  # 速度の下位(小数部)バイト
            ptr += 1
        ram[ptr] = 0  # XL
        ptr += 1
        ram[ptr] = 0  # YL
        ptr += 1
        b, c = b_at_entry, c_at_entry  # push bc ... pop bc で外側ループの値に戻す
        ram[ptr] = 40 if (b % 2 == 0) else 80  # YH
        ptr += 1
        ram[ptr] = (b * 4) & 0xFF  # XH
        ptr += 1
        ram[ptr] = 8 if (b % 2 == 1) else 4  # パターン番号
        ptr += 1
        color = (c + 2) & 0x0F
        ram[ptr] = color
        ptr += 1
        c = (c + 1) & 0xFF
        if color == 14:  # cp 14 は直前に計算したcolor(=A)と比較している(cではない)
            c = 0
        b -= 1

    return [dict(zip(FIELDS, ram[i * 10:(i + 1) * 10])) for i in range(SPRITE_COUNT)]


def reflect_axis(pos_hi: int, pos_lo: int, vel_hi: int, vel_lo: int, threshold: int):
    """spmove の1軸分(X or Y)。8.8固定小数点で座標を更新し、しきい値
    (Xは0E000h, Yは0A000h)以上になったら反射する(壁で跳ね返る)。
    整数部がちょうど0FFhになった場合は0にクランプする(asmのnot_255x/not_255y)。
    """
    pos = (pos_hi << 8) | pos_lo
    vel = (vel_hi << 8) | vel_lo
    new_pos = (pos + vel) & 0xFFFF
    new_hi = (new_pos >> 8) & 0xFF
    new_lo = new_pos & 0xFF
    if new_pos >= threshold:
        if new_hi == 0xFF:
            new_hi = 0
            new_lo = 0
        vel = (-vel) & 0xFFFF
        vel_hi = (vel >> 8) & 0xFF
        vel_lo = vel & 0xFF
    return new_hi, new_lo, vel_hi, vel_lo


def advance_sprites(sprites):
    """spmove_loop の1周分(32スプライト全部をX,Yそれぞれ1回だけ更新する)。"""
    out = []
    for s in sprites:
        xh, xl, dxh, dxl = reflect_axis(s['xh'], s['xl'], s['dxh'], s['dxl'], 0xE000)
        yh, yl, dyh, dyl = reflect_axis(s['yh'], s['yl'], s['dyh'], s['dyl'], 0xA000)
        out.append(dict(dxh=dxh, dxl=dxl, dyh=dyh, dyl=dyl, xl=xl, yl=yl, yh=yh, xh=xh,
                         pat=s['pat'], col=s['col']))
    return out


# モジュールdocstring「フレームと録画の対応」参照。録画1枚目 = init_sprites()から
# 5回advance_sprites()した状態。Simulation.__init__でLEAD_IN_STEPS-1回進めておき、
# test_support側の最初のrender()(warmup、出力には含まれない)でその状態を描画、
# 最初のstep()呼び出しでちょうど5回目の advance_sprites に到達させる。
LEAD_IN_STEPS = 5
FRAME_COUNT = 120  # ../expected/sc1_sp08_openmsx.webm の実測フレーム数


class Simulation:
    """vdpと32スプライト分の状態だけを持つ状態機械。surfaceの作成・
    vdp.render(surface)の呼び出しは呼び出し側(test_support)の責務。
    """

    def __init__(self):
        self.vdp = build_vdp()
        self.sprites = init_sprites()
        for _ in range(LEAD_IN_STEPS - 1):
            self.sprites = advance_sprites(self.sprites)
        self._sync_vdp()

    def step(self):
        self.sprites = advance_sprites(self.sprites)
        self._sync_vdp()

    def _sync_vdp(self):
        for i, s in enumerate(self.sprites):
            self.vdp.set_sprite(i, s['xh'], s['yh'], s['pat'], s['col'])


def test_random_step_from_zero():
    # loop4に入る直前のseedは実機で0だった(モジュールdocstring参照)。
    # seed=0からのrandom_stepは「0を4回2倍しても0、sbcもキャリー0なら0のまま、
    # 最後に0x7321を足すだけ」になるはずで、実際にそう計算できることを確認する。
    assert random_step(0) == 0x7321


def test_initial_state_matches_hardware():
    # openMSXのデバッガで実機RAM(sprites=0C000h、320バイト)を直接ダンプし、
    # 1バイトも違わないことを確認済みの値の一部(idx0と、seedとの衝突バグが
    # 起きるidx25)をスポットチェックする。
    sprites = init_sprites()
    s0 = sprites[0]
    assert (s0['dxh'], s0['dxl'], s0['dyh'], s0['dyl']) == (255, 33, 255, 45)
    assert (s0['xl'], s0['yl'], s0['yh'], s0['xh']) == (0, 0, 40, 128)
    assert (s0['pat'], s0['col']) == (4, 2)

    # idx25はY/X座標を書き込んだ直後からidx26以降のcall randomがそのバイト列を
    # seedとして読み書きし続けるため、単純な初期化式(y=40/80, x=b*4)通りには
    # ならない(モジュールdocstring参照)。この値も実機ダンプと一致確認済み。
    s25 = sprites[25]
    assert (s25['dxh'], s25['dxl'], s25['dyh'], s25['dyl']) == (255, 226, 255, 107)
    assert (s25['xl'], s25['yl']) == (0, 0)
    assert (s25['yh'], s25['xh']) == (7, 143)
    assert (s25['pat'], s25['col']) == (8, 14)


def test_reflect_axis_bounces_and_negates_velocity():
    # 0DF00h(整数部0xDF) + velocity 0x0100(+1.0px) = 0E000h ちょうど。
    # しきい値(0E000h)以上になったので反射し、速度が反転する。
    new_hi, new_lo, vel_hi, vel_lo = reflect_axis(0xDF, 0x00, 0x01, 0x00, 0xE000)
    assert (new_hi, new_lo) == (0xE0, 0x00)
    assert (vel_hi, vel_lo) == (0xFF, 0x00)


def test_reflect_axis_clamps_when_integer_part_wraps_to_ff():
    # 加算後の整数部がちょうど0FFhになるケースはasm側で0にクランプされる
    # (not_255x/not_255y)。
    new_hi, new_lo, vel_hi, vel_lo = reflect_axis(0xDF, 0x00, 0x20, 0xFF, 0xE000)
    assert (new_hi, new_lo) == (0, 0)
    assert (vel_hi, vel_lo) == (0xDF, 0x01)


def test_matches_expected_video():
    # 他のsc1_spNN.pyと同じく、このシミュレーション自身が生成した
    # ../expected/sc1_sp08.webm とのリグレッション比較(完全一致必須)。
    assert_matches_expected_video(Simulation, FRAME_COUNT, __file__)


def test_matches_openmsx_capture():
    # モジュールdocstring「実機キャプチャとの完全一致」参照。ROM側のVSYNC同期を
    # H.TIMIフック+割り込みハンドラ内での直接VDPポート書き込みに修正した結果、
    # ../expected/sc1_sp08_openmsx.webm(実機キャプチャ)と120フレーム全て
    # ビット完全一致するようになった。
    expected_path = expected_path_for(__file__, "sc1_sp08_openmsx.webm")
    actual = render_expected_frames(Simulation, FRAME_COUNT)
    compare_to_expected(actual, expected_path, SCREEN_WIDTH, SCREEN_HEIGHT, EXPECTED_SCALE, __file__)


def update_expected():
    render_and_write_expected(Simulation, FRAME_COUNT, __file__)


if __name__ == "__main__":
    main(globals(), Simulation, "sc1_sp08", update_expected=update_expected)
