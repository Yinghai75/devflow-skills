#!/usr/bin/env python3
"""DevFlow UAT issue 活跃视图压缩工具。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


BEIJING = ZoneInfo("Asia/Shanghai")
ISSUE_ID_RE = re.compile(r"^  - id:\s*(UAT-\d{3,}(?:-R\d+)?)\s*$")
STATUS_RE = re.compile(r"^    status:\s*\"?([^\"\n]+)\"?\s*$")
HISTORY_REF_RE = re.compile(r"^    history_ref:\s*(.+?)\s*$")
KEEP_SCALAR_KEYS = {
    "id",
    "title",
    "severity",
    "status",
    "created_at",
    "description",
    "regression_of",
    "post_acceptance",
    "duplicate_of",
    "related_issue",
    "split_from",
}


@dataclass(frozen=True)
class CompactIssuesResult:
    active_path: Path
    history_path: Path | None
    compacted_count: int


def compact_issues(feature: Path | str, max_issue_lines: int = 50) -> CompactIssuesResult:
    feature = Path(feature)
    issues_path = feature / "issues.yaml"
    content = issues_path.read_text(encoding="utf-8")
    blocks = _issue_blocks(content)
    if not blocks:
        return CompactIssuesResult(active_path=issues_path, history_path=None, compacted_count=0)

    compacted: list[str] = []
    output = ["issues:"]
    history_ref = ""
    for block in blocks:
        if _is_compacted_stub(block):
            output.append(block.rstrip())
            continue
        status = _issue_status(block)
        should_compact = status in {"closed", "deferred"} or len(block.splitlines()) > max_issue_lines
        if should_compact:
            compacted.append(block)
            continue
        output.append(block.rstrip())

    if compacted:
        evidence_dir = feature / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(BEIJING).strftime("%Y%m%d-%H%M%S")
        history_path = evidence_dir / f"uat-compact-history-{stamp}.yaml"
        suffix = 1
        while history_path.exists():
            suffix += 1
            history_path = evidence_dir / f"uat-compact-history-{stamp}-{suffix}.yaml"
        history_ref = str(history_path.relative_to(feature))
        history_path.write_text("issues:\n" + "\n".join(compacted).rstrip() + "\n", encoding="utf-8")
        output = ["issues:"]
        for block in blocks:
            if block in compacted:
                output.append(_compact_stub(block, history_ref).rstrip())
            else:
                output.append(block.rstrip())
    else:
        history_path = None

    issues_path.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
    return CompactIssuesResult(
        active_path=issues_path,
        history_path=history_path,
        compacted_count=len(compacted),
    )


def _issue_blocks(content: str) -> list[str]:
    blocks: list[list[str]] = []
    current: list[str] | None = None
    for raw in content.splitlines():
        if ISSUE_ID_RE.match(raw):
            if current:
                blocks.append(current)
            current = [raw]
            continue
        if current is not None:
            current.append(raw)
    if current:
        blocks.append(current)
    return ["\n".join(block) for block in blocks]


def _issue_status(block: str) -> str:
    for line in block.splitlines():
        match = STATUS_RE.match(line)
        if match:
            return match.group(1).strip()
    return "open"


def _history_ref(block: str) -> str:
    for line in block.splitlines():
        match = HISTORY_REF_RE.match(line)
        if match:
            return match.group(1).strip().strip('"')
    return ""


def _is_compacted_stub(block: str) -> bool:
    if not _history_ref(block):
        return False
    for line in block.splitlines():
        if line.startswith("      "):
            return False
        if line.startswith("    "):
            key = line.strip().split(":", 1)[0]
            if key not in KEEP_SCALAR_KEYS and key != "history_ref":
                return False
    return True


def _compact_stub(block: str, history_ref: str) -> str:
    lines: list[str] = []
    for line in block.splitlines():
        if line.startswith("  - id:"):
            lines.append(line)
            continue
        if not line.startswith("    ") or line.startswith("      "):
            continue
        key = line.strip().split(":", 1)[0]
        if key in KEEP_SCALAR_KEYS and key != "history_ref":
            lines.append(line)
    lines.append(f'    history_ref: "{history_ref}"')
    return "\n".join(lines)
