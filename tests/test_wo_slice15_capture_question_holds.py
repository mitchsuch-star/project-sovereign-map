"""Row WO, slice 15 — "The Capture Question Holds" (August 21, 2026).

One lifecycle, five filed holes plus one found while building. The single
slot `world.pending_capture_choice` could be created, crossed, clobbered,
misapplied and dropped without the player ever being told:

  WO-22 (P1) the auto-end-turn defer never read the slot, so a capture on
        the last AP auto-advanced across the unanswered question;
  WO-26 (P2) two of the three producers were BARE writes and silently
        overwrote an earlier marshal's unanswered question;
  WO-27 (P2, re-filed from P3) the estate prune lacked the pending-choice
        carve-out its four siblings carry;
  WO-29 (P3) the typed answer had no identity check — and the filed fix
        ("thread the dialogue_id") is unbuildable, so identity is bound by
        CONTENT instead;
  WO-30 (P3) `/load` never surfaced a restored question, on either side of
        the wire;
  WO-34 (new) a naval landing mounted the question and shipped a response
        that could not render it.

Landing record: docs/WEIRD_OUTCOMES_SPEC.md §3 slice 15.

Every test below names, in its docstring, the mutation that kills it. The
two structural pins (the soft-lock ordering pin and the `.gd` body pin) are
mutation-tested in the mutation sweep recorded in the landing record — a
structural pin whose mutation nobody ran is a comment with a `def` in front
of it, which is how slice 7's drift pin hid eight leaks behind a green 30/30.
"""

import contextlib
import io
import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.commands.executor import CommandExecutor
from backend.models.marshal import Marshal
from backend.models.region import get_starting_controllers
from backend.models.world_state import (
    WorldState,
    apply_secure_effects,
    build_capture_choice,
    mount_or_auto_secure_capture,
    plunder_yield,
)

REPO = Path(__file__).resolve().parents[1]
MAIN_GD = (REPO / "godot-client" / "project-sovereign" / "scripts" / "main.gd")
MAIN_PY = REPO / "backend" / "main.py"
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


def _suppress():
    return contextlib.redirect_stdout(io.StringIO())


def _world():
    """The legacy fixture world with Lyon declared FOREIGN.

    CA8-13: liberating France's own starting soil asks no question, and Lyon
    is French homeland in this fixture — so it must be declared foreign for
    a capture here to be the conquest these tests mean to exercise (the
    recipe is `test_plunder_secure.TestPlayerCaptureTriggersPopup`).
    """
    world = WorldState(player_nation="France")
    world._starting_controllers = {
        **get_starting_controllers(), "Lyon": "Britain",
        "Belgium": "Britain",
    }
    world.regions["Paris"].controller = "France"
    for name in ("Lyon", "Belgium"):
        world.regions[name].controller = "Britain"
        world.regions[name].stability = 80
        world.regions[name].garrison_strength = 0
        world.regions[name].garrison_detachment = False
    for m in list(world.marshals.values()):
        if m.location in ("Lyon", "Belgium") and m.nation != "France":
            m.location = "Waterloo"
    ney = world.get_marshal("Ney")
    ney.location = "Paris"
    ney.strength = 30000
    world.pending_capture_choice = None
    return world, {"world": world}


def _attack(world, gs, marshal="Ney", target="Lyon"):
    executor = CommandExecutor()
    parsed = {"success": True,
              "command": {"action": "attack", "marshal": marshal,
                          "target": target}}
    with _suppress():
        return executor.execute(parsed, gs)


def _drain_ap(world, command_points=1):
    """Both pools must empty for `should_end_turn` — `world_state.use_action`
    reads `actions_remaining <= 0 and admin_actions_remaining <= 0`. A
    last-COMMAND-point attack with admin AP still in hand does NOT
    auto-advance; the filed row's "last AP" wording was narrower than it
    sounded."""
    world.actions_remaining = command_points
    world.admin_actions_remaining = 0


def _offer_dialogue(nation="Prussia"):
    return {
        "type": "incoming_proposal",
        "target_nation": nation,
        "talleyrand_text": f"Sire, {nation} proposes open borders.",
        "options": [{"label": "Accept", "description": "",
                     "action": "accept_ai_proposal"}],
        "context": {"proposal": {"type": "open_borders",
                                 "proposer_nation": nation},
                    "source_nation": nation,
                    "proposal_type": "open_borders"},
        "turn_created": 1,
        "blocking": False,
    }


