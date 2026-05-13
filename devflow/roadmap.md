# DevFlow Roadmap

## 当前 feature

### 补齐 DevFlow runtime 发布依赖与 issue 压缩工具

状态：待 UAT/验收

目标：让公开 devflow-skills 仓库的 runtime helper、模板和 skill 调用路径形成可发布、可测试的单一事实源；补齐 `compact-issues` helper，并移除 `run-gate` 的 `shell=True` 风险。

范围：runtime helper、模板、测试、`df-uat`/相关 skill 规则、README 中英文安装与机制说明。

非目标：共享分派矩阵抽取、最终回复格式抽取、子代理模型策略调整。

## 后续 backlog

### 评估共享分派矩阵与最终回复格式抽取

状态：保留

目标：在不破坏单 skill 自包含的前提下，评估是否需要 shared policy 或生成式同步机制减少重复。

非目标：本 feature 不做该抽取。

### 评估 constraint-audit 输出结构化

状态：保留

目标：如后续实际使用中发现人工审计成本高，再评估是否增加结构化输出或 CLI 辅助。

非目标：不因本轮 review 单独扩大实现范围。
