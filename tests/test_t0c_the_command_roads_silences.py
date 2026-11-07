"""T0-C "the command road's silences" — the third slice of Tier 0 of the
November 6, 2026 whole-game review (`docs/audits/GAME_REVIEW_2026_11_06.md`
§4.1 #7, #10, #11, #14, #23 and the harness rows; `BUG_FIXES.md` §GR GR-21 …
GR-32; the rules `SYSTEMS_REFERENCE.md` §180).

Every row is a sentence the game read wrong or answered in silence, measured
on a fresh shipped 1805 board through `POST /command` with the mock parser
(the CX-R1 harness): the verdict is the reply AND the state delta.

CMDFEEL-3  the objection's Trust arm offered an attack the executor refuses
           (a man on peace soil) — the alternative builder asks the executor's
           own predicate now (`field_is_barred`).
CMDFEEL-1  "march to <here> and attack Mack" spent 2 AP on a null march and
           never named the leg — refused free, the leg handed back as the
           order it is; a real march's reply says "On arrival he attacks …".
CMDFEEL-2  "take up a defensive position in Lorraine" dropped the province —
           the stance verb joins the stationary arms (refused by name, or the
           place disclosed).
CMDFEEL-4  a commander in the purpose clause hijacked a province named earlier.
CMDFEEL-5  "fortify everyone" / "Move everybody at Rhineland to Swabia" /
           "March Bernadotte to Dresden and …" / "hold ney".
CMDFEEL-6  "The Emperor's corps will move …" / "The Emperor orders …".
CMDFEEL-7  "bring the Army of Italy to Piedmont and hold the passes".
CMDFEEL-9  no War Purpose card for a declaration the fresh-peace floor refuses.
CMDFEEL-10 "recruit for Marmont" names its man.
CMDFEEL-15 "probe" and "appoint" read.
CMDFEEL-13 the driver refuses a script with an unknown top-level key.
CMDFEEL-14 a MARSHALS digest row a turn.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import backend.main as M  # noqa: E402
from backend.commands import disobedience as D  # noqa: E402
from backend.commands import group_orders as G  # noqa: E402
from backend.commands.combat_executor import war_purpose_bar  # noqa: E402
from backend.commands.economy_executor import unbound_levy_recipient  # noqa: E402
from backend.commands.parser import CommandParser, normalize_sovereign_address  # noqa: E402

DRIVER = REPO / "tools" / "playtest_driver.py"


# ═══════════════════════════════════════════════════════════════════════════
# Harness — a fresh SHIPPED 1805 board per test, the mock parser, POST /command.
# ═══════════════════════════════════════════════════════════════════════════
@pytest.fixture
def board(monkeypatch, tmp_path):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path / "saves"))
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False, "a probe must never pay"
    return TestClient(M.app)


def _post(client, text):
    return client.post("/command", json={"command": text}).json()


def _parse(text):
    return M.parser.parse(text, M.get_llm_game_state(), world=M.world)


def _ap(world):
    return (world.actions_remaining, world.admin_actions_remaining)


def _load_driver(name):
    spec = importlib.util.spec_from_file_location(name, str(DRIVER))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ═══════════════════════════════════════════════════════════════════════════
# CMDFEEL-3 (GR-23) — the alternative passes the executor's own permission.
# ═══════════════════════════════════════════════════════════════════════════
def _peace_soil(world, soil="Austria"):
    """France at peace with Austria; Frankfurt (beside Ney at Rhineland) made
    `soil`; Kutuzov (Russia, at war with France) standing on it, in sight."""
    world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "PEACE"
    world.get_region("Frankfurt").controller = soil
    kutuzov = world.marshals["Kutuzov"]
    kutuzov.location = "Frankfurt"
    kutuzov.strength = 38000
    world.calculate_visibility()
    return world.marshals["Ney"], kutuzov


class TestTheAlternativePassesTheExecutorsPermission:
    """CMDFEEL-3 (GR-23): "Trust him and he will attack Kutuzov at Carniola"
    on a board at peace with Austria — the same attack typed was refused."""

    def test_the_predicate_is_the_executors(self, board):
        ney, kutuzov = _peace_soil(M.world)
        assert D.field_is_barred(M.world, ney, "Frankfurt", kutuzov), "peace soil bars the field"
        M.world.get_region("Frankfurt").controller = "Russia"
        assert not D.field_is_barred(M.world, ney, "Frankfurt", kutuzov), "the enemy's own soil is open"

    def test_a_man_on_peace_soil_is_not_in_range(self, board):
        ney, kutuzov = _peace_soil(M.world)
        assert kutuzov.name not in {m.name for m in D.get_enemies_in_range(ney, M.world)}
        M.world.get_region("Frankfurt").controller = "Russia"
        assert kutuzov.name in {m.name for m in D.get_enemies_in_range(ney, M.world)}

    def test_the_suggestion_is_vetted(self, board):
        ney, kutuzov = _peace_soil(M.world)
        attack = {"action": "attack", "target": kutuzov.name}
        assert D._can_execute_suggestion(ney, attack, M.world) is False
        M.world.get_region("Frankfurt").controller = "Russia"
        assert D._can_execute_suggestion(ney, attack, M.world) is True

    def test_the_aggressive_chain_never_offers_the_field(self, board):
        ney, kutuzov = _peace_soil(M.world)
        preferred = D._get_aggressive_preferred(ney, M.world) or {}
        assert not (preferred.get("action") == "attack" and preferred.get("target") == kutuzov.name)
        alt = M.world.disobedience_system._generate_alternative(
            ney, {"action": "retreat", "target": None}, M.world) or {}
        assert not (alt.get("action") == "attack" and alt.get("target") == kutuzov.name), alt

    def test_the_same_man_on_his_own_soil_is_the_offer(self, board):
        ney, kutuzov = _peace_soil(M.world, soil="Russia")
        preferred = D._get_aggressive_preferred(ney, M.world) or {}
        assert preferred == {"action": "attack", "target": kutuzov.name}, preferred

    def test_the_ai_keeps_pt_f1(self, board):
        """The AI's lead keeps PT-F1 (a field on a third party's soil is legal
        for it): the predicate answers False for a court's marshal."""
        _ney, kutuzov = _peace_soil(M.world)
        mack = M.world.marshals["Mack"]
        assert not D.field_is_barred(M.world, mack, "Frankfurt", kutuzov)


