"""Pre-Deploy S14f — the re-measure's rows (DD-B, October 24, 2026).

The pins of `docs/BUG_FIXES.md` §S14E: one class per row (`TestS14E<n>`),
one per sibling the sweep found (`TestS14EX<n>`), and the rulings' own
classes (`TestS14ED2`, `TestS14ED3`, `TestS14ED4`). Part 1 (October 24,
2026) holds the P1 S14E-1 with S14E-D1, the P2s S14E-2 … 15, the rulings
D2 … D4 and the part's siblings; part 2 adds the P3s S14E-16 … 35. Each
section below carries its row's record: the cause, the sighting, the fix.
Merged from the part's row files (`tests/test_s14f_row<NN>.py`) by the
landing's merge script; the sections' helpers are prefixed `_r<n>_` so the
file stays one module (the hook's `--dist loadgroup` keeps it on one worker).
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import contextlib
import io
import json
import re

import pytest


# ══════════════════════════════════════════════════════════════════════════
# row01
# ══════════════════════════════════════════════════════════════════════════
# S14E-1 (the re-measure's P1) with its ruling S14E-D1 — RE-RULED by the user
# on October 25, 2026: the aggressive deed stays his, with the muster, the log
# line and teeth; every other personality asks (the record below is part 1's).
# 
# Pre-Deploy S14f part 1 (October 24, 2026; `docs/BUG_FIXES.md` §S14E,
# `docs/DESIGN_REFINEMENT.md` §S14E D1). The sea road's P1 (turn 4, action
# 72): "Massena, march to Milan" — a plain move home with an armistice to
# Austria in transit — ran through Austrian-held Tyrol; Archduke John barred
# the road and `_handle_first_step_blocked`'s aggressive arm fought him
# unasked at a raw ratio of 0.7 or better (`_strategic_execution`: no
# objection, no muster gate, no quote), drawing five corps, +8 alarm and
# 1,691 men lost on the march. Reproduced on the shipped 1805 board: Massena
# (aggressive, 42,000) at Bohemia, Archduke John (20,000) at Tyrol, the road
# to Milan Bohemia → Tyrol → Milan — before the fix the reply read
# "Massena: 'Archduke John bars the way!' Engaging!" over a fought battle
# (`requires_input` None, `first_step_combat` True).
# 
# The fix: the aggressive marshal's TYPED order asks on its blocked first
# step like every other personality — one modal (`interrupt_type: contact`),
# his temperament in his line ("Archduke John bars the way at Tyrol, Sire —
# I can take him."), Berthier's muster beside it, nothing fought; `attack`
# runs today's attack, `go_around` re-plots the lawful road. Kept as today
# (`_typed_first_step_asks`): a delegation-inferred order's own gate, a
# PURSUE that finds its quarry on the first step, a march whose arrival tail
# names the man met, and the AI's side. A standing order's later contacts
# keep today's rule (the per-turn processor is untouched).
# 
# S14E-X1 (the sweep): the cautious / balanced ask named no muster while the
# bad-odds ask beside it did — the one builder now carries Berthier's note.
# S14E-X2: when nobody would answer the guns the ask stood on the marshal's
# word alone; Berthier now gives the solo figure against the fog-banded foe.

_R1_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                / "assets" / "maps" / "europe_1805.json")


def _r1_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r1_boot():
    from backend.models.world_state import WorldState
    with _r1_quiet():
        return WorldState.from_scenario(str(_R1_SCENARIO))


@pytest.fixture
def _r1_board(_r1_boot):
    """The shipped 1805 board, Massena moved to Bohemia so his road home to
    Milan runs through Austrian-held Tyrol, where Archduke John stands."""
    from backend.commands.executor import CommandExecutor
    from backend.models.world_state import WorldState
    world = WorldState.from_dict(json.loads(json.dumps(_r1_boot.to_dict(), default=str)))
    massena = world.get_marshal("Massena")
    john = world.get_marshal("ArchdukeJohn")
    assert massena.personality == "aggressive" and john.location == "Tyrol"
    massena.location = "Bohemia"
    world.calculate_visibility()
    executor = CommandExecutor()
    return world, {"world": world}, executor, massena, john


def _r1_march(executor, game_state, marshal: str, target: str, *, strategic_type="MOVE_TO",
              action="move", raw=None):
    with _r1_quiet():
        return executor.execute({
            "command": {"raw_input": raw or f"{marshal}, {action} {target}",
                        "marshal": marshal, "action": action, "target": target},
            "is_strategic": True, "strategic_type": strategic_type,
        }, game_state)


class TestS14E1:
    """S14E-D1 as RE-RULED by the user (October 25, 2026 — "making him ask is
    removing fun friction"): the aggressive marshal's typed march that meets
    an enemy on its first step at favourable odds FIGHTS, as before part 1 —
    the deed stays his — but no longer in silence: the muster block rides
    the battle's head, the reply and the campaign log name the deed as his,
    and it has teeth (a laurel of initiative and +2 trust on a win, −5 trust
    on a loss, nothing on a stalemate). Every other personality keeps the ask
    with Berthier's muster (S14E-X1); the bad-odds ask is untouched."""

    def test_the_typed_march_fights_at_favourable_odds_and_names_the_deed(self, _r1_board):
        world, gs, executor, massena, john = _r1_board
        assert massena.strength / john.strength >= 0.7
        trust_before = int(massena.trust)
        glory_before = len(massena.glory_events)
        result = _r1_march(executor, gs, "Massena", "Milan")
        assert result.get("success") is True
        assert result.get("requires_input") is not True
        assert result.get("first_step_combat") is True
        msg = result.get("message", "")
        assert "Archduke John bars the way at Tyrol, Sire — I can take him." in msg
        assert "Massena engages him on the road, on his own judgment." in msg
        # the muster block rides the battle's head (the answered contact's idiom)
        assert "MUSTER" in msg   # the block rides the battle's head
        # a battle was fought — somebody bled
        assert john.strength < 20000 or massena.strength < 42000
        # the deed's record and its teeth
        rec = result.get("first_step_initiative") or {}
        assert rec.get("marshal") == "Massena" and rec.get("enemy") == "ArchdukeJohn"
        assert rec.get("outcome") in ("won", "lost", "stalemate")
        if rec["outcome"] == "won":
            assert "the initiative was his and so is the laurel" in msg
            assert int(massena.trust) == min(100, trust_before + 2)
            assert len(massena.glory_events) >= glory_before + 1
        elif rec["outcome"] == "lost":
            assert "without your word and lost it — −5 trust" in msg
            assert int(massena.trust) == max(0, trust_before - 5)
        else:
            assert "nothing gained, nothing charged" in msg
            assert int(massena.trust) == trust_before

    def test_the_campaign_log_names_the_deed_as_his(self, _r1_board):
        world, gs, executor, massena, john = _r1_board
        _r1_march(executor, gs, "Massena", "Milan")
        battles = [e for e in world.event_log if e.get("type") == "battle" and e.get("attacker") == "Massena"]
        assert battles and battles[-1].get("initiative") is True
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner(battles[-1], world)
        assert "on his own judgment, on the road" in line

    def test_the_teeth_both_ways(self, _r1_board):
        """The outcomes drive the teeth: a win takes the laurel and +2 trust,
        a loss −5 trust, a stalemate nothing — read off the deed helper with
        a staged battle result, the V2b defiance magnitudes."""
        world, gs, executor, massena, john = _r1_board
        se = executor._strategic
        def run(victor, awarded):
            massena.trust.set(60)
            world._initiative_laurel_awarded = awarded   # what the chokepoint left
            result = {"events": [{"type": "battle", "victor": victor}], "message": "x"}
            deed = se._initiative_deed(massena, john, "Tyrol", world, result, "x",
                                       len(world.event_log), player=True)
            return deed, int(massena.trust), int(deed["record"]["glory"])
        deed, trust, laurels = run("Massena", 1)
        assert deed["record"]["outcome"] == "won" and trust == 62 and laurels == 1
        assert "+1 glory, +2 trust" in deed["message"]
        deed, trust, laurels = run("ArchdukeJohn", 0)
        assert deed["record"]["outcome"] == "lost" and trust == 55 and laurels == 0
        deed, trust, laurels = run("", 0)
        assert deed["record"]["outcome"] == "stalemate" and trust == 60 and laurels == 0
        assert getattr(world, "_initiative_laurel_awarded", 0) == 0   # read once, cleared
        # the AI's deed: the old line, no teeth
        ai = se._initiative_deed(john, massena, "Bohemia", world,
                                 {"events": [{"type": "battle", "victor": "ArchdukeJohn"}]},
                                 "x", len(world.event_log), player=False)
        assert ai["record"] is None and "Engaging!" in ai["message"]

    def test_the_laurel_goes_through_the_one_chokepoint(self, _r1_board):
        """FA-S16-D4: every accrual is inside `record_battle_glory`; the deed
        ARMS the laurel and the chokepoint awards it after its own gates —
        one point beyond the battle's, none for a skirmish, none for a
        sovereign, none when the armed man did not win."""
        world, gs, executor, massena, john = _r1_board
        from backend.game_logic import jealousy
        def battle(attacker, armed, won=True, atk_cas=3000, def_cas=9000):
            if armed:
                jealousy.arm_initiative_laurel(world, attacker)
            n = len(attacker.glory_events)
            jealousy.record_battle_glory(world, attacker, john, attacker_won=won, defender_won=not won,
                                         attacker_casualties=atk_cas, defender_casualties=def_cas,
                                         conquered=False, pre_attacker_strength=42000,
                                         pre_defender_strength=20000)
            pts = sum(e["points"] for e in attacker.glory_events[n:])
            return pts, jealousy.take_initiative_laurel_awarded(world)
        plain, _ = battle(massena, armed=False)
        armed, awarded = battle(massena, armed=True)
        assert awarded == 1 and armed == plain + 1
        # a skirmish is not a laurel: the floor governs the deed's point too
        _, awarded = battle(massena, armed=True, atk_cas=10, def_cas=20)
        assert awarded == 0
        # the armed man lost: no laurel
        _, awarded = battle(massena, armed=True, won=False, atk_cas=9000, def_cas=3000)
        assert awarded == 0
        # a sovereign accrues none
        napoleon = world.get_marshal("Napoleon")
        _, awarded = battle(napoleon, armed=True)
        assert awarded == 0

    def test_the_bad_odds_ask_is_untouched(self, _r1_board):
        world, gs, executor, massena, john = _r1_board
        john.strength = 70000   # 42,000 against 70,000: 0.6, below the bar
        world.calculate_visibility()
        result = _r1_march(executor, gs, "Massena", "Milan")
        assert result.get("requires_input") is True
        assert massena.pending_interrupt["interrupt_type"] == "contact_bad_odds"
        assert "Odds unfavorable" in result["message"]
        assert john.strength == 70000

    def test_the_cautious_march_still_asks_and_its_answers_hold(self, _r1_board):
        """The cautious arm asks with Berthier's muster (S14E-X1) and its
        answers hold — driven at the seam, since the cautious planner routes
        round a seen corps and never meets him on the open board."""
        world, gs, executor, massena, john = _r1_board
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.models.marshal import StrategicOrder
        davout = world.get_marshal("Davout")
        assert davout.personality == "cautious"
        davout.location = "Bohemia"
        world.calculate_visibility()
        davout.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Milan", target_type="region", started_turn=1,
            original_command="Davout, march to Milan", path=["Tyrol", "Milan"])
        with _r1_quiet():
            result = executor._strategic._handle_first_step_blocked(
                davout, [john], "Tyrol", world, gs)
        assert result.get("requires_input") is True
        assert davout.pending_interrupt["interrupt_type"] == "contact"
        assert davout.pending_interrupt["options"] == ["attack", "go_around", "hold_position", "cancel_order"]
        assert "Enemy at Tyrol. How shall I proceed, Sire?" in result["message"]
        assert "Berthier adds:" in result["message"]
        assert john.strength == 20000 and davout.location == "Bohemia"
        with _r1_quiet():
            answer = StrategicOrderProcessor(executor).handle_response(
                "Davout", "blocked_path", "go_around", world, gs)
        assert answer.get("success") is True and john.strength == 20000
        order = davout.strategic_order
        assert order is not None and "Tyrol" not in (order.path or []) and order.path[-1] == "Milan"

    def test_a_pursuit_that_finds_its_quarry_fights_too(self, _r1_board):
        world, gs, executor, massena, john = _r1_board
        result = _r1_march(executor, gs, "Massena", "ArchdukeJohn", strategic_type="PURSUE",
                           action="attack", raw="Massena, pursue Archduke John")
        assert result.get("requires_input") is not True
        assert john.strength < 20000 or massena.location == "Tyrol"

    def test_the_inferred_order_keeps_its_own_gate(self, _r1_board, monkeypatch):
        """CR-5 §6.3c: a delegation-inferred order's favourable read fights
        at once; its bad read routes through the one-modal bad-odds confirm."""
        world, gs, executor, massena, john = _r1_board
        from backend.commands import objection_v2
        from backend.models.marshal import StrategicOrder
        monkeypatch.setattr(objection_v2, "inferred_attack_favorable", lambda *a, **k: True)
        massena.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Milan", target_type="region", started_turn=1,
            original_command="the army to Milan", path=["Tyrol", "Milan"])
        massena.strategic_order.delegation_inferred = True
        with _r1_quiet():
            result = executor._strategic._handle_first_step_blocked(
                massena, [john], "Tyrol", world, gs)
        assert result is not None and result.get("requires_input") is not True
        assert result.get("first_step_combat") is True

    def test_the_ai_side_keeps_todays_rule_without_teeth(self, _r1_board):
        world, gs, executor, massena, john = _r1_board
        from backend.models.marshal import StrategicOrder
        john.personality = "aggressive"
        john.strength = 60000
        trust_before = int(john.trust)
        john.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Vienna", target_type="region", started_turn=1,
            original_command="John to Vienna", path=["Bohemia", "Vienna"])
        with _r1_quiet():
            result = executor._strategic._handle_first_step_blocked(
                john, [massena], "Bohemia", world, gs)
        assert result is not None and result.get("requires_input") is not True
        assert john.pending_interrupt is None
        assert result.get("first_step_initiative") is None
        assert int(john.trust) == trust_before

    def test_the_quote_says_what_the_executor_does(self, _r1_board):
        world, gs, executor, massena, john = _r1_board
        from backend.commands.order_quotes import march_quote
        q = march_quote(world, massena, "Milan")
        assert q["ok"] and "Archduke John blocks the road at Tyrol" in q["contact"]
        assert "attacks him at once if the numbers favour him, else asks your orders" in q["contact"]


class TestS14EX1:
    """The cautious / balanced first-step ask carries Berthier's muster."""

    def test_the_cautious_ask_names_the_muster(self):
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import StrategicOrder
        from backend.models.world_state import WorldState
        world = WorldState(player_nation="France")
        gs = {"world": world}
        davout = world.get_marshal("Davout")
        assert davout.personality == "cautious"
        davout.location = "Paris"
        davout.strength = 30000
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strength = 24000
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"
        wellington.strength = 40000
        world.calculate_visibility()
        davout.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Rhineland", target_type="region", started_turn=1,
            original_command="Davout, march to Rhineland", path=["Belgium", "Rhineland"])
        executor = CommandExecutor()
        with _r1_quiet():
            result = executor._strategic._handle_first_step_blocked(
                davout, [wellington], "Belgium", world, gs)
        assert result["requires_input"] is True
        assert "Enemy at Belgium. How shall I proceed, Sire?" in result["message"]
        assert "Berthier adds:" in result["message"] and "would answer the guns" in result["message"]
        assert davout.pending_interrupt["interrupt_type"] == "contact"


class TestS14EX2:
    """Nobody would answer the guns: the ask carries the solo figure (the
    bad-odds ask, since the favourable aggressive arm fights — D1 re-ruled)."""

    def test_the_solo_figure_when_nobody_joins(self, _r1_board):
        world, gs, executor, massena, john = _r1_board
        john.strength = 70000
        world.calculate_visibility()
        result = _r1_march(executor, gs, "Massena", "Milan")
        assert result.get("requires_input") is True
        note = result["message"].split("Berthier adds:")[1]
        assert "Massena 42,000 against Archduke John" in note
        assert "no other corps stands within reach" in note

    def test_the_source_note_is_still_empty_for_the_three_pins(self, _r1_board):
        world, gs, executor, massena, john = _r1_board
        assert executor._combat._bad_odds_muster_note(massena, john, world) == ""
        assert executor._combat._contact_muster_note(massena, john, world).startswith(" Berthier adds:")
        # the AI's marshal gets nothing (the note is copy on the player's modal)
        assert executor._combat._contact_muster_note(john, massena, world) == ""



# ══════════════════════════════════════════════════════════════════════════
# row02
# ══════════════════════════════════════════════════════════════════════════
# S14E-2 — the muster never prices the campaign pay a corps on allied soil draws.
# 
# Cause: `WorldState.calculate_turn_upkeep` bills 12g per 1,000 men (EAD-1) for
# each corps standing outside its court's homeland on allied or neutral soil,
# but no muster surface quotes it - the supply note, the materiel note and the
# joiner rows (DDB-13/14) leave the bill that follows from where the corps
# will stand unsaid, and the what-if desk shares the gap.
# 
# Fix: the EAD-1 predicate is factored into ONE pair of helpers on WorldState
# (`campaign_pay_homeland`, `campaign_pay_at`) that `calculate_turn_upkeep` and
# the muster both read; `_build_muster_preview` adds a `campaign_note` beside
# the materiel note (rendered by `_format_muster_lines`, so the what-if desk
# prints the same line).

_R2_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client"
                / "project-sovereign" / "assets" / "maps" / "europe_1805.json")
_R2_MINUS = "−"


@pytest.fixture(scope="module")
def _r2_boot():
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(_R2_SCENARIO))


@pytest.fixture
def _r2_world(_r2_boot):
    from backend.models.world_state import WorldState
    w = WorldState.from_dict(json.loads(json.dumps(_r2_boot.to_dict(), default=str)))
    w.get_marshal("Mack").strength = 52000
    w.calculate_visibility()
    return w


def _r2_combat():
    from backend.commands.executor import CommandExecutor
    with contextlib.redirect_stdout(io.StringIO()):
        return CommandExecutor()._combat


def _r2_muster(w, lead="Davout", foe="Mack") -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return _r2_combat()._build_muster_preview(
            w.get_marshal(lead), w.get_marshal(foe), w, {"world": w})


def _r2_figure(note: str) -> int:
    m = re.search(_R2_MINUS + r"([\d,]+)g", note)
    assert m, note
    return int(m.group(1).replace(",", ""))


def _r2_stand_there(w, pv, region="Swabia") -> None:
    """Put the lead and every joiner who marches to the guns where the
    muster says they will stand - the board the next upkeep bill reads."""
    lead = pv["attacker"]["name"]
    w.get_marshal(lead).location = region
    for row in pv["rows"]:
        if row["will_join"] and row.get("stands_after"):
            w.get_marshal(row["marshal"]).location = region


class TestS14E2:
    def test_a_muster_on_allied_soil_prints_the_campaign_pay_it_will_add(self, _r2_world):
        w = _r2_world
        assert w.get_region("Swabia").controller == "Bavaria"
        assert w.get_diplomatic_state("France", "Bavaria") == "ALLIANCE"
        pv = _r2_muster(w)
        note = pv["campaign_note"]
        assert note.startswith("Swabia is Bavaria's soil — the corps standing there are "
                               "fed by contract, about " + _R2_MINUS)
        assert note.endswith("g more a turn.")
        # Hand figure: (strength // 1000) * 12 for the lead and each corps
        # that marches to the guns - Davout 26, Ney 24, Lannes 18, Murat 22,
        # Napoleon 10 (thousand) = 100 * 12.
        assert _r2_figure(note) == 1200
        assert pv["campaign_pay_more"] == 1200

    def test_shown_equals_applied_against_the_upkeep_bill(self, _r2_world):
        w = _r2_world
        pv = _r2_muster(w)
        before = w.calculate_turn_upkeep("France")["campaign_pay"]
        _r2_stand_there(w, pv)
        after = w.calculate_turn_upkeep("France")["campaign_pay"]
        assert after - before == _r2_figure(pv["campaign_note"]) > 0

    def test_the_rendered_muster_carries_the_line_beside_the_materiel_note(self, _r2_world):
        w = _r2_world
        pv = _r2_muster(w)
        text = _r2_combat()._format_muster_lines(pv)
        lines = text.split("\n")
        i = next(k for k, ln in enumerate(lines) if ln.strip().startswith("Materiel:"))
        assert lines[i + 1].strip() == pv["campaign_note"]

    def test_the_what_if_desk_prints_the_same_line(self, _r2_world):
        from backend.ai.question_desk import _answer_what_if
        w = _r2_world
        pv = _r2_muster(w)
        with contextlib.redirect_stdout(io.StringIO()):
            answer = _answer_what_if(w, "France", "Mack", "Davout")
        assert answer and pv["campaign_note"] in answer

    def test_the_province_what_if_prints_it_too(self, _r2_world):
        """The desk's second road ("what are Davout's odds against Swabia")
        renders the same block through `_muster_lines`."""
        from backend.ai.question_desk import _answer_what_if_region, _muster_lines
        w = _r2_world
        pv = _r2_muster(w)
        with contextlib.redirect_stdout(io.StringIO()):
            text = _muster_lines(w, w.get_marshal("Davout"), w.get_marshal("Mack"))
            answer = _answer_what_if_region(w, "France", "Swabia", "Davout")
        assert pv["campaign_note"] in text
        assert answer and pv["campaign_note"] in answer

    @pytest.mark.parametrize("holder", ["France", "Austria"])
    def test_own_soil_and_enemy_soil_carry_no_note(self, _r2_world, holder):
        w = _r2_world
        w.get_region("Swabia").controller = holder
        pv = _r2_muster(w)
        assert "campaign_note" not in pv
        assert "campaign" not in _r2_combat()._format_muster_lines(pv).lower()

    def test_a_vassals_soil_carries_no_note(self, _r2_world):
        w = _r2_world
        w.diplomatic_states[w._make_diplo_key("France", "Bavaria")] = "VASSAL"
        assert "campaign_note" not in _r2_muster(w)

    def test_a_neutral_courts_soil_carries_the_note(self, _r2_world):
        w = _r2_world
        w.diplomatic_states[w._make_diplo_key("France", "Bavaria")] = "PEACE"
        pv = _r2_muster(w)
        # The field on peace soil is closed to every joiner (`neutral_soil`),
        # so only the lead's own 26,000 would be fed by contract there.
        assert all(not r["will_join"] for r in pv["rows"])
        assert _r2_figure(pv["campaign_note"]) == 312

    def test_corps_already_standing_there_add_nothing(self, _r2_world):
        w = _r2_world
        for name in ("Davout", "Ney", "Lannes", "Murat", "Napoleon"):
            w.get_marshal(name).location = "Swabia"
        pv = _r2_muster(w)
        assert "campaign_note" not in pv

    def test_a_court_that_is_at_peace_with_everyone_pays_nothing(self, _r2_world):
        w = _r2_world
        for key in list(w.diplomatic_states):
            if w.diplomatic_states[key] == "WAR":
                w.diplomatic_states[key] = "PEACE"
        assert w.campaign_pay_homeland("France") is None
        assert w.calculate_turn_upkeep("France")["campaign_pay"] == 0

    def test_the_legacy_world_prices_nothing(self):
        from backend.models.world_state import WorldState
        w = WorldState(player_nation="France")
        assert w.campaign_pay_homeland("France") is None

    def test_the_bill_and_the_quote_read_one_predicate(self, _r2_world):
        """Parity: every corps of ours, on every kind of soil, is billed by
        `calculate_turn_upkeep` exactly what `campaign_pay_at` says."""
        w = _r2_world
        homeland = w.campaign_pay_homeland("France")
        assert homeland is not None
        for region in ("Swabia", "Lorraine", "Munich", "Carniola", "Franconia",
                       "Rhineland", "Tyrol"):
            for m in w.marshals.values():
                if m.nation == "France":
                    m.location = region
            expect = 0
            for m in w.marshals.values():
                if m.nation == "France" and m.strength > 0:
                    info = w.campaign_pay_at("France", m.location, m.strength, homeland)
                    expect += info["pay"] if info else 0
            assert w.calculate_turn_upkeep("France")["campaign_pay"] == expect, region

    def test_every_court_is_billed_by_the_one_predicate(self, _r2_world):
        """GR5: the rule is every court's. Austria on Bavarian soil pays as
        France does; the sum the bill returns is the predicate's own."""
        w = _r2_world
        for nation in sorted({m.nation for m in w.marshals.values()}):
            for m in w.marshals.values():
                if m.nation == nation and nation != "France":
                    m.location = "Munich"
            homeland = w.campaign_pay_homeland(nation)
            expect = 0
            for m in w.marshals.values():
                if m.nation == nation and m.strength > 0 and homeland is not None:
                    info = w.campaign_pay_at(nation, m.location, m.strength, homeland)
                    expect += info["pay"] if info else 0
            billed = w.calculate_turn_upkeep(nation)
            assert billed["campaign_pay"] == expect, nation
            assert sum(r["pay"] for r in billed["campaign_ground"]) == expect, nation

    def test_no_second_formula_for_the_pay(self):
        """Source census: the bill and the quote both go through
        `campaign_pay_at`; neither carries its own rate or its own soil test."""
        import inspect
        from backend.commands.combat_executor import CombatExecutor
        from backend.models.world_state import WorldState
        bill = inspect.getsource(WorldState.calculate_turn_upkeep)
        quote = inspect.getsource(CombatExecutor._campaign_pay_quote)
        for src in (bill, quote):
            assert "campaign_pay_at(" in src
            assert "CAMPAIGN_PAY_RATE" not in src
            assert '"WAR", "VASSAL"' not in src
        pred = inspect.getsource(WorldState.campaign_pay_at)
        assert "CAMPAIGN_PAY_RATE" in pred and '"WAR", "VASSAL"' in pred

    def test_upkeep_names_the_ground_with_the_same_keys(self, _r2_world):
        w = _r2_world
        row = w.calculate_turn_upkeep("France")["campaign_ground"][0]
        assert list(row) == ["marshal", "region", "holder", "pay"]
        assert row["holder"] == "Bavaria" and row["region"] == "Franconia"

    def test_the_bankruptcy_mercy_halves_the_quote_as_it_halves_the_bill(self, _r2_world):
        w = _r2_world
        w.nation_bankruptcy_turns["France"] = 1
        pv = _r2_muster(w)
        assert _r2_figure(pv["campaign_note"]) == 600


# ══════════════════════════════════════════════════════════════════════════
# row03
# ══════════════════════════════════════════════════════════════════════════
# S14E-3 - the concessions wizard (the `terms_guidance` dialogue) has a way out.
# 
# Pre-Deploy S14f part 1 (October 24, 2026; defect row S14E-3 in
# `docs/BUG_FIXES.md`). The re-measure's conquest road: Esc and the drawn X on
# `proposal_confirm_popup.gd` act only when some option's action is in
# `_SAFE_EXIT_ACTIONS` (UXR3-F5), and the first four steps of the wizard
# (territory / province / gold / Action Points) carried only forward answers -
# Esc dead, no X, no Back; only the final confirm had Reconsider. The player
# could leave only by picking an answer that sounded like paying Austria.
# 
# The fix, built in `DiplomaticExecutor._process_dialogue_choice`: every step of
# a guided wizard (`terms_guidance`, and its sibling the ultimatum demand wizard)
# is finished with a "Never mind" option (action `reconsider`, which pops the
# dialogue and spends nothing - the terms live only in the dialogue's context)
# and, from the second step on, a "Back" option (action `step_back`) that
# restores the step the answer was given on, exactly as it was served, with the
# answer undone. The earlier steps are kept as a stack in the step's own
# context, so a save mid-wizard keeps its Back.
# 
# Sibling pins (letter C): `TestS14EX3` the ultimatum demand wizard (blocking,
# five steps, the same missing exit), `TestS14EX4` the small confirms whose
# "keep what I had" option was not a safe exit on the client.

REPO = Path(__file__).resolve().parents[1]
POPUP_GD = REPO / "godot-client" / "project-sovereign" / "scripts" / "proposal_confirm_popup.gd"
SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json")


# ══════════════════════════════════════════════════════════════════════════
# The fixture world - the walk helpers (the idiom of test_terms_guidance.py)
# ══════════════════════════════════════════════════════════════════════════

def _r3_world(score: int = -20):
    """The legacy fixture world with France at war with Austria and losing."""
    from backend.models.world_state import WorldState
    w = WorldState()
    key = w._make_diplo_key("France", "Austria")
    w.nation_relations[key] = -30
    w.diplomatic_states[key] = "WAR"
    if not hasattr(w, "war_scores"):
        w.war_scores = {}
    first = key.split("|")[0]
    w.war_scores[key] = score if first == "France" else -score
    return w


def _r3_stage_draft(w, target: str = "Austria", proposal_type: str = "peace"):
    """The proposal the wizard is entered from (its 'Adjust terms' option)."""
    w.dialogue_manager.replace({
        "type": "proposal_confirm",
        "target_nation": target,
        "talleyrand_text": "Test proposal.",
        "options": [
            {"label": "Send as suggested", "description": "Send.", "action": "execute_proposal",
             "terms": {"type": proposal_type, "proposal_type": proposal_type,
                       "proposer_nation": "France", "target_nation": target,
                       "sweeteners": [], "demands": [], "clauses": []}},
            {"label": "Adjust terms", "description": "Build the offer step by step.",
             "action": "adjust_terms"},
            {"label": "Reconsider", "description": "Let me think.", "action": "reconsider"},
        ],
        "context": {"proposal_type": proposal_type},
        "turn_created": int(w.current_turn),
        "blocking": False,
    })


def _r3_rig():
    from backend.commands.executor import CommandExecutor
    w = _r3_world()
    ex = CommandExecutor()
    gs = {"world": w}
    _r3_stage_draft(w)
    return w, ex, gs


def _r3_click(rig, action: str) -> dict:
    """Answer the live dialogue the way the client does: by the 1-based index
    of the option that carries `action`."""
    w, ex, gs = rig
    current = w.pending_diplomatic_dialogue
    assert current is not None, f"no dialogue standing when {action!r} was clicked"
    actions = [o.get("action") for o in current.get("options", [])]
    assert action in actions, f"{action!r} not offered on {current.get('type')!r}: {actions}"
    return ex.handle_diplomatic_dialogue_response(actions.index(action) + 1, gs)


def _r3_esc(dialogue) -> str:
    """What the client's Esc (and its drawn X) would send for this dialogue:
    `proposal_confirm_popup.gd::_find_safe_exit_action` - the first AVAILABLE
    option whose action is in `_SAFE_EXIT_ACTIONS` - read off the .gd source.
    "" means Esc does nothing and the X is hidden."""
    gd = POPUP_GD.read_text(encoding="utf-8")
    body = re.search(r"const _SAFE_EXIT_ACTIONS = \[(.*?)\]", gd, re.S).group(1)
    safe = set(re.findall(r'"([a-z_]+)"', body))
    for option in (dialogue or {}).get("options", []):
        if isinstance(option, dict) and option.get("available", True) and option.get("action") in safe:
            return str(option["action"])
    return ""


def _r3_actions(rig_or_world) -> list:
    w = rig_or_world[0] if isinstance(rig_or_world, tuple) else rig_or_world
    cur = w.pending_diplomatic_dialogue
    return [o.get("action") for o in (cur or {}).get("options", [])]


# the five steps of the concessions wizard, as the clicks that reach them
_R3_STEPS = {
    "territory": ["adjust_terms"],
    "province": ["adjust_terms", "territory_yes"],
    "gold": ["adjust_terms", "territory_no_gold"],
    "ap": ["adjust_terms", "territory_no_gold", "skip_gold"],
    "confirm": ["adjust_terms", "territory_no_gold", "skip_gold", "skip_ap"],
}


def _r3_walk(path):
    rig = _r3_rig()
    for action in path:
        out = _r3_click(rig, action)
        assert out.get("success"), (action, out)
    return rig


def _r3_ledger(w) -> dict:
    """What a wizard must never touch: the purse, the points, the treaties, the
    court's temper, and anything in transit."""
    return {
        "dp": w.diplomatic_points,
        "gold": dict(w.nation_gold),
        "states": dict(w.diplomatic_states),
        "relations": dict(w.nation_relations),
        "in_transit": w.proposal_in_transit,
        "turn": w.current_turn,
    }


# ══════════════════════════════════════════════════════════════════════════
# S14E-3 - the concessions wizard
# ══════════════════════════════════════════════════════════════════════════

