# 断点

- 时间：2026-05-15 15:47:25 CST
- 当前状态：`$df-accept` 前 review comment 已处理；实现和本机 runtime 副本已同步。
- 已完成：
  - 建立仓内 `runtime/` 正本，包含 CLI、templates、tests。
  - `run-gate` 改为 `shell=False` argv 执行，并拒绝 shell 控制符。
  - 新增 `compact-issues` helper，压缩历史到 `evidence/` 并保留 `history_ref`。
  - README 中英文和 `df-uat` 规则已同步。
  - Review fix：`compact-issues` 重复运行不再重压已有 `history_ref`；UAT issue 标题/描述写入 YAML 安全标量；`df-uat` helper 路径改为 `~/.codex/local/devflow/devflow_cli.py`。
  - Review fix 2：仅跳过真正 compact stub；带旧 `history_ref` 但新增长调查记录的 active issue 仍会再次压缩。
  - Review fix 3：兼容旧版已压缩 stub；读取时允许旧版一层标量字段，生成新 stub 仍只保留精简字段。
- 验证：
  - 仓内 runtime 单测 PASS，40 tests。
  - 本机 runtime 单测 PASS，40 tests。
  - `df-plan` / `df-uat` quick_validate PASS。
  - `devflow-runtime-unit` 和 `git-diff-check` gate PASS，最新证据见 `evidence/devflow-runtime-unit-20260515-154715.log`、`evidence/git-diff-check-20260515-154715.log` 与 `evidence/manifest.json`。
- 下一步：
  - 归档前先处理当前未提交 diff；工作区未收口前不得直接归档。
  - `opusreviews/` 仍是未跟踪输入目录，未纳入发布提交。
