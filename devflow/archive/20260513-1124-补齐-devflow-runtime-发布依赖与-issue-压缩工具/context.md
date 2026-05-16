---
title: "补齐 DevFlow runtime 发布依赖与 issue 压缩工具"
lane: "high-risk"
target_env: "local"
created_at: "2026-05-13 11:24:23 CST"
---

# 背景

## 目标

让公开 devflow-skills 仓库的 runtime helper、模板和 skill 调用路径形成可发布、可测试的单一事实源；补齐 df-uat issue 压缩 helper，并移除 run-gate shell=True 执行风险。

## 约束

- 不混入共享分派矩阵抽取
- 不改子代理模型策略
- 不删除历史 UAT 记录
- 不改变 df-* skill 自包含原则

## 成功标准

- 公开安装后 helper 路径可用
- compact-issues 能迁移历史并保留 history_ref
- run-gate 不再使用 shell=True
- 相关单测通过
- README 中英文同步

## 目标环境

local

## Codebase Map

- map_modules_read: ["skill-entrypoints", "runtime-helper", "docs-and-release"]
- codebase_map_waiver: standard/high-risk 车道缺失或过期时，必须先用 df-codebase-map 按 scope 刷新。

## Pre-Plan Discovery

- 用户/角色：DevFlow skills 维护者，需要判断外部 review 的结构性建议是否值得升 feature。
- 产品形态：公开 `devflow-skills` 仓库 + 本机 runtime helper 的组合发行物。
- 技术栈与运行环境：Markdown skills、Python runtime helper、`uv run python` 执行。
- 架构边界：skill 保持规则入口；runtime helper 承担确定性脚手架、issue 维护和 gate 执行；README 负责公开安装说明。
- 合同草案：skill 中出现硬阻断时必须有可执行 helper 或明确人工替代路径；gate 执行默认 `shell=False`。
- 当前垂直切片：runtime packaging、`compact-issues`、`run-gate` 安全化和文档同步。
- 后续 backlog：共享分派矩阵/最终回复抽取、constraint-audit 输出结构化。
- 已锁定决定：本 feature 不执行共享抽取；不提交 review 输入目录；先计划，等待 `$df-execute`。
- 未决问题：执行期需最终确认公开仓库 runtime 落点和 `npx skills add` 对非 skill 目录的安装行为。
