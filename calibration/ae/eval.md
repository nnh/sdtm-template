# AE 較正

随時更新（2026-06-27 時点）

入力「有害事象」から正準モデル（`canonical.json`）を作り、2 つの実在 ground truth と照合する。手法の妥当性検証・評価ハーネス・ルール還流が目的（`../README.md`）。

## ground truth

- `ground-truth/bridgehead-template-1.json` — bridgehead の「有害事象」テンプレート（内部の bridgehead から GraphQL 取得、approved、16 field_items。テンプレート ID は internal）
- `ground-truth/ae_questionnaire.json` — JASPEHR FHIR Questionnaire（実装、AE1–AE15＋`_CO`）

両者は**同じ 16 SDTM 変数**を共有し、CT の表現だけが異なる。正準モデルはこの 16 変数を 1 モデルで保持できた。

## 項目対応

| SDTM 変数 | 正準 kind/codelist | bridgehead GT（fieldType / CT） | FHIR GT（type / answer*） | 表現差 |
|---|---|---|---|---|
| AETERM | meddra LLT | meddra / なし・presence | choice / `meddra-llt|28.1`・autocomplete | 同義（MedDRA） |
| AETOXGR | ct AETOXGR | radio / CT "AETOXGR" | choice / inline answerOption Grade1-5 | ★ CT vs インライン |
| AESEV | ct AESEV(C66769) | radio / CT "Severity/Intensity Scale for AE" | choice / ValueSet C66769 | CT 同定差 |
| AESTDTC | date | date / date≤today＋presence | date | バリデータ差 |
| AESER | ct NY(C66742) | radio / CT "No Yes Response 1"・presence | choice / ValueSet C66742・radio | CT 同定差 |
| AESDTH–AESMIE（6） | ct NY(C66742) | radio / CT "No Yes Response 1"（presence なし） | choice / ValueSet C66742・radio | 同上 |
| AEACN | ct ACN(C66767) | radio / CT "Action Taken with Study Treatment 1" | choice / ValueSet C66767 | CT 同定差 |
| AEREL | ct AEREL | radio / CT "AEREL" | choice / inline answerOption RELATED,NOT_RELATED | ★ CT vs インライン |
| AEOUT | ct AEOUT(C66768) | radio / CT "Outcome of Event 1" | choice / ValueSet C66768 | CT 同定差 |
| AEENDTC | date | date / date≤today＋presence | date | バリデータ差 |
| _CO | text | text_area / presence | text | 同義（Ptosh 拡張） |

## 結果

- **正準モデルは AE の全 16 変数を 1 モデルで表現でき、両 ground truth を再構成できる**。モデルの欠落による不一致はゼロ。手法（収集項目→正準→二重出力）は AE で成立。
- 不一致は**モデルの欠陥ではなくエミッタ層の表現差**（想定どおり）。各差は下記ルールで決定論的に変換できる。

## 較正で確定したエミッタ規則

1. **CT 同定マップ**：正準は NCI codelist（C-code＋submission 名）で CT を持つ。bridgehead は内部 CT 名/uuid/series で持つため、`NCI codelist ↔ bridgehead CT` の対応が必要。bridgehead `controlledTerminologies(name:)` / CT の cdisc_code で解決する（例 AESEV=C66769↔"Severity/Intensity Scale for AE"、NY=C66742↔"No Yes Response 1"、ACN=C66767↔"Action Taken with Study Treatment 1"、AEOUT=C66768↔"Outcome of Event 1"）。
2. **NCI 1,181 codelist に無い CT は FHIR でインライン**：AETOXGR（CTCAE Grade）・AEREL は NCI ValueSet に対応が無く、FHIR 実装は `answerOption` でインライン定義。bridgehead は名前付き CT。→ ルール「codelist が NCI に無ければ FHIR は inline answerOption、bridgehead は名前付き CT」。
3. **バリデータは bridgehead 側で表現**：presence・date≤Date.current は bridgehead field_items に出る。FHIR Questionnaire（実装）は required/validators を持たない最小形。→ バリデータは bridgehead エミッタの責務。FHIR は JASPEHR 仕様の拡張待ち。
4. **重篤判定 6 項目はテンプレート層で required=false**：条件付き必須（SER=Y のとき）は試験別 builder 層で付与（手順書 3.4.1）。テンプレートには持たせない＝二層モデルと整合。
5. **`_CO`（経過内容）は Ptosh 拡張変数**：bridgehead `text_area`、FHIR `text`。両系で表現可。

## ルール候補

- CT 同定マップ（NCI C-code ↔ bridgehead CT 名）の維持が必須 → refdata に対応表を持つ。
- 「NCI に無い codelist は FHIR inline」ルールの一般化可否（AETOXGR/AEREL 以外でも）。
- FHIR 出力に required/validators を載せるか（JASPEHR 仕様の今後に依存）。

## 次

新規項目（ground truth なし）への適用へ。AE で確定したエミッタ規則と CT 同定マップを用い、AI が blind に生成した案を人が裁定する。
