# 最终验收

## 验收结论

通过。用户明确跳过人工 UAT，作为本 DevFlow 内部 skill/runtime 治理任务的人工 UAT waiver；机器门禁、review-loop 和覆盖审计已收口。

## 必检项

- [x] checklist 全部完成或明确豁免
- [x] validation.md 中关键门禁已有证据
- [x] UAT issue 已关闭或转入 devflow/issues
- [x] 高风险任务具备 RED 证据或历史故障样本说明
- [x] 发布闭环适用性已确认；适用时已完成发布、自检和生效确认
- [x] codebase map 已检查；过期模块卡片已刷新或明确豁免
- [x] truth doc 已检查；涉及边界变更时已同步更新或明确豁免
- [x] golden set 已检查；涉及行为变更时样本已更新或明确豁免
- [x] AI review loop 证据已检查；适用时 findings 已 pass、waiver 或 manual_review
- [x] Capability Coverage Matrix 已闭环；高风险能力逐行具备实现、validation、UAT、不可替代证据或 waiver
- [x] execute validation gap 已回顾；首测发现 3 个或更多 issue 时已记录改进建议

## Stale Gate

- capability_coverage_matrix_checked: true
- capability_coverage_matrix_ref: plan.md#capability-coverage-matrix
- capability_coverage_matrix_evidence:
  - handoff.md coverage_snapshot 收口：5 个能力行均有实现、validation、UAT 项或 waiver
  - validation.md V-001 至 V-007
  - evidence/manifest.json
- capability_coverage_matrix_waiver: "人工 UAT 由用户明确跳过；uat.md 已记录 waiver 和残余风险"
- codebase_map_checked: true
- codebase_map_refreshed:
  - devflow/shared/codebase_map/OVERVIEW.md
  - devflow/shared/codebase_map/modules/skill-entrypoints.md
  - devflow/shared/codebase_map/modules/runtime-helper.md
  - devflow/shared/codebase_map/modules/docs-and-release.md
- truth_doc_checked: true
- truth_doc_refreshed:
  - "waiver: 本仓库没有 docs/design/system_framework_truth.md；本 feature 用 codebase map 模块卡片作为设计同步载体"
- golden_set_checked: true
- golden_set_refreshed:
  - "waiver: 本 feature 不新增业务 golden sample；compact fixture 已纳入 runtime/tests/test_devflow_cli.py"
- review_loop_checked: true
- review_loop_status: pass
- review_loop_waiver: 无
- execute_validation_gap: 不适用
- waiver:
  - "用户明确跳过人工 UAT，直接 $df-accept；本 feature 不涉及业务发布、真实浏览器、Dify、插件或 ERP 写入路径"
  - "前序 validated feature 仍在 roadmap 的前序待验收中，作为 independent_followup，不阻断本 feature 归档"
