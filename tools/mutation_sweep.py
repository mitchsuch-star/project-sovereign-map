"""Mutation sweep harness — row PT acceptance rule 3.

    "Every new test must fail when its production line is reverted.
     Report the sweep count and any inert pin found."

Reads a JSON list of mutations::

    [{"file": "backend/...py",
      "old": "<exact source substring>",
      "new": "<the reverted/broken form>",
      "tests": "tests/test_x.py::TestY",
      "id": "PT-A1 subtractive"}]

For each: apply the mutation, run the named tests, restore the file, and
report KILLED (tests failed -> the pin binds) or **INERT** (tests still
passed -> the pin proves nothing and must be replaced).

Usage:
    python -m tools.mutation_sweep tools/_sweep_pt_a.json
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")


def _baseline_green(mutations: list[dict]) -> bool:
    """Every named test target must PASS before a single mutation is applied.

    Added Aug 23, 2026 (UX23-B), because the harness had been reporting a
    false clean sweep. A test file with a SYNTAX ERROR does not collect, pytest
    exits non-zero, and this harness reads non-zero as "the pin bound the
    mutation" — so a broken test file makes every mutation report KILLED. That
    is the most dangerous possible failure mode for an instrument whose whole
    job is telling you your pins are real: it reports perfect health precisely
    when it is blind. Measured: 30 of 30 "killed" against a file that could not
    be imported.
    """
    targets = sorted({m["tests"] for m in mutations if m.get("tests")})
    for target in targets:
        proc = subprocess.run(
            [PY, "-m", "pytest", *target.split(), "-q", "--tb=line",
             "-p", "no:randomly"],
            cwd=ROOT, capture_output=True, text=True, timeout=900)
        if proc.returncode != 0:
            print("!! BASELINE NOT GREEN — refusing to sweep.")
            print(f"   {target} fails BEFORE any mutation is applied, so every")
            print("   mutation would report KILLED and the sweep would be a lie.")
            print((proc.stdout or "")[-1500:])
            return False
    return True


def run(mutations: list[dict]) -> int:
    if not _baseline_green(mutations):
        return 2
    killed, inert, broken = [], [], []
    for i, m in enumerate(mutations, 1):
        path = ROOT / m["file"]
        original = path.read_text(encoding="utf-8")
        if m["old"] not in original:
            broken.append(m.get("id", m["file"]))
            print(f"[{i:2}] !! ANCHOR NOT FOUND — {m.get('id')}")
            continue
        if original.count(m["old"]) != 1:
            broken.append(m.get("id", m["file"]))
            print(f"[{i:2}] !! ANCHOR NOT UNIQUE ({original.count(m['old'])}) "
                  f"— {m.get('id')}")
            continue
        path.write_text(original.replace(m["old"], m["new"]), encoding="utf-8")
        try:
            proc = subprocess.run(
                [PY, "-m", "pytest", *m["tests"].split(), "-q", "--tb=no",
                 "-p", "no:randomly"],
                cwd=ROOT, capture_output=True, text=True, timeout=900)
        finally:
            path.write_text(original, encoding="utf-8")
        if proc.returncode != 0:
            killed.append(m.get("id"))
            print(f"[{i:2}] KILLED   {m.get('id')}")
        else:
            inert.append(m.get("id"))
            print(f"[{i:2}] ** INERT ** {m.get('id')}  <-- pin proves nothing")

    print(f"\nswept {len(mutations)}: {len(killed)} killed, "
          f"{len(inert)} INERT, {len(broken)} anchor-failures")
    if inert:
        print("INERT PINS:")
        for name in inert:
            print(f"  - {name}")
    return 1 if (inert or broken) else 0


if __name__ == "__main__":
    payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    sys.exit(run(payload))
