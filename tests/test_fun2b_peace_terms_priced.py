"""Row FUN, Session FUN-2b "peace terms priced" — its behaviour test, opened by
FUN-2 (November 26, 2026) with three strict pins and built November 27, 2026
(`docs/NEXT_SESSION_PROMPT.md`'s FUN-2b block; `SYSTEMS_REFERENCE.md` §241;
the rules `backend/game_logic/land_price.py` and `fear.py`'s FUN-2b half; the
seams `tests/_fun2b_seams.py`).

The brief: "taking a province at the table costs war score (the settlement's own
scorer); a total conquest by treaty takes more than one war." FUN-2 made land
taken BY ARMS cost fear; FUN-2b prices land taken AT THE TABLE, gives the
table's land the same fear a capture gives, and land handed back the reverse.

The three pins FUN-2 wrote (strict xfails) are plain tests now, unchanged in
what they assert: the table's price keeps rising past five provinces; a cession
at the table frightens like a capture; land handed back calms the court.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path

import pytest

from backend.game_logic import fear as F
from backend.game_logic import land_price as LP
from backend.models.world_state import WorldState

SCENARIO = os.path.join("godot-client", "project-sovereign", "assets", "maps", "europe_1805.json")
AUSTRIA = ["Tyrol", "Carniola", "Croatia", "Hungary", "Moravia", "Bohemia", "Vienna"]
ROOT = Path(__file__).resolve().parents[1]


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _booted():
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


@pytest.fixture()
def world(_booted):
    return WorldState.from_dict(json.loads(json.dumps(_booted.to_dict(), default=str)))


def _score(world, a, b, value):
    key = world._make_diplo_key(a, b)
    world.war_scores[key] = value if key.split("|")[0] == a else -value


def _take(world, *regions, garrison=True):
    with _quiet():
        for region in regions:
            world.capture_region(region, "France")
            if garrison:
                world.regions[region].garrison_strength = 3000
                world.regions[region].garrison_detachment = True
    world.invalidate_active_nations_cache()


def _stage(world, terms=None, covered=("Austria",), mode="PROPOSE"):
    from backend.game_logic.settlement_staging import stage_settlement_confirm
    with _quiet():
        staged = stage_settlement_confirm(
            world, war_id="war_1", actor_nation="France", settlement_terms=terms,
            covered_enemy_participants=list(covered), selected_target_nation=covered[-1],
            caller_kind="player_editor", dialogue_mode=mode)
    assert staged.get("success"), staged
    return staged["diplomatic_dialogue"]


def _row(dialogue, court="Austria"):
    for row in dialogue.get("per_court_acceptance") or []:
        if row.get("nation") == court:
            return row
    raise AssertionError(court)


def _land_rows(dialogue, court="Austria"):
    return [s for s in (_row(dialogue, court).get("demand_suggestions") or [])
            if s.get("clause_type") == "territory_cede" and s.get("group") == "demand"]


def _cede(court, region, to="France"):
    return {"type": "territory_cede", "from": court, "to": to, "region": region}


def _apply(world, terms, war_id="war_1"):
    from backend.game_logic import settlement_ratify as SR
    with _quiet():
        return SR._apply_settlement_terms(world, settlement_terms=terms, war_id=war_id)


def _delta(before, world):
    after = dict(world.court_grudges)
    return {c: after.get(c, 0) - before.get(c, 0) for c in set(after) | set(before)
            if after.get(c, 0) != before.get(c, 0)}


def _table(world):
    inst = world.war_instances["war_1"]
    return LP.table_for(world, war_id="war_1", war_instance=inst,
                        proposer_side=inst["side_by_nation"]["France"],
                        proposer_side_leader="France", covered=["Austria"])


# ═══════════════════════════════════════════════════════════════════════
# The three pins FUN-2 wrote, plain tests now
# ═══════════════════════════════════════════════════════════════════════

class TestFUN2bPeaceTermsPriced:

    def test_a_bilateral_total_cession_is_refused_at_any_war_score(self, world):
        from backend.game_logic.diplomacy import calculate_acceptance
        from backend.game_logic.diplomacy import get_war_score_for
        key = world._make_diplo_key("France", "Austria")
        world.war_scores[key] = 100 if key.split("|")[0] == "France" else -100
        assert get_war_score_for(world, "France", "Austria") == 100     # France is winning
        result = calculate_acceptance({
            "type": "peace", "proposer_nation": "France", "target_nation": "Austria",
            "demands": [{"type": "territory", "regions": list(AUSTRIA),
                         "from": "Austria", "to": "France"}]}, world)
        assert result["outcome"] == "REJECT"
        # FUN-2b: refused by the rule, said in plain words (named apart from
        # the components, which their readers sum as figures)
        assert result.get("takes_every_province") is True
        assert "takes_every_province" not in result["components"]
        assert "No country gives up all its land at one peace" in result["feedback"]

    def test_the_tables_price_keeps_rising_past_five_provinces(self):
        from backend.game_logic.diplomatic_templates import calculate_raw_treaty_harshness
        from backend.game_logic.settlement_scoring import calculate_term_harshness_penalty

        def penalty(n):
            raw = calculate_raw_treaty_harshness({"clauses": [], "demands": [
                {"type": "territory_cede", "regions": AUSTRIA[:n]}]})
            return calculate_term_harshness_penalty(raw)["score"]

        assert penalty(7) < penalty(5)

    def test_a_cession_at_the_table_frightens_like_a_capture(self, world):
        from backend.game_logic import game_end
        region = world.regions["Tyrol"]
        region.controller = "France"
        region.stability = 50
        world.invalidate_active_nations_cache()
        game_end.record_province_title(world, "Tyrol", game_end.TITLE_TREATY, "Austria", "France")
        assert F.fear_of(world, "Bavaria") > 0

    def test_land_handed_back_calms_the_court(self, world):
        from backend.game_logic.diplomacy import hand_back_province
        world.capture_region("Tyrol", "France")
        before = F.fear_of(world, "Austria")
        hand_back_province(world, "Austria", "France", "Tyrol")
        assert F.fear_of(world, "Austria") < before


# ═══════════════════════════════════════════════════════════════════════
# The price (PRICE)
# ═══════════════════════════════════════════════════════════════════════

class TestThePrice:

    def test_every_province_costs_nine_on_the_land_term_with_no_floor(self):
        from backend.game_logic.diplomatic_templates import calculate_raw_treaty_harshness
        from backend.game_logic.settlement_scoring import calculate_term_harshness_penalty
        for n in range(1, 8):
            raw = calculate_raw_treaty_harshness({"clauses": [], "demands": [
                {"type": "territory_cede", "regions": AUSTRIA[:n]}]})
            assert calculate_term_harshness_penalty(raw)["score"] == -9 * n

    def test_a_courts_own_losses_count_every_province_and_the_capital_more(self, world):
        from backend.game_logic.settlement_scoring import calculate_leader_own_losses
        terms = [_cede("Austria", r) for r in AUSTRIA]
        got = calculate_leader_own_losses(world, accepting_leader="Austria", settlement_terms=terms)
        assert got["capital_lost"] is True and got["floor_lifted"] is True
        assert got["score"] == 7 * -5 - 15                       # -50: past the old -25 floor
        two = calculate_leader_own_losses(world, accepting_leader="Austria",
                                          settlement_terms=terms[:2])
        assert two["score"] == -10

    def test_the_list_price_is_fourteen_and_the_capital_twenty_nine(self, world):
        assert LP.list_price(world, "Austria", "Tyrol") == 14
        assert LP.list_price(world, "Austria", "Vienna") == 29

    def test_austrias_number_keeps_falling_past_five_on_the_board(self, world):
        _score(world, "France", "Austria", 100)
        table = _table(world)
        totals = [table.total([{"type": "peace"}] + [_cede("Austria", r) for r in AUSTRIA[:n]],
                              "Austria") for n in range(8)]
        assert all(b < a for a, b in zip(totals, totals[1:]))
        assert totals[5] - totals[6] == 14 and totals[6] - totals[7] == 29   # Vienna last

    def test_the_seam_down_restores_both_floors(self, world, monkeypatch):
        from backend.game_logic.settlement_scoring import (
            calculate_leader_own_losses, calculate_term_harshness_penalty)
        monkeypatch.setattr(LP, "the_tables_price_keeps_rising", lambda: False)
        assert calculate_term_harshness_penalty(2.1)["score"] == -45
        assert calculate_term_harshness_penalty(3.0)["score"] == -45
        got = calculate_leader_own_losses(world, accepting_leader="Austria",
                                          settlement_terms=[_cede("Austria", r) for r in AUSTRIA])
        assert got["score"] == -25 and got["floor_lifted"] is False


# ═══════════════════════════════════════════════════════════════════════
# The whole country (WHOLE)
# ═══════════════════════════════════════════════════════════════════════

class TestTheWholeCountry:

    def test_the_validator_refuses_a_package_that_takes_every_province(self, world):
        from backend.game_logic.settlement_validation import validate_settlement_terms
        _score(world, "France", "Austria", 100)
        inst = world.war_instances["war_1"]
        whole = [{"type": "peace"}] + [_cede("Austria", r) for r in AUSTRIA]
        got = validate_settlement_terms(whole, world=world, war_instance=inst,
                                        proposer_side=inst["side_by_nation"]["France"],
                                        enforce_solvency=False)
        assert got["valid"] is False and got["error"] == "takes_every_province"
        assert got["court"] == "Austria"
        assert "takes more than one war" in got["disabled_reason_display"]
        assert LP.whole_country_clause(world, whole[:-1], war_instance=inst) is None

    def test_a_peace_between_two_computer_courts_keeps_the_ninety_line(self, world):
        from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance
        inst = make_synthetic_war_instance("war_px", attackers=["Prussia"], defenders=["Saxony"],
                                           attacker_leader="Prussia", defender_leader="Saxony")
        world.war_instances["war_px"] = inst
        terms = [{"type": "peace"}, _cede("Saxony", "Dresden", to="Prussia")]
        assert LP.whole_country_clause(world, terms, war_instance=inst) is None
        _score(world, "Prussia", "Saxony", 50)
        _apply(world, terms, war_id="war_px")
        assert world.regions["Dresden"].controller == "Saxony"      # under 90: dropped, as before
        _score(world, "Prussia", "Saxony", 95)
        _apply(world, terms, war_id="war_px")
        assert world.regions["Dresden"].controller == "Prussia"     # D2: an AI war may erase a minor

    def test_the_ratifier_drops_a_whole_country_named_whatever_the_score(self, world):
        from backend.game_logic import settlement_ratify as SR
        _score(world, "France", "Saxony", 100)
        inst = world.war_instances["war_1"]
        if "Saxony" not in (inst.get("side_by_nation") or {}):
            inst["defenders"].append("Saxony")
            inst["side_by_nation"]["Saxony"] = "defenders"
            inst["active_participants"].append("Saxony")
        terms = [{"type": "peace"}, _cede("Saxony", "Dresden")]
        with _quiet():
            SR._apply_settlement_terms(world, settlement_terms=terms, war_id="war_1")
        assert world.regions["Dresden"].controller == "Saxony"
        assert "Saxony" in world.get_active_nations()

    def test_the_hand_pick_refuses_the_last_province_and_takes_the_one_before(self, world):
        from backend.game_logic.settlement_actions import handle_settlement_dialogue_action
        _score(world, "France", "Austria", 100)
        _take(world, "Tyrol", "Carniola", "Croatia", "Hungary", "Moravia")
        dialogue = _stage(world, terms=[{"type": "peace"}])

        def add(d, region):
            with _quiet():
                return handle_settlement_dialogue_action(
                    world, action="settlement_demand_add", dialogue=d,
                    action_params={"action": "settlement_demand_add", "nation": "Austria",
                                   "group": "demand", "clause_type": "territory_cede",
                                   "region": region})
        first = add(dialogue, "Bohemia")
        assert first.get("success") is True
        last = add(first["diplomatic_dialogue"], "Vienna")
        assert last.get("success") is False and last.get("error") == "takes_every_province"

    def test_the_guided_pool_never_offers_the_last_province(self, world):
        from backend.game_logic.settlement_baseline import _demand_baseline_region_candidates
        _take(world, *[r for r in AUSTRIA if r != "Bohemia"])
        assert world.get_nation_regions("Austria") == ["Bohemia"]
        assert _demand_baseline_region_candidates(
            world, court="Austria", proposer_side_participants=["France"]) == []

    @staticmethod
    def _austria_holds_nothing(world):
        # the Papal States' case the carve rule exists for: a court standing with
        # its every province in the carver's hands (set directly: no capture erases it)
        for name in AUSTRIA:
            world.regions[name].controller = "France"
        world.invalidate_active_nations_cache()

    def test_an_authored_carve_alone_keeps_the_decisive_victory_line(self, world):
        """The Papal States and Naples are one province each: the Roman Republic
        and Murat's crown (NA-6c, DY-6) stay reachable at a decisive victory."""
        from backend.game_logic.settlement_validation import evaluate_create_client_eligibility
        inst = world.war_instances["war_1"]
        self._austria_holds_nothing(world)
        _score(world, "France", "Austria", 60)
        low = evaluate_create_client_eligibility(
            world, war_instance=inst, template_id="Hungary", from_court="Austria", carver="France")
        assert low["eligible"] is False and low["refusal_code"] == "carve_total_annexation_blocked"
        _score(world, "France", "Austria", 95)
        high = evaluate_create_client_eligibility(
            world, war_instance=inst, template_id="Hungary", from_court="Austria", carver="France")
        assert high["eligible"] is True
        carve_only = [{"type": "peace"}, {"type": "create_client", "from": "Austria", "to": "France",
                                          "tag": "Hungary", "provinces": ["Hungary"]}]
        world.regions["Hungary"].controller = "Austria"
        world.invalidate_active_nations_cache()
        assert LP.whole_country_clause(world, carve_only, war_instance=inst) is None

    def test_cessions_and_a_carve_never_swallow_a_court(self, world):
        inst = world.war_instances["war_1"]
        _take(world, "Tyrol", "Carniola", "Croatia", "Moravia", "Bohemia")
        assert sorted(world.get_nation_regions("Austria")) == ["Hungary", "Vienna"]
        package = [{"type": "peace"}, _cede("Austria", "Vienna"),
                   {"type": "create_client", "from": "Austria", "to": "France",
                    "tag": "Hungary", "provinces": ["Hungary"]}]
        assert LP.whole_country_clause(world, package, war_instance=inst) == (2, "Austria")

    def test_a_two_court_peace_between_computer_courts_is_not_refused_by_the_rule(self, world):
        from backend.game_logic.diplomacy import calculate_acceptance
        result = calculate_acceptance({
            "type": "peace", "proposer_nation": "Prussia", "target_nation": "Saxony",
            "demands": [{"type": "territory", "regions": ["Dresden"]}]}, world)
        assert result.get("takes_every_province") is None

    def test_the_rule_binds_every_peace_of_frances_house_and_no_other(self, world):
        # `war_council.aim_cessions` (the AI's aim letter) and the letters read this
        assert LP.whole_rule_binds(world, "Austria", "Switzerland")     # a client of France
        assert LP.whole_rule_binds(world, "France", "Austria")
        assert not LP.whole_rule_binds(world, "Prussia", "Saxony")
        assert LP.whole_rule_binds(world, "Prussia", "Saxony", players_table=True)

    def test_an_ai_letter_never_takes_every_province_of_a_court_of_the_house(self, world):
        held = list(world.get_nation_regions("KingdomOfItaly"))
        demands = [{"type": "gold_lump", "value": 100}] + [
            {"type": "territory_cede", "value": 1, "regions": [r]} for r in held]
        out = LP.trim_whole_demands(world, "KingdomOfItaly", demands, "Austria")
        taken = {r for d in out for r in (d.get("regions") or [])}
        assert taken and not set(held) <= taken
        assert any(d["type"] == "gold_lump" for d in out)
        table = [_cede("KingdomOfItaly", r, to="Austria") for r in held]
        kept = LP.trim_whole_terms(world, "KingdomOfItaly", table)
        assert len(kept) == len(held) - 1

    def test_the_formables_keep_the_carves_decisive_victory_row(self, world):
        from backend.game_logic.formations import build_formables_payload
        TestTheWholeCountry._austria_holds_nothing(world)
        _score(world, "France", "Austria", 95)
        with _quiet():
            payload = build_formables_payload(world)
        rows = [r for r in (payload.get("formables") if isinstance(payload, dict) else payload) or []
                if isinstance(r, dict)]
        hungary = [r for r in rows if r.get("tag") == "Hungary"]
        assert hungary
        texts = [t for t in hungary[0].get("gate_terms") or [] if isinstance(t, dict)]
        assert any("needs war score 90" in str(t.get("text") or "") and t.get("met") for t in texts)

    def test_the_seam_down_restores_the_ninety_line(self, world, monkeypatch):
        monkeypatch.setattr(LP, "no_court_signs_away_every_province", lambda: False)
        inst = world.war_instances["war_1"]
        whole = [{"type": "peace"}] + [_cede("Austria", r) for r in AUSTRIA]
        assert LP.whole_country_clause(world, whole, war_instance=inst) is None


