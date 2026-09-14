"""IQ-2 "The Collapse Is Legible" (Sept 14, 2026) — the morning dispatch and
the defeat-imminent warning.

Measured in played 40-turn campaigns: a France reduced to one province and
then to none (Paris lost, the Emperor taken) played on while the briefing
narrated an ordinary morning — Talleyrand's "The diplomatic winds favor us.",
the soil alarm pricing each turn of occupation of the LAST province as "worth
a province to their recruiting sergeants", Berthier's "Your armies stand
ready, Sire. The initiative is ours." — and the only collapse warning the game
owned was switched off on every sandbox world.

Binding scope note, pinned throughout: legible is not terminal. Nothing here
may say the campaign ends, call it a defeat, or call France eliminated.

Every pin fails if its production line is reverted or its lever set False.
"""

import contextlib
import io
import json
from pathlib import Path

import pytest

from backend.game_logic import collapse
from backend.game_logic import dispatch as D
from backend.game_logic.turn_manager import get_defeat_imminent_state
from backend.models.intel import FULL
from backend.models.world_state import WorldState
from backend.notifications import DEFEAT_IMMINENT_WARNING

SCENARIO = str(
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json")

FORBIDDEN = ("campaign ends", "game over", "defeat", "eliminated",
             "last chance")

GENERAL_LEVERS = (
    "THE_SITUATION_NAMES_THE_EMPTY_FIELD",
    "THE_SOIL_NOTE_COUNTS_THE_FREE_CORPS",
    "TALLEYRAND_OFFERS_NO_DOWNGRADE",
    "WAR_PURPOSE_COUNTS_WHAT_IS_HELD",
    "THE_SETTLEMENT_TIER_NAMES_WHOSE_TERMS",
    "THE_LAPSED_LEAGUE_NAMES_THE_WAR",
)


def _boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCENARIO)


def _reduce(world, keep=("Paris",), to="Austria"):
    """Hand every French province except `keep` to a court at war with her."""
    for name in list(world.get_nation_regions("France")):
        if name not in keep:
            world.regions[name].controller = to
    world.invalidate_active_nations_cache()
    return world


@contextlib.contextmanager
def _lever(module, name, value):
    old = getattr(module, name)
    setattr(module, name, value)
    try:
        yield
    finally:
        setattr(module, name, old)


@contextlib.contextmanager
def _all_levers(value):
    with contextlib.ExitStack() as stack:
        stack.enter_context(_lever(collapse, "THE_COLLAPSE_IS_LEGIBLE", value))
        for name in GENERAL_LEVERS:
            stack.enter_context(_lever(D, name, value))
        yield


def _page(head) -> str:
    if not head:
        return ""
    return " ".join([head["text"], *head["sub_beats"]])


def _clean(text: str) -> bool:
    low = text.lower()
    return not any(word in low for word in FORBIDDEN)


def _put_mack_on(world, region):
    """An enemy army standing on `region`, seen by our own intel (R5-legal)."""
    mack = world.marshals["Mack"]
    mack.location = region
    intel = world.intel[region]
    intel.visibility = FULL
    intel.last_updated_turn = int(world.current_turn)
    intel.known_marshals = [{"name": "Mack", "nation": "Austria",
                             "strength": int(mack.strength)}]
    return mack


@pytest.fixture
def world():
    return _boot()


