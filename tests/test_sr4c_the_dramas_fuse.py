"""SR-4c "The drama's fuse" (Score Mandate Chunk 4, AAR-D3, Sept 26 2026).

The Jealousy gate re-opened (JEALOUSY_SPEC §0.7). Measured first on the
session exit's AAR arm: 21 French grievances and 13 audience cards in 18
turns (Soult's on turns 12, 15 and 17; Murat's three turns apart), the crown
on Ney on turn 1 for ONE Shadowed point, "the laurels have passed" on turn 9
when Ney and Murat stood level, and — in the hand-played AAR — a crown for
Oudinot's 420-against-1,007 fight with a raid, the only glory in the window.

Four levers (jealousy.py): THE_LAUREL_FLOOR, THE_CROWN_WANTS_LAURELS,
THE_AUDIENCE_WAITS, THE_FIRES_SAY_WHY. Each class pins its lever with a
sensitivity arm (the lever down reproduces the defect).
"""

from pathlib import Path

import pytest

from backend.game_logic import battle_scale
from backend.game_logic import jealousy as J
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "europe_1805.json")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    w = WorldState.from_dict(world1805.to_dict())
    w.authority_tracker.authority = 50
    return w


def _glory_today(world, name):
    return sum(int(e.get("points", 0)) for e in world.marshals[name].glory_events
               if int(e.get("turn", -1)) == int(world.current_turn))


def _clear_glory(world):
    for m in world.marshals.values():
        m.glory_events = []
        m.glory_crowned = False


# ═══════════════════════════ THE LAUREL FLOOR ═══════════════════════════════

class TestTheLaurelFloor:
    def test_the_predicate_is_the_engines_own_battle_floor(self):
        assert J.is_laurel(400, 500) is False          # 900: a skirmish
        assert J.is_laurel(420, 1007) is True          # the Oudinot fight: a battle
        assert J.is_laurel(600, 400) is True           # exactly the floor
        assert J.is_laurel("x", 3) is True             # unreadable is never downgraded

    def test_the_floor_reads_battle_scale_at_call_time(self, monkeypatch):
        monkeypatch.setattr(battle_scale, "MIN_BATTLE_CASUALTIES", 5000)
        assert J.is_laurel(1500, 2000) is False
        monkeypatch.setattr(battle_scale, "MIN_BATTLE_CASUALTIES", 100)
        assert J.is_laurel(40, 70) is True

    def test_the_decisive_arm_is_read_when_the_floor_is_retuned(self, monkeypatch):
        # Retune the floor above the decisive test's own minimum: a decisive
        # exchange must still count (the arm the ruling names).
        monkeypatch.setattr(battle_scale, "MIN_BATTLE_CASUALTIES", 50000)
        assert J.is_laurel(3000, 9000) is True          # > 10,000 at 3:1
        assert J.is_laurel(5000, 6000) is False         # not decisive

    def test_a_skirmish_earns_and_costs_no_glory(self, world):
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        lannes = world.marshals["Lannes"]
        _clear_glory(world)
        J.record_battle_glory(world, ney, mack, True, False, 300, 500,
                              conquered=True, pre_attacker_strength=4000,
                              pre_defender_strength=5000,
                              attacker_participants=[ney, lannes])
        assert _glory_today(world, "Ney") == 0
        assert _glory_today(world, "Lannes") == 0
        assert _glory_today(world, "Mack") == 0

    def test_a_battle_still_earns_its_laurels(self, world):
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        _clear_glory(world)
        J.record_battle_glory(world, ney, mack, True, False, 420, 1007,
                              conquered=False, pre_attacker_strength=4500,
                              pre_defender_strength=3000)
        assert _glory_today(world, "Ney") == 2          # victory + decisive
        # (Mack, outnumbered, loses no glory — spec §1's no-stigma rule, unchanged)
        assert _glory_today(world, "Mack") == 0

    def test_lever_down_a_skirmish_scores(self, world, monkeypatch):
        monkeypatch.setattr(J, "THE_LAUREL_FLOOR", False)
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        _clear_glory(world)
        J.record_battle_glory(world, ney, mack, True, False, 300, 500,
                              conquered=True, pre_attacker_strength=4000,
                              pre_defender_strength=5000)
        assert _glory_today(world, "Ney") > 0

    def test_a_skirmish_stalemate_earns_no_partial_glory(self, world):
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        _clear_glory(world)
        # out-bled 2:1 but tiny: DR-1 would have paid STALEMATE_GLORY
        J.record_battle_glory(world, ney, mack, False, False, 200, 500,
                              conquered=False, pre_attacker_strength=4000,
                              pre_defender_strength=5000)
        assert _glory_today(world, "Ney") == 0


