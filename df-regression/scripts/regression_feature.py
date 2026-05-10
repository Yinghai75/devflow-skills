#!/usr/bin/env python3
"""DevFlow archive feature regression helper."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from typing import Iterable


VALID_SEVERITIES = {"low", "medium", "high", "critical"}
DEVFLOW_CLI = Path("/Users/yinghai/.codex/local/devflow/devflow_cli.py")


def load_devflow_cli():
    spec = importlib.util.spec_from_file_location("devflow_cli", DEVFLOW_CLI)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 DevFlow CLI：{DEVFLOW_CLI}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def now_text() -> str:
    return load_devflow_cli().now_text()


def archive_root(repo: Path) -> Path:
    return repo / "devflow" / "archive"


def issue_pattern(issue_id: str) -> re.Pattern[str]:
    return re.compile(rf"^\s*- id:\s*{re.escape(issue_id)}\s*$", re.M)


def find_archive_features(repo: Path, source_issue: str) -> list[Path]:
    root = archive_root(repo)
    if not root.exists():
        return []
    matches: list[Path] = []
    for feature in sorted(path for path in root.iterdir() if path.is_dir()):
        issues = feature / "issues.yaml"
        if issues.exists() and issue_pattern(source_issue).search(read_text(issues)):
            matches.append(feature)
    return matches


def resolve_feature(repo: Path, feature: str | None, source_issue: str | None) -> Path:
    if feature:
        path = Path(feature)
        if not path.is_absolute():
            path = repo / feature
        path = path.resolve()
        if not path.is_dir():
            raise FileNotFoundError(f"feature 不存在：{path}")
        if archive_root(repo).resolve() not in path.parents:
            raise ValueError(f"feature 不在 devflow/archive 下：{path}")
        return path
    if not source_issue:
        raise ValueError("必须提供 --feature 或 --source-issue")
    matches = find_archive_features(repo, source_issue)
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(f"未在 devflow/archive 中找到源 issue：{source_issue}")
    formatted = "\n".join(str(path) for path in matches)
    raise RuntimeError(f"源 issue 匹配多个 archive feature，请显式传 --feature：\n{formatted}")


def next_regression_id(feature: Path, source_issue: str) -> str:
    issues = read_text(feature / "issues.yaml")
    prefix = f"{source_issue}-R"
    numbers = [
        int(match.group(1))
        for match in re.finditer(rf"^\s*- id:\s*{re.escape(prefix)}(\d+)\s*$", issues, flags=re.M)
    ]
    return f"{prefix}{max(numbers, default=0) + 1}"


def next_post_acceptance_id(feature: Path) -> str:
    issues_path = feature / "issues.yaml"
    if not issues_path.exists():
        raise FileNotFoundError(f"{feature} 中不存在 issues.yaml")
    issues = read_text(issues_path)
    numbers = [
        int(match.group(1))
        for match in re.finditer(r"^\s*- id:\s*UAT-(\d+)(?:-R\d+)?\s*$", issues, flags=re.M)
    ]
    return f"UAT-{max(numbers, default=0) + 1:03d}"


def ensure_source_issue(feature: Path, source_issue: str) -> None:
    issues = feature / "issues.yaml"
    if not issues.exists() or not issue_pattern(source_issue).search(read_text(issues)):
        raise FileNotFoundError(f"{feature} 中不存在源 issue：{source_issue}")


def quote_yaml(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def register_issue(repo: Path, args: argparse.Namespace) -> None:
    if args.severity not in VALID_SEVERITIES:
        raise ValueError(f"无效严重度：{args.severity}")
    feature = resolve_feature(repo, args.feature, args.source_issue)
    ensure_source_issue(feature, args.source_issue)
    issue_id = next_regression_id(feature, args.source_issue)
    created = now_text()
    append_text(
        feature / "issues.yaml",
        f"""  - id: {issue_id}
    title: {quote_yaml(args.title)}
    severity: {args.severity}
    status: open
    regression_of: {args.source_issue}
    created_at: {quote_yaml(created)}
    description: {quote_yaml(args.description)}
""",
    )
    append_text(
        feature / "uat.md",
        f"""
## {issue_id} {args.title}

- 严重度：{args.severity}
- 状态：open
- 回归来源：{args.source_issue}
- 现象：{args.description}
""",
    )
    load_devflow_cli().update_state(feature, current_step=f"记录回归 issue {issue_id}，来源 {args.source_issue}")
    print(f"feature: {feature}")
    print(f"issue: {issue_id}")


def register_new_issue(repo: Path, args: argparse.Namespace) -> None:
    if args.severity not in VALID_SEVERITIES:
        raise ValueError(f"无效严重度：{args.severity}")
    feature = resolve_feature(repo, args.feature, None)
    issue_id = next_post_acceptance_id(feature)
    created = now_text()
    append_text(
        feature / "issues.yaml",
        f"""  - id: {issue_id}
    title: {quote_yaml(args.title)}
    severity: {args.severity}
    status: open
    post_acceptance: true
    created_at: {quote_yaml(created)}
    description: {quote_yaml(args.description)}
""",
    )
    append_text(
        feature / "uat.md",
        f"""
## {issue_id} {args.title}

