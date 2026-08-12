org 08000h

bank_message:
    ld hl,msg
    ret

msg:
    db "BANK2",0

    ds 08000h - $, 0