# ═══════════════════════════════════════════════════════════════════════
# The offers (OFFER) and the table's words
# ═══════════════════════════════════════════════════════════════════════

class TestTheOffers:

    def test_the_opening_draft_offers_land_only_where_the_court_still_signs(self, world):
        _score(world, "France", "Austria", 100)
        dialogue = _stage(world)
        terms = dialogue.get("settlement_terms") or []
        table = _table(world)
        for term in terms:
            if term.get("type") == "territory_cede":
                assert table.total(terms, str(term.get("from"))) >= 50

    def test_a_take_row_she_would_refuse_is_greyed_with_its_price(self, world):
        _score(world, "France", "Austria", 100)
        dialogue = _stage(world)
        row = _land_rows(dialogue)[0]
        total = _row(dialogue)["total"]
        after = total - row["price"]
        assert row["price"] > 0 and row["price_display"] == (
            f"would cost her {row['price']} more — she would fall to {after}")
        if after < 50 <= total:
            assert row["available"] is False
            assert row["disabled_reason_display"] == (
                f"She would refuse: taking {row['action_params']['region']} would bring her down "
                f"to {after}, under the 50 she needs to sign.")
        elif total < 50:
            assert row["available"] is False
            assert row["disabled_reason_display"] == (
                f"She would refuse: with these terms she is at {total}, under the 50 she needs "
                f"to sign, and taking {row['action_params']['region']} would bring her down to "
                f"{after}.")

    def test_a_take_row_she_would_give_is_offered_and_its_dropdown_kept_to_what_she_gives(self, world):
        _score(world, "France", "Austria", 100)
        dialogue = _stage(world, terms=[{"type": "peace"}])
        total = _row(dialogue)["total"]
        row = _land_rows(dialogue)[0]
        assert total - row["price"] >= 50
        assert row.get("available") is not False
        table = _table(world)
        for region in row.get("region_options") or []:
            assert table.total([{"type": "peace"}, _cede("Austria", region)], "Austria") >= 50

    def test_the_courts_line_says_how_many_more_provinces_she_would_give(self, world):
        _score(world, "France", "Austria", 100)
        dialogue = _stage(world, terms=[{"type": "peace"}])
        row = _row(dialogue)
        table = _table(world)
        terms = [{"type": "peace"}]
        gives = 0
        from backend.game_logic.settlement_baseline import _demand_baseline_region_candidates
        remaining = list(_demand_baseline_region_candidates(
            world, court="Austria", proposer_side_participants=["France"]))
        while remaining:                      # the cheapest she would still give, then the next
            scored = [(table.total(terms + [_cede("Austria", r)], "Austria") or -999, r)
                      for r in remaining]
            best = max(scored)
            if best[0] < 50:
                break
            terms, gives = terms + [_cede("Austria", best[1])], gives + 1
            remaining.remove(best[1])
        expected = {0: "She would give no land now: win more of the war, ask less of her, or "
                       "give her something for it.",
                    1: "She would give 1 more province now."}.get(
            gives, f"She would give {gives} more provinces now.")
        assert row["land_line"] == expected

    def test_a_land_line_on_the_table_says_what_it_costs(self, world):
        _score(world, "France", "Austria", 100)
        dialogue = _stage(world, terms=[{"type": "peace"}, _cede("Austria", "Bohemia")])
        lines = [d for d in _row(dialogue)["current_demands"] if d["clause_type"] == "territory_cede"]
        table = _table(world)
        price = (table.total([{"type": "peace"}], "Austria")
                 - table.total([{"type": "peace"}, _cede("Austria", "Bohemia")], "Austria"))
        total = _row(dialogue)["total"]
        assert lines[0]["price"] == price
        assert lines[0]["price_display"] == (
            f"costs her {price} — without it she would be at {total + price}")

    def test_the_legend_and_the_fear_line_ride_the_table(self, world):
        _score(world, "France", "Austria", 100)
        dialogue = _stage(world, terms=[{"type": "peace"}, _cede("Austria", "Bohemia")])
        assert dialogue["land_legend"].startswith(
            "The number beside a country's name is how willing she is to sign; she signs at 50.")
        assert "No country gives up every province it holds at one peace" in dialogue["land_legend"]
        assert dialogue["fear_line"].startswith("This peace would add to Europe's fear of France:")

    def test_harshers_land_is_asked_only_where_she_still_signs(self, world):
        from backend.game_logic.settlement_actions import _land_the_war_buys
        inst = world.war_instances["war_1"]
        side = inst["side_by_nation"]["France"]
        cand = {"Austria": dict(_cede("Austria", "Bohemia"), authored_by="talleyrand")}
        _score(world, "France", "Austria", 100)
        kept = _land_the_war_buys(world, cand, terms=[{"type": "peace"}], war_id="war_1",
                                  war_instance=inst, proposer_side=side, proposer_leader="France",
                                  covered=["Austria"])
        assert kept == cand
        heavy = [{"type": "peace"}, {"type": "gold_indemnity", "from": "Austria", "to": "France",
                                     "amount": 2000}]
        none = _land_the_war_buys(world, cand, terms=heavy, war_id="war_1", war_instance=inst,
                                  proposer_side=side, proposer_leader="France", covered=["Austria"])
        assert none == {}

    def test_a_declared_province_she_cannot_give_stays_off_the_opening_draft(self, world):
        from backend.game_logic.declared_goals import declared_draft
        inst = world.war_instances["war_1"]
        side = inst["side_by_nation"]["France"]
        key = world._make_diplo_key("France", "Austria")
        world.war_objectives[key]["France"]["declared_terms"] = [
            {"kind": "province", "from": "Austria", "region": "Bohemia", "declarer": "France"}]
        _score(world, "France", "Austria", 100)
        rich = declared_draft(world, war_instance=inst, proposer_side=side,
                              proposer_leader="France", covered=["Austria"], war_id="war_1")
        assert any(t.get("region") == "Bohemia" for t in rich)
        _score(world, "France", "Austria", 40)
        poor = declared_draft(world, war_instance=inst, proposer_side=side,
                              proposer_leader="France", covered=["Austria"], war_id="war_1")
        assert not any(t.get("region") == "Bohemia" for t in poor)

    def test_the_seam_down_offers_the_row_ungreyed(self, world, monkeypatch):
        monkeypatch.setattr(LP, "the_table_offers_only_what_the_war_buys", lambda: False)
        _score(world, "France", "Austria", 60)
        dialogue = _stage(world)
        for row in _land_rows(dialogue):
            assert row.get("available") is not False

    def test_an_unarmed_world_keeps_the_old_table(self, world):
        world.fear_rules = None
        _score(world, "France", "Austria", 100)
        dialogue = _stage(world, terms=[{"type": "peace"}, _cede("Austria", "Bohemia")])
        assert dialogue["land_legend"] == "" and dialogue["fear_line"] == ""
        row = _row(dialogue)
        assert "land_line" not in row
        assert all("price" not in d for d in row["current_demands"])

    def test_the_table_sends_whole_numbers(self, world):
        _score(world, "France", "Austria", 100)
        dialogue = _stage(world, terms=[{"type": "peace"}, _cede("Austria", "Bohemia")])

        def walk(node, path="root"):
            if isinstance(node, bool):
                return
            assert not isinstance(node, float), path
            if isinstance(node, dict):
                for k, v in node.items():
                    walk(v, f"{path}.{k}")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f"{path}[{i}]")
        for row in dialogue["per_court_acceptance"]:
            walk({k: row.get(k) for k in ("land_line", "current_demands", "demand_suggestions")})


