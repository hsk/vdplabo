org 08000h

bank_message:
    ld hl,msg
    ret
msg:
    db "BANK1",0

    ds 04000h - $, 0
