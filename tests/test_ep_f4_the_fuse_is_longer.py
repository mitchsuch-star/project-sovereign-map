"""Row EP, slice F4 — "The fuse is longer" (`docs/ENDGAME_PLAN.md` §1 F4, D11).

The live review (`BUG_FIXES.md` LV-21, `DESIGN_REFINEMENT.md` LV-D1) measured
the reward curve as built: after Ulm (turn 1) four marshals expected 40–80g a
turn, the dispatch carried an UNMET MARSHALS block from turn 2, and on turn 7
of a WINNING campaign the Fontainebleau collective petition fired for 600g a
turn. Every mechanic worked; the fuse was too short.

The ruling reshapes the CURVE, not the numbers (`dotation.py` F4 block):

* an expectation rises only on a DEED — a decisive victory with the marshal
  as LEAD, or a rise in his glory RANK that his own accrual earned;
* at most once per marshal per 4 turns, never before turn 6;
* the collective petition needs turn >= 12, three eroding men and >= 300g
  unmet;
* the dispatch's UNMET MARSHALS block names a man only within 2 turns of
  erosion.

Four levers, one per arm of the `BASELINE_SERIES` attribution; all four down
is the pre-F4 curve byte-for-byte. GR5: the AI's marshals climb the same
curve and its grant rung reads the same predicates.
"""

import contextlib
import io
import os

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import dotation as D
from backend.game_logic import jealousy as J
from backend.game_logic.battle_scale import is_decisive_exchange
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIO = os.path.join(REPO, "godot-client", "project-sovereign", "assets",
                        "maps", "europe_1805.json")


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(scope="module")
def _boot():
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


@pytest.fixture
def world(_boot):
    return WorldState.from_dict(_boot.to_dict())


def _execute(world, command):
    with _quiet():
        return CommandExecutor().execute({"command": command}, {"world": world})


def _decisive_win(world, turn=6, attacker="Ney", defender="Mack"):
    """Mack dies whatever the rolls — a decisive victory with Ney as LEAD."""
    world.current_turn = turn
    ney = world.marshals[attacker]
    mack = world.marshals[defender]
    mack.location = ney.location
    # A full corps is cut to 900 (Ney's side destroys it outright); a fresh
    # remnant (_fresh_enemy, 60 men) keeps its size — 900 would stand.
    mack.strength = min(int(mack.strength), 900)
    mack.fortified = False
    result = _execute(world, {"marshal": attacker, "action": "attack",
                              "target": defender, "type": "specific",
                              "_muster_confirmed": True})
    assert result["success"] is True, result.get("message")
    return ney, result


# ═══════════════════════════════════════════════════════════════════════════
# THE CURVE IS DEED-KEYED
# ═══════════════════════════════════════════════════════════════════════════


