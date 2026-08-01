"""AI-6 + AI-6b — the narration cap, relevance weighting, and tempo
(docs/AI_INTENT_SPEC.md §4.6 + §11.1 Stage F; landing record §19).

The three narration pins the stage exit demands:
- THE CAP: at most INTENT_DISPATCH_CAP routine ladder-movement lines per
  dispatch, chosen by weight x proximity-to-French-interest, the rest
  collapsed into ONE tail line;
- THE EXEMPTION: fore-warnings, declarations and every §4.6a beat are
  EVENTS on their own dispatch types — the cap machinery never sees
  them (v1.2: the cap governs routine movement only);
- NEVER-COLLAPSED: a beat never lands in the tail — including Stage E's
  beat-class pair `design_promoted` / `volte_face` (the §18.1 handoff).

Movement detection is the nation_agenda_seen idiom on a new serialized
sibling `nation_intent_seen` (nation -> "want|price"): first observation
silent, want-changes silent (agenda_shift owns them), survival silent
(the crisis machinery owns that drama) — only a same-want RUNG change
is weather worth a line.
"""

from pathlib import Path

import pytest

from backend.game_logic import intent as intent_module
from backend.game_logic.intent import (
    INTENT_DISPATCH_CAP,
    NARRATION_EXEMPT_EVENT_TYPES,
    IntentView,
    process_intent_movements,
)
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture()
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _view(nation, want="test_design", price="align", weight=60,
          against=None, survival=False):
    return IntentView(nation=nation, want_id=want, want_title="The Design",
                      want_type="acquire_regions", against=against,
                      weight=weight, price=price, survival=survival)


def _patch_views(monkeypatch, views):
    original = intent_module.get_nation_intent

    def patched(nation, world):
        if nation in views:
            return views[nation]
        return original(nation, world)

    monkeypatch.setattr(intent_module, "get_nation_intent", patched)


def _movement_events(world):
    return [e for e in world.pending_dispatch_events
            if e.get("type") in ("intent_hardens", "intent_eases")]


def _tail_events(world):
    return [e for e in world.pending_dispatch_events
            if e.get("type") == "intent_movement_tail"]


class TestMovementDetection:
    def test_first_observation_is_silent(self, world):
        assert process_intent_movements(world) == []
        assert world.nation_intent_seen  # recorded, not announced
        assert _movement_events(world) == []

    def test_same_want_rung_change_emits_one_line(self, world,
                                                  monkeypatch):
        process_intent_movements(world)  # record the boot state
        _patch_views(monkeypatch, {
            "Prussia": _view("Prussia", want="hanoverian_prize",
                             price="coerce", weight=74,
                             against="France")})
        world.nation_intent_seen["Prussia"] = "hanoverian_prize|align"
        events = process_intent_movements(world)
        hardens = [e for e in events if e["type"] == "intent_hardens"]
        assert [e["nation"] for e in hardens] == ["Prussia"]
        queued = _movement_events(world)
        assert len(queued) == 1
        assert queued[0]["template_vars"]["price"] == "an ultimatum"
        assert queued[0]["fog_rule"] == "always"

    def test_cooling_emits_eases(self, world, monkeypatch):
        process_intent_movements(world)
        _patch_views(monkeypatch, {
            "Prussia": _view("Prussia", want="hanoverian_prize",
                             price="ask", weight=30)})
        world.nation_intent_seen["Prussia"] = "hanoverian_prize|coerce"
        events = process_intent_movements(world)
        assert [e["type"] for e in events] == ["intent_eases"]

    def test_want_change_is_the_shift_beats_news(self, world,
                                                 monkeypatch):
        """A new design is agenda_shift's announcement (NA-1) — the rung
        channel stays silent on a want-change turn."""
        process_intent_movements(world)
        _patch_views(monkeypatch, {
            "Prussia": _view("Prussia", want="revanche_prussia",
                             price="fight", weight=90)})
        world.nation_intent_seen["Prussia"] = "hanoverian_prize|ask"
        assert process_intent_movements(world) == []
        assert world.nation_intent_seen["Prussia"] == (
            "revanche_prussia|fight")

    def test_survival_stays_silent(self, world, monkeypatch):
        """The Knife at the Throat belongs to the crisis machinery."""
        process_intent_movements(world)
        _patch_views(monkeypatch, {
            "Prussia": _view("Prussia", want="survival", price="fight",
                             weight=95, survival=True)})
        world.nation_intent_seen["Prussia"] = "hanoverian_prize|ask"
        assert process_intent_movements(world) == []
        assert "Prussia" not in world.nation_intent_seen

    def test_unchanged_rung_stays_quiet(self, world):
        process_intent_movements(world)
        assert process_intent_movements(world) == []