# ═══════════════════════════════════════════════════════════════════════
# A1 — the headline class
# ═══════════════════════════════════════════════════════════════════════
class TestTheCollapseLeads:
    def test_the_weight_the_template_and_the_standing_ladder(self):
        wts = D.HEADLINE_WEIGHTS
        assert wts["empire_reduced"] == 100 == wts["capital_lost"]
        assert wts["empire_reduced"] < wts["sovereign_captured"]
        assert D._HEADLINE_TEMPLATES["empire_reduced"] == "Sire — {line}"
        assert "empire_reduced" in D.STANDING_HEADLINE_CLASSES
        variants = D._STANDING_ESCALATION["empire_reduced"]
        assert len(variants) >= 2 and len(set(variants)) == len(variants)
        for text in variants:
            assert "{turns}" in text
            rendered = text.format(turns=5, line="France holds X.")
            assert _clean(rendered), rendered

    def test_one_province_leads_with_the_collapse(self, world):
        _reduce(world)
        head = D._build_headline(world, "France")
        state = collapse.get_collapse_state(world)
        assert head["class"] == "empire_reduced"
        assert head["text"] == "Sire — " + collapse.summary_line(world, state)
        assert "France holds a single province: Paris." in head["text"]
        assert _clean(_page(head))

    def test_the_lever_down_board_has_no_collapse_headline(self, world):
        _reduce(world)
        with _lever(collapse, "THE_COLLAPSE_IS_LEGIBLE", False):
            head = D._build_headline(world, "France")
        assert head is None or head["class"] != "empire_reduced"
        assert "holds a single province" not in _page(head)

    def test_a_standing_realm_has_none(self, world):
        head = D._build_headline(world, "France")
        assert head is None or head["class"] != "empire_reduced"

    def test_it_leads_a_same_turn_capital_lost(self, world):
        _reduce(world, keep=())
        world.event_log.append({
            "type": "region_captured", "region": "Paris",
            "captured_by": "Austria", "captured_from": "France",
            "turn": world.current_turn})
        head = D._build_headline(world, "France")
        assert head["class"] == "empire_reduced"
        assert "France holds no province of her own." in head["text"]
        assert any("HAS FALLEN" in b for b in head["sub_beats"]), head
        with _lever(collapse, "THE_COLLAPSE_IS_LEGIBLE", False):
            world.headline_lead_memory = {}
            assert D._build_headline(world, "France")["class"] == "capital_lost"

    def test_the_soil_alarm_folds_into_the_last_province(self, world):
        _reduce(world)
        _put_mack_on(world, "Paris")
        head = D._build_headline(world, "France")
        page = _page(head)
        assert head["class"] == "empire_reduced"
        assert "Paris. Mack stands on it. No French corps stands in his path." in head["text"]
        assert "crossed into" not in page
        assert "recruiting sergeants" not in page

    def test_lever_down_the_soil_alarm_is_back(self, world):
        _reduce(world)
        _put_mack_on(world, "Paris")
        with _lever(collapse, "THE_COLLAPSE_IS_LEGIBLE", False):
            page = _page(D._build_headline(world, "France"))
        assert "Mack has crossed into Paris" in page

    def test_the_escalation_counts_honestly_and_never_promises_an_end(self, world):
        _reduce(world)
        pages, notes = [], []
        for _ in range(4):
            world.current_turn += 1
            d = D.build_morning_dispatch(world)
            pages.append(_page(d.get("headline")))
            notes.append(d["berthier_note"])
        assert "3 turns now the Empire has stood reduced." in pages[2], pages[2]
        assert "reduced 4 turns" in pages[3], pages[3]
        for text in pages + notes:
            assert _clean(text), text
            assert "The initiative is ours" not in text


# ═══════════════════════════════════════════════════════════════════════
# A2 — the lever clause
# ═══════════════════════════════════════════════════════════════════════
class TestTheFallenProvinceLever:
    def test_silent_when_there_is_no_province_left(self, world):
        _reduce(world, keep=())
        assert D._home_captured_lever(world, "Paris", "France", {}) == ""

    def test_lever_down_it_speaks_again(self, world):
        _reduce(world, keep=())
        with _lever(collapse, "THE_COLLAPSE_IS_LEGIBLE", False):
            assert "garrison you detach" in D._home_captured_lever(
                world, "Paris", "France", {})

    def test_one_province_still_has_something_to_garrison(self, world):
        _reduce(world)
        assert "garrison you detach" in D._home_captured_lever(
            world, "Paris", "France", {})


# ═══════════════════════════════════════════════════════════════════════
# A3 — Berthier's close
# ═══════════════════════════════════════════════════════════════════════
def _note(world, headline_class=""):
    return D._pick_berthier_note(
        world, "France", D._build_marshal_status(world, "France"),
        D._build_situation(world, "France"), headline_class=headline_class)


KEEP_PARIS = ("Paris is all France holds, Sire. Keep it, and the army in "
              "the field still has a treasury behind it.")


