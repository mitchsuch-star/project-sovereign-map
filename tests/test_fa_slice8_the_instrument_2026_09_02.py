"""Final Whole-Game Audit — slice 8, "The Instrument" (the reproduction half).

The memo scheduled the harness LAST. The Sept-2 verification pass moved it
FIRST, for the reason the memo's own standing rule states: every later slice
is told to reproduce its row before building it, and these are precisely the
harness defects that corrupt a reproduction.

Rows built here:

* **FA-92** (P3) — `tools/mutation_sweep.py` classified a mutation solely on
  `proc.returncode != 0`, so a mutation that DETONATED the module (every
  named test erroring at collection or setup, zero assertions evaluated) was
  printed as `KILLED`. The instrument reported perfect health exactly when it
  was blind.

Measured before building, on a throwaway module and test file, because an
exit code was the whole classification and the question is whether an exit
code can carry the distinction. It cannot:

    import-time raise in the module under test  -> rc 2, errors 1, failures 0
    a broken shared fixture (all tests ERROR)   -> rc 1, errors 2, failures 0
    a genuine assertion catch                   -> rc 1, errors 0, failures 2

The middle row is the one that matters: **rc 1 with zero failures is
byte-indistinguishable from a real kill by return code alone.**
"""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "mutation_sweep_under_test", REPO_ROOT / "tools" / "mutation_sweep.py")
sweep = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("mutation_sweep_under_test", sweep)
_spec.loader.exec_module(sweep)


MODULE_SRC = "def add(a, b):\n    return a + b\n"
TEST_SRC = (
    "from mod_under_test import add\n"
    "\n"
    "def test_add():\n"
    "    assert add(1, 2) == 3\n"
    "\n"
    "def test_add_again():\n"
    "    assert add(2, 2) == 4\n"
)


def _fixture_repo(tmp_path):
    """A two-file repo the real harness can sweep, outside the real one."""
    (tmp_path / "mod_under_test.py").write_text(MODULE_SRC, encoding="utf-8")
    (tmp_path / "test_mod_under_test.py").write_text(TEST_SRC, encoding="utf-8")
    return tmp_path


def _mutation(kind):
    base = {"file": "mod_under_test.py", "tests": "test_mod_under_test.py"}
    if kind == "killed":
        return dict(base, id="A/killed", old="return a + b", new="return a - b")
    if kind == "broken":
        # Detonates at import: the module raises before `add` is defined, so
        # the test file cannot be collected and no assertion is ever reached.
        return dict(base, id="B/broken", old="def add(a, b):",
                    new="raise RuntimeError('boom')\ndef add(a, b):")
    if kind == "inert":
        # A source change the pins cannot see. Addition commutes.
        return dict(base, id="C/inert", old="return a + b", new="return b + a")
    raise AssertionError(kind)


def _run(tmp_path, monkeypatch, mutations, capsys):
    monkeypatch.setattr(sweep, "ROOT", _fixture_repo(tmp_path))
    code = sweep.run(mutations)
    return code, capsys.readouterr().out


class TestTheSweepTellsAKillFromADetonation:
    """FA-92. The three verdicts, driven through the REAL harness."""

    def test_an_assertion_catch_is_killed(self, tmp_path, monkeypatch, capsys):
        code, out = _run(tmp_path, monkeypatch, [_mutation("killed")], capsys)
        assert "KILLED   A/killed" in out
        assert "** BROKEN **" not in out
        assert "swept 1: 1 killed, 0 INERT, 0 BROKEN" in out
        assert code == 0

    def test_a_detonating_mutation_is_broken_not_killed(
            self, tmp_path, monkeypatch, capsys):
        """The row's headline. Before FA-92 this printed `KILLED`."""
        code, out = _run(tmp_path, monkeypatch, [_mutation("broken")], capsys)
        assert "** BROKEN ** B/broken" in out
        assert "KILLED" not in out
        assert "no pin evaluated" in out
        assert code == 1, "a sweep that evaluated nothing must not exit clean"

    def test_a_surviving_mutation_is_still_inert(
            self, tmp_path, monkeypatch, capsys):
        code, out = _run(tmp_path, monkeypatch, [_mutation("inert")], capsys)
        assert "** INERT ** C/inert" in out
        assert code == 1

    def test_the_summary_line_counts_all_three(
            self, tmp_path, monkeypatch, capsys):
        code, out = _run(
            tmp_path, monkeypatch,
            [_mutation("killed"), _mutation("broken"), _mutation("inert")],
            capsys)
        assert "swept 3: 1 killed, 1 INERT, 1 BROKEN, 0 anchor-failures" in out
        assert "BROKEN MUTATIONS (rewrite these — they prove nothing):" in out
        assert code == 1