# ═══════════════════════════════════════════════════════════════════════
# Land at the table frightens (FRIGHT)
# ═══════════════════════════════════════════════════════════════════════

class TestLandAtTheTableFrightens:

    def test_a_cession_writes_exactly_what_a_capture_would(self, world):
        expected = F.capture_deltas(world, "Bohemia", "Austria", "France")
        before = dict(world.court_grudges)
        _apply(world, [{"type": "peace"}, _cede("Austria", "Bohemia")])
        assert world.regions["Bohemia"].controller == "France"
        assert _delta(before, world) == expected

    def test_the_forecast_says_what_the_signature_writes(self, world):
        terms = [{"type": "peace"}, _cede("Austria", "Bohemia")]
        forecast = F.table_forecast(world, terms)
        before = dict(world.court_grudges)
        _apply(world, terms)
        assert forecast["adds"] == _delta(before, world)

    def test_land_france_already_held_frightens_nobody_again(self, world):
        _take(world, "Tyrol")
        before = dict(world.court_grudges)
        assert F.table_forecast(world, [_cede("Austria", "Tyrol")])["adds"] == {}
        _apply(world, [{"type": "peace"}, _cede("Austria", "Tyrol")])
        assert _delta(before, world) == {}

    def test_a_status_quo_retention_frightens_nobody_again(self, world):
        from backend.game_logic import game_end
        _take(world, "Tyrol")
        before = dict(world.court_grudges)
        game_end.record_province_title(world, "Tyrol", game_end.TITLE_TREATY, "Austria", "France",
                                       retained=True)
        assert _delta(before, world) == {}

    def test_a_carve_to_a_client_of_france_frightens(self, world):
        from backend.game_logic import game_end
        expected = F.capture_deltas(world, "Hungary", "Austria", "France")
        before = dict(world.court_grudges)
        world.regions["Hungary"].controller = "Switzerland"          # a client of France's house
        world.invalidate_active_nations_cache()
        game_end.record_carve_titles(world, ["Hungary"], "Austria", "Switzerland", "France")
        assert _delta(before, world).get("Austria", 0) == expected["Austria"] > 0

    def test_a_cession_between_computer_courts_frightens_nobody(self, world):
        from backend.game_logic import game_end
        before = dict(world.court_grudges)
        world.regions["Tyrol"].controller = "Bavaria"
        game_end.record_province_title(world, "Tyrol", game_end.TITLE_TREATY, "Austria", "Bavaria")
        assert _delta(before, world) == {}

    def test_the_seam_down_frightens_nobody(self, world, monkeypatch):
        monkeypatch.setattr(F, "land_at_the_table_frightens", lambda: False)
        before = dict(world.court_grudges)
        _apply(world, [{"type": "peace"}, _cede("Austria", "Bohemia")])
        assert _delta(before, world) == {}

    def test_the_fear_line_names_who_would_cross_the_line(self, world):
        world.court_grudges["Saxony"] = 48
        line = F.table_line(world, [_cede("Austria", "Bohemia")])
        assert "Saxony +8" in line
        assert ("With it Saxony's fear of France would reach 56 — past the 50 at which a "
                "country joins a coalition: she would join" in line
                or "Saxony's fear of France would reach 56, past 50, but she would stay out" in line)


