# 較正

随時更新（2026-06-27 時点）

「答えのある問題」で手法を較正してから、答えのない新規項目へ適用するための作業場。各ケースは `<domain>/` に置く。

## 目的

1. パイプライン「収集項目→正準モデル→出力」が正しく動くことを、実在 ground truth を持つ例で検証する。
2. AI ドラフトを主観でなく**差分で機械採点**する評価ハーネスを作る。
3. 人手版との食い違いを `../docs/rule-candidates.md` へ還流する。

## ground truth の取得

- bridgehead テンプレート（JSON 正解）：内部の bridgehead から GraphQL `template(id:)` で field_items を取得（手順は internal、内部情報は非公開）
- JASPEHR FHIR（Questionnaire 正解）：内部の用語サーバ `cdisc_hapi_docker/data/` から取得（内部情報は非公開）
- 用語 refdata：同じ内部の用語サーバ `data/value_sets/`・`code_systems/`（内部情報は非公開）

## 評価観点

ドメイン一致／SDTM 変数の過不足／CT・ValueSet 紐付け／命名・ラベル／バリデータ。差分のうち AI の誤りは修正、改善余地・人手版の問題はルール候補へ。

## ケース

- `ae/` — 有害事象。2 つの ground truth（bridgehead の「有害事象」テンプレート・`ae_questionnaire.json`）を持つ較正ケース。
