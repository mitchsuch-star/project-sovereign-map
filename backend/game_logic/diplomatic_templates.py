"""
Diplomatic Template Library — Phase 8 Session 3

Templates T1-T10 for Talleyrand's conversational diplomacy.
Templates T11-T27 are Session 4-6 scope.

Architecture:
  DIPLOMATIC_TEMPLATES keyed by (situation, game_bucket, specificity)
  Each template has text (with {slots}), options, and recommendation index.
"""

from typing import Any, Dict, Mapping, Optional

from backend.nation_config import get_player_nation


def _diplomat_name_from_record(record: Any) -> str:
    if record is None:
        return ""
    if isinstance(record, dict):
        return str(record.get("name", "") or "")
    return str(getattr(record, "name", "") or "")


def resolve_named_diplomat(
    speaker: str,
    nation: str,
    world: Any = None,
) -> str:
    """Resolve a presentation speaker to a named envoy or chancery fallback."""
    speaker_key = str(speaker or "").strip().lower()
    nation_name = str(nation or "").strip()

    if speaker_key == "system":
        return ""
    if speaker_key == "foreign_office":
        return f"The Chancery of {nation_name}" if nation_name else "The Chancery"
    if speaker_key == "talleyrand":
        return "Talleyrand"

    if speaker_key in {"envoy", "named_diplomat", "diplomat"}:
        diplomats = getattr(world, "diplomats", None) if world is not None else None
        if isinstance(diplomats, dict):
            resolved = _diplomat_name_from_record(diplomats.get(nation_name))
            if resolved:
                return resolved
            return f"The Chancery of {nation_name}" if nation_name else "The Chancery"

        from backend.models.diplomat import STARTING_DIPLOMATS
        resolved = _diplomat_name_from_record(STARTING_DIPLOMATS.get(nation_name))
        if resolved:
            return resolved
        return f"The Chancery of {nation_name}" if nation_name else "The Chancery"

    if speaker:
        return str(speaker)
    return f"The Chancery of {nation_name}" if nation_name else "The Chancery"

# ═══════ TEMPLATE LIBRARY ═══════
# Key: (intent_type, diplo_state, bucket_group)
# bucket_group: specific bucket name OR "any" for wildcard
# Lookup order: exact match → (intent, state, "any") → fallback

