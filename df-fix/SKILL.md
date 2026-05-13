---
name: df-fix
description: "对 DevFlow UAT issue 执行 plan → execute → validate → UAT 闭环；根因清楚时直接修复，根因不清时先调查。用户提到 $df-fix、df-fix、修 UAT issue、修 open issue 时使用；在 $df-uat 中登记 critical/high issue、阻断当前 UAT 的 issue、或用户反馈 UAT 失败后需要改实现时也必须自动使用。"
metadata:
  short-description: "修复 DevFlow UAT issue"
---

# df-fix
围绕当前 feature 的 `issues.yaml` 修复 UAT issue。
## 强制接管
- 当前 feature 存在 open UAT issue 时，禁止“顺手修”实现文件；必须先进入本 skill。
- 从 `$df-uat` 转修前，必须先完成本轮反馈 intake 并明确 issue id；用户要求修刚登记的 UAT issue 时，切到 `$df-fix <issue-id>`。
- 先读取 `issues.yaml` 并明确目标 issue id；没有目标 id 时只能调查和登记 issue，不能改实现文件。
- 已先做补丁但未完成本流程时，不得声明完成；必须补齐真实 RED、修复验证、门禁和 DevFlow 记录后才允许关闭 issue。
- 本 skill 闭环优先级高于继续 UAT；关闭 issue 后再回 `$df-uat`。

## 能力边界
即使当前项目环境可操作真实浏览器和容器，跨 3+ 运行中组件、运行态漂移、或同一 issue 已跨 3+ 组件/文件修过仍未关闭时，也已超出单次会话的有效操作半径。此类问题切 `integration-debug`：只加探针和读运行态快照，定位单一断点后才能降级修复，禁止边修边验、修一环看一环。

## 车道分流
读取目标 issue 后锁定 `issue_scope`，读取 `codebase_map/OVERVIEW.md` 并只读命中的模块卡片。随后用排除法分流，并在 `issues.yaml` 或 `handoff.md` 的本轮最新段落写入 `map_modules_read`、`fix_lane`、`lane_reason`、`q1_causal_chain`、`q2_regression_list`、`q3_platform_assumptions`；fast-fix 快速路径只需先写 `q1_causal_chain`。未落盘前不得改实现文件。分流后用 `[绿灯] fast-fix`、`[黄灯] scoped-fix`、`[红灯] integration-debug/high-risk-fix` 向用户报告。

### 防钻空子
- `q1/q2/q3` 必须写入持久记录（`issues.yaml`、`handoff.md`、`uat.md` 或 evidence），每轮必须针对本轮 RED 更新；fast-fix 可省 q2/q3，验证失败升级前必须补齐。
- 改代码前诊断字段 + `fix_lane` 必须已落盘；缺任一项只能调查不能改实现文件。

| 车道 | 适用条件 | 动作 |
|------|----------|------|
| `integration-debug` | 跨 3+ 运行中组件的端到端链路问题；同一 issue 已修 2+ 环节但仍未关闭；需要真实浏览器/插件/外部站点才能验证全链路 | 只加探针不改业务代码。给用户探针步骤 → 用户跑 → AI 读数据 → 定位单一断点后降级为 scoped/high-risk 单点修复 |
| `high-risk-fix` | 跨 Dify/插件/Broker/`nas-agent`/`erp-executor`/容器/发布链路；验收口径或职责边界变化；真实浏览器/登录态/外部站点/发布后路径；post-acceptance；`fetch` 改包、DOM 猜测、乐观渲染修正、本地气泡改字；回滚/撤销/重写已通过用户验收的修复 | 只调查、登记证据；若确认是单点错误，按 high-risk 收窄闸门处理，否则回 `$df-plan` |
| `fast-fix` | 仅文案、样式、单组件展示、单函数纯逻辑或测试断言补漏，且不命中高风险 | 最小 RED、最小修复、targeted 验证 |
| `scoped-fix` | 默认车道：当前 feature 影响面内的受控回归 | 写回归面清单，同一路径复现，修后跑 targeted test、构建和相关门禁 |

若 UAT issue 暴露的是架构缺陷，而不是单点实现错误，例如需要改变模块职责、公共合同、状态归属、数据流方向、共享抽象或部署边界，`df-fix` 只能记录证据和止损结论，随后回 `$df-plan` 走 architecture adjustment；不得把架构重设伪装成 fix 补丁。

强制判定问题：
- `q1_causal_chain`：描述从最上游源头到用户可见症状的因果链、当前修复点位置、是否能改在更上游；必须写清已通过/已失败/未验证的链路段，以及运行态是否已加载本轮代码。
- `q2_regression_list`：列出本次修改可能影响的已通过 UAT issue 和用户可见硬契约；跨不同功能区域时升级 `high-risk-fix`。
- `q3_platform_assumptions`：列出对平台/API/DSL/权限/配置/跨模块契约的假设，标注已实测/已查文档/未验证；含未验证假设时不得进入 `fast-fix` 或 `scoped-fix`。
- hard q3 仅在修复依赖新增或改变上述用法时触发；不要求全库扫描，只查相关文件、相邻模块、codebase map 命中模块或调用链近邻。
- hard q3 证据仅限近邻精确既有模式、官方文档或 runtime probe；mock 单测不能证明平台能力存在。
- 找不到证据时写 `unverified_platform_use`，只能调查或加 probe，不得实现。

