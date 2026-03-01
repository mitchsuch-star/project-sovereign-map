# Conversational Diplomacy Layer — Design Document

> **Status:** APPROVED v1.2 — Design gate passed. Sessions unified into DIPLOMACY_SPEC §14 (7-session plan). Cross-document consistency verified against DIPLOMACY_SPEC v2.2.
> **Phase:** 8 (overlay on DIPLOMACY_SPEC.md)
> **Prerequisite:** DIPLOMACY_SPEC.md v2.1 approved. This document defines the INTERACTION LAYER, not the mechanical systems.
> **Relationship to DIPLOMACY_SPEC:** This spec replaces §2c (Talleyrand commands — keywords preserved, flow redesigned), §2d (proposal flow — transit mechanics preserved, presentation redesigned), §2g (feasibility — enhanced to conversation), and §9a (AI proposal popups — delivered through dialogue system). §10b (Diplomatic Ledger) is UNCHANGED — the Ledger is a data screen, complementary to the dialogue system. All formula/state/treaty mechanics in DIPLOMACY_SPEC remain unchanged. This is the steering wheel; DIPLOMACY_SPEC is the engine.

---

## §1. Executive Summary

### What This Is

A conversation layer that sits between the player's natural language input and the diplomacy engine. Instead of constructing treaty clauses and submitting proposals (EU4), the player **talks to Talleyrand** and he talks back. He has opinions. He fills in details. He pushes back. He might do something different than what you asked. The gap between "what you said" and "what he did" IS the diplomatic game.

### Why It Matters

Combat already works this way — you say "Ney, attack Wellington" and Ney might say "That's suicide, Sire." This is what makes the game special. Diplomacy must feel identical: you say "Talleyrand, deal with Prussia" and Talleyrand responds "Sire, Hardenberg is proud but practical. I'd suggest offering peace with generous terms — 200 gold per turn and open borders should suffice. *Though personally, I would add a protection guarantee. It costs us nothing and makes them feel safe.*"

No strategy game has ever done this. Diplomacy in every 4X game is a menu. Here it's a conversation with a brilliant, untrustworthy advisor.

### The Fun Pitch

You have the greatest diplomat in European history on your payroll. He's smarter than you, he knows it, and he has his own agenda. Sometimes his advice saves your empire. Sometimes he's steering you toward his vision of France, not yours. You can override him — you're Napoleon — but he might go behind your back. The question isn't "what are the optimal treaty terms?" The question is "do I trust Talleyrand?"

### Core Constraint

**Everything works in mock mode.** Mock mode IS the game. LLM mode adds better voice acting on the same structure. If it's not fun in mock, it's not fun. Mock forces us to design the conversation STRUCTURE, which is better for consistent gameplay.

---

## §2. Conversation Flow Architecture

### 2a. The Dialogue State Machine

Diplomatic conversations use a multi-step flow, similar to the existing objection system (`pending_objection` → player responds → execution continues). The new pattern:

```
Player command
    ↓
Parser detects diplomatic intent (addressee = Talleyrand)
    ↓
Conversation Engine evaluates:
  - What did the player ask? (specificity level)
  - What's the game state? (war scores, relations, threats)
  - What does Talleyrand think? (personality-driven assessment)
    ↓
Talleyrand responds (dialogue + options)
    ↓
world.pending_diplomatic_dialogue = {dialogue state}
    ↓
Player picks an option (or types follow-up in LLM mode)
    ↓
Action executes via existing DIPLOMACY_SPEC mechanics
```

**New WorldState field:** `pending_diplomatic_dialogue` (dict or None). Stores the conversation state between turns of player interaction. Same pattern as `pending_objection` and `pending_strategic_objection`.

**Conversation depth: 2 exchanges maximum for action commands.** Player says something → Talleyrand responds with recommendation + options → player picks → action executes. Advisory conversations (§8) may go to 3 exchanges but never 4+.

### 2b. The Dialogue State Dict

```python
pending_diplomatic_dialogue = {
    "type": "proposal_options",     # dialogue type (see §2c)
    "target_nation": "Prussia",     # context
    "talleyrand_text": "...",       # what Talleyrand says
    "options": [                    # 2-4 player choices
        {
            "label": "Do it",
            "description": "Send proposal with Talleyrand's suggested terms",
            "action": "execute_proposal",
            "terms": {...},         # mechanical data for execution
        },
        {
            "label": "Harsher terms",
            "description": "Demand more — Talleyrand may object",
            "action": "modify_harsh",
        },
        {
            "label": "What else could we offer?",
            "description": "Talleyrand lists available clause types",
            "action": "expand_options",
        },
    ],
    "context": {                    # game state snapshot for follow-up
        "war_score": 20,
        "relation": -60,
        "threat": 40,
        "suggested_terms": {...},
    },
    "turn_created": 5,             # used for auto-dismiss: non-blocking dialogues auto-dismiss
                                    # on end-turn if turn_created < current_turn.
                                    # Blocking dialogues (blocking=True) IGNORE turn_created.
    "blocking": False,              # True for incoming_proposal and sabotage_confrontation
}
```

**Serialization rules:** `pending_diplomatic_dialogue` must survive save/load. All values are primitives (str, int, bool, list, dict) — no object references. The `context` sub-dict stores snapshots, not live references. Serialization pattern:

```python
# In world_state.py to_dict():
"pending_diplomatic_dialogue": self.pending_diplomatic_dialogue,  # already primitive-only

# In world_state.py from_dict():
world.pending_diplomatic_dialogue = d.get("pending_diplomatic_dialogue", None)
```

Run `pytest tests/test_serialization_enforcement.py -v` after implementation. Update `docs/SAVE_FORMAT_REFERENCE.md` with the new field.

### 2c. Dialogue Types

| Type | Trigger | Talleyrand Behavior | Depth |
|------|---------|-------------------|-------|
| `proposal_options` | Vague command ("deal with Prussia") | Presents 2-3 approaches | 2 exchanges |
| `proposal_confirm` | Medium command ("offer peace to Prussia") | Suggests specific terms, asks confirmation | 2 exchanges |
| `proposal_execute` | Specific command (full clause list) | Objects or executes (existing §2d flow) | 1-2 exchanges |
| `advisory` | "What about Austria?" / "Who's the threat?" | Strategic analysis, recommendations | 2-3 exchanges |
| `feasibility` | "What would it take to...?" | Formula-backed assessment with Schemer bias | 1 exchange |
| `incoming_proposal` | AI sends proposal | Presents proposal with his spin | 2 exchanges | **blocking** |
| `sabotage_confrontation` | Sabotage discovered | Dramatic reveal, player choice | 2 exchanges | **blocking** |
| `proactive_suggestion` | Talleyrand notices an opportunity | Morning Dispatch suggestion | 1-2 exchanges | non-blocking |

### 2d. The Command → Dialogue Router

When the parser detects a Talleyrand-addressed command, it classifies specificity before routing:

```python
def classify_diplomatic_intent(parsed_command, world):
    """Classify player command into specificity level + dialogue type."""

    target_nation = parsed_command.get("target_nation")
    has_proposal_type = parsed_command.get("proposal_type") is not None
    has_clauses = len(parsed_command.get("clauses", [])) > 0
    is_question = parsed_command.get("is_question", False)
    has_diplomatic_keywords = parsed_command.get("has_diplomatic_keywords", True)

    # M6: Military command addressed to Talleyrand — no diplomatic keywords found
    if not has_diplomatic_keywords and not is_question:
        return "not_diplomatic"  # Caller returns Talleyrand deflection (see below)

    # M3: Validate target nation against known nations
    if target_nation is not None:
        known_nations = world.get_known_nations()  # WorldState getter (SPEC §13)
        if target_nation not in known_nations:
            return "unknown_nation"  # Caller returns Talleyrand-voiced error

    if is_question:
        return "advisory"  # or "feasibility" based on keywords

    if has_clauses:
        return "proposal_execute"   # SPECIFIC — full terms provided
    elif has_proposal_type:
        return "proposal_confirm"   # MEDIUM — type known, terms needed
    elif target_nation:
        return "proposal_options"   # VAGUE with target — what to do WITH them
    else:
        return "proposal_options"   # VAGUE — what to do AT ALL

# Error responses (Talleyrand-voiced):
# "not_diplomatic" → "Sire, I am a diplomat, not a general. Perhaps you
#   meant to address one of your marshals?"
# "unknown_nation" → "Sire, I am not aware of a nation called {input}.
#   Our diplomatic landscape includes {known_nations_list}."
```

---

## §3. The Specificity Spectrum

### 3a. VAGUE — "Talleyrand, deal with Prussia"

The most FUN path. Talleyrand shines here because he gets to be an advisor, not just a messenger.

**What happens:**
1. Conversation engine evaluates game state (war score, relation, threat, current diplomatic state with Prussia)
2. Talleyrand presents 2-3 approaches, ranked by his preference (Schemer bias)
3. Player picks one → either executes immediately or transitions to `proposal_confirm`

**Example — France is winning against Prussia (war score +20):**

```
PLAYER: "Talleyrand, deal with Prussia"

TALLEYRAND: "Prussia is bloodied but not broken, Sire. Hardenberg's
pride won't accept submission, but he might accept peace if we're
generous. I see three paths:

  [1] Offer peace with generous terms — open borders and 200 gold
      per turn should suffice. This preserves our diplomatic standing.

  [2] Press our advantage — demand Rhineland and tribute. They may
      refuse, but our war score gives us leverage.

  [3] Ignore Prussia for now — focus our efforts on courting Austria
      before she joins the coalition.

I would recommend the first option, Sire. A quick peace frees us
to address the Austrian question."
```

**In mock mode:** Template selected by (target_nation_state=WAR, game_state_bucket=WINNING, relation_bucket=HOSTILE). Options are mechanically generated from available diplomatic actions. Talleyrand's recommendation is the option with the highest projected acceptance score (§6) — with Schemer bias applied.

**DP cost display on options:** Each option displays its DP cost. Options costing more than the player's current DP show "(insufficient DP)" and selecting them triggers Talleyrand: "We lack the diplomatic capital for that, Sire. Perhaps something more modest." Options that cost 0 DP (advisory, feasibility, mission cancel) are always available. Example:
```
  [1] Offer generous peace (2 DP)
  [2] Press for favorable terms (2 DP)
  [3] Armistice — buy time (1 DP)
  [4] Ignore Prussia for now (0 DP)
```
If player has 1 DP, options 1 and 2 show "(insufficient DP)" and are soft-blocked.

**In LLM mode:** Same options, same recommendation, but Talleyrand's voice is richer. The LLM gets the template structure as a skeleton and fills in characterful prose.

**Player picks option 1 → transitions to `proposal_confirm`:**