# ═══════════════════════════════════════════════════════════════════
# WO-22 — the auto-advance defers on the capture question
# ═══════════════════════════════════════════════════════════════════


class TestWO22TheAutoAdvanceDefers:

    def test_last_ap_capture_does_not_auto_advance(self):
        """The headline. Mutation that kills it: restore the defer to
        `if should_auto_end_turn and world.dialogue_manager
        .has_current_turn_offers():`."""
        world, gs = _world()
        _drain_ap(world)
        turn_before = world.current_turn
        result = _attack(world, gs)
        assert result["success"] is True
        assert world.regions["Lyon"].controller == "France"
        assert world.pending_capture_choice is not None
        assert world.current_turn == turn_before, (
            "the turn advanced across an unanswered capture question")
        assert result["action_info"]["turn_advanced"] is False

    def test_the_notice_names_the_province_and_its_price(self):
        """The defer states its terms — the same priced restatement the
        refusal and stale-answer paths speak through. Mutation: replace
        `self._capture._pending_prompt(pending)` with a bare
        "a decision is pending"."""
        world, gs = _world()
        _drain_ap(world)
        gold = plunder_yield(world.regions["Lyon"])
        result = _attack(world, gs)
        msg = result.get("message", "")
        assert "All actions are spent" in msg
        assert "Lyon" in msg
        assert f"{gold:,}" in msg
        assert "'plunder'" in msg and "'secure'" in msg

    def test_the_typed_move_producer_defers_too(self):
        """The second producer. A fix written against the attack RESULT dict
        instead of world state passes the test above and leaves this red.
        Mutation: make `_auto_end_turn_defer_notice` read
        `result.get("pending_capture_choice")`."""
        world, gs = _world()
        _drain_ap(world)
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        turn_before = world.current_turn
        executor = CommandExecutor()
        parsed = {"success": True,
                  "command": {"action": "move", "marshal": "Ney",
                              "target": "Lyon"}}
        with _suppress():
            result = executor.execute(parsed, gs)
        assert result["success"] is True
        assert world.regions["Lyon"].controller == "France"
        assert world.pending_capture_choice is not None
        assert world.current_turn == turn_before
        assert "All actions are spent" in result.get("message", "")

    def test_the_estate_stage_defers_in_its_own_words(self):
        """Stage-agnostic by construction — the defer reads the FIELD, not
        `stage`. Mutation: gate the defer on
        `pending.get("stage") != "estate"`."""
        world, gs = _world()
        _drain_ap(world)
        world.pending_capture_choice = {
            "stage": "estate", "region": "Lyon", "capturer": "Ney",
            "estate_holder": "Blucher", "windfall": 400,
            "options": ["confiscate", "respect"],
        }
        executor = CommandExecutor()
        notice = executor._auto_end_turn_defer_notice(world)
        assert "Blucher" in notice
        assert "'confiscate'" in notice and "'respect'" in notice

    def test_both_reasons_are_stated_when_both_apply(self):
        """A notice that hides the second reason sends the player to end the
        turn explicitly and be refused again. Mutation: `return` after the
        first reason instead of joining."""
        world, gs = _world()
        _drain_ap(world)
        world.dialogue_manager.push(_offer_dialogue())
        result = _attack(world, gs)
        msg = result.get("message", "")
        assert "Lyon" in msg
        assert "unanswered envoys remain" in msg

    def test_nothing_pending_still_auto_advances(self):
        """FALSIFIABLE NEGATIVE — the control arm. A truthiness slip that
        deferred unconditionally would freeze every campaign. Mutation:
        make `_auto_end_turn_defer_notice` return a constant string."""
        world, gs = _world()
        _drain_ap(world)
        turn_before = world.current_turn
        executor = CommandExecutor()
        parsed = {"success": True,
                  "command": {"action": "scout", "marshal": "Ney",
                              "target": "Lyon"}}
        with _suppress():
            executor.execute(parsed, gs)
        assert world.pending_capture_choice is None
        assert world.current_turn == turn_before + 1

    def test_no_capture_answer_route_runs_through_execute(self, swapped):
        """THE SOFT-LOCK PIN, and the reason the defer is safe at all.

        After the defer the player holds 0 AP in both pools and the
        pending-choice block at the head of `execute()` refuses every
        command, `end turn` included. The only exit is answering — and that
        works solely because neither answer route passes through
        `execute()`. Route one through it and this slice's defer becomes a
        soft-lock with no player exit.

        Behavioural, not textual: both routes are driven with the slot full
        and both pools empty. Mutation: move the typed capture router in
        `main.py` below the `executor.execute(` call, or delete the
        `/capture_choice` endpoint's direct `handle_capture_choice` call.
        """
        client, m = swapped
        for route in ("typed", "endpoint"):
            m.world.pending_capture_choice = None
            region_name = next(
                r.name for r in m.world.regions.values()
                if r.controller == m.world.player_nation)
            m.world.pending_capture_choice = build_capture_choice(
                m.world, m.world.regions[region_name], "Ney", "Britain")
            m.world.actions_remaining = 0
            m.world.admin_actions_remaining = 0
            if route == "typed":
                data = client.post("/command",
                                   json={"command": "secure"}).json()
            else:
                data = client.post(
                    "/capture_choice", json={"choice": "secure"}).json()
            assert data.get("success") is True, (
                f"the {route} answer route was refused with 0 AP — the "
                f"WO-22 defer is a soft-lock")
            assert m.world.pending_capture_choice is None


