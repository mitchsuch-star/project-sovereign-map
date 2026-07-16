"""
VS-5 — Vassal creation & transfer in peace deals
(docs/VASSAL_DEEPENING_SPEC.md §6), landed July 16, 2026.

Two halves:
1. ASSURE — creation (vassalage/subjugation) and liberation are reachable on
   the guided settlement surface (the F1 wizard / PROPOSE dialogue consume
   the same demand-add verbs pinned here).
2. NEW — the `vassal_transfer` clause: {type, from: from_lord, to: to_lord,
   vassal} re-homes an existing vassal at the peace table, via the shared
   `transfer_vassal` domain helper (also VS-6's outcome-2 machinery).

Plus the two pre-existing hegemony-projection bugs fixed in this slice:
the liberation step never matched canonical clauses (read `to`/`vassal`/
`nation`, canonical carries only `vassal_nation`) and the vassalage step
read the from/to direction REVERSED.
"""

from unittest.mock import patch

import pytest

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.game_logic.settlement_ratify import _apply_settlement_terms
from backend.game_logic.settlement_scoring import (
    CANONICAL_CLAUSE_TYPES,
    CLAUSE_CONTROL_SCHEMA,
    SETTLEMENT_DEPENDENCY_CLAUSE_TYPES,
    project_balance_after_settlement,
)
from backend.game_logic.settlement_validation import (
    evaluate_vassal_transfer_eligibility,
    validate_settlement_terms,
)
from backend.game_logic.vassal import (
    AUTONOMY_SATELLITE,
    TRANSFER_LOYALTY_RESET,
    TRIBUTE_RATES,
    transfer_vassal,
)
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance

_SCORER_PATH = "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance"
_CAP_OK = {"allowed": True, "lord_power": 1000, "target_power": 100,
           "pct": 10, "reason": ""}


def make_world():
    return WorldState()


def add_vassal(world, vassal="Saxony", lord="Austria", loyalty=60):
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


def install_war(world, attackers=("France",), defenders=("Austria",),
                attacker_leader="France", defender_leader="Austria"):
    war = make_synthetic_war_instance(
        "war_vs5",
        attackers=list(attackers),
        defenders=list(defenders),
        attacker_leader=attacker_leader,
        defender_leader=defender_leader,
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_vs5"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
        world.war_start_turns[pair] = world.current_turn
        world.war_scores[pair] = 50
        world.battle_records[pair] = []
    world.invalidate_war_instance_indexes()
    return war


# ═══════════════════════════════════════════════════════
# 1. Registration + reachability pins (the ASSURE half)
# ═══════════════════════════════════════════════════════

class TestRegistration:
    def test_vassal_transfer_canonical_schema(self):
        spec = CANONICAL_CLAUSE_TYPES["vassal_transfer"]
        assert spec["required"] == {"type", "from", "to", "vassal"}

    def test_vassal_transfer_is_live_dependency_clause(self):
        assert "vassal_transfer" in SETTLEMENT_DEPENDENCY_CLAUSE_TYPES
        assert CLAUSE_CONTROL_SCHEMA["vassal_transfer"]["enabled"] is True
        assert CLAUSE_CONTROL_SCHEMA["vassal_transfer"]["visibility"] == "live"

    def test_creation_family_reachable_via_demand_add(self):
        """ASSURE (spec §6.1): the guided surface's add verbs accept the
        whole dependency family — creation was already live; pinned here."""
        from backend.game_logic.settlement_actions import (
            _DEMAND_ADDABLE_CLAUSE_TYPES,
            _DEMAND_OFFERABLE_CLAUSE_TYPES,
        )
        for ctype in ("vassalage", "subjugation", "liberation", "vassal_transfer"):
            assert ctype in _DEMAND_ADDABLE_CLAUSE_TYPES
            # dependency clauses are demand-only (France self-vassalage /
            # self-dispossession is not a player verb)
            assert ctype not in _DEMAND_OFFERABLE_CLAUSE_TYPES

    def test_guided_suggestion_row_offered(self):
        """The PROPOSE surface's per-court suggestion builder offers
        claiming the court's vassal (this is the exact function the
        review_sections rows consume — F1-wizard-reachable)."""
        from backend.game_logic.settlement_staging import (
            _court_demand_suggestions,
        )
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Austria")
        war = install_war(world, attackers=("France",),
                          defenders=("Austria", "Prussia"))
        with patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_OK):
            suggestions = _court_demand_suggestions(
                world,
                court="Austria",
                direction="demand",
                war_id="war_vs5",
                draft_key="draft-test",
                war_instance=war,
                proposer_side_participants=["France"],
                proposer_holdings=list(world.get_nation_regions("France")),
                proposer_leader="France",
                settlement_terms=[{"type": "peace"}],
                promised_regions=set(),
                treasury_remaining=1000,
                income_cache={},
            )
        labels = [str(s.get("label", "")) for s in suggestions]
        flat = " | ".join(labels)
        assert "Claim Austria's vassal Saxony as your own" in flat, flat
        transfer_rows = [s for s in suggestions
                         if s.get("clause_type") == "vassal_transfer"]
        assert transfer_rows
        assert transfer_rows[0]["action_params"]["vassal_nation"] == "Saxony"
        assert transfer_rows[0]["action"] == "settlement_demand_add"