class TestTheClassifierReadsOutcomesNotExitCodes:
    """The measured reason the exit code is not enough, pinned directly.

    A mutation can make EVERY named test error at SETUP — a broken shared
    fixture, an import the tests share — and pytest exits 1, exactly as it
    does for a real assertion failure. Only the per-testcase outcomes
    separate them.
    """

    def _report(self, tmp_path, body):
        path = tmp_path / "report.xml"
        path.write_text(body, encoding="utf-8")
        return path

    def test_failures_are_counted_as_failed(self, tmp_path):
        counts = sweep._outcome_counts(self._report(tmp_path, (
            '<testsuites><testsuite name="pytest">'
            '<testcase name="a"><failure message="x"/></testcase>'
            '<testcase name="b"/></testsuite></testsuites>')))
        assert counts == {"failed": 1, "errored": 0, "other": 1}

    def test_setup_errors_are_never_counted_as_failures(self, tmp_path):
        """The case an exit code cannot see: rc 1, and nothing was evaluated."""
        counts = sweep._outcome_counts(self._report(tmp_path, (
            '<testsuites><testsuite name="pytest">'
            '<testcase name="a"><error message="setup boom"/></testcase>'
            '<testcase name="b"><error message="setup boom"/></testcase>'
            '</testsuite></testsuites>')))
        assert counts["failed"] == 0
        assert counts["errored"] == 2

    def test_a_missing_report_is_not_a_kill(self, tmp_path):
        """pytest crashed before writing anything — that is BROKEN, not KILLED."""
        assert sweep._outcome_counts(tmp_path / "absent.xml")["failed"] == 0

    def test_an_unparseable_report_is_not_a_kill(self, tmp_path):
        assert sweep._outcome_counts(
            self._report(tmp_path, "<testsuites"))["failed"] == 0

    def test_a_run_with_no_testcases_is_not_a_kill(self, tmp_path):
        """The fourth false-kill class, named by the refuter pass: a
        mutation whose target is TEST source can make the named node id
        unresolvable — pytest exits non-zero having run ZERO tests, and the
        old classifier printed KILLED. `_baseline_green` cannot catch it by
        construction, because the id resolves on the un-mutated file."""
        counts = sweep._outcome_counts(self._report(
            tmp_path, '<testsuites><testsuite name="pytest"/></testsuites>'))
        assert counts == {"failed": 0, "errored": 0, "other": 0}


class TestTheAnchorGuardsStillHold:
    """The pre-existing verdicts FA-92 must not disturb."""

    def test_a_missing_anchor_is_still_an_anchor_failure(
            self, tmp_path, monkeypatch, capsys):
        code, out = _run(tmp_path, monkeypatch, [
            {"file": "mod_under_test.py", "tests": "test_mod_under_test.py",
             "id": "D/absent", "old": "return a * b", "new": "return a - b"}],
            capsys)
        assert "ANCHOR NOT FOUND" in out
        assert code == 1

    def test_a_red_baseline_still_refuses_to_sweep(
            self, tmp_path, monkeypatch, capsys):
        """UX23-B's guard: a test file that cannot collect made EVERY
        mutation report KILLED. FA-92 closes the same hole one layer in."""
        repo = _fixture_repo(tmp_path)
        (repo / "test_mod_under_test.py").write_text(
            "import does_not_exist\n", encoding="utf-8")
        monkeypatch.setattr(sweep, "ROOT", repo)
        code = sweep.run([_mutation("killed")])
        assert code == 2
        assert "BASELINE NOT GREEN" in capsys.readouterr().out


class TestAMutationIsNeverMaskedByStaleBytecode:
    """Found Sept 2, 2026 while building FA-92, by driving the harness at
    speed — which is what a sweep does, one subprocess after another.

    CPython and pytest's rewritten cache both validate a `.pyc` on
    **(source mtime in whole seconds, source size)**. A mutation that does
    not change the file's LENGTH, written inside the same wall-clock second
    as the run that compiled it, leaves both fields identical — the stale
    bytecode is reused, the mutation never reaches the interpreter, and a
    pin that binds perfectly is printed `** INERT **`.

    Measured as a lever experiment before the fix: the identical
    one-mutation sweep returned KILLED · KILLED · KILLED · **INERT** with
    the purge disabled and nothing changed but the clock, and KILLED 4/4
    with it enabled. The forensics on the INERT trial showed the pyc's
    recorded source-mtime equal to the mutated file's.

    This is FA-92's defect wearing the opposite face, and the costlier one:
    a false KILLED lets a weak pin ship, a false INERT gets a GOOD test
    rewritten. The pin below constructs the collision by hand so it does not
    depend on the clock.
    """

    MUTANT = "def add(a, b):\n    return a - b\n"

    def _compile_and_collide(self, tmp_path):
        """Leave the repo with a MUTATED source and a pyc that claims to
        be current for it. Returns the module path."""
        import os
        import struct
        import subprocess

        module = tmp_path / "mod_under_test.py"
        module.write_text(MODULE_SRC, encoding="utf-8")
        (tmp_path / "test_mod_under_test.py").write_text(TEST_SRC,
                                                         encoding="utf-8")
        subprocess.run([sweep.PY, "-m", "pytest", "test_mod_under_test.py",
                        "-q", "--tb=no", "-p", "no:randomly"],
                       cwd=tmp_path, capture_output=True, timeout=900)
        cached = sorted((tmp_path / "__pycache__").glob("mod_under_test.*.pyc"))
        assert cached, "the baseline run wrote no bytecode to go stale"
        stamp = struct.unpack("<I", cached[0].read_bytes()[8:12])[0]
        # Same length as the original, so the size field also still matches.
        assert len(self.MUTANT) == len(MODULE_SRC)
        module.write_text(self.MUTANT, encoding="utf-8")
        os.utime(module, (stamp, stamp))
        return module

    def _tests_pass(self, tmp_path):
        import subprocess
        return subprocess.run(
            [sweep.PY, "-m", "pytest", "test_mod_under_test.py", "-q",
             "--tb=no", "-p", "no:randomly"],
            cwd=tmp_path, capture_output=True, timeout=900).returncode == 0

    def test_the_collision_really_masks_the_mutation(self, tmp_path):
        """The hazard itself: a broken `add` whose tests still pass."""
        self._compile_and_collide(tmp_path)
        assert self._tests_pass(tmp_path), (
            "the stale-bytecode collision did not reproduce — if this ever "
            "fails because CPython changed its validation, the purge below "
            "is belt-and-braces rather than load-bearing, and this pin "
            "should be re-derived, not deleted")

    def test_the_purge_defeats_it(self, tmp_path):
        module = self._compile_and_collide(tmp_path)
        sweep._invalidate_bytecode(module)
        assert not self._tests_pass(tmp_path), (
            "after the purge the mutated source must actually be compiled")

    def test_the_purge_leaves_other_modules_alone(self, tmp_path):
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        mine = cache / "target.cpython-313.pyc"
        theirs = cache / "bystander.cpython-313.pyc"
        for path in (mine, theirs):
            path.write_bytes(b"x")
        sweep._invalidate_bytecode(tmp_path / "target.py")
        assert not mine.exists()
        assert theirs.exists()

    def test_no_cache_directory_is_not_an_error(self, tmp_path):
        sweep._invalidate_bytecode(tmp_path / "never_imported.py")

    def test_both_the_apply_and_the_restore_purge(self):
        """A census, not a grep for the word: the sweep must invalidate when
        it WRITES the mutant (or the run reads stale bytecode) and when it
        RESTORES (or the NEXT mutation does)."""
        import ast
        import inspect

        tree = ast.parse(inspect.getsource(sweep.run))
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name)
                 and n.func.id == "_invalidate_bytecode"]
        assert len(calls) == 2, (
            f"expected the apply and the restore to purge; found {len(calls)}")


