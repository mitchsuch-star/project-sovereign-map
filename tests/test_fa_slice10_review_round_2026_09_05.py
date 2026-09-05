"""FA slice 10 — the three-lens review round (September 5, 2026).

Three lenses at `f1fe18ab`, each finding put to two independent refuters. Nine
survived; this file pins the five that changed code or were unpinned.

The round found no P1 inside the fix — the first of six that has not — but it
found three things the slice itself shipped:

* **The arrival register was chosen from GOLD ALONE.** FA-N16 split `amount`
  from `amount_offered` and added a no-gold register that says "nothing changes
  hands but the quiet". `ai_diplomacy._settlement_offer_build_terms` drops the
  indemnity when the payer's chest is empty and falls through to the CARVE gate
  by design — so the settlement the producer builds for a beaten, bankrupt
  France (a white peace plus a `create_client` erecting the Duchy of Normandy
  out of French soil) got a voice line stating the opposite of its own second
  clause. A register may never assert what the package does not do.

* **FA-3's departed-court drop narrowed the COVERAGE and not the TERMS.** An
  offer whose indemnity or carve names the offering leader — which the
  producer's decisive-band arm always does — staged a review that consent made
  ratifiable and that the ratification then rejected with
  `clause_target_uncovered`, after the letter had been consumed, on an
  `ai_system` review advertising no editor. That is the exact "true when drawn,
  false when pressed" class the slice exists to close.

* **`departed_courts_note` was produced and delivered nowhere** (GR9), and its
  one sentence said "has already made her own peace" of a court France had
  destroyed — the elimination path this same slice made ordinary.

And two things about the pins rather than the code, which are findings in this
project's terms: three of the forty-one swept mutations were killed only by a
source-text census of the line they mutate, and one test that named itself the
FA-17 behaviour pin executed no production line at all. Those are repaired in
the slice's own file; the two unpinned `settlement_actions.py` seams and one of
`_mounted_settlement_dialogue`'s undocumented gates are pinned here.
"""

import contextlib
import io
import json
from pathlib import Path

import pytest

import backend.game_logic.settlement_offers as SO
from backend.game_logic.settlement_offers import (
    build_incoming_settlement_offer_popup,
    handle_incoming_settlement_offer_action,
)
from backend.game_logic.settlement_routes import _mounted_settlement_dialogue
from backend.game_logic.settlement_staging import stage_settlement_confirm
from backend.game_logic.settlement_routes import (
    evaluate_war_detail_actionability,
)
from backend.models.world_state import WorldState

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "playtest_saves" / "fixture_t20_ambient.json"

LEVERS = [
    (SO, "REGISTER_READS_THE_PACKAGE"),
    (SO, "DEPARTED_COURT_TAKES_ITS_CLAUSES"),
    (SO, "DEPARTED_COURT_NOTE_IS_DELIVERED"),
]


@pytest.fixture(autouse=True)
def _levers_at_default():
    saved = [(mod, name, getattr(mod, name)) for mod, name in LEVERS]
    yield
    for mod, name, value in saved:
        setattr(mod, name, value)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _fixture_world():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    with _quiet():
        return WorldState.from_dict(data["world_state"])


@pytest.fixture
def world():
    return _fixture_world()


def _current_offer(w):
    dm = w.dialogue_manager
    for d in ([dm.peek()] if dm.peek() else []) + dm.iter_queue():
        if d.get("type") == "incoming_settlement_offer":
            return d
    return None


def _offer_ids(w):
    dm = w.dialogue_manager
    return [d.get("offer_id") for d
            in ([dm.peek()] if dm.peek() else []) + dm.iter_queue()
            if d.get("type") == "incoming_settlement_offer"]


def _popup(w, terms):
    offer = dict(_current_offer(w) or {})
    offer["settlement_terms"] = terms
    with _quiet():
        return build_incoming_settlement_offer_popup(w, offer)


