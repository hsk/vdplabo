
head = ["anim1","anim2","anim3","anim4","no","hex","name"]
ef7_sp00_start = [
    #  anim1               ,anim2               ,anim3               ,anim4                #no hex ,name
    # 爆発
    ["spj09_explosion_tree","spj09_explosion_tree","spj09_explosion_tree","spj09_explosion_tree", 1 , 0x01,"キノコ雲"],
    ["spj36_explosion1"    ,"spj37_explosion2"    ,"spj37_explosion2"    ,"spj36_explosion1"    , 2 , 0x02,"爆発"],
    # 弾
    ["spj14_fire"          ,"spj14_fire"          ,"spj14_fire"          ,"spj14_fire"          , 3 , 0x03,"火の玉"],
    ["spj15_missile_green" ,"spj15_missile_green" ,"spj15_missile_green" ,"spj15_missile_green" , 4 , 0x04,"ミサイル緑"],
    ["spj16_misile_read"   ,"spj16_misile_read"   ,"spj16_misile_read"   ,"spj16_misile_read"   , 5 , 0x05,"ミサイル赤"],
    ["spj17_missile_black" ,"spj17_missile_black" ,"spj17_missile_black" ,"spj17_missile_black" , 6 , 0x06,"ミサイル黒"],
    ["spj18_missile_blue"  ,"spj18_missile_blue"  ,"spj18_missile_blue"  ,"spj18_missile_blue"  , 7 , 0x07,"ミサイル青"],
    ["spj19_missile_yellow","spj19_missile_yellow","spj19_missile_yellow","spj19_missile_yellow", 8 , 0x08,"ミサイル黄"],
    ["spj13_bullet4"       ,"spj12_bullet3"       ,"spj11_bullet2"       ,"spj10_bullet1"       , 9 , 0x09,"敵弾"],
    # 通常敵
    ["spj26_mukadens"      ,"spj26_mukadens"      ,"spj26_mukadens"      ,"spj26_mukadens"      , 10, 0x0a,"ムカデンス"],
    ["spj25_skeg"          ,"spj25_skeg"          ,"spj25_skeg"          ,"spj25_skeg"          , 11, 0x0b,"スケグ"],
    ["spj27_kanari"        ,"spj27_kanari"        ,"spj27_kanari"        ,"spj27_kanari"        , 12, 0x0c,"カナリー"],
    ["spj32_looper"        ,"spj32_looper"        ,"spj32_looper"        ,"spj32_looper"        , 13, 0x0d,"ルーパー"],
    ["spj28_par"           ,"spj28_par"           ,"spj28_par"           ,"spj28_par"           , 14, 0x0e,"パーコメン"],
    ["spj29_jet1"          ,"spj29_jet1"          ,"spj29_jet1"          ,"spj29_jet1"          , 15, 0x0f,"ジェット1"],
    ["spj30_jet2l"         ,"spj31_jet2r"         ,"spj30_jet2l"         ,"spj31_jet2r"         , 16, 0x10,"ジェット2"],
    ["spj35_ida"           ,"spj35_ida"           ,"spj35_ida"           ,"spj35_ida"           , 17, 0x11,"アイダ"],
    ["spj38_tomos1"        ,"spj38_tomos1"        ,"spj39_tomos2"        ,"spj40_tomos3"        , 18, 0x12,"トモス"],
    ["spj41_dom_green_l"   ,"spj42_dom_green_r"   ,"spj41_dom_green_l"   ,"spj42_dom_green_r"   , 19, 0x13,"ドム緑"],
    ["spj43_dom_red_l"     ,"spj44_dom_red_r"     ,"spj43_dom_red_l"     ,"spj44_dom_red_r"     , 20, 0x14,"ドム赤"],
    ["spj45_dom_black_l"   ,"spj46_dom_black_r"   ,"spj45_dom_black_l"   ,"spj46_dom_black_r"   , 21, 0x15,"ドム黒"],
    ["spj47_dom_blue_l"    ,"spj48_dom_blue_r"    ,"spj49_dom_blue2"     ,"spj50_dom_blue3"     , 22, 0x16,"ドム青"],
    # 地上物
    #  anim1            ,anim2              ,3,4, no, hex,name
    ["spj01_tree1"      ,"spj01_tree1"      ,0,0, 23, 0x17,"木"],
    ["spj02_tree2"      ,"spj02_tree2"      ,0,0, 24, 0x18,"枯れ木"],
    ["spj03_tree3"      ,"spj03_tree3"      ,0,0, 25, 0x19,"柱黄色"],
    ["spj04_tree4"      ,"spj04_tree4"      ,0,0, 26, 0x1a,"柱灰色"],
    ["spj06_tree6"      ,"spj06_tree6"      ,0,0, 27, 0x1b,"ヤシ青"],
    ["spj07_tree7"      ,"spj07_tree7"      ,0,0, 28, 0x1c,"タワー青"],
    ["spj08_tree8"      ,"spj08_tree8"      ,0,0, 29, 0x1d,"岩山"],
    ["spj05_tree5"      ,"spj05_tree5"      ,0,0, 30, 0x1e,"タワー"],
    ["spj34_mom"        ,"spj34_mom"        ,0,0, 31, 0x1f,"マンモス"],
    ["spj20_huyu"       ,"spj20_huyu"       ,0,0, 32, 0x20,"浮遊岩"],
    ["spj21_ice"        ,"spj21_ice"        ,0,0, 33, 0x21,"氷"],
    ["spj22_kusa"       ,"spj22_kusa"       ,0,0, 34, 0x22,"草"],
    ["spj24_kinoko"     ,"spj24_kinoko"     ,0,0, 35, 0x23,"キノコ"],
    ["spj33_bean_red"   ,"spj33_bean_red"   ,0,0, 36, 0x24,"ビンズビーン赤"],
    ["spj33_bean_red"   ,"spj33_bean_red"   ,0,0, 37, 0x25,"ビンズビーン赤"],
    ["spj23_iwa"        ,"spj23_iwa"        ,0,0, 38, 0x26,"岩"],
    ["spj35_ida"        ,"spj35_ida"        ,0,0, 39, 0x27,"岩"],
    ["spj51_kusa2"      ,"spj51_kusa2"      ,0,0, 40, 0x28,"草2"],
    ["spj52_tree9"      ,"spj52_tree9"      ,0,0, 41, 0x29,"ヤシ紫"],
    ["spj53_tree10"     ,"spj53_tree10"     ,0,0, 42, 0x2a,"ヤシ緑"],
    ["spj54_tree11"     ,"spj54_tree11"     ,0,0, 43, 0x2b,"タワー緑"],
    ["spj55_tree12"     ,"spj55_tree12"     ,0,0, 44, 0x2c,"タワー赤"],
    ["spj56_bean_green" ,"spj56_bean_green" ,0,0, 45, 0x2d,"ビンズビーン緑"],
    ["spj57_bean_yellow","spj33_bean_red"   ,0,0, 46, 0x2e,"ビンズビーン赤"],
    ["spj58_huyu_iwa"   ,"spj58_huyu_iwa"   ,0,0, 47, 0x2f,"浮遊岩"],
    # タイトル
    ["spj107_title1l"   ,"spj109_title2l","spj111_title3l","spj109_title2l", 48, 0x30,"タイトル左側"],
    ["spj108_title1r"   ,"spj110_title1r","spj112_title3r","spj110_title1r", 49, 0x31,"タイトル右側"],
    # 地上物
    ["spj113_tree_kouri","spj113_tree_kouri",0,0, 50, 0x32,"氷山"],
    ["spj115_iwa3"      ,"spj115_iwa3"      ,0,0, 51, 0x33,"岩3"],
    ["spj116_iwa4"      ,"spj116_iwa4"      ,0,0, 52, 0x34,"岩4"],
    ["spj117_kikai_tree","spj117_kikai_tree",0,0, 53, 0x35,"機械岩"],
]