class TestTheRestoreRestores:
    """Found by the FA-92 reproduction fleet, at the same six lines: the
    harness's `finally` block did not put back what it read.

    `read_text`/`write_text` do universal-newline translation, so a pure-LF
    target came back CRLF. Measured on `backend/game_logic/calendar.py`:
    3,047 bytes in, 3,129 out, all 82 newlines converted. `core.autocrlf`
    is true here, so `git status` calls the file modified and `git diff`
    shows nothing — a state that invites the next reader to "fix" it. Eight
    of the 75 files the committed sweep sets target are pure LF today, and
    this is the recorded cause of row WO slice 10's "the lever-setter
    matched LF-anchored patterns and silently set nothing once the sweep
    re-emitted the file as CRLF".

    The constraint that makes it non-trivial: 444 of the 719 committed
    mutations carry a MULTI-LINE `old` authored with `\n`, and 340 of the
    repo's Python files are CRLF — so matching on raw bytes would report
    ANCHOR NOT FOUND across most of the corpus. Normalize to match, keep
    the bytes to restore.
    """

    LF_MODULE = MODULE_SRC                       # "\n" endings
    CRLF_MODULE = MODULE_SRC.replace("\n", "\r\n")

    def _sweep_one(self, tmp_path, monkeypatch, capsys, module_bytes, old, new):
        module = tmp_path / "mod_under_test.py"
        module.write_bytes(module_bytes)
        (tmp_path / "test_mod_under_test.py").write_text(
            TEST_SRC, encoding="utf-8")
        monkeypatch.setattr(sweep, "ROOT", tmp_path)
        code = sweep.run([{"file": "mod_under_test.py",
                           "tests": "test_mod_under_test.py",
                           "id": "X", "old": old, "new": new}])
        capsys.readouterr()
        return code, module.read_bytes()

    def test_an_lf_file_is_restored_byte_for_byte(
            self, tmp_path, monkeypatch, capsys):
        raw = self.LF_MODULE.encode("utf-8")
        _, after = self._sweep_one(tmp_path, monkeypatch, capsys, raw,
                                   "return a + b", "return a - b")
        assert after == raw
        assert b"\r\n" not in after

    def test_a_crlf_file_is_restored_byte_for_byte(
            self, tmp_path, monkeypatch, capsys):
        raw = self.CRLF_MODULE.encode("utf-8")
        _, after = self._sweep_one(tmp_path, monkeypatch, capsys, raw,
                                   "return a + b", "return a - b")
        assert after == raw

    def test_a_multiline_lf_anchor_still_matches_a_crlf_file(
            self, tmp_path, monkeypatch, capsys):
        """The regression a raw-bytes fix would have shipped: 444 of the
        719 committed anchors span lines, and most target files are CRLF."""
        raw = self.CRLF_MODULE.encode("utf-8")
        code, after = self._sweep_one(
            tmp_path, monkeypatch, capsys, raw,
            "def add(a, b):\n    return a + b", "def add(a, b):\n    return a - b")
        assert code == 0, "the multi-line anchor must still bind"
        assert after == raw

    def test_the_mutant_is_written_in_the_files_own_ending(self, tmp_path):
        """Not observable through `run` (it restores), so pinned directly:
        a CRLF file's mutant stays CRLF and an LF file's stays LF."""
        crlf = self.CRLF_MODULE.encode("utf-8")
        text, newline = sweep._normalized(crlf)
        assert "\r\n" not in text and newline == "\r\n"
        assert sweep._denormalized(text, newline) == crlf

        lf = self.LF_MODULE.encode("utf-8")
        text, newline = sweep._normalized(lf)
        assert newline == "\n"
        assert sweep._denormalized(text, newline) == lf


# ═══════════════════════════════════════════════════════════════════════
# FA-10 + FA-74 — "a stale refusal is not an answer"
#
# Filed as two rows; measured to be two halves of ONE rule written into
# three memories at one site. The verification pass called them merge
# candidates (both born in the audit's own filing commit, neither with
# priority); reading the code settles what that means — they are neither
# the same edit nor independent defects:
#
#   FA-74 -> `_answered_dialogue_ids`, reset by `begin_post()`, so its
#            blast radius is ONE answer chain;
#   FA-10 -> `_refused_choices`, initialised once and never reset, so its
#            blast radius is the WHOLE RUN.
#
# And a third memory neither row names: `digest.recent`, the cycle-guard
# trail. Fixing only the two filed halves makes the legitimate retry answer
# the same surface with the same word twice in one chain, which is exactly
# what `drain()` calls an ANSWER CYCLE — it stops the chain and leaves every
# other blocker standing. That is a worse outcome than the defect, and it is
# why this is built as one rule over three stores.
# ═══════════════════════════════════════════════════════════════════════

