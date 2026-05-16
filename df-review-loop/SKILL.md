---
name: df-review-loop
description: "自动化 Codex code review 循环：用 codex exec review 审查 uncommitted/base/commit diff，落盘 review 证据，按 P0/P1/P2 分流修复、复审、waiver 或止损。用户提到 $df-review-loop、df-review-loop、自动 review、review loop、反复 /review，或 df-execute/df-fix 要做提交前/提交后 AI review 时使用。"
metadata:
  short-description: "自动化 Codex review 循环"
---

# df-review-loop

把人工 `/review -> 修复 -> 再 /review` 变成可落盘、可止损的机器循环。本 skill 只处理 AI code review，不替代 validation、UAT 或 accept audit。

## 环境与边界

- 自动模式要求当前环境可执行 `codex exec review`，并支持 `--uncommitted`、`--base`、`--commit`、`--json`、`-o/--output-last-message`。
- 不调用 TUI slash command `/review`；必须用普通 shell 入口。
- review 输出必须落盘到当前 feature 的 `evidence/reviews/`，finding 正本是 `review-findings.yaml`，不能只留在聊天、终端或 `handoff.md`。
- review finding 不是 UAT issue；只有用户可见失败面才进 `issues.yaml`。旧 `REVIEW-*` 只作为历史压缩对象。
- 命令不可用、空输出、无法解析或超时，写 `review_loop_status: tooling_blocked`，并在 `handoff.md` 写人工 review checklist、阻断原因和后续补跑条件；不得声称 PASS。
- 每轮修复仍必须按调用方 skill 执行 validation、git checkpoint、codebase map 刷新和状态更新。

## 目标与模型

- 提交前审查当前改动：`--uncommitted`。
- 审查单个已提交 commit：`--commit <sha>`。
- 审查分支或多 commit aggregate：`--base <branch-or-sha>`。
- 覆盖漏实现审查：coverage review mode，通常在 aggregate review 或 `$df-execute` 收口前执行；它必须走 prompt-driven review，不能退化成默认 diff review。
- 历史 commit 已有 follow-up fix 后，下一轮复审切到 aggregate 目标，不继续审原始 SHA。

模型/effort 选择：先用 `DEVFLOW_REVIEW_MODEL` / `DEVFLOW_REVIEW_EFFORT`，再用项目 `devflow/shared/review_config.yaml`，否则继承当前 Codex 配置并显式 `model_reasoning_effort="high"`。本机 `codex-auto-review` 只能记录为 local override，不写成跨机器默认。文档或低风险小 diff 可降到 `medium` 并记录原因；指定模型失败时去掉 `-m` 重试一次；`xhigh` 只用于第三轮前的二次裁决、安全/数据损坏/跨模块职责问题。

## 命令形态

每轮生成独立目录：
`<feature>/evidence/reviews/<YYYYMMDD-HHMMSS>-<target>/round-01.md`

每轮先写 `instructions.md`。普通 code review 的 instructions 是人工审查上下文，不一定传给 CLI；coverage review mode 的 instructions 必须作为 prompt/stdin 传入。

普通 code review：
`codex exec review <target flags> <model flags> -c 'model_reasoning_effort="<effort>"' --title "<短上下文>" --json -o <round.md> > <round.jsonl>`

coverage review mode：
`codex exec review <model flags> -c 'model_reasoning_effort="<effort>"' --title "<短上下文>-coverage" --json -o <round.md> - < <instructions.md> > <round.jsonl>`

当前 Codex CLI 的 target review 不能稳定搭配自定义 prompt。普通 review 若误用 prompt/stdin 失败，保留 stderr 为 `tooling-retry.log`，再用无 prompt 的 target 默认形态重跑；coverage review 不能降级，prompt-driven run 失败即 `tooling_blocked`。

instructions 必须写：feature/checklist/issue id、目标类型、允许写入路径、P0/P1/P2 处理规则、scope 判定依据、只报告可证明 bug/数据风险/安全问题/回归风险/缺失测试。

## coverage review mode

coverage review mode 审“计划承诺的用户可见能力是否缺实现”，普通 code review PASS 不能代表 coverage PASS。

