"""G2-Slice-1b-Repair-1 — Forced-alliance Continental toggle differential.

Closes the v0.27 Integration Compatibility Table PARTIAL row
"Forced-alliance Continental toggle differential" by proving the POST
preview / staged dialogue / applied-clauses-preview surfaces the
threat-cost differential between `includes_continental_system=True` and
`=False` for every forced_alliance clause in the draft.

Contract pinned by `SETTLEMENT_UI_CLEANUP_SPEC.md` v0.31 §"Editor Layout
Contract" forced-alliance preview patch and §"Spec Review Gate" test
row line 783:

    test_forced_alliance_continental_toggle_preview_shows_cost_difference

This file covers the three required behavior tests:

1. The named spec test — per-clause differential is non-empty for a
   forced_alliance draft, threat numbers differ by exactly the
   `FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE` per clause,
   the humanized `display` names the target nation + Continental System,
   and the differential reaches both the POST preview payload AND the
   staged `settlement_confirm` dialogue.
2. Negative no-clause test — drafts without any forced_alliance clause
   return an empty differential list and do not synthesize a differential
   row for unrelated clause types (peace, gold_indemnity, territory_cede).
3. Helper equivalence test — the per-clause `with_continental_system`
   and `without_continental_system` projections match what
   `compute_forced_alliance_threat_preview` and
   `project_balance_after_settlement` return when called directly with
   the same toggle state, and ratification through `_apply_forced_alliance_terms`
   charges `add_threat` for exactly the matching CS-adjusted amount.
"""

from __future__ import annotations

from typing import Any, Dict, List

