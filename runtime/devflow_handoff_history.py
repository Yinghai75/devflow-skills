"""DevFlow handoff 溢出上下文归档辅助函数。"""

from __future__ import annotations

import re
from pathlib import Path


HANDOFF_HISTORY_REF_RE = re.compile(r"archived_handoff_context:\s*([^\s]+)")


def handoff_context_for_save(feature: Path, handoff_content: str, clear_context: bool) -> str:
    """返回保存 handoff 时应参与上下文保留计算的完整内容。"""

    if clear_context:
        return handoff_content
    archived_context = referenced_handoff_history_context(feature, handoff_content)
    if not archived_context:
        return handoff_content
    return f"{handoff_content.rstrip()}\n\n{archived_context}\n"


def archive_handoff_overflow(feature: Path, overflow: str, stamp: str, timestamp: str) -> str:
    """把被截断的 handoff 上下文写入 evidence，并返回 feature-relative 路径。"""

    evidence_dir = feature / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    history_path = evidence_dir / f"handoff-history-{stamp}.md"
    history_path.write_text(
        f"# 被截断的 handoff 上下文\n\n> 截断时间：{timestamp}\n\n{overflow}\n",
        encoding="utf-8",
    )
    return str(history_path.relative_to(feature))


def attach_handoff_history_ref(content: str, history_ref: str) -> str:
    """在当前 handoff 中写入归档上下文引用，供 restore 和后续 save 读取。"""

    return (
        f"{content.rstrip()}\n\n"
        "## 已归档的执行上下文\n\n"
        f"- archived_handoff_context: {history_ref}\n"
    )


def restore_handoff_content(feature: Path, handoff_content: str) -> str:
    """恢复 handoff 正文，并补回当前 handoff 引用的归档上下文。"""

    archived_context = referenced_handoff_history_context(feature, handoff_content)
    if not archived_context:
        return handoff_content
    return (
        f"{handoff_content.rstrip()}\n\n"
        "## 已归档的执行上下文\n\n"
        f"{archived_context}\n"
    )


def referenced_handoff_history_context(feature: Path, handoff_content: str) -> str:
    """读取当前 handoff 引用的最新归档上下文。"""

    refs = HANDOFF_HISTORY_REF_RE.findall(handoff_content)
    if not refs:
        return ""
    history_path = safe_feature_path(feature, refs[-1])
    if not history_path or not history_path.exists() or not history_path.is_file():
        return ""
    return history_body(history_path.read_text(encoding="utf-8"))


def safe_feature_path(feature: Path, ref: str) -> Path | None:
    candidate = (feature / ref).resolve()
    try:
        candidate.relative_to(feature.resolve())
    except ValueError:
        return None
    return candidate


def history_body(content: str) -> str:
    parts = content.split("\n\n", 2)
    if len(parts) == 3 and parts[0].startswith("# 被截断的 handoff 上下文"):
        return parts[2].strip()
    return content.strip()
