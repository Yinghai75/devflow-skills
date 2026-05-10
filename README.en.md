<div align="center">

# DevFlow Skills

![DevFlow Skills](./asset/devflow-skills-cover-clean.png)

**English** · [中文](./README.md)

**A lightweight AI coding workflow for individual developers: 10 skills, about 880 instruction lines, one complete feature lifecycle**

<p>
  <img src="https://img.shields.io/badge/status-beta-F59E0B?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/skills-10-6366F1?style=flat-square" alt="Skills"/>
  <img src="https://img.shields.io/badge/instructions-~880-10B981?style=flat-square" alt="Instructions"/>
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"/>
</p>

</div>

---

## Why DevFlow

Many AI coding workflows solve bigger problems: specification management, team collaboration, multi-agent orchestration, and complex project governance. DevFlow aims at a narrower problem:

**One developer + one coding agent, moving one development task to acceptance while keeping it recoverable and archivable.**

Using a rough count from the current public repositories, the instruction footprint is very different:

| Framework | Main units | Agent config | Rough instruction footprint |
| --- | --- | --- | --- |
| [Superpowers](https://github.com/obra/superpowers) | 14 skills | 1 agent file | about 3,200 lines |
| [GSD](https://github.com/gsd-build/get-shit-done) | 99 workflows | 33 agent files | about 47,600 lines |
| **DevFlow** | **10 skills** | **5 lightweight sub-agent roles** | **about 880 lines** |

The heavier the instruction stack, the more tokens each session burns and the easier it is for an agent to lose the thread inside long prompts. DevFlow narrows the scope: it does not try to cover every project-governance scenario; it focuses on making one feature lifecycle solid for an individual developer.

It does not try to take over the whole project, and it does not turn every small request into a heavy specification process. DevFlow splits a feature into a few fixed stages:

```text
goal capture -> plan review -> implementation and validation -> UAT loop -> final archive
```

The tradeoffs are deliberate:

- **State lives in the repo**: goals, plans, checklists, validation evidence, and handoffs are written into the `devflow/` file tree.
- **The workflow stays light**: 10 skills, about 880 `SKILL.md` instruction lines, organized around a feature lifecycle.
- **Recovery is cheap**: run `df-status -r` in a new session to restore the current feature, plan, and next step.
- **Risk control is conservative**: high-risk work requires RED evidence, blast-radius gates, and release checks. The agent cannot self-certify by writing "passed".

---

## When It Helps

- **AI fixes one issue and causes three regressions?** Blast-radius gates force old behavior to be protected before changing new behavior.
- **A new session forgets where the task stopped?** `handoff.md` plus `df-status -r` restores the checkpoint.
- **The agent says "tests passed" but did not run them?** `run-gate` produces machine evidence; text claims do not count.
- **You want AI help but not full autopilot?** Plan review and manual UAT keep human control at key points.
- **Heavy workflows burn too much context?** About 880 skill instruction lines keep the workflow compact.

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
/df-init        # New requirement: create a feature directory and classify the risk lane
/df-backlog     # Later item: record a new idea in roadmap/backlog without interrupting current work
/df-plan        # Decide how to build it: plan, checklist, validation, then stop for review
/df-codebase-map # Code map: generate or refresh implementation-level navigation
/df-execute     # Build: work through the checklist and update state and evidence
/df-status -r   # New session: restore the last handoff
/df-uat         # User acceptance: record UAT results and issues
/df-fix         # Fix: close UAT issues and run regression gates
/df-regression  # Post-acceptance regression: handle follow-up UAT issues for archived features
/df-accept      # Archive: check evidence and gates, then move the feature to archive/
```

---

## Workflow

```text
┌─────────┐    ┌─────────┐    ┌────────────┐    ┌────────┐    ┌───────────┐
│ df-init │───▶│ df-plan │───▶│ df-execute │───▶│ df-uat │───▶│ df-accept │
└─────────┘    └─────────┘    └────────────┘    └────────┘    └───────────┘
     │              │               ▲                │              │
     ▼              ▼               │                ▼              ▼
┌────────────┐ ┌────────────────┐ ┌────────┐   write issues.yaml ┌───────────────┐
│ df-backlog │ │ df-codebase-map │ │ df-fix │◀──────────────────│ df-regression │
└────────────┘ └────────────────┘ └────────┘                   └───────────────┘

              df-status: save a handoff at any stage / restore with df-status -r
```

Three lanes:

- **fast**: low-risk docs and small fixes. The path can be shorter.
- **standard**: normal multi-file development. Plan, execute, UAT, fix, accept.
- **high-risk**: state machines, production release, data writes, cross-module orchestration. Requires RED evidence, blast-radius gates, and release checks.

`df-init` classifies the risk lane conservatively. Work touching online objects is automatically upgraded to `high-risk`.

---

## Design Principles

- **State in the repo, not in chat history**: goals, plans, checklists, validation evidence, and handoffs all live under `devflow/`. A human can read, edit, or take over directly.
- **Machine evidence, not document-only claims**: key gates run through `run-gate`, and results are written to `evidence/manifest.json`. Agent-written "passed" text is not evidence.
- **Planning and execution are separate**: `df-plan` stops at a review point by default. You confirm before `df-execute` continues.
- **Changing one thing must not break three**: high-risk work starts with failing tests or reproduction evidence, then uses blast-radius gates to protect existing behavior.

---

## Skills

| Skill | What it does | What it outputs |
| --- | --- | --- |
| `df-init` | Capture goals, constraints, success criteria, and risk lane. | `context.md`, `state.yaml` |
| `df-backlog` | Record later work without interrupting the current feature. | updated `roadmap.md` |
| `df-plan` | Write the plan, checklist, validation strategy, and blast-radius gates. | `plan.md`, `checklist.yaml`, `validation.md` |
| `df-codebase-map` | Generate, refresh, and consume implementation-level code maps. | `devflow/shared/codebase_map/` |
| `df-execute` | Implement checklist items while updating state and evidence. | code changes, `evidence/manifest.json`, `handoff.md` |
| `df-uat` | Guide manual UAT and record acceptance issues. | `uat.md`, `issues.yaml` |
| `df-fix` | Fix UAT issues and run regression gates. | fix commits, updated evidence |
| `df-regression` | Handle post-acceptance UAT regressions for archived features. | regression issue, fix feature, validation evidence |
| `df-accept` | Check completion, evidence, gates, and archive the feature. | `acceptance.md`, `devflow/archive/` |
| `df-status` | Save a handoff or restore context in a new session. | `handoff.md` |

---

## Runtime Directory

After `df-init`, your repository gets:

```text
your-repo/
└── devflow/
    ├── active/
    │   └── 2026-05-01-add-login/     # current feature
    │       ├── context.md             # goals, constraints, success criteria
    │       ├── plan.md                # implementation plan
    │       ├── checklist.yaml         # executable task checklist
    │       ├── validation.md          # validation strategy + blast-radius gates
    │       ├── state.yaml             # current state and checkpoint
    │       ├── handoff.md             # cross-session handoff
    │       ├── uat.md                 # UAT notes
    │       ├── issues.yaml            # issues found during UAT
    │       ├── acceptance.md          # acceptance report
    │       └── evidence/              # machine evidence
    │           └── manifest.json
    ├── archive/                       # archived features
    ├── roadmap.md                     # long-goal backlog
    └── shared/
        ├── gate_registry.yaml         # gate registry
        ├── golden_sets/               # golden samples
        └── codebase_map/              # implementation-level code map
```

These files are the source of truth. The agent reads them to recover context, and you can open, review, or edit them directly.

---

## License

MIT
