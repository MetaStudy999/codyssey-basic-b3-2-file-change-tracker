# B3-2 Mission Work Packet

## 1. Identity

- Mission ID: `B3-2`
- Title: 파일이 언제 어떻게 바뀌었는지 기록하는 작은 프로그램 만들기
- Target Repository: `MetaStudy999/codyssey-basic-b3-2-file-change-tracker`
- Work branch: `mission/b3-2`
- Dependency: `NONE`
- Starting target-repository baseline: `42983da7400e7690b91fbeb39d23ae1c397c4166`

## 2. Control Tower Baseline

- Control Tower: `MetaStudy999/codyssey-basic`
- Frozen baseline SHA: `0d1581b3e82366988f57e1d76da311c028b8e15e`
- Active Wave: `20260808-01`
- Write boundary: this Mission repository only
- Control Tower: READ ONLY

### Baseline drift / inconsistency found

The Starter Packet names the representative Mission index as:

`docs/02-domains/03-data-structures-algorithms/b3-2-file-change-tracker.md`

That path does not exist at the frozen baseline. The actual frozen-baseline index is:

`docs/02-domains/03-data-structures-algorithms/b3-2-mini-git.md`

This is recorded as a Control-Tower documentation gap only; the Control Tower is not modified by this Workcell.

## 3. Source Inventory

| Source | Path | State | Use |
|---|---|---|---|
| Mission PDF | `b3-2-mission.pdf` | `VALID` | Highest-authority Mission source |
| Mission Markdown | `b3-2-mission.md` | `DUPLICATE` / `VALID` | Readable transcription of the PDF; no requirement-changing conflict found |
| Evaluation candidate | `b3-2-evaluation.md` | `UNVERIFIED` | Substantive local checklist, but official provenance was not independently established |
| Control Tower Mission index | frozen `.../b3-2-mini-git.md` | `VALID` | Mission identity/status summary only |
| Starter Packet | frozen `docs/00-governance/work-packets/b3-2.md` | `VALID` starter guidance | Must not override the Mission Source |

### Source validity checks

- Mission PDF is 7 pages, readable, non-empty, and matches the Mission Markdown in substantive requirements.
- Mission Markdown preserves the PDF's command set, graph/index/sorting requirements, constraints, bonus separation, and execution conditions.
- No requirement-changing PDF/Markdown conflict was found.
- `b3-2-evaluation.md` contains meaningful criteria, but no separate official Evaluation source or provenance marker was available in the accessible sources. It therefore cannot introduce new official requirements.

## 4. Source Mode / Confidence / Gaps

- Source Mode: `MISSION-LED`
- Source Confidence: `MEDIUM`
- G1 Source Gap:
  - Official Evaluation provenance remains unverified.
  - The frozen Starter Packet contains a stale/wrong representative Mission-index path.

G1 may close because the official Mission PDF is valid and sufficient to define the implementation. The unverified Evaluation file is used only as a review aid where it does not add requirements beyond the Mission.

## 5. Mission Contract

### Required result

Create one CLI-based Mini Git program that runs on Python 3.10+ and implements the required repository, branch, commit graph, traversal, search, sorting, and REPL behaviors.

### Confirmed required functionality

1. Commands are case-insensitive.
2. Quoted string arguments can contain spaces.
3. Option forms include `SEARCH --author=<name>` and `LOG --sort-by=date|author`.
4. Invalid input uses standardized concise errors such as `Invalid args`, `Unknown branch: <name>`, `Unknown commit: <hash>`.
5. Commit nodes contain `hash`, `message`, `author`, `timestamp`, `parents`.
6. Commit storage supports fast hash lookup.
7. Commit hashes are unique within a session.
8. The commit graph remains a DAG.
9. Maintain at least two inverted indexes: keyword -> commit hashes and author -> commit hashes.
10. Keyword index tokens come from whitespace split + lowercase normalization.
11. Do not use Python standard sorting APIs such as `sorted()` or `list.sort()`.
12. `INIT <user_name>` resets the repository, creates `main`, sets HEAD, and records the current author.
13. `BRANCH <name>` creates a branch at the current commit.
14. `SWITCH <name>` changes HEAD to the named branch.
15. `COMMIT <message>` creates a commit whose parent is the current branch head when one exists and updates indexes.
16. `LOG` prints parents before children and identifies hash/author/timestamp/message.
17. `LOG --sort-by=date|author` uses a directly implemented sorting algorithm.
18. `PATH <a> <b>` treats parent edges as undirected, returns a shortest path, returns `No path` when disconnected, and resolves equal-length paths by lexicographically smallest `hash1->hash2->...` string.
19. `ANCESTORS <hash>` returns all reachable ancestors.
20. `SEARCH <keyword>` and `SEARCH --author=<name>` are inverted-index based rather than full commit-store scans.
21. REPL prompt repeats until `exit` or `quit`.
22. Algorithm logic for traversal/sorting/indexing is separated into functions/classes and documented.
23. Graph-specific third-party libraries are prohibited.
24. File-content tracking, network communication, and persistence are out of required scope.
25. Required submission includes an entry point such as `main.py` and `README.md`.

### Non-scope / bonus backlog

The following are optional and will not delay completion:

- text-file `diff`
- merge command / two-parent merge commit CLI
- sorting-performance comparison with multiple algorithms

## 6. Requirement Traceability

