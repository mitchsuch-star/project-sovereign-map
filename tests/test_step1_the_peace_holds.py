"""Score Finish Step 1 "The peace holds" (September 29, 2026) — RS-1, RS-2,
RS-10, RS-16, SF-V1 and SF-V5. Spec: docs/SCORE_FINISH_SPEC.md §3 Step 1
(the landing record) and §6.1 (RS-D1, pinned in
`test_rs_d1_recognition_by_defeat.py`); rules SYSTEMS_REFERENCE.md §81; rows
BUG_FIXES.md §Full Play Retest.

The September-28 retest's two P1s: RS-1 — a fresh peace re-broken by an
ally's offensive cascade (Britain and Russia signed with France on turn 10
and were dragged back on turn 12 by Austria's declaration); RS-2 — the
league the summons made possible marched Austria, and Austria's war
unsigned what it had ceded (47 → 41 of 45) on the same end turn the
Congress dissolved. Every pin here drives the real seams — `declare_war`,
`form_coalition`, the settlement ratifier, the ONE diplomatic-state setter,
the per-turn title reconciliation, `POST /command`'s own producers — and
reads the answer back.
"""

import contextlib
import copy
import io
import json
from pathlib import Path

import pytest

from backend.game_logic import ai_diplomacy, coalition, congress, dispatch, game_end
from backend.game_logic import diplomacy as D
from backend.game_logic.settlement_ratify import (
    ratify_settlement_confirm,
    write_settlement_peace_floors,
)
from backend.game_logic.settlement_staging import stage_settlement_confirm
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCEN = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
           / "europe_1805.json")
T24 = (REPO / "docs" / "audits" / "playtest_digests" / "rs0928-hand-played"
       / "retest_t24_summonable.json")
THE_FIVE = ("Vienna", "Bohemia", "Moravia", "Tyrol", "Carniola")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _boot() -> WorldState:
    with _quiet():
        return WorldState.from_scenario(SCEN)


def _hold(world, region, holder, taken_from, kind=game_end.TITLE_CONQUEST):
    world.regions[region].controller = holder
    game_end.record_province_title(world, region, kind, taken_from, holder)
    world.invalidate_active_nations_cache()


def _ratify(world, proposer, target, ptype="peace", demands=None):
    with _quiet():
        return world._ratify_treaty({
            "proposer_nation": proposer, "target_nation": target,
            "type": ptype, "sweeteners": [], "demands": list(demands or [])})


def _declare(world, aggressor, target):
    with _quiet():
        return D.declare_war(world, aggressor, target)


def _stage_titles(w, need=None):
    need = congress.hold_titled(w) if need is None else need
    for nation in ("Hanover", "Denmark", "Portugal", "Sardinia", "Naples",
                   "Saxony", "Hesse"):
        for region in sorted(w.get_nation_regions(nation)):
            if congress.titled(w)["count"] >= need:
                return
            if region == "Lisbon":
                continue
            _hold(w, region, "France", nation, kind=game_end.TITLE_TREATY)


def _sit(w):
    _stage_titles(w)
    w.diplomatic_points = 6
    with _quiet():
        result = congress.summon(w)
    assert result["success"], result["message"]
    return result


def _tick(w, n=1):
    with _quiet():
        for _ in range(n):
            w.current_turn += 1
            game_end.process_end_of_turn(w, turn_ended=w.current_turn - 1)


def _events(w, phase, court=None):
    return [e for e in w.event_log if e.get("type") == "congress"
            and e.get("phase") == phase and (court is None or e.get("court") == court)]


def _peace_with_the_coalition(w):
    """The retest's turn-10 shape: Britain, Russia and Austria each sign a
    bilateral peace with France (the ratifier stamps the pair resolved)."""
    for court in ("Britain", "Russia", "Austria"):
        _ratify(w, court, "France")
    for court in ("Britain", "Russia", "Austria"):
        assert w.get_diplomatic_state(court, "France") == "PEACE"
        assert coalition.peace_with_target_is_fresh(court, w, "France")


# ════════════════════════════════════════════════════════════════════════
# RS-1 — the offensive cascade keeps a fresh peace
# ════════════════════════════════════════════════════════════════════════

