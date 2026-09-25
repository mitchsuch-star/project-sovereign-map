"""GE-3 "The Congress of Paris" — the review round (September 25, 2026).

A four-lens review of the Congress (the table, the sitting, dormancy, the
verbs, the bills, the narration, the client, the tests) filed 69 findings.
Each surviving finding is pinned here on the REAL seams — `congress.*`, the
`/command` road, `game_end.process_end_of_turn`, `_ratify_treaty`,
`capture_region`, `declare_war`, `coalition.qualifies_for_coalition`,
`advance_turn` — and numbered by the review's own finding (`#n`). The
landing record is `ENDGAME_PLAN.md` §6 GE-3 (review round); the rules are
`SYSTEMS_REFERENCE.md` §66.
"""

import contextlib
import io
import json
import math

import pytest

from backend.game_logic import coalition, congress, dotation, game_end
from tests.test_congress_of_paris import (
    _boot, _latch, _peace, _sit, _stage_titles, _tick,
)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _set_score(w, court, score):
    """Move `court`'s formula score to exactly `score` by relation."""
    base = congress.recognition_score(w, court)["score"]
    key = w._make_diplo_key(court, "France")
    w.nation_relations[key] = int(w.nation_relations.get(key, 0)) + (score - base)
    assert congress.recognition_score(w, court)["score"] == score


def _set_relation(w, court, value):
    w.nation_relations[w._make_diplo_key(court, "France")] = int(value)


def _events(w, phase, court=None):
    return [e for e in w.event_log if e.get("type") == "congress"
            and e.get("phase") == phase and (court is None or e.get("court") == court)]


def _close_the_ports(w):
    for nation in ("Portugal", "Denmark", "Sweden", "Ottoman", "Naples",
                   "Prussia", "Russia", "Austria", "Sardinia"):
        w.diplomatic_states[w._make_diplo_key(nation, "Britain")] = "WAR"
    w.invalidate_active_nations_cache()


@pytest.fixture
def client(monkeypatch):
    from fastapi.testclient import TestClient
    import backend.main as M
    from tests._chip_census import board_env
    prior = (M.world, M.game_state.get("world"), M.parser)
    board_env(monkeypatch)
    yield TestClient(M.app), M
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


def _post(tc, text):
    with _quiet():
        return tc.post("/command", json={"command": text}).json()


# ════════════════════════════════════════════════════════════════════════
# The table
# ════════════════════════════════════════════════════════════════════════

class TestTheTableTellsTheTruth:
    def test_1_the_treaty_lever_is_one_the_court_can_ratify(self):
        from backend.game_logic.diplomacy import check_relation_requirement
        w = _boot()
        _peace(w, "Russia")
        _set_relation(w, "Russia", 30)
        _sit(w)
        pr = congress.price(w, "Russia")
        treaty = next(lv for lv in pr["levers"] if lv["key"] == "treaty")
        state = w.get_diplomatic_state("Russia", "France")
        if treaty.get("relation"):
            # the courtship the alliance needs is FOLDED into the lever
            assert treaty["state"] == "ALLIANCE"
            assert 30 + treaty["relation"] >= 40
        else:
            assert check_relation_requirement(state, treaty["state"], 30)
            assert treaty["state"] != "ALLIANCE"

    def test_2_a_truce_leads_with_the_signed_peace(self):
        w = _boot()
        _sit(w)
        w.diplomatic_states[w._make_diplo_key("Austria", "France")] = "ARMISTICE"
        w.invalidate_active_nations_cache()
        pr = congress.price(w, "Austria")
        assert pr["levers"][0]["key"] == "peace"
        assert pr["text"].startswith("sign a peace with Austria")
        with _quiet():
            w._ratify_treaty({"proposer_nation": "Austria", "target_nation": "France",
                              "type": "peace", "demands": [], "sweeteners": []})
        row = congress.answer(w, "Austria")
        assert row["stance"] == congress.RECOGNIZES and row["by"] == "treaty"

    def test_2_a_truce_that_runs_out_does_not_sign(self):
        w = _boot()
        _sit(w)
        congress.note_ratification(w, ["Austria"], False)
        assert not (w.congress.get("signed") or {}).get("Austria")

    def test_5_the_projection_reads_the_congress_that_will_sit(self):
        w = _boot()
        w.campaign_seed = "austerlitz"
        w.current_turn = 30
        _stage_titles(w)
        w.diplomatic_points = 6
        before = {c: next(x["value"] for x in congress.recognition_score(w, c)["components"]
                          if x["key"] == "jitter") for c in congress.great_powers(w)}
        assert congress.summon(w)["success"]
        after = {c: next(x["value"] for x in congress.recognition_score(w, c)["components"]
                         if x["key"] == "jitter") for c in congress.great_powers(w)}
        assert before == after

    def test_6_the_arbiter_can_be_bought(self):
        w = _boot()
        _peace(w, "Russia")
        _set_relation(w, "Russia", 30)
        _sit(w)
        pr = congress.price(w, "Russia")
        design = next((lv for lv in pr["levers"] if lv["key"] == "design"), None)
        assert design is not None and design["value"] > 0
        assert "arbiter_of_europe" in design["chain"]

    def test_6_the_ports_are_a_lever_at_peace(self):
        w = _boot()
        _peace(w, "Britain")
        _sit(w)
        row = congress.answer(w, "Britain")
        assert row["stance"] == congress.REFUSES
        pr = congress.price(w, "Britain", row)
        assert any(lv["key"] == "ports" for lv in pr["levers"])
        assert "ports" in pr["text"]

    def test_7_quote_charge_receipt_and_score_agree_on_a_part_paid_court(self):
        w = _boot()
        w.nation_gold["France"] = 20000
        _sit(w)
        _set_score(w, "Prussia", 20)
        assert congress.pay_sweetener(w, "Prussia", 550)["points"] == 5
        lever = next(lv for lv in congress.price(w, "Prussia")["levers"]
                     if lv["key"] == "sweetener")
        before = congress.recognition_score(w, "Prussia")["score"]
        paid = congress.pay_sweetener(w, "Prussia", lever["gold"])
        assert paid["success"] and paid["charge"] == lever["gold"]
        assert paid["points"] == lever["value"]
        assert f"(+{lever['value']})" in paid["message"]
        assert congress.recognition_score(w, "Prussia")["score"] - before == lever["value"]

    def test_8_the_war_score_reads_from_the_emperors_side(self):
        w = _boot()
        _sit(w)
        key = w._make_diplo_key("Austria", "France")
        w.war_scores[key] = -30 if key.startswith("Austria") else 30
        row = congress.answer(w, "Austria")
        assert row["stance"] == congress.REFUSES
        assert "our war score +30" in row["reason"]
        lever = next(lv for lv in congress.price(w, "Austria", row)["levers"]
                     if lv["key"] == "war")
        assert lever["text"].startswith("win the war to +40 (now +30)")

    def test_9_before_a_summons_a_beaten_court_would_sue(self):
        w = _boot()
        key = w._make_diplo_key("Austria", "France")
        w.war_scores[key] = -45 if key.startswith("Austria") else 45
        row = congress.answer(w, "Austria")
        assert row["stance"] == congress.SUES and row.get("projected")
        assert "would sue once the Congress sits" in row["reason"]
        pr = congress.price(w, "Austria", row)
        assert "its envoy brings the terms" not in pr["text"]
        assert pr["text"].startswith("summon the Congress")

    def test_9_a_suing_court_at_the_end_is_named_apart_and_bears_no_grudge(self):
        w = _boot()
        _sit(w)
        for court in ("Britain", "Russia", "Prussia"):
            _latch(w, court)
        key = w._make_diplo_key("Austria", "France")
        with _quiet():
            for _ in range(congress.congress_turns(w) + 1):
                w.war_scores[key] = -45 if key.startswith("Austria") else 45
                _tick(w)
        c = w.congress
        assert c["status"] == congress.DISSOLVED
        assert "Austria" not in c["refusers"]
        assert c["sued_at_the_end"] == ["Austria"]
        assert "sued, and the Emperor did not sign its peace" in c["dissolve_reason"]

    def test_47_a_withdrawn_court_names_its_withdrawal_on_the_clock(self):
        w = _boot()
        _sit(w)
        _set_score(w, "Prussia", 60)
        congress.take_the_signatures(w)
        w.capture_region("Hanover", "France")
        line = congress.state_line(w)
        assert "Prussia REFUSES (withdrew: Hanover)" in line

    def test_57_a_chained_buy_off_says_it_takes_one_order_each(self):
        w = _boot()
        _peace(w, "Austria")
        _sit(w)
        pr = congress.price(w, "Austria")
        design = next((lv for lv in pr["levers"] if lv["key"] == "design"), None)
        if design is not None and design.get("orders", 1) > 1:
            assert "one order each" in design["text"]


