"""Row WO, slice 12 - the copy sweep.

Landing record: docs/WEIRD_OUTCOMES_SPEC.md section 3 slice 12.

Rows: WO-9 (the conquest events stamp `captured_from`, so PT-E5's own-soil
carve-out can keep an AI ATTACK-capture of the player's province in the
enemy-phase report) · WO-10 (the ratio sentence qualifies its estimate; a
LAST_KNOWN court prints a band, never its exact aggregate) · WO-12 (the
under-capacity concentration tax narrates as concentration, both surfaces)
· WO-15 (a prisoner is a prisoner, not "(dead)") · WO-16 (mauled publishes
the proportion and gains a 500-man floor - the recorded dissent lives at
the constant) · §4 N-8b (the rout sentence is repeat-aware on the
`battle_counts` seam) · WO-45 (a short query is never answered with a
province it cannot justify) · WO-33 (strategic combat rows carry
`battle_report`) · WO-42 (a liberation is logged) · WO-43 (the Gazette's
captions rank by gravity) · WO-44 (the scan floor no longer loses the
just-played turn; tail-stamped specials dedupe by identity) · the two
legacy Specify-lists (six, in fact) read the live world · WO-D10's copy
half (the exile refusal names the HOME-soil gate).

Every test names the mutation that kills it.
"""

import contextlib
import io
import re
import tokenize
from pathlib import Path

import pytest

from backend.commands import strategic as STRAT
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor
from backend.game_logic import dispatch as D
from backend.game_logic import gazette as G
from backend.game_logic import recruitment as R
from backend.game_logic.diplomatic_ledger import _format_army_strength
from backend.models.intel import FULL, LAST_KNOWN, STALE
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState, is_own_soil_recapture
from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
COMBAT_PY = REPO / "backend" / "commands" / "combat_executor.py"
DIPLO_PY = REPO / "backend" / "commands" / "diplomatic_executor.py"
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "europe_1805.json")

_DOCSTRING_HEADS = ('"""', "'''", 'r"""')


def _code_only(text: str) -> str:
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if (tok.type == tokenize.STRING
                    and tok.line.strip().startswith(_DOCSTRING_HEADS)):
                continue
            out.append(tok.string)
    except (tokenize.TokenError, IndentationError):
        return text
    return chr(10).join(out)


def _squeeze(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _pair(world, a, b, state):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = state
    if state == "WAR":
        world.war_start_turns[key] = world.current_turn


def _executor():
    return _quiet(CommandExecutor)


@pytest.fixture(scope="module")
def europe():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO_PATH))


def _attack(marshal, target, **flags):
    return {"command": {"marshal": marshal, "action": "attack",
                        "target": target, **flags}}


# ══════════════════════════════════════════════════════════════════
# WO-9 - the conquest events carry `captured_from`
# ══════════════════════════════════════════════════════════════════

