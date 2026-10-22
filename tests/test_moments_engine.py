"""S14c part 1 — the moments' engine and its transport, UNARMED
(`docs/EVENTS_SPEC.md` §3–§5, §9 Part 1; the siblings `BUG_FIXES.md` §S14C).

The shipped 1805 boot authors no `moments` block, so every pin here arms the
real booted world with the staged fixture `tests/fixtures/moments_block.json`
(the deck exactly as ruled) and drives the real seams: each letter arrives at
its resolved turn when its premise holds and is `passed` when it does not;
each answer applies exactly its plan on three boards (rich, poor, clamped); a
closed Accept leaves the letter standing; an unanswered letter lapses as its
decline and writes no cooldown key; every status survives a save round trip;
the bands resolve; the validator refuses each bad block; and the siblings
S14C-X4, X6, X7, X8 (with X18–X20), X9, X16 and X17 are pinned.
"""
import ast
import contextlib
import copy
import io
import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.game_logic import imperial_designs as ID
from backend.game_logic import moments as MO
from backend.game_logic import treaty as T
from tests import _chip_census as C

REPO = Path(__file__).resolve().parents[1]
BACKEND = REPO / "backend"
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
FIXTURE = REPO / "tests" / "fixtures" / "moments_block.json"
SWEEP_SEEDS = ["historical", "ulm", "austerlitz", "jena", "marengo",
               "eylau", "friedland", "wagram", "lodi", "rivoli"]


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _block():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    return M.world


@pytest.fixture
def armed(world):
    world.moments = MO.from_block(_block())
    return world


@pytest.fixture
def client(world):
    return TestClient(M.app)


def _rel(world, court):
    return int(world.nation_relations.get(world._make_diplo_key("France", court), 0))


def _at(world, turn):
    world.current_turn = int(turn)
    world.invalidate_active_nations_cache()


def _tick(world):
    with _quiet():
        return MO.tick(world)


def _letter(world, moment_id):
    dm = world.dialogue_manager
    for d in [dm.peek()] + list(dm.iter_queue()):
        if MO.is_moment_letter(d) and MO.moment_id_of(d) == moment_id:
            return d
    return None


def _make_current(world, letter):
    dm = world.dialogue_manager
    if dm.peek() is not letter:
        dm.remove_matching(lambda d: d is letter)
        dm.preempt(letter)
    assert dm.peek() is letter


def _rich(world):
    world.nation_gold["France"] = 20_000
    world.diplomatic_points = 7
    world.admin_actions_remaining = 2


def _vassalize(world, court, loyalty=60, autonomy=1):
    world.vassals[court] = {"lord": "France", "loyalty": int(loyalty), "autonomy": int(autonomy),
                            "path": "treaty", "tribute_rate": 0.75}
    world.diplomatic_states[world._make_diplo_key("France", court)] = "VASSAL"
    world.invalidate_active_nations_cache()


def _stage_decree_board(world):
    """M4's premise made true: Holland Autonomous and at peace with Britain
    while France fights her — the board where the Decree would shut a port."""
    world.vassals["Holland"]["autonomy"] = 2
    world.diplomatic_states[world._make_diplo_key("Holland", "Britain")] = "PEACE"
    world.invalidate_active_nations_cache()


# ═══════════════════════════════════════════════════════════════════════════
# Unarmed — the shipped boot authors no block
# ═══════════════════════════════════════════════════════════════════════════

class TestUnarmed:
    """A world whose scenario authors no block is UNARMED — the bare flag
    world, the tutorial, the legacy rollback. Re-seated consciously by S14c
    part 2's second landing, which ARMED the shipped 1805 boot (its pins:
    tests/test_moments_armed.py): these read a world with no block."""

    def test_a_world_with_no_block_is_unarmed_and_the_tick_touches_nothing(self):
        from backend.models.world_state import WorldState
        bare = WorldState(player_nation="France")
        assert bare.moments == {} and not MO.armed(bare)
        before = copy.deepcopy(bare.to_dict())
        assert MO.tick(bare) == []
        assert bare.to_dict() == before and bare.to_dict()["moments"] == {}

    def test_the_shipped_scenario_arms_the_whole_deck(self):
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        assert [e["id"] for e in data["moments"]["deck"]] == [
            "bavarian_match", "throne_of_holland", "crown_of_the_reich", "decree_of_berlin"]

    def test_every_reader_answers_nothing_on_an_unarmed_world(self, world):
        world.moments = {}
        assert MO.deck(world) == [] and MO.owner(world) == ""
        assert MO.status(world, "bavarian_match") == ""
        court_letter = {"type": "incoming_proposal", "target_nation": "Prussia",
                        "context": {"source_nation": "Prussia", "proposal_type": "peace"}}
        assert not MO.is_moment_letter(court_letter) and not MO.keeps_open(court_letter, 1)
        assert MO.lapse_default(world, court_letter) == {}


# ═══════════════════════════════════════════════════════════════════════════
# The store and its bands
# ═══════════════════════════════════════════════════════════════════════════

