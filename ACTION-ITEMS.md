# アクションアイテム

先進医療実績報告（AMCPR1A）SDTM テンプレートのレビューと還流。詳細は `docs/work-logs/20260628-work-log.md`。

## レビュー待ち

- [ ] マッピングのレビュー（CDISC 担当レビュア2名）— PR #2
- [ ] Skill のあり方・Ptosh/JASPEHR 位置づけの意見（エンジニア2名）
- [ ] 全体への意見（1名）

## 設計の確認事項

- [ ] `PRDOSTOT`（手技に dose 変数）が標準 PR 変数か bridgehead `domainFields(PR)` で確認
- [ ] sponsor 拡張 CT を bridgehead に登録し `is_tbc` を解消（ONGOING / DISCONTINUED / EFFECTIVE / NOT EFFECTIVE / UNKNOWN / OVRLEFF / JPY / 費用 FATESTCD 4種）
- [ ] `HODUR` の整数→ISO8601 P{n}D 変換を export 側で実装
- [ ] 診断名 MH テンプレート（別管理）に `--SPID` を付与

## Phase 6 還流

- [ ] レビュー確定後、確定判断を `docs/rule-candidates.md` へ蒸留（候補: FA 費用格納・`--DOSTOT` 転用・sponsor 拡張マッピング・SPID provenance・RWD の count-in-interventions）。誤りは retire。established 昇格はメンテナのキュレーション。
