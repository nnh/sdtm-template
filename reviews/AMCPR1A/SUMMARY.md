# 先進医療実績報告 JASPEHR template 設計サマリー

随時更新（2026-06-28 時点）

対象: 先進医療「実績報告」様式第1号別添1（`2025sensinhoukoku_1-1_A`）を SDTM-native な JASPEHR template 化したテンプレート群。モード: RWD・観察（共通ルールのみ適用、介入ヒューリスティック抑制）。フォーム識別子 `--SPID` には**先進医療名**が入る（provenance）。整理コード AMCPR1A はリポジトリ/PR 用のフォーム整理名。出力: `output/*.json`（10件・bridgehead TemplateInput・全 `status: draft`）。**項目はフォーム表示順に忠実**（ドメイン非集約）。

## 凡例

- **CRF**: 人が入力する欄（`FieldItem::Article`）。型・選択肢・制約を記載。
- **Assigned**: 非表示の固定値（`FieldItem::Assigned`, hidden）。SDTM レコードの構造を保つため自動代入し、画面には出さない。
- submission value の `*` = sponsor 拡張（標準 CT になし。bridgehead 登録まで `is_tbc`）。無印 = 標準 CT 実在確認済。

## フォーム構成

- 先進医療の種別で **2バリアント**: 手技・処置・検査・機器使用→**PR**、薬物・生物製剤・再生医療等製品→**EC**。
- 共通テンプレート: 患者基本情報（DM）／診断名（MH・別管理）／入院期間（HO）／転帰（DS）／評価結果（RS）／費用（FA×4）。
- **先進医療名**＝フォーム入力。PR/EC の topic `--TRT` であり、同値を全ドメインの `--SPID` に設定（provenance）。
- **患者番号**＝`SUBJID`（hidden・診察券番号から自動代入）。
- 除外: 総合計（M列）＝ ①+②+③+④ の自動算出のため非収集。

## 項目とドメインの対応

フォーム（Excel）の表示順。

| 位置 | 項目 | ドメイン | 入力変数 | 編集区分 |
|---|---|---|---|---|
| B4 | 保険医療機関名 | DM | SITEID（値=保険医療機関コード） | CRF |
| B8 | 先進医療名 | 全ドメイン / PR・EC | --SPID ／ PRTRT・ECTRT | CRF |
| A | 患者番号 | DM | SUBJID | hidden（自動） |
| B | 診断名 | MH | MHTERM | CRF（別管理） |
| C | 年齢 | DM | AGE（+AGEU） | CRF |
| D | 性別 | DM | SEX | CRF |
| E | 初回実施日 | PR / EC | PRSTDTC / ECSTDTC | CRF（date） |
| F | 入院期間 | HO | HODUR | CRF（整数→P{n}D） |
| G | 実施回数 | PR / EC | PRDOSTOT / ECDOSTOT | CRF（整数） |
| H | 転帰 | DS | DSDECOD | CRF（radio） |
| I・J・K・L | 費用①②③④ | FA×4 | FAORRES | CRF（整数） |
| N | 評価結果 | RS | RSORRES | CRF（radio） |
| M | 総合計 | — | — | 除外 |

## テンプレート別フィールド定義

**DM / 患者基本情報** — `DM_患者基本情報.json`

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| DMSPID | Assigned | テンプレート識別子 | （空）＝先進医療名を設定（provenance） |
| SITEID | CRF（text） | 保険医療機関名 | submission value = 保険医療機関コード（表示は機関名） |
| SUBJID | Assigned（hidden） | 患者番号 | 診察券番号から自動代入 |
| AGE | CRF（整数） | 年齢 | numericality 整数・>=0。単位 AGEU=YEARS |
| AGEU | Assigned | 年齢単位 | `YEARS`（C66781） |
| SEX | CRF（radio） | 性別 | 男=`M` / 女=`F`（C66731） |

