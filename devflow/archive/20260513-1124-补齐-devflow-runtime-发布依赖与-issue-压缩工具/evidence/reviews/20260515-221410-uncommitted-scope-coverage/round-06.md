补丁新增了 scope 外 review finding 的审计规则，但当前判断顺序允许匹配的 manual_review/waiver 绕过这些必填审计字段，归档门禁会漏放不合规的 P0/P1 finding。

Review comment:

- [P2] 阻止 manual_review 绕过 scope 外审计字段 — /Users/yinghai/SynologyDrive/codex/devflow/runtime/devflow_cli.py:826-829
  当 P0/P1 finding 标记为 `out_of_scope_followup` 或 `independent_followup` 时，若同时有匹配的 `manual_review`/waiver，`review_resolution_matches()` 会先返回非阻断，导致缺少 `non_blocking_reason`、`followup_owner`、`no_overlap_evidence` 的 scope 外 finding 也能通过归档审计；这绕过了本次新增的“scope 外 P0/P1 必须具备可审计非阻断理由、后续归属和无交叉证据”的门禁。