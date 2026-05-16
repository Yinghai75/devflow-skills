---
name: df-pr-merge
description: "DevFlow PR 交付：在 df-accept 后推送 feature 分支，创建或复用 GitHub PR，等待 CI，通过后默认 squash merge 到 main 并拉回本地。用户提到 $df-pr-merge、df-pr-merge、PR CI merge、合并 main、推送 feature branch 后走 PR/CI 时使用。"
metadata:
  short-description: "PR/CI/squash merge 交付"
---

# df-pr-merge

把已经收口的 feature 分支通过 GitHub PR、CI 和 squash merge 合入 `main`。本 skill 只处理 GitHub 交付动作，不替代 `$df-accept`、机器验证、人工 UAT 或 review-loop。

## 边界

- `df-accept` 管 DevFlow feature 是否完成、能否归档。
- `df-pr-merge` 管已收口分支如何进入 `main`。
- `.github/workflows/ci.yml` 是 GitHub CI 的事实源；本 skill 只等待和执行 PR 检查，不在 skill 里重写 CI 内容。
- 默认合并方式是 `squash`。只有用户明确要求时才改为 `merge` 或 `rebase`。
- 默认要求仓库没有 active DevFlow feature。若存在 `devflow/active/.current` 或 active feature 目录，先回 `$df-accept`；非 DevFlow 小改必须由用户明确允许 `--allow-unaccepted`。

## 前置检查

1. 检查当前仓库和分支：
   - `git status --short --branch`
   - 当前分支不得是 `main`。
   - 工作区必须干净。
2. 若仓库有 `devflow/`，检查：
   - 不得存在未归档 active feature，除非用户明确允许非 DevFlow 小改绕过。
   - 不把 `df-accept` 未通过的 feature 直接推 PR 合并。
3. 检查 GitHub CLI：
   - `gh --version`
   - `gh auth status`
4. 确认 `.github/workflows/ci.yml` 是否存在。不存在时可以继续开 PR，但必须提醒用户本仓没有 GitHub CI 门禁。

## 标准执行

完整 PR/CI/squash merge 流程使用：

`uv run python /Users/yinghai/.codex/local/devflow/pr_ci_merge.py --repo <repo> --merge`

脚本会执行：

1. 检查工作区干净、当前不在 `main`、`gh` 可用。
2. 检查 DevFlow active feature 已收口。
3. `git push -u origin <current-branch>`。
4. 创建或复用指向 `main` 的 PR。
5. 等待 GitHub checks 出现在 PR 上；若 PR 为 `DIRTY`，明确提示先解决冲突，因为 GitHub 不会运行 `pull_request` CI。
6. 等待 `gh pr checks --watch --fail-fast`。
7. CI 通过后用 `squash` 合并 PR。
8. 拉回本地 `main`：若当前 worktree 可 checkout `main`，直接切回并 `git pull --ff-only origin main`；若 `main` 已被其他 worktree checkout，则在那个 worktree 执行 `git pull --ff-only origin main`。

## 常用参数

- `--merge`：CI 通过后合并 PR。`df-pr-merge` 默认应使用该参数。
- `--merge-method squash|merge|rebase`：合并方式，默认 `squash`。
- `--title "<标题>" --body-file <path>`：新建 PR 时手动指定标题和正文；不传时默认使用 `gh pr create --fill`。
- `--delete-branch`：合并后删除远端 feature 分支。
- `--draft`：新建 draft PR；不能和 `--merge` 同用。
- `--skip-ci-wait`：跳过等待 CI。只有用户明确说明 CI 已确认通过时才使用。
- `--checks-discovery-timeout <秒>`：等待 GitHub checks 出现在 PR 上的时间，默认 60 秒。
- `--allow-unaccepted`：允许存在 active DevFlow feature 时继续。只用于非 DevFlow 小改或用户明确绕过。
- 不传 `--merge`：只 push、建/复用 PR、等 CI，通过后停住，不合并。

## 失败处理

- CI 失败：不合并；用 `gh pr checks <pr>`、Actions 日志或项目测试定位，不要绕过。
- PR 有冲突：`mergeStateStatus=DIRTY` 时不等待 CI，不合并；先把 `main` 合入当前分支或 rebase，解决冲突后重新 push。
- 没有 checks：`mergeStateStatus=CLEAN` 但超时仍无 checks 时，不合并；只有用户明确确认无 CI/已人工验证时才使用 `--skip-ci-wait`。
- `gh` 未登录：提示用户运行 `gh auth login`。
- branch protection 阻断：报告 GitHub 返回的具体阻断项，不用 admin bypass。
- 工作区不干净：先提交或清理；不要把 PR 交付和未分组业务改动混在一起。
- active feature 未归档：回 `$df-accept`；不要用 PR 合并代替归档审计。

## 回复口径

最终回复先说：

- PR 是否已创建/复用。
- CI 是否通过。
- 是否已 squash merge。
- 本地 `main` 是否已拉回。

再列 PR URL、合并方式、当前分支和失败阻断项。对于本 skill，不需要报告业务本地发布、远端发布或 UAT readiness，除非本次 PR 交付本身包含发布动作。
