# 旧仕様・進捗の履歴（現行設計には適用しない）

現行ルールはルートの README.md、実装状況は hardware/README.md を参照。以下は更新前の記録です。技術値も再検証してから利用してください。

# A-keyboard hardware — 設計作業中

更新: 2026-09-09。**発注用データではありません。PCB配線・機構検証は未完了です。**

## 実PCBへの反映状況（最新）

- KonnectライブAPIで左PCBの外形と66部品の配置を反映・保存済み (`reports/56-left-apply.json`)。
- 右PCBへ回路図を同期し、109部品の初期配置を保存済み (`reports/60-right-sync.json`, `61-right-initial-placement.json`)。
- 左右の丸い外形、共通領域の対称性、1.5Uキーキャップ範囲をEdge.Cuts / Dwgs.Userに反映。
- 直接ソケット＋裏面配線用 `Split:XIAO_DirectSocket_BottomWires` を作成。公式DIP穴位置（列間15.24 mm、ピッチ2.54 mm）を使用し、裏面配線15端子のB面ランドを追加。**接続・穴・部品の干渉検証は未完了**。右PCBに配置済み。左PCBのU1は旧定義のままで更新が必要。
- 右電源部品は基板外の作業領域に仮置き。背面電源スイッチ・USBの最終位置は未実装。XIAO実装高さ・アンテナ領域も未確定。
- DRCは未合格。左507件・右516件（未配線、重なり、警告等の合計）。現在の基板は製造不可。
- 実PCB確認画像: `reports/left-approved-placement.svg`, `right-initial-placement.svg` / `.png`。

以下の過去の進捗記述と異なる場合、この「実PCBへの反映状況」を優先してください。

## 現行仕様への訂正 — 2026-09-09

### 背面アクセスと筐体条件

- XIAOの裏面パッドをMain側へ向け、絶縁配線を基板間に収める。変換基板は追加しない。
- USB-C挿入口を背面へ向ける。XIAOとUSBコネクタの金属シェルは筐体背面から突出させない。
- USB開口はケーブルの金属端子だけでなく樹脂プラグの進入と指での抜き差しを考慮する。奥まり過ぎによる挿入不足を避けるため、実ケーブルの嵌合長とケース壁厚を確認して位置決めする。
- 抜き差しの荷重を受ける筐体支持を設け、ソケットとはんだ付け線に荷重を集中させない。
- 左右の共通キー、背面、内側親指輪郭は鏡像。外側ボール周辺だけ専用形状。
- 前が低く後ろが高い筐体。参考画像の前17 mm・後24 mm・奥行110 mmは目標であり、現在のMX、ホットスワップ、ソケット構成で成立した寸法ではない。
- 最新検討図にこの断面を反映。実PCBのXIAO位置・ソケット寸法・ケース開口は未確定。図は縮尺保証なし。


ユーザー指示により **変換基板を追加しません**。左右のMain PCBにXIAOを直接ソケットで浮かせ、裏面端子は絶縁線でMainへ接続する構成です。`carrier/` は撤回済み案であり製作対象外です。

- 左右回路図からJ4を削除、U1を復元し、SW24をMainへ戻しました。左右ERCはエラー0/警告0。
- U1のソケット／裏面配線接続用フットプリントは未確定・未割当です。旧PCBの直付けU1配置を使わないでください。
- 最新の検討図は `reports/direct-socket-layout-study.png` / `.svg`。旧 `underside-layout-study.*` は撤回済みです。
- 左の長い親指キー2個、右の長い親指キー2個を1.5Uとして描画。左Ctrlは1.25U。画像からの推定寸法であり、実キーキャップとの照合が必要です。
- 右ボール周辺は丸い形に修正。実PCBの外形・部品配置には未反映です。`tools/direct-socket-layout-study.json` は機構検討値です。
- PCB配線、ソケットの干渉確認、裏面配線の着脱方法、電源スイッチの高さは未完了。
- 変更記録: `tools/51-no-carrier.json`, `reports/51-no-carrier.json`。回路図に残る旧SW1/J4注記は、追加した訂正注記により失効しています。

## 撤回済み案の記録（以下は現行仕様ではありません）

左右専用のキー基板と、各側の裏面に着脱するXIAOユニットで構成します。後方のXIAO用張り出しをなくし、USBと電源操作を背面へ向けます。XIAO Plusの裏面端子を含めてユニットへはんだ付けし、ユニットごと取り外します。

- 左: MX 22個＋ロータリーエンコーダーの押下接点。
- 右: MX 20個＋クリックボタン2個＋ロータリーエンコーダーの押下接点。外側の親指側に34 mmボール。
- 4行×6列マトリクス、COL2ROW、23接点/側。
- 各MXキーにSK6805-EC15 RGB LED。左22個、右20個。
- 後部に高さを持たせてユニットを収納。基板間7.47 mmのSamtec FTSH/FLEを候補として設計中。

`reports/underside-layout-study.svg` / `.png` は構造検討図です。キー裏面3.3 mm、XIAO高さ3.5 mm、ユニット基板1.0 mmは仮定値であり、実装保証寸法ではありません。電源スイッチをユニットの下側へ配置する案を示しています。3D干渉、アンテナ、取付ねじ、筐体傾斜は未検証です。

## プロジェクトと反映状況