CARVE = {"type": "create_client", "from": "France", "to": "Britain",
         "tag": "Normandy", "provinces": ["Normandy"],
         "client_display_name": "Duchy of Normandy"}


# ═══════════════════════════════════════════════════════════════════════
# The register reads the package
# ═══════════════════════════════════════════════════════════════════════


class TestTheRegisterReadsThePackage:

    def test_a_carve_is_not_announced_as_nothing_changing_hands(self, world):
        """The measured case: the producer's own output for a beaten, broke
        France read "No indemnity either way — the war simply stops, and
        nothing changes hands but the quiet" over a clause erecting an enemy
        client on French soil."""
        payload = _popup(world, [{"type": "peace"}, dict(CARVE)])
        assert payload["amount"] == 0 and payload["amount_offered"] == 0
        for line in (payload["talleyrand_text"], payload["proposer_voice"]):
            assert line
            assert "nothing changes hands" not in line
            assert "simply stops" not in line
            assert "none is offered" not in line

    def test_it_sends_the_reader_to_the_terms(self, world):
        payload = _popup(world, [{"type": "peace"}, dict(CARVE)])
        spoken = payload["talleyrand_text"] + " " + payload["proposer_voice"]
        assert "articles" in spoken or "read what they ask" in spoken
        # And the clause itself is still listed, unchanged.
        assert any("Duchy of Normandy" in row
                   for row in payload["terms_summary"])

    def test_a_true_white_peace_still_says_nothing_changes_hands(self, world):
        """The `_none` register is not deleted — it is narrowed to the case it
        was written for."""
        payload = _popup(world, [{"type": "peace"}])
        assert "nothing changes hands" in payload["talleyrand_text"]

    @pytest.mark.parametrize("clause", [
        {"type": "territory_cede", "from": "France", "to": "Britain",
         "region": "Normandy"},
        {"type": "vassalage", "from": "France", "to": "Britain"},
        {"type": "forced_alliance", "from": "France", "to": "Britain"},
        {"type": "gold_per_turn", "from": "France", "to": "Britain",
         "amount": 99, "turns": 5},
    ])
    def test_every_substantive_family_takes_the_terms_register(
            self, world, clause):
        """The gold split does not see a recurring stream either, which is why
        `gold_per_turn` is in the set."""
        payload = _popup(world, [{"type": "peace"}, dict(clause)])
        assert "nothing changes hands" not in payload["talleyrand_text"]

    def test_the_lever_down_restores_the_gold_only_reading(self, world):
        SO.REGISTER_READS_THE_PACKAGE = False
        payload = _popup(world, [{"type": "peace"}, dict(CARVE)])
        assert "nothing changes hands" in payload["talleyrand_text"]

    def test_the_gold_registers_are_untouched(self, world):
        asked = _popup(world, [
            {"type": "peace"},
            {"type": "gold_indemnity", "from": "France", "to": "Britain",
             "amount": 400}])
        assert asked["amount"] == 400 and "asks 400" in asked["proposer_voice"]
        paid = _popup(world, [
            {"type": "peace"},
            {"type": "gold_indemnity", "from": "Britain", "to": "France",
             "amount": 400}])
        assert paid["amount_offered"] == 400
        assert "ask" not in paid["proposer_voice"].lower()

    def test_a_carve_that_also_carries_gold_keeps_the_gold_register(
            self, world):
        """Gold is the louder fact when it is present; the terms list carries
        the carve, as it did before."""
        payload = _popup(world, [
            {"type": "peace"}, dict(CARVE),
            {"type": "gold_indemnity", "from": "France", "to": "Britain",
             "amount": 400}])
        assert payload["amount"] == 400
        assert "asks 400" in payload["proposer_voice"]


# ═══════════════════════════════════════════════════════════════════════
# A departed court takes its clauses with it
# ═══════════════════════════════════════════════════════════════════════


def _clause_offer(w, amount=3770):
    offer = _current_offer(w)
    offer["settlement_terms"] = [
        {"type": "peace"},
        {"type": "gold_indemnity", "from": "Britain", "to": "France",
         "amount": amount}]
    return offer