```
TALLEYRAND: "Very well, Sire. I propose the following terms to Hardenberg:

  Peace treaty. Prussia retains Berlin and all current holdings.
  Open borders between France and Prussia.
  Prussia pays 200 gold per turn.

  My assessment: Challenging but possible with concessions. Hardenberg
  is proud — the gold demand may sting. Shall I proceed?"

  [Send it]  [Sweeten the deal]  [Never mind]
```

Player clicks "Send it" → proposal enters transit per DIPLOMACY_SPEC §2d transit mechanics (1-turn transit, sabotage during transit, return popup). The transit MECHANICS are unchanged; this DESIGN doc redesigns only the PRESENTATION (dialogue-based instead of simple popup).

### 3b. MEDIUM — "Talleyrand, offer peace to Prussia"

Player knows WHAT they want (peace) but not the terms. Talleyrand fills in details.

**What happens:**
1. Talleyrand evaluates what terms would make the acceptance formula hit ~50 (the ACCEPT threshold)
2. He presents a package — his "best guess" at what would work
3. Schemer bias: he may inflate concessions slightly ("a protection guarantee costs us nothing") to favor his preferred outcome. **Design note:** This is intentional — Talleyrand's bias DOES affect mechanical outcomes in the MEDIUM path through the player's trust. If the player sends Talleyrand's suggested terms without checking the Ledger, they may send overly generous proposals. The Strategic Ledger (D key) exists as the player's verification tool. Learning to cross-check Talleyrand's suggestions against the raw numbers IS the trust-calibration meta-game

**Example:**

```
PLAYER: "Talleyrand, offer peace to Prussia"

TALLEYRAND: "A wise choice, Sire. Given our current military position
and Hardenberg's temperament, I'd suggest offering:

  Peace with open borders.
  200 gold per turn as a gesture of goodwill.
  A protection guarantee — it costs us nothing and makes
  Prussia feel secure.

  My assessment: Achievable with modest effort. The protection
  guarantee is what tips the scales.

  [Send these terms]  [More generous]  [Harsher]  [Let me specify]
```

**"Let me specify" opens a clause-selection flow** — the player can manually add/remove clauses. This is the bridge between conversational and mechanical interfaces.

**Clause-selection UI (terminal interface):**

```
TALLEYRAND: "Very well, Sire. What terms shall I present?

  Current proposal: Peace with Prussia
  Clauses so far: (none)

  Available clause types:
    [1] Gold lump sum — "add gold 500"
    [2] Gold/turn — "add gold_per_turn 200"
    [3] Territory (demand) — "demand Rhineland"
    [4] Territory (offer) — "offer Saxony"
    [5] Open borders — "add open_borders"
    [6] Military access — "add military_access"
    [7] Protection guarantee — "add protection"
    [8] Manpower — "add infantry 5000"
    [9] Unit trade — "add cavalry_for_artillery 2500"

  Commands: 'add [clause]', 'remove [#]', 'done', 'cancel'
  Type 'done' when finished to see Talleyrand's assessment."
```

The player builds clauses one at a time. Each `add` command appends to the clause list and re-displays with updated harshness and projected acceptance. `done` transitions to `proposal_confirm` with the assembled terms. `cancel` exits with no DP cost. In mock mode, commands are parsed via keyword matching. In LLM mode, free-text like "throw in 200 gold and demand Rhineland" is parsed into clause additions.

**Save/load during clause-selection (N1 resolution):** The clause-selection sub-state is stored within `pending_diplomatic_dialogue` as:
```python
pending_diplomatic_dialogue = {
    "type": "clause_selection",
    "target_nation": "Prussia",
    "proposal_type": "peace",
    "current_clauses": [{"type": "open_borders"}, {"type": "gold_per_turn", "amount": 200}],
    "talleyrand_text": "Current proposal: Peace with Prussia...",
    "options": [{"label": "Done", "action": "finalize_clauses"}, ...],
    "context": {...},
    "turn_created": 5,
    "blocking": False,
}
```
On game load, if `type == "clause_selection"`, the Godot client re-displays the clause builder with `current_clauses` pre-populated. This survives save/load because all values are primitives (str, int, list of dicts).

### 3c. SPECIFIC — "Talleyrand, propose peace with Prussia: they keep Berlin, open borders, 200 gold/turn"

The existing spec behavior. Talleyrand evaluates the specific terms and either:
- **Executes** if he agrees (or if trust/authority are high enough)
- **Objects** if he disagrees (MILD/MODERATE/STRONG per §3e of DIPLOMACY_SPEC)
- **Suggests modification** if the terms are close but suboptimal

**Example — terms Talleyrand dislikes (too harsh):**

```
PLAYER: "Talleyrand, demand Prussia cede Rhineland, pay 500 gold/turn,
         and grant us military access"

TALLEYRAND: "Sire, I must advise against these terms. Demanding
Rhineland AND 500 gold per turn is beyond what Hardenberg can accept.
He would sooner fight to the death. More importantly, such demands
will drive Austria into the coalition. The courts of Europe are watching.

I would suggest moderating to 200 gold per turn and dropping the
territory demand. We can always revisit Rhineland later.

  [Send my terms as ordered]  [Use Talleyrand's suggestion]
  [Modify terms]"
```

This is a **diplomatic objection** — the same MILD/MODERATE/STRONG pattern from combat, but expressed as part of the conversation rather than as a separate popup system. See §10 for the full objection design.

### 3d. Fast-Track for Specific + Agree

When a SPECIFIC command is unambiguous AND Talleyrand agrees (no objection), skip the full dialogue and execute immediately with a brief confirmation:

```
PLAYER: "Talleyrand, propose peace to Saxony with open borders"

TALLEYRAND: "At once, Sire. I shall deliver these terms to Einsiedel.
Expect a response by next turn. (2 DP spent)"
```

This is a 1-exchange fast path — no options popup, no confirmation step. The command executes directly via the existing DIPLOMACY_SPEC §2d flow. This preserves conversation depth for vague commands and objections while eliminating friction for clear, uncontroversial orders. T7 ("A reasonable proposal, Sire") is the template — when Talleyrand agrees AND the command is fully specified, present only `[Send] [Wait, let me reconsider]` with Send as the default.

---

## §4. Mock Template Library

### 4a. Template Architecture

Templates are structured as:

```python
DIPLOMATIC_TEMPLATES = {
    (situation, game_bucket, specificity): {
        "text": "Template string with {slots}...",
        "options": [...],
        "recommendation": 0,  # index of Talleyrand's preferred option
    }
}
```

**Situation types:** `peace_from_winning`, `peace_from_losing`, `peace_from_stalemate`, `alliance_proposal`, `vassalage_demand`, `advisory_threat`, `advisory_opportunity`, `incoming_accept`, `incoming_reject`, `incoming_counter`, `vague_hostile`, `vague_neutral`, `vague_friendly`, `feasibility`, `proactive_opportunity`, `proactive_warning`

**Game state buckets** (derived from war_score + relation + threat):

```python
def get_game_bucket(target_nation, world):
    war_score = world.get_war_score("France", target_nation)
    relation = world.get_nation_relation("France", target_nation)
    threat = world.threat_level
    state = world.get_diplomatic_state("France", target_nation)

    if state == "WAR":
        if war_score > 30: return "winning_comfortably"
        if war_score > 0:  return "winning_slightly"
        if war_score > -10: return "stalemate"
        if war_score > -30: return "losing_slightly"
        return "losing_badly"
    else:
        if relation > 20:  return "friendly"
        if relation > -20: return "neutral"
        return "hostile"
```

**Specificity levels:** `vague`, `medium`, `specific` (from §3)

### 4b. Template Library — 27 Core Templates

---

**T1: VAGUE + WAR + WINNING_COMFORTABLY**

```
"Prussia reels from our victories, Sire. {target_diplomat} knows the
situation is dire. Three paths present themselves:

[1] Offer generous peace — end hostilities now, preserve our strength
    for other fronts. Terms: open borders, {suggested_gold} gold/turn. (Costs 2 DP)

[2] Press for submission — demand territory and tribute. {target_nation}
    may refuse, but our position has never been stronger. (Costs 2 DP)

[3] Continue fighting — total military victory opens the door to
    vassalage. But every turn of war risks Austrian intervention.

I counsel peace, Sire. A magnanimous victor is a feared one."
```
*Recommendation: 0 (peace). Schemer bias: prefers restrained expansion. Options [1] and [2] cost 2 DP — shown in option descriptions.*

---

**T2: VAGUE + WAR + LOSING_BADLY**

```
"Sire, I must speak plainly. Our position against {target_nation} is...
untenable. {target_diplomat} smells blood. Our options are limited:

[1] Sue for armistice — buy time to regroup. We will pay dearly, but
    we will survive. (Costs 1 DP)

[2] Approach a third party — {neutral_nation} might mediate. It would
    cost us diplomatic capital but avoid direct humiliation. (Costs 2 DP)

[3] Fight on — military reversal changes everything. But if it doesn't
    come soon, the terms will only grow harsher.

An armistice now, Sire. Pride is a luxury we cannot afford."
```
*Recommendation: 0 (armistice). Schemer bias: survival first.*

---

**T3: VAGUE + WAR + STALEMATE**

```
"The war with {target_nation} grinds on, Sire. Neither side can force
a decision. {target_diplomat} knows this as well as we do.

[1] Propose peace — both sides keep current holdings. Open borders
    and modest tribute would sweeten the deal. (Costs 2 DP)

[2] Propose armistice — a breathing space. Three turns to reposition
    before deciding on peace or renewed offensive. (Costs 1 DP)

[3] Escalate — one decisive battle could break the stalemate. But
    defeat would leave us exposed.

A stalemate favors the patient, Sire. I suggest we propose peace
while we still negotiate from a position of equality."
```
*Recommendation: 0 (peace).*

---

**T4: MEDIUM (PEACE) + WAR + WINNING_SLIGHTLY**

```
"Peace with {target_nation}, Sire? Prudent. Given our position and
{target_diplomat}'s temperament, I suggest:

  Peace treaty. {target_nation} retains {their_capital}.
  Open borders between our nations.
  {target_nation} pays {suggested_gold} gold per turn.
  {optional_clause}

My assessment: {difficulty_tier}. {formula_hint}. (Costs 2 DP)

The Diplomatic Ledger (D key) has the precise figures, Sire.

[Send these terms]  [More generous]  [Harsher]  [Let me specify]"
```
*{optional_clause} filled by Schemer bias: protection guarantee if threat > 30 ("it costs us nothing"), Continental System participation if Britain involved.*

---

**T5: MEDIUM (ALLIANCE) + PEACE + FRIENDLY**

