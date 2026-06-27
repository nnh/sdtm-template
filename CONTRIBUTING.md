# 協業ガイド

SDTM テンプレート作成の半自動化を、ドメイン専門家とエンジニアの協業で育てるためのルール。全員が自分の Claude Code を自分のマシンでこのリポジトリに対して使う（Claude のプラン差・Teams 契約差は無関係）。clone すれば `CLAUDE.md`・`docs/`・`.claude/skills/` が全員の Claude を同じ前提で動かす。

## 体制

`main` への取り込みはすべて **Pull Request** 経由。**`main` へマージできるのはメンテナのみ**（branch protection）。PR の merge＝採用、close＝不採用。ルール候補が merge されると `house-rules.md` の established ルールに昇格する＝**ルールのライフサイクルが PR レビューそのもの**。

## 役割

| 役割 | 担当 | 主な貢献 |
|---|---|---|
| メンテナ | メンテナ | 採否判断・方針。`main` の唯一の merger。`docs/house-rules.md`・`docs/jaspehr.md`・`strategy.md` の CODEOWNER |
| ドメイン専門家・利用者 | 作成担当とレビュア | テンプレ評価・修正、ルール候補、新規テンプレ依頼。skill を使い、Claude が PR まで代行 |
| エンジニア | エンジニア | 正準モデル→出力エミッタ、refdata 同期、FHIR Questionnaire、bridgehead/ptosh・JASPEHR 連携 |

## branch 命名

- `feedback/<name>/<topic>` — ルール候補・テンプレ修正の気づき（非エンジニア中心）
- `feat/<topic>` / `fix/<topic>` — コード・エミッタ・refdata（エンジニア）
- `main` 直接コミット禁止。必ず branch → PR。

## 非エンジニアのフロー

作成担当とレビュアは Git を意識しなくてよい。skill を使い、気づきを述べると Claude が branch 作成〜PR 作成まで代行する。Claude に依頼する例：

```
draft-sdtm-template で <項目> のドラフトを作って。
気づいた点を rule-candidates に追記して、PR にして。
```

Claude が行うこと：`feedback/<name>/<topic>` を切る → `docs/rule-candidates.md` に候補を追記（対象・出自・Why・状態 candidate）→ `gh pr create` でメンテナへ PR。テンプレートの実体（JSON）は機微情報のためコミットせず、PR には**気づき・ルール候補・差分の論点**を載せる。

## ルール昇格

`docs/rule-candidates.md`（candidate）→ PR → メンテナが merge すれば `docs/house-rules.md` へ established として転記（適用範囲タグを付す）／不採用は close、誤りは retired。**人の承認なしに established へ昇格しない。**

## 機微情報

**コミット禁止**（`.gitignore` 済）：

- `refdata/`（MedDRA・WHODrug は**ライセンス品**。NCI CT も実体は置かない）
- 患者データ・症例データ
- `calibration/**/ground-truth/`（bridgehead 内部テンプレ・FHIR 実装サンプル）
- skill の `output/`

共有するのは「作り方」（skill・ルール・正準モデル・較正の分析）だけ。「中身」（用語実体・実テンプレ・患者データ）は各自が内部の用語サーバ／内部の bridgehead から取得する（内部情報は非公開）。

## セットアップ

1. clone（`.claude/skills/draft-sdtm-template/` が自動ロードされる）
2. 用語 refdata を取得：用語 refdata（FHIR CodeSystem/ValueSet）を内部の用語サーバから取得し、必要ドメインの ValueSet を `refdata/` に複製（手順は `docs/references.md`、内部情報は非公開）
3. ground truth が要る較正は内部の bridgehead と内部の用語サーバから取得（手順は internal）

## レビュー観点

ドメイン一致／SDTM 変数の過不足／CT・ValueSet 紐付け／命名・ラベル（TESTCD 8 文字・ASCII 等 `docs/house-rules.md`）／適用ルールの明示／複数候補と推奨度。RWD モードでは介入ヒューリスティックの非適用が明記されているか。
