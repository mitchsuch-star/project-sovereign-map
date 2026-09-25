"""GE-3 "The Congress of Paris" — the victory arm (row EP).

Spec: docs/ENDGAME_PLAN.md §2 (RULED) and §4; landing record ENDGAME_PLAN §6
GE-3; rules SYSTEMS_REFERENCE.md §66. Done-when §8 items 2 and 3:

  2. `summon the congress` is refused with named gate terms below 50 titled
     and accepted at 50; every great power answers every turn; each price
     on the table, applied, flips the court (driven pins per lever).
  3. The Premature arm loses; the boot board (35 titled) cannot summon;
     E1 fires on total elimination. The two ARMS are pinned DRIVEN — the
     committed fixtures played through the real driver, real end turns and
     all — in `tests/test_congress_review_round.py::TestTheArmsDriven`
     (review #61/#64: the `_tick` sittings below exercise the Congress's own
     tick, never the enemy phase, the coalition turn or the petitions'
     lapse, and are not the arms). The Pressburg arm's reach from the 1805
     boot, played, is GE-V's measurement.

Every staging drives the REAL seams — `congress.summon` / `/command`,
`game_end.process_end_of_turn` (the one per-turn caller), the capture and
declaration seams, `_ratify_treaty` — and every price pin APPLIES the
lever the table names and reads the answer back.
"""

import contextlib
import copy
import io
import json
import random
from pathlib import Path

import pytest

from backend.game_logic import coalition, congress, game_end
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCEN = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
           / "europe_1805.json")

# Provinces handed to France by TREATY to stage a summonable board (15 on
# top of the boot bloc's 35). Minors only, so the four great powers stand.
_STAGE_FROM = ("Hanover", "Denmark", "Portugal", "Sardinia", "Naples",
               "Saxony", "Hesse")


def _boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCEN)


def _stage_titles(w, need=None, keep=("Lisbon",)):
    """Title France up to `need` (default hold_titled) provinces by treaty."""
    need = congress.hold_titled(w) if need is None else need
    moved = []
    for nation in _STAGE_FROM:
        for region in sorted(w.get_nation_regions(nation)):
            if congress.titled(w)["count"] >= need:
                return moved
            if region in keep:
                continue
            w.regions[region].controller = "France"
            game_end.record_province_title(w, region, game_end.TITLE_TREATY,
                                           nation, "France")
            w.invalidate_active_nations_cache()
            moved.append(region)
    return moved


def _peace(w, court):
    w.diplomatic_states[w._make_diplo_key(court, "France")] = "PEACE"
    w.invalidate_active_nations_cache()


def _sit(w):
    _stage_titles(w)
    w.diplomatic_points = 6
    result = congress.summon(w)
    assert result["success"], result["message"]
    return result


def _tick(w, n=1):
    stamped = []
    for _ in range(n):
        w.current_turn += 1
        stamped += game_end.process_end_of_turn(w, turn_ended=w.current_turn - 1)
    return stamped


def _latch(w, court):
    """A signed war-ending treaty of a BEATEN court — the §2.4 treaty
    recognition (review #0: only a peace signed while the Congress sits, or
    one in which the court ceded to us, latches)."""
    _peace(w, court)
    congress.note_ratification(w, [court], True, beaten=[court])


def _satisfy_all(w):
    for court in congress.great_powers(w):
        _latch(w, court)


# ════════════════════════════════════════════════════════════════════════
# The flag and the record
# ════════════════════════════════════════════════════════════════════════

class TestTheFlagAndTheRecord:
    def test_the_1805_campaign_arms_the_congress_with_the_ruled_numbers(self):
        w = _boot()
        assert congress.armed(w)
        block = w.campaign_end
        for key, value in (("hold_titled", 45), ("congress_turns", 8),
                           ("recognition_threshold", 50),
                           ("refuser_weight_per_turn", 15),
                           ("congress_alarm_gate", 40), ("hold_alarm_ceiling", 80),
                           ("cs_shutout_pct", 60), ("sue_score", -40),
                           ("sweetener_per_1000", 10), ("sweetener_cap", 20),
                           ("dissolve_alarm", 15), ("congress_cooldown", 10)):
            assert block[key] == value, key

    def test_the_bare_and_the_tutorial_world_never_see_it(self):
        bare = WorldState(player_nation="France", sovereign_map="europe")
        assert not congress.armed(bare)
        assert congress.build_congress_payload(bare) is None
        assert congress.state_line(bare) is None
        assert congress.clock_payload(bare) is None

    def test_the_lever_down_disarms(self, monkeypatch):
        w = _boot()
        monkeypatch.setattr(congress, "THE_CONGRESS_SITS", False)
        assert not congress.armed(w)
        assert congress.build_congress_payload(w) is None

    def test_none_until_a_great_power_signs_or_a_summons(self):
        w = _boot()
        assert w.congress is None
        _tick(w, 3)
        assert w.congress is None, "the ambient board never writes the record"

    def test_the_one_field_round_trips(self):
        w = _boot()
        _sit(w)
        _tick(w, 2)
        data = json.loads(json.dumps(w.to_dict()))
        assert data["congress"]["status"] == congress.SITTING
        again = WorldState.from_dict(data)
        assert again.congress == w.congress
        assert congress.sitting(again)

    def test_a_pre_ge3_save_loads_with_none(self):
        w = _boot()
        data = json.loads(json.dumps(w.to_dict()))
        data.pop("congress", None)
        assert WorldState.from_dict(data).congress is None

    def test_a_ge1_block_without_the_congress_keys_falls_back_to_the_defaults(self):
        w = _boot()
        w.campaign_end = {"verdict_turn": 44, "fall_grace_turns": 5,
                          "captivity_grace_turns": 10, "title_turns": 12}
        assert congress.hold_titled(w) == congress.HOLD_TITLED
        assert congress.congress_turns(w) == congress.CONGRESS_TURNS
        assert congress.sue_score(w) == congress.SUE_SCORE


class TestTheValidator:
    def _v(self, block):
        from backend.modding.validator import validate_scenario
        return validate_scenario({"sovereign_map": "europe", "player_nation": "France",
                                  "campaign_end": block}, check_adjacency=False)

    def test_the_congress_keys_are_known(self):
        result = self._v({"verdict_turn": 44, "hold_titled": 50, "sue_score": -40,
                          "cs_shutout_pct": 60, "congress_cooldown": 10})
        assert result.is_valid
        assert not [e for e in result.warnings if "campaign_end" in e.path]

    def test_out_of_range_congress_keys_are_errors(self):
        assert any("sue_score" in e.path for e in self._v(
            {"verdict_turn": 44, "sue_score": 10}).errors)
        assert any("cs_shutout_pct" in e.path for e in self._v(
            {"verdict_turn": 44, "cs_shutout_pct": 0.6}).errors)


# ════════════════════════════════════════════════════════════════════════
# The summons — the gate terms (§2.3, done-when §8.2 first half)
# ════════════════════════════════════════════════════════════════════════

