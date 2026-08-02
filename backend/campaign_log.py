"""
Campaign Log — Fog-filtered event log for player review (Phase 6.5)

Filters world.event_log to narrative-relevant events and applies fog of war
rules so the player only sees what they should know about.

Design decisions:
- 14 event types shown (combat, territory, economy, command categories)
- Fog filtering uses current visibility (consistent with _filter_tactical_events_by_visibility)
- One-liner formatting with safe .get() defaults throughout
"""

from collections import Counter

from backend.models.intel import FULL, PARTIAL


# Action display names — single source in display_names.py (R7)
from backend.display_names import OBJECTION_DISPLAY as _OBJECTION_DISPLAY
from backend.display_names import DEFIANCE_DISPLAY as _DEFIANCE_DISPLAY
from backend.display_names import ally_entry_block_line
from backend.display_names import diplomatic_decision_reason_display
from backend.display_names import display_nation
from backend.display_names import humanize_entity_name
from backend.game_logic.commitments_routing import (
    COMMITMENTS_ROUTES,
    format_commitments_notice,
)


def _display_action(action: str) -> str:
    """Translate raw action name for objection context (gerund form)."""
    if not action:
        return action
    return _OBJECTION_DISPLAY.get(action, action.replace("_", " "))


def _display_defiance_action(action: str) -> str:
    """Translate raw action name for defiance context (past tense)."""
    if not action:
        return action
    return _DEFIANCE_DISPLAY.get(action, action.replace("_", " "))


def _decision_reason_suffix(event: dict) -> str:
    reason = str(event.get("decision_reason", "") or "")
    if not reason:
        return ""
    # W6-0 (BUG-CA-7 log half): "counterparty_reversal" is a cooldown-
    # mechanics tag stamped when the PLAYER answers an AI proposal, not a
    # diplomatic motive — rendering it read as gibberish in the live audit
    # ("(counterparty reversal)"). Suppress it; real AI motives still render.
    if reason == "counterparty_reversal":
        return ""
    return f" ({diplomatic_decision_reason_display(reason)})"


# ============================================================================
# EVENT TYPE WHITELIST — only these 14 types appear in the Campaign Log
# ============================================================================

CAMPAIGN_LOG_TYPES = {
    # Combat
    "battle",
    "bombardment",
    "retreat",
    "marshal_broken",
    "marshal_recovered",
    # W6-7 Marshal Fates
    "marshal_captured",
    "last_stand",
    "marshal_released",
    # Territory
    "region_captured",
    # Economy
    "recruitment",
    "building_started",
    "building_completed",
    "building_damaged",
    "bankruptcy",
    "desertion",
    # Command
    "objection",
    "strategic_order",
    "defiance",
    # W6-5 The Literal Doctrine: fidelity beat (held to his letter while
    # the world shifted — pure narration, no choice)
    "literal_fidelity",
    # Diplomacy (Session 8D)
    "diplomatic_treaty_signed",
    "diplomatic_war_declared",
    "diplomatic_vassal_rebellion",
    "diplomatic_treaty_broken",
    "diplomatic_alliance_cascade",
    "diplomatic_ai_ai_treaty",
    # AI-2a: the court-to-court refusal moment (§5 pin 8's public half)
    "ai_ai_proposal_refused",
    "commitment_paradox_resolved",
    # Deep audit fix: missing event types
    "war_declaration",
    "defensive_cascade",
    "offensive_cascade",
    "coalition_declared",
    "coalition_dissolved",
    "balance_of_europe_shifted",
    # V3 Session 8: missing event types
    "nation_eliminated",
    "vassal_auto_join_war",
    "vassal_refuses_call",  # VS-4: disaffected vassal declines the call-to-arms
    "vassal_transferred",   # VS-5: peace-table lord re-homing
    "vassal_defected",      # VS-6: bribed coalition-flip (transfer or free+war)
    "coalition_member_left",
    # R8 Session 6: 16 previously-silent event types
    "ai_proposal_accepted",
    "ai_proposal_counter_failed",
    "ai_proposal_rejected",
    "auto_downgrade",
    "coalition_brewing_cancelled",
    "coalition_brewing_started",
    "counter_offer_accepted",
    "counter_offer_rejected",
    "diplomatic_discrepancy",
    "diplomatic_downgrade",
    "diplomatic_mission_cancelled_eliminated",
    "diplomatic_mission_started",
    "diplomatic_proposal_sent",
    "garrison_placed",
    "proposal_voided_by_coalition",
    "relationship_change",
    # PL-14: Ultimatum events
    "ultimatum_issued",
    "ultimatum_accepted",
    "ultimatum_rejected",
    # NA-5 §8: incoming AI ultimatum resolution (arrival rides proposal_arrived)
    "ai_ultimatum_accepted",
    "ai_ultimatum_rejected",
    "ai_ultimatum_void",
    # PL-27/PL-34: Proposal queue visibility events
    "proposal_arrived",
    "proposal_expired_unseen",
    "proposal_dropped_overflow",
    # Offer lifetime: lapsed at end of turn
    "offer_lapsed",
    "hard_reject_posture_triggered",
    "hard_reject_posture_cleared",
    # Memory and Pressure v2.4.3 — B-B7 Make Amends (spec §8.6.1)
    "amends_offered",
    # Memory and Pressure v2.4.3 — B-B4 call-to-arms refusal (spec §8.8)
    "call_to_arms_refused_defensive",
    "call_to_arms_refused_offensive",
    "call_to_arms_honored_costly",
    "oathbreaker_posture_triggered",
    "oathbreaker_posture_cleared",
    "war_entry_ledger",
    # Peace Deals BPH-A — peace ratification event
    "peace_ratified",
    # WPS-A — war objectives
    "war_objective_declared",
    "war_objective_ticking_started",
    # WPS-C — forced alliance + liberation
    "forced_alliance_imposed",
    "vassal_liberated",
    # WB-B — war bargain lifecycle
    "bargain_ratified",
    "bargain_triggered",
    "bargain_fulfilled",
    "bargain_breached",
    "bargain_voided",
    # WB-C — war-entry integration
    "hard_block_surfaced",
    "ally_refused_free_join",
    "declaration_backed_out",
    "bargain_repudiated",
    "ally_entry_accepted",
    "ally_entry_refused",
    "counter_bargain_accepted",
    "counter_bargain_rejected",
    # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §11.6 (D1/D2) — settlement
    # reaction event families with their own settlement route metadata.
    "settlement_summary",
    "settlement_digest",
    # SC-33 recurring settlement gold (G4F smoke follow-up): the per-turn
    # payments must survive into the campaign log history, not just the
    # one-morning dispatch.
    "settlement_recurring_gold_paid",
    "settlement_recurring_gold_partial",
    "settlement_recurring_gold_completed",
    "settlement_recurring_gold_cancelled",
    # SC-30 / Slice G1: the Request Terms lifecycle
    "settlement_terms_requested",
    "settlement_terms_request_granted",
    "settlement_terms_request_refused",
    # Slice H (approved July 3, 2026): full-agency ally petitions
    "settlement_ally_petition_granted",
    "settlement_ally_petition_declined",
    "settlement_bargain_honored",
    # ES-7 Estate Endowments (Economy Revisit S7)
    "dotation_granted",
    "estate_lost",
    # ES-7 second pass (§0.6.8) — the rente
    "rente_granted",
    "rente_revoked",
    # W6-8 The Spoils of War — conquered-estate resolution
    "estate_confiscated",
    "estate_respected",
    # Jealousy v3.2 (docs/JEALOUSY_SPEC.md §11)
    "jealousy_fired",
    "jealousy_resolved",
    "jealousy_escalation",
    "jealousy_autonomous",
    "jealousy_confrontation",
    "rivalry_confrontation",
    "glory_crowned",
    # ESP riders (Jealousy v3.2 build)
    "fontainebleau_petition",
    "rente_defaulted",
    # Marshal recruitment
    "marshal_commissioned",
    # Nation Agendas NA-1 (docs/NATION_AGENDAS_SPEC.md)
    "agenda_shift",
    # Nation Agendas NA-3 §5.9 — the Ansbach trap
    "agenda_violation",
    # Nation Agendas NA-6 §11.8 — a nation is proclaimed
    "nation_formed",
    # AI-2b D5 counter-instruments (AI_INTENT_SPEC §6 D5, §3.3, §12.3)
    "sponsorship_granted",
    "sponsorship_reneged",
    "sponsorship_expired",
    "design_bought_off",
    "bargain_reneged",
    "guarantee_pledged",
    "guarantee_abandoned",
    # AI-2d §12.6 — the allegiance auction
    "allegiance_auction_opened",
    "allegiance_auction_resolved",
    # AI-2e §3.7 — the paymaster's gold, on the record
    "british_subsidy",
    # AI-2b review fix — an instrument ending WITHOUT a breaker (term
    # served, ward aggression, or a war nobody can honestly be blamed
    # for) is still on the record; silence was the defect.
    "instrument_lapsed",
    # AI-3 Stage D (AI_INTENT_SPEC §4.3, §4.6a) — the war council's beats:
    # the fore-warned crisis (beat 2), the coercive demand (beat 3's AI-AI
    # arm), the stand-down with its cause named (beat 7, pin 21), and a
    # guarantor honouring its pledge at the declaration.
    "crisis_brewing",
    "coercive_demand",
    "crisis_passed",
    "guarantee_honored",
    # AI-4b Stage D (§4.4) — a third-party war ends without France (beat 6).
    "third_party_peace",
    # §16.1-8 the exclusive ruling — an eclipse coalition yields to the
    # anti-France process the turn France's own alarm crosses brewing.
    "coalition_dissolved_for_france",
    # AI-5b Stage E (§3.6) — a humiliated court promotes its grievance
    # into a real design (emergent designs), and a beaten-then-courted
    # great power reverses into a partner (beat 5, the volte-face).
    "design_promoted",
    "volte_face",
    # DEF-5 naval (NAVAL_SPEC §8 — the appended types, 142→156 flipped
    # consciously at NV-0..NV-3): the Wooden Wall's events.
    "fleet_laid_down",          # a keel goes down (NV-0)
    "fleet_posture",            # blockade/guard order (NV-0)
    "blockade_begins",          # a nation comes under blockade (NV-1)
    "blockade_broken",          # the blockade lifts (NV-1)
    "cs_tier_shift",            # Continental System closure tier change (NV-1)
    "strait_open",              # a crossing verdict flips open (NV-3)
    "strait_shut",              # a crossing verdict flips shut (NV-3)
    "boulogne_camp",            # the descent camp is staged (NV-3)
    "trafalgar",                # a DECISIVE fleet action (NV-2)
    "fleet_action",             # an indecisive fleet action (NV-2)
    "expedition_landed",        # the H4 gamble lands (NV-2)
    "expedition_intercepted",   # caught at sea, corps bled (NV-2)
    "expedition_turned_back",   # the patrols close the passage (NV-2)
    "naval_turnback",           # an AI army halted at a covered strait (NV-2)
}

# ============================================================================
# CATEGORY MAP — maps event type to display category
# ============================================================================

