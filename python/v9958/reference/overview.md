# V9958固有機能(YJK/YAE以外)— openMSX実装

対応: [v9958.md](../stage1/docs/v9958.md)

V9958かどうかの判定は `src/video/VDP.hh` の `hasYJK()`:

```cpp
/** Does this VDP support YJK display?
  * @return True for V9958, false otherwise.
  */
[[nodiscard]] bool hasYJK() const {
    return (version & VM_YJK) != 0;
}
```

```cpp
V9938      = 0,
V9958      = VM_YJK,
```

YJK/YAEの画面モード自体は[screen10.md](screen10.md)〜[screen12.md](screen12.md)を参照。ここではそれ以外にR#25で追加されたV9958固有機能をまとめる。

## 1. 非Graphicモードでのコマンド実行(CMDビット)

V9938ではVDPコマンドはSCREEN5〜8(Graphic4〜7)でしか動作しないが、V9958はR#25のCMDビットが立っていればそれ以外のモード(Text2, Multicolorなど)でもコマンドを実行できる。

`src/video/VDP.hh`:

```cpp
/** Are commands possible in non Graphic modes? (V9958 only)
  * @return True iff CMD bit set.
  */
[[nodiscard]] bool getCmdBit() const {
    return (controlRegs[25] & 0x40) != 0;
}
```

`src/video/VDPCmdEngine.cc` の `updateDisplayMode()` がこれを受けて、内部的な「コマンド実行モード番号」`scrMode` を決定する:

```cpp
void VDPCmdEngine::updateDisplayMode(DisplayMode mode, bool cmdBit, EmuTime time)
{
    int newScrMode = [&] {
        switch (mode.getBase()) {
        case DisplayMode::GRAPHIC4:
            return 0;
        case DisplayMode::GRAPHIC5:
            return 1;
        case DisplayMode::GRAPHIC6:
            return 2;
        case DisplayMode::GRAPHIC7:
            return 3;
        default:
            if (cmdBit) {
                return 4; // like GRAPHIC7, but non-planar
                          // TODO timing might be different
            } else {
                return -1; // no commands
            }
        }
    }();
    ...
```

Graphic4〜7以外のモードのとき、CMDビットが立っていれば「Graphic7相当だが非planar」というscrMode=4に、立っていなければ`-1`(コマンド不可)になる。`executeCommand()`側にはこの前提を示すコメントがある:

```cpp
void VDPCmdEngine::executeCommand(EmuTime time)
{
    // V9938 ops only work in SCREEN 5-8.
    // V9958 ops work in non SCREEN 5-8 when CMD bit is set
    if (scrMode < 0) {
        commandDone(time);
        return;
    }
```

呼び出し元は `src/video/VDP.cc` の `execSetMode()`:

```cpp
void VDP::execSetMode(EmuTime time)
{
    updateDisplayMode(
        DisplayMode(controlRegs[0], controlRegs[1], controlRegs[25]),
        getCmdBit(),
        time);
}
```

## 2. ボーダーマスク(MSKビット)

R#25のbit1。有効にすると左ボーダーを8ピクセル分拡張する。

`src/video/VDP.hh`:

```cpp
/** Gets the current border mask setting.
  * Border mask extends the left border by 8 pixels if enabled.
  * This is a V9958 feature, on older VDPs it always returns false.
  * @return true iff enabled.
  */
[[nodiscard]] bool isBorderMasked() const {
    return (controlRegs[25] & 0x02) != 0;
}
```

使用箇所は `src/video/PixelRenderer.cc`:

```cpp
int borderL = vdp.getLeftBorder();
int displayL =
    vdp.isBorderMasked() ? borderL : vdp.getLeftBackground();
```

## 3. YJKモード時の水平位置調整(+4ドット)

R#25のbit3(YJKビットそのもの)が立っていると、水平調整量(R#18由来)に+4される。`src/video/VDP.cc` `execHorAdjust()`:

```cpp
void VDP::execHorAdjust(EmuTime time)
{
    int newHorAdjust = (controlRegs[18] & 0x0F) ^ 0x07;
    if (controlRegs[25] & 0x08) {
        newHorAdjust += 4;
    }
    renderer->updateHorizontalAdjust(newHorAdjust, time);
    horizontalAdjust = newHorAdjust;
}
```

YJK系モードは4ピクセル単位でJ/Kを共有するデコード([screen12.md](screen12.md)参照)のため、表示位置の基準がGraphic7などと4ドットずれる、という調整と考えられる。

## 4. 描画側でのYJKパレット事前計算

`src/video/SDLRasterizer.cc` では、MSX1でもYJKでもない通常パレットとは別に、`hasYJK()`がtrueの場合だけV9958用のYJK→RGB変換済みパレット(`V9958_COLORS`)を事前計算している:

```cpp
} else {
    if (vdp.hasYJK()) {
        // Precalculate palette for V9958 colors.
        if (renderSettings.isColorMatrixIdentity()) {
            ...
            for (auto [rgb, col] : enumerate(V9958_COLORS)) {
                col = screen.mapRGB255(ivec3(
                    intensity[(rgb >> 10) & 31],
                    intensity[(rgb >>  5) & 31],
                    intensity[(rgb >>  0) & 31]));
```

`V9958_COLORS`は32768通り(15bit RGB)のYJK由来カラーテーブルで、[screen12.md](screen12.md)の`palette32768`参照先にあたる(テーブル本体は別途生成されている定数)。
