<div align="center">

# DevFlow Skills

![DevFlow Skills](./asset/devflow-skills-cover-clean.png)

**English** · [中文](./README.md)

**A lightweight AI coding workflow for individual developers: 10 skills, about 875 instruction lines, covering planning, execution, UAT, fixes, archival, and recovery**

<p>
  <img src="https://img.shields.io/badge/status-beta-F59E0B?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/skills-10-6366F1?style=flat-square" alt="Skills"/>
  <img src="https://img.shields.io/badge/instructions-~875-10B981?style=flat-square" alt="Instructions"/>
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"/>
</p>

</div>

---

## Why DevFlow

DevFlow solves a narrow problem:

**One developer + one coding agent, moving one development task to acceptance while keeping it recoverable and archivable.**

It is not a heavy specification platform, and it does not try to let an agent take over an entire project. DevFlow writes state into the repository so authorization, evidence, handoffs, UAT failures, and release checks all return to the same facts.

Rough comparison from current public repositories:

| Framework | Main units | Agent config | Rough instruction footprint |
| --- | --- | --- | --- |
| [Superpowers](https://github.com/obra/superpowers) | 14 skills | 1 agent file | about 3,200 lines |
| [GSD](https://github.com/gsd-build/get-shit-done) | 99 workflows | 33 agent files | about 47,600 lines |
| **DevFlow** | **10 skills** | **5 lightweight sub-agent roles** | **about 875 lines** |

Core tradeoffs:

- **State lives in the repo**: goals, plans, checklists, UAT notes, issues, evidence, handoffs, and archives live under `devflow/`.
- **Planning and execution are separate**: `df-plan` stops at review; code changes require explicit `$df-execute` or equivalent execution wording.
- **Layered context reads**: read `codebase_map/OVERVIEW.md` first, then only the module cards that match the task.
- **Evidence before claims**: key gates need script output or runtime probes; handwritten "passed" text is not evidence.
- **UAT issues are closed as a loop**: capture the full feedback round first, then enter `df-fix` by issue id.

---

## Install

### Skills CLI

```bash
npx skills add https://github.com/Yinghai75/devflow-skills
```

Use this in agent environments that support installing GitHub skill repositories through `npx skills`, such as Codex CLI and Claude Code.

### Manual Install

```bash
# Codex CLI
mkdir -p ~/.codex/skills
git clone https://github.com/Yinghai75/devflow-skills.git /tmp/devflow-skills-codex
cp -R /tmp/devflow-skills-codex/df-* ~/.codex/skills/

# Claude Code
mkdir -p ~/.claude/skills
git clone https://github.com/Yinghai75/devflow-skills.git /tmp/devflow-skills-claude
cp -R /tmp/devflow-skills-claude/df-* ~/.claude/skills/
```

For other agents, copy the `df-*` directories into that agent's skills directory. Each `df-*` directory is an independent skill with `SKILL.md` as its entry point.

---

## Quick Start

```bash
/df-plan        # Start and plan a feature: create the directory, classify risk, write plan and UAT matrix
/df-backlog     # Later item: record a roadmap/backlog item without interrupting current work
/df-codebase-map # Code map: maintain OVERVIEW + matching module cards to save context
/df-constraint-audit # Constraint audit: find duplicated or conflicting gates, status semantics, and contracts
/df-execute     # Execute the checklist after explicit authorization
/df-status -r   # New session: restore the current feature and handoff
/df-uat         # Manual UAT: guide real-path testing and capture the full feedback round
/df-fix         # Fix UAT issues: triage, RED, patch, validate, close
/df-regression  # Post-acceptance regression: handle follow-up UAT issues for archived features
/df-accept      # Archive: check gates, UAT, codebase map, truth docs, and golden sets
```

---

## Workflow

```text
┌─────────┐    ┌────────────┐    ┌────────┐    ┌───────────┐
│ df-plan │───▶│ df-execute │───▶│ df-uat │───▶│ df-accept │
└─────────┘    └────────────┘    └────────┘    └───────────┘
     │              ▲                │              │
     ▼              │                ▼              ▼
┌────────────┐ ┌────────────────┐ ┌────────┐    ┌───────────────┐
│ df-backlog │ │ df-codebase-map │ │ df-fix │◀──│ df-regression │
└────────────┘ └────────────────┘ └────────┘    └───────────────┘

df-status: save a handoff at any stage / restore with df-status -r
df-constraint-audit: read-only constraint drift audit at any stage
```

Risk lanes are classified by `df-plan`:

- **fast**: low-risk docs, small fixes, pure display, or local logic.
- **standard**: normal multi-file development through plan, execute, UAT, fix, and accept.
- **high-risk**: state machines, production releases, data writes, cross-module orchestration, real browser paths, or external sites. Requires RED evidence, blast-radius gates, and release checks.

---

## Current Mechanics

### Layered Codebase Map

`df-codebase-map` maintains `devflow/shared/codebase_map/`:

- `OVERVIEW.md` is always loaded, capped at 30 lines, and only contains a directory atlas, dependency graph, and module card index.
- `modules/*.md` cards are capped at 30 lines and only contain key files, boundaries and risks, conventions and tests.
- `df-plan` and `df-fix` read only OVERVIEW plus matching module cards, then record `map_modules_read`.
- `df-execute` and `df-fix` refresh only cards touched by each git checkpoint.
- `df-accept` performs the final stale gate to ensure touched cards were refreshed.

The goal is context economy: the common layer gives the atlas, and the detail layer loads only a few relevant cards.

### Platform And Contract Evidence Gate

When adding or changing platform capabilities, public APIs, DSL/config syntax, permission declarations, runtime assumptions, or cross-module contracts, implementation cannot rely on inference alone.

Accepted evidence is limited to:

- nearby exact existing patterns;
- official documentation;
- runtime probes.

If no evidence is found, the agent can only investigate or add probes. Mock tests do not prove that a platform capability exists.

### Single Source Of Truth And Constraint Audit

`df-plan` requires gate behavior, status semantics, and interface contracts in `checklist.yaml` and `validation.md` to use references such as script path plus pass/fail line numbers, instead of restating script logic in prose.

`df-constraint-audit` read-only scans the active feature for:

- gate descriptions that conflict with actual Python gate behavior;
- status drift across `state.yaml`, `acceptance.md`, `handoff.md`, `issues.yaml`, and `uat.md`;
- duplicated descriptions of the same gate behavior, contract, or status semantics.

### UAT Intake Before Fixing

`df-uat` is both the manual UAT entry point and the issue intake layer. If one feedback round contains multiple errors, screenshots, field problems, session symptoms, or retest results, the full batch must be captured first:

- split by user-visible failure surface;
- deduplicate, reopen, or register issues;
- update `issues.yaml`, `uat.md`, `handoff.md`, and `state.yaml`;
- stop after recording when the user says to only record, only read, or not fix yet.

Only after the full feedback round is captured may the agent choose one explicit issue id and enter `df-fix`.

### df-fix Triage And Stop-Loss

`df-fix` handles open UAT issues in the active feature and triages before code changes:

- **fast-fix**: tiny, low-risk, clear root cause; quick RED, patch, targeted test, atomic commit.
- **scoped-fix**: default lane for controlled regressions inside the current feature scope.
- **high-risk-fix**: Dify, plugin, Broker, `nas-agent`, `erp-executor`, containers, release paths, or real runtime behavior. It defaults to investigation until a narrow reason is written.
- **integration-debug**: 3+ live components or repeated multi-hop failures. Add probes and read runtime snapshots first, then downgrade after locating one breakpoint.

Before code changes, `fix_lane`, `q1_causal_chain`, `q2_regression_list`, and `q3_platform_assumptions` must be persisted. Every fix attempt needs a git checkpoint. Stop-loss writes `doom_loop_breaker` and requires the user to choose between returning to `df-plan` or continuing probe-based diagnosis.

### Sub-Agent Dispatch

`df-execute` keeps the main model focused on decisions and orchestration while delegating bounded work:

- search, localization, comparison: `explorer`;
- code implementation: `executor`, falling back to `worker`;
- gate execution and diff review: `verifier`;
- plan gaps: `planner` or return to `df-plan`.

`df-fix` is more conservative. The main agent owns issue judgment, lane triage, `q1/q2/q3`, stop-loss, issue closure, and final status. Sub-agents only handle bounded localization, narrow patches, and verification. Multiple executors must not work concurrently on the core fix for the same user-visible failure.

---

## Skills

| Skill | What it does | What it outputs |
| --- | --- | --- |
| `df-plan` | Start and plan a feature: create the directory, classify risk, read the codebase map, resolve gray areas, write plan and UAT coverage. | `context.md`, `plan.md`, `checklist.yaml`, `validation.md`, `uat.md`, `state.yaml` |
| `df-backlog` | Record later work without interrupting the current feature. | updated `devflow/roadmap.md` |
| `df-codebase-map` | Maintain the layered code map: OVERVIEW plus matching module cards. | `devflow/shared/codebase_map/` |
| `df-constraint-audit` | Read-only audit for drift between gate descriptions, status semantics, contracts, and facts. | constraint findings and source-of-truth recommendations |
| `df-execute` | Execute checklist items after explicit authorization, run targeted tests first, then commit and update evidence. | code changes, commits, `evidence/manifest.json`, `handoff.md` |
| `df-status` | Save a handoff or restore the current feature in a new session. | `handoff.md`, restored context |
| `df-uat` | Guide manual UAT and capture the full feedback round. | `uat.md`, `issues.yaml` |
| `df-fix` | Fix active feature UAT issues through RED, patch, validation, closure, and regression notes. | fix commits, issue closure records, validation evidence |
| `df-regression` | Handle post-acceptance regressions or new UAT issues for archived features. | regression issues, evidence, closure records in the archive feature |
| `df-accept` | Final acceptance and archival, checking checklist, UAT, gates, codebase map, truth docs, and golden sets. | `acceptance.md`, `devflow/archive/` |

---

## Runtime Directory

After `df-plan`, your repository gets:

```text
your-repo/
└── devflow/
    ├── active/
    │   └── 2026-05-01-add-login/     # current feature
    │       ├── context.md             # goal, constraints, success criteria, map_modules_read
    │       ├── plan.md                # implementation plan and boundaries
    │       ├── checklist.yaml         # executable checklist
    │       ├── validation.md          # validation strategy + blast-radius gates
    │       ├── state.yaml             # current state, authorization, checkpoint
    │       ├── handoff.md             # cross-session handoff
    │       ├── uat.md                 # UAT matrix and retest notes
    │       ├── issues.yaml            # active UAT issue view
    │       ├── acceptance.md          # acceptance report
    │       └── evidence/              # machine evidence and history
    │           └── manifest.json
    ├── archive/                       # archived features
    ├── roadmap.md                     # long-goal backlog
    └── shared/
        ├── gate_registry.yaml         # gate registry
        ├── golden_sets/               # golden samples
        └── codebase_map/              # OVERVIEW + modules/*.md
```

These files are the source of truth. The agent reads them to recover context, and a human can review, edit, or take over directly.

---

## License

MIT