```
"An alliance with {target_nation}? An excellent notion, Sire.
{target_diplomat} has shown warmth toward France. I would propose:

  Defensive alliance. Mutual defense against aggression.
  Open borders maintained.
  Joint military coordination.

{target_diplomat_personality_note}

My assessment: {difficulty_tier}. {formula_hint}. (Costs 2 DP)

Of course, Sire, this is merely my assessment. The Ledger may tell
a different story.

[Propose alliance]  [Start with non-aggression first]
[What would they want in return?]"
```
*{target_diplomat_personality_note}: Hawk → "Hardenberg respects strength — our recent victories help." Dove → "Einsiedel fears conflict — this offer gives him security." Schemer → "Metternich will want something in return. He always does."*

---

**T6: MEDIUM (VASSALAGE) + WAR + WINNING_COMFORTABLY**

```
"Vassalage, Sire? Bold. {target_nation} will not submit willingly,
but our military position is compelling. The terms that might work:

  Vassalage at SATELLITE level — {target_nation} retains domestic
  authority but joins our wars and pays 75% tribute.
  Protection guarantee from France.
  {suggested_sweetener}

My assessment: {difficulty_tier}. {formula_hint}. (Costs 2 DP)

Be warned, Sire — vassalage raises threat by {threat_increase} with
every court in Europe. Is it worth the cost?

[Demand vassalage]  [Offer treaty peace instead]
[What would make them accept?]"
```

---

**T7: SPECIFIC + TALLEYRAND_AGREES**

```
"A reasonable proposal, Sire. I shall deliver these terms to
{target_diplomat} personally. Expect a response by next turn.

  {clause_summary}

My assessment: {difficulty_tier}.

[Send]  [Wait, let me reconsider]"
```
*Short — player gave specific terms, Talleyrand agrees, just confirm and go.*

---

**T8: SPECIFIC + TALLEYRAND_OBJECTS (MODERATE)**

```
"Sire, I must counsel caution. These terms are {objection_reason}.
{target_diplomat} {prediction}. More importantly, {strategic_concern}.

I would suggest {modification_summary}.

[Send my terms as ordered]  [Use your suggestion]  [Modify terms]"
```
*Objection reasons by trigger: too harsh → "beyond what any court would accept", too generous → "beneath the dignity of France", war declaration → "how coalitions are born".*

---

**T9: INCOMING PROPOSAL — TALLEYRAND RECOMMENDS ACCEPT**

```
"Sire, {target_diplomat} has arrived with a proposal from {target_nation}:

  {proposal_summary}

{talleyrand_assessment}

I recommend acceptance, Sire. {acceptance_reason}.

[Accept]  [Reject]  [Counter-offer — costs 1 DP]"
```
*Assessment varies by Schemer bias: may recommend accepting a bad deal if it serves long-term stability, or recommend rejecting a good deal if it makes France look weak.*

---

**T10: INCOMING PROPOSAL — TALLEYRAND RECOMMENDS REJECT**

```
"Sire, {target_diplomat} presents terms that are, frankly, insulting:

  {proposal_summary}

{target_nation} offers us nothing while demanding {worst_clause}.
{talleyrand_spin}

[Reject outright]  [Counter-offer]  [Accept anyway]"
```
*{talleyrand_spin}: Schemer adds strategic context. "Rejecting now sends a message. Hardenberg will return with better terms once he sees our army at his gates."*

---

**T11: INCOMING PROPOSAL — COUNTER-OFFER RECOMMENDED**

```
"Sire, {target_diplomat}'s proposal is... a starting point. Not
acceptable as written, but there is room to negotiate:

  Their terms: {proposal_summary}
  The sticking point: {worst_clause}

I suggest we counter with: {counter_suggestion}. This costs 1 DP
and another turn of negotiation, but {counter_reason}.

[Accept their terms]  [Counter with Talleyrand's suggestion]
[Counter with my own terms]  [Reject]"
```

---

**T12: ADVISORY — THREAT ASSESSMENT**

```
"You ask about {target_nation}, Sire? Let me assess the situation.

{target_nation} is currently at {state} with France.
Relations stand at {relation} — {relation_description}.
{target_diplomat} is a {personality} — {personality_implication}.

{threat_assessment}

{recommendation}

The Diplomatic Ledger (D key) has the precise figures if you wish to verify.

[Thank you]  [What should we do about it?]  [How do we improve relations?]"
```
*{threat_assessment} varies: WAR → war score analysis. PEACE + hostile → "They are watching. A military setback could push them into the coalition." PEACE + friendly → "A reliable partner, for now."*

---

**T13: ADVISORY — OPPORTUNITY**

```
"{opportunity_observation}

I believe we could {suggested_action}. The cost would be {dp_cost} DP,
and I estimate {difficulty_tier} odds of success.

{schemer_aside}

[Do it]  [Tell me more]  [Not now]"
```
*{schemer_aside}: "Though I confess, Sire, I have been cultivating this opportunity for some time." or "Of course, there are... subtleties that a less experienced diplomat might miss."*

---

**T14: FEASIBILITY — ACHIEVABLE**

```
"Can we reach terms with {target_nation}? Yes, Sire, I believe so.

The key factor is {largest_positive}. Working against us: {largest_negative}.

I would rate this as: {difficulty_tier}.

The most effective path: {actionable_hint}.

[Proceed with a proposal]  [Improve relations first]  [Not now]"
```

---

**T15: FEASIBILITY — NEARLY IMPOSSIBLE**

```
"Sire, I must be frank. {proposal_type} with {target_nation} is...
{difficulty_tier}.

The primary obstacle: {largest_negative}. Even with {best_lever},
the numbers do not favor us.

What would change this: {required_shift}. Until then, I would counsel
patience — or military pressure.

[Try anyway]  [What else could we do?]  [Understood]"
```

---

**T16: PROACTIVE — MORNING DISPATCH SUGGESTION**

```
"A diplomatic observation, Sire: {observation}.

{suggested_action_text}

Shall I pursue this? It would cost {dp_cost} DP.

[Yes, proceed]  [Tell me more]  [Not now]"
```
*Observations triggered by: relation_with_third_party changing, war score shift, vassal loyalty warning, alliance opportunity, Continental System opportunity.*

---

**T17: SABOTAGE CONFRONTATION**

```
"Sire, Berthier's agents have uncovered a discrepancy. The proposal
delivered to {target_nation} was not... precisely as you ordered.

  You ordered: {original_terms}
  Talleyrand delivered: {actual_terms}

{talleyrand_defense}

[Confront Talleyrand]  [Overlook it — perhaps he was right]"
```
*{talleyrand_defense}: "Sire, I adjusted the terms because {rationalization}. The result speaks for itself — {target_nation} accepted." or "I confess to a small modification. {excuse}. The outcome, however, is favorable."*

---

**T18: VAGUE + PEACE + NEUTRAL (no war, no strong feelings)**

```
"{target_nation} and France are at peace, Sire, though the air is
hardly warm. {target_diplomat} {neutral_posture}. Our options:

[1] Improve relations — assign me to court {target_nation}. Slow
    but steady, {mission_effect} per turn.

[2] Propose open borders — a low-commitment step that improves trade
    and builds trust.

[3] Gather intelligence — I can spend three turns learning their
    true intentions and alliances.

[4] Leave well enough alone — not every relationship requires tending.

{schemer_recommendation}"
```

---

**T19: VAGUE + PEACE + HOSTILE (not at war, but relations are terrible)**

```
"A delicate situation, Sire. {target_nation} is at peace with us
in name only — relations stand at {relation}. {target_diplomat}
{hostile_posture}.

[1] Improve relations urgently — assign me to intensive diplomacy.
    We need to prevent {target_nation} from joining the coalition.

[2] Propose non-aggression — a formal commitment might stabilize
    things, if they'll agree. My assessment: {difficulty_tier}.

[3] Prepare for the worst — if {target_nation} joins the war,
    we need our forces positioned accordingly.

Time is not on our side here, Sire. {target_diplomat} is {ai_activity}."
```

---

**T20: MISSION RECOMMENDATION**

```
"If you wish, Sire, I can dedicate my efforts to {mission_type} with
{target_nation}. This would cost {dp_cost} DP per turn and produce
{mission_effect}.

Currently {current_status}. {tradeoff_note}

[Begin this mission]  [What about other options?]  [Not now]"
```
*{tradeoff_note}: "This would mean pausing my current work on Austria" or "I am currently idle — an efficient use of my time."*

---

**T21: VAGUE + WAR + WINNING_SLIGHTLY**

```
"We hold the advantage against {target_nation}, Sire, though not yet
decisively. {target_diplomat} is under pressure but not desperate.

[1] Offer generous peace now — lock in our gains before the tide turns.
    Open borders and {suggested_gold} gold/turn. (Costs 2 DP)

[2] Push for better terms — one more victory would strengthen our hand
    considerably. Continue fighting with an eye toward a stronger peace.

[3] Propose an armistice — freeze the lines while we address other fronts.
    Less commitment than peace, but buys time. (Costs 1 DP)

Our position is good but not commanding, Sire. I favor peace while fortune
smiles on us — but I understand the temptation to press further."
```
*Recommendation: 0 (peace). Schemer bias: moderate expansion aversion.*

---

**T22: VAGUE + WAR + LOSING_SLIGHTLY**

```
"The situation with {target_nation} grows concerning, Sire. Our war score
stands at {war_score} — not catastrophic, but the trend is unfavorable.
{target_diplomat} senses opportunity.

[1] Sue for peace — accept moderate terms now before they worsen. The
    longer we wait, the harsher {target_diplomat}'s demands. (Costs 2 DP)

[2] Propose armistice — stop the bleeding without conceding defeat.
    Three turns to regroup. (Costs 1 DP)

[3] Fight on — a single victory reverses the dynamic entirely. But
    defeat would make the eventual peace far more expensive.

I would not normally counsel retreat, Sire, but diplomacy is not retreat.
It is the art of choosing one's battles."
```
*Recommendation: 0 (peace). Schemer bias: strongly favors de-escalation when losing.*

---

**T23: VAGUE + PEACE + FRIENDLY (post-peace, ally management)**

```
"Our relations with {target_nation} are {relation_description}, Sire.
{target_diplomat} {friendly_posture}. A fine foundation to build upon.

[1] Propose an alliance — formalize our friendship. Mutual defense
    would deter would-be aggressors. (Costs 2 DP)

[2] Propose open borders — trade and passage rights.
    Strengthens the bond without the commitment of alliance. (Costs 1 DP)

[3] Maintain the status quo — not every friendship needs a treaty.
    Save our diplomatic resources for more pressing matters.

The Diplomatic Ledger (D key) has the precise figures if you wish
to verify my assessment, Sire."
```
*Recommendation: 0 (alliance). Schemer bias: favors stabilizing alliances. Note: Option [2] proposes OPEN_BORDERS (SPEC §5a), not a custom "trade agreement" — no such state exists.*

