"""
Validation layer for LLM parse results.
Ensures LLM can't hallucinate invalid marshals, actions, or targets.

This layer sits between LLM response and command execution to:
1. Clamp scores to valid ranges
2. Reject invalid marshals/actions
3. Clear invalid targets (let executor handle)
4. Block unimplemented features with friendly messages
"""

import re
from typing import List, Optional, Set

from .schemas import ParseResult


# =============================================================================
# VALID GAME ENTITIES
# =============================================================================

# Movement-family actions whose unknown target must survive validation so the
# executor's fuzzy matcher can NAME the unknown place instead of reporting a
# missing destination (Sweep-5). Other actions keep the clear-silently
# recovery (the executor picks a sensible co-located target).
_TARGET_PASSTHROUGH_ACTIONS: Set[str] = {"move", "scout", "naval_expedition"}

# Actions that require marshal + validation
VALID_ACTIONS: Set[str] = {
    "attack",
    "defend",
    "hold",       # Alias for defend, executor handles
    "wait",       # Free action, pass turn
    "move",
    "scout",
    "retreat",
    "drill",
    "fortify",
    "unfortify",
    "stance_change",
    "recruit",
    "charge",     # Cavalry recklessness
    "restrain",   # Restrain reckless cavalry
    "cancel",     # Cancel strategic order (Phase E)
    # Strategic actions (LLM may return these directly)
    "pursue",     # Strategic PURSUE - chasing enemy marshal
    "support",    # Strategic SUPPORT - marching to ally
    "reinforce",  # Alias for support
    "march",      # Strategic MOVE_TO - multi-turn movement
    # Economy actions (Phase 6.2.E)
    "build",      # Build a building at a region
    "repair",     # Repair war damage or damaged building
    # Economy info command (Phase 6.2.G) — free action
    "economy",    # Display treasury/income/upkeep breakdown
    # Garrison command (Session 31) — detach troops to defend a region
    "garrison",   # Leave garrison detachment in current region
    # Square formation (Session 67) — Tactical Triangle Part A
    "form_square",   # Infantry anti-cavalry formation (1 AP)
    "break_square",  # Return to line formation (free)
    # Vassal System (Phase 8 Session 5)
    "invest_vassal",    # Invest in vassal (+10 loyalty)
    "change_autonomy",  # Change vassal autonomy level
    "make_vassal",      # Create a vassal
    "grant_region_to_vassal",  # VS-3: cede a province to a vassal
    # Diplomatic actions — break/downgrade (Phase 8 wiring)
    "diplomatic_break",      # Break an active treaty
    "diplomatic_downgrade",  # Voluntarily downgrade diplomatic state
    # Diplomatic actions — Phase 4 (war declaration, ultimatum)
    "diplomatic_declare_war",  # Declare war on a nation
    "diplomatic_ultimatum",    # Issue ultimatum to a nation
    # Vassal release (Phase 8 Session 5)
    "release_vassal",          # Release a vassal nation
    # Diplomatic actions — LLM-returned meta-actions (Phase 8 wiring)
    "diplomatic_proposal",     # Start diplomatic proposal dialogue
    "diplomatic_mission",      # Start diplomatic mission
    "diplomatic_feasibility",  # Request feasibility check
    "diplomatic_advisory",     # Request advisory conversation
    "diplomatic_error",        # Diplomatic error fallback
    # Memory and Pressure v2.4.3 — B-B7 Make Amends active-redemption verb
    # (standard variant only; grievance variant ships with B-B4 per spec §8.6.1a)
    "make_amends",
    # WPS-A: Set war purpose (0 AP political declaration)
    "set_war_purpose",
    # WB-C: Repudiate a live war bargain
    "repudiate_bargain",
    # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 White Peace Affordance —
    # distinct labeled action that stages settlement_confirm with
    # white_peace=true and bypasses the editor empty-Ratify gate.
    "propose_white_peace",
    # ES-7 Estate Endowment (Economy Revisit S7) — "endow Ney with Swabia";
    # marshal + region target, validated like other marshal actions.
    "grant_dotation",
    # ES-7 second pass (§0.6.8) — the rente: "grant Ney a rente" /
    # "revoke Ney's rente"; marshal-only, face auto-sized in the executor.
    "grant_pension",
    "revoke_pension",
    # Marshal Recruitment (Jealousy v3.2 final phase) — "commission Grouchy";
    # target = candidate name from the nation's authored marshal_pool.
    "recruit_marshal",
    # FA-S9-D1 (slice 14): bring a marshal back from the desk.
    "recall_marshal",
    # AI-2b D5 counter-instruments (AI_INTENT_SPEC §6 D5) — nation-target
    # diplomacy verbs, 1 DP each charged in-executor:
    "sponsor_design",    # "sponsor Prussia against Austria, 200 gold" (0 = licence)
    "buy_off_design",    # "buy off Prussia" — compensation, price derived
    "guarantee_nation",  # "guarantee Saxony" — pledge to defend
    # DEF-5 naval — "The Wooden Wall" (NAVAL_SPEC §9): the four verbs.
    "build_fleet",       # "build ships" / "lay down a ship" — 1 admin AP + 400g
    "set_fleet_posture",  # "blockade the enemy" / "guard home waters"
    "naval_expedition",  # "land Soult in Munster" — the H4 gamble, marshal-carried
    "naval_diversion",   # "order the diversion" — the §5.3 Grand Diversion
    # ═══════ ADD NEW ACTIONS HERE ═══════
    # This is the SINGLE SOURCE OF TRUTH for valid LLM actions.
    # Also update: llm_client.py keywords, parser.py valid_actions,
    # executor.py _execute_*, world_state.py _action_costs
}