class TestTheCascadeKeepsAFreshPeace:

    def test_the_retest_shape_britain_and_russia_stay_at_peace(self):
        w = _boot()
        w.current_turn = 10
        _peace_with_the_coalition(w)
        w.current_turn = 12
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        result = _declare(w, "Austria", "France")
        assert result["success"]
        assert w.get_diplomatic_state("Austria", "France") == "WAR"
        for court in ("Britain", "Russia"):
            assert w.get_diplomatic_state(court, "France") == "PEACE", court
        barred = {e["nation"]: e for e in result["war_entry_ledger"]
                  if e["path"] == "hard_illegal"}
        assert barred["Britain"]["reason"] == "fresh peace with France"
        assert barred["Russia"]["reason"] == "fresh peace with France"
        assert barred["Britain"]["side"] == "attacker"
        # nobody was refused a call they were free to answer
        assert not any(e["path"].startswith("refused") for e in result["war_entry_ledger"])

    def test_the_lever_down_reproduces_the_retest(self, monkeypatch):
        monkeypatch.setattr(D, "THE_CASCADE_KEEPS_A_FRESH_PEACE", False)
        w = _boot()
        w.current_turn = 10
        _peace_with_the_coalition(w)
        w.current_turn = 12
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        _declare(w, "Austria", "France")
        assert w.get_diplomatic_state("Britain", "France") == "WAR"
        assert w.get_diplomatic_state("Russia", "France") == "WAR"

    def test_the_bar_reads_its_three_seams_in_order(self):
        w = _boot()
        w.current_turn = 10
        _peace_with_the_coalition(w)
        assert D.offensive_call_bar(w, "Britain", "France") == "fresh peace with France"
        # the floor lapses; a pair cooldown still binds
        w.current_turn = 10 + coalition.FRESH_PEACE_FLOOR_TURNS
        assert D.offensive_call_bar(w, "Britain", "France") == ""
        w.armistice_cooldowns[w._make_diplo_key("Britain", "France")] = 3
        assert D.offensive_call_bar(w, "Britain", "France") == (
            "a truce's cooldown binds it to France (3 more turns)")
        w.armistice_cooldowns.pop(w._make_diplo_key("Britain", "France"))
        # while the Congress sits, a court that answers it is not called
        _sit(w)
        congress.note_ratification(w, ["Britain"], True, beaten=["Britain"])
        assert congress.answer(w, "Britain")["stance"] == congress.RECOGNIZES
        assert D.offensive_call_bar(w, "Britain", "France") == (
            "it recognizes the Congress — the Congress of Paris sits")

    def test_a_pair_cooldown_bars_the_call_at_the_cascade(self):
        w = _boot()
        w.current_turn = 10
        _peace_with_the_coalition(w)
        w.current_turn = 10 + coalition.FRESH_PEACE_FLOOR_TURNS + 1
        w.armistice_cooldowns[w._make_diplo_key("Britain", "France")] = 4
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        result = _declare(w, "Austria", "France")
        assert w.get_diplomatic_state("Britain", "France") == "PEACE"
        assert w.get_diplomatic_state("Russia", "France") == "WAR"
        barred = {e["nation"]: e["reason"] for e in result["war_entry_ledger"]
                  if e["path"] == "hard_illegal"}
        assert barred == {"Britain": "a truce's cooldown binds it to France (4 more turns)"}

    def test_the_league_that_forms_the_turn_after_keeps_the_peace(self):
        """The retest's headline, at the coalition's own seam: the league
        forms at T+1 around Austria and Russia; Austria's declaration
        cascades to Britain through the boot's alliance triangle — and
        Britain, fresh from the table, stays at peace."""
        w = _boot()
        w.current_turn = 10
        _peace_with_the_coalition(w)
        w.current_turn = 11
        with _quiet():
            result = coalition.form_coalition(["Austria", "Russia"], w)
        assert result.get("success"), result
        assert w.get_diplomatic_state("Austria", "France") == "WAR"
        assert w.get_diplomatic_state("Russia", "France") == "WAR"
        assert w.get_diplomatic_state("Britain", "France") == "PEACE"
        assert "Britain" not in (w.active_coalition or {}).get("members", [])

    def test_the_league_lever_down_marches_britain_back(self, monkeypatch):
        """RS-1's lever down reproduces the cascade — with SFR-DR1's lever
        down too (the economy audit, October 5, 2026, re-seated consciously):
        since the league's members declare in their own right, Austria's
        declaration no longer sweeps her allies in at all, so the shipped
        march back needs both levers down; with SFR-DR1 up Britain keeps the
        peace even with RS-1's lever down."""
        monkeypatch.setattr(D, "THE_CASCADE_KEEPS_A_FRESH_PEACE", False)
        monkeypatch.setattr(coalition, "THE_LEAGUE_DECLARES_IN_ITS_OWN_RIGHT", False)
        w = _boot()
        w.current_turn = 10
        _peace_with_the_coalition(w)
        w.current_turn = 11
        with _quiet():
            result = coalition.form_coalition(["Austria", "Russia"], w)
        assert result.get("success"), result
        assert w.get_diplomatic_state("Britain", "France") == "WAR"

        monkeypatch.setattr(coalition, "THE_LEAGUE_DECLARES_IN_ITS_OWN_RIGHT", True)
        w = _boot()
        w.current_turn = 10
        _peace_with_the_coalition(w)
        w.current_turn = 11
        with _quiet():
            result = coalition.form_coalition(["Austria", "Russia"], w)
        assert result.get("success"), result
        assert w.get_diplomatic_state("Britain", "France") == "PEACE"

    def test_the_defensive_arm_is_untouched(self):
        """An attack on a court whose defensive ally just signed with the
        attacker: the ally answers the attack (the fresh peace is the
        AGGRESSOR's to break, and he broke it)."""
        w = _boot()
        w.current_turn = 10
        _peace_with_the_coalition(w)
        w.current_turn = 12
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        # France attacks Austria: Britain and Russia are Austria's allies
        # (ALLIANCE answers offensively AND defensively).
        _declare(w, "France", "Austria")
        assert w.get_diplomatic_state("Britain", "France") == "WAR"
        assert w.get_diplomatic_state("Russia", "France") == "WAR"


class TestTheWarPreviewNamesTheBarredAlly:

    def _spain_bound(self):
        """France at peace with Austria; Spain (France's ally, at peace with
        Austria since the boot) under a pair cooldown with Austria."""
        w = _boot()
        _austria_out_of_the_war(w)
        assert w.get_diplomatic_state("Spain", "Austria") == "PEACE"
        w.armistice_cooldowns[w._make_diplo_key("Spain", "Austria")] = 3
        return w

    def test_a_barred_ally_is_named_apart_with_the_cascades_reason(self):
        w = self._spain_bound()
        preview = D.preview_war_declaration(w, "France", "Austria")
        assert {"nation": "Spain",
                "reason": "a truce's cooldown binds it to Austria (3 more turns)"} in preview["offensive_barred"]
        assert "Spain" not in preview["offensive_joiners"]
        # the cascade agrees with the review
        w.diplomatic_points = 9
        result = _declare(w, "France", "Austria")
        assert result["success"], result
        assert w.get_diplomatic_state("Spain", "Austria") == "PEACE"

    def test_the_lever_down_promises_the_ally_the_cascade_would_refuse(self, monkeypatch):
        monkeypatch.setattr(D, "THE_CASCADE_KEEPS_A_FRESH_PEACE", False)
        w = self._spain_bound()
        preview = D.preview_war_declaration(w, "France", "Austria")
        assert preview["offensive_barred"] == []
        assert "Spain" in preview["offensive_joiners"]


