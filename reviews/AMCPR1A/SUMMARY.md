# 先進医療実績報告 SDTM テンプレート設計サマリー

随時更新（2026-06-28 時点）

対象: 先進医療「実績報告」様式第1号別添1（`2025sensinhoukoku_1-1_A`）を SDTM-native eCRF（JASPEHR）化したテンプレート群。モード: RWD・観察（共通ルールのみ適用、介入ヒューリスティックは抑制）。フォーム識別子 SPID: `AMCPR1A`。出力: `output/*.json`（bridgehead TemplateInput 形式・全 `status: draft`）。

## 凡例

- **CRF**: 人が入力する欄（`FieldItem::Article`）。型・選択肢・制約を記載。
- **Assigned**: 非表示の固定値（`FieldItem::Assigned`, hidden）。SDTM レコードの構造を保つため自動代入し、画面には出さない。
- submission value の `*` = sponsor 拡張（標準 CT になし。bridgehead 登録まで `is_tbc` 警告）。無印 = 標準 CT 実在確認済。

## フォーム構成

- 先進医療の種別で **2バリアント**に分割（先進医療名ごとにフォームが分かれる運用）:
  - 手技・処置・検査・機器使用ベース → **PR** テンプレート
  - 薬物・生物製剤・再生医療等製品ベース → **EC** テンプレート
- 共通テンプレート（両バリアントで使用）: 診断名（MH・既存 template 19）／入院期間（HO）／転帰（DS）／評価結果（RS）／費用（FA×4）。
- 全ドメインに `--SPID = AMCPR1A`（hidden）を付与 → provenance（フォーム由来の明示）。1患者1先進医療のため RELREC は不要。
- 除外: 年齢（AGE）・性別（SEX）＝指示により不要。総合計（M列）＝ ①+②+③+④ の自動算出のため非収集。

## 項目とドメインの対応

| 実績報告の列 | 項目 | ドメイン | 入力変数 | 編集区分 |
|---|---|---|---|---|
| B | 診断名 | MH | MHTERM（既存 template 19） | CRF |
| E | 初回実施日 | PR / EC | PRSTDTC / ECSTDTC | CRF（date） |
| G | 実施回数 | PR / EC | PRDOSTOT / ECDOSTOT | CRF（整数） |
| F | 入院期間 | HO | HODUR | CRF（整数→P{n}D） |
| H | 転帰 | DS | DSDECOD | CRF（radio） |
| N | 評価結果 | RS | RSORRES | CRF（radio） |
| I・J・K・L | 費用①②③④ | FA×4 | FAORRES | CRF（整数） |
| C / D / M | 年齢 / 性別 / 総合計 | — | — | 除外 |

## テンプレート別フィールド定義

**PR / 先進医療（手技・処置・検査）** — `PR_先進医療-手技処置検査.json`

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| PRSPID | Assigned | テンプレート識別子 | `AMCPR1A` |
| PRTRT | Assigned | 先進医療名 | （空）試験構築時に先進医療名を固定設定 |
| PRSTDTC | CRF（date） | 初回実施日 | 日付。未来日付禁止は自動付与 |
| PRDOSTOT | CRF（整数） | 実施回数（回） | numericality 整数・>=1（--DOSTOT を回数に転用） |
| PRDOSU | Assigned | 実施回数の単位 | `APPLICATION`（UNIT CT C71620・標準） |

**EC / 先進医療（薬物・生物製剤・再生医療等製品）** — `EC_先進医療-薬物生物製剤再生医療等製品.json`

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| ECSPID | Assigned | テンプレート識別子 | `AMCPR1A` |
| ECTRT | Assigned | 先進医療名 | （空）試験構築時に先進医療名を固定設定 |
| ECSTDTC | CRF（date） | 初回実施日 | 日付。未来日付禁止は自動付与 |
| ECDOSTOT | CRF（整数） | 実施回数（回） | numericality 整数・>=1（--DOSTOT を回数に転用） |
| ECDOSU | Assigned | 実施回数の単位 | `APPLICATION`（UNIT CT C71620・標準） |

