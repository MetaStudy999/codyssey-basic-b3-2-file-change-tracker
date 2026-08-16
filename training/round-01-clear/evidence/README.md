# B3-2 R01 — Evidence Guide

## 자동 검증

```bash
bash training/round-01-clear/environment/verify.sh
```

실제 `Result: N PASS / 0 FAIL` 결과를 저장합니다.

## 권장 REPL 시나리오

```text
INIT alice
COMMIT "root commit"
BRANCH left
BRANCH right
SWITCH left
COMMIT "add login feature"
COMMIT "fix login validation"
SWITCH right
COMMIT "add profile page"
LOG
LOG --sort-by=date
LOG --sort-by=author
PATH c000003 c000004
ANCESTORS c000003
SEARCH login
SEARCH --author=alice
```

실제 생성 hash는 실행 결과를 사용합니다.

## 확인 포인트

- branch가 commit을 복사하지 않고 pointer로 동작
- 각 commit에 hash/message/author/timestamp/parents 표시
- 기본 LOG에서 모든 parent가 child보다 앞
- date/author custom sorting
- PATH가 parent-child를 undirected로 보아 branch 사이를 연결
- ANCESTORS는 parent 방향으로만 탐색
- SEARCH가 keyword/author index 결과 반환

## 오류 Evidence

```text
COMMIT
SWITCH missing
PATH c999999 c000001
SEARCH
HELLO
```

다음 표준 오류가 상황에 맞게 나타나는지 확인합니다.

- `Invalid args`
- `Unknown branch: <name>`
- `Unknown commit: <hash>`
- `Unknown command: <name>`
- `No path`

## 금지 API 확인

`verify.sh`의 AST 검사로 Reference core에 `sorted()`, `list.sort()`, NetworkX가 없음을 확인합니다.

## CLEAR

unit test나 Reference 코드만으로 CLEAR하지 않습니다. 실제 REPL graph, PATH, SEARCH, error scenario와 설명형 Evaluation까지 확인합니다.
