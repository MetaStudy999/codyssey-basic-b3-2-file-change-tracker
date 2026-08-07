# B3-2 Learning Guide - Mini Git

## 오늘의 목표

이 구현을 직접 실행하면서 다음을 자기 말로 설명할 수 있는 상태를 목표로 합니다.

1. Git commit graph가 왜 DAG인지
2. branch와 HEAD가 무엇을 가리키는지
3. 기본 LOG가 왜 위상 정렬 성격을 갖는지
4. PATH에서 BFS를 쓰는 이유
5. ANCESTORS에서 visited가 필요한 이유
6. inverted index가 전체 순회보다 왜 유리한지
7. 직접 구현한 merge sort의 복잡도와 안정성

---

## 1. Commit DAG

DAG는 **Directed Acyclic Graph(방향성 비순환 그래프)** 입니다.

이 미션의 방향은 다음처럼 이해하면 됩니다.

```text
child commit ---> parent commit
```

새 커밋은 이미 존재하는 커밋만 부모로 참조합니다. 과거 커밋이 미래 커밋을 부모로 참조하지 않기 때문에 정상 생성 흐름에서는 cycle이 생기지 않습니다.

cycle이 생기면 "어느 커밋이 먼저인가"를 결정할 수 없고, ancestor traversal이나 topological log가 종료되지 않거나 모순된 결과를 만들 수 있습니다.

코드 위치: `mini_git/repository.py::commit`, `log_topological`

---

## 2. Branch와 HEAD

이 구현에서 branch는 commit 자체가 아니라 **commit hash를 가리키는 pointer** 입니다.

```text
branches = {
    "main": "000003",
    "feature": "000002"
}

current_branch = "main"
```

`current_branch`가 Git의 HEAD 개념에 해당합니다. 새 COMMIT을 만들면 현재 branch pointer가 새 hash로 이동합니다.

```text
main -> 000002
COMMIT
main -> 000003
```

코드 위치: `MiniGitRepository.branches`, `current_branch`, `head_hash`

---

## 3. 기본 LOG와 위상 정렬 성격

Mission은 최신순이 아니라 **부모가 자식보다 먼저** 보이도록 요구합니다.

예:

```text
A <- B <- C
     \
      D
```

가능한 기본 LOG:

```text
A, B, C, D
```

또는

```text
A, B, D, C
```

둘 다 모든 parent-before-child 조건을 만족할 수 있습니다.

구현은 각 commit의 parent 수를 indegree로 보고, indegree가 0인 commit부터 처리하는 Kahn 방식의 topological traversal을 사용합니다.

시간복잡도는 commit 수 V, parent edge 수 E에 대해 O(V + E)입니다.

---

## 4. PATH와 BFS

Mission의 PATH는 parent edge 방향을 무시하고 연결을 양방향으로 봅니다.

```text
A <- B <- C

PATH C A
C -> B -> A
```

BFS(Breadth-First Search, 너비 우선 탐색)는 시작점에서 edge 수가 1인 후보, 2인 후보, 3인 후보 순서로 탐색하므로 unweighted graph의 shortest path에 적합합니다.

### 동률 규칙

최단 경로가 여러 개면 path 문자열이 사전순으로 가장 작은 것을 선택해야 합니다.

그래서 각 노드의 neighbor hash를 `merge_sort`로 사전순 처리하고 BFS queue의 순서를 결정합니다.

시간복잡도 기본값은 O(V + E)이고, 이 구현은 각 expansion의 neighbor ordering 때문에 추가 정렬 비용이 포함됩니다.

---

## 5. ANCESTORS와 visited

ANCESTORS는 parent 방향으로만 올라갑니다.

```text
A <- B <- D
 \      /
  <- C -
```

D의 ancestor는 A, B, C 입니다.

여러 경로에서 A를 다시 만날 수 있으므로 visited set이 없으면 같은 commit을 반복 처리하게 됩니다. DAG라도 중복 경로는 존재할 수 있기 때문에 visited가 필요합니다.

---

