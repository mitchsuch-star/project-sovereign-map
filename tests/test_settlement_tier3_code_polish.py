"""May 24, 2026 audit punch list Tier 3 - code polish behavior tests.

Behavior coverage for the Tier 3 P1+P2 code fixes and P3 polish landed
in the May 24, 2026 audit punch list Tier 3 sweep:

Backend (Python):

- (1) P1 Rule 2 fix: `balance_post_share` float field replaced by
  `balance_post_share_pct` integer-percent field in
  `compute_forced_alliance_continental_toggle_differential(...)`. The
  legacy float field is gone and Godot can read the new field raw
  without crashing.
- (2) P2 Rule 8 fix: `_concession_baseline_select_transferable_region`
  iterates via `world.get_nation_regions(participant)` rather than
  scanning every region. The optimization is behaviour-preserving and
  uses the cached lookup so the 1805 Europe map does not pay an O(R)
  cost per `/diplomatic_preview` call.
- (3) P2 UX fix: `build_incoming_settlement_offer_popup` renders
  `gold_per_turn`, `region_transfer`, `forced_alliance`, `vassalage`,
  `subjugation`, and `liberation` clauses with structured copy instead
  of the bare `ttype.replace("_", " ").title()` fallback.

Godot (source-level scan):

- (4) `proposal_confirm_popup.gd` collapses the previous double-banner
  cluster (Talleyrand reasoning + outcome banner) into a single
  surrender-draft banner when `surrender_preset=true`.
- (5) `proposal_confirm_popup.gd` suppresses the "Top pressure" line
  when the acceptance band is `accept`/`acceptable` and the score
  comfortably exceeds threshold (>= +10).

Dialogue manager:

- (6) `DialogueManager.iter_queue()` is the public read-only view of
  queued dialogues; behaviour pinned in
  `tests/test_dialogue_manager.py::TestDialogueManagerIterQueue`. This
  bundle adds a backend-call test that the settlement-preview helpers
  route their `_queue` peeks through the public method rather than the
  private attribute.
"""

from __future__ import annotations

import pathlib
from typing import Any, Dict, List, Mapping

import pytest

from backend.game_logic.settlement_preview import (
    build_incoming_settlement_offer_popup,
)
from backend.game_logic.settlement_offers import (
    _is_offer_known_to_dialogue_manager,
)
from backend.game_logic.settlement_routes import (
    _settlement_dialogue_active,
)
from backend.game_logic.settlement_scoring import (
    FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE,
    compute_forced_alliance_continental_toggle_differential,
)
from backend.models.dialogue_manager import DialogueManager
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


GODOT_ROOT = (
    pathlib.Path(__file__).resolve().parents[1]
    / "godot-client"
    / "project-sovereign"
    / "scripts"
)


# ─────────────────────────────────────────────────────────────────────────────
# (1) P1: balance_post_share float -> balance_post_share_pct int
# ─────────────────────────────────────────────────────────────────────────────


def _make_forced_alliance_world() -> tuple[WorldState, str]:
    world = WorldState()
    world.current_turn = 5
    war_id = "war_tier3_001"
    war_instance = make_synthetic_war_instance(
        war_id=war_id,
        attackers=["France"],
        defenders=["Austria"],
        attacker_leader="France",
        defender_leader="Austria",
    )
    world.war_instances = {war_id: war_instance}
    return world, war_id


def _forced_alliance_term(*, from_n: str, to_n: str, cs: bool) -> Dict[str, Any]:
    return {
        "type": "forced_alliance",
        "from": from_n,
        "to": to_n,
        "includes_continental_system": cs,
    }