class TestWO9TheCaptureStamp:

    def test_an_unopposed_conquest_is_stamped(self):
        """Killed by dropping the stamp from the unopposed producer."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=30000, personality="aggressive")
        world = WorldFactory.with_marshals([ney])
        _pair(world, "France", "Britain", "WAR")
        world.get_region("Netherlands").garrison_strength = 0   # unopposed
        res = _quiet(_executor().execute, _attack("Ney", "Netherlands"),
                     {"world": world})
        assert res["success"] is True, res
        conquest = [e for e in res.get("events", []) if e.get("type") == "conquest"]
        assert conquest, res.get("events")
        assert conquest[0]["captured_from"] == "Britain"
        assert conquest[0]["captured_by"] == "France"

    def test_both_conquest_producers_are_stamped(self):
        """Census (code-only): the garrison-destroyed producer is reached
        only through a garrison battle, so its stamp is pinned by source."""
        code = _squeeze(_code_only(COMBAT_PY.read_text(encoding="utf-8")))
        blocks = code.split('"type":"conquest"')[1:]
        assert len(blocks) == 2
        for block in blocks:
            head = block[:400]
            assert '"captured_from":old_controller' in head
            assert '"captured_by":marshal.nation' in head

    def test_the_enemy_phase_keeps_an_ai_attack_capture_of_our_soil(self):
        """PT-E5's carve-out keys on `captured_from`; without the stamp an
        AI attack-capture of a French province was dropped by the FULL
        gate (own soil is PARTIAL by construction)."""
        import backend.main as m
        from backend.models.intel import PARTIAL

        world = _quiet(WorldState, player_nation="France")
        world.calculate_visibility()
        # The 1805 board reads its own soil PARTIAL; the legacy fixture
        # stamps it FULL, which would satisfy the filter's visibility gate
        # regardless of the stamp - so the gate is set to the played shape.
        world.get_region_intel("Belgium").visibility = PARTIAL

        def _phase(event):
            return {"nations": {"Britain": {"actions": [{
                "marshal": "Wellington", "action_type": "attack",
                "message": "Wellington takes Belgium.",
                "events": [event]}]}}}

        stamped = {"type": "conquest", "marshal": "Wellington",
                   "region": "Belgium", "captured_by": "Britain",
                   "captured_from": "France"}
        bare = {"type": "conquest", "marshal": "Wellington",
                "region": "Belgium"}
        kept = m._filter_enemy_phase_by_visibility(_phase(stamped), world)
        dropped = m._filter_enemy_phase_by_visibility(_phase(bare), world)
        assert kept["nations"]["Britain"]["actions"], "the stamped capture was dropped"
        assert not dropped["nations"].get("Britain", {}).get("actions"), (
            "the bare event survived — the pin cannot tell the stamp apart")


# ══════════════════════════════════════════════════════════════════
# WO-10 - the estimate says how good it is; a last sighting is a band
# ══════════════════════════════════════════════════════════════════

class TestWO10TheQualifiedEstimate:

    def test_the_note_names_the_coverage(self):
        assert "counts nothing" in D._enemy_strength_note(
            {"total": 0, "counted": 0, "exact": 0})
        assert "3 of 5 known corps" in D._enemy_strength_note(
            {"total": 1, "counted": 5, "exact": 2})
        assert "known corps only" in D._enemy_strength_note(
            {"total": 1, "counted": 4, "exact": 4})

    def test_the_situation_carries_the_note(self):
        """Killed by dropping `enemy_strength_note` from the situation
        dict or making the note empty."""
        world = _quiet(WorldState, player_nation="France")
        world.calculate_visibility()
        dispatch = _quiet(D.build_morning_dispatch, world)
        found = []

        def walk(node):
            if isinstance(node, dict):
                if "enemy_strength_note" in node:
                    found.append(node["enemy_strength_note"])
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(dispatch)
        assert found, "the situation dict carries no note"
        assert found[0].startswith("(") and "corps" in found[0]

    def test_the_detail_matches_the_estimator(self):
        world = _quiet(WorldState, player_nation="France")
        world.calculate_visibility()
        detail = D._enemy_strength_estimate_detail(world, "France")
        assert detail["total"] == D._estimate_enemy_strength_from_intel(world, "France")
        assert 0 <= detail["exact"] <= detail["counted"]

    def test_a_last_sighting_is_a_band_not_the_aggregate(self):
        """Killed by dropping the LAST_KNOWN arm (the exact figure returns)."""
        assert _format_army_strength(51238, LAST_KNOWN) == "Considerable (last seen)"
        assert _format_army_strength(51238, STALE) == "Considerable"
        assert _format_army_strength(51238, FULL) == "51,238 men"
        assert _format_army_strength(51238, "no-such-tier") == "Unknown"


# ══════════════════════════════════════════════════════════════════
# WO-12 - concentration is not starvation
# ══════════════════════════════════════════════════════════════════

class TestWO12TheConcentrationTax:

    def _crowded_paris(self):
        corps = [MarshalFactory.infantry(name=f"Corps{i}", location="Paris",
                                         strength=4000, personality="cautious")
                 for i in range(3)]
        return WorldFactory.with_marshals(corps)

    def test_an_under_capacity_stack_is_a_crowd(self):
        """Killed by stamping every event "shortage"."""
        world = self._crowded_paris()
        events = _quiet(world.process_supply_attrition)
        ours = [e for e in events if e.get("region") == "Paris"]
        assert ours, "the death-ball tax did not fire"
        assert all(e["cause"] == "concentration" for e in ours)
        assert all(e["message"].startswith("Crowded at Paris") for e in ours)
        assert all("3 corps" in e["message"] for e in ours)

    def test_an_over_capacity_stack_is_a_shortage(self):
        horde = MarshalFactory.infantry(name="Horde", location="Brittany",
                                        strength=200000, personality="cautious")
        world = WorldFactory.with_marshals([horde])
        events = _quiet(world.process_supply_attrition)
        ours = [e for e in events if e.get("marshal") == "Horde"]
        assert ours
        assert ours[0]["cause"] == "shortage"
        assert ours[0]["message"].startswith("Supply shortage at Brittany")

    def _with_run(self, cause):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=10000, personality="aggressive")
        world = WorldFactory.with_marshals([ney], current_turn=8)
        for turn in (6, 7):
            world.event_log.append({"type": "supply_attrition", "turn": turn,
                                    "marshal": "Ney", "nation": "France",
                                    "region": "Belgium", "losses": 100,
                                    "cause": cause})
        return world, ney

    def test_the_roster_note_names_the_cause(self):
        """Killed by printing the starving line whatever the cause."""
        world, ney = self._with_run("concentration")
        note = D._derive_danger(ney, world, "France",
                                D._collect_supply_attrition_turns(world))
        assert note.startswith("Crowded — Belgium carries more corps")
        world2, ney2 = self._with_run("shortage")
        note2 = D._derive_danger(ney2, world2, "France",
                                 D._collect_supply_attrition_turns(world2))
        assert note2.startswith("Starving — supply has failed at Belgium")

    def test_a_legacy_row_without_a_cause_reads_shortage(self):
        world, ney = self._with_run("concentration")
        for e in world.event_log:
            e.pop("cause", None)
        assert D._latest_supply_cause(world, "Ney") == "shortage"


# ══════════════════════════════════════════════════════════════════
# WO-15 - a prisoner is not dead
# ══════════════════════════════════════════════════════════════════

class TestWO15ThePrisonerIsNotDead:

    def test_the_recruit_refusal_names_the_captor(self):
        """Killed by removing the captor branch."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=0, personality="aggressive")
        ney.captured_by = "Britain"
        dead = MarshalFactory.infantry(name="Drouot", location="Belgium",
                                       strength=0, personality="cautious")
        world = WorldFactory.with_marshals([ney, dead])
        assert _quiet(world.find_nearest_marshal_to_region, "Belgium") is None
        blocked = list(getattr(world, "_last_nearest_marshal_block", []))
        assert "Ney (a prisoner of Britain)" in blocked
        assert "Drouot (dead)" in blocked
        assert "Ney (dead)" not in blocked


# ══════════════════════════════════════════════════════════════════
# WO-16 - "mauled" says the proportion and has a floor
# ══════════════════════════════════════════════════════════════════

def _mauled_world(strength):
    world = _quiet(WorldState, player_nation="France")
    world.current_turn = 6
    ney = world.get_marshal("Ney")
    ney.location = "Bohemia"
    ney.strength = strength
    return world, ney


def _battle(name, casualties, turn=6):
    return {"type": "battle", "turn": turn, "location": "Bohemia",
            "defender": name, "defender_nation": "France",
            "defender_casualties": casualties,
            "attacker": "ArchdukeCharles", "attacker_nation": "Austria"}


class TestWO16MauledSaysTheProportion:

    def test_the_words(self):
        assert D._mauled_proportion(2218, 8218) == "a quarter"
        assert D._mauled_proportion(3000, 9000) == "a third"
        assert D._mauled_proportion(5000, 9000) == "half"
        assert D._mauled_proportion(8000, 9000) == "three-quarters"

    def test_the_headline_publishes_the_proportion(self):
        """Killed by freezing `_mauled_proportion` at "a quarter" or by
        dropping `proportion` from the template."""
        world, ney = _mauled_world(6000)
        world.event_log.append(_battle("Ney", 3000))        # 3,000 of 9,000
        head = _quiet(D._build_headline, world, "France")
        assert head is not None and head["class"] == "own_mauled"
        assert "a third of his corps — 3,000 men —" in head["text"]

    def test_the_floor_keeps_a_remnants_scratch_off_the_page(self):
        """29 of 89 men is a third and used to lead the briefing. Killed by
        dropping the `OWN_MAULED_MIN_CASUALTIES` clause."""
        assert D.OWN_MAULED_MIN_CASUALTIES == 500
        world, ney = _mauled_world(60)
        world.event_log.append(_battle("Ney", 29))
        head = _quiet(D._build_headline, world, "France")
        assert head is None or head["class"] != "own_mauled"