class TestTheSettlementWritesThePairCooldown:

    def _two_v_two(self):
        from tests.test_common_peace_c2_ratification import (
            _install_two_v_two_war, _stage_dialogue)
        world = WorldState()
        _install_two_v_two_war(world)
        return world, _stage_dialogue

    def test_every_pair_moved_to_peace_carries_the_fresh_peace_floor(self, monkeypatch):
        from backend.game_logic import settlement_scoring as SS
        from tests.test_common_peace_c2_ratification import _acceptance_always_passes
        monkeypatch.setattr(SS, "calculate_common_peace_acceptance", _acceptance_always_passes)
        world, stage = self._two_v_two()
        dialogue = stage(world, settlement_terms=[])
        with _quiet():
            result = ratify_settlement_confirm(world, dialogue)
        assert result["success"] and result["war_ended"]
        floor = coalition.FRESH_PEACE_FLOOR_TURNS
        for pair in ("Austria|France", "Austria|Saxony", "France|Prussia", "Prussia|Saxony"):
            assert world.diplomatic_states[pair] == "PEACE"
            assert world.armistice_cooldowns.get(pair) == floor, pair
        # the store every war-entry gate reads
        assert D.offensive_call_bar(world, "Prussia", "France").startswith(
            "fresh peace with France") or D.offensive_call_bar(
            world, "Prussia", "France").startswith("a truce's cooldown")

    def test_the_ai_ai_third_party_peace_carries_the_same_floor(self):
        """GR5: the headless AI-vs-AI road (`settlement_third_party`) runs
        through the ONE transition helper, so its peace carries the floor
        too (the pre-RS-1 write sat in the player's ratifier alone)."""
        from backend.game_logic.settlement_third_party import (
            THIRD_PARTY_MIN_WAR_TURNS, process_third_party_settlements)
        w = _boot()
        with _quiet():
            D.declare_war(w, "Prussia", "Hanover")
        war_id, war = next((wid, war) for wid, war in w.war_instances.items()
                           if war.get("ended_turn") is None
                           and "Prussia" in (war.get("active_participants") or [])
                           and "Hanover" in (war.get("active_participants") or []))
        war["created_turn"] = int(w.current_turn) - THIRD_PARTY_MIN_WAR_TURNS - 1
        w.war_exhaustion["Hanover"] = 150
        key = w._make_diplo_key("Hanover", "Prussia")
        w.war_scores[key] = -95 if key.startswith("Hanover") else 95
        with _quiet():
            events = process_third_party_settlements(w)
        assert any(e["type"] == "third_party_peace" for e in events)
        assert w.get_diplomatic_state("Prussia", "Hanover") == "PEACE"
        assert w.armistice_cooldowns.get(key) == coalition.FRESH_PEACE_FLOOR_TURNS
        assert D.offensive_call_bar(w, "Hanover", "Prussia") == "fresh peace with Prussia"

    def test_a_longer_cooldown_already_there_is_kept(self):
        world = WorldState()
        world.armistice_cooldowns["Austria|France"] = 9
        written = write_settlement_peace_floors(world, [
            {"pair": "Austria|France", "current_state_before": "WAR", "final_state": "PEACE"},
            {"pair": "France|Prussia", "current_state_before": "ARMISTICE", "final_state": "PEACE"},
            {"pair": "Prussia|Saxony", "current_state_before": "WAR", "final_state": "ARMISTICE"},
            {"pair": "Austria|Saxony", "current_state_before": "PEACE", "final_state": "PEACE"},
        ])
        assert written == ["Austria|France", "France|Prussia"]
        assert world.armistice_cooldowns == {
            "Austria|France": 9, "France|Prussia": coalition.FRESH_PEACE_FLOOR_TURNS}

    def test_the_lever_down_writes_nothing(self, monkeypatch):
        from backend.game_logic import settlement_ratify as SR
        monkeypatch.setattr(SR, "THE_SETTLEMENT_WRITES_THE_PAIR_COOLDOWN", False)
        world = WorldState()
        assert write_settlement_peace_floors(world, [
            {"pair": "Austria|France", "current_state_before": "WAR", "final_state": "PEACE"}]) == []
        assert world.armistice_cooldowns == {}


# ════════════════════════════════════════════════════════════════════════
# RS-2 — a Congress war contests, not breaks, the ceder's titles
# ════════════════════════════════════════════════════════════════════════

@pytest.fixture
def ceded_vienna():
    """Austria at peace, the five provinces ceded by TREATY, the Congress
    sitting (the titles staged from the minors)."""
    w = _boot()
    _austria_out_of_the_war(w)
    for region in THE_FIVE:
        _hold(w, region, "France", "Austria", kind=game_end.TITLE_TREATY)
    w.congress = None  # the white peace above latched nothing to keep here
    _sit(w)
    assert all(w.province_title[r]["kind"] == game_end.TITLE_TREATY for r in THE_FIVE)
    return w


def _austria_out_of_the_war(w):
    """Austria signs with France and with Bavaria, the one attacker it still
    fights after France's clients follow their lord: it EXITS the boot war
    instance (`exited_turn`, `separate_peace`), so a later declaration by
    Austria opens a new war instead of colliding with the old one's sides."""
    _ratify(w, "Austria", "France")
    _ratify(w, "Austria", "Bavaria")
    assert w.war_instances["war_1"]["participant_meta"]["Austria"]["exited_turn"] is not None
    assert w.get_diplomatic_state("Austria", "France") == "PEACE"


