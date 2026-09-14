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

    def test_a_co_located_attacker_uses_the_existing_lines(self):
        _w, res, _logs, losses = _battle(A_SAME, "Ney", "Mack")
        assert losses["Davout"] == 2195
        assert res["reinforcement_messages"] == [
            "Massed effective strength: 30,000 (lead) + 19,312 committed (Davout) = 49,312.",
            "His supporting ally lost 2,195 men.",
        ]

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
        same rule. No trust number for a foreign court's marshal."""
        _w, res, _logs, _ = _battle(ENEMY_CO, "Ney", "Mack", trusts={"ArchdukeJohn": 5})
        note = res["battle_report"]["trust_note"]
        assert note == ("Archduke John fought for Austria without conviction — half his "
                        "weight never reached the field.")
        assert "trust" not in note and "ArchdukeJohn" not in note
        _w, res, _logs, _ = _battle(ENEMY_CO, "Ney", "Mack", trusts={"ArchdukeJohn": 65})
        assert "trust_note" not in res["battle_report"]

    def test_the_enemys_lost_fraction_is_one_minus_the_factor(self, monkeypatch):
        """At the blessed 0.5 the kept and the lost fractions are both "half",
        so this is the only arm that can tell them apart."""
        monkeypatch.setattr(CE, "BROKEN_TRUST_CONTRIBUTION", 0.25)
        _w, res, _logs, _ = _battle(ENEMY_CO, "Ney", "Mack", trusts={"ArchdukeJohn": 5})
        assert res["battle_report"]["trust_note"] == (
            "Archduke John fought for Austria without conviction — three-quarters of "
            "his weight never reached the field.")

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
        _w, res, _logs, _ = _battle(D_CO, "Moore", "Ney", trusts={"Davout": 10})
        dav = _contingent(res, "defender", "Davout")
        assert dav["faith"] == ("His faith in you is spent (trust 10) — half his weight "
                                "reached the field.")
        assert dav["committed"] == 30000          # the figure is left alone
        assert "faith" not in _contingent(res, "defender", "Ney")

    def test_the_enemys_marshal(self):
        _w, res, _logs, _ = _battle(ENEMY_CO, "Ney", "Mack", trusts={"ArchdukeJohn": 5})
        john = _contingent(res, "defender", "ArchdukeJohn")
        assert john["faith"] == ("He fought without conviction — half his weight never "
                                 "reached the field.")

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
        assert davout["faith"].startswith("His faith in you is spent (trust 10)")


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
        code = _body("enemy_phase_dialog.gd", "_format_action")
        assert "var reinf_color = Utils.COLOR_INFO" in code
        assert 'if msg_text.find("arrived") >= 0:\n\t\t\t\treinf_color = Utils.COLOR_SUCCESS' in code
        assert "if msg_text.findn(marker) >= 0:\n\t\t\t\t\t\treinf_color = COLOR_ERROR" in code
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
    @pytest.mark.parametrize("func", ["_make_block", "_populate_shelf"])
    def test_the_caption_is_read_null_safe(self, func):
        code = _body("battle_diorama.gd", func)
        assert 'var faith_v = c.get("faith", null)' in code
        assert 'var faith := str(faith_v) if faith_v is String else ""' in code
        assert 'if faith != "":' in code
        assert 'str(c.get("faith"' not in code
