# B3-2 R01 — Reference Build

## 목적

공식 Mission/Evaluation을 기준으로 **DAG 기반 commit graph + branch pointer + graph traversal + custom sorting + inverted index**를 직접 구현한 CLI Mini Git 기준본을 준비합니다.

Reference Build가 완료되어도 Phase C에서 실제 REPL/자동 검증/Evidence를 확인하기 전에는 `✅ CLEAR`로 판정하지 않습니다.

## Source of Truth

1. `b3-2-mission.pdf`
2. `b3-2-mission.md`
3. `b3-2-evaluation.md`

## Reference 설계 결정

- Python 3.10+
- 그래프 전용 라이브러리 사용 안 함
- `sorted()`, `list.sort()` 사용 안 함
- Commit hash: 세션 내 증가 카운터 기반 (`c000001`, `c000002`, ...)
- Commit repository: `dict[hash, Commit]`
- Branch pointer: `dict[branch_name, commit_hash | None]`
- `HEAD`: 현재 branch 이름을 가리킴
- Inverted Index:
  - `keyword -> commit_hash list`
  - `author -> commit_hash list`
- LOG 기본: 부모를 재귀적으로 먼저 방문하는 DFS 기반 parent-first ordering
- LOG sort: 직접 구현 stable merge sort, 평균/최악 O(n log n)
- PATH: BFS distance + 사전순 최소 next hash 선택으로 shortest path 중 lexicographically smallest path 보장
- PATH edge: parent-child를 undirected edge로 해석
- ANCESTORS: parent 방향 DFS/BFS
- CLI: `shlex.split()`으로 quoted strings, case-insensitive commands

## Reference Complete Path

1. Commit/Repository/Branch 구조
2. INIT/BRANCH/SWITCH/COMMIT
3. Inverted Index 갱신
4. LOG parent-first
5. custom stable merge sort
6. PATH shortest + lexicographic tie-break
7. ANCESTORS
8. SEARCH keyword/author
9. CLI error contract
10. tests/verify
11. Evaluation Q&A
12. Runtime Evidence
13. CLEAR

## 상태

**Reference Build 진행 중 / Mission 상태 ⬜ NOT STARTED / Runtime 미시작**