class TestBerthierCloses:
    def test_the_collapse_rung_catches_the_hand_back(self, world):
        _reduce(world)
        assert _note(world) == KEEP_PARIS
        with _lever(collapse, "THE_COLLAPSE_IS_LEGIBLE", False):
            assert _note(world) != KEEP_PARIS

    def test_the_hand_back_through_the_built_dispatch(self, world):
        _reduce(world)
        world.headline_lead_memory = {
            "class": "empire_reduced", "identity": "empire_reduced",
            "streak": 6, "runs": {"empire_reduced": 6}}
        d = D.build_morning_dispatch(world)
        assert d["berthier_note"] == KEEP_PARIS

    def test_the_headline_class_gets_the_forces_aware_note(self, world):
        _reduce(world)
        assert _note(world, "empire_reduced") == KEEP_PARIS
        assert KEEP_PARIS != D._HEADLINE_BERTHIER_NOTES["empire_reduced"]

    def test_fallen_with_a_corps_standing(self, world):
        _reduce(world, keep=())
        assert _note(world) == (
            "France holds no province, Sire. The army in the field is the "
            "Empire now — every province it retakes pays again.")

    def test_fallen_with_no_corps_free(self, world):
        _reduce(world, keep=())
        for m in world.marshals.values():
            if m.nation == "France":
                m.strength = 0
        assert _note(world) == (
            "France holds no province and no corps stands free, Sire. What "
            "is decided now will be decided at a table.")

    def test_the_last_province_under_an_enemy_army_pays_nothing(self, world):
        _reduce(world)
        _put_mack_on(world, "Paris")
        assert "Paris" in world.get_disrupted_regions()
        note = _note(world)
        assert "while an enemy army stands on it, it pays us nothing" in note
        assert note != KEEP_PARIS

    def test_a_victory_under_collapse_is_field_scoped(self, world):
        assert _note(world, "victory_won") == D._HEADLINE_BERTHIER_NOTES["victory_won"]
        _reduce(world)
        assert _note(world, "victory_won") == (
            "The field is ours today, Sire — hold what it bought.")

    def test_the_soil_note_counts_the_free_corps(self, world):
        old = D._HEADLINE_BERTHIER_NOTES["enemy_on_our_soil"]
        assert _note(world, "enemy_on_our_soil") == old
        french = [m for m in world.marshals.values() if m.nation == "France"]
        for m in french:
            m.strength = 0
        # A prisoner under arms is not free either.
        french[0].strength = 5000
        french[0].captured_by = "Austria"
        truth = ("They are on our soil, Sire, and no corps of ours stands "
                 "free to meet them.")
        assert _note(world, "enemy_on_our_soil") == truth
        with _lever(D, "THE_SOIL_NOTE_COUNTS_THE_FREE_CORPS", False):
            assert _note(world, "enemy_on_our_soil") == old


# ═══════════════════════════════════════════════════════════════════════
# A4 — Talleyrand
# ═══════════════════════════════════════════════════════════════════════
def _quiet_all_but(world, keep=()):
    cool = {}
    for n in world.enemy_nations:
        if n in keep:
            continue
        for trig in ("acceptance_crossed", "war_score_shift",
                     "vassal_loyalty", "relation_threshold"):
            cool[f"{n}|{trig}"] = 99
    world.proactive_suggestion_cooldowns = cool


class TestTalleyrand:
    def test_the_collapse_names_the_true_cause(self, world):
        _reduce(world)
        world.proactive_suggestion_cooldowns = {}
        report = D._build_talleyrand_report(world, "France")
        acc = [o for o in report if o["trigger_type"] == "acceptance_crossed"]
        assert acc, report
        for o in acc:
            assert "no court fears France any longer" in o["message"]
            assert "winds favor us" not in o["message"]
        world.proactive_suggestion_cooldowns = {}
        with _lever(collapse, "THE_COLLAPSE_IS_LEGIBLE", False):
            report = D._build_talleyrand_report(world, "France")
        assert any("The diplomatic winds favor us." in o["message"]
                   for o in report), report

    def test_the_idle_nudge_asks_the_one_open_question(self, world):
        _reduce(world, keep=())
        world.current_turn = 6
        world.talleyrand_state = "IDLE"
        world.active_diplomatic_mission = None
        world.proposal_in_transit = None
        _quiet_all_but(world)
        report = D._build_talleyrand_report(world, "France")
        nudge = [o for o in report if o["trigger_type"] == "idle_nudge"]
        assert [o["message"] for o in nudge] == [
            "Sire, no envoy of ours is abroad while Austria holds Paris. "
            "France holds no province of her own. Shall I sound out what "
            "terms the courts would grant?"]
        _quiet_all_but(world)
        with _lever(collapse, "THE_COLLAPSE_IS_LEGIBLE", False):
            report = D._build_talleyrand_report(world, "France")
        assert any("Perhaps too quiet" in o["message"] for o in report)

    def test_an_ally_is_never_offered_a_downgrade(self, world):
        state = world.get_diplomatic_state("France", "Bavaria")
        assert state == "ALLIANCE"
        _quiet_all_but(world, keep=("Bavaria",))
        report = D._build_talleyrand_report(world, "France")
        assert not [o for o in report
                    if o["trigger_type"] == "acceptance_crossed"
                    and o["target_nation"] == "Bavaria"], report
        _quiet_all_but(world, keep=("Bavaria",))
        with _lever(D, "TALLEYRAND_OFFERS_NO_DOWNGRADE", False):
            report = D._build_talleyrand_report(world, "France")
        assert [o for o in report
                if o["trigger_type"] == "acceptance_crossed"
                and o["target_nation"] == "Bavaria"], (
            "the measured defect no longer reproduces lever-down", report)