# ══════════════════════════════════════════════════════════════════
# §4 N-8b - the rout sentence is repeat-aware
# ══════════════════════════════════════════════════════════════════

class TestTheRoutRepeats:

    def test_the_first_battle_keeps_the_old_sentence(self):
        world = WorldFactory.basic()
        world.battle_counts = {}
        assert D._rout_clause(world, "Belgium", "Wellington") == \
            "Wellington's corps is broken and flees."

    def test_later_battles_say_so(self):
        """Killed by freezing the index at 0."""
        world = WorldFactory.basic()
        world.battle_counts = {"Belgium": 2}
        assert "second time" in D._rout_clause(world, "Belgium", "Wellington")
        world.battle_counts = {"Belgium": 3}
        assert "yet again" in D._rout_clause(world, "Belgium", "Wellington")
        world.battle_counts = {"Belgium": 9}
        assert "Belgium" in D._rout_clause(world, "Belgium", "Wellington")


# ══════════════════════════════════════════════════════════════════
# WO-45 - a short query is never answered with a guess
# ══════════════════════════════════════════════════════════════════

class TestWO45TheShortNameGuess:

    @pytest.mark.parametrize("query,guess", [
        # Measured on the shipped board before the fix, both refusing arms:
        ("Nye", "Ukraine"),        # partial_ratio 80 -> the implausible-auto-correct arm
        ("Sco", "Gascony"),        # a CONTAINED 3-letter string scores a full 100
        ("Ulm", "Stockholm"),      # 67 -> the SUGGEST arm ("Did you mean 'Stockholm'?")
        ("Sax", "White Russia"),   # 67 -> the suggest arm, against nothing at all
    ])
    def test_a_short_query_is_never_answered_with_a_guess(self, europe, query, guess):
        """Killed by dropping the `_too_short` floor from EITHER arm — `Nye`
        and `Sco` reach the WO-2 implausible-auto-correct arm, `Ulm` and
        `Sax` the native suggest arm; the first sweep found the suggest-arm
        pin inert because every case had gone through the other door."""
        ex = _executor()
        region, err = ex._fuzzy_match_region(query, europe)
        assert region is None
        assert "Did you mean" not in err["message"], err
        assert guess not in err["message"]
        assert err["message"] == f"Region '{query}' not found."

    def test_a_real_typo_still_asks(self, europe):
        ex = _executor()
        region, err = ex._fuzzy_match_region("Venetia", europe)
        assert region is None
        assert "Did you mean" in err["message"]

    def test_end_to_end_the_attack_refusal_carries_no_guess(self, europe):
        import copy
        world = copy.deepcopy(europe)
        res = _quiet(_executor().execute, _attack("Ney", "Nye"), {"world": world})
        assert res.get("success") is False
        assert "Did you mean" not in (res.get("message") or "")


# ══════════════════════════════════════════════════════════════════
# WO-33 - a strategic combat row carries its report
# ══════════════════════════════════════════════════════════════════