# ═══════════════════════════════════════════════════════════════════
# WO-26 — the slot cannot be clobbered
# ═══════════════════════════════════════════════════════════════════


class TestWO26TheQuestionIsNotOverwritten:

    def test_second_capture_secures_rather_than_deleting_the_first(self):
        """The combat producer. Mutation: restore the bare
        `world.pending_capture_choice = build_capture_choice(...)` in
        `combat_executor._attempt_region_capture`."""
        world, gs = _world()
        earlier = {"region": "Elsewhere", "capturer": "Augereau",
                   "previous_controller": "Austria"}
        world.pending_capture_choice = earlier
        lyon = world.regions["Lyon"]
        lyon.buildings = [{"type": "market"}]
        lyon.building_under_construction = {"type": "fortification"}
        executor = CommandExecutor()
        with _suppress():
            capture = executor._combat._attempt_region_capture(
                world.get_marshal("Ney"), "Lyon", world, gs)
        assert capture["captured"] is True
        assert world.pending_capture_choice is earlier, (
            "the earlier marshal's unanswered question was overwritten")
        assert capture["capture_choice"] == "secure"
        assert capture["auto_secured"] is True
        assert lyon.stability == 25
        assert all(b.get("damaged") for b in lyon.buildings)
        assert lyon.building_under_construction is None
        rows = [e for e in world.event_log
                if e.get("type") == "region_captured"
                and e.get("region") == "Lyon"]
        assert len(rows) == 1 and rows[0]["method"] == "secure"

    def test_an_empty_slot_still_asks(self):
        """FALSIFIABLE NEGATIVE — the guard must not eat the ordinary
        interactive question. Mutation: drop the `world
        .pending_capture_choice is not None` test and always auto-secure."""
        world, gs = _world()
        executor = CommandExecutor()
        with _suppress():
            capture = executor._combat._attempt_region_capture(
                world.get_marshal("Ney"), "Lyon", world, gs)
        assert capture["captured"] is True
        assert capture["capture_choice"] is None
        assert capture["auto_secured"] is False
        assert world.pending_capture_choice["region"] == "Lyon"

    def test_two_occupations_completing_on_one_tick_keep_the_first(self):
        """The occupation producer — a distinct seam. The combat fix alone
        passes the first test here and leaves this red. Mutation: restore
        the bare write in `_apply_occupation_capture_effects`."""
        world, _gs = _world()
        for name, marshal_name in (("Lyon", "Ney"), ("Belgium", "Davout")):
            m = world.get_marshal(marshal_name)
            assert m is not None, marshal_name
            m.location = name
            m.occupation_region = name
            m.occupation_turns_held = 0
            m.occupation_turns_required = 1
        with _suppress():
            world._process_tactical_states()
        pending = world.pending_capture_choice
        assert pending is not None
        first, second = pending["region"], (
            "Belgium" if pending["region"] == "Lyon" else "Lyon")
        assert world.regions[second].controller == "France"
        assert world.regions[second].stability == 25
        rows = [e for e in world.event_log
                if e.get("type") == "region_captured"
                and e.get("region") == second]
        assert len(rows) == 1 and rows[0]["method"] == "secure", (
            f"{second} was captured and then silently dropped while "
            f"{first}'s question stood")

    def test_secure_effects_have_one_implementation(self):
        """The hoist earns its keep: a change to `apply_secure_effects` that
        the answered "secure" path did not inherit is now impossible.

        The comparative half alone would be INERT — measured in this slice's
        mutation sweep: dropping the watchtower arm changes BOTH paths, so
        they stay equal and the test stays green. It is kept because it binds
        the real drift (someone re-inlining a divergent `_apply_secure`) and
        paired with ABSOLUTE assertions below, which is what makes a dropped
        arm red.
        """
        world, gs = _world()

        def _seed(region):
            region.controller = "France"
            region.stability = 80
            region.plundered = True
            region.buildings = [{"type": "market"}, {"type": "stable"}]
            region.building_under_construction = {"type": "fortification"}
            region.watchtower = "active"
            return region

        direct = _seed(world.regions["Lyon"])
        answered = _seed(world.regions["Belgium"])
        apply_secure_effects(direct)
        world.pending_capture_choice = {
            "region": "Belgium", "capturer": "Ney",
            "previous_controller": "Britain"}
        executor = CommandExecutor()
        with _suppress():
            executor.handle_capture_choice("secure", gs)

        def _shape(r):
            return (r.stability, r.plundered,
                    [b.get("damaged") for b in r.buildings],
                    r.building_under_construction,
                    getattr(r, "watchtower", "none"))

        assert _shape(direct) == _shape(answered)
        # Absolute, so a dropped arm in the ONE implementation reds here
        # even though both paths would drop it together.
        assert direct.stability == 25
        assert direct.plundered is False
        assert all(b.get("damaged") for b in direct.buildings)
        assert direct.building_under_construction is None
        assert direct.watchtower == "damaged"

    def test_one_writer_census(self):
        """CENSUS — the guard is only structural if nothing else writes the
        slot for a fresh capture. Every `world.pending_capture_choice = …`
        in backend/ must be one of: the shared producer's mount, an answer
        consuming it (`= None`), or the game-over cleanup.

        Mutation: add a bare `world.pending_capture_choice = {...}` anywhere
        in backend/ and this reds naming the file and line.
        """
        allowed = {
            # the ONE mount, inside the shared producer
            ("backend/models/world_state.py", "build_capture_choice("),
            # answers consuming the question
            ("backend/commands/capture_executor.py", "None"),
            # W6-8 stage transition, on a slot the answer just cleared
            ("backend/commands/capture_executor.py", "estate_pending"),
            # game-over modal cleanup
            ("backend/game_logic/turn_manager.py", "None"),
            # save restore — the question round-trips whole
            ("backend/models/world_state.py", "data.get("),
        }
        offenders = []
        found = 0
        for path in sorted((REPO / "backend").rglob("*.py")):
            rel = path.relative_to(REPO).as_posix()
            for i, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), 1):
                stripped = line.strip()
                if not re.match(
                        r"^(self|world)\.pending_capture_choice\s*=\s*(?!=)",
                        stripped):
                    continue
                found += 1
                rhs = stripped.split("=", 1)[1].strip()
                if not any(rel == f and rhs.startswith(token)
                           for f, token in allowed):
                    offenders.append(f"{rel}:{i}  {stripped}")
        assert found >= 4, (
            f"the census matched only {found} assignments — the regex has "
            f"drifted off the code it is supposed to be watching")
        assert not offenders, (
            "bare writes to the single-slot capture question:\n"
            + "\n".join(offenders))


