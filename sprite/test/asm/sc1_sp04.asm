; MSX カセットROM SCREEN1 sprite demo
WRTVDP equ 00047h
LDIRVM equ 0005Ch
CHGMOD equ 0005Fh
SNSMAT equ 00141h
RDVDP  equ 0013Eh
SPRATR equ 01B00h
SPRPAT equ 03800h
RG1SAV equ 0F3E0h       ; VDPレジスタ退避アドレス
STATFL equ 0F3E7h
JIFFY  equ 0FC9Eh
HTIMI  equ 0FD9Fh
    org 04000h
rom_header:
    db "AB"
    dw init
    dw 0, 0, 0, 0, 0
player_x equ 0C000h
vint equ 0C010h         ; H.TIMIフックが立てるフラグ(RAM。ROM上のdbに
                        ; 置くと書き込みが無視されるため要注意だった)
htimi_old equ 0C011h    ; H.TIMIの元の5バイトを退避するRAMバッファ
init:
    call screen_init
    call install_htimi_hook
    ; CHGMOD(screen_init内)がH.TIMIフックを上書き前の状態に戻す可能性がある
    ; ため、フック設置はscreen_initの後に行う
    call pattern_name_table_init
    call sprite_attribute_table_init
    call player_init
    jp main

install_htimi_hook:
    ; ../../../asm/int.asm と同じH.TIMIフック手法。JIFFYポーリング/HALTでは
    ; 実測でframe44付近(JIFFYの256ラップ)を境に挙動が変わる謎の現象が
    ; 確認されていたため、割り込みで直接フラグ(vint)を立てる方式に変更した。
    ; H.TIMIの元の5バイトをhtimi_oldへ退避してから、H.TIMIをhtimi_repへの
    ; JP(3バイト)に書き換える。htimi_newはvintを立てた後htimi_old(元の
    ; 5バイト、通常はBIOSのret 5個)へそのまま継続する。
    di
    ld hl, HTIMI
    ld de, htimi_old
    ld bc, 5
    ldir
    ld hl, htimi_rep
    ld de, HTIMI
    ld bc, 3
    ldir
    ei
    ret
htimi_rep:
    jp htimi_new
htimi_new:
    ; player_move相当(キー読み取り+player_x更新)をここで行う。BIOSの
    ; keyintは H_TIMI を呼んだ後にSCNCNT駆動の背後スキャン(key_in、3割り込み
    ; おきに余分なコストがかかる)を行うため、メインループ側でSNSMATを
    ; 呼ぶ形にしていると、その背後スキャンのコストでぎりぎりのタイミングが
    ; 崩れることがあった(../asm/README.md参照)。H_TIMI呼び出し自体は
    ; その背後スキャンより前に来るので、ここで直接読めば影響を受けない。
    ;
    ; キー入力(GTSTCKを経由せず、SNSMATでキーマトリクスの行8を直接読む。
    ; 行8: bit7=RIGHT, bit4=LEFT (0=押されている、openMSXの
    ; src/input/Keyboard.cc のキーマトリクス表と同じ)
    ld a, 8
    call SNSMAT
    ld hl, player_x
    bit 7, a
    jr nz, timi_end_right   ; bit7が1(押されていない)なら飛ぶ
        inc (hl)
    timi_end_right:
    bit 4, a
    jr nz, timi_end_left    ; bit4が1(押されていない)なら飛ぶ
        dec (hl)
    timi_end_left:
    ld a, 1
    ld (vint), a
    jp htimi_old    ; htimi_oldはRAM上のバッファ(コード直後に連続配置できない
                     ; ため、フォールスルーではなく明示的にjpする)
main:
    call wait_vsync
    call player_draw
    call player_collision
    jr main
screen_init:
    ; screen 1
    ld a, 1
    call CHGMOD
    ; スプライト拡大
    ld a, (RG1SAV)
    or 000000001b   ; sprite magnify
    ld b, a
    ld c, 1
    call WRTVDP
    ret
pattern_name_table_init:
    ; VRAMへパターンネームテーブルを転送
    ld de, SPRPAT
    ld hl, sprite_pattern_data
    ld bc, 8
    call LDIRVM
    ret
sprite_attribute_table_init:
    ; VRAMへスプライト属性を転送
    ld de, SPRATR
    ld hl, sprite_attr_data
    ld bc, 12
    call LDIRVM
    ret
player_init:
    ; プレイヤー設定
    ld hl, player_x
    ld (hl), 100
    inc hl
    ld (hl), 0
    inc hl
    ld (hl), 15
    ret
wait_vsync:
    ; VSYNC(H.TIMIフックで立てたvintフラグを待つ。asm/int.asmと同じ手法)
    xor a
    ld (vint), a
    vsync:
        ld a, (vint)
        cp 0
        jr z, vsync
    ret
player_draw:
    ; sprite0 X更新
    ld de, SPRATR + 1
    ld hl, player_x
    ld bc, 3
    call LDIRVM
    ret
player_collision:
    ; 衝突判定 と色設定
    ld a,(STATFL)
    and 000100000b
    jr nz, collision
        ld a, (JIFFY)
        and 0fh
        ld hl, player_x + 2
        ld (hl), 15
        ret
    collision:
        ld hl, player_x + 2
        ld (hl), 6
    ret

sprite_attr_data:
    db 115, 100, 0, 15 ; sprite0 (player)
    db 100, 100, 0, 14 ; sprite1
    db 100,  40, 0, 11 ; sprite2
sprite_pattern_data:
    db 000011000b
    db 000111100b
    db 001111110b
    db 011011011b
    db 011111111b
    db 000100100b
    db 001011010b
    db 010100010b
end:
    ds 08000h - $, 0