class TestAWarWhileTheCongressSitsContests:

    def test_the_ceders_own_declaration_contests_and_the_count_holds(self, ceded_vienna):
        w = ceded_vienna
        before = congress.titled(w)["count"]
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        result = _declare(w, "Austria", "France")
        assert result["success"]
        for region in THE_FIVE:
            rec = w.province_title[region]
            assert rec["kind"] == game_end.TITLE_TREATY
            assert rec["contested"] == {"by": "Austria", "turn": w.current_turn}
        assert congress.titled(w)["count"] == before
        assert game_end.contested_titles(w) == {"Austria": sorted(THE_FIVE)}
        event = _events(w, "contested", "Austria")
        assert len(event) == 1 and event[0]["regions"] == sorted(THE_FIVE)
        titled = next(c for c in congress.hold_conditions(w) if c["key"] == "titled")
        assert titled["met"]
        assert "Austria's war contests what it ceded (Bohemia, Carniola, Moravia …) — counted while the Congress sits" in titled["text"]

    def test_the_leagues_declaration_contests_too(self, ceded_vienna):
        """The retest's road: the coalition declares for Austria."""
        w = ceded_vienna
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        w.current_turn += coalition.FRESH_PEACE_FLOOR_TURNS
        with _quiet():
            result = coalition.form_coalition(["Austria"], w)
        assert result.get("success"), result
        assert w.get_diplomatic_state("Austria", "France") == "WAR"
        assert all(w.province_title[r]["kind"] == game_end.TITLE_TREATY for r in THE_FIVE)
        assert game_end.contested_titles(w) == {"Austria": sorted(THE_FIVE)}

    def test_the_emperors_own_sword_still_breaks(self, ceded_vienna):
        w = ceded_vienna
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        w.diplomatic_points = 9
        result = _declare(w, "France", "Austria")
        assert result["success"], result
        for region in THE_FIVE:
            rec = w.province_title[region]
            assert rec["kind"] == game_end.TITLE_CONQUEST
            assert rec["reopened_by"] == "Austria" and "contested" not in rec
        assert game_end.contested_titles(w) == {}

    @pytest.mark.parametrize("a, b, reason, drew", [
        ("France", "Austria", "war_declaration", True),
        ("Austria", "France", "war_declaration", False),
        ("France", "Austria", "offensive_cascade", True),
        ("Austria", "France", "offensive_cascade", False),
        ("France", "Austria", "defensive_cascade", False),
        ("Austria", "France", "defensive_cascade", True),
        ("Austria", "France", "treaty_break", True),
        ("Austria", "France", "", True),
        ("Austria", "Prussia", "war_declaration", True),
    ])
    def test_who_drew_the_sword_reads_the_setters_own_argument_order(self, a, b, reason, drew):
        w = _boot()
        assert game_end.player_drew_the_sword(w, a, b, reason) is drew

    def test_joining_an_allys_offensive_war_breaks_and_a_defensive_join_shelters(self, ceded_vienna):
        w = ceded_vienna
        with _quiet():
            D.set_diplomatic_state(w, "France", "Austria", "WAR", "defensive_cascade")
        assert all("contested" in w.province_title[r] for r in THE_FIVE)
        w2 = _boot()
        _austria_out_of_the_war(w2)
        for region in THE_FIVE:
            _hold(w2, region, "France", "Austria", kind=game_end.TITLE_TREATY)
        w2.congress = None
        _sit(w2)
        with _quiet():
            D.set_diplomatic_state(w2, "France", "Austria", "WAR", "offensive_cascade")
        assert all(w2.province_title[r]["kind"] == game_end.TITLE_CONQUEST for r in THE_FIVE)

    def test_no_shelter_without_a_sitting_congress(self):
        w = _boot()
        _austria_out_of_the_war(w)
        for region in THE_FIVE:
            _hold(w, region, "France", "Austria", kind=game_end.TITLE_TREATY)
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        _declare(w, "Austria", "France")
        assert all(w.province_title[r]["kind"] == game_end.TITLE_CONQUEST for r in THE_FIVE)

    def test_the_lever_down_breaks_as_before(self, ceded_vienna, monkeypatch):
        monkeypatch.setattr(game_end, "A_CONGRESS_WAR_CONTESTS_NOT_BREAKS", False)
        w = ceded_vienna
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        _declare(w, "Austria", "France")
        assert all(w.province_title[r]["kind"] == game_end.TITLE_CONQUEST for r in THE_FIVE)
        assert not _events(w, "contested")

    def test_a_signed_peace_keeps_the_titles_and_latches_the_court(self, ceded_vienna):
        w = ceded_vienna
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        _declare(w, "Austria", "France")
        before = congress.titled(w)["count"]
        _ratify(w, "Austria", "France")
        assert w.get_diplomatic_state("Austria", "France") == "PEACE"
        for region in THE_FIVE:
            rec = w.province_title[region]
            assert rec["kind"] == game_end.TITLE_TREATY and "contested" not in rec
        assert congress.titled(w)["count"] == before
        signed = (congress.record(w) or {}).get("signed") or {}
        assert signed["Austria"]["kind"] == "table" and signed["Austria"]["broken"] is None
        assert congress.answer(w, "Austria")["stance"] == congress.RECOGNIZES

    def test_an_unsigned_end_reopens_them_and_a_truce_does_not_end_the_contest(self, ceded_vienna):
        w = ceded_vienna
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        _declare(w, "Austria", "France")
        with _quiet():
            D.set_diplomatic_state(w, "Austria", "France", "ARMISTICE", "test_truce")
        assert all("contested" in w.province_title[r] for r in THE_FIVE)
        # the per-turn lapse reads the truce as the war still on
        assert game_end.lapse_contested_titles(w) == []
        assert all("contested" in w.province_title[r] for r in THE_FIVE)
        # the truce runs out into peace: the unsigned end
        with _quiet():
            D.set_diplomatic_state(w, "Austria", "France", "PEACE", "armistice_expired_peace")
        for region in THE_FIVE:
            rec = w.province_title[region]
            assert rec["kind"] == game_end.TITLE_CONQUEST
            assert rec["reopened_by"] == "Austria" and rec["since"] == w.current_turn
            assert "contested" not in rec

    def test_the_sitting_ending_with_the_war_still_on_reopens_them(self, ceded_vienna):
        w = ceded_vienna
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        _declare(w, "Austria", "France")
        assert game_end.lapse_contested_titles(w) == []
        w.congress["status"] = congress.DISSOLVED
        w.congress["dissolved_turn"] = w.current_turn
        with _quiet():
            game_end.reconcile_province_titles(w)
        for region in THE_FIVE:
            assert w.province_title[region]["kind"] == game_end.TITLE_CONQUEST
        assert game_end.contested_titles(w) == {}

    def test_a_province_actually_lost_still_breaks_the_hold(self, ceded_vienna):
        w = ceded_vienna
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        _declare(w, "Austria", "France")
        with _quiet():
            assert w.capture_region("Tyrol", "Austria")
        assert "Tyrol" in w.congress["lost"]
        assert w.province_title.get("Tyrol") is None or w.province_title["Tyrol"].get("holder") != "France"
        lost = next(c for c in congress.hold_conditions(w) if c["key"] == "lost")
        assert not lost["met"]
        # SF-END-1: a count that fell short names the LOSS, never the
        # contest that still counts (the played sitting's dissolution had
        # read "… contests what it ceded — counted while the Congress sits").
        titled = next(c for c in congress.hold_conditions(w) if c["key"] == "titled")
        assert not titled["met"]
        assert titled["text"].endswith(" — Tyrol taken by force")
        assert "contests" not in titled["text"]
        from backend.campaign_log import congress_dissolve_reason
        assert congress_dissolve_reason("titled", titled["text"]).endswith("— Tyrol taken by force")
        # the fall is read at the tick, and the cooldown line carries its cause
        _tick(w)
        assert w.congress["status"] == congress.DISSOLVED
        line = congress.state_line(w)
        assert line.startswith(f"THE CONGRESS OF PARIS — dissolved on turn {w.congress['dissolved_turn']} — "
                               "the titled provinces fell short (")
        assert "— Tyrol taken by force; it may be summoned again on turn" in line

    def test_the_contest_round_trips(self, ceded_vienna):
        w = ceded_vienna
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        _declare(w, "Austria", "France")
        with _quiet():
            again = WorldState.from_dict(w.to_dict())
        assert game_end.contested_titles(again) == {"Austria": sorted(THE_FIVE)}
        assert congress.titled(again)["count"] == congress.titled(w)["count"]

    def test_the_log_and_the_dispatch_carry_the_contest(self, ceded_vienna):
        from backend.campaign_log import format_event_oneliner
        w = ceded_vienna
        w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "France"), None)
        _declare(w, "Austria", "France")
        event = _events(w, "contested", "Austria")[0]
        line = format_event_oneliner(event, "France")
        assert line.startswith("Austria's war contests what it ceded (Bohemia, Carniola, Moravia …) — counted while the Congress sits")
        got = []

        def _add(cls, identity="", **fields):
            got.append((cls, identity, fields))

        dispatch._congress_candidate(w, event, _add)
        assert got and got[0][0] == "congress_contested"
        assert got[0][1] == f"congress_contested:Austria:{w.current_turn}"
        assert "contests what it ceded" in got[0][2]["line"]
        assert dispatch.HEADLINE_WEIGHTS["congress_contested"] == dispatch.HEADLINE_WEIGHTS["congress_war"] - 1


