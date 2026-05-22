"""DevFlow 分段断点的运行时辅助规则。"""

from __future__ import annotations

import re
from typing import Iterable


PERSISTENT_HANDOFF_HEADINGS = (
    "dispatch_queue",
    "uat 断点",
    "当前 uat 断点",
    "uat-ready",
    "current_uat_breakpoint",
    "review_loop_breaker",
    "doom_loop_breaker",
    "stop-loss",
    "stop_loss",
    "止损",
    "硬停",
    "失败摘要",
    "当前断点",
)
PERSISTENT_HANDOFF_INLINE_PREFIXES = (
    "dispatch_queue:",
    "current_uat_breakpoint:",
    "review_loop_breaker:",
    "doom_loop_breaker:",
    "stop-loss:",
    "stop_loss:",
)
CLEAR_HANDOFF_CONTEXT_MARKERS = (
    "clear_handoff_context",
)


def accept_state_blockers(state: dict[str, str | list[str]]) -> list[str]:
    """返回会阻断最终归档的分段断点状态。"""

    status = str(state.get("status", "")).strip().lower()
    if status == "ready_for_uat":
        return ["当前 feature 处于 ready_for_uat；必须先完成当前断点 UAT 或 waiver 后再归档"]
    return []


def build_handoff_content(
    summary: str,
    next_steps: Iterable[str] | None,
    timestamp: str,
    existing_content: str = "",
    clear_context: bool = False,
) -> str:
    """生成新的 handoff，并保留旧 handoff 中的队列、断点和止损上下文。"""

    steps = "\n".join(f"  - {step}" for step in (next_steps or [])) or "  - 待补充"
    content = f"""# 断点

- 时间：{timestamp}
- 当前状态：{summary}
- 下一步：
    {steps}
"""
    marker_text = " ".join([summary, *(next_steps or [])])
    preserved = "" if clear_context or should_clear_handoff_context(marker_text) else persistent_handoff_context(existing_content)
    if preserved:
        content += f"\n## 已保留的执行上下文\n\n{preserved}\n"
    return content


def should_clear_handoff_context(text: str) -> bool:
    lowered = text.lower()
    tokens = set(re.split(r"\s+", lowered))
    return any(marker in tokens for marker in CLEAR_HANDOFF_CONTEXT_MARKERS)


def persistent_handoff_context(content: str) -> str:
    """只保留影响恢复执行的旧 handoff 内容，避免普通状态保存抹掉断点元数据。"""

    lines = content.strip().splitlines()
    if not lines:
        return ""
    sections: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line_has_marker(line):
            index += 1
            continue
        if is_heading(line):
            section, index = collect_heading_section(lines, index)
        else:
            section, index = collect_inline_context(lines, index)
        if section:
            sections.append(section)
    return "\n\n".join(dedupe_sections(sections))


def line_has_marker(line: str) -> bool:
    lowered = line.lower()
    if is_heading(line):
        heading = re.sub(r"^#{1,6}\s+", "", lowered).strip()
        return any(marker in heading for marker in PERSISTENT_HANDOFF_HEADINGS)
    stripped = lowered.strip()
    return any(stripped.startswith(marker) for marker in PERSISTENT_HANDOFF_INLINE_PREFIXES)


def is_heading(line: str) -> bool:
    return bool(re.match(r"^#{1,6}\s+", line))


def heading_level(line: str) -> int:
    match = re.match(r"^(#{1,6})\s+", line)
    return len(match.group(1)) if match else 0


def collect_heading_section(lines: list[str], start: int) -> tuple[str, int]:
    level = heading_level(lines[start])
    index = start + 1
    while index < len(lines):
        if is_heading(lines[index]) and heading_level(lines[index]) <= level:
            break
        index += 1
    return "\n".join(lines[start:index]).strip(), index


def collect_inline_context(lines: list[str], start: int) -> tuple[str, int]:
    index = start + 1
    while index < len(lines):
        current = lines[index]
        if is_heading(current):
            break
        if current and not current.startswith((" ", "\t", "-", "*")) and not line_has_marker(current):
            break
        index += 1
    return "\n".join(lines[start:index]).strip(), index


def dedupe_sections(sections: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for section in sections:
        if section in seen:
            continue
        seen.add(section)
        output.append(section)
    return output
