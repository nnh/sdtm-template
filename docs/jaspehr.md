# JASPEHR と本サブプロジェクトの位置づけ

随時更新（2026-06-27 時点）

本サブプロジェクト（SDTM テンプレート作成の半自動化）が、JASPEHR / CDISC 拡張 WG の中でどこに位置し、何を入出力するかを整理する。一次資料は内部の設計資料「JASPEHR-Ptosh Project」「JASPEHR CDISC SDTM Implementation Strategy」、内部レビューログ、JASPEHR の上位リポジトリ（内部情報は非公開）。

## JASPEHR とは

**JApanese Standard Platform for EHRs**。AMED・内閣府 SIP・厚労省が支援する公的研究で、JASPEHR 主宰が立ち上げた、ベンダー非依存の **FHIR ベース EHR テンプレート仕様**。各 EHR ベンダー（参加 EHR ベンダー）が共通 FHIR マスタを自社テンプレートエンジンに変換し、診療で埋めて **FHIR QuestionnaireResponse** を産出する。

**CDISC 拡張 WG**（別 AMED 研究、メンテナが PI）は、JASPEHR の FHIR 仕様に **CDISC SDTM メタデータを埋め込み**、JASPEHR で収集したデータを CDISC 準拠データセットへ直接流せるようにする。本サブプロジェクトはこの WG の中核テーマに対応する。

## 中核思想

**入力時にエンコードする**（事後マッピングしない）。事後マッピングは「約2000変数 × 100万レコード ＝ 約20億判断／試験」。入力時エンコードは「約2000テンプレート設計判断を一度だけ」。この6桁の差が、収集の入口で SDTM/CT を埋め込む理由。テンプレート作成の省力化に AI を使うことが研究主題そのもの（「収集項目を入れたら SDTM へマッピングして bridgehead テンプレートのたたき台を作る AI エージェント」）。

## FHIR 設計の決定事項

eCRF ＝ **FHIR Questionnaire**。4 種のメタデータの対応：

- **SDTM 変数名**（約70ドメイン・2〜3千変数）→ Questionnaire の `item.code`（StructureDefinition でバージョン管理。拡張 `sdtm-variable-name` も併用）
- **Controlled Terminology**（約1,181 ValueSet・約5万選択肢）→ FHIR **CodeSystem ＋ ValueSet**
- **MedDRA**（約9万 LLT）→ FHIR CodeSystem（autocomplete で入力、llt_code/llt_kanji/llt_name）
- **WHODrug / IDF**（約3万）→ FHIR CodeSystem。IDF コードと WHODrug Global コードのデュアル格納（CMTRT=IDF英名、CMDECOD=WHODrug Generic Name）。ライセンス非保持時は IDF のみ保持し下流変換（license-aware）

要点：

- 選択肢は `answerValueSet`（Canonical URL）で外部 ValueSet を参照。表示は `display`／日本語は `designation(language: ja)`。
- CDISC 提出値は拡張 `https://jaspehr.jp/fhir/StructureDefinition/cdisc-submission-value`（valueString）で保持（表示「はい」↔提出値「Y」等）。
- 固定値の SDTM 変数（LBTESTCD/LBCAT 等）は `questionnaire-item-hidden` ＋ `initial` で非表示・既定値化。
- CT の synthetic code 戦略：C-Code は codelist 文脈で submission value が変わるため、CodeSystem の concept.code を `C-Code:CodelistName` とし、`baseCode`/`codelistName`/`submissionValue` を property 化。

## bridgehead ↔ Ptosh の正確な関係

- **bridgehead** = テンプレートと用語マスタの**正本DB**（`term.thor` で NCI EVS から CT 取込）。
- **Ptosh** = テンプレートを自分で持たず、`Bridgehead::GraphQL`（`BRIDGEHEAD_URL`）で**実行時に取得**し、`to_fields` でシートのフィールド＋選択肢に変換する利用者。
- 計画：bridgehead のテンプレート → **JASPEHR 規格 FHIR Questionnaire を吐き出すソフト**。さらに QuestionnaireResponse → SDTM CSV へ逆変換。

