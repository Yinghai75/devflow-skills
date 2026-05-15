import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from devflow_cli import (
    TEMPLATE_DIR,
    accept_feature,
    add_uat_issue,
    create_feature,
    ensure_shared,
    existing_uat_issue_ids,
    infer_lane,
    is_executable_command,
    recommend_gates,
    registry_gates,
    restore_handoff,
    run_gate,
    save_handoff,
    update_state,
)
from devflow_issues import compact_issues


class DevFlowCliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_feature_generates_required_files_and_parseable_frontmatter(self):
        feature = create_feature(
            repo=self.repo,
            title="修复 Dify 状态机回填",
            lane="high-risk",
            goal="确保状态机回填不会破坏主链状态",
            constraints=["不改线上对象"],
            success=["新增防炸门禁"],
        )

        expected = {
            "context.md",
            "plan.md",
            "checklist.yaml",
            "state.yaml",
            "validation.md",
            "uat.md",
            "issues.yaml",
            "review-findings.yaml",
            "handoff.md",
            "acceptance.md",
        }
        self.assertEqual(expected, {p.name for p in feature.iterdir() if p.is_file()})
        self.assertTrue((self.repo / "devflow/shared/gate_registry.yaml").exists())
        self.assertTrue((self.repo / "devflow/shared/golden_sets").is_dir())
        self.assertTrue((self.repo / "devflow/shared/codebase_map/OVERVIEW.md").exists())
        self.assertTrue((self.repo / "devflow/shared/codebase_map/modules").is_dir())

        plan = (feature / "plan.md").read_text(encoding="utf-8")
        self.assertTrue(plan.startswith("---\n"))
        self.assertIn('lane: "high-risk"', plan)
        self.assertIn("修复 Dify 状态机回填", plan)
        self.assertIn("## 非目标", plan)
        self.assertEqual(1, plan.count("## Capability Coverage Matrix"))
        self.assertNotIn("verify matrix", plan.lower())
        self.assertIn("用户动作链", plan)
        self.assertIn("下游成功判据", plan)
        self.assertIn("失败信号", plan)
        self.assertIn("不可替代证据", plan)
        context = (feature / "context.md").read_text(encoding="utf-8")
        checklist = (feature / "checklist.yaml").read_text(encoding="utf-8")
        self.assertIn('target_env: "local"', context)
        self.assertIn("map_modules_read:", context)
        self.assertIn("codebase_map_waiver:", context)
        self.assertIn("确认设计文档是否需要同步更新", checklist)
        self.assertIn("确认发布闭环是否适用", checklist)
        validation = (feature / "validation.md").read_text(encoding="utf-8")
        self.assertIn("Capability Coverage Matrix 核验", validation)
        self.assertIn("用户动作链", validation)
        uat = (feature / "uat.md").read_text(encoding="utf-8")
        self.assertIn("Capability Coverage Matrix 对齐项", uat)
        self.assertIn("对应下游成功判据", uat)
        acceptance = (feature / "acceptance.md").read_text(encoding="utf-8")
        self.assertIn("capability_coverage_matrix_checked: false", acceptance)
        self.assertIn("codebase_map_checked: false", acceptance)
        self.assertIn("truth_doc_checked: false", acceptance)
        self.assertIn("golden_set_checked: false", acceptance)
        self.assertIn("review_loop_checked: false", acceptance)
        review_findings = (feature / "review-findings.yaml").read_text(encoding="utf-8")
        self.assertIn("review_loop_status: not_applicable", review_findings)

    def test_ensure_shared_creates_codebase_map_overview(self):
        ensure_shared(self.repo)

        overview = (self.repo / "devflow/shared/codebase_map/OVERVIEW.md").read_text(encoding="utf-8")

        self.assertIn("仓库索引", overview)
        self.assertTrue((self.repo / "devflow/shared/codebase_map/modules").is_dir())

    def test_default_gate_registry_has_no_placeholder_commands(self):
        ensure_shared(self.repo)
        feature = create_feature(self.repo, "默认门禁", "standard", "检查默认 registry", [], [])

        commands = [str(gate.get("command", "")) for gate in registry_gates(feature)]

        self.assertGreaterEqual(len(commands), 5)
        for command in commands:
            self.assertTrue(is_executable_command(command), command)
            self.assertNotIn("按项目", command)
            self.assertNotIn("待补充", command)

    def test_fast_lane_validation_keeps_fast_note(self):
        feature = create_feature(self.repo, "快速文档", "fast", "补文档", [], [])

        validation = (feature / "validation.md").read_text(encoding="utf-8")

        self.assertIn("fast 车道可轻量填写", validation)

    def test_create_feature_skips_hidden_template_files(self):
        hidden = TEMPLATE_DIR / ".DS_Store"
        hidden.write_text("不应生成", encoding="utf-8")
        try:
            feature = create_feature(self.repo, "隐藏模板", "standard", "检查模板", [], [])
        finally:
            hidden.unlink(missing_ok=True)

        self.assertFalse((feature / ".DS_Store").exists())

    def test_save_and_restore_handoff_records_current_breakpoint(self):
        feature = create_feature(self.repo, "局部修复", "standard", "完成修复", [], [])

        save_handoff(feature, "正在执行 checklist 第 2 项", next_steps=["运行单测"])
        restored = restore_handoff(self.repo)

        self.assertEqual(feature, restored.feature_dir)
        self.assertIn("正在执行 checklist 第 2 项", restored.content)
        self.assertIn("运行单测", restored.content)

    def test_update_state_keeps_single_updated_at_field(self):
        feature = create_feature(self.repo, "状态更新", "standard", "完成修复", [], [])

        update_state(feature, current_step="第一步")
        update_state(feature, current_step="第二步")

        state = (feature / "state.yaml").read_text(encoding="utf-8")
        self.assertEqual(1, state.count("updated_at:"))

    def test_add_uat_issue_creates_feature_local_issue(self):
        feature = create_feature(self.repo, "UAT 问题", "standard", "闭环 UAT", [], [])

        issue = add_uat_issue(feature, "按钮无响应", "点击保存后没有提示", severity="high")

        issues = (feature / "issues.yaml").read_text(encoding="utf-8")
        uat = (feature / "uat.md").read_text(encoding="utf-8")
        self.assertEqual("UAT-001", issue.issue_id)
        self.assertIn("按钮无响应", issues)
        self.assertIn("点击保存后没有提示", uat)

    def test_add_uat_issue_escapes_yaml_sensitive_text(self):
        feature = create_feature(self.repo, "UAT 转义", "standard", "闭环 UAT", [], [])

        add_uat_issue(feature, '按钮"保存"无响应', "第一行\n第二行: 带冒号", severity="high")

        fields = self.issue_fields(feature / "issues.yaml")
        self.assertEqual('按钮"保存"无响应', json.loads(fields["title"]))
        self.assertEqual("第一行\n第二行: 带冒号", json.loads(fields["description"]))

    def test_add_uat_issue_uses_archived_history_for_next_id(self):
        feature = create_feature(self.repo, "UAT 历史分层", "standard", "闭环 UAT", [], [])
        evidence = feature / "evidence"
        evidence.mkdir()
        (evidence / "uat-full-history.yaml").write_text(
            """issues:
  - id: UAT-010
    status: closed
""",
            encoding="utf-8",
        )

        issue = add_uat_issue(feature, "新失败面", "复测发现新的问题", severity="medium")

        self.assertEqual("UAT-011", issue.issue_id)
        self.assertEqual([11], existing_uat_issue_ids(feature)[-1:])

    def test_add_uat_issue_rejects_invalid_severity(self):
        feature = create_feature(self.repo, "UAT 严重度", "standard", "闭环 UAT", [], [])

        with self.assertRaisesRegex(ValueError, "无效严重度"):
            add_uat_issue(feature, "按钮无响应", "点击保存后没有提示", severity="urgent")

    def test_recommend_gates_matches_high_risk_surfaces(self):
        feature = create_feature(self.repo, "登录恢复", "high-risk", "修复登录", [], [])

        result = recommend_gates(feature, surfaces=["dify", "state-machine", "login"])

        self.assertIn("dify-export-validate", result.selected_ids)
        self.assertIn("state-machine-regression", result.selected_ids)
        self.assertIn("official-site-login-smoke", result.selected_ids)
        validation = (feature / "validation.md").read_text(encoding="utf-8")
        self.assertIn("Impact Map", validation)
        self.assertIn("RED Evidence", validation)

    def test_accept_blocks_high_risk_without_effective_gate(self):
        feature = create_feature(self.repo, "高风险无门禁", "high-risk", "改状态机", [], [])

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("高风险任务未选择有效防炸门禁", result.messages)

    def test_accept_blocks_incomplete_checklist(self):
        feature = create_feature(self.repo, "未完成 checklist", "standard", "局部修复", [], [])
        update_state(feature, status="validated")

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("checklist 仍有未完成项", result.messages)

    def test_accept_blocks_open_uat_issues(self):
        feature = create_feature(self.repo, "开放 UAT", "standard", "修复 UAT", [], [])
        self.complete_default_checklist(feature)
        update_state(feature, status="validated")
        add_uat_issue(feature, "按钮无响应", "点击保存后没有提示")

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("仍有未关闭 UAT issue", result.messages)

    def test_accept_blocks_fixed_pending_retest_issue(self):
        feature = create_feature(self.repo, "待复测 issue", "standard", "修复 UAT", [], [])
        self.complete_default_checklist(feature)
        update_state(feature, status="validated")
        (feature / "issues.yaml").write_text(
            """issues:
  - id: UAT-001
    title: "已修待复测"
    severity: high
    status: fixed_pending_retest
    description: "代码已改，但用户原路径尚未复测"
""",
            encoding="utf-8",
        )

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("仍有未关闭 UAT issue", result.messages)

    def test_accept_blocks_closed_issue_with_pending_retest_markers(self):
        feature = create_feature(self.repo, "旧待复测 issue", "standard", "修复 UAT", [], [])
        self.complete_default_checklist(feature)
        update_state(feature, status="validated")
        (feature / "issues.yaml").write_text(
            """issues:
  - id: UAT-001
    title: "closed 但需复测"
    severity: high
    status: closed
    needs_retest: true
    description: "legacy closed 仍需复测"
  - id: UAT-002
    title: "closed 但 pending"
    severity: medium
    status: closed
    retest_status: pending
    description: "legacy closed pending"
""",
            encoding="utf-8",
        )

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("仍有未关闭 UAT issue", result.messages)

    def test_accept_blocks_unresolved_review_findings(self):
        feature = create_feature(self.repo, "未处理 review", "standard", "修复 review finding", [], [])
        self.complete_default_checklist(feature)
        (feature / "review-findings.yaml").write_text(
            """review_loop_status: pass
rounds: []
findings:
  - priority: P1
    file: runtime/devflow_cli.py
    line: 1
    summary: "accept 未阻断 review finding"
    status: open
waivers: []
manual_review: []
tooling_blocked: false
""",
            encoding="utf-8",
        )

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("review-findings.yaml 存在未处理 P0/P1", result.messages)

    def test_accept_blocks_stale_review_findings_when_review_evidence_exists(self):
        feature = create_feature(self.repo, "陈旧 review", "standard", "修复 review finding", [], [])
        self.complete_default_checklist(feature)
        review_dir = feature / "evidence" / "reviews" / "round-01"
        review_dir.mkdir(parents=True)
        (review_dir / "round-01.md").write_text("P1: 未处理", encoding="utf-8")

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("review loop 已触发但未完成 pass/waiver/manual_review", result.messages)

    def test_accept_allows_waived_review_findings(self):
        feature = create_feature(self.repo, "已豁免 review", "standard", "修复 review finding", [], [])
        self.complete_default_checklist(feature)
        self.write_review_round(feature)
        (feature / "review-findings.yaml").write_text(
            """review_loop_status: pass
rounds: []
findings:
  - priority: P1
    file: runtime/devflow_cli.py
    line: 1
    summary: "accept 未阻断 review finding"
    decision: waived
waivers:
  - finding_summary: "accept 未阻断 review finding"
    summary: "已人工确认不适用"
manual_review: []
tooling_blocked: false
""",
            encoding="utf-8",
        )

        result = accept_feature(feature)

        self.assertTrue(result.ok)

    def test_accept_allows_top_level_manual_review_resolution(self):
        feature = create_feature(self.repo, "人工 review", "standard", "修复 review finding", [], [])
        self.complete_default_checklist(feature)
        (feature / "review-findings.yaml").write_text(
            """review_loop_status: tooling_blocked
rounds: []
findings:
  - priority: P1
    file: runtime/devflow_cli.py
    line: 1
    summary: "accept 未阻断 review finding"
    status: open
waivers: []
manual_review:
  - finding_summary: "accept 未阻断 review finding"
    summary: "已人工复核并确认不阻断归档"
tooling_blocked: true
""",
            encoding="utf-8",
        )

        result = accept_feature(feature)

        self.assertTrue(result.ok)

    def test_accept_does_not_apply_unrelated_waiver_to_open_p1(self):
        feature = create_feature(self.repo, "无关 waiver", "standard", "修复 review finding", [], [])
        self.complete_default_checklist(feature)
        self.write_review_round(feature)
        (feature / "review-findings.yaml").write_text(
            """review_loop_status: pass
rounds: []
findings:
  - priority: P2
    summary: "已豁免的 P2"
    status: open
  - priority: P1
    summary: "仍未处理的 P1"
    status: open
waivers:
  - finding_summary: "已豁免的 P2"
    summary: "P2 不阻断"
manual_review: []
tooling_blocked: false
""",
            encoding="utf-8",
        )

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("review-findings.yaml 存在未处理 P0/P1", result.messages)

    def test_accept_does_not_apply_source_path_waiver_to_all_findings(self):
        feature = create_feature(self.repo, "source path waiver", "standard", "修复 review finding", [], [])
        self.complete_default_checklist(feature)
        self.write_review_round(feature)
        (feature / "review-findings.yaml").write_text(
            """review_loop_status: pass
rounds: []
findings:
  - priority: P1
    source_path: evidence/reviews/round-01/round-01.md
    summary: "已豁免的 P1"
    status: open
  - priority: P1
    source_path: evidence/reviews/round-01/round-01.md
    summary: "仍未处理的 P1"
    status: open
waivers:
  - source_path: evidence/reviews/round-01/round-01.md
    finding_summary: "已豁免的 P1"
    summary: "只豁免第一条"
manual_review: []
tooling_blocked: false
""",
            encoding="utf-8",
        )

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("review-findings.yaml 存在未处理 P0/P1", result.messages)

    def test_accept_blocks_pass_review_status_without_round_evidence(self):
        feature = create_feature(self.repo, "缺 review 证据", "standard", "修复 review finding", [], [])
        self.complete_default_checklist(feature)
        (feature / "review-findings.yaml").write_text(
            """review_loop_status: pass
rounds: []
findings: []
waivers: []
manual_review: []
tooling_blocked: false
""",
            encoding="utf-8",
        )

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("review loop pass 缺少 evidence/reviews 轮次证据", result.messages)

    def test_accept_blocks_pass_review_status_with_only_empty_round_dir(self):
        feature = create_feature(self.repo, "空 review 目录", "standard", "修复 review finding", [], [])
        self.complete_default_checklist(feature)
        (feature / "evidence" / "reviews" / "round-01").mkdir(parents=True)
        (feature / "review-findings.yaml").write_text(
            """review_loop_status: pass
rounds: []
findings: []
waivers: []
manual_review: []
tooling_blocked: false
""",
            encoding="utf-8",
        )

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("review loop pass 缺少 evidence/reviews 轮次证据", result.messages)

    def test_accept_blocks_tooling_blocked_review_loop(self):
        feature = create_feature(self.repo, "review 工具阻断", "standard", "修复 review finding", [], [])
        self.complete_default_checklist(feature)
        (feature / "review-findings.yaml").write_text(
            """review_loop_status: tooling_blocked
rounds: []
findings: []
waivers: []
manual_review: []
tooling_blocked: true
""",
            encoding="utf-8",
        )

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("review loop 未通过或工具阻断", result.messages)

    def test_accept_does_not_treat_description_status_as_open_issue(self):
        feature = create_feature(self.repo, "描述包含 status", "standard", "修复 UAT", [], [])
        self.complete_default_checklist(feature)
        (feature / "issues.yaml").write_text(
            """issues:
  - id: UAT-001
    title: "描述包含状态"
    severity: medium
    status: closed
    description: "复现日志包含 status: open 字样"
""",
            encoding="utf-8",
        )

        result = accept_feature(feature)

        self.assertTrue(result.ok)

    def test_accept_warns_empty_validation_for_standard_lane(self):
        feature = create_feature(self.repo, "空验证", "standard", "局部修复", [], [])
        self.complete_default_checklist(feature)

        result = accept_feature(feature)

        self.assertTrue(result.ok)
        self.assertIn("validation.md 仍是初始模板", result.warnings)

    def test_accept_blocks_string_evidence_without_manifest(self):
        feature = create_feature(self.repo, "字符串证据", "high-risk", "改状态机", [], [])
        recommend_gates(feature, surfaces=["state-machine"])
        self.complete_default_checklist(feature)
        update_state(
            feature,
            status="validated",
            red_evidence="已新增失败样本并确认失败",
            validation_evidence="state-machine-regression 已通过",
        )

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("缺少机器生成的门禁证据", result.messages)

    def test_accept_blocks_high_risk_without_coverage_matrix_closure(self):
        feature = create_feature(self.repo, "高风险矩阵未闭环", "high-risk", "改状态机", [], [])
        recommend_gates(feature, surfaces=["state-machine"])
        self.complete_default_checklist(feature)
        update_state(feature, status="validated", red_evidence="已确认 state-machine-regression 的 RED 样本")
        (feature / "evidence").mkdir()
        (feature / "evidence" / "manifest.json").write_text(
            json.dumps(
                {"gates": [{"gate_id": "state-machine-regression", "status": "passed"}]},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        result = accept_feature(feature)

        self.assertFalse(result.ok)
        self.assertIn("高风险能力缺少 Capability Coverage Matrix 闭环证据", result.messages)

    def test_run_gate_records_evidence_and_accept_archives_feature(self):
        feature = create_feature(self.repo, "高风险有门禁", "high-risk", "改状态机", [], [])
        recommend_gates(feature, surfaces=["state-machine"])
        self.complete_default_checklist(feature)
        update_state(feature, status="validated", red_evidence="已确认 state-machine-regression 的 RED 样本")
        self.mark_coverage_matrix_checked(feature)
        self.replace_gate_command(feature, "state-machine-regression", "uv --version")

        evidence = run_gate(feature, "state-machine-regression")
        result = accept_feature(feature)

        self.assertEqual("passed", evidence.status)
        self.assertTrue(result.ok)
        self.assertFalse(feature.exists())
        self.assertTrue((self.repo / "devflow/archive" / feature.name).exists())

    def test_run_gate_rejects_shell_control_tokens(self):
        feature = create_feature(self.repo, "拒绝 shell 控制符", "high-risk", "改状态机", [], [])
        self.replace_gate_command(feature, "state-machine-regression", "uv --version && touch pwned")

        with self.assertRaisesRegex(ValueError, "缺少可执行 command"):
            run_gate(feature, "state-machine-regression")
        self.assertFalse((self.repo / "pwned").exists())

    def test_compact_issues_keeps_history_ref_and_next_id(self):
        feature = create_feature(self.repo, "压缩 UAT issue", "standard", "闭环 UAT", [], [])
        long_history = "\n".join(f"      - step: {index}" for index in range(55))
        (feature / "issues.yaml").write_text(
            f"""issues:
  - id: UAT-001
    title: "旧失败面"
    severity: high
    status: closed
    description: "已关闭但历史很长"
    investigation:
{long_history}
  - id: UAT-010
    title: "当前失败面"
    severity: medium
    status: open
    description: "仍需处理"
""",
            encoding="utf-8",
        )

        result = compact_issues(feature)
        issue = add_uat_issue(feature, "新失败面", "复测发现新的问题", severity="medium")
        issues = (feature / "issues.yaml").read_text(encoding="utf-8")

        self.assertEqual(1, result.compacted_count)
        self.assertIsNotNone(result.history_path)
        self.assertIn("history_ref:", issues)
        self.assertNotIn("已关闭但历史很长", issues)
        self.assertNotIn("step: 54", issues)
        self.assertEqual("UAT-011", issue.issue_id)

    def test_compact_issues_archives_closed_review_issue(self):
        feature = create_feature(self.repo, "压缩 review 历史", "standard", "闭环 UAT", [], [])
        (feature / "issues.yaml").write_text(
            """issues:
  - id: REVIEW-001
    title: "旧 review finding"
    severity: medium
    status: closed
    description: "review 流水账不应留在活跃 UAT 视图"
    validation:
      - command: "uv run pytest"
  - id: UAT-001
    title: "当前失败面"
    severity: high
    status: open
    description: "仍需处理"
""",
            encoding="utf-8",
        )

        result = compact_issues(feature)
        issues = (feature / "issues.yaml").read_text(encoding="utf-8")
        history = result.history_path.read_text(encoding="utf-8") if result.history_path else ""

        self.assertEqual(1, result.compacted_count)
        self.assertIn("  - id: REVIEW-001", issues)
        self.assertIn("history_ref:", issues)
        self.assertNotIn("review 流水账", issues)
        self.assertIn("review 流水账", history)
        self.assertIn("  - id: UAT-001", issues)
        self.assertIn("仍需处理", issues)

    def test_compact_issues_next_id_reads_active_and_history(self):
        feature = create_feature(self.repo, "历史 id 去重", "standard", "闭环 UAT", [], [])
        (feature / "issues.yaml").write_text(
            """issues:
  - id: UAT-001
    title: "旧失败面"
    severity: high
    status: closed
    description: "已关闭"
  - id: UAT-002
    title: "当前失败面"
    severity: medium
    status: open
    description: "仍需处理"
""",
            encoding="utf-8",
        )

        compact_issues(feature)
        issue = add_uat_issue(feature, "新失败面", "新问题", severity="low")

        self.assertEqual("UAT-003", issue.issue_id)
        self.assertEqual([1, 2, 3], existing_uat_issue_ids(feature))

    def test_compact_issues_is_idempotent_for_existing_history_ref(self):
        feature = create_feature(self.repo, "重复压缩", "standard", "闭环 UAT", [], [])
        (feature / "evidence").mkdir()
        history = feature / "evidence" / "uat-001-full-history.yaml"
        history.write_text(
            """issues:
  - id: UAT-001
    title: "旧失败面"
    status: closed
    investigation:
      - step: preserved
""",
            encoding="utf-8",
        )
        (feature / "issues.yaml").write_text(
            """issues:
  - id: UAT-001
    title: "旧失败面"
    severity: high
    status: closed
    history_ref: "evidence/uat-001-full-history.yaml"
""",
            encoding="utf-8",
        )

        result = compact_issues(feature)

        self.assertEqual(0, result.compacted_count)
        self.assertIsNone(result.history_path)
        self.assertIn("preserved", history.read_text(encoding="utf-8"))
        self.assertEqual(1, len(list((feature / "evidence").glob("*.yaml"))))

    def test_compact_issues_keeps_legacy_stub_with_extra_scalars(self):
        feature = create_feature(self.repo, "旧版 stub 兼容", "standard", "闭环 UAT", [], [])
        (feature / "evidence").mkdir()
        history = feature / "evidence" / "uat-001-full-history.yaml"
        history.write_text(
            """issues:
  - id: UAT-001
    title: "旧失败面"
    status: closed
    investigation:
      - step: preserved
""",
            encoding="utf-8",
        )
        (feature / "issues.yaml").write_text(
            """issues:
  - id: UAT-001
    title: "旧失败面"
    severity: high
    status: closed
    created_at: "2026-05-13 13:13:13 CST"
    description: "旧版 compact stub 保留的一层标量"
    regression_of: UAT-000
    history_ref: "evidence/uat-001-full-history.yaml"
""",
            encoding="utf-8",
        )

        result = compact_issues(feature)
        issues = (feature / "issues.yaml").read_text(encoding="utf-8")

        self.assertEqual(0, result.compacted_count)
        self.assertIsNone(result.history_path)
        self.assertIn("created_at:", issues)
        self.assertIn("description:", issues)
        self.assertIn('history_ref: "evidence/uat-001-full-history.yaml"', issues)
        self.assertEqual(1, len(list((feature / "evidence").glob("*.yaml"))))

    def test_compact_issues_recompacts_oversized_active_issue_with_history_ref(self):
        feature = create_feature(self.repo, "重开后再次压缩", "standard", "闭环 UAT", [], [])
        (feature / "evidence").mkdir()
        original_history = feature / "evidence" / "uat-001-full-history.yaml"
        original_history.write_text(
            """issues:
  - id: UAT-001
    status: closed
    investigation:
      - step: original
""",
            encoding="utf-8",
        )
        new_history = "\n".join(f"      - step: reopened-{index}" for index in range(55))
        (feature / "issues.yaml").write_text(
            f"""issues:
  - id: UAT-001
    title: "旧失败面"
    severity: high
    status: open
    history_ref: "evidence/uat-001-full-history.yaml"
    investigation:
{new_history}
""",
            encoding="utf-8",
        )

        result = compact_issues(feature)
        issues = (feature / "issues.yaml").read_text(encoding="utf-8")

        self.assertEqual(1, result.compacted_count)
        self.assertIsNotNone(result.history_path)
        self.assertIn("history_ref:", issues)
        self.assertNotIn("reopened-54", issues)
        self.assertIn("uat-001-full-history.yaml", result.history_path.read_text(encoding="utf-8"))
        self.assertIn("original", original_history.read_text(encoding="utf-8"))

    def test_compact_issues_keeps_pending_retest_issue_active(self):
        feature = create_feature(self.repo, "复测 pending 保留", "standard", "闭环 UAT", [], [])
        (feature / "issues.yaml").write_text(
            """issues:
  - id: UAT-001
    title: "刚关闭待复测"
    severity: high
    status: closed
    needs_retest: true
    description: "用户还没复测，不能压成历史 stub"
  - id: UAT-002
    title: "也待复测"
    severity: medium
    status: closed
    retest_status: pending
    description: "仍需用户确认"
""",
            encoding="utf-8",
        )

        result = compact_issues(feature)
        issues = (feature / "issues.yaml").read_text(encoding="utf-8")

        self.assertEqual(0, result.compacted_count)
        self.assertIsNone(result.history_path)
        self.assertIn("用户还没复测", issues)
        self.assertIn("仍需用户确认", issues)

    def test_failed_gate_blocks_accept(self):
        feature = create_feature(self.repo, "失败门禁", "high-risk", "改状态机", [], [])
        recommend_gates(feature, surfaces=["state-machine"])
        self.complete_default_checklist(feature)
        update_state(feature, status="validated", red_evidence="已确认 state-machine-regression 的 RED 样本")
        self.replace_gate_command(feature, "state-machine-regression", "uv --unknown-devflow-flag")

        evidence = run_gate(feature, "state-machine-regression")
        result = accept_feature(feature)

        self.assertEqual("failed", evidence.status)
        self.assertFalse(result.ok)
        self.assertIn("存在失败门禁证据", result.messages)

    def test_run_gate_rejects_placeholder_command(self):
        feature = create_feature(self.repo, "占位门禁", "high-risk", "改状态机", [], [])
        recommend_gates(feature, surfaces=["state-machine"])
        self.replace_gate_command(feature, "state-machine-regression", "TODO: 按实际命令填写")

        with self.assertRaisesRegex(ValueError, "缺少可执行 command"):
            run_gate(feature, "state-machine-regression")

    def test_infer_lane_upgrades_high_risk_surfaces(self):
        lane = infer_lane(
            requested_lane="standard",
            title="修复 Dify workflow 状态机",
            goal="涉及数据写入和登录恢复",
            surfaces=["workflow"],
            paths=["workflows/main.yml"],
        )

        self.assertEqual("high-risk", lane)

    def test_online_target_env_upgrades_to_high_risk(self):
        lane = infer_lane(
            requested_lane="standard",
            title="发布线上配置",
            goal="同步线上生效",
            target_env="online",
        )

        self.assertEqual("high-risk", lane)

    def complete_default_checklist(self, feature: Path) -> None:
        (feature / "checklist.yaml").write_text(
            """items:
  - id: DF-001
    title: "补全计划与验证门禁"
    status: done
    owner: main
    paths: []
    validation: []
""",
            encoding="utf-8",
        )

    def replace_gate_command(self, feature: Path, gate_id: str, command: str) -> None:
        registry = self.repo / "devflow" / "shared" / "gate_registry.yaml"
        lines = registry.read_text(encoding="utf-8").splitlines()
        output = []
        in_gate = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- id:"):
                in_gate = stripped == f"- id: {gate_id}"
            if in_gate and stripped.startswith("command:"):
                output.append(f'    command: "{command}"')
            else:
                output.append(line)
        registry.write_text("\n".join(output) + "\n", encoding="utf-8")

    def write_review_round(self, feature: Path) -> None:
        review_dir = feature / "evidence" / "reviews" / "round-01"
        review_dir.mkdir(parents=True)
        (review_dir / "round-01.md").write_text("review pass", encoding="utf-8")

    def mark_coverage_matrix_checked(self, feature: Path) -> None:
        path = feature / "acceptance.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace(
                "capability_coverage_matrix_checked: false",
                "capability_coverage_matrix_checked: true",
            ),
            encoding="utf-8",
        )

    def issue_fields(self, path: Path) -> dict[str, str]:
        fields: dict[str, str] = {}
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith(("title:", "description:")):
                key, value = line.split(":", 1)
                fields[key] = value.strip()
        return fields


if __name__ == "__main__":
    unittest.main()
