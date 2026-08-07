# AGENTS.md - B3-2 Mini Git

## Role

This repository is the isolated B3-2 Mission Workcell. Keep changes inside this repository and the active Mission branch.

## Source of Truth

1. `b3-2-mission.pdf`
2. `b3-2-mission.md`
3. `b3-2-evaluation.md` only as an `UNVERIFIED` review checklist; it must not add official requirements
4. `MISSION-WORK-PACKET.md`
5. README / learning docs
6. code
7. tests
8. actual evidence

The frozen Control Tower baseline is `0d1581b3e82366988f57e1d76da311c028b8e15e` and is READ ONLY for this Workcell.

## Scope

Required scope:

- case-insensitive Mini Git REPL
- Commit DAG / branch pointer / HEAD
- unique session hashes and hash lookup
- keyword/author inverted indexes
- custom sorting
- LOG / PATH / ANCESTORS / SEARCH
- required error paths
- automated tests, runtime evidence, learning guide

Out of required scope:

- file-content tracking
- network communication
- persistence
- bonus diff
- bonus merge CLI
- sorting-performance benchmark

## Hard Constraints

- Python 3.10+
- no graph-specific third-party library
- do not call Python standard sorting APIs such as `sorted()` or `list.sort()` in program code
- do not invent requirements from the unverified Evaluation file
- do not claim expected output as actual evidence
- do not expose credentials or secrets
- do not redesign the project beyond the minimal Mission scope

## Review Focus

Report only findings that can affect Mission completion:

- BLOCKER
- MAJOR
- confirmed requirement omission
- test failure
- false PASS / false evidence
- secret exposure

Do not request cosmetic refactors, enterprise architecture, bonus features, or unrelated hardening.

## Test Commands

```bash
python -m compileall -q main.py mini_git tests
python -m unittest discover -s tests -v
```

Representative runtime:

```bash
python main.py
```

## Status Definitions

- TODO: not implemented/run
- IMPLEMENTED: code exists, execution not yet verified
- TESTED: reliable automated test passed
- PASS: implementation + actual verification + required evidence complete
- NEEDS-RUNTIME: external/user runtime still required
- BLOCKED: external dependency prevents progress

## Stop Condition

Stop review when confirmed Mission requirements are satisfied, required tests and runtime/evidence pass, and BLOCKER=0 / MAJOR=0. Optional improvements go to backlog and must not delay merge.
