---
name: df-execute
description: "执行当前 DevFlow feature 的 checklist，并从目标反推覆盖缺口：按计划实现、更新 state.yaml/checklist.yaml/handoff.md，默认按分派矩阵使用精简子代理池处理边界清晰任务。用户提到 $df-execute、df-execute、DevFlow 执行时使用。"
metadata:
  short-description: "执行 DevFlow checklist"
---

# df-execute

按当前 feature 的 `checklist.yaml` 连续执行，并证明 feature 目标没有漏实现。所有沟通与产物使用简体中文，时间按北京时间。

## 启动硬闸

- 只能在用户显式 `$df-execute`、`df-execute`、`执行`、`按 checklist 做`、`继续执行`、`直接执行`、`全自动推进` 等执行语义下启动。
- Plan Mode 退出后系统自动注入的 “Implement the plan in a fresh context” 不算授权；上一阶段是 `$df-plan` 时只能停在计划审阅点。
- 启动前读当前 feature 的 `state.yaml`。只有 `status: planned` 或 `ready_for_execute` 可进入执行；`ready_for_uat` 只能在当前断点 UAT 已通过或 waiver 后恢复执行；`planning` 必须回 `$df-plan`。
- 若 `status: ready_for_uat` 且当前断点对应的 UAT 项未全部通过、waiver 或明确记录不阻断，拒绝继续后续 DF，提示先运行 `$df-uat` 完成当前断点；若已通过，则先把状态写回 `ready_for_execute`，再从下一个 pending DF 继续。
- 若 `execution_authorized: false` 且当前用户消息没有显式执行授权，停止并要求用户发送 `$df-execute` 或明确“执行”。
- 真正开始前把 `state.yaml` 写为 `status: executing`，记录本轮授权来源；不得只凭 proposed plan 或系统自动句进入执行。

## coverage expansion gate

改代码前交叉读取 `context.md`、`plan.md`、`checklist.yaml`、`validation.md`、`uat.md`、`handoff.md`、`state.yaml`。首次执行必须覆盖这些正本；恢复执行时若 `handoff.md` 超过 100 行，只读最新断点、`coverage_snapshot`、止损区块和当前 checklist 相关段落。

只核验 `plan.md#Capability Coverage Matrix`；coverage verification 是只读检查，不是新阶段，不得生成额外矩阵，也不得改 `plan.md`、`checklist.yaml`、`validation.md`、`uat.md`。

- 首次执行或 `handoff.md` 尚无 `coverage_snapshot`：全量核验矩阵，把摘要写入 `handoff.md#coverage_snapshot`。高风险核心能力缺 checklist、validation、UAT 或不可替代证据时，暂停并记录 `coverage_gaps`，等待用户决定回 `$df-plan`、waiver 或拆后续 feature。
- 恢复执行或已有 snapshot：只核验当前和后续 `pending` / `in_progress` 项对应的矩阵行；不得重审已完成或不相关能力。
- 若当前 checklist 项只有烟雾测试或文档验证，无法覆盖对应用户路径，当前项不得开工。
- 附件、上传、截图/PDF/Excel、粘贴、工作台初始空态、操作人绑定等高风险能力，只在对应矩阵行进入当前或后续项时逐项核验 checklist / validation / UAT / waiver。

## 执行循环

