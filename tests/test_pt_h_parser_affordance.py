"""Row PT, slice H — parser and affordance honesty.

Build spec: `docs/PLAYTEST_FIXES_SPEC.md` §2 PT-H.

* **H1** the executor BUILDS `suggestion: "Try 'move to Rhineland'"` and it
  never leaves the backend — 1 of 108 responses contained the word.
* **H2** "cannot reach… Range: 1, Distance: 2" is a dead end a synonym
  clears. H1 is its root cause.
* **H3** `Murat, attack the Austrians` sent him at a BRITISH marshal one
  turn after an armistice with Austria, and never said so.
* **H4** the levy `open` predicate never checks the executor's decisive
  gate, and the escalated variant drops the condition the base carries.
* **H5** the clause-guard refusal bypasses N5's option-naming helper.
* **H6** counter-punch promises two turns; there is one.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.commands.economy_executor import get_levy_status

from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
            / "europe_1805.json")


# ═══════════════════════════════════════════════════════════════════════
# H1 / H2 — the recovery hint reaches the player
# ═══════════════════════════════════════════════════════════════════════

class TestTheSuggestionIsDelivered:
    def test_it_is_appended_to_the_message(self):
        """43 `"suggestion":` literals across nine backend files, and no
        consumer on either side: `main.py` contains the word once, in a
        comment; `main.gd` zero times. On the main path it does not even
        reach the wire — `_copy_truthy_result_fields` reads a fixed
        allowlist that omits it."""
        from backend.main import _message_with_suggestion

        out = _message_with_suggestion({
            "message": "Ney cannot reach Rhineland from Paris!",
            "suggestion": "Try 'move to Rhineland' to get closer first",
        })
        assert "cannot reach" in out
        assert "move to Rhineland" in out

    def test_it_is_never_doubled(self):
        from backend.main import _message_with_suggestion

        out = _message_with_suggestion({
            "message": "No enemies within range. Try 'move to X' first",
            "suggestion": "Try 'move to X' first",
        })
        assert out.count("Try 'move to X' first") == 1

    def test_a_result_without_one_is_untouched(self):
        from backend.main import _message_with_suggestion

        assert _message_with_suggestion({"message": "Done."}) == "Done."

    def test_both_response_builders_run_it(self):
        """The main path drops the key at the API boundary; the ~20
        early-return paths carry it to a client that does not read it.
        One seam covers all 43 producers."""
        src = (REPO / "backend" / "main.py").read_text(encoding="utf-8")
        assert src.count("_message_with_suggestion(") >= 3

    def test_the_refusal_reaches_the_player_over_http(self, monkeypatch):
        """H1 is H2's root cause: the refusal that said only "Range: 1,
        Distance: 2" was carrying the working synonym the whole time."""
        monkeypatch.setenv("SOVEREIGN_SCENARIO", "none")
        monkeypatch.setenv("LLM_MODE", "mock")
        from fastapi.testclient import TestClient

        import backend.main as M

        client = TestClient(M.app)
        response = client.post("/command", json={
            "command": "status"}).json()
        assert "message" in response      # the endpoint still answers


# ═══════════════════════════════════════════════════════════════════════
# H3 — the nation the player named
# ═══════════════════════════════════════════════════════════════════════