# ═══════════════════════════════════════════════════════════════════════════
# CMDFEEL-1 (GR-21) — the null march with an attack leg.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheNullMarchWithAnAttackLeg:

    def test_a_march_to_his_own_province_with_a_leg_is_refused_free(self, board):
        lannes = M.world.marshals["Lannes"]
        assert lannes.location == "Franche-Comte"
        before = _ap(M.world)
        resp = _post(board, "Lannes, march to Franche-Comte and attack Mack")
        assert resp["success"] is False
        assert "already stands at Franche-Comte" in resp["message"]
        assert "'Lannes, pursue Mack'" in resp["message"], resp["message"]
        assert resp.get("remedy_command") == "Lannes, pursue Mack"
        assert _ap(M.world) == before, "nothing spent"
        assert lannes.strategic_order is None, "no null march stands"

    def test_a_bare_leg_with_nobody_there_says_so(self, board):
        before = _ap(M.world)
        resp = _post(board, "Lannes, march to Franche-Comte then attack")
        assert resp["success"] is False
        assert "No enemy stands there to attack" in resp["message"], resp["message"]
        assert _ap(M.world) == before
        assert M.world.marshals["Lannes"].strategic_order is None

    def test_the_plain_null_march_is_unchanged(self, board):
        resp = _post(board, "Lannes, march to Franche-Comte")
        assert resp["success"] is False
        assert resp["message"].startswith("Lannes already stands at Franche-Comte")
        assert "remedy_command" not in resp or not resp.get("remedy_command")

    def test_a_real_march_names_its_second_leg(self, board):
        resp = _post(board, "Lannes, march to Paris, then attack Mack")
        assert resp["success"] is True
        assert "On arrival he attacks Mack." in resp["message"], resp["message"]
        order = M.world.marshals["Lannes"].strategic_order
        assert order is not None and order.attack_on_arrival and order.arrival_target == "Mack"

    def test_a_real_march_with_an_arrival_verb_names_it(self, board):
        resp = _post(board, "Lannes, march to Paris then fortify")
        assert resp["success"] is True
        assert "On arrival he fortifies." in resp["message"], resp["message"]

    def test_a_plain_march_carries_no_leg_clause(self, board):
        resp = _post(board, "Lannes, march to Paris")
        assert resp["success"] is True
        assert "On arrival he" not in resp["message"], resp["message"]