# ════════════════════════════════════════════════════════════════════════
# The sitting
# ════════════════════════════════════════════════════════════════════════

class TestTheSitting:
    def test_10_a_signed_court_is_never_marched_by_the_lowered_gate(self):
        w = _boot()
        _peace(w, "Austria")
        _set_relation(w, "Austria", -40)
        _sit(w)
        congress.note_ratification(w, ["Austria"], True)   # signed at the table
        assert congress.answer(w, "Austria")["stance"] == congress.RECOGNIZES
        assert congress.coalition_gate(w) == congress.CONGRESS_ALARM_GATE
        assert congress.spared_from_coalition(w, "Austria", "France")
        assert coalition.qualifies_for_coalition("Austria", w) is False

    def test_19_a_court_in_a_truce_is_never_marched_while_it_sits(self):
        w = _boot()
        _sit(w)
        w.diplomatic_states[w._make_diplo_key("Austria", "France")] = "ARMISTICE"
        w.invalidate_active_nations_cache()
        _set_relation(w, "Austria", -60)
        assert congress.spared_from_coalition(w, "Austria", "France") == "in a truce with us"
        assert coalition.qualifies_for_coalition("Austria", w) is False

    def test_18_a_court_turned_mid_turn_is_not_marched(self):
        w = _boot()
        w.nation_gold["France"] = 20000
        _sit(w)
        with _quiet():
            _tick(w)
        assert (w.congress["answers"]["Prussia"]["stance"]) == congress.REFUSES
        _set_score(w, "Prussia", 45)
        assert congress.pay_sweetener(w, "Prussia", 1000)["stance"] == congress.RECOGNIZES
        assert "Prussia" not in congress.live_refusers(w)
        assert congress.refuser_qualifies(w, "Prussia", "France") is False
        assert coalition.qualifies_for_coalition("Prussia", w) is False

    def test_11_a_siege_is_lifted_by_the_peace(self):
        w = _boot()
        mack = w.marshals["Mack"]
        mack.location = "Rhineland"
        mack.occupation_region = "Rhineland"
        mack.occupation_turns_held = 0
        mack.occupation_turns_required = 1
        _peace(w, "Austria")
        with _quiet():
            w.advance_turn()
        assert w.regions["Rhineland"].controller == "France"
        assert not getattr(mack, "occupation_region", None)

    def test_12_a_ceders_war_names_what_it_reopened(self):
        from backend.game_logic.diplomacy import declare_war
        w = _boot()
        _sit(w)
        with _quiet():
            _tick(w)
            declare_war(w, "Hanover", "France")
        titled = next(h for h in congress.hold_conditions(w) if h["key"] == "titled")
        assert titled["met"] is False
        assert "Hanover's war reopened what it ceded" in titled["text"]
        with _quiet():
            _tick(w)
        from backend.campaign_log import congress_dissolve_reason
        said = congress_dissolve_reason(w.congress["dissolve_key"],
                                        w.congress["dissolve_reason"])
        assert "Hanover's war reopened what it ceded" in said

    def test_13_a_satellites_own_capture_never_unsigns_a_great_power(self):
        w = _boot()
        _latch(w, "Austria")
        w.capture_region("Carniola", "KingdomOfItaly")
        assert congress.answer(w, "Austria")["by"] == "treaty"
        assert not w.congress["signed"]["Austria"]["broken"]

    def test_14_a_capture_in_a_war_never_withdraws_the_court(self):
        w = _boot()
        _sit(w)
        w.capture_region("Estonia", "France")
        assert "Russia" not in (w.congress.get("withdrawn") or {})
        assert "Britain" not in (w.congress.get("withdrawn") or {})

    def test_15_joining_an_allys_offensive_draws_the_sword(self):
        from backend.game_logic.diplomacy import declare_war
        w = _boot()
        _sit(w)
        with _quiet():
            _tick(w)
            declare_war(w, "Spain", "Prussia")
        if w.get_diplomatic_state("France", "Prussia") != "WAR":
            pytest.skip("France is not drawn into Spain's war on this board")
        held = {h["key"]: h for h in congress.hold_conditions(w)}
        assert held["declared"]["met"] is False
        assert "we joined Spain's war on Prussia" in held["declared"]["text"]
        with _quiet():
            _tick(w)
        assert not _events(w, "war", "Prussia")

    def test_17_e1_waits_for_paris_and_the_emperor(self):
        from backend.game_logic import fall
        w = _boot()
        for court in congress.great_powers(w):
            for region in list(w.get_nation_regions(court)):
                w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        sov = fall.sovereign_of(w, "France")
        with _quiet():
            w.capture_marshal(sov, "Sweden")
        assert _tick(w) == []
        assert not congress.imperial_peace_signed(w)

    def test_17_the_floor_never_lifts_a_captive_reign(self):
        w = _boot()
        inputs = game_end.verdict_inputs(w)
        inputs = dict(inputs, imperial_peace=True, emperor="captive",
                      provinces_held=1, capital_held=True)
        assert game_end.verdict_tier(w, inputs)["tier"] == "eclipse"
        inputs = dict(inputs, emperor="free", capital_held=False)
        assert game_end.verdict_tier(w, inputs)["tier"] == "eclipse"
        inputs = dict(inputs, emperor="free", capital_held=True)
        assert game_end.verdict_tier(w, inputs)["tier"] == "ascendant"

    def test_63_a_recogniser_that_takes_a_titled_province_withdraws(self):
        w = _boot()
        _sit(w)
        _latch(w, "Austria")
        region = next(r for r in congress.titled(w)["titled"]
                      if game_end.province_title_kind(w, r, "France") == "treaty")
        was = congress.was_titled(w, region)
        assert was
        w.capture_region(region, "Austria")
        assert congress.answer(w, "Austria")["stance"] == congress.REFUSES
        assert congress.answer(w, "Austria")["by"] == "withdrawn"
        with _quiet():
            _tick(w)
        assert "Austria" in w.congress["refusers"]