class TestTheStore:
    def test_one_shape_for_the_scenario_key_and_the_save(self):
        scenario = MO.store_from_data({"moments": _block()})
        assert scenario["state"] == {} and scenario["block"]["owner"] == "France"
        assert "_comment" not in scenario["block"]
        saved = {"moments": {"block": scenario["block"],
                             "state": {"bavarian_match": {"status": "passed", "turn": 11,
                                                          "reason": "premise"}}}}
        restored = MO.store_from_data(saved)
        assert restored["state"]["bavarian_match"]["reason"] == "premise"
        assert MO.store_from_data({}) == {} and MO.store_from_data({"moments": {"deck": []}}) == {}

    def test_an_unresolved_band_collapses_to_its_authored_value(self):
        store = MO.from_block(_block())
        turns = {e["id"]: e.get("turn") for e in store["block"]["deck"]}
        assert turns == {"bavarian_match": 8, "throne_of_holland": 18,
                         "crown_of_the_reich": None, "decree_of_berlin": 29}

    def test_historical_resolves_every_window_to_its_value(self):
        from backend.game_logic.campaign_variance import resolve_moment_turns
        block = resolve_moment_turns(_block(), "historical")
        assert [e.get("turn") for e in block["deck"]] == [8, 18, None, 29]

    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_every_seed_resolves_inside_its_band(self, seed):
        from backend.game_logic.campaign_variance import resolve_moment_turns
        authored = {e["id"]: e.get("turn") for e in _block()["deck"]}
        block = resolve_moment_turns(_block(), seed)
        for e in block["deck"]:
            band = (authored[e["id"]] or {}).get("band") if isinstance(authored[e["id"]], dict) else None
            if band:
                assert isinstance(e["turn"], int) and band[0] <= e["turn"] <= band[1]
            else:
                assert "turn" not in e        # the causal Reich never varies

    def test_an_unbanded_window_never_varies_and_the_resolver_is_idempotent(self):
        from backend.game_logic.campaign_variance import resolve_moment_turns
        block = _block()
        block["deck"][1]["turn"] = {"value": 18}
        outs = {s: resolve_moment_turns(copy.deepcopy(block), s)["deck"][1]["turn"]
                for s in SWEEP_SEEDS}
        assert set(outs.values()) == {18}
        once = resolve_moment_turns(copy.deepcopy(block), "ulm")
        assert resolve_moment_turns(copy.deepcopy(once), "ulm") == once

    def test_the_band_varies_across_the_sweep(self):
        from backend.game_logic.campaign_variance import resolve_moment_turns
        turns = {resolve_moment_turns(_block(), s)["deck"][0]["turn"] for s in SWEEP_SEEDS}
        assert len(turns) > 1, "the M1 band [8, 10] should spread across ten seeds"

    def test_the_boot_resolves_through_the_scenario_variance(self):
        from backend.game_logic.campaign_variance import apply_scenario_variance
        data = {"moments": _block()}
        apply_scenario_variance(data, "historical")
        assert [e.get("turn") for e in data["moments"]["deck"]] == [8, 18, None, 29]
        data = {"moments": _block()}
        apply_scenario_variance(data, "jena")
        assert all(isinstance(e.get("turn"), int) for e in data["moments"]["deck"] if "lag" not in e)


# ═══════════════════════════════════════════════════════════════════════════
# The validator
# ═══════════════════════════════════════════════════════════════════════════

def _scenario_with(block):
    data = json.loads(SCENARIO.read_text(encoding="utf-8"))
    data["moments"] = block
    return data


def _moment_errors(block):
    from backend.modding.validator import validate_scenario
    return [e for e in validate_scenario(_scenario_with(block)).errors if e.path.startswith("moments")]


def _bad(mutate):
    block = _block()
    mutate(block)
    return {e.path for e in _moment_errors(block)}


class TestTheValidator:
    def test_the_ruled_deck_validates(self):
        assert _moment_errors(_block()) == []

    @pytest.mark.parametrize("label, mutate, path", [
        ("unknown predicate", lambda b: b["deck"][0]["when"].update(predicate="omen"), "moments.deck[0].when"),
        ("unknown op", lambda b: b["deck"][0]["accept"]["ops"].append({"op": "glory", "amount": 1}),
         "moments.deck[0].accept.ops[5]"),
        ("a priced decline", lambda b: b["deck"][0]["decline"]["ops"].append({"op": "gold", "amount": 100}),
         "moments.deck[0].decline.ops[1]"),
        ("a VP-1 source", lambda b: b["deck"][0]["accept"]["ops"][4].update(source="act_of_confederation"),
         "moments.deck[0].accept.ops[4].source"),
        ("an unlabelled source", lambda b: b["deck"][0]["accept"]["ops"][4].update(source="moment_nowhere"),
         "moments.deck[0].accept.ops[4].source"),
        ("a date that is not its turn", lambda b: b["deck"][0].update(date="1806-02-14"), "moments.deck[0].date"),
        ("windows too close", lambda b: b["deck"][1].update(turn={"value": 11, "band": [11, 12]},
                                                            date="1806-02-25"), "moments.deck"),
        ("a title past 40", lambda b: b["deck"][0].update(title="T" * 41), "moments.deck[0].title"),
        ("a record past 240", lambda b: b["deck"][0].update(record="R" * 241), "moments.deck[0].record"),
        ("a caption past 36", lambda b: b["deck"][0]["accept"].update(caption="C" * 37),
         "moments.deck[0].accept.caption"),
        ("turn and lag both", lambda b: b["deck"][2].update(turn=21), "moments.deck[2]"),
        ("a causal entry without an anchor", lambda b: b["deck"][2]["when"].update(predicate="court_warm",
                                                                                 court="Austria"),
         "moments.deck[2].when"),
        ("an unknown road", lambda b: b["deck"][3].update(roads=["moon"]), "moments.deck[3].roads"),
        ("an envoy with no court", lambda b: b["deck"][1]["voice"].pop("nation"), "moments.deck[1].voice.nation"),
        ("a duplicate id", lambda b: b["deck"][1].update(id="bavarian_match"), "moments.deck[1].id"),
        ("an id that is a law's", lambda b: b["deck"][0].update(id="berlin_decree"), "moments.deck[0].id"),
        ("a window past the Verdict", lambda b: b["deck"][3].update(turn={"value": 43, "band": [43, 43]},
                                                                    date="1807-06-25"), "moments.deck[3].turn"),
        ("a gold price out of band", lambda b: b["deck"][0]["accept"]["ops"][1].update(amount=5000),
         "moments.deck[0].accept.ops[1].amount"),
        ("a pacing gap out of band", lambda b: b["pacing"].update(min_gap=9), "moments.pacing.min_gap"),
        ("a law not the owner's", lambda b: b["deck"][3]["when"].update(law="landwehr"), "moments.deck[3].when.law"),
        ("an unknown court", lambda b: b["deck"][0]["when"].update(court="Atlantis"), "moments.deck[0].when.court"),
    ])
    def test_each_bad_block_is_refused(self, label, mutate, path):
        assert path in _bad(mutate), label

    def test_the_calendar_inverse_is_the_validator_s_alone(self):
        """S14C-X6: `calendar.turn_for_date` checks an authored date; no
        mechanic imports it — the calendar stays display-only."""
        importers = []
        for path in BACKEND.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and any(a.name == "turn_for_date" for a in node.names):
                    importers.append(path.relative_to(REPO).as_posix())
                if isinstance(node, ast.Attribute) and node.attr == "turn_for_date":
                    importers.append(path.relative_to(REPO).as_posix())
        assert sorted(set(importers)) == ["backend/modding/validator.py"]