## 6. Inverted Index

전체 순회 검색은 commit이 N개면 매 검색마다 N개의 message를 확인해야 합니다.

```text
전체 순회
query -> commit1 -> commit2 -> ... -> commitN
```

역색인은 commit 생성 시 미리 token별 hash 목록을 만듭니다.

```text
"login" -> [000002, 000010, 000015]
"alice" -> [000001, 000002]
```

검색 시 query token에 해당하는 postings만 가져오므로 후보 수가 작을수록 전체 순회보다 훨씬 적은 commit만 확인합니다.

Trade-off는 commit 생성 때 index 갱신 비용과 추가 메모리가 필요하다는 점입니다.

코드 위치: `_index_commit`, `search_keyword`, `search_author`

---

## 7. 직접 구현 Merge Sort

Python의 표준 정렬 함수를 사용하지 않고 `mini_git/sorting.py`에서 stable merge sort를 구현했습니다.

동작:

```text
[4, 1, 3, 2]
   split
[4, 1] [3, 2]
   split
[4] [1] [3] [2]
   merge
[1, 4] [2, 3]
   merge
[1, 2, 3, 4]
```

특성:

| 항목 | 값 |
|---|---|
| 평균 시간 | O(n log n) |
| 최악 시간 | O(n log n) |
| 추가 공간 | O(n) |
| 안정 정렬 | Yes |

같은 key일 때 left 원소를 먼저 뽑기 때문에 안정성이 유지됩니다.

---

## 8. 데이터가 10배 늘어나면?

평가용 설명 포인트:

- Commit lookup: dict이므로 평균 O(1) 유지
- keyword/author search: postings가 너무 커지는 인기 token은 병목 가능
- 기본 LOG: O(V + E), commit 수에 비례해 증가
- PATH: BFS가 최악의 경우 graph 대부분을 탐색
- `PATH` neighbor sorting은 degree가 큰 node에서 추가 비용 발생
- 모든 상태가 메모리에 있으므로 매우 큰 history에서는 persistence / paging / compressed index가 필요할 수 있음

이 미션에서는 persistence가 공식 필수가 아니므로 구현하지 않습니다.

---

## 9. 요구사항이 바뀐다면?

### PATH를 부모 방향만 허용

현재 `_neighbors()`는 parents + children을 반환합니다. 부모 방향만 허용하려면 parents만 반환하도록 PATH 전용 neighbor 정책을 바꾸면 됩니다. 그러면 descendant 방향으로는 이동할 수 없어 일부 기존 path가 `No path`가 됩니다.

### `LOG --sort-by=author`도 parent-before-child를 유지

단순 author 정렬만으로는 dependency가 깨질 수 있습니다. 이 경우 ready queue에 들어온 commit들 중 author 기준 우선순위를 적용하는 **priority-aware topological ordering**이 필요합니다. 표준 정렬 API가 금지되어 있으므로 ready 후보 선택도 직접 구현해야 합니다.

### hash를 난수 기반으로 변경

- 장점: 실제 Git hash처럼 생성 순서를 직접 드러내지 않음
- 단점: 테스트 재현성이 낮아질 수 있음
- 카운터 기반은 deterministic해서 디버깅과 tie-break 테스트가 쉽습니다.

---

## 10. 직접 실행 학습 순서

```text
INIT "Alice"
COMMIT "Initial commit"
BRANCH feature
COMMIT "Main work"
SWITCH feature
COMMIT "Feature work"
LOG
PATH 000001 000003
ANCESTORS 000003
SEARCH feature
SEARCH --author=Alice
LOG --sort-by=author
quit
```

각 명령 후 다음을 말로 설명해 보세요.

- 어떤 dictionary/list/index가 바뀌었는가?
- branch pointer는 어디로 이동했는가?
- graph edge는 무엇이 추가되었는가?
- 검색은 전체 commit을 훑었는가, postings에서 시작했는가?

이 네 질문에 코드 위치를 근거로 답할 수 있으면 미션의 핵심 학습 목표에 도달한 것입니다.