class TestTheExpectationReadsTheDeeds:

    def test_the_record_no_longer_prices_the_claim(self):
        m = Marshal(name="Ney", strength=20000, location="Paris", nation="France", personality="aggressive")
        m.battles_won = 5
        assert D.get_expectation(m) == 0, "five wins are a record, not a claim"
        m.expectation_steps = 5
        assert D.get_expectation(m) == D.expectation_for_wins(5) == 200

    def test_the_lever_down_reads_battles_won_again(self, monkeypatch):
        monkeypatch.setattr(D, "EXPECTATION_RISES_ON_DEEDS", False)
        m = Marshal(name="Ney", strength=20000, location="Paris", nation="France", personality="aggressive")
        m.battles_won = 3
        m.expectation_steps = 0
        assert D.get_expectation(m) == 120

    def test_the_sovereign_expects_nothing_either_way(self):
        m = Marshal(name="Napoleon", strength=10000, location="Paris", nation="France", personality="sovereign")
        assert m.is_sovereign
        m.expectation_steps = 7
        assert D.get_expectation(m) == 0
        assert not D.raise_expectation(m, type("W", (), {"current_turn": 20})())

    def test_no_claim_is_felt_before_turn_six(self, world):
        ney, result = _decisive_win(world, turn=5)
        assert ney.battles_won >= 1, "the record still ratchets"
        assert ney.expectation_steps == 0
        assert D.get_expectation(ney) == 0
        assert "expectation_note" not in (result.get("battle_report") or {})

    def test_a_decisive_victory_as_lead_raises_it_from_turn_six(self, world):
        ney, result = _decisive_win(world, turn=6)
        assert ney.expectation_steps == 1
        assert ney.last_expectation_rise_turn == 6
        assert D.get_expectation(ney) == 40
        note = (result.get("battle_report") or {}).get("expectation_note", "")
        assert "expectation of reward" in note

    def test_one_rise_per_four_turns(self, world):
        ney, _ = _decisive_win(world, turn=6)
        assert ney.expectation_steps == 1
        # Turn 8: another decisive win, still inside the cooldown.
        world.marshals["Mack2"] = _fresh_enemy(world, "Mack2")
        _decisive_win(world, turn=8, defender="Mack2")
        assert ney.expectation_steps == 1, "one rise per four turns"
        assert "one rise per" in D.expectation_rise_blocked(ney, world)
        world.marshals["Mack3"] = _fresh_enemy(world, "Mack3")
        _decisive_win(world, turn=10, defender="Mack3")
        assert ney.expectation_steps == 2

    def test_the_cooldown_lever_down_lets_them_stack(self, world, monkeypatch):
        monkeypatch.setattr(D, "EXPECTATION_RISE_COOLDOWN_ACTIVE", False)
        ney, _ = _decisive_win(world, turn=6)
        world.marshals["Mack2"] = _fresh_enemy(world, "Mack2")
        _decisive_win(world, turn=7, defender="Mack2")
        assert ney.expectation_steps == 2

    def test_the_cap_is_the_cap(self, world):
        ney = world.marshals["Ney"]
        ney.expectation_steps = 8            # 320 -> capped at 300
        assert D.get_expectation(ney) == D.EXPECTATION_CAP
        _decisive_win(world, turn=6)
        assert ney.expectation_steps == 8
        assert "cap" in D.expectation_rise_blocked(ney, world)

    def test_a_tactical_victory_raises_nothing(self, _boot):
        """A battle won on points, both corps standing, the exchange inside
        2:1 — a record, not a claim, for either lead. (The probe that wrote
        this test had Davout and Napoleon beside Ney, and THAT exchange was
        1.5k to 12.7k — decisive by the war score's own test, and rightly a
        rise.) The rolls decide the outcome, so the fixture hunts a genuine
        points victory across seeds and pins the first it finds; a stalemate
        or an annihilation is not the case under test."""
        import random
        found = None
        for seed in range(12):
            world = WorldState.from_dict(_boot.to_dict())
            world.current_turn = 6
            ney = world.marshals["Ney"]
            mack = world.marshals["Mack"]
            _isolate(world, ney)
            mack.location = ney.location
            mack.fortified = False
            ney.strength = 24000
            mack.strength = 30000
            ney_before, mack_before = ney.strength, mack.strength
            before = (ney.expectation_steps, mack.expectation_steps)
            random.seed(seed)
            with _quiet():
                result = CommandExecutor().execute(
                    {"command": {"marshal": "Ney", "action": "attack",
                                 "target": "Mack", "type": "specific",
                                 "_muster_confirmed": True}},
                    {"world": world})
            assert result["success"] is True
            outcome = str((result.get("events") or [{}])[0].get("outcome", ""))
            if "victory" not in outcome:
                continue
            if outcome in D.FULL_VICTORY_OUTCOMES or mack.strength <= 0 \
                    or ney.strength <= 0 or getattr(mack, "captured_by", ""):
                continue
            # Nobody else fought, so the strength deltas ARE the raw exchange.
            if is_decisive_exchange(ney_before - ney.strength,
                                    mack_before - mack.strength):
                continue
            found = (seed, outcome, before, ney, mack)
            break
        if found is None:
            pytest.skip("no seed in twelve gave a points victory inside 2:1")
        seed, outcome, before, ney, mack = found
        assert (ney.expectation_steps, mack.expectation_steps) == before, (
            f"seed {seed}, {outcome}: a battle won on points is a record, "
            f"not a claim — for either lead")

    def test_a_reinforcer_never_rises(self, world):
        """Davout stands where Ney fights and shares the victory; only the
        LEAD's claim rises."""
        ney = world.marshals["Ney"]
        davout = world.marshals["Davout"]
        davout.location = ney.location
        davout.strength = 25000
        _decisive_win(world, turn=6)
        assert ney.expectation_steps == 1
        assert davout.expectation_steps == 0, "a reinforcement is not a deed"

    def test_the_enemy_climbs_the_same_curve(self, _boot):
        """GR5: Mack, attacking a French corps as lead on turn 6, has his own
        claim on Vienna raised by the same seam — exactly when the victory
        is decisive by the same test (a 52,000-man corps attacking 900 men
        produced 136 to 467 casualties, both standing: a points victory,
        rightly no deed; against 15,000 the exchange stays inside 2:1). A
        sixty-man remnant is destroyed outright. The fixture pins the seam's
        verdict against the rule on every seed and requires a rise."""
        import random
        rises = 0
        for seed in range(12):
            world = WorldState.from_dict(_boot.to_dict())
            world.current_turn = 6
            mack = world.marshals["Mack"]
            ney = world.marshals["Ney"]
            ney.location = mack.location
            _isolate(world, ney)           # no French corps within reach
            ney.strength = 60
            ney.fortified = False
            mack_before, ney_before = mack.strength, ney.strength
            random.seed(seed)
            with _quiet():
                result = CommandExecutor().execute(
                    {"command": {"marshal": "Mack", "action": "attack",
                                 "target": "Ney", "type": "specific",
                                 "_muster_confirmed": True}},
                    {"world": world})
            assert result["success"] is True, result.get("message")
            outcome = str((result.get("events") or [{}])[0].get("outcome", ""))
            if not outcome.startswith("attacker_"):
                continue
            ney_after = world.marshals.get("Ney")
            decisive = D.is_decisive_victory(
                outcome, mack_before - mack.strength,
                ney_before - (ney_after.strength if ney_after else 0),
                loser=ney_after)
            assert mack.expectation_steps == (1 if decisive else 0), (
                f"seed {seed}: {outcome}, decisive={decisive}")
            if decisive:
                assert mack.last_expectation_rise_turn == 6
                rises += 1
        assert rises >= 1, "no seed in twelve gave Mack a decisive victory"


