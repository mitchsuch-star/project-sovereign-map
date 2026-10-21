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
import dataclasses
from typing import Any

from backend.models.intel import FULL, PARTIAL


# Action display names — single source in display_names.py (R7)
from backend.display_names import OBJECTION_DISPLAY as _OBJECTION_DISPLAY
from backend.display_names import DEFIANCE_DISPLAY as _DEFIANCE_DISPLAY
from backend.display_names import ally_entry_block_line
from backend.display_names import plural as _plural  # LV-9 (row EP F2)
from backend.display_names import diplomatic_decision_reason_display
from backend.display_names import display_nation
from backend.display_names import humanize_entity_name
from backend.display_names import with_definite_article
from backend.game_logic.commitments_routing import (
    COMMITMENTS_ROUTES,
    format_commitments_notice,
)
from backend.display_names import marshal_title  # SF5-X3: the ONE style for a marshal in prose

# SF-LB-3's rider (Score Finish Step 7b): "AI-AI treaty: Sweden and Austria
# (Defensive Alliance)" read as a debug line in the chronicle; it is a
# sentence now ("Sweden and Austria sign a Defensive Alliance"). False = the
# old line byte for byte.
THE_COURTS_TREATIES_READ_AS_PROSE = True


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


# FA-S17-16 (slice 17, Phase 4) — the log names what was proposed: one
# envoy, one name. The
# letter-book titles a row from the TERMS the letter carries (PT-D3's landed
# decision — a `friendly_gift` at relation < 0 is rewritten into an
# `open_borders` proposal downstream, and titling the row "Gift of
# Friendship" above a body reading "Proposal: Open Borders Agreement"
# contradicts itself), while the campaign log named the CONTEXT label — the
# court's original intent. Both are defensible alone; together the player
# reads two names for one envoy ("LETTER Hanover: Open Borders Agreement"
# then "We rejected Hanover's gift of friendship proposal", 174 log rows
# across the Phase-3 tree). The log now prefers the terms-derived name the
# player actually answered, and the context label — which the batching
# predicate keys on — is untouched.

# IQ-4 "The Cabinet Is Visible" — the log names the mission: the
# `diplomatic_mission_started`
# one-liner printed the raw type key with its underscores swapped for spaces
# ("Talleyrand dispatched on COURT NATION to PapalStates") — an R7 leak at
# both halves. It now names the mission and the court through the display
# chokepoints.


def mission_reason_phrase(reason: str, regions=None, expiry=None) -> str:
    """How a diplomatic mission ended, in the player's words (IQ-4 §3.1).

    The ONE phrase table: the Strategic Ledger's "Last mission" line, the
    Diplomatic Ledger's Talleyrand tab and the campaign log's
    `diplomatic_mission_ended` one-liner all read it.
    """
    if reason == "ceiling":
        return "relations reached +100"
    if reason == "duration":
        if regions is None:
            return "done"        # the grant has lapsed, or was never counted
        k = int(regions or 0)
        text = f"done — {k} province{'' if k == 1 else 's'} open to us"
        if expiry:
            text += f" until turn {int(expiry)}"
        return text
    if reason == "alliance_broken":
        return "their alliance broke"
    if reason == "recalled":
        return "recalled"
    if reason == "replaced":
        return "replaced by a new mission"
    if reason == "starved":
        return "collapsed for want of DP"
    if reason == "eliminated":
        return "the court no longer exists"
    return str(reason or "ended").replace("_", " ")


def _proposal_label(event: dict) -> str:
    """Player-facing label for an event's proposal_type. Never the raw key.

    FA-S17-16 (Phase 4): when the producer recorded the terms-derived type
    (`proposal_type_offered`), that is the name the player saw on the letter
    and the one this line uses. The `proposal_type` key stays the court's
    original intent, because the collapse predicate keys on it.

    CA8-23 (creative audit, Aug 4 2026): ten call sites in this module each
    hand-rolled `(event.get("proposal_type") or "proposal").replace("_", " ")`,
    so the campaign log announced the played campaign's most consequential
    diplomatic event as *"an armistice losing proposal"* and buried it as
    *"Austria's armistice losing offer lapsed unanswered"*. `display_names`
    has mapped `armistice_losing` -> "Armistice" since PL-14; nobody asked it.
    Exposing a raw internal key to the player is on this project's own
    Don't-Do list.

    `armistice_losing` was not the only leak — the same `.replace()` rendered
    `design_purchase`, `sell_neutrality`, `offer_vassalage`, `broker_peace`,
    `ultimatum_demand`, `friendly_gift` and `opportunistic` as their internal
    tokens too. Routing through the map fixes the whole family at once and
    leaves one place to add the next type.

    Lower-cased because the campaign log writes sentences, not headings:
    "Prussia rebuffs Austria (open borders agreement)". The map owns WHAT a
    proposal is called; this module owns the register it is said in.

    The empty case keeps the old literal so a type-less event still reads as
    a sentence rather than "Unknown Proposal".
    """
    from backend.display_names import proposal_display_name
    # FA-S17-16: prefer the type the letter CARRIED (what the player read and
    # answered) over the court's original intent, when the producer knew it.
    raw = ""
    raw = str(event.get("proposal_type_offered") or "").strip()
    raw = raw or str(event.get("proposal_type") or "").strip()
    if not raw:
        return "proposal"
    return proposal_display_name(raw).lower()


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
    # FA-R5 (slice 14): an escalade against a static garrison. Two of the
    # resolver's three exits — the works HOLDING, and the garrison being
    # destroyed into an OCCUPATION — left no trace on any persistent
    # surface; only the third (fall straight to capture) was covered, by
    # the `region_captured` written downstream. 160 -> 161 flipped
    # CONSCIOUSLY: unlike slice 11's `vassal_broke_free`, there was no
    # inert type to retire in exchange. A producer census over the whole
    # backend found exactly six types with no producer at all
    # (`ally_entry_accepted`, `ally_entry_refused`, `bargain_repudiated`,
    # `counter_bargain_rejected`, `proposal_dropped_overflow`,
    # `proposal_expired_unseen`) — every one of them `diplomacy`, while
    # all seventeen `combat` types have live producers. Retiring a
    # diplomacy half-pair to make room for a combat type would deform a
    # live family AND red a pin anyway, so the count moves instead. That
    # is what the ten `len(CAMPAIGN_LOG_TYPES) == 161` pins are for.
    "garrison_assault",
    "retreat",
    "marshal_broken",
    "marshal_recovered",
    # W6-7 Marshal Fates
    "marshal_captured",
    "last_stand",
    "marshal_released",
    # PC15-1: corps annihilation — the fall was silent before this type
    "marshal_destroyed",
    # VP-M1 "The Fortunes of War" (GE-D1, Sept 25, 2026): a general carried
    # from the field wounded — out WOUND_TURNS turns, the corps standing.
    # A general KILLED rides `marshal_destroyed` with cause
    # "killed_in_action" (one removal seam, one tombstone). 167 -> 168
    # flipped consciously; no inert type was retired in exchange.
    "marshal_wounded",
    # GE-1 (Sept 25, 2026): the campaign's own endings — the Fall, the
    # Verdict of History, a Humbled Peace — each leave ONE chronicle line
    # (`game_end.record_ending`). 165 -> 166 flipped consciously; the
    # census `test_no_silent_drops` requires the producer's type be here.
    "campaign_ending",
    # GE-3 "The Congress of Paris" (Sept 25, 2026): ONE chronicle type for
    # the whole sitting, told apart by its `phase` — summoned, recognized,
    # withdrew, war, warning, subsidy, sweetener, dissolved (congress.py
    # writes every one literally, with the player's `nation`, so the fog
    # filter's player arm passes it). The Imperial Peace itself rides
    # GE-1's `campaign_ending` (cause "imperial_peace"). 166 -> 167 flipped
    # consciously; no inert type was retired in exchange.
    "congress",
    # WIN-D3 "The Road Home": the evacuation corridor a peace grants, and
    # the countdown when a corps dawdles on soil that is no longer its own.
    # (Internment itself rides PC15-1's `marshal_destroyed` with
    # cause="interned" — one removal seam, one tombstone, one ladder.)
    "evacuation_granted",
    "evacuation_lapsing",
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
    # FA-N74 (slice 11): `diplomatic_vassal_rebellion` sat here with a fog
    # arm and a one-liner and NO PRODUCER — nothing ever logged it, because
    # none of `check_vassal_rebellion`'s three exits wrote to `event_log` at
    # all. It is retired for the type that is now written, so the count is
    # unchanged and the ten `len(CAMPAIGN_LOG_TYPES)` pins hold.  (They read
    # 161 since FA-R5; the count "nine" was already stale when this was
    # written — slice 11 added the tenth in its own file.)
    "vassal_broke_free",
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
    # VD-C "The Contingent" (Step 5, October 3, 2026): a satellite's
    # contingent raised, marching home, home (crowned / decimated / plain),
    # lost in the field, or walking out on a break — ONE type, its `beat`
    # names which. 171 -> 172 flipped CONSCIOUSLY: the men a loyal client
    # gives its lord had no persistent surface.
    "vassal_contingent",
    # IQ-7 "The Client's Petition" (September 16, 2026): a loyal client's
    # petition answered — granted, refused, or left to lapse. 164 -> 165
    # flipped CONSCIOUSLY: the one non-rebellion decision the satellite web
    # asks had no persistent surface, and (as at FA-R5) the only producerless
    # types available to retire are all `diplomacy` half-pairs.
    "client_petition_answered",
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
    # IQ-4 "The Cabinet Is Visible": the log recorded a mission's start and
    # never how it ended (ceiling, duration, alliance broken, recalled,
    # starved). Registered unconditionally; `MISSION_LOG_ENDS` gates the
    # producer (`diplomatic_dialogue.record_mission_end`).
    "diplomatic_mission_ended",
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
    # PC-R7 (ii) part 2 — the war's declared articles, declared and settled
    "war_articles_declared",
    "war_articles_settled",
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
    # PC-R3 (S13e part 2): a dictated stream's last payment sends its sureties home
    "surety_returned",
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
    # FA-N52 (slice 17): the laurels PASSING reaches the log (and Le Moniteur)
    # like the crowning always did — the dispatch beat existed, the row did not.
    "glory_crown_lost",
    # ESP riders (Jealousy v3.2 build)
    "fontainebleau_petition",
    "rente_defaulted",
    # Marshal recruitment
    "marshal_commissioned",
    # IQ-1 SW-1 "The Substitute Market": men bought rather than called.
    # A purchase leaves a trace for the same reason FA-R5 gave the
    # garrison assault one — an AI nation putting 30,000 bought men in the
    # line is news, and without a row it happens on no persistent surface.
    "substitutes_purchased",
    # CA9-F13: a standing order voided by a battle the marshal
    # ANSWERED rather than chose. It died silently — Murat's march
    # on Vienna was cancelled by a jealousy attack and the player
    # found out by giving him an order two turns later.
    "order_voided_by_battle",
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
    # DD-1 S8 Step 3 — the verbs (October 12, 2026): a bid laid before a
    # court in play (SFR-D40); a home province asked back from an ally, with
    # its outcome (SFR-D42). 173 -> 175 flipped consciously — neither had a
    # persistent surface and no inert diplomacy type was retired in exchange.
    "allegiance_bid",
    "province_returned",
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
    "continental_system_membership",  # a court joins or leaves the System (the Tilsit clause, SF Step 7)
    "strait_open",              # a crossing verdict flips open (NV-3)
    "strait_shut",              # a crossing verdict flips shut (NV-3)
    "boulogne_camp",            # the descent camp is staged (NV-3)
    "trafalgar",                # a DECISIVE fleet action (NV-2)
    "fleet_action",             # an indecisive fleet action (NV-2)
    "expedition_landed",        # the H4 gamble lands (NV-2)
    "expedition_intercepted",   # caught at sea, corps bled (NV-2)
    "expedition_turned_back",   # the patrols close the passage (NV-2)
    "naval_turnback",           # an AI army halted at a covered strait (NV-2)
    # SR-5r "The Laws" (REFORMS_SPEC §8 "The events" — 168→171 flipped
    # consciously at RF-1): a court's acts of state had no persistent record.
    "law_enacted",              # a law put in force, or restored in arrears (R8)
    "law_repealed",             # a law struck down by its own court (R4)
    "law_lapsed",               # a law the treasury could not pay (R5)
}

# ============================================================================
# CATEGORY MAP — maps event type to display category
# ============================================================================

CATEGORY_MAP = {
    "battle": "combat",
    "bombardment": "combat",
    "garrison_assault": "combat",   # FA-R5 (slice 14)
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
    "glory_crown_lost": "command",
    "fontainebleau_petition": "command",
    "rente_defaulted": "economy",
    "marshal_commissioned": "command",
    "substitutes_purchased": "economy",
    "order_voided_by_battle": "command",
    "marshal_captured": "combat",
    "marshal_destroyed": "combat",
    "marshal_wounded": "combat",
    "campaign_ending": "command",
    # GE-3: the Congress is diplomacy — recognitions, refusals, a London
    # purse, a sweetener at the table, the War of the Congress, the end.
    "congress": "diplomacy",
    "evacuation_granted": "diplomacy",
    # The clock is the treaty's, but the decision it demands is an order to a
    # marshal — so it files with the command traffic the player must answer.
    "evacuation_lapsing": "command",
    "last_stand": "combat",
    "marshal_released": "diplomacy",
    # Diplomacy (Session 8D)
    "diplomatic_treaty_signed": "diplomacy",
    "diplomatic_war_declared": "diplomacy",
    "vassal_broke_free": "diplomacy",
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
    # DD-1 S8 Step 3 — the verbs
    "allegiance_bid": "diplomacy",
    "province_returned": "diplomacy",
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
    "vassal_contingent": "diplomacy",    # VD-C
    "client_petition_answered": "diplomacy",  # IQ-7
    "coalition_member_left": "diplomacy",
    # SR-5r RF-1: the laws — the chest's own sink.
    "law_enacted": "economy",
    "law_repealed": "economy",
    "law_lapsed": "economy",
    # DEF-5 naval (NV-0..NV-3): the Wooden Wall's fourteen types.
    "fleet_laid_down": "economy",
    "fleet_posture": "command",
    "blockade_begins": "economy",
    "blockade_broken": "economy",
    "cs_tier_shift": "economy",
    "continental_system_membership": "diplomacy",
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
    "diplomatic_mission_ended": "diplomacy",
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
    # PC-R7 (ii) part 2
    "war_articles_declared": "diplomacy",
    "war_articles_settled": "diplomacy",
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
    "surety_returned": "diplomacy",
    "settlement_terms_requested": "diplomacy",
    "settlement_terms_request_granted": "diplomacy",
    "settlement_terms_request_refused": "diplomacy",
    "settlement_ally_petition_granted": "diplomacy",
    "settlement_ally_petition_declined": "diplomacy",
    "settlement_bargain_honored": "diplomacy",
}