# ═══════════════════════════════════════════════════════════════════════════
# CMDFEEL-2 (GR-22) — the stance verb with a place.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheStanceVerbWithAPlace:

    def test_the_place_he_stands_in_is_disclosed(self, board):
        napoleon = M.world.marshals["Napoleon"]
        assert napoleon.location == "Lorraine"
        resp = _post(board, "Napoleon, take up a defensive position in Lorraine")
        assert resp["success"] is True
        assert "DEFENSIVE stance at Lorraine" in resp["message"], resp["message"]
        assert str(napoleon.stance.value).lower() == "defensive"

    def test_another_place_is_refused_by_name_as_defend_is(self, board):
        napoleon = M.world.marshals["Napoleon"]
        napoleon.location = "Paris"
        before, stance = _ap(M.world), napoleon.stance
        resp = _post(board, "Napoleon, take up a defensive position in Lorraine")
        assert resp["success"] is False
        assert "stands at Paris, not Lorraine" in resp["message"], resp["message"]
        assert "a stance is taken where the corps stands" in resp["message"]
        assert "'Napoleon, defensive stance' to take it at Paris" in resp["message"]
        assert _ap(M.world) == before and napoleon.stance == stance
        defend = _post(board, "Napoleon, defend Lorraine")
        assert defend["success"] is False and "stands at Paris, not Lorraine" in defend["message"]

    def test_a_stance_without_a_place_is_untouched(self, board):
        resp = _post(board, "Ney, aggressive stance")
        assert resp["success"] is True
        assert " at " not in resp["message"].split("Effect:")[0]
        assert str(M.world.marshals["Ney"].stance.value).lower() == "aggressive"

    def test_the_arm_is_stationary(self):
        from backend.commands.exit_predicate import STATIONARY_ARMS
        assert "stance_change" in STATIONARY_ARMS


# ═══════════════════════════════════════════════════════════════════════════
# CMDFEEL-4 (GR-24) — a province named first leads.
# ═══════════════════════════════════════════════════════════════════════════
class TestAProvinceNamedFirstLeads:

    @pytest.mark.parametrize("line, marshal, action, place", [
        ("Murat, ride for Swabia and find Mack's flank.", "Murat", "move", "Swabia"),
        ("Massena, send patrols into Tyrol and report John's strength.", "Massena", "scout", "Tyrol"),
        ("Transfer Bernadotte to Tyrol to threaten John", "Bernadotte", "move", "Tyrol"),
        ("Soult will push patrols toward Swabia to fix Mack's position", "Soult", "scout", "Swabia"),
        ("Bernadotte goes to Swabia and falls on Mack's rear", "Bernadotte", "move", "Swabia"),
        ("Murat is to probe Swabia and count Mack's guns.", "Murat", "scout", "Swabia"),
    ])
    def test_the_province_keeps_the_slot(self, board, line, marshal, action, place):
        parsed = _parse(line)
        assert parsed["success"], parsed
        cmd = parsed["command"]
        assert (cmd["marshal"], cmd["action"], cmd["target"]) == (marshal, action, place), cmd

    def test_the_reply_is_the_boards_not_a_lecture(self, board):
        resp = _post(board, "Murat, ride for Swabia and find Mack's flank.")
        assert "is a commander" not in resp["message"], resp["message"]

    def test_a_commander_named_first_keeps_the_slot(self, board):
        cmd = _parse("Murat, scout Mack at Swabia")["command"]
        assert cmd["target"] == "Mack"

    def test_an_attack_is_not_touched(self, board):
        cmd = _parse("Ney, attack Mack at Swabia")["command"]
        assert (cmd["action"], cmd["target"]) == ("attack", "Mack")