def _isolate(world, marshal):
    """Every OTHER French corps is sent to the far west, so no reinforcement
    reaches the field — the exchange is the two principals' alone."""
    for m in world.marshals.values():
        if m.nation == "France" and m.name != marshal.name:
            m.location = "Brittany"
            m.strategic_order = None


def _fresh_enemy(world, name):
    """An Austrian REMNANT standing where Ney stands — Mack himself is gone
    after the first decisive win. Sixty men: the casualty model leaves a
    900-man corps standing at ~450 (a points victory), while a remnant is
    zeroed by `take_casualties` and the outcome is `attacker_victory`."""
    ney = world.marshals["Ney"]
    m = Marshal(name=name, strength=60, location=ney.location,
                nation="Austria", personality="literal")
    m.original_nation = "Austria"
    return m


# ═══════════════════════════════════════════════════════════════════════════
# THE SECOND DEED — A RANK EARNED
# ═══════════════════════════════════════════════════════════════════════════


class TestTheRankRise:

    def _observe(self, world, marshal, position, accrued):
        return D.observe_glory_rank(marshal, world, position, accrued)

    def test_first_observation_is_silent(self, world):
        world.current_turn = 10
        ney = world.marshals["Ney"]
        assert ney.glory_rank_seen == 0
        assert self._observe(world, ney, 1, True) is False
        assert ney.glory_rank_seen == 1
        assert ney.expectation_steps == 0

    def test_a_rank_earned_this_turn_raises_it(self, world):
        world.current_turn = 10
        ney = world.marshals["Ney"]
        ney.glory_rank_seen = 3
        assert self._observe(world, ney, 1, True) is True
        assert ney.expectation_steps == 1
        assert ney.last_expectation_rise_turn == 10

    def test_a_rank_handed_over_by_decay_is_not_a_deed(self, world):
        world.current_turn = 10
        ney = world.marshals["Ney"]
        ney.glory_rank_seen = 3
        assert self._observe(world, ney, 1, False) is False
        assert ney.expectation_steps == 0
        assert ney.glory_rank_seen == 1, "the position is still recorded"

    def test_a_rank_that_fell_or_held_raises_nothing(self, world):
        world.current_turn = 10
        ney = world.marshals["Ney"]
        ney.glory_rank_seen = 1
        assert self._observe(world, ney, 1, True) is False
        assert self._observe(world, ney, 2, True) is False
        assert ney.expectation_steps == 0

    def test_the_rank_rise_keeps_the_floor_and_the_cooldown(self, world):
        ney = world.marshals["Ney"]
        ney.glory_rank_seen = 3
        world.current_turn = 5
        assert self._observe(world, ney, 1, True) is False, "before turn 6"
        ney.glory_rank_seen = 3
        world.current_turn = 6
        assert self._observe(world, ney, 1, True) is True
        ney.glory_rank_seen = 3
        world.current_turn = 8
        assert self._observe(world, ney, 1, True) is False, "inside the cooldown"

    def test_the_jealousy_pass_observes_every_ladder(self, world):
        """The once-per-turn pass records positions for every nation (GR5)
        and raises a claim for a man whose glory carried him up a rung."""
        world.current_turn = 9
        ney = world.marshals["Ney"]
        davout = world.marshals["Davout"]
        # Last turn's ladder, as remembered: Davout above Ney.
        for m in world.marshals.values():
            if m.nation == "France" and not getattr(m, "is_sovereign", False):
                m.glory_rank_seen = 0
        ney.glory_rank_seen = 2
        davout.glory_rank_seen = 1
        davout.glory_events = [{"turn": 8, "points": 3}]
        ney.glory_events = [{"turn": 8, "points": 2}, {"turn": 9, "points": 4}]
        world._jealousy_processed_turn = None
        with _quiet():
            J.process_turn(world)
        assert ney.glory_rank_seen == 1
        assert ney.expectation_steps == 1, "Ney passed Davout by his own deed"
        assert davout.expectation_steps == 0
        # An Austrian ladder is recorded too.
        mack = world.marshals["Mack"]
        assert mack.glory_rank_seen >= 1


