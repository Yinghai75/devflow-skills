---
name: df-uat
description: "引导当前 DevFlow feature 的人工 UAT，并把验收中发现的问题记录为 issues.yaml 条目；用于 UAT 验收与问题闭环。用户提到 $df-uat、df-uat、人工验收、记录验收问题时使用。"
metadata:
  short-description: "记录 DevFlow UAT issue"
---

# df-uat

引导当前 feature 的人工 UAT，并把验收过程中发现的问题记录为 feature-local issue。普通 UAT issue 不放进 `devflow/issues/`，除非明确转为跨 feature 或后置问题。

`df-uat` 不只是事后登记问题；它也是人工验收会话入口。应基于当前 feature 的 `uat.md`、`acceptance.md`、`validation.md` 和 `handoff.md`，带用户逐项完成真实环境验收。只有用户反馈出现异常、不符合预期或证据缺失无法关闭时，才生成 issue。

## 流程

1. 读取 active feature。
2. 读取 `uat.md`、`acceptance.md`、`validation.md`、`handoff.md`，提取待人工验收项、已完成证据、waiver 和当前阻塞项。
3. 按顺序引导用户执行 UAT。每次只给 1-3 个明确操作步骤，并说明期望看到的结果。
4. 根据用户反馈判断：
   - 通过：记录该项已通过；若还有未完成 UAT 项，直接提示下一项的 1-3 个操作步骤和期望结果。
   - 不通过：提取 issue 标题、现象、严重度；严重度只能是 `low`、`medium`、`high`、`critical`。
   - 信息不足：要求用户补充最小必要证据，例如截图、页面文字、控制台错误、请求响应或具体复现步骤。
   - 越界试测：按“非当前 UAT 项反馈”处理。
5. 需要记录 issue 时运行：
   `uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> uat "<标题>" "<现象>" --severity <low|medium|high|critical>`
6. 回复生成的 issue id，并按“Issue 后续判定”明确是自动进入 `$df-fix <issue-id>`，还是继续下一项 UAT。没有 issue id 时禁止转修。

脚本会拒绝非法严重度，不要用 `urgent`、`blocker` 等临时值绕过枚举。

不要把 UAT issue 单独升级为 debug 阶段；只有根因不清时才进入调查模式。

## 非当前 UAT 项反馈

用户可能在当前 UAT 中顺手测试到后续 UAT 项。处理顺序：

1. 先判定归属：当前 UAT 项、后续 UAT 项提前覆盖、后续 UAT 项 issue、信息不足。
2. 如果是后续 UAT 项提前覆盖，只在 `uat.md` 记录动作与证据；只有用户明确反馈该项通过，才关闭该项。
3. 如果是后续 UAT 项 issue，登记 issue，标题写清所属 UAT 项；不算当前 UAT 项失败。
4. 登记后提醒用户先收口当前 UAT；不要跟随用户切到后续阶段，也不要自动 `$df-fix`，除非该 issue 阻断当前 UAT 或用户明确要求暂停当前 UAT 去修。

## Issue 后续判定

- `critical/high`、前置能力失败、会污染后续证据：立即自动进入 `$df-fix <issue-id>` 修复；不得在 `$df-uat` 流程内直接改实现文件。
- `low/medium`、独立且不影响后续证据：可以继续下一条 UAT，并说明为什么不阻断。
- 信息不足：先补最小证据，不继续也不修。

## 自动转修边界

- UAT 中允许修阻塞项，但必须先生成 UAT issue，再显式切到 `$df-fix <issue-id>` 流程；禁止先修后补 issue。
- 即使根因明显，也禁止“顺手修”：不得跳过 `$df-fix` 的读取、修复、门禁、记录闭环。
- `$df-uat` 本身只允许读取证据、引导复测、登记 issue、更新 UAT 记录；实现代码、工作流、服务配置改动必须发生在 `$df-fix`。

## 引导原则

- 不要把 `uat.md` 中的待验证项直接全部登记为 issue；它们只是 UAT checklist。
- 只有用户执行后反馈异常，或明确无法获得必要证据，才记录 issue。
- 引导用户操作真实环境时，必须区分“期望结果”和“如果不符合请反馈什么”。
- 当前 UAT 项通过或关闭相关 issue 后，不要停在“已完成”；应自动读取 `uat.md` 找到下一项未完成 UAT，并给出下一步操作。
- 若下一项依赖当前项刚产出的会话、页面或证据，说明可以复用什么；若不能复用，明确要求从新的 UAT 步骤开始。
- 已有机器证据不要求用户重复验证，除非 `uat.md` 明确要求真实环境人工验收。
- 如果用户反馈“通过/正常/符合预期”，不要生成 issue；继续下一项。
- 如果用户反馈“不知道怎么验”，先给更具体的操作步骤，而不是记录 issue。

## 下一步

- UAT 全部通过且无 open issue 时，提示进入 `$df-accept`。
- 有 open issue 时，按严重度进入 `$df-fix <issue-id>` 或继续下一项 UAT；修复后回到 `$df-uat` 复测。
