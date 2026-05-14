---
name: df-accept
description: "DevFlow 最终验收：检查 checklist、UAT issue、验证证据和高风险防炸门禁；通过后归档 feature。用户提到 $df-accept、df-accept、DevFlow 验收或归档时使用。"
metadata:
  short-description: "验收并归档 DevFlow feature"
---

# df-accept

最终验收当前 DevFlow feature。未满足门禁时阻断归档。

## 检查项

1. `checklist.yaml` 全部完成或明确 waiver。
2. `validation.md` 中关键门禁已有执行证据，且 feature 内存在机器生成的 `evidence/manifest.json` 与日志。
3. `issues.yaml` 中 UAT issue 已关闭，或明确转入 `devflow/issues/`。
4. `issues.yaml` 中不得存在同一失败面的重复 UAT 串；先合并口径或标注 `duplicate_of` / `related_issue` 后再验收。
5. 高风险任务必须选择有效防炸门禁；只跑 smoke test 不算。
6. 高风险新增逻辑必须有 RED 证据、失败样本或历史故障复现说明。
7. 若 `target_env` 为 `dev-full`/`online`，或任务涉及 Dify 发布、容器、线上对象，发布闭环检查项必须完成：发布、自检、生效确认三类证据都要写入 checklist/validation/handoff。
8. 归档前检查 `git status --short`：工作区应干净，或只剩用户明确要求保留的不提交改动；DevFlow 归档移动本身也应提交。
9. 若当前 feature 属于 `devflow/roadmap.md` 中的长目标，归档前必须更新 roadmap：标记当前 feature 完成、保留或调整后续 feature backlog，并在回复里说明下一项建议；不得把 POC 完成表述为整体目标完成。
10. `uat.md` 必须覆盖所有用户可见新能力、真实浏览器路径、外部站点路径、插件回流、Dify 发布生效和 ERP 写入审计路径；没有人工 UAT 通过记录时，必须有明确 waiver、残余风险和后续归属。
11. 对真实环境高风险路径，`uat.md` 或 `handoff.md` 必须写清最小“验证画像”：入口路径、客户端/浏览器、profile/登录态来源、目标环境、样本类型；否则不得把后续不同路径的验证结果视为等价复测。
12. 验收前汇总本 feature 修改路径，对照 `codebase_map/OVERVIEW.md` 卡片索引确定命中的模块卡片；检查命中卡片是否已被 execute/fix 刷新，未刷新则刷新或写 waiver。如有新增目录/模块，同步更新 OVERVIEW。
13. 本 feature 涉及模块接口、状态归属或职责边界变更时，检查 `system_framework_truth.md` 和对应 module_map 是否已被 execute/fix 同步更新；未更新则更新或写 waiver。
14. 本 feature 涉及行为变更时，检查 `devflow/shared/golden_sets/` 中受影响的样本是否已更新；golden 门禁是否已跑且样本与当前代码一致。
15. `acceptance.md` 必须记录 `codebase_map_checked`、`truth_doc_checked`、`golden_set_checked` 及各自的 refreshed/waiver 状态。未完成不得归档。
16. 若本 feature 的 `first_pass` UAT 发现 3 个或更多 issue，在 `acceptance.md` 记录 `execute_validation_gap`：回顾哪些失败本可在 execute 阶段通过更强 gate、RED 测试或 golden sample 发现，并把改进建议写入 roadmap、backlog 或后续 feature 的 `validation.md` 参考。该项是回顾性检查，不单独阻断归档。

## 脚本门禁

运行：

`uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> accept`

脚本失败时，不要归档，不要宣称完成；按失败信息补证据或回到 `$df-fix` / `$df-plan`。

通过后 feature 从 `devflow/active/` 移到 `devflow/archive/`。

归档脚本通过后再次检查 `git status --short`，只暂存归档相关路径并提交；若还有业务改动未提交，先回到 `$df-execute` 或 `$df-fix` 分组提交，不要把未归档业务改动混进归档提交。

脚本前必须做人工 UAT 覆盖审计；当前 CLI 只能检查 checklist、issue 和 manifest，不能判断“实现了某个真实用户路径但没做人工 UAT”。发现覆盖缺口时，即使脚本通过也不得归档。脚本后只做确认性复核，确认归档移动和状态更新没有引入新缺口。

脚本前必须做 codebase map / truth doc / golden set 三项 stale gate（检查项 12-14）；CLI 不会自动判断过期，agent 必须主动检查。脚本后只做确认性复核，发现缺口时即使脚本通过也不得归档。

若 standard 车道没有选择门禁，且 `validation.md` 仍是初始模板，脚本会给出非阻断警告。看到该警告时应补上实际验证记录；不要把 warning 当成防炸门禁。

## 阻断规则

脚本会阻断以下情况：

- checklist 仍有 `pending` 或 `in_progress`。
- `issues.yaml` 仍有 `open` issue。
- 高风险 feature 未选择 regression、golden、integration 或 e2e 类型门禁。
- 已选择关键门禁但没有通过 `run-gate` 生成的通过证据。
- 任一门禁在 manifest 中记录为 failed。
- 固定 checklist 项没有完成或 waiver，包括设计文档同步检查、发布闭环适用性检查。
- `uat.md` 仍是初始模板、只有泛泛人工验收记录，或缺少核心用户可见路径的人工 UAT/waiver。

agent 自己写入的 `validation_evidence: 已通过` 只算说明文字，不算通过证据。

## UAT 覆盖审计

归档前从 `checklist.yaml`、`validation.md`、`handoff.md`、`issues.yaml`、`uat.md` 做交叉检查：

- checklist 中每个用户可见能力是否在 `uat.md` 有对应项。
- Golden Set Delta 中每个新增样本是否有自动证据，且真实用户路径是否有人工 UAT 或 waiver。
- 涉及真实 Microsoft Edge、官网页面、本机插件、Dify WebApp、ERP 写入审计的路径是否有真实环境步骤和结果。
- 已关闭 UAT issue 是否有复测记录，不只是“测试/构建通过”。
- 是否把 fixture、mock、curl、DSL check、run-gate 当成真实人工 UAT 通过。

若发现缺口：

- 不归档。
- 在回复中明确列出缺口和对应能力。
- 回到 `$df-uat` 补人工 UAT 引导，或回到 `$df-plan` 补 `uat.md` 覆盖矩阵。
- 只有用户明确接受 waiver 时，才可把缺口记录为 waiver；高风险核心能力 waiver 必须同步写入 roadmap 或后续 backlog。
- 若缺口是“历史 GREEN 没写清验证画像”，先补文档和证据口径，再决定是否需要重新做同路径 UAT。

注意：`df-accept` 通过只代表 DevFlow feature 可以归档。对于目标环境为 `online` 的任务，未完成项目 runbook 要求的发布闭环、线上自检和生效确认前，不得要求用户复测，也不得宣称功能已上线可验证。

## 下一步

- 归档成功且 `devflow/roadmap.md` 有后续 feature 时，提示下一项 feature，并建议用 `$df-plan` 继续。
- 归档成功且无后续 backlog 时，明确说明 feature 已归档、当前 DevFlow 任务无后续项。
