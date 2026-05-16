# Docs 与发布模块

## 关键文件

- `README.md`
- `README.en.md`
- `.gitignore`
- `AGENTS.md`
- `CLAUDE.md`

## 边界与风险

- README 必须反映真实可安装内容，不得暗示未随仓库发布的 helper 已自动可用。
- 英文 README 可用英文说明，但 DevFlow 状态字面量保留中文。
- `opusreviews/`、会话日志、本机路径样本和敏感信息不纳入发布提交，除非用户明确要求。

## 惯例与测试

- README 中英文同步更新。
- 手动安装步骤复制 `df-*`；runtime helper 仍同步到 `~/.codex/local/devflow/`。
- 发布前检查 `git status --short`，区分正式 DevFlow 产物、review 输入和临时文件。
- 用 `git diff --check` 做基础收口。