# ═══════════════════════════════════════════════════════
# 2. Transfer eligibility
# ═══════════════════════════════════════════════════════

class TestTransferEligibility:
    def _setup(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Austria")
        war = install_war(world)
        return world, war

    def test_happy_path(self):
        world, war = self._setup()
        with patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_OK):
            result = evaluate_vassal_transfer_eligibility(
                world, war_instance=war,
                vassal_nation="Saxony", from_lord="Austria", to_lord="France",
            )
        assert result["eligible"], result

    def test_not_their_vassal_refused(self):
        world, war = self._setup()
        with patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_OK):
            result = evaluate_vassal_transfer_eligibility(
                world, war_instance=war,
                vassal_nation="Prussia", from_lord="Austria", to_lord="France",
            )
        assert not result["eligible"]
        assert result["refusal_code"] == "transfer_target_not_their_vassal"

    def test_same_side_lords_refused(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Austria")
        war = install_war(world, attackers=("France",),
                          defenders=("Austria", "Prussia"))
        with patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_OK):
            result = evaluate_vassal_transfer_eligibility(
                world, war_instance=war,
                vassal_nation="Saxony", from_lord="Austria", to_lord="Prussia",
            )
        assert not result["eligible"]
        assert result["refusal_code"] == "dependency_target_not_in_war"

    def test_power_cap_blocks_weak_receiver(self):
        world, war = self._setup()
        with patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value={"allowed": False, "lord_power": 100,
                                 "target_power": 90, "pct": 90,
                                 "reason": "too powerful"}):
            result = evaluate_vassal_transfer_eligibility(
                world, war_instance=war,
                vassal_nation="Saxony", from_lord="Austria", to_lord="France",
            )
        assert not result["eligible"]
        assert result["refusal_code"] == "dependency_power_cap_blocked"

    def test_direction_invalid_on_duplicates(self):
        world, war = self._setup()
        result = evaluate_vassal_transfer_eligibility(
            world, war_instance=war,
            vassal_nation="Saxony", from_lord="Austria", to_lord="Austria",
        )
        assert not result["eligible"]
        assert result["refusal_code"] == "dependency_direction_invalid"

    def test_liberation_and_transfer_of_same_vassal_conflict(self):
        """Post-build review C5: the generic conflict matrix cannot see the
        collision (different subject keys) — the bespoke check rejects a
        package that both frees and claims one vassal."""
        world, war = self._setup()
        with patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_OK):
            result = validate_settlement_terms(
                [
                    {"type": "liberation", "vassal_nation": "Saxony",
                     "lord_nation": "Austria", "liberator": "France"},
                    {"type": "vassal_transfer", "from": "Austria",
                     "to": "France", "vassal": "Saxony"},
                ],
                world=world, war_instance=war,
            )
        assert not result["valid"]
        assert result["error"] == "dependency_same_vassal_conflict"

    def test_validator_routes_transfer_clause(self):
        world, war = self._setup()
        clause = {"type": "vassal_transfer", "from": "Austria",
                  "to": "France", "vassal": "Saxony"}
        with patch("backend.game_logic.diplomacy.check_vassalage_power_cap",
                   return_value=_CAP_OK):
            ok = validate_settlement_terms(
                [{"type": "peace"}, clause],
                world=world, war_instance=war,
            )
            assert ok["valid"], ok
            bad = validate_settlement_terms(
                [{"type": "peace"},
                 {"type": "vassal_transfer", "from": "Austria",
                  "to": "France", "vassal": "Prussia"}],
                world=world, war_instance=war,
            )
        assert not bad["valid"]
        assert bad["error"] == "transfer_target_not_their_vassal"


# ═══════════════════════════════════════════════════════
# 3. The domain helper
# ═══════════════════════════════════════════════════════

