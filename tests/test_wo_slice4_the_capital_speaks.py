"""WO slice 4 — "The Capital Speaks" (WEIRD_OUTCOMES_SPEC §3 slice 4).

The defect, measured on the real 1805 board before a line was written.
Four French homeland provinces lost on one turn, Soult taken prisoner,
every event stamped `captured_from: France` — the page depended entirely
on which order the captures happened to reach the log, and two of the
three orderings were wrong::

    Paris logged FIRST
      LEAD  Sire - Paris has fallen. Enemy colours fly over French homeland soil.
       sub  Sire - Limousin has fallen. Enemy colours fly over French homeland soil.
       sub  Sire - Berry has fallen. Enemy colours fly over French homeland soil.
      Paris on page? True   Soult on page? False

    Paris logged LAST                      <- the crowding case
      LEAD  Sire - Limousin has fallen. Enemy colours fly over French homeland soil.
       sub  Sire - Berry has fallen. Enemy colours fly over French homeland soil.
       sub  Sire - Normandy has fallen. Enemy colours fly over French homeland soil.
      Paris on page? FALSE  Soult on page? False

Four candidates at one weight, a stable sort, three slots. The fall of the
capital was not merely narrated like Limousin — on that ordering it was
not narrated at all, and Soult, at weight 95, reached the page in NO
ordering whatever.

Two more, measured the same way:

  * an ALLY liberating Paris from Austria printed "Sire - Paris has
    fallen. Enemy colours fly over French homeland soil." (WO-11: the
    class had no direction guard, while its own sibling arm two lines
    below has always had one);
  * `gazette._special_reason` captioned the fall of our own capital
    "a capital stormed" — the victor's phrase, in the loser's newspaper.

Five things land together (spec §3 slice 4). The two that are easy to get
wrong, and are pinned hardest here:

  * the diverse tail is a PREFERENCE, not a per-class collapse. The naive
    "one beat per class" reds CA8-5's own falsifiable negative — two
    different marshals broken on one turn are two pieces of news — so the
    rule only reorders what is already eligible and falls back when no
    fresh class exists. `TestTheTailNeverSwallowsDistinctNews` is that
    guard, and the three CA8 pins named in spec §2 D-10 stay green.
  * the direction guard must not suppress a REAL loss. Every one of the
    six production `region_captured` producers stamps `captured_from`
    from `region.controller` read immediately before `capture_region()`
    (world_state `mount_or_auto_secure_capture` + the occupation pair,
    capture_executor's plunder/secure answers, combat_executor's
    `_apply_ai_capture_choice`), so the positive guard is safe —
    `TestTheWoundStillFiresWhenItIsReal` is the negative that proves it.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from backend.campaign_log import CAMPAIGN_LOG_TYPES
from backend.game_logic import dispatch as dispatch_mod
from backend.game_logic import gazette as gazette_mod
from backend.game_logic.dispatch import (
    HEADLINE_WEIGHTS,
    SUB_BEAT_SLOTS,
    _build_headline,
    build_morning_dispatch,
)
from backend.models.world_state import WorldState

from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)

# The measured turn (see the module docstring). Four homeland provinces,
# one of them the capital, plus a marshal taken.
T_LOST = ["Paris", "Limousin", "Berry", "Normandy"]


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _capture(world, region, by="Austria", frm="France", turn=None):
    world.log_event({
        "type": "region_captured",
        "turn": world.current_turn if turn is None else turn,
        "region": region, "captured_by": by, "captured_from": frm,
        "method": "secure",
    })


def _take_marshal(world, name="Soult", nation="France", captor="Austria"):
    world.log_event({
        "type": "marshal_captured", "turn": world.current_turn,
        "marshal": name, "nation": nation, "captor": captor,
    })


def _page(head):
    return head["text"] + " || " + " || ".join(head["sub_beats"])


# ════════════════════════════════════════════════════════════════════════
# 1. The capital gets its own voice, and its own rank
# ════════════════════════════════════════════════════════════════════════

class TestTheCapitalLeads:

    def test_the_measured_turn_now_leads_with_the_capital(self, world):
        world.current_turn = 12
        for r in T_LOST:
            _capture(world, r)
        _take_marshal(world)
        head = _build_headline(world, "France")
        assert head["class"] == "capital_lost", head
        assert "Paris HAS FALLEN" in head["text"], head["text"]
        assert "Austria" in head["text"], head["text"]

    @pytest.mark.parametrize("order", [
        ["Paris", "Limousin", "Berry", "Normandy"],
        ["Limousin", "Berry", "Normandy", "Paris"],   # the crowding case
        ["Limousin", "Paris", "Berry", "Normandy"],
    ], ids=["paris-first", "paris-last", "paris-second"])
    def test_the_page_no_longer_depends_on_the_order_of_the_log(
            self, world1805, order):
        """The measured defect in one assertion: with four candidates at
        one weight the page was decided by log order, and Paris fell off
        it entirely when it happened to be logged last."""
        world = WorldState.from_dict(world1805.to_dict())
        world.current_turn = 12
        for r in order:
            _capture(world, r)
        _take_marshal(world)
        head = _build_headline(world, "France")
        assert head["class"] == "capital_lost", (order, head)
        assert "Paris" in _page(head), (order, head)

    def test_the_shape_of_the_page_is_order_independent(self, world1805):
        """What the slice actually guarantees, stated honestly. The first
        draft of this test asserted the page was md5-identical across
        orderings and FAILED on the third one: which of three equal-weight
        province losses fills the MIDDLE slot still follows the log, and
        nothing in this slice changes that (nor should it — they are
        genuinely equal news). What is now invariant is the part that was
        broken: the lead, and the KINDS of news that reach the page."""
        shapes, leads, digests = set(), set(), set()
        for order in (T_LOST, list(reversed(T_LOST)),
                      ["Limousin", "Paris", "Normandy", "Berry"],
                      ["Normandy", "Limousin", "Paris", "Berry"]):
            w = WorldState.from_dict(world1805.to_dict())
            w.current_turn = 12
            for r in order:
                _capture(w, r)
            _take_marshal(w)
            head = _build_headline(w, "France")
            shapes.add((head["class"],) + tuple(
                "marshal" if "Marshal" in b else "province"
                for b in head["sub_beats"]))
            leads.add(head["text"])
            assert "Soult" in _page(head), (order, head)
            digests.add(hashlib.md5(
                _page(head).encode("utf-8")).hexdigest())
        assert shapes == {("capital_lost", "province", "marshal")}, shapes
        assert len(leads) == 1, leads
        # ...and the honest limit, pinned so nobody later "fixes" it by
        # accident and calls it a regression: the middle slot still varies.
        assert len(digests) > 1, digests

    def test_the_ordering_pin_including_the_top_of_the_table(self):
        """Spec §2 D-5 / §4 N-3: the eval's D6 reasoning never mentioned
        `sovereign_captured`, and NP-4's ruling — the Eagle in Chains
        outranks even a fallen homeland province — stays intact ABOVE the
        new class."""
        w = HEADLINE_WEIGHTS
        assert w["sovereign_captured"] == 101
        assert w["capital_lost"] == 100
        assert w["home_captured"] == 99
        assert w["marshal_destroyed"] == 96
        assert w["marshal_captured"] == 95
        assert (w["sovereign_captured"] > w["capital_lost"]
                > w["home_captured"] > w["marshal_destroyed"]
                > w["marshal_captured"])

    def test_the_sovereign_still_outranks_the_capital(self, world):
        """The person before the place — NP-4, as behaviour."""
        world.current_turn = 12
        _capture(world, "Paris")
        world.log_event({
            "type": "marshal_captured", "turn": 12, "marshal": "Napoleon",
            "nation": "France", "captor": "Austria", "sovereign": True,
        })
        head = _build_headline(world, "France")
        assert head["class"] == "sovereign_captured", head
        # ...and the capital is still told, one line down.
        assert "Paris HAS FALLEN" in " ".join(head["sub_beats"]), head

    def test_an_ordinary_homeland_province_still_reads_home_captured(
            self, world):
        """The falsifiable negative for the split: `home_captured` must
        still exist and still fire for soil that is not the capital."""
        world.current_turn = 12
        _capture(world, "Limousin")
        head = _build_headline(world, "France")
        assert head["class"] == "home_captured", head
        assert head["weight"] == 99


# ════════════════════════════════════════════════════════════════════════
# 2. Structural, never the word "Paris"
# ════════════════════════════════════════════════════════════════════════

class TestThePredicateIsStructural:

    def test_the_class_follows_the_capital_map_not_the_name(self, world):
        """Move France's capital and the ceremony moves with it. This is
        the whole of contract item 2: a scenario whose player capital is
        not Paris — a formed nation, a carved client, a mod — gets the
        same sentence about its own seat."""
        world.current_turn = 12
        world.nation_capitals["France"] = "Berry"
        _capture(world, "Berry")
        _capture(world, "Paris")
        head = _build_headline(world, "France")
        assert head["class"] == "capital_lost", head
        assert "Berry HAS FALLEN" in head["text"], head["text"]
        # Paris is now just another homeland province, and says so.
        assert any("Paris has fallen" in b for b in head["sub_beats"]), head

    def test_a_capital_outside_the_starting_regions_still_fires(self, world):
        """The arm is read OUTSIDE the `home_regions` branch on purpose —
        a formed or carved state's capital need not be a starting region,
        and nesting it would have made the class unreachable there."""
        world.current_turn = 12
        assert "Rome" not in (world.nation_starting_regions.get("France") or [])
        world.nation_capitals["France"] = "Rome"
        _capture(world, "Rome")
        head = _build_headline(world, "France")
        assert head["class"] == "capital_lost", head

    def test_a_world_with_no_capital_for_the_player_does_not_crash(
            self, world):
        world.current_turn = 12
        world.nation_capitals.pop("France", None)
        _capture(world, "Limousin")
        head = _build_headline(world, "France")
        assert head["class"] == "home_captured", head

    def test_the_source_of_the_arm_names_no_province(self):
        """A source census, because a behavioural test cannot tell a
        structural read from a lucky literal."""
        import inspect
        src = inspect.getsource(dispatch_mod._build_headline)
        arm = src.split("_own_capital = ", 1)[1].split("elif _ours_to_lose", 1)[0]
        assert "get_nation_capital(player_nation)" in arm
        assert "Paris" not in arm, arm

    def test_it_works_on_the_legacy_world_too(self):
        """Most of the suite builds the 19-region fixture world; the new
        arm must not misfire or crash there. Its France capital IS Paris,
        which is why two W6 pins were consciously retargeted off it."""
        w = WorldFactory.basic()
        assert w.get_nation_capital("France") == "Paris"
        w.event_log = [{
            "type": "region_captured", "region": "Paris",
            "captured_by": "Prussia", "captured_from": "France",
            "turn": w.current_turn - 1,
        }]
        head = _build_headline(w, "France")
        assert head["class"] == "capital_lost", head


# ════════════════════════════════════════════════════════════════════════
# 3. WO-11 — the wound has a direction
# ════════════════════════════════════════════════════════════════════════

class TestAnAllyLiberatingIsNotAWound:

    def test_an_ally_retaking_the_capital_fires_nothing(self, world):
        """The measured line: Spain retaking Paris from Austria printed
        "Sire - Paris has fallen. Enemy colours fly over French homeland
        soil." — the game's most ceremonial wound, as a rescue's reward."""
        world.current_turn = 20
        _capture(world, "Paris", by="Spain", frm="Austria")
        assert _build_headline(world, "France") is None

    def test_an_ally_retaking_an_ordinary_homeland_province_fires_nothing(
            self, world):
        world.current_turn = 20
        _capture(world, "Limousin", by="Spain", frm="Austria")
        assert _build_headline(world, "France") is None

    def test_soil_changing_hands_between_two_enemies_is_not_a_fresh_wound(
            self, world):
        """We already lost it. It is not lost again because the flag over
        it changed — which is what "the player's side LOST it" means."""
        world.current_turn = 20
        _capture(world, "Berry", by="Russia", frm="Austria")
        assert _build_headline(world, "France") is None