# Meta actions that bypass validation entirely
META_ACTIONS: Set[str] = {
    "help",
    "end_turn",
    "debug",
    "status",
    "unknown",  # Failed parse, let executor handle error message
    "economy",  # Free info command, no marshal needed (Phase 6.2.G)
    # Vassal commands (Phase 8 Session 5) — no marshal needed
    "invest_vassal",
    "change_autonomy",
    "make_vassal",
    "grant_region_to_vassal",  # VS-3
    # AI-2b D5 instruments — nation-target, no marshal needed
    "sponsor_design",
    "buy_off_design",
    "guarantee_nation",
    # DEF-5 naval — nation-level fleet orders, no marshal needed
    # (naval_expedition is deliberately NOT here: it carries a corps).
    "build_fleet",
    "set_fleet_posture",
    "naval_diversion",
    # Diplomatic actions — no marshal needed
    "diplomatic_break",
    "diplomatic_downgrade",
    "diplomatic_declare_war",
    "diplomatic_ultimatum",
    # Diplomatic meta-actions (Phase 8 wiring)
    "release_vassal",
    "diplomatic_proposal",
    "diplomatic_mission",
    "diplomatic_feasibility",
    "diplomatic_advisory",
    "diplomatic_error",
    # Memory and Pressure v2.4.3 — B-B7 (no marshal needed, paid in DP/gold)
    "make_amends",
    # WPS-A: Set war purpose — no marshal needed
    "set_war_purpose",
    # WB-C: Repudiate war bargain — no marshal needed
    "repudiate_bargain",
    # Imperial Settlement (WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §11) —
    # opens the C2 settlement_confirm dialogue. No marshal needed.
    "propose_common_peace",
    # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 White Peace Affordance —
    # distinct labeled action that stages settlement_confirm with
    # white_peace=true and bypasses the editor empty-Ratify gate.
    "propose_white_peace",
    # SC-30 / Slice G1 — ask the enemy war leader to name settlement
    # terms (the Request Terms lifecycle). No marshal needed.
    "request_terms",
}