**HO / 入院期間** — `HO_入院期間.json`

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| HOSPID | Assigned | テンプレート識別子 | `AMCPR1A` |
| HOTERM | Assigned | 医療上のイベント | `HOSPITALIZATION` |
| HODUR | CRF（整数） | 入院期間（日） | numericality 整数・>=0。整数入力→ISO8601 `P{n}D` に写像 |

**DS / 転帰** — `DS_転帰.json`

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| DSSPID | Assigned | テンプレート識別子 | `AMCPR1A` |
| DSCAT | Assigned | 区分 | `DISPOSITION EVENT` |
| DSDECOD | CRF（radio） | 転帰 | 治癒=`RECOVERY` / 継続=`ONGOING`* / 中止=`DISCONTINUED`* / 死亡=`DEATH`（CT C66727 NCOMPLT） |

DSTERM（verbatim）は選択肢の表示ラベル（治癒/継続/中止/死亡）から導出。

**RS / 評価結果** — `RS_評価結果.json`

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| RSSPID | Assigned | テンプレート識別子 | `AMCPR1A` |
| RSTESTCD | Assigned | 評価項目コード | `OVRLEFF`* |
| RSTEST | Assigned | 評価項目名 | `Overall Efficacy` |
| RSORRES | CRF（radio） | 評価結果 | 有効=`EFFECTIVE`* / 無効=`NOT EFFECTIVE`* / 不明=`UNKNOWN`*（sponsor コードリスト） |

RSSTRESC（標準化）は RSORRES と同値を導出。「不明」は RWD のため非表示にせず保持。

**FA×4 / 費用** — `FA_保険外併用療養費分.json` ほか3ファイル（共通構造）

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| FASPID | Assigned | テンプレート識別子 | `AMCPR1A` |
| FACAT | Assigned | 区分 | `COST` |
| FATESTCD | Assigned | 費用項目コード | ①`COSTINS` / ②`COSTCOP` / ③`COSTPAT` / ④`COSTOTH`（各 sponsor） |
| FATEST | Assigned | 費用項目名 | 英語名（下表） |
| FAOBJ | Assigned | 対象（先進医療名） | （空）試験構築時に設定。FAOBJ で対象を明示（RELREC 不要） |
| FAORRESU | Assigned | 通貨単位 | `JPY`*（ISO 4217・UNIT CT 非収載のため sponsor 拡張） |
| FAORRES | CRF（整数） | 費用金額（円） | numericality 整数・>=0 |

FA 4テンプレートの FATESTCD / FATEST / ラベル:

| ファイル | FATESTCD | FATEST | FAORRES ラベル |
|---|---|---|---|
| FA_保険外併用療養費分 | COSTINS | Cost, Insurer-Paid Combined Care Portion | ①保険外併用療養費分（保険者負担）（円） |
| FA_一部負担金 | COSTCOP | Cost, Insured Copayment Portion | ②一部負担金（被保険者負担）（円） |
| FA_患者負担 | COSTPAT | Cost, Patient Burden of Advanced Medical Care | ③患者負担（先進医療費用）（円） |
| FA_その他 | COSTOTH | Cost, Other | ④その他（円） |

## CRF 入力欄一覧

データ入力担当が画面で実際に入力する欄（hidden を除く）。

| ドメイン | 変数 | ラベル | 型 | 選択肢 / 制約 |
|---|---|---|---|---|
| PR / EC | --STDTC | 初回実施日 | date | 未来日付禁止 |
| PR / EC | --DOSTOT | 実施回数（回） | 整数 | >=1 |
| HO | HODUR | 入院期間（日） | 整数 | >=0（→P{n}D） |
| DS | DSDECOD | 転帰 | radio | 治癒 / 継続 / 中止 / 死亡 |
| RS | RSORRES | 評価結果 | radio | 有効 / 無効 / 不明 |
| FA×4 | FAORRES | 費用①〜④（円） | 整数 | >=0 |
| MH | MHTERM | 診断名 | （既存 template 19） | — |

