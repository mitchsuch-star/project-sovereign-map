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
report one of three verdicts:

    KILLED       at least one test FAILED -> an assertion caught it, the
                 pin binds.
    **INERT**    the tests still passed -> the pin proves nothing and must
                 be replaced.
    **BROKEN**   the run went red with zero failures -> every named test
                 ERRORED at collection or setup, so nothing evaluated the
                 pin. The mutation detonated the module; rewrite it.
                 (FA-92 — before Sept 2, 2026 this was reported as KILLED.)

Usage:
    python -m tools.mutation_sweep tools/_sweep_pt_a.json
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")


def _normalized(raw: bytes) -> tuple:
    """``(text with LF endings, the file's own newline)``.

    The sweep must satisfy two requirements that pull against each other:

    * **anchors are authored with ``\\n``** — 444 of the 719 committed
      mutations carry a multi-line ``old``, and 340 of the repo's Python
      files are CRLF, so matching against raw bytes would report ANCHOR NOT
      FOUND for most of the corpus;
    * **the restore must be byte-exact** — ``read_text``/``write_text`` do
      universal-newline translation, so an LF file came back CRLF and the
      ``finally`` block did not restore what it read. Measured on
      ``backend/game_logic/calendar.py``: 3,047 bytes in, 3,129 bytes out,
      all 82 newlines converted. With ``core.autocrlf=true`` that shows in
      ``git status`` with an EMPTY ``git diff`` — a state that invites the
      next reader to "fix" it with a checkout. Eight of the 75 files the
      committed sweep sets target are pure LF today, and this is the
      recorded cause of row WO slice 10's "the lever-setter matched
      LF-anchored patterns and silently set nothing once the sweep
      re-emitted the file as CRLF".

    So: normalize for MATCHING, keep the original bytes for RESTORING, and
    re-emit the mutant in the file's own ending.
    """
    text = raw.decode("utf-8")
    return text.replace("\r\n", "\n"), ("\r\n" if b"\r\n" in raw else "\n")


def _denormalized(text: str, newline: str) -> bytes:
    return text.replace("\n", newline).encode("utf-8")


def _invalidate_bytecode(path: pathlib.Path) -> None:
    """Drop every cached ``.pyc`` for ``path`` before pytest reads it again.

    Found Sept 2, 2026 while building FA-92, by driving this harness at speed
    — which is exactly what a sweep does, one subprocess after another.

    CPython (and pytest's assertion-rewritten cache beside it) validates a
    ``.pyc`` on **(source mtime in whole seconds, source size)**. A mutation
    that does not change the file's LENGTH — ``+`` for ``-``, ``>=`` for
    ``<=``, ``and`` for ``or``, a swapped pair of operands — applied inside
    the same wall-clock second as the previous run leaves both fields
    identical, so the stale bytecode is reused and **the mutation never
    reaches the interpreter**. The tests pass, and the sweep prints
    ``** INERT **`` for a pin that binds perfectly.

    That is FA-92's defect wearing the opposite face, and the more expensive
    one: a false KILLED lets a weak pin ship, a false INERT gets a GOOD test
    rewritten. Measured: the same one-mutation sweep printed KILLED and then
    INERT on consecutive invocations, with nothing changed but the clock.

    The SECOND direction is worse and is why the restore purges too: the
    poisoned bytecode survives a byte-exact restore. `_baseline_green` can
    then report "fails BEFORE any mutation is applied" on a clean tree, and
    an ordinary `pytest` — or the pre-commit hook — runs production code
    that is not on disk. 21 of the 719 committed mutations (2.9%) are in the
    vulnerable same-length class, one of them inside the sweep whose own
    record claims "56 killed, 0 inert at close".
    """
    cache = path.parent / "__pycache__"
    if not cache.is_dir():
        return
    for stale in cache.glob(path.stem + ".*.pyc"):
        try:
            stale.unlink()
        except OSError:
            pass