class TestTheWoundStillFiresWhenItIsReal:
    """The dangerous direction. A guard that suppressed a real capital
    loss would be far worse than the bug it fixes, so each production
    shape of "we lost it" gets its own pin."""

    def test_the_enemy_taking_the_capital_from_us_fires(self, world):
        world.current_turn = 12
        _capture(world, "Paris", by="Austria", frm="France")
        assert _build_headline(world, "France")["class"] == "capital_lost"

    def test_the_enemy_taking_homeland_from_us_fires(self, world):
        world.current_turn = 12
        _capture(world, "Limousin", by="Austria", frm="France")
        assert _build_headline(world, "France")["class"] == "home_captured"

    def test_a_vassals_province_is_still_our_loss(self, world):
        """The sibling arm has always counted a vassal's soil as ours;
        hoisting the guard must not quietly drop that."""
        world.current_turn = 12
        world.vassals["Bavaria"] = {"lord": "France", "loyalty": 60,
                                    "autonomy": 50}
        bav = next((r for r, reg in world.regions.items()
                    if reg.controller == "Bavaria"), None)
        assert bav, "the 1805 board must have Bavarian soil"
        _capture(world, bav, by="Austria", frm="Bavaria")
        head = _build_headline(world, "France")
        assert head is not None and head["class"] in (
            "region_lost", "region_lost_estate"), head

    def test_every_production_producer_stamps_the_direction(self):
        """The guard reads `captured_from`. If any producer omitted it,
        a real loss would be silently suppressed — so the producers are
        pinned by census, not by trusting the comment at gazette.py:95."""
        producers = {
            "backend/models/world_state.py": 3,
            "backend/commands/capture_executor.py": 2,
            "backend/commands/combat_executor.py": 1,
        }
        for rel, count in producers.items():
            src = (REPO / rel).read_text(encoding="utf-8")
            blocks = re.findall(
                r'"type":\s*"region_captured",(?:[^}]*?)"captured_from":',
                src, re.S)
            assert len(blocks) == count, (rel, len(blocks), count)
            # ...and no producer anywhere logs one WITHOUT the key.
            total = len(re.findall(r'"type":\s*"region_captured"', src))
            assert total == count, (rel, "a producer omits captured_from")