---

**T24: MEDIUM (PEACE) + WAR + LOSING**

```
"Peace, Sire? Under these circumstances, it will not come cheaply.
{target_diplomat} holds the stronger hand — our war score stands at
{war_score}. To have any hope of acceptance, I suggest:

  Peace treaty. France offers open borders.
  France pays {suggested_gold} gold per turn.
  {optional_concession}

My assessment: {difficulty_tier}. {formula_hint}. (Costs 2 DP)

I will not deceive you, Sire — these are hard terms. But they are
better than the terms we will face in three more turns of defeats.

[Send these terms]  [Less generous — I won't grovel]  [Let me specify]
[Not now — we fight on]"
```
*{optional_concession}: territory cession if war_score < -30.*

---

**T25: MEDIUM (ALLIANCE) + PEACE + NEUTRAL**

```
"An alliance with {target_nation}? Ambitious, Sire. {target_diplomat}
is neither hostile nor friendly — relations stand at {relation}.
An alliance from neutral ground requires incentive:

  Defensive alliance with open borders.
  France offers {suggested_gold} gold per turn as a gesture.
  {optional_sweetener}

My assessment: {difficulty_tier}. {formula_hint}. (Costs 2 DP)

{target_diplomat_personality_note}

Of course, Sire, there is a cheaper path — improving relations first
makes the eventual alliance less expensive. The choice is yours.

[Propose alliance]  [Improve relations first (mission)]
[Start with non-aggression]  [Let me specify]"
```
*{optional_sweetener}: protection guarantee if threat > 30.*

---

**T26: SPECIFIC + TALLEYRAND_OBJECTS (STRONG)**

```
"Sire — I must speak plainly. These terms are {objection_reason}.
{target_diplomat} will not merely refuse — {strong_prediction}.

{strategic_warning}

I have served France through revolution and empire. I tell you now:
this course leads to {dire_consequence}. I urge you to reconsider.

My alternative: {modification_summary}.

[Send my terms as ordered]  [Use your suggestion]  [Modify terms]"
```
*STRONG objection language: "will unite every court in Europe against us" / "is how empires fall" / "guarantees a coalition." Defiance possible on "Send my terms as ordered."*

---

**T27: FEASIBILITY — CHALLENGING (30-49 projected acceptance)**

```
"Can we reach terms with {target_nation}? Possible, Sire, but it
will require effort — and perhaps concessions.

The key factor working for us: {largest_positive}.
Working against us: {largest_negative}.

I would rate this as: {difficulty_tier} — not impossible, but far
from certain.

The most effective path: {actionable_hint}. Alternatively,
{fallback_approach} would improve our odds over {turns_estimate} turns.

[Proceed with a proposal]  [Improve relations first]
[What exactly would tip the scales?]  [Not now]"
```
*Covers the 30-49 "interesting middle" that T14 (achievable, 50+) and T15 (impossible, <30) don't address.*

### 4c. Dynamic Slot Resolution

Templates contain `{slots}` resolved at runtime from game state:

```python
SLOT_RESOLVERS = {
    # Null-safe: all resolvers handle None returns from world methods.
    # Nations without diplomats (carved vassals) use fallback text.
    # Golden Rule #2: All numeric slots MUST return int() before reaching Godot.
    # Resolvers returning numbers must wrap in int().
    "target_diplomat": lambda w, n: _safe_diplomat_name(w, n),
    "target_nation": lambda w, n: n,
    "their_capital": lambda w, n: (w.get_nation_capital(n) or "their capital"),
    "suggested_gold": lambda w, n: _suggest_gold_per_turn(w, n)[0],  # unpack int from (gold, is_sufficient) tuple
    "relation": lambda w, n: int(w.get_nation_relation("France", n)),
    "relation_description": lambda w, n: _relation_description(w, n),
    "difficulty_tier": lambda w, n: _get_feasibility_tier(w, n),
    "formula_hint": lambda w, n: _get_formula_feedback(w, n),
    "war_score": lambda w, n: int(w.get_war_score("France", n)),
    "threat_increase": lambda w, n: _threat_delta(proposal_type),
    "target_diplomat_personality_note": lambda w, n: _safe_personality_note(w, n),
    # ... etc
}

def _safe_diplomat_name(world, nation):
    """Null-safe diplomat name — carved vassals may lack diplomats."""
    diplomat = world.get_diplomat(nation)
    return diplomat.name if diplomat else "their representatives"

def _safe_personality_note(world, nation):
    """Null-safe personality note — returns empty string for nations without diplomats."""
    diplomat = world.get_diplomat(nation)
    if not diplomat:
        return ""
    # ... personality-based note generation


def _relation_description(world, nation):
    """Natural language for relation value."""
    rel = world.get_nation_relation("France", nation)
    if rel > 40:  return "warm and promising"
    if rel > 10:  return "cautiously positive"
    if rel > -10: return "cool but stable"
    if rel > -40: return "hostile and deteriorating"
    return "deeply hostile — war may be inevitable"

def _suggest_gold_per_turn(world, nation):
    """Suggest gold amount that would make acceptance formula work.
    Returns (gold_amount, is_sufficient) tuple.
    Cached per (nation, turn) to avoid repeated calculation."""
    cache_key = (nation, world.turn)
    if cache_key in _gold_suggestion_cache:
        return _gold_suggestion_cache[cache_key]

    for gold in range(100, 501, 50):
        projected = _project_acceptance(world, nation, gold_per_turn=gold)
        if projected > 45:
            _gold_suggestion_cache[cache_key] = (gold, True)
            return (gold, True)

    # No amount of gold works — template should switch to honest assessment
    _gold_suggestion_cache[cache_key] = (500, False)
    return (500, False)

_gold_suggestion_cache = {}  # cleared on turn advance

# When is_sufficient is False, template text changes:
# Instead of "{suggested_gold} gold/turn should suffice"
# Use: "No amount of gold alone will overcome {largest_negative}.
#       Military pressure or relation improvement is needed first."
```

### 4d. Personality Modifier on Template Selection

Talleyrand is always Schemer. But the template library supports personality variants for future diplomats:

```python
def select_template(situation, game_bucket, specificity, personality=None):
    """Select best template, applying personality modifier to recommendation.
    personality: Read from world.get_diplomat("France").personality at call time.
    Defaults to "schemer" for Talleyrand, but MUST be dynamic — Replace with Loyalist
    (SPEC §3d) changes this to "loyalist", disabling all Schemer bias logic below."""
    if personality is None:
        personality = "schemer"  # fallback, but callers should pass actual value
    base = DIPLOMATIC_TEMPLATES[(situation, game_bucket, specificity)]

    if personality == "schemer":
        # Talleyrand prefers restrained expansion, stability
        # Shifts recommendation toward peace when winning
        # Shifts recommendation toward survival when losing
        if game_bucket == "winning_comfortably":
            base["recommendation"] = 0  # Always recommend peace when winning
        # Add Schemer-flavored asides — vary insertion point to avoid
        # mechanical feeling (before recommendation, between options, as postscript)
        aside = random.choice(SCHEMER_ASIDES[situation])
        insertion = random.choice(["before_recommendation", "after_options", "postscript"])
        if insertion == "before_recommendation":
            base["text"] = base["text"].replace("{recommendation_line}", aside + "\n\n{recommendation_line}")
        elif insertion == "postscript":
            base["text"] += "\n\n" + aside
        else:  # after_options (default)
            base["text"] += "\n\n" + aside

    return base

SCHEMER_ASIDES = {
    "peace_from_winning": [
        "*A generous peace is remembered longer than a harsh one, Sire.*",
        "*Victory is sweetest when it leaves the enemy grateful, not vengeful.*",
    ],
    "vassalage_demand": [
        "*A willing vassal is worth ten conquered provinces, Sire.*",
        "*Empires built on fear crumble. Those built on interest endure.*",
    ],
    # ...
}
```

---

## §5. Talleyrand's Voice

### 5a. Character Pillars

Talleyrand is:
1. **Brilliant** — His advice is genuinely good ~70% of the time. He sees angles the player misses.
2. **Self-serving** — ~30% of the time, his advice subtly favors his own vision (restrained France, European balance of power). The player learns to detect this.
3. **Urbane** — Never rude, never panicked. Even bad news comes wrapped in silk. "Our position is... not without its challenges, Sire."
4. **Strategic** — Thinks in terms of European balance, not just France's immediate gain. "Crushing Prussia today creates a problem for the next decade."
5. **Loyal-ish** — He serves France. Or rather, he serves what he believes France should be. Not always the same thing as what Napoleon believes France should be.

### 5b. Voice Patterns (Mock Mode)

Templates use consistent linguistic patterns to create Talleyrand's voice:

**Hedging when he disapproves:** "I must counsel caution..." / "There are... subtleties..." / "Sire, I wonder if perhaps..."

**Confidence when he approves:** "An excellent choice, Sire." / "Precisely what I would have advised." / "The courts of Europe will take notice."

**Manipulation markers:** "It costs us nothing..." (always suspect) / "Personally, I would add..." (Schemer bias) / "Of course, there are considerations that a purely military mind might overlook..." (flattering insult)

**Historical anchoring:** "We must not repeat the mistake of..." / "Tilsit showed us that..." / "The Continental System, as currently conceived..."

### 5c. Schemer Bias in Conversation

Talleyrand's Schemer personality biases his conversation in specific, predictable ways that the player can learn to detect:

| Game State | Talleyrand's Bias | How It Manifests |
|---|---|---|
| France winning, threat > 50 | Overstates risk of harsh terms | "Demanding Berlin will unite ALL of Europe against us" (true but exaggerated) |
| France winning, threat < 30 | Honest — no bias needed | Straight assessment |
| France losing | Honest — survival aligns with his goals | Urgent but accurate |
| Neutral nation relation > +20 | Understates difficulty of alliance | "Austria is practically on our doorstep" (optimistic by one tier) |
| Player proposing war on neutral | STRONG objection, threat-based | "This is how coalitions are born, Sire" (genuine wisdom AND self-interest) |
| Vassal being harsh | Pushes for generous terms | "A willing vassal is worth ten conquered provinces" |

**The 70/30 rule in mock mode (condition-based, not random):** Bias triggers when ALL of a row's bias conditions in the table above are met (e.g., threat > 50 for "overstates risk" bias, relation > +20 for "understates difficulty" bias). When bias conditions are NOT met, the recommendation is formula-optimal (no shift). When conditions ARE met, the selected template shifts the recommendation by one option toward Talleyrand's preferred outcome. This makes bias fully deterministic — same game state always produces the same recommendation. The "70/30" ratio emerges from how often bias conditions are satisfied across typical gameplay, not from a random roll. The mechanical data (acceptance scores, war scores) is always accurate in the dialogue — only the RECOMMENDATION is biased.