- 类型：验收后新增 issue
- 严重度：{args.severity}
- 状态：open
- 现象：{args.description}
""",
    )
    load_devflow_cli().update_state(feature, current_step=f"记录验收后新增 UAT issue {issue_id}")
    print(f"feature: {feature}")
    print(f"issue: {issue_id}")


def run_gate(repo: Path, args: argparse.Namespace) -> None:
    feature = resolve_feature(repo, args.feature, args.source_issue)
    evidence = load_devflow_cli().run_gate(feature, args.gate_id)
    print(evidence.log_path)
    if evidence.status != "passed":
        raise SystemExit(2)


def split_issue_blocks(text: str) -> list[list[str]]:
    lines = text.splitlines()
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if re.match(r"^\s*- id:\s+", line) and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks


def issue_block_id(block: list[str]) -> str | None:
    for line in block:
        match = re.match(r"^\s*- id:\s*(\S+)\s*$", line)
        if match:
            return match.group(1)
    return None


def issue_block_has_field(block: list[str], key: str) -> bool:
    prefix = f"    {key}:"
    return any(line.startswith(prefix) for line in block)


def replace_or_append_field(block: list[str], key: str, value: str) -> list[str]:
    prefix = f"    {key}:"
    output: list[str] = []
    replaced = False
    skip_list = False
    for line in block:
        if skip_list and line.startswith("      - "):
            continue
        skip_list = False
        if line.startswith(prefix):
            output.append(f"    {key}: {value}")
            replaced = True
            if key == "evidence":
                skip_list = True
        else:
            output.append(line)
    if not replaced:
        output.append(f"    {key}: {value}")
    return output


def evidence_yaml(paths: Iterable[str]) -> str:
    items = [path for path in paths if path]
    if not items:
        return "[]"
    return "\n" + "\n".join(f"      - {quote_yaml(path)}" for path in items)


def close_issue(repo: Path, args: argparse.Namespace) -> None:
    feature = resolve_feature(repo, args.feature, args.source_issue)
    issues_path = feature / "issues.yaml"
    text = read_text(issues_path)
    blocks = split_issue_blocks(text)
    found = False
    issue_kind = "回归 issue"
    new_blocks: list[list[str]] = []
    for block in blocks:
        if issue_block_id(block) == args.issue_id:
            found = True
            if issue_block_has_field(block, "post_acceptance"):
                issue_kind = "验收后新增 UAT issue"
            block = replace_or_append_field(block, "status", "closed")
            block = replace_or_append_field(block, "resolved_at", quote_yaml(now_text()))
            block = replace_or_append_field(block, "resolution", quote_yaml(args.resolution))
            block = replace_or_append_field(block, "evidence", evidence_yaml(args.evidence))
        new_blocks.append(block)
    if not found:
        raise FileNotFoundError(f"未找到 issue：{args.issue_id}")
    write_text(issues_path, "\n".join("\n".join(block) for block in new_blocks) + "\n")

    append_text(
        feature / "uat.md",
        f"""
### {args.issue_id} {issue_kind}关闭

- 状态：closed
- 修复：{args.resolution}
- 证据：{', '.join(args.evidence) if args.evidence else '未记录'}
""",
    )
    summary = f"已关闭{issue_kind} {args.issue_id}，等待用户复测或回到 df-accept/后续流程"
    load_devflow_cli().update_state(feature, current_step=summary)
    append_text(
        feature / "handoff.md",
        f"""
- {summary}
  - 修复：{args.resolution}
  - 证据：{', '.join(args.evidence) if args.evidence else '未记录'}
""",
    )
    print(f"feature: {feature}")
    print(f"closed: {args.issue_id}")


def print_resolved_feature(repo: Path, args: argparse.Namespace) -> None:
    print(resolve_feature(repo, args.feature, args.source_issue))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DevFlow 已归档 feature 回归 issue 工具")
    parser.add_argument("--repo", default=".", help="项目根目录")
    sub = parser.add_subparsers(dest="command", required=True)

    resolve = sub.add_parser("resolve-feature")
    resolve.add_argument("--feature")
    resolve.add_argument("--source-issue")

    register = sub.add_parser("register")
    register.add_argument("--feature")
    register.add_argument("--source-issue", required=True)
    register.add_argument("--title", required=True)
    register.add_argument("--description", required=True)
    register.add_argument("--severity", default="medium", choices=sorted(VALID_SEVERITIES))

    register_new = sub.add_parser("register-new")
    register_new.add_argument("--feature", required=True)
    register_new.add_argument("--title", required=True)
    register_new.add_argument("--description", required=True)
    register_new.add_argument("--severity", default="medium", choices=sorted(VALID_SEVERITIES))

    run = sub.add_parser("run-gate")
    run.add_argument("gate_id")
    run.add_argument("--feature")
    run.add_argument("--source-issue")

    close = sub.add_parser("close")
    close.add_argument("--feature")
    close.add_argument("--source-issue")
    close.add_argument("--issue-id", required=True)
    close.add_argument("--resolution", required=True)
    close.add_argument("--evidence", action="append", default=[])

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    try:
        if args.command == "resolve-feature":
            print_resolved_feature(repo, args)
        elif args.command == "register":
            register_issue(repo, args)
        elif args.command == "register-new":
            register_new_issue(repo, args)
        elif args.command == "run-gate":
            run_gate(repo, args)
        elif args.command == "close":
            close_issue(repo, args)
        else:
            parser.error("未知命令")
    except Exception as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
