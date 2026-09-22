TARGETs = sc1_sp01 sc1_sp02 sc1_sp03 sc1_sp04 sc1_sp05 sc1_sp06 sc1_sp07 sc1_sp08 \
		  sc4_sp01 sc4_sp02 \
          sc5_sp01 sc5_sp02 sc5_sp03 sc5_sp03_2 sc5_sp04 sc5_sp05 sc5_sp06 sc5_sp07 \
          sc7_sp01

all: $(TARGETs)

#sc1_%:
#	z88dk-z80asm -b $@.asm -orom/$@.rom
#	rm -rf *.o

# パレット実測用の診断ROM。実行はせずビルドのみ(実行はprobe_palette.pyから)。
probe_palette:
	z88dk-z80asm -b probe_palette.asm -orom/probe_palette.rom
	rm -rf *.o

# ビルド+実測+PALETTE定数の出力まで1コマンドで行う。
probe-palette: probe_palette
	python3 probe_palette.py rom/probe_palette.rom

sc%:
	echo "ビルド中: $@"
	java -jar glass-0.6.jar $@.asm rom/$@.rom
#	../../../../../msxemu/msx2_sdl/app rom/$@.rom
run_%:
	make $*
	openmsx -carta rom/$*.rom

show-path:
	openmsx -command "puts \"=== 録画データの保存先 ===\"; puts [file join $$env(OPENMSX_USER_DATA) \"captures\"]; quit"

# SETTLE/DURATIONはフレーム数(--settle-frames/--duration-frames)で指定する。
# 秒指定だと期待値のフレーム数にちょうど合わせるのに半端な小数(例: 139/60秒)
# が必要になり扱いにくいため。
# - SETTLE: 周期的なアニメーションのROM(sc1_sp05など)は、デフォルトの
#   settle(0.2秒=12フレーム)だと録画開始がROM側のフレーム周期の境界と
#   噛み合わず、期待値と1フレーム単位の半端なズレが出ることがある。
#   境界に合う値を実測して各テストファイル側(start_cなど)と揃えて使う
#   (../python/sc1_sp05.py参照)。
# - DURATION: デフォルトの録画時間(2秒=120フレーム)より長いexpected
#   (sc1_sp06など、起動直後に長い静止区間がありFRAME_COUNTが120を超える
#   ROM)を録る時に使う。expected側(../python/<ROM>.py)のフレーム数以上を
#   指定すること。
cap_% capture_%:
	make $*
	python3 capture_openmsx.py rom/$*.rom -o ../expected/$*_openmsx.webm $(if $(SETTLE),--settle-frames $(SETTLE),) $(if $(DURATION),--duration-frames $(DURATION),)

test_%:
	python3 compare_webm.py ../expected/$*.webm ../expected/$*_openmsx.webm

captest_%:
	make $*
	python3 capture_openmsx.py rom/$*.rom -o ../expected/$*_openmsx.webm $(if $(SETTLE),--settle-frames $(SETTLE),) $(if $(DURATION),--duration-frames $(DURATION),)
	python3 compare_webm.py ../expected/$*.webm ../expected/$*_openmsx.webm

# sc1_sp05はWAIT_FRAMES=5周期の境界に合わせるため、settleを10フレームに
# 固定してキャプチャする(実測値。理由は上のコメントと../python/sc1_sp05.py
# のstart_cコメント参照)。ターゲット固有変数として指定するだけで、
# レシピ自体は上のcap_test_%パターンがそのまま使われる。
captest_sc1_sp05 capture_sc1_sp05: SETTLE = 10

# sc1_sp06はLEAD_IN_FRAMES(wait_1sec相当)込みでexpectedが139フレーム
# (../python/sc1_sp06.pyのFRAME_COUNT)あるため、デフォルトの2秒(120フレーム)
# では足りない。compare_webm.pyはフレーム数の厳密一致を要求するので、
# ちょうど139フレームを指定する。
captest_sc1_sp06 capture_sc1_sp06: DURATION = 139

# sc4(SCREEN4/192ライン)はsc5(SCREEN5/212ライン)とVBLANKタイミングが異なるため、
# ROM側の5フレーム周期境界に噛み合うSETTLE値も違う(実測: sc5=13, sc4=15)。
captest_sc4_sp01 capture_sc4_sp01 cap_sc4_sp01: SETTLE = 15
captest_sc4_sp02 capture_sc4_sp02 cap_sc4_sp02: SETTLE = 15

captest_sc5_sp01 capture_sc5_sp01 cap_sc5_sp01: SETTLE = 15
captest_sc5_sp02 capture_sc5_sp02 cap_sc5_sp02: SETTLE = 15
captest_sc5_sp06 capture_sc5_sp06 cap_sc5_sp06: DURATION = 200
captest_sc5_sp07 capture_sc5_sp07 cap_sc5_sp07: DURATION = 256

captest_sc7_sp01 capture_sc7_sp01: SETTLE = 40


# 全ROMをビルドし直してopenMSXキャプチャ(../expected/*_openmsx.webm)を
# 撮り直す(capture_%を全ターゲット分まわすだけ。SETTLE/DURATIONの
# ターゲット固有変数は$(MAKE)の再帰呼び出しでもそのまま効く)。
# 古いスケール(4倍=1280x960など)で撮られたままのファイルを
# 現在のデフォルト(openMSXの-doublesize, 640x480)に揃えたい時に使う。
recapture-all:
	@for t in $(TARGETs); do $(MAKE) capture_$$t; done

clean:
	rm -rf rom/*.rom