class TestTheGate:
    def test_boot_reads_the_gate_with_35_of_50(self):
        w = _boot()
        assert congress.titled(w)["count"] == 35
        assert congress.phase(w) == "gate"
        line = congress.state_line(w)
        assert line.startswith("THE CONGRESS OF PARIS — 35 of 45 titled")
        assert line.endswith(congress.CABINET_HINT)
        refusal = congress.summon_refusal(w)
        assert "35 titled provinces" in refusal and "45 are needed" in refusal

    def test_the_held_unsettled_provinces_are_named(self):
        w = _boot()
        w.regions["Tyrol"].controller = "France"
        game_end.record_province_title(w, "Tyrol", game_end.TITLE_CONQUEST,
                                       "Austria", "France")
        w.invalidate_active_nations_cache()
        assert "(1 held, unsettled: Tyrol)" in congress.state_line(w)

    def test_at_fifty_titled_it_may_be_summoned(self):
        w = _boot()
        _stage_titles(w)
        assert congress.titled(w)["count"] == 45
        assert congress.summon_refusal(w) is None
        assert "the powers may be summoned" in congress.state_line(w)

    @pytest.mark.parametrize("breaker, key", [
        ("capital", "capital"),
        ("emperor", "emperor"),
        ("brink", "satellites"),
        ("dp", "dp"),
    ])
    def test_every_gate_term_blocks_by_name(self, breaker, key):
        w = _boot()
        # Slack for the term under test: Paris lost is one titled province
        # fewer, and a satellite below loyalty 40 un-titles its homeland
        # (Holland's four) — the titled term would otherwise speak first.
        _stage_titles(w, need=55)
        w.diplomatic_points = 6
        if breaker == "capital":
            w.regions["Paris"].controller = "Britain"
            w.invalidate_active_nations_cache()
        elif breaker == "emperor":
            w.marshals["Napoleon"].captured_by = "Austria"
        elif breaker == "brink":
            w.vassals["Holland"]["loyalty"] = 8
        elif breaker == "dp":
            w.diplomatic_points = 1
        terms = {t["key"]: t for t in congress.gate_terms(w)}
        assert terms[key]["met"] is False
        refusal = congress.summon_refusal(w)
        assert refusal == terms[key]["refusal"]
        assert congress.summon(w)["success"] is False

    def test_the_refusal_is_the_first_unmet_term_in_executor_order(self):
        w = _boot()
        w.diplomatic_points = 0
        w.regions["Paris"].controller = "Britain"
        w.invalidate_active_nations_cache()
        terms = [t for t in congress.gate_terms(w) if t["key"] != "admin"]
        first = next(t for t in terms if not t["met"])
        assert first["key"] == "titled"
        assert congress.summon_refusal(w) == first["refusal"]

    def test_a_sitting_congress_and_a_signed_peace_refuse_a_second_summons(self):
        w = _boot()
        _sit(w)
        assert "already sits" in congress.summon_refusal(w)

    def test_the_cooldown_after_a_dissolution(self):
        w = _boot()
        _sit(w)
        w.regions["Paris"].controller = "Britain"
        w.invalidate_active_nations_cache()
        _tick(w)
        assert w.congress["status"] == congress.DISSOLVED
        w.regions["Paris"].controller = "France"
        w.invalidate_active_nations_cache()
        # The dissolution itself raised the alarm (+15, to 85) — the alarm
        # term would speak first; calm it to read the cooldown's own words.
        assert int(w.threat_level) >= 80
        w.threat_by_target["France"] = 60
        assert congress.cooldown_left(w) == 9
        assert "will not answer another summons" in congress.summon_refusal(w)
        assert congress.phase(w) == "cooldown"
        assert "may be summoned again on turn" in congress.state_line(w)
        _tick(w, 9)
        assert congress.cooldown_left(w) == 0
        assert congress.summon_refusal(w) is None

    def test_summon_opens_the_sitting_and_logs_beat_one(self):
        w = _boot()
        before = len(w.event_log)
        result = _sit(w)
        c = w.congress
        assert c["status"] == congress.SITTING and c["number"] == 1
        assert c["ends_turn"] == c["summoned_turn"] + 8
        assert set(c["answers"]) == set(congress.great_powers(w))
        summoned = [e for e in w.event_log[before:]
                    if e.get("type") == "congress" and e.get("phase") == "summoned"]
        assert len(summoned) == 1
        assert "The Emperor summons the powers of Europe to Paris" in result["message"]
        assert "declare no war" in result["message"]


class TestTheSummonsDriven:
    """`summon the congress` through the real /command road (done-when §8.2)."""

    @pytest.fixture
    def client(self, monkeypatch):
        from fastapi.testclient import TestClient
        import backend.main as M
        from tests._chip_census import board_env
        prior = (M.world, M.game_state.get("world"), M.parser)
        board_env(monkeypatch)
        yield TestClient(M.app), M
        M.world = prior[0]
        M.game_state["world"] = prior[1]
        M.parser = prior[2]

    def _post(self, tc, text):
        with contextlib.redirect_stdout(io.StringIO()):
            return tc.post("/command", json={"command": text}).json()

    def test_refused_at_boot_with_the_named_term_and_nothing_spent(self, client):
        tc, M = client
        w = M.world
        dp, admin = w.diplomatic_points, w.admin_actions_remaining
        r = self._post(tc, "summon the congress")
        assert r["success"] is False
        assert "35 titled provinces" in r["message"]
        assert w.diplomatic_points == dp and w.admin_actions_remaining == admin
        assert w.congress is None

    def test_accepted_at_fifty_for_two_dp_and_one_admin_action(self, client):
        tc, M = client
        w = M.world
        _stage_titles(w)
        w.diplomatic_points = 5
        admin = w.admin_actions_remaining
        r = self._post(tc, "summon the congress")
        assert r["success"] is True, r["message"]
        assert w.diplomatic_points == 3
        assert w.admin_actions_remaining == admin - 1
        assert congress.sitting(w)

    def test_a_question_never_summons(self, client):
        tc, M = client
        w = M.world
        _stage_titles(w)
        w.diplomatic_points = 5
        self._post(tc, "can we summon the congress?")
        assert not congress.sitting(w)

    def test_get_congress_is_the_one_payload(self, client):
        tc, M = client
        with contextlib.redirect_stdout(io.StringIO()):
            body = tc.get("/congress").json()
        assert body["success"] is True and body["armed"] is True
        assert body["phase"] == "gate" and body["titled"] == 35
        assert [c["nation"] for c in body["courts"]] == congress.great_powers(M.world)
        assert body["available"] is False

    def test_the_wizard_row_rides_the_nation_list(self, client):
        tc, M = client
        with contextlib.redirect_stdout(io.StringIO()):
            body = tc.get("/diplomatic_preview").json()
        row = body["congress"]
        assert row["command"] == congress.SUMMON_COMMAND
        full = congress.build_congress_payload(M.world)
        assert row["gate_terms"] == full["gate_terms"]
        assert row["available"] is False
        assert row["unavailable_reason"] == full["unavailable_reason"]

    def test_the_diplomatic_ledger_carries_the_table(self, client):
        tc, M = client
        with contextlib.redirect_stdout(io.StringIO()):
            body = tc.get("/diplomatic_ledger").json()
        assert body["ledger"]["congress"]["phase"] == "gate"


# ════════════════════════════════════════════════════════════════════════
# The table — how a court answers (§2.4)
# ════════════════════════════════════════════════════════════════════════

