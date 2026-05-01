<div align="center">

# DevFlow Skills

![DevFlow Skills](./asset/devflow-skills-cover-clean.png)

[English](./README.en.md) · **中文**

**面向个人开发任务的轻量、可恢复、人在环 AI 编码工作流**

<p>
  <img src="https://img.shields.io/badge/status-beta-F59E0B?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/skills-7-6366F1?style=flat-square" alt="Skills"/>
  <img src="https://img.shields.io/badge/workflow-DevFlow-10B981?style=flat-square" alt="Workflow"/>
</p>

</div>

---

## 为什么做 DevFlow

已经有很多 AI 编码工作流和规格框架，DevFlow 解决的是更窄的问题：**一个人和一个 coding agent 如何把一次开发任务稳定推进到可验收、可恢复、可归档**。

它不试图编排一组 agent，也不把每个任务都升级成重型规格工程。DevFlow 把状态落在你的仓库里，用少量固定阶段覆盖完整生命周期：

```text
目标收敛 -> 计划审阅 -> 执行验证 -> UAT 闭环 -> 最终归档
```

这样做的取舍很明确：

- **更少隐式上下文**：任务状态在 `devflow/` 文件树里，不只在聊天记录里。
- **更少流程负担**：只有 7 个 skills，围绕 feature 生命周期组织。
- **更强恢复能力**：新会话可以通过 `df-status -r` 找回当前 feature、计划和下一步。
- **更保守的风险控制**：高风险任务要求 RED 证据、防炸门禁和发布闭环。

---

## 安装

### 通过 Skills CLI

```bash
npx skills add https://github.com/Yinghai75/devflow-skills
```

适用于支持 `npx skills` 安装 GitHub skill 仓库的 agent 环境，例如 Codex CLI、Claude Code 等。

### 手动安装

```bash
# Codex CLI
mkdir -p ~/.codex/skills
git clone https://github.com/Yinghai75/devflow-skills.git /tmp/devflow-skills-codex
cp -R /tmp/devflow-skills-codex/df-* ~/.codex/skills/

# Claude Code
mkdir -p ~/.claude/skills
git clone https://github.com/Yinghai75/devflow-skills.git /tmp/devflow-skills-claude
cp -R /tmp/devflow-skills-claude/df-* ~/.claude/skills/
```

安装后，从一个明确开发目标开始：

```bash
/df-init
```

---

## 快速上手

- **拿到新需求**：运行 `/df-init`，创建 feature 目录并分诊风险车道。
- **确定怎么做**：运行 `/df-plan`，生成计划、checklist 和验证方案，停在审阅点。
- **开始实施**：运行 `/df-execute`，按 checklist 执行并更新状态和证据。
- **中断后恢复**：在新会话运行 `/df-status -r`，恢复上次断点。
- **验收归档**：运行 `/df-uat`、`/df-fix`、`/df-accept`，完成 UAT 闭环和归档。

---

## 核心设计

| 维度 | 重型规格/编排框架 | DevFlow |
| --- | --- | --- |
| 核心对象 | specs、agent、phase 或多角色协作 | 单个可交付 feature |
| 状态位置 | 规格目录、聊天历史或 agent 内部状态 | 仓库内 `devflow/` 文件树 |
| 恢复方式 | 依赖上下文续接或重新读取多份文档 | `df-status -r` 恢复当前断点 |
| 风险处理 | 流程通常相对固定 | 自动分诊 `fast`、`standard`、`high-risk` |
| 验证口径 | 容易变成文档自证 | checklist、validation、evidence 和 UAT issue 闭环 |
| 人在环 | 可能追求尽量自动化 | 计划审阅和验收默认保留人工确认点 |

---

## 工作流

```text
┌─────────┐    ┌─────────┐    ┌────────────┐    ┌────────┐    ┌───────────┐
│ df-init │───▶│ df-plan │───▶│ df-execute │───▶│ df-uat │───▶│ df-accept │
└─────────┘    └─────────┘    └────────────┘    └────────┘    └───────────┘
                                      ▲              │
                                      │              ▼
                                  ┌────────┐    记录 issues.yaml
                                  │ df-fix │◀────────┘
                                  └────────┘

df-status：任意阶段保存 handoff，或在新会话用 df-status -r 恢复断点
```

- `fast` 车道适合低风险文档、小范围局部修复，可以更快进入验收。
- `standard` 车道适合常规多文件开发，按计划、执行、UAT、修复、验收推进。
- `high-risk` 车道适合状态机、线上发布、数据写入、跨模块编排等任务，要求 RED 证据、防炸门禁和发布闭环。

---

## Skills 总览

| Skill | 作用 | 主要产物 |
| --- | --- | --- |
| `df-init` | 启动 feature，收敛目标、约束、成功标准和风险车道。 | `context.md`、`state.yaml` |
| `df-plan` | 编写人读计划、执行清单和验证方案。 | `plan.md`、`checklist.yaml`、`validation.md` |
| `df-execute` | 按 checklist 实施任务，更新状态和证据。 | 代码改动、`evidence/manifest.json`、`handoff.md` |
| `df-uat` | 引导人工 UAT，记录验收问题。 | `uat.md`、`issues.yaml` |
| `df-fix` | 修复 UAT issue，并跑回归验证。 | 修复提交、更新后的验证证据 |
| `df-accept` | 检查完成度、UAT issue、验证证据和风险门禁，通过后归档。 | `acceptance.md`、`devflow/archive/<date-slug>/` |
| `df-status` | 保存或恢复跨会话断点。 | `handoff.md` |

---

## 运行时目录结构

运行 `df-init` 后，目标仓库会出现 DevFlow 工作区：

```text
your-repo/
└── devflow/
    ├── active/
    │   └── 2026-05-01-add-login/
    │       ├── context.md
    │       ├── plan.md
    │       ├── checklist.yaml
    │       ├── validation.md
    │       ├── state.yaml
    │       ├── handoff.md
    │       ├── uat.md
    │       ├── issues.yaml
    │       ├── acceptance.md
    │       └── evidence/
    │           └── manifest.json
    ├── archive/
    ├── roadmap.md
    └── shared/
        ├── gate_registry.yaml
        └── golden_sets/
```

这些文件是 DevFlow 的正本状态：agent 可以读，人也可以审阅、修改和接管。

---

## 仓库结构

```text
.
├── df-init/
├── df-plan/
├── df-execute/
├── df-uat/
├── df-fix/
├── df-accept/
├── df-status/
└── asset/
```

每个 `df-*` 目录都是一个独立 skill，入口文件为 `SKILL.md`。

---

## 许可

MIT
