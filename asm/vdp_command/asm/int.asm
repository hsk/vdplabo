; define
IO_VDP_PORT1	:= 0x99
CHGMOD			:= 0x005F
H_TIMI			:= 0xFD9F
; BSAVE_HEADER
defb	0xFE        ; bsave header saddr
defw	initialize  ; bsave header saddr
defw	end_address ; bsave header eaddr
defw	initialize  ; bsave header exec

	org			0xB000
initialize:
	; SCREEN1
	ld			a, 1
	call		CHGMOD

	;; 割り込みフック処理
	; 割り込み禁止
	di
	; h_timi から h_timi_old に5バイトコピー
	ld		hl, h_timi
	ld		de, h_timi_old
	ld		bc, 5
	ldir
	; h_timi_rep から h_timi に3バイトコピー
	ld		hl, h_timi_rep
	ld		de, h_timi
	ld		bc, 3
	ldir
	; 割り込み許可
	ei
	jp main
h_timi_rep:
	jp		h_timi_new
h_timi_new:
	ld          a, 1
	ld			[vint],a
h_timi_old:
	db			0xc9, 0xc9, 0xc9, 0xc9, 0xc9
vint:
	db 0
vsync_wait:
	ld hl,vint
	xor a
	ld [hl],a
	loop1:
		cp [hl]
		jr z,loop1
	ret

main:
	call vsync_wait

	; この位置は、割り込み処理ルーチンなので、割り込み禁止状態。
	ld			b, 24				; 24行
	ld			de, 0x1801			; パターンネームテーブル(SCREEN1) のアドレス
	ld			c, IO_VDP_PORT1
loop:
	push		bc
	; VDP の VRAMリードアドレスを DE にする
	out			[c], e
	out			[c], d
	dec			c
	; VRAM から 31byte 読みだす
	ld			hl, line_buffer
	ld			b, 31
	inir
	; A に乱数を得る
	call		random
	ld			[line_buffer + 31], a
	; VDP の VRAMライトアドレスを DE にする
	dec			de
	ld			a, d
	or			a, 0x40
	inc			c
	out			[c], e
	out			[c], a
	dec			c
	; VRAM へ 32byte 書き出す
	ld			hl, line_buffer
	ld			b, 32
	otir
	; DE に 33 を加算する
	ld			bc, 33
	ex			de, hl
	add			hl, bc
	ex			de, hl
	pop			bc
	djnz		loop
	jp main

line_buffer::
	db			0,0,0,0,0,0,0,0
	db			0,0,0,0,0,0,0,0
	db			0,0,0,0,0,0,0,0
	db			0,0,0,0,0,0,0,0
; =============================================================================
;	random
;	input)
;		none
;	output)
;		a ... random value 0...255
;	break)
;		af, b
; =============================================================================
random::
	ld			a, [random_seed1]
	rlca
	ld			b, a
	ld			a, [random_seed2]
	rrca
	rrca
	xor			a, b
	dec			a
	ld			[random_seed1], a
	ld			a, b
	inc			a
	ld			[random_seed2], a
	ret
random_seed1:
	db			0b1001_1101
random_seed2:
	db			0b1010_0011
end_address:
