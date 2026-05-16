# df-review-loop instructions

当前 feature：补齐 DevFlow runtime 发布依赖与 issue 压缩工具

本轮目标：提交前审查当前 uncommitted diff。重点审查本轮为吸收 Opus round6/round6b review 对 DevFlow skill 文档、README 和 runtime template 做的 scope 收缩改动。

当前允许 scope：
- `df-plan/SKILL.md`
- `df-execute/SKILL.md`
- `df-fix/SKILL.md`
- `df-review-loop/SKILL.md`
- `README.md`
- `README.en.md`
- `runtime/templates/plan.md`
- `devflow/shared/review_config.yaml`

当前明确非 scope：
- 不提交 `opusreviews/` 输入目录。
- 不重构 runtime helper 实现。
- 不改变业务项目代码。
- 不新增发布流程、UAT 流程或模型别名默认。

审查规则：
- 只报告可证明的 bug、数据风险、安全问题、回归风险或缺失测试。
- P0/P1 阻断；P2 仅在确定 bug 且位于当前 scope 内时阻断。
- 每条 finding 必须先给出 scope 判断：`in_scope`、`out_of_scope_followup` 或 `uncertain_scope`。
- scope 外 P0/P1 不要要求本轮直接修；应标为 follow-up 或要求暂停决策。
- 风格、偏好、计划外重构、超出当前 feature 的建议写为 waiver/follow-up，不作为阻断。

重点检查：
- 普通 P0/P1 review finding 是否在自动修复前被 `scope_decision` 约束，避免跨 checklist/issue 修补。
- coverage matrix 是否仍会诱导 `df-execute` 或 `df-fix` 在执行/修复期补全局矩阵。
- `df-fix` 是否仍会生成或依赖 `issue_closure_contract`。
- `df-review-loop` 是否仍会把本机模型别名作为共享默认。
- README 和 runtime template 是否与 skill 语义一致。