class TestTier3BalancePostSharePctIsInt:
    """P1 Rule 2 — every numeric field must be int for Godot safety."""

    def test_balance_post_share_pct_is_int_not_float(self):
        world, war_id = _make_forced_alliance_world()
        rows = compute_forced_alliance_continental_toggle_differential(
            world,
            war_id=war_id,
            settlement_terms=[
                _forced_alliance_term(from_n="Austria", to_n="France", cs=True),
            ],
        )
        assert len(rows) == 1
        with_cs = rows[0]["with_continental_system"]
        without_cs = rows[0]["without_continental_system"]
        assert isinstance(with_cs["balance_post_share_pct"], int)
        assert isinstance(without_cs["balance_post_share_pct"], int)
        # Golden Rule 2: bool is a subtype of int in Python; assert
        # the field is a real int, not a bool sneaking through.
        assert type(with_cs["balance_post_share_pct"]) is int
        assert type(without_cs["balance_post_share_pct"]) is int

    def test_legacy_balance_post_share_float_field_is_gone(self):
        world, war_id = _make_forced_alliance_world()
        rows = compute_forced_alliance_continental_toggle_differential(
            world,
            war_id=war_id,
            settlement_terms=[
                _forced_alliance_term(from_n="Austria", to_n="France", cs=True),
            ],
        )
        with_cs = rows[0]["with_continental_system"]
        without_cs = rows[0]["without_continental_system"]
        assert "balance_post_share" not in with_cs
        assert "balance_post_share" not in without_cs

    def test_threat_delta_difference_still_matches_surcharge(self):
        # Surrounding contract pinned by
        # tests/test_settlement_forced_alliance_continental_toggle.py;
        # mirror it here so the Tier 3 sweep flags any drift.
        world, war_id = _make_forced_alliance_world()
        rows = compute_forced_alliance_continental_toggle_differential(
            world,
            war_id=war_id,
            settlement_terms=[
                _forced_alliance_term(from_n="Austria", to_n="France", cs=True),
            ],
        )
        assert rows[0]["threat_delta_difference"] == int(
            FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE
        )


# ─────────────────────────────────────────────────────────────────────────────
# (2) P2 Rule 8: concession baseline uses get_nation_regions
# ─────────────────────────────────────────────────────────────────────────────


class TestTier3ConcessionBaselineUsesGetNationRegions:
    """P2 Rule 8 — no per-region scan in `/diplomatic_preview` hot path."""

    def test_concession_baseline_calls_get_nation_regions_for_each_proposer(self):
        from backend.game_logic import settlement_baseline

        world = WorldState()
        world.current_turn = 4

        calls: List[str] = []
        original_lookup = world.get_nation_regions

        def _spy(nation: str):
            calls.append(nation)
            return original_lookup(nation)

        world.get_nation_regions = _spy  # type: ignore[assignment]

        settlement_baseline._concession_baseline_select_transferable_region(
            world,
            proposer_side_participants=["France", "Austria"],
            accepting_leader="Britain",
        )

        # Both proposers must be probed through the cached lookup.
        assert "France" in calls
        assert "Austria" in calls

    def test_concession_baseline_returns_same_region_with_and_without_helper(self):
        # Behaviour preservation: the optimization must select the same
        # region as the legacy full-scan path. We assert by running the
        # helper twice with the live world and against a stub world
        # whose `get_nation_regions` is deleted so the defensive
        # fallback runs.
        from backend.game_logic import settlement_baseline

        world = WorldState()
        world.current_turn = 4

        original = settlement_baseline._concession_baseline_select_transferable_region(
            world,
            proposer_side_participants=["France"],
            accepting_leader="Britain",
        )

        # Force the defensive fallback by removing the helper.
        class _Shim:
            def __init__(self, src: WorldState) -> None:
                self.regions = src.regions
                self.current_turn = src.current_turn
                self.region_connections = getattr(src, "region_connections", {})

        shim = _Shim(world)
        fallback = settlement_baseline._concession_baseline_select_transferable_region(
            shim,
            proposer_side_participants=["France"],
            accepting_leader="Britain",
        )
        assert original == fallback


# ─────────────────────────────────────────────────────────────────────────────
# (3) P2 UX: non-gold clause rendering in incoming offer popup
# ─────────────────────────────────────────────────────────────────────────────


