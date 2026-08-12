# vdp_command

V9938のVDPコマンド(HMMC/HMMMなど)を、実機同等のアセンブリ(glass-0.6.jarでビルドするROMカートリッジ)で検証するためのディレクトリです。BASICやディスクBIOSに頼らずワンソースで動くので、実機・エミュレータどちらでも手軽にテストできます。

- [asm/sc5_vdp01.asm](asm/sc5_vdp01.asm) — SCREEN5、HMMC(CPU→VRAM高速転送)コマンドのサンプル
- [asm/sc5_vdp02.asm](asm/sc5_vdp02.asm) — SCREEN5、HMMM(VRAM→VRAMコピー)コマンドのサンプル
- [asm/sc5_vdp03_hmmc.asm](asm/sc5_vdp03_hmmc.asm) — HMMCパラメータをRAM上のワークエリア経由で構成する版
- [asm/sc5_vdp04_hmmc_hmmm.asm](asm/sc5_vdp04_hmmc_hmmm.asm) — HMMC+HMMMを組み合わせた版
- [asm/todo.md](asm/todo.md) — スプライト関連の実験メモ(BASIC/アセンブラ両方のサンプル集)
- [asm/rom/](asm/rom) — ビルド済みROMの出力先

対応するコマンド仕様のドキュメントは [v9938/stage1/docs/v9938_cmd01hmmc.md](../v9938/stage1/docs/v9938_cmd01hmmc.md) 以降を参照してください。ここでのアセンブリ検証結果が、Python参照実装(`v9938`配下)のコマンド機能を実装する際の期待値の根拠になります。
