#!/usr/bin/env python3
"""DevFlow 的确定性脚手架与状态维护工具。"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo

from devflow_issues import compact_issues


BEIJING = ZoneInfo("Asia/Shanghai")
VALID_LANES = {"fast", "standard", "high-risk"}
VALID_SEVERITIES = {"low", "medium", "high", "critical"}
VALID_TARGET_ENVS = {"local", "dev-fast", "dev-full", "online"}
EFFECTIVE_GATE_TYPES = {"regression", "golden", "integration", "e2e"}
EXECUTABLE_PREFIXES = {
    "uv",
    "python",
    "python3",
    "bash",
    "sh",
    "zsh",
    "npm",
    "npx",
    "pnpm",
    "bun",
    "yarn",
    "node",
    "make",
    "pytest",
    "cargo",
    "go",
    "docker",
    "docker-compose",
    "curl",
    "git",
    "env",
}
COMMAND_PLACEHOLDERS = {"按项目", "待补充", "todo", "tbd", "实际命令", "填写", "替换"}
SHELL_CONTROL_TOKENS = {"|", "||", "&", "&&", ";", "<", ">", ">>", "2>", "2>>"}
HIGH_RISK_MARKERS = {
    "dify",
    "workflow",
    "workflows",
    "state-machine",
    "状态机",
    "main-state",
    "数据写入",
    "写入",
    "login",
    "登录",
    "权限",
    "线上",
    "发布",
    "shared-runtime",
    "runtime",
    "orchestration",
    "跨模块",
}
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


@dataclass(frozen=True)
class Handoff:
    feature_dir: Path
    content: str


@dataclass(frozen=True)
class UatIssue:
    issue_id: str
    title: str


@dataclass(frozen=True)
class GateRecommendation:
    selected_ids: list[str]


@dataclass(frozen=True)
class AcceptResult:
    ok: bool
    messages: list[str]
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GateEvidence:
    gate_id: str
    status: str
    log_path: Path
    exit_code: int


def now_text() -> str:
    return datetime.now(BEIJING).strftime("%Y-%m-%d %H:%M:%S %Z")


def slugify(title: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", title.strip()).strip("-")
    return cleaned.lower()[:48] or "feature"


def active_root(repo: Path) -> Path:
    return repo / "devflow" / "active"


def archive_root(repo: Path) -> Path:
    return repo / "devflow" / "archive"


def shared_root(repo: Path) -> Path:
    return repo / "devflow" / "shared"


def codebase_map_root(repo: Path) -> Path:
    return shared_root(repo) / "codebase_map"


def feature_to_repo(feature: Path | str) -> Path:
    feature = Path(feature).resolve()
    repo = feature.parents[2]
    if not (repo / "devflow").is_dir():
        raise ValueError(f"无法从 feature 目录推断 repo 根目录：{feature}")
    return repo


def feature_to_devflow(feature: Path | str) -> Path:
    return feature_to_repo(feature) / "devflow"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def ensure_shared(repo: Path) -> None:
    shared = shared_root(repo)
    (shared / "golden_sets").mkdir(parents=True, exist_ok=True)
    ensure_codebase_map(repo)
    registry = shared / "gate_registry.yaml"
    if registry.exists():
        return
    write_text(
        registry,
        """# DevFlow 项目门禁注册表。按项目实际命令更新 command 字段。