`q1/q2/q3` 应体现 codebase map 中的结构、接口和风险，但不新增额外必填字段。map 命中风险不自动等于 `high-risk-fix`；scope 外风险只登记为 `scope_expansion_request`，不能直接扩大改动。

### high-risk 收窄闸门
`high-risk-fix` 默认不得改实现文件。可通过以下方式收窄，但有次数限制：
- 正式降级：写 `lane_downgrade_reason` 后降为 `scoped-fix`。
- 收窄补丁：保持 `high-risk-fix`，写 `narrow_patch_reason` 后做单点修复。

同一 issue 的降级 + 收窄补丁合计不超过 2 次。第 3 次起必须触发止损出路，不得再使用降级或收窄补丁。止损触发后降级/收窄计数器归零但同时锁定，只有用户确认后才能重置。未写理由前，在 high-risk 车道只能读代码、跑探针、登记证据。

止损规则：同一 issue 两次补丁失败、同一方案两次产生新回归、需要第三个 workaround、同一文件/模块在当前 feature 的不同 UAT issue 中被修改超过 3 次、或同一 issue 已分别修过 3 个或更多不同组件/文件时，必须立即 git checkpoint 并在 `handoff.md` 写入 `doom_loop_breaker`（最后 GREEN、当前 RED、差异表、恢复权限条件），然后**流程硬锁**。出路二选一且需用户确认后才恢复改代码权限：根因不清/链路断点未定位则切 `integration-debug` 只加探针；根因已清但方案需重设计则回 `$df-plan`。

止损文档必须写入 `handoff.md`，下一轮必须先读止损区块。跨组件链路止损后，必须先画完整链路证据表再动手，单测/构建不替代运行态探针。

高风险链路必须定义一个不可替代的用户可见 runtime gate；项目或 feature 已定义专用 gate 时必须作为阻断条件执行。gate 不可执行时写明阻断原因和人工替代证据，不得关闭 issue。

## fast-fix 快速路径
当 `fix_lane=fast-fix` 时只走 4 步：确认 issue 并写 1 行 `q1_causal_chain`；改代码并跑 targeted test；只暂存相关文件做原子提交；关闭 `issues.yaml` 后回 `$df-uat`。验证失败立即升级 `scoped-fix` 走标准流程，不需要读取全部 plan/validation/handoff 或写运行态证据分级。

## 子代理使用

主代理保留 issue 判定、车道分流、`q1/q2/q3`、止损、关闭 issue、UAT 结论和最终回复；子代理只做边界清楚的定位、窄补丁和验证。

### 分派规则

- `fast-fix` 默认不 spawn；除非需要跨多文件搜索定位。
- 主代理直接执行的默认条件：≤ 2 文件且 ≤ 30 行且不需要搜索定位。
- 搜索、定位、比较、历史证据梳理 → spawn `explorer`。
- `scoped-fix` 中根因明确且实现代码 > 2 文件或 > 30 行 → spawn `executor`（回退 `worker`）。
- `high-risk-fix` 未写 `lane_downgrade_reason` 或 `narrow_patch_reason` 前，只能 spawn `explorer` / `verifier`，不得 spawn 写业务代码的子代理。
- `integration-debug` 只能 spawn 只读 `explorer`；如需写入，仅允许 `executor` 添加探针，不得改业务逻辑。
- 跑门禁、审查 diff、复核运行态 gate → spawn `verifier`。
- 触发止损、影响面超过当前 plan、或需要重设计 → 回 `$df-plan`；必要时 spawn `planner`，不得继续派 executor 补丁。

### 并发

- 并发只用于只读任务，或写入边界完全不重叠的窄补丁。
- 同一用户可见失败面的核心修复不得并发多个 executor。
- 默认 `fork_context=false`，只传最小上下文包。
- 子代理完成且不再复用时必须回收。

