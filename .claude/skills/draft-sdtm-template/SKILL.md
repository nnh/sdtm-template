---
name: draft-sdtm-template
description: "bridgehead の SDTM テンプレート（CDISC 取得項目定義）のドラフトを半自動生成するワークフロー。項目名や元データ項目を受け取り、候補ドメイン×変数を推奨度付きで複数提示し、人が選択したものを TemplateInput JSON として組み立て、bridgehead に draft 投入する。承認は人が行う。『SDTM テンプレートを作りたい』『この項目のテンプレートのドラフトを』『RWD のこのカラムを SDTM にマッピングしたい』等で使う。"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, AskUserQuestion, TaskCreate, TaskUpdate, TaskList
---

# SDTM テンプレート生成ワークフロー

bridgehead の CDISC テンプレート（SDTM 取得項目定義）を **ドラフト生成型** で作る。AI が推奨度付きの候補を提示し、人が選び、人が承認する。各フェーズは **ユーザーの確認を得てから** 次へ進む。勝手に承認・確定しない。

## 知識ベース

このスキルは以下を根拠に判断する（パスはリポジトリルート基準）。

- `docs/house-rules.md` — 命名・CT・デフォルト・条件付き必須・変数取捨・グルーピング・適用範囲タグ・RWD モード・ライフサイクル
- `docs/jaspehr.md` — JASPEHR での位置づけ・FHIR 設計・正準モデル→二重出力
- `docs/references.md` — 一次ソース・標準データ出所・正本マニュアル
- `docs/eval-seed.md` / `docs/rule-candidates.md` — 評価種・未確定ルール

**ルールは適用範囲タグ（共通／介入のみ）に従って取捨する。** 適用したルールは必ず根拠に列挙する（ライフサイクルの還流のため）。

## 出力と用語

**スタンドアロンで動く**。bridgehead も Ptosh も実行時には使わない。正準テンプレートモデルを作り、ファイルとして出力する。

- 一次出力：**bridgehead TemplateInput JSON**（Ptosh で今すぐ使える形。取り込みは後段の任意ステップ）
- 後続出力：**JASPEHR FHIR Questionnaire ＋ 参照 ValueSet**（世界標準。`docs/jaspehr.md` の設計に従う）
- 用語解決：ローカルの **JASPEHR FHIR CodeSystem/ValueSet**（CT/MedDRA/WHODrug-IDF）refdata を参照。未整備の CT は「未検証」と明記し捏造しない。

将来 bridgehead GraphQL（`upsertTemplate` 等）で取り込みを自動化する選択肢はあるが、試行では使わない。

## ワークノート

1 件の作成ごとに `tasks/sdtm-<slug>-notes.md` に蓄積する：入力、判定モード、提示候補と推奨度、人の選択、修正と Why、サーバ検証結果。コミットには含めない。修正は Phase 6 で `rule-candidates.md` へ還流する。

## フェーズ一覧

| # | フェーズ | 確認ゲート | 概要 |
|---|---|---|---|
| 1 | 入力受付・モード判定 | **要確認**（曖昧時） | protocol-driven か RWD かを判定 |
| 2 | 候補生成 | - | 候補ドメイン×変数を複数導出 |
| 3 | CT 解決・ルール適用・推奨度付け | - | 実在 CT 設定、適用ルール選別、スコア付与 |
| 4 | 候補提示・選択 | **要確認** | 推奨度付き候補を提示し人が選ぶ |
| 5 | 組み立て・セルフチェック・出力 | **要確認** | 正準モデル→TemplateInput JSON（後続で FHIR）をファイル出力 |
| 6 | 知見の還流 | - | worknote → rule-candidates へ修正を蒸留 |

---

## フェーズ1: 入力受付・モード判定

入力を受け取り、`house-rules.md`「入力2モードと適用範囲」で分類する。

- **protocol-driven（介入研究）**：項目名＋SAP/PRT 文脈（章 URL）。共通＋介入ルールを適用。依頼に作成依頼者名・項目名・SAP URL・PRT URL が揃っているか確認する。
- **RWD・観察研究（SAP/PRT なし）**：ソースデータ項目（カラム名・サンプル値・元語彙 ICD/LOINC/RxNorm/FHIR/OMOP・データ辞書）。共通ルールのみ適用。

モードが曖昧、または必要情報が不足する場合は AskUserQuestion で確認する（推測で進めない）。RWD では元語彙とサンプル値を必ず尋ねる。

---

## フェーズ2: 候補生成

項目の意味・語彙から**候補ドメイン×変数構成を複数**導く。1 組に絞らない。

