---
name: df-plan
description: "为当前 DevFlow feature 编写人读版 plan.md、checklist.yaml 和 validation.md；强制高风险任务生成 Blast Radius Guard、TDD/RED 证据要求和门禁选择。用户提到 $df-plan、df-plan、DevFlow 计划时使用。"
metadata:
  short-description: "编写 DevFlow 计划"
---

# df-plan

为 `devflow/active/<date-slug>/` 生成可执行、可恢复的人读版计划。正本是文档，不是 executor prompt。

## 输入

1. 读取 `devflow/active/.current` 指向的 feature；若不存在，选择最新 active feature。
2. 读取 `context.md`、`state.yaml`、`devflow/shared/gate_registry.yaml`。
2b. 若本次 `df-plan` 是从 `df-fix` 止损升级进入的（`handoff.md` 含止损 checkpoint hash 或 `fix_lane=high-risk-fix`），必须先读取 `handoff.md` 的止损区块，包括链路状态表、闸门条件清单和 `evidence/` 中引用的止损文档。新方案必须基于止损证据设计，不得从头规划；向用户展示方案时必须同时展示止损闸门的 ✅/❌ 状态。
3. 涉及主链、长尾链、官网子链、`nas-agent`、`erp-executor`、容器职责边界、状态机或跨模块编排时，先使用 `framework-truth-guard` 对齐边界。
4. 使用 `df-codebase-map` 按 `context.md` 的 scope 检查并读取命中 units，顺序固定为 `manifest.yaml → scope 命中的 units → local files`；禁止全文读取整个 map 目录。
5. 如果 scope 不够，先补 scope 或在 `context.md`/`plan.md` 记录 waiver，不得边扩边规划实现。
6. 新功能、行为变更和 bugfix 必须在计划中先写 RED 证据步骤：失败测试、失败 golden sample、历史故障复现或明确的人工复现脚本。
7. 读取 `context.md` 的 `target_env`；目标环境为 `dev-full`/`online`，或任务涉及 Dify 发布、容器、线上对象时，必须把发布闭环写入 checklist。
8. 如果 `context.md` 或用户原始输入显示这是长目标的一部分，读取并维护 `devflow/roadmap.md`；没有该文件时先补建，列出当前 feature 和后续 feature backlog。

## 轻量探索

`df-plan` 必须内置轻量探索纪律，但不创建额外规格目录，不提交设计文档，也不转入其他计划 skill。

- 目标、非目标、约束、成功标准不清时，先问用户；每次只问最关键的一个问题。
- 方案存在真实灰区且会被 `plan.md` 锁定时，必须先进入文本讨论：用普通文本列出 1-3 个编号问题、每题给出 2-3 个可选方案和取舍，然后停下来等待用户回复。即使当前环境不能使用 `request_user_input` 控件，也不得把控件不可用解释为默认同意或自动选择。
- 已由用户原话、`context.md`、`roadmap.md`、上游计划或已完成 feature 明确锁定的决定不得重复询问；只讨论仍未锁定且会影响范围、方案、风险、验收或发布闭环的灰区。
- 若 `roadmap.md` 或 `context.md` 中出现“待规划问题”“待确定”“建议”“候选”“可选”等未锁定表述，默认视为需要文本讨论，除非用户显式要求自动规划。
- 文本讨论不是自动模式。除非用户在同一轮明确要求“直接规划”“自动选择”“全自动推进”或等价表述，否则必须等用户回复后再落盘或更新正式计划文件。
- 对 fast 车道且只有低风险实现细节不确定的任务，可以在 `plan.md` 写“执行期可调整假设”；但不得把产品行为、职责边界、目标环境、发布范围、数据来源或门禁豁免当作低风险细节直接默认。
- 方案比较前先对照 `docs/design/system_framework_truth.md` 的「禁止集成模式」（F1-F4）；命中任一条的方案必须被替换为替代方案，不得以「能 work」或「最直接」为由选择禁止模式。
- 方案不唯一时，在 `plan.md` 写 2-3 个可行方案、取舍理由、推荐方案和放弃方案。
- 对高风险任务，方案比较必须覆盖影响面、可回滚性、验证成本和失败后果。
- 对 fast 车道的小改动，可以用一段“方案与取舍”代替完整多方案表。
- 对长 plan，不强制使用 phase 命名；可以拆成多个 feature。关键是保留完整后续 backlog，不得只规划 POC 或第一段。

## 必写内容

更新：

- `plan.md`：目标、非目标、方案、任务拆分、风险、验收标准。
- `checklist.yaml`：可逐项执行的任务，包含 `id`、`title`、`status`、`owner`、`paths`、`validation`。
- `validation.md`：基础验证和 Blast Radius Guard。
- `state.yaml`：必须写入 `status: planned` 或 `status: ready_for_execute`，并写入 `execution_authorized: false`；这是计划落盘后的默认状态。
- `handoff.md`：当前断点与下一步，必须明确“等待用户显式 `$df-execute` 或等价执行授权”。
- `uat.md`：人工 UAT 覆盖矩阵；高风险 feature 不允许只保留初始模板。
- `devflow/roadmap.md`：当任务来自长 plan 时，记录总目标、当前 feature、后续 feature backlog、每个 feature 的目标环境和验收口径。

