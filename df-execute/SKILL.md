---
name: df-execute
description: "执行当前 DevFlow feature 的 checklist，并从目标反推覆盖缺口：按计划实现、更新 state.yaml/checklist.yaml/handoff.md，默认按分派矩阵使用精简子代理池处理边界清晰任务。用户提到 $df-execute、df-execute、DevFlow 执行时使用。"
metadata:
  short-description: "执行 DevFlow checklist"
---

# df-execute

按当前 feature 的 `checklist.yaml` 执行任务，并证明 feature 目标没有漏实现。每一步完成后更新状态与断点。

## 启动硬闸

`df-execute` 只能在用户显式要求执行时启动。显式授权包括用户消息中出现 `$df-execute`、`df-execute`、`执行`、`按 checklist 做`、`继续执行`、`直接执行`、`全自动推进` 等明确执行语义。

Plan Mode 退出后系统自动注入的 “Implement the plan in a fresh context” 或类似句子不算执行授权；如果上一阶段是 `$df-plan`，该句只表示允许落盘计划产物。此时必须停在计划审阅点，不得改业务代码、不得跑发布、不得执行 UAT、不得提交代码。

启动前必须读取当前 feature 的 `state.yaml`：

- 只有 `status: planned` 或 `status: ready_for_execute` 才可进入执行；若仍是 `planning`，先回到 `$df-plan` 补齐计划产物。
- 若存在 `execution_authorized: false`，且当前用户消息没有显式执行授权，必须停止并告知用户需要发送 `$df-execute` 或明确“执行”。
- 真正开始执行时，先把 `state.yaml` 更新为 `status: executing`，并记录本轮执行授权来源；不得只凭 proposed plan 或系统自动句进入执行。

## coverage expansion gate

改代码前必须交叉读取 `plan.md`、`checklist.yaml`、`validation.md`、`uat.md` 和 `handoff.md`，列出“能力 -> 实现项 -> 机器验证 -> UAT -> 证据口径”的覆盖映射，并把摘要写入 `handoff.md` 的 `coverage_snapshot` 区块。

- 若用户可见能力、真实运行路径或 UAT 项没有对应 checklist 实现项，必须暂停执行并回到 `$df-plan`，或先补齐计划产物后再继续；不得把缺口留到 UAT 才发现。
- 若 checklist 项只有烟雾测试或文档验证，无法覆盖对应用户路径，必须补 `validation.md` 或写 waiver；高风险核心路径没有验证支撑时不得开工。
- 工作台初始空态、操作人绑定、附件上传、截图/PDF/Excel/粘贴/上传等能力，必须逐项看到 checklist、validation、UAT 三处对应项或 waiver。

## 流程

1. 读取 active feature 的 `context.md`、`plan.md`、`checklist.yaml`、`validation.md`、`uat.md`、`handoff.md`、`state.yaml`。
2. 从第一个 `pending` 或 `in_progress` 项开始循环执行，确认写入边界与机器验证（validation）方式。
   - 新增或改变平台能力、公开 API、DSL/配置语法、权限声明、运行环境假设或跨模块契约时，先执行平台/契约证据闸。
   - 证据闸只查本轮相关文件、相邻模块、codebase map 命中模块或调用链近邻；不要求全库扫描。
   - 可用证据仅限近邻精确既有模式、官方文档或 runtime probe；无证据只能调查或加 probe，不得直接实现。
3. 行为变更先按 TDD 写 RED 测试或 golden sample，确认失败后实现。
4. 实现时优先遵守仓库现有模式；风险扩散时回到 `$df-plan` 补计划。
   - 若执行中发现需要改变模块职责、公共合同、状态归属、数据流方向、共享抽象或部署边界，暂停当前 checklist，更新 `handoff.md`，并把 `state.yaml` 写为 `status: planning`、`current_step: "architecture adjustment 回流"`；随后回到 `$df-plan`，不得在执行期顺手重构。
