"""Row IQ-5 "Both Sides of the Butcher's Bill" (September 14, 2026).

Build contract: the lead's ruling on the two recon reports (PR-X2, PR-X3).

  PR-X2 — both sides report their own scope everywhere a casualty figure is
          shown. A reinforced side's losses say whether a figure is the lead
          corps' or the army's; a side that fought ALONE is never labelled.
          Surfaces: the terminal Berthier line, the enemy-phase dialog, the
          campaign log (bounded by the field, not the lead), the morning
          dispatch (it mauls the man who bled), the playtest digest.
  PR-X3 — trust's price is named where it is paid. When FA-D23 halves a
          marshal's weight the battle report names trust and the figure, on
          BOTH sides of the field; the muster row stops saying "at odds" for
          a cause that is not the relationship, and "half" for a quarter.

Everything is display only (GR6): no mechanical casualty figure moves (R2),
and each lever set False reproduces the prior surface byte for byte.

Every battle here is fought on the SHIPPED 1805 board through the real
`_execute_attack`, driven the way the enemy AI drives it
(`CommandExecutor.execute` with `_autonomous_execution`), seeded.
"""
from __future__ import annotations

import ast
import contextlib
import copy
import inspect
import io
import json
import random
import re
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.campaign_log import format_event_oneliner
from backend.commands.combat_executor import (
    CombatExecutor,
    pair_contribution_breakdown,
    weight_phrase,
)
from backend.commands.executor import CommandExecutor
from backend.game_logic import dispatch as D
from backend.game_logic import jealousy as J
from backend.models.world_state import WorldState

ROOT = next(p for p in (Path(__file__).resolve().parents[1], Path.cwd())
            if (p / "backend").is_dir())
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
GD = ROOT / "godot-client" / "project-sovereign" / "scripts"

CE = CombatExecutor


# ═══════════════════════════════════════════════════════════════════════
# Staging — the recon's own geometries, on the shipped board
# ═══════════════════════════════════════════════════════════════════════

@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _boot():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


def _stage(w, placements):
    """`placements` = {name: (region, strength)}; every other marshal is parked
    far from the field (the recon's `probe1.stage`)."""
    for m in w.marshals.values():
        if m.name in placements:
            continue
        m.location = "Moscow" if m.nation != "France" else "Gascony"
    for name, (region, strength) in placements.items():
        m = w.marshals[name]
        m.location, m.strength, m.morale = region, strength, 75
        m.retreat_recovery = 0
        m.broken = False
        m.retreated_this_turn = False
        m.moved_this_turn = False
        m.reinforced_this_turn = False
        m.drilling = False
        m.holding_position = False
        m.fortified = False
        m.strategic_order = None
    w.calculate_visibility()
    return w


def _trust(m, value):
    m.trust.modify(value - m.trust.value)
    assert m.trust.value == value


def _fight(w, attacker, target, seed):
    """The call the enemy AI makes. Returns (result, the battle log events)."""
    random.seed(seed)
    ex = CommandExecutor()
    n0 = len(w.event_log)
    with _quiet():
        res = ex.execute({"command": {"type": "specific", "marshal": attacker,
                                      "action": "attack", "target": target,
                                      "_autonomous_execution": True}},
                         {"world": w, "debug_mode": True, "executor": ex})
    assert res.get("success"), res.get("message")
    return res, [e for e in w.event_log[n0:] if e.get("type") == "battle"]


def _battle(placements, attacker, target, seed=3, trusts=None, rels=None):
    w = _stage(_boot(), placements)
    for name, value in (trusts or {}).items():
        _trust(w.marshals[name], value)
    for (a, b), value in (rels or {}).items():
        w.marshals[a].relationships[b] = value
    before = {n: int(w.marshals[n].strength) for n in placements}
    res, logs = _fight(w, attacker, target, seed)
    # a man destroyed on the field leaves the roster (tombstoned): he lost all
    losses = {n: before[n] - int(getattr(w.marshals.get(n), "strength", 0))
              for n in placements}
    return w, res, logs, losses


# Paris borders Berry and Artois; Swabia borders Franconia and Rhineland.
D_ADJ = {"Ney": ("Paris", 20000), "Davout": ("Berry", 30000), "Moore": ("Artois", 60000)}
D_CO = {"Ney": ("Paris", 20000), "Davout": ("Paris", 30000), "Moore": ("Artois", 60000)}
D_STUB = {"Ney": ("Paris", 500), "Davout": ("Berry", 48000), "Moore": ("Artois", 100000)}
A_ADJ = {"Ney": ("Franconia", 30000), "Davout": ("Rhineland", 25000), "Mack": ("Swabia", 40000)}
A_SAME = {"Ney": ("Swabia", 30000), "Davout": ("Swabia", 25000), "Mack": ("Swabia", 40000)}
A_STUB = {"Ney": ("Franconia", 500), "Davout": ("Rhineland", 48000), "Mack": ("Swabia", 40000)}
LONE_DEF = {"Ney": ("Franconia", 30000), "Davout": ("Rhineland", 30000), "Mack": ("Swabia", 1500)}
ENEMY_CO = {"Ney": ("Franconia", 40000), "Mack": ("Swabia", 30000),
            "ArchdukeJohn": ("Swabia", 20000)}
AI_V_AI = {"Castanos": ("Franconia", 40000), "Mack": ("Swabia", 30000),
           "ArchdukeJohn": ("Swabia", 20000)}


def test_the_geometry_is_the_recons():
    w = _boot()
    assert {"Berry", "Artois"} <= set(w.get_region("Paris").adjacent_regions)
    assert {"Franconia", "Rhineland"} <= set(w.get_region("Swabia").adjacent_regions)


def test_both_levers_default_on():
    assert CE.BOTH_SIDES_NAME_THEIR_SCOPE is True
    assert CE.TRUST_NAMES_ITS_PRICE is True
    assert CE.TRUST_REACHES_THE_FIELD is True
    assert CE.BROKEN_TRUST_CONTRIBUTION == 0.5


def _cs(res):
    return res["battle_report"]["casualty_summary"]


def _side(res, side):
    return res["events"][0][side]


def _headline_texts(w):
    with _quiet():
        head = D._build_headline(w, "France")
    if head is None:
        return None, []
    return head, [head["text"], *head.get("sub_beats", [])]


# ═══════════════════════════════════════════════════════════════════════
# PR-X2 R1 — the defender carries the label (the row's completion pin)
# ═══════════════════════════════════════════════════════════════════════

class TestTheDefenderCarriesTheLabel:
    def test_d_adj_seed_3_labels_the_defender(self):
        """THE ROW. Moore attacks Ney at Paris; Davout marches in from Berry.
        The description says "Ney's army 6,814"; before IQ-5 the report said
        "Casualties: Moore 4,688 | Ney 2,725" with no label."""
        w, res, _logs, losses = _battle(D_ADJ, "Moore", "Ney")
        cs = _cs(res)
        assert cs["defender_casualties_scope"] == "own corps"
        assert cs["defender_casualties"] == 20000 - w.marshals["Ney"].strength == 2725
        assert losses == {"Ney": 2725, "Davout": 4089, "Moore": 4688}
        # the army figure is the one the event (enemy-phase transport) carries
        assert _side(res, "defender")["casualties"] == 6814 == 2725 + 4089
        assert _side(res, "defender")["casualties_scope"] == "army"
        # the attacker fought alone and carries no label
        assert cs["attacker_casualties_scope"] == ""
        assert "casualties_scope" not in _side(res, "attacker")

    def test_the_lead_remainder_is_named_beside_the_army_losses(self):
        """IQ-5 review (#20): `lead_remaining` EQUALS the event's `remaining`
        by construction — both are the lead's post-battle strength, and the
        pursuit block updates both together; nothing else moves either. The
        fix IQ5-2 made is the LABEL ("'s own corps"), not a corrected number.
        So no pin can stage the two apart (a fixture that did would be
        fabricated), and the sweep row that swapped one for the other was
        behaviour-neutral and is deleted."""
        w, res, _logs, _ = _battle(D_ADJ, "Moore", "Ney")
        d = _side(res, "defender")
        assert d["lead_remaining"] == int(w.marshals["Ney"].strength) == 17275
        assert d["remaining"] == d["lead_remaining"]
        assert type(d["lead_remaining"]) is int
        assert _side(res, "attacker")["lead_remaining"] == int(w.marshals["Moore"].strength)

    def test_the_mirror_labels_a_reinforced_attacker(self):
        w, res, _logs, losses = _battle(A_ADJ, "Ney", "Mack")
        cs = _cs(res)
        assert cs["attacker_casualties_scope"] == "own corps"
        assert cs["attacker_casualties"] == losses["Ney"] == 3132
        assert cs["defender_casualties_scope"] == ""
        assert _side(res, "attacker")["casualties_scope"] == "army"
        assert _side(res, "attacker")["casualties"] == losses["Ney"] + losses["Davout"]
        assert "casualties_scope" not in _side(res, "defender")

    def test_a_solo_battle_carries_no_label_anywhere(self):
        """The coordinated branch is the only producer whose report figure can
        differ from the army figure. A solo battle stays as it was."""
        w = _stage(_boot(), {"Ney": ("Franconia", 30000), "Mack": ("Swabia", 40000)})
        res, logs = _fight(w, "Ney", "Mack", 3)
        cs = _cs(res)
        assert "own corps" not in json.dumps(cs)
        for side in ("attacker", "defender"):
            assert "casualties_scope" not in _side(res, side)
            assert "lead_remaining" not in _side(res, side)
        assert not any("field_before" in k or "participant_losses" in k for k in logs[0])

    def test_lever_down_has_no_defender_key(self, monkeypatch):
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        w, res, _logs, _ = _battle(D_ADJ, "Moore", "Ney")
        cs = _cs(res)
        assert "defender_casualties_scope" not in cs
        assert cs["attacker_casualties_scope"] == ""
        for side in ("attacker", "defender"):
            assert "casualties_scope" not in _side(res, side)
            assert "lead_remaining" not in _side(res, side)

    def test_lever_down_keeps_the_old_attacker_label(self, monkeypatch):
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        _w, res, _logs, _ = _battle(A_ADJ, "Ney", "Mack")
        assert _cs(res)["attacker_casualties_scope"] == "own corps"


# ═══════════════════════════════════════════════════════════════════════
# PR-X2 R1 — a lone side is never labelled (the sensitivity pin)
# ═══════════════════════════════════════════════════════════════════════

def _naive_mirror(distribution, lead, raw, share):
    """What the row's completion text, built literally, would have shipped:
    the attacker's `raw != share` arithmetic mirrored onto the defender."""
    return int(raw) != int(share)


class TestALoneSideIsNeverLabelled:
    # Mack 1,500 fights ALONE at Swabia against Ney + Davout. The overkill
    # cap (seeds 3, 7: raw 1,534 capped to 1,500) and the `< 50 -> 0` rubble
    # rule (seed 5: raw 1,499, report 1,500) separate the two numbers.
    SEEDS = (3, 5, 7)

    @pytest.mark.parametrize("seed", SEEDS)
    def test_the_arithmetic_disagrees_and_the_label_still_does_not_lie(self, seed):
        _w, res, _logs, _ = _battle(LONE_DEF, "Ney", "Mack", seed=seed)
        cs = _cs(res)
        raw = _side(res, "defender")["casualties"]
        # the trap is really in the fixture: a raw-vs-share mirror WOULD fire
        assert raw != cs["defender_casualties"], (seed, raw, cs["defender_casualties"])
        assert cs["defender_casualties_scope"] == ""
        assert "casualties_scope" not in _side(res, "defender")
        # the other side IS an army and says so
        assert cs["attacker_casualties_scope"] == "own corps"

    def test_no_seed_labels_the_lone_side(self):
        for seed in range(1, 9):
            _w, res, _logs, _ = _battle(LONE_DEF, "Ney", "Mack", seed=seed)
            assert _cs(res)["defender_casualties_scope"] == "", seed

    def test_the_naive_mirror_fails_this_pin(self, monkeypatch):
        """SENSITIVITY: swap the distribution predicate for the naive mirror and
        the seed-3 lone Mack is labelled "own corps" — i.e. the pin above goes
        red under the fix the row literally asked for."""
        monkeypatch.setattr(CE, "_side_fought_as_army", staticmethod(_naive_mirror))
        _w, res, _logs, _ = _battle(LONE_DEF, "Ney", "Mack", seed=3)
        assert _cs(res)["defender_casualties_scope"] == "own corps"
        assert _side(res, "defender").get("casualties_scope") == "army"


# ═══════════════════════════════════════════════════════════════════════
# PR-X2 R1 — the reconcile itself (distribution predicate, legacy fallback)
# ═══════════════════════════════════════════════════════════════════════

def _result(atk_raw, def_raw, atk_orig, def_orig):
    return {
        "attacker": {"name": "Ney", "casualties": atk_raw},
        "defender": {"name": "Mack", "casualties": def_raw},
        "battle_report": {"casualty_summary": {
            "attacker_original": atk_orig, "defender_original": def_orig}},
    }


NEY = SimpleNamespace(name="Ney", strength=18000)
MACK = SimpleNamespace(name="Mack", strength=0)


