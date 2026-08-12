    include "spj.asm"
; --------------------------------------------------------------------------
; 通常敵の画像テーブル (ボスやエンディングはない)
ef7_sp00_start:
    ;  anim1               ,anim2               ,anim3               ,anim4                ;no hex ,name
    ; 爆発
    dw spj09_explosion_tree,spj09_explosion_tree,spj09_explosion_tree,spj09_explosion_tree ;1  0x01,キノコ雲
    dw spj36_explosion1    ,spj37_explosion2    ,spj37_explosion2    ,spj36_explosion1     ;2  0x02,爆発2
    ; 弾
    dw spj14_fire          ,spj14_fire          ,spj14_fire          ,spj14_fire           ;3  0x03,火の玉
    dw spj15_missile_green ,spj15_missile_green ,spj15_missile_green ,spj15_missile_green  ;4  0x04,ミサイル緑
    dw spj16_misile_read   ,spj16_misile_read   ,spj16_misile_read   ,spj16_misile_read    ;5  0x05,ミサイル赤
    dw spj17_missile_black ,spj17_missile_black ,spj17_missile_black ,spj17_missile_black  ;6  0x06,ミサイル黒
    dw spj18_missile_blue  ,spj18_missile_blue  ,spj18_missile_blue  ,spj18_missile_blue   ;7  0x07,ミサイル青
    dw spj19_missile_yellow,spj19_missile_yellow,spj19_missile_yellow,spj19_missile_yellow ;8  0x08,ミサイル黄
    dw spj13_bullet4       ,spj12_bullet3       ,spj11_bullet2       ,spj10_bullet1        ;9  0x09,敵弾
    ; 通常敵
    dw spj26_mukadens      ,spj26_mukadens      ,spj26_mukadens      ,spj26_mukadens       ;10 0x0a,ムカデンス
    dw spj25_skeg          ,spj25_skeg          ,spj25_skeg          ,spj25_skeg           ;11 0x0b,スケグ
    dw spj27_kanari        ,spj27_kanari        ,spj27_kanari        ,spj27_kanari         ;12 0x0c,カナリー
    dw spj32_looper        ,spj32_looper        ,spj32_looper        ,spj32_looper         ;13 0x0d,ルーパー
    dw spj28_par           ,spj28_par           ,spj28_par           ,spj28_par            ;14 0x0e,パーコメン
    dw spj29_jet1          ,spj29_jet1          ,spj29_jet1          ,spj29_jet1           ;15 0x0f,ジェット1
    dw spj30_jet2l         ,spj31_jet2r         ,spj30_jet2l         ,spj31_jet2r          ;16 0x10,ジェット2
    dw spj35_ida           ,spj35_ida           ,spj35_ida           ,spj35_ida            ;17 0x11,アイダ
    dw spj38_tomos1        ,spj38_tomos1        ,spj39_tomos2        ,spj40_tomos3         ;18 0x12,トモス
    dw spj41_dom_green_l   ,spj42_dom_green_r   ,spj41_dom_green_l   ,spj42_dom_green_r    ;19 0x13,ドム緑
    dw spj43_dom_red_l     ,spj44_dom_red_r     ,spj43_dom_red_l     ,spj44_dom_red_r      ;20 0x14,ドム赤
    dw spj45_dom_black_l   ,spj46_dom_black_r   ,spj45_dom_black_l   ,spj46_dom_black_r    ;21 0x15,ドム黒
    dw spj47_dom_blue_l    ,spj48_dom_blue_r    ,spj49_dom_blue2     ,spj50_dom_blue3      ;22 0x16,ドム青
    ; 地上物
    ;  anim1            ,anim2            ,3,4 ;no hex ,name
    dw spj01_tree1      ,spj01_tree1      ,0,0 ;23 0x17,木
    dw spj02_tree2      ,spj02_tree2      ,0,0 ;24 0x18,枯れ木
    dw spj03_tree3      ,spj03_tree3      ,0,0 ;25 0x19,柱黄色
    dw spj04_tree4      ,spj04_tree4      ,0,0 ;26 0x1a,柱灰色
    dw spj06_tree6      ,spj06_tree6      ,0,0 ;27 0x1b,ヤシ青
    dw spj07_tree7      ,spj07_tree7      ,0,0 ;28 0x1c,タワー青
    dw spj08_tree8      ,spj08_tree8      ,0,0 ;29 0x1d,岩山
    dw spj05_tree5      ,spj05_tree5      ,0,0 ;30 0x1e,タワー
    dw spj34_mom        ,spj34_mom        ,0,0 ;31 0x1f,マンモス
    dw spj20_huyu       ,spj20_huyu       ,0,0 ;32 0x20,浮遊岩
    dw spj21_ice        ,spj21_ice        ,0,0 ;33 0x21,氷
    dw spj22_kusa       ,spj22_kusa       ,0,0 ;34 0x22,草
    dw spj24_kinoko     ,spj24_kinoko     ,0,0 ;35 0x23,キノコ
    dw spj33_bean_red   ,spj33_bean_red   ,0,0 ;36 0x24,ビンズビーン赤
    dw spj33_bean_red   ,spj33_bean_red   ,0,0 ;37 0x25,ビンズビーン赤
    dw spj23_iwa        ,spj23_iwa        ,0,0 ;38 0x26,岩
    dw spj35_ida        ,spj35_ida        ,0,0 ;39 0x27,岩
    dw spj51_kusa2      ,spj51_kusa2      ,0,0 ;40 0x28,草2
    dw spj52_tree9      ,spj52_tree9      ,0,0 ;41 0x29,ヤシ紫
    dw spj53_tree10     ,spj53_tree10     ,0,0 ;42 0x2a,ヤシ緑
    dw spj54_tree11     ,spj54_tree11     ,0,0 ;43 0x2b,タワー緑
    dw spj55_tree12     ,spj55_tree12     ,0,0 ;44 0x2c,タワー赤
    dw spj56_bean_green ,spj56_bean_green ,0,0 ;45 0x2d,ビンズビーン緑
    dw spj57_bean_yellow,spj33_bean_red   ,0,0 ;46 0x2e,ビンズビーン赤
    dw spj58_huyu_iwa   ,spj58_huyu_iwa   ,0,0 ;47 0x2f,浮遊岩
    ; タイトル
    dw spj107_title1l   ,spj109_title2l,spj111_title3l,spj109_title2l ;48 0x30,タイトル左側
    dw spj108_title1r   ,spj110_title1r,spj112_title3r,spj110_title1r ;49 0x31,タイトル右側
    ; 地上物
    dw spj113_tree_kouri,spj113_tree_kouri,0,0 ;50 0x32,氷山
    dw spj115_iwa3      ,spj115_iwa3      ,0,0 ;51 0x33,岩3
    dw spj116_iwa4      ,spj116_iwa4      ,0,0 ;52 0x34,岩4
    dw spj117_kikai_tree,spj117_kikai_tree,0,0 ;53 0x35,機械岩





