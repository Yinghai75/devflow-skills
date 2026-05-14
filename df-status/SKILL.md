---
name: df-status
description: "保存或恢复 DevFlow 当前 feature 断点；df-status 默认写 handoff.md，df-status -r 在 /new 后恢复上下文。用户提到 $df-status、df-status、DevFlow 状态或恢复时使用。"
metadata:
  short-description: "保存/恢复 DevFlow 断点"
---

# df-status

管理 DevFlow 跨会话上下文。

## 保存断点

默认保存当前状态：

`uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> status --summary "<当前状态>" --next "<下一步1>,<下一步2>"`

保存前读取当前 feature 的 `state.yaml` 和 `checklist.yaml`，摘要要写清：

- 当前做到哪一项。
- 已改哪些关键文件。
- 已跑哪些验证，结果是什么。
- 下一步最小动作。

## 恢复断点

`df-status -r` 时运行：

`uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> status -r`

然后读取输出中的 feature 目录，并补读 `context.md`、`plan.md`、`checklist.yaml`、`validation.md`、`issues.yaml`。若存在 `review-findings.yaml`，同时读取其 `review_loop_status`、未处理 P0/P1 和 waiver/manual_review 记录。

## 下一步

- 保存断点后，提示下次新会话使用 `$df-status -r` 恢复。
- 恢复断点后，读取 `handoff.md` 的下一步，提示继续 `$df-execute`、`$df-uat` 或 `$df-fix`。
