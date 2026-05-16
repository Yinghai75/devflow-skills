The changes introduce two workflow regressions: the repo now points at a new active feature before the previous validated one can be accepted, and the new mandatory compaction gate depends on helper behavior that does not match the documented contract. Those issues are enough to make the patch incorrect.

Full review comments:

- [P1] Keep the validated feature active until it is archived — /Users/yinghai/SynologyDrive/codex/devflow/devflow/active/.current:1-1
  Repointing `devflow/active/.current` here strands `20260513-1124-补齐-devflow-runtime-发布依赖与-issue-压缩工具` even though `devflow/roadmap.md` still says that feature is waiting for `$df-accept`. `df-accept`, `df-status`, and the other `df-*` flows resolve the “当前 feature” through `.current`, so a normal `$df-accept` will now audit the new planned feature instead of archiving the already-validated one; finishing the pending acceptance would require manual pointer surgery.

- [P1] Don't front-load compaction on a helper that still shrinks open issues — /Users/yinghai/SynologyDrive/codex/devflow/df-fix/SKILL.md:16-16
  This new entry gate assumes `compact-issues` will preserve active open/retest issues, but `runtime/devflow_issues.py::_should_compact` still compacts any block longer than `max_issue_lines` unless it has pending-retest markers. In a feature with 3+ closed issues and one long open issue, following this rule will compact the active issue and then fail the new “open/retest issue 未被压缩” check, blocking `$df-fix` (and the matching `$df-uat` rule) until the helper behavior or the trigger contract is changed.