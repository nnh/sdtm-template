# SDTM テンプレート作成 house rules

随時更新（2026-06-27 時点）

bridgehead で CDISC テンプレート（SDTM 取得項目定義）を作成する際の慣行ルール集。正本の内部マニュアル「eCRF構築手順書」、内部レビューログの作成・レビュー記録、Ptosh のリポジトリ（非公開）のコードから蒸留（内部情報は非公開）。skill のドラフト生成・セルフチェックの根拠とする。出典は各項末に記す。

## 対象範囲

本書は **CDISC テンプレート作成（bridgehead, CDISC 担当者の作業）** のルール。試験別 eCRF 構築（builder, 構築担当者の作業：VISIT/ARM・論理式・デフォルト値の試験固有設定）は手順書本体を参照。

## 入力2モードと適用範囲

ルールには適用範囲がある。各節の冒頭に **適用** を記す。

- **共通**：SDTM IG 準拠・CT 紐付け・命名（TESTCD 8 文字等）・ASCII 規則など、データの出自に依らず常に適用する構造的・標準的ルール。
- **介入のみ**：前向き収集を前提とした設計ヒューリスティック（条件付き必須・前向き入力向けデフォルト値・「不明」非表示・hugeradio 等）。これらは RWD では**ノイズになりうるため適用しない**。

入力モード：

1. **protocol-driven（介入研究）**：入力＝項目名＋SAP/PRT 文脈。共通＋介入のルールをすべて適用。依頼フォーマット（手順書 3.1）：作成依頼者名／項目名／SAP 該当部位 URL（章番号まで）／PRT 該当部位 URL（章番号まで）。有害事象項目は MedDRA/J で LLT を検索し英語名称を FAOBJ に記載、LLT 複数時は「日本語カレント: Y」を選択、該当なしは SOC のその他の grade を記載。
2. **RWD・観察研究（SAP/PRT なし）**：入力＝ソースデータ項目（カラム名・サンプル値・データ辞書・元語彙 ICD/LOINC/RxNorm/FHIR/OMOP 等）。**共通ルールのみ**適用し、介入ヒューリスティックは抑制。詳細は「RWD・観察研究モード」節。

## 命名規則

**適用: 共通**（CTCAE Grade 命名は介入寄り）

- **--TESTCD は 8 文字以内**（SDTM 制約）。略号は曖昧さを避けて命名する：`ETV6RUNX`→`ETV6RNX1`（RUNX2,3 と区別）、`RUNX1-RUNX1`→`RUNX1-RUNX1T1`（旧 AML1/ETO）。〔Chat 2020-04-14〜15〕
- **記号の代用にアンダースコアを使わない**：`INV_16_`→`INV_16`（括弧の代用としての末尾 `_` は不可）。〔Chat 2020-04-15〕
- **--TEST / ラベルは検査内容が一意に伝わる表記**にする。検査法が結果解釈に効く場合はラベル/名称に明記：定性/定量 PCR 法、FISH 法 等。`RUNX1-RUNX1` のように何の検査か不明な名称は不可。〔Chat 2020-04-15〕
- **日本語表記は正式な臨床用語に合わせる**：`複合型染色体異常`→`複雑核型`（日本血液学会ガイドライン準拠）、`Hyperdiploidy`→`Hyperdiploid`、`Hypodiploidy`→`Hypodiploid`、`GGT`→`γ-GTP`。プロトコル/CRF からの流用語でも正式用語へ修正する。〔Chat 2019-01・2020-04-14〕
- **CTCAE Grade テンプレートの命名**：grade がプロトコル規定の場合、CTCAE バージョンをテンプレート Name に付す（例「発熱性好中球減少症のGrade (CTCAE v5.0)」）。フィールドラベルではなく Name 側に付すのが運用。〔Chat 2020-04-30〜05-01〕

## データ値・統制用語

**適用: 共通**（「不明」非表示は介入のみの収集方針）

- **submission value は ASCII 印字可能文字のみ**。機種依存文字・Unicode 記号は不可：`≤`→`<=`、記号と文字の位置も統一（`10^-3≤`→`>=10^-3`）。コード制約も `format: /\A[[:ascii:]&&[:print:]]+\z/`。〔Chat 2020-06-15／`controlled_terminology.rb`〕
- **選択肢は原則 Controlled Terminology を用いる**。CT に無い場合のみオリジナル作成。参照元は NCI EVS の SDTM Terminology。〔手順書 3.1〕
- **オプション/CT の命名規則**：Controlled Terminology Name・CDISC Terminology Name・CDISC Code は、その CT を設定する変数名とする。〔Chat 2020-06-11〕
- **排他的でない「Other …」選択肢を作らない**。他の選択肢と重複しうる「その他」は原則不可（排他的な場合のみ可）。部位等は自由文入力が本来の形。〔Chat 2020-06-20〕
- **転帰の「不明」は表示しない運用**（AE 転帰・事象発現後の措置とも）。テンプレート側で非表示。〔手順書 3.4.1〕

