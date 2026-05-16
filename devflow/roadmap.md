# DevFlow Roadmap

## 前序待验收

### 补齐 DevFlow runtime 发布依赖与 issue 压缩工具

状态：validated，等待 `$df-accept`

目标：让公开 devflow-skills 仓库的 runtime helper、模板和 skill 调用路径形成可发布、可测试的单一事实源；补齐 `compact-issues` helper，并移除 `run-gate` 的 `shell=True` 风险。

说明：该 feature 已完成实现和验证，本轮只读取其背景，不改写其正式产物。

## 已归档

### 精简 DevFlow skills 并收敛上下文读取策略

状态：archived

目标：在保留单 skill 可读关键规则的前提下，吸收 opus 计划中合理的 skill 精简、handoff/issues 读取策略和 issues 前置压缩规则，降低上下文消耗且不削弱 DevFlow 执行合同。

范围：`df-plan`、`df-execute`、`df-fix`、`df-uat`、`df-review-loop`、README 中英文、shared protocol 发布可达性、compact-issues 入口规则、codebase map。

归档：`devflow/archive/20260516-1529-精简-devflow-skills-并收敛上下文读取策略`

说明：用户明确跳过人工 UAT，作为内部 DevFlow skill/runtime 治理任务的 waiver；机器门禁、review-loop 和覆盖审计已收口。

## 后续 backlog

### 评估 constraint-audit 输出结构化

状态：保留

目标：如后续实际使用中发现人工审计成本高，再评估是否增加结构化输出或 CLI 辅助。

非目标：不因本轮 review 单独扩大实现范围。
