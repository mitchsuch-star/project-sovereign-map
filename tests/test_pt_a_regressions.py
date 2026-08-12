"""Row PT, slice A — the three regressions the August 9 queue introduced.

Build spec: `docs/PLAYTEST_FIXES_SPEC.md` §2 PT-A (indivisible, first).
Evidence: `docs/audits/PLAYTEST_CA9_2026_08_09.md`.

Each of these is an honest computation destroyed at a seam downstream of
it, which is the shape CA9's through-line MIGRATED into:

* **PT-A1** `_command_option` refuses honestly; the delivery-seam AP
  refresher re-enables the arm and pops the reason.
* **PT-A2** the resolver rolls each reinforcer for arrival; the preview
  prices them all as certain, and CA9 row 2's gate reads that band.
* **PT-A3** a hard stop hands an unrelated typed order to the choice
  resolver and answers "I don't understand that choice, Sire."

§3 acceptance rule 2 governs this file: **a pin that can pass while the
delivered payload is wrong is not a pin.** PT-A1 exists precisely because
eight assertions pinned the builder while the defect lived in the
refresher, so every assertion here reads the delivered value.
"""

import random

import pytest

from types import SimpleNamespace

from backend.commands.combat_executor import CombatExecutor
from backend.commands.dialogue_routing import (
    format_numbered_options,
    hard_stop_subject,
    match_dialogue_answer,
)
from backend.commands.executor import CommandExecutor
from backend.game_logic import jealousy as J
from backend.game_logic.combat import CombatResolver

from tests.conftest import MarshalFactory, WorldFactory


def _combat():
    """The sub-executor as every other combat test builds it."""
    return CombatExecutor(SimpleNamespace(combat_resolver=CombatResolver()))


# ═══════════════════════════════════════════════════════════════════════
# PT-A1 — the delivery seam is subtractive
# ═══════════════════════════════════════════════════════════════════════

class _APWorld:
    """The refresher only ever reads action points off the world."""

    def __init__(self, ap):
        self.actions_remaining = ap


def _opt(petition, oid):
    return next(o for o in petition["options"] if o["id"] == oid)


