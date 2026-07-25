"""IGR-B — the campaign log becomes readable.

`docs/INGAME_REVIEW_FIXES_SPEC.md` §2 IGR-B, gate record §5 Q1 option (a):
aggregate the court-to-court refusal family at the VIEW layer, keyed
`(turn, proposal_type)`.

The defect, measured deterministically (20 ambient turns, `historical`
seed, zero player actions): the burst turn's page carried 26 rows of which
23 were `ai_ai_proposal_refused`, burying that turn's `agenda_shift` — the
one dramatic line — at index 25 of 26. After the collapse the same page is
5 rows and the shift sits at index 4.

Two hazards this file exists to pin, both found by reproducing them by
hand before the code was written:

  1. **Save corruption.** `filter_campaign_log` returns the *originals,
     not copies* — the very dicts in `world.event_log`, which
     `WorldState.to_dict` serializes. Stamping `collapsed_count` in place
     would bake view state into every save from that moment on.
  2. **The bare key eats the player's own diplomacy.**
     `(turn, proposal_type)` is not unique to refusals:
     `diplomatic_proposal_sent`, `proposal_arrived` and `offer_lapsed`
     carry a `proposal_type` from the same vocabulary and all take an
     "always show" branch. Measured: `offer_lapsed` lands on turn 3 — the
     burst turn itself.

And the standing constraint: the refusal RECORD is AI-3's ladder-gate
substrate (`war_council` reads `get_refused_asks`), so nothing here may
touch the producer. View layer only.
"""

import copy
import json

from backend.campaign_log import (
    CAMPAIGN_LOG_TYPES,
    collapse_refusal_family,
    filter_campaign_log,
    format_event_oneliner,
)
from backend.models.intel import FULL
from backend.models.world_state import WorldState


REFUSAL = "ai_ai_proposal_refused"


def _refusal(proposer, refused_by, turn=3, ptype="open_borders"):
    """A producer-shaped refusal event (the exact 6 keys both sites write)."""
    return {
        "type": REFUSAL,
        "proposer": proposer,
        "recipient": refused_by,
        "refused_by": refused_by,
        "proposal_type": ptype,
        "turn": turn,
    }


# ════════════════════════════════════════════════════════════
# THE PURE FUNCTION
# ════════════════════════════════════════════════════════════

class TestCollapseShape:

    def test_empty_input(self):
        assert collapse_refusal_family([]) == []
        assert collapse_refusal_family(None) == []

    def test_lone_refusal_passes_through_byte_identical(self):
        """A bucket of one keeps its own line — and its own object."""
        event = _refusal("Austria", "Prussia")
        out = collapse_refusal_family([event])
        assert len(out) == 1
        assert out[0] is event
        assert "collapsed_count" not in out[0]

    def test_burst_becomes_one_row_at_the_first_members_index(self):
        events = [
            {"type": "battle", "turn": 3},
            _refusal("Austria", "Prussia"),
            _refusal("Austria", "Bavaria"),
            _refusal("Austria", "Saxony"),
            {"type": "agenda_shift", "turn": 3},
        ]
        out = collapse_refusal_family(events)
        assert [e["type"] for e in out] == ["battle", REFUSAL, "agenda_shift"]
        assert out[0] is events[0]          # untouched neighbours
        assert out[2] is events[4]
        assert out[1]["collapsed_count"] == 3
        assert out[1]["collapsed_pairs"] == [
            {"proposer": "Austria", "refused_by": "Prussia"},
            {"proposer": "Austria", "refused_by": "Bavaria"},
            {"proposer": "Austria", "refused_by": "Saxony"},
        ]

    def test_the_dramatic_line_rises_to_the_top_of_the_page(self):
        """The whole point: the agenda_shift stops being row 25 of 26."""
        events = [_refusal("Austria", f"Court{i}") for i in range(23)]
        events.append({"type": "agenda_shift", "turn": 3})
        before = events.index(events[-1])
        out = collapse_refusal_family(events)
        after = [e["type"] for e in out].index("agenda_shift")
        assert before == 23
        assert after == 1
        assert len(out) == 2

    def test_distinct_turns_never_merge(self):
        events = [_refusal("Austria", "Prussia", turn=t) for t in (3, 3, 4, 4)]
        out = collapse_refusal_family(events)
        assert len(out) == 2
        assert [e["turn"] for e in out] == [3, 4]
        assert [e["collapsed_count"] for e in out] == [2, 2]

    def test_distinct_proposal_types_never_merge(self):
        events = [
            _refusal("Austria", "Prussia", ptype="open_borders"),
            _refusal("Austria", "Bavaria", ptype="open_borders"),
            _refusal("Austria", "Saxony", ptype="defensive_alliance"),
            _refusal("Austria", "Hesse", ptype="defensive_alliance"),
        ]
        out = collapse_refusal_family(events)
        assert len(out) == 2
        assert [e["proposal_type"] for e in out] == [
            "open_borders", "defensive_alliance"]

    def test_degrades_to_the_number_of_types(self):
        """Measured max on the ambient run is 2 types on a burst turn."""
        events = []
        for ptype in ("open_borders", "defensive_alliance", "non_aggression"):
            events += [_refusal("Austria", f"C{i}", ptype=ptype)
                       for i in range(9)]
        out = collapse_refusal_family(events)
        assert len(out) == 3

    def test_order_is_preserved(self):
        events = [
            {"type": "battle", "turn": 3},
            _refusal("Austria", "Prussia"),
            {"type": "conquest", "turn": 3},
            _refusal("Austria", "Bavaria"),
            {"type": "agenda_shift", "turn": 3},
        ]
        out = collapse_refusal_family(events)
        assert [e["type"] for e in out] == [
            "battle", REFUSAL, "conquest", "agenda_shift"]

    def test_non_dict_entries_survive(self):
        events = ["junk", _refusal("Austria", "Prussia")]
        out = collapse_refusal_family(events)
        assert out[0] == "junk"