# ═══════════════════════════════════════════════════════════════════════════
# Arrival — each letter at its resolved turn when its premise holds
# ═══════════════════════════════════════════════════════════════════════════

class TestArrival:
    def test_the_match_arrives_on_its_turn(self, armed):
        _at(armed, 7)
        assert _tick(armed) == []
        _at(armed, 8)
        assert _tick(armed) == ["bavarian_match"]
        letter = _letter(armed, "bavarian_match")
        assert letter is not None and MO.status(armed, "bavarian_match") == MO.STATUS_FIRED
        rows = [e for e in armed.event_log if e.get("type") == "moment"]
        assert [(e["phase"], e["moment"], e["nation"]) for e in rows] == [
            ("arrived", "bavarian_match", "France")]
        notices = [n for n in armed.notifications.get_pending()
                   if (n.get("details") or {}).get("moment_id") == "bavarian_match"]
        assert len(notices) == 1

    def test_a_false_premise_is_passed_silently_after_its_window(self, armed):
        armed.diplomatic_states[armed._make_diplo_key("France", "Bavaria")] = "PEACE"
        armed.nation_relations[armed._make_diplo_key("France", "Bavaria")] = 10
        for turn in (8, 9, 10):
            _at(armed, turn)
            assert _tick(armed) == []
        _at(armed, 11)
        _tick(armed)
        assert MO.status_row(armed, "bavarian_match") == {"status": "passed", "turn": 11,
                                                           "reason": "premise"}
        assert not [e for e in armed.event_log if e.get("type") == "moment"]

    def test_holland_arrives_when_she_slips_and_not_when_she_holds(self, armed):
        _at(armed, 18)
        armed.vassals["Holland"]["loyalty"] = 90
        armed.moments["state"]["bavarian_match"] = {"status": "passed", "turn": 11, "reason": "premise"}
        from backend.game_logic.vassal import forecast_vassal_loyalty
        assert forecast_vassal_loyalty(armed, "France", "Holland")["forecast"] >= 0
        assert _tick(armed) == []                           # loyalty 90, a steady forecast
        armed.vassals["Holland"]["loyalty"] = 66
        _at(armed, 19)
        assert _tick(armed) == ["throne_of_holland"]

    def test_the_reich_arrives_a_turn_after_the_confederation_is_told(self, armed):
        state = ID._state(armed)
        state["road"], state["proclaimed_turn"] = "rhine", 10
        state["fulfilled"]["rhine.confederation"] = 19      # stamped at the end of turn 19
        for mid in ("bavarian_match", "throne_of_holland"):
            armed.moments["state"][mid] = {"status": "passed", "turn": 12, "reason": "premise"}
        _at(armed, 20)                                      # the morning that tells it
        assert _tick(armed) == []
        _at(armed, 21)                                      # lag 1
        assert _tick(armed) == ["crown_of_the_reich"]

    def test_the_reich_is_forsworn_on_another_road_and_never_varies(self, armed):
        state = ID._state(armed)
        state["road"], state["proclaimed_turn"] = "crowns", 10
        _at(armed, 12)
        _tick(armed)
        assert MO.status_row(armed, "crown_of_the_reich")["reason"] == "forsworn"
        assert MO.status_row(armed, "decree_of_berlin")["reason"] == "forsworn"

    def test_a_reich_resolving_at_the_verdict_is_passed(self, armed):
        state = ID._state(armed)
        state["road"], state["proclaimed_turn"] = "rhine", 10
        state["fulfilled"]["rhine.confederation"] = 42      # told at 43, lag 1 -> 44 = the Verdict
        for mid in ("bavarian_match", "throne_of_holland", "decree_of_berlin"):
            armed.moments["state"][mid] = {"status": "passed", "turn": 33, "reason": "premise"}
        _at(armed, 43)
        _tick(armed)
        assert MO.status_row(armed, "crown_of_the_reich")["reason"] == "verdict"

    def test_the_decree_arrives_only_where_it_would_shut_a_port(self, armed):
        for mid in ("bavarian_match", "throne_of_holland", "crown_of_the_reich"):
            armed.moments["state"][mid] = {"status": "passed", "turn": 20, "reason": "premise"}
        _at(armed, 29)
        assert _tick(armed) == []                           # Holland fights Britain: no bite
        _stage_decree_board(armed)
        _at(armed, 30)
        assert _tick(armed) == ["decree_of_berlin"]


# ═══════════════════════════════════════════════════════════════════════════
# Shown = applied — the closed op table on three boards
# ═══════════════════════════════════════════════════════════════════════════

_EVERY_SIMPLE_OP = {
    "id": "battery", "kind": "letter", "title": "The Battery", "turn": 5, "grace": 2,
    "when": {"predicate": "court_warm", "court": "Bavaria"}, "roads": ["any"],
    "voice": {"speaker": "cabinet"}, "record": "A staged letter.",
    "accept": {"caption": "Everything", "ops": [
        {"op": "gold", "amount": 1500}, {"op": "dp", "amount": 2},
        {"op": "relation", "court": "Bavaria", "delta": 20},
        {"op": "loyalty", "court": "Bavaria", "delta": 15},
        {"op": "alarm", "amount": 3, "source": "moment_bavarian_match"}]},
    "decline": {"caption": "Nothing", "ops": [{"op": "relation", "court": "Bavaria", "delta": -5}]},
}


def _battery_world(world, *, rich, clamp):
    world.moments = {"block": {"owner": "France", "pacing": {}, "deck": [copy.deepcopy(_EVERY_SIMPLE_OP)]},
                     "state": {"battery": {"status": "fired", "turn": 5}}}
    _vassalize(world, "Bavaria", loyalty=95 if clamp else 50)
    world.nation_relations[world._make_diplo_key("France", "Bavaria")] = 95 if clamp else 40
    world.threat_by_target["France"] = 99 if clamp else 30
    if rich:
        _rich(world)
    else:
        world.nation_gold["France"] = 100
    return MO.entry(world, "battery")