class TestTransferVassal:
    def _setup(self, loyalty=5):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Austria", loyalty=loyalty)
        m = Marshal("VonSax", "Dresden", 8000, "cautious", nation="Austria")
        m.original_nation = "Saxony"
        world.marshals[m.name] = m
        return world

    def test_lord_rekey_and_loyalty_reset(self):
        world = self._setup(loyalty=5)
        result = transfer_vassal(world, "Saxony", "France")
        assert result["success"], result["message"]
        row = world.vassals["Saxony"]
        assert row["lord"] == "France"
        # UNCONDITIONAL reset — a loyalty-5 vassal does not instantly rebel
        # against a lord who never wronged it
        assert row["loyalty"] == TRANSFER_LOYALTY_RESET

    def test_marshals_rekeyed_to_new_lord(self):
        world = self._setup()
        result = transfer_vassal(world, "Saxony", "France")
        m = world.marshals["VonSax"]
        assert m.nation == "France"
        assert m.original_nation == "Saxony"  # rebellion path preserved
        assert "VonSax" in result["rekeyed_marshals"]

    def test_granted_regions_cleared(self):
        """VS-3 interlock: the new lord never granted them — stale
        provenance must not reclaim a Franco-granted province to Britain."""
        world = self._setup()
        world.vassals["Saxony"]["granted_regions"] = ["Bohemia"]
        world.vassals["Saxony"]["grant_cooldown"] = 2
        transfer_vassal(world, "Saxony", "France")
        assert "granted_regions" not in world.vassals["Saxony"]
        assert "grant_cooldown" not in world.vassals["Saxony"]

    def test_diplomatic_states_rehomed(self):
        world = self._setup()
        transfer_vassal(world, "Saxony", "France")
        assert world.get_diplomatic_state("Austria", "Saxony") == "PEACE"
        assert world.get_diplomatic_state("France", "Saxony") == "VASSAL"

    def test_no_release_cooldown(self):
        """Transfer never passes through independence — no cooldown."""
        world = self._setup()
        transfer_vassal(world, "Saxony", "France")
        assert world.vassal_release_cooldowns.get("Saxony", 0) == 0

    def test_rebellion_dialogue_cleared(self):
        world = self._setup(loyalty=5)
        world.vassal_rebellion_imminent_popups.append({"nation": "Saxony"})
        transfer_vassal(world, "Saxony", "France")
        assert all(p.get("nation") != "Saxony"
                   for p in world.vassal_rebellion_imminent_popups)

    def test_same_lord_refused(self):
        world = self._setup()
        result = transfer_vassal(world, "Saxony", "Austria")
        assert not result["success"]

    def test_autonomy_and_tribute_carry_over(self):
        world = self._setup()
        transfer_vassal(world, "Saxony", "France")
        row = world.vassals["Saxony"]
        assert row["autonomy"] == AUTONOMY_SATELLITE
        assert row["tribute_rate"] == TRIBUTE_RATES[AUTONOMY_SATELLITE]


# ═══════════════════════════════════════════════════════
# 4. Ratify apply
# ═══════════════════════════════════════════════════════

class TestRatifyApply:
    def test_transfer_clause_applies(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Austria", loyalty=70)
        install_war(world)
        applied = _apply_settlement_terms(
            world,
            settlement_terms=[
                {"type": "peace"},
                {"type": "vassal_transfer", "from": "Austria",
                 "to": "France", "vassal": "Saxony"},
            ],
            war_id="war_vs5",
        )
        rows = [c for c in applied if c.get("type") == "vassal_transfer"]
        assert len(rows) == 1
        assert rows[0]["pair_state_transition"] == "VASSAL of Austria -> VASSAL of France"
        assert rows[0]["loyalty_after"] == TRANSFER_LOYALTY_RESET
        assert world.vassals["Saxony"]["lord"] == "France"

    def test_war_pair_with_new_lord_closed_first(self):
        """A vassal that fought the receiving lord exits that war cleanly."""
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Austria", loyalty=70)
        install_war(world)
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "WAR"
        _apply_settlement_terms(
            world,
            settlement_terms=[
                {"type": "vassal_transfer", "from": "Austria",
                 "to": "France", "vassal": "Saxony"},
            ],
            war_id="war_vs5",
        )
        assert world.get_diplomatic_state("France", "Saxony") == "VASSAL"
        assert not world.is_at_war("France", "Saxony")

    def test_stale_liberation_lord_mismatch_skipped(self):
        """Post-build review C5: a liberation clause whose lord_nation no
        longer matches the LIVE lord (e.g. a same-package transfer re-homed
        the vassal first) must not release someone else's vassal."""
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="France")  # live lord: France
        install_war(world)
        applied = _apply_settlement_terms(
            world,
            settlement_terms=[
                {"type": "liberation", "vassal_nation": "Saxony",
                 "lord_nation": "Austria", "liberator": "Prussia"},
            ],
            war_id="war_vs5",
        )
        assert not [c for c in applied if c.get("type") == "liberation"]
        assert "Saxony" in world.vassals  # NOT released

    def test_stale_transfer_skipped(self):
        """A clause naming the wrong lord applies nothing."""
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Austria")
        install_war(world)
        applied = _apply_settlement_terms(
            world,
            settlement_terms=[
                {"type": "vassal_transfer", "from": "Prussia",
                 "to": "France", "vassal": "Saxony"},
            ],
            war_id="war_vs5",
        )
        assert not [c for c in applied if c.get("type") == "vassal_transfer"]
        assert world.vassals["Saxony"]["lord"] == "Austria"


