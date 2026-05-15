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

## 写入边界与代码地图

- map_modules_read: []
- 新代码放置规则：待从 scoped codebase map 补充。
- 禁止修改区域：待从 scoped codebase map 补充。
- 受保护接口：待从 scoped codebase map 补充。

## Checklist

- 见 `checklist.yaml`。

## Capability Coverage Matrix

> 单一能力覆盖矩阵。`df-execute` coverage verification、`df-review-loop` coverage review 和 `df-accept` 归档审计都只核验本表，不另建额外验证矩阵。`df-fix` 只把当前 issue 对应行作为只读参考；没有对应行时，feature lane 或 fix lane 任一为 high-risk 都必须暂停，直到回 `$df-plan`、写 waiver 或调整 scope；非 high-risk 的 fast/scoped 修复才可按 q1/q2、RED -> GREEN 和回归面关闭。不能在修复期补全局矩阵。`fast` / `standard` 车道中不适用的高风险列可写 N/A 或 waiver；`high-risk` 车道必须填满所有列。

| 用户可见能力 | 用户动作链 | 下游成功判据 | 失败信号 | 实现项 | validation | UAT 项 | 不可替代证据 | waiver/残余风险 |
|---|---|---|---|---|---|---|---|---|
| 待补充 | 待补充 | 待补充 | 待补充 | checklist.yaml:DF-001 | validation.md:待补充 | uat.md:待补充 | 待补充 | 无 |

## 验证计划

- 见 `validation.md`。
