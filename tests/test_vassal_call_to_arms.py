"""
VS-4 — Loyalty-gated call-to-arms (docs/VASSAL_DEEPENING_SPEC.md §5),
landed July 16, 2026.

Loyalty has military teeth, through the single-source
vassal_military_contribution tiers:
  loyal (>=60)       — full contribution, byte-identical to pre-VS-4;
  wavering (35-59)   — the nation still answers the call, but its assimilated
                       ex-marshals are withheld from auto-reinforce/muster
                       unless under an explicit SUPPORT order (A-D4 pattern);
  disaffected (<35)  — refuses NEW war-cascade auto-joins outright.

Pinned boundaries: refusal gates only NEW calls (no retroactive mid-war
exit); direct player orders stay obeyed (SUPPORT brings him); GR5-symmetric.
"""

from types import SimpleNamespace

import pytest

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import _process_war_cascade
from backend.game_logic.vassal import (
    AUTONOMY_SATELLITE,
    CONTRIBUTION_DISAFFECTED_BELOW,
    CONTRIBUTION_LOYAL_MIN,
    TRIBUTE_RATES,
    vassal_military_contribution,
)


def make_world():
    return WorldState()


def add_vassal(world, vassal="Saxony", lord="France", loyalty=60):
    world.vassals[vassal] = {
        "lord": lord,
        "loyalty": int(loyalty),
        "autonomy": AUTONOMY_SATELLITE,
        "path": "treaty",
        "created_turn": 1,
        "tribute_rate": TRIBUTE_RATES[AUTONOMY_SATELLITE],
        "carved_from": None,
        "regions": None,
    }
    key = world._make_diplo_key(lord, vassal)
    world.diplomatic_states[key] = "VASSAL"
    world.nation_relations[key] = 0
    world.invalidate_active_nations_cache()


# ═══════════════════════════════════════════════════════
# 1. The tier helper
# ═══════════════════════════════════════════════════════

class TestContributionTiers:
    def test_tier_matrix(self):
        world = make_world()
        add_vassal(world, loyalty=CONTRIBUTION_LOYAL_MIN)
        assert vassal_military_contribution(world, "Saxony") == "loyal"
        world.vassals["Saxony"]["loyalty"] = CONTRIBUTION_LOYAL_MIN - 1
        assert vassal_military_contribution(world, "Saxony") == "wavering"
        world.vassals["Saxony"]["loyalty"] = CONTRIBUTION_DISAFFECTED_BELOW
        assert vassal_military_contribution(world, "Saxony") == "wavering"
        world.vassals["Saxony"]["loyalty"] = CONTRIBUTION_DISAFFECTED_BELOW - 1
        assert vassal_military_contribution(world, "Saxony") == "disaffected"

    def test_non_vassal_is_loyal(self):
        world = make_world()
        assert vassal_military_contribution(world, "Prussia") == "loyal"


# ═══════════════════════════════════════════════════════
# 2. War-cascade refusal (both arms)
# ═══════════════════════════════════════════════════════

