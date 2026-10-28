"""The October 27, 2026 enemy-AI sweep's seams, held DOWN.

Every behavioural change of the sweep (`SYSTEMS_REFERENCE.md` §157) sits
behind a named function a series arm can replace (`tools/playtest_driver.py
--seam MODULE:NAME=EXPR`, the S13b idiom: the seam becomes `lambda *a, **k:
EXPR`). This list is the sweep OFF: a recorded board — the Step 7 CMD-H
page, the DL arm, the IQ-7 turn-6 board, the Massena march — is reproduced
with it, exactly as `THE_LEAGUE_TREATS_WHEN_SPENT = False` is held in the
IQ-7 fixture. Display-only changes have no seam; they move no board.

`hold_down(monkeypatch)` applies the same list in-process.
"""
from __future__ import annotations

import importlib

OCT27_SEAMS_DOWN = [
    # ── the enemy generals (OCT27-39 … 50) ──
    "backend.ai.enemy_ai:EnemyAI._capture_intent_allowed=True",
    "backend.ai.enemy_ai:EnemyAI._liberation_holder_ok=True",
    "backend.ai.enemy_ai:EnemyAI._crossing_ok=True",
    "backend.ai.enemy_ai:EnemyAI._order_affordable=True",
    "backend.ai.enemy_ai:engagement_fellows=frozenset()",
    "backend.commands.combat_executor:charge_has_a_man=True",
    "backend.ai.enemy_ai:EnemyAI._recovery_holds_fortified=False",
    "backend.ai.enemy_ai:EnemyAI._recovery_dest_blocked=False",
    "backend.ai.enemy_ai:EnemyAI._supply_dest_held=False",
    "backend.ai.enemy_ai:EnemyAI._screen_retreat_unfortifies=False",
    "backend.ai.enemy_ai:EnemyAI._artillery_setting_up=False",
    "backend.ai.enemy_ai:EnemyAI._stance_allowed=(True, '')",
    "backend.ai.enemy_ai:EnemyAI._survival_defend_refused=False",
    "backend.ai.enemy_ai:EnemyAI._staging_order=list(set(a[1]))",
    "backend.ai.enemy_ai:EnemyAI._staging_candidates=[min(a[1], key=a[2])]",
    "backend.ai.enemy_ai:EnemyAI._stagnation_fallback_dests=list(a[4])",
    # ── the AI-to-AI table and the proposal rungs (OCT27-6 … 13, 24 … 27, 38) ──
    "backend.game_logic.ai_diplomacy:proposer_meant_it=True",
    "backend.game_logic.ai_diplomacy:rest_refused_pair=None",
    "backend.game_logic.ai_diplomacy:flush_intent_on_refusal=None",
    "backend.game_logic.ai_diplomacy:slot_claim_allowed=True",
    "backend.game_logic.turn_manager:letter_counted=True",
    "backend.game_logic.ai_diplomacy:auction_rests=False",
    "backend.game_logic.ai_diplomacy:alignment_ask_recent=False",
    "backend.game_logic.ai_diplomacy:committed_gold_lump=0",
    "backend.game_logic.ai_diplomacy:province_return_skips=False",
    "backend.game_logic.ai_diplomacy:repeated_ask_factor=1",
    "backend.game_logic.ai_diplomacy:never_shorter=int(a[1])",
    "backend.game_logic.ai_diplomacy:signing_cools=True",
    "backend.game_logic.ai_diplomacy:_hope_alive=True",
    # ── the intent ladder and the guarantees (OCT27-14 … 20) ──
    "backend.game_logic.agendas:coveted_unmet=not __import__('backend.game_logic.agendas').game_logic.agendas._controlled_by_self_or_vassal(a[0], a[1], a[2])",
    "backend.game_logic.instruments:live_guarantees_of=[r for r in (getattr(a[0], 'diplomatic_guarantees', []) or []) if isinstance(r, dict) and r.get('protected') == a[1]]",
    "backend.game_logic.war_council:reset_stall_on_pass=None",
    "backend.game_logic.war_council:failed_declaration_stalls=False",
    "backend.models.world_state:release_frontier_cache=None",
    # ── the coalition (OCT27-2 … 4) ──
    "backend.game_logic.coalition:brew_cancel_floor=40",
    "backend.game_logic.coalition:rearm_exhaustion_mark=int(a[1])",
    "backend.game_logic.coalition:successor_target=None",
    # ── the other instruments (OCT27-29, 31 … 33) ──
    "backend.game_logic.settlement_third_party:war_is_the_players=False",
    "backend.game_logic.settlement_third_party:bonded_exit_floor=int(a[3]) + int(__import__('backend.game_logic.bond').game_logic.bond.break_ranks_depth(a[0], a[1], a[2])['exhaustion'])",
    "backend.game_logic.bond:exhaustion_depth_ceiling=10**9",
    "backend.game_logic.congress:unwarn_on_relent=None",
    "backend.game_logic.settlement_helpers:merge_keeps_letters=None",
    # ── the player's roads (OCT27-21, 23) ──
    "backend.commands.diplomatic_executor:override_asks_the_table=None",
]

