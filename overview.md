# SDTM テンプレート半自動化 全体像

随時更新（2026-06-27 時点）

Ptosh における「SDTM-native な eCRF テンプレート」の作成・公開・利用パイプラインと、現行の手作業ワークフローを整理する。半自動化の方針案は `strategy.md` を参照。

## パイプライン

```
[SDTM IG / CT 標準]
      │  取り込み
      ▼
bridgehead   ← テンプレート Editor/Publisher（Ptosh のリポジトリ・非公開）
   CDISC::Domain → Variable（SDTM IG 定義）
   CDISC::ControlledTerminology + Term（CT コードリスト）
   CDISC::Template（field_items を持つ取得項目定義。draft / approved）
      │  Ptosh が実行時に GraphQL で取得（Bridgehead::GraphQL, BRIDGEHEAD_URL）
      ▼
Ptosh（Ptosh 本体 EDC / builder 環境）
   Ptosh はテンプレートを自前保存せず、bridgehead から live 取得し to_fields で変換
   Trial → Sheet → FieldItem::Base（CRF メタデータ）＋ Option（CT 由来）
      │
      ▼
aCRF / Define-XML / CDISC 形式データ出力
```

bridgehead が「設計・標準管理」層、Ptosh が「試験ごとの CRF 組み立て・実データ収集」層。テンプレートは bridgehead で一元管理され、各試験の builder 環境で再利用される。

## テンプレートのデータ構造

bridgehead の `CDISC::Template`（`app/models/cdisc/template.rb`）。

| 要素 | 内容 |
|---|---|
| `name` | テンプレート名。domain 内で一意（例「白血球数」「初発診断日」「CD19」） |
| `domain` | SDTM ドメイン（AE, LB, MH, …） |
| `status` | `draft` / `approved`。approved には reviewer ロールが必要。draft CT を含むと approve 不可 |
| `field_items[]` | JSONB 配列。1 項目 = 1 フィールド |
| `uuid` / `is_tbc` | 一意キー / CT 版ズレ検出フラグ（要確認状態） |

各 `field_item` の主なキー（GraphQL `FieldItemInput`）：

- `type`: `FieldItem::Article`（入力）/ `Heading`（見出し）/ `Note`（コメント）/ `Assigned`（非表示・自動代入）
- `field_type`: `text` / `date` / `select` / `radio_button` / `autocomplete` / `sae_report`
- `cdisc_variable_suffix`: SDTM 変数の接尾辞（TERM, ORRES, DTC, TESTCD, TEST, …。prefix=domain で `LBORRES` 等になる）
- `label` / `default_value` / `description` / `level` / `is_invisible`
- `controlled_terminology`: `{name, uuid, series}`（CT への参照）
- `validators`: `presence`（条件付き必須は `validate_presence_if` に論理式）/ `numericality` / `length` / `date` / `formula`

`CDISC::Variable#to_template` が SDTM IG 定義（core=required → presence、data_type=num → numericality、term_name → CT 紐付け）から field_item の**雛形を決定論的に生成**する。AI の付加価値はその上の判断層（後述）。

## 統制用語

`CDISC::ControlledTerminology` + `Term`。`submission_value`（提出値）/ `label` / version 管理。master とコピー（試験固有改変）がある。テンプレートの `default_value` が最新版 CT の submission_value に存在しなければ `is_tbc`（to be confirmed）警告が立つ。例：AETOXGR（CTCAE Grade）、AEREL（因果関係）。

## 書き込み・検証 API

- 書き込み：GraphQL `upsertTemplate(template: TemplateInput)` — `{name, domain, field_items[], status}` を渡す。`status: approved` は reviewer 認可が必要なので、AI 生成は `draft` で投入が基本。
- 検証：投入時に必須・一意・CT 整合（`is_tbc` / `warnings`）をサーバ側が自動判定。AI が CT コードを捏造しても弾ける。
- 横断検索：`TemplateField`（domain / variable / label / default_value / CT 名で既存テンプレートを全文検索）→ 既存資産を few-shot・コピー元として再利用可能。

## 役割と二層構造

作業は二層に分かれる（正本マニュアル「eCRF構築手順書」より）。本サブプロジェクトの自動化対象は前者。

1. **CDISC テンプレート作成**（bridgehead, CDISC 担当者）：再利用可能な SDTM 取得項目定義を作る。「新規テンプレート作成依頼」（作成依頼者名・項目名・SAP URL・PRT URL）で起票。
2. **試験別 eCRF 構築**（builder, 構築担当者→構築確認者→CDISC 担当者）：各試験の CRF をテンプレートと試験固有設定（VISIT/ARM・論理式・デフォルト値）から組み立てる。

## 現行ワークフロー

CDISC テンプレート作成の往復。内部レビューログ（内部情報は非公開）の作成・レビューログより。

1. **作成**：作成担当（DM）が bridgehead の `/cdisc/templates/NNN/edit` で新規作成または既存コピー＆改変
2. **判断要素**：
   - ドメイン選定（例：心エコーは PE か PR か）
   - 変数の取捨（コピー後に METHOD を毎回削除する等）
   - CT・デフォルト値（MHTERM に MedDRA LLT コードを既定設定、AETOXGR=CTCAE Grade）
   - 条件付き必須・論理式（`LBORRES` に `STAT.blank?`、`LBDTC` に `ORRES.present?`、`CMENRF` に `(ENDTC.blank? && ENRF=='CONTINUED')||…`）
   - 命名・表記（`GGT` ではなく `γ-GTP`、TESTCD/TEST/OBJ の整備）
   - コピー横展開（CD19 を複製し TESTCD/TEST のみ変えて CD10/CD22/CD3… を量産）
3. **レビュー**：CDISC担当（レビュア）が確認・指摘し承認
4. **公開**：approve 後、Ptosh の各試験 builder 環境で再利用

このログは「入力＝臨床項目／出力＝確定テンプレート」の対応例の宝庫であり、評価セット（eval）の一次ソースになる。

## 参照ソース

- Ptosh のリポジトリ（非公開、bridgehead）: `src/app/models/cdisc/`, `src/app/graphql/mutations/cdisc/upsert_template.rb`, `src/CLAUDE.md`
- Ptosh のリポジトリ（非公開、本体 EDC）: `.claude/CLAUDE.md`, `.claude/context/crf-design.md`, `.claude/skills/`（既存スキル運用の参考）
- 内部レビューログ（内部情報は非公開）
