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
3. 先做 UAT 覆盖审计，再按顺序引导用户执行 UAT。每次只给 1-3 个明确操作步骤，并说明期望看到的结果。
4. 若验收项涉及真实浏览器、真实客户端、本机插件、外部站点、登录态、设备态、账号态或本地缓存/会话，先从已有文档和证据提取“验证画像”：
   - 入口路径：用户如何进入该能力，是手动打开、系统跳转、脚本拉起还是页面内继续操作。
   - 客户端画像：浏览器/客户端品牌、channel、是否真实用户窗口。
   - 会话画像：是否复用用户既有 profile、既有登录态、既有 cookie/storage、既有插件状态。
   - 环境画像：目标环境、网络位置、样本类型、是否真实账号/真实站点。
   - 只有画像缺失时，才补问用户或在 `uat.md`/证据中显式记缺口。
5. 根据用户反馈判断：
   - 通过：记录该项已通过；若还有未完成 UAT 项，直接提示下一项的 1-3 个操作步骤和期望结果。
   - 不通过：提取 issue 标题、现象、严重度；严重度只能是 `low`、`medium`、`high`、`critical`。
   - 信息不足：要求用户补充最小必要证据，例如截图、页面文字、控制台错误、请求响应或具体复现步骤。
   - 越界试测：按“非当前 UAT 项反馈”处理。
6. 需要记录 issue 前，必须先执行“Issue 去重与重开规则”；只有确认不是既有 issue 的同一用户可见问题，才运行：
   `uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo <repo> uat "<标题>" "<现象>" --severity <low|medium|high|critical>`
7. 回复生成的 issue id，并按“Issue 后续判定”明确是自动进入 `$df-fix <issue-id>`，还是继续下一项 UAT。没有 issue id 时禁止转修。
8. 若判定需要进入 `$df-fix <issue-id>`，必须立即读取 `df-fix` skill 并按其流程继续；禁止在 `$df-uat` 语境下直接修改实现文件。

脚本会拒绝非法严重度，不要用 `urgent`、`blocker` 等临时值绕过枚举。

不要把 UAT issue 单独升级为 debug 阶段；只有根因不清时才进入调查模式。

## Issue 去重与重开规则

- UAT issue 按用户可见失败面划分，不按技术根因、补丁方案、代码位置或 harness 划分。
- 新建 issue 前必须查 `issues.yaml` 最近和相关 issue。
- 同一失败面已有 open issue：禁止新建，续写原 issue。
- 同一失败面已有 closed issue 且复测失败：重开或追加 `regression`，禁止新建。
- 只有用户可见失败面独立时才允许新建。
- 拆分混合 issue 时必须写明 `split_from` / `related_issue`。
- 若 `issues.yaml` 是活跃上下文视图，必须同时查它声明的 `history_ref`、`evidence/*history*.yaml` 和 `evidence/*full*.yaml`，避免历史已关闭问题被重复新建。
- 用户说“通过/正常”时，先确认对应 issue id；未确认时不得擅自关闭新 issue。
- 标题写用户现象；技术细节写 `investigation`。

## Issue 分层与归档

`issues.yaml` 应保持为当前 UAT 的活跃工作集，而不是完整修复流水账。目标是让 agent 每次进入 UAT 时能快速看清“现在还卡什么”，同时不丢失历史证据。

- 活跃文件只保留 open issue、刚关闭但仍需复测的 issue、当前断点、最新证据和 `history_ref`。
- 长修复历史、旧 investigation、过期尝试、完整 timeline 和大量证据清单应归档到 `evidence/` 下的历史文件，例如 `evidence/uat-xxx-full-history.yaml`。
- 归档前必须确认历史文件可追溯原始 issue id、状态、关键证据和迁移时间；归档后在活跃 issue 写 `history_ref`。
- 不得为了压缩而删除正式记录；只能迁移到 feature-local `evidence/` 或等价正式证据目录。
- 新增或重开 issue 时，只在活跃 `issues.yaml` 写当前失败面和最新证据；旧轮次细节继续追加到历史文件或专门 evidence 文件。
- 如果活跃 `issues.yaml` 超过约 150 行，或单个 issue 的历史超过约 80 行，先做分层压缩再继续登记新 issue。
- 分层后必须校验 YAML 可解析，并确认下一个 UAT id 不会与活跃或历史 id 冲突。

## 非当前 UAT 项反馈

用户可能在当前 UAT 中顺手测试到后续 UAT 项。处理顺序：

