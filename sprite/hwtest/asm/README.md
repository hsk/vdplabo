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