class TestTheTurn24ReplayHolds:

    def test_forty_seven_holds_through_the_leagues_war(self):
        """The retest's own save, played through the fixed sitting: the
        league marches Austria, its war CONTESTS the five titles, and the
        count never falls under the hold while the Congress sits (it read
        47 → 41 and dissolved on turn 28 before Step 1)."""
        from backend.game_logic.turn_manager import TurnManager
        save = json.loads(T24.read_text(encoding="utf-8"))
        with _quiet():
            w = WorldState.from_dict(save["world_state"])
        assert congress.titled(w)["count"] == 47
        with _quiet():
            assert congress.summon(w)["success"]
        tm = TurnManager(w)
        rows = []
        with _quiet():
            for _ in range(8):
                tm.end_turn()
                rows.append((w.current_turn, congress.titled(w)["count"],
                             w.get_diplomatic_state("Austria", "France"),
                             sorted(game_end.contested_titles(w).get("Austria", [])),
                             (w.congress or {}).get("status")))
                if (w.congress or {}).get("status") != congress.SITTING:
                    break
        assert all(count >= 45 for _t, count, _s, _c, _st in rows), rows
        war_turns = [r for r in rows if r[2] == "WAR"]
        assert war_turns, rows
        assert all(r[3] for r in war_turns), rows
        dissolved = [r for r in rows if r[4] == congress.DISSOLVED]
        if dissolved:
            reason = str((w.congress or {}).get("dissolve_reason") or "")
            assert "titled" not in reason, reason


# ════════════════════════════════════════════════════════════════════════
# RS-10 — the gate warns about the league the summons makes possible
# ════════════════════════════════════════════════════════════════════════

class TestTheSummonsNamesTheLoweredGate:

    def _summonable(self):
        w = _boot()
        for court in ("Austria", "Britain", "Russia"):
            _ratify(w, court, "France")
        w.congress = None
        _stage_titles(w)
        w.diplomatic_points = 6
        assert congress.state_line(w) and "may be summoned" in congress.state_line(w)
        return w

    def test_the_gate_line_warns_and_names_the_courts(self):
        w = self._summonable()
        refusers = sorted(c for c in congress.great_powers(w)
                          if congress.answer(w, c)["stance"] == congress.REFUSES)
        assert len(refusers) >= 2
        line = congress.state_line(w)
        gate = w.campaign_end["congress_alarm_gate"]
        alarm = int(w.threat_by_target.get("France", 0) or 0)
        assert (f" · the summons lowers the league's gate to {gate} while two great "
                f"powers refuse (Europe's alarm stands at {alarm}): ") in line
        assert "would gather against us" in line
        assert all(c in line for c in refusers)
        tail = "it would brew at once" if alarm >= gate else f"once the alarm reaches {gate}"
        assert line.endswith(tail)

    def test_the_summons_says_it_too(self):
        w = self._summonable()
        with _quiet():
            result = congress.summon(w)
        assert result["success"]
        assert "The summons lowers the league's gate to" in result["message"]
        assert "would gather against us" in result["message"]

    def test_a_brewing_league_names_when_it_declares(self):
        w = self._summonable()
        w.coalition_brewing = {"qualifying_nations": ["Austria", "Russia"],
                               "turns_remaining": 2, "started_turn": w.current_turn,
                               "threat_at_start": 60}
        assert congress.league_warning(w).endswith(
            " — a league already brews; it declares in 2 turns")

    def test_the_lever_down_and_the_lone_refuser_are_silent(self, monkeypatch):
        w = self._summonable()
        assert congress.league_warning(w)
        monkeypatch.setattr(congress, "THE_SUMMONS_NAMES_THE_LOWERED_GATE", False)
        assert congress.league_warning(w) == ""
        assert " · the summons" not in congress.state_line(w)
        monkeypatch.setattr(congress, "THE_SUMMONS_NAMES_THE_LOWERED_GATE", True)
        for court in ("Austria", "Russia", "Britain"):
            congress.note_ratification(w, [court], True, beaten=[court])
        assert congress.league_warning(w) == ""

    def test_the_march_blocker_reads_the_brewing_league(self, monkeypatch):
        w = self._summonable()
        _sit(w)
        w.active_coalition = None
        stock = congress.march_blocker(w, "Prussia")
        assert stock.startswith("no coalition stands against us to join — a league gathers only at alarm")
        w.coalition_brewing = {"qualifying_nations": ["Austria", "Russia"],
                               "turns_remaining": 3, "started_turn": w.current_turn,
                               "threat_at_start": 60}
        line = congress.march_blocker(w, "Prussia")
        assert line == (f"no coalition stands against us yet — a league brews and "
                        f"declares in 3 turns (alarm {int(w.threat_by_target.get('France', 0) or 0)} "
                        f"against a gate of {coalition.brewing_gate(w)})")
        monkeypatch.setattr(congress, "THE_SUMMONS_NAMES_THE_LOWERED_GATE", False)
        assert congress.march_blocker(w, "Prussia") == stock


# ════════════════════════════════════════════════════════════════════════
# RS-16 — the alarm line is one forecast of the tick
# ════════════════════════════════════════════════════════════════════════