### 5d. Proactive Suggestions — "Talleyrand's Report"

Talleyrand should occasionally bring things up without being asked. This makes him feel alive.

**Delivery mechanism: Morning Dispatch section.** After Berthier's military report, Talleyrand gets 0-2 paragraphs:

```
═══ DIPLOMATIC REPORT — Talleyrand ═══

"Sire, I've noticed Austrian relations with Prussia cooling. Metternich
plays both sides, but his patience may be running thin. This could be
an opportunity — or a warning."

  → [Ask Talleyrand to elaborate] [Dismiss]
```

**Trigger conditions for proactive suggestions:**

| Trigger | Cooldown | Priority | Example |
|---|---|---|---|
| Nation relation crossed a threshold (-40, -20, 0, +20, +40) | 5 turns per nation | HIGH | "Relations with Austria have improved to cautiously positive..." |
| War score shifted >15 in one turn | 3 turns | HIGH | "Our victory has dramatically shifted the diplomatic landscape..." |
| Enemy AI began a diplomatic mission targeting France's ally/vassal | Immediate | HIGH | "I have reason to believe Prussian agents are active in Saxony..." |
| Diplomatic opportunity (acceptance formula for a beneficial proposal crossed 50) | 10 turns per nation | MEDIUM | "Sire, I believe Hardenberg may be ready to discuss peace..." |
| Vassal loyalty dropped below 40 | 5 turns per vassal | MEDIUM | "Unrest in Saxony, Sire. The situation requires attention." |
| Alliance expired or degraded automatically | Immediate | HIGH | "Our alliance with Austria is deteriorating..." |
| No diplomatic action taken for 3+ turns | Once | LOW | "Sire, the diplomatic front has been quiet. Perhaps too quiet." |

