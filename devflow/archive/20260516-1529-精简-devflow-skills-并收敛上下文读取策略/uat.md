# UAT 记录

## 人工验收记录

- 时间：2026-05-16 CST
- 结论：用户明确表示“devflow 就不做 UAT 了，直接 `$df-accept`”。
- waiver：本 feature 是 DevFlow skill/runtime 文档治理和本地 helper 规则修正，不涉及业务发布、远端发布、真实浏览器、插件、Dify WebApp 或 ERP 写入路径；人工 UAT 不执行，由机器门禁、review-loop 和用户显式验收意图替代。
- 残余风险：未由人工逐项打开 skill/README 做视觉审阅；若后续使用中发现说明歧义，按 `$df-fix` 或后续 feature 处理。

## Capability Coverage Matrix 对齐项

> UAT 项来自 `plan.md#capability-coverage-matrix`。这里只写操作步骤、期望结果和复测记录，不维护额外覆盖矩阵。

### UAT-001：瘦身后的 skill 仍能独立说明关键硬闸

- 覆盖能力：Agent 读取瘦身后的 skill 仍能独立执行关键 DevFlow 规则。
- 对应用户动作链：人工打开 `df-execute/SKILL.md`、`df-fix/SKILL.md`、`df-plan/SKILL.md`、`df-review-loop/SKILL.md`，只读正文和关键摘要。
- 对应下游成功判据：能判断何时允许执行、何时必须止损、scope 外 P0/P1 怎么处理、何时不能 UAT/accept。
- 对应失败信号：必须继续打开外部协议文件才知道能否执行、能否关闭 issue 或能否继续 UAT。
- uat_phase: first_pass
- 环境：local 文档审阅。
- 操作步骤：
  1. 打开上述四个 `SKILL.md`。
  2. 分别查找 `execution_authorized`、`scope_decision`、`doom_loop_breaker`、`compact-issues`、`Capability Coverage Matrix`。
  3. 确认每个关键规则在 skill 内有摘要或硬阻断语句。
- 期望结果：关键硬闸不依赖外部文件才能被理解。
- 不可替代证据：人工审阅记录和关键规则路径清单。
- 自动证据：validation.md:V-001。
- 状态：waived，用户明确跳过人工 UAT；自动证据见 validation.md:V-001 和 review-findings.yaml

### UAT-002：长 issues/handoff 入口不会先吞全量历史

- 覆盖能力：Agent 恢复长 `handoff.md` / 长 `issues.yaml` 时先 scoped read 或压缩。
- 对应用户动作链：人工模拟进入 `$df-uat` 或 `$df-fix <issue-id>`，当前 feature 有长 handoff 或多个 closed issue。
- 对应下游成功判据：skill 指令要求先 compact 或只读相关段落，再继续登记/修复。
- 对应失败信号：指令仍要求全量读取长 closed 历史；或没有 3+ closed issue 前置压缩条件。
- uat_phase: first_pass
- 环境：local 文档审阅，可配合测试 fixture。
- 操作步骤：
  1. 打开 `df-uat/SKILL.md` 和 `df-fix/SKILL.md`。
  2. 检查入口步骤是否包含 compact 前置条件。
  3. 检查 `handoff.md` 读取是否限制为最新断点和相关段落。
- 期望结果：长上下文读取策略和 compact 前置条件明确。
- 不可替代证据：人工审阅记录和 compact helper gate。
- 自动证据：validation.md:V-003、V-004、V-005。
- 状态：waived，用户明确跳过人工 UAT；自动证据见 validation.md:V-003、V-004、V-005

### UAT-003：公开安装说明覆盖 shared protocol 或明确不依赖它

- 覆盖能力：shared protocol 不破坏公开安装和单 skill 可用性。
- 对应用户动作链：按 README 手动安装步骤判断复制后 skill 引用是否可达。
- 对应下游成功判据：若存在 `shared-protocols/` 引用，README/README.en 复制步骤覆盖该目录；若不采用外部协议，skill 内联规则足够完整。
- 对应失败信号：README 仍只复制 `df-*`，但 skill 引用了 `../shared-protocols/*.md`。
- uat_phase: first_pass
- 环境：local 文档审阅。
- 操作步骤：
  1. 打开 `README.md` 与 `README.en.md` 的安装段。
  2. 打开被修改的 `SKILL.md`，查找 `shared-protocols` 引用。
  3. 对照确认安装路径与引用路径一致。
- 期望结果：复制安装和 symlink 本机使用都不会出现断引用。
- 不可替代证据：README 中英文安装段和引用完整性检查结果。
- 自动证据：validation.md:V-002、V-006。
- 状态：waived，用户明确跳过人工 UAT；实际方案不引入 shared-protocols 依赖，自动证据见 validation.md:V-002、V-006
