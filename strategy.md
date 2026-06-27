# SDTM テンプレート作成の半自動化 方針提案

随時更新（2026-06-27 時点）

ゴール水準＝**ドラフト生成型**（AI が案を生成し人が確認・承認）、利用者＝**作成担当とレビュア＋他スタッフへ展開**（属人性解消）を前提とする。システム全体像は `overview.md`、JASPEHR / CDISC 拡張 WG での位置づけは `docs/jaspehr.md` を参照。

本システムは JASPEHR CDISC 拡張 WG（メンテナが PI の AMED 研究）の中核テーマ「収集項目→SDTM マッピング→テンプレートのたたき台を作る AI エージェント」に対応する。**入力時エンコード**（事後マッピングの約20億判断を約2000テンプレート設計判断に圧縮）が思想的根拠。

## 現状理解の要約

作成担当（DM）が bridgehead でテンプレート（＝SDTM ドメインの取得項目定義）を新規作成・コピー改変し、CDISC担当（レビュア）がレビュー・承認する手作業。各テンプレートは `domain` と `field_items[]`（変数・CT・デフォルト値・バリデータ）からなる JSONB で、GraphQL `upsertTemplate` で書き込め、サーバ側に必須・CT 整合の検証がある。つまり**「判断（どの変数・CT・既定値・論理式にするか）」が人手のボトルネックで、機械化可能な土台（雛形生成 `Variable#to_template`・書き込み API・検証）は既に存在する**。

## 自動化対象の切り分け

| 工程 | AI 代替可（ドラフト生成） | 人の判断を保持 |
|---|---|---|
| ドメイン選定 | ○ 項目名・文脈から候補ドメインを提案 | △ 境界事例（PE/PR 等）は人が確定 |
| 変数の取捨 | ○ IG 必須＋慣行から field_items を構成、不要変数（METHOD 等）を除外 | △ 試験固有の追加・削除 |
| CT・デフォルト値 | ○ CT master から submission_value を**検索して**設定（捏造しない） | ○ MedDRA 既定コード等の妥当性は人が確認 |
| 条件付き必須・論理式 | ○ 既存パターン（`STAT.blank?` 等）を踏襲した式を提案 | ○ 論理の正しさは人が確認 |
| 命名・表記 | ○ house rule（γ-GTP 等）を適用 | △ 新規表記の最終決定 |
| コピー横展開 | ◎ CD19→CD10/CD22… の TESTCD/TEST 差し替えは最も自動化向き | 軽微 |
| レビュー | ○ 投入前セルフチェック（必須・CT 整合・命名）でレビュアの確認を補助 | ◎ 承認（approved）は reviewer が実施 |

人間が最終承認する「ドラフト生成型」は、規制環境（GCP / ER・ES 指針、監査証跡必須）とも整合する。AI 出力は常に `status: draft` で投入し、approve は人が行う。

## 実現手段の比較

| 案 | 内容 | メリット | デメリット・リスク | 工数感 |
|---|---|---|---|---|
| **A. Claude Code skill** | bridgehead リポジトリ内に `/draft-sdtm-template` skill を置き、項目名→`TemplateInput` JSON＋根拠＋レビュー観点を出力。CT/IG/既存テンプレを参照 | Ptosh で skill 運用実績あり＝採用障壁が低い／既存検証 API をそのまま活用／人がレビューに集中できる | skill 単体では bridgehead の生データ（CT・IG・既存テンプレ）取得に API 接続が必要 | 小〜中 |
| B. スタンドアロン アプリ | 項目リスト→テンプレ一括生成する独立 Web/CLI | バッチ生成・非エンジニアの GUI 運用に向く | `Variable#to_template`・検証・UI の再実装が二重投資／保守者が増える | 大 |
| C. MCP サーバ＋汎用チャット | bridgehead を MCP 化し Claude から CT 検索・既存テンプレ検索・upsert を呼ぶ | 対話的に「この項目を作って」と依頼できる／読み書きを安全に仲介 | MCP の認証・公開範囲の設計が必要／単体では house rule の知識が薄い | 中 |
| D. bridgehead UI 内蔵 AI | 編集画面に「AI ドラフト」ボタンを実装 | 作成担当の現行 UI 動線に最も自然 | フロント/バック改修と LLM 連携実装が必要／実験サイクルが遅い | 大 |

## 推奨案

**A（Claude Code skill）を「スタンドアロン・ファイル入出力」で運用する。** bridgehead も Ptosh も**実行時には使わない**。skill は入力（収集項目／RWD ソース項目）＋ローカルの用語 refdata ＋ house-rules から、**正準テンプレートモデル**を作り、ファイルとして出力する。取り込みは後段の任意ステップ。

ここでの「スタンドアロン」は**比較表の案 B（bridgehead の検証・UI・DB を再実装する重いアプリ）ではない**。bridgehead の `to_template`・検証・DB は再実装せず、出力 JSON を bridgehead のインポート形式に合わせることで「簡便に取り込める」状態にするだけ。

### アーキテクチャ

```
[収集項目 / RWDソース項目]
      │  skill: draft-sdtm-template（ローカル完結）
      ▼
  正準テンプレートモデル（ドメイン×SDTM変数×CT×バリデータ×hidden/既定）
      ├──▶ bridgehead TemplateInput JSON   … Ptosh で今すぐ使う（優先）
      └──▶ JASPEHR FHIR Questionnaire＋ValueSet … 世界標準（後続）
  用語は JASPEHR FHIR CodeSystem/ValueSet（CT/MedDRA/WHODrug-IDF）から解決
```