class TestShownIsApplied:
    @pytest.mark.parametrize("clamp", [False, True])
    def test_every_op_delivers_exactly_its_plan(self, world, clamp):
        e = _battery_world(world, rich=True, clamp=clamp)
        p = MO.plan(world, e, "accept")
        assert p["ok"], p["refusal"]
        rows = {r["op"]: r for r in p["rows"]}
        MO._apply(world, p)
        assert int(world.nation_gold["France"]) == rows["gold"]["after"]
        assert int(world.diplomatic_points) == rows["dp"]["after"]
        assert _rel(world, "Bavaria") == rows["relation"]["after"]
        assert int(world.vassals["Bavaria"]["loyalty"]) == rows["loyalty"]["courts"][0]["after"]
        assert int(world.threat_by_target["France"]) == rows["alarm"]["after"]
        if clamp:
            assert rows["relation"]["after"] == 100 and rows["alarm"]["after"] == 100
            assert rows["loyalty"]["courts"][0]["after"] == 100
            assert "95 → 100" in p["quote"]
        assert int(world.gold_spent_this_turn.get("France", 0)) >= 1500   # shown as Spent

    def test_a_poor_board_refuses_and_charges_nothing(self, world):
        e = _battery_world(world, rich=False, clamp=False)
        before = copy.deepcopy((world.nation_gold["France"], world.diplomatic_points,
                                _rel(world, "Bavaria"), world.threat_by_target["France"]))
        p = MO.plan(world, e, "accept")
        assert not p["ok"] and "1,500 gold is asked; the treasury holds 100." == p["refusal"]
        letter = MO.build_letter(world, e, 5)
        world.dialogue_manager.push(letter)
        _make_current(world, letter)
        result = MO.answer(world, letter, "accept")
        assert result["success"] is False and result.get("moment_stands")
        assert world.dialogue_manager.peek() is letter            # the letter stands
        assert (world.nation_gold["France"], world.diplomatic_points, _rel(world, "Bavaria"),
                world.threat_by_target["France"]) == before

    def test_the_autonomy_op_is_the_executor_s_own_plan(self, world):
        from backend.game_logic import vassal as V
        world.vassals["Holland"]["loyalty"] = 60
        _rich(world)
        e = copy.deepcopy(_block()["deck"][1])
        e["turn"] = 18
        world.moments = {"block": {"owner": "France", "deck": [e]},
                         "state": {"throne_of_holland": {"status": "fired", "turn": 18}}}
        p = MO.plan(world, MO.entry(world, "throne_of_holland"), "accept")
        plan = V.autonomy_change_plan(world, "Holland", 2, actor="France")
        assert p["ok"] and p["rows"][0]["loyalty_after"] == plan["loyalty_after"]
        dp = world.diplomatic_points
        MO._apply(world, p)
        assert world.vassals["Holland"]["autonomy"] == 2
        assert world.vassals["Holland"]["loyalty"] == plan["loyalty_after"]
        assert world.diplomatic_points == dp - 1
        assert "tribute 75% → 50%" in p["quote"]

    def test_the_decree_op_is_the_full_verb_admin_action_included(self, armed):
        """The critics' R3: `enact_law` never spends the admin action — the
        op does, as the executor would."""
        from backend.game_logic import naval, reforms
        _rich(armed)
        _stage_decree_board(armed)
        p = MO.plan(armed, MO.entry(armed, "decree_of_berlin"), "accept")
        assert p["ok"], p["refusal"]
        row = p["rows"][0]
        assert "1 administrative action" in p["quote"]
        admin = armed.admin_actions_remaining
        MO._apply(armed, p)
        assert reforms.is_in_force(reforms.find_law(armed, "France", "berlin_decree"))
        assert armed.admin_actions_remaining == admin - 1
        assert naval.closed_ports_against(armed, "Britain") == row["ports_after"] > row["ports_before"]

    def test_no_admin_action_closes_the_decree_with_the_law_s_own_words(self, armed):
        from backend.game_logic import reforms
        _rich(armed)
        armed.admin_actions_remaining = 0
        p = MO.plan(armed, MO.entry(armed, "decree_of_berlin"), "accept")
        assert not p["ok"] and p["refusal"] == reforms.law_refusal(armed, "France", "berlin_decree")


# ═══════════════════════════════════════════════════════════════════════════
# The transport through the real endpoints
# ═══════════════════════════════════════════════════════════════════════════