CATEGORY_MAP = {
    "battle": "combat",
    "bombardment": "combat",
    "retreat": "combat",
    "marshal_broken": "combat",
    "marshal_recovered": "combat",
    "region_captured": "territory",
    "recruitment": "economy",
    "building_started": "economy",
    "building_completed": "economy",
    "building_damaged": "economy",
    "bankruptcy": "economy",
    "desertion": "economy",
    # ES-7 Estate Endowments (Economy Revisit S7)
    "dotation_granted": "economy",
    "estate_lost": "economy",
    # ES-7 second pass (§0.6.8) — the rente
    "rente_granted": "economy",
    "rente_revoked": "economy",
    # W6-8 The Spoils of War
    "estate_confiscated": "economy",
    "estate_respected": "economy",
    "objection": "command",
    "strategic_order": "command",
    "defiance": "command",
    "literal_fidelity": "command",
    # Jealousy v3.2 — marshal-drama events live under "command"
    "jealousy_fired": "command",
    "jealousy_resolved": "command",
    "jealousy_escalation": "command",
    "jealousy_autonomous": "command",
    "jealousy_confrontation": "command",
    "rivalry_confrontation": "command",
    "glory_crowned": "command",
    "fontainebleau_petition": "command",
    "rente_defaulted": "economy",
    "marshal_commissioned": "command",
    "marshal_captured": "combat",
    "last_stand": "combat",
    "marshal_released": "diplomacy",
    # Diplomacy (Session 8D)
    "diplomatic_treaty_signed": "diplomacy",
    "diplomatic_war_declared": "diplomacy",
    "diplomatic_vassal_rebellion": "diplomacy",
    "diplomatic_treaty_broken": "diplomacy",
    "diplomatic_alliance_cascade": "diplomacy",
    "diplomatic_ai_ai_treaty": "diplomacy",
    "ai_ai_proposal_refused": "diplomacy",
    "commitment_paradox_resolved": "diplomacy",
    # AI-2b D5 counter-instruments
    "sponsorship_granted": "diplomacy",
    "sponsorship_reneged": "diplomacy",
    "sponsorship_expired": "diplomacy",
    "design_bought_off": "diplomacy",
    "bargain_reneged": "diplomacy",
    "guarantee_pledged": "diplomacy",
    "guarantee_abandoned": "diplomacy",
    # AI-2d §12.6 — the allegiance auction
    "allegiance_auction_opened": "diplomacy",
    "allegiance_auction_resolved": "diplomacy",
    # AI-2e §3.7 — the paymaster subsidy
    "british_subsidy": "diplomacy",
    "instrument_lapsed": "diplomacy",
    "crisis_brewing": "diplomacy",
    "coercive_demand": "diplomacy",
    "crisis_passed": "diplomacy",
    "guarantee_honored": "diplomacy",
    "third_party_peace": "diplomacy",
    "coalition_dissolved_for_france": "diplomacy",
    # Deep audit fix: missing event types
    "war_declaration": "diplomacy",
    "defensive_cascade": "diplomacy",
    "offensive_cascade": "diplomacy",
    "coalition_declared": "diplomacy",
    "coalition_dissolved": "diplomacy",
    "balance_of_europe_shifted": "diplomacy",
    # V3 Session 8: missing event types
    "nation_eliminated": "diplomacy",
    "vassal_auto_join_war": "diplomacy",
    "vassal_refuses_call": "diplomacy",  # VS-4
    "vassal_transferred": "diplomacy",   # VS-5
    "vassal_defected": "diplomacy",      # VS-6
    "coalition_member_left": "diplomacy",
    # DEF-5 naval (NV-0..NV-3): the Wooden Wall's fourteen types.
    "fleet_laid_down": "economy",
    "fleet_posture": "command",
    "blockade_begins": "economy",
    "blockade_broken": "economy",
    "cs_tier_shift": "economy",
    "strait_open": "combat",
    "strait_shut": "combat",
    "boulogne_camp": "combat",
    "trafalgar": "combat",
    "fleet_action": "combat",
    "expedition_landed": "combat",
    "expedition_intercepted": "combat",
    "expedition_turned_back": "combat",
    "naval_turnback": "combat",
    # R8 Session 6: 16 previously-silent event types
    "ai_proposal_accepted": "diplomacy",
    "agenda_shift": "diplomacy",
    "agenda_violation": "diplomacy",
    "design_promoted": "diplomacy",
    "volte_face": "diplomacy",
    "nation_formed": "diplomacy",
    "ai_proposal_counter_failed": "diplomacy",
    "ai_proposal_rejected": "diplomacy",
    "auto_downgrade": "diplomacy",
    "coalition_brewing_cancelled": "diplomacy",
    "coalition_brewing_started": "diplomacy",
    "counter_offer_accepted": "diplomacy",
    "counter_offer_rejected": "diplomacy",
    "diplomatic_discrepancy": "diplomacy",
    "diplomatic_downgrade": "diplomacy",
    "diplomatic_mission_cancelled_eliminated": "diplomacy",
    "diplomatic_mission_started": "diplomacy",
    "diplomatic_proposal_sent": "diplomacy",
    "garrison_placed": "territory",
    "proposal_voided_by_coalition": "diplomacy",
    "relationship_change": "command",
    # PL-14: Ultimatum events
    "ultimatum_issued": "diplomacy",
    "ultimatum_accepted": "diplomacy",
    "ultimatum_rejected": "diplomacy",
    # NA-5 §8: incoming AI ultimatum resolution
    "ai_ultimatum_accepted": "diplomacy",
    "ai_ultimatum_rejected": "diplomacy",
    "ai_ultimatum_void": "diplomacy",
    # PL-27/PL-34: Proposal queue visibility events
    "proposal_arrived": "diplomacy",
    "proposal_expired_unseen": "diplomacy",
    "proposal_dropped_overflow": "diplomacy",
    # Offer lifetime: lapsed at end of turn
    "offer_lapsed": "diplomacy",
    "hard_reject_posture_triggered": "diplomacy",
    "hard_reject_posture_cleared": "diplomacy",
    # Memory and Pressure v2.4.3 — B-B7 Make Amends
    "amends_offered": "diplomacy",
    # Memory and Pressure v2.4.3 — B-B4 call-to-arms refusal (§8.8)
    "call_to_arms_refused_defensive": "diplomacy",
    "call_to_arms_refused_offensive": "diplomacy",
    "call_to_arms_honored_costly": "diplomacy",
    "oathbreaker_posture_triggered": "diplomacy",
    "oathbreaker_posture_cleared": "diplomacy",
    "war_entry_ledger": "diplomacy",
    # Peace Deals BPH-A
    "peace_ratified": "diplomacy",
    # WPS-A — war objectives
    "war_objective_declared": "diplomacy",
    "war_objective_ticking_started": "diplomacy",
    # WPS-C — forced alliance + liberation
    "forced_alliance_imposed": "diplomacy",
    "vassal_liberated": "diplomacy",
    # WB-B — war bargain lifecycle
    "bargain_ratified": "diplomacy",
    "bargain_triggered": "diplomacy",
    "bargain_fulfilled": "diplomacy",
    "bargain_breached": "diplomacy",
    "bargain_voided": "diplomacy",
    # WB-C — war-entry integration
    "hard_block_surfaced": "diplomacy",
    "ally_refused_free_join": "diplomacy",
    "declaration_backed_out": "diplomacy",
    "bargain_repudiated": "diplomacy",
    "ally_entry_accepted": "diplomacy",
    "ally_entry_refused": "diplomacy",
    "counter_bargain_accepted": "diplomacy",
    "counter_bargain_rejected": "diplomacy",
    # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §11.6 (D1/D2)
    "settlement_summary": "diplomacy",
    "settlement_digest": "diplomacy",
    # SC-33 recurring settlement gold (G4F smoke follow-up)
    "settlement_recurring_gold_paid": "diplomacy",
    "settlement_recurring_gold_partial": "diplomacy",
    "settlement_recurring_gold_completed": "diplomacy",
    "settlement_recurring_gold_cancelled": "diplomacy",
    "settlement_terms_requested": "diplomacy",
    "settlement_terms_request_granted": "diplomacy",
    "settlement_terms_request_refused": "diplomacy",
    "settlement_ally_petition_granted": "diplomacy",
    "settlement_ally_petition_declined": "diplomacy",
    "settlement_bargain_honored": "diplomacy",
}


def _is_player_event(event: dict, player_nation: str) -> bool:
    """Check if an event belongs to the player (always shown regardless of fog)."""
    # Direct nation match
    if event.get("nation") == player_nation:
        return True
    if event.get("attacker_nation") == player_nation:
        return True
    if event.get("defender_nation") == player_nation:
        return True
    if event.get("declaring_nation") == player_nation:
        return True
    if event.get("target_nation") == player_nation:
        return True
    # captured_by for region_captured
    if event.get("captured_by") == player_nation:
        return True
    # SC-33 recurring settlement payments — the player is a party as payer
    # or recipient (G4F smoke follow-up).
    if event.get("from_nation") == player_nation:
        return True
    if event.get("to_nation") == player_nation:
        return True
    return False


def _get_event_region(event: dict) -> str:
    """Extract region name from an event dict (various field names used)."""
    return (event.get("location") or event.get("region")
            or event.get("from") or event.get("defender_location")
            or event.get("attacker_location") or event.get("target_region") or "")


def _player_marshal_involved(event: dict, world_state) -> bool:
    """Check if a player marshal is involved in a combat event."""
    player_nation = world_state.player_nation
    for field in ("attacker", "defender", "marshal"):
        name = event.get(field, "")
        if name:
            m = world_state.get_marshal(name)
            if m and m.nation == player_nation:
                return True
    return False


