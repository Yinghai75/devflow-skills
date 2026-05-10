<div align="center">

# DevFlow Skills

![DevFlow Skills](./asset/devflow-skills-cover-clean.png)

[English](./README.en.md) · **中文**

**个人开发者的轻量 AI 编码工作流：11 个 skills，约 890 行指令，覆盖完整 feature 生命周期**

<p>
  <img src="https://img.shields.io/badge/status-beta-F59E0B?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/skills-11-6366F1?style=flat-square" alt="Skills"/>
  <img src="https://img.shields.io/badge/instructions-~890-10B981?style=flat-square" alt="Instructions"/>
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"/>
</p>

</div>

---

## 为什么做 DevFlow

很多 AI 编码工作流都在解决更大的问题：规格管理、团队协作、多 agent 编排、复杂项目治理。DevFlow 的目标更窄：

**一个人 + 一个 coding agent，把一次开发任务稳定推到可验收、可恢复、可归档。**

按当前公开仓库粗略统计，不同方案的指令规模差异很明显：

| 框架 | 主要单元 | 子代理配置 | 粗略指令量 |
| --- | --- | --- | --- |
| [Superpowers](https://github.com/obra/superpowers) | 14 个 skills | 1 个 agent 文件 | 约 3,200 行 |
| [GSD](https://github.com/gsd-build/get-shit-done) | 99 个 workflows | 33 个 agent 文件 | 约 47,600 行 |
| **DevFlow** | **11 个 skills** | **5 类精简子代理角色** | **约 890 行** |

指令越重，每次会话烧的 token 越多，agent 越容易在长提示词里迷失重点。DevFlow 选择把范围收窄：不追求覆盖所有项目治理场景，只把个人开发的一次 feature 做扎实。

它不追求“全自动接管项目”，也不把每个小需求都升级成重型规格工程。DevFlow 把一次 feature 拆成几个固定阶段：

```text
目标收敛 -> 计划审阅 -> 执行验证 -> UAT 闭环 -> 最终归档
```

核心取舍：

- **状态落仓库**：目标、计划、checklist、验证证据和断点都写进 `devflow/` 文件树。
- **流程足够轻**：11 个 skills，约 890 行 `SKILL.md` 指令，围绕 feature 生命周期组织。
- **恢复成本低**：换会话后运行 `df-status -r`，即可恢复当前 feature、计划和下一步。
- **风险控制保守**：高风险任务要求 RED 证据、防炸门禁和发布闭环，agent 不能只写“已通过”来自证。

---

## 适用场景

- **AI 修一个问题引出三个回归？** DevFlow 的防炸门禁要求先证明旧功能不坏再改。
- **换个会话上次做到哪就忘了？** `handoff.md` + `df-status -r` 可以恢复断点。
- **AI 说“已通过测试”但其实没跑？** `run-gate` 生成机器证据，agent 不能自说自话。
- **想用 AI 但不敢全放手？** 计划审阅 + 人工 UAT，关键节点人在环。
- **框架太重烧太多 token？** 约 890 行 skill 指令，不在提示词里塞一整套重型流程。

---

## 安装

### Skills CLI（推荐）

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

其他 agent：将 `df-*` 目录复制到对应 skills 路径即可。每个 `df-*` 目录都是独立 skill，入口为 `SKILL.md`。

---

## 快速上手

```bash
/df-init        # 拿到需求：创建 feature 目录，收敛目标，分诊风险车道
/df-backlog     # 先不做：把新想法登记到 roadmap/backlog
/df-plan        # 确定怎么做：生成计划、checklist、验证方案，停在审阅点
/df-codebase-map # 看代码地图：生成或刷新实现层导航
/df-constraint-audit # 查约束漂移：审计门禁、状态码、接口契约是否重复或矛盾
/df-execute     # 开始实施：按 checklist 执行，更新状态和证据
/df-status -r   # 换会话了：恢复上次断点
/df-uat         # 人工验收：记录 UAT 结果和问题
/df-fix         # 修复问题：修 UAT issue，跑回归门禁
/df-regression  # 验收后回归：处理已归档 feature 的追加 UAT 问题
/df-accept      # 最终归档：检查证据和门禁，通过后移入 archive/
```

---

## 工作流

```text
┌─────────┐    ┌─────────┐    ┌────────────┐    ┌────────┐    ┌───────────┐
│ df-init │───▶│ df-plan │───▶│ df-execute │───▶│ df-uat │───▶│ df-accept │
└─────────┘    └─────────┘    └────────────┘    └────────┘    └───────────┘
     │              │               ▲                │              │
     ▼              ▼               │                ▼              ▼
┌────────────┐ ┌────────────────┐ ┌────────┐    记录 issues.yaml ┌───────────────┐
│ df-backlog │ │ df-codebase-map │ │ df-fix │◀───────────────────│ df-regression │
└────────────┘ └────────────────┘ └────────┘                    └───────────────┘

              df-status：任意阶段保存断点 / 新会话 df-status -r 恢复
```

三种车道：

- **fast**：低风险文档、小修复。流程更短，可以更快进入验收和归档。
- **standard**：常规多文件开发。按计划、执行、UAT、修复、验收推进。
- **high-risk**：状态机、线上发布、数据写入、跨模块编排。要求 RED 证据、防炸门禁和发布闭环。

风险车道由 `df-init` 保守分诊。涉及线上对象时自动升级为 `high-risk`，不允许手工降级绕过。

---

## 设计理念

- **状态落仓库，不落聊天记录**：目标、计划、checklist、验证证据和断点全部写进 `devflow/`。人可以直接读、改、接管。
- **机器证据，不是文档自证**：关键门禁通过 `run-gate` 执行，结果写入 `evidence/manifest.json`。agent 手写的“已通过”不算数。
- **计划和执行分离**：`df-plan` 完成后默认停在审阅点。你确认后才进入 `df-execute`。
- **做一点不能炸三点**：高风险任务要求先写失败测试或复现证据，再用防炸门禁覆盖影响面和回归验证。

---

## Skills 总览

| Skill | 做什么 | 产出什么 |
| --- | --- | --- |
| `df-init` | 收敛目标、约束、成功标准，分诊风险车道。 | `context.md`、`state.yaml` |
| `df-backlog` | 登记不应打断当前 feature 的新事项。 | 更新 `roadmap.md` |
| `df-plan` | 写计划、执行清单、验证方案和防炸门禁。 | `plan.md`、`checklist.yaml`、`validation.md` |
| `df-codebase-map` | 生成、刷新和消费实现层代码地图。 | `devflow/shared/codebase_map/` |
| `df-constraint-audit` | 审计门禁、状态码语义和接口契约的重复或矛盾。 | 约束问题清单、整改建议 |
| `df-execute` | 按 checklist 逐项实施，更新状态和证据。 | 代码改动、`evidence/manifest.json`、`handoff.md` |
| `df-uat` | 引导人工 UAT，记录验收问题。 | `uat.md`、`issues.yaml` |
| `df-fix` | 修复 UAT issue，跑回归门禁。 | 修复提交、更新证据 |
| `df-regression` | 处理已归档 feature 的验收后追加回归。 | 回归 issue、修复 feature、验证证据 |
| `df-accept` | 检查完成度、证据、门禁，归档 feature。 | `acceptance.md`、`devflow/archive/` |
| `df-status` | 保存断点，或在新会话恢复上下文。 | `handoff.md` |

---

## 运行时目录

运行 `df-init` 后，你的仓库会出现：

```text
your-repo/
└── devflow/
    ├── active/
    │   └── 2026-05-01-add-login/     # 当前 feature
    │       ├── context.md             # 目标、约束、成功标准
    │       ├── plan.md                # 实施方案
    │       ├── checklist.yaml         # 可逐项执行的任务清单
    │       ├── validation.md          # 验证方案 + 防炸门禁
    │       ├── state.yaml             # 当前状态和断点
    │       ├── handoff.md             # 跨会话交接
    │       ├── uat.md                 # UAT 记录
    │       ├── issues.yaml            # UAT 发现的问题
    │       ├── acceptance.md          # 验收报告
    │       └── evidence/              # 机器证据
    │           └── manifest.json
    ├── archive/                       # 已归档 feature
    ├── roadmap.md                     # 长目标 backlog
    └── shared/
        ├── gate_registry.yaml         # 门禁注册表
        ├── golden_sets/               # 黄金样本
        └── codebase_map/              # 实现层代码地图
```

这些文件是正本状态。agent 读它们来恢复上下文，你也可以随时打开审阅或直接编辑。

---

## 许可

MIT
