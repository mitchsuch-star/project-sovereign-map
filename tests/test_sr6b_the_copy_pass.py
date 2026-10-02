"""SR-6b "The copy pass" (Score Finish Step 2, October 2, 2026).

RS-18 the voiced summary fills its two slots · RS-21 the warning names its
component and consent drops it · RS-22 one court to press · RS-25 the System
names its condition · RS-26 / NPC-12 the field speaks display names · RS-29
the support order and the court's own rank · NPC-23 the serial join ·
NPC-24 the famine's dead · NP-X6 the sovereign's card · NP-X7 the honorific
· SRX-6 / SF-V2 the white peace's own blocker and header · WO-D11's copy.
"""
import contextlib
import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import display_names as DN
from backend.commands import strategic as ST
from backend.commands.parser import CommandParser
from backend.game_logic import combat as CB
from backend.game_logic import congress as CG
from backend.game_logic import diplomacy as D
from backend.game_logic import diplomatic_templates as DT
from backend.game_logic import dispatch
from backend.game_logic import reforms
from backend.game_logic import settlement_presentation as SP
from backend.game_logic import settlement_staging as SG
from backend.game_logic.settlement_staging import (build_settlement_preview,
                                                   stage_settlement_confirm)
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCEN = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
           / "europe_1805.json")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture
def world():
    with _quiet():
        return WorldState.from_scenario(SCEN)


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


# ═══════════════════════════════════════════════════════════════════════════
# RS-18 — the voiced summary's two slots
# ═══════════════════════════════════════════════════════════════════════════

def _event(**over):
    base = {
        "type": "settlement_summary", "war_id": "war_1",
        "war_label": "France vs Austria", "proposer_side": "defenders",
        "proposer_members": ["France"], "proposer_leader": "France",
        "accepting_members": ["Austria"],
        "terms_summary": ["Gold indemnity: 100 gold from France to Austria"],
        "applied_clauses": [
            {"type": "gold_indemnity", "from": "France", "to": "Austria", "amount": 100}],
        "participant_reactions": [{"nation": "Austria", "reaction": "accepts"}],
    }
    base.update(over)
    return base


class TestTheSummaryFillsItsSlots:

    def test_a_clause_received_and_one_paid(self):
        line = SP.compose_summary_oneliner(_event(applied_clauses=[
            {"type": "gold_indemnity", "from": "France", "to": "Austria", "amount": 100},
            {"type": "territory_cede", "from": "Austria", "to": "France", "region": "Tyrol"}]))
        assert "Returning " in line and "steadies the coalition" in line
        received, paid = SP._summary_slots(_event(applied_clauses=[
            {"type": "gold_indemnity", "from": "France", "to": "Austria", "amount": 100},
            {"type": "territory_cede", "from": "Austria", "to": "France", "region": "Tyrol"}]))
        assert "Tyrol" in received and "100 gold" in paid
        assert received in line and paid in line
        assert line.count("100 gold") == 1

    def test_a_payment_alone_is_never_voiced_as_a_return(self):
        line = SP.compose_summary_oneliner(_event())
        assert "Returning" not in line, line
        assert "accounting" in line        # the common-peace register

    def test_lever_down_fills_both_slots_with_the_head_term(self, monkeypatch):
        monkeypatch.setattr(SP, "THE_SUMMARY_FILLS_ITS_SLOTS", False)
        line = SP.compose_summary_oneliner(_event())
        assert line.count("100 gold") == 2 and "Returning" in line


# ═══════════════════════════════════════════════════════════════════════════
# RS-21 — the warning names its component; consent drops it
# ═══════════════════════════════════════════════════════════════════════════