import unicodedata

def text_width(s):
    width = 0
    for c in s:
        if unicodedata.east_asian_width(c) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width

print(f"|No|Name          |{'anim1':20}|{'anim2':20}|{'anim3':20}|{'anim4':20}|")
print(f"|--|--------------|{'-'*20}|{'-'*20}|{'-'*20}|{'-'*20}|")
for v in ef7_sp00_start:
    print(f"|{v[5]:2}|{v[6]}{' ' * (14-text_width(v[6]))}|{v[0]:20}|{v[1]:20}|{v[2]:20}|{v[3]:20}|")

gf24_sub2_enemy_no_tbl = [ # 生成Noから敵No
    10,10,10,10,10,10,10,10,10,10, #  1-10
    10,10,10,10,11,11,11,12,17,13, # 11-20
    13,14,14,15,16,16,16,16,17,17, # 21-30
    17,17,17,17,18,19,19,19,19,20, # 31-40
    20,20,20,21,21,22,22,22,22,22, # 41-50
    22,22,17,17, 1, 1, 1, 1, 1, 1, # 51-60
]

gf24_sub1_enemy_spawn_cnt_tbl = [ #生成Noから敵の数
      # 1,2,3,4,5,6,7,8,9,10
        3,3,3,3,3,3,3,3,3,3, #  1-10
        3,3,3,3,3,3,3,3,4,7, # 11-20
        7,3,3,3,3,3,3,3,1,2, # 21-30
        3,1,2,3,3,1,1,1,1,1, # 31-40
        1,1,1,3,3,1,1,1,1,3, # 41-50
        1,1,4,1,1,1,1,1,1,1, # 51-60
        1,1,1,1,1,           # 61-65
]