# S14i — the sweep's RULINGS (OCT27-D1 … D13, taken as recommended October 27,
# 2026), one entry per row so `tools/_s14i_series_arms.py` attributes each.
# They join the list above: every recorded board was recorded before them.
S14I_SEAMS_BY_ROW = {
    "D1": ["backend.game_logic.coalition:coalition_friction_floor=None"],
    "D2": ["backend.game_logic.coalition:league_target=getattr(a[0], 'player_nation', 'France')",
           "backend.game_logic.coalition:dissolution_cooldown_turns=__import__('backend.game_logic.coalition').game_logic.coalition.COALITION_COOLDOWN_TURNS",
           "backend.game_logic.settlement_third_party:eclipse_league_holds=False"],
    "D3": ["backend.game_logic.ai_diplomacy:menace_for=int(getattr(a[0], 'threat_level', 0))",
           "backend.game_logic.ai_diplomacy:eclipse_menace_shared=None"],
    "D4": ["backend.game_logic.ai_diplomacy:shared_menace_bonus=0"],
    "D5": ["backend.game_logic.instruments:sponsorship_redundant=__import__('backend.game_logic.instruments').game_logic.instruments.standing_sponsorship_amount(a[0], a[1], a[2]) > 0",
           "backend.game_logic.ai_diplomacy:rivalry_step_allowed=True",
           "backend.game_logic.ai_diplomacy:note_rivalry_step=None"],
    "D6": ["backend.game_logic.war_council:exposure_against=__import__('backend.game_logic.war_council').game_logic.war_council.get_exposure_view(a[0], a[1])",
           "backend.game_logic.instruments:void_unlawful_joins=False",
           "backend.game_logic.war_council:guarantee_deterred=any(g.get('guarantor') != a[1] for g in __import__('backend.game_logic.instruments').game_logic.instruments.live_guarantees_of(a[0], a[3]))"],
    "D7": ["backend.game_logic.instruments:honour_on_road=[]"],
    # S14i part 2 — D8 … D13.
    "D8": ["backend.game_logic.agendas:violation_latch_reads_the_map=False",
           "backend.game_logic.emergent_designs:emergent_design_refreshes=False"],
    "D9": ["backend.game_logic.ai_diplomacy:province_letter_to_player=None"],
    "D10": ["backend.game_logic.diplomacy:personality_term=min(a[0], a[1]) if (a[2] == 'vassalage' or a[3] < -3) else a[0]",
            "backend.game_logic.diplomacy:held_cession_rate=0.0",
            "backend.game_logic.diplomacy:situation_changed_is_free=False",
            "backend.game_logic.diplomacy:forced_alliance_step=0",
            "backend.game_logic.diplomacy:arrival_drift_line=''"],
    "D11": ["backend.game_logic.ai_diplomacy:sweetener_multiplier=float(a[0])",
            "backend.game_logic.ai_diplomacy:compact_aim_for=a[2][0] if a[2] else ''"],
    "D12": ["backend.game_logic.vassal:bribed_client_marches=False",
            "backend.game_logic.settlement_third_party:client_war_waits_for_france=False",
            "backend.game_logic.vassal:onramp_assimilates=False",
            "backend.game_logic.vassal:client_follows_lord_footing='ARMISTICE' if a[0] in ('ARMISTICE', 'DEFENSIVE_ALLIANCE', 'ALLIANCE') else 'PEACE'"],
    "D13": ["backend.ai.enemy_ai:cooldown_by_target=False",
            "backend.ai.enemy_ai:reevaluates_blocked_rung=False",
            "backend.ai.enemy_ai:front_means_hostile=False",
            "backend.ai.enemy_ai:ai_rng=__import__('random')",
            "backend.game_logic.turn_manager:separate_ai_phases=False"],
}
OCT27_SEAMS_DOWN += [spec for row in S14I_SEAMS_BY_ROW for spec in S14I_SEAMS_BY_ROW[row]]