# ═══════════════════════════════════════════════════════════════════════════
# THE COLLECTIVE PETITION WAITS
# ═══════════════════════════════════════════════════════════════════════════


def _make_eroding(world, name, steps=3):
    m = world.marshals[name]
    m.expectation_steps = steps
    m.dotation_regions = []
    m.pension = 0
    m.expectation_grace_turn = int(world.current_turn) - D.GRACE_TURNS
    assert D.is_eroding(m, world)
    return m


class TestTheCollectivePetitionWaits:

    def _three(self, world, steps=3):
        return [_make_eroding(world, n, steps) for n in ("Ney", "Murat", "Lannes")]

    def test_no_petition_before_turn_twelve(self, world):
        world.current_turn = 8
        self._three(world)
        with _quiet():
            J.check_fontainebleau(world, [])
        assert world.pending_marshal_petition is None

    def test_no_petition_over_small_change(self, world):
        world.current_turn = 12
        self._three(world, steps=2)          # 3 x 80 = 240 < 300
        with _quiet():
            J.check_fontainebleau(world, [])
        assert world.pending_marshal_petition is None

    def test_the_petition_fires_at_twelve_with_the_bill_over_three_hundred(self, world):
        world.current_turn = 12
        self._three(world, steps=3)          # 3 x 120 = 360
        events = []
        with _quiet():
            J.check_fontainebleau(world, events)
        petition = world.pending_marshal_petition
        assert petition and petition["kind"] == "fontainebleau"
        assert any(e["type"] == "fontainebleau_petition" for e in events)

    def test_the_wait_still_re_arms_the_latch(self, world):
        """The count check runs first, so a count that fell during the wait
        re-arms the latch — the wait does not swallow the re-arm."""
        world.current_turn = 8
        world.fontainebleau_armed = False
        self._three(world)
        world.marshals["Ney"].expectation_steps = 0
        with _quiet():
            J.check_fontainebleau(world, [])
        assert world.fontainebleau_armed is True

    def test_the_lever_down_fires_on_turn_seven(self, world, monkeypatch):
        monkeypatch.setattr(J, "THE_COLLECTIVE_PETITION_WAITS", False)
        world.current_turn = 7
        self._three(world, steps=2)
        with _quiet():
            J.check_fontainebleau(world, [])
        assert world.pending_marshal_petition is not None