gf24_sub3_enemy_setpos = [3,4,5,6,10,11,13]

gf24_sub3_enemy_data_tbl = [
    'ed01','ed02','ed03','ed04','ed05','ed06','ed07','ed08','ed09','ed10', #  1-10
    'ed11','ed12','ed13','ed14','ed15','ed16','ed17','ed18','ed19','ed20', # 11-20
    'ed21','ed22','ed23','ed24','ed25','ed26','ed27','ed28','ed29','ed30', # 21-30
    'ed31','ed32','ed33','ed34','ed35','ed36','ed37','ed38','ed39','ed40', # 31-40
    'ed41','ed42','ed43','ed44','ed45','ed46','ed47','ed48','ed49','ed50', # 41-50
    'ed51','ed52','ed53','ed01','ed01',                                    # 51-55
]
eds = {
        #                             AINO,
        #       3,   4,   5,   6,00ah,00bh,00dh , # 設定位置
    "ed01": [0x0e,0x14,0x20,0x00,0x09,0x28,0x03], # ムカデンス 1,アイダ9,キノコ雲1
    "ed02": [0x09,0x00,0x00,0x00,0x09,0x0f,0x03], # ムカデンス 2
    "ed03": [0x02,0x10,0x03,0x00,0x09,0x10,0x03], # ムカデンス 3
    "ed04": [0x02,0x10,0x35,0x00,0x09,0x11,0x03], # ムカデンス 4
    "ed05": [0x02,0x10,0x3f,0x00,0x09,0x12,0x03], # ムカデンス 5
    "ed06": [0x02,0x10,0x03,0x00,0x09,0x13,0x03], # ムカデンス 6
    "ed07": [0x02,0x10,0x04,0x00,0x09,0x14,0x03], # ムカデンス 7
    "ed08": [0x02,0x10,0x30,0x00,0x09,0x15,0x03], # ムカデンス 8
    "ed09": [0x1b,0x14,0x0d,0x00,0x09,0x16,0x03], # ムカデンス 9
    "ed10": [0x1b,0x14,0x31,0x00,0x09,0x17,0x03], # ムカデンス 10
    "ed11": [0x16,0x14,0x00,0x00,0x09,0x18,0x03], # ムカデンス 11
    "ed12": [0x16,0x14,0x39,0x00,0x09,0x19,0x03], # ムカデンス 12
    "ed13": [0x12,0x00,0x28,0x00,0x09,0x1a,0x03], # ムカデンス 13
    "ed14": [0x02,0x10,0x00,0x00,0x09,0x29,0x03], # ムカデンス 14
    "ed15": [0x10,0x00,0x00,0x00,0x09,0x0a,0x03], # スケグ1
    "ed16": [0x06,0x03,0x00,0x00,0x09,0x0b,0x03], # スケグ2
    "ed17": [0x06,0x03,0x30,0x00,0x09,0x0c,0x03], # スケグ3
    "ed18": [0x1b,0x0d,0x20,0x00,0x03,0x02,0x03], # カナリー1
    "ed19": [0x1b,0x15,0x1a,0x00,0x00,0x01,0x04], # アイダ1
    "ed20": [0x1b,0x0f,0x20,0x00,0x00,0x06,0x03], # ルーパー1
    "ed21": [0x1b,0x0b,0x20,0x00,0x00,0x07,0x03], # ルーパー2
    "ed22": [0x1b,0x0b,0x28,0x00,0x09,0x03,0x03], # パーコメン1
    "ed23": [0x13,0x0b,0x00,0x00,0x09,0x04,0x03], # パーコメン2
    "ed24": [0x1b,0x0f,0x20,0x00,0x08,0x02,0x03], # ジェット11
    "ed25": [0x1b,0x10,0x3c,0x00,0x07,0x0d,0x05], # ジェット21
    "ed26": [0x1b,0x10,0x00,0x01,0x07,0x0e,0x05], # ジェット22
    "ed27": [0x1b,0x0c,0x40,0x00,0x07,0x0d,0x05], # ジェット23
    "ed28": [0x1b,0x0c,0x00,0x01,0x07,0x0e,0x05], # ジェット24
    "ed29": [0x1b,0x0c,0x1e,0x00,0x03,0x08,0x05], # アイダ2
    "ed30": [0x1b,0x0c,0x1e,0x00,0x03,0x08,0x05], # アイダ3
    "ed31": [0x1b,0x0c,0x1e,0x00,0x03,0x08,0x05], # アイダ4
    "ed32": [0x1b,0x0c,0x0e,0x01,0x03,0x09,0x05], # アイダ5
    "ed33": [0x1b,0x0c,0x0e,0x01,0x03,0x09,0x05], # アイダ6
    "ed34": [0x1b,0x0c,0x0e,0x01,0x03,0x09,0x05], # アイダ7
    "ed35": [0x1b,0x0b,0x20,0x03,0x09,0x05,0x03], # トモス1
    "ed36": [0x1b,0x10,0x28,0x00,0x04,0x1b,0x05], # ドム緑1
    "ed37": [0x1b,0x10,0x0d,0x01,0x04,0x1c,0x05], # ドム緑2
    "ed38": [0x1b,0x10,0x28,0x01,0x04,0x1d,0x05], # ドム緑3
    "ed39": [0x1b,0x10,0x0d,0x00,0x04,0x1e,0x05], # ドム緑4
    "ed40": [0x1b,0x10,0x28,0x01,0x05,0x1d,0x05], # ドム赤1
    "ed41": [0x1b,0x10,0x0d,0x00,0x05,0x1e,0x05], # ドム赤2
    "ed42": [0x1b,0x10,0x28,0x01,0x05,0x1f,0x05], # ドム赤3
    "ed43": [0x1b,0x10,0x0d,0x00,0x05,0x20,0x05], # ドム赤4
    "ed44": [0x1b,0x10,0x05,0x00,0x06,0x21,0x03], # ドム黒1
    "ed45": [0x1b,0x10,0x32,0x01,0x06,0x22,0x03], # ドム黒2
    "ed46": [0x02,0x0a,0x05,0x03,0x07,0x23,0x03], # ドム青1
    "ed47": [0x02,0x0a,0x32,0x03,0x07,0x24,0x03], # ドム青2
    "ed48": [0x1b,0x10,0x0f,0x01,0x07,0x25,0x03], # ドム青3
    "ed49": [0x1b,0x10,0x27,0x00,0x07,0x26,0x03], # ドム青4
    "ed50": [0x1b,0x0c,0x20,0x02,0x07,0x27,0x03], # ドム青5
    "ed51": [0x1b,0x10,0x05,0x00,0x07,0x25,0x03], # ドム青6
    "ed52": [0x1b,0x10,0x32,0x00,0x07,0x26,0x03], # ドム青7
    "ed53": [0x1b,0x15,0x1a,0x00,0x00,0x01,0x04], # アイダ8
}