class TestTheCap:
    def _four_movers(self, world, monkeypatch):
        """Two France-concerned courts at MODEST weight, two far courts
        at HIGHER raw weight — relevance must beat raw weight or the
        §4.6 rule ('weight alone cannot tell them apart') is dead.
        Denmark and the Ottoman border no member of France's boot bloc
        (Sweden would NOT do here — Swedish Pomerania sits on the German
        coast and earns the border multiplier); Prussia and Austria are
        patched to aim at France itself."""
        views = {
            "Prussia": _view("Prussia", want="hanoverian_prize",
                             price="coerce", weight=50,
                             against="France"),
            "Austria": _view("Austria", want="redeem_italy",
                             price="coerce", weight=48,
                             against="France"),
            "Denmark": _view("Denmark", want="baltic_mastery",
                             price="coerce", weight=90,
                             against="Russia"),
            "Ottoman": _view("Ottoman", want="danube_quarrel",
                             price="coerce", weight=88,
                             against="Russia"),
        }
        _patch_views(monkeypatch, views)
        world.nation_intent_seen.update({
            "Prussia": "hanoverian_prize|align",
            "Austria": "redeem_italy|align",
            "Denmark": "baltic_mastery|align",
            "Ottoman": "danube_quarrel|align",
        })
        return views

    def test_cap_two_lines_plus_one_tail(self, world, monkeypatch):
        process_intent_movements(world)
        self._four_movers(world, monkeypatch)
        events = process_intent_movements(world)
        lines = [e for e in events if e["type"] == "intent_hardens"]
        tails = [e for e in events if e["type"] == "intent_movement_tail"]
        assert len(lines) == INTENT_DISPATCH_CAP == 2
        assert len(tails) == 1 and tails[0]["count"] == 2
        queued_tail = _tail_events(world)
        assert queued_tail[0]["template_vars"]["count"] == "2"

    def test_relevance_beats_raw_weight(self, world, monkeypatch):
        """The Prussian design on Hanover outranks the Danube quarrel
        even at 40 points less raw weight — proximity to French
        interest is the tiebreaker the §4.6 rule demands."""
        process_intent_movements(world)
        self._four_movers(world, monkeypatch)
        events = process_intent_movements(world)
        chosen = {e["nation"] for e in events
                  if e["type"] == "intent_hardens"}
        assert chosen == {"Prussia", "Austria"}

    def test_single_overflow_tail_grammar(self, world, monkeypatch):
        process_intent_movements(world)
        views = {
            "Prussia": _view("Prussia", want="a", price="coerce",
                             weight=80, against="France"),
            "Austria": _view("Austria", want="b", price="coerce",
                             weight=70, against="France"),
            "Sweden": _view("Sweden", want="c", price="coerce",
                            weight=20, against="Russia"),
        }
        _patch_views(monkeypatch, views)
        world.nation_intent_seen.update({
            "Prussia": "a|align", "Austria": "b|align",
            "Sweden": "c|align"})
        process_intent_movements(world)
        tail = _tail_events(world)[0]["template_vars"]
        assert tail == {"count": "1", "plural": "", "verb": "s",
                        "poss": "its"}

    def test_no_tail_when_under_the_cap(self, world, monkeypatch):
        process_intent_movements(world)
        _patch_views(monkeypatch, {
            "Prussia": _view("Prussia", want="a", price="coerce",
                             weight=80, against="France")})
        world.nation_intent_seen["Prussia"] = "a|align"
        process_intent_movements(world)
        assert _tail_events(world) == []


