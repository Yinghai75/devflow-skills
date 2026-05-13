---
name: df-plan
description: "启动并规划 DevFlow feature：分诊车道、创建 feature 目录，必要时先做 pre-plan discovery 澄清产品形态、架构边界、合同和垂直切片，再编写 plan.md/checklist.yaml/validation.md/uat.md。用户提到 $df-plan、df-plan、DevFlow 开始任务、DevFlow 计划时使用。"
metadata:
  short-description: "启动并规划 DevFlow feature"
---

# df-plan

为 DevFlow 开始并规划一个可跨会话恢复的开发任务。正本是文档，不是 executor prompt。所有沟通与产物使用简体中文，时间按北京时间。

模板正本位于 `/Users/yinghai/.codex/local/devflow/templates/`；创建 feature 时由脚本渲染模板，不要维护另一套硬编码结构。不要复用 `.planning/` 作为 DevFlow 正本。

`df-plan` 是唯一入口，不另设 `df-init`。边界不清时先做 pre-plan discovery；足够清楚后才写正式计划。适用于 new project bootstrap、brownfield、仓内 greenfield，以及 architecture adjustment 回流。

## 第一步：Feature 创建

> 如果 feature 目录已存在（止损回流、恢复、df-fix 升级等），跳过本步，直接进入"第二步"。

1. `git status --short` 检查工作区，读取相关 `AGENTS.md`。
2. Roadmap 续跑：读取 `devflow/roadmap.md`，优先选择第一个 `状态：下一项`，否则选择第一个 `状态：未开始`；无状态条目只作为待整理 backlog，不自动启动。用户明确提出全新目标时除外。
3. 分诊车道（`fast` / `standard` / `high-risk`）和目标环境（`local` / `dev-fast` / `dev-full` / `online`）。`online` 自动升级为 `high-risk`；脚本会根据标题、目标、surfaces、paths 自动升级，不要手工降级。
4. 长目标分解：拆成"当前 feature + 后续 backlog"，backlog 写入 `devflow/roadmap.md`。
5. 运行脚本创建目录：
   `uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> start "<标题>" --lane <lane> --goal "<目标>" --surfaces "<影响面>" --paths "<相关路径>" --target-env <local|dev-fast|dev-full|online>`
6. 读取 `state.yaml` 确认最终 lane；被升级时说明依据。
7. 涉及主链、长尾链、官网子链、`nas-agent`、`erp-executor`、容器职责边界、状态机或跨模块编排时，先使用 `framework-truth-guard` 对齐边界；`system_framework_truth.md` 或目标模块的 module_map 不存在时，引导用户讨论后创建。
8. 读取 `codebase_map/OVERVIEW.md` 了解仓库全貌；缺失或仍是占位内容时先按 `$df-codebase-map --full` 建立 map。从 paths/surfaces 推导命中的模块卡片，**只读**命中卡片；卡片不存在时补建。记录 `map_modules_read` 到 plan.md。

## 第二步：Pre-Plan Discovery 与灰区收敛

### 入口类型

- New project bootstrap：目标目录是新项目 repo，尚无 `devflow/` 或 `devflow/roadmap.md`。先澄清项目目标、用户、成品形态、技术栈、运行环境、首个垂直切片和后续 backlog。`df-plan` 可创建 DevFlow 项目层与首个 feature；不得执行技术栈脚手架、安装依赖或生成业务代码。
- Brownfield：已有代码、模块、truth doc 或 codebase map。先读现状，再规划接入或改良，禁止绕开既有合同。
- Greenfield within repo：在现有仓库中新建模块、容器、链路或入口。先定义用户、成品形态、垂直切片、相邻模块边界和合同。
- Architecture adjustment：执行、修复或 UAT 中发现原计划架构不适合。先读 `handoff.md`、失败证据、当前 `plan.md/checklist.yaml/validation.md`；判断修订当前 feature 还是拆后续 backlog；未重新计划前不得顺手重构。