ai1_a1_sub_tbl = [
	'A1S01','A1S02','A1S03','A1S04','A1S05','A1S06','A1S07','A1S08','A1S08','A1S0A','A1S0B','A1S0C','A1S0D','A1S0E','A1S0F','A1S10',
	'A1S11','A1S12','A1S13','A1S14','A1S14','A1S16','A1S16','A1S18','A1S18','A1S1A','A1S1B','A1S1C','A1S1D','A1S1E','A1S1F','A1S20',
	'A1S21','A1S22','A1S23','A1S24','A1S25','A1S25','A1S27','A1S28','A1S29','A1S2A','A1S2B','A1S2A','A1S2A','A1S2E','A1S2F','A1S30',
	'A1S2F','A1S2F','A1S2F','A1S2F','A1S2F','A1S2F',
]
gf24_sub4_data = [
    #   0,    1,  2,  3,  4,  5,  6,  7
    "es2","es0","es0","es0","es0","es0","es0","es0",
    "es0","es0","es0","es0","es0","es0","es0","es0",
    "es0","es5","es6","es4","es4","es0","es0","es2",
    "es0","es0","es7","es8","es1","es1","es1","es1",
    "es1","es1","es9","es0","es0","es0","es0","es0",
    "es0","es0","es0","es0","es0","es0","es0","es0",
    "es0","es9","es0","es0","es0","es0","es0","es0",
    "es0","es0","es0","es0","es0","es0","es0","es0",
    "es0","es0","es0","es0","es0","es0","es0","es0",
    "es0","es0","es0","es0","es0",
]
enemy_tbl = {}

