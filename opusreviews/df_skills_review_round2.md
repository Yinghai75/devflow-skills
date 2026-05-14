# DevFlow df-* Skills Review — 第二轮（GPT 改良后）

> **审阅者**: Claude Opus 4.6 (Thinking)
> **审阅时间**: 2026-05-13
> **对照基线**: 上次 review 提出的全部问题 vs `/Users/yinghai/SynologyDrive/codex/devflow/df-*/SKILL.md`

---

## 一、GPT 改了什么（逐条追踪）

### 🔴 上次必须修的 3 项

| # | 问题 | 状态 | 变化 |
|---|------|------|------|
| **M1** | codebase-map 卡片"3 节 vs 5 节"矛盾 | ✅ **已修** | L47 原来写"按 5 节模板"，现在改为"按 3 节模板"；L56 原来写"5 节内容"，现在改为"3 节内容"。和 L85 的模板定义完全一致了。 |
| **2.5** | roadmap 状态标记在 df-plan 和 df-backlog 之间缺协调 | ✅ **已修** | `df-plan` L21 大幅补充了 roadmap 状态解析规则；`df-backlog` L33 新增了状态行规范（`状态：下一项/未开始/进行中/已完成并归档/保留/已关闭`）。两边已对齐。 |
| **P4** | F1-F4 编号引用可能不存在 | ❌ **未改** | `df-plan` L86 仍写"禁止集成模式（F1-F4）"。GPT 可能认为 truth doc 确实有这个编号——需要验证。 |

### 🟡 上次建议修的 7 项

| # | 问题 | 状态 | 变化 |
|---|------|------|------|
| **2.3** | 子代理分派矩阵重复 | ❌ **未改** | df-execute 和 df-fix 仍各自维护一套。可以理解——抽取到 shared 是较大重构。 |
| **2.4** | df-execute 缺 doom_loop_breaker | ✅ **已修** | `df-execute` L70 新增"同一文件/模块在当前 feature 中被修改超过 3 次仍未通过"；L72 新增"重复修改或跨组件链路止损时写入 `doom_loop_breaker`"。现在和 df-fix 对齐了。 |
| **E3** | 子代理角色表的模型版本号会过期 | ✅ **已修** | `df-execute` L89-94 角色表已去掉具体模型版本号（原来写"5.3 low / 5.3 medium / 5.4 medium / 5.5 xhigh"），改为只写角色用途和可写范围。**这应该就是 GPT 说的"误判"——不是我误判，而是 GPT 认同了我的建议并做了修改。** |
| **F2** | doom_loop_breaker 段落拆分 | ❌ **未改** | df-fix L53 仍然是一个超长段落。低优先级，可接受。 |
| **A1** | "前后"审计歧义 | ✅ **已修** | `df-accept` L42 改为"脚本前必须做人工 UAT 覆盖审计…脚本后只做确认性复核"；L44 同理。歧义消除了。 |
| **P2** | OVERVIEW 占位符时的处理 | ✅ **已修** | `df-plan` L28 新增"缺失或仍是占位内容时先按 `$df-codebase-map --full` 建立 map"。 |
| **U1** | 增加 compact-issues CLI 命令 | ❌ **未改** | df-uat 仍要求手动压缩。可以理解——CLI 改动需要单独 feature。 |

### 🟢 上次可选改进

| # | 问题 | 状态 | 变化 |
|---|------|------|------|
| **2.2** | write-before-code gate 术语统一 | ❌ **未改** | 低优先级，合理。 |
| **F3** | 最终回复格式提取到 shared | ❌ **未改** | 低优先级，合理。 |
| **C1/C2** | constraint-audit 触发时机和输出 | ❌ **未改** | |
| **D1** | CLI shell=True 安全风险 | ❌ **未改** | |
| **E4** | subagent_handoff.md 引用存在性 | ❌ **未改** | |
| **E1** | architecture adjustment 回流时 state.yaml 状态 | ✅ **已修** | `df-execute` L33 新增"把 `state.yaml` 写为 `status: planning`、`current_step: \"architecture adjustment 回流\"`"。和我建议的完全一致。 |
| **P6** | discovery 阶段允许只读验证技术栈 | ✅ **已修** | `df-plan` L107 新增"Discovery 可用 `--help`、官方文档或只读本地配置验证技术栈可行性，但不得写文件或安装依赖"。 |
| **F1** | "AI 有 computer use 能力"改为项目特定 | ✅ **部分修** | `df-fix` L18 原来写"AI 有 computer use 能力，可操作真实 Edge 浏览器和容器"，现在改为"即使当前项目环境可操作真实浏览器和容器"。语气从能力声明变成了条件假设，更准确。 |
| **M2** | stash diff 具体命令 | ✅ **已修** | `df-codebase-map` L54 改为"WIP 用 `git stash show --name-only stash@{0}` 或等价 stash 引用"。 |

