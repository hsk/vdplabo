# スプライトモード1/2に関するアセンブラサンプルコード

ここには、スプライトモード1(`sc1_sp*`)とスプライトモード2(`sc5_sp*`)に関するサンプルコードがあります。

詳しくは [ドキュメント](../docs/README.md) を見てください。

## ビルド・実行方法

```sh
make sc1_sp01   # sc1_sp01.asm をビルドし、rom/sc1_sp01.rom を openMSX で実行
make sc5_sp01   # sc5_sp01.asm をビルドし、rom/sc5_sp01.rom を openMSX で実行
```

各ファイル名がそのままターゲット名になっている。`sc1_sp01`〜`sc1_sp08`は`z88dk-z80asm`で、
`sc5_sp01`〜`sc5_sp07`(`sc5_sp03_2`, `sc5_hra`含む)は`glass-0.6.jar`でビルドし、
どちらも`openmsx -carta rom/<ターゲット名>.rom`で起動する。

```sh
make        # 全ターゲットを順番にビルド・実行
make clean  # rom/*.rom を削除
```

## reference/

`sc5_sp*`シリーズとは別に置いている第三者製の参考実装。詳しくは [reference/README.md](reference/README.md) を参照。

## openMSXでの自動録画 (capture_openmsx.py)

実機(openMSX)で実際に動かした結果を録画し、[../python/](../python) の
エンジンで再現した [../expected/](../expected) のgoldenと見比べるためのツール。

```sh
python capture_openmsx.py rom/sc1_sp01.rom --boot-wait 6.5 --duration 1
```

- 録画には`record`コマンドを使う。openMSXの`record`はZMBV(Zip Motion Blocks
  Video)というロスレスコーデックでAVIに保存する。ffmpegがZMBVのデコーダを
  内蔵しているのでそのまま読める
- `-control stdio`で自動操作すると、実際にはウィンドウを作らずヘッドレス的に
  動いてしまい、`screenshot`/`record`が"成功した"と返してきても中身が
  不定(ノイズ)になったりファイルが作られなかったりする(実測して確認済み)。
  そのため`-script`に渡すTclファイルの中で`after <ms> ...`を使い、
  録画の開始・終了・終了処理をあらかじめスケジュールする方式にしている
  (これなら通常起動と同じくウィンドウが正しく作られる)
- Tclの`after`の遅延コマンドは`{...}`で1引数にまとめず、スペース区切りの
  複数引数のまま渡すこと。`after 3000 record start foo.avi`はOKだが
  `after 3000 {record start foo.avi}`は`invalid command name`になる
  (原因不明、要注意点として記録)
- 起動直後はC-BIOSのロゴ画面が表示される。ロゴが終わって実際のROMの
  `init`が始まるまでの時間は実行ごとにばらつきがあった(5秒でもまだ
  ロゴのままのことがあった)。`--boot-wait`は余裕を持った値にすること
- 録画される画面は320x240で、可視領域256x192の周囲にボーダー(枠)が
  付いた状態。中央寄せと仮定して単純にクロップしている
  (`BORDER_X=32, BORDER_Y=24`)。この前提が崩れるケース(枠色が
  非対称など)は未検証
- 背景色(枠の内側の背景)はpythonエンジン側(stage4)がR#7未実装のため
  黒固定だが、実機/openMSXでは実際に青(BIOSデフォルトのBAKCLR=4)になる。
  スプライト自体のピクセルは一致することを確認済み