# ═══════════════════════════════════════════════════════════════════════════
# CMDFEEL-5 (GR-25) — the army named after the verb; roles kept.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheArmyNamedAfterTheVerb:

    def test_fortify_everyone_fans_out(self, board):
        resp = _post(board, "fortify everyone")
        assert resp.get("clarification_kind") != "marshal_choice"
        assert resp["message"].startswith("The order goes to the army, corps by corps"), resp["message"]
        assert "'fortify'" in resp["message"]

    def test_the_corps_at_a_place_alone(self, board):
        at = [m.name for m in M.world.marshals.values()
              if m.nation == "France" and m.location == "Rhineland"]
        assert len(at) >= 2
        resp = _post(board, "Move everybody at Rhineland to Swabia.")
        assert resp.get("clarification_kind") != "marshal_choice"
        assert "the corps at Rhineland" in resp["message"], resp["message"]
        assert f"{len(at)} corps" in resp["message"]
        for name in at:
            assert f"{name}:" in resp["message"] or f"{name} " in resp["message"], resp["message"]
        elsewhere = [m.name for m in M.world.marshals.values()
                     if m.nation == "France" and m.location != "Rhineland"]
        assert elsewhere and not any(f"{name}:" in resp["message"] for name in elsewhere), resp["message"]

    def test_the_relative_clause_reads_the_same(self, board):
        resp = _post(board, "Everybody who is at Rhineland goes to Swabia")
        assert "the corps at Rhineland" in resp["message"], resp["message"]

    def test_a_place_with_no_corps_says_so(self, board):
        assert not [m for m in M.world.marshals.values() if m.nation == "France" and m.location == "Paris"]
        before = _ap(M.world)
        resp = _post(board, "Move everybody at Paris to Lorraine")
        assert resp["success"] is False
        assert "No corps of ours stands at Paris" in resp["message"], resp["message"]
        assert _ap(M.world) == before

    def test_march_everyone_to_a_province(self, board):
        resp = _post(board, "march everyone to Swabia")
        assert "Region 'Everyone' not found" not in resp["message"]
        assert resp["message"].startswith("The order goes to the army"), resp["message"]

    def test_the_marshal_sent_and_his_tail(self, board):
        cmd = _parse("March Bernadotte to Dresden and let the Elector see French bayonets.")["command"]
        assert (cmd["marshal"], cmd["action"], cmd["target"]) == ("Bernadotte", "move", "Dresden"), cmd
        resp = _post(board, "March Bernadotte to Dresden and let the Elector see French bayonets.")
        assert resp.get("clarification_kind") != "marshal_choice"
        assert "Bernadotte" not in (resp.get("message") or "").split("march to")[-1][:12]

    def test_hold_ney_is_neys_hold(self, board):
        resp = _post(board, "hold ney")
        assert resp.get("clarification_kind") != "marshal_choice"
        assert resp["success"] is True
        assert resp["message"].startswith("Ney will hold Rhineland"), resp["message"]

    @pytest.mark.parametrize("line, who, rest, at", [
        ("fortify everyone", "everyone", "fortify", None),
        ("march everyone to Swabia", "everyone", "march to Swabia", None),
        ("Move everybody at Rhineland to Swabia.", "everybody", "Move to Swabia.", "Rhineland"),
        ("Everybody who is at Rhineland goes to Swabia", "Everybody", "go to Swabia", "Rhineland"),
        ("everyone fortify", "everyone", "fortify", None),
        ("the army marches on Swabia", "army", "march to Swabia", None),
    ])
    def test_the_head_reader(self, line, who, rest, at):
        head = G.collective_head(line, places=["Rhineland", "Swabia", "East Prussia"])
        assert head is not None, line
        assert head["who"].lower() == who.lower() and head["rest"] == rest, head
        assert head.get("at") == at

    @pytest.mark.parametrize("line", [
        "take all the guns to Swabia",
        "Ney, attack Mack",
        "send Ney to Swabia",
    ])
    def test_not_a_collective(self, line):
        assert G.collective_head(line, places=["Swabia"]) is None

    def test_a_two_word_place(self):
        head = G.collective_head("move everyone at East Prussia to Berlin", places=["East Prussia", "Berlin"])
        assert head and head["at"] == "East Prussia" and head["rest"] == "move to Berlin"