# ════════════════════════════════════════════════════════════════════════
# The War of the Congress (#4 #23 #43 #54 #66)
# ════════════════════════════════════════════════════════════════════════

class TestTheWarOfTheCongress:
    def test_the_warning_comes_one_turn_before_the_war_and_never_with_it(self):
        w = _boot()
        _sit(w)
        assert congress.march_blocker(w, "Prussia") == ""
        ticks = {}
        with _quiet():
            for n in range(1, 5):
                _tick(w)
                ticks[n] = ([e["phase"] for e in _events(w, "warning", "Prussia")],
                            [e["phase"] for e in _events(w, "war", "Prussia")])
        assert ticks[1] == ([], [])
        assert ticks[2] == (["warning"], [])
        assert ticks[3] == (["warning"], ["war"])

    def test_no_coalition_no_countdown_and_no_warning(self):
        w = _boot()
        _sit(w)
        w.active_coalition = None
        blocker = congress.march_blocker(w, "Prussia")
        assert blocker.startswith("no coalition stands against us")
        row = next(c for c in congress.build_congress_payload(w)["courts"]
                   if c["nation"] == "Prussia")
        assert "war_in" not in row and row["march_blocker"] == blocker
        with _quiet():
            _tick(w, 4)
        assert not _events(w, "warning", "Prussia")

    @pytest.mark.parametrize("state, said", [
        ("ARMISTICE", "a truce holds it"),
        ("ALLIANCE", "our alliance holds it"),
        ("DEFENSIVE_ALLIANCE", "our alliance holds it"),
    ])
    def test_a_court_that_cannot_march_is_never_promised_a_war(self, state, said):
        w = _boot()
        _sit(w)
        w.diplomatic_states[w._make_diplo_key("Prussia", "France")] = state
        w.invalidate_active_nations_cache()
        assert congress.march_blocker(w, "Prussia") == said
        with _quiet():
            _tick(w, 4)
        assert not _events(w, "warning", "Prussia")
        assert not _events(w, "war", "Prussia")

    def test_war_in_counts_to_the_real_war(self):
        w = _boot()
        _sit(w)
        with _quiet():
            _tick(w)
        row = next(c for c in congress.build_congress_payload(w)["courts"]
                   if c["nation"] == "Prussia")
        assert row["war_in"] == 2
        with _quiet():
            _tick(w)
        row = next(c for c in congress.build_congress_payload(w)["courts"]
                   if c["nation"] == "Prussia")
        assert row["war_in"] == 1

    def test_the_join_clears_the_joiners_letters(self):
        w = _boot()
        _sit(w)
        w.dialogue_manager.push({"type": "incoming_proposal",
                                 "target_nation": "Prussia",
                                 "context": {"proposal_type": "non_aggression"}})
        w.proposal_in_transit = {"target": "Prussia", "dp_cost": 2}
        dp = int(w.diplomatic_points)
        result = coalition.join_coalition(w, "Prussia")
        assert result["success"]
        assert result.get("voided_proposal") == "Prussia"
        assert w.proposal_in_transit is None
        assert int(w.diplomatic_points) == dp + 2
        remaining = [w.dialogue_manager.peek()] + list(w.dialogue_manager.iter_queue())
        assert not any(isinstance(d, dict) and d.get("target_nation") == "Prussia"
                       for d in remaining)


# ════════════════════════════════════════════════════════════════════════
# The pressure readers and London's purse (#21 #22 #24)
# ════════════════════════════════════════════════════════════════════════

