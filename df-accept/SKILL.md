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
4. 高风险任务必须选择有效防炸门禁；只跑 smoke test 不算。
5. 高风险新增逻辑必须有 RED 证据、失败样本或历史故障复现说明。
6. 若改动影响系统框架正本，相关设计文档已同步更新。
7. 若 `target_env` 为 `dev-full`/`online`，或任务涉及 Dify 发布、容器、线上对象，发布闭环检查项必须完成：发布、自检、生效确认三类证据都要写入 checklist/validation/handoff。
8. 归档前检查 `git status --short`：工作区应干净，或只剩用户明确要求保留的不提交改动；DevFlow 归档移动本身也应提交。
9. 若当前 feature 属于 `devflow/roadmap.md` 中的长目标，归档前必须更新 roadmap：标记当前 feature 完成、保留或调整后续 feature backlog，并在回复里说明下一项建议；不得把 POC 完成表述为整体目标完成。

## 脚本门禁

运行：

`uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> accept`

脚本失败时，不要归档，不要宣称完成；按失败信息补证据或回到 `$df-fix` / `$df-plan`。

通过后 feature 从 `devflow/active/` 移到 `devflow/archive/`。

归档脚本通过后再次检查 `git status --short`，只暂存归档相关路径并提交；若还有业务改动未提交，先回到 `$df-execute` 或 `$df-fix` 分组提交，不要把未归档业务改动混进归档提交。

若 standard 车道没有选择门禁，且 `validation.md` 仍是初始模板，脚本会给出非阻断警告。看到该警告时应补上实际验证记录；不要把 warning 当成防炸门禁。

## 阻断规则

脚本会阻断以下情况：

- checklist 仍有 `pending` 或 `in_progress`。
- `issues.yaml` 仍有 `open` issue。
- 高风险 feature 未选择 regression、golden、integration 或 e2e 类型门禁。
- 已选择关键门禁但没有通过 `run-gate` 生成的通过证据。
- 任一门禁在 manifest 中记录为 failed。
- 固定 checklist 项没有完成或 waiver，包括设计文档同步检查、发布闭环适用性检查。

agent 自己写入的 `validation_evidence: 已通过` 只算说明文字，不算通过证据。

注意：`df-accept` 通过只代表 DevFlow feature 可以归档。对于目标环境为 `online` 的任务，未完成项目 runbook 要求的发布闭环、线上自检和生效确认前，不得要求用户复测，也不得宣称功能已上线可验证。

## 下一步

- 归档成功且 `devflow/roadmap.md` 有后续 feature 时，提示下一项 feature，并建议用 `$df-init` 继续。
- 归档成功且无后续 backlog 时，明确说明 feature 已归档、当前 DevFlow 任务无后续项。
