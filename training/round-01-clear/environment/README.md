# B3-2 R01 Environment

## Golden Path

- Python 3.10+
- 외부 그래프 라이브러리 없음
- Reference 실행: `python3 training/round-01-clear/reference/main.py`
- `sorted()` / `list.sort()` 사용 금지
- 정렬은 직접 구현 stable merge sort 사용

## 실행

```bash
export PYTHONPATH="$PWD/training/round-01-clear/reference"
python3 training/round-01-clear/reference/main.py
```

## 검증

```bash
bash training/round-01-clear/environment/verify.sh
```

verify는 Python 문법, unit tests, 금지 정렬 API/그래프 라이브러리, 기본 CLI smoke를 검사하도록 설계합니다. 실제 REPL 시나리오와 설명형 평가는 Phase C에서 별도로 확인합니다.