计划中应写明预期 git 提交分组：按可独立验证的 checklist 项、UAT issue 或防炸门禁边界拆分；高风险/跨模块任务不得把无关改动合进同一提交。

`plan.md` 必须写一行 `map_units_read: [...]`，并体现 scoped codebase map 给出的写入边界、新代码放置规则、禁止修改区域和受保护接口。`validation.md` 可参考 unit 的 `Recommended Gates`，但最终门禁必须来自 `devflow/shared/gate_registry.yaml`。

当前 feature 的 `plan.md` 只规划本 feature 的可执行细节；后续 feature 不展开成当前 checklist，但必须在 `devflow/roadmap.md` 保留目标、顺序、依赖和进入条件，避免当前 feature 归档后丢失长 plan 后段。

`checklist.yaml` 必须保留并完成以下固定检查项，除非明确 `waived` 且写明理由：

- 设计文档同步检查：影响系统框架正本、模块职责、Dify 与执行器分工、容器接口契约或主状态归属时，同步更新对应 `docs/design` 文档。
- 发布闭环适用性检查：目标环境为 `dev-full`/`online`，或涉及 Dify/容器/线上对象时，列出发布、自检、生效确认步骤；不适用时写明理由。

## UAT 覆盖矩阵

`df-plan` 必须从 `plan.md`、`checklist.yaml`、`validation.md` 的 Impact Map、Protected Surfaces、Golden Set Delta 中反推人工 UAT 项，并写入 `uat.md`。

每个用户可见新能力、真实浏览器路径、外部站点路径、插件交互、发布后运行态路径都必须对应至少一条 UAT 项，除非明确 waiver。机器测试、fixture 截图、mock、curl、DSL check、dev-full gate 只能作为支持证据，不能替代这些真实人工 UAT 项。

每条 UAT 项至少写明：覆盖能力、环境、1-3 个操作步骤、期望结果、证据口径、自动证据和当前状态。

特别规则：

- 涉及“本机浏览器”“官网采集”“插件回流”“ERP 写入”“Dify 发布生效”的能力，必须有真实环境 UAT 项；如果无法自动操作浏览器，也要留下人工验收步骤和待用户确认项。
- 如果某能力只完成了接口、Broker、fixture 或自动测试，`uat.md` 必须标记为“待人工 UAT”，不得写成已通过。
- 如果决定不做某项真实 UAT，必须在 `uat.md` 和 `validation.md` 写 waiver，说明原因、残余风险和后续归属。

## 人工确认门槛

`df-plan` 完成后必须停在计划审阅点，向用户说明计划路径、关键取舍、门禁和下一步建议，等待用户确认后才能进入 `$df-execute`。

如果 Plan Mode 退出后出现系统自动注入的 “Implement the plan in a fresh context” 或类似句子，只允许把 proposed plan 落成上述 DevFlow 计划产物；不得把它解释为执行授权。除非同一条用户消息中显式出现 `$df-execute`、`执行`、`按 checklist 做`、`直接执行`、`全自动推进` 等等价授权，否则禁止修改业务代码、跑发布、执行 UAT、提交代码或把 checklist 项推进为已完成。

止损回流场景下，计划审阅点必须额外展示：止损原因（从 `handoff.md` 提取）、未满足的闸门条件（逐条标 ✅/❌）、新方案与上次失败方案的差异、仍未验证的平台假设。用户未确认前禁止进入 `$df-execute`。

例外：用户在同一轮明确要求“直接执行”“全自动推进”或等价表述时，可以继续执行，但回复中必须说明已按用户授权跳过计划审阅停顿。

## Blast Radius Guard

高风险任务必须在 `validation.md` 写清：

- Impact Map：模块、状态、接口、工作流、数据写入、线上对象。
- Protected Surfaces：现有不能破坏的能力。
- Gate Selection：从 `devflow/shared/gate_registry.yaml` 选择必跑门禁。
- Golden Set Delta：本次新增或更新的样本。
- TDD/RED Evidence：失败测试、失败样本或历史故障复现。
- Waiver：无法自动化时的人工 UAT 替代项和残余风险。

可用脚本辅助推荐门禁：
`uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> gates --surfaces "dify,state-machine,login"`

只跑 smoke test 不能算防炸门禁。每个关键门禁要写明能拦什么风险、失败信号是什么、RED 证据或历史样本是什么。

涉及跨模块编排时，必须优先选择至少一个 `integration` 或 `e2e` 类型门禁，例如项目 registry 中的 dev-fast/dev-full 聚合门禁。涉及线上发布时，不要把代码侧归档当成上线完成；发布闭环必须有独立 checklist 项和证据。

## 证据要求

- `validation.md` 可以记录人工解释，但不能代替机器证据。
- 已选择的关键门禁必须后续通过 `run-gate` 生成 `evidence/manifest.json` 和对应日志；`df-accept` 不接受 agent 手写的“已通过”字段作为门禁通过依据。
- 高风险任务的 RED 证据要写入 `state.yaml` 或 `validation.md`，并在 checklist 中包含“先确认失败，再实现”的步骤。
