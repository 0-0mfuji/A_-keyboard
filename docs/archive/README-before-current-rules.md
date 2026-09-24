# 旧仕様・進捗の履歴（現行設計には適用しない）

現行ルールはルートの README.md、実装状況は hardware/README.md を参照。以下は更新前の記録です。技術値も再検証してから利用してください。


# A_-Keyboard

**Custom Wireless Split Keyboard with Integrated Trackball**

A_-Keyboardは、左右分割型のワイヤレスメカニカルキーボードにPMW3610ベースのトラックボールを統合する完全自作キーボードプロジェクトです。

本設計では以下を主要方針とします。

* Seeed Studio XIAO nRF52840 Plus
* ZMK Firmware
* BLE Split
* PMW3610DM-SUDU Trackball
* Cherry MX compatible switches
* Kailh Hot-Swap sockets
* 1S LiPo battery
* 左右共通Main PCB
* Trackball専用Sub-PCB
* JLCPCB / JLCPCB PCBAを意識した部品構成

> **Hardware Revision:** Rev.A
> **Status:** Hardware design specification / Prototype
> **EDA:** KiCad
> **Firmware:** ZMK

---

# 1. Design Goals

A_-Keyboard Rev.Aの設計目標は以下です。

1. 完全ワイヤレスSplit Keyboard
2. 左右それぞれにXIAO nRF52840 Plusを搭載
3. ZMK BLE Splitを使用
4. 片側最大30キーの5×6キーマトリクス
5. Cherry MX / Kailh Hot-Swap対応
6. PMW3610トラックボール対応
7. Trackball Sensor PCBをMain PCBから分離
8. 300～500mAhの1セルLiPoバッテリー対応
9. USB Type-Cによる充電
10. 同じMain PCBデータを左右で使用
11. Trackballを左右どちらにも搭載可能な設計
12. JLCPCBで製造可能
13. 将来的なケース・ボール位置変更に追従しやすい構成
14. Rev.AではRGB LEDを実装せず、消費電力と設計リスクを抑える

---

# 2. System Architecture

```text
                        Host PC / Mac / Tablet
                                │
                         BLE HID / USB
                                │
                     ┌──────────────────┐
                     │ ZMK Central Side │
                     │ XIAO nRF52840+   │
                     └────────┬─────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
        Key Matrix       PMW3610          LiPo Battery
        5 Rows × 6 Cols  Trackball         300-500mAh
                             │
                       Trackball Sub-PCB

                              ↑
                       BLE Split Link
                              ↓

                     ┌──────────────────┐
                     │ZMK Peripheral    │
                     │XIAO nRF52840+    │
                     └────────┬─────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                Key Matrix          LiPo Battery
                5 Rows × 6 Cols     300-500mAh
```

Rev.Aでは、**Trackballを搭載している側を原則ZMK Central**とします。

ZMK自体はsplit peripheral側のpointing deviceも`zmk,input-split`を使って扱えますが、Rev.Aではファームウェア・BLE通信・デバッグを単純化するため、Trackball側をCentralとします。 ([ZMK Firmware][1])

---

# 3. Board Architecture

本プロジェクトは2種類のPCBで構成します。

```text
A_-Keyboard
│
├── Main PCB
│   ├── XIAO nRF52840 Plus
│   ├── 5 × 6 Key Matrix
│   ├── Kailh Hot-Swap
│   ├── 1N4148W
│   ├── Battery Connector
│   ├── Power Switch
│   ├── Reset Switch
│   └── Trackball FFC Connector
│
└── Trackball PCB
    ├── PMW3610DM-SUDU
    ├── LM18-LSI
    ├── TLV74318 1.8V LDO
    ├── Decoupling / Charge Pump Components
    └── FFC Connector
```

Main PCBは左右共通Gerberを目標とします。

ただし、

> 「左右で同じPCBを使う」

ことと、

> 「すべての部品を完全に同じ面へ実装する」

ことは分けて考えます。

Rev.Aでは**Left Population / Right Population**を許容します。

---

# 4. MCU

## 4.1 Controller

| Parameter     | Specification                   |
| ------------- | ------------------------------- |
| Module        | Seeed Studio XIAO nRF52840 Plus |
| MCU           | Nordic nRF52840                 |
| Wireless      | Bluetooth Low Energy            |
| Logic Voltage | 3.3V                            |
| USB           | USB Type-C                      |
| Battery       | 1S LiPo                         |
| Firmware      | ZMK                             |
| Qty           | 1 per half                      |

XIAO nRF52840 PlusにはD0～D19が公開され、D17/D18/D19にはSPI用の追加ピンが割り当てられています。Rev.Aではこの追加GPIOをPMW3610用として使用します。 ([Seeed Studio Wiki][2])

日本向けにはXIAO nRF52840 Plus / Sense Plusについて工事設計認証番号 **222-257139** が発行されています。実製品では認証済みモジュールのRF部分・アンテナ条件を変更しないことを前提とします。 ([Seeed Studio Files][3])

---

# 5. GPIO Assignment — Rev.A

Rev.Aでは以下を**基準ピンアサイン**とします。

## 5.1 Pin Assignment

