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
エンジンで再現した [../expected/](../expected) の期待値と見比べるためのツール。

```sh
python capture_openmsx.py rom/sc1_sp01.rom --settle 0.2 --duration 1
```

webmまで一括で作りたい場合は出力先の拡張子を`.webm`にすると、
録画→クロップ→ニアレストネイバー4倍拡大→保存までまとめて行う。
Makefileからは`make capture ROM=<ターゲット名>`で1コマンドで実行できる
(先に`make <ターゲット名>`でromを作っておくこと)。

```sh
make sc1_sp05             # rom/sc1_sp05.rom を作る
make capture ROM=sc1_sp05 # ../expected/sc1_sp05_openmsx.webm を作る
```

- 録画には`record`コマンドを使う。openMSXの`record`はZMBV(Zip Motion Blocks
  Video)というロスレスコーデックでAVIに保存する。ffmpegがZMBVのデコーダを
  内蔵しているのでそのまま読める
- `-control stdio`で自動操作すると、実際にはウィンドウを作らずヘッドレス的に
  動いてしまい、`screenshot`/`record`が"成功した"と返してきても中身が
  不定(ノイズ)になったりファイルが作られなかったりする(実測して確認済み)。
  そのため`-script`に渡すTclファイルの中で`after time <seconds> ...`を使い、
  録画の開始・終了・終了処理をあらかじめスケジュールする方式にしている
  (これなら通常起動と同じくウィンドウが正しく作られる)
- Tclの`after`の遅延コマンドは`{...}`で1引数にまとめず、スペース区切りの
  複数引数のまま渡すこと。`after time 3 record start foo.avi`はOKだが
  `after time 3 {record start foo.avi}`は`invalid command name`になる
  (原因不明、要注意点として記録)
- `after <ms>`(サブコマンド無しの素のフォーム)は`after realtime`と同じ
  ホストの壁時計(実時間)ベースで、ホストの負荷次第でどのエミュレート
  フレームで発火するかにブレが出る(../input/README.mdのキー入力精度の
  問題で実測して発覚)。`after time <seconds>`はエミュレート側のCPU/VDP
  サイクルに同期したクロック(Scheduler)を使うため、ホストの状況に関係なく
  完全に決定論的に発火する(openMSXソース src/events/AfterCommand.cc で確認)。
  録画開始・停止の秒数程度ならブレていても実害は無かったが、フレーム単位で
  タイミングを合わせたい用途(キー入力など)では`after time`必須
- 起動直後はC-BIOSのロゴ画面が表示され、実際のROMの`init`が始まるまでの
  時間は実時間待ちだと実行ごとにばらつきがあった(5秒でもまだロゴのまま
  のことがあった)。そこで実時間の`--boot-wait`ではなく、**ROMヘッダの
  `dw init`(オフセット2-3バイト)から`init`の実アドレスを直接計算し、
  openMSXのデバッガでそのアドレスにブレークポイントを張って実行到達を
  検出する**方式にした。これはエミュレート内部の時間に基づくため
  完全に決定論的(複数回実行して寸分違わず同じフレームでヒットすることを
  確認済み)。`--settle`はブレークポイント到達後、録画開始までの
  待ち秒数(init自体の実行は一瞬なので短くて良い、デフォルト0.2秒)
  - ブレークポイントのコールバック内で`puts`しても画面内コンソールにしか
    出ずOSの標準出力には流れないので、結果を取り出したい場合はTclの
    `open`/`puts`/`close`でファイルに直接書き込む必要がある(ハマりポイント)
  - この方式はopenMSXのデバッガ機能に依存しているため、FPGA実機などの
    HDMIキャプチャには使えない。そちらは映像の中身から同期点を検出する
    別のアプローチが必要になる
- 録画される画面は320x240(SCREEN5以降でも実測で同じ320x240になることを
  確認済み)。以前は可視領域256x192だけを中央寄せと仮定してクロップしていたが、
  SCREEN5以降は可視領域が256x212/512x212など可変な上、枠色(BDRCLR)自体も
  テスト対象にしたいため、今はクロップせず320x240のまま比較する
  (python側エンジンも同じ320x240キャンバスに可視領域を中央配置して描画する。
  `engine/python/sprite{1,2}/stage4.py`のCANVAS_WIDTH/HEIGHT参照)
- 背景色(枠色含む)はpythonエンジン側(stage4)もR#7(get_backdrop_color)を
  実装済みで、実機/openMSXの値と比較対象になる