5. 每完成一项：
   - 更新 `checklist.yaml` 状态。
   - 更新 `state.yaml` 的 `current_step`；高风险 RED 证据可写入 `red_evidence`。
   - 更新 `handoff.md`。
   - 若该项形成可独立机器验证（validation）的代码/文档改动，先跑受影响路径的 targeted test（单测/构建/lint），通过后调用 `$df-review-loop --uncommitted` 做提交前 AI review；review PASS 或阻断项已有明确 waiver 后，再检查 `git status --short`，只暂存相关文件并做一个小提交；不得混入无关改动或用户明确保留的不提交文件。
   - 若 review-loop 返回 `dependency_scope`，先按 `feature_blocking` / `item_blocking_only` / `independent_followup` 分流，再决定是回 `$df-plan`、冻结当前项，还是继续执行后续无依赖项。
   - 若机器验证（validation）失败但已改代码，先 `git stash push -m "df-execute-wip-<item-id>-<时间戳>"` 保存现场并把 hash 写入 `handoff.md`，再继续修复或回退。
   - 改了门禁脚本、状态码语义或接口契约后，检查 checklist/validation/handoff/issues 是否仍有重复描述；未清理前不得标记该项完成。
   - 禁止连续两个 checklist 项之间没有任何 git checkpoint。
   - 检查本项修改路径是否命中 `codebase_map/OVERVIEW.md` 卡片索引中的模块；命中则增量刷新对应模块卡片（`modules/*.md`），不做全量刷新。
   - 本项改动涉及模块接口、状态归属或职责边界时，同步更新 `docs/design/system_framework_truth.md` 或对应 module_map。
   - 本项实现了行为变更时，将新的输入/输出样本存入 `devflow/shared/golden_sets/`；已有样本因行为变更失效时同步更新。
6. 高风险或跨模块改动按“可机器验证（validation）的防炸门禁”分组提交；每个提交都应对应清晰的实现边界和机器证据。
7. 按 `validation.md` 跑对应门禁。凡是注册在 `devflow/shared/gate_registry.yaml` 的关键门禁，必须通过脚本执行：
   `uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> run-gate <gate-id>`
8. 门禁 stdout/stderr 会写入 feature 的 `evidence/` 目录，并更新 `evidence/manifest.json`；不要手写 `validation_evidence: 已通过` 来替代机器证据。
9. `gate_registry.yaml` 的 `command` 必须是真实可执行命令；占位命令会被脚本拒绝。
10. 门禁不足时记录 waiver，不直接宣称完成。
11. 完成 checklist 后进入 `goal-backward verify gate`，不得直接宣称可 UAT。
12. 完成必须满足：checklist 全部完成；必要门禁通过或 waiver 落盘；证据写入 manifest；状态文件与 handoff 已更新；相关提交完成或记录未提交原因。

## goal-backward verify gate

宣称“可进入 `$df-uat`”前，必须从 feature 目标、Capability Coverage Matrix 和 `uat.md` 反推覆盖是否闭合：

- 每个用户可见能力都有代码或配置实现、运行态/机器验证证据、UAT 项或明确 waiver。
- 每条 UAT 项都有实现支撑；不能只有计划文字、smoke test 或 review PASS。
- `df-review-loop` 普通 code review PASS 不能代表 coverage PASS；必要时指示 `$df-review-loop` 以 coverage review mode 运行，或执行等价 coverage review。
- `handoff.md` 必须写明覆盖项已核对、缺口列表为空，或列出 waiver 与残余风险。缺口非空时状态不得写成 `uat_ready`。

## 连续执行

