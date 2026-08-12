# 敵スプライトのデータ

いろいろなデータがあるのだけどごちゃごちゃしているので文章にまとめます。

- 敵描画計算
  - ef7_sp00_start 敵Noとスプライト画像(アニメ4パターン)の対応表
    - これで敵Noと名前が紐付きます
  - sprite_ptn_param_tbl z座標に関連
    - EFSub3_get_sprite_pattern_parameters
  - sprite_zoom_parameters ズーム表示用
- 初期化表
  - gf20_enemy_spawn_scripts 生成のスクリプトリスト
    - ステージNoから ENEMY_SPAWN_SCRIPT_0cc77h
    - escript1 - escript17 と escript_bonus の参照で生成Noが含まれている
    - 呼び出し関数 GF20_InitEnemySpawnScript １度に2つ読み込む
  - gf24_sub1_enemy_spawn_cnt_tbl 生成Noから敵の数
  - gf24_sub2_enemy_no_tbl        生成Noから敵No
  - gf24_sub3_enemy_setpos        生成Noから生成位置
  - gf24_sub3_enemy_data_tbl      生成Noから生成データ
  - gf24_sub4_data                生成Noから初期化関数


## ef7_sp00_start

|No|Name          |anim1               |anim2               |anim3               |anim4               |
|--|--------------|--------------------|--------------------|--------------------|--------------------|
| 1|キノコ雲      |spj09_explosion_tree|spj09_explosion_tree|spj09_explosion_tree|spj09_explosion_tree|
| 2|爆発          |spj36_explosion1    |spj37_explosion2    |spj37_explosion2    |spj36_explosion1    |
| 3|火の玉        |spj14_fire          |spj14_fire          |spj14_fire          |spj14_fire          |
| 4|ミサイル緑    |spj15_missile_green |spj15_missile_green |spj15_missile_green |spj15_missile_green |
| 5|ミサイル赤    |spj16_misile_read   |spj16_misile_read   |spj16_misile_read   |spj16_misile_read   |
| 6|ミサイル黒    |spj17_missile_black |spj17_missile_black |spj17_missile_black |spj17_missile_black |
| 7|ミサイル青    |spj18_missile_blue  |spj18_missile_blue  |spj18_missile_blue  |spj18_missile_blue  |
| 8|ミサイル黄    |spj19_missile_yellow|spj19_missile_yellow|spj19_missile_yellow|spj19_missile_yellow|
| 9|敵弾          |spj13_bullet4       |spj12_bullet3       |spj11_bullet2       |spj10_bullet1       |
|10|ムカデンス    |spj26_mukadens      |spj26_mukadens      |spj26_mukadens      |spj26_mukadens      |
|11|スケグ        |spj25_skeg          |spj25_skeg          |spj25_skeg          |spj25_skeg          |
|12|カナリー      |spj27_kanari        |spj27_kanari        |spj27_kanari        |spj27_kanari        |
|13|ルーパー      |spj32_looper        |spj32_looper        |spj32_looper        |spj32_looper        |
|14|パーコメン    |spj28_par           |spj28_par           |spj28_par           |spj28_par           |
|15|ジェット1     |spj29_jet1          |spj29_jet1          |spj29_jet1          |spj29_jet1          |
|16|ジェット2     |spj30_jet2l         |spj31_jet2r         |spj30_jet2l         |spj31_jet2r         |
|17|アイダ        |spj35_ida           |spj35_ida           |spj35_ida           |spj35_ida           |
|18|トモス        |spj38_tomos1        |spj38_tomos1        |spj39_tomos2        |spj40_tomos3        |
|19|ドム緑        |spj41_dom_green_l   |spj42_dom_green_r   |spj41_dom_green_l   |spj42_dom_green_r   |
|20|ドム赤        |spj43_dom_red_l     |spj44_dom_red_r     |spj43_dom_red_l     |spj44_dom_red_r     |
|21|ドム黒        |spj45_dom_black_l   |spj46_dom_black_r   |spj45_dom_black_l   |spj46_dom_black_r   |
|22|ドム青        |spj47_dom_blue_l    |spj48_dom_blue_r    |spj49_dom_blue2     |spj50_dom_blue3     |
|23|木            |spj01_tree1         |spj01_tree1         |                   0|                   0|
|24|枯れ木        |spj02_tree2         |spj02_tree2         |                   0|                   0|
|25|柱黄色        |spj03_tree3         |spj03_tree3         |                   0|                   0|
|26|柱灰色        |spj04_tree4         |spj04_tree4         |                   0|                   0|
|27|ヤシ青        |spj06_tree6         |spj06_tree6         |                   0|                   0|
|28|タワー青      |spj07_tree7         |spj07_tree7         |                   0|                   0|
|29|岩山          |spj08_tree8         |spj08_tree8         |                   0|                   0|
|30|タワー        |spj05_tree5         |spj05_tree5         |                   0|                   0|
|31|マンモス      |spj34_mom           |spj34_mom           |                   0|                   0|
|32|浮遊岩        |spj20_huyu          |spj20_huyu          |                   0|                   0|
|33|氷            |spj21_ice           |spj21_ice           |                   0|                   0|
|34|草            |spj22_kusa          |spj22_kusa          |                   0|                   0|
|35|キノコ        |spj24_kinoko        |spj24_kinoko        |                   0|                   0|
|36|ビンズビーン赤|spj33_bean_red      |spj33_bean_red      |                   0|                   0|
|37|ビンズビーン赤|spj33_bean_red      |spj33_bean_red      |                   0|                   0|
|38|岩            |spj23_iwa           |spj23_iwa           |                   0|                   0|
|39|岩            |spj35_ida           |spj35_ida           |                   0|                   0|
|40|草2           |spj51_kusa2         |spj51_kusa2         |                   0|                   0|
|41|ヤシ紫        |spj52_tree9         |spj52_tree9         |                   0|                   0|
|42|ヤシ緑        |spj53_tree10        |spj53_tree10        |                   0|                   0|
|43|タワー緑      |spj54_tree11        |spj54_tree11        |                   0|                   0|
|44|タワー赤      |spj55_tree12        |spj55_tree12        |                   0|                   0|
|45|ビンズビーン緑|spj56_bean_green    |spj56_bean_green    |                   0|                   0|
|46|ビンズビーン赤|spj57_bean_yellow   |spj33_bean_red      |                   0|                   0|
|47|浮遊岩        |spj58_huyu_iwa      |spj58_huyu_iwa      |                   0|                   0|
|48|タイトル左側  |spj107_title1l      |spj109_title2l      |spj111_title3l      |spj109_title2l      |
|49|タイトル右側  |spj108_title1r      |spj110_title1r      |spj112_title3r      |spj110_title1r      |
|50|氷山          |spj113_tree_kouri   |spj113_tree_kouri   |                   0|                   0|
|51|岩3           |spj115_iwa3         |spj115_iwa3         |                   0|                   0|
|52|岩4           |spj116_iwa4         |spj116_iwa4         |                   0|                   0|
|53|機械岩        |spj117_kikai_tree   |spj117_kikai_tree   |                   0|                   0|

