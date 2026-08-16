#!/usr/bin/env bash
# B3-2 R01 verification-only helper.

set -u

PASS=0
FAIL=0
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROUND_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
REFERENCE="$ROUND_DIR/reference"

pass() { echo "[PASS] $1"; PASS=$((PASS + 1)); }
fail() { echo "[FAIL] $1"; FAIL=$((FAIL + 1)); }

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "[FAIL] Python not found"
    echo "Result: 0 PASS / 1 FAIL"
    exit 1
fi

if $PYTHON -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)'; then
    pass "Python >= 3.10"
else
    fail "Python >= 3.10 required"
fi

for file in \
  "$REFERENCE/main.py" \
  "$REFERENCE/mini_git/models.py" \
  "$REFERENCE/mini_git/algorithms.py" \
  "$REFERENCE/mini_git/repository.py" \
  "$REFERENCE/mini_git/cli.py" \
  "$REFERENCE/tests/test_mini_git.py"; do
    [ -f "$file" ] && pass "file exists: ${file#$ROUND_DIR/}" || fail "file missing: ${file#$ROUND_DIR/}"
done

if PYTHONPATH="$REFERENCE" $PYTHON -m compileall -q "$REFERENCE"; then
    pass "Python syntax compile"
else
    fail "Python syntax compile"
fi

if PYTHONPATH="$REFERENCE" $PYTHON -m unittest discover -s "$REFERENCE/tests" -p 'test_*.py' >/tmp/b3-2-tests.out 2>&1; then
    pass "Reference unit tests"
else
    fail "Reference unit tests (see /tmp/b3-2-tests.out)"
fi

if REFERENCE="$REFERENCE" $PYTHON <<'PY'
import ast
import os
import sys

root = os.path.join(os.environ["REFERENCE"], "mini_git")
violations = []
for name in os.listdir(root):
    if not name.endswith(".py"):
        continue
    path = os.path.join(root, name)
    with open(path, "r", encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "sorted":
                violations.append((name, node.lineno, "sorted()"))
            if isinstance(node.func, ast.Attribute) and node.func.attr == "sort":
                violations.append((name, node.lineno, ".sort()"))
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in ("networkx",):
                    violations.append((name, node.lineno, "graph library"))
        if isinstance(node, ast.ImportFrom) and node.module in ("networkx",):
            violations.append((name, node.lineno, "graph library"))
if violations:
    for item in violations:
        print("forbidden:", item)
    sys.exit(1)
PY
then
    pass "no sorted/list.sort/networkx in Mini Git core"
else
    fail "forbidden sort/graph library usage detected"
fi

if PYTHONPATH="$REFERENCE" $PYTHON - <<'PY'
from mini_git.cli import execute
from mini_git.repository import MiniGitRepository
r = MiniGitRepository()
checks = [
    execute(r, "INIT alice").startswith("Initialized"),
    "c000001" in execute(r, 'COMMIT "root commit"'),
    execute(r, "BRANCH feature/a").startswith("Created branch"),
    execute(r, "SWITCH feature/a").startswith("Switched"),
    "c000002" in execute(r, 'COMMIT "add feature"'),
    "c000001" in execute(r, "ANCESTORS c000002"),
]
raise SystemExit(0 if all(checks) else 1)
PY
then
    pass "basic command smoke test"
else
    fail "basic command smoke test"
fi

echo
printf 'Result: %d PASS / %d FAIL\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
