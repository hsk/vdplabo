# ----------------------------------------
# V9938 Sprite Mode 2 emulator
# ----------------------------------------
import pygame
import sys
import random
import math
class V9938:
    SCREEN_WIDTH  = 256
    # SCREEN5-8(V9938のビットマップモード)はSCREEN1と違い212ライン表示
    # (実測: CHGMODでSCREEN5にした時点でR#9のLNビットが立ち、可視領域が
    # 192ではなく212ラインになる。openMSXキャプチャとの比較で、192決め打ち
    # だと上下10ラインずつが誤って枠(border)側に分類されることが判明した)。
    # SCREEN4(GRAPHIC3)はR#9のLNビットが立たず192ライン表示のまま
    # (openMSXキャプチャのボーダー幅の実測で確認済み)なので、V9938(screen_height=192)
    # のようにコンストラクタ引数で切り替える。デフォルトは従来通り212。
    SCREEN_HEIGHT = 212
    # openMSXの生キャプチャ(枠込み)に合わせたキャンバス全体のサイズ。
    # 可視領域(SCREEN_WIDTH/HEIGHT)はこの中央に配置される。
    CANVAS_WIDTH = 320
    CANVAS_HEIGHT = 240
    BORDER_X = (CANVAS_WIDTH - SCREEN_WIDTH) // 2   # 32
    BORDER_Y = (CANVAS_HEIGHT - SCREEN_HEIGHT) // 2  # 14
    SPRITE_COUNT = 32
    SPRITE_PATTERN_COUNT = 256
    SPRITE_LIMIT = 8
    VRAM_SIZE = 128 * 1024
    PALETTE = [
        (0, 0, 0),         # 0 Transparent
        (0, 0, 0),         # 1 Black
        (43, 221, 43),     # 2 Medium green
        (118, 255, 118),   # 3 Light green
        (43, 43, 255),     # 4 Dark blue
        (81, 118, 255),    # 5 Light blue
        (187, 43, 43),     # 6 Dark red
        (81, 221, 255),    # 7 Cyan
        (255, 43, 43),     # 8 Medium red
        (255, 118, 118),   # 9 Light red
        (221, 221, 43),    # 10 Dark yellow
        (221, 221, 153),   # 11 Light yellow
        (43, 153, 43),     # 12 Dark green
        (221, 81, 187),    # 13 Magenta
        (187, 187, 187),   # 14 Gray
        (255, 255, 255),   # 15 White
    ]
    # VDPレジスタ16(パレットデータ)のR/G/B各3bit値(0-7)を8bit RGBへ変換する表。
    # 実機のDAC変換カーブは単純な線形ではないため、上のPALETTE定数
    # (probe_palette.pyでopenMSX実機から実測した値)から各色のR/G/B成分を
    # 逆算して求めた8段階(0,43,81,118,153,187,221,255)を使う。
    RGB_LEVELS = (0, 43, 81, 118, 153, 187, 221, 255)
    def __init__(self, screen_height=SCREEN_HEIGHT):
        self.SCREEN_HEIGHT = screen_height
        self.BORDER_Y = (self.CANVAS_HEIGHT - screen_height) // 2
        self.vram = bytearray(self.VRAM_SIZE)
        self.reg = bytearray(12)
        self.stat = bytearray(1)
        # パレット(R#16)はインスタンスごとにPALETTEのコピーを持ち、
        # set_paletteで一部の色番号だけ差し替えられるようにする
        # (CHGMODはBIOSデフォルトのパレットを再現するが、実機/asm側が
        # R#16で書き換えた番号だけ変わり、残りはデフォルトのまま)。
        self.palette = list(self.PALETTE)
        self.set_sprite_pattern_table(0x1b00)
        self.set_sprite_attribute_table(0x3800)
        # 実機(V9938)は未使用スプライトのY座標に終端マーカー216を置いて
        # スキャンを打ち切る(sprite2.md参照)。set_sprite()を呼んでいない
        # エントリはVRAM初期値0のままだと「Y=0の実在スプライト」として
        # 誤って第9スプライト判定に数えられてしまうため、コンストラクタで
        # 全エントリを216(終端)にしておく。
        for i in range(self.SPRITE_COUNT):
            self.vram[self.get_sprite_attribute_table() + i * 4] = 216
        self.set_sprite_mag(False)
        self.set_sprite_size16(False)
        self.set_spd(False)
        self.set_5s(False)
        self.set_5s_index(0)
        self.set_collision(False)
        self.set_backdrop_color(4)  # BIOSデフォルト(BAKCLR=4, 青)
        self.screen_bg_color = 4  # BIOSがCHGMOD時にVRAM(ビットマップ)へ焼き込む背景色
    def set_backdrop_color(self, value):
        """VDPレジスタ7(border/backdrop)を設定する。

        GRAPHIC系モードではこのレジスタは実機上「枠(border)」のみを制御し、
        画面内(ビットマップが描く可視領域)の背景色には影響しない
        (CHGMOD実行後にWRTVDPで直接R#7を書き換えても、枠だけが変わり
        画面内背景は変わらないことをC-BIOS/openMSXで実測して確認済み。
        sprite1/stage4.pyのV9918.set_backdrop_colorと同じ。画面内背景を
        変えたい場合はset_screen_background_colorを使う)。
        """
        self.reg[7] = (self.reg[7] & 0xF0) | (value & 0x0F)
    def get_backdrop_color(self):
        return self.reg[7] & 0x0F
    def set_palette(self, index, r, g, b):
        """VDPレジスタ16(パレットデータ)相当。r,g,bはV9938の3bit値(0-7)。

        指定したindexだけを書き換える(他の色番号はPALETTEのデフォルトのまま)。
        """
        self.palette[index & 0x0F] = (
            self.RGB_LEVELS[r & 7], self.RGB_LEVELS[g & 7], self.RGB_LEVELS[b & 7],
        )
    def get_palette(self, index):
        return self.palette[index & 0x0F]
    def set_screen_background_color(self, value):
        """画面内(可視領域)の背景色を設定する。

        実機ではCHGMOD実行時にBAKCLRワークエリアの値がVRAM(ビットマップ)へ
        焼き込まれることで決まる(このエンジンはビットマップそのものは
        再現していないため、可視領域の背景色として直接保持する)。
        """
        self.screen_bg_color = value & 0x0F
    def get_screen_background_color(self):
        return self.screen_bg_color
    def set_sprite_pattern_table(self, addr):
        self.reg[6] = (addr >> 11) & 0x3F
    def get_sprite_pattern_table(self):
        return (self.reg[6] & 0x3F) << 11
    def set_sprite_attribute_table(self, addr):
        # R#5のA9ビット(bit0-1)は必ず1に設定する。
        self.reg[5] = ((addr >> 7) & 0b11111100) | 0b11
        self.reg[11] = (addr >> 15) & 0b11
    def get_sprite_attribute_table(self):
        addr = (self.reg[11] & 0b11) << 15
        addr |= (self.reg[5] & 0b11111100) << 7
        return addr
    def get_sprite_color_table(self):
        # 専用レジスタは存在せず、SATアドレスから自動的に(512を引いた値に)決まる。
        return (self.get_sprite_attribute_table() - 512) & (self.VRAM_SIZE - 1)
    def set_sprite_mag(self, value):
        self.reg[1] &= ~1
        self.reg[1] |= 1 if value else 0
    def get_sprite_mag(self):
        return (self.reg[1] & 1) != 0
    def set_sprite_size16(self, value):
        self.reg[1] &= ~2
        self.reg[1] |= 2 if value else 0
    def get_sprite_size16(self):
        return (self.reg[1] & 2) != 0
    def set_spd(self, value):
        self.reg[8] &= ~2
        self.reg[8] |= 2 if value else 0
    def get_spd(self):
        return (self.reg[8] & 2) != 0
    def set_collision(self, value):
        self.stat[0] &= ~(1<<5)
        self.stat[0] |= (1<<5) if value else 0
    def get_collision(self):
        return (self.stat[0] & (1<<5)) != 0
    def set_5s(self, value):
        self.stat[0] &= ~(1<<6)
        self.stat[0] |= (1<<6) if value else 0
    def get_5s(self):
        return (self.stat[0] & (1<<6)) != 0
    def set_5s_index(self, value):
        self.stat[0] &= ~(31)
        self.stat[0] |= value & 31
    def get_5s_index(self):
        return self.stat[0] & 31
    def set_sprite_pattern(self, ch, data):
        addr = self.get_sprite_pattern_table() + ch * 8
        for i in range(8):
            self.vram[addr] = data[i]
            addr += 1
    def set_sprite_color(self, ch, colors):
        # 実機のスプライトカラーテーブルは、8x8/16x16のサイズ設定に関わらず
        # 1スプライトあたり常に16バイト固定でストライドする(16x16時の
        # 16ライン分を格納できるよう確保されており、8x8時は先頭8バイトだけが
        # 使われる)。sc5_sp04.asmはこの実機仕様に依存しており、意図的に
        # 「1個先のスプライト」のcolorオフセット(+16)へBIGFILしているのに
        # openMSX実機キャプチャではその隣のスプライトの色として反映される
        # (実測して確認済み。ストライドを8にしていると再現できない)。
        addr = self.get_sprite_color_table() + ch * 16
        for i in range(8):
            self.vram[addr] = colors[i]
            addr += 1
    def set_sprite_pattern16x16(self, ch, data):
        base = ch & 0xFC
        p = [[],[],[],[]]
        for y in range(16):
            row = data[y]
            p[0+(y//8)*2].append((row >> 8) & 0xFF)
            p[1+(y//8)*2].append(row & 0xFF)
        for i in range(4):
            self.set_sprite_pattern(base + i, p[i])
    def set_sprite(self, no, x, y, pattern, color, ec = False):
        addr = self.get_sprite_attribute_table() + no * 4
        self.vram[addr + 0] = y & 0xff
        self.vram[addr + 1] = x & 0xff
        self.vram[addr + 2] = pattern & 0xff
        self.vram[addr + 3] = (color | (128 if ec else 0)) & 0xff
    def render(self, surface):
        """surfaceはCANVAS_WIDTH x CANVAS_HEIGHT(320x240, 枠込み)を想定する。

        枠(border)全体をget_backdrop_color()で塗った上で、可視領域
        (SCREEN_WIDTH x SCREEN_HEIGHT)だけをsubsurfaceとして切り出し、
        get_screen_background_color()で塗ってからスプライトを描画する。
        枠色と画面内背景色は実機上別々に決まる(set_backdrop_colorの
        docstring参照)ため、この2つは独立に塗り分ける。subsurfaceは
        親と同じピクセルバッファを指すため、render_line_sprites側は
        可視領域ローカル座標のまま変更不要。
        """
        self._surface = surface
        surface.fill(self.palette[self.get_backdrop_color()])
        active = surface.subsurface((self.BORDER_X, self.BORDER_Y, self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        active.fill(self.palette[self.get_screen_background_color()])
        self.set_5s(False)
        # 実機の仕様: 第5(9)スプライトフラグが立っていない時、5S#には
        # 終端マーカー(216)自身のインデックスが入る(216が無い=32個全部
        # 使われている場合は31。openMSXキャプチャとの実測で確認済み)。
        # オーバーフローが一度も起きなければこの値のまま、起きれば
        # render_line_sprites側がset_5s(True)と一緒に上書きする。
        self.set_5s_index(self._last_sprite_index())
        self.set_collision(False)
        if self.get_spd(): return
        for y in range(self.SCREEN_HEIGHT):
            self.render_line_sprites(active, y)
    def _last_sprite_index(self):
        attr_addr = self.get_sprite_attribute_table()
        for i in range(self.SPRITE_COUNT):
            if self.vram[attr_addr + i * 4] == 216:
                return i
        return 31
    def get_at(self, x, y):
        """直前のrender()で使われたsurfaceの、可視領域ローカル座標(x, y)のRGB値を返す。"""
        return self._surface.get_at((x + self.BORDER_X, y + self.BORDER_Y))[:3]
    def render_line_sprites(self, surface, y):
        sprites_on_line = 0
        draw_log = bytearray(self.SCREEN_WIDTH)
        attr_addr = self.get_sprite_attribute_table()
        color_table = self.get_sprite_color_table()
        pattern_table = self.get_sprite_pattern_table()
        mag = 2 if self.get_sprite_mag() else 1
        size = (16 if self.get_sprite_size16() else 8) * mag
        # このラインで自分より前(小さいindex)に実在したスプライトが既にあったか。
        # CCビット(0x40)が立ったスプライトは、Xが重なっていなくても「このライン上に
        # 前のスプライトが(Xの重なりに関係なく)存在した場合だけ」表示され、
        # 無ければそのライン全体で何も描かれない実機仕様がある
        # (sc5_sp05_openmsx.webmを実測して確認済み: index番号最小のCCスプライトが
        # 単独で乗るラインは完全に非表示になるが、より小さいindexの非CCスプライトが
        # 同じラインのどこかに存在すれば、Xが重ならなくてもCCスプライト自身の色で
        # ソロ表示される。sc5_sp04.pyのケースはたまたま2枚のY範囲が完全に一致していた
        # ため、このライン単位の判定と従来のピクセル単位判定の違いが表面化しなかった)。
        has_prior_sprite = False
        for i in range(self.SPRITE_COUNT):
            spr_y = self.vram[attr_addr + 0]
            x = self.vram[attr_addr + 1]
            spr_ptn = self.vram[attr_addr + 2]
            color_byte = self.vram[attr_addr + 3]
            attr_addr += 4
            if spr_y == 216: return  # V9938スプライトモード2の終端マーカー(sprite2.md参照。MSX1のモード1は208)
            spr_y = (spr_y + 1) & 255
            if color_byte & 0x80: x -= 32
            if not (spr_y <= y < spr_y + size): continue
            sprites_on_line += 1
            if sprites_on_line > self.SPRITE_LIMIT:
                self.set_5s(True)
                self.set_5s_index(i)
                return
            py = y - spr_y
            if mag == 2: py >>= 1
            if self.get_sprite_size16():
                spr_ptn = spr_ptn & 0xFC
                if py >= 8:
                    spr_ptn += 2
                    py -= 8
                blocks = [spr_ptn, spr_ptn + 1]
            else:
                blocks = [spr_ptn]
            row_color = self.vram[color_table + i * 16 + py]
            cc_bit = (row_color & 0x40) != 0
            color_index = row_color & 0x0F
            if cc_bit and not has_prior_sprite:
                has_prior_sprite = True
                continue
            has_prior_sprite = True
            if color_index == 0: continue
            color = self.palette[color_index]
            for pat_no in blocks:
                bits = self.vram[pattern_table + (pat_no * 8) + py]
                for px in range(8):
                    for _ in range(mag):
                        if 0 <= x < self.SCREEN_WIDTH and bits & (0x80 >> px):
                            if draw_log[x] == 0:
                                draw_log[x] = color_index
                                surface.set_at((x, y), color)
                            else:
                                self.set_collision(True)
                                if cc_bit:
                                    draw_log[x] |= color_index
                                    surface.set_at((x, y), self.palette[draw_log[x]])
                        x += 1
if __name__ == "__main__":
    vdp = V9938()
    def machine(rom):
        rom.init()
        pygame.init()
        SCALE = 3
        window = pygame.display.set_mode(
            (vdp.CANVAS_WIDTH * SCALE, vdp.CANVAS_HEIGHT * SCALE)
        )
        pygame.display.set_caption("V9938 Sprite Emulator")
        screen = pygame.Surface((vdp.CANVAS_WIDTH, vdp.CANVAS_HEIGHT))
        clock = pygame.time.Clock()
        frame = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            rom.run(frame)
            vdp.render(screen)
            if vdp.get_collision():
                print("SPRITE COLLISION")
            if vdp.get_5s():
                print(f"SPRITE OVERFLOW: 9th sprite={vdp.get_5s_index()}")
            scaled = pygame.transform.scale(
                screen,
                (vdp.CANVAS_WIDTH * SCALE, vdp.CANVAS_HEIGHT * SCALE)
            )
            window.blit(scaled, (0, 0))
            pygame.display.flip()
            frame += 1
            clock.tick(60)
    class ROM:
        def init(self):
            # Sprite 0 pattern
            vdp.set_sprite_pattern(0, [
                0b00111100,
                0b01111110,
                0b11111111,
                0b11011011,
                0b11111111,
                0b01111110,
                0b00111100,
                0b00011000,
            ])
            # Sprite 1 pattern
            vdp.set_sprite_pattern(1, [
                0b00011000,
                0b00111100,
                0b01111110,
                0b11111111,
                0b01111110,
                0b00111100,
                0b00011000,
                0b00000000,
            ])
            # 16x16 sprite patterns
            vdp.set_sprite_pattern16x16(4,[
                0b0001111111111000,
                0b0011111111111100,
                0b0110111100001110,
                0b0100111011110110,
                0b1110110111111011,
                0b1110110111111011,
                0b1110110111111111,
                0b1110110000001111,
                0b1110110111110111,
                0b1110110111111011,
                0b1110110111111011,
                0b1110110111111011,
                0b0110111011110110,
                0b0110111100001110,
                0b0011111111111100,
                0b0001111111111000,
            ])
            # Another 16x16 sprite pattern
            vdp.set_sprite_pattern16x16(8,[
                0b0000000110000000,
                0b0000001111000000,
                0b0000011111100000,
                0b0000111111110000,
                0b0001111111111000,
                0b0011111111111100,
                0b0111111111111110,
                0b1111111111111111,
                0b1111111111111111,
                0b0111111111111110,
                0b0011111111111100,
                0b0001111111111000,
                0b0000111111110000,
                0b0000011111100000,
                0b0000001111000000,
                0b0000000110000000,
            ])
            # 重ね合わせデモ用の8x8塗りつぶし円パターン(ベン図らしく丸にする)
            vdp.set_sprite_pattern(2, [
                0b00111100,
                0b01111110,
                0b11111111,
                0b11111111,
                0b11111111,
                0b11111111,
                0b01111110,
                0b00111100,
            ])
            self.sps = [{} for _ in range(29)]
            # Create sprites
            for i,s in enumerate(self.sps):
                s["x"] = 16 + i * 6
                s["y"] = 40 + (i % 2) * 40
                s["color"] = (i % 14) + 2
                s["dx"] = random.randint(-20,20)/10.0
                s["dy"] = random.randint(-20,20)/10.0
                vdp.set_sprite_color(i, [s["color"]]*8)
            # 残り3枚(29,30,31番)はCCビットを立てた重ね合わせデモ用に固定で使う。
            # 3枚が同じ中心の周りを回りながら、半径が伸び縮みして
            # 近づいて重なったり離れたりを繰り返す。重なった瞬間は色がORされて変わる。
            self.venn_center = (24, 20)
            self.venn = [
                {"index": 29, "phase": 0.0, "color": 2},              # Medium green
                {"index": 30, "phase": 2 * math.pi / 3, "color": 4},  # Dark blue
                {"index": 31, "phase": 4 * math.pi / 3, "color": 8},  # Medium red
            ]
            for v in self.venn:
                vdp.set_sprite_color(v["index"], [v["color"] | 0x40]*8)
            self.mode = 3
        def run(self,frame):
            if frame % 180 == 0:
                self.mode = (self.mode + 1) & 3
                vdp.set_sprite_size16(self.mode >= 2)
                vdp.set_sprite_mag((self.mode % 2) == 1)
            size = 16 if vdp.get_sprite_size16() else 8
            size = size * 2 if vdp.get_sprite_mag() else size
            if frame % 180 == 0:
                for i, s in enumerate(self.sps):
                    if s["x"] >= 256 - size: s["x"] = 256 - size - 1
                    if s["y"] >= 192 - size: s["y"] = 192 - size - 1
                    if vdp.get_sprite_size16():
                        s["pattern"] = ((i % 2) + 1) * 4
                    else:
                        s["pattern"] = i % 2
            # 重ね合わせデモの3枚: 半径が伸び縮みしながら共通の中心を回り、
            # 近づいて重なる瞬間と離れる瞬間を繰り返す。
            venn_pattern = 8 if vdp.get_sprite_size16() else 2
            radius = 4 + 4 * math.sin(frame * 0.02)
            cx, cy = self.venn_center
            for v in self.venn:
                angle = v["phase"] + frame * 0.03
                vx = cx + radius * math.cos(angle)
                vy = cy + radius * math.sin(angle)
                vdp.set_sprite(v["index"], int(vx), int(vy), venn_pattern, v["color"])
            for i, s in enumerate(self.sps):
                s["x"] += s["dx"]
                s["y"] += s["dy"]
                if not (0 < s["x"] < 256 - size): s["dx"] = -s["dx"]
                if not (0 < s["y"] < 192 - size): s["dy"] = -s["dy"]
                vdp.set_sprite(i, int(s["x"]), int(s["y"]), s["pattern"], s["color"])
    machine(ROM())