class TestS14E3:
    # ── reproduction: the steps offer an exit ────────────────────────────

    @pytest.mark.parametrize("step", list(_R3_STEPS))
    def test_every_step_of_the_wizard_offers_a_way_out(self, step):
        rig = _r3_walk(_R3_STEPS[step])
        cur = rig[0].pending_diplomatic_dialogue
        assert cur["type"] == "terms_guidance"
        assert "reconsider" in _r3_actions(rig), (
            f"the {step} step offers no safe exit, so Esc is dead and the X is hidden: "
            f"{_r3_actions(rig)}")

    @pytest.mark.parametrize("step", list(_R3_STEPS))
    def test_esc_and_the_x_find_it_on_every_step(self, step):
        """The client's Esc / X derive their action from the options: on every
        step it is `reconsider` (the pre-fix territory/province/gold/AP steps
        answered "" - Esc dead, X hidden)."""
        rig = _r3_walk(_R3_STEPS[step])
        assert _r3_esc(rig[0].pending_diplomatic_dialogue) == "reconsider"
        # and never Back: the corridor's way out is the door, not the last room
        assert _r3_esc(rig[0].pending_diplomatic_dialogue) != "step_back"

    @pytest.mark.parametrize("step", ["territory", "province", "gold", "ap"])
    def test_the_way_out_is_named_never_mind(self, step):
        rig = _r3_walk(_R3_STEPS[step])
        exits = [o for o in rig[0].pending_diplomatic_dialogue["options"]
                 if o.get("action") == "reconsider"]
        assert [o["label"] for o in exits] == ["Never mind"]
        assert exits[0].get("description"), "the button says what it does"

    def test_the_exhausted_province_step_offers_it_too(self):
        # every non-capital province but Lyon gone: one candidate, then none
        rig = _r3_rig()
        w = rig[0]
        for name, region in w.regions.items():
            if region.controller == "France" and name not in ("Paris", "Lyon"):
                region.controller = "Austria"
        _r3_click(rig, "adjust_terms")
        _r3_click(rig, "territory_yes")
        out = _r3_click(rig, "skip_region")
        assert "no more" in out["message"].lower()
        assert "reconsider" in _r3_actions(rig)
        assert "step_back" in _r3_actions(rig)

    def test_the_final_confirm_keeps_its_own_reconsider(self):
        rig = _r3_walk(_R3_STEPS["confirm"])
        options = rig[0].pending_diplomatic_dialogue["options"]
        assert [o["label"] for o in options if o["action"] == "reconsider"] == ["Reconsider"]
        assert sum(1 for o in options if o["action"] == "reconsider") == 1
        assert "execute_proposal" in _r3_actions(rig) and "adjust_terms" in _r3_actions(rig)

    def test_the_answers_keep_their_numbers(self):
        """The exits are appended: nothing the typed route and the existing
        pins count by index moves."""
        rig = _r3_walk(_R3_STEPS["gold"])
        assert _r3_actions(rig)[:4] == ["offer_gold", "more_gold", "less_gold", "skip_gold"]
        rig = _r3_walk(_R3_STEPS["province"])
        assert _r3_actions(rig)[:3] == ["offer_region", "skip_region", "enough_territory"]
        rig = _r3_walk(_R3_STEPS["territory"])
        assert _r3_actions(rig)[:3] == ["territory_yes", "territory_no_gold", "territory_no_ap"]
        rig = _r3_walk(_R3_STEPS["ap"])
        assert _r3_actions(rig)[:2] == ["offer_ap", "skip_ap"]

    # ── Never mind: nothing staged, nothing spent ────────────────────────

    @pytest.mark.parametrize("step", list(_R3_STEPS))
    def test_never_mind_at_each_step_leaves_nothing_behind(self, step):
        rig = _r3_walk(_R3_STEPS[step])
        w = rig[0]
        before = _r3_ledger(w)
        out = _r3_click(rig, "reconsider")
        assert out["success"], out
        assert "diplomatic_dialogue" not in out, "no further step is served"
        assert w.pending_diplomatic_dialogue is None
        assert w.dialogue_manager.peek() is None
        assert list(w.dialogue_manager.iter_queue()) == []
        assert _r3_ledger(w) == before, "nothing is spent, sent or moved"
        # no half-built terms anywhere in the saved world
        saved = json.dumps(w.to_dict(), default=str)
        for leftover in ("approved_sweeteners", "approved_regions", "ranked_candidates", "back_stack"):
            assert leftover not in saved, f"{leftover} survives Never mind at the {step} step"

    def test_never_mind_after_a_province_and_gold_were_agreed_drops_them(self):
        rig = _r3_walk(["adjust_terms", "territory_yes", "offer_region", "offer_gold"])
        w = rig[0]
        assert any(s["type"] == "gold_per_turn"
                   for s in w.pending_diplomatic_dialogue["context"]["approved_sweeteners"])
        before = _r3_ledger(w)
        _r3_click(rig, "reconsider")
        assert w.pending_diplomatic_dialogue is None
        assert _r3_ledger(w) == before
        assert "approved_sweeteners" not in json.dumps(w.to_dict(), default=str)

    # ── Back ─────────────────────────────────────────────────────────────

    def test_the_first_step_has_no_back_and_every_later_step_has_one(self):
        assert "step_back" not in _r3_actions(_r3_walk(_R3_STEPS["territory"]))
        for step in ("province", "gold", "ap", "confirm"):
            assert "step_back" in _r3_actions(_r3_walk(_R3_STEPS[step])), step

    def test_back_is_not_a_safe_exit_and_never_mind_stays_first_for_escape(self):
        rig = _r3_walk(_R3_STEPS["gold"])
        actions = _r3_actions(rig)
        assert actions.index("reconsider") != -1 and "back_out" not in actions
        labels = [o["label"] for o in rig[0].pending_diplomatic_dialogue["options"]]
        assert "Back" in labels and "Never mind" in labels

    def test_back_from_the_gold_step_returns_the_territory_step(self):
        # province agreed -> gold; Back is the province step, as it was served,
        # with the cession undone
        rig = _r3_walk(["adjust_terms", "territory_yes"])
        served = rig[0].pending_diplomatic_dialogue
        candidate_text = served["talleyrand_text"]
        _r3_click(rig, "offer_region")
        cur = rig[0].pending_diplomatic_dialogue
        assert "gold" in cur["talleyrand_text"].lower()
        assert cur["context"]["approved_regions"], "the cession was agreed"
        out = _r3_click(rig, "step_back")
        assert out["success"], out
        back = rig[0].pending_diplomatic_dialogue
        assert out["diplomatic_dialogue"] is back
        assert back["talleyrand_text"] == candidate_text
        assert back["context"]["approved_regions"] == []
        assert back["context"]["approved_sweeteners"] == []
        assert back["context"]["candidate_index"] == 0
        assert [o["action"] for o in back["options"]][:3] == ["offer_region", "skip_region", "enough_territory"]
        assert "reconsider" in _r3_actions(rig)
        # and the answer can be given differently
        out = _r3_click(rig, "enough_territory")
        assert "gold" in out["message"].lower()
        assert rig[0].pending_diplomatic_dialogue["context"]["approved_sweeteners"] == []

    def test_back_from_gold_after_declining_territory_returns_the_first_question(self):
        rig = _r3_walk(_R3_STEPS["gold"])
        out = _r3_click(rig, "step_back")
        assert "concessions" in out["message"].lower()
        assert _r3_actions(rig)[:3] == ["territory_yes", "territory_no_gold", "territory_no_ap"]
        assert "step_back" not in _r3_actions(rig), "the first step has nothing to return to"

    def test_back_from_the_ap_step_returns_gold_with_the_gold_undone(self):
        rig = _r3_walk(["adjust_terms", "territory_no_gold", "offer_gold"])
        assert any(s["type"] == "gold_per_turn"
                   for s in rig[0].pending_diplomatic_dialogue["context"]["approved_sweeteners"])
        _r3_click(rig, "step_back")
        back = rig[0].pending_diplomatic_dialogue
        assert [o["action"] for o in back["options"]][:4] == ["offer_gold", "more_gold", "less_gold", "skip_gold"]
        assert back["context"]["approved_sweeteners"] == []

    def test_back_from_the_confirm_returns_ap_with_the_ap_undone(self):
        rig = _r3_walk(["adjust_terms", "territory_no_gold", "skip_gold", "offer_ap"])
        assert [s["type"] for s in rig[0].pending_diplomatic_dialogue["context"]["approved_sweeteners"]] == ["ap_per_turn"]
        _r3_click(rig, "step_back")
        back = rig[0].pending_diplomatic_dialogue
        assert [o["action"] for o in back["options"]][:2] == ["offer_ap", "skip_ap"]
        assert back["context"]["approved_sweeteners"] == []
        assert back["context"]["guidance_state"] == "ap"

    def test_back_all_the_way_walks_every_step_in_reverse(self):
        rig = _r3_walk(["adjust_terms", "territory_yes", "offer_region", "offer_gold", "offer_ap"])
        seen = []
        for _ in range(8):
            if "step_back" not in _r3_actions(rig):
                break
            _r3_click(rig, "step_back")
            seen.append(rig[0].pending_diplomatic_dialogue["context"]["guidance_state"])
        assert seen == ["ap", "gold", "region_pick", "territory"], seen
        assert rig[0].pending_diplomatic_dialogue["context"]["approved_sweeteners"] == []

    def test_more_gold_is_the_same_step_so_back_leaves_the_gold_step(self):
        rig = _r3_walk(_R3_STEPS["gold"])
        first = rig[0].pending_diplomatic_dialogue["context"]["gold_amount"]
        _r3_click(rig, "more_gold")
        assert rig[0].pending_diplomatic_dialogue["context"]["gold_amount"] > first
        _r3_click(rig, "step_back")
        # the territory question, not the gold step at its old amount
        assert _r3_actions(rig)[:3] == ["territory_yes", "territory_no_gold", "territory_no_ap"]

    def test_skipping_a_province_can_be_stepped_back_over(self):
        rig = _r3_walk(["adjust_terms", "territory_yes"])
        first_text = rig[0].pending_diplomatic_dialogue["talleyrand_text"]
        _r3_click(rig, "skip_region")
        assert rig[0].pending_diplomatic_dialogue["context"]["candidate_index"] == 1
        _r3_click(rig, "step_back")
        back = rig[0].pending_diplomatic_dialogue
        assert back["talleyrand_text"] == first_text
        assert back["context"]["candidate_index"] == 0

    def test_start_over_clears_the_way_back(self):
        rig = _r3_walk(_R3_STEPS["confirm"])
        _r3_click(rig, "adjust_terms")        # "Start over"
        assert "step_back" not in _r3_actions(rig)
        assert rig[0].pending_diplomatic_dialogue["context"]["back_stack"] == []

    def test_back_costs_nothing_and_changes_no_ledger(self):
        rig = _r3_walk(["adjust_terms", "territory_yes", "offer_region", "offer_gold"])
        before = _r3_ledger(rig[0])
        _r3_click(rig, "step_back")
        _r3_click(rig, "step_back")
        assert _r3_ledger(rig[0]) == before

    def test_a_forged_back_on_the_first_step_is_refused_and_leaves_the_step(self):
        rig = _r3_walk(_R3_STEPS["territory"])
        w, ex, gs = rig
        cur = w.pending_diplomatic_dialogue
        forged = dict(cur)
        forged["options"] = list(cur["options"]) + [
            {"label": "Back", "description": "x", "action": "step_back"}]
        w.dialogue_manager.replace(forged)
        out = ex.handle_diplomatic_dialogue_response(len(forged["options"]), gs)
        assert out["success"] is False
        assert w.pending_diplomatic_dialogue is forged, "the step stands"

    # ── what the wire and the save carry ─────────────────────────────────

    def test_the_stack_is_json_clean_and_every_number_is_an_int(self):
        rig = _r3_walk(["adjust_terms", "territory_yes", "offer_region", "offer_gold", "offer_ap"])
        cur = rig[0].pending_diplomatic_dialogue
        stack = cur["context"]["back_stack"]
        assert len(stack) == 4
        wire = json.loads(json.dumps(cur))

        def floats(node, trail=""):
            if isinstance(node, float):
                yield trail
            elif isinstance(node, dict):
                for k, v in node.items():
                    yield from floats(v, f"{trail}/{k}")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    yield from floats(v, f"{trail}[{i}]")

        assert list(floats(wire["context"])) == [], "the wizard's own context (and the stack in it) carries no float"
        for snap in stack:
            assert "back_stack" not in (snap.get("context") or {}), "the stack does not nest"
            assert "dialogue_id" not in snap, "a restored step is given a fresh identity"

    def test_a_save_taken_mid_wizard_keeps_its_back(self):
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import WorldState
        rig = _r3_walk(["adjust_terms", "territory_yes", "offer_region"])
        w = rig[0]
        reloaded = WorldState.from_dict(json.loads(json.dumps(w.to_dict(), default=str)))
        cur = reloaded.pending_diplomatic_dialogue
        assert cur is not None and cur["type"] == "terms_guidance"
        actions = [o["action"] for o in cur["options"]]
        assert "step_back" in actions and "reconsider" in actions
        ex = CommandExecutor()
        out = ex.handle_diplomatic_dialogue_response(actions.index("step_back") + 1, {"world": reloaded})
        assert out["success"], out
        assert reloaded.pending_diplomatic_dialogue["context"]["guidance_state"] == "region_pick"
        assert reloaded.pending_diplomatic_dialogue["context"]["approved_regions"] == []

    def test_the_dialogue_id_binds_back_like_every_other_answer(self):
        rig = _r3_walk(["adjust_terms", "territory_yes"])
        w, ex, gs = rig
        old_id = w.pending_diplomatic_dialogue["dialogue_id"]
        _r3_click(rig, "offer_region")
        new_id = w.pending_diplomatic_dialogue["dialogue_id"]
        assert new_id != old_id
        actions = _r3_actions(rig)
        stale = ex.handle_diplomatic_dialogue_response(
            actions.index("step_back") + 1, gs, dialogue_id=old_id)
        assert stale["success"] is False and stale.get("stale_dialogue") is True
        fresh = ex.handle_diplomatic_dialogue_response(
            actions.index("step_back") + 1, gs, dialogue_id=new_id)
        assert fresh["success"] is True
        assert w.pending_diplomatic_dialogue["dialogue_id"] not in (old_id, new_id)

    # ── the typed route reaches the same options (shown == accepted) ──────

    def test_a_typed_never_mind_and_back_answer_the_wizard(self):
        from backend.commands.dialogue_routing import match_dialogue_answer
        rig = _r3_walk(_R3_STEPS["gold"])
        w, ex, gs = rig
        cur = w.pending_diplomatic_dialogue
        token = match_dialogue_answer(cur, "back")
        assert token is not None, "typed 'back' answers the Back option"
        assert ex.handle_diplomatic_dialogue_response(token, gs)["success"]
        assert _r3_actions(rig)[:3] == ["territory_yes", "territory_no_gold", "territory_no_ap"]
        cur = w.pending_diplomatic_dialogue
        token = match_dialogue_answer(cur, "never mind")
        assert token is not None, "typed 'never mind' answers the Never mind option"
        assert ex.handle_diplomatic_dialogue_response(token, gs)["success"]
        assert w.pending_diplomatic_dialogue is None

    # ── the client keeps Esc and the X for it ────────────────────────────

    def test_the_client_keeps_reconsider_a_safe_exit_and_never_back(self):
        gd = POPUP_GD.read_text(encoding="utf-8")
        body = re.search(r"const _SAFE_EXIT_ACTIONS = \[(.*?)\]", gd, re.S).group(1)
        safe = set(re.findall(r'"([a-z_]+)"', body))
        assert "reconsider" in safe, "Never mind is the wizard's exit: Esc and the X ride on it"
        assert "step_back" not in safe and "back" not in safe, "Back is a step, not an exit"
        assert '_close_x.visible = exit_action != ""' in gd
        assert "_on_option_selected(exit_action)" in gd

    def test_the_shipped_board_walk_through_the_endpoint(self, _r3_client):
        c, w = _r3_client
        key = w._make_diplo_key("France", "Austria")
        w.nation_relations[key] = -60          # a hostile court: the territory question is asked
        drafted = _r3_post(c, "/command", {"command": "propose peace to Austria"})
        draft = drafted["diplomatic_dialogue"]
        step = _r3_choose(c, draft, "adjust_terms")["diplomatic_dialogue"]
        assert step["type"] == "terms_guidance" and "concessions" in step["talleyrand_text"].lower()
        assert "reconsider" in [o["action"] for o in step["options"]]
        picked = _r3_choose(c, step, "territory_yes")["diplomatic_dialogue"]
        assert "step_back" in [o["action"] for o in picked["options"]]
        back = _r3_choose(c, picked, "step_back")["diplomatic_dialogue"]
        assert "concessions" in back["talleyrand_text"].lower()
        dp = w.diplomatic_points
        out = _r3_choose(c, back, "reconsider")
        assert out["success"] and not out.get("diplomatic_dialogue")
        assert w.pending_diplomatic_dialogue is None and w.proposal_in_transit is None
        assert w.diplomatic_points == dp


# ══════════════════════════════════════════════════════════════════════════
# Siblings
# ══════════════════════════════════════════════════════════════════════════

_R3_ULT_STEPS = {
    "gold": [],
    "territory": ["ultimatum_skip_gold"],
}


def _r3_ultimatum_rig():
    """The ultimatum demand wizard, entered from the ultimatum draft's Customize."""
    from backend.commands.executor import CommandExecutor
    w = _r3_world(score=20)
    key = w._make_diplo_key("France", "Austria")
    w.diplomatic_states[key] = "PEACE"
    w.nation_relations[key] = 10
    # a decisive superiority and a pool to conscript from: every wizard step is asked
    for m in w.marshals.values():
        if m.nation == "France":
            m.strength = max(int(m.strength), 40000)
        elif m.nation == "Austria":
            m.strength = min(int(m.strength), 5000)
    w.manpower_pools.setdefault("Austria", {}).update({"infantry": 9000, "cavalry": 4000, "artillery": 1500})
    w.dialogue_manager.replace({
        "type": "ultimatum_confirm",
        "target_nation": "Austria",
        "turn_created": int(w.current_turn),
        "prompt": "Shall we deliver this ultimatum?",
        "options": [
            {"label": "Deliver Ultimatum", "action": "execute_ultimatum",
             "terms": {"demands": [{"type": "gold_lump", "value": 100}], "sweeteners": [], "clauses": [],
                       "type": "ultimatum_demand"}},
            {"label": "Customize demands", "action": "ultimatum_customize"},
            {"label": "Reconsider", "action": "reconsider"},
        ],
        "terms": {"demands": [{"type": "gold_lump", "value": 100}], "sweeteners": [], "clauses": [],
                  "type": "ultimatum_demand"},
        "context": {},
    })
    rig = (w, CommandExecutor(), {"world": w})
    out = _r3_click(rig, "ultimatum_customize")
    assert out["success"], out
    return rig


class TestS14EX3:
    """The ultimatum demand wizard (`ultimatum_demand_wizard`) is the same
    multi-step wizard with the same missing exit - and it is a BLOCKING
    dialogue, so the player could not even type past it."""

    def test_every_step_offers_never_mind_and_the_later_ones_back(self):
        rig = _r3_ultimatum_rig()
        seen = []
        for _ in range(8):
            cur = rig[0].pending_diplomatic_dialogue
            assert cur is not None
            actions = [o["action"] for o in cur["options"]]
            seen.append((cur["type"], cur["context"].get("guidance_state")))
            assert "reconsider" in actions, (cur["type"], actions)
            if cur["type"] == "ultimatum_confirm":
                break
            forward = next(a for a in actions if a.startswith("ultimatum_") and a not in
                           ("ultimatum_more_gold", "ultimatum_less_gold", "ultimatum_demand_gold",
                            "ultimatum_demand_region", "ultimatum_territory_yes",
                            "ultimatum_demand_manpower", "ultimatum_more_manpower",
                            "ultimatum_less_manpower", "ultimatum_another_type"))
            _r3_click(rig, forward)
        assert len(seen) >= 3, seen

    def test_never_mind_clears_the_blocking_wizard_and_spends_nothing(self):
        rig = _r3_ultimatum_rig()
        w = rig[0]
        assert w.pending_diplomatic_dialogue["type"] == "ultimatum_demand_wizard"
        _r3_click(rig, "ultimatum_demand_gold")          # an answer already given
        before = _r3_ledger(w)
        out = _r3_click(rig, "reconsider")
        assert out["success"]
        assert w.pending_diplomatic_dialogue is None and w.dialogue_manager.peek() is None
        assert _r3_ledger(w) == before
        assert "approved_demands" not in json.dumps(w.to_dict(), default=str)

    def test_back_returns_the_previous_step_with_the_demand_undone(self):
        rig = _r3_ultimatum_rig()
        w = rig[0]
        first = w.pending_diplomatic_dialogue
        assert "step_back" not in [o["action"] for o in first["options"]]
        first_text = first["talleyrand_text"]
        _r3_click(rig, "ultimatum_demand_gold")
        cur = w.pending_diplomatic_dialogue
        assert "step_back" in [o["action"] for o in cur["options"]]
        assert cur["context"]["approved_demands"], "the gold demand was agreed"
        _r3_click(rig, "step_back")
        back = w.pending_diplomatic_dialogue
        assert back["talleyrand_text"] == first_text
        assert back["context"]["approved_demands"] == []
        assert "step_back" not in [o["action"] for o in back["options"]]

    def test_more_demand_is_the_same_step_for_back(self):
        rig = _r3_ultimatum_rig()
        w = rig[0]
        _r3_click(rig, "ultimatum_skip_gold")
        _r3_click(rig, "ultimatum_skip_territory")
        cur = w.pending_diplomatic_dialogue
        assert cur["context"]["guidance_state"] == "ultimatum_manpower_type"
        _r3_click(rig, "ultimatum_pick_manpower_type")
        cur = w.pending_diplomatic_dialogue
        assert cur["context"]["guidance_state"] == "ultimatum_manpower_amount"
        depth = len(cur["context"]["back_stack"])
        amount = cur["context"]["manpower_amount"]
        _r3_click(rig, "ultimatum_less_manpower")
        cur = w.pending_diplomatic_dialogue
        assert cur["context"]["manpower_amount"] < amount
        assert len(cur["context"]["back_stack"]) == depth, "a new figure is not a new step"
        _r3_click(rig, "step_back")
        assert w.pending_diplomatic_dialogue["context"]["guidance_state"] == "ultimatum_manpower_type"

    def test_the_ultimatum_confirm_reached_through_the_wizard_has_its_back(self):
        rig = _r3_ultimatum_rig()
        w = rig[0]
        for _ in range(8):
            cur = w.pending_diplomatic_dialogue
            if cur["type"] == "ultimatum_confirm":
                break
            actions = [o["action"] for o in cur["options"]]
            skip = next((a for a in actions if "skip" in a or a in ("ultimatum_done_manpower",)), None)
            _r3_click(rig, skip)
        cur = w.pending_diplomatic_dialogue
        assert cur["type"] == "ultimatum_confirm"
        actions = [o["action"] for o in cur["options"]]
        assert actions.count("reconsider") == 1 and "step_back" in actions
        assert "execute_ultimatum" in actions and "ultimatum_start_over" in actions
        before = cur["context"]["guidance_state"]
        _r3_click(rig, "step_back")
        assert w.pending_diplomatic_dialogue["type"] == "ultimatum_demand_wizard"
        assert w.pending_diplomatic_dialogue["context"]["guidance_state"] != before

    def test_start_over_clears_the_way_back(self):
        rig = _r3_ultimatum_rig()
        w = rig[0]
        for _ in range(8):
            cur = w.pending_diplomatic_dialogue
            if cur["type"] == "ultimatum_confirm":
                break
            actions = [o["action"] for o in cur["options"]]
            _r3_click(rig, next(a for a in actions if "skip" in a or a == "ultimatum_done_manpower"))
        _r3_click(rig, "ultimatum_start_over")
        assert "step_back" not in [o["action"] for o in w.pending_diplomatic_dialogue["options"]]


class TestS14EX4:
    """The small confirms whose neutral option ("Cancel", "Keep my draft",
    "Keep the joint settlement") was not in the client's safe-exit list: Esc
    was dead and the X hidden on a one-question confirm that has a plain way
    back. Pinned at the source, where `_SAFE_EXIT_ACTIONS` lives."""

    _KEPT = {
        "cancel_pushback": ("backend/commands/diplomatic_executor.py", "pushback_confirm"),
        "keep_current_settlement_draft": ("backend/game_logic/settlement_actions.py", "settlement_confirm"),
        "keep_current_scope_draft": ("backend/game_logic/settlement_staging.py", "settlement_scope_replace_confirm"),
        "keep_joint_settlement": ("backend/game_logic/settlement_staging.py", "settlement_pair_substitute_confirm"),
    }

    def _safe(self) -> set:
        gd = POPUP_GD.read_text(encoding="utf-8")
        body = re.search(r"const _SAFE_EXIT_ACTIONS = \[(.*?)\]", gd, re.S).group(1)
        return set(re.findall(r'"([a-z_]+)"', body))

    @pytest.mark.parametrize("action", sorted(_KEPT))
    def test_the_neutral_option_is_a_safe_exit(self, action):
        assert action in self._safe(), f"{action} is the plain way back and Esc must reach it"
        source, dtype = self._KEPT[action]
        text = (REPO / source).read_text(encoding="utf-8")
        assert f'"{action}"' in text, f"{source} no longer builds {action}"
        assert f'"{dtype}"' in text

    def test_the_destructive_options_are_not_exits(self):
        safe = self._safe()
        for acts in ("confirm_pair_substitute", "replace_current_scope_draft", "confirm_settlement",
                     "back_out_settlement", "execute_proposal", "insist_original", "accept_nudge"):
            assert acts not in safe, f"Esc must never take {acts}"

    def test_esc_on_the_built_confirms_takes_the_keep_option(self):
        """The three settlement confirms, built, and the exit the client's
        Esc would find on each (its `_find_safe_exit_action`, read off the
        .gd): the option that keeps the player's draft, never the one that
        replaces it."""
        from backend.game_logic.settlement_actions import _build_settlement_replace_confirm_dialogue
        from backend.game_logic.settlement_staging import (
            _build_pair_substitute_confirm_dialogue,
            _build_settlement_scope_replace_confirm_dialogue,
        )
        cur = {"war_id": "w1", "war_label": "The War", "selected_target_nation": "Austria",
               "covered_enemy_participants": ["Austria"], "settlement_terms": [], "options": []}
        replace = _build_settlement_replace_confirm_dialogue(
            cur, replacement_terms=[], apply_action="apply_x", apply_label="Apply",
            replacement_kind="k", message="m")
        scope = _build_settlement_scope_replace_confirm_dialogue(
            cur, incoming_request={"war_id": "w1", "selected_target_nation": "Russia",
                                   "covered_enemy_participants": ["Russia"]})
        pair = _build_pair_substitute_confirm_dialogue(
            cur, action="seek_bilateral_peace", proposal_type="peace",
            selected_target="Austria", eligibility={})
        assert _r3_esc(replace) == "keep_current_settlement_draft"
        assert _r3_esc(scope) == "keep_current_scope_draft"
        assert _r3_esc(pair) == "keep_joint_settlement"

    def test_esc_on_a_drafting_pushback_cancels_it(self):
        """Talleyrand softened the terms: Accept his version / Insist on
        original (Authority -3) / Cancel. Esc is the Cancel."""
        from unittest.mock import patch
        from backend.commands.executor import CommandExecutor
        w = _r3_world()
        terms = {"type": "peace", "proposal_type": "peace", "proposer_nation": "France",
                 "target_nation": "Austria", "sweeteners": [],
                 "demands": [{"type": "gold_per_turn", "value": 100}], "clauses": []}
        w.dialogue_manager.replace({
            "type": "proposal_confirm", "target_nation": "Austria", "talleyrand_text": "Draft.",
            "options": [
                {"label": "Send as suggested", "description": "Send.", "action": "execute_proposal",
                 "terms": terms},
                {"label": "Harsher terms", "description": "Demand more.", "action": "modify_harsh",
                 "terms": terms},
                {"label": "Reconsider", "description": "Let me think.", "action": "reconsider"},
            ],
            "context": {"proposal_type": "peace"}, "turn_created": int(w.current_turn), "blocking": False,
        })
        with patch("backend.commands.diplomatic_defiance.roll_drafting_pushback", return_value=True):
            out = CommandExecutor().handle_diplomatic_dialogue_response(2, {"world": w})
        pushback = out["diplomatic_dialogue"]
        assert pushback["type"] == "pushback_confirm"
        assert _r3_esc(pushback) == "cancel_pushback"


# ══════════════════════════════════════════════════════════════════════════
# helpers that need pytest
# ══════════════════════════════════════════════════════════════════════════

def _r3_post(client, path: str, body: dict) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post(path, json=body).json()


def _r3_choose(client, dialogue: dict, action: str) -> dict:
    """The client's way: the 1-based index of the option, with the dialogue's id."""
    for index, option in enumerate(dialogue.get("options") or [], start=1):
        if isinstance(option, dict) and option.get("action") == action:
            body = {"choice": index}
            if dialogue.get("dialogue_id") is not None:
                body["dialogue_id"] = dialogue["dialogue_id"]
            return _r3_post(client, "/respond_to_diplomatic_dialogue", body)
    raise AssertionError(f"no {action!r} option on {dialogue.get('type')!r}")


@pytest.fixture
def _r3_client(monkeypatch):
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


# ══════════════════════════════════════════════════════════════════════════
# row04
# ══════════════════════════════════════════════════════════════════════════
# S14E-4 (S14f part 1, Oct 24, 2026) — a peace with Austria shelters the Russian
# armies on Austrian soil, and neither the peace preview nor the what-if said so.
# 
# Cause: after the peace PT-F1's neutral arm refuses the player's lead a field on
# Austrian soil (`combat_executor.field_on_peace_soil`, DDB-14) — by design — but
# `diplomacy.build_war_context_snapshot` never named the enemy corps the peace
# would shelter, and `question_desk._answer_what_if` printed a full muster the
# typed order would refuse.
# 
# Fix: ONE predicate (`world_state.frontier_halt_owner` / `sheltering_court`, the
# guard's neutral arm, now able to read the board a treaty would leave) feeds a
# `sanctuary` row beside the fallout in every peace preview
# (`peace_sanctuary`), and the what-if (the army's and the province's) asks
# `field_on_peace_soil` first and prints the order's own refusal.
# 
# Siblings pinned here (class `TestS14EXB<k>`): the refusal prints display
# names (XB1), the truce preview (XB2), the province what-if (XB3), the
# settlement table's review row and the per-court chip (XB4), the counsel
# (XB5), the incoming offer's review card and the wizard's preview (XB6).

REPO = Path(__file__).resolve().parents[1]
_R4_SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"

_R4_LINE = ("Kutuzov (Russia) stands at Moravia, Austria's soil — after this peace "
            "no corps of ours may take the field against him there.")
_R4_REFUSAL = ("Murat cannot march on Kutuzov: Moravia is Austria's soil, and we are at "
               "peace with Austria — no corps of ours may take the field there.")


@pytest.fixture(scope="module")
def _r4_boot():
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(_R4_SCENARIO))


@pytest.fixture
def _r4_w(_r4_boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(_r4_boot.to_dict(), default=str)))


def _r4_place(w, **where) -> None:
    for name, loc in where.items():
        w.get_marshal(name).location = loc
    w._build_marshal_index()
    w.invalidate_active_nations_cache()
    w.calculate_visibility()


def _r4_moravia(w) -> None:
    """The measured board (conquest #8): Kutuzov in Moravia, Austria's, with a
    French corps at Vienna to see him."""
    _r4_place(w, Kutuzov="Moravia", Murat="Vienna")


def _r4_state(w, other: str, state: str) -> None:
    w.diplomatic_states[w._make_diplo_key("France", other)] = state


def _r4_snapshot(w, kind: str = "peace", terms=None, target: str = "Austria") -> dict:
    from backend.game_logic.diplomacy import build_war_context_snapshot
    with contextlib.redirect_stdout(io.StringIO()):
        return build_war_context_snapshot(w, "France", target, kind, terms=terms)


def _r4_sanctuary(snapshot: dict) -> list:
    return [x for x in snapshot.get("fallout_warnings", [])
            if x.get("warning_type") == "sanctuary"]


@contextlib.contextmanager
def _r4_client(w):
    """The player's road: /command on a swapped world (three globals, restored)."""
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    saved = (M.game_state["world"], M.world, M.parser)
    M.game_state["world"] = w
    M.world = w
    M.parser = CommandParser(use_real_llm=False)
    try:
        yield TestClient(M.app)
    finally:
        M.game_state["world"], M.world, M.parser = saved


def _r4_say(client, text: str) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json={"command": text}).json()


class TestS14E4:
    def test_the_peace_preview_names_the_corps_the_peace_will_shelter(self, _r4_w):
        _r4_moravia(_r4_w)
        rows = _r4_sanctuary(_r4_snapshot(_r4_w))
        assert [r["display"] for r in rows] == [_R4_LINE]
        assert rows[0]["court"] == "Austria" and rows[0]["region"] == "Moravia"
        assert rows[0]["marshals"] == ["Kutuzov"]

    def test_two_corps_on_one_province_are_one_line_naming_both(self, _r4_w):
        _r4_place(_r4_w, Kutuzov="Moravia", Buxhowden="Moravia", Murat="Vienna")
        rows = _r4_sanctuary(_r4_snapshot(_r4_w))
        assert [r["display"] for r in rows] == [
            "Buxhowden (Russia) and Kutuzov (Russia) stand at Moravia, Austria's soil — "
            "after this peace no corps of ours may take the field against them there."]

    def test_no_line_when_no_third_party_corps_stands_on_the_soil(self, _r4_w):
        # the boot: Kutuzov at Podolia, Buxhowden at Volhynia, Mack and the
        # Archdukes (the TARGET's own) on Austrian ground
        assert _r4_sanctuary(_r4_snapshot(_r4_w)) == []

    def test_the_targets_own_corps_are_not_sheltered_by_the_peace(self, _r4_w):
        _r4_place(_r4_w, Mack="Moravia", Murat="Vienna")
        assert _r4_sanctuary(_r4_snapshot(_r4_w)) == []

    def test_a_fogged_corps_is_not_named(self, _r4_w):
        _r4_place(_r4_w, Kutuzov="Moravia")           # no French eyes near
        from backend.models.intel import PARTIAL
        assert not _r4_w.get_region_intel("Moravia").visibility_at_least(PARTIAL)
        assert _r4_sanctuary(_r4_snapshot(_r4_w)) == []

    def test_a_corps_on_a_war_court_soil_is_not_sheltered(self, _r4_w):
        """Kutuzov in Russian Podolia, in view: Russia is at war with us and no
        peace with Austria changes that ground."""
        _r4_place(_r4_w, Kutuzov="Podolia", Murat="Moravia")
        from backend.models.intel import PARTIAL
        assert _r4_w.get_region_intel("Podolia").visibility_at_least(PARTIAL)
        assert _r4_sanctuary(_r4_snapshot(_r4_w)) == []

    def test_the_line_is_the_refusals_own_predicate(self, _r4_w):
        """shown == applied: sign the peace, and the typed lead is refused the
        very field the preview named — by the same court, in the same breath."""
        _r4_moravia(_r4_w)
        row = _r4_sanctuary(_r4_snapshot(_r4_w))[0]
        _r4_state(_r4_w, "Austria", "PEACE")
        from backend.commands.combat_executor import field_on_peace_soil
        from backend.commands.executor import CommandExecutor
        block = field_on_peace_soil(
            CommandExecutor()._combat, _r4_w.get_marshal("Murat"), "Moravia", _r4_w,
            enemy_nation="Russia")
        assert block is not None and block["owner"] == row["court"] == "Austria"
        with _r4_client(_r4_w) as client:
            typed = _r4_say(client, "Murat, attack Kutuzov")
        assert typed["success"] is False and typed["message"] == _R4_REFUSAL

    @pytest.mark.parametrize("state", [
        "WAR", "ARMISTICE", "PEACE", "OPEN_BORDERS", "NON_AGGRESSION",
        "DEFENSIVE_ALLIANCE", "ALLIANCE", "VASSAL"])
    def test_the_previews_predicate_agrees_with_the_guard_on_every_state(self, _r4_w, state):
        """The drift pin: the board a treaty WOULD leave, read through
        `frontier_halt_owner(assume=...)`, answers exactly what the guard
        (`field_on_peace_soil`) answers once that state is real — killed by
        changing either alone."""
        _r4_moravia(_r4_w)
        from backend.commands.combat_executor import field_on_peace_soil
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import sheltering_court
        kutuzov, murat = _r4_w.get_marshal("Kutuzov"), _r4_w.get_marshal("Murat")
        shown = sheltering_court(_r4_w, "France", kutuzov,
                                 {"states": {"Austria": state}, "controllers": {}})
        _r4_state(_r4_w, "Austria", state)
        block = field_on_peace_soil(CommandExecutor()._combat, murat, "Moravia", _r4_w,
                                    enemy_nation="Russia")
        assert (shown is not None) == (block is not None), (state, shown, block)
        if block is not None:
            assert shown == block["owner"] == "Austria"

    def test_building_the_preview_changes_nothing_on_the_board(self, _r4_w):
        """Display only: the AI's side (and every decision) reads the same world."""
        _r4_moravia(_r4_w)
        before = json.dumps(_r4_w.to_dict(), default=str, sort_keys=True)
        _r4_snapshot(_r4_w)
        assert json.dumps(_r4_w.to_dict(), default=str, sort_keys=True) == before

    def test_the_ai_lead_keeps_pt_f1_and_strikes_from_sheltered_soil(self, _r4_w):
        """GR5's named difference is untouched: the refusal is the PLAYER's."""
        _r4_moravia(_r4_w)
        _r4_state(_r4_w, "Austria", "PEACE")
        from backend.commands.combat_executor import field_on_peace_soil
        from backend.commands.executor import CommandExecutor
        murat = _r4_w.get_marshal("Murat")
        assert field_on_peace_soil(CommandExecutor()._combat, murat, "Moravia", _r4_w,
                                   enemy_nation="Russia") is not None
        # Kutuzov (Russia, at war with France) attacks Murat at Vienna: not refused
        kutuzov = _r4_w.get_marshal("Kutuzov")
        assert field_on_peace_soil(CommandExecutor()._combat, kutuzov, "Vienna", _r4_w,
                                   enemy_nation="France") is None

    def test_what_if_prints_the_refusal_and_no_muster_on_peace_soil(self, _r4_w):
        _r4_moravia(_r4_w)
        _r4_state(_r4_w, "Austria", "PEACE")
        from backend.ai.question_desk import _answer_what_if
        text = _answer_what_if(_r4_w, "France", "Kutuzov", "Murat")
        assert text == f"The order would be refused, Sire: {_R4_REFUSAL} Nothing spent."
        assert "Were you to give the order" not in text and "MUSTER" not in text

    def test_what_if_with_no_corps_named_refuses_for_the_nearest_lead(self, _r4_w):
        _r4_moravia(_r4_w)
        _r4_state(_r4_w, "Austria", "PEACE")
        from backend.ai.question_desk import _answer_what_if
        text = _answer_what_if(_r4_w, "France", "Kutuzov")
        assert "no corps of ours may take the field there" in text and "MUSTER" not in text

    def test_what_if_is_the_orders_own_sentence_through_command(self, _r4_w):
        _r4_moravia(_r4_w)
        _r4_state(_r4_w, "Austria", "PEACE")
        with _r4_client(_r4_w) as client:
            asked = _r4_say(client, "what if Murat attacks Kutuzov")["message"]
            typed = _r4_say(client, "Murat, attack Kutuzov")["message"]
        assert typed in asked and asked.startswith("The order would be refused, Sire: ")

    def test_what_if_still_weighs_the_field_while_the_war_runs(self, _r4_w):
        _r4_moravia(_r4_w)
        from backend.ai.question_desk import _answer_what_if
        text = _answer_what_if(_r4_w, "France", "Kutuzov", "Murat")
        assert "Were you to give the order" in text and "no corps of ours" not in text

    def test_what_if_a_corps_already_on_the_spot_is_not_refused(self, _r4_w):
        """A gun, or a corps standing in the very province, fights where it stands."""
        _r4_place(_r4_w, Kutuzov="Moravia", Murat="Moravia")
        _r4_state(_r4_w, "Austria", "PEACE")
        from backend.ai.question_desk import _answer_what_if
        text = _answer_what_if(_r4_w, "France", "Kutuzov", "Murat")
        assert "Were you to give the order" in text


class TestS14EX7:
    """The refusal's words used the roster key ("ArchdukeCharles") — a raw
    internal name in a player-facing sentence (the typed order, the what-if)."""

    def test_the_refusal_prints_display_names(self, _r4_w):
        from backend.commands.combat_executor import peace_soil_refusal
        said = peace_soil_refusal(_r4_w.get_marshal("Murat"),
                                  _r4_w.get_marshal("ArchdukeCharles"),
                                  {"owner": "Prussia"})["message"]
        assert said.startswith("Murat cannot march on Archduke Charles: ")
        assert "ArchdukeCharles" not in said


class TestS14EX8:
    """A TRUCE shelters exactly as a peace does (the guard reads `is_at_war`,
    and an armistice is not a war) — the truce preview says so, in its words."""

    def test_the_truce_preview_says_truce(self, _r4_w):
        _r4_moravia(_r4_w)
        rows = _r4_sanctuary(_r4_snapshot(_r4_w, kind="armistice"))
        assert [r["display"] for r in rows] == [_R4_LINE.replace("this peace", "this truce")]

    def test_the_truce_shelters_in_fact(self, _r4_w):
        _r4_moravia(_r4_w)
        _r4_state(_r4_w, "Austria", "ARMISTICE")
        from backend.commands.combat_executor import field_on_peace_soil
        from backend.commands.executor import CommandExecutor
        assert field_on_peace_soil(CommandExecutor()._combat, _r4_w.get_marshal("Murat"),
                                   "Moravia", _r4_w, enemy_nation="Russia") is not None

    def test_a_peace_after_a_truce_adds_no_new_shelter(self, _r4_w):
        """Already beyond reach under the truce: this peace shelters no one NEW."""
        _r4_moravia(_r4_w)
        _r4_state(_r4_w, "Austria", "ARMISTICE")
        assert _r4_sanctuary(_r4_snapshot(_r4_w)) == []


class TestS14EX9:
    """`what are Murat's odds against Moravia` — the province road of the
    what-if printed a muster over a corps the order refuses."""

    def test_the_province_what_if_prints_the_refusal(self, _r4_w):
        _r4_moravia(_r4_w)
        _r4_state(_r4_w, "Austria", "PEACE")
        from backend.ai.question_desk import _answer_what_if_region
        text = _answer_what_if_region(_r4_w, "France", "Moravia", "Murat")
        assert text == f"The order would be refused, Sire: {_R4_REFUSAL} Nothing spent."

    def test_the_province_what_if_still_weighs_a_war_field(self, _r4_w):
        _r4_moravia(_r4_w)
        from backend.ai.question_desk import _answer_what_if_region
        text = _answer_what_if_region(_r4_w, "France", "Moravia", "Murat")
        assert "Were you to give the order" in text