# ═══════════════════════════════════════════════════════════════════════
# Land handed back calms (CALM)
# ═══════════════════════════════════════════════════════════════════════

class TestLandHandedBackCalms:

    def test_the_court_calms_by_exactly_what_taking_it_added(self, world):
        from backend.game_logic.diplomacy import hand_back_province
        before = dict(world.court_grudges)
        _take(world, "Tyrol")
        added = _delta(before, world)
        mid = dict(world.court_grudges)
        hand_back_province(world, "Austria", "France", "Tyrol")
        assert _delta(mid, world) == {"Austria": -added["Austria"]}     # Bavaria keeps hers

    def test_a_cession_from_france_at_the_table_calms_its_court(self, world):
        _take(world, "Tyrol")
        mid = dict(world.court_grudges)
        line = F.table_line(world, [_cede("France", "Tyrol", to="Austria")])
        assert line.startswith("Handing back Tyrol would calm Austria: her fear of France falls")
        _apply(world, [{"type": "peace"}, _cede("France", "Tyrol", to="Austria")])
        assert _delta(mid, world).get("Austria", 0) < 0

    def test_the_status_quos_return_home_calms(self, world):
        from backend.game_logic import game_end
        _take(world, "Tyrol")
        mid = dict(world.court_grudges)
        game_end._return_home(world, "Tyrol", "Austria", "France")
        assert _delta(mid, world).get("Austria", 0) < 0

    def test_a_surety_going_home_calms(self, world):
        _take(world, "Tyrol")
        mid = dict(world.court_grudges)
        world._return_surety_regions({"from": "Austria", "to": "France",
                                      "surety_regions": ["Tyrol"]}, "Austria|France")
        assert world.regions["Tyrol"].controller == "Austria"
        assert _delta(mid, world).get("Austria", 0) < 0

    def test_the_ledger_saves_and_loads(self, world):
        _take(world, "Tyrol")
        taken = dict(world.fear_book["taken"]["Tyrol"])
        again = WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))
        assert again.fear_book["taken"]["Tyrol"] == taken
        assert F.clean_book({"taken": {"Tyrol": {"Austria": "x", "": 3}, "": {"A": 1}}}) == {
            "causes": {}, "faded": {}}

    def test_the_ledger_keeps_only_what_the_house_holds(self, world):
        _take(world, "Tyrol")
        world.regions["Tyrol"].controller = "Austria"
        world.invalidate_active_nations_cache()
        F.fade(world)
        assert "Tyrol" not in (world.fear_book.get("taken") or {})

    def test_a_rising_is_not_a_hand_back(self, world):
        _take(world, "Tyrol", garrison=False)
        mid = dict(world.court_grudges)
        with _quiet():
            F.rise(world, "Tyrol")
        assert world.regions["Tyrol"].controller == "Austria"
        assert _delta(mid, world) == {}

    def test_the_seam_down_calms_nobody_and_keeps_no_ledger(self, world, monkeypatch):
        from backend.game_logic.diplomacy import hand_back_province
        monkeypatch.setattr(F, "land_handed_back_calms", lambda: False)
        _take(world, "Tyrol")
        assert "taken" not in world.fear_book
        mid = dict(world.court_grudges)
        hand_back_province(world, "Austria", "France", "Tyrol")
        assert _delta(mid, world) == {}


