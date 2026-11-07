"""T0-F "the eclipse brew" — the sixth slice of Tier 0 of the November 6,
2026 whole-game review (`docs/audits/GAME_REVIEW_2026_11_06.md` §4.1 #8;
`BUG_FIXES.md` §GR GR-4, GR-39, GR-41; the rules `SYSTEMS_REFERENCE.md`
§182).

GR-4 / GR-39 — a coalition against a non-player hegemon brewed with ONE
qualifying court, could not form (`form_coalition` needs two members),
cancelled with no cooldown, and 7b re-announced the same impossible brew
every three turns forever (friedland T18/21/24/27/30). The brew reads the
league's own formation gate now (`a_league_the_brew_could_form`, at BOTH
brew sites — the anti-France brew is the swept sibling), and a formation
that fails at the countdown's expiry rests the chanceries
(`COALITION_COOLDOWN_TURNS`) and says the effort collapsed. Seam:
`brew_follows_formation`.

GR-41 — an AI-vs-AI refused design ask recurred on the dedupe window's
fixed 6-turn cadence: the `design_ask` branch returned before OCT27-13's
`rest_refused_pair`, so the ordered-pair cooldown was never stamped, and
trigger 0a never read it. The refusal stamps the pair now and 0a honors it
(`_is_on_cooldown(..., recipient=target)` — 6, then 12, then 18 turns by
`repeated_ask_factor`), so a refused ask gets rarer. Seam:
`a_refused_ask_rests`.
"""
from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic import ai_diplomacy  # noqa: E402
from backend.game_logic import coalition as co  # noqa: E402
from backend.game_logic.ai_diplomacy import (  # noqa: E402
    NATION_REJECTION_COOLDOWN,
    REFUSAL_DEDUPE_TURNS,
    TYPE_REJECTION_COOLDOWN,
    _evaluate_ai_ai_proposal,
    _get_cooldowns,
    _is_on_cooldown,
    _resolve_ai_ai_proposal,
    _set_cooldowns,
    get_refused_asks,
)
from backend.models.world_state import WorldState  # noqa: E402
from tests.test_ai_intent_peacetime import (  # noqa: E402
    _fake_view,
    _set_relation,
)

SCENARIO = REPO / "godot-client/project-sovereign/assets/maps/europe_1805.json"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(scope="module")
def _board():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO)).to_dict()


@pytest.fixture
def world(_board):
    return WorldState.from_dict(_board)


def _everyone_warm_to(world, target, but=()):
    """Clear the qualifying set for `target` down to `but` — every other
    court warm (+40), the named ones at -20."""
    for n in co._get_all_nations(world):
        if n in (target, world.player_nation):
            continue
        _set_relation(world, n, target, -20 if n in but else 40)


def _no_anti_france_noise(world):
    """Keep sections 6-7 quiet so 7b is the arm under test: the boot's
    Third Coalition cleared (zeroing France's alarm would otherwise
    DISSOLVE it mid-pass, and the dissolution cooldown gates 7b), no brew
    standing, the chanceries unrested, France's own alarm under the
    gate."""
    world.active_coalition = None
    world.coalition_brewing = None
    world.coalition_cooldown = 0
    world.threat_by_target[world.player_nation] = 0


