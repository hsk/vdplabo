VDP_P1  equ     $99             ; レジスタ書き込みポート
VDP_P3  equ     $9b             ; ポート#3 (間接アクセスポート)
CHGMOD  equ     $005f           ; 画面モード変更 (a=モード)

;--- ram上のワークエリア定義 ---
ram_prm equ   $c000           ; hmmcパラメータ（11バイト）のコピー先領域
ram_clr equ   ram_prm + 8   ; コピー先での r#44 (clr) のアドレス
ram_hmmm_prm equ ram_prm+(rom_hmmm-rom_prm)          ; hmmmパラメータ（15バイト）のコピー先領域
        org     $4000           ; romの開始アドレス
        db      "AB"            ; romマジックid
        dw      init            ; パワーオン・リセット時の開始アドレス
        ds      12, 0           ; 予約領域

init:
        ; スタックポインタの初期化（ramを使用するため必須）
        ld      sp, ($f380)         ; h.stkp (システム標準位置)

        ; 1. screen 5 に切り替え
        ld      a, 5                ; screen 5
        call    CHGMOD

        di                          ; vdpを直接制御するため割り込み禁止
        call hmmc_16x16_init
        ; 3. hmmcコマンドの実行完了待ち
        call    wait_vdp
        ld      hl, image_data      ; 画像データの先頭アドレス
        call    hmmc_16x16

        call    wait_vdp

        ld      hl, ram_hmmm_prm    ; hmmmのパラメータテーブル
        call    set_vdp_regs        ; vdpレジスタに転送

        call    wait_vdp

        ld      a, 16
        ld      (ram_hmmm_prm + 4), a
        ld      hl, ram_hmmm_prm    ; hmmmのパラメータテーブル
        call    set_vdp_regs        ; vdpレジスタに転送
        call    wait_vdp

        ld      a, 32
        ld      (ram_hmmm_prm + 4), a
        ld      hl, ram_hmmm_prm    ; hmmmのパラメータテーブル
        call    set_vdp_regs        ; vdpレジスタに転送
        ;jp main_loop
        call    wait_vdp

        ;sxにセット
        ld      a, 48
        out     (VDP_P1), a
        ld      a, 36 + $80         ; 32を指定
        out     (VDP_P1), a

        ld      a, 0
        out     (VDP_P1), a
        ld      a, 38 + $80         ; 32を指定
        out     (VDP_P1), a

        ld      a, $d0              ; hmmmコマンド
        out     (VDP_P1), a
        ld      a, 46 + $80         ; r#46 にコマンド送信
        out     (VDP_P1),a

        ei                          ; 割り込み許可

main_loop:
        jr      main_loop

hmmm:
        ld      a, $d0              ; r#36 から開始
        out     (VDP_P1), a
        ld      a, 45 + $80         ; r#17 に 36 を指定
        out     (VDP_P1), a
        ret