class TestThePurseAndTheEnvoys:
    def _london(self, w):
        _peace(w, "Britain")
        w.nation_gold["Britain"] = 5000
        _sit(w)

    def test_24_london_never_funds_a_court_it_is_at_war_with(self):
        w = _boot()
        self._london(w)
        w.diplomatic_states[w._make_diplo_key("Britain", "Prussia")] = "WAR"
        w.invalidate_active_nations_cache()
        with _quiet():
            _tick(w)
        assert "Prussia" not in (w.congress.get("paid_this_turn") or [])

    def test_24_london_keeps_her_floor(self):
        w = _boot()
        self._london(w)
        w.nation_gold["Britain"] = 2100
        with _quiet():
            _tick(w)
        assert not w.congress.get("paid_this_turn")
        assert w.nation_gold["Britain"] >= 2000

    def test_24_london_never_funds_a_court_the_emperor_bought(self):
        from backend.game_logic.instruments import create_compensation_bargain
        w = _boot()
        self._london(w)
        create_compensation_bargain(w, payer="France", recipient="Prussia",
                                    design_id="hanoverian_prize", granted={"gold": 1})
        with _quiet():
            _tick(w)
        assert "Prussia" not in (w.congress.get("paid_this_turn") or [])

    def test_21_the_sue_rung_leaves_a_pending_settlement_to_carry_the_peace(self):
        from backend.game_logic import ai_diplomacy
        w = _boot()
        _sit(w)
        key = w._make_diplo_key("Austria", "France")
        w.war_scores[key] = -75 if key.startswith("Austria") else 75
        war = ai_diplomacy._find_war_instance_for_pair(w, "Austria", "France")
        w.pending_settlement_dialogues = [{"type": "incoming_settlement_offer",
                                           "war_id": war.get("war_id")}]
        with _quiet():
            proposal = ai_diplomacy.process_diplomatic_phase("Austria", w)
        assert not (proposal or {}).get("congress_recognition")

    def test_22_the_war_room_names_the_gate_the_mechanic_reads(self):
        from backend.game_logic.diplomatic_advisory import _assess_situation
        w = _boot()
        _sit(w)
        w.active_coalition = None
        w.coalition_brewing = None
        w.threat_by_target["France"] = 30
        with _quiet():
            text = json.dumps(_assess_situation(w), default=str)
        assert "below 60" not in text


# ════════════════════════════════════════════════════════════════════════
# The verbs (#27 #28 #29 #31 #32 #33)
# ════════════════════════════════════════════════════════════════════════

class TestTheVerbs:
    @pytest.mark.parametrize("line", [
        "Ney, attack Mack so we can summon the congress",
        "Davout, fortify Paris so that I can summon the congress",
        "Lannes, attack Mack, we need the win to summon the congress",
        "Murat, scout Swabia so I know whether to summon the congress",
        "Ney attack Mack so we can summon the congress",
    ])
    def test_27_a_marshals_order_that_mentions_the_summons_never_summons(self, client, line):
        tc, M = client
        w = M.world
        _stage_titles(w)
        w.diplomatic_points = 5
        dp, admin = w.diplomatic_points, w.admin_actions_remaining
        r = _post(tc, line)
        assert not congress.sitting(w), r.get("message")
        assert w.diplomatic_points == dp and w.admin_actions_remaining == admin
        said = str(r.get("message") or "")
        assert "summons the powers" not in said
        # the marshal's order is his — never turned into a Congress question
        assert "The Congress of Paris" not in said, said

    @pytest.mark.parametrize("line", [
        "Talleyrand, summon the congress?",
        "Talleyrand summon the congress?",
        "perhaps we summon the congress",
        "maybe summon the congress",
        "it might be time to summon the congress",
        "we could summon the congress",
        "I wonder whether to summon the congress",
        "not sure whether to summon the congress",
        "explain how to summon the congress",
        "remind me how to summon the congress",
        "Talleyrand, advise me on whether to summon the congress",
        "summon the congress in two turns",
        "Prussia says we cannot summon the congress",
        "Prussia has asked us to summon the congress",
        "the courts expect us to summon the congress",
    ])
    def test_28_32_a_question_or_a_hedge_never_summons(self, client, line):
        tc, M = client
        w = M.world
        _stage_titles(w)
        w.diplomatic_points = 5
        r = _post(tc, line)
        assert not congress.sitting(w), (line, r.get("message"))
        assert w.diplomatic_points == 5

    @pytest.mark.parametrize("line", [
        "summon the congress",
        "Talleyrand, summon the congress",
        "summon the great powers to Paris",
        "I summon the congress",
    ])
    def test_33_the_summons_reads_the_forms_the_game_prints(self, client, line):
        tc, M = client
        w = M.world
        _stage_titles(w)
        w.diplomatic_points = 5
        r = _post(tc, line)
        assert congress.sitting(w), (line, r.get("message"))

    def test_28_a_question_to_the_minister_never_pays(self, client):
        tc, M = client
        w = M.world
        w.nation_gold["France"] = 20000
        _sit(w)
        _post(tc, "Talleyrand, offer Prussia 1000 gold for recognition?")
        assert not (w.congress.get("sweeteners") or {}).get("Prussia")

    @pytest.mark.parametrize("line, paid", [
        ("offer Prussia not 500 but 1500 gold for recognition", 1500),
        ("to recognize our 1805 borders, offer Prussia 1500 gold", 1500),
        ("offer Prussia 1 000 gold for recognition", 1000),
        ("offer Prussia 800g for recognition", 800),
        ("offer Prussia an 800g sweetener", 800),
        ("offer Prussia a sweetener of 800 gold", 800),
        ("offer Berlin 1000 gold for recognition", 1000),
    ])
    def test_29_33_the_gold_is_the_gold_the_line_names(self, client, line, paid):
        tc, M = client
        w = M.world
        w.nation_gold["France"] = 20000
        _sit(w)
        _set_score(w, "Prussia", 0)
        r = _post(tc, line)
        assert r.get("success") is True, (line, r.get("message"))
        assert (w.congress.get("sweeteners") or {}).get("Prussia") == paid

    @pytest.mark.parametrize("line", [
        "offer Prussia peace in recognition of the treaty of 1805",
        "on turn 3 offer Prussia 1000 gold for recognition and 500 gold more",
    ])
    def test_29_no_figure_or_two_figures_pay_nothing(self, client, line):
        tc, M = client
        w = M.world
        w.nation_gold["France"] = 20000
        _sit(w)
        gold, dp = w.nation_gold["France"], w.diplomatic_points
        _post(tc, line)
        assert not (w.congress.get("sweeteners") or {}).get("Prussia")
        assert w.nation_gold["France"] == gold and w.diplomatic_points == dp

    @pytest.mark.parametrize("text, amount, refused", [
        ("offer Prussia 1000 gold for recognition", 1000, False),
        ("offer Prussia not 500 but 1500 gold for recognition", 1500, False),
        ("in 2 turns offer Prussia 1000 gold for recognition", 1000, False),
        ("offer Prussia 1000 gold and 500 gold for recognition", None, True),
        ("offer Prussia 1000 for recognition", 1000, False),
        ("offer Prussia in recognition of the treaty of 1805", None, False),
        ("don't offer Prussia 500 gold; offer Prussia 1500 gold for recognition", 1500, False),
        ("offer Prussia a sweetener for our 1805 borders", None, False),
    ])
    def test_29_the_amount_reader(self, text, amount, refused):
        got, refusal = congress.sweetener_amount(text)
        assert got == amount
        assert bool(refusal) is refused

    @pytest.mark.parametrize("line", [
        "Talleyrand, offer Prussia an alliance in recognition of the Treaty of 1805",
        "Talleyrand, offer Prussia an alliance and 1000 gold for recognition",
    ])
    def test_31_an_alliance_in_recognition_stays_the_cabinets(self, client, line):
        tc, M = client
        w = M.world
        w.nation_gold["France"] = 20000
        _sit(w)
        gold = w.nation_gold["France"]
        _post(tc, line)
        assert not (w.congress.get("sweeteners") or {}).get("Prussia")
        assert w.nation_gold["France"] == gold

    def test_33_the_emperors_own_court_is_refused_in_its_own_words(self, client):
        tc, M = client
        w = M.world
        w.nation_gold["France"] = 20000
        _sit(w)
        r = _post(tc, "offer France 1000 gold for recognition")
        assert r.get("success") is False
        assert "Name the court" not in r.get("message", "")