## Assigned 固定値一覧

| ドメイン | 変数 | 固定値 | 役割 |
|---|---|---|---|
| 全 | --SPID | `AMCPR1A` | provenance（フォーム由来の明示） |
| PR / EC | --TRT | （空） | topic 変数＝先進医療名。試験構築時に設定 |
| PR / EC | --DOSU | `APPLICATION` | 回数の単位（UNIT CT 標準） |
| HO | HOTERM | `HOSPITALIZATION` | 入院イベントの topic |
| DS | DSCAT | `DISPOSITION EVENT` | disposition 区分 |
| RS | RSTESTCD / RSTEST | `OVRLEFF` / `Overall Efficacy` | 評価項目 |
| FA | FACAT | `COST` | 費用カテゴリ |
| FA | FATESTCD / FATEST | COSTINS/COSTCOP/COSTPAT/COSTOTH ほか | 費用項目 |
| FA | FAOBJ | （空） | 所見の対象＝先進医療名。試験構築時に設定 |
| FA | FAORRESU | `JPY` | 通貨単位 |

## sponsor 拡張と標準採用の一覧

bridgehead 登録まで `is_tbc` が立つ sponsor 拡張:

| ドメイン | 変数 | 値 | 出自 |
|---|---|---|---|
| DS | DSDECOD | `ONGOING`, `DISCONTINUED` | NCOMPLT(C66727) になし |
| RS | RSORRES | `EFFECTIVE`, `NOT EFFECTIVE`, `UNKNOWN` | 標準 RS 応答は RECIST のため該当なし |
| RS | RSTESTCD | `OVRLEFF` | sponsor（拡張可コードリスト） |
| FA | FATESTCD | `COSTINS`/`COSTCOP`/`COSTPAT`/`COSTOTH` | 費用は SDTM 標準外 |
| FA | FAORRESU | `JPY` | UNIT CT に通貨非収載（ISO 4217） |

標準 CT 実在確認済（`is_tbc` なし）: `APPLICATION`（UNIT C71620）、`RECOVERY`・`DEATH`（NCOMPLT C66727）。

## SPID と provenance

全レコードが `--SPID = AMCPR1A` を持つため、複数テンプレートが同居しても「どのフォーム由来のレコードか」を区別できる（Ptosh のシート名略称→SPID 運用と同形）。標準 Identifier 変数で CT 不要・完全準拠。

## RELREC の要否

本フォームは **1患者 = 1先進医療 / 1報告** のため、ある患者の全レコードは `USUBJID` だけで同一エピソードに一意に束ねられ、**RELREC は不要**。費用 FA は `FAOBJ`（先進医療名）で対象を明示し、HO/DS/RS は 1介入につき自明。RELREC（または `--LNKID`/`--LNKGRP`）が要るのは **1患者に複数の先進医療があり、どの介入に紐づくかを特定する必要がある場合のみ**。

## 要対応事項

- 既存の診断名テンプレート（MH・template 19）に `MHSPID = AMCPR1A` を付与（bridgehead 側で編集）。
- `PRDOSTOT`（手技に dose 変数）は標準 PR 変数外の可能性 → bridgehead `domainFields(PR)` で確認。
- 先進医療名（PRTRT / ECTRT / FAOBJ）は試験構築時に固定値を設定。
- sponsor 拡張 CT（上表）を bridgehead に登録し `is_tbc` を解消。
- `HODUR` の整数入力→ISO8601 `P{n}D` 変換を export 側で実装。
- SPID 文字列 `AMCPR1A` は Ptosh のシート名略称の流儀に合わせて変更可。

## 出力ファイル一覧

- `PR_先進医療-手技処置検査.json`（PR）
- `EC_先進医療-薬物生物製剤再生医療等製品.json`（EC）
- `HO_入院期間.json`（HO）
- `DS_転帰.json`（DS）
- `RS_評価結果.json`（RS）
- `FA_保険外併用療養費分.json` / `FA_一部負担金.json` / `FA_患者負担.json` / `FA_その他.json`（FA×4）