# ═══════════════════════════════════════════════════════════════════
# WO-27 — an open question keeps the estate on the rolls
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def europe():
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _estate_world(europe):
    """A France-held province that funds an AUSTRIAN marshal's estate, with
    the plunder/secure question still open on it.

    The province must have started under a THIRD party: both producers
    short-circuit on `is_own_soil_recapture`, so an Austrian estate on
    Austrian-origin soil could never raise the question in the first place.
    """
    world = WorldState.from_dict(json.loads(json.dumps(europe.to_dict())))
    holder = next(m for m in world.marshals.values() if m.nation == "Austria")
    region = next(r for r in world.regions.values()
                  if r.controller == "Austria"
                  and world._starting_controllers.get(r.name) == "Austria"
                  and not getattr(r, "is_capital", False))
    # A third party's soil that Austria took and France has now taken back.
    world._starting_controllers[region.name] = "Bavaria"
    holder.dotation_regions = [region.name]
    region.controller = "France"
    world.pending_capture_choice = build_capture_choice(
        world, region, "Ney", "Austria")
    return world, holder, region


class TestWO27TheEstateSurvivesTheQuestion:

    def test_open_question_keeps_the_estate_on_the_rolls(self, europe):
        """Mutation: drop `and not capture_choice_pending(self, r)` from the
        prune's `lost` comprehension."""
        world, holder, region = _estate_world(europe)
        world._process_dotation_state()
        assert region.name in holder.dotation_regions
        assert not [e for e in world.event_log
                    if e.get("type") == "estate_lost"
                    and e.get("region") == region.name]

    def test_without_a_question_the_estate_is_still_pruned(self, europe):
        """FALSIFIABLE NEGATIVE — the carve-out is not a blanket amnesty.
        Mutation: make `capture_choice_pending` return True
        unconditionally."""
        world, holder, region = _estate_world(europe)
        world.pending_capture_choice = None
        world._process_dotation_state()
        assert region.name not in holder.dotation_regions
        assert [e for e in world.event_log
                if e.get("type") == "estate_lost"
                and e.get("region") == region.name]

    def test_the_estate_question_still_mounts_after_the_prune(self, europe):
        """The consequence the filed row missed and the larger half of the
        defect: `find_enemy_estate_holder` reads `dotation_regions` raw, so
        a pruned estate means the W6-8 confiscate/respect question is never
        asked at all — no windfall, no goodwill, an `estate_lost` fired in
        its place. Same mutation as above."""
        world, holder, region = _estate_world(europe)
        world._process_dotation_state()
        executor = CommandExecutor()
        with _suppress():
            result = executor.handle_capture_choice(
                "secure", {"world": world})
        assert result["success"] is True
        pending = world.pending_capture_choice
        assert pending is not None and pending.get("stage") == "estate"
        assert pending["estate_holder"] == holder.name

    def test_respect_after_the_prune_is_not_a_paid_no_op(self, europe):
        """The filed row's own consequence, stated precisely: the +5 DOES
        fire (neither `respected_estate_mod` nor `is_estate_respected` reads
        `dotation_regions`) and is then REVOKED on the next advance by
        `prune_respected_estates`, which drops entries whose region is not
        on the holder's rolls. Same mutation."""
        from backend.game_logic.dotation import (
            RESPECT_ACCEPTANCE_BONUS, respected_estate_mod,
        )
        world, holder, region = _estate_world(europe)
        world._process_dotation_state()
        executor = CommandExecutor()
        with _suppress():
            executor.handle_capture_choice("secure", {"world": world})
            executor.handle_capture_choice("respect", {"world": world})
        assert respected_estate_mod(world, "France", holder.nation) == (
            RESPECT_ACCEPTANCE_BONUS)
        world._dotation_processed_turn = None
        world.current_turn += 1
        world._process_dotation_state()
        assert region.name in holder.dotation_regions
        assert respected_estate_mod(world, "France", holder.nation) == (
            RESPECT_ACCEPTANCE_BONUS), (
            "the courtesy was paid for and then revoked one turn later")


