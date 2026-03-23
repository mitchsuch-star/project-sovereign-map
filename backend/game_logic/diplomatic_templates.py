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
            "Their court speaks well of France. "
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
            "{target_nation} is currently at war with France. "
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
            "{target_nation} is at peace with France. "
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

        # Get diplomat for target nation
        diplomats = getattr(world, 'diplomats', {})
        target_diplomat = diplomats.get(target_nation)
        slots["target_diplomat"] = target_diplomat.name if target_diplomat else "their diplomat"

        # Numeric values
        player_nation = getattr(world, 'player_nation', 'France')
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
    ("Britain", "gold_useless"): "Britain's coffers overflow — offering gold insults Castlereagh. Territory speaks louder.",
    ("Britain", "coveted_territory_offered"): "The Netherlands secures Britain's continental foothold. Castlereagh values it above gold.",
    ("Britain", "dominant_terms"): "Britain's continental army is small. Castlereagh knows his position — he'll accept reasonable terms.",
    ("Britain", "desperate_terms"): "Castlereagh drives a hard bargain. I've included everything short of Paris itself.",
    ("Britain", "neutral_deal"): "An island nation with continental ambitions. This arrangement serves both parties' interests.",
    ("Britain", "friendly_deal"): "Castlereagh is amenable, for once. Best to lock in terms before his mood shifts.",
    ("Britain", "hostile_deal"): "Castlereagh despises us openly. Only overwhelming terms have any chance.",
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
    ("Britain", "coveted_unavailable"): "Castlereagh values his continental footholds, but they are beyond our gift at present. We must work with what we have.",
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
    ("Britain", "modified_harsh"): "Castlereagh's island gives him options we cannot eliminate. Harsh terms risk outright rejection.",
    ("Britain", "modified_generous"): "Even Castlereagh may warm to terms this favorable. Britain values pragmatism.",
    ("Saxony", "modified_harsh"): "Poor Einsiedel has little left to give. These demands may break Saxony entirely.",
    ("Saxony", "modified_generous"): "Einsiedel will weep with gratitude. Such generosity buys a loyal vassal, Sire.",
    ("_default", "modified_harsh"): "I have drafted more demanding terms, Sire. They will not accept lightly.",
    ("_default", "modified_generous"): "I have drafted more generous terms, Sire. Such magnanimity should improve acceptance.",
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

    war_score = get_war_score_for(world, "France", target_nation)

    # --- Stage 1: Base terms ---
    terms = _build_base_terms(target_nation, proposal_type, world)

    # --- Stage 2: Nation-specific injection ---
    context_tags = []
    profile = NATION_DESIRE_PROFILES.get(target_nation, {})

    # 2a. Territory sweeteners: prefer coveted regions
    has_territory_sweetener = any(
        s.get("type") == "territory_cede" for s in terms.get("sweeteners", []))
    coveted = [r for r in profile.get("covets_regions", [])
               if r in world.get_nation_regions("France")]
    target_holds_all_coveted = all(
        r in world.get_nation_regions(target_nation)
        for r in profile.get("covets_regions", [])
    ) if profile.get("covets_regions") else True

    # Check if target covets regions France doesn't control (hint to conquer first)
    all_coveted = profile.get("covets_regions", [])
    coveted_unavailable = [r for r in all_coveted
                           if r not in world.get_nation_regions("France")
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
            candidates = rank_cession_candidates(world, "France", target_nation)
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
    france_regions = world.get_nation_regions("France")
    border = []
    for rname in target_regions:
        region = world.regions.get(rname)
        if region and any(adj in france_regions for adj in region.adjacent_regions):
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

    terms["talleyrand_commentary"] = _get_smart_commentary(
        target_nation, context_tags[0])

    # --- Stage 5: Return ---
    return terms


def _build_base_terms(target_nation: str, proposal_type: str, world) -> Dict:
    """Build base treaty terms using war_score/relation thresholds.

    Extracted from the original generate_suggested_terms() — no logic changes.
    """
    from backend.game_logic.diplomacy import get_war_score_for
    diplo_key = world._make_diplo_key("France", target_nation)
    relation = world.nation_relations.get(diplo_key, 0)
    war_score = get_war_score_for(world, "France", target_nation)

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
        elif war_score < -20 or relation < -50:
            # If losing or deeply hostile, offer gold to sweeten
            gold_factor = max(abs(war_score) * 3, abs(relation))
            gold_offer = min(200, max(50, int(gold_factor)))
            terms["sweeteners"].append({"type": "gold_per_turn", "value": int(gold_offer)})

            # R147: Offer territory cession when losing
            # Non-capital regions first; capital only as desperate last resort
            from backend.models.region import NATION_CAPITALS
            france_capital = NATION_CAPITALS.get("France", "Paris")
            france_regions = world.get_nation_regions("France")
            non_capital = [r for r in france_regions if r != france_capital]
            max_cede = 1 if war_score >= -40 else 2
            for region in non_capital[:max_cede]:
                terms["sweeteners"].append({"type": "territory_cede", "value": 1, "regions": [region]})
            # Capital offered only as desperate last resort (war_score < -60)
            if war_score < -60 and len(non_capital) < max_cede:
                terms["sweeteners"].append({"type": "territory_cede", "value": 1, "regions": [france_capital]})

            # R148: Offer manpower when losing badly
            if war_score < -30:
                france_pool = getattr(world, 'manpower_pools', {}).get("France", {}).get("infantry", 0)
                offer_amount = min(5000, int(france_pool * 0.25))
                if offer_amount >= 1000:
                    terms["sweeteners"].append({"type": "infantry_manpower", "value": int(offer_amount)})

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
            france_capital = NATION_CAPITALS.get("France", "Paris")
            france_regions = world.get_nation_regions("France")
            non_capital = [r for r in france_regions if r != france_capital]
            if non_capital:
                terms["sweeteners"].append({"type": "territory_cede", "value": 1, "regions": [non_capital[0]]})
            elif war_score < -60:
                # Capital only as desperate last resort
                terms["sweeteners"].append({"type": "territory_cede", "value": 1, "regions": [france_capital]})

    return terms


def _validate_economic_feasibility(terms, target_nation, world, war_score=0):
    """Cap gold/territory offers and demands to economically feasible levels."""
    player_gold = world.nation_gold.get("France", 0)
    player_income = world.calculate_turn_income("France").get("income", 0)
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
