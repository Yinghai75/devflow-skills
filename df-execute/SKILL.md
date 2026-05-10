---
name: df-execute
description: "执行当前 DevFlow feature 的 checklist：按计划实现、更新 state.yaml/checklist.yaml/handoff.md，默认按分派矩阵使用精简子代理池处理边界清晰任务。用户提到 $df-execute、df-execute、DevFlow 执行时使用。"
metadata:
  short-description: "执行 DevFlow checklist"
---

# df-execute

按当前 feature 的 `checklist.yaml` 执行任务。每一步完成后更新状态与断点。

## 启动硬闸

`df-execute` 只能在用户显式要求执行时启动。显式授权包括用户消息中出现 `$df-execute`、`df-execute`、`执行`、`按 checklist 做`、`继续执行`、`直接执行`、`全自动推进` 等明确执行语义。

Plan Mode 退出后系统自动注入的 “Implement the plan in a fresh context” 或类似句子不算执行授权；如果上一阶段是 `$df-plan`，该句只表示允许落盘计划产物。此时必须停在计划审阅点，不得改业务代码、不得跑发布、不得执行 UAT、不得提交代码。

启动前必须读取当前 feature 的 `state.yaml`：

- 只有 `status: planned` 或 `status: ready_for_execute` 才可进入执行；若仍是 `planning`，先回到 `$df-plan` 补齐计划产物。
- 若存在 `execution_authorized: false`，且当前用户消息没有显式执行授权，必须停止并告知用户需要发送 `$df-execute` 或明确“执行”。
- 真正开始执行时，先把 `state.yaml` 更新为 `status: executing`，并记录本轮执行授权来源；不得只凭 proposed plan 或系统自动句进入执行。

## 流程

1. 读取 active feature 的 `context.md`、`plan.md`、`checklist.yaml`、`validation.md`、`state.yaml`。
2. 从第一个 `pending` 或 `in_progress` 项开始循环执行，确认写入边界与验证方式。
3. 行为变更先按 TDD 写 RED 测试或 golden sample，确认失败后实现。
4. 实现时优先遵守仓库现有模式；风险扩散时回到 `$df-plan` 补计划。
5. 每完成一项：
   - 更新 `checklist.yaml` 状态。
   - 更新 `state.yaml` 的 `current_step`；高风险 RED 证据可写入 `red_evidence`。
   - 更新 `handoff.md`。
   - 若该项形成可独立验证的代码/文档改动，检查 `git status --short`，只暂存相关文件并做一个小提交；不得混入无关改动或用户明确保留的不提交文件。
   - 若该项验证失败但已改代码，先 `git stash push -m "df-execute-wip-<item-id>-<时间戳>"` 保存现场并把 hash 写入 `handoff.md`，再继续修复或回退。
   - 禁止连续两个 checklist 项之间没有任何 git checkpoint。
6. 高风险或跨模块改动按“可验证防炸门禁”分组提交；每个提交都应对应清晰的实现边界和验证证据。
7. 按 `validation.md` 跑对应门禁。凡是注册在 `devflow/shared/gate_registry.yaml` 的关键门禁，必须通过脚本执行：
   `uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> run-gate <gate-id>`
8. 门禁 stdout/stderr 会写入 feature 的 `evidence/` 目录，并更新 `evidence/manifest.json`；不要手写 `validation_evidence: 已通过` 来替代机器证据。
9. `gate_registry.yaml` 的 `command` 必须是真实可执行命令；占位命令会被脚本拒绝。
10. 门禁不足时记录 waiver，不直接宣称完成。
11. 完成必须满足：checklist 全部完成；必要门禁通过或 waiver 落盘；证据写入 manifest；状态文件与 handoff 已更新；相关提交完成或记录未提交原因。

## 连续执行

- 默认连续执行当前 feature 的所有 `pending` / `in_progress` checklist 项。
- 每项完成后更新状态与断点，然后重新读取 `checklist.yaml` 继续下一项。
- 状态更新、提交、验证证据落盘是 checkpoint，不是停机点。
- 只有以下情况才暂停：checklist 全部完成、命中止损规则、需要用户决策、权限阻塞、不可定位的验证阻塞、用户明确要求只执行单项。
- 可定位的验证失败应继续修复并重跑；不得因一次普通验证失败停止执行。

## 止损规则

出现以下任一情况时，暂停当前执行并向用户汇报，不要继续扩大改动：

- 同一 checklist 项连续 3 轮没有实质进展。
- 同一实现方案连续 3 次失败或导致新的回归。
- 验证失败原因不清，且继续修改需要猜测。
- 实际影响面超过 `plan.md` / `validation.md` 记录的范围。