class TestTheTable:
    def test_every_great_power_answers(self):
        w = _boot()
        rows = {c: congress.answer(w, c) for c in congress.great_powers(w)}
        assert set(rows) == {"Britain", "Russia", "Austria", "Prussia"}
        assert {r["stance"] for r in rows.values()} <= set(congress.STANCES)
        # At boot three courts are at war with France; Prussia at peace.
        for court in ("Britain", "Russia", "Austria"):
            assert rows[court]["by"] == "war"
        assert rows["Prussia"]["by"] == "formula"

    def test_gone_by_elimination_and_by_vassalage(self):
        w = _boot()
        for region in list(w.get_nation_regions("Austria")):
            w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        assert congress.answer(w, "Austria")["stance"] == congress.GONE
        w.vassals["Prussia"] = {"lord": "France", "loyalty": 60}
        w.invalidate_active_nations_cache()
        row = congress.answer(w, "Prussia")
        assert row["stance"] == congress.GONE and row["by"] == "vassal"

    def test_at_war_refuses_and_sues_at_minus_forty_or_its_capital(self, monkeypatch):
        w = _boot()
        _sit(w)
        from backend.game_logic import diplomacy
        scores = {"Austria": -12}
        monkeypatch.setattr(diplomacy, "get_war_score_for",
                            lambda world, a, b: scores.get(a, 0))
        assert congress.answer(w, "Austria")["stance"] == congress.REFUSES
        scores["Austria"] = -40
        row = congress.answer(w, "Austria")
        assert row["stance"] == congress.SUES
        assert congress.court_must_sue(w, "Austria")
        scores["Austria"] = -5
        w.regions["Vienna"].controller = "France"
        w.invalidate_active_nations_cache()
        assert congress.answer(w, "Austria")["stance"] == congress.SUES

    def test_the_treaty_latch_recognizes_and_a_new_war_breaks_it(self):
        w = _boot()
        _latch(w, "Austria")
        row = congress.answer(w, "Austria")
        assert row["stance"] == congress.RECOGNIZES and row["by"] == "treaty"
        from backend.game_logic.diplomacy import set_diplomatic_state
        with contextlib.redirect_stdout(io.StringIO()):
            set_diplomatic_state(w, "France", "Austria", "WAR", "war_declaration")
        assert congress.answer(w, "Austria")["by"] == "war"
        assert w.congress["signed"]["Austria"]["broken"]["reason"] == "a new war"

    def test_a_white_peace_before_the_summons_does_not_latch(self):
        """Review #0: the first cut latched EVERY war-ending peace at any
        time — the commanded arm's turn-4 peace settled three of the four
        answers years before the summons. Only a beaten court's peace, or
        one signed while the Congress sits, latches."""
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w._ratify_treaty({"proposer_nation": "Austria", "target_nation": "France",
                              "type": "peace", "demands": [], "sweeteners": []})
        assert not ((w.congress or {}).get("signed") or {}).get("Austria")
        assert congress.answer(w, "Austria")["by"] == "formula"

    def test_a_peace_the_emperor_gave_ground_in_never_latches(self):
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w._ratify_treaty({"proposer_nation": "Austria", "target_nation": "France",
                              "type": "peace", "sweeteners": [],
                              "demands": [{"type": "territory_cede",
                                           "regions": ["Rhineland"]}]})
        assert not ((w.congress or {}).get("signed") or {}).get("Austria")

    def test_the_beaten_courts_peace_latches(self):
        """Pressburg: Austria cedes to the Emperor, and recognizes the
        order it signed — through the real ratifier."""
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w._ratify_treaty({"proposer_nation": "France", "target_nation": "Austria",
                              "type": "peace", "sweeteners": [],
                              "demands": [{"type": "territory_cede",
                                           "regions": ["Tyrol"]}]})
        assert w.congress["signed"]["Austria"]["broken"] is None
        assert w.congress["signed"]["Austria"]["kind"] == "beaten"
        row = congress.answer(w, "Austria")
        assert row["stance"] == congress.RECOGNIZES and row["by"] == "treaty"

    def test_a_peace_signed_at_the_table_latches(self):
        w = _boot()
        _sit(w)
        with contextlib.redirect_stdout(io.StringIO()):
            w._ratify_treaty({"proposer_nation": "Austria", "target_nation": "France",
                              "type": "peace", "demands": [], "sweeteners": []})
        assert w.congress["signed"]["Austria"]["kind"] == "table"
        assert congress.answer(w, "Austria")["stance"] == congress.RECOGNIZES

    def test_a_truce_does_not_latch(self):
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w._ratify_treaty({"proposer_nation": "Austria", "target_nation": "France",
                              "type": "armistice", "demands": [], "sweeteners": []})
        assert not ((w.congress or {}).get("signed") or {}).get("Austria")

    def test_a_french_capture_from_its_bloc_breaks_the_latch(self):
        w = _boot()
        _latch(w, "Austria")
        w.capture_region("Tyrol", "France")
        rec = w.congress["signed"]["Austria"]
        assert rec["broken"] and "Tyrol" in rec["broken"]["reason"]
        assert congress.answer(w, "Austria")["stance"] == congress.REFUSES

    def test_the_formula_components_sum_to_the_score(self):
        w = _boot()
        row = congress.answer(w, "Prussia")
        assert row["score"] == sum(c["value"] for c in row["components"])
        rel = next(c for c in row["components"] if c["key"] == "relation")
        assert rel["value"] == -10

    @pytest.mark.parametrize("state, bonus", [
        ("ALLIANCE", 20), ("DEFENSIVE_ALLIANCE", 10), ("NON_AGGRESSION", 5),
        ("OPEN_BORDERS", 5), ("PEACE", 0)])
    def test_the_treaty_bonus(self, state, bonus):
        w = _boot()
        w.diplomatic_states[w._make_diplo_key("Prussia", "France")] = state
        w.invalidate_active_nations_cache()
        comps = {c["key"]: c["value"] for c in congress.answer(w, "Prussia")["components"]}
        assert comps["treaty"] == bonus

    def test_war_weariness_at_sixty_is_worth_ten(self):
        w = _boot()
        w.war_exhaustion["Prussia"] = 59
        base = congress.recognition_score(w, "Prussia")["score"]
        w.war_exhaustion["Prussia"] = 60
        assert congress.recognition_score(w, "Prussia")["score"] == base + 10

    def test_an_acquire_design_on_french_held_soil_is_minus_twelve(self):
        w = _boot()
        comps = {c["key"]: c for c in congress.answer(w, "Prussia")["components"]}
        assert comps["design"]["value"] == 0
        w.regions["Hanover"].controller = "France"
        w.invalidate_active_nations_cache()
        comps = {c["key"]: c for c in congress.answer(w, "Prussia")["components"]}
        assert comps["design"]["value"] == -12
        assert "Hanover" in comps["design"]["label"]

    def test_a_design_bought_off_by_france_is_plus_twelve(self):
        from backend.game_logic.instruments import create_compensation_bargain
        w = _boot()
        w.regions["Hanover"].controller = "France"
        w.invalidate_active_nations_cache()
        create_compensation_bargain(w, payer="France", recipient="Prussia",
                                    design_id="hanoverian_prize", granted={"gold": 1})
        comps = {c["key"]: c["value"] for c in congress.answer(w, "Prussia")["components"]}
        assert comps["design"] == 12

    def test_the_arbiter_fears_early_every_other_court_late(self):
        w = _boot()
        _stage_titles(w)
        _peace(w, "Russia")
        _peace(w, "Austria")
        russia = {c["key"]: c["value"] for c in congress.answer(w, "Russia")["components"]}
        austria = {c["key"]: c["value"] for c in congress.answer(w, "Austria")["components"]}
        assert russia["fear"] < austria["fear"] <= 0

    def test_a_court_inside_our_bloc_does_not_fear_it(self):
        w = _boot()
        _stage_titles(w)
        w.diplomatic_states[w._make_diplo_key("Prussia", "France")] = "ALLIANCE"
        w.invalidate_active_nations_cache()
        comps = {c["key"]: c["value"] for c in congress.answer(w, "Prussia")["components"]}
        assert comps["fear"] == 0

    def test_the_jitter_is_zero_on_the_historical_seed_and_bounded_otherwise(self):
        w = _boot()
        comps = {c["key"]: c["value"] for c in congress.answer(w, "Prussia")["components"]}
        assert comps["jitter"] == 0
        w.campaign_seed = "austerlitz"
        w.current_turn = 30
        values = set()
        for n in range(1, 6):
            w.congress = {"number": n}
            comps = {c["key"]: c["value"] for c in congress.answer(w, "Prussia")["components"]}
            assert -3 <= comps["jitter"] <= 3
            values.add(comps["jitter"])
        assert len(values) > 1

    def test_a_truce_takes_the_formula_and_says_so(self):
        w = _boot()
        w.diplomatic_states[w._make_diplo_key("Austria", "France")] = "ARMISTICE"
        w.invalidate_active_nations_cache()
        row = congress.answer(w, "Austria")
        assert row["by"] == "formula"
        assert row["reason"].startswith("a truce is not a peace")


