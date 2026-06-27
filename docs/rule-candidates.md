# house rule candidate

随時更新（2026-06-27 時点）

テンプレート作成・レビューの過程で抽出された **未確定のルール候補**。確立ルールは `house-rules.md`。ライフサイクルは `house-rules.md`「house rule のライフサイクル」を参照。

各候補は、レビュア・メンテナのキュレーションで `house-rules.md` へ昇格（established）または撤回（retired）する。**人の承認なしに昇格しない。**

## 記入フォーマット

| 日付 | 候補ルール | 出自（テンプレ/Chat/監査差分） | 指摘者 | Why | 状態 |
|---|---|---|---|---|---|

- 出自：対象テンプレート ID・Chat メッセージ・`templateLogs` 差分のいずれか
- Why：なぜそのルールが要るか（後世に残す価値が高いのは Why）
- 状態：candidate / 昇格済み / retired

## 候補一覧

| 日付 | 候補ルール | 出自 | 指摘者 | Why | 状態 |
|---|---|---|---|---|---|
| 2026-06-27 | CT 同定マップ（NCI codelist C-code ↔ bridgehead CT 名/uuid）を refdata に持つ | AE 較正（bridgehead テンプレ1 vs ae_questionnaire.json） | calibration | bridgehead は内部 CT 名、FHIR は NCI C-code で同一 CT を指すため、両出力に変換するには対応表が要る | candidate |
| 2026-06-27 | NCI 1,181 codelist に無い CT（AETOXGR・AEREL 等）は FHIR で inline answerOption、bridgehead は名前付き CT として出力 | AE 較正 | calibration | CTCAE Grade・因果関係スケールは NCI ValueSet に対応が無く、実装も inline で表現していた | candidate |
| 2026-06-27 | バリデータ（presence・date≤Date.current）は bridgehead エミッタの責務。FHIR 出力に required/validators を載せるかは JASPEHR 仕様の今後に依存 | AE 較正 | calibration | FHIR 実装サンプルは required/validators を持たない最小形だった | candidate |
| 2026-06-27 | 重篤判定6項目はテンプレート層で required=false（条件付き必須は試験別 builder 層）。二層モデルと整合 | AE 較正＋手順書3.4.1 | calibration | テンプレートに条件付き必須を焼き込まない方針の確認 | candidate |

## 抽出元シグナル

1. 人が AI ドラフトを修正した差分（skill が出力した「適用ルール」と突合し、説明できない修正を候補化）
2. bridgehead `templateLogs` の監査差分（既存承認テンプレと規則生成結果の乖離）
3. 内部レビューログのレビュー指摘（内部情報は非公開）