class TestTheReconcilePredicate:
    def test_an_ally_who_bled_makes_the_side_an_army(self):
        br = _result(8141, 1500, 20171, 1500)
        CE._reconcile_report_survivors(br, NEY, MACK,
                                       {"Ney": 2171, "Davout": 5970}, {"Mack": 1500})
        cs = br["battle_report"]["casualty_summary"]
        assert cs["attacker_casualties_scope"] == "own corps"
        assert br["attacker"]["casualties_scope"] == "army"

    def test_a_lone_corps_hit_past_its_strength_is_not(self):
        """raw 1,534, share 1,500 — the overkill cap."""
        br = _result(8141, 1534, 20171, 1500)
        CE._reconcile_report_survivors(br, NEY, MACK,
                                       {"Ney": 2171, "Davout": 5970}, {"Mack": 1500})
        cs = br["battle_report"]["casualty_summary"]
        assert cs["defender_casualties_scope"] == ""
        assert "casualties_scope" not in br["defender"]

    def test_an_ally_who_bled_nothing_does_not(self):
        br = _result(2171, 1500, 20171, 1500)
        CE._reconcile_report_survivors(br, NEY, MACK, {"Ney": 2171, "Davout": 0},
                                       {"Mack": 1500})
        assert br["battle_report"]["casualty_summary"]["attacker_casualties_scope"] == ""
        assert "casualties_scope" not in br["attacker"]

    def test_the_legacy_three_argument_call_falls_back_to_the_arithmetic(self):
        """The PT-D unit pins and M4 call it with three arguments. With no
        distribution the old `raw != share` test stands — on both sides."""
        br = _result(8141, 4000, 20171, 5000)   # defender share = 5000 - 0
        CE._reconcile_report_survivors(br, NEY, MACK)
        cs = br["battle_report"]["casualty_summary"]
        assert cs["attacker_casualties"] == 2171
        assert cs["attacker_casualties_scope"] == "own corps"
        assert cs["defender_casualties"] == 5000
        assert cs["defender_casualties_scope"] == "own corps"
        br = _result(2171, 5000, 20171, 5000)
        CE._reconcile_report_survivors(br, NEY, MACK)
        cs = br["battle_report"]["casualty_summary"]
        assert cs["attacker_casualties_scope"] == "" == cs["defender_casualties_scope"]

    def test_lever_down_is_the_pre_iq5_function(self, monkeypatch):
        """No defender key, no event stamp, and the attacker's label is the old
        arithmetic even with a distribution in hand (so the lone overkill is
        labelled exactly as it used to be)."""
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        br = _result(1534, 8141, 1500, 20171)
        lone = SimpleNamespace(name="Ney", strength=0)
        CE._reconcile_report_survivors(br, lone, MACK, {"Ney": 1500}, {"Mack": 2171})
        cs = br["battle_report"]["casualty_summary"]
        assert "defender_casualties_scope" not in cs
        assert cs["attacker_casualties_scope"] == "own corps"
        assert "casualties_scope" not in br["attacker"]
        assert "casualties_scope" not in br["defender"]


# ═══════════════════════════════════════════════════════════════════════
# PR-X2 R3 — co-located stacks are named
# ═══════════════════════════════════════════════════════════════════════

class TestCoLocatedStacksAreNamed:
    def test_d_co_names_davout_and_his_dead(self):
        """The ordinary way to mass a defence printed NOTHING: Davout's 4,424
        dead appeared only in the diorama."""
        _w, res, _logs, losses = _battle(D_CO, "Moore", "Ney")
        assert losses["Davout"] == 4424
        assert res["reinforcement_messages"] == [
            "Ney fought with Davout beside him — massed effective strength: "
            "20,000 (lead) + 23,175 committed (Davout) = 43,175.",
            "Ney's supporting ally lost 4,424 men.",
        ]

    def test_a_co_located_attacker_names_his_lead(self):
        """FLIPPED CONSCIOUSLY (IQ-5 review D). This pinned the old
        subject-less pair ("Massed effective strength: …", "His supporting
        ally lost …"), which only read right under an arrival line naming
        the lead. With nobody arriving, nothing named whose mass it was —
        in the enemy phase "His" sat above the player's own marshal's lines.
        The co-located attacker is named now, mirroring the defender."""
        _w, res, _logs, losses = _battle(A_SAME, "Ney", "Mack")
        assert losses["Davout"] == 2195
        assert res["reinforcement_messages"] == [
            "Ney fought with Davout beside him — massed effective strength: "
            "30,000 (lead) + 19,312 committed (Davout) = 49,312.",
            "Ney's supporting ally lost 2,195 men.",
        ]

    def test_the_enemy_attacker_is_named_above_the_players_lines(self):
        """The finding's own geometry: Mack + Archduke John attack Ney +
        Davout, all at Swabia. Before, the first loss line was "His
        supporting ally lost 1,368 men" directly above Ney's own lines."""
        _w, res, _logs, losses = _battle(
            {"Mack": ("Swabia", 40000), "ArchdukeJohn": ("Swabia", 20000),
             "Ney": ("Swabia", 20000), "Davout": ("Swabia", 15000)}, "Mack", "Ney")
        msgs = res["reinforcement_messages"]
        assert msgs[0].startswith("Mack fought with Archduke John beside him — ")
        assert msgs[1] == f"Mack's supporting ally lost {losses['ArchdukeJohn']:,} men."
        assert msgs[2].startswith("Ney fought with Davout beside him — ")
        assert not any(m.startswith("His ") for m in msgs)

    def test_a_multi_word_attacking_lead_is_prose_in_both_lines(self):
        """IQ-5 review sweep, row 88 came back INERT: reverting `_rn(marshal.name)`
        to the raw key on the co-located ATTACKER's line left every pin green,
        because every attacking lead staged here was one word. Archduke
        Charles leads the stack now — both of his lines must carry the prose
        form, on the lead AND the man beside him, with no roster key anywhere."""
        _w, res, _logs, losses = _battle(
            {"ArchdukeCharles": ("Swabia", 40000), "ArchdukeJohn": ("Swabia", 20000),
             "Ney": ("Swabia", 20000)}, "ArchdukeCharles", "Ney")
        msgs = res["reinforcement_messages"]
        assert msgs[0].startswith(
            "Archduke Charles fought with Archduke John beside him — massed effective strength: ")
        assert msgs[1] == (f"Archduke Charles's supporting ally lost "
                           f"{losses['ArchdukeJohn']:,} men.")
        assert not any(_CAMEL.search(m) for m in msgs), msgs

    def test_a_mixed_attacker_stack_keeps_the_arrival_wording(self):
        """One man marched in AND one stood beside the lead: the arrival line
        names the lead, so the literal CO-6 / Session-66 strings stand (the
        CA8 source census pins them). Ney and Lannes stand on the field at
        Swabia; Davout marches in from Rhineland (which borders it)."""
        _w, res, _logs, _ = _battle(
            {"Ney": ("Swabia", 30000), "Lannes": ("Swabia", 20000),
             "Davout": ("Rhineland", 25000), "Mack": ("Swabia", 40000)}, "Ney", "Mack")
        msgs = res["reinforcement_messages"]
        assert msgs[0] == "Davout's forces arrived to reinforce Ney!"
        assert msgs[1].startswith("Massed effective strength: 30,000 (lead) + ")
        assert "(Davout, Lannes)" in msgs[1]
        assert msgs[2].startswith("His supporting allies lost ")

    def test_a_multi_word_co_located_attacker_lead_is_prose(self, monkeypatch):
        """The sweep's own finding: every co-located-ATTACKER pin above used
        a one-word lead, for which `_rn` is the identity, so dropping the
        display function from the attacker's two named lines changed
        nothing. Archduke Charles leads with Archduke John (+1) beside him
        against Ney, all at Swabia: both lines are prose, and with the
        lever down the pre-IQ-5 surface has no co-located lines at all."""
        placements = {"ArchdukeCharles": ("Swabia", 40000), "ArchdukeJohn": ("Swabia", 20000),
                      "Ney": ("Swabia", 30000)}
        _w, res, _logs, losses = _battle(placements, "ArchdukeCharles", "Ney")
        assert losses["ArchdukeJohn"] == 1034
        assert res["reinforcement_messages"] == [
            "Archduke Charles fought with Archduke John beside him — massed effective "
            "strength: 40,000 (lead) + 19,453 committed (Archduke John) = 59,453.",
            "Archduke Charles's supporting ally lost 1,034 men.",
        ]
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        _w, res, _logs, _ = _battle(placements, "ArchdukeCharles", "Ney")
        assert "reinforcement_messages" not in res

    def test_an_enemy_stack_is_named_in_prose_not_by_key(self):
        _w, res, _logs, losses = _battle(ENEMY_CO, "Ney", "Mack")
        msgs = res["reinforcement_messages"]
        assert msgs[0].startswith("Mack fought with Archduke John beside him — ")
        assert "(Archduke John)" in msgs[0]
        assert not any("ArchdukeJohn" in m for m in msgs)
        assert msgs[1] == f"Mack's supporting ally lost {losses['ArchdukeJohn']:,} men."

    def test_the_arrival_wordings_are_unchanged(self):
        """CO-6 and CA8-1: a reinforcer who MARCHED keeps the old sentences."""
        _w, res, _logs, _ = _battle(D_ADJ, "Moore", "Ney")
        assert res["reinforcement_messages"] == [
            "Ney was reinforced — massed effective strength: 20,000 (lead) + "
            "23,175 committed (Davout) = 43,175.",
            "Ney's supporting ally lost 4,089 men.",
        ]
        _w, res, _logs, _ = _battle(A_ADJ, "Ney", "Mack")
        assert res["reinforcement_messages"] == [
            "Davout's forces arrived to reinforce Ney!",
            "Massed effective strength: 30,000 (lead) + 18,750 committed (Davout) = 48,750.",
            "His supporting ally lost 2,610 men.",
        ]

    def test_lever_down_co_located_stacks_print_nothing(self, monkeypatch):
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        _w, res, _logs, _ = _battle(D_CO, "Moore", "Ney")
        assert res.get("reinforcement_messages") is None
        _w, res, _logs, _ = _battle(A_SAME, "Ney", "Mack")
        assert res.get("reinforcement_messages") is None

    def test_lever_down_arrivals_are_byte_identical(self, monkeypatch):
        _w, up, _logs, _ = _battle(D_ADJ, "Moore", "Ney")
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        _w, down, _logs, _ = _battle(D_ADJ, "Moore", "Ney")
        assert up["reinforcement_messages"] == down["reinforcement_messages"]


# ═══════════════════════════════════════════════════════════════════════
# PR-X2 R4 — the campaign log is bounded by the field, not the lead
# ═══════════════════════════════════════════════════════════════════════

class TestTheLogIsBoundedByTheField:
    def test_d_stub_prints_the_armys_loss(self):
        """Before: `(3,191 / 500 casualties)` for a 12,866-man loss."""
        _w, _res, logs, losses = _battle(D_STUB, "Moore", "Ney")
        assert losses["Ney"] + losses["Davout"] == 12866
        line = format_event_oneliner(logs[0])
        assert "(3,191 / 12,866 casualties)" in line
        assert "/ 500 casualties" not in line
        ev = logs[0]
        assert ev["defender_field_before"] == 48500
        assert ev["attacker_field_before"] == 100000
        # the lead's figure is still stamped for a reader that wants it
        assert ev["defender_strength_before"] == 500

    def test_a_stub_prints_the_armys_loss_on_the_attacker_side(self):
        _w, _res, logs, _ = _battle(A_STUB, "Ney", "Mack")
        assert "(5,465 / 5,754 casualties)" in format_event_oneliner(logs[0])

    def test_the_field_still_clamps_an_annihilation(self):
        line = format_event_oneliner({
            "type": "battle", "turn": 4, "location": "Paris",
            "attacker": "Moore", "attacker_nation": "Britain",
            "defender": "Ney", "defender_nation": "France",
            "outcome": "attacker_victory",
            "attacker_casualties": 3000, "defender_casualties": 60000,
            "attacker_strength_before": 100000, "defender_strength_before": 500,
            "attacker_field_before": 100000, "defender_field_before": 48500,
        })
        assert "48,500" in line and "60,000" not in line

    def test_an_event_without_the_field_reads_the_lead(self):
        """A solo battle, an old save, the lever down: the PT-D6 clamp stands."""
        line = format_event_oneliner({
            "type": "battle", "turn": 4, "location": "Paris",
            "attacker": "Moore", "attacker_nation": "Britain",
            "defender": "Ney", "defender_nation": "France",
            "outcome": "attacker_victory",
            "attacker_casualties": 3191, "defender_casualties": 12866,
            "attacker_strength_before": 100000, "defender_strength_before": 500,
        })
        assert "(3,191 / 500 casualties)" in line

    def test_the_combat_builders_are_untouched(self):
        """R4: the field figure is stamped by the executor, never by a third
        builder in combat.py (`TestTheClampCoversBothBuilders`)."""
        src = (ROOT / "backend" / "game_logic" / "combat.py").read_text(encoding="utf-8")
        assert "field_before" not in src
        assert "participant_losses" not in src

    def test_the_keys_survive_a_save(self):
        w, _res, logs, _ = _battle(D_STUB, "Moore", "Ney")
        with _quiet():
            back = WorldState.from_dict(json.loads(json.dumps(w.to_dict())))
        ev = [e for e in back.event_log if e.get("type") == "battle"][-1]
        assert ev["defender_field_before"] == 48500
        assert ev["defender_participant_losses"] == logs[0]["defender_participant_losses"]
        assert "(3,191 / 12,866 casualties)" in format_event_oneliner(ev)

    def test_lever_down_prints_the_old_clamp(self, monkeypatch):
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        _w, _res, logs, _ = _battle(D_STUB, "Moore", "Ney")
        assert "(3,191 / 500 casualties)" in format_event_oneliner(logs[0])
        assert not any("field_before" in k or "participant_losses" in k for k in logs[0])


# ═══════════════════════════════════════════════════════════════════════
# PR-X2 R5 — the dispatch mauls the man who bled
# ═══════════════════════════════════════════════════════════════════════

class TestTheDispatchMaulsTheManWhoBled:
    def test_d_stub_names_davout(self):
        """Before: "Ney was mauled at Paris: three-quarters of his corps —
        12,866 men". Ney's corps was 500 men; Davout lost 12,734."""
        w, _res, logs, losses = _battle(D_STUB, "Moore", "Ney")
        assert losses["Davout"] == 12734
        rows = {r["marshal"]: r for r in logs[0]["defender_participant_losses"]}
        assert rows["Davout"] == {"marshal": "Davout", "casualties": 12734,
                                  "strength_before": 48000}
        assert rows["Ney"]["casualties"] == 132
        _head, texts = _headline_texts(w)
        assert ("Sire — Davout was mauled at Paris: a quarter of his corps — "
                "12,734 men — lost in a single action.") in texts
        assert not any("Ney was mauled" in t for t in texts)

    def test_d_adj_mauls_nobody(self):
        """Ney and Davout each lost 13.6% — under the threshold. Before, the
        army's 6,814 divided by Ney's 20,000 mauled Ney."""
        w, _res, _logs, _ = _battle(D_ADJ, "Moore", "Ney")
        head, texts = _headline_texts(w)
        assert not any("mauled" in t for t in texts)
        assert head is None or head["class"] != "own_mauled"

    def test_lever_down_is_the_old_lead_only_beat(self, monkeypatch):
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        w, _res, _logs, _ = _battle(D_ADJ, "Moore", "Ney")
        head, texts = _headline_texts(w)
        assert head["class"] == "own_mauled"
        assert ("Sire — Ney was mauled at Paris: a quarter of his corps — "
                "6,814 men — lost in a single action.") == head["text"]
        w, _res, _logs, _ = _battle(D_STUB, "Moore", "Ney")
        _head, texts = _headline_texts(w)
        assert ("Sire — Ney was mauled at Paris: three-quarters of his corps — "
                "12,866 men — lost in a single action.") in texts

    @staticmethod
    def _world_with(rows):
        with _quiet():
            world = WorldState(player_nation="France")
        world.current_turn = 6
        world.event_log.append({
            "type": "battle", "turn": 6, "location": "Bohemia",
            "defender": "Ney", "defender_nation": "France",
            "defender_casualties": sum(r["casualties"] for r in rows),
            "defender_participant_losses": rows,
            "attacker": "ArchdukeCharles", "attacker_nation": "Austria",
        })
        return world

    def test_the_per_man_beat_keeps_the_absolute_floor(self):
        """WO-16's floor binds each man: 400 of 1,000 is 40%, and a scratch."""
        world = self._world_with([
            {"marshal": "Ney", "casualties": 0, "strength_before": 20000},
            {"marshal": "Davout", "casualties": 400, "strength_before": 1000}])
        _head, texts = _headline_texts(world)
        assert not any("mauled" in t for t in texts)

    def test_the_per_man_beat_fires_for_the_reinforcer(self):
        world = self._world_with([
            {"marshal": "Ney", "casualties": 10, "strength_before": 20000},
            {"marshal": "Davout", "casualties": 3000, "strength_before": 9000}])
        _head, texts = _headline_texts(world)
        assert any("Davout was mauled at Bohemia: a third of his corps — 3,000 men —" in t
                   for t in texts), texts
        assert not any("Ney was mauled" in t for t in texts)

    def test_a_man_no_longer_on_the_roster_is_skipped(self):
        world = self._world_with([
            {"marshal": "Ney", "casualties": 10, "strength_before": 20000},
            {"marshal": "NoSuchMarshal", "casualties": 9000, "strength_before": 10000}])
        _head, texts = _headline_texts(world)
        assert not any("mauled" in t for t in texts)


# ═══════════════════════════════════════════════════════════════════════
# PR-X2 R2 — no mechanical figure moves
# ═══════════════════════════════════════════════════════════════════════

def _mechanics(w, res, logs):
    ev = res["events"][0]
    return {
        "strengths": {n: m.strength for n, m in w.marshals.items()},
        "morale": {n: m.morale for n, m in w.marshals.items()},
        "event": {s: {k: ev[s][k] for k in ("casualties", "remaining", "morale")}
                  for s in ("attacker", "defender")},
        "log": {k: logs[0][k] for k in ("attacker_casualties", "defender_casualties",
                                        "attacker_strength_before",
                                        "defender_strength_before", "outcome")},
        "outcome": ev.get("outcome"),
    }


class TestNoMechanicalFigureMoves:
    def test_the_scope_lever_is_display_only(self, monkeypatch):
        w, res, logs, _ = _battle(D_STUB, "Moore", "Ney")
        up = _mechanics(w, res, logs)
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        w, res, logs, _ = _battle(D_STUB, "Moore", "Ney")
        assert _mechanics(w, res, logs) == up

    def test_the_trust_lever_is_display_only(self, monkeypatch):
        w, res, logs, _ = _battle(D_CO, "Moore", "Ney", trusts={"Davout": 10})
        up = _mechanics(w, res, logs)
        monkeypatch.setattr(CE, "TRUST_NAMES_ITS_PRICE", False)
        w, res, logs, _ = _battle(D_CO, "Moore", "Ney", trusts={"Davout": 10})
        assert _mechanics(w, res, logs) == up

    def test_every_new_number_is_an_int(self):
        """GR2: Godot crashes on floats."""
        _w, res, logs, _ = _battle(D_STUB, "Moore", "Ney")
        for side in ("attacker", "defender"):
            assert type(_side(res, side)["lead_remaining"]) is int
            assert type(logs[0][f"{side}_field_before"]) is int
            for row in logs[0][f"{side}_participant_losses"]:
                assert type(row["casualties"]) is int
                assert type(row["strength_before"]) is int


# ═══════════════════════════════════════════════════════════════════════
# PR-X3 R7 — one source for the arithmetic and the copy
# ═══════════════════════════════════════════════════════════════════════

def _old_scale(lead, ally, reach):
    """The pre-IQ-5 `_pair_contribution_scale`, verbatim — the drift oracle."""
    from backend.commands.objection_v2 import TrustTier, get_trust_tier
    scaling = CE._RELATIONSHIP_SCALING
    scale = scaling.get(lead.get_relationship(ally.name), 1.0)
    lead_jealous = getattr(lead, "jealous_of", None) == ally.name
    ally_jealous = getattr(ally, "jealous_of", None) == lead.name
    if lead_jealous or ally_jealous:
        jealous_one = lead if lead_jealous else ally
        if jealous_one.personality == "aggressive":
            return 0.0
        pair_rel = min(lead.get_relationship(ally.name), ally.get_relationship(lead.name))
        scale = scaling.get(pair_rel, 1.0)
    if reach and scale > 0.0:
        t = getattr(getattr(ally, "trust", None), "value", None)
        if t is not None and get_trust_tier(int(t)) == TrustTier.HOSTILE:
            scale *= CE.BROKEN_TRUST_CONTRIBUTION
    return scale


GRIEVANCES = ("none", "ally_cautious", "ally_aggressive", "lead_cautious", "lead_aggressive")


def _set_grievance(lead, ally, grievance):
    lead.jealous_of = None
    ally.jealous_of = None
    lead.personality = "cautious"
    ally.personality = "cautious"
    if grievance.startswith("ally_"):
        ally.jealous_of = lead.name
        ally.personality = grievance.split("_")[1]
    elif grievance.startswith("lead_"):
        lead.jealous_of = ally.name
        lead.personality = grievance.split("_")[1]


class TestOneSourceForTheArithmetic:
    def test_the_breakdown_has_exactly_the_contracted_keys(self):
        w = _boot()
        bd = pair_contribution_breakdown(w.marshals["Ney"], w.marshals["Davout"])
        assert set(bd) == {"scale", "relationship_scale", "trust_factor", "grievance",
                           "relationship", "trust"}
        assert bd["trust"] == 85 and type(bd["trust"]) is int

    def test_the_drift_census(self, monkeypatch):
        """relationship (both directions) x trust x grievance x FA-D23 lever:
        the refactor is arithmetic-identical, and the product equals its
        factors (so the copy cannot drift from the number)."""
        w = _boot()
        ex = CommandExecutor()
        lead, ally = w.marshals["Ney"], w.marshals["Davout"]
        cells = 0
        for reach in (True, False):
            monkeypatch.setattr(CE, "TRUST_REACHES_THE_FIELD", reach)
            for rel_la in (-2, -1, 0, 1, 2):
                for rel_al in (-2, -1, 0, 1, 2):
                    for trust in (100, 30, 29, 0):
                        for grievance in GRIEVANCES:
                            lead.relationships[ally.name] = rel_la
                            ally.relationships[lead.name] = rel_al
                            _trust(ally, trust)
                            _set_grievance(lead, ally, grievance)
                            old = _old_scale(lead, ally, reach)
                            bd = ex._combat._pair_contribution_breakdown(lead, ally)
                            assert ex._combat._pair_contribution_scale(lead, ally) == old
                            assert bd["scale"] == old
                            assert pair_contribution_breakdown(lead, ally) == bd
                            assert bd["scale"] == bd["relationship_scale"] * bd["trust_factor"]
                            assert bd["trust_factor"] in (1.0, CE.BROKEN_TRUST_CONTRIBUTION)
                            if bd["trust_factor"] < 1.0:
                                assert reach and trust < 30 and bd["scale"] > 0.0
                            if grievance == "none":
                                expected_g = ""
                            elif grievance.endswith("aggressive"):
                                expected_g = "aggressive"
                            else:
                                expected_g = "withheld"
                            assert bd["grievance"] == expected_g
                            cells += 1
        assert cells == 2 * 25 * 4 * 5

    def test_the_committed_sum_is_float_identical(self):
        w = _boot()
        ex = CommandExecutor()
        ney, dav, lannes = w.marshals["Ney"], w.marshals["Davout"], w.marshals["Lannes"]
        _trust(dav, 10)
        ney.relationships["Lannes"] = 1
        expected = 0.0
        for r in (dav, lannes):
            s = _old_scale(ney, r, True)
            expected += (CE.COMMITTED_ALPHA * r.strength * r.get_combat_effectiveness()
                         * r.get_attack_modifier(1.0, consume=False) * s)
        assert ex._combat._committed_reinforcement_strength(ney, [ney, dav, lannes], w) == expected

    @pytest.mark.parametrize("fraction,phrase", [
        (0.25, "a quarter of"), (0.5, "half"), (0.75, "three-quarters of"),
        (0.625, "about 62% of"), (0.3, "about 30% of")])
    def test_the_weight_phrase_is_true(self, fraction, phrase):
        assert weight_phrase(fraction) == phrase


# ═══════════════════════════════════════════════════════════════════════
# PR-X3 R8 — the muster row is branched on cause
# ═══════════════════════════════════════════════════════════════════════

OLD_HALF = "— but he and Ney are at odds; expect about half his weight"
TRUST_ONLY = ("— but his faith in you is spent (trust {t}); expect half the weight "
              "he would otherwise bring")
BOTH = ("— but he and Ney are at odds, and his faith in you is spent (trust {t}); "
        "expect a quarter of his weight")


def _muster_row(rel=0, trust=85, jealous=False):
    w = _boot()
    ney, dav, mack = w.marshals["Ney"], w.marshals["Davout"], w.marshals["Mack"]
    ney.relationships["Davout"] = rel
    dav.relationships["Ney"] = rel
    _trust(dav, trust)
    if jealous:
        dav.jealous_of = "Ney"          # Davout is cautious at boot
        assert dav.personality == "cautious"
    ce = CommandExecutor()._combat
    with _quiet():
        pv = ce._build_muster_preview(ney, mack, w, {"world": w})
    row = next(r for r in pv["rows"] if r["marshal"] == "Davout")
    return row, pv, ce


class TestTheMusterRowIsBranchedOnCause:
    def test_the_relationship_arm_is_verbatim(self):
        """PT-D's pin: "about half his weight" for a −1 pair at factory trust."""
        row, _pv, _ce = _muster_row(rel=-1, trust=85)
        assert row["withholds"] == OLD_HALF
        row, _pv, _ce = _muster_row(rel=0, trust=85, jealous=True)
        assert row["withholds"] == OLD_HALF

    def test_trust_alone_names_his_faith_not_a_quarrel(self):
        row, pv, ce = _muster_row(rel=0, trust=20)
        assert row["withholds"] == TRUST_ONLY.format(t=20)
        assert "at odds" not in row["withholds"]
        assert row["withholds"] in ce._format_muster_lines(pv)

    @pytest.mark.parametrize("rel", [1, 2])
    def test_friends_are_never_told_they_are_at_odds(self, rel):
        """A +1 friend brings 0.625 — half of the 1.25 he would otherwise bring.
        "Half the weight he would otherwise bring" is the true sentence."""
        row, _pv, _ce = _muster_row(rel=rel, trust=20)
        assert row["withholds"] == TRUST_ONLY.format(t=20)

    def test_both_causes_say_a_quarter(self):
        row, _pv, _ce = _muster_row(rel=-1, trust=20)
        assert row["withholds"] == BOTH.format(t=20)
        row, _pv, _ce = _muster_row(rel=0, trust=20, jealous=True)
        assert row["withholds"] == BOTH.format(t=20)

    def test_the_boundary_is_objection_v2s_line(self):
        row, _pv, _ce = _muster_row(rel=0, trust=30)
        assert not row.get("withholds")
        row, _pv, _ce = _muster_row(rel=0, trust=29)
        assert row["withholds"] == TRUST_ONLY.format(t=29)

    def test_the_word_broken_is_never_printed(self):
        """The card says "Strained" from 21 to 29 while the halving applies."""
        for rel, trust, jealous in ((0, 25, False), (-1, 25, False), (0, 25, True)):
            row, _pv, _ce = _muster_row(rel=rel, trust=trust, jealous=jealous)
            assert "Broken" not in row["withholds"] and "trust 25" in row["withholds"]

    def test_will_join_and_the_odds_are_untouched(self, monkeypatch):
        row, up, _ce = _muster_row(rel=-1, trust=20)
        monkeypatch.setattr(CE, "TRUST_NAMES_ITS_PRICE", False)
        row_down, down, _ce = _muster_row(rel=-1, trust=20)
        assert row["will_join"] is True and row_down["will_join"] is True
        assert up["attacker"]["committed_strength"] == down["attacker"]["committed_strength"]
        assert up["odds_band"] == down["odds_band"]

    @pytest.mark.parametrize("rel,trust,jealous", [
        (0, 20, False), (1, 20, False), (-1, 20, False), (0, 20, True), (-1, 85, False)])
    def test_lever_down_is_the_old_string(self, monkeypatch, rel, trust, jealous):
        monkeypatch.setattr(CE, "TRUST_NAMES_ITS_PRICE", False)
        row, _pv, _ce = _muster_row(rel=rel, trust=trust, jealous=jealous)
        assert row["withholds"] == OLD_HALF


# ═══════════════════════════════════════════════════════════════════════
# PR-X3 R9 — the trust note, on both sides of the field
# ═══════════════════════════════════════════════════════════════════════

class TestTheTrustNoteOnBothSides:
    def test_the_attackers_side(self):
        """Ney attacks Mack; Davout (trust 20) marches in from Rhineland. The
        massed line printed "+ 9,375 committed" with no reason."""
        _w, res, _logs, _ = _battle(A_ADJ, "Ney", "Mack", trusts={"Davout": 20})
        note = res["battle_report"]["trust_note"]
        assert note == ("Davout's faith in you is spent (trust 20) — he committed 9,375 "
                        "to the fight where he would have brought 18,750.")
        assert "+ 9,375 committed (Davout)" in res["reinforcement_messages"][1]
        assert note not in res["reinforcement_messages"]
        # "would have brought" is the healthy man's figure, same battle
        _w, healthy, _logs, _ = _battle(A_ADJ, "Ney", "Mack")
        assert "+ 18,750 committed (Davout)" in healthy["reinforcement_messages"][1]
        assert "trust_note" not in healthy["battle_report"]

    def test_the_defenders_side_when_he_marched_in(self):
        _w, res, _logs, _ = _battle(D_ADJ, "Moore", "Ney", trusts={"Davout": 10})
        assert res["battle_report"]["trust_note"] == (
            "Davout's faith in you is spent (trust 10) — he committed 11,587 to the "
            "fight where he would have brought 23,175.")

    def test_the_defenders_side_when_he_stood_beside_him(self):
        """The arm where nothing at all used to print."""
        _w, res, _logs, _ = _battle(D_CO, "Moore", "Ney", trusts={"Davout": 10})
        note = res["battle_report"]["trust_note"]
        assert note == ("Davout's faith in you is spent (trust 10) — he committed 11,587 "
                        "to the fight where he would have brought 23,175.")
        assert "+ 11,587 committed (Davout)" in res["reinforcement_messages"][0]
        assert "Broken" not in note

    def test_a_relationship_halving_is_not_a_trust_note(self):
        """Control: rel −1 at trust 85 also commits 11,418 — and it is NOT his
        faith, so nothing says it is."""
        _w, res, _logs, _ = _battle(D_CO, "Moore", "Ney", trusts={"Davout": 85},
                                    rels={("Ney", "Davout"): -1, ("Davout", "Ney"): -1})
        assert "+ 11,418 committed (Davout)" in res["reinforcement_messages"][0]
        assert "trust_note" not in res["battle_report"]
        _w, res, _logs, _ = _battle(D_CO, "Moore", "Ney")
        assert "trust_note" not in res["battle_report"]

    def test_the_enemys_disaffection_is_readable(self):
        """FA-D23's own promise: the player can read enemy disaffection off the
        same rule. No trust number for a foreign court's marshal.

        FLIPPED CONSCIOUSLY (IQ-5 review A): the sentence was the absolute
        "half his weight never reached the field", false for every
        non-neutral pair; it is relative now (`_faith_share_clause`)."""
        _w, res, _logs, _ = _battle(ENEMY_CO, "Ney", "Mack", trusts={"ArchdukeJohn": 5})
        note = res["battle_report"]["trust_note"]
        assert note == ("Archduke John fought for Austria without conviction — he brought "
                        "half what he otherwise would.")
        assert "trust" not in note and "ArchdukeJohn" not in note
        assert "his weight" not in note        # the absolute form is gone
        _w, res, _logs, _ = _battle(ENEMY_CO, "Ney", "Mack", trusts={"ArchdukeJohn": 65})
        assert "trust_note" not in res["battle_report"]

    def test_the_enemys_fraction_is_the_trust_factor_itself(self, monkeypatch):
        """At the blessed 0.5 the kept and the lost fractions are both "half",
        so a non-0.5 factor is the only arm that tells a relative clause from
        its complement. FLIPPED CONSCIOUSLY (review A): it used to pin the
        complement ("three-quarters … never reached"); the relative clause
        quotes the factor ("a quarter of what he otherwise would")."""
        monkeypatch.setattr(CE, "BROKEN_TRUST_CONTRIBUTION", 0.25)
        _w, res, _logs, _ = _battle(ENEMY_CO, "Ney", "Mack", trusts={"ArchdukeJohn": 5})
        assert res["battle_report"]["trust_note"] == (
            "Archduke John fought for Austria without conviction — he brought a "
            "quarter of what he otherwise would.")

    def test_a_battle_the_player_did_not_fight_says_nothing(self):
        _w, res, _logs, _ = _battle(AI_V_AI, "Castanos", "Mack", trusts={"ArchdukeJohn": 5})
        assert "trust_note" not in res["battle_report"]
        for side in ("attacker", "defender"):
            for c in res["battle_diorama"][side]["contingents"]:
                assert "faith" not in c

    def test_no_halving_no_note(self, monkeypatch):
        monkeypatch.setattr(CE, "TRUST_REACHES_THE_FIELD", False)
        _w, res, _logs, _ = _battle(D_CO, "Moore", "Ney", trusts={"Davout": 10})
        assert "trust_note" not in res["battle_report"]

    def test_lever_down_names_nothing(self, monkeypatch):
        monkeypatch.setattr(CE, "TRUST_NAMES_ITS_PRICE", False)
        for placements, a, t, trusts in (
                (A_ADJ, "Ney", "Mack", {"Davout": 20}),
                (D_CO, "Moore", "Ney", {"Davout": 10}),
                (ENEMY_CO, "Ney", "Mack", {"ArchdukeJohn": 5})):
            _w, res, _logs, _ = _battle(placements, a, t, trusts=trusts)
            assert "trust_note" not in res["battle_report"]
            for side in ("attacker", "defender"):
                for c in res["battle_diorama"][side]["contingents"]:
                    assert "faith" not in c


# ═══════════════════════════════════════════════════════════════════════
# PR-X3 R11 — the diorama's `faith` caption
# ═══════════════════════════════════════════════════════════════════════

def _contingent(res, side, name):
    return next(c for c in res["battle_diorama"][side]["contingents"] if c["name"] == name)


class TestTheDioramaCaption:
    def test_the_players_marshal(self):
        """FLIPPED CONSCIOUSLY (review A): the absolute "half his weight
        reached the field" became the relative clause."""
        _w, res, _logs, _ = _battle(D_CO, "Moore", "Ney", trusts={"Davout": 10})
        dav = _contingent(res, "defender", "Davout")
        assert dav["faith"] == ("Faith spent (trust 10): he brought half what he "
                                "otherwise would.")
        assert dav["committed"] == 30000          # the figure is left alone
        assert "faith" not in _contingent(res, "defender", "Ney")

    def test_the_enemys_marshal(self):
        """FLIPPED CONSCIOUSLY (review A)."""
        _w, res, _logs, _ = _battle(ENEMY_CO, "Ney", "Mack", trusts={"ArchdukeJohn": 5})
        john = _contingent(res, "defender", "ArchdukeJohn")
        assert john["faith"] == ("Without conviction: he brought half what he otherwise "
                                 "would.")

    def test_a_healthy_field_has_no_caption(self):
        _w, res, _logs, _ = _battle(D_CO, "Moore", "Ney")
        assert "faith" not in _contingent(res, "defender", "Davout")

    def test_the_no_show_shelf_is_never_captioned(self, monkeypatch):
        """A man who never reached the field brought none of his weight, so he
        carries no caption even if a record names him.

        The battle must stay COORDINATED to reach the guard: a lone reinforcer
        who fails to arrive turns the fight into a solo battle, and the solo
        path computes no faith records at all (the sweep caught a first cut
        built that way as INERT). So: Ney and Davout stand together at Paris
        (coordinated), and Soult — literal, so he never marches unordered —
        waits at Berry and lands on the shelf as `refused`. A record is forced
        for BOTH men; Davout is the positive control that it really captions."""
        w = _stage(_boot(), {**D_CO, "Soult": ("Berry", 20000)})
        assert w.marshals["Soult"].personality == "literal"
        men = [w.marshals["Davout"], w.marshals["Soult"]]

        def forced(self, attacker, defender, atk, dfn):
            return [{"marshal": m, "side": "defender", "trust": 10,
                     "trust_factor": 0.5, "committed": 1, "full": 2} for m in men]

        monkeypatch.setattr(CE, "_faith_records", forced)
        res, _logs = _fight(w, "Moore", "Ney", 3)
        soult = _contingent(res, "defender", "Soult")
        davout = _contingent(res, "defender", "Davout")
        assert soult["status"] == "refused"
        assert "faith" not in soult
        assert davout["status"] == "engaged"
        # FLIPPED CONSCIOUSLY (review A): the caption's new, shorter prefix.
        assert davout["faith"].startswith("Faith spent (trust 10):")


# ═══════════════════════════════════════════════════════════════════════
# PR-X3 R10 — the jealousy card reads the breakdown
# ═══════════════════════════════════════════════════════════════════════

class TestTheJealousyCard:
    @staticmethod
    def _card(trust, personality="cautious"):
        w = _boot()
        dav, ney = w.marshals["Davout"], w.marshals["Ney"]
        dav.jealous_of = "Ney"
        dav.personality = personality
        dav.jealousy_turns_remaining = 3
        _trust(dav, trust)
        return J._standing_cost_detail(dav, ney), dav.strength

    @staticmethod
    def _old(men):
        return (f"Free, and it fixes nothing. For 3 more turns he brings about half the "
                f"weight of his {men:,} men to any battle Ney leads, and the quarrel may "
                f"harden further.")

    @pytest.mark.parametrize("trust", [85, 30])
    def test_at_trust_30_and_above_it_is_byte_identical(self, trust):
        text, men = self._card(trust)
        assert text == self._old(men)

    @pytest.mark.parametrize("trust", [29, 20])
    def test_below_30_it_gives_the_true_fraction_and_names_his_faith(self, trust):
        text, men = self._card(trust)
        assert text == (f"Free, and it fixes nothing. For 3 more turns he brings a quarter "
                        f"of the weight of his {men:,} men to any battle Ney leads, for his "
                        f"faith in you is spent (trust {trust}), and the quarrel may harden "
                        f"further.")

    def test_the_aggressive_arm_is_untouched(self):
        text, men = self._card(20, personality="aggressive")
        assert f"he brings NONE of his {men:,} men" in text
        assert "faith" not in text

    def test_lever_down_is_the_old_card(self, monkeypatch):
        monkeypatch.setattr(CE, "TRUST_NAMES_ITS_PRICE", False)
        text, men = self._card(20)
        assert text == self._old(men)


# ═══════════════════════════════════════════════════════════════════════
# The harness — the digest prints both scopes and the trust note
# ═══════════════════════════════════════════════════════════════════════

def _digest(tmp_path):
    sys.path.insert(0, str(ROOT / "tools"))
    import playtest_driver as drv
    meta = {"name": "iq5", "seed": 3, "llm": "mock", "transport": "in-process",
            "policy": {}}
    return drv.Digest(tmp_path, meta)


def _digest_lines(tmp_path, report):
    dg = _digest(tmp_path)
    dg.battle(report)
    return [ln for ln in (tmp_path / "digest.md").read_text(encoding="utf-8").splitlines()
            if "⚔" in ln]


class TestTheDigest:
    def test_a_real_report_prints_both_scopes_and_the_note(self, tmp_path):
        _w, res, _logs, _ = _battle(D_ADJ, "Moore", "Ney", trusts={"Davout": 10})
        (line,) = _digest_lines(tmp_path, res["battle_report"])
        assert "Moore (lost 3712) vs Ney (lost 2626, own corps)" in line
        assert line.endswith(" — Davout's faith in you is spent (trust 10) — he "
                             "committed 11,587 to the fight where he would have "
                             "brought 23,175.")

    def test_a_note_on_several_lines_stays_on_one(self, tmp_path):
        report = {"casualty_summary": {"attacker_name": "Moore", "attacker_casualties": 1,
                                       "defender_name": "Ney", "defender_casualties": 2},
                  "trust_note": "A is spent.\n  B is spent."}
        (line,) = _digest_lines(tmp_path, report)
        assert line.endswith("(lost 2) — A is spent. B is spent.")

    def test_absent_or_null_keys_print_the_old_line(self, tmp_path):
        report = {"casualty_summary": {"attacker_name": "Moore", "attacker_casualties": 10,
                                       "defender_name": "Ney", "defender_casualties": 20,
                                       "defender_casualties_scope": None},
                  "trust_note": None}
        (line,) = _digest_lines(tmp_path, report)
        assert line == "  - ⚔ Moore (lost 10) vs Ney (lost 20)"


# ═══════════════════════════════════════════════════════════════════════
# The enemy-phase transport — the defender case only arrives this way
# ═══════════════════════════════════════════════════════════════════════

class TestTheEnemyPhaseTransportKeepsTheKeys:
    def test_the_visible_enemy_phase_carries_scope_and_note(self):
        import backend.main as M
        w, res, _logs, _ = _battle(D_ADJ, "Moore", "Ney", trusts={"Davout": 10})
        phase = {"total_actions": 1,
                 "nations": {"Britain": {"actions": [res], "action_count": 1}}}
        with _quiet():
            visible = M._build_visible_enemy_phase(phase, w)
        (action,) = visible["nations"]["Britain"]["actions"]
        assert action["battle_report"]["casualty_summary"]["defender_casualties_scope"] == "own corps"
        assert action["battle_report"]["trust_note"].startswith("Davout's faith in you")
        d = action["events"][0]["defender"]
        assert d["casualties_scope"] == "army" and d["lead_remaining"] == 17374


# ═══════════════════════════════════════════════════════════════════════
# The clients — census pins on FUNCTION BODIES, comment lines stripped
# ═══════════════════════════════════════════════════════════════════════

_GD_TOP_LEVEL = re.compile(
    r"^(func |static func |var |const |signal |class |class_name |enum |extends |@)")


def _gd_code(src: str, func: str) -> str:
    """The body of GDScript `func <func>(` with full-line comments dropped
    (an inline `#` split would gut every `[color=#…` bbcode string).

    The body ends at the next TOP-LEVEL declaration, not at the next
    column-0 character: `enemy_phase_dialog.gd` has string literals that
    span a raw newline, whose continuation (`")`) sits at column 0."""
    lines = src.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(f"func {func}("))
    body = []
    for ln in lines[start + 1:]:
        if _GD_TOP_LEVEL.match(ln):
            break
        body.append(ln)
    return "\n".join(ln for ln in body if not ln.lstrip().startswith("#"))


def _body(file: str, func: str) -> str:
    return _gd_code((GD / file).read_text(encoding="utf-8"), func)


def _markers(code: str) -> list:
    m = re.search(r"failure_markers = \[(.*?)\]", code, re.S)
    assert m, "no failure_markers list in the body"
    return re.findall(r'"([^"]+)"', m.group(1))


class TestTheCensusHelperReadsCodeNotComments:
    def test_a_key_named_only_in_a_comment_is_not_counted(self):
        src = ("func a():\n"
               "\t# report.get(\"trust_note\", \"\") is read here, says the comment\n"
               "\tvar x = 1\n"
               "func b():\n"
               "\tvar t = report.get(\"trust_note\", \"\")\n")
        assert 'report.get("trust_note"' not in _gd_code(src, "a")
        assert 'report.get("trust_note"' in _gd_code(src, "b")
        assert "var x = 1" in _gd_code(src, "a") and "var t" not in _gd_code(src, "a")


class TestTheTerminalReadsBothScopes:
    CODE = property(lambda self: _body("main.gd", "_display_berthier_report"))

    def test_the_defender_label_is_built_and_printed(self):
        code = self.CODE
        assert 'casualty.get("defender_casualties_scope", "")' in code
        assert 'var def_label = def_name if def_scope == "" else def_name + "\'s " + def_scope' in code
        casualties = next(ln for ln in code.splitlines() if "Casualties: " in ln)
        assert '" | " + def_label + " "' in casualties
        assert '" | " + def_name + " "' not in casualties

    def test_the_scope_reads_are_null_safe(self):
        code = self.CODE
        assert "if not (def_scope is String):" in code
        assert "if not (atk_scope is String):" in code
        assert 'str(casualty.get("defender_casualties_scope"' not in code

    def test_the_trust_note_is_read_after_the_jealousy_note(self):
        code = self.CODE
        assert 'var tr_note = report.get("trust_note", "")' in code
        assert 'if tr_note is String and tr_note != "":' in code
        assert '+ tr_note + "[/color]"' in code
        assert 'str(report.get("trust_note"' not in code
        assert code.index('report.get("jealousy_note"') < code.index('report.get("trust_note"')


class TestTheMassAndLossLinesAreNotFailures:
    def test_the_terminal_has_three_colours_not_two(self):
        code = _body("main.gd", "_display_reinforcement_messages")
        fail_arm = code.split("elif is_failure:")[1].split("else:")[0]
        info_arm = code.split("elif is_failure:")[1].split("else:")[1]
        assert "COLOR_REINF_FAIL" in fail_arm and "COLOR_REINF_INFO" not in fail_arm
        assert "COLOR_REINF_INFO" in info_arm and "COLOR_REINF_FAIL" not in info_arm
        assert "text.findn(marker) >= 0" in code

    def test_the_enemy_phase_has_three_colours_not_two(self):
        """FLIPPED CONSCIOUSLY (IQ-5 review G): the arrival / no-show colours
        are no longer the literals COLOR_SUCCESS / COLOR_ERROR but the SIDE's
        (`arrive_color` / `noshow_color`, set from `_reinforcement_side`).
        The three-kinds rule this pinned still holds — report lines stay
        COLOR_INFO — and is asserted in full below."""
        code = _body("enemy_phase_dialog.gd", "_format_action")
        assert "var reinf_color = Utils.COLOR_INFO" in code
        assert 'if msg_text.find("arrived") >= 0:\n\t\t\t\treinf_color = arrive_color' in code
        assert "if msg_text.findn(marker) >= 0:\n\t\t\t\t\t\treinf_color = noshow_color" in code
        assert 'Utils.COLOR_SUCCESS if msg_text.find("arrived") >= 0 else COLOR_ERROR' not in code
        assert "if not (reinf_msgs is Array):" in code

    def test_both_clients_hold_the_same_marker_list(self):
        main = _markers(_body("main.gd", "_display_reinforcement_messages"))
        epd = _markers(_body("enemy_phase_dialog.gd", "_format_action"))
        assert main == epd and len(main) >= 5

    def test_every_no_show_reason_carries_a_marker_and_no_report_line_does(self):
        """Read off the producer: every not-arrived sentence `_execute_attack`
        can append is painted red by both clients, and every other line it
        appends (arrivals, mass, allied losses) is NOT."""
        markers = [m.lower() for m in _markers(_body("main.gd",
                                                     "_display_reinforcement_messages"))]
        tree = ast.parse(textwrap.dedent(inspect.getsource(CE._execute_attack)))

        def text_of(node):
            return "".join(n.value for n in ast.walk(node)
                           if isinstance(n, ast.Constant) and isinstance(n.value, str))

        reasons = [text_of(n.value) for n in ast.walk(tree)
                   if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "friendly_reason"
                           for t in n.targets)]
        assert len(reasons) >= 7, reasons
        for r in reasons:
            assert any(m in r.lower() for m in markers), r
            assert "arrived" not in r

        appended = [n.args[0] for n in ast.walk(tree)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "append" and isinstance(n.func.value, ast.Name)
                    and n.func.value.id == "reinf_messages"]
        reports = [text_of(a) for a in appended
                   if not (isinstance(a, ast.Name) and a.id == "friendly_reason")]
        assert sum("massed effective strength" in r.lower() for r in reports) >= 3
        # "His supporting ally…", "His supporting allies…", "{X}'s supporting
        # {ally|allies} lost…" (the last with the noun in a variable)
        assert sum("supporting" in r.lower() and "lost" in r.lower()
                   for r in reports) >= 3
        for r in reports:
            if "arrived" in r:
                continue
            assert not any(m in r.lower() for m in markers), r


class TestTheEnemyPhaseDialogReadsTheKeys:
    def test_the_battle_line_names_whose_losses(self):
        code = _body("enemy_phase_dialog.gd", "_format_battle")
        assert 'var atk_is_army = str(attacker.get("casualties_scope", "")) == "army"' in code
        assert 'var def_is_army = str(defender.get("casualties_scope", "")) == "army"' in code
        assert 'var atk_lead_rem = attacker.get("lead_remaining", null)' in code
        assert 'var def_lead_rem = defender.get("lead_remaining", null)' in code
        assert "if def_is_army and (def_lead_rem is int or def_lead_rem is float):" in code
        assert "\"'s army: \"" in code and "\"'s own corps: \"" in code

    def test_the_berthier_whitelist_reads_scope_and_note(self):
        code = _body("enemy_phase_dialog.gd", "_format_berthier_report")
        assert 'var def_scope = casualty.get("defender_casualties_scope", "")' in code
        assert 'var atk_scope = casualty.get("attacker_casualties_scope", "")' in code
        assert "if not (def_scope is String):" in code
        assert 'var def_label = def_name if def_scope == "" else def_name + "\'s " + def_scope' in code
        assert '" | " + def_label + " "' in code and '" | " + def_name + " "' not in code
        assert 'var tr_note = report.get("trust_note", "")' in code
        assert 'if tr_note is String and tr_note != "":' in code
        assert "Utils.humanize_nation_keys_in_text(tr_note)" in code
        assert code.index('report.get("jealousy_note"') < code.index('report.get("trust_note"')


class TestTheDioramaDrawsTheCaption:
    def test_the_caption_is_read_null_safe(self):
        code = _body("battle_diorama.gd", "_make_block")
        assert 'var faith_v = c.get("faith", null)' in code
        assert 'var faith := str(faith_v) if faith_v is String else ""' in code
        assert 'if faith != "":' in code
        assert 'str(c.get("faith"' not in code

    def test_the_shelf_never_reads_the_caption(self):
        """FLIPPED CONSCIOUSLY (IQ-5 review B): this used to pin a null-safe
        read in `_populate_shelf` — an arm the backend can never reach (it
        attaches `faith` only to a man who stood on the field, and the shelf
        holds only the absent). Deleted; its comment was false."""
        code = _body("battle_diorama.gd", "_populate_shelf")
        assert 'c.get("faith"' not in code
        assert "faith" not in code.replace("# ", "")  # no code names it


# ═══════════════════════════════════════════════════════════════════════
# IQ-5 REVIEW ROUND — pins for rulings A..H (each finding's own geometry)
# ═══════════════════════════════════════════════════════════════════════

_CAMEL = re.compile(r"[a-z][A-Z]")
_GD_TEXT = lambda f: (GD / f).read_text(encoding="utf-8")  # noqa: E731


def _staged_battle(placements, attacker, target, seed=3, trusts=None, lead=None,
                   ally=None):
    """`_battle`, but also returns the pair breakdown read BEFORE the fight
    (the engine's own `scale`), so a pin can show the geometry is one where
    an absolute fraction and the relative clause disagree."""
    w = _stage(_boot(), placements)
    for name, value in (trusts or {}).items():
        _trust(w.marshals[name], value)
    bd = (pair_contribution_breakdown(w.marshals[lead], w.marshals[ally])
          if lead and ally else None)
    res, logs = _fight(w, attacker, target, seed)
    return w, res, logs, bd


class TestTheFaithCopyIsRelative:
    """Ruling A (#3 #4 #7 #12). The caption and the enemy note quoted an
    ABSOLUTE fraction built from the trust factor alone — false on every
    Rival (0.25 total) and Friendly (0.625) pair. They read the shared
    relative clause now. Each pin is on a geometry where the absolute form
    WOULD have lied: the engine's total scale differs from the factor."""

    REL = "he brought half what he otherwise would"

    def test_the_player_rival(self):
        """Ney–Bernadotte, the shipped Rival pair (−1 both ways)."""
        _w, res, _logs, bd = _staged_battle(
            {"Ney": ("Paris", 20000), "Bernadotte": ("Paris", 30000),
             "Moore": ("Artois", 60000)}, "Moore", "Ney",
            trusts={"Bernadotte": 20}, lead="Ney", ally="Bernadotte")
        assert bd["relationship"] == -1 and bd["scale"] == 0.25
        assert bd["trust_factor"] == 0.5
        cap = _contingent(res, "defender", "Bernadotte")["faith"]
        assert cap == f"Faith spent (trust 20): {self.REL}."
        assert "his weight" not in cap          # the absolute form is gone
        # the note's two figures are the same ratio the caption states
        assert res["battle_report"]["trust_note"] == (
            "Bernadotte's faith in you is spent (trust 20) — he committed 5,709 to "
            "the fight where he would have brought 11,418.")

    def test_the_player_friend(self):
        """Ney–Lannes (+1): 0.625 of his base weight reached — "half his
        weight" was false; half of what he would otherwise bring is true."""
        _w, res, _logs, bd = _staged_battle(
            {"Ney": ("Paris", 20000), "Lannes": ("Paris", 30000),
             "Moore": ("Artois", 60000)}, "Moore", "Ney",
            trusts={"Lannes": 20}, lead="Ney", ally="Lannes")
        assert bd["relationship"] == 1 and bd["scale"] == 0.625
        assert _contingent(res, "defender", "Lannes")["faith"] == (
            f"Faith spent (trust 20): {self.REL}.")
        assert res["battle_report"]["trust_note"] == (
            "Lannes's faith in you is spent (trust 20) — he committed 16,778 to the "
            "fight where he would have brought 33,556.")

    def test_the_enemy_rival(self):
        """Kutuzov–Buxhowden (−1): three-quarters never reached; the old
        note said half."""
        _w, res, _logs, bd = _staged_battle(
            {"Ney": ("Franconia", 40000), "Kutuzov": ("Swabia", 30000),
             "Buxhowden": ("Swabia", 20000)}, "Ney", "Kutuzov",
            trusts={"Buxhowden": 20}, lead="Kutuzov", ally="Buxhowden")
        assert bd["relationship"] == -1 and bd["scale"] == 0.25
        assert res["battle_report"]["trust_note"] == (
            f"Buxhowden fought for Russia without conviction — {self.REL}.")
        assert _contingent(res, "defender", "Buxhowden")["faith"] == (
            f"Without conviction: {self.REL}.")

    def test_the_enemy_friend(self):
        """Archduke Charles–Archduke John (+1): 62.5% reached, the old note
        said half never did."""
        _w, res, _logs, bd = _staged_battle(
            {"Ney": ("Franconia", 40000), "ArchdukeCharles": ("Swabia", 30000),
             "ArchdukeJohn": ("Swabia", 20000)}, "Ney", "ArchdukeCharles",
            trusts={"ArchdukeJohn": 5}, lead="ArchdukeCharles", ally="ArchdukeJohn")
        assert bd["relationship"] == 1 and bd["scale"] == 0.625
        assert res["battle_report"]["trust_note"] == (
            f"Archduke John fought for Austria without conviction — {self.REL}.")
        assert _contingent(res, "defender", "ArchdukeJohn")["faith"] == (
            f"Without conviction: {self.REL}.")

    def test_one_source_for_the_three_sentences(self):
        from backend.commands import combat_executor as cex
        assert cex._faith_share_clause(0.5) == self.REL
        assert cex._faith_share_clause(0.25) == "he brought a quarter of what he otherwise would"
        src = inspect.getsource(cex.CombatExecutor._faith_captions)
        assert src.count("_faith_share_clause(") == 2
        assert "weight_phrase" not in src
        note = inspect.getsource(cex.CombatExecutor._compose_trust_note)
        assert note.count("_faith_share_clause(") == 1
        assert "1.0 - " not in note


def _rm(placements, attacker, target, seed=3, trusts=None):
    return _battle(placements, attacker, target, seed=seed, trusts=trusts)[1].get(
        "reinforcement_messages")


# The geometries ruling C names.
LEAD_JOHN_CO = {"Ney": ("Franconia", 40000), "ArchdukeJohn": ("Swabia", 20000),
                "Mack": ("Swabia", 30000)}
JOHN_ARRIVES_ATK = {"Mack": ("Swabia", 40000), "Ney": ("Franconia", 20000),
                    "ArchdukeJohn": ("Bohemia", 30000)}


class TestEveryReinforcementNameIsProse:
    """Ruling C (#1 #6 #9 #13 #15 #17). The first cut humanised the arrival
    line alone; the massed parenthesis, every no-show arm and a multi-word
    lead's loss line still printed roster keys (R7)."""

    def test_a_multi_word_lead_is_named_in_both_lines(self):
        """The pin that should have caught it used Mack, a one-word lead."""
        assert _rm(LEAD_JOHN_CO, "Ney", "ArchdukeJohn") == [
            "Archduke John fought with Mack beside him — massed effective strength: "
            "20,000 (lead) + 23,175 committed (Mack) = 43,175.",
            "Archduke John's supporting ally lost 4,268 men.",
        ]

    def test_a_multi_word_arrival_on_the_attacker_side(self):
        assert _rm(JOHN_ARRIVES_ATK, "Mack", "Ney", seed=1) == [
            "Archduke John's forces arrived to reinforce Mack!",
            "Massed effective strength: 40,000 (lead) + 22,500 committed "
            "(Archduke John) = 62,500.",
            "His supporting ally lost 1,355 men.",
        ]

    def test_the_no_show_seeds_are_prose_too(self):
        """Seeds 2 and 6 are no-shows: "ArchdukeJohn could not reach…"."""
        for seed in (2, 6):
            assert _rm(JOHN_ARRIVES_ATK, "Mack", "Ney", seed=seed) == [
                "Archduke John could not reach the battlefield in time."]

    @pytest.mark.parametrize("seed", range(1, 9))
    def test_no_roster_key_on_any_seed(self, seed):
        for placements, a, t in ((JOHN_ARRIVES_ATK, "Mack", "Ney"),
                                 (LEAD_JOHN_CO, "Ney", "ArchdukeJohn"),
                                 (ENEMY_CO, "Ney", "Mack")):
            for m in _rm(placements, a, t, seed=seed) or []:
                assert not _CAMEL.search(m), (seed, m)

    def test_lever_down_is_720597da_literally(self, monkeypatch):
        """Compared with the LITERAL pre-IQ-5 strings, not with lever-up (the
        first pin compared lever-up to lever-down on one-word Davout, so it
        could see neither IQ5-10's unconditional rename nor the prior form)."""
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        assert _rm(JOHN_ARRIVES_ATK, "Mack", "Ney", seed=1) == [
            "ArchdukeJohn's forces arrived to reinforce Mack!",
            "Massed effective strength: 40,000 (lead) + 22,500 committed "
            "(ArchdukeJohn) = 62,500.",
            "His supporting ally lost 1,355 men.",
        ]
        assert _rm(JOHN_ARRIVES_ATK, "Mack", "Ney", seed=2) == [
            "ArchdukeJohn could not reach the battlefield in time."]

    def test_the_display_function_is_the_lever(self, monkeypatch):
        ce = CommandExecutor()._combat
        assert ce._reinf_name("ArchdukeJohn") == "Archduke John"
        assert ce._reinf_name("Ney") == "Ney"
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        assert ce._reinf_name("ArchdukeJohn") == "ArchdukeJohn"

    def test_every_no_show_reason_names_through_the_display_function(self):
        """AST census: no `friendly_reason` interpolates the raw
        `r['marshal']` / `marshal.name` — only `_who` / `_rn(...)`."""
        tree = ast.parse(textwrap.dedent(inspect.getsource(CE._execute_attack)))
        reasons = [n.value for n in ast.walk(tree)
                   if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "friendly_reason"
                           for t in n.targets)]
        assert len(reasons) >= 7
        for node in reasons:
            for sub in ast.walk(node):
                if isinstance(sub, ast.FormattedValue):
                    src = ast.unparse(sub.value)
                    assert src == "_who" or src.startswith("_rn("), src


# E: a 90-man Davout stands beside Ney at Paris; the rubble rule takes him.
D_CO_RUBBLE = {"Ney": ("Paris", 20000), "Davout": ("Paris", 90),
               "Moore": ("Artois", 100000)}


class TestTheRubbleIsReported:
    """Ruling E (#2). A co-located man wiped out by `take_casualties`'
    `< 50 -> 0` rule was reported with his distributed share ("lost 48
    men" for a 90-man corps that was gone)."""

    def test_the_loss_line_rows_and_diorama_say_ninety(self):
        _w, res, logs, losses = _battle(D_CO_RUBBLE, "Moore", "Ney", seed=1)
        assert losses["Davout"] == 90
        assert res["reinforcement_messages"][1] == "Ney's supporting ally lost 90 men."
        rows = {r["marshal"]: r for r in logs[0]["defender_participant_losses"]}
        assert rows["Davout"] == {"marshal": "Davout", "casualties": 90,
                                  "strength_before": 90}
        dav = _contingent(res, "defender", "Davout")
        assert (dav["casualties"], dav["remaining"], dav["status"]) == (90, 0, "destroyed")

    def test_the_army_figure_stays_mechanical(self):
        """R2: the event and the log keep the distributed sum (10,778), not
        the realised 10,820 — they feed record_battle, the war score, the
        decisive test and the campaign ledger."""
        _w, res, logs, losses = _battle(D_CO_RUBBLE, "Moore", "Ney", seed=1)
        assert _side(res, "defender")["casualties"] == 10778
        assert logs[0]["defender_casualties"] == 10778
        assert losses["Ney"] + losses["Davout"] == 10820

    def test_a_man_who_survives_the_battle_is_not_read_as_rubble(self):
        """Seed 2: Davout loses 38 and keeps 52 — above the rubble line. He is
        not reported as lost whole (the hazard's capture trap: the figure is
        read BEFORE capture or retreat move anyone)."""
        _w, res, logs, _losses = _battle(D_CO_RUBBLE, "Moore", "Ney", seed=2)
        assert res["reinforcement_messages"][1] == "Ney's supporting ally lost 38 men."
        rows = {r["marshal"]: r for r in logs[0]["defender_participant_losses"]}
        assert rows["Davout"]["casualties"] == 38
        assert _contingent(res, "defender", "Davout")["remaining"] == 52

    def test_it_is_display_only(self, monkeypatch):
        w, res, logs, _ = _battle(D_CO_RUBBLE, "Moore", "Ney", seed=1)
        up = _mechanics(w, res, logs)
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        w, res, logs, _ = _battle(D_CO_RUBBLE, "Moore", "Ney", seed=1)
        assert _mechanics(w, res, logs) == up


LONE_NEY_CO = {"Ney": ("Franconia", 60), "Mack": ("Swabia", 70000),
               "ArchdukeJohn": ("Swabia", 40000)}
LONE_NEY_SOLO = {"Ney": ("Franconia", 60), "Mack": ("Swabia", 70000)}


class TestALoneSidesLossIsOneFigure:
    """Ruling F (#8). A LONE side destroyed by the rubble rule (or the
    overkill cap) printed its raw figure under a bare name while the report
    printed the applied loss — on both battle paths."""

    def test_the_coordinated_path(self):
        _w, res, logs, _ = _battle(LONE_NEY_CO, "Mack", "Ney", seed=1)
        d = _side(res, "defender")
        assert d["casualties"] == 28              # the mechanical raw figure stands
        assert d["applied_casualties"] == 60
        assert type(d["applied_casualties"]) is int
        assert "applied_casualties" not in _side(res, "attacker")   # an army side
        assert _cs(res)["defender_casualties"] == 60
        assert logs[0]["defender_casualties"] == 28
        assert logs[0]["defender_applied_casualties"] == 60
        assert "(9 / 60 casualties)" in format_event_oneliner(logs[0])
        assert "Ney 60" in res["message"] and "Ney 28" not in res["message"]
        assert _contingent(res, "defender", "Ney")["casualties"] == 60

    def test_the_solo_path(self):
        """The solo report derived "60 -> 31" for a destroyed corps."""
        _w, res, logs, _ = _battle(LONE_NEY_SOLO, "Mack", "Ney", seed=1)
        d = _side(res, "defender")
        assert (d["casualties"], d["applied_casualties"], d["remaining"]) == (29, 60, 0)
        cs = _cs(res)
        assert (cs["defender_casualties"], cs["defender_remaining"]) == (60, 0)
        assert "(8 / 60 casualties)" in format_event_oneliner(logs[0])
        assert _contingent(res, "defender", "Ney")["casualties"] == 60
        assert "applied_casualties" not in _side(res, "attacker")

    def test_the_overkill_cap_on_a_lone_corps(self):
        _w, res, logs, _ = _battle(LONE_DEF, "Ney", "Mack", seed=5)
        d = _side(res, "defender")
        assert (d["casualties"], d["applied_casualties"]) == (1499, 1500)
        assert "Mack 1,500" in res["message"] and "Mack 1,499" not in res["message"]
        assert "(198 / 1,500 casualties)" in format_event_oneliner(logs[0])

    def test_the_description_rewrite_is_bounded(self):
        rw = CE._rewrite_lone_casualties
        assert rw("Casualties: Mack 9, Ney 25.", "Ney", 25, 60) == "Casualties: Mack 9, Ney 60."
        assert rw("Ney 250 and Ney 25,000", "Ney", 25, 60) == "Ney 250 and Ney 25,000"
        assert rw("ArchdukeJohn 25", "John", 25, 60) == "ArchdukeJohn 25"
        assert rw("Ney suffered 25 casualties.", "Ney", 25, 60) == "Ney suffered 60 casualties."

    def test_lever_down_is_the_pre_iq5_surface(self, monkeypatch):
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        _w, res, logs, _ = _battle(LONE_NEY_SOLO, "Mack", "Ney", seed=1)
        assert "applied_casualties" not in _side(res, "defender")
        assert (_cs(res)["defender_casualties"], _cs(res)["defender_remaining"]) == (29, 31)
        assert "defender_applied_casualties" not in logs[0]
        assert "(8 / 29 casualties)" in format_event_oneliner(logs[0])

    def test_it_is_display_only(self, monkeypatch):
        for placements in (LONE_NEY_CO, LONE_NEY_SOLO):
            w, res, logs, _ = _battle(placements, "Mack", "Ney", seed=1)
            up = _mechanics(w, res, logs)
            monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
            w, res, logs, _ = _battle(placements, "Mack", "Ney", seed=1)
            assert _mechanics(w, res, logs) == up
            monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", True)

    def test_the_log_prefers_the_applied_figure(self):
        ev = {"type": "battle", "turn": 4, "location": "Franconia",
              "attacker": "Mack", "attacker_nation": "Austria",
              "defender": "Ney", "defender_nation": "France",
              "outcome": "attacker_tactical_victory",
              "attacker_casualties": 9, "defender_casualties": 28,
              "attacker_strength_before": 70000, "defender_strength_before": 60}
        assert "(9 / 28 casualties)" in format_event_oneliner(ev)
        ev["defender_applied_casualties"] = 60
        assert "(9 / 60 casualties)" in format_event_oneliner(ev)

    def test_the_enemy_phase_transport_carries_it(self):
        import backend.main as M
        w, res, _logs, _ = _battle(LONE_NEY_CO, "Mack", "Ney", seed=1)
        phase = {"total_actions": 1,
                 "nations": {"Austria": {"actions": [res], "action_count": 1}}}
        with _quiet():
            visible = M._build_visible_enemy_phase(phase, w)
        (action,) = visible["nations"]["Austria"]["actions"]
        assert action["events"][0]["defender"]["applied_casualties"] == 60

    def test_the_dialog_prefers_it_on_a_lone_side_only(self):
        code = _body("enemy_phase_dialog.gd", "_format_battle")
        for side, name in (("atk", "attacker"), ("def", "defender")):
            assert (f'\tvar {side}_applied = {name}.get("applied_casualties", null)\n'
                    f'\tif not {side}_is_army and ({side}_applied is int or '
                    f'{side}_applied is float):\n'
                    f'\t\t{name}_casualties = {side}_applied') in code
        # read before the lines that print the figure
        assert code.index("def_applied") < code.index("if def_is_army:")


class TestTheColoursBelongToASide:
    """Ruling G (#11). Census pins — the suite must not need the Godot
    binary. The colour keys on the battle's ATTACKER nation, never on text."""

    def test_the_lever_exists_and_is_up(self):
        assert "const IQ5_COLOUR_BY_SIDE := true" in _GD_TEXT("enemy_phase_dialog.gd")

    def test_the_side_decides_the_two_colours(self):
        code = _body("enemy_phase_dialog.gd", "_format_action")
        assert "var reinf_side = _reinforcement_side(action)" in code
        assert ('\t\tvar arrive_color = Utils.COLOR_SUCCESS\n'
                '\t\tvar noshow_color = COLOR_ERROR\n'
                '\t\tif reinf_side == "enemy":\n'
                '\t\t\tarrive_color = COLOR_ERROR\n'
                '\t\t\tnoshow_color = Utils.COLOR_SUCCESS\n'
                '\t\telif reinf_side == "third":\n'
                '\t\t\tarrive_color = Utils.COLOR_INFO\n'
                '\t\t\tnoshow_color = Utils.COLOR_INFO') in code

    def test_the_side_is_the_battles_attacker(self):
        code = _body("enemy_phase_dialog.gd", "_reinforcement_side")
        assert 'if not IQ5_COLOUR_BY_SIDE:\n\t\treturn "player"' in code
        assert 'var an = ev.get("attacker_nation", "")' in code
        assert 'var dn = ev.get("defender_nation", "")' in code
        assert 'var nat = action.get("nation", "")' in code
        assert ('\tif atk_nation == _PLAYER_NATION:\n\t\treturn "player"\n'
                '\tif def_nation == _PLAYER_NATION:\n\t\treturn "enemy"\n'
                '\treturn "third"') in code
        assert "msg_text" not in code and "find(" not in code   # never the prose

    def test_our_army_destroyed_is_a_loss(self):
        code = _body("enemy_phase_dialog.gd", "_format_battle")
        assert ('\t\tvar destroyed_color = Utils.COLOR_CONQUEST\n'
                '\t\tif IQ5_COLOUR_BY_SIDE and str(event.get("defender_nation", "")) '
                '== _PLAYER_NATION:\n'
                '\t\t\tdestroyed_color = COLOR_ERROR\n'
                '\t\tresult += "[color=#" + destroyed_color + "]    ARMY DESTROYED!') in code

    def test_main_gd_is_left_alone(self):
        """main.gd only ever shows a French attack — its colours stay."""
        code = _body("main.gd", "_display_reinforcement_messages")
        assert "_reinforcement_side" not in code and "IQ5_COLOUR_BY_SIDE" not in code


class TestTheEnemyPhasePrintsTheFigure:
    """H #16: the pins checked that keys were READ, never the branch that
    prints them or the figure printed (or→and, `if false:`, a def/atk swap
    all stayed green)."""

    def test_the_casualties_gate_is_or(self):
        code = _body("enemy_phase_dialog.gd", "_format_berthier_report")
        assert '\tif atk_scope != "" or def_scope != "":\n' in code

    def test_each_army_branch_prints_its_own_figure(self):
        code = _body("enemy_phase_dialog.gd", "_format_battle")
        for flag, name in (("atk_is_army", "attacker"), ("def_is_army", "defender")):
            assert (f'\tif {flag}:\n'
                    f'\t\tresult += "[color=#" + Utils.COLOR_INFO + "]    " + '
                    f'{name}_name + "\'s army: "\n'
                    f'\t\tresult += _format_number({name}_casualties) + " casualties — "\n'
                    f'\t\tresult += {name}_name + "\'s own corps: "\n'
                    f'\t\tresult += _format_number({name}_remaining) + " remaining') in code

    def test_the_berthier_line_reads_each_side_from_its_own_key(self):
        code = _body("enemy_phase_dialog.gd", "_format_berthier_report")
        assert '\t\tvar def_cas = casualty.get("defender_casualties", 0)' in code
        assert '\t\tvar atk_cas = casualty.get("attacker_casualties", 0)' in code
        assert ('\t\tresult += ("[color=#" + COLOR_RPT + "]    Casualties: " + atk_label + " "\n'
                '\t\t\t+ _format_number(atk_cas) + " | " + def_label + " "\n'
                '\t\t\t+ _format_number(def_cas) + "[/color]\\n")') in code


class TestTheTerminalFlagsANoShow:
    """H #18: a marker match must SET is_failure (flip it, drop the loop or
    start it true and every no-show renders report grey)."""

    def test_the_marker_match_sets_the_failure(self):
        code = _body("main.gd", "_display_reinforcement_messages")
        assert "\t\tvar is_failure = false\n" in code
        assert ("\t\tif not is_arrival:\n"
                "\t\t\tfor marker in failure_markers:\n"
                "\t\t\t\tif text.findn(marker) >= 0:\n"
                "\t\t\t\t\tis_failure = true\n") in code


def _raw_func(file: str, func: str) -> str:
    """The raw text of `func <func>(` up to the next `\\nfunc ` — never a
    fixed-length scrape (the NA-6 dead-name-pin failure)."""
    src = _GD_TEXT(file)
    start = src.index(f"\nfunc {func}(")
    end = src.find("\nfunc ", start + 1)
    return src[start:end if end != -1 else len(src)]


class TestTheNullGuardIsPinned:
    """H #19: IQ5-11's present-but-null guard had no pin."""

    def test_the_guard_is_the_is_array_form(self):
        body = _raw_func("main.gd", "_display_result")
        assert ('\n\tif response.get("reinforcement_messages") is Array and not '
                'response.reinforcement_messages.is_empty():\n'
                '\t\t_display_reinforcement_messages(response.reinforcement_messages)') in body
        assert 'response.has("reinforcement_messages")' not in body

    def test_the_slice_is_the_function(self):
        body = _raw_func("main.gd", "_display_result")
        assert body.count("\nfunc ") == 1          # only its own header
        assert "typeof(reinf) == TYPE_ARRAY" not in body   # the sibling elsewhere


class TestOneJoinNames:
    """H #21: the executor carried a duplicate `_join_names`; a pin on one
    could not see the other. One source now."""

    def test_the_executor_holds_no_copy(self):
        from backend.commands import combat_executor as cex
        assert not hasattr(cex, "_join_names")
        assert "def _join_names" not in inspect.getsource(cex)

    @pytest.mark.parametrize("names,prose", [
        (["Davout"], "Davout"),
        (["Davout", "Lannes"], "Davout and Lannes"),
        (["Davout", "Lannes", "Soult"], "Davout, Lannes and Soult"),
        (["Archduke John", "Mack", "Davout", "Lannes"], "Archduke John, Mack, Davout and Lannes")])
    def test_the_battle_report_copy_is_identical_for_the_call_site(self, names, prose):
        from backend.game_logic.battle_report import _join_names
        old = "".join(names) if len(names) <= 1 else ", ".join(names[:-1]) + " and " + names[-1]
        assert _join_names(names) == old == prose

    def test_two_co_located_men(self):
        """The hazard's working geometry: Davout AND Lannes stand with Ney."""
        msgs = _rm({"Ney": ("Paris", 20000), "Davout": ("Paris", 30000),
                    "Lannes": ("Paris", 25000), "Moore": ("Artois", 100000)},
                   "Moore", "Ney")
        assert msgs[0].startswith("Ney fought with Davout and Lannes beside him — ")
        assert "committed (Davout, Lannes)" in msgs[0]

    def test_three_co_located_men(self):
        """The "A, B and C" branch — a third man (Soult, Rival to Ney, still
        brings half) joins the stack. Order is the participant order."""
        msgs = _rm({"Ney": ("Paris", 20000), "Davout": ("Paris", 30000),
                    "Lannes": ("Paris", 25000), "Soult": ("Paris", 22000),
                    "Moore": ("Artois", 120000)}, "Moore", "Ney")
        assert msgs == [
            "Ney fought with Davout, Soult and Lannes beside him — massed effective "
            "strength: 20,000 (lead) + 62,974 committed (Davout, Soult, Lannes) = 82,974.",
            "Ney's supporting allies lost 10,238 men.",
        ]


class TestAnEnemyCourtIsNamedInProse:
    """H #21 (RM9): the enemy trust note's court was only ever pinned on
    Austria, whose tag IS its display form. A stub on the one tag != display
    court (the Ottoman marshal is alone, so no end-to-end battle can reach
    it — the same-nation filter would drop a re-flagged man)."""

    def _note(self, nation, name="Abdurrahman"):
        w = _boot()
        ce = CommandExecutor()._combat
        stub = SimpleNamespace(name=name, nation=nation)
        rec = {"marshal": stub, "side": "defender", "trust": 5, "trust_factor": 0.5,
               "committed": 1, "full": 2}
        return ce._compose_trust_note(
            w, SimpleNamespace(nation="France"), SimpleNamespace(nation=nation), [rec])

    def test_the_ottoman_court(self):
        assert self._note("Ottoman") == (
            "Abdurrahman fought for the Ottoman Empire without conviction — he brought "
            "half what he otherwise would.")

    def test_a_plain_court_takes_no_article(self):
        assert self._note("Austria", "Mack").startswith("Mack fought for Austria without")


# C: the geometries probe 2 measured.
CHARLES_REINFORCED = {"Ney": ("Swabia", 40000), "ArchdukeCharles": ("Franconia", 30000),
                      "ArchdukeJohn": ("Bohemia", 25000)}


def _sulking(w, who, at):
    w.marshals[who].jealous_of = at
    w.marshals[who].jealousy_turns_remaining = 3


class TestTheDefenderAndTheNoShowsAreProse:
    def test_a_multi_word_defender_arrival(self):
        """Bohemia borders Franconia: Archduke John marches in to defend."""
        assert _rm(CHARLES_REINFORCED, "Ney", "ArchdukeCharles", seed=1) == [
            "Archduke Charles was reinforced — massed effective strength: 30,000 "
            "(lead) + 24,316 committed (Archduke John) = 54,316.",
            "Archduke Charles's supporting ally lost 2,077 men.",
        ]

    def test_lever_down_defender_arrival_is_720597da(self, monkeypatch):
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", False)
        assert _rm(CHARLES_REINFORCED, "Ney", "ArchdukeCharles", seed=1) == [
            "ArchdukeCharles was reinforced — massed effective strength: 30,000 "
            "(lead) + 24,316 committed (ArchdukeJohn) = 54,316.",
            "ArchdukeCharles's supporting ally lost 2,077 men.",
        ]

    @pytest.mark.parametrize("seed", range(1, 9))
    def test_no_roster_key_on_the_defender_arrival(self, seed):
        for m in _rm(CHARLES_REINFORCED, "Ney", "ArchdukeCharles", seed=seed) or []:
            assert not _CAMEL.search(m), (seed, m)

    def _sulk(self, placements, attacker, target, who, at, lever, monkeypatch, seed=1):
        monkeypatch.setattr(CE, "BOTH_SIDES_NAME_THEIR_SCOPE", lever)
        w = _stage(_boot(), placements)
        _sulking(w, who, at)
        res, _ = _fight(w, attacker, target, seed)
        return res.get("reinforcement_messages")

    def test_the_grievance_arm(self, monkeypatch):
        assert self._sulk(JOHN_ARRIVES_ATK, "Mack", "Ney", "ArchdukeJohn", "Mack",
                          True, monkeypatch) == [
            "Archduke John did not march. His quarrel with Mack kept him where he stood."]
        assert self._sulk(JOHN_ARRIVES_ATK, "Mack", "Ney", "ArchdukeJohn", "Mack",
                          False, monkeypatch) == [
            "ArchdukeJohn did not march. His quarrel with Mack kept him where he stood."]

    def test_the_grievance_arm_names_a_multi_word_lead(self, monkeypatch):
        """`marshal.name` in the arm goes through the display function too.

        Seed-robust: Archduke Charles–Archduke John are an authored +1 pair,
        so the derived −1 leaves the grievance at 0 and John's arrival roll
        still PASSES on most seeds (`grievance_withheld` is the reason only
        when he FAILS it). Seeds 1..12 are searched, at least one no-show
        is required (2, 6 and 10 at the time of writing), and every no-show
        must be the exact grievance line; an arrival is the exact prose
        arrival line, never a roster key."""
        placements = {"ArchdukeCharles": ("Swabia", 40000), "Ney": ("Franconia", 20000),
                      "ArchdukeJohn": ("Bohemia", 30000)}
        no_shows = 0
        for seed in range(1, 13):
            msgs = self._sulk(placements, "ArchdukeCharles", "Ney", "ArchdukeJohn",
                              "ArchdukeCharles", True, monkeypatch, seed=seed)
            assert not any(_CAMEL.search(m) for m in msgs), (seed, msgs)
            if any("arrived" in m for m in msgs):
                assert msgs[0] == ("Archduke John's forces arrived to reinforce "
                                   "Archduke Charles!"), seed
                assert msgs[1].startswith("Massed effective strength: 40,000 (lead) + "), seed
                continue
            no_shows += 1
            assert msgs == ["Archduke John did not march. His quarrel with Archduke "
                            "Charles kept him where he stood."], seed
        assert no_shows >= 1


class TestTheRubbleOnTheAttackerSide:
    """Ruling E, the attacker mirror: a 55-man Davout beside Ney attacking.
    The seed that rubbles him is FOUND, not assumed; at least one must."""

    def test_the_attacker_side_too(self):
        placements = {"Ney": ("Swabia", 30000), "Davout": ("Swabia", 55),
                      "Mack": ("Swabia", 60000)}
        hit = 0
        for seed in range(1, 13):
            _w, res, logs, losses = _battle(placements, "Ney", "Mack", seed=seed)
            if losses["Davout"] != 55:
                continue
            hit += 1
            assert "Ney's supporting ally lost 55 men." in res["reinforcement_messages"]
            rows = {r["marshal"]: r for r in logs[0]["attacker_participant_losses"]}
            assert rows["Davout"]["casualties"] == 55
            assert _contingent(res, "attacker", "Davout")["casualties"] == 55
        assert hit >= 1

    def test_the_log_prefers_the_attackers_applied_figure(self):
        ev = {"type": "battle", "turn": 4, "location": "Swabia",
              "attacker": "Ney", "attacker_nation": "France",
              "defender": "Mack", "defender_nation": "Austria",
              "outcome": "defender_victory",
              "attacker_casualties": 27, "defender_casualties": 9,
              "attacker_strength_before": 60, "defender_strength_before": 70000}
        assert "(27 / 9 casualties)" in format_event_oneliner(ev)
        ev["attacker_applied_casualties"] = 60
        assert "(60 / 9 casualties)" in format_event_oneliner(ev)


class TestTheCaptionSitsUnderTheCorps:
    """Ruling B (#10). Structural only — the suite must not need Godot.

    Measured headless on the real tableau (show_diorama, settled frame,
    visible-pixel sprite bounds; the probe is in the review scratchpad):
    the shipped caption was a FOURTH text row, and in the reinforced case
    (a "marched to the guns" status row present) it landed on the lead's
    locket (38x7 px) and name label (36x5 px) on both columns; set before
    `autowrap_mode`, its size never wrapped (one ~420px line into the
    opposing half, per the review). Under the figures, outboard, 150 wide
    at y=+30: no collision at depth 1 or 2, either column, reinforced or
    co-located (y=+22 still grazed a fallen figure by 1 px)."""

    def test_autowrap_is_set_before_the_size(self):
        code = _body("battle_diorama.gd", "_make_block")
        a = code.index("faith_l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART")
        m = code.index("faith_l.custom_minimum_size = Vector2(FAITH_CAPTION_W, 0.0)")
        s = code.index("faith_l.size = Vector2(FAITH_CAPTION_W, 14.0)")
        assert a < m < s

    def test_it_sits_under_the_feet_outboard(self):
        code = _body("battle_diorama.gd", "_make_block")
        assert ("\t\t\tfaith_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT\n"
                "\t\t\tfaith_l.position = Vector2(FAITH_CAPTION_INBOARD - FAITH_CAPTION_W,\n"
                "\t\t\t\t\tFAITH_CAPTION_Y)") in code
        assert ("\t\t\tfaith_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT\n"
                "\t\t\tfaith_l.position = Vector2(-FAITH_CAPTION_INBOARD, FAITH_CAPTION_Y)") in code
        assert "faith_l.position = Vector2(text_x" not in code

    def test_the_measured_constants(self):
        src = _GD_TEXT("battle_diorama.gd")
        const = {k: float(re.search(rf"const {k} := ([-\d.]+)", src).group(1))
                 for k in ("FAITH_CAPTION_W", "FAITH_CAPTION_Y", "FAITH_CAPTION_INBOARD")}
        assert const["FAITH_CAPTION_Y"] >= 30.0      # below the feet and a fallen figure
        assert const["FAITH_CAPTION_W"] <= 150.0     # clear of the next block inboard
        assert const["FAITH_CAPTION_INBOARD"] <= 20.0


# ═══════════════════════════════════════════════════════════════════════
# IQ-5 REVIEW ROUND — ruling J (#5): the card prices the grievance's INCREMENT
# ═══════════════════════════════════════════════════════════════════════

OLD_CARD = ("Free, and it fixes nothing. For 3 more turns he brings about half the weight "
            "of his {men:,} men to any battle {lead} leads, and the quarrel may harden further.")


def _let_it_stand(who, at, trust=None, rels=None):
    """Fire the §6 confrontation for `who` (jealous of `at`) on the shipped
    boot through the real producer, `queue_confrontation_petition`, and read
    the "Let it stand" option's `detail` off `world.pending_marshal_petition`
    — the surface the player reads, not the helper. Returns (detail, world,
    the engine's own breakdown, its counterfactual)."""
    w = _boot()
    m, t = w.marshals[who], w.marshals[at]
    for (a, b), value in (rels or {}).items():
        w.marshals[a].relationships[b] = value
    if trust is not None:
        _trust(m, trust)
    m.jealous_of = at
    m.jealousy_turns_remaining = 3
    assert w.pending_marshal_petition is None
    with _quiet():
        assert J.queue_confrontation_petition(w, m, t) == J.PETITION_QUEUED
    pet = w.pending_marshal_petition
    assert pet["kind"] == "jealousy_confrontation" and pet["speaker"] == who
    (opt,) = [o for o in pet["options"] if o["id"] == "acknowledge"]
    assert opt["label"] == "Let it stand" and opt["cost_note"] == "Free"
    return (opt["detail"], w, pair_contribution_breakdown(t, m),
            pair_contribution_breakdown(t, m, without_grievance=True))


class TestTheCardPricesTheIncrement:
    """Ruling J (#5, P2, confirmed by two refuters). `_standing_cost_detail`
    read the breakdown and used it only when `scale > 0 and trust_factor <
    1`, so on the ordinary board — Bernadotte (cautious) Rival to Ney, the
    derived −1 driving the pair to −2 and the engine applying 0.0 — the
    "Let it stand" card still priced "about half the weight of his 17,000
    men". The card prices the grievance's INCREMENT now: the engine's scale
    against the same source's counterfactual without the grievance
    (`pair_contribution_breakdown(..., without_grievance=True)`), behind
    `TRUST_NAMES_ITS_PRICE`. Every pin reads the petition the player reads,
    on the authored pairs; relationships are hand-set only to reach an arm
    the boot cannot."""

    NONE_NEY = ("Free, and it fixes nothing. For 3 more turns he brings NONE of his "
                "17,000 men to any battle Ney leads, and the quarrel may harden further.")

    def test_bernadotte_jealous_of_ney_brings_none(self):
        detail, w, bd, cf = _let_it_stand("Bernadotte", "Ney")
        b = w.marshals["Bernadotte"]
        assert (b.personality, b.trust.value, b.strength) == ("cautious", 40, 17000)
        assert b.relationships["Ney"] == -1 == w.marshals["Ney"].relationships["Bernadotte"]
        assert (bd["scale"], bd["relationship"], bd["grievance"], bd["trust_factor"]) == (
            0.0, -2, "withheld", 1.0)
        assert (cf["scale"], cf["relationship"], cf["grievance"]) == (0.5, -1, "")
        assert detail == self.NONE_NEY
        assert "half" not in detail

    def test_at_trust_25_it_is_still_none_never_a_quarter(self):
        """The finding's second cell: the new branch had the true figure in
        hand and still said half. Trust has nothing left to halve."""
        detail, _w, bd, cf = _let_it_stand("Bernadotte", "Ney", trust=25)
        assert (bd["scale"], bd["trust_factor"]) == (0.0, 1.0)
        assert (cf["scale"], cf["trust_factor"]) == (0.25, 0.5)
        assert detail == self.NONE_NEY
        assert "quarter" not in detail and "faith" not in detail

    def test_the_card_agrees_with_the_muster_row(self):
        """The finding's contradiction, closed: the muster row for the same
        pair refuses him outright (a −2 read is `hostile_refuses`), and the
        card no longer prices "about half" for a man who will not come."""
        detail, w, _bd, _cf = _let_it_stand("Bernadotte", "Ney")
        ce = CommandExecutor()._combat
        with _quiet():
            pv = ce._build_muster_preview(w.marshals["Ney"], w.marshals["Mack"], w, {"world": w})
        row = next(r for r in pv["rows"] if r["marshal"] == "Bernadotte")
        assert row["will_join"] is False and row["reason"] == "hostile_refuses"
        assert "he brings NONE of his 17,000 men" in detail

    def test_an_already_hostile_pair_costs_no_weight(self):
        """Hazard 1: Bernadotte–Davout is authored −2 both ways. The engine
        applies 0.0 with the grievance AND without it, so "NONE for 3 more
        turns" would promise a return that never comes."""
        detail, w, bd, cf = _let_it_stand("Bernadotte", "Davout")
        assert w.marshals["Bernadotte"].relationships["Davout"] == -2
        assert w.marshals["Davout"].relationships["Bernadotte"] == -2
        assert bd["scale"] == cf["scale"] == 0.0 and cf["relationship"] == -2
        assert detail == ("Free, and it fixes nothing. For 3 more turns he brings NONE of his "
                          "17,000 men to any battle Davout leads, quarrel or no quarrel — they are "
                          "openly at odds already, and the quarrel may harden further.")

    def test_a_friend_loses_his_goodwill(self):
        """Hazard 2: Soult–Massena is the authored +1 pair. The grievance
        costs the friendship's ×1.25 — a real price "no weight penalty"
        would have hidden; and never `weight_phrase(1.0)` ("about 100% of")."""
        detail, w, bd, cf = _let_it_stand("Soult", "Massena")
        assert w.marshals["Soult"].personality == "literal"
        assert (w.marshals["Soult"].relationships["Massena"],
                w.marshals["Massena"].relationships["Soult"]) == (1, 1)
        assert (bd["scale"], bd["relationship"]) == (1.0, 0)
        assert (cf["scale"], cf["relationship"]) == (1.25, 1)
        assert detail == ("Free, and it fixes nothing. For 3 more turns he brings his 30,000 men to "
                          "any battle Massena leads, but no more — the goodwill that made him worth "
                          "a quarter more is gone, and the quarrel may harden further.")
        assert "half" not in detail and "100%" not in detail

    def test_the_lost_goodwill_is_derived_from_the_table(self, monkeypatch):
        """Never a hardcoded quarter. A devoted (+2) pair — none is authored,
        so hand-set to reach the arm — falls 1.5 -> 1.25 ("about 20%"); and
        a re-tuned +1 of 1.5 reads "half"."""
        detail, _w, bd, cf = _let_it_stand(
            "Soult", "Massena", rels={("Soult", "Massena"): 2, ("Massena", "Soult"): 2})
        assert (bd["scale"], cf["scale"]) == (1.25, 1.5)
        assert detail == ("Free, and it fixes nothing. For 3 more turns he brings about 125% of the "
                          "weight of his 30,000 men to any battle Massena leads, but less than he "
                          "would — the goodwill that made him worth about 20% more is gone, and the "
                          "quarrel may harden further.")
        monkeypatch.setattr(CE, "_RELATIONSHIP_SCALING", {**CE._RELATIONSHIP_SCALING, 1: 1.5})
        detail, _w, bd, cf = _let_it_stand("Soult", "Massena")
        assert (bd["scale"], cf["scale"]) == (1.0, 1.5)
        assert detail == ("Free, and it fixes nothing. For 3 more turns he brings his 30,000 men to "
                          "any battle Massena leads, but no more — the goodwill that made him worth "
                          "half more is gone, and the quarrel may harden further.")

    def test_the_more_phrase_drops_the_trailing_of(self):
        assert J._more_phrase(0.25) == "a quarter"
        assert J._more_phrase(0.5) == "half"
        assert J._more_phrase(0.75) == "three-quarters"
        assert J._more_phrase(0.2) == "about 20%"
        assert J._more_phrase(1.0) == "about 100%"
        assert J._more_phrase(1.5) == "about 150%"

    def test_a_quarrel_that_costs_no_weight_says_so(self):
        """An asymmetric pair the web never authors (the Win/Loss formula moves
        ORDERED pairs, so a campaign can reach it): Ney reads Davout at −1,
        Davout reads Ney at +1. The grievance's −1 lands on Davout's side and
        the pair's worse direction is −1 either way — half with the quarrel,
        half without. Hand-set to prove the arm the boot cannot reach."""
        detail, _w, bd, cf = _let_it_stand(
            "Davout", "Ney", rels={("Ney", "Davout"): -1, ("Davout", "Ney"): 1})
        assert bd["scale"] == cf["scale"] == 0.5
        assert detail == ("Free, and it fixes nothing. For 3 more turns the quarrel costs no weight "
                          "— he already brings half his 26,000 men to any battle Ney leads, and the "
                          "quarrel may harden further.")
        detail, _w, bd, cf = _let_it_stand(
            "Davout", "Ney", rels={("Ney", "Davout"): 0, ("Davout", "Ney"): 1})
        assert bd["scale"] == cf["scale"] == 1.0
        assert detail == ("Free, and it fixes nothing. For 3 more turns the quarrel costs no weight "
                          "— he already brings his full weight to any battle Ney leads, and the "
                          "quarrel may harden further.")
        assert "100%" not in detail

    def test_the_faith_arm_and_the_byte_identity_stand(self):
        """Davout→Ney (0 authored, −1 derived): the R10 arm's own geometry,
        through the petition surface — `TestTheJealousyCard` pins the same
        through the helper, unmodified."""
        detail, w, bd, cf = _let_it_stand("Davout", "Ney")
        assert (bd["scale"], cf["scale"]) == (0.5, 1.0)
        assert detail == OLD_CARD.format(men=w.marshals["Davout"].strength, lead="Ney")
        detail, _w, bd, _cf = _let_it_stand("Davout", "Ney", trust=20)
        assert (bd["scale"], bd["trust_factor"]) == (0.25, 0.5)
        assert detail == ("Free, and it fixes nothing. For 3 more turns he brings a quarter of the "
                          "weight of his 26,000 men to any battle Ney leads, for his faith in you is "
                          "spent (trust 20), and the quarrel may harden further.")

    def test_the_aggressive_arm_is_untouched(self):
        detail, _w, bd, cf = _let_it_stand("Murat", "Ney")
        assert (bd["grievance"], bd["scale"], cf["scale"]) == ("aggressive", 0.0, 0.5)
        assert detail == ("Free, and it fixes nothing. For 3 more turns he brings NONE of his "
                          "22,000 men to any battle Ney leads, and the quarrel may harden further.")

    @pytest.mark.parametrize("who,at", [("Bernadotte", "Ney"), ("Bernadotte", "Davout"),
                                        ("Soult", "Massena"), ("Davout", "Ney")])
    def test_lever_down_is_the_old_card(self, monkeypatch, who, at):
        monkeypatch.setattr(CE, "TRUST_NAMES_ITS_PRICE", False)
        detail, w, _bd, _cf = _let_it_stand(who, at)
        assert detail == OLD_CARD.format(men=w.marshals[who].strength, lead=at)

    def test_the_counterfactual_is_a_pure_read_off_the_one_source(self):
        """`without_grievance=True` is the jealousy block skipped and nothing
        else: the relationship is the lead's own read (a lead's derived −1
        stays), the trust factor applies as usual, nothing is written, and
        the default call is the default call."""
        w = _boot()
        lead, ally = w.marshals["Ney"], w.marshals["Davout"]
        cells = 0
        for rel_la in (-2, -1, 0, 1, 2):
            for rel_al in (-2, -1, 0, 1, 2):
                for trust in (85, 20):
                    for grievance in GRIEVANCES:
                        lead.relationships[ally.name] = rel_la
                        ally.relationships[lead.name] = rel_al
                        _trust(ally, trust)
                        _set_grievance(lead, ally, grievance)
                        before = (lead.jealous_of, ally.jealous_of)
                        bd = pair_contribution_breakdown(lead, ally)
                        cf = pair_contribution_breakdown(lead, ally, without_grievance=True)
                        assert (lead.jealous_of, ally.jealous_of) == before
                        assert pair_contribution_breakdown(lead, ally, without_grievance=False) == bd
                        assert set(cf) == set(bd)
                        assert cf["grievance"] == ""
                        assert cf["relationship"] == lead.get_relationship(ally.name)
                        assert cf["relationship_scale"] == CE._RELATIONSHIP_SCALING.get(
                            cf["relationship"], 1.0)
                        assert cf["scale"] == cf["relationship_scale"] * cf["trust_factor"]
                        assert cf["trust"] == trust
                        if grievance == "none":
                            assert cf == bd
                        elif grievance.startswith("ally_"):
                            saved, ally.jealous_of = ally.jealous_of, None
                            assert cf == pair_contribution_breakdown(lead, ally)
                            ally.jealous_of = saved
                        cells += 1
        assert cells == 25 * 2 * 5

    def test_only_the_card_asks_for_the_counterfactual(self):
        """AST census over backend/: exactly one call passes the keyword, and
        it is `_standing_cost_detail`'s — no mechanical reader does."""
        calls = []
        for path in sorted((ROOT / "backend").rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and any(
                        k.arg == "without_grievance" for k in node.keywords):
                    calls.append(path.name)
        assert calls == ["jealousy.py"]
        assert inspect.getsource(J._standing_cost_detail).count("without_grievance=True)") == 1
