# DevFlow df-* Skills Review — 第四轮：df-review-loop 新增及集成

> **审阅者**: Claude Opus 4.6 (Thinking)
> **审阅时间**: 2026-05-14
> **审阅范围**: 新增 `df-review-loop` + `df-execute`/`df-fix`/`df-accept`/`df-uat`/`README` 的联动变更
> **审阅基线**: Round 3 review 后的版本 vs 当前版本

---

## 一、变更全景

### 1.1 新增文件

| 文件 | 行数 | 说明 |
|------|------|------|
| `df-review-loop/SKILL.md` | 109 | 全新 skill：自动化 `codex exec review` 循环 |

### 1.2 修改的既有文件

| 文件 | 关键变更 |
|------|----------|
| `df-execute/SKILL.md` | L38 提交前调用 `$df-review-loop --uncommitted`；L84/L93 verifier 角色增加 review 证据复核；L101-102 编排步骤 4-5 改写为 review loop 集成 |
| `df-fix/SKILL.md` | L74 verifier 增加 review 证据复核；L93 步骤 8 增加关闭 issue 前必须跑 review loop；L95 步骤 9 P0/P1 未处理不得关闭 issue |
| `df-accept/SKILL.md` | L29 新增检查项 16（`execute_validation_gap` 回顾——来自 Round 3 T5 建议） |
| `df-uat/SKILL.md` | L103 新增 `uat_phase` 引导原则（来自 Round 3 T3 建议） |
| `README.md` | 11 skills / ~1050 行；验证层次表增加 AI review loop 行；Skills 总览表增加 df-review-loop |
| `df-plan/SKILL.md` | 无变化 |

### 1.3 Round 3 建议的落地情况

| # | 建议 | 状态 |
|---|------|------|
| T1 | 术语约定写入 README | ✅ 已落地（我上轮直接改的），GPT 进一步扩展为 4 行表 |
| T2 | df-fix 补回归门禁前移步骤 11e | ✅ 保留（我上轮直接改的），L101 |
| T3 | df-uat 加 `uat_phase` | ✅ GPT 落地，L103 |
| T4 | skill 中"验证"措辞标注 | ✅ GPT 在 df-execute 中全面替换为"机器验证（validation）" |
| T5 | df-accept 补 `execute_validation_gap` | ✅ GPT 落地，L29 检查项 16 |

---

## 二、df-review-loop 逐节分析

### 2.1 ✅ 定位精准

L10 的边界声明写得很好：

> 本 skill 只处理 AI code review，不替代 validation、UAT 或 accept audit。

这和 Round 3 建立的验证层次体系完全一致：validation（机器测试/门禁）、AI review loop（代码审查）、UAT（人工验收）、accept audit（归档审计）是四个独立概念。新 skill 没有侵入其他层。

### 2.2 ✅ P0/P1/P2 分流合理

| 级别 | 处理 | 评价 |
|------|------|------|
| P0/P1 | 必须修或证明 false positive | ✅ 硬闸 |
| P2 确定 bug | 修 | ✅ 合理 |
| P2 风格/偏好/扩 scope | waiver | ✅ 关键——防止 review 变成无限追完美 |
| P3 / 无优先级 | 只记录 | ✅ 不阻断 |

L17 "不能无限追 P2" 是整个 skill 最重要的设计决策。

### 2.3 ✅ 止损设计和 DevFlow 体系对齐

L85-93 的 `review_loop_breaker` 和 df-fix 的 `doom_loop_breaker`、df-execute 的止损规则风格一致：触发条件明确、出路二选一（integration-debug 或回 df-plan）、需要用户确认。

### 2.4 ✅ finding ≠ UAT issue 的边界清晰

L16：

> review finding 不是 UAT issue；只有用户可见失败面才进 `issues.yaml`。review finding 先写入 `review-findings.yaml` 或 `handoff.md`。

这避免了 review 机器发现和人工 UAT 发现的混淆。

### 2.5 ✅ 目标选择中的 aggregate 复审提醒

L25：

