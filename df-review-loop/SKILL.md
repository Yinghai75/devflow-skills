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

普通 code review 默认不落 `instructions.md`；coverage review mode 必须先写 `instructions.md` 并作为 prompt/stdin 传入。

普通 code review：
`codex exec review <target flags> <model flags> -c 'model_reasoning_effort="<effort>"' --title "<短上下文>" --json -o <round.md> > <tmp-jsonl>`

coverage review mode：
`codex exec review <model flags> -c 'model_reasoning_effort="<effort>"' --title "<短上下文>-coverage" --json -o <round.md> - < <instructions.md> > <tmp-jsonl>`

当前 Codex CLI 的 target review 不能稳定搭配自定义 prompt。普通 review 若误用 prompt/stdin 失败，保留 stderr 为 `tooling-retry.log`，再用无 prompt 的 target 默认形态重跑；coverage review 不能降级，prompt-driven run 失败即 `tooling_blocked`。

review 指令内容必须覆盖：feature/checklist/issue id、目标类型、允许写入路径、P0/P1/P2 处理规则、scope 判定依据、只报告可证明 bug/数据风险/安全问题/回归风险/缺失测试。

## coverage review mode

coverage review mode 审“计划承诺的用户可见能力是否缺实现”，普通 code review PASS 不能代表 coverage PASS。

- 只审 `plan.md#Capability Coverage Matrix`，并遵守调用方传入的 scope。
- `df-execute` 首次执行和归档前 aggregate review 可全量审；断点续跑只审当前和后续 pending / in_progress 项对应行；`df-fix` 只审当前 issue 的 `coverage_reference` 行。
- instructions 必须要求对照矩阵行、`uat.md`、`checklist.yaml`、当前 diff、`evidence/manifest.json`、`handoff.md` 输出每行的实现、validation、UAT、不替代证据或 waiver。
- coverage P1 包括：矩阵承诺的能力没有 UI/API/工作流/配置/测试/运行态证据；用户动作链、成功判据或失败信号缺实现/validation/UAT 支撑；validation 只覆盖 smoke/build/lint，未覆盖矩阵要求的用户路径、真实浏览器、插件、Dify、ERP 或附件类能力。
- finding 写入 `review-findings.yaml` 并标记 `mode: coverage`。未修或未 waiver 的 P1 阻断 `$df-execute` 宣称 `uat_ready`，也阻断 `$df-accept`。

## 运行模式

review-loop 有三种运行模式，由调用方指定：

### discover-only（实现期默认）

按 P0/P1/P2 动态分级。整体硬上限 **3 轮**（含首轮），不区分由哪个 priority 触发。

- **P0 in-scope**：修 → 复审 → 新 P0 继续修 → 循环至无 P0 或达到 3 轮。**P0 scope 外**：写 `uncertain_scope` 暂停。
- **P1 in-scope**：修 1 次 → 复审 1 轮但**只看新 P0**；发现新 P0 则进入 P0 循环，否则忽略继续。复审计入全局轮数。**P1 scope 外**：写 `out_of_scope_followup`。
- **P2/P3**：标记 `deferred_to_post_uat`，不修不循环。
- 达到 3 轮仍有未处理 P0：写 `review_loop_breaker` + `dependency_scope: feature_blocking`，**止损等用户决定**（不得继续实现或提示进入 UAT）。

### regression-check-only（UAT 修复期）

`uat_status: RED` 时自动触发。跑 1 轮，只拦截新 P0/P1 回归（新 P0/P1 in-scope 立即修，不复审），P2/P3 和 scope 外 waiver。结果：`regression_check_done`。

### post-uat（UAT 全绿后，由 df-accept 触发）

逐 commit review（`--commit <sha>`）。处理所有 `deferred_to_post_uat` findings：scope 判定 → P0/P1 必须修 → P2 限投 1 轮。默认 2 轮 / 硬上限 3 轮，达到上限**停下等用户决定**。可批量修后跑 1 次 aggregate 复审。

## 分流、止损与证据

读 `round.md` 后建立 finding 列表（`priority`/`file`/`line`/`summary`/`decision`/`round`/`source_path`）。每条 finding 先判定 `scope_decision`（`in_scope`/`out_of_scope_followup`/`independent_followup`/`uncertain_scope`），不得仅凭 priority 扩大范围；P0 也必须先写 `scope_decision`。

触发硬上限或以下任一条件立即止损并写 `handoff.md#review_loop_breaker`：同一 finding 两轮仍复现；同一方案造成新 P0/P1 回归；需要第三个 workaround；finding 要求改变模块职责/公共合同/状态归属/数据流/部署边界。止损写 `dependency_scope`（`feature_blocking` / `item_blocking_only` / `independent_followup`），无法证明后续项独立时默认 `feature_blocking`。

证据瘦身：JSONL 只作临时解析输入，不作为正式证据保留；`instructions.md` 只在 coverage review mode 落盘；`review-findings.yaml` 已关闭 finding 只保留 `id`/`status`/`round`；`handoff.md` 只保留最新 + 上一个断点。

## 调用方要求

`df-execute`（实现期）：每个 checklist 项完成 targeted validation 后，用 `discover-only` 模式跑 `--uncommitted`，按该模式内部规则处理（P0 循环复审 / P1 修后只查新 P0 / P2 defer）。存在未修/未 waiver P0 时不得写 `uat_ready`。

`df-fix`（UAT 修复期）：目标 issue RED/GREEN 后，用 `regression-check-only` 模式跑 `--uncommitted`（自动传入 `uat_status: RED`）。只拦截新 P0/P1 回归；其余不阻断 issue 关闭。高风险 issue 的 review PASS 不能替代用户可见 runtime gate。

`df-accept`（UAT 全绿后）：归档前若 `review-findings.yaml` 存在 `deferred_to_post_uat`，用 `post-uat` 模式逐 commit review 并批量修 deferred findings。
