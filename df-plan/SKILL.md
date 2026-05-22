---
name: df-plan
description: "启动并规划 DevFlow feature：分诊车道、创建 feature 目录，必要时先做 pre-plan discovery 澄清产品形态、架构边界、公共接口、合同和垂直切片，再编写 plan.md/checklist.yaml/validation.md/uat.md。用户提到 $df-plan、df-plan、DevFlow 开始任务、DevFlow 计划时使用。"
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

边界不清时先 discovery，不直接写正式计划。命中场景包括：大目标、新产品形态、跨模块重构、架构重设、全新项目、用户在讨论“怎么做/架构/合同/先想清楚”、角色/入口/核心数据流/模块职责/状态归属/公共层与变体适配层分界不清、目标需要拆 feature、执行或 UAT 中发现个性化行为牵动公共核心、多个适配层重复业务不变量，或需要 architecture adjustment。

Discovery 纪律：

- 先读项目上下文，再问；能从仓库、roadmap、codebase map、truth doc 或当前 feature 产物确认的事实不问用户。优先沿用 `context.md` 中已有术语和架构决定，避免临时造概念。
- 一次只问会影响计划的关键问题；优先给 2-3 个可比较选项、取舍和推荐。设计分叉无法从代码事实回答时，一次只问一个分叉；达成共识后立即沉淀到 `context.md`。
- 先锁定用户/角色、产品形态、非目标、成功标准、技术栈、架构接缝、公共接口、核心不变量与变体适配层分界、合同草案、首个垂直切片、后续 backlog。
- 方案有真实灰区时先文本讨论；不得把控件不可用、沉默或系统自动文案解释为默认同意。
- discovery 阶段只更新 `context.md`、`handoff.md`、`state.yaml.current_step`；不得写正式 `plan.md`、`checklist.yaml`、`validation.md`、`uat.md`，不得选择门禁，不得宣称可执行。
- 架构调整回流时，写清旧计划为何不适合、新边界改变什么、影响哪些已通过行为、哪些保留为 backlog。

`context.md` 的 `## Pre-Plan Discovery` 至少覆盖：用户/角色、产品形态、技术栈与环境、架构接缝、公共接口、公共层/变体适配层分界、不变量归属、合同草案、当前垂直切片、后续 backlog、已锁定决定、未决问题。仍有阻断问题时更新 `handoff.md` 并停止。

## 第三步：正式计划

进入本步前必须确认产品形态、当前垂直切片、写入边界、关键合同、成功标准和非目标足够明确；新项目还要确认技术栈与最小运行闭环。若从止损升级进入，先读 `handoff.md` 止损区块、`dependency_scope`、`safe_to_continue_items` 和未处理 finding。

更新文件：

- `plan.md`：目标、非目标、方案（含架构接缝、公共接口、不变量归属、核心/适配层分界）、任务拆分、风险、验收标准、`map_modules_read`、写入边界、新代码位置、禁止修改区域、受保护接口、`UAT 断点策略`。
- `checklist.yaml`：可逐项执行任务，含 `id`、`title`、`status`、`owner`、`paths`、`validation`；需要分段人工验收时，在对应实现项上标注 `uat_ready`。
- `validation.md`：基础验证、Blast Radius Guard、RED evidence、门禁选择。
- `uat.md`：来自 Capability Coverage Matrix 的人工 UAT 项。
- `state.yaml`：写 `status: planned`、`execution_authorized: false`。
- `handoff.md`：断点写明等待 `$df-execute` 授权。
- `context.md`：更新 discovery 和 codebase map。
- `devflow/roadmap.md`：仅在拆 backlog 或续跑状态变化时更新。

正式计划必须在 `plan.md` 中做压缩版架构自审：