_dspec = importlib.util.spec_from_file_location(
    "playtest_driver_fa_slice8", REPO_ROOT / "tools" / "playtest_driver.py")
pdriver = importlib.util.module_from_spec(_dspec)
sys.modules.setdefault("playtest_driver_fa_slice8", pdriver)
_dspec.loader.exec_module(pdriver)


class ScriptedTransport:
    """Replies in order for the dialogue path; the last reply repeats."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.posts = []

    def post(self, path, payload=None):
        self.posts.append((path, payload))
        if path != "/respond_to_diplomatic_dialogue":
            return {"success": True}
        answered = sum(1 for p in self.posts
                       if p[0] == "/respond_to_diplomatic_dialogue") - 1
        return dict(self.replies[min(answered, len(self.replies) - 1)])

    def get(self, path):
        return {}


class RecordingDigest:
    """The real `Digest`'s answer bookkeeping, borrowed rather than copied.

    `popup` and `discount_answer` are the production methods themselves, so
    this double cannot drift from the rule under test.
    """

    popup = pdriver.Digest.popup
    discount_answer = pdriver.Digest.discount_answer

    def __init__(self):
        self.recent = []
        self.lines = []
        self.notes = []
        self.unknown_blockers = []
        self.counters = {"popups": 0}

    def _md(self, line):
        self.lines.append(line)

    def record(self, kind, **fields):
        pass

    def note(self, text):
        self.notes.append(text)
        self.lines.append(text)

    def battle(self, report):
        pass


STALE = {"success": False, "stale_dialogue": True,
         "message": "Sire, another matter has arrived since - this concerns "
                    "Saxony. Your earlier answer was not delivered;"}
REAL_REFUSAL = {"success": False,
                "message": "You have not the diplomatic points, Sire."}
ACCEPTED = {"success": True, "message": "Signed."}


def _offer(did=17):
    return {"type": "incoming_settlement_offer", "dialogue_id": did,
            "from_nation": "Russia", "proposal_type": "armistice_losing",
            "options": [{"id": "reject"}, {"id": "accept"}]}


def _answerer(transport, digest=None):
    digest = digest or RecordingDigest()
    answerer = pdriver.Answerer(transport, digest,
                                dict(pdriver.POLICY_DEFAULTS), False)
    answerer.begin_post()
    return answerer, digest


def _dialogue_posts(transport):
    return [p for p in transport.posts
            if p[0] == "/respond_to_diplomatic_dialogue"]


class TestAStaleRefusalIsNotAnAnswer:

    def test_the_word_is_not_blacklisted_for_the_rest_of_the_run(self):
        """FA-10's half. `_refused_choices` is never reset, so memorising an
        ORDERING refusal banned the offer's only sane answer for the whole
        campaign — measured on four major-court offers in the archived
        24-turn flagship, and on an `--diplomacy accept` run that answered a
        settlement with `request revision` because accept had been banned."""
        answerer, _ = _answerer(ScriptedTransport([STALE]))
        answerer.scan({"diplomatic_dialogue": _offer()})
        assert answerer._refused_choices == {}, (
            "an ordering refusal says nothing about the word we sent")

    def test_a_real_executor_refusal_is_still_remembered(self):
        """The negative control. WO slice 5 added this memory because a DP
        shortage made the driver re-send the same doomed word every turn
        until end turn was refused forever — blocked on 3 of 7 seeds."""
        answerer, _ = _answerer(ScriptedTransport([REAL_REFUSAL]))
        answerer.scan({"diplomatic_dialogue": _offer()})
        assert answerer._refused_choices, (
            "a refusal the executor actually judged must still be remembered")

    def test_the_id_is_not_marked_answered(self):
        """FA-74's half: the chain-scoped memory. Marked answered, the same
        offer promoted back in the same chain logged `(stale passthrough)`
        and was never re-offered."""
        answerer, _ = _answerer(ScriptedTransport([STALE]))
        answerer.scan({"diplomatic_dialogue": _offer()})
        assert 17 not in answerer._answered_dialogue_ids

    def test_a_delivered_answer_is_marked_answered(self):
        answerer, _ = _answerer(ScriptedTransport([ACCEPTED]))
        answerer.scan({"diplomatic_dialogue": _offer()})
        assert 17 in answerer._answered_dialogue_ids

    def test_the_offer_is_answered_again_when_it_comes_back(self):
        """The whole point: the offer is answered on the retry rather than
        left standing forever."""
        transport = ScriptedTransport([STALE, ACCEPTED])
        answerer, _ = _answerer(transport)
        answerer.scan({"diplomatic_dialogue": _offer()})
        answerer.scan({"diplomatic_dialogue": _offer()})
        answers = _dialogue_posts(transport)
        assert len(answers) == 2, "the second presentation must be answered"
        assert answers[1][1]["dialogue_id"] == 17
        assert 17 in answerer._answered_dialogue_ids


class TestTheRetryDoesNotReadAsACycle:
    """The third memory, which neither row names and which the naive fix
    would have broken."""

    def test_a_stale_attempt_leaves_no_cycle_signature(self):
        answerer, digest = _answerer(ScriptedTransport([STALE]))
        answerer.scan({"diplomatic_dialogue": _offer()})
        assert digest.recent == [], (
            "a refused-as-stale attempt never reached the executor and must "
            "not count toward drain()'s answer-cycle guard")

    def test_the_digest_still_shows_the_attempt(self):
        """WO slice 5's rule: a wedge must be legible. Only the signature is
        withdrawn — the LINE stays."""
        answerer, digest = _answerer(ScriptedTransport([STALE]))
        answerer.scan({"diplomatic_dialogue": _offer()})
        assert any("#17" in line for line in digest.lines)
        assert any("refused" in note for note in digest.notes)

    def test_a_delivered_answer_still_signs_the_trail(self):
        answerer, digest = _answerer(ScriptedTransport([ACCEPTED]))
        answerer.scan({"diplomatic_dialogue": _offer()})
        assert len(digest.recent) == 1

    def test_the_retry_does_not_trip_the_answer_cycle_guard(self):
        """End to end through the real `drain()`: stale, then accepted, in
        ONE chain. Without the discount this raises ANSWER CYCLE and stops
        the chain — the regression the naive fix would have shipped.

        The refusal reply re-presents the same offer, which is what the
        W6-0 guard actually does (it returns `diplomatic_dialogue: dialogue`
        — the dialogue currently on top)."""
        transport = ScriptedTransport(
            [dict(STALE, diplomatic_dialogue=_offer()), ACCEPTED])
        digest = RecordingDigest()
        answerer = pdriver.Answerer(transport, digest,
                                    dict(pdriver.POLICY_DEFAULTS), False)
        pdriver.drain(transport, digest, answerer,
                      {"diplomatic_dialogue": _offer()}, False)
        assert not any("ANSWER CYCLE" in n for n in digest.notes), digest.notes
        assert not digest.unknown_blockers
        assert 17 in answerer._answered_dialogue_ids
        assert len(_dialogue_posts(transport)) == 2


class TestTheRetryIsBounded:
    def test_a_surface_that_goes_stale_twice_is_left_standing_with_a_reason(self):
        transport = ScriptedTransport([STALE])
        answerer, digest = _answerer(transport)
        for _ in range(3):
            answerer.scan({"diplomatic_dialogue": _offer()})
        assert len(_dialogue_posts(transport)) == pdriver.MAX_STALE_ATTEMPTS, (
            "one retry, then stop — an unbounded retry spins the chain")
        assert any("refused as stale" in line for line in digest.lines), (
            "and the digest must say WHY it was left standing")

    def test_the_bound_is_per_chain(self):
        """The next command's chain starts the count over — a surface that
        was wedged behind one turn's traffic is not banned for the run. That
        is the distinction between this bound and FA-10's defect."""
        transport = ScriptedTransport([STALE])
        answerer, _ = _answerer(transport)
        for _ in range(3):
            answerer.scan({"diplomatic_dialogue": _offer()})
        assert len(_dialogue_posts(transport)) == pdriver.MAX_STALE_ATTEMPTS
        answerer.begin_post()
        answerer.scan({"diplomatic_dialogue": _offer()})
        assert len(_dialogue_posts(transport)) == pdriver.MAX_STALE_ATTEMPTS + 1


