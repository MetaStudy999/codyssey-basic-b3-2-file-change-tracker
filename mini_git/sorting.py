"""Sorting algorithms implemented without Python's standard sorting APIs."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K")


def merge_sort(items: Sequence[T], key: Callable[[T], K]) -> list[T]:
    """Return a stable ascending merge-sort result using ``key`` for comparison.

    Merge sort is O(n log n) in both the average and worst case. This
    implementation is stable because equal keys are taken from the left half
    first.
    """

    if len(items) <= 1:
        return list(items)

    middle = len(items) // 2
    left = merge_sort(items[:middle], key)
    right = merge_sort(items[middle:], key)
    return _merge(left, right, key)


def _merge(left: list[T], right: list[T], key: Callable[[T], K]) -> list[T]:
    """Merge two already ordered lists while preserving stability."""

    result: list[T] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if key(left[left_index]) <= key(right[right_index]):
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    while left_index < len(left):
        result.append(left[left_index])
        left_index += 1

    while right_index < len(right):
        result.append(right[right_index])
        right_index += 1

    return result
