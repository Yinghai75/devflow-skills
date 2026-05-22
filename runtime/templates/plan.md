---
title: "{{title}}"
lane: "{{lane}}"
status: draft
created_at: "{{created_at}}"
map_modules_read: []
---

# 计划

## 目标

{{goal}}

## 非目标

- 待补充。

## 方案

- 待补充。

## 架构自审

- 架构接缝与公共接口：待补充。
- 公共核心、变体适配层与不变量归属：待补充。
- 接缝替换测试：待补充，说明新增/变更行为是否能通过公共接口或适配层替换，而不迫使调用方跟随内部细节变化。
- 深模块检查：待补充，说明新增模块是否隐藏复杂度；若只是透传层，写合并或重设边界方案。
- 回流信号：待补充，说明哪些发现会触发 architecture adjustment 回 `$df-plan`。

## 写入边界与代码地图

- map_modules_read: []
- 新代码放置规则：待从 scoped codebase map 补充。
- 禁止修改区域：待从 scoped codebase map 补充。
- 受保护接口：待从 scoped codebase map 补充。

## Checklist

- 见 `checklist.yaml`。

## Capability Coverage Matrix

> 单一能力覆盖矩阵。`df-execute` coverage verification、`df-review-loop` coverage review 和 `df-accept` 归档审计都只核验本表，不另建额外验证矩阵。`df-fix` 只把当前 issue 对应行作为只读参考；没有对应行时，feature lane 或 fix lane 任一为 high-risk 都必须暂停，直到回 `$df-plan`、写 waiver 或调整 scope；非 high-risk 的 fast/scoped 修复才可按 q1/q2、RED -> GREEN 和回归面关闭。不能在修复期补全局矩阵。`UAT 断点`列用于声明哪个 DF 完成后可停下验收，推荐写成 `CP-x / checklist.yaml:DF-xxx -> UAT-xxx`；`CP-x` 只是阅读标签，真正执行绑定仍是 checklist item 的 `uat_ready`。这不是第二张矩阵。`fast` / `standard` 车道中不适用的高风险列可写 N/A 或 waiver；`high-risk` 车道必须填满所有列。

| 用户可见能力 | 用户动作链 | 下游成功判据 | 失败信号 | 实现项 | validation | UAT 项 | UAT 断点 | 不可替代证据 | waiver/残余风险 |
|---|---|---|---|---|---|---|---|---|---|
| 待补充 | 待补充 | 待补充 | 待补充 | checklist.yaml:待补充（实现项） | validation.md:待补充 | uat.md:UAT-001 | CP-待补充 / checklist.yaml:待补充（实现项） -> UAT-001 | 待补充 | 无 |

## UAT 断点策略

- 是否需要分段 UAT-ready 断点：待补充。
- 首个用户可感知阶段成果：待补充；若没有早期断点，说明 waiver/残余风险。
- 推荐断点阶梯：工作台/入口可见 -> 主输入解析可试 -> 外部数据源/真实查询可见 -> 业务规则可验 -> 人工介入闭环可验 -> 正式输出物或确认动作可验 -> 持久化、安全、集成收口。
- 断点声明规则：只在对应实现 checklist item 上写 `uat_ready`；不得新增“执行人工 UAT”类 checklist item。
- `uat_ready` 最小字段：`level`（required/advisory）、`uat_items`、`reason`。
- 粗断点自检：一个 `uat_ready` 不得同时覆盖 UI + 输入解析 + 外部数据 + 业务计算 + 输出，或一次打包 4 个以上 UAT 项；确需如此时写 waiver。
- 无断点时说明原因：待补充。

## 验证计划

- 见 `validation.md`。
