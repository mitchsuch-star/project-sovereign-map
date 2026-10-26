"""Score Finish Step 9, SF-RR4 "war, truce and the standing order" (October 21,
2026; rules SYSTEMS_REFERENCE.md §139).

Every row reproduced on today's tree before a line was written (four read-only
investigators staged them; most were the playtester's quoted digest lines):

    `Davout, attack Mack` -> "(Trust him and he will fortify …)", priced
      nowhere, and the next order "Not enough actions!"                (SFR-D3)
    the contact interrupt "88k with the muster committed … Odds
      unfavorable", the muster "114k … favorable" a click later         (SFR-D4)
    `Massena, hold Milan` -> the Emperor's muster draws him off Milan  (SFR-D5)
    "Trust him and he will attack Mack" -> the battle against the
      Archduke Charles, covering Mack's retreat                         (SFR-D6)
    the attack objection pricing one corps        (SFR-D18, closed by DDB-19)
      — and its live sibling, the pursuit's                             (RR4-X1)
    `Ney, support Davout` -> trust -> "the Pursue order is not issued" (SFR-D22)
    "no nearer home … interned where they stand" at Milan, France's;
      "why must Massena go home?" shrugged                              (SFR-D29)
    "469 to enemy harassment" crossing an ally's ground                 (SFR-D31)
    "Paget drives a forced march — Piedmont → Lyonnais → Piedmont"      (SFR-D35)
    two laws lapse where one repeal would keep the other               (SFR-B14)
    "Munich has been captured by France!" — the works unnamed           (EG-X5)

and EG-D3's bench (ruled October 13, 2026): Spain's La Romana, Blake and
Cuesta, Sweden's Toll and Adlercreutz, Bavaria's Wrede, authored in
`marshal_pool`, validated, each court commissioning from it at war.

Every fix is ONE function seam held down here to reproduce its row (the DD-B
idiom — no module lever). What reaches the AI is attributed in
`tools/_sf_rr4_series_arms.py` (`tools/_sf_rr4_series_arms_final.json`).
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.ai.enemy_ai as EA
import backend.ai.question_desk as QD
import backend.commands.combat_executor as CE
import backend.commands.defiance as DEF
import backend.commands.executor as EX
import backend.commands.movement_executor as ME
import backend.commands.objection_v2 as OV2
import backend.commands.strategic_executor as SE
import backend.commands.tactical_executor as TE
import backend.game_logic.dispatch as DS
import backend.game_logic.garrison_report as GR
import backend.game_logic.recruitment as RC
import backend.game_logic.reforms as RF
import backend.game_logic.withdrawal as W
import backend.main as M
from backend.commands.parser import CommandParser
from backend.game_logic.diplomacy import set_diplomatic_state
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with _quiet():
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


@pytest.fixture
def steady(monkeypatch):
    """The objection's dice held still (the investigators' boards): the mood
    variance flat, no defiance."""
    for mod in (EX, SE, OV2):
        monkeypatch.setattr(mod, "apply_mood_variance", lambda concern: concern)
    monkeypatch.setattr(DEF, "calculate_defiance_chance", lambda *a, **k: 0.0)


@pytest.fixture
def world():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


def post(client, line):
    with _quiet():
        return client.post("/command", json={"command": line}).json()


def ask(client, line):
    return str(post(client, line).get("message") or "")


def answer(client, choice):
    with _quiet():
        return client.post("/respond_to_objection", json={"choice": choice}).json()


def combat():
    with _quiet():
        return EX.CommandExecutor()._combat


def _see(w):
    with _quiet():
        w.calculate_visibility()
        w.invalidate_active_nations_cache()


# ═════════════ SFR-D3: the Trust arm states its price ═════════════════════════

class TestSFRD3TheTrustArmStatesItsPrice:

    def _board(self, client, w):
        w.get_marshal("Mack").strength = 60000
        for name, m in w.marshals.items():
            if m.nation == "France" and name != "Davout":
                m.strength = 100
        ask(client, "Massena, hold Milan")
        return post(client, "Davout, attack Mack at Swabia")

    def test_trusting_names_the_two_actions(self, shipped, steady):
        client, w = shipped
        r = self._board(client, w)
        message = str(r.get("message"))
        assert "(Trust him and he will fortify current position instead. Trusting costs 2 actions " \
               "— he must first go defensive.)" in message, message
        assert r["objection"]["trust_ap_cost"] == 2
        assert r["objection"]["trust_note"] == "he must first go defensive"

    def test_seam_down_trust_is_unpriced(self, shipped, steady, monkeypatch):
        client, w = shipped
        monkeypatch.setattr(TE, "answer_terms", lambda world, marshal, order: (1, ""))
        r = self._board(client, w)
        assert "Trusting costs" not in str(r.get("message"))
        assert "trust_ap_cost" not in r["objection"]

    def test_the_answer_terms_are_the_gates_price(self, world):
        davout = world.get_marshal("Davout")
        fortify = {"action": "fortify", "target": davout.location}
        assert TE.answer_terms(world, davout, fortify) == (2, "he must first go defensive")
        assert TE.answer_terms(world, davout, {"action": "attack", "target": "Mack"}) == (1, "")
        assert TE.answer_terms(world, davout, None) == (0, "")


# ═════════════ SFR-D4: the interrupt reads the muster's figure ════════════════

class TestSFRD4OneFigureOneReading:

    def _board(self, client, w):
        mack, lannes = w.get_marshal("Mack"), w.get_marshal("Lannes")
        mack.strength, mack.location = 42190, "Swabia"
        lannes.strength = 16957
        return post(client, "Lannes, march to Swabia"), lannes, mack

    def test_the_note_is_the_musters(self, shipped):
        client, w = shipped
        r, lannes, mack = self._board(client, w)
        message = str(r.get("message"))
        assert "Odds unfavorable" in message           # his own read stays solo
        odds = combat().muster_odds(lannes, mack, w)
        joint = int(lannes.strength + odds["committed_attacker"])
        assert f"{joint:,} with the muster committed" in message, message
        assert f"weighed together, the balance of force looks {odds['band']}" in message

    def test_seam_down_the_note_sums_unpriced(self, shipped, monkeypatch):
        client, w = shipped

        def _unpriced(cx, marshal, enemy, world):
            joiners = [world.marshals[n] for n in cx.muster_odds(marshal, enemy, world)["joining"]]
            return {"committed": float(cx._committed_reinforcement_strength(
                marshal, joiners, world, expected_at=enemy.location)), "band": None}
        monkeypatch.setattr(CE, "staff_muster_reading", _unpriced)
        r, lannes, mack = self._board(client, w)
        message = str(r.get("message"))
        odds = combat().muster_odds(lannes, mack, w)
        assert f"{int(lannes.strength + odds['committed_attacker']):,} with the muster" not in message
        assert "weighed together" not in message


# ═════════════ SFR-D5: a hold holds ═══════════════════════════════════════════

class TestSFRD5AHoldHoldsItsPost:

    def _preview(self, client, w):
        ask(client, "Massena, hold Milan")
        w.get_marshal("Mack").location = "Munich"
        nap = w.get_marshal("Napoleon")
        nap.location, nap.strength = "Swabia", 8585
        pv = combat()._build_muster_preview(nap, w.get_marshal("Mack"), w, {"world": w})
        return next(r for r in pv["rows"] if r["marshal"] == "Massena")

    def test_the_muster_leaves_him_at_milan(self, shipped):
        client, w = shipped
        row = self._preview(client, w)
        assert row["will_join"] is False and row["reason"] == "holding_position"
        assert "at Milan — order 'Massena, support Napoleon' and he leaves it to march" \
            in row["standing_order_hint"]
        assert CE.holds_a_post(w.get_marshal("Massena"))
        assert w.get_marshal("Massena").holding_position is False   # aggressive: the flag never set

    def test_seam_down_he_marches_off_his_post(self, shipped, monkeypatch):
        client, w = shipped
        monkeypatch.setattr(CE, "holds_a_post",
                            lambda m: bool(getattr(m, "holding_position", False)))
        assert self._preview(client, w)["will_join"] is True

    def test_a_hold_not_yet_reached_is_a_march(self, world):
        from backend.models.marshal import StrategicOrder
        m = world.get_marshal("Massena")
        m.strategic_order = StrategicOrder(command_type="HOLD", target="Piedmont",
                                           target_type="region", started_turn=1,
                                           original_command="Massena, hold Piedmont")
        assert not CE.holds_a_post(m)


# ═════════════ SFR-D6: the quote names the man who will stand ═════════════════

class TestSFRD6TheManWhoStands:

    def _stage(self, w):
        w.get_marshal("Massena").location = "Munich"
        mack = w.get_marshal("Mack")
        mack.location, mack.strength, mack.retreated_this_turn = "Tyrol", 13000, True
        w.get_marshal("ArchdukeCharles").location = "Tyrol"
        _see(w)

    def test_trust_and_muster_name_the_archduke(self, shipped, steady):
        client, w = shipped
        self._stage(w)
        message = ask(client, "Massena, fortify")
        assert ("(Trust him and he will attack Archduke Charles at Tyrol as he covers "
                "Mack's retreat instead.)") in message, message
        pv = combat()._build_muster_preview(w.get_marshal("Massena"), w.get_marshal("Mack"),
                                            w, {"world": w})
        assert pv["target"]["name"] == "ArchdukeCharles"
        assert pv["target"]["covering"] == "Mack"
        assert "vs Archduke Charles (" in combat()._format_muster_lines(pv)
        assert "covering Mack's retreat, at Tyrol" in combat()._format_muster_lines(pv)

    def test_seam_down_the_quote_names_mack(self, shipped, steady, monkeypatch):
        client, w = shipped
        self._stage(w)
        monkeypatch.setattr(CE, "answering_defender", lambda world, enemy: enemy)
        assert "(Trust him and he will attack Mack at Tyrol instead.)" in ask(client, "Massena, fortify")
        pv = combat()._build_muster_preview(w.get_marshal("Massena"), w.get_marshal("Mack"),
                                            w, {"world": w})
        assert pv["target"]["name"] == "Mack" and "covering" not in pv["target"]

    def test_the_swap_itself_is_unchanged(self, world):
        self._stage(world)
        assert CE.covering_ally(world, world.get_marshal("Mack")).name == "ArchdukeCharles"
        world.get_marshal("Mack").retreated_this_turn = False
        assert CE.covering_ally(world, world.get_marshal("Mack")) is None


# ═════════════ SFR-D18 (closed by DDB-19) and RR4-X1 the pursuit ══════════════

class TestSFRD18AndThePursuit:

    def test_d18_closed_the_attack_reads_the_muster(self, shipped, steady):
        client, w = shipped
        r = post(client, "Davout, attack Mack at Swabia")
        assert not w.pending_objection, r.get("message")

    def test_d18_seam_down_the_attack_objects(self, shipped, steady, monkeypatch):
        client, w = shipped
        monkeypatch.setattr(OV2, "muster_expected_totals", lambda m, e, world: None)
        assert "The odds are not in our favor" in ask(client, "Davout, attack Mack at Swabia")

    def test_x1_the_pursuit_reads_the_muster(self, shipped, steady):
        client, w = shipped
        post(client, "Davout, pursue Mack")
        assert w.pending_strategic_objection is None

    def test_x1_seam_down_the_pursuit_objects(self, shipped, steady, monkeypatch):
        client, w = shipped
        monkeypatch.setattr(OV2, "pursue_muster_totals", lambda m, e, world: None)
        post(client, "Davout, pursue Mack")
        assert w.pending_strategic_objection is not None


# ═════════════ SFR-D22: trusting him issues his chase ═════════════════════════

class TestSFRD22TrustIssuesTheChase:

    def _stage(self, client, w):
        w.get_marshal("Mack").location = "Bohemia"
        w.get_marshal("ArchdukeJohn").location = "Tyrol"
        _see(w)
        return ask(client, "Ney, support Davout")

    def test_the_objection_names_and_trust_issues_it(self, shipped, steady):
        client, w = shipped
        message = self._stage(client, w)
        assert "(Trust him and he will pursue Archduke John at Tyrol instead.)" in message, message
        ney = w.get_marshal("Ney")
        before, actions = int(ney.trust.value), int(w.actions_remaining)
        r = answer(client, "trust")
        assert "not issued" not in str(r.get("message"))
        order = ney.strategic_order
        assert order is not None and (order.command_type, order.target) == ("PURSUE", "ArchdukeJohn")
        assert int(w.actions_remaining) == actions - 1
        assert int(ney.trust.value) - before == int(r.get("trust_change") or 0) > 0

    def test_seam_down_the_order_is_declined(self, shipped, steady, monkeypatch):
        client, w = shipped
        monkeypatch.setattr(SE, "objection_already_answered", lambda command: False)
        self._stage(client, w)
        r = answer(client, "trust")
        assert "the Pursue order is not issued" in str(r.get("message"))
        assert w.get_marshal("Ney").strategic_order is None


# ═════════════ SFR-D29: the road home, said and asked ═════════════════════════

def _stranded_at_milan(w):
    w.regions["Milan"].controller = "France"
    w.regions["Piedmont"].controller = "France"
    for name in ("Massena", "Murat"):
        w.marshals[name].location = "Milan"
    with _quiet():
        set_diplomatic_state(w, "France", "Austria", "ARMISTICE", "test")
    for n in ("Munich", "Piedmont"):
        w.regions[n].controller = "Austria"
    w._evac_direction_cache = None
    w.current_turn += 1
    with _quiet():
        return W.process_evacuation_grants(w)


def _tick(w):
    w.current_turn += 1
    with _quiet():
        return W.process_evacuation_grants(w)


ENCLAVE = "Milan is ours, but Austrian ground at Munich, Piedmont and Tyrol cuts it off from home"


class TestSFRD29TheRoadHome:

    def test_the_grant_and_the_warning_name_the_enclave(self, world):
        granted = _stranded_at_milan(world)
        assert any(ENCLAVE in e["message"] and "changed hands" not in e["message"]
                   for e in granted if e["type"] == "evacuation_granted")          # RR4-X4
        warned = [e for e in _tick(world) if e["type"] == "evacuation_lapsing"]
        assert warned and all(ENCLAVE in e["message"] for e in warned), warned
        assert all(e["message"].endswith("interned by Austria.") for e in warned)
        assert warned[0]["cut_off_by"] == "Austria"

    def test_seam_down_the_warning_reads_false(self, world, monkeypatch):
        monkeypatch.setattr(W, "stranding_cause", lambda w, m: None)
        _stranded_at_milan(world)
        warned = [e for e in _tick(world) if e["type"] == "evacuation_lapsing"]
        assert warned and all("ours" not in e["message"] for e in warned)
        assert all(e["message"].endswith("before his corps is interned.") for e in warned)

    def test_the_page_names_it_too(self, world):
        _stranded_at_milan(world)
        row = next(e for e in _tick(world) if e["type"] == "evacuation_lapsing")
        assert DS._passage_why(world, row) == " — " + ENCLAVE
        assert DS._passage_interned(row, 2) == "by Austria"
        assert DS._passage_interned({}, 2) == "where they stand"
        line = DS._HEADLINE_TEMPLATES["passage_lapsing"].format(
            who="Massena and Murat", is_are="are", why=DS._passage_why(world, row),
            passage_clause="leaves 2 turns to spare", his_their="their",
            interned=DS._passage_interned(row, 2))
        assert line == ("Sire — Massena and Murat are no nearer home — " + ENCLAVE + ", and the "
                        "safe passage leaves 2 turns to spare. After that their corps will be "
                        "interned by Austria.")

    def test_x12_the_newest_reading_leads(self):
        stale, fresh = {"turn": 5, "turns_left": 0}, {"turn": 6, "turns_left": 2}
        assert min([stale, fresh], key=DS.lapsing_reading_key) is fresh
        same_turn = [{"turn": 6, "turns_left": 2}, {"turn": 6, "turns_left": 1}]
        assert min(same_turn, key=DS.lapsing_reading_key)["turns_left"] == 1

    def test_the_internment_names_the_enclave(self, world):                       # RR4-X5
        _stranded_at_milan(world)
        interned = []
        for _ in range(6):
            interned += [e for e in _tick(world) if e["type"] == "marshal_interned"]
        assert interned
        assert all("cut off at Milan by Austrian ground" in e["message"]
                   and "Austria has disarmed and interned it." in e["message"]
                   and "quit Austrian soil" not in e["message"] for e in interned)

    def test_the_set_aside_names_the_passage(self, world):                        # RR4-X7
        from backend.models.marshal import StrategicOrder
        order = StrategicOrder(command_type="MOVE_TO", target="Franche-Comte",
                               target_type="region", started_turn=1,
                               original_command=W.ROAD_HOME_COMMAND)
        clause = EX.set_aside_clause(world.get_marshal("Massena"), order)
        assert clause.startswith("Massena's march home to Franche-Comte is set aside — the safe "
                                 "passage still counts down")

    @pytest.mark.parametrize("question", [
        "why must Massena go home?", "why is Massena being sent home?",
        "why is Massena stranded?", "what is internment?", "what does internment mean?",
        "is Murat safe from internment?", "how long is the safe passage?",
        "what is the road home?"])
    def test_the_desk_answers_the_road_home(self, shipped, question):
        client, w = shipped
        _stranded_at_milan(w)
        reply = ask(client, question)
        assert ENCLAVE in reply, (question, reply)
        assert "cannot answer" not in reply

    def test_the_desk_answers_the_truce(self, shipped):
        client, w = shipped
        _stranded_at_milan(w)
        reply = ask(client, "what does the truce with Austria mean?")
        assert reply.startswith("A truce pauses the war, Sire; it does not end it")
        assert "The armistice with Austria has" in reply and ENCLAVE in reply
        assert ask(client, "how long does the truce with Austria last?").startswith(
            "The armistice with Austria has")                                     # RR4-X6

    def test_seam_down_the_desk_shrugs(self, shipped, monkeypatch):
        client, w = shipped
        _stranded_at_milan(w)
        monkeypatch.setattr(QD, "_answer_road_home", lambda *a, **k: None)
        assert ENCLAVE not in ask(client, "why must Massena go home?")

    def test_home_ground_is_said_so(self, shipped):
        client, w = shipped
        _stranded_at_milan(w)
        reply = ask(client, "is Davout safe from internment?")
        assert reply.startswith("Davout stands on home ground"), reply


# ═════════════ SFR-D31: an enemy harasses, an ally does not ═══════════════════

class TestSFRD31OnlyAnEnemyHarasses:

    def _swabia(self, world, controller):
        region = world.get_region("Swabia")
        region.controller = controller
        region.garrison_detachment, region.garrison_strength = True, 1500
        return region

    def test_an_ally_and_a_truce_do_not(self, world):
        davout = world.get_marshal("Davout")
        assert ME.harassment_losses(world, davout, self._swabia(world, "Bavaria")) == 0
        assert ME.harassment_losses(world, davout, self._swabia(world, "Austria")) == \
            int(davout.strength * 0.02)
        with _quiet():
            set_diplomatic_state(world, "France", "Austria", "ARMISTICE", "test")
        assert ME.harassment_losses(world, davout, self._swabia(world, "Austria")) == 0

    def test_the_march_reads_it(self, world):
        self._swabia(world, "Bavaria")
        with _quiet():
            info = EX.CommandExecutor()._calculate_movement_attrition(
                world.get_marshal("Davout"), "Swabia", world)
        assert info["harassment_losses"] == 0

    def test_seam_down_an_ally_harasses(self, world, monkeypatch):
        old = (lambda w, m, r: int(m.strength * 0.02)
               if (r and r.controller and r.controller != m.nation
                   and r.garrison_detachment and r.garrison_strength > 0) else 0)
        monkeypatch.setattr(ME, "harassment_losses", old)
        self._swabia(world, "Bavaria")
        with _quiet():
            info = EX.CommandExecutor()._calculate_movement_attrition(
                world.get_marshal("Davout"), "Swabia", world)
        assert info["harassment_losses"] > 0


# ═════════════ SFR-D35: no hop back ═══════════════════════════════════════════

def _paget_hops(world):
    from backend.models.marshal import Marshal, Stance
    with _quiet():
        paget = Marshal("Paget", "Gascony", 4659, "aggressive", nation="Britain")
        paget.stance = Stance.AGGRESSIVE
        world.marshals["Paget"] = paget
        moore = world.get_marshal("Moore")
        moore.strength, moore.fortified = 5000, False
        castanos = world.get_marshal("Castanos")
        castanos.location, castanos.strength = "Normandy", 14120
        world.refresh_marshal_indexes()
        world.invalidate_active_nations_cache()
        world.calculate_visibility()
    hops = ["Gascony"]
    ai = EA.EnemyAI(EX.CommandExecutor())
    orig = EA.EnemyAI._execute_action

    def _execute(self, action, game_state):
        result = orig(self, action, game_state)
        if action.get("marshal") == "Paget" and result.get("success"):
            loc = world.get_marshal("Paget").location
            if loc != hops[-1]:
                hops.append(loc)
        return result
    with _quiet():
        EA.EnemyAI._execute_action = _execute
        try:
            ai.decrement_all_cooldowns(world)
            ai.process_nation_turn("Britain", world, {"world": world})
        finally:
            EA.EnemyAI._execute_action = orig
    return hops


class TestSFRD35NoHopBack:

    def test_paget_advances_and_stays(self, world):
        hops = _paget_hops(world)
        assert hops[:2] == ["Gascony", "Berry"], hops
        assert len(hops) == len(set(hops)), hops

    def test_seam_down_paget_bounces(self, world, monkeypatch):
        monkeypatch.setattr(EA, "ai_hop_backtracks", lambda *a, **k: False)
        hops = _paget_hops(world)
        assert hops[:3] == ["Gascony", "Berry", "Gascony"], hops

    def test_the_urgent_rungs_may_fall_back(self):
        visited = {"Gascony", "Berry"}
        assert EA.ai_hop_backtracks(visited, {"action": "retreat", "target": "Gascony"}, 8)
        assert not EA.ai_hop_backtracks(visited, {"action": "retreat", "target": "Gascony"}, 2)
        assert not EA.ai_hop_backtracks(visited, {"action": "attack", "target": "Gascony"}, 8)
        assert EA.ai_records_the_visit({"action": "attack"})


# ═════════════ SFR-B14: the AI repeals before a law lapses ════════════════════

def _austria_on_the_edge(world, shortfall):
    """A long war has eaten Austria's revenue (six provinces lost — the
    investigator's board): her two laws in force, a positive chest, a
    negative Net, and the turn's end `shortfall` gold short."""
    from backend.game_logic.ledger import chest_forecast
    rows = {r["id"]: r for r in RF.deck(world, "Austria")}
    with _quiet():
        for law in ("landwehr", "generalissimus"):
            RF.enact_law(world, "Austria", rows[law])
        lost = [r for r in world.regions.values()
                if r.controller == "Austria" and not getattr(r, "is_capital", False)][:6]
        for region in lost:
            region.controller = "France"
        world.invalidate_active_nations_cache()
    forecast = chest_forecast(world, "Austria")
    world.nation_gold["Austria"] = int(world.nation_gold["Austria"]) - int(forecast["projected"]) - shortfall
    assert int(world.nation_gold["Austria"]) > 0 and int(forecast["net"]) < 0
    return rows