class TestTheBrewReadsTheFormationGate:
    """GR-4 / GR-39 — the gate."""

    def test_the_member_rule_counts_the_courts_at_war_too(self, world):
        # On the 1805 boot France ALONE is at war with Russia, and the
        # player is never counted toward an eclipse league: one qualifying
        # court cannot form it.
        assert co.get_nations_at_war_with_target(world, "Russia") == ["France"]
        assert co.a_league_the_brew_could_form(world, ["Prussia"], "Russia") is False
        assert co.a_league_the_brew_could_form(world, [], "Russia") is False
        assert co.a_league_the_brew_could_form(
            world, ["Prussia", "Sweden"], "Russia") is True
        # Austria's belligerents include BAVARIA (the 1805 boot), so a
        # court already at war with the target counts as a member and one
        # qualifying court suffices there.
        assert "Bavaria" in co.get_nations_at_war_with_target(world, "Austria")
        assert co.a_league_the_brew_could_form(world, ["Prussia"], "Austria") is True

    def test_a_one_court_brew_never_starts(self, world, monkeypatch):
        _no_anti_france_noise(world)
        _everyone_warm_to(world, "Russia", but=("Prussia",))
        monkeypatch.setattr(co, "_eclipse_candidate", lambda w: ("Russia", 70))
        with _quiet():
            co.process_coalition_turn(world)
        assert world.coalition_brewing is None
        assert not [e for e in world.event_log
                    if e.get("type") == "coalition_brewing_started"]

    def test_a_two_court_brew_still_starts(self, world, monkeypatch):
        _no_anti_france_noise(world)
        _everyone_warm_to(world, "Russia", but=("Prussia", "Sweden"))
        monkeypatch.setattr(co, "_eclipse_candidate", lambda w: ("Russia", 70))
        with _quiet():
            co.process_coalition_turn(world)
        assert world.coalition_brewing is not None
        assert world.coalition_brewing.get("target_nation") == "Russia"

    def test_the_seam_down_restores_the_one_court_brew(self, world, monkeypatch):
        _no_anti_france_noise(world)
        _everyone_warm_to(world, "Russia", but=("Prussia",))
        monkeypatch.setattr(co, "_eclipse_candidate", lambda w: ("Russia", 70))
        monkeypatch.setattr(co, "brew_follows_formation", lambda: False)
        with _quiet():
            co.process_coalition_turn(world)
        assert world.coalition_brewing is not None, "the pre-fix reading"

    def test_the_anti_france_sibling_reads_the_same_gate(self, world, monkeypatch):
        """Rule 10: one qualifying court and nobody at war with France
        cannot form a league either — the brew against France waits too."""
        world.active_coalition = None
        world.coalition_brewing = None
        world.coalition_cooldown = 0
        for key in list(world.diplomatic_states):
            if world.player_nation in key:
                world.diplomatic_states[key] = "PEACE"
        _everyone_warm_to(world, world.player_nation, but=("Prussia",))
        world.threat_by_target[world.player_nation] = 65
        monkeypatch.setattr(co, "_eclipse_candidate", lambda w: None)
        with _quiet():
            co.process_coalition_turn(world)
        assert world.coalition_brewing is None
        monkeypatch.setattr(co, "brew_follows_formation", lambda: False)
        # the first pass decayed the staged alarm — restore it for the
        # control, the gate under test is the formation read, not decay
        world.threat_by_target[world.player_nation] = 65
        with _quiet():
            co.process_coalition_turn(world)
        assert world.coalition_brewing is not None, "the pre-fix reading"


class TestAFailedFormationRestsTheChanceries:
    """GR-39 — the expiry."""

    def _expiring_brew(self, world):
        _no_anti_france_noise(world)
        _everyone_warm_to(world, "Russia", but=("Prussia",))
        world.threat_by_target["Russia"] = 70
        world.coalition_brewing = {
            "qualifying_nations": ["Prussia"],
            "turns_remaining": 1,
            "started_turn": int(world.current_turn),
            "threat_at_start": 70,
            "target_nation": "Russia",
        }

    def test_the_failed_expiry_sets_the_cooldown_and_says_so(self, world, monkeypatch):
        self._expiring_brew(world)
        monkeypatch.setattr(co, "_eclipse_candidate", lambda w: ("Russia", 70))
        with _quiet():
            co.process_coalition_turn(world)
        assert world.coalition_brewing is None
        assert world.coalition_cooldown == co.COALITION_COOLDOWN_TURNS
        assert [e for e in world.event_log
                if e.get("type") == "coalition_brewing_cancelled"]

    def test_the_rested_chanceries_do_not_rebrew(self, world, monkeypatch):
        self._expiring_brew(world)
        monkeypatch.setattr(co, "_eclipse_candidate", lambda w: ("Russia", 70))
        with _quiet():
            co.process_coalition_turn(world)
            co.process_coalition_turn(world)
        assert world.coalition_brewing is None
        assert not [e for e in world.event_log
                    if e.get("type") == "coalition_brewing_started"]

    def test_the_seam_down_restores_the_three_turn_loop(self, world, monkeypatch):
        """The review's loop, reproduced in ONE call with the seam down:
        the expiry cancels without a cooldown and 7b re-brews the same
        impossible set in the same pass."""
        self._expiring_brew(world)
        monkeypatch.setattr(co, "_eclipse_candidate", lambda w: ("Russia", 70))
        monkeypatch.setattr(co, "brew_follows_formation", lambda: False)
        with _quiet():
            co.process_coalition_turn(world)
        assert world.coalition_cooldown == 0
        assert world.coalition_brewing is not None, "the re-brew — the loop"
        assert [e for e in world.event_log
                if e.get("type") == "coalition_brewing_started"]