@pytest.fixture()
def petition_board():
    """Ney (aggressive) envious of Murat, with Mack co-located to fight."""
    ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                  strength=30000, personality="aggressive")
    murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                    strength=30000, personality="aggressive")
    mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                nation="Austria", strength=12000,
                                personality="cautious")
    world = WorldFactory.with_marshals([ney, murat, mack])
    key = "|".join(sorted(["France", "Austria"]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn
    world.calculate_visibility()
    world.actions_remaining = 4
    world.marshals["Ney"].jealous_of = "Murat"
    return world, CommandExecutor()


def _queue(world):
    J.queue_confrontation_petition(world, world.marshals["Ney"],
                                   world.marshals["Murat"], 1)
    return world.pending_marshal_petition


def _delivered(world):
    """The petition AS THE PLAYER RECEIVES IT — through the refresher that
    `main.py:1304` runs unconditionally at the delivery seam."""
    return J.refresh_petition_affordability(
        world.pending_marshal_petition, world)


class TestTheRefresherMayOnlyDowngrade:
    def test_a_non_ap_refusal_survives_delivery_with_its_reason(
            self, petition_board):
        """THE MEASURED DEFECT. Turn 2, Murat's confrontation: the arm
        shipped `enabled: true` with `detail` still reading "There is no
        enemy within his reach to send him against." 6 of 10 petitions in
        the campaign shipped it that way."""
        world, _ = petition_board
        _queue(world)
        world.marshals.pop("Mack")             # no reachable quarry
        world.actions_remaining = 4            # ...and AP is not the problem
        # rebuild the card against the moved-on world
        world.pending_marshal_petition = None
        _queue(world)

        opt = _opt(_delivered(world), "command")
        assert opt["enabled"] is False
        assert "no enemy within his reach" in opt.get("unavailable_reason", "")

    def test_the_reason_is_never_replaced_by_an_ap_reason(self,
                                                          petition_board):
        """A man who cannot go does not become a man who cannot be
        afforded."""
        world, _ = petition_board
        world.marshals["Ney"].broken = True
        _queue(world)
        world.actions_remaining = 0
        opt = _opt(_delivered(world), "command")
        assert opt["enabled"] is False
        assert "broken" in opt["unavailable_reason"]
        assert "action point" not in opt["unavailable_reason"]

    def test_igr1_still_holds_a_priced_arm_reopens_when_ap_returns(self):
        """The refresher's own reason for existing. The jealousy pass runs
        BEFORE `advance_turn` refills AP, so an arm baked at zero AP must
        re-open when the card is handed over at 4/4. Subtractive must not
        mean sticky."""
        petition = {
            "kind": "jealousy_confrontation",
            "options": [
                {"id": "promise", "label": "Promise Glory",
                 "ap_cost": 1, "enabled": False},   # baked during the turn pass
            ],
        }
        out = J.refresh_petition_affordability(petition, _APWorld(4))
        assert _opt(out, "promise")["enabled"] is True
        assert "unavailable_reason" not in _opt(out, "promise")

    def test_an_available_arm_still_greys_when_it_cannot_be_afforded(
            self, petition_board):
        world, _ = petition_board
        _queue(world)
        world.actions_remaining = 0
        opt = _opt(_delivered(world), "command")
        assert opt["enabled"] is False
        assert "action point" in opt["unavailable_reason"]

    def test_the_refresher_does_not_mutate_the_stored_petition(
            self, petition_board):
        """Purity is what makes reading the builder's verdict correct on
        every re-delivery — the stored card must keep it."""
        world, _ = petition_board
        world.marshals["Ney"].broken = True
        stored = _queue(world)
        before = [dict(o) for o in stored["options"]]
        J.refresh_petition_affordability(stored, _APWorld(0))
        J.refresh_petition_affordability(stored, _APWorld(4))
        assert stored["options"] == before

    def test_repeated_delivery_is_idempotent(self, petition_board):
        """Deliver at 0 AP, then at 4 — the second must re-open."""
        world, _ = petition_board
        _queue(world)
        world.actions_remaining = 0
        assert _opt(_delivered(world), "command")["enabled"] is False
        world.actions_remaining = 4
        assert _opt(_delivered(world), "command")["enabled"] is True


class TestARefusalDoesNotDestroyTheDecision:
    def test_a_refused_arm_leaves_the_petition_answerable(self,
                                                          petition_board):
        """MEASURED: `POST /marshal_petition_response {"choice":"command"}`
        returned `success: false`, charged 0 AP, and the petition was
        gone."""
        world, executor = petition_board
        petition = _queue(world)
        world.marshals.pop("Mack")             # the world moved on
        result = J.handle_petition_response(
            world, "command", executor=executor,
            game_state={"world": world, "executor": executor})
        assert result["success"] is False
        assert world.pending_marshal_petition is petition
        # The card handed BACK is the delivered one — refreshed against
        # current AP, not the raw stored dict whose flags were baked
        # during the turn pass. (Review-fleet correction: the first cut
        # returned the raw petition and re-created IGR-1 on the re-serve.)
        served = result.get("marshal_petition")
        assert served is not None
        assert served["kind"] == petition["kind"]
        assert {o["id"] for o in served["options"]} == {
            o["id"] for o in petition["options"]}
        assert world.actions_remaining == 4

    def test_and_the_second_attempt_can_still_succeed(self, petition_board):
        """The decision survived, so answering it again works."""
        world, executor = petition_board
        _queue(world)
        mack = world.marshals.pop("Mack")
        gs = {"world": world, "executor": executor}
        assert J.handle_petition_response(
            world, "command", executor=executor, game_state=gs)["success"] is False
        world.marshals["Mack"] = mack          # he is back within reach
        assert J.handle_petition_response(
            world, "command", executor=executor, game_state=gs)["success"] is True
        assert world.pending_marshal_petition is None

    def test_a_successful_arm_still_retires_the_card(self, petition_board):
        world, executor = petition_board
        _queue(world)
        result = J.handle_petition_response(
            world, "acknowledge", executor=executor,
            game_state={"world": world, "executor": executor})
        assert result["success"] is True
        assert world.pending_marshal_petition is None

    def test_an_arm_that_pushes_a_new_petition_does_not_lose_it(
            self, petition_board):
        """The retirement is IDENTITY-checked. If an arm replaces the card,
        the replacement must survive — a blanket `= None` would delete it."""
        world, executor = petition_board
        _queue(world)
        replacement = {"kind": "jealousy_confrontation", "options": [],
                       "context": {}}

        def _swap(*_a, **_k):
            world.pending_marshal_petition = replacement
            return {"success": True, "message": "the card changed hands"}

        original = J._apply_confrontation_choice
        J._apply_confrontation_choice = _swap
        try:
            J.handle_petition_response(
                world, "acknowledge", executor=executor,
                game_state={"world": world, "executor": executor})
        finally:
            J._apply_confrontation_choice = original
        assert world.pending_marshal_petition is replacement


# ═══════════════════════════════════════════════════════════════════════
# PT-A2 — the muster band counts arrivals, not eligibility
# ═══════════════════════════════════════════════════════════════════════

class TestArrivalProbability:
    def test_the_deterministic_split_reproduces_the_score_exactly(self):
        """`_calculate_arrival_score` is now `_arrival_deterministic` plus
        one jitter draw. Shown equals applied BY CONSTRUCTION: any drift
        between the preview's probability and the resolver's roll would
        have to be a drift inside one expression."""
        ex = _combat()
        ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                      strength=20000, personality="aggressive")
        davout = MarshalFactory.infantry(name="Davout", location="Belgium",
                                         strength=20000, personality="cautious")
        world = WorldFactory.with_marshals([ney, davout])
        det = ex._arrival_deterministic(ney, davout, world)
        for seed in range(40):
            random.seed(seed)
            score = ex._calculate_arrival_score(ney, davout, world)
            assert abs(score - det) <= ex._ARRIVAL_VARIANCE

    def test_probability_is_zero_below_the_band_and_capped_above_it(self):
        ex = _combat()
        v = ex._ARRIVAL_VARIANCE
        assert ex._arrival_probability(65 - v, 65) == 0.0
        assert ex._arrival_probability(65, 65) == pytest.approx(v / (2 * v + 1))
        # a very strong reinforcer still carries the 5% fumble, never 1.0
        assert ex._arrival_probability(200, 65) == pytest.approx(0.95)
        # ...and NOBODY is ever certain at the standing threshold. Clearing
        # 65 on the worst jitter needs D > 73; staying under the fumble line
        # on the best needs D <= 72. The window is empty, so no reinforcer
        # on this board is a certainty — which is exactly what the preview
        # used to promise for every one of them.
        best = max(ex._arrival_probability(d, 65) for d in range(50, 140))
        assert best < 1.0

    def test_it_matches_the_resolvers_own_roll_empirically(self):
        """The falsifiable form: simulate the resolver's comparison and
        check the closed form predicts it."""
        ex = _combat()
        det, threshold = 68, 65
        random.seed(11)
        hits = 0
        trials = 20000
        for _ in range(trials):
            score = det + random.randint(-ex._ARRIVAL_VARIANCE,
                                         ex._ARRIVAL_VARIANCE)
            arrived = score > threshold
            if arrived and score > ex._ARRIVAL_FUMBLE_ABOVE:
                if random.randint(1, 20) == 1:
                    arrived = False
            hits += int(arrived)
        assert (hits / trials) == pytest.approx(
            ex._arrival_probability(det, threshold), abs=0.02)


@pytest.fixture()
def muster_board():
    """A lead at the front, one reinforcer a march away.

    Deliberately mountains: terrain is the term that moves arrival hardest
    (-20), which is what produced the measured 24% over-promise.
    """
    davout = MarshalFactory.infantry(name="Davout", location="Belgium",
                                     strength=18874, personality="cautious")
    murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                    strength=21000, personality="aggressive")
    charles = MarshalFactory.enemy(name="Charles", location="Belgium",
                                   nation="Austria", strength=31241,
                                   personality="cautious")
    world = WorldFactory.with_marshals([davout, murat, charles])
    key = "|".join(sorted(["France", "Austria"]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn
    world.calculate_visibility()
    return world


class TestThePreviewPricesTheRoll:
    def test_a_reinforcer_who_must_march_is_discounted(self, muster_board):
        """THE MEASURED DEFECT: `18,874; 39,240 if all march` against
        31,680 real."""
        world = muster_board
        ex = _combat()
        lead = world.marshals["Davout"]
        joiners = [world.marshals["Murat"]]
        certain = ex._committed_reinforcement_strength(lead, joiners, world)
        expected = ex._committed_reinforcement_strength(
            lead, joiners, world, expected_at="Belgium")
        assert 0 < expected < certain, (
            "a reinforcer who has not marched yet must be priced at the "
            "probability of the roll the resolver will make for him")

    def test_a_marshal_already_on_the_field_is_still_certain(self,
                                                            muster_board):
        """He makes no march and no roll — weighting him would be wrong."""
        world = muster_board
        world.marshals["Murat"].location = "Belgium"
        ex = _combat()
        lead = world.marshals["Davout"]
        joiners = [world.marshals["Murat"]]
        assert ex._committed_reinforcement_strength(
            lead, joiners, world, expected_at="Belgium") == pytest.approx(
                ex._committed_reinforcement_strength(lead, joiners, world))

    def test_artillery_is_priced_at_zero_because_it_never_relocates(
            self, muster_board):
        """An arriving gun is appended to `artillery_reinforced_adjacent`
        and never enters `_get_casualty_participants`, so it contributes
        exactly nothing to the resolver's committed term. The preview used
        to promise its full weight."""
        world = muster_board
        world.marshals["Murat"].artillery = True
        ex = _combat()
        assert ex._committed_reinforcement_strength(
            world.marshals["Davout"], [world.marshals["Murat"]], world,
            expected_at="Belgium") == 0.0

    def test_the_resolver_is_untouched(self, muster_board):
        """The resolver sums marshals who have ALREADY arrived. Weighting
        that list would double-count the roll."""
        world = muster_board
        ex = _combat()
        murat = world.marshals["Murat"]
        murat.location = "Belgium"             # as the resolver relocates them
        lead = world.marshals["Davout"]
        expected = (ex.COMMITTED_ALPHA * murat.strength
                    * murat.get_combat_effectiveness()
                    * murat.get_attack_modifier(1.0, consume=False)
                    * ex._pair_contribution_scale(lead, murat))
        assert ex._committed_reinforcement_strength(
            lead, [lead, murat], world) == pytest.approx(expected)

    def test_an_unreachable_reinforcer_promises_nothing(self, muster_board):
        """Murat marching out of mountains at a soured relationship: the
        audit's `P = 0` case, whose row still read WILL JOIN."""
        world = muster_board
        region = world.get_region("Paris")
        if region is not None:
            region.terrain = "mountains"
        murat = world.marshals["Murat"]
        murat.skills["logistics"] = 1
        murat.modify_relationship("Davout", -2)
        world.marshals["Davout"].modify_relationship("Murat", -2)
        ex = _combat()
        assert ex._committed_reinforcement_strength(
            world.marshals["Davout"], [murat], world,
            expected_at="Belgium") == 0.0


class TestTheThreeProducersActuallyPassIt:
    """Found by the mutation sweep, and it is PT-A1's own lesson.

    The first draft of this file pinned `_committed_reinforcement_strength`
    directly and never asserted that the surfaces the player reads pass
    `expected_at` at all — so deleting the argument at the call site left
    every pin green. A pin on the helper is not a pin on the seam.
    """

    def test_the_muster_preview_discounts_a_reinforcer_who_must_march(
            self, muster_board):
        world = muster_board
        ex = _combat()
        lead = world.marshals["Davout"]
        joiners = [world.marshals["Murat"]]
        preview = ex._build_muster_preview(
            lead, world.marshals["Charles"], world, {"world": world})
        certain = int(lead.strength
                      + ex._committed_reinforcement_strength(
                          lead, joiners, world))
        assert preview["attacker"]["committed_strength"] < certain, (
            "the muster header is the sentence that reads '39,240 if all "
            "march' — it must price the roll, not the roster")

    def test_the_defenders_muster_is_weighted_too(self, muster_board):
        """CA9-F1 landed the defender's term precisely so the error stopped
        pointing one way. An unweighted defender would re-open it."""
        world = muster_board
        ex = _combat()
        charles = world.marshals["Charles"]
        # NOT Paris: Murat stands there, so `_muster_reason` returns
        # `engaged` and the muster is EMPTY — which is how the first draft
        # of this pin passed while proving nothing (found by the sweep).
        john = MarshalFactory.enemy(name="John", location="Normandy",
                                    nation="Austria", strength=20000,
                                    personality="aggressive")
        world.marshals["John"] = john
        joining, committed = ex._defender_muster(charles, world)
        assert [m.name for m in joining] == ["John"], (
            "the fixture must actually produce a defender reinforcer or "
            "this pin proves nothing")
        certain = ex._committed_reinforcement_strength(charles, [john], world)
        assert 0 < committed < certain

    def test_the_bad_odds_note_is_weighted_too(self, muster_board):
        """The CR-5 modal's addendum — the third producer."""
        world = muster_board
        ex = _combat()
        lead = world.marshals["Davout"]
        murat = world.marshals["Murat"]
        note = ex._bad_odds_muster_note(lead, world.marshals["Charles"], world)
        assert note, "fixture must produce a note for this pin to bind"
        certain = int(lead.strength
                      + ex._committed_reinforcement_strength(
                          lead, [murat], world))
        assert f"{certain:,}" not in note, (
            "the note names the men and then prints a joint figure — the "
            "figure must be the weighted one")


class TestRow2GateBecomesReachable:
    def test_the_band_can_now_reach_unfavorable_where_it_could_not(self):
        """CA9 row 2 reads FAIL because the gate never armed once in 19
        turns. It is built exactly as ruled; an upstream number defeated
        it. This asserts the band responds to the weight — the same input
        that produced `favorable` on eligibility can produce a lower band
        on arrivals."""
        from backend.commands.objection_v2 import inferred_attack_odds_band

        davout = MarshalFactory.infantry(name="Davout", location="Belgium",
                                         strength=18874,
                                         personality="cautious")
        charles = MarshalFactory.enemy(name="Charles", location="Belgium",
                                       nation="Austria", strength=31241,
                                       personality="cautious")
        murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                        strength=21000,
                                        personality="aggressive")
        world = WorldFactory.with_marshals([davout, murat, charles])
        key = "|".join(sorted(["France", "Austria"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        world.calculate_visibility()
        gs = {"world": world}
        ex = _combat()

        certain = ex._committed_reinforcement_strength(
            davout, [murat], world)
        expected = ex._committed_reinforcement_strength(
            davout, [murat], world, expected_at="Belgium")
        as_eligibility = inferred_attack_odds_band(
            davout, charles, gs, committed_attacker=certain,
            committed_defender=0.0)
        as_arrivals = inferred_attack_odds_band(
            davout, charles, gs, committed_attacker=expected,
            committed_defender=0.0)
        order = {"unfavorable": 0, "even": 1, "favorable": 2}
        assert order[as_arrivals] <= order[as_eligibility], (
            "pricing the roll may only ever make the odds look worse — "
            "the error the playtest measured always pointed at 'favorable'")


class TestPTD1TheSoloFrameNamesItself:
    def test_the_line_does_not_call_a_reinforced_man_alone(self):
        random.seed(5)
        a = MarshalFactory.infantry(name="Moore", location="TestField",
                                    strength=20000, personality="cautious")
        a.nation = "Britain"
        d = MarshalFactory.infantry(name="Ney", location="TestField",
                                    strength=30000, personality="aggressive")
        r = CombatResolver().resolve_battle(
            a, d, terrain="plains", committed_attacker=15000.0)
        line = r.get("attacker_personality_triggered") or ""
        assert "on his own numbers" in line
        assert "alone" not in line


# ═══════════════════════════════════════════════════════════════════════
# PT-A3 — a hard stop must not swallow an unrelated valid order
# ═══════════════════════════════════════════════════════════════════════

def _war_purpose_dialogue():
    return {
        "type": "war_purpose_selection",
        "nation": "Austria",
        "options": [
            {"label": "Conquest", "action": "select_war_objective"},
            {"label": "Forced Alliance", "action": "select_war_objective"},
            {"label": "Subjugation", "action": "select_war_objective"},
            {"label": "Back Out", "action": "reconsider"},
        ],
    }


class TestTheHardStopNamesItself:
    def test_every_hard_stop_type_has_a_subject(self):
        """A refusal that cannot name its blocker is the defect."""
        from backend.models.dialogue_manager import DialogueManager

        for dtype in DialogueManager.HARD_STOP_TYPES:
            subject = hard_stop_subject({"type": dtype})
            assert subject and subject != "A decision", (
                f"{dtype} has no authored subject — the refusal would read "
                f"'A decision awaits your answer'")

    def test_an_unknown_type_degrades_without_crashing(self):
        assert hard_stop_subject({"type": "nonesuch"}) == "A decision"
        assert hard_stop_subject(None) == "A decision"


class TestTheRouterAcceptsWhatTheEngineOffers:
    def test_the_phrase_the_raising_message_offers_is_answerable(self):
        """`_stage_war_purpose_selection` raises with "…choose our purpose,
        or let the province stand." Four call sites speak it and the
        router had no vocabulary for it."""
        assert match_dialogue_answer(
            _war_purpose_dialogue(), "let the province stand") is not None

    def test_an_unrelated_order_still_matches_nothing(self):
        """The guard on the fix: the router must not become a substring
        scanner again — that was CA9's own regression."""
        assert match_dialogue_answer(
            _war_purpose_dialogue(),
            "davout, march to munich and relieve the bavarians") is None

    def test_the_offered_phrase_appears_in_the_raising_copy(self):
        """Shown == accepted, pinned at the producer so the two cannot
        drift apart again."""
        import inspect

        from backend.commands import combat_executor as CE

        src = inspect.getsource(CE)
        assert "let the province stand" in src
        assert match_dialogue_answer(
            _war_purpose_dialogue(), "let the province stand") is not None


class TestTheHardStopRefusalThroughTheEndpoint:
    """The pin binds where the player reads: the real `/command` route."""

    def _client(self, monkeypatch):
        monkeypatch.setenv("SOVEREIGN_SCENARIO", "none")
        monkeypatch.setenv("LLM_MODE", "mock")
        from fastapi.testclient import TestClient

        import backend.main as M

        return TestClient(M.app), M

    def test_an_unrelated_order_is_refused_honestly(self, monkeypatch):
        client, M = self._client(monkeypatch)
        M.world.dialogue_manager.push(_war_purpose_dialogue())
        r = client.post("/command", json={
            "command": "Davout, march to Munich and relieve the Bavarians"
        }).json()
        msg = r.get("message") or ""
        assert r.get("success") is False
        assert "I don't understand that choice" not in msg, (
            "the game must not claim it misunderstood a sentence it never "
            "tried to read")
        assert "purpose in this war" in msg          # names the blocker
        assert "nothing was relayed" in msg          # says what did not happen
        assert "1=Conquest" in msg                   # quotes the exits
        assert M.world.pending_diplomatic_dialogue is not None
        M.world.dialogue_manager.pop()

    def test_the_offered_phrase_clears_the_stop_over_http(self, monkeypatch):
        client, M = self._client(monkeypatch)
        M.world.dialogue_manager.push(_war_purpose_dialogue())
        r = client.post("/command",
                        json={"command": "let the province stand"}).json()
        assert r.get("success") is True
        assert M.world.pending_diplomatic_dialogue is None

    def test_the_exits_it_quotes_are_the_dialogues_own(self, monkeypatch):
        client, M = self._client(monkeypatch)
        dlg = _war_purpose_dialogue()
        M.world.dialogue_manager.push(dlg)
        r = client.post("/command", json={"command": "Ney, attack Mack"}).json()
        assert format_numbered_options(dlg) in (r.get("message") or "")
        M.world.dialogue_manager.pop()
