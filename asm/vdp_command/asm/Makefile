all: sp01

sc%:
	java -jar glass-0.6.jar $@.asm rom/$@.rom
#	../../../../../msxemu/msx2_sdl/app rom/$@.rom
	openmsx -carta rom/$@.rom
clean:
	rm -rf rom/*.rom
t%:
	java -jar glass-0.6.jar sc$*.asm rom/sc$*.rom
	 rom/sc$*.rom