def _admin_phase(world):
    ai = EA.EnemyAI(EX.CommandExecutor())
    with _quiet():
        results = ai.execute_admin_phase("Austria", world, {"world": world})
    return [(r.get("ai_action") or {}).get("action") for r in results]


class TestSFRB14TheRepealBeforeTheLapse:

    def test_the_court_repeals_the_lesser_law(self, world):
        _austria_on_the_edge(world, 80)
        forecast = RF.lapse_forecast(world, "Austria")
        assert forecast and forecast["law"] == "landwehr"
        world.admin_actions_remaining = 0          # RR4-X8: the player's pool is not the AI's
        assert _admin_phase(world)[:1] == ["repeal_law"]
        assert [r["id"] for r in RF.laws_in_force(world, "Austria")] == ["landwehr"]

    def test_seam_down_the_law_still_lapses(self, world, monkeypatch):
        monkeypatch.setattr(RF, "ai_repeal_before_lapse", lambda *a, **k: None)
        monkeypatch.setattr(RF, "ai_holds_the_purse", lambda *a, **k: False)
        _austria_on_the_edge(world, 80)
        assert "repeal_law" not in _admin_phase(world)
        assert [r["id"] for r in RF.laws_in_force(world, "Austria")] == ["landwehr", "generalissimus"]
        assert RF.lapse_forecast(world, "Austria") is not None

    def test_no_repeal_that_saves_nothing_and_no_spending(self, world):
        _austria_on_the_edge(world, 277)       # no repeal covers it
        assert RF.ai_repeal_before_lapse(world, "Austria", 2) is None
        assert RF.ai_holds_the_purse(world, "Austria") is True
        assert _admin_phase(world) == []        # RR4-X9: the purse is held

    def test_seam_down_the_court_spends_over_the_edge(self, world, monkeypatch):
        monkeypatch.setattr(RF, "ai_holds_the_purse", lambda *a, **k: False)
        _austria_on_the_edge(world, 277)
        assert _admin_phase(world) != []


