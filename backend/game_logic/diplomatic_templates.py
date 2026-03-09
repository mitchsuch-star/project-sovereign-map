"""
Diplomatic Template Library — Phase 8 Session 3

Templates T1-T10 for Talleyrand's conversational diplomacy.
Templates T11-T27 are Session 4-6 scope.

Architecture:
  DIPLOMATIC_TEMPLATES keyed by (situation, game_bucket, specificity)
  Each template has text (with {slots}), options, and recommendation index.
"""

from typing import Dict, Optional

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
            "War score stands at {war_score}. I see several paths forward."
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
            "War score: {war_score}. We must act before things deteriorate further."
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
            "War score: {war_score}. Neither side has a decisive advantage."
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
            "Current relation: {relation}. State: {current_state}. "
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
            "Relation: {relation}. State: {current_state}. "
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
            "I suggest the following terms. War score: {war_score}, relation: {relation}."
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
            "I have prepared appropriate terms. Relation: {relation}, state: {current_state}."
        ),
        "options": [
            {
                "label": "Send as suggested",
                "description": "Send the proposal with my recommended terms.",
                "action": "execute_proposal",
            },
            {
                "label": "Adjust terms",
                "description": "Let me see what else we could offer or demand.",
                "action": "expand_options",
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
            "{target_nation} is currently at war with France. "
            "War score: {war_score}. Relation: {relation}.\n\n"
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
            "{target_nation} is at peace with France. "
            "Relation: {relation}. State: {current_state}.\n\n"
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
                "description": "Trust -10, Authority +5, cooldown 5 turns.",
                "action": "confront_sabotage",
            },
            {
                "label": "Overlook",
                "description": "Trust +3. Talleyrand gains confidence.",
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


def get_coalition_template(category: str) -> Optional[Dict]:
    """Get a coalition template by category name."""
    return COALITION_TEMPLATES.get(category)


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
            "Current state: {current_state}, relation: {relation}."
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

        # Get diplomat for target nation
        diplomats = getattr(world, 'diplomats', {})
        target_diplomat = diplomats.get(target_nation)
        slots["target_diplomat"] = target_diplomat.name if target_diplomat else "their diplomat"

        # Numeric values
        diplo_key = world._make_diplo_key("France", target_nation)
        relation = int(world.nation_relations.get(diplo_key, 0))
        state = world.get_diplomatic_state("France", target_nation)
        # R38: Only show war score when nations are at war
        if state == "WAR":
            slots["war_score"] = str(int(world.war_scores.get(diplo_key, 0)))
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


# ═══════ SUGGESTED TERMS GENERATION ═══════

def generate_suggested_terms(target_nation: str, proposal_type: str, world) -> Dict:
    """Generate reasonable default treaty terms based on game state.

    Returns a dict with proposal terms suitable for calculate_acceptance().
    """
    diplo_key = world._make_diplo_key("France", target_nation)
    relation = world.nation_relations.get(diplo_key, 0)
    war_score = world.war_scores.get(diplo_key, 0)

    terms = {
        "type": proposal_type,
        "proposer_nation": "France",
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
        elif war_score < -20:
            # If losing, offer gold to sweeten
            gold_offer = min(200, abs(war_score) * 3)
            terms["sweeteners"].append({"type": "gold_per_turn", "value": int(gold_offer)})

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

    return terms


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


def calculate_treaty_harshness(treaty: Dict) -> float:
    """Calculate harshness score (0.0-1.0) from treaty clauses.

    Used for DD8-4 escalating harshness tracking.
    """
    harshness = 0.0
    for clause in treaty.get("clauses", []):
        ctype = clause.get("type", "")
        if ctype == "gold_per_turn":
            harshness += 0.1 * (clause.get("amount", 0) / 100)
        elif ctype == "territory_cede":
            harshness += 0.2 * len(clause.get("regions", []))
        elif ctype == "manpower_per_turn":
            harshness += 0.15
    return min(1.0, harshness)
