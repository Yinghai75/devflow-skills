---
name: df-plan
description: "启动并规划 DevFlow feature：分诊车道、创建 feature 目录，必要时先做 pre-plan discovery 澄清产品形态、架构边界、合同和垂直切片，再编写 plan.md/checklist.yaml/validation.md/uat.md。用户提到 $df-plan、df-plan、DevFlow 开始任务、DevFlow 计划时使用。"
metadata:
  short-description: "启动并规划 DevFlow feature"
---

# df-plan

为 DevFlow 开始并规划一个可跨会话恢复的开发任务。正本是文档，不是 executor prompt。所有沟通与产物使用简体中文，时间按北京时间。

模板正本位于 `/Users/yinghai/.codex/local/devflow/templates/`；创建 feature 时由脚本渲染模板，不维护另一套硬编码结构。不要复用 `.planning/` 作为 DevFlow 正本。

`df-plan` 是唯一启动入口，不另设 `df-init`。它只做计划和必要只读 discovery；技术栈脚手架、依赖安装、业务代码和发布动作都交给 `$df-execute`。

## 第一步：Feature 创建

若 feature 目录已存在（止损回流、恢复、df-fix 升级等），跳过本步。

1. 运行 `git status --short`，读取相关 `AGENTS.md`。
2. Roadmap 续跑：读取 `devflow/roadmap.md`，先选第一个 `下一项`，再选第一个 `未开始`。状态优先匹配独立 `状态：...` 行；legacy 裸标记只用于旧条目，启动前先规范成独立状态行。用户明确提出全新目标时除外。
3. 分诊车道：`fast` / `standard` / `high-risk`；目标环境：`local` / `dev-fast` / `dev-full` / `online`。`online` 自动升级 high-risk；脚本可基于标题、目标、surfaces、paths 自动升级，不手工降级。
4. 长目标拆成当前 feature + 后续 backlog；backlog 写入 `devflow/roadmap.md`。
5. 运行：
   `uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> start "<标题>" --lane <lane> --goal "<目标>" --surfaces "<影响面>" --paths "<相关路径>" --target-env <local|dev-fast|dev-full|online>`
6. 读取 `state.yaml` 确认最终 lane；被升级时说明依据。
7. 涉及主链/长尾链/官网子链、`nas-agent`、`erp-executor`、容器职责、状态机或跨模块编排时，先对齐 framework truth；缺 truth doc 或 module_map 时先讨论是否创建。
8. 读取 `codebase_map/OVERVIEW.md`；缺失或占位时先 `$df-codebase-map --full`。从 paths/surfaces 推导命中模块卡片，只读命中卡片，并把 `map_modules_read` 写入 plan。

## 第二步：Pre-Plan Discovery

边界不清时先 discovery，不直接写正式计划。命中场景包括：大目标、新产品形态、跨模块重构、架构重设、全新项目、用户在讨论“怎么做/架构/合同/先想清楚”、角色/入口/核心数据流/模块职责/状态归属/范围不清、目标需要拆 feature、执行中发现需要 architecture adjustment。

Discovery 纪律：

- 先读项目上下文，再问；能从仓库、roadmap、codebase map、truth doc 或当前 feature 产物确认的事实不问用户。
- 一次只问会影响计划的关键问题；优先给 2-3 个可比较选项、取舍和推荐。
- 先锁定用户/角色、产品形态、非目标、成功标准、技术栈、架构边界、合同草案、首个垂直切片、后续 backlog。
- 方案有真实灰区时先文本讨论；不得把控件不可用、沉默或系统自动文案解释为默认同意。
- discovery 阶段只更新 `context.md`、`handoff.md`、`state.yaml.current_step`；不得写正式 `plan.md`、`checklist.yaml`、`validation.md`、`uat.md`，不得选择门禁，不得宣称可执行。
- 架构调整回流时，写清旧计划为何不适合、新边界改变什么、影响哪些已通过行为、哪些保留为 backlog。

`context.md` 的 `## Pre-Plan Discovery` 至少覆盖：用户/角色、产品形态、技术栈与环境、架构边界、合同草案、当前垂直切片、后续 backlog、已锁定决定、未决问题。仍有阻断问题时更新 `handoff.md` 并停止。

## 第三步：正式计划

