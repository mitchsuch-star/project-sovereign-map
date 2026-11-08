"""T2-2 — peace closes the theatre (`DYNAMISM_SPEC.md` §2 Tier 2;
November 8, 2026; the rules `SYSTEMS_REFERENCE.md` §188).

The rule, one clause in the ONE coveting predicate
(`agendas.region_coveted`): a region whose holder has JUST made peace
with the coveter is not coveted while the fresh-peace floor runs —
`coalition.fresh_peace_turns_left`, the game's one fresh-peace rule
(5 turns), deliberately no second constant. The design sleeps DERIVED,
never stored; the deck advances past it (Austria signs and turns to the
Eastern Question) and it wakes the turn the floor lapses. The seam
`a_fresh_peace_quiets_the_design` (tests/_t2_seams.py) holds the old
reading for the recorded boards and the attribution arms.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic.agendas import (  # noqa: E402
    coveted_unmet,
    get_active_agenda,
    region_coveted,
)
from tests._t2_seams import T2_SEAMS_DOWN, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")


@pytest.fixture()
def world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed="historical")


def _sign_peace(world, a: str, b: str, turns_ago: int = 0) -> None:
    """Sign the pair's peace for real: end every LIVE instance that holds
    them on opposite sides (the boot war included — a staged fresh peace
    beside a still-burning war would read "back at war" and rightly
    suppress the grudge), set the pair state to PEACE, and leave an ended
    instance in the shape `fresh_peace_turns_left` reads."""
    ended = int(world.current_turn) - int(turns_ago)
    found = False
    for inst in (world.war_instances or {}).values():
        meta = inst.get("participant_meta") or {}
        mine, theirs = meta.get(a), meta.get(b)
        if not mine or not theirs:
            continue
        if mine.get("side") and mine.get("side") != theirs.get("side"):
            if inst.get("ended_turn") is None:
                inst["ended_turn"] = ended
            found = True
    if not found:
        world.war_instances[f"t2_2::{a}|{b}"] = {
            "attackers": [a], "defenders": [b],
            "participant_meta": {a: {"side": "attackers"},
                                 b: {"side": "defenders"}},
            "ended_turn": ended,
        }
    world.diplomatic_states[world._make_diplo_key(a, b)] = "PEACE"
    _fresh_eyes(world)


def _fresh_eyes(world) -> None:
    world._agenda_cache = None
    world.invalidate_active_nations_cache()


class TestTheRule:
    def test_a_fresh_peace_quiets_the_holders_region(self, world):
        # Piedmont is France's own at boot — coveted by Austria's
        # redeem_italy until the ink dries.
        assert region_coveted(world, "Austria", "Piedmont")
        _sign_peace(world, "Austria", "France")
        assert not region_coveted(world, "Austria", "Piedmont")
        assert not coveted_unmet(world, "Austria", "Piedmont")

    def test_the_floor_lapses_and_the_design_wakes(self, world):
        _sign_peace(world, "Austria", "France", turns_ago=0)
        assert not region_coveted(world, "Austria", "Piedmont")
        world.current_turn += 5          # FRESH_PEACE_FLOOR_TURNS
        _fresh_eyes(world)
        assert region_coveted(world, "Austria", "Piedmont")

    def test_a_vassals_region_reads_the_overlord(self, world):
        # Milan is the Kingdom of Italy's — France's client; the peace
        # with FRANCE quiets it (the effective holder, `_top_overlord`).
        assert region_coveted(world, "Austria", "Milan")
        _sign_peace(world, "Austria", "France")
        assert not region_coveted(world, "Austria", "Milan")

    def test_a_third_partys_peace_quiets_nothing(self, world):
        # Prussia's peace with France is not Austria's.
        _sign_peace(world, "Prussia", "France")
        assert region_coveted(world, "Austria", "Piedmont")

    def test_own_and_vassal_clauses_untouched(self, world):
        assert not region_coveted(world, "France", "Piedmont")
        _sign_peace(world, "Austria", "France")
        assert not region_coveted(world, "France", "Piedmont")

    def test_the_seam_down_restores_the_old_reading(self, world,
                                                    monkeypatch):
        _sign_peace(world, "Austria", "France")
        hold_down(monkeypatch, T2_SEAMS_DOWN)
        assert region_coveted(world, "Austria", "Piedmont")


class TestTheStory:
    def test_austria_signs_and_turns_to_the_eastern_question(self, world):
        """Pressburg's shape: peaces with France (Milan's overlord,
        Piedmont, Savoy) and Bavaria (Munich, Swabia) put both Italian
        and German designs to sleep — the deck advances to the Eastern
        Question; the floor lapses and the Italian design wakes."""
        before = get_active_agenda("Austria", world)
        assert before is not None and before.id == "redeem_italy"
        _sign_peace(world, "Austria", "France")
        _sign_peace(world, "Austria", "Bavaria")
        view = get_active_agenda("Austria", world)
        assert view is not None and view.id == "the_eastern_question", view
        world.current_turn += 5
        _fresh_eyes(world)
        after = get_active_agenda("Austria", world)
        assert after is not None and after.id == "redeem_italy"

    def test_dormancy_is_derived_never_stored(self, world):
        keys_before = set(world.to_dict().keys())
        _sign_peace(world, "Austria", "France")
        get_active_agenda("Austria", world)
        assert set(world.to_dict().keys()) == keys_before

    def test_the_peace_closes_the_theatre_not_the_grudge(self, world):
        """T2-2's companion (the slice's own catch — three grudge pins
        went red before it): §5.8's grudge subject is exactly the design
        the peace suppressed, so the grudge reader sees the deck with the
        theatre OPEN while the activation sleeps. Austria signs with
        France, turns to the Eastern Question — and still grudges her."""
        from backend.game_logic.agendas import get_agenda_grudge_nations
        _sign_peace(world, "Austria", "France")
        _sign_peace(world, "Austria", "Bavaria")
        view = get_active_agenda("Austria", world)
        assert view is not None and view.id == "the_eastern_question"
        assert "Austria" in get_agenda_grudge_nations(world)

    def test_a_fresh_peace_never_satisfies_the_design(self, world):
        """Dormancy is never satisfaction (the slice's own catch — the
        first dated re-record showed Holland proclaiming the United
        Netherlands on two seeds without Flanders ever taken): under the
        floor the design SLEEPS (not active) but stays UNSATISFIED — no
        +10 resolve, no formation, no early separate peace for winning
        nothing (the GE-1 pathology by another door). Satisfaction reads
        the theatre-open covet."""
        from backend.game_logic.agendas import entry_satisfied
        entry = next(e for e in world.agendas["Austria"]
                     if e.get("id") == "redeem_italy")
        assert not entry_satisfied(world, "Austria", entry)
        _sign_peace(world, "Austria", "France")
        _sign_peace(world, "Austria", "Bavaria")
        assert get_active_agenda("Austria", world).id == "the_eastern_question"
        assert not entry_satisfied(world, "Austria", entry)

    def test_the_ink_proclaims_no_crown(self, world):
        """The formation poll reads `entry_satisfied`: a freed Holland at
        fresh peace with Flanders' holder (France) must NOT proclaim the
        United Netherlands — and DOES the moment it actually holds
        Flanders (the staging's own control)."""
        from backend.game_logic.formations import process_formations
        del world.vassals["Holland"]          # Amsterdam answers no one
        _sign_peace(world, "Holland", "France")
        proclaimed = [p["nation"] for p in process_formations(world)]
        assert "Holland" not in proclaimed
        world.regions["Flanders"].controller = "Holland"
        _fresh_eyes(world)
        proclaimed = [p["nation"] for p in process_formations(world)]
        assert "Holland" in proclaimed

    def test_returned_targets_still_dissolve_the_grudge(self, world):
        """The R156 payoff survives the companion: hand Austria every
        Italian and German target and the grudge dissolves even inside
        the fresh-peace window (the theatre-open read keeps the
        self/vassal clause)."""
        from backend.game_logic.agendas import get_agenda_grudge_nations
        _sign_peace(world, "Austria", "France")
        _sign_peace(world, "Austria", "Bavaria")
        for name in ("Milan", "Piedmont", "Savoy", "Munich", "Swabia"):
            world.regions[name].controller = "Austria"
        world.invalidate_frontier_cache() if hasattr(
            world, "invalidate_frontier_cache") else None
        _fresh_eyes(world)
        assert "Austria" not in get_agenda_grudge_nations(world)


# The seeds whose 40-turn world-lines moved under the rule, T2-B record →
# T2-2 record (the per-seed truth: only boards where an AI–AI peace
# actually touches a coveted theatre move; the other seven keep theirs,
# HISTORICAL among them). The first, pre-fix chain had moved historical
# and wagram too — by the phantom United Netherlands alone.
MOVED_SEEDS = ["austerlitz", "lodi", "ulm"]


class TestTheMeasure:
    """The dated re-record `tools/_dy_signature_t2_2_2026_11_08.json`
    against the T2-B record (the kept-record idiom — the committed
    `_dy_signature_bands_2026_11_08.json` stays its slice's truth)."""

    @pytest.fixture(scope="class")
    def records(self):
        import json
        bands = json.loads(
            (REPO / "tools" / "_dy_signature_bands_2026_11_08.json")
            .read_text(encoding="utf-8"))
        t22 = json.loads(
            (REPO / "tools" / "_dy_signature_t2_2_2026_11_08.json")
            .read_text(encoding="utf-8"))
        return bands, t22

    def test_the_rule_keeps_the_floor(self, records):
        bands, t22 = records
        assert t22["story_class_count"] >= bands["story_class_count"]
        assert t22["story_class_count"] == 10

    def test_the_moved_seeds_are_the_record(self, records):
        bands, t22 = records
        moved = [s for s in sorted(bands["seeds"])
                 if bands["seeds"][s]["signature"]
                 != t22["seeds"][s]["signature"]]
        assert moved == MOVED_SEEDS, moved

    def test_historical_is_byte_identical(self, records):
        bands, t22 = records
        assert bands["seeds"]["historical"] == t22["seeds"]["historical"]

    def test_no_crown_by_ink_on_any_seed(self, records):
        """The satisfaction fix's measure-level face: no seed's
        `formations` column gained a state this slice (the pre-fix chain
        read Holland on two)."""
        _bands, t22 = records
        assert all(not s["signature"].get("formations")
                   for s in t22["seeds"].values())