# ═══════════════════════════════════════════════════════════════════
# WO-29 — the typed answer binds by content
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture
def swapped():
    """A mock-parser TestClient over a world THIS test owns.

    `/command` reads the module-global `world`, `game_state["world"]` and the
    parser singleton — swap all three or the request silently runs against
    the developer's live world AND the real Anthropic API (measured: the
    first draft of this file spent two live API calls on "plunder it").
    """
    import backend.main as m
    from backend.commands.parser import CommandParser as _CP

    saved = (m.parser, m.world, m.game_state)
    m.parser = _CP(use_real_llm=False)
    m.world = WorldState(player_nation="France")
    m.game_state = {"world": m.world}
    try:
        yield TestClient(m.app), m
    finally:
        m.parser, m.world, m.game_state = saved


@pytest.fixture
def endpoint(swapped):
    client, m = swapped
    world = m.world
    region = next(r for r in world.regions.values()
                  if r.controller == world.player_nation)
    other = next(r for r in world.regions.values()
                 if r.name != region.name)
    world.pending_capture_choice = build_capture_choice(
        world, region, "Ney", "Britain")
    return client, m, region, other


class TestWO29TheTypedAnswerNamesItsProvince:

    def test_naming_the_wrong_province_is_refused(self, endpoint):
        """Mutation: delete the `region is not None and str(region) != …`
        block from `handle_capture_choice`."""
        client, m, region, other = endpoint
        gold_before = m.world.nation_gold.get(m.world.player_nation, 0)
        data = client.post(
            "/command", json={"command": f"plunder {other.name}"}).json()
        assert data["success"] is False
        assert data.get("stale_dialogue") is True
        assert m.world.pending_capture_choice["region"] == region.name
        assert m.world.nation_gold.get(m.world.player_nation, 0) == gold_before
        assert region.name in data["message"]

    def test_naming_the_right_province_applies(self, endpoint):
        """Mutation: make `_typed_capture_answer` require a bare token."""
        client, m, region, _other = endpoint
        data = client.post(
            "/command", json={"command": f"secure {region.name}"}).json()
        assert data["success"] is True
        assert m.world.pending_capture_choice is None

    def test_the_filler_words_are_stripped(self, endpoint):
        """"secure the province X" is the same answer. Mutation: delete the
        filler-strip loop."""
        client, m, region, _other = endpoint
        data = client.post(
            "/command",
            json={"command": f"secure the province {region.name}"}).json()
        assert data["success"] is True
        assert m.world.pending_capture_choice is None

    def test_a_bare_answer_still_resolves(self, endpoint):
        """The pre-slice shape is untouched — no keyword ownership moves."""
        client, m, _region, _other = endpoint
        data = client.post("/command", json={"command": "secure"}).json()
        assert data["success"] is True
        assert m.world.pending_capture_choice is None

    def test_trailing_words_that_name_no_province_fall_through(
            self, endpoint):
        """"plunder it" carries no province, so it is NOT a capture answer:
        it goes to the ordinary pipeline byte-for-byte as before this slice
        (HEAD's gate was an exact-token membership test, which "plunder it"
        also failed). The question stands, nothing is paid.

        Recorded honestly: what the ordinary pipeline then does is hand it to
        the parser, which does not understand it and answers with Berthier's
        confusion rather than restating the question the game just asked.
        That is a pre-existing wart of the typed route, not something this
        slice introduces or fixes — it belongs to slice 11's typed-route
        residue.

        Mutation: make `_typed_capture_answer` return `(token, None)` on
        unmatched trailing words — that would silently apply "plunder it" as
        a bare answer AND swallow sentences the parser owns.
        """
        client, m, region, _other = endpoint
        gold_before = m.world.nation_gold.get(m.world.player_nation, 0)
        data = client.post("/command", json={"command": "plunder it"}).json()
        assert data["success"] is False
        assert data.get("capture_choice") is None
        assert m.world.pending_capture_choice is not None
        assert m.world.pending_capture_choice["region"] == region.name
        assert m.world.nation_gold.get(m.world.player_nation, 0) == gold_before

    def test_the_resolver_is_inert_with_nothing_pending(self, endpoint):
        """FALSIFIABLE NEGATIVE — with no question standing the sentence
        belongs to the parser, as it always did."""
        client, m, _region, other = endpoint
        m.world.pending_capture_choice = None
        assert m._typed_capture_answer(m.world, "plunder") is None
        assert m._typed_capture_answer(
            m.world, f"plunder {other.name}") is None


