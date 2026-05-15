---
name: df-review-loop
description: "自动化 Codex code review 循环：用 codex exec review 审查 uncommitted/base/commit diff，落盘 review 证据，按 P0/P1/P2 分流修复、复审、waiver 或止损。用户提到 $df-review-loop、df-review-loop、自动 review、review loop、反复 /review，或 df-execute/df-fix 要做提交前/提交后 AI review 时使用。"
metadata:
  short-description: "自动化 Codex review 循环"
---

# df-review-loop

把人工 `/review -> 修复 -> 再 /review` 变成可落盘、可止损的机器循环。本 skill 只处理 AI code review，不替代 validation、UAT 或 accept audit。

## 环境要求

- 自动模式要求当前环境可执行 `codex exec review`，并支持 `--uncommitted`、`--base`、`--commit`、`--json` 和 `-o/--output-last-message`。
- 这是 Codex CLI 集成，不是跨 agent 通用审查协议。非 Codex 环境或命令不可用时，不能声称 review PASS；必须在 `review-findings.yaml` 写 `review_loop_status: tooling_blocked`，并在 `handoff.md` 写清人工 review checklist、阻断原因和后续补跑条件。
- 若只能做人工审查，人工结论必须写入 `review-findings.yaml` 的 waiver 或 manual_review 段，供 `$df-accept` 复核。

## 边界

- 不调用 TUI slash command `/review`；必须使用普通 shell 入口 `codex exec review`。
- review 输出必须落盘到当前 feature 的 `evidence/reviews/`，不能只留在聊天或终端输出。
- review finding 不是 UAT issue；只有用户可见失败面才进 `issues.yaml`。review finding 写入 `review-findings.yaml`；旧 feature 缺少该文件时先创建，不把 `handoff.md` 当主要 finding 表。
- 不能无限追 P2。P0/P1 必修；P2 只修确定 bug、局部且在当前 scope 内的问题，其余写 waiver。
- 每轮修复仍必须按调用方 skill 执行 validation、git checkpoint、codebase map 刷新和状态更新。

## 目标选择

- 提交前审查当前改动：使用 `--uncommitted`。
- 审查单个已提交 commit：使用 `--commit <sha>`。
- 审查一个分支或多 commit aggregate：使用 `--base <branch-or-sha>`。
- 覆盖漏实现审查：使用 `coverage review mode`，通常在 aggregate review 或 `$df-execute` 收口前执行；该模式必须走带完整 instructions 的 prompt-driven review，不能退化成默认 target diff review。
- 若已对某个历史 commit 做了 follow-up fix，下一轮复审必须切到 aggregate 目标（通常 `--base <base>` 或 `--uncommitted`），不要继续审原始 SHA，否则会重复报已由后续 commit 修掉的问题。

## 模型设置

发布默认不硬编码本机模型别名。模型和 effort 选择顺序：

1. 若环境变量 `DEVFLOW_REVIEW_MODEL`、`DEVFLOW_REVIEW_EFFORT` 存在，作为全局默认优先使用，并在 `review-findings.yaml` 记录来源。
2. 若项目在 `devflow/shared/review_config.yaml` 声明 review 配置，作为项目默认使用，并在 `review-findings.yaml` 记录来源。
3. 若没有上述配置，默认继承当前 Codex 配置，只显式设置 `model_reasoning_effort="high"`。
4. 本机存在 `codex-auto-review` 这类专用模型别名时可以使用，但必须记录为 local override；不得把该别名写成跨机器默认。

降级与升级：

- 仅文档、文案或很小的低风险 diff：可用 `medium` effort，并记录降级原因。
- 指定模型失败：去掉 `-m` 继承当前 Codex 配置重试一次，并在 `review-findings.yaml` 记录 fallback。
- `xhigh` 只用于第三轮前的二次裁决、安全/数据损坏/跨模块职责问题，不能作为默认循环强度。

## 命令形态

每轮都生成独立目录，例如：

`<feature>/evidence/reviews/<YYYYMMDD-HHMMSS>-<target>/round-01.md`

每轮都必须先把本轮审查意图写入同目录的 `instructions.md`。该文件是审查证据和人工上下文，不等于一定会作为 CLI prompt 传入。

当前 Codex CLI 0.130.0 的 `codex exec review` 在 help 中显示可用 `[PROMPT]` / `-` 从 stdin 读取，但实测 target review（`--uncommitted`、`--base`、`--commit`）不能稳定搭配自定义 prompt 或 stdin。因此 DevFlow 分两种命令形态：