def _outcome_counts(report: pathlib.Path) -> dict:
    """Read a pytest ``--junitxml`` report into {failed, errored, other}.

    FA-92. The harness used to classify on ``proc.returncode != 0`` alone,
    and an exit code cannot tell a pin that BOUND from a mutation that merely
    DETONATED. Measured, three ways, on a throwaway module and test file:

      * an import-time ``raise`` in the module under test  -> rc 2,
        junit ``errors=1 failures=0`` (one synthetic case for the collection
        error);
      * a mutation that breaks a shared fixture so every test errors at
        SETUP  -> rc **1**, ``errors=2 failures=0`` — indistinguishable from
        a real kill by exit code;
      * a genuine assertion catch                          -> rc 1,
        ``failures=2 errors=0``.

    The middle case is why the exit code is not enough and why this reads the
    report instead. A ``<failure>`` is an assertion (or any exception raised
    inside the test BODY) catching the mutation; an ``<error>`` is pytest
    failing to collect, set up or tear the test down — nothing was evaluated.
    A run with NO testcases at all counts as nothing evaluated too: a
    mutation whose target is TEST source can make the named node id
    unresolvable, and pytest then exits non-zero having run zero tests.

    **BROKEN means "a human must look at this mutation", never "the pin
    failed."** The trade is deliberate and has a cost worth stating: a
    genuine kill whose only assertion sits behind a fixture that itself
    boots through the mutated code reports BROKEN, because every test then
    errors at SETUP and no assertion is reached. That shape is common here
    — 30 of the 48 distinct target test files use fixtures. Re-target the
    mutation, or move the pin below the fixture; do not "fix" it by
    counting errors as kills, which is the defect this closed.
    """
    counts = {"failed": 0, "errored": 0, "other": 0}
    if not report.exists():
        return counts
    try:
        root = ET.parse(report).getroot()
    except ET.ParseError:
        return counts
    for case in root.iter("testcase"):
        kinds = {child.tag for child in case}
        if "failure" in kinds:
            counts["failed"] += 1
        elif "error" in kinds:
            counts["errored"] += 1
        else:
            counts["other"] += 1
    return counts


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
    killed, inert, broken, detonated = [], [], [], []
    for i, m in enumerate(mutations, 1):
        path = ROOT / m["file"]
        original_bytes = path.read_bytes()
        original, newline = _normalized(original_bytes)
        if m["old"] not in original:
            broken.append(m.get("id", m["file"]))
            print(f"[{i:2}] !! ANCHOR NOT FOUND — {m.get('id')}")
            continue
        if original.count(m["old"]) != 1:
            broken.append(m.get("id", m["file"]))
            print(f"[{i:2}] !! ANCHOR NOT UNIQUE ({original.count(m['old'])}) "
                  f"— {m.get('id')}")
            continue
        path.write_bytes(_denormalized(
            original.replace(m["old"], m["new"]), newline))
        _invalidate_bytecode(path)
        with tempfile.TemporaryDirectory() as tmp:
            report = pathlib.Path(tmp) / "sweep.xml"
            try:
                proc = subprocess.run(
                    [PY, "-m", "pytest", *m["tests"].split(), "-q", "--tb=no",
                     "-p", "no:randomly", f"--junitxml={report}"],
                    cwd=ROOT, capture_output=True, text=True, timeout=900)
            finally:
                # BYTE-EXACT, from the bytes we read — not a re-encode of the
                # normalized text. See `_normalized`.
                path.write_bytes(original_bytes)
                # Symmetric with the apply: the NEXT mutation must not read
                # bytecode compiled from this one.
                _invalidate_bytecode(path)
            counts = _outcome_counts(report)
        if proc.returncode == 0:
            inert.append(m.get("id"))
            print(f"[{i:2}] ** INERT ** {m.get('id')}  <-- pin proves nothing")
        elif counts["failed"]:
            killed.append(m.get("id"))
            print(f"[{i:2}] KILLED   {m.get('id')}")
        else:
            # FA-92: the run went red without a single ASSERTION catching it.
            # Every named test errored at collection or setup, or nothing was
            # collected at all — so this mutation detonated the module and the
            # pin was never evaluated. Reporting it as a kill is the most
            # dangerous lie an assurance instrument can tell: it reports
            # perfect health exactly when it is blind.
            detonated.append(m.get("id"))
            print(f"[{i:2}] ** BROKEN ** {m.get('id')}  <-- mutation detonated "
                  f"({counts['errored']} errored, 0 failed) — no pin evaluated")

    print(f"\nswept {len(mutations)}: {len(killed)} killed, "
          f"{len(inert)} INERT, {len(detonated)} BROKEN, "
          f"{len(broken)} anchor-failures")
    if inert:
        print("INERT PINS:")
        for name in inert:
            print(f"  - {name}")
    if detonated:
        print("BROKEN MUTATIONS (rewrite these — they prove nothing):")
        for name in detonated:
            print(f"  - {name}")
    return 1 if (inert or broken or detonated) else 0


if __name__ == "__main__":
    payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    sys.exit(run(payload))