# ═══════════════════════════ THE CROWN WANTS LAURELS ════════════════════════

def _set_glory(world, name, points):
    J._append_glory(world.marshals[name], world.current_turn, points)


class TestTheCrownWantsLaurels:
    def test_one_shadowed_point_wears_no_crown(self, world):
        _clear_glory(world)
        _set_glory(world, "Ney", 1)
        J.recompute_crowns(world)
        assert not world.marshals["Ney"].glory_crowned

    def test_two_points_wear_no_crown(self, world):
        _clear_glory(world)
        _set_glory(world, "Ney", 2)
        J.recompute_crowns(world)
        assert not world.marshals["Ney"].glory_crowned

    def test_the_floor_is_crowned(self, world):
        _clear_glory(world)
        _set_glory(world, "Ney", J.CROWN_MIN_GLORY)
        events = J.recompute_crowns(world)
        assert world.marshals["Ney"].glory_crowned
        assert any(e["type"] == "glory_crowned" for e in events)

    def test_the_floor_binds_every_board(self, world):
        _clear_glory(world)
        _set_glory(world, "ArchdukeCharles", 2)
        J.recompute_crowns(world)
        assert not world.marshals["ArchdukeCharles"].glory_crowned
        _set_glory(world, "ArchdukeCharles", 1)
        J.recompute_crowns(world)
        assert world.marshals["ArchdukeCharles"].glory_crowned

    def test_lever_down_any_point_is_crowned(self, world, monkeypatch):
        monkeypatch.setattr(J, "THE_CROWN_WANTS_LAURELS", False)
        _clear_glory(world)
        _set_glory(world, "Ney", 1)
        J.recompute_crowns(world)
        assert world.marshals["Ney"].glory_crowned


# ═══════════════════════════ THE FIRES SAY WHY ═══════════════════════════════

class TestTheCrownLostSaysWhere:
    def _crown_ney(self, world):
        _clear_glory(world)
        _set_glory(world, "Ney", 4)
        J.recompute_crowns(world)
        assert world.marshals["Ney"].glory_crowned

    def _lost(self, world):
        before = len(world.event_log)
        events = J.recompute_crowns(world)
        lost = [e for e in events if e["type"] == "glory_crown_lost"]
        rows = [r for r in world.event_log[before:] if r.get("type") == "glory_crown_lost"]
        return lost, rows

    def test_passed_to_a_man(self, world):
        self._crown_ney(world)
        _set_glory(world, "Murat", 6)
        lost, rows = self._lost(world)
        assert "passed to Murat" in lost[0]["message"], lost
        assert rows[0]["why"] == "passed" and rows[0]["successor"] == "Murat"

    def test_level_names_the_men_and_no_one_wears_it(self, world):
        self._crown_ney(world)
        _set_glory(world, "Murat", 4)
        lost, rows = self._lost(world)
        msg = lost[0]["message"]
        assert "stand level" in msg and "Murat" in msg and "no one wears" in msg, msg
        assert "passed" not in msg
        assert rows[0]["why"] == "level"

    def test_faded_when_nobody_holds_enough(self, world):
        self._crown_ney(world)
        world.marshals["Ney"].glory_events = [{"turn": world.current_turn, "points": 1}]
        lost, rows = self._lost(world)
        msg = lost[0]["message"]
        assert "faded" in msg and "passed" not in msg, msg
        assert rows[0]["why"] == "faded"

    def test_the_log_composes_its_sentence_from_the_row(self):
        from backend.campaign_log import format_event_oneliner
        faded = format_event_oneliner({"type": "glory_crown_lost", "marshal": "Ney",
                                       "nation": "France", "why": "faded", "successor": ""})
        assert "faded" in faded and "passed" not in faded
        passed = format_event_oneliner({"type": "glory_crown_lost", "marshal": "Ney",
                                        "nation": "France", "why": "passed",
                                        "successor": "Murat"})
        assert "passed to" in passed and "Murat" in passed
        legacy = format_event_oneliner({"type": "glory_crown_lost", "marshal": "Ney",
                                        "nation": "France"})
        assert legacy.endswith("the laurels have passed")

    def test_lever_down_says_passed_for_a_tie(self, world, monkeypatch):
        monkeypatch.setattr(J, "THE_FIRES_SAY_WHY", False)
        self._crown_ney(world)
        _set_glory(world, "Murat", 4)
        lost, rows = self._lost(world)
        assert lost[0]["message"].endswith("the laurels have passed.")
        assert "why" not in rows[0]