> 若已对某个历史 commit 做了 follow-up fix，下一轮复审必须切到 aggregate 目标

这是从实际使用中提炼的陷阱规避——否则 reviewer 会重复报已被后续 commit 修掉的问题。

---

## 三、问题与建议

### 3.1 🔴 `codex exec review` 是 Codex CLI 专属命令，可移植性为零

**现状**：`df-review-loop` 的核心命令是 `codex exec review`（L14、L49）。这是 OpenAI Codex CLI 的特有入口。如果用户使用 Claude Code、Cursor、Aider 或其他 agent 环境，整个 skill 无法工作。

**影响**：DevFlow 定位为跨 agent 的开源 skill 仓库（README 写了 Codex CLI 和 Claude Code 两种安装方式）。新增一个硬绑定 Codex CLI 的 skill 会破坏这个定位。

**建议**：

- 在 skill 开头明确标注 `## 环境要求` 或 `## 前提条件`，写清需要 `codex exec review` 可用。
- 设计一个抽象层或可配置的 review 命令入口（例如 `state.yaml` 或 `devflow/shared/` 里配置 review 命令模板），让非 Codex 环境可以替换为等价的 review 工具。
- 或者退一步，在 L14 加一段：若当前环境没有 `codex exec review`，本 skill 降级为手动 review checklist（给用户 review 提示清单，但不做自动循环）。

### 3.2 🔴 `codex-auto-review` 模型别名是本机配置，不可发布

**现状**：L31 写了 `-m codex-auto-review`，L33 说 "codex-auto-review 是本机 catalog 中的 review 专用模型"。这是你（用户）的本机模型别名，其他安装 DevFlow 的用户没有这个配置。

**影响**：其他用户安装后执行会直接报错 "model not found"。

**建议**：

- 把模型选择改为配置化：从 `state.yaml`、`devflow/shared/review_config.yaml` 或环境变量读取，有默认值。
- 或者把 L31-39 的模型设置改为建议性文档而非硬编码命令参数。例如："默认使用当前 Codex 配置的模型 + `reasoning_effort=high`；项目可在 `devflow/shared/review_config.yaml` 中覆盖模型和 effort"。

### 3.3 🟡 `review-findings.yaml` 未纳入 DevFlow 产物体系

**现状**：L16 提到 review finding 写入 `review-findings.yaml` 或 `handoff.md`，L76 也提到 "更新 `review-findings.yaml` 或 `handoff.md`"。但：

- `review-findings.yaml` 没有出现在 README 的运行时目录结构中。
- `df-accept` 的检查项没有验证 review 证据的完整性。
- `df-status -r` 恢复时没有读取 `review-findings.yaml`。

**建议**：

- 如果 `review-findings.yaml` 是正式产物，需要：(1) 加入 README 运行时目录树；(2) `df-accept` 增加检查项；(3) `df-status -r` 恢复时读取。
- 如果它只是临时工作区，应明确说"每轮 review 结束后 findings 可归档到 `evidence/reviews/`，不需要跨会话持久化"。
- 建议选前者——因为 `df-execute` L101 写了 "review PASS 或阻断项都有明确 waiver 后才允许提交"，这意味着 review findings 实质上是提交的门禁证据，应该被 accept 审计。

### 3.4 🟡 df-accept 没有检查 review 证据

**现状**：`df-accept` 的 15+1 项检查覆盖了 checklist、validation、UAT、codebase map、truth doc、golden set——但没有检查 `evidence/reviews/` 是否存在、review loop 是否 PASS 或有 waiver。

**影响**：执行和修复阶段做了 review loop，但归档时没有验证 review 证据是否齐全。这和 "证据先于断言" 的核心取舍不一致。

**建议**：在 `df-accept` 检查项中增加一条：

> 17. 若 checklist 中有通过 `$df-review-loop` 审查的提交，`evidence/reviews/` 必须包含对应的 review 轮次记录和最终 `review_loop_status: pass` 或 waiver。缺失时写 waiver 或补跑。