def filter_campaign_log(event_log: list, world_state) -> list:
    """
    Filter the full event log for the Campaign Log overlay.

    Rules:
    1. Only CAMPAIGN_LOG_TYPES are included
    2. Player-generated events (objection, strategic_order) always shown
    3. Player-nation events always shown
    4. Battle/bombardment: shown if player marshal involved OR region FULL
    5. Retreat/marshal_broken/marshal_recovered: player marshal OR region PARTIAL+
    6. Region_captured: player captures always; enemy if region PARTIAL+
    7. Enemy economy events: region PARTIAL+

    Args:
        event_log: Full world.event_log list
        world_state: WorldState for fog checks

    Returns:
        Filtered list of event dicts (originals, not copies)
    """
    if not event_log:
        return []

    player_nation = world_state.player_nation
    filtered = []

    for event in event_log:
        if not isinstance(event, dict):
            continue

        event_type = event.get("type", "")
        if event_type not in CAMPAIGN_LOG_TYPES:
            continue

        # Command events (player-generated) — always show
        if event_type in ("objection", "strategic_order", "defiance"):
            filtered.append(event)
            continue

        # Player-nation events — always show
        if _is_player_event(event, player_nation):
            filtered.append(event)
            continue

        if event_type == "commitment_paradox_resolved":
            filtered.append(event)
            continue

        # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §11.6 — settlement
        # summary / digest events use their own fog rule (see
        # `settlement_presentation.is_settlement_event_visible`).
        if event_type in ("settlement_summary", "settlement_digest"):
            from backend.game_logic.settlement_presentation import (
                is_settlement_event_visible,
            )
            if is_settlement_event_visible(event, world_state, player_nation):
                filtered.append(event)
            continue

        # Peace ratification: player-involved always; foreign settlements need PARTIAL+.
        if event_type == "peace_ratified":
            from backend.game_logic.diplomatic_ledger import _get_nation_visibility
            nations_to_check = []
            for key in ("proposer_nation", "target_nation"):
                val = event.get(key)
                if val:
                    nations_to_check.append(val)
            nations_to_check.extend(event.get("ratifying_nations", []) or [])
            visible = False
            for nation in nations_to_check:
                if nation == player_nation:
                    visible = True
                    break
                vis = _get_nation_visibility(nation, world_state)
                if vis in (FULL, PARTIAL):
                    visible = True
                    break
            if visible:
                filtered.append(event)
            continue

        # WPS-A: objective declarations are public to known courts; ticking
        # starts are visible to involved belligerents and their close treaty allies.
        if event_type in ("war_objective_declared", "war_objective_ticking_started"):
            from backend.game_logic.diplomatic_ledger import _get_nation_visibility
            declaring = event.get("declaring_nation", "")
            target = event.get("target_nation", "")
            visible = False
            if declaring and world_state.get_diplomatic_state(player_nation, declaring) in (
                "WAR", "ALLIANCE", "DEFENSIVE_ALLIANCE"
            ):
                visible = True
            if target and world_state.get_diplomatic_state(player_nation, target) in (
                "WAR", "ALLIANCE", "DEFENSIVE_ALLIANCE"
            ):
                visible = True
            if event_type == "war_objective_declared":
                for nation in (declaring, target):
                    if nation and _get_nation_visibility(nation, world_state) in (FULL, PARTIAL):
                        visible = True
                        break
            if visible:
                filtered.append(event)
            continue

        # WPS-C: Forced alliance and liberation are diplomatic events visible
        # when either involved nation has PARTIAL+ visibility.
        if event_type in ("forced_alliance_imposed", "vassal_liberated"):
            from backend.game_logic.diplomatic_ledger import _get_nation_visibility
            visible = False
            for nation_field in (
                "imposer", "target", "imposing_nation", "forced_nation",
                "vassal_nation", "former_lord", "liberator", "liberator_nation",
            ):
                n = event.get(nation_field, "")
                if n == player_nation:
                    visible = True
                    break
                if n and _get_nation_visibility(n, world_state) in (FULL, PARTIAL):
                    visible = True
                    break
            if visible:
                filtered.append(event)
            continue

        # From here: enemy events — need fog checks
        region = _get_event_region(event)

        # Battle / bombardment: player marshal involved OR region FULL
        if event_type in ("battle", "bombardment"):
            if _player_marshal_involved(event, world_state):
                filtered.append(event)
                continue
            if region:
                intel = world_state.get_region_intel(region)
                if intel.visibility == FULL:
                    filtered.append(event)
            continue

        # Retreat / marshal_broken / marshal_recovered: player marshal OR PARTIAL+
        if event_type in ("retreat", "marshal_broken", "marshal_recovered"):
            if _player_marshal_involved(event, world_state):
                filtered.append(event)
                continue
            if region:
                intel = world_state.get_region_intel(region)
                if intel.visibility in (FULL, PARTIAL):
                    # FINAL-16: Strip retreat destination if destination region is fogged
                    if event_type == "retreat" and event.get("to"):
                        to_region = event.get("to")
                        to_intel = world_state.get_region_intel(to_region)
                        if to_intel.visibility not in (FULL, PARTIAL):
                            event = dict(event)  # Copy to avoid mutating original
                            del event["to"]
                    filtered.append(event)
            continue

        # Region captured: enemy captures if region PARTIAL+
        if event_type == "region_captured":
            if region:
                intel = world_state.get_region_intel(region)
                if intel.visibility in (FULL, PARTIAL):
                    filtered.append(event)
            continue

        # Bankruptcy: public knowledge — always show
        if event_type == "bankruptcy":
            filtered.append(event)
            continue

        # AI-2d §12.6: an announced flip is town-crier public — the whole
        # point of the beat is that the auction is IN PLAY (pin 11: no
        # hidden dispositions), so both auction events always show.
        # AI-3/AI-4b Stage D: the war-council beats ride the same arm —
        # beat 2 IS the fore-warning contract ("I saw that coming"), and
        # DPF-1 says diplomacy has no fog. A crisis, its demand, its
        # ending, a guarantor marching, and a congress are court
        # knowledge across Europe.
        # AI-5b Stage E: a promoted design and a volte-face are court
        # knowledge too — a sworn revanche and a great power changing
        # sides are the two loudest things a chancery can do.
        if event_type in ("allegiance_auction_opened",
                          "allegiance_auction_resolved",
                          "crisis_brewing", "coercive_demand",
                          "crisis_passed", "guarantee_honored",
                          "third_party_peace",
                          "coalition_dissolved_for_france",
                          "design_promoted", "volte_face"):
            filtered.append(event)
            continue

        # Economy events (enemy): region PARTIAL+
        if event_type in ("recruitment", "building_started", "building_completed",
                          "building_damaged", "desertion",
                          # ES-7: an enemy court's endowments are visible only
                          # where our intel reaches (region PARTIAL+)
                          "dotation_granted", "estate_lost",
                          # W6-8: same rule for conquered-estate resolutions
                          "estate_confiscated", "estate_respected"):
            # Try to get a region for the event
            econ_region = event.get("region") or event.get("location") or ""
            if econ_region:
                intel = world_state.get_region_intel(econ_region)
                if intel.visibility in (FULL, PARTIAL):
                    filtered.append(event)
            # Bankruptcy/desertion may lack region — check nation match
            # (already handled above by _is_player_event for player nation)
            continue

        # Diplomacy events (Session 8D): PARTIAL+ on any relevant nation
        if event_type in ("diplomatic_treaty_signed", "diplomatic_war_declared",
                          "diplomatic_treaty_broken", "diplomatic_alliance_cascade",
                          "diplomatic_ai_ai_treaty",
                          # AI-2a review fix [14]: the court-to-court refusal
                          # rides the same visibility arm as its treaty
                          # sibling — without this branch the event was
                          # silently dropped and NO surface showed it.
                          "ai_ai_proposal_refused",
                          # AI-2b: instrument events ride the same arm —
                          # a player-party event passes the player-event
                          # gate above; court-to-court needs PARTIAL+ on a
                          # named party (payer/recipient/breaker/victim).
                          "sponsorship_granted", "sponsorship_reneged",
                          "sponsorship_expired", "design_bought_off",
                          "bargain_reneged", "guarantee_pledged",
                          "guarantee_abandoned",
                          # AI-2e: the paymaster subsidy rides the same
                          # PARTIAL+ arm (payer/recipient keys)
                          "british_subsidy",
                          "instrument_lapsed",
                          "balance_of_europe_shifted",
                          "call_to_arms_refused_defensive",
                          "call_to_arms_refused_offensive",
                          "call_to_arms_honored_costly"):
            # Check PARTIAL+ on any nation mentioned
            from backend.game_logic.diplomatic_ledger import _get_nation_visibility
            nations_to_check = []
            for key in (
                "nation", "nation_a", "nation_b", "target", "aggressor",
                "breaker", "victim", "honorer", "hegemon", "speaker_nation",
                "proposer", "recipient", "refused_by",
                # AI-2b/AI-2d instrument + auction parties
                "payer", "guarantor", "protected", "winner",
            ):
                val = event.get(key)
                if val:
                    nations_to_check.append(val)
            visible = False
            for nation in nations_to_check:
                if nation == player_nation:
                    visible = True
                    break
                vis = _get_nation_visibility(nation, world_state)
                if vis in (FULL, PARTIAL):
                    visible = True
                    break
            if visible:
                filtered.append(event)
            continue

        # War/cascade events: player-involved or PARTIAL+ on any nation
        if event_type in (
            "war_declaration", "defensive_cascade", "offensive_cascade",
            "war_entry_ledger",
        ):
            from backend.game_logic.diplomatic_ledger import _get_nation_visibility
            nations_to_check = []
            for key in ("aggressor", "target", "defender", "ally", "against", "attacker_ally"):
                val = event.get(key)
                if val:
                    nations_to_check.append(val)
            visible = False
            for nation in nations_to_check:
                if nation == player_nation:
                    visible = True
                    break
                vis = _get_nation_visibility(nation, world_state)
                if vis in (FULL, PARTIAL):
                    visible = True
                    break
            if visible:
                filtered.append(event)
            continue

        # Coalition events: always show (they target France)
        if event_type in ("coalition_declared", "coalition_dissolved", "coalition_member_left"):
            filtered.append(event)
            continue

        # Vassal rebellion: player vassal always shown
        if event_type == "diplomatic_vassal_rebellion":
            filtered.append(event)
            continue

        # Nation eliminated: public knowledge
        if event_type == "nation_eliminated":
            filtered.append(event)
            continue

        # Vassal auto-join / VS-4 refusal / VS-5 transfer / VS-6 defection:
        # show if player involved or PARTIAL+
        if event_type in ("vassal_auto_join_war", "vassal_refuses_call",
                          "vassal_transferred", "vassal_defected"):
            from backend.game_logic.diplomatic_ledger import _get_nation_visibility
            vassal = event.get("vassal") or event.get("nation", "")
            overlord = (event.get("overlord") or event.get("lord")
                        or event.get("from_lord") or event.get("to_lord", ""))
            visible = False
            for nation in (vassal, overlord):
                if nation == player_nation:
                    visible = True
                    break
                if nation:
                    vis = _get_nation_visibility(nation, world_state)
                    if vis in (FULL, PARTIAL):
                        visible = True
                        break
            if visible:
                filtered.append(event)
            continue

        # ── R8 Session 6: fog rules for 16 previously-silent types ──

        # Player-generated diplomacy events: always show
        if event_type in ("diplomatic_proposal_sent", "diplomatic_mission_started",
                          "diplomatic_discrepancy", "counter_offer_accepted",
                          "counter_offer_rejected"):
            filtered.append(event)
            continue

        # AI proposal responses to player: always show (player is target)
        # NA-5: the ultimatum pair is the same shape — the player answered.
        if event_type in ("ai_proposal_accepted", "ai_proposal_rejected",
                          "ai_proposal_counter_failed",
                          "ai_ultimatum_accepted", "ai_ultimatum_rejected",
                          "ai_ultimatum_void"):
            filtered.append(event)
            continue

        # PL-27/PL-34: Proposal queue events + lapse — always show (player-facing)
        if event_type in ("proposal_arrived", "proposal_expired_unseen",
                          "proposal_dropped_overflow", "offer_lapsed",
                          "hard_reject_posture_triggered", "hard_reject_posture_cleared",
                          "oathbreaker_posture_triggered",
                          "oathbreaker_posture_cleared"):
            filtered.append(event)
            continue

        # IGR-A1: the ally-entry hard block. Written only from the PLAYER's own
        # declaration review (build_declaration_preview is the sole live
        # producer), so it is always the player's business — but it carries
        # none of the keys `_is_player_event` checks, so it had no branch here
        # at all and never reached the overlay. No fog concern: it names an
        # ally of the player and the enemy of the war the player is declaring.
        if event_type == "hard_block_surfaced":
            filtered.append(event)
            continue

        # Coalition brewing: always show (targets France)
        if event_type in ("coalition_brewing_started", "coalition_brewing_cancelled",
                          "proposal_voided_by_coalition"):
            filtered.append(event)
            continue

        # Nation Agendas: agenda shifts and neutrality violations are open
        # court knowledge — always show (diplomacy has no fog).
        if event_type in ("agenda_shift", "agenda_violation",
                          "nation_formed"):
            filtered.append(event)
            continue

        # Garrison placed: show if player or region PARTIAL+
        if event_type == "garrison_placed":
            garrison_region = event.get("region", "")
            if garrison_region:
                intel = world_state.get_region_intel(garrison_region)
                if intel.visibility in (FULL, PARTIAL):
                    filtered.append(event)
            continue

        # Relationship change: always show (player marshals only)
        if event_type == "relationship_change":
            filtered.append(event)
            continue

        # Jealousy v3.2: marshal-drama events are PLAYER-court records —
        # enemy friction reaches the player through battle reports and
        # fog-filtered dispatch intel (spec §9b), never the campaign log.
        if event_type in ("jealousy_fired", "jealousy_resolved",
                          "jealousy_escalation", "jealousy_autonomous",
                          "jealousy_confrontation", "rivalry_confrontation",
                          "glory_crowned", "fontainebleau_petition",
                          "rente_defaulted", "marshal_commissioned"):
            if event.get("nation") == world_state.player_nation:
                filtered.append(event)
            continue

        # Diplomatic downgrade / auto_downgrade: PARTIAL+ on either nation
        if event_type in ("diplomatic_downgrade", "auto_downgrade"):
            from backend.game_logic.diplomatic_ledger import _get_nation_visibility
            nations_to_check = []
            for key in ("nation_a", "nation_b"):
                val = event.get(key)
                if val:
                    nations_to_check.append(val)
            visible = False
            for nation in nations_to_check:
                if nation == player_nation:
                    visible = True
                    break
                vis = _get_nation_visibility(nation, world_state)
                if vis in (FULL, PARTIAL):
                    visible = True
                    break
            if visible:
                filtered.append(event)
            continue

        # Mission cancelled (eliminated nation): always show
        if event_type == "diplomatic_mission_cancelled_eliminated":
            filtered.append(event)
            continue

    return filtered