class TestARefusedAskRests:
    """GR-41."""

    def _prussia_asks_hanover(self, world, monkeypatch):
        views = {"Prussia": _fake_view("Prussia", against="Hanover",
                                       price="buy",
                                       want_id="hanoverian_prize")}
        monkeypatch.setattr(
            "backend.game_logic.intent.get_nation_intent",
            lambda nation, w: views.get(nation,
                                        _fake_view(nation, against=None,
                                                   price="indifferent",
                                                   want_id=None)))

    def test_the_refusal_stamps_the_ordered_pair(self, world, monkeypatch):
        self._prussia_asks_hanover(world, monkeypatch)
        proposal = _evaluate_ai_ai_proposal("Prussia", "Hanover", world)
        assert proposal == {"type": "design_ask", "proposer": "Prussia",
                            "target": "Hanover"}
        event = _resolve_ai_ai_proposal(proposal, world)
        assert event and event["type"] == "ai_ai_proposal_refused"
        cooldowns = _get_cooldowns(world)
        assert cooldowns.get("Prussia>Hanover|design_ask") == TYPE_REJECTION_COOLDOWN
        assert cooldowns.get("Prussia>Hanover|nation") == NATION_REJECTION_COOLDOWN

    def test_trigger_0a_honors_the_rest_past_the_dedupe_window(self, world, monkeypatch):
        self._prussia_asks_hanover(world, monkeypatch)
        event = _resolve_ai_ai_proposal(
            _evaluate_ai_ai_proposal("Prussia", "Hanover", world), world)
        assert event
        world.current_turn += REFUSAL_DEDUPE_TURNS + 1
        assert _is_on_cooldown("Prussia", "design_ask", world, 0,
                               recipient="Hanover")
        proposal = _evaluate_ai_ai_proposal("Prussia", "Hanover", world)
        assert proposal is None or proposal.get("type") != "design_ask", (
            proposal)

    def test_a_spent_rest_frees_the_ask(self, world, monkeypatch):
        self._prussia_asks_hanover(world, monkeypatch)
        _resolve_ai_ai_proposal(
            _evaluate_ai_ai_proposal("Prussia", "Hanover", world), world)
        world.current_turn += REFUSAL_DEDUPE_TURNS + 1
        cooldowns = _get_cooldowns(world)
        cooldowns["Prussia>Hanover|design_ask"] = 0
        cooldowns["Prussia>Hanover|nation"] = 0
        _set_cooldowns(world, cooldowns)
        proposal = _evaluate_ai_ai_proposal("Prussia", "Hanover", world)
        assert proposal == {"type": "design_ask", "proposer": "Prussia",
                            "target": "Hanover"}

    def test_the_second_refusal_rests_twice_as_long(self, world, monkeypatch):
        """`repeated_ask_factor`: the second refusal inside
        REFUSAL_MEMORY_TURNS doubles the type cooldown — a refused ask
        gets RARER, the row's whole expectation."""
        self._prussia_asks_hanover(world, monkeypatch)
        _resolve_ai_ai_proposal(
            _evaluate_ai_ai_proposal("Prussia", "Hanover", world), world)
        world.current_turn += REFUSAL_DEDUPE_TURNS + 1
        cooldowns = _get_cooldowns(world)
        cooldowns["Prussia>Hanover|design_ask"] = 0
        cooldowns["Prussia>Hanover|nation"] = 0
        _set_cooldowns(world, cooldowns)
        second = _resolve_ai_ai_proposal(
            _evaluate_ai_ai_proposal("Prussia", "Hanover", world), world)
        assert second and second["type"] == "ai_ai_proposal_refused"
        assert _get_cooldowns(world).get("Prussia>Hanover|design_ask") == (
            TYPE_REJECTION_COOLDOWN * 2)

    def test_the_seam_down_restores_the_six_turn_cadence(self, world, monkeypatch):
        self._prussia_asks_hanover(world, monkeypatch)
        monkeypatch.setattr(ai_diplomacy, "a_refused_ask_rests", lambda: False)
        _resolve_ai_ai_proposal(
            _evaluate_ai_ai_proposal("Prussia", "Hanover", world), world)
        assert not [k for k in _get_cooldowns(world) if ">" in k], (
            "no stamp with the seam down")
        world.current_turn += REFUSAL_DEDUPE_TURNS + 1
        proposal = _evaluate_ai_ai_proposal("Prussia", "Hanover", world)
        assert proposal == {"type": "design_ask", "proposer": "Prussia",
                            "target": "Hanover"}, "the pre-fix cadence"
        assert get_refused_asks(world, "Prussia", "Hanover")
