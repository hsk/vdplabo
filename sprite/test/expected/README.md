# 期待値(golden)

各サンプル(`scN_spNN`)の「正しい描画結果」を録画したロスレスwebmの置き場所です。

- ファイル名はasm/pythonファイルと同じにします (例: `sc1_sp01.asm` → `sc1_sp01.webm`)
- 特定の実装(pythonエンジンなど)専用ではなく、**同じサンプルを検証する
  どの実装からも参照される共有データ**という位置づけです。
  現状は [../python/](../python) のテストが使っていますが、将来
  openMSXや実機を使ったテストを追加する場合も同じファイルと比較する想定です
- フォーマットの詳細(VP9 `gbrp`, 4倍拡大保存など)は
  [../python/video_golden.py](../python/video_golden.py) を参照してください
- 生成/更新は各テストファイルを `--update-golden` 付きで実行します
  (例: `python ../python/sc1_sp01.py --update-golden`)
