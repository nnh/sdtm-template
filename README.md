# sdtm-template

SDTM テンプレート作成（CDISC 取得項目定義）の半自動化。収集項目／RWD ソース項目から、正準テンプレートモデルを作り、**bridgehead TemplateInput JSON**（Ptosh 用）と **JASPEHR FHIR Questionnaire**（世界標準）を生成する AI エージェント。JASPEHR CDISC 拡張 WG（AMED）の研究テーマに対応。

## はじめに

- 何を・なぜ：`CLAUDE.md`（セッション開始時に読む）、`strategy.md`（方針）、`docs/jaspehr.md`（JASPEHR での位置づけ）
- 協業のしかた：`CONTRIBUTING.md`（PR モデル・役割・機微情報）
- 慣行ルール：`docs/house-rules.md`
- 使い方：clone すれば `.claude/skills/draft-sdtm-template/` が Claude Code で自動ロードされる。用語 refdata（FHIR CodeSystem/ValueSet）は内部の用語サーバから取得（`docs/references.md`、内部情報は非公開）

## スタンドアロン

bridgehead も Ptosh も実行時には不要。skill はローカルのファイルだけで動き、出力 JSON を bridgehead のインポート形式に合わせる。取り込みは後段の任意ステップ。