# ═══════════════════════════════════════════════════════════════════════════
# THE UNMET BLOCK WAITS
# ═══════════════════════════════════════════════════════════════════════════


class TestTheUnmetBlockWaits:

    def _owing(self, world, grace_turns_ago):
        world.current_turn = 10
        ney = world.marshals["Ney"]
        ney.expectation_steps = 3
        ney.dotation_regions = []
        ney.pension = 0
        ney.expectation_grace_turn = (
            -1 if grace_turns_ago is None else 10 - grace_turns_ago)
        return ney

    def _row(self, world):
        return next((r for r in D.build_unmet_marshals(world, "France")
                     if r["marshal"] == "Ney"), None)

    def test_a_fresh_shortfall_is_the_rails_row_not_the_briefings(self, world):
        self._owing(world, None)
        assert self._row(world) is None
        self._owing(world, 1)                 # 3 turns of patience left
        assert self._row(world) is None

    def test_within_two_turns_of_erosion_he_is_named(self, world):
        self._owing(world, 2)                 # 2 left
        row = self._row(world)
        assert row and row["grace_turns_left"] == 2 and row["eroding"] is False
        self._owing(world, 3)                 # 1 left
        assert self._row(world)["grace_turns_left"] == 1

    def test_an_eroding_man_is_always_named(self, world):
        self._owing(world, D.GRACE_TURNS + 2)
        row = self._row(world)
        assert row and row["eroding"] is True

    def test_a_captive_is_never_an_alarm(self, world):
        ney = self._owing(world, None)
        ney.captured_by = "Austria"
        assert self._row(world) is None

    def test_the_lever_down_names_him_at_once(self, world, monkeypatch):
        monkeypatch.setattr(D, "THE_UNMET_BLOCK_WAITS", False)
        self._owing(world, None)
        assert self._row(world)["grace_turns_left"] == D.GRACE_TURNS


# ═══════════════════════════════════════════════════════════════════════════
# THE SAVE, THE AI, THE PREDICATE
# ═══════════════════════════════════════════════════════════════════════════