1. ドメイン候補を列挙（例：検査値→LB/FA、イベント→AE/CE/MH、投薬→CM/EC）。RWD は元語彙起点（LOINC→LB、ICD/MedDRA→AE/MH、RxNorm/WHO-DD→CM/EC、FHIR/OMOP→対応）。
2. 各候補で `domainFields(domain)` の IG 雛形を取得し、`cdisc.yml` の自動算出変数・対象外ドメインを除外（`house-rules.md`「変数の取捨」）。
3. `searchTemplates(searchText)` で既存類似テンプレートを引き、構成・命名・条件式の前例を集める。
4. RWD で判断に迷う項目は「既存介入テンプレを RWD 用に簡略化した案」と「RWD 専用に組み直した案」の双方を候補に含める。

---

## フェーズ3: CT 解決・ルール適用・推奨度付け

各候補について：

1. **CT 解決**：CT が要る変数は `controlledTerminologies(name)` で実在コードリストを検索し submission value を設定。捏造禁止。ASCII 規則（`≤`→`<=` 等）を適用。
2. **ルール適用**：モードに応じた established ルールのみ適用（適用範囲タグに従う）。RWD で抑制した介入ルールは「RWD のため非適用」と記録。適用ルールを列挙。
3. **命名**：TESTCD 8 文字以内、曖昧さ回避、TEST/ラベルは検査内容が一意に伝わる表記、日本語は正式用語。
4. **推奨度**：各候補に ◎/○/△（または 0–100）を付け、pros/cons を言語化。**閾値（既定 ○ 以上）を超える候補は残す**。

---

## フェーズ4: 候補提示・選択

推奨度付き候補をユーザーに提示し、選択を仰ぐ（**要確認**）。最有力が突出する場合も、検討した代替案と除外理由を併記する。

### 候補提示フォーマット

```markdown
### 候補A — 推奨度 ◎
- ドメイン: LB
- 変数構成: LBTESTCD / LBTEST / LBORRES / LBORRESU / LBDTC ...
- CT: LBORRESU = <CT 名/コード>（実在確認: 済/未検証）
- 適用ルール: [TESTCD 8文字] [ASCII] [自動算出変数除外] ...
- 非適用（RWD等）: [条件付き必須] — RWD のため
- 理由: （なぜこのドメイン/構成が妥当か。pros/cons）

### 候補B — 推奨度 ○
...（同形式。Aとの違いと、Bを選ぶべきケース）
```

ユーザーが候補を選択・修正するまで停止する。複数選択や折衷の指示にも対応する。

---

## フェーズ5: 組み立て・セルフチェック・出力

選択された候補を正準テンプレートモデルにし、そこから bridgehead **TemplateInput JSON** をファイル出力する（FHIR Questionnaire 出力は後続フェーズ。同じ正準モデルから生成）。

### TemplateInput スキーマ

```jsonc
{
  "name": "白血球数（/uL）",
  "domain": "LB",
  "status": "draft",            // 常に draft。approved は人が UI/権限で行う
  "fieldItems": [
    {
      "type": "FieldItem::Article",      // Article/Heading/Note/Assigned
      "fieldType": "select",             // text/date/select/radio_button/autocomplete/sae_report
      "cdiscVariableSuffix": "ORRES",
      "label": "白血球数",
      "defaultValue": "",
      "controlledTerminology": { "name": "...", "uuid": "...", "series": "..." },
      "validators": { "presence": { "validate_presence_if": "STAT.blank?" } },
      "uuid": "<生成>"
    }
  ]
}
```

### 投入前セルフチェック

- 必須変数の充足、TESTCD 8 文字、submission value が ASCII 印字可能のみ
- CT のデフォルト値が submission value に存在（`is_tbc` 警告の事前回避）
- モード別ルールの適用漏れ・誤適用がないか

### 出力

ユーザー承認後（**要確認**）、`output/<domain>_<name>.json` に TemplateInput JSON（`status: draft`）を書き出す。これは bridgehead のインポート形式と同形で、後で手取り込み（画面貼り付け）または将来 `upsertTemplate` で投入できる。**approved への昇格は人が行う**。bridgehead に取り込めば `warnings`/`is_tbc` でサーバ検証もかかる。

---

## フェーズ6: 知見の還流

ユーザーの修正・レビュー指摘を `house-rules.md` のライフサイクルに沿って蒸留する。

1. worknote の「人の選択・修正」と、フェーズ3で列挙した「適用ルール」を突合。
2. 既存ルールで説明できない修正を `docs/rule-candidates.md` に追記（対象テンプレ ID・指摘者・日付・Why・状態 candidate）。
3. 既存ルールの誤りが判明した場合は、その旨を candidate として記録（retire 提案）。

**candidate を established に自動昇格しない。** 昇格・撤回はレビュア・メンテナのキュレーションに委ねる。

---

## 評価

`evals/evals.json` のケースで挙動を確認する。正解テンプレートは内部の bridgehead から `template(id:)` で取得した値（`docs/eval-seed.md`、ID は internal）。採点観点：モード判定・ドメイン一致・必須変数充足・CT 一致・命名規則準拠・複数候補提示・適用ルールの明示。