1. 从第一个 `pending` 或 `in_progress` checklist 项开始，确认写入边界、受影响模块和 validation，并在 `handoff.md` 写当前 wave 的 `dispatch_queue`：每项写 `task_id`、`checklist_item`、`agent_role`、`write_scope`、`read_scope`、`validation`、`depends_on`、`attempt_count`、`last_failure_summary`、`next_decision` 和完成判据。队列为空时不得改代码，除非命中 `inline_micro_fix`。
2. 新增或改变平台能力、公开 API、DSL/配置语法、权限声明、运行环境假设或跨模块契约时，先做平台/契约证据闸。证据限近邻既有模式、官方文档或 runtime probe；证据收集优先交给 `explorer`，证据核验优先交给 `verifier`；无证据只能调查或加 probe。
3. 行为变更先写 RED 测试、fixture 或 golden sample 并确认失败，再实现；RED 测试实现进入 `dispatch_queue`，优先交给 `executor`/`worker`。RED 测试默认绑定模块公共接口、用户可见行为或外部可观察状态，不直接断言私有 helper 或内部协作者调用顺序；确需 mock 时只 mock 外部 IO、平台或时间等边界，并写明理由。
4. 影响面超过计划、需要改变模块职责/公共合同/状态归属/数据流/共享抽象/部署边界时，暂停当前项，更新 `handoff.md`，把 `state.yaml` 写为 `status: planning`、`current_step: "architecture adjustment 回流"`，随后回 `$df-plan`。
5. 按 wave 循环执行：分派当前 `dispatch_queue` -> wait/collect -> 收集 targeted test / lint / build 证据 -> 更新 `checklist.yaml`、`state.yaml.current_step`、`handoff.md` -> 必要时记录 `red_evidence` -> 下一队列项或下一 checklist 项。每轮失败后由主代理更新 `attempt_count` 和 `last_failure_summary`；更换子代理、拆换 `task_id` 或重写 prompt 不得清零同一 checklist 项/同一方案的失败计数。
6. 可独立机器验证的改动必须先产生 targeted test / lint / build 证据，再用 `discover-only` 模式调用 `$df-review-loop --uncommitted`，按该模式内部规则处理（P0 循环复审 / P1 修后只查新 P0 / P2 defer）。review-loop 仍走内置 code review；返回的 P0/P1 必须先按 `scope_decision` 分流：`in_scope` 修复追加回 `dispatch_queue` 并交给 `executor`/`worker`，`uncertain_scope` 立即暂停并写止损，`out_of_scope_followup` / `independent_followup` 只记录后续项。存在未修/未 waiver P0，或未分流的 P1 时，不得写 `state.yaml status: ready_for_uat`。
7. review-loop 返回 `dependency_scope` 时先分流：`feature_blocking` 停整个 feature；`item_blocking_only` 只有证明后续项零文件/接口/状态/门禁/UAT 动作链交叉时才能冻结当前项并继续；`independent_followup` 记录后置计划后继续。
8. 机器验证失败但已改代码，先 stash 或 WIP commit，记录 hash、失败原因和下一步，再继续修复或回流。
9. 每个可独立验证项必须 git checkpoint：通过则只暂存相关文件做原子提交；失败但已改代码则 stash/WIP commit 并记录 hash；命中止损则立即 checkpoint。
10. checkpoint 后检查修改路径是否命中 codebase map；命中则只刷新相关模块卡片，刷新前的只读定位可交给 `explorer`。涉及接口、状态归属或职责边界时同步 truth doc 或 module map；行为变更时同步 golden sample。修改门禁脚本、状态码语义或接口契约后，清理 checklist / validation / handoff / issues 中重复或漂移描述。
11. 每个 checklist item 完成机器验证、review-loop、checkpoint 和必要文档同步后，检查该项是否有 `uat_ready`：
    - `level: required`：立即暂停，不继续后续 DF；写 `state.yaml status: ready_for_uat`，在 `handoff.md` 写当前断点、对应 `uat_items`、已完成证据、下一步 `$df-uat` 和后续 pending DF。
    - `level: advisory`：普通 `$df-execute` 下同样暂停并建议 UAT；用户本轮明确“全自动推进”时，可在 `handoff.md` 记录越过理由、断点 UAT 编号和残余风险后继续。
    - 缺少 `level`、`uat_items` 或 `reason` 时视为计划缺口；暂停并回 `$df-plan` 补断点映射。
12. 默认连续执行所有 pending / in_progress 项；只有 checklist 全部完成、命中 `uat_ready` 断点、止损、需要用户决策、权限阻塞、不可定位验证阻塞或用户要求单项时暂停。

## validation 与 evidence

- 按 `validation.md` 跑对应门禁。注册在 `devflow/shared/gate_registry.yaml` 的关键门禁必须通过：
  `uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> run-gate <gate-id>`
- 门禁 stdout/stderr 由脚本写入 feature `evidence/` 并更新 `evidence/manifest.json`；不要用手写“已通过”替代机器证据。
- `gate_registry.yaml` 的 `command` 必须真实可执行；占位命令会被拒绝。
- 门禁不足时记录 waiver，不得宣称完成。

## goal-backward verify gate

checklist 全部完成后，宣称“可进入 `$df-uat`”前，必须从 feature 目标、Capability Coverage Matrix、`validation.md`、`uat.md` 和 evidence 反推覆盖闭合：

