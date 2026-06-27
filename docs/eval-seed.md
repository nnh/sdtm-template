# eval 種データ

随時更新（2026-06-27 時点）

skill の評価セットの種。内部レビューログから抽出した「項目名 → 承認済みテンプレート」の対応。正解テンプレートの実体は内部の bridgehead から取得して確定する（レビュア承認済み＝正解とする運用は未確認論点、`strategy.md` 参照）。

ドメイン・判断のバリエーションを優先して採録（網羅ではない）。**ground-truth のテンプレート ID は internal に保持**（内部情報は非公開）。本書には項目名と判断ポイントのみを記し、ID は載せない。

| 項目名 | ドメイン | 判断ポイント |
|---|---|---|
| 初発診断日 | MH | MHTERM に MedDRA LLT デフォルト、Article Type=MedDRA |
| 有害事象 | AE | AETOXGR=CTCAE Grade・AEREL=因果関係の CT 設定 |
| 併用薬（事前明記 / 薬剤名入力） | CM | CMENRF に ENRF 整合の論理式チェック |
| 白血球数（/uL） | LB | METHOD 削除、LBORRES/LBDTC に条件付き必須 |
| CNS浸潤（CNS Status） | — | ステータス評価パターン、LINKGRP 運用の対象 |
| CD19 ほか表面抗原 | — | コピー横展開（TESTCD/TEST のみ差し替えで CD10/CD22/CD3…） |
| 移植前処置薬剤 | — | TRT をテキスト→薬剤名フィールド、ENRF 追加 |
| 二次がん | — | DECOD 削除、PRESP/OCCUR を Assigned/NY デフォルト Y、診断日必須 |
| 血液学的再発 | CE | CE のグルーピングは VISIT、LINKGRP 削除 |
| CTCAE Grade 各種（発熱性好中球減少症 等） | — | Name に「(CTCAE v5.0)」、欠損 grade の扱い、FAOBJ/FAORRES ラベル検証 |
| PCR-MRD 測定（定量 / カテゴリ） | LB | LBORRES submission value の ASCII 化（≤→<=、記号位置統一） |
| 急性GVHD grade | — | grade 0–IV、未実施は NOT DONE、grade か未実施のいずれか必須 |

## 取得手順

1. 各項目の正解テンプレート ID は internal に保持する。内部の bridgehead から field_items を取得し JSON 保存（手順は internal）。
2. 項目名（依頼相当）を入力、取得 JSON を正解として eval ケース化（既存スキルの `evals/evals.json` の形式を参考）。
3. skill のドラフト出力と正解を、ドメイン一致・必須変数充足・CT 一致・命名規則準拠の観点で採点。