ef0a_spj_tbl:
	dw 0                    ,0                    ,0                    ,0                     ; 0,0x00,なし
	dw spj59_boss_explosion1,spj60_boss_explosion2,spj60_boss_explosion2,spj59_boss_explosion1 ; 1,0x01,ボス爆発
	dw spj14_fire           ,spj14_fire           ,spj14_fire           ,spj14_fire            ; 2,0x02,火の玉
	dw spj15_missile_green  ,spj15_missile_green  ,spj15_missile_green  ,spj15_missile_green   ; 3,0x03,ミサイル緑
	dw spj16_misile_read    ,spj16_misile_read    ,spj16_misile_read    ,spj16_misile_read     ; 4,0x04,ミサイル赤
	dw spj17_missile_black  ,spj17_missile_black  ,spj17_missile_black  ,spj17_missile_black   ; 5,0x05,ミサイル黒
	dw spj18_missile_blue   ,spj18_missile_blue   ,spj18_missile_blue   ,spj18_missile_blue    ; 6,0x06,ミサイル青
	dw 0                    ,0                    ,0                    ,0                     ; 7,0x07,なし
	dw spj13_bullet4        ,spj12_bullet3        ,spj11_bullet2        ,spj10_bullet1         ; 8,0x08,敵弾
	dw spj61_oct            ,spj61_oct            ,spj61_oct            ,spj61_oct             ; 9,0x09,オクト
	dw spj84_sq_head3       ,spj83_sq_head2       ,spj82_sq_head1       ,spj62_sq_head0        ;10,0x0a,スケイラ頭
	dw spj87_sq_body3       ,spj86_sq_body2       ,spj85_sq_body1       ,spj63_sq_body0        ;11,0x0b,スケイラ体
	dw spj64_ida_head       ,spj64_ida_head       ,0                    ,0                     ;12,0x0c,アイダ頭
	dw spj90_godani_head3   ,spj89_godani_head2   ,spj88_godani_head1   ,spj65_godani_head0    ;13,0x0d,ゴダーニ頭
	dw spj66_rolly1         ,spj66_rolly1         ,spj67_rolly2         ,spj67_rolly2          ;14,0x0e,ローリー
	dw spj66_rolly1         ,spj66_rolly1         ,spj67_rolly2         ,spj67_rolly2          ;15,0x0f,ローリー
	dw spj68_tetra1         ,spj69_tetra2         ,spj69_tetra2         ,spj69_tetra2          ;16,0x10,テトラ
	dw spj68_tetra1         ,spj69_tetra2         ,spj69_tetra2         ,spj69_tetra2          ;17,0x11,テトラ
	dw spj70_syura          ,spj70_syura          ,spj70_syura          ,spj70_syura           ;18,0x12,シュラ
	dw spj93_hone_head3     ,spj92_hone_head2     ,spj91_hone_head1     ,spj71_hone_head       ;19,0x13,骨頭
	dw spj96_hone_body3     ,spj95_hone_body2     ,spj94_hone_body1     ,spj72_hone_body       ;20,0x14,骨体
	dw spj73_komainu_l      ,valb75ch             ,spj73_komainu_l      ,spj73_komainu_l       ;21,0x15,狛犬左
	dw spj74_komainu_r      ,spj74_komainu_r      ,spj74_komainu_r      ,spj74_komainu_r       ;22,0x16,狛犬右
	dw spj75_stanray_l      ,spj75_stanray_l      ,spj75_stanray_l      ,spj75_stanray_l       ;23,0x17,スタンレー左
	dw spj76_stanray_c      ,spj76_stanray_c      ,spj76_stanray_c      ,spj76_stanray_c       ;24,0x18,スタンレー中
	dw spj77_stanray_r      ,spj77_stanray_r      ,spj77_stanray_r      ,spj77_stanray_r       ;25,0x19,スタンレー右
	dw spj81_wiwi3          ,spj78_wiwi1          ,spj79_wiwi2          ,spj79_wiwi2           ;26,0x1a,ウィウィジャンボウ
	dw spj42_dom_green_r    ,spj41_dom_green_l    ,spj42_dom_green_r    ,spj41_dom_green_l     ;27,0x1b,ドム緑
	dw spj44_dom_red_r      ,spj43_dom_red_l      ,spj44_dom_red_r      ,spj43_dom_red_l       ;28,0x1c,ドム赤
	dw spj45_dom_black_l    ,spj46_dom_black_r    ,val58c8h_on_spj_tbl  ,spj45_dom_black_l     ;29,0x1d,ドム黒
	dw spj114_dom_muteki    ,spj48_dom_blue_r     ,spj49_dom_blue2      ,spj50_dom_blue3       ;30,0x1e,ドム青
	dw spj38_tomos1         ,spj39_tomos2         ,spj40_tomos3         ,spj40_tomos3          ;31,0x1f,トモス
	dw spj21_ice            ,spj21_ice            ,spj21_ice            ,spj21_ice             ;32,0x20,氷
	dw spj35_ida            ,spj35_ida            ,spj35_ida            ,spj35_ida             ;33,0x21,アイダ
	dw spj80_looper_p       ,spj80_looper_p       ,spj80_looper_p       ,spj80_looper_p        ;34,0x22,ルーパー紫
	dw spj08_tree8          ,spj08_tree8          ,0                    ,0                     ;35,0x23,機械タワー
	dw spj30_jet2l          ,spj31_jet2r          ,spj30_jet2l          ,spj31_jet2r           ;36,0x24,ジェット2
	dw spj23_iwa            ,spj23_iwa            ,0                    ,0                     ;37,0x25,岩
	dw 0                    ,0                    ,0                    ,0                     ;38,0x26,
	dw 0                    ,0                    ,0                    ,0                     ;39,0x27,
	dw 0                    ,0                    ,0                    ,0                     ;40,0x28,
	dw 0                    ,0                    ,0                    ,0                     ;41,0x29,
	dw 0                    ,0                    ,0                    ,0                     ;42,0x2a,
	dw spj105_hayaoh_head   ,spj105_hayaoh_head   ,spj105_hayaoh_head   ,spj105_hayaoh_head    ;43,0x2b,ハヤオー頭
	dw spj106_hayaoh_body   ,spj106_hayaoh_body   ,spj106_hayaoh_body   ,spj106_hayaoh_body    ;44,0x2c,ハヤオー体
















































































































































































































































