"""
VS-6 — The Defection: coalition-flip as a BRIBE
(docs/VASSAL_DEEPENING_SPEC.md §7), landed July 16, 2026.

A flip is TRANSACTIONAL: a nation at war with the lord must offer the
wavering vassal a concession (gold-funded in v1). No willing/able briber →
the vassal stays. When the bribe lands: (a) transfer to the briber as new
lord (VS-5 machinery, costs 600g + WPS-B power cap), or (b) FREE + at WAR
with the former lord (300g — the deliberate contrast to F8b's graceful
PEACE). Resolves IMMEDIATELY in the AI diplomatic phase (structural
double-fire guard vs courting/cascade/rebellion).
"""

from unittest.mock import patch

import pytest

from backend.models.world_state import WorldState
from backend.game_logic.vassal import (
    AUTONOMY_SATELLITE,
    BRIBE_ELIGIBLE_LOYALTY,
    BRIBE_FREE_COST,
    BRIBE_TRANSFER_COST,
    CONTRIBUTION_DISAFFECTED_BELOW,
    TRANSFER_LOYALTY_RESET,
    TRIBUTE_RATES,
    attempt_vassal_bribe,
)

_CAP_OK = {"allowed": True, "lord_power": 1000, "target_power": 100,
           "pct": 10, "reason": ""}
_CAP_BLOCKED = {"allowed": False, "lord_power": 100, "target_power": 90,
                "pct": 90, "reason": "too powerful"}


def make_world():
    return WorldState()


def add_vassal(world, vassal="Saxony", lord="France", loyalty=30):
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


def set_at_war(world, a, b):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = "WAR"


# ═══════════════════════════════════════════════════════
# 1. The bribe gate
# ═══════════════════════════════════════════════════════

class TestBribeGating:
    def test_threshold_is_the_vs4_disaffected_line(self):
        """'First they stop fighting for you, then they flip' — the bribe
        window opens exactly where VS-4's withholding begins."""
        assert BRIBE_ELIGIBLE_LOYALTY == CONTRIBUTION_DISAFFECTED_BELOW

    def test_no_bribe_without_war_with_lord(self):
        world = make_world()
        add_vassal(world, loyalty=10)
        world.nation_gold["Austria"] = 5000
        # Austria NOT at war with France
        events = attempt_vassal_bribe(world, "Austria")
        assert events == []
        assert "Saxony" in world.vassals

    def test_no_bribe_for_loyal_vassal(self):
        world = make_world()
        add_vassal(world, loyalty=80)
        set_at_war(world, "Austria", "France")
        world.nation_gold["Austria"] = 5000
        events = attempt_vassal_bribe(world, "Austria")
        assert events == []

    def test_no_bribe_without_gold(self):
        world = make_world()
        add_vassal(world, loyalty=10)
        set_at_war(world, "Austria", "France")
        world.nation_gold["Austria"] = BRIBE_FREE_COST - 1
        events = attempt_vassal_bribe(world, "Austria")
        assert events == []
        assert "Saxony" in world.vassals

    def test_spiral_widens_the_window(self):
        """Loyalty 45 is safe at healthy grip but courtable in a spiral."""
        world = make_world()
        add_vassal(world, loyalty=45)
        set_at_war(world, "Austria", "France")
        world.nation_gold["Austria"] = 5000
        # Healthy grip: no approach at 45
        with patch("backend.game_logic.vassal.random.random", return_value=0.0):
            assert attempt_vassal_bribe(world, "Austria") == []
        # Spiral: authority floor + capital lost → grip < 30
        world.authority_tracker.authority = 20
        paris = world.regions.get("Paris")
        if paris is not None:
            paris.controller = "Austria"
        world.invalidate_active_nations_cache()
        with patch("backend.game_logic.vassal.random.random", return_value=0.0), \
             patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_OK):
            events = attempt_vassal_bribe(world, "Austria")
        assert events and events[0]["type"] == "vassal_defected"

    def test_failed_bribe_stays_and_warns(self):
        world = make_world()
        add_vassal(world, loyalty=30)
        set_at_war(world, "Austria", "France")
        world.nation_gold["Austria"] = 5000
        with patch("backend.game_logic.vassal.random.random", return_value=0.99):
            events = attempt_vassal_bribe(world, "Austria")
        assert events and events[0]["type"] == "vassal_bribe_refused"
        assert "Saxony" in world.vassals
        # The approach cost half the purse
        assert world.nation_gold["Austria"] == 5000 - BRIBE_FREE_COST // 2
        # The lord's court heard of it
        titles = [n.get("title", "") for n in world.notifications.get_pending()]
        assert any("Tempts" in t for t in titles)

    def test_per_vassal_latch_blocks_pile_on(self):
        """N members at war cannot pile on one vassal in a single turn."""
        world = make_world()
        add_vassal(world, loyalty=30)
        set_at_war(world, "Austria", "France")
        set_at_war(world, "Prussia", "France")
        world.nation_gold["Austria"] = 5000
        world.nation_gold["Prussia"] = 5000
        with patch("backend.game_logic.vassal.random.random", return_value=0.99):
            first = attempt_vassal_bribe(world, "Austria")
            second = attempt_vassal_bribe(world, "Prussia")
        assert first  # the first approach happened
        assert second == []  # the latch held