## 本サブプロジェクトの入出力

```
[収集項目 / RWDソース項目]
        │  draft-sdtm-template（AIエージェント）
        ▼
  内部の正準テンプレートモデル（ドメイン×SDTM変数×CT×バリデータ）
        ├──▶ bridgehead TemplateInput JSON（Ptosh で今すぐ使う・優先）
        └──▶ JASPEHR FHIR Questionnaire ＋ 参照 ValueSet（世界標準・後続）
   用語は JASPEHR FHIR CodeSystem/ValueSet（CT/MedDRA/WHODrug-IDF）から解決
```

bridgehead も Ptosh も**実行時には不要**。テンプレートは JSON 文書であり、本システムは正しい JSON（と将来 FHIR）を作るだけ。取り込みは後段の任意ステップ。

## 既存ツール・サーバ・検証スタック

- リポジトリ：JASPEHR の上位リポジトリ（非公開）、`mokjpn/ODM2JASPEHR`（CDISC ODM-XML→JASPEHR template）、`mokjpn/JASPEHRRenderer`、`mokjpn/read.jaspehr`、Ptosh のリポジトリ（非公開）、`nnh/ptosh-ct-update`、`nnh/CTCAE2MedDRA_J`
- 検証スタック：NLM Form Builder（BSD）＋ HAPI FHIR R4（Apache 2.0）。JASPEHR Editor（AWS ECR の Docker `jaspher-editor`）。
- 用語：HAPI FHIR ローカル（`localhost:8080/fhir/ValueSet/...`）に CT・MedDRA LLT・IDF-WHODrug を登録済（エンジニア）。CodeSystem 自動生成は GitHub Actions 構想（NCI EVS TSV ＋ ja-translations → CodeSystem/ValueSet）。
- IG：`https://jaspehr.jp/wp-content/docs/full-ig_v0.5.11/site/StructureDefinition-jaspehr-questionnaire.html`
- 用語・サンプルの実体は内部の用語サーバ（`cdisc_hapi_docker`）から取得（内部情報は非公開）。

## 用語 refdata と実 FHIR コンベンション

Box `cdisc_hapi_docker/data/` が HAPI FHIR 投入用の用語・サンプル一式。これを refdata として使う。

- `value_sets/ValueSet-C<NCIコード>.json`（**1,181 件**、CT コードリスト＝NCI C-code ごとの ValueSet）
- `code_systems/CodeSystem-C<NCIコード>.json`（同上の CodeSystem）
- `meddra-llt.json`（MedDRA LLT）、`idf-whodd.json`・`drugs.json`・`value-set-tsumura.json`（WHODrug/IDF）
- `ae_questionnaire.json`・`sdtm_dm_sample.json`（FHIR Questionnaire の実例＝出力の正本）

`ae_questionnaire.json` から読み取れる**実装の実コンベンション**（ドラフト strategy doc とは一部異なり、こちらが実装の正）：

- SDTM 変数：item の `extension`（url `https://www.cdisc.org/standards/foundational/sdtm`、`valueString` に変数名 例 `AETERM`）。`_CO`（経過内容）等の Ptosh 拡張変数も同様。
- CT 選択肢：`answerValueSet` に NCI ValueSet の canonical＋版（例 `https://cdisc.org/terminology/nci/valueset/C66769|2025-09-26`。C66769=AESEV, C66742=NY, C66767=ACN, C66768=AEOUT）。Box の `ValueSet-C66769.json` と対応。
- MedDRA：`answerValueSet: .../ValueSet/meddra-llt|28.1` ＋ itemControl `autocomplete`。
- 少数項目は `answerOption`（valueCoding）でインライン定義（CTCAE Grade・AEREL）。itemControl は `radio-button`/`autocomplete`。
- 構成：トップ `group`（例 "AE"）配下に項目（AE1…AE15＋`_CO`）。

