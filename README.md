# VDP Labo

これは MSX の VDP を実装しながらゼロから理解するための研究です。
最初はVDPの本質的な要素のみを簡潔に実装して理解を深め、徐々に機能を厳密に作成していきます。

完成したMSXエミュレータを作ることよりも、VDPの各機能を段階的に実装し、その動作原理を理解することを優先します。

## ディレクトリ構成

実装言語で大きく2つに分かれる。PC上でVDPの挙動をシミュレートするPython実装は [python/](python) に、実機/エミュレータ上でZ80アセンブリを動かして挙動を検証するものは [asm/](asm) にまとめている。[sprite/](sprite) はPython実装と実機検証が対になった研究テーマのため、この2分類の例外として現状のディレクトリ構成を維持している。

### python/ — VDPチップ別の段階的研究 (メイン)

チップ(V9918/V9938/V9958/V9968/V9990)ごとに、下記の「進め方」のステージ1〜4を踏んで実装していく。各ステージの詳細は各ディレクトリのREADMEを参照。

| チップ | 概要 | 進捗 |
| --- | --- | --- |
| [python/v9918](python/v9918) | TMS9918A互換。stage1〜4まで実装あり | スプライト機能はstage4(レジスタ駆動)まで到達 |
| [python/v9938](python/v9938) | MSX2用。stage1にスプライト実装、他ステージはドキュメントのみ | 実装は一部、コマンド系はドキュメントのみ |
| [python/v9958](python/v9958) | MSX2+用。stage1のドキュメントのみ | 未実装 |
| [python/v9968](python/v9968) | 後継VDP(検討用)。ドキュメントのみ | 未実装 |
| [python/v9990](python/v9990) | MSXturboR用。stage1のドキュメントのみ | 未実装 |

その他、VDPチップ研究ではない一般的な教材も python/ 配下に置いている。

- [python/cpu](python/cpu) — MSXに限らない、CPU+割り込み+VDPステータス的な概念を最小構成で学ぶための独立した教材。
- [python/timing](python/timing) — エミュレーションにおける時間の進め方(フレーム単位〜クロック単位〜スケジューラ)についての解説。

### asm/ — 実機アセンブリでの検証

- [asm/ascii16](asm/ascii16) — ASCII16メガロムのスロット切り替え(バンク切り替え)デモ。
- [asm/vdp_command](asm/vdp_command) — V9938のVDPコマンド(HMMC/HMMMなど)を実機アセンブリで検証するテストROM集。

R-Type風ゲーム制作の実験(敵/背景描画・キーフレームアニメーション)は別リポジトリ [msx-games](../msx-games) に分離した。

### その他

- [sprite/](sprite) — スプライトモード1/2について、Python参照実装(`sprite/src`)と、実機で動くZ80アセンブリのサンプル(`sprite/asm`)を集めた実地検証コード。VDPエミュレータ実装時の期待値の参考にする。

## TODO

- [ ] gif で保存機能をつける。
- [ ] asm/ に、JUnitのような自動テストスイート形式でMSX実機VDPの挙動を検証するテストROMを作りたい(アイデア段階。デモに走らず、まずは設計を詰めてから着手する)。

## 研究の進め方 (ロードマップ)

1. ステージ1 適当に機能ごとに作ってみる
    - 本質的に重要な機能を単純に作ってみる
        - レジスタは使わずに作る
        - VRAMの構成も考えない
        - ビットマップに描画する
        - 当たり判定などしない
        - 表示制限もしない
    - [x] [python/v9918/stage1](python/v9918/stage1)
    - [ ] [python/v9938/stage1](python/v9938/stage1) (スプライトのみ着手)
    - [ ] [python/v9958/stage1](python/v9958/stage1) (ドキュメントのみ)
    - [ ] [python/v9968/stage1](python/v9968/stage1) (ドキュメントのみ)
    - [ ] [python/v9990/stage1](python/v9990/stage1) (ドキュメントのみ)

2. ステージ2 ラスタライズを意識する
    - ラインごとに描画する
        - ラスタごとの表示制限をつける
    - [x] [python/v9918/stage2](python/v9918/stage2)
    - [ ] [python/v9938/stage2](python/v9938/stage2)
    - [ ] [python/v9958/stage2](python/v9958/stage2)
    - [ ] [python/v9968/stage2](python/v9968/stage2)
    - [ ] [python/v9990/stage2](python/v9990/stage2)

3. VRAMのアドレスを確定させる
    - VRAMの構造をしっかり確定させる
    - [ ] [python/v9918/stage3](python/v9918/stage3) (スプライトのみ着手)
    - [ ] [python/v9938/stage3](python/v9938/stage3)
    - [ ] [python/v9958/stage3](python/v9958/stage3)
    - [ ] [python/v9968/stage3](python/v9968/stage3)
    - [ ] [python/v9990/stage3](python/v9990/stage3)

4. レジスタを確定させる
    - レジスタを使って扱うようにする
    - [ ] [python/v9918/stage4](python/v9918/stage4) (スプライトのみ着手)
    - [ ] [python/v9938/stage4](python/v9938/stage4) (レジスタ一覧ドキュメントのみ)
    - [ ] [python/v9958/stage4](python/v9958/stage4)
    - [ ] [python/v9968/stage4](python/v9968/stage4)
    - [ ] [python/v9990/stage4](python/v9990/stage4)

5. チップを統合する
    - v9918 と v9938 を1つにまとめて v9938a とする
    - v9938a と v9958 をまとめて v9958a とする
    - v9958 と v9990 をまとめて v9978 とする