- 默认连续执行当前 feature 的所有 `pending` / `in_progress` checklist 项。
- 每项完成后更新状态与断点，然后重新读取 `checklist.yaml` 继续下一项。
- 状态更新、提交、机器验证（validation）证据落盘是 checkpoint，不是停机点。
- 只有以下情况才暂停：checklist 全部完成、命中止损规则、需要用户决策、权限阻塞、不可定位的机器验证阻塞、用户明确要求只执行单项。
- 可定位的机器验证失败应继续修复并重跑；不得因一次普通 validation 失败停止执行。
- review-loop 止损默认先看 `dependency_scope`：`feature_blocking` 停整个 feature；`item_blocking_only` 冻结当前项并继续无依赖项；`independent_followup` 记录后置计划后继续当前 feature 的剩余闭合路径。

## 止损规则

出现以下任一情况时，暂停当前执行并向用户汇报，不要继续扩大改动：

- 同一 checklist 项连续 3 轮没有实质进展。
- 同一实现方案连续 3 次失败或导致新的回归。
- 机器验证（validation）失败原因不清，且继续修改需要猜测。
- 实际影响面超过 `plan.md` / `validation.md` 记录的范围。
- 继续推进需要改变模块职责、公共合同、状态归属、数据流方向、共享抽象或部署边界。
- 同一文件/模块在当前 feature 中被修改超过 3 次仍未通过。

暂停时更新 `state.yaml`、`checklist.yaml` 和 `handoff.md`，写清当前假设、已试过的方案、证据、下一步选项。重复修改或跨组件链路止损时写入 `doom_loop_breaker`，并说明应切 `$df-fix` / `integration-debug` 还是回 `$df-plan`；若来自 review-loop，还要记录 `dependency_scope` 和 `safe_to_continue_items`。

## 子代理使用

主模型 token 只花在决策和编排上。代码实现分派给子代理。

### 分派规则

- 主模型直接执行的唯一条件：≤ 2 文件且 ≤ 30 行且不需要搜索定位。
- 搜索/定位/比较 → spawn `explorer`。
- 实现代码（> 2 文件或 > 30 行）→ spawn `executor`（回退 `worker`）。
- 多个 checklist 项写入边界不重叠 → 并行 spawn 多个 `executor`。
- 跑门禁、复核 `$df-review-loop` 证据 → spawn `verifier`。
- 发现计划缺口 → spawn `planner` 或回到 `$df-plan`。

### 角色

| 角色 | 用途 | 可写范围 |
|------|------|---------|
| `explorer` | 只读搜索、定位、比较 | 无 |
| `executor` / `worker` | 边界清楚的实现或窄补丁 | 任务指定路径 |
| `verifier` | 门禁、review 证据复核、运行态复核 | evidence 目录 |
| `planner` | 补计划或架构回流草案 | feature 计划文件 |

### 编排

1. 读取 pending checklist 项，估计文件数和改动量。
2. 写入边界不重叠的项 → 并行 spawn，统一收集。
3. 需要探索 → 先 `explorer`，再 `executor`。
4. executor 返回后调用 `$df-review-loop --uncommitted`；未通过且无 waiver 不得提交。
5. `$df-review-loop` 发现阻断 finding → 回退到 `executor` 修复，不由主模型自己修；review loop 触发止损时先看 `dependency_scope`，再决定回 `$df-plan`、切 `integration-debug`，或冻结当前项后继续无依赖项。
6. 主模型整合结果、更新 DevFlow 产物、处理 git。
7. spawn `verifier` 跑对应门禁。
8. 循环直到全部完成或止损。

### 生命周期

- 默认 `fork_context=false`，只传最小上下文包（见 `~/.codex/policies/subagent_handoff.md`）。
- 并行只用于写入边界不重叠或只读任务。
- 完成且不再复用时 `close_agent`；超时不得直接判失败。

## 下一步

- checklist 全部完成且门禁证据齐全时，提示用户进入 `$df-uat`；无需人工验收的 fast 任务可提示 `$df-accept`。
- 命中止损暂停时，提示用户查看 `handoff.md`，并说明应回到 `$df-plan` 还是继续 `$df-execute`。