### 3.5 🟡 fast-fix 是否豁免 review loop 未显式说明

**现状**：`df-fix` L60 的 fast-fix 快速路径是 4 步（确认 → 改 → targeted test → 原子提交），没有提到 `$df-review-loop`。L93 步骤 8 的 review loop 调用写在 "以下流程适用于 `scoped-fix` 和 `high-risk-fix`" 段落内。

**评价**：fast-fix 豁免 review loop 是合理的（极小低风险改动不值得多跑一轮 AI review），但这个豁免是隐式的——读者需要自行推断 fast-fix 段落不包含 review loop。

**建议**：在 fast-fix 段落 (L60) 末尾加一句明确豁免：

> fast-fix 不要求 `$df-review-loop`；若验证失败升级为 `scoped-fix` 后必须补跑。

### 3.6 🟡 review_loop_breaker 和 doom_loop_breaker 的交互

**现状**：`df-review-loop` 有自己的止损（`review_loop_breaker`），`df-fix` 有 `doom_loop_breaker`。当 review loop 在 df-fix 内部触发止损时：

- review_loop_breaker 写入 `handoff.md`
- 但 doom_loop_breaker 的计数器（两次补丁失败、同一文件修 3+ 次等）是否受 review loop 内部的修复轮次影响？

**风险**：review loop 内部的修复轮次可能不被 df-fix 的止损计数器识别，导致一个 issue 实际被修了 6+ 次（df-fix 3 次 + review loop 内部 3 轮）但 doom_loop_breaker 只计了 3 次。

**建议**：明确 review loop 内部的修复轮次是否计入 df-fix 的止损计数器。建议：**计入**。在 `df-review-loop` 的止损节加一句：

> review loop 内每轮修复算作调用方（df-execute 或 df-fix）的一次修复尝试，计入调用方的止损计数器。

### 3.7 🟢 L49 命令行过长，实际可执行性存疑

**现状**：

```
codex exec review <target> -m <model> -c 'model_reasoning_effort="<effort>"' --json -o <round.md> "<review instructions>" > <round.jsonl>
```

这一行在实际 shell 中执行时，`<review instructions>` 可能很长（包含 feature id、checklist item、P0/P1/P2 规则等），容易超过命令行长度限制或遇到引号转义问题。

**建议**：考虑支持从文件读取 review instructions：`--instructions-file <path>` 或 stdin pipe。这是执行细节，优先级低。

### 3.8 🟢 Round 3 T4（"验证"措辞标注）只在 df-execute 完成

**现状**：GPT 在 df-execute 中把"验证"全部替换为"机器验证（validation）"，但 df-fix 中的措辞仍然使用"验证"（如 L93 "修复验证"）。

**评价**：df-fix 中的"验证"通常指"修复后复跑 + 门禁"，语义上是 validation 而非 UAT，但没有加括号标注。渐进式完成是合理的，低优先级。

---

## 四、README 验证层次表的变化

Round 3 我建议了 3 行表（validation / UAT / accept audit）。GPT 扩展为 4 行，增加了 **AI review loop**：

| 概念 | 含义 | 执行阶段 | 产物 |
|------|------|----------|------|
| **validation**（机器验证） | 测试、构建、门禁脚本、runtime probe | df-execute、df-fix | `evidence/manifest.json` |
| **AI review loop**（代码审查循环） | `codex exec review`、P0/P1/P2 分流… | df-review-loop、df-execute、df-fix | `evidence/reviews/` |
| **UAT**（人工验收） | 真实路径、真实环境、人工操作和观察 | df-uat | `uat.md` 记录 |
| **accept audit**（归档审计） | 证据完整性、覆盖率、stale gate | df-accept | `acceptance.md` |

**评价**：扩展为 4 层是合理的——AI review 确实和 validation（自动测试/门禁）是不同的东西：validation 检查"代码行为是否正确"，review 检查"代码质量/风险/正确性是否有人（或 AI）审过"。分开列出消除了歧义。

但 L133 的措辞值得注意：