- 每个矩阵行都有实现、机器验证证据、UAT 项或明确 waiver。
- `fast` 行只要求用户可见能力和实现项闭合；`standard` 行要求实现项、validation、UAT 闭合；`high-risk` 行逐列闭合或 waiver。
- 每条 UAT 项能回指同一矩阵行；不能只有计划文字、smoke test 或 review PASS。
- 普通 code review PASS 不能代表 coverage PASS；必要时运行 `$df-review-loop` 的 coverage review mode 或等价覆盖审查。
- Aggregate review（`--base`）只在 UAT 全绿且无 open issue 后做一次；UAT 仍有 open/needs_retest issue 时，不启动 aggregate review。
- `handoff.md` 写明覆盖核对结论。缺口非空时不得写 `state.yaml status: ready_for_uat`，只报告缺口和下一步选项。

## 止损规则

出现任一情况立即暂停并更新 `state.yaml`、`checklist.yaml`、`handoff.md`：同一 checklist 项连续 3 轮无实质进展；同一方案连续 3 次失败或引入回归；同一队列项或等价子任务更换子代理后仍连续失败；验证失败原因不清且继续修改需要猜测；实际影响面超过计划；需要架构/合同/状态/数据流调整；同一文件/模块在当前 feature 中被修改超过 3 次仍未通过。

重复修改或跨组件链路止损时写 `doom_loop_breaker`，说明应切 `$df-fix` / `integration-debug` 还是回 `$df-plan`。来自 review-loop 时还要记录 `dependency_scope` 和 `safe_to_continue_items`。

## 编排与子代理循环

主代理是 checklist orchestrator，不是 executor。主代理只保留计划读取、scope/止损判断、coverage gate、队列拆分、状态更新、提交边界和最终结论；搜索、实现、修复、重构和门禁验证必须进入 `dispatch_queue` 并交给子代理。

`inline_micro_fix` 是唯一内联例外，必须同时满足：≤1 文件、≤10 行、无需搜索定位、不是 review finding、不是真实 UAT/runtime/publish 链路、不是测试/门禁/DSL/插件/发布脚本、未命中高风险或跨模块职责边界，并在 `handoff.md` 写 `inline_micro_fix_reason`。队列为空且不满足该例外时，主代理不得编辑代码。

三层分派规则：

- 边界清晰：输入输出明确，且通常不超过 1-3 个文件、≤100 行净变更的实现、修复、重构、测试或验证任务，交给 `executor`/`worker`，必要时让子代理同时写 targeted test。
- 复杂项：超过 3 文件、预计超过 100 行净变更、跨模块或新建+改写混合，主代理先拆成 2-3 个可独立验证子任务，再逐个交给 `executor`/`worker`；拆不动则回 `$df-plan`。
- 边界不清：影响面、公共合同、状态归属或架构职责不确定时，不开工，记录 `handoff.md` 后回 `$df-plan`。

角色分派：搜索/定位/比较/事实收集用 `explorer`；实现/修复/重构用 `executor`，未注册时回退 `worker`；门禁脚本、evidence、runtime 证据和 diff 复核用 `verifier`；计划缺口用 `planner` 或回 `$df-plan`。review-loop 发现阻断 finding 时，修复交给 `executor`/`worker`。

每轮最多同时分派只读任务或写入边界完全不重叠的队列项。子代理运行时，主代理不得读写同一 `write_scope` 或同一验证证据，只能处理不相交的编排、状态和只读证据。默认 `fork_context=false`，handoff 规范见 `~/.codex/policies/subagent_handoff.md`。

`handoff.md` 只保留当前 wave 的 `dispatch_queue`、最新失败摘要、止损区块和 evidence 引用；完整子代理输出、长日志、review/rework 流水写入 `evidence/` 或对应证据文件，避免把 handoff 变成队列全量历史。

当前运行环境若不允许 spawn 子代理，仍不得整块吞掉实现：先按同一 `dispatch_queue` 拆项，记录 `subagent_unavailable_reason`，再逐项顺序执行、逐项验证、逐项 checkpoint。复杂项拆不动或边界不清时回 `$df-plan` 或止损。

## 下一步

- checklist 全部完成且门禁证据齐全时：有人工 UAT 项或 `uat_ready` 断点则写 `state.yaml status: ready_for_uat` 并提示进入 `$df-uat`；无需人工验收的 fast 任务写 `state.yaml status: validated`，记录 no-UAT waiver 后提示 `$df-accept`。
- 命中止损时，提示用户查看 `handoff.md`，并说明应回 `$df-plan` 还是继续 `$df-execute`。