| XIAO | nRF52840 | Net                  | Function                   |
| ---- | -------- | -------------------- | -------------------------- |
| D0   | P0.02    | ROW0                 | Keyboard Row 0             |
| D1   | P0.03    | ROW1                 | Keyboard Row 1             |
| D2   | P0.28    | ROW2                 | Keyboard Row 2             |
| D3   | P0.29    | ROW3                 | Keyboard Row 3             |
| D4   | P0.04    | ROW4                 | Keyboard Row 4             |
| D5   | P0.05    | COL0                 | Keyboard Column 0          |
| D6   | P1.11    | COL1                 | Keyboard Column 1          |
| D7   | P1.12    | COL2                 | Keyboard Column 2          |
| D8   | P1.13    | COL3                 | Keyboard Column 3          |
| D9   | P1.14    | COL4                 | Keyboard Column 4          |
| D10  | P1.15    | COL5                 | Keyboard Column 5          |
| D11  | P0.15    | TB_RESET             | PMW3610 nRESET             |
| D12  | P0.19    | TB_CS                | PMW3610 nCS                |
| D13  | P1.01    | TB_MOTION            | PMW3610 MOTION             |
| D14  | P0.09    | RESERVED             | NFC1 / Future              |
| D15  | P0.10    | RESERVED             | NFC2 / Future              |
| D16  | P0.31    | BAT_SENSE / RESERVED | Battery ADC                |
| D17  | P1.03    | TB_SCLK              | PMW3610 SCLK               |
| D18  | P1.05    | RESERVED             | SPI MISO / Future          |
| D19  | P1.07    | TB_SDIO              | PMW3610 bidirectional SDIO |

D14/D15はNFC兼用ピンなので、Rev.Aでは使用しません。

D18も3-wire SPIでは不要なため予約します。

これにより、

```text
Matrix       = 11 GPIO
Trackball    = 5 GPIO
Reserved     = 4 GPIO
```

となります。

---

# 6. KiCad Schematic Hierarchy

KiCadプロジェクトは以下のように分けることを推奨します。

```text
hardware/
├── main/
│   ├── a_-keyboard-main.kicad_pro
│   ├── a_-keyboard-main.kicad_sch
│   ├── a_-keyboard-main.kicad_pcb
│   │
│   └── sheets/
│       ├── power.kicad_sch
│       ├── mcu.kicad_sch
│       ├── matrix.kicad_sch
│       └── trackball_interface.kicad_sch
│
└── trackball/
    ├── a_-keyboard-trackball.kicad_pro
    ├── a_-keyboard-trackball.kicad_sch
    └── a_-keyboard-trackball.kicad_pcb
```

推奨回路図Sheet構成：

```text
Root
├── MCU
├── Power
├── Keyboard Matrix
└── Trackball Interface
```

Trackball Sub-PCBは別KiCad Projectにします。

---

# 7. Power Architecture

## 7.1 Main Board Power

```text
Protected 1S LiPo
      │
      │ BAT+
      ▼
J_BAT
      │
      ▼
SW_PWR
      │
      ▼
XIAO BAT+
      │
      ├── XIAO internal power circuit
      │
      └── USB-C charging
```

GNDは共通とします。

## 7.2 Battery Specification

| Parameter       | Specification                     |
| --------------- | --------------------------------- |
| Chemistry       | LiPo / Li-Ion                     |
| Cells           | 1S                                |
| Nominal Voltage | 3.7V                              |
| Capacity        | 300–500mAh                        |
| Protection      | **Protected battery recommended** |
| Connector       | JST-PH 2.0 or equivalent          |
| Qty             | 1 per side                        |

**注意:** JST系LiPoは製品によってコネクタ極性が異なる場合があるため、PCBシルクに必ず

```text
BAT+
BAT-
```

を明示します。

コネクタの「1番ピンだから+」という前提にはしません。

---

# 8. Power Switch

左右それぞれに物理電源スイッチを設けます。

```text
J_BAT BAT+
    │
    └── SW_PWR ─── XIAO BAT+
```

推奨：

* SPST Slide Switch
* Rated current > 500mA
* 小型SMDまたはTHT

Rev.Aでは単純なBattery Disconnect方式とします。

そのため、

**SW_PWR = OFFの場合、USB接続時にXIAOは起動できますが、切り離されたバッテリーは充電されません。**

「電源OFFでもバッテリー充電可能」にしたい場合はRev.BでMOSFET Load Switch方式を検討します。

---

# 9. Reset Switch

XIAOのReset端子に外部タクトスイッチを設けます。

```text
XIAO RESET
    │
    ├──── SW_RESET ─── GND
    │
    └──── TP_RESET
```

部品：

```text
SW_RESET : Momentary Normally Open
```

Reset端子は通常時Openとします。

---

# 10. Keyboard Matrix

## 10.1 Matrix Size

Rev.Aでは片側最大：

```text
5 Rows × 6 Columns = 30 Keys
```

とします。

```text
        COL0 COL1 COL2 COL3 COL4 COL5
ROW0     K00  K01  K02  K03  K04  K05
ROW1     K10  K11  K12  K13  K14  K15
ROW2     K20  K21  K22  K23  K24  K25
ROW3     K30  K31  K32  K33  K34  K35
ROW4     K40  K41  K42  K43  K44  K45
```

実際のキー数が30未満の場合、不要な交点を配置しません。

---

# 11. Matrix Diode Direction

Rev.Aでは：

```text
COL2ROW
```

とします。

回路：

```text
COLx ─── SWxx ─── Dxx ─── ROWy
                    →
```

より明確には、

```text
COLx
 │
 └── Switch
       │
       └── Diode Anode
              │>| 
                │
                └── Diode Cathode ── ROWy
```

つまり、

```text
Anode   → Column side
Cathode → Row side
```

です。

ZMKでは：

```dts
diode-direction = "col2row";
```

と設定します。

`col2row`ではダイオードのカソードがRow側になります。 ([ZMK Firmware][4])

---

# 12. Matrix Diodes

| Parameter | Specification |
| --------- | ------------- |
| Device    | 1N4148W       |
| Package   | SOD-123       |
| Qty       | One per key   |
| Reference | D1, D2, D3... |

