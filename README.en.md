<div align="center">

# DevFlow Skills

![DevFlow Skills](./asset/devflow-skills-cover-clean.png)

**English** · [中文](./README.md)

**A lightweight, recoverable, human-in-the-loop AI coding workflow for personal development tasks**

<p>
  <img src="https://img.shields.io/badge/status-beta-F59E0B?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/skills-7-6366F1?style=flat-square" alt="Skills"/>
  <img src="https://img.shields.io/badge/workflow-DevFlow-10B981?style=flat-square" alt="Workflow"/>
</p>

</div>

---

## Why DevFlow

There are already many AI coding workflows and specification frameworks. DevFlow targets a narrower problem: **how one developer and one coding agent can move a development task to acceptance, keep it recoverable, and archive it cleanly**.

It does not try to orchestrate a team of agents, and it does not turn every task into a heavy specification project. DevFlow stores state in your repository and uses a small set of fixed stages:

```text
goal capture -> plan review -> implementation and validation -> UAT loop -> final archive
```

The tradeoffs are deliberate:

- **Less implicit context**: task state lives in the `devflow/` file tree, not only in chat history.
- **Less workflow weight**: 7 skills organized around a feature lifecycle.
- **Stronger recovery**: `df-status -r` restores the current feature, plan, and next step.
- **Conservative risk control**: high-risk work requires RED evidence, blast-radius gates, and release checks.

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

Start from a concrete development goal:

```bash
/df-init
```

---

## Quick Start

- **New requirement**: run `/df-init` to create a feature directory and classify the risk lane.
- **Plan the work**: run `/df-plan` to write the plan, checklist, and validation strategy, then stop for review.
- **Implement**: run `/df-execute` to work through the checklist while updating state and evidence.
- **Resume later**: run `/df-status -r` in a new session to restore the last handoff.
- **Accept and archive**: run `/df-uat`, `/df-fix`, and `/df-accept` to close the UAT loop and archive the feature.

---

## Core Design

| Dimension | Heavy specification/orchestration frameworks | DevFlow |
| --- | --- | --- |
| Core object | specs, agents, phases, or role collaboration | one deliverable feature |
| State location | spec directories, chat history, or agent state | repository-local `devflow/` file tree |
| Recovery | context continuation or rereading multiple docs | `df-status -r` restores the current handoff |
| Risk handling | usually a fixed process | automatic `fast`, `standard`, and `high-risk` lanes |
| Validation | can drift into document-only claims | checklist, validation, evidence, and UAT issue loop |
| Human role | often optimized toward automation | plan review and acceptance stay human-in-the-loop by default |

---

## Workflow

```text
┌─────────┐    ┌─────────┐    ┌────────────┐    ┌────────┐    ┌───────────┐
│ df-init │───▶│ df-plan │───▶│ df-execute │───▶│ df-uat │───▶│ df-accept │
└─────────┘    └─────────┘    └────────────┘    └────────┘    └───────────┘
                                      ▲              │
                                      │              ▼
                                  ┌────────┐    write issues.yaml
                                  │ df-fix │◀────────┘
                                  └────────┘

df-status: save a handoff at any stage, or restore it in a new session with df-status -r
```

- `fast` is for low-risk docs and small local fixes.
- `standard` is for normal multi-file development with plan, execution, UAT, fix, and acceptance.
- `high-risk` is for state machines, production release, data writes, cross-module orchestration, and similar work; it requires RED evidence, blast-radius gates, and release checks.

---

## Skills

| Skill | Purpose | Main outputs |
| --- | --- | --- |
| `df-init` | Start a feature and capture goals, constraints, success criteria, and risk lane. | `context.md`, `state.yaml` |
| `df-plan` | Write a human-readable plan, checklist, and validation strategy. | `plan.md`, `checklist.yaml`, `validation.md` |
| `df-execute` | Implement the checklist while updating state and evidence. | code changes, `evidence/manifest.json`, `handoff.md` |
| `df-uat` | Guide manual UAT and record findings. | `uat.md`, `issues.yaml` |
| `df-fix` | Fix UAT issues and run regression validation. | fix commits, updated evidence |
| `df-accept` | Check completion, UAT issues, evidence, and risk gates before archiving. | `acceptance.md`, `devflow/archive/<date-slug>/` |
| `df-status` | Save or restore a cross-session handoff. | `handoff.md` |

---

## Runtime File Tree

After `df-init`, the target repository gets a DevFlow workspace:

```text
your-repo/
└── devflow/
    ├── active/
    │   └── 2026-05-01-add-login/
    │       ├── context.md
    │       ├── plan.md
    │       ├── checklist.yaml
    │       ├── validation.md
    │       ├── state.yaml
    │       ├── handoff.md
    │       ├── uat.md
    │       ├── issues.yaml
    │       ├── acceptance.md
    │       └── evidence/
    │           └── manifest.json
    ├── archive/
    ├── roadmap.md
    └── shared/
        ├── gate_registry.yaml
        └── golden_sets/
```

These files are DevFlow's source of truth: the agent can read them, and you can review, edit, or take over at any time.

---

## Repository Layout

```text
.
├── df-init/
├── df-plan/
├── df-execute/
├── df-uat/
├── df-fix/
├── df-accept/
├── df-status/
└── asset/
```

Each `df-*` directory is an independent skill with `SKILL.md` as its entry point.

---

## License

MIT