## デフォルト値

**適用: 介入のみ**（CT 値との一致検証 `is_tbc` は共通）

- **CT のデフォルト値は submission value と一致必須**。不一致だと `is_tbc`（要確認）警告。AI は CT master を検索して実在値を設定する。〔`template.rb#check_is_tbc?`〕
- 既知の既定例：MHTERM=MedDRA LLT コード、AETOXGR=CTCAE Grade、AEREL=因果関係、CAT のデフォルトは文脈に応じ `GENETICS` 等、NY 系は文脈により `Y`。〔Chat 2019-12〜2020-04〕

## バリデータ・論理式・条件付き必須

**適用: 介入のみ**（日付の未来禁止・数値/必須の自動付与は共通の構造ルール）

- **条件付き入力必須**は `validators.presence.validate_presence_if` に式を入れる。例：`LBORRES` に `STAT.blank?`、`LBDTC` に `ORRES.present?`。〔Chat 2020-03-24〕
- **--STAT（未実施）との排他**パターン：`(ORRES.blank? && STAT=='NOT DONE') || (ORRES.present? && STAT.blank?)` で結果か未実施のいずれかを担保。〔手順書 3.3.4〕
- **--ENRF/タイミング変数**の整合式：`(ENDTC.blank? && ENRF=='CONTINUED') || (ENDTC.blank? && ENRF=='ONGOING')`。〔Chat 2020-02-04〕
- **日付変数は未来日付を自動禁止**：`validate_date_before_or_equal_to: Date.current` が `pre_defined_validators.yml` で自動付与される（テンプレート側の手設定不要）。〔`pre_defined_validators.yml`〕
- 数値変数は numericality、必須変数は presence が `to_template` で自動付与。〔`variable.rb#to_template`〕

## 変数の取捨

**適用: 共通**（METHOD のコピー時削除は介入寄りの慣行）

- **MedDRA 派生など自動算出変数は収集しない**（テンプレートに含めない）：AE/MH の LLT・DECOD・PTCD・SOC 系、DM の SUBJID・SITEID・ARM、CM の DECOD 等。`cdisc.yml#calculable_variables` で定義。〔`cdisc.yml`〕
- **利用対象外ドメイン**：CO, TA, TE, TV, TD, TI, TS, TM, RELREC, POOLDEF, RELSUB 等は使わない。〔`cdisc.yml#unusable_domains`〕
- **METHOD はコピー時に既定で削除**（毎回削除している運用）。ただし検査法で結果を区別する必要がある場合は残し、`GIEMSA STAIN`/`KARYOTYPING`/`FISH` 等を設定。〔Chat 2020-03-24・04-15〕
- **Ptosh 拡張変数**：SEQ を持つドメインに `_CO`（Comment）、DS/CE に `_AE`（SAE Report）が自動付与される。〔`sdtm.thor`〕

## ドメイン選定・グルーピング

**適用: 共通＋介入混在**（ドメイン選定は共通／LINKGRP・VISIT グルーピング・PRESP/OCCUR は介入のみ）

- ドメイン選定は項目の意味で判断（例：PSL 反応性の評価は CNS 浸潤ステータスと同形で整理／心エコーは PE か PR か等、境界事例は人が確定）。〔Chat 2019-01・2020-04-30〕
- **グルーピングの使い分け**：CE と検査値のグルーピングは VISIT で行い LINKGRP は不要（削除）。RS と検査値のグルーピングは LINKGRP で行う。LINKGRP は文字 1〜3 文字＋連番（例 TP1, TP2）。〔Chat 2020-06-19／手順書 3.2.10–3.2.11〕
- イベント報告（再発・二次がん等）で根拠データを収集する場合、CE/RS と根拠 LB/FA を LINKGRP で紐付け、オプション名・値・ラベルに CE term と同値を設定しデフォルト化。〔手順書 3.2.10〕
- 事前明示イベントは PRESP=Y → OCCUR で有無収集（OCCUR 必須、日付はありの場合のみ必須・なしは入力不可）。〔手順書 3.2.10〕

## RWD・観察研究モード