# ═════════════ EG-X5 + RR4-X10: the works a capture takes are named ════════════

class TestEGX5TheWorksAreNamed:

    def test_the_line(self, world):
        assert GR.capture_garrison_line(world, "Munich", 2000, "Bavaria") == \
            "The last 2,000 of the garrison at Munich give way."
        assert GR.capture_garrison_line(world, "Munich", 0, "Bavaria") == \
            "Munich's works stood empty — no garrison held them."
        assert GR.capture_garrison_line(world, "Swabia", 0, "Bavaria") == ""


def _drive(tmp_path, name, seed, turns, *extra):
    env = dict(os.environ)
    env.update({"PYTHONHASHSEED": "0", "LLM_MODE": "mock",
                "INK_IRON_SAVE_DIR": str(tmp_path / "_saves")})
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED"):
        env.pop(key, None)
    cmd = [sys.executable, str(REPO / "tools" / "playtest_driver.py"), "--name", name, "--fresh",
           "--out", str(tmp_path), "--llm", "mock",
           "--script", "tools/playtest_scripts/commanded_full40.json", "--turns", str(turns),
           "--diplomacy", "accept", "--seed", seed, *extra]
    subprocess.run(cmd, cwd=str(REPO), env=env, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, check=True, timeout=900)
    return tmp_path / name