进入本步前必须确认产品形态、当前垂直切片、写入边界、关键合同、成功标准和非目标足够明确；新项目还要确认技术栈与最小运行闭环。若从止损升级进入，先读 `handoff.md` 止损区块、`dependency_scope`、`safe_to_continue_items` 和未处理 finding。

更新文件：

- `plan.md`：目标、非目标、方案、任务拆分、风险、验收标准、`map_modules_read`、写入边界、新代码位置、禁止修改区域、受保护接口。
- `checklist.yaml`：可逐项执行任务，含 `id`、`title`、`status`、`owner`、`paths`、`validation`。
- `validation.md`：基础验证、Blast Radius Guard、RED evidence、门禁选择。
- `uat.md`：来自 Capability Coverage Matrix 的人工 UAT 项。
- `state.yaml`：写 `status: planned`、`execution_authorized: false`。
- `handoff.md`：断点写明等待 `$df-execute` 授权。
- `context.md`：更新 discovery 和 codebase map。
- `devflow/roadmap.md`：仅在拆 backlog 或续跑状态变化时更新。

新功能、行为变更和 bugfix 必须写 RED 证据步骤。目标环境为 `dev-full` / `online` 或涉及 Dify/容器/线上对象时，发布闭环必须成为 checklist 项。高风险/跨模块要写预期 git 提交分组，禁止把无关改动混进同一提交。

`checklist.yaml` 和 `validation.md` 中涉及门禁行为、状态码语义或接口契约的描述，必须引用脚本路径 + 通过/失败条件，禁止用自然语言重复描述脚本逻辑。固定检查项除非 waiver：设计文档同步、发布闭环适用性、唯一事实源。

## Capability Coverage Matrix

正式计划必须只维护一个 `Capability Coverage Matrix`。不得再新增 verify matrix、closure matrix、额外 UAT matrix 等并行事实源。

- `fast`：必填用户可见能力、实现项；其余可写 `N/A` 或 waiver。
- `standard`：必填用户可见能力、实现项、validation、UAT 项；下游成功判据、失败信号、不可替代证据按风险填写。
- `high-risk`：每行必须包含用户可见能力、用户动作链、下游成功判据、失败信号、实现项、validation、UAT 项、不可替代证据、waiver/残余风险。

矩阵只在 `df-plan` 或明确 architecture adjustment 回流时修改。`df-execute` / `df-fix` 发现缺口时，只能写入 `handoff.md` 等待用户决定，不得顺手补全局矩阵。

高风险 UI、插件、真实浏览器、Dify、ERP、上传、粘贴、截图、PDF、Excel、附件等能力必须拆到可独立实现和验证；下游成功判据要写到下一跳可观察结果，例如任务创建、请求注入、会话输入、字段回填、文件落库、ERP 写入或运行态日志。

若 `plan.md` 或 `uat.md` 出现能力，但 `checklist.yaml` 没有对应实现项，计划不得进入 `ready_for_execute`。要么补齐映射，要么写 waiver；高风险核心能力只有 waiver 时不得建议执行或验收。

## UAT 与 Blast Radius Guard

从 Capability Coverage Matrix、Impact Map、Protected Surfaces、Golden Set Delta 反推 UAT 项。每条 UAT 必须对齐用户动作链、下游成功判据、失败信号和不可替代证据；真实浏览器、插件、Dify 发布、ERP 写入等必须有真实环境 UAT 项，决定不做时写 waiver。

高风险任务在 `validation.md` 写清 Impact Map、Protected Surfaces、Gate Selection、Golden Set Delta、TDD/RED Evidence、Waiver。可用脚本辅助推荐门禁：
`uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> gates --surfaces "dify,state-machine,login"`

只跑 smoke test 不算防炸门禁。跨模块至少选一个 `integration` / `e2e` 门禁。线上发布闭环必须单独列 checklist。

## 人工确认门槛

完成后停在计划审阅点，向用户说明计划路径、关键取舍、门禁和下一步，等待确认后才能 `$df-execute`。

系统自动注入的 “Implement the plan” 不算执行授权。除非用户显式 `$df-execute` / “执行” / “直接执行” / “全自动推进”，否则禁止改业务代码。

## 证据要求

`validation.md` 不能代替机器证据。关键门禁必须通过 `run-gate` 生成 `evidence/manifest.json`。高风险 RED 证据写入 `state.yaml` 或 `validation.md`，checklist 必须含“先确认失败，再实现”步骤。