class TestWO33TheReportRidesTheRow:

    def _pair_with_order(self, order):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=30000, personality="aggressive")
        ney.strategic_order = order
        wel = MarshalFactory.enemy(name="Wellington", location="Netherlands",
                                   nation="Britain", strength=3000)
        world = WorldFactory.with_marshals([ney, wel], current_turn=2)
        _pair(world, "France", "Britain", "WAR")
        return world, ney, wel

    def _result(self, victor):
        return {"success": True, "message": "fought",
                "battle_report": {"summary": "a report"},
                "battle_result": {"victor": victor},
                "events": [{"type": "battle", "outcome": "x"}],
                "new_state": {"world": object()}}

    @pytest.mark.parametrize("victor,outcome", [
        ("Ney", "victory"), ("Wellington", "defeat"), ("", "stalemate")])
    def test_every_outcome_carries_the_report(self, victor, outcome):
        """Killed by making `_combat_carry` return nothing."""
        order = StrategicOrder(command_type="MOVE_TO", target="Netherlands",
                               target_type="region", started_turn=1,
                               original_command="x", issued_turn=1)
        world, ney, wel = self._pair_with_order(order)
        sp = StrategicOrderProcessor(_executor())
        row = _quiet(sp._handle_combat_result, ney, wel, self._result(victor),
                     world, {"world": world})
        assert row["action"] == "combat"
        assert row["outcome"] == outcome
        assert row["battle_report"] == {"summary": "a report"}
        assert row["battle_details"]["message"] == "fought"
        assert "new_state" not in row["battle_details"]

    def test_a_cleared_order_still_carries_it(self):
        world, ney, wel = self._pair_with_order(None)
        sp = StrategicOrderProcessor(_executor())
        row = _quiet(sp._handle_combat_result, ney, wel, self._result("Ney"),
                     world, {"world": world})
        assert row["battle_report"] == {"summary": "a report"}

    def test_the_hold_sally_row_carries_it_too(self):
        order = StrategicOrder(command_type="HOLD", target="Belgium",
                               target_type="region", started_turn=1,
                               original_command="x", issued_turn=1)
        world, ney, wel = self._pair_with_order(order)
        ney.holding_position = True
        ney.hold_region = "Belgium"
        wel.strength = 2000
        wel.morale = 26
        reports = _quiet(StrategicOrderProcessor(_executor()).process_strategic_orders,
                         world, {"world": world})
        assert reports and reports[0]["action"] == "sally"
        assert "battle_report" in reports[0]
        assert reports[0]["battle_details"] is not None

    def test_the_carry_strips_the_world(self):
        carry = STRAT._combat_carry({"battle_report": 1, "new_state": {"w": 1}, "k": 2})
        assert carry["battle_report"] == 1
        assert carry["battle_details"] == {"battle_report": 1, "k": 2}
        assert STRAT._combat_carry(None) == {"battle_report": None,
                                              "battle_details": None}


# ══════════════════════════════════════════════════════════════════
# WO-42 - the liberation is logged
# ══════════════════════════════════════════════════════════════════

class TestWO42TheLiberationIsLogged:

    def _lost_belgium(self):
        ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                      strength=40000, personality="aggressive")
        wel = MarshalFactory.enemy(name="Wellington", location="Belgium",
                                   nation="Britain", strength=2000)
        wel.morale = 26
        world = WorldFactory.with_marshals([ney, wel])
        _pair(world, "France", "Britain", "WAR")
        world.get_region("Belgium").controller = "Britain"
        world.get_region("Belgium").garrison_strength = 0
        assert is_own_soil_recapture(world, "Belgium", "France")
        return world, ney

    def _liberations(self, world):
        return [e for e in world.event_log
                if e.get("type") == "region_captured"
                and e.get("method") == "liberated"]

    def test_the_attack_capture_logs_the_liberation(self):
        """Killed by dropping the `log_event` at the `_apply_secure` arm."""
        world, ney = self._lost_belgium()
        res = _quiet(_executor().execute, _attack("Ney", "Wellington"),
                     {"world": world})
        assert res["success"] is True
        assert world.get_region("Belgium").controller == "France"
        rows = self._liberations(world)
        assert len(rows) == 1
        assert rows[0]["region"] == "Belgium"
        assert rows[0]["captured_by"] == "France"
        assert rows[0]["captured_from"] == "Britain"
        assert not world.pending_capture_choice

    def test_the_occupation_capture_logs_the_liberation(self):
        """Killed by dropping the `log_event` at the occupation arm."""
        world, ney = self._lost_belgium()
        ney.location = "Belgium"
        world.marshals.pop("Wellington")
        _quiet(world._apply_occupation_capture_effects, ney, "Belgium")
        rows = self._liberations(world)
        assert len(rows) == 1 and rows[0]["captured_from"] == "Britain"

    def test_the_dispatch_home_arm_is_reachable_now(self):
        """The dead "is French again" line finally has a producer. A
        BLOODLESS liberation, deliberately: when a battle wins the field,
        CA8-26's victory line absorbs the map fact by design."""
        world, ney = self._lost_belgium()
        world.marshals.pop("Wellington")
        world.current_turn = 6
        res = _quiet(_executor().execute, _attack("Ney", "Belgium"), {"world": world})
        assert res["success"] is True, res
        assert world.get_region("Belgium").controller == "France"
        assert self._liberations(world)
        head = _quiet(D._build_headline, world, "France")
        assert head is not None
        rendered = head["text"] + " " + " ".join(head.get("sub_beats", []))
        assert "Belgium is French again" in rendered