# ═══════════════════════════════════════════════════════
# 2. Outcome (a): transfer to the briber
# ═══════════════════════════════════════════════════════

class TestTransferOutcome:
    def test_briber_becomes_new_lord(self):
        world = make_world()
        add_vassal(world, loyalty=20)
        set_at_war(world, "Austria", "France")
        world.nation_gold["Austria"] = 5000
        with patch("backend.game_logic.vassal.random.random", return_value=0.0), \
             patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_OK):
            events = attempt_vassal_bribe(world, "Austria")
        assert events[0]["outcome"] == "transfer"
        row = world.vassals["Saxony"]
        assert row["lord"] == "Austria"
        assert row["loyalty"] == TRANSFER_LOYALTY_RESET  # changed masters,
        # not necessarily happier — VS-4/VS-R apply immediately
        assert world.nation_gold["Austria"] == 5000 - BRIBE_TRANSFER_COST
        assert world.get_diplomatic_state("Austria", "Saxony") == "VASSAL"
        assert world.get_diplomatic_state("France", "Saxony") == "PEACE"


# ═══════════════════════════════════════════════════════
# 3. Outcome (b): free + GUARANTEED WAR with the old lord
# ═══════════════════════════════════════════════════════

class TestFreeHostileOutcome:
    def _bribe_free(self, world, briber="Austria"):
        with patch("backend.game_logic.vassal.random.random", return_value=0.0), \
             patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_BLOCKED):
            return attempt_vassal_bribe(world, briber)

    def test_freed_vassal_is_at_war_with_former_lord(self):
        """The deliberate contrast to F8b's graceful PEACE break."""
        world = make_world()
        add_vassal(world, loyalty=20)
        set_at_war(world, "Austria", "France")
        world.nation_gold["Austria"] = 5000
        events = self._bribe_free(world)
        assert events[0]["outcome"] == "free_hostile"
        assert "Saxony" not in world.vassals
        assert world.is_at_war("Saxony", "France")
        assert world.nation_gold["Austria"] == 5000 - BRIBE_FREE_COST

    def test_armistice_respected(self):
        """A respected armistice stays respected even through a bribe."""
        world = make_world()
        add_vassal(world, loyalty=20)
        set_at_war(world, "Austria", "France")
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "ARMISTICE"
        world.nation_gold["Austria"] = 5000
        events = self._bribe_free(world)
        assert events[0]["outcome"] == "free_armistice"
        assert not world.is_at_war("Saxony", "France")

    def test_granted_provinces_reclaimed_on_hostile_break(self):
        """VS-3 interlock: the gift flips back when the vassal turns hostile."""
        world = make_world()
        add_vassal(world, loyalty=20)
        world.vassals["Saxony"]["granted_regions"] = ["Bohemia"]
        world.regions["Bohemia"].controller = "Saxony"
        world.invalidate_active_nations_cache()
        set_at_war(world, "Austria", "France")
        world.nation_gold["Austria"] = 5000
        events = self._bribe_free(world)
        assert events[0]["outcome"] == "free_hostile"
        assert world.regions["Bohemia"].controller == "France"

    def test_sibling_shock_applies(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", loyalty=20)
        add_vassal(world, vassal="Prussia", loyalty=70)
        set_at_war(world, "Austria", "France")
        world.nation_gold["Austria"] = 5000
        self._bribe_free(world)
        assert world.vassals["Prussia"]["loyalty"] == 60  # -10 shock

    def test_freed_vassal_warms_to_the_briber(self):
        world = make_world()
        add_vassal(world, loyalty=20)
        set_at_war(world, "Austria", "France")
        world.nation_gold["Austria"] = 5000
        self._bribe_free(world)
        key = world._make_diplo_key("Saxony", "Austria")
        assert world.nation_relations.get(key, 0) >= 30


# ═══════════════════════════════════════════════════════
# 4. GR5 + legibility
# ═══════════════════════════════════════════════════════

class TestSymmetryAndLegibility:
    def test_gr5_enemy_lords_satellite_biddable(self):
        """Lord-neutral: any lord's satellite can be bribed (latent until
        an enemy lord holds one; pinned with a synthetic Prussia-lord web).
        The bribing nation here is FRANCE-agnostic — Austria bribes
        Prussia's satellite."""
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Prussia", loyalty=20)
        set_at_war(world, "Austria", "Prussia")
        world.nation_gold["Austria"] = 5000
        with patch("backend.game_logic.vassal.random.random", return_value=0.0), \
             patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_OK):
            events = attempt_vassal_bribe(world, "Austria")
        assert events and events[0]["outcome"] == "transfer"
        assert world.vassals["Saxony"]["lord"] == "Austria"

    def test_defection_fires_critical_notification(self):
        world = make_world()
        add_vassal(world, loyalty=20)
        set_at_war(world, "Austria", "France")
        world.nation_gold["Austria"] = 5000
        with patch("backend.game_logic.vassal.random.random", return_value=0.0), \
             patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_OK):
            attempt_vassal_bribe(world, "Austria")
        titles = [n.get("title", "") for n in world.notifications.get_pending()]
        assert any("DEFECTS" in t for t in titles)

    def test_campaign_log_one_liner(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({
            "type": "vassal_defected",
            "vassal": "Holland",
            "lord": "France",
            "briber": "Britain",
            "outcome": "free_hostile",
        })
        assert "DEFECTION" in line and "Holland" in line and "Britain" in line

    def test_dispatch_template_registered(self):
        from backend.game_logic.dispatch import (
            _DIPLOMATIC_EVENT_PRIORITY,
            _DIPLOMATIC_EVENT_TEMPLATES,
        )
        assert "diplomatic_vassal_defected" in _DIPLOMATIC_EVENT_TEMPLATES
        assert _DIPLOMATIC_EVENT_PRIORITY.get(
            "diplomatic_vassal_defected") == "HIGH"

    def test_cooldown_blocks_repeat_approach(self):
        world = make_world()
        add_vassal(world, loyalty=30)
        set_at_war(world, "Austria", "France")
        world.nation_gold["Austria"] = 5000
        with patch("backend.game_logic.vassal.random.random", return_value=0.99):
            attempt_vassal_bribe(world, "Austria")
            second = attempt_vassal_bribe(world, "Austria")
        assert second == []  # defect|Austria|Saxony cooldown holds

    def test_transfer_from_player_relieves_threat(self):
        """Post-build review C8: losing a satellite to a transfer relieves
        the anti-player threat like every other loss path."""
        world = make_world()
        add_vassal(world, loyalty=20)
        set_at_war(world, "Austria", "France")
        world.nation_gold["Austria"] = 5000
        world.threat_level = 50
        with patch("backend.game_logic.vassal.random.random", return_value=0.0), \
             patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_OK):
            events = attempt_vassal_bribe(world, "Austria")
        assert events[0]["outcome"] == "transfer"
        assert world.threat_level == 40