# ════════════════════════════════════════════════════════════════════════
# The sweetener's refusals (#3 #30)
# ════════════════════════════════════════════════════════════════════════

class TestTheSweetenerRefuses:
    def _world(self):
        w = _boot()
        w.nation_gold["France"] = 20000
        _sit(w)
        return w

    def _refused_free(self, w, court, amount, said):
        gold, dp = w.nation_gold["France"], w.diplomatic_points
        refusal = congress.sweetener_refusal(w, court, amount)
        assert refusal and said in refusal, refusal
        assert congress.pay_sweetener(w, court, amount)["success"] is False
        assert w.nation_gold["France"] == gold and w.diplomatic_points == dp

    def test_a_withdrawn_court(self):
        w = self._world()
        _set_score(w, "Prussia", 60)
        congress.take_the_signatures(w)
        w.capture_region("Hanover", "France")
        self._refused_free(w, "Prussia", 2000, "withdrew")

    def test_a_signed_court(self):
        w = self._world()
        _latch(w, "Austria")
        self._refused_free(w, "Austria", 1000, "has signed")

    def test_a_shut_out_court(self):
        w = _boot()
        w.nation_gold["France"] = 20000
        _peace(w, "Britain")
        _close_the_ports(w)
        _sit(w)
        assert congress.answer(w, "Britain")["stance"] == congress.SHUT_OUT
        self._refused_free(w, "Britain", 1000, "shut out")

    def test_a_court_that_already_recognizes(self):
        w = self._world()
        _set_score(w, "Prussia", 55)
        self._refused_free(w, "Prussia", 1000, "already recognizes")

    def test_gold_that_buys_nothing(self):
        w = self._world()
        _set_score(w, "Prussia", 0)
        self._refused_free(w, "Prussia", 50, "buys nothing")


# ════════════════════════════════════════════════════════════════════════
# The bills (#20 #34 #35 #36 #37 #38 #39 #40 #62 #65)
# ════════════════════════════════════════════════════════════════════════

