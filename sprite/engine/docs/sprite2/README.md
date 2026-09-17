# Sprite Renderer 実装段階 (スプライトモード2)

[sprite1](../sprite1/README.md)と同じ4段階で進めるが、スプライトモード2固有の
以下の機能が加わる。

- 1ラインあたりの表示制限が4枚(5th sprite)から8枚(9th sprite)に増える
- パレットが512色中16色の可変パレットになり、スプライトの行(パターンの1ライン)
  ごとに色を指定できる(sprite color table)
- CCビットを立てると、既に描画されている色とORを取って重ね合わせられる

## 1. Phase 1: 全画面描画

まずは「動くものを作る」。sprite1のPhase1に、スプライトモード2固有の
色指定・重ね合わせを追加する。実装済み。

### 1.1. 特徴

- 1フレーム単位描画
- 全pixel再構築
- 単純ループ
- VRAM直接参照しない
- レジスタ簡略化

### 1.2. 実装した機能

- [x] 8x8 sprite
- [x] 16x16
- [x] magnify
- [x] sprite color table (行ごとの色指定)
- [x] CCビットによる色の重ね合わせ(OR)

color 0 transparent・collision・9th sprite・scanline化はこの段階では意図的に対象外(Phase 2以降で扱う)。

### 1.3. 目的

まず sprite2 特有の色指定・重ね合わせが表示されること。

---

## 2. Phase 2: 1ライン描画(scanline)

MSX2/V9938らしい構造へ移行。未着手。

### 2.1. 特徴

- scanline renderer
- lineNumber 単位描画
- 1ラインの表示制限が sprite1 の4枚から8枚に増える
- 重ね合わせ(CCビットのOR)をscanline単位で行う

### 2.2. 実装する機能

- [ ] scanline sprite描画
- [ ] 1ライン8枚制限
- [ ] 9th sprite
- [ ] sprite priority
- [ ] collision
- [ ] Y判定

### 2.3. 目的

実機挙動へ近づける。

---

## 3. Phase 3: VRAM使用

VDP構造へ移行。未着手。

### 3.1. 特徴

- SAT/SGT/スプライトカラーテーブルを VRAMから読む
- CPU memory と分離
- V9938のメモリマップに合わせたアドレス計算(詳細は[stage4.md](stage4.md)参照)

### 3.2. 実装する機能

- [ ] Sprite Attribute Table
- [ ] Sprite Generator Table
- [ ] Sprite Color Table (行ごとの色+CCビット)
- [ ] pattern address計算
- [ ] Y=208終端
- [ ] 16x16 pattern連結

### 3.3. 目的

「本物のV9938」にする。

---

## 4. Phase 4: レジスタ駆動

完全なVDP化。未着手。テーブルアドレス計算・ステータスレジスタの詳細は
[stage4.md](stage4.md) を参照。

### 4.1. 特徴

- reg[] による動作切替
- mode依存
- 実機互換

### 4.2. 実装する機能

- [ ] sprite size register
- [ ] magnify register
- [ ] table base register (R#5, R#6, R#11)
- [ ] status register (5S, collision, 5th sprite#)
- [ ] EC bit
- [ ] SPD(スプライト非表示)ビット

### 4.3. 目的

実機互換エミュレータ完成。