- 普通 code review：按 target 默认 review 形态执行，不给额外 PROMPT，不用 `- < instructions.md`。
- coverage review mode：必须把完整 `instructions.md` 通过 PROMPT/stdin 传入，且不得同时传 `--uncommitted` / `--base` / `--commit`。目标范围、base/commit/uncommitted、允许检查的矩阵行、UAT/checklist/evidence 路径和输出格式都写进 `instructions.md`，由模型按 instructions 读取文件和 diff。若该形态失败，写 `review_loop_status: tooling_blocked`，不得 fallback 到默认 target diff review 冒充 coverage PASS。

普通 code review 执行形态：

`codex exec review <target flags> <model flags> -c 'model_reasoning_effort="<effort>"' --title "<短上下文>" --json -o <round.md> > <round.jsonl>`

coverage review mode 执行形态：

`codex exec review <model flags> -c 'model_reasoning_effort="<effort>"' --title "<短上下文>-coverage" --json -o <round.md> - < <instructions.md> > <round.jsonl>`

`--title` 只放短上下文，例如 feature id、checklist item 或 UAT issue id；普通 code review 的完整 P0/P1/P2 分流、scope、允许写入路径和 q1/q2 回归面仍写入 `instructions.md`，并在解析 findings 时作为人工判定依据。coverage review mode 的矩阵行、scope、UAT/checklist/evidence 路径和 per-row 输出要求必须写入 prompt；没有成功传入 prompt 的 coverage run 一律无效。

普通 code review 若误用了 PROMPT/stdin 导致 CLI 报错，必须保留失败命令的 stderr 为 `tooling-retry.log`，随后用无 PROMPT/stdin 的 target 默认形态重跑。只有重跑产出有效 `round.md` 时，本轮才能继续解析；否则写 `review_loop_status: tooling_blocked`。coverage review mode 不能使用这条重跑降级路径；prompt-driven coverage run 失败时直接按 `tooling_blocked` 处理。

若当前 shell/终端不适合保存 JSONL，至少必须保留 `-o <round.md>`；不能让 review 只输出到聊天上下文。

review instructions 必须包含：

- 当前 feature、checklist item 或 UAT issue id。
- 本轮目标是提交前、单 commit 还是 aggregate。
- P0/P1/P2 的处理规则：P0/P1 阻断；P2 仅确定 bug 阻断；风格或计划外扩 scope 写 waiver。
- 只报告可证明的 bug、数据风险、安全问题、回归风险或缺失测试；不要把超出当前计划的重构建议当阻断。

## coverage review mode

coverage review mode 用来审“计划承诺的用户可见能力是否缺实现”，不等同于普通 diff code review。普通 code review PASS 不能代表 coverage PASS。

该模式只审 `plan.md` 的 `Capability Coverage Matrix`，但默认遵守调用方传入的 scope。`df-execute` 首次执行和归档前 aggregate review 可全量审；断点续跑只审当前和后续 `pending` / `in_progress` checklist 项对应的矩阵行；`df-fix` 只审当前 issue 的 `coverage_reference` 行。instructions 必须要求模型对照作用域内矩阵行、`uat.md`、`checklist.yaml`、当前 diff、`evidence/manifest.json` 和 `handoff.md` 查缺失能力，输出每个矩阵行的实现、validation、UAT 支撑、不可替代证据或 waiver。

coverage review 的 P1 包括：

- `Capability Coverage Matrix` 承诺的用户可见能力没有对应 UI、API、工作流、配置、测试或运行态证据。
- 矩阵中的用户动作链、下游成功判据或失败信号没有实现/validation/UAT 支撑。
- validation 只覆盖 smoke / build / lint，未覆盖矩阵要求的用户路径、真实浏览器路径、插件交互、Dify 发布生效、ERP 写入或附件类能力。

coverage finding 写入 `review-findings.yaml`，并标记 `mode: coverage`；未修复或未 waiver 的 P1 会阻断 `$df-execute` 宣称 `uat_ready`，也阻断 `$df-accept` 归档。

## 解析与分流

读 `round.md` 后建立本轮 finding 列表，至少记录 priority、file、line、summary、decision、round、source_path。

