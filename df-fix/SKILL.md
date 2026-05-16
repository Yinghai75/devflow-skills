---
name: df-fix
description: "对 DevFlow UAT issue 执行 plan → execute → validate → UAT 闭环；根因清楚时直接修复，根因不清时先调查。用户提到 $df-fix、df-fix、修 UAT issue、修 open issue 时使用；在 $df-uat 中登记 critical/high issue、阻断当前 UAT 的 issue、或用户反馈 UAT 失败后需要改实现时也必须自动使用。"
metadata:
  short-description: "修复 DevFlow UAT issue"
---

# df-fix

围绕当前 feature 的 `issues.yaml` 修复 UAT issue。修复完成不等于最终验收；最后仍需 `$df-accept`。

## 强制接管

- 当前 feature 存在 open UAT issue 时，禁止“顺手修”；必须进入本 skill。
- 从 `$df-uat` 转修前，必须完成本轮反馈 intake 并明确 issue id；用户要求修刚登记的问题时切到 `$df-fix <issue-id>`。
- 读取 `issues.yaml` 前先执行 compact 前置检查：closed/deferred issue 达到 3 个及以上，或长历史主要来自 closed/deferred issue 时，运行 `uv run python ~/.codex/local/devflow/devflow_cli.py --repo <repo> compact-issues`，再确认 YAML 可解析、open/retest issue 未被压缩、下一个 UAT id 不冲突。若目标 open/retest issue 本身超过 50 行，不得先 compact；只读当前摘要、最新证据和 `history_ref` 后继续修复。
- 先读取 open / fixed_pending_retest / needs_retest issue 的当前摘要并确认目标 id；没有目标 id 时只能调查和登记，不能改实现。
- 已先做补丁但未完成本流程时，不得声明完成；必须补齐 RED、修复验证、门禁、review 和 DevFlow 记录。
- 本 skill 闭环优先级高于继续 UAT；关闭 issue 后回 `$df-uat` 复测。

长 `handoff.md` / `issues.yaml` 采用 scoped reading：`handoff.md` 超过 100 行时先读最新断点、止损区块和目标 issue 相关段落；closed issue 默认只读 id、状态、复测标记、最新证据和 `history_ref`。本 skill 必须读全目标 issue 的当前失败面、最新证据、复测状态和 `history_ref`。

## 车道分流

读取目标 issue 后，读 `codebase_map/OVERVIEW.md` 和命中模块卡片。改实现前必须在 `issues.yaml` 或 `handoff.md` 最新段落落盘：`map_modules_read`、`fix_lane`、`lane_reason`、`q1_causal_chain`；除 fast-fix 外还要落 `q2_regression_list`、`q3_platform_assumptions`。缺任一项只能调查。

- `fast-fix`：文案、样式、单组件展示、单函数纯逻辑或测试断言补漏，且不命中高风险。只需 1 行 q1、最小 RED、最小修复、targeted test、原子提交、关闭 issue 后回 UAT；验证失败立即升级 scoped-fix 并补 review-loop。
- `scoped-fix`：默认车道，当前 feature 影响面内的受控回归。写回归面清单，同一路径 RED/GREEN，修后跑 targeted test、构建、相关门禁和 `$df-review-loop --uncommitted`。
- `high-risk-fix`：跨 Dify/插件/Broker/`nas-agent`/`erp-executor`/容器/发布链路、验收口径或职责边界变化、真实浏览器/登录态/外部站点/发布后路径、DOM 猜测/改包/乐观渲染等。默认只调查；确认单点错误后写降级或收窄理由才可窄补丁。
- `integration-debug`：跨 3+ 运行中组件、同一 issue 已修 2+ 环节仍未关闭、或必须真实浏览器/插件/外部站点验证全链路。只加探针和读运行态快照，定位单一断点后再降级。

强制判定：

- `q1_causal_chain` 写清上游源头到用户可见症状的因果链、当前修复点、已验证/失败/未验证链路段，以及运行态是否加载本轮代码。
- `q2_regression_list` 写可能影响的已通过 UAT issue 和用户可见硬契约；跨不同功能区时升级 high-risk。
- `q3_platform_assumptions` 写平台/API/DSL/权限/配置/跨模块契约假设，标注已实测/已查文档/未验证。hard q3 只在新增或改变这些用法时触发；证据限近邻既有模式、官方文档或 runtime probe。含未验证假设时不得进入 fast/scoped 实现。
- 架构缺陷不是 fix 补丁：需要改变模块职责、公共合同、状态归属、数据流、共享抽象或部署边界时，记录证据后回 `$df-plan`。

## high-risk 收窄与止损

`high-risk-fix` 未写 `lane_downgrade_reason` 或 `narrow_patch_reason` 前不得改实现。降级 + 收窄补丁合计不超过 2 次；第 3 次必须止损，用户确认前不得重置。

同一 issue 两次补丁失败、同一方案两次引入新回归、需要第三个 workaround、同一文件/模块在当前 feature 不同 UAT issue 中被修改超过 3 次、或同一 issue 已修过 3 个及以上组件/文件时，立即 checkpoint 并在 `handoff.md` 写 `doom_loop_breaker`。出路只有两个：根因不清切 `integration-debug` 加探针；根因清楚但方案需重设计则回 `$df-plan`。用户确认前流程硬锁。

