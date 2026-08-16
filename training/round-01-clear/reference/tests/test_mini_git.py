from __future__ import annotations

import unittest

from mini_git.algorithms import stable_merge_sort
from mini_git.cli import execute
from mini_git.models import Commit
from mini_git.repository import MiniGitError, MiniGitRepository


class RepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = MiniGitRepository()
        self.repo.init("alice")

    def test_init_branch_switch_and_commit_graph(self) -> None:
        first = self.repo.commit("Initial commit")
        self.repo.branch("feature/login")
        self.repo.switch("feature/login")
        second = self.repo.commit("Add login feature")

        self.assertEqual(first.parents, [])
        self.assertEqual(second.parents, [first.hash])
        self.assertEqual(self.repo.current_head(), second.hash)
        self.assertEqual(self.repo.branches["main"], first.hash)

    def test_parent_first_log(self) -> None:
        first = self.repo.commit("first")
        self.repo.branch("feature/a")
        self.repo.switch("feature/a")
        second = self.repo.commit("second")
        third = self.repo.commit("third")
        hashes = [commit.hash for commit in self.repo.log_parent_first()]
        self.assertLess(hashes.index(first.hash), hashes.index(second.hash))
        self.assertLess(hashes.index(second.hash), hashes.index(third.hash))

    def test_shortest_path_across_branches(self) -> None:
        root = self.repo.commit("root")
        self.repo.branch("left")
        self.repo.branch("right")

        self.repo.switch("left")
        left1 = self.repo.commit("left one")
        left2 = self.repo.commit("left two")

        self.repo.switch("right")
        right1 = self.repo.commit("right one")

        path = self.repo.path(left2.hash, right1.hash)
        self.assertEqual(path, [left2.hash, left1.hash, root.hash, right1.hash])
        self.assertEqual(self.repo.path(root.hash, root.hash), [root.hash])

    def test_ancestors(self) -> None:
        first = self.repo.commit("one")
        second = self.repo.commit("two")
        third = self.repo.commit("three")
        result = self.repo.ancestors(third.hash)
        self.assertEqual(result, [first.hash, second.hash])

    def test_inverted_index_keyword_and_author(self) -> None:
        first = self.repo.commit("Add login feature")
        second = self.repo.commit("Fix login validation")
        self.repo.commit("Document profile")

        keyword = [commit.hash for commit in self.repo.search_keyword("login")]
        author = [commit.hash for commit in self.repo.search_author("ALICE")]
        self.assertEqual(keyword, [first.hash, second.hash])
        self.assertEqual(len(author), 3)

    def test_unknown_branch_and_commit(self) -> None:
        with self.assertRaises(MiniGitError):
            self.repo.switch("missing")
        with self.assertRaises(MiniGitError):
            self.repo.path("c999999", "c888888")


class SortingTests(unittest.TestCase):
    def test_stable_merge_sort(self) -> None:
        commits = [
            Commit("c3", "m3", "bob", "2026-01-03T00:00:00+00:00", []),
            Commit("c1", "m1", "alice", "2026-01-01T00:00:00+00:00", []),
            Commit("c2", "m2", "alice", "2026-01-02T00:00:00+00:00", []),
        ]
        by_author = stable_merge_sort(commits, key=lambda commit: commit.author)
        self.assertEqual([commit.hash for commit in by_author], ["c1", "c2", "c3"])
        by_date = stable_merge_sort(commits, key=lambda commit: commit.timestamp)
        self.assertEqual([commit.hash for commit in by_date], ["c1", "c2", "c3"])


class CliTests(unittest.TestCase):
    def test_commands_and_case_insensitive_input(self) -> None:
        repo = MiniGitRepository()
        self.assertIn("Initialized", execute(repo, 'init "Alice Kim"'))
        first = execute(repo, 'commit "Add login feature"')
        self.assertIn("c000001", first)
        self.assertIn("Add login feature", execute(repo, "SEARCH login"))
        self.assertIn("Alice Kim", execute(repo, 'SEARCH --author="Alice Kim"'))
        self.assertIn("c000001", execute(repo, "LOG"))
        self.assertIn("c000001", execute(repo, "LOG --sort-by=date"))

    def test_errors(self) -> None:
        repo = MiniGitRepository()
        self.assertEqual(execute(repo, "COMMIT"), "Invalid args")
        self.assertEqual(execute(repo, "HELLO"), "Unknown command: HELLO")
        self.assertEqual(execute(repo, "INIT alice"), "Initialized repository for alice on main")
        self.assertEqual(execute(repo, "SWITCH missing"), "Unknown branch: missing")
        self.assertEqual(execute(repo, "PATH c999999 c000001"), "Unknown commit: c999999")


if __name__ == "__main__":
    unittest.main()
