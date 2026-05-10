---
name: df-regression
description: "处理已 df-accept / 已归档 DevFlow feature 的 UAT 追加回归问题；用于 $df-regression、验收后追加 issue、已 accept 的 UAT 回归修复。"
metadata:
  short-description: "修复已归档 UAT 回归"
---

# df-regression

处理已经 `$df-accept` 并归档后的 UAT 追加问题。它覆盖两类场景：

- 原 UAT 已通过/已 accept，但用户后来复测发现同一验收项仍有问题。
- feature 已归档后，用户发现一个此前没有登记过的新 UAT 问题。

本 skill 不替代 `$df-fix`：

- `$df-fix`：当前 active feature 的 open UAT issue。
- `$df-regression`：已归档 feature 的 UAT 回归追加 issue，或验收后新增 UAT issue。

## 强制边界

- 不得使用 `devflow_cli.py uat` 登记 issue；该命令只写当前 active feature。
- 不得使用 `devflow_cli.py run-gate` 跑门禁；该命令只读取当前 active feature。
- 必须用本 skill 的 helper 指定 archive feature 写入 issue、门禁证据和 manifest。
- 当前 active feature 只允许读取，不得把 regression 的证据、handoff 或 state 写入当前 active。
- 必须先登记 issue，拿到 `UAT-xxx-Rn` 或 `UAT-xxx` 后再改实现文件。

## Helper

脚本路径：

`/Users/yinghai/.codex/skills/df-regression/scripts/regression_feature.py`

常用命令：

```bash
uv run python /Users/yinghai/.codex/skills/df-regression/scripts/regression_feature.py --repo <repo> resolve-feature --source-issue UAT-009
uv run python /Users/yinghai/.codex/skills/df-regression/scripts/regression_feature.py --repo <repo> register --source-issue UAT-009 --title "<标题>" --description "<现象>" --severity medium
uv run python /Users/yinghai/.codex/skills/df-regression/scripts/regression_feature.py --repo <repo> register-new --feature <archive-feature> --title "<标题>" --description "<现象>" --severity medium
uv run python /Users/yinghai/.codex/skills/df-regression/scripts/regression_feature.py --repo <repo> run-gate --feature <archive-feature> unit-tests
uv run python /Users/yinghai/.codex/skills/df-regression/scripts/regression_feature.py --repo <repo> close --feature <archive-feature> --issue-id UAT-009-R1 --resolution "<修复说明>" --evidence "<证据路径>"
```

## Issue 编号

- 同一已关闭 UAT 没修干净：从源 UAT 派生 `UAT-009-R1`、`UAT-009-R2`，`issues.yaml` 必须写入 `regression_of: UAT-009`。
- 已归档 feature 的全新 UAT 问题：开下一个普通编号，例如 `UAT-010`，`issues.yaml` 必须写入 `post_acceptance: true`，不得写 `regression_of`。
- 如果不能唯一定位源 UAT 所属 archive feature，先向用户确认目标 feature；不得猜。
- 没有源 UAT 的新增问题必须显式提供 `--feature <archive-feature>`。

## 场景判断

- 用户反馈“之前那个 UAT 仍然没好”“同一个点还挡住/还失败”：使用 `register --source-issue <id>`。
- 用户反馈“已 accept 的 feature 又发现一个新 UAT issue”“不属于现有 UAT，要开新序号”：使用 `register-new --feature <archive-feature>`。
- 如果实际是新需求、范围扩展或体验增强，不登记到已归档 feature；改用 `$df-backlog` 或新 feature。

## 流程

1. 读取用户反馈，判断是既有 UAT 回归还是验收后新增问题。
2. 既有 UAT 回归：用 helper `resolve-feature --source-issue <id>` 定位 archive feature。
3. 既有 UAT 回归：用 helper `register` 创建 `UAT-xxx-Rn`：
   - `title` 写清回归问题；
   - `description` 写用户反馈和最小复现现象；
   - `severity` 只能是 `low`、`medium`、`high`、`critical`。
4. 验收后新增问题：确认目标 archive feature 后，用 helper `register-new` 创建下一个 `UAT-xxx`。
5. 读取 archive feature 的 `plan.md`、`validation.md`、`issues.yaml`、`uat.md`、`handoff.md` 和相关代码。
6. 若问题来自真实浏览器、真实客户端、本机插件、外部站点、登录态、设备态、本地缓存或发布后路径，先从 archive feature 的历史 GREEN 证据中提取“验证画像”：
   - 入口路径
   - 客户端/浏览器/设备类型
   - profile、登录态、cookie/storage、插件状态是否复用
   - 样本类型、目标环境、账号态
   - 只有确认与历史 GREEN 同画像时，才可把两次结果直接比较
7. 按 `$df-fix` 的 RED → 修复 → 验证闭环执行：
   - UAT/runtime/跨模块问题必须先用真实复现、页面操作、HTTP 探测、容器检查或契约 gate 击中失败面；
   - mock 单测只能补防回归，不能单独作为真实 RED；
   - 根因不清时先调查，不用“会通过的测试”代替调查。
8. 回归验证默认先复用历史 GREEN 的同一验证画像；除非当前假设就是“画像维度引入回归”，否则不得先切到新的临时 profile、新入口或新的自动化方式。
9. 若为了定位问题需要改变验证画像，必须把该轮结果标注为“探索性对比验证”，说明变化维度与目的；探索性结果不能直接覆盖 archive feature 的原 UAT 口径。
10. 修复后先复跑触发该 issue 的同一真实步骤，再跑最小自动测试和对应门禁。
11. 注册门禁必须用 helper `run-gate --feature <archive-feature> <gate-id>`。
12. 用 helper `close` 关闭 `UAT-xxx-Rn` 或 `UAT-xxx`，同步 `issues.yaml`、`uat.md`、`state.yaml`、`handoff.md` 和 `evidence/manifest.json`。

## 记录要求

- `issues.yaml` 中保留源 issue 的 closed 状态，不要把原 UAT 改回 open。
- regression issue 或验收后新增 issue 单独关闭，并记录 `resolved_at`、`resolution`、`evidence`。
- `uat.md` 必须区分：
  - 原 UAT 现象；
  - 验收后追加回归现象；
  - 验收后新增问题现象；
  - RED；
  - 修复；
  - 验证。
- 涉及真实环境路径的 regression，记录中必须写清历史 GREEN 验证画像、本轮验证画像，以及两者是否一致。
- `state.yaml` 的 `current_step` 写成“已关闭 <issue-id>，等待用户复测或回到 df-accept/后续流程”。

## 完成口径

修复完成后说明：

- 这是已验收项的回归追加修复，还是验收后新增 UAT issue 修复；
- 已关闭的原 UAT 不改写为 open；
- 新增的 `UAT-xxx-Rn` 或 `UAT-xxx` 已关闭；
- 用户复测前需要执行的生效步骤，例如重新加载插件、刷新页面、重启服务等。