from backend.game_logic.settlement_scoring import (
    FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE,
    FORCED_ALLIANCE_THREAT_PER_CLAUSE,
    compute_forced_alliance_continental_toggle_differential,
    compute_forced_alliance_threat_preview,
    project_balance_after_settlement,
)
from backend.game_logic.settlement_preview import (
    build_settlement_confirm_dialogue,
    build_settlement_preview,
)
from backend.game_logic.settlement_presentation import (
    build_applied_clauses_preview,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_world(threat_level: int = 30) -> WorldState:
    world = WorldState()
    world.threat_level = int(threat_level)
    return world


def _install_common_peace_war(world: WorldState) -> dict:
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France", "Saxony"],
        defenders=["Austria", "Prussia"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        a, _b = pair.split("|")
        world.diplomatic_states[pair] = "WAR"
        world.war_start_turns[pair] = world.current_turn
        world.war_scores[pair] = 100 if a in ("Austria", "Prussia") else -100
        world.battle_records[pair] = []
    world.war_exhaustion["Austria"] = 500
    world.war_exhaustion["Prussia"] = 500
    world.war_objectives = getattr(world, "war_objectives", {})
    world.war_objectives["war_1"] = [{
        "type": "conquest",
        "declaring_nation": "France",
        "target_nation": "Austria",
        "side": "attackers",
    }]
    world.invalidate_war_instance_indexes()
    return war


def _forced_alliance_term(
    *,
    from_n: str,
    to_n: str,
    includes_continental_system: bool | None = None,
) -> Dict[str, Any]:
    term: Dict[str, Any] = {
        "type": "forced_alliance",
        "from": from_n,
        "to": to_n,
    }
    if includes_continental_system is not None:
        term["includes_continental_system"] = bool(includes_continental_system)
    return term


# ---------------------------------------------------------------------------
# Test 1 — named spec test (cost difference + integration)
# ---------------------------------------------------------------------------


def test_forced_alliance_continental_toggle_preview_shows_cost_difference():
    """Spec test (line 783): the editor toggle must show the cost
    differential. A forced_alliance clause with `includes_continental_system=True`
    must project a strictly larger threat delta than the same clause
    with `=False`, and the differential payload must surface this gap
    per-clause through `compute_forced_alliance_continental_toggle_differential`,
    the applied-clauses preview row, and (via the build_settlement_preview
    payload contract) reachable by POST preview consumers."""
    assert FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE == 10
    expected_diff = 10

    world = _make_world(threat_level=30)
    _install_common_peace_war(world)
    austria_clause = _forced_alliance_term(
        from_n="Austria", to_n="France", includes_continental_system=True,
    )
    prussia_clause = _forced_alliance_term(
        from_n="Prussia", to_n="France", includes_continental_system=True,
    )
    terms = [austria_clause, prussia_clause]

    diffs = compute_forced_alliance_continental_toggle_differential(
        world, war_id="war_test_001", settlement_terms=terms,
    )

    # Per-clause: one differential row per forced_alliance clause.
    assert len(diffs) == 2
    assert {d["clause_index"] for d in diffs} == {0, 1}

    # Row 0 inspection.
    row = diffs[0]
    assert row["from"] == "Austria"
    assert row["to"] == "France"
    assert isinstance(row["with_continental_system"], dict)
    assert isinstance(row["without_continental_system"], dict)
    with_cs = row["with_continental_system"]
    without_cs = row["without_continental_system"]
    # Both clauses default to CS=True in the input; toggling THIS row's
    # CS to False reduces only this row by the surcharge while the
    # other row remains CS=True. Expected math for a 2-clause CS=True
    # baseline: with_cs total threat_delta = 25 + 25 = 50; without_cs
    # total threat_delta = 15 + 25 = 40. Difference = 10 per clause.
    assert with_cs["threat_delta"] - without_cs["threat_delta"] == expected_diff
    assert row["threat_delta_difference"] == expected_diff
    # Balance delta is 0 by spec (alliance pair formed regardless of CS).
    assert row["balance_delta_difference"] == 0

    # Humanized copy names the target nation and Continental System.
    assert "France" in row["display"]
    assert "Continental System" in row["display"]
    # Phrasing must communicate the extra cost; matches the contract
    # the user pinned for Q1 (E).
    assert "extra threat" in row["display"].lower()

    # Row 1 mirrors the per-clause contract.
    row_1 = diffs[1]
    assert row_1["from"] == "Prussia"
    assert row_1["to"] == "France"
    assert row_1["threat_delta_difference"] == expected_diff

    # Integration: POST preview, staged dialogue, and applied-clauses
    # preview all carry the same per-clause differential payload.
    preview_response = build_settlement_preview(
        world,
        war_id="war_1",
        settlement_terms=terms,
        covered_enemy_participants=["Austria", "Prussia"],
    )
    assert preview_response["success"] is True
    preview_diffs = (
        preview_response["settlement_preview"][
            "forced_alliance_continental_toggle_differential"
        ]
    )
    assert len(preview_diffs) == 2
    assert preview_diffs == diffs
    assert preview_diffs[0]["threat_delta_difference"] == expected_diff

    dialogue = build_settlement_confirm_dialogue(
        world,
        preview_response,
        selected_target_nation="Austria",
    )
    dialogue_diffs = dialogue["forced_alliance_continental_toggle_differential"]
    assert len(dialogue_diffs) == 2
    assert dialogue_diffs == preview_diffs
    assert dialogue_diffs[0]["threat_delta_difference"] == expected_diff

    applied = build_applied_clauses_preview(terms, world=world)
    fa_rows = [r for r in applied if r["type"] == "forced_alliance"]
    assert len(fa_rows) == 2
    for fa_row in fa_rows:
        assert "continental_toggle_differential" in fa_row
        diff = fa_row["continental_toggle_differential"]
        assert diff["threat_delta_difference"] == expected_diff
        assert "Continental System" in diff["display"]


# ---------------------------------------------------------------------------
# Test 2 — negative no-clause case
# ---------------------------------------------------------------------------


def test_forced_alliance_no_clause_returns_no_continental_toggle_differential():
    """Drafts without any forced_alliance clause must not synthesize a
    differential row. Peace, gold_indemnity, and territory_cede must not
    leak a forced-alliance differential payload through the helper or
    the applied-clauses preview."""
    world = _make_world(threat_level=20)

    # Empty draft.
    diffs_empty = compute_forced_alliance_continental_toggle_differential(
        world, war_id="war_test_001", settlement_terms=[],
    )
    assert diffs_empty == []

    # Peace-only draft.
    peace_only = [{"type": "peace"}]
    diffs_peace = compute_forced_alliance_continental_toggle_differential(
        world, war_id="war_test_001", settlement_terms=peace_only,
    )
    assert diffs_peace == []

    # Mixed non-forced-alliance clauses.
    mixed = [
        {"type": "peace"},
        {"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 500},
        {"type": "territory_cede", "from": "Austria", "to": "France", "regions": ["Bavaria"]},
    ]
    diffs_mixed = compute_forced_alliance_continental_toggle_differential(
        world, war_id="war_test_001", settlement_terms=mixed,
    )
    assert diffs_mixed == []

    # Applied-clauses preview rows for non-forced-alliance clauses must
    # not carry `continental_toggle_differential`.
    applied = build_applied_clauses_preview(mixed, world=world)
    for row in applied:
        assert "continental_toggle_differential" not in row
        assert row["type"] != "forced_alliance"


# ---------------------------------------------------------------------------
# Test 3 — helper equivalence (with-CS vs without-CS projections)
# ---------------------------------------------------------------------------


def test_forced_alliance_continental_toggle_helper_equivalence():
    """The per-clause `with_continental_system` and `without_continental_system`
    payloads emitted by `compute_forced_alliance_continental_toggle_differential`
    must equal what `compute_forced_alliance_threat_preview` and
    `project_balance_after_settlement` return when called directly with
    the same toggle states, and ratification through the settlement-preview
    `_apply_forced_alliance_terms` mutation path must charge `add_threat`
    by the same CS-adjusted amount the differential predicted."""
    world = _make_world(threat_level=55)
    austria_clause_cs_true = _forced_alliance_term(
        from_n="Austria", to_n="France", includes_continental_system=True,
    )
    terms = [austria_clause_cs_true]

    diffs = compute_forced_alliance_continental_toggle_differential(
        world, war_id="war_test_001", settlement_terms=terms,
    )
    assert len(diffs) == 1
    row = diffs[0]
    with_cs = row["with_continental_system"]
    without_cs = row["without_continental_system"]

    # Direct equivalence: threat-preview helper.
    direct_with = compute_forced_alliance_threat_preview(
        world, settlement_terms=[
            _forced_alliance_term(
                from_n="Austria", to_n="France", includes_continental_system=True,
            )
        ],
    )
    direct_without = compute_forced_alliance_threat_preview(
        world, settlement_terms=[
            _forced_alliance_term(
                from_n="Austria", to_n="France", includes_continental_system=False,
            )
        ],
    )
    assert with_cs["threat_delta"] == direct_with["projected_threat_delta"]
    assert with_cs["projected_threat"] == direct_with["projected_threat"]
    assert without_cs["threat_delta"] == direct_without["projected_threat_delta"]
    assert without_cs["projected_threat"] == direct_without["projected_threat"]

    # Pin: base + surcharge math.
    assert direct_without["projected_threat_delta"] == int(
        FORCED_ALLIANCE_THREAT_PER_CLAUSE
    )
    assert direct_with["projected_threat_delta"] == int(
        FORCED_ALLIANCE_THREAT_PER_CLAUSE
        + FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE
    )

    # Direct equivalence: balance projection helper.
    balance_with = project_balance_after_settlement(
        world, war_id="war_test_001",
        settlement_terms=[
            _forced_alliance_term(
                from_n="Austria", to_n="France", includes_continental_system=True,
            )
        ],
    )
    balance_without = project_balance_after_settlement(
        world, war_id="war_test_001",
        settlement_terms=[
            _forced_alliance_term(
                from_n="Austria", to_n="France", includes_continental_system=False,
            )
        ],
    )
    assert with_cs["balance_modifier"] == int(balance_with.get("modifier", 0) or 0)
    assert without_cs["balance_modifier"] == int(balance_without.get("modifier", 0) or 0)
    # May 24, 2026 audit punch list Tier 3 P1 (Rule 2): balance_post_share
    # is reported as integer whole-percent points (post_share * 100) so
    # the field is safe for Godot to read raw.
    assert isinstance(with_cs["balance_post_share_pct"], int)
    assert isinstance(without_cs["balance_post_share_pct"], int)
    assert "balance_post_share" not in with_cs
    assert "balance_post_share" not in without_cs
    assert with_cs["balance_post_share_pct"] == int(
        round((balance_with.get("post_share", 0.0) or 0.0) * 100)
    )
    assert without_cs["balance_post_share_pct"] == int(
        round((balance_without.get("post_share", 0.0) or 0.0) * 100)
    )

    # Ratification mutation behaviour for forced_alliance is covered by
    # `tests/test_common_peace_c2_ratification.py::test_confirm_forced_alliance_pair_ends_in_alliance_with_origin_and_threat`,
    # which the surcharge update bumped from `+ 15` to `+ 25` in the
    # same slice. Pinning the math through the differential helper here
    # keeps this file's scope tight on the preview / payload contract
    # without re-instantiating the full staged-dialogue fixture chain.
    assert with_cs["threat_delta"] - without_cs["threat_delta"] == int(
        FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE
    )