# IQ-2 (Sept 14, 2026) — D1, the player's losses are the player's events.
# `_is_player_event` read
# `captured_by` and never `captured_from`, so a province WE lost fell to the
# fog arm below, and the fog arm reads the province's CURRENT intel. A
# province that is no longer ours decays (`decay_intel`) the moment no French
# eye stands on it, so the chronicle un-wrote our own losses: measured in the
# played 40-turn campaign, 27 of 27 own-loss rows fell to 5 within two end
# turns (28 -> 3 once France held no province), and Le Moniteur reads the
# same filter. A loss is our own event — fog-safe, it names nothing the map
# does not already show us. All eight production producers stamp
# `captured_from` (census: test_wo_slice4_the_capital_speaks).

# EAS-2 (SR-6c, Oct 2 2026): the campaign log has an importance tier. The
# client renders every row at one size, coloured by category and never by
# weight; this is the BACKEND half — a display-only `tier` on every row
# `GET /campaign_log` returns (lead / notable / routine), read by nothing
# mechanical. Every CAMPAIGN_LOG_TYPES member is classified in exactly one
# of the three sets (a census pin fails for an unclassified new type); two
# types refine on the event's own fields. False = no `tier` key.
THE_LOG_HAS_AN_IMPORTANCE_TIER = True

LOG_TIER_LEAD = frozenset({
    "bankruptcy", "campaign_ending", "coalition_declared",
    "coalition_dissolved", "coalition_dissolved_for_france", "congress",
    "diplomatic_treaty_broken", "diplomatic_treaty_signed",
    "diplomatic_war_declared", "expedition_landed", "last_stand",
    "marshal_captured", "marshal_destroyed", "nation_eliminated",
    "nation_formed", "peace_ratified", "trafalgar", "ultimatum_issued",
    "vassal_broke_free", "vassal_defected", "vassal_liberated",
    "volte_face", "war_declaration",
})

LOG_TIER_NOTABLE = frozenset({
    "agenda_shift", "agenda_violation", "balance_of_europe_shifted",
    "bargain_breached", "bargain_reneged", "battle", "blockade_begins",
    "blockade_broken", "bombardment", "boulogne_camp",
    "call_to_arms_honored_costly", "call_to_arms_refused_defensive",
    "call_to_arms_refused_offensive", "coalition_brewing_started",
    "coalition_member_left", "coercive_demand", "continental_system_membership",
    "crisis_brewing",
    "crisis_passed", "defensive_cascade", "design_bought_off",
    "design_promoted", "desertion", "diplomatic_alliance_cascade",
    "estate_confiscated", "estate_lost", "expedition_intercepted",
    "fleet_action", "fontainebleau_petition", "forced_alliance_imposed",
    "garrison_assault", "glory_crowned", "jealousy_autonomous",
    "jealousy_confrontation", "jealousy_escalation", "jealousy_fired",
    "law_enacted", "marshal_broken", "marshal_commissioned",
    "marshal_released", "marshal_wounded", "offensive_cascade",
    "proposal_arrived", "region_captured", "retreat",
    "rivalry_confrontation", "settlement_summary", "strait_open",
    "strait_shut", "third_party_peace", "ultimatum_accepted",
    "ultimatum_rejected", "vassal_contingent", "vassal_refuses_call",
    "vassal_transferred",
})

LOG_TIER_ROUTINE = frozenset({
    "ai_ai_proposal_refused", "ai_proposal_accepted",
    "ai_proposal_counter_failed", "ai_proposal_rejected",
    "ai_ultimatum_accepted", "ai_ultimatum_rejected", "ai_ultimatum_void",
    "allegiance_auction_opened", "allegiance_auction_resolved",
    "allegiance_bid", "province_returned", "surety_returned",
    "ally_entry_accepted", "ally_entry_refused", "ally_refused_free_join",
    "amends_offered", "auto_downgrade", "bargain_fulfilled",
    "bargain_ratified", "bargain_repudiated", "bargain_triggered",
    "bargain_voided", "british_subsidy", "building_completed",
    "building_damaged", "building_started", "client_petition_answered",
    "coalition_brewing_cancelled", "commitment_paradox_resolved",
    "counter_bargain_accepted", "counter_bargain_rejected",
    "counter_offer_accepted", "counter_offer_rejected", "cs_tier_shift",
    "declaration_backed_out", "defiance", "diplomatic_ai_ai_treaty",
    "diplomatic_discrepancy", "diplomatic_downgrade",
    "diplomatic_mission_cancelled_eliminated", "diplomatic_mission_ended",
    "diplomatic_mission_started", "diplomatic_proposal_sent",
    "dotation_granted", "estate_respected", "evacuation_granted",
    "evacuation_lapsing", "expedition_turned_back", "fleet_laid_down",
    "fleet_posture", "garrison_placed", "glory_crown_lost",
    "guarantee_abandoned", "guarantee_honored", "guarantee_pledged",
    "hard_block_surfaced", "hard_reject_posture_cleared",
    "hard_reject_posture_triggered", "instrument_lapsed",
    "jealousy_resolved", "law_lapsed", "law_repealed", "literal_fidelity",
    "marshal_recovered", "naval_turnback", "oathbreaker_posture_cleared",
    "oathbreaker_posture_triggered", "objection", "offer_lapsed",
    "order_voided_by_battle", "proposal_dropped_overflow",
    "proposal_expired_unseen", "proposal_voided_by_coalition",
    "recruitment", "relationship_change", "rente_defaulted",
    "rente_granted", "rente_revoked", "settlement_ally_petition_declined",
    "settlement_ally_petition_granted", "settlement_bargain_honored",
    "settlement_digest", "settlement_recurring_gold_cancelled",
    "settlement_recurring_gold_completed", "settlement_recurring_gold_paid",
    "settlement_recurring_gold_partial",
    "settlement_terms_request_granted", "settlement_terms_request_refused",
    "settlement_terms_requested", "sponsorship_expired",
    "sponsorship_granted", "sponsorship_reneged", "strategic_order",
    "substitutes_purchased", "vassal_auto_join_war", "war_entry_ledger",
    "war_objective_declared", "war_objective_ticking_started",
    "war_articles_declared", "war_articles_settled",
})

LOG_TIERS = ("lead", "notable", "routine")


def event_tier(event: dict, world=None) -> str:
    """The importance tier of one campaign-log row (EAS-2, display only).

    `battle` and `region_captured` refine: a battle that took the
    province, destroyed or routed a corps, or was decisive LEADS; a
    capital changing hands LEADS (read off the world's region, so no
    producer needs a new key); the rest of each family is notable.
    Unknown types read routine. "" with the lever down.
    """
    if not THE_LOG_HAS_AN_IMPORTANCE_TIER:
        return ""
    etype = str(event.get("type") or "")
    if etype == "battle":
        outcome = str(event.get("outcome") or "")
        if (event.get("region_conquered") or event.get("auto_bombardment_kill")
                or event.get("marshal_destroyed") or event.get("marshal_captured")
                or "decisive" in outcome or outcome == "mutual_destruction"):
            return "lead"
        for side in ("attacker", "defender"):
            block = event.get(side)
            if isinstance(block, dict) and block.get("forced_retreat"):
                return "lead"
        if event.get("forced_retreat") or event.get("capture_choice"):
            return "lead"
        return "notable"
    if etype == "region_captured":
        region = None
        if world is not None:
            region = (getattr(world, "regions", None) or {}).get(str(event.get("region") or ""))
        if event.get("capital") or (region is not None and getattr(region, "is_capital", False)):
            return "lead"
        return "notable"
    if etype in LOG_TIER_LEAD:
        return "lead"
    if etype in LOG_TIER_NOTABLE:
        return "notable"
    return "routine"


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
    # IQ-2 D1: ...and captured_from — the province taken FROM us.
    if (event.get("type") == "region_captured" and event.get("captured_from") == player_nation):
        return True
    # SC-33 recurring settlement payments — the player is a party as payer
    # or recipient (G4F smoke follow-up).
    if event.get("from_nation") == player_nation:
        return True
    if event.get("to_nation") == player_nation:
        return True
    # The Tilsit clause's slice: the Continental System is the player's own
    # instrument, so a court joining or leaving it is always the player's business.
    if (event.get("type") == "continental_system_membership"
            and event.get("lord") == player_nation):
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


# The court-to-court arm: a third party's story the player may see at
# PARTIAL+ on any named party. This is the ENGINE's own definition of "an
# AI-vs-AI beat", and it is a module constant so a consumer can be checked
# AGAINST it rather than restating it. The slice-15 review round found the
# playtest driver's hand-rolled allowlist overlapping this by 5 of 19, with
# `british_subsidy` — served 21 times on a 30-turn board — dropped every
# time, so a reader of the digest concluded the paymaster funded nobody.
COURT_TO_COURT_EVENT_TYPES = (
    "diplomatic_treaty_signed", "diplomatic_war_declared",
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
    # DD-1 S8 Step 3: a court asks its ally for its home province back
    # (`nation` / `target_nation` keys; a player-party event passes above)
    "province_returned",
    "balance_of_europe_shifted",
    "call_to_arms_refused_defensive",
    "call_to_arms_refused_offensive",
    "call_to_arms_honored_costly",
)


# WPS-A's fog rule for a war's purpose — and PC-R7 (ii) part 2's articles,
# declared and settled, which ride it: belligerents and close allies see
# them; the declarations (and their settling) also reach any known court.
_PURPOSE_EVENT_TYPES = ("war_objective_declared", "war_objective_ticking_started",
                        "war_articles_declared", "war_articles_settled")