class TestCascadeRefusal:
    def test_disaffected_refuses_offensive_call(self):
        """Lord attacks; a disaffected satellite does NOT follow."""
        world = make_world()
        add_vassal(world, loyalty=30)
        cascade = _process_war_cascade(world, "France", "Prussia")
        types = [c.get("cascade_type") for c in cascade]
        assert "vassal_refuses_call" in types
        assert not world.is_at_war("Saxony", "Prussia")
        entry = next(c for c in cascade
                     if c.get("cascade_type") == "vassal_refuses_call")
        assert entry["vassal"] == "Saxony"
        assert entry["loyalty"] == 30
        assert "message" in entry

    def test_disaffected_refuses_defensive_call(self):
        """Lord is attacked; the disaffected satellite still refuses."""
        world = make_world()
        add_vassal(world, loyalty=30)
        cascade = _process_war_cascade(world, "Prussia", "France")
        types = [c.get("cascade_type") for c in cascade]
        assert "vassal_refuses_call" in types
        assert not world.is_at_war("Saxony", "Prussia")

    def test_loyal_vassal_still_auto_joins(self):
        world = make_world()
        add_vassal(world, loyalty=80)
        cascade = _process_war_cascade(world, "France", "Prussia")
        types = [c.get("cascade_type") for c in cascade]
        assert "vassal_offensive_auto_join" in types
        assert world.is_at_war("Saxony", "Prussia")

    def test_wavering_vassal_still_auto_joins(self):
        """Wavering (35-59) gates only the MARSHAL-level contribution —
        the nation still answers the call."""
        world = make_world()
        add_vassal(world, loyalty=45)
        cascade = _process_war_cascade(world, "France", "Prussia")
        types = [c.get("cascade_type") for c in cascade]
        assert "vassal_offensive_auto_join" in types
        assert world.is_at_war("Saxony", "Prussia")

    def test_no_retroactive_mid_war_exit(self):
        """A vassal ALREADY in the war stays in it when loyalty collapses —
        refusal gates only NEW calls (pinned boundary)."""
        world = make_world()
        add_vassal(world, loyalty=80)
        _process_war_cascade(world, "France", "Prussia")
        assert world.is_at_war("Saxony", "Prussia")
        world.vassals["Saxony"]["loyalty"] = 10
        cascade = _process_war_cascade(world, "France", "Prussia")
        types = [c.get("cascade_type") for c in cascade]
        assert "vassal_refuses_call" not in types
        assert world.is_at_war("Saxony", "Prussia")

    def test_gr5_enemy_lords_satellite_refuses_too(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Prussia", loyalty=30)
        cascade = _process_war_cascade(world, "France", "Prussia")
        types = [c.get("cascade_type") for c in cascade]
        assert "vassal_refuses_call" in types
        assert not world.is_at_war("Saxony", "France")

    def test_refusal_recorded_in_war_entry_ledger(self):
        world = make_world()
        add_vassal(world, loyalty=30)
        entries = []
        _process_war_cascade(world, "France", "Prussia",
                             war_entry_entries=entries)
        refused = [e for e in entries if e.get("path") == "refused_disaffected"]
        assert len(refused) == 1
        assert refused[0]["nation"] == "Saxony"


# ═══════════════════════════════════════════════════════
# 3. Marshal-level gates (reinforcement + muster pairing)
# ═══════════════════════════════════════════════════════

class TestMarshalGates:
    def _battlefield(self, world, loyalty):
        """Primary French marshal in the Saxony region; an assimilated
        ex-Saxon corps stands adjacent in Dresden."""
        add_vassal(world, loyalty=loyalty)
        region = world.regions["Saxony"]
        assert "Dresden" in region.adjacent_regions
        primary = Marshal("Primary", "Saxony", 20000, "aggressive", nation="France")
        candidate = Marshal("ExSaxon", "Dresden", 10000, "cautious", nation="France")
        candidate.original_nation = "Saxony"
        world.marshals[primary.name] = primary
        world.marshals[candidate.name] = candidate
        return primary, candidate

    def _executor(self):
        from backend.commands.executor import CommandExecutor
        return CommandExecutor()

    def test_wavering_contingent_withheld_from_auto_reinforce(self):
        world = make_world()
        primary, candidate = self._battlefield(world, loyalty=45)
        combat = self._executor()._combat
        assert combat._is_reinforcement_eligible(
            candidate, primary, "Saxony", "France", world) is False

    def test_loyal_contingent_reinforces(self):
        world = make_world()
        primary, candidate = self._battlefield(world, loyalty=80)
        combat = self._executor()._combat
        assert combat._is_reinforcement_eligible(
            candidate, primary, "Saxony", "France", world) is True

    def test_support_order_overrides_withholding(self):
        """Direct orders stay obeyed — an explicit SUPPORT for the primary
        brings the wavering contingent (the A-D4 pattern)."""
        world = make_world()
        primary, candidate = self._battlefield(world, loyalty=45)
        candidate.strategic_order = SimpleNamespace(
            command_type="SUPPORT", target=primary.name)
        combat = self._executor()._combat
        assert combat._is_reinforcement_eligible(
            candidate, primary, "Saxony", "France", world) is True

    def test_pursue_into_battle_region_also_overrides(self):
        """Post-build review C4: a PURSUE whose quarry stands in the battle
        region is also 'the written word' (byte-mirrors the Grouchy-rule
        predicate the muster preview uses — shown must equal applied)."""
        world = make_world()
        primary, candidate = self._battlefield(world, loyalty=45)
        quarry = Marshal("Quarry", "Saxony", 5000, "cautious", nation="Prussia")
        world.marshals[quarry.name] = quarry
        candidate.strategic_order = SimpleNamespace(
            command_type="PURSUE", target="Quarry")
        combat = self._executor()._combat
        assert combat._is_reinforcement_eligible(
            candidate, primary, "Saxony", "France", world) is True

    def test_gate_released_when_vassalage_ends(self):
        """original_nation of a FORMER vassal (row gone) does not gate."""
        world = make_world()
        primary, candidate = self._battlefield(world, loyalty=45)
        del world.vassals["Saxony"]
        world.invalidate_active_nations_cache()
        combat = self._executor()._combat
        assert combat._is_reinforcement_eligible(
            candidate, primary, "Saxony", "France", world) is True

    def test_muster_preview_pairs_with_the_gate(self):
        """W6-4 shown = applied: the muster names the withholding."""
        world = make_world()
        primary, candidate = self._battlefield(world, loyalty=45)
        combat = self._executor()._combat
        will_join, reason = combat._muster_reason(
            candidate, primary, "Saxony", "France", world)
        assert will_join is False
        assert reason == "vassal_wavering"

    def test_muster_support_order_answers(self):
        world = make_world()
        primary, candidate = self._battlefield(world, loyalty=45)
        candidate.strategic_order = SimpleNamespace(
            command_type="SUPPORT", target=primary.name)
        combat = self._executor()._combat
        will_join, reason = combat._muster_reason(
            candidate, primary, "Saxony", "France", world)
        assert will_join is True
        assert reason == "has_support_order"

    def test_muster_reason_has_display_copy(self):
        from backend.display_names import MUSTER_REASON_DISPLAY
        assert "vassal_wavering" in MUSTER_REASON_DISPLAY


# ═══════════════════════════════════════════════════════
# 4. Legibility surfaces
# ═══════════════════════════════════════════════════════

class TestLegibility:
    def test_campaign_log_one_liner(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({
            "type": "vassal_refuses_call",
            "vassal": "Holland",
            "lord": "France",
            "against": "Austria",
            "loyalty": 28,
        })
        assert "Holland" in line
        assert "refuses" in line
        assert "28" in line

    def test_auto_join_one_liner_drive_by_lord_key(self):
        """Drive-by fixed with VS-4: the emitter passes `lord`, and the
        one-liner used to read only `overlord` (always 'Unknown')."""
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({
            "type": "vassal_auto_join_war",
            "vassal": "Holland",
            "lord": "France",
            "against": "Austria",
        })
        assert "France" in line

    def test_dispatch_template_registered(self):
        from backend.game_logic.dispatch import (
            _DIPLOMATIC_EVENT_PRIORITY,
            _DIPLOMATIC_EVENT_TEMPLATES,
        )
        assert "diplomatic_vassal_refuses_call" in _DIPLOMATIC_EVENT_TEMPLATES
        assert _DIPLOMATIC_EVENT_PRIORITY.get(
            "diplomatic_vassal_refuses_call") == "HIGH"

    def test_refusal_fires_player_notification(self):
        world = make_world()
        add_vassal(world, loyalty=30)
        _process_war_cascade(world, "France", "Prussia")
        titles = [n.get("title", "") for n in world.notifications.get_pending()]
        assert any("Refuses the Call" in t for t in titles)

    def test_refusal_dispatch_event_visible_under_player_vassal_rule(self):
        """Post-build review C3: the player_vassal fog rule checks
        vassals.get(template_vars["nation"]) — the event must carry the
        VASSAL there (carrying the lord made the player-lord arm
        unconditionally invisible in the Morning Dispatch)."""
        world = make_world()
        add_vassal(world, loyalty=30)
        _process_war_cascade(world, "France", "Prussia")
        events = [e for e in world.pending_dispatch_events
                  if e.get("type") == "diplomatic_vassal_refuses_call"]
        assert events
        assert events[0]["template_vars"]["nation"] == "Saxony"
        from backend.game_logic.dispatch import _is_dispatch_event_visible
        assert _is_dispatch_event_visible(events[0], world, "France") is True
