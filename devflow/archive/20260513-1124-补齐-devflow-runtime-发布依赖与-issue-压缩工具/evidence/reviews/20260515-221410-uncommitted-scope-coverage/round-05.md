补丁引入了 df-fix 与生成计划模板/README 之间的关键门禁口径不一致，会导致缺少覆盖矩阵行的高风险场景被不同技能按不同规则处理。其余代码和测试未发现明确阻断问题。

Review comment:

- [P2] Align the missing-row gate with feature lanes — /Users/yinghai/SynologyDrive/codex/devflow/df-fix/SKILL.md:93-93
  在找不到 `Capability Coverage Matrix` 对应行时，这里按 `fix_lane` 放行 `fast-fix` / `scoped-fix`，但同一改动里的 plan 模板和 README 按 feature lane 规定 `high-risk` feature 必须暂停回 `$df-plan`/waiver/scope 决策。这样高风险 feature 中被分流为 `scoped-fix` 的缺行 issue 会被直接修复关闭，绕过高风险覆盖硬闸；反过来 standard feature 的 `high-risk-fix` 又会和模板口径冲突。建议统一使用 feature lane 或 fix lane，并明确二者交叉时的优先级。