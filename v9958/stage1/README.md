# v9958/stage1

このステージでは１画面ごと一気に描画する基本的機能のみを実装したサンプルを作ります(v9918/stage1と同じ考え方)。V9958はMSX2+用VDPで、YJK方式の高色数モード(SCREEN10/11/12、GRAPHIC7系)が追加されています。

現時点では実装(.py)はまだなく、ドキュメントのみ。

ドキュメント

- [ ] [docs/v9958.md](docs/v9958.md) — SCREEN10/11/12を統合した `v9958.py` を作る構想メモ
- [ ] [docs/v9958_screen10.md](docs/v9958_screen10.md) — 256x212、YJK256色モードの解説
- [ ] [docs/v9958_screen11.md](docs/v9958_screen11.md) — 同上(SCREEN11)
- [ ] [docs/v9958_screen12.md](docs/v9958_screen12.md) — 同上(SCREEN12、フルカラー相当)

## 次にやること

- `v9918/stage1` と同じ構成で、まずSCREEN10/11/12それぞれの単体実装(`v9958_screenXX.py`)を作るところから着手する。