- 只审 `plan.md#Capability Coverage Matrix`，并遵守调用方传入的 scope。
- `df-execute` 首次执行和归档前 aggregate review 可全量审；断点续跑只审当前和后续 pending / in_progress 项对应行；`df-fix` 只审当前 issue 的 `coverage_reference` 行。
- instructions 必须要求对照矩阵行、`uat.md`、`checklist.yaml`、当前 diff、`evidence/manifest.json`、`handoff.md` 输出每行的实现、validation、UAT、不替代证据或 waiver。
- coverage P1 包括：矩阵承诺的能力没有 UI/API/工作流/配置/测试/运行态证据；用户动作链、成功判据或失败信号缺实现/validation/UAT 支撑；validation 只覆盖 smoke/build/lint，未覆盖矩阵要求的用户路径、真实浏览器、插件、Dify、ERP 或附件类能力。
- finding 写入 `review-findings.yaml` 并标记 `mode: coverage`。未修或未 waiver 的 P1 阻断 `$df-execute` 宣称 `uat_ready`，也阻断 `$df-accept`。

## 解析与分流

读 `round.md` 后建立 finding 列表，至少记录 `priority`、`file`、`line`、`summary`、`decision`、`round`、`source_path`。指纹使用 `priority + file + line + normalized_summary`，重复指纹只更新轮次。

每条 finding 修复前必须先判定 `scope_decision`：`in_scope` / `out_of_scope_followup` / `independent_followup` / `uncertain_scope`。判定标准是修复是否只改当前 checklist item / issue 的实现文件，且不触碰其他能力行合同、接口、状态归属或模块职责；依据来自调用方的 item、issue、coverage rows、允许路径、q1/q2 回归面和当前 diff。不得仅凭 priority 自动扩大范围。

- P0/P1：仅 `in_scope` 时必须修或写 false positive；当前 scope 内未处理 P0/P1 不得提交或关闭 issue。
- scope 外 P0/P1：写 follow-up 或 independent follow-up，不自动修；不能证明独立或影响当前交付安全时写 `uncertain_scope` 并暂停。
- P2：明确 bug、数据风险或测试缺口且在当前 scope 内才修；风格、偏好、架构扩 scope 或证据不足写 waiver。
- P3 / 无优先级建议默认不阻断，只记录。

## 循环与止损

默认最多 3 轮，绝对硬上限 5 轮。第 5 轮后无论 finding 状态如何必须止损。

循环：运行 review 并落盘；解析并更新 `review-findings.yaml`；修 `scope_decision: in_scope` 的阻断项；跑调用方 validation 和门禁；git checkpoint；选择正确 target 复审；无阻断 finding 时写 `review_loop_status: pass`。

满足任一条件立即停止自动修复，写 `handoff.md#review_loop_breaker`：达到第 5 轮；进入第 4 轮仍有新 P1 或确定 bug P2；同一 finding 两轮修复后仍复现；同一方案造成新 P1/P2 回归；需要第三个 workaround；finding 要求改变模块职责、公共合同、状态归属、数据流方向、共享抽象或部署边界。

止损必须写 `dependency_scope`：

- `feature_blocking`：影响后续 checklist、UAT、公共合同、状态归属、数据流、共享抽象或部署边界；停整个 feature，根因不清回 `integration-debug`，根因清楚但需重设计回 `$df-plan`。
- `item_blocking_only`：仅适用于 `df-execute`；必须证明当前阻断项与后续项没有文件、接口、状态、门禁或 UAT 动作链交叉，并写 `safe_to_continue_items`。
- `independent_followup`：后置跟进或独立增强，不得冒充当前 feature 已闭合。

止损后不得继续补丁式修复；无法证明后续项独立时默认 `feature_blocking`。

## 调用方要求

`df-execute`：executor 返回且 targeted validation 通过后，提交前用 `--uncommitted`；review PASS 或阻断项有 waiver 后才提交 checklist 项；多 commit 交付前可用 `--base <base>` 做 aggregate review。

`df-fix`：目标 issue RED/GREEN 后，关闭 issue 前审本轮修复 diff；当前修复引入的回归必须先修；独立失败面只记录 review finding，不冒充 UAT issue。高风险 issue 的 review PASS 不能替代用户可见 runtime gate。review-loop 止损时当前 UAT issue 仍 open/blocked，不得使用 `item_blocking_only`，也不得继续 UAT 或 `$df-accept`；只有与当前 issue 无关且可后置的 finding 才能写 `independent_followup`。
