---
name: df-init
description: "启动 DevFlow 个人开发轻量工作流：分诊任务车道，创建 devflow/active/date-slug feature 目录，收敛目标、约束和成功标准。用户提到 $df-init、df-init、DevFlow 开始任务时使用。"
metadata:
  short-description: "启动 DevFlow feature"
---

# df-init

用 DevFlow 开始一个可跨会话恢复的开发任务。所有沟通与产物使用简体中文，时间按北京时间。

## 流程

1. 快速读取当前仓库上下文：`git status --short`、相关 `AGENTS.md`、必要项目文档。
2. Roadmap 续跑：如果仓库已有 `devflow/roadmap.md`，且用户没有明确提出全新目标，先读取 roadmap，选择第一个 `下一项` 或 `未开始` 的 feature 作为本次 `$df-init` 目标；不要重新从长 plan 猜测，也不要跳过未完成 backlog。
3. 灰区收敛：先判断目标、非目标、约束、成功标准和风险面是否足够明确。
   - 足够明确：继续创建 feature。
   - 可合理推断：继续创建 feature，并在 `context.md` 记录待确认点。
   - 关键目标、验收口径或风险边界不清：先问用户一个最关键的问题，不要一次抛出长问题列表。
4. 长目标分解：
   - 如果用户给的是长 plan、包含 POC/本地实现/生产实现/线上验证等多段目标，必须先拆成“当前 feature + 后续 feature backlog”，不要只截取第一段。
   - 后续 backlog 写入仓库级 `devflow/roadmap.md`；若文件已存在，追加或更新对应条目，不覆盖无关内容。
   - 当前 feature 的 `context.md` 必须写明它对应 backlog 中哪一项，以及下一项 feature 是什么。
5. 分诊车道：
   - `fast`：低风险文档、小范围局部修复。
   - `standard`：多文件、跨会话、需要 UAT 的常规任务。
   - `high-risk`：状态机、Dify workflow、数据写入、登录/权限、线上发布、共享 runtime、跨模块编排。
6. 判断目标环境：默认 `local`；本地快速联调用 `dev-fast`，本地完整复刻用 `dev-full`，线上/FZNAS/Dify 线上对象用 `online`。`online` 会自动升级为 `high-risk`。
7. 分诊必须保守：即使用户或 agent 传入 `standard`，只要标题、目标、surfaces、paths 或 target_env 命中高风险面，脚本会自动升级为 `high-risk`；不要手工降级绕过。
8. 运行脚本创建目录：
   `uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> start "<标题>" --lane <lane> --goal "<目标>" --surfaces "<影响面>" --paths "<相关路径>" --target-env <local|dev-fast|dev-full|online>`
9. 读取生成的 `state.yaml` 确认最终 lane；如果被升级为 `high-risk`，回复中明确说明升级依据。
10. 回复 feature 目录路径、它在 `devflow/roadmap.md` 中的位置、后续 backlog 摘要，并说明下一步应运行 `$df-plan`。

## 产物

脚本会生成：

- `devflow/active/<date-slug>/context.md`
- `plan.md`
- `checklist.yaml`
- `state.yaml`
- `validation.md`
- `uat.md`
- `issues.yaml`
- `handoff.md`
- `acceptance.md`
- `devflow/roadmap.md`（仅当输入是长目标或跨多个 feature 的 plan 时维护）
- `devflow/shared/gate_registry.yaml`
- `devflow/shared/golden_sets/`

不要复用 `.planning/` 作为 DevFlow 正本。

模板正本位于 `/Users/yinghai/.codex/local/devflow/templates/`；创建 feature 时由脚本渲染模板，不要维护另一套硬编码结构。