DIPLOMATIC_TEMPLATES = {
    # ══════════════════════════════════════════════
    # T1: VAGUE + WAR + winning_comfortably
    # ══════════════════════════════════════════════
    ("proposal_options", "WAR", "winning_comfortably"): {
        "text": (
            "Sire, we hold a commanding position against {target_nation}. "
            "Their armies falter and their courts grow anxious. I see several paths forward."
        ),
        "options": [
            {
                "label": "Generous peace",
                "description": "Offer magnanimous terms — build goodwill for the future.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Harsh demands",
                "description": "Press our advantage — demand territory and tribute.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Continue fighting",
                "description": "We can extract more concessions on the battlefield.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T2: VAGUE + WAR + losing_badly
    # ══════════════════════════════════════════════
    ("proposal_options", "WAR", "losing_badly"): {
        "text": (
            "Sire, our position against {target_nation} is... precarious. "
            "The battlefield has not favored us. We must act before things deteriorate further."
        ),
        "options": [
            {
                "label": "Sue for peace",
                "description": "Request peace on reasonable terms while we still can.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Offer concessions",
                "description": "Sweeten the deal with gold or territory to secure acceptance.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Stall",
                "description": "Buy time — request an armistice while we regroup.",
                "action": "execute_proposal",
                "proposal_type": "armistice",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T3: VAGUE + WAR + stalemate (also winning_slightly, losing_slightly)
    # ══════════════════════════════════════════════
    ("proposal_options", "WAR", "stalemate"): {
        "text": (
            "Sire, the war with {target_nation} is at a standstill. "
            "Neither side has won a decisive advantage on the battlefield."
        ),
        "options": [
            {
                "label": "Propose peace",
                "description": "End the bloodshed on balanced terms.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Press advantage",
                "description": "Continue the campaign — one victory could tip the balance.",
                "action": "dismiss",
            },
            {
                "label": "Wait",
                "description": "Hold position and see how events unfold.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T4: VAGUE + PEACE + hostile
    # ══════════════════════════════════════════════
    ("proposal_options", "PEACE", "hostile"): {
        "text": (
            "Sire, relations with {target_nation} are tense. "
            "There is deep mistrust between our courts. "
            "Tread carefully."
        ),
        "options": [
            {
                "label": "Improve relations",
                "description": "Send me to build bridges — a diplomatic mission.",
                "action": "start_mission",
                "terms": {"mission_type": "IMPROVE_RELATIONS"},
            },
            {
                "label": "Propose open borders",
                "description": "A small step — opening borders shows good faith.",
                "action": "execute_proposal",
                "proposal_type": "open_borders",
            },
            {
                "label": "Leave them be",
                "description": "Some wounds need time to heal.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T5: VAGUE + PEACE + friendly
    # ══════════════════════════════════════════════
    ("proposal_options", "PEACE", "friendly"): {
        "text": (
            "Sire, {target_nation} views us favorably. "
            "Their court speaks well of {player_nation}. "
            "The time may be ripe to deepen our ties."
        ),
        "options": [
            {
                "label": "Propose alliance",
                "description": "A full military alliance — mutual defense and cooperation.",
                "action": "execute_proposal",
                "proposal_type": "alliance",
            },
            {
                "label": "Non-aggression pact",
                "description": "A more cautious step — guarantee peace without military commitment.",
                "action": "execute_proposal",
                "proposal_type": "non_aggression",
            },
            {
                "label": "Vassalage",
                "description": "Bind them to our will as a vassal state.",
                "action": "execute_proposal",
                "proposal_type": "vassalage",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T6: MEDIUM + WAR (any bucket) — suggest specific terms
    # ══════════════════════════════════════════════
    ("proposal_confirm", "WAR", "any"): {
        "text": (
            "Sire, regarding the {proposal_type} proposal to {target_nation}, "
            "I have prepared terms appropriate to the current military situation."
        ),
        "options": [
            {
                "label": "Send as suggested",
                "description": "Send the proposal with my recommended terms.",
                "action": "execute_proposal",
            },
            {
                "label": "Harsher terms",
                "description": "Demand more — we can afford to push.",
                "action": "modify_harsh",
            },
            {
                "label": "More generous",
                "description": "Sweeten the offer to improve chances of acceptance.",
                "action": "modify_generous",
            },
            {
                "label": "Adjust terms",
                "description": "Build the offer step by step.",
                "action": "adjust_terms",
            },
            {
                "label": "Reconsider",
                "description": "Let me think about this.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T6b: MEDIUM + PEACE (any bucket)
    # ══════════════════════════════════════════════
    ("proposal_confirm", "PEACE", "any"): {
        "text": (
            "Sire, regarding the {proposal_type} proposal to {target_nation}, "
            "I have prepared terms that reflect the current diplomatic climate."
        ),
        "options": [
            {
                "label": "Send as suggested",
                "description": "Send the proposal with my recommended terms.",
                "action": "execute_proposal",
            },
            # BUGFIX (Bug 4B): These options were missing from PEACE template.
            # Without them, peacetime proposals only offered "Adjust terms" which
            # hit the terms_guidance dead-end in Godot. Must match WAR template (T6).
            # See BUGFIX_PLAN_PROPOSAL_FLOW.md.
            {
                "label": "Harsher terms",
                "description": "Demand more — press our advantage.",
                "action": "modify_harsh",
            },
            {
                "label": "More generous",
                "description": "Sweeten the offer to improve chances of acceptance.",
                "action": "modify_generous",
            },
            {
                "label": "Adjust terms",
                "description": "Build the offer step by step.",
                "action": "adjust_terms",
            },
            {
                "label": "Reconsider",
                "description": "Let me think about this.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T7: SPECIFIC + agree (Talleyrand agrees)
    # Fast-track: immediate execution with [Send][Reconsider]
    # ══════════════════════════════════════════════
    ("proposal_execute", "WAR", "any"): {
        "text": "At once, Sire. I shall deliver your {proposal_type} proposal to {target_nation}.",
        "options": [
            {
                "label": "Send",
                "description": "Dispatch Talleyrand immediately.",
                "action": "send",
            },
            {
                "label": "Reconsider",
                "description": "Wait — let me reconsider.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    ("proposal_execute", "PEACE", "any"): {
        "text": "At once, Sire. I shall present your {proposal_type} proposal to {target_nation}.",
        "options": [
            {
                "label": "Send",
                "description": "Dispatch Talleyrand immediately.",
                "action": "send",
            },
            {
                "label": "Reconsider",
                "description": "Wait — let me reconsider.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T8: SPECIFIC + object (Talleyrand disagrees)
    # STUB for Session 3 — always agrees (T7 used instead)
    # Real objection logic added in Session 6
    # ══════════════════════════════════════════════

    # ══════════════════════════════════════════════
    # T9: FEASIBILITY — handled by generate_feasibility_dialogue()
    # Template not needed here; logic is in diplomatic_dialogue.py
    # ══════════════════════════════════════════════

    # ══════════════════════════════════════════════
    # T10: MISSION START — handled by generate_mission_dialogue()
    # Template not needed here; logic is in diplomatic_dialogue.py
    # ══════════════════════════════════════════════

    # ══════════════════════════════════════════════════════════════
    # SESSION 4 TEMPLATES (T11-T20)
    # ══════════════════════════════════════════════════════════════

    # ══════════════════════════════════════════════
    # T11: INCOMING PROPOSAL — AI proposes to player
    # Used by deliver_ai_proposal() in ai_diplomacy.py
    # ══════════════════════════════════════════════
    ("incoming_proposal", "WAR", "any"): {
        "text": (
            "Sire, {target_diplomat} has arrived with a proposal from {target_nation}:\n\n"
            "  {proposal_summary}\n\n"
            "{talleyrand_assessment}"
        ),
        "options": [
            {
                "label": "Accept",
                "description": "Ratify the treaty as presented.",
                "action": "accept_ai_proposal",
            },
            {
                "label": "Reject",
                "description": "Send the envoy away empty-handed. (Relation -5)",
                "action": "reject_ai_proposal",
            },
            {
                "label": "Counter-offer",
                "description": "Propose modified terms. (Costs 1 DP)",
                "action": "counter_ai_proposal",
            },
        ],
        "recommendation": 0,
    },

    ("incoming_proposal", "PEACE", "any"): {
        "text": (
            "Sire, {target_diplomat} has arrived with a proposal from {target_nation}:\n\n"
            "  {proposal_summary}\n\n"
            "{talleyrand_assessment}"
        ),
        "options": [
            {
                "label": "Accept",
                "description": "Ratify the proposal.",
                "action": "accept_ai_proposal",
            },
            {
                "label": "Reject",
                "description": "Decline. (Relation -5)",
                "action": "reject_ai_proposal",
            },
            {
                "label": "Counter-offer",
                "description": "Suggest modified terms. (Costs 1 DP)",
                "action": "counter_ai_proposal",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T12: PROPOSAL WITH TALLEYRAND ASSESSMENT
    # When Talleyrand adds his own spin on AI proposal
    # ══════════════════════════════════════════════
    ("incoming_proposal_assessed", "WAR", "any"): {
        "text": (
            "Sire, a proposal from {target_nation}:\n\n"
            "  {proposal_summary}\n\n"
            "My assessment: {talleyrand_assessment}\n\n"
            "The Diplomatic Ledger (D key) has the precise figures."
        ),
        "options": [
            {
                "label": "Accept",
                "description": "Accept the terms.",
                "action": "accept_ai_proposal",
            },
            {
                "label": "Reject",
                "description": "Refuse. (Relation -5)",
                "action": "reject_ai_proposal",
            },
            {
                "label": "Counter-offer",
                "description": "Propose modifications. (1 DP)",
                "action": "counter_ai_proposal",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T13: ADVISORY — Nation status assessment
    # Used by diplomatic_advisory.py
    # ══════════════════════════════════════════════
    ("advisory", "WAR", "any"): {
        "text": (
            "You ask about {target_nation}, Sire? Let me assess the situation.\n\n"
            "{target_nation} is currently at war with {player_nation}. "
            "The campaign continues and passions run deep.\n\n"
            "The Diplomatic Ledger (D key) has the precise figures."
        ),
        "options": [
            {
                "label": "What should we do?",
                "description": "Ask Talleyrand for a recommendation.",
                "action": "expand_to_proposal",
            },
            {
                "label": "Thank you",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    ("advisory", "PEACE", "any"): {
        "text": (
            "You ask about {target_nation}, Sire?\n\n"
            "{target_nation} is at peace with {player_nation}. "
            "The diplomatic situation is as one might expect between our courts.\n\n"
            "The Diplomatic Ledger (D key) has the precise figures."
        ),
        "options": [
            {
                "label": "What should we do?",
                "description": "Ask Talleyrand for a recommendation.",
                "action": "expand_to_proposal",
            },
            {
                "label": "Thank you",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T14: ADVISORY — Threat assessment (multi-nation)
    # ══════════════════════════════════════════════
    ("advisory_threat", "any", "any"): {
        "text": (
            "An assessment of the diplomatic landscape, Sire.\n\n"
            "{threat_analysis}\n\n"
            "{recommendation}"
        ),
        "options": [
            {
                "label": "What should we do?",
                "description": "Ask for a specific recommendation.",
                "action": "expand_to_proposal",
            },
            {
                "label": "Thank you",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T15: ADVISORY — Recommendation
    # ══════════════════════════════════════════════
    ("advisory_recommendation", "any", "any"): {
        "text": (
            "{recommendation_text}\n\n"
            "The Diplomatic Ledger (D key) has the precise figures, Sire."
        ),
        "options": [
            {
                "label": "Do it",
                "description": "Proceed with Talleyrand's suggestion.",
                "action": "execute_proposal",
            },
            {
                "label": "Tell me more",
                "description": "Elaborate on the recommendation.",
                "action": "expand_to_proposal",
            },
            {
                "label": "Not now",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T16: COUNTER-OFFER PRESENTATION
    # When M3 algorithm generates a counter-offer
    # ══════════════════════════════════════════════
    ("counter_offer", "WAR", "any"): {
        "text": (
            "Sire, I have modified the terms. {target_nation} may find these more acceptable:\n\n"
            "  {counter_summary}\n\n"
            "My assessment: this counter-offer has improved chances of acceptance."
        ),
        "options": [
            {
                "label": "Accept counter",
                "description": "Accept these modified terms.",
                "action": "accept_ai_proposal",
            },
            {
                "label": "Reject",
                "description": "Reject the entire negotiation.",
                "action": "reject_ai_proposal",
            },
        ],
        "recommendation": 0,
    },

    ("counter_offer", "PEACE", "any"): {
        "text": (
            "Sire, I have adjusted the terms for {target_nation}:\n\n"
            "  {counter_summary}\n\n"
            "These modified terms should be more palatable."
        ),
        "options": [
            {
                "label": "Accept counter",
                "description": "Accept the modified terms.",
                "action": "accept_ai_proposal",
            },
            {
                "label": "Reject",
                "description": "Reject entirely.",
                "action": "reject_ai_proposal",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T17: CONFLICT ALERT — Alliance conflict detected
    # ══════════════════════════════════════════════
    ("conflict_alert", "any", "any"): {
        "text": (
            "Sire, a complication. Accepting this proposal would conflict with "
            "our existing obligations.\n\n"
            "{conflict_description}\n\n"
            "{target_nation} must choose which alliance to honor."
        ),
        "options": [
            {
                "label": "Accept anyway",
                "description": "Accept — the conflicting party must decide.",
                "action": "accept_with_conflict",
            },
            {
                "label": "Reject",
                "description": "Reject to avoid the conflict.",
                "action": "reject_ai_proposal",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T18: PROPOSAL REJECTED RESPONSE
    # AI's response to player rejecting their proposal
    # ══════════════════════════════════════════════
    ("proposal_rejected", "WAR", "any"): {
        "text": (
            "{target_diplomat} receives your rejection with "
            "{rejection_reaction}. Relations with {target_nation} have cooled."
        ),
        "options": [
            {
                "label": "So be it",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    ("proposal_rejected", "PEACE", "any"): {
        "text": (
            "{target_diplomat} accepts your decision with "
            "{rejection_reaction}. Relations have shifted."
        ),
        "options": [
            {
                "label": "Understood",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T19: FEASIBILITY UPDATE
    # Updated feasibility after game state changes
    # ══════════════════════════════════════════════
    ("feasibility_update", "any", "any"): {
        "text": (
            "Sire, the diplomatic landscape has shifted. My previous assessment "
            "of {target_nation} requires revision.\n\n"
            "{updated_assessment}"
        ),
        "options": [
            {
                "label": "Pursue this",
                "description": "Act on the new assessment.",
                "action": "execute_proposal",
            },
            {
                "label": "Noted",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T20: PROACTIVE DISPATCH ENTRY
    # Talleyrand's observation for Morning Dispatch
    # ══════════════════════════════════════════════
    ("proactive_suggestion", "any", "any"): {
        "text": (
            "A diplomatic observation, Sire: {observation}\n\n"
            "{suggested_action_text}"
        ),
        "options": [
            {
                "label": "Ask Talleyrand to elaborate",
                "description": "Open a diplomatic conversation.",
                "action": "elaborate",
            },
            {
                "label": "Dismiss",
                "description": "Noted.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },
    # ══════════════════════════════════════════════════════════════
    # SESSION 6 TEMPLATES (T21-T27)
    # ══════════════════════════════════════════════════════════════

    # ══════════════════════════════════════════════
    # T21: PRE-PROPOSAL OBJECTION — MILD
    # Flavor text, no blocking — Talleyrand grumbles
    # ══════════════════════════════════════════════
    ("pre_proposal_objection_mild", "any", "any"): {
        "text": (
            "{objection_text}\n\n"
            "Nevertheless, I shall carry out your wishes, Sire."
        ),
        "options": [
            {
                "label": "Send as ordered",
                "description": "Dispatch Talleyrand with your original terms.",
                "action": "send",
            },
            {
                "label": "Reconsider",
                "description": "Perhaps Talleyrand has a point.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T22: SABOTAGE CONFRONTATION
    # What was ordered vs what was delivered + reasoning
    # ══════════════════════════════════════════════
    ("sabotage_confrontation", "any", "any"): {
        "text": (
            "Berthier's agents report that the proposal delivered to "
            "{target_nation} was not precisely as you ordered.\n\n"
            "You ordered: {original_summary}\n"
            "Talleyrand sent: {modified_summary}\n\n"
            "Talleyrand: \"{sabotage_reasoning}\""
        ),
        "options": [
            {
                "label": "Confront",
                "description": "Authority +5, cooldown 5 turns.",
                "action": "confront_sabotage",
            },
            {
                "label": "Overlook",
                "description": "Authority -3. Talleyrand gains confidence.",
                "action": "overlook_sabotage",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T23: SABOTAGE CONFRONTATION — OVERLOOK AFTERMATH
    # Confirmation after overlooking sabotage
    # ══════════════════════════════════════════════
    ("sabotage_confrontation_overlook", "any", "any"): {
        "text": (
            "You choose to overlook the discrepancy. Talleyrand inclines "
            "his head — a small acknowledgment that his judgment was trusted."
        ),
        "options": [
            {
                "label": "Understood",
                "description": "Dismiss.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T24: ENEMY RESPONSE — HAWK (Castlereagh, Hardenberg)
    # Grudging accept, demanding counter, contemptuous reject
    # ══════════════════════════════════════════════
    ("enemy_response_hawk", "any", "accept"): {
        "text": (
            "{target_diplomat} receives your terms with barely concealed displeasure. "
            "\"We accept — for now. Do not mistake pragmatism for weakness.\""
        ),
        "options": [
            {"label": "Noted", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_hawk", "any", "counter"): {
        "text": (
            "{target_diplomat} slams the table. \"These terms are insulting. "
            "Here is what {target_nation} will accept — and nothing less.\""
        ),
        "options": [
            {"label": "Consider counter", "description": "Review the counter-offer.", "action": "review_counter"},
            {"label": "Reject", "description": "Refuse.", "action": "reject_ai_proposal"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_hawk", "any", "reject"): {
        "text": (
            "{target_diplomat}'s contempt is palpable. \"You waste our time "
            "with this? {target_nation} will remember this insult.\""
        ),
        "options": [
            {"label": "So be it", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T25: ENEMY RESPONSE — SCHEMER (Metternich)
    # Calculating accept, probing counter, deflecting reject
    # ══════════════════════════════════════════════
    ("enemy_response_schemer", "any", "accept"): {
        "text": (
            "{target_diplomat} smiles — never a reassuring sign. "
            "\"An acceptable arrangement. {target_nation} agrees... with interest.\""
        ),
        "options": [
            {"label": "Noted", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_schemer", "any", "counter"): {
        "text": (
            "{target_diplomat} examines the terms at length. \"Interesting. "
            "But perhaps we could adjust... here, and here. "
            "A small modification that benefits us both.\""
        ),
        "options": [
            {"label": "Consider counter", "description": "Review the counter-offer.", "action": "review_counter"},
            {"label": "Reject", "description": "Refuse.", "action": "reject_ai_proposal"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_schemer", "any", "reject"): {
        "text": (
            "{target_diplomat} merely raises an eyebrow. \"A pity. "
            "But doors that close today may open tomorrow. "
            "{target_nation} is patient.\""
        ),
        "options": [
            {"label": "Understood", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T26: ENEMY RESPONSE — DOVE (Einsiedel / future diplomats)
    # Grateful accept, apologetic counter, regretful reject
    # ══════════════════════════════════════════════
    ("enemy_response_dove", "any", "accept"): {
        "text": (
            "{target_diplomat} visibly relaxes. \"This is most welcome. "
            "{target_nation} accepts with gratitude and hopes for lasting peace.\""
        ),
        "options": [
            {"label": "Good", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_dove", "any", "counter"): {
        "text": (
            "{target_diplomat} wrings his hands. \"We appreciate the gesture, "
            "truly. But our court requires... adjustments. "
            "Please, consider this modest counter-proposal.\""
        ),
        "options": [
            {"label": "Consider counter", "description": "Review the counter-offer.", "action": "review_counter"},
            {"label": "Reject", "description": "Refuse.", "action": "reject_ai_proposal"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_dove", "any", "reject"): {
        "text": (
            "{target_diplomat} looks pained. \"I am sorry, truly. "
            "{target_nation} cannot accept these terms. "
            "Perhaps... in time... we might try again?\""
        ),
        "options": [
            {"label": "Perhaps", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T27: ENEMY RESPONSE — LOYALIST (generic formal)
    # Formal accept, formal counter, formal reject
    # ══════════════════════════════════════════════
    ("enemy_response_loyalist", "any", "accept"): {
        "text": (
            "{target_diplomat} delivers the response formally. "
            "\"{target_nation} accepts the terms as presented.\""
        ),
        "options": [
            {"label": "Noted", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_loyalist", "any", "counter"): {
        "text": (
            "{target_diplomat} presents the response with precision. "
            "\"{target_nation} proposes the following modifications to the terms.\""
        ),
        "options": [
            {"label": "Consider counter", "description": "Review the counter-offer.", "action": "review_counter"},
            {"label": "Reject", "description": "Refuse.", "action": "reject_ai_proposal"},
        ],
        "recommendation": 0,
    },
    ("enemy_response_loyalist", "any", "reject"): {
        "text": (
            "{target_diplomat} delivers the rejection without emotion. "
            "\"{target_nation} declines the proposed terms.\""
        ),
        "options": [
            {"label": "Understood", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    },
    "settlement_open_war_detail_recovery_talleyrand": (
        "Sire, I will keep the draft intact and return us to the live war "
        "detail for {war_label}."
    ),
    "settlement_open_history_recovery_talleyrand": (
        "Sire, this war has ended; the settlement record now belongs in "
        "the diplomatic ledger."
    ),
    "settlement_no_alternative_route_chancery": (
        "This settlement cannot currently be recovered from the existing "
        "surfaces. Close the review and reassess the war next turn."
    ),
}

# ═══════ COALITION TEMPLATES (T28-T34, Session 7) ═══════
# Template categories for coalition events. These use coalition-specific slot variables.

COALITION_TEMPLATES = {
    # T28: Coalition murmur (threat 40-59)
    "coalition_murmur": {
        "text": (
            "Sire, at threat level {threat_level}, the courts of {hostile_nations} "
            "grow restless. Our recent successes alarm them."
        ),
        "priority": "normal",
    },
    # T29: Coalition brewing (threat 60+)
    "coalition_brewing": {
        "text": (
            "Your Majesty, I must speak with the utmost urgency. {qualifying_nations} "
            "are forming a coalition against us. We have {turns_remaining} turns to prevent it. "
            "Shall I approach the weakest member with terms?"
        ),
        "priority": "high",
    },
    # T30: Coalition declared
    "coalition_declared": {
        "text": (
            "The {coalition_name} has declared against us. {leader} leads "
            "{member_list}. All of Europe stands against you, Sire."
        ),
        "priority": "critical",
    },
    # T31: Coalition member weakening
    "coalition_member_weak": {
        "text": (
            "{nation}'s resolve is faltering. Their war exhaustion has reached "
            "{war_exhaustion}. They may be amenable to separate terms."
        ),
        "priority": "normal",
    },
    # T32: Coalition split advice
    "coalition_advice_split": {
        "text": (
            "I recommend approaching {target_nation} with generous peace terms. "
            "They are the weakest link in the coalition. A separate peace would "
            "fracture the alliance."
        ),
        "priority": "normal",
    },
    # T33: Coalition dissolved
    "coalition_dissolved": {
        "text": (
            "The {coalition_name} has collapsed. A moment of respite, Sire. "
            "But I counsel moderation — harsh demands breed the next coalition."
        ),
        "priority": "normal",
    },
    # T34: Coalition harsh warning
    "coalition_harsh_warning": {
        "text": (
            "Sire, these terms will add {threat_increase} to our threat level. "
            "At the current rate, another coalition may form within turns. "
            "I urge restraint."
        ),
        "priority": "normal",
    },
}


SETTLEMENT_VOICE_TEMPLATES: Dict[str, str] = {
    "settlement_advisory_common_peace_talleyrand": (
        "Sire, the settlement of {war_label} is not a curtain call; it is an "
        "accounting. {standing_summary} must be read beside {contribution_summary}, "
        "and the largest political cost remains {top_blocker}."
    ),
    "settlement_advisory_defensive_talleyrand": (
        "Sire, a defensive peace is judged by what it preserves. Returning "
        "{restored_claim} steadies the coalition, while {limited_concession} "
        "buys quiet without dressing necessity as conquest."
    ),
    "settlement_acceptance_castlereagh": (
        "His Majesty's Government accepts the settlement of {war_label}. "
        "London records the terms and reserves its judgment on the consequences."
    ),
    "settlement_acceptance_hardenberg": (
        "Prussia accepts the settlement of {war_label}. Hardenberg notes what "
        "has been conceded, and what honor will require us to remember."
    ),
    "settlement_acceptance_metternich": (
        "Vienna accepts the settlement of {war_label}. Metternich observes that "
        "the arrangement is sufficient for today, which is not the same as final."
    ),
    "settlement_acceptance_einsiedel": (
        "Saxony accepts the settlement of {war_label}, respectfully and with "
        "relief. Einsiedel asks only that small courts may now breathe."
    ),
    "settlement_rejection_castlereagh": (
        "London cannot accept the settlement of {war_label}. The obstacle is "
        "{top_blocker}; His Majesty's Government will not pretend otherwise."
    ),
    "settlement_rejection_hardenberg": (
        "Prussia rejects the settlement of {war_label}. {top_blocker} is not a "
        "detail to be filed away; it is an insult to Prussian standing."
    ),
    "settlement_rejection_metternich": (
        "Vienna declines the settlement of {war_label}. The difficulty, if one "
        "must name it plainly, is {top_blocker}; Austria prefers clarity before ink."
    ),
    "settlement_rejection_einsiedel": (
        "Saxony cannot accept the settlement of {war_label}. Einsiedel begs "
        "France to understand that {top_blocker} leaves us no safe answer."
    ),
    "settlement_sold_out_by_leader_castlereagh": (
        "London observes that {leader} purchased peace with {victim}. Such an "
        "arrangement will be remembered in the next coalition."
    ),
    "settlement_sold_out_by_leader_hardenberg": (
        "Hardenberg names the matter plainly: {leader} sold out {victim}. "
        "Prussia does not forget who treats an ally as payment."
    ),
    "settlement_sold_out_by_leader_metternich": (
        "Vienna notes that {leader} found {victim} a convenient price. "
        "Metternich will adjust the ledger accordingly."
    ),
    "settlement_sold_out_by_leader_einsiedel": (
        "Einsiedel records, with regret, that {leader} has left {victim} to bear "
        "the cost. Small courts understand that lesson too well."
    ),
    "settlement_rewarded_ally_castlereagh": (
        "London acknowledges that {beneficiary} received {reward}. The reward "
        "is material; the obligation it creates is political."
    ),
    "settlement_rewarded_ally_hardenberg": (
        "Hardenberg accepts {reward} for {beneficiary} as recognition, not charity. "
        "Prussia values a settlement that honors contribution."
    ),
    "settlement_rewarded_ally_metternich": (
        "Metternich observes that {beneficiary} has been granted {reward}. "
        "A favor so precisely placed is rarely accidental."
    ),
    "settlement_rewarded_ally_einsiedel": (
        "Einsiedel thanks France for {reward} to {beneficiary}. It is a modest "
        "security perhaps, but for Saxony security is never modest."
    ),
    "settlement_excluded_ally_castlereagh": (
        "London notes that {excluded_ally} contributed {contribution_summary} "
        "and received no seat in the settlement. The omission is legible."
    ),
    "settlement_excluded_ally_hardenberg": (
        "Hardenberg will not dress this as oversight. {excluded_ally} gave "
        "{contribution_summary}, and the settlement answered with silence."
    ),
    "settlement_excluded_ally_metternich": (
        "Vienna has noticed that {excluded_ally}'s {contribution_summary} did "
        "not survive into the articles. Such absences have weight."
    ),
    "settlement_excluded_ally_einsiedel": (
        "Einsiedel asks, respectfully, how {excluded_ally} should explain "
        "{contribution_summary} when the treaty grants nothing in return."
    ),
    "settlement_advisory_common_peace_serial_peace_weapon": (
        "Sire, peeling {departing_enemy} from {war_label} weakens {remaining_leader}, "
        "but it also teaches the remaining courts that separate peace has a price."
    ),
    # Settlement aftermath digest (spec §11.6 line 1288). Voiced in
    # Talleyrand register so the rolled-up overflow line keeps the
    # settlement family's narrative voice rather than reading as system
    # log text. Spec §16.1 line 1602.
    "settlement_aftermath_digest_talleyrand": (
        "Sire, {hidden_count} further courts have entered the {war_label} "
        "settlement into their ledgers — quieter reactions, but each one "
        "remembered."
    ),
    # SC-19 settlement voice families (Settlement UI Cleanup G2-Slice-5).
    # Each family is bound to a specific trigger and surface; using any
    # of these on the wrong surface fails the SC-19 row's required test.
    #
    # Live review heading — replaces the raw verdict f-string at the
    # settlement_confirm popup heading. Talleyrand voice for outgoing
    # review where France authored the package.
    "settlement_review_heading_talleyrand": (
        "Sire, the settlement of {war_label} stands ready for ratification. "
        "Acceptance reads as {acceptance_band}; the largest pressure remains "
        "{top_blocker}."
    ),
    # Foreign-court / observer settlement voice for fog-visible
    # foreign-only settlements where France is neither proposer nor
    # accepting member. SC-19 amendment: chancery voice, not Talleyrand
    # authorship.
    "settlement_observed_foreign_court_chancery": (
        "Foreign Office records the settlement of {war_label}. The court of "
        "{accepting_leader} reviews the terms; we observe rather than author."
    ),
    # Blocked ratification banner — shown when fresh acceptance verdict
    # is reject/blocked or hard stops exist and the Ratify Settlement
    # option is absent from the dialogue. SC-15b/SC-3 amendment: must
    # not use "Will they accept?" framing.
    "settlement_blocked_for_ratification_talleyrand": (
        "Sire, the settlement of {war_label} cannot be ratified now: "
        "{top_blocker}. Revise terms or stand down before pressing further."
    ),
    # Rescore-after-staging banner — fresh ratification scoring changed
    # an accepted staged package into rejected/below-threshold/hard-stop.
    "settlement_rescored_after_staging_talleyrand": (
        "Sire, the situation has shifted since this settlement was staged. "
        "Acceptance now reads {acceptance_band}; review the terms again "
        "before ratifying."
    ),
    # Discard-confirm prompt (SC-2) — Back Out from a non-empty authored
    # draft asks the player to confirm before clearing terms.
    "settlement_discard_confirm_talleyrand": (
        "Sire, the authored terms for {war_label} will be discarded if we "
        "back out now. Shall I keep the draft, or strike it from the table?"
    ),
    # Cross-war collision (SC-26) — a second settlement entry was
    # attempted while a different war already holds the active dialogue.
    "settlement_collision_active_review_talleyrand": (
        "Sire, the settlement of {active_war_label} is already on the table; "
        "resolve it before opening a separate review for {blocked_war_label}."
    ),
    # Reopen-cap exhausted (SC-14b) — attempt 4 for the same
    # (war_id, turn) — pin the player to the choose-from-war-detail
    # escape rather than another reopen loop.
    "settlement_reopen_cap_exhausted_talleyrand": (
        "Sire, this settlement of {war_label} cannot be reopened again — "
        "choose the war from war detail and stage afresh."
    ),
    # SC-29 / G2-Slice-7 pair-scoped peace substitute CTAs. The rejected
    # settlement popup may surface these only when the selected target
    # pair is eligible under `evaluate_pair_peace_substitute_eligibility`.
    # Talleyrand frames the substitute as a pair-scoped fallback, not as a
    # repeated settlement attempt.
    "settlement_seek_bilateral_peace_instead_talleyrand": (
        "Sire, since the larger settlement of {war_label} cannot ratify, "
        "I shall open a separate bilateral peace with {target_nation}; "
        "the other hostile pairs remain at war until they are addressed "
        "in turn."
    ),
    "settlement_seek_armistice_instead_talleyrand": (
        "Sire, an armistice with {target_nation} buys quiet on that "
        "front while {war_label} continues elsewhere; it does not end "
        "the war, but it does end the bleeding."
    ),
    # SC-31 / G2-Slice-8 Voice Bible §16.1 surrender / dependency families.
    # Surrender preset is a structured, labeled action — Talleyrand frames
    # it as deliberate concession, not collapse — and the foreign-court
    # reactions answer the dependency consequence (loss of sovereignty,
    # lord assimilation, Continental System pull) rather than treating it
    # as a generic peace acceptance.
    "settlement_surrender_preset_authored_talleyrand": (
        "Sire, the surrender draft for {war_label} is set: peace, and "
        "{vassal_kind} of {proposer_leader} under {accepting_leader}. "
        "It costs us our sovereignty; it ends the war."
    ),
    "settlement_surrender_preset_blocked_talleyrand": (
        "Sire, surrender terms cannot be drafted now: {top_blocker}. "
        "Author concessions or hold the line until the field changes."
    ),
    "settlement_dependency_ratified_talleyrand": (
        "Sire, the settlement of {war_label} binds {vassal_nation} "
        "to {lord_nation} as a {vassal_kind}. The crown survives; "
        "the court answers to {lord_nation} now."
    ),
    "settlement_dependency_acceptance_castlereagh": (
        "His Majesty's Government accepts the settlement of {war_label} "
        "with {vassal_nation} under {lord_nation}. London notes the "
        "submission and will measure {lord_nation} by what it does next."
    ),
    "settlement_dependency_acceptance_hardenberg": (
        "Prussia accepts the settlement of {war_label}. Hardenberg records "
        "that {vassal_nation} now answers to {lord_nation}, and that "
        "Prussian standing must adjust accordingly."
    ),
    "settlement_dependency_acceptance_metternich": (
        "Vienna accepts the settlement of {war_label}. Metternich "
        "observes that {vassal_nation}'s submission to {lord_nation} "
        "rearranges Europe quietly; quiet does not mean settled."
    ),
    "settlement_dependency_acceptance_einsiedel": (
        "Saxony accepts the settlement of {war_label}. Einsiedel hopes, "
        "with care, that {lord_nation} remembers small courts when "
        "{vassal_nation} kneels."
    ),
    "settlement_dependency_rejection_castlereagh": (
        "London cannot accept the settlement of {war_label}. The "
        "subjection of {vassal_nation} to {lord_nation} is more than "
        "a treaty matter; {top_blocker} forbids it."
    ),
    "settlement_dependency_rejection_hardenberg": (
        "Prussia rejects the settlement of {war_label}. Hardenberg "
        "names the obstacle plainly: {top_blocker}. {vassal_nation} "
        "cannot be handed to {lord_nation} under those circumstances."
    ),
    "settlement_dependency_rejection_metternich": (
        "Vienna declines the settlement of {war_label}. The difficulty "
        "is {top_blocker}; Austria will not consent to {vassal_nation} "
        "becoming a vassal of {lord_nation} on those terms."
    ),
    "settlement_dependency_rejection_einsiedel": (
        "Saxony cannot accept the settlement of {war_label}. Einsiedel "
        "begs {lord_nation} to understand that {top_blocker} leaves "
        "{vassal_nation} no safe answer."
    ),
    "settlement_liberation_ratified_talleyrand": (
        "Sire, the settlement of {war_label} frees {vassal_nation} from "
        "{former_lord} into a defensive alliance with {liberator}. The "
        "court of {vassal_nation} will remember who opened the door."
    ),
    # SC-33 / G2-Slice-9 recurring gold payment Voice Bible families.
    # Authored / ratified / completed split mirrors the surrender preset
    # authored / ratified pattern so the player hears a deliberate
    # framing when the obligation is drafted, when it ratifies, and
    # when it concludes.
    "settlement_recurring_gold_authored_talleyrand": (
        "Sire, the draft commits {payer} to {amount_per_turn} gold per "
        "turn to {recipient} for {turns} turns ({projected_total} gold "
        "in total). Recurring payments steady the peace; they also "
        "tie the treasury for years."
    ),
    "settlement_recurring_gold_ratified_talleyrand": (
        "Sire, the settlement of {war_label} obliges {payer} to send "
        "{amount_per_turn} gold per turn to {recipient} for {turns} "
        "turns. The first installment leaves the treasury next turn."
    ),
    "settlement_recurring_gold_completed_talleyrand": (
        "Sire, the recurring obligation from {payer} to {recipient} "
        "for {war_label} is fulfilled — {total_amount} gold has changed "
        "hands. The clause closes itself."
    ),
    # SC-5 reversal / Slice G1 commit 2 incoming-offer Voice Bible §16.1
    # families. Talleyrand frames the offer for the player's reading;
    # each foreign court's voice is what the proposer-side leader puts
    # on the dispatch. The committed copy distinguishes incoming
    # acceptance framing ("they are asking for") from outgoing review
    # framing ("we are asking for").
    "settlement_incoming_offer_arrival_talleyrand": (
        "Sire, {proposer_leader} has dispatched a settlement of "
        "{war_label}. They ask {amount} gold to close the war; the "
        "table is theirs to set, the signature is ours to give or "
        "withhold."
    ),
    "settlement_incoming_offer_arrival_castlereagh": (
        "His Majesty's Government offers terms for {war_label}. London "
        "asks {amount} gold and a return to peace; the price is set, "
        "and London is not in the habit of revising figures lightly."
    ),
    "settlement_incoming_offer_arrival_hardenberg": (
        "Prussia proposes a settlement of {war_label}. Hardenberg names "
        "{amount} gold as the close; what Prussia gives by signing is "
        "quiet, and what Prussia keeps is the lesson."
    ),
    "settlement_incoming_offer_arrival_metternich": (
        "Vienna submits terms for {war_label}. Metternich asks {amount} "
        "gold; the figure is modest by Vienna's reckoning and the "
        "alternative is another season of campaign."
    ),
    "settlement_incoming_offer_arrival_einsiedel": (
        "Saxony forwards a settlement of {war_label}. Einsiedel asks "
        "{amount} gold, respectfully — small courts cannot afford long "
        "wars, and the offer is shaped accordingly."
    ),
    "settlement_incoming_offer_arrival_chancery": (
        "The chancery of {proposer_leader} has forwarded a settlement "
        "of {war_label}. The terms ask {amount} gold; the court awaits "
        "France's answer."
    ),
    # Request Revision is the accepting-side counter authoring route.
    # Talleyrand explains that we are opening the editor seeded from the
    # exact offered package so the player can revise before sending a
    # counter; this must NOT reuse outgoing "Revise Terms" framing.
    "settlement_incoming_offer_request_revision_talleyrand": (
        "Sire, I shall open the offered terms for {war_label} for our "
        "own hand. We answer the dispatch from {proposer_leader} with a "
        "counter draft, not silence."
    ),
    # Blocked recovery for the accepting-side review (player accepted the
    # offer but it cannot ratify in its current form). Talleyrand names
    # the blocker and points the player at Request Revision rather than
    # outgoing Revise Terms copy.
    "settlement_incoming_offer_blocked_recovery_talleyrand": (
        "Sire, the offer from {proposer_leader} cannot ratify as it "
        "stands: {top_blocker}. Request a revision and we answer with "
        "our own draft instead of refusing without a reply."
    ),
    # Cross-court observer copy when a non-French court learns that a
    # settlement was blocked. Spec §SC-19 amendment + §SC-30 Voice Bible
    # cross-court rule require chancery voice (not Talleyrand) so the
    # observed-from-outside reading does not pretend French authorship.
    "settlement_blocked_for_ratification_observer": (
        "The chancery records the draft of {war_label} as blocked. "
        "{top_blocker} leaves no court with signatures to exchange."
    ),
    # G2-Slice-W1 white-peace heading families. Authored as part of the
    # May 24, 2026 audit punch list Tier 2: `build_settlement_confirm_dialogue`
    # already calls `resolve_settlement_voice_line` for these two keys at
    # the white_peace branches of the heading text logic, but the templates
    # were missing — the resolver therefore returned empty and the popup
    # fell through to inline f-string fallbacks. Authoring them here brings
    # the white-peace heading under Voice Bible §16.1 alongside the
    # blocked / ratifiable / observer variants above.
    "settlement_white_peace_heading_talleyrand": (
        "Sire, the white peace for {war_label} is ready: no terms exchanged, "
        "no map redrawn — only the war ends. Ratify and the field falls quiet."
    ),
    "settlement_white_peace_blocked_talleyrand": (
        "Sire, a white peace for {war_label} cannot be sealed as it stands: "
        "{top_blocker}. Author terms or hold until the field shifts."
    ),
    # Losing-side concession-baseline Voice Bible families. Authored as
    # part of the May 24, 2026 audit punch list Tier 2 so the concession
    # baseline reasoning the popup already renders is registered Voice
    # Bible copy rather than a hard-coded f-string in
    # `_format_concession_reasoning(...)`. `{summary}` is the formatted
    # one-line concession action the helper already constructs ("pay X
    # gold", "cede Y", or both joined). `{accepting_leader}` echoes the
    # foreign-court target so the line reads as deliberate authoring
    # rather than as a generic acceptance hint.
    "settlement_concession_authored_talleyrand": (
        "Sire, the concession draft — {summary} — would lift acceptance "
        "toward {accepting_leader}. It is what the field asks of us."
    ),
    # Losing-side pressure-explanation family. Authored alongside the
    # concession-baseline family so the dialogue can surface a Talleyrand
    # reading of why the player is on the losing side (top negative
    # pressure component + accepting leader), not only the baseline
    # reasoning. Surfaced on the dialogue as `losing_side_pressure_voice`
    # when `losing_for_concession_baseline=True` and resolved with
    # `{war_label}`, `{top_pressure_label}`, and `{accepting_leader}`.
    "settlement_losing_side_pressure_explained_talleyrand": (
        "Sire, the pressure on {war_label} reads against us — {top_pressure_label} "
        "is the loudest blocker, and {accepting_leader} is the court whose "
        "acceptance must shift before terms move."
    ),
}


def get_settlement_voice_template(template_key: str) -> Optional[str]:
    """Return committed Imperial Settlement copy by exact template key."""
    return SETTLEMENT_VOICE_TEMPLATES.get(str(template_key or ""))


def resolve_settlement_voice_line(template_key: str, **slots: Any) -> str:
    """Resolve a committed settlement voice template with caller-supplied slots."""
    template = get_settlement_voice_template(template_key)
    if not template:
        return ""
    safe_slots = {key: str(value) for key, value in slots.items()}
    return template.format_map(_MissingSettlementSlot(safe_slots))


class _MissingSettlementSlot(dict):
    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"


def resolve_coalition_template(category: str, world, **kwargs) -> Optional[str]:
    """Resolve a coalition template with slot variables.

    Accepts keyword arguments for coalition-specific slots like
    threat_level, hostile_nations, qualifying_nations, etc.
    """
    template = COALITION_TEMPLATES.get(category)
    if not template:
        return None

    text = template["text"]
    slots = {k: str(v) for k, v in kwargs.items()}

    # Auto-fill from world state
    slots.setdefault("threat_level", str(int(getattr(world, 'threat_level', 0))))

    try:
        return text.format_map(_SafeFormatMap(slots))
    except (KeyError, ValueError):
        return text


# ═══════ FALLBACK TEMPLATES ═══════
# Used when no exact template match is found

FALLBACK_TEMPLATES = {
    "proposal_options": {
        "text": (
            "Sire, how shall I approach {target_nation}? "
            "I await your instructions."
        ),
        "options": [
            {
                "label": "Propose peace",
                "description": "Seek a peaceful resolution.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Improve relations",
                "description": "Send me on a diplomatic mission.",
                "action": "start_mission",
                "terms": {"mission_type": "IMPROVE_RELATIONS"},
            },
            {
                "label": "Dismiss",
                "description": "Not now.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },
    "proposal_confirm": {
        "text": (
            "Sire, I shall prepare a {proposal_type} proposal for {target_nation}. "
            "Shall I proceed with standard terms?"
        ),
        "options": [
            {
                "label": "Proceed",
                "description": "Send with suggested terms.",
                "action": "execute_proposal",
            },
            # BUGFIX (Bug 4B): Modify options were missing from fallback template.
            # See BUGFIX_PLAN_PROPOSAL_FLOW.md.
            {
                "label": "Harsher terms",
                "description": "Demand more — press our advantage.",
                "action": "modify_harsh",
            },
            {
                "label": "More generous",
                "description": "Sweeten the offer to improve chances of acceptance.",
                "action": "modify_generous",
            },
            {
                "label": "Adjust terms",
                "description": "Build the offer step by step.",
                "action": "adjust_terms",
            },
            {
                "label": "Reconsider",
                "description": "Let me think about this.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },
    "proposal_execute": {
        "text": "At once, Sire. I shall deliver your proposal to {target_nation}.",
        "options": [
            {
                "label": "Send",
                "description": "Dispatch immediately.",
                "action": "send",
            },
            {
                "label": "Reconsider",
                "description": "Wait.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },
}


def get_template(intent_type: str, diplo_state: str, bucket: str,
                 proposal_type: Optional[str] = None) -> Dict:
    """Look up the best matching template.

    Lookup order:
    1. Exact match: (intent_type, diplo_state, bucket)
    2. Wildcard bucket: (intent_type, diplo_state, "any")
    3. Similar buckets for WAR states
    4. Fallback by intent_type
    """
    # 1. Exact match
    key = (intent_type, diplo_state, bucket)
    if key in DIPLOMATIC_TEMPLATES:
        template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
        if proposal_type:
            template["_proposal_type"] = proposal_type
        return template

    # 2. Wildcard bucket
    key = (intent_type, diplo_state, "any")
    if key in DIPLOMATIC_TEMPLATES:
        template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
        if proposal_type:
            template["_proposal_type"] = proposal_type
        return template

    # 3. Similar buckets for WAR
    if diplo_state == "WAR":
        similar_map = {
            "winning_slightly": "winning_comfortably",
            "losing_slightly": "losing_badly",
        }
        similar = similar_map.get(bucket)
        if similar:
            key = (intent_type, diplo_state, similar)
            if key in DIPLOMATIC_TEMPLATES:
                template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
                if proposal_type:
                    template["_proposal_type"] = proposal_type
                return template

    # 4. Neutral bucket for PEACE
    if diplo_state == "PEACE" and bucket == "neutral":
        # Try hostile template as fallback for neutral
        key = (intent_type, diplo_state, "hostile")
        if key in DIPLOMATIC_TEMPLATES:
            template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
            if proposal_type:
                template["_proposal_type"] = proposal_type
            return template

    # 5. Fallback
    if intent_type in FALLBACK_TEMPLATES:
        template = _deep_copy_template(FALLBACK_TEMPLATES[intent_type])
        if proposal_type:
            template["_proposal_type"] = proposal_type
        return template

    # Ultimate fallback
    return {
        "text": "Sire, I await your instructions regarding {target_nation}.",
        "options": [
            {"label": "Dismiss", "description": "Never mind.", "action": "dismiss"},
        ],
        "recommendation": 0,
    }


def _deep_copy_template(template: Dict) -> Dict:
    """Deep copy a template dict (simple structures only)."""
    result = {
        "text": template["text"],
        "options": [opt.copy() for opt in template.get("options", [])],
        "recommendation": template.get("recommendation", 0),
    }
    # Copy terms dicts in options
    for i, opt in enumerate(result["options"]):
        if "terms" in template.get("options", [])[i]:
            result["options"][i]["terms"] = template["options"][i]["terms"].copy()
    return result


def resolve_template_text(text: str, world, target_nation: Optional[str] = None) -> str:
    """Resolve {slot_name} placeholders in template text.

    Golden Rule #2: ALL numeric slots are int() wrapped.
    """
    if not text:
        return text

    slots = {}

    if target_nation:
        slots["target_nation"] = target_nation
        slots["player_nation"] = get_player_nation(world)

        # Get diplomat for target nation
        diplomats = getattr(world, 'diplomats', {})
        target_diplomat = diplomats.get(target_nation)
        slots["target_diplomat"] = target_diplomat.name if target_diplomat else "their diplomat"

        # Numeric values
        player_nation = get_player_nation(world)
        diplo_key = world._make_diplo_key(player_nation, target_nation)
        relation = int(world.nation_relations.get(diplo_key, 0))
        state = world.get_diplomatic_state(player_nation, target_nation)
        # R38: Only show war score when nations are at war
        if state == "WAR":
            from backend.game_logic.diplomacy import get_war_score_for
            slots["war_score"] = str(int(get_war_score_for(world, player_nation, target_nation)))
        else:
            slots["war_score"] = "N/A"
        slots["relation"] = str(relation)
        slots["current_state"] = state
        slots["dp_cost"] = "1"  # Default, overridden per-context

        # R82: rejection_reaction based on relation
        if relation < -40:
            slots["rejection_reaction"] = "cold fury"
        elif relation < 0:
            slots["rejection_reaction"] = "barely concealed displeasure"
        else:
            slots["rejection_reaction"] = "diplomatic composure"

    # Generic slots
    slots["dp"] = str(int(getattr(world, 'diplomatic_points', 0)))

    # Coalition slots (Session 7)
    slots["threat_level"] = str(int(getattr(world, 'threat_level', 0)))
    coalition = getattr(world, 'active_coalition', None)
    if coalition:
        slots["coalition_name"] = coalition.get("name", "The Coalition")
        slots["leader"] = coalition.get("leader", "")
        slots["member_list"] = ", ".join(coalition.get("members", []))

    # Resolve — use .get for safety
    try:
        return text.format_map(_SafeFormatMap(slots))
    except (KeyError, ValueError):
        return text


class _SafeFormatMap(dict):
    """Format map that returns {key} for missing keys instead of raising."""
    def __missing__(self, key):
        return "{" + key + "}"


def resolve_template_text_with_type(text: str, world, target_nation: Optional[str],
                                     proposal_type: Optional[str] = None) -> str:
    """Resolve template text with proposal_type slot."""
    result = resolve_template_text(text, world, target_nation)
    if proposal_type and "{proposal_type}" in result:
        result = result.replace("{proposal_type}", proposal_type)
    return result


# ═══════ NATION DESIRE PROFILES ═══════

NATION_DESIRE_PROFILES = {
    "Prussia": {
        "covets_regions": ["Saxony", "Dresden"],
        "values_gold": "low",
        "values_territory": "high",
        "values_ap": "medium",
        "diplomatic_lever": "ambition",
        "weakness": "overextension",
    },
    "Austria": {
        "covets_regions": ["Bavaria", "Tyrol", "Bohemia"],
        "values_gold": "medium",
        "values_territory": "high",
        "values_ap": "low",
        "diplomatic_lever": "stability",
        "weakness": "pride",
    },
    "Britain": {
        "covets_regions": ["Netherlands", "Hanover"],
        "values_gold": "low",
        "values_territory": "medium",
        "values_ap": "medium",
        "diplomatic_lever": "trade",
        "weakness": "isolation",
    },
    "Saxony": {
        "covets_regions": ["Saxony", "Dresden"],
        "values_gold": "high",
        "values_territory": "low",
        "values_ap": "high",
        "diplomatic_lever": "survival",
        "weakness": "desperation",
    },
}


# ═══════ TALLEYRAND COMMENTARY ═══════

TALLEYRAND_COMMENTARY = {
    # --- Prussia ---
    ("Prussia", "coveted_territory_offered"): "Saxony is the prize Hardenberg dreams of. Offering it buys more than gold ever could.",
    ("Prussia", "gold_useless"): "Prussia's treasury is adequate — they desire land, not coin. I've weighted the offer accordingly.",
    ("Prussia", "border_territory_demanded"): "The Rhineland gives us a buffer against Prussian ambition. A wise demand.",
    ("Prussia", "dominant_terms"): "Hardenberg will bristle, but Prussia is in no position to refuse. Press the advantage.",
    ("Prussia", "neutral_deal"): "A straightforward arrangement. Hardenberg is practical — he'll weigh the terms honestly.",
    ("Prussia", "friendly_deal"): "Hardenberg is well-disposed toward us. A generous arrangement cements the friendship.",
    ("Prussia", "hostile_deal"): "Hardenberg bristles at our very name. Only substantial concessions will move him.",
    # --- Austria ---
    ("Austria", "coveted_territory_offered"): "Bavaria is Austria's natural sphere. Returning it costs us little and buys Metternich's goodwill.",
    ("Austria", "gold_for_poor"): "Vienna's treasury grows thin after years of war. Gold per turn steadies their hand — and their loyalty.",
    ("Austria", "desperate_terms"): "Metternich is a schemer — even generous terms may not satisfy him. But we must try.",
    ("Austria", "neutral_deal"): "Metternich will study every clause for hidden advantage. I've kept the terms clean.",
    ("Austria", "friendly_deal"): "Metternich sees advantage in cooperation. Let us reward his pragmatism.",
    ("Austria", "hostile_deal"): "Metternich is hostile but calculating. A sufficiently attractive offer may still tempt him.",
    # --- Britain ---
    ("Britain", "gold_useless"): "Britain's coffers overflow — offering gold insults the British cabinet. Territory speaks louder.",
    ("Britain", "coveted_territory_offered"): "The Netherlands secures Britain's continental foothold. The British chancery values it above gold.",
    ("Britain", "dominant_terms"): "Britain's continental army is small. Their cabinet knows its position — it will accept reasonable terms.",
    ("Britain", "desperate_terms"): "The British chancery drives a hard bargain. I've included everything short of Paris itself.",
    ("Britain", "neutral_deal"): "An island nation with continental ambitions. This arrangement serves both parties' interests.",
    ("Britain", "friendly_deal"): "The British chancery is amenable, for once. Best to lock in terms before the mood shifts.",
    ("Britain", "hostile_deal"): "The British cabinet despises us openly. Only overwhelming terms have any chance.",
    # --- Saxony ---
    ("Saxony", "gold_for_poor"): "Saxony's treasury is nearly empty. Even modest gold buys Einsiedel's eternal gratitude.",
    ("Saxony", "protection_offered"): "Saxony lives in fear of Prussian annexation. A French guarantee is worth more than gold to them.",
    ("Saxony", "ap_for_weak"): "An extra action each turn transforms a small nation's capabilities. Einsiedel will understand this.",
    ("Saxony", "coveted_territory_offered"): "Einsiedel cares only for the survival of his homeland. Territorial guarantees speak loudest.",
    ("Saxony", "neutral_deal"): "A small nation, easily satisfied. Einsiedel will accept any arrangement that preserves Saxony.",
    ("Saxony", "friendly_deal"): "Einsiedel is a loyal friend. A gentle deal strengthens bonds cheaply.",
    ("Saxony", "hostile_deal"): "Even gentle Einsiedel has turned cold. We must offer more than usual.",
    # --- Coveted unavailable (France doesn't control what they want) ---
    ("Prussia", "coveted_unavailable"): "Hardenberg dreams of Saxony, but it is not yet ours to offer. Conquer it first, Sire, and he will come to the table eagerly.",
    ("Austria", "coveted_unavailable"): "Metternich yearns for Bavaria, but we do not hold it. Secure it first, and these negotiations transform entirely.",
    ("Britain", "coveted_unavailable"): "Britain values its continental footholds, but they are beyond our gift at present. We must work with what we have.",
    ("Saxony", "coveted_unavailable"): "Einsiedel's homeland is not ours to return. Until we hold it, we cannot offer what matters most to him.",
    ("_default", "coveted_unavailable"): "They desire territory we do not yet control. Conquer it first, Sire, and our bargaining position transforms.",
    # --- Defaults ---
    ("_default", "coveted_territory_offered"): "I've included territory they particularly desire. It should tip the balance in our favor.",
    ("_default", "gold_for_poor"): "Their treasury is strained. Gold speaks loudly to those who lack it.",
    ("_default", "gold_useless"): "Gold would be wasted here — I've substituted something they actually value.",
    ("_default", "smart_cession"): "I've selected our least valuable border territory for cession. We lose little of strategic worth.",
    ("_default", "desperate_terms"): "We are not in a position to be choosy, Sire. I've assembled the most persuasive package possible.",
    ("_default", "dominant_terms"): "They have little choice but to accept. I've kept the demands firm but not humiliating.",
    ("_default", "neutral_deal"): "Standard terms, Sire. Neither generous nor harsh — a foundation for negotiation.",
    ("_default", "protection_offered"): "A guarantee of protection costs us nothing but obligation. For them, it means survival.",
    ("_default", "ap_for_weak"): "An extra action per turn is transformative for a smaller power. They will value this highly.",
    ("_default", "border_territory_demanded"): "Border territory provides strategic depth. A prudent demand.",
    ("_default", "friendly_deal"): "They are well-disposed. I've proposed fair terms that reward the friendship.",
    ("_default", "cautious_deal"): "Relations are tepid. I've balanced the terms to avoid giving offense.",
    ("_default", "hostile_deal"): "Relations are poor. I've included extra incentives to overcome their reluctance.",
    # --- Modified terms (harsh/generous iterations) ---
    ("Prussia", "modified_harsh"): "Hardenberg's pride is wounded, but Prussia cannot refuse. Press the advantage, Sire.",
    ("Prussia", "modified_generous"): "Generosity toward Prussia costs us little. Hardenberg will remember this kindness.",
    ("Austria", "modified_harsh"): "Metternich will protest, but his options narrow with each demand. Hold firm.",
    ("Austria", "modified_generous"): "Metternich appreciates magnanimity — it allows him to save face at court.",
    ("Britain", "modified_harsh"): "Britain's island position gives its cabinet options we cannot eliminate. Harsh terms risk outright rejection.",
    ("Britain", "modified_generous"): "Even the British chancery may warm to terms this favorable. Britain values pragmatism.",
    ("Saxony", "modified_harsh"): "Poor Einsiedel has little left to give. These demands may break Saxony entirely.",
    ("Saxony", "modified_generous"): "Einsiedel will weep with gratitude. Such generosity buys a loyal vassal, Sire.",
    ("_default", "modified_harsh"): "I have drafted more demanding terms, Sire. They will not accept lightly.",
    ("_default", "modified_generous"): "I have drafted more generous terms, Sire. Such magnanimity should improve acceptance.",
}


# ═══════ ULTIMATUM TERMS GENERATION (PL-14 §2) ═══════

def generate_ultimatum_terms(target_nation: str, world) -> Dict:
    """Generate coercive demands based on military advantage.

    Returns: {"demands": [...], "sweeteners": [], "clauses": [], "type": "ultimatum_demand"}
    No AP demands (requires war_score > 80, impossible in peacetime).
    No sweeteners ever — ultimatums are pure extortion.
    No proposal_type key — uses "type" only (PL-13 lesson).
    """
    demands = []
    player = get_player_nation(world)

    # ── Gold demand: capped at 50% of target income (AM-15.7: use get_nation_regions) ──
    target_income = 0
    target_gold = 0
    regions = getattr(world, 'regions', {})
    for rname in world.get_nation_regions(target_nation):
        region = regions.get(rname)
        if region:
            target_income += getattr(region, 'income_value', 0)
    target_gold = getattr(world, 'nation_gold', {}).get(target_nation, 0)

    if target_income > 0:
        gold_demand = min(300, max(50, int(target_income * 0.5)))
        demands.append({"type": "gold_per_turn", "value": int(gold_demand)})
    elif target_gold > 0:
        gold_lump = min(500, max(50, int(target_gold * 0.3)))
        demands.append({"type": "gold_lump", "value": int(gold_lump)})

    # ── Territory demand: coveted regions if France controls adjacent (AM-15.7) ──
    france_regions = set(world.get_nation_regions(player))
    target_regions = set(world.get_nation_regions(target_nation))

    # Calculate military superiority
    marshals = getattr(world, 'marshals', {})
    player_strength = sum(m.strength for m in marshals.values() if m.nation == player and m.strength > 0)
    target_strength = sum(m.strength for m in marshals.values() if m.nation == target_nation and m.strength > 0)
    has_military_superiority = player_strength > target_strength * 1.2

    if has_military_superiority and len(target_regions) > 2:
        # Prefer regions adjacent to France-controlled territory
        adjacent_targets = []
        for t_name in target_regions:
            t_region = regions.get(t_name)
            if not t_region:
                continue
            # Skip capitals
            from backend.models.region import NATION_CAPITALS
            if t_name == NATION_CAPITALS.get(target_nation):
                continue
            connections = getattr(t_region, 'adjacent_regions', [])
            if any(c in france_regions for c in connections):
                adjacent_targets.append(t_name)
        if adjacent_targets:
            demands.append({"type": "territory_cede", "value": 1, "regions": adjacent_targets[:1]})

    # ── Manpower demand: proportional to troop advantage ──
    troop_advantage = player_strength - target_strength
    if troop_advantage > 5000:
        manpower_demand = min(5000, int(troop_advantage * 0.1))
        if manpower_demand >= 500:
            demands.append({"type": "manpower_infantry", "value": int(manpower_demand)})

    # Ensure at least one demand (gold floor)
    if not demands:
        demands.append({"type": "gold_lump", "value": 100})

    return {
        "demands": demands,
        "sweeteners": [],
        "clauses": [],
        "type": "ultimatum_demand",
    }


# ═══════ SUGGESTED TERMS GENERATION ═══════

def generate_suggested_terms(target_nation: str, proposal_type: str, world) -> Dict:
    """Generate smart treaty terms based on game state AND nation-specific knowledge.

    5-stage pipeline:
      1. Base terms (war_score/relation thresholds)
      2. Nation-specific clause injection (coveted territory, gold calibration, protection)
      3. Economic reality check (cap offers/demands to feasible levels)
      4. Talleyrand commentary (explain WHY these terms)
      5. Return
    """
    from backend.game_logic.diplomacy import get_war_score_for, SPECIAL_BONUSES
    from backend.models.region import NATION_CAPITALS

    player_nation = get_player_nation(world)
    war_score = get_war_score_for(world, player_nation, target_nation)

    # --- Stage 1: Base terms ---
    terms = _build_base_terms(target_nation, proposal_type, world)

    # --- Stage 2: Nation-specific injection ---
    context_tags = []
    profile = NATION_DESIRE_PROFILES.get(target_nation, {})

    # 2a. Territory sweeteners: prefer coveted regions
    has_territory_sweetener = any(
        s.get("type") == "territory_cede" for s in terms.get("sweeteners", []))
    coveted = [r for r in profile.get("covets_regions", [])
               if r in world.get_nation_regions(player_nation)]
    target_holds_all_coveted = all(
        r in world.get_nation_regions(target_nation)
        for r in profile.get("covets_regions", [])
    ) if profile.get("covets_regions") else True

    # Check if target covets regions France doesn't control (hint to conquer first)
    all_coveted = profile.get("covets_regions", [])
    coveted_unavailable = [r for r in all_coveted
                           if r not in world.get_nation_regions(player_nation)
                           and r not in world.get_nation_regions(target_nation)]

    if has_territory_sweetener or (coveted and war_score < 0 and not target_holds_all_coveted):
        if coveted:
            terms["sweeteners"] = [s for s in terms.get("sweeteners", [])
                                   if s.get("type") != "territory_cede"]
            terms["sweeteners"].append(
                {"type": "territory_cede", "value": 1, "regions": [coveted[0]]})
            bonus_clause = f"territory_{coveted[0].lower()}"
            terms.setdefault("clauses", [])
            if bonus_clause not in terms["clauses"]:
                terms["clauses"].append(bonus_clause)
            context_tags.append("coveted_territory_offered")
        elif has_territory_sweetener:
            candidates = rank_cession_candidates(world, player_nation, target_nation)
            if candidates:
                terms["sweeteners"] = [s for s in terms["sweeteners"]
                                       if s.get("type") != "territory_cede"]
                terms["sweeteners"].append(
                    {"type": "territory_cede", "value": 1, "regions": [candidates[0][0]]})
                context_tags.append("smart_cession")
    elif coveted_unavailable and not coveted:
        # France doesn't control what they want — hint to conquer it first
        context_tags.append("coveted_unavailable")

    # 2b. Territory demands: prefer border regions
    has_territory_demand = any(
        d.get("type") in ("territory_cede", "territory")
        for d in terms.get("demands", []))
    target_regions = world.get_nation_regions(target_nation)
    player_regions = world.get_nation_regions(player_nation)
    border = []
    for rname in target_regions:
        region = world.regions.get(rname)
        if region and any(adj in player_regions for adj in region.adjacent_regions):
            if rname != NATION_CAPITALS.get(target_nation):
                border.append(rname)

    if has_territory_demand or (war_score > 30 and border):
        if border:
            terms["demands"] = [d for d in terms.get("demands", [])
                                if d.get("type") not in ("territory_cede", "territory")]
            terms["demands"].append(
                {"type": "territory_cede", "value": 1, "regions": [border[0]]})
            context_tags.append("border_territory_demanded")

    # 2c. Gold calibration — only tag when gold sweeteners actually exist
    gold_pref = profile.get("values_gold", "medium")
    has_gold_sweetener = any("gold" in s.get("type", "") for s in terms.get("sweeteners", []))
    if gold_pref == "high":
        for s in terms.get("sweeteners", []):
            if "gold" in s.get("type", ""):
                s["value"] = int(s["value"] * 1.5)
        if has_gold_sweetener:
            context_tags.append("gold_for_poor")
    elif gold_pref == "low":
        # Bug 4 fix: Remove gold sweeteners when nation doesn't value gold
        # AND alternative sweeteners (territory) exist. If gold is the only
        # sweetener, keep it at 50% to avoid empty offers.
        non_gold = [s for s in terms.get("sweeteners", [])
                    if "gold" not in s.get("type", "")]
        if has_gold_sweetener and non_gold:
            # Alternative sweeteners exist — drop gold entirely
            terms["sweeteners"] = non_gold
            context_tags.append("gold_useless")
        elif has_gold_sweetener:
            # Gold is the only sweetener — reduce but keep
            for s in terms.get("sweeteners", []):
                if "gold" in s.get("type", ""):
                    s["value"] = int(s["value"] * 0.5)

    # 2d. Protection clause for survival-driven nations
    if (profile.get("diplomatic_lever") == "survival"
            and proposal_type in ("peace", "defensive_alliance", "alliance")):
        if "protection_promised" in SPECIAL_BONUSES.get(target_nation, {}):
            if "protection_promised" not in terms.get("clauses", []):
                terms.setdefault("clauses", []).append("protection_promised")
                context_tags.append("protection_offered")

    # 2e. AP for nations that value extra actions
    ap_pref = profile.get("values_ap", "medium")
    if ap_pref == "high" and war_score < -30:
        if not any(s.get("type") == "ap_per_turn" for s in terms.get("sweeteners", [])):
            terms["sweeteners"].append({"type": "ap_per_turn", "value": 1})
            context_tags.append("ap_for_weak")

    # --- Stage 3: Economic reality check ---
    _validate_economic_feasibility(terms, target_nation, world, war_score=war_score)

    # --- Stage 4: Commentary ---
    if not context_tags:
        if war_score < -30:
            context_tags.append("desperate_terms")
        elif war_score > 30:
            context_tags.append("dominant_terms")
        else:
            from backend.game_logic.diplomatic_dialogue import get_game_bucket
            bucket = get_game_bucket(target_nation, world)
            if bucket == "friendly":
                context_tags.append("friendly_deal")
            elif bucket == "hostile":
                context_tags.append("hostile_deal")
            elif bucket == "neutral":
                context_tags.append("cautious_deal")
            else:
                context_tags.append("neutral_deal")

    commentary = _get_smart_commentary(target_nation, context_tags[0])

    # PL-25: Append situational flavor from recent events (AM-25.5/25.6)
    flavor = _get_situational_flavor(target_nation, world)
    if flavor and flavor != commentary:
        commentary = f"{commentary}\n\n{flavor}"
    terms["talleyrand_commentary"] = commentary

    # --- Stage 5: Return ---
    return terms


def _build_base_terms(target_nation: str, proposal_type: str, world, deterministic: bool = False) -> Dict:
    """Build base treaty terms using war_score/relation thresholds.

    Args:
        target_nation: Target nation name
        proposal_type: Type of proposal
        world: WorldState
        deterministic: If True, skip jitter (for testing). Default False.
    """
    from backend.game_logic.diplomacy import get_war_score_for
    player_nation = get_player_nation(world)
    diplo_key = world._make_diplo_key(player_nation, target_nation)
    relation = world.nation_relations.get(diplo_key, 0)
    war_score = get_war_score_for(world, player_nation, target_nation)

    terms = {
        "type": proposal_type,
        "proposal_type": proposal_type,  # PL-13-D: normalize dual-key at source
        "proposer_nation": player_nation,
        "target_nation": target_nation,
        "sweeteners": [],
        "demands": [],
        "clauses": [],
    }

    if proposal_type == "peace":
        # Include open borders if relation isn't too hostile
        if relation > -20:
            terms["clauses"].append("open_borders")

        # If winning, demand gold/turn proportional to advantage
        if war_score > 20:
            gold_demand = min(300, war_score * 5)
            terms["demands"].append({"type": "gold_per_turn", "value": int(gold_demand)})
        elif war_score < -20 or relation < -50:
            # If losing or deeply hostile, offer gold to sweeten
            gold_factor = max(abs(war_score) * 3, abs(relation))
            gold_offer = min(200, max(50, int(gold_factor)))
            terms["sweeteners"].append({"type": "gold_per_turn", "value": int(gold_offer)})

            # R147: Offer territory cession when losing
            # Non-capital regions first; capital only as desperate last resort
            from backend.models.region import NATION_CAPITALS
            player_capital = NATION_CAPITALS.get(player_nation, "Paris")
            player_regions = world.get_nation_regions(player_nation)
            non_capital = [r for r in player_regions if r != player_capital]
            max_cede = 1 if war_score >= -40 else 2
            for region in non_capital[:max_cede]:
                terms["sweeteners"].append({"type": "territory_cede", "value": 1, "regions": [region]})
            # Capital offered only as desperate last resort (war_score < -60)
            if war_score < -60 and len(non_capital) < max_cede:
                terms["sweeteners"].append({"type": "territory_cede", "value": 1, "regions": [player_capital]})

            # R148: Offer manpower when losing badly
            if war_score < -30:
                player_pool = getattr(world, 'manpower_pools', {}).get(player_nation, {}).get("infantry", 0)
                offer_amount = min(5000, int(player_pool * 0.25))
                if offer_amount >= 1000:
                    terms["sweeteners"].append({"type": "manpower_infantry", "value": int(offer_amount)})

            # R148: Offer AP when desperate
            if war_score < -50:
                terms["sweeteners"].append({"type": "ap_per_turn", "value": 1})

    elif proposal_type == "defensive_alliance":
        # Defensive alliance: mutual defense, open borders
        terms["clauses"].append("open_borders")

    elif proposal_type == "alliance":
        # Alliance: minimal terms, mutual defense
        terms["clauses"].append("open_borders")

    elif proposal_type == "vassalage":
        # Vassalage: tribute based on target economy
        target_gold = world.nation_gold.get(target_nation, 500)
        tribute = max(100, int(target_gold * 0.15))
        terms["demands"].append({"type": "gold_per_turn", "value": int(tribute)})

    elif proposal_type == "open_borders":
        terms["clauses"].append("open_borders")

    elif proposal_type == "non_aggression":
        pass  # No special terms needed

    elif proposal_type in ("armistice", "armistice_losing", "armistice_winning"):
        # Armistice is a temporary ceasefire
        terms["type"] = "armistice_losing" if war_score < 0 else "armistice_winning"

        # R150: Sweeten armistice when losing OR when relation is very hostile
        # Hostile nations won't accept bare armistice even at neutral war score
        needs_sweetener = war_score < -10 or relation < -50
        if needs_sweetener:
            gold_amount = max(200, min(2000, max(abs(war_score), abs(relation)) * 20))
            terms["sweeteners"].append({"type": "gold_lump", "value": int(gold_amount)})

        if war_score < -30:
            # Offer 1 territory as armistice sweetener (non-capital first)
            from backend.models.region import NATION_CAPITALS
            player_capital = NATION_CAPITALS.get(player_nation, "Paris")
            player_regions = world.get_nation_regions(player_nation)
            non_capital = [r for r in player_regions if r != player_capital]
            if non_capital:
                terms["sweeteners"].append({"type": "territory_cede", "value": 1, "regions": [non_capital[0]]})
            elif war_score < -60:
                # Capital only as desperate last resort
                terms["sweeteners"].append({"type": "territory_cede", "value": 1, "regions": [player_capital]})

    # PL-25: Amount jitter ±20% on gold/manpower values (demands + sweeteners)
    if not deterministic:
        import random
        jitter = random.uniform(0.8, 1.2)
    else:
        jitter = 1.0
    _JITTER_TYPES = {"gold_per_turn", "gold_lump", "manpower_infantry", "manpower_cavalry", "manpower_artillery"}
    for d in terms.get("demands", []):
        if d.get("type") in _JITTER_TYPES:
            d["value"] = int(d["value"] * jitter)
    for s in terms.get("sweeteners", []):
        if s.get("type") in _JITTER_TYPES:
            s["value"] = int(s["value"] * jitter)

    return terms


def _validate_economic_feasibility(terms, target_nation, world, war_score=0):
    """Cap gold/territory offers and demands to economically feasible levels."""
    player_nation = get_player_nation(world)
    player_gold = world.nation_gold.get(player_nation, 0)
    player_income = world.calculate_turn_income(player_nation).get("income", 0)
    target_income = world.calculate_turn_income(target_nation).get("income", 0)
    gold_cap_pct = 0.50 if war_score < -30 else 0.25

    for s in terms.get("sweeteners", []):
        if s.get("type") == "gold_lump":
            s["value"] = int(min(s["value"], max(50, int(player_gold * gold_cap_pct))))
        elif s.get("type") == "gold_per_turn":
            s["value"] = int(min(s["value"], max(25, int(player_income * 0.2))))
    for d in terms.get("demands", []):
        if d.get("type") == "gold_per_turn":
            d["value"] = int(min(d["value"], max(25, int(target_income * 0.5))))
    # Force all values to int (Godot crashes on floats)
    for s in terms.get("sweeteners", []):
        if "value" in s:
            s["value"] = int(s["value"])
    for d in terms.get("demands", []):
        if "value" in d:
            d["value"] = int(d["value"])


def _get_smart_commentary(target_nation, context_tag):
    """Look up Talleyrand's commentary for a nation + context tag."""
    key = (target_nation, context_tag)
    if key in TALLEYRAND_COMMENTARY:
        return TALLEYRAND_COMMENTARY[key]
    default_key = ("_default", context_tag)
    if default_key in TALLEYRAND_COMMENTARY:
        return TALLEYRAND_COMMENTARY[default_key]
    return "I have assembled terms befitting the situation, Sire."


def _get_situational_flavor(target_nation: str, world) -> str:
    """PL-25: Generate situational flavor line from recent events.

    Uses event API (AM-25.6: NOT battle_history which is a zombie field).
    Safe access throughout (AM-25.5: no crash on turn 1 / empty events).

    Returns:
        Flavor string, or default TALLEYRAND_COMMENTARY fallthrough
    """
    player_nation = get_player_nation(world)

    # Check recent battles (last 3 turns) — AM-25.6: use event API
    recent_events = world.get_events_since_turn(max(1, world.current_turn - 3)) if hasattr(world, 'get_events_since_turn') else []
    recent_battles = [e for e in recent_events if e.get("type") == "battle"] if recent_events else []

    # Victory over target nation
    if recent_battles:
        for battle in reversed(recent_battles):
            att_nation = battle.get("attacker_nation", "")
            def_nation = battle.get("defender_nation", "")
            outcome = battle.get("outcome", "")
            if def_nation == target_nation and att_nation == player_nation and outcome in ("attacker_victory", "decisive_attacker_victory"):
                return "They are weakened, Sire. Our recent victory gives us the advantage at the table."
            if att_nation == target_nation and def_nation == player_nation and outcome in ("defender_victory", "decisive_defender_victory"):
                return "They are weakened, Sire. Their failed attack leaves them in no position to refuse."

    # Check diplomatic history for recent alliance breaks
    diplo_history = getattr(world, 'diplomatic_history', [])
    if diplo_history:
        for event in reversed(diplo_history[-10:]):
            if event.get("type") == "alliance_broken" and target_nation in (event.get("nation_a"), event.get("nation_b")):
                return "They stand alone. A generous offer now buys loyalty cheaply."

    # High coalition threat
    if hasattr(world, 'coalition_threat'):
        threat = getattr(world, 'coalition_threat', 0)
        if threat > 60:
            return "The courts watch us, Sire. Moderation may serve us better than force."

    # No situational event → return empty (base commentary already covers the default)
    return ""


def get_desire_profile_nudge_bias(target_nation: str) -> Dict:
    """PL-25 AM-25.9: Get desire profile bias for pen nudge targeting.

    Returns multipliers that influence which demand the pen nudge targets.
    Higher multiplier = more likely to be targeted for softening.

    Returns:
        Dict with 'territory_mult', 'nudge_override_type', 'sweetener_bias'
    """
    profile = NATION_DESIRE_PROFILES.get(target_nation, {})
    result = {
        "territory_mult": 1.0,
        "nudge_override_type": None,  # If set, this type becomes nudge target
        "sweetener_bias": None,       # Preferred sweetener type
    }

    # AM-25.9: Territory-valuing nations → territory demands get 1.5x harshness
    if profile.get("values_territory") == "high":
        result["territory_mult"] = 1.5

    # AM-25.9: Weakness → nudge override
    weakness = profile.get("weakness", "")
    if weakness == "overextension":
        result["nudge_override_type"] = "territory_cede"
    elif weakness == "isolation":
        # Diplomatic demands — AP is closest proxy
        result["nudge_override_type"] = "ap_per_turn"

    # AM-25.9: Sweetener bias from diplomatic_lever
    lever = profile.get("diplomatic_lever", "")
    if lever == "trade":
        result["sweetener_bias"] = "gold_per_turn"
    elif lever == "stability":
        result["sweetener_bias"] = "non_aggression"

    return result


# ═══════ CONVERSATIONAL TERMS GUIDANCE ═══════

def rank_cession_candidates(world, player_nation: str, target_nation: str) -> list:
    """Rank player regions for cession, prioritizing border + empty + cheap.

    Returns list of [region_name, reason_text] pairs, sorted best-to-cede first.
    Excludes the player's capital.
    """
    from backend.models.region import NATION_CAPITALS, REGION_TYPE_INCOME

    capital = NATION_CAPITALS.get(player_nation, "")
    player_regions = world.get_nation_regions(player_nation)
    target_regions = world.get_nation_regions(target_nation)

    candidates = []
    for region_name in player_regions:
        if region_name == capital:
            continue
        region = world.regions.get(region_name)
        if not region:
            continue

        # Score components
        is_border = any(adj in target_regions for adj in region.adjacent_regions)
        has_buildings = len(region.buildings) > 0
        income = REGION_TYPE_INCOME.get(region.region_type, 100)

        # Build reason text
        building_types = ", ".join(b["type"].replace("_", " ") for b in region.buildings)
        if is_border and not has_buildings:
            reason = (f"{region_name} borders {target_nation} territory and has no "
                      f"strategic improvements — an ideal concession.")
        elif is_border and has_buildings:
            reason = (f"{region_name} borders {target_nation} territory — a logical "
                      f"concession, though we lose its {building_types}.")
        elif not has_buildings:
            reason = f"{region_name} has no strategic improvements — we lose little by offering it."
        else:
            reason = f"{region_name} is a {region.region_type} of modest strategic value."

        # Sort key: border first (not is_border=False first), then empty, then cheap
        candidates.append([region_name, reason, (not is_border, has_buildings, income)])

    candidates.sort(key=lambda c: c[2])
    return [[c[0], c[1]] for c in candidates]


def rank_ultimatum_territory_candidates(world, player_nation: str, target_nation: str) -> list:
    """Rank target regions for ultimatum demands, prioritizing border + valuable.

    Returns list of [region_name, reason_text] pairs, sorted best-to-demand first.
    Only includes regions adjacent to player territory. Excludes target's capital.
    """
    from backend.models.region import NATION_CAPITALS, REGION_TYPE_INCOME

    capital = NATION_CAPITALS.get(target_nation, "")
    player_regions = set(world.get_nation_regions(player_nation))
    target_region_names = world.get_nation_regions(target_nation)

    candidates = []
    for region_name in target_region_names:
        if region_name == capital:
            continue
        region = world.regions.get(region_name)
        if not region:
            continue

        # Only regions adjacent to player territory
        is_border = any(adj in player_regions for adj in region.adjacent_regions)
        if not is_border:
            continue

        has_buildings = len(region.buildings) > 0
        income = REGION_TYPE_INCOME.get(region.region_type, 100)

        # Build reason text
        if has_buildings:
            building_types = ", ".join(b["type"].replace("_", " ") for b in region.buildings)
            reason = (f"{region_name} borders our territory and has {building_types} "
                      f"— a valuable acquisition.")
        else:
            reason = f"{region_name} borders our territory — a natural extension of our domain."

        # Sort: buildings first (more valuable), then higher income
        candidates.append([region_name, reason, (not has_buildings, -income)])

    candidates.sort(key=lambda c: c[2])
    return [[c[0], c[1]] for c in candidates]


# ═══════ ENEMY DIPLOMAT VOICE RESOLUTION ═══════

# Maps diplomat personality to template key prefix
_PERSONALITY_TO_TEMPLATE = {
    "hawk": "enemy_response_hawk",
    "schemer": "enemy_response_schemer",
    "dove": "enemy_response_dove",
    "loyalist": "enemy_response_loyalist",
}


def get_enemy_response_template(
    target_nation: str,
    outcome: str,
    world,
) -> Dict:
    """Get personality-keyed enemy response template.

    Looks up the target nation's diplomat personality and returns
    the appropriate T24-T27 template variant.

    Args:
        target_nation: The responding nation
        outcome: "accept", "counter", or "reject"
        world: WorldState (for diplomat lookup)

    Returns:
        Template dict with personality-appropriate text
    """
    # Look up diplomat personality
    diplomats = getattr(world, 'diplomats', {})
    diplomat = diplomats.get(target_nation)
    personality = getattr(diplomat, 'personality', 'loyalist') if diplomat else 'loyalist'

    template_key = _PERSONALITY_TO_TEMPLATE.get(personality, "enemy_response_loyalist")

    # Try exact match: (template_key, "any", outcome)
    key = (template_key, "any", outcome)
    if key in DIPLOMATIC_TEMPLATES:
        template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
        return template

    # Fallback to loyalist
    key = ("enemy_response_loyalist", "any", outcome)
    if key in DIPLOMATIC_TEMPLATES:
        template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
        return template

    # Ultimate fallback
    return {
        "text": f"{target_nation} responds to your proposal.",
        "options": [
            {"label": "Noted", "description": "Dismiss.", "action": "dismiss"},
        ],
        "recommendation": 0,
    }


def resolve_enemy_response_text(template: Dict, world, target_nation: str) -> str:
    """Resolve slots in an enemy response template.

    Resolves {target_diplomat} and {target_nation} slots.

    Args:
        template: Template dict from get_enemy_response_template()
        world: WorldState
        target_nation: The responding nation

    Returns:
        Resolved text string
    """
    text = template.get("text", "")
    return resolve_template_text(text, world, target_nation)


def _accumulate_raw_treaty_harshness(treaty: Dict) -> float:
    """Sum the raw clause + demand harshness weights without any clamp.

    Internal helper shared by `calculate_treaty_harshness()` (1.0-clamped,
    bilateral) and `calculate_raw_treaty_harshness()` (unclamped, used by
    the common-peace acceptance formula's `term_harshness_penalty` per
    `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §6.acceptance line 1115).
    """
    harshness = 0.0
    for clause in treaty.get("clauses", []):
        ctype = clause.get("type", "")
        if ctype == "gold_per_turn":
            # SC-33 / G2-Slice-9: finite-duration recurring gold (settlement
            # clauses carry an explicit `turns` field) uses the lump-sum
            # gold-indemnity weight (`0.08 per 100 gold`) applied to the
            # full projected obligation `amount * turns`. Bilateral
            # treaties record `gold_per_turn` without a `turns` field —
            # those are perpetual streams and keep the original per-turn
            # weight so existing bilateral acceptance is not perturbed.
            turns = int(clause.get("turns", 0) or 0)
            if turns > 0:
                harshness += 0.08 * (
                    (clause.get("amount", 0) or 0) * turns / 100
                )
            else:
                harshness += 0.1 * (clause.get("amount", 0) / 100)
        elif ctype == "territory_cede":
            harshness += 0.3 * len(clause.get("regions", []))
        elif ctype == "manpower_per_turn":
            harshness += 0.15
        elif ctype == "forced_alliance":
            harshness += 0.4
        elif ctype == "liberation":
            harshness += 0.3
    # PL-12-B: Include demands in harshness calculation
    for demand in treaty.get("demands", []):
        if not isinstance(demand, dict):
            continue
        dtype = demand.get("type", "")
        amt = abs(demand.get("value", 0) or demand.get("amount", 0) or 0)
        if dtype == "gold_per_turn":
            # SC-33 / G2-Slice-9: finite settlement-style stream projects
            # to lump-sum weight; bilateral perpetual stream keeps the
            # legacy per-turn weight. See clause branch above for details.
            d_turns = int(demand.get("turns", 0) or 0)
            if d_turns > 0:
                harshness += 0.08 * (amt * d_turns / 100)
            else:
                harshness += 0.1 * (amt / 100)
        elif dtype in ("territory_cede", "territory"):
            regions = demand.get("regions", [])
            count = len(regions) if regions else max(1, amt)
            harshness += 0.3 * count
        elif dtype == "ap_per_turn":
            harshness += 0.3 * max(1, amt)
        elif dtype == "manpower_per_turn":
            harshness += 0.15
        elif dtype == "gold_lump":
            harshness += 0.08 * (amt / 100)
        elif dtype in ("manpower_infantry", "manpower_cavalry", "manpower_artillery", "manpower"):
            harshness += 0.15
        elif dtype == "forced_alliance":
            harshness += 0.4
        elif dtype == "liberation":
            harshness += 0.3
        elif dtype in ("vassalage", "subjugation"):
            harshness += 0.5
    return harshness


def calculate_treaty_harshness(treaty: Dict) -> float:
    """Calculate harshness score (0.0-1.0) from treaty clauses AND demands.

    Used for DD8-4 escalating harshness tracking and PL-12 acceptance penalty.
    Bilateral acceptance callers MUST keep using this 1.0-clamped helper.
    Common-peace acceptance must call `calculate_raw_treaty_harshness()`
    instead — the 1.5 ceiling is applied inside the C1b acceptance helper.
    """
    return min(1.0, _accumulate_raw_treaty_harshness(treaty))


def get_treaty_harshness_for_consumer(
    treaty: Dict,
    *,
    consumer: str = "common_peace",
) -> float:
    """SC-24: pick the right harshness scale for a treaty record.

    Common-peace consumers (ledger, AI proposal generation, coalition
    threat interpretation, dispatch one-liners, notification warnings)
    read the raw common-peace harshness (`raw_harshness`) so authored
    multi-clause packages that exceed 1.0 stay legible. Legacy bilateral
    consumers may still read the 1.0-clamped `harshness` field.

    Treaty records produced by `_record_common_peace_treaties` carry
    both fields plus a `source="common_peace"` tag. Records that pre-
    date SC-24 (or come from bilateral ratification) only carry the
    legacy clamped field; this helper falls back to it transparently.
    """
    if not isinstance(treaty, Mapping):
        return 0.0
    consumer = str(consumer or "").lower()
    source = str(treaty.get("source") or "").lower()
    if consumer in {
        "diplomatic_ledger",
        "ai_diplomacy",
        "coalition",
        "dispatch",
        "notifications",
    } and source == "common_peace":
        if "raw_harshness" in treaty:
            try:
                return float(treaty.get("raw_harshness") or 0.0)
            except (TypeError, ValueError):
                pass
    if "raw_harshness" in treaty and consumer == "common_peace_acceptance":
        try:
            return float(treaty.get("raw_harshness") or 0.0)
        except (TypeError, ValueError):
            pass
    try:
        return float(treaty.get("harshness") or treaty.get("clamped_harshness") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def calculate_raw_treaty_harshness(treaty: Dict) -> float:
    """Unclamped sum of treaty clause + demand harshness weights.

    Used exclusively by common-peace acceptance per
    `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §6.acceptance line 1115:

        term_harshness_penalty =
            -min(45, round((min(raw_total_harshness, 1.5) / 1.5) * 45))

    The 1.5 ceiling is applied at the acceptance helper, NOT here, so
    callers can audit the raw weight (settlement reviews show this in
    debug output) and detect packages that exceed the spec's
    settlement-tier harshness ceilings (white_peace 0.10 / favorable_terms
    0.25 / dictated_terms 0.45 / harsh_peace 0.70 / total_victory 1.00 —
    spec §6.acceptance line 1188-1196).
    """
    return _accumulate_raw_treaty_harshness(treaty)


# ═══════ BPH-A: TERM OWNERSHIP ANNOTATION ═══════

_TERM_DISPLAY_LABELS = {
    "territory_cede": "{from_nation} cedes {detail} to {to_nation}",
    "territory": "{from_nation} cedes {detail} to {to_nation}",
    "territory_return": "{from_nation} returns {detail} to {to_nation}",
    "gold_lump": "{from_nation} pays {value} gold to {to_nation}",
    "gold_per_turn": "{from_nation} pays {value} gold per turn to {to_nation}",
    "manpower_infantry": "{from_nation} transfers {value} infantry to {to_nation}",
    "manpower_cavalry": "{from_nation} transfers {value} cavalry to {to_nation}",
    "manpower_artillery": "{from_nation} transfers {value} artillery to {to_nation}",
    "ap_per_turn": "{from_nation} cedes {value} AP per turn to {to_nation}",
    "open_borders": "Mutual open borders between {nation_a} and {nation_b}",
    "military_access": "{from_nation} grants military access to {to_nation}",
    "protection": "{from_nation} guarantees {to_nation}'s sovereignty",
    "protection_promised": "{from_nation} guarantees {to_nation}'s sovereignty",
    "continental_system_lifted": "{from_nation} closes ports to Britain",
    "forced_alliance": "{from_nation} enters ALLIANCE with {to_nation} and joins the Continental System",
    "liberation": "{from_nation} is liberated from vassalage",
}


_VASSAL_TERRITORY_ADJECTIVES = {
    "Bavaria": "Bavarian",
    "Saxony": "Saxon",
}


def _safe_int(value, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_regions(raw_regions) -> list:
    if not raw_regions:
        return []
    if isinstance(raw_regions, str):
        return [raw_regions]
    try:
        return [str(region) for region in raw_regions if region]
    except TypeError:
        return []


def _vassal_territory_label(vassal_nation: str) -> str:
    adjective = _VASSAL_TERRITORY_ADJECTIVES.get(vassal_nation, vassal_nation)
    return f"{adjective} territory"


def _get_vassal_nation(term: Dict) -> str:
    if not isinstance(term, dict):
        return ""
    return (
        term.get("vassal_nation")
        or term.get("vassal_name")
        or term.get("territory_nation")
        or term.get("sovereign_nation")
        or term.get("original_owner")
        or ""
    )


def _build_display_label(clause_type: str, from_nation: str, to_nation: str,
                         regions: list, value: int, vassal_nation: str = "") -> str:
    template = _TERM_DISPLAY_LABELS.get(clause_type)
    if not template:
        from backend.display_names import clause_display_name
        return clause_display_name(clause_type)

    detail = ", ".join(regions) if regions else "territory"
    if vassal_nation and clause_type in ("territory_cede", "territory", "territory_return"):
        detail = f"{detail} ({_vassal_territory_label(vassal_nation)})"
    return template.format(
        from_nation=from_nation, to_nation=to_nation,
        detail=detail, value=int(value),
        nation_a=from_nation, nation_b=to_nation,
    )


def annotate_peace_terms(terms: Dict, proposer_nation: str, target_nation: str) -> list:
    """Annotate every clause/sweetener/demand with ownership fields per BPH §7.1.

    Returns a list of annotated term dicts, each with:
      clause_type, from_nation, to_nation, regions, term_direction,
      sweetener_value (if applicable), display_label
    """
    annotated = []
    explicit_concession_regions = set()
    for sweetener in terms.get("sweeteners", []):
        if not isinstance(sweetener, dict):
            continue
        if sweetener.get("type") in ("territory_cede", "territory"):
            explicit_concession_regions.update(
                region.strip().lower()
                for region in _coerce_regions(sweetener.get("regions", []))
                if region
            )

    for sweetener in terms.get("sweeteners", []):
        if not isinstance(sweetener, dict):
            continue
        stype = sweetener.get("type", "")
        regions = _coerce_regions(sweetener.get("regions", []))
        value = _safe_int(sweetener.get("value", 0))
        vassal_nation = _get_vassal_nation(sweetener)
        annotated.append({
            "clause_type": stype,
            "from_nation": proposer_nation,
            "to_nation": target_nation,
            "regions": regions,
            "term_direction": "concession",
            "sweetener_value": value,
            "display_label": _build_display_label(
                stype, proposer_nation, target_nation, regions, value, vassal_nation),
        })

    for demand in terms.get("demands", []):
        if not isinstance(demand, dict):
            continue
        dtype = demand.get("type", "")
        regions = _coerce_regions(demand.get("regions", []))
        value = _safe_int(demand.get("value", 0))
        vassal_nation = _get_vassal_nation(demand)
        annotated.append({
            "clause_type": dtype,
            "from_nation": target_nation,
            "to_nation": proposer_nation,
            "regions": regions,
            "term_direction": "demand",
            "sweetener_value": -value if value else 0,
            "display_label": _build_display_label(
                dtype, target_nation, proposer_nation, regions, value, vassal_nation),
        })

    for clause in terms.get("clauses", []):
        if isinstance(clause, str):
            ctype = clause
            regions = []
            value = 0
            vassal_nation = ""
        elif isinstance(clause, dict):
            ctype = clause.get("type", "")
            regions = _coerce_regions(clause.get("regions", []))
            value = _safe_int(clause.get("value", 0))
            vassal_nation = _get_vassal_nation(clause)
        else:
            continue

        if ctype in ("open_borders",):
            annotated.append({
                "clause_type": ctype,
                "from_nation": proposer_nation,
                "to_nation": target_nation,
                "regions": [],
                "term_direction": "mutual",
                "sweetener_value": 0,
                "display_label": _build_display_label(ctype, proposer_nation, target_nation, [], 0),
            })
        elif ctype == "protection_promised":
            annotated.append({
                "clause_type": ctype,
                "from_nation": proposer_nation,
                "to_nation": target_nation,
                "regions": [],
                "term_direction": "concession",
                "sweetener_value": 0,
                "display_label": _build_display_label(ctype, proposer_nation, target_nation, [], 0),
            })
        elif ctype == "continental_system_lifted":
            annotated.append({
                "clause_type": ctype,
                "from_nation": target_nation,
                "to_nation": proposer_nation,
                "regions": [],
                "term_direction": "demand",
                "sweetener_value": 0,
                "display_label": _build_display_label(ctype, target_nation, proposer_nation, [], 0),
            })
        elif ctype == "military_access":
            granting = proposer_nation
            receiving = target_nation
            if isinstance(clause, dict):
                granting = (
                    clause.get("granting_nation")
                    or clause.get("from_nation")
                    or clause.get("from")
                    or granting
                )
                receiving = (
                    clause.get("receiving_nation")
                    or clause.get("to_nation")
                    or clause.get("to")
                    or receiving
                )
            direction = "mutual"
            if granting == proposer_nation and receiving == target_nation:
                direction = "concession"
            elif granting == target_nation and receiving == proposer_nation:
                direction = "demand"
            annotated.append({
                "clause_type": ctype,
                "from_nation": granting,
                "to_nation": receiving,
                "regions": [],
                "term_direction": direction,
                "sweetener_value": 0,
                "display_label": _build_display_label(ctype, granting, receiving, [], 0),
            })
        elif ctype.startswith("territory_"):
            region_name = ctype.split("_", 1)[1] if "_" in ctype else ""
            if region_name and region_name not in ("cede", "return"):
                if region_name.strip().lower() in explicit_concession_regions:
                    continue
                annotated.append({
                    "clause_type": "territory_cede",
                    "from_nation": proposer_nation,
                    "to_nation": target_nation,
                    "regions": [region_name.title()],
                    "term_direction": "concession",
                    "sweetener_value": 0,
                    "display_label": _build_display_label(
                        "territory_cede", proposer_nation, target_nation,
                        [region_name.title()], 0),
                })
            else:
                annotated.append({
                    "clause_type": ctype,
                    "from_nation": proposer_nation,
                    "to_nation": target_nation,
                    "regions": regions,
                    "term_direction": "concession",
                    "sweetener_value": 0,
                    "display_label": _build_display_label(
                        ctype, proposer_nation, target_nation, regions, value, vassal_nation),
                })
        else:
            annotated.append({
                "clause_type": ctype,
                "from_nation": proposer_nation,
                "to_nation": target_nation,
                "regions": regions,
                "term_direction": "mutual",
                "sweetener_value": 0,
                "display_label": _build_display_label(
                    ctype, proposer_nation, target_nation, regions, value, vassal_nation),
            })

    return annotated
