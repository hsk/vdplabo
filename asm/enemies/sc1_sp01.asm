; MSX カセットROM SCREEN 1 スプライト1つ
; --- MSX BIOSのアドレス定義 ---
WRTVDP equ 00047h       ; VDPレジスタ書き込み (B=レジスタ, C=値)
CHGMOD equ 0005Fh       ; 画面モード変更 (Aレジスタでモード指定)
FILVRM equ 00056h       ; VRAM を一定値で埋める (A=値, BC=サイズ, HL=VRAM宛先)
LDIRVM equ 0005Ch       ; メモリからVRAMへ一括転送 (BC=サイズ, DE=VRAM宛先, HL=メモリ元)
SPRATR equ 01B00h       ; VRAMのスプライト属性テーブル起点アドレス
SPRPAT equ 03800h       ; VRAMのパターンジェネレータ起点アドレス
RG1SAV equ 0F3E0h       ; VDPレジスタ退避アドレス
; --- ROMヘッダ ---
    org 04000h          ; カセットROMはページ2(04000h)に配置
rom_header:
    db "AB"             ; ROMの識別ID (04000h)
    dw init             ; 電源ON時に実行するアドレス (04002h)
    dw 0, 0, 0, 0, 0    ; 残りのヘッダ領域を0で埋める
; --- メインプログラム ---
init:
    ; SCREEN 1 の設定
    ld a, 1
    call CHGMOD
    ; スプライト拡大
    ld a, (RG1SAV)
    or 000000001b   ; sprite magnify
    ld b, a         ; 設定データ
    ld c, 1         ; ポートNo.
    call WRTVDP
    ; VRAMへパターンネームテーブルを転送
    ld de, SPRPAT               ; VRAMのパターンジェネレータ起点アドレス
    ld hl, sprite_pattern_data  ; 転送元
    ld bc, 8                    ; 転送サイズ (8バイト)
    call LDIRVM
    ; VRAMへスプライト属性(座標)を転送
    ld de, SPRATR               ; VRAMのスプライト属性テーブル起点アドレス
    ld hl, sprite_attr_data     ; 転送元
    ld bc, 4                    ; 4バイト (Y, X, パターン, 補足)
    call LDIRVM
main:
    jr main             ; 画面を維持するため無限ループ
sprite_attr_data:
    ; Y座標,X座標,パターン,色
    db  100,  100,       0,15
sprite_pattern_data:
    db 000111100b
    db 001111110b
    db 011111111b
    db 011111111b
    db 011111111b
    db 011111111b
    db 001111110b
    db 000111100b
end:
    ; ROMサイズを16KB（最小サイズ）に合わせるためのパディング
    ds 08000h - $, 0
