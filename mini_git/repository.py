"""In-memory Mini Git repository, indexes, and graph algorithms."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from datetime import datetime, timezone

from .models import Commit
from .sorting import merge_sort


class MiniGitError(Exception):
    """Base exception for user-facing Mini Git errors."""


class MiniGitRepository:
    """Store commits, branch pointers, indexes, and graph operations in memory."""

    def __init__(self, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._reset_state()

    def _reset_state(self) -> None:
        self.commits: dict[str, Commit] = {}
        self.commit_order: list[str] = []
        self.branches: dict[str, str | None] = {}
        self.current_branch: str | None = None
        self.current_user: str | None = None
        self.keyword_index: dict[str, list[str]] = {}
        self.author_index: dict[str, list[str]] = {}
        self.children: dict[str, list[str]] = {}
        self._counter = 0

    @property
    def initialized(self) -> bool:
        """Return whether INIT has established repository state."""

        return self.current_branch is not None and self.current_user is not None

    @property
    def head_hash(self) -> str | None:
        """Return the commit hash referenced by the current branch."""

        if self.current_branch is None:
            return None
        return self.branches[self.current_branch]

    def init(self, user_name: str) -> None:
        """Reset the session, create main, set HEAD to main, and set the author."""

        if not user_name:
            raise MiniGitError("Invalid args")
        self._reset_state()
        self.current_user = user_name
        self.current_branch = "main"
        self.branches["main"] = None

    def create_branch(self, branch_name: str) -> None:
        """Create a branch pointer at the current HEAD commit."""

        self._require_initialized()
        if not branch_name:
            raise MiniGitError("Invalid args")
        if branch_name in self.branches:
            raise MiniGitError(f"Branch already exists: {branch_name}")
        self.branches[branch_name] = self.head_hash

    def switch_branch(self, branch_name: str) -> None:
        """Move HEAD to an existing branch name."""

        self._require_initialized()
        if branch_name not in self.branches:
            raise MiniGitError(f"Unknown branch: {branch_name}")
        self.current_branch = branch_name

    def commit(
        self,
        message: str,
        *,
        parents: tuple[str, ...] | None = None,
        timestamp: datetime | None = None,
    ) -> Commit:
        """Create a commit and atomically update branch and inverted indexes.

        ``parents`` is optional for tests and future merge-style extension. The
        required CLI path leaves it unset, so the current branch HEAD becomes
        the single parent when one exists.
        """

        self._require_initialized()
        if not message:
            raise MiniGitError("Invalid args")

        if parents is None:
            head = self.head_hash
            parents = (head,) if head is not None else ()

        for parent_hash in parents:
            self._require_commit(parent_hash)

        commit_hash = self._next_hash()
        commit = Commit(
            hash=commit_hash,
            message=message,
            author=self.current_user or "",
            timestamp=timestamp or self._clock(),
            parents=parents,
        )

        self.commits[commit_hash] = commit
        self.commit_order.append(commit_hash)
        self.children[commit_hash] = []
        for parent_hash in parents:
            self.children[parent_hash].append(commit_hash)

        if self.current_branch is None:
            raise MiniGitError("Repository not initialized")
        self.branches[self.current_branch] = commit_hash
        self._index_commit(commit)
        return commit

    def log_topological(self) -> list[Commit]:
        """Return all commits with every parent before each child.

        This is a Kahn-style topological traversal. Ready nodes and child lists
        preserve insertion order, so output is deterministic without relying on
        standard sorting helpers.
        """

        self._require_initialized()
        indegree: dict[str, int] = {}
        for commit_hash in self.commit_order:
            indegree[commit_hash] = len(self.commits[commit_hash].parents)

        ready: deque[str] = deque()
        for commit_hash in self.commit_order:
            if indegree[commit_hash] == 0:
                ready.append(commit_hash)

        result: list[Commit] = []
        visited_count = 0
        while ready:
            commit_hash = ready.popleft()
            result.append(self.commits[commit_hash])
            visited_count += 1
            for child_hash in self.children.get(commit_hash, []):
                indegree[child_hash] -= 1
                if indegree[child_hash] == 0:
                    ready.append(child_hash)

        if visited_count != len(self.commits):
            raise MiniGitError("Commit graph contains a cycle")
        return result

    def log_sorted(self, sort_by: str) -> list[Commit]:
        """Return commits ordered by date or author via the custom merge sort."""

        self._require_initialized()
        commits = [self.commits[commit_hash] for commit_hash in self.commit_order]
        if sort_by == "date":
            return merge_sort(commits, key=lambda item: item.timestamp)
        if sort_by == "author":
            return merge_sort(commits, key=lambda item: item.author.casefold())
        raise MiniGitError("Invalid args")

    def shortest_path(self, start_hash: str, end_hash: str) -> list[str] | None:
        """Return the required shortest undirected path with lexical tie-break.

        Parent relationships are treated as undirected edges. BFS guarantees
        minimum edge count. Each expansion uses the custom merge sort on
        neighboring hashes, making the first discovered equal-length path the
        lexicographically smallest ``hash1->hash2->...`` path.
        """

        self._require_commit(start_hash)
        self._require_commit(end_hash)
        if start_hash == end_hash:
            return [start_hash]

        queue: deque[list[str]] = deque([[start_hash]])
        visited = {start_hash}

        while queue:
            path = queue.popleft()
            current = path[-1]
            neighbors = self._neighbors(current)
            for neighbor in neighbors:
                if neighbor in visited:
                    continue
                next_path = path + [neighbor]
                if neighbor == end_hash:
                    return next_path
                visited.add(neighbor)
                queue.append(next_path)

        return None

    def ancestors(self, commit_hash: str) -> list[Commit]:
        """Return every reachable ancestor exactly once in creation order."""

        self._require_commit(commit_hash)
        visited: set[str] = set()
        stack = list(self.commits[commit_hash].parents)

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            for parent_hash in self.commits[current].parents:
                if parent_hash not in visited:
                    stack.append(parent_hash)

        return [self.commits[item] for item in self.commit_order if item in visited]

    def search_keyword(self, query: str) -> list[Commit]:
        """Search from inverted-index postings rather than scanning all commits.

        For a quoted multi-token query, postings are intersected first, then the
        small candidate set is checked for the literal lowercased phrase.
        """

        tokens = [token.lower() for token in query.split() if token]
        if not tokens:
            return []

        postings: list[list[str]] = []
        for token in tokens:
            hashes = self.keyword_index.get(token)
            if not hashes:
                return []
            postings.append(hashes)

        allowed_sets = [set(items) for items in postings[1:]]
        normalized_query = query.lower()
        results: list[Commit] = []
        for commit_hash in postings[0]:
            if any(commit_hash not in allowed for allowed in allowed_sets):
                continue
            commit = self.commits[commit_hash]
            if normalized_query in commit.message.lower():
                results.append(commit)
        return results

    def search_author(self, author: str) -> list[Commit]:
        """Return commits directly from the author inverted index."""

        hashes = self.author_index.get(author, [])
        return [self.commits[commit_hash] for commit_hash in hashes]

    def branch_names_at(self, commit_hash: str) -> list[str]:
        """Return branch names that currently point at ``commit_hash``."""

        result: list[str] = []
        for name, target in self.branches.items():
            if target == commit_hash:
                result.append(name)
        return result

    def _neighbors(self, commit_hash: str) -> list[str]:
        neighbors = list(self.commits[commit_hash].parents)
        neighbors.extend(self.children.get(commit_hash, []))
        return merge_sort(neighbors, key=lambda item: item)

    def _index_commit(self, commit: Commit) -> None:
        author_postings = self.author_index.setdefault(commit.author, [])
        author_postings.append(commit.hash)

        seen_tokens: set[str] = set()
        for token in commit.message.split():
            normalized = token.lower()
            if normalized in seen_tokens:
                continue
            seen_tokens.add(normalized)
            keyword_postings = self.keyword_index.setdefault(normalized, [])
            keyword_postings.append(commit.hash)

    def _next_hash(self) -> str:
        self._counter += 1
        return f"{self._counter:06x}"

    def _require_initialized(self) -> None:
        if not self.initialized:
            raise MiniGitError("Repository not initialized")

    def _require_commit(self, commit_hash: str) -> Commit:
        commit = self.commits.get(commit_hash)
        if commit is None:
            raise MiniGitError(f"Unknown commit: {commit_hash}")
        return commit