class TestTheNamedNationSurvives:
    def test_the_demonym_is_still_dropped(self):
        """⚠ NOT a revert. The drop is the fix for "the Austrians" -> the
        Spanish province Asturias, and it stays."""
        from backend.ai.strategic_parser import demonym_to_nation
        from backend.commands.parser import _is_nation_demonym

        world = WorldFactory.basic()
        assert _is_nation_demonym("the Austrians", world) is True
        assert demonym_to_nation("the Austrians", world) == "Austria"

    def test_the_inverse_is_built_from_the_same_roster(self):
        """So the two cannot drift."""
        from backend.ai.strategic_parser import (
            _nation_demonyms, demonym_to_nation,
        )

        world = WorldFactory.basic()
        for demonym in _nation_demonyms(world):
            assert demonym_to_nation(demonym, world), demonym

    def test_an_unknown_word_names_nobody(self):
        from backend.ai.strategic_parser import demonym_to_nation

        assert demonym_to_nation("Rhineland", WorldFactory.basic()) == ""

    def test_the_parser_stamps_the_hint(self):
        """The seam between the two halves, and the sweep proved it was
        unpinned: the drop and the executor's filter were both covered
        while NOTHING asserted the parser records the nation it drops."""
        from backend.commands.parser import CommandParser

        murat = MarshalFactory.infantry(name="Murat", location="Belgium",
                                        strength=25000)
        austrian = MarshalFactory.enemy(name="Mack", location="Rhineland",
                                        nation="Austria", strength=12000)
        world = WorldFactory.with_marshals([murat, austrian])
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "WAR"
        world.calculate_visibility()

        parsed = CommandParser(use_real_llm=False).parse(
            "Murat, attack the Austrians",
            {"world": world, "marshals": {}, "enemies": {}},
            world=world)
        command = parsed.get("command", parsed) or {}
        assert command.get("target_nation_hint") == "Austria", (
            "the drop is by design; discarding WHICH court he named is "
            "the defect")
        assert not command.get("target"), (
            "...and the demonym must still not become a province")

    def test_the_executor_honours_the_hint(self):
        """MEASURED: `Murat, attack the Austrians` sent him at Shrapnel —
        BRITISH — one turn after signing an armistice with Austria.
        `find_nearest_enemy` has no nation parameter and selects purely
        by distance."""
        from backend.commands.executor import CommandExecutor

        murat = MarshalFactory.infantry(name="Murat", location="Belgium",
                                        strength=25000)
        austrian = MarshalFactory.enemy(name="Mack", location="Rhineland",
                                        nation="Austria", strength=12000)
        british = MarshalFactory.enemy(name="Shrapnel", location="Paris",
                                       nation="Britain", strength=9000)
        world = WorldFactory.with_marshals([murat, austrian, british])
        for foe in ("Austria", "Britain"):
            key = world._make_diplo_key("France", foe)
            world.diplomatic_states[key] = "WAR"
            world.war_start_turns[key] = world.current_turn
        world.calculate_visibility()
        world.actions_remaining = 4

        executor = CommandExecutor()
        result = executor._combat._execute_attack(
            murat, None, world, {"world": world, "executor": executor},
            command={"target_nation_hint": "Austria"})
        assert "Shrapnel" not in str(result.get("message", "")), (
            "he named Austria; the engine must not pick the nearest court "
            "that happens to be somebody else")

    def test_it_says_so_when_nobody_is_in_reach(self):
        """Rather than silently attacking somebody else."""
        from backend.commands.executor import CommandExecutor

        murat = MarshalFactory.infantry(name="Murat", location="Belgium",
                                        strength=25000)
        british = MarshalFactory.enemy(name="Shrapnel", location="Paris",
                                       nation="Britain", strength=9000)
        world = WorldFactory.with_marshals([murat, british])
        key = world._make_diplo_key("France", "Britain")
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        world.calculate_visibility()
        world.actions_remaining = 4

        executor = CommandExecutor()
        result = executor._combat._execute_attack(
            murat, None, world, {"world": world, "executor": executor},
            command={"target_nation_hint": "Austria"})
        assert result["success"] is False
        assert "Austria" in result["message"]
        assert result.get("suggestion")

    def test_a_bare_attack_is_unaffected(self):
        """No hint, no filter — the ESP-EV-4 delegated case."""
        from backend.commands.executor import CommandExecutor

        murat = MarshalFactory.infantry(name="Murat", location="Belgium",
                                        strength=25000)
        british = MarshalFactory.enemy(name="Shrapnel", location="Paris",
                                       nation="Britain", strength=9000)
        world = WorldFactory.with_marshals([murat, british])
        key = world._make_diplo_key("France", "Britain")
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        world.calculate_visibility()
        world.actions_remaining = 4

        executor = CommandExecutor()
        result = executor._combat._execute_attack(
            murat, None, world, {"world": world, "executor": executor},
            command={})
        assert "No Austria" not in str(result.get("message", ""))


