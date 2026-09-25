"""FA slice 17, Phase 4 part A (September 12, 2026) — the re-score's P2 rows
and three of its rulings, each behind a lever whose False arm reproduces the
prior behaviour.

  FA-S17-9  the pursuit quotes the sighting it was plotted from, and a cold
            trail ends as an outcome
  FA-S17-11 the battle that took a commander says so, at any scale
  FA-S17-12 + ruling FA-S17-D4: a cooled petition is retired at delivery
  FA-S17-10 (NARROWED to the harness) the digest prints the scope label
  ruling FA-S17-D5: the Guard's last road is named before it is spent
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

from backend.commands import strategic as ST
from backend.commands.combat_executor import CombatExecutor
from backend.commands.executor import CommandExecutor
from backend.commands.strategic_executor import StrategicExecutor
from backend.game_logic import jealousy as J
from tests.conftest import MarshalFactory, WorldFactory

ROOT = next(p for p in (Path(__file__).resolve().parents[1], Path.cwd()) if (p / "backend").is_dir())


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _at_war(world, a="France", b="Austria"):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn
    return world


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-9 — the pursuit quotes its sighting; a cold trail is an outcome
# ═══════════════════════════════════════════════════════════════════════
class TestThePursuitQuotesItsSighting:
    @staticmethod
    def _board():
        ney = MarshalFactory.infantry(name="Ney", location="Belgium", strength=20000,
                                      personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Waterloo", nation="Austria",
                                    strength=9000)
        world = _at_war(WorldFactory.with_marshals([ney, mack]))
        world.calculate_visibility()
        return world, ney, mack

    def _issue(self, world):
        """A PURSUE is a STRATEGIC order, not an action id — the typed route
        is `Ney, attack Mack` upgraded by `detect_strategic_command`."""
        ex = CommandExecutor()
        # `is_strategic` / `strategic_type` are TOP-LEVEL keys on the parsed
        # dict (the executor's strategic routing reads them there), not inside
        # `command` — the shape `tests/test_bugfix_session3.py::make_cmd` uses.
        parsed = {
            "command": {"action": "strategic_command", "marshal": "Ney",
                        "target": "Mack", "raw_command": "Ney, pursue Mack"},
            "is_strategic": True,
            "strategic_type": "PURSUE",
        }
        with _quiet():
            return ex.execute(parsed, {"world": world, "executor": ex})

    def test_the_acceptance_line_names_a_province_not_unknown(self):
        world, ney, mack = self._board()
        res = self._issue(world)
        msg = str(res.get("message", ""))
        assert "pursues" in msg, msg
        assert "(at unknown)" not in msg, msg
        assert "(at Waterloo)" in msg, msg

    def test_the_sighting_survives_a_first_step_that_loses_the_quarry(self, monkeypatch):
        """The row's own mechanism: the first step's visibility refresh can
        lose the quarry, and the line used to re-resolve AFTER it."""
        world, ney, mack = self._board()
        calls = {"n": 0}
        real = StrategicExecutor._pursue_known_location

        def fading(self, w, marshal, enemy):
            # The measured sequence: the issuance fog gate resolves him
            # (call 1), the road is plotted from him (call 2), the first step
            # runs — and any resolution AFTER it finds him gone.
            calls["n"] += 1
            return real(self, w, marshal, enemy) if calls["n"] <= 2 else None

        monkeypatch.setattr(StrategicExecutor, "_pursue_known_location", fading)
        res = self._issue(world)
        assert calls["n"] >= 1
        assert "(at unknown)" not in str(res.get("message", "")), res.get("message")

    def test_lever_down_reproduces_the_unknown_line(self, monkeypatch):
        world, ney, mack = self._board()
        calls = {"n": 0}
        real = StrategicExecutor._pursue_known_location

        def fading(self, w, marshal, enemy):
            # The measured sequence: the issuance fog gate resolves him
            # (call 1), the road is plotted from him (call 2), the first step
            # runs — and any resolution AFTER it finds him gone.
            calls["n"] += 1
            return real(self, w, marshal, enemy) if calls["n"] <= 2 else None

        monkeypatch.setattr(StrategicExecutor, "_pursue_known_location", fading)
        monkeypatch.setattr(StrategicExecutor, "PURSUIT_QUOTES_THE_SIGHTING", False)
        res = self._issue(world)
        assert "(at unknown)" in str(res.get("message", "")), res.get("message")


class TestTheColdTrailIsAnOutcome:
    @staticmethod
    def _order_with_no_intel():
        from backend.models.marshal import StrategicOrder
        ney = MarshalFactory.infantry(name="Ney", location="Belgium", strength=20000,
                                      personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Hanover", nation="Austria",
                                    strength=9000)
        world = _at_war(WorldFactory.with_marshals([ney, mack]))
        ney.strategic_order = StrategicOrder(
            command_type="PURSUE", target="Mack", target_type="marshal",
            started_turn=int(world.current_turn) - 1, issued_turn=None,
            path=["Waterloo"], original_command="Ney, pursue Mack")
        # no intel on Mack at all
        world.region_intel = {}
        return world, ney

    def _tick(self, world, ney):
        proc = ST.StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            return proc._execute_strategic_turn(ney, world, {"world": world})

    def test_the_verdict_says_the_trail_went_cold_and_where(self):
        world, ney = self._order_with_no_intel()
        report = self._tick(world, ney)
        msg = str((report or {}).get("message", ""))
        assert "trail has gone cold" in msg, msg
        assert "Waterloo" in msg, msg
        assert "Scout for him" in msg, msg
        assert ney.strategic_order is None

    def test_it_is_not_the_issuance_refusals_sentence(self):
        """An order never accepted and an order that has been running must
        not end with the same sentence — that is the whole row."""
        world, ney = self._order_with_no_intel()
        report = self._tick(world, ney)
        assert "No intelligence on" not in str((report or {}).get("message", ""))

    def test_lever_down_reproduces_the_bare_refusal(self, monkeypatch):
        monkeypatch.setattr(ST, "THE_COLD_TRAIL_IS_AN_OUTCOME", False)
        world, ney = self._order_with_no_intel()
        report = self._tick(world, ney)
        msg = str((report or {}).get("message", ""))
        assert "No intelligence on Mack's position" in msg, msg
        assert "trail has gone cold" not in msg


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-11 — the battle that took a commander says so, at any scale
# ═══════════════════════════════════════════════════════════════════════
class TestTheCaptureIsOnTheReport:
    @staticmethod
    def _report():
        return {"battle_report": {"observation": "Scarcely an action, Sire."}}

    def test_a_sovereigns_capture_leads_the_report(self):
        """Flipped consciously by the GE-1 verification round (V21): the
        Emperor's fate REPLACES the verdict about scale rather than being
        appended to it — every skirmish verdict denies the day mattered
        ("too small a scale to signify"), which is false of the field that
        took the Emperor. An ordinary marshal's capture is still appended
        (the FA-S17-11 ruling, pinned below)."""
        nap = MarshalFactory.infantry(name="Napoleon", location="Belgium", strength=0,
                                      personality="sovereign")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium", nation="Austria",
                                    strength=9000)
        nap.captured_by = "Britain"
        br = self._report()
        CombatExecutor._stamp_capture_on_report(br, nap, mack, {"Napoleon", "Mack"})
        obs = br["battle_report"]["observation"]
        assert obs == "The Emperor himself was taken on that field — Britain holds him."
        assert "Scarcely an action" not in obs

    def test_an_ordinary_marshal_is_named(self):
        soult = MarshalFactory.infantry(name="Soult", location="Belgium", strength=0)
        mack = MarshalFactory.enemy(name="Mack", location="Belgium", nation="Austria",
                                    strength=9000)
        soult.captured_by = "Austria"
        br = self._report()
        CombatExecutor._stamp_capture_on_report(br, soult, mack, {"Soult", "Mack"})
        assert "Soult was taken on that field — Austria holds him" in br["battle_report"]["observation"]

    def test_a_captivity_that_began_elsewhere_is_not_claimed(self):
        """The pass reports what IT did: a man already a prisoner when the
        guns opened is not 'taken on that field'."""
        soult = MarshalFactory.infantry(name="Soult", location="Belgium", strength=0)
        mack = MarshalFactory.enemy(name="Mack", location="Belgium", nation="Austria",
                                    strength=9000)
        soult.captured_by = "Austria"
        br = self._report()
        CombatExecutor._stamp_capture_on_report(br, soult, mack, {"Mack"})
        assert br["battle_report"]["observation"] == "Scarcely an action, Sire."

    def test_it_is_idempotent(self):
        soult = MarshalFactory.infantry(name="Soult", location="Belgium", strength=0)
        soult.captured_by = "Austria"
        br = self._report()
        for _ in range(3):
            CombatExecutor._stamp_capture_on_report(br, soult, None, {"Soult"})
        assert br["battle_report"]["observation"].count("was taken on that field") == 1

    def test_lever_down_leaves_the_report_alone(self, monkeypatch):
        monkeypatch.setattr(CombatExecutor, "THE_CAPTURE_IS_ON_THE_REPORT", False)
        soult = MarshalFactory.infantry(name="Soult", location="Belgium", strength=0)
        soult.captured_by = "Austria"
        br = self._report()
        CombatExecutor._stamp_capture_on_report(br, soult, None, {"Soult"})
        assert br["battle_report"]["observation"] == "Scarcely an action, Sire."

    def test_the_fate_pass_calls_it(self):
        src = (ROOT / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        i = src.index("def _handle_forced_retreat")
        j = src.index("def _stamp_capture_on_report")
        body = src[i:j]
        assert "_free_before = {m.name for m in (attacker, defender)" in body
        assert "self._stamp_capture_on_report(battle_result, attacker, defender," in body


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-D5 — the Guard's last road is named before it is spent
# ═══════════════════════════════════════════════════════════════════════
class TestTheGuardCountsItsRoads:
    @staticmethod
    def _cornered(strength):
        nap = MarshalFactory.infantry(name="Napoleon", location="Belgium",
                                      strength=strength, personality="sovereign")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium", nation="Austria",
                                    strength=40000)
        world = _at_war(WorldFactory.with_marshals([nap, mack]))
        ex = CommandExecutor()
        with _quiet():
            ex._combat._check_marshal_fate(nap, mack, world)
        return nap

    def test_a_toll_that_leaves_room_says_nothing_new(self):
        nap = self._cornered(4000)
        note = getattr(nap, "_sovereign_toll_note", "")
        assert "bought the road" in note
        assert "cannot buy another road" not in note

    def test_the_last_road_is_named_while_he_still_has_a_choice(self):
        # 100 men: the toll takes 30, leaving 70; the NEXT toll would leave 49
        nap = self._cornered(100)
        note = getattr(nap, "_sovereign_toll_note", "")
        assert "bought the road" in note
        assert "cannot buy another road" in note
        assert "70 men about him now" in note
        assert nap.strength == 70

    def test_lever_down_keeps_the_silent_note(self, monkeypatch):
        monkeypatch.setattr(CombatExecutor, "THE_GUARD_COUNTS_ITS_ROADS", False)
        nap = self._cornered(100)
        assert "cannot buy another road" not in getattr(nap, "_sovereign_toll_note", "")


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-12 + FA-S17-D4 — a cooled petition is retired at delivery
# ═══════════════════════════════════════════════════════════════════════
class TestTheAudienceIsStillOwed:
    @staticmethod
    def _board(jealous_of="Davout"):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium", strength=20000)
        dav = MarshalFactory.infantry(name="Davout", location="Belgium", strength=20000)
        world = WorldFactory.with_marshals([ney, dav])
        ney.jealous_of = jealous_of
        return world, ney

    @staticmethod
    def _card(marshal="Ney", target="Davout"):
        return {"kind": "jealousy_confrontation", "marshal": marshal,
                "context": {"marshal": marshal, "target": target},
                "options": [{"id": "acknowledge"}]}

    def test_a_live_quarrel_is_delivered(self):
        world, ney = self._board()
        assert J.petition_is_still_live(self._card(), world) is True

    def test_a_cooled_quarrel_is_retired(self):
        world, ney = self._board(jealous_of=None)
        assert J.petition_is_still_live(self._card(), world) is False

    def test_a_quarrel_that_moved_on_is_retired(self):
        world, ney = self._board(jealous_of="Soult")
        assert J.petition_is_still_live(self._card(), world) is False

    def test_a_marshal_who_cannot_ask_is_retired(self):
        world, ney = self._board()
        ney.captured_by = "Austria"
        assert J.petition_is_still_live(self._card(), world) is False

    def test_other_kinds_are_untouched(self):
        world, ney = self._board(jealous_of=None)
        for kind in ("fontainebleau_petition", "rivalry_event", "war_weary"):
            card = self._card()
            card["kind"] = kind
            assert J.petition_is_still_live(card, world) is True, kind

    def test_lever_down_delivers_the_stale_card(self, monkeypatch):
        monkeypatch.setattr(J, "THE_AUDIENCE_IS_STILL_OWED", False)
        world, ney = self._board(jealous_of="Soult")
        assert J.petition_is_still_live(self._card(), world) is True

    def test_the_delivery_seam_asks(self):
        src = (ROOT / "backend" / "main.py").read_text(encoding="utf-8")
        i = src.index('response["deferred_marshal_petition"] = refresh_petition_affordability')
        window = src[max(0, i - 700):i]
        assert "petition_is_still_live(_petition, world)" in window

    def test_the_answer_time_guard_still_stands(self):
        """The delivery check is defence in depth, not a replacement: a card
        already in the player's hands when the quarrel cools must still be
        refused honestly."""
        src = (ROOT / "backend" / "game_logic" / "jealousy.py").read_text(encoding="utf-8")
        assert "marshal.jealous_of != _asked_about" in src
        assert "The moment has passed —" in src


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-10 — the harness prints the label the game sets
# ═══════════════════════════════════════════════════════════════════════
class TestTheDigestPrintsTheScope:
    def test_the_driver_reads_the_scope_key(self):
        src = (ROOT / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        assert 'summary.get("attacker_casualties_scope")' in src
        i = src.index("_atk_scope = str(summary.get")
        j = src.index("head = (f\"{summary['attacker_name']} (lost ", i)
        assert j > i, "the scope must be resolved before the head line"

    def test_the_game_sets_it_on_a_coordinated_battle(self):
        """The row's premise, re-measured: the game does NOT disagree with
        itself — it labels the two figures (PT-D5), and the digest dropped
        the label."""
        import random
        random.seed(3)
        ney = MarshalFactory.infantry(name="Ney", location="Belgium", strength=30000,
                                      personality="aggressive")
        dav = MarshalFactory.infantry(name="Davout", location="Belgium", strength=25000,
                                      personality="cautious")
        mack = MarshalFactory.enemy(name="Mack", location="Waterloo", nation="Austria",
                                    strength=20000)
        world = _at_war(WorldFactory.with_marshals([ney, dav, mack]))
        ex = CommandExecutor()
        with _quiet():
            res = ex.execute({"command": {"type": "specific", "marshal": "Ney",
                                          "action": "attack", "target": "Mack"}},
                             {"world": world, "executor": ex})
        cs = ((res.get("battle_report") or {}).get("casualty_summary") or {})
        assert cs.get("attacker_casualties_scope") == "own corps", cs
        assert int(cs.get("attacker_casualties", 0)) > 0
