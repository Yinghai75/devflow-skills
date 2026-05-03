---
name: df-fix
description: "对 DevFlow UAT issue 执行 plan → execute → validate → UAT 闭环；根因清楚时直接修复，根因不清时先调查。用户提到 $df-fix、df-fix、修 UAT issue、修 open issue 时使用；在 $df-uat 中登记 critical/high issue、阻断当前 UAT 的 issue，或用户反馈 UAT 失败后需要改实现时也必须自动使用。"
metadata:
  short-description: "修复 DevFlow UAT issue"
---

# df-fix

围绕当前 feature 的 `issues.yaml` 修复 UAT issue。

## 强制接管

- 一旦当前 feature 存在需要修复的 open UAT issue，禁止“顺手修”实现文件；必须先进入本 skill。
- 从 `$df-uat` 登记 `critical/high` issue、阻断当前 UAT 的 issue，或用户明确要求修刚登记的 UAT issue 时，立即停止 UAT 引导并切到 `$df-fix <issue-id>`。
- 切到本 skill 后，先读取 `issues.yaml` 并明确目标 issue id；没有目标 issue id 时只能调查和登记 issue，不能改实现文件。
- 已经先做了补丁但尚未完成本流程时，不得把它声明为已完成；必须补齐真实 RED、修复验证、门禁和 DevFlow 记录后，才允许关闭 issue。
- 本 skill 的闭环优先级高于继续 UAT；修复关闭后再回到 `$df-uat` 继续下一项。

## 三车道分流

读取目标 issue 后先用排除法分流，并在 `issues.yaml` 或本轮记录中写入 `fix_lane`、`lane_reason`、`q1_causal_chain`、`q2_regression_list`、`q3_platform_assumptions`；未记录前不得改实现文件。分流后用 `[绿灯] fast-fix`、`[黄灯] scoped-fix`、`[红灯] high-risk-fix` 向用户报告。

| 车道 | 适用条件 | 动作 |
|------|----------|------|
| `high-risk-fix` | 跨 Dify/插件/Broker/`nas-agent`/`erp-executor`/容器/发布链路；验收口径或职责边界变化；真实浏览器/登录态/外部站点/发布后路径；post-acceptance；`fetch` 改包、DOM 猜测、乐观渲染修正、本地气泡改字；回滚/撤销/重写已通过用户验收的修复 | 只调查、登记证据并回 `$df-plan`；若调查确认是单点错误且不扩大影响面，可记录 `lane_downgrade_reason` 后降为 `scoped-fix` |
| `fast-fix` | 仅文案、样式、单组件展示、单函数纯逻辑或测试断言补漏，且不命中高风险 | 最小 RED、最小修复、targeted 验证 |
| `scoped-fix` | 默认车道：当前 feature 影响面内的受控回归 | 写回归面清单，同一路径复现，修后跑 targeted test、构建和相关门禁 |

强制判定问题：

- `q1_causal_chain`：描述从最上游源头到用户可见症状的因果链、当前修复点位置、是否能改在更上游；若不修上游，说明原因。
- `q2_regression_list`：列出本次修改可能影响的已通过 UAT issue；若清单跨不同功能区域，升级 `high-risk-fix`。
- `q3_platform_assumptions`：列出对 Dify/React/Edge/浏览器 API 等平台行为的假设，并标注已实测、已查文档或未验证；含未验证假设时不得进入 `fast-fix` 或 `scoped-fix`。

止损规则：同一 issue 两次补丁失败、同一方案两次产生新回归、需要第三个 workaround、或同一文件/模块在当前 feature 的不同 UAT issue 中被修改超过 3 次，必须升级 `high-risk-fix`。回 `$df-plan` 的目的不是让 AI 自我循环，而是制造人工检查点：必须展示因果链、修复点和平台假设验证状态，等待用户确认后才能回到 `$df-fix` 执行。

## 流程

1. 读取 `issues.yaml` 中 open issue，确认目标 issue。
2. 读取 `plan.md`、`validation.md`、`uat.md`、`handoff.md`、相关代码和测试，按“三车道分流”定 lane。
3. 若 issue 来自真实环境、真实浏览器、本机插件、外部站点、登录态或发布后路径，先从历史 GREEN 提取“验证画像”：入口、客户端/浏览器、profile/登录态、cookie/storage、插件状态、样本类型、目标环境；历史 GREEN 没写清时先补记录。
4. 先定 RED：纯逻辑可先单测；UAT/runtime/跨模块必须先用真实复现、HTTP 探测、容器检查、页面操作或契约 gate 击中失败面；mock 单测只能补防回归。
5. 真实复现默认复用历史 GREEN 同一验证画像；若改变画像做对比实验，证据必须标注“探索性验证/对比验证”，且不能替代同路径复测。
6. 根因明确且未命中止损则修复；根因不清先调查并记录假设、证据和最小复现，不得用会通过的测试代替调查。
7. 修复后先复跑触发 issue 的同一真实步骤，再按回归面清单跑最小自动测试、构建和对应门禁；注册门禁必须用 `run-gate` 生成 `evidence/manifest.json`。
8. 提交前自检本次改动是否碰到已通过用户验收的代码；若碰到，逐项确认对应验收条件仍成立，否则在 `issues.yaml` 记录回归风险或重开相关 issue。
9. 更新 `issues.yaml`、`uat.md`、`state.yaml`、`handoff.md`，证据区分真实复现/运行态验证、自动测试/门禁、回归面覆盖、验证画像是否一致；不得把未覆盖的面写成已通过。
10. 每个 UAT issue 默认一个原子修复提交；提交前检查 `git status --short`，只暂存该 issue 的修复、测试和证据文件，不混入无关改动或用户明确保留的不提交文件。

修复完成不等于最终验收；最后仍需 `$df-accept`。

## 返工与重复 issue 规则

- `df-fix` 修用户可见失败面，不修技术假设编号。
- 根因变化、补丁失败、复现方式变化：续写同一 issue，禁止新建兄弟 UAT，并重新分流。
- 用户复测仍失败：先判断是否触发止损、升级 `high-risk-fix`、切到 `$df-regression`，或继续 `scoped-fix`；不得默认连续手修。
- 自动测试、Playwright harness、源码检查只能作为证据，不得触发新 UAT issue。
- 只有失败面独立或混合 issue 需要拆分时，才允许新建；必须写 `related_issue` / `split_from`。
- 关闭 issue 前，如最近 3 条 UAT 指向同一失败面，先合并口径；否则不得进入 `$df-accept`。
