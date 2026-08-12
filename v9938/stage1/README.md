# v9938/stage1

このステージでは１画面ごと一気に描画する基本的機能のみを実装したサンプルを作ります(v9918/stage1と同じ考え方)。V9938はMSX2用VDPで、GRAPHIC3〜7モードやVDPコマンド(HMMC/HMMM等)が追加されています。

- [x] [v9938_sprite2.py](v9938_sprite2.py) — スプライトモード2(パレット+スプライト単位カラーテーブル)の実装

ドキュメント

- [x] [docs/v9938.md](docs/v9938.md)
- [x] [docs/v9938_graphics3.md](docs/v9938_graphics3.md)
- [x] [docs/v9938_graphics4.md](docs/v9938_graphics4.md) / [docs/v9938_graphics4.py](docs/v9938_graphics4.py) — GRAPHIC4(SCREEN5)の実装サンプルもdocs内にある
- [x] [docs/v9938_graphics5.md](docs/v9938_graphics5.md)
- [x] [docs/v9938_graphics6.md](docs/v9938_graphics6.md)
- [x] [docs/v9938_graphics7.md](docs/v9938_graphics7.md)
- [x] [docs/v9938_sprite2.md](docs/v9938_sprite2.md)
- [x] VDPコマンド解説 [docs/v9938_cmd01hmmc.md](docs/v9938_cmd01hmmc.md) 〜 [docs/v9938_cmd12point.md](docs/v9938_cmd12point.md)
- [x] GRAPHIC4向けコマンド解説 [docs/g4/](docs/g4) (`v9938_g4cmd01hmmc.md` 〜 `v9938_g4cmd12point.md`)

## 現状

ドキュメントは充実しているが、実装(.py)があるのは `v9938_sprite2.py` と `docs/v9938_graphics4.py` のみ。GRAPHIC3/5/6/7、TEXT2、VDPコマンド類はこれから実装する段階。実機でのVDPコマンド検証は [vdp_command/](../../vdp_command) を参照。