原則としてSMD実装とします。

PCBシルクにはダイオードのカソード側を明確に表示します。

---

# 13. Switch / Hot-Swap Footprint

対応：

* Cherry MX
* MX-compatible switch
* 3-pin
* 5-pin
* Kailh MX Hot-Swap Socket

## Footprint Design

Mechanical footprintには以下を含めます。

```text
MX Switch center hole
MX electrical pins
MX 5-pin stabilizing holes
Kailh Hot-Swap Socket pads
Optional LED mechanical holes
```

ただし、**DiodeをMX Switchと同一のKiCad footprintに統合しません。**

回路図では：

```text
SW1
D1

SW2
D2

SW3
D3
...
```

という独立した部品にします。

PCB Editor上では、

```text
SW1 + D1
SW2 + D2
SW3 + D3
```

をそれぞれGroup化して配置します。

これにより、

* BOM
* RefDes
* JLCPCB PCBA
* Pick & Place
* ERC
* 回路追跡

を正常に維持できます。

---

# 14. Trackball Interface — Main PCB

Trackball PCBとMain PCBの間には8pin FFC/FPCを使用します。

推奨：

```text
8 Pin
0.5 mm Pitch
Bottom/Top Contact type selected according to mechanical design
```

Rev.AではSideraKB PMW3610 breakoutのFFC pinoutとの互換性を意識して以下に固定します。 ([GitHub][5])

## 14.1 J_TB Pinout

| Pin | Net       | Description               |
| --: | --------- | ------------------------- |
|   1 | GND       | Ground                    |
|   2 | +3V3      | Sensor PCB input          |
|   3 | TB_CS     | PMW3610 nCS               |
|   4 | NC        | Reserved                  |
|   5 | TB_SDIO   | Bidirectional serial data |
|   6 | TB_SCLK   | Serial clock              |
|   7 | TB_MOTION | Motion interrupt          |
|   8 | TB_RESET  | Sensor reset              |

Main PCB：

```text
J_TB.1 → GND
J_TB.2 → XIAO +3V3
J_TB.3 → D12 / P0.19
J_TB.4 → NC
J_TB.5 → D19 / P1.07
J_TB.6 → D17 / P1.03
J_TB.7 → D13 / P1.01
J_TB.8 → D11 / P0.15
```

---

# 15. Trackball SPI

PMW3610は通常のMOSI/MISO分離型4-wire SPIではなく、**SDIOを送受信で共有する3-wire synchronous serial interface**を使用します。最大SCLKは2MHzです。 

```text
XIAO                PMW3610

D17 / TB_SCLK ───── SCLK
D19 / TB_SDIO ───── SDIO
D12 / TB_CS   ───── nCS
D13 / MOTION  ◀──── MOTION
D11 / RESET   ───── nRESET
```

Zephyr / ZMK側では、SDIOの物理ピンをSPIM MOSIとMISOの両方として割り当てる方式が既存PMW3610実装で使用されています。 ([GitHub][6])

---

# 16. Trackball Sub-PCB

Trackball PCBは以下の構成とします。

```text
3.3V input
   │
   ├─────────────────────────→ PMW3610 VDDIO
   │
   ▼
TLV74318
   │
   ▼
1.8V
   │
   └─────────────────────────→ PMW3610 VDD
```

つまり：

```text
PMW3610 Core Voltage = 1.8V
PMW3610 IO Voltage   = 3.3V
```

とします。

PMW3610の推奨動作電圧はVDD=1.7～2.1V、VDDIO=1.7～3.3Vです。したがって3.3V GPIOのXIAOと接続するRev.Aでは、**VDD=1.8V / VDDIO=3.3V**とします。 

---

# 17. Trackball Sub-PCB Connector

Sub-PCB側：

| FFC Pin | Net     |
| ------: | ------- |
|       1 | GND     |
|       2 | VIN_3V3 |
|       3 | nCS     |
|       4 | NC      |
|       5 | SDIO    |
|       6 | SCLK    |
|       7 | MOTION  |
|       8 | nRESET  |

Main PCBと**1:1ストレート接続**とします。

FFCコネクタのTop Contact / Bottom Contactの違いにより実際の番号が左右反転しないよう、KiCad footprintのPin 1と実物コネクタの接点方向を必ず確認します。

---

# 18. PMW3610 Pin Definition

KiCad symbolは以下の16pinで作成します。

| Pin | Name    | Type          | Connection        |
| --: | ------- | ------------- | ----------------- |
|   1 | +VCSEL  | Power         | Reference circuit |
|   2 | SDIO    | Bidirectional | TB_SDIO           |
|   3 | SCLK    | Input         | TB_SCLK           |
|   4 | NC      | NC            | No connection     |
|   5 | NCS     | Input         | TB_CS             |
|   6 | VDDIO   | Power         | +3V3              |
|   7 | NRESET  | Input         | TB_RESET          |
|   8 | MOTION  | Output        | TB_MOTION         |
|   9 | VCP     | Power         | Reference circuit |
|  10 | PASS_T  | Power         | Reference circuit |
|  11 | GND     | Power         | GND               |
|  12 | CP      | Power         | Reference circuit |
|  13 | CN      | Power         | Reference circuit |
|  14 | VDD     | Power         | +1V8              |
|  15 | XYLASER | Power         | Reference circuit |
|  16 | -VCSEL  | Power         | Reference circuit |

このpinoutはPixArt PMW3610DM-SUDU datasheetに基づきます。 

---

# 19. PMW3610 Reference Circuit

重要：

PMW3610の、

```text
+VCSEL
-VCSEL
VCP
PASS_T
CP
CN
XYLASER
```