# ═══════════════════════════════════════════════════════════════════════
# The surfaces: the two-court card, the footer, the Codex, the client
# ═══════════════════════════════════════════════════════════════════════

class TestTheSurfaces:

    def test_the_two_court_card_says_the_peaces_fear(self, world):
        from backend.game_logic.diplomatic_dialogue import _bilateral_fear_line
        line = _bilateral_fear_line(world, {"demands": [
            {"type": "territory_cede", "regions": ["Bohemia"]}]}, "France", "Austria")
        assert line.startswith("This peace would add to Europe's fear of France:")
        assert _bilateral_fear_line(world, {"demands": []}, "France", "Austria") == ""

    def test_the_footer_says_the_table_frightens_and_a_hand_back_calms(self, world):
        footer = F.league_footer(world)
        assert "by force or at the peace table" in footer
        assert "calms the country it goes to" in footer

    def test_the_codex_says_the_new_rules(self):
        text = (ROOT / "godot-client" / "project-sovereign" / "scripts" / "codex_terms.gd").read_text(
            encoding="utf-8")
        assert "by force or at the peace table" in text
        assert "No country gives up every province it holds at one peace" in text
        assert "the sixth costs as much as the first" in text
        assert "A province you hand back calms the country it goes to" in text

    def test_the_client_draws_the_prices_the_line_the_legend_and_the_fear(self):
        text = (ROOT / "godot-client" / "project-sovereign" / "scripts"
                / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        for key in ('line.get("price_display")', 'row.get("land_line")', 'sugg.get("price_display")',
                    'data.get("land_legend")', 'data.get("fear_line")'):
            assert key in text, key


# ═══════════════════════════════════════════════════════════════════════
# The seams
# ═══════════════════════════════════════════════════════════════════════

class TestTheSeams:

    def test_every_seam_ships_up_and_replays_down(self):
        from tests._fun2b_seams import FUN2B_SEAMS_DOWN, SEAMS
        from tests._oct27_seams import OCT27_SEAMS_DOWN
        assert [row for row, _m, _n in SEAMS] == ["PRICE", "WHOLE", "OFFER", "FRIGHT", "CALM"]
        for _row_name, module, name in SEAMS:
            assert getattr(module, name)() is True
        for spec in FUN2B_SEAMS_DOWN:
            assert spec in OCT27_SEAMS_DOWN


# ═══════════════════════════════════════════════════════════════════════
# The review's rows (a frozen copy, three lanes — BUG_FIXES "Row FUN, Session FUN-2b")
# ═══════════════════════════════════════════════════════════════════════

class TestTheReviewsRows:

    def test_land_taken_from_france_and_ceded_back_frightens_nobody(self, world):
        """FUN2B-7: the capture road's own "recovered" rule at the treaty road."""
        prior = {"kind": "conquest", "from": "France", "holder": "Austria", "house": "Austria"}
        before = dict(world.court_grudges)
        world.regions["Bohemia"].controller = "France"
        world.invalidate_active_nations_cache()
        assert F.treaty_moves_land(world, "Bohemia", "Austria", "France", prior) == 0
        assert _delta(before, world) == {}
        world.regions["Bohemia"].controller = "Austria"
        world.province_title["Bohemia"] = dict(prior)
        world.invalidate_active_nations_cache()
        assert F.table_forecast(world, [_cede("Austria", "Bohemia")])["adds"] == {}

    def test_a_retention_of_enemy_held_ground_calms_nobody(self, world):
        """FUN2B-8: only land France's house HELD is handed back."""
        _take(world, "Tyrol")
        mid = dict(world.court_grudges)
        enemy_held = {"kind": "conquest", "from": "France", "holder": "Austria", "house": "Austria"}
        assert F.treaty_moves_land(world, "Tyrol", "France", "Austria", enemy_held) == 0
        assert _delta(mid, world) == {}

    def test_what_a_taking_added_fades_as_the_fear_does(self, world):
        """FUN2B-9: an old conquest handed back never wipes fear a newer one added."""
        from backend.game_logic.diplomacy import hand_back_province
        _take(world, "Tyrol")
        added = int(world.fear_book["taken"]["Tyrol"]["Austria"])
        for _ in range(3):
            F.fade(world)
        left = added - 3 * F.rule(world, "fade")
        assert world.fear_book["taken"]["Tyrol"]["Austria"] == left
        world.court_grudges["Austria"] = 40              # a newer taking's fear on top
        hand_back_province(world, "Austria", "France", "Tyrol")
        assert world.court_grudges["Austria"] == 40 - left

    def test_the_fear_reads_the_board_as_it_stood_before_the_cession(self, world):
        """FUN2B-10: the treaty roads move the controller before the title — the
        courts beside the province still count as the loser's neighbours."""
        world.regions["Swabia"].controller = "Austria"            # not Austria's homeland
        world.invalidate_active_nations_cache()
        expected = F.capture_deltas(world, "Swabia", "Austria", "France")
        assert F.table_forecast(world, [_cede("Austria", "Swabia")])["adds"] == expected
        before = dict(world.court_grudges)
        _apply(world, [{"type": "peace"}, _cede("Austria", "Swabia")])
        assert world.regions["Swabia"].controller == "France"
        assert _delta(before, world) == expected

    def test_a_fault_in_the_fear_never_costs_a_province_its_title(self, world, monkeypatch):
        """FUN2B-11: the hook has its own guard."""
        from backend.game_logic import game_end

        def boom(*_a, **_k):
            raise RuntimeError("fear fault")
        monkeypatch.setattr(F, "treaty_moves_land", boom)
        world.regions["Bohemia"].controller = "France"
        game_end.record_province_title(world, "Bohemia", game_end.TITLE_TREATY, "Austria", "France")
        assert world.province_title["Bohemia"]["holder"] == "France"

    def test_the_last_province_greying_obeys_its_seam(self, world, monkeypatch):
        """FUN2B-12: the seam down restores the old table's offers too."""
        _take(world, *[r for r in AUSTRIA if r != "Bohemia"])
        assert LP.keeps_one(world, "Austria", [], "Bohemia") is False
        monkeypatch.setattr(LP, "no_court_signs_away_every_province", lambda: False)
        assert LP.keeps_one(world, "Austria", [], "Bohemia") is True

    def test_a_coalition_that_cannot_form_yet_reads_as_ready_not_joined(self, world, monkeypatch):
        """FUN2B-13: "she would join ... but a coalition needs 3 ... so not yet"."""
        real = F.table_forecast

        def forecast(w, terms):
            got = real(w, terms)
            got["joiners"] = ["Saxony"]
            got["crossing"] = ["Saxony"]
            got["when"] = ("but a coalition needs 3 countries and only 2 would stand against us, "
                           "so not yet")
            got["adds"] = dict(got["adds"], Saxony=8)
            return got
        monkeypatch.setattr(F, "table_forecast", forecast)
        world.active_coalition = None
        line = F.table_line(world, [_cede("Austria", "Bohemia")])
        assert "she would be ready to join a coalition against us — but a coalition needs 3" in line

    def test_a_free_province_says_she_would_stay_at_her_number(self):
        """FUN2B-14."""
        assert LP.price_words(0, after=12) == "would cost her nothing — she would stay at 12"
        assert LP.price_words(14, after=56) == "would cost her 14 more — she would fall to 56"

    def test_the_province_letter_says_the_calm_before_the_click(self, world):
        """FUN2B-15: the "return our province" letter is a click road that moves land."""
        from backend.game_logic.ai_diplomacy import (
            PROVINCE_RETURN_TYPE, _build_province_return_dialogue)
        _take(world, "Tyrol")
        proposal = {"source": "Austria", "proposal_type": PROVINCE_RETURN_TYPE,
                    "terms": {"type": PROVINCE_RETURN_TYPE, "proposer_nation": "Austria",
                              "target_nation": "France", "sweeteners": [], "clauses": [],
                              "demands": [{"type": "territory_cede", "value": 1,
                                           "regions": ["Tyrol"]}],
                              "region": "Tyrol"}}
        dialogue = _build_province_return_dialogue(proposal, world)
        line = dialogue["popup_payload"]["return_line"]
        assert line.startswith("Handing back Tyrol would calm Austria: her fear of France falls")
        assert line in dialogue["popup_payload"]["clauses"]

    def test_each_province_in_the_dropdown_says_its_own_price(self, world):
        """FUN2B-16: the row's price is its first province's."""
        _score(world, "France", "Austria", 100)
        dialogue = _stage(world, terms=[{"type": "peace"}])
        row = _land_rows(dialogue)[0]
        options = row.get("region_options") or []
        labels = row.get("region_labels") or []
        assert len(labels) == len(options)
        for region, label in zip(options, labels):
            assert label.startswith(f"{region} (would cost her ")

    def test_the_client_draws_the_peace_cards_fear_and_the_legend_only_where_prices_are(self):
        """FUN2B-17/18: the two-court PEACE card is the peace preview; the legend
        speaks of figures drawn only on the authoring surface."""
        text = (ROOT / "godot-client" / "project-sovereign" / "scripts"
                / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        preview = text.split("func _build_peace_preview_content", 1)[1].split("\nfunc ", 1)[0]
        assert 'data.get("fear_line")' in preview
        assert 'land_legend != "null" and authoring_surface' in text
        assert 'sugg.get("region_labels")' in text
        letter = (ROOT / "godot-client" / "project-sovereign" / "scripts"
                  / "incoming_proposal_popup.gd").read_text(encoding="utf-8")
        assert 'accept_btn.tooltip_text = str(data.get("return_line", ""))' in letter


class TestTheHooksRows:
    """The commit hook's first run (FUN2B-22 … FUN2B-24): what the whole suite
    found that the touched families had not."""

    def test_a_padded_scroll_keeps_its_pad_when_only_its_content_changes(self):
        """FUN2B-22: a change of a scroll's CONTENT alone keeps its whole-line
        pad and measures the lines again; only a change of its width, its
        box's height or its unpadded window takes the pad away first. The
        driven pin is `test_dd_b_the_client_hands`'s
        `test_the_peace_table_stands_still_under_a_dial` (the table's body
        swung 11 px for two frames under its first press)."""
        utils = (ROOT / "godot-client" / "project-sovereign" / "scripts" / "utils.gd").read_text(encoding="utf-8")
        settled = utils.split("static func _scroll_window_settled(", 1)[1].split("\nstatic func ", 1)[0]
        keep = settled.index("if _same_window(sc, rec, spacer, was, key):\n\t\t\treturn true")
        assert keep < settled.index('rec["h0"] = -1.0'), "the content-only check comes before the reset"
        same = utils.split("static func _same_window(", 1)[1].split("\nstatic func ", 1)[0]
        assert 'unpadded += float(rec["floor0"]) - float(rec["floor_set"])' in same
        assert 'unpadded += spacer.custom_minimum_size.y * float(rec["share"])' in same
        assert 'return absf(unpadded - float(rec["h0"])) <= 0.5' in same

    def test_a_province_lookup_that_fails_is_reported_not_swallowed(self, monkeypatch):
        """FUN2B-23: the land-price module's one lookup of what a court holds
        reports a fault (CODE-3, `errors.report`) instead of three silent
        handlers."""
        calls = []
        monkeypatch.setattr(LP, "report", lambda exc, site: calls.append(site))

        class _NoLookup:
            def get_nation_regions(self, court):
                raise RuntimeError("no board")

        assert LP._held(_NoLookup(), "Austria") == set()
        assert calls == ["land_price._held: get_nation_regions"]
        assert LP.takes_every_province(_NoLookup(), "Austria", [{"type": "territory_cede", "from": "Austria",
                                                                 "regions": ["Tyrol"]}]) is False
