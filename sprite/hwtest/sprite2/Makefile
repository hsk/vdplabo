TARGETs = sc5_hra sc5_sp01 sc5_sp02 sc5_sp03 sc5_sp03_2 \
          sc5_sp04 sc5_sp05 sc5_sp06 sc5_sp07

all: $(TARGETs)

sc%:
	java -jar ../glass-0.6.jar $@.asm rom/$@.rom
#	../../../../../msxemu/msx2_sdl/app rom/$@.rom
	openmsx -carta rom/$@.rom
clean:
	rm -rf rom/*.rom
