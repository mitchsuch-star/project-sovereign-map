"""PT-D1 + PT-D4 — enemy-phase / muster presentation (Aug 1, 2026 re-measure).

PT-D4 — move-chain presentation. One corps legally chains 3-4 moves per
enemy phase (symmetric AP), but the transcript rendered each hop as its own
"moves to X" bullet: Moore retook four provinces in ONE phase, John marched
Languedoc→Provence→Piedmont→Milan in one — "the single loudest contributor
to the addendum's 'enemy phase as theater: 5.5'". Chains of 3+ hops now
collapse into ONE forced-march entry at the view layer
(main._collapse_enemy_move_chains — after the fog filter, presentation
only, the moves themselves untouched).

PT-D1 — muster one-voice odds. The muster header prices its verdict on the
COMMITTED joint force (CO-2) while the personality line in the same message
prices its -10% on the marshal's SOLO ratio. Both frames are now labelled:
the header names the committed figure, the cautious line says "alone" when
reinforcers committed.
"""

from __future__ import annotations

import random
from pathlib import Path
from types import SimpleNamespace

import pytest

import backend.main as main_module
from backend.commands.combat_executor import CombatExecutor
from backend.game_logic.combat import CombatResolver
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _move_entry(marshal, src, dst, losses=0, nation="Austria", extra_events=None):
    events = [{"type": "move", "marshal": marshal, "from": src, "to": dst}]
    if losses:
        events[0]["march_losses"] = int(losses)
    events.extend(extra_events or [])
    return {
        "success": True,
        "message": f"{marshal} moves from {src} to {dst}",
        "events": events,
        "ai_action": {"marshal": marshal, "action": "move", "target": dst},
        "nation": nation,
    }


def _attack_entry(marshal, target, nation="Austria"):
    return {
        "success": True,
        "message": f"{marshal} attacks {target}",
        "events": [],
        "ai_action": {"marshal": marshal, "action": "attack", "target": target},
        "nation": nation,
    }


def _phase(actions, nation="Austria"):
    return {
        "nations": {nation: {"actions": list(actions),
                             "action_count": len(actions)}},
        "total_actions": len(actions),
        "summary": [],
    }


def _collapse(phase, world):
    return main_module._collapse_enemy_move_chains(phase, world)


# ═══════════════════════════════════════════════════════════════════════
# PT-D4: chains of 3+ collapse to one forced-march entry
# ═══════════════════════════════════════════════════════════════════════

class TestMoveChainCollapse:
    def test_three_hop_chain_is_one_line(self, world):
        phase = _phase([
            _move_entry("John", "Languedoc", "Provence", losses=400),
            _move_entry("John", "Provence", "Piedmont", losses=500),
            _move_entry("John", "Piedmont", "Milan", losses=340),
        ])
        out = _collapse(phase, world)
        actions = out["nations"]["Austria"]["actions"]
        assert len(actions) == 1, "a 3-hop chain must render as ONE entry"
        entry = actions[0]
        assert entry["ai_action"]["action"] == "forced_march"
        assert entry["ai_action"]["marshal"] == "John"
        fm = entry["forced_march"]
        assert fm["stages"] == ["Provence", "Piedmont", "Milan"]
        assert fm["to"] == "Milan"
        assert fm["march_losses"] == 1240, "attrition must be summed"
        assert out["total_actions"] == 1
        assert out["nations"]["Austria"]["action_count"] == 1

    def test_two_hop_chain_is_untouched(self, world):
        phase = _phase([
            _move_entry("John", "Languedoc", "Provence"),
            _move_entry("John", "Provence", "Piedmont"),
        ])
        out = _collapse(phase, world)
        actions = out["nations"]["Austria"]["actions"]
        assert len(actions) == 2
        assert all(a["ai_action"]["action"] == "move" for a in actions)

    def test_own_non_move_action_breaks_the_chain(self, world):
        """move,move,attack,move,move — two 2-segments, nothing collapses."""
        phase = _phase([
            _move_entry("John", "A1", "A2"),
            _move_entry("John", "A2", "A3"),
            _attack_entry("John", "Ney"),
            _move_entry("John", "A3", "A4"),
            _move_entry("John", "A4", "A5"),
        ])
        out = _collapse(phase, world)
        actions = out["nations"]["Austria"]["actions"]
        assert len(actions) == 5, (
            "an interposed attack is a barrier — no segment reached 3 hops")

    def test_interleaved_other_marshal_does_not_break_the_chain(self, world):
        """Round-robin interleaving: John's hops collapse; Mack's entries
        survive in place and in order."""
        phase = _phase([
            _move_entry("John", "A1", "A2"),
            _move_entry("Mack", "B1", "B2"),
            _move_entry("John", "A2", "A3"),
            _attack_entry("Mack", "Ney"),
            _move_entry("John", "A3", "A4"),
        ])
        out = _collapse(phase, world)
        actions = out["nations"]["Austria"]["actions"]
        assert len(actions) == 3
        kinds = [(a["ai_action"]["marshal"], a["ai_action"]["action"])
                 for a in actions]
        assert kinds == [("Mack", "move"), ("Mack", "attack"),
                         ("John", "forced_march")], (
            "the merged entry sits at the LAST hop's position; other "
            "marshals' entries keep theirs")

    def test_discontinuous_hops_do_not_stitch(self, world):
        """A from/to discontinuity starts a new segment — never invent a
        route the events do not record."""
        phase = _phase([
            _move_entry("John", "A1", "A2"),
            _move_entry("John", "A2", "A3"),
            _move_entry("John", "B7", "B8"),  # discontinuity
        ])
        out = _collapse(phase, world)
        actions = out["nations"]["Austria"]["actions"]
        assert len(actions) == 3
        assert all(a["ai_action"]["action"] == "move" for a in actions)

    def test_capture_hops_keep_their_conquest_events(self, world):
        """Moore's four-province recapture: the chain collapses but every
        conquest event survives on the merged entry, so each fall still
        renders under the one march line."""
        conquest = {"type": "conquest", "region": "Wessex",
                    "capture_choice": "secure"}
        phase = _phase([
            _move_entry("Moore", "L1", "Wessex", nation="Britain",
                        extra_events=[conquest]),
            _move_entry("Moore", "Wessex", "Mercia", nation="Britain"),
            _move_entry("Moore", "Mercia", "Anglia", nation="Britain"),
        ], nation="Britain")
        out = _collapse(phase, world)
        actions = out["nations"]["Britain"]["actions"]
        assert len(actions) == 1
        merged_events = actions[0]["events"]
        assert any(e.get("type") == "conquest" for e in merged_events)
        assert sum(1 for e in merged_events if e.get("type") == "move") == 3

    def test_origin_named_only_at_full_intel(self, world):
        """The per-hop bullets never disclosed the ORIGIN — the merged line
        may name it only where the player's own intel is FULL."""
        # A French marshal's location is FULL by the boot fog contract.
        soult = world.marshals["Soult"]
        full_region = soult.location
        phase = _phase([
            _move_entry("Mack", full_region, "X2"),
            _move_entry("Mack", "X2", "X3"),
            _move_entry("Mack", "X3", "X4"),
        ])
        out = _collapse(phase, world)
        fm = out["nations"]["Austria"]["actions"][0]["forced_march"]
        assert fm.get("from") == full_region

        phase2 = _phase([
            _move_entry("Mack", "Galicia", "X2"),
            _move_entry("Mack", "X2", "X3"),
            _move_entry("Mack", "X3", "X4"),
        ])
        out2 = _collapse(phase2, world)
        fm2 = out2["nations"]["Austria"]["actions"][0]["forced_march"]
        assert "from" not in fm2, (
            "an unscouted origin must stay unnamed — the old bullets never "
            "disclosed it and the collapse may not start now")

    def test_summary_and_totals_stay_consistent(self, world):
        phase = _phase([
            _move_entry("John", "A1", "A2"),
            _move_entry("John", "A2", "A3"),
            _move_entry("John", "A3", "A4"),
            _attack_entry("Mack", "Ney"),
        ])
        out = _collapse(phase, world)
        n = sum(len(d.get("actions", []))
                for d in out.get("nations", {}).values())
        assert out["total_actions"] == n == 2
        assert len(out["summary"]) == 2