class TestTheTransport:
    def test_the_letter_reads_as_a_moment_on_every_read_seam(self, armed, client):
        _rich(armed)
        _at(armed, 8)
        _tick(armed)
        letter = _letter(armed, "bavarian_match")
        _make_current(armed, letter)
        assert T._letter_kind(letter) == "moment"
        popup = client.get("/pending_envoy").json()["incoming_proposal"]
        assert popup["is_moment"] and popup["proposal_type_display"] == "A Moment of History"
        assert popup["dialogue_id"] == letter["dialogue_id"]
        assert popup["from_nation"] == ""
        quotes = [a["quote"] for a in popup["answers"]]
        assert quotes[0].startswith("Seal the match: 2 diplomatic points")
        assert quotes[1] == "Let Baden keep her: Bavaria's goodwill 60 → 55."
        assert popup["unanswered_line"].startswith("If unanswered by Late January 1806:")
        rows = client.get("/mailbox").json()["items"]
        row = next(r for r in rows if r["proposal_type"] == "moment_letter")
        assert row["source_nation"] == "The Cabinet"
        assert row["summary_text"] == "A Moment of History: The Bavarian Match"

    def test_a_closed_accept_keeps_its_stamp_across_every_read(self, armed, client):
        """S14C-X8: the treaty restamp used to erase a closed stamp."""
        armed.nation_gold["France"] = 100
        _at(armed, 8)
        _tick(armed)
        letter = _letter(armed, "bavarian_match")
        _make_current(armed, letter)
        for _ in range(2):
            popup = client.get("/pending_envoy").json()["incoming_proposal"]
            accept = next(o for o in popup["options"] if o["action"] == "accept_ai_proposal")
            assert accept["enabled"] is False and "treasury holds 100" in accept["reason"]
        result = client.post("/respond_to_diplomatic_dialogue",
                             json={"choice": "accept_ai_proposal",
                                   "dialogue_id": letter["dialogue_id"]}).json()
        assert result["success"] is False and armed.dialogue_manager.peek() is letter

    def test_the_accept_applies_its_quote_through_the_endpoint(self, armed, client):
        _rich(armed)
        _at(armed, 8)
        _tick(armed)
        letter = _letter(armed, "bavarian_match")
        _make_current(armed, letter)
        quote = MO.plan(armed, MO.entry(armed, "bavarian_match"), "accept")
        rel, gold, dp = _rel(armed, "Bavaria"), armed.nation_gold["France"], armed.diplomatic_points
        with _quiet():
            result = client.post("/respond_to_diplomatic_dialogue",
                                 json={"choice": "accept_ai_proposal",
                                       "dialogue_id": letter["dialogue_id"]}).json()
        assert result["success"] is True, result
        assert _rel(armed, "Bavaria") == rel + 20
        assert armed.nation_gold["France"] == gold - 1000 and armed.diplomatic_points == dp - 2
        assert quote["ok"] and MO.status_row(armed, "bavarian_match")["answer"] == "accept"
        assert _letter(armed, "bavarian_match") is None
        assert not [n for n in armed.notifications.get_pending()
                    if (n.get("details") or {}).get("moment_id") == "bavarian_match"]
        assert [e["phase"] for e in armed.event_log if e.get("type") == "moment"] == ["arrived", "answered"]

    def test_the_counter_refuses_and_the_letter_stands(self, armed):
        from backend.commands.executor import CommandExecutor
        _at(armed, 8)
        _tick(armed)
        letter = _letter(armed, "bavarian_match")
        _make_current(armed, letter)
        result = CommandExecutor()._handle_counter_ai_proposal(letter, armed)
        assert result["success"] is False and armed.dialogue_manager.peek() is letter

    def test_a_moment_letter_never_locks_the_wizard(self, armed):
        """Seam 9 (A2): only a court's offer locks the wizard."""
        _at(armed, 8)
        _tick(armed)
        dm = armed.dialogue_manager
        letters = [d for d in [dm.peek()] + list(dm.iter_queue()) if d]
        others = [d for d in letters if d.get("type") in dm.CURRENT_TURN_OFFER_TYPES
                  and not MO.is_moment_letter(d)]
        assert any(MO.is_moment_letter(d) for d in letters)
        assert dm.has_current_turn_offers() == bool(others)

    def test_unanswered_it_lapses_as_its_decline_with_no_cooldown_key(self, armed):
        """S14C-X9: the `"Unknown"` fallback wrote cooldown keys for a court
        called Unknown."""
        _at(armed, 8)
        _tick(armed)
        letter = _letter(armed, "bavarian_match")
        dm = armed.dialogue_manager
        assert dm._extract_lapse_info(letter)["nation"] == ""
        rel = _rel(armed, "Bavaria")
        first = [x for x in dm.lapse_pending_offers(current_turn=8, world=armed)
                 if x.get("proposal_type") == "moment_letter"]
        assert first == [] and _letter(armed, "bavarian_match") is not None   # stands its first turn
        lapsed = [x for x in dm.lapse_pending_offers(current_turn=9, world=armed)
                  if x.get("proposal_type") == "moment_letter"]
        assert lapsed and lapsed[0]["nation"] == ""
        assert lapsed[0]["moment"]["line"].startswith("The Bavarian Match was left unanswered — Let Baden keep her")
        assert _rel(armed, "Bavaria") == rel - 5
        assert MO.status_row(armed, "bavarian_match")["status"] == "lapsed"

    def test_a_real_end_turn_lapse_writes_no_cooldown_and_tells_its_own_sentence(self, armed, client):
        from backend.campaign_log import format_event_oneliner
        from backend.game_logic.dispatch import _lapsed_offer_row
        _at(armed, 8)
        _tick(armed)
        assert _letter(armed, "bavarian_match") is not None
        with _quiet():
            C.post(client, {"command": "end turn"})          # ends turn 8: kept
            assert _letter(armed, "bavarian_match") is not None
            C.post(client, {"command": "end turn"})          # ends turn 9: lapses
        world = M.world
        assert _letter(world, "bavarian_match") is None
        keys = list((getattr(world, "ai_proposal_cooldowns", {}) or {}))
        assert not [k for k in keys if k.startswith("Unknown") or k.startswith("|")
                    or k.endswith("|moment_letter")], keys
        row = next(e for e in world.event_log if e.get("type") == "offer_lapsed"
                   and e.get("proposal_type") == "moment_letter")
        assert row["nation"] == "" and row["moment"]["id"] == "bavarian_match"
        assert format_event_oneliner(row).startswith("The Bavarian Match was left unanswered")
        assert _lapsed_offer_row(row)["line"].startswith("The Bavarian Match was left unanswered")

    def test_a_standing_moment_letter_moves_no_ai_reader(self, armed):
        """Seam 10: every court-keyed reader of the queue finds no court on a
        moment letter."""
        from backend.game_logic import ai_diplomacy as AI
        from backend.game_logic.envoy_digest import is_routine_small_court
        _at(armed, 8)
        _tick(armed)
        letter = _letter(armed, "bavarian_match")
        assert not is_routine_small_court(letter, armed)
        nations = list(armed.get_active_nations())
        with_letter = {n: AI._has_pending_proposal_from(n, armed) for n in nations}
        armed.dialogue_manager.remove_matching(lambda d: d is letter)
        without = {n: AI._has_pending_proposal_from(n, armed) for n in nations}
        assert with_letter == without
        assert "target_nation" not in letter and "source_nation" not in letter["context"]
        assert "proposal" not in letter["context"]


# ═══════════════════════════════════════════════════════════════════════════
# Pacing — R1, R2, R3, the gap and the open letter
# ═══════════════════════════════════════════════════════════════════════════

def _twin_block(second_turn):
    a = copy.deepcopy(_EVERY_SIMPLE_OP)
    a.update(id="first", turn=8, accept={"caption": "Yes", "ops": []})
    b = copy.deepcopy(a)
    b.update(id="second", turn=second_turn)
    return {"owner": "France", "pacing": {"max_open": 1, "min_gap": 3}, "deck": [a, b]}