# S14j — the economy rebalance (the user, October 27, 2026: "lets actually fix
# this economy before build"), one entry per amount so
# `tools/_s14j_series_arms.py` attributes each. They join the list above:
# every recorded board was recorded before them.
S14J_SEAMS_BY_ROW = {
    # J1 a detached garrison keeps its pay: a corps detached into a
    # garrison draws the field rate (the standing capital garrisons do not).
    "J1": ["backend.models.world_state:garrisons_draw_pay=False"],
    # J2 conquests cost what they yield: every occupation tier +0.15.
    "J2": ["backend.models.region:occupation_fraction_for=0.50 if a[0] <= 25 else (0.35 if a[0] <= 50 else (0.20 if a[0] <= 75 else 0.10))"],
    # J3 the state's running cost: the crown term 30 → 200, and the AI's
    # purse reads the Net before the Charges (the counsel's rule).
    "J3": ["backend.models.world_state:charges_crown_rate=30",
           "backend.game_logic.reforms:ai_reads_net_before_charges=False"],
}
OCT27_SEAMS_DOWN += [spec for row in S14J_SEAMS_BY_ROW for spec in S14J_SEAMS_BY_ROW[row]]

# S14k — the courts take the field (the user, October 28, 2026: "they should
# get armies or the ability to make them, we want the game dynamic"), one
# entry per row so `tools/_s14k_series_arms.py` attributes each. They join
# the list above: every recorded board was recorded before them.
S14K_SEAMS_BY_ROW = {
    # K1 the 1805 field corps: Saxony's Zezschwitz, Portugal's Bernardim
    # Freire (down: the two courts boot armyless, as before).
    "K1": ["backend.models.world_state:boot_marshal_stands=(a[0] or {}).get('nation') not in ('Saxony', 'Portugal')"],
    # K2 the benches of the courts that had none (down: those benches empty).
    "K2": ["backend.models.world_state:bench_stands=a[0] not in ('Portugal', 'Saxony', 'Hesse', 'Hanover', 'Holland', 'KingdomOfItaly', 'Switzerland', 'Denmark', 'Naples', 'Ottoman')"],
    # K3 a menaced court calls up its first general.
    "K3": ["backend.game_logic.recruitment:court_called_to_arms=False"],
    # K4 a satellite fights its lord's war by its contingent.
    "K4": ["backend.game_logic.recruitment:satellite_serves_by_contingent=False"],
    # K5 the force limit reads the court's tier (down: one floor, 60,000).
    "K5": ["backend.models.world_state:force_limit_floor=60000"],
}
OCT27_SEAMS_DOWN += [spec for row in S14K_SEAMS_BY_ROW for spec in S14K_SEAMS_BY_ROW[row]]


def parse(spec: str):
    target, expr = str(spec).split("=", 1)
    module_name, attr = target.split(":", 1)
    return module_name, attr, expr.strip()


def hold_down(monkeypatch, specs=OCT27_SEAMS_DOWN) -> None:
    """Apply the list in-process through `monkeypatch` (a `pytest.MonkeyPatch`
    for a module-scoped fixture), the driver's own `_apply_seams` semantics."""
    for spec in specs:
        module_name, attr, expr = parse(spec)
        owner = importlib.import_module(module_name)
        *path, name = attr.split(".")
        for step in path:
            owner = getattr(owner, step)
        assert callable(getattr(owner, name)), spec
        monkeypatch.setattr(owner, name, eval("lambda *a, **k: " + expr, {}))
