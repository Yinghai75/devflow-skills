---
title: "补齐 DevFlow runtime 发布依赖与 issue 压缩工具"
lane: "high-risk"
status: planned
created_at: "2026-05-13 11:24:23 CST"
map_modules_read: ["skill-entrypoints", "runtime-helper", "docs-and-release"]
---

# 计划

## 目标

让公开 devflow-skills 仓库的 runtime helper、模板和 skill 调用路径形成可发布、可测试的单一事实源；补齐 df-uat issue 压缩 helper，并移除 run-gate shell=True 执行风险。

## 非目标

- 不抽取共享分派矩阵或最终回复模板。
- 不调整子代理模型、角色或 `subagent_handoff.md` 策略。
- 不改变已发布 skill 的核心流程语义。
- 不把 `opusreviews/` 输入目录作为发布内容提交。

## 方案

1. 先保留当前 legacy roadmap 小修 diff，不回退；把结构性建议拆成本 feature 执行。
2. 建立 runtime 发布正本：把当前本机 `/Users/yinghai/.codex/local/devflow/` 的 CLI、templates、tests 作为待纳入公开仓库的 runtime 源；执行期确认最终落点，优先选择仓内 `runtime/`，安装说明同步到 `~/.codex/local/devflow/` 目标路径。
3. 为 `df-uat` 的硬阻断补 `compact-issues`：从活跃 `issues.yaml` 抽离长历史到 feature-local `evidence/`，活跃 issue 保留当前失败面、状态、最新证据和 `history_ref`；压缩后必须保证 YAML 可解析、历史 id 可追溯、下一个 UAT id 不冲突。
4. 硬化 `run-gate`：门禁命令仍由 `gate_registry.yaml` 注册，但 runtime 用 `shlex.split` 得到 argv 后以 `shell=False` 执行；拒绝 shell 控制符、重定向和占位命令。
5. 同步 skill 与 README：`df-uat` 写明 helper 命令，`df-execute`/`df-plan` 只保留必要 runtime 规则，README 中英文说明 runtime helper 安装/同步口径。
6. 用单测、skill 校验和 `git diff --check` 收口；本地安装副本同步作为执行期单独 checklist 项，不在计划阶段改运行代码。

## 写入边界与代码地图

- map_modules_read: ["skill-entrypoints", "runtime-helper", "docs-and-release"]
- 新代码放置规则：runtime helper 源码优先放仓内 `runtime/`；skill 只写调用合同，不内嵌长脚本。
- 禁止修改区域：不改 `asset/` 图片；不提交 `opusreviews/`；不删除正式 DevFlow 产物。
- 受保护接口：`df-plan`/`df-execute` 授权边界、`df-uat` issue id 语义、`run-gate` evidence manifest 格式、README 10-skill 总览。

## Checklist

- 见 `checklist.yaml`。

## 验证计划

- 见 `validation.md`。

## 预期提交分组

- `docs(devflow): plan runtime helper packaging feature`
- `feat(runtime): package devflow cli and compact issues helper`
- `docs(skills): document runtime helper install and usage`