class TestShutOut:
    def _close(self, w, n=16):
        from backend.game_logic import naval
        # Shut ports by putting Continental coast courts at war with Britain.
        for nation in ("Portugal", "Denmark", "Sweden", "Ottoman", "Naples",
                       "Prussia", "Russia", "Austria", "Sardinia"):
            if round(naval.closure_against(w, "Britain") * naval.continental_ports_total(w)) >= n:
                return
            w.diplomatic_states[w._make_diplo_key(nation, "Britain")] = "WAR"
        w.invalidate_active_nations_cache()

    def test_london_is_shut_out_at_sixty_percent_with_no_corps_abroad(self):
        w = _boot()
        row = congress.answer(w, "Britain")
        assert row["stance"] == congress.REFUSES
        assert row["shut_out"]["needed"] == 16
        self._close(w)
        row = congress.answer(w, "Britain")
        assert row["stance"] == congress.SHUT_OUT
        assert "16 of 26 ports" in row["reason"] or "of 26 ports" in row["reason"]

    def test_a_british_corps_on_the_continent_keeps_her_at_the_table(self):
        w = _boot()
        self._close(w)
        moore = next(m for m in w.marshals.values() if m.nation == "Britain")
        moore.location = "Flanders"
        assert congress.answer(w, "Britain")["stance"] != congress.SHUT_OUT
        assert moore.name in congress.corps_on_the_continent(w, "Britain")

    def test_once_the_ports_fall_short_in_a_sitting_she_is_not_shut_out_again(self):
        w = _boot()
        _sit(w)
        _tick(w)                       # the ports fall short at an end turn
        assert w.congress["shut_out_broken"] is True
        self._close(w)
        assert congress.answer(w, "Britain")["stance"] != congress.SHUT_OUT


# ════════════════════════════════════════════════════════════════════════
# The price — each lever, APPLIED, moves the court by what the table says
# (shown = applied) and the bundle flips it (done-when §8.2).
# ════════════════════════════════════════════════════════════════════════

class TestThePriceIsTrue:
    def _prussia_near(self, w, target_score):
        """Stage Prussia at peace with its score at `target_score`."""
        base = congress.recognition_score(w, "Prussia")["score"]
        key = w._make_diplo_key("Prussia", "France")
        w.nation_relations[key] = int(w.nation_relations.get(key, 0)) + (target_score - base)
        return congress.recognition_score(w, "Prussia")["score"]

    def test_every_lever_moves_the_score_by_its_stated_value(self):
        from backend.game_logic.instruments import create_compensation_bargain
        w = _boot()
        _sit(w)
        w.regions["Hanover"].controller = "France"
        w.invalidate_active_nations_cache()
        row = congress.answer(w, "Prussia")
        pr = congress.price(w, "Prussia", row)
        levers = {lv["key"]: lv for lv in pr["levers"]}
        base = row["score"]
        assert set(levers) >= {"sweetener", "design", "treaty", "relation"}
        # the design lever — applied for real
        design = levers["design"]
        for design_id in design["chain"]:
            create_compensation_bargain(w, payer="France", recipient="Prussia",
                                        design_id=design_id, granted={"gold": 1})
        after_design = congress.recognition_score(w, "Prussia")["score"]
        assert after_design - base == design["value"]
        # the treaty lever — the best treaty the relation lets it RATIFY
        # (review #1: an alliance at relation −10 is refused by the ratifier),
        # applied through the real ratifier, never a direct state write.
        treaty = levers["treaty"]
        assert treaty["state"] != "ALLIANCE"
        with contextlib.redirect_stdout(io.StringIO()):
            result = w._ratify_treaty({"proposer_nation": "France",
                                       "target_nation": "Prussia",
                                       "type": treaty["state"].lower(),
                                       "demands": [], "sweeteners": []})
        assert result.get("type") != "diplomatic_treaty_failed", result
        assert w.get_diplomatic_state("Prussia", "France") == treaty["state"]
        after_treaty = congress.recognition_score(w, "Prussia")["score"]
        assert after_treaty - after_design == treaty["value"]

    def test_the_bundle_applied_flips_the_court(self):
        from backend.game_logic.instruments import create_compensation_bargain
        w = _boot()
        w.nation_gold["France"] = 20000
        _sit(w)
        w.regions["Hanover"].controller = "France"
        w.invalidate_active_nations_cache()
        row = congress.answer(w, "Prussia")
        assert row["stance"] == congress.REFUSES
        pr = congress.price(w, "Prussia", row)
        assert pr["bundle"], pr["text"]
        for lever in pr["bundle"]:
            key = lever["key"]
            if key == "sweetener":
                assert congress.pay_sweetener(w, "Prussia", lever["gold"])["success"]
            elif key == "design":
                for design_id in lever["chain"]:
                    create_compensation_bargain(w, payer="France", recipient="Prussia",
                                                design_id=design_id, granted={"gold": 1})
            elif key == "treaty":
                w.diplomatic_states[w._make_diplo_key("Prussia", "France")] = lever["state"]
                w.invalidate_active_nations_cache()
            elif key == "relation":
                rel = w._make_diplo_key("Prussia", "France")
                w.nation_relations[rel] = int(w.nation_relations[rel]) + int(lever["value"])
        assert congress.answer(w, "Prussia")["stance"] == congress.RECOGNIZES

    def test_a_sweetener_alone_flips_a_court_near_the_line(self):
        w = _boot()
        w.nation_gold["France"] = 5000
        _sit(w)
        self._prussia_near(w, 42)
        row = congress.answer(w, "Prussia")
        pr = congress.price(w, "Prussia", row)
        assert pr["bundle"] and [lv["key"] for lv in pr["bundle"]] == ["sweetener"]
        gold = pr["bundle"][0]["gold"]
        assert gold == 800 and "800g sweetener" in pr["text"]
        result = congress.pay_sweetener(w, "Prussia", gold)
        assert result["success"], result["message"]
        assert congress.answer(w, "Prussia")["stance"] == congress.RECOGNIZES
        assert w.nation_gold["France"] == 5000 - 800

    def test_the_sweetener_is_capped_and_the_excess_is_not_taken(self):
        w = _boot()
        w.nation_gold["France"] = 9000
        _sit(w)
        r = congress.pay_sweetener(w, "Prussia", 5000)
        assert r["success"] and r["charge"] == 2000
        assert w.nation_gold["France"] == 7000
        comps = {c["key"]: c["value"] for c in congress.answer(w, "Prussia")["components"]}
        assert comps["sweetener"] == 20
        again = congress.pay_sweetener(w, "Prussia", 1000)
        assert again["success"] is False and "most gold can buy" in again["message"]

    @pytest.mark.parametrize("why, expect", [
        ("not_sitting", "summon the Congress first"),
        ("at_war", "at war with Austria"),
        ("not_a_power", "not a great power"),
    ])
    def test_the_sweetener_refusals(self, why, expect):
        w = _boot()
        court = "Prussia"
        if why != "not_sitting":
            _sit(w)
        if why == "at_war":
            court = "Austria"
        if why == "not_a_power":
            court = "Bavaria"
        refusal = congress.sweetener_refusal(w, court, 1000)
        assert refusal and expect.lower() in refusal.lower()

    def test_the_war_lever_leads_to_a_suing_peace_that_recognizes(self, monkeypatch):
        """Beat Austria to −40 → it SUES, the Congress rung sends a peace
        carrying the recognition clause, ratifying it latches RECOGNIZES."""
        from backend.game_logic import ai_diplomacy, diplomacy
        w = _boot()
        _sit(w)
        key = w._make_diplo_key("Austria", "France")
        w.war_scores[key] = 40 if key.startswith("Austria") is False else -40
        assert diplomacy.get_war_score_for(w, "Austria", "France") <= -40
        assert congress.answer(w, "Austria")["stance"] == congress.SUES
        with contextlib.redirect_stdout(io.StringIO()):
            proposal = ai_diplomacy.process_diplomatic_phase("Austria", w)
        assert proposal and proposal.get("congress_recognition")
        assert "congress_recognition" in proposal["terms"]["clauses"]
        assert proposal["proposal_type"] == "peace" or proposal.get("type") == "peace"
        congress.note_ratification(w, ["Austria"], True)
        _peace(w, "Austria")
        assert congress.answer(w, "Austria")["stance"] == congress.RECOGNIZES

    def test_the_sue_rung_is_dormant_without_a_congress(self):
        from backend.game_logic import ai_diplomacy
        w = _boot()
        key = w._make_diplo_key("Austria", "France")
        w.war_scores[key] = 40 if not key.startswith("Austria") else -40
        with contextlib.redirect_stdout(io.StringIO()):
            proposal = ai_diplomacy.process_diplomatic_phase("Austria", w)
        assert not (proposal or {}).get("congress_recognition")