# ═══════════════════════════════════════════════════════════════════════
# A5 — the situation block
# ═══════════════════════════════════════════════════════════════════════
class TestSituation:
    def test_an_empty_field_is_named_not_priced_at_999(self, world):
        sit = D._build_situation(world, "France")
        assert sit["no_field_army"] is False
        assert sit["collapse"] is None
        for m in world.marshals.values():
            if m.nation == "France":
                m.strength = 0
        sit = D._build_situation(world, "France")
        assert sit["no_field_army"] is True
        assert sit["strength_ratio_pct"] == 999  # kept for compatibility

    def test_the_collapse_rides_the_situation(self, world):
        _reduce(world)
        sit = D._build_situation(world, "France")
        assert sit["collapse"] == collapse.get_collapse_state(world)
        assert sit["collapse"]["tier"] == "last_province"
        json.dumps(sit["collapse"])  # Godot-safe: no objects, no floats
        assert isinstance(sit["collapse"]["standing_men"], int)

    def test_lever_down_neither_key_exists(self, world):
        with _lever(D, "THE_SITUATION_NAMES_THE_EMPTY_FIELD", False):
            sit = D._build_situation(world, "France")
        assert "no_field_army" not in sit and "collapse" not in sit


# ═══════════════════════════════════════════════════════════════════════
# A6 — the war-purpose lines
# ═══════════════════════════════════════════════════════════════════════
def _line_vs(world, nation):
    return next(row["text"] for row in D._build_war_objective_section(world, "France")
                if row["target_nation"] == nation)


def _set_score(world, opponent, score):
    from backend.game_logic.diplomacy import get_war_score_for
    key = world._make_diplo_key("France", opponent)
    world.war_scores[key] = score if key.split("|")[0] == "France" else -score
    assert get_war_score_for(world, "France", opponent) == score


class TestWarObjectives:
    def test_one_of_many_is_not_held(self, world):
        assert "[HELD]" in _line_vs(world, "Britain")
        _reduce(world)
        text = _line_vs(world, "Britain")
        assert "[HELD]" not in text
        n = len(world.war_objectives[world._make_diplo_key("France", "Britain")]
                ["France"]["target_regions"])
        assert f"[1 of {n} held]" in text
        with _lever(D, "WAR_PURPOSE_COUNTS_WHAT_IS_HELD", False):
            assert "[HELD]" in _line_vs(world, "Britain")

    def test_a_losing_score_names_whose_terms(self, world):
        _set_score(world, "Britain", -65)
        assert "Settlement: Harsh Peace — theirs to impose (-65)" in _line_vs(world, "Britain")
        with _lever(D, "THE_SETTLEMENT_TIER_NAMES_WHOSE_TERMS", False):
            assert "Settlement: Harsh Peace (-65)" in _line_vs(world, "Britain")
        _set_score(world, "Britain", 65)
        assert "Settlement: Harsh Peace (+65)" in _line_vs(world, "Britain")


# ═══════════════════════════════════════════════════════════════════════
# A7 — the lapsed league
# ═══════════════════════════════════════════════════════════════════════
def _dissolved_line(world):
    world.pending_dispatch_events = []
    D.queue_dispatch_event(world, "diplomatic_coalition_dissolved", {}, "always")
    rows = D._build_diplomatic_events_section(world, "France")
    return next(r["text"] for r in rows if r["type"] == "diplomatic_coalition_dissolved")


class TestTheLapsedLeague:
    def test_the_wars_that_go_on_are_named(self, world):
        assert sorted(world.get_nations_at_war_with("France")) == ["Austria", "Britain", "Russia"]
        assert _dissolved_line(world) == (
            "The coalition against France has dissolved — but Austria, "
            "Britain and Russia remain at war with us.")
        with _lever(D, "THE_LAPSED_LEAGUE_NAMES_THE_WAR", False):
            assert _dissolved_line(world) == "The coalition against France has dissolved."

    def test_a_france_at_peace_hears_the_plain_line(self, world):
        for key, state in list(world.diplomatic_states.items()):
            if state == "WAR" and "France" in key.split("|"):
                world.diplomatic_states[key] = "PEACE"
        w = world
        assert w.get_nations_at_war_with("France") == []
        assert _dissolved_line(w) == "The coalition against France has dissolved."