class TestS14EX10:
    """The settlement table: its review carries the row (a settlement that
    leaves Russia at war shelters her corps on Austrian soil), and the
    per-court "Separate peace with Austria" chip says it."""

    def test_a_partial_settlement_review_names_the_sheltered_corps(self, _r4_w):
        _r4_moravia(_r4_w)
        from backend.game_logic.settlement_staging import build_settlement_preview
        with contextlib.redirect_stdout(io.StringIO()):
            out = build_settlement_preview(_r4_w, war_id="war_1",
                                           covered_enemy_participants=["Austria"])
        warnings = out["settlement_preview"]["review_sections"]["sections"]["warnings"]
        rows = [w for w in warnings["inline"] + warnings["overflow"] if w.get("code") == "sanctuary"]
        assert [r["detail"] for r in rows] == [_R4_LINE]
        assert rows[0]["code_display"] == "Enemy corps sheltered"

    def test_a_whole_war_settlement_shelters_no_one(self, _r4_w):
        """Russia is covered: her war ends with Austria's — nobody is left to shelter."""
        _r4_moravia(_r4_w)
        from backend.game_logic.settlement_staging import build_settlement_preview
        with contextlib.redirect_stdout(io.StringIO()):
            out = build_settlement_preview(_r4_w, war_id="war_1")
        review = out["settlement_preview"]["review_sections"]
        assert review["sections"]["warnings"]["inline"] is not None
        assert not [w for w in (review["sections"]["warnings"]["inline"]
                                + review["sections"]["warnings"]["overflow"])
                    if w.get("code") == "sanctuary"]

    def test_an_archived_settlements_review_never_carries_the_row(self, _r4_w):
        """The ledger's past settlements read a past peace: `extra_warning_rows` is the live preview's."""
        _r4_moravia(_r4_w)
        from backend.game_logic.settlement_presentation import build_settlement_review
        review = build_settlement_review(
            war_id="war_1", war_label="x", proposer_side="attackers",
            accepting_side="defenders", covered_enemy_participants=["Austria"],
            terms=[], allies=[], warnings=[], acceptance=None, world=_r4_w)
        sections = review["sections"]["warnings"]
        assert not [w for w in sections["inline"] + sections["overflow"]
                    if w.get("code") == "sanctuary"]

    def test_the_separate_peace_chip_says_it(self, _r4_w):
        _r4_moravia(_r4_w)
        from backend.game_logic.settlement_staging import separate_peace_chip
        with contextlib.redirect_stdout(io.StringIO()):
            chip = separate_peace_chip(_r4_w, "Austria", war_id="war_1",
                                       staged_terms=[], actor="France")
        assert chip["sanctuary_display"] == _R4_LINE
        assert _R4_LINE in chip["description"]

    def test_the_chip_is_silent_when_nobody_would_be_sheltered(self, _r4_w):
        from backend.game_logic.settlement_staging import separate_peace_chip
        with contextlib.redirect_stdout(io.StringIO()):
            chip = separate_peace_chip(_r4_w, "Austria", war_id="war_1",
                                       staged_terms=[], actor="France")
        assert "sanctuary_display" not in chip


class TestS14EX11:
    """The counsel offered `Murat, attack Kutuzov` — an order the executor
    refuses once the soil is peace soil ("the counsel offers what the executor TAKES")."""

    def test_the_counsel_never_offers_the_refused_attack(self, _r4_w):
        _r4_moravia(_r4_w)
        from backend.ai.counsel import _attack_candidates, _visible_enemy_map
        enemies = _visible_enemy_map(_r4_w, "France")
        marshals = [m for m in _r4_w.get_player_marshals() if m.name == "Murat"]

        def pairs():
            return [(m.name, e.name) for m, e in
                    _attack_candidates(_r4_w, "France", marshals, enemies)]
        assert ("Murat", "Kutuzov") in pairs()          # the war: offered
        _r4_state(_r4_w, "Austria", "PEACE")
        assert ("Murat", "Kutuzov") not in pairs()      # the peace: refused, so not offered


class TestS14EX12:
    """The incoming offer's review card and the wizard's preview read the same
    builder: both carry the row."""

    def test_the_incoming_offer_card_carries_the_row(self, _r4_w):
        _r4_moravia(_r4_w)
        from backend.game_logic.mailbox_payloads import attach_peace_preview
        terms = {"type": "peace", "proposer_nation": "Austria", "target_nation": "France",
                 "sweeteners": [], "demands": [], "clauses": []}
        with contextlib.redirect_stdout(io.StringIO()):
            payload = attach_peace_preview(_r4_w, {}, "Austria", terms)
        rows = [w for w in payload["fallout_warnings"] if w.get("warning_type") == "sanctuary"]
        assert [r["display"] for r in rows] == [_R4_LINE]

    def test_the_wizards_peace_preview_carries_the_row(self, _r4_w):
        _r4_moravia(_r4_w)
        from backend.game_logic.diplomacy import get_diplomatic_preview
        with contextlib.redirect_stdout(io.StringIO()):
            preview = get_diplomatic_preview(_r4_w, "Austria")
        snap = (preview.get("war_context_snapshots") or {}).get("propose_peace")
        assert snap is not None
        assert [w["display"] for w in snap["fallout_warnings"]
                if w.get("warning_type") == "sanctuary"] == [_R4_LINE]

    def test_a_province_the_terms_take_is_no_longer_the_courts_soil(self, _r4_w):
        """France demands Moravia: at the signature it is French ground, and
        Kutuzov on it is an enemy on our soil — nothing is sheltered there."""
        _r4_moravia(_r4_w)
        terms = {"type": "peace", "sweeteners": [], "clauses": [],
                 "demands": [{"type": "territory_cede", "regions": ["Moravia"], "value": 0}]}
        assert _r4_sanctuary(_r4_snapshot(_r4_w, terms=terms)) == []

    def test_the_client_ranks_the_row_among_the_first_three_consequences(self):
        """The popups show three consequences and count the rest: the row must
        not be the one cut (priority 2, with the ally fallout)."""
        scripts = REPO / "godot-client" / "project-sovereign" / "scripts"
        for name in ("incoming_proposal_popup.gd", "proposal_confirm_popup.gd"):
            src = (scripts / name).read_text(encoding="utf-8")
            assert ('["separate_peace_ally", "contingent_released", "sanctuary"]' in src), name


# ══════════════════════════════════════════════════════════════════════════
# row05
# ══════════════════════════════════════════════════════════════════════════
# S14E-5 (S14f part 1, October 24, 2026) — the declaration offers a purpose on
# a capital a third court already holds, and nothing on the way to war says the
# target is a rump.
# 
# The cause: the War Purpose card (`diplomacy.get_available_war_objectives`)
# marked conquest / forced alliance `available: True` although a conquest-class
# purpose ticks only while the AGGRESSOR holds the target's capital; the
# Cabinet's nation page, the card, Talleyrand's objection and the articles stage
# read nothing of what the court still held; the capture of its last province ran
# `_eliminate_nation` with only a rail icon; the Intelligence book printed
# "1 regions".
# 
# The fix: `diplomacy.court_holdings` / `court_holdings_line` (the live holdings,
# one reading) ride the card's prompt and the Cabinet page (`holdings_line`);
# for the PLAYER a conquest-class purpose is `available: False` with a reason
# while a third court holds the capital (the AI's side is unchanged); the
# objection names the rump; the articles stage names the last province; the
# player's capture of a court's last province prints "Hanover has no province
# left — the war is over, Sire." on that command's reply; the plural.
# 
# Siblings (sweep): TestS14EX14 the Cabinet's Declare War chip, D2 the articles
# stage, D3 the mid-war purpose, D4 the `declare_war` backstop, D5 the ledger's
# "1 regions left", D6 the wizard reads `holdings_line`.

_R5_ROOT = Path(__file__).resolve().parent.parent
_R5_SCENARIO = _R5_ROOT / "godot-client/project-sovereign/assets/maps/europe_1805.json"
_R5_GD = _R5_ROOT / "godot-client/project-sovereign/scripts"

_R5_RUMP_LINE = "Hanover holds 1 province (Osnabruck); the rest are Prussia's."


@pytest.fixture(scope="module")
def _r5_boot():
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(_R5_SCENARIO))


@pytest.fixture
def _r5_world(_r5_boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(_r5_boot.to_dict(), default=str)))


def _r5_rump(world, keep=("Osnabruck",), taker="Prussia"):
    """Hanover keeps ``keep``; ``taker`` holds the rest of its 1805 homeland."""
    for name in world.nation_starting_regions["Hanover"]:
        world.regions[name].controller = "Hanover" if name in keep else taker
    world.invalidate_active_nations_cache()
    return world


def _r5_gd(name):
    return (_R5_GD / name).read_text(encoding="utf-8")


@contextlib.contextmanager
def _r5_client(world):
    import backend.main as main_module
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    originals = (main_module.game_state["world"], main_module.world, main_module.parser)
    main_module.game_state["world"] = world
    main_module.world = world
    main_module.parser = CommandParser(use_real_llm=False)
    try:
        yield TestClient(main_module.app)
    finally:
        (main_module.game_state["world"], main_module.world,
         main_module.parser) = originals


class TestS14E5:
    def test_conquest_class_purposes_are_closed_while_a_third_court_holds_the_capital(self, _r5_world):
        from backend.game_logic.diplomacy import get_available_war_objectives
        w = _r5_rump(_r5_world)
        assert w.regions[w.get_nation_capital("Hanover")].controller == "Prussia"
        by_type = {o["type"]: o for o in get_available_war_objectives(w, "France", "Hanover")}
        for kind in ("conquest", "forced_alliance", "subjugation"):
            assert by_type[kind]["available"] is False, kind
            assert "Prussia" in by_type[kind]["reason"], kind
            assert "Hanover" in by_type[kind]["reason"], kind

    def test_the_reason_names_the_holder_and_the_capital(self, _r5_world):
        from backend.game_logic.diplomacy import get_available_war_objectives
        w = _r5_rump(_r5_world)
        conquest = get_available_war_objectives(w, "France", "Hanover")[0]
        assert conquest["reason"] == (
            "Prussia holds Hanover, Hanover's capital; this purpose scores only while we hold it.")

    def test_the_cards_question_reads_the_live_holdings(self, _r5_world):
        from backend.game_logic.diplomacy import war_purpose_prompt
        w = _r5_rump(_r5_world)
        assert war_purpose_prompt(w, "Hanover") == (
            "Choose your war purpose against Hanover. " + _R5_RUMP_LINE)

    def test_the_cabinets_nation_page_carries_the_holdings_line(self, _r5_world):
        from backend.game_logic.diplomacy import get_diplomatic_preview
        w = _r5_rump(_r5_world)
        page = get_diplomatic_preview(w, "Hanover")
        assert page["holdings_line"] == _R5_RUMP_LINE
        assert page["holdings"] == {"provinces": 1, "homeland": 6, "rump": True,
                                    "capital_holder": "Prussia"}
        with _r5_client(w) as client:
            http = client.get("/diplomatic_preview", params={"nation": "Hanover"}).json()
        assert http["success"] is True
        assert http["holdings_line"] == _R5_RUMP_LINE

    def test_talleyrands_objection_names_the_rump(self, _r5_world):
        from backend.commands.executor import CommandExecutor
        w = _r5_rump(_r5_world, keep=("Hanover",))     # the capital is Hanover's own
        w.threat_level = 60
        w.diplomatic_points = 10
        w.diplomatic_objection_popup = None
        result = CommandExecutor()._execute_diplomatic_declare_war(
            {"target_nation": "Hanover", "war_objective": "conquest"}, w)
        text = result["diplomatic_objection_popup"]["objection_text"]
        assert "Hanover is a rump, Sire: it holds only Hanover. Taking it ends Hanover" in text
        assert "alarm buys one province." in text

    def test_the_last_provinces_capture_prints_the_elimination_line(self, _r5_world):
        from backend.game_logic.diplomacy import set_diplomatic_state
        w = _r5_rump(_r5_world)
        set_diplomatic_state(w, "France", "Hanover", "WAR", "test")
        w.marshals["Ney"].location = "Flanders"
        with _r5_client(w) as client:
            first = client.post("/command", json={"command": "Ney, move to Osnabruck"}).json()
            assert w.regions["Osnabruck"].controller == "France"
            assert "Osnabruck falls to France" in first["message"]
            assert "Hanover has no province left — the war is over, Sire." in first["message"]
            # read, then cleared: the NEXT reply does not say it again
            again = client.post("/command", json={"command": "status"}).json()
        assert "has no province left" not in again["message"]

    def test_a_capture_that_leaves_a_province_prints_no_such_line(self, _r5_world):
        from backend.game_logic.diplomacy import set_diplomatic_state
        w = _r5_rump(_r5_world, keep=("Osnabruck", "Oldenburg"))
        set_diplomatic_state(w, "France", "Hanover", "WAR", "test")
        w.marshals["Ney"].location = "Flanders"
        with _r5_client(w) as client:
            reply = client.post("/command", json={"command": "Ney, move to Osnabruck"}).json()
        assert w.regions["Osnabruck"].controller == "France"
        assert "no province left" not in reply["message"]

    def test_the_intelligence_book_agrees_the_count_with_its_noun(self):
        text = _r5_gd("strategic_ledger.gd")
        assert 'Utils.plural(sregions, "province")' in text
        assert 'str(sregions) + " regions' not in text

    def test_a_normal_target_is_unchanged(self, _r5_world):
        from backend.game_logic.diplomacy import (
            court_holdings_line, get_available_war_objectives, get_diplomatic_preview,
            war_purpose_prompt,
        )
        w = _r5_world
        objectives = get_available_war_objectives(w, "France", "Hanover")
        assert [o["available"] for o in objectives] == [True, True, True]
        assert war_purpose_prompt(w, "Hanover") == "Choose your war purpose against Hanover."
        assert court_holdings_line(w, "Hanover") == ""
        page = get_diplomatic_preview(w, "Hanover")
        assert page["holdings_line"] == ""
        assert page["holdings"]["rump"] is False

    def test_the_ai_sees_the_card_it_always_saw(self, _r5_world):
        """GR5: only what the PLAYER is shown changes — the AI's objective
        availability (read by `declare_war` and the war council) does not."""
        from backend.game_logic.diplomacy import get_available_war_objectives
        from backend.game_logic.war_council import can_declare_war
        w = _r5_rump(_r5_world, taker="Russia")        # a third court on the capital
        for aggressor in ("Prussia", "Austria", "Russia"):
            objectives = get_available_war_objectives(w, aggressor, "Hanover")
            assert objectives[0]["available"] is True, aggressor
            assert objectives[1]["available"] is True, aggressor
        assert get_available_war_objectives(w, "France", "Hanover")[0]["available"] is False
        assert can_declare_war(w, "Prussia", "Hanover", "conquest").get("reason") != "objective_unavailable"


class TestS14EX14:
    """The Cabinet's Declare War chip is shown == applied."""

    def test_the_declare_war_chip_is_shut_with_the_cards_reason(self, _r5_world):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        w = _r5_rump(_r5_world)
        chip = next(a for a in get_available_diplomatic_actions(w, "Hanover")
                    if a["action"] == "declare_war")
        assert chip["available"] is False
        assert chip["disabled_reason"] == (
            "Prussia holds Hanover, Hanover's capital; this purpose scores only while we hold it.")

    def test_the_chip_stays_open_for_a_normal_court(self, _r5_world):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        chip = next(a for a in get_available_diplomatic_actions(_r5_world, "Hanover")
                    if a["action"] == "declare_war")
        assert chip["available"] is True


class TestS14EX15:
    """The articles stage names the last province."""

    def test_the_last_province_article_says_it_ends_the_court(self, _r5_world):
        from backend.game_logic.declared_goals import article_candidates, _candidate_description
        w = _r5_rump(_r5_world, keep=("Hanover",))
        article = next(a for a in article_candidates(w, "France", "Hanover")
                       if a["kind"] == "province")
        text = _candidate_description(w, article)
        assert text.startswith("Hanover's last province, and its capital — taking it ends Hanover;")

    def test_an_ordinary_province_article_is_unchanged(self, _r5_world):
        from backend.game_logic.declared_goals import article_candidates, _candidate_description
        article = next(a for a in article_candidates(_r5_world, "France", "Hanover")
                       if a["kind"] == "province")
        assert "last province" not in _candidate_description(_r5_world, article)


class TestS14EX16:
    """A purpose set mid-war reads the same gate."""

    def test_the_mid_war_purpose_is_refused_with_the_reason(self, _r5_world):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.diplomacy import set_diplomatic_state
        w = _r5_rump(_r5_world)
        set_diplomatic_state(w, "France", "Hanover", "WAR", "test")
        result = CommandExecutor()._diplomatic._set_war_purpose_inner("Hanover", "conquest", w)
        assert result["success"] is False
        assert result["message"].startswith("Prussia holds Hanover, Hanover's capital;")


class TestS14EX17:
    """`declare_war` is the player's backstop at the same gate."""

    def test_the_players_declaration_is_refused_by_the_gate(self, _r5_world):
        from backend.game_logic.diplomacy import declare_war
        w = _r5_rump(_r5_world)
        result = declare_war(w, "France", "Hanover", war_objective="conquest")
        assert result["success"] is False
        assert "Prussia holds Hanover" in result["message"]
        assert w.get_diplomatic_state("France", "Hanover") != "WAR"

    def test_the_typed_declaration_is_refused_and_spends_nothing(self, _r5_world):
        from backend.commands.executor import CommandExecutor
        w = _r5_rump(_r5_world)
        w.diplomatic_points = 5
        w.threat_level = 0
        result = CommandExecutor()._execute_diplomatic_declare_war(
            {"target_nation": "Hanover", "war_objective": "conquest"}, w)
        assert result["success"] is False
        assert result["message"].startswith("Prussia holds Hanover, Hanover's capital;")
        assert w.diplomatic_points == 5
        assert w.get_diplomatic_state("France", "Hanover") != "WAR"

    def test_the_ais_declaration_goes_through_as_it_did(self, _r5_world):
        from backend.game_logic.diplomacy import declare_war
        w = _r5_rump(_r5_world, taker="Russia")
        result = declare_war(w, "Prussia", "Hanover", war_objective="conquest")
        assert result["success"] is True


class TestS14EX18:
    """The ledger's order line agrees its count with its noun too."""

    def test_the_orders_book_says_one_region_left(self):
        text = _r5_gd("strategic_ledger.gd")
        assert 'Utils.plural(path_left, "region") + " left)"' in text
        assert 'str(path_left) + " regions left)"' not in text

    def test_the_strategic_report_says_one_region_away(self):
        text = _r5_gd("strategic_report_popup.gd")
        assert 'Utils.plural(int(distance), "region") + " away)"' in text
        assert 'str(distance) + " regions away)"' not in text


class TestS14EX19:
    """The war page's Set War Purpose row is shown == applied too."""

    def test_the_set_purpose_row_is_shut_with_the_cards_reason(self, _r5_world):
        from backend.game_logic.declared_goals import war_purpose_action
        from backend.game_logic.diplomacy import set_diplomatic_state
        w = _r5_rump(_r5_world)
        set_diplomatic_state(w, "France", "Hanover", "WAR", "test")
        row = war_purpose_action(w, "France", "Hanover")
        assert row["available"] is False
        assert row["disabled_reason"].startswith("Prussia holds Hanover, Hanover's capital;")

    def test_the_row_is_open_while_the_target_holds_its_capital(self, _r5_world):
        from backend.game_logic.declared_goals import war_purpose_action
        from backend.game_logic.diplomacy import set_diplomatic_state
        w = _r5_world
        set_diplomatic_state(w, "France", "Hanover", "WAR", "test")
        row = war_purpose_action(w, "France", "Hanover")
        assert row["available"] is True and row["disabled_reason"] == ""


class TestS14E5TheCabinetPage:
    """The Cabinet's page draws the line the backend sends."""

    def test_the_wizard_reads_the_holdings_line(self):
        text = _r5_gd("diplomacy_wizard.gd")
        assert 'data.get("holdings_line"' in text


# ══════════════════════════════════════════════════════════════════════════
# row06
# ══════════════════════════════════════════════════════════════════════════
# S14E-6 + S14E-D2 (Pre-Deploy S14f part 1, October 24, 2026) — a court's own
# white peace is not another court's claim of victory.
# 
# Cause: `compute_per_court_acceptance` passed the WHOLE package to every court's
# scorer, and `calculate_common_peace_acceptance` fed that whole package into the
# court's own legitimacy tier (`_has_non_trivial_terms` exempting only the
# proposing side's burdens), so one demand on Portugal read as "a victory the
# field has not delivered" on Austria's and Russia's white peace — and
# "More generous" then seeded 100 gold a court to the clause cap, the blocker
# untouched.
# 
# Fix: ONE slicing helper (`settlement_scoring.court_slice_of_package`) — the
# clauses that bind or pay the court and the ground that passes to or from it —
# feeds the legitimacy tier (the user-recommended reading of S14E-D2, built as
# the recommendation); the row names the offending clause and court from
# `component_debug`; "More generous" refuses ("Gold cannot buy this, Sire — …")
# when every holdout's blocker is a mismatch the dial would leave standing, and
# never seeds gold for such a court.
# 
# `TestS14E6` is the defect half (the blocker names clause and court; the dial's
# refusal); `TestS14ED2` is the design half (the slice); `TestS14EX27` … are the
# sibling sweep's pins.

_R6_REPO = Path(__file__).resolve().parents[1]
_R6_SCENARIO = (_R6_REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
                / "europe_1805.json")
_R6_COURTS = ["Austria", "Portugal", "Russia"]


def _r6_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r6_boot():
    from backend.models.world_state import WorldState
    with _r6_quiet():
        return WorldState.from_scenario(str(_R6_SCENARIO))


@pytest.fixture
def _r6_board(_r6_boot):
    """The shipped 1805 board with Portugal at war on France's war_1, a third
    covered court beside Austria and Russia (the conquest sighting's table)."""
    from backend.models.world_state import WorldState
    w = WorldState.from_dict(json.loads(json.dumps(_r6_boot.to_dict(), default=str)))
    inst = w.war_instances["war_1"]
    inst["defenders"].append("Portugal")
    inst["side_by_nation"]["Portugal"] = "defenders"
    inst["active_participants"].append("Portugal")
    w.diplomatic_states[w._make_diplo_key("France", "Portugal")] = "WAR"
    return w


def _r6_demand(region="Beira", **extra):
    return dict({"type": "territory_cede", "from": "Portugal", "to": "France", "region": region}, **extra)


def _r6_table(w, terms, covered=None):
    from backend.game_logic import settlement_baseline as SB
    inst = w.war_instances["war_1"]
    with _r6_quiet():
        view = SB.compute_per_court_acceptance(
            w, war_id="war_1", war_instance=inst, proposer_side="attackers",
            accepting_side="defenders", proposer_side_leader="France",
            covered_enemy_participants=list(covered or _R6_COURTS), settlement_terms=list(terms))
    return {r["nation"]: r for r in view["per_court_acceptance"]}, view


def _r6_comp(row, key):
    return dict((x["component"], x["value"]) for x in row["component_breakdown"]).get(key)


def _r6_scorer(w, terms, court, covered=None):
    from backend.game_logic import settlement_scoring as SC
    inst = w.war_instances["war_1"]
    with _r6_quiet():
        return SC.calculate_common_peace_acceptance(
            w, war_id="war_1", war_instance=inst, proposer_side="attackers",
            accepting_side="defenders", accepting_leader=court, proposer_side_leader="France",
            covered_enemy_participants=list(covered or _R6_COURTS), settlement_terms=list(terms))


def _r6_slice_down(monkeypatch):
    """The ruling DOWN — the series seam: every court reads the whole package."""
    from backend.game_logic import settlement_scoring as SC
    monkeypatch.setattr(SC, "court_slice_of_package", lambda package, court: SC._iter_terms(package))


def _r6_dialogue(w, terms, covered=None):
    from backend.game_logic import settlement_staging as SS
    with _r6_quiet():
        pv = SS.build_settlement_preview(
            w, war_id="war_1", settlement_terms=list(terms),
            covered_enemy_participants=list(covered or _R6_COURTS), actor_nation="France",
            ignore_active_dialogue=True)
        assert pv.get("success"), pv
        dlg = SS.build_settlement_confirm_dialogue(
            w, pv, caller_kind=SS.SETTLEMENT_EDITOR_CALLER_KIND, dialogue_mode="PROPOSE")
    w.dialogue_manager.push(dlg)
    return dlg


def _r6_dial(w, dlg, scope, action="settlement_dial_generous"):
    from backend.game_logic import settlement_actions as SA
    with _r6_quiet():
        return SA.handle_settlement_dialogue_action(
            w, action=action, dialogue=dlg, action_params={"scope": scope})


_R6_WHITE = [{"type": "peace"}]


