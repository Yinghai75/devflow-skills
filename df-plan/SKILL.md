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
3. 涉及主链、长尾链、官网子链、`nas-agent`、`erp-executor`、容器职责边界、状态机或跨模块编排时，先使用 `framework-truth-guard` 对齐边界。
4. 新功能、行为变更和 bugfix 必须在计划中先写 RED 证据步骤：失败测试、失败 golden sample、历史故障复现或明确的人工复现脚本。
5. 读取 `context.md` 的 `target_env`；目标环境为 `dev-full`/`online`，或任务涉及 Dify 发布、容器、线上对象时，必须把发布闭环写入 checklist。
6. 如果 `context.md` 或用户原始输入显示这是长目标的一部分，读取并维护 `devflow/roadmap.md`；没有该文件时先补建，列出当前 feature 和后续 feature backlog。

## 轻量探索

`df-plan` 必须内置轻量探索纪律，但不创建额外规格目录，不提交设计文档，也不转入其他计划 skill。

- 目标、非目标、约束、成功标准不清时，先问用户；每次只问最关键的一个问题。
- 方案不唯一时，在 `plan.md` 写 2-3 个可行方案、取舍理由、推荐方案和放弃方案。
- 对高风险任务，方案比较必须覆盖影响面、可回滚性、验证成本和失败后果。
- 对 fast 车道的小改动，可以用一段“方案与取舍”代替完整多方案表。
- 对长 plan，不强制使用 phase 命名；可以拆成多个 feature。关键是保留完整后续 backlog，不得只规划 POC 或第一段。

## 必写内容

更新：

- `plan.md`：目标、非目标、方案、任务拆分、风险、验收标准。
- `checklist.yaml`：可逐项执行的任务，包含 `id`、`title`、`status`、`owner`、`paths`、`validation`。
- `validation.md`：基础验证和 Blast Radius Guard。
- `handoff.md`：当前断点与下一步。
- `devflow/roadmap.md`：当任务来自长 plan 时，记录总目标、当前 feature、后续 feature backlog、每个 feature 的目标环境和验收口径。

计划中应写明预期 git 提交分组：按可独立验证的 checklist 项、UAT issue 或防炸门禁边界拆分；高风险/跨模块任务不得把无关改动合进同一提交。

当前 feature 的 `plan.md` 只规划本 feature 的可执行细节；后续 feature 不展开成当前 checklist，但必须在 `devflow/roadmap.md` 保留目标、顺序、依赖和进入条件，避免当前 feature 归档后丢失长 plan 后段。

`checklist.yaml` 必须保留并完成以下固定检查项，除非明确 `waived` 且写明理由：

- 设计文档同步检查：影响系统框架正本、模块职责、Dify 与执行器分工、容器接口契约或主状态归属时，同步更新对应 `docs/design` 文档。
- 发布闭环适用性检查：目标环境为 `dev-full`/`online`，或涉及 Dify/容器/线上对象时，列出发布、自检、生效确认步骤；不适用时写明理由。

## 人工确认门槛

`df-plan` 完成后必须停在计划审阅点，向用户说明计划路径、关键取舍、门禁和下一步建议，等待用户确认后才能进入 `$df-execute`。

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
