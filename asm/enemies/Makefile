en%:
	java -jar glass-0.6.jar $@.asm rom/$@.rom
#	z80asm -i $@.asm -o rom/$@.rom

#	../../../../../msxemu/msx2_sdl/app rom/$@.rom
	openmsx -carta rom/$@.rom
clean:
	rm -rf rom/*.rom
t%:
	java -jar glass-0.6.jar sc$*.asm rom/sc$*.rom
	 rom/sc$*.rom

sp:
#	java -jar glass-0.6.jar spj_index.asm -L spj.lst rom/spj.rom
	z80asm spj_index.asm -L -orom/spj.rom 2> spj.txt