# ════════════════════════════════════════════════════════════
# IGR-B — THE REFUSAL FAMILY COLLAPSE (gate Q1, option (a))
# ════════════════════════════════════════════════════════════

# The ONE campaign-log family whose producer scales O(n²): the court-to-
# court refusal is emitted from a pair loop over every active nation
# (19 at boot → 171 pairs), and refusals are deliberately excluded from
# the anti-spam counter (`ai_diplomacy.py` ~:2649), so a burst turn scans
# and emits across the whole board at once. Measured on the deterministic
# 20-turn ambient run: turn 3 emits 69 raw refusals, of which 23 survive
# the fog filter onto a 26-row page — burying that turn's `agenda_shift`
# ("The court of X takes up a new design") at index 25 of 26.
#
# Deliberately a tuple of ONE. No other campaign-log family has this
# shape, and widening it is not owed work — a new family would have to
# earn a row of its own with its own measurement.
COLLAPSIBLE_REFUSAL_TYPES = ("ai_ai_proposal_refused",)

# Above this many distinct courts on a side, listing them stops being a
# sentence and becomes a roster; the aggregate names only the courts that
# actually carry the burst, or states a bare count if none does.
COLLAPSE_NAMED_LIMIT = 3

# A real burst is heavy-tailed, not flat: measured live, one page carried
# {Prussia 10, Austria 4, Denmark 1, Bavaria 1} — four courts, but Prussia
# alone is 62% of it. Naming by CARDINALITY alone deleted "Prussia knocked
# on ten doors and was turned away at every one", which is the whole story,
# because two minors each made one approach. This is the share one or two
# courts must carry before the sentence names them as the principals.
COLLAPSE_DOMINANCE = 0.6


def collapse_refusal_family(events: list) -> list:
    """Aggregate bursts of court-to-court refusals for DISPLAY only.

    Pure. Called from the `GET /campaign_log` handler *after*
    `filter_campaign_log` — never inside it (51 test call sites depend on
    that function's contract, and the collapse is a view concern).

    Buckets by `(turn, proposal_type)` **within the refusal family only**.
    A bucket of one passes through untouched (the same object). A bucket
    of N is represented by ONE shallow copy of its FIRST member, carrying
    the display-only keys `collapsed_count` and `collapsed_pairs`;
    `format_event_oneliner` renders the aggregate sentence from them.

    Two hard rules, both load-bearing:

    1. **Gate on the event TYPE first.** `filter_campaign_log` returns
       *originals, not copies*, and `(turn, proposal_type)` is NOT unique
       to refusals — `diplomatic_proposal_sent` (the player's own
       proposal), `proposal_arrived` and `offer_lapsed` all carry a
       `proposal_type` from the same vocabulary, and all three take an
       "always show" branch above. A bare key bucket merges the player's
       own diplomacy into the aggregate and deletes it. Verified live:
       `offer_lapsed` lands on turn 3 — the burst turn itself.
    2. **Never mutate the input dicts.** They are the very objects in
       `world.event_log`, which is serialized into every save
       (`world_state.to_dict` copies whatever is there). Stamping
       `collapsed_count` in place would bake view state into the save
       file permanently. Hence `dict(event)`; the family carries six
       scalar keys, so a shallow copy is sufficient.

    The producer is untouched by design: both emission sites are gated on
    `record_diplomatic_refusal`, the writer of `world.diplomatic_refusals`
    that AI-3's ladder gate reads (`war_council` `CRISIS_REFUSALS_REQUIRED`).
    Throttling the producer would change AI war decisions; this does not.

    Args:
        events: fog-filtered event dicts, in log order.

    Returns:
        A new list, same order, with each collapsed bucket represented by
        one synthetic entry at its first member's position.
    """
    if not events:
        return []
    events = list(events)      # the caller's contract says list; do not
                               # silently return [] for any other iterable

    buckets: dict = {}
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        if event.get("type") not in COLLAPSIBLE_REFUSAL_TYPES:
            continue
        key = (event.get("turn"), event.get("proposal_type"))
        buckets.setdefault(key, []).append(index)

    # Only a genuine burst collapses; a lone refusal keeps its own line.
    collapse_at = {}
    superseded = set()
    for key, indices in buckets.items():
        if len(indices) < 2:
            continue
        collapse_at[indices[0]] = key
        superseded.update(indices[1:])

    out = []
    for index, event in enumerate(events):
        if index in superseded:
            continue
        key = collapse_at.get(index)
        if key is None:
            out.append(event)          # untouched, same object
            continue
        members = [events[i] for i in buckets[key]]
        collapsed = dict(event)        # rule 2 — never the model's dict
        collapsed["collapsed_count"] = len(members)
        collapsed["collapsed_pairs"] = [
            {
                "proposer": m.get("proposer"),
                "refused_by": m.get("refused_by") or m.get("recipient"),
            }
            for m in members
        ]
        out.append(collapsed)
    return out


def _unique_in_order(values) -> list:
    """Distinct truthy values, first-seen order (stable copy for tests)."""
    seen = set()
    ordered = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _join_courts(names: list) -> str:
    """'A', 'A and B', 'A, B and C' — chancery list register."""
    if len(names) == 1:
        return names[0]
    return f"{', '.join(names[:-1])} and {names[-1]}"


def _principal_courts(names, count: int) -> list:
    """The one or two courts carrying most of a burst, else an empty list.

    Only consulted once a side is too crowded to list outright. Frequency
    is the point: `collapsed_pairs` keeps every pair, so multiplicity is
    available, and it is the only thing that separates "Prussia was turned
    away by ten courts, and two minors also asked around" from a genuinely
    diffuse season of failed diplomacy.
    """
    tally = Counter(name for name in names if name)
    if len(tally) <= COLLAPSE_NAMED_LIMIT or count <= 0:
        return []
    for how_many in (1, 2):
        top = [name for name, _ in tally.most_common(how_many)]
        if sum(tally[name] for name in top) >= count * COLLAPSE_DOMINANCE:
            return top
    return []


def _collapsed_refusal_line(event: dict, ptype: str, count: int) -> str:
    """One honest sentence for a collapsed refusal bucket.

    The count is always stated: the turn header now reads the collapsed
    row count, so if the sentence did not disclose how many approaches it
    stands for, the rest would have vanished silently — which is worse
    than the spam it replaces.

    Raw nation tags, exactly as the uncollapsed arm and its
    `diplomatic_ai_ai_treaty` sibling pass them: the client repairs them
    through `Utils.humanize_nation_keys_in_text`, and the NA-6 formation
    overrides can only rename a nation that is still a raw tag. Composing
    finished prose with `display_nation` here would bake a dead name into
    the sentence past the point either repair can reach it (the §11.8
    stage-3 hazard IGR-A hit).
    """
    pairs = event.get("collapsed_pairs") or []
    proposers = _unique_in_order(p.get("proposer") for p in pairs)
    refusers = _unique_in_order(p.get("refused_by") for p in pairs)

    # A SMALL bucket loses nothing: when one side is a single court and the
    # other is short enough to list, every name in the uncollapsed rows
    # survives into the aggregate and the collapse is pure profit. Measured
    # live, the common two- and three-row buckets are exactly this shape,
    # and rendering them as "Britain rebuffs 2 courts" threw away the two
    # courts to save one row.
    if len(proposers) == 1 and len(refusers) <= COLLAPSE_NAMED_LIMIT:
        return f"{_join_courts(refusers)} rebuff {proposers[0]} ({ptype})"
    if len(refusers) == 1 and len(proposers) <= COLLAPSE_NAMED_LIMIT:
        return f"{refusers[0]} rebuffs {_join_courts(proposers)} ({ptype})"

    # One court against a crowd — the crowd becomes a number.
    if len(proposers) == 1:
        return f"{len(refusers)} courts rebuff {proposers[0]} ({ptype})"
    if len(refusers) == 1:
        return f"{refusers[0]} rebuffs {len(proposers)} courts ({ptype})"

    # Naming stays symmetric from here: the real board produces both
    # shapes — one page was 5 askers against 10 courts (genuinely
    # anonymous), another was 7 approaches falling on just 2 courts, which
    # is "two courts turned Europe away" and is not a bare count.
    if 2 <= len(proposers) <= COLLAPSE_NAMED_LIMIT:
        return (f"{count} approaches from {_join_courts(proposers)} "
                f"are rebuffed ({ptype})")
    if 2 <= len(refusers) <= COLLAPSE_NAMED_LIMIT:
        return (f"{count} approaches to {_join_courts(refusers)} "
                f"are rebuffed ({ptype})")

    # Too many courts to list — name the ones that ARE the burst, if any.
    chief = _principal_courts((p.get("proposer") for p in pairs), count)
    if chief:
        return (f"{count} approaches rebuffed, chiefly from "
                f"{_join_courts(chief)} ({ptype})")
    chief = _principal_courts((p.get("refused_by") for p in pairs), count)
    if chief:
        return (f"{count} approaches rebuffed, chiefly by "
                f"{_join_courts(chief)} ({ptype})")
    return f"{count} approaches rebuffed among the courts ({ptype})"


def _name_tag(name: str, nation: str) -> str:
    """Format 'Name (Nation)' when nation is available, else just 'Name'.

    Creative audit July 19 2026: enemy marshal keys are camelCase internally
    ("ArchdukeCharles"), and this is the single chokepoint every campaign-log
    marshal line renders through — so the raw key reached the player as
    "ArchdukeCharles (Austria) attacked Massena", one line away from the same
    event's correctly-spaced `enemy_voice`. Humanized here so every call site
    is fixed at once (R7).
    """
    display = humanize_entity_name(name)
    if nation:
        return f"{display} ({display_nation(nation)})"
    return display