# FA slice 7 (FA-N9): ONE list. parser.py kept a THIRD hand-copied "needs no
# marshal" list beside META_ACTIONS, and the three naval verbs were in
# neither copy — so `lay down a ship` (the help text's own example) fell
# into the marshal word-scan and asked "Did you mean Davout?". The parser's
# list is now META_ACTIONS | PARSER_ONLY_META; the two are disjoint by pin,
# and the seven parser-only entries are genuine orders (charge, restrain,
# build, repair, recruit) plus the two routed-by-hand verbs.
PARSER_ONLY_META = frozenset({
    "charge", "restrain", "build", "repair", "meta_command", "cheat", "recruit",
})

# The Aug 30, 2026 review's rule, moved here from parser.py so the parser's
# strategic gate and llm_client's LLM-fallback gate read ONE set: a READ or a
# housekeeping verb, never an order to a marshal. Deliberately NOT META_ACTIONS
# and NOT the executor's `free_actions` (which holds retreat/wait).
NON_ORDER_ACTIONS = frozenset({
    "help", "status", "debug", "cheat", "economy", "treasury", "finances",
    "end_turn", "meta_command",
})

# FA slice 7: verbs the STRATEGIC layer may never upgrade. Measured before
# this set existed: `withdraw Ney's rente` parsed as revoke_pension and then
# the strategic table's bare "withdraw" upgraded it into a 2-AP MOVE_TO toward
# a phantom province "Ney'S Rente" — the same road stood open to every
# administrative verb whose sentence carried a march word. META_ACTIONS is in
# the set because a marshal-less verb has nobody to carry a standing order;
# "unknown" rides along harmlessly (validation refuses it before the
# strategic layer ever runs — measured, no unknown parse is rescued today).
ADMINISTRATIVE_ACTIONS = frozenset({
    "grant_pension", "revoke_pension", "grant_dotation", "recruit_marshal",
    "recall_marshal",
    "recruit", "build", "repair", "garrison",
})
NEVER_STRATEGIC_ACTIONS = frozenset(
    META_ACTIONS | NON_ORDER_ACTIONS | ADMINISTRATIVE_ACTIONS)

# Valid stances for stance_change action
VALID_STANCES: Set[str] = {
    "aggressive",
    "defensive",
    "neutral",
}

# CR-3(d): the only actions a diplomatic_data payload may carry into the
# executor's dialogue dispatch. parser.py trusts diplomatic_data["action"]
# over the top-level action, so an unvalidated live-LLM payload could
# smuggle an arbitrary dispatch key past the anti-hallucination layer
# (latent until BYOK arms live parsing for players). Mirrors the full set
# the mock parser's diplomatic router can emit.
DIPLOMATIC_ACTION_ALLOWLIST: Set[str] = {
    "diplomatic_proposal",
    "diplomatic_mission",
    "diplomatic_feasibility",
    "diplomatic_advisory",
    "diplomatic_error",
    "diplomatic_break",
    "diplomatic_downgrade",
    "diplomatic_declare_war",
    "diplomatic_ultimatum",
    "make_amends",
    "set_war_purpose",
    "repudiate_bargain",
    "propose_common_peace",
    "propose_white_peace",
    "request_terms",
}

# CR-3(d) review fix: the fields a PARSE may legitimately mint on
# diplomatic_data — exactly the mock diplomatic router's output contract.
# Everything else is stripped at the seam: the executor's dialogue dispatch
# trusts flags like confirmed_objection / _treaty_warning_resolved /
# ally_entry_decisions, which are added by DIALOGUE RESPONSES downstream and
# must never arrive pre-set from an LLM parse (confirmation-gate bypass).
DIPLOMATIC_DATA_ALLOWED_FIELDS: Set[str] = {
    "action",
    "diplomat",
    "target_nation",
    "proposal_type",
    "clauses",
    "mission_type",
    "is_question",
    "has_diplomatic_keywords",
    "tone",
    "raw_text",
    "amends_variant",
    "objective_type",
    "error",
    "message",
}


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def _edit_distance_le2(a: str, b: str) -> bool:
    """True when Levenshtein(a, b) <= 2. Small bounded DP — validation.py is a
    leaf module and must not import the parser's helper (circular)."""
    if abs(len(a) - len(b)) > 2:
        return False
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1,
                               previous[j - 1] + (ca != cb)))
        if min(current) > 2:
            return False
        previous = current
    return previous[-1] <= 2


