# v9968/stage1

このステージでは１画面ごと一気に描画する基本的機能のみを実装したサンプルを作ります(v9918/stage1と同じ考え方)。V9968は将来のVDP検討用のドキュメント段階で、実装(.py)はまだありません。

ドキュメント

- [ ] [docs/v9968.md](docs/v9968.md) — 拡張モード選択レジスタについてのメモ
- [ ] [docs/v9968_1epal.md](docs/v9968_1epal.md) — パレットの指定方法
- [ ] [docs/v9968_2sprite3.md](docs/v9968_2sprite3.md) — スプライトモード3の参考メモ
- [ ] [docs/v9968_3cmd.md](docs/v9968_3cmd.md) — VDPコマンド概要
- [ ] [docs/v9968_3cmd1lrmm.md](docs/v9968_3cmd1lrmm.md) — LRMM(回転拡大縮小)コマンド
- [ ] [docs/v9968_3cmd2lfmc.md](docs/v9968_3cmd2lfmc.md) — LFMC(CPU→VRAM フォント描画)コマンド
- [ ] [docs/v9968_3cmd3lfmm.md](docs/v9968_3cmd3lfmm.md) — LFMM(VRAM→VRAM フォント描画)コマンド
- [ ] [docs/v9968_s16.md](docs/v9968_s16.md) — 拡張モード選択レジスタ

## 注記

同じ内容のドキュメントが [v9968/docs/](../docs) にも重複して置かれている(中身は完全に同一)。将来的にはどちらかへ統一する必要がある。

## 次にやること

- `v9918/stage1` と同じ構成で、まず単体の描画サンプル(.py)を作るところから着手する。