class TestTheDigestDoubleCannotDrift:
    """The stub digests in the driver's test files re-implement `popup`'s
    rule by hand. A method the Answerer calls but `Digest` does not define
    would surface only as an AttributeError in whichever test happened to
    drive that arm."""

    def test_every_digest_method_the_driver_calls_exists(self):
        import ast
        import inspect
        import textwrap

        called = set()
        for func in (pdriver.Answerer.scan, pdriver.drain):
            src = textwrap.dedent(inspect.getsource(func))
            for node in ast.walk(ast.parse(src)):
                if not (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)):
                    continue
                owner = node.func.value
                if (isinstance(owner, ast.Attribute) and owner.attr == "d") or (
                        isinstance(owner, ast.Name) and owner.id == "digest"):
                    called.add(node.func.attr)
        assert called, "the census found no digest calls — it has stopped working"
        missing = [name for name in called if not hasattr(pdriver.Digest, name)]
        assert not missing, missing


# ═══════════════════════════════════════════════════════════════════════
# FA-37 — the digest shows only the headline and treasury/net/provinces
# FA-87 — and what it does show is a field the client never renders
# ═══════════════════════════════════════════════════════════════════════

class TestTheLedgerLineNamesTheComponents:
    """FA-37. `net` answers "is France solvent"; it cannot answer WHY, which
    is the only question an economy evaluation asks. Every archived digest
    had to be re-derived with a bespoke probe to learn that Contributions
    fired when Paget stood on Normandy."""

    ECONOMY = {"income": 3400, "trade_income": 350, "upkeep": 2450,
               "blockade": 175, "admiralty": 90, "contributions": 0,
               "requisitions": 0, "occupation": 0, "overseas": 0,
               "state_charges": 19, "vassal_tribute": 895,
               "treaty_gold": 0, "settlement_gold": 0, "infrastructure": 0,
               "dotation_skim": 0, "rente_cost": 0, "net": 1961}

    def _digest(self):
        digest = RecordingDigest()
        digest.ledger_line = pdriver.Digest.ledger_line.__get__(digest)
        digest.NET_COMPONENTS = pdriver.Digest.NET_COMPONENTS
        digest._last_provinces = None
        return digest

    def test_every_moved_component_is_named(self):
        digest = self._digest()
        digest.ledger_line(2511, 1961, 68, 28, economy=self.ECONOMY)
        net = [line for line in digest.lines if line.strip().startswith("- NET")]
        assert net, digest.lines
        for label in ("income", "trade", "upkeep", "blockade", "admiralty",
                      "charges", "tribute"):
            assert label in net[0], label

    def test_a_component_that_did_not_move_is_not_printed(self):
        """A line of eleven zeroes hides the one term that turned on."""
        digest = self._digest()
        digest.ledger_line(2511, 1961, 68, 28, economy=self.ECONOMY)
        net = [line for line in digest.lines
               if line.strip().startswith("- NET")][0]
        for label in ("contributions", "requisitions", "occupation",
                      "overseas", "rentes", "dotations"):
            assert label not in net, label

    def test_a_component_that_turns_on_appears(self):
        digest = self._digest()
        digest.ledger_line(2511, 1961, 68, 28,
                           economy=dict(self.ECONOMY, contributions=240))
        assert any("contributions 240" in line for line in digest.lines)

    def test_no_economy_payload_is_not_an_error(self):
        digest = self._digest()
        digest.ledger_line(2511, 1961, 68, 28)
        assert any(line.startswith("- LEDGER") for line in digest.lines)
        assert not any("- NET" in line for line in digest.lines)

    def test_the_component_keys_are_the_ledgers_own(self):
        """A drift pin: the labels are the driver's, the KEYS must be the
        backend's. `build_strategic_ledger`'s economy block is the source."""
        import backend.game_logic.ledger as ledger_module
        source = open(ledger_module.__file__, encoding="utf-8").read()
        for key, _label in pdriver.Digest.NET_COMPONENTS:
            assert f'"{key}"' in source, key