# ════════════════════════════════════════════════════════════════════════
# 4. The Gazette speaks in our own voice
# ════════════════════════════════════════════════════════════════════════

class TestTheGazetteCaption:

    def _ev(self, region="Paris", by="Austria", frm="France"):
        return {"type": "region_captured", "turn": 12, "region": region,
                "captured_by": by, "captured_from": frm}

    def test_our_own_capital_is_captioned_in_the_losers_voice(self, world):
        assert gazette_mod._special_reason(
            world, [self._ev()]) == "THE CAPITAL HAS FALLEN"

    def test_an_enemy_capital_keeps_the_victors_caption(self, world):
        """The falsifiable negative — the caption must NOT change for
        somebody else's capital."""
        assert gazette_mod._special_reason(
            world, [self._ev(region="Vienna", by="France", frm="Austria")]
        ) == "a capital stormed"

    def test_a_third_partys_capital_keeps_the_victors_caption(self, world):
        assert gazette_mod._special_reason(
            world, [self._ev(region="Berlin", by="Russia", frm="Prussia")]
        ) == "a capital stormed"

    def test_the_sovereign_special_case_is_untouched(self, world):
        assert gazette_mod._special_reason(world, [{
            "type": "marshal_captured", "turn": 12, "marshal": "Napoleon",
            "nation": "France", "captor": "Austria", "sovereign": True,
        }]) == "THE EMPEROR TAKEN"

    def test_an_ordinary_province_forces_no_special_edition(self, world):
        assert gazette_mod._special_reason(
            world, [self._ev(region="Limousin")]) is None

    @pytest.mark.parametrize("order", ["capital-first", "emperor-first"])
    def test_the_capital_never_outranks_the_emperor(self, world, order):
        """Found by the pre-build fleet and reproduced by hand. Every arm
        of `_special_reason` returns immediately inside `for event in
        turn_events`, so the arms are ranked by LOG ORDER, not by their
        position in the file. Without a guard the new caption preempted
        "THE EMPEROR TAKEN" whenever Paris happened to be logged first —
        while the dispatch, on the same two events, ranks them 101 > 100.
        The paper must not contradict the briefing."""
        emperor = {"type": "marshal_captured", "turn": 12,
                   "marshal": "Napoleon", "nation": "France",
                   "captor": "Austria", "sovereign": True}
        events = ([self._ev(), emperor] if order == "capital-first"
                  else [emperor, self._ev()])
        assert gazette_mod._special_reason(
            world, events) == "THE EMPEROR TAKEN"

    def test_a_foreign_sovereign_does_not_suppress_our_caption(self, world):
        """The guard is scoped to OUR sovereign. Austria's emperor taken
        by Russia is not a reason to stop reporting the fall of Paris."""
        assert gazette_mod._special_reason(world, [
            self._ev(),
            {"type": "marshal_captured", "turn": 12, "marshal": "Charles",
             "nation": "Austria", "captor": "Russia", "sovereign": True},
        ]) == "THE CAPITAL HAS FALLEN"

    def test_the_caption_survives_the_fog_filter(self, world):
        """The Gazette feeds `_special_reason` from
        `filter_campaign_log`, and the loss of our OWN capital is not a
        `_is_player_event` exemption (that helper matches `captured_by`,
        never `captured_from`) — it survives on retained intel. A caption
        that the filter always ate would be unreachable copy, so this
        proves the whole chain, not just the arm."""
        from backend.campaign_log import filter_campaign_log
        world.current_turn = 12
        world.regions["Paris"].controller = "Austria"
        world.calculate_visibility()
        raw = [self._ev()]
        visible = filter_campaign_log(raw, world)
        assert visible, "the player cannot see his own capital fall"
        assert gazette_mod._special_reason(
            world, visible) == "THE CAPITAL HAS FALLEN"