gates:
  - id: unit-tests
    type: regression
    surfaces: [python, unit, local]
    command: "uv run python -m unittest discover"
    risk_blocked: "局部逻辑回归"
    failure_signal: "单元测试失败"
  - id: dify-export-validate
    type: integration
    surfaces: [dify, workflow, online-object]
    command: "uv run python scripts/gen_dify_dsl.py --check"
    risk_blocked: "Dify 工作流结构或发布对象漂移"
    failure_signal: "导出校验、节点连线或关键字段不一致"
  - id: state-machine-regression
    type: regression
    surfaces: [state-machine, main-state, orchestration]
    command: "uv run python scripts/run_main_chatflow_regression_gate.py --json"
    risk_blocked: "主状态流转、阶段边界或回填逻辑被破坏"
    failure_signal: "历史样本状态不一致或阶段断言失败"
  - id: dev-fast-integration
    type: integration
    surfaces: [integration, dev-fast, cross-module, dify, orchestration]
    command: "uv run python scripts/run_dev_fast_gate.py --json"
    risk_blocked: "跨模块契约、Dify 邻域门禁或 dev-fast 集成路径被破坏"
    failure_signal: "dev-fast 聚合门禁失败或生成失败项"
  - id: dev-full-e2e
    type: e2e
    surfaces: [e2e, dev-full, dify, container, online-object]
    command: "uv run python scripts/run_dev_full_gate.py --json"
    risk_blocked: "本地完整复刻、Dify 容器联调或端到端样本路径失效"
    failure_signal: "dev-full 完整门禁失败或样本回放不一致"
  - id: official-site-login-smoke
    type: e2e
    surfaces: [login, official-site, erp-executor, browser]
    command: "uv run python -m pytest -q"
    risk_blocked: "首轮登录恢复、权限或浏览器执行器边界被破坏"
    failure_signal: "登录流程无法完成或职责边界被绕回 Dify"
""",
    )


def current_source_commit(repo: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def ensure_codebase_map(repo: Path) -> None:
    root = codebase_map_root(repo)
    (root / "modules").mkdir(parents=True, exist_ok=True)
    overview = root / "OVERVIEW.md"
    if overview.exists():
        return
    # 占位 OVERVIEW，等 df-plan 或 df-codebase-map 全量扫描后填充
    write_text(
        overview,
        f"# 仓库索引\n\n> 待 df-plan 或 df-codebase-map 全量扫描后生成。\n",
    )


def create_feature(
    repo: Path | str,
    title: str,
    lane: str = "standard",
    goal: str = "",
    constraints: Iterable[str] | None = None,
    success: Iterable[str] | None = None,
    surfaces: Iterable[str] | None = None,
    paths: Iterable[str] | None = None,
    target_env: str = "local",
) -> Path:
    repo = Path(repo)
    if target_env not in VALID_TARGET_ENVS:
        choices = ", ".join(sorted(VALID_TARGET_ENVS))
        raise ValueError(f"无效目标环境：{target_env}，合法值：{choices}")
    lane = infer_lane(
        lane,
        title=title,
        goal=goal,
        surfaces=surfaces or [],
        paths=paths or [],
        target_env=target_env,
    )
    if lane not in VALID_LANES:
        raise ValueError(f"无效车道：{lane}")
    ensure_shared(repo)
    stamp = datetime.now(BEIJING).strftime("%Y%m%d-%H%M")
    feature = (active_root(repo) / f"{stamp}-{slugify(title)}").resolve()
    feature.mkdir(parents=True, exist_ok=False)
    constraints = list(constraints or [])
    success = list(success or [])
    created = now_text()

    context = {
        "title": title,
        "lane": lane,
        "created_at": created,
        "target_env": target_env,
        "goal": goal or "待补充",
        "constraints": bullet_list(constraints),
        "success": bullet_list(success),
        "fast_note": fast_note(lane),
        "codebase_map_waiver": codebase_map_waiver_note(lane),
    }
    for template in sorted(TEMPLATE_DIR.iterdir()):
        if template.is_file() and not template.name.startswith("."):
            write_text(feature / template.name, render_template(template, context))
    save_active_pointer(repo, feature)
    return feature


def bullet_list(values: Iterable[str]) -> str:
    values = [value for value in values if value]
    if not values:
        return "- 待补充"
    return "\n".join(f"- {value}" for value in values)


def render_template(template: Path, context: dict[str, str]) -> str:
    text = template.read_text(encoding="utf-8")
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def fast_note(lane: str) -> str:
    if lane != "fast":
        return ""
    return "\n> fast 车道可轻量填写，但涉及高风险面时必须补全本节。\n"


def codebase_map_waiver_note(lane: str) -> str:
    if lane == "fast":
        return "fast 车道可豁免；如豁免，必须写明理由、残余风险和后续补 scope 条件。"
    return "standard/high-risk 车道缺失或过期时，必须先用 df-codebase-map 按 scope 刷新。"


def infer_lane(
    requested_lane: str,
    title: str = "",
    goal: str = "",
    surfaces: Iterable[str] | None = None,
    paths: Iterable[str] | None = None,
    target_env: str = "local",
) -> str:
    if requested_lane == "high-risk":
        return "high-risk"
    haystack = " ".join([title, goal, target_env, *(surfaces or []), *(paths or [])]).lower()
    if any(marker.lower() in haystack for marker in HIGH_RISK_MARKERS):
        return "high-risk"
    if target_env == "online":
        return "high-risk"
    return requested_lane


def save_active_pointer(repo: Path, feature: Path) -> None:
    write_text(repo / "devflow" / "active" / ".current", str(feature.resolve()) + "\n")


def load_active_feature(repo: Path) -> Path:
    pointer = repo / "devflow" / "active" / ".current"
    if pointer.exists():
        candidate = Path(pointer.read_text(encoding="utf-8").strip())
        if candidate.exists():
            return candidate
    candidates = sorted(active_root(repo).glob("*"), key=lambda p: p.name)
    dirs = [p for p in candidates if p.is_dir()]
    if not dirs:
        raise FileNotFoundError("未找到 active feature")
    return dirs[-1]


def save_handoff(feature: Path | str, summary: str, next_steps: Iterable[str] | None = None) -> None:
    feature = Path(feature)
    steps = "\n".join(f"  - {step}" for step in (next_steps or [])) or "  - 待补充"
    write_text(
        feature / "handoff.md",
        f"""# 断点

