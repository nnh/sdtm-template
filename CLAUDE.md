# sdtm-template サブプロジェクト

## セッション開始時

**まず `overview.md`（システム全体像）と `strategy.md`（半自動化の方針案）を読むこと。**

## 目的

Ptosh のリポジトリ（非公開）の bridgehead 上で行われている **SDTM-native な eCRF テンプレート作成** を、Claude を用いて**半自動化（ドラフト生成型）** するための設計・知識ベース・スキルを育てるサブプロジェクト。

現状は作成担当（DM）が作成・CDISC担当（レビュア）がレビューする手作業。これを「AIがドラフト生成 → 人が確認・承認」に置き換え、属人性を解消して他スタッフにも展開することがゴール。

## ディレクトリ構成

```
sdtm-template/
├── CLAUDE.md      # このファイル
├── overview.md    # システム全体像（パイプライン・データモデル・現行ワークフロー）※随時更新の中核文書
├── strategy.md    # 半自動化の方針提案（選択肢比較・推奨案・ロードマップ・未確認論点）
├── docs/
│   ├── house-rules.md      # 慣行ルール集（適用範囲タグ・RWD モード・ライフサイクル）
│   ├── rule-candidates.md  # 未確定ルールの還流先
│   ├── references.md       # 一次ソース・GraphQL API・標準データ出所・JASPEHR
│   ├── jaspehr.md          # JASPEHR/CDISC拡張WGでの位置づけ・FHIR設計・正準モデル→二重出力
│   └── eval-seed.md        # 評価セットの種（項目名→テンプレ ID）
├── calibration/            # 較正（答えのある例で手法検証）。README.md ＋ ae/{canonical.json, eval.md}
├── refdata/                # 用語シード（.gitignore・内部の用語サーバから取得）
├── .claude/skills/draft-sdtm-template/   # スキル正本（clone で自動ロード）SKILL.md ＋ evals/
└── .github/                # CODEOWNERS / pull_request_template.md / ISSUE_TEMPLATE/
```

協業は `CONTRIBUTING.md`（PR モデル・メンテナが main の唯一の merger・機微情報の隔離）。リポジトリ入口は `README.md`。

## スキルの3本柱

`skill/draft-sdtm-template/` は以下を実装する。詳細は `strategy.md`「設計の3本柱」。

1. 入力2モード（protocol-driven / RWD）でルールセットを切替
2. house rule の自己進化（established/candidate/retired の還流ループ）
3. 推奨度付き複数候補の提示と人による選択

## 関連リソース

- Ptosh の builder 環境・テンプレート Editor（内部情報は非公開）
- テンプレート Editor/Publisher・Ptosh 本体 EDC（既存 .claude/skills あり）は Ptosh のリポジトリ（非公開）。内部参照は internal
- 作成・レビューの議論ログ（内部レビューログ、内部情報は非公開）
- 正本の内部マニュアル「eCRF構築手順書」（内部情報は非公開）

## 運用方針

- 事実（データモデル・ワークフロー）は必ず一次ソース（リポジトリ実ファイル・内部レビューログ・bridgehead 実画面）に遡って確認してから記述する
- 人物は役割ラベル（作成担当（DM）／CDISC担当（レビュア）／エンジニア／メンテナ）で表記し、個人の氏名は記載しない（内部情報は非公開）
- `overview.md` は一読で最新の全体像が掴める最終形のみを保つ（更新履歴・TODO は溜めない）