class TestTheDispatchLineCarriesTheRail:
    """FA-37. Defections, transfers, rebellions, eliminations, war
    declarations and every naval and AI-Intent beat land on the diplomatic
    rail and nowhere else — so the archived audit-ambient40 digest holds 40
    turns with no mention of France's three vassals although all three were
    lost."""

    def _digest(self):
        digest = RecordingDigest()
        digest.dispatch = pdriver.Digest.dispatch.__get__(digest)
        digest.MAX_RAIL_ROWS = pdriver.Digest.MAX_RAIL_ROWS
        return digest

    def test_a_high_priority_row_is_archived(self):
        digest = self._digest()
        digest.dispatch("Sire — Swabia has been taken by Austria.", events=[
            {"type": "diplomatic_vassal_defected", "priority": "HIGH",
             "text": "Switzerland has gone over to Austria."}])
        assert any("diplomatic_vassal_defected" in line
                   for line in digest.lines)
        assert any("gone over to Austria" in line for line in digest.lines)

    def test_routine_intent_chatter_is_not(self):
        digest = self._digest()
        digest.dispatch("head", events=[
            {"type": "intent_eases", "priority": "LOW", "text": "cooling"},
            {"type": "paymaster_subsidy", "priority": "MEDIUM", "text": "gold"}])
        assert not any("RAIL" in line for line in digest.lines)

    def test_the_rail_is_capped_with_an_honest_tail(self):
        digest = self._digest()
        digest.dispatch("head", events=[
            {"type": f"t{i}", "priority": "HIGH", "text": f"line {i}"}
            for i in range(9)])
        rails = [line for line in digest.lines if "RAIL" in line]
        assert len(rails) == pdriver.Digest.MAX_RAIL_ROWS + 1
        assert rails[-1].endswith("more")

    def test_turn_events_are_counted(self):
        digest = self._digest()
        digest.dispatch("head", turn_events=[{"type": "vassal_loyalty"}] * 6)
        assert any("TURN EVENTS 6" in line for line in digest.lines)

    def test_the_families_this_row_was_filed_for_are_graded_high(self):
        """The filter is HIGH-only, so it is only safe while the families
        that carry a satellite changing hands, a nation dying or a war
        beginning are graded HIGH. A re-grading to MEDIUM would silently
        hide them from every future digest — this pin reds instead."""
        from backend.game_logic.dispatch import _DIPLOMATIC_EVENT_PRIORITY
        for etype in ("diplomatic_vassal_defected",
                      "diplomatic_vassal_transferred",
                      "diplomatic_vassal_rebellion",
                      "nation_eliminated",
                      "diplomatic_treaty_broken",
                      "diplomatic_war_declared"):
            assert _DIPLOMATIC_EVENT_PRIORITY.get(etype) == "HIGH", etype


class TestTheThreatTrajectoryExists:
    """FA-37/FA-39: `threat` sat in `ledger_line`'s signature and never
    printed. Measured against a live payload — `GET /ledger` carries no
    `threat_level` and no `threat` at ANY depth, so the recursive dig
    returned None on every turn of every archived run."""

    @staticmethod
    def _shipped_client(monkeypatch):
        """The SHIPPED 1805 boot. The suite pins `SOVEREIGN_SCENARIO=none`
        (the bare flag world), which has no marshals and no coalition — a
        payload shape this row's claims are not about."""
        import backend.main as M
        from backend.commands.parser import CommandParser
        from fastapi.testclient import TestClient

        monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
        monkeypatch.delenv("SOVEREIGN_MAP", raising=False)
        monkeypatch.delenv("SOVEREIGN_SMOKE_START", raising=False)
        M._reset_world_state()
        monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
        return TestClient(M.app)

    def test_the_ledger_payload_has_no_threat_key(self, monkeypatch):
        """The reason the old read was dead, pinned so a builder does not
        'fix' it by putting the dig back."""
        client = self._shipped_client(monkeypatch)
        assert pdriver.dig(client.get("/ledger").json(),
                           "threat_level", "threat") is None

    def test_the_dispatch_payload_carries_it(self, monkeypatch):
        client = self._shipped_client(monkeypatch)
        client.post("/command", json={"command": "end turn"})
        morning = (client.get("/dispatch").json() or {}).get("dispatch") or {}
        threat = pdriver.dig(morning.get("coalition_status"),
                             "threat_level", "threat")
        assert isinstance(threat, (int, float)), morning.get("coalition_status")


