from __future__ import annotations

import re
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from mini_git.cli import MiniGitCLI
from mini_git.repository import MiniGitRepository


class SequenceClock:
    def __init__(self) -> None:
        self._seconds = 0

    def __call__(self) -> datetime:
        self._seconds += 1
        return datetime(2026, 8, 8, 0, 0, self._seconds, tzinfo=timezone.utc)


class MiniGitRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = MiniGitRepository(clock=SequenceClock())
        self.cli = MiniGitCLI(self.repo)

    def test_init_sets_main_head_and_user_and_resets_state(self) -> None:
        self.assertIn("Initialized repository", self.cli.execute('INIT "Alice Kim"'))
        first = self.repo.commit("first")
        self.assertEqual("main", self.repo.current_branch)
        self.assertEqual("Alice Kim", self.repo.current_user)
        self.assertEqual(first.hash, self.repo.head_hash)

        self.cli.execute('init "Bob Lee"')
        self.assertEqual("main", self.repo.current_branch)
        self.assertEqual("Bob Lee", self.repo.current_user)
        self.assertIsNone(self.repo.head_hash)
        self.assertEqual({}, self.repo.commits)

    def test_branch_switch_and_commit_update_only_current_branch(self) -> None:
        self.cli.execute('INIT "Alice"')
        root = self.repo.commit("root")
        self.cli.execute("BRANCH feature")
        self.cli.execute("SWITCH feature")
        feature_commit = self.repo.commit("feature work")

        self.assertEqual(feature_commit.hash, self.repo.branches["feature"])
        self.assertEqual(root.hash, self.repo.branches["main"])
        self.assertEqual((root.hash,), feature_commit.parents)

    def test_unknown_branch_and_invalid_args_are_concise(self) -> None:
        self.cli.execute("INIT Alice")
        self.assertEqual("Unknown branch: missing", self.cli.execute("SWITCH missing"))
        self.assertEqual("Invalid args", self.cli.execute("PATH only-one"))
        self.assertEqual("Invalid args", self.cli.execute('COMMIT "unterminated'))

    def test_hashes_are_unique_and_parent_links_follow_head(self) -> None:
        self.repo.init("Alice")
        first = self.repo.commit("first")
        second = self.repo.commit("second")
        third = self.repo.commit("third")
        self.assertEqual(3, len({first.hash, second.hash, third.hash}))
        self.assertEqual((), first.parents)
        self.assertEqual((first.hash,), second.parents)
        self.assertEqual((second.hash,), third.parents)

    def test_log_places_every_parent_before_child(self) -> None:
        self.repo.init("Alice")
        root = self.repo.commit("root")
        self.repo.create_branch("feature")
        main_commit = self.repo.commit("main")
        self.repo.switch_branch("feature")
        feature_commit = self.repo.commit("feature")
        merge_like = self.repo.commit("join", parents=(main_commit.hash, feature_commit.hash))

        hashes = [item.hash for item in self.repo.log_topological()]
        positions = {value: index for index, value in enumerate(hashes)}
        for item in self.repo.commits.values():
            for parent in item.parents:
                self.assertLess(positions[parent], positions[item.hash])
        self.assertLess(positions[root.hash], positions[merge_like.hash])

    def test_custom_date_and_author_sort(self) -> None:
        self.repo.init("Zoe")
        c1 = self.repo.commit("one")
        self.repo.current_user = "Alice"
        c2 = self.repo.commit("two")
        self.repo.current_user = "Mina"
        c3 = self.repo.commit("three")

        self.assertEqual([c1.hash, c2.hash, c3.hash], [c.hash for c in self.repo.log_sorted("date")])
        self.assertEqual([c2.hash, c3.hash, c1.hash], [c.hash for c in self.repo.log_sorted("author")])

    def test_shortest_path_and_lexical_tie_break(self) -> None:
        self.repo.init("Alice")
        root = self.repo.commit("root")
        self.repo.create_branch("right")
        left = self.repo.commit("left")
        self.repo.switch_branch("right")
        right = self.repo.commit("right")
        join = self.repo.commit("join", parents=(left.hash, right.hash))

        path = self.repo.shortest_path(left.hash, right.hash)
        self.assertEqual([left.hash, root.hash, right.hash], path)
        self.assertNotEqual([left.hash, join.hash, right.hash], path)

    def test_no_path_for_disconnected_roots(self) -> None:
        self.repo.init("Alice")
        self.repo.create_branch("orphan")
        left = self.repo.commit("left root")
        self.repo.switch_branch("orphan")
        right = self.repo.commit("right root")
        self.assertIsNone(self.repo.shortest_path(left.hash, right.hash))

    def test_ancestors_returns_complete_set(self) -> None:
        self.repo.init("Alice")
        root = self.repo.commit("root")
        self.repo.create_branch("feature")
        main = self.repo.commit("main")
        self.repo.switch_branch("feature")
        feature = self.repo.commit("feature")
        join = self.repo.commit("join", parents=(main.hash, feature.hash))

        ancestor_hashes = {item.hash for item in self.repo.ancestors(join.hash)}
        self.assertEqual({root.hash, main.hash, feature.hash}, ancestor_hashes)

    def test_keyword_and_author_search_use_indexed_postings(self) -> None:
        self.repo.init("Alice Kim")
        first = self.repo.commit("Add login feature")
        self.repo.current_user = "Bob"
        self.repo.commit("Fix payment")
        self.repo.current_user = "Alice Kim"
        third = self.repo.commit("Refine login tests")

        self.assertEqual([first.hash, third.hash], [c.hash for c in self.repo.search_keyword("login")])
        self.assertEqual([first.hash], [c.hash for c in self.repo.search_keyword("login feature")])
        self.assertEqual([first.hash, third.hash], [c.hash for c in self.repo.search_author("Alice Kim")])
        self.assertEqual([first.hash, third.hash], self.repo.keyword_index["login"])

    def test_case_insensitive_commands_and_quoted_arguments(self) -> None:
        self.assertIn("Current user: Alice Kim", self.cli.execute('iNiT "Alice Kim"'))
        output = self.cli.execute('cOmMiT "Add login feature"')
        self.assertIn("Add login feature", output)
        self.assertIn("Found 1 commit", self.cli.execute('sEaRcH "login feature"'))
        self.assertIn("Found 1 commit", self.cli.execute('SEARCH "--author=Alice Kim"'))

    def test_unknown_commit_error(self) -> None:
        self.repo.init("Alice")
        self.assertEqual("Unknown commit: deadbe", self.cli.execute("ANCESTORS deadbe"))


class SourceConstraintTests(unittest.TestCase):
    def test_program_does_not_call_standard_sort_apis(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        source_paths = [project_root / "main.py"] + list((project_root / "mini_git").glob("*.py"))
        forbidden = [
            re.compile(r"\bsor" + r"ted\s*\("),
            re.compile(r"\.so" + r"rt\s*\("),
        ]
        for path in source_paths:
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden:
                self.assertIsNone(pattern.search(text), f"forbidden sort API in {path}")

    def test_repl_runs_commands_and_exits(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        session = 'INIT "Alice"\nCOMMIT "Initial commit"\nLOG\nquit\n'
        completed = subprocess.run(
            [sys.executable, "main.py"],
            cwd=project_root,
            input=session,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode)
        self.assertIn("mini-git>", completed.stdout)
        self.assertIn("Initialized repository", completed.stdout)
        self.assertIn("Initial commit", completed.stdout)
        self.assertIn("commit 000001", completed.stdout)


if __name__ == "__main__":
    unittest.main()
