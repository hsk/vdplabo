# スプライトモード2に関するサンプルコード

ここには、スプライトモード2に関するサンプルコードがあります。

詳しくは [ドキュメント](../docs/README.md) を見てください。

## ビルド・実行方法

```sh
make sc5_sp01   # sc5_sp01.asm をビルドし、rom/sc5_sp01.rom を openMSX で実行
```

`sc`で始まる各ファイル名(`sc5_sp01`〜`sc5_sp07`, `sc5_sp03_2`, `sc5_hra`など)がそのままターゲット名になっている(`glass-0.6.jar`でビルドし、`openmsx -carta rom/<ターゲット名>.rom`で起動する)。

```sh
make clean  # rom/*.rom を削除
```