**Existence guard:** Before generating any proactive suggestion, verify the target entity still exists. Specifically: check vassal still exists in `world.vassals` before generating vassal loyalty suggestions (a vassal that rebelled at turn start should not generate a loyalty warning in the same turn's dispatch). Check nation still exists (not fully conquered/dissolved) before generating nation-specific suggestions.

**Frequency cap:** Maximum 2 diplomatic observations per dispatch. Highest priority wins. If nothing triggers, Talleyrand is silent (no filler text).

**Cooldown serialization:** Trigger cooldowns are tracked in `world.proactive_suggestion_cooldowns` (Dict[str, int], key format "nation|trigger_type", value = turns remaining). Added to SPEC §13 field list. Must serialize via to_dict/from_dict. Cooldowns decrement by 1 each turn during advance_turn() step 9 (§7f processing order).

**AI proposal suppression:** If an incoming AI proposal is pending for this turn, suppress proactive suggestions. Talleyrand is "busy" handling the incoming proposal. The suppressed suggestion can re-trigger next turn if conditions still hold.

**Player acts on suggestion:** The `[Ask Talleyrand to elaborate]` button opens a dialogue whose type depends on the trigger:

| Trigger Type | Elaboration Routes To | Rationale |
|---|---|---|
| Diplomatic opportunity (acceptance crossed 50) | `proposal_options` | Opportunity → actionable proposal |
| War score shifted | `advisory` | Military update → strategic analysis |
| Enemy courting vassal | `advisory` | Threat → threat assessment |
| Vassal loyalty drop | `advisory` | Warning → situation analysis |
| Relation threshold crossed | `advisory` or `proposal_options` (if positive threshold) | Depends on direction — positive = opportunity, negative = warning |
| Alliance decay | `advisory` | Degradation → what to do about it |
| No diplomatic action for 3+ turns | `proposal_options` | Nudge toward action |

Not all suggestions lead to proposals. Threat assessments and loyalty warnings route to advisory conversations, not proposal builders.

---

## §6. Enemy Diplomat Voices

### 6a. Response Personality by Type

When proposals reach the enemy court, the acceptance formula decides the outcome (unchanged). But the RESPONSE TEXT varies by diplomat personality:

**HAWK (Castlereagh, Hardenberg) — Responses:**

| Outcome | Response Style |
|---|---|
| ACCEPT | Grudging, face-saving. "Britain does not negotiate with conquerors — but we will accept this... arrangement. Do not mistake pragmatism for weakness." |
| COUNTER | Demanding, prideful. "These terms are insufficient. Prussia's honor demands at minimum: {counter_terms}. Take it or leave it." |
| REJECT | Contemptuous, defiant. "France overreaches. Hardenberg tears your proposal in half. 'Tell your Emperor that Prussia remembers.'" |

**SCHEMER (Metternich) — Responses:**

| Outcome | Response Style |
|---|---|
| ACCEPT | Calculating, positioning. "An interesting proposal. Austria finds it... adequate. For now. Metternich signs with a smile that doesn't reach his eyes." |
| COUNTER | Probing, extractive. "Metternich studies the terms with great interest. He has... suggestions. Small modifications, really. {counter_terms}." |
| REJECT | Polite, non-committal. "Metternich regrets that the current proposal does not align with Austrian interests. Perhaps in time the circumstances will change." |

**DOVE (Einsiedel) — Responses:**

| Outcome | Response Style |
|---|---|
| ACCEPT | Relieved, grateful. "His Majesty is grateful for France's continued... attention. Saxony accepts with humble thanks. Einsiedel bows deeply." |
| COUNTER | Nervous, apologetic. "Einsiedel wrings his hands. 'His Majesty asks most respectfully if perhaps the tribute could be... reduced? Saxony is small, as you know.'" |
| REJECT | Fearful, formal. "Einsiedel pales but delivers his message. 'Saxony cannot accept terms that would render the kingdom... insolvent. We beg France's understanding.'" |

### 6b. Talleyrand's Commentary on Enemy Responses

**Counter-offer at 0 DP:** When the player receives a counter-offer but has 0 DP (cannot afford to renegotiate at 1 DP), Talleyrand's recommendation acknowledges the constraint: "I'd suggest we renegotiate, but we lack the diplomatic capital. Accept or reject — those are our options, Sire." The [Renegotiate] option shows "(1 DP — insufficient)" and is soft-blocked.

After delivering the enemy's response, Talleyrand adds his own assessment:

```python
TALLEYRAND_RESPONSE_COMMENTARY = {
    ("hawk", "accept"): [
        "Hardenberg's pride is wounded, but discipline holds. He will honor this treaty — for now.",
        "A Hawk who accepts peace is a Hawk who remembers. Keep your army ready, Sire.",
    ],
    ("hawk", "reject"): [
        "Hardenberg is posturing, Sire. He'll break. Another battle should convince him.",
        "Pride before survival. A common failing among military minds.",
    ],
    ("schemer", "accept"): [
        "Metternich accepted too quickly. He's getting something we didn't see. Watch Austria closely.",
        "The spider has agreed. I wonder what web he's already spinning with these terms.",
    ],
    ("schemer", "reject"): [
        "Metternich stalls for leverage. He wants us to sweeten the deal — or he's waiting for our position to weaken.",
        "A Schemer's refusal is never final. It's an invitation to negotiate on his terms.",
    ],
    ("dove", "accept"): [
        "Einsiedel is relieved. Saxony will be a loyal partner — as long as we protect them.",
        "A willing friend, Sire. Treat them gently and they'll serve us for a generation.",
    ],
    ("dove", "reject"): [
        "Even Einsiedel has limits, Sire. We asked too much of a small nation.",
        "When a Dove refuses, the terms truly were too harsh. Consider moderating.",
    ],
}
```

---

## §7. Information Architecture

### 7a. Two Paths to Information

| Path | Interface | Character | Accuracy | Use Case |
|---|---|---|---|---|
| **Ask Talleyrand** | Conversation (typed command) | Personality-colored | 70-100% (Schemer bias) | "What's the situation with Austria?" |
| **Diplomatic Ledger** | Data screen (D key) | Raw numbers | 100% accurate | Check exact relation values, treaty terms, war scores |

**These complement, not duplicate.** Talleyrand gives you the STORY ("Austria wavers — Metternich plays both sides but fears our army. I estimate relations at roughly -25."). The Ledger gives you the NUMBERS (France-Austria Relation: -30, State: PEACE, Threat: 45).

### 7b. Talleyrand's Assessments Can Be Wrong

Talleyrand's verbal relation estimates have an accuracy band based on his skill and Schemer bias (§2g of DIPLOMACY_SPEC). When he says "relations are approximately -25," the real value might be -30. When he says "Achievable with modest effort," it might actually be "Challenging."

**The player learns to calibrate.** After a few proposals where Talleyrand said "this should work" and it didn't, the player learns to check the Ledger. After a few where Talleyrand said "this is impossible" and the Ledger shows it was close, the player learns to question his pessimism about harsh terms.

**This is deliberate gameplay.** The tension between "trust your advisor" and "check the numbers yourself" is part of the diplomatic experience. It mirrors the historical tension: Napoleon trusted Talleyrand's assessments for years before realizing Talleyrand was subtly steering French policy toward moderation.

### 7c. When to Use Which

| Player Intent | Use Talleyrand | Use Ledger |
|---|---|---|
| "What should I do?" | Yes — advisory conversation | No |
| "What are the exact numbers?" | No | Yes — Tab 1 Nation Overview |
| "Is this proposal realistic?" | Yes — feasibility check | Check after for verification |
| "What treaties do we have?" | Either | Yes — Tab 2 Active Treaties |
| "What's Talleyrand doing?" | Either ("Talleyrand, status") | Yes — Tab 4 Talleyrand Status |
| "What happened in recent diplomacy?" | Morning Dispatch | Campaign Log |

---

## §8. Strategic Conversations — The "What If" Advisor

### 8a. The Advisory Pattern

The player can ask Talleyrand strategic questions. These aren't proposals — they're conversations about the state of the world.

**Availability during IN_TRANSIT:** Advisory questions are available even when Talleyrand is IN_TRANSIT carrying a proposal. Narratively, Talleyrand's network of agents and correspondents keeps him informed even while traveling. Mechanically, advisory is a 0-DP momentary state that doesn't conflict with transit. Proposal creation remains blocked during IN_TRANSIT (only one proposal at a time).

**Mock mode keyword detection:**

```python
ADVISORY_KEYWORDS = {
    "what about": "assess_nation",
    "what should": "recommend_action",
    "who is": "compare_threats",
    "should i": "recommend_action",
    "what happens if": "predict_outcome",
    "what if": "predict_outcome",
    "bigger threat": "compare_threats",
    "focus on": "recommend_priority",
    "can we": "feasibility",
    "how do we": "recommend_action",
}

# m7: Question detection for mock parser — needed for is_question field
def _detect_question(text):
    """Detect if text is a question (advisory routing depends on this)."""
    text = text.strip()
    if text.endswith("?"):
        return True
    lower = text.lower()
    question_starters = ["what", "who", "how", "should", "can", "could",
                         "will", "would", "is", "are", "do", "does"]
    return any(lower.startswith(s + " ") for s in question_starters)
```

### 8b. Five Advisory Conversation Examples

**Example 1: Threat Comparison**

```
PLAYER: "Talleyrand, who's the bigger threat — Britain or Austria?"

TALLEYRAND: "An astute question, Sire. Britain is implacable — Castlereagh
will never accept French dominance on the continent. But Britain fights
with gold, not soldiers. Their continental forces are limited.

Austria is the more immediate danger. Metternich sits at -30 relations
with a defensive alliance with both Britain AND Prussia. If he joins
the war, we face 60,000 additional troops on our eastern flank.

My assessment: Austria is the urgent threat. Britain is the enduring one.
Address Austria first — court her, or crush her, but do not ignore her.

[What should we do about Austria?]  [And Britain?]  [Thank you]"
```

*Mock mode: Compares army sizes, relations, alliance networks. "Urgent" = hostile + large army + shares border. "Enduring" = at war + no way to eliminate.*

**Example 2: Predictive Question**

```
PLAYER: "Talleyrand, if we beat Austria at Vienna, would Prussia sue for peace?"

TALLEYRAND: "A decisive victory at Vienna would certainly shift the
diplomatic landscape. Currently, our war score against Prussia stands
at {war_score}. A major Austrian defeat would:

  - Eliminate Austria as Prussia's potential ally
  - Demonstrate French military supremacy
  - Isolate Prussia diplomatically

I estimate Hardenberg would become receptive to peace within 2-3 turns
of an Austrian collapse — provided our terms are reasonable. He is proud,
but not foolish.

However, Sire — this assumes we WIN at Vienna. Archduke Charles is
no amateur.

[What terms would Prussia accept?]  [How do we prepare for Vienna?]
[Thank you]"
```

*Mock mode: Evaluates hypothetical acceptance formula with boosted war_score and relation_modifier (Austria defeat = +15 war score vs Prussia, +10 relation from fear).*

**Example 3: Priority Recommendation**

```
PLAYER: "Should I focus on military victory or diplomatic solution with Prussia?"

TALLEYRAND: "That depends on your goals, Sire.

  MILITARY PATH: Capture Berlin (2-3 turns of offensive), then dictate
  terms. Costs AP, risks casualties, but results in stronger position.
  War score is currently {war_score} — you need approximately +40 more
  for submission terms.

  DIPLOMATIC PATH: Improve relations (3-4 turns), then propose peace.
  Costs DP, preserves army strength, but terms will be moderate. Current
  acceptance projection: {projected_acceptance}.

  COMBINED: Win one more battle, THEN propose. Military pressure makes
  diplomatic solutions cheaper.

I favor the combined approach. A single decisive victory followed by
generous terms — the Tilsit model.

[Focus on military]  [Focus on diplomacy]  [Combined approach]"
```

*Mock mode: Compares AP cost of military path vs DP cost of diplomatic path. "Combined" always recommended by Schemer when war_score is positive but below 40.*

**Example 4: Open-Ended Situation Assessment**

```
PLAYER: "Talleyrand, what's our diplomatic situation?"

TALLEYRAND: "An overview, Sire:

  BRITAIN — At war. Castlereagh is unyielding. Peace requires either
  total military victory or a continental settlement that makes war
  pointless for them. Long-term problem.

  PRUSSIA — At war. Bloodied but fighting. War score: {score}. Peace
  is possible if we offer reasonable terms. Priority: moderate.

  AUSTRIA — At peace, but hostile. Relations: {rel}. Metternich is
  watching. If we stumble, he joins the coalition. Priority: URGENT.

  SAXONY — Friendly. Potential vassal or ally. Low priority but
  easy win.

My recommendation: secure Austria before it's too late. An Austrian
alliance — or at minimum, non-aggression — changes everything.

[Tell me more about Austria]  [What about Prussia?]  [Thank you]"
```

*Mock mode: Iterates over all nations, generates one-liner per nation based on (state, relation, war_score). Recommendation = nation with worst relation that isn't at war, or nation most likely to join coalition.*

**Overview template variants (prevent pattern fatigue in mock mode):** The open-ended overview has 4 structural variants, randomly selected:
1. **Standard** — iterates all nations alphabetically (Example 4 above).
2. **Threat-first** — leads with the biggest threat nation, then others briefly: "The Austrian question dominates everything else, Sire. ..."
3. **Opportunity-first** — leads with the best opportunity: "Good news first, Sire — Saxony is ripe for alliance. Now, the challenges..."
4. **Comparative** — picks the two most important nations and compares them directly: "The question, Sire, is whether Austria or Prussia poses the greater danger..."

**Example 5: "What Would It Take"**

```
PLAYER: "What would it take to flip Austria to our side?"

TALLEYRAND: "Austria — the great question of our era. Metternich's
price is high, Sire.

  Current acceptance for alliance: {projected_score}/50 — {difficulty_tier}.

  The key obstacle: {largest_negative_component}.
  Our strongest card: {largest_positive_component}.

  What would change this:
  - Improve relations to at least 0 ({turns_estimate} turns of courtship)
  - A decisive military victory to demonstrate we're the winning side
  - Offer Bavaria as territorial concession (+8 to acceptance)

  The Metternich factor: he's a Schemer. He won't commit until he's
  certain of the outcome. But once he commits, he commits fully.

[Begin courting Austria]  [What if we offered Bavaria?]
[Can we undermine the British-Austrian alliance?]"
```

*Mock mode: Runs the acceptance formula with hypothetical modifiers, identifies the gap, suggests the cheapest way to close it.*

---

## §9. Popup/UI Integration

### 9a. Diplomatic Dialogue Popup Design

Diplomatic conversations appear as full-width popups in the terminal area, similar to objection popups but with richer content:

```
╔══════════════════════════════════════════════════════════════╗
║  TALLEYRAND                                                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  "Prussia is bloodied but not broken, Sire. Hardenberg's    ║
║  pride won't accept submission, but he might accept peace    ║
║  if we're generous.                                          ║
║                                                              ║
║  I'd suggest offering open borders and 200 gold per turn.    ║
║  A protection guarantee would seal the deal — it costs us    ║
║  nothing and makes them feel safe."                          ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  [1] Send these terms          [2] Harsher terms             ║
║  [3] What else could we offer? [4] Cancel                    ║
╚══════════════════════════════════════════════════════════════╝
```

**Save/load mid-dialogue:** On game load, check `pending_diplomatic_dialogue`. If present and `blocking=True`, display the popup immediately (same pattern as `pending_objection` load handling). If present and `blocking=False`, display on next player input (non-blocking dialogues don't interrupt the load flow). The Godot client checks the field in its `_on_game_loaded()` handler and calls `_display_diplomatic_dialogue()` if set.

**Player responds by:**
- Pressing number keys (1-4) — fast, works in mock and LLM mode
- Typing a free response — LLM mode parses intent, mock mode tries keyword match and falls back to "Please choose an option (1-4)"

### 9b. Popup Response Flow

```
Player input during pending_diplomatic_dialogue:
  ↓
  Is it a number (1-4)?
    → Execute corresponding option action
  Is it a keyword match to an option? ("do it", "send", "cancel")
    → Execute matched option
  Is it a free text response?
    → LLM mode: parse intent, map to closest option or generate new response
    → Mock mode (1st attempt): "I'm not sure what you mean, Sire. Please choose: [1-4]"
    → Mock mode (2nd+ attempt): "Please choose an option (1-{n}), Sire.
      If you'd like to cancel this conversation, type 'cancel'."
  ↓
  **DP deduction timing:** DP is deducted when `execute_proposal` fires (when the
  player confirms "Send it"), NOT when the conversation begins. Cancelling a
  conversation at any point costs 0 DP. The player can explore options, modify
  terms, and consult Talleyrand freely — only the final "Send" commits resources.

  Option action:
    "execute_proposal" → Enter proposal transit (§2d of DIPLOMACY_SPEC). DP deducted HERE.
    "modify_harsh" → New dialogue with harsher terms (max 2 iterations — see below)
    "modify_generous" → New dialogue with softer terms
    "expand_options" → New dialogue listing clause types
    "begin_mission" → Start diplomatic mission (§2e)
    "elaborate" → New dialogue with more detail (depth +1, max 3 — see below)
    "cancel" → Clear dialogue, no action

  **Depth enforcement (advisory conversations):**
  At depth 3, all options must be terminal actions only (execute, dismiss, cancel,
  begin_mission). No "Tell me more" or "Elaborate" options appear. The template
  selection logic strips non-terminal options at max depth.

  **Modify_harsh iteration cap:**
  Maximum 2 modification iterations (original → harsher → even harsher). After 2
  modifications, the "Harsher" option is replaced with "Send these terms or specify
  your own." At maximum harshness, Talleyrand: "Sire, I cannot propose terms more
  severe than total subjugation. These are the harshest terms possible."

  **Modify_generous iteration cap:**
  Maximum 2 modification iterations (same as harsh). After 2 generous modifications,
  the "More generous" option is replaced with "Let me specify my own terms."
  At maximum generosity, Talleyrand: "Sire, we are offering everything short of
  the crown itself. Any more and we negotiate from our knees."
```

### 9c. Interaction with Existing Popup Systems

**Blocking priority hierarchy (strict, highest wins):**

1. `pending_objection` — combat/tactical objections (always top priority)
2. `pending_strategic_objection` — strategic order objections
3. `pending_diplomatic_dialogue` (blocking=True) — incoming AI proposals, sabotage confrontation
4. `pending_diplomatic_dialogue` (blocking=False) — player-initiated dialogues (advisory, proposal_options, etc.)

When a higher-priority state is set, lower-priority states are preserved but not displayed. The player resolves them in priority order. Strategic per-turn execution (`_strategic_execution = True`) ignores `pending_diplomatic_dialogue` entirely — it's autonomous and doesn't require player input.

**Blocking vs non-blocking dialogues:**

| Dialogue Type | Blocking? | End-Turn Behavior |
|---|---|---|
| `incoming_proposal` | **Yes** | Blocks end-turn. Player MUST respond (Accept/Reject/Counter). |
| `sabotage_confrontation` | **Yes** | Blocks end-turn. Player MUST choose (Confront/Overlook). |
| `proposal_options` | No | Auto-dismisses on end-turn. |
| `proposal_confirm` | No | Auto-dismisses on end-turn. |
| `proposal_execute` | No | Auto-dismisses on end-turn. |
| `advisory` | No | Auto-dismisses on end-turn. |
| `feasibility` | No | Auto-dismisses on end-turn. |
| `proactive_suggestion` | No | Auto-dismisses on end-turn. |

**Auto-dismiss trace:** When a non-blocking dialogue is auto-dismissed on end-turn, add a Morning Dispatch note: "Your discussion about {target_nation} was not concluded. Talleyrand awaits your direction." This prevents player confusion when context is lost between turns.

**Blocking dialogue response message (with current options):**

```python
# In executor.py, add to the pending check hierarchy:
if world.pending_diplomatic_dialogue is not None:
    dialogue = world.pending_diplomatic_dialogue
    # Include current options so player knows HOW to respond
    option_labels = [f"[{i+1}] {o['label']}" for i, o in enumerate(dialogue.get("options", []))]
    options_text = "  ".join(option_labels)
    return {
        "success": False,
        "message": f"Talleyrand awaits your response regarding {dialogue.get('target_nation', 'diplomacy')}. {options_text}",
        "awaiting_diplomatic_response": True,
        "diplomatic_dialogue": dialogue,
    }

# End-turn blocking check:
if world.pending_diplomatic_dialogue and world.pending_diplomatic_dialogue.get("blocking"):
    return {
        "success": False,
        "message": "You must respond to the diplomatic matter before ending the turn.",
        "awaiting_diplomatic_response": True,
        "diplomatic_dialogue": world.pending_diplomatic_dialogue,
    }
```

### 9d. New Endpoint

```python
# In main.py
@app.post("/respond_to_diplomatic_dialogue")
async def respond_to_diplomatic_dialogue(request: dict):
    """Handle player response to Talleyrand's dialogue.

    Request body:
        {"choice": int | str}
        - int (1-4): index of selected option
        - str: keyword or free text (LLM mode only for free text)

    Response body (success):
        {"success": True, "message": str, "diplomatic_dialogue": dict | None,
         "new_state": <stripped WorldState>}
        - If action triggers a new dialogue (e.g., "expand_options"),
          diplomatic_dialogue contains the new dialogue state.
        - If action is terminal (execute, cancel), diplomatic_dialogue is None.

    Response body (error):
        {"success": False, "message": str}
        - Invalid choice number: "Please choose an option (1-{n}), Sire."
        - No pending dialogue: "No diplomatic matter awaits your attention, Sire."
        - DP insufficient for chosen action: "Insufficient diplomatic resources."
    """
    choice = request.get("choice")
    world = game_state["world"]

    if world.pending_diplomatic_dialogue is None:
        return {"success": False, "message": "No diplomatic matter awaits your attention, Sire."}

    dialogue = world.pending_diplomatic_dialogue
    options = dialogue.get("options", [])

    # Resolve choice to option index
    if isinstance(choice, int):
        if choice < 1 or choice > len(options):
            return {"success": False,
                    "message": f"Please choose an option (1-{len(options)}), Sire."}
        selected = options[choice - 1]
    elif isinstance(choice, str):
        selected = _match_keyword_to_option(choice, options)
        if selected is None:
            return {"success": False,
                    "message": f"Please choose an option (1-{len(options)}), Sire."}
    else:
        return {"success": False, "message": "Invalid input."}

    # Execute the selected action
    result = _execute_dialogue_action(selected, dialogue, world)

    # Clear dialogue if terminal action
    if selected["action"] in ("execute_proposal", "cancel", "dismiss",
                               "begin_mission", "confront", "overlook"):
        world.pending_diplomatic_dialogue = None

    # Strip new_state before returning (CLAUDE.md serialization warning)
    cleaned = {k: v for k, v in result.items() if k != "new_state"}
    return cleaned
```

---

## §10. Diplomatic Objection & Confrontation System

### 10a. Design Assessment — Are Diplomatic Objections a Good Idea?

**Yes, but they must be PART of the conversation, not a separate system.**

In combat, objections interrupt the command flow: you say "attack," marshal objects, popup appears. This works because combat commands are atomic — one action, one objection point.

Diplomatic commands are conversational. When the player says "Talleyrand, offer peace to Prussia," Talleyrand's response IS the objection. He doesn't need a separate popup — his recommended terms already reflect his opinion, and his dialogue text explains why. If the player says "harsher terms," Talleyrand pushes back IN THE CONVERSATION.

**Recommendation: Merge objections into the conversation flow.** No separate `pending_objection` for diplomatic commands. Talleyrand's objections are expressed as dialogue within `pending_diplomatic_dialogue`.

### 10b. How Diplomatic Objections Manifest

Instead of the V2a MILD/MODERATE/STRONG popup pattern, diplomatic objections are graduated dialogue responses:

| Severity | In Combat | In Diplomacy |
|---|---|---|
| MILD | Flavor text, no popup | Talleyrand's suggestion differs from player's intent, mild language |
| MODERATE | Popup with choices | Talleyrand presents alternatives prominently, warns of consequences |
| STRONG | Popup, defiance possible | Talleyrand argues forcefully, options include "Send my terms as ordered" (defiance possible on this path) |

**Example — MODERATE diplomatic objection:**

```
PLAYER: "Talleyrand, demand Prussia cede Rhineland and pay 400 gold/turn"

TALLEYRAND: "Sire, I must counsel caution. Demanding Rhineland will ensure
Prussia never forgives us — Hardenberg will rally his nation for revenge.
And 400 gold per turn from an economy already strained by war?

The courts of Europe are watching. Harsh terms breed coalitions.

I would suggest: peace with open borders and 200 gold per turn. This
preserves our gains without creating an eternal enemy.

[Send my terms as ordered]  [Use Talleyrand's suggestion]  [Modify terms]"
```

If the player picks "Send my terms as ordered" — this is equivalent to "insist" in the V2a system. Defiance can now trigger per §3a of DIPLOMACY_SPEC.

### 10c. The Honesty Problem — Schemer Objections

**Key difference from combat:** When Ney objects, it's honest ("this is suicide"). When Talleyrand objects, it MIGHT be honest OR it might be manipulation.

**Design: Talleyrand's objection honesty varies, and the player can learn to tell the difference over time.**

| Signal | Honest Objection | Manipulative Objection |
|---|---|---|
| **Formula alignment** | Acceptance score really is low | Acceptance score is actually fine |
| **Threat accuracy** | Threat really would spike | Threat increase is moderate |
| **Consistency** | Talleyrand objected to similar proposals before | First time he objects to this type |
| **Ledger check** | Numbers confirm his warnings | Numbers contradict his warnings |
| **Post-outcome** | If overridden, bad result confirms wisdom | If overridden, good result reveals manipulation |

**How the player learns:** After overriding Talleyrand and getting a GOOD result (the proposal worked despite his warnings), a Morning Dispatch note appears: "Talleyrand's assessment of the Prussian court appears to have been... pessimistic." This teaches the player that sometimes Talleyrand's STRONG objection is him steering, not warning.

After overriding and getting a BAD result, the note is different: "Talleyrand's warnings about the Austrian reaction prove prescient." This reinforces that sometimes he genuinely knows better.

**Over 20-30 turns of play, the player develops an intuition:** "Talleyrand always objects to harsh terms against nations he likes (high relation). When he objects to something that the Ledger says should work, he's probably manipulating me. When he objects to something the Ledger says is risky, he's probably right."

This is the deepest form of the "disobedience as negotiation" philosophy: the player negotiates not just with foreign powers, but with their OWN diplomat.

### 10d. Two Objection Points

**Pre-proposal (prevention):** Talleyrand objects to terms before departing. Expressed as part of the conversation dialogue. Player can insist, modify, or trust. If insist → defiance possible during transit.

**Post-return (discovery):** If defiance triggered during transit, the terms Talleyrand delivered differ from what the player ordered. Discovery happens per §3c of DIPLOMACY_SPEC (40% base chance + 10%/turn). When discovered:

```
╔══════════════════════════════════════════════════════════════╗
║  DIPLOMATIC DISCREPANCY DISCOVERED                           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Berthier's agents report that the proposal delivered to     ║
║  Prussia was not precisely as you ordered.                   ║
║                                                              ║
║  You ordered:     Cede Rhineland, 400 gold/turn              ║
║  Talleyrand sent: Open borders, 200 gold/turn                ║
║                                                              ║
║  The result: Prussia ACCEPTED.                               ║
║                                                              ║
║  Talleyrand: "Sire, I adjusted the terms because demanding   ║
║  Rhineland would have ensured rejection. The result speaks   ║
║  for itself — we have peace."                                ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  [Confront] Trust -10, Authority +5, cooldown 5 turns        ║
║  [Overlook] Trust +3, Talleyrand gains confidence            ║
╚══════════════════════════════════════════════════════════════╝
```

This is a DRAMATIC MOMENT. The player discovers their trusted advisor went behind their back. The proposal might have succeeded (Talleyrand was right!) or might have been accepted on worse terms than necessary (Talleyrand was self-serving). Either way, the player must decide: punish the betrayal or accept the result.

### 10e. Building Blocks — Enemy Diplomat Objections

**Do enemy diplomats object to their own leaders?** Yes — simplified.

Enemy diplomats have personalities that color AI decisions. When the AI decision tree (§9) selects a diplomatic action, the enemy diplomat's personality can modify it:

- **Hawk** Castlereagh: blocks peace proposals when war score is above -20 ("we can still win"). AI must override or wait.
- **Schemer** Metternich: modifies harsh proposals to be slightly softer (same pattern as Talleyrand sabotage). This is observable: "Austria's counter-offer is surprisingly moderate — Metternich's hand, perhaps?"
- **Dove** Einsiedel: blocks aggressive actions (war declarations, harsh demands). Saxony's AI is constrained by its dove diplomat.

**Player exploitation:** The player can observe enemy diplomatic patterns and infer internal conflicts. "Austria keeps proposing moderate terms despite being in a strong position — Metternich is restraining them. If we can drive Austria to replace Metternich (via extreme military pressure), their next diplomat might be a Hawk who overreaches."

**Implementation note:** This is a v2 feature. For v1, enemy diplomat personality affects response TEXT only (§6), not AI behavior. The groundwork is in the architecture (personality → behavior modifier), but the behavioral effects are future scope.

### 10f. Recommendation Summary

| Aspect | Recommendation | Rationale |
|---|---|---|
| Separate objection popup? | **No** — merge into dialogue | Diplomacy is conversational; interruptions break flow |
| Objection severity visible? | **Implicitly** — via dialogue intensity | "I must counsel caution" = MODERATE; "This is madness" = STRONG |
| Honesty variation? | **Yes** — 70/30 honest/manipulative | Core Schemer identity; creates depth |
| Post-return confrontation? | **Yes** — dramatic popup | Best moment in the system; creates trust dilemma |
| Enemy diplomat objections? | **v2** — text-only in v1 | Architecture supports it; implementation deferred |
| Defiance trigger point? | On "Send my terms" after STRONG disagreement | Mirrors combat "insist" → defiance pattern |

---

## §11. Interaction with Existing Spec — What Changes

### 11a. DIPLOMACY_SPEC Sections Replaced

| Section | Status | Replacement |
|---|---|---|
| §2c (Commands) | **Keywords preserved, flow redesigned** | Commands now trigger dialogue, not direct execution |
| §2d (Proposal Flow) | **Mechanics preserved, presentation redesigned** | Transit/return mechanics unchanged. Popup presentation uses dialogue system |
| §2g (Feasibility) | **Enhanced** | Feasibility is now a conversation (T14/T15), not just a report |
| §9a (AI Proposals) | **Enhanced** | AI proposals delivered through dialogue system (T9/T10/T11) |
| §10b (Diplomatic Ledger) | **Unchanged** | Ledger remains a data screen; dialogue is complementary |

### 11b. DIPLOMACY_SPEC Sections Unchanged

| Section | Why |
|---|---|
| §1 (Nations, Map) | Pure data — no interaction layer |
| §3 (Defiance) | Mechanics unchanged; triggered from dialogue "insist" |
| §4 (DP) | Economy unchanged |
| §5 (States) | Transition mechanics unchanged |
| §6 (Acceptance Formula) | The engine — completely unchanged |
| §7 (Treaties) | Clause mechanics unchanged |
| §8 (Vassals) | Vassal mechanics unchanged |
| §9b/c (AI response/AI-AI) | AI behavior unchanged |
| §11 (Fog) | Intel mechanics unchanged |
| §12 (Edge Cases) | All edge cases still apply |

### 11c. New Systems Added

| System | File(s) | Purpose |
|---|---|---|
| Dialogue State Machine | `backend/game_logic/diplomatic_dialogue.py` (new) | Conversation flow, template selection, state management |
| Template Library | `backend/game_logic/diplomatic_templates.py` (new) | 20+ templates with slot resolution |
| Dialogue Router | Addition to `llm_client.py` | Classify specificity, route to dialogue engine |
| Dialogue Endpoint | Addition to `main.py` | `/respond_to_diplomatic_dialogue` |
| WorldState field | `world_state.py` | `pending_diplomatic_dialogue` (dict or None) — must serialize (see §2b) |
| Morning Dispatch section | `dispatch.py` | Talleyrand's Report (0-2 paragraphs) |
| Gold suggestion cache | `backend/game_logic/diplomatic_dialogue.py` | `_gold_suggestion_cache` — cleared on turn advance |

**Implementation note:** Update `docs/SAVE_FORMAT_REFERENCE.md` with `pending_diplomatic_dialogue` field definition. Update `docs/ROADMAP.md` Phase 8 to reference this design document and the 4-session plan.

---

## §12. Mock vs LLM Mode

### 12a. What's Identical

| Component | Mock | LLM |
|---|---|---|
| Dialogue structure | Same | Same |
| Options presented | Same 2-4 choices | Same 2-4 choices |
| Mechanical outcomes | Identical | Identical |
| Schemer bias | Same triggers, same direction | Same triggers, same direction |
| Template selection logic | Same | Same |
| Formula evaluation | Identical | Identical |

### 12b. What LLM Enhances

| Component | Mock | LLM |
|---|---|---|
| Dialogue text | Template with {slots} | Free-form prose with character voice |
| Advisory conversations | Structured analysis templates | Genuine conversational flow |
| Follow-up parsing | Keyword match to options | Natural language understanding |
| Talleyrand's asides | Random selection from list | Context-aware improvisation |
| Enemy diplomat responses | Template per personality | Personality-consistent prose |
| Free text input | Falls back to "choose 1-4" | Parses intent, maps to action |

### 12c. The Mock Mode Guarantee

**If it's not fun in mock, it's not fun.** LLM mode makes Talleyrand sound more human, but mock mode must:
- Present clear options that teach the player about the diplomacy system
- Make Talleyrand's personality visible through template word choices
- Give the player enough information to make informed decisions
- Create the feeling of advising with a person, not clicking a menu

The key to making mock feel conversational: **options are framed as advice, not as a list.** "I'd suggest the first option, Sire — but if you insist on harsher terms, I can present alternatives" is a conversation. "Select: A) Peace B) Demand C) Cancel" is a menu. Same options, radically different feeling.

---

## §13. Risk Assessment

### 13a. What Could Go Wrong

| Risk | Severity | Mitigation |
|---|---|---|
| Templates feel repetitive after 20 hours | HIGH | Large template library (20+ base × variants), slot-driven variety, LLM mode for replay |
| Dialogue depth slows gameplay | MEDIUM | Hard cap at 2-3 exchanges; "Send it" always available as escape hatch |
| Schemer bias is invisible to players | MEDIUM | Morning Dispatch hints when bias detected; Ledger provides ground truth |
| Mock free-text input feels broken | LOW | Clear "choose 1-4" fallback; free text is LLM-mode bonus, not mock expectation |
| Conversation state leaks across turns | LOW | Auto-dismiss `pending_diplomatic_dialogue` on turn advance |
| Dialogue blocks combat commands | MEDIUM | Clear "Cancel" option; auto-dismiss on turn end |

### 13b. What's Hardest to Get Right

1. **Template variety.** 27 base templates × 5 game state buckets × 5 nations = 675 potential combinations. Most share templates with slot substitution; advisory overview has 4 structural variants to prevent pattern fatigue.

2. **Schemer bias calibration.** Too subtle = invisible = pointless. Too obvious = annoying = player always ignores Talleyrand. The 70/30 split needs playtesting.

3. **Option labels.** Each option must be short enough to fit a button but descriptive enough to make the choice meaningful. "More generous" vs "Sweeten the deal" vs "Offer more" — word choice matters.

4. **Advisory conversation depth.** "What if" questions in mock mode require mapping natural language to formula queries. The keyword list must be comprehensive enough to catch most phrasings.

---

## §14. Implementation Plan — Unified with DIPLOMACY_SPEC

> **The conversation layer sessions (A-D) are merged into DIPLOMACY_SPEC §14's unified 7-session plan.** This section preserves file and test details; see DIPLOMACY_SPEC §14 for the authoritative session timeline.

### 14a. New Files

**Directory:** `backend/game_logic/` (flat structure, consistent with existing codebase patterns).

| File | Purpose | Estimated Size | Unified Session |
|---|---|---|---|
| `backend/game_logic/diplomatic_dialogue.py` | Dialogue state machine, classify_intent, build_dialogue | ~300 lines | Session 3 |
| `backend/game_logic/diplomatic_templates.py` | Template library, slot resolvers, personality modifiers | ~500 lines | Session 3 |
| `backend/game_logic/diplomatic_advisory.py` | Strategic conversation handlers, "what if" engine | ~200 lines | Session 4 |

### 14b. Modified Files

| File | Changes | Unified Session |
|---|---|---|
| `backend/ai/llm_client.py` | Add diplomatic keyword detection before marshal detection (~50 lines) | Session 3 |
| `backend/commands/executor.py` | Add `pending_diplomatic_dialogue` blocking check; dialogue response handler (~100 lines) | Session 3 |
| `backend/models/world_state.py` | Add `pending_diplomatic_dialogue` field + serialization (~15 lines) | Session 3 |
| `backend/main.py` | Add `/respond_to_diplomatic_dialogue` endpoint; wire dialogue into command flow (~60 lines) | Session 3 |
| `backend/game_logic/dispatch.py` | Add Talleyrand's Report section to morning dispatch (~80 lines) | Session 4 |
| `godot-client/.../main.gd` | Diplomatic dialogue popup rendering and input handling (~150 lines) | Session 7 |

### 14c. Session Mapping (Old → Unified)

| Old Session | Merged Into | DIPLOMACY_SPEC Session |
|---|---|---|
| **A** (Foundation) | Dialogue state machine + 10 templates + endpoint | **Session 3** (Talleyrand Commands) |
| **B** (Conversations) | Advisory + proactive + remaining templates | **Session 4** (AI Proposals) |
| **C** (Objections) | Merged objections + sabotage confrontation + voices | **Session 6** (Defiance) |
| **D** (UI + Polish) | Godot popup + calibration + blocking behavior | **Session 7** (Ledger UI + Polish) |

### 14d. Test Strategy

- **Template coverage:** Each template renders without errors for all 5 nations x all game state buckets
- **Dialogue flow:** Each dialogue type completes without stale state
- **Specificity routing:** Vague/medium/specific commands route correctly
- **Option execution:** Each option in each template produces the correct mechanical action
- **Serialization:** `pending_diplomatic_dialogue` survives save/load
- **Integration:** Dialogue system works with existing proposal transit, defiance, and acceptance formula

---

## §15. The Fun Argument

Every strategy game has diplomacy. In every one, it's a menu. Select proposal type. Add clauses. Click send. Wait for accept/reject. Repeat. It's spreadsheet management dressed up with flags and portraits.

Ink & Iron does something no strategy game has ever done: **diplomacy as conversation with a character who has opinions.**

When the player says "deal with Prussia," they don't get a dropdown. They get Talleyrand — brilliant, urbane, manipulative — laying out options and recommending the one that serves his vision of France. The player can follow his advice, override him, or ask him to explain. And sometimes, when they override him, he goes behind their back.

This creates three layers of gameplay that no menu can provide:

1. **The diplomatic game:** Negotiate treaties, manage alliances, prevent coalitions. The formula engine handles this. Every strategy game has it.

2. **The advisory game:** Learn to calibrate Talleyrand's bias. When he says "impossible," is it really impossible, or is he steering you? Check the Ledger. Compare his assessments to outcomes. Develop an intuition for when to trust and when to verify. No strategy game has this.

3. **The relationship game:** Over 30+ turns, develop a relationship with your diplomat. Sometimes trust him over the numbers. Sometimes punish his defiance. Sometimes realize he was right all along. The same "disobedience as negotiation" that makes combat special, now applied to the negotiating table. No strategy game has this either.

The mock mode guarantee means this isn't vaporware dependent on AI. Twenty carefully written templates, a smart slot system, and a state machine that makes option-picking feel like conversation — that's the game. LLM mode makes it sing, but mock mode makes it work.

**This is the feature that makes Ink & Iron unique.** Not the combat — though that's great. Not the marshals — though they're unforgettable. It's that you have a relationship with your foreign minister, and that relationship IS the diplomatic game.