# ════════════════════════════════════════════════════════════════════════
# 5. The diverse tail
# ════════════════════════════════════════════════════════════════════════

class TestTheDiverseTail:

    def test_the_last_slot_reaches_a_kind_of_news_not_yet_on_the_page(
            self, world):
        """Measured before: Soult, taken prisoner at weight 95, appeared
        on the page in NO ordering of the four province losses."""
        world.current_turn = 12
        for r in T_LOST:
            _capture(world, r)
        _take_marshal(world)
        head = _build_headline(world, "France")
        assert len(head["sub_beats"]) == 2
        assert "Limousin" in head["sub_beats"][0]
        assert "Soult" in head["sub_beats"][1], head["sub_beats"]

    def test_the_first_slot_is_ranked_by_weight_not_by_freshness(self, world):
        """Only the LAST slot is reserved; the first is still the highest
        weighted eligible candidate.

        REPLACES AN INERT PIN found by the mutation sweep (S4-10). The
        first version of this test used the four-province fixture, where
        the lead is `capital_lost` and so `home_captured` is a FRESH
        class at slot 0 — applying the tail rule there selects the very
        same candidate, and the mutation "apply the rule to the first
        slot too" survived. Dropping the capital makes the lead
        `home_captured` itself, and now the two rules genuinely disagree:
        by weight slot 0 is another province, by freshness it would be
        Soult."""
        world.current_turn = 12
        for r in ("Limousin", "Berry", "Normandy"):
            _capture(world, r)
        _take_marshal(world)
        head = _build_headline(world, "France")
        assert head["class"] == "home_captured", head
        assert head["sub_beats"][0].endswith(
            "Enemy colours fly over French homeland soil."), head["sub_beats"]
        assert "Soult" in head["sub_beats"][1], head["sub_beats"]

    def test_the_slot_count_is_named(self):
        assert SUB_BEAT_SLOTS == 2