class TestPacing:
    def test_r1_a_crisis_defers_and_r2_ends_the_letter_on_screen(self, armed):
        armed.war_intents = {"Prussia": {"coveter": "Prussia", "target": "Hanover",
                                         "opened_turn": 7, "foregrounded": True,
                                         "foregrounded_turn": 7}}
        rel = _rel(armed, "Bavaria")
        for turn in (8, 9):
            _at(armed, turn)
            assert _tick(armed) == []
            assert MO.status(armed, "bavarian_match") == ""
        _at(armed, 10)                                      # its grace ends under the crisis
        assert _tick(armed) == []
        assert MO.status_row(armed, "bavarian_match")["reason"] == "crowded"
        assert _rel(armed, "Bavaria") == rel - 5            # the decline applied
        receipt = [e for e in armed.pending_dispatch_events if e["type"] == "moment_receipt"]
        assert len(receipt) == 1 and "could not be laid before the Emperor" in receipt[0]["template_vars"]["line"]
        assert [e["phase"] for e in armed.event_log if e.get("type") == "moment"] == ["passed"]

    def test_r3_one_moment_a_morning(self, world):
        world.moments = MO.from_block(_twin_block(8))
        _at(world, 8)
        assert _tick(world) == ["first"]
        assert MO.status(world, "second") == ""

    def test_the_gap_and_the_open_letter_hold(self, world):
        world.moments = MO.from_block(_twin_block(9))
        _at(world, 8)
        assert _tick(world) == ["first"]
        world.moments["state"]["first"]["status"] = "answered"
        _at(world, 9)
        assert _tick(world) == []                           # within the gap
        _at(world, 11)
        assert _tick(world) == ["second"]
        world.moments = MO.from_block(_twin_block(11))
        _at(world, 8)
        _tick(world)                                        # `first` stands open
        _at(world, 11)
        assert _tick(world) == []                           # one open letter

    # S14C-X24 (S14c part 4): a letter once DUE — its premise true, its gate
    # open, inside its window — and deferred ends arrived or on screen;
    # `passed(premise)` is the silent word only for a board that contradicted
    # it for its whole window.
    _CRISIS = {"Prussia": {"coveter": "Prussia", "target": "Hanover", "opened_turn": 7,
                           "foregrounded": True, "foregrounded_turn": 7}}

    def _cool_bavaria(self, world):
        key = world._make_diplo_key("France", "Bavaria")
        world.diplomatic_states[key] = "PEACE"              # the alliance broken...
        world.nation_relations[key] = 10                    # ...and the court cold

    def test_x24_a_letter_due_under_a_crisis_ends_on_screen_when_its_court_cools(self, armed):
        armed.war_intents = copy.deepcopy(self._CRISIS)
        for turn in (8, 9):
            _at(armed, turn)
            assert _tick(armed) == []
        assert MO.was_due(armed, "bavarian_match") and armed.moments["due"] == {"bavarian_match": 8}
        self._cool_bavaria(armed)                           # the evening of T9
        _at(armed, 10)                                      # its last morning, the premise now false
        assert _tick(armed) == []
        assert MO.status_row(armed, "bavarian_match") == {"status": "passed", "turn": 10, "reason": "crowded"}
        assert _rel(armed, "Bavaria") == 5                  # the decline applied, as for any crowd-out
        receipt = [e for e in armed.pending_dispatch_events if e["type"] == "moment_receipt"]
        assert len(receipt) == 1 and "goodwill 10 → 5" in receipt[0]["template_vars"]["line"]
        assert [(e["phase"], e.get("reason")) for e in armed.event_log
                if e.get("type") == "moment"] == [("passed", "crowded")]

    def test_x24_a_due_letter_whose_premise_returns_still_arrives(self, armed):
        armed.war_intents = copy.deepcopy(self._CRISIS)
        _at(armed, 8)
        assert _tick(armed) == []                           # due, deferred
        armed.war_intents = {}
        self._cool_bavaria(armed)
        _at(armed, 9)
        assert _tick(armed) == [] and MO.status(armed, "bavarian_match") == ""   # not its last morning
        armed.diplomatic_states[armed._make_diplo_key("France", "Bavaria")] = "ALLIANCE"
        _at(armed, 10)
        assert _tick(armed) == ["bavarian_match"]

    def test_x24_a_letter_never_due_passes_in_silence(self, armed):
        self._cool_bavaria(armed)
        for turn in (8, 9, 10):
            _at(armed, turn)
            assert _tick(armed) == []
        _at(armed, 11)
        _tick(armed)
        assert MO.status_row(armed, "bavarian_match")["reason"] == "premise"
        assert not MO.was_due(armed, "bavarian_match") and "due" not in armed.moments
        assert not [e for e in armed.pending_dispatch_events if e["type"] == "moment_receipt"]

    def test_x24_the_due_mark_survives_a_save(self, armed):
        from backend.models.world_state import WorldState
        armed.war_intents = copy.deepcopy(self._CRISIS)
        _at(armed, 8)
        _tick(armed)
        restored = WorldState.from_dict(json.loads(json.dumps(armed.to_dict())))
        assert restored.moments == armed.moments and MO.was_due(restored, "bavarian_match")


# ═══════════════════════════════════════════════════════════════════════════
# Saves — every status round-trips; the backfill
# ═══════════════════════════════════════════════════════════════════════════