class TestTheExemption:
    def test_beats_are_never_capped_or_collapsed(self, world,
                                                 monkeypatch):
        """The never-collapsed pin: a turn with FIVE queued beats and
        four routine movements shows every beat untouched — the cap
        spends only the routine budget. Includes Stage E's pair per the
        §18.1 handoff."""
        from backend.game_logic.dispatch import queue_dispatch_event
        process_intent_movements(world)
        beats = [
            ("crisis_brewing", {"nation": "Prussia", "target": "Hanover",
                                "instruments": "compensate"}),
            ("coercive_demand", {"nation": "Prussia",
                                 "target": "Hanover"}),
            ("crisis_passed", {"nation": "Prussia", "target": "Hanover",
                               "cause": "bought off"}),
            ("design_promoted", {"nation": "Prussia", "author": "Austria",
                                 "province_line": "Silesia"}),
            ("volte_face", {"nation": "Russia", "partner": "France",
                            "gaze": "Her court turns east."}),
        ]
        for event_type, vars_ in beats:
            queue_dispatch_event(world, event_type, vars_, "always")
        TestTheCap._four_movers(TestTheCap(), world, monkeypatch)
        process_intent_movements(world)
        queued_types = [e["type"] for e in world.pending_dispatch_events]
        for event_type, _vars in beats:
            assert queued_types.count(event_type) == 1, (
                f"{event_type} must survive the cap untouched")
        assert queued_types.count("intent_hardens") == 2
        assert queued_types.count("intent_movement_tail") == 1

    def test_exempt_tuple_carries_the_stage_e_pair(self):
        """§18.1 handoff, pinned: the cap machinery's exemption registry
        enumerates design_promoted and volte_face beside the beats."""
        assert "design_promoted" in NARRATION_EXEMPT_EVENT_TYPES
        assert "volte_face" in NARRATION_EXEMPT_EVENT_TYPES
        for beat in ("crisis_brewing", "coercive_demand", "crisis_passed",
                     "broken_bargain", "third_party_peace",
                     "guarantee_called", "agenda_shift"):
            assert beat in NARRATION_EXEMPT_EVENT_TYPES

    def test_collapse_target_is_exactly_the_movement_family(self):
        """Structural half of never-collapsed: nothing in the exempt
        tuple is a movement type, and the movement types are not
        exempt-listed (they are the cap's ONLY subjects)."""
        for movement_type in ("intent_hardens", "intent_eases",
                              "intent_movement_tail"):
            assert movement_type not in NARRATION_EXEMPT_EVENT_TYPES


class TestSerializationAndScoping:
    def test_seen_map_round_trips(self, world):
        process_intent_movements(world)
        restored = WorldState.from_dict(world.to_dict())
        assert restored.nation_intent_seen == world.nation_intent_seen
        # And the reload does not burst: same state, no lines.
        assert process_intent_movements(restored) == []

    def test_pre_stage_f_save_reads_empty(self, world):
        payload = world.to_dict()
        payload.pop("nation_intent_seen", None)
        restored = WorldState.from_dict(payload)
        assert restored.nation_intent_seen == {}

    def test_legacy_world_is_silent(self):
        legacy = WorldState()
        assert process_intent_movements(legacy) == []
        assert legacy.nation_intent_seen == {}

    def test_registration_complete(self):
        """Template + priority drift pins for the three new dispatch
        types (an unregistered type renders empty — the CLAUDE.md
        recurring bug)."""
        from backend.game_logic.dispatch import (
            _DIPLOMATIC_EVENT_PRIORITY,
            _DIPLOMATIC_EVENT_TEMPLATES,
        )
        for event_type in ("intent_hardens", "intent_eases",
                           "intent_movement_tail"):
            assert event_type in _DIPLOMATIC_EVENT_TEMPLATES
            assert event_type in _DIPLOMATIC_EVENT_PRIORITY

    def test_cap_is_the_blessed_two(self):
        """Blessed number (in-band tunable — flipping this pin is the
        conscious act the standing rule demands)."""
        assert INTENT_DISPATCH_CAP == 2


class TestTempo:
    def test_one_foregrounded_crisis_worldwide(self, world, monkeypatch):
        """AI-6b's tempo rule, pinned FRESH at the war council (no prior
        test asserted it): with two LIVE open crises — both courts held
        at `fight` so neither cools as satisfied/starved during the poll
        — only ONE is foregrounded after the promotion pass, and it is
        the OLDEST. The §4.6a failure mode ('four simultaneous crises
        reading as noise') stays structurally impossible."""
        _patch_views(monkeypatch, {
            "Prussia": _view("Prussia", want="hanoverian_prize",
                             price="fight", weight=90,
                             against="Hanover"),
            "Austria": _view("Austria", want="redeem_italy",
                             price="fight", weight=90,
                             against="Hanover"),
        })
        world.war_intents = {
            "Prussia": {
                "coveter": "Prussia", "target": "Hanover",
                "design_id": "hanoverian_prize", "want_title": "The Prize",
                "opened_turn": int(world.current_turn) - 3,
                "foregrounded": False, "foregrounded_turn": None,
                "coerce_recorded_turn": None, "treaty_broken_turn": None,
            },
            "Austria": {
                "coveter": "Austria", "target": "Hanover",
                "design_id": "redeem_italy", "want_title": "Redeem Italy",
                "opened_turn": int(world.current_turn) - 1,
                "foregrounded": False, "foregrounded_turn": None,
                "coerce_recorded_turn": None, "treaty_broken_turn": None,
            },
        }
        from backend.game_logic.war_council import process_war_council
        process_war_council(world)
        foregrounded = [coveter for coveter, record
                        in world.war_intents.items()
                        if record.get("foregrounded")]
        assert foregrounded == ["Prussia"], (
            "one foregrounded crisis at a time, world-wide — and the "
            "oldest waits the shortest")