def _turn_block(digest: str, turn: int) -> str:
    head = f"## Turn {turn} "
    start = digest.index(head)
    end = digest.find("\n## Turn ", start + 1)
    return digest[start:end if end != -1 else None]


class TestEGX5TheDrivenArm:
    """The gate's CMD-H arm (historical): on turn 6 Lannes's field win takes
    Munich, whose works held 2,000 (Austria's capture had emptied them)."""

    def test_the_report_names_the_garrison(self, tmp_path):
        arm = _drive(tmp_path, "CMD-H", "historical", 6)
        block = _turn_block((arm / "digest.md").read_text(encoding="utf-8"), 6)
        assert "capture_choice[capture]: Munich" in block
        assert "Munich falls to Lannes. The last 2,000 of the garrison at Munich give way." in block

    def test_seam_down_the_capture_is_silent(self, tmp_path):
        arm = _drive(tmp_path, "CMD-H", "historical", 6,
                     "--seam", 'backend.game_logic.garrison_report:capture_garrison_line=""')
        block = _turn_block((arm / "digest.md").read_text(encoding="utf-8"), 6)
        assert "capture_choice[capture]: Munich" in block
        assert "garrison" not in block.lower()


# ═════════════ EG-D3: the secondaries' bench ═══════════════════════════════════