class TestSaves:
    def test_every_status_survives_a_round_trip(self, armed):
        from backend.models.world_state import WorldState
        armed.moments["state"] = {
            "bavarian_match": {"status": "answered", "turn": 8, "answer": "accept", "answered_turn": 8},
            "throne_of_holland": {"status": "lapsed", "turn": 18, "answer": "decline", "lapsed_turn": 19},
            "crown_of_the_reich": {"status": "passed", "turn": 22, "reason": "forsworn"},
            "decree_of_berlin": {"status": "fired", "turn": 29},
        }
        restored = WorldState.from_dict(json.loads(json.dumps(armed.to_dict())))
        assert restored.moments == armed.moments
        for reason in MO.PASS_REASONS:
            armed.moments["state"]["crown_of_the_reich"]["reason"] = reason
            assert WorldState.from_dict(json.loads(json.dumps(armed.to_dict()))).moments == armed.moments

    def test_the_backfill_passes_what_closed_before_the_save(self, world):
        data = {"moments": _block()}
        _at(world, 10)
        store = MO.backfill_store(world, data, "historical")
        assert store["state"] == {"bavarian_match": {"status": "passed", "turn": 10,
                                                     "reason": "before_save"}}
        _at(world, 20)
        assert set(MO.backfill_store(world, data, "historical")["state"]) == {
            "bavarian_match", "throne_of_holland"}

    def test_the_backfill_passes_a_causal_entry_already_due(self, world):
        state = ID._state(world)
        state["road"], state["fulfilled"]["rhine.confederation"] = "rhine", 15
        _at(world, 20)
        store = MO.backfill_store(world, {"moments": _block()}, "historical")
        assert store["state"]["crown_of_the_reich"]["reason"] == "before_save"

    def test_the_backfill_uses_the_save_s_own_seed(self, world):
        _at(world, 1)
        for seed in SWEEP_SEEDS:
            from backend.game_logic.campaign_variance import resolve_moment_turns
            expected = resolve_moment_turns(_block(), seed)["deck"][0]["turn"]
            assert MO.backfill_store(world, {"moments": _block()}, seed)["block"]["deck"][0]["turn"] == expected

    def test_a_carried_store_is_never_overwritten(self, armed):
        from backend.save_manager import _backfill_moments
        armed.moments["state"]["bavarian_match"] = {"status": "passed", "turn": 11, "reason": "premise"}
        before = copy.deepcopy(armed.moments)
        _backfill_moments(armed)
        assert armed.moments == before

    def test_to_dict_stays_at_500_lines(self):
        """S14C-X16: the `moments` key folds into the designs' line."""
        src = (BACKEND / "models" / "world_state.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "to_dict"
                  and n.lineno > 8000)
        assert fn.end_lineno - fn.lineno + 1 <= 500
        assert '"moments": copy.deepcopy(self.moments)' in src


# ═══════════════════════════════════════════════════════════════════════════
# The siblings
# ═══════════════════════════════════════════════════════════════════════════

class TestTheNonTreatyRegistry:
    """S14C-X8, X18–X20: a letter that ratifies no treaty between the pair is
    never judged as one — a PEACE pair's Yield or Accept is not closed as a
    'downgrade' on the first read."""

    def test_an_ultimatum_s_yield_stays_open_after_a_read(self, world):
        from backend.game_logic import ai_diplomacy as AI
        from backend.game_logic.diplomatic_templates import generate_ultimatum_terms
        with _quiet():
            terms = generate_ultimatum_terms("France", world, issuer="Prussia")
            dialogue = AI._build_ai_ultimatum_dialogue(
                AI._make_proposal("Prussia", "ultimatum", 7, terms, world), world)
            world.dialogue_manager.push(dialogue)
        assert world.get_diplomatic_state("France", "Prussia") == "PEACE"
        M._build_pending_envoy_popup_from_dialogue(world, world.dialogue_manager.peek())
        yield_option = next(o for o in dialogue["options"] if o["action"] == "accept_ai_ultimatum")
        assert yield_option.get("enabled", True) is not False
        assert T.CLOSED_CLAUSE_KEY not in yield_option

    def test_an_offered_crown_s_accept_stays_open(self, world):
        from backend.game_logic import ai_diplomacy as AI
        terms = {"type": "offer_vassalage", "proposer_nation": "Sweden", "target_nation": "France",
                 "demands": [], "sweeteners": []}
        with _quiet():
            proposal = AI._make_proposal("Sweden", "offer_vassalage", 9, terms, world)
            proposal["_force_send"] = True
            AI.deliver_ai_proposal(proposal, world)
        dialogue = world.dialogue_manager.peek()
        accept = next(o for o in dialogue["options"] if o["action"] == "accept_ai_proposal")
        assert accept.get("enabled", True) is not False and T.CLOSED_CLAUSE_KEY not in accept

    def test_a_broker_s_ask_is_answered_on_its_own_road(self, world):
        letter = {"type": "incoming_proposal", "target_nation": "Prussia",
                  "context": {"proposal_type": "broker_peace", "source_nation": "Prussia",
                              "proposal": {"type": "broker_peace", "proposer_nation": "Prussia",
                                           "target_nation": "Austria", "war_id": "w"}}}
        assert T._letter_kind(letter) == "broker_peace"
        assert T.can_sign(world, letter, action="accept_ai_proposal").ok

    def test_the_registry_reads_dialogues_never_a_bare_proposal(self):
        assert T.non_treaty_kind({"type": "offer_vassalage", "proposer_nation": "Sweden",
                                  "target_nation": "France"}) == ""
        assert T._letter_kind({"type": "offer_vassalage", "proposer_nation": "Sweden",
                               "target_nation": "France"}) == "treaty"

    def test_every_label_the_producers_send_has_a_road(self):
        """The census: every proposal type a producer hands `_make_proposal`
        is a treaty the ratifier signs, a label the terms rewrite to one, or
        a registered non-treaty letter — none falls through to be judged as
        a peace."""
        rewritten = {"friendly_gift", "opportunistic", "design_purchase", "sell_neutrality",
                     "harsh_peace", "armistice_stalemate", "armistice_winning"}
        own_arms = {"call_to_arms", "client_petition"}
        known = set(T.TREATY_STATE_MAP) | rewritten | own_arms | set(T.NON_TREATY_LETTERS)
        labels = set()
        for path in BACKEND.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and getattr(node.func, "id", getattr(node.func, "attr", ""))
                        == "_make_proposal" and len(node.args) >= 2
                        and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str)):
                    labels.add(node.args[1].value)
        assert labels, "the census found no producer"
        assert labels <= known, sorted(labels - known)