# ═══════════════════════════════════════════════════════════════════════════
# CMDFEEL-6 (GR-26) — the Emperor in subject position.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheEmperorInSubjectPosition:

    @pytest.mark.parametrize("line, want", [
        ("The Emperor's corps will move to Orleanais.", "Napoleon, move to Orleanais."),
        ("the Emperor's guard marches to Swabia", "Napoleon, marches to Swabia"),
        ("The Emperor orders a general attack on Swabia.", "Napoleon, general attack on Swabia."),
        ("the Emperor orders Ney to attack Mack", "order Ney to attack Mack"),
        ("the Emperor will march to Swabia", "Napoleon, march to Swabia"),
    ])
    def test_rewritten(self, line, want):
        assert normalize_sovereign_address(line, "Napoleon") == want

    @pytest.mark.parametrize("line", [
        "The Emperor's corps is exhausted",
        "the Emperor orders his dinner",
        "the Emperor of Austria demands Venetia",
        "the Emperor is displeased",
        "Ney, support the Emperor",
    ])
    def test_untouched(self, line):
        assert normalize_sovereign_address(line, "Napoleon") == line

    def test_end_to_end_the_possessive_marches_him(self, board):
        resp = _post(board, "The Emperor's corps will move to Orleanais.")
        assert resp.get("clarification_kind") != "unknown_name"
        assert resp["success"] is True, resp["message"]
        assert M.world.marshals["Napoleon"].location == "Orleanais"

    def test_end_to_end_the_narration_verb_is_his_order(self, board):
        cmd = _parse("The Emperor orders a general attack on Swabia.")["command"]
        assert (cmd["marshal"], cmd["action"], cmd["target"]) == ("Napoleon", "attack", "Swabia"), cmd


# ═══════════════════════════════════════════════════════════════════════════
# CMDFEEL-7 (GR-27) — the march with a terrain hold.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheMarchWithATerrainHold:

    def test_the_sentence_is_a_march_that_holds_on_arrival(self, board):
        parsed = _parse("Massena, bring the Army of Italy to Piedmont and hold the passes.")
        assert parsed["success"] and parsed.get("is_strategic"), parsed
        assert parsed["strategic_type"] == "MOVE_TO"
        assert parsed["command"]["target"] == "Piedmont"
        assert parsed.get("arrival_verb") == "hold" or parsed["command"].get("arrival_verb") == "hold", parsed

    def test_end_to_end_the_piedmont_leg_is_relayed(self, board):
        resp = _post(board, "Massena, bring the Army of Italy to Piedmont and hold the passes.")
        assert resp["success"] is True, resp["message"]
        assert "Region 'Passes' not found" not in resp["message"]
        assert "begins march to Piedmont" in resp["message"], resp["message"]
        assert "holds" in resp["message"], resp["message"]

    def test_a_bare_hold_on_a_terrain_noun_is_answered_as_terrain(self, board):
        before = _ap(M.world)
        resp = _post(board, "Ney, hold the passes")
        assert resp["success"] is False
        assert "Did you mean" not in resp["message"], resp["message"]
        assert "The map knows no passes by that name" in resp["message"], resp["message"]
        assert _ap(M.world) == before

    @pytest.mark.parametrize("tail, fuses", [
        ("hold the passes", True), ("hold the heights.", True), ("fortify the bridge", True),
        ("hold it", True), ("hold Bavaria", False), ("hold the line of the Danube", False),
    ])
    def test_the_arrival_tail(self, tail, fuses):
        from backend.ai.strategic_parser import ARRIVAL_VERB_TAIL_RE
        assert bool(ARRIVAL_VERB_TAIL_RE.match(tail)) is fuses