- 时间：{now_text()}
- 当前状态：{summary}
- 下一步：
{steps}
""",
    )
    update_state(feature, current_step=summary)


def restore_handoff(repo: Path | str) -> Handoff:
    repo = Path(repo)
    feature = load_active_feature(repo)
    return Handoff(feature_dir=feature, content=(feature / "handoff.md").read_text(encoding="utf-8"))


def existing_uat_issue_ids(feature: Path | str) -> list[int]:
    feature = Path(feature)
    paths = [feature / "issues.yaml"]
    evidence_dir = feature / "evidence"
    if evidence_dir.exists():
        paths.extend(sorted(evidence_dir.glob("*.yaml")))
        paths.extend(sorted(evidence_dir.glob("*.yml")))

    ids: set[int] = set()
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\bUAT-(\d{3,})\b", content):
            ids.add(int(match.group(1)))
    return sorted(ids)


def add_uat_issue(
    feature: Path | str,
    title: str,
    description: str,
    severity: str = "medium",
) -> UatIssue:
    feature = Path(feature)
    if severity not in VALID_SEVERITIES:
        choices = ", ".join(sorted(VALID_SEVERITIES))
        raise ValueError(f"无效严重度：{severity}，合法值：{choices}")
    existing = (feature / "issues.yaml").read_text(encoding="utf-8")
    ids = existing_uat_issue_ids(feature)
    issue_id = f"UAT-{(max(ids) if ids else 0) + 1:03d}"
    if existing.strip() == "issues: []":
        write_text(feature / "issues.yaml", "issues:\n")
    append_text(
        feature / "issues.yaml",
        f"""  - id: {issue_id}
    title: "{title}"
    severity: {severity}
    status: open
    created_at: "{now_text()}"
    description: "{description}"
""",
    )
    append_text(
        feature / "uat.md",
        f"""
## {issue_id} {title}