_PURPOSE_KNOWN_COURT_TYPES = ("war_objective_declared", "war_articles_declared",
                              "war_articles_settled")


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

        # WIN-D3: the corridor beat names corps and the provinces they are
        # marching to, so it is army intelligence wearing a treaty's clothes.
        # Shown only to a signatory. A third party learns of the peace
        # through the ordinary diplomatic channels; it does not learn the
        # order of march. (Recorded limit — WAR_WITHDRAWAL_SPEC §7a.)
        if event_type == "evacuation_granted":
            if player_nation in (event.get("nation_a"), event.get("nation_b")):
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
        if event_type in _PURPOSE_EVENT_TYPES:
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
            if event_type in _PURPOSE_KNOWN_COURT_TYPES:
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

        # FA-R5 (slice 14): a THIRD PARTY's escalade. Both of the player's
        # own directions have already exited above — `_is_player_event`
        # reads `attacker_nation` and `defender_nation`, and the producer
        # stamps both — so this arm only ever sees somebody else's siege.
        # Without it the function's DROP default swallowed them silently,
        # and the ambient board produces one (Austria against the Kingdom
        # of Italy at Milan, turn 10). PARTIAL is enough where `battle`
        # demands FULL: a garrison figure is a coarser fact than a field
        # battle's order of march — a besieged town is visible from the
        # next province, and the row carries no corps dispositions.
        if event_type == "garrison_assault":
            if region:
                intel = world_state.get_region_intel(region)
                if intel.visibility in (FULL, PARTIAL):
                    filtered.append(event)
            continue

        # PC15-1: marshal_destroyed — the player's own falls passed the
        # player-event gate above; an enemy corps destroyed BY the player's
        # army is the player's own battle (victor arm); a third party's fall
        # needs eyes on the field (region PARTIAL+).
        # WIN-D3: a foreign corps overstaying its passage is visible only
        # where we have eyes. Our own passed the player gate above (the
        # event carries `nation`).
        if event_type == "evacuation_lapsing":
            if region:
                intel = world_state.get_region_intel(region)
                if intel.visibility in (FULL, PARTIAL):
                    filtered.append(event)
            continue

        if event_type == "marshal_destroyed":
            if event.get("victor") == player_nation:
                filtered.append(event)
                continue
            if region:
                intel = world_state.get_region_intel(region)
                if intel.visibility in (FULL, PARTIAL):
                    filtered.append(event)
            continue

        # Retreat / marshal_broken / marshal_recovered / marshal_wounded
        # (VP-M1): player marshal OR PARTIAL+
        if event_type in ("retreat", "marshal_broken", "marshal_recovered",
                          "marshal_wounded"):
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
                          "design_promoted", "volte_face",
                          # SR-5r RF-1: a court's laws are court knowledge
                          # across Europe (REFORMS_SPEC §8: "diplomacy
                          # has no fog").
                          "law_enacted", "law_repealed", "law_lapsed"):
            filtered.append(event)
            continue

        # Economy events (enemy): region PARTIAL+
        if event_type in ("recruitment", "building_started", "building_completed",
                          "building_damaged", "desertion",
                          # ES-7: an enemy court's endowments are visible only
                          # where our intel reaches (region PARTIAL+)
                          "dotation_granted", "estate_lost",
                          # W6-8: same rule for conquered-estate resolutions
                          "estate_confiscated", "estate_respected",
                          # IQ-1 IQ1-3D rider 2: a court BUYING substitutes is
                          # an economy event under exactly this rule, and it was
                          # absent from the tuple — so every non-player purchase
                          # fell through the loop and was dropped, while twelve
                          # `len(CAMPAIGN_LOG_TYPES) == 163` pin comments
                          # asserted the row existed "because an AI nation
                          # buying 30,000 men had no persistent surface".
                          #
                          # ⚠ The decision fleet reported this as "the filter
                          # has NO economy branch and no default arm". Half
                          # right, and the correction is the smaller fix: the
                          # branch has been here since Session 8 — the TYPE was
                          # missing from it. The producer also emitted no
                          # `region` key, so the "region PARTIAL+" rule below
                          # had nothing to read; it does now.
                          "substitutes_purchased"):
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
        if event_type in COURT_TO_COURT_EVENT_TYPES:
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

        # A satellite breaking free: shown when it was OUR satellite, and
        # otherwise only where we can see the court (GR5 — the web has other
        # lords since VS-5, so "player vassal always shown" cannot stand as a
        # blanket rule).
        if event_type == "vassal_broke_free":
            if str(event.get("lord") or "") == player_nation:
                filtered.append(event)
                continue
            # Review round: the first cut read the VASSAL's visibility alone,
            # while every sibling vassal arm in this function reads BOTH
            # courts (`for nation in (vassal, overlord)`). A satellite
            # breaking from a lord we watch closely is news we would have,
            # even if the satellite itself is dark.
            from backend.game_logic.diplomatic_ledger import _get_nation_visibility
            if any(_get_nation_visibility(str(nation or ""), world_state)
                   in (FULL, PARTIAL)
                   for nation in (event.get("vassal"), event.get("lord"))):
                filtered.append(event)
            continue

        # Nation eliminated: public knowledge
        if event_type == "nation_eliminated":
            filtered.append(event)
            continue

        # Vassal auto-join / VS-4 refusal / VS-5 transfer / VS-6 defection /
        # IQ-7 petition answered: show if player involved or PARTIAL+
        if event_type in ("vassal_auto_join_war", "vassal_refuses_call",
                          "vassal_transferred", "vassal_defected",
                          "client_petition_answered", "vassal_contingent"):
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
                          "diplomatic_mission_ended",
                          "diplomatic_discrepancy", "counter_offer_accepted",
                          "counter_offer_rejected"):
            filtered.append(event)
            continue

        # AI proposal responses to player: always show (player is target)
        # NA-5: the ultimatum pair is the same shape — the player answered.
        # Slice 17 review round (L2-3, found while re-keying the Gazette): the
        # player's OWN ultimatum answer (`ultimatum_accepted` /
        # `ultimatum_rejected`, written with a `target` and no nation key)
        # matched no arm and fell through to the drop — his own act was
        # invisible on the log screen and unreachable to Le Moniteur.
        if event_type in ("ai_proposal_accepted", "ai_proposal_rejected",
                          "ai_proposal_counter_failed",
                          "ai_ultimatum_accepted", "ai_ultimatum_rejected",
                          "ai_ultimatum_void",
                          "ultimatum_accepted", "ultimatum_rejected"):
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
                          "glory_crowned", "glory_crown_lost",
                          "fontainebleau_petition",
                          "rente_defaulted", "marshal_commissioned",
                          "order_voided_by_battle"):
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
    """'A', 'A and B', 'A, B and C' — chancery list register.

    PR-2 (playtest re-score, September 12 2026): the list is the single
    chokepoint every court-list one-liner passes through, and it rendered
    internal tags — measured, "Portugal, Saxony and PapalStates rebuff
    Prussia".
    """
    from backend.display_names import display_nation
    names = [display_nation(str(n)) for n in names]
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

    PR-2b (review round, September 12 2026) — this paragraph used to say
    the opposite and was WRONG about the mechanism, so it is restated with
    the reading that was verified: names are humanised HERE, on both sides
    of the verb. `formations.apply_formation_names_to_history` searches for
    `display_nation(tag)` — the HUMANISED form — so composing with it is
    exactly what the NA-6 dead-name repair keys on, not something that
    escapes it (measured: pre-fix "KingdomOfItaly rebuffs ..." was repaired
    client-side to "Italy"; post-fix "Kingdom of Italy rebuffs ..." is
    repaired backend-side to the same thing). The client's
    `Utils.humanize_nation_keys_in_text` simply no-ops on an already-clean
    line. What the earlier wording got right is the hazard it names — a
    dead name baked past every repair — and that hazard belongs to a
    producer that bypasses `apply_formation_names_to_history` entirely,
    which is `gazette.py`'s call to `format_event_oneliner`.
    """
    from backend.display_names import display_nation as _named
    pairs = event.get("collapsed_pairs") or []
    proposers = [_named(n) for n in _unique_in_order(p.get("proposer") for p in pairs)]
    refusers = [_named(n) for n in _unique_in_order(p.get("refused_by") for p in pairs)]

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


# ════════════════════════════════════════════════════════════════════════
# GE-3 "The Congress of Paris" — the chronicle's words for the sitting.
# Shared with the morning dispatch and Le Moniteur (one sentence per fact).
# ════════════════════════════════════════════════════════════════════════

def and_join(names: list) -> str:
    """"Austria", "Austria and Russia", "Austria, Prussia and Russia"."""
    names = [str(n) for n in names if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def _paren(text: str) -> str:
    """The parenthetical a hold condition carries — "(48 of 50)",
    "(we declared on Austria)" — without its brackets, or ""."""
    if "(" not in text or ")" not in text:
        return ""
    return text[text.find("(") + 1:text.rfind(")")].strip()


def congress_dissolve_reason(key: str, text: str) -> str:
    """Why the Congress dissolved, as a FAILURE.

    The dissolution records the hold condition that failed in the words the
    TABLE uses for it — which state the CONDITION ("Paris held", "the
    Emperor free", "no war declared since the summons"), not its breach. A
    reader shown "The Congress dissolves — Paris held." is told the opposite
    of what happened, so the chronicle, the dispatch and the paper all turn
    the condition into what broke through this one function, keyed on the
    condition's `key` (congress.hold_conditions)."""
    key = str(key or "")
    text = str(text or "")
    # A condition may carry its cause after an em dash ("… (44 of 50) —
    # Hanover's war reopened what it ceded (Kalenberg)"): the parenthetical
    # is read from the condition, the cause is kept whole.
    head, _, cause = text.partition(" — ")
    inside = _paren(head)
    if key == "titled":
        return ("the titled provinces fell short"
                + (f" ({inside})" if inside else "")
                + (f" — {cause}" if cause else ""))
    if key == "capital":
        capital = text[:-len(" held")] if text.endswith(" held") else "the capital"
        return f"{capital or 'the capital'} was lost"
    if key == "emperor":
        return "the Emperor was taken"
    if key == "satellites":
        # The hold's own clause already says how each was lost ("Saxony rose
        # in rebellion" / "Saxony defected to Britain").
        return inside or "a satellite was lost"
    if key == "lost":
        return "a titled province fell" + (f" ({inside})" if inside else "")
    if key == "declared":
        return "the Emperor drew the sword" + (f" ({inside})" if inside else "")
    if key == "alarm":
        return "Europe's alarm rose too high" + (f" ({inside})" if inside else "")
    return text or "the hold broke"


def coalition_phrase(name: str) -> str:
    """"Third Coalition" / "The Fourth Austrian Coalition" as the object of
    a sentence — "joins the Third Coalition"."""
    name = str(name or "").strip()
    if not name:
        return ""
    if name.lower().startswith("the "):
        return "the " + name[4:]
    return "the " + name


def _congress_court(event: dict, key: str = "court") -> str:
    court = str(event.get(key) or "")
    return display_nation(court) if court else "A great power"


def _format_congress_event(event: dict) -> str:
    """One line per `phase` of the GE-3 `congress` event — never the raw
    `message`, which the producer writes in the table's metonyms."""
    phase = str(event.get("phase") or "")
    if phase == "summoned":
        number = int(event.get("number") or 1)
        head = ("The Emperor summons the powers to Paris"
                + (" again" if number > 1 else ""))
        ends = event.get("ends_turn")
        if ends is not None:
            return f"{head} — the Congress sits until turn {int(ends)}."
        return f"{head}."
    if phase == "recognized":
        court = _congress_court(event)
        if str(event.get("stance") or "") == "SHUT OUT":
            return (f"{court} is shut out of the Congress of Paris — the "
                    f"ports of the Continent are closed to her.")
        return f"{court} signs at the Congress of Paris."
    if phase == "withdrew":
        court = _congress_court(event)
        reason = str(event.get("reason") or "")
        if reason.startswith("it withdrew: "):
            reason = reason[len("it withdrew: "):]
        if str(event.get("was") or "") == "SHUT OUT":
            return (f"{court} is no longer shut out of the Congress of Paris"
                    + (f" — {reason}" if reason else "") + ".")
        return (f"{court} withdraws its signature from the Congress of Paris"
                + (f" — {reason}" if reason else "") + ".")
    if phase == "war":
        court = _congress_court(event)
        coalition = str(event.get("coalition") or "")
        if coalition:
            return (f"{court} answers the Congress with cannon, and joins "
                    f"{coalition_phrase(coalition)}.")
        return f"{court} answers the Congress with cannon."
    if phase == "warning":
        court = _congress_court(event)
        return (f"{court} warns the Congress: one more turn of refusal, and "
                f"it answers with cannon.")
    if phase == "contested":
        # RS-2: a ceder's war while the Congress sits contests its cessions
        # — counted still; the break waits on the war.
        court = _congress_court(event)
        regions = [str(r) for r in (event.get("regions") or []) if r]
        named = (f" ({', '.join(regions[:3])}{' …' if len(regions) > 3 else ''})"
                 if regions else "")
        return (f"{court}'s war contests what it ceded{named} — counted while "
                f"the Congress sits; a peace re-signs it, a dissolution "
                f"reopens it.")
    if phase == "subsidy":
        payer = _congress_court(event, "payer")
        court = _congress_court(event)
        amount = int(event.get("amount") or 0)
        return f"{payer} pays {court} {amount:,}g a turn to refuse the Congress."
    if phase == "sweetener":
        court = _congress_court(event)
        amount = int(event.get("amount") or 0)
        if str(event.get("stance") or "") == "RECOGNIZES":
            return (f"{amount:,}g laid before {court} at the Congress — "
                    f"{court} now recognizes the order.")
        return f"{amount:,}g laid before {court} at the Congress."
    if phase == "dissolved":
        key = str(event.get("key") or "")
        reason = congress_dissolve_reason(key, str(event.get("reason") or ""))
        line = f"The Congress of Paris dissolves — {reason}."
        refusers = [display_nation(r) for r in (event.get("refusers") or []) if r]
        if refusers and key != "unsigned":
            # A broken hold ends the sitting before its answer: the courts
            # had not signed; they were not asked to the end.
            line += f" {and_join(refusers)} had not signed."
        return line
    return "A dispatch from the Congress of Paris."


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


def _holdings_left_clause(event: dict) -> str:
    """IQ-2 D2: what a loss of our own soil left us, when it left us almost
    nothing. `WorldState.log_event` stamps `holdings_left` (read AFTER the
    controller change) and `holdings_realm` (the formed display name) on a
    province taken from the player on a sandbox world; an event without the
    key — every pre-IQ-2 row, every other court's loss — renders
    byte-identically. Speaks only at the collapse ceiling: 0 and 1."""
    if "holdings_left" not in event:
        return ""
    try:
        left = int(event.get("holdings_left"))
    except (TypeError, ValueError):
        return ""
    realm = (event.get("holdings_realm")
             or display_nation(event.get("captured_from") or ""))
    if left == 0:
        return f" — {realm} holds no province"
    if left == 1:
        return f" — {realm} holds a single province"
    return ""


def _possessive_court(tag) -> str:
    """SRX-22: a court's name in the possessive — "Saxony's", "the Ottoman
    Empire's", "the Papal States'" (a plural name takes the bare
    apostrophe)."""
    name = with_definite_article(display_nation(str(tag or "Unknown")))
    return f"{name}'" if name.endswith("s") else f"{name}'s"


# CODE-2b (October 2026): what the stages of `format_event_oneliner`
# share. Built once at the driver's head, never on the wire. The parameters
# are init fields; every other field is set by the stage that first assigns
# it — `slots` with no default, so a read before any assignment raises as
# the local it replaced did.
_NEXT_STAGE = object()


@dataclasses.dataclass(slots=True, repr=False, eq=False)
class OnelinerContext:
    event: Any
    player_nation: Any
    world: Any
    event_type: Any = dataclasses.field(init=False)


def format_event_oneliner(event: dict, player_nation: str = "", world=None) -> str:
    """
    Produce a human-readable one-liner for a campaign log event.

    Uses .get() with safe defaults throughout — missing fields produce
    graceful degradation rather than crashes.  Nation tags are appended
    to marshal names so the player can identify friend/foe at a glance.

    Args:
        event: A single event dict from the event log
        world: SF5-X3 / NPC-12 (Step 7 slice 7) — when given, a marshal
            named by a fate line ("CAPTURED", "WOUNDED", "KILLED", ...)
            is styled by his court's own rank through
            `display_names.marshal_title`; without it he is still
            humanised ("Marshal Archduke Charles", never the key).

    Returns:
        Human-readable one-liner string

    CODE-2b (October 2026): a driver of named stages behind one
    `OnelinerContext`. A stage returns `_NEXT_STAGE` to continue or the
    result to stop; nothing on the context reaches the wire.

     1. `_oneliner_head` — The type read; a commitments notice goes to its own
        formatter; a war that shatters a treaty names it.
     2. `_oneliner_the_field` — Battles, bombardments, escalades, retreats, the
        broken and the recovered, a province captured.
     3. `_oneliner_purse_and_court` — Levies, works, bankruptcy and desertion;
        jealousy and glory; petitions, rentes, commissions, substitutes; voided
        orders, agendas, new nations; dotations and estates.
     4. `_oneliner_orders_and_fates` — Objections, the campaign's end, the
        congress, literal fidelity; a marshal captured, evacuated, wounded,
        destroyed, standing last or released; standing orders and defiance.
     5. `_oneliner_diplomacy` — Treaties, war aims, settlements, the ally's
        entry, AI-AI treaties and the D5 counter-instruments, crises and
        designs (Session 8D).
     6. `_oneliner_laws` — A law enacted, repealed or lapsed (SR-5r).
     7. `_oneliner_the_sea` — Fleets, blockades, the Continental System, the
        straits, the Descent and the expeditions (DEF-5); the flip in play.
     8. `_oneliner_allegiance` — The allegiance bid, a province returned, the
        auction resolved (DD-1).
     9. `_oneliner_cascades_and_coalitions` — A war declared, the cascades, a
        coalition declared or dissolved.
    10. `_oneliner_the_fallen_and_the_clients` — A nation eliminated; vassals
        joining, refusing, transferred, defecting; the client's petition; a
        member leaving the coalition.
    11. `_oneliner_proposals_and_ultimatums` — AI proposals and ultimatums, the
        brewing coalition, counter-offers, missions, the proposal queue,
        garrisons, relationships, the peace ratified (R8, PL-14, PL-27, BPH).
    12. `_oneliner_unknown` — The fall-through: an unknown type is named, never
        dropped.
    """
    ctx = OnelinerContext(
        event=event,
        player_nation=player_nation,
        world=world,
    )
    for stage in (
            _oneliner_head,
            _oneliner_the_field,
            _oneliner_purse_and_court,
            _oneliner_orders_and_fates,
            _oneliner_diplomacy,
            _oneliner_laws,
            _oneliner_the_sea,
            _oneliner_allegiance,
            _oneliner_cascades_and_coalitions,
            _oneliner_the_fallen_and_the_clients,
            _oneliner_proposals_and_ultimatums,
    ):
        result = stage(ctx)
        if result is not _NEXT_STAGE:
            return result
    return _oneliner_unknown(ctx)


def _oneliner_head(ctx: OnelinerContext):
    """Stage 1 of `format_event_oneliner`: The type read; a commitments notice
    goes to its own formatter; a war that shatters a treaty names it."""
    ctx.event_type = ctx.event.get("type", "")
    if ctx.event_type in COMMITMENTS_ROUTES and ctx.event_type != "witness_strike_recorded":
        return format_commitments_notice(ctx.event_type, ctx.event)

    if ctx.event_type in ("diplomatic_war_declared", "war_declaration") and ctx.event.get("breached_treaty"):
        aggressor = ctx.event.get("aggressor") or ctx.event.get("nation", "Unknown")
        target = ctx.event.get("target", "Unknown")
        return f"War declared: {aggressor} -> {target} (shattering {ctx.event.get('breached_treaty')})"

    # NOTE (Aug 2026 health-check audit): every event type in
    # COMMITMENTS_ROUTES (except witness_strike_recorded) is formatted by the
    # early format_commitments_notice() return above — per-type arms for
    # routed types below that point are unreachable and were removed
    # (diplomatic_treaty_broken, commitment_paradox_resolved, the five
    # bargain_* route types, amends_offered, the three call_to_arms_* types,
    # both hard_reject_posture_* types). Pinned by
    # tests/test_health_check_audit_2026_08_14.py.
    return _NEXT_STAGE


def _oneliner_the_field(ctx: OnelinerContext):
    """Stage 2 of `format_event_oneliner`: Battles, bombardments, escalades,
    retreats, the broken and the recovered, a province captured."""
    if ctx.event_type == "battle":
        # Humanized at binding, not only at _name_tag: the outcome clause
        # ("ArchdukeCharles tactical victory") interpolates these directly and
        # leaked the raw key past the tag chokepoint (creative audit July 19
        # 2026). _name_tag is idempotent on an already-spaced name.
        attacker = humanize_entity_name(ctx.event.get("attacker", "Unknown"))
        atk_nation = ctx.event.get("attacker_nation", "")
        defender = humanize_entity_name(ctx.event.get("defender", "Unknown"))
        def_nation = ctx.event.get("defender_nation", "")
        location = ctx.event.get("location", "unknown location")
        outcome = ctx.event.get("outcome", "")
        atk_cas = ctx.event.get("attacker_casualties", 0)
        def_cas = ctx.event.get("defender_casualties", 0)
        # IQ-5 review (F): a LONE side the rubble rule (or the overkill cap)
        # destroyed lost its whole corps — "Ney 25" for a 60-man corps that
        # went to 0 was the raw figure, not the loss. The executor stamps a
        # display-only `*_applied_casualties` on exactly that side (never an
        # army side, never with BOTH_SIDES_NAME_THEIR_SCOPE down); prefer
        # it. The mechanical `*_casualties` above is untouched (R2).
        _atk_applied = ctx.event.get("attacker_applied_casualties")
        if _atk_applied is not None:
            atk_cas = _atk_applied
        _def_applied = ctx.event.get("defender_applied_casualties")
        if _def_applied is not None:
            def_cas = _def_applied
        # PT-D6: an army cannot lose more men than it had. Casualties are
        # computed uncapped and `take_casualties` clamps the strength
        # rather than the number, so an annihilation printed the overkill
        # — "Mack 15,815" against 15,437 men — while Berthier's report,
        # which derives from the surviving strength, printed 15,437.
        # Clamp the RENDER; the mechanical figure is untouched by design
        # (it feeds exhaustion, the out-bled predicate and the score).
        #
        # IQ-5 R4 (PR-X2): bounded by the FIELD, not the lead. A reinforced
        # side's `*_casualties` is the whole army's loss while
        # `*_strength_before` is the lead corps alone — so the clamp shrank
        # a 12,866-man loss to "500" (the lead's stub). The executor's
        # coordinated branch stamps `*_field_before` (every participant's
        # strength at resolve); read it first. Absent — a solo battle, the
        # IQ-5 lever down, an old save — and the lead's figure stands.
        _atk_before = ctx.event.get("attacker_field_before")
        if _atk_before is None:
            _atk_before = ctx.event.get("attacker_strength_before")
        _def_before = ctx.event.get("defender_field_before")
        if _def_before is None:
            _def_before = ctx.event.get("defender_strength_before")
        if _atk_before is not None:
            atk_cas = min(int(atk_cas), int(_atk_before))
        if _def_before is not None:
            def_cas = min(int(def_cas), int(_def_before))
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
        battle_name = ctx.event.get("battle_name", "")
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
        deleg_phrase = ctx.event.get("delegation_phrase")
        if deleg_phrase:
            line += f' — on your word: "{deleg_phrase}"'
        # W6-6: the enemy commander's one-line register rides as a flavor
        # suffix (already humanized + quoted at composition).
        enemy_voice = ctx.event.get("enemy_voice")
        if enemy_voice:
            line += f" — {enemy_voice}"
        return line

    if ctx.event_type == "bombardment":
        attacker = ctx.event.get("attacker", "Unknown")
        atk_nation = ctx.event.get("attacker_nation", "")
        location = (ctx.event.get("defender_location")
                    or ctx.event.get("attacker_location")
                    or "unknown location")
        defender_casualties = ctx.event.get("defender_casualties", 0)
        return (f"{_name_tag(attacker, atk_nation)} bombarded {location} — "
                f"{defender_casualties:,} casualties")

    # FA-R5 (slice 14): the escalade. Both outcomes render from the SAME
    # structured fields the producer stamps and the client's slice-11 arm
    # reads, so the log and the enemy-phase dialog cannot tell different
    # stories about one assault.
    if ctx.event_type == "garrison_assault":
        marshal = ctx.event.get("marshal", "Unknown")
        atk_nation = ctx.event.get("attacker_nation", "")
        region = ctx.event.get("region", "unknown location")
        gar_lost = int(ctx.event.get("garrison_losses", 0) or 0)
        remaining = int(ctx.event.get("garrison_remaining", 0) or 0)
        atk_lost = int(ctx.event.get("attacker_losses", 0) or 0)
        tag = _name_tag(marshal, atk_nation)
        if ctx.event.get("held"):
            return (f"{tag} assaulted the {region} garrison — {gar_lost:,} "
                    f"lost, {remaining:,} still under arms "
                    f"({humanize_entity_name(marshal)} loses {atk_lost:,})")
        return (f"{tag} stormed the {region} garrison — it is destroyed "
                f"({humanize_entity_name(marshal)} loses {atk_lost:,})")

    if ctx.event_type == "retreat":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        from_loc = ctx.event.get("from", "unknown")
        to_loc = ctx.event.get("to", "")
        tag = _name_tag(marshal, nation)
        if to_loc:
            return f"{tag} retreated from {from_loc} to {to_loc}"
        return f"{tag} retreated from {from_loc}"

    if ctx.event_type == "marshal_broken":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        location = ctx.event.get("location", "unknown location")
        return f"{_name_tag(marshal, nation)} was broken at {location}"

    if ctx.event_type == "marshal_recovered":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        location = ctx.event.get("location", "")
        tag = _name_tag(marshal, nation)
        if location:
            return f"{tag} recovered at {location}"
        return f"{tag} recovered"

    if ctx.event_type == "region_captured":
        captured_by = ctx.event.get("captured_by", "Unknown")
        region = ctx.event.get("region", "unknown region")
        method = ctx.event.get("method", "")
        if method:
            return (f"{region} captured by {captured_by} ({method})"
                    + _holdings_left_clause(ctx.event))
        return f"{region} captured by {captured_by}" + _holdings_left_clause(ctx.event)
    return _NEXT_STAGE


def _oneliner_purse_and_court(ctx: OnelinerContext):
    """Stage 3 of `format_event_oneliner`: Levies, works, bankruptcy and
    desertion; jealousy and glory; petitions, rentes, commissions, substitutes;
    voided orders, agendas, new nations; dotations and estates."""
    if ctx.event_type == "recruitment":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        amount = ctx.event.get("amount", 0)
        recruit_type = ctx.event.get("recruit_type", "infantry")
        return f"{_name_tag(marshal, nation)} recruited {amount:,} {recruit_type}"

    if ctx.event_type == "building_started":
        building = (ctx.event.get("building") or "building").replace("_", " ").title()
        region = ctx.event.get("region", "unknown region")
        return f"Construction started: {building} in {region}"

    if ctx.event_type == "building_completed":
        building = (ctx.event.get("building") or "building").replace("_", " ").title()
        region = ctx.event.get("region", "unknown region")
        owner = str(ctx.event.get("nation") or "")
        if ctx.player_nation and owner and owner != ctx.player_nation:
            # AAR-16: a foreign court's work names its owner in the log
            # too; the player's own row is byte-identical.
            article = "" if building.endswith("s") else "a "
            return (f"{display_nation(owner)} completes {article}"
                    f"{building.lower()} in {region}")
        return f"Construction complete: {building} in {region}"

    if ctx.event_type == "building_damaged":
        building = (ctx.event.get("building") or "building").replace("_", " ").title()
        region = ctx.event.get("region", "unknown region")
        return f"Building damaged: {building} in {region}"

    if ctx.event_type == "bankruptcy":
        nation = ctx.event.get("nation", "Unknown")
        return f"{nation} treasury bankrupt — desertion imminent"

    if ctx.event_type == "desertion":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        amount = ctx.event.get("amount", 0)
        return f"Desertion: {_name_tag(marshal, nation)} lost {amount:,} troops"

    if ctx.event_type == "jealousy_fired":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        # CA8 sweep 4: `marshal` reaches the player through `_name_tag`
        # (which humanises the camelCase key) and `target` — a marshal name
        # in the SAME sentence — did not: "envious of ArchdukeCharles's
        # victories". Unreachable for the player today (every French roster
        # and bench name is single-token, and the fog filter shows him only
        # his own nation's jealousy rows), so this is symmetry, not urgency.
        target = humanize_entity_name(ctx.event.get("target", "a rival"))
        personality = ctx.event.get("personality", "")
        # CA8-8: this channel composes its own sentence and had the same
        # three-string monoculture as the dispatch. A recurrence reads
        # differently from a first quarrel; `fires` is absent on pre-CA8-8
        # saves, which falls through to the first-time wording.
        if int(ctx.event.get("fires", 1) or 1) >= 2:
            return (f"{_name_tag(marshal, nation)} takes up his grievance "
                    f"against {target} again")
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

    if ctx.event_type == "jealousy_resolved":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        if ctx.event.get("by_action"):
            return (f"{_name_tag(marshal, nation)}'s grievance is settled — "
                    f"he fights with renewed vigor")
        return f"{_name_tag(marshal, nation)}'s resentment cools with time"

    if ctx.event_type == "jealousy_escalation":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        target = humanize_entity_name(ctx.event.get("target", "a rival"))
        # CA8-8: the payload carries `level` and this formatter
        # ignored it, so a tier-1 escalation the dispatch describes as "a
        # matter of concern" was logged as "entrenched" — the same event
        # contradicting itself across two surfaces on the same turn.
        # CA8 sweep 4 corrects this note: `level` has been on the payload
        # since the producer was written, so the default below is DEFENSIVE,
        # not a compatibility shim. `fires` and `mutual` ARE new keys with
        # live fallbacks; `level` is not one of them.
        # 2 / 3 are jealousy.ESCALATION_PERMANENT_LEVEL and
        # ESCALATION_MUTUAL_LEVEL — inlined rather than imported, because
        # this is a display module and jealousy.py imports the log's own
        # helpers (a cycle for two integers is a poor trade).
        level = int(ctx.event.get("level", 2) or 2)
        if level <= 1:
            return (f"The rivalry between {_name_tag(marshal, nation)} and "
                    f"{target} is now a matter of concern among the staff")
        # CA8-8 review fix: the level advances to 3 whether or not the
        # tier-3 reciprocity actually applied — the producer skips it when
        # the target is not STANDING (e.g. mid-rout recovery) — so this arm
        # asserted a mutual feud against a marshal with no grievance at all.
        # `mutual` is absent on pre-fix saves, which falls through to the
        # entrenched wording rather than to the stronger claim.
        if level >= 3 and ctx.event.get("mutual"):
            return (f"The feud between {_name_tag(marshal, nation)} and "
                    f"{target} is mutual — each schemes against the other")
        return (f"The rivalry between {_name_tag(marshal, nation)} and "
                f"{target} has become entrenched")

    if ctx.event_type == "jealousy_autonomous":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        target = humanize_entity_name(ctx.event.get("target", "the enemy"))
        return (f"{_name_tag(marshal, nation)} attacked {target} on his own "
                f"initiative, hungry for glory")

    if ctx.event_type == "jealousy_confrontation":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        choice = ctx.event.get("choice", "acknowledge")
        # Q2(a) (CA9 row 3): the `command` arm needs its own row, or a
        # player who gave a marshal an army reads that he "was heard".
        choice_str = {"promise": "was promised glory",
                      "rebuke": "was rebuked",
                      "command": "was given a command",
                      "acknowledge": "was heard"}.get(choice, "was heard")
        return f"{_name_tag(marshal, nation)} aired his grievance and {choice_str}"

    if ctx.event_type == "rivalry_confrontation":
        marshal = ctx.event.get("marshal", "Unknown")
        other = ctx.event.get("other", "a rival")
        nation = ctx.event.get("nation", "")
        return (f"Harsh words between {_name_tag(marshal, nation)} and "
                f"{other} — the Emperor intervened")

    if ctx.event_type == "glory_crowned":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        return (f"{_name_tag(marshal, nation)} stands crowned with glory — "
                f"the army's most celebrated commander")

    if ctx.event_type == "glory_crown_lost":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        # SR-4c (AAR-D3): the row carries where the laurels went; a pre-SR-4c
        # row (no `why`) keeps its old sentence byte for byte.
        why = ctx.event.get("why")
        successor = ctx.event.get("successor") or ""
        if why == "passed" and successor:
            return (f"{_name_tag(marshal, nation)} is no longer the army's most "
                    f"celebrated commander — the laurels have passed to "
                    f"{_name_tag(successor, nation)}")
        if why == "level" and successor:
            return (f"{_name_tag(marshal, nation)} no longer wears the laurels "
                    f"alone — {successor} stand level")
        if why == "faded":
            return (f"{_name_tag(marshal, nation)}'s laurels have faded — no "
                    f"commander stands above the rest")
        return (f"{_name_tag(marshal, nation)} is no longer the army's most "
                f"celebrated commander — the laurels have passed")

    if ctx.event_type == "fontainebleau_petition":
        marshals = ctx.event.get("marshals", []) or []
        roll = ", ".join(marshals) if marshals else "The marshals"
        choice = ctx.event.get("choice", "")
        if choice == "concede":
            return f"The marshals' petition was answered with rentes: {roll}"
        if choice == "refuse":
            return f"The marshals' petition was refused: {roll}"
        if choice == "promise":
            return f"The marshals were promised the next conquest: {roll}"
        return f"The marshals petitioned the Emperor: {roll}"

    if ctx.event_type == "rente_defaulted":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        face = int(ctx.event.get("face", 0))
        return (f"The treasury defaulted on {_name_tag(marshal, nation)}'s "
                f"rente of {face}g/turn")

    if ctx.event_type == "marshal_commissioned":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        location = ctx.event.get("location", "the capital")
        return (f"{_name_tag(marshal, nation)} commissioned to the "
                f"marshalate — raises his corps at {location}")

    if ctx.event_type == "substitutes_purchased":
        # IQ-1 SW-1. Names the price, because the price IS the mechanic —
        # a substitute costs four times the drafted man at a full class and
        # sixteen times at an empty one.
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        men = int(ctx.event.get("men", 0))
        gold = int(ctx.event.get("gold", 0))
        return (f"{_name_tag(marshal, nation)} takes {men:,} substitutes "
                f"into the line — {gold:,} gold, and not a man off the rolls")

    if ctx.event_type == "order_voided_by_battle":
        # CA9-F13: the standing order the marshal lost by answering a
        # battle he did not choose. Murat's march on Vienna went this way
        # in the played campaign and nothing said so.
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        region = ctx.event.get("region", "the field")
        verb = str(ctx.event.get("order", "") or "march").replace("_", " ").lower()
        target = humanize_entity_name(str(ctx.event.get("order_target", "") or ""))
        tail = f" to {verb} {target}".rstrip() if target else ""
        return (f"{_name_tag(marshal, nation)} marched to the guns at "
                f"{region} — his standing order{tail} is void")

    if ctx.event_type == "agenda_shift":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        focus = ctx.event.get("focus", "new ambitions")
        return f"The court of {nation} takes up a new design: {focus}"

    if ctx.event_type == "agenda_violation":
        violator = display_nation(ctx.event.get("violator", "Unknown"))
        holder = display_nation(ctx.event.get("guard_holder", "Unknown"))
        region = ctx.event.get("region", "its guarded lands")
        return (f"{holder} seethes: {violator}'s columns cross {region} "
                f"in defiance of its neutrality")

    if ctx.event_type == "nation_formed":
        formed = ctx.event.get("display_name") or display_nation(
            ctx.event.get("nation", "Unknown"))
        old = ctx.event.get("old_display_name") or ""
        if old and old != formed:
            return f"{old} is no more — {formed} is proclaimed"
        return f"{formed} is proclaimed"

    if ctx.event_type == "dotation_granted":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        region = ctx.event.get("region", "an estate")
        title = ctx.event.get("title", "")
        title_str = f" — styled {title}" if title else ""
        return f"{_name_tag(marshal, nation)} endowed with {region}{title_str}"

    if ctx.event_type == "estate_lost":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        region = ctx.event.get("region", "his estate")
        return f"{_name_tag(marshal, nation)} stripped of his estate at {region}"

    if ctx.event_type == "rente_granted":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        face = int(ctx.event.get("face", 0))
        return f"{_name_tag(marshal, nation)} granted a rente of {face}g/turn"

    if ctx.event_type == "rente_revoked":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        face = int(ctx.event.get("face", 0))
        return f"{_name_tag(marshal, nation)}'s rente of {face}g/turn withdrawn"

    if ctx.event_type == "estate_confiscated":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        region = ctx.event.get("region", "the estate")
        captor = ctx.event.get("confiscated_by", "the conqueror")
        return (f"{captor} confiscated {_name_tag(marshal, nation)}'s "
                f"estate at {region}")

    if ctx.event_type == "estate_respected":
        marshal = ctx.event.get("marshal", "Unknown")
        nation = ctx.event.get("nation", "")
        region = ctx.event.get("region", "the estate")
        respecter = ctx.event.get("respected_by", "the conqueror")
        return (f"{respecter} honored {_name_tag(marshal, nation)}'s "
                f"title at {region}")
    return _NEXT_STAGE


def _oneliner_orders_and_fates(ctx: OnelinerContext):
    """Stage 4 of `format_event_oneliner`: Objections, the campaign's end, the
    congress, literal fidelity; a marshal captured, evacuated, wounded,
    destroyed, standing last or released; standing orders and defiance."""
    if ctx.event_type == "objection":
        marshal = ctx.event.get("marshal", "Unknown")
        action = _display_action(ctx.event.get("action", ""))
        resolution = ctx.event.get("resolution", "")
        if action and resolution:
            return f"{marshal} objected to {action} ({resolution})"
        if action:
            return f"{marshal} objected to {action}"
        return f"{marshal} objected to order"

    if ctx.event_type == "campaign_ending":
        # GE-1: "THE VERDICT OF HISTORY — The reign, unfinished, is judged
        # as it stands. (An Empire Contested)"
        title = str(ctx.event.get("title") or "THE END OF THE CAMPAIGN")
        line = str(ctx.event.get("cause_line") or "")
        tier = str(ctx.event.get("tier_title") or "")
        tail = f" ({tier.title()})" if tier else ""
        return f"{title} — {line}{tail}" if line else f"{title}{tail}"

    if ctx.event_type == "congress":
        # GE-3: one arm per phase (`_format_congress_event`).
        return _format_congress_event(ctx.event)

    if ctx.event_type == "literal_fidelity":
        # W6-5: the beat's message IS the line (composed in marshal_voice).
        return ctx.event.get("message", "A literal marshal held to his orders.")

    if ctx.event_type == "marshal_captured":
        marshal = ctx.event.get("marshal", "Unknown")
        captor = ctx.event.get("captor", "the enemy")
        location = ctx.event.get("location", "the field")
        # NP-V: the chronicle must not demote a sovereign to a marshal —
        # "Marshal Napoleon CAPTURED" printed in the same Gazette issue
        # whose masthead read THE EMPEROR TAKEN. This formatter takes no
        # `world`, so it branches on the event's own `sovereign` key
        # (stamped by WorldState.capture_marshal / release).
        if ctx.event.get("sovereign"):
            return f"THE EMPEROR {marshal} TAKEN by {captor} at {location}"
        return f"{marshal_title(ctx.world, marshal, start=True)} CAPTURED by {captor} at {location}"

    if ctx.event_type == "evacuation_granted":
        a = ctx.event.get("nation_a", "")
        b = ctx.event.get("nation_b", "")
        names = ctx.event.get("marshals") or []
        turns = int(ctx.event.get("turns") or 0)
        cut = ctx.event.get("cut_off") or []
        if ctx.event.get("mid_treaty"):
            # FA-N61 (slice 12): the same type, a different moment. The peace
            # was signed turns ago; this corps was stranded after it, and the
            # standing treaty put him on the road. Rendering it with the
            # sentence above would announce the peace a second time.
            who = ", ".join(names) or "A corps"
            dest = (ctx.event.get("destinations") or {}).get(
                names[0] if names else "", "")
            return (f"{who} put on the road home from "
                    f"{ctx.event.get('region', 'the field')}"
                    + (f" to {dest}" if dest else "")
                    + f" under the peace with {b} — {turns} turns")
        if not names and cut:
            return (f"Peace between {a} and {b} — "
                    f"{', '.join(cut)} cut off, no road home")
        head = (f"Safe passage home granted by the peace between {a} and "
                f"{b} — {len(names)} corps, {turns} turns")
        return head + (f"; {', '.join(cut)} cut off" if cut else "")

    if ctx.event_type == "evacuation_lapsing":
        marshal = ctx.event.get("marshal", "Unknown")
        location = ctx.event.get("location", "the field")
        left = int(ctx.event.get("turns_left") or 0)
        return (f"{marshal_title(ctx.world, marshal, start=True)}'s safe passage is LAPSING at {location} "
                f"— {_plural(left, 'turn')} before internment")

    if ctx.event_type == "marshal_wounded":
        # VP-M1 "The Fortunes of War": the man, not the corps.
        marshal = ctx.event.get("marshal", "Unknown")
        location = ctx.event.get("location", "the field")
        until = int(ctx.event.get("until_turn") or 0)
        tail = f" — out until turn {until}" if until else ""
        return f"{marshal_title(ctx.world, marshal, start=True)} WOUNDED at {location}{tail}; the corps stands"

    if ctx.event_type == "marshal_destroyed":
        marshal = ctx.event.get("marshal", "Unknown")
        location = ctx.event.get("location", "the field")
        victor = ctx.event.get("victor") or ""
        cause = ctx.event.get("cause") or ""
        if cause == "killed_in_action":
            # VP-M1: struck down at the head of his corps — the corps lives.
            return (f"{marshal_title(ctx.world, marshal, start=True)} KILLED at {location}"
                    + (f" — struck down by {victor}'s guns" if victor else "")
                    + "; the corps passes to another hand")
        # GE-1 "The Eagle Falls": the sovereign killed with his corps is a
        # man, not a corps — the event carries `sovereign` because the
        # formatter has no world to look him up in.
        if ctx.event.get("sovereign"):
            return (f"THE EMPEROR {marshal} FALLS at {location}"
                    + (f" — his corps annihilated by {victor}" if victor else ""))
        if cause == "attrition":
            return (f"{marshal_title(ctx.world, marshal, start=True)}'s corps DESTROYED at {location} — "
                    f"starved out by supply attrition")
        # WIN-D3: internment is not annihilation. The corps is off the board
        # by the same seam, but it was disarmed, not destroyed.
        if cause == "interned":
            if victor:
                return (f"{marshal_title(ctx.world, marshal, start=True)}'s corps INTERNED at {location} "
                        f"by {victor} — its safe passage had expired")
            return (f"{marshal_title(ctx.world, marshal, start=True)}'s corps INTERNED at {location} — "
                    f"its safe passage had expired")
        if victor:
            return (f"{marshal_title(ctx.world, marshal, start=True)}'s corps DESTROYED at {location} "
                    f"by {victor}")
        return f"{marshal_title(ctx.world, marshal, start=True)}'s corps DESTROYED at {location}"

    if ctx.event_type == "last_stand":
        marshal = ctx.event.get("marshal", "Unknown")
        location = ctx.event.get("location", "the field")
        inflicted = int(ctx.event.get("casualties_inflicted", 0) or 0)
        return (f"{humanize_entity_name(marshal)}'s last stand at {location} — "
                f"{inflicted:,} enemy casualties before the end")

    if ctx.event_type == "marshal_released":
        marshal = ctx.event.get("marshal", "Unknown")
        captor = ctx.event.get("captor", "captivity")
        reason = (ctx.event.get("reason") or "release").replace("_", " ")
        # GE-1 verification round: two sovereign "releases" are not the end
        # of a captivity, and the chronicle said they were.
        if ctx.event.get("reason") == "escorted_home":
            lost = int(ctx.event.get("corps_interned", 0) or 0)
            where = str(ctx.event.get("interned_at") or "the frontier")
            return (f"THE EMPEROR {marshal}'s corps INTERNED at {where} by "
                    f"{display_nation(captor)}"
                    + (f" ({lost:,} men)" if lost else "")
                    + " — the Emperor himself escorted home")
        if ctx.event.get("reason") == "set_down_at_home":
            return (f"THE EMPEROR {marshal}'s corps is gone, with no court at "
                    f"war to take him — he returns home with an escort")
        if ctx.event.get("sovereign"):  # NP-V: see marshal_captured above
            return (f"THE EMPEROR {marshal} is restored to France by "
                    f"{captor} ({reason})")
        return f"{marshal_title(ctx.world, marshal, start=True)} released by {captor} ({reason})"

    if ctx.event_type == "strategic_order":
        marshal = ctx.event.get("marshal", "Unknown")
        order_type = ctx.event.get("order_type", "UNKNOWN")
        # Human-readable order type (MOVE_TO → "move to", HOLD → "hold", etc.)
        display_order = {
            "MOVE_TO": "move to", "HOLD": "hold",
            "SUPPORT": "support", "PURSUE": "pursue",
        }.get(order_type, order_type.lower().replace("_", " "))
        from backend.display_names import order_target_display
        destination = order_target_display(ctx.event.get("destination", ""))  # EG-X1
        if destination:
            return f"{marshal} ordered to {display_order} {destination}"
        return f"{marshal} ordered to {display_order}"

    if ctx.event_type == "defiance":
        marshal = ctx.event.get("marshal", "Unknown")
        defiance_action = _display_defiance_action(ctx.event.get("defiance_action", "acted independently"))
        return f"{marshal} defied orders and {defiance_action} instead"
    return _NEXT_STAGE


def _oneliner_diplomacy(ctx: OnelinerContext):
    """Stage 5 of `format_event_oneliner`: Treaties, war aims, settlements, the
    ally's entry, AI-AI treaties and the D5 counter-instruments, crises and
    designs (Session 8D)."""
    # ── Diplomacy events (Session 8D) ──
    if ctx.event_type == "diplomatic_treaty_signed":
        nation_a = ctx.event.get("nation_a") or (ctx.event.get("nations", [None, None])[0] or "Unknown")
        nation_b = ctx.event.get("nation_b") or (ctx.event.get("nations", [None, None])[1] if len(ctx.event.get("nations", [])) > 1 else "Unknown")
        treaty_type = (ctx.event.get("treaty_type") or "treaty").replace("_", " ")
        return f"Treaty signed: {nation_a} and {nation_b} ({treaty_type})"

    if ctx.event_type == "diplomatic_war_declared":
        aggressor = ctx.event.get("aggressor") or ctx.event.get("nation", "Unknown")
        target = ctx.event.get("target", "Unknown")
        breached_treaty = ctx.event.get("breached_treaty", "")
        if breached_treaty:
            return f"War declared: {aggressor} → {target} (shattering {breached_treaty})"
        return f"War declared: {aggressor} → {target}"

    if ctx.event_type == "war_objective_declared":
        declaring = ctx.event.get("declaring_nation", "Unknown")
        target = ctx.event.get("target_nation", "Unknown")
        obj_type = (ctx.event.get("objective_type") or "unknown").replace("_", " ").title()
        regions = ctx.event.get("target_regions", [])
        region_str = f" (target: {', '.join(regions)})" if regions else ""
        return f"{declaring} declares {obj_type} against {target}{region_str}"

    # PC-R7 (ii) part 2: the articles declared, and settled at the peace —
    # the event carries its own words (`declared_goals`).
    if ctx.event_type in ("war_articles_declared", "war_articles_settled"):
        return str(ctx.event.get("display") or "").rstrip(".")

    if ctx.event_type == "war_objective_ticking_started":
        declaring = ctx.event.get("declaring_nation", "Unknown")
        region = ctx.event.get("target_region", "unknown")
        rate = ctx.event.get("rate", 0)
        return f"{declaring} holds {region} — ticking war score (+{rate}/turn)"

    if ctx.event_type == "forced_alliance_imposed":
        imposer = ctx.event.get("imposing_nation") or ctx.event.get("imposer", "Unknown")
        target = ctx.event.get("forced_nation") or ctx.event.get("target", "Unknown")
        return f"Forced alliance: {target} enters alliance with {imposer} under duress"

    if ctx.event_type == "vassal_liberated":
        vassal = ctx.event.get("vassal_nation", "Unknown")
        former_lord = ctx.event.get("former_lord", "")
        liberator = ctx.event.get("liberator_nation") or ctx.event.get("liberator", "Unknown")
        if former_lord:
            return f"Liberation: {vassal} freed from {former_lord} by {liberator}"
        return f"Liberation: {vassal} freed from vassalage by {liberator}"

    if ctx.event_type == "settlement_summary":
        from backend.game_logic.settlement_presentation import (
            compose_summary_oneliner,
        )

        return compose_summary_oneliner(ctx.event)

    if ctx.event_type == "settlement_digest":
        from backend.game_logic.settlement_presentation import (
            compose_digest_oneliner,
        )

        return compose_digest_oneliner(ctx.event)

    # SC-33 recurring settlement gold (G4F smoke follow-up): the payments
    # fired in the morning dispatch but vanished from the campaign log
    # history entirely (type-filtered out).
    # SC-30 / Slice G1: the Request Terms lifecycle beats.
    if ctx.event_type == "settlement_terms_requested":
        return (
            f"Terms requested from {ctx.event.get('answering_leader', 'the enemy court')} "
            f"on {ctx.event.get('war_label', 'the war')}."
        )

    if ctx.event_type == "settlement_terms_request_granted":
        return (
            f"{ctx.event.get('answering_leader', 'The enemy court')} answered our "
            f"request with settlement terms for {ctx.event.get('war_label', 'the war')}."
        )

    if ctx.event_type == "settlement_terms_request_refused":
        return (
            f"{ctx.event.get('answering_leader', 'The enemy court')} refused to name "
            f"terms for {ctx.event.get('war_label', 'the war')}."
        )

    # Slice H: full-agency ally petition beats.
    if ctx.event_type == "settlement_ally_petition_granted":
        return (
            f"Granted {ctx.event.get('ally_nation', 'an ally')}'s settlement "
            f"petition over {ctx.event.get('claim_region', 'its claim')} on "
            f"{ctx.event.get('war_label', 'the war')}."
        )

    if ctx.event_type == "settlement_ally_petition_declined":
        return (
            f"Declined {ctx.event.get('ally_nation', 'an ally')}'s settlement "
            f"petition over {ctx.event.get('claim_region', 'its claim')} on "
            f"{ctx.event.get('war_label', 'the war')}."
        )

    if ctx.event_type == "settlement_bargain_honored":
        return (
            f"Honored the pledge on {ctx.event.get('claim_region', 'the claim')} "
            f"to {ctx.event.get('ally_nation', 'an ally')} in the settlement "
            f"draft of {ctx.event.get('war_label', 'the war')}."
        )

    if ctx.event_type == "settlement_recurring_gold_paid":
        return (
            f"{ctx.event.get('from_nation', 'Unknown')} paid "
            f"{ctx.event.get('amount_paid', '?')} gold to "
            f"{ctx.event.get('to_nation', 'Unknown')} on the settlement of "
            f"{ctx.event.get('war_label', 'the war')} "
            f"({ctx.event.get('turns_remaining', '?')} turns remaining)."
        )

    if ctx.event_type == "settlement_recurring_gold_partial":
        return (
            f"{ctx.event.get('from_nation', 'Unknown')} could only pay "
            f"{ctx.event.get('amount_paid', '?')}/{ctx.event.get('amount_due', '?')} "
            f"gold to {ctx.event.get('to_nation', 'Unknown')} on the settlement "
            f"of {ctx.event.get('war_label', 'the war')}."
        )

    if ctx.event_type == "settlement_recurring_gold_completed":
        return (
            f"Settlement obligation fulfilled: {ctx.event.get('total_amount', '?')} "
            f"gold from {ctx.event.get('from_nation', 'Unknown')} to "
            f"{ctx.event.get('to_nation', 'Unknown')} "
            f"({ctx.event.get('war_label', 'the war')})."
        )

    if ctx.event_type == "surety_returned":
        _regions = ctx.event.get("regions")
        _regions = ", ".join(_regions) if isinstance(_regions, list) else str(_regions or "")
        return (
            f"The indemnity is paid: {_regions} — held by "
            f"{ctx.event.get('payee', 'Unknown')} until paid — return to "
            f"{ctx.event.get('ceder', 'Unknown')}."
        )

    if ctx.event_type == "settlement_recurring_gold_cancelled":
        reason = str(ctx.event.get("reason", "circumstances")).replace("_", " ")
        return (
            f"Recurring settlement payment from "
            f"{ctx.event.get('from_nation', 'Unknown')} to "
            f"{ctx.event.get('to_nation', 'Unknown')} cancelled ({reason})."
        )

    if ctx.event_type == "hard_block_surfaced":
        # IGR-A1: was `reason.replace("_", " ")` — i.e. "no participation
        # path" straight to the chronicle. The raw key still rides the event
        # (old saves included); only the rendering changed.
        beneficiary = ctx.event.get("beneficiary", "Unknown")
        target_enemy = ctx.event.get("target_enemy") or ctx.event.get("named_enemy", "Unknown")
        return ally_entry_block_line(
            str(ctx.event.get("hard_block_reason", "")),
            beneficiary,
            target_enemy,
            str(ctx.event.get("promiser", "") or ""),
        )

    if ctx.event_type == "ally_refused_free_join":
        beneficiary = ctx.event.get("beneficiary", "Unknown")
        target_enemy = ctx.event.get("target_enemy") or ctx.event.get("named_enemy", "Unknown")
        return f"{beneficiary} declined to join against {target_enemy} without terms."

    if ctx.event_type == "declaration_backed_out":
        named_enemy = ctx.event.get("named_enemy") or ctx.event.get("target_enemy", "Unknown")
        return f"War declaration against {named_enemy} cancelled."

    if ctx.event_type == "bargain_repudiated":
        beneficiary = ctx.event.get("beneficiary", "Unknown")
        claim_region = ctx.event.get("claim_region", "Unknown")
        return f"France repudiated the bargain with {beneficiary} over {claim_region}."

    if ctx.event_type == "ally_entry_accepted":
        beneficiary = ctx.event.get("beneficiary", "Unknown")
        named_enemy = ctx.event.get("named_enemy", "Unknown")
        return f"{beneficiary} joins the war against {named_enemy}."

    if ctx.event_type == "ally_entry_refused":
        beneficiary = ctx.event.get("beneficiary", "Unknown")
        named_enemy = ctx.event.get("named_enemy", "Unknown")
        return f"{beneficiary} refuses to join against {named_enemy}."

    if ctx.event_type == "counter_bargain_accepted":
        beneficiary = ctx.event.get("beneficiary", "Unknown")
        claim_region = ctx.event.get("demanded_region") or ctx.event.get("claim_region", "Unknown")
        return f"Counter-bargain accepted: {beneficiary} claims {claim_region}."

    if ctx.event_type == "counter_bargain_rejected":
        beneficiary = ctx.event.get("beneficiary", "Unknown")
        return f"Counter-bargain from {beneficiary} rejected."

    if ctx.event_type == "vassal_broke_free":
        nation = ctx.event.get("vassal") or ctx.event.get("nation", "Unknown")
        lord = ctx.event.get("lord") or "its lord"
        exit_path = str(ctx.event.get("exit") or "")
        if exit_path == "vassal_rebellion_armistice":
            return (f"Vassal rebellion: {nation} breaks free of {lord} "
                    f"— the armistice holds.")
        if exit_path == "vassal_rebellion_independent":
            return (f"Vassal rebellion: {nation} breaks free of {lord} "
                    f"and stands alone.")
        # FA-S12-2: the FOURTH arm, and it is not a rebellion at all — the
        # lord is dead and the satellite is free by default. Without it the
        # `lord_eliminated` exit falls through to "…has broken free. War.",
        # which is wrong in every clause: nobody broke anything and there is
        # no war.
        if exit_path == "lord_eliminated":
            return (f"{lord} has fallen — {nation} is a satellite no longer, "
                    f"and its corps march under their own colours again.")
        return f"Vassal rebellion: {nation} has broken free of {lord}. War."


    if ctx.event_type == "diplomatic_alliance_cascade":
        nation = ctx.event.get("defender") or ctx.event.get("nation", "Unknown")
        ally = ctx.event.get("ally", "Unknown")
        # SR-6a RS-23: the enemy named where the event carries it.
        against = ctx.event.get("against")
        if against:
            return f"Alliance cascade: {nation} enters war against {against} via {ally}"
        return f"Alliance cascade: {nation} enters war via {ally}"

    if ctx.event_type == "diplomatic_ai_ai_treaty":
        nation_a = ctx.event.get("nation_a", "Unknown")
        nation_b = ctx.event.get("nation_b", "Unknown")
        treaty_type = (ctx.event.get("treaty_type") or "treaty").replace("_", " ")
        if THE_COURTS_TREATIES_READ_AS_PROSE:
            # SF-LB-3 rider (Score Finish Step 7b): two courts' treaty as a
            # sentence of the chronicle, the courts by name.
            return (f"{with_definite_article(display_nation(nation_a), capitalize=True)} "
                    f"and {with_definite_article(display_nation(nation_b))} sign "
                    f"a {treaty_type}")
        return f"AI-AI treaty: {nation_a} and {nation_b} ({treaty_type})"

    if ctx.event_type == "ai_ai_proposal_refused":
        # AI-2a: the court-to-court refusal — the ask happened, was
        # rebuffed, and the balance of power is WITNESSED (§3.4).
        proposer = ctx.event.get("proposer", "Unknown")
        refused_by = ctx.event.get("refused_by") or ctx.event.get("recipient",
                                                          "Unknown")
        ptype = _proposal_label(ctx.event)
        # IGR-B: a burst of these arrives collapsed into one row.
        count = int(ctx.event.get("collapsed_count") or 0)
        if count > 1:
            return _collapsed_refusal_line(ctx.event, ptype, count)
        return f"{refused_by} rebuffs {proposer} ({ptype})"

    # PC-R7 (ii) part 3: the league's bond rides the directed records' events
    # (granted / reneged / expired / lapsed with kind "bond") — its own words.
    if ctx.event.get("kind") == "bond" or ctx.event.get("instrument") == "bond":
        from backend.game_logic.bond import log_line as _bond_log_line
        _line = _bond_log_line(ctx.event_type, ctx.event)
        if _line:
            return _line

    # AI-2b: the D5 counter-instruments.
    if ctx.event_type == "sponsorship_granted":
        payer = display_nation(ctx.event.get("payer", "Unknown"))
        recipient = display_nation(ctx.event.get("recipient", "Unknown"))
        aim = display_nation(ctx.event.get("aim", "")) if ctx.event.get("aim") else ""
        if ctx.event.get("kind") == "neutrality":
            return (f"{payer} buys {recipient}'s neutrality"
                    + (f" in the war over {aim}" if aim else ""))
        if ctx.event.get("licence"):
            return f"{payer} licences {recipient}'s design against {aim}"
        return (f"{payer} sponsors {recipient}"
                + (f" against {aim}" if aim else "")
                + f" ({int(ctx.event.get('amount', 0))}g/turn)")

    if ctx.event_type == "sponsorship_reneged":
        breaker = display_nation(ctx.event.get("breaker", "Unknown"))
        victim = display_nation(ctx.event.get("victim", "Unknown"))
        noun = ("licence" if ctx.event.get("licence")
                else "neutrality compact"
                if ctx.event.get("kind") == "neutrality" else "sponsorship")
        return f"THE BROKEN BARGAIN: {breaker} tears up its {noun} with {victim}"

    if ctx.event_type == "sponsorship_expired":
        payer = display_nation(ctx.event.get("payer", "Unknown"))
        recipient = display_nation(ctx.event.get("recipient", "Unknown"))
        return f"The compact between {payer} and {recipient} lapses"

    if ctx.event_type == "design_bought_off":
        payer = display_nation(ctx.event.get("payer", "Unknown"))
        recipient = display_nation(ctx.event.get("recipient", "Unknown"))
        if ctx.event.get("clause") == "territory_compensate":
            # PC-R7 (ii): the compensation clause, struck at the peace.
            region = str(ctx.event.get("region") or "")
            if ctx.event.get("form") == "pointed":
                title = str(ctx.event.get("design_title") or "its design")
                return (f"The peace points {recipient} elsewhere: {payer} licenses "
                        f"{title} ({region}) — her other designs sleep")
            return f"The peace compensates {recipient} with {region}, {payer}'s"
        return f"{payer} buys off {recipient}'s design — the want sleeps"

    if ctx.event_type == "bargain_reneged":
        breaker = display_nation(ctx.event.get("breaker", "Unknown"))
        victim = display_nation(ctx.event.get("victim", "Unknown"))
        return (f"THE BROKEN BARGAIN: {breaker} reneges on its compact "
                f"with {victim} — the design returns")

    if ctx.event_type == "guarantee_pledged":
        guarantor = display_nation(ctx.event.get("guarantor", "Unknown"))
        protected = display_nation(ctx.event.get("protected", "Unknown"))
        return f"{guarantor} guarantees {protected}"

    if ctx.event_type == "guarantee_abandoned":
        breaker = display_nation(ctx.event.get("breaker", "Unknown"))
        victim = display_nation(ctx.event.get("victim", "Unknown"))
        return (f"A guarantee proves paper: {breaker} abandons "
                f"{victim} to its attackers")

    if ctx.event_type == "british_subsidy":
        payer = display_nation(ctx.event.get("payer", "Unknown"))
        recipient = display_nation(ctx.event.get("recipient", "Unknown"))
        amount = int(ctx.event.get("amount", 0))
        return f"{payer}'s gold: {amount}g reaches {recipient}"

    if ctx.event_type == "instrument_lapsed":
        payer = display_nation(ctx.event.get("payer", "Unknown"))
        recipient = display_nation(ctx.event.get("recipient", "Unknown"))
        reason = ctx.event.get("reason", "")
        if reason == "term_served":
            return (f"The bargain between {payer} and {recipient} is "
                    f"served in full — the design wakes")
        if reason == "ward_aggression":
            return (f"{recipient} marches of its own will — "
                    f"{payer}'s guarantee is void, unblamed")
        return (f"War overtakes the compact between {payer} and "
                f"{recipient} — it lapses, no breaker named")

    if ctx.event_type == "crisis_brewing":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        target = display_nation(ctx.event.get("target", "Unknown"))
        return f"THE BREWING CRISIS: {nation} will move on {target}"

    if ctx.event_type == "coercive_demand":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        target = display_nation(ctx.event.get("target", "Unknown"))
        return f"{nation} delivers a final demand to {target} — refused"

    if ctx.event_type == "crisis_passed":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        target = display_nation(ctx.event.get("target", "Unknown"))
        cause = str(ctx.event.get("cause", "starved"))
        # Single source: war_council owns the beat-7 cause taxonomy, incl.
        # AI-3r's exposed / outmatched / penniless (July 25, 2026 review).
        from backend.game_logic.war_council import crisis_cause_phrase
        cause_copy = crisis_cause_phrase(cause)
        return f"THE CRISIS PASSES: {nation} stands down over {target} ({cause_copy})"

    if ctx.event_type == "guarantee_honored":
        guarantor = display_nation(ctx.event.get("guarantor", "Unknown"))
        ward = display_nation(ctx.event.get("ward", "Unknown"))
        aggressor = display_nation(ctx.event.get("aggressor", "Unknown"))
        return f"{guarantor} honours its guarantee of {ward} — war on {aggressor}"

    if ctx.event_type == "third_party_peace":
        a = display_nation(ctx.event.get("proposer", "Unknown"))
        b = display_nation(ctx.event.get("accepter", "Unknown"))
        return f"THE CONGRESS: {a} and {b} make peace without France"

    if ctx.event_type == "coalition_dissolved_for_france":
        prev = display_nation(ctx.event.get("previous_target", "Unknown"))
        return (f"The coalition against {prev} dissolves — Europe "
                f"remembers who the real danger is")

    if ctx.event_type == "design_promoted":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        author = display_nation(ctx.event.get("author", "Unknown"))
        regions = list(ctx.event.get("regions") or [])
        first = regions[0] if regions else "its provinces"
        tail = f" and {len(regions) - 1} more" if len(regions) > 1 else ""
        return (f"REVANCHE: {nation} swears to retake {first}{tail} — "
                f"{author} is not forgiven")

    if ctx.event_type == "volte_face":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        partner = display_nation(ctx.event.get("partner", "Unknown"))
        return (f"THE VOLTE-FACE: {nation}, beaten and then courted, "
                f"takes {partner}'s hand")
    return _NEXT_STAGE


def _oneliner_laws(ctx: OnelinerContext):
    """Stage 6 of `format_event_oneliner`: A law enacted, repealed or lapsed
    (SR-5r)."""
    # ── SR-5r "The Laws" (REFORMS_SPEC §8) ────────────────────────────
    if ctx.event_type in ("law_enacted", "law_repealed", "law_lapsed"):
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        name = str(ctx.event.get("name") or ctx.event.get("law") or "a law")
        if name.startswith("The "):
            name = "the " + name[4:]
        upkeep = int(ctx.event.get("upkeep", 0) or 0)
        if ctx.event_type == "law_repealed":
            return f"{nation} repeals {name}"
        if ctx.event_type == "law_lapsed":
            return (f"{nation} cannot pay for {name} ({upkeep:,}g a turn) — "
                    f"the law lapses")
        verb = "restores" if ctx.event.get("restored") else "enacts"
        return f"{nation} {verb} {name} ({upkeep:,}g a turn)"
    return _NEXT_STAGE


def _oneliner_the_sea(ctx: OnelinerContext):
    """Stage 7 of `format_event_oneliner`: Fleets, blockades, the Continental
    System, the straits, the Descent and the expeditions (DEF-5); the flip in
    play."""
    # ── DEF-5 naval (NV-0..NV-3) ──────────────────────────────────────
    if ctx.event_type == "fleet_laid_down":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        return (f"{nation} lays down a ship of the line "
                f"({int(ctx.event.get('ships', 0))} sail, readiness "
                f"{int(ctx.event.get('readiness', 0))})")

    if ctx.event_type == "fleet_posture":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        posture = ctx.event.get("posture", "guard")
        return (f"{nation}'s fleet stands out on blockade" if posture == "blockade"
                else f"{nation}'s fleet returns to guard home waters")

    if ctx.event_type == "blockade_begins":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        blockader = display_nation(ctx.event.get("blockader", "Unknown"))
        trade = str(ctx.event.get("trade_words") or "halved")
        return f"BLOCKADE: {blockader} closes {nation}'s ports — trade {trade}, crews rot at anchor"

    if ctx.event_type == "blockade_broken":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        return f"The blockade of {nation} is broken — her ports breathe again"

    if ctx.event_type == "continental_system_membership":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        tail = str(ctx.event.get("tail") or "")
        if ctx.event.get("action") == "left":
            return f"{nation} leaves the Continental System{tail}"
        return f"{nation} joins the Continental System{tail}"

    if ctx.event_type == "cs_tier_shift":
        target = display_nation(ctx.event.get("target", "Unknown"))
        pct = int(ctx.event.get("closure_pct", 0))
        tier = int(ctx.event.get("tier", 0))
        if tier > 0:
            return (f"THE CONTINENTAL SYSTEM: {pct}% of the Continent's ports "
                    f"closed — {target}'s war-weariness rises +{tier}/turn")
        return (f"The Continental System loosens — {pct}% of the Continent's "
                f"ports closed, {target} breathes")

    if ctx.event_type == "strait_open":
        a, b = ctx.event.get("link_a"), ctx.event.get("link_b")
        if a and b:
            return f"THE STRAIT LIES OPEN: the {a}–{b} crossing can be forced"
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        against = display_nation(ctx.event.get("against", "Unknown"))
        return (f"THE STRAIT LIES OPEN: {nation}'s diversion draws the "
                f"{against} fleet off station")

    if ctx.event_type == "strait_shut":
        a = ctx.event.get("link_a", "?")
        b = ctx.event.get("link_b", "?")
        coverer = display_nation(ctx.event.get("coverer", "")) if ctx.event.get("coverer") else ""
        tail = f" — {coverer} commands the water" if coverer else ""
        return f"The {a}–{b} crossing is shut{tail}"

    if ctx.event_type == "boulogne_camp":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        against = display_nation(ctx.event.get("against", "Unknown"))
        return (f"THE CAMP: {nation} masses {ctx.event.get('strength', 0):,} men "
                f"on the invasion coast — {against} watches the water")

    if ctx.event_type in ("trafalgar", "fleet_action"):
        winner = display_nation(ctx.event.get("winner", "Unknown"))
        loser = display_nation(ctx.event.get("loser", "Unknown"))
        if ctx.event.get("decisive"):
            return (f"TRAFALGAR: {winner}'s line shatters {loser}'s fleet — "
                    f"a decisive action at sea")
        return f"Action at sea: {winner}'s squadrons get the better of {loser}"

    if ctx.event_type == "expedition_landed":
        marshal = ctx.event.get("marshal", "The expedition")
        target = ctx.event.get("target", "?")
        return (f"THE LANDING: {marshal} puts {int(ctx.event.get('troops', 0)):,} "
                f"men ashore at {target}")

    if ctx.event_type == "expedition_intercepted":
        marshal = ctx.event.get("marshal", "The expedition")
        coverer = display_nation(ctx.event.get("coverer", "the enemy"))
        return (f"INTERCEPTED: {coverer}'s squadrons catch {marshal}'s "
                f"transports at sea — {int(ctx.event.get('troops_lost', 0)):,} men lost")

    if ctx.event_type == "expedition_turned_back":
        marshal = ctx.event.get("marshal", "The expedition")
        target = ctx.event.get("target", "?")
        return f"{marshal}'s expedition to {target} is turned back at sea"

    if ctx.event_type == "naval_turnback":
        marshal = ctx.event.get("marshal", "An army")
        nation = display_nation(ctx.event.get("nation", ""))
        a, b = ctx.event.get("link_a", "?"), ctx.event.get("link_b", "?")
        prefix = f"{nation}'s {marshal}" if nation else marshal
        return f"{prefix} halts at the {a}–{b} crossing — hostile sail command the water"

    if ctx.event_type == "allegiance_auction_opened":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        return f"THE FLIP IS IN PLAY: {nation} weighs its allegiance"
    return _NEXT_STAGE


def _oneliner_allegiance(ctx: OnelinerContext):
    """Stage 8 of `format_event_oneliner`: The allegiance bid, a province
    returned, the auction resolved (DD-1)."""
    # DD-1 S8 Step 3 — the verbs (October 12, 2026)
    if ctx.event_type == "allegiance_bid":
        suitor = display_nation(ctx.event.get("nation", "Unknown"))
        court = display_nation(ctx.event.get("target_nation", "Unknown"))
        return (f"{suitor} lays {int(ctx.event.get('gold', 0) or 0)} gold before the court of "
                f"{court} — the bid stands at {int(ctx.event.get('total', 0) or 0)}; the flip "
                f"resolves on turn {int(ctx.event.get('resolves_turn', 0) or 0)}")

    if ctx.event_type == "province_returned":
        asker = display_nation(ctx.event.get("nation", "Unknown"))
        holder = display_nation(ctx.event.get("target_nation", "Unknown"))
        region = ctx.event.get("region", "a province")
        if ctx.event.get("outcome") == "returned":
            return f"{holder} hands {region} back to {asker} — the liberated soil comes home"
        return (f"{holder} declines to return {region} to {asker} "
                f"({int(ctx.event.get('shortfall', 0) or 0)} more standing wanted)")

    if ctx.event_type == "allegiance_auction_resolved":
        nation = display_nation(ctx.event.get("nation", "Unknown"))
        outcome = ctx.event.get("outcome", "")
        if outcome == "lapsed":
            return f"The moment passes — {nation} keeps its own counsel"
        if outcome == "no_suitor":
            return f"No court bids for {nation}; the flip dissolves"
        winner = display_nation(ctx.event.get("winner") or "Unknown")
        if outcome == "player_offer":
            return (f"{nation} chooses France — their envoy carries "
                    f"the pact")
        return f"THE FLIP: {nation} signs with {winner}"
    return _NEXT_STAGE


def _oneliner_cascades_and_coalitions(ctx: OnelinerContext):
    """Stage 9 of `format_event_oneliner`: A war declared, the cascades, a
    coalition declared or dissolved."""
    # Deep audit fix: new event types
    if ctx.event_type == "war_declaration":
        aggressor = ctx.event.get("aggressor") or ctx.event.get("nation", "Unknown")
        target = ctx.event.get("target", "Unknown")
        return f"War declared: {aggressor} → {target}"

    if ctx.event_type == "defensive_cascade":
        # FA-S17-8 (Phase 3): the producer writes `defender`; this read
        # `nation` and printed "Unknown joins war via …" twenty times across
        # seventeen Phase-3 runs.
        nation = ctx.event.get("defender") or ctx.event.get("nation", "Unknown")
        ally = ctx.event.get("ally", "Unknown")
        return f"Defensive cascade: {nation} joins war via {ally}"

    if ctx.event_type == "offensive_cascade":
        nation = ctx.event.get("nation", "Unknown")
        aggressor = ctx.event.get("aggressor", "Unknown")
        return f"Offensive cascade: {nation} joins {aggressor}'s war"

    if ctx.event_type == "coalition_declared":
        members = ctx.event.get("members", [])
        members_str = ', '.join(members) if members else 'Unknown'
        # Stage D review fix [r6]: an ECLIPSE coalition names its own
        # target — never dressed as a coalition against France.
        target = ctx.event.get("target_nation") or "France"
        # Slice 17 review round (L2-5): the paper names the coalition the
        # notification names ("The Fourth Austria Coalition") — FA-N85's
        # ordinal reached every surface but this one.
        name = str(ctx.event.get("coalition_name") or "")
        prefix = f"{name} — " if name else ""
        if target != "France":
            return (f"{prefix}Coalition formed against {display_nation(target)}! "
                    f"Members: {members_str}")
        return f"{prefix}Coalition formed against France! Members: {members_str}"

    if ctx.event_type == "coalition_dissolved":
        target = ctx.event.get("target_nation") or "France"
        # IQ-3: a treaty-dissolved league stamps `alarm_spent`; the entry
        # says the league is spent and by how much. No key = as before.
        spent = ctx.event.get("alarm_spent") or None
        if target != "France":
            if spent:
                return (f"Coalition against {display_nation(target)} has "
                        f"dissolved — the league is spent.")
            return f"Coalition against {display_nation(target)} has dissolved."
        if spent:
            frm, to = int(spent.get("from", 0)), int(spent.get("to", 0))
            moved = (f"Europe's alarm falls from {frm} to {to}" if frm > to
                     else f"Europe's alarm stands at {to}")
            line = (f"Coalition against France has dissolved — the league "
                    f"is spent; {moved}")
            # IQ-3 review: a court genuinely still at war (the separate-peace
            # road) is named; courts signing in the same action never are.
            still = [display_nation(c) for c in (ctx.event.get("courts_at_war") or []) if c]
            if still:
                joined = (still[0] if len(still) == 1
                          else ", ".join(still[:-1]) + f" and {still[-1]}")
                verb = "remains" if len(still) == 1 else "remain"
                line += f"; {joined} {verb} at war with us"
            return line + "."
        # IQ-2: the league lapses on low threat and ends no war — the entry
        # now carries the courts still fighting France (`courts_at_war`,
        # stamped by coalition.dissolve_coalition).
        # An entry without the key renders exactly as before.
        still_at_war = [display_nation(c) for c in (ctx.event.get("courts_at_war") or []) if c]
        if still_at_war:
            joined = (still_at_war[0] if len(still_at_war) == 1
                      else ", ".join(still_at_war[:-1]) + f" and {still_at_war[-1]}")
            verb = "remains" if len(still_at_war) == 1 else "remain"
            return (f"Coalition against France has dissolved — {joined} "
                    f"{verb} at war with us.")
        return "Coalition against France has dissolved."
    return _NEXT_STAGE


def _oneliner_the_fallen_and_the_clients(ctx: OnelinerContext):
    """Stage 10 of `format_event_oneliner`: A nation eliminated; vassals
    joining, refusing, transferred, defecting; the client's petition; a member
    leaving the coalition."""
    # V3 Session 8: new event types
    if ctx.event_type == "nation_eliminated":
        # SRX-21: the court by its name, never its tag.
        nation = with_definite_article(
            display_nation(ctx.event.get("nation", "Unknown")), capitalize=True)
        return f"{nation} has been eliminated from the war."

    if ctx.event_type == "vassal_auto_join_war":
        vassal = ctx.event.get("vassal") or ctx.event.get("nation", "Unknown")
        # Drive-by (VS-4 build): the emitter passes "lord"; the old read of
        # only "overlord" rendered every one-liner as "Unknown's war".
        overlord = ctx.event.get("overlord") or ctx.event.get("lord", "Unknown")
        # PR-2: measured, "Vassal KingdomOfItaly joined France's war."
        # NB: no local import here — `display_nation` is module-level, and a
        # function-scoped `from ... import` would shadow it for EVERY other
        # arm of this same function (measured: UnboundLocalError on the
        # `nation` arm ~600 lines below, caught by the IGR-B endpoint pins).
        return (f"Vassal {display_nation(vassal)} joined "
                f"{display_nation(overlord)}'s war.")

    if ctx.event_type == "vassal_refuses_call":
        # VS-4: a disaffected satellite declines the call-to-arms
        vassal = ctx.event.get("vassal", "Unknown")
        lord = ctx.event.get("lord", "Unknown")
        loyalty = ctx.event.get("loyalty", "?")
        return (f"{vassal} refuses {lord}'s call to arms "
                f"(loyalty {loyalty}).")

    if ctx.event_type == "vassal_contingent":
        # VD-C: the beat's own sentence, composed through display_nation at
        # the producer (`contingent._beat`) — the message IS the one-liner.
        return str(ctx.event.get("message") or
                   f"{display_nation(ctx.event.get('vassal', 'Unknown'))}'s contingent.")

    if ctx.event_type == "vassal_transferred":
        # VS-5: peace-table lord re-homing
        # Slice 17 review round (L2-4): raw nation keys reached Le Moniteur
        # ("KingdomOfItaly passes from…") — the R7 chokepoint, like the rows
        # around it.
        vassal = display_nation(ctx.event.get("vassal", "Unknown"))
        from_lord = display_nation(ctx.event.get("from_lord", "Unknown"))
        to_lord = display_nation(ctx.event.get("to_lord", "Unknown"))
        return (f"{vassal} passes from {from_lord}'s suzerainty "
                f"to {to_lord}'s.")

    if ctx.event_type == "vassal_defected":
        # VS-6: the bribed coalition-flip
        vassal = ctx.event.get("vassal", "Unknown")
        lord = ctx.event.get("lord", "Unknown")
        briber = ctx.event.get("briber", "Unknown")
        outcome = ctx.event.get("outcome", "")
        if outcome == "transfer":
            return (f"THE DEFECTION: {briber}'s gold buys {vassal} away "
                    f"from {lord} — it serves a new master.")
        return (f"THE DEFECTION: {briber}'s gold turns {vassal} against "
                f"{lord} — the freed satellite takes the field.")

    if ctx.event_type == "client_petition_answered":
        # IQ-7: a client's petition — answered by its lord, or by silence.
        # "The Kingdom of Italy's petition for Tyrol — granted."
        vassal = with_definite_article(
            display_nation(str(ctx.event.get("vassal") or "Unknown")),
            capitalize=True)
        subject = str(ctx.event.get("subject") or "")
        region = str(ctx.event.get("region") or "")
        outcome = str(ctx.event.get("outcome") or "")
        ask = (f"for {region}" if subject == "province" and region
               else "for relief from tribute")
        if outcome == "granted":
            verdict = "granted"
        elif outcome == "fulfilled":
            # IQ-7 review R1 (Sept 18, 2026): the deed was done by the lord's
            # own cede before the answer — honoured, never "refused".
            return (f"{vassal}'s petition {ask} — already ceded by our own "
                    f"hand; honoured.")
        elif outcome == "withdrawn":
            return f"{vassal}'s petition {ask} — withdrawn, nothing charged."
        elif outcome == "unanswered":
            verdict = ("left unanswered, refused"
                       if ctx.event.get("penalty", True) else "left unanswered")
        else:
            verdict = "refused"
        # IQ-7 review R8(e): a refusal (spoken or by silence) quotes the
        # applied price its own event already carries.
        tail = ""
        if (ctx.event.get("penalty") and verdict.endswith("refused")
                and ctx.event.get("loyalty_before") is not None):
            tail = (f": loyalty {ctx.event.get('loyalty_before')} → "
                    f"{ctx.event.get('loyalty_after')}, bond "
                    f"{ctx.event.get('relation_before')} → {ctx.event.get('relation_after')}")
        return f"{vassal}'s petition {ask} — {verdict}{tail}."

    if ctx.event_type == "coalition_member_left":
        nation = ctx.event.get("nation", "Unknown")
        return f"{nation} has left the coalition."
    return _NEXT_STAGE


def _oneliner_proposals_and_ultimatums(ctx: OnelinerContext):
    """Stage 11 of `format_event_oneliner`: AI proposals and ultimatums, the
    brewing coalition, counter-offers, missions, the proposal queue, garrisons,
    relationships, the peace ratified (R8, PL-14, PL-27, BPH)."""
    # ── R8 Session 6: format strings for 16 previously-silent types ──

    # W6-0 (BUG-CA-7 log half): these two events fire when the PLAYER answers
    # an incoming AI proposal — `source` is the nation that PROPOSED, and we
    # are the side that answered. The old copy reversed the direction
    # ("Saxony rejected our open borders proposal" when we rejected Saxony's).
    if ctx.event_type == "ai_proposal_accepted":
        # SRX-22: the court by its name ("the Papal States'", not
        # "PapalStates's").
        source = _possessive_court(ctx.event.get("source", "Unknown"))
        proposal_type = _proposal_label(ctx.event)
        return f"We accepted {source} {proposal_type} proposal{_decision_reason_suffix(ctx.event)}"

    if ctx.event_type == "ai_proposal_rejected":
        source = _possessive_court(ctx.event.get("source", "Unknown"))
        proposal_type = _proposal_label(ctx.event)
        return f"We rejected {source} {proposal_type} proposal{_decision_reason_suffix(ctx.event)}"

    if ctx.event_type == "ai_proposal_counter_failed":
        source = ctx.event.get("source", "Unknown")
        return f"{source} rejected our counter-offer{_decision_reason_suffix(ctx.event)}"

    # NA-5 §8: incoming AI ultimatum resolution (same direction rule as the
    # ai_proposal pair — `source` issued the demand, WE answered it).
    if ctx.event_type == "ai_ultimatum_accepted":
        source = ctx.event.get("source", "Unknown")
        return f"We yielded to {source}'s ultimatum — their demands conceded"

    if ctx.event_type == "ai_ultimatum_rejected":
        source = ctx.event.get("source", "Unknown")
        return f"We defied {source}'s ultimatum — their court will not forget"

    if ctx.event_type == "ai_ultimatum_void":
        source = ctx.event.get("source", "Unknown")
        if ctx.event.get("reason") == "gone":
            return f"{source}'s ultimatum died with their court"
        return f"{source}'s ultimatum was overtaken by war — the demand is void"

    if ctx.event_type == "auto_downgrade":
        nation_a = ctx.event.get("nation_a", "Unknown")
        nation_b = ctx.event.get("nation_b", "Unknown")
        from_state = (ctx.event.get("from_state") or "treaty").replace("_", " ")
        to_state = (ctx.event.get("to_state") or "peace").replace("_", " ")
        return f"Relations auto-downgraded: {nation_a}–{nation_b} ({from_state} → {to_state})"

    if ctx.event_type == "coalition_brewing_started":
        threat = ctx.event.get("threat_level", 0)
        qualifying = ctx.event.get("qualifying_nations", [])
        nations_str = ", ".join(qualifying) if qualifying else "several nations"
        # Stage D review fix [r1]: name a non-France target explicitly.
        brew_target = ctx.event.get("target_nation") or "France"
        if brew_target != "France":
            return (f"Coalition brewing against {display_nation(brew_target)} "
                    f"— {nations_str} consulting (their alarm: {threat})")
        return f"Coalition brewing — {nations_str} alarmed (threat: {threat})"

    if ctx.event_type == "coalition_brewing_cancelled":
        if ctx.event.get("reason") == "the_imperial_peace":
            # SF-RR7: the signing dismisses the brew — and buys no more.
            courts = [display_nation(n) for n in (ctx.event.get("qualifying_nations") or [])]
            among = f" among {and_join(courts)}" if courts else ""
            return (f"The Imperial Peace dismisses the league brewing{among} — "
                    f"the lesser courts signed nothing")
        return "Coalition threat has subsided"

    if ctx.event_type == "counter_offer_accepted":
        source = ctx.event.get("source", "Unknown")
        proposal_type = _proposal_label(ctx.event)
        return f"{source} accepted our counter-offer ({proposal_type}){_decision_reason_suffix(ctx.event)}"

    if ctx.event_type == "counter_offer_rejected":
        source = ctx.event.get("source", "Unknown")
        proposal_type = _proposal_label(ctx.event)
        return f"{source} rejected our counter-offer ({proposal_type}){_decision_reason_suffix(ctx.event)}"

    if ctx.event_type == "diplomatic_discrepancy":
        message = ctx.event.get("message", "Talleyrand altered your proposal")
        return message

    if ctx.event_type == "diplomatic_downgrade":
        nation_a = ctx.event.get("nation_a", "Unknown")
        nation_b = ctx.event.get("nation_b", "Unknown")
        from_state = (ctx.event.get("from_state") or "treaty").replace("_", " ")
        to_state = (ctx.event.get("to_state") or "peace").replace("_", " ")
        return f"Relations downgraded: {nation_a}–{nation_b} ({from_state} → {to_state})"

    if ctx.event_type == "diplomatic_mission_cancelled_eliminated":
        target = ctx.event.get("target", "Unknown")
        return f"Diplomatic mission to {target} cancelled — nation eliminated"

    if ctx.event_type == "diplomatic_mission_started":
        # IQ-4 §3.8: the mission and the court through the display
        # chokepoints — never "COURT NATION", never "PapalStates".
        from backend.display_names import MISSION_TYPE_DISPLAY
        raw_type = str(ctx.event.get("mission_type") or "")
        type_display = MISSION_TYPE_DISPLAY.get(
            raw_type, raw_type.replace("_", " ").title() or "a mission")
        return (f"Talleyrand sent to "
                f"{display_nation(ctx.event.get('target') or 'Unknown')}: "
                f"{type_display}.")

    if ctx.event_type == "diplomatic_mission_ended":
        # IQ-4 §3.8: how a mission ended — the log had only its start.
        turns = int(ctx.event.get("turns_active") or 0)
        dp_spent = int(ctx.event.get("dp_spent") or 0)
        expiry = ctx.event.get("expiry")
        if expiry is None and ctx.event.get("reason") == "duration" and ctx.event.get("turn"):
            # The intel grant runs five turns from the completing tick
            # (`_process_mission_effects`: `current_turn + 5`).
            expiry = int(ctx.event.get("turn")) + 5
        phrase = mission_reason_phrase(
            str(ctx.event.get("reason") or ""), ctx.event.get("regions_revealed"), expiry)
        return (f"Talleyrand's mission to "
                f"{display_nation(ctx.event.get('target') or 'Unknown')} ended: "
                f"{phrase} ({turns} turn{'' if turns == 1 else 's'}, "
                f"{dp_spent} DP).")

    if ctx.event_type == "diplomatic_proposal_sent":
        target = ctx.event.get("target", "Unknown")
        proposal_type = _proposal_label(ctx.event)
        return f"Proposal sent to {target} ({proposal_type})"

    # PL-27/PL-34: Proposal queue visibility events
    if ctx.event_type == "proposal_arrived":
        from backend.display_names import with_indefinite_article
        source = ctx.event.get("source", "Unknown")
        # IQ-7 review [14]/[31] (R10): a client's petition is a petition,
        # not "an a client's petition proposal (Client Petition)".
        if str(ctx.event.get("proposal_type") or "") == "client_petition":
            court = with_definite_article(display_nation(str(source)))
            return f"An envoy from {court} has arrived with a petition"
        proposal_type = _proposal_label(ctx.event)
        return (f"An envoy from {source} has arrived with "
                f"{with_indefinite_article(proposal_type)} proposal{_decision_reason_suffix(ctx.event)}")

    if ctx.event_type == "oathbreaker_posture_triggered":
        nation = ctx.event.get("nation", "Unknown")
        return f"{nation} is marked as an oathbreaker after repeated refusals"

    if ctx.event_type == "oathbreaker_posture_cleared":
        nation = ctx.event.get("nation", "Unknown")
        return f"{nation}'s oathbreaker posture has cleared"

    if ctx.event_type == "war_entry_ledger":
        aggressor = ctx.event.get("aggressor", "Unknown")
        target = ctx.event.get("target", "Unknown")
        entries = ctx.event.get("entries", []) or []
        return (
            f"War-entry ledger recorded for {aggressor} against {target} "
            f"({len(entries)} call path{'' if len(entries) == 1 else 's'})"
        )


    if ctx.event_type == "proposal_expired_unseen":
        source = ctx.event.get("source", "Unknown")
        proposal_type = _proposal_label(ctx.event)
        return f"{source}'s {proposal_type} envoy departed — proposal expired unanswered"

    if ctx.event_type == "proposal_dropped_overflow":
        source = ctx.event.get("source", "Unknown")
        proposal_type = _proposal_label(ctx.event)
        return f"{source}'s {proposal_type} envoy turned away — too many waiting"

    if ctx.event_type == "offer_lapsed":
        nation = ctx.event.get("nation", "Unknown")
        # IQ-7 review R8(e)/[31]: a lapsed petition carries the price the
        # lapse hook stamped on this row (`turn_manager`), never the generic
        # "offer lapsed unanswered" that every free lapse gets.
        if str(ctx.event.get("proposal_type") or "") == "client_petition":
            court = with_definite_article(display_nation(str(nation)), capitalize=True)
            petition = ctx.event.get("petition") if isinstance(ctx.event.get("petition"), dict) else {}
            outcome = str(petition.get("outcome") or "")
            if outcome == "withdrawn":
                return f"{court}'s petition lapsed unanswered — moot, nothing charged"
            if petition.get("penalty"):
                return (f"{court}'s petition lapsed unanswered — refused: "
                        f"loyalty {petition.get('loyalty_before')} → "
                        f"{petition.get('loyalty_after')}, bond "
                        f"{petition.get('relation_before')} → "
                        f"{petition.get('relation_after')}")
            if petition:
                return f"{court}'s petition lapsed unanswered — nothing charged"
            return f"{court}'s petition lapsed unanswered"
        # DDB-2: an ally's call to arms lapses as a refusal, at its price.
        if str(ctx.event.get("proposal_type") or "") == "call_to_arms":
            court = with_definite_article(display_nation(str(nation)), capitalize=True)
            call = ctx.event.get("call_to_arms") if isinstance(ctx.event.get("call_to_arms"), dict) else {}
            if call.get("penalty"):
                return f"{court}'s call to arms lapsed unanswered — refused, at its price"
            return f"{court}'s call to arms lapsed unanswered — nothing charged"
        proposal_type = _proposal_label(ctx.event)
        return f"{nation}'s {proposal_type} offer lapsed unanswered"

    if ctx.event_type == "garrison_placed":
        marshal = ctx.event.get("marshal", "Unknown")
        region = ctx.event.get("region", "unknown region")
        troops = ctx.event.get("troops", 0)
        # NPC-12: "ArchdukeCharles garrisoned Franche-Comte" (measured).
        return f"{humanize_entity_name(marshal)} garrisoned {region} ({troops:,} troops)"

    if ctx.event_type == "proposal_voided_by_coalition":
        target = ctx.event.get("target", "Unknown")
        return f"Envoy to {target} recalled — they joined the coalition"

    if ctx.event_type == "relationship_change":
        marshal = ctx.event.get("marshal", "Unknown")
        toward = ctx.event.get("toward", "Unknown")
        change = ctx.event.get("change", 0)
        new_label = ctx.event.get("new_label", "")
        sign = "+" if change > 0 else ""
        label_str = f" ({new_label})" if new_label else ""
        return f"{marshal} → {toward}: {sign}{change}{label_str}"

    # PL-14: Ultimatum events
    if ctx.event_type == "ultimatum_issued":
        target = ctx.event.get("target", "Unknown")
        return f"Ultimatum delivered to {target}"

    if ctx.event_type == "ultimatum_accepted":
        target = ctx.event.get("target", "Unknown")
        return f"{target} accepted our ultimatum — concessions extracted"

    if ctx.event_type == "ultimatum_rejected":
        target = ctx.event.get("target", "Unknown")
        return f"{target} rejected our ultimatum — casus belli granted"

    # Peace Deals BPH-A + BPH-D
    if ctx.event_type == "peace_ratified":
        proposer = ctx.event.get("proposer_nation", "Unknown")
        target = ctx.event.get("target_nation", "Unknown")
        transition = ctx.event.get("state_transition", "")
        if transition.endswith("_TO_ARMISTICE"):
            term_count = len(ctx.event.get("annotated_terms", []))
            suffix = f" ({term_count} term{'s' if term_count != 1 else ''})" if term_count else ""
            return f"Armistice ratified: {proposer} and {target}{suffix}"
        outcome = ctx.event.get("war_outcome", "")
        outcome_labels = {
            "french_victory": "French victory",
            "enemy_victory": "enemy victory",
            "stalemate": "stalemate",
            "white_peace": "white peace",
        }
        outcome_label = outcome_labels.get(outcome, "")
        parts = []
        gained = ctx.event.get("territory_gained", [])
        if gained:
            parts.append(f"gained {', '.join(gained)}")
        lost = ctx.event.get("territory_lost", [])
        if lost:
            parts.append(f"lost {', '.join(lost)}")
        gold_in = ctx.event.get("gold_received", 0)
        if gold_in:
            parts.append(f"+{gold_in} gold")
        gold_out = ctx.event.get("gold_paid", 0)
        if gold_out:
            parts.append(f"-{gold_out} gold")
        detail = " — " + ", ".join(parts) if parts else ""
        label = f" ({outcome_label})" if outcome_label else ""
        return f"Peace with {target}{label}{detail}"
    return _NEXT_STAGE


def _oneliner_unknown(ctx: OnelinerContext):
    """Stage 12 of `format_event_oneliner`: The fall-through: an unknown type
    is named, never dropped."""
    return f"Event: {ctx.event_type}"