def format_event_oneliner(event: dict) -> str:
    """
    Produce a human-readable one-liner for a campaign log event.

    Uses .get() with safe defaults throughout — missing fields produce
    graceful degradation rather than crashes.  Nation tags are appended
    to marshal names so the player can identify friend/foe at a glance.

    Args:
        event: A single event dict from the event log

    Returns:
        Human-readable one-liner string
    """
    event_type = event.get("type", "")
    if event_type in COMMITMENTS_ROUTES and event_type != "witness_strike_recorded":
        return format_commitments_notice(event_type, event)

    if event_type in ("diplomatic_war_declared", "war_declaration") and event.get("breached_treaty"):
        aggressor = event.get("aggressor") or event.get("nation", "Unknown")
        target = event.get("target", "Unknown")
        return f"War declared: {aggressor} -> {target} (shattering {event.get('breached_treaty')})"

    if event_type == "diplomatic_treaty_broken":
        nation = event.get("breaker") or event.get("nation", "Unknown")
        treaty_type = (event.get("treaty_type") or "treaty").replace("_", " ")
        target = event.get("other") or event.get("target") or "Unknown"
        reason_phrase = event.get("reason_phrase", "")
        family = event.get("end_reason_family", "")
        # Distinguish forced / counterparty-led ruptures from voluntary breach
        # so the log one-liner carries the fault classification.
        if family == "obsolescence_or_external":
            return f"Treaty dragged apart: {nation} - {treaty_type} with {target} (cascade)"
        if family == "counterparty_reversal":
            return f"Treaty broken by counterparty: {target} - {treaty_type} with {nation}"
        if reason_phrase:
            return f"Treaty broken: {nation} - {treaty_type} with {target} {reason_phrase}"
        return f"Treaty broken: {nation} - {treaty_type} with {target}"

    if event_type == "commitment_paradox_resolved":
        chosen = event.get("chosen_nation", "Unknown")
        spurned = event.get("spurned_nation", "Unknown")
        reliability_before = event.get("reliability_before")
        reliability_after = event.get("reliability_after")
        if reliability_before is not None and reliability_after is not None:
            return (
                f"Commitment paradox resolved: chose {chosen} over {spurned} "
                f"({reliability_before} -> {reliability_after} reliability)"
            )
        return f"Commitment paradox resolved: chose {chosen} over {spurned}"

    if event_type == "battle":
        # Humanized at binding, not only at _name_tag: the outcome clause
        # ("ArchdukeCharles tactical victory") interpolates these directly and
        # leaked the raw key past the tag chokepoint (creative audit July 19
        # 2026). _name_tag is idempotent on an already-spaced name.
        attacker = humanize_entity_name(event.get("attacker", "Unknown"))
        atk_nation = event.get("attacker_nation", "")
        defender = humanize_entity_name(event.get("defender", "Unknown"))
        def_nation = event.get("defender_nation", "")
        location = event.get("location", "unknown location")
        outcome = event.get("outcome", "")
        atk_cas = event.get("attacker_casualties", 0)
        def_cas = event.get("defender_casualties", 0)
        # F9 fix: combat.py emits attacker_victory / defender_victory /
        # attacker_tactical_victory / defender_tactical_victory / stalemate /
        # mutual_destruction — never the "*_wins" forms this branch used to test,
        # so every real battle rendered as "draw". Map the actual vocabulary.
        if outcome == "attacker_victory":
            result = f"{attacker} decisive victory"
        elif outcome == "attacker_tactical_victory":
            result = f"{attacker} tactical victory"
        elif outcome == "defender_victory":
            result = f"{defender} decisive victory"
        elif outcome == "defender_tactical_victory":
            result = f"{defender} holds the field"
        elif outcome == "mutual_destruction":
            result = "mutual destruction"
        elif outcome in ("stalemate", ""):
            result = "stalemate"
        else:
            result = outcome.replace("_", " ")
        # W6-2 Dynamic Battle Naming: lead with the composed name when the
        # event carries one ("Second Battle of Swabia: ..."); events without
        # a name (legacy saves, garrison assaults) keep the classic form.
        battle_name = event.get("battle_name", "")
        if battle_name:
            line = (f"{battle_name}: {_name_tag(attacker, atk_nation)} attacked "
                    f"{_name_tag(defender, def_nation)} — "
                    f"{result} ({atk_cas:,} / {def_cas:,} casualties)")
        else:
            line = (f"{_name_tag(attacker, atk_nation)} attacked "
                    f"{_name_tag(defender, def_nation)} at {location} — "
                    f"{result} ({atk_cas:,} / {def_cas:,} casualties)")
        # CR-5 Phase 4 rider (d) "words become the record" (§6.4): quote the
        # player's verbatim phrase when this battle came from a delegation the
        # marshal INTERPRETED. Present only on inferred/delegation orders — an
        # explicitly-typed attack carries no phrase, so it is never quoted back.
        deleg_phrase = event.get("delegation_phrase")
        if deleg_phrase:
            line += f' — on your word: "{deleg_phrase}"'
        # W6-6: the enemy commander's one-line register rides as a flavor
        # suffix (already humanized + quoted at composition).
        enemy_voice = event.get("enemy_voice")
        if enemy_voice:
            line += f" — {enemy_voice}"
        return line

    if event_type == "bombardment":
        attacker = event.get("attacker", "Unknown")
        atk_nation = event.get("attacker_nation", "")
        location = (event.get("defender_location")
                    or event.get("attacker_location")
                    or "unknown location")
        defender_casualties = event.get("defender_casualties", 0)
        return (f"{_name_tag(attacker, atk_nation)} bombarded {location} — "
                f"{defender_casualties:,} casualties")

    if event_type == "retreat":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        from_loc = event.get("from", "unknown")
        to_loc = event.get("to", "")
        tag = _name_tag(marshal, nation)
        if to_loc:
            return f"{tag} retreated from {from_loc} to {to_loc}"
        return f"{tag} retreated from {from_loc}"

    if event_type == "marshal_broken":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        location = event.get("location", "unknown location")
        return f"{_name_tag(marshal, nation)} was broken at {location}"

    if event_type == "marshal_recovered":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        location = event.get("location", "")
        tag = _name_tag(marshal, nation)
        if location:
            return f"{tag} recovered at {location}"
        return f"{tag} recovered"

    if event_type == "region_captured":
        captured_by = event.get("captured_by", "Unknown")
        region = event.get("region", "unknown region")
        method = event.get("method", "")
        if method:
            return f"{region} captured by {captured_by} ({method})"
        return f"{region} captured by {captured_by}"

    if event_type == "recruitment":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        amount = event.get("amount", 0)
        recruit_type = event.get("recruit_type", "infantry")
        return f"{_name_tag(marshal, nation)} recruited {amount:,} {recruit_type}"

    if event_type == "building_started":
        building = (event.get("building") or "building").replace("_", " ").title()
        region = event.get("region", "unknown region")
        return f"Construction started: {building} in {region}"

    if event_type == "building_completed":
        building = (event.get("building") or "building").replace("_", " ").title()
        region = event.get("region", "unknown region")
        return f"Construction complete: {building} in {region}"

    if event_type == "building_damaged":
        building = (event.get("building") or "building").replace("_", " ").title()
        region = event.get("region", "unknown region")
        return f"Building damaged: {building} in {region}"

    if event_type == "bankruptcy":
        nation = event.get("nation", "Unknown")
        return f"{nation} treasury bankrupt — desertion imminent"

    if event_type == "desertion":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        amount = event.get("amount", 0)
        return f"Desertion: {_name_tag(marshal, nation)} lost {amount:,} troops"

    if event_type == "jealousy_fired":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        target = event.get("target", "a rival")
        personality = event.get("personality", "")
        if personality == "aggressive":
            return (f"{_name_tag(marshal, nation)}, envious of {target}'s "
                    f"victories, grows restless for glory")
        if personality == "cautious":
            return (f"{_name_tag(marshal, nation)} has grown distant toward "
                    f"{target} — staff report reduced cooperation")
        if personality == "literal":
            return (f"{_name_tag(marshal, nation)} throws himself into his "
                    f"post with obsessive diligence")
        return f"{_name_tag(marshal, nation)} nurses a grievance against {target}"

    if event_type == "jealousy_resolved":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        if event.get("by_action"):
            return (f"{_name_tag(marshal, nation)}'s grievance is settled — "
                    f"he fights with renewed vigor")
        return f"{_name_tag(marshal, nation)}'s resentment cools with time"

    if event_type == "jealousy_escalation":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        target = event.get("target", "a rival")
        return (f"The rivalry between {_name_tag(marshal, nation)} and "
                f"{target} has become entrenched")

    if event_type == "jealousy_autonomous":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        target = event.get("target", "the enemy")
        return (f"{_name_tag(marshal, nation)} attacked {target} on his own "
                f"initiative, hungry for glory")

    if event_type == "jealousy_confrontation":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        choice = event.get("choice", "acknowledge")
        choice_str = {"promise": "was promised glory",
                      "rebuke": "was rebuked",
                      "acknowledge": "was heard"}.get(choice, "was heard")
        return f"{_name_tag(marshal, nation)} aired his grievance and {choice_str}"

    if event_type == "rivalry_confrontation":
        marshal = event.get("marshal", "Unknown")
        other = event.get("other", "a rival")
        nation = event.get("nation", "")
        return (f"Harsh words between {_name_tag(marshal, nation)} and "
                f"{other} — the Emperor intervened")

    if event_type == "glory_crowned":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        return (f"{_name_tag(marshal, nation)} stands crowned with glory — "
                f"the army's most celebrated commander")

    if event_type == "fontainebleau_petition":
        marshals = event.get("marshals", []) or []
        roll = ", ".join(marshals) if marshals else "The marshals"
        choice = event.get("choice", "")
        if choice == "concede":
            return f"The marshals' petition was answered with rentes: {roll}"
        if choice == "refuse":
            return f"The marshals' petition was refused: {roll}"
        if choice == "promise":
            return f"The marshals were promised the next conquest: {roll}"
        return f"The marshals petitioned the Emperor: {roll}"

    if event_type == "rente_defaulted":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        face = int(event.get("face", 0))
        return (f"The treasury defaulted on {_name_tag(marshal, nation)}'s "
                f"rente of {face}g/turn")

    if event_type == "marshal_commissioned":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        location = event.get("location", "the capital")
        return (f"{_name_tag(marshal, nation)} commissioned to the "
                f"marshalate — raises his corps at {location}")

    if event_type == "agenda_shift":
        nation = display_nation(event.get("nation", "Unknown"))
        focus = event.get("focus", "new ambitions")
        return f"The court of {nation} takes up a new design: {focus}"

    if event_type == "agenda_violation":
        violator = display_nation(event.get("violator", "Unknown"))
        holder = display_nation(event.get("guard_holder", "Unknown"))
        region = event.get("region", "its guarded lands")
        return (f"{holder} seethes: {violator}'s columns cross {region} "
                f"in defiance of its neutrality")

    if event_type == "nation_formed":
        formed = event.get("display_name") or display_nation(
            event.get("nation", "Unknown"))
        old = event.get("old_display_name") or ""
        if old and old != formed:
            return f"{old} is no more — {formed} is proclaimed"
        return f"{formed} is proclaimed"

    if event_type == "dotation_granted":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        region = event.get("region", "an estate")
        title = event.get("title", "")
        title_str = f" — styled {title}" if title else ""
        return f"{_name_tag(marshal, nation)} endowed with {region}{title_str}"

    if event_type == "estate_lost":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        region = event.get("region", "his estate")
        return f"{_name_tag(marshal, nation)} stripped of his estate at {region}"

    if event_type == "rente_granted":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        face = int(event.get("face", 0))
        return f"{_name_tag(marshal, nation)} granted a rente of {face}g/turn"

    if event_type == "rente_revoked":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        face = int(event.get("face", 0))
        return f"{_name_tag(marshal, nation)}'s rente of {face}g/turn withdrawn"

    if event_type == "estate_confiscated":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        region = event.get("region", "the estate")
        captor = event.get("confiscated_by", "the conqueror")
        return (f"{captor} confiscated {_name_tag(marshal, nation)}'s "
                f"estate at {region}")

    if event_type == "estate_respected":
        marshal = event.get("marshal", "Unknown")
        nation = event.get("nation", "")
        region = event.get("region", "the estate")
        respecter = event.get("respected_by", "the conqueror")
        return (f"{respecter} honored {_name_tag(marshal, nation)}'s "
                f"title at {region}")

    if event_type == "objection":
        marshal = event.get("marshal", "Unknown")
        action = _display_action(event.get("action", ""))
        resolution = event.get("resolution", "")
        if action and resolution:
            return f"{marshal} objected to {action} ({resolution})"
        if action:
            return f"{marshal} objected to {action}"
        return f"{marshal} objected to order"

    if event_type == "literal_fidelity":
        # W6-5: the beat's message IS the line (composed in marshal_voice).
        return event.get("message", "A literal marshal held to his orders.")

    if event_type == "marshal_captured":
        marshal = event.get("marshal", "Unknown")
        captor = event.get("captor", "the enemy")
        location = event.get("location", "the field")
        return f"Marshal {marshal} CAPTURED by {captor} at {location}"

    if event_type == "last_stand":
        marshal = event.get("marshal", "Unknown")
        location = event.get("location", "the field")
        inflicted = int(event.get("casualties_inflicted", 0) or 0)
        return (f"{marshal}'s last stand at {location} — "
                f"{inflicted:,} enemy casualties before the end")

    if event_type == "marshal_released":
        marshal = event.get("marshal", "Unknown")
        captor = event.get("captor", "captivity")
        reason = (event.get("reason") or "release").replace("_", " ")
        return f"Marshal {marshal} released by {captor} ({reason})"

    if event_type == "strategic_order":
        marshal = event.get("marshal", "Unknown")
        order_type = event.get("order_type", "UNKNOWN")
        # Human-readable order type (MOVE_TO → "move to", HOLD → "hold", etc.)
        display_order = {
            "MOVE_TO": "move to", "HOLD": "hold",
            "SUPPORT": "support", "PURSUE": "pursue",
        }.get(order_type, order_type.lower().replace("_", " "))
        destination = event.get("destination", "")
        if destination:
            return f"{marshal} ordered to {display_order} {destination}"
        return f"{marshal} ordered to {display_order}"

    if event_type == "defiance":
        marshal = event.get("marshal", "Unknown")
        defiance_action = _display_defiance_action(event.get("defiance_action", "acted independently"))
        return f"{marshal} defied orders and {defiance_action} instead"

    # ── Diplomacy events (Session 8D) ──
    if event_type == "diplomatic_treaty_signed":
        nation_a = event.get("nation_a") or (event.get("nations", [None, None])[0] or "Unknown")
        nation_b = event.get("nation_b") or (event.get("nations", [None, None])[1] if len(event.get("nations", [])) > 1 else "Unknown")
        treaty_type = (event.get("treaty_type") or "treaty").replace("_", " ")
        return f"Treaty signed: {nation_a} and {nation_b} ({treaty_type})"

    if event_type == "diplomatic_war_declared":
        aggressor = event.get("aggressor") or event.get("nation", "Unknown")
        target = event.get("target", "Unknown")
        breached_treaty = event.get("breached_treaty", "")
        if breached_treaty:
            return f"War declared: {aggressor} → {target} (shattering {breached_treaty})"
        return f"War declared: {aggressor} → {target}"

    if event_type == "war_objective_declared":
        declaring = event.get("declaring_nation", "Unknown")
        target = event.get("target_nation", "Unknown")
        obj_type = (event.get("objective_type") or "unknown").replace("_", " ").title()
        regions = event.get("target_regions", [])
        region_str = f" (target: {', '.join(regions)})" if regions else ""
        return f"{declaring} declares {obj_type} against {target}{region_str}"

    if event_type == "war_objective_ticking_started":
        declaring = event.get("declaring_nation", "Unknown")
        region = event.get("target_region", "unknown")
        rate = event.get("rate", 0)
        return f"{declaring} holds {region} — ticking war score (+{rate}/turn)"

    if event_type == "forced_alliance_imposed":
        imposer = event.get("imposing_nation") or event.get("imposer", "Unknown")
        target = event.get("forced_nation") or event.get("target", "Unknown")
        return f"Forced alliance: {target} enters alliance with {imposer} under duress"

    if event_type == "vassal_liberated":
        vassal = event.get("vassal_nation", "Unknown")
        former_lord = event.get("former_lord", "")
        liberator = event.get("liberator_nation") or event.get("liberator", "Unknown")
        if former_lord:
            return f"Liberation: {vassal} freed from {former_lord} by {liberator}"
        return f"Liberation: {vassal} freed from vassalage by {liberator}"

    if event_type == "bargain_ratified":
        promiser = event.get("promiser", "France")
        beneficiary = event.get("beneficiary", "Unknown")
        target_enemy = event.get("target_enemy", "Unknown")
        claim_region = event.get("claim_region", "Unknown")
        return f"{promiser} and {beneficiary} ratified a bargain against {target_enemy}: French priority claim on {claim_region}."

    if event_type == "bargain_triggered":
        beneficiary = event.get("beneficiary", "Unknown")
        target_enemy = event.get("target_enemy", "Unknown")
        claim_region = event.get("claim_region", "Unknown")
        return f"{beneficiary} joins against {target_enemy}; the bargain over {claim_region} is now active."

    if event_type == "bargain_fulfilled":
        promiser = event.get("promiser", "Unknown")
        claim_region = event.get("claim_region", "Unknown")
        return f"{promiser} honored the bargain: {claim_region} secured under France's claim."

    if event_type == "bargain_breached":
        fault_nation = event.get("fault_nation", "Unknown")
        beneficiary = event.get("beneficiary", "Unknown")
        claim_region = event.get("claim_region", "Unknown")
        return f"{fault_nation} broke the bargain with {beneficiary} over {claim_region}."

    if event_type == "bargain_voided":
        beneficiary = event.get("beneficiary", "Unknown")
        claim_region = event.get("claim_region", "Unknown")
        end_reason = (event.get("end_reason") or "external").replace("_", " ")
        return f"Bargain with {beneficiary} over {claim_region} lapsed ({end_reason})."

    if event_type == "settlement_summary":
        from backend.game_logic.settlement_presentation import (
            compose_summary_oneliner,
        )

        return compose_summary_oneliner(event)

    if event_type == "settlement_digest":
        from backend.game_logic.settlement_presentation import (
            compose_digest_oneliner,
        )

        return compose_digest_oneliner(event)

    # SC-33 recurring settlement gold (G4F smoke follow-up): the payments
    # fired in the morning dispatch but vanished from the campaign log
    # history entirely (type-filtered out).
    # SC-30 / Slice G1: the Request Terms lifecycle beats.
    if event_type == "settlement_terms_requested":
        return (
            f"Terms requested from {event.get('answering_leader', 'the enemy court')} "
            f"on {event.get('war_label', 'the war')}."
        )

    if event_type == "settlement_terms_request_granted":
        return (
            f"{event.get('answering_leader', 'The enemy court')} answered our "
            f"request with settlement terms for {event.get('war_label', 'the war')}."
        )

    if event_type == "settlement_terms_request_refused":
        return (
            f"{event.get('answering_leader', 'The enemy court')} refused to name "
            f"terms for {event.get('war_label', 'the war')}."
        )

    # Slice H: full-agency ally petition beats.
    if event_type == "settlement_ally_petition_granted":
        return (
            f"Granted {event.get('ally_nation', 'an ally')}'s settlement "
            f"petition over {event.get('claim_region', 'its claim')} on "
            f"{event.get('war_label', 'the war')}."
        )

    if event_type == "settlement_ally_petition_declined":
        return (
            f"Declined {event.get('ally_nation', 'an ally')}'s settlement "
            f"petition over {event.get('claim_region', 'its claim')} on "
            f"{event.get('war_label', 'the war')}."
        )

    if event_type == "settlement_bargain_honored":
        return (
            f"Honored the pledge on {event.get('claim_region', 'the claim')} "
            f"to {event.get('ally_nation', 'an ally')} in the settlement "
            f"draft of {event.get('war_label', 'the war')}."
        )

    if event_type == "settlement_recurring_gold_paid":
        return (
            f"{event.get('from_nation', 'Unknown')} paid "
            f"{event.get('amount_paid', '?')} gold to "
            f"{event.get('to_nation', 'Unknown')} on the settlement of "
            f"{event.get('war_label', 'the war')} "
            f"({event.get('turns_remaining', '?')} turns remaining)."
        )

    if event_type == "settlement_recurring_gold_partial":
        return (
            f"{event.get('from_nation', 'Unknown')} could only pay "
            f"{event.get('amount_paid', '?')}/{event.get('amount_due', '?')} "
            f"gold to {event.get('to_nation', 'Unknown')} on the settlement "
            f"of {event.get('war_label', 'the war')}."
        )

    if event_type == "settlement_recurring_gold_completed":
        return (
            f"Settlement obligation fulfilled: {event.get('total_amount', '?')} "
            f"gold from {event.get('from_nation', 'Unknown')} to "
            f"{event.get('to_nation', 'Unknown')} "
            f"({event.get('war_label', 'the war')})."
        )

    if event_type == "settlement_recurring_gold_cancelled":
        reason = str(event.get("reason", "circumstances")).replace("_", " ")
        return (
            f"Recurring settlement payment from "
            f"{event.get('from_nation', 'Unknown')} to "
            f"{event.get('to_nation', 'Unknown')} cancelled ({reason})."
        )

    if event_type == "hard_block_surfaced":
        # IGR-A1: was `reason.replace("_", " ")` — i.e. "no participation
        # path" straight to the chronicle. The raw key still rides the event
        # (old saves included); only the rendering changed.
        beneficiary = event.get("beneficiary", "Unknown")
        target_enemy = event.get("target_enemy") or event.get("named_enemy", "Unknown")
        return ally_entry_block_line(
            str(event.get("hard_block_reason", "")),
            beneficiary,
            target_enemy,
            str(event.get("promiser", "") or ""),
        )

    if event_type == "ally_refused_free_join":
        beneficiary = event.get("beneficiary", "Unknown")
        target_enemy = event.get("target_enemy") or event.get("named_enemy", "Unknown")
        return f"{beneficiary} declined to join against {target_enemy} without terms."

    if event_type == "declaration_backed_out":
        named_enemy = event.get("named_enemy") or event.get("target_enemy", "Unknown")
        return f"War declaration against {named_enemy} cancelled."

    if event_type == "bargain_repudiated":
        beneficiary = event.get("beneficiary", "Unknown")
        claim_region = event.get("claim_region", "Unknown")
        return f"France repudiated the bargain with {beneficiary} over {claim_region}."

    if event_type == "ally_entry_accepted":
        beneficiary = event.get("beneficiary", "Unknown")
        named_enemy = event.get("named_enemy", "Unknown")
        return f"{beneficiary} joins the war against {named_enemy}."

    if event_type == "ally_entry_refused":
        beneficiary = event.get("beneficiary", "Unknown")
        named_enemy = event.get("named_enemy", "Unknown")
        return f"{beneficiary} refuses to join against {named_enemy}."

    if event_type == "counter_bargain_accepted":
        beneficiary = event.get("beneficiary", "Unknown")
        claim_region = event.get("demanded_region") or event.get("claim_region", "Unknown")
        return f"Counter-bargain accepted: {beneficiary} claims {claim_region}."

    if event_type == "counter_bargain_rejected":
        beneficiary = event.get("beneficiary", "Unknown")
        return f"Counter-bargain from {beneficiary} rejected."

    if event_type == "diplomatic_vassal_rebellion":
        nation = event.get("nation") or event.get("vassal", "Unknown")
        return f"Vassal rebellion: {nation} has broken free!"


    if event_type == "diplomatic_alliance_cascade":
        nation = event.get("defender") or event.get("nation", "Unknown")
        ally = event.get("ally", "Unknown")
        return f"Alliance cascade: {nation} enters war via {ally}"

    if event_type == "diplomatic_ai_ai_treaty":
        nation_a = event.get("nation_a", "Unknown")
        nation_b = event.get("nation_b", "Unknown")
        treaty_type = (event.get("treaty_type") or "treaty").replace("_", " ")
        return f"AI-AI treaty: {nation_a} and {nation_b} ({treaty_type})"

    if event_type == "ai_ai_proposal_refused":
        # AI-2a: the court-to-court refusal — the ask happened, was
        # rebuffed, and the balance of power is WITNESSED (§3.4).
        proposer = event.get("proposer", "Unknown")
        refused_by = event.get("refused_by") or event.get("recipient",
                                                          "Unknown")
        ptype = (event.get("proposal_type") or "proposal").replace("_", " ")
        # IGR-B: a burst of these arrives collapsed into one row.
        count = int(event.get("collapsed_count") or 0)
        if count > 1:
            return _collapsed_refusal_line(event, ptype, count)
        return f"{refused_by} rebuffs {proposer} ({ptype})"

    # AI-2b: the D5 counter-instruments.
    if event_type == "sponsorship_granted":
        payer = display_nation(event.get("payer", "Unknown"))
        recipient = display_nation(event.get("recipient", "Unknown"))
        aim = display_nation(event.get("aim", "")) if event.get("aim") else ""
        if event.get("kind") == "neutrality":
            return (f"{payer} buys {recipient}'s neutrality"
                    + (f" in the war over {aim}" if aim else ""))
        if event.get("licence"):
            return f"{payer} licences {recipient}'s design against {aim}"
        return (f"{payer} sponsors {recipient}"
                + (f" against {aim}" if aim else "")
                + f" ({int(event.get('amount', 0))}g/turn)")

    if event_type == "sponsorship_reneged":
        breaker = display_nation(event.get("breaker", "Unknown"))
        victim = display_nation(event.get("victim", "Unknown"))
        noun = ("licence" if event.get("licence")
                else "neutrality compact"
                if event.get("kind") == "neutrality" else "sponsorship")
        return f"THE BROKEN BARGAIN: {breaker} tears up its {noun} with {victim}"

    if event_type == "sponsorship_expired":
        payer = display_nation(event.get("payer", "Unknown"))
        recipient = display_nation(event.get("recipient", "Unknown"))
        return f"The compact between {payer} and {recipient} lapses"

    if event_type == "design_bought_off":
        payer = display_nation(event.get("payer", "Unknown"))
        recipient = display_nation(event.get("recipient", "Unknown"))
        return f"{payer} buys off {recipient}'s design — the want sleeps"

    if event_type == "bargain_reneged":
        breaker = display_nation(event.get("breaker", "Unknown"))
        victim = display_nation(event.get("victim", "Unknown"))
        return (f"THE BROKEN BARGAIN: {breaker} reneges on its compact "
                f"with {victim} — the design returns")

    if event_type == "guarantee_pledged":
        guarantor = display_nation(event.get("guarantor", "Unknown"))
        protected = display_nation(event.get("protected", "Unknown"))
        return f"{guarantor} guarantees {protected}"

    if event_type == "guarantee_abandoned":
        breaker = display_nation(event.get("breaker", "Unknown"))
        victim = display_nation(event.get("victim", "Unknown"))
        return (f"A guarantee proves paper: {breaker} abandons "
                f"{victim} to its attackers")

    if event_type == "british_subsidy":
        payer = display_nation(event.get("payer", "Unknown"))
        recipient = display_nation(event.get("recipient", "Unknown"))
        amount = int(event.get("amount", 0))
        return f"{payer}'s gold: {amount}g reaches {recipient}"

    if event_type == "instrument_lapsed":
        payer = display_nation(event.get("payer", "Unknown"))
        recipient = display_nation(event.get("recipient", "Unknown"))
        reason = event.get("reason", "")
        if reason == "term_served":
            return (f"The bargain between {payer} and {recipient} is "
                    f"served in full — the design wakes")
        if reason == "ward_aggression":
            return (f"{recipient} marches of its own will — "
                    f"{payer}'s guarantee is void, unblamed")
        return (f"War overtakes the compact between {payer} and "
                f"{recipient} — it lapses, no breaker named")

    if event_type == "crisis_brewing":
        nation = display_nation(event.get("nation", "Unknown"))
        target = display_nation(event.get("target", "Unknown"))
        return f"THE BREWING CRISIS: {nation} will move on {target}"

    if event_type == "coercive_demand":
        nation = display_nation(event.get("nation", "Unknown"))
        target = display_nation(event.get("target", "Unknown"))
        return f"{nation} delivers a final demand to {target} — refused"

    if event_type == "crisis_passed":
        nation = display_nation(event.get("nation", "Unknown"))
        target = display_nation(event.get("target", "Unknown"))
        cause = str(event.get("cause", "starved"))
        # Single source: war_council owns the beat-7 cause taxonomy, incl.
        # AI-3r's exposed / outmatched / penniless (July 25, 2026 review).
        from backend.game_logic.war_council import crisis_cause_phrase
        cause_copy = crisis_cause_phrase(cause)
        return f"THE CRISIS PASSES: {nation} stands down over {target} ({cause_copy})"

    if event_type == "guarantee_honored":
        guarantor = display_nation(event.get("guarantor", "Unknown"))
        ward = display_nation(event.get("ward", "Unknown"))
        aggressor = display_nation(event.get("aggressor", "Unknown"))
        return f"{guarantor} honours its guarantee of {ward} — war on {aggressor}"

    if event_type == "third_party_peace":
        a = display_nation(event.get("proposer", "Unknown"))
        b = display_nation(event.get("accepter", "Unknown"))
        return f"THE CONGRESS: {a} and {b} make peace without France"

    if event_type == "coalition_dissolved_for_france":
        prev = display_nation(event.get("previous_target", "Unknown"))
        return (f"The coalition against {prev} dissolves — Europe "
                f"remembers who the real danger is")

    if event_type == "design_promoted":
        nation = display_nation(event.get("nation", "Unknown"))
        author = display_nation(event.get("author", "Unknown"))
        regions = list(event.get("regions") or [])
        first = regions[0] if regions else "its provinces"
        tail = f" and {len(regions) - 1} more" if len(regions) > 1 else ""
        return (f"REVANCHE: {nation} swears to retake {first}{tail} — "
                f"{author} is not forgiven")

    if event_type == "volte_face":
        nation = display_nation(event.get("nation", "Unknown"))
        partner = display_nation(event.get("partner", "Unknown"))
        return (f"THE VOLTE-FACE: {nation}, beaten and then courted, "
                f"takes {partner}'s hand")

    # ── DEF-5 naval (NV-0..NV-3) ──────────────────────────────────────
    if event_type == "fleet_laid_down":
        nation = display_nation(event.get("nation", "Unknown"))
        return (f"{nation} lays down a ship of the line "
                f"({int(event.get('ships', 0))} sail, readiness "
                f"{int(event.get('readiness', 0))})")

    if event_type == "fleet_posture":
        nation = display_nation(event.get("nation", "Unknown"))
        posture = event.get("posture", "guard")
        return (f"{nation}'s fleet stands out on blockade" if posture == "blockade"
                else f"{nation}'s fleet returns to guard home waters")

    if event_type == "blockade_begins":
        nation = display_nation(event.get("nation", "Unknown"))
        blockader = display_nation(event.get("blockader", "Unknown"))
        return f"BLOCKADE: {blockader} closes {nation}'s ports — trade halved, crews rot at anchor"

    if event_type == "blockade_broken":
        nation = display_nation(event.get("nation", "Unknown"))
        return f"The blockade of {nation} is broken — her ports breathe again"

    if event_type == "cs_tier_shift":
        target = display_nation(event.get("target", "Unknown"))
        pct = int(event.get("closure_pct", 0))
        tier = int(event.get("tier", 0))
        if tier > 0:
            return (f"THE CONTINENTAL SYSTEM: {pct}% of the Continent's ports "
                    f"closed — {target}'s war-weariness rises +{tier}/turn")
        return (f"The Continental System loosens — {pct}% of the Continent's "
                f"ports closed, {target} breathes")

    if event_type == "strait_open":
        a, b = event.get("link_a"), event.get("link_b")
        if a and b:
            return f"THE STRAIT LIES OPEN: the {a}–{b} crossing can be forced"
        nation = display_nation(event.get("nation", "Unknown"))
        against = display_nation(event.get("against", "Unknown"))
        return (f"THE STRAIT LIES OPEN: {nation}'s diversion draws the "
                f"{against} fleet off station")

    if event_type == "strait_shut":
        a = event.get("link_a", "?")
        b = event.get("link_b", "?")
        coverer = display_nation(event.get("coverer", "")) if event.get("coverer") else ""
        tail = f" — {coverer} commands the water" if coverer else ""
        return f"The {a}–{b} crossing is shut{tail}"

    if event_type == "boulogne_camp":
        nation = display_nation(event.get("nation", "Unknown"))
        against = display_nation(event.get("against", "Unknown"))
        return (f"THE CAMP: {nation} masses {event.get('strength', 0):,} men "
                f"on the invasion coast — {against} watches the water")

    if event_type in ("trafalgar", "fleet_action"):
        winner = display_nation(event.get("winner", "Unknown"))
        loser = display_nation(event.get("loser", "Unknown"))
        if event.get("decisive"):
            return (f"TRAFALGAR: {winner}'s line shatters {loser}'s fleet — "
                    f"a decisive action at sea")
        return f"Action at sea: {winner}'s squadrons get the better of {loser}"

    if event_type == "expedition_landed":
        marshal = event.get("marshal", "The expedition")
        target = event.get("target", "?")
        return (f"THE LANDING: {marshal} puts {int(event.get('troops', 0)):,} "
                f"men ashore at {target}")

    if event_type == "expedition_intercepted":
        marshal = event.get("marshal", "The expedition")
        coverer = display_nation(event.get("coverer", "the enemy"))
        return (f"INTERCEPTED: {coverer}'s squadrons catch {marshal}'s "
                f"transports at sea — {int(event.get('troops_lost', 0)):,} men lost")

    if event_type == "expedition_turned_back":
        marshal = event.get("marshal", "The expedition")
        target = event.get("target", "?")
        return f"{marshal}'s expedition to {target} is turned back at sea"

    if event_type == "naval_turnback":
        marshal = event.get("marshal", "An army")
        nation = display_nation(event.get("nation", ""))
        a, b = event.get("link_a", "?"), event.get("link_b", "?")
        prefix = f"{nation}'s {marshal}" if nation else marshal
        return f"{prefix} halts at the {a}–{b} crossing — hostile sail command the water"

    if event_type == "allegiance_auction_opened":
        nation = display_nation(event.get("nation", "Unknown"))
        return f"THE FLIP IS IN PLAY: {nation} weighs its allegiance"

    if event_type == "allegiance_auction_resolved":
        nation = display_nation(event.get("nation", "Unknown"))
        outcome = event.get("outcome", "")
        if outcome == "lapsed":
            return f"The moment passes — {nation} keeps its own counsel"
        if outcome == "no_suitor":
            return f"No court bids for {nation}; the flip dissolves"
        winner = display_nation(event.get("winner") or "Unknown")
        if outcome == "player_offer":
            return (f"{nation} chooses France — their envoy carries "
                    f"the pact")
        return f"THE FLIP: {nation} signs with {winner}"

    # Deep audit fix: new event types
    if event_type == "war_declaration":
        aggressor = event.get("aggressor") or event.get("nation", "Unknown")
        target = event.get("target", "Unknown")
        return f"War declared: {aggressor} → {target}"

    if event_type == "defensive_cascade":
        nation = event.get("nation", "Unknown")
        ally = event.get("ally", "Unknown")
        return f"Defensive cascade: {nation} joins war via {ally}"

    if event_type == "offensive_cascade":
        nation = event.get("nation", "Unknown")
        aggressor = event.get("aggressor", "Unknown")
        return f"Offensive cascade: {nation} joins {aggressor}'s war"

    if event_type == "coalition_declared":
        members = event.get("members", [])
        members_str = ', '.join(members) if members else 'Unknown'
        # Stage D review fix [r6]: an ECLIPSE coalition names its own
        # target — never dressed as a coalition against France.
        target = event.get("target_nation") or "France"
        if target != "France":
            return (f"Coalition formed against {display_nation(target)}! "
                    f"Members: {members_str}")
        return f"Coalition formed against France! Members: {members_str}"

    if event_type == "coalition_dissolved":
        target = event.get("target_nation") or "France"
        if target != "France":
            return f"Coalition against {display_nation(target)} has dissolved."
        return "Coalition against France has dissolved."

    # V3 Session 8: new event types
    if event_type == "nation_eliminated":
        nation = event.get("nation", "Unknown")
        return f"{nation} has been eliminated from the war."

    if event_type == "vassal_auto_join_war":
        vassal = event.get("vassal") or event.get("nation", "Unknown")
        # Drive-by (VS-4 build): the emitter passes "lord"; the old read of
        # only "overlord" rendered every one-liner as "Unknown's war".
        overlord = event.get("overlord") or event.get("lord", "Unknown")
        return f"Vassal {vassal} joined {overlord}'s war."

    if event_type == "vassal_refuses_call":
        # VS-4: a disaffected satellite declines the call-to-arms
        vassal = event.get("vassal", "Unknown")
        lord = event.get("lord", "Unknown")
        loyalty = event.get("loyalty", "?")
        return (f"{vassal} refuses {lord}'s call to arms "
                f"(loyalty {loyalty}).")

    if event_type == "vassal_transferred":
        # VS-5: peace-table lord re-homing
        vassal = event.get("vassal", "Unknown")
        from_lord = event.get("from_lord", "Unknown")
        to_lord = event.get("to_lord", "Unknown")
        return (f"{vassal} passes from {from_lord}'s suzerainty "
                f"to {to_lord}'s.")

    if event_type == "vassal_defected":
        # VS-6: the bribed coalition-flip
        vassal = event.get("vassal", "Unknown")
        lord = event.get("lord", "Unknown")
        briber = event.get("briber", "Unknown")
        outcome = event.get("outcome", "")
        if outcome == "transfer":
            return (f"THE DEFECTION: {briber}'s gold buys {vassal} away "
                    f"from {lord} — it serves a new master.")
        return (f"THE DEFECTION: {briber}'s gold turns {vassal} against "
                f"{lord} — the freed satellite takes the field.")

    if event_type == "coalition_member_left":
        nation = event.get("nation", "Unknown")
        return f"{nation} has left the coalition."

    # ── R8 Session 6: format strings for 16 previously-silent types ──

    # W6-0 (BUG-CA-7 log half): these two events fire when the PLAYER answers
    # an incoming AI proposal — `source` is the nation that PROPOSED, and we
    # are the side that answered. The old copy reversed the direction
    # ("Saxony rejected our open borders proposal" when we rejected Saxony's).
    if event_type == "ai_proposal_accepted":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"We accepted {source}'s {proposal_type} proposal{_decision_reason_suffix(event)}"

    if event_type == "ai_proposal_rejected":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"We rejected {source}'s {proposal_type} proposal{_decision_reason_suffix(event)}"

    if event_type == "ai_proposal_counter_failed":
        source = event.get("source", "Unknown")
        return f"{source} rejected our counter-offer{_decision_reason_suffix(event)}"

    # NA-5 §8: incoming AI ultimatum resolution (same direction rule as the
    # ai_proposal pair — `source` issued the demand, WE answered it).
    if event_type == "ai_ultimatum_accepted":
        source = event.get("source", "Unknown")
        return f"We yielded to {source}'s ultimatum — their demands conceded"

    if event_type == "ai_ultimatum_rejected":
        source = event.get("source", "Unknown")
        return f"We defied {source}'s ultimatum — their court will not forget"

    if event_type == "ai_ultimatum_void":
        source = event.get("source", "Unknown")
        if event.get("reason") == "gone":
            return f"{source}'s ultimatum died with their court"
        return f"{source}'s ultimatum was overtaken by war — the demand is void"

    if event_type == "auto_downgrade":
        nation_a = event.get("nation_a", "Unknown")
        nation_b = event.get("nation_b", "Unknown")
        from_state = (event.get("from_state") or "treaty").replace("_", " ")
        to_state = (event.get("to_state") or "peace").replace("_", " ")
        return f"Relations auto-downgraded: {nation_a}–{nation_b} ({from_state} → {to_state})"

    if event_type == "coalition_brewing_started":
        threat = event.get("threat_level", 0)
        qualifying = event.get("qualifying_nations", [])
        nations_str = ", ".join(qualifying) if qualifying else "several nations"
        # Stage D review fix [r1]: name a non-France target explicitly.
        brew_target = event.get("target_nation") or "France"
        if brew_target != "France":
            return (f"Coalition brewing against {display_nation(brew_target)} "
                    f"— {nations_str} consulting (their alarm: {threat})")
        return f"Coalition brewing — {nations_str} alarmed (threat: {threat})"

    if event_type == "coalition_brewing_cancelled":
        return "Coalition threat has subsided"

    if event_type == "counter_offer_accepted":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"{source} accepted our counter-offer ({proposal_type}){_decision_reason_suffix(event)}"

    if event_type == "counter_offer_rejected":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"{source} rejected our counter-offer ({proposal_type}){_decision_reason_suffix(event)}"

    if event_type == "diplomatic_discrepancy":
        message = event.get("message", "Talleyrand altered your proposal")
        return message

    if event_type == "diplomatic_downgrade":
        nation_a = event.get("nation_a", "Unknown")
        nation_b = event.get("nation_b", "Unknown")
        from_state = (event.get("from_state") or "treaty").replace("_", " ")
        to_state = (event.get("to_state") or "peace").replace("_", " ")
        return f"Relations downgraded: {nation_a}–{nation_b} ({from_state} → {to_state})"

    if event_type == "diplomatic_mission_cancelled_eliminated":
        target = event.get("target", "Unknown")
        return f"Diplomatic mission to {target} cancelled — nation eliminated"

    if event_type == "diplomatic_mission_started":
        target = event.get("target", "Unknown")
        mission_type = (event.get("mission_type") or "diplomatic mission").replace("_", " ")
        return f"Talleyrand dispatched on {mission_type} to {target}"

    if event_type == "diplomatic_proposal_sent":
        target = event.get("target", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"Proposal sent to {target} ({proposal_type})"

    # PL-27/PL-34: Proposal queue visibility events
    if event_type == "proposal_arrived":
        from backend.display_names import with_indefinite_article
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return (f"An envoy from {source} has arrived with "
                f"{with_indefinite_article(proposal_type)} proposal{_decision_reason_suffix(event)}")

    if event_type == "amends_offered":
        # B-B7 (spec §8.6.1) + B-B4 (spec §8.6.1a grievance variant) —
        # France's repair gesture toward target_nation. `actor_nation` is
        # always France in v0.1, kept on the event for forward-compat with
        # §8.6.1 design intent that allows other actors in later phases.
        actor = event.get("actor_nation", "France")
        target = event.get("target_nation") or event.get("nation", "Unknown")
        gold_spent = int(event.get("gold_spent", 0) or 0)
        dp_spent = int(event.get("dp_spent", 0) or 0)
        variant = str(event.get("amends_variant") or "standard").lower()
        # Spec §8.6.1 / §8.6.1a require deterministic deltas in the payload;
        # reflect them on the one-liner so the public log carries the
        # political price. The grievance variant adds the "for the
        # abandoned alliance" qualifier so the ledger disambiguates at a
        # glance.
        if variant == "grievance":
            return (
                f"{actor} offered amends to {target} for the abandoned alliance "
                f"({gold_spent}g, {dp_spent} DP)"
            )
        return (
            f"{actor} offered amends to {target} "
            f"({gold_spent}g, {dp_spent} DP)"
        )

    if event_type == "call_to_arms_refused_defensive":
        # Spec §8.8 substrate one-liner. Rich notice copy now routes through
        # commitments metadata; this public-log fallback records who refused
        # whom and whether the refusal ended an alliance (§8.8.7a).
        breaker = event.get("breaker", "Unknown")
        victim = event.get("victim", "Unknown")
        if event.get("alliance_terminated"):
            return (
                f"{breaker} refused the defensive call from {victim}, "
                "ending the alliance"
            )
        return f"{breaker} refused the defensive call from {victim}"

    if event_type == "call_to_arms_refused_offensive":
        breaker = event.get("breaker", "Unknown")
        victim = event.get("victim", "Unknown")
        return f"{breaker} refused the offensive call from {victim}"

    if event_type == "call_to_arms_honored_costly":
        honorer = event.get("honorer", "Unknown")
        victim = event.get("victim", "Unknown")
        return f"{honorer} honored a costly defensive call from {victim}"

    if event_type == "oathbreaker_posture_triggered":
        nation = event.get("nation", "Unknown")
        return f"{nation} is marked as an oathbreaker after repeated refusals"

    if event_type == "oathbreaker_posture_cleared":
        nation = event.get("nation", "Unknown")
        return f"{nation}'s oathbreaker posture has cleared"

    if event_type == "war_entry_ledger":
        aggressor = event.get("aggressor", "Unknown")
        target = event.get("target", "Unknown")
        entries = event.get("entries", []) or []
        return (
            f"War-entry ledger recorded for {aggressor} against {target} "
            f"({len(entries)} call path{'' if len(entries) == 1 else 's'})"
        )

    if event_type == "hard_reject_posture_triggered":
        victim = event.get("victim_nation", "Unknown")
        perpetrator = event.get("perpetrator_nation", "France")
        return f"{victim} has shut the chancery to {perpetrator} after repeated betrayals"

    if event_type == "hard_reject_posture_cleared":
        victim = event.get("victim_nation", "Unknown")
        perpetrator = event.get("perpetrator_nation", "France")
        return f"{victim} has reopened deeper diplomacy with {perpetrator}"

    if event_type == "proposal_expired_unseen":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"{source}'s {proposal_type} envoy departed — proposal expired unanswered"

    if event_type == "proposal_dropped_overflow":
        source = event.get("source", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"{source}'s {proposal_type} envoy turned away — too many waiting"

    if event_type == "offer_lapsed":
        nation = event.get("nation", "Unknown")
        proposal_type = (event.get("proposal_type") or "proposal").replace("_", " ")
        return f"{nation}'s {proposal_type} offer lapsed unanswered"

    if event_type == "garrison_placed":
        marshal = event.get("marshal", "Unknown")
        region = event.get("region", "unknown region")
        troops = event.get("troops", 0)
        return f"{marshal} garrisoned {region} ({troops:,} troops)"

    if event_type == "proposal_voided_by_coalition":
        target = event.get("target", "Unknown")
        return f"Envoy to {target} recalled — they joined the coalition"

    if event_type == "relationship_change":
        marshal = event.get("marshal", "Unknown")
        toward = event.get("toward", "Unknown")
        change = event.get("change", 0)
        new_label = event.get("new_label", "")
        sign = "+" if change > 0 else ""
        label_str = f" ({new_label})" if new_label else ""
        return f"{marshal} → {toward}: {sign}{change}{label_str}"

    # PL-14: Ultimatum events
    if event_type == "ultimatum_issued":
        target = event.get("target", "Unknown")
        return f"Ultimatum delivered to {target}"

    if event_type == "ultimatum_accepted":
        target = event.get("target", "Unknown")
        return f"{target} accepted our ultimatum — concessions extracted"

    if event_type == "ultimatum_rejected":
        target = event.get("target", "Unknown")
        return f"{target} rejected our ultimatum — casus belli granted"

    # Peace Deals BPH-A + BPH-D
    if event_type == "peace_ratified":
        proposer = event.get("proposer_nation", "Unknown")
        target = event.get("target_nation", "Unknown")
        transition = event.get("state_transition", "")
        if transition.endswith("_TO_ARMISTICE"):
            term_count = len(event.get("annotated_terms", []))
            suffix = f" ({term_count} term{'s' if term_count != 1 else ''})" if term_count else ""
            return f"Armistice ratified: {proposer} and {target}{suffix}"
        outcome = event.get("war_outcome", "")
        outcome_labels = {
            "french_victory": "French victory",
            "enemy_victory": "enemy victory",
            "stalemate": "stalemate",
            "white_peace": "white peace",
        }
        outcome_label = outcome_labels.get(outcome, "")
        parts = []
        gained = event.get("territory_gained", [])
        if gained:
            parts.append(f"gained {', '.join(gained)}")
        lost = event.get("territory_lost", [])
        if lost:
            parts.append(f"lost {', '.join(lost)}")
        gold_in = event.get("gold_received", 0)
        if gold_in:
            parts.append(f"+{gold_in} gold")
        gold_out = event.get("gold_paid", 0)
        if gold_out:
            parts.append(f"-{gold_out} gold")
        detail = " — " + ", ".join(parts) if parts else ""
        label = f" ({outcome_label})" if outcome_label else ""
        return f"Peace with {target}{label}{detail}"

    return f"Event: {event_type}"