class TestTheBills:
    def _unpaid_ney(self, w):
        ney = w.marshals["Ney"]
        ney.expectation_steps = 3
        assert dotation.get_shortfall(ney, w) > 0
        return ney

    def test_38_the_summons_prices_the_rentes(self):
        w = _boot()
        ney = w.marshals["Ney"]
        ney.pension = 200
        _stage_titles(w)
        text = congress.summons_cost_text(w)
        extra = (math.ceil(dotation.RENTE_PREMIUM * 1.5 * 200)
                 - math.ceil(dotation.RENTE_PREMIUM * 200))
        assert f"(+{extra:,}g a turn)" in text

    def test_40_the_income_phase_charges_the_dividend_while_it_sits(self):
        w = _boot()
        ney = w.marshals["Ney"]
        ney.pension = 200
        plain = dotation.get_nation_rente_bill(w, "France")
        _sit(w)
        assert dotation.get_nation_rente_bill(w, "France") == \
            plain - math.ceil(dotation.RENTE_PREMIUM * 200) + \
            math.ceil(dotation.RENTE_PREMIUM * 1.5 * 200)
        w.threat_by_target["France"] = 95
        with _quiet():
            _tick(w)
        assert w.congress["status"] == congress.DISSOLVED
        assert dotation.get_nation_rente_bill(w, "France") == plain

    def test_34_the_collective_petition_is_priced_at_delivery(self):
        from backend.game_logic import jealousy
        w = _boot()
        ney = self._unpaid_ney(w)
        petition = {"kind": "fontainebleau",
                    "context": {"marshals": ["Ney"]},
                    "options": [{"id": "concede", "detail": "stale"}]}
        plain = jealousy.refresh_petition_affordability(petition, w)["options"][0]["detail"]
        assert "×1.5" not in plain
        _sit(w)
        sitting = jealousy.refresh_petition_affordability(petition, w)["options"][0]["detail"]
        assert "×1.5" in sitting
        assert sitting == jealousy.fontainebleau_concede_detail(w, [ney])
        assert petition["options"][0]["detail"] == "stale"   # pure

    def test_34_the_redemption_settle_arm_is_priced_at_the_read(self):
        from backend.commands import disobedience
        w = _boot()
        ney = self._unpaid_ney(w)
        ney.redemption_pending = True
        option = disobedience.settle_account_option(ney, w)
        assert option is not None
        w.pending_redemption = {"marshal": "Ney", "options": [dict(option)]}
        _sit(w)
        live = disobedience.standing_redemption(w)
        settle = next(o for o in live["options"] if o["id"] == "settle_account")
        assert "×1.5" in settle["description"]

    def test_20_62_the_rail_is_restated_when_the_congress_ends(self):
        w = _boot()
        ney = self._unpaid_ney(w)
        ney.expectation_grace_turn = int(w.current_turn)   # a standing row
        exp = dotation.get_expectation(ney)
        sat = dotation.get_satisfaction(ney, w) if hasattr(dotation, "get_satisfaction") else 0
        dotation.post_expectation_notice(w, ney, exp, sat,
                                         dotation.get_shortfall(ney, w), 2)
        _sit(w)
        sitting_rows = [n for n in w.notifications.get_pending()
                        if (n.get("details") or {}).get("marshal") == "Ney"
                        and (n.get("details") or {}).get("action_label")]
        assert sitting_rows[0]["details"]["action_label"] == \
            dotation.rente_action_keys(ney, w)["action_label"]   # re-quoted x1.5
        w.threat_by_target["France"] = 95
        with _quiet():
            _tick(w)
        assert w.congress["status"] == congress.DISSOLVED
        rows = [n for n in w.notifications.get_pending()
                if (n.get("details") or {}).get("marshal") == "Ney"
                and (n.get("details") or {}).get("action_label")]
        assert rows, "no reward row for Ney"
        live = dotation.rente_action_keys(ney, w)
        assert rows[0]["details"]["action_label"] == live.get("action_label")
        assert "×1.5" not in rows[0].get("message", "")

    def test_36_the_owed_bill_never_arrives_on_the_tick_that_ends_it(self, monkeypatch):
        from backend.game_logic import jealousy
        calls = []
        monkeypatch.setattr(jealousy, "queue_fontainebleau_petition",
                            lambda *a, **k: calls.append(k) or jealousy.PETITION_QUEUED)
        w = _boot()
        self._unpaid_ney(w)
        _sit(w)
        calls.clear()
        w.congress["petition_owed"] = True
        w.threat_by_target["France"] = 95
        with _quiet():
            _tick(w)
        assert w.congress["status"] == congress.DISSOLVED
        assert calls == [] and w.congress["petition_owed"] is False

    def test_65_the_dissolution_raises_each_eligible_marshal_one_rung(self):
        w = _boot()
        w.current_turn = 12          # past F4's floor (no rise before turn 6)
        _sit(w)
        before = {m.name: int(getattr(m, "expectation_steps", 0) or 0)
                  for m in w.marshals.values() if m.nation == "France"}
        w.threat_by_target["France"] = 95
        with _quiet():
            _tick(w)
        raised = set(w.congress["expectation_raised"])
        assert raised
        for m in w.marshals.values():
            if m.nation != "France":
                continue
            if m.name in raised:
                assert int(m.expectation_steps) == before[m.name] + 1
            if getattr(m, "is_sovereign", False):
                assert m.name not in raised

    def test_39_a_blocked_retry_logs_no_arrival(self):
        from backend.game_logic import jealousy
        w = _boot()
        ney = self._unpaid_ney(w)
        w.pending_marshal_petition = {"kind": "confrontation", "options": []}
        before = len([e for e in w.event_log if e.get("type") == "fontainebleau_petition"])
        status = jealousy.queue_fontainebleau_petition(w, [ney], reason="congress")
        after = len([e for e in w.event_log if e.get("type") == "fontainebleau_petition"])
        if status != jealousy.PETITION_QUEUED:
            assert after == before

    def test_37_the_petition_row_states_the_stakes(self):
        from backend.game_logic import vassal
        title, body = vassal.client_petition_notice(
            "Holland", {"dp_cost": 1, "refusal_loyalty": 20,
                        "relation_refusal_step": 20, "loyalty_stakes": 2,
                        "lapse_counts_as_refusal": True})
        assert title == "Petition from Holland"
        assert "−20 loyalty (×2 while the Congress of Paris sits), −20 bond" in body


# ════════════════════════════════════════════════════════════════════════
# The narration (#16 #42 #44 #46 #49 #50 #52 #53 #55 #56 #60)
# ════════════════════════════════════════════════════════════════════════