class TestTheAlarmLineIsAForecast:

    @pytest.mark.parametrize("board", ["boot", "t24"])
    def test_the_forecast_is_the_tick(self, board):
        if board == "boot":
            w = _boot()
        else:
            save = json.loads(T24.read_text(encoding="utf-8"))
            with _quiet():
                w = WorldState.from_dict(save["world_state"])
        fc = coalition.forecast_alarm_tick(w)
        assert fc["now"] == int(w.threat_by_target.get("France", 0) or 0)
        assert fc["net"] == fc["next"] - fc["now"]
        with _quiet():
            coalition.process_coalition_turn(w)
        assert int(w.threat_by_target.get("France", 0) or 0) == fc["next"], fc

    def test_the_t24_board_rises_and_the_line_says_so(self):
        save = json.loads(T24.read_text(encoding="utf-8"))
        with _quiet():
            w = WorldState.from_dict(save["world_state"])
        fc = coalition.forecast_alarm_tick(w)
        assert fc["net"] == 1 and fc["decay"] == 3
        assert ("our bloc's weight in Europe", 3) in fc["gains"]
        road = congress.alarm_road(w)
        assert road.startswith("rising 1 a turn: our bloc's weight in Europe +3, ")
        assert "against 3 of decay (one, plus one for each court at peace with us, at most three)" in road
        assert road.endswith("; a treaty that dissolves a league halves it")

    def test_the_boot_board_falls_and_the_line_says_so(self):
        w = _boot()
        fc = coalition.forecast_alarm_tick(w)
        assert fc["net"] < 0
        assert congress.alarm_road(w).startswith(f"falling {-fc['net']} a turn: ")

    def test_holding_and_the_cap(self):
        w = _boot()
        w.threat_by_target["France"] = 100
        fc = coalition.forecast_alarm_tick(w)
        assert fc["capped"] and fc["next"] == 100 - fc["decay"]
        assert "the alarm cannot rise past 100" in congress.alarm_road(w)

    def test_the_lever_down_is_the_old_gross_decay_line(self, monkeypatch):
        monkeypatch.setattr(congress, "THE_ALARM_LINE_IS_A_FORECAST", False)
        w = _boot()
        decay = coalition._calculate_threat_decay(w)
        assert congress.alarm_road(w).startswith(f"it falls {decay} a turn (one, plus one")


# ════════════════════════════════════════════════════════════════════════
# SF-V1 — no AI treaty offer the table refuses
# ════════════════════════════════════════════════════════════════════════

class TestNoOfferTheTableRefuses:

    def _sweden(self, relation):
        w = _boot()
        key = w._make_diplo_key("Sweden", "France")
        assert w.get_diplomatic_state("Sweden", "France") == "PEACE"
        w.nation_relations[key] = relation
        return w

    def test_the_refusal_reads_the_ratifiers_own_guards(self):
        w = self._sweden(-60)
        assert ai_diplomacy.treaty_offer_refusal(w, "Sweden", "defensive_alliance") == (
            "relations -60 are below the 20 a DEFENSIVE_ALLIANCE needs")
        assert ai_diplomacy.treaty_offer_refusal(w, "Sweden", "open_borders") == (
            "relations -60 are below the -20 a OPEN_BORDERS needs")
        assert ai_diplomacy.treaty_offer_refusal(w, "Sweden", "peace") == ""
        w.nation_relations[w._make_diplo_key("Sweden", "France")] = -10
        assert ai_diplomacy.treaty_offer_refusal(w, "Sweden", "open_borders") == ""
        w.nation_relations[w._make_diplo_key("Sweden", "France")] = 25
        assert ai_diplomacy.treaty_offer_refusal(w, "Sweden", "defensive_alliance") == ""
        w.diplomatic_states[w._make_diplo_key("Sweden", "France")] = "ALLIANCE"
        w.invalidate_active_nations_cache()
        assert ai_diplomacy.treaty_offer_refusal(w, "Sweden", "defensive_alliance") == (
            "already at ALLIANCE — DEFENSIVE_ALLIANCE would be no upgrade")

    def test_the_best_pact_walks_the_ladder(self):
        w = self._sweden(12)
        assert ai_diplomacy.best_ratifiable_treaty(w, "Sweden", "defensive_alliance") == "non_aggression"
        w.nation_relations[w._make_diplo_key("Sweden", "France")] = -10
        assert ai_diplomacy.best_ratifiable_treaty(w, "Sweden", "alliance") == "open_borders"
        w.nation_relations[w._make_diplo_key("Sweden", "France")] = -60
        assert ai_diplomacy.best_ratifiable_treaty(w, "Sweden", "defensive_alliance") is None
        assert ai_diplomacy.best_ratifiable_treaty(w, "Sweden", "friendly_gift") == "friendly_gift"

    def test_the_transport_withholds_the_letter_the_table_refuses(self):
        w = self._sweden(-60)
        terms = ai_diplomacy._build_proposal_terms("Sweden", "defensive_alliance", 0, w)
        proposal = ai_diplomacy._make_proposal("Sweden", "defensive_alliance", 9, terms, w)
        with _quiet():
            assert ai_diplomacy.deliver_ai_proposal(proposal, w) is None
        assert w.pending_diplomatic_dialogue is None
        w.nation_relations[w._make_diplo_key("Sweden", "France")] = 25
        with _quiet():
            delivered = ai_diplomacy.deliver_ai_proposal(proposal, w)
        assert delivered and w.pending_diplomatic_dialogue is not None

    def test_the_lever_down_sends_the_letter_the_ratifier_then_refuses(self, monkeypatch):
        monkeypatch.setattr(ai_diplomacy, "NO_OFFER_THE_TABLE_REFUSES", False)
        w = self._sweden(-60)
        terms = ai_diplomacy._build_proposal_terms("Sweden", "defensive_alliance", 0, w)
        proposal = ai_diplomacy._make_proposal("Sweden", "defensive_alliance", 9, terms, w)
        with _quiet():
            assert ai_diplomacy.deliver_ai_proposal(proposal, w)
        assert w.pending_diplomatic_dialogue is not None
        result = _ratify(w, "Sweden", "France", ptype="defensive_alliance")
        assert result["type"] == "diplomatic_treaty_failed"

    def test_the_auction_offers_the_best_pact_the_relation_permits(self, monkeypatch):
        from backend.game_logic import intent as I

        def bandwagon(nation, world):
            real = I.get_nation_intent.__wrapped__ if hasattr(I.get_nation_intent, "__wrapped__") else None
            return I.IntentView(nation=nation, want_id="x", want_title="x", want_type="align",
                                against=None, weight=50, price="bandwagon", survival=False)

        monkeypatch.setattr(I, "get_nation_intent", bandwagon)
        w = self._sweden(12)
        # nobody outbids France
        for other in w.get_active_nations():
            if other not in ("Sweden", "France"):
                w.nation_relations[w._make_diplo_key("Sweden", other)] = -80
        w.allegiance_auctions = {"Sweden": {"opened_turn": w.current_turn - 3,
                                            "resolves_turn": w.current_turn}}
        with _quiet():
            events = ai_diplomacy.process_allegiance_auctions(w)
        resolved = next(e for e in events if e["type"] == "allegiance_auction_resolved")
        assert resolved["winner"] == "France" and resolved["outcome"] == "player_offer"
        dialogue = w.pending_diplomatic_dialogue
        assert dialogue is not None
        assert (dialogue.get("context") or {}).get("proposal_type") == "non_aggression"

    def test_the_auction_below_every_floor_wins_no_pact(self, monkeypatch):
        from backend.game_logic import intent as I
        monkeypatch.setattr(I, "get_nation_intent", lambda nation, world: I.IntentView(
            nation=nation, want_id="x", want_title="x", want_type="align",
            against=None, weight=50, price="bandwagon", survival=False))
        w = self._sweden(-60)
        for other in w.get_active_nations():
            if other not in ("Sweden", "France"):
                w.nation_relations[w._make_diplo_key("Sweden", other)] = -80
        w.allegiance_auctions = {"Sweden": {"opened_turn": w.current_turn - 3,
                                            "resolves_turn": w.current_turn}}
        with _quiet():
            events = ai_diplomacy.process_allegiance_auctions(w)
        resolved = next(e for e in events if e["type"] == "allegiance_auction_resolved")
        assert resolved["winner"] == "France" and resolved["outcome"] == "player_won_no_pact"
        assert w.pending_diplomatic_dialogue is None

    def test_the_refusal_copy_names_the_treaty_and_the_floor(self):
        w = self._sweden(-60)
        result = _ratify(w, "Sweden", "France", ptype="defensive_alliance")
        assert result["type"] == "diplomatic_treaty_failed"
        assert result["message"] == "Relations with Sweden stand at -60; a Defensive Alliance needs 20."


