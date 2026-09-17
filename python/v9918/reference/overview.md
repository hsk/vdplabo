# VDPバージョン判定とMSX1固定パレット

出典: `src/video/VDP.hh`, `src/video/VDP.cc`, `src/video/DisplayMode.hh`

## チップ種別の表現

openMSXは1つの`VDP`クラスで TMS9918A〜V9958 まで(このfork独自のV9968も含め)全チップを扱う。チップ種別はビットフラグの組み合わせで表現され、`isMSX1VDP()`が true になるものが「V9918系」。

`src/video/VDP.hh` (771-819行目付近):

```cpp
static constexpr unsigned VM_MSX1             =   1; // set-> MSX1,       unset-> MSX2 or MSX2+
// ...
static constexpr unsigned VM_YJK              =  64; // set-> has YJK (MSX2+)

enum VDPVersion : unsigned {
	TMS99X8A   = VM_MSX1 | VM_PALCOL_MIRRORING | VM_VRAM_REMAPPING,
	// ...
	TMS9929A   = VM_MSX1 | VM_PALCOL_MIRRORING | VM_VRAM_REMAPPING | VM_PAL,
	TMS9129    = VM_MSX1 | VM_PAL,
	TMS91X8    = VM_MSX1,
	T6950PAL   = VM_MSX1 | VM_TOSHIBA_PALETTE | VM_NO_MIRRORING | VM_PAL,
	T6950NTSC  = VM_MSX1 | VM_TOSHIBA_PALETTE | VM_NO_MIRRORING,
	T7937APAL  = VM_MSX1 | VM_TOSHIBA_PALETTE | VM_PAL,
	T7937ANTSC = VM_MSX1 | VM_TOSHIBA_PALETTE,
	YM2220PAL  = VM_MSX1 | VM_YM2220_PALETTE | VM_PALCOL_MIRRORING | VM_PAL,
	YM2220NTSC = VM_MSX1 | VM_YM2220_PALETTE | VM_PALCOL_MIRRORING,
	V9938      = 0,
	V9958      = VM_YJK,
};
```

判定関数:

```cpp
[[nodiscard]] bool isMSX1VDP() const {
	return (version & VM_MSX1) != 0;
}
```

MSX1系だけでもTMS9918A(北米向け/NTSC)、TMS9929A(PAL)、TMS9129、東芝T6950/T7937A、YM2220 など複数の実チップ・互換チップがあり、パレット生成方式が異なる(下記)。

## MSX1固定パレット

MSX1系VDPはV9938以降と違いパレットレジスタを持たず、チップに焼き込まれた固定16色パレットを使う。openMSXは `getMSX1Palette()` でチップ種別ごとに異なる固定パレット(またはアナログ出力からの変換式)を返す。

`src/video/VDP.cc` (1553行目〜):

```cpp
std::array<std::array<uint8_t, 3>, 16> VDP::getMSX1Palette() const
{
	assert(isMSX1VDP());
	if (MSXDevice::getDeviceConfig().findChild("rgboutput3bit") != nullptr) {
		return THREE_BIT_RGB_PALETTE;
	}
	if ((version & VM_TOSHIBA_PALETTE) != 0) {
		return TOSHIBA_PALETTE;
	}
	if ((version & VM_YM2220_PALETTE) != 0) {
		return YM2220_PALETTE;
	}
	std::array<std::array<uint8_t, 3>, 16> tmsPalette;
	for (auto color : xrange(16)) {
		// convert from analog output to YPbPr
		float Y  = TMS9XXXA_ANALOG_OUTPUT[color][0];
		float Pr = TMS9XXXA_ANALOG_OUTPUT[color][1] - 0.5f;
		float Pb = TMS9XXXA_ANALOG_OUTPUT[color][2] - 0.5f;
		// apply the saturation
		Pr *= (narrow<float>(saturationPr) * (1.0f / 100.0f));
		Pb *= (narrow<float>(saturationPb) * (1.0f / 100.0f));
		// convert to RGB as follows:
		//   |R|   | 1  0      1.402 |   |Y |
		//   |G| = | 1 -0.344 -0.714 | x |Pb|
		//   |B|   | 1  1.722  0     |   |Pr|
		// ...(YPbPr -> RGB変換が続く)
	}
	return tmsPalette;
}
```

TMS9918A/9928A系は本来アナログ出力チップなので、`v9918.py`のように「固定パレット」として扱ってよい一方、実機系統(素のTMS/PAL用TMS9929A/東芝製/YM2220製)によって微妙に色味が違うことがここから読み取れる。このプロジェクトのpythonリファレンス実装が「パレットは固定」としているのは、この中の1系統(標準的なTMS9XXXA_ANALOG_OUTPUT変換)に相当する。

## 表示モードとスプライトモードの対応

`src/video/DisplayMode.hh` — MSX1で使えるベースモードは `GRAPHIC1`(0x00) / `TEXT1`(0x01) / `MULTICOLOR`(0x02) / `GRAPHIC2`(0x04) の4つ(`mode & 0x18 == 0`、つまり `isV9938Mode()` が false のもの)。

```cpp
[[nodiscard]] constexpr int getSpriteMode(bool isMSX1) const {
	switch (getBase()) {
	case GRAPHIC1: case MULTICOLOR: case GRAPHIC2:
		return 1;
	case MULTIQ: // depends on VDP type
		return isMSX1 ? 1 : 0;
	case GRAPHIC3: case GRAPHIC4: case GRAPHIC5:
	case GRAPHIC6: case GRAPHIC7:
		return 2;
	case TEXT1: case TEXT1Q: case TEXT2:
	default:
		return 0;
	}
}
```

Graphics1/2/マルチカラーは「スプライトモード1」、Text1はスプライト無し、という対応がここで決まる。呼び出し側は `getSpriteMode(vdp.isMSX1VDP())` の形で常にチップ種別を渡している(`SpriteChecker.hh` 283行目)。
