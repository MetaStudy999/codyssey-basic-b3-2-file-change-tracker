# B3-2 Mini Git Reference

## 실행

```bash
export PYTHONPATH="$PWD/training/round-01-clear/reference"
python3 training/round-01-clear/reference/main.py
```

종료: `exit`, `quit`, Ctrl+D, Ctrl+C.

## 명령

```text
INIT <user_name>
BRANCH <branch_name>
SWITCH <branch_name>
COMMIT <message>
LOG
LOG --sort-by=date
LOG --sort-by=author
PATH <commit1> <commit2>
ANCESTORS <commit_hash>
SEARCH <keyword>
SEARCH --author=<name>
```

공백이 있는 문자열은 큰따옴표로 감쌉니다.

```text
INIT "Alice Kim"
COMMIT "Add login feature"
SEARCH --author="Alice Kim"
```

## 내부 구조

```text
mini_git/
├── models.py       # Commit
├── algorithms.py   # stable merge sort / string min
├── repository.py   # DAG, branches, indexes, traversal
└── cli.py          # parser + REPL
```

## Commit DAG

Commit은 다음 필드를 가집니다.

- `hash`
- `message`
- `author`
- `timestamp`
- `parents`

Reference의 공개 CLI는 merge command가 없으므로 일반 commit은 부모 0개 또는 1개입니다. 자료구조 자체는 `parents: list[str]`로 DAG 형태를 보존합니다.

## Branch

branch는 commit을 복사하지 않고 특정 commit hash를 가리키는 pointer입니다.

```text
branches["main"] = "c000003"
head_branch = "main"
```

## LOG

기본 `LOG`는 parent-first DFS를 사용합니다. 부모를 재귀적으로 먼저 output에 추가한 뒤 자식을 추가해 모든 parent가 child보다 먼저 나오도록 합니다.

`LOG --sort-by=date|author`는 Python `sorted()`나 `list.sort()`를 사용하지 않고 직접 구현한 **stable merge sort**를 사용합니다.

- 평균: O(n log n)
- 최악: O(n log n)
- 안정 정렬: Yes

## PATH

공식 규칙대로 parent-child 연결을 **무방향 간선**으로 보고 shortest path를 찾습니다.

1. target에서 BFS distance 계산
2. source에서 distance가 1 줄어드는 이웃만 후보로 선택
3. 후보 중 hash가 사전순으로 가장 작은 것을 선택

따라서 최단경로가 여러 개라면 commit hash sequence가 사전순으로 가장 작은 경로를 반환합니다.

## ANCESTORS

지정 commit에서 `parents` 방향으로만 탐색하여 모든 조상을 중복 없이 반환합니다.

## Inverted Index

commit 생성 시 message를 공백으로 split하고 lowercase token으로 정규화합니다.

```text
keyword -> [commit_hash, ...]
author  -> [commit_hash, ...]
```

SEARCH는 모든 commit을 매번 순회하지 않고 index에서 후보 hash를 가져옵니다.

## 금지사항

- `sorted()` 금지
- `list.sort()` 금지
- graph 전용 library 사용 안 함

## 검증

```bash
bash training/round-01-clear/environment/verify.sh
```
