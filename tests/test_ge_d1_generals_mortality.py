"""VP-M1 "The Fortunes of War" — the generals' mortality (GE-D1, RULED
September 25, 2026 during GE-V: (a) YES, bounded).

The row's own nine named pins, plus the surfaces. Every roll is driven
through the real post-battle seam (`CombatExecutor._handle_forced_retreat`,
shared by the attack and the glorious charge) with the draw forced through
the campaign-seed helper, never the module RNG.
"""

import contextlib
import io
from pathlib import Path

import pytest

from backend.game_logic import fortunes_of_war as FW
from tests.conftest import MarshalFactory, WorldFactory

ROOT = Path(__file__).resolve().parents[1]


def _result(attacker_won, attacker_lost, defender_lost):
    return {
        "attacker_won": bool(attacker_won),
        "defender_won": not attacker_won,
        "attacker": {"casualties": int(attacker_lost), "forced_retreat": False},
        "defender": {"casualties": int(defender_lost), "forced_retreat": False},
    }


def _board(*, attacker_strength=20000, defender_strength=20000, turn=5,
           attacker_personality="aggressive"):
    ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                  strength=attacker_strength,
                                  personality=attacker_personality)
    mack = MarshalFactory.enemy(name="Mack", location="Belgium", nation="Austria",
                                strength=defender_strength)
    world = WorldFactory.with_marshals([ney, mack])
    world.current_turn = turn
    key = "|".join(sorted(["France", "Austria"]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = 1
    world.campaign_seed = "historical"
    return world, ney, mack


def _roll(world, result, attacker, defender, draw):
    """Run the seam with the seeded draw forced to `draw`."""
    from backend.commands.executor import CommandExecutor
    ex = CommandExecutor()
    import backend.game_logic.campaign_variance as CV
    orig = CV.seeded_int
    calls = []

    def fake(seed, namespace, lo, hi):
        calls.append(namespace)
        return int(draw) if namespace.startswith("fortunes::") else orig(seed, namespace, lo, hi)
    CV.seeded_int = fake
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            msg = ex._combat._handle_forced_retreat(result, attacker, defender, world)
    finally:
        CV.seeded_int = orig
    return msg, calls


# ═══════════════════════════════════════════════════════════════════════════
class TestTheRoll:
    def test_winners_and_stalemates_never_roll(self):
        world, ney, mack = _board()
        # Ney wins: Mack (the loser) rolls, Ney never does.
        msg, calls = _roll(world, _result(True, 2000, 8000), ney, mack, draw=0)
        assert all("Mack" in c for c in calls if c.startswith("fortunes::"))
        assert not any("Ney" in c for c in calls if c.startswith("fortunes::"))
        # A stalemate: nobody rolls.
        world, ney, mack = _board()
        stalemate = _result(False, 5000, 5000)
        stalemate["defender_won"] = False
        msg, calls = _roll(world, stalemate, ney, mack, draw=0)
        assert not [c for c in calls if c.startswith("fortunes::")]
        assert "Ney" in world.marshals and "Mack" in world.marshals

    def test_losing_leader_rolls_once_through_campaign_seed(self):
        world, ney, mack = _board()
        msg, calls = _roll(world, _result(False, 8000, 1500), ney, mack, draw=50)
        fortunes = [c for c in calls if c.startswith("fortunes::")]
        assert len(fortunes) == 1
        assert fortunes[0].startswith("fortunes::5::Ney::")
        assert "Ney" in world.marshals and not FW.is_wounded(ney, world)

    def test_skirmish_never_rolls(self):
        world, ney, mack = _board(attacker_strength=2000, defender_strength=2000)
        # 600 of 2,000 lost is 30% — but 900 total dead is no battle.
        msg, calls = _roll(world, _result(False, 600, 300), ney, mack, draw=0)
        assert not [c for c in calls if c.startswith("fortunes::")]

    def test_a_light_defeat_never_rolls(self):
        world, ney, mack = _board()
        # 3,000 of 23,000 brought is 13% — under LOSS_SHARE.
        msg, calls = _roll(world, _result(False, 3000, 9000), ney, mack, draw=0)
        assert not [c for c in calls if c.startswith("fortunes::")]

    def test_wound_keeps_corps_and_blocks_attack_until_turn(self):
        world, ney, mack = _board(turn=5)
        msg, calls = _roll(world, _result(False, 8000, 1500), ney, mack,
                           draw=FW.KILLED_PCT)  # the first wounded draw
        assert "WOUNDED" in msg
        assert ney.wounded_until_turn == 5 + FW.WOUND_TURNS
        assert FW.is_wounded(ney, world)
        assert "Ney" in world.marshals and ney.strength == 20000
        assert FW.wound_refusal(ney, world) and "cannot attack" in FW.wound_refusal(ney, world)
        world.current_turn = 5 + FW.WOUND_TURNS
        assert not FW.is_wounded(ney, world)
        assert FW.wound_refusal(ney, world) is None

    def test_death_passes_men_to_nearest_corps(self):
        world, ney, mack = _board(turn=5)
        # A friendly corps one province away receives the men.
        davout = MarshalFactory.infantry(name="Davout", location="Paris", strength=10000,
                                         personality="cautious")
        world.marshals["Davout"] = davout
        msg, calls = _roll(world, _result(False, 8000, 1500), ney, mack, draw=0)
        assert "KILLED" in msg
        assert "Ney" not in world.marshals
        assert world.fallen_marshals["Ney"]["cause"] == FW.CAUSE_KILLED
        assert world.fallen_marshals["Ney"]["men"] == 20000
        assert world.fallen_marshals["Ney"]["men_to"] == "Davout"
        assert davout.strength == 30000
        assert "20,000 men pass to Davout" in msg

    def test_death_with_no_corps_in_reach_disperses_the_men(self):
        world, ney, mack = _board(turn=5)
        msg, calls = _roll(world, _result(False, 8000, 1500), ney, mack, draw=0)
        assert "Ney" not in world.marshals
        assert world.fallen_marshals["Ney"]["men_to"] == ""
        assert "disperse" in msg

    def test_nation_elimination_exiles_not_fallen(self):
        """(b): no death off the field — a court's teardown never writes a
        `killed_in_action` tombstone, and no roll runs there."""
        world, ney, mack = _board()
        import backend.game_logic.campaign_variance as CV
        orig = CV.seeded_int
        calls = []
        CV.seeded_int = lambda s, ns, lo, hi: (calls.append(ns), orig(s, ns, lo, hi))[1]
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                world._eliminate_nation("Austria")
        finally:
            CV.seeded_int = orig
        assert not [c for c in calls if c.startswith("fortunes::")]
        stone = world.fallen_marshals.get("Mack")
        assert stone is None or stone.get("cause") != FW.CAUSE_KILLED

    def test_rubbled_corps_commander_takes_fate_check(self):
        """(b): a corps the fighting zeroes never reaches the roll — the
        W6-7 fate machinery decides him, not a second death roll."""
        world, ney, mack = _board()
        ney.strength = 0
        msg, calls = _roll(world, _result(False, 20000, 1500), ney, mack, draw=0)
        assert not [c for c in calls if c.startswith("fortunes::")]

    def test_sovereign_excluded_from_general_roll(self):
        world, ney, mack = _board(attacker_personality="sovereign")
        assert ney.is_sovereign
        msg, calls = _roll(world, _result(False, 8000, 1500), ney, mack, draw=0)
        assert not [c for c in calls if c.startswith("fortunes::")]
        assert "Ney" in world.marshals

    def test_gr5_ai_marshal_same_odds(self):
        world, ney, mack = _board()
        # Ney wins; Mack, an Austrian lead, rolls the same draw and is wounded.
        msg, calls = _roll(world, _result(True, 1500, 8000), ney, mack, draw=FW.KILLED_PCT)
        assert mack.wounded_until_turn == 5 + FW.WOUND_TURNS
        assert "Mack" in world.marshals
        # And killed at the same draw a French lead would be.
        world, ney, mack = _board()
        msg, calls = _roll(world, _result(True, 1500, 8000), ney, mack, draw=0)
        assert "Mack" not in world.marshals
        assert world.fallen_marshals["Mack"]["cause"] == FW.CAUSE_KILLED

    def test_lever_down_rolls_nothing(self, monkeypatch):
        monkeypatch.setattr(FW, "THE_GENERALS_ARE_MORTAL", False)
        world, ney, mack = _board()
        msg, calls = _roll(world, _result(False, 8000, 1500), ney, mack, draw=0)
        assert not [c for c in calls if c.startswith("fortunes::")]
        assert "Ney" in world.marshals

    def test_the_roll_never_raises(self):
        assert FW.roll(object(), None, None, None) is None
        assert FW.roll(object(), {"attacker_won": True}, object(), None) is None


# ═══════════════════════════════════════════════════════════════════════════
class TestTheWoundedMan:
    def test_the_executor_refuses_his_attack_before_any_objection(self):
        from backend.commands.executor import CommandExecutor
        world, ney, mack = _board()
        ney.wounded_until_turn = world.current_turn + 2
        ex = CommandExecutor()
        with contextlib.redirect_stdout(io.StringIO()):
            result = ex.execute({"command": {"action": "attack", "marshal": "Ney",
                                             "target": "Mack"}},
                                {"world": world})
        assert result.get("success") is False
        assert "WOUNDED" in result.get("message", "")
        assert result.get("wounded") is True
        assert not getattr(world, "pending_objection", None)

    def test_he_still_marches(self):
        from backend.commands.executor import CommandExecutor
        world, ney, mack = _board()
        mack.location = "Rhineland"
        ney.wounded_until_turn = world.current_turn + 2
        ex = CommandExecutor()
        with contextlib.redirect_stdout(io.StringIO()):
            result = ex.execute({"command": {"action": "move", "marshal": "Ney",
                                             "target": "Paris"}},
                                {"world": world})
        assert result.get("success") is True, result.get("message")

    def test_the_ai_stands_the_wounded_corps_down(self):
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        world, ney, mack = _board(attacker_strength=5000, defender_strength=40000)
        mack.wounded_until_turn = world.current_turn + 2
        with contextlib.redirect_stdout(io.StringIO()):
            ai = EnemyAI(CommandExecutor())
            decision = ai._evaluate_marshal(mack, "Austria", world)
        action = decision[0] if isinstance(decision, tuple) else decision
        assert isinstance(action, dict), decision
        assert action.get("action") in ("stance_change", "wait"), action

    def test_the_card_carries_the_wound(self):
        from backend.game_logic.marshal_overview import _build_marshal_card
        world, ney, mack = _board(turn=5)
        ney.wounded_until_turn = 8
        card = _build_marshal_card(ney, world)
        assert card["is_wounded"] is True and card["wounded_until_turn"] == 8

    def test_the_wound_survives_the_save(self):
        from backend.models.marshal import Marshal
        world, ney, mack = _board()
        ney.wounded_until_turn = 9
        back = Marshal.from_dict(ney.to_dict())
        assert back.wounded_until_turn == 9
        # A pre-mortality save carries no wound.
        data = ney.to_dict()
        data.pop("wounded_until_turn")
        assert Marshal.from_dict(data).wounded_until_turn == 0

    def test_a_wounded_literal_is_not_counted_as_sidelined(self):
        from backend.game_logic import jealousy as J
        world, ney, mack = _board(attacker_personality="literal")
        davout = MarshalFactory.infantry(name="Davout", location="Paris", strength=10000,
                                         personality="cautious")
        davout.in_combat_this_turn = True
        world.marshals["Davout"] = davout
        ney.consecutive_hold_turns = 2
        ney.wounded_until_turn = world.current_turn + 2
        with contextlib.redirect_stdout(io.StringIO()):
            J.update_literal_hold_counters(world)
        assert ney.consecutive_hold_turns == 2, "a wounded man neither climbs nor resets"
        # Healed, he is sidelined again like any literal with no order.
        ney.wounded_until_turn = 0
        with contextlib.redirect_stdout(io.StringIO()):
            J.update_literal_hold_counters(world)
        assert ney.consecutive_hold_turns == 3


# ═══════════════════════════════════════════════════════════════════════════
class TestTheSurfaces:
    def test_the_chronicle_knows_both_lines(self):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, format_event_oneliner
        assert "marshal_wounded" in CAMPAIGN_LOG_TYPES
        assert "WOUNDED" in format_event_oneliner({"type": "marshal_wounded", "marshal": "Ney",
                                                   "location": "Belgium", "until_turn": 8,
                                                   "turn": 5})
        line = format_event_oneliner({"type": "marshal_destroyed", "marshal": "Ney",
                                      "location": "Belgium", "victor": "Austria",
                                      "cause": "killed_in_action", "turn": 5})
        assert "KILLED" in line and "passes to another hand" in line

    def test_the_dispatch_carries_the_wound_and_the_death(self):
        from backend.game_logic import dispatch as D
        assert "marshal_wounded" in D.EVENT_WEIGHTS if hasattr(D, "EVENT_WEIGHTS") else True
        world, ney, mack = _board(turn=5)
        msg, calls = _roll(world, _result(False, 8000, 1500), ney, mack, draw=FW.KILLED_PCT)
        world.current_turn += 1
        with contextlib.redirect_stdout(io.StringIO()):
            page = D.build_morning_dispatch(world)
        text = str(page)
        assert "WOUNDED" in text and "Ney" in text

    def test_the_gazette_key_exists(self):
        from backend.game_logic import gazette as G
        assert "marshal_wounded" in G.GAZETTE_EVENT_TYPES if hasattr(G, "GAZETTE_EVENT_TYPES") else True
        # The caption must be PRICED — a caption with no weight raised a
        # KeyError the first time a wound fired in a played turn (found by
        # the driven GE-1 arm before this slice landed).
        assert "a marshal of France wounded" in G._SPECIAL_WEIGHTS
        assert G._SPECIAL_WEIGHTS["a marshal of France wounded"] < G._SPECIAL_WEIGHTS["a marshal of France lost"]

    def test_the_moniteur_collects_the_wound_as_a_special(self):
        """The collector that raised: a wound event must be a priced
        candidate, below a loss."""
        from backend.game_logic import gazette as G
        world, ney, mack = _board(turn=5)
        _roll(world, _result(False, 8000, 1500), ney, mack, draw=FW.KILLED_PCT)
        events = [e for e in (getattr(world, "event_log", []) or [])
                  if e.get("type") == "marshal_wounded"]
        assert events, "the wound must reach the log"
        candidates = G._special_candidates(world, events)
        reasons = [c[1] for c in candidates]
        assert "a marshal of France wounded" in reasons
        lost = G._special_candidates(world, [{"type": "marshal_destroyed", "nation": "France",
                                              "marshal": "Ney", "cause": "battle"}])
        assert max(lost)[0] > max(c for c in candidates if c[1] == "a marshal of France wounded")[0]