# ═══════════════════════════════════════════════════════════════════════════
# CMDFEEL-9 (GR-28) — no War Purpose card under the fresh-peace floor.
# ═══════════════════════════════════════════════════════════════════════════
def _austrian_nassau(world, cooldown):
    world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "PEACE"
    if cooldown:
        world.armistice_cooldowns[world._make_diplo_key("France", "Austria")] = cooldown
    nassau = world.get_region("Nassau")
    nassau.controller = "Austria"
    nassau.garrison_strength = 0
    for m in world.marshals.values():
        if m.location == "Nassau":
            m.location = "Bohemia"
    world.calculate_visibility()


class TestTheWarPurposeBar:

    def test_the_bar_is_the_cooldowns_words(self, board):
        _austrian_nassau(M.world, 4)
        bar = war_purpose_bar(M.world, "France", "Austria")
        assert bar.startswith("Our peace with Austria is fresh") and "4 more turns" in bar, bar
        assert war_purpose_bar(M.world, "France", "Prussia") == ""
        assert war_purpose_bar(M.world, "France", "France") == ""

    def test_an_attack_under_the_floor_is_refused_once_and_free(self, board):
        _austrian_nassau(M.world, 4)
        before = _ap(M.world)
        resp = _post(board, "Ney, attack Nassau")
        assert resp["success"] is False, resp["message"]
        assert "our peace with Austria is fresh" in resp["message"], resp["message"]
        assert "4 more turns" in resp["message"]
        assert not resp.get("war_purpose_popup")
        assert M.world.dialogue_manager.peek() is None, "no card staged"
        assert _ap(M.world) == before

    def test_without_the_floor_the_card_is_staged(self, board):
        _austrian_nassau(M.world, 0)
        resp = _post(board, "Ney, attack Nassau")
        assert resp.get("war_purpose_popup") or (
            (M.world.dialogue_manager.peek() or {}).get("type") == "war_purpose_selection"), resp

    def test_every_staging_site_reads_the_bar(self):
        source = (REPO / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        assert source.count("self._stage_or_bar_war_purpose(") == 3, "the three pursuit-capture sites"
        attack_site = source[source.index("def _stage_war_purpose_for_attack"):][:900]
        assert "war_purpose_bar(" in attack_site, "the attack site reads the bar first"
        # the card itself is staged from the attack site and the one helper alone
        assert source.count("self._stage_war_purpose_selection(") == 2

    def test_the_helper_bars_or_stages(self, board):
        from backend.commands.executor import CommandExecutor
        _austrian_nassau(M.world, 3)
        block = {"arm": "neutral", "owner": "Austria", "message": " x"}
        combat = CommandExecutor()._combat
        staged, clause = combat._stage_or_bar_war_purpose(M.world, "France", block, "Nassau")
        assert staged is None and clause.startswith(" To seize Nassau is to make war on Austria — and our peace")
        assert clause.endswith("The province stands.") and M.world.dialogue_manager.peek() is None
        M.world.armistice_cooldowns.clear()
        staged, clause = combat._stage_or_bar_war_purpose(M.world, "France", block)
        assert staged and staged["target_nation"] == "Austria"
        assert clause == " To seize it is to make war on Austria — choose our purpose, or let the province stand."
        assert (M.world.dialogue_manager.peek() or {}).get("type") == "war_purpose_selection"


# ═══════════════════════════════════════════════════════════════════════════
# CMDFEEL-10 (GR-29) — the levy names its man.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheLevyNamesItsMan:

    def test_a_man_on_the_bench(self, board):
        before = _ap(M.world)
        resp = _post(board, "recruit for Marmont")
        assert resp["success"] is False
        assert resp["message"].startswith("Marmont is not in your order of battle"), resp["message"]
        assert "commission Marmont" in resp["message"]
        assert resp.get("remedy_command") == "commission Marmont"
        assert _ap(M.world) == before

    def test_a_name_nobody_has(self, board):
        resp = _post(board, "recruit for Zorblax")
        assert resp["success"] is False
        assert resp["message"] == "There is no 'Zorblax' in the order of battle, Sire. Whom did you intend?"

    def test_a_roster_name_keeps_its_road(self, board):
        resp = _post(board, "recruit for Ney")
        assert "order of battle" not in (resp.get("message") or "")

    def test_a_common_noun_falls_through(self, board):
        resp = _post(board, "recruit for the campaign")
        assert "order of battle" not in (resp.get("message") or "")

    def test_the_reader(self, board):
        w = M.world
        assert unbound_levy_recipient(w, "recruit for Marmont") == {"name": "Marmont", "on_the_bench": True}
        assert unbound_levy_recipient(w, "recruit for marmont") == {"name": "Marmont", "on_the_bench": True}
        assert unbound_levy_recipient(w, "recruit for Zorblax") == {"name": "Zorblax", "on_the_bench": False}
        assert unbound_levy_recipient(w, "recruit for Ney") is None
        assert unbound_levy_recipient(w, "recruit for Davout's corps") is None
        assert unbound_levy_recipient(w, "recruit for Marmont's corps") == {"name": "Marmont", "on_the_bench": True}
        assert unbound_levy_recipient(w, "recruit infantry for the Guard") is None
        assert unbound_levy_recipient(w, "recruit to full strength") is None
        assert unbound_levy_recipient(w, "recruit in Lorraine for Austria") is None


# ═══════════════════════════════════════════════════════════════════════════
# CMDFEEL-15 (GR-32) — "probe" and "appoint" read.
# ═══════════════════════════════════════════════════════════════════════════
class TestProbeAndAppoint:

    def test_probe_is_the_scout(self, board):
        cmd = _parse("Massena, probe Piedmont for any Austrian movement.")["command"]
        assert (cmd["marshal"], cmd["action"], cmd["target"]) == ("Massena", "scout", "Piedmont"), cmd

    def test_appoint_is_the_commission(self, board):
        cmd = _parse("appoint Mortier")["command"]
        assert (cmd["action"], cmd["target"]) == ("recruit_marshal", "Mortier"), cmd
        resp = _post(board, "berthier appoint mortier")
        assert "Mortier" in resp["message"] and "cannot" not in resp["message"].lower()[:40], resp["message"]

    def test_the_routed_words_know_them(self):
        from backend.ai.routed_order_words import ROUTED_ORDER_WORDS
        assert {"probe", "appoint"} <= set(ROUTED_ORDER_WORDS)


# ═══════════════════════════════════════════════════════════════════════════
# CMDFEEL-13 (GR-30) — the driver refuses a script with an unknown key.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheDriverRefusesAnUnknownKey:

    def test_the_reader(self):
        drv = _load_driver("playtest_driver_t0c_keys")
        assert drv.unknown_script_keys({"name": "x", "_note": "n", "orders": [], "questions": []}) == ["orders", "questions"]
        assert drv.unknown_script_keys({"name": "x", "seed": "historical", "llm": "mock", "turns": {},
                                        "policy": {}, "policy_at": {}, "preconditions": {}, "scenario": ""}) == []
        assert drv.unknown_script_keys({"name": "x", "turns": {}, "dl_lines": [], "clicks": [], "doors": [], "hold": {}}) == []
        assert drv.unknown_script_keys([]) == ["<not an object>"]

    def test_every_committed_driver_script_is_read_and_every_census_file_refused(self):
        drv = _load_driver("playtest_driver_t0c_scripts")
        refused = {}
        for path in sorted((REPO / "tools" / "playtest_scripts").glob("*.json")):
            bad = drv.unknown_script_keys(json.loads(path.read_text(encoding="utf-8")))
            if bad:
                refused[path.name] = bad
        assert refused, "the blind census files carry 'orders'"
        assert all(name.startswith("unrehearsed_") for name in refused), refused
        assert all("orders" in bad for bad in refused.values()), refused

    def test_run_refuses_before_it_boots(self, tmp_path, capsys):
        import argparse
        drv = _load_driver("playtest_driver_t0c_run")
        script = tmp_path / "blind.json"
        script.write_text(json.dumps({"name": "blind", "_note": "a census file", "orders": [{"line": "Ney, attack Mack"}]}),
                          encoding="utf-8")
        ns = argparse.Namespace(script=str(script), turns=10)
        assert drv.run(ns) == 2
        err = capsys.readouterr().err
        assert "'orders'" in err and "10 empty turns" in err and "unrehearsed_census" in err, err


# ═══════════════════════════════════════════════════════════════════════════
# CMDFEEL-14 (GR-31) — the digest sees the marshals.
# ═══════════════════════════════════════════════════════════════════════════
class _Recorder:
    """Borrows the real Digest's method (the stub-Digest idiom)."""

    def __init__(self, drv):
        self.lines, self.records = [], []
        self.marshals_line = drv.Digest.marshals_line.__get__(self, _Recorder)

    def _md(self, line):
        self.lines.append(line)

    def record(self, kind, **fields):
        self.records.append({"kind": kind} | fields)


class TestTheDigestSeesTheMarshals:

    def test_the_row(self):
        drv = _load_driver("playtest_driver_t0c_row")
        r = _Recorder(drv)
        r.marshals_line([
            {"name": "Ney", "trust": 40, "label": "Strained", "vindication": 0, "pending": False,
             "glory": 12, "rank": 1, "jealous_of": "", "captured": False},
            {"name": "Murat", "trust": 65, "label": "Loyal", "vindication": 2, "pending": True,
             "glory": 3, "rank": 4, "jealous_of": "Ney", "captured": False},
            {"name": "Lannes", "trust": 50, "label": "Steady", "vindication": 0, "pending": False,
             "glory": 0, "rank": 0, "jealous_of": "", "captured": True},
        ])
        assert r.lines == ["- MARSHALS Ney trust 40 Strained glory 12 (#1) · "
                           "Murat trust 65 Loyal glory 3 (#4) vind +2 vind pending envies Ney · "
                           "Lannes captured"]
        assert r.records[0]["kind"] == "marshals"
        assert r.records[0]["marshals"]["Murat"]["trust"] == 65
        assert r.records[0]["marshals"]["Lannes"]["captured"] is True

    def test_none_prints_nothing_and_an_empty_board_prints_none(self):
        drv = _load_driver("playtest_driver_t0c_none")
        r = _Recorder(drv)
        r.marshals_line(None)
        assert r.lines == [] and r.records == []
        r.marshals_line([])
        assert r.lines == ["- MARSHALS none"]

    def test_the_reader_is_the_cards_own_figures(self, board):
        drv = _load_driver("playtest_driver_t0c_reader")

        class _Transport:
            def get(self, path):
                return board.get(path).json()

        rows = drv._marshal_standing(_Transport())
        assert rows and {row["name"] for row in rows} == {
            m.name for m in M.world.marshals.values() if m.nation == "France"}
        ney = next(row for row in rows if row["name"] == "Ney")
        assert ney["trust"] == int(M.world.marshals["Ney"].trust.value)
        assert ney["label"] == M.world.marshals["Ney"].trust.get_label()
        assert set(ney) == {"name"} | set(drv._MARSHAL_STANDING_KEYS)

    def test_a_failed_read_is_none(self):
        drv = _load_driver("playtest_driver_t0c_fail")

        class _Broken:
            def get(self, path):
                raise RuntimeError("down")

        assert drv._marshal_standing(_Broken()) is None

    def test_it_is_sited_in_the_loop_after_the_ledger_and_gated(self):
        source = DRIVER.read_text(encoding="utf-8")
        ledger_at = source.index("digest.ledger_line(dig(ledger")
        row_at = source.index("digest.marshals_line(_marshal_standing(transport)")
        assert 0 < row_at - ledger_at < 2500
        assert "if THE_DIGEST_SEES_THE_MARSHALS else None" in source
        drv = _load_driver("playtest_driver_t0c_lever")
        assert drv.THE_DIGEST_SEES_THE_MARSHALS is True


# ═══════════════════════════════════════════════════════════════════════════
# The slice's hygiene — nothing here changes a mechanic the series reads.
# ═══════════════════════════════════════════════════════════════════════════
def test_the_arrival_object_list_is_the_terrain_list():
    from backend.ai.strategic_parser import UNMAPPED_TERRAIN_NOUNS, _ARRIVAL_VERB_OBJECTS
    for noun in UNMAPPED_TERRAIN_NOUNS:
        assert re.search(r"\b" + re.escape(noun) + r"\b", _ARRIVAL_VERB_OBJECTS), noun