class TestS14ED2:
    """The design half: the legitimacy tier reads the court's OWN slice."""

    def test_a_the_slice_is_the_clauses_that_bind_or_pay_the_court(self):
        from backend.game_logic.settlement_scoring import clause_parties, court_slice_of_package
        package = [
            {"type": "peace"},
            {"type": "territory_cede", "from": "Portugal", "to": "France", "region": "Beira"},
            {"type": "gold_indemnity", "from": "France", "to": "Austria", "amount": 200},
            {"type": "gold_per_turn", "from": "Russia", "to": "France", "amount": 50, "turns": 4},
            {"type": "liberation", "vassal_nation": "Saxony", "lord_nation": "Prussia", "liberator": "Austria"},
            {"type": "vassal_transfer", "from": "Prussia", "to": "France", "vassal": "Hanover"},
        ]
        kinds = lambda court: [(t["type"], t.get("from") or t.get("lord_nation")) for t in court_slice_of_package(package, court)]  # noqa: E731
        # Portugal: its own cession, and the shared peace — nothing of Austria's or Russia's
        assert kinds("Portugal") == [("peace", None), ("territory_cede", "Portugal")]
        # Austria: paid by France (a clause that PAYS it) and the liberator of Saxony
        assert kinds("Austria") == [("peace", None), ("gold_indemnity", "France"), ("liberation", "Prussia")]
        # Russia: its stream to France
        assert kinds("Russia") == [("peace", None), ("gold_per_turn", "Russia")]
        # the transferred vassal is a party of the transfer
        assert [t["type"] for t in court_slice_of_package(package, "Hanover")] == ["peace", "vassal_transfer"]
        assert clause_parties({"type": "liberation", "vassal_nation": "A", "lord_nation": "B", "liberator": "C"}) == ["B", "A", "C"] \
            or sorted(clause_parties({"type": "liberation", "vassal_nation": "A", "lord_nation": "B", "liberator": "C"})) == ["A", "B", "C"]
        # no court named: the whole package (a caller with nobody in hand scores nothing court-shaped)
        assert len(court_slice_of_package(package, "")) == len(package)
        assert len(court_slice_of_package(package, None)) == len(package)

    def test_b_before_the_ruling_austria_and_russia_read_mismatch_for_portugals_demand(self, _r6_board, monkeypatch):
        """THE REPRODUCTION (ruling down = the whole package, as shipped before)."""
        _r6_slice_down(monkeypatch)
        rows, _ = _r6_table(_r6_board, _R6_WHITE + [_r6_demand()])
        for court in ("Austria", "Russia"):
            assert _r6_comp(rows[court], "settlement_tier_legitimacy") == -20, court   # base -10, mismatch -10
            assert rows[court]["top_blocker_component"] == "settlement_tier_legitimacy"
            assert rows[court]["top_blocker_detail"] == "tier_mismatch", court
        assert _r6_scorer(_r6_board, _R6_WHITE + [_r6_demand()], "Austria")["component_debug"][
            "settlement_tier_legitimacy"]["exceeded_ceiling"] is True

    def test_c_after_it_austria_and_russia_read_their_own_white_peace_and_only_portugal_carries_the_claim(self, _r6_board):
        rows, _ = _r6_table(_r6_board, _R6_WHITE + [_r6_demand()])
        for court in ("Austria", "Russia"):
            assert _r6_comp(rows[court], "settlement_tier_legitimacy") == -10, court   # the white peace's base only
            assert rows[court].get("top_blocker_detail") != "tier_mismatch", court
            tier = _r6_scorer(_r6_board, _R6_WHITE + [_r6_demand()], court)["component_debug"][
                "settlement_tier_legitimacy"]
            assert tier["exceeded_ceiling"] is False and tier["offending_terms"] == []
            assert tier["slice_clause_count"] == 1 and tier["package_clause_count"] == 2   # the peace alone
        assert _r6_comp(rows["Portugal"], "settlement_tier_legitimacy") == -20
        assert rows["Portugal"]["top_blocker_detail"] == "tier_mismatch"

    def test_d_the_ruling_moves_the_numbers_by_the_mismatch_alone(self, _r6_board, monkeypatch):
        """Acceptance numbers move — by the 10 points of the mismatch on each
        court that does not own the clause, nothing else."""
        terms = _R6_WHITE + [_r6_demand()]
        after, _ = _r6_table(_r6_board, terms)
        _r6_slice_down(monkeypatch)
        before, _ = _r6_table(_r6_board, terms)
        for court in ("Austria", "Russia"):
            assert int(after[court]["total"]) - int(before[court]["total"]) == 10, court
        assert after["Portugal"]["total"] == before["Portugal"]["total"]

    def test_e_a_slice_never_lowers_a_courts_legitimacy(self, _r6_board, monkeypatch):
        """The slice is a subset of the package, so the tier can only rise."""
        packages = [
            _R6_WHITE,
            _R6_WHITE + [_r6_demand()],
            _R6_WHITE + [{"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 300},
                         _r6_demand("Lisbon")],
            _R6_WHITE + [{"type": "gold_indemnity", "from": "France", "to": "Russia", "amount": 100}],
        ]
        for terms in packages:
            after, _ = _r6_table(_r6_board, terms)
            with monkeypatch.context() as m:
                _r6_slice_down(m)
                before, _ = _r6_table(_r6_board, terms)
            for court in _R6_COURTS:
                assert (_r6_comp(after[court], "settlement_tier_legitimacy")
                        >= _r6_comp(before[court], "settlement_tier_legitimacy")), (court, terms)

    def test_f_above_the_white_peace_the_ceiling_reads_the_slice_too(self, _r6_board, monkeypatch):
        """A court at its own dictated-terms score (45) is not over its
        harshness ceiling by a heavy demand laid on ANOTHER court."""
        w = _r6_board
        key = w._make_diplo_key("France", "Austria")
        w.war_scores[key] = 45 if key.split("|")[0] == "France" else -45
        heavy = _R6_WHITE + [_r6_demand("Beira"), _r6_demand("Lisbon"), _r6_demand("Porto"),
                             {"type": "gold_indemnity", "from": "Portugal", "to": "France", "amount": 900}]
        after = _r6_scorer(w, heavy, "Austria")["component_debug"]["settlement_tier_legitimacy"]
        _r6_slice_down(monkeypatch)
        before = _r6_scorer(w, heavy, "Austria")["component_debug"]["settlement_tier_legitimacy"]
        assert before["tier"] == after["tier"] == "dictated_terms"
        assert before["exceeded_ceiling"] is True and before["raw_total_harshness"] > before["ceiling"]
        assert after["exceeded_ceiling"] is False and after["raw_total_harshness"] == 0.0
        assert after["score"] - before["score"] == 10

    def test_g_the_slice_helper_is_the_one_seam(self, _r6_board, monkeypatch):
        """The scorer reads `court_slice_of_package` late (the series seam)."""
        from backend.game_logic import settlement_scoring as SC
        seen = []
        real = SC.court_slice_of_package

        def spy(package, court):
            seen.append(court)
            return real(package, court)
        monkeypatch.setattr(SC, "court_slice_of_package", spy)
        _r6_scorer(_r6_board, _R6_WHITE + [_r6_demand()], "Austria")
        assert seen == ["Austria"]

    def test_h_a_one_court_table_is_unchanged(self, _r6_board, monkeypatch):
        """With one covered court every clause that names a covered court names
        it: the slice is the package, so the shipped single-court tables (and
        the AI-to-AI third-party table, whose clauses all run loser -> winner)
        read exactly what they read before."""
        terms = _R6_WHITE + [{"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 300}]
        after = _r6_scorer(_r6_board, terms, "Austria", covered=["Austria"])
        _r6_slice_down(monkeypatch)
        before = _r6_scorer(_r6_board, terms, "Austria", covered=["Austria"])
        assert after["components"] == before["components"] and after["score"] == before["score"]


    def test_i_the_third_party_table_reads_the_whole_package(self, _r6_board):
        """AI-4b's table (`settlement_third_party`): every clause runs between
        the loser and the winner, so the winner's slice IS the package — the
        AI-to-AI acceptance reads what it read before the ruling."""
        from backend.game_logic.settlement_scoring import court_slice_of_package
        terms = [{"type": "peace"},
                 {"type": "gold_indemnity", "from": "Austria", "to": "Russia", "amount": 400},
                 {"type": "territory_cede", "from": "Austria", "to": "Russia", "region": "Moravia"}]
        assert court_slice_of_package(terms, "Russia") == terms
        assert court_slice_of_package(terms, "Austria") == terms

    def test_j_the_ai_letters_dry_run_reads_the_slice_as_the_players_table_does(self, _r6_board):
        """`ai_diplomacy.courts_the_letter_carries` / `_letter_would_carry` run
        the PLAYER's per-court table on the AI's own letter (PC-R4): a court the
        letter's clause does not name reads its own white peace there too."""
        from backend.game_logic import ai_diplomacy as AI
        war = _r6_board.war_instances["war_1"]
        letter = _R6_WHITE + [{"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 300}]
        rows, _ = _r6_table(_r6_board, letter, covered=["Austria", "Russia"])
        assert _r6_comp(rows["Russia"], "settlement_tier_legitimacy") == -10      # no claim of victory on her
        assert _r6_comp(rows["Austria"], "settlement_tier_legitimacy") == -20     # her own gold IS the claim
        with _r6_quiet():
            kept = AI.courts_the_letter_carries(
                _r6_board, "war_1", war, player="France", covered=["Austria", "Russia"],
                terms=letter, writer="Austria")
        assert "Austria" in kept


class TestS14E6:
    """The defect half: the blocker names the clause and the court; the dial
    refuses what gold cannot buy."""

    def test_a_the_blocker_names_the_clause_and_the_court_from_component_debug(self, _r6_board):
        rows, _ = _r6_table(_r6_board, _R6_WHITE + [_r6_demand()])
        row = rows["Portugal"]
        assert row["top_blocker_clause"] == "the demand for Beira on Portugal"
        assert row["top_blocker_cure"] == "remove it, or drop Portugal"
        assert row["top_blocker_line"] == (
            "The demand for Beira on Portugal reads as a claim of victory the field has not "
            "delivered — remove it, or drop Portugal.")
        assert [t["region"] for t in row["top_blocker_terms"]] == ["Beira"]
        tier = _r6_scorer(_r6_board, _R6_WHITE + [_r6_demand()], "Portugal")["component_debug"][
            "settlement_tier_legitimacy"]
        assert tier["court"] == "Portugal" and [t["region"] for t in tier["offending_terms"]] == ["Beira"]
        # a row that is not a mismatch carries none of it
        assert "top_blocker_clause" not in rows["Austria"] and "top_blocker_line" not in rows["Russia"]

    def test_b_the_voice_and_the_heading_speak_the_clause(self, _r6_board):
        from backend.game_logic.diplomatic_templates import resolve_multi_court_settlement_voice
        rows, view = _r6_table(_r6_board, _R6_WHITE + [_r6_demand()])
        with _r6_quiet():
            voice = resolve_multi_court_settlement_voice(
                _r6_board, per_court_acceptance=list(rows.values()),
                overall_acceptance=view["overall_acceptance"])
        line = next(v["line"] for v in voice["per_court_voice"] if v["nation"] == "Portugal")
        assert "the demand for Beira on Portugal reads as a claim of victory the field has not delivered" in line
        austria = next(v["line"] for v in voice["per_court_voice"] if v["nation"] == "Austria")
        assert "claim of victory" not in austria and "Beira" not in austria
        # the Talleyrand heading, on a table where the claim IS the top blocker
        dlg = _r6_dialogue(_r6_board, _R6_WHITE + [_r6_demand()], covered=["Portugal"])
        assert "the demand for Beira on Portugal reads as a claim of victory the field has not delivered" in dlg["talleyrand_text"]
        assert "remove it" in dlg["talleyrand_text"]

    def test_c_the_mismatch_names_each_kind_of_clause(self):
        from backend.display_names import claim_clause_noun, claim_clauses_phrase, tier_mismatch_cure
        assert claim_clause_noun({"type": "gold_indemnity", "from": "Portugal", "amount": 1200}, "Portugal") == \
            "the 1,200-gold indemnity on Portugal"
        assert claim_clause_noun({"type": "gold_per_turn", "from": "Austria", "amount": 50, "turns": 4}, "Austria") == \
            "the 50-gold-a-turn tribute for 4 turns on Austria"
        assert claim_clause_noun({"type": "forced_alliance", "from": "Austria", "to": "France"}, "Austria") == \
            "the alliance forced upon Austria"
        assert claim_clause_noun({"type": "vassalage", "from": "Saxony", "to": "France"}, "Saxony") == \
            "the vassalage of Saxony"
        assert claim_clause_noun({"type": "territory_cede", "from": "Austria", "to": "France",
                                  "regions": ["Tyrol", "Carniola"]}, "Austria") == \
            "the demand for Tyrol and Carniola on Austria"
        assert claim_clauses_phrase([_r6_demand("Beira"), _r6_demand("Lisbon"), _r6_demand("Porto")], "Portugal") == \
            "the demand for Beira on Portugal, the demand for Lisbon on Portugal and 1 more"
        assert tier_mismatch_cure("Portugal", can_drop=False) == "remove it"
        assert tier_mismatch_cure("Portugal", plural=True) == "remove them, or drop Portugal"

    def test_d_more_generous_refuses_what_gold_cannot_buy_and_adds_no_clause(self, _r6_board):
        """A demand the player authored stands under every dial sweep — the
        legitimacy blocker is the clause, and no gold touches it."""
        terms = _R6_WHITE + [_r6_demand(authored_by="player")]
        dlg = _r6_dialogue(_r6_board, terms, covered=["Portugal"])
        row = next(r for r in dlg["per_court_acceptance"] if r["nation"] == "Portugal")
        assert row["top_blocker_detail"] == "tier_mismatch"
        out = _r6_dial(_r6_board, dlg, "table")
        assert out["success"] is False and out["error"] == "settlement_dial_gold_cannot_buy"
        # the only court at this table has no Drop (the V5 coverage floor): the cure is the Remove
        assert out["error_display"] == (
            "Gold cannot buy this, Sire — the demand for Beira on Portugal reads as a claim of "
            "victory the field has not delivered; remove it.")
        assert out["mutated"] is False and out["gold_cannot_buy"] == ["Portugal"]
        # the click is re-attached to the mounted dialogue with its reason, and the draft is untouched
        assert out["diplomatic_dialogue"]["settlement_terms"] == terms
        assert out["diplomatic_dialogue"]["settlement_terms"] == dlg["settlement_terms"]
        # the focused Ease says the same
        focused = _r6_dial(_r6_board, dlg, "Portugal")
        assert focused["success"] is False and focused["error"] == "settlement_dial_gold_cannot_buy"

    def test_e_a_mixed_table_eases_the_others_and_seeds_nothing_for_the_unbuyable_court(self, _r6_board):
        terms = _R6_WHITE + [_r6_demand(authored_by="player")]
        dlg = _r6_dialogue(_r6_board, terms)
        out = _r6_dial(_r6_board, dlg, "table")
        assert out["success"] is True
        eased = [(t["from"], t["to"], t["amount"]) for t in out["settlement_terms"] if t["type"] == "gold_indemnity"]
        assert ("France", "Portugal", 100) not in eased          # no gold for the court gold cannot buy
        assert ("France", "Austria", 100) in eased and ("France", "Russia", 100) in eased
        assert len(out["settlement_terms"]) == 4                  # peace, the demand, two seeds — nowhere near the cap
        assert "Gold cannot buy Portugal's consent, Sire — the demand for Beira on Portugal" in out["message"]
        # click again and again: Portugal never gets a seed, the cap is never filled with gold
        current = out["diplomatic_dialogue"]
        for _ in range(4):
            nxt = _r6_dial(_r6_board, current, "table")
            assert nxt["success"] is True
            assert not any(t["type"] == "gold_indemnity" and t["to"] == "Portugal" for t in nxt["settlement_terms"])
            current = nxt["diplomatic_dialogue"]
        from backend.game_logic.settlement_scoring import MAX_SETTLEMENT_CLAUSE_COUNT
        assert len(current["settlement_terms"]) < MAX_SETTLEMENT_CLAUSE_COUNT

    def test_f_a_mismatch_the_dial_cures_is_not_refused(self, _r6_board):
        """An unprotected territory demand on the court is dropped by an Ease —
        the click cures the mismatch, so it is not 'what gold cannot buy'."""
        dlg = _r6_dialogue(_r6_board, _R6_WHITE + [_r6_demand()], covered=["Portugal"])
        out = _r6_dial(_r6_board, dlg, "Portugal")
        assert out["success"] is True, out.get("error_display")
        assert not any(t["type"] == "territory_cede" for t in out["settlement_terms"])

    def test_g_a_tier_base_blocker_is_not_refused_gold_buys_it(self, _r6_board):
        """The white peace's BASE (-10) is bought down by a concession; only a
        mismatch the dial leaves standing is refused."""
        dlg = _r6_dialogue(_r6_board, _R6_WHITE, covered=["Austria", "Russia"])
        out = _r6_dial(_r6_board, dlg, "Austria")
        assert out["success"] is True
        assert any(t["type"] == "gold_indemnity" and t["to"] == "Austria" for t in out["settlement_terms"])

    def test_h_the_carry_hint_names_the_clause_instead_of_pointing_at_the_dial(self, _r6_board):
        dlg = _r6_dialogue(_r6_board, _R6_WHITE + [_r6_demand(authored_by="player")], covered=["Portugal"])
        hint = dlg["propose_carry_hint"]
        assert "The demand for Beira on Portugal reads as a claim of victory" in hint
        assert "Use 'More generous'" not in hint            # every easeable holdout is a mismatch: the dial is not the way
        mixed = _r6_dialogue(_r6_board, _R6_WHITE + [_r6_demand(authored_by="player")])["propose_carry_hint"]
        assert "Use 'More generous'" in mixed and "The demand for Beira on Portugal reads as a claim" in mixed


    def test_i_the_popup_prints_the_clause_beside_the_blocker(self):
        src = (_R6_REPO / "godot-client" / "project-sovereign" / "scripts"
               / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        assert 'var blocker_clause = _safe_str(row.get("top_blocker_clause"))' in src
        assert 'blocker += " — " + blocker_clause' in src or 'blocker += " — " + blocker_clause' in src


class TestS14EX27:
    """Sibling sweep (Golden Rule 10): every other reader of the package-wide
    tier now reads the same slice."""

    def test_a_the_leader_level_preview_and_the_per_court_rows_agree(self, _r6_board):
        """`build_settlement_preview`'s leader-level acceptance and the row of
        the same court are one reading of the tier."""
        from backend.game_logic import settlement_staging as SS
        terms = _R6_WHITE + [_r6_demand()]
        with _r6_quiet():
            pv = SS.build_settlement_preview(
                _r6_board, war_id="war_1", settlement_terms=terms,
                covered_enemy_participants=_R6_COURTS, actor_nation="France", ignore_active_dialogue=True)
        body = pv["settlement_preview"]
        rows = {r["nation"]: r for r in body["per_court_acceptance"]}
        leader = body["accepting_leader"]
        assert body["acceptance"]["components"]["settlement_tier_legitimacy"] == _r6_comp(
            rows[leader], "settlement_tier_legitimacy")

    def test_b_the_counsels_flip_reads_the_courts_own_blocker(self, _r6_board):
        """The counsel's flip is the holdout's own top blocker term — Austria's
        is no longer 'settlement legitimacy' for Portugal's clause."""
        rows, view = _r6_table(_r6_board, _R6_WHITE + [_r6_demand()])
        lowest = min((r for r in rows.values() if r.get("total") is not None), key=lambda r: int(r["total"]))
        assert lowest["nation"] in ("Austria", "Russia")
        assert lowest["top_blocker_component"] != "settlement_tier_legitimacy" \
            or lowest["top_blocker_detail"] != "tier_mismatch"

    def test_c_the_ratify_time_rescore_reads_the_same_slice(self, _r6_board):
        """The ratifier's single-leader rescore (`calculate_common_peace_
        acceptance`) and the per-court gate read one tier for one court."""
        terms = _R6_WHITE + [_r6_demand()]
        rows, _ = _r6_table(_r6_board, terms)
        scored = _r6_scorer(_r6_board, terms, "Austria")
        assert scored["components"]["settlement_tier_legitimacy"] == _r6_comp(rows["Austria"], "settlement_tier_legitimacy")
        assert scored["score"] == rows["Austria"]["total"]


# ══════════════════════════════════════════════════════════════════════════
# row07
# ══════════════════════════════════════════════════════════════════════════
# S14E-7 — End Turn never says the corps are spent and a known army stands
# beside them (Pre-Deploy S14f part 1; `docs/BUG_FIXES.md` §S14E).
# 
# Cause: the client's one end-turn gate checked lapsing envoys, petitions, an
# unanswered last stand and a treasury projected negative (DDB-13) but no army
# item; morale and danger printed only at dawn (`dispatch._derive_danger`) or on
# a receipt, so a known 55,000-man army beside three spent corps was shown at
# turn start and never re-surfaced at the click.
# 
# Fix: `dispatch.end_turn_army_warning(world, nation)` — ONE backend-computed
# gate line from `MORALE_FAILING_BELOW` (the threshold `_derive_danger` reads
# too) and a fog-legal scan of the known enemies beside the spent corps — rides
# every base response as `end_turn_army_warning`; the client's gate shows it on
# the treasury line's once-per-gate latch (`_army_warned`).
# 
#   TestS14E7     the builder on the fixture world and the shipped 1805 board,
#                 the passthrough on `/command` and a POST handler, the client
#                 gate by source.
#   TestS14EX28   the sweep: the threshold is ONE constant — the dispatch's
#                 danger line, the gate's line and the muster's warning read it.
#   TestS14EX29   the sweep: a passed gate re-arms for the next day, and the
#                 gate's closing instruction names the item that stopped it.

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"

_R7_KEY = "end_turn_army_warning"


def _r7_src(name: str = "main.gd") -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _r7_func(src: str, name: str) -> str:
    """A GDScript function's body: from its header to the next top-level one."""
    start = src.index(f"func {name}(")
    end = src.find("\nfunc ", start + 1)
    return src[start:end if end != -1 else len(src)]


def _r7_board(spent=("Ney", "Davout", "Drouot"), morale=30, waterloo=None):
    """The fixture world: the named French corps stand at Belgium at `morale`;
    Wellington (Britain, 52,000) stands at Waterloo and Gneisenau (Prussia,
    32,000) at Rhineland — both adjacent to Belgium, both at war with France,
    both PARTIAL after the visibility pass. `waterloo` overrides Waterloo's
    visibility label."""
    from backend.models.world_state import WorldState
    w = WorldState(player_nation="France")
    for name in spent:
        w.marshals[name].location = "Belgium"
        w.marshals[name].morale = morale
    w.calculate_visibility()
    if waterloo is not None:
        w.intel["Waterloo"].visibility = waterloo
    return w


def _r7_line(w):
    from backend.game_logic.dispatch import end_turn_army_warning
    return end_turn_army_warning(w, w.player_nation)


@contextlib.contextmanager
def _r7_served(world):
    """Swap the three module globals together and restore them."""
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    saved = (M.game_state["world"], M.world, M.parser)
    M.game_state["world"] = world
    M.world = world
    M.parser = CommandParser(use_real_llm=False)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            yield TestClient(M.app)
    finally:
        M.game_state["world"], M.world, M.parser = saved


class TestS14E7:
    # ── the builder on the fixture world ──────────────────────────────────
    def test_three_spent_corps_beside_a_partial_army_yield_the_line(self):
        w = _r7_board()
        assert _r7_line(w) == (
            "3 corps stand below 40% morale beside Wellington (~55,000, Waterloo) "
            "— end the turn anyway?")

    def test_a_confirmed_army_is_named_at_the_figure_the_dispatch_prints(self):
        from backend.models.intel import FULL
        w = _r7_board(waterloo=FULL)
        # The dispatch prints a FULL province's corps at its exact strength
        # ("55,404 [confirmed]"), never the band — the gate line is the same.
        assert _r7_line(w) == (
            "3 corps stand below 40% morale beside Wellington (52,000, Waterloo) "
            "— end the turn anyway?")

    def test_the_figure_is_the_players_intel_not_the_true_strength(self):
        w = _r7_board()
        w.marshals["Wellington"].strength = 54321      # still "large force"
        assert "~55,000" in _r7_line(w)
        assert "54,321" not in _r7_line(w)

    def test_one_spent_corps_is_named_with_the_singular_verb(self):
        w = _r7_board(spent=("Ney",))
        assert _r7_line(w) == (
            "Ney's corps stands below 40% morale beside Wellington (~55,000, "
            "Waterloo) — end the turn anyway?")

    def test_high_morale_yields_null(self):
        assert _r7_line(_r7_board(morale=70)) is None

    def test_the_threshold_is_below_forty_not_at_forty(self):
        assert _r7_line(_r7_board(morale=40)) is None
        assert _r7_line(_r7_board(morale=39)) is not None

    def test_no_visible_enemy_yields_null_and_a_fogged_one_is_not_named(self):
        from backend.models.intel import UNKNOWN
        w = _r7_board()
        w.intel["Waterloo"].visibility = UNKNOWN
        w.intel["Rhineland"].visibility = UNKNOWN
        assert _r7_line(w) is None
        # Wellington is the larger army — and the unseen one: the line names
        # the man the player can see.
        w.intel["Rhineland"].visibility = "partial"
        line = _r7_line(w)
        assert "Gneisenau" in line and "Wellington" not in line, line
        assert "~27,500" in line and "Rhineland" in line, line

    def test_an_army_that_is_not_beside_the_spent_corps_yields_null(self):
        w = _r7_board(spent=("Ney",))
        w.marshals["Wellington"].location = "Hanover"      # two provinces off
        w.marshals["Gneisenau"].location = "Berlin"
        w.calculate_visibility()
        assert _r7_line(w) is None

    def test_a_court_we_are_at_peace_with_is_not_an_army_beside_us(self):
        w = _r7_board(spent=("Ney",))
        w.marshals["Wellington"].location = "Hanover"
        w.marshals["Gneisenau"].location = "Berlin"
        w.marshals["ArchdukeCharles"].location = "Waterloo"   # Austria: peace
        w.calculate_visibility()
        assert not w.is_at_war("France", "Austria")
        assert _r7_line(w) is None

    def test_the_largest_known_army_is_named_and_counts_only_the_corps_beside_him(self):
        # Ney and Davout stand at Belgium (beside Wellington AND Gneisenau);
        # Grouchy at Lyon is beside Gneisenau (Rhineland) only.
        w = _r7_board(spent=("Ney", "Davout"))
        w.marshals["Grouchy"].morale = 20
        line = _r7_line(w)
        assert line.startswith("2 corps stand below 40% morale beside Wellington"), line
        # Take Wellington out of reach: all three are beside Gneisenau now.
        w.marshals["Wellington"].location = "Hanover"
        w.calculate_visibility()
        assert _r7_line(w).startswith(
            "3 corps stand below 40% morale beside Gneisenau"), _r7_line(w)

    def test_a_captured_or_destroyed_corps_is_not_a_standing_corps(self):
        w = _r7_board(spent=("Ney", "Davout", "Drouot"))
        w.marshals["Ney"].captured_by = "Britain"
        w.marshals["Davout"].strength = 0
        assert _r7_line(w).startswith("Drouot's corps stands below 40%"), _r7_line(w)

    def test_a_healthy_board_costs_no_enemy_scan(self):
        """Rule 8: with no spent corps the builder returns before it reads a
        single enemy, let alone a region."""
        w = _r7_board(morale=90)

        def _boom(*_a, **_k):
            raise AssertionError("scanned the enemy with nothing spent")
        w.get_visible_enemies = _boom
        assert _r7_line(w) is None

    def test_only_the_players_nation_is_warned(self):
        from backend.game_logic.dispatch import end_turn_army_warning
        w = _r7_board()
        assert end_turn_army_warning(w, "Britain") is None

    def test_the_shipped_board_names_mack_beside_three_spent_corps(self):
        from backend.models.world_state import WorldState
        with contextlib.redirect_stdout(io.StringIO()):
            w = WorldState.from_scenario(str(SCENARIO))
        for name in ("Ney", "Davout", "Soult"):
            w.marshals[name].morale = 20
        assert _r7_line(w) == (
            "3 corps stand below 40% morale beside Mack (~55,000, Swabia) "
            "— end the turn anyway?")
        for name in ("Ney", "Davout", "Soult"):
            w.marshals[name].morale = 100
        assert _r7_line(w) is None

    # ── the passthrough ───────────────────────────────────────────────────
    def test_the_line_rides_a_command_response(self):
        w = _r7_board()
        with _r7_served(w) as client:
            r = client.post("/command", json={"command": "status"}).json()
        assert _R7_KEY in r, sorted(r)
        assert r[_R7_KEY] == _r7_line(w)

    def test_the_line_rides_a_post_handlers_base_response(self):
        w = _r7_board()
        with _r7_served(w) as client:
            r = client.post("/cancel_order", json={"marshal": "Ney"}).json()
        assert _R7_KEY in r, sorted(r)
        assert r[_R7_KEY] == _r7_line(w)

    def test_the_end_turn_response_carries_the_new_days_reading(self):
        w = _r7_board()
        with _r7_served(w) as client:
            r = client.post("/command", json={"command": "end turn"}).json()
        assert r.get("turn_ended"), r.get("message")
        assert r[_R7_KEY] == _r7_line(w)      # the board the response describes

    def test_the_builder_is_a_pure_read(self):
        import json
        w = _r7_board()
        before = json.dumps(w.to_dict(), default=str, sort_keys=True)
        assert _r7_line(w) is not None
        assert json.dumps(w.to_dict(), default=str, sort_keys=True) == before

    def test_a_calm_board_sends_null_not_a_missing_key(self):
        w = _r7_board(morale=90)
        with _r7_served(w) as client:
            r = client.post("/command", json={"command": "status"}).json()
        assert _R7_KEY in r and r[_R7_KEY] is None

    def test_the_line_is_a_string_and_the_base_builder_sends_it(self):
        import backend.main as M
        w = _r7_board()
        with contextlib.redirect_stdout(io.StringIO()):
            r = M.build_base_response(w)
        assert isinstance(r[_R7_KEY], str)

    # ── the client's gate, by source ──────────────────────────────────────
    def test_the_client_reads_the_field_and_re_arms_when_it_changes(self):
        src = _r7_src()
        assert "var end_turn_army_warning: String = \"\"" in src
        assert "var _army_warned: bool = false" in src
        sync = _r7_func(src, "_sync_response_hud")
        assert 'response.get("end_turn_army_warning")' in sync
        assert "if _army != end_turn_army_warning:\n\t\t\t_army_warned = false" in sync

    def test_the_gate_stops_once_on_the_line(self):
        src = _r7_src()
        gate = _r7_func(src, "_execute_end_turn")
        # The DDB-13 clause stands byte-for-byte (two older pins read it) …
        assert ("if _current_lapsing_count > 0 or not _current_decision_names.is_empty() "
                "or (_treasury_goes_negative() and not _treasury_warned):") in gate
        # … and the army's own clause follows it.
        assert "if _army_warning_stands():" in gate
        assert gate.index("_treasury_goes_negative()") < gate.index("_army_warning_stands()")
        body = _r7_func(src, "_army_warning_stands")
        assert "end_turn_army_warning != \"\" and not _army_warned" in body
        card = _r7_func(src, "_show_lapse_confirmation")
        assert "_army_warned = true" in card
        assert "parts.append(end_turn_army_warning)" in card
        # The question closes the card: the army line comes after the treasury's.
        assert card.index("_treasury_warned = true") < card.index("_army_warned = true")


class TestS14EX28:
    """Sweep: the threshold is ONE constant."""

    def test_the_constant_is_forty(self):
        from backend.game_logic import dispatch
        assert dispatch.MORALE_FAILING_BELOW == 40

    def test_the_danger_line_and_the_gate_line_flip_together(self, monkeypatch):
        from backend.game_logic import dispatch
        w = _r7_board(spent=("Ney",), morale=50)
        assert _r7_line(w) is None
        assert "Morale failing" not in dispatch._derive_danger(
            w.marshals["Ney"], w, "France", {})
        monkeypatch.setattr(dispatch, "MORALE_FAILING_BELOW", 55)
        assert _r7_line(w).startswith("Ney's corps stands below 55% morale"), _r7_line(w)
        assert "Morale failing (50)" in dispatch._derive_danger(
            w.marshals["Ney"], w, "France", {})

    def test_the_musters_morale_warning_reads_the_same_constant(self):
        src = (REPO / "backend" / "commands" / "economy_executor.py").read_text(
            encoding="utf-8")
        assert "elif new_morale < MORALE_FAILING_BELOW:" in src
        assert "elif new_morale < 40:" not in src

    def test_no_second_forty_in_the_danger_derivation(self):
        src = (REPO / "backend" / "game_logic" / "dispatch.py").read_text(encoding="utf-8")
        body = src[src.index("def _derive_danger("):src.index("_ROUT_CLAUSES = (")]
        assert "int(marshal.morale) < MORALE_FAILING_BELOW" in body
        assert "int(marshal.morale) < 40" not in body


class TestS14EX29:
    """Sweep: the other once-per-gate line (DDB-13's treasury) and the gate's
    closing instruction."""

    def test_a_passed_gate_re_arms_the_army_line_for_the_next_day(self):
        send = _r7_func(_r7_src(), "_send_end_turn")
        assert "_army_warned = false" in send

    def test_the_closing_instruction_names_the_item_that_stopped_the_turn(self):
        card = _r7_func(_r7_src(), "_show_lapse_confirmation")
        assert "to end the turn in deficit" in card       # the treasury's own
        assert "to end the turn anyway" in card           # the army's
        # The deficit instruction is no longer the catch-all else.
        tail = card[card.index("elif not _current_decision_names.is_empty():"):]
        assert "_treasury_goes_negative()" in tail[:tail.index("to end the turn in deficit")]


class TestS14EX30:
    """Sweep (DDB-13's own latch): `_treasury_warned` re-armed only when the
    projected net's integer changed, so a deficit that STOOD at an unchanged
    net gated once and never again on later turns. The gate is per End Turn:
    a passed gate re-arms the treasury's line as it re-arms the army's."""

    def test_a_passed_gate_re_arms_the_treasury_line_too(self):
        send = _r7_func(_r7_src(), "_send_end_turn")
        assert "_treasury_warned = false" in send
        assert send.index("_army_warned = false") < send.index("_treasury_warned = false")


# ══════════════════════════════════════════════════════════════════════════
# row08
# ══════════════════════════════════════════════════════════════════════════
# S14E-8 (Pre-Deploy S14f part 1, October 24, 2026) — the armistice the Cabinet
# scores, the preview shows and the send finds is ONE figure; the lever names its
# road and its control (`docs/BUG_FIXES.md` §S14E).
# 
# Cause: `diplomatic_templates._build_base_terms` stamped `terms["type"]` from
# `get_side_war_score_for` (the SIDE sum over the whole opposing coalition) while
# the wizard row, the counsel's roads line, the acceptance seam and the send all
# type the truce by `armistice_variant_for` (the PAIR's stored score) — on a
# board where the pair and the side differ in sign the preview scored the other
# variant, twenty base points off the send (the measured 44 against 24). Beside
# it `counsel._lever_sentence` priced "a payment of N gold" without the road or
# the control that makes it.
# 
# Fix: `_build_base_terms` stamps the type through `armistice_variant_for`, so the
# snapshot, the confirm's estimate and the send score the one type; the lever
# sentence names the road by the roads line's own label ("Open Settlement with
# Britain alone") and the control by the table's offer row ("Offer gold to
# Britain"), with the stride of the line's +/- controls.
# 
# Drives the shipped 1805 boot (the Third Coalition: France against Britain,
# Austria and Russia in one war instance) through the real endpoints.

_R8_ROOT = Path(__file__).resolve().parents[1]
_R8_SCENARIO = (_R8_ROOT / "godot-client" / "project-sovereign" / "assets"
                / "maps" / "europe_1805.json")
_R8_CONFIRM_POPUP = (_R8_ROOT / "godot-client" / "project-sovereign" / "scripts"
                     / "proposal_confirm_popup.gd")


@pytest.fixture(scope="module")
def _r8_boot():
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(_R8_SCENARIO))


@pytest.fixture
def _r8_world(_r8_boot):
    from backend.models.world_state import WorldState
    w = WorldState.from_dict(json.loads(json.dumps(_r8_boot.to_dict(), default=str)))
    w.diplomatic_points = 30
    return w


def _r8_set(w, nation_a: str, nation_b: str, a_view: int) -> None:
    """Store the pair's war score from `nation_a`'s chair."""
    key = w._make_diplo_key(nation_a, nation_b)
    w.war_scores[key] = a_view if key.split("|")[0] == nation_a else -a_view


def _r8_board(w, britain: int, austria: int, russia: int = 0):
    """The Third Coalition board with chosen pair scores (France's chair)."""
    _r8_set(w, "France", "Britain", britain)
    _r8_set(w, "France", "Austria", austria)
    _r8_set(w, "France", "Russia", russia)
    return w


@pytest.fixture
def _r8_client(monkeypatch, _r8_world):
    """The in-process HTTP idiom on the shipped board: `M.world`,
    `M.game_state["world"]` and the mock parser swapped together."""
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    monkeypatch.setattr(M, "world", _r8_world)
    monkeypatch.setitem(M.game_state, "world", _r8_world)
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), _r8_world


def _r8_post(client, path: str, body: dict) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post(path, json=body).json()


def _r8_quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


# (the pair's score from France's chair against Britain, Austria's) — the SIGNS
# of the pair and of the side differ in both: the measured shape (Britain a
# touch behind, Austria far ahead, the coalition in the black), and its mirror
# (Britain ahead, Austria a little ahead the other way, the coalition in the red).
_R8_SHAPES = [
    pytest.param(-2, 60, "armistice_losing", id="pair_behind_side_ahead"),
    pytest.param(10, -18, "armistice_winning", id="pair_ahead_side_behind"),
]


class TestS14E8:
    # ── the board is what the row says it is ─────────────────────────────

    @pytest.mark.parametrize("britain,austria,pair_variant", _R8_SHAPES)
    def test_the_board_splits_the_pair_from_the_side(self, _r8_world, britain, austria,
                                                     pair_variant):
        """Guard the guard: the pin below proves nothing on a board where the
        pair and the side agree."""
        from backend.game_logic import diplomacy as D
        w = _r8_board(_r8_world, britain, austria)
        pair = D.get_war_score_for(w, "France", "Britain")
        side = D.get_side_war_score_for(w, "France", "Britain")
        assert (pair < 0) != (side < 0), (pair, side)
        assert D.armistice_variant_for(w, "France", "Britain") == pair_variant

    # ── the source: the draft is typed by the pair ───────────────────────

    @pytest.mark.parametrize("britain,austria,pair_variant", _R8_SHAPES)
    @pytest.mark.parametrize("asked", ["armistice", "armistice_winning", "armistice_losing"])
    def test_the_draft_is_typed_by_the_pair_whatever_variant_asked(
            self, _r8_world, britain, austria, pair_variant, asked):
        from backend.game_logic.diplomatic_templates import _build_base_terms
        w = _r8_board(_r8_world, britain, austria)
        terms = _build_base_terms("Britain", asked, w, deterministic=True)
        assert terms["type"] == pair_variant, (
            f"the draft's type came from the side sum: {terms['type']} "
            f"(pair says {pair_variant})")
        assert terms["proposal_type"] == asked, "the asked-for key is left to the send's own rules"

    def test_the_other_courts_pair_types_its_own_draft(self, _r8_world):
        """Austria's pair (+60) is winning and so is the side: one board, two
        courts, each draft typed by its OWN pair."""
        from backend.game_logic.diplomatic_templates import _build_base_terms
        w = _r8_board(_r8_world, -2, 60)
        assert _build_base_terms("Austria", "armistice", w, deterministic=True)["type"] == \
            "armistice_winning"
        assert _build_base_terms("Britain", "armistice", w, deterministic=True)["type"] == \
            "armistice_losing"

    def test_a_bilateral_war_is_unmoved(self):
        """FALSIFIABLE NEGATIVE: with no coalition the pair IS the side, so the
        drafts keep their old type at every sign (zero reads winning)."""
        from backend.game_logic.diplomatic_templates import _build_base_terms
        from backend.models.world_state import WorldState
        for score, expect in ((19, "armistice_winning"), (0, "armistice_winning"),
                              (-1, "armistice_losing"), (-15, "armistice_losing")):
            world = WorldState()
            key = world._make_diplo_key("France", "Austria")
            world.diplomatic_states[key] = "WAR"
            world.nation_relations[key] = -80
            world.war_scores[key] = score if key.split("|")[0] == "France" else -score
            terms = _build_base_terms("Austria", "armistice", world, deterministic=True)
            assert terms["type"] == expect, (score, terms["type"])

    # ── the four surfaces: ONE figure ────────────────────────────────────

    @pytest.mark.parametrize("primed", [True, False], ids=["after_wizard_open", "typed_road"])
    @pytest.mark.parametrize("britain,austria,pair_variant", _R8_SHAPES)
    def test_one_figure_across_the_wizard_row_the_roads_line_the_preview_and_the_send(
            self, _r8_client, britain, austria, pair_variant, primed):
        from backend.game_logic import diplomacy as D
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        client, w = _r8_client
        _r8_board(w, britain, austria)
        # the send rolls Talleyrand's defiance (`random`); a cooling-off turn
        # keeps the pin deterministic — a sabotaged proposal is another matter
        w.talleyrand_defiance_cooldown = 9
        other = "armistice_winning" if pair_variant == "armistice_losing" else "armistice_losing"

        # the figure the send is judged on: the pair variant over the draft
        draft = _r8_quiet(generate_suggested_terms, "Britain", "armistice", w,
                          deterministic=True)
        assert not draft["sweeteners"] and not draft["demands"], (
            "the pin's board drafts an empty truce, so jitter cannot move a figure")

        def _scored(variant: str) -> int:
            return int(D.calculate_acceptance({
                "type": variant, "proposer_nation": "France", "target_nation": "Britain",
                "sweeteners": [], "demands": [], "clauses": []}, w)["score"])

        figure = _scored(pair_variant)
        assert _scored(other) != figure, "the board must tell the two variants apart"

        # 1. the wizard row
        actions = _r8_quiet(D.get_available_diplomatic_actions, w, "Britain")
        row = next(a for a in actions if a["action"] == "propose_armistice")
        assert row["likelihood_score"] == figure

        # 2. the roads line + 3. the preview's snapshot (the wizard open's one memo)
        if primed:
            preview = _r8_quiet(D.get_diplomatic_preview, w, "Britain")
            truce = next(r for r in preview["counsel_roads"] if r["road"] == "truce")
            assert truce["score"] == figure
            shown = next(line for line in preview["counsel_roads_display"]
                         if line.startswith("Propose Armistice"))
            assert f"{figure} of 50" in shown, shown
            snapshot = preview["war_context_snapshots"]["propose_armistice"]
            assert snapshot["acceptance_preview"]["score"] == max(0, min(100, figure))
        else:
            w.talleyrand_counsel_memory = {}

        # 4. the confirm the player opens (the typed road, or pre-filled from the memo)
        opened = _r8_post(client, "/command", {"command": "Talleyrand, propose armistice to Britain"})
        dialogue = opened["diplomatic_dialogue"]
        assert dialogue["type"] == "proposal_confirm"
        assert dialogue["acceptance_estimate"] == max(0, min(100, figure))
        assert dialogue["war_context_snapshot"]["acceptance_preview"]["score"] == \
            max(0, min(100, figure))
        send = next(o for o in dialogue["options"] if o["action"] == "execute_proposal")
        assert send["terms"]["type"] == pair_variant, "the stamped type is the pair's"

        # 5. the send
        sent = _r8_post(client, "/respond_to_diplomatic_dialogue",
                        {"choice": "execute_proposal", "dialogue_id": dialogue["dialogue_id"]})
        assert sent["success"], sent.get("message")
        assert w.proposal_in_transit["acceptance_snapshot"] == figure

    # ── the lever names its road and its control ─────────────────────────

    def test_the_lever_names_the_road_and_the_control(self, _r8_world):
        """The Britain table alone is short of the line by a sum the scorer
        credits: the lever says WHERE (the road, as the roads line prints it)
        and WHAT to press (the table's offer row), not just the sum."""
        from backend.game_logic import counsel as CS
        w = _r8_board(_r8_world, 20, 20, 20)
        reading = _r8_quiet(CS.read_counsel, w, "Britain")
        alone = next(r for r in reading["roads"] if r["road"] == "table_alone")
        gold = int(alone["gold_to_carry"])
        assert gold > 0 and not alone["carries"], alone
        road = next(line for line in _r8_quiet(CS.roads_display, reading)
                    if line.startswith("Open Settlement with Britain alone"))
        lever = CS._lever_sentence(reading)
        assert f"A payment of {gold} gold to Britain would carry the table with her alone." in lever
        assert "At the table: Open Settlement with Britain alone, then Offer gold to Britain" in lever
        assert f"{gold} or more" in lever
        assert "move it by 100" in lever
        assert road.split(" — ")[0] == "Open Settlement with Britain alone"
        line = _r8_quiet(CS.compose_counsel_line, reading, None)["line"]
        assert "At the table: Open Settlement with Britain alone, then Offer gold to Britain" in line

    def test_the_lever_is_a_pure_function_of_the_reading(self):
        from backend.game_logic import counsel as CS
        reading = {"court_display": "Britain", "roads": [{
            "road": "table_alone", "available": True, "carries": False,
            "label": "Open Settlement with Britain alone", "gold_to_carry": 975}]}
        lever = CS._lever_sentence(reading)
        assert lever.startswith("A payment of 975 gold to Britain would carry the table with her alone. ")
        assert "At the table: Open Settlement with Britain alone, then Offer gold to Britain, 975 or more" in lever
        # no sum, no sentence about gold: the old fall-through stands
        reading["roads"][0].pop("gold_to_carry")
        assert "payment" not in CS._lever_sentence(reading)

    def test_the_control_the_lever_names_is_on_the_table_as_the_player_sees_it(
            self, _r8_client):
        """Open the table the way the wizard's row does (`counsel_coverage`)
        and read the offer row the lever points at, and the +/- stride."""
        from backend.game_logic import counsel as CS
        from backend.game_logic.settlement_baseline import SETTLEMENT_DIAL_GOLD_STEP
        client, w = _r8_client
        _r8_board(w, 20, 20, 20)
        reading = _r8_quiet(CS.read_counsel, w, "Britain")
        alone = next(r for r in reading["roads"] if r["road"] == "table_alone")
        opened = _r8_post(client, "/command", {
            "command": "propose common peace with Britain", "action": "propose_common_peace",
            "target_nation": "Britain", "counsel_coverage": ["Britain"],
            "war_id": alone["war_id"]})
        dialogue = opened["diplomatic_dialogue"]
        assert dialogue["type"] == "settlement_confirm", opened.get("message")
        britain = next(r for r in dialogue["per_court_acceptance"] if r["nation"] == "Britain")
        offers = [s for s in britain["demand_suggestions"]
                  if s["group"] == "offer" and s["clause_type"] == "gold_indemnity"]
        assert offers, "the table offers France's gold to Britain"
        # the row reads "Offer 300 gold to Britain"; the lever says "Offer gold to Britain"
        assert re.fullmatch(r"Offer \d+ gold to Britain", offers[0]["label"]), offers[0]["label"]
        lever = CS._lever_sentence(reading)
        assert re.sub(r"Offer \d+ gold", "Offer gold", offers[0]["label"]) in lever
        # the +/- controls step the line by the server's stride (the client mirrors it)
        popup = _R8_CONFIRM_POPUP.read_text(encoding="utf-8")
        assert "[url=mag:%d:%d:amount:-][-][/url][url=mag:%d:%d:amount:+][+][/url]" in popup
        assert re.search(rf"DEMAND_GOLD_MAGNITUDE_STEP\s*=\s*{int(SETTLEMENT_DIAL_GOLD_STEP)}\b", popup)
        assert f"move it by {int(SETTLEMENT_DIAL_GOLD_STEP)}" in lever


# ══════════════════════════════════════════════════════════════════════════
# row09
# ══════════════════════════════════════════════════════════════════════════
# S14E-9 — "Improve Relations reads '+0 over 2 turns' beside 'Net +7 a turn'
# and nothing names the declaration that ate the gain or the errand that paused
# the mission" (DD-B re-measure, diplomacy-first #7, October 24, 2026;
# `docs/BUG_FIXES.md` §S14E).
# 
# Cause: the Cabinet's mission row (`diplomacy._cancel_mission_row`) printed
# current-minus-start only; the tick's earnings, the declaration's -15 on the
# declarer's relation with every court (`declare_war`), and the paused turns
# (`_process_mission_dp`) were never recorded; the declaration beat named no cost
# to France; the dispatch's "Relations now at N" was frozen when the event was
# queued, and sat beside the declaration that had already undone it.
# 
# Fix: the mission record keeps `earned`, `shocks` (each with its cause) and
# `paused_errand` / `paused_starved`, written by the SAME writes that move the
# relation; ONE line (`diplomatic_dialogue.mission_ledger_line`) feeds the Cabinet
# row, the Strategic Ledger, the Talleyrand tab, the rail and the end beats; the
# declaration beat names its cost; the progress line reads the live relation when
# the dispatch is BUILT.

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")


@contextlib.contextmanager
def _r9_quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(scope="module")
def _r9_boot():
    from backend.models.world_state import WorldState
    with _r9_quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def _r9_w(_r9_boot):
    from backend.models.world_state import WorldState
    with _r9_quiet():
        return WorldState.from_dict(json.loads(json.dumps(_r9_boot.to_dict(), default=str)))


@pytest.fixture(autouse=True)
def _r9_no_blowback(monkeypatch):
    from backend.game_logic import diplomatic_dialogue as DD
    monkeypatch.setitem(DD.MISSION_EFFECTS["COURT_NATION"], "undermine_chance", 0.0)


def _r9_rel(w, a, b):
    return int(w.nation_relations.get(w._make_diplo_key(a, b), 0) or 0)


def _r9_set_rel(w, a, b, value):
    w.nation_relations[w._make_diplo_key(a, b)] = int(value)


def _r9_stage(w, mission_type, target, **extra):
    """The dict the executor's `start_mission` arm writes (no new keys)."""
    mission = {
        "type": mission_type, "target": target, "turns_active": 0,
        "paused": False, "paused_turns": 0, "started_turn": int(w.current_turn),
        "initial_relation": _r9_rel(w, w.player_nation, target),
    }
    mission.update(extra)
    w.active_diplomatic_mission = mission
    w.talleyrand_state = "ON_MISSION"
    return mission


def _r9_tick(w, dp=10):
    """One quiet mission tick: steps 2, 3 and 4c of `process_diplomacy_turn`."""
    from backend.game_logic import diplomacy as D
    w.diplomatic_points = dp
    with _r9_quiet():
        D._process_mission_dp(w)
        D._process_mission_effects(w)
        D._process_relation_decay(w)


def _r9_errand_tick(w, dp=10):
    """One advance while he carries a proposal: paused, IN_TRANSIT."""
    from backend.game_logic import diplomacy as D
    w.diplomatic_points = dp
    w.active_diplomatic_mission["paused"] = True
    w.talleyrand_state = "IN_TRANSIT"
    with _r9_quiet():
        D._process_mission_dp(w)
        D._process_mission_effects(w)


def _r9_the_run(w):
    """The sighting, reconstructed on the shipped board: Improve Relations
    on Prussia for two funded turns, two turns paused on an errand, then
    Prussia declares war on Hanover (-15 with every court, France's included)."""
    from backend.game_logic import diplomacy as D
    _r9_set_rel(w, "France", "Prussia", 10)
    _r9_stage(w, "IMPROVE_RELATIONS", "Prussia")
    _r9_tick(w)
    _r9_tick(w)
    w.talleyrand_state = "ON_MISSION"
    _r9_errand_tick(w)
    _r9_errand_tick(w)
    w.talleyrand_state = "ON_MISSION"
    w.active_diplomatic_mission["paused"] = False
    w.pending_dispatch_events = []
    with _r9_quiet():
        res = D.declare_war(w, "Prussia", "Hanover")
    assert res["success"], res
    return res


def _r9_cancel_row(w, court="Prussia"):
    from backend.game_logic import diplomacy as D
    w.diplomatic_points = 10
    with _r9_quiet():
        rows = {a["action"]: a for a in D.get_available_diplomatic_actions(w, court)}
    return rows["cancel_mission"]


class TestS14E9:
    def test_the_cabinet_row_prints_earned_the_shock_and_the_pause(self, _r9_w):
        _r9_the_run(_r9_w)
        text = _r9_cancel_row(_r9_w)["effect_text"]
        assert "+16 earned" in text, text
        assert "-15 from Prussia's declaration on Hanover" in text, text
        assert "paused 2 turns on your errand" in text, text
        # the order: earned, then the shock, then the pause after a semicolon
        assert text.index("+16 earned") < text.index("-15 from") < text.index("; paused 2 turns")

    def test_shown_is_applied_the_record_is_the_writes_themselves(self, _r9_w):
        w = _r9_w
        _r9_set_rel(w, "France", "Prussia", 10)
        _r9_stage(w, "IMPROVE_RELATIONS", "Prussia")
        before = _r9_rel(w, "France", "Prussia")
        _r9_tick(w)
        # the tick wrote +8; the decay then took 1 — the record keeps the WORK
        assert w.active_diplomatic_mission["earned"] == 8
        assert _r9_rel(w, "France", "Prussia") - before == 7

    def test_a_clamped_write_records_what_landed(self, _r9_w):
        w = _r9_w
        _r9_set_rel(w, "France", "Prussia", 97)
        _r9_stage(w, "IMPROVE_RELATIONS", "Prussia")
        _r9_tick(w)                                   # +8 ordered, +3 landed, then done
        assert w.active_diplomatic_mission["earned"] == 3
        assert w.active_diplomatic_mission.get("completed") is True

    def test_the_shock_is_the_declarations_own_landed_write(self, _r9_w):
        w = _r9_w
        _r9_set_rel(w, "France", "Prussia", -95)          # only 5 left to fall
        _r9_stage(w, "IMPROVE_RELATIONS", "Prussia")
        from backend.game_logic import diplomacy as D
        with _r9_quiet():
            D.declare_war(w, "Prussia", "Hanover")
        (shock,) = w.active_diplomatic_mission["shocks"]
        assert shock["delta"] == -5 and shock["kind"] == "war_declaration"
        assert (shock["by"], shock["on"]) == ("Prussia", "Hanover")

    def test_a_declaration_that_misses_the_pair_records_nothing(self, _r9_w):
        w = _r9_w
        from backend.game_logic import diplomacy as D
        _r9_stage(w, "IMPROVE_RELATIONS", "Prussia")
        with _r9_quiet():
            D.declare_war(w, "Saxony", "Hanover")          # hits Saxony's relations only
        assert not (w.active_diplomatic_mission.get("shocks") or [])

    def test_our_own_declaration_is_named_as_ours(self, _r9_w):
        w = _r9_w
        from backend.game_logic import diplomacy as D
        _r9_stage(w, "IMPROVE_RELATIONS", "Prussia")
        with _r9_quiet():
            D.declare_war(w, "France", "Hanover")
        text = _r9_cancel_row(w)["effect_text"]
        assert "from our declaration on Hanover" in text, text

    def test_the_paused_turns_are_counted_once_each_and_only_while_away(self, _r9_w):
        w = _r9_w
        _r9_stage(w, "IMPROVE_RELATIONS", "Prussia")
        _r9_tick(w)
        _r9_errand_tick(w)
        assert w.active_diplomatic_mission["paused_errand"] == 1
        _r9_errand_tick(w)
        assert w.active_diplomatic_mission["paused_errand"] == 2
        assert w.active_diplomatic_mission["turns_active"] == 1, "a paused turn is not a funded turn"
        # a starved pause is its own count — it never reads as an errand
        w.talleyrand_state = "ON_MISSION"
        w.active_diplomatic_mission["paused"] = False
        _r9_tick(w, dp=0)
        assert w.active_diplomatic_mission["paused_starved"] == 1
        assert w.active_diplomatic_mission["paused_errand"] == 2

    def test_the_beat_names_its_cost_to_france(self, _r9_w):
        from backend.game_logic.dispatch import _build_diplomatic_events_section
        w = _r9_w
        with _r9_quiet():
            w.pending_dispatch_events = []
            from backend.game_logic import diplomacy as D
            D.declare_war(w, "Prussia", "Hanover")
            events = _build_diplomatic_events_section(w, "France")
        (beat,) = [e for e in events if e["type"] == "diplomatic_war_declared"]
        assert beat["text"].startswith("Prussia has declared war on Hanover"), beat
        assert "relations with every court, France's included, fall 15" in beat["text"], beat

    def test_a_casus_belli_halves_the_cost_the_beat_names(self, _r9_w):
        from backend.game_logic.dispatch import _build_diplomatic_events_section
        w = _r9_w
        from backend.game_logic import diplomacy as D
        with _r9_quiet():
            w.pending_dispatch_events = []
            D.declare_war(w, "Prussia", "Hanover", casus_belli=True)
            events = _build_diplomatic_events_section(w, "France")
        (beat,) = [e for e in events if e["type"] == "diplomatic_war_declared"]
        assert f"fall {-D.declaration_relation_penalties(True)[1]}" in beat["text"], beat

    def test_a_war_on_france_or_by_france_names_no_extra_cost(self, _r9_w):
        from backend.game_logic.dispatch import _build_diplomatic_events_section
        w = _r9_w
        from backend.game_logic import diplomacy as D
        with _r9_quiet():
            w.pending_dispatch_events = []
            D.declare_war(w, "France", "Hanover")
            events = _build_diplomatic_events_section(w, "France")
        (beat,) = [e for e in events if e["type"] == "diplomatic_war_declared"]
        assert "fall" not in beat["text"], beat

    def test_the_progress_line_reads_the_relation_when_the_dispatch_is_built(self, _r9_w):
        from backend.game_logic.dispatch import _build_diplomatic_events_section
        w = _r9_w
        _r9_the_run(w)
        # the tick that queued the line saw a higher relation than stands now
        queued = [e for e in w.pending_dispatch_events
                  if e.get("type") == "diplomatic_mission_progress"]
        live = _r9_rel(w, "France", "Prussia")
        with _r9_quiet():
            w.pending_dispatch_events.append(
                {"type": "diplomatic_mission_progress",
                 "template_vars": {"nation": "Prussia", "value": 99},
                 "fog_rule": "player_mission", "queued_turn": int(w.current_turn)})
            events = _build_diplomatic_events_section(w, "France")
        (line,) = [e for e in events if e["type"] == "diplomatic_mission_progress"]
        assert f"Relations now at {live}" in line["text"], (line, live, queued)
        assert "99" not in line["text"]
        assert "-15 from Prussia's declaration on Hanover" in line["text"], line

    def test_a_quiet_run_keeps_the_old_progress_line_byte_for_byte(self, _r9_w):
        from backend.game_logic.dispatch import _build_diplomatic_events_section
        w = _r9_w
        _r9_set_rel(w, "France", "Prussia", 10)
        _r9_stage(w, "IMPROVE_RELATIONS", "Prussia")
        w.pending_dispatch_events = []
        _r9_tick(w)
        with _r9_quiet():
            events = _build_diplomatic_events_section(w, "France")
        (line,) = [e for e in events if e["type"] == "diplomatic_mission_progress"]
        assert line["text"] == (
            f"Talleyrand's efforts in Prussia continue. Relations now at "
            f"{_r9_rel(w, 'France', 'Prussia')}."), line

    def test_every_reader_prints_the_same_line(self, _r9_w):
        from backend.game_logic import diplomatic_dialogue as DD
        from backend.game_logic import diplomatic_ledger as DL
        from backend.game_logic import ledger as L
        w = _r9_w
        _r9_the_run(w)
        line = DD.mission_status(w)["ledger_line"]
        assert line == ("+16 earned, -15 from Prussia's declaration on Hanover; "
                        "paused 2 turns on your errand"), line
        assert line in _r9_cancel_row(w)["effect_text"]
        assert L.build_cabinet(w)["ledger_line"] == line
        with _r9_quiet():
            tab = DL.build_diplomatic_ledger(w)["talleyrand"]
        assert tab["active_mission"]["ledger_line"] == line
        DD.restate_mission_notice(w)
        (row,) = [n for n in w.notifications.get_pending() if n.get("type") == "diplomatic_mission"]
        assert line in row["message"], row["message"]

    def test_the_end_beat_and_the_log_tell_the_same_tally(self, _r9_w):
        from backend import campaign_log as CL
        from backend.game_logic import diplomatic_dialogue as DD
        w = _r9_w
        _r9_the_run(w)
        mission = dict(w.active_diplomatic_mission)
        DD.record_mission_end(w, mission, "recalled")
        (row,) = [n for n in w.notifications.get_pending() if n.get("type") == "diplomatic_mission"]
        assert "-15 from Prussia's declaration on Hanover" in row["message"], row["message"]
        ended = [e for e in w.event_log if e.get("type") == "diplomatic_mission_ended"][-1]
        text = CL.format_event_oneliner(ended)
        assert "-15 from Prussia's declaration on Hanover" in text, text

    def test_the_record_survives_a_save(self, _r9_w):
        from backend.models.world_state import WorldState
        w = _r9_w
        _r9_the_run(w)
        with _r9_quiet():
            again = WorldState.from_dict(json.loads(json.dumps(w.to_dict(), default=str)))
        m = again.active_diplomatic_mission
        assert m["earned"] == 16 and m["paused_errand"] == 2
        assert [(s["delta"], s["kind"]) for s in m["shocks"]] == [(-15, "war_declaration")]

    def test_an_old_save_without_the_fields_still_reads(self, _r9_w):
        from backend.game_logic import diplomatic_dialogue as DD
        w = _r9_w
        _r9_stage(w, "IMPROVE_RELATIONS", "Prussia", turns_active=3)
        status = DD.mission_status(w)
        assert status["ledger_line"] == "" and status["earned"] == 0
        assert "over 3 turns" in _r9_cancel_row(w)["effect_text"]

    def test_no_mission_no_trace(self, _r9_w):
        w = _r9_w
        from backend.game_logic import diplomacy as D
        assert w.active_diplomatic_mission is None
        with _r9_quiet():
            D.declare_war(w, "Prussia", "Hanover")
        assert w.active_diplomatic_mission is None

    def test_the_zero_turn_row_still_says_begun(self, _r9_w):
        """S14D-X51's pin, re-asserted with a shock in the record."""
        from backend.game_logic import diplomacy as D
        w = _r9_w
        _r9_stage(w, "IMPROVE_RELATIONS", "Prussia")
        with _r9_quiet():
            D.declare_war(w, "Prussia", "Hanover")
        text = _r9_cancel_row(w)["effect_text"]
        assert "over 0 turns" not in text and ", 0 turns" not in text, text
        assert "begun" in text and "first turn ticks" in text, text
        assert "from Prussia's declaration on Hanover" in text, text


class TestS14EX42:
    """Sibling (the other renderer of the declaration beat): the notice rail's
    "Prussia Declares War!" row names the cost to France as the dispatch does —
    and says nothing extra for a war France fights or chose."""

    def test_the_rail_row_names_the_cost(self, _r9_w):
        from backend.game_logic import diplomacy as D
        w = _r9_w
        with _r9_quiet():
            D.declare_war(w, "Prussia", "Hanover")
        (row,) = [n for n in w.notifications.get_pending() if n.get("type") == "war_declared"]
        assert row["message"].endswith(
            "\u2014 relations with every court, France's included, fall 15."), row["message"]

    def test_our_own_war_adds_nothing(self, _r9_w):
        from backend.game_logic import diplomacy as D
        w = _r9_w
        with _r9_quiet():
            D.declare_war(w, "France", "Hanover")
        (row,) = [n for n in w.notifications.get_pending() if n.get("type") == "war_declared"]
        assert "fall" not in row["message"], row["message"]


class TestS14EX44:
    """Sibling (the other writes that take France's relation with a court):
    a third power's treaty break and downgrade drag the mission's pair exactly
    as a declaration does, and the books record them with their cause."""

    def test_a_treaty_break_is_a_shock_with_its_cause(self, _r9_w):
        from backend.game_logic import diplomacy as D
        w = _r9_w
        _r9_set_rel(w, "France", "Prussia", 30)
        _r9_stage(w, "IMPROVE_RELATIONS", "Prussia")
        key = w._make_diplo_key("Prussia", "Saxony")
        w.diplomatic_states[key] = "NON_AGGRESSION"
        w.active_treaties[key] = {"type": "non_aggression", "nations": ["Prussia", "Saxony"]}
        w.nation_dp = dict(getattr(w, "nation_dp", {}) or {}, Prussia=5)
        with _r9_quiet():
            res = D.break_treaty(key, "Prussia", w)
        assert res["success"], res
        (shock,) = w.active_diplomatic_mission["shocks"]
        assert (shock["kind"], shock["delta"], shock["by"], shock["on"]) == (
            "treaty_break", -10, "Prussia", "Saxony")
        assert "-10 from Prussia's treaty break with Saxony" in _r9_cancel_row(w)["effect_text"]

    def test_a_downgrade_is_a_shock_with_its_cause(self, _r9_w):
        from backend.game_logic import diplomacy as D
        w = _r9_w
        _r9_set_rel(w, "France", "Prussia", 30)
        _r9_stage(w, "IMPROVE_RELATIONS", "Prussia")
        key = w._make_diplo_key("Prussia", "Saxony")
        w.diplomatic_states[key] = "ALLIANCE"
        penalties = D.DOWNGRADE_PENALTIES[("ALLIANCE", "DEFENSIVE_ALLIANCE")]
        assert penalties["relation_all"] != 0, "the ladder's first rung takes the court's standing"
        with _r9_quiet():
            res = D.execute_downgrade(w, "Prussia", "Saxony")
        assert res["success"], res
        (shock,) = w.active_diplomatic_mission["shocks"]
        assert (shock["kind"], shock["by"], shock["on"]) == ("downgrade", "Prussia", "Saxony")
        assert shock["delta"] == penalties["relation_all"]


# ══════════════════════════════════════════════════════════════════════════
# row10
# ══════════════════════════════════════════════════════════════════════════
# S14E-10 + S14E-D3 (Pre-Deploy S14f part 1, October 24, 2026; `docs/BUG_FIXES.md`
# S14E-10, `docs/DESIGN_REFINEMENT.md` S14E-D3).
# 
# CAUSE. Ratifying a white peace at the table cost an ally -18 and a durable
# grievance no screen priced: the ratifier's proposer-side pass shut out the
# allies ITS plan reached, while the forecast read another predicate off the
# contribution ledger (the `no_standing` allies the ratifier skips), the Cabinet
# had no label for `grievance_modifier` ("Grievance Modifier" printed raw), the
# white peace's advisory named "settlement ratified" as its cost, and the
# bilateral road carried the same ally in for nothing.
# FIX (D3: keep the price and state it; close the inconsistency the other way).
# ONE predicate, `settlement_reactions.proposer_ally_plan`, is read by the
# ratifier and by the forecast (shown == applied), and the sentence "Spain is
# left out: -18 relation and a grievance; Make Amends (400g + 2 DP) clears it."
# is stated on the table, the chip and the bilateral preview, and applied by the
# bilateral ratifier too; the grievance term is worded by the flag's TYPE.
# 
# Siblings: TestS14EX45 ... (the sweep). Boards: the SHIPPED 1805 boot.

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"

SPAIN_LINE = ("Spain is left out: -18 relation and a grievance; "
              "Make Amends (400g + 2 DP) clears it.")
# S14E-10's sweep (the orchestrator's XO8): on the boot board Spain stands at the
# alliance's line (40), so the -18 takes it under and the price says so.
SPAIN_CLOCK = (" It takes the alliance under the 40 it holds on (40 → 22) — "
               "Reassure Ally in the Cabinet before it lapses.")
HOLLAND_LINE = "Holland is left out: -7 relation."
BAVARIA_LEFT_OUT_18 = ("Bavaria's war with Austria ends in this instrument; she takes nothing by "
                       "it and is left out: -18 relation and a grievance; Make Amends "
                       "(400g + 2 DP) clears it.")


def _r10_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r10_boot():
    from backend.models.world_state import WorldState
    with _r10_quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def _r10_w(_r10_boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(_r10_boot.to_dict(), default=str)))


def _r10_fight(w, **points):
    """Give nations battle contribution in the war (the material the
    reactions read): `_r10_fight(w, France=200, Spain=200)`."""
    from backend.game_logic.war_contribution import open_episode
    for nation, pts in points.items():
        episode = open_episode(w, "war_1", nation, joined_turn=0, war_sequence=1)
        episode["battle"] = pts
        episode["total"] = pts


def _r10_rel(w, a, b):
    return int(w.nation_relations.get(w._make_diplo_key(a, b), 0) or 0)


def _r10_white_peace(w, covered=("Austria", "Britain", "Russia")):
    """Preview, stage and ratify the table's white peace with the courts
    named (the scorer patched to carry, as the ratification tests do).
    Returns (preview, dialogue, result)."""
    import unittest.mock as mock
    from backend.game_logic import settlement_ratify as SR
    from backend.game_logic import settlement_scoring as SS
    from backend.game_logic.settlement_staging import build_settlement_preview, stage_settlement_confirm
    from tests.test_common_peace_c2_ratification import _acceptance_always_passes
    covered = list(covered)
    with _r10_quiet():
        preview = build_settlement_preview(
            w, war_id="war_1", covered_enemy_participants=covered,
            settlement_terms=[{"type": "peace"}])["settlement_preview"]
    with mock.patch.object(SS, "calculate_common_peace_acceptance", _acceptance_always_passes):
        with _r10_quiet():
            staged = stage_settlement_confirm(
                w, war_id="war_1", settlement_terms=[], covered_enemy_participants=covered,
                white_peace=True)
        assert staged["success"], staged
        dialogue = w.pending_diplomatic_dialogue
        with _r10_quiet():
            out = SR.ratify_settlement_confirm(w, dialogue)
    assert out["success"], out
    return preview, dialogue, out


def _r10_applied(out):
    return {r["ally"]: r for r in out["settlement_reactions"]["proposer_side_reactions"]
            if r["kind"] == "ally_shut_out"}


def _r10_flag(w, victim, grievance_type, episode="e1"):
    from backend.game_logic.diplomacy import _add_grievance_flag
    return _add_grievance_flag(w, breaker="France", victim=victim, grievance_type=grievance_type,
                               episode_id=episode, source_episode_type="test")


# ═══════════════════════════════════════════════════════════════════════════
# S14E-10 — the price, stated before the click, from the ratifier's own plan
# ═══════════════════════════════════════════════════════════════════════════

class TestS14E10:
    def test_a_the_forecast_is_the_ratifiers_set_and_the_ratifier_applies_it(self, _r10_w):
        """A three-pair white peace at the table: the chip's forecast lists
        Spain (-18 and a grievance) and Holland (-7) - and NOT Bavaria or the
        Kingdom of Italy, who have no standing and whom the ratifier skips -
        and the ratification applies exactly that."""
        from backend.game_logic.diplomacy import _get_grievance_flags
        w = _r10_w
        _r10_fight(w, France=200, Spain=200, Holland=10)
        before = {n: _r10_rel(w, "France", n) for n in ("Spain", "Holland", "Bavaria", "KingdomOfItaly")}
        preview, _dialogue, out = _r10_white_peace(w)

        forecast = {r["nation"]: r for r in preview["shut_out_forecast"]}
        assert set(forecast) == {"Spain", "Holland"}, forecast
        assert forecast["Spain"]["display"] == SPAIN_LINE + SPAIN_CLOCK
        assert forecast["Holland"]["display"] == HOLLAND_LINE
        assert (forecast["Spain"]["relation_delta"], forecast["Spain"]["grievance_flag_added"]) == (-18, True)
        assert (forecast["Holland"]["relation_delta"], forecast["Holland"]["grievance_flag_added"]) == (-7, False)

        applied = _r10_applied(out)
        assert set(applied) == set(forecast), "the forecast lists EXACTLY the allies the ratifier punishes"
        for nation, row in forecast.items():
            assert applied[nation]["relation_delta"] == row["relation_delta"], nation
            assert applied[nation]["grievance_flag_added"] == row["grievance_flag_added"], nation
            assert applied[nation]["severity"] == row["severity"], nation

        assert _r10_rel(w, "France", "Spain") == before["Spain"] - 18
        assert _r10_rel(w, "France", "Holland") == before["Holland"] - 7
        assert _r10_rel(w, "France", "Bavaria") == before["Bavaria"]
        assert _r10_rel(w, "France", "KingdomOfItaly") == before["KingdomOfItaly"]
        assert [f["grievance_type"] for f in _get_grievance_flags(w, "France", "Spain")] == ["settlement_shut_out"]
        assert _get_grievance_flags(w, "France", "Holland") == []
        assert _get_grievance_flags(w, "France", "Bavaria") == []

    def test_b_the_price_is_stated_on_the_review_and_the_dialogue_before_the_click(self, _r10_w):
        w = _r10_w
        _r10_fight(w, France=200, Spain=200, Holland=10)
        preview, dialogue, _out = _r10_white_peace(w)
        review = preview["review_sections"]
        assert {r["nation"] for r in review["shut_out_allies_preview"]} == {"Spain", "Holland"}
        spain = next(r for r in review["shut_out_allies_preview"] if r["nation"] == "Spain")
        assert spain["display"] == SPAIN_LINE + SPAIN_CLOCK and spain["relation_delta"] == -18
        thirds = {r["nation"]: r for r in review["third_party_reaction_preview"]
                  if r["kind"].startswith("shut_out_ally")}
        assert thirds["Spain"]["kind"] == "shut_out_ally_grievance" and thirds["Spain"]["display"] == SPAIN_LINE + SPAIN_CLOCK
        assert thirds["Holland"]["kind"] == "shut_out_ally_relation" and thirds["Holland"]["display"] == HOLLAND_LINE
        # the staged dialogue carries the same rows at the top level (the client's footer reads them)
        assert [r["display"] for r in dialogue["shut_out_forecast"]] == \
            [r["display"] for r in preview["shut_out_forecast"]]
        assert all(isinstance(r["relation_delta"], int) and isinstance(r["material_points"], int)
                   and isinstance(r["material_share_pct"], int) for r in dialogue["shut_out_forecast"])

    def test_c_the_make_amends_price_is_the_executors_never_a_literal(self, _r10_w, monkeypatch):
        from backend.commands.diplomatic_executor import DiplomaticExecutor as DE
        from backend.game_logic import cabinet_rows
        monkeypatch.setattr(DE, "_MAKE_AMENDS_GRIEVANCE_GOLD_COST", 777)
        monkeypatch.setattr(DE, "_MAKE_AMENDS_GRIEVANCE_DP_COST", 5)
        assert cabinet_rows.amends_price_words() == "777g + 5 DP"
        w = _r10_w
        _r10_fight(w, France=200, Spain=200)
        preview, _d, out = _r10_white_peace(w)
        spain = next(r for r in preview["shut_out_forecast"] if r["nation"] == "Spain")
        assert spain["display"] == ("Spain is left out: -18 relation and a grievance; "
                                    "Make Amends (777g + 5 DP) clears it." + SPAIN_CLOCK)
        assert spain["amends"] == {"action": "make_amends_grievance", "gold": 777, "dp": 5,
                                   "price_display": "777g + 5 DP"}
        # ...and the dispatch's after-the-fact line quotes the same source
        from backend.game_logic.settlement_presentation import compose_summary_oneliner
        assert "Make Amends (777g + 5 DP) clears it" in compose_summary_oneliner(
            out["settlement_reactions"]["summary_event"])

    def test_d_an_ally_with_no_standing_is_not_listed_and_not_punished(self, _r10_w):
        """The old forecast listed `no_standing` allies; the ratifier skips
        them (spec 14.4). On the boot nobody has fought: nobody is listed,
        nobody is punished."""
        from backend.game_logic.diplomacy import _get_grievance_flags
        w = _r10_w
        before = {n: _r10_rel(w, "France", n) for n in ("Spain", "Holland", "Bavaria", "KingdomOfItaly")}
        preview, _d, out = _r10_white_peace(w)
        assert preview["shut_out_forecast"] == []
        assert _r10_applied(out) == {}
        assert before == {n: _r10_rel(w, "France", n) for n in before}
        assert all(_get_grievance_flags(w, "France", n) == [] for n in before)

    def test_e_a_seat_ally_the_old_forecast_missed_is_listed_at_the_ratifiers_figure(self, _r10_w):
        """A major with a seat and no material in the war: the ratifier gives
        it the reduced hit (-7, no grievance flag - spec 14.2). The ledger
        predicate listed nobody for it; the plan lists it at -7."""
        from backend.game_logic.diplomacy import _get_grievance_flags
        w = _r10_w
        original = w.get_power_tier
        w.get_power_tier = lambda nation, _o=original: "major" if nation == "Spain" else _o(nation)
        before = _r10_rel(w, "France", "Spain")
        preview, _d, out = _r10_white_peace(w)
        forecast = {r["nation"]: r for r in preview["shut_out_forecast"]}
        assert set(forecast) == {"Spain"}, forecast
        assert forecast["Spain"]["severity"] == "minor_shut_out_major_zero_material"
        # the seat ally at the line: -7 takes the alliance under its 40 too (the clock clause)
        assert forecast["Spain"]["display"] == (
            "Spain is left out: -7 relation." + SPAIN_CLOCK.replace("(40 → 22)", "(40 → 33)"))
        applied = _r10_applied(out)
        assert set(applied) == {"Spain"} and applied["Spain"]["relation_delta"] == -7
        assert applied["Spain"]["grievance_flag_added"] is False
        assert _r10_rel(w, "France", "Spain") == before - 7
        assert _get_grievance_flags(w, "France", "Spain") == []

    def test_f_the_assessment_prints_the_shut_out_label_never_grievance_modifier(self, _r10_w):
        from backend.game_logic import diplomacy as D
        w = _r10_w
        _r10_fight(w, France=200, Spain=200)
        _r10_white_peace(w)
        with _r10_quiet():
            preview = D.get_diplomatic_preview(w, "Spain")
        rows = preview["acceptance_preview"]["negative"] + preview["acceptance_preview"]["positive"]
        grievance = next(r for r in rows if r["key"] == "grievance_modifier")
        assert grievance["label"] == "Left out of the peace — Make Amends clears it"
        assert grievance["value"] == -30
        assert not any(r["label"] == "Grievance Modifier" for r in rows)
        make_amends = next(a for a in preview["actions"] if a["action"] == "make_amends_grievance")
        assert make_amends["display_name"] == "Make Amends for Being Left Out of the Peace"

    def test_g_the_feedback_reads_by_flag_type(self, _r10_w):
        from backend.display_names import feedback_phrase
        from backend.game_logic import diplomacy as D
        w = _r10_w
        proposal = {"type": "alliance", "proposer_nation": "France", "target_nation": "Spain",
                    "sweeteners": [], "demands": [], "clauses": []}
        assert D.calculate_acceptance(proposal, w)["grievance_kind"] == ""
        assert feedback_phrase("grievance_modifier", "negative") == "their grievance over abandoned alliances"
        _r10_flag(w, "Spain", "settlement_shut_out")
        shut = D.calculate_acceptance(proposal, w)
        assert shut["grievance_kind"] == "settlement_shut_out"
        assert "their grievance at being left out of the peace" in shut["feedback"]
        assert "abandoned" not in shut["feedback"]
        # an abandoned alliance reads as today
        w.betrayal_history.clear()
        _r10_flag(w, "Spain", "defensive_call_refused")
        assert "their grievance over abandoned alliances" in D.calculate_acceptance(proposal, w)["feedback"]
        # two kinds on one pair: the several wrongs, not either one's name
        _r10_flag(w, "Spain", "settlement_shut_out", episode="e2")
        mixed = D.calculate_acceptance(proposal, w)
        assert mixed["grievance_kind"] == "mixed" and "several grievances" in mixed["feedback"]

    def test_h_the_make_amends_row_names_the_flag_it_clears(self, _r10_w):
        from backend.game_logic import cabinet_rows
        w = _r10_w
        w.nation_gold["France"] = 1000
        w.diplomatic_points = 4
        _r10_flag(w, "Spain", "settlement_shut_out")
        rows = {r["action"]: r for r in cabinet_rows.amends_actions(w, "France", "Spain")}
        row = rows["make_amends_grievance"]
        assert row["display_name"] == "Make Amends for Being Left Out of the Peace"
        assert (row["gold_cost"], row["dp_cost"]) == (400, 2) and row["available"]
        assert cabinet_rows.amends_price_words() == "400g + 2 DP"
        # the abandoned alliance keeps today's name (and a flag with no type is one)
        w.betrayal_history.clear()
        _r10_flag(w, "Spain", "defensive_call_refused")
        assert cabinet_rows.amends_actions(w, "France", "Spain")[0]["display_name"] == \
            "Make Amends for the Abandoned Alliance"

    def test_i_the_white_peace_advisory_never_names_the_ratification_as_a_blocker(self, _r10_w):
        from backend.game_logic.settlement_presentation import compose_summary_oneliner
        w = _r10_w
        _r10_fight(w, France=200, Spain=200, Holland=10)
        _preview, _d, out = _r10_white_peace(w)
        line = compose_summary_oneliner(out["settlement_reactions"]["summary_event"], world=w)
        assert "white peace" in line
        assert SPAIN_LINE in line and HOLLAND_LINE in line
        assert "settlement ratified" not in line and "largest political cost" not in line
        # a white peace nobody paid for says so; it still never says "settlement ratified"
        quiet = {"type": "settlement_summary", "war_id": "war_1", "war_label": "France vs Austria",
                 "white_peace": True, "terms_summary": [], "applied_clauses": [],
                 "participant_reactions": [{"kind": "ally_rewarded", "ally": "Bavaria"}]}
        quiet_line = compose_summary_oneliner(quiet)
        assert "No ally is left out by it." in quiet_line and "settlement ratified" not in quiet_line
        # a peace with terms keeps the accounting register
        terms = dict(quiet, white_peace=False, terms_summary=["territory_cede: Austria to France"],
                     applied_clauses=[{"type": "territory_cede", "from": "Austria", "to": "France"}])
        assert "accounting" in compose_summary_oneliner(terms)

    def test_j_the_client_reads_the_new_fields(self):
        popup = (SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        assert 'data.get("shut_out_forecast", [])' in popup and "Left out of the peace" in popup
        wizard = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert 'data.get("grievance_line", "")' in wizard

    def test_m_a_partial_tables_forecast_is_its_ratifications_set(self, _r10_w):
        """The Austria-alone table: the ratifier's pass reaches every ally of
        the proposing side, not only the ones whose war it ends (Spain fights
        Britain on) - so the forecast must list her too, at the figure the
        ratifier applies. (Whether the pass SHOULD reach her is the open
        question filed beside this row; what is pinned here is shown == applied.)"""
        w = _r10_w
        _r10_fight(w, France=200, Spain=200, Bavaria=200)
        preview, _d, out = _r10_white_peace(w, covered=("Austria",))
        forecast = {r["nation"]: r for r in preview["shut_out_forecast"]}
        applied = _r10_applied(out)
        assert set(forecast) == set(applied) == {"Spain", "Bavaria"}
        assert "Spain" in applied, "the ally whose war the table does not end is reached"
        for nation, row in forecast.items():
            assert (applied[nation]["relation_delta"], applied[nation]["grievance_flag_added"]) == \
                (row["relation_delta"], row["grievance_flag_added"]), nation

    def test_l_an_ally_made_to_pay_is_priced_as_the_ratifier_prices_her(self, _r10_w):
        """PC-R7 (ii): a province of the ALLY pays the compensation and she
        gains nothing by the same peace - the major shut-out, named. The
        forecast reads the same plan (even with no standing in the war)."""
        from backend.game_logic.settlement_reactions import forecast_proposer_side_reactions
        w = _r10_w
        paid = [{"type": "territory_compensate", "from": "Bavaria", "to": "Austria", "region": "Franconia"}]
        rows = forecast_proposer_side_reactions(w, war_id="war_1", proposer_side="attackers",
                                                settlement_terms=paid)
        assert [r["nation"] for r in rows] == ["Bavaria"]
        assert rows[0]["severity"] == "paid_for_the_peace"
        assert rows[0]["display"] == ("Bavaria pays Franconia and is left out: -18 relation and a "
                                      "grievance; Make Amends (400g + 2 DP) clears it.")
        # named in the same instrument (the Pressburg exchange): rewarded, not listed
        traded = paid + [{"type": "territory_cede", "from": "Austria", "to": "Bavaria", "regions": ["Tyrol"]}]
        assert forecast_proposer_side_reactions(w, war_id="war_1", proposer_side="attackers",
                                                settlement_terms=traded) == []

    def test_k_the_ai_roads_never_reach_the_reaction(self, _r10_w):
        """BASELINE_SERIES guard: an AI-AI peace writes no shut-out record -
        the reaction is reached only by the player's table
        (`ratify_settlement_confirm`) and the player's bilateral treaty."""
        w = _r10_w
        _r10_fight(w, Bavaria=200, Spain=200)
        history = json.dumps(w.betrayal_history, default=str)
        memories = json.dumps(getattr(w, "settlement_memories", {}), default=str)
        with _r10_quiet():
            w._ratify_treaty({"type": "peace", "proposer_nation": "Austria", "target_nation": "Bavaria",
                              "sweeteners": [], "demands": [], "clauses": []})
        assert json.dumps(w.betrayal_history, default=str) == history
        assert json.dumps(getattr(w, "settlement_memories", {}), default=str) == memories
        src = (REPO / "backend" / "models" / "world_state.py").read_text(encoding="utf-8")
        gate = src.index("shut_out_carried_allies(")
        assert "ctx.is_player_treaty" in src[src.rindex("ctx._carried_in: List[Dict] = []", 0, gate):gate]


# ═══════════════════════════════════════════════════════════════════════════
# S14E-D3 — the bilateral road: the same outcome, the same price, said first
# ═══════════════════════════════════════════════════════════════════════════

class TestS14ED3:
    def test_a_the_bilateral_preview_states_the_price(self, _r10_w):
        from backend.game_logic import diplomacy as D
        w = _r10_w
        _r10_fight(w, France=200, Bavaria=200)
        words = D.separate_peace_words(w, "France", "Austria")
        assert words["carried"] == ["Bavaria"]
        assert words["per_ally"]["Bavaria"] == BAVARIA_LEFT_OUT_18
        assert words["display"] == words["chip"] == BAVARIA_LEFT_OUT_18
        assert words["shut_out"]["Bavaria"]["display"] == \
            "Bavaria is left out: -18 relation and a grievance; Make Amends (400g + 2 DP) clears it."
        assert D.separate_peace_note(w, "France", "Austria") == BAVARIA_LEFT_OUT_18
        rows = [r for r in D.get_peace_commitment_conflicts(w, "France", "Austria", [])
                if r["conflict_type"] == "carried_in"]
        assert len(rows) == 1 and rows[0]["severity"] == "WARNING"
        assert rows[0]["display"] == BAVARIA_LEFT_OUT_18
        assert rows[0]["detail"]["relation_change"] == -18 and rows[0]["detail"]["grievance"] is True
        # the draft's note on the proposal confirm says it too (Talleyrand's "mark one thing")
        from backend.game_logic.diplomatic_dialogue import separate_peace_note_text
        assert separate_peace_note_text(w, "France", "Austria") == f"Mark one thing, Sire: {BAVARIA_LEFT_OUT_18}"
        # ...and the AI's letter, read from the player's chair, before it is accepted
        incoming = [r for r in D.get_peace_commitment_conflicts(w, "France", "Austria", [], incoming=True)
                    if r["conflict_type"] == "carried_in"]
        assert incoming and incoming[0]["severity"] == "WARNING" and incoming[0]["display"] == BAVARIA_LEFT_OUT_18

    def test_b_the_bilateral_ratifier_applies_the_same_plan(self, _r10_w):
        from backend.game_logic.diplomacy import _get_grievance_flags
        w = _r10_w
        _r10_fight(w, France=200, Bavaria=200)
        before = _r10_rel(w, "France", "Bavaria")
        with _r10_quiet():
            res = w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                                    "sweeteners": [], "demands": [], "clauses": []})
        assert res and res.get("type") == "diplomatic_treaty_signed"
        assert _r10_rel(w, "France", "Bavaria") == before - 18
        assert [f["grievance_type"] for f in _get_grievance_flags(w, "France", "Bavaria")] == ["settlement_shut_out"]
        aftermath = w.peace_ratification_log[-1]["political_aftermath"]
        assert BAVARIA_LEFT_OUT_18 in aftermath, aftermath

    def test_c_the_tables_separate_peace_chip_states_it(self, _r10_w):
        from backend.game_logic.settlement_staging import separate_peace_chip
        w = _r10_w
        _r10_fight(w, France=200, Bavaria=200)
        chip = separate_peace_chip(w, "Austria", war_id="war_1", staged_terms=[], actor="France")
        assert chip.get("available", True) is not False, chip
        assert chip["separate_peace_display"] == BAVARIA_LEFT_OUT_18
        assert BAVARIA_LEFT_OUT_18 in chip["description"] and chip["carried_in"] == ["Bavaria"]

    def test_d_a_carried_ally_with_no_standing_is_free_and_says_so(self, _r10_w):
        """Spec 14.4: no standing, no reaction - on the table and on this road."""
        from backend.game_logic import diplomacy as D
        w = _r10_w
        words = D.separate_peace_words(w, "France", "Austria")
        assert words["shut_out"] == {}
        assert words["per_ally"]["Bavaria"] == \
            "Bavaria's war with Austria ends in this instrument; she takes nothing by it."
        assert [r for r in D.get_peace_commitment_conflicts(w, "France", "Austria", [])
                if r["conflict_type"] == "carried_in"][0]["severity"] == "INFO"
        before = _r10_rel(w, "France", "Bavaria")
        with _r10_quiet():
            w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                              "sweeteners": [], "demands": [], "clauses": []})
        assert _r10_rel(w, "France", "Bavaria") == before

    def test_e_a_named_ally_is_thanked_never_left_out(self, _r10_w):
        from backend.game_logic import diplomacy as D
        w = _r10_w
        _r10_fight(w, France=200, Bavaria=200)
        tyrol = [{"type": "territory_cede", "from": "Austria", "to": "Bavaria", "region": "Tyrol"}]
        words = D.separate_peace_words(w, "France", "Austria", tyrol)
        assert words["per_ally"]["Bavaria"] == \
            "Bavaria's war with Austria ends in this instrument; she is named for Tyrol."
        assert words["shut_out"] == {}

    def test_f_the_table_and_the_bilateral_road_agree_on_the_same_ally(self, _r10_w):
        """One plan: the Austria-alone table and the bilateral peace price
        Bavaria identically."""
        from backend.game_logic import diplomacy as D
        from backend.game_logic.settlement_staging import build_settlement_preview
        w = _r10_w
        _r10_fight(w, France=200, Bavaria=200)
        with _r10_quiet():
            preview = build_settlement_preview(
                w, war_id="war_1", covered_enemy_participants=["Austria"],
                settlement_terms=[{"type": "peace"}])["settlement_preview"]
        table = {r["nation"]: r for r in preview["shut_out_forecast"]}
        bilateral = D.separate_peace_words(w, "France", "Austria")["shut_out"]
        assert table["Bavaria"]["display"] == bilateral["Bavaria"]["display"]
        assert (table["Bavaria"]["relation_delta"], table["Bavaria"]["grievance_flag_added"]) == \
            (bilateral["Bavaria"]["relation_delta"], bilateral["Bavaria"]["grievance_flag_added"]) == (-18, True)