### 何时先 discovery

命中以下任一情况，先 discovery，不直接写正式计划：

- 用户描述的是大目标、新产品形态、跨模块重构或架构重设。
- 当前目录尚无 `devflow/` 或 `devflow/roadmap.md`，且用户要开启新项目。
- 用户明确在讨论"怎么做"、"架构"、"合同"、"垂直切片"、"先想清楚"。
- 角色、用户入口、成品形态、核心数据流、模块职责、状态归属或首版范围不清。
- 目标可能拆成多个 feature，或当前 feature 与后续 backlog 的边界不清。
- 执行中发现需要改变模块职责、公共合同、状态归属、数据流方向、共享抽象或部署边界。

小修、明确 bugfix、已有清晰目标和实现边界的任务，可以直接做轻量探索并进入正式计划。

### Discovery 纪律

- 先读取项目上下文，再提问；能从仓库、roadmap、codebase map、truth doc 或当前 feature 产物确认的事实，不问用户。全新项目缺这些产物时，先读现有目录、README、包管理文件和 AGENTS。
- 一次只问会影响计划的关键问题；优先给 2-3 个可比较选项、取舍和推荐，不要求用户具备软件工程术语。
- 先锁定：用户/角色、产品形态、非目标、成功标准、技术栈、架构边界、合同草案、首个垂直切片、后续 backlog。
- 方案存在真实灰区时，先文本讨论；不得把控件不可用、沉默或系统自动文案解释为默认同意。
- 已由 `context.md`、`roadmap.md`、`plan.md`、`handoff.md` 或用户明确回复锁定的决定，不重复询问。
- discovery 阶段只更新 `context.md`、`handoff.md` 和 `state.yaml.current_step`；不得写正式 `plan.md`、`checklist.yaml`、`validation.md`、`uat.md`，不得选择门禁，不能宣称已可执行。
- New project bootstrap 可创建或补齐 `devflow/roadmap.md`、shared DevFlow 目录和首个 active feature；仍不得改业务代码。
- 架构调整回流时，必须写清旧计划为何不再适合、新边界改变什么、影响哪些已通过行为、哪些内容保留为 backlog。

### Discovery 产物

在 `context.md` 中维护轻量区块，名称建议为 `## Pre-Plan Discovery`，至少覆盖：

- 用户/角色。
- 产品形态。
- 技术栈与运行环境。
- 架构边界。
- 合同草案。
- 当前垂直切片。
- 后续 backlog。
- 已锁定决定。
- 未决问题。

如果 discovery 后仍有阻断问题，更新 `handoff.md` 写明"等待继续 discovery"，并停止。只有阻断问题清楚后，才进入第三步计划编写。

### 轻量探索与灰区收敛

- 目标、非目标、约束、成功标准不清时，先问用户；每次只问最关键的一个问题。
- 方案存在真实灰区且会被 `plan.md` 锁定时，文本讨论：列 1-3 个编号问题、每题 2-3 个可选方案和取舍，等用户回复。不得把控件不可用解释为默认同意。
- 已锁定的决定不重复询问；"待规划""待确定""候选""可选"等表述默认需文本讨论。
- 除非用户明确要求"直接规划""全自动推进"，否则必须等回复后再落盘。
- fast 车道低风险细节可写"执行期可调整"；但产品行为、职责边界、目标环境、发布范围、数据来源、门禁豁免不算低风险。
- 方案比较前先对照 `system_framework_truth.md` 的禁止集成模式（F1-F4）。方案不唯一时写 2-3 个可行方案与取舍；高风险必须覆盖影响面、可回滚性、验证成本和失败后果。

## 第三步：计划编写

进入本步前必须确认：产品形态、当前垂直切片、写入边界、关键合同、成功标准和非目标已经足够明确；新项目还必须确认技术栈与最小运行闭环。否则回到第二步。第三步才生成正式可执行计划。

