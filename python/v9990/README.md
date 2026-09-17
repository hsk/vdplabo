# v9990

MSXturboR用VDP。解像度・色数をフレキシブルに変えられる多モードVDPで、P1/P2モードとB0〜B7のビットマップモード、独自のコマンドセット(LMMC/LMMV/LMCM/LMMM/CMMC/CMMM/BMXL/BMLX/BMLL/LINE/SEARCH/POINT/PSET/ADVANCE)を持つ。[ルートREADME](../README.md)の「研究の進め方」のうち、現状は stage1 の計画段階(TODOリスト)で実装・ドキュメントともほぼ未着手。

| ステージ | 概要 | 状態 |
| --- | --- | --- |
| [stage1](stage1) | 適当に機能ごとに作ってみる | 計画(TODOリスト)のみ、実装・ドキュメントともほぼ未着手 |
| stage2〜4 | (ロードマップ参照) | ディレクトリ未作成 |

## stage1 — 適当に機能ごとに作ってみる

解像度と色数を柔軟に変えられるVDPなので一見範囲が大きく見えるが、モードを絞って作ることで単純化できる想定。README上に対応予定のモード/コマンド一覧がTODOチェックリストとして並んでいるが、実装(.py)・ドキュメント(.md)ともにほぼ手つかず。

- 画面モード: P1/P2(パターンモード)、B0〜B7(ビットマップモード。YJK/YUVを含む各種カラーモード)
- VDPコマンド: STOP/LMMC/LMMV/LMCM/LMMM/CMMC/CMMM/BMXL/BMLX/BMLL/LINE/SEARCH/POINT/PSET/ADVANCE
- ドキュメントは `docs/README.md` と `docs/v9990_sprite.md` が存在するのみで、その他は未作成

## 次のステップ

- モードを1つ選んで最初の単体実装(例: P1モードの基本描画)に着手する
- 他チップと同様、まずレジスタ・VRAM構成を考えない単純な実装から始める
