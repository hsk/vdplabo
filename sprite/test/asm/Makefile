TARGETs = sc1_sp01 sc1_sp02 sc1_sp03 sc1_sp04 sc1_sp05 sc1_sp06 sc1_sp07 sc1_sp08 \
          sc5_hra sc5_sp01 sc5_sp02 sc5_sp03 sc5_sp03_2 sc5_sp04 sc5_sp05 sc5_sp06 sc5_sp07

all: $(TARGETs)

sc1_%:
	z88dk-z80asm -b $@.asm -orom/$@.rom
	rm -rf *.o
	openmsx -carta rom/$@.rom

sc5_%:
	java -jar glass-0.6.jar $@.asm rom/$@.rom
#	../../../../../msxemu/msx2_sdl/app rom/$@.rom
	openmsx -carta rom/$@.rom

show-path:
	openmsx -command "puts \"=== 録画データの保存先 ===\"; puts [file join $$env(OPENMSX_USER_DATA) \"captures\"]; quit"

# openMSXで実際にROMを実行し、録画結果を ../expected/<ROM>_openmsx.webm に保存する。
# 例: make capture ROM=sc1_sp05 (先に make sc1_sp05 でrom/sc1_sp05.romを作っておくこと)
# ターゲット名を rom名の接頭辞(sc1_/sc5_)に合わせるとsc1_%/sc5_%パターンと
# 衝突してビルドの方が実行されてしまうため、変数指定方式にしている。
capture:
	python3 capture_openmsx.py rom/$(ROM).rom -o ../expected/$(ROM)_openmsx.webm

clean:
	rm -rf rom/*.rom
