# sprite2/stage2 について

Phase 2: 1ライン描画(scanline)。実装済み。

- [x] scanline sprite描画
- [x] 1ライン8枚制限
- [x] 9th sprite
- [x] sprite priority
- [x] collision
- [x] Y判定

## sprite1/stage2との違い

- 1ラインの表示制限が4枚から8枚に増える(5th sprite→9th sprite)。
- sprite1にはない重ね合わせ(CCビットのOR)を、scanline単位でも
  正しく行う必要がある(stage1の全画面描画版では1画面まとめて
  draw_bufferを見ていたが、scanline版では1ラインごとに正しく
  処理できるようにする)。
- スキャンライン描画・優先順位・衝突判定・Y判定の基本的な考え方自体は
  sprite1/stage2と同じ。