周辺は一般的なデジタルICの電源回路ではありません。

**自己流で簡略化しません。**

Rev.AではPixArt Application CircuitまたはSideraKB Rev.2.xの実績回路をベースとして、そのままKiCadへ転記します。

PixArt自身も推奨application circuitを規定しています。 

---

# 20. PMW3610 Recommended BOM

実装実績のあるSideraKB PMW3610 Rev.2.xをRev.Aの基準とします。 ([GitHub][5])

| Ref  | Value                 | Footprint             |
| ---- | --------------------- | --------------------- |
| U1   | PMW3610DM-SUDU        | 16-pin sensor package |
| U2   | TLV74318              | SOT-23-5              |
| C1   | 3.3µF / 16V           | 0805                  |
| C2   | 100nF                 | 0603                  |
| C3   | 100nF                 | 0603                  |
| C4   | 100nF                 | 0603                  |
| C5   | 10nF                  | 0603                  |
| C6   | 10µF                  | 0805                  |
| C7   | 10nF                  | 0603                  |
| C8   | 1µF                   | 0603                  |
| C9   | 1µF                   | 0603                  |
| C10  | DNI                   | 0603                  |
| R1   | 10kΩ                  | 0603                  |
| J1   | Optional Debug Header | 1×7                   |
| J2   | 8pin FFC              | 0.5mm                 |
| Lens | LM18-LSI              | —                     |

Capacitorsは原則：

```text
X7R
±10%
6.3V or greater
```

を使用します。

---

# 21. PMW3610 Reset

PMW3610のnRESETには内部weak pull-upがありますが、Rev.Aではデバッグ性を高めるため、

```text
nRESET ── 10kΩ ── +3V3
```

の外部pull-upを配置可能にします。

```text
R_RESET = 10kΩ
```

ただしDNI可能とします。

MCUから：

```text
D11 → nRESET
```

を接続します。

---

# 22. Test Points — Trackball PCB

最低限以下をTest Pointとして用意します。

```text
TP_3V3
TP_1V8
TP_GND
TP_SCLK
TP_SDIO
TP_CS
TP_MOTION
TP_RESET
```

特に、

```text
3V3
1V8
GND
```

は必須とします。

---

# 23. Trackball Mechanical Specification

## Ball

```text
Diameter: 34 mm nominal
```

Rev.Aでは34mmを基準とします。

## Bearings

```text
3 × support points
2–3 mm ceramic / metal bearings
```

推奨：

* Ceramic bearing balls
* POM support
* Ball transfer unitsはRev.Aでは使用しない

---

# 24. Optical Height

PMW3610 + LM18-LSIでは、lens reference planeからtracking surfaceまで：

```text
Minimum : 2.2 mm
Typical : 2.4 mm
Maximum : 2.6 mm
```

が推奨されています。 

そのためTrackball Holderは固定寸法一発勝負にせず、

```text
Shim
Spacer
Slot
Replaceable sensor mount
```

のいずれかでZ方向を調整できる構造にします。

Rev.A目標：

```text
Mechanical adjustment capability:
approximately ±0.5 mm or greater
```

PCB位置を直接接着固定しないことを推奨します。

---

# 25. Trackball PCB Mounting

Trackball Sub-PCBはケースへ3～4点で固定します。

設計目標：

```text
PCB
 │
 ├─ Lens
 │
 ├─ PMW3610
 │
 └─ Adjustable Mount
        │
        └─ Keyboard Case
```

Sensor + Lens + PCBの相対位置は固定し、

**ケースに対してSensor PCB全体を上下調整する方式**を優先します。

---

# 26. PMW3610 Assembly Warning

PMW3610は一般的なSMDセンサーではなく、光学系・VCSELを含む特殊部品です。

PixArt datasheetではセンサーpackageについてwave solder processを前提としたassembly recommendationが記載されています。 

したがってRev.Aでは、

```text
JLCPCB PCBA:
LDO + passive components + FFC connector

Manual assembly:
PMW3610 sensor + LM18-LSI
```

を基本方針とします。

PMW3610を通常のSMT reflow対象として扱わないこと。

---

# 27. Reversible Main PCB Strategy

Rev.Aでは、

```text
ONE PCB DESIGN
        ↓
 Left Half / Right Half
```

を目標とします。

ただし以下は左右で実装面を変更できるようにします。

```text
XIAO
Battery Connector
Power Switch
Trackball Connector
Diodes
Hot-Swap Sockets
```

## Important

XIAO nRF52840 PlusではD11～D19を含む追加端子が基板裏側にも存在するため、通常版XIAOの7pin×2だけを想定したfootprintでは不足します。 ([Seeed Studio Wiki][2])

そのため専用：

```text
XIAO_nRF52840_Plus_Reversible
```

footprintを作成します。

---

# 28. XIAO Reversible Footprint Requirements

Custom footprintには：

```text
D0-D10
5V
GND
3V3

D11-D19
BAT
RESET where accessible
```

を含めます。

Rev.Aでは、Front mount / Back mount双方に対応できるよう、

```text
Front-side land pattern
+
Back-side mirrored land pattern
+
via connections where required
```

を検討します。

**XIAO footprintは製造発注前に実寸印刷して、実物モジュールを重ねて確認すること。**

これはRev.Aの必須検証項目です。

---

# 29. Antenna Keep-Out

XIAOのBLE antenna周辺には、

* Battery
* Metal screw
* Trackball bearing
* Ground plane
* Copper pour
* Metal case
* Cable bundle

をできるだけ配置しません。

PCB Layoutではアンテナ正面側をケース外周へ向けます。

Front / Back両面についてRF antenna周辺をKeep-Out Areaとして設定します。

