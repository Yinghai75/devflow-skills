The acceptance gate now rejects a valid audited out-of-scope finding when the audit details are stored in the existing waiver/manual_review sections rather than duplicated on the finding. This can incorrectly block feature archival.

Review comment:

- [P2] Honor audited waiver/manual_review records for scoped followups — /Users/yinghai/SynologyDrive/codex/devflow/runtime/devflow_cli.py:826-827
  When a P0/P1 finding is marked `out_of_scope_followup` or `independent_followup`, this early return only inspects audit fields on the finding itself and bypasses the existing matching `waivers` / `manual_review` records. In the documented workflow those audit details may live in the resolution record, so a finding with a matching manual review containing `non_blocking_reason`, follow-up owner, and no-overlap evidence is still rejected at accept time.