class TestTheSaveAndTheAI:

    def test_the_three_fields_round_trip(self):
        m = Marshal(name="Ney", strength=20000, location="Paris", nation="France", personality="aggressive")
        m.expectation_steps = 4
        m.last_expectation_rise_turn = 9
        m.glory_rank_seen = 2
        back = Marshal.from_dict(m.to_dict())
        assert (back.expectation_steps, back.last_expectation_rise_turn,
                back.glory_rank_seen) == (4, 9, 2)

    def test_a_pre_f4_save_keeps_what_he_was_owed(self):
        m = Marshal(name="Ney", strength=20000, location="Paris", nation="France", personality="aggressive")
        m.battles_won = 5
        data = m.to_dict()
        for key in ("expectation_steps", "last_expectation_rise_turn", "glory_rank_seen"):
            data.pop(key, None)
        back = Marshal.from_dict(data)
        assert back.expectation_steps == 5, "backfilled from the old curve's count"
        assert back.last_expectation_rise_turn == -1
        assert back.glory_rank_seen == 0
        assert D.get_expectation(back) == 200

    def test_the_ai_grant_rung_reads_the_same_curve(self, world):
        """An Austrian marshal with five wins on his record but no deed
        yet has no shortfall the rung can see; five deeds and it endows."""
        from backend.ai.enemy_ai import EnemyAI
        mack = world.marshals["Mack"]
        for m in world.marshals.values():
            if m.nation == "Austria":
                m.expectation_steps = 0
                m.pension = 0
        mack.battles_won = 5
        ai = EnemyAI(CommandExecutor())
        assert ai._find_dotation_grant("Austria", world, 5000) is None
        mack.expectation_steps = 5
        grant = ai._find_dotation_grant("Austria", world, 5000)
        assert grant and grant["marshal"] == "Mack"

    def test_the_decisive_exchange_is_the_war_scores_own(self):
        assert is_decisive_exchange(2000, 9000) is True
        assert is_decisive_exchange(9000, 2000) is True
        assert is_decisive_exchange(4000, 7000) is False, "inside 2:1"
        assert is_decisive_exchange(1000, 4000) is False, "below 10,000"
        assert is_decisive_exchange(0, 12000) is False

    def test_record_battle_reads_the_shared_predicate(self, world):
        """A 2.5:1 exchange above 10,000 dead is decisive for the WAR SCORE
        exactly because it is decisive for the reward curve — one predicate,
        `battle_scale.is_decisive_exchange`, read by both."""
        from backend.game_logic.diplomacy import record_battle
        assert world.is_at_war("France", "Austria")
        key = world._make_diplo_key("France", "Austria")
        world.decisive_battles = {}
        with _quiet():
            record_battle(world, "France", "Austria", "France", 4000, 10000, "Swabia")
        records = world.decisive_battles.get(key, [])
        assert len(records) == 1, records
        assert records[0]["ratio"] == 2.5

    def test_decisive_by_outcome_fate_or_exchange(self):
        loser = Marshal(name="Mack", strength=0, location="Swabia", nation="Austria", personality="literal")
        assert D.is_decisive_victory("attacker_victory", 1000, 1000) is True
        assert D.is_decisive_victory("attacker_tactical_victory", 1000, 1000,
                                     loser=loser) is True, "the loser is gone"
        captive = Marshal(name="Mack", strength=5000, location="Swabia", nation="Austria", personality="literal")
        captive.captured_by = "France"
        assert D.is_decisive_victory("attacker_tactical_victory", 1000, 1000,
                                     loser=captive) is True
        standing = Marshal(name="Mack", strength=5000, location="Swabia", nation="Austria", personality="literal")
        assert D.is_decisive_victory("attacker_tactical_victory", 3000, 9000,
                                     loser=standing) is True, "a decisive exchange"
        assert D.is_decisive_victory("attacker_tactical_victory", 3000, 4000,
                                     loser=standing) is False


# ═══════════════════════════════════════════════════════════════════════════
# THE LIVE REVIEW'S OWN OPENING — ULM ON TURN ONE
# ═══════════════════════════════════════════════════════════════════════════


class TestUlmRaisesNoClaimOnTurnOne:
    """The review's measured board: `Ney, attack Mack` on turn 1 destroys
    Mack's corps and captures him. Under F4 no claim is felt, the dispatch
    carries no UNMET MARSHALS block, and no collective petition can fire
    before turn 12 — the first ten minutes are the campaign's, not the
    marshals' bills'."""

    def test_the_first_victory_asks_for_nothing(self, world):
        from backend.game_logic.dispatch import build_morning_dispatch
        ney = world.marshals["Ney"]
        mack = world.marshals["Mack"]
        mack.strength = 900
        mack.fortified = False
        mack.location = ney.location
        result = _execute(world, {"marshal": "Ney", "action": "attack",
                                  "target": "Mack", "type": "specific",
                                  "_muster_confirmed": True})
        assert result["success"] is True
        assert ney.battles_won >= 1
        assert ney.expectation_steps == 0
        assert "expectation_note" not in (result.get("battle_report") or {})
        with _quiet():
            dispatch = build_morning_dispatch(world)
        situation = dispatch["situation"]
        assert situation["unmet_marshals"] == []
        assert situation["expectation_rises"] == []