```text
Rule Area:
Copper = Keep Out
Via    = Keep Out
Track  = Keep Out
```

モジュールのアンテナおよびRF回路そのものは変更しません。

---

# 30. PCB Layer Stack

Rev.A Main PCB：

```text
2 Layers

F.Cu
FR-4
B.Cu
```

推奨：

```text
Board thickness : 1.6 mm
Copper           : 1 oz
Surface finish   : Lead-free HASL or ENIG
```

Trackball PCBも基本1.6mm / 2 Layerとします。

機構上必要ならTrackball PCBのみ1.0mmへ変更可能です。

---

# 31. PCB Design Rules

初期KiCadルール：

```text
Minimum Track Width  : 0.20 mm
Minimum Clearance    : 0.20 mm
Via Diameter         : 0.60 mm
Via Drill            : 0.30 mm
```

Trackball boardなど狭い箇所のみ：

```text
Track Width : 0.15 mm
Clearance   : 0.15 mm
```

まで許容します。

---

# 32. Net Classes

KiCad Net Classes：

## Default

```text
Width      : 0.20 mm
Clearance  : 0.20 mm
Via        : 0.60 / 0.30 mm
```

## POWER

対象：

```text
BAT+
+3V3
+1V8
GND
```

推奨：

```text
Width: >= 0.40 mm where practical
```

## TRACKBALL_SPI

対象：

```text
TB_SCLK
TB_SDIO
TB_CS
TB_MOTION
TB_RESET
```

推奨：

```text
Width: 0.20 mm
```

SCLK / SDIOは可能な限り短くします。

---

# 33. Ground Plane

Main PCB：

```text
F.Cu : Signal + partial GND fill
B.Cu : Primarily GND plane
```

を基本とします。

ただしXIAO antenna keep-out内にはGND copperを入れません。

Trackball PCBはSensor周辺のGNDを十分確保しますが、光学用cutout・lens・datasheet指定clearanceを優先します。

---

# 34. Routing Policy

FreeRoutingを使用する場合：

## Auto-route Allowed

```text
ROW0-ROW4
COL0-COL5
```

## Manual Routing Required

```text
BAT+
3V3
1V8

PMW3610 power
PMW3610 charge pump
PMW3610 VCSEL network

TB_SCLK
TB_SDIO
TB_CS

XIAO antenna region
```

PMW3610周辺は原則Auto-routerを使用しません。

---

# 35. Decoupling Placement

すべてのPMW3610 decoupling capacitorは対応pinのできる限り近くに配置します。

原則：

```text
Sensor pin
   │
   ├── Capacitor
   │       │
   │      GND
   │
   └── other routing
```

とし、

```text
Sensor pin → long trace → capacitor
```

の配置を避けます。

LDO input/output capacitorsもU2近傍に配置します。

---

# 36. PCB Test Points — Main Board

最低限：

```text
TP_BAT
TP_3V3
TP_GND

TP_ROW0
TP_COL0

TP_TB_SCLK
TP_TB_SDIO
TP_TB_CS
TP_TB_MOTION
```

を配置します。

可能なら：

```text
TP_D17
TP_D19
TP_RESET
```

も設けます。

---

# 37. PCB Silkscreen

必須表示：

```text
A_-KEYBOARD
REV.A

LEFT / RIGHT orientation
BAT+
BAT-
FFC PIN 1
XIAO USB direction
Power ON/OFF
Diode Cathode
```

左右共通PCBでは特に、

```text
L
R
```

のorientation markerを両面Silkscreenへ入れます。

---

# 38. Trackball Placement Options

左右共通PCBには両側ともTrackball Interfaceを持たせます。

想定：

```text
Left PCB
  Trackball connector available

Right PCB
  Trackball connector available
```

通常は片側だけTrackball PCBを接続します。

将来的には、

```text
Left Trackball
Right Trackball
Dual Trackball
```

への拡張を可能にします。

Rev.AファームウェアではSingle Trackballのみを対象とします。

---

# 39. Firmware Architecture

Firmware：

```text
ZMK
│
├── Left Shield
├── Right Shield
│
├── Shared Matrix DTSI
│
├── XIAO nRF52840 Plus board configuration
│
└── PMW3610 external driver
```

物理pointing deviceを使用するため：

```text
CONFIG_ZMK_POINTING=y
CONFIG_SPI=y
```

を基本とします。

現在のZMKではphysical pointing deviceおよびsplit peripheral側pointing deviceの仕組みが提供されています。 ([ZMK Firmware][1])

---

# 40. Suggested ZMK Matrix Configuration

概念的には：

```dts
kscan0: kscan {
    compatible = "zmk,kscan-gpio-matrix";
    diode-direction = "col2row";

    /* ROW0 - ROW4 */
    row-gpios = <...>;

    /* COL0 - COL5 */
    col-gpios = <...>;
};
```

Rev.A pin mappingとZMK overlayは必ず1:1で管理します。

README、KiCad net名、ZMK net定義で名称を統一します。

例：

```text
ROW0
ROW1
ROW2
ROW3
ROW4

COL0
COL1
COL2
COL3
COL4
COL5
```

---

# 41. Suggested PMW3610 Firmware Mapping

概念：

```text
SCLK   = D17 / P1.03
SDIO   = D19 / P1.07
CS     = D12 / P0.19
MOTION = D13 / P1.01
RESET  = D11 / P0.15
```

PMW3610は3-wire interfaceなので、ZephyrのpinctrlではSDIOをMOSI/MISO双方へ割り当てる構成を使用します。

例：