# ═══════════════════════════════════════════════════════════════════════
# PT-D1: one odds vocabulary per message
# ═══════════════════════════════════════════════════════════════════════

class TestMusterOneVoiceOdds:
    def _mk(self, name, strength, personality, nation):
        return Marshal(name, "TestField", int(strength), personality, nation)

    def test_cautious_solo_frame_names_its_frame_without_claiming_solitude(self):
        """PT-D1. The CONDITION was always right; the WORD was backwards.

        Pin flipped consciously August 12, 2026. The qualifier fires
        exactly when reinforcers ARE committed — that is the only case
        with a joint frame to distinguish from — but it used to read
        "at unfavorable odds alone" on the same screen that printed
        "Massed effective strength: 18,874 (lead) + 12,806 committed".
        "alone" was meant adverbially and read as "by himself".
        """
        random.seed(5)
        a = self._mk("Moore", 20000, "cautious", "Britain")
        d = self._mk("Ney", 30000, "aggressive", "France")
        r = CombatResolver().resolve_battle(
            a, d, terrain="plains", committed_attacker=15000.0)
        line = r.get("attacker_personality_triggered") or ""
        assert "at unfavorable odds on his own numbers" in line, (
            "with reinforcers committed, the solo -10% line must name its "
            "frame — beside a joint-frame muster header it read as a "
            "contradiction")
        assert "alone" not in line, (
            "the man is NOT alone — that is the whole condition under "
            "which this qualifier prints")

    def test_solo_battle_copy_is_byte_stable(self):
        random.seed(5)
        a = self._mk("Moore", 20000, "cautious", "Britain")
        d = self._mk("Ney", 30000, "aggressive", "France")
        r = CombatResolver().resolve_battle(a, d, terrain="plains")
        line = r.get("attacker_personality_triggered") or ""
        assert "at unfavorable odds." in line
        assert "alone" not in line, (
            "a genuinely solo battle has one frame — no qualifier")

    def _muster_lines(self, committed):
        ce = CombatExecutor(SimpleNamespace(combat_resolver=CombatResolver()))
        preview = {
            "attacker": {"name": "Ney", "strength": 24000,
                         "committed_strength": committed},
            "target": {"name": "Mack", "location": "Ulm",
                       "strength_display": "30,000 men"},
            "odds_band": "favorable",
            "rows": [],
            "shared_casualty_note": "",
        }
        return ce._format_muster_lines(preview)

    def test_header_names_the_committed_figure(self):
        text = self._muster_lines(committed=41000)
        assert "24,000" in text
        # CA9-F1 (pin consciously re-blessed): the qualifier changed from
        # "with the muster committed" to "if all march". The figure is what
        # the muster LADDER predicts, not what has happened — the played
        # campaign fought Franconia at 18,101 under a preview of 54,408, and
        # the unqualified past-tense phrasing read as a promise. What is
        # pinned is unchanged: the header names the figure its verdict uses.
        assert "41,000 if all march" in text, (
            "the odds band is priced on the committed force — the header "
            "must name the figure its verdict uses")

    def test_header_stays_legacy_for_a_solo_muster(self):
        text = self._muster_lines(committed=24000)
        assert "if all march" not in text
        assert "MUSTER — Ney (24,000) vs" in text