SAP/PRT が存在しない取得項目（RWD・レジストリ・EHR 等）のテンプレート化方針。CDISC は RWD の SDTM 化を推進しており（RWD Connect、*SDTM Implementation for Observational Studies* 2024、FHIR-CDISC Mapping）、本サブプロジェクトも視野に入れる。プロジェクト内の関連論文は `../../papers/20260429_PAP_RE05_*`・`../../papers/20260526_SHTI336_ehds-*` を参照。

原則：

- **共通ルールのみ適用、介入ヒューリスティックは抑制**。介入向けの条件付き必須・前向き入力デフォルト・「不明」非表示・hugeradio 等は、観測済みデータの写像では設計ノイズになるため適用しない。
- **event-based を前提に写像する**。研究データは protocol-based だが healthcare data は event-based（CDISC の整理）。VISIT/EPOCH/前向きタイミング前提を置かず、--DTC は観測日時、不規則・欠測を許容する。
- **出自と語彙を起点にドメイン/変数を決める**。ソース項目の元語彙（LOINC→LB、ICD/MedDRA→AE/MH、RxNorm/WHO-DD→CM/EC、FHIR リソース種別、OMOP テーブル）から候補を導く。
- **トレーサビリティを残す**。ソース項目→SDTM 変数の写像根拠、導出は --DRVFL、関連は RELREC/RDOMAIN で表現できるよう候補に含める。BRIDG を中間モデルとして意識。
- **経験則は「適用しない」と明示**。RWD モードで抑制した介入ルールは出力の根拠欄に「RWD のため非適用」と記録し、人が要否を判断できるようにする。

判断に迷う項目は「介入向け既存テンプレートを RWD 用に複製・簡略化した案」と「RWD 専用に組み直した案」を**両方**候補提示する（次節の複数候補方針）。

## house rule のライフサイクル

テンプレートを作る過程そのものでルールを育てる仕組み。ルールは固定知識ではなく、レビュー・修正から継続的に蒸留する（メンテナの方針「Why を残す」「ルールを Doc に記載していく」を踏襲）。

ルールの状態：

- **established**：本書に記載済みの確立ルール。skill が根拠として適用する。
- **candidate**：レビュー修正等から抽出した未確定の規則。`rule-candidates.md` に出自付きで蓄積。
- **retired**：誤り・陳腐化で撤回したルール。

還流ループ：

1. **根拠の明示**：skill は各ドラフトで「適用した established ルール」を列挙する。これにより人の修正が特定ルールに紐づく。
2. **シグナル収集**：(a) 人が AI ドラフトを修正した差分、(b) bridgehead `templateLogs` の監査差分（既存承認テンプレと規則生成結果の乖離）、(c) Chat のレビュー指摘。
3. **candidate 化**：既存ルールで説明できない修正は `rule-candidates.md` に追記（対象テンプレート・指摘者・日付・Why）。
4. **キュレーション**：レビュア・メンテナが candidate を established へ昇格 or retire。昇格時は本書へ転記し適用範囲タグを付す。
5. **反映**：更新ルールで次回ドラフトが改善。誤りは retired として再発を防ぐ。

人の承認なしに candidate を established に自動昇格しない（ドリフト防止）。

## skill 適用方針

入力モード（protocol-driven / RWD）を最初に判定し、適用するルールセットを切り替える。出力は単一案ではなく**推奨度付きの複数候補**とする。

1. **モード判定**：SAP/PRT 文脈ありか、ソースデータ項目（語彙・サンプル値）かで判定。曖昧なら人に確認。
2. **候補生成**：項目から候補ドメイン×変数構成を複数導く。`domains`/`domainFields` で IG 雛形、`searchTemplates` で既存類似テンプレートを取得して根拠にする。
3. **CT 解決**：`controlledTerminologies` で実在 CT を検索し submission value を設定（捏造禁止、ASCII 規則準拠）。
4. **ルール適用**：モードに応じた established ルールのみ適用。RWD で抑制したルールは「非適用」と根拠に明記。
5. **推奨度付け**：各候補に推奨度（◎/○/△ 等）と理由（pros/cons）を付す。**閾値以上の候補は複数提示**し、人が選択できる形にする。最有力が突出する場合も検討した代替案を併記。
6. **セルフチェック**：命名・ASCII・CT 一致・必須変数充足を本書で検査。
7. **投入・還流**：人が選択した候補を `status: draft` で `upsertTemplate` 投入 → `warnings`/`is_tbc` を再チェック → 人がレビュー・承認 → 修正をライフサイクルへ還流。
