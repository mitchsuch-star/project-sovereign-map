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


def run(mutations: list[dict]) -> int:
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
