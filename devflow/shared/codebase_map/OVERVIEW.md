# 仓库索引

## Atlas

- `df-*/SKILL.md`：10 个 DevFlow skill 入口，要求单 skill 自包含。
- `README.md` / `README.en.md`：公开安装、机制总览和技能表。
- `df-regression/scripts/regression_feature.py`：已归档 feature 回归 helper。
- `/Users/yinghai/.codex/local/devflow/`：当前本机 runtime helper、templates、tests；尚未纳入公开仓库。

## 模块卡片

- `modules/skill-entrypoints.md`：skill 指令合同、跨 skill 约束和 README 同步。
- `modules/runtime-helper.md`：本机 DevFlow CLI、模板和测试。
- `modules/docs-and-release.md`：公开安装说明、发布口径和敏感信息边界。

## 当前风险

- 公开仓库 skills 引用本机 runtime 路径，发布安装与真实运行依赖可能脱节。
- `df-uat` 已把 issue 压缩设为硬阻断，但 runtime 没有对应 helper。
- 本机 `run_gate` 仍使用 `shell=True` 执行门禁命令。