class TestTheTailNeverSwallowsDistinctNews:
    """Spec §3 slice 4's named trap, and spec §2 D-10's three pins. The
    obvious implementation — collapse repeated classes — reds CA8-5's own
    falsifiable negative. The rule must be a preference with a fallback."""

    def test_two_different_marshals_taken_both_reach_the_page(self, world):
        world.current_turn = 12
        _take_marshal(world, "Soult")
        _take_marshal(world, "Lannes")
        head = _build_headline(world, "France")
        page = _page(head)
        assert "Soult" in page and "Lannes" in page, head

    def test_three_provinces_and_nothing_else_still_fill_both_slots(
            self, world):
        """No fresh class exists, so the tail falls back — nothing is
        dropped that dedupe would have kept."""
        world.current_turn = 12
        for r in ("Limousin", "Berry", "Normandy"):
            _capture(world, r)
        head = _build_headline(world, "France")
        assert len(head["sub_beats"]) == 2, head
        named = _page(head)
        for r in ("Limousin", "Berry", "Normandy"):
            assert r in named, (r, head)

    def test_the_ca8_5_pins_are_named_here_so_they_are_never_orphaned(self):
        """§2 D-10 lists three pins that must stay green through this
        slice. They live in another file; this asserts they still EXIST,
        so a future rename cannot silently retire the guard."""
        src = (REPO / "tests" / "test_creative_audit_ca8_2026_08_04.py"
               ).read_text(encoding="utf-8")
        for name in ("def test_two_different_marshals_still_get_two_beats",
                     "def test_three_battles_by_one_marshal_take_one_slot",
                     "def test_another_marshals_break_is_not_absorbed"):
            assert name in src, name

    def test_a_repeated_class_is_still_deduped_by_identity(self, world):
        """CA8-5's positive case is untouched: the SAME province reported
        twice is one beat."""
        world.current_turn = 12
        _capture(world, "Limousin")
        _capture(world, "Limousin")
        _capture(world, "Berry")
        head = _build_headline(world, "France")
        assert sum(1 for b in [head["text"], *head["sub_beats"]]
                   if "Limousin" in b) == 1, head