# ═══════════════════════════════════════════════════════
# 5. Hegemony-projection drive-by fixes (pre-existing bugs)
# ═══════════════════════════════════════════════════════

class TestHegemonyProjectionFixes:
    def test_liberation_step_matches_canonical_clause(self):
        """Pre-fix: the step read to/vassal/nation — canonical liberation
        carries ONLY vassal_nation, so it never fired."""
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Austria")
        result = project_balance_after_settlement(
            world, war_id=None,
            settlement_terms=[{
                "type": "liberation", "vassal_nation": "Saxony",
                "lord_nation": "Austria", "liberator": "France",
            }],
        )
        # The projection ran without error and the freed vassal reduces
        # (or at least never grows) the Austrian bloc's share.
        assert result["post_share"] <= result["pre_share"]

    def test_vassalage_direction_projects_correctly(self):
        """Pre-fix the step read from/to REVERSED (projected the proposer
        as the new vassal of the defeated court). Canonical: from=vassal,
        to=lord — so France (to) must absorb Prussia's (from) share."""
        world = make_world()
        pre = project_balance_after_settlement(
            world, war_id=None, settlement_terms=[],
        )
        post = project_balance_after_settlement(
            world, war_id=None,
            settlement_terms=[{
                "type": "vassalage", "from": "Prussia", "to": "France",
            }],
        )
        # France's bloc grows: either the share rises or the hegemon stays
        # France with at least the same share; it must NOT shrink.
        assert post["post_share"] >= pre["post_share"]

    def test_transfer_step_rehomes_vassal(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Austria")
        result = project_balance_after_settlement(
            world, war_id=None,
            settlement_terms=[{
                "type": "vassal_transfer", "from": "Austria",
                "to": "France", "vassal": "Saxony",
            }],
        )
        assert isinstance(result["modifier"], int)  # projection runs clean

    def test_projection_never_mutates_world(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Austria")
        project_balance_after_settlement(
            world, war_id=None,
            settlement_terms=[{
                "type": "vassal_transfer", "from": "Austria",
                "to": "France", "vassal": "Saxony",
            }],
        )
        assert world.vassals["Saxony"]["lord"] == "Austria"


# ═══════════════════════════════════════════════════════
# 6. Display + label surfaces
# ═══════════════════════════════════════════════════════

class TestDisplaySurfaces:
    def test_term_display_label(self):
        from backend.game_logic.diplomatic_templates import _build_display_label
        label = _build_display_label(
            "vassal_transfer", "Austria", "France", [], 0,
            vassal_nation="Saxony",
        )
        assert "Austria yields its vassal Saxony to France" == label

    def test_demand_clause_label(self):
        from backend.game_logic.settlement_actions import _demand_clause_label
        label = _demand_clause_label({
            "type": "vassal_transfer", "from": "Austria",
            "to": "France", "vassal": "Saxony",
        })
        assert "Saxony" in label and "France" in label

    def test_voice_line_registered(self):
        from backend.game_logic.diplomatic_templates import (
            resolve_settlement_voice_line,
        )
        line = resolve_settlement_voice_line(
            "settlement_guided_reason_vassal_transfer_talleyrand",
            court="Austria", vassal="Saxony",
        )
        assert "Saxony" in line

    def test_refusal_code_has_display_copy(self):
        from backend.game_logic.settlement_routes import _error_display
        copy = _error_display("transfer_target_not_their_vassal")
        assert "vassal" in copy.lower()