| ID | Requirement | Primary Source |
|---|---|---|
| REQ-B3-2-001 | Case-insensitive CLI and quoted strings | Mission PDF p.2-3 / Mission MD §4.1 |
| REQ-B3-2-002 | Standard option forms and concise errors | Mission PDF p.3 / Mission MD §4.1 |
| REQ-B3-2-003 | Commit model + DAG + fast hash lookup + unique hash | Mission PDF p.3 / Mission MD §4.2 |
| REQ-B3-2-004 | keyword/author inverted indexes | Mission PDF p.3 / Mission MD §4.3 |
| REQ-B3-2-005 | No standard sorting APIs; custom comparator-capable sort | Mission PDF p.3, p.5-6 / Mission MD §4.4, §7 |
| REQ-B3-2-006 | INIT/BRANCH/SWITCH/COMMIT | Mission PDF p.3-4 / Mission MD §4.5 |
| REQ-B3-2-007 | Parent-before-child LOG | Mission PDF p.4 / Mission MD §4.5 |
| REQ-B3-2-008 | date/author sorted LOG | Mission PDF p.4 / Mission MD §4.5 |
| REQ-B3-2-009 | Undirected shortest PATH + lexicographic tie-break + No path | Mission PDF p.4 / Mission MD §4.5 |
| REQ-B3-2-010 | All ANCESTORS | Mission PDF p.4 / Mission MD §4.5 |
| REQ-B3-2-011 | Inverted-index SEARCH keyword/author | Mission PDF p.4 / Mission MD §4.5 |
| REQ-B3-2-012 | REPL and exit/quit | Mission PDF p.2 / Mission MD §2.4 |
| REQ-B3-2-013 | Python 3.10+, separated algorithm logic, docstrings | Mission PDF p.5-6 / Mission MD §6-7 |
| REQ-B3-2-014 | No file-content tracking/network; persistence not required | Mission PDF p.6 / Mission MD §7 |
| REQ-B3-2-015 | `main.py`-style entry point + README | Mission PDF p.2 / Mission MD §2.5 |

## 7. Repository Baseline

At Workcell start the repository contains only:

- `README.md`
- `b3-2-mission.md`
- `b3-2-mission.pdf`
- `b3-2-evaluation.md`

There is no implementation, test suite, data model, REPL, or evidence package yet.

Baseline status:

- Code: `TODO`
- Tests: `TODO`
- Runtime evidence: `TODO`
- Learning content: `TODO`

## 8. Minimal Sufficient Design

```text
main.py
mini_git/
  models.py       Commit model
  sorting.py      custom stable merge sort
  repository.py   commit store, branches, HEAD, indexes, graph algorithms
  cli.py          command parsing + REPL
  __init__.py
tests/
  test_mini_git.py
docs/
  LEARNING.md
evidence/
  test-output.txt
  repl-transcript.txt
```

Design rules:

- Deterministic counter-based hashes for session uniqueness and testability.
- Insertion-ordered commit store for deterministic parent-before-child traversal support.
- Custom stable merge sort reused for date/author ordering and lexical neighbor ordering.
- BFS for shortest path with custom lexical neighbor ordering to satisfy the tie-break rule.
- Ancestor traversal guarded by a visited set.
- Search candidates always originate from the inverted indexes; multi-token phrase queries intersect postings before candidate verification.

## 9. Agent Routing

- Orchestrator / Integrator: ChatGPT
- Primary Builder: ChatGPT in this Workcell because no separate Codex execution surface is available here
- Automated test harness: Python `unittest` + CLI subprocess tests + static forbidden-sort check
- Independent reviewer: one GitHub PR review pass by ChatGPT against Source/Test evidence; no second reviewer unless BLOCKER/MAJOR remains
- Human runtime: not required for this in-memory CLI because the available execution environment can run Python and the REPL end-to-end

Review budget:

- Self review: 1
- Independent review: 1
- Targeted re-test after fixes: at most 1 unless a blocking defect remains

## 10. Test Plan

- INIT creates/reset main, HEAD, user.
- Branch creation/switch and branch-local commit movement.
- Unknown branch and invalid arguments.
- Hash uniqueness and parent links.
- DAG parent-before-child LOG across branches/disconnected roots.
- Custom date/author sort and forbidden API static check.
- PATH shortest route, disconnected `No path`, and lexicographic tie-break.
- ANCESTORS complete set.
- Keyword and author SEARCH correctness and index-origin behavior.
- Multi-token/quoted search query.
- Case-insensitive commands and quoted commit/user arguments.
- REPL `exit` / `quit`.

## 11. Runtime Plan

Execute locally in a Python 3.10+ environment:

```bash
python -m unittest discover -s tests -v
python main.py
```

A scripted REPL session will be captured as actual evidence.

## 12. Evidence Plan

Required evidence will include:

- test runner output
- representative REPL transcript
- branch/commit log output
- path, ancestors, and search output
- code locations for custom sorting and inverted indexing

Expected output is not evidence; only actual executed output will be stored.

## 13. Dependency / Drift Check

- Official dependency: `NONE`
- Recommended dependency: `NONE`
- Control-Tower drift: wrong Mission-index filename in Starter Packet, documented above

## 14. Gate Checklist

- [x] G1 SOURCE - source states/mode/gaps and contract established
- [ ] G2 BUILD
- [ ] G3 TEST
- [ ] G4 REVIEW
- [ ] G5 RUNTIME
- [ ] G6 EVIDENCE
- [ ] G7 LEARN
- [ ] G8 MERGE

## 15. STOP Rule

Stop when all confirmed Mission requirements pass, required tests and runtime evidence exist, BLOCKER=0, MAJOR=0, learning material is present, and the Mission PR is merged. Bonus work must not delay completion.

## 16. Handoff Contract

At completion create:

- `HANDOFF.md`
- `mission-result.yaml`

They must record final Mission commit/merge SHA, PR, Source Mode/Confidence/Gaps, requirement status, G1-G8 status, tests, runtime/evidence, learning status, BLOCKER/MAJOR counts, and remaining bonus backlog.