## 流程
以下流程适用于 `scoped-fix` 和 `high-risk-fix`；`integration-debug` 只能加探针/读证据，`fast-fix` 走快速路径。
1. 读取 `issues.yaml` 中 open issue，确认目标 issue。
2. 若目标 issue 为 `high-risk-fix` 或 `handoff.md` 含止损 checkpoint，先读止损区块和引用证据；闸门未满足前只能补运行态证据。
3. 读取 `plan.md`、`validation.md`、`uat.md`、`handoff.md`、相关代码和测试，按“车道分流”定 lane。
4. 来自真实环境、浏览器、插件、外部站点、登录态或发布后路径的 issue，先提取历史 GREEN 验证画像：入口、客户端、登录态、插件状态、样本、环境、最后可用基线、runtime gate。
5. 先定 RED：纯逻辑可用单测；UAT/runtime/跨模块必须用真实复现、HTTP 探测、容器检查、页面操作或契约 gate 击中失败面；mock 单测只能补防回归。
6. 跨运行中组件的 issue，改代码前确认源码口径和运行态口径是否一致；无法确认时先把漂移风险写入证据表。
7. 改代码前确认诊断字段 + `fix_lane` 已落盘且与本轮 RED 一致；根因明确且未命中止损则修复，根因不清先调查并记录假设、证据和最小复现。
8. 修复后先复跑触发 issue 的同一真实步骤；跨组件链路还必须复跑不可替代 runtime gate，再按回归面清单跑最小自动测试、构建和对应门禁。
8b. 跨组件 issue 验证结论必须标注每个环节是运行态已验证还是仅代码已改；只有代码证据时不得写“已修复”，只能写“代码已改，运行态未验证”。凡是用户可见回归（q2 契约中列出的）在最终载体中出现，直接判 RED。
9. 提交前确认已通过 UAT 的代码不受影响；有专用门禁时必须引用其 pass/fail 结果。
10. 更新 `issues.yaml`、`uat.md`、`state.yaml`、`handoff.md`，证据区分真实复现/运行态验证、自动测试/门禁、回归面覆盖、验证画像是否一致；不得把未覆盖的面写成已通过。若结论不是“可以 UAT”，必须在记录中补 `uat_unlock_next_steps` 或等价段落，写清进入 UAT 还差的最小动作、执行主体、样本/命令/页面、通过标准和阻断原因；禁止只写“不建议 UAT”“运行态未验证”“待复测”这类不可执行结论。
11. **每轮修复尝试后必须 git checkpoint**，不等 issue 关闭：通过则原子提交 `fix(<issue-id>): <一句话描述>`；未通过但已改代码则 stash/WIP commit 并把 hash 写入 `handoff.md`；止损触发则立即 checkpoint；提交前只暂存该 issue 相关文件；禁止连续两轮修复之间没有任何 checkpoint。
11b. git checkpoint 后，检查本轮修改路径是否命中 `codebase_map/OVERVIEW.md` 卡片索引中的模块；命中则增量刷新对应模块卡片。
11c. 本轮改动涉及模块接口、状态归属或职责边界时，同步更新 `docs/design/system_framework_truth.md` 或对应 module_map。
11d. 修复改变了业务行为时，更新 `devflow/shared/golden_sets/` 中受影响的样本。
12. 最终回复必须先用人话给状态结论，再列证据。第一段固定回答：本地发布是否完成、远端发布是否完成、现在能否直接 UAT、还缺什么；禁止先堆命令、hash、测试清单或 DevFlow 术语。随后再写 UAT 状态（`可以 UAT` / `暂不建议 UAT` / `只完成代码验证`），紧跟对象限定（业务故障 / 门禁 / 运行态 / 文档）。可以 UAT 时写 1-3 条用户具体操作和期望结果。只要不是“可以 UAT”，必须紧跟一个“要到可以 UAT 还差什么”清单，逐条写明：
   - `谁执行`：agent 继续执行、用户手动操作，或需要用户授权/登录。
   - `做什么`：具体命令、页面动作、样本输入、发布/重载/刷新步骤。
   - `通过标准`：必须看到的会话导出字段、页面状态、日志、hash、测试结果或用户可见结果。
   - `为什么现在不能 UAT`：指出缺的是发布、生效确认、真实浏览器 gate、远端 gate、登录态、样本、权限还是用户人工确认。
   禁止只写“不建议 UAT”“还需验证”“等复测”“运行态未验证”而不写可执行解锁步骤。运行态未验证时禁止写“已修复”。

修复完成不等于最终验收；最后仍需 `$df-accept`。

## 返工与重复 issue 规则

- `df-fix` 修用户可见失败面，不修技术假设编号。
- 根因变化、补丁失败、复现方式变化：续写同一 issue，禁止新建兄弟 UAT，并重新分流。
- 用户复测仍失败：先判断是否触发止损、升级 `high-risk-fix`、切到 `$df-regression`，或继续 `scoped-fix`；不得默认连续手修。
- DOM 隐藏、请求改包、乐观自动提交、浏览器注入类修复命中真实页面时，禁止使用宽泛祖先选择器或猜测式重写作为最终修复；若必须使用，需先保存真实页面快照/选择器证据，并把“原用户动作仍能产生运行态日志或状态变化”列为 runtime gate。
- 自动测试、Playwright harness、源码检查只能作为证据，不得触发新 UAT issue。
- `handoff.md` 中的门禁结论只写脚本路径 + PASS/FAIL + 关键输出，不重新描述脚本内部判定逻辑。
- 修改门禁脚本、状态码语义或接口契约后，必须同步清理 checklist/issues/handoff 中同一行为的重复描述；未同步不得关闭 issue。
- 只有失败面独立或混合 issue 需要拆分时，才允许新建；必须写 `related_issue` / `split_from`。
- 关闭 issue 前，如最近 3 条 UAT 指向同一失败面，先合并口径；否则不得进入 `$df-accept`。
