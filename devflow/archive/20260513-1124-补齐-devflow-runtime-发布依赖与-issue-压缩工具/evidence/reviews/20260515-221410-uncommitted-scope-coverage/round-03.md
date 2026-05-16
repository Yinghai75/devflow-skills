The runtime/template changes mostly align with the new scoped review behavior, but the generated plan template weakens the high-risk df-fix missing-matrix-row gate and can mislead future fixes. This should be corrected before the patch is considered safe.

Review comment:

- [P2] Preserve the high-risk missing-row stop gate — /Users/yinghai/SynologyDrive/codex/devflow/runtime/templates/plan.md:36-36
  When a generated high-risk feature later runs `df-fix` and the target issue has no matching Capability Coverage Matrix row, this template tells the agent to close via q1/q2 + RED/GREEN/regression instead of pausing; that contradicts the updated `df-fix`/README rule that high-risk missing rows must stop until re-plan, waiver, or scope adjustment. Because new `plan.md` files are read as the feature-local source during fixes, this can let high-risk issues bypass the intended coverage gate.