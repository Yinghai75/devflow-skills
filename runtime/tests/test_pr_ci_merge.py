import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pr_ci_merge import (
    CommandResult,
    build_pr_create_command,
    parse_worktree_list,
    pull_back_main,
    wait_for_ci,
)


class PrCiMergeTest(unittest.TestCase):
    def test_parse_worktree_list_reads_branch_and_prunable(self):
        entries = parse_worktree_list(
            "\n".join(
                [
                    "worktree /repo/main",
                    "HEAD 111",
                    "branch refs/heads/main",
                    "",
                    "worktree /tmp/stale",
                    "HEAD 222",
                    "detached",
                    "prunable gitdir file points to non-existent location",
                    "",
                ]
            )
        )

        self.assertEqual(2, len(entries))
        self.assertEqual(Path("/repo/main"), entries[0].path)
        self.assertEqual("main", entries[0].branch)
        self.assertFalse(entries[0].prunable)
        self.assertTrue(entries[1].prunable)

    def test_pull_back_main_uses_existing_main_worktree(self):
        calls = []

        def fake_run(args, *, cwd, check=True, capture=True):
            if args == ["git", "worktree", "list", "--porcelain"]:
                return CommandResult(
                    stdout="\n".join(
                        [
                            "worktree /repo/main",
                            "HEAD 111",
                            "branch refs/heads/main",
                            "",
                            "worktree /repo/feature",
                            "HEAD 222",
                            "branch refs/heads/feature",
                            "",
                        ]
                    ),
                    stderr="",
                )
            if args == ["git", "status", "--short"]:
                return CommandResult(stdout="", stderr="")
            calls.append((args, cwd))
            return CommandResult(stdout="", stderr="")

        with patch("pr_ci_merge.current_branch", return_value="feature"):
            with patch("pr_ci_merge.run", side_effect=fake_run):
                pull_back_main(Path("/repo/feature"), "origin", "main")

        self.assertNotIn((["git", "checkout", "main"], Path("/repo/feature")), calls)
        self.assertIn((["git", "pull", "--ff-only", "origin", "main"], Path("/repo/main")), calls)

    def test_wait_for_ci_reports_dirty_before_check_watch(self):
        with patch(
            "pr_ci_merge.view_pr_status",
            return_value={"mergeStateStatus": "DIRTY", "statusCheckRollup": []},
        ):
            with self.assertRaises(SystemExit) as caught:
                wait_for_ci(Path("/repo"), 1, discovery_timeout=0, poll_interval=1)

        self.assertIn("merge conflict", str(caught.exception))

    def test_build_pr_create_command_defaults_to_fill(self):
        command = build_pr_create_command(
            branch="feature",
            base="main",
            draft=False,
            title=None,
            body_file=None,
        )

        self.assertEqual(["gh", "pr", "create", "--fill", "--base", "main", "--head", "feature"], command)

    def test_build_pr_create_command_accepts_title_and_body_file(self):
        command = build_pr_create_command(
            branch="feature",
            base="main",
            draft=True,
            title="修复 Sigma URL",
            body_file=Path("/tmp/pr.md"),
        )

        self.assertEqual(
            [
                "gh",
                "pr",
                "create",
                "--base",
                "main",
                "--head",
                "feature",
                "--title",
                "修复 Sigma URL",
                "--body-file",
                "/tmp/pr.md",
                "--draft",
            ],
            command,
        )


if __name__ == "__main__":
    unittest.main()
