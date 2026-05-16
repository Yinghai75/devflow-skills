---
title: "精简 DevFlow skills 并收敛上下文读取策略"
lane: "high-risk"
target_env: "local"
created_at: "2026-05-16 15:29:46 CST"
---

# 背景

## 目标

在保留单 skill 可读关键规则的前提下，吸收 opus 计划中合理的 skill 精简、handoff/issues 读取策略和 issues 前置压缩规则，降低上下文消耗且不削弱 DevFlow 执行合同。

## 输入材料

- `opusreviews/df_skills_slim_plan.md`：提出 #3 handoff 分段读取、#4 skill 文件精简、#5 issues.yaml closed stub 自动压缩。
- 当前 skill 行数基线：
  - `df-plan/SKILL.md`：161 行。
  - `df-review-loop/SKILL.md`：156 行。
  - `df-execute/SKILL.md`：139 行。
  - `df-fix/SKILL.md`：127 行。
  - `df-uat/SKILL.md`：119 行。
  - `df-accept/SKILL.md`：91 行。
  - `df-codebase-map/SKILL.md`：109 行。
  - `df-regression/SKILL.md`：104 行。

## 约束

- 仓库 `AGENTS.md` 要求单个 skill 的 `SKILL.md` 自包含，避免依赖未发布本地上下文。
- README 当前手动安装步骤只复制 `df-*` 到 skills 路径，并复制 `runtime/` 到 `~/.codex/local/devflow/`。
- 本机 `~/.codex/skills/df-*` 是到本仓库 `df-*` 目录的 symlink；但公开安装不能假设 symlink。
- 前一个 active feature 已 validated，等待 `$df-accept`；本 feature 不改写它的正式产物。

## 成功标准

- 新计划产物完整：`plan.md`、`checklist.yaml`、`validation.md`、`uat.md`、`handoff.md`、`state.yaml`、`context.md` 已落盘。
- 后续 `$df-execute` 能按 checklist 执行，并且每项都有对应 validation / UAT / 不可替代证据。
- shared protocol 若被采用，不破坏复制安装路径，也不让 hard gate 只存在外部文件。
- `df-fix` / `df-uat` 的 compact 入口规则能覆盖长 closed 历史，且不误压 open/retest issue。

## 目标环境

local

## Codebase Map

- map_modules_read:
  - `devflow/shared/codebase_map/OVERVIEW.md`
  - `devflow/shared/codebase_map/modules/skill-entrypoints.md`
  - `devflow/shared/codebase_map/modules/runtime-helper.md`
  - `devflow/shared/codebase_map/modules/docs-and-release.md`
- codebase_map_waiver: 无。命中模块已只读。

## Pre-Plan Discovery

- 用户/角色：维护 DevFlow skills 的个人开发者和 agent 编排者。
- 产品形态：公开发布的 `df-*` Codex skills 仓库，本机通过 symlink 使用，其他用户可能复制安装。
- 技术栈与运行环境：Markdown skill 文档、DevFlow runtime helper、`uv` 运行 Python 测试，本 feature 目标环境为 local。
- 架构边界：skill 入口仍是 `df-*/SKILL.md`；共享协议只能作为发布可达的辅助文档，不能成为唯一硬闸事实源。
- 合同草案：
  - `SKILL.md` 保留关键摘要和硬阻断条件。
  - 共享协议文件可承载重复细则，但引用必须可达。
  - `issues.yaml` 活跃视图优先，长历史迁移到 feature-local `evidence/`，不得删除正式记录。
- 当前垂直切片：先规划 skill 瘦身、上下文读取、compact 前置和文档同步，不执行代码修改。
- 后续 backlog：如果本轮发现 root `shared-protocols/` 与安装生态不兼容，后续可单独规划“skill 发布打包结构调整”。
- 已锁定决定：不强求 80 行；不把核心逻辑只留外部引用；不动前一个 validated feature。
- 未决问题：无阻断问题。shared protocol 采用方式在 DF-002 中以 RED 和验证闭环决策。
