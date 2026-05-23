---
name: df-uat
description: "用户提到 $df-uat、df-uat、人工验收、记录验收问题、UAT 反馈 intake 或复测时使用。"
metadata:
  short-description: "记录 DevFlow UAT issue"
---

# df-uat

引导当前 feature 的人工 UAT，并把验收过程中发现的问题记录为 feature-local issue。普通 UAT issue 不放进 `devflow/issues/`，除非明确转为跨 feature 或后置问题。

`df-uat` 不只是事后登记问题；它也是人工验收会话入口。应基于当前 feature 的 `uat.md`、`acceptance.md`、`validation.md` 和 `handoff.md`，带用户逐项完成真实环境验收。只有用户反馈出现异常、不符合预期或证据缺失无法关闭时，才生成 issue。

## 流程

1. 读取 active feature。
2. 读取 `uat.md`、`acceptance.md`、`validation.md`、`handoff.md`、`state.yaml`，提取待人工验收项、已完成证据、waiver、当前 UAT 断点和当前阻塞项。`uat.md` scoped reading：有当前断点时，只读该断点 `uat_items` 的详情，其他项只读 id + 状态摘要；无断点时，只读未完成项详情，已通过项只读 id + 状态摘要；覆盖审计只核对每项是否存在和状态，不读详细描述。长 `handoff.md` / `issues.yaml` 同样采用 scoped reading，但当前断点、当前 UAT 项、阻断 issue 和最新证据必须读全。
3. 开始 UAT 前先检查活跃 `issues.yaml`：closed/deferred issue 达到 3 个及以上，或长历史主要来自 closed/deferred issue 时，必须先运行 `uv run python ~/.codex/local/devflow/devflow_cli.py --repo <repo> compact-issues`，校验 YAML 可解析，确认 open / fixed_pending_retest / needs_retest 未被压缩，并确认下一个 UAT id 不会与活跃或历史 id 冲突。若 open/retest issue 本身超过 50 行，不得先 compact；只读当前摘要、最新证据和 `history_ref` 后继续 intake。
4. 先做 UAT 覆盖审计，确认每个 UAT 项都能回指 `plan.md#capability-coverage-matrix` 的用户动作链、下游成功判据、失败信号和不可替代证据。若当前 UAT 的入口、用户动作链或可观察结果在实现与证据中根本不存在，停止引导，在 `handoff.md` 记录 `plan_gap` 或 `execution_gap`，提示回 `$df-plan` 或 `$df-fix`；不得带用户做假 UAT。若当前 `state.yaml status: ready_for_uat` 或 `handoff.md` 写有当前断点，本轮只引导该断点 `uat_items`；不得提前推进后续断点或全量 UAT。没有当前断点时，才按顺序引导所有未完成 UAT。每次只给 1-3 个明确操作步骤，并说明期望看到的结果。
5. 若验收项涉及真实浏览器、真实客户端、本机插件、外部站点、登录态、设备态、账号态或本地缓存/会话，先从已有文档和证据提取"验证画像"：
   - 入口路径：用户如何进入该能力，是手动打开、系统跳转、脚本拉起还是页面内继续操作。
   - 客户端画像：浏览器/客户端品牌、channel、是否真实用户窗口。
   - 会话画像：是否复用用户既有 profile、既有登录态、既有 cookie/storage、既有插件状态。
   - 环境画像：目标环境、网络位置、样本类型、是否真实账号/真实站点。
   - 只有画像缺失时，才补问用户或在 `uat.md`/证据中显式记缺口。
6. 根据用户反馈判断：
   - 通过：记录该项已通过；若当前断点内还有未完成 UAT 项，直接提示下一项的 1-3 个操作步骤和期望结果；不要跳到后续断点。
   - 不通过：提取 issue 标题、现象、严重度；严重度只能是 `low`、`medium`、`high`、`critical`。
   - 信息不足：要求用户补充最小必要证据，例如截图、页面文字、控制台错误、请求响应或具体复现步骤。
   - 越界试测：按"非当前 UAT 项反馈"处理。
