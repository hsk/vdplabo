all: stg01.asm stg02.asm stg03.asm f

stg01.asm 1:
	python rescomp.py stg01.png 8 > stg01.asm
stg02.asm 2:
	python rescomp.py stg02.png 8 > stg02.asm
stg03.asm 3:
	python rescomp.py stg03.png 8 > stg03.asm
f:
	python resfield.py > field.asm

clean:
	rm stg*.asm
