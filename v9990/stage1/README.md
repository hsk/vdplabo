# v9990/stage1

このステージでは１画面ごと一気に描画する基本的機能のみを実装したサンプルを作ります。

解像度と色数をフレキシブルに変えられるVDPなので巨大に思えるけど、モードを絞って作ることで単純化できるはず。

- [ ] [v9990.py](v9990.py)
    - [ ] [v9990_p1.py](v9990_p1.py)
        - [ ] [v9990_p1sp.py](v9990_p1sp.py)
    - [ ] [v9990_p2.py](v9990_p2.py)
        - [ ] [v9990_p2sp.py](v9990_p2sp.py)
    - [ ] [v9990_b0.py](v9990_b0.py) NTSC 192x212(192x424) PAL 192x290(192x580)
    - [ ] [v9990_b1.py](v9990_b1.py) NTSC 256x212(256x424)
        - [ ] [v9990_bsp.py](v9990_bsp.py)
        - [ ] [v9990_b1bp1.py](v9990_b1bp1.py)
        - [ ] [v9990_b1bp2.py](v9990_b1bp2.py)
        - [ ] [v9990_b1bp4.py](v9990_b1bp4.py)
        - [ ] [v9990_b1bp6.py](v9990_b1bp6.py)
        - [ ] [v9990_b1bd8.py](v9990_b1bd8.py)
        - [ ] [v9990_b1bd16.py](v9990_b1bd16.py)
        - [ ] [v9990_b1byjk.py](v9990_b1byjk.py)
        - [ ] [v9990_b1byjkp.py](v9990_b1byjkp.py)
        - [ ] [v9990_b1byuv.py](v9990_b1byuv.py)
        - [ ] [v9990_b1byuvp.py](v9990_b1byuvp.py)
    - [ ] [v9990_b2.py](v9990_b2.py)
    - [ ] [v9990_b3.py](v9990_b3.py)
    - [ ] [v9990_b4.py](v9990_b4.py)
    - [ ] [v9990_b5.py](v9990_b5.py)
    - [ ] [v9990_b6.py](v9990_b6.py)
    - [ ] [v9990_b7.py](v9990_b7.py)
- [ ] [v9990_cmd.py](v9990_cmd.py)
    - [ ] [v9990_cmd00stop.py](v9990_cmd00stop.py)
    - [ ] [v9990_cmd01lmmc.py](v9990_cmd01lmmc.py)
    - [ ] [v9990_cmd02lmmv.py](v9990_cmd02lmmv.py)
    - [ ] [v9990_cmd03lmcm.py](v9990_cmd03lmcm.py)
    - [ ] [v9990_cmd04lmmm.py](v9990_cmd04lmmm.py)
    - [ ] [v9990_cmd05cmmc.py](v9990_cmd05cmmc.py)
    - [ ] [v9990_cmd07cmmm.py](v9990_cmd07cmmm.py)
    - [ ] [v9990_cmd08bmxl.py](v9990_cmd08bmxl.py)
    - [ ] [v9990_cmd09bmlx.py](v9990_cmd09bmlx.py)
    - [ ] [v9990_cmd10bmll.py](v9990_cmd10bmll.py)
    - [ ] [v9990_cmd11line.py](v9990_cmd11line.py)
    - [ ] [v9990_cmd12search.py](v9990_cmd12search.py)
    - [ ] [v9990_cmd13point.py](v9990_cmd13point.py)
    - [ ] [v9990_cmd14pset.py](v9990_cmd14pset.py)
    - [ ] [v9990_cmd15advance.py](v9990_cmd15advance.py)

ドキュメント

- [ ] [docs/v9990.md](docs/v9990.md)
    - [ ] [docs/v9990_p1sp.md](docs/v9990_p1sp.md)
    - [ ] [docs/v9990_p2sp.md](docs/v9990_p2sp.md)
    - [ ] [docs/v9990_p1.md](docs/v9990_p1.md)
    - [ ] [docs/v9990_p2.md](docs/v9990_p2.md)
    - [ ] [docs/v9990_bsp.md](docs/v9990_bsp.md)
    - [ ] [docs/v9990_b1.md](docs/v9990_b1.md)
        - [ ] [docs/v9990_b1bp1.md](docs/v9990_b1bp1.md)
        - [ ] [docs/v9990_b1bp2.md](docs/v9990_b1bp2.md)
        - [ ] [docs/v9990_b1bp4.md](docs/v9990_b1bp4.md)
        - [ ] [docs/v9990_b1bp6.md](docs/v9990_b1bp6.md)
        - [ ] [docs/v9990_b1bd8.md](docs/v9990_b1bd8.md)
        - [ ] [docs/v9990_b1bd16.md](docs/v9990_b1bd16.md)
        - [ ] [docs/v9990_b1byjk.md](docs/v9990_b1byjk.md)
        - [ ] [docs/v9990_b1byjkp.md](docs/v9990_b1byjkp.md)
        - [ ] [docs/v9990_b1byuv.md](docs/v9990_b1byuv.md)
        - [ ] [docs/v9990_b1byuvp.md](docs/v9990_b1byuvp.md)
    - [ ] [docs/v9990_b2.md](docs/v9990_b2.md)
    - [ ] [docs/v9990_b3.md](docs/v9990_b3.md)
    - [ ] [docs/v9990_b4.md](docs/v9990_b4.md)
    - [ ] [docs/v9990_b5.md](docs/v9990_b5.md)
    - [ ] [docs/v9990_b6.md](docs/v9990_b6.md)
    - [ ] [docs/v9990_b7.md](docs/v9990_b7.md)
- [ ] [docs/v9990_cmd.md](docs/v9990_cmd.md)
    - [ ] [docs/v9990_cmd00stop.md](docs/v9990_cmd00stop.md) 停止
    - [ ] [docs/v9990_cmd01lmmc.md](docs/v9990_cmd01lmmc.md) CPUからVRAM
    - [ ] [docs/v9990_cmd02lmmv.md](docs/v9990_cmd02lmmv.md) VDPからVRAM(FILL RECT)
    - [ ] [docs/v9990_cmd03lmcm.md](docs/v9990_cmd03lmcm.md) VRAMからCPU
    - [ ] [docs/v9990_cmd04lmmm.md](docs/v9990_cmd04lmmm.md) VRAMからVRAM(COPY)
    - [ ] [docs/v9990_cmd05cmmc.md](docs/v9990_cmd05cmmc.md) CPUの文字データはカラー処理され、VRAM
    - [ ] [docs/v9990_cmd07cmmm.md](docs/v9990_cmd07cmmm.md) VRAMの文字データはカラー処理され、VRAM
    - [ ] [docs/v9990_cmd08bmxl.md](docs/v9990_cmd08bmxl.md) VRAM線形アドレスからVRAM RECT
    - [ ] [docs/v9990_cmd09bmlx.md](docs/v9990_cmd09bmlx.md) VRAM RECTからVRAM線形アドレス
    - [ ] [docs/v9990_cmd10bmll.md](docs/v9990_cmd10bmll.md) VRAM線形アドレスからVRAM線形アドレス
    - [ ] [docs/v9990_cmd11line.md](docs/v9990_cmd11line.md) ライン描画
    - [ ] [docs/v9990_cmd12search.md](docs/v9990_cmd12search.md) 検索
    - [ ] [docs/v9990_cmd13point.md](docs/v9990_cmd13point.md) 色取得
    - [ ] [docs/v9990_cmd14pset.md](docs/v9990_cmd14pset.md) 点描画
    - [ ] [docs/v9990_cmd15advance.md](docs/v9990_cmd15advance.md) 描画ポインタ移動
