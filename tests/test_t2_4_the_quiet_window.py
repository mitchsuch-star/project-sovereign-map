"""T2-4 — the quiet-window sleep: Russia's two shores
(`DYNAMISM_SPEC.md` §2 Tier 2; November 8, 2026; the rules
`SYSTEMS_REFERENCE.md` §190).

The rule, one clause in `_contain_active` (`agendas.py`, beside the
SF-LB-1 Armed-Peace sibling): a contain design sleeps once the court's
OWN war with its hegemon has been over for the quiet window
(`AGENDA_QUIET_WINDOW_TURNS`, 8) — not belligerent with him (WAR or
ARMISTICE wakes it at once), and the ended war ON RECORD (the witness:
a court that never fought its hegemon keeps the design armed, so
contain can still drive its first war — Sweden boots at PEACE with
France and her scourge must not sleep at boot — and a NEW hegemon
re-arms the watch). The clock is `coalition.pair_war_quiet_turns`
(the fresh-peace scan's shape over BOTH war stores — the archive keeps
the witness past retention, no flap at age 10). The deck advances:
the arbiter stands down and `gulf_and_straits` wakes. Dormancy is
never satisfaction (the T2-2 law — `_entry_satisfied`'s contain arm
reads the share directly). The seam `a_quiet_window_sleeps_the_arbiter`
(tests/_t2_seams.py) holds the old reading for the recorded boards and
the attribution arms.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic.agendas import (  # noqa: E402
    AGENDA_QUIET_WINDOW_TURNS,
    entry_satisfied,
    get_active_agenda,
)
from backend.game_logic.coalition import pair_war_quiet_turns  # noqa: E402
from tests._t2_seams import T2_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
T2_4_DOWN = T2_SEAMS_BY_ROW["T2-4"]


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


def _sign_peace(world, a: str, b: str, turns_ago: int = 0) -> None:
    """The T2-2 staging idiom: end every LIVE instance holding the pair
    on opposite sides (the boot war included), set the pair to PEACE,
    leave an ended instance in the shape the pair-end scans read."""
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
        world.war_instances[f"t2_4::{a}|{b}"] = {
            "attackers": [a], "defenders": [b],
            "participant_meta": {a: {"side": "attackers"},
                                 b: {"side": "defenders"}},
            "ended_turn": ended,
        }
    world.diplomatic_states[world._make_diplo_key(a, b)] = "PEACE"
    _fresh_eyes(world)


def _no_wars_on_record(world, nation: str, target: str) -> None:
    """The never-fought board: no instance live or archived, the pair
    at PEACE."""
    world.war_instances.clear()
    world.archived_war_instances = []
    world.diplomatic_states[world._make_diplo_key(nation, target)] = "PEACE"
    _fresh_eyes(world)


def _view_id(world, nation: str):
    view = get_active_agenda(nation, world)
    return getattr(view, "id", None)


class TestTheRule:
    def test_the_quiet_window_wakes_the_second_shore(self, world):
        # Boot truth first: the arbiter is live (the pair at war).
        assert _view_id(world, "Russia") == "arbiter_of_europe"
        _sign_peace(world, "Russia", "France",
                    turns_ago=AGENDA_QUIET_WINDOW_TURNS)
        assert pair_war_quiet_turns("Russia", world, "France") \
            == AGENDA_QUIET_WINDOW_TURNS
        view = get_active_agenda("Russia", world)
        assert view is not None and view.id == "gulf_and_straits", (
            "the arbiter must stand down after the quiet window and the "
            "deck advance to the Tsar's two shores")
        assert view.type == "acquire_regions"

    def test_not_a_turn_before_the_window(self, world):
        _sign_peace(world, "Russia", "France",
                    turns_ago=AGENDA_QUIET_WINDOW_TURNS - 1)
        assert _view_id(world, "Russia") == "arbiter_of_europe"

    @pytest.mark.parametrize("state", ["OPEN_BORDERS", "NON_AGGRESSION"])
    def test_states_more_at_peace_than_peace_sleep_too(self, world, state):
        # Deliberately wider than the SF-LB-1 sibling's literal PEACE:
        # open borders and non-aggression are quieter still.
        _sign_peace(world, "Russia", "France",
                    turns_ago=AGENDA_QUIET_WINDOW_TURNS)
        world.diplomatic_states[world._make_diplo_key("Russia", "France")] \
            = state
        _fresh_eyes(world)
        assert _view_id(world, "Russia") == "gulf_and_straits"

    def test_an_armistice_never_sleeps_the_watch(self, world):
        # A paused war is the war (the module's belligerent doctrine).
        _sign_peace(world, "Russia", "France",
                    turns_ago=AGENDA_QUIET_WINDOW_TURNS)
        world.diplomatic_states[world._make_diplo_key("Russia", "France")] \
            = "ARMISTICE"
        _fresh_eyes(world)
        assert _view_id(world, "Russia") == "arbiter_of_europe"

    def test_the_wars_return_wakes_it_at_once(self, world):
        _sign_peace(world, "Russia", "France",
                    turns_ago=AGENDA_QUIET_WINDOW_TURNS)
        assert _view_id(world, "Russia") == "gulf_and_straits"
        world.diplomatic_states[world._make_diplo_key("Russia", "France")] \
            = "WAR"
        _fresh_eyes(world)
        assert _view_id(world, "Russia") == "arbiter_of_europe"


class TestTheWitness:
    def test_never_fought_stays_armed(self, world):
        # The first-war law: Sweden boots at PEACE with France with no
        # war on record — the scourge must not sleep at boot (and a
        # crafted no-record Russia reads the same).
        assert world.get_diplomatic_state("Sweden", "France") == "PEACE"
        assert pair_war_quiet_turns("Sweden", world, "France") is None
        assert _view_id(world, "Sweden") == "scourge_of_the_usurper"
        _no_wars_on_record(world, "Russia", "France")
        assert pair_war_quiet_turns("Russia", world, "France") is None
        assert _view_id(world, "Russia") == "arbiter_of_europe"

    def test_the_witness_is_the_hegemons_own(self, world):
        # A war with ANOTHER court quiets nothing — which is also why a
        # NEW hegemon re-arms the watch (no war with him on record).
        _no_wars_on_record(world, "Russia", "France")
        world.war_instances["t2_4::Russia|Austria"] = {
            "attackers": ["Russia"], "defenders": ["Austria"],
            "participant_meta": {"Russia": {"side": "attackers"},
                                 "Austria": {"side": "defenders"}},
            "ended_turn": int(world.current_turn) - 12,
        }
        _fresh_eyes(world)
        assert _view_id(world, "Russia") == "arbiter_of_europe"

    def test_the_witness_survives_the_archive(self, world):
        # End 12 turns past, the instance moved to the archive at
        # retention (10): the sleep must NOT flap awake for want of
        # evidence.
        _no_wars_on_record(world, "Russia", "France")
        world.archived_war_instances.append({
            "attackers": ["France"], "defenders": ["Russia"],
            "participant_meta": {"France": {"side": "attackers"},
                                 "Russia": {"side": "defenders"}},
            "ended_turn": int(world.current_turn) - 12,
        })
        _fresh_eyes(world)
        assert pair_war_quiet_turns("Russia", world, "France") == 12
        assert _view_id(world, "Russia") == "gulf_and_straits"

    def test_a_separate_peace_exit_is_the_pairs_end(self, world):
        # The exiter's own war ends at its exited_turn while the
        # instance fights on (the Pressburg shape).
        _no_wars_on_record(world, "Russia", "France")
        world.war_instances["t2_4::third_coalition"] = {
            "attackers": ["France"], "defenders": ["Russia", "Austria"],
            "participant_meta": {
                "France": {"side": "attackers"},
                "Austria": {"side": "defenders"},
                "Russia": {"side": "defenders",
                           "exited_turn": int(world.current_turn)
                           - AGENDA_QUIET_WINDOW_TURNS},
            },
        }
        _fresh_eyes(world)
        assert pair_war_quiet_turns("Russia", world, "France") \
            == AGENDA_QUIET_WINDOW_TURNS
        assert _view_id(world, "Russia") == "gulf_and_straits"

    def test_the_pair_resolved_record_counts(self, world):
        # The T2-3 renege shape: the pair resolved by diplo_key_meta
        # while the instance lives on for others.
        _no_wars_on_record(world, "Russia", "France")
        pair_key = world._make_diplo_key("Russia", "France")
        world.war_instances["t2_4::resolved_pair"] = {
            "attackers": ["France"], "defenders": ["Austria"],
            "participant_meta": {"France": {"side": "attackers"},
                                 "Austria": {"side": "defenders"}},
            "diplo_key_meta": {pair_key: {
                "pair_status": "resolved",
                "resolved_turn": int(world.current_turn)
                - AGENDA_QUIET_WINDOW_TURNS,
            }},
        }
        _fresh_eyes(world)
        assert pair_war_quiet_turns("Russia", world, "France") \
            == AGENDA_QUIET_WINDOW_TURNS
        assert _view_id(world, "Russia") == "gulf_and_straits"


class TestTheLaws:
    def test_dormancy_is_never_satisfaction(self, world):
        # The T2-2 law: a sleeping arbiter never reads satisfied while
        # the share stands — no +10 resolve, no early separate peace.
        _sign_peace(world, "Russia", "France",
                    turns_ago=AGENDA_QUIET_WINDOW_TURNS)
        assert _view_id(world, "Russia") == "gulf_and_straits"
        arbiter = next(e for e in world.agendas["Russia"]
                       if e.get("id") == "arbiter_of_europe")
        assert entry_satisfied(world, "Russia", arbiter) is False

    def test_satisfaction_by_share_is_untouched(self, world):
        # share < floor satisfies, asleep or awake alike.
        crafted = {"id": "t2_4_sat", "type": "contain_hegemon",
                   "share_floor": 1.5}
        assert entry_satisfied(world, "Russia", crafted) is True
        _sign_peace(world, "Russia", "France",
                    turns_ago=AGENDA_QUIET_WINDOW_TURNS)
        assert entry_satisfied(world, "Russia", crafted) is True

    def test_the_armed_peace_sibling_is_independent(self, world,
                                                    monkeypatch):
        # SF-LB-1 sleeps even the morning after the treaty, with the
        # T2-4 seam down — the two sleeps share nothing but the bed.
        from backend.game_logic import coalition as C
        monkeypatch.setattr(
            C, "armed_peace_reading",
            lambda w, ahead=0: {"holds": True, "hegemon": "France"})
        _sign_peace(world, "Russia", "France", turns_ago=0)
        hold_down(monkeypatch, T2_4_DOWN)
        _fresh_eyes(world)
        assert _view_id(world, "Russia") == "gulf_and_straits"

    def test_the_volte_face_route_is_untouched(self, world, monkeypatch):
        # In the hegemon's bloc the design is inactive BEFORE the quiet
        # clause — the Tilsit route reads the same with the seam down.
        _no_wars_on_record(world, "Russia", "France")
        world.diplomatic_states[world._make_diplo_key("Russia", "France")] \
            = "ALLIANCE"
        _fresh_eyes(world)
        assert _view_id(world, "Russia") == "gulf_and_straits"
        hold_down(monkeypatch, T2_4_DOWN)
        _fresh_eyes(world)
        assert _view_id(world, "Russia") == "gulf_and_straits"

    def test_swedens_one_design_deck_goes_dark(self, world):
        # The shared law: the scourge sleeps the same way, and a
        # one-design deck leaves the court design-less.
        _sign_peace(world, "Sweden", "France",
                    turns_ago=AGENDA_QUIET_WINDOW_TURNS)
        assert get_active_agenda("Sweden", world) is None

    def test_the_sleep_survives_the_save(self, world):
        # Derived from stores that serialize — no new world field.
        from backend.models.world_state import WorldState
        _sign_peace(world, "Russia", "France",
                    turns_ago=AGENDA_QUIET_WINDOW_TURNS)
        assert _view_id(world, "Russia") == "gulf_and_straits"
        back = WorldState.from_dict(
            json.loads(json.dumps(world.to_dict(), default=str)))
        assert _view_id(back, "Russia") == "gulf_and_straits"

    def test_the_seam_down_restores_the_old_reading(self, world,
                                                    monkeypatch):
        _sign_peace(world, "Russia", "France",
                    turns_ago=AGENDA_QUIET_WINDOW_TURNS)
        assert _view_id(world, "Russia") == "gulf_and_straits"
        hold_down(monkeypatch, T2_4_DOWN)
        _fresh_eyes(world)
        assert _view_id(world, "Russia") == "arbiter_of_europe", (
            "down: the arbiter watches forever — the pre-T2-4 reading, "
            "byte for byte")


class TestTheMeasure:
    """The dated re-record `tools/_dy_signature_t2_4_2026_11_08.json`
    against the T2-3 record (the kept-record idiom — each committed
    record stays its slice's truth). ZERO AMBIENT MOVERS, deliberately
    read: the ten ambient boards never end a war of FRANCE'S own (the
    idle player signs nothing), so no pair with the hegemon ever
    reaches the quiet window inside 40 turns — the road to the second
    shore is the PLAYER'S own peace, a reactive and discoverable
    consequence of signing with the Tsar; and Sweden, at peace with
    France from boot, is held armed by the witness law on every seed
    (without it her never-fought scourge slept at boot and every
    world-line moved, wrongly). The behavior proof is this file's
    staged pins; the record pins the ambient silence."""

    @pytest.fixture(scope="class")
    def records(self):
        prev = json.loads(
            (REPO / "tools" / "_dy_signature_t2_3_2026_11_08.json")
            .read_text(encoding="utf-8"))
        new = json.loads(
            (REPO / "tools" / "_dy_signature_t2_4_2026_11_08.json")
            .read_text(encoding="utf-8"))
        return prev, new

    def test_the_sleep_keeps_the_floor(self, records):
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