# ════════════════════════════════════════════════════════════════════════
# The hold and the tick (§2.5–§2.6)
# ════════════════════════════════════════════════════════════════════════

class TestTheHold:
    def test_the_seven_conditions(self):
        w = _boot()
        _sit(w)
        keys = [h["key"] for h in congress.hold_conditions(w)]
        assert keys == ["titled", "capital", "emperor", "satellites", "lost",
                        "declared", "alarm"]
        assert all(h["met"] for h in congress.hold_conditions(w))

    @pytest.mark.parametrize("breaker, key", [
        ("capital", "capital"), ("emperor", "emperor"), ("titled", "titled"),
        ("alarm", "alarm"),
    ])
    def test_a_broken_condition_dissolves_at_the_tick(self, breaker, key):
        w = _boot()
        if breaker != "titled":
            _stage_titles(w, need=51)   # Paris lost must not also be the count
        _sit(w)
        alarm_before = int(w.threat_level)
        if breaker == "capital":
            w.regions["Paris"].controller = "Britain"
        elif breaker == "emperor":
            w.marshals["Napoleon"].captured_by = "Austria"
        elif breaker == "titled":
            w.regions["Brittany"].controller = "Britain"
        elif breaker == "alarm":
            w.threat_by_target["France"] = 85
            alarm_before = 85
        w.invalidate_active_nations_cache()
        _tick(w)
        c = w.congress
        assert c["status"] == congress.DISSOLVED
        assert c["dissolve_key"] == key
        assert int(w.threat_level) >= min(100, alarm_before + 15) - 1

    def test_a_titled_province_lost_and_retaken_the_same_turn_still_breaks_it(self):
        w = _boot()
        _sit(w)
        w.capture_region("Brittany", "Britain")
        w.capture_region("Brittany", "France")
        assert "Brittany" in w.congress["lost"]
        _tick(w)
        assert w.congress["dissolve_key"] == "lost"

    def test_a_french_declaration_breaks_it(self):
        from backend.game_logic.diplomacy import declare_war
        w = _boot()
        _sit(w)
        with contextlib.redirect_stdout(io.StringIO()):
            declare_war(w, "France", "Sweden")
        assert w.congress["declared"] == ["Sweden"]
        _tick(w)
        assert w.congress["dissolve_key"] == "declared"

    def test_a_declaration_on_france_does_not(self):
        from backend.game_logic.diplomacy import declare_war
        w = _boot()
        _sit(w)
        with contextlib.redirect_stdout(io.StringIO()):
            declare_war(w, "Sweden", "France")
        assert w.congress["declared"] == []

    def test_a_satellite_rebellion_breaks_it(self):
        from backend.game_logic.vassal import record_vassal_break
        w = _boot()
        _sit(w)
        record_vassal_break(w, vassal="Switzerland", lord="France",
                            exit_path="vassal_rebellion")
        assert w.congress["rebellions"] == ["Switzerland"]
        _tick(w)
        assert w.congress["dissolve_key"] == "satellites"

    def test_the_strip_records_every_end_turn(self):
        w = _boot()
        _sit(w)
        _tick(w, 3)
        strip = w.congress["strip"]
        assert [s["day"] for s in strip] == [0, 1, 2]
        assert all(s["held"] for s in strip)
        assert set(strip[0]["stances"]) == set(congress.great_powers(w))

    def test_the_clock_line_while_it_sits(self):
        w = _boot()
        _sit(w)
        assert "the powers gather" in congress.state_line(w)
        _tick(w, 3)
        line = congress.state_line(w)
        assert line.startswith("THE CONGRESS SITS — turn 3 of 8 · 45 of 45 titled")
        assert congress.clock_payload(w)["phase"] == "sitting"