# ════════════════════════════════════════════════════════════════════════
# 6. Wiring, and the things this slice must NOT move
# ════════════════════════════════════════════════════════════════════════

class TestWiringAndBlastRadius:

    def test_the_new_class_carries_a_template_and_a_closing_note(self):
        assert "capital_lost" in dispatch_mod._HEADLINE_TEMPLATES
        assert "capital_lost" in dispatch_mod._HEADLINE_BERTHIER_NOTES
        assert "capital_lost" not in dispatch_mod.STANDING_HEADLINE_CLASSES

    def test_every_headline_class_has_a_template_and_a_note(self):
        """The CA8-22 class of bug, as a census: the note lookup is
        GUARDED, so a class without one ends the briefing with Berthier
        saying nothing at all — silently. Two classes shipped that way in
        August and nothing caught it."""
        for cls in HEADLINE_WEIGHTS:
            assert cls in dispatch_mod._HEADLINE_TEMPLATES, cls
            assert cls in dispatch_mod._HEADLINE_BERTHIER_NOTES, cls
        assert set(dispatch_mod._HEADLINE_TEMPLATES) == set(HEADLINE_WEIGHTS)

    def test_the_note_actually_reaches_the_built_dispatch(self, world):
        world.current_turn = 12
        _capture(world, "Paris")
        d = build_morning_dispatch(world)
        assert d["headline"]["class"] == "capital_lost"
        assert d["berthier_note"] == (
            "The army will hear of this before nightfall, Sire. Every "
            "order you give today will be read as your answer to it.")

    def test_no_campaign_log_type_moves(self):
        """Spec §2 D-15: headline classes are DISPLAY vocabulary, not
        event types. This slice adds no event and moves no log-type pin."""
        assert len(CAMPAIGN_LOG_TYPES) == 160
        assert "capital_lost" not in CAMPAIGN_LOG_TYPES
        assert "home_captured" not in CAMPAIGN_LOG_TYPES

    def test_no_godot_script_switches_on_a_headline_class(self):
        """The slice claims ZERO `.gd` changes. That is only true if no
        client script branches on the class string."""
        root = REPO / "godot-client"
        offenders = []
        for path in root.rglob("*.gd"):
            text = path.read_text(encoding="utf-8", errors="replace")
            for cls in ("home_captured", "capital_lost", "capital_stormed",
                        "sovereign_captured", "marshal_captured"):
                if f'"{cls}"' in text:
                    offenders.append((path.name, cls))
        assert not offenders, offenders

    def test_the_headline_adds_no_serialized_field(self, world):
        before = set(world.to_dict())
        world.current_turn = 12
        _capture(world, "Paris")
        _build_headline(world, "France")
        assert set(world.to_dict()) == before


