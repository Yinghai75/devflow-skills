#!/usr/bin/env python3
"""通过 GitHub PR、CI 和可选合并把当前分支交付到 main。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_BASE = "main"
DEFAULT_REMOTE = "origin"


@dataclass(frozen=True)
class CommandResult:
    stdout: str
    stderr: str


def run(
    args: list[str],
    *,
    cwd: Path,
    check: bool = True,
    capture: bool = True,
) -> CommandResult:
    try:
        completed = subprocess.run(
            args,
            cwd=cwd,
            check=False,
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
        )
    except FileNotFoundError:
        raise SystemExit(f"未找到命令：{args[0]}")

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    if check and completed.returncode != 0:
        joined = " ".join(args)
        if stdout.strip():
            print(stdout.strip(), file=sys.stderr)
        if stderr.strip():
            print(stderr.strip(), file=sys.stderr)
        raise SystemExit(f"命令失败：{joined}")
    return CommandResult(stdout=stdout, stderr=stderr)


def resolve_repo(path: str) -> Path:
    repo_arg = Path(path).expanduser().resolve()
    if not repo_arg.exists():
        raise SystemExit(f"repo 不存在：{repo_arg}")
    result = run(["git", "rev-parse", "--show-toplevel"], cwd=repo_arg)
    return Path(result.stdout.strip()).resolve()


def git_text(repo: Path, *args: str) -> str:
    return run(["git", *args], cwd=repo).stdout.strip()


def require_clean_worktree(repo: Path) -> None:
    status = git_text(repo, "status", "--short")
    if status:
        print(status, file=sys.stderr)
        raise SystemExit("工作区不干净。请先提交或清理改动后再运行。")


def require_gh_ready(repo: Path) -> None:
    run(["gh", "--version"], cwd=repo)
    try:
        run(["gh", "auth", "status"], cwd=repo)
    except SystemExit:
        raise SystemExit("gh 未登录。请先运行 gh auth login。")


def current_branch(repo: Path) -> str:
    branch = git_text(repo, "branch", "--show-current")
    if not branch:
        raise SystemExit("当前不在普通分支上，无法创建 PR。")
    return branch


def ensure_feature_branch(branch: str, base: str) -> None:
    if branch == base:
        raise SystemExit(f"当前已经在 {base}，请先切到 feature 分支。")


def active_feature_dirs(repo: Path) -> list[Path]:
    active = repo / "devflow" / "active"
    if not active.is_dir():
        return []
    return sorted(path for path in active.iterdir() if path.is_dir())


def require_devflow_accepted(repo: Path, allow_unaccepted: bool) -> None:
    if allow_unaccepted or not (repo / "devflow").is_dir():
        return

    current = repo / "devflow" / "active" / ".current"
    active_dirs = active_feature_dirs(repo)
    if current.exists() or active_dirs:
        if current.exists():
            pointer = current.read_text(encoding="utf-8").strip()
            print(f"active feature 指针仍存在：{pointer}", file=sys.stderr)
        if active_dirs:
            joined = ", ".join(path.name for path in active_dirs)
            print(f"仍存在 active feature：{joined}", file=sys.stderr)
        raise SystemExit("DevFlow feature 尚未归档。请先运行 $df-accept，或明确使用 --allow-unaccepted。")


def warn_if_no_ci(repo: Path) -> None:
    ci = repo / ".github" / "workflows" / "ci.yml"
    if not ci.exists():
        print("警告：未发现 .github/workflows/ci.yml；PR 可能没有 GitHub CI 门禁。", file=sys.stderr)


def push_branch(repo: Path, remote: str, branch: str) -> None:
    print(f"推送分支：{remote}/{branch}")
    run(["git", "push", "-u", remote, branch], cwd=repo, capture=False)


def find_pr_for_branch(repo: Path, branch: str) -> dict[str, object] | None:
    result = run(
        [
            "gh",
            "pr",
            "list",
            "--head",
            branch,
            "--state",
            "open",
            "--json",
            "number,url,title,headRefName,baseRefName,isDraft",
        ],
        cwd=repo,
    )
    prs = json.loads(result.stdout or "[]")
    if not prs:
        return None
    return prs[0]


def create_or_reuse_pr(repo: Path, branch: str, base: str, draft: bool) -> dict[str, object]:
    existing = find_pr_for_branch(repo, branch)
    if existing:
        number = int(existing["number"])
        existing_base = str(existing.get("baseRefName", ""))
        if existing_base != base:
            raise SystemExit(f"已有 PR #{number} 指向 {existing_base}，不是目标 base {base}。")
        print(f"复用已有 PR：#{number} {existing.get('url', '')}")
        return existing

    command = ["gh", "pr", "create", "--fill", "--base", base, "--head", branch]
    if draft:
        command.append("--draft")
    print("创建 PR")
    run(command, cwd=repo, capture=False)

    created = find_pr_for_branch(repo, branch)
    if not created:
        raise SystemExit("PR 已创建但无法反查 PR 编号。")
    print(f"PR：#{created['number']} {created.get('url', '')}")
    return created


def wait_for_ci(repo: Path, pr_number: int) -> None:
    print(f"等待 GitHub CI：PR #{pr_number}")
    run(["gh", "pr", "checks", str(pr_number), "--watch", "--fail-fast"], cwd=repo, capture=False)


def ensure_mergeable_pr(pr: dict[str, object]) -> None:
    if bool(pr.get("isDraft")):
        raise SystemExit("PR 仍是 draft。请先手动 gh pr ready 后再合并。")


def merge_pr(repo: Path, pr_number: int, method: str, delete_branch: bool) -> None:
    command = ["gh", "pr", "merge", str(pr_number), f"--{method}"]
    if delete_branch:
        command.append("--delete-branch")
    print(f"合并 PR #{pr_number}，方式：{method}")
    run(command, cwd=repo, capture=False)


def pull_back_main(repo: Path, remote: str, base: str) -> None:
    print(f"切回 {base} 并拉取 {remote}/{base}")
    run(["git", "checkout", base], cwd=repo, capture=False)
    run(["git", "pull", "--ff-only", remote, base], cwd=repo, capture=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="push 当前 feature branch，创建/复用 PR，等待 GitHub CI，并可选 squash merge 回 main 后拉回本仓。"
    )
    parser.add_argument("--repo", default=".", help="目标 git 仓库路径，默认当前目录。")
    parser.add_argument("--base", default=DEFAULT_BASE, help="PR base 分支，默认 main。")
    parser.add_argument("--remote", default=DEFAULT_REMOTE, help="git remote，默认 origin。")
    parser.add_argument("--draft", action="store_true", help="新建 PR 时创建 draft PR。")
    parser.add_argument("--merge", action="store_true", help="CI 通过后合并 PR。未传时只停在 CI 通过。")
    parser.add_argument(
        "--merge-method",
        choices=["merge", "squash", "rebase"],
        default="squash",
        help="PR 合并方式，默认 squash。",
    )
    parser.add_argument("--delete-branch", action="store_true", help="合并后删除远端 feature 分支。")
    parser.add_argument(
        "--skip-ci-wait",
        action="store_true",
        help="不等待 GitHub CI。仅用于已确认 CI 状态的情况。",
    )
    parser.add_argument(
        "--allow-unaccepted",
        action="store_true",
        help="允许存在 active DevFlow feature 时继续。仅用于非 DevFlow 小改或人工确认绕过。",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.draft and args.merge:
        raise SystemExit("--draft 与 --merge 不能同时使用：draft PR 需要先人工 ready。")

    repo = resolve_repo(args.repo)
    require_clean_worktree(repo)
    require_devflow_accepted(repo, args.allow_unaccepted)
    require_gh_ready(repo)
    warn_if_no_ci(repo)

    branch = current_branch(repo)
    ensure_feature_branch(branch, args.base)

    push_branch(repo, args.remote, branch)
    pr = create_or_reuse_pr(repo, branch, args.base, args.draft)
    pr_number = int(pr["number"])

    if not args.skip_ci_wait:
        wait_for_ci(repo, pr_number)

    if args.merge:
        latest_pr = find_pr_for_branch(repo, branch) or pr
        ensure_mergeable_pr(latest_pr)
        merge_pr(repo, pr_number, args.merge_method, args.delete_branch)
        pull_back_main(repo, args.remote, args.base)
        print("完成：PR 已合并，本地 main 已拉回。")
        return

    print("完成：PR 已创建/复用，CI 已通过。未传 --merge，因此未合并 main。")


if __name__ == "__main__":
    main()
