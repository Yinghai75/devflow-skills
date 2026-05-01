---
name: df-fix
description: "对 DevFlow UAT issue 执行 plan → execute → validate → UAT 闭环；根因清楚时直接修复，根因不清时先调查。用户提到 $df-fix、df-fix、修 UAT issue 时使用。"
metadata:
  short-description: "修复 DevFlow UAT issue"
---

# df-fix

围绕当前 feature 的 `issues.yaml` 修复 UAT issue。

## 流程

1. 读取 `issues.yaml` 中 open issue，确认目标 issue。
2. 读取 `plan.md`、`validation.md`、相关代码和测试。
3. 若修复会扩大影响面，先回到 `$df-plan` 更新 Impact Map、门禁和 checklist。
4. 根因明确：按 TDD 写失败测试或复现样本，确认 RED 后实现。
5. 根因不清：使用系统化调试，先记录假设、证据和最小复现。
6. 跑 issue 对应门禁和 feature 关键门禁；注册门禁必须用 `run-gate` 生成 `evidence/manifest.json`，不能只在文档里写“已通过”。
7. 更新 `issues.yaml`、`uat.md`、`state.yaml`、`handoff.md`。
8. 每个 UAT issue 默认一个原子修复提交；提交前检查 `git status --short`，只暂存该 issue 的修复、测试和证据文件，不混入无关改动或用户明确保留的不提交文件。

修复完成不等于最终验收；最后仍需 `$df-accept`。