class TestDeterminism:
    """Spec §3 slice 4 Done-when: the probe reproduces md5-identical under
    PYTHONHASHSEED=1 and =2 — the §4 method rule, since a builder that
    iterates a set or a dict of marshals can be hash-order dependent."""

    PROBE = (
        "import os,sys,json,hashlib\n"
        "sys.path.insert(0, os.getcwd())\n"
        "os.environ.setdefault('LLM_MODE','mock')\n"
        "from backend.models.world_state import WorldState\n"
        "from backend.game_logic.dispatch import _build_headline\n"
        "w = WorldState.from_scenario(r'%s')\n"
        "w.current_turn = 12\n"
        "for r in ['Limousin','Berry','Normandy','Paris']:\n"
        "    w.log_event({'type':'region_captured','turn':12,'region':r,\n"
        "                 'captured_by':'Austria','captured_from':'France',\n"
        "                 'method':'secure'})\n"
        "w.log_event({'type':'marshal_captured','turn':12,"
        "'marshal':'Soult','nation':'France','captor':'Austria'})\n"
        "h = _build_headline(w,'France')\n"
        "page = h['text'] + '||' + '||'.join(h['sub_beats'])\n"
        "sys.stdout.write('DIGEST:' + "
        "hashlib.md5(page.encode('utf-8')).hexdigest())\n"
    ) % str(SCENARIO_PATH)

    def _run(self, seed):
        env = dict(os.environ, PYTHONHASHSEED=str(seed), LLM_MODE="mock")
        env.pop("SOVEREIGN_SCENARIO", None)
        out = subprocess.run([sys.executable, "-c", self.PROBE], cwd=str(REPO),
                             env=env, capture_output=True, text=True,
                             timeout=300)
        assert "DIGEST:" in out.stdout, (out.stdout[-2000:], out.stderr[-2000:])
        return out.stdout.split("DIGEST:")[1].strip()

    def test_the_page_is_md5_identical_under_two_hash_seeds(self):
        assert self._run(1) == self._run(2)
