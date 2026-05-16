当前改动引入了 skill 文档与 runtime accept gate 的语义不一致，并且 high-risk fix 缺矩阵行时的阻断语义不够明确；此外还有不应进入本轮提交的 untracked 输入目录。上述问题会导致流程卡死或绕过高风险覆盖门禁。

Full review comments:

- [P2] 同步运行时对 scope 外 P1 的处理 — /Users/yinghai/SynologyDrive/codex/devflow/df-accept/SKILL.md:30-30
  当 `review-findings.yaml` 里的 P0/P1 只有 `scope_decision: out_of_scope_followup` 或 `independent_followup` 并附带非阻断证据时，这里允许归档；但 `runtime/devflow_cli.py` 的 `is_blocking_review_finding()` 仍只识别 fixed/waived/manual_review/closed 等状态或 waiver/manual_review 记录，完全忽略 `scope_decision`。按新 `$df-review-loop` 规则正确记录的 scope 外 P1 仍会被 `accept_feature()` 卡住；需要同步 runtime gate 和测试，或不要在 skill 中放行这种状态。

- [P2] 阻断 high-risk 缺矩阵行时继续关闭 issue — /Users/yinghai/SynologyDrive/codex/devflow/df-fix/SKILL.md:93-93
  当目标是 `high-risk-fix` 且矩阵找不到对应能力行时，这里只要求写 handoff 建议并禁止补矩阵，没有要求暂停或回 `$df-plan`；随后步骤 8 在没有 `coverage_reference` 时仍可按 issue 关闭条件继续关闭。这样 high-risk 缺覆盖行的修复能绕过 README 里“high-risk 缺行必须回 `$df-plan`”的硬闸，应明确该场景不得继续修复/关闭，直到用户确认回 plan、waiver 或调整 scope。

- [P3] 统一 scope_decision 的可选值 — /Users/yinghai/SynologyDrive/codex/devflow/df-review-loop/SKILL.md:88-90
  这里把 `scope_decision` 枚举限定为 `in_scope` / `out_of_scope_followup` / `uncertain_scope`，但下一条规则和 df-accept 又要求识别 `independent_followup`。当 finding 属于独立后续项时，agent 要么遵守枚举而不会写 accept 规则里的值，要么写出不在本枚举内的状态，导致结构化记录和后续解析口径不一致；请把 `independent_followup` 纳入同一枚举，或统一映射为一个值。

- [P2] 移除本轮不应提交的 opusreviews 输入 — /Users/yinghai/SynologyDrive/codex/devflow/opusreviews/df_skills_review_round6_scope_explosion.md:1-1
  当前 untracked 变更包含 `opusreviews/`，但本 feature 的写入边界明确不提交这个输入目录；如果它随当前变更进入提交，会把外部 review 输入稿作为发布内容带进仓库，而不是 DevFlow runtime/skill 正本产物。提交前应删除、移动到临时区或加入忽略规则，只保留正式 evidence/文档产物。