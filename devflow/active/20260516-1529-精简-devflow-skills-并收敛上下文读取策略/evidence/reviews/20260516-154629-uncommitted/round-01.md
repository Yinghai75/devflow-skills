The patch introduces a new shared-protocol dependency that the primary `skills add` installation flow does not install, and it adds a df-fix precheck that can block repairs for long open issues. Those are functional regressions in the repository’s published skill workflow.

Full review comments:

- [P1] Keep shared rules inline or install `shared-protocols/` with `skills add` — /Users/yinghai/SynologyDrive/codex/devflow/df-execute/SKILL.md:22-22
  These new `../shared-protocols/*.md` references break the repository’s advertised `npx skills add …` install path. I verified that `skills add` only installs the 12 `df-*` directories into `.agents/skills/*`; it does not copy the sibling `shared-protocols/` directory, so an installed skill like `df-execute` ends up with a dangling `../shared-protocols/context-reading.md` path. In that setup the agent loses the delegated rules entirely, which means Codex/Claude users following the default install flow get incomplete skill behavior after this change.

- [P2] Do not run `compact-issues` before fixing a long open issue — /Users/yinghai/SynologyDrive/codex/devflow/df-fix/SKILL.md:16-16
  The new df-fix entry gate now compacts whenever any issue block exceeds 50 lines, but `compact_issues()` compacts oversized blocks regardless of status. That means a real `status: open` target issue with >50 lines will be stubbed before repair starts, and the subsequent invariant here (`open/retest issue 未被压缩`) can never hold. In practice, the long issues that most need `df-fix` become unreadable or blocked at entry instead of being repairable.