# ═══════════════════════════════════════════════════════════════════
# WO-30 — a loaded save raises the question it restored
# ═══════════════════════════════════════════════════════════════════


class TestWO30TheLoadedSaveRaisesIt:

    @pytest.fixture
    def saved(self, swapped, tmp_path, monkeypatch):
        from backend import save_manager

        client, m = swapped
        monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path)
        world = m.world
        region = next(r for r in world.regions.values()
                      if r.controller == world.player_nation)
        world.pending_capture_choice = build_capture_choice(
            world, region, "Ney", "Britain")
        save_manager.save_game(world, save_name="wo30",
                               filepath=tmp_path / "wo30.json")
        return client, m, region

    def test_load_response_carries_both_capture_keys(self, saved):
        """Mutation: delete the three-line passthrough at the tail of
        `/load`."""
        client, m, region = saved
        m.world.pending_capture_choice = None
        data = client.post("/load", json={"filename": "wo30.json"}).json()
        assert data["success"] is True
        assert data.get("pending_capture_choice") is True
        assert data.get("capture_data", {}).get("region") == region.name
        assert "plunder_gold" in data.get("capture_data", {})

    def test_load_still_leaves_a_queued_popup_alone(self, saved):
        """The IGR-X7 / PC15-10 B0 non-draining contract survives the new
        keys.

        The popup must be queued in the world that gets SAVED — `/load`
        replaces the module-global world wholesale, so a popup set on the
        pre-load world is simply gone and the assertion proves nothing
        (measured INERT in this slice's first sweep).

        Mutation: swap the fill for `_include_popup_passthroughs`.
        """
        from backend import save_manager

        client, m, _region = saved
        m.world.coalition_popup = {"nations": ["Austria"]}
        save_manager.save_game(
            m.world, save_name="wo30",
            filepath=save_manager.SAVE_DIR / "wo30.json")
        data = client.post("/load", json={"filename": "wo30.json"}).json()
        assert m.world.coalition_popup is not None, (
            "the queued popup did not survive the save/load round trip — "
            "this test cannot say anything about draining")
        assert data.get("coalition_popup") is None
        assert data.get("pending_capture_choice") is True

    def test_the_world_swap_handler_raises_it_client_side(self):
        """The backend passthrough is invisible without this: the /load
        client handler consults no route table. Bounded to the FUNCTION
        BODY — the NA-6 dead-name pin failed in July 2026 by scraping a
        fixed char count and overshooting into the next function, where
        somebody else's call satisfied it.

        Mutation: remove the raise from `_apply_world_swap_response`.
        """
        src = MAIN_GD.read_text(encoding="utf-8")
        start = src.index("func _apply_world_swap_response(")
        rest = src[start:]
        nxt = re.search(r"\nfunc ", rest[1:])
        body = rest[:nxt.start() + 1] if nxt else rest
        assert 200 < len(body) < 4000, (
            f"the function-body extraction returned {len(body)} chars — it "
            f"has drifted off the function it claims to bound")
        assert "_response_has_capture_choice_route" in body
        assert "_route_capture_choice_response" in body

    def test_the_client_route_pair_still_exists(self):
        """The pin above is only meaningful while the predicate/route pair
        it names are the real ones. Mutation: rename either."""
        src = MAIN_GD.read_text(encoding="utf-8")
        assert "func _response_has_capture_choice_route(" in src
        assert "func _route_capture_choice_response(" in src

    def test_blocking_state_surface_census(self):
        """CENSUS — "the next new slot cannot silently drop".

        Keyed on the CLIENT's own modal route table, not on an attribute
        prefix: the route table is what decides whether a player ever sees a
        piece of blocking state, and it is the thing a future slice edits.
        Every response key any modal route reads must be classified — queue
        delivered, explicitly re-attached at /load, transient by design, or
        a known gap with a filed row. An unclassified key reds this test.

        Mutation: add a route to `_configure_response_routes` reading a new
        key, or delete `pending_capture_choice` from LOAD_REATTACHED.
        """
        from backend.models.cooldown_manager import PopupQueue

        QUEUE_DELIVERED = set(PopupQueue.RESPONSE_KEYS.values())
        LOAD_REATTACHED = {
            # WO-30: `/load` sets these two explicitly (they are a plain
            # world attribute, not a queue member) and the world-swap
            # handler raises the modal from them.
            "pending_capture_choice", "capture_data",
        }
        TRANSIENT_BY_DESIGN = {
            # per-command results; nothing survives a save to re-raise
            "state": "clarification / objection response state",
            "pending_glorious_charge": "a marshal's in-request charge offer",
            "diplomatic_dialogue": "re-derived from the dialogue manager",
            # read as NEGATIVE conditions ("not while an enemy phase is on
            # screen"), never as the payload a modal renders
            "strategic_reports": "an end-turn tail, not blocking state",
            "enemy_phase": "an end-turn tail, not blocking state",
        }
        KNOWN_SILENT_AT_LOAD = {
            # Found by slice 15's census; strictly worse than WO-30 was and
            # deliberately NOT folded into it. Filed as WO-35 / WO-36.
            "pending_objection": "WO-35 — survives the save, but its route "
                                 "requires success==true and the block "
                                 "returns success False",
            "pending_interrupt": "WO-35 — marshal-level, restored but never "
                                 "re-attached at /load",
            "redemption_event": "WO-36 — world.pending_redemption survives "
                                "the save and no /load path re-attaches it",
        }
        src = MAIN_GD.read_text(encoding="utf-8")
        table = re.search(
            r"func _configure_response_routes\(\):(.*?)\nfunc ",
            src, re.S)
        assert table, "the route table could not be located"
        matchers = re.findall(r'"matches":\s*"([A-Za-z0-9_]+)"',
                              table.group(1))
        assert len(matchers) >= 12, (
            f"only {len(matchers)} routes parsed — the table shape moved "
            f"and this census is no longer reading it")
        unclassified = []
        for fn in matchers:
            marker = f"func {fn}("
            assert marker in src, f"{fn} is declared but not defined"
            start = src.index(marker)
            rest = src[start:]
            nxt = re.search(r"\nfunc ", rest[1:])
            body = rest[:nxt.start() + 1] if nxt else rest
            keys = set(re.findall(r'response\.has\("([a-z_]+)"\)', body))
            keys |= set(re.findall(r'response\.get\("([a-z_]+)"', body))
            assert keys, f"{fn} yielded no response keys — the parse broke"
            for key in keys:
                if key in ("success",):
                    continue
                if (key in QUEUE_DELIVERED or key in LOAD_REATTACHED
                        or key in TRANSIENT_BY_DESIGN
                        or key in KNOWN_SILENT_AT_LOAD):
                    continue
                unclassified.append(f"{fn} -> {key}")
        assert not unclassified, (
            "a modal route reads blocking state nobody has classified. Give "
            "it a /load path, or declare it transient/known-silent with a "
            "filed row:\n" + "\n".join(sorted(unclassified)))