class TestTheResolution:
    def test_the_eighth_turn_all_signed_is_the_imperial_peace(self):
        w = _boot()
        _sit(w)
        _satisfy_all(w)
        stamped = _tick(w, 8)
        assert not stamped
        stamped = _tick(w)
        assert [r["cause"] for r in stamped] == [game_end.CAUSE_IMPERIAL_PEACE]
        rec = stamped[0]
        assert rec["terminal"] is False and not getattr(w, "game_over", False)
        assert rec["register"] == "imperial_peace"
        block = rec["summary"]["congress"]
        assert block["route"] == "congress"
        assert {c["stance"] for c in block["courts"]} == {"SIGNED"}
        assert [s["day"] for s in block["sitting"]] == list(range(1, 9))
        assert block["moniteur_line"].startswith("LE MONITEUR — Paris,")
        assert "epilogue" not in rec["summary"]
        assert w.congress["status"] == congress.CONCLUDED

    def test_the_imperial_peace_never_fires_twice(self):
        w = _boot()
        _sit(w)
        _satisfy_all(w)
        _tick(w, 9)
        assert game_end.has_ending(w, game_end.CAUSE_IMPERIAL_PEACE)
        assert "The Imperial Peace is signed" in congress.summon_refusal(w)
        assert congress.state_line(w) is None
        assert _tick(w) == []

    def test_the_eighth_turn_unsigned_dissolves_naming_the_courts(self):
        w = _boot()
        _sit(w)
        _tick(w, 9)
        c = w.congress
        assert c["status"] == congress.DISSOLVED and c["dissolve_key"] == "unsigned"
        assert "would not sign" in c["dissolve_reason"]
        assert set(c["refusers"]) == {"Britain", "Russia", "Austria", "Prussia"}
        dissolved = [e for e in w.event_log if e.get("type") == "congress"
                     and e.get("phase") == "dissolved"]
        assert dissolved and dissolved[-1]["refusers"] == c["refusers"]

    def test_the_verdict_after_the_imperial_peace_is_never_contested(self):
        w = _boot()
        _sit(w)
        _satisfy_all(w)
        _tick(w, 9)
        tier = game_end.verdict_tier(w)
        assert tier["tier"] in ("ascendant", "triumph")
        assert "signed the order at Paris" in " ".join(tier["lines"])

    def test_a_humbled_peace_after_it_still_forces_the_eclipse(self):
        w = _boot()
        _sit(w)
        _satisfy_all(w)
        _tick(w, 9)
        game_end.record_ending(w, "defeat", game_end.CAUSE_HUMBLED)
        assert game_end.verdict_tier(w)["tier"] == "eclipse"

    def test_the_end_turn_payload_leads_with_the_gold_card(self):
        from backend.game_logic.turn_manager import _attach_endings
        w = _boot()
        before = len(game_end.endings(w))
        _sit(w)
        _satisfy_all(w)
        _tick(w, 9)
        game_end.record_ending(w, "verdict", game_end.CAUSE_VERDICT)
        result = {}
        _attach_endings(result, w, before)
        assert result["ending"]["cause"] == game_end.CAUSE_IMPERIAL_PEACE

    def test_a_fall_this_turn_ends_everything_no_dissolution(self):
        w = _boot()
        _sit(w)
        game_end.record_ending(w, "defeat", game_end.CAUSE_EAGLE_FALLS)
        alarm = int(w.threat_level)
        # Review #49: the Fall CLOSES the sitting — no dissolution's alarm,
        # and no surface left saying it sits.
        assert w.congress["status"] == congress.ENDED
        _tick(w)
        assert w.congress["status"] == congress.ENDED
        assert int(w.threat_level) <= alarm + 3
        assert congress.phase(w) == "ended"
        assert congress.state_line(w) is None
        assert congress.summon(w)["success"] is False


class TestTheUniversalMonarchy:
    def _empty(self):
        w = _boot()
        for court in congress.great_powers(w):
            for region in list(w.get_nation_regions(court)):
                w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        return w

    def test_e1_fires_at_the_first_end_turn_without_a_congress(self):
        w = self._empty()
        assert congress.no_great_power_stands(w)
        stamped = _tick(w)
        assert [r["cause"] for r in stamped] == [game_end.CAUSE_IMPERIAL_PEACE]
        assert stamped[0]["cause_line"] == ("No great power remains to contest the "
                                            "order of the French Empire.")
        assert stamped[0]["summary"]["congress"]["route"] == "universal_monarchy"

    def test_a_vassalized_great_power_counts_as_gone(self):
        w = _boot()
        for court in ("Britain", "Russia", "Austria"):
            for region in list(w.get_nation_regions(court)):
                w.regions[region].controller = "France"
        w.vassals["Prussia"] = {"lord": "France", "loyalty": 60}
        w.invalidate_active_nations_cache()
        assert congress.no_great_power_stands(w)

    def test_the_lever_down_keeps_it_quiet(self, monkeypatch):
        w = self._empty()
        monkeypatch.setattr(congress, "THE_UNIVERSAL_MONARCHY", False)
        assert _tick(w) == []

    def test_the_declared_line_is_kept_for_a_detail_less_stamp(self):
        assert game_end._cause_line(_boot(), game_end.CAUSE_IMPERIAL_PEACE, {}) == \
            "Europe accepts the order of the French Empire."


# ════════════════════════════════════════════════════════════════════════
# Refusal has teeth — the pressure readers (§2.5), dormant with no Congress
# ════════════════════════════════════════════════════════════════════════