class TestADepartedCourtTakesItsClauses:

    def test_the_accept_refuses_a_package_naming_a_dead_court(self, world):
        """Measured before the fix: `can_ratify: True`, "Ratify Settlement"
        enabled, and pressing it answered "The submitted terms failed
        validation; review and correct them.\""""
        offer = _clause_offer(world)
        offer_id = offer.get("offer_id")
        with _quiet():
            world._eliminate_nation("Britain")
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        assert result.get("success") is False
        assert result.get("error") == "offer_terms_name_a_departed_court"
        assert "Revise Terms" in str(result.get("error_display") or "")
        assert result.get("must_reopen") is False
        assert offer_id in _offer_ids(world), "the letter must stand"

    def test_the_refusal_names_the_court_and_why_it_left(self, world):
        offer = _clause_offer(world)
        with _quiet():
            world._eliminate_nation("Britain")
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        message = str(result.get("message") or "")
        assert "Britain" in message
        assert "no longer exists" in message

    def test_without_the_rule_the_button_lies(self, world):
        """The lever-off arm reproduces the defect exactly: the review stages,
        consent makes it ratifiable, and the ratification refuses."""
        SO.DEPARTED_COURT_TAKES_ITS_CLAUSES = False
        from backend.game_logic.settlement_ratify import (
            ratify_settlement_confirm,
        )
        offer = _clause_offer(world)
        with _quiet():
            world._eliminate_nation("Britain")
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        assert result.get("success") is True
        staged = world.dialogue_manager.peek()
        assert staged.get("can_ratify") is True
        with _quiet():
            ratified = ratify_settlement_confirm(world, staged)
        assert ratified.get("success") is False
        assert "revalidation" in str(ratified.get("error") or "")

    def test_revise_terms_drops_the_dead_clause_instead(self, world):
        """The recovery route the refusal names. This arm opens an EDITABLE
        draft, so the package is rewritten rather than refused."""
        offer = _clause_offer(world)
        with _quiet():
            world._eliminate_nation("Britain")
        result = handle_incoming_settlement_offer_action(
            world, action="request_settlement_revision", dialogue=offer)
        assert result.get("success") is True
        staged = world.dialogue_manager.peek()
        assert staged.get("dialogue_mode") == "PROPOSE"
        assert staged.get("settlement_terms") == [{"type": "peace"}]
        assert "Britain" not in (staged.get("covered_enemy_participants") or [])

    def test_a_package_naming_only_live_courts_is_untouched(self, world):
        """The narrowness: a departed court that no clause names — FA-3's own
        motivating Russia case — still accepts and ratifies."""
        offer = _current_offer(world)
        covered = list(offer.get("covered_enemy_participants") or [])
        from backend.game_logic.settlement_helpers import resolve_pair_to_resolved
        war = world.war_instances[offer["war_id"]]
        with _quiet():
            for key in [k for k in list(war.get("active_diplo_keys") or [])
                        if covered[-1] in k.split("|")]:
                resolve_pair_to_resolved(world, key)
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        assert result.get("success") is True
        assert world.dialogue_manager.peek().get("can_ratify") is True

    def test_the_predicate_reads_the_validator_own_rule(self, world):
        """Drift pin: the accept's predicate and the V2 coverage check must
        name the same courts, or one of them will let a package through that
        the other rejects."""
        from backend.game_logic.settlement_validation import _clause_role_nations
        clause = dict(CARVE)
        assert set(_clause_role_nations(clause)) & {"France", "Britain"}
        assert SO._terms_naming_departed_courts(
            [clause], ["Britain"]) == ["Britain"]
        assert SO._terms_naming_departed_courts([clause], ["Russia"]) == []


# ═══════════════════════════════════════════════════════════════════════
# The note is delivered, and it names the exit
# ═══════════════════════════════════════════════════════════════════════


