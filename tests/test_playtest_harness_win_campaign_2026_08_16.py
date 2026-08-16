"""Playtest-harness fixes from the Aug 16, 2026 "try to win" campaign.

Four harness defects, each of which had silently degraded EVERY prior
unattended evaluation:

  1. NPC-16 (harness half) — an interrupt raised during end-turn rides
     only ``strategic_reports[i].requires_input``. The driver scanned
     only the top-level ``pending_interrupt`` key, never answered it,
     and the marshal — then the turn loop — froze. The Godot client has
     always read the report list (main.gd:4218); now the driver does too.
  2. The enemy-phase verb — it lives at ``row["ai_action"]["action"]``
     (turn_manager.py builds it). PC15-H tried to fix the "0 attacks"
     under-read by reading ``row["action"]``, a key that does not exist,
     so every digest reported 0 attacks no matter what happened.
  3. The answer cycle — ``settlement_confirm`` option 1 stages a pair
     substitute; the chooser's ``keep_joint_settlement`` is DOCUMENTED to
     restore the prior dialogue. Neither is a game defect, but together
     they loop forever: 97 popups and a `blocked` run that reads like an
     engine fault. Answering one surface the same way twice in a single
     post now stops the chain and says so.
  4. The province scoreboard — GET /ledger wraps its body under
     "ledger", so the conquest counter read None. Without it a campaign
     can annihilate an empire and never notice its own map did not grow
     (measured: France 29 provinces at boot, 29 after Austria fell).
"""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DRIVER_PATH = REPO_ROOT / "tools" / "playtest_driver.py"