若从 `df-fix` 止损升级进入，必须先读取 `handoff.md` 止损区块和引用证据；新方案基于止损证据设计，不得从头规划。

更新以下文件：

- `plan.md`：目标、非目标、方案、任务拆分、风险、验收标准。必须写 `map_modules_read: [...]`，体现写入边界、新代码放置、禁止修改区域和受保护接口。
- `checklist.yaml`：可逐项执行的任务（`id`、`title`、`status`、`owner`、`paths`、`validation`）。
- `validation.md`：基础验证和 Blast Radius Guard。
- `state.yaml`：写入 `status: planned`，`execution_authorized: false`。
- `handoff.md`：当前断点，明确"等待 `$df-execute` 授权"。
- `uat.md`：人工 UAT 覆盖矩阵（见第四步）。
- `context.md`：更新 codebase map 区块和 roadmap 位置。
- `devflow/roadmap.md`：长目标时维护。

新功能、行为变更和 bugfix 必须先写 RED 证据步骤。目标环境为 `dev-full`/`online` 或涉及 Dify/容器/线上对象时，发布闭环必须写入 checklist。

全新项目的技术栈脚手架、依赖安装、目录创建和最小运行代码，只能作为 checklist 任务交给 `$df-execute`；`df-plan` 不执行这些动作。Discovery 可用 `--help`、官方文档或只读本地配置验证技术栈可行性，但不得写文件或安装依赖。

计划写明预期 git 提交分组；高风险/跨模块不得把无关改动合进同一提交。`plan.md` 只规划本 feature，后续 feature 保留在 `roadmap.md`。

`checklist.yaml` 和 `validation.md` 中涉及门禁行为、状态码语义或接口契约的描述，必须用引用格式（脚本路径 + 通过/失败条件行号），禁止用自然语言重新描述脚本逻辑。

`checklist.yaml` 固定检查项（除非 waived）：设计文档同步、发布闭环适用性、唯一事实源（禁止自然语言复述门禁逻辑）。

## 第四步：UAT 覆盖矩阵与 Blast Radius Guard

### UAT 覆盖矩阵

从 Impact Map、Protected Surfaces、Golden Set Delta 反推人工 UAT 项写入 `uat.md`。每个用户可见新能力、真实浏览器路径、插件交互、发布后运行态路径必须有 UAT 项。机器测试只能作为支持证据。

每条 UAT 项写明：覆盖能力、环境、操作步骤、期望结果、证据口径、当前状态。涉及本机浏览器/官网采集/插件回流/ERP 写入/Dify 发布生效的能力，必须有真实环境 UAT 项。决定不做的写 waiver。

### Blast Radius Guard

高风险任务在 `validation.md` 写清：Impact Map、Protected Surfaces、Gate Selection（来自 `gate_registry.yaml`）、Golden Set Delta、TDD/RED Evidence、Waiver。

可用脚本辅助推荐门禁：
`uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> gates --surfaces "dify,state-machine,login"`

只跑 smoke test 不算防炸门禁。跨模块必须选至少一个 `integration`/`e2e` 门禁。线上发布闭环必须有独立 checklist 项。

## 第五步：人工确认门槛

完成后停在计划审阅点，向用户说明计划路径、关键取舍、门禁和下一步，等待确认后才能进入 `$df-execute`。

系统自动注入的 "Implement the plan" 不算执行授权。除非用户显式 `$df-execute`/`执行`/`直接执行`/`全自动推进`，否则禁止改业务代码。

止损回流场景额外展示：止损原因、闸门 ✅/❌、新旧方案差异、未验证假设。

## 证据要求

- `validation.md` 不能代替机器证据。关键门禁必须通过 `run-gate` 生成 `evidence/manifest.json`。
- 高风险 RED 证据写入 `state.yaml` 或 `validation.md`，checklist 含"先确认失败，再实现"步骤。