---

## 二、GPT 说的"误判"是哪条？

从改动内容看，GPT 可能指的是 **E3（模型版本号）**。但这不是我的"误判"——我说"模型版本号会很快过期"，GPT 确实按我的建议改了（去掉了具体版本号）。GPT 可能的意思是：它认为当初写模型版本号是有意为之、用于指导具体模型选择，不算"会过期的错误"，只是在你转达 review 时改了。

另一种可能是 **P4（F1-F4 编号）**——如果 `system_framework_truth.md` 确实有 F1-F4 编号体系，那我说"可能不存在"就是误判。需要验证 truth doc。

> [!IMPORTANT]
> **建议你问 GPT 确认一下它说的"误判"具体是哪一条**，我可以针对性回应。

---

## 三、本轮新发现

### 3.1 ⚠️ df-plan L21 的 roadmap 状态解析过于复杂

新版 L21 写了一段很长的解析规则：

> 按优先级选择：先第一个 `下一项`（独立 `状态：下一项`，或无独立状态行时条目标题、首行、紧邻标题元信息里的 legacy 裸 `下一项`），再第一个 `未开始`（独立 `状态：未开始`，或无独立状态行时的 legacy 裸 `未开始`）。使用 legacy 状态启动前，先把该条目补写为独立 `状态：...` 行。无状态且无 legacy 标记的条目只作为待整理 backlog，不自动启动。

这段规则实际上描述了两套解析策略（新格式 + legacy 格式 + 升级路径），嵌在一个句子里。对 agent 来说很难准确执行。

**建议**：拆成简洁的两步：
1. 优先匹配独立 `状态：下一项` 行
2. 回退匹配 legacy 裸标记，找到后先补写独立状态行再继续

或者更激进一点：既然 `df-backlog` 已经规定了状态行规范，旧 roadmap 条目可以一次性迁移，不需要在 df-plan 里维护 legacy 解析逻辑。

### 3.2 ✅ df-fix L18 的改写很好

从"AI 有 computer use 能力"改为"即使当前项目环境可操作真实浏览器和容器"，巧妙地把能力声明变成了条件限定。这样同一个 skill 文件可以在有和没有 computer use 的项目中都适用。

### 3.3 df-uat、df-constraint-audit、df-regression、df-status 无变化

这几个 skill 和上次完全一致，意味着 GPT 只改了有明确问题的 skill，没有做不必要的扩散修改。这是好的。

---

## 四、总结

| 维度 | 数量 |
|------|------|
| 上次提出的问题总数 | 20 |
| GPT 已修 | 10 |
| GPT 未改（合理跳过） | 8 |
| 仍待确认 | 1（P4 F1-F4 编号） |
| GPT 所说的"误判" | 1（待确认，最可能是 E3 或 P4） |
| 本轮新发现 | 1（L21 roadmap 解析过于复杂） |

**整体评价**：GPT 这轮改动非常精准——改了该改的，没碰不需要碰的。最有价值的几个修复：
- **E1**（architecture adjustment 回流状态）和 **2.4**（df-execute 补 doom_loop_breaker）填补了执行期的止损缺口
- **A1**（前后审计歧义）消除了 agent 可能做两遍完整审计的误解
- **2.5 + df-backlog L33**（roadmap 状态标记）解决了跨 skill 的格式契约

唯一的建议是 **P4（F1-F4）** 需要验证，以及 **L21 的 legacy 解析逻辑** 可以简化。