def _load_driver():
    """Import the driver module by path (tools/ is not a package)."""
    spec = importlib.util.spec_from_file_location("_playtest_driver",
                                                  DRIVER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_playtest_driver"] = module
    spec.loader.exec_module(module)
    return module


driver = _load_driver()


# ═══════════════════════════════════════════════════════════════════
# 1. NPC-16 — the end-turn interrupt is discoverable
# ═══════════════════════════════════════════════════════════════════

class TestInterruptReportDiscovery:
    def test_finds_the_report_awaiting_input(self):
        response = {"strategic_reports": [
            {"marshal": "Soult", "requires_input": False},
            {"marshal": "Napoleon", "requires_input": True,
             "interrupt_type": "cannon_fire",
             "options": ["investigate", "continue_order"]},
        ]}
        found = driver._interrupt_report(response)
        assert found["marshal"] == "Napoleon"
        assert found["interrupt_type"] == "cannon_fire"

    def test_returns_falsy_when_nothing_awaits(self):
        assert not driver._interrupt_report(
            {"strategic_reports": [{"marshal": "Ney", "requires_input": False}]})
        assert not driver._interrupt_report({})
        assert not driver._interrupt_report(None)

    def test_scan_answers_an_end_turn_interrupt(self):
        """The whole point: no top-level pending_interrupt, yet the
        driver still posts to /strategic_response. Before the fix this
        returned no follow-up and the campaign froze."""
        posts = []

        class FakeTransport:
            def post(self, path, body):
                posts.append((path, body))
                return {}

        class FakeDigest:
            def __init__(self):
                self.recent = []

            def popup(self, key, summary, answer):
                self.recent.append((key, str(answer)))

            def battle(self, report):
                pass

        answerer = driver.Answerer(FakeTransport(), FakeDigest(),
                                   dict(driver.POLICY_DEFAULTS), False)
        followups = answerer.scan({"strategic_reports": [
            {"marshal": "Napoleon", "requires_input": True,
             "interrupt_type": "cannon_fire",
             "options": ["investigate", "continue_order"]}]})

        assert len(followups) == 1
        path, body = posts[0]
        assert path == "/strategic_response"
        assert body["marshal_name"] == "Napoleon"
        # handle_response dispatches on the STORED interrupt_type, but the
        # driver must not send the empty string it used to send.
        assert body["response_type"] == "cannon_fire"
        assert body["choice"] == "investigate"


# ═══════════════════════════════════════════════════════════════════
# 2. The enemy-phase verb — the "0 attacks" under-read
# ═══════════════════════════════════════════════════════════════════

class TestEnemyPhaseVerb:
    def test_reads_the_nested_ai_action_verb(self):
        row = {"nation": "Russia",
               "ai_action": {"action": "attack", "marshal": "Kutuzov"}}
        assert driver._verb(row) == "attack"

    def test_falls_back_to_flat_keys(self):
        assert driver._verb({"action": "MOVE"}) == "move"
        assert driver._verb({"action_type": "Recruit"}) == "recruit"

    def test_absent_verb_is_empty_never_none(self):
        assert driver._verb({"message": "x"}) == ""
        assert driver._verb(None) == ""

    def test_the_regression_shape_that_read_zero(self):
        """The exact payload shape the backend ships: `action` absent,
        verb nested. A substring test over row['action'] sees None."""
        rows = [{"nation": "Russia",
                 "ai_action": {"action": "attack", "marshal": "Kutuzov"}}
                for _ in range(3)]
        assert len([r for r in rows if "attack" in driver._verb(r)]) == 3
        # and the pre-fix read finds nothing at all
        assert not [r for r in rows
                    if "attack" in str(r.get("action") or "")]


# ═══════════════════════════════════════════════════════════════════
# 3. The answer cycle guard
# ═══════════════════════════════════════════════════════════════════

class _CyclingAnswerer:
    """Answers forever with the same (key, choice) — the settlement
    bounce, distilled."""

    def __init__(self, digest):
        self.d = digest
        self.calls = 0

    def scan(self, response):
        self.calls += 1
        self.d.popup("diplomatic_dialogue", "settlement_confirm", "1")
        return [{"next": True}]


class _Digest:
    def __init__(self):
        self.recent = []
        self.notes = []
        self.unknown_blockers = []

    def popup(self, key, summary, answer):
        self.recent.append((str(key), str(answer)))

    def note(self, text):
        self.notes.append(text)


class TestAnswerCycleGuard:
    def test_stops_well_before_the_chain_cap(self):
        digest = _Digest()
        answerer = _CyclingAnswerer(digest)
        driver.drain(None, digest, answerer, {"start": True}, False)
        # Two identical answers is the trip point, so the guard fires long
        # before MAX_ANSWERS_PER_POST (which produced 97 popups).
        assert answerer.calls == 2
        assert answerer.calls < driver.MAX_ANSWERS_PER_POST
        assert any("ANSWER CYCLE" in n for n in digest.notes)

    def test_records_an_unknown_blocker_for_the_meta(self):
        digest = _Digest()
        driver.drain(None, digest, _CyclingAnswerer(digest), {}, False)
        assert digest.unknown_blockers
        assert digest.unknown_blockers[0]["reason"] == "answer-cycle"

    def test_strict_mode_raises(self):
        digest = _Digest()
        try:
            driver.drain(None, digest, _CyclingAnswerer(digest), {}, True)
        except RuntimeError as exc:
            assert "cycle" in str(exc)
        else:
            raise AssertionError("--strict must fail loudly on a cycle")

    def test_distinct_answers_are_not_a_cycle(self):
        """Progress must not be mistaken for looping: a chain that
        answers different surfaces runs to its natural end."""
        digest = _Digest()

        class Progressing:
            def __init__(self):
                self.n = 0

            def scan(self, response):
                self.n += 1
                if self.n > 3:
                    return []
                digest.popup("popup", "s", f"choice-{self.n}")
                return [{"step": self.n}]

        answerer = Progressing()
        driver.drain(None, digest, answerer, {}, False)
        assert not digest.notes
        assert not digest.unknown_blockers


# ═══════════════════════════════════════════════════════════════════
# 4. The pair-substitute answer follows the diplomacy policy
# ═══════════════════════════════════════════════════════════════════

class TestPairSubstitutePolicy:
    def _choice(self, mode):
        policy = dict(driver.POLICY_DEFAULTS)
        policy["diplomacy"] = mode
        answerer = driver.Answerer(None, None, policy, False)
        return answerer._dialogue_choice(
            {"type": "settlement_pair_substitute_confirm", "options": []})

    def test_accepting_run_commits_to_the_substitute(self):
        assert self._choice("accept") == "confirm_pair_substitute"

    def test_declining_run_keeps_the_joint_draft(self):
        assert self._choice("decline") == "keep"


# ═══════════════════════════════════════════════════════════════════
# 5. The province scoreboard reads the wrapped ledger body
# ═══════════════════════════════════════════════════════════════════

class TestProvinceScoreboard:
    def test_driver_unwraps_the_ledger_envelope(self):
        """GET /ledger returns {"success":…, "ledger": {…}} — reading
        `territories` off the envelope yields None, which is what shipped
        `provinces None` on every row."""
        source = DRIVER_PATH.read_text(encoding="utf-8")
        assert 'ledger.get("ledger")' in source
        assert '.get("territories")' in source

    def test_ledger_line_reports_the_delta(self):
        digest = driver.Digest.__new__(driver.Digest)
        digest.counters = {}
        digest.recent = []
        digest._last_provinces = None
        lines = []
        digest._md = lines.append
        digest.record = lambda *a, **k: None

        digest.ledger_line(100, 5, None, 29)
        digest.ledger_line(100, 5, None, 30)
        assert "provinces 29" in lines[0]
        assert "provinces 30 (+1)" in lines[1]