def _depart(world, nation, *, kill):
    offer = _current_offer(world)
    war = world.war_instances[offer["war_id"]]
    if kill:
        with _quiet():
            world._eliminate_nation(nation)
        return
    from backend.game_logic.settlement_helpers import resolve_pair_to_resolved
    with _quiet():
        for key in [k for k in list(war.get("active_diplo_keys") or [])
                    if nation in k.split("|")]:
            resolve_pair_to_resolved(world, key)


class TestTheNoteIsDeliveredAndNamesTheExit:

    def test_an_annihilated_court_is_not_said_to_have_made_peace(self, world):
        """The sentence was unconditional. `_live_covered_for_offer` derives
        departure from the war's side lists, and the commonest way a court
        leaves them is CONQUEST — which this very slice made ordinary."""
        offer = _current_offer(world)
        departing = list(offer.get("covered_enemy_participants") or [])[-1]
        _depart(world, departing, kill=True)
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        note = str(result.get("departed_courts_note") or "")
        assert f"{departing} no longer exists" in note
        assert "made her own peace" not in note

    def test_a_court_that_really_settled_still_reads_that_way(self, world):
        offer = _current_offer(world)
        departing = list(offer.get("covered_enemy_participants") or [])[-1]
        _depart(world, departing, kill=False)
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        note = str(result.get("departed_courts_note") or "")
        assert "has already made her own peace" in note
        assert "no longer exists" not in note

    def test_the_note_reaches_a_surface_the_player_reads(self, world):
        """GR9. A whole-repo census found the key had no consumer at all —
        no backend arm folded it into `message`, and no `.gd` read it."""
        offer = _current_offer(world)
        departing = list(offer.get("covered_enemy_participants") or [])[-1]
        _depart(world, departing, kill=False)
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        note = str(result.get("departed_courts_note") or "")
        assert note
        assert note in str(result.get("message") or "")
        staged = result.get("diplomatic_dialogue") or {}
        assert note in str(staged.get("talleyrand_text") or "")

    def test_the_review_the_player_answers_carries_it_too(self, world):
        offer = _current_offer(world)
        departing = list(offer.get("covered_enemy_participants") or [])[-1]
        _depart(world, departing, kill=False)
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        note = str(result.get("departed_courts_note") or "")
        mounted = world.dialogue_manager.peek() or {}
        assert note in str(mounted.get("talleyrand_text") or "")

    def test_the_lever_down_restores_the_undelivered_note(self, world):
        SO.DEPARTED_COURT_NOTE_IS_DELIVERED = False
        offer = _current_offer(world)
        departing = list(offer.get("covered_enemy_participants") or [])[-1]
        _depart(world, departing, kill=False)
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        note = str(result.get("departed_courts_note") or "")
        assert note
        assert note not in str(result.get("message") or "")

    def test_the_review_arm_delivers_it_as_well(self, world):
        offer = _current_offer(world)
        departing = list(offer.get("covered_enemy_participants") or [])[-1]
        _depart(world, departing, kill=False)
        result = handle_incoming_settlement_offer_action(
            world, action="request_settlement_revision", dialogue=offer)
        note = str(result.get("departed_courts_note") or "")
        assert note and note in str(result.get("message") or "")


# ═══════════════════════════════════════════════════════════════════════
# The three seams the slice changed and did not pin
# ═══════════════════════════════════════════════════════════════════════


