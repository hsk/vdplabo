; MSX カセットROM SCREEN1 sprite demo (Fixed-Point Easing Version)
WRTVDP equ 00047h
FILVRM equ 00056h
LDIRVM equ 0005Ch
CHGMOD equ 0005Fh
GTSTCK equ 000D5h
RDVDP  equ 0013Eh
KILBUF equ 00156h
SPRATR equ 01B00h
SPRPAT equ 03800h
RG1SAV equ 0F3E0h
STATFL equ 0F3E7h
JIFFY  equ 0FC9Eh

; ワークエリアの定義（5バイト構造に変更）
; [ Y小数(1B), Y整数(1B), X(1B), パターン(1B), カラー(1B) ]
sprites equ 0C000h

    org 04000h
rom_header:
    db "AB"
    dw init
    dw 0, 0, 0, 0, 0
init:
    call screen_init
    call pattern_name_table_init
    call sprites_init
    ; 最初の一回、画面外でVRAMを更新（ゴミ取り用）
    call update_vram
    call wait_1sec
    ; フレームカウンターの初期化
    ld c, 0
    call main
    call wait_1sec ; 1秒待ち
    jr init
main:
    inc c
    ld a, c
    cp 150          ; 150フレーム経過したら終了ループへ
    ret z
    call sprites_move
    ; --- 画面同期とVRAM転送 ---
    call wait_vsync
    call update_vram
    jp main

screen_init:
    ; screen 1
    ld a, 1
    call CHGMOD
    
    ; スプライト拡大（サイズ16x16）
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
    ld bc, 8*4
    call LDIRVM
    ret
sprites_init:
    ; 計算用スプライトバッファ（5バイト構成）の初期化
    ld hl, sprites
    ld a, 88        ; 初期X座標
    ld c, 0         ; パターン番号
    ld b, 4
    sprite_init:
        ld (hl), 0      ; Y座標（小数部）
        inc hl
        ld (hl), -17    ; Y座標（整数部）
        inc hl
        ld (hl), a      ; X座標
        add a, 24       ; X座標を間隔空けて並べる
        inc hl
        ld (hl), c      ; パターン
        inc c
        inc hl
        ld (hl), 5      ; カラー
        inc hl
        djnz sprite_init
    ret

sprites_move:
    ld b, 4         ; ループ回数（4文字分）
    ld hl, sprites  ; スプライトデータの先頭（Y小数部のアドレス）
    ld de, start_delay

    sprite_move:
        push bc         ; ループカウンタの退避
        push de         ; ディレイポインタの退避

        ; --- [出現タイマーチェック] ---
        ld a, (de)      ; 開始フレームを取得
        cp c            ; 現在のフレームと比較
        jr z, start_ok  ; ぴったりなら動かす
            jr c, start_ok  ; 過去なら動かす
            jr next_sprite  ; まだ未来ならこのスプライトは動かさない
        start_ok:
            ; --- [固定小数点イージング（減速）の核心] ---
            ; 1. DE = 現在の16bit Y座標(Q8.8) を読み込む
            ld e, (hl)      ; E = 小数部
            inc hl
            ld d, (hl)      ; D = 整数部 (これで DE = 現在の座標)

            ; 2. BC = 目標Y座標（整数88 ➔ 固定小数 88*256 = 05800h）
            ld bc, 05800h   ; B = 88(整数部), C = 0(小数部)

            ; 3. BC（目標） - DE（現在） = HL（残り距離）
            push hl         ; 書き戻し用のアドレス（整数部の場所）を退避
                ld h, b
                ld l, c         ; HL = 目標座標
                or a            ; キャリークリア
                sbc hl, de      ; HL = 目標 - 現在 （残り距離）

                ; 4. 残り距離が非常に少なくなったら強制的に目標値にして止める（ハンチング防止）
                ld a, h
                cp 0
                jr nz, calc_speed
                    ld a, l
                    cp 4            ; 残り距離が4/256以下（ほぼ0ピクセル）になったら
                    jr c, lock_position

                calc_speed:
                ; 5. 残り距離（HL）を 8 で割って「速度」にする (1/8減速イージング)
                sra h
                rr l    ; 1回シフト
                sra h
                rr l    ; 2回シフト
                sra h
                rr l    ; 3回シフト (HL = 移動速度)

                ; 6. 現在地（DE） ＋ 速度（HL） ＝ 新しい位置（HL）
                add hl, de
                ld b, h
                ld c, l

            lock_position:
            ; 目標値（BC）に完全に固定
            pop hl          ; ★重要：ロック時も必ずスタックからアドレスを復帰させる！
            ld (hl), b      ; 目標のY整数部（88）を保存
            dec hl
            ld (hl), c      ; 目標のY小数部（0）を保存

        next_sprite:
        ; 次のスプライトデータ（5バイト先）へポインタを進める
        inc hl
        inc hl
        inc hl
        inc hl
        inc hl
        pop de          ; ディレイポインタ復帰
        inc de          ; 次の文字のディレイデータへ
        pop bc          ; ループカウンタ復帰
    djnz sprite_move
    ret

; --- 📦 5バイト構造を正しい4バイトにしてVRAM（SPRATR）へ送る関数 ---
update_vram:
    ld hl, sprites
    ld de, SPRATR
    ld b, 4         ; 4スプライト分
    vram_loop:
        push bc
        inc hl          ; 1バイト目（Y小数部）をスキップ！★ここがミソ
        
        ; 残りの4バイト（Y整数, X, パターン, カラー）をVRAMへ直接転送
        ld bc, 4
        push de
        push hl
        call LDIRVM     ; HLが4進み、DE（VRAMアドレス）も4進むことはない
        pop hl
        pop de
        inc hl
        inc hl
        inc hl
        inc hl
        inc de
        inc de
        inc de
        inc de
        pop bc
        djnz vram_loop
    ret

wait_vsync:
    ld hl, JIFFY
    ld a, (hl)
    vsync:
        cp (hl)
        jr z, vsync
    ret

wait_1sec:
    ; 1秒待ち
    ld b, 60
    loop1:
        call wait_vsync
        djnz loop1
    ret

start_delay:
    db 0, 12, 24, 36    ; 各文字が動き出すフレーム時間差

sprite_pattern_data:
    ; T
    db 011111111b, 000011000b, 000011000b, 000011000b, 000011000b, 000011000b, 000011000b, 000011000b
    ; Y
    db 010000001b, 011000011b, 001100110b, 000111100b, 000011000b, 000011000b, 000011000b, 000011000b
    ; P
    db 011111110b, 011000011b, 011000011b, 011111110b, 011000000b, 011000000b, 011000000b, 011000000b
    ; E
    db 011111111b, 011000000b, 011000000b, 011111100b, 011000000b, 011000000b, 011000000b, 011111111b

end:
    ds 08000h - $, 0