class TestNeverMutatesTheModel:
    """Hazard 1 — `filter_campaign_log` hands back the live save objects."""

    def test_input_dicts_gain_no_keys(self):
        events = [_refusal("Austria", "Prussia"),
                  _refusal("Austria", "Bavaria")]
        snapshot = copy.deepcopy(events)
        collapse_refusal_family(events)
        assert events == snapshot

    def test_the_collapsed_row_is_a_new_object(self):
        events = [_refusal("Austria", "Prussia"),
                  _refusal("Austria", "Bavaria")]
        out = collapse_refusal_family(events)
        assert out[0] is not events[0]
        assert "collapsed_count" not in events[0]

    def test_collapsed_pairs_is_a_fresh_list(self):
        """A nested value shared with the model would still reach the save."""
        events = [_refusal("Austria", "Prussia"),
                  _refusal("Austria", "Bavaria")]
        out = collapse_refusal_family(events)
        out[0]["collapsed_pairs"].append({"proposer": "X", "refused_by": "Y"})
        assert all("collapsed_pairs" not in e for e in events)

    def test_world_event_log_survives_the_whole_view_pipeline(self):
        """The end-to-end gate: filter -> collapse leaves the log pristine."""
        world = WorldState()
        world.event_log.extend([
            _refusal("Austria", "Prussia"),
            _refusal("Austria", "Bavaria"),
            {"type": "battle", "turn": 3, "nation": world.player_nation},
        ])
        snapshot = copy.deepcopy(world.event_log)
        ids = [id(e) for e in world.event_log]

        collapse_refusal_family(filter_campaign_log(world.event_log, world))

        assert world.event_log == snapshot
        assert [id(e) for e in world.event_log] == ids
        assert "collapsed_count" not in json.dumps(world.to_dict())


class TestTheBareKeyWouldEatPlayerDiplomacy:
    """Hazard 2 — gate on the event TYPE, not on `(turn, proposal_type)`."""

    def test_the_players_own_proposal_is_never_bucketed(self):
        events = [
            {"type": "diplomatic_proposal_sent", "target": "Prussia",
             "proposal_type": "non_aggression", "turn": 3},
            _refusal("Bavaria", "Hesse", ptype="non_aggression"),
            _refusal("Bavaria", "Baden", ptype="non_aggression"),
        ]
        out = collapse_refusal_family(events)
        assert len(out) == 2
        assert out[0] is events[0]                    # survived untouched
        assert out[0]["type"] == "diplomatic_proposal_sent"
        assert out[1]["collapsed_count"] == 2

    def test_offer_lapsed_and_proposal_arrived_survive_the_burst_turn(self):
        """Both were measured live on turn 3 — the burst turn itself."""
        events = [
            _refusal("Bavaria", "Hesse", ptype="non_aggression"),
            {"type": "offer_lapsed", "nation": "Russia",
             "offer_type": "x", "proposal_type": "non_aggression", "turn": 3},
            {"type": "proposal_arrived", "nation": "Austria",
             "proposal_type": "non_aggression", "turn": 3},
            _refusal("Bavaria", "Baden", ptype="non_aggression"),
        ]
        out = collapse_refusal_family(events)
        assert [e["type"] for e in out] == [
            REFUSAL, "offer_lapsed", "proposal_arrived"]
        assert out[0]["collapsed_count"] == 2

    def test_two_non_refusals_sharing_the_key_are_both_kept(self):
        """Reproduced by hand pre-build: a bare key merged and deleted one."""
        events = [
            {"type": "diplomatic_proposal_sent",
             "proposal_type": "non_aggression", "turn": 3},
            {"type": "offer_lapsed",
             "proposal_type": "non_aggression", "turn": 3},
        ]
        out = collapse_refusal_family(events)
        assert len(out) == 2