class TestTheNarration:
    def test_44_the_emperors_declaration_is_never_the_courts_cannon(self):
        from backend.game_logic.diplomacy import declare_war
        w = _boot()
        _sit(w)
        with _quiet():
            _tick(w)
            declare_war(w, "France", "Prussia")
            _tick(w)
        assert not _events(w, "war", "Prussia")

    def test_16_the_dissolution_counts_the_cooldown_the_gate_reads(self):
        from backend.game_logic.dispatch import build_morning_dispatch
        w = _boot()
        _sit(w)
        w.threat_by_target["France"] = 95
        with _quiet():
            _tick(w)
            dispatch = build_morning_dispatch(w)
        text = json.dumps(dispatch, ensure_ascii=False)
        left = congress.cooldown_left(w)
        assert f"for {left} turns" in text
        assert f"for {congress.cooldown_turns(w)} turns" not in text or left == congress.cooldown_turns(w)

    def test_50b_two_signatures_on_one_tick_count_in_order(self):
        w = _boot()
        _sit(w)
        with _quiet():
            _tick(w)
        _set_score(w, "Prussia", 60)
        congress.note_ratification(w, ["Austria"], True)
        _peace(w, "Austria")
        with _quiet():
            _tick(w)
        counts = [e.get("standing") for e in _events(w, "recognized")]
        assert counts == sorted(counts) and len(set(counts)) == len(counts)

    def test_50c_the_bundle_never_reads_plus_plus(self):
        w = _boot()
        _sit(w)
        for court in congress.great_powers(w):
            assert "+ +" not in congress.price(w, court)["text"]

    def test_52_the_gate_line_names_the_breach(self):
        from backend.game_logic import fall
        w = _boot()
        _stage_titles(w)
        w.threat_by_target["France"] = 88
        assert "too high (88" in congress.state_line(w)
        w.threat_by_target["France"] = 50
        sov = fall.sovereign_of(w, "France")
        sov.captured_by = "Austria"
        line = congress.state_line(w)
        assert "the Emperor is a prisoner" in line and "the Emperor free" not in line

    def test_53_the_tab_says_what_broke(self):
        from backend.game_logic.diplomacy import declare_war
        w = _boot()
        _sit(w)
        with _quiet():
            _tick(w)
            declare_war(w, "France", "Ottoman")
            _tick(w)
        payload = congress.build_congress_payload(w)
        assert payload["phase"] == "cooldown"
        assert payload["dissolve_reason"].startswith("the Emperor drew the sword")

    def test_55_the_concluded_table_is_the_endings_own(self):
        w = _boot()
        _sit(w)
        for court in congress.great_powers(w):
            _latch(w, court)
        with _quiet():
            _tick(w, congress.congress_turns(w) + 1)
        assert congress.imperial_peace_signed(w)
        payload = congress.build_congress_payload(w)
        assert payload["phase"] == "concluded"
        for row in payload["courts"]:
            assert row["price"] == "" and not row["levers"]
            assert row["stance"] in congress.SATISFIED

    def test_56_the_universal_monarchy_carries_no_dissolved_strip(self):
        w = _boot()
        _sit(w)
        with _quiet():
            _tick(w, 2)
        w.threat_by_target["France"] = 95
        with _quiet():
            _tick(w)
        assert w.congress["status"] == congress.DISSOLVED
        w.threat_by_target["France"] = 10
        for court in congress.great_powers(w):
            for region in list(w.get_nation_regions(court)):
                w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        stamped = _tick(w)
        assert stamped and stamped[0]["detail"]["route"] == "universal_monarchy"
        assert stamped[0]["detail"]["sitting"] == []

    def test_46_the_universal_monarchy_is_never_told_as_a_signature(self):
        w = _boot()
        for court in congress.great_powers(w):
            for region in list(w.get_nation_regions(court)):
                w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        stamped = _tick(w)
        lines = stamped[0]["summary"]["verdict"]["lines"]
        assert not any("signed the order at Paris" in ln for ln in lines)
        from backend.ai.first_contact import _congress_goal_clause
        clause, signed = _congress_goal_clause(w)
        assert signed and "Congress of Paris" not in clause

    def test_60_a_terminal_term_outranks_a_spent_action(self):
        w = _boot()
        _sit(w)
        w.admin_actions_remaining = 0
        payload = congress.build_congress_payload(w)
        assert payload["unavailable_reason"].startswith("The Congress already sits")

    def test_42_the_moniteur_prints_the_answer_the_tick_took(self):
        from backend.game_logic import gazette
        w = _boot()
        _sit(w)
        w.gazette_issues = [{"turn": w.current_turn + 1, "special": False,
                             "special_reason": "", "congress": ["stale"]}]
        w.threat_by_target["France"] = 95
        with _quiet():
            _tick(w)
        issue = w.gazette_issues[-1]
        assert issue["congress"] != ["stale"]
        assert issue["special_reason"] == "THE CONGRESS OF PARIS DISSOLVES"
        assert issue["congress"][0].startswith("The Congress of Paris dissolves")
        assert gazette  # the module the tick re-composes through


# ════════════════════════════════════════════════════════════════════════
# The driver's Congress line (#50f #67)
# ════════════════════════════════════════════════════════════════════════

class TestTheDriverLine:
    def _digest(self):
        from tools import playtest_driver as D
        lines = []

        class Stub:
            record = staticmethod(lambda *a, **k: None)

            def _md(self, text):
                lines.append(text)
        stub = Stub()
        return stub, lines, D.Digest.congress_line

    def test_a_blocked_gate_and_a_reopened_gate_both_print(self):
        stub, lines, fn = self._digest()
        fn(stub, {"phase": "gate", "line": "THE CONGRESS OF PARIS — 43 of 50 titled · summon from the Cabinet (F1)"})
        assert lines == []
        fn(stub, {"phase": "gate", "line": "THE CONGRESS OF PARIS — 50 of 50 titled · Europe's alarm too high (85 — the Congress needs it below 80)"})
        assert len(lines) == 1
        opened = "THE CONGRESS OF PARIS — 50 of 50 titled · the powers may be summoned — summon from the Cabinet (F1)"
        fn(stub, {"phase": "gate", "line": opened})
        fn(stub, {"phase": "cooldown", "line": "THE CONGRESS OF PARIS — dissolved on turn 3"})
        fn(stub, {"phase": "gate", "line": opened})
        assert len(lines) == 4


# ════════════════════════════════════════════════════════════════════════
# The arms, DRIVEN (#61 #64): the committed fixtures played through the real
# driver — /command orders, real end turns, the enemy phase, the petitions
# answered by the stated policy — never `_tick` sittings.
# ════════════════════════════════════════════════════════════════════════

