# スプライトモード1に関するサンプルコード

ここには、スプライトモード1に関するサンプルコードがあります。

詳しくは [ドキュメント](../docs/README.md) を見てください。

## ビルド・実行方法

```sh
make sc1_sp01   # sc1_sp01.asm をビルドし、rom/sc1_sp01.rom を openMSX で実行
```

`sc1_sp01`〜`sc1_sp08` の各ファイル名がそのままターゲット名になっている(`z88dk-z80asm`でビルドし、`openmsx -carta rom/<ターゲット名>.rom`で起動する)。

```sh
make        # 全ターゲットを順番にビルド・実行
make clean  # rom/*.rom を削除
```
