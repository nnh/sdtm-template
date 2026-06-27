# 参照リソース

随時更新（2026-06-27 時点）

sdtm-template の一次ソースと技術インターフェース。

## 正本ドキュメント

- **eCRF構築手順書**: 人手ワークフローの正本となる内部マニュアル。役割・要件定義・CRF 種別ごとの構築手順・house rules を網羅（内部情報は非公開）
- テンプレート管理スプレッドシート（作成トラッキング）: 内部の管理資料（内部情報は非公開）
- 作成・レビュー議論ログ: 内部レビューログ（テンプレート作成の判断・指摘の一次記録、内部情報は非公開）

## リポジトリ

- bridgehead（テンプレート Editor/Publisher）: Ptosh のリポジトリ（非公開）。`src/app/models/cdisc/`, `src/app/graphql/`, `src/lib/tasks/*.thor`
- Ptosh 本体 EDC: Ptosh のリポジトリ（非公開）。`.claude/skills/`・`.claude/context/crf-design.md` がスキル設計の参考
- 調査用クローン: `/tmp/sdtm-recon/`（揮発。再取得は `gh repo clone`）

## 標準データの出所

- SDTM IG ドメイン/変数: CDISC 配布の `SDTM-IG <version>.xml` を `bundle exec thor cdisc:sdtm:import <version>` で取り込み（`sdtm.thor`）
- Controlled Terminology: NCI EVS の TSV（`https://evs.nci.nih.gov/ftp1/CDISC/SDTM/`）を `term.thor` で取り込み

## bridgehead GraphQL API

skill が参照・投入に使う想定の操作（`src/app/graphql/types/query_type.rb`, `mutations/cdisc/`）。

読み取り（query）:
- `templates(name, domain, status=approved)` / `template(id|uuid, isCopy, sdtmVersion)` — テンプレート一覧・取得
- `searchTemplates(domain, searchText, status)` — 既存テンプレートの全文検索（変数名/ラベル/デフォルト値/CT 名）
- `domains(name, version)` — SDTM ドメイン＋変数
- `domainFields(domain, core)` — ドメインの field_items 雛形（`to_template` 由来。header＋変数）
- `controlledTerminologies(name, version, status)` / `controlledTerminology(...)` — CT 検索・取得
- `sdtmVersions` / `controlledTerminologyVersions` / `templateDomains` / `unusableDomains` / `calculableVariables(domain)`
- `templateLogs(id)` / `controlledTerminologyLogs(id)` — 監査ログ

書き込み（mutation）:
- `upsertTemplate(template: {name, domain, fieldItems[], status})` — 作成/更新。`status: approved` は reviewer 認可必須 → AI 生成は `draft` 固定
- `upsertControlledTerminology(...)` / `deleteTemplate` / `deleteControlledTerminology`

投入後はサーバ側 `warnings` / `is_tbc` でセルフチェック可能。

## 一括 export/import

`src/lib/tasks/` の Thor タスク（`sdtm.thor` IG 取り込み、`term.thor` CT 取り込み、`cdisc.thor`、`release.thor`、`templates/ct_diff_report.md.erb` CT 差分レポート）。知識ベースの一括構築・更新に利用可能。

## JASPEHR

位置づけ・FHIR 設計の詳細は `jaspehr.md`。

- 一次資料：内部の設計資料「JASPEHR-Ptosh Project」「JASPEHR CDISC SDTM Implementation Strategy」、内部レビューログ（内部情報は非公開）
- リポジトリ：JASPEHR の上位リポジトリ（非公開）、`mokjpn/ODM2JASPEHR`・`mokjpn/JASPEHRRenderer`・`mokjpn/read.jaspehr`、`nnh/ptosh-ct-update`、`nnh/CTCAE2MedDRA_J`
- IG：`https://jaspehr.jp/wp-content/docs/full-ig_v0.5.11/site/StructureDefinition-jaspehr-questionnaire.html`
- 用語 FHIR CodeSystem/ValueSet 実体：内部の用語サーバ（`cdisc_hapi_docker`）から取得（内部情報は非公開）。`data/value_sets/`＝CT 1,181 ValueSet、`data/code_systems/`、`data/meddra-llt.json`・`idf-whodd.json`、`data/ae_questionnaire.json`（FHIR Questionnaire 実例）
- FHIR 拡張・URL：SDTM 変数＝`item.code`（＋拡張 `http://jaspehr.org/fhir/StructureDefinition/sdtm-variable-name`）、CDISC 提出値＝拡張 `https://jaspehr.jp/fhir/StructureDefinition/cdisc-submission-value`、非表示＝`questionnaire-item-hidden`＋`initial`、選択肢＝`answerValueSet`（外部 ValueSet・日本語は `designation language: ja`）
- 検証スタック：NLM Form Builder（`LHNCBC/formbuilder-lhcforms`）＋ HAPI FHIR R4。JASPEHR Editor（AWS ECR Docker `jaspher-editor`）
- 用語元データ：CT＝NCI EVS（`https://evs.nci.nih.gov/ftp1/CDISC/SDTM/Archive/`）、MedDRA＝MedDRA/J、WHODrug＝UMC WHODrug Global＋IDF（MT協議会）