# ════════════════════════════════════════════════════════════
# THE SENTENCE
# ════════════════════════════════════════════════════════════

def _line(pairs, ptype="open_borders"):
    events = [_refusal(p, r, ptype=ptype) for p, r in pairs]
    return format_event_oneliner(collapse_refusal_family(events)[0])


class TestCollapsedLine:

    def test_uncollapsed_arm_is_byte_identical(self):
        """The lone-refusal sentence must not move — it is pinned elsewhere."""
        line = format_event_oneliner(_refusal("Austria", "Prussia",
                                              ptype="defensive_alliance"))
        assert line == "Prussia rebuffs Austria (defensive alliance)"

    def test_a_count_of_one_never_renders_the_aggregate(self):
        event = dict(_refusal("Austria", "Prussia"), collapsed_count=1)
        assert format_event_oneliner(event) == (
            "Prussia rebuffs Austria (open borders)")

    def test_one_proposer_many_refusers(self):
        """The story: 'N courts rebuff X'. Measured live on turns 5, 6, 12."""
        line = _line([("Prussia", "Baden"), ("Prussia", "Hesse"),
                      ("Prussia", "Saxony")])
        assert line == "3 courts rebuff Prussia (open borders)"

    def test_one_refuser_many_proposers(self):
        """Measured live on turns 2 and 13."""
        line = _line([("Baden", "Britain"), ("Hesse", "Britain"),
                      ("Saxony", "Britain")])
        assert line == "Britain rebuffs 3 courts (open borders)"

    def test_few_proposers_are_named(self):
        """Measured live on turn 3 — the burst turn."""
        line = _line([("Prussia", "Baden"), ("Prussia", "Hesse"),
                      ("Bavaria", "Saxony"), ("Bavaria", "Hanover")])
        assert line == ("4 approaches from Prussia and Bavaria "
                        "are rebuffed (open borders)")

    def test_three_proposers_use_the_oxford_join(self):
        line = _line([("Prussia", "Baden"), ("Bavaria", "Hesse"),
                      ("Saxony", "Hanover"), ("Saxony", "Naples")])
        assert line == ("4 approaches from Prussia, Bavaria and Saxony "
                        "are rebuffed (open borders)")

    def test_many_proposers_fall_back_to_the_anonymous_count(self):
        pairs = [(f"P{i}", f"R{i}") for i in range(6)]
        line = _line(pairs)
        assert line == "6 approaches rebuffed among the courts (open borders)"

    def test_the_count_is_always_stated(self):
        """The turn header now shows the collapsed row count, so a sentence
        that hid the number would delete history silently."""
        for pairs in (
            [("Prussia", "Baden"), ("Prussia", "Hesse")],
            [("Baden", "Britain"), ("Hesse", "Britain")],
            [("Prussia", "Baden"), ("Bavaria", "Hesse")],
            [(f"P{i}", f"R{i}") for i in range(6)],
        ):
            assert any(ch.isdigit() for ch in _line(pairs))

    def test_the_proposal_type_is_always_named(self):
        line = _line([("Prussia", "Baden"), ("Prussia", "Hesse")],
                     ptype="defensive_alliance")
        assert "(defensive alliance)" in line

    def test_raw_nation_tags_are_preserved(self):
        """The client repairs tags via `humanize_nation_keys_in_text`, and the
        NA-6 formation overrides can only rename a still-raw tag. Baking
        `display_nation` prose here is the §11.8 stage-3 hazard IGR-A hit."""
        line = _line([("KingdomOfItaly", "PapalStates"),
                      ("KingdomOfItaly", "Naples")])
        assert "KingdomOfItaly" in line
        assert "Kingdom of Italy" not in line


# ════════════════════════════════════════════════════════════
# THE ENDPOINT
# ════════════════════════════════════════════════════════════