1. 先判定归属：当前 UAT 项、后续 UAT 项提前覆盖、后续 UAT 项 issue、信息不足。
2. 如果是后续 UAT 项提前覆盖，只在 `uat.md` 记录动作与证据；只有用户明确反馈该项通过，才关闭该项。
3. 如果是后续 UAT 项 issue，登记 issue，标题写清所属 UAT 项；不算当前 UAT 项失败。
4. 登记后提醒用户先收口当前 UAT；不要跟随用户切到后续阶段，也不要自动 `$df-fix`，除非该 issue 阻断当前 UAT 或用户明确要求暂停当前 UAT 去修。

## Issue 后续判定

- `critical/high`、前置能力失败、会污染后续证据：立即自动进入 `$df-fix <issue-id>` 修复；不得在 `$df-uat` 流程内直接改实现文件，不得把“先修再补记录”当作合格闭环。
- `low/medium`、独立且不影响后续证据：可以继续下一条 UAT，并说明为什么不阻断。
- 信息不足：先补最小证据，不继续也不修。

## 自动转修边界

- UAT 中允许修阻塞项，但必须先生成 UAT issue，再显式切到 `$df-fix <issue-id>` 流程；禁止先修后补 issue。
- 即使根因明显，也禁止“顺手修”：不得跳过 `$df-fix` 的读取、修复、门禁、记录闭环。
- `$df-uat` 本身只允许读取证据、引导复测、登记 issue、更新 UAT 记录；实现代码、工作流、服务配置改动必须发生在 `$df-fix`。
- 进入 `$df-fix` 前必须给用户一句状态切换说明，例如“已登记 UAT-xxx，按 df-fix 修复闭环处理”；随后按 `df-fix` 的强制接管规则执行。

## 引导原则

- 不要把 `uat.md` 中的待验证项直接全部登记为 issue；它们只是 UAT checklist。
- 只有用户执行后反馈异常，或明确无法获得必要证据，才记录 issue。
- 涉及真实运行路径的 UAT，默认先复用既有通过证据中的同一验证画像；不得无说明地切换到新的 profile、新的脚本入口、新的账号态或新的自动化方式。
- 若为了调查必须改变验证画像，必须先明确这是“探索性验证”而不是“等价复测”；探索性结果不能直接覆盖原 UAT 口径。
- 引导用户操作真实环境时，必须区分“期望结果”和“如果不符合请反馈什么”。
- 当前 UAT 项通过或关闭相关 issue 后，不要停在“已完成”；应自动读取 `uat.md` 找到下一项未完成 UAT，并给出下一步操作。
- 若下一项依赖当前项刚产出的会话、页面或证据，说明可以复用什么；若不能复用，明确要求从新的 UAT 步骤开始。
- 已有机器证据不要求用户重复验证，除非 `uat.md` 明确要求真实环境人工验收。
- 如果用户反馈“通过/正常/符合预期”，不要生成 issue；继续下一项。
- 如果用户反馈“不知道怎么验”，先给更具体的操作步骤，而不是记录 issue。

## UAT 覆盖审计

开始引导前必须检查 `uat.md` 是否覆盖了当前 feature 的用户可见能力和真实运行路径。只读取现有文档，不自行扩大需求范围。

审计输入：

- `checklist.yaml` 中所有会产生用户可见行为、外部站点交互、插件交互、Dify 运行态变化、ERP 写入或发布生效的任务。
- `validation.md` 的 Impact Map、Protected Surfaces、Golden Set Delta。
- `handoff.md` 中已实现但尚未人工复测的路径。
- `issues.yaml` 中曾经失败后又关闭的用户可见失败面。

若发现以下任一情况，必须先补 `uat.md`，再继续引导：

- `uat.md` 仍是初始模板或只有“暂无”。
- 某个用户可见新能力只有自动测试、fixture、curl 或门禁证据，没有人工 UAT 项。
- 涉及真实浏览器、官网采集、插件回流、Dify 发布生效、ERP 写入审计的路径没有真实环境 UAT 项。
- 已关闭 issue 的失败面没有对应复测记录。
- 高风险真实环境能力的 `uat.md` 没写清验证画像，导致后续复测无法判断是否仍在同一路径上。

补项规则：

- 给缺口生成“待人工 UAT”项，写清操作步骤、期望结果和证据口径。
- 对高风险真实环境项，同时写清最小验证画像：入口、客户端/浏览器、profile/登录态来源、目标环境、样本类型。
- 不得因为已有机器证据就自动标记通过。
- 若用户明确不做该项真实 UAT，记录 waiver、残余风险和后续归属；高风险或核心能力 waiver 后不得建议 `$df-accept`，除非用户明确接受该残余风险。
- 如果补出的 UAT 项是当前能力的前置核心路径，优先引导该项，而不是继续后续体验项。

## 下一步

- UAT 全部通过且无 open issue 时，提示进入 `$df-accept`。
- 有 open issue 时，按严重度进入 `$df-fix <issue-id>` 或继续下一项 UAT；修复后回到 `$df-uat` 复测。
