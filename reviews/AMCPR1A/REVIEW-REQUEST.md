# 先進医療実績報告 SDTM テンプレート レビュー依頼

随時更新（2026-06-28 時点）

## 目的

先進医療「実績報告」様式第1号別添1（`2025sensinhoukoku_1-1_A`）を SDTM-native eCRF（JASPEHR）化したテンプレート群（draft）について、**SDTM 設計判断の妥当性**をレビュー担当（CDISC 担当）に依頼する。確定後、判断は house-rules のライフサイクルに沿って `rule-candidates.md` → established へ還流する。

## 対象成果物

- `SUMMARY.md` — 設計の全容（項目↔ドメイン、各変数の CRF/assigned 区分、CT、固定値）
- `aCRF.html` — Ptosh `CDISC::Annotatable` 形式の annotated CRF（1患者入力フォーム・ドメイン色注釈）
- `templates/*.json` — bridgehead TemplateInput（9件・全 `status: draft`）

## 前提

- モード: RWD・観察（SAP/PRT なし＝共通ルールのみ適用、介入ヒューリスティックは抑制）
- `--SPID`＝先進医療名（フォーム入力・全ドメイン共通の provenance）。AMCPR1A はリポジトリ/PR 用のフォーム整理コード
- 項目はフォーム表示順に忠実（ドメイン非集約）
- 除外: 総合計＝自動算出のみ（年齢・性別は収集する）
- 機微情報なし（患者データ・用語実体・内部テンプレ・実名を含まない。先進医療名・施設コードはフォーム入力）

## レビュー方法

各判断ポイントに ○（妥当）／×（要修正）／コメント を付与してください。× は代替案・正しい設計を併記いただけると還流が速くなります。GitHub のインラインコメントも歓迎です。

## 判断ポイント

### 1. 入力モード = RWD・観察
- 採用: SAP/PRT がない事後集計の規制報告様式のため RWD・観察モード。
- 根拠: house-rules「入力2モードと適用範囲」。介入向け条件付き必須・前向きデフォルト・「不明」非表示を抑制。
- 確認: この位置づけで妥当か。介入として扱うべき要素はあるか。

### 2. 先進医療を種別で PR / EC の2フォームに分割
- 採用: 手技・処置・検査・機器使用→PR、薬物・生物製剤・再生医療等製品→EC。
- 根拠: 先進医療名ごとにフォームが分かれる運用（1施設の種類数は限定的）。Interventions クラスの適切なドメイン選定。
- 確認: 2分割の運用で問題ないか。両者にまたがる先進医療の扱い。

### 3. 実施回数を Interventions の --DOSTOT に転用
- 採用: SDTM に「実施回数」標準変数がなく SUPP 不使用方針のため、用量総量変数 `--DOSTOT` に整数格納。単位は UNIT CT 標準語 `APPLICATION`（実在確認済）。
- 根拠: PR/EC ドメイン内に単一フィールドで格納（ユーザー方針：無理してでもドメイン内）。
- 代替: 反復レコード（回数＝件数の導出）／FA に分離。
- 確認: 用量変数の意味上書きは許容か。**特に PR（手技）は本来 dosing せず `PRDOSTOT` は標準 PR 変数外の可能性**（要 `domainFields(PR)` 確認）。反復レコード/FA に戻すべきか。

### 4. 入院期間を `HO / HODUR`
- 採用: 入院＝Healthcare Encounters。在院日数を `HODUR` に格納。整数（日）入力→ISO8601「P{n}D」へ写像。`HOTERM=HOSPITALIZATION`。
- 代替: FA（在院日数＝整数＋`FAORRESU=DAYS`）。
- 確認: HO/HODUR の写像でよいか。整数→ISO8601 変換の実装方針。

### 5. 転帰を DS / DSDECOD にマッピング
- 採用: 治療コースの転帰＝disposition。`DSCAT=DISPOSITION EVENT`。CT は NCOMPLT（C66727）を一次照合。
  - 治癒=`RECOVERY`（標準）／死亡=`DEATH`（標準）／継続=`ONGOING`（sponsor 拡張）／中止=`DISCONTINUED`（sponsor 拡張）
- 確認: このマッピングでよいか。治癒は `RECOVERY` か `COMPLETED` か。継続/中止の sponsor 値の妥当性。

### 6. 評価結果を RS / RSORRES に格納
- 採用: 有効性評価＝Disease Response。`RSTESTCD=OVRLEFF`（sponsor・標準は RECIST 系）。有効=`EFFECTIVE`／無効=`NOT EFFECTIVE`／不明=`UNKNOWN`（全値 sponsor）。「不明」は RWD のため保持。
- 確認: RS で妥当か（FA 案もあり）。`OVRLEFF` と3値 submission value の妥当性。

### 7. 費用①〜④を FA に格納
- 採用: SDTM に費用標準ドメインがなく SUPP 不使用のため FA に押し込み。1費用=1 FATESTCD（`COSTINS`/`COSTCOP`/`COSTPAT`/`COSTOTH`）の横展開。通貨は ISO 4217 `JPY`（UNIT CT 非収載のため sponsor 拡張）。
- 確認: 費用の FA 格納・SUPP 不使用方針の継続でよいか。通貨単位の扱い。

### 8. 先進医療名を --SPID に設定し RELREC 不要
- 採用: フォーム入力の先進医療名を全ドメインの `--SPID` に設定し provenance タグとする。PR/EC では同値が topic `--TRT` も兼ねる。1患者1先進医療のため `USUBJID` で一意＝RELREC 不要（FA は `FAOBJ` で対象明示）。
- 確認: 先進医療名＝SPID（兼 --TRT）の運用でよいか。RELREC 不要の判断でよいか。

### 9. sponsor 拡張 CT の登録
- 該当: `ONGOING`/`DISCONTINUED`（DS）、`EFFECTIVE`/`NOT EFFECTIVE`/`UNKNOWN`/`OVRLEFF`（RS）、`JPY`（FA）、費用 FATESTCD 4種。
- 確認: bridgehead への CT 登録の進め方（`is_tbc` 解消）。

### 10. 保険医療機関を `DM.SITEID` に格納
- 採用: 報告施設を `SITEID` に格納し、submission value は保険医療機関コード（Ptosh 保持）とする。表示は機関名。
- 確認: SITEID への格納・コードを submission value とする運用でよいか。

### 11. 患者番号を DM.SUBJID に自動代入
- 採用: フォームに入力欄はなく、JASPEHR template 上は hidden で診察券番号を `SUBJID` に自動代入。
- 確認: 診察券番号→SUBJID の自動代入でよいか。

### 12. 年齢・性別を DM に収集
- 採用: `DM.AGE`（+`AGEU=YEARS`）、`DM.SEX`（男=`M`/女=`F`・C66731 一次照合）。
- 確認: 収集方針・SEX のコード対応でよいか。

## 次への接続

レビュー結果を `REVIEW-RESPONSE` として反映し、**確定した判断のみ** `docs/rule-candidates.md` に蓄積する（誤りは retire）。candidate の established 昇格はメンテナのキュレーションに委ねる（自動昇格しない）。