```dts
psels = <
    NRF_PSEL(SPIM_SCK,  1, 3),
    NRF_PSEL(SPIM_MOSI, 1, 7),
    NRF_PSEL(SPIM_MISO, 1, 7)
>;
```

ただし、**使用するSPIM instance名はXIAO nRF52840 Plus用のZMK/Zephyr board definitionを作成した後に確定するものとし、回路図側では物理GPIO P1.03/P1.07を仕様として固定します。**

これによりZMK側のSoC peripheral instance変更がPCB設計に影響しません。

---

# 42. ZMK / XIAO Plus Validation Requirement

XIAO nRF52840はZMKで広く利用されていますが、Rev.AではPlus追加GPIOも使用するため、PCB発注前に以下をブレッドボードで確認します。

```text
[1] ZMK build for XIAO nRF52840 Plus

[2] D11 output test

[3] D12 output test

[4] D13 interrupt input test

[5] D17 clock output test

[6] D19 bidirectional GPIO / SPI test

[7] PMW3610 Product ID read

[8] PMW3610 motion read

[9] BLE mouse HID

[10] ZMK BLE Split + PMW3610 simultaneously
```

**この10項目が完了するまでMain PCB Rev.Aを量産発注しません。**

---

# 43. Prototype Plan

## Prototype 0 — Electronics

PCBなし。

```text
XIAO nRF52840 Plus
+
PMW3610 Breakout
+
Breadboard / wires
```

Goal：

```text
PMW3610 → ZMK → BLE mouse movement
```

---

## Prototype 1 — Matrix

```text
XIAO Plus
+
small key matrix
```

Goal：

```text
Matrix scanning
BLE split
Battery
Deep sleep
Wake
```

---

## Rev.A PCB

実機用Main PCB + Trackball PCB。

Goal：

```text
Keyboard functionality
Trackball functionality
Power validation
Mechanical validation
```

装飾LEDなし。

---

## Rev.B

Rev.Aの結果を反映。

候補：

```text
RGB LED
Improved reversible footprint
Smaller Trackball PCB
Power optimization
Battery charge while OFF
Dual Trackball
Case optimization
Production PCBA optimization
```

---

# 44. Rev.A Main Board BOM

片側：

| Ref      | Component             |      Qty |
| -------- | --------------------- | -------: |
| U1       | XIAO nRF52840 Plus    |        1 |
| SW1-SW30 | MX-compatible switch  | up to 30 |
| HS1-HS30 | Kailh Hot-Swap socket | up to 30 |
| D1-D30   | 1N4148W               | up to 30 |
| J_BAT    | JST-PH 2.0            |        1 |
| SW_PWR   | SPST slide switch     |        1 |
| SW_RESET | Tactile switch        |        1 |
| J_TB     | 8pin 0.5mm FFC        |        1 |
| BAT1     | Protected 1S LiPo     |        1 |
| TP*      | Test pads             |  several |

---

# 45. Trackball Board BOM

| Ref     | Component         | Qty |
| ------- | ----------------- | --: |
| U1      | PMW3610DM-SUDU    |   1 |
| U2      | TLV74318 1.8V LDO |   1 |
| Lens    | LM18-LSI          |   1 |
| R1      | 10kΩ              |   1 |
| C1      | 3.3µF             |   1 |
| C2-C4   | 100nF             |   3 |
| C5      | 10nF              |   1 |
| C6      | 10µF              |   1 |
| C7      | 10nF              |   1 |
| C8-C9   | 1µF               |   2 |
| C10     | DNI               |   1 |
| J1      | 8pin 0.5mm FFC    |   1 |
| Ball    | 34mm trackball    |   1 |
| Bearing | 2–3mm             |   3 |

---

# 46. KiCad Symbol Naming

推奨：

```text
AKeyboard:Seeed_XIAO_nRF52840_Plus
AKeyboard:PMW3610DM_SUDU
```

標準部品：

```text
Device:D
Device:R
Device:C
Switch:SW_Push
Connector_Generic:Conn_01x08
```

---

# 47. KiCad Footprint Naming

Custom library：

```text
AKeyboard.pretty/
│
├── MX_Hotswap_1U_Reversible.kicad_mod
├── XIAO_nRF52840_Plus_Reversible.kicad_mod
├── PMW3610DM_SUDU.kicad_mod
├── FFC_8P_0.5mm.kicad_mod
└── Trackball_Mount_Reference.kicad_mod
```

---

# 48. Key Footprint Strategy

1キーを「1つの電気部品」にまとめるのではなく、

```text
SW
HotSwap mechanical pads
5-pin holes
LED holes
```

をSwitch footprintに含め、

```text
Diode
```

だけは別部品にします。

KiCad PCB Editor上で：

```text
[ SW1 + D1 ] → Group
[ SW2 + D2 ] → Group
...
```

として扱います。

参考：