def _world_with_a_visible_burst(n=23):
    """A world whose refusal burst survives the fog filter.

    The refusal branch needs PARTIAL+ on a named party, resolved through
    each nation's marshal locations, so intel is set there.
    """
    world = WorldState()
    for marshal in world.marshals.values():
        world.get_region_intel(marshal.location).visibility = FULL
    # Austria is the common proposer, so its own marshals carry the
    # PARTIAL+ visibility every pair in the burst is filtered on.
    assert any(m.nation == "Austria" for m in world.marshals.values()), (
        "fixture world must field an Austrian marshal")
    world.event_log.extend(
        [_refusal("Austria", f"Court{i}") for i in range(n)])
    world.event_log.append({"type": "agenda_shift", "turn": 3,
                            "nation": "Austria",
                            "want_title": "The Gulf and the Straits"})
    return world


class TestEndpoint:

    def _get(self, world):
        import backend.main as main_mod
        prev_world, prev_state = main_mod.world, main_mod.game_state["world"]
        main_mod.world = world
        main_mod.game_state["world"] = world
        try:
            return main_mod.get_campaign_log()
        finally:
            main_mod.world = prev_world
            main_mod.game_state["world"] = prev_state

    def test_the_burst_page_collapses(self):
        world = _world_with_a_visible_burst()
        raw = [e for e in filter_campaign_log(world.event_log, world)
               if e.get("turn") == 3]
        assert sum(1 for e in raw if e["type"] == REFUSAL) == 23, (
            "fixture must reproduce a real burst")

        payload = self._get(world)
        page = next(t for t in payload["turns"] if t["turn"] == 3)["events"]
        assert sum(1 for e in page if e["type"] == REFUSAL) == 1
        assert len(page) <= 5

    def test_the_dramatic_line_is_visible_without_scrolling(self):
        world = _world_with_a_visible_burst()
        payload = self._get(world)
        page = next(t for t in payload["turns"] if t["turn"] == 3)["events"]
        idx = [e["type"] for e in page].index("agenda_shift")
        assert idx < 5

    def test_the_payload_carries_the_display_only_keys(self):
        world = _world_with_a_visible_burst()
        payload = self._get(world)
        page = next(t for t in payload["turns"] if t["turn"] == 3)["events"]
        row = next(e for e in page if e["type"] == REFUSAL)
        assert row["collapsed_count"] == 23
        assert len(row["collapsed_pairs"]) == 23

    def test_the_rendered_display_states_the_count(self):
        world = _world_with_a_visible_burst()
        payload = self._get(world)
        page = next(t for t in payload["turns"] if t["turn"] == 3)["events"]
        row = next(e for e in page if e["type"] == REFUSAL)
        assert row["display"] == "23 courts rebuff Austria (open borders)"

    def test_the_endpoint_does_not_touch_the_model(self):
        world = _world_with_a_visible_burst()
        snapshot = copy.deepcopy(world.event_log)
        ids = [id(e) for e in world.event_log]
        refusals = copy.deepcopy(world.diplomatic_refusals)
        length = len(world.event_log)

        self._get(world)

        assert world.event_log == snapshot
        assert [id(e) for e in world.event_log] == ids
        assert len(world.event_log) == length
        assert world.diplomatic_refusals == refusals

    def test_a_save_taken_after_viewing_carries_no_view_state(self):
        world = _world_with_a_visible_burst()
        self._get(world)
        dumped = json.dumps(world.to_dict())
        assert "collapsed_count" not in dumped
        assert "collapsed_pairs" not in dumped


# ════════════════════════════════════════════════════════════
# THE CONTRACTS THE SLICE MUST NOT BREAK
# ════════════════════════════════════════════════════════════

class TestContracts:

    def test_no_new_event_type(self):
        assert len(CAMPAIGN_LOG_TYPES) == 140

    def test_the_collapse_is_not_inside_the_filter(self):
        """51 test call sites depend on `filter_campaign_log`'s contract."""
        world = _world_with_a_visible_burst()
        raw = [e for e in filter_campaign_log(world.event_log, world)
               if e.get("type") == REFUSAL]
        assert len(raw) == 23
        assert all("collapsed_count" not in e for e in raw)

    def test_the_ai3_ladder_gate_is_untouched(self):
        """The refusal RECORD is AI-3's substrate; the view never reaches it."""
        from backend.game_logic.war_council import _ladder_climbed
        world = _world_with_a_visible_burst()
        courts = list(world.enemy_nations)[:5]
        before = [_ladder_climbed(world, a, b)
                  for a in courts for b in courts if a != b]

        collapse_refusal_family(filter_campaign_log(world.event_log, world))

        after = [_ladder_climbed(world, a, b)
                 for a in courts for b in courts if a != b]
        assert before == after

    def test_the_producer_record_is_not_written_by_the_view(self):
        world = _world_with_a_visible_burst()
        before = copy.deepcopy(world.diplomatic_refusals)
        collapse_refusal_family(filter_campaign_log(world.event_log, world))
        assert world.diplomatic_refusals == before
