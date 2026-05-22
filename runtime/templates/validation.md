# 验证计划

## 基础验证

- 待补充。

## Capability Coverage Matrix 核验

- 矩阵来源：`plan.md#capability-coverage-matrix`。
- 用户动作链：待补充。
- 下游成功判据：待补充。
- 失败信号：待补充。
- 不可替代证据：待补充。
- 本文件只记录每个矩阵行对应的 validation 项；不得另建额外验证或关闭矩阵。
- UAT 断点核验事实源：`plan.md#capability-coverage-matrix` 的 `UAT 断点`列与 `checklist.yaml` 的 `uat_ready`；本文件不重复维护断点清单。

## Blast Radius Guard

### Impact Map

- 待补充。

### Protected Surfaces

- 待补充。

### Gate Selection

- 待补充。
- 涉及跨模块编排时，至少选择一个 integration/e2e 门禁。
- 目标环境为 dev-full/online 或涉及 Dify/容器/线上对象时，发布闭环门禁与自检项必须进入 checklist。

### Golden Set Delta

- 待补充。

### TDD/RED Evidence

- 待补充。
- 测试表面：RED/回归测试默认绑定公共接口、用户可见行为或外部可观察状态；如需 mock，仅 mock 外部 IO、平台或时间等边界并说明原因。

### Waiver

- 无。

{{fast_note}}
