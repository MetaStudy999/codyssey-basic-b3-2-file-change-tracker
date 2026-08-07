"""Core data models for the B3-2 Mini Git implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Commit:
    """Immutable commit metadata stored in the in-memory commit DAG."""

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: tuple[str, ...]
