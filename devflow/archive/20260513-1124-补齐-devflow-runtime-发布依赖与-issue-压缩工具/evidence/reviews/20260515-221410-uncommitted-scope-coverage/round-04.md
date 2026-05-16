The runtime accept gate can archive an explicitly uncertain P0/P1 review finding when it is waived, contradicting the new contract. The current untracked change set also includes raw review evidence with local paths/session logs that should not be submitted.

Full review comments:

- [P2] Fail closed on uncertain review scope — /Users/yinghai/SynologyDrive/codex/devflow/runtime/devflow_cli.py:826-827
  When a P0/P1 finding has `scope_decision: uncertain_scope` but also has a matching waiver/manual_review record or a resolved status, `accept_feature` still returns OK because the resolution checks short-circuit before any uncertain-scope block. The updated df-accept contract says `uncertain_scope` must still block archival, so this lets features with unresolved scope uncertainty be archived.

- [P2] Drop raw review logs with local paths — /Users/yinghai/SynologyDrive/codex/devflow/devflow/active/20260513-1124-补齐-devflow-runtime-发布依赖与-issue-压缩工具/evidence/reviews/20260515-221410-uncommitted-scope-coverage/round-01.md:5-5
  This untracked evidence file contains raw review output with absolute `/Users/yinghai/...` workspace paths, and the same evidence directory includes JSONL command/session transcripts. If these untracked files are committed with the change, they violate the repo policy against submitting session logs or local workspace paths and make the published DevFlow artifact non-portable.