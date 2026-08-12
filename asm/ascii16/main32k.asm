; 32k rom demo
    org 04000h
    db "AB"
    dw start
    dw 0,0,0,0,0,0,0,0,0
; MSXでは4000h-7FFFhと8000h-BFFFhが別スロットになっている場合がある。
; このROMは4000hから起動しているが、8000h側にも同じROMを見せたい。
; RSLREGで現在実行中のスロットを取得し、ENASLTで8000hページへ割り当てる。
; これを行わないと CALL 8000h がRAMや別スロットへ飛ぶことがある。
start:
    ; RSLREGで現在実行中のスロットを取得
    call	0x0138 ; RSLREG
	; ENASLTで8000hページへ割り当てる。
    ld		b,a
	srl		a
	srl		a
	ld		hl, 0x8000
	call	0x0024 ; ENASLT
	ei

    ld hl,msg
    call print_string
    ld hl,msg2
    call print_string
    ;ld a,1
    ;ld (7000h),a
    ; bank_message はROMイメージ上では8000h以降に配置されている。
    ; ENASLT実行前は8000h側にROMが見えていないため呼び出せない。
    ; 上記のスロット設定後に初めてCALLできる。
    call bank_message
    call print_string
loop:
    jr loop
CHPUT: equ 00A2h
print_string:
    loop1:
        ld a,(hl)
        or a
        ret z
        call CHPUT
        inc hl
        jr loop1
msg: db "hogehoge\r\n", 0
msg2: db "fugahuga\r\n", 0
; 4000hから始まったROMを8000h位置までゼロ埋めする。
; これにより以降のコードはROM内の後半16KB(実行時は8000h-BFFFh)へ配置される。
    ds 08000h - $
    org 08000h
; このルーチンは実行時アドレス8000hに配置される。
; call bank_message は機械語として CALL 8000h になる。
bank_message:
    ld hl, bank_msg1
    ret
bank_msg1: db "bank msg1\r\n", 0

    ds 0c000h - $