# ═══════════════════════════════════════════════════════════════════════
# A8 — the white peace
# ═══════════════════════════════════════════════════════════════════════
class TestTheWhitePeace:
    PEACE = {"type": "peace_ratified", "proposer_nation": "France",
             "target_nation": "Austria", "ratifying_nations": ["France", "Austria"],
             "war_outcome": "white_peace", "state_transition": "WAR_TO_PEACE"}

    def test_it_names_the_holding(self, world):
        _reduce(world)
        world.event_log.append(dict(self.PEACE, turn=world.current_turn))
        page = _page(D._build_headline(world, "France"))
        assert ("A white peace — the map stands as it was: France holds a "
                "single province: Paris.") in page

    def test_lever_down_the_reassurance_returns(self, world):
        _reduce(world)
        world.event_log.append(dict(self.PEACE, turn=world.current_turn))
        with _lever(collapse, "THE_COLLAPSE_IS_LEGIBLE", False):
            page = _page(D._build_headline(world, "France"))
        assert "A white peace — the map stands as it was." in page


# ═══════════════════════════════════════════════════════════════════════
# A9 — the defeat-imminent warning's sandbox arm
# ═══════════════════════════════════════════════════════════════════════
class TestTheWarning:
    def test_fallen(self, world):
        _reduce(world, keep=())
        w = get_defeat_imminent_state(world)
        assert w["severity"] == "critical"
        assert w["notification_title"] == "The Empire Without Soil"
        assert w["heading"] == "THE EMPIRE IN EXTREMIS"
        assert w["controlled_region_count"] == 0 and w["controlled_regions"] == []
        assert w["message"].endswith(collapse.CAMPAIGN_CONTINUES)
        assert "Paris is in Austria's hands." in w["message"]
        for text in (w["message"], w["notification_title"], w["heading"]):
            assert _clean(text), text

    def test_last_province(self, world):
        _reduce(world)
        w = get_defeat_imminent_state(world)
        assert w["severity"] == "warning"
        assert w["notification_title"] == "One Province Remains"
        assert w["controlled_regions"] == ["Paris"]
        assert w["living_marshals"] == collapse.get_collapse_state(world)["standing"]
        assert _clean(w["message"])

    def test_silent_for_a_standing_realm_and_lever_down(self, world):
        assert get_defeat_imminent_state(world) is None
        _reduce(world)
        with _lever(collapse, "THE_COLLAPSE_IS_LEGIBLE", False):
            assert get_defeat_imminent_state(world) is None

    def test_the_legacy_arm_is_untouched(self):
        w = WorldState(player_nation="France")
        for name, region in w.regions.items():
            region.controller = "France" if name == "Paris" else "Prussia"
        w.invalidate_active_nations_cache()
        warning = get_defeat_imminent_state(w)
        assert "campaign ends" in warning["message"]
        assert "heading" not in warning
        d = D.build_morning_dispatch(w)
        assert "heading" not in d["defeat_imminent_warning"]

    def test_the_dispatch_carries_the_heading_and_dedupes(self, world):
        _reduce(world)
        D.build_morning_dispatch(world)
        d = D.build_morning_dispatch(world)
        assert d["defeat_imminent_warning"]["heading"] == "THE EMPIRE IN EXTREMIS"
        rows = [n for n in world.notifications.get_pending()
                if n.get("type") == DEFEAT_IMMINENT_WARNING]
        assert len(rows) == 1 and rows[0]["title"] == "One Province Remains"


# ═══════════════════════════════════════════════════════════════════════
# N1 — the legacy world is byte-identical, every lever up or down
# ═══════════════════════════════════════════════════════════════════════
def _legacy_page():
    w = WorldState(player_nation="France")
    for name, region in w.regions.items():
        region.controller = "France" if name == "Paris" else "Prussia"
    w.invalidate_active_nations_cache()
    w.current_turn = 6
    D.queue_dispatch_event(w, "diplomatic_coalition_dissolved", {}, "always")
    return json.dumps(D.build_morning_dispatch(w), sort_keys=True, default=str)


def test_the_legacy_dispatch_is_byte_identical():
    with _all_levers(True):
        up = _legacy_page()
    with _all_levers(False):
        down = _legacy_page()
    assert up == down
