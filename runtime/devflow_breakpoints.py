"""DevFlow 分段断点的运行时辅助规则。"""

from __future__ import annotations

import re
from typing import Iterable

MAX_PRESERVED_LINES = 60

# 截断时优先保留的区块关键词（出现在区块首行即视为优先）
PRIORITY_CONTEXT_MARKERS = (
    "dispatch_queue",
    "doom_loop_breaker",
    "review_loop_breaker",
    "stop-loss",
    "stop_loss",
    "止损",
    "硬停",
    "fix_context_card",
    "uat 断点",
    "当前 uat 断点",
    "当前断点",
    "current_uat_breakpoint",
)


PERSISTENT_HANDOFF_HEADINGS = (
    "dispatch_queue",
    "uat 断点",
    "当前 uat 断点",
    "uat-ready",
    "current_uat_breakpoint",
    "fix_context_card",
    "plan_gap",
    "execution_gap",
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
    "fix_context_card:",
    "plan_gap:",
    "execution_gap:",
    "review_loop_breaker:",
    "doom_loop_breaker:",
    "stop-loss:",
    "stop_loss:",
)
GAP_HANDOFF_HEADINGS = (
    "plan_gap",
    "execution_gap",
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
) -> tuple[str, str]:
    """生成新的 handoff，并保留旧 handoff 中的队列、断点和止损上下文。

    Returns:
        (content, overflow) — overflow 为被截断的旧上下文，
        调用方负责归档到 evidence/。空字符串表示无溢出。
    """

    steps = "\n".join(f"  - {step}" for step in (next_steps or [])) or "  - 待补充"
    content = f"""# 断点

- 时间：{timestamp}
- 当前状态：{summary}
- 下一步：
    {steps}
"""
    marker_text = " ".join([summary, *(next_steps or [])])
    overflow = ""
    if clear_context or should_clear_handoff_context(marker_text):
        sections: list[str] = []
    else:
        sections = _persistent_handoff_sections(existing_content)
    if sections:
        kept, overflow_sections = cap_preserved_context(sections)
        if kept:
            content += f"\n## 已保留的执行上下文\n\n{'\n\n'.join(kept)}\n"
        overflow = "\n\n".join(overflow_sections)
    return content, overflow


def should_clear_handoff_context(text: str) -> bool:
    lowered = text.lower()
    tokens = set(re.split(r"\s+", lowered))
    return any(marker in tokens for marker in CLEAR_HANDOFF_CONTEXT_MARKERS)


def persistent_handoff_context(content: str) -> str:
    """只保留影响恢复执行的旧 handoff 内容，避免普通状态保存抹掉断点元数据。"""
    sections = _persistent_handoff_sections(content)
    return "\n\n".join(sections)


def _persistent_handoff_sections(content: str) -> list[str]:
    """提取并去重影响恢复执行的旧 handoff 区块，返回语义完整的 section 列表。"""
    lines = content.strip().splitlines()
    if not lines:
        return []
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
    return dedupe_sections(sections)


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
        if lines[index] and not lines[index].startswith((" ", "\t", "-", "*")) and line_has_marker(lines[index]):
            break
        index += 1
    return "\n".join(lines[start:index]).strip(), index


def collect_inline_context(lines: list[str], start: int) -> tuple[str, int]:
    index = start + 1
    while index < len(lines):
        current = lines[index]
        if is_heading(current):
            break
        if current and not current.startswith((" ", "\t", "-", "*")):
            break
        index += 1
    return "\n".join(lines[start:index]).strip(), index


def dedupe_sections(sections: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    latest_fix_context_card = ""
    latest_gap_sections: dict[str, str] = {}
    for section in sections:
        if is_fix_context_card_section(section):
            latest_fix_context_card = section
            continue
        gap_key = gap_section_key(section)
        if gap_key:
            latest_gap_sections[gap_key] = section
            continue
        if section in seen:
            continue
        seen.add(section)
        output.append(section)
    for key in ("plan_gap", "execution_gap"):
        if key in latest_gap_sections:
            output.append(latest_gap_sections[key])
    if latest_fix_context_card:
        output.append(latest_fix_context_card)
    return output


def is_fix_context_card_section(section: str) -> bool:
    lines = section.splitlines()
    if not lines:
        return False
    first = lines[0].strip().lower()
    return first.startswith("fix_context_card:") or bool(re.match(r"^#{1,6}\s+fix_context_card\b", first))


def gap_section_key(section: str) -> str:
    lines = section.splitlines()
    if not lines:
        return ""
    first = lines[0].strip().lower()
    for key in GAP_HANDOFF_HEADINGS:
        if first.startswith(f"{key}:") or re.match(rf"^#{{1,6}}\s+{key}\b", first):
            return key
    return ""


def _is_priority_section(section: str) -> bool:
    """判断区块是否属于恢复执行的优先上下文。"""
    first_line = section.strip().splitlines()[0].lower() if section.strip() else ""
    return any(marker in first_line for marker in PRIORITY_CONTEXT_MARKERS)


def cap_preserved_context(
    sections: list[str],
    max_lines: int = MAX_PRESERVED_LINES,
) -> tuple[list[str], list[str]]:
    """限制保留上下文的总行数。

    超过 max_lines 时，优先保留 dispatch_queue、止损和 fix_context_card 区块，
    其余旧上下文作为 overflow 返回，由调用方归档到 evidence/。

    Args:
        sections: 语义完整的 section 列表（heading + 内容已绑定）。

    Returns:
        (kept, overflow) — 均为 section 列表。
    """
    total = sum(len(s.splitlines()) for s in sections)
    if total <= max_lines:
        return sections, []

    priority: list[str] = []
    non_priority: list[str] = []
    for section in sections:
        (priority if _is_priority_section(section) else non_priority).append(section)

    # 优先填充 priority 区块，再填充 non-priority
    kept: list[str] = []
    overflow: list[str] = []
    used_lines = 0
    for section in priority:
        section_lines = len(section.splitlines())
        if used_lines + section_lines <= max_lines:
            kept.append(section)
            used_lines += section_lines
        else:
            overflow.append(section)
    for section in non_priority:
        section_lines = len(section.splitlines())
        if used_lines + section_lines <= max_lines:
            kept.append(section)
            used_lines += section_lines
        else:
            overflow.append(section)

    return kept, overflow
