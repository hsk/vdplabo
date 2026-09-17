# Sprite Renderer 実装段階

## 1. Phase 1: 全画面描画

まずは「動くものを作る」。

### 1.1. 特徴

- 1フレーム単位描画
- 全pixel再構築
- 単純ループ
- VRAM直接参照しない
- レジスタ簡略化

### 1.2. 実装する機能

- [x] 8x8 sprite
- [x] 16x16
- [x] magnify
- [x] 単色描画
- color 0 transparent
- [x] SAT読み込み
- [x] pattern描画
- [x] パレット描画

### 1.3. 後回し

- collision
- 5S
- scanline
- EC

### 1.4. 目的

まず sprite が表示されること。

---

## 2. Phase 2: 1ライン描画(scanline)

MSX/TMS9918らしい構造へ移行。

### 2.1. 特徴

- scanline renderer
- lineNumber 単位描画
- raster構造
- VDP寄り

### 2.2. 実装する機能

- [x] scanline sprite描画
- [x] 1ライン4枚制限
- [ ] 5th sprite
- [ ] sprite priority
- [ ] collision
- [x] Y判定

### 2.3. この段階でMSX感がかなり出る

- チラつき
- sprite drop
- collision timing

### 2.4. 目的

実機挙動へ近づける。

---

## 3. Phase 3: VRAM使用

VDP構造へ移行。

### 3.1. 特徴

- SAT/SGT を VRAMから読む
- CPU memory と分離
- VDP memory map 化

### 3.2. 実装する機能

- [ ] Sprite Attribute Table
- [ ] Sprite Generator Table
- [ ] pattern address計算
- [ ] Y=208終端
- [ ] 16x16 pattern連結

### 3.3. この段階でできること

- 実ROM動作
- BIOS互換
- VRAM dump解析

### 3.4. 目的

「本物のVDP」にする。

---

## 4. Phase 4: レジスタ駆動

完全なVDP化。

### 4.1. 特徴

- reg[] による動作切替
- mode依存
- 実機互換

### 4.2. 実装する機能

- sprite size register
- magnify register
- table base register
- status register
- [ ] EC bit
- [ ] collision flag
- [ ] 5S flag

### 4.3. この段階でできること

- MSX BIOS対応
- 実機レベル互換
- SCREEN mode切替

### 4.4. 目的

実機互換エミュレータ完成。