暂停时更新 `state.yaml`、`checklist.yaml` 和 `handoff.md`，写清当前假设、已试过的方案、证据、下一步选项。

## 子代理使用

主代理默认编排，优先分派。只有任务很短、薄改、强耦合，或拆分成本高于收益时，才由主代理直接执行。

### 分派矩阵

| 条件 | 执行方式 |
|------|---------|
| 需要先定位、比较、收集事实或确认影响面 | 先 spawn `explorer`，拿到结果后再决定实现方式 |
| 写入边界清晰、验收标准明确、无需主代理持有完整上下文 | spawn `executor`；若当前会话未注册该类型，回退到同定义的 `worker` |
| 多个 checklist 项或子任务写入边界不重叠 | 并行 spawn 多个 `executor`；未注册时回退到多个 `worker`；只读探索可并行 spawn `explorer` |
| 需要跑门禁、审查 diff、核验证据 | spawn `verifier`；若当前会话未注册该类型，由主代理执行验证，不用 `explorer` 冒充 |
| 临时发现计划缺口、影响面扩大或验收口径变化 | spawn `planner` 补计划；若当前会话未注册该类型，主代理暂停实现并回到 `$df-plan` |
| 任务非常短、薄改、强耦合，或拆分成本高于收益 | 主代理直接执行，并在 handoff 记录原因 |

默认分派；只有最后一行允许主代理直接实现。

### 编排循环

1. 读取所有 `pending` / `in_progress` checklist 项，识别写入边界和验证方式。
2. 找出可并行且写入边界不重叠的项；若超过 1 项，按矩阵并行分派并统一收集结果。
3. 单项执行时，若需要探索，先 spawn `explorer`；若探索后仍边界清晰，spawn `executor`，未注册时回退到 `worker`；否则主代理执行或回到 `$df-plan`。
4. 整合子代理结果后，主代理更新 `checklist.yaml`、`state.yaml`、`handoff.md`，并按提交分组规则处理 git。
5. 跑对应门禁并写入 evidence；验证失败但原因可定位时继续修复并重跑。
6. 重新读取 checklist，直到全部完成或命中止损规则。

可用角色：

- `explorer`：只读探索、定位、比较、核验证据。输入探索目标、相关路径、关注点；输出发现摘要、路径、推荐；不得写项目文件；完成时返回“探索完成”。
- `executor`：实现单个边界清晰的 checklist 项。输入目标、写入边界、验收标准、相关路径；输出改动文件、验证结果、提交信息或未提交原因；只写指定路径；完成时返回“执行完成”。
- `worker`：`executor` 的兼容回退，职责、输入输出和写入边界与 `executor` 相同。
- `verifier`：跑门禁、审查 diff、核验证据。输入门禁 ID 或 diff 范围、验收标准；输出通过/失败、证据路径和风险说明；只写 evidence 目录；完成时返回“验证完成”。
- `planner`：临时补充 `plan.md`、`checklist.yaml`、`validation.md`。输入补计划原因、当前断点和影响面；只写当前 feature 目录内计划文件；完成时返回“计划补充完成”。

主代理负责编排、冲突判断、结果整合、状态文件更新、提交分组、门禁最终判定与最终回复。当前会话若未注册 `executor` / `verifier` / `planner`，只允许按上面的明确回退处理。

生命周期：

- spawn 后记录 agent id。
- 并行时收集 ids 后统一 `wait_agent`。
- 拿到最终结果并完成整合后，对已完成且不再复用的子代理调用 `close_agent(id)`。
- `wait_agent` 超时、子代理仍在运行、或已有中间产物，不得直接判失败或提前关闭；应轮询、延长等待、读取中间产物或继续主线后再回收。
- 同一 checklist 项强相关任务可复用同一子代理；换题、换边界或任务结束时关闭。

上下文：

- 默认 `fork_context=false`。
- 只传 feature 目录、当前 checklist 项、相关路径、写入边界、约束、证据摘要和验收标准。
- 并行只用于写入边界不重叠或只读任务。
- 使用 `fork_context=true` 必须符合 `~/.codex/policies/subagent_handoff.md` 的例外条件，并在进度说明里披露原因。

## 下一步

- checklist 全部完成且门禁证据齐全时，提示用户进入 `$df-uat`；无需人工验收的 fast 任务可提示 `$df-accept`。
- 命中止损暂停时，提示用户查看 `handoff.md`，并说明应回到 `$df-plan` 还是继续 `$df-execute`。