**PR / 先進医療（手技・処置・検査）** — `PR_先進医療-手技処置検査.json`

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| PRSPID | Assigned | テンプレート識別子 | （空）＝先進医療名を設定 |
| PRTRT | CRF（text） | 先進医療名 | topic＝先進医療名（入力）。同値を --SPID へ |
| PRSTDTC | CRF（date） | 初回実施日 | 未来日付禁止は自動付与 |
| PRDOSTOT | CRF（整数） | 実施回数（回） | numericality 整数・>=1（--DOSTOT を回数に転用） |
| PRDOSU | Assigned | 実施回数の単位 | `APPLICATION`（C71620） |

**EC / 先進医療（薬物・生物製剤・再生医療等製品）** — `EC_先進医療-薬物生物製剤再生医療等製品.json`

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| ECSPID | Assigned | テンプレート識別子 | （空）＝先進医療名を設定 |
| ECTRT | CRF（text） | 先進医療名 | topic＝先進医療名（入力）。同値を --SPID へ |
| ECSTDTC | CRF（date） | 初回実施日 | 未来日付禁止は自動付与 |
| ECDOSTOT | CRF（整数） | 実施回数（回） | numericality 整数・>=1（--DOSTOT を回数に転用） |
| ECDOSU | Assigned | 実施回数の単位 | `APPLICATION`（C71620） |

**HO / 入院期間** — `HO_入院期間.json`

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| HOSPID | Assigned | テンプレート識別子 | （空）＝先進医療名を設定 |
| HOTERM | Assigned | 医療上のイベント | `HOSPITALIZATION` |
| HODUR | CRF（整数） | 入院期間（日） | numericality 整数・>=0。整数(日)→ISO8601 `P{n}D` |

**DS / 転帰** — `DS_転帰.json`

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| DSSPID | Assigned | テンプレート識別子 | （空）＝先進医療名を設定 |
| DSCAT | Assigned | 区分 | `DISPOSITION EVENT` |
| DSDECOD | CRF（radio） | 転帰 | 治癒=`RECOVERY` / 継続=`ONGOING`* / 中止=`DISCONTINUED`* / 死亡=`DEATH`（C66727） |

**RS / 評価結果** — `RS_評価結果.json`

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| RSSPID | Assigned | テンプレート識別子 | （空）＝先進医療名を設定 |
| RSTESTCD | Assigned | 評価項目コード | `OVRLEFF`* |
| RSTEST | Assigned | 評価項目名 | `Overall Efficacy` |
| RSORRES | CRF（radio） | 評価結果 | 有効=`EFFECTIVE`* / 無効=`NOT EFFECTIVE`* / 不明=`UNKNOWN`* |

**FA×4 / 費用** — `FA_保険外併用療養費分.json` ほか3ファイル

| 変数 | 区分 | ラベル | 値・選択肢・制約 |
|---|---|---|---|
| FASPID | Assigned | テンプレート識別子 | （空）＝先進医療名を設定 |
| FACAT | Assigned | 区分 | `COST` |
| FATESTCD | Assigned | 費用項目コード | ①`COSTINS` / ②`COSTCOP` / ③`COSTPAT` / ④`COSTOTH` |
| FATEST | Assigned | 費用項目名 | 英語名 |
| FAOBJ | Assigned | 対象（先進医療名） | （空）＝先進医療名を設定。FAOBJ で対象を明示 |
| FAORRESU | Assigned | 通貨単位 | `JPY`*（ISO 4217・UNIT CT 非収載） |
| FAORRES | CRF（整数） | 費用金額（円） | numericality 整数・>=0 |

診断名（MH）は別管理のテンプレートを使用（MHTERM・MedDRA LLT を autocomplete でコード化。MHDECOD は導出のため非収集）。

## CRF 入力欄一覧

データ入力担当が画面で入力する欄（hidden を除く・フォーム順）。

