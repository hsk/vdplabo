;=========================================================
; SCREEN 7 Full Screen Vertical Stripes Test
;=========================================================

CHGMOD:  EQU 005FH      ; 画面モードを変更する
SETWRT:  EQU 0053H      ; VRAMの書き込みアドレスを設定する

SCR7_MOD: EQU 7         ; SCREEN 7 のモード番号
FORCLR: EQU 0F3E9H  ; 前景色ワークエリア
BAKCLR: EQU 0F3EAH  ; 背景色ワークエリア
BDRCLR: EQU 0F3EBH  ; 周辺色ワークエリア
CHGCLR: EQU 0062H   ; 画面色変更BIOSアドレス

    org 04000h
rom_header:
    db "AB"
    dw init
    dw 0, 0, 0, 0, 0
init:
    ;--- 1. SCREEN 7 に画面を切り替える ---
    LD  A, SCR7_MOD
    CALL CHGMOD
    ; 背景色設定 (例: 背景1、周辺5)
    LD A, 15
    LD (FORCLR), A
    LD A, 7
    LD (BAKCLR), A
    LD A, 5
    LD (BDRCLR), A
    CALL CHGCLR

    ;--- 2. VRAMの書き込み開始アドレスを 00000H に設定 ---
    LD  HL, 0000H
    CALL SETWRT

    ;--- 3. 画面全体（212ライン）のループ処理 ---
    LD  A, (0007H) ; 0007Hに入っているポートアドレス（通常98H）を読み込む
    LD  C, A       ; Cレジスタにポートアドレスを設定
    LD  E, 212/2     ; Y方向のループ回数（212ライン分）

    LINE_LOOP:
         LD  B, 0      ; 横方向のパターン繰り返し回数

        PATTERN_LOOP:
                LD  A, 01FH
                OUT (C), A
                DJNZ PATTERN_LOOP ; Bレジスタが0になるまで（32回）ループ

        PATTERN_LOOP2:
                LD  A, 0F1H
                OUT (C), A
                DJNZ PATTERN_LOOP2 ; Bレジスタが0になるまで（32回）ループ

        ; 1ライン描き終わったら、次のラインへ
        DEC E
        JR  NZ, LINE_LOOP ; Eレジスタが0になるまで（212回）ループ

    ;--- 5. 終了してBASICに戻る ---
    loop:
        JP  loop
end:
    ds 08000h - $, 0
