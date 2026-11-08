"""T2-5 — Prussia's second design: Swedish Pomerania
(`DYNAMISM_SPEC.md` §2 Tier 2; November 8, 2026; the rules
`SYSTEMS_REFERENCE.md` §191).

Authored content, no new rule of play: `swedish_pomerania`
(`acquire_regions`, ["Stralsund"] — the drawn province of Swedish
Pomerania, Sweden's at boot) joins Prussia's deck BEHIND
`armed_neutrality`. The seat is the slice's ruling: `_active_guard_map`
prices ACTIVE guards only (a latent guard prices nothing — S14G-11),
and Stralsund is coveted on essentially every board, so an acquire
seated above the guard would kill the Ansbach trap and retire
Prussia's ruled neutral posture (S14k). Seated third, the claim
speaks only when Prussia is already at war with the Hanover question
settled — 1715 Stettin, 1815 the actual acquisition. No order band
(the §3.8.2 gate ruled none for Prussia), no readiness (the
`gulf_and_straits` second-design precedent), no seam (content, the
T2-B precedent — the kept-record idiom covers the measure).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic.agendas import (  # noqa: E402
    _active_guard_map,
    entry_satisfied,
    get_active_agenda,
    get_agenda_military_targets,
    region_coveted,
)

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
DECK_IDS = ["hanoverian_prize", "armed_neutrality", "swedish_pomerania"]


@pytest.fixture()
def world():
    from backend.models.world_state import WorldState
    w = WorldState.from_scenario(str(SCENARIO), seed="historical")
    w.current_turn = 20
    _fresh_eyes(w)
    return w


def _fresh_eyes(world) -> None:
    world._agenda_cache = None
    world.invalidate_active_nations_cache()


def _conquer(world, region_name: str, nation: str) -> None:
    world.regions[region_name].controller = nation
    _fresh_eyes(world)


def _set_state(world, a: str, b: str, state: str) -> None:
    world.diplomatic_states[world._make_diplo_key(a, b)] = state
    _fresh_eyes(world)


def _view_id(world, nation: str):
    view = get_active_agenda(nation, world)
    return getattr(view, "id", None)


class TestTheSeat:
    def test_boot_invisible_on_every_seed(self):
        # The pin-22 sibling: the prize leads at boot, the claim third,
        # on historical and on rolled seeds alike (deck CONTENT is
        # Tier 1 — fixed; only play can surface the claim).
        from backend.models.world_state import WorldState
        for seed in ("historical", "iron-eagle-07", "stern-lion-42"):
            w = WorldState.from_scenario(str(SCENARIO), seed=seed)
            assert _view_id(w, "Prussia") == "hanoverian_prize", seed
            assert [e.get("id") for e in w.agendas["Prussia"]] \
                == DECK_IDS, seed

    def test_inactive_by_order_not_by_predicate(self, world):
        # Stralsund is coveted at boot — the claim is held back by the
        # deck walk alone, exactly the gulf_and_straits shape.
        assert region_coveted(world, "Prussia", "Stralsund")
        assert _view_id(world, "Prussia") == "hanoverian_prize"

    def test_the_guards_seat_held(self, world):
        # The S14k pin re-affirmed on the widened deck: Hanover taken,
        # at peace — the GUARD is the next stop, never the claim.
        _conquer(world, "Hanover", "Prussia")
        assert _view_id(world, "Prussia") == "armed_neutrality"

    def test_the_ansbach_trap_is_intact(self, world):
        # The seat's whole point: with the guard active, Berlin is
        # still a priced guard region (a latent guard prices nothing —
        # the acquire seated ABOVE it would have killed this).
        _conquer(world, "Hanover", "Prussia")
        assert _view_id(world, "Prussia") == "armed_neutrality"
        guard_map = _active_guard_map(world)
        assert guard_map.get("Berlin") == "Prussia"

    def test_the_waterfall_at_war(self, world):
        # The re-seat's mirror: Hanover settled, Prussia belligerent —
        # the guard skipped, the claim speaks.
        _conquer(world, "Hanover", "Prussia")
        _set_state(world, "Prussia", "Russia", "WAR")
        view = get_active_agenda("Prussia", world)
        assert view is not None and view.id == "swedish_pomerania"
        assert view.type == "acquire_regions"

    def test_the_target_is_stralsund(self, world):
        _conquer(world, "Hanover", "Prussia")
        _set_state(world, "Prussia", "Russia", "WAR")
        assert get_agenda_military_targets("Prussia", world) \
            == ["Stralsund"]


class TestTheClauses:
    def test_a_fresh_peace_with_sweden_suppresses_it(self, world):
        # T2-2's clause, derived: ink with Stockholm quiets the claim
        # while the floor runs — the war board's view falls to None.
        _conquer(world, "Hanover", "Prussia")
        _set_state(world, "Prussia", "Russia", "WAR")
        assert _view_id(world, "Prussia") == "swedish_pomerania"
        world.war_instances["t2_5::Prussia|Sweden"] = {
            "attackers": ["Prussia"], "defenders": ["Sweden"],
            "participant_meta": {"Prussia": {"side": "attackers"},
                                 "Sweden": {"side": "defenders"}},
            "ended_turn": int(world.current_turn),
        }
        _set_state(world, "Prussia", "Sweden", "PEACE")
        assert _view_id(world, "Prussia") is None

    def test_an_allys_shore_is_not_coveted(self, world):
        # AN_ALLY_IS_NOT_COVETED: a Swedish ally keeps her shore.
        _conquer(world, "Hanover", "Prussia")
        _set_state(world, "Prussia", "Russia", "WAR")
        _set_state(world, "Prussia", "Sweden", "ALLIANCE")
        assert _view_id(world, "Prussia") is None

    def test_satisfaction_is_the_shore_in_hand(self, world):
        deck = world.agendas["Prussia"]
        claim = next(e for e in deck if e.get("id") == "swedish_pomerania")
        assert entry_satisfied(world, "Prussia", claim) is False
        _conquer(world, "Stralsund", "Prussia")
        assert entry_satisfied(world, "Prussia", claim) is True

    def test_the_deck_round_trips_the_save(self, world):
        from backend.models.world_state import WorldState
        back = WorldState.from_dict(
            json.loads(json.dumps(world.to_dict(), default=str)))
        assert [e.get("id") for e in back.agendas["Prussia"]] == DECK_IDS

    def test_the_emergent_idiom_is_untouched(self, world):
        # The revanche contract: an emergent entry PREPENDS and leads
        # the walk; the claim's seat never shifts index 0.
        world.agendas["Prussia"].insert(0, {
            "id": "t2_5_emergent", "type": "acquire_regions",
            "regions": ["Flanders"], "emergent": True,
        })
        _fresh_eyes(world)
        assert _view_id(world, "Prussia") == "t2_5_emergent"
        assert [e.get("id") for e in world.agendas["Prussia"]] \
            == ["t2_5_emergent"] + DECK_IDS


class TestTheMeasure:
    """The dated re-record `tools/_dy_signature_t2_5_2026_11_08.json`
    against the T2-4 record (the kept-record idiom — each committed
    record stays its slice's truth). ZERO AMBIENT MOVERS, deliberately
    read: the claim is boot-invisible by SEAT (the prize leads) and
    ambient-invisible by CORRIDOR — the waterfall needs Hanover
    settled AND Prussia belligerent, and even on marengo, where the
    bandwagoned Prussia IS at war, Hanover's province passes to Hesse
    and stays coveted, so the prize never settles. The corridor is
    the played game's own: the player's Schoenbrunn — take the
    dangled Hanover, find yourself at war, and Berlin's eye turns to
    Stralsund. The behavior proof is this file's staged pins; the
    record pins the ambient silence."""

    @pytest.fixture(scope="class")
    def records(self):
        prev = json.loads(
            (REPO / "tools" / "_dy_signature_t2_4_2026_11_08.json")
            .read_text(encoding="utf-8"))
        new = json.loads(
            (REPO / "tools" / "_dy_signature_t2_5_2026_11_08.json")
            .read_text(encoding="utf-8"))
        return prev, new

    def test_the_claim_keeps_the_floor(self, records):
        prev, new = records
        assert new["story_class_count"] >= prev["story_class_count"]
        assert new["story_class_count"] == 10

    def test_no_ambient_seed_moves(self, records):
        prev, new = records
        moved = [s for s in sorted(prev["seeds"])
                 if prev["seeds"][s] != new["seeds"][s]]
        assert moved == [], moved

    def test_historical_is_byte_identical(self, records):
        prev, new = records
        assert prev["seeds"]["historical"] == new["seeds"]["historical"]