7. 需要记录 issue 前，必须先执行"Issue 去重与重开规则"；只有确认不是既有 issue 的同一用户可见问题，才运行：
   `uv run python ~/.codex/local/devflow/devflow_cli.py --repo <repo> uat "<标题>" "<现象>" --severity <low|medium|high|critical>`
8. 回复生成的 issue id，并继续完成本轮用户反馈 intake；没有 issue id 时禁止转修。
9. 本轮反馈全部登记、去重、重开和落盘完成后，按"Issue 后续判定"明确是进入 `$df-fix <issue-id>`，继续当前断点下一项 UAT，还是当前断点已通过后回 `$df-execute`。
10. 若判定需要进入 `$df-fix <issue-id>`，必须立即读取 `df-fix` skill 并按其流程继续；禁止在 `$df-uat` 语境下直接修改实现文件。

脚本会拒绝非法严重度，不要用 `urgent`、`blocker` 等临时值绕过枚举。

不要把 UAT issue 单独升级为 debug 阶段；只有根因不清时才进入调查模式。

## Issue 去重与重开规则

- UAT issue 按用户可见失败面划分，不按技术根因、补丁方案、代码位置或 harness 划分。
- 新建 issue 前必须查 `issues.yaml` 最近和相关 issue。
- 同一失败面已有 open issue：禁止新建，续写原 issue。
- 同一失败面已有 closed issue 且复测失败：重开或追加 `regression`，禁止新建。
- 只有用户可见失败面独立时才允许新建。
- 拆分混合 issue 时必须写明 `split_from` / `related_issue`。
- 若 `issues.yaml` 是活跃上下文视图，必须同时查 active stub 的 `history_ref`、`evidence/*history*.yaml` 和 `evidence/*full*.yaml`，避免历史已关闭问题被重复新建。
- `review-findings.yaml` 是 review finding 正本；新 review finding 不得写入 `issues.yaml`。遗留 `REVIEW-*` 只允许作为历史压缩对象迁移到 `evidence/`。
- `issues.yaml` 中的 gate、investigation、regression_guard_contract 只写文件路径 + 通过/失败结论，不重新描述脚本内部判定逻辑。
- 用户说"通过/正常"时，先确认对应 issue id；未确认时不得擅自关闭新 issue。
- 标题写用户现象；技术细节写 `investigation`。

## Issue 分层与归档

`issues.yaml` 应保持为当前 UAT 的活跃工作集，而不是完整修复流水账。目标是让 agent 每次进入 UAT 时能快速看清"现在还卡什么"，同时不丢失历史证据。

- 活跃文件只保留 open issue、刚关闭但仍需复测的 issue、当前断点、最新证据和 `history_ref`。
- 长修复历史、旧 investigation、过期尝试、完整 timeline 和大量证据清单应归档到 `evidence/` 下的历史文件，例如 `evidence/uat-xxx-full-history.yaml`。
- 归档前必须确认历史文件可追溯原始 issue id、状态、关键证据和迁移时间；归档后在活跃 issue 写 `history_ref`。
- 不得为了压缩而删除正式记录；只能迁移到 feature-local `evidence/` 或等价正式证据目录。
- 新增或重开 issue 时，只在活跃 `issues.yaml` 写当前失败面和最新证据；旧轮次细节继续追加到历史文件或专门 evidence 文件。
- `$df-uat` 开始阶段和登记新 issue 前，如果 closed/deferred issue 达到 3 个及以上，或长历史主要来自 closed/deferred issue，必须先做分层压缩再继续；这是硬阻断，不是建议。open / fixed_pending_retest / needs_retest issue 即使超过 50 行也不得被前置压缩，只能 scoped read 并继续当前 UAT / fix。
- 分层压缩优先使用 helper：`uv run python ~/.codex/local/devflow/devflow_cli.py --repo <repo> compact-issues`。
- 分层后必须校验 YAML 可解析，确认 open / fixed_pending_retest / needs_retest issue 未被压缩，并确认下一个 UAT id 不会与活跃或历史 id 冲突。

