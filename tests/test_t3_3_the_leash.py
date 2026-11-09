"""T3-3 — the leash (`AI_INTENT_SPEC.md` §13.2 R4; `DYNAMISM_SPEC.md`
§2 Tier 3; November 8, 2026; the rules `SYSTEMS_REFERENCE.md` §195).

ONE predicate — `war_council.aim_pull_set` — widens the at-war pick
bias from the design's unmet targets to the court's WAR AIMS: the
objective record's targets and the RECAPTURE of its own lost soil join
the pull (the recall rides the aim itself; P3.7 keeps the hard recall,
structurally earlier in the ladder). `enemy_ai._agenda_covet_set`
consults it through the same per-(nation, turn) memo, so the four
ranged pick surfaces read exactly what they always read (GR5: same
rungs, new bias input, no teleports). Seam
`a_leash_pulls_the_march` (`tests/_t3_seams.py`, the recorded boards'
hold-list picking it up through `T3_SEAMS_BY_ROW`).

AI-3c (the pre-war massing) was found BUILT at Stage D during this
slice's census — `get_intent_frontier` + P7's crisis-frontier arm,
pinned in `test_ai_intent_war_decision.py::TestAI3cFrontier` (massing
ground, release-with-the-crisis, deckless-empty) — so §13.1's Q1
closed THEN; the records carry the dated correction and this file
adds only the no-crisis default, never a duplicate.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic.agendas import get_agenda_military_targets  # noqa: E402
from backend.game_logic.war_council import (  # noqa: E402
    aim_pull_set,
    get_intent_frontier,
)
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
T3_3_DOWN = T3_SEAMS_BY_ROW["T3-3"]


@pytest.fixture()
def world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed="historical")


def _fresh_eyes(world) -> None:
    world._agenda_cache = None
    world.invalidate_active_nations_cache()


class TestThePull:
    def test_peace_reads_the_design_alone(self, world):
        # Prussia at peace: the pull IS today's covet read, byte for
        # byte — the leash never touches a court below war.
        assert aim_pull_set(world, "Prussia") \
            == frozenset(get_agenda_military_targets("Prussia", world))

    def test_the_boot_pull_is_the_outstanding_aim(self, world):
        # Austria at war: the defense records' own soil is HELD, so the
        # pull is exactly the Italian design — no Vienna, no Bohemia
        # (held aims never pull), and no Paris: the capital default
        # PERMITS the storm, it never steers the march (with the seat
        # in the pull Austria marched across France instead of for
        # Italy — the conduct extension's own catch).
        assert aim_pull_set(world, "Austria") \
            == frozenset({"Milan", "Piedmont", "Savoy"})

    def test_the_capital_default_is_a_per_pair_permission(self, world):
        # Bavaria fights Austria inside France's 1805 war, whose other
        # side Britain leads: her pull is her design alone (the Tyrol),
        # and the conduct rule lets her storm VIENNA — the enemy's own
        # seat — while Bohemia, no aim and no seat, stays closed.
        from backend.game_logic.war_council import annexation_permitted
        assert aim_pull_set(world, "Bavaria") == frozenset({"Tyrol"})
        assert annexation_permitted(world, "Bavaria", "Vienna")
        assert not annexation_permitted(world, "Bavaria", "Bohemia")

    def test_an_objective_target_joins_the_pull_at_war(self, world):
        key = world._make_diplo_key("Austria", "France")
        world.war_objectives.setdefault(key, {})["Austria"] = {
            "target_regions": ["Flanders"]}
        assert "Flanders" in aim_pull_set(world, "Austria")

    def test_the_recapture_pull(self, world):
        # A lost home province (not the capital) joins the pull the
        # moment it falls, and leaves it the moment it is retaken —
        # the recall riding the aim itself.
        world.regions["Tyrol"].controller = "Bavaria"
        _fresh_eyes(world)
        assert "Tyrol" in aim_pull_set(world, "Austria")
        world.regions["Tyrol"].controller = "Austria"
        _fresh_eyes(world)
        assert "Tyrol" not in aim_pull_set(world, "Austria")

    def test_a_fallen_capital_is_the_whole_pull(self, world):
        # The probe's own story: the capital's loss trips the survival
        # override — the ambitions empty, and the pull is the road home
        # alone. The leash and the survival law agree.
        world.regions["Vienna"].controller = "France"
        _fresh_eyes(world)
        assert aim_pull_set(world, "Austria") == frozenset({"Vienna"})

    def test_a_war_without_a_record_binds_nothing(self):
        # The legacy rollback world carries no war records (its wars
        # are diplomatic states alone): the conduct rule has no aim to
        # read there, and the court fights as it always did — the
        # extension's own catch (the first cut froze the AI outright).
        from backend.game_logic.war_council import annexation_permitted
        from backend.models.world_state import WorldState
        legacy = WorldState(player_nation="France")
        assert not (legacy.war_instances or {})
        enemy_soil = next(
            (name for name, region in legacy.regions.items()
             if region.controller == "France"), None)
        assert enemy_soil
        for nation in legacy.get_active_nations():
            if nation != "France":
                assert annexation_permitted(legacy, nation, enemy_soil)

    def test_the_seam_down_restores_the_design_read(self, world,
                                                    monkeypatch):
        key = world._make_diplo_key("Austria", "France")
        world.war_objectives.setdefault(key, {})["Austria"] = {
            "target_regions": ["Flanders"]}
        hold_down(monkeypatch, T3_3_DOWN)
        assert aim_pull_set(world, "Austria") \
            == frozenset(get_agenda_military_targets("Austria", world))


class TestTheConsult:
    def _ai(self):
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        return EnemyAI(CommandExecutor())

    def test_the_covet_memo_consults_the_pull(self, world):
        key = world._make_diplo_key("Austria", "France")
        world.war_objectives.setdefault(key, {})["Austria"] = {
            "target_regions": ["Flanders"]}
        ai = self._ai()
        assert ai._agenda_covet_set("Austria", world) \
            == aim_pull_set(world, "Austria")

    def test_the_memo_refreshes_per_turn(self, world):
        ai = self._ai()
        before = ai._agenda_covet_set("Austria", world)
        key = world._make_diplo_key("Austria", "France")
        world.war_objectives.setdefault(key, {})["Austria"] = {
            "target_regions": ["Flanders"]}
        # Same turn: the memo stands (GR8's documented staleness).
        assert ai._agenda_covet_set("Austria", world) == before
        world.current_turn += 1
        assert "Flanders" in ai._agenda_covet_set("Austria", world)

    def test_the_biased_distance_credits_an_objective_target(self, world):
        from backend.game_logic.agendas import AGENDA_TARGET_DISTANCE_BONUS
        key = world._make_diplo_key("Austria", "France")
        world.war_objectives.setdefault(key, {})["Austria"] = {
            "target_regions": ["Flanders"]}
        ai = self._ai()
        raw = world.get_distance("Vienna", "Flanders")
        assert ai._agenda_biased_distance("Vienna", "Flanders",
                                          "Austria", world) \
            == raw - AGENDA_TARGET_DISTANCE_BONUS

    def test_the_strategic_sort_lists_a_pull_region_first(self, world):
        key = world._make_diplo_key("Austria", "France")
        world.war_objectives.setdefault(key, {})["Austria"] = {
            "target_regions": ["Flanders"]}
        ai = self._ai()
        regions = ai._get_strategic_enemy_regions("Austria", world)
        assert regions, "France's soil stands in reach"
        if "Flanders" in regions:
            pulled = [r for r in regions
                      if r in aim_pull_set(world, "Austria")]
            assert regions[0] in aim_pull_set(world, "Austria") \
                or not pulled

    def test_p37_keeps_the_hard_recall(self, world):
        # The ladder's own recall outranks every pull: a lost home
        # province makes `_find_homeland_defense` act (the P3.7 slot
        # sits before P7's march in the decision order; the capital
        # arm is elevated to priority 2).
        # A controller flip under a standing army is no staging — march
        # Archduke John out, THEN the province falls (Bavaria holds it;
        # Austria is at war with her, P3.7's PC15-D4 gate).
        world.marshals["ArchdukeJohn"].location = "Carniola"
        world.regions["Tyrol"].controller = "Bavaria"
        _fresh_eyes(world)
        ai = self._ai()
        # The phase loop seeds these per-phase stores; the helper is
        # called directly here.
        ai._recapture_marshal_assignments = {}
        ai._recapture_targets_claimed = set()
        marshals = [m for m in world.marshals.values()
                    if m.nation == "Austria"]
        assert marshals
        actions = [ai._find_homeland_defense(m, "Austria", world)
                   for m in marshals]
        assert any(a for a in actions), \
            "a lost home region must draw a recapture order"

    def test_the_conduct_rule_annexes_only_the_aim(self, world):
        # The slice's second half (the user's "Extend with conduct
        # rule" after the first chain read the pull ALONE raising the
        # debt 397 → 421): at war, on-pull soil may be annexed, an
        # enemy's seat may be stormed (the capital default as a
        # permission), and other soil may not.
        from backend.game_logic.war_council import annexation_permitted
        key = world._make_diplo_key("Austria", "France")
        world.war_objectives.setdefault(key, {})["Austria"] = {
            "target_regions": ["Flanders"]}
        assert annexation_permitted(world, "Austria", "Flanders")
        assert annexation_permitted(world, "Austria", "Milan")
        assert annexation_permitted(world, "Austria", "Paris")
        assert not annexation_permitted(world, "Austria", "Burgundy")

    def test_a_war_without_an_object_storms_only_the_seat(self, world):
        # Stage Sweden into a war with Denmark (no objective, no acquire
        # arm): the pull is EMPTY — nothing steers the march — but the
        # war still has its point, the enemy's seat may be stormed, and
        # nothing else is annexed: a court without an object does not
        # drift sideways.
        from backend.game_logic.war_council import annexation_permitted
        world.diplomatic_states[world._make_diplo_key(
            "Sweden", "Denmark")] = "WAR"
        world.war_instances["t3_3::S|D"] = {
            "attackers": ["Sweden"], "defenders": ["Denmark"],
            "participant_meta": {"Sweden": {"side": "attackers"},
                                 "Denmark": {"side": "defenders"}},
        }
        _fresh_eyes(world)
        assert aim_pull_set(world, "Sweden") == frozenset()
        assert annexation_permitted(world, "Sweden", "Copenhagen")
        assert not annexation_permitted(world, "Sweden", "Holstein")

    def test_the_player_and_vassals_are_exempt(self, world):
        from backend.game_logic.war_council import annexation_permitted
        assert annexation_permitted(world, "France", "Vienna")
        world.vassals["Holland"] = {"lord": "France", "loyalty": 50}
        assert annexation_permitted(world, "Holland", "Hanover")

    def test_the_conduct_seam_down_restores_the_grab(self, world,
                                                     monkeypatch):
        from backend.game_logic.war_council import annexation_permitted
        hold_down(monkeypatch, T3_3_DOWN)
        assert annexation_permitted(world, "Austria", "Amsterdam")

    def test_p45_skips_an_off_aim_walk_in(self, world):
        # Integration at the rung: Archduke John beside an undefended
        # off-aim Bavarian province finds no capture; the same province
        # inside the pull is taken. Franconia is Bavaria's, undefended,
        # adjacent to Tyrol — and no aim of Austria's.
        ai = self._ai()
        ai._walk_ins_this_turn = {}
        # The safety rule has its own pins — staged safe here so the
        # CONDUCT filter is what decides (not Franconia's geometry) —
        # and the boot garrisons march out (Bernadotte and Deroy stand
        # in Franconia; P4.5 takes only UNDEFENDED ground).
        ai._evaluate_capture_safety = lambda *a, **k: (True, "staged")
        world.marshals["Bernadotte"].location = "Westphalia"
        world.marshals["Deroy"].location = "Munich"
        john = world.marshals["ArchdukeJohn"]
        assert john.location == "Tyrol"
        assert "Franconia" in world.regions["Tyrol"].adjacent_regions
        action = ai._find_undefended_capture(john, "Austria", world)
        assert not (action and action.get("target") == "Franconia"), action
        # Name Franconia an aim and the walk-in opens.
        key = world._make_diplo_key("Austria", "Bavaria")
        world.war_objectives.setdefault(key, {})["Austria"] = {
            "target_regions": ["Franconia"]}
        ai._agenda_covet_cache = None
        action = ai._find_undefended_capture(john, "Austria", world)
        assert action and action.get("target") == "Franconia", action

    def test_the_massing_default_is_quiet(self, world):
        # AI-3c stands BUILT (Stage D; TestAI3cFrontier owns the
        # massing pins) — here only the no-crisis default: the boot
        # board arms nobody, the frontier reads empty.
        for nation in ("Austria", "Prussia", "Russia"):
            assert get_intent_frontier(world, nation) == []


class TestTheMeasure:
    """The two chains on the final tree (the kept-record idiom). The
    CONTROL (`_dy_signature_t3_3_control_2026_11_08.json`, both T3-3
    seams held down through `INK_IRON_SEAMS`) proves the instrument's
    corrections moved no world-line; the FINAL
    (`_dy_signature_t3_3_2026_11_08.json`) against it is T3-3's own
    effect, under one metric: the debt falls on every seed, and the
    story classes fall 10 → 8 — the honest cost of discipline (eylau
    and jena converge on wagram's story: Holland, no longer annexed
    off-aim, survives on eylau; Spain never reaches the fight on
    jena)."""

    @pytest.fixture(scope="class")
    def records(self):
        import json as _json
        load = lambda name: _json.loads(  # noqa: E731
            (REPO / "tools" / name).read_text(encoding="utf-8"))
        return (load("_dy_signature_t3_2_2026_11_08.json"),
                load("_dy_signature_t3_3_control_2026_11_08.json"),
                load("_dy_signature_t3_3_2026_11_08.json"))

    @staticmethod
    def _world_line(signature):
        return {k: v for k, v in signature.items()
                if k != "captures_outside_aim"}

    def test_the_control_moves_no_world_line(self, records):
        t32, control, _final = records
        for seed in t32["seeds"]:
            assert (self._world_line(control["seeds"][seed]["signature"])
                    == self._world_line(t32["seeds"][seed]["signature"])), seed

    def test_the_debt_falls_on_every_seed(self, records):
        _t32, control, final = records
        debt = lambda r, s: r["seeds"][s]["signature"]["captures_outside_aim"]  # noqa: E731
        for seed in control["seeds"]:
            assert debt(final, seed) < debt(control, seed), seed
        assert sum(debt(control, s) for s in control["seeds"]) == 386
        assert sum(debt(final, s) for s in final["seeds"]) == 208

    def test_the_classes_are_the_record(self, records):
        _t32, control, final = records
        assert control["story_class_count"] == 10
        assert final["story_class_count"] == 8
        import json as _json
        merged = [s for s in ("eylau", "jena", "wagram")]
        classes = {s: _json.dumps(final["seeds"][s]["story_class"],
                                  sort_keys=True) for s in merged}
        assert len(set(classes.values())) == 1, classes