# ════════════════════════════════════════════════════════════════════════
# SF-V5 — no whole-war letter the table refuses
# ════════════════════════════════════════════════════════════════════════

class TestTheLetterCoversOnlyThePairsAtWar:

    def _truce(self, w, court):
        for member in ("France", "Spain", "Holland", "Bavaria", "KingdomOfItaly"):
            key = w._make_diplo_key(member, court)
            if w.diplomatic_states.get(key) == "WAR":
                w.diplomatic_states[key] = "ARMISTICE"
        w.invalidate_active_nations_cache()

    def test_a_court_in_a_truce_is_not_covered(self):
        w = _boot()
        war = w.war_instances["war_1"]
        assert ai_diplomacy._covered_at_war(w, war, player="France") == ["Britain", "Austria", "Russia"]
        self._truce(w, "Russia")
        assert ai_diplomacy._covered_at_war(w, war, player="France") == ["Britain", "Austria"]

    def test_the_emitter_drops_the_truce_court_and_the_leader_in_a_truce_hands_the_pen_on(self, monkeypatch):
        monkeypatch.setattr(ai_diplomacy, "_letter_would_carry", lambda *a, **k: True)
        w = _boot()
        war = w.war_instances["war_1"]
        self._truce(w, "Russia")
        with _quiet():
            offer = ai_diplomacy._emit_settlement_offer_for_war(
                w, "war_1", war, player="France", current_turn=w.current_turn,
                pending=[], cooldowns={})
        assert offer is not None
        assert sorted(offer["covered_enemy_participants"]) == ["Austria", "Britain"]
        # the leader itself in a truce: the senior covered court writes it
        self._truce(w, "Britain")
        with _quiet():
            offer = ai_diplomacy._emit_settlement_offer_for_war(
                w, "war_1", war, player="France", current_turn=w.current_turn,
                pending=[], cooldowns={})
        assert offer["covered_enemy_participants"] == ["Austria"]
        assert offer["proposer_nation"] == "Austria"

    def test_no_covered_court_at_war_refuses_the_war_and_writes_nothing(self, monkeypatch):
        monkeypatch.setattr(ai_diplomacy, "_letter_would_carry", lambda *a, **k: True)
        w = _boot()
        war = w.war_instances["war_1"]
        for court in ("Britain", "Austria", "Russia"):
            self._truce(w, court)
        assert ai_diplomacy._settlement_offer_eligible_for_war(
            w, war, player="France", current_turn=w.current_turn) == "no_covered_enemy_at_war"
        cooldowns = {}
        with _quiet():
            assert ai_diplomacy._emit_settlement_offer_for_war(
                w, "war_1", war, player="France", current_turn=w.current_turn,
                pending=[], cooldowns=cooldowns) is None
        assert cooldowns == {}

    def test_the_lever_down_covers_the_truce_court_again(self, monkeypatch):
        monkeypatch.setattr(ai_diplomacy, "THE_LETTER_COVERS_ONLY_THE_PAIRS_AT_WAR", False)
        monkeypatch.setattr(ai_diplomacy, "_letter_would_carry", lambda *a, **k: True)
        w = _boot()
        war = w.war_instances["war_1"]
        self._truce(w, "Russia")
        with _quiet():
            offer = ai_diplomacy._emit_settlement_offer_for_war(
                w, "war_1", war, player="France", current_turn=w.current_turn,
                pending=[], cooldowns={})
        assert sorted(offer["covered_enemy_participants"]) == ["Austria", "Britain", "Russia"]