def _marshal_mentioned(raw_text: str, marshal: str) -> bool:
    """Word-boundary (typo-tolerant) check that the utterance actually names
    the marshal. Tokens shorter than 4 chars must match exactly; longer ones
    tolerate edit distance <= 2 (the fuzzy budget the parser itself uses)."""
    name = marshal.lower()
    for token in re.findall(r"[a-zA-Z][a-zA-Z'\-]+", raw_text.lower()):
        if token == name:
            return True
        if len(token) >= 4 and len(name) >= 4 and _edit_distance_le2(token, name):
            return True
    return False


def validate_parse_result(
    result: ParseResult,
    valid_marshals: List[str],
    valid_regions: List[str],
    valid_targets: List[str],  # regions + enemy marshals
    raw_text: Optional[str] = None,
) -> ParseResult:
    """
    Validate and sanitize LLM parse result.

    Validation rules:
    - Meta actions (help, debug, etc.) → bypass validation
    - Invalid marshals → matched=False + suggestion
    - Marshal the utterance never named → cleared (CR-4 focus / CR-2
      clarification own the default, exactly as in mock mode)
    - Multi-marshal commands → "coming soon"
    - Strategic commands → "coming soon"
    - Invalid actions → matched=False + suggestion
    - Invalid target_stance → matched=False + suggestion
    - Invalid targets → cleared silently (executor picks), EXCEPT
      movement-family targets which pass through so the executor's fuzzy
      matcher can name the unknown place
    - Scores → clamped 0-100

    Args:
        result: ParseResult from LLM
        valid_marshals: List of marshal names in game
        valid_regions: List of region names in game
        valid_targets: Combined list of regions + enemy marshals
        raw_text: The player's original utterance (live path only) — enables
            the invented-marshal guard; None skips it (hand-built dicts, mock)

    Returns:
        Validated/corrected ParseResult (mutated in place)
    """
    # CR-3(d): diplomatic_data["action"] is the key parser.py actually
    # dispatches on for diplomatic commands — validate it BEFORE the
    # META_ACTIONS bypass below (which would wave the whole result through
    # on the strength of the top-level action alone).
    if result.diplomatic_data is not None:
        if not result.diplomatic_data:
            # Empty-payload hallucination ({} / "" / []): the dispatch seam
            # (parser.py) keys on truthiness and would ignore it anyway —
            # normalize instead of killing an otherwise-valid parse.
            result.diplomatic_data = None
        elif not isinstance(result.diplomatic_data, dict) or (
                result.diplomatic_data.get("action")
                not in DIPLOMATIC_ACTION_ALLOWLIST):
            diplo_action = (result.diplomatic_data.get("action")
                            if isinstance(result.diplomatic_data, dict)
                            else result.diplomatic_data)
            result.matched = False
            result.diplomatic_data = None
            result.suggestion = (
                f"Unknown diplomatic action: {diplo_action}. "
                "Try: propose peace with <nation>, declare war on <nation>, "
                "or address Talleyrand directly."
            )
            return result
        else:
            # Allowlisted action: strip every field a parse may not mint
            # (confirmation-gate flags etc. — see DIPLOMATIC_DATA_ALLOWED_FIELDS)
            result.diplomatic_data = {
                k: v for k, v in result.diplomatic_data.items()
                if k in DIPLOMATIC_DATA_ALLOWED_FIELDS
            }

    # Convert valid lists to sets for O(1) lookup
    marshal_set = set(valid_marshals)
    target_set = set(valid_targets)

    # ── Applies to EVERY parse, including META actions ──────────────────────
    # July 18, 2026: the META bypass below used to sit ABOVE these two, so a
    # META parse skipped both. That was too wide a hole:
    #
    #   • the score clamp is what guarantees ambiguity/strategic_score are
    #     in-range integers, and downstream feedback does arithmetic on them;
    #   • the Sweep-5 invented-marshal guard exists precisely because the live
    #     LLM will name a marshal the player never uttered — a META action is
    #     no less able to invent one, and the deterministic focus/clarification
    #     flow should own that case here too.
    #
    # What legitimately stays BELOW the bypass: the marshal-set membership
    # check, the multi-marshal check and the VALID_ACTIONS check. META actions
    # are nation-level, carry no marshal, and are deliberately absent from
    # VALID_ACTIONS — so those three would reject them wrongly.
    result.ambiguity = max(0, min(100, result.ambiguity))
    result.strategic_score = max(0, min(100, result.strategic_score))

    if (raw_text and result.marshals and len(result.marshals) == 1
            and result.marshals[0] in marshal_set
            and not _marshal_mentioned(raw_text, result.marshals[0])):
        print(f"[VALIDATION] LLM invented marshal '{result.marshals[0]}' "
              f"for {raw_text!r} — cleared (focus/clarification owns it)")
        result.marshals = []

    # Meta actions bypass the REMAINING validation (see above for what they
    # no longer bypass).
    if result.action in META_ACTIONS:
        return result

    # Validate marshals exist
    if result.marshals:
        invalid_marshals = [m for m in result.marshals if m not in marshal_set]
        if invalid_marshals:
            result.matched = False
            available = ", ".join(valid_marshals[:3])
            if len(valid_marshals) > 3:
                available += "..."
            result.suggestion = f"Unknown marshal: {invalid_marshals[0]}. Available: {available}"
            return result

    # Multi-marshal commands: not yet implemented
    if result.marshals and len(result.marshals) > 1:
        result.matched = False
        result.suggestion = "Multi-marshal commands coming in a future update!"
        return result

    # (Sweep-5 invented-marshal guard hoisted above the META bypass — see the
    # block near the top of this function. It is a live-LLM hallucination
    # guard, and a META parse hallucinates just as readily.)

    # Phase 5.2: Validate strategic command type if present
    VALID_STRATEGIC_TYPES = {"MOVE_TO", "PURSUE", "HOLD", "SUPPORT"}
    if getattr(result, 'is_strategic', False) or getattr(result, 'command_type', '') == "strategic":
        st = getattr(result, 'strategic_type', None)
        if st and st not in VALID_STRATEGIC_TYPES:
            # Invalid strategic type — fall through to tactical
            result.is_strategic = False
            result.strategic_type = None
            print(f"[VALIDATION] Invalid strategic_type '{st}', falling back to tactical")

    # Validate action is known. July 2026 AI audit: a live LLM returning
    # "action": null yielded action=None, which the old truthy guard let
    # through as matched=True — the anti-hallucination layer's one job.
    if not result.action or result.action not in VALID_ACTIONS:
        result.matched = False
        result.suggestion = f"Unknown action: {result.action}. Try: attack, move, defend, scout, fortify, drill"
        return result

    # Validate stance for stance_change action
    if result.action == "stance_change":
        if result.target_stance and result.target_stance not in VALID_STANCES:
            result.matched = False
            result.suggestion = f"Unknown stance: {result.target_stance}. Use: aggressive, defensive, or neutral"
            return result

    # Clear invalid targets silently (let executor/personality pick) — EXCEPT
    # movement-family actions, where a nulled target turns an honest "no such
    # place" into a bogus "Move order requires a destination" (Sweep-5 live
    # finding: "move to Venetia"). Passing the raw string through lets the
    # executor's fuzzy matcher own the verdict ("Region 'Venetia' not found.
    # Nearby: ...") and rescue near-miss spellings the strict set check kills.
    if result.target and result.target not in target_set:
        if result.action not in _TARGET_PASSTHROUGH_ACTIONS:
            result.target = None

    return result