class TestThePressure:
    def test_every_reader_is_dormant_with_no_congress(self):
        w = _boot()
        for court in congress.great_powers(w):
            assert congress.refusal_weight(w, court, "France") == 0
            assert congress.refuser_qualifies(w, court, "France") is False
        assert congress.coalition_gate(w) is None
        assert coalition.brewing_gate(w) == coalition.THREAT_BREWING_MIN
        assert congress.peace_dividend(w, "France") == 1.0
        assert congress.petition_stakes(w, "France") == 1
        assert congress.grudge_contributions(w, 2) == []

    def test_a_refuser_hardens_fifteen_a_turn(self):
        w = _boot()
        _sit(w)
        assert congress.refusal_turns(w, "Prussia") == 0
        _tick(w, 2)
        assert congress.refusal_turns(w, "Prussia") == 2
        assert congress.refusal_weight(w, "Prussia", "France") == 30
        assert congress.refusal_weight(w, "Prussia", "Austria") == 0

    def test_the_refusal_term_reaches_the_intent_weight(self):
        from backend.game_logic import intent
        w = _boot()
        _sit(w)
        _tick(w, 2)
        view = intent.get_nation_intent("Austria", w)
        if view.against != "France":
            pytest.skip("Austria's design is not aimed at France on this board")
        with_term = view.weight
        import backend.game_logic.congress as C
        old = C.THE_CONGRESS_HARDENS_REFUSERS
        try:
            C.THE_CONGRESS_HARDENS_REFUSERS = False
            w._intent_cache = None
            without = intent.get_nation_intent("Austria", w).weight
        finally:
            C.THE_CONGRESS_HARDENS_REFUSERS = old
            w._intent_cache = None
        assert with_term >= without
        assert with_term == min(100, without + congress.refusal_weight(w, "Austria", "France"))

    def test_the_gate_drops_to_forty_with_two_refusers(self):
        w = _boot()
        _sit(w)
        assert len(congress.stored_refusers(w)) >= 2
        assert congress.coalition_gate(w) == 40
        assert coalition.brewing_gate(w) == 40
        assert coalition.get_threat_tier(45, brewing_at=coalition.brewing_gate(w)) == "Brewing"
        assert coalition.get_threat_tier(45) == "Murmurs"

    def test_a_friendly_refuser_qualifies_for_the_coalition_while_it_sits(self):
        w = _boot()
        key = w._make_diplo_key("Prussia", "France")
        w.nation_relations[key] = 5
        assert not coalition.qualifies_for_coalition("Prussia", w)
        _sit(w)
        assert congress.answer(w, "Prussia")["stance"] == congress.REFUSES
        assert coalition.qualifies_for_coalition("Prussia", w)

    def test_a_recognizer_is_never_marched(self):
        w = _boot()
        key = w._make_diplo_key("Prussia", "France")
        w.nation_relations[key] = 5
        _sit(w)
        _latch(w, "Prussia")
        _tick(w)
        assert congress.answer(w, "Prussia")["stance"] == congress.RECOGNIZES
        assert not coalition.qualifies_for_coalition("Prussia", w)

    def test_with_no_coalition_standing_the_lowered_gate_brews_one(self):
        w = _boot()
        _sit(w)
        _tick(w)
        w.active_coalition = None
        w.coalition_brewing = None
        w.coalition_cooldown = 0
        w.threat_by_target["France"] = 45
        assert congress.coalition_gate(w) == 40
        with contextlib.redirect_stdout(io.StringIO()):
            coalition.process_coalition_turn(w)
        assert w.coalition_brewing or w.active_coalition

    def test_the_stock_gate_does_not_brew_at_45(self):
        w = _boot()
        w.active_coalition = None
        w.coalition_brewing = None
        w.coalition_cooldown = 0
        w.threat_by_target["France"] = 45
        with contextlib.redirect_stdout(io.StringIO()):
            coalition.process_coalition_turn(w)
        assert not w.coalition_brewing and not w.active_coalition

    def test_the_war_of_the_congress_joins_a_standing_coalition(self):
        w = _boot()
        assert w.active_coalition and w.active_coalition["target_nation"] == "France"
        _sit(w)
        before = len(w.event_log)
        with contextlib.redirect_stdout(io.StringIO()):
            _tick(w, congress.WAR_AFTER_REFUSALS + 1)
        assert w.is_at_war("Prussia", "France")
        assert "Prussia" in w.active_coalition["members"]
        phases = [e.get("phase") for e in w.event_log[before:] if e.get("type") == "congress"]
        assert "warning" in phases and "war" in phases

    def test_london_pays_every_other_refuser(self):
        from backend.game_logic import naval
        w = _boot()
        _peace(w, "Britain")
        # Britain boots AT its authored 2,000 paymaster floor (NA-3: the boot
        # turn pays nothing) — review #24's floor binds the Congress purse too.
        w.nation_gold["Britain"] = 5000
        _sit(w)
        assert congress.answer(w, "Britain")["stance"] == congress.REFUSES
        gold = dict(w.nation_gold)
        with contextlib.redirect_stdout(io.StringIO()):
            _tick(w)
        paid = w.congress.get("paid_this_turn") or []
        assert paid
        assert naval.trade_dominance_nation(w) == "Britain"
        # The tick alone moved the purses (no income phase in `_tick`).
        for court in paid:
            assert w.nation_gold[court] == gold[court] + congress.LONDON_SUBSIDY
        assert w.nation_gold["Britain"] == (gold["Britain"]
                                            - congress.LONDON_SUBSIDY * len(paid))

    def test_france_outbids_london_with_a_standing_sponsorship(self, monkeypatch):
        from backend.game_logic import instruments
        w = _boot()
        _peace(w, "Britain")
        _sit(w)
        monkeypatch.setattr(instruments, "standing_sponsorship_amount",
                            lambda world, payer, recipient: 500)
        gold = dict(w.nation_gold)
        with contextlib.redirect_stdout(io.StringIO()):
            _tick(w)
        assert (w.congress.get("paid_this_turn") or []) == []
        assert w.nation_gold["Britain"] == gold["Britain"]

    def test_the_grudge_after_a_dissolution(self):
        w = _boot()
        _sit(w)
        _tick(w, 9)
        rows = congress.grudge_contributions(w, 2)
        assert rows and rows[0]["source"] == "congress_grudge" and rows[0]["amount"] == 2
        assert congress.grudge_contributions(w, 1)[0]["amount"] == 1
        w.current_turn += congress.GRUDGE_TURNS
        assert congress.grudge_contributions(w, 2) == []

    def test_the_bills_multiply_only_while_it_sits(self):
        w = _boot()
        _sit(w)
        assert congress.peace_dividend(w, "France") == 1.5
        assert congress.peace_dividend(w, "Austria") == 1.0
        # The stakes double from the sitting's FIRST DAY, not on the summons
        # turn itself (the driver arms measured the summons' own bills at x2
        # un-titling a fresh satellite before the sitting began).
        assert congress.petition_stakes(w, "France") == 1
        _tick(w)
        assert congress.petition_stakes(w, "France") == 2
        assert congress.petition_stakes(w, "Austria") == 1


# ════════════════════════════════════════════════════════════════════════
# The Premature arm (§2.8): summoned at exactly 50 with refusers and no
# preparation, the Congress is lost — on three seeds.
# ════════════════════════════════════════════════════════════════════════

class TestThePrematureArm:
    @pytest.mark.parametrize("seed", ["historical", "ulm", "austerlitz"])
    def test_a_premature_summons_loses_the_congress(self, seed):
        with contextlib.redirect_stdout(io.StringIO()):
            w = WorldState.from_scenario(SCEN, seed=seed)
        _sit(w)
        random.seed(10_000)
        _tick(w, 9)
        assert w.congress["status"] == congress.DISSOLVED
        assert not game_end.has_ending(w, game_end.CAUSE_IMPERIAL_PEACE)

    def test_the_accept_arm_holds_thirty_five_and_cannot_summon(self):
        w = _boot()
        assert congress.titled(w)["count"] == 35
        assert congress.summon(w)["success"] is False


# ════════════════════════════════════════════════════════════════════════
# The surfaces — ONE payload, ONE line
# ════════════════════════════════════════════════════════════════════════

class TestTheSurfaces:
    def test_the_payload_is_json_and_ints(self):
        w = _boot()
        _sit(w)
        payload = congress.build_congress_payload(w)
        json.dumps(payload)
        assert payload["phase"] == "sitting" and payload["sitting"] is True
        assert len(payload["hold"]) == 7 and len(payload["courts"]) == 4
        for row in payload["courts"]:
            assert row["stance"] in congress.STANCES
            assert isinstance(row["threshold"], int)

    def test_the_strategic_ledger_and_the_dispatch_carry_the_clock(self):
        from backend.game_logic.ledger import build_strategic_ledger
        w = _boot()
        ledger = build_strategic_ledger(w)
        assert ledger["congress_clock"]["line"] == congress.state_line(w)
        assert ledger["congress_clock"]["severity"] == "gate"

    def test_the_end_turn_dispatch_carries_the_clock(self):
        from backend.game_logic.dispatch import build_morning_dispatch
        w = _boot()
        _sit(w)
        _tick(w, 2)
        with contextlib.redirect_stdout(io.StringIO()):
            dispatch = build_morning_dispatch(w)
        clock = dispatch["congress_clock"]
        assert clock["line"] == congress.state_line(w)
        assert clock["phase"] == "sitting" and clock["severity"] in ("warning", "critical")

    def test_the_war_room_prints_the_line_and_the_table(self):
        from backend.game_logic.diplomatic_advisory import _assess_situation
        w = _boot()
        _sit(w)
        _tick(w, 2)
        out = _assess_situation(w)
        text = out.get("text") or out.get("talleyrand_text") or json.dumps(out)
        assert congress.state_line(w) in text
        assert "Prussia: REFUSES" in text

    def test_talleyrand_names_the_biggest_blocker(self):
        w = _boot()
        _sit(w)
        counsel = congress.counsel(w)
        assert counsel["court"] in congress.great_powers(w)
        assert counsel["price"]

    def test_the_moniteur_column_while_it_sits(self):
        """The production column (`gazette._congress_column`), not a copy."""
        from backend.game_logic import gazette
        w = _boot()
        assert gazette._congress_column(w, None) == []
        _sit(w)
        w.current_turn += 1
        assert gazette._congress_column(w, None)[0].startswith("The powers gather")
        w.current_turn += 1
        column = gazette._congress_column(w, None)
        assert column[0] == "The Congress of Paris has sat 1 of its 8 turns."
        assert any("refuses" in line for line in column)