| プロジェクト | 回路図 | PCB |
|---|---|---|
| `left/a-keyboard-left` | 着脱接続へ更新、RGB含む3ページ | 以前の直付け案112部品。今回の回路図・外形の同期待ち。未配線 |
| `right/a-keyboard-right` | 着脱接続へ更新、RGB含む3ページ | 未配置・未配線 |
| `carrier/a-keyboard-carrier` | 新規作成、XIAO＋30ピン接続＋電源スイッチ | 未配置・未配線 |
| `main/a-keyboard-main` | 旧左右共通案 | 参照用。現行設計ではない |

**今回のERCは左右・ユニットともエラー0/警告0** (`reports/split-left-erc.json`, `split-right-erc.json`, `carrier-erc.json`)。これは接続ルールの検査結果であり、電源・機構・RF性能の検証完了を意味しません。

左右の外形ライブラリ `split.pretty/Left_Outline` / `Right_Outline` は張り出しを除いた形に更新しました。保存済みPCBにはまだ同期していません。`reports/split-layout-study.*` は旧形状のため使わないでください。

## 着脱インターフェース

Main J4 ↔ Carrier J1。1–29番はXIAOフットプリントの端子番号を維持。30番はMainのBAT+からユニットへの入力。ユニットSW1を通った電池電圧が28番BAT_SWでMainのLED電源回路へ戻ります。

| 端子 | 信号 |
|---|---|
| 1–4 | ROW0–ROW3 |
| 5 | ENC_A |
| 6–11 | COL0–COL5 |
| 12 / 13 / 14 | +3V3 / GND / VBUS |
| 15 / 16 / 17 | TB_RESET / TB_CS / TB_MOTION |
| 18 / 19 | LED_EN / LED_DATA（NFC端子をGPIO化） |
| 20 | D16/BAT（MainではNC） |
| 21 / 22 / 23 | TB_SCLK / ENC_B / TB_SDIO |
| 24 / 25 / 26 | SWDIO / SWDCLK / RESET |
| 27 / 28 / 29 / 30 | GND / BAT_SW / GND / BAT_IN |

左側のトラックボール信号、未使用デバッグ端子等はMainでNC。右FFC J1: 1 GND / 2 +3V3 / 3 TB_CS / 4 NC / 5 TB_SDIO / 6 TB_SCLK / 7 TB_MOTION / 8 TB_RESET。

Samtec候補: Main FLE-115-01-G-DV-A、Carrier FTSH-115-02-F-DV-A。メーカーの推奨ランドからKonnectでフットプリントを作成しました。**Main裏面への反転・実際の嵌合ピン一致はPCB配置時に検証が必要**です。

## RGBと電源

TPS61023でBAT_SWから約5 Vへ昇圧し、SN74AHCT1G125でLEDデータをレベル変換。LED_ENで昇圧回路を停止できる配線です。ソフトウェア実装・実機動作は未検証です。追加LEDスイッチは現状設けていません。

LEDは5 mA/色、全白の公称LED電流は左330 mA/5 V、右300 mA/5 V。制御回路消費と変換損失は別に必要です。保護付き1S LiPoは連続1 A以上を前提に実部品を選定する必要があります。初期消灯、低輝度開始とし、LED_ENを下げる前にLED_DATAをLOWにします。D14/D15のNFC機能解除も必要です。

電源スイッチは500ASSP1M6QE（3 A候補）。OFFで電池をXIAOから切断するため、OFF中は充電できません。USB接続中はOFFでもXIAOが給電される場合があります。旧JS102011SAQN（0.3 A）は採用しません。

## 残作業

1. 3基板への同期・配置。背面USBと電源スイッチ、部品高さとソケット、アンテナ禁止領域、固定方法の確定。
2. 回路図PDFの更新後の見た目確認、LED回路の電源・過渡動作レビュー。
3. 右34 mmボールの支持構造とPMW3610センサー基板（未作成）。
4. 全配線、DRC、シルク、製造・組立図。旧共通基板の配線候補を流用しないこと。
5. ファームウェアのGPIO割当、LED電源制御、輝度・消費電流制限と実機検証。

Gerberは未出力です。

## 出典と編集経路

- [foostan/kbd](https://github.com/foostan/kbd), commit `1f12004a1c9714d0eabec4028c9ae4b259b41562`: MXホットスワップ穴・端子配置。
- [Salicylic-acid3/KiCAD_FootPrint](https://github.com/Salicylic-acid3/KiCAD_FootPrint), commit `9ade20b79abc7716e23f86f6b70f1b357333653c`: ResetSW。
- [Seeed XIAO Plus](https://wiki.seeedstudio.com/XIAO_BLE/): 公式端子番号とフットプリント。
- [FLE推奨ランド](https://suddendocs.samtec.com/prints/fle-1xx-xx-xx-dv-x-footprint.pdf)、[FTSH推奨ランド](https://suddendocs.samtec.com/prints/ftsh-1xx-xx-xxx-dv-xxx-footprint.pdf)。
- LED、昇圧IC、インダクタの資料は `reports/` と回路図に記載。

KiCadソースとライブラリの変更はすべてKonnect MCP経由です。`tools/konnect_call.py` はインストール済みKonnectのMCP stdioクライアントです。`tools/43`〜`49` のJSONと `reports/` の対応結果が今回の変更記録です。各JSONは一度だけ実行する変更履歴であり、一括再実行は禁止です。
