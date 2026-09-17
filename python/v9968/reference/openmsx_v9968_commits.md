# openMSX V9968 差分コミット一覧

[buppu3/openMSX](https://github.com/buppu3/openMSX) の `v9968` ブランチに、本家 [openMSX/openMSX](https://github.com/openMSX/openMSX) からフォークした `master` ブランチ相当のベースコミットからの差分として積まれているコミット一覧(古い順、全47コミット)。

- base (`master`, フォーク元との分岐点): `9aab65445144dacf7488afa080bba8eeed2a9233`
- head (`v9968`): `4bc4b2ef86923635744f02f6beea0a236ba2f310`
- 取得日: 2026-09-17
- 差分パッチ本体: [openmsx_v9968.diff](openmsx_v9968.diff)

## コミット一覧

- e71f10e21 Add EPAL feature
- d4d55c685 Add S16,SVNS,ILNS feature
- 7a774eab4 Add P#4
- d4aae6cf7 Add SP3 feature
- fe550e593 Add SPS feature
- 9b706fdbd Fix the issue with the number of sprites in SP3
- be0fbb58e Fix the function to hide all sprites at once in SPS mode
- e1a6ba04d Modify VDP clock resolution to quadruple
- 7d4f1cca4 Add HS feature
- 1ef600788 Add ToDo.txt
- d93b1e033 Add FID feature
- cee1e7d55 Modify the memory access slot
- b95f54746 Add LRMM, LFMM, XHR, FG4 features
- 4e888fd74 Fix the operation of VRAM interleaving (Planar) and legacy extended VRAM
- 706274b15 Modify the access speed in HS mode
- df72108f5 Add new registers to ImGuiVdpRegs
- 79713744b Fix the effect of the value of the SZ bit in the sprite attribute
- c8b4fd003 Add FIL feature
- 2c57181ac Fix SpriteMode2 display issues in Planar mode
- 469bfe21d Add V9968 machine definition file
- cd3fda832 Update ToDo.txt
- 25ccc1626 Modify ImGuiSprite to support SP3
- 879db8f3c Fix for inability to change palette
- ba791463e Modify according to the LRMM operation correction of the original chip
- a9208263a Modify the timing of the access slot
- 06b97f1aa Add configuration for V9968 cartridge
- a5bc1ef8e Fix the EPAL issue
- 44bafa8ee Update README
- bc46e92b0 Fix the V9968 issue occurring on "DEVCON.COM"
- 7e0739b81 update README
- 4e057bfb1 update README
- 7e181b45f Modify ToDo.txt with new VRAM timing tasks
- 9e156c835 Fix write cache flush processing for LMMS, HMMS, LFMM, and LRMM
- fefdff88c 202512190716
- 0d98bbd8d Fix for cache flush when aborting VDP commands
- 31b10546b Merge branch 'v9968' of https://github.com/buppu3/openMSX into v9968
- 891069a55 update ToDo
- 822da9fbb Modify the VRAM refresh timing for V9968
- 6a4259916 Modify the bit width of the VDP command register
- ecd752ed5 Update ToDo
- 281374da8 Fix the “5th sprite” processing in Mode 3
- 2b4e105a1 Add collision check in SP3 mode (not yet tested)
- 7f5f1182d Fix the VRAM address mask used in P#0 during non-EVR mode
- 873df9d23 Fix the extended parameter register mask for VDP commands
- d884c4b29 Add the FORCE_HS flag to advanced settings
- fd90ed560 Merge branch 'master' into v9968
- 4bc4b2ef8 Fix the reset value for the color palette