class TestABrokenRivalIsNotGone:
    def _envy(self, world):
        massena, davout = world.marshals["Massena"], world.marshals["Davout"]
        massena.jealous_of = "Davout"
        massena.jealousy_turns_remaining = 3
        return massena, davout

    def _pass_messages(self, world):
        events = []
        world._jealousy_processed_turn = None
        events = J.process_turn(world)
        return [e.get("message", "") for e in events
                if e.get("type") == "jealousy_resolved" and e.get("marshal") == "Massena"]

    def test_a_broken_rival_is_named_broken(self, world):
        massena, davout = self._envy(world)
        davout.broken = True
        msgs = self._pass_messages(world)
        assert msgs and "falling back" in msgs[0], msgs
        assert "no one left to envy" not in msgs[0]
        assert massena.jealous_of is None

    def test_a_destroyed_rival_is_gone(self, world):
        massena, davout = self._envy(world)
        davout.strength = 0
        msgs = self._pass_messages(world)
        assert msgs and "no one left to envy" in msgs[0], msgs

    def test_lever_down_a_broken_rival_is_gone(self, world, monkeypatch):
        monkeypatch.setattr(J, "THE_FIRES_SAY_WHY", False)
        massena, davout = self._envy(world)
        davout.broken = True
        msgs = self._pass_messages(world)
        assert msgs and "no one left to envy" in msgs[0], msgs


# ═══════════════════════════ THE AUDIENCE WAITS ═════════════════════════════

