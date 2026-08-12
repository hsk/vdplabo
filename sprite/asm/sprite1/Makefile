$TARGETs = sc1_sp01 sc1_sp02 sc1_sp03 sc1_sp04 \
           sc1_sp05 sc1_sp06 sc1_sp07 sc1_sp08
all: $(TARGETs)

sc%:
#	java -jar glass-0.6.jar $@.asm rom/$@.rom
	z88dk-z80asm -b $@.asm -orom/$@.rom
	rm -rf *.o
#	../../../../../msxemu/msx2_sdl/app rom/$@.rom
	openmsx -carta rom/$@.rom
clean:
	rm -rf rom/*.rom
