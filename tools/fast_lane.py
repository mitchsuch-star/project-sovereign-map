"""Row FUN, FUN-1 (November 25, 2026) — the fast lane.

The tests that name what changed, run in a few minutes, so one session can hand
the user several playable builds. The full gate — the pre-commit hook's `ruff`
and the whole suite — still runs at every commit (the user's ruling of
November 20, 2026: "the gate stays, the wait goes").

    .venv/Scripts/python.exe tools/fast_lane.py              # run the selection
    .venv/Scripts/python.exe tools/fast_lane.py --list       # print it only
    .venv/Scripts/python.exe tools/fast_lane.py --with-engine  # window tests too
    .venv/Scripts/python.exe tools/fast_lane.py --base HEAD~1 [paths ...]

What it selects, for each changed file (`git diff --name-only <base>` plus
untracked files, or the paths given):
* a test file itself;
* `backend/x/y.py` → every test that names `backend.x.y` (or `backend/x/y.py`,
  or `from backend.x import y`);
* a client or tool script (`*.gd`, `tools/*.py`) → every test that names its
  file (`map_renderer_base.gd`, `dd_b_play`);
* a doc (`*.md`) → every test that names the doc's file.
Of conftest's `engine` lane, the modules that open a WINDOW or start a sandboxed
backend (they boot Godot and take minutes each) are left out unless
`--with-engine`, and the lane says which; the lane's source pins that launch
nothing stay in.

A fast HINT, not coverage: a test that reaches a module only through another
(`backend.main`'s TestClient, `importlib`) is not picked. The commit's gate is
the coverage.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from typing import Iterable, List, Optional, Sequence

REPO = pathlib.Path(__file__).resolve().parent.parent
TESTS = REPO / "tests"


def changed_files(base: str = "HEAD") -> List[str]:
    """What changed against `base`, tracked and untracked, repo-relative."""
    def _lines(*args: str) -> List[str]:
        out = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                             stdin=subprocess.DEVNULL)
        return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]
    return sorted(set(_lines("diff", "--name-only", base))
                  | set(_lines("ls-files", "--others", "--exclude-standard")))


def patterns_for(path: str) -> List[re.Pattern]:
    """The text a test must contain to be about `path`."""
    text = str(path).replace("\\", "/")
    repo = str(REPO).replace("\\", "/").rstrip("/") + "/"
    if text.lower().startswith(repo.lower()):
        text = text[len(repo):]          # an absolute path inside the repo
    p = pathlib.PurePosixPath(text)
    if p.suffix == ".py" and p.parts and p.parts[0] == "backend":
        parts = list(p.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        dotted = r"\.".join(re.escape(x) for x in parts)
        slashed = "/".join(p.parts)
        pats = [re.compile(dotted + r"\b"), re.compile(re.escape(slashed))]
        if len(parts) >= 2:
            pkg = r"\.".join(re.escape(x) for x in parts[:-1])
            pats.append(re.compile(r"from\s+" + pkg + r"\s+import\s+[^\n(]*\b"
                                   + re.escape(parts[-1]) + r"\b"))
            # a parenthesised import over several lines
            pats.append(re.compile(r"from\s+" + pkg + r"\s+import\s*\([^)]*\b"
                                   + re.escape(parts[-1]) + r"\b"))
        return pats
    if p.suffix in (".gd", ".md", ".json", ".tscn"):
        return [re.compile(re.escape(p.name))]
    if p.suffix == ".py" and p.parts and p.parts[0] == "tools":
        return [re.compile(re.escape(p.stem) + r"\b")]
    return []


def select_tests(changed: Iterable[str], tests_dir: pathlib.Path = TESTS,
                 engine_modules: Sequence[str] = (), with_engine: bool = False) -> List[str]:
    """The test FILE NAMES (sorted) the changed paths call for."""
    changed = [str(c).replace("\\", "/") for c in changed]
    picked = set()
    pats: List[re.Pattern] = []
    for c in changed:
        name = pathlib.PurePosixPath(c).name
        if c.startswith("tests/") and name.startswith("test_") and name.endswith(".py"):
            picked.add(name)
            continue
        pats.extend(patterns_for(c))
    if pats:
        for f in sorted(tests_dir.glob("test_*.py")):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if any(p.search(text) for p in pats):
                picked.add(f.name)
    if not with_engine:
        skip = {n for n in picked if n[:-3] in set(engine_modules) and _launches(tests_dir / n)}
        picked = {n for n in picked if n not in skip}
        global LAST_SKIPPED
        LAST_SKIPPED = sorted(skip)
    return sorted(n for n in picked if (tests_dir / n).is_file())


# The window or backend a module starts (conftest's own reading of the engine
# lane, `tests/test_the_engine_lanes.py`): a source pin that launches nothing
# stays in the fast lane.
_LAUNCH_MARKS = ("dd_b_play", "--windowed", "start_backend", "_start_engine_run", "Start-Process")
LAST_SKIPPED: List[str] = []


def _launches(path: pathlib.Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return True
    return any(mark in text for mark in _LAUNCH_MARKS)


def _engine_modules() -> List[str]:
    try:
        sys.path.insert(0, str(REPO))
        from tests.conftest import ENGINE_LANES   # noqa: WPS433 — read, not run
        return sorted(ENGINE_LANES.get("engine", ()))
    except Exception as exc:   # loud: without the lane, window tests would run
        print(f"[fast lane] WARNING: could not read conftest's engine lane ({exc}); "
              f"pass --with-engine knowingly or fix the import", file=sys.stderr)
        return []


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="*", help="changed paths (default: git diff + untracked)")
    ap.add_argument("--base", default="HEAD")
    ap.add_argument("--list", action="store_true", help="print the selection and stop")
    ap.add_argument("--with-engine", action="store_true", help="include the window-opening modules")
    args = ap.parse_args(argv)
    changed = args.paths or changed_files(args.base)
    tests = ["tests/" + n for n in select_tests(changed, TESTS, _engine_modules(), args.with_engine)]
    print(f"[fast lane] {len(changed)} changed file(s) -> {len(tests)} test file(s)")
    for t in tests:
        print("   ", t)
    if LAST_SKIPPED:
        print(f"[fast lane] left out (they open a window; --with-engine runs them): "
              f"{', '.join(LAST_SKIPPED)}")
    if args.list or not tests:
        return 0
    backend = [c for c in changed if c.endswith(".py") and c.startswith("backend/")
               and (REPO / c).is_file()]
    if backend:
        lint = subprocess.run([sys.executable, "-m", "ruff", "check", *backend], cwd=REPO,
                              stdin=subprocess.DEVNULL)
        if lint.returncode != 0:
            return lint.returncode
    cmd = [sys.executable, "-m", "pytest", *tests, "-q", "-p", "no:cacheprovider"]
    if len(tests) > 3:
        cmd += ["-n", "10", "--dist", "loadgroup"]
    return subprocess.run(cmd, cwd=REPO, stdin=subprocess.DEVNULL).returncode


if __name__ == "__main__":
    sys.exit(main())