class TestTheSeamsTheSliceDidNotPin:

    def test_backing_out_of_a_review_does_not_promote_the_letter(self, world):
        """`settlement_actions._action_return_to_settlement_terms` lost its
        `dialogue_manager.pop()` in this slice — three production changes in
        that file carried no test and no mutation, and the FA-N4 cell called
        the route "pinned".

        MEASURED, four arms ({pop re-added, not} x {the rule on, off}): the
        deletion is INERT on this geometry. With the rule ON, popping first
        promotes the letter, the promotion is no longer read as a draft, and
        the staging tail preempts it back — byte-identical outcome. With the
        rule OFF the draft cannot be staged at all, so the arm is unreachable.
        The pop deletion is therefore defence in depth, not a behaviour
        change, and its two mutations were DELETED from the sweep rather than
        left reporting INERT. What this pin binds is the OUTCOME the route
        must have, which is what a future re-widening of the type set would
        break."""
        from backend.game_logic.settlement_actions import (
            handle_settlement_dialogue_action,
        )
        offer_id = _current_offer(world).get("offer_id")
        staged = stage_settlement_confirm(
            world, war_id="war_2", actor_nation=world.player_nation,
            caller_kind="player_editor", dialogue_mode="PROPOSE")
        assert staged.get("success") is True
        dialogue = world.dialogue_manager.peek()
        with _quiet():
            result = handle_settlement_dialogue_action(
                world, action="return_to_settlement_terms", dialogue=dialogue)
        head = world.dialogue_manager.peek() or {}
        assert head.get("type") == "settlement_confirm"
        assert head.get("war_id") == "war_2"
        assert result.get("error") != "cross_war_settlement_collision"
        assert offer_id in _offer_ids(world)

    def test_submitting_for_review_does_not_promote_the_letter_either(
            self, world):
        """The sibling deletion in `_action_submit_settlement_for_review`,
        measured inert on the same four arms. See the note above: the pin is
        on the outcome, not on the deleted statement."""
        from backend.game_logic.settlement_actions import (
            handle_settlement_dialogue_action,
        )
        offer_id = _current_offer(world).get("offer_id")
        stage_settlement_confirm(
            world, war_id="war_2", actor_nation=world.player_nation,
            caller_kind="player_editor", dialogue_mode="PROPOSE")
        dialogue = world.dialogue_manager.peek()
        if not (dialogue.get("settlement_terms") or []):
            pytest.skip("the generated baseline is empty on this board")
        with _quiet():
            result = handle_settlement_dialogue_action(
                world, action="submit_settlement_for_review",
                dialogue=dialogue)
        head = world.dialogue_manager.peek() or {}
        assert head.get("war_id") == "war_2"
        assert result.get("error") != "cross_war_settlement_collision"
        assert offer_id in _offer_ids(world)

    def test_a_standing_letter_no_longer_blocks_the_war_detail_route(
            self, world):
        """`_mounted_settlement_dialogue` has THREE callers, not the one the
        landing record glossed. This is the war-detail settlement recovery
        gate — narrowing the helper changed its verdict too, and nothing
        pinned it."""
        assert _mounted_settlement_dialogue(world) is None, (
            "the fixture's standing offer must not read as a mounted draft")
        verdict = evaluate_war_detail_actionability(
            world, war_id="war_2", selected_target_nation="Switzerland",
            actor_nation=world.player_nation)
        assert verdict.get("error") != "settlement_collision_active"
        assert verdict.get("actionable") is not False or verdict.get("error")

    def test_a_real_draft_still_blocks_that_route(self, world):
        """The other direction: the gate is intact for a genuine draft."""
        stage_settlement_confirm(
            world, war_id="war_1", actor_nation=world.player_nation,
            caller_kind="player_editor", dialogue_mode="PROPOSE")
        assert _mounted_settlement_dialogue(world) is not None
        verdict = evaluate_war_detail_actionability(
            world, war_id="war_2", selected_target_nation="Switzerland",
            actor_nation=world.player_nation)
        assert verdict.get("error") == "settlement_collision_active"
        assert verdict.get("actionable") is False

    def test_the_helper_has_exactly_three_callers(self):
        """A census, so the next reader of the record is not surprised the way
        this round was. If a fourth appears, the record must name it."""
        import ast
        callers = []
        for path in sorted((ROOT / "backend").rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id == "_mounted_settlement_dialogue"):
                    callers.append(path.name)
        assert sorted(callers) == [
            "settlement_routes.py",
            "settlement_staging.py",
            "settlement_validation.py",
        ], callers