# ═══════════════════════════════════════════════════════
# 5. Real war-instance integration (post-build review C1 + C2 —
#    both HIGH, reproduced live: a CASCADED-IN satellite of a wartime
#    lord is exactly the scenario the slice was built for, and the
#    diplomatic_states-only fixtures above never build an instance)
# ═══════════════════════════════════════════════════════

class TestBribeWithRealWarInstance:
    def _cascaded_world(self):
        """Austria declares a REAL war on France; loyal Saxony cascade-joins
        France's side (an active defender participant of war_1); loyalty
        then collapses mid-war."""
        from backend.game_logic.diplomacy import declare_war
        world = make_world()
        add_vassal(world, loyalty=60)
        world.nation_gold["Austria"] = 5000
        result = declare_war(world, "Austria", "France")
        assert result.get("success"), result
        assert world.is_at_war("Saxony", "Austria")  # cascaded in
        world.vassals["Saxony"]["loyalty"] = 10
        return world

    def _pair_in_any_active_instance(self, world, a, b):
        key = world._make_diplo_key(a, b)
        for inst in (getattr(world, "war_instances", {}) or {}).values():
            if key in (inst.get("active_diplo_keys") or []):
                return True
        return False

    def test_c1_transfer_settles_the_briber_vassal_war_pair(self):
        """C1: the transfer must exit the Austria|Saxony pair from the war
        instance (PEACE + cleanup) BEFORE re-homing — never force-flip
        WAR→VASSAL leaving the pair stranded active forever."""
        world = self._cascaded_world()
        with patch("backend.game_logic.vassal.random.random", return_value=0.0), \
             patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_OK):
            events = attempt_vassal_bribe(world, "Austria")
        assert events and events[0]["outcome"] == "transfer"
        assert world.vassals["Saxony"]["lord"] == "Austria"
        assert world.get_diplomatic_state("Austria", "Saxony") == "VASSAL"
        assert not self._pair_in_any_active_instance(world, "Austria", "Saxony")

    def test_c2_free_outcome_is_hostile_not_peace_fallback(self):
        """C2: the cascaded-in satellite must exit its old (lord's-side)
        wars first so the guaranteed-WAR outcome actually fires — the
        pre-fix code hit the war-instance side conflict and silently fell
        back to PEACE (still at war with its paid liberator)."""
        world = self._cascaded_world()
        with patch("backend.game_logic.vassal.random.random", return_value=0.0), \
             patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_BLOCKED):
            events = attempt_vassal_bribe(world, "Austria")
        assert events and events[0]["outcome"] == "free_hostile"
        assert "Saxony" not in world.vassals
        assert world.is_at_war("Saxony", "France")       # the guarantee
        assert not world.is_at_war("Saxony", "Austria")  # liberator peace
        assert not self._pair_in_any_active_instance(world, "Austria", "Saxony")