class TestTheEnemyPhaseSummaryIsReadable:
    """FA-87 (and FA-86, which the verification pass filed as its duplicate
    in the same commit — one defect, two rows)."""

    BOMBARDMENT = ("=" * 40 + "\n  BOMBARDMENT: Shrapnel → Massena\n"
                   + "=" * 40 + "\nThe guns thunder.")
    CAPTURE = ("\n[Combat] ArchdukeCharles's DEFENSIVE stance hampers "
               "offensive operations (-10% attack)\n"
               "ArchdukeCharles attacks with overwhelming force. Casualties: "
               "ArchdukeCharles's army 1,188, Deroy 7,465. Both armies remain "
               "in the field. Bohemia has been captured by Austria!\n"
               "[Materiel] Guns, horses and stores lost with the fallen.")

    def test_a_banner_is_never_the_summary(self):
        assert pdriver.first_line(self.BOMBARDMENT) == (
            "BOMBARDMENT: Shrapnel → Massena")

    def test_a_tactical_annotation_yields_to_the_prose(self):
        assert pdriver.salient_line(self.CAPTURE).startswith(
            "ArchdukeCharles attacks with overwhelming force")

    def test_an_all_annotation_message_still_says_something(self):
        assert pdriver.salient_line("[Shield] He stands firm!") == (
            "[Shield] He stands firm!")

    def test_the_capture_caption_names_the_capture(self):
        needles = ("captur", "has fallen", "falls to", "taken by", "seized")
        caption = pdriver.matching_line(self.CAPTURE, needles, 150)
        assert caption.endswith("Bohemia has been captured by Austria!")

    def test_the_capture_caption_keeps_the_run_up_when_it_fits(self):
        """The conquest is often a trailing fragment whose subject is the
        sentence before it."""
        needles = ("captur",)
        march = ("ArchdukeJohn marches from Tyrol into Carniola unopposed! "
                 "(232 lost to march) Captured: Bavaria → Austria")
        assert pdriver.matching_line(march, needles, 150) == march

    def test_a_message_with_no_needle_falls_back(self):
        assert pdriver.matching_line("Nothing happened.", ("captur",)) == (
            "Nothing happened.")

    def test_the_jsonl_keeps_the_whole_message(self):
        """The record's own comment promises "the query surface should never
        be thinner than the markdown", and it stored `first_line(..., 200)`.
        Measured while building this row: a probe scanning the jsonl for
        capture prose found ONE of the three the markdown had flagged."""
        import ast
        import inspect
        import textwrap

        src = textwrap.dedent(inspect.getsource(pdriver.Digest.enemy_phase))
        record = [n for n in ast.walk(ast.parse(src))
                  if isinstance(n, ast.Call)
                  and isinstance(n.func, ast.Attribute)
                  and n.func.attr == "record"]
        assert record, "the enemy-phase record call moved"
        rendered = ast.unparse(record[0])
        assert "'message': a.get('message')" in rendered, rendered


# ═══════════════════════════════════════════════════════════════════════
# FA-40 — the archived tutorial digest cannot evidence the lesson
#
# The committed driver script had drifted from the shipped card in three
# independent ways, so the archived `audit-tutorial` digest reproduces the
# PC15-9 symptom ("Target out of range") from OUTSIDE the beat's window and
# under a policy the card argues against:
#
#   * the bombardment fired at loop 4; PC15-9 moved its gate to 2, because
#     Jellacic's hold on Tyrol is only guaranteed through T3;
#   * first blood fired at loop 3; its gate is 4;
#   * the conquest beat issued `Ney, attack Jellacic`; the card suggests
#     `Davout, move to Bohemia`;
#   * and the run used `objection: trust` while step V says, in the card's
#     own words, "I advise INSIST, Sire".
#
# Both arms now walk the whole lesson. The only refusal left in either is
# the one the card explicitly TEACHES — "if an Austrian corps holds it, the
# refusal names him — attack that name" — followed by the attack that takes
# the province.
# ═══════════════════════════════════════════════════════════════════════

TUTORIAL_SCRIPT = REPO_ROOT / "tools" / "playtest_scripts" / "tutorial_lesson.json"
TUTORIAL_TRUST = (REPO_ROOT / "tools" / "playtest_scripts"
                  / "tutorial_lesson_trust.json")
OVERLAY = (REPO_ROOT / "godot-client" / "project-sovereign" / "scripts"
           / "tutorial_overlay.gd")


def _shipped_steps():
    """(id, turn_gate, suggest) for every step of the shipped card."""
    import re as _re

    src = OVERLAY.read_text(encoding="utf-8")
    body = src[src.index("STEPS"):src.index("Resume anchor")]
    steps = []
    for block in body.split('"id":')[1:]:
        ident = _re.match(r'\s*"([^"]+)"', block)
        gate = _re.search(r'"turn_gate":\s*(\d+)', block)
        suggest = _re.search(r'"suggest":\s*"([^"]*)"', block)
        if ident and gate and suggest is not None:
            steps.append((ident.group(1), int(gate.group(1)),
                          suggest.group(1)))
    return steps


def _script(path):
    import json
    return json.loads(path.read_text(encoding="utf-8"))


