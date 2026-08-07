# codyssey-basic-b3-2-file-change-tracker

B3-2 **파일이 언제 어떻게 바뀌었는지 기록하는 작은 프로그램 만들기**의 CLI 기반 Mini Git 구현입니다.

> 이 미션은 실제 파일 내용을 버전 관리하는 Git을 복제하지 않습니다. 공식 범위에 맞춰 **커밋 메타데이터, Commit DAG, Branch pointer, 탐색, 역색인, 직접 정렬**을 구현합니다.

## 요구 환경

- Python 3.10 이상
- 외부 패키지 없음

## 실행

```bash
python main.py
```

REPL 프롬프트:

```text
mini-git>
```

종료:

```text
exit
quit
```

## 명령어

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

명령어는 대소문자를 구분하지 않습니다. 사용자명, 커밋 메시지, 검색어에 공백이 있으면 따옴표로 감쌉니다.

```text
INIT "Alice Kim"
COMMIT "Add login feature"
SEARCH "login feature"
SEARCH "--author=Alice Kim"
```

`SEARCH --author=<name>` 형식에서 작성자 이름에 공백이 있으면 전체 옵션 토큰을 따옴표로 감싸야 합니다.

## 핵심 구조

```text
main.py
mini_git/
├── models.py       # Commit dataclass
├── sorting.py      # 직접 구현한 stable merge sort
├── repository.py   # DAG, branch/HEAD, index, traversal
└── cli.py          # 명령 파싱과 REPL
tests/
└── test_mini_git.py
docs/
└── LEARNING.md
evidence/
├── test-output.txt
└── repl-transcript.txt
```

### Commit DAG

각 커밋은 다음 필드를 가집니다.

- `hash`
- `message`
- `author`
- `timestamp`
- `parents`

커밋 hash는 세션 내 증가 카운터를 6자리 16진수 문자열로 표현합니다. 예: `000001`, `000002`. 이 방식은 세션 내 유일성을 단순하게 보장하고 테스트 재현성이 높습니다.

### Branch / HEAD

- `branches`: branch name -> commit hash(또는 아직 커밋이 없으면 `None`)
- `current_branch`: 현재 HEAD가 가리키는 branch name

`COMMIT`이 성공하면 현재 branch pointer만 새 커밋으로 이동합니다.

### Inverted Index

커밋 생성 시 즉시 두 인덱스를 갱신합니다.

```text
keyword -> [commit_hash, ...]
author  -> [commit_hash, ...]
```

키워드는 Mission 기준 그대로 `message.split()` 후 `lower()`로 정규화합니다. 검색은 commit store 전체를 순회하지 않고 postings에서 후보를 가져옵니다. 여러 단어 검색은 postings 교집합으로 후보를 줄인 후 그 후보에 대해서만 phrase를 확인합니다.

### 직접 구현 정렬

`mini_git/sorting.py`의 stable merge sort를 사용합니다.

- 평균 시간복잡도: O(n log n)
- 최악 시간복잡도: O(n log n)
- 추가 공간: O(n)
- 안정 정렬: Yes

Python 표준 정렬 API는 프로그램 코드에서 호출하지 않습니다.

### LOG

기본 `LOG`는 Kahn 방식의 위상 정렬 성격으로 모든 부모가 자식보다 먼저 출력되도록 합니다.

`LOG --sort-by=date|author`는 Mission이 별도로 요구하는 정렬 결과이며, 기본 `LOG`의 부모-자식 선후 조건을 추가로 강제하지 않습니다.

### PATH

- parent edge를 무방향 edge로 취급
- BFS로 최소 간선 수 보장
- 이웃 hash를 직접 구현한 merge sort로 사전순 처리
- 따라서 같은 길이의 최단 경로가 여러 개면 `hash1->hash2->...` 문자열 기준 사전순 최소 경로를 선택

### ANCESTORS

부모 방향으로 DFS 성격의 traversal을 수행하고 visited set으로 중복을 방지합니다. 결과는 커밋 생성 순서로 표시합니다.

## 오류 예

```text
Invalid args
Unknown branch: feature-x
Unknown commit: deadbe
Repository not initialized
```

## 테스트

```bash
python -m unittest discover -s tests -v
```

테스트 범위:

- INIT / reset
- branch / switch / branch-local commit
- unique hash / parent link
- parent-before-child LOG
- custom date/author sort
- 금지된 표준 정렬 API 호출 정적 검사
- PATH shortest / No path / tie-break
- ANCESTORS
- keyword / author inverted-index search
- quoted args / case-insensitive command
- REPL subprocess
- 오류 경로

## Source 상태

G1 Source Discovery 결과는 [`MISSION-WORK-PACKET.md`](./MISSION-WORK-PACKET.md)에 기록합니다.

- Mission PDF: VALID
- Mission Markdown: PDF와 실질 요구 동일한 readable transcription
- Evaluation file: 내용은 유효하지만 공식 provenance는 UNVERIFIED
- Mode: MISSION-LED

따라서 구현 요구사항은 Mission PDF/Markdown에서 확정하고 Evaluation 문서는 추가 요구를 만드는 근거로 사용하지 않습니다.

## 문서

- [Mission](./b3-2-mission.md)
- [Evaluation candidate](./b3-2-evaluation.md)
- [Mission Work Packet](./MISSION-WORK-PACKET.md)
- [Learning Guide](./docs/LEARNING.md)

## 선택 과제

공식 보너스인 file diff, merge command, 2개 이상 정렬 알고리즘 성능 비교는 기본 완료 범위에서 제외했습니다. STOP Rule에 따라 필수 요구를 지연시키지 않습니다.