# gf24_sub1_enemy_spawn_cnt_tbl 生成Noから敵の数

        ;  1,2,3,4,5,6,7,8,9,10
        db 3,3,3,3,3,3,3,3,3,3 ;  1-10
        db 3,3,3,3,3,3,3,3,4,7 ; 11-20
        db 7,3,3,3,3,3,3,3,1,2 ; 21-30
        db 3,1,2,3,3,1,1,1,1,1 ; 31-40
        db 1,1,1,3,3,1,1,1,1,3 ; 41-50
        db 1,1,4,1,1,1,1,1,1,1 ; 51-60
        db 1,1,1,1,1           ; 61-65

# gf24_sub3_enemy_setpos        生成Noから生成位置

    gf24_sub3_enemy_setpos:
    gf24_sub3_enemy_setpos_start:
        db 003h,004h,005h,006h,00ah,00bh
    gf24_sub3_enemy_setpos_last:
        db 00dh


# gf24_sub4_data                生成Noから初期化関数

    gf24_sub4_data:
        ;       0,  1,  2,  3,  4,  5,  6,  7
    es_01: dw es2,es0,es0,es0,es0,es0,es0,es0
    es_09: dw es0,es0,es0,es0,es0,es0,es0,es0
    es_11: dw es0,es5,es6,es4,es4,es0,es0,es2
    es_19: dw es0,es0,es7,es8,es1,es1,es1,es1
    es_21: dw es1,es1,es9,es0,es0,es0,es0,es0
    es_29: dw es0,es0,es0,es0,es0,es0,es0,es0
    es_31: dw es0,es9,es0,es0,es0,es0,es0,es0
    es_39: dw es0,es0,es0,es0,es0,es0,es0,es0
    es_41: dw es0,es0,es0,es0,es0,es0,es0,es0
    es_49: dw es0,es0,es0,es0,es0

## gf24_sub2_enemy_no_tbl 生成Noから敵No

        db 10,10,10,10,10,10,10,10,10,10 ;  1-10
        db 10,10,10,10,11,11,11,12,17,13 ; 11-20
        db 13,14,14,15,16,16,16,16,17,17 ; 21-30
        db 17,17,17,17,18,19,19,19,19,20 ; 31-40
        db 20,20,20,21,21,22,22,22,22,22 ; 41-50
        db 22,22,17,17, 1, 1, 1, 1, 1, 1 ; 51-60


## sprite_ptn_param_tbl
