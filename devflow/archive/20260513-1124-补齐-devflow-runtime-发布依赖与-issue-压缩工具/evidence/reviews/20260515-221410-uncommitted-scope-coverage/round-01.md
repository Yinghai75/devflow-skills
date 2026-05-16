补丁的主要 scope 收缩方向是合理的，但新增规则与既有 df-execute/df-accept 收口门禁存在不一致，会导致 fast 车道和 scope 外 review finding 在后续流程中被误阻断。

Full review comments:

- [P2] 让 fast 车道的覆盖收口按车道判定 — /Users/yinghai/SynologyDrive/codex/devflow/df-plan/SKILL.md:121-121
  当 feature 被分到 `fast` 且计划按这里只填「用户可见能力、实现项」，把 validation/UAT/证据列写成 `N/A` 时，`df-execute` 的 goal-backward gate 仍无条件要求每个矩阵行都有运行态/机器验证证据和 UAT 项/明确 waiver。结果 fast 任务会在收口时被误判 coverage gap，或被迫补不必要的验证/UAT，抵消本次按车道降级的目的；这里需要同步定义 N/A/waiver 如何让下游 gate 放行，或让 df-execute 按 lane 判定。

- [P2] 为 scope 外 P1 写入 df-accept 可识别的状态 — /Users/yinghai/SynologyDrive/codex/devflow/df-review-loop/SKILL.md:90-90
  当 review 报出当前 scope 外但可独立后置的 P0/P1 时，这里要求只记录 `out_of_scope_followup`/`independent_followup` 而不修；但现有 `df-accept` 只允许最终 `review_loop_status: pass` 或未修 finding 有明确 waiver/manual_review，且会阻断未处理 P0/P1。这样一个按本规则正确后置的 P1 仍会在归档时卡死，或逼调用方把 follow-up 伪装成 waiver；需要把非阻断 follow-up 的最终状态纳入 accept 规则，或在这里要求同时写入可审计的 waiver/manual_review。