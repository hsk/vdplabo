# sprite2/stage3 について

Phase 3: VRAM使用。未着手。

- [ ] Sprite Attribute Table
- [ ] Sprite Generator Table
- [ ] Sprite Color Table (行ごとの色+CCビット)
- [ ] pattern address計算
- [ ] Y=208終端
- [ ] 16x16 pattern連結

## sprite1/stage3との違い

- sprite1にはない Sprite Color Table (行ごとの色+CCビット) をVRAM上に
  追加で配置する必要がある。
- V9938はVRAMが最大128KBまで扱えるため、テーブルアドレスの計算に
  sprite1(V9918、16KB)にはない上位アドレスビット(R#11)が絡む。
  詳細は[stage4.md](stage4.md)を参照。
- SAT/SGTをVRAMから読む、Y=208終端、16x16 pattern連結といった
  基本構造自体はsprite1/stage3と同じ。