# ═══════════════════════════════════════════════════════════════════
# WO-34 — the naval landing asks the question it mounted
# ═══════════════════════════════════════════════════════════════════


class TestWO34TheLandingAsksItsQuestion:

    def test_the_landing_result_carries_the_question(self):
        """Found while building slice 15: the expedition mounted the
        question through the shared pipeline and shipped a response the
        client cannot render it from — `main.gd` gates the modal on
        `pending_capture_choice`, which was never set.

        Mutation: delete the two-key stamp at the tail of the landing arm in
        `naval_executor.py`.
        """
        src = (REPO / "backend" / "commands"
               / "naval_executor.py").read_text(encoding="utf-8")
        assert 'result["pending_capture_choice"] = True' in src
        assert 'result["capture_data"] = world.pending_capture_choice' in src
        # …and it is inside the LANDING arm, not bolted on at the end.
        landed = src.index('"landed": True')
        stamp = src.index('result["pending_capture_choice"] = True')
        assert 0 < stamp - landed < 2500, (
            "the capture stamp drifted out of the landing arm")

    def test_the_landing_arm_reaches_the_shared_producer(self):
        """The stamp is only meaningful while the landing still captures
        through `_attempt_region_capture` — the seam that mounts the
        question. Mutation: inline a bare capture in the landing arm."""
        src = (REPO / "backend" / "commands"
               / "naval_executor.py").read_text(encoding="utf-8")
        assert "_attempt_region_capture(" in src
        assert "pending_capture_choice =" not in src, (
            "the naval executor must never write the slot itself")


# ═══════════════════════════════════════════════════════════════════
# The shared producer, directly
# ═══════════════════════════════════════════════════════════════════


class TestTheSharedProducer:

    def test_auto_secure_flag_decides_even_on_an_empty_slot(self):
        """The march policy (IGR-X5) is a caller-passed flag, distinct from
        the universal collision rule. Mutation: make `auto_secure` a no-op
        — the PF-3 pin reds with it."""
        world, _gs = _world()
        region = world.regions["Lyon"]
        assert world.pending_capture_choice is None
        out = mount_or_auto_secure_capture(
            world, region, "Ney", "Britain", "France", auto_secure=True)
        assert out == "secure"
        assert world.pending_capture_choice is None
        assert region.stability == 25

    def test_the_collision_rule_needs_no_strategic_flag(self):
        """An occupied slot cannot be asked again — that rule is universal,
        which is why the occupation producer (which has no concept of
        `_strategic_execution`) is covered too."""
        world, _gs = _world()
        earlier = {"region": "Elsewhere", "capturer": "Augereau"}
        world.pending_capture_choice = earlier
        out = mount_or_auto_secure_capture(
            world, world.regions["Lyon"], "Ney", "Britain", "France")
        assert out == "secure"
        assert world.pending_capture_choice is earlier