# ════════════════════════════════════════════════════════════════════════
# What the driver arms found (the Pressburg and Premature arms, §2.8)
# ════════════════════════════════════════════════════════════════════════

class TestWhatTheArmsFound:
    def _prussia_at(self, w, score):
        base = congress.recognition_score(w, "Prussia")["score"]
        key = w._make_diplo_key("Prussia", "France")
        w.nation_relations[key] = int(w.nation_relations.get(key, 0)) + (score - base)

    def test_a_signature_at_the_table_holds_through_the_drift(self):
        """Paid at exactly the price (50), Berlin fell to 49 by the advance's
        relation drift and the Congress dissolved "Berlin had not signed"."""
        w = _boot()
        _sit(w)
        self._prussia_at(w, 50)
        assert congress.answer(w, "Prussia")["stance"] == congress.RECOGNIZES
        assert congress.take_the_signatures(w) == ["Prussia"]
        key = w._make_diplo_key("Prussia", "France")
        w.nation_relations[key] = int(w.nation_relations[key]) - 1
        _tick(w)
        row = congress.answer(w, "Prussia")
        assert row["stance"] == congress.RECOGNIZES and row["by"] == "table"
        assert w.congress["answers"]["Prussia"]["stance"] == congress.RECOGNIZES

    def test_a_capture_from_its_bloc_lifts_the_signature(self):
        w = _boot()
        _sit(w)
        self._prussia_at(w, 50)
        congress.take_the_signatures(w)
        w.capture_region("Silesia", "France")
        row = congress.answer(w, "Prussia")
        assert row["stance"] == congress.REFUSES and row["by"] == "withdrawn"
        assert "Prussia" not in (w.congress.get("signed_at_table") or {})

    def test_the_end_turn_signs_before_the_advance(self):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.turn_manager import TurnManager
        w = _boot()
        _sit(w)
        self._prussia_at(w, 50)
        turn = int(w.current_turn)
        random.seed(10_000)
        with contextlib.redirect_stdout(io.StringIO()):
            TurnManager(w, executor=CommandExecutor()).end_turn(
                {"world": w, "executor": CommandExecutor()})
        assert w.congress["signed_at_table"].get("Prussia") == turn

    def test_a_signature_is_never_taken_on_a_read(self):
        w = _boot()
        _sit(w)
        self._prussia_at(w, 50)
        congress.build_congress_payload(w)
        congress.state_line(w)
        assert not w.congress.get("signed_at_table")

    def test_the_continent_is_the_mainland_france_can_march_to(self):
        w = _boot()
        land = congress.mainland(w)
        assert len(land) == 92
        for inside in ("Paris", "Lisbon", "Vienna", "Flanders", "Holstein", "Naples"):
            assert inside in land, inside
        for outside in ("London", "Copenhagen", "Stockholm", "Corsica", "Cagliari"):
            assert outside not in land, outside
        moore = w.marshals["Moore"]
        moore.location = "Copenhagen"
        assert congress.corps_on_the_continent(w, "Britain") == []
        moore.location = "Flanders"
        assert congress.corps_on_the_continent(w, "Britain") == ["Moore"]

    def _close(self, w):
        for nation in ("Portugal", "Denmark", "Sweden", "Ottoman", "Naples",
                       "Prussia", "Russia", "Austria", "Sardinia"):
            w.diplomatic_states[w._make_diplo_key(nation, "Britain")] = "WAR"
        w.invalidate_active_nations_cache()

    def test_a_landing_driven_off_restores_the_shut_out(self):
        """The corps half is LIVE: only the ports latch."""
        w = _boot()
        self._close(w)
        _sit(w)
        assert congress.answer(w, "Britain")["stance"] == congress.SHUT_OUT
        moore = w.marshals["Moore"]
        moore.location = "Flanders"
        _tick(w)
        assert congress.answer(w, "Britain")["stance"] == congress.REFUSES
        assert not w.congress.get("shut_out_broken")
        moore.location = "London"
        _tick(w)
        assert congress.answer(w, "Britain")["stance"] == congress.SHUT_OUT

    def test_a_shut_out_lapse_is_not_a_withdrawn_signature(self):
        from backend.campaign_log import format_event_oneliner
        w = _boot()
        self._close(w)
        _sit(w)
        _tick(w)
        w.marshals["Moore"].location = "Flanders"
        before = len(w.event_log)
        _tick(w)
        rows = [e for e in w.event_log[before:]
                if e.get("type") == "congress" and e.get("phase") == "withdrew"]
        assert rows and rows[0]["was"] == congress.SHUT_OUT
        assert "Moore" in rows[0]["reason"] and "Flanders" in rows[0]["reason"]
        line = format_event_oneliner(rows[0])
        assert "no longer shut out" in line and "withdraws its signature" not in line

    def test_a_defection_breaks_the_hold(self):
        w = _boot()
        _sit(w)
        congress.note_rebellion(w, "Holland", "France", defected_to="Britain")
        hold = {h["key"]: h for h in congress.hold_conditions(w)}
        assert hold["satellites"]["met"] is False
        assert "Holland defected to Britain" in hold["satellites"]["text"]
        _tick(w)
        assert w.congress["dissolve_key"] == "satellites"

    def test_the_defection_seam_reports_to_the_congress(self):
        import inspect
        from backend.game_logic import vassal
        src = inspect.getsource(vassal)
        start = src.index('"type": "vassal_defected",')
        assert "defected_to=nation" in src[start:start + 800]

    def test_the_gate_refuses_a_summons_the_alarm_would_break(self):
        w = _boot()
        _stage_titles(w)
        w.diplomatic_points = 6
        w.threat_by_target["France"] = 85
        terms = {t["key"]: t for t in congress.gate_terms(w)}
        assert terms["alarm"]["met"] is False
        refusal = congress.summon_refusal(w)
        assert refusal == terms["alarm"]["refusal"]
        assert "would dissolve at its first end turn" in refusal
        assert congress.summon(w)["success"] is False

    def test_the_summons_turn_bills_carry_ordinary_stakes(self):
        from backend.game_logic import vassal
        w = _boot()
        _sit(w)
        assert congress.day_of_sitting(w) == 0
        assert vassal._petition_stakes(w, "France") == 1
        _tick(w)
        assert vassal._petition_stakes(w, "France") == 2