* [Salicylic-acid3/KiCAD_FootPrint](https://github.com/Salicylic-acid3/KiCAD_FootPrint)
* [foostan/kbd](https://github.com/foostan/kbd)

---

# 49. Manufacturing

## Main PCB

Target：

```text
JLCPCB
2-layer FR-4
1.6mm
1oz
```

PCBA対象：

```text
1N4148W
passive components
possibly connectors
```

Manual assembly：

```text
XIAO
HotSwap sockets if necessary
Battery
Mechanical switches
```

---

# 50. Trackball PCB Manufacturing

JLCPCB PCBA候補：

```text
TLV74318
Resistors
Capacitors
FFC connector
```

Manual：

```text
PMW3610DM-SUDU
LM18-LSI
```

とします。

Sensorの実装工程を量産前に必ず確認します。

---

# 51. ERC Checklist

KiCad ERC実行前後で：

* [ ] BAT+が3V3に直接接続されていない
* [ ] XIAO BATとLiPoのみ接続
* [ ] Trackball VINは3V3
* [ ] PMW3610 VDDは1V8
* [ ] PMW3610 VDDIOは3V3
* [ ] PMW3610 GND接続
* [ ] PMW3610 NC pinはNC marker
* [ ] Diode polarity確認
* [ ] Matrix ROW/COL shortなし
* [ ] FFC Pin 1 orientation確認
* [ ] RESET pull-up確認
* [ ] Power switch接続確認

---

# 52. PCB DRC Checklist

* [ ] XIAO antenna keep-out
* [ ] Batteryとantennaを離す
* [ ] PMW3610 capacitorをsensor近傍へ
* [ ] LDO capacitorをLDO近傍へ
* [ ] 1V8 traceを短くする
* [ ] SPI traceを短くする
* [ ] FFC pin numbering確認
* [ ] HotSwap socket clearance確認
* [ ] Case screw clearance確認
* [ ] Switch plate clearance確認
* [ ] Trackball mechanical cutout確認
* [ ] XIAO USB-C access確認
* [ ] Battery connector access確認
* [ ] Power switch access確認
* [ ] Reset button access確認

---

# 53. Pre-Fabrication Checklist

Gerber発注前：

* [ ] XIAO Plus実物でfootprint確認
* [ ] MX Switch実物でfootprint確認
* [ ] Kailh socket実物でfootprint確認
* [ ] FFC connector実物でfootprint確認
* [ ] PMW3610実物でfootprint確認
* [ ] LM18-LSI実物でmechanical確認
* [ ] PCBを1:1で紙印刷
* [ ] Key spacing確認
* [ ] Case outline確認
* [ ] USB connector位置確認
* [ ] Trackball位置確認
* [ ] Batteryサイズ確認
* [ ] ZMK Prototype 0成功
* [ ] PMW3610 Product ID取得成功
* [ ] Trackball movement取得成功
* [ ] BLE HID動作成功
* [ ] BLE split動作成功

---

# 54. Bring-Up Procedure

PCB到着後、いきなりバッテリーを接続しません。

## Step 1

電源なしで：

```text
BAT+ ↔ GND resistance
3V3  ↔ GND resistance
1V8  ↔ GND resistance
```

を確認。

---

## Step 2

Trackball PCB単体：

```text
3.3V input
```

を供給。

測定：

```text
VIN = approximately 3.3V
VDDIO = approximately 3.3V
VDD = approximately 1.8V
```

---

## Step 3

XIAOをUSBのみで起動。

確認：

```text
3V3
GPIO
ZMK
USB
```

---

## Step 4

Matrix：

```text
1 key
→
1 row/column
→
all keys
```

の順に確認。

---

## Step 5

PMW3610：

```text
Product ID
→
MOTION interrupt
→
Delta X/Y
→
ZMK HID mouse
```

の順に確認。

---

## Step 6

最後にLiPoを接続。

```text
Battery operation
Charging
Power switch
BLE split
Sleep
Wake
```

を確認します。

---

# 55. Design Risks

Rev.Aで特に注意する項目：

| Risk                               | Priority |
| ---------------------------------- | -------- |
| XIAO Plus追加GPIOのZMK対応              | Critical |
| PMW3610 3-wire SPI                 | Critical |
| PMW3610 1.8V / 3.3V power domains  | Critical |
| XIAO Plus reversible footprint     | High     |
| Trackball optical height           | High     |
| FFC connector orientation          | High     |
| Antenna placement                  | High     |
| LiPo polarity                      | High     |
| Case / PCB mechanical interference | Medium   |
| PCBA availability                  | Medium   |

---

# 56. Rev.A Frozen Decisions

Rev.Aで固定する事項：

```text
MCU
  Seeed Studio XIAO nRF52840 Plus

Firmware
  ZMK

Matrix
  5 × 6 per side
  COL2ROW

Diode
  1N4148W

Switch
  MX Compatible

Socket
  Kailh HotSwap

Trackball Sensor
  PMW3610DM-SUDU

Lens
  LM18-LSI

Ball
  34 mm

Trackball IO
  3-wire SPI

Trackball VDD
  1.8V

Trackball VDDIO
  3.3V

LDO
  TLV74318

Trackball Connector
  8-pin 0.5mm FFC

Battery
  Protected 1S LiPo
  300–500mAh

Main PCB
  2 Layer
  1.6mm

Trackball PCB
  Separate PCB

RGB
  Not populated in Rev.A
```

---

# 57. Items Not Frozen Yet

以下はMechanical Design確定後に決定します。

```text
Exact key layout
Thumb cluster geometry
Trackball left/right position
Trackball tilt angle
Ball bearing diameter
Case thickness
Plate material
FFC cable length
Battery physical dimensions
XIAO physical orientation
Power switch model
FFC connector exact manufacturer
```

これらは回路の基本architectureを変更しません。

---

# 58. Software & Tools

* [KiCad](https://www.kicad.org/) — Schematic / PCB
* [FreeRouting](https://freerouting.org/) — Matrix auto-routing
* [FreeCAD](https://www.freecadweb.org/) — Case / Trackball holder
* [ZMK Firmware](https://zmk.dev/) — Keyboard firmware
* [JLCPCB](https://jlcpcb.com/) — PCB / PCBA
* [Konnect](https://github.com/mixelpixx/Konnect) — XIAO reference library

---

# 59. Reference Designs

## Keyboard Footprints

* [Salicylic-acid3/KiCAD_FootPrint](https://github.com/Salicylic-acid3/KiCAD_FootPrint)
* [foostan/kbd](https://github.com/foostan/kbd)

## PMW3610

Primary design references:

* PixArt PMW3610DM-SUDU Data Sheet
* PixArt PMW3610 Application Circuit
* SideraKB PMW3610 PCB Rev.2.x
* ZMK PMW3610 external driver implementations

PMW3610にはLM18-LSI lensを使用します。PixArtのdatasheetでも同レンズとの使用を前提としています。 

---

# 60. Development Order

A_-Keyboardでは、以下の順番を守ります。

```text
1. GPIO allocation
        ↓
2. XIAO Plus ZMK test
        ↓
3. PMW3610 breadboard test
        ↓
4. Key matrix schematic
        ↓
5. Main schematic
        ↓
6. Trackball schematic
        ↓
7. ERC
        ↓
8. Footprints
        ↓
9. Mechanical layout
        ↓
10. PCB routing
        ↓
11. DRC
        ↓
12. 1:1 paper print
        ↓
13. Gerber
        ↓
14. Prototype manufacturing
        ↓
15. Electrical bring-up
        ↓
16. Mechanical tuning
        ↓
17. Rev.B
```

---

# 61. KiCad Starting Point

この仕様に基づき、最初にKiCadで作成する回路は以下です。

```text
                        XIAO nRF52840 Plus
                    ┌──────────────────────┐

ROW0 ───────────────┤ D0
ROW1 ───────────────┤ D1
ROW2 ───────────────┤ D2
ROW3 ───────────────┤ D3
ROW4 ───────────────┤ D4

COL0 ───────────────┤ D5
COL1 ───────────────┤ D6
COL2 ───────────────┤ D7
COL3 ───────────────┤ D8
COL4 ───────────────┤ D9
COL5 ───────────────┤ D10

TB_RESET ───────────┤ D11
TB_CS ──────────────┤ D12
TB_MOTION ──────────┤ D13

                    │ D14 RESERVED
                    │ D15 RESERVED
                    │ D16 BAT/RESERVED

TB_SCLK ────────────┤ D17
                    │ D18 RESERVED
TB_SDIO ────────────┤ D19

+3V3 ───────────────┤ 3V3
GND ────────────────┤ GND

BAT_SW ─────────────┤ BAT+
                    └──────────────────────┘
```

Trackball interface：

```text
XIAO                           FFC
                              ┌─────┐
GND ──────────────────────────┤ 1
3V3 ──────────────────────────┤ 2
D12 / TB_CS ──────────────────┤ 3
NC ───────────────────────────┤ 4
D19 / TB_SDIO ────────────────┤ 5
D17 / TB_SCLK ────────────────┤ 6
D13 / TB_MOTION ──────────────┤ 7
D11 / TB_RESET ───────────────┤ 8
                              └─────┘
```

Matrix：

```text
COL0 ── SW1 ── D1 ── ROW0
COL1 ── SW2 ── D2 ── ROW0
COL2 ── SW3 ── D3 ── ROW0
...

COL0 ── SW7 ── D7 ── ROW1
...
```

Trackball Power：

```text
                  +3V3
                    │
          ┌─────────┴───────────┐
          │                     │
          │                     ▼
          │                 TLV74318
          │                     │
          │                    1V8
          │                     │
          ▼                     ▼
     PMW3610 VDDIO         PMW3610 VDD
          3.3V                 1.8V
```

この4ブロック、

```text
MCU
Matrix
Power
Trackball Interface
```

からKiCad schematicを開始します。

---

# License

TBD.

Hardware license candidates:

```text
CERN-OHL-P-2.0
```

Firmware:

```text
MIT / Apache-2.0 compatible with included modules
```

External reference designs retain their respective licenses.

---

## A_-Keyboard Rev.A

**Wireless. Split. Mechanical. Trackball. Open Hardware.**

---

この形にしておくと、次にやるべき作業がかなり明確になります。特に重要なのは、README内の**「61. KiCad Starting Point」までが回路図の仕様として固定された**ことです。

次の段階では、文章ではなく実際の設計に落とし込んで、**「KiCadで配置する部品をRefDes単位で全部並べた回路図設計表」**、つまり `U1 / J1 / SW1〜30 / D1〜30 / 各Net名 / 接続先` を作ると、そのままKiCad入力作業に入れます。

[1]: https://zmk.dev/docs/hardware-integration/pointing?utm_source=chatgpt.com "Pointing Devices | ZMK Firmware"
[2]: https://wiki.seeedstudio.com/XIAO_BLE/?utm_source=chatgpt.com "Getting Started with Seeed Studio XIAO nRF52840 Series | Seeed Studio Wiki"
[3]: https://files.seeedstudio.com/Seeed_Certificate/documents_certificate/102010694-TELEC.pdf?utm_source=chatgpt.com "Certificate Number: 222-257139 Rev. No. 01 Date of"
[4]: https://v0-3-branch.zmk.dev/docs/config/kscan?utm_source=chatgpt.com "Keyboard Scan Configuration | ZMK Firmware"
[5]: https://github.com/siderakb/siderakb-website/blob/starlight/main/src/content/docs/mouse-sensors/pmw3610/rev2.md?utm_source=chatgpt.com "siderakb-website/src/content/docs/mouse-sensors/pmw3610/rev2.md at starlight/main · siderakb/siderakb-website · GitHub"
[6]: https://github.com/hidsh/zmk-pmw3610-pcb/blob/master/boards/shields/pmw3610-pcb/pmw3610-pcb.overlay?utm_source=chatgpt.com "zmk-pmw3610-pcb/boards/shields/pmw3610-pcb/pmw3610-pcb.overlay at master · hidsh/zmk-pmw3610-pcb · GitHub"