class TestFoundInPassing:

    def test_one_defender_stands_in_his_path(self):
        """`enemy_on_our_soil` printed "Ney stand in his path." Killed by
        reverting the verb agreement."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=30000, personality="aggressive")
        wel = MarshalFactory.enemy(name="Wellington", location="Belgium",
                                   nation="Britain", strength=20000)
        world = WorldFactory.with_marshals([ney, wel], current_turn=6)
        _pair(world, "France", "Britain", "WAR")
        world.calculate_visibility()
        head = _quiet(D._build_headline, world, "France")
        assert head is not None and head["class"] == "enemy_on_our_soil"
        assert "Ney stands in his path." in head["text"]


# ══════════════════════════════════════════════════════════════════
# WO-43 / WO-44 - the Gazette's gravest caption, and its scan floor
# ══════════════════════════════════════════════════════════════════

def _cap(region, by, frm, turn=12):
    return {"type": "region_captured", "turn": turn, "region": region,
            "captured_by": by, "captured_from": frm}


def _emperor(turn=12):
    return {"type": "marshal_captured", "turn": turn, "marshal": "Napoleon",
            "nation": "France", "captor": "Austria", "sovereign": True}


def _marshal_lost(turn=12):
    return {"type": "marshal_captured", "turn": turn, "marshal": "Ney",
            "nation": "France", "captor": "Austria"}


class TestWO43TheGravestCaptionWins:

    @pytest.mark.parametrize("order", ["capital-first", "emperor-first"])
    def test_an_enemy_capital_never_outranks_the_emperor(self, europe, order):
        """The measured defect: Vienna stormed by France preempted THE
        EMPEROR TAKEN when logged first. Killed by returning the FIRST
        candidate instead of the heaviest."""
        vienna = _cap("Vienna", "France", "Austria")
        events = [vienna, _emperor()] if order == "capital-first" else [_emperor(), vienna]
        assert G._special_reason(europe, events) == "THE EMPEROR TAKEN"

    def test_a_capital_stormed_outranks_a_marshal_lost(self, europe):
        assert G._special_reason(europe, [_marshal_lost(), _cap("Vienna", "France", "Austria")]) \
            == "a capital stormed"

    def test_a_crown_struck_outranks_a_capital_stormed(self, europe):
        assert G._special_reason(europe, [
            _cap("Vienna", "France", "Austria"),
            {"type": "nation_eliminated", "turn": 12, "nation": "Austria"},
        ]) == "a crown struck from the map"

    def test_our_capital_outranks_a_marshal_lost(self, europe):
        assert G._special_reason(europe, [_marshal_lost(), _cap("Paris", "Austria", "France")]) \
            == "THE CAPITAL HAS FALLEN"

    def test_the_candidates_carry_their_event_identity(self, europe):
        keys = {c[2] for c in G._special_candidates(
            europe, [_cap("Vienna", "France", "Austria"),
                     _cap("Berlin", "France", "Prussia")])}
        assert len(keys) == 2 and all("a capital stormed|" in k for k in keys)

    def test_nothing_grave_is_still_none(self, europe):
        assert G._special_reason(europe, [_cap("Limousin", "Austria", "France")]) is None


class TestWO44TheScanFloor:

    def _paper(self, europe):
        import copy
        world = copy.deepcopy(europe)
        world.gazette_issues = []
        world.event_log = []
        for name in ("Vienna", "Berlin"):
            world.get_region_intel(name).visibility = FULL
        return world

    def test_a_special_on_the_tick_after_a_special_is_published(self, europe):
        """Measured: with the last issue at turn 11 and Paris falling on
        turn 11, no paper at all — the clamp `max(last_turn + 1, turn - 1)`
        excluded the just-played turn. Killed by restoring the clamp."""
        world = self._paper(europe)
        world.current_turn = 11
        world.event_log.append(_cap("Vienna", "France", "Austria", turn=10))
        first = _quiet(G.process_gazette, world)
        assert first and first["special_reason"] == "a capital stormed"
        world.current_turn = 12
        world.event_log.append(_cap("Berlin", "France", "Prussia", turn=11))
        second = _quiet(G.process_gazette, world)
        assert second is not None, "the just-played turn's capital was lost"
        assert second["special_reason"] == "a capital stormed"
        assert "Berlin" in second["special_key"]

    def test_the_same_tail_stamped_event_never_forces_a_second_edition(self, europe):
        """Killed by dropping the identity dedupe."""
        world = self._paper(europe)
        world.current_turn = 11
        # A tail-stamped special: stamped with the POST-increment turn.
        world.event_log.append(_cap("Vienna", "France", "Austria", turn=11))
        first = _quiet(G.process_gazette, world)
        assert first and "Vienna" in first["special_key"]
        world.current_turn = 12          # the same event is still >= turn - 1
        second = _quiet(G.process_gazette, world)
        assert second is None

    def test_a_different_capital_on_the_next_tick_still_prints(self, europe):
        world = self._paper(europe)
        world.current_turn = 11
        world.event_log.append(_cap("Vienna", "France", "Austria", turn=11))
        assert _quiet(G.process_gazette, world)
        world.current_turn = 12
        world.event_log.append(_cap("Berlin", "France", "Prussia", turn=11))
        second = _quiet(G.process_gazette, world)
        assert second and "Berlin" in second["special_key"]


# ══════════════════════════════════════════════════════════════════
# The Specify-lists read the live world; WO-D10's copy half
# ══════════════════════════════════════════════════════════════════

class TestTheSpecifyListIsLive:

    def test_the_literal_is_gone(self):
        code = _code_only(DIPLO_PY.read_text(encoding="utf-8"))
        assert "Britain, Prussia, Austria, or Saxony" not in code
        assert _squeeze(code).count("_specify_courts(world)") >= 6

    def test_the_legacy_world_lists_its_courts(self):
        from backend.commands.diplomatic_executor import _specify_courts
        world = _quiet(WorldState, player_nation="France")
        assert _specify_courts(world) == "Austria, Britain, Prussia, or Saxony"

    def test_the_1805_world_lists_more_than_four(self, europe):
        from backend.commands.diplomatic_executor import _specify_courts
        listed = _specify_courts(europe)
        assert "Russia" in listed or "or one of" in listed
        assert "France" not in listed

    def test_the_declare_war_refusal_reads_the_live_list(self, europe):
        """Killed by returning the old literal from the helper."""
        import copy
        world = copy.deepcopy(europe)
        res = _quiet(_executor().execute, {"command": {
            "action": "diplomatic_declare_war",
            "diplomatic_data": {"diplomat": "Talleyrand",
                                "action": "diplomatic_declare_war",
                                "target_nation": None}}}, {"world": world})
        msg = res.get("message") or ""
        assert "against which nation shall we declare war? Specify:" in msg
        assert "Saxony." not in msg or "or one of" in msg
        assert "Austria" in msg


class TestWOD10TheHomeSoilGate:

    def test_the_exile_refusal_names_the_gate(self, europe):
        """Killed by reverting the sentence."""
        import copy
        world = copy.deepcopy(europe)
        candidate = dict(world.marshal_pool["France"][0])
        world.nation_gold["France"] = 10 ** 6
        for arm in list(world.manpower_pools.get("France", {})):
            world.manpower_pools["France"][arm] = 10 ** 6
        for region in world.regions.values():
            if region.controller == "France":
                region.controller = "Britain"
        world.invalidate_active_nations_cache()
        refusal = R.check_commission(world, "France", candidate)
        assert refusal and "No HOME soil remains" in refusal
        assert "home province" in refusal
