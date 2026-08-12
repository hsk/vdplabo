org 08000h

bank_message:
    ld hl,msg
    ret

msg:
    db "BANK3",0

    ds 08000h - $, 0