高风险链路必须定义不可替代的用户可见 runtime gate。项目或 feature 有专用 gate 时必须执行；不可执行时写明阻断原因和人工替代证据，不得关闭 issue。

## 修复流程

1. 确认目标 issue、读取止损区块和引用证据；闸门未满足前只能补运行态证据。
2. 读取 `plan.md`、`validation.md`、`uat.md`、`handoff.md`、相关代码和测试，并只读 `plan.md#Capability Coverage Matrix` 中目标 issue 对应行作为 `coverage_reference`。
3. 找不到对应能力行时，feature lane 或 fix lane 任一为 high-risk 必须暂停，等待用户确认回 `$df-plan`、waiver 或调整 scope；非 high-risk 的 fast/scoped 可按 q1、RED -> GREEN 和回归面关闭。
4. 来自真实环境、浏览器、插件、外部站点、登录态或发布后路径的 issue，先提取历史 GREEN 验证画像：入口、客户端、登录态/插件状态、样本、环境、最后可用基线、runtime gate。
5. 先定 RED：纯逻辑用单测；UAT/runtime/跨模块用真实复现、HTTP 探测、容器检查、页面操作或契约 gate。mock 单测只能补防回归。
6. 跨运行中组件时，改代码前确认源码口径与运行态口径一致；不能确认则先记录漂移风险。
7. 根因明确且未命中止损才修复；根因不清先调查，记录假设、证据和最小复现。
8. 修后复跑目标 issue 的原始动作链；有 `coverage_reference` 时同步核对失败信号、成功判据和不可替代证据。跨组件还必须复跑 runtime gate，再跑最小自动测试、构建和相关门禁。review 调用 `$df-review-loop --uncommitted`，始终传入 `uat_status: RED`，触发 regression-check-only 模式（1 轮，新 P0/P1 in-scope 立即修，P2 waiver）。
9. 结论必须区分“运行态已验证”和“仅代码已改”。只有失败信号消失、review P0/P1 已处理或 waiver、门禁通过且关闭条件满足，才可关闭 issue。
10. 更新 `issues.yaml`、`uat.md`、`state.yaml`、`handoff.md`。`issues.yaml` 只保留当前失败面摘要、状态、最新证据路径、复测标记、`history_ref`；长诊断、review/rework 流水和完整证据写入 `evidence/` 或 `handoff.md`。
11. 每轮修复尝试后必须 git checkpoint，不等 issue 关闭：通过则原子提交；未通过但已改代码则 stash/WIP commit 并记录 hash；止损则立即 checkpoint。checkpoint 后检查 codebase map 命中模块，涉及接口/状态/职责边界时同步 truth doc 或 module map，行为变更时同步 golden sample。
12. 关闭 issue 时若仍等用户复测，写 `needs_retest: true` 或 `retest_status: pending`；关闭且复测通过后，下次 `$df-uat` 或登记 issue 前必须 compact 成 stub。

## 子代理使用

主代理保留 issue 判定、车道分流、q1/q2/q3、止损、关闭 issue、UAT 结论和最终回复；子代理只做边界清楚的定位、窄补丁和验证。`fast-fix` 默认不 spawn；搜索用 `explorer`，明确实现用 `executor`/`worker`，门禁复核用 `verifier`。`high-risk-fix` 未写降级或收窄理由前不得派写业务代码的子代理；`integration-debug` 只能读证据或加探针。当前运行环境若不允许 spawn 子代理，则由主代理按同一边界执行。

## 返工与重复 issue

- `df-fix` 修用户可见失败面，不修技术假设编号。
- 根因变化、补丁失败、复现方式变化：续写同一 issue，禁止新建兄弟 UAT，并重新分流。
- 用户复测仍失败：先判断是否止损、升级 high-risk、切 `$df-regression`，或继续 scoped-fix；不得默认连续手修。
- DOM 隐藏、请求改包、乐观自动提交、浏览器注入类修复命中真实页面时，禁止宽泛祖先选择器或猜测式重写作为最终修复；确需使用时先保存真实快照/选择器证据，并把原用户动作的运行态日志或状态变化列为 runtime gate。
- 自动测试、Playwright harness、源码检查只能作为证据，不得触发新 UAT issue。
- 只有失败面独立或混合 issue 需要拆分时，才允许新建，并写 `related_issue` / `split_from`。
- 关闭 issue 前，如最近 3 条 UAT 指向同一失败面，先合并口径；否则不得进入 `$df-accept`。

## 最终回复

最终回复先给人话状态，再列证据。涉及发布、运行态或 UAT 时，必须明确本地发布是否完成、远端发布是否完成、现在能否直接 UAT、还缺什么；工具链、skill、文档或只读任务只说明“不涉及业务发布/UAT”和下一步。涉及 UAT 且结论不是“可以 UAT”时，必须紧跟“要到可以 UAT 还差什么”，逐条写谁执行、做什么、通过标准、为什么现在不能 UAT。运行态未验证时禁止写“已修复”。