class TestTheAudienceWaits:
    def _fire(self, world, who, whom, delta=2, threshold=2):
        events = []
        J.apply_jealousy(world, world.marshals[who], world.marshals[whom],
                         delta=delta, threshold=threshold, events=events)
        return [e for e in events if e.get("type") == "jealousy_fired"]

    def _answer_and_cool(self, world, who):
        J.handle_petition_response(world, "acknowledge")
        J.clear_jealousy(world, world.marshals[who], resolved_by_action=False)
        assert world.pending_marshal_petition is None

    def test_the_first_audience_is_heard_and_stamped(self, world):
        world.current_turn = 4
        self._fire(world, "Massena", "Davout")
        assert world.pending_marshal_petition["kind"] == "jealousy_confrontation"
        assert J.last_audience_turn(world.marshals["Massena"]) == 4

    def test_he_does_not_ask_again_within_the_cooldown(self, world):
        world.current_turn = 4
        self._fire(world, "Massena", "Davout")
        self._answer_and_cool(world, "Massena")
        world.current_turn = 7
        fires = self._fire(world, "Massena", "Soult")
        assert world.pending_marshal_petition is None
        # the grievance itself stands — only the card waits
        assert world.marshals["Massena"].jealous_of == "Soult"
        msg = fires[0]["message"]
        assert "He asked for an audience on turn 4" in msg, msg
        assert f"before turn {4 + J.AUDIENCE_COOLDOWN_TURNS}" in msg, msg
        # the key stays unstamped: the card retries on the pair's next fire
        seen = set(world.jealousy_confrontations_seen or [])
        assert not any(k.startswith(J._pair_key("Massena", "Soult")) for k in seen)

    def test_he_asks_again_when_the_cooldown_has_run(self, world):
        world.current_turn = 4
        self._fire(world, "Massena", "Davout")
        self._answer_and_cool(world, "Massena")
        world.current_turn = 4 + J.AUDIENCE_COOLDOWN_TURNS
        self._fire(world, "Massena", "Soult")
        assert world.pending_marshal_petition is not None
        assert world.pending_marshal_petition["speaker"] == "Massena"
        assert J.last_audience_turn(world.marshals["Massena"]) == 4 + J.AUDIENCE_COOLDOWN_TURNS

    def test_another_man_is_not_held_by_his_clock(self, world):
        world.current_turn = 4
        self._fire(world, "Massena", "Davout")
        self._answer_and_cool(world, "Massena")
        world.current_turn = 5
        self._fire(world, "Lannes", "Soult")
        assert world.pending_marshal_petition is not None
        assert world.pending_marshal_petition["speaker"] == "Lannes"

    def test_the_damage_going_permanent_never_waits(self, world):
        world.current_turn = 4
        self._fire(world, "Massena", "Davout")
        self._answer_and_cool(world, "Massena")
        world.current_turn = 6
        J._set_escalation_level(world.marshals["Massena"], "Soult",
                                J.ESCALATION_PERMANENT_LEVEL)
        self._fire(world, "Massena", "Soult")
        petition = world.pending_marshal_petition
        assert petition is not None
        assert int(petition["context"]["escalation_level"]) >= J.ESCALATION_PERMANENT_LEVEL

    def test_a_card_that_replaces_his_own_stale_one_never_waits(self, world):
        """F6: a card still standing from before a by-action settlement is
        replaced by the re-fire's card. The replacement is the SAME
        audience re-worded — if it waited, neither card would stand."""
        world.current_turn = 4
        davout, ney = world.marshals["Davout"], world.marshals["Ney"]
        J.apply_jealousy(world, davout, ney, delta=2, threshold=1, events=[])
        stale = world.pending_marshal_petition
        assert stale and stale["context"]["marshal"] == "Davout"
        J.clear_jealousy(world, davout, resolved_by_action=True, where="Tyrol")
        J.apply_jealousy(world, davout, ney, delta=2, threshold=1, events=[])
        card = world.pending_marshal_petition
        assert card is not None and card is not stale
        assert str(card["body"]).startswith("Settled once at Tyrol"), card["body"]

    def test_lever_down_he_asks_again_at_once(self, world, monkeypatch):
        monkeypatch.setattr(J, "THE_AUDIENCE_WAITS", False)
        world.current_turn = 4
        self._fire(world, "Massena", "Davout")
        self._answer_and_cool(world, "Massena")
        world.current_turn = 7
        self._fire(world, "Massena", "Soult")
        assert world.pending_marshal_petition is not None
        assert "__audience__" not in world.marshals["Massena"].jealousy_history

    def test_the_clock_survives_the_save(self, world):
        world.current_turn = 4
        self._fire(world, "Massena", "Davout")
        world2 = WorldState.from_dict(world.to_dict())
        assert J.last_audience_turn(world2.marshals["Massena"]) == 4
        world2.current_turn = 6
        assert J.audience_wait(world2, world2.marshals["Massena"], 0) == \
            J.AUDIENCE_COOLDOWN_TURNS - 2

    def test_an_enemy_marshal_keeps_no_clock(self, world):
        world.current_turn = 4
        self._fire(world, "Mack", "ArchdukeCharles")
        assert "__audience__" not in world.marshals["Mack"].jealousy_history
        assert world.pending_marshal_petition is None