| 位置 | ドメイン | 変数 | ラベル | 型 | 選択肢 / 制約 |
|---|---|---|---|---|---|
| ヘッダ | DM | SITEID | 保険医療機関名 | text | 値=保険医療機関コード |
| ヘッダ | PR/EC | --TRT（＝--SPID） | 先進医療名 | text | provenance 兼 topic |
| 患者 | MH | MHTERM | 診断名 | autocomplete | MedDRA LLT |
| 患者 | DM | AGE | 年齢 | 整数 | >=0（AGEU=YEARS） |
| 患者 | DM | SEX | 性別 | radio | 男 / 女 |
| 患者 | PR/EC | --STDTC | 初回実施日 | date | 未来日付禁止 |
| 患者 | HO | HODUR | 入院期間（日） | 整数 | >=0（→P{n}D） |
| 患者 | PR/EC | --DOSTOT | 実施回数（回） | 整数 | >=1 |
| 患者 | DS | DSDECOD | 転帰 | radio | 治癒 / 継続 / 中止 / 死亡 |
| 患者 | FA×4 | FAORRES | 費用①〜④（円） | 整数 | >=0 |
| 患者 | RS | RSORRES | 評価結果 | radio | 有効 / 無効 / 不明 |

患者番号（DM.SUBJID）は hidden（診察券番号から自動代入）。

## Assigned 固定値一覧

| ドメイン | 変数 | 固定値 | 役割 |
|---|---|---|---|
| 全 | --SPID | （空）＝先進医療名 | provenance（フォーム由来の明示） |
| DM | SUBJID | （空）＝診察券番号 | 自動代入（hidden） |
| DM | AGEU | `YEARS` | 年齢単位 |
| PR / EC | --DOSU | `APPLICATION` | 回数の単位（UNIT CT 標準） |
| HO | HOTERM | `HOSPITALIZATION` | 入院イベントの topic |
| DS | DSCAT | `DISPOSITION EVENT` | disposition 区分 |
| RS | RSTESTCD / RSTEST | `OVRLEFF` / `Overall Efficacy` | 評価項目 |
| FA | FACAT | `COST` | 費用カテゴリ |
| FA | FATESTCD / FATEST | COSTINS/COSTCOP/COSTPAT/COSTOTH ほか | 費用項目 |
| FA | FAOBJ | （空）＝先進医療名 | 所見の対象 |
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
| DM | SITEID | 保険医療機関コード | 施設マスタ（CT ではない） |

標準 CT 実在確認済（`is_tbc` なし）: `APPLICATION`（C71620）、`RECOVERY`・`DEATH`（C66727）、`M`・`F`（C66731）、`YEARS`（C66781）。

## SPID と provenance

`--SPID` には**先進医療名**が入り、全ドメイン共通の provenance タグとなる（複数テンプレートが同居しても、どのフォーム由来かを区別）。PR/EC では同値が topic `--TRT` も兼ねる。標準 Identifier 変数で CT 不要・完全準拠。

## RELREC の要否

本フォームは 1患者 = 1先進医療 / 1報告 のため、ある患者の全レコードは `USUBJID` だけで同一エピソードに一意に束ねられ、**RELREC は不要**。費用 FA は `FAOBJ`（先進医療名）で対象を明示。RELREC（または `--LNKID`/`--LNKGRP`）が要るのは 1患者に複数の先進医療がある場合のみ。

## 要対応事項

- 診断名（MH）テンプレートは別管理。SDTM 設計上は MHTERM・MedDRA LLT（autocomplete）。
- `PRDOSTOT`（手技に dose 変数）は標準 PR 変数外の可能性 → bridgehead `domainFields(PR)` で確認。
- 先進医療名（--TRT / --SPID / FAOBJ）はフォーム入力。SITEID は保険医療機関コードを設定。
- sponsor 拡張 CT（上表）を bridgehead に登録し `is_tbc` を解消。
- `HODUR` の整数→ISO8601 `P{n}D` 変換を export 側で実装。

## 出力ファイル一覧

- `DM_患者基本情報.json`（DM）
- `PR_先進医療-手技処置検査.json`（PR）／ `EC_先進医療-薬物生物製剤再生医療等製品.json`（EC）
- `HO_入院期間.json`（HO）／ `DS_転帰.json`（DS）／ `RS_評価結果.json`（RS）
- `FA_保険外併用療養費分.json` / `FA_一部負担金.json` / `FA_患者負担.json` / `FA_その他.json`（FA×4）