# ═══════════════════════════════════════════════════════════════════════════
# Siblings (Golden Rule 10): the class, swept
# ═══════════════════════════════════════════════════════════════════════════

class TestS14EX45:
    """The proposer-side pass read the side's LEADER off the live instance
    AFTER the cleanup. Once a whole war ends, that field holds whichever
    member left last (the Kingdom of Italy), so the -18, the memory and the
    grievance flag were written between THAT court and the allies - not
    France - and the forecast could not have matched the sum applied."""

    def test_the_reaction_is_written_by_the_leader_before_the_cleanup(self, _r10_w):
        from backend.game_logic.diplomacy import _get_grievance_flags
        w = _r10_w
        _r10_fight(w, France=200, Spain=200)
        before_spain = _r10_rel(w, "France", "Spain")
        preview, _d, out = _r10_white_peace(w)
        assert w.war_instances["war_1"].get("ended_turn") is not None, "the whole war ended at this table"
        assert _r10_rel(w, "France", "Spain") == before_spain - 18
        assert [f["grievance_type"] for f in _get_grievance_flags(w, "France", "Spain")] == ["settlement_shut_out"]
        for court in ("KingdomOfItaly", "Holland", "Bavaria"):
            assert _get_grievance_flags(w, court, "Spain") == [], court
        assert "France" not in _r10_applied(out), "the leader is never her own shut-out ally"
        assert {r["nation"] for r in preview["shut_out_forecast"]} == set(_r10_applied(out))


class TestS14EX46:
    """The ratifier read the ally's material SHARE after the pairs closed
    (PC-F81's class: `cleanup_war_end` closes the contribution episode and the
    share reads 0), so a consulted ally with a 22% share - a major shut-out in
    spec 14.2 - was given the minor -7 and no grievance."""

    def test_the_share_is_read_before_the_pairs_close(self, _r10_w):
        w = _r10_w
        _r10_fight(w, France=78, Holland=22)
        before = _r10_rel(w, "France", "Holland")
        preview, _d, out = _r10_white_peace(w)
        forecast = {r["nation"]: r for r in preview["shut_out_forecast"]}
        assert forecast["Holland"]["standing_level"] == "consult"
        assert forecast["Holland"]["material_share_pct"] == 22
        assert forecast["Holland"]["severity"] == "major_shut_out"
        applied = _r10_applied(out)["Holland"]
        assert (applied["severity"], applied["relation_delta"], applied["grievance_flag_added"]) == \
            ("major_shut_out", -18, True)
        assert _r10_rel(w, "France", "Holland") == before - 18


class TestS14EX47:
    """The reaction's price printed AFTER the fact only, bare of its cure:
    "Spain shut out by France" in the archived review's warning and on the
    dispatch's white-peace line."""

    def test_the_archived_review_warning_states_the_price_and_the_cure(self, _r10_w):
        from backend.game_logic.settlement_presentation import (
            _reaction_warning_detail, build_settlement_review_from_event,
        )
        w = _r10_w
        _r10_fight(w, France=200, Spain=200)
        _p, _d, out = _r10_white_peace(w)
        reaction = _r10_applied(out)["Spain"]
        assert _reaction_warning_detail("ally_shut_out", reaction) == SPAIN_LINE
        review = build_settlement_review_from_event(out["settlement_reactions"]["summary_event"])
        details = [x.get("detail") for x in (review["sections"]["warnings"]["inline"]
                                             + review["sections"]["warnings"]["overflow"])]
        assert SPAIN_LINE in details, details
        # a bare reaction record (no price recorded) keeps the old words
        assert _reaction_warning_detail("ally_shut_out", {"ally": "Spain", "leader": "France"}) == \
            "Spain shut out by France"


class TestS14EX48:
    """The Cabinet's relation line printed the figure and never the cause
    ("Relation: +22 (cool)")."""

    def test_the_cabinet_names_the_grievance_the_court_holds(self, _r10_w):
        from backend.game_logic import diplomacy as D
        w = _r10_w
        with _r10_quiet():
            assert D.get_diplomatic_preview(w, "Spain")["grievance_line"] == ""
        _r10_flag(w, "Spain", "settlement_shut_out")
        with _r10_quiet():
            line = D.get_diplomatic_preview(w, "Spain")["grievance_line"]
        assert line == (f"Spain holds a grievance against us: being left out of the peace "
                        f"(since turn {w.current_turn}). Make Amends (400g + 2 DP) clears one.")


class TestS14EX49:
    """S14C-X4's class swept to `_COMPONENT_LABELS`: every nonzero term the
    Cabinet's acceptance preview can print has a name, and the state/debug
    readings (a count of flags, a floor, a posture's turns) are never listed
    as factors."""

    def test_every_acceptance_component_is_labelled_or_metadata(self, _r10_w):
        from backend.game_logic import diplomacy as D
        w = _r10_w
        keys = set()
        for ptype in ("peace", "alliance", "armistice_winning", "vassalage", "open_borders"):
            result = D.calculate_acceptance({"type": ptype, "proposer_nation": "France",
                                             "target_nation": "Austria", "sweeteners": [],
                                             "demands": [], "clauses": []}, w)
            keys |= set(result["components"])
        named = set(D._COMPONENT_LABELS) | set(D._COMPONENT_LABELED_BY_STATE) | set(D._COMPONENT_METADATA_KEYS)
        assert keys <= named, sorted(keys - named)
        assert not (set(D._COMPONENT_LABELS) & set(D._COMPONENT_METADATA_KEYS))
        for key, label in D._COMPONENT_LABELS.items():
            assert label != key.replace("_", " ").title(), key

    def test_the_old_missing_keys_now_print_names(self):
        from backend.game_logic import diplomacy as D
        assert D.acceptance_term_label("bargain_value_mod") == "A war bargain offered"
        assert D.acceptance_term_label("coalition_loyalty") == "Her loyalty to the league"
        assert D.acceptance_term_label("agenda_mod", 5) == "Advances their design"
        assert D.acceptance_term_label("agenda_mod", -5) == "Entrenches their denial"
        assert D.acceptance_term_label("grievance_modifier", -30, "settlement_shut_out") == \
            "Left out of the peace — Make Amends clears it"
        assert D.acceptance_term_label("grievance_modifier", -30, "") == \
            "Abandoned alliance — Make Amends clears it"

    def test_the_cabinet_never_lists_a_metadata_reading_as_a_factor(self, _r10_w):
        from backend.game_logic import diplomacy as D
        w = _r10_w
        _r10_flag(w, "Spain", "settlement_shut_out")
        with _r10_quiet():
            preview = D.get_diplomatic_preview(w, "Spain")
        rows = preview["acceptance_preview"]["negative"] + preview["acceptance_preview"]["positive"]
        assert not [r for r in rows if r["key"] in D._COMPONENT_METADATA_KEYS], rows


# ══════════════════════════════════════════════════════════════════════════
# row11
# ══════════════════════════════════════════════════════════════════════════
# S14E-11 — "An ally slid from +33 to +2 and collapsed to a defensive alliance
# over five turns while the Cabinet's counsel named no lever and the warning
# carried none" (DD-B re-measure, diplomacy-first #9, October 24, 2026;
# `docs/BUG_FIXES.md` §S14E).
# 
# Cause: ALLIANCE deliberately omits Improve Relations and offers Reassure Ally
# (WO-D2 / G1 contract 8); the counsel (`diplomacy._base_recommendation_and_mission`)
# considered `mission_improve_relations` only, so an ally's page printed the dead
# end "Relations must improve before proposals will find purchase."; and
# `check_auto_downgrade`'s warning was a plain line with no cause and no lever.
# 
# Fix: the counsel names Reassure Ally or Make Amends (whichever is open) for an
# ally's slide — "recall Talleyrand from Russia first" when the one mission slot
# is busy — and the same lever, read from the same gates the Cabinet's rows read
# (`mission_gate`, `cabinet_rows.amends_actions`), rides the "may collapse"
# warning with its cause (the slide, in points and turns).

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")


@contextlib.contextmanager
def _r11_quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(scope="module")
def _r11_boot():
    from backend.models.world_state import WorldState
    with _r11_quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def _r11_w(_r11_boot):
    from backend.models.world_state import WorldState
    with _r11_quiet():
        w = WorldState.from_dict(json.loads(json.dumps(_r11_boot.to_dict(), default=str)))
    w.diplomatic_points = 10
    return w


def _r11_set_rel(w, a, b, value):
    w.nation_relations[w._make_diplo_key(a, b)] = int(value)


def _r11_preview(w, court="Spain"):
    from backend.game_logic import diplomacy as D
    with _r11_quiet():
        return D.get_diplomatic_preview(w, court)


def _r11_busy(w, target="Russia", mission_type="IMPROVE_RELATIONS"):
    w.active_diplomatic_mission = {
        "type": mission_type, "target": target, "turns_active": 1,
        "paused": False, "paused_turns": 0, "started_turn": int(w.current_turn),
        "initial_relation": 0}
    w.talleyrand_state = "ON_MISSION"


def _r11_strike(w, court="Spain"):
    """One live betrayal strike France -> court: Make Amends has something to clear."""
    from backend.game_logic import diplomacy as D
    key = D._betrayal_key("France", court)
    w.betrayal_history = dict(getattr(w, "betrayal_history", {}) or {})
    record = dict(w.betrayal_history.get(key, {}) or {})
    record["strikes"] = [{"severity": "moderate", "turn": 1, "episode_id": "r11-strike",
                          "decays_on_turn": int(w.current_turn) + 9}]
    w.betrayal_history[key] = record
    w.nation_gold["France"] = 5000


def _r11_warn(w, court="Spain", state="ALLIANCE", relation=2, history=(33, 20, 10)):
    from backend.game_logic import diplomacy as D
    key = w._make_diplo_key("France", court)
    w.diplomatic_states[key] = state
    w.nation_relations[key] = relation
    w.relation_history[key] = list(history)
    w.turns_below_threshold = {}
    events = []
    with _r11_quiet():
        for _ in range(3):
            events.extend(D.check_auto_downgrade(w))
    (warning,) = [e for e in events if e["type"] == "downgrade_warning" and "France" in e["nations"]]
    return warning


class TestS14E11:
    def test_a_sliding_ally_is_counselled_to_reassure(self, _r11_w):
        w = _r11_w
        _r11_set_rel(w, "France", "Spain", 2)
        pv = _r11_preview(w)
        text = pv["recommendation"]
        assert "Relations must improve before proposals will find purchase." not in text, text
        assert "Talleyrand recommends: Reassure Ally" in text, text
        assert "Spain" in text and "2" in text, text
        assert pv["recommended_mission"] == "REASSURE_ALLY"
        assert pv["actions"][0]["action"] == "mission_reassure"
        assert pv["actions"][0]["counsel_first"] is True

    def test_the_boot_ally_at_the_line_is_counselled_too(self, _r11_w):
        w = _r11_w
        assert int(w.nation_relations[w._make_diplo_key("France", "Spain")]) == 40
        pv = _r11_preview(w)
        assert "Reassure Ally" in pv["recommendation"], pv["recommendation"]

    def test_the_counsel_quotes_the_figure_the_row_quotes(self, _r11_w):
        from backend.game_logic.diplomatic_dialogue import mission_effect_magnitude
        w = _r11_w
        _r11_set_rel(w, "France", "Spain", 2)
        pv = _r11_preview(w)
        eff = mission_effect_magnitude(w, "REASSURE_ALLY", "relation_change")
        row = pv["actions"][0]
        assert f"{eff:+d}" in pv["recommendation"], pv["recommendation"]
        assert f"{eff:+d}" in row["effect_text"], row["effect_text"]

    def test_a_busy_slot_says_recall_him_first(self, _r11_w):
        w = _r11_w
        _r11_set_rel(w, "France", "Spain", 2)
        _r11_busy(w, "Russia")
        pv = _r11_preview(w)
        text = pv["recommendation"]
        assert "recall Talleyrand from Russia first" in text, text
        assert "Reassure Ally" in text, text
        row = {a["action"]: a for a in pv["actions"]}["mission_reassure"]
        assert row["available"] is False and row["disabled_reason"] == "Mission already active"
        assert not pv.get("recommended_mission"), "a shut row is not promoted"

    def test_a_diplomat_abroad_with_a_proposal_says_when_he_is_home(self, _r11_w):
        w = _r11_w
        _r11_set_rel(w, "France", "Spain", 2)
        w.talleyrand_state = "IN_TRANSIT"
        pv = _r11_preview(w)
        text = pv["recommendation"]
        assert "Reassure Ally" in text and "when he is home" in text, text
        assert "Relations must improve before proposals will find purchase." not in text, text
        row = {a["action"]: a for a in pv["actions"]}["mission_reassure"]
        assert row["available"] is False and row["disabled_reason"] == "Talleyrand in transit"

    def test_make_amends_is_named_when_it_is_the_open_lever(self, _r11_w):
        w = _r11_w
        _r11_set_rel(w, "France", "Spain", 2)
        _r11_strike(w)
        _r11_busy(w, "Russia")                       # Reassure shut, Make Amends not a mission
        pv = _r11_preview(w)
        text = pv["recommendation"]
        assert "Talleyrand recommends: Make Amends" in text, text
        assert "recall Talleyrand from Russia first" in text, text
        rows = {a["action"]: a for a in pv["actions"]}
        assert rows["make_amends"]["available"] is True
        assert pv["actions"][0]["action"] == "make_amends"
        assert pv["actions"][0]["counsel_first"] is True

    def test_both_open_names_reassure_and_mentions_amends(self, _r11_w):
        w = _r11_w
        _r11_set_rel(w, "France", "Spain", 2)
        _r11_strike(w)
        text = _r11_preview(w)["recommendation"]
        assert "Talleyrand recommends: Reassure Ally" in text, text
        assert "Make Amends" in text, text

    def test_a_healthy_ally_is_counselled_as_before(self, _r11_w):
        w = _r11_w
        _r11_set_rel(w, "France", "Bavaria", 75)
        text = _r11_preview(w, "Bavaria")["recommendation"]
        assert "Reassure" not in text and "frays" not in text, text

    def test_the_warning_carries_the_cause_and_the_lever(self, _r11_w):
        w = _r11_w
        warning = _r11_warn(w)
        assert warning["message"] == (
            "Relations with Spain have slid 31 points in 3 turns — Reassure Ally in the "
            "Cabinet before the alliance lapses in 2 turns."), warning["message"]
        assert warning["turns_remaining"] == 2 and warning["lever"] == "mission_reassure"

    def test_the_warning_with_the_slot_busy_says_recall_first(self, _r11_w):
        w = _r11_w
        _r11_busy(w, "Russia")
        warning = _r11_warn(w)
        assert "recall Talleyrand from Russia first, then Reassure Ally" in warning["message"], warning
        assert warning["lever"] == ""

    def test_the_warning_names_make_amends_when_it_is_open(self, _r11_w):
        w = _r11_w
        _r11_strike(w)
        _r11_busy(w, "Russia")
        warning = _r11_warn(w)
        assert "Make Amends" in warning["message"], warning
        assert warning["lever"] == "make_amends"

    def test_a_defensive_alliance_is_told_improve_relations(self, _r11_w):
        w = _r11_w
        warning = _r11_warn(w, state="DEFENSIVE_ALLIANCE", relation=-15, history=(30, 10, -2))
        assert "Improve Relations in the Cabinet" in warning["message"], warning
        assert "defensive alliance lapses" in warning["message"], warning

    def test_a_pair_with_no_history_reads_its_standing(self, _r11_w):
        w = _r11_w
        warning = _r11_warn(w, history=())
        assert "Relations with Spain stand at 2" in warning["message"], warning["message"]
        assert "Reassure Ally in the Cabinet" in warning["message"], warning["message"]

    def test_an_ai_pair_keeps_the_old_words(self, _r11_w):
        from backend.game_logic import diplomacy as D
        w = _r11_w
        key = w._make_diplo_key("Austria", "Russia")
        w.diplomatic_states[key] = "ALLIANCE"
        w.nation_relations[key] = 0
        w.turns_below_threshold = {}
        events = []
        with _r11_quiet():
            for _ in range(3):
                events.extend(D.check_auto_downgrade(w))
        (warning,) = [e for e in events if e["type"] == "downgrade_warning"
                      and set(e["nations"]) == {"Austria", "Russia"}]
        assert warning["message"] == (
            "Relations between Austria and Russia are deteriorating. "
            "Alliance may collapse in 2 turns.")

    def test_counsel_first_prefers_the_longest_row_name(self):
        from backend.game_logic import diplomacy as D
        rows = [{"action": "make_amends", "display_name": "Make Amends"},
                {"action": "make_amends_grievance",
                 "display_name": "Make Amends for the Abandoned Alliance"}]
        out = D.counsel_first([dict(r) for r in rows],
                              "x. Talleyrand recommends: Make Amends for the Abandoned Alliance — y.", "")
        assert out[0]["action"] == "make_amends_grievance"


class TestS14EX41:
    """Sibling (the busy slot on a court that is NOT an ally): the dead end
    "Relations must improve before proposals will find purchase." stood bare
    when Improve Relations was shut by the one slot being on another errand."""

    def test_a_free_slot_reads_as_it_always_did(self, _r11_w):
        w = _r11_w
        text = _r11_preview(w, "Prussia")["recommendation"]
        assert text.startswith("No proposal would find purchase now. Talleyrand recommends: "
                               "Improve Relations mission"), text

    def test_a_busy_slot_says_recall_him_first(self, _r11_w):
        w = _r11_w
        _r11_busy(w, "Russia")
        pv = _r11_preview(w, "Prussia")
        text = pv["recommendation"]
        assert text.startswith("Relations must improve before proposals will find purchase."), text
        assert "recall Talleyrand from Russia first" in text, text
        assert not pv.get("recommended_mission"), "a shut row is not promoted"


class TestS14EX43:
    """Sibling (the dispatch's relation-threshold advisory): the morning line
    for an ally that has just slid under the line its alliance holds on read
    "Caution may be warranted." — now the lever, from the same gates."""

    def _advisory(self, w, court, state, previous, now):
        from backend.game_logic.dispatch import _build_talleyrand_report
        key = w._make_diplo_key("France", court)
        w.diplomatic_states[key] = state
        w.nation_relations[key] = now
        w.previous_nation_relations = {key: previous}
        w.proactive_suggestion_cooldowns = {}
        with _r11_quiet():
            rows = _build_talleyrand_report(w, "France")
        return [r for r in rows if r.get("trigger_type") == "relation_threshold"
                and r.get("target_nation") == court]

    def test_an_ally_under_its_line_is_told_the_lever(self, _r11_w):
        w = _r11_w
        (row,) = self._advisory(w, "Spain", "ALLIANCE", 41, 38)
        assert row["message"].startswith("Relations with Spain have deteriorated past 40 to 38."), row
        assert "Reassure Ally in the Cabinet" in row["message"], row
        assert "Caution may be warranted" not in row["message"], row

    def test_any_other_crossing_keeps_its_caution(self, _r11_w):
        w = _r11_w
        (row,) = self._advisory(w, "Spain", "ALLIANCE", 21, 19)       # past 20: not the alliance's line
        assert row["message"].endswith("Caution may be warranted."), row


# ══════════════════════════════════════════════════════════════════════════
# row12
# ══════════════════════════════════════════════════════════════════════════
# S14E-12 - the muster's "expect about N" is a mean with no floor or bad-day
# figure, and a corps priced at nothing still reads WILL JOIN.
# 
# Cause: `_build_muster_preview` prices each joiner at the probability of his
# arrival roll (PT-A2) - a mean of a lumpy outcome, printed alone - and
# `_priced_coordination` stamps the coordination bonus as if every WILL JOIN
# corps were present, a 0%-odds one included, where the resolver stamps only the
# corps that arrive.
# 
# Fix: the header also prints "certain N; a bad day (1 in 10) M", exact over the
# joiners' outcome set (2^N, N capped at 6 by highest odds) with each outcome
# priced under its OWN coordination; a corps whose arrival odds are exactly
# nothing is labelled "CANNOT ARRIVE", stands nowhere after the battle, and is
# dropped from the coordination the muster prices (the player's lead only).

_R12_P_BRAVO = (9 + 8 * 0.95) / 17     # logistics 5, aggressive: det 80
_R12_P_CHARLIE = 13 / 17               # logistics 3, aggressive: det 70


def _r12_combat():
    from backend.commands.executor import CommandExecutor
    with contextlib.redirect_stdout(io.StringIO()):
        return CommandExecutor()._combat


def _r12_board(zero=True, extra=0, co_located=False):
    """Alpha (cautious, Belgium) on Foe (Austria, Belgium) with Bravo and
    Charlie a march away; Delta (cavalry, logistics 0) cannot arrive."""
    from tests.conftest import MarshalFactory, WorldFactory
    lead = MarshalFactory.infantry(name="Alpha", location="Belgium",
                                   strength=20000, personality="cautious")
    bravo = MarshalFactory.infantry(name="Bravo", location="Paris",
                                    strength=18000, personality="aggressive")
    charlie = MarshalFactory.infantry(name="Charlie", location="Normandy",
                                      strength=15000, personality="aggressive")
    foe = MarshalFactory.enemy(name="Foe", location="Belgium", nation="Austria",
                               strength=40000, personality="cautious")
    ms = [lead, bravo, charlie, foe]
    if zero:
        ms.append(MarshalFactory.cavalry(name="Delta", location="Waterloo",
                                         strength=9000, personality="aggressive"))
    if co_located:
        ms.append(MarshalFactory.infantry(name="Echo", location="Belgium",
                                          strength=6000, personality="aggressive"))
    for i in range(extra):
        ms.append(MarshalFactory.infantry(
            name=f"Extra{i}", location=("Paris", "Normandy", "Rhineland")[i % 3],
            strength=5000 + 500 * i, personality="aggressive"))
    w = WorldFactory.with_marshals(ms)
    key = "|".join(sorted(["France", "Austria"]))
    w.diplomatic_states[key] = "WAR"
    w.war_start_turns[key] = w.current_turn
    w.marshals["Bravo"].skills["logistics"] = 5
    w.marshals["Charlie"].skills["logistics"] = 3
    if zero:
        w.marshals["Delta"].skills["logistics"] = 0
    for i in range(extra):
        w.marshals[f"Extra{i}"].skills["logistics"] = 3
    w.get_region("Normandy").terrain = "plains"
    w.get_region("Waterloo").terrain = "plains"
    w.calculate_visibility()
    return w


def _r12_muster(w, ex=None) -> dict:
    ex = ex or _r12_combat()
    with contextlib.redirect_stdout(io.StringIO()):
        return ex._build_muster_preview(
            w.marshals["Alpha"], w.marshals["Foe"], w, {"world": w})


def _r12_applied(arrivals, **board) -> int:
    """The strength the RESOLVER would mass when exactly `arrivals` come:
    relocate them to the field, stamp the coordination the way
    `_attack_reinforce_and_coordinate` does (exclude_from_adjacent = the
    arrived names, read on the field), then sum the committed term."""
    ex = _r12_combat()
    w = _r12_board(**board)
    lead = w.marshals["Alpha"]
    team = [w.marshals[n] for n in arrivals]
    for m in team:
        m.location = "Belgium"
    ex._calculate_coordination_context(
        lead, w, exclude_from_adjacent=set(arrivals), field="Belgium")
    return int(lead.strength + ex._committed_reinforcement_strength(lead, team, w))


class TestS14E12:
    def test_the_odds_are_the_resolvers_own(self):
        ex = _r12_combat()
        w = _r12_board()
        lead = w.marshals["Alpha"]
        assert ex._expected_arrival_weight(lead, w.marshals["Bravo"], w,
                                           "Belgium") == pytest.approx(_R12_P_BRAVO)
        assert ex._expected_arrival_weight(lead, w.marshals["Charlie"], w,
                                           "Belgium") == pytest.approx(_R12_P_CHARLIE)
        assert ex._expected_arrival_weight(lead, w.marshals["Delta"], w,
                                           "Belgium") == 0.0

    def test_the_floor_and_the_bad_day_are_exact_over_the_outcome_set(self):
        """Two uncertain joiners: four outcomes, each at its hand-computed
        probability, each valued under the resolver's own stamping."""
        w = _r12_board()
        pv = _r12_muster(w)
        p1, p2 = _R12_P_BRAVO, _R12_P_CHARLIE
        outcomes = {
            (): (1 - p1) * (1 - p2),
            ("Charlie",): (1 - p1) * p2,
            ("Bravo",): p1 * (1 - p2),
            ("Bravo", "Charlie"): p1 * p2,
        }
        assert sum(outcomes.values()) == pytest.approx(1.0)
        values = {k: _r12_applied(k) for k in outcomes}
        # The bad day: the least value whose cumulative probability reaches
        # one in ten, walking the outcomes from the worst up.
        cumulative, bad = 0.0, None
        for key in sorted(outcomes, key=lambda k: values[k]):
            cumulative += outcomes[key]
            if cumulative >= 0.10:
                bad = values[key]
                break
        assert values[()] == 20000                       # the lead alone
        assert values[()] < values[("Charlie",)] < values[("Bravo",)] < values[("Bravo", "Charlie")]
        assert bad == values[("Bravo",)]                  # 0.0055 + 0.018 < 0.10 <= + 0.2298
        att = pv["attacker"]
        assert att["floor_strength"] == values[()]
        assert att["bad_day_strength"] == bad
        text = _r12_combat()._format_muster_lines(pv)
        assert (f"; certain {values[()]:,}; a bad day (1 in 10) {bad:,})" in text), text

    def test_the_mean_is_not_moved(self):
        """The header's "expect about" is PT-A2's mean, untouched: it equals
        the per-corps odds times the per-corps share under the one stamp."""
        ex = _r12_combat()
        w = _r12_board(zero=False)
        pv = _r12_muster(w, ex)
        w2 = _r12_board(zero=False)
        lead = w2.marshals["Alpha"]
        team = [w2.marshals["Bravo"], w2.marshals["Charlie"]]
        with ex._priced_coordination(lead, team, w2.marshals["Foe"], [], w2, "Belgium"):
            expect = sum(
                p * ex._committed_share(lead, m, ex._pair_contribution_scale(lead, m))
                for p, m in ((_R12_P_BRAVO, team[0]), (_R12_P_CHARLIE, team[1])))
        assert pv["attacker"]["committed_strength"] == int(lead.strength + expect)

    def test_the_mean_is_byte_identical_with_the_levers_down_when_nobody_is_unreachable(
            self, monkeypatch):
        import backend.commands.combat_executor as CE
        ex = _r12_combat()
        up = _r12_muster(_r12_board(zero=False), ex)
        monkeypatch.setattr(CE, "A_CORPS_THAT_CANNOT_ARRIVE_IS_NOT_PRESENT", False)
        monkeypatch.setattr(CE, "THE_MUSTER_STATES_ITS_SPREAD", False)
        down = _r12_muster(_r12_board(zero=False), ex)
        assert up["attacker"]["committed_strength"] == down["attacker"]["committed_strength"]
        assert up["attacker"]["ceiling_strength"] == down["attacker"]["ceiling_strength"]
        assert up["odds_band"] == down["odds_band"]
        assert "floor_strength" not in down["attacker"]

    def test_a_zero_odds_corps_is_not_labelled_will_join(self):
        ex = _r12_combat()
        pv = _r12_muster(_r12_board(), ex)
        delta = next(r for r in pv["rows"] if r["marshal"] == "Delta")
        assert delta["will_join"] is True and delta["arrival_odds"] == 0
        assert delta["cannot_arrive"] is True
        assert "stands_after" not in delta                 # he stands nowhere new
        assert "order 'Delta, support Alpha'" in delta["arrival_note"]   # the lever stays
        text = ex._format_muster_lines(pv)
        assert "CANNOT ARRIVE — Delta:" in text
        assert "WILL JOIN — Delta" not in text
        assert "WILL JOIN — Bravo:" in text and "WILL JOIN — Charlie:" in text
        bravo = next(r for r in pv["rows"] if r["marshal"] == "Bravo")
        assert "cannot_arrive" not in bravo and "stands_after" in bravo

    def test_a_zero_odds_corps_does_not_inflate_the_coordination_price(self, monkeypatch):
        """Delta is cavalry among infantry: stamped present he would buy the
        combined-arms bonus for every other corps. The resolver never finds
        him on the field - he stays at Waterloo, an adjacent ally."""
        import backend.commands.combat_executor as CE
        ex = _r12_combat()
        up = _r12_muster(_r12_board(), ex)
        assert up["attacker"]["ceiling_strength"] == _r12_applied(("Bravo", "Charlie"))
        monkeypatch.setattr(CE, "A_CORPS_THAT_CANNOT_ARRIVE_IS_NOT_PRESENT", False)
        down = _r12_muster(_r12_board(), ex)
        assert down["attacker"]["committed_strength"] > up["attacker"]["committed_strength"]
        assert down["attacker"]["ceiling_strength"] > up["attacker"]["ceiling_strength"]

    def test_the_ceiling_is_the_most_the_resolver_can_reach(self):
        ex = _r12_combat()
        up = _r12_muster(_r12_board(), ex)
        assert up["attacker"]["ceiling_strength"] == _r12_applied(("Bravo", "Charlie"))
        assert up["attacker"]["committed_strength"] < up["attacker"]["ceiling_strength"]

    def test_the_floor_holds_the_men_already_on_the_field(self):
        """A corps sharing the field makes no roll: he is in every outcome."""
        w = _r12_board(co_located=True)
        pv = _r12_muster(w)
        assert pv["attacker"]["floor_strength"] == _r12_applied(("Echo",), co_located=True)
        assert pv["attacker"]["floor_strength"] > 20000

    def test_no_uncertain_corps_means_no_spread(self):
        w = _r12_board(co_located=True)
        for name in ("Bravo", "Charlie", "Delta"):
            del w.marshals[name]
        pv = _r12_muster(w)
        assert "floor_strength" not in pv["attacker"]
        assert "certain" not in _r12_combat()._format_muster_lines(pv)

    def test_the_header_prints_nothing_the_floor_cannot_back(self):
        """No floor below the mean, no clause: a header from a literal preview."""
        ex = _r12_combat()
        pv = _r12_muster(_r12_board(), ex)
        pv["attacker"]["floor_strength"] = pv["attacker"]["committed_strength"]
        assert "certain" not in ex._format_muster_lines(pv)

    def test_a_bad_day_as_bad_as_the_floor_says_so(self):
        ex = _r12_combat()
        pv = _r12_muster(_r12_board(), ex)
        pv["attacker"]["bad_day_strength"] = pv["attacker"]["floor_strength"]
        text = ex._format_muster_lines(pv)
        assert ", and a bad day (1 in 10) is no better)" in text

    def test_the_outcome_spread_by_hand(self):
        ex = _r12_combat()
        # Half the days the lead stands alone: the floor is 10, and so is one day in ten.
        assert ex._outcome_spread([(0.5, 10.0), (0.4, 30.0), (0.1, 100.0)], 0.10) == (10.0, 10.0)
        # 5% at 10, 5% at 20, 90% at 100: one day in ten is 20 or worse.
        assert ex._outcome_spread([(0.05, 10.0), (0.05, 20.0), (0.9, 100.0)], 0.10) == (10.0, 20.0)
        # A 3% disaster is a floor, not a bad day.
        assert ex._outcome_spread([(0.03, 5.0), (0.07, 40.0), (0.9, 90.0)], 0.10) == (5.0, 40.0)
        # An outcome that cannot happen is no floor.
        assert ex._outcome_spread([(0.0, 1.0), (1.0, 50.0)], 0.10) == (50.0, 50.0)

    def test_more_than_six_uncertain_corps_withhold_the_bad_day_and_keep_the_floor(self):
        ex = _r12_combat()
        # Two named + 5 extras = 7 uncertain: over the cap.
        w = _r12_board(zero=False, extra=5)
        pv = _r12_muster(w, ex)
        assert "floor_strength" in pv["attacker"]
        assert "bad_day_strength" not in pv["attacker"]
        assert pv["attacker"]["floor_strength"] == 20000    # all absent: the lead alone
        text = ex._format_muster_lines(pv)
        assert "; certain 20,000)" in text and "bad day" not in text
        # Exactly six is still claimed.
        pv6 = _r12_muster(_r12_board(zero=False, extra=4), ex)
        assert "bad_day_strength" in pv6["attacker"]

    def test_the_what_if_desk_prints_the_same_header(self):
        """The shipped 1805 board: the what-if is the order's own render."""
        import json
        from pathlib import Path
        from backend.ai.question_desk import _answer_what_if
        from backend.models.world_state import WorldState
        scenario = (Path(__file__).resolve().parents[1] / "godot-client"
                    / "project-sovereign" / "assets" / "maps" / "europe_1805.json")
        with contextlib.redirect_stdout(io.StringIO()):
            w = WorldState.from_scenario(str(scenario))
        w = WorldState.from_dict(json.loads(json.dumps(w.to_dict(), default=str)))
        w.get_marshal("Mack").strength = 52000
        w.calculate_visibility()
        ex = _r12_combat()
        with contextlib.redirect_stdout(io.StringIO()):
            pv = ex._build_muster_preview(w.get_marshal("Davout"),
                                          w.get_marshal("Mack"), w, {"world": w})
            answer = _answer_what_if(w, "France", "Mack", "Davout")
        assert pv["attacker"]["floor_strength"] < pv["attacker"]["committed_strength"]
        m = re.search(r"certain ([\d,]+); a bad day \(1 in 10\) ([\d,]+)\)", answer)
        assert m, answer
        assert int(m.group(1).replace(",", "")) == pv["attacker"]["floor_strength"]
        assert int(m.group(2).replace(",", "")) == pv["attacker"]["bad_day_strength"]

    def test_the_ais_reads_are_untouched(self, monkeypatch):
        """GR5's named difference: the filter is the player's lead's. An
        Austrian lead's `muster_odds` (the jealousy P3.9 rung) reads the
        shipped arithmetic, byte for byte, with the lever up or down."""
        import backend.commands.combat_executor as CE
        from tests.conftest import MarshalFactory, WorldFactory

        def austrian():
            lead = MarshalFactory.enemy(name="Karl", location="Belgium", nation="Austria",
                                        strength=20000, personality="cautious")
            j = MarshalFactory.enemy(name="Jodl", location="Paris", nation="Austria",
                                     strength=18000, personality="aggressive")
            z = MarshalFactory.enemy(name="Zeta", location="Waterloo", nation="Austria",
                                     strength=9000, personality="aggressive")
            z.cavalry = True
            fr = MarshalFactory.infantry(name="Foe", location="Belgium", strength=30000)
            w = WorldFactory.with_marshals([lead, j, z, fr])
            key = "|".join(sorted(["France", "Austria"]))
            w.diplomatic_states[key] = "WAR"
            w.war_start_turns[key] = w.current_turn
            j.skills["logistics"] = 5
            z.skills["logistics"] = 0
            w.get_region("Waterloo").terrain = "plains"
            w.calculate_visibility()
            return w

        ex = _r12_combat()
        w = austrian()
        assert ex._expected_arrival_weight(w.marshals["Karl"], w.marshals["Zeta"], w,
                                           "Belgium") == 0.0
        with contextlib.redirect_stdout(io.StringIO()):
            up = ex.muster_odds(w.marshals["Karl"], w.marshals["Foe"], w)
        monkeypatch.setattr(CE, "A_CORPS_THAT_CANNOT_ARRIVE_IS_NOT_PRESENT", False)
        w = austrian()
        with contextlib.redirect_stdout(io.StringIO()):
            down = ex.muster_odds(w.marshals["Karl"], w.marshals["Foe"], w)
        assert up == down

    def test_the_objections_totals_skip_the_spread_and_do_not_move(self):
        """`muster_expected_totals` (DDB-19) takes only the totals: it asks
        for no spread, and the totals are the preview's own."""
        from backend.commands.objection_v2 import muster_expected_totals
        ex = _r12_combat()
        w = _r12_board()
        pv = _r12_muster(w, ex)
        with contextlib.redirect_stdout(io.StringIO()):
            lean = ex._build_muster_preview(w.marshals["Alpha"], w.marshals["Foe"], w,
                                            {"world": w}, with_spread=False)
            totals = muster_expected_totals(w.marshals["Alpha"], w.marshals["Foe"], w)
        assert "floor_strength" not in lean["attacker"]
        assert totals == (pv["attacker"]["committed_strength"],
                          pv["target"]["committed_strength"])

    def test_the_players_gate_reads_the_screens_context(self):
        """`muster_odds` (the gate) and the preview (the screen) agree on
        the board with a corps that cannot arrive."""
        ex = _r12_combat()
        w = _r12_board()
        pv = _r12_muster(w, ex)
        with contextlib.redirect_stdout(io.StringIO()):
            odds = ex.muster_odds(w.marshals["Alpha"], w.marshals["Foe"], w)
        assert odds["band"] == pv["odds_band"]
        assert int(w.marshals["Alpha"].strength + odds["committed_attacker"]) == \
            pv["attacker"]["committed_strength"]

    def test_the_state_is_restored(self):
        """The preview prices hypotheticals; it leaves nobody moved or stamped."""
        ex = _r12_combat()
        w = _r12_board()
        before = {n: (m.location, m.total_coordination_attack_bonus
                      if hasattr(m, "total_coordination_attack_bonus") else None,
                      getattr(m, "sovereign_presence", None))
                  for n, m in w.marshals.items()}
        _r12_muster(w, ex)
        after = {n: (m.location, m.total_coordination_attack_bonus
                     if hasattr(m, "total_coordination_attack_bonus") else None,
                     getattr(m, "sovereign_presence", None))
                 for n, m in w.marshals.items()}
        assert before == after


class TestS14EX64:
    """Sibling: the CR-5 bad-odds modal's Berthier addendum named a corps that
    cannot arrive among the men who "would answer the guns"."""

    def test_the_staffs_note_names_only_corps_that_can_arrive(self):
        ex = _r12_combat()
        w = _r12_board()
        note = ex._bad_odds_muster_note(w.marshals["Alpha"], w.marshals["Foe"], w)
        assert note
        assert "Bravo" in note and "Charlie" in note
        assert "Delta" not in note

    def test_a_note_with_only_unreachable_corps_is_silent(self):
        ex = _r12_combat()
        w = _r12_board()
        del w.marshals["Bravo"], w.marshals["Charlie"]
        assert ex._bad_odds_muster_note(w.marshals["Alpha"], w.marshals["Foe"], w) == ""


class TestS14EX65:
    """Sibling: the supply and materiel quotes billed the bodies of a corps
    that cannot arrive as standing at the field."""

    def test_the_supply_quote_bills_only_the_bodies_that_can_stand_there(self):
        w = _r12_board()
        pv = _r12_muster(w)
        # Alpha 20,000 + Bravo 18,000 + Charlie 15,000; Delta's 9,000 never come.
        assert pv["supply"]["bodies"] == 53000
        assert pv["supply"]["corps"] == 3

    def test_the_old_reading_billed_him(self, monkeypatch):
        import backend.commands.combat_executor as CE
        monkeypatch.setattr(CE, "A_CORPS_THAT_CANNOT_ARRIVE_IS_NOT_PRESENT", False)
        pv = _r12_muster(_r12_board())
        assert pv["supply"]["bodies"] == 62000

    def test_the_materiel_quote_musters_the_same_men(self, monkeypatch):
        w = _r12_board()
        w.sovereign_map = "europe"
        pv = _r12_muster(w)
        assert "of the 53,000 we muster" in pv["materiel_note"]


# ══════════════════════════════════════════════════════════════════════════
# row13
# ══════════════════════════════════════════════════════════════════════════
# S14E-13 (Pre-Deploy S14f part 1; `docs/BUG_FIXES.md` §S14E) — a march that
# takes the Descent's camp out of its provinces resets two turns of staging and
# no order says so.
# 
# The cause: the camp is the men standing in `camp_provinces` (Flanders, Artois,
# Normandy, Brittany) at the turn-end tick (`naval.camp_strength`,
# `_camp_tick`), but Flanders borders Picardy, not Artois, so a march from
# Flanders to Normandy steps out of the camp at issue — and the march reply, the
# plain move's reply and the confirm card's quote said nothing (only
# `supply_warning_line` rode them); the camp line named the four provinces only
# in its "No army is staged" branches.
# 
# The fix: `naval.camp_leave_line(world, marshal, road, origin)` — read off the
# camp's own predicate (shown == applied) — rides the strategic march reply, the
# plain move reply, the standing march's turn report (S14E-XJ1) and the quote
# (`order_quotes` field `camp`, read by the confirm card, the province panel and
# Berthier's desk); the "Staged:" branch of `camp_line` names the four
# provinces. The map is NOT tinted: the row calls that a design call and it is
# left to the user (BUG_FIXES S14E-13 stays the owner of the decision).
# 
# Every board is the shipped 1805 campaign.

_R13_REPO = Path(__file__).resolve().parents[1]
_R13_SCENARIO = (_R13_REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "europe_1805.json")
_R13_SCRIPTS = _R13_REPO / "godot-client" / "project-sovereign" / "scripts"

_R13_LINE = ("Picardy lies outside the camp — this takes 46,500 men out of it; "
             "the 2-turn count resets at the turn's end.")


@pytest.fixture(scope="module")
def _r13_boot():
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(_R13_SCENARIO))


@pytest.fixture
def _r13_world(_r13_boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(_r13_boot.to_dict(), default=str)))


@pytest.fixture
def _r13_client(monkeypatch):
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _r13_cmd(c, text: str) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return c.post("/command", json={"command": text}).json()


def _r13_camp_corps(w, at: str, men: int = 46500, name: str = "Soult", turns: int = 2):
    """The sea #5's shape: one corps the size of the whole camp standing in
    `at`, the rest of France parked where the boot leaves them."""
    from backend.game_logic import naval as NV
    m = w.marshals[name]
    m.location = at
    m.strength = men
    m.strategic_order = None
    w._build_marshal_index()
    NV.get_fleet(w, "France")["camp_turns"] = turns
    return m


def _r13_src(name: str) -> str:
    return (_R13_SCRIPTS / name).read_text(encoding="utf-8")


class TestS14E13:
    def test_the_line_names_the_stop_and_the_men(self, _r13_world):
        from backend.game_logic import naval as NV
        m = _r13_camp_corps(_r13_world, "Flanders")
        assert (NV.camp_leave_line(_r13_world, m, ["Picardy", "Artois", "Normandy"])
                == _R13_LINE)

    def test_a_march_inside_the_camp_says_nothing(self, _r13_world):
        from backend.game_logic import naval as NV
        m = _r13_camp_corps(_r13_world, "Artois")
        assert "Normandy" in _r13_world.get_region("Artois").adjacent_regions
        assert NV.camp_leave_line(_r13_world, m, ["Normandy"]) == ""

    def test_a_corps_outside_the_camp_marching_in_or_around_says_nothing(self, _r13_world):
        from backend.game_logic import naval as NV
        m = _r13_camp_corps(_r13_world, "Picardy")
        assert NV.camp_leave_line(_r13_world, m, ["Artois", "Normandy"]) == ""
        assert NV.camp_leave_line(_r13_world, m, ["Orleanais"]) == ""

    def test_the_quote_carries_it(self, _r13_world):
        from backend.commands.order_quotes import march_quote
        m = _r13_camp_corps(_r13_world, "Flanders")
        q = march_quote(_r13_world, m, "Normandy")
        assert q["ok"], q
        assert q["road"][0] == "Picardy"
        assert q.get("camp") == _R13_LINE, q

    def test_the_quote_inside_the_camp_is_blank(self, _r13_world):
        from backend.commands.order_quotes import march_quote
        m = _r13_camp_corps(_r13_world, "Artois")
        q = march_quote(_r13_world, m, "Normandy")
        assert q["ok"], q
        assert q.get("camp", None) == "", q

    def test_the_support_and_follow_quotes_carry_it_too(self, _r13_world):
        from backend.commands.order_quotes import support_quote
        m = _r13_camp_corps(_r13_world, "Flanders")
        ally = _r13_world.marshals["Ney"]
        ally.location = "Paris"
        _r13_world._build_marshal_index()
        q = support_quote(_r13_world, m, ally)
        assert q["ok"], q
        assert q.get("camp", "").startswith("Picardy lies outside the camp"), q

    def test_berthiers_desk_says_it_too(self, _r13_world):
        from backend.ai.state_desk import _answer_march_cost
        _r13_camp_corps(_r13_world, "Flanders")
        answer = _answer_march_cost(_r13_world, "Normandy", "Soult")
        assert _R13_LINE in answer, answer

    def test_the_march_reply_carries_it(self, _r13_client):
        c, w = _r13_client
        m = _r13_camp_corps(w, "Flanders")
        r = _r13_cmd(c, "Soult, march to Normandy")
        assert m.location == "Picardy", r.get("message")
        assert _R13_LINE in r["message"], r["message"]

    def test_the_march_reply_inside_the_camp_says_nothing(self, _r13_client):
        c, w = _r13_client
        m = _r13_camp_corps(w, "Artois")
        r = _r13_cmd(c, "Soult, march to Normandy")
        assert m.location == "Normandy", r.get("message")
        assert "outside the camp" not in r["message"], r["message"]

    def test_the_plain_move_reply_carries_it(self, _r13_client):
        c, w = _r13_client
        m = _r13_camp_corps(w, "Flanders")
        r = _r13_cmd(c, "Soult, move to Picardy")
        assert m.location == "Picardy", r.get("message")
        assert _R13_LINE in r["message"], r["message"]

    def test_the_staged_line_names_the_four_provinces(self, _r13_world):
        from backend.game_logic import naval as NV
        _r13_camp_corps(_r13_world, "Flanders")
        line = NV.camp_line(_r13_world, "France")
        assert line.startswith("Staged: 46,500 men have stood 2 turns in the camp ")
        assert "(Flanders, Artois, Normandy, Brittany)" in line, line
        assert "marching out of those provinces resets the count" in line, line

    def test_shown_is_applied_the_tick_resets_exactly_when_the_line_is_shown(self, _r13_world):
        """The line and `_camp_tick` read one predicate: where the line is
        shown the count falls to 0 at the turn's end; where it is blank the
        count keeps climbing."""
        from backend.game_logic import naval as NV
        w = _r13_world
        m = _r13_camp_corps(w, "Flanders")
        line = NV.camp_leave_line(w, m, ["Picardy", "Artois", "Normandy"])
        assert line
        m.location = "Picardy"                       # the first step, taken
        assert NV.camp_leave_line(w, m, ["Picardy"], origin="Flanders") == line
        NV._camp_tick(w)
        assert NV.get_fleet(w, "France")["camp_turns"] == 0
        # ... and inside the camp the same corps keeps the count
        m2 = _r13_camp_corps(w, "Artois")
        assert NV.camp_leave_line(w, m2, ["Normandy"]) == ""
        m2.location = "Normandy"
        NV._camp_tick(w)
        assert NV.get_fleet(w, "France")["camp_turns"] == 3

    def test_a_camp_that_survives_the_leaving_says_nothing(self, _r13_world):
        """Another corps holds the 40,000 in the camp: the count is not
        touched, so nothing is said (the line is a price, not a reminder)."""
        from backend.game_logic import naval as NV
        w = _r13_world
        big = _r13_camp_corps(w, "Artois", men=45000, name="Massena")
        small = _r13_camp_corps(w, "Flanders", men=6000, name="Soult")
        assert NV.camp_strength(w, "France") == 51000
        assert NV.camp_leave_line(w, small, ["Picardy"]) == ""
        # ... but the big corps leaving leaves 6,000: the count falls
        line = NV.camp_leave_line(w, big, ["Paris"])
        assert line.startswith("Paris lies outside the camp — this takes 45,000 men"), line

    def test_a_count_not_yet_begun_is_worded_for_it(self, _r13_world):
        from backend.game_logic import naval as NV
        m = _r13_camp_corps(_r13_world, "Flanders", turns=0)
        line = NV.camp_leave_line(_r13_world, m, ["Picardy"])
        assert line == ("Picardy lies outside the camp — this takes 46,500 men out "
                        "of it; no turn counts toward staging while they stand there.")

    def test_at_peace_with_the_island_there_is_nothing_to_reset(self, _r13_world):
        from backend.game_logic import diplomacy as D
        from backend.game_logic import naval as NV
        with contextlib.redirect_stdout(io.StringIO()):
            D.set_diplomatic_state(_r13_world, "France", "Britain", "PEACE", "peace_ratified")
        m = _r13_camp_corps(_r13_world, "Flanders", turns=0)
        assert NV.camp_leave_line(_r13_world, m, ["Picardy"]) == ""

    def test_a_corps_under_the_camp_size_says_nothing(self, _r13_world):
        from backend.game_logic import naval as NV
        m = _r13_camp_corps(_r13_world, "Flanders", men=20000, turns=0)
        assert NV.camp_leave_line(_r13_world, m, ["Picardy"]) == ""

    def test_only_the_players_corps_are_told(self, _r13_world):
        from backend.game_logic import naval as NV
        m = _r13_camp_corps(_r13_world, "Flanders")
        _r13_world.player_nation = "Austria"
        assert NV.camp_leave_line(_r13_world, m, ["Picardy"]) == ""

    def test_the_client_reads_the_field(self):
        card = _r13_src("order_confirm_card.gd")
        panel = _r13_src("region_panel.gd")
        assert 'q.get("camp"' in card, "the confirm card prints the camp line"
        assert 'q.get("camp"' in panel, "the province panel's chip notes carry it"


class TestS14EX53:
    """S14E-XJ1 (the sweep): a STANDING march's step out of the camp is the
    same silent undoing — the turn report said only "marches to X"."""

    def test_the_standing_marchs_step_out_of_the_camp_is_told(self, _r13_world):
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.models.marshal import StrategicOrder
        w = _r13_world
        m = _r13_camp_corps(w, "Artois")
        m.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Berry", target_type="region",
            started_turn=int(w.current_turn) - 1, original_command="march to Berry",
            path=["Paris", "Berry"], issued_turn=int(w.current_turn) - 1)
        proc = StrategicOrderProcessor(CommandExecutor())
        with contextlib.redirect_stdout(io.StringIO()):
            report = proc._execute_strategic_turn(m, w, {"world": w})
        assert m.location == "Paris", report
        assert ("Paris lies outside the camp — this takes 46,500 men out of it; "
                "the 2-turn count resets at the turn's end.") in report["message"], report

    def test_a_standing_step_inside_the_camp_says_nothing(self, _r13_world):
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.models.marshal import StrategicOrder
        w = _r13_world
        m = _r13_camp_corps(w, "Artois")
        m.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Paris", target_type="region",
            started_turn=int(w.current_turn) - 1, original_command="march to Paris",
            path=["Normandy", "Paris"], issued_turn=int(w.current_turn) - 1)
        proc = StrategicOrderProcessor(CommandExecutor())
        with contextlib.redirect_stdout(io.StringIO()):
            report = proc._execute_strategic_turn(m, w, {"world": w})
        assert m.location == "Normandy", report
        assert "outside the camp" not in report["message"], report


# ══════════════════════════════════════════════════════════════════════════
# row14
# ══════════════════════════════════════════════════════════════════════════
# S14E-14 (Pre-Deploy S14f part 1; `docs/BUG_FIXES.md` §S14E) — the Grand
# Diversion's card prices the window and the wait but not the fleet a failure
# loses.
# 
# The cause: a caught diversion is `resolve_diversion`'s failure arm →
# `resolve_fleet_action` at `diversion_failure_readiness` — against Britain's
# sail and Russia's the ratio is about 2, a decisive defeat that takes about
# half of every pooled fleet — and no surface quoted it (the card, the chip
# note, the Admiralty's terms and the help stopped at "caught coming home and
# fights at readiness 60"; the expedition's card prices its own failure).
# 
# The fix: `naval.fleet_action_forecast` — built on the resolver's own
# arithmetic (`_fleet_action_odds`, `combined_effective`, the `FLEET_ACTION_*`
# constants, `_side_loss_counts`), pure, at the failure arm's readiness —
# and `naval.diversion_failure_clause`, ONE sentence read by the card, the chip
# note, the third term's `detail` on the Admiralty's ledger and the help.
# The sweep's S14E-XJ2: an INTERCEPTED expedition fights the same fleet action,
# and its card priced only the corps (`naval.expedition_intercept_clause`).
# 
# Every board is the shipped 1805 campaign.

_R14_REPO = Path(__file__).resolve().parents[1]
_R14_SCENARIO = (_R14_REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "europe_1805.json")
_R14_SCRIPTS = _R14_REPO / "godot-client" / "project-sovereign" / "scripts"

_R14_BOOT_CLAUSE = (
    "If she is caught she meets Britain's 110 effective against our 49 — a "
    "decisive defeat is the likely result: about half of every pooled fleet "
    "(France 45→~20, Spain 30→~14, Holland 12→~5) is lost; Britain's side "
    "loses ~4%.")


@pytest.fixture(scope="module")
def _r14_boot():
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(_R14_SCENARIO))


def _r14_copy(world):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))


@pytest.fixture
def _r14_world(_r14_boot):
    return _r14_copy(_r14_boot)


@pytest.fixture
def _r14_client(monkeypatch):
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _r14_cmd(c, text: str) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return c.post("/command", json={"command": text}).json()


def _r14_caught(world, monkeypatch=None, jitter_zero: bool = False) -> dict:
    """Throw the diversion on a COPY with the success roll forced to fail —
    the real failure arm, the real resolver. Returns the diversion's result."""
    from backend.game_logic import naval as NV
    copy = _r14_copy(world)
    if monkeypatch is not None:
        monkeypatch.setattr(NV, "_pct_roll", lambda *_a, **_k: False)
        if jitter_zero:
            import backend.game_logic.campaign_variance as CV
            real = CV.seeded_int
            monkeypatch.setattr(
                CV, "seeded_int",
                lambda seed, ns, lo, hi, *a, **k: 0 if str(ns).startswith("naval::action::")
                else real(seed, ns, lo, hi, *a, **k))
    with contextlib.redirect_stdout(io.StringIO()):
        return NV.resolve_diversion(copy, "France")


class TestS14E14:
    def test_the_boot_forecast_reads_the_failure_readiness(self, _r14_world):
        from backend.game_logic import naval as NV
        rec = NV.get_fleet(_r14_world, "France")
        assert NV.diversion_failure_readiness(rec) == 60
        f = NV.diversion_failure_forecast(_r14_world, "France")
        assert f["attacker_readiness"] == 60
        assert f["loser"] == "France" and f["decisive"] is True
        assert (f["attacker_effective"], f["defender_effective"]) == (49, 110)
        # PURE: the record kept its readiness.
        assert NV.get_fleet(_r14_world, "France")["readiness"] == 70

    def test_the_forecast_equals_the_resolvers_losses(self, _r14_world, monkeypatch):
        """Shown == applied: at the same readiness, with the seeded jitter at
        its centre, the resolver's ship losses ARE the forecast's — fleet by
        fleet, both sides."""
        from backend.game_logic import naval as NV
        forecast = NV.diversion_failure_forecast(_r14_world, "France")
        result = _r14_caught(_r14_world, monkeypatch, jitter_zero=True)
        action = result["fleet_action"]
        assert result["window"] is False
        assert action["loser"] == forecast["loser"]
        assert action["decisive"] is forecast["decisive"]
        for side in ("attacker_side", "defender_side"):
            got = action["losses"][forecast[side]["nation"]]
            want = {f["nation"]: f["lost"] for f in forecast[side]["fleets"]}
            assert got == want, (side, got, want)

    @pytest.mark.parametrize("turn", [1, 2, 3, 5, 8, 13])
    def test_with_the_real_jitter_the_resolver_stays_inside_the_band(
            self, _r14_boot, monkeypatch, turn):
        """The seeded roll moves the loser's fraction ±10% (relative) — the
        forecast is the centre of that band and the verdict never moves."""
        from backend.game_logic import naval as NV
        world = _r14_copy(_r14_boot)
        world.current_turn = turn
        forecast = NV.diversion_failure_forecast(world, "France")
        action = _r14_caught(world, monkeypatch)["fleet_action"]
        assert action["decisive"] is forecast["decisive"]
        assert action["loser"] == forecast["loser"]
        for f in forecast["attacker_side"]["fleets"]:
            got = action["losses"]["France"][f["nation"]]
            slack = f["ships"] * (forecast["attacker_side"]["fraction_pct"] / 100.0) * 0.10 + 1
            assert abs(got - f["lost"]) <= slack, (f, got)

    def test_the_forecast_changes_with_the_fleet_she_would_meet(self, _r14_world):
        """It reads the board, not a constant: a Britain at half her sail is
        a different forecast."""
        from backend.game_logic import naval as NV
        before = NV.diversion_failure_forecast(_r14_world, "France")
        NV.get_fleet(_r14_world, "Britain")["ships"] = 30
        after = NV.diversion_failure_forecast(_r14_world, "France")
        assert after["defender_effective"] < before["defender_effective"]
        assert after["attacker_side"]["fraction_pct"] < before["attacker_side"]["fraction_pct"]

    def test_a_fleet_that_would_win_the_action_is_told_so(self, _r14_world):
        from backend.game_logic import naval as NV
        NV.get_fleet(_r14_world, "Britain")["ships"] = 10
        clause = NV.diversion_failure_clause(_r14_world, "France")
        assert "she carries the action" in clause, clause
        assert "a decisive defeat" not in clause

    def test_the_boot_clause(self, _r14_world):
        from backend.game_logic import naval as NV
        assert NV.diversion_failure_clause(_r14_world, "France") == _R14_BOOT_CLAUSE

    def test_the_card_carries_it(self, _r14_client):
        c, w = _r14_client
        r = _r14_cmd(c, "order the diversion")
        assert r.get("naval_confirm"), r
        assert _R14_BOOT_CLAUSE in r["message"], r["message"]
        assert "fights at readiness 60" in r["message"]
        # the old terms stand beside it
        assert "times in 100" in r["message"] and "Sail? (yes / no)" in r["message"]

    def test_the_chip_note_carries_it(self, _r14_world):
        from backend.game_logic import naval as NV
        chip = [c for c in NV.build_admiralty_report(_r14_world)["chips"]
                if c["command"] == "order the diversion"][0]
        assert chip["enabled"] is True
        assert _R14_BOOT_CLAUSE[0].lower() + _R14_BOOT_CLAUSE[1:] in chip["note"], chip["note"]
        # the odds, the wait and the window forecast survive
        assert "in 100 at readiness" in chip["note"]
        assert "opens London-Normandy" in chip["note"]

    def test_the_terms_carry_it_as_a_detail_never_a_fourth_gate(self, _r14_world):
        from backend.game_logic import naval as NV
        report = NV.build_admiralty_report(_r14_world)
        terms = report["diversion_terms"]
        assert len(terms) == 3
        assert terms[2]["detail"] == _R14_BOOT_CLAUSE
        assert terms == NV.diversion_terms_for(_r14_world, "France")
        assert "detail" not in terms[0] and "detail" not in terms[1]
        assert report["diversion_available"] is True

    def test_the_help_carries_it(self, _r14_world):
        from backend.commands.meta_executor import MetaExecutor
        text = MetaExecutor(None)._execute_help({}, {"world": _r14_world})["message"]
        assert "The Grand Diversion (1 AP)" in text
        flat = " ".join(text.split())    # the help is hand-wrapped
        assert "Caught, she fights the action at her readiness less 10" in flat
        assert "loses 20% of every pooled fleet, up to 55% in a decisive defeat" in flat
        assert _R14_BOOT_CLAUSE in flat, flat[flat.find("Caught, she fights"):][:700]

    def test_the_help_without_a_board_keeps_the_rule(self):
        from backend.commands.meta_executor import MetaExecutor
        text = MetaExecutor(None)._execute_help({}, {})["message"]
        flat = " ".join(text.split())
        assert "Caught, she fights the action at her readiness less 10" in flat
        assert "If she is caught" not in flat

    def test_no_fleet_or_no_hostile_no_clause(self, _r14_world):
        from backend.game_logic import naval as NV
        NV.get_fleet(_r14_world, "France")["ships"] = 0
        assert NV.diversion_failure_clause(_r14_world, "France") == ""
        assert NV.diversion_failure_forecast(_r14_world, "France") is None

    def test_the_ledger_renders_the_detail(self):
        src = (_R14_SCRIPTS / "strategic_ledger.gd").read_text(encoding="utf-8")
        assert 'term.get("detail", "")' in src
        assert "div_detail" in src

    def test_the_resolver_is_unmoved_by_the_forecast(self, _r14_world, monkeypatch):
        """Asking for the forecast writes nothing: the same throw on a world
        that was forecast first and one that was not leaves identical fleets."""
        from backend.game_logic import naval as NV
        fresh = _r14_copy(_r14_world)
        NV.diversion_failure_forecast(_r14_world, "France")
        NV.diversion_failure_clause(_r14_world, "France")
        NV.build_admiralty_report(_r14_world)
        a = _r14_caught(_r14_world, monkeypatch)
        b = _r14_caught(fresh, monkeypatch)
        assert a["fleet_action"]["losses"] == b["fleet_action"]["losses"]


class TestS14EX54:
    """S14E-XJ2 (the sweep): an INTERCEPTED expedition ALSO brings the fleet
    to action (`resolve_expedition`'s intercept arm → `resolve_fleet_action`
    with the coverer, at the fleet's CURRENT readiness) and its card priced
    only the corps' 30%."""

    @staticmethod
    def _soult_at_brittany(world, men: int = 10000):
        s = world.marshals["Soult"]
        s.location = "Brittany"
        s.strength = men
        s.strategic_order = None
        world._build_marshal_index()
        return s

    @staticmethod
    def _card(world, target: str = "Munster") -> dict:
        from backend.commands.executor import CommandExecutor
        with contextlib.redirect_stdout(io.StringIO()):
            return CommandExecutor()._naval._execute_naval_expedition(
                {"marshal": "Soult", "action": "naval_expedition", "target": target,
                 "raw_command": f"land Soult in {target}"}, {"world": world})

    def test_the_boot_watch_is_an_interception(self, _r14_world):
        """Every watched landing on the boot board is decisive coverage (the
        ratio is 1.86): a failed run is an interception, not a turn-back."""
        from backend.game_logic import naval as NV
        quote = NV.expedition_slip_odds(_r14_world, "France", "Munster", 10000)
        assert quote["coverer"] == "Britain"
        assert NV.expedition_intercepts(_r14_world, "France", quote) is True

    def test_the_card_prices_the_fleet_as_well_as_the_corps(self, _r14_world):
        from backend.game_logic import naval as NV
        self._soult_at_brittany(_r14_world)
        r = self._card(_r14_world)
        assert r.get("naval_confirm"), r
        forecast = NV.fleet_action_forecast(_r14_world, "France", "Britain")
        want = "If she is intercepted " + NV.fleet_action_clause(forecast)
        assert "A failed run costs ~30% of the corps if intercepted" in r["message"]
        assert want in r["message"], r["message"]
        assert "a decisive defeat is the likely result" in want
        # at the fleet's CURRENT readiness — the intercept arm docks no 10
        assert forecast["attacker_readiness"] == 70

    def test_the_forecast_equals_the_interception_arm(self, _r14_world, monkeypatch):
        """Shown == applied for the sibling too: the resolver's intercepted
        run takes exactly what the card quoted (jitter at its centre)."""
        import backend.game_logic.campaign_variance as CV
        from backend.game_logic import naval as NV
        soult = self._soult_at_brittany(_r14_world)
        forecast = NV.fleet_action_forecast(_r14_world, "France", "Britain")
        world = _r14_copy(_r14_world)
        soult = world.marshals["Soult"]
        monkeypatch.setattr(NV, "_pct_roll", lambda *_a, **_k: False)
        real = CV.seeded_int
        monkeypatch.setattr(
            CV, "seeded_int",
            lambda seed, ns, lo, hi, *a, **k: 0 if str(ns).startswith("naval::action::")
            else real(seed, ns, lo, hi, *a, **k))
        with contextlib.redirect_stdout(io.StringIO()):
            result = NV.resolve_expedition(world, soult, "Munster")
        assert result["intercepted"] is True
        got = result["fleet_action"]["losses"]["France"]
        assert got == {f["nation"]: f["lost"] for f in forecast["attacker_side"]["fleets"]}

    def test_a_run_that_cannot_be_intercepted_says_nothing_extra(self, _r14_world):
        from backend.game_logic import naval as NV
        NV.get_fleet(_r14_world, "Britain")["ships"] = 40
        self._soult_at_brittany(_r14_world)
        quote = NV.expedition_slip_odds(_r14_world, "France", "Munster", 10000)
        assert quote["coverer"] and not NV.expedition_intercepts(_r14_world, "France", quote)
        r = self._card(_r14_world)
        assert r.get("naval_confirm"), r
        assert "If she is intercepted" not in r["message"], r["message"]
        assert NV.expedition_intercept_clause(_r14_world, "France", "Munster", 10000) == ""

    def test_the_admiralty_notes_name_the_rule(self, _r14_world):
        from backend.game_logic import naval as NV
        notes = " ".join(NV.build_admiralty_report(_r14_world)["expedition_notes"])
        assert "an intercepted run also brings the fleet to action" in notes
        assert NV.fleet_action_rule_phrase() in notes


class TestS14EX55:
    """S14E-XJ3 (the sweep): Berthier's desk answers "what does the diversion
    risk" with a rule that said "lost, the fleet pays at sea" and no figure."""

    def test_the_desks_rule_names_the_bill(self, _r14_client):
        c, _w = _r14_client
        for question in ("what does the diversion risk",
                         "what are the odds of the diversion"):
            r = _r14_cmd(c, question)
            assert "lost, the fleet pays at sea." in r["message"], r["message"]
            assert _R14_BOOT_CLAUSE in r["message"], r["message"]

    def test_the_rule_without_a_fleet_keeps_its_old_words(self, _r14_world):
        from backend.ai.state_desk import _rule_text
        from backend.game_logic import naval as NV
        NV.get_fleet(_r14_world, "France")["ships"] = 0
        text = _rule_text(_r14_world, "diversion", False)
        assert text.endswith("lost, the fleet pays at sea.")


# ══════════════════════════════════════════════════════════════════════════
# row15
# ══════════════════════════════════════════════════════════════════════════
# S14E-15 (P2, pillar naval) — the Free Ireland road's next step lived on the
# Formable Nations page alone (Pre-Deploy S14f part 1; `docs/BUG_FIXES.md`
# §S14E-15, the sea #12).
# 
# Cause: the road to a carved state (Ireland needs Ulster AND Munster, held by
# the carver's bloc, at a table, while the war runs) was surfaced on the
# Formables page, the table's "Erect" row and the first-open line — and at none
# of the points of ACTION: not the landing or the capture reply, not the Munster
# panel, not the Admiralty, not the war card ("Munster stays ours"), not the
# offer or the review that closed the road with a peace.
# 
# Fix: ONE builder, `formations.road_notes(world)`, over the formables the
# player's bloc has begun but not finished (some of a template's provinces, not
# all), feeding the capture question and reply, the landing result, the region
# payload (`road_note`), the Admiralty's notes and its chip ranking, the war
# card's held line and the offer / review (`road_peace_lines`). Player-only
# display; nothing is added when no road is begun.

_r15_scenario = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps" / "europe_1805.json")

_r15_ireland = ("Ireland needs Ulster too — it lies a march from Munster; "
                "carve at a table while the war with Britain runs")


@pytest.fixture(scope="module")
def _r15_boot():
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(_r15_scenario))