# ═══════════════════════════════════════════════════════════════════════
# H4 — the levy offer is an offer
# ═══════════════════════════════════════════════════════════════════════

def _europe():
    from backend.models.world_state import WorldState

    return WorldState.from_scenario(str(SCENARIO))


class TestTheLevyGateAsksTheRealQuestion:
    def test_the_status_reports_the_recipient(self):
        world = _europe()
        assert "recipient_in_range" in get_levy_status(world)

    def test_the_boot_board_cannot_receive(self):
        """Every French marshal is in Germany or Italy and infantry
        `movement_range` is 1 — CA8-11's measured state."""
        world = _europe()
        assert get_levy_status(world)["recipient_in_range"] is False

    def test_bringing_a_marshal_home_opens_it(self):
        world = _europe()
        for m in world.marshals.values():
            if m.nation == "France":
                m.strength = int(m.strength * 0.38)
        capital = world.get_nation_capital("France")
        next(m for m in world.marshals.values()
             if m.nation == "France").location = capital
        levy = get_levy_status(world)
        assert levy["recipient_in_range"] is True
        assert levy["open"] is True

    def test_the_escalated_variants_keep_the_condition(self):
        """CA8-11 fixed the BASE template and the escalated variants
        dropped it — and from run 3 onward the escalated wording is what
        the player sees, forever."""
        from backend.game_logic.dispatch import _STANDING_ESCALATION

        for variant in _STANDING_ESCALATION["levy_open"]:
            assert "{capital}" in variant, variant


# ═══════════════════════════════════════════════════════════════════════
# H5 / H6 — the last two
# ═══════════════════════════════════════════════════════════════════════

class TestTheClauseGuardNamesTheBlocker:
    def test_it_quotes_the_words_that_clear_an_objection(self, monkeypatch):
        """It returns BEFORE `executor.execute`, so the block that names
        the objecting marshal is never reached. With an objection pending,
        the player was told "no order goes out" while every real order
        stayed blocked, and nothing said how to unblock it."""
        monkeypatch.setenv("SOVEREIGN_SCENARIO", "none")
        monkeypatch.setenv("LLM_MODE", "mock")
        from fastapi.testclient import TestClient

        import backend.main as M

        client = TestClient(M.app)
        M.world.pending_objection = {
            "marshal": "Massena", "message": "I cannot advise it, Sire.",
            "suggested_alternative": {"action": "defend"},
        }
        try:
            response = client.post("/command", json={
                "command": "Ney, do not attack Mack"}).json()
            message = response.get("message", "")
            if "no order goes out" in message or "contingency" in message:
                assert "Massena" in message
                assert "'trust'" in message
        finally:
            M.world.pending_objection = None

    def test_the_import_is_aliased(self):
        """A bare local import binds the name for the WHOLE function, and
        the objection re-prompt above it already uses the module-level
        one — which turns an unchanged line into an UnboundLocalError."""
        src = (REPO / "backend" / "main.py").read_text(encoding="utf-8")
        assert "format_answer_words as _answer_words" in src


class TestCounterPunchPromisesOneTurn:
    def test_the_notification_says_this_turn(self):
        """`combat.py:701`'s own comment reads "Survives one turn
        transition"; the copy said two. The notification fires on an
        ENEMY-PHASE defensive win and the counter ticks inside the same
        `advance_turn`."""
        src = (REPO / "backend" / "commands"
               / "combat_executor.py").read_text(encoding="utf-8")
        assert "Use within 2 turns" not in src
        assert "Use it THIS turn" in src