class TestTheWarningNamesItsComponent:

    def test_the_display_and_the_sign(self):
        row = SP._enrich_warning_row({"category": "acceptance_component",
                                      "component": "settlement_tier_legitimacy",
                                      "value": -8})
        assert row["detail"] == f"{DN.acceptance_component_display('settlement_tier_legitimacy')} (-8)"
        assert "Tier" not in row["detail"]
        row = SP._enrich_warning_row({"category": "acceptance_component",
                                      "component": "agenda_settlement_mod", "value": 12})
        assert row["detail"] == f"{DN.acceptance_component_display('agenda_settlement_mod')} (+12)"

    def test_lever_down_title_cases_the_key(self, monkeypatch):
        monkeypatch.setattr(SP, "THE_WARNING_NAMES_ITS_COMPONENT", False)
        row = SP._enrich_warning_row({"category": "acceptance_component",
                                      "component": "settlement_tier_legitimacy", "value": -8})
        assert row["detail"] == "Settlement Tier Legitimacy"

    def test_consent_drops_the_acceptance_concerns(self, world):
        terms = [{"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 100}]
        with _quiet():
            plain = build_settlement_preview(world, war_id="war_1", settlement_terms=terms,
                                             covered_enemy_participants=["Austria"])
            consented = build_settlement_preview(world, war_id="war_1", settlement_terms=terms,
                                                 covered_enemy_participants=["Austria"],
                                                 consenting_courts=["Austria"])
        plain = plain["settlement_preview"]
        consented = consented["settlement_preview"]
        assert any(w.get("category") == "acceptance_component" for w in plain["warnings"])
        assert not any(w.get("category") == "acceptance_component" for w in consented["warnings"])
        assert any(w.get("category") == "acceptance_component"
                   for w in consented["warnings_before_consent"])


# ═══════════════════════════════════════════════════════════════════════════
# RS-22 — one court to press
# ═══════════════════════════════════════════════════════════════════════════

def _rows():
    return [{"nation": "Austria", "total": 60, "threshold": 50},
            {"nation": "Russia", "total": 55, "threshold": 50},
            {"nation": "Britain", "total": 20, "threshold": 50}]


class TestOneCourtToPress:

    def test_one_named_the_others_apiece(self, world):
        line = SG.legitimacy_sentence(world, _rows(), ["Britain"], 50)
        assert "Press Austria alone: the separate peace." in line, line
        assert "The others — Russia — can each be treated with alone, at" in line
        assert "apiece" in line
        assert "Press Austria and Russia alone" not in line

    def test_lever_down_joins_them(self, world, monkeypatch):
        monkeypatch.setattr(SG, "THE_HINT_PRESSES_ONE_COURT", False)
        line = SG.legitimacy_sentence(world, _rows(), ["Britain"], 50)
        assert "Press Austria and Russia alone: the separate peace." in line
        assert "apiece" not in line


# ═══════════════════════════════════════════════════════════════════════════
# RS-25 — the System names its condition
# ═══════════════════════════════════════════════════════════════════════════

def _britain_row():
    return {"court": "Britain", "shut_out": {"applies": True, "needed": 13,
                                            "closed": 0, "total": 26}}


class TestTheSystemNamesItsCondition:

    def test_through_a_truce(self, world):
        D.set_diplomatic_state(world, "France", "Britain", "ARMISTICE", "test")
        lever = CG._ports_lever(_britain_row(), world)
        assert lever["text"] == ("the System shuts a port only against a court at war "
                                 "with it — in a truce, no port is closed to her")

    def test_at_peace_and_at_war(self, world):
        D.set_diplomatic_state(world, "France", "Britain", "PEACE", "test")
        assert "at peace, no port is closed to her" in CG._ports_lever(_britain_row(), world)["text"]
        D.set_diplomatic_state(world, "France", "Britain", "WAR", "test")
        assert CG._ports_lever(_britain_row(), world)["text"].startswith("shut 13 of 26 ports (now 0)")

    def test_lever_down_counts_through_a_truce(self, world, monkeypatch):
        monkeypatch.setattr(CG, "THE_SYSTEM_NAMES_ITS_CONDITION", False)
        D.set_diplomatic_state(world, "France", "Britain", "ARMISTICE", "test")
        assert CG._ports_lever(_britain_row(), world)["text"].startswith("shut 13 of 26 ports (now 0)")

    def test_the_decree_says_at_war(self):
        assert reforms.effect_line({"type": "cs_closure", "value": 1}) == (
            "every client shuts its ports to Britain at war, whatever its autonomy")


# ═══════════════════════════════════════════════════════════════════════════
# RS-26 / NPC-12 — the field speaks display names
# ═══════════════════════════════════════════════════════════════════════════

def _prose(obj, out):
    """Every SENTENCE in the payload (a bare roster key in a structured
    field is not prose and is not the row's subject)."""
    if isinstance(obj, str):
        if " " in obj.strip():
            out.append(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("target", "marshal", "name", "attacker", "defender", "roster_name",
                     "marshals", "enemies", "map_data", "game_state", "known_marshals"):
                continue
            _prose(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _prose(v, out)
    return out


class TestTheFieldSpeaksDisplayNames:

    def test_the_resolver_seam(self):
        class M:
            def __init__(self, name): self.name = name
        text = CB._field_names("[Shield] ArchdukeCharles's DEFENSIVE stance; Davout gains "
                               "the advantage over ArchdukeCharles. ArchdukeCharless",
                               M("Davout"), M("ArchdukeCharles"))
        assert text == ("[Shield] Archduke Charles's DEFENSIVE stance; Davout gains "
                        "the advantage over Archduke Charles. ArchdukeCharless")

    def test_a_driven_battle(self, shipped):
        """Massena and Archduke Charles at Milan — the whole reply, the
        battle report and the muster read the display name."""
        client, world = shipped
        charles = world.marshals["ArchdukeCharles"]
        massena = world.marshals["Massena"]
        charles.location = massena.location
        world._build_marshal_index()
        world.calculate_visibility()
        r = post(client, "Massena, attack Archduke Charles")
        if r.get("muster_confirm") or r.get("pending_objection"):
            r = post(client, "attack anyway") if r.get("muster_confirm") else post(client, "trust")
        assert "Archduke Charles" in r.get("message", ""), r.get("message")
        for line in _prose({"message": r.get("message"),
                            "battle_report": r.get("battle_report"),
                            "events": r.get("events")}, []):
            assert "ArchdukeCharles" not in line, line

    def test_the_muster_hedge(self, shipped):
        client, world = shipped
        charles = world.marshals["ArchdukeCharles"]
        john = world.marshals["ArchdukeJohn"]
        massena = world.marshals["Massena"]
        charles.location = massena.location
        for r_name in world.regions[massena.location].adjacent_regions:
            if not world.get_marshals_in_region(r_name):
                john.location = r_name
                break
        world._build_marshal_index()
        world.calculate_visibility()
        from backend.commands.combat_executor import CombatExecutor
        note = CombatExecutor.muster_preview if hasattr(CombatExecutor, "muster_preview") else None
        r = post(client, "Massena, attack Archduke Charles")
        text = json.dumps(r.get("muster_confirm") or r.get("battle_report") or r.get("message"))
        assert "ArchdukeCharles does not stand alone" not in text

    def test_the_ledger_prints_the_display_name(self, world):
        from backend.game_logic import ledger
        charles = world.marshals["ArchdukeCharles"]
        world.get_region_intel(charles.location).refresh(
            "full", "scout", int(world.current_turn),
            marshals=[{"name": "ArchdukeCharles", "nation": "Austria",
                       "strength": int(charles.strength)}],
            total_strength=int(charles.strength))
        rows = [r for r in ledger._build_intel(world, "France")["known_enemies"]
                if r.get("roster_name") == "ArchdukeCharles"]
        assert rows and rows[0]["name"] == "Archduke Charles"

    def test_lever_down_keeps_the_key(self, monkeypatch):
        monkeypatch.setattr(CB, "THE_FIELD_SPEAKS_DISPLAY_NAMES", False)
        class M:
            def __init__(self, name): self.name = name
        assert CB._field_names("ArchdukeCharles holds", M("ArchdukeCharles")) == "ArchdukeCharles holds"


# ═══════════════════════════════════════════════════════════════════════════
# RS-29 / NP-X7 — the support order; the court's own rank
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRankIsTheCourtsOwn:

    def test_the_support_phrase_is_singular(self, monkeypatch):
        assert ST._strategic_command_flavor("SUPPORT") == "his support order"
        monkeypatch.setattr(ST, "A_SUPPORT_ORDER_IS_SINGULAR", False)
        assert ST._strategic_command_flavor("SUPPORT") == "reinforcement orders"

    def test_the_honorific(self, world):
        assert DN.marshal_honorific(world, "Napoleon") == "the Emperor Napoleon"
        assert DN.marshal_honorific(world, "Ney") == "Marshal Ney"
        assert DN.marshal_honorific(world, "ArchdukeJohn") == "the Archduke John"
        assert DN.marshal_honorific(world, "Kutuzov") == "General Kutuzov"
        assert DN.marshal_honorific(world, "Nobody") == "Marshal Nobody"

    def test_lever_down_titles_everyone_a_marshal(self, world, monkeypatch):
        monkeypatch.setattr(DN, "THE_HONORIFIC_IS_THE_COURTS_OWN", False)
        assert DN.marshal_honorific(world, "ArchdukeJohn") == "Marshal Archduke John"
        assert DN.marshal_honorific(world, "Kutuzov") == "Marshal Kutuzov"
        assert DN.marshal_honorific(world, "Napoleon") == "the Emperor Napoleon"

    def test_the_capture_headline(self, world):
        world.log_event({"type": "marshal_captured", "marshal": "ArchdukeJohn",
                         "nation": "Austria", "captor": "France",
                         "location": "Carniola"})
        with _quiet():
            head = dispatch._build_headline(world, "France") or {}
        texts = [head.get("text", "")] + list(head.get("sub_beats", []))
        line = next((t for t in texts if "is taken" in t), "")
        assert line.startswith("Sire — the Archduke John of Austria is taken at Carniola"), texts

    def test_the_desk_and_the_wound(self, shipped):
        client, world = shipped
        msg = post(client, "where is Napoleon?").get("message", "")
        assert msg.startswith("the Emperor Napoleon stands at"), msg
        msg = post(client, "where is Ney?").get("message", "")
        assert msg.startswith("Marshal Ney stands at"), msg
        world.log_event({"type": "marshal_wounded", "marshal": "Napoleon",
                         "nation": "France", "location": "Lorraine", "turns": 3})
        with _quiet():
            head = dispatch._build_headline(world, "France") or {}
        texts = [head.get("text", "")] + list(head.get("sub_beats", []))
        assert any("the Emperor Napoleon is WOUNDED" in t for t in texts), texts


# ═══════════════════════════════════════════════════════════════════════════
# NPC-23 / NPC-24 / NP-X6 — three copy rows
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSmallCopyRows:

    def test_the_defenders_are_joined_in_series(self, world):
        from backend.models.intel import FULL
        home = world.get_nation_capital("France")
        for name in ("Lannes", "Murat", "Napoleon"):
            world.marshals[name].location = home
        world._build_marshal_index()
        mack = world.marshals["Mack"]
        mack.location = home
        world._build_marshal_index()
        world.get_region_intel(home).refresh(
            FULL, "marshal_present", int(world.current_turn),
            marshals=[{"name": "Mack", "nation": "Austria", "strength": int(mack.strength)}],
            total_strength=int(mack.strength))
        world.event_log.clear()
        with _quiet():
            head = dispatch._build_headline(world, "France") or {}
        texts = [head.get("text", "")] + list(head.get("sub_beats", []))
        line = next((t for t in texts if "in his path" in t), "")
        assert "Lannes, Murat and Napoleon stand in his path." in line, texts

    def test_the_famine_counts_its_dead(self):
        variant = dispatch._STANDING_ESCALATION["supply_strain"][1]
        text = variant.format(who="Massena", have="has", turns=4, region="Tyrol",
                              losses="1,351 men", losses_dead="1,351 men dead",
                              remedy="Move a corps.")
        assert "1,351 men dead. The country will ask" in text
        assert "{losses}." not in variant

    @staticmethod
    def _starving(world):
        """Three French corps on one province, two turns of attrition logged
        — the ec_levy staging, so the producer's own ladder fires."""
        corps = [m for m in world.marshals.values()
                 if m.nation == "France" and not m.is_sovereign][:3]
        loc = corps[0].location
        for m in corps:
            m.location = loc
        for t in (9, 10):
            world.current_turn = t
            for m in corps:
                world.log_event({"type": "supply_attrition", "marshal": m.name,
                                 "nation": "France", "region": loc,
                                 "losses": 1400})
        world.current_turn = 10
        return loc

    def test_the_producer_counts_the_dead_under_the_lever(self, world, monkeypatch):
        """The sweep's lesson: the template pin above formats the slot by
        hand and reaches no production line. This one drives the producer —
        lever up, the field reads "8,400 men dead"; lever down, the bare
        figure the pre-slice page printed."""
        self._starving(world)
        with _quiet():
            cand = dispatch._supply_strain_candidate(world, "France")
        assert cand and cand["fields"]["losses_dead"] == "8,400 men dead", cand
        assert cand["fields"]["losses"] == "8,400 men"
        monkeypatch.setattr(dispatch, "THE_FAMINE_COUNTS_ITS_DEAD", False)
        with _quiet():
            down = dispatch._supply_strain_candidate(world, "France")
        assert down["fields"]["losses_dead"] == "8,400 men", down

    def test_the_sovereigns_card_states_the_true_half(self, world):
        from backend.game_logic import marshal_overview as MO
        card = next(c for c in MO.build_marshal_overview(world) if c["name"] == "Napoleon")
        text = json.dumps(card)
        assert "never asks" not in text
        assert "read back to you by Berthier" in text
        from backend.models.personality import PERSONALITY_DESCRIPTIONS
        desc = json.dumps({str(k): v for k, v in PERSONALITY_DESCRIPTIONS.items()})
        assert "never asks" not in desc


# ═══════════════════════════════════════════════════════════════════════════
# SRX-6 / SF-V2 — the white peace's own blocker and header
# ═══════════════════════════════════════════════════════════════════════════

class TestTheWhitePeaceSpeaksForItself:

    def test_the_spoken_clause(self, monkeypatch):
        assert DT.spoken_blocker_phrase("settlement_tier_legitimacy", "", white_peace=True) == (
            "it claims no victory, but a whole-war peace still needs every covered "
            "court's consent, and not every court consents")
        assert DT.spoken_blocker_phrase("settlement_tier_legitimacy", "") == (
            "the terms claim a victory the field has not delivered")
        monkeypatch.setattr(DT, "THE_WHITE_PEACE_SPEAKS_ITS_OWN_BLOCKER", False)
        assert "claim a victory" in DT.spoken_blocker_phrase(
            "settlement_tier_legitimacy", "", white_peace=True)

    def test_the_typed_route_at_boot(self, shipped):
        client, world = shipped
        r = post(client, "propose common peace with Austria")
        text = json.dumps(r)
        assert "claim a victory the field has not delivered" not in text, text[:600]
        dialogue = world.pending_diplomatic_dialogue or {}
        assert dialogue.get("white_peace") and not dialogue.get("can_ratify"), dialogue.get("message")
        assert "claims no victory" in dialogue.get("message", ""), dialogue.get("message")
        voices = [str(r.get("voice_line") or r.get("line") or "")
                  for r in (dialogue.get("per_court_acceptance") or [])]
        assert voices and all("claims no victory" in v for v in voices if "consent" in v), voices

    def test_no_will_not_carry_beside_a_live_ratify(self):
        verdict = {"carries": False, "carry_verdict_display":
                   "Will NOT carry as drafted — every court must reach 50. Holding out: Britain 20/50."}
        out = SG._verdict_beside_the_button(verdict, white_peace=True, can_ratify=True)
        assert out["carry_verdict_display"].startswith("Carries on the leader's word")
        assert out["per_court_verdict_display"].startswith("Will NOT carry")
        assert SG._verdict_beside_the_button(verdict, white_peace=True, can_ratify=False) is verdict
        assert SG._verdict_beside_the_button(verdict, white_peace=False, can_ratify=True) is verdict

    def test_every_staged_white_peace_agrees_with_its_button(self, world):
        for covered in (["Austria"], ["Austria", "Britain", "Russia"]):
            while world.dialogue_manager.pop() is not None:
                pass
            with _quiet():
                staged = stage_settlement_confirm(
                    world, war_id="war_1", settlement_terms=[{"type": "peace"}],
                    covered_enemy_participants=covered)
            assert staged["success"], staged
            d = world.pending_diplomatic_dialogue
            verdict = str((d.get("overall_acceptance") or {}).get("carry_verdict_display") or "")
            assert not (d.get("can_ratify") and verdict.startswith("Will NOT carry")), (covered, verdict)


# ═══════════════════════════════════════════════════════════════════════════
# WO-D11 (the copy half) — the march names the forfeit
# ═══════════════════════════════════════════════════════════════════════════

class TestTheMarchNamesTheForfeit:

    def _stage(self, world):
        """Ney at Dresden beside EMPTY, ungarrisoned Bohemia — Archduke
        Charles's estate; the march walks in, auto-secures (IGR-X5) and the
        title is stripped at the advance."""
        ney = world.marshals["Ney"]
        charles = world.marshals["ArchdukeCharles"]
        assert world.regions["Bohemia"].controller == "Austria"
        assert not world.get_marshals_in_region("Bohemia")
        assert not int(getattr(world.regions["Bohemia"], "garrison_strength", 0) or 0)
        ney.location = "Dresden"
        world._build_marshal_index()
        charles.dotation_regions = ["Bohemia"]
        world.calculate_visibility()
        return "Bohemia"

    def test_the_sentence(self, shipped):
        client, world = shipped
        target = self._stage(world)
        r = post(client, f"Ney, march to {target}")
        assert r.get("success"), r.get("message")
        if world.marshals["Ney"].location != target:
            r = post(client, "end turn")
        assert world.regions[target].controller == "France", r.get("message")
        assert "The province is secured. Archduke Charles's estate there is forfeit" in r.get("message", ""), r.get("message")
        # The sentence is TRUE: no question is pending, so the advance's
        # prune strips the title and logs the loss — no windfall, no
        # goodwill entry. The prune is called directly: an end turn here
        # would let the Archdukes march back in and the title stand.
        assert world.regions[target].controller == "France"
        world._process_dotation_state()
        assert "Bohemia" not in (world.marshals["ArchdukeCharles"].dotation_regions or [])
        assert any(e.get("type") == "estate_lost" and e.get("region") == "Bohemia"
                   for e in world.event_log)
        assert not any(e.get("type") == "estate_respected" for e in world.event_log)

    def test_lever_down_says_only_secured(self, shipped, monkeypatch):
        from backend.commands import movement_executor as ME
        monkeypatch.setattr(ME, "THE_MARCH_NAMES_THE_FORFEIT", False)
        client, world = shipped
        target = self._stage(world)
        r = post(client, f"Ney, march to {target}")
        if world.marshals["Ney"].location != target:
            r = post(client, "end turn")
        assert "The province is secured." in r.get("message", "")
        assert "estate there is forfeit" not in json.dumps(r)