## 非当前 UAT 项反馈

用户可能在当前 UAT 中顺手测试到后续 UAT 项，尤其是当前 feature 存在分段 UAT-ready 断点时。处理顺序：

1. 先判定归属：当前 UAT 项、后续 UAT 项提前覆盖、后续 UAT 项 issue、信息不足。
2. 如果是后续 UAT 项提前覆盖，只在 `uat.md` 记录动作与证据；只有用户明确反馈该项通过，才关闭该项。
3. 如果是后续 UAT 项 issue，登记 issue，标题写清所属 UAT 项，并在 `issues.yaml` 写 `checkpoint_scope: future_checkpoint` 和对应 `uat_items` / `source_uat_items`；不算当前 UAT 项失败。
4. 登记后提醒用户先收口当前 UAT；不要跟随用户切到后续阶段，也不要自动 `$df-fix`，除非该 issue 阻断当前 UAT 或用户明确要求暂停当前 UAT 去修。

## 分段 UAT-ready 断点

- 当前断点来源只读 `state.yaml`、`handoff.md` 和 checklist item 的 `uat_ready` 元数据；`df-uat` 不规划新断点，不重排 `uat_items`。
- 当前断点 UAT 全部通过或 waiver，且仍有 pending / in_progress checklist item 时，把 `state.yaml status` 写回 `ready_for_execute`，用 `df-status --clear-context` 保存 handoff，写明已通过的 `uat_items` 和下一条 pending DF，并提示用户继续 `$df-execute`。
- 当前断点 UAT 全部通过或 waiver，且 checklist 已全部 done/waived、所有 UAT 均完成且无 open/retest issue 时，先把 `state.yaml status` 从 `ready_for_uat` 写为 `validated`，用 `df-status --clear-context` 保存 handoff，写明当前 UAT 断点已清除、全部 `uat_items` 已通过或 waiver，再提示进入 `$df-accept`。
- 断点通过判定：`issue.status in {open, fixed_pending_retest}` -> 阻断；`needs_retest: true` -> 阻断；`retest_status: pending` -> 阻断；`checkpoint_scope: future_checkpoint` 且 `uat_items` 不属于当前断点 -> 不阻断但保留到后续断点；缺少 scope 的 open/retest issue -> 默认阻断；其他情况才可通过。阻断时按严重度进入 `$df-fix <issue-id>` 或继续补当前断点证据。
- 旧 feature 没有 `uat_ready` 断点时保持原语义：按 `uat.md` 顺序引导全部人工 UAT，全绿后提示 `$df-accept`。

## 本轮反馈 intake 硬闸

`$df-uat` 首要职责是把用户本轮反馈的所有 UAT 问题完整记录下来。用户一次给出多个异常、截图、会话现象、字段错误或复测结论时，必须先完成整批 intake，禁止登记第一个高严重度 issue 后立刻转修。

- 先把本轮反馈拆成用户可见失败面清单；逐项判断当前 UAT 项、后续 UAT 项、既有 issue 重开、同一失败面续写或信息不足。
- 对每个失败面完成去重、登记或重开，并同步更新 `issues.yaml`、`uat.md`、`handoff.md`、`state.yaml` 中必要的 UAT 记录。
- 本轮反馈仍有未处理项、未确认归属、未落盘 issue 或需要补最小证据时，禁止进入 `$df-fix`。
- 用户明确说"先只读"、"只记录"、"先把 issues 落盘"、"不要修"时，完成记录后必须停下，只给 issue 清单和建议下一步，不得转修。
- 只有本轮反馈 intake 完成后，才允许按严重度和阻断关系选择一个明确 issue id 进入 `$df-fix <issue-id>`。

## Issue 后续判定

- `critical/high`、前置能力失败、会污染后续证据：先完成本轮反馈 intake；若用户未要求只记录，intake 完成后进入 `$df-fix <issue-id>` 修复；不得在 `$df-uat` 流程内直接改实现文件，不得把"先修再补记录"当作合格闭环。
- 登记 `critical/high` 时，如已定位根因或有明确嫌疑，把 `causal_hint`、`affected_files`、`reproduction` 写入 issue 可选字段，减少 `$df-fix` 重复理解成本。
- `low/medium`、独立且不影响后续证据：可以继续下一条 UAT，并说明为什么不阻断。
- 信息不足：先补最小证据，不继续也不修。

