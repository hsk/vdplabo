# SCREEN2かSCREEN4でスペハリ作る計画

## 背景描画研究

PCGのカラーテーブル書き換えで背景を高速に綺麗に描画する

- [x] 1. pythonで実験
  - [field1.py](field1.py) 4x4でチェッカー描画 ([詳細](field1.md))
  - [field2.py](field2.py) 1ライン単位でストライプ描画([詳細](field2.md))
  - [field3.py](field3.py) 1ライン単位でストライプ描画(補正あり)([詳細](field3.md))
- [x] 2. pythonでテーブル生成
  - [field4.py](field4.py) ([詳細](field4.md))
- [x] 3. アセンブラでテーブルを用いて描画
  - [sc2_field1.py](sc2_field1.py) ストライプ描画4段階([詳細](sc2_field1.md))
  - [sc2_field2.py](sc2_field2.py) ストライプ描画１６段階化([詳細](sc2_field2.md))
- [x] 4. アセンブラで高速化
  - [x] [sc2_field3.py](sc2_field3.py) 中間カラーテーブルを使用した高速化([詳細](sc2_field3.md))
  - [x] [sc2_field4.py](sc2_field4.py) SPを使った高速化、関数化([詳細](sc2_field4.md))
  - [ ] [sc2_field5.py](sc2_field5.py) SPを使った更なる高速化([詳細](sc2_field5.md))
- [x] 5. パターンテーブルで調整して地面だけ描画する。
  - [x] [sc2_field6.py](sc2_field6.py) パターンテーブルだけで空と地面([詳細](sc2_field6.md))
- [x] 6. 天井と地面を分離して描画する
  - [x] [sc2_field7.py](sc2_field7.py) パターンテーブルだけで分離描画([詳細](sc2_field7.md))
    - [x] [sc2_field7_1.py](sc2_field7_1.py) sc2_field8の高速化1
    - [x] [sc2_field7_2.py](sc2_field7_2.py) sc2_field8の高速化2
  - [x] キーボードの左右で天井の高さを指定できるようにする。
  - [x] 天井の高さで上下の描画を分けて行う。
- [x] 7. 仮想VRAM化する
  - [sc2_field8.py](sc2_field8.py) ([詳細](sc2_field8.md))
- [x] 8. 背景を描画できるようにする
  - [sc2_field09.py](sc2_field09.py) ([詳細](sc2_field09.md))
- [x] 9. 背景を横スクロールできるようにする
  - [sc2_field10.py](sc2_field10.py) ([詳細](sc2_field10.md))
- [ ] 10. ステージ切り替えできるようにする
  - [sc2_field11.py](sc2_field11.py) ([詳細](sc2_field11.md))
- [ ] 11. 色パターンを反転させて表示できるようにすることで明滅で色数を増やす。
  - [sc2_field14.py](sc2_field14.py) ([詳細](sc2_field14.md))
- [ ] 12. 背景分割スクロール
  - [ ] 雲とか、城を分割スクロールで表現する
  - [sc2_field15.py](sc2_field15.py) ([詳細](sc2_field15.md))
- [x] 13. 空と地面だけ描画する。
  - [x] [sc2_field30.py](sc2_field30.py) 空と地面だけ(基本版)([詳細](sc2_field30.md))
  - [ ] [sc2_field31.py](sc2_field31.py) 空と地面だけ(高速化版)([詳細](sc2_field31.md))
  - [ ] [sc2_field32.py](sc2_field32.py) カラーテーブルと合わせる([詳細](sc2_field32.md))

## PCGキャラ描画システム