理由：
1. **試行に最適・最簡**：サービス・API・DB を立てず、ファイルを入れて JSON を出すだけ。すぐ着手でき、壊れない。
2. **二重出力で両目標を満たす**：bridgehead 取り込み（実務）と FHIR Questionnaire（世界標準・JASPEHR）を、同じ正準モデルから生成。
3. **既存資産を再実装しない**：判断層（LLM が得意）に集中。雛形・検証は将来 bridgehead 取り込み時にサーバ側が担う。
4. **採用障壁が低い**：Ptosh チームは既に `.claude/skills/` と eval を運用中。スキル配布で横展開できる。
5. **人間中心・規制整合**：draft 生成＋人の承認が、ドラフト生成型ゴールと監査証跡要件に合う。

### 設計の3本柱

1. **入力2モード（protocol-driven / RWD）**：介入研究は SAP/PRT 文脈ありで共通＋介入ルールを適用。RWD・観察研究は SAP/PRT なし＝ソースデータ項目を入力とし、**共通ルールのみ**適用して介入ヒューリスティックを抑制する（CDISC は RWD の SDTM 化を推進：RWD Connect・SDTM for Observational Studies・FHIR-CDISC Mapping）。経験則がノイズになる懸念に対応。詳細 `docs/house-rules.md`。
2. **house rule の自己進化**：テンプレート作成の過程でルールを育てる還流ループ（established / candidate / retired）。skill は適用ルールを明示し、人の修正・監査差分・Chat 指摘から candidate を `docs/rule-candidates.md` に蓄積、人がキュレーションで昇格・撤回する。
3. **推奨度付き複数候補**：候補ドメイン×変数は 1 組に絞らず、閾値以上を推奨度＋理由付きで複数提示し人が選択する。

### ロードマップ

| フェーズ | 成果物 | 要件 | 状態 |
|---|---|---|---|
| 0 全体像・方針 | overview・strategy・house rule 言語化・JASPEHR 理解 | なし | 完了 |
| 1 知識ベース＋skill 骨組み | `docs/`（house-rules・references・eval-seed・rule-candidates・jaspehr）、`skill/draft-sdtm-template/`。3本柱を実装 | なし | 完了 |
| 2 スタンドアロン最小動作 | 用語 refdata（JASPEHR FHIR CT/MedDRA/WHODrug の小さなシード）＋正準モデル＋**bridgehead TemplateInput JSON 出力**。手元の項目で 1〜2 件作って bridgehead に手で取り込み検証 | 用語 refdata の入手 | 次 |
| 3 FHIR 出力 | 同じ正準モデルから **JASPEHR FHIR Questionnaire＋参照 ValueSet** を出力。HAPI/Form Builder で表示確認 | JASPEHR 仕様 v0.5.11 準拠確認 | 後 |
| 4 レビュー支援・バッチ・RWD・還流 | レビュー観点の自動事前チェック／CRF 一式バッチ／RWD 写像（LOINC/FHIR/OMOP 起点）／rule-candidates 還流の運用 | — | 後 |

## 確定事項

- **skill 正本＝本サブプロジェクト**（`cdisc/sdtm-template/`）で育成・配布。
- **スタンドアロン・ファイル入出力**で動かす（bridgehead/ptosh は実行時不要）。出力は bridgehead インポート形式に合わせ、後で簡便に取り込めるようにする。
- **正準モデル → 二重出力**（bridgehead TemplateInput JSON が優先、JASPEHR FHIR Questionnaire が後続）。
- **用語 refdata は JASPEHR FHIR CodeSystem/ValueSet**（CT/MedDRA/WHODrug-IDF）から解決する。実体は内部の用語サーバ（CT 1,181 ValueSet＋MedDRA/WHODrug＋`ae_questionnaire.json` 実例）に到達確認済み。**取得は内部の用語サーバから**（内部情報は非公開）。
- house rule は `docs/house-rules.md`、JASPEHR の理解は `docs/jaspehr.md` に集約。

参考：bridgehead は読み書き GraphQL（`domains`/`controlledTerminologies`/`searchTemplates`/`upsertTemplate`）を持つので、**将来**取り込みを自動化する選択肢はある。ただし試行では使わない。

## 未確認の論点

1. **refdata の取り込み方**（入手は解決済＝内部の用語サーバ）：内部の用語サーバの用語を毎回参照するか、必要分の小シードを `sdtm-template/refdata/` に複製するか。試行では「使うドメインの ValueSet だけ複製」が軽い。
2. **最初の出力スコープ**：Phase 2 はまず bridgehead TemplateInput JSON のみでよいか（FHIR は Phase 3）。
3. **JASPEHR 仕様準拠の粒度**：FHIR 出力時に v0.5.11／CDISC 拡張ドラフト（参加 EHR ベンダーが起草中）のどこまでに合わせるか。
4. **eval の正解定義**：レビュア承認済みテンプレート＝正解とする運用でよいか。
5. **house rule 引用の扱い**：`house-rules.md` は内部レビューログの個人発言を出典として引用している。内部限定運用で問題ないか。