set_vdp_regs:
        ld      a, 32               ; レジスタ間接指定の開始番号 (r#32)
        out     (VDP_P1), a
        ld      a,17 + $80          ; r#17に32を指定
        out     (VDP_P1), a
        ; ポート#1に対して、r#32〜r#46までの15バイトを連続出力
        ld      c, VDP_P3
        ld      b, 15
        otir
        ret
set_dx:
        out     (VDP_P1), a
        ld      a,32 + $80          ; 32を指定
        out     (VDP_P1), a
        ret
hmmc_16x16_init:
        ; 2. romにあるパラメータのひな形をramへコピー (ldir)
        ld      hl, rom_prm         ; コピー元（rom）
        ld      de, ram_prm         ; コピー先（ram）
        ld      bc, rom_prm_end - rom_prm   ; 11バイト
        ldir
        ret
;--------------------------------------------------------
; サブルーチン: vdpコマンドレジスタ(r#36〜r#46)の一括設定
; hl = パラメータテーブルの先頭ポインタ
;--------------------------------------------------------
hmmc_16x16:
        ld      d,b
        ld      a,(hl)          ; 第1バイト目を取得
        ld      (ram_clr), a    ; 【修正】ram上の変数領域に書き込み
        inc     hl              ; ポインタを第2バイト目に進める
        push    hl              ; 画像データのポインタを一時退避
        ld      hl, ram_prm     ; 【修正】ramのアドレスを指定

        ; 連続転送レジスタをオートインクリメントのr#36
        ld      a, 36           ; r#36 から開始
        out     (VDP_P1), a
        ld      a, 17 + $80     ; r#17 に 36 を指定
        out     (VDP_P1), a
        ; 連続転送
        ld      c, VDP_P3       ; ポート#3
        ld      b, 11           ; r#36〜r#46 の計11バイト
        otir                    ; 一括高速転送
        pop     hl              ; 画像データのポインタを復帰
        ; 連続転送レジスタを非オートインクリメントのr#44
        ld      a, 44 + $80     ; r#44 の非オートインクリメントにする
        out     (VDP_P1), a
        ld      a, 17 + $80     ; r#17 に 36 を指定
        out     (VDP_P1), a
        ; 残りの127バイトをotirで連続転送
        ld      b, 127          ; 残りのバイト数 (16*8 - 1 = 127)
        otir
        ret

;--------------------------------------------------------
; サブルーチン: vdpコマンドの実行完了（ceフラグ）待ち
;--------------------------------------------------------
wait_vdp:
        ld      a, 2            ; s#2 を指定
        out     (VDP_P1), a
        ld      a, 15 + $80
        out     (VDP_P1), a
.wait_loop:
        in      a, (VDP_P1)     ; s#2 を読み出し
        and     $01             ; bit 0 (ceフラグ) をチェック
        jr      nz, .wait_loop  ; ce=1（実行中）ならループ
        ret


;--------------------------------------------------------
; hmmc パラメータデータひな形（rom領域に配置）
;--------------------------------------------------------
rom_prm:
        dw      0               ; r#36-37: dx (16)
        dw      256             ; r#38-39: dy (16)
        dw      16              ; r#40-41: nx (16)
        dw      16              ; r#42-43: ny (16)
        db      0               ; r#44:    clr (初期値0、ram上で書き換え)
        db      0               ; r#45:    arg (方向フラグ=0)
        db      $f0             ; r#46:    cmd (hmmcコード)
;--------------------------------------------------------
; hmmm パラメータデータ（各項目2バイト、下位・上位バイトの順）
;--------------------------------------------------------
rom_hmmm:
        dw      0               ; r#32-33: sx (ソースx = 0)
        dw      256             ; r#34-35: sy (ソースy = 0)
        dw      0               ; r#36-37: dx (デスティネーションx = 16)
        dw      0               ; r#38-39: dy (デスティネーションy = 16)
        dw      16              ; r#40-41: nx (幅 = 16ドット)
        dw      16              ; r#42-43: ny (高さ = 1ドット)
        dw      0               ; r#44-45: 引数clr/arg (カラーコードの下位上位・方向フラグ)
        db      $d0             ; r#46:    cmd (コマンド種別 = hmmm)
rom_prm_end:
;--------------------------------------------------------
; 画像データ（16×16ドット、計128バイト）
;--------------------------------------------------------
image_data:
        db      $00, $0f, $ff, $ff, $ff, $ff, $f0, $00
        db      $0f, $ff, $ff, $ff, $ff, $ff, $ff, $00
        db      $ff, $f8, $88, $88, $88, $88, $8f, $f0
        db      $ff, $88, $88, $88, $88, $88, $88, $ff
        db      $ff, $88, $88, $88, $88, $88, $88, $ff
        db      $ff, $88, $88, $88, $88, $88, $88, $ff
        db      $ff, $88, $88, $88, $88, $88, $88, $ff
        db      $ff, $88, $88, $88, $88, $88, $88, $ff
        db      $ff, $88, $88, $88, $88, $88, $88, $ff
        db      $ff, $88, $88, $88, $88, $88, $88, $ff
        db      $ff, $88, $88, $88, $88, $88, $88, $ff
        db      $ff, $88, $88, $88, $88, $88, $88, $ff
        db      $ff, $88, $88, $88, $88, $88, $88, $ff
        db      $ff, $f8, $88, $88, $88, $88, $8f, $f0
        db      $0f, $ff, $ff, $ff, $ff, $ff, $ff, $00
        db      $00, $0f, $ff, $ff, $ff, $ff, $f0, $00
end:
        ds      $8000 - $, $ff
