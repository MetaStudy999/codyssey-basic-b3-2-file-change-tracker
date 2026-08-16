# B3-2 R01 — Evaluation Q&A Reference

## 1. Git commit graph가 왜 DAG인가?

commit은 과거 parent를 가리키고 새 commit은 기존 commit을 부모로 만들어집니다. 정상적인 commit 생성에서는 미래 commit을 부모로 가리키지 않으므로 방향을 따라 과거로 이동하며 cycle이 생기지 않습니다. branch는 commit 자체가 아니라 특정 commit을 가리키는 pointer입니다.

## 2. branch를 pointer로 이해하면 무엇이 달라지는가?

branch 생성은 commit 전체를 복사하는 작업이 아니라 현재 HEAD commit hash를 가리키는 새 이름을 만드는 작업입니다. SWITCH는 `head_branch`가 어떤 branch pointer를 사용할지 바꾸는 동작이고, COMMIT은 새 node를 만든 뒤 현재 branch pointer를 새 hash로 이동시킵니다.

## 3. 기본 LOG에서 부모가 자식보다 먼저 나와야 하는 이유와 구현은?

공식 미션의 학습용 LOG는 최신순이 아니라 parent-first입니다. Reference는 commit을 출력하기 전에 해당 commit의 parent를 재귀적으로 먼저 방문합니다. 이미 출력한 hash는 visited로 막고, visiting 중 같은 hash를 다시 만나면 cycle로 판단합니다.

## 4. 직접 구현 정렬 알고리즘은 무엇인가?

Reference는 stable merge sort를 사용합니다.

- 평균 시간복잡도: O(n log n)
- 최악 시간복잡도: O(n log n)
- 안정 정렬: Yes
- 추가 메모리: O(n)

`sorted()`와 `list.sort()`를 사용하지 않습니다.

## 5. 안정 정렬이란?

정렬 key가 같은 두 원소의 기존 상대 순서를 유지하는 정렬입니다. merge 과정에서 key가 같으면 왼쪽 원소를 먼저 선택하면 안정성을 유지할 수 있습니다.

## 6. PATH는 왜 BFS를 사용하는가?

공식 PATH는 parent-child 연결을 무방향 간선으로 보았을 때 간선 수가 가장 적은 경로를 요구합니다. 모든 간선 가중치가 같으므로 BFS가 source에서 각 node까지의 최단 간선 수를 구하는 표준 방법입니다.

## 7. 최단경로가 여러 개면 사전순 최소 경로를 어떻게 보장하는가?

Reference는 target에서 BFS distance를 계산합니다. source에서 target으로 이동할 때 `distance`가 정확히 1 줄어드는 이웃만 최단경로 후보입니다. 그 후보 중 commit hash가 사전순으로 가장 작은 이웃을 매 단계 선택하면 첫 번째로 달라지는 hash가 최소가 되므로 전체 hash sequence도 사전순 최소가 됩니다.

## 8. ANCESTORS와 PATH 탐색 방향은 어떻게 다른가?

- ANCESTORS: child → parents 방향만 탐색
- PATH: parent-child 연결을 무방향으로 보아 부모와 자식 모두 이웃

같은 graph라도 문제 정의에 따라 간선 방향 해석이 달라집니다.

## 9. Inverted Index는 왜 순회 검색보다 빠른가?

순회 검색은 매 SEARCH마다 모든 commit message를 검사해 O(V) 비용이 듭니다. Inverted Index는 commit 생성 시 token→hash 목록을 미리 만들고 검색 시 keyword bucket에서 후보만 바로 가져옵니다. index 구축/갱신 비용과 메모리를 추가로 쓰는 대신 반복 검색 비용을 줄입니다.

## 10. keyword token 기준은 무엇인가?

공식 최소 기준대로 commit message를 공백 기준 `split()`하고 소문자 `lower()`로 정규화합니다. 따라서 Reference keyword search는 부분 문자열 검색이 아니라 정규화된 token과 정확히 일치하는 index lookup입니다.

## 11. author index는 어떻게 동작하는가?

commit 생성 시 `author.lower()`를 key로 commit hash를 append합니다. `SEARCH --author=<name>`에서도 입력을 lowercase해 같은 bucket을 조회합니다.

## 12. hash를 증가 카운터로 만든 이유와 한계는?

미션은 세션 내 unique hash를 요구하며 실제 cryptographic Git SHA 구현을 요구하지 않습니다. `c000001`처럼 증가하는 ID는 중복을 확실히 피하고 graph 학습에 집중할 수 있습니다. 실제 Git은 content-addressed hash를 사용해 객체 내용과 식별을 연결합니다.

## 13. Commit lookup에 dict를 사용하는 것은 왜 허용되는가?

B3-2는 B3-1처럼 내장 key-value collection 금지 미션이 아닙니다. 공식 요구도 commit hash로 빠르게 찾을 수 있는 저장소 예시로 hash map을 제시합니다. Python dict를 repository index로 사용하고 핵심 학습 대상은 graph traversal, sorting, inverted index입니다.

## 14. LOG의 parent-first와 `LOG --sort-by`는 왜 다른 기준을 가질 수 있는가?

기본 LOG는 공식 학습 목적상 parent-before-child를 보장합니다. `--sort-by=date|author`는 별도의 정렬 요구로 비교 key에 따라 전체 commit을 정렬하는 기능입니다. 평가에서는 두 기능의 목적을 구분해 설명합니다.

## 15. 자료가 10만 commit으로 커지면 어디가 병목인가?

Reference `_neighbors()`는 child를 찾기 위해 commit 전체를 순회하므로 PATH 반복 탐색에서 비효율적입니다. 대규모로 확장한다면 `parent -> children` adjacency index를 별도로 유지하고, persistent storage/index를 사용하며, search index와 graph metadata도 디스크/DB 구조로 옮길 수 있습니다.
