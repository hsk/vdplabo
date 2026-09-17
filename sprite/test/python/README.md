# Python版テスト

[../asm/](../asm) の実機サンプル(`scN_spNN.asm`)と1対1で対応させ、
[../../engine/python/](../../engine/python) のエンジンで同じVRAM設定を再現して検証するテストです。

- ファイル名はasmファイルと同じにします (例: `sc1_sp01.asm` → `sc1_sp01.py`)
- asmの初期化処理(スプライトパターン/属性テーブルの設定)を再現し、
  実行結果の期待値([../docs/](../docs)の解説を参照)をピクセル単位でアサートします
- asm側の挙動に忠実に合わせます。関数単位で見ると分かりにくい制御フロー
  (レジスタが関数境界をまたいで生き残るなど)もあるので、ラベル単位ではなく
  実際の実行順序を追って確認すること。例えば `sc1_sp01.asm` は
  `screen_init`単体を見るとスプライト拡大の`WRTVDP`呼び出しが無いように見えるが、
  次の`pattern_name_table_init`の先頭が`call WRTVDP`になっており、
  `ret`/`call`はBCレジスタを壊さないため実際には拡大が効く(要注意点)

## 実行方法

```sh
python sc1_sp01.py          # 自動テストのみ実行 (pygameウィンドウは開かない)
python sc1_sp01.py --show   # pygameウィンドウで目視確認
```

pytestは使わず、`test_`で始まる関数をファイル自身が実行する簡易ランナーにしています
(依存を増やさないため)。ただし関数名の規約は合わせてあるので、将来pytestを導入した場合もそのまま拾えます。

## golden動画による検証

静止画1枚(`sc1_sp01`など)・アニメーション(`sc1_sp06`など)を問わず、
[video_golden.py](video_golden.py) を使って録画したロスレスwebm
([goldens/](goldens)以下, 例: `goldens/sc1_sp01.webm`)と実行結果を
フレームごとにピクセル単位で比較します(静止画は1フレームのwebmとして扱います)。
これとは別に、期待される座標のピクセル色を直接アサートするテストも用意しています
(goldenファイルを作る前の設計確認や、特定ピクセルだけの素早いチェックに便利なため)。

- webmは`libvpx-vp9`の`gbrp`(RGBのままVP9符号化、色空間変換なし)でエンコードしているため
  ビット完全一致で比較でき、輪郭のにじみ(クロマブリーディング)も出ません。
  通常のyuv420p/yuv444pは`-lossless 1`でもRGB→YUV変換の丸め誤差でにじみが出て
  ビット完全一致しないため使っていません(H.264の`libx264rgb`も試したが、
  ブラウザでの再生互換性がVP9の`gbrp`=Profile 1より劣るためVP9を採用)
- goldenは実寸(256x192)ではなく、ニアレストネイバーで**4倍**(1024x768)に
  拡大して保存します。ドット絵なので拡大しても劣化せずビット完全一致比較でき、
  かつそのまま見やすいファイルとしても使えるので、比較用と目視確認用を兼用しています
  (比較時はテスト側も同じ倍率でフレームを拡大してから突き合わせます)
- QuickTime Playerはwebm自体に非対応です(VLC/IINA/ffplayなら再生可)。
  目視確認は`--show`のpygameウィンドウでも可能です
- goldenの新規作成/更新は `python sc1_sp01.py --update-golden` のように
  各テストファイルを`--update-golden`付きで実行します
- さらに拡大した別ファイルが欲しい場合(SNS投稿用など)は
  `python video_golden.py goldens/sc1_sp06.webm --scale 5 --open` のように
  goldenを入力にして`video_golden.py`単体でも拡大できます(`*_view.webm`はgitignore対象)
- このwebm golden方式は、将来openMSXや自作エミュレータが出力するフレーム列にも
  同じ`video_golden.py`をそのまま使い回すことを想定しています

`ffmpeg`がPATH上にある必要があります(`brew install ffmpeg`)。

## sandbox/

どのasmサンプルとも対応しない実験用スクリプトの置き場です。