> `verifier` 是 df-execute 和 df-fix 中的子代理角色名，负责执行 validation 门禁、复核 review 证据和运行态证据；AI diff 审查由 `df-review-loop` 统一处理。

这里 `verifier` 的职责和 `df-review-loop` 有重叠："复核 review 证据" vs "AI diff 审查"。建议收窄 `verifier` 的定义：verifier 只**读取和复核** review loop 产出的证据（检查是否 PASS），不自己做 diff 审查。当前措辞已经基本表达了这个意思，但可以更明确。

---

## 五、跨 skill 一致性检查

### 5.1 ✅ df-execute 的集成干净

L38（提交前跑 review）和 L101-102（编排步骤中的 review loop 位置）清晰地把 review loop 嵌入了 "executor 返回 → review → 提交" 的流水线中。review 失败时回退到 executor 修复（L102），不由主模型自己修——和子代理分派哲学一致。

### 5.2 ✅ df-fix 的集成合理但需要注意 fast-fix 豁免

L93 在步骤 8 中插入 review loop，L95 在步骤 9 加了 P0/P1 硬闸。位置正确：在 RED/GREEN 验证之后、关闭 issue 之前。

fast-fix 的隐式豁免见 3.5 节。

### 5.3 ⚠️ df-plan 没有提到 review loop

`df-plan` 在第三步计划编写中没有提到 review loop 作为 checklist 的固定检查项。目前 review loop 是 df-execute 和 df-fix 的内嵌行为，不需要在 plan 里显式规划。

但如果一个项目不使用 Codex CLI（见 3.1），review loop 会静默失败或被跳过。`df-plan` 是否应该在 `validation.md` 中记录 review loop 的可用性？

**建议**：低优先级。当前 review loop 由 df-execute/df-fix 自动触发，不需要在 plan 里规划。但如果 3.1 的环境配置化落地了，`df-plan` 可以在创建 feature 时检测 review 能力并记录。

---

## 六、改进优先级总结

| # | 改动 | 优先级 | 理由 |
|---|------|--------|------|
| **R1** | `codex exec review` 标注环境依赖或抽象命令入口 | 🔴 高 | 破坏跨 agent 可移植性 |
| **R2** | `codex-auto-review` 模型别名改为配置化 | 🔴 高 | 其他用户安装后直接报错 |
| **R3** | `review-findings.yaml` 纳入产物体系或明确临时性 | 🟡 中 | 产物边界不清 |
| **R4** | df-accept 增加 review 证据检查项 | 🟡 中 | 和"证据先于断言"原则一致 |
| **R5** | fast-fix 显式声明豁免 review loop | 🟡 中 | 消除隐式推断 |
| **R6** | review_loop_breaker 轮次计入调用方止损计数器 | 🟡 中 | 防止止损计数被绕过 |
| **R7** | L49 命令行长度 / instructions 文件化 | 🟢 低 | 执行细节 |
| **R8** | df-fix 中"验证"措辞标注 | 🟢 低 | 渐进式完成 |

---

## 七、总结

`df-review-loop` 是一个**设计质量高**的新增 skill：

- **定位精准**：只做 AI code review，不侵入 validation/UAT/accept audit
- **P0/P1/P2 分流 + "不追 P2" 纪律**：解决了 review 无限循环的核心风险
- **和 df-execute/df-fix 的集成干净**：位置正确（修复后、提交前）、止损规则和体系对齐
- **GPT 同时落地了 Round 3 的全部 5 个建议**（T1-T5）

**最大的问题是可移植性**：`codex exec review` 和 `codex-auto-review` 两个硬编码把整个 skill 绑定在了 Codex CLI + 特定本机配置上。如果 DevFlow 的目标受众包括非 Codex 用户（README 写了 Claude Code 安装方式），R1 和 R2 是必须解决的。

次要问题是 `review-findings.yaml` 和 `evidence/reviews/` 还没有完全纳入 DevFlow 的产物体系（df-accept 不检查、df-status 不恢复、README 目录树不列）。