@pytest.fixture
def _r15_world(_r15_boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(
        json.loads(json.dumps(_r15_boot.to_dict(), default=str)))


def _r15_hold(world, *provinces, nation="France"):
    for province in provinces:
        world.regions[province].controller = nation
    world.invalidate_active_nations_cache()


def _r15_summary(world) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return world.get_filtered_game_state_summary()


def _r15_boot_war(world):
    for war_id, inst in world.war_instances.items():
        if not isinstance(inst, dict) or inst.get("ended_turn") is not None:
            continue
        side = inst.get("side_by_nation") or {}
        if "France" in side and "Britain" in side:
            covered = [n for n, s in side.items() if s != side["France"]]
            return war_id, inst, covered
    raise AssertionError("no boot war with France and Britain in it")


def _r15_ready_corps(world, name="Soult", where="Brittany", men=12000):
    marshal = world.get_marshal(name)
    marshal.location = where
    marshal.strength = men
    world._build_marshal_index()
    return marshal


def _r15_command(world, line: str) -> dict:
    """`/command` through the in-process client on THIS world — the three
    module globals swapped together and restored (the `_client_with` idiom)."""
    import backend.main as main_module
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    originals = (main_module.game_state["world"], main_module.world,
                 main_module.parser)
    main_module.game_state["world"] = world
    main_module.world = world
    main_module.parser = CommandParser(use_real_llm=False)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return TestClient(main_module.app).post(
                "/command", json={"command": line}).json()
    finally:
        (main_module.game_state["world"], main_module.world,
         main_module.parser) = originals


class TestS14E15:
    # ── the builder ───────────────────────────────────────────────────────

    def test_munster_held_at_war_names_ulster(self, _r15_world):
        from backend.game_logic.formations import road_notes
        w = _r15_world
        assert w.get_diplomatic_state("France", "Britain") == "WAR"
        _r15_hold(w, "Munster")
        notes = road_notes(w)
        [road] = notes["roads"]
        assert road["tag"] == "Ireland" and road["state"] == "open"
        assert road["held"] == ["Munster"] and road["missing"] == ["Ulster"]
        assert road["court"] == "Britain"
        assert road["text"] == _r15_ireland
        assert notes["by_province"] == {"Munster": _r15_ireland,
                                        "Ulster": _r15_ireland}
        assert notes["by_court"]["Britain"][0]["tag"] == "Ireland"
        assert notes["completing"] == ["Ulster"]

    def test_the_march_clause_reads_the_registry_not_a_literal(self, _r15_world):
        """Ulster is a LAND march from Munster (no sea link); cut the edge and
        the clause changes — it is derived from the same adjacency."""
        from backend.game_logic.formations import road_notes
        w = _r15_world
        _r15_hold(w, "Munster")
        w.regions["Munster"].adjacent_regions = []
        w.regions["Ulster"].adjacent_regions = ["Highlands"]
        assert ("it lies beyond Munster" in
                road_notes(w)["by_province"]["Ulster"])

    def test_the_road_pauses_when_the_war_ends(self, _r15_world):
        from backend.game_logic.formations import road_notes
        w = _r15_world
        _r15_hold(w, "Munster")
        w.diplomatic_states[w._make_diplo_key("France", "Britain")] = "PEACE"
        notes = road_notes(w)
        [road] = notes["roads"]
        assert road["state"] == "paused" and road["war"] is False
        assert "has ended" in road["text"] and "reopens the road" in road["text"]
        # a paused road is not a landing target and closes nothing by a peace
        assert notes["completing"] == [] and notes["by_court"] == {}

    def test_a_truce_keeps_the_road_open(self, _r15_world):
        """The Formables page's own gate term: an ARMISTICE counts as the war."""
        from backend.game_logic.formations import road_notes
        w = _r15_world
        _r15_hold(w, "Munster")
        w.diplomatic_states[w._make_diplo_key("France", "Britain")] = "ARMISTICE"
        assert road_notes(w)["roads"][0]["state"] == "open"

    def test_no_partly_met_formable_adds_nothing_anywhere(self, _r15_world):
        from backend.game_logic import naval
        from backend.game_logic.formations import (
            road_note_for, road_notes, road_peace_lines,
        )
        from backend.game_logic.war_status import _held_line
        w = _r15_world
        empty = {"roads": [], "by_province": {}, "by_court": {}, "completing": []}
        # the boot: nothing held (and the Italy watcher stands at 2 of 5 —
        # a Class T dream is the client's own climb, never a road note)
        assert road_notes(w) == empty
        assert road_note_for(w, "Munster") == ""
        assert road_peace_lines(w, ["Britain"], [{"type": "peace"}]) == []
        assert _held_line(w, "France", ["Britain"]) == ""
        assert not any("road_note" in row
                       for row in _r15_summary(w)["map_data"].values())
        assert not any("Ireland" in n for n in
                       naval.build_admiralty_report(w).get("expedition_notes", []))
        # both provinces held at war: the carve is AVAILABLE — the table's
        # Erect row and the page carry it; nothing is "partly met", so the
        # points of action (the panels, the Admiralty, the capture reply)
        # add nothing — the war card and the peace lines carry the READY
        # road (S14E-X, the sweep's whole-held sibling; `TestS14EX61`)
        _r15_hold(w, "Munster", "Ulster")
        ready = road_notes(w)
        assert ready["by_province"] == {} and ready["completing"] == []
        assert [r["state"] for r in ready["roads"]] == ["ready"]
        assert road_note_for(w, "Munster") == ""
        # nothing held but the war running: not begun
        _r15_hold(w, "Munster", "Ulster", nation="Britain")
        assert road_notes(w) == empty

    def test_the_notes_are_the_players_alone(self, _r15_world):
        """An AI court holding Munster at war with Britain begins no road of
        the player's: the notes read the PLAYER's bloc (Spain is a French
        satellite at the boot, so a court outside it is the witness)."""
        from backend.game_logic.formations import road_notes
        w = _r15_world
        assert "Russia" not in w.get_bloc_members("France")
        _r15_hold(w, "Munster", nation="Russia")
        assert road_notes(w)["roads"] == []

    def test_an_ally_in_the_bloc_counts_as_the_bloc(self, _r15_world):
        from backend.game_logic.formations import road_notes
        w = _r15_world
        assert "Russia" not in w.get_bloc_members("France")
        _r15_hold(w, "Munster", nation="Russia")
        w.diplomatic_states[w._make_diplo_key("France", "Russia")] = "ALLIANCE"
        w.invalidate_bloc_members_cache()
        assert road_notes(w)["roads"][0]["held"] == ["Munster"]

    # ── (a) the capture reply and the landing result ──────────────────────

    def test_the_capture_question_and_its_reply_carry_the_note(self, _r15_world):
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import capture_choice_prompt
        w = _r15_world
        executor = CommandExecutor()
        game_state = {"world": w}
        soult = w.get_marshal("Soult")
        capture = executor._combat._attempt_region_capture(
            soult, "Munster", w, game_state)
        assert capture["captured"]
        pending = w.pending_capture_choice
        assert pending["road_note"] == _r15_ireland
        assert _r15_ireland in capture_choice_prompt(pending)
        reply = executor.handle_capture_choice("secure", game_state)
        assert reply["success"] and _r15_ireland in reply["message"]

    def test_a_capture_elsewhere_is_byte_identical(self, _r15_world):
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import capture_choice_prompt
        w = _r15_world
        executor = CommandExecutor()
        soult = w.get_marshal("Soult")
        capture = executor._combat._attempt_region_capture(
            soult, "Highlands", w, {"world": w})
        assert capture["captured"]
        assert "road_note" not in w.pending_capture_choice
        assert "Ireland" not in capture_choice_prompt(w.pending_capture_choice)
        reply = executor.handle_capture_choice("secure", {"world": w})
        assert "Ireland" not in reply["message"]

    def test_the_landing_result_carries_the_note_once(self, _r15_world):
        from backend.commands.executor import CommandExecutor
        w = _r15_world
        executor = CommandExecutor()
        game_state = {"world": w}
        w.fleets["Britain"]["ships"] = 0
        _r15_ready_corps(w)
        result = executor._naval._execute_naval_expedition(
            {"marshal": "Soult", "action": "naval_expedition",
             "target": "Munster",
             "raw_command": "land Soult in Munster confirmed"}, game_state)
        assert result["landed"]
        assert result["message"].count(_r15_ireland) == 1
        assert w.pending_capture_choice["road_note"] == _r15_ireland

    def test_a_held_beach_still_names_the_road(self, _r15_world):
        """The second landing: Ulster contested (a defender holds it), Munster
        ours — the landing result names the road although nothing was taken."""
        from backend.commands.executor import CommandExecutor
        w = _r15_world
        _r15_hold(w, "Munster")
        executor = CommandExecutor()
        w.fleets["Britain"]["ships"] = 0
        _r15_ready_corps(w)
        defender = next(m for m in w.marshals.values() if m.nation == "Britain")
        defender.location = "Ulster"
        defender.strength = 9000
        w._build_marshal_index()
        result = executor._naval._execute_naval_expedition(
            {"marshal": "Soult", "action": "naval_expedition",
             "target": "Ulster",
             "raw_command": "land Soult in Ulster confirmed"}, {"world": w})
        assert result["landed"]
        assert result["message"].count(_r15_ireland) == 1

    # ── (b) the region payload ────────────────────────────────────────────

    def test_the_munster_and_ulster_panels_carry_the_note(self, _r15_world):
        w = _r15_world
        _r15_hold(w, "Munster")
        data = _r15_summary(w)["map_data"]
        assert data["Munster"]["road_note"] == _r15_ireland
        assert data["Ulster"]["road_note"] == _r15_ireland
        assert "road_note" not in data["Paris"]
        assert sum(1 for row in data.values() if "road_note" in row) == 2

    def test_the_response_the_client_reads_carries_the_note(self, _r15_world):
        """The wire: `/command` -> `game_state.map_data` (what the region
        panel renders from) and the priced capture question's `capture_data`."""
        w = _r15_world
        _r15_hold(w, "Munster")
        body = _r15_command(w, "status")
        data = body["game_state"]["map_data"]
        assert data["Munster"]["road_note"] == _r15_ireland
        assert data["Ulster"]["road_note"] == _r15_ireland
        assert "road_note" not in data["Paris"]

    # ── (c) the Admiralty ─────────────────────────────────────────────────

    def test_the_admiralty_terms_name_the_road(self, _r15_world):
        from backend.game_logic import naval
        w = _r15_world
        _r15_hold(w, "Munster")
        report = naval.build_admiralty_report(w)
        assert _r15_ireland in report["expedition_notes"]

    def test_the_road_completing_shore_ranks_first(self, _r15_world, _r15_boot):
        """A corps at a yard: with Munster held, Ulster is the first landing
        chip; on a board with no road the same corps' ordering is the old
        one (enemy shores, then odds, then distance)."""
        from backend.game_logic import naval
        from backend.models.world_state import WorldState
        base = WorldState.from_dict(
            json.loads(json.dumps(_r15_boot.to_dict(), default=str)))
        _r15_ready_corps(base)
        old = naval.build_admiralty_report(base)["expedition_chips"]
        assert old and old[0]["command"] != "land Soult in Ulster"
        assert not any("road to Ireland" in c["note"] for c in old)

        w = _r15_world
        _r15_hold(w, "Munster")
        _r15_ready_corps(w)
        options = naval.expedition_landing_options(w, "France")
        assert "Ulster" in options, "Ulster must be a lawful landing here"
        chips = naval.build_admiralty_report(w)["expedition_chips"]
        assert chips[0]["command"] == "land Soult in Ulster"
        assert "the next step on the road to Ireland (Munster held)" in chips[0]["note"]
        # the rest keep the old order after it
        rest = [c["command"] for c in chips[1:]]
        assert "land Soult in Ulster" not in rest

    def test_a_corps_on_munster_is_told_the_march_not_offered_a_chip(self, _r15_world):
        """Ulster is a land march from Munster, so a corps ON Munster is never
        offered an Ulster landing (the expedition is for what feet cannot
        reach) — the terms line is the honest surface, and it says so."""
        from backend.game_logic import naval
        w = _r15_world
        _r15_hold(w, "Munster")
        soult = _r15_ready_corps(w, where="Munster")
        options = naval.expedition_landing_options(w, "France")
        assert all(row["marshal"] != soult.name
                   for row in options.get("Ulster", []))
        report = naval.build_admiralty_report(w)
        assert not any(c["command"] == "land Soult in Ulster"
                       for c in report["expedition_chips"])
        assert _r15_ireland in report["expedition_notes"]
        assert "it lies a march from Munster" in _r15_ireland

    # ── (d) the war card ──────────────────────────────────────────────────

    def test_the_war_card_closes_the_carve_in_its_held_line(self, _r15_world):
        from backend.game_logic.war_status import _held_line, build_active_wars
        w = _r15_world
        _r15_hold(w, "Munster")
        line = _held_line(w, "France", ["Britain"])
        assert line == (
            "A peace signed now is on the held line: Munster stays ours by the "
            "treaty — and closes the Ireland carve, Ulster not yet held.")
        wars = build_active_wars(w)
        rows = wars.get("wars") if isinstance(wars, dict) else wars
        held = [r.get("held_line", "") for r in rows]
        assert any("closes the Ireland carve, Ulster not yet held" in h
                   for h in held), held

    def test_a_road_held_by_an_ally_still_speaks_on_the_war_card(
            self, _r15_world, monkeypatch):
        """The status quo names nothing France herself keeps (an ally holds
        Munster): the card carries the road's own sentence, never an empty
        held line and never a false 'on the held line'."""
        from backend.game_logic import game_end
        from backend.game_logic.war_status import _held_line
        w = _r15_world
        _r15_hold(w, "Munster")
        monkeypatch.setattr(game_end, "status_quo_forecast_lines",
                            lambda *a, **k: {"lines": [], "warnings": []})
        assert _held_line(w, "France", ["Britain"]) == (
            "A peace signed now closes the Ireland carve, "
            "Ulster not yet held.")

    # ── (e) the offer and the review ──────────────────────────────────────

    def test_the_road_peace_line_is_the_one_sentence(self, _r15_world):
        from backend.game_logic.formations import road_peace_lines
        w = _r15_world
        _r15_hold(w, "Munster")
        assert road_peace_lines(w, ["Britain"], [{"type": "peace"}]) == [
            "This peace ends the war and closes the Ireland carve — "
            "Ulster not yet held."]
        # another court's peace closes nothing of Britain's road
        assert road_peace_lines(w, ["Austria"], [{"type": "peace"}]) == []

    def test_the_offer_card_carries_the_closing_line(self, _r15_world):
        from backend.game_logic.settlement_offers import (
            build_incoming_settlement_offer_popup,
        )
        w = _r15_world
        _r15_hold(w, "Munster")
        war_id, inst, covered = _r15_boot_war(w)
        side = inst["side_by_nation"]
        offer = {
            "type": "incoming_settlement_offer",
            "dialogue_type": "incoming_settlement_offer",
            "offer_id": f"settlement_offer:{war_id}:{w.current_turn}:1",
            "war_id": war_id, "proposer_nation": "Britain",
            "proposer_side": side["Britain"], "accepting_side": side["France"],
            "accepting_leader": "France",
            "covered_enemy_participants": list(covered),
            "settlement_terms": [{"type": "peace"}],
            "turn_created": int(w.current_turn),
        }
        popup = build_incoming_settlement_offer_popup(w, offer)
        assert ("This peace ends the war and closes the Ireland carve — "
                "Ulster not yet held.") in popup["terms_summary"]

    def test_the_ratification_review_carries_the_closing_line(self, _r15_world):
        from backend.game_logic.settlement_staging import stage_settlement_confirm
        w = _r15_world
        _r15_hold(w, "Munster")
        war_id, _inst, covered = _r15_boot_war(w)
        staged = stage_settlement_confirm(
            w, war_id=war_id, actor_nation="France", white_peace=True,
            caller_kind="ai_system", covered_enemy_participants=covered,
            selected_target_nation="Britain", consenting_courts=list(covered),
            consent_terms=[], consent_offer_id="r15")
        dialogue = staged.get("diplomatic_dialogue") or {}
        assert dialogue.get("road_closing_lines") == [
            "This peace ends the war and closes the Ireland carve — "
            "Ulster not yet held."], staged
        # the White Peace label keys on the status-quo review alone
        assert not any("Ireland" in line
                       for line in dialogue.get("status_quo_review", []))

    def test_a_review_on_a_board_with_no_road_adds_no_line(self, _r15_world):
        from backend.game_logic.settlement_staging import stage_settlement_confirm
        w = _r15_world
        war_id, _inst, covered = _r15_boot_war(w)
        staged = stage_settlement_confirm(
            w, war_id=war_id, actor_nation="France", white_peace=True,
            caller_kind="ai_system", covered_enemy_participants=covered,
            selected_target_nation="Britain", consenting_courts=list(covered),
            consent_terms=[], consent_offer_id="r15b")
        dialogue = staged.get("diplomatic_dialogue") or {}
        assert dialogue.get("road_closing_lines") == []

    # ── the sweep: every other road, by the ONE builder ───────────────────

    def test_another_road_gets_the_same_notes(self, _r15_world):
        """An authored two-province template carved from one court (the shape
        a Confederation of the Rhine would take) rides the same builder: the
        panel payload, the war card and the review all follow."""
        from backend.game_logic.formations import road_notes, road_peace_lines
        from backend.game_logic.war_status import _held_line
        w = _r15_world
        start = w._starting_controllers if getattr(w, "_starting_controllers", None) else None
        if start is None:
            from backend.models.region import get_starting_controllers
            start = get_starting_controllers()
        austrian = [p for p, c in start.items()
                    if c == "Austria" and p in w.regions][:2]
        assert len(austrian) == 2
        w.formable_nations["Confederation"] = {
            "display_name": "Confederation of the Rhine", "flag": "Confederation",
            "provinces": list(austrian)}
        w.diplomatic_states[w._make_diplo_key("France", "Austria")] = "WAR"
        _r15_hold(w, austrian[0])
        notes = road_notes(w)
        road = next(r for r in notes["roads"] if r["tag"] == "Confederation")
        assert road["state"] == "open" and road["court"] == "Austria"
        assert road["missing"] == [austrian[1]]
        assert notes["by_province"][austrian[1]].startswith(
            f"Confederation of the Rhine needs {austrian[1]} too")
        assert "carve at a table while the war with Austria runs" in road["text"]
        data = _r15_summary(w)["map_data"]
        assert data[austrian[0]]["road_note"] == road["text"]
        assert data[austrian[1]]["road_note"] == road["text"]
        assert ("closes the Confederation of the Rhine carve, "
                f"{austrian[1]} not yet held") in _held_line(w, "France", ["Austria"])
        assert road_peace_lines(w, ["Austria"], [{"type": "peace"}]) == [
            "This peace ends the war and closes the Confederation of the Rhine "
            f"carve — {austrian[1]} not yet held."]
        # a package that erects the template itself closes nothing
        assert road_peace_lines(
            w, ["Austria"],
            [{"type": "peace"}, {"type": "create_client", "tag": "Confederation",
                                 "from": "Austria", "to": "France"}]) == []
        # the Ireland road is untouched by it
        assert not any(r["tag"] == "Ireland" for r in notes["roads"])


class TestS14EX59:
    """Sibling sweep (Golden Rule 10): the MARCH route into a capture. The
    attack, charge, landing and executor routes all speak through
    `capture_choice_prompt`; the march that auto-secures (a standing order's
    hop) asks no question and said only "The province is secured." — it names
    the road too."""

    _ULSTER_FIRST = ("Ireland needs Munster too — it lies a march from Ulster; "
                     "carve at a table while the war with Britain runs")

    def _march_into_ulster(self, world, *, strategic: bool):
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        soult = world.get_marshal("Soult")
        soult.location = "Highlands"
        soult.strength = 12000
        soult.moved_this_turn = False
        world._build_marshal_index()
        return executor._movement._execute_move(
            soult, "Ulster", world, {"world": world},
            strategic_execution=strategic)

    def test_the_auto_secured_march_names_the_road(self, _r15_world):
        result = self._march_into_ulster(_r15_world, strategic=True)
        assert result["success"], result["message"]
        assert "The province is secured." in result["message"]
        assert f"{self._ULSTER_FIRST}." in result["message"]
        assert _r15_world.pending_capture_choice is None

    def test_the_asked_march_names_the_road_at_the_question(self, _r15_world):
        result = self._march_into_ulster(_r15_world, strategic=False)
        assert result["success"], result["message"]
        assert result["message"].count(self._ULSTER_FIRST) == 1
        assert _r15_world.pending_capture_choice["road_note"] == self._ULSTER_FIRST

    def test_a_march_off_the_road_says_nothing(self, _r15_world):
        from backend.commands.executor import CommandExecutor
        w = _r15_world
        soult = w.get_marshal("Soult")
        soult.location = "Wales"
        soult.strength = 12000
        soult.moved_this_turn = False
        w._build_marshal_index()
        target = next(a for a in w.regions["Wales"].adjacent_regions
                      if w.regions[a].controller == "Britain"
                      and a not in ("Ulster", "Munster"))
        result = CommandExecutor()._movement._execute_move(
            soult, target, w, {"world": w}, strategic_execution=True)
        assert result["success"], result["message"]
        assert "Ireland" not in result["message"]


class TestS14EX61:
    """S14E-15's sweep, the whole-held road: with Munster AND Ulster held and
    the war with Britain running, the carve is AVAILABLE — and a peace with
    Britain closed it unannounced on the war card, the offer and the review.
    A `ready` row feeds ONLY `by_court` (those three surfaces); the panels,
    the Admiralty and the capture reply add nothing (no next province)."""

    def test_the_ready_road_is_named_where_a_peace_would_close_it(self, _r15_world):
        from backend.game_logic import naval
        from backend.game_logic.formations import (
            road_note_for, road_notes, road_peace_lines, road_war_card_clause,
        )
        from backend.game_logic.war_status import _held_line
        w = _r15_world
        _r15_hold(w, "Munster", "Ulster")
        notes = road_notes(w)
        assert [r["state"] for r in notes["by_court"]["Britain"]] == ["ready"]
        assert road_war_card_clause(w, ["Britain"], notes) == {
            "Britain": "and closes the Ireland carve — erect it at the table first"}
        assert road_peace_lines(w, ["Britain"], [{"type": "peace"}]) == [
            "This peace ends the war and closes the Ireland carve — erect it at the table first."]
        assert _held_line(w, "France", ["Britain"]).endswith(
            "— and closes the Ireland carve — erect it at the table first.")
        # the package that erects it closes nothing
        assert road_peace_lines(w, ["Britain"], [{"type": "create_client", "tag": "Ireland"}]) == []
        # the points of action stay silent: there is no next province
        assert road_note_for(w, "Munster") == "" and road_note_for(w, "Ulster") == ""
        assert not any("Ireland" in n for n in
                       naval.build_admiralty_report(w).get("expedition_notes", []))

    def test_a_ready_road_at_peace_is_no_road(self, _r15_world):
        from backend.game_logic.formations import road_notes
        from backend.game_logic.diplomacy import set_diplomatic_state
        w = _r15_world
        _r15_hold(w, "Munster", "Ulster")
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            set_diplomatic_state(w, "France", "Britain", "PEACE", "test")
        assert road_notes(w)["roads"] == []


# ══════════════════════════════════════════════════════════════════════════
# row31
# ══════════════════════════════════════════════════════════════════════════
# S14E-31 with its ruling S14E-D4 — a floor on the war title's ground rung,
# and a `court=` read that is the court's own ground.
# 
# Pre-Deploy S14f part 1 (October 24, 2026; `docs/BUG_FIXES.md` §S14E,
# `docs/DESIGN_REFINEMENT.md` §S14E D4). The sea road's #8 (turn 6, action
# 94): one 6,500-man beachhead on Munster renamed the seven-power war "War
# for Munster" — `war_title`'s ground rung named the first enemy home
# province France's side held with no weight floor (ruling J set none) — and
# the Austrian truce row carried the name, because a `court=` read took the
# whole enemy side's ground where the docstring promised the court's own.
# Reproduced on the shipped 1805 board: France holding Munster alone read
# "War for Munster" on the league's war and on Austria's row.
# 
# The build (`_ground_rung`): an owner's ground titles the war when the
# holders have its CAPITAL, TWO OR MORE of its home provinces, or A QUARTER
# of them; below the floor the league or the court keeps the title and the
# line still names what is held. A `court=` read is that court's ground —
# what we hold of hers and what she holds of ours. The wound rung carries the
# same floor (a France that lost one province is not fighting the War for
# Alsace; one that lost Paris is fighting the War for Paris).

_R31_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")


def _r31_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r31_boot():
    from backend.models.world_state import WorldState
    with _r31_quiet():
        return WorldState.from_scenario(str(_R31_SCENARIO))


@pytest.fixture
def _r31_w(_r31_boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(_r31_boot.to_dict(), default=str)))


class TestS14E31:
    def test_a_lone_beachhead_leaves_the_league_its_title(self, _r31_w):
        from backend.game_logic.war_title import war_title
        w = _r31_w
        assert w.regions["Munster"].controller == "Britain"
        w.regions["Munster"].controller = "France"
        rec = war_title(w, "war_1")
        assert rec["title"] == "War with the Third Coalition" and rec["source"] == "league"
        # the ground is still read and named on the line
        assert rec["theirs_we_hold"] == ["Munster"]
        assert rec["line"] == "The War with the Third Coalition: France holds Munster of Britain's."

    def test_the_truce_row_reads_the_courts_own_ground(self, _r31_w):
        from backend.game_logic.war_status import _title_block
        from backend.game_logic.war_title import war_title
        w = _r31_w
        w.regions["Munster"].controller = "France"
        austria = war_title(w, court="Austria")
        assert austria["title"] == "War with Austria"
        assert austria["theirs_we_hold"] == [] and "Munster" not in austria["line"]
        assert austria["line"] == "The War with Austria: nothing taken yet on either side."
        britain = war_title(w, court="Britain")
        assert britain["title"] == "War with Britain"
        assert britain["line"] == "The War with Britain: France holds Munster of Britain's."
        row = _title_block(w, "", "Austria")
        assert row["war_title"] == "War with Austria" and row["war_stake"] == []

    def test_two_provinces_or_the_capital_clear_the_floor(self, _r31_w):
        from backend.game_logic.war_title import war_title
        w = _r31_w
        w.regions["Munster"].controller = "France"
        w.regions["Bohemia"].controller = "France"
        w.regions["Tyrol"].controller = "France"
        rec = war_title(w, "war_1")
        assert rec["title"] == "War for Bohemia" and rec["source"] == "ground"
        assert war_title(w, court="Austria")["title"] == "War for Bohemia"
        assert war_title(w, court="Britain")["title"] == "War with Britain"
        # the capital alone clears it
        w.regions["Bohemia"].controller = "Austria"
        w.regions["Tyrol"].controller = "Austria"
        w.regions["Vienna"].controller = "France"
        assert war_title(w, "war_1")["title"] == "War for Vienna"

    def test_the_wound_carries_the_same_floor(self, _r31_w):
        from backend.game_logic.war_title import war_title
        w = _r31_w
        home = list(w.nation_starting_regions["France"])
        lost = next(r for r in home if r != "Paris")
        w.regions[lost].controller = "Austria"
        rec = war_title(w, "war_1")
        assert rec["ours_they_hold"] == [lost]
        assert rec["title"] == "War with the Third Coalition"
        w.regions["Paris"].controller = "Austria"
        assert war_title(w, "war_1")["title"] == "War for Paris"


class TestS14ED4:
    """The floor itself, on a bare world: the capital, two provinces, or a
    quarter of the owner's home."""

    @staticmethod
    def _world(home, capital):
        return SimpleNamespace(
            nation_starting_regions={"Court": list(home)},
            get_nation_capital=lambda nation: capital,
            current_turn=5, province_title={},
        )

    def test_a_quarter_of_a_small_court_is_enough(self):
        from backend.game_logic.war_title import _ground_rung
        w = self._world(["A", "B", "C", "D"], "A")
        assert _ground_rung(w, [(5, 0, "B", "Court")]) == [(5, 0, "B", "Court")]

    def test_one_of_six_is_below_the_floor(self):
        from backend.game_logic.war_title import _ground_rung
        w = self._world(["A", "B", "C", "D", "E", "F"], "A")
        assert _ground_rung(w, [(5, 0, "B", "Court")]) == []
        assert _ground_rung(w, [(5, 0, "B", "Court"), (6, 0, "C", "Court")]) == [
            (5, 0, "B", "Court"), (6, 0, "C", "Court")]
        assert _ground_rung(w, [(5, 1, "A", "Court")]) == [(5, 1, "A", "Court")]

    def test_the_order_of_the_ground_is_kept(self):
        from backend.game_logic.war_title import _ground_rung
        w = self._world(["A", "B", "C", "D", "E", "F"], "A")
        ground = [(3, 0, "C", "Court"), (4, 0, "B", "Court")]
        assert _ground_rung(w, ground) == ground


# ══════════════════════════════════════════════════════════════════════════
# rowXO
# ══════════════════════════════════════════════════════════════════════════
# The orchestrator's own sibling pins of S14f part 1 (October 24, 2026) —
# the small siblings the row agents filed and left in files they could not
# touch while a neighbour edited them, built at the part's close:
# 
# - the province panel's "Attack" chip quoted `ok` over a corps sheltered on
#   peace soil (S14E-4's sweep; `order_quotes.attack_quote`, and the "march &
#   attack" chip's arrival target);
# - a march's silent undoings on the order card and the panel — Davout's
#   Iron Resolve stacks, a formed square, a turn-1 drill (S14E-13's sweep;
#   `movement_executor.departure_note`, the quote field `departs`, four
#   readers; the stacks on the move and march replies too);
# - the first-open Admiralty camp line never said a march out resets the
#   count (S14E-13's sweep; `first_open._line_admiralty_camp`, within the cap);
# - the bilateral peace preview and a court's own peace letter said nothing
#   of the formable road the peace closes (S14E-15's sweep;
#   `diplomatic_dialogue.attach_status_quo_forecast`, `road_closing`);
# - the recruit reply's "1 regions away" (S14E-5's sweep).

_RXO_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")
_RXO_REPO = Path(__file__).resolve().parents[1]


def _rxo_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _rxo_boot():
    from backend.models.world_state import WorldState
    with _rxo_quiet():
        return WorldState.from_scenario(str(_RXO_SCENARIO))


@pytest.fixture
def _rxo_w(_rxo_boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(_rxo_boot.to_dict(), default=str)))


class TestS14EX13:
    """The province panel's Attack chip over a sheltered corps."""

    def test_the_attack_chip_dims_with_the_refusal_on_peace_soil(self, _rxo_w):
        from backend.commands.order_quotes import attack_quote, march_quote
        from backend.game_logic.diplomacy import set_diplomatic_state
        w = _rxo_w
        murat = w.get_marshal("Murat")
        kutuzov = w.get_marshal("Kutuzov")
        murat.location = "Vienna"
        kutuzov.location = "Moravia"
        w.calculate_visibility()
        # at war with Austria the field is lawful: the chip quotes ok
        before = attack_quote(w, murat, kutuzov)
        assert before["ok"] is True and not before["refusal"]
        with _rxo_quiet():
            set_diplomatic_state(w, "France", "Austria", "PEACE", "test")
        after = attack_quote(w, murat, kutuzov)
        assert after["ok"] is False
        assert "Moravia is Austria's soil, and we are at peace with Austria" in after["refusal"]
        assert "Kutuzov" in after["refusal"] and "ArchdukeCharles" not in after["refusal"]
        # the "march & attack" chip carries the same refusal for its arrival target
        murat.location = "Bohemia"
        w.calculate_visibility()
        chip = march_quote(w, murat, "Moravia", then_attack="Kutuzov")
        assert chip["ok"] is False and "peace with Austria" in chip["refusal"]
        # a gun fires from where it stands: no refusal of its chip
        murat.location = "Vienna"
        murat.artillery = True
        assert attack_quote(w, murat, kutuzov)["ok"] is True


class TestS14EX56:
    """What a march costs the corps as it stands — said on the card, the
    panel, the desk and (the stacks) the reply."""

    def test_the_quote_names_the_stacks_the_square_and_the_drill(self, _rxo_w):
        from backend.commands.movement_executor import departure_note
        from backend.commands.order_quotes import march_quote
        w = _rxo_w
        davout = w.get_marshal("Davout")
        davout.iron_resolve_stacks = 3
        line = departure_note(davout, quote=True)
        assert line == "Davout's 3 Iron Resolve stacks (+24% on his next attack) are lost to the march."
        davout.iron_resolve_stacks = 1
        assert "1 Iron Resolve stack (+8% on his next attack) is lost" in departure_note(davout)
        davout.iron_resolve_stacks = 0
        davout.square_formation = True
        davout.drilling = True
        davout.drilling_locked = False
        quote_line = departure_note(davout, quote=True)
        assert "Davout's square breaks on the march." in quote_line
        assert "Davout's drill is lost to the march" in quote_line
        # the reply names only the stacks: the move already prints the square's break
        assert departure_note(davout) == ""
        davout.square_formation = False
        davout.drilling = False
        davout.iron_resolve_stacks = 2
        q = march_quote(w, davout, "Franconia")
        assert q["departs"] == "Davout's 2 Iron Resolve stacks (+16% on his next attack) are lost to the march."
        davout.iron_resolve_stacks = 0
        assert march_quote(w, davout, "Franconia")["departs"] == ""

    def test_the_four_readers_print_the_field(self):
        card = (_RXO_REPO / "godot-client" / "project-sovereign" / "scripts"
                / "order_confirm_card.gd").read_text(encoding="utf-8")
        assert card.count('q.get("departs", "")') == 2
        panel = (_RXO_REPO / "godot-client" / "project-sovereign" / "scripts"
                 / "region_panel.gd").read_text(encoding="utf-8")
        assert 'q.get("departs", "")' in panel
        desk = (_RXO_REPO / "backend" / "ai" / "state_desk.py").read_text(encoding="utf-8")
        assert 'q.get("departs")' in desk

    def test_the_move_and_the_march_replies_name_the_stacks(self, _rxo_w):
        from backend.commands.executor import CommandExecutor
        w = _rxo_w
        gs = {"world": w}
        executor = CommandExecutor()
        davout = w.get_marshal("Davout")
        davout.iron_resolve_stacks = 3
        with _rxo_quiet():
            moved = executor.execute({"command": {"marshal": "Davout", "action": "move",
                                                  "target": "Lorraine"}}, gs)
        assert moved.get("success") is True
        assert "Davout's 3 Iron Resolve stacks (+24% on his next attack) are lost to the march." in moved["message"]
        assert davout.iron_resolve_stacks == 0
        ney = w.get_marshal("Ney")
        ney.iron_resolve_stacks = 2
        with _rxo_quiet():
            marched = executor.execute({
                "command": {"raw_input": "Ney, march to Lorraine", "marshal": "Ney",
                            "action": "move", "target": "Lorraine"},
                "is_strategic": True, "strategic_type": "MOVE_TO"}, gs)
        assert marched.get("success") is True
        assert "Ney's 2 Iron Resolve stacks (+16% on his next attack) are lost to the march." in marched["message"]


class TestS14EX58:
    """The first-open Admiralty camp line says a march out resets the count."""

    def test_the_line_says_it_within_the_cap(self):
        from backend.game_logic import first_open as FO
        line = FO._line_admiralty_camp(None, None)
        assert len(line) <= FO.LINE_CAP
        assert "a march out resets the count" in line
        assert "can open the Strait for up to" in line and "blockade on you" in line


class TestS14EX60:
    """The bilateral peace preview and a court's peace letter name the road
    the peace closes, as the settlement offer and the review do."""

    def test_the_bilateral_preview_carries_the_road_line(self, _rxo_w):
        from backend.game_logic.diplomatic_dialogue import attach_status_quo_forecast
        w = _rxo_w
        w.regions["Munster"].controller = "France"
        payload = {"clauses": ["Peace"]}
        out = attach_status_quo_forecast(w, payload, "France", "Britain",
                                         {"demands": [], "sweeteners": [], "clauses": []},
                                         summary_key="clauses")
        road = "This peace ends the war and closes the Ireland carve — Ulster not yet held."
        assert road in out["clauses"]
        assert out["status_quo_forecast"]["road_closing"] == [road]
        assert road not in out["status_quo_forecast"]["lines"]   # the held line keys on `lines`
        # the annotated rows carry it as its own type where that section renders
        payload2 = {"annotated_terms": [{"type": "peace", "display_label": "Peace"}]}
        out2 = attach_status_quo_forecast(w, payload2, "France", "Britain",
                                          {"demands": [], "sweeteners": [], "clauses": []})
        assert any(r.get("type") == "road_closing" and r.get("display_label") == road
                   for r in out2["annotated_terms"])
        # no road begun: nothing added
        w.regions["Munster"].controller = "Britain"
        out3 = attach_status_quo_forecast(w, {"clauses": []}, "France", "Britain",
                                          {"demands": [], "sweeteners": [], "clauses": []},
                                          summary_key="clauses")
        assert out3["status_quo_forecast"]["road_closing"] == [] and road not in out3["clauses"]

    def test_a_re_shown_letter_does_not_repeat_the_line(self):
        src = (_RXO_REPO / "backend" / "game_logic" / "mailbox_payloads.py").read_text(encoding="utf-8")
        assert '_prior.get("road_closing")' in src


class TestS14EX20:
    """The recruit reply's plural."""

    def test_the_recruit_reply_pluralises_the_distance(self):
        src = (_RXO_REPO / "backend" / "commands" / "economy_executor.py").read_text(encoding="utf-8")
        assert "regions away)" not in src
        assert "{plural(distance, 'region')} away" in src


class TestS14EX40:
    """The AI-to-AI downgrade's dispatch line prints the states' display
    names, never the raw keys (S14E-9's sweep)."""

    def test_the_downgrade_line_reads_display_states(self):
        src = (_RXO_REPO / "backend" / "game_logic" / "ai_diplomacy.py").read_text(encoding="utf-8")
        assert 'has downgraded relations with {weaker}: {state} → {new_state}' not in src
        assert '_STATE_DISPLAY.get(state, state)' in src and '_STATE_DISPLAY.get(new_state, new_state)' in src
        from backend.display_names import STATE_DISPLAY
        assert STATE_DISPLAY["DEFENSIVE_ALLIANCE"] == "Defensive Alliance"


class TestS14EX35:
    """The roads line never prints a raw negative (S14E-8's sweep)."""

    def test_the_roads_line_clamps_at_zero(self):
        from backend.game_logic.counsel import roads_display
        lines = roads_display({"roads": [
            {"label": "Propose Peace", "number": -8, "threshold": 50, "available": True, "carries": False},
            {"label": "Propose Armistice", "number": 25, "threshold": 50, "available": True, "carries": False},
        ]})
        assert lines[0].startswith("Propose Peace — 0 of 50")
        assert lines[1].startswith("Propose Armistice — 25 of 50")


class TestS14EX52:
    """The shut-out price says when it takes the alliance under its line
    (S14E-10's sweep, after S14E-11's lever landed)."""

    def test_the_price_names_the_alliance_clock(self, _rxo_w):
        from backend.game_logic.settlement_reactions import alliance_clock_clause, shut_out_words
        from backend.game_logic.diplomacy import STATE_RELATION_THRESHOLDS
        w = _rxo_w
        line = int(STATE_RELATION_THRESHOLDS["ALLIANCE"])
        assert w.get_diplomatic_state("France", "Spain") == "ALLIANCE"
        key = w._make_diplo_key("France", "Spain")
        w.nation_relations[key] = line
        words = shut_out_words(w, {"ally": "Spain", "relation_delta": -18, "grievance_flag_added": True})
        assert words.startswith("Spain is left out: -18 relation and a grievance;")
        assert f"It takes the alliance under the {line} it holds on ({line} → {line - 18}) — Reassure Ally in the Cabinet before it lapses." in words
        # comfortably above the line: no clause; a minor hit that stays on the line: none
        w.nation_relations[key] = line + 30
        assert alliance_clock_clause(w, "Spain", -18) == ""
        w.nation_relations[key] = line + 7
        assert alliance_clock_clause(w, "Spain", -7) == ""
        # not an alliance: none
        assert alliance_clock_clause(w, "Russia", -18) == ""


class TestS14EX21:
    """A conquest-class purpose whose capital a third court took mid-war is
    told on the morning that it cannot score (S14E-5's sweep)."""

    def test_the_dispatch_names_the_dead_purpose(self, _rxo_w):
        from backend.game_logic import diplomacy as D
        from backend.game_logic.dispatch import _build_war_objective_section
        w = _rxo_w
        k = w._make_diplo_key("France", "Hanover")
        w.war_objectives.setdefault(k, {})["France"] = D.create_war_objective(
            "conquest", "France", "Hanover", ["Hanover"], w.current_turn)
        with _rxo_quiet():
            before = [ln for ln in _build_war_objective_section(w, "France") if ln["target_nation"] == "Hanover"]
        assert before and not before[0]["cannot_score"] and "Cannot score" not in before[0]["text"]
        w.regions["Hanover"].controller = "Prussia"
        with _rxo_quiet():
            after = [ln for ln in _build_war_objective_section(w, "France") if ln["target_nation"] == "Hanover"]
        assert after[0]["cannot_score"] is True
        assert "Cannot score: Prussia holds Hanover, Hanover's capital" in after[0]["text"]


class TestS14EX66:
    """`relay.muster_counts` no longer counts a corps the muster prices at
    nothing (S14E-12's sweep): the relayed SUPPORT order is the lever that
    would bring him."""

    def test_a_corps_that_cannot_arrive_is_not_counted_as_marching(self):
        from backend.commands.relay import muster_counts
        rows = [{"marshal": "Ney", "will_join": True},
                {"marshal": "Murat", "will_join": True, "cannot_arrive": True}]
        result = {"muster_preview": {"rows": rows}}
        assert muster_counts(result, "Ney") is True
        assert muster_counts(result, "Murat") is False
        assert muster_counts({}, "Ney") is False