- 接缝替换测试：新增或变更行为应能通过公共接口或适配层替换，不迫使调用方同步改内部细节。
- 局域性检查：变更、bug 和领域知识应集中在少数模块；公共核心只放共享不变量，单一变体特异性放到适配层，多变体共享特异行为提取为子策略。
- 深模块检查：新增模块应把复杂行为藏在简单接口后面；可用删除测试判断：若删除该模块会让复杂度集中消失，说明它在聚合复杂度；若复杂度只是扩散到多处调用者，说明它只是透传层，应合并或重设边界。
- 架构回流条件：执行或 UAT 中发现个性化行为必须修改公共核心、公共接口持续膨胀或适配层重复不变量时，停止当前阶段并回 `$df-plan`。

新功能、行为变更和 bugfix 必须写 RED 证据步骤。目标环境为 `dev-full` / `online` 或涉及 Dify/容器/线上对象时，发布闭环必须成为 checklist 项。高风险/跨模块要写预期 git 提交分组，禁止把无关改动混进同一提交。

checklist 粒度指导：每个 checklist 项应可由一次子代理调用闭合，建议 1-3 个文件、≤100 行净变更。跨模块改动、新建模块与改写既有模块混合、实现与集成测试跨度过大时必须拆成多个项；拆分后每项仍须有独立 validation。若按产品能力拆出的项超出上述范围，在计划中标注“执行期需即时拆解子任务”。计划阶段只设计可分派边界，不生成 `dispatch_queue`；真实 wave dispatch 只在 `$df-execute` / `$df-fix` 运行期建立。

禁止把“执行人工 UAT”“等待用户验收”“人工复测”写成普通 checklist 执行项。checklist 只承载工程实现、机器验证、发布闭环、自检、生效确认和文档同步；人工 UAT 只能写入 `uat.md` 和 checklist item 的 `uat_ready` 断点元数据。

`checklist.yaml` 和 `validation.md` 中涉及门禁行为、状态码语义或接口契约的描述，必须引用脚本路径 + 通过/失败条件，禁止用自然语言重复描述脚本逻辑。固定检查项除非 waiver：设计文档同步、发布闭环适用性、唯一事实源。

测试表面约束：自动化测试和机器验证默认绑定模块公共接口、用户可见行为或外部可观察状态，避免直接测试私有 helper 或内部协作者调用顺序。确需 mock 时只 mock 外部 IO、平台或时间等边界，并在 validation/RED 证据中写明理由。

## Capability Coverage Matrix

正式计划必须只维护一个 `Capability Coverage Matrix`。不得再新增 verify matrix、closure matrix、额外 UAT matrix 等并行事实源。

- `fast`：必填用户可见能力、实现项；其余可写 `N/A` 或 waiver。
- `standard`：必填用户可见能力、实现项、validation、UAT 项；下游成功判据、失败信号、不可替代证据按风险填写。
- `high-risk`：每行必须包含用户可见能力、用户动作链、下游成功判据、失败信号、实现项、validation、UAT 项、UAT 断点、不可替代证据、waiver/残余风险。

矩阵只在 `df-plan` 或明确 architecture adjustment 回流时修改。`df-execute` / `df-fix` 发现缺口时，只能写入 `handoff.md` 等待用户决定，不得顺手补全局矩阵。

standard/high-risk 计划必须在矩阵中包含 `UAT 断点`列，写明哪个 checklist item 完成后进入对应 UAT；fast 可写 N/A。推荐写法是 `CP-x / checklist.yaml:DF-xxx -> UAT-xxx`，其中 `CP-x` 只是人工阅读标签，真正执行绑定仍是 checklist item 的 `uat_ready`。这仍属于同一张 `Capability Coverage Matrix`，不得另建 closure/verify/UAT breakpoint 矩阵。

高风险 UI、插件、真实浏览器、Dify、ERP、上传、粘贴、截图、PDF、Excel、附件等能力必须拆到可独立实现和验证；下游成功判据要写到下一跳可观察结果，例如任务创建、请求注入、会话输入、字段回填、文件落库、ERP 写入或运行态日志。