class TestTheLetterIsReadAtTheAnswer:
    """SF-V5's second seam: the board moves under a letter inside the same
    phase (the OP arm's turn 10 — Russia's truce, answered the same enemy
    phase the letter arrived). The accept drops the truce court from the
    coverage and says so; the review then has no unscoreable row."""

    def _letter(self, w):
        from backend.game_logic.settlement_offers import promote_pending_settlement_offers
        war = w.war_instances["war_1"]
        w.pending_settlement_dialogues = []
        with _quiet():
            offer = ai_diplomacy._emit_settlement_offer_for_war(
                w, "war_1", war, player="France", current_turn=w.current_turn,
                pending=w.pending_settlement_dialogues, cooldowns={})
        assert offer is not None
        assert sorted(offer["covered_enemy_participants"]) == ["Austria", "Britain", "Russia"]
        with _quiet():
            promoted = promote_pending_settlement_offers(w)
        return promoted[0]

    def _truce(self, w, court):
        for member in ("France", "Spain", "Holland", "Bavaria", "KingdomOfItaly"):
            key = w._make_diplo_key(member, court)
            if w.diplomatic_states.get(key) == "WAR":
                w.diplomatic_states[key] = "ARMISTICE"
        w.invalidate_active_nations_cache()

    def test_a_truce_signed_after_the_letter_is_dropped_at_the_answer(self, monkeypatch):
        from backend.game_logic.settlement_offers import handle_incoming_settlement_offer_action
        monkeypatch.setattr(ai_diplomacy, "_letter_would_carry", lambda *a, **k: True)
        w = _boot()
        letter = self._letter(w)
        self._truce(w, "Russia")
        with _quiet():
            result = handle_incoming_settlement_offer_action(
                w, action="accept_settlement_offer", dialogue=letter)
        assert result["success"], result
        assert result["departed_courts"] == ["Russia"]
        assert result["departed_courts_note"].startswith("Russia stands in a truce with us")
        staged = result["diplomatic_dialogue"]
        assert sorted(staged["covered_enemy_participants"]) == ["Austria", "Britain"]
        assert not any("no_direct_war_score" in str(h) for h in (staged.get("hard_stops") or []))

    def test_the_lever_down_keeps_the_truce_court_and_hard_stops(self, monkeypatch):
        from backend.game_logic.settlement_offers import handle_incoming_settlement_offer_action
        monkeypatch.setattr(ai_diplomacy, "_letter_would_carry", lambda *a, **k: True)
        monkeypatch.setattr(ai_diplomacy, "THE_LETTER_COVERS_ONLY_THE_PAIRS_AT_WAR", False)
        w = _boot()
        letter = self._letter(w)
        self._truce(w, "Russia")
        with _quiet():
            result = handle_incoming_settlement_offer_action(
                w, action="accept_settlement_offer", dialogue=letter)
        staged = result.get("diplomatic_dialogue") or {}
        assert "Russia" in (staged.get("covered_enemy_participants") or [])
        assert not result.get("departed_courts")


class TestTheLetterIsRatifiableWhenSent:

    def test_the_dry_run_reads_the_per_court_table_with_consent(self, monkeypatch):
        from backend.game_logic import settlement_baseline as SB
        seen = {}

        def table(world, **kwargs):
            seen.update(kwargs)
            return {"overall_acceptance": {"carries": False}}

        monkeypatch.setattr(SB, "compute_per_court_acceptance", table)
        w = _boot()
        war = w.war_instances["war_1"]
        assert ai_diplomacy._letter_would_carry(
            w, "war_1", war, player="France", covered=["Britain", "Austria"],
            terms=[{"type": "peace"}]) is False
        assert seen["consenting_courts"] == ["Britain", "Austria"]
        assert seen["covered_enemy_participants"] == ["Britain", "Austria"]
        assert seen["proposer_side"] == "attackers" and seen["accepting_side"] == "defenders"
        monkeypatch.setattr(SB, "compute_per_court_acceptance",
                            lambda world, **kw: {"overall_acceptance": {"carries": True}})
        assert ai_diplomacy._letter_would_carry(
            w, "war_1", war, player="France", covered=["Britain"], terms=[]) is True

    def test_a_letter_that_would_not_carry_is_withheld_and_spends_no_cooldown(self, monkeypatch):
        monkeypatch.setattr(ai_diplomacy, "_letter_would_carry", lambda *a, **k: False)
        w = _boot()
        war = w.war_instances["war_1"]
        pending, cooldowns = [], {}
        with _quiet():
            assert ai_diplomacy._emit_settlement_offer_for_war(
                w, "war_1", war, player="France", current_turn=w.current_turn,
                pending=pending, cooldowns=cooldowns) is None
        assert pending == [] and cooldowns == {}

    def test_the_lever_down_sends_it_anyway(self, monkeypatch):
        monkeypatch.setattr(ai_diplomacy, "THE_LETTER_IS_RATIFIABLE_WHEN_SENT", False)
        monkeypatch.setattr(ai_diplomacy, "_letter_would_carry", lambda *a, **k: False)
        w = _boot()
        war = w.war_instances["war_1"]
        pending, cooldowns = [], {}
        with _quiet():
            offer = ai_diplomacy._emit_settlement_offer_for_war(
                w, "war_1", war, player="France", current_turn=w.current_turn,
                pending=pending, cooldowns=cooldowns)
        assert offer is not None and pending == [offer]

    def test_the_periodic_producer_survives_a_withheld_letter(self, monkeypatch):
        monkeypatch.setattr(ai_diplomacy, "_emit_settlement_offer_for_war", lambda *a, **k: None)
        monkeypatch.setattr(ai_diplomacy, "_settlement_offer_eligible_for_war", lambda *a, **k: None)
        monkeypatch.setattr(ai_diplomacy, "league_offer_gate", lambda *a, **k: None)
        w = _boot()
        w.ai_settlement_cooldowns = {}
        with _quiet():
            assert ai_diplomacy.process_settlement_offer_phase(w) == []

    def test_a_terms_request_the_table_cannot_answer_lapses_aloud(self, monkeypatch):
        monkeypatch.setattr(ai_diplomacy, "_emit_settlement_offer_for_war", lambda *a, **k: None)
        monkeypatch.setattr(ai_diplomacy, "_settlement_offer_eligible_for_war", lambda *a, **k: None)
        monkeypatch.setattr(ai_diplomacy, "league_offer_gate", lambda *a, **k: None)
        w = _boot()
        w.settlement_terms_requests = {"war_1": {
            "status": "requested", "requested_turn": w.current_turn,
            "resolved_turn": None, "resolve_reason": "", "cooldown_until_turn": 0,
            "answering_leader": "Britain"}}
        w.ai_settlement_cooldowns = {}
        with _quiet():
            assert ai_diplomacy.process_settlement_offer_phase(w) == []
        entry = w.settlement_terms_requests["war_1"]
        assert entry["status"] == "refused" and entry["resolve_reason"] == "no_ratifiable_terms"
        assert entry["cooldown_until_turn"] == w.current_turn + ai_diplomacy.REQUEST_TERMS_COOLDOWN_TURNS
        notice = [n for n in w.notifications.get_pending()
                  if n.get("title") == "No terms from Britain"]
        assert notice and "the request lapses" in notice[0]["message"]
        logged = [e for e in w.event_log if e.get("type") == "settlement_terms_request_refused"]
        assert logged and logged[-1]["resolve_reason"] == "no_ratifiable_terms"