- 严重度：{severity}
- 状态：open
- 现象：{description}
""",
    )
    update_state(feature, current_step=f"记录 UAT issue {issue_id}")
    return UatIssue(issue_id=issue_id, title=title)


def registry_gates(feature: Path) -> list[dict[str, str | list[str]]]:
    registry = feature_to_devflow(feature) / "shared" / "gate_registry.yaml"
    gates: list[dict[str, str | list[str]]] = []
    current: dict[str, str | list[str]] | None = None
    for raw in registry.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("- id:"):
            if current:
                gates.append(current)
            current = {"id": line.split(":", 1)[1].strip()}
        elif current is not None and ":" in line:
            key, value = line.split(":", 1)
            value = value.strip().strip('"')
            if value.startswith("[") and value.endswith("]"):
                current[key] = [part.strip() for part in value[1:-1].split(",") if part.strip()]
            else:
                current[key] = value
    if current:
        gates.append(current)
    return gates


def registry_gate(feature: Path, gate_id: str) -> dict[str, str | list[str]]:
    for gate in registry_gates(feature):
        if gate.get("id") == gate_id:
            return gate
    raise KeyError(f"未知门禁：{gate_id}")


def recommend_gates(feature: Path | str, surfaces: Iterable[str]) -> GateRecommendation:
    feature = Path(feature)
    wanted = {surface.strip() for surface in surfaces if surface.strip()}
    selected: list[dict[str, str | list[str]]] = []
    for gate in registry_gates(feature):
        gate_surfaces = set(gate.get("surfaces", [])) if isinstance(gate.get("surfaces"), list) else set()
        if wanted & gate_surfaces:
            selected.append(gate)
    ids = [str(gate["id"]) for gate in selected]
    update_state(feature, selected_gates=ids)
    append_text(
        feature / "validation.md",
        "\n## 已选择门禁\n"
        + "\n".join(
            f"- `{gate['id']}`：拦截风险：{gate.get('risk_blocked', '待补充')}；失败信号：{gate.get('failure_signal', '待补充')}"
            for gate in selected
        )
        + "\n",
    )
    return GateRecommendation(selected_ids=ids)


def update_state(feature: Path, **updates: str | list[str]) -> None:
    path = feature / "state.yaml"
    lines = path.read_text(encoding="utf-8").splitlines()
    updates = {**updates, "updated_at": now_text()}
    keys = set(updates)
    output: list[str] = []
    skip_list = False
    for line in lines:
        if skip_list and line.startswith("  - "):
            continue
        skip_list = False
        key = line.split(":", 1)[0] if ":" in line else ""
        if key in keys:
            value = updates[key]
            if isinstance(value, list):
                output.append(f"{key}:")
                output.extend(f"  - {item}" for item in value)
                skip_list = True
            else:
                output.append(f'{key}: "{value}"')
            keys.remove(key)
        else:
            output.append(line)
    for key in keys:
        value = updates[key]
        if isinstance(value, list):
            output.append(f"{key}:")
            output.extend(f"  - {item}" for item in value)
        else:
            output.append(f'{key}: "{value}"')
    write_text(path, "\n".join(output) + "\n")


def parse_state(feature: Path) -> dict[str, str | list[str]]:
    state: dict[str, str | list[str]] = {}
    current_key = ""
    for raw in (feature / "state.yaml").read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("  - ") and current_key:
            state.setdefault(current_key, [])
            assert isinstance(state[current_key], list)
            state[current_key].append(line[4:].strip().strip('"'))
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key
            value = value.strip().strip('"')
            state[key] = [] if value == "" else value
    return state


def gate_type_map(feature: Path) -> dict[str, str]:
    return {str(gate["id"]): str(gate.get("type", "")) for gate in registry_gates(feature)}


def run_gate(feature: Path | str, gate_id: str) -> GateEvidence:
    feature = Path(feature)
    gate = registry_gate(feature, gate_id)
    command = str(gate.get("command", "")).strip()
    if not is_executable_command(command):
        raise ValueError(f"门禁 {gate_id} 缺少可执行 command")
    evidence_dir = feature / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(BEIJING).strftime("%Y%m%d-%H%M%S")
    log_path = evidence_dir / f"{gate_id}-{stamp}.log"
    repo = feature_to_repo(feature)
    argv = command_argv(command)
    if argv is None:
        raise ValueError(f"门禁 {gate_id} 缺少可执行 command")
    completed = subprocess.run(argv, shell=False, cwd=repo, text=True, capture_output=True)
    status = "passed" if completed.returncode == 0 else "failed"
    write_text(
        log_path,
        "\n".join(
            [
                f"gate: {gate_id}",
                f"status: {status}",
                f"exit_code: {completed.returncode}",
                f"command: {command}",
                f"run_at: {now_text()}",
                "",
                "## stdout",
                completed.stdout,
                "## stderr",
                completed.stderr,
            ]
        ),
    )
    record = {
        "gate_id": gate_id,
        "status": status,
        "exit_code": completed.returncode,
        "command": command,
        "run_at": now_text(),
        "log_path": str(log_path.relative_to(feature)),
    }
    append_manifest(feature, record)
    return GateEvidence(gate_id=gate_id, status=status, log_path=log_path, exit_code=completed.returncode)


def manifest_path(feature: Path) -> Path:
    return feature / "evidence" / "manifest.json"


def append_manifest(feature: Path, record: dict[str, str | int]) -> None:
    path = manifest_path(feature)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"gates": []}
    data.setdefault("gates", []).append(record)
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def evidence_records(feature: Path) -> list[dict[str, str | int]]:
    path = manifest_path(feature)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    records = data.get("gates", [])
    return records if isinstance(records, list) else []


def is_executable_command(command: str) -> bool:
    return command_argv(command) is not None


def command_argv(command: str) -> list[str] | None:
    if not command:
        return None
    lowered = command.lower()
    if any(marker in lowered for marker in COMMAND_PLACEHOLDERS):
        return None
    try:
        parts = shlex.split(command)
    except ValueError:
        return None
    if not parts:
        return None
    if any(part in SHELL_CONTROL_TOKENS for part in parts):
        return None
    if any("$(" in part or "`" in part for part in parts):
        return None
    executable = parts[0]
    if executable in EXECUTABLE_PREFIXES or executable.startswith("./") or executable.startswith("/"):
        return parts
    return None


def checklist_incomplete(feature: Path) -> bool:
    path = feature / "checklist.yaml"
    current_item = False
    saw_item = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("- id:"):
            current_item = True
            saw_item = True
            continue
        if current_item and line.startswith("status:"):
            status = line.split(":", 1)[1].strip().strip('"')
            current_item = False
            if status not in {"done", "waived"}:
                return True
    return not saw_item


def has_open_issues(feature: Path) -> bool:
    for raw in (feature / "issues.yaml").read_text(encoding="utf-8").splitlines():
        if raw.startswith("    status:") and raw.split(":", 1)[1].strip().strip('"') not in {"closed", "deferred"}:
            return True
    return False


def validation_is_initial_template(feature: Path, lane: str) -> bool:
    current = (feature / "validation.md").read_text(encoding="utf-8").strip()
    expected = render_template(TEMPLATE_DIR / "validation.md", {"fast_note": fast_note(lane)}).strip()
    return current == expected or current.count("待补充") >= 5


def accept_feature(feature: Path | str) -> AcceptResult:
    feature = Path(feature)
    state = parse_state(feature)
    messages: list[str] = []
    warnings: list[str] = []
    lane = str(state.get("lane", "standard"))
    selected = state.get("selected_gates", [])
    selected_ids = selected if isinstance(selected, list) else []
    gate_types = gate_type_map(feature)
    effective = [gate for gate in selected_ids if gate_types.get(gate) in EFFECTIVE_GATE_TYPES and gate != "smoke"]
    records = evidence_records(feature)
    passed_gates = {str(record.get("gate_id")) for record in records if record.get("status") == "passed"}
    failed_gates = [str(record.get("gate_id")) for record in records if record.get("status") == "failed"]
    if checklist_incomplete(feature):
        messages.append("checklist 仍有未完成项")
    if has_open_issues(feature):
        messages.append("仍有未关闭 UAT issue")
    if lane == "high-risk" and not effective:
        messages.append("高风险任务未选择有效防炸门禁")
    if lane == "high-risk" and not state.get("red_evidence"):
        messages.append("高风险任务缺少 RED 证据或历史故障样本")
    if failed_gates:
        messages.append("存在失败门禁证据")
    if effective and not records:
        messages.append("缺少机器生成的门禁证据")
    missing_gate_evidence = [gate for gate in effective if gate not in passed_gates]
    if missing_gate_evidence and records:
        messages.append("关键门禁缺少通过证据")
    if lane == "standard" and not effective and validation_is_initial_template(feature, lane):
        warnings.append("validation.md 仍是初始模板")
    if messages:
        return AcceptResult(ok=False, messages=messages, warnings=warnings)

    repo = feature_to_repo(feature)
    destination = archive_root(repo) / feature.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"归档目录已存在：{destination}")
    shutil.move(str(feature), str(destination))
    pointer = active_root(repo) / ".current"
    if pointer.exists():
        pointer.unlink()
    return AcceptResult(ok=True, messages=[f"已归档到 {destination}"], warnings=warnings)


def parse_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="DevFlow 本地状态工具")
    parser.add_argument("--repo", default=".", help="项目根目录")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    start.add_argument("title")
    start.add_argument("--lane", default="standard", choices=sorted(VALID_LANES))
    start.add_argument("--goal", default="")
    start.add_argument("--constraints", default="")
    start.add_argument("--success", default="")
    start.add_argument("--surfaces", default="")
    start.add_argument("--paths", default="")
    start.add_argument("--target-env", default="local", choices=sorted(VALID_TARGET_ENVS))

    status = sub.add_parser("status")
    status.add_argument("--restore", "-r", action="store_true")
    status.add_argument("--summary", default="")
    status.add_argument("--next", default="")

    uat = sub.add_parser("uat")
    uat.add_argument("title")
    uat.add_argument("description")
    uat.add_argument("--severity", default="medium", choices=sorted(VALID_SEVERITIES))

    gates = sub.add_parser("gates")
    gates.add_argument("--surfaces", required=True)

    run = sub.add_parser("run-gate")
    run.add_argument("gate_id")

    sub.add_parser("compact-issues")

    sub.add_parser("accept")

    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    if args.command == "start":
        feature = create_feature(
            repo,
            args.title,
            args.lane,
            args.goal,
            parse_list(args.constraints),
            parse_list(args.success),
            parse_list(args.surfaces),
            parse_list(args.paths),
            args.target_env,
        )
        print(feature)
        return 0
    if args.command == "status":
        if args.restore:
            handoff = restore_handoff(repo)
            print(f"feature: {handoff.feature_dir}")
            print(handoff.content)
        else:
            feature = load_active_feature(repo)
            save_handoff(feature, args.summary or "保存断点", parse_list(args.next))
            print(feature / "handoff.md")
        return 0
    feature = load_active_feature(repo)
    if args.command == "uat":
        issue = add_uat_issue(feature, args.title, args.description, args.severity)
        print(issue.issue_id)
        return 0
    if args.command == "gates":
        result = recommend_gates(feature, parse_list(args.surfaces))
        print("\n".join(result.selected_ids))
        return 0
    if args.command == "run-gate":
        evidence = run_gate(feature, args.gate_id)
        print(evidence.log_path)
        return 0 if evidence.status == "passed" else 2
    if args.command == "compact-issues":
        result = compact_issues(feature)
        print(result.history_path or result.active_path)
        return 0
    if args.command == "accept":
        result = accept_feature(feature)
        for warning in result.warnings:
            print(f"警告：{warning}")
        for message in result.messages:
            print(message)
        return 0 if result.ok else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
