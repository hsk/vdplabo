# asm/ascii16

ASCII16メガロムのスロット切り替え(バンク切り替え)を実機アセンブリで検証するデモ。`glass-0.6.jar`(Z80アセンブラ)でビルドし、openMSXで実行する。

## 背景: なぜスロット切り替えが要るのか

MSXでは `4000h-7FFFh` と `8000h-BFFFh` が別スロットになっている場合がある。ROMが `4000h` から起動していても、`8000h` 側に同じROMを見せるには `RSLREG` で現在実行中のスロットを取得し、`ENASLT` で `8000h` ページへ割り当てる必要がある。これをしないと、`CALL 8000h` がRAMや別スロットへ飛んでしまう。`main_ascii16.asm`/`main32k.asm` の先頭でこの手順を踏んでいる。

## ファイル

- `main32k.asm` → `main32k.rom` — 32KB ROM版。`8000h`以降にもコードを配置し、スロット設定後に `CALL 8000h`(`bank_message`)できることを確認する最小デモ
- `main_ascii16.asm` → `main_ascii16.rom` — ASCII16版。`7000h` へのライトでバンクを切り替え(`bank_message`/`bank_message2`)ながら文字列を表示する
- `bank1.asm` / `bank2.asm` / `bank3.asm` — `8000h`に配置する単体バンクの実験用コード(それぞれ `BANK1`/`BANK2`/`BANK3` という文字列を返すだけ)。`Makefile`のビルド対象には含まれておらず、バンク切り替えの挙動を個別に試すための断片
- `t.txt` — `main.rom` を `z80dasm` で逆アセンブルしたログ

## ビルド・実行方法

```sh
cd asm/ascii16
make 1   # main32k.asm をビルドし、Plain ROMとしてopenMSXで実行
make 2   # main_ascii16.asm をビルドし、ASCII16 ROMとしてopenMSXで実行
```

## 現状

`main_ascii16.rom`/`main32k.rom`ともに文字列表示とバンク切り替えの動作確認は完了している。`bank1〜3.asm`は独立した実験断片のままで、`main_ascii16.asm`のバンクデータとしては未統合。