若 `plan.md` 或 `uat.md` 出现能力，但 `checklist.yaml` 没有对应实现项，计划不得进入 `ready_for_execute`。要么补齐映射，要么写 waiver；高风险核心能力只有 waiver 时不得建议执行或验收。

## UAT 与 Blast Radius Guard

从 Capability Coverage Matrix、Impact Map、Protected Surfaces、Golden Set Delta 反推 UAT 项。每条 UAT 必须对齐用户动作链、下游成功判据、失败信号和不可替代证据；真实浏览器、插件、Dify 发布、ERP 写入等必须有真实环境 UAT 项，决定不做时写 waiver。

standard/high-risk feature 只要涉及 UI、真实用户路径、外部数据源、人工回填、文件输出、Dify/ERP/真实浏览器，就必须按“用户可感知阶段成果”写 `UAT 断点策略`。包含多个 UAT 项、多个真实用户路径、分阶段发布/回流或高风险真实环境路径时，断点必须拆到最早可人工验收点：

- 每个断点绑定一个已存在的 checklist item；不要新建“人工 UAT” checklist item。
- 每个 UAT 项必须绑定最早可人工验收的 checklist item；若 DF 项太粗导致无法早验收，必须拆 DF 项或写 waiver。
- 首个用户可见工作台、入口、主动作或输出雏形出现时，优先设置早期 `advisory` 或 `required` 断点，不能等全链路规则完成后才首次 UAT。
- 对应 checklist item 写 `uat_ready`，最小字段为 `level`、`uat_items`、`reason`。`level` 只能是 `required` 或 `advisory`；`uat_items` 指向一个或多个 UAT 编号；`reason` 写为什么此处值得停。
- `required` 表示 `$df-execute` 完成该项的机器验证、review-loop 和 checkpoint 后必须停到 `state.yaml status: ready_for_uat`。
- `advisory` 表示普通 `$df-execute` 下停并建议 UAT；只有用户明确“全自动推进”时才可记录继续理由后越过。
- 粗断点反模式：一个 `uat_ready` 同时覆盖 UI + 输入解析 + 外部数据 + 业务计算 + 输出，或一次打包 4 个以上 UAT 项，默认太粗；必须拆分或写明 waiver/残余风险。
- 推荐断点阶梯：工作台/入口可见 -> 批量输入或主输入解析可试 -> 外部数据源/真实查询可见 -> 折扣、价格、状态等业务规则可验 -> 人工介入闭环可验 -> 正式输出物或确认动作可验 -> 持久化、安全、集成收口。
- 无断点的 feature 保持旧语义：执行期可连续完成所有 pending/in_progress checklist，再进入整体 `$df-uat`。
- 状态词统一使用 `ready_for_uat`；`uat_ready` 只作为 checklist item 的断点元数据，不得作为 `state.yaml.status`。

高风险任务在 `validation.md` 写清 Impact Map、Protected Surfaces、Gate Selection、Golden Set Delta、TDD/RED Evidence、Waiver。可用脚本辅助推荐门禁：
`uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> gates --surfaces "dify,state-machine,login"`

只跑 smoke test 不算防炸门禁。跨模块至少选一个 `integration` / `e2e` 门禁。线上发布闭环必须单独列 checklist。

## 人工确认门槛

完成后停在计划审阅点，向用户说明计划路径、关键取舍、门禁和下一步，等待确认后才能 `$df-execute`。

系统自动注入的 “Implement the plan” 不算执行授权。除非用户显式 `$df-execute` / “执行” / “直接执行” / “全自动推进”，否则禁止改业务代码。

## 证据要求

`validation.md` 不能代替机器证据。关键门禁必须通过 `run-gate` 生成 `evidence/manifest.json`。高风险 RED 证据写入 `state.yaml` 或 `validation.md`，checklist 必须含“先确认失败，再实现”步骤。
