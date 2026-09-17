# スプライトエンジン (C++/SDL2版)

[python/](../python) と同じ設計のスプライトエンジンを C++/SDL2 で移植したもの。

各ステージは `stageN.hpp` にSDLへ依存しないエンジン本体(クラス)を実装し、
`stageN.cpp` がそれを読み込んでSDLのウィンドウ/イベントループを回す、という構成にする。

解説は [../docs/](../docs) を参照(pythonとC++で同じ内容)。

## ビルド・実行方法

```sh
cd sprite1
make               # 全ステージ(stage1, stage2-1, stage2-2, stage2, stage3, stage4)をビルド
make stage2        # stage2 だけビルド
make run-stage2    # stage2 をビルドして実行
make clean         # ビルド成果物を削除
```

SDL2 (`sdl2-config` が使えること) が必要。macOSでは `brew install sdl2` でインストールできる。

## sprite1/ の各ステージ

pythonと同じ内容(32個のスプライトが8x8/16x16・等倍/拡大を切り替えながら
跳ね回るデモ)を、Phase 1〜4の各段階で実装し直している。詳しくは
[../docs/sprite1/](../docs/sprite1) を参照。

- `stage1` — 全画面描画。ラインごとの表示制限はない。
- `stage2-1` — 1ライン描画にしただけの最初のステップ(5th sprite/衝突判定なし)。
- `stage2-2` — `stage2-1` に5th sprite判定を追加。
- `stage2` — Phase 2の完成形。5th sprite・衝突判定・Early Clock・Y=208終端を実装。
- `stage3` — スプライトパターン/属性テーブルをVRAM上に配置。
- `stage4` — テーブルアドレスやモードをVDPレジスタ/ステータスレジスタ経由で操作。
