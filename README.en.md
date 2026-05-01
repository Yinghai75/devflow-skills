<div align="center">

# DevFlow Skills

![DevFlow Skills](./asset/devflow-skills-cover.png)

**English** · [中文](./README.md)

**A lightweight, recoverable, human-in-the-loop AI coding workflow for personal development tasks**

<p>
  <img src="https://img.shields.io/badge/status-beta-F59E0B?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/skills-7-6366F1?style=flat-square" alt="Skills"/>
  <img src="https://img.shields.io/badge/workflow-DevFlow-10B981?style=flat-square" alt="Workflow"/>
</p>

</div>

---

## Install

```bash
npx skills add https://github.com/Yinghai75/devflow-skills
```

Start from a concrete development goal:

```bash
/df-init
```

Then move through the workflow:

```bash
/df-plan
/df-execute
/df-uat
/df-fix
/df-accept
```

Save or restore context across sessions:

```bash
/df-status
/df-status -r
```

---

## What DevFlow Does

DevFlow is a small set of workflow skills for personal development. It does not aim to be a fully autonomous agent orchestration system. Instead, it turns one development task into a readable, recoverable, and verifiable feature lifecycle.

It helps you:

- Write goals, constraints, plans, validation, and UAT evidence into project files.
- Resume work across sessions without relying on chat history.
- Treat risky changes conservatively with RED evidence, blast-radius checks, and release gates.
- Keep human review points in the loop when goals or acceptance criteria are unclear.

---

## Skills

| Skill | Purpose |
| --- | --- |
| `df-init` | Start a feature, create `devflow/active/<date-slug>/`, and capture goals, constraints, success criteria, and risk lane. |
| `df-plan` | Write `plan.md`, `checklist.yaml`, and `validation.md`; add blast-radius and validation gates for risky work. |
| `df-execute` | Implement the checklist while updating state, evidence, and handoff notes. |
| `df-uat` | Guide manual UAT and record findings in `issues.yaml`. |
| `df-fix` | Investigate, fix, validate, and close UAT issues. |
| `df-accept` | Check completion, UAT issues, validation evidence, and gates before archiving the feature. |
| `df-status` | Save a handoff or restore the current DevFlow context in a new session. |

---

## Workflow

```text
df-init -> df-plan -> df-execute -> df-uat -> df-fix -> df-accept
```

`df-status` works across the whole workflow:

- Run `df-status` before stopping to update `handoff.md`.
- Run `df-status -r` in a new session to restore the current feature, plan, state, and next step.

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

