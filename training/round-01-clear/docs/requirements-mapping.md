# B3-2 R01 — Requirement / Implementation / Verification / Evidence

| ID | Requirement | Reference Implementation | Verification | Evidence |
|---|---|---|---|---|
| R01 | INIT user + main + HEAD | `repository.py:init` | unit/smoke/REPL | terminal |
| R02 | BRANCH current HEAD pointer | `branch()` | unit/REPL | branch scenario |
| R03 | SWITCH branch | `switch()` | unit/REPL | terminal |
| R04 | COMMIT hash/message/author/time/parents | `Commit`, `commit()` | unit/REPL | LOG |
| R05 | unique commit hash | monotonic `c000001` counter | unit/REPL | LOG |
| R06 | DAG structure | parent references + cycle guard in LOG | unit/code | graph explanation |
| R07 | commit hash fast lookup | `dict[hash, Commit]` | code/unit | Q&A |
| R08 | LOG parent before child | parent-first DFS | unit/REPL | LOG output |
| R09 | `LOG --sort-by=date` | stable merge sort | unit/REPL | LOG output |
| R10 | `LOG --sort-by=author` | stable merge sort | unit/REPL | LOG output |
| R11 | no `sorted()`/`list.sort()` | custom merge sort | AST verify | verify output |
| R12 | PATH shortest undirected | BFS distance | unit/REPL | PATH output |
| R13 | shortest tie → lexicographically smallest hashes | greedy reconstruction on distance DAG | code/unit where applicable | Q&A |
| R14 | PATH invalid commit / no path | error / `No path` | CLI tests | terminal |
| R15 | ANCESTORS all parents | parent-direction traversal | unit/REPL | output |
| R16 | keyword inverted index | split/lower token → hashes | unit/REPL | SEARCH output |
| R17 | author inverted index | lowercase author → hashes | unit/REPL | SEARCH output |
| R18 | case-insensitive commands | CLI upper normalization | CLI tests | terminal |
| R19 | quoted strings | `shlex.split()` | CLI tests | terminal |
| R20 | standard errors | Invalid args / Unknown branch/commit | CLI tests | terminal |
| R21 | graph/sort concepts | `evaluation-qa.md` | user explanation | evaluator check |

## Phase C 핵심 Runtime

1. INIT → root COMMIT
2. main에서 branch 2개 생성 후 각자 commit
3. 기본 LOG에서 parent-first 확인
4. LOG date/author 확인
5. PATH로 branch 간 shortest path 확인
6. ANCESTORS 확인
7. SEARCH keyword/author 확인
8. Invalid args / Unknown branch / Unknown commit / No path 확인
9. `verify.sh` 실제 0 FAIL
