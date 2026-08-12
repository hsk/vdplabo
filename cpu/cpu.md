# とても簡単な CPU + 割り込みエミュレータ

pygame を使った簡易ゲーム機風 CPU エミュレータです。

特徴:

- メモリベースのCPU
- 割り込み (IRQ)
- VBlank
- キーボード入力
- IOポート
- ラベル付きジャンプ
- pygame描画
- スプライト描画

構成イメージ:

```text
+----------------------+
| pygame               |
|----------------------|
| 画面描画             |
| キーボード入力       |
| VBlank生成           |
+----------+-----------+
           |
           v
+----------------------+
| CPU                  |
|----------------------|
| ACC                  |
| PC                   |
| zero_flag            |
| stack                |
| IRQ                  |
+----------+-----------+
           |
           v
+----------------------+
| Memory / IO          |
+----------------------+
```

---

# 1. CPU構成

## レジスタ

| 名前 | 説明 |
|---|---|
| ACC | アキュムレータ |
| PC | プログラムカウンタ |
| zero_flag | 演算結果が0なら1 |
| stack | CALL/IRQ退避用 |
| irq_status | IRQ状態 |

---

# 2. 命令

## 2.1. NOP

何もしません。

```python
("NOP",)
```

---

## 2.2. LABEL name

ラベル定義です。

```python
("LABEL", "main_loop")
```

ジャンプ先として利用できます。

---

## 2.3. LDI value

即値を ACC にロードします。

```python
("LDI", 123)
```

結果:

```text
ACC = 123
```

---

## 2.4. LDA addr

メモリから ACC へロードします。

```python
("LDA", 0x20)
```

---

## 2.5. STA addr

ACC をメモリへ保存します。

```python
("STA", 0x20)
```

---

## 2.6. ADD addr

メモリ値を ACC に加算します。

```python
("ADD", 0x20)
```

---

## 2.7. SUB addr

メモリ値を ACC から減算します。

```python
("SUB", 0x20)
```

---

## 2.8. AND addr

論理AND。

```python
("AND", 0x20)
```

ゲーム入力判定でよく使いますl

---

## 2.9. JMP addr

無条件ジャンプします。

```python
("JMP", "main_loop")
```

または:

```python
("JMP", 0x100)
```

---

## 2.10. JZ addr

zero_flag が1ならジャンプします。

```python
("JZ", "loop")
```

---

## 2.11. JNZ addr

zero_flag が0ならジャンプします。

```python
("JNZ", "loop")
```

---

## 2.12. IN port

IOポートを読み込みます。

```python
("IN", 0x10)
```

結果は ACC に入ります。

---

## 2.13. OUT port

ACC を IOポートへ出力します。

```python
("OUT", 0x20)
```

---

## 2.14. PUSHA

ACC をスタックへ退避します。

```python
("PUSHA",)
```

---

## 2.15. POPA

ACC をスタックから復帰します。

```python
("POPA",)
```

---

## 2.16. IRET

割り込み復帰します。

```python
("IRET",)
```

---

# 3. 割り込み

## IRQ発生

```python
cpu.interrupt_request(CPU.IRQ_VBLANK)
```

または:

```python
cpu.interrupt_request(CPU.IRQ_KEYBOARD)
```

---

## IRQ種類

| 名前 | 値 |
|---|---|
| IRQ_VBLANK | 1 |
| IRQ_KEYBOARD | 2 |

複数IRQは OR されます。

---

## IRQ Status Register

```python
("IN", 0x00)
```

で IRQ status を取得します。

| bit | 意味 |
|---|---|
| bit0 | VBLANK |
| bit1 | KEYBOARD |

読むと自動クリアされます。

MSXやZ80系の VDP status register に近い構成です。

---

# 4. キーボード

## IOポート

| port | 内容 |
|---|---|
| 0x10 | キーボード状態 |

---

## キービット

| bit | キー |
|---|---|
| 0x1 | LEFT |
| 0x2 | RIGHT |
| 0x4 | UP |
| 0x8 | DOWN |

---

# 5. VBlank

pygame 側が毎フレーム:

```python
cpu.interrupt_request(CPU.IRQ_VBLANK)
```

を呼びます。

CPU側は:

```python
("IN", 0x00)
```

でVBlankを確認します。

---

# 6. 描画

pygame がメモリを直接読みます。

| address | 内容 |
|---|---|
| 0x0e | sprite x |
| 0x0f | sprite y |

---

## 描画例

```python
x = cpu.memory[0x0e]
y = cpu.memory[0x0f]
```

16x16 の矩形として描画されます。

---

# 7. ゲームループ例

```python
main_program = [

    ("LABEL", "main_loop"),

    ("IN", 0x00),
    ("JZ", "main_loop"),

    ("AND", 0x22),
    ("JZ", "check_keyboard"),

    # VBLANK処理
    ("LDA", 0x0e),
    ("ADD", 0x20),
    ("STA", 0x0e),

    ("LABEL", "check_keyboard"),

    ("IN", 0x10),
    ("STA", 0x30),

    ("JMP", "main_loop"),
]
```

---

# 8. 実機との対応

| このエミュレータ | 実機 |
|---|---|
| CPU | Z80 |
| pygame | VDP/GPU |
| io[] | IOポート |
| interrupt_request | IRQ線 |
| irq_status | VDP status |
| memory | RAM |
| 0x0e/0x0f | sprite attribute table |

かなり:

- MSX
- NES
- PCエンジン
- GameBoy

などに近い構造になっています。

