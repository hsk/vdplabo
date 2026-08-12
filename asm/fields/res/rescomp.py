import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
# MSX SCREEN 2 用リソースコンパイラ rescomp.py
# rescomp.py は画像ファイルから MSX SCREEN 2 用のパターンテーブル、カラーテーブル、ネームテーブルを生成するツールです。
# pygame を使用して画像を読み込み、MSX SCREEN 2 の制約に合わせてデータを変換します。
#
# 生成したデータはアセンブラから利用できる形式で標準出力へ出力します。
#
# ## 入力
#
# 入力は PNG などの画像ファイルです。
#
# ```text
# rescomp.py image.png [start_pattern_no]
# ```
# 
# image.png 画像は 8x8 ドット単位で分割して処理します。
# start_pattern_noはオプションで開始パターン番号を指定します。
# start_pattern_noはデフォルト0です。
# 
# ## 出力
# 
# 以下のデータを生成します。
# 
# - パターンテーブル
# - カラーテーブル
# - ネームテーブル
# 
# 必要に応じてラベル付きのアセンブラソースとして出力します。
# 
# ## パターンの生成
# 
# まず画像を8x8の画像データとして分割して処理し、パターンとカラーデータを作り連想配列にデータから作った名前で保存し、同時にネームテーブルを作ります。
# ネームテーブルのパターン番号はstart_pattern_noから始まり、新しいパターンならばインクリメントされます。
# パターン生成時に、２色以上使っているラインがあれば、エラー出力しつつ、１６番目の色を赤にして置き換えた画像を生成しエラー画像を作ってユーザーに提示します。
def gen_pattern(filename, ptn_no=0):
    img = pygame.image.load(filename)
    w, h = img.get_size()

    pattern_data = {}
    name_data = []

    for y in range(0, h, 8):
        row = []
        for x in range(0, w, 8):
            ptn = gen_pattern8x8(img, x, y)

            if ptn not in pattern_data:
                pattern_data[ptn] = ptn_no
                ptn_no += 1

            row.append(pattern_data[ptn])

        name_data.append(row)

    name = os.path.splitext(os.path.basename(filename))[0]
    output_bg(name, pattern_data, name_data)

# 8x8のパターン(パターン８バイトと色8バイトの16バイト)を生成
def gen_pattern8x8(img, x1, y1):
    pattern_bytes = []
    color_bytes = []

    for y in range(8):
        colors = []

        for x in range(8):
            c = img.get_at_mapped((x1 + x, y1 + y))
            color = c & 0x0F
            colors.append(color)

        used = sorted(set(colors))

        if len(used) == 0:
            fg = 0
            bg = 0
        elif len(used) == 1:
            fg = used[0]
            bg = used[0]
        else:
            fg = used[1]
            bg = used[0]

        pattern = 0
        for x in range(8):
            if colors[x] == fg:
                pattern |= 1 << (7 - x)

        pattern_bytes.append(pattern)
        color_bytes.append((fg << 4) | bg)

    return bytes(pattern_bytes + color_bytes)

# ## 背景データ生成
# 生成する名前はファイル名の拡張子を取り除いたものに_pattern_data、_color_data、_name_dataをつけたラベルをつけて出力されます。
# パターンの連想配列からパターンデータ、カラーテーブルを出力します。
# 生成したネームテーブルからネームテーブルを出力します。
def output_bg(name, pattern_data, name_data):
    print(f"{name}_pattern_data:")

    sorted_patterns = sorted(pattern_data.items(), key=lambda x: x[1])

    for ptn, i in sorted_patterns:
        data = list(ptn[:8])
        print("    db " + ",".join(f"${v:02x}" for v in data) + " ; " + str(i))

    print()
    print(f"{name}_color_data:")

    for ptn, i in sorted_patterns:
        data = list(ptn[8:16])
        print("    db " + ",".join(f"${v:02x}" for v in data) + " ; " + str(i))

    print()
    print(f"{name}_name_data:")

    for row in name_data:
        print("    db " + ",".join(f"{v:3d}" for v in row))

# 背景は 64x20 などの仮想画面サイズにも対応できるようにし、後のスクロール処理で利用できるデータを出力します。#
if __name__ == '__main__':
    import sys

    pygame.init()

    if len(sys.argv) < 2:
        print('usage: rescomp.py image.png [start_pattern_no]')
        sys.exit(1)

    filename = sys.argv[1]
    start_pattern_no = int(sys.argv[2]) if len(sys.argv) >= 3 else 0

    gen_pattern(filename, start_pattern_no)