class TestTheTutorialScriptMirrorsTheShippedLesson:

    def test_the_census_can_read_the_card(self):
        """If the overlay's STEPS shape changes, the pins below would pass
        vacuously. They must fail loudly instead."""
        steps = _shipped_steps()
        assert len(steps) >= 12, steps
        assert any(i == "bombardment" and g == 2 for i, g, _s in steps)
        assert any(i == "first_battle" and g == 4 for i, g, _s in steps)

    def test_every_suggested_command_is_issued_at_its_own_gate(self):
        """The pin that would have caught all three drifts. `end turn` is
        excluded — the driver ends every turn itself — and the two answer
        steps carry no suggestion (a policy answers them)."""
        turns = _script(TUTORIAL_SCRIPT)["turns"]
        for ident, gate, suggest in _shipped_steps():
            if not suggest or suggest == "end turn":
                continue
            issued = turns.get(str(gate)) or []
            assert suggest in issued, (
                f"step {ident} (gate {gate}) suggests {suggest!r}; the "
                f"script issues {issued!r} on that loop")

    # FA-N78 (slice 14 part 2c): the card used to counsel "I advise INSIST",
    # naming the TYPED token — which the shipped client cannot accept at that
    # beat, because the objection modal disables the command line. The card
    # now names the BUTTON ("Proceed as Ordered"), while the headless driver
    # still answers with the token. Both are correct and they must agree, so
    # the pin binds the two through an explicit mapping rather than through a
    # literal that only one surface uses.
    OBJECTION_COUNSEL = {
        "insist": "I advise PROCEED AS ORDERED",
        "trust": "I advise TRUST",
        "compromise": "I advise COMPROMISE",
    }

    def test_the_policy_follows_the_cards_own_counsel(self):
        policy = _script(TUTORIAL_SCRIPT)["policy"]["objection"]
        assert policy == "insist"
        counsel = self.OBJECTION_COUNSEL[policy]
        assert counsel in OVERLAY.read_text(encoding="utf-8"), (
            f"the driver answers {policy!r} but the card does not counsel it")

    def test_the_trust_branch_has_its_own_script(self):
        trust = _script(TUTORIAL_TRUST)
        assert trust["policy"]["objection"] == "trust"
        assert trust["scenario"] == "tutorial"

    def test_both_scripts_declare_the_lesson_scenario(self):
        """`scenario` was CLI-only, so the archived digest could not say
        which board produced it — and `tutorial_lesson.json` could be run
        against the 1805 campaign in silence."""
        for path in (TUTORIAL_SCRIPT, TUTORIAL_TRUST):
            assert _script(path)["scenario"] == "tutorial", path

    def test_the_driver_reads_the_scripts_scenario(self):
        import argparse

        args = argparse.Namespace(name=None, seed=None, llm=None, scenario="")
        script = {"scenario": "tutorial"}
        args.scenario = args.scenario or script.get("scenario") or ""
        assert args.scenario == "tutorial"
        # …and that the production line exists, in the same idiom as its
        # siblings, rather than only in this test.
        src = (REPO_ROOT / "tools" / "playtest_driver.py").read_text(
            encoding="utf-8")
        assert ('args.scenario = args.scenario or script.get("scenario")'
                in src)


class TestTheCallSitesActuallyUseThem:
    """The sweep's own answer to two INERT pins.

    `matching_line` and the dispatch threat source were both pinned as pure
    functions and as payload facts — so reverting the CALL SITE changed
    nothing and the pins proved nothing about the digest a reader opens.
    These drive the real seams.
    """

    def test_the_capture_row_is_captioned_by_the_capture_sentence(self):
        """Drives `Digest.enemy_phase`. Reverting its `matching_line` call to
        `first_line` puts the tactical annotation back under the flag —
        `🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers…`,
        verbatim from the archive."""
        digest = RecordingDigest()
        for name in ("enemy_phase", "battle", "autonomous_attacks"):
            method = getattr(pdriver.Digest, name, None)
            if method is not None:
                setattr(digest, name, method.__get__(digest))
        digest.counters = {"popups": 0, "battles": 0}
        digest.enemy_phase([{
            "nation": "Austria",
            "ai_action": {"action": "attack", "marshal": "ArchdukeCharles"},
            "message": ("[Combat] ArchdukeCharles's DEFENSIVE stance hampers "
                        "offensive operations (-10% attack)\n"
                        "ArchdukeCharles attacks with overwhelming force. "
                        "Both armies remain in the field. Bohemia has been "
                        "captured by Austria!")}])
        flags = [line for line in digest.lines if "🏴" in line]
        assert flags, digest.lines
        assert flags[0].rstrip().endswith(
            "Bohemia has been captured by Austria!"), flags[0]
        assert "DEFENSIVE stance" not in flags[0]

    def test_a_real_run_prints_a_threat_figure(self, tmp_path, monkeypatch):
        """Drives the driver's own turn loop end to end on the SHIPPED board.

        `dig(ledger, "threat_level", "threat")` returns None on every turn —
        which is why no archived digest has a coalition-threat trajectory —
        so a pin on the payloads alone leaves the call site free to go back
        to reading the wrong endpoint."""
        import subprocess

        monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path / "saves"))
        monkeypatch.setenv("LLM_MODE", "mock")
        monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
        out = tmp_path / "runs"
        proc = subprocess.run(
            [sweep.PY, "tools/playtest_driver.py", "--turns", "2",
             "--name", "threat-pin", "--fresh", "--llm", "mock",
             "--out", str(out)],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=900)
        digest = out / "threat-pin" / "digest.md"
        assert digest.exists(), (proc.stdout or "")[-1500:]
        ledger_lines = [line for line in
                        digest.read_text(encoding="utf-8").splitlines()
                        if line.startswith("- LEDGER")]
        assert ledger_lines, "the run produced no LEDGER line"
        assert all("threat " in line for line in ledger_lines), ledger_lines
        assert any("- NET " in line for line in
                   digest.read_text(encoding="utf-8").splitlines())