def _incoming_offer(*, terms: List[Mapping[str, Any]]) -> Dict[str, Any]:
    return {
        "type": "incoming_settlement_offer",
        "offer_id": "offer_tier3_a",
        "war_id": "war_tier3_001",
        "proposer_nation": "Britain",
        "accepting_side": "defenders",
        "covered_enemy_participants": ["France"],
        "settlement_terms": list(terms),
    }


class TestTier3IncomingOfferNonGoldClauseRendering:
    """P2 UX — non-gold clauses must render with structured copy."""

    def test_region_transfer_renders_with_region_and_parties(self):
        world = WorldState()
        offer = _incoming_offer(
            terms=[
                {"type": "peace"},
                {
                    "type": "region_transfer",
                    "region": "Hannover",
                    "from": "France",
                    "to": "Britain",
                },
            ]
        )
        popup = build_incoming_settlement_offer_popup(world, offer)
        joined = " | ".join(popup["terms_summary"])
        assert "Peace" in joined
        # Structured copy: region name + both parties appear together
        # rather than the bare label.
        assert "Hannover" in joined
        assert "France" in joined and "Britain" in joined

    def test_forced_alliance_includes_continental_system_suffix_when_toggle_on(self):
        world = WorldState()
        offer = _incoming_offer(
            terms=[
                {"type": "peace"},
                {
                    "type": "forced_alliance",
                    "from": "France",
                    "to": "Britain",
                    "includes_continental_system": True,
                },
            ]
        )
        popup = build_incoming_settlement_offer_popup(world, offer)
        joined = " | ".join(popup["terms_summary"])
        assert "Forced alliance" in joined
        assert "Continental System" in joined

    def test_forced_alliance_omits_continental_system_suffix_when_toggle_off(self):
        world = WorldState()
        offer = _incoming_offer(
            terms=[
                {
                    "type": "forced_alliance",
                    "from": "France",
                    "to": "Britain",
                    "includes_continental_system": False,
                },
            ]
        )
        popup = build_incoming_settlement_offer_popup(world, offer)
        joined = " | ".join(popup["terms_summary"])
        assert "Forced alliance" in joined
        assert "Continental System" not in joined

    def test_gold_per_turn_renders_amount_and_duration_and_parties(self):
        world = WorldState()
        offer = _incoming_offer(
            terms=[
                {"type": "peace"},
                {
                    "type": "gold_per_turn",
                    "from": "France",
                    "to": "Britain",
                    "amount": 50,
                    "turns": 4,
                },
            ]
        )
        popup = build_incoming_settlement_offer_popup(world, offer)
        joined = " | ".join(popup["terms_summary"])
        assert "50 gold/turn" in joined
        assert "4 turns" in joined
        assert "France" in joined and "Britain" in joined

    def test_vassalage_subjugation_liberation_render_with_parties(self):
        world = WorldState()
        offer = _incoming_offer(
            terms=[
                {"type": "vassalage", "from": "France", "to": "Britain"},
                {"type": "subjugation", "from": "Spain", "to": "Britain"},
                {"type": "liberation", "region": "Poland"},
            ]
        )
        popup = build_incoming_settlement_offer_popup(world, offer)
        joined = " | ".join(popup["terms_summary"])
        # All three clause types must render via the canonical
        # `_term_display` helper rather than the bare title-case
        # fallback. Each clause name appears with from/to parties or
        # a region name; the literal title-case fallback for any of
        # them ("Vassalage", "Subjugation", "Liberation" alone with
        # no context) is not the contract.
        assert "France" in joined and "Britain" in joined
        assert "Spain" in joined
        assert "Poland" in joined

    def test_gold_indemnity_keeps_amount_leading_format(self):
        # Regression: gold_indemnity must keep the existing
        # amount-leading format so the popup leads with the offered
        # gold value.
        world = WorldState()
        offer = _incoming_offer(
            terms=[
                {"type": "peace"},
                {
                    "type": "gold_indemnity",
                    "from": "France",
                    "to": "Britain",
                    "amount": 250,
                },
            ]
        )
        popup = build_incoming_settlement_offer_popup(world, offer)
        joined = " | ".join(popup["terms_summary"])
        assert "250 gold" in joined
        assert "France" in joined and "Britain" in joined