def _drive(tmp_path, name, script, save, turns, *extra):
    import os
    import subprocess
    import sys
    from pathlib import Path
    repo = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONHASHSEED="0")
    env.pop("PYTHONIOENCODING", None)
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        env.pop(key, None)
    env["INK_IRON_SAVE_DIR"] = str(tmp_path / "saves")
    proc = subprocess.run(
        [sys.executable, str(repo / "tools" / "playtest_driver.py"), "--name", name,
         "--seed", "historical", "--script", str(repo / script),
         "--from-save", str(repo / save), "--turns", str(turns),
         "--out", str(tmp_path), "--fresh", *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=900, env=env, cwd=str(repo))
    run = tmp_path / name
    assert (run / "meta.json").is_file(), proc.stderr[-2000:]
    meta = json.loads((run / "meta.json").read_text(encoding="utf-8"))
    digest = (run / "digest.md").read_text(encoding="utf-8")
    return meta, digest


class TestTheArmsDriven:
    def test_61_the_pressburg_arm_wins_the_imperial_peace(self, tmp_path):
        meta, digest = _drive(tmp_path, "pin-ge3-pressburg",
                              "tools/playtest_scripts/ge3_pressburg.json",
                              "tests/fixtures/playtest_saves/fixture_ge3_pressburg.json",
                              12, "--diplomacy", "accept", "--stop-on-ending")
        assert meta["status"] == "ending-reached", meta["status"]
        assert "ENDING — THE IMPERIAL PEACE" in digest
        turns = [int(line.split()[2]) for line in digest.splitlines()
                 if line.startswith("## Turn ")]
        assert turns and 33 <= turns[-1] <= 48

    def test_64_the_premature_arm_dissolves_under_pressure(self, tmp_path):
        meta, digest = _drive(tmp_path, "pin-ge3-premature",
                              "tools/playtest_scripts/ge3_premature.json",
                              "tests/fixtures/playtest_saves/fixture_ge3_premature.json",
                              10, "--diplomacy", "decline")
        assert "THE IMPERIAL PEACE" not in digest
        dissolved = [line for line in digest.splitlines()
                     if "THE CONGRESS OF PARIS — dissolved on turn" in line]
        assert dissolved, "the Congress never dissolved"
        on = int(dissolved[0].split("dissolved on turn ")[1].split(";")[0])
        # before its eighth day (summoned turn 1 → the eighth answer is turn 9)
        assert on < 9


class TestTheBoundaries:
    """#66: the ruled numbers at their edges."""

    def test_one_refuser_never_lowers_the_gate(self):
        w = _boot()
        _sit(w)
        for court in ("Britain", "Russia", "Austria"):
            _latch(w, court)
        assert congress.live_refusers(w) == ["Prussia"]
        assert congress.coalition_gate(w) is None
        assert coalition.brewing_gate(w) == coalition.THREAT_BREWING_MIN

    def test_two_refusers_lower_it_to_forty(self):
        w = _boot()
        _sit(w)
        for court in ("Britain", "Russia"):
            _latch(w, court)
        assert len(congress.live_refusers(w)) == 2
        assert congress.coalition_gate(w) == 40

    def test_the_alarm_ceiling_is_strict(self):
        w = _boot()
        _sit(w)
        w.threat_by_target["France"] = 79
        assert next(h for h in congress.hold_conditions(w) if h["key"] == "alarm")["met"]
        w.threat_by_target["France"] = 80
        assert not next(h for h in congress.hold_conditions(w) if h["key"] == "alarm")["met"]

    def test_the_sue_cadence_is_three_turns(self):
        w = _boot()
        _sit(w)
        assert congress.sue_due(w, "Austria")
        congress.note_sued(w, "Austria")
        w.current_turn += 2
        assert not congress.sue_due(w, "Austria")
        w.current_turn += 1
        assert congress.sue_due(w, "Austria")

    def test_the_grudge_is_ten_turns(self):
        w = _boot()
        _sit(w)
        w.threat_by_target["France"] = 95
        with _quiet():
            _tick(w)
        assert congress.grudge_contributions(w, 5)
        w.current_turn = int(w.congress["dissolved_turn"]) + 9
        assert congress.grudge_contributions(w, 5)
        w.current_turn = int(w.congress["dissolved_turn"]) + 10
        assert congress.grudge_contributions(w, 5) == []

    def test_a_withdrawal_is_logged_with_what_it_had_been(self):
        w = _boot()
        _sit(w)
        _set_score(w, "Prussia", 60)
        with _quiet():
            _tick(w)
        assert congress.answer(w, "Prussia")["stance"] == congress.RECOGNIZES
        w.capture_region("Hanover", "France")
        with _quiet():
            _tick(w)
        rows = _events(w, "withdrew", "Prussia")
        assert rows and rows[-1]["was"] == congress.RECOGNIZES
        assert _events(w, "recognized", "Prussia")


class TestToldOnce:
    def test_50d_the_war_of_the_congress_is_never_a_bare_war_headline_too(self):
        from backend.game_logic.dispatch import build_morning_dispatch
        w = _boot()
        _sit(w)
        with _quiet():
            _tick(w, 3)
        assert _events(w, "war", "Prussia"), "the War of the Congress did not fire"
        with _quiet():
            text = json.dumps(build_morning_dispatch(w), ensure_ascii=False)
        assert "Prussia and France are at war" not in text


class TestWhatTheSweepFound:
    """The pins the GE-3 sweep's first pass proved INERT, each built on the
    geometry where only the guarded branch decides."""

    def test_war_in_after_a_blocker_lifts(self):
        """A court refusing two turns while no coalition stood is WARNED at
        the next end turn and marches at the one after — two, not one."""
        w = _boot()
        _sit(w)
        standing = w.active_coalition
        w.active_coalition = None
        with _quiet():
            _tick(w, 2)
        assert congress.refusal_turns(w, "Prussia") == 2
        assert not _events(w, "warning", "Prussia")
        w.active_coalition = standing
        row = next(c for c in congress.build_congress_payload(w)["courts"]
                   if c["nation"] == "Prussia")
        assert row["war_in"] == 2
        with _quiet():
            _tick(w)
        assert _events(w, "warning", "Prussia") and not _events(w, "war", "Prussia")
        with _quiet():
            _tick(w)
        assert _events(w, "war", "Prussia")

    def test_14_a_court_in_a_truce_never_withdraws(self):
        w = _boot()
        _sit(w)
        w.diplomatic_states[w._make_diplo_key("Austria", "France")] = "ARMISTICE"
        w.invalidate_active_nations_cache()
        _set_score(w, "Austria", 60)
        assert congress.answer(w, "Austria")["stance"] == congress.RECOGNIZES
        w.capture_region("Tyrol", "France")
        assert "Austria" not in (w.congress.get("withdrawn") or {})

    def test_55_a_court_that_signed_with_gold_stays_signed_on_the_card(self):
        w = _boot()
        w.nation_gold["France"] = 20000
        _sit(w)
        for court in ("Britain", "Russia", "Austria"):
            _latch(w, court)
        _set_score(w, "Prussia", 40)
        assert congress.pay_sweetener(w, "Prussia", 1000)["stance"] == congress.RECOGNIZES
        with _quiet():
            _tick(w, congress.congress_turns(w) + 1)
        assert congress.imperial_peace_signed(w)
        # live, the sweetener no longer counts — the card must not re-read it
        assert congress.answer(w, "Prussia")["stance"] == congress.REFUSES
        row = next(c for c in congress.build_congress_payload(w)["courts"]
                   if c["nation"] == "Prussia")
        assert row["stance"] == congress.RECOGNIZES and row["price"] == ""
