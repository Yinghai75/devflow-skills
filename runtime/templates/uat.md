# UAT 记录

## 人工验收记录

暂无。

## UAT 断点说明

- 当前断点由 `state.yaml`、`handoff.md` 和 `checklist.yaml` 的 `uat_ready` 派生；本文件不手工维护当前断点状态。
- UAT 项的来源断点写在各 UAT 条目的“来源断点”字段，并应与 `plan.md#capability-coverage-matrix` 保持一致。
- 解锁条件：本断点全部通过或 waiver 后，如仍有 pending checklist，状态回到 `ready_for_execute`；全部完成后状态先写为 `validated`，再进入 `$df-accept`。
- 断点边界：只验收本断点对应的用户可感知阶段成果，不顺带验收后续 DF 能力。

## Capability Coverage Matrix 对齐项

> UAT 项来自 `plan.md#capability-coverage-matrix`。这里只写操作步骤、期望结果和复测记录，不维护额外覆盖矩阵。

### UAT-001：待补

- 覆盖能力：
- 来源断点：
- 对应用户动作链：
- 对应下游成功判据：
- 对应失败信号：
- uat_phase: first_pass
- 环境：
- 操作步骤：
  1. 待补
- 期望结果：
- 不可替代证据：
- 自动证据：
- 状态：待人工 UAT