# ─────────────────────────────────────────────────────────────────────────────
# (4) Godot: surrender double-banner merge
# ─────────────────────────────────────────────────────────────────────────────


class TestTier3GodotSurrenderBannerMerge:
    """Source-level scans pinning the Godot collapse of the double banner."""

    def test_surrender_preset_banner_block_is_single_branch(self):
        path = GODOT_ROOT / "proposal_confirm_popup.gd"
        text = path.read_text(encoding="utf-8")
        # The new single banner reads the two flags together and renders
        # the staged surrender outcome OR the offered draft, never both.
        assert "var surrender_preset_staged = bool(data.get(\"surrender_preset\", false))" in text
        assert (
            "var surrender_preset_visible = bool(data.get(\"surrender_preset_visible\", false))"
            in text
        )
        # The staged banner must include the outcome label.
        assert "[b]Surrender draft[/b]" in text
        # The previous standalone-outcome banner branch with no
        # reasoning-or-merge logic must be gone — the surrender block is
        # a single if/else now.
        legacy_outcome_only = (
            "if bool(data.get(\"surrender_preset\", false)):\n"
            "\t\tbbcode += \"[color=#d09080][b]Surrender draft[/b]"
        )
        assert legacy_outcome_only not in text


# ─────────────────────────────────────────────────────────────────────────────
# (5) Godot: Top pressure suppression on comfortable accept
# ─────────────────────────────────────────────────────────────────────────────


class TestTier3GodotTopPressureSuppression:
    """Source-level scan for the comfortable-accept suppression branch."""

    def test_top_pressure_line_suppressed_when_total_comfortably_above_threshold(self):
        path = GODOT_ROOT / "proposal_confirm_popup.gd"
        text = path.read_text(encoding="utf-8")
        # Suppression flag must exist, gate on band_code accept/acceptable,
        # and use a >= +10 margin.
        assert "var suppress_top_pressure = false" in text
        assert "band_code in [\"accept\", \"acceptable\"]" in text
        assert "current_total - current_threshold >= 10" in text
        # The Top pressure line render is gated on `not suppress_top_pressure`.
        assert "not suppress_top_pressure" in text


# ─────────────────────────────────────────────────────────────────────────────
# (6) DialogueManager: iter_queue() is used by settlement_preview
# ─────────────────────────────────────────────────────────────────────────────


class TestTier3SettlementPreviewUsesPublicIterQueue:
    """settlement_preview peeks must route through the public method."""

    def test_settlement_dialogue_active_routes_through_iter_queue(self):
        dm = DialogueManager()
        calls = {"iter_queue": 0}
        original = dm.iter_queue

        def _spy() -> List[Dict[str, Any]]:
            calls["iter_queue"] += 1
            return original()

        dm.iter_queue = _spy  # type: ignore[assignment]

        class _StubWorld:
            def __init__(self) -> None:
                self.pending_diplomatic_dialogue = None
                self.dialogue_manager = dm

        _settlement_dialogue_active(_StubWorld(), "war_x")
        assert calls["iter_queue"] >= 1

    def test_is_offer_known_to_dialogue_manager_routes_through_iter_queue(self):
        dm = DialogueManager()
        calls = {"iter_queue": 0, "peek": 0}
        original_iter = dm.iter_queue
        original_peek = dm.peek

        def _spy_iter() -> List[Dict[str, Any]]:
            calls["iter_queue"] += 1
            return original_iter()

        def _spy_peek():
            calls["peek"] += 1
            return original_peek()

        dm.iter_queue = _spy_iter  # type: ignore[assignment]
        dm.peek = _spy_peek  # type: ignore[assignment]

        class _StubWorld:
            def __init__(self) -> None:
                self.dialogue_manager = dm

        _is_offer_known_to_dialogue_manager(_StubWorld(), offer_id="offer_x")
        assert calls["peek"] >= 1
        assert calls["iter_queue"] >= 1
