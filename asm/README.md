# asm

MSXの実ロム(Z80アセンブリ、glass-0.6.jarでビルド)を使った実験群。

- [ascii16/](ascii16) — ASCII16メガロムのスロット切り替え(バンク切り替え)デモ。`RSLREG`/`ENASLT` を使って複数バンクを跨いだ実行を検証する。
- [vdp_command/](vdp_command) — V9938のVDPコマンド(HMMC/HMMMなど)を実機アセンブリで検証するテストROM集。

R-Type風シューティングゲーム制作の実験(旧enemies/, fields/, key/)は [../../msx-games](../../msx-games) へ分離した。VDPスプライト研究の実験場としては引き続き参照する。

その他: [int.asm](int.asm), [Makefile](Makefile), [todo.md](todo.md)(スプライト実験のBASIC/アセンブラサンプル集) はこのディレクトリ直下の補助ファイル。