class TestTheAlarmLabels:
    def test_every_alarm_source_has_a_label(self):
        """S14C-X4: every literal source `add_threat` / `reduce_threat` is
        called with resolves to a label, never its raw key title-cased."""
        from backend.game_logic.diplomatic_ledger import _THREAT_SOURCE_LABELS, _threat_source_label
        missing = []
        for path in BACKEND.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call)
                        and getattr(node.func, "id", getattr(node.func, "attr", "")) in ("add_threat",
                                                                                      "reduce_threat")):
                    continue
                if len(node.args) < 3:
                    continue
                arg = node.args[2]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    key = arg.value
                elif isinstance(arg, ast.JoinedStr) and arg.values and isinstance(arg.values[0], ast.Constant):
                    key = str(arg.values[0].value) + "x"   # a dynamic family: its prefix
                else:
                    continue
                label = _threat_source_label(None, key)
                if key not in _THREAT_SOURCE_LABELS and label == key.replace("_", " ").title():
                    missing.append(f"{path.name}:{node.lineno} {key}")
        assert not missing, missing

    def test_the_moments_alarm_sources_are_labelled_and_never_vp1_s(self):
        from backend.game_logic.diplomatic_ledger import _THREAT_SOURCE_LABELS
        sources = {op["source"] for e in _block()["deck"] for side in ("accept", "decline")
                   for op in e[side]["ops"] if op["op"] == "alarm"}
        assert sources == {"moment_bavarian_match", "moment_reich"}
        assert sources <= set(_THREAT_SOURCE_LABELS)
        assert not sources & {ID.ACT_ALARM_SOURCE, ID.DECISIVE_PEACE_SOURCE,
                              "act_of_confederation", "schonbrunn", "blockade"}

    def test_no_op_reaches_a_vp1_verb(self):
        """§3.6: the op table has no proclamation, Act or designs write."""
        src = (BACKEND / "game_logic" / "moments.py").read_text(encoding="utf-8")
        for forbidden in ("proclaim(", "decree(", "stamp_decisive_peace", "_apply_teeth",
                          "imperial_designs.state", "ID._state"):
            assert forbidden not in src, forbidden
        assert set(MO.OPS) == {"gold", "dp", "relation", "alarm", "loyalty", "autonomy", "enact_law"}

    def test_no_nation_literal_in_the_engine(self):
        """Q6: the deck is France's content, never the code's."""
        src = (BACKEND / "game_logic" / "moments.py").read_text(encoding="utf-8")
        from backend.nation_config import EUROPE_ROSTER
        code = re.sub(r'""".*?"""', "", src, flags=re.S)
        code = "\n".join(line.split("#")[0] for line in code.splitlines())
        found = [n for n in EUROPE_ROSTER if re.search(rf'["\']{n}["\']', code)]
        assert not found, found


class TestTheRoadState:
    def test_road_state_reads_the_proclamation(self, world):
        state = ID._state(world)
        assert ID.road_state(world, "rhine") == "open"
        state["road"] = "rhine"
        assert (ID.road_state(world, "rhine"), ID.road_state(world, "crowns")) == ("proclaimed", "forsworn")

    def test_no_module_re_derives_forsworn(self):
        """S14C-X17: every inline "forsworn" test routes through `road_state`."""
        shapes = [r"bool\(chosen\) and \w+ (?:!=|not in)", r"want not in \(ACT_ANY_ROAD, chosen\)",
                  r"if chosen and rid != chosen", r"proclaimed_road\(world\) != road_id"]
        for path in BACKEND.rglob("*.py"):
            src = path.read_text(encoding="utf-8")
            for shape in shapes:
                assert not re.search(shape, src), f"{path.name}: {shape}"


class TestTheSharedHelpers:
    def test_adjust_loyalty_clamps_and_reports_what_it_delivered(self, world):
        from backend.game_logic.vassal import adjust_loyalty
        _vassalize(world, "Bavaria", loyalty=95)
        assert adjust_loyalty(world, "Bavaria", 15) == {"before": 95, "after": 100, "delivered": 5}
        assert adjust_loyalty(world, "Bavaria", -200)["after"] == 0
        assert adjust_loyalty(world, "Bavaria", 5, lord="Austria") is None
        assert adjust_loyalty(world, "Atlantis", 5) is None

    def test_the_autonomy_plan_is_what_the_executor_applies(self, world):
        from backend.game_logic import vassal as V
        world.vassals["Holland"]["loyalty"] = 60
        world.diplomatic_points = 3
        plan = V.autonomy_change_plan(world, "Holland", 2, actor="France")
        result = V.change_vassal_autonomy(world, "Holland", 2, actor="France")
        assert result["success"] and plan["ok"]
        assert world.vassals["Holland"]["loyalty"] == plan["loyalty_after"]
        assert world.diplomatic_points == 2
        assert (plan["tribute_before"], plan["tribute_after"]) == (75, 50)
        assert V.autonomy_change_plan(world, "Holland", 2, actor="France")["message"].endswith("already Autonomous.")

    def test_the_foreground_pair(self, world):
        from backend.game_logic.war_council import foreground_in_tenure, record_in_tenure
        assert not record_in_tenure({"foregrounded": False}, 5)
        assert record_in_tenure({"foregrounded": True, "foregrounded_turn": 4}, 5)
        world.war_intents = {}
        assert not foreground_in_tenure(world)
        world.war_intents = {"Prussia": {"foregrounded": True, "foregrounded_turn": world.current_turn}}
        assert foreground_in_tenure(world)

    def test_the_as_if_decree_read_leaves_the_live_law_alone(self, world):
        from backend.game_logic import naval, reforms
        _stage_decree_board(world)
        assert naval.decree_clients(world, "Britain") == []
        assert naval.decree_clients(world, "Britain", decree_by="France") == ["Holland"]
        assert not reforms.is_in_force(reforms.find_law(world, "France", "berlin_decree"))
        assert (naval.closed_ports_against(world, "Britain", decree_by="France")
                > naval.closed_ports_against(world, "Britain"))


class TestTheLogType:
    def test_the_moment_type_is_registered_and_speaks_every_phase(self):
        from backend import campaign_log as CL
        assert "moment" in CL.CAMPAIGN_LOG_TYPES and CL.CATEGORY_MAP["moment"] == "diplomacy"
        assert "moment" in CL.LOG_TIER_NOTABLE
        for phase, needle in (("arrived", "laid before the Emperor"), ("answered", "Seal the match")):
            line = CL.format_event_oneliner({"type": "moment", "phase": phase, "nation": "France",
                                             "title": "The Bavarian Match", "caption": "Seal the match"})
            assert needle in line
        assert not CL.format_event_oneliner({"type": "moment"}).startswith("Event:")
