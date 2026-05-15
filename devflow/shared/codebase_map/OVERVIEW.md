# 仓库索引

## Atlas

- `df-*/SKILL.md`：11 个 DevFlow skill 入口，要求单 skill 自包含。
- `README.md` / `README.en.md`：公开安装、机制总览和技能表。
- `df-regression/scripts/regression_feature.py`：已归档 feature 回归 helper。
- `runtime/`：公开仓库 runtime helper 正本、templates、tests；同步到 `~/.codex/local/devflow/` 后供 skills 调用。

## 模块卡片

- `modules/skill-entrypoints.md`：skill 指令合同、跨 skill 约束和 README 同步。
- `modules/runtime-helper.md`：DevFlow CLI、issue 压缩 helper、模板和测试。
- `modules/docs-and-release.md`：公开安装说明、发布口径和敏感信息边界。
- `df-review-loop/SKILL.md`：Codex review 自动循环，供 df-execute/df-fix 调用。

## 当前风险

- 修改 `runtime/` 后必须同步 `~/.codex/local/devflow/`，否则 skills 实际调用旧 helper。
- `compact-issues` 必须同时保护活跃视图可读性、历史可追溯性和下一个 UAT id 唯一性。
- `run_gate` 必须保持 `shell=False` 和 shell 控制符拒绝，避免门禁命令注入面。