## 自动转修边界

- UAT 中允许修阻塞项，但必须先完成本轮反馈 intake，再显式切到 `$df-fix <issue-id>` 流程；禁止先修后补 issue，禁止只登记部分反馈就开修。
- 即使根因明显，也禁止"顺手修"：不得跳过 `$df-fix` 的读取、修复、门禁、记录闭环。
- `$df-uat` 本身只允许读取证据、引导复测、登记 issue、更新 UAT 记录；实现代码、工作流、服务配置改动必须发生在 `$df-fix`。
- 进入 `$df-fix` 前必须给用户一句状态切换说明，并列出本轮已登记/续写/重开的 issue 清单，例如"本轮反馈已全部登记：UAT-001、UAT-002；现在按 df-fix 修复 UAT-001"；随后按 `df-fix` 的强制接管规则执行。

### fix_context_card

进入 `$df-fix` 前，必须在 `handoff.md` 写入或替换唯一的 `## fix_context_card`，不超过 20 行。最少包含 `target_issue`、`severity`、`failure_surface`、`current_breakpoint`、`coverage_matrix_row` 或 `coverage_reference`、`reproduction`、`uat_progress`，可选写 `causal_hint` 和 `affected_files`。未知字段写 `unknown`；不得为补卡片重读全量长文件。

## 引导原则

- 待验证项不等于 issue；只有用户反馈异常或证据缺失时才登记。用户说"通过"则继续下一项，说"不知道怎么验"则给更具体步骤。
- 涉及真实运行路径的 UAT，默认复用既有验证画像；改变画像时必须标注"探索性验证"，结果不覆盖原 UAT 口径。
- `uat.md` 中的 UAT 项应标注 `uat_phase`：首测写 `first_pass`，修复后复测写 `retest`。首测发现 bug 是正常 intake；复测阶段若发现同类新 bug，应在 issue 中标记 `regression_pattern`，并提示 `$df-fix` 评估能否前移为机器门禁。
- 当前项通过后自动引导下一项；引导时区分"期望结果"和"不符合时请反馈什么"。

## UAT 覆盖审计

开始引导前，交叉检查 `plan.md#capability-coverage-matrix`、`checklist.yaml`、`validation.md`、`handoff.md`、`issues.yaml` 与 `uat.md`，确认每个用户可见能力和真实运行路径都有对应 UAT 项，且 UAT 操作步骤与矩阵里的用户动作链、下游成功判据、失败信号一致。当前断点只要求当前 UAT 对应能力已经真实存在；所有 UAT 全部通过后，才要求它们合起来覆盖 `plan.md#目标`。

必须先补 `uat.md` 再继续引导的情况：`uat.md` 仍是初始模板；用户可见能力只有机器证据没有人工 UAT 项；涉及真实浏览器/官网/插件/Dify 发布/ERP 写入的路径没有真实环境 UAT 项；已关闭 issue 没有复测记录；高风险能力没写清验证画像；UAT 只写“确认正常”“入口可用”“显示合理”等无法证明能力的虚验收。

补项时只补同一 `Capability Coverage Matrix` 对应的 UAT 项，写清操作步骤、期望结果、失败信号和不可替代证据；高风险项同时写最小验证画像（入口、客户端、profile/登录态、目标环境、样本）。机器证据不替代人工 UAT 通过。用户明确不做某项时记录 waiver 和残余风险；高风险核心能力 waiver 后不得建议 `$df-accept`。前置核心路径的缺口优先引导。

## 下一步

- UAT 全部通过且无 open issue 时，提示进入 `$df-accept`。
- 有 open issue 时，按严重度进入 `$df-fix <issue-id>` 或继续下一项 UAT；修复后回到 `$df-uat` 复测。
