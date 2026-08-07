"""Command parser and REPL for the B3-2 Mini Git."""

from __future__ import annotations

import shlex
from datetime import datetime

from .models import Commit
from .repository import MiniGitError, MiniGitRepository


class MiniGitCLI:
    """Translate case-insensitive CLI commands into repository operations."""

    def __init__(self, repository: MiniGitRepository | None = None) -> None:
        self.repository = repository or MiniGitRepository()

    def execute(self, line: str) -> str:
        """Execute one command line and return user-facing output text."""

        try:
            parts = shlex.split(line)
        except ValueError:
            return "Invalid args"

        if not parts:
            return ""

        command = parts[0].upper()
        try:
            if command == "INIT":
                return self._init(parts)
            if command == "BRANCH":
                return self._branch(parts)
            if command == "SWITCH":
                return self._switch(parts)
            if command == "COMMIT":
                return self._commit(parts)
            if command == "LOG":
                return self._log(parts)
            if command == "PATH":
                return self._path(parts)
            if command == "ANCESTORS":
                return self._ancestors(parts)
            if command == "SEARCH":
                return self._search(parts)
            return f"Unknown command: {parts[0]}"
        except MiniGitError as exc:
            return str(exc)

    def _init(self, parts: list[str]) -> str:
        if len(parts) != 2:
            return "Invalid args"
        self.repository.init(parts[1])
        return (
            "Initialized repository.\n"
            "Current branch: main\n"
            f"Current user: {parts[1]}"
        )

    def _branch(self, parts: list[str]) -> str:
        if len(parts) != 2:
            return "Invalid args"
        self.repository.create_branch(parts[1])
        return f"Created branch: {parts[1]}"

    def _switch(self, parts: list[str]) -> str:
        if len(parts) != 2:
            return "Invalid args"
        self.repository.switch_branch(parts[1])
        return f"Switched to branch: {parts[1]}"

    def _commit(self, parts: list[str]) -> str:
        if len(parts) != 2:
            return "Invalid args"
        commit = self.repository.commit(parts[1])
        return f"[{self.repository.current_branch} {commit.hash}] {commit.message}"

    def _log(self, parts: list[str]) -> str:
        if len(parts) == 1:
            commits = self.repository.log_topological()
        elif len(parts) == 2 and parts[1].startswith("--sort-by="):
            sort_by = parts[1].split("=", 1)[1].lower()
            commits = self.repository.log_sorted(sort_by)
        else:
            return "Invalid args"
        return self._format_commit_list(commits, empty_text="No commits")

    def _path(self, parts: list[str]) -> str:
        if len(parts) != 3:
            return "Invalid args"
        path = self.repository.shortest_path(parts[1], parts[2])
        if path is None:
            return "No path"
        return "Path: " + " -> ".join(path)

    def _ancestors(self, parts: list[str]) -> str:
        if len(parts) != 2:
            return "Invalid args"
        commits = self.repository.ancestors(parts[1])
        return self._format_commit_list(commits, empty_text="Ancestors: (none)")

    def _search(self, parts: list[str]) -> str:
        if len(parts) != 2:
            return "Invalid args"
        argument = parts[1]
        if argument.startswith("--author="):
            author = argument.split("=", 1)[1]
            if not author:
                return "Invalid args"
            commits = self.repository.search_author(author)
        else:
            commits = self.repository.search_keyword(argument)
        if not commits:
            return "Found 0 commits"
        body = "\n".join(f"- {item.hash}: {item.message}" for item in commits)
        return f"Found {len(commits)} commit(s):\n{body}"

    def _format_commit_list(self, commits: list[Commit], *, empty_text: str) -> str:
        if not commits:
            return empty_text
        blocks: list[str] = []
        for commit in commits:
            branches = self.repository.branch_names_at(commit.hash)
            branch_suffix = f" [{', '.join(branches)}]" if branches else ""
            blocks.append(
                f"commit {commit.hash} "
                f"({commit.author}, {self._format_timestamp(commit.timestamp)})"
                f"{branch_suffix}\n{commit.message}"
            )
        return "\n".join(blocks)

    @staticmethod
    def _format_timestamp(timestamp: datetime) -> str:
        return timestamp.isoformat(timespec="seconds")


def run_repl(cli: MiniGitCLI | None = None) -> None:
    """Run the interactive ``mini-git>`` prompt until exit, quit, or EOF."""

    active_cli = cli or MiniGitCLI()
    while True:
        try:
            line = input("mini-git> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if line.strip().lower() in {"exit", "quit"}:
            break

        output = active_cli.execute(line)
        if output:
            print(output)