# 生成No -> 敵生成スクリプト
for spawn_no, es in enumerate(gf24_sub4_data, start=1):
    enemy_tbl.setdefault(spawn_no, {})
    enemy_tbl[spawn_no]["es"] = es

# 生成No -> 敵Data
for spawn_no, enemy_data in enumerate(gf24_sub3_enemy_data_tbl, start=1):
    enemy_tbl.setdefault(spawn_no, {})
    enemy_tbl[spawn_no]["enemy_data"] = enemy_data

# 生成No -> 敵No
for spawn_no, enemy_no in enumerate(gf24_sub2_enemy_no_tbl, start=1):
    enemy_tbl.setdefault(spawn_no, {})
    enemy_tbl[spawn_no]["enemy_no"] = enemy_no
# 生成No -> 出現数
for spawn_no, cnt in enumerate(gf24_sub1_enemy_spawn_cnt_tbl, start=1):
    enemy_tbl.setdefault(spawn_no, {})
    enemy_tbl[spawn_no]["spawn_cnt"] = cnt

for spawn_no,v in enemy_tbl.items():
    if not "enemy_no" in v: continue
    print(f"v = {int(v['enemy_no'])}")
    if int(v["enemy_no"]-1) > len(ef7_sp00_start): continue
    v2 = ef7_sp00_start[int(v["enemy_no"]-1)]
    print(f"v2 = {v2}")
    enemy_tbl[spawn_no]["enemy_name"] = v2[6]
    enemy_tbl[spawn_no]['a1'] = v2[0]
    enemy_tbl[spawn_no]['a2'] = v2[1]
    enemy_tbl[spawn_no]['a3'] = v2[2]
    enemy_tbl[spawn_no]['a4'] = v2[3]
    data = enemy_tbl[spawn_no].get('enemy_data','')
    ai = eds.get(data,[1,2,3,4,5,0xff])[5]
    AS =  ai1_a1_sub_tbl[ai-1] if ai-1 < len(ai1_a1_sub_tbl) else ""
    ai = f"{ai:02X}" if ai != 0xff else ""
    enemy_tbl[spawn_no]['ai'] = ai
    enemy_tbl[spawn_no]['as'] = AS
#print(enemy_tbl)

names = {}

print(f"|SpawnNo|Name        |No|Cnt|Img 1|Img 2|Img 3|Img 4|Ed  |Fun|AI|AS   |")
print(f"|-------|------------|--|---|-----|-----|-----|-----|----|---|--|-----|")
for k,v in enemy_tbl.items():
    no = v.get("enemy_no", "")
    cnt = v.get('spawn_cnt',"")
    name = v.get('enemy_name','')
    namid = names.get(name,1)
    names[name] = namid+1
    name += str(namid)
    v['name'] = name
    name += (' ' * (12-text_width(name)))
    a1 = v.get('a1','')[0:5] if v.get('a1','') != 0 else '    0'
    a2 = v.get('a2','')[0:5] if v.get('a2','') != 0 else '    0'
    a3 = v.get('a3','')[0:5] if v.get('a3','') != 0 else '    0'
    a4 = v.get('a4','')[0:5] if v.get('a4','') != 0 else '    0'
    data = v.get('enemy_data','')
    es = v.get('es','')
    ai = v.get('ai','')
    AS = v.get('as','')
    print(f"|{k:7}|{name}|{no:2}|{cnt:3}|{a1:5}|{a2:5}|{a3:5}|{a4:5}|{data:4}|{es:3}|{ai:2}|{AS:5}|")

as2rec = {}
for k,v in enemy_tbl.items():
    AS = v.get('as','')
    if AS == '': continue
    name = v.get('name','')
    as2rec[AS] = as2rec.get(AS,[])
    as2rec[AS].append(f"AS{k:02}: ; {name}")

for k,v in sorted(as2rec.items()):
    print(f"{k}:{v}")