- 每条 finding 在修复前必须先判定 `scope_decision`：`in_scope` / `out_of_scope_followup` / `independent_followup` / `uncertain_scope`。判定依据是调用方传入的 checklist item、UAT issue、coverage rows、允许写入路径、q1/q2 回归面和当前 diff；不得仅凭 priority 自动扩大修复范围。
- `P0` / `P1`：仅当 `scope_decision: in_scope` 时必须修复或写明为何是 false positive；不能带着当前 scope 内未处理 P0/P1 提交或关闭 issue。
- scope 外 P0/P1 不得在本轮自动修复：能证明独立时写 `out_of_scope_followup` / `independent_followup`，并记录非阻断理由、后续归属和与当前交付无交叉的证据；不能证明独立或影响当前交付安全时写 `uncertain_scope` 并暂停询问用户或回调用方止损。
- `P2`：若是明确 bug、数据风险、测试缺口且在当前 scope 内，修；若是风格、偏好、架构扩 scope 或证据不足，写 waiver。
- `P3` / 无优先级建议：默认不阻断，只记录。
- 无法解析、超时、空输出或只有 JSONL 没有最终消息：判为 `tooling_blocked`，不能当 PASS。

finding 指纹使用 `priority + file + line + normalized_summary`。同一指纹重复出现时更新 round 记录，不新建兄弟 finding。

## 循环

默认最多 3 轮。

1. 运行 review 并落盘。
2. 解析 findings，更新 `review-findings.yaml`。
3. 对 `scope_decision: in_scope` 的阻断项执行修复：`df-execute` 场景回 executor；`df-fix` 场景回当前 issue 的修复流程。scope 外或不确定 finding 只记录 follow-up、waiver 或暂停，不得进入自动修复。
4. 跑调用方要求的 targeted validation 和门禁。
5. 做 git checkpoint；提交信息可包含 `review` 或调用方 issue/checklist id。
6. 重新选择正确 target 并复审。
7. 无阻断 finding 时写 `review_loop_status: pass`。

## 止损

满足任一条件立即停止自动修复，写入 `handoff.md` 的 `review_loop_breaker`：

- 进入第 4 轮仍有新的 P1 或确定 bug P2。
- 同一 finding 两轮修复后仍复现。
- 同一方案造成新的 P1/P2 回归。
- 需要第三个 workaround。
- review finding 要求改变模块职责、公共合同、状态归属、数据流方向、共享抽象或部署边界。

review loop 内每轮修复都算作调用方（`df-execute` 或 `df-fix`）的一次修复尝试，计入调用方止损计数器；不能把 review 内部修复轮次当作独立空间绕过 `doom_loop_breaker`。

止损时必须同时写 `dependency_scope`：

- `feature_blocking`：影响后续 checklist、UAT、公共合同、状态归属、数据流、共享抽象或部署边界；立即停整个 feature，根因不清回 `integration-debug`，根因清楚但需要重设计回 `$df-plan`。
- `item_blocking_only`：仅适用于 `df-execute`；只阻断当前 checklist 项；必须证明当前阻断项与后续项没有文件、接口、状态、门禁或 UAT 动作链交叉，并在 `handoff.md` 写 `safe_to_continue_items`，其余已证明无依赖的项可继续。
- `independent_followup`：属于后置跟进或独立增强；写入后续计划，不得冒充当前 feature 已闭合。

止损后不得继续补丁式修复。若无法证明后续项独立，默认按 `feature_blocking` 处理。

## 调用方要求

`df-execute` 调用时：

- executor 返回且 targeted validation 通过后，提交前用 `--uncommitted` 跑本 skill。
- review PASS 或阻断项都有明确 waiver 后才允许提交该 checklist 项。
- 多 commit 交付前可再用 `--base <base>` 做 aggregate review。

`df-fix` 调用时：

- 触发 issue 的同一路径 RED/GREEN 验证后，关闭 issue 前必须对本轮修复 diff 跑本 skill。
- review finding 若暴露当前修复引入的回归，必须先修；若是独立失败面，只记录为 review finding，不冒充 UAT issue。
- 高风险 issue 的 review PASS 不能替代用户可见 runtime gate。
- review-loop 止损时，当前 UAT issue 仍视为未关闭；不得使用 `item_blocking_only`，也不得继续 UAT 或 `$df-accept`。若阻断项属于当前 issue 或其回归面，写 `feature_blocking` 并遵守 `df-fix` 硬锁；只有与当前 issue 无关且可后置的 finding 才能写 `independent_followup`。