BENCH = {"Spain": ["LaRomana", "Blake", "Cuesta"], "Sweden": ["Toll", "Adlercreutz"],
         "Bavaria": ["Wrede"]}


class TestEGD3TheBench:

    def test_authored_and_valid(self, world):
        from backend.modding.validator import validate_scenario
        for court, names in BENCH.items():
            assert [c["name"] for c in world.marshal_pool[court]] == names, court
        assert [c["name"] for c in world.contingent_commanders["Bavaria"]] == ["Raglovich"]
        assert [c["name"] for c in world.contingent_commanders["Spain"]] == ["Kindelan"]
        result = validate_scenario(str(SCENARIO))
        assert result.is_valid, [e.message for e in result.errors if e.severity == "error"]

    @pytest.mark.parametrize("court,first", [("Spain", "LaRomana"), ("Sweden", "Toll"),
                                             ("Bavaria", "Wrede")])
    def test_each_court_commissions_at_war(self, world, court, first):
        if not world.get_nations_at_war_with(court):
            with _quiet():
                set_diplomatic_state(world, court, "France", "WAR", "test")
        world.nation_gold[court] = 10000
        action = RC.find_ai_commission(world, court, 10000)
        assert action == {"marshal": None, "action": "recruit_marshal", "target": first,
                          "_acting_nation": court}
        world.marshal_pool.pop(court)                 # the bench down: as before
        assert RC.find_ai_commission(world, court, 10000) is None

    def test_wrede_takes_the_field_through_the_shared_executor(self, world):
        world.nation_gold["Bavaria"] = 10000
        ai = EA.EnemyAI(EX.CommandExecutor())
        with _quiet():
            ai.execute_admin_phase("Bavaria", world, {"world": world})
        wrede = world.get_marshal("Wrede")
        assert wrede is not None and wrede.nation == "Bavaria" and wrede.location == "Munich"
        assert wrede.get_relationship("Deroy") == -1
        assert world.get_marshal("Deroy").get_relationship("Wrede") == -1

    def test_the_series_record(self):
        from tests.test_ai_intent_threat_migration import (
            SERIES_BEFORE_THE_BENCH, SERIES_BEFORE_THE_DEFENDERS_MUSTER)
        rec = json.loads((REPO / "tools" / "_sf_rr4_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert rec["prior"] == SERIES_BEFORE_THE_BENCH == rec["arms"]["0"]["series"]
        # S14f p3 (October 25, 2026): this record's ALL was the standing series
        # until S14E-D12 moved it; the historical link reads the series before
        # the defender's muster, never the live BASELINE_SERIES.
        assert rec["arms"]["ALL"]["series"] == SERIES_BEFORE_THE_DEFENDERS_MUSTER
        assert rec["arms"]["B"]["first_divergence_vs_prior"] == 7
        assert rec["arms"]["J"]["first_divergence_vs_prior"] == 14
        for lever in ("N", "R", "P", "V", "H", "A", "O"):
            assert rec["arms"][lever]["series"] == rec["prior"], lever
        commissioned = {(n, m) for _t, n, m in rec["arms"]["ALL"]["reach"]["commissions"]}
        assert {("Spain", "Cuesta"), ("Sweden", "Toll")} <= commissioned
