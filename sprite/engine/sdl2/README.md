# スプライトエンジン (C++/SDL2版)

[python/](../python) と同じ設計のスプライトエンジンを C++/SDL2 で移植したもの。

各ステージは `stageN.hpp` にSDLへ依存しないエンジン本体(クラス)を実装し、
`stageN.cpp` がそれを読み込んでSDLのウィンドウ/イベントループを回す、という構成にする。

解説は [../docs/](../docs) を参照(pythonとC++で同じ内容)。

## ビルド・実行方法

```sh
cd sprite1
make        # stage1 をビルド
make run    # ビルドして実行
make clean  # ビルド成果物を削除
```

SDL2 (`sdl2-config` が使えること) が必要。macOSでは `brew install sdl2` でインストールできる。
