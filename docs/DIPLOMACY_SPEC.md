# Diplomacy System — Design Spec

> **Status:** DRAFT v2.0 — Full audit revision. 40+ findings addressed. Self-audit: 68/80 (Grade A). Needs final design gate approval before implementation.
> **Phase:** 8
> **Prerequisite:** Phase 7b COMPLETE. Jealousy system implementation may run in parallel.
> **Companion:** COALITION_SPEC.md (builds on this spec — threat level, coalition formation, coordinated AI). War score formula now defined inline (§6e) — COALITION_SPEC builds on it but no longer owns it.

---

## Design Philosophy

"Diplomacy is war by other means — and Talleyrand fights it better than you." The player doesn't click buttons on a diplomacy screen. They talk to Talleyrand, who talks to the world. He has opinions. He has his own agenda. He might not deliver the message you sent. The same personality-driven command loop that makes combat interesting (talk to marshals → they talk back → they might disobey) now extends to the negotiating table.

Historical anchor: Napoleon's diplomatic failures were as decisive as his military victories. The Continental System alienated allies. Harsh treaty terms bred resentment. Coalition after coalition formed because Napoleon couldn't stop conquering. Talleyrand — his own Foreign Minister — secretly worked to restrain French expansion, believing Napoleon's ambition would destroy France. He was right. The player's diplomatic challenge is the same: you CAN demand everything, but should you?

**Core principle:** Deterministic rules engine, LLM for flavor only. The Acceptance Formula decides if proposals succeed. Mock mode works identically — keyword parser for commands, canned personality-keyed responses. LLM explains WHY ("The Prussian court finds your terms... barely tolerable"), never decides IF.

---

## §1. Nations & The Expanded Map

### 1a. Five Nations

| Nation | Starting State vs France | Role | Capital | AP/Turn |
|--------|-------------------------|------|---------|---------|
| **France** | Player | Dominant military power | Paris | 4 |
| **Britain** | WAR | Major enemy, naval power (abstracted), hard to flip | — (off-map) | 4 |
| **Prussia** | WAR | Major enemy, CAN be flipped to neutral/ally | Berlin | 4 |
| **Austria** | PEACE (hostile) | Swing state — both sides court them. Relation -30. | Vienna | 3 |
| **Saxony** | PEACE (French-leaning) | Minor nation, vassalizable by treaty or conquest. Relation +40. | Dresden | 2 |

**Britain is special:** No capital on the map, no regions to conquer. British power is projected through continental holdings (Netherlands, Waterloo, Hanover) and naval supremacy (abstracted as economic/strategic effects — see §1d). Britain can lose all continental territory and still be at war. Peace with Britain requires diplomatic resolution, not military conquest. This makes them the diplomatic endgame — you can't just march to London.

**Nation-specific AP:** Reflects administrative capacity. France (4) is the most capable. Austria (3) is bureaucratic. Saxony (2) is tiny. This matters for treaty clauses that cost AP/turn — paying 1 AP/turn when you only have 2 is crippling.

### 1b. Expanded Map (18 Regions)

Expanded from 13 to 18. Goals: French strategic depth, Waterloo deathball broken, Austria on eastern edge, Saxony as central buffer. Layout designed to translate to 1805 full European map.

**APPROVED: 19 regions confirmed. Adjacency and starting forces need playtesting.**

```
                    [Netherlands]---[Hanover]---[Berlin]
                     /        \        |    \      |
                    /          \       |     \     |
              [Belgium]------[Waterloo]|   [Saxony]|
               /    \                  |    / |    |
              /      \                 |   /  |  [Bohemia]
         [Normandy] [Rhineland]--------+-/   |    |
            |    \      |              |     |    |
            |     \     |          [Bavaria]-+--[Vienna]
        [Brittany] [Paris]            |      |    |
                \    |            [Tyrol]-----+   |
              [Bordeaux]            |             |
                   |            [Milan]-----------+
              [Lyon]---[Marseille]   |
                  \                  |
                   +-----[Milan]----+

(Simplified — see adjacency table for exact connections)
```

#### Region Table

| # | Region | Type | Terrain | Income | Controller | Notes |
|---|--------|------|---------|--------|------------|-------|
| 1 | **Paris** | capital | urban | 300 | France | French capital |
| 2 | **Normandy** | town | plains | 100 | France | NEW — western depth |
| 3 | **Brittany** | rural | forest | 50 | France | Unchanged |
| 4 | **Bordeaux** | rural | plains | 50 | France | Unchanged |
| 5 | **Lyon** | major_city | hills | 200 | France | Unchanged |
| 6 | **Marseille** | city | plains | 150 | France | Unchanged |
| 7 | **Belgium** | town | plains | 100 | France | French frontier |
| 8 | **Milan** | city | urban | 150 | France | French Italy |
| 9 | **Netherlands** | rural | plains | 50 | Britain | British continental |
| 10 | **Waterloo** | rural | hills | 50 | Britain | Wellington's position |
| 11 | **Hanover** | town | plains | 100 | Britain | British crown territory |
| 12 | **Berlin** | capital | urban | 250 | Prussia | NEW — Prussian capital |
| 13 | **Rhineland** | town | river_crossing | 100 | Prussia | Renamed from "Rhine" |
| 14 | **Saxony** | city | plains | 150 | Saxony | NEW — buffer state |
| 15 | **Dresden** | town | hills | 100 | Saxony | NEW — Saxon capital |
| 16 | **Bavaria** | town | hills | 100 | Austria | Austrian sphere |
| 17 | **Vienna** | capital | urban | 300 | Austria | Austrian capital |
| 18 | **Bohemia** | city | forest | 150 | Austria | NEW — northern Austria |
| 19 | **Tyrol** | town | mountains | 100 | Austria | NEW — Alpine barrier |

**19 regions confirmed.** Dresden gives Saxony a proper capital — "capture Dresden" is a clearer objective than "occupy the Saxony region." One extra region is worth it for QA coverage of vassalage gameplay.

#### Adjacency Table

| Region | Adjacent To |
|--------|------------|
| Paris | Normandy, Belgium, Lyon, Bordeaux |
| Normandy | Paris, Brittany, Belgium |
| Brittany | Normandy, Bordeaux |
| Bordeaux | Brittany, Paris, Lyon, Marseille |
| Lyon | Paris, Bordeaux, Marseille, Rhineland, Milan |
| Marseille | Lyon, Bordeaux, Milan |
| Belgium | Paris, Normandy, Netherlands, Waterloo, Rhineland |
| Milan | Lyon, Marseille, Tyrol, Vienna |
| Netherlands | Belgium, Waterloo, Hanover |
| Waterloo | Belgium, Netherlands, Hanover |
| Hanover | Netherlands, Waterloo, Saxony, Berlin |
| Berlin | Hanover, Saxony, Bohemia |
| Rhineland | Belgium, Lyon, Saxony, Bavaria |
| Saxony | Hanover, Berlin, Rhineland, Bavaria, Bohemia, Dresden |
| Dresden | Saxony, Bohemia |
| Bavaria | Rhineland, Saxony, Vienna, Tyrol |
| Vienna | Bavaria, Bohemia, Tyrol, Milan |
| Bohemia | Berlin, Saxony, Dresden, Vienna |
| Tyrol | Bavaria, Vienna, Milan |

**Key design choices:**
- **Waterloo no longer adjacent to Paris.** Must go through Belgium. Breaks deathball — Wellington can't threaten Paris directly.
- **Rhineland connects to Lyon.** French southern territory connects to the German front via Rhineland, giving France interior lines.
- **Saxony is the crossroads.** Adjacent to Hanover, Berlin, Rhineland, Bavaria, Bohemia, Dresden. Whoever controls Saxony controls central Europe. This is WHY Saxony is the diplomatic prize.
- **Milan connects to Vienna.** Italy is the backdoor to Austria. Historical route of Napoleon's 1797 and 1805 campaigns.
- **Tyrol is the mountain wall.** Mountains terrain makes it a natural barrier between Bavaria and Italy. Difficult to attack through, easy to defend.
- **Britain has no capital on map.** Netherlands, Waterloo, Hanover are continental footholds. Losing them hurts British economy but doesn't end the war.

### 1c. Starting Forces

| Nation | Marshal | Location | Strength | Personality | Type | Notes |
|--------|---------|----------|----------|-------------|------|-------|
| **France** | Ney | Belgium | 72,000 | Aggressive | Cavalry | Unchanged |
| **France** | Davout | Paris | 48,000 | Cautious | Infantry | Unchanged |
| **France** | Grouchy | Lyon | 28,000 | Literal | Infantry | MOVED from Waterloo → Lyon (deathball fix) |
| **France** | Drouot | Paris | 25,000 | Cautious | Artillery | Unchanged |
| **Britain** | Wellington | Waterloo | 52,000 | Cautious | Infantry | Unchanged |
| **Britain** | Uxbridge | Hanover | 24,000 | Aggressive | Cavalry | MOVED from Netherlands → Hanover |
| **Prussia** | Blücher | Berlin | 40,000 | Aggressive | Infantry | MOVED from Rhine → Berlin |
| **Prussia** | Gneisenau | Rhineland | 32,000 | Cautious | Infantry | NEW marshal, Prussian second-in-command |
| **Austria** | Archduke Charles | Vienna | 35,000 | Cautious | Infantry | NEW — Austria's best general |
| **Austria** | Schwarzenberg | Bohemia | 25,000 | Cautious | Infantry | NEW — cautious coalition commander |
| **Saxony** | Reynier | Dresden | 10,000 | Literal | Infantry | NEW — historical Saxon commander |

**Force balance:**
- France: 173,000 total (4 marshals, 8 regions)
- Coalition at war: Britain 76,000 + Prussia 72,000 = 148,000 (4 marshals, 5 regions)
- Neutral: Austria 60,000 (2 marshals, 4 regions), Saxony 10,000 (1 marshal, 2 regions)
- **If Austria joins coalition:** 208,000 vs France 173,000 (+ potential Saxony 10,000)

This creates the diplomatic tension: France is stronger than Britain+Prussia alone, but if Austria joins, France is outnumbered. The player MUST either prevent Austrian entry or flip Prussia.

### 1d. Starting Economy

| Nation | Starting Gold | Income (approx) | Upkeep (5g/1000) | Net/Turn | Notes |
|--------|--------------|------------------|-------------------|----------|-------|
| France | 800 | 1,100 | 865 | +235 | 8 regions, strong economy |
| Britain | 1,500 | 200 + 300 naval | 380 | +120 | 3 regions + naval income |
| Prussia | 800 | 350 | 360 | -10 | 2 regions, tight economy |
| Austria | 600 | 650 | 300 | +350 | 4 regions, not at war (no war costs) |
| Saxony | 200 | 250 | 50 | +200 | 2 regions, tiny army |

**British Naval Income:** Britain receives +300 gold/turn from naval supremacy (trade dominance, colonial revenue). This is an abstracted effect — no ship-to-ship combat. Can be reduced via Continental System diplomatic action (see §5d). This makes Britain economically resilient despite small continental holdings.

**Manpower Pools (new nations):**

```python
DEFAULT_MANPOWER_POOLS = {
    "France":  {"infantry": 80000, "cavalry": 15000, "artillery": 10000},
    "Britain": {"infantry": 50000, "cavalry": 8000,  "artillery": 5000},
    "Prussia": {"infantry": 60000, "cavalry": 10000, "artillery": 5000},
    "Austria": {"infantry": 40000, "cavalry": 5000,  "artillery": 3000},
    "Saxony":  {"infantry": 15000, "cavalry": 2000,  "artillery": 1000},
}
```

### 1e. Starting Diplomatic States

| Pair | Starting State | Notes |
|------|---------------|-------|
| France ↔ Britain | WAR | Active war from game start |
| France ↔ Prussia | WAR | Active war from game start |
| France ↔ Austria | PEACE | Not at war, but relation -30 signals hostility. Austria watching. |
| France ↔ Saxony | PEACE (French-leaning) | Friendly terms, open to alliance/vassalage |
| Britain ↔ Prussia | ALLIANCE | Coalition partners |
| Britain ↔ Austria | DEFENSIVE_ALLIANCE | Will join if Austria is attacked |
| Britain ↔ Saxony | PEACE | Neutral |
| Prussia ↔ Austria | DEFENSIVE_ALLIANCE | Coalition partners |
| Prussia ↔ Saxony | PEACE | Neighbors, Prussia covets Saxony |
| Austria ↔ Saxony | PEACE | Neutral |

**Starting Nation Relations (§6 scale, -100 to +100):**

| Pair | Relation | Why |
|------|----------|-----|
| France ↔ Britain | -80 | Ancient rivals, active war |
| France ↔ Prussia | -60 | At war, but historically flippable |
| France ↔ Austria | -30 | Hostile but not committed |
| France ↔ Saxony | +40 | French-leaning, historical Confederation of the Rhine |
| Britain ↔ Prussia | +60 | Coalition allies |
| Britain ↔ Austria | +40 | Anti-French alignment |
| Britain ↔ Saxony | 0 | Indifferent |
| Prussia ↔ Austria | +30 | Coalition partners, some tension |
| Prussia ↔ Saxony | -10 | Prussia wants to absorb Saxony |
| Austria ↔ Saxony | +10 | Mild positive, both fear Prussia slightly |

---

## §2. Diplomatic Representatives

Each nation has a diplomatic representative. The player commands Talleyrand. Enemy diplomats shape AI proposals and responses.

### 2a. Diplomatic Personality Types

| Type | Effect | Archetype |
|------|--------|-----------|
| **Schemer** | Best diplomatic stats. May "diplomatically defy" at low authority/trust. Substitutes what HE thinks is best — not betrayal, course correction. | Talleyrand |
| **Loyalist** | Moderate stats, never sabotages, always reliable. | Caulaincourt |
| **Hawk** | Penalties to peace proposals, bonuses to demands/ultimatums. Objects to generous terms. | Hardenberg |
| **Dove** | Bonuses to peace/alliance, penalties to harsh demands. Objects to conquest-driven proposals. | Metternich |

### 2b. Diplomatic Representatives

| Nation | Representative | Personality | Skill | Biography |
|--------|---------------|-------------|-------|-----------|
| **France** | **Talleyrand** | Schemer | 10 | "The devil's diplomat. Serves France — or rather, serves what he believes France should be. Not always the same thing." |
| **Britain** | **Castlereagh** | Hawk | 7 | "Cold, calculating, implacable. Views any French advantage as a threat to the balance of power." |
| **Prussia** | **Hardenberg** | Hawk | 6 | "Prussian pride dressed in diplomatic language. Demands respect, offers little." |
| **Austria** | **Metternich** | Dove | 8 | "The spider of European diplomacy. Prefers the web to the sword. Will join whoever seems likely to win." |
| **Saxony** | **Count Einsiedel** | Loyalist | 4 | "A minor court's minor diplomat. Follows orders, keeps his head down, hopes Saxony survives." |

**Diplomat Skill affects:**
- Acceptance formula bonus (§6)
- DP efficiency (§4)
- Sabotage detection difficulty (§3b)
- Proposal quality (how much the other side trusts your word)

### 2c. Talleyrand — The Player's Diplomat

Talleyrand is the diplomatic equivalent of Berthier + a marshal combined. He:

**Executes:** Proposals, negotiations, treaty formalization, counter-offers
**Reports:** Diplomatic situation via Diplomatic Dispatch (see §10), nation attitudes, coalition risk warnings
**Objects:** When proposals are "beneath France" (too generous) or when threat level is spiking (too aggressive)
**Sabotages:** At low authority/trust, may alter deal terms (see §3)

**Commands via text (same interaction pattern as marshals):**
```
"Talleyrand, propose peace with Prussia"
"Talleyrand, offer Austria an alliance"
"Talleyrand, demand Saxony's vassalage"
"Talleyrand, offer Prussia: peace, they keep Rhineland, 200 gold/turn"
"Talleyrand, improve relations with Austria"
"Talleyrand, invest in Saxony"
"Talleyrand, gather intel on Prussia"
"Talleyrand, downgrade alliance with Austria"
```

**Mock mode parsing keywords:**
- `propose/offer/suggest` → diplomatic proposal (see §2d for flow)
- `demand/insist/require` → harsh proposal (Hawk penalty, Dove bonus on receiving end)
- `peace/armistice/ceasefire` → peace proposals
- `alliance/pact/defense` → alliance proposals
- `vassal/submit/subjugate` → vassalage proposals
- `open borders/access/passage` → border treaties
- `cancel/break/renounce` → treaty cancellation
- `improve relations/court/charm` → IMPROVE_RELATIONS mission (§2e)
- `invest/fund/support` + vassal name → INVEST_IN_VASSAL one-shot (§8b)
- `gather intel/spy/investigate` → GATHER_INTEL mission (§2e)
- `undermine/weaken/sabotage alliance` → UNDERMINE_ALLIANCE mission (§2e)
- `downgrade/reduce/withdraw` → diplomatic state downgrade (§5b.1)
- Target nation parsed from command: "with Prussia", "to Austria", etc.

### 2d. Proposal Flow — "Talleyrand Goes, Comes Back"

Diplomatic proposals are NOT instant. You tell Talleyrand what you want. He travels, negotiates, and returns next turn with a package. This creates tension, forces planning, and is where defiance happens (he alters the proposal during the travel turn).

**The flow:**

```
TURN 1: Player issues proposal command
  "Talleyrand, propose peace with Prussia: they keep Berlin, open borders, 200 gold/turn"
  → DP spent immediately (2 DP for peace proposal)
  → Talleyrand objection check fires (§3d). If player insists, defiance roll (§3a).
  → Talleyrand "departs" — proposal is IN TRANSIT for 1 turn
  → Morning Dispatch next turn: "Talleyrand has departed for the Prussian court."
  → Sabotage (if defiance triggered) is applied NOW, during transit

TURN 2: Talleyrand returns with response (popup at start of turn)
  → Acceptance formula (§6) evaluated on what Talleyrand ACTUALLY delivered
  → Three possible responses:

  ACCEPT (score >= 50):
    "Sire, Hardenberg has accepted our terms. The treaty is ready for ratification."
    → [Ratify]  — Treaty takes effect immediately
    → [Reject]  — Player changes mind (relation -10 for wasting their time)

  COUNTER-OFFER (score 30-49):
    "Sire, Hardenberg finds our terms... insufficient. He proposes modifications."
    → Shows: original terms vs counter-terms (what they changed)
    → [Accept Counter]  — Ratify their version (free, 0 DP)
    → [Reject]          — Walk away (relation -5)
    → [Renegotiate]     — Costs 1 DP, Talleyrand departs again (another turn)

  REJECT (score < 30):
    "Sire, Hardenberg has refused our proposal outright. He offers no alternative."
    → [Acknowledge]  — Relation -5
    → No renegotiate option — they won't even talk. Improve relations first.
```

**Key implications:**
- **Proposals take 1 turn.** You can't propose peace and get it same-turn. Plan ahead.
- **Renegotiation costs DP AND time.** Each round of renegotiation is 1 DP + 1 turn. Deep negotiations are expensive.
- **Defiance happens during transit.** When Talleyrand returns, the popup shows what was ACTUALLY proposed. If sabotaged, the terms differ from what you ordered — but the player only sees the result (unless discovered via §3c).
- **Counter-offers are FREE to accept.** You spent DP on the initial proposal. Accepting their counter doesn't cost more DP — only renegotiating does.
- **One proposal in transit at a time.** Talleyrand can't negotiate with Prussia AND Austria simultaneously. He can run a diplomatic MISSION (§2e) while a proposal is in transit, but not a second proposal. This forces diplomatic prioritization.
- **Player proposal cooldown (per-nation):** After a proposal is REJECTED, the player cannot propose to the same nation for **3 turns**. After the same proposal TYPE is rejected, cooldown is **5 turns** for that type. Tracked in `player_proposal_cooldowns`. Prevents proposal spam (same anti-spam rules as AI proposals in §9a, now symmetrical). Counter-offers and renegotiations don't trigger the cooldown (only outright rejection does).

**Talleyrand availability:**
```
Talleyrand states:
  IDLE          — Available for proposals or missions
  IN_TRANSIT    — Carrying a proposal, returns next turn
  ON_MISSION    — Running a diplomatic mission (§2e), can be reassigned

During IN_TRANSIT:
  - Cannot send new proposals (Talleyrand is physically at the foreign court)
  - CAN continue an existing mission (mission runs on auto)
  - CAN respond to incoming AI proposals (Berthier relays to Talleyrand)

During ON_MISSION:
  - CAN send proposals (mission pauses for 1 turn while Talleyrand travels)
  - Mission resumes automatically when Talleyrand returns
```

### 2e. Diplomatic Missions (Strategic Orders for Diplomacy)

Same pattern as military strategic orders (MOVE_TO, PURSUE, HOLD, SUPPORT). Talleyrand gets assigned an ongoing mission that consumes DP per turn. Like a marshal on HOLD or PURSUE, the mission runs automatically each turn until cancelled or reassigned.

**Commands:**
```
"Talleyrand, improve relations with Austria"    → IMPROVE_RELATIONS mission
"Talleyrand, court Austria"                     → COURT_NATION mission
"Talleyrand, gather intel on Prussia"           → GATHER_INTEL mission
"Talleyrand, undermine the British-Prussian alliance" → UNDERMINE_ALLIANCE mission
"Talleyrand, reassure Austria"                  → REASSURE_ALLY mission
"Talleyrand, cancel mission" / "Talleyrand, halt" → Cancel active mission
```

| Mission | DP/Turn | Target | Effect | Duration | Notes |
|---------|---------|--------|--------|----------|-------|
| **IMPROVE_RELATIONS** | 1 | Any nation | +5 relation/turn | Ongoing | Bread and butter. Slow but steady. |
| **COURT_NATION** | 2 | Neutral/hostile | +8 relation/turn, 20% chance/turn to weaken their strongest alliance by -3 | Ongoing | Expensive. This is how you flip Austria. |
| **UNDERMINE_ALLIANCE** | 2 | Nation pair | Target pair loses -3 relation/turn | Ongoing | Weaken Britain-Prussia bond. Requires PARTIAL+ intel on target pair. |
| **GATHER_INTEL** | 1 | Any nation | Reveals relations, army sizes, treaty details, diplomatic intentions | 3 turns (auto-completes) | One-shot. Intel delivered via dispatch on completion. |
| **REASSURE_ALLY** | 1 | Your ally/partner | Prevents alliance decay, +3 relation/turn | Ongoing | Maintain what you have. Cheaper than rebuilding. |
| **CONTINENTAL_SYSTEM** | 2 | Britain (special) | See §5d | Ongoing | Reframed as a diplomatic mission. |

**Removed: IMPROVE_LOYALTY mission.** Vassal loyalty is now maintained passively (garrison, autonomy, gold investment) plus the one-shot "Invest in vassal" action (§4b, §8b). This frees Talleyrand for actual diplomacy. See §8b for the full passive maintenance model.

**Mission rules:**
- **One mission at a time.** Choosing IMPROVE_RELATIONS with Austria cancels any active mission. Talleyrand's attention is finite.
- **DP deducted at start of turn.** If you can't afford the mission, it auto-pauses (Morning Dispatch: "Talleyrand's diplomatic efforts have been curtailed — insufficient resources").
- **Proposals interrupt missions temporarily.** If you send a proposal while Talleyrand is on a mission, the mission pauses for the transit turn. It resumes when he returns.
- **Cancellation is free** (0 DP, same as strategic order cancel).
- **Mission effects are cumulative per turn.** IMPROVE_RELATIONS running for 3 turns = +15 total relation.
- **Enemy diplomats run missions too (Building Blocks).** AI nations assign their diplomats to missions using the same costs and effects. AI mission priorities follow §9 decision tree.

**Talleyrand skill bonus on missions:**
```
Skill 10 (Talleyrand): mission effects +50% (IMPROVE_RELATIONS = +7.5/turn, round to +8)
Skill 7-9: mission effects as listed
Skill 4-6: mission effects -25% (rounded down)
```

### 2f. Command Parser Routing

Diplomatic commands use a **name-gated prefix** to distinguish from marshal commands. The parser checks the addressee name FIRST:

```
Input: "Talleyrand, propose peace with Prussia"

Step 1 — Name resolution (parser.py):
  - Extract addressee from command prefix (before first comma)
  - Check against marshal names (fuzzy match, existing logic)
  - Check against diplomat names (Talleyrand only for player)
  - If diplomat match → route to diplomatic command parser
  - If marshal match → route to military command parser (existing)
  - If ambiguous (no comma, no clear addressee) → try military parser first,
    fall back to diplomatic keywords ("propose", "treaty", "alliance")

Step 2 — Diplomatic keyword parsing (new section in llm_client.py mock parser):
  - Keywords already defined in §2c: propose/offer/demand/peace/alliance/etc.
  - Returns: {"action": "diplomatic_proposal", "diplomat": "Talleyrand",
              "target_nation": "Prussia", "proposal_type": "peace",
              "clauses": [...], "tone": "propose" | "demand"}

Step 3 — Execution routing (executor.py):
  - If action == "diplomatic_*" → route to _execute_diplomatic() family
  - Diplomatic actions check DP (not AP)
  - Diplomatic actions check Talleyrand availability (not marshal availability)

Step 4 — LLM integration (prompt_builder.py):
  - Diplomatic commands use diplomat-aware prompts
  - Few-shot examples include Talleyrand-addressed commands
  - VALID_ACTIONS updated with diplomatic action types
```

**Mock parser keywords for diplomatic routing** (added to `llm_client.py` ~line 416):
```python
# Diplomatic command detection (check BEFORE marshal commands)
if addressee_is_diplomat:
    if any(kw in text for kw in ["propose", "offer", "suggest"]):
        return {"action": "diplomatic_proposal", ...}
    if any(kw in text for kw in ["demand", "insist", "require"]):
        return {"action": "diplomatic_demand", ...}
    if any(kw in text for kw in ["improve relations", "court", "charm"]):
        return {"action": "diplomatic_mission", "mission_type": "IMPROVE_RELATIONS", ...}
    # ... (full keyword list in §2c)
```

---

## §3. Talleyrand's Diplomatic Defiance

Same pattern as combat defiance (V2b). Talleyrand doesn't betray France — he does what he believes is advantageous. The player orders one thing; Talleyrand delivers something slightly different.

### 3a. Defiance Probability Curve

```
defiance_chance = base + authority_mod + trust_mod + variance

Base:          0.05 (5% — rare by default)

Authority modifier:
  authority >= 80:  -0.05 (Strong Emperor → Talleyrand obeys)
  authority >= 60:  +0.00 (Neutral)
  authority >= 40:  +0.05 (Weakening → Talleyrand "helps")
  authority < 40:   +0.15 (Weak Emperor → Talleyrand takes charge)

Trust modifier (Talleyrand's personal trust):
  trust >= 80:  -0.05 (High loyalty)
  trust >= 50:  +0.00 (Neutral)
  trust >= 30:  +0.05 (Growing independence)
  trust < 30:   +0.10 (Acting on own judgment)

Variance: random.uniform(-0.05, 0.05)

Hard cap: 0.30 (30% maximum — even at lowest authority+trust)
Floor:    0.02 (Schemer minimum — Talleyrand is NEVER fully tamed)
```

**Schemer minimum (E4 fix):** Unlike combat marshals (who CAN reach 0% defiance), Talleyrand always has a 2% baseline. This is the Schemer personality expressing itself — he's the greatest diplomat of his era and always reserves the right to "adjust" your proposals. A player who maxes authority AND trust still faces a 1-in-50 chance of sabotage. This prevents the exploit of trivially neutralizing defiance through high stats.

**Example scenarios:**
- Authority 85, Trust 75: 0.05 - 0.05 - 0.05 = -0.05 → Floor 0.02 (2% — Schemer minimum)
- Authority 60, Trust 55 (game start): 0.05 + 0.00 + 0.00 = 0.05 → 5% baseline (Talleyrand at trust 55 is right on the edge — one bad turn drops him to the +0.05 bracket)
- Authority 50, Trust 45: 0.05 + 0.00 + 0.05 = 0.10 → 10% (trust dropped below 50 — Schemer activates)
- Authority 35, Trust 25: 0.05 + 0.15 + 0.10 = 0.30 → Maximum (30%)

### 3b. What Talleyrand Changes

When defiance triggers, Talleyrand modifies the proposal — he doesn't refuse it entirely. The modification depends on what the player ordered:

| Player Orders | Talleyrand Delivers | Rationale |
|---------------|---------------------|-----------|
| Demand 3 regions | Demands 2 regions | "Demanding Berlin ensures they never forgive us" |
| Reject an offer | Stalls instead of rejecting | "I left the door open, Sire" |
| Harsh vassal terms | Generous vassal terms | "A willing vassal is worth ten conquered provinces" |
| Demand AP/turn tribute | Reduces to gold/turn | "AP demands breed rebellion faster than anything" |
| Unit trade (1000 cavalry) | Offers 2000 cavalry | "I gave them 2,000 instead of 1,000 — they were much more amenable" |
| Gold-for-manpower deal | Overpays slightly | "A generous exchange ensures continued cooperation" |
| War declaration on neutral | Sends ultimatum instead | "Give them a chance to submit — the optics matter" |
| Generous peace offer | Adds face-saving clause | "We must not appear desperate, Sire" |

**Mechanical implementation:**
```python
def apply_diplomatic_defiance(original_proposal, talleyrand, world):
    """Modify proposal based on Talleyrand's judgment."""
    modified = original_proposal.copy()

    if original_proposal.harshness > 0.7:  # Too aggressive
        # Soften: reduce territory demands, lower tribute
        modified.territory_demands = max(0, modified.territory_demands - 1)
        modified.gold_per_turn = int(modified.gold_per_turn * 0.6)
        modified.defiance_type = "softened"
    elif original_proposal.harshness < 0.3:  # Too generous
        # Harden: add face-saving clause, increase demands slightly
        modified.gold_per_turn = int(modified.gold_per_turn * 1.3)
        modified.defiance_type = "hardened"
    else:
        # Stall: delay delivery by 1 turn instead of sending immediately
        modified.delivery_delay = 1
        modified.defiance_type = "stalled"

    return modified
```

### 3c. Discovery

Sabotage is discoverable. Two detection paths:

1. **Morning Dispatch (automatic):** If Talleyrand defied, there's a 40% chance per turn that Berthier's intelligence network discovers the discrepancy. Chance increases by +10% per turn the sabotage remains hidden (turns into eventual certainty).

2. **Nation response mismatch:** If the target nation's response doesn't match what you'd expect from your proposal, the player may notice ("I demanded 3 regions, why are they discussing 2?"). The response text includes hints.

**When discovered:**
- Campaign log entry: "Talleyrand altered your proposal to Prussia. He demanded 2 regions instead of 3."
- Notification (HIGH): "Diplomatic discrepancy discovered"
- Player can: confront Talleyrand (trust -10, authority +5, defiance cooldown 5 turns) or overlook it (trust +3, Talleyrand gains confidence → defiance chance doesn't change)

### 3d. Talleyrand's Objections (Pre-Proposal)

Before defiance rolls, Talleyrand can object to proposals — same pattern as marshal objections:

**Objects to harsh terms when threat is high:**
> "Sire, demanding Vienna will unite all of Europe against us. The courts are watching."

**Objects to generous terms when France is winning:**
> "Sire, offering open borders to a nation we're defeating rewards their failure."

**Objects to war declarations on neutrals:**
> "Sire, Austria has given us no cause for war. Attacking them is how coalitions are born."

Objection uses the V2a pattern (MILD/MODERATE/STRONG concern levels). Player can insist → defiance chance applies. Talleyrand is Schemer personality — his objection threshold is shaped by strategic calculation, not honor or fear.

---

## §4. Diplomatic Points (DP)

Diplomacy has its own action economy, separate from military AP. The player must choose how to spend limited DP each turn — court Austria vs. negotiate with Prussia vs. maintain Saxony loyalty.

### 4a. DP Generation

```
Base DP per turn: 2

Talleyrand skill bonus:
  Skill 10 (Talleyrand): +1 bonus DP
  Skill 7-9:             +0
  Skill 4-6:             -0 (but actions cost more — see 4b)

Authority modifier:
  Authority >= 60: +1 bonus DP (Emperor's word carries weight)
  Authority < 30:  -1 DP (nobody listens to a weak Emperor)

Capital controlled:
  Paris controlled: +0 (baseline)
  Paris lost:       -1 DP (diplomatic credibility shattered)

Maximum DP per turn: 5
Minimum DP per turn: 1 (hard floor — always at least 1 diplomatic action)
```

**France at game start: 2 base + 1 (Talleyrand skill 10) + 1 (authority ~60) = 4 DP/turn.**

The authority threshold was lowered from 80 to 60 so France starts with meaningful diplomatic capacity (4 DP). Dropping below authority 60 costs 1 DP — creating real stakes for authority management. Maximum increased to 5 to leave room for authority 80+ bonus future expansion if needed.

DP does NOT accumulate between turns. Use it or lose it. This forces priority decisions every turn — "what's my diplomatic priority THIS turn?" Same design philosophy as AP. You can't hoard command capacity.

### 4b. DP Costs

| Action | DP Cost | Notes |
|--------|---------|-------|
| **Propose peace** | 2 | Major diplomatic action |
| **Propose alliance** | 2 | Major diplomatic action |
| **Propose non-aggression** | 1 | Minor pact |
| **Propose open borders** | 1 | Minor pact |
| **Propose downgrade** | 1 | Step down one diplomatic state (§5b.1) |
| **Demand vassalage** | 3 | Major commitment (exceeds base — requires Authority bonus DP or multi-turn effort) |
| **Offer tribute/trade deal** | 1 | Gold, manpower, or AP clause |
| **Respond to AI proposal** | 0 | Free — reacting to diplomacy doesn't cost DP |
| **Cancel/break treaty** | 1 | Costs diplomatic credibility + relation hit |
| **Invest in vassal** | 1 | 200 gold + 1 DP → +10 vassal loyalty. One-shot. Max once per vassal per 3 turns. (§8b) |
| **Start/cancel mission** | 0 | Missions cost DP/turn (§2e), but starting/cancelling is free |

**Removed from this table (v1.2 dedup):** "Improve relations" was listed here as a 1 DP one-shot AND in §2e as an ongoing mission. The one-shot version is removed — use the IMPROVE_RELATIONS mission (§2e) for all relation improvement. This is cleaner: missions are the ongoing tool, proposals are the transactional tool.

**Diplomat skill efficiency:**
- Skill 7+: costs are as listed
- Skill 4-6: all costs +1 (incompetent diplomat wastes effort)
- Skill < 4: all costs +2

**Enemy diplomats use the same costs** (Building Blocks). AI DP pools use the SAME generation formula:

| Nation | Base | Skill Bonus | Authority Bonus | Typical DP | Notes |
|--------|------|-------------|-----------------|-----------|-------|
| France | 2 | +1 (Talleyrand 10) | +1 (auth ~60) | **4** | Player nation |
| Britain | 2 | +1 (Castlereagh 7+) | +0 | **3** | No capital on map (no capital penalty) |
| Prussia | 2 | +0 (Hardenberg 6) | +0 | **2** | Tight economy, tight diplomacy |
| Austria | 2 | +1 (Metternich 8) | +0 | **3** | Metternich compensates for bureaucracy |
| Saxony | 2 | +0 (Einsiedel 4) | +0 | **2** | Minor power, -1 skill penalty → effective 1 DP (costs +1) |

AI DP generation uses `_calculate_dp(diplomat, nation_authority)` — same function as player. No hardcoded pools. AI nations that gain/lose authority (from losing wars, breaking treaties) see DP change dynamically.

---

## §5. Diplomatic States & Transitions

### 5a. State Definitions

States between each nation pair, from most hostile to most friendly. **Hostility within a state is expressed by relation value, not by a separate state** — there is no "HOSTILE_NEUTRAL." Austria at PEACE with relation -30 behaves differently from Saxony at PEACE with relation +40, but both are mechanically at PEACE.

| State | Movement | Combat | Economy | Other |
|-------|----------|--------|---------|-------|
| **WAR** | Cannot enter enemy territory without attacking | Full combat | Pillage/plunder enabled | Default hostile state |
| **ARMISTICE** | Cannot enter enemy territory | No combat (ceasefire) | No trade | 3-turn minimum duration. Either side can end it (returns to WAR) |
| **PEACE** | Cannot enter each other's territory | No combat | Trade (+50 gold/turn bilateral) | Stable state, breaking requires war declaration |
| **OPEN_BORDERS** | Can move through each other's territory | No combat | Trade (+100 gold/turn bilateral) | No military access — can move THROUGH, not station troops |
| **NON_AGGRESSION** | Cannot enter each other's territory | No combat | Trade (+150 gold/turn bilateral) | Breaking pact = severe relation hit (-40) and threat spike |
| **DEFENSIVE_ALLIANCE** | Open borders + military coordination | Defend ally if attacked | Trade (+150 gold/turn bilateral) | If ally is attacked by third party, you enter WAR with the attacker |
| **ALLIANCE** | Full military coordination | Joint wars, coordinated attacks | Trade (+200 gold/turn bilateral) | Offensive + defensive. Can call ally into wars. |
| **VASSAL** | Lord controls vassal movement | Lord can order vassal troops | Tribute flows to lord | See §8 for full vassal mechanics |

### 5b. Transition Rules

Transitions must follow adjacency — no jumping from WAR to ALLIANCE:

```
UPGRADE PATH (left to right):
WAR → ARMISTICE → PEACE → OPEN_BORDERS → NON_AGGRESSION → DEFENSIVE_ALLIANCE → ALLIANCE
                                                                                    ↓
                                                                                 VASSAL

DOWNGRADE PATH (right to left — §5b.1):
ALLIANCE → DEFENSIVE_ALLIANCE → NON_AGGRESSION → OPEN_BORDERS → PEACE
  (Any downgrade costs 1 DP, relation hit varies by severity — see §5b.1)

Special transitions:
  Any state → WAR (war declaration, always possible, costs vary)
  VASSAL → WAR (rebellion — vassal breaks free)
  PEACE/above → VASSAL (negotiated vassalage — requires acceptance formula)
  WAR + conquest → VASSAL (military vassalage — hold capital + high war score)
```

#### 5b.1. Downgrade Transitions

Diplomatic states can degrade without jumping to WAR. Downgrades follow reverse adjacency (one step at a time):

| From → To | DP Cost | Relation Hit (target) | Relation Hit (all) | Threat | Notes |
|-----------|---------|----------------------|--------------------|----|-------|
| ALLIANCE → DEF_ALLIANCE | 1 | -15 | -5 | +5 | Withdrawing offensive commitment |
| DEF_ALLIANCE → NON_AGGRESSION | 1 | -20 | -5 | +5 | Breaking defensive promise |
| NON_AGGRESSION → OPEN_BORDERS | 1 | -15 | 0 | +3 | Moderate diplomatic cooling |
| OPEN_BORDERS → PEACE | 1 | -10 | 0 | 0 | Closing borders |
| PEACE → WAR | 1 | -30 | -15 | +20 | Full war declaration (§5c) |

**When do downgrades happen?**
- **Player-initiated:** "Talleyrand, downgrade alliance with Austria" — explicit command.
- **AI-initiated:** AI may downgrade relations when: (a) threat from target rises, (b) relation drops below state threshold (e.g., relation < +20 with an ally), (c) strategic realignment.
- **Treaty-break triggered:** Breaking specific treaty clauses may force a downgrade (e.g., violating open borders = OPEN_BORDERS → PEACE).
- **Automatic decay:** Relations that remain 30+ points below the state's relation threshold for 5 consecutive turns trigger automatic downgrade with reduced penalties (half relation hit, no threat). Morning Dispatch warns 2 turns before auto-downgrade: "Talleyrand warns: our alliance with Austria is deteriorating."

#### 5b.2. Armistice Cooldown

After an armistice expires or is broken, the same nation pair cannot enter another armistice for **5 turns** (prevents armistice-chaining exploit). Tracked per nation-pair in `armistice_cooldowns`. War must continue or peace must be negotiated.

**Transition costs (proposer):**

| From → To | DP Cost | Relation Requirement | Notes |
|-----------|---------|---------------------|-------|
| WAR → ARMISTICE | 1 | None (war exhaustion drives this) | 3-turn minimum |
| ARMISTICE → PEACE | 2 | Relation > -60 | May require treaty clauses |
| PEACE → OPEN_BORDERS | 1 | Relation > -20 | |
| OPEN_BORDERS → NON_AGGRESSION | 1 | Relation > 0 | |
| NON_AGGRESSION → DEF_ALLIANCE | 2 | Relation > +20 | |
| DEF_ALLIANCE → ALLIANCE | 2 | Relation > +40 | |
| Any → VASSAL (treaty) | 3 | Relation > +20 OR war score > 60 | |
| Any → WAR | 1 | None | Costs relation -30, threat +20 |

### 5c. War Declaration Rules

Declaring war on a neutral/friendly nation:
- Costs 1 DP
- Relation with target: -30 immediately
- Relation with ALL other nations: -15 ("aggressor" penalty)
- Threat level: +20 (tracked on WorldState, feeds into COALITION_SPEC coalition formation)
- Talleyrand will object (STRONG concern) if target is neutral and threat > 50
- If target has allies: all allies enter WAR with you (defensive alliance trigger)

**Casus Belli (reduces penalties):**
If the target broke a treaty, attacked your ally, or controls your core territory, the aggressor penalty is halved (-15 → -7 relation with others, threat +10 instead of +20). Casus belli is tracked automatically from treaty breaks and attacks.

### 5d. Continental System (Special Action)

A diplomatic action specifically targeting British economic power:

```
Continental System:
  Cost: 2 DP/turn to maintain (as diplomatic mission, §2e)
  Effect: Nations at PEACE or above with France close ports to Britain
  British naval income: reduced by 75g per nation participating
  Maximum reduction: 200g total (diminishing returns — smuggling, evasion)
  Participant relation with Britain: -20
  Participant relation with France: +10

  Requires: PEACE or above with target nation
  Risk: Participating nations may refuse (acceptance formula check each turn)
         Refusal costs France 5 relation with that nation
         Each participating nation checks: relation with France > +10
           AND relation with Britain < +30 (won't sacrifice good British ties)
```

The Continental System is historically the centerpiece of Napoleonic economic warfare. It creates diplomatic tension — France must maintain good relations with continental powers to enforce the blockade, while Britain tries to undermine it.

**E5 balance:** Per-nation reduction lowered from 100g to 75g, total capped at 200g (was uncapped). Even with all 3 continental nations participating (225g raw), cap limits to 200g — Britain retains 100g naval income (cannot be fully shut down). Historically accurate: the Continental System leaked constantly, and Britain's global trade couldn't be completely blocked by continental embargo.

---

## §6. Acceptance Formula

Deterministic formula that decides whether a diplomatic proposal succeeds. LLM explains, never decides.

### 6a. Core Formula

```
acceptance_score = base_disposition
                 + war_score_modifier
                 + relation_modifier
                 + threat_modifier
                 + deal_sweetener
                 + diplomat_skill_bonus
                 + personality_modifier

Threshold: acceptance_score >= 50 → ACCEPT
           acceptance_score 30-49 → COUNTER_OFFER (AI proposes modified terms)
           acceptance_score < 30  → REJECT
```

### 6b. Component Breakdown

**Base Disposition (by proposal type):**

| Proposal Type | Base | Notes |
|---------------|------|-------|
| Armistice (from losing side) | 40 | Loser wants peace — reasonable |
| Armistice (from winning side) | 20 | "Why stop when we're winning?" |
| Peace treaty | 30 | Standard starting point |
| Alliance proposal | 20 | Alliance is a big commitment |
| Vassalage demand | 10 | Nobody wants to be a vassal |
| Open borders | 35 | Low commitment, easy to accept |
| Non-aggression | 30 | Moderate commitment |

**War Score Modifier (per point of war score, -100 to +100):**
```
war_score * 0.3

Example: War score +50 (France winning) → +15 to acceptance of French proposals
         War score -30 (France losing) → -9 to acceptance of French proposals
```

**War score formula (§6e):** Defined inline below. Positive = nation_a winning.

**Military Supremacy Modifier (§6b.1):**
When war score >= 70 AND proposer holds target's capital, add a flat +25 to acceptance. This is the Tilsit scenario — after crushing military victory, even harsh terms become negotiable. Without this, the acceptance formula cannot produce dictated peace (vassalage base 10 + war score 30 + supremacy 25 + skill 8 = 73 → ACCEPT). Required for historically plausible outcomes like the Treaty of Tilsit (1807) or the Treaty of Pressburg (1805).

**Relation Modifier:**
```
relation / 2

Example: Relation +40 → +20 acceptance
         Relation -60 → -30 acceptance
```

**Threat Modifier (anti-France proposals only):**
```
When France proposes TO a hostile/neutral nation:
  threat_level * -0.3  (high threat makes nations MORE resistant to French diplomacy)

When non-France nations propose AGAINST France:
  threat_level * 0.2   (high threat makes anti-French proposals MORE attractive)
```

**Deal Sweetener (treaty clauses offered by proposer):**
```
Gold lump sum:       +1 per 200 gold offered
Gold per turn:       +3 per 100 gold/turn offered
Infantry manpower:   +2 per 5000 troops offered
Cavalry manpower:    +4 per 2500 cavalry offered (precious)
Artillery manpower:  +5 per 1500 artillery offered (rare)
Unit swap (offered): +3 per unit trade favorable to target
AP per turn:         +8 per AP/turn offered (most valuable)
Territory:           +5 per region ceded
Open borders:        +3
Protection:          +5 (guarantee of defense)
```

**Deal Demands (clauses demanded — NEGATIVE modifiers):**
```
Gold/turn demanded:   -2 per 100 gold/turn
Territory demanded:   -5 per region
AP/turn demanded:     -25 per AP/turn (WAR REPARATION — nearly impossible)
Unit swap (demanded): -2 per unit trade unfavorable to target
```

**Diplomat Skill Bonus:**
```
(proposer_skill - target_skill) * 2

Example: Talleyrand (10) vs Hardenberg (6) → +8
         Count Einsiedel (4) vs Metternich (8) → -8
```

**Personality Modifier:**

| Target Personality | Peace/Alliance Proposals | Harsh Demands/Ultimatums |
|-------------------|--------------------------|--------------------------|
| Dove (Metternich) | +10 | -10 |
| Hawk (Castlereagh, Hardenberg) | -5 | +5 |
| Loyalist (Einsiedel) | +0 | +0 |
| Schemer (Talleyrand, if receiving) | +5 | +5 (respects boldness) |

### 6c. Worked Example

**France proposes peace with Prussia. War score +20 (France slightly ahead). Relation -60. Threat 40. Talleyrand (10) proposes. Hardenberg (6) receives. France offers: Prussia keeps Berlin, open borders, 200 gold/turn.**

```
Base disposition (peace):        30
War score (+20 * 0.3):          +6
Relation (-60 / 2):            -30
Threat (40 * -0.3):            -12
Deal sweetener:
  Open borders:                 +3
  200 gold/turn:                +6
Diplomat skill (10-6)*2:        +8
Personality (Hawk, peace):      -5

Total:                          6 → REJECT
```

Prussia says no — too bitter, too much threat. France needs to sweeten the deal (territory concession? more gold?) or reduce threat level first.

**Same proposal but France also offers Saxony (territory):**
```
Previous total:                  6
+ Territory (Saxony):           +5
+ Extra sweetener (Saxony is
  what Prussia wants):          +10 (special bonus — see §6d)

Total:                          21 → still REJECT, but closer
```

Still rejected. France needs to either improve relations first, win more battles, or reduce threat. Diplomacy is hard.

### 6d. Special Acceptance Bonuses

Some proposals get bonuses based on what the target actually wants:

| Target | Wants | Bonus |
|--------|-------|-------|
| Prussia | Saxony | +10 if Saxony offered as part of deal |
| Austria | Bavaria | +8 if Bavaria offered |
| Britain | Continental System lifted | +15 if Continental System ended as clause |
| Saxony | Survival guarantee | +10 if protection promised |

These represent strategic interests that make certain deals inherently more attractive.

### 6e. War Score Formula

War score is calculated per war (nation pair at WAR). Range: -100 to +100. Positive means nation_a is winning.

```
war_score = territory_score + battle_score + decisive_battle_bonus + capital_score

Territory score (max ±40):
  +5 per enemy starting region currently held by you
  -5 per your starting region currently held by enemy
  Capped at ±40

Battle score (max ±30):
  +3 per battle won against this nation
  -3 per battle lost against this nation
  Capped at ±30

Decisive Battle Bonus (max ±20):
  When a battle results in:
    (a) Casualty ratio > 2:1 in winner's favor, AND
    (b) Total battle casualties > 10,000 (serious engagement)
  → Winner gets +10 war score bonus against the loser
  Cap: ±20 per war (max 2 decisive bonuses — prevents farming small battles)

  This is the Austerlitz/Jena mechanic. A single crushing victory dramatically
  shifts diplomatic leverage. Players who win big decisive battles gain a
  meaningful war score advantage that opens diplomatic options (peace proposals
  become more favorable, vassalage demands become possible).

  Decisive battles are tracked: {"turn": int, "winner_casualties": int,
  "loser_casualties": int, "location": str}. Displayed in Diplomatic Ledger
  Tab 3 as named events: "Decisive Victory at Berlin (Turn 8)".

Capital score (max ±30):
  +20 if you hold enemy capital
  -20 if enemy holds your capital
  +10 if enemy capital is contested (friendly marshal present, not yet captured)

Total capped at ±100.
```

**War score updates automatically** at the end of each turn based on current territory control and cumulative battle record. Territory score recalculates from scratch each turn (current holdings vs starting holdings). Battle score and decisive battle bonus are cumulative.

**War score decays toward 0** at -2/turn when no battles have occurred for 3+ turns. Represents fading military momentum — a victory from 10 turns ago carries less diplomatic weight than a fresh one. Decisive battle bonuses do NOT decay (they represent historical turning points).

**Implementation:** `_calculate_war_score(nation_a, nation_b, world)` in `diplomacy.py`. Called during `advance_turn()` for all active wars. Stored in `world.war_scores`.

---

## §7. Treaty System

### 7a. Treaty Clause Types

| Clause | Direction | Mechanical Effect | Notes |
|--------|-----------|-------------------|-------|
| **Gold lump sum** | Either | One-time gold transfer | Paid on treaty ratification |
| **Gold/turn** | Either | Recurring payment each turn | Checked at income phase |
| **Manpower (infantry)** | Either | One-time troop transfer to infantry pool | Specified amount |
| **Cavalry for artillery** | Either | Unit type swap — cavalry pool → artillery pool | Historically common (nations had different strengths) |
| **Artillery for cavalry** | Either | Reverse unit swap — artillery pool → cavalry pool | Austria had great cavalry, France great artillery |
| **Gold for manpower** | Either | Buy recruits from ally (gold → infantry/cav/art pool) | Rate: 200g per 5000 infantry, 300g per 2500 cavalry, 400g per 1500 artillery |
| **Manpower for gold** | Either | Sell recruits for treasury (pool → gold) | Reverse of above |
| **AP/turn** | Either | Lose AP each turn | WAR REPARATION TIER — see §7c |
| **Territory** | Either | Cede specific regions | Controller changes, stability drops to 50 |
| **Open borders** | Mutual | Movement through territory | Cannot station troops (must keep moving) |
| **Military access** | One-way | Their troops can enter your territory | Stronger than open borders |
| **Continental System** | France→target | Target closes ports to Britain | See §5d |
| **Protection guarantee** | One-way | Guarantor enters WAR if target is attacked | |

**Unit trade notes:** Cavalry-for-artillery swaps create interesting gameplay. Trade excess cavalry to Saxony for gold. Austria offers artillery in exchange for open borders — do you take the guns and let them march through? Talleyrand might sabotage a unit trade by offering MORE than authorized ("I gave them 2,000 cavalry instead of 1,000 — they were much more amenable").

### 7b. Treaty Bundling

Proposals are bundled — multiple clauses evaluated as a package:

```
"Talleyrand, offer Prussia peace: they keep Berlin, we get open borders, 200 gold/turn from them"

Parsed clauses:
  - Peace (WAR → ARMISTICE → PEACE path, fast-tracked)
  - Territory: France does NOT demand Berlin
  - Open borders: mutual
  - Gold tribute: Prussia pays 200/turn

Each clause contributes to deal_sweetener in acceptance formula.
```

**Harsh vs Generous:**
The formula uses a `harshness` score derived from clause balance:
```
harshness = (value_demanded - value_offered) / total_deal_value
  0.0 = perfectly balanced
  1.0 = all take, no give
  -1.0 = all give, no take (extremely generous)

Dove targets get +10 acceptance for harshness < 0.3 (generous)
Hawk targets get +5 acceptance for harshness > 0.6 (respects strength)
```

### 7c. AP Treaty Clauses — War Reparation Tier

AP is the most valuable resource in the game. Treaty AP reflects that:

**Demanding AP:** Requires overwhelming war score (> 80) OR conquest-vassalage. You only get AP tribute from a nation you've utterly defeated. Prussia isn't giving you command capacity unless you're standing in Berlin.

**Offering AP:** Almost never rational. Only makes sense as desperate war reparations to stop total conquest. "We'll cripple our command to buy survival."

**Cap:** 1 AP/turn max per treaty. Even in total defeat, more than 1 AP/turn would be game-breaking.

**Acceptance formula:** Massive negative modifier. AI nations treat AP demands as extreme:
```
AP demand penalty in acceptance formula: -25 per AP/turn demanded
(vs the +8 sweetener for OFFERING AP — asymmetric by design)

Only achievable with: max war score + territory held + other concessions
```

**Talleyrand reaction:** Talleyrand ALWAYS objects (STRONG concern) to AP demands unless war score > 80. "Sire, demanding their command capacity will ensure eternal enmity. No nation forgets such humiliation."

**AP as sabotage vector:** Talleyrand might offer more AP than authorized in a deal where France is PAYING AP ("I offered them 1 AP/turn instead of the gold you suggested — they were far more amenable"). This is his most dangerous sabotage — it directly cripples French command capacity.

This makes AP in treaties a late-game dominance move, not a routine negotiation tool. Historically accurate — Napoleon demanded troops and resources from vassals, but demanding sovereignty is how coalitions are born.

### 7d. Treaty Duration & Breaking

- Treaties have no expiration by default (permanent until broken or superseded)
- Armistice: minimum 3 turns, then either side can end
- Breaking a treaty:
  - Costs 1 DP
  - Relation with target: -30
  - Relation with all nations: -10 (treaty-breaker reputation)
  - Threat level: +15
  - Casus belli granted to victim
  - If breaking alliance/defensive alliance: more severe (-40 relation, +25 threat)

### 7e. Trade Income Integration

Trade income from diplomatic states is applied during the **income phase** of `advance_turn()`, alongside region income and upkeep:

```python
# In world_state.py advance_turn(), after region income calculation:
for pair_key, state in self.diplomatic_states.items():
    nation_a, nation_b = pair_key.split("|")
    trade_bonus = TRADE_INCOME.get(state, 0)  # §5a table values
    if trade_bonus > 0:
        self.nation_gold[nation_a] += trade_bonus
        self.nation_gold[nation_b] += trade_bonus

TRADE_INCOME = {
    "PEACE": 50, "OPEN_BORDERS": 100, "NON_AGGRESSION": 150,
    "DEFENSIVE_ALLIANCE": 150, "ALLIANCE": 200
}
# WAR and ARMISTICE: 0 (no trade during hostilities)
```

**Treaty clause gold/turn** is applied in the same income phase, immediately after trade income. Gold lump sums are applied on treaty ratification turn only.

**Display:** Trade income appears in the Strategic Ledger Economy tab as a separate line item: "Trade income: +150 (Prussia NON_AGGRESSION, Austria PEACE)".

---

## §8. Vassal System

### 8a. Two Paths to Vassalage

**Treaty Path (Diplomatic Vassalage):**
- Requires acceptance formula score >= 50 (difficult for vassalage — base 10, but Military Supremacy §6b.1 helps)
- Typically requires: high war score, generous tribute, protection guarantee
- Threat increase: +5 (minimal — willing vassalage)
- Starting vassal loyalty: 60 + (generosity_bonus * 10) (range: 60-90)

**Conquest Path (Military Vassalage):**
- Requires: hold target's capital + war score > 60 against them
- No acceptance check — you conquered them, they submit
- Threat increase: +25 (massive — conquest vassalage terrifies other nations)
- Starting vassal loyalty: 20 + (garrison_size / 5000) (range: 20-40)

### 8b. Vassal Loyalty — Passive Maintenance Model

**Design principle:** Vassal management is primarily passive — based on autonomy, garrison, gold investment, and military success. **Talleyrand is NOT required to manage vassals.** This allows historically accurate multi-vassal empires (Napoleon had 10+ client states). The diplomat's time is for making new deals, not babysitting existing ones.

Scale 0-100. Determines vassal cooperation and rebellion risk.

**Loyalty Generation (per turn):**
```
Autonomy-based drift (replaces flat -2):
  PUPPET (0):      -4/turn (total control breeds resentment — historically accurate)
  SATELLITE (1):   -2/turn (moderate control, moderate drift)
  AUTONOMOUS (2):  +1/turn (self-governance stabilizes — loyalty slowly rises)

Passive modifiers (no diplomat required):
  Garrison in vassal capital:                     +5 (primary maintenance tool)
  Garrison strength bonus:                        +1 per 5000 troops (max +3)
  Gold investment treaty (gold/turn TO vassal):   +1 per 100 gold/turn
  Shared enemy (both at war with same nation):    +2 (common cause)
  Lord winning wars:                              +1 per battle won this turn (max +3)
  Lord losing wars:                               -2 per battle lost this turn (max -6)
  Relation with lord:                             relation / 20 (can be negative)

Active modifier (costs DP, one-shot):
  "Invest in vassal" action (§4b):                +10 loyalty, costs 1 DP + 200 gold
    Max once per vassal per 3 turns (cooldown prevents spam)
    Does NOT require Talleyrand to be on-mission — he handles it and returns to IDLE
```

**PUPPET nerf (M8/E2):** PUPPET autonomy now drifts at -4/turn (doubled from -2). PUPPET extracts 100% income but requires constant garrison + investment to maintain. Without garrison: net -4/turn → rebellion in 15-25 turns from starting loyalty. With garrison (8000+): net +4/turn → stable but expensive. This prevents PUPPET from being the obvious optimal choice — SATELLITE and AUTONOMOUS are competitive alternatives that require less maintenance.

**Multi-vassal example:** Player has 3 vassals (Saxony SATELLITE, Bavaria AUTONOMOUS, Prussia PUPPET).
- Saxony: garrison (3k) → +5, shared enemy → +2, drift -2 = net +5/turn. Stable, cheap.
- Bavaria: AUTONOMOUS drift +1, no garrison needed. Self-maintaining. Costs 50% income.
- Prussia: PUPPET drift -4, garrison (8k) → +5+1 = net +2/turn. Requires large garrison to maintain.
- Talleyrand: FREE for missions. Can court Austria, undermine alliances, propose peace — not stuck babysitting.

### 8c. Vassal Obligations

| Level | Tribute | Military | Diplomacy | Maintenance Burden |
|-------|---------|----------|-----------|-------------------|
| PUPPET | 100% income | Lord commands all units | No independent diplomacy | High — -4 drift, needs garrison+investment |
| SATELLITE | 75% income | Must join lord's wars, lord suggests orders | Can negotiate with neutrals | Medium — -2 drift, garrison recommended |
| AUTONOMOUS | 50% income | Must join lord's wars, own army decisions | Free diplomacy except declaring war | Low — +1 drift, self-sustaining |

**Autonomy can be changed** by the lord (1 DP cost, takes effect next turn). Upgrading autonomy (PUPPET→SATELLITE) gives +10 loyalty bonus. Downgrading (SATELLITE→PUPPET) gives -15 loyalty penalty. Choose wisely.

### 8d. Vassal Rebellion

When loyalty hits 0:
- Vassal declares independence (returns to WAR with former lord)
- Vassal army turns hostile — all vassal marshals become enemies
- Threat level: -10 (other nations see France weakened)
- Relation with former vassal: -50
- **Cascade risk:** If lord has other vassals, they each get -10 loyalty ("if Saxony can break free...")

**Rebellion warning thresholds:**
- Loyalty < 40: Morning Dispatch warning ("Talleyrand reports unrest in Saxony")
- Loyalty < 20: Morning Dispatch urgent ("Saxony is on the verge of rebellion")
- Loyalty < 10: Notification (HIGH) — "Saxony: IMMINENT REBELLION"
- Loyalty = 0: Rebellion fires

### 8e. Enemy Courting Your Vassals

**APPROVED: Include in v1 (simplified form).** Enemy nations can spend 2 DP to "court" a player vassal, reducing loyalty by 10-20 per successful attempt (acceptance formula applies — vassal must want to be courted). This adds the full diplomatic loop: you must maintain vassal loyalty while enemies try to peel them away. Historically essential (every Napoleonic vassal eventually defected).

**Simplified v1:**
- AI spends 2 DP to court vassal
- If vassal loyalty < 50 AND courting nation relation with vassal > 0: loyalty -15
- If vassal loyalty < 50 AND courting nation relation with vassal < 0: loyalty -5 (even enemies of the vassal can destabilize)
- If vassal loyalty >= 50: courting attempt fails (loyalty too high — vassal is content)
- Player sees: Morning Dispatch "Talleyrand reports Prussian agents in Dresden"
- Counter: "Invest in vassal" (§4b) — 1 DP + 200 gold → +10 loyalty
- **Courting cooldown:** Same nation can only court same vassal every 3 turns

---

## §9. AI Diplomatic Behavior

### 9a. AI Proposals TO Player

AI nations actively make proposals. These use the same proposal flow as player proposals (§2d) — the AI's diplomat "travels" to you, and you receive the proposal at the start of your turn as a popup:

```
"Sire, a Prussian envoy has arrived. Hardenberg proposes:

  An armistice. Prussia will withdraw to Berlin.
  They request: safe passage through Saxony, 100 gold lump sum.

  Talleyrand's assessment: 'Prussia is desperate, Sire. We could
  demand far more. But an armistice now frees us to deal with Austria.'"

[Accept]       — Treaty ratified (free, 0 DP)
[Reject]       — Proposal rejected (relation -5)
[Renegotiate]  — Counter-proposal (costs 1 DP, Talleyrand departs next turn)
```

**Anti-spam protection:**
```
Rate limits:
  Max 1 AI proposal delivered to player per turn (queue if multiple)
  Per-nation cooldown: 3 turns after REJECTION before same nation can propose again
  Per-nation cooldown: 5 turns after same proposal TYPE rejected (no armistice spam)
  AI-AI proposals: max 2 per turn total across all AI nations

Priority when multiple queued:
  P1 > P2 > ... > P7 (highest urgency first)
  Same priority: most recent proposal wins

Queue visible in Diplomatic Ledger Tab 4:
  "Pending envoys: Austria (alliance proposal, arrives next turn)"
```

**Talleyrand's assessment:** Every incoming AI proposal includes a 1-2 sentence assessment from Talleyrand. This is flavor text shaped by his personality (Schemer — strategic calculation). In mock mode, keyed to proposal type + war score + relation. Talleyrand might recommend accepting a bad deal if it serves his long-term vision, or rejecting a good deal if it makes France look weak.

**AI proposal triggers (decision tree):**

| Condition | Proposal | Priority |
|-----------|----------|----------|
| Losing badly (war score < -40) | Armistice/peace | P1 (survival) |
| War stalemate (war score -10 to +10 for 5+ turns) | Armistice | P2 |
| Threat level > 60 AND not allied with France | Seek alliance with other anti-France nations | P3 |
| Relation > +30 AND at peace | Propose non-aggression/alliance upgrade | P4 |
| Economy struggling (gold < 200 and declining) | Trade deal / tribute offer | P5 |
| Vassal loyalty < 40 (if courting) | Court vassal | P6 |
| Opportunism: enemy distracted by another war | Propose terms that favor them | P7 |

### 9b. AI Response to Player Proposals

Uses the same acceptance formula (§6). The AI doesn't cheat — it evaluates proposals identically to how the player's proposals would be evaluated in reverse.

**Counter-offer logic:**
When acceptance_score is 30-49 (COUNTER_OFFER range), the AI generates a modified proposal:
- If too harsh: removes most expensive clause the player demanded
- If too generous: AI adds a clause they want
- Counter-offers are free for the AI (same as player — responding costs 0 DP)

### 9c. AI-AI Diplomacy

Nations negotiate with each other automatically. This makes the world feel alive.

**Per-turn AI diplomatic phase (runs after military phase):**
1. Each AI nation evaluates its DP budget
2. Priority 1: Survival diplomacy (seek peace if losing)
3. Priority 2: Alliance maintenance (strengthen existing allies)
4. Priority 3: Opportunistic proposals (court neutrals, destabilize enemies)

**Observable by player:**
- AI-AI treaties are announced in Morning Dispatch: "Talleyrand reports that Britain and Austria have signed a defensive alliance."
- Fog-filtered: player needs PARTIAL+ intel on at least one party to learn about the treaty
- Some AI-AI diplomacy is hidden (especially anti-France coordination) — creates discovery moments

**AI-AI acceptance:** Same formula, both sides. Metternich's high skill gives Austria an advantage in AI-AI negotiations. Castlereagh's Hawk personality makes British alliance proposals slightly harder to reject (aura of strength).

---

## §10. UI & Integration

### 10a. Diplomatic Top Bar

The existing top bar (Phase 6.5) gains diplomatic elements. Same pattern as the current turn counter, AP display, and notification bar.

**New top bar elements:**

```
┌──────────────────────────────────────────────────────────────────┐
│ Turn 5  │  AP: 3/4  │  DP: 2/3  │  ⚔ Talleyrand: Courting Austria │  [!] 1 envoy  │
└──────────────────────────────────────────────────────────────────┘
```

| Element | Display | Notes |
|---------|---------|-------|
| **DP Counter** | `DP: 2/3` | Diplomatic Points remaining / max. Same style as AP counter. |
| **Talleyrand Status** | `Talleyrand: [status]` | Shows current state: Idle, In Transit (Prussia), Courting Austria, Improving Loyalty (Saxony), etc. |
| **Envoy Indicator** | `[!] 1 envoy` | Number of pending AI proposals waiting for response. Clickable → opens first proposal popup. |
| **Threat Level** | Hidden unless > 30 | `⚠ Threat: 45` — appears in amber/red when coalition risk is meaningful. |

**Hotkey integration:**
- **D** — Opens Diplomatic Ledger (full screen, see §10b)
- Envoy indicator click or hotkey — Opens pending proposal popup
- Talleyrand status click — Opens Talleyrand Status tab in Diplomatic Ledger

**Top bar controller updates (`top_bar.gd`):**
- DP refreshed each turn (same pattern as AP refresh)
- Talleyrand status string updated on mission change, proposal send, return
- Envoy count updated when AI proposals arrive in diplomatic_queue
- Threat level visibility gated by threshold (> 30)

### 10b. Diplomatic Ledger (D key)

Same pattern as Strategic Ledger. CanvasLayer 50. Shows:

**Tab 1 — Nation Overview:**
```
┌─────────────────────────────────────────┐
│ DIPLOMATIC LEDGER          DP: 3/3      │
├─────────────────────────────────────────┤
│ [1] BRITAIN      WAR        Rel: -80    │
│     Castlereagh (Hawk)      Skill: 7    │
│     Continental: 3 regions   Army: 76k  │
│     Active treaties: None               │
│                                         │
│ [2] PRUSSIA      WAR        Rel: -60    │
│     Hardenberg (Hawk)       Skill: 6    │
│     Regions: 2              Army: 72k   │
│     Active treaties: Alliance (Britain) │
│                                         │
│ [3] AUSTRIA      PEACE      Rel: -30   │
│     Metternich (Dove)       Skill: 8    │
│     Regions: 4              Army: 60k   │
│     Treaties: Def.Alliance (Brit, Prus) │
│                                         │
│ [4] SAXONY    FRENCH_PEACE   Rel: +40   │
│     Einsiedel (Loyalist)    Skill: 4    │
│     Regions: 2              Army: 10k   │
│     Treaties: None                      │
│     Vassal eligible                     │
│                                         │
│ [D] Close    [Tab] Next Section         │
└─────────────────────────────────────────┘
```

**Tab 2 — Active Treaties:**
List of all treaties, clauses, duration, cancellation cost.

**Tab 3 — Threat & Coalition:**
Threat level bar, coalition risk assessment, contributing factors.

**Tab 4 — Talleyrand Status:**
```
┌─────────────────────────────────────────┐
│ TALLEYRAND STATUS                       │
├─────────────────────────────────────────┤
│ Trust: 55 (Wary)    Skill: 10           │
│ DP: 2/3 remaining                       │
│                                         │
│ Current Mission: COURT_NATION (Austria)  │
│   Duration: 3 turns    Effect: +8 rel/t │
│   Progress: -30 → -14 (+16 total)       │
│                                         │
│ Proposal In Transit: None               │
│ Pending Envoys: 1                       │
│   → Prussia: Armistice (arrives Turn 6) │
│                                         │
│ Sabotage Warning: None detected         │
│                                         │
│ [Cancel Mission]  [D] Close             │
└─────────────────────────────────────────┘
```

### 10c. Integration Points

| System | Connection |
|--------|-----------|
| **Authority** | Low authority → Talleyrand defiance chance increases. Authority > 80 → +1 DP. |
| **Trust** | Talleyrand has his own trust value (starts at 55 — Schemer felt from day one). Low trust → sabotage chance increases. |
| **Morning Dispatch** | Diplomatic events, Talleyrand warnings, AI proposals, treaty changes, sabotage discovery |
| **Campaign Log** | Treaty signed, alliance formed, vassal acquired, sabotage discovered, war declared |
| **Notifications** | AI proposals (HIGH), treaty expiring/broken (HIGH), sabotage discovered (HIGH), loyalty warning (MEDIUM) |
| **Threat/Coalition** | Feeds into COALITION_SPEC. Conquests, broken treaties, war declarations all raise threat. |
| **AP** | Treaty clause type — can be demanded or offered. AP/turn clauses directly modify `nation_actions`. |
| **Economy** | Gold/manpower as treaty clauses. Vassal tribute. Continental System. Trade income from peaceful relations. |
| **Fog of War** | See §11 |
| **Objection System** | Talleyrand uses same V2a objection pattern (MILD/MODERATE/STRONG) |
| **Defiance System** | Talleyrand diplomatic defiance uses same probability curve pattern as V2b |

---

## §11. Fog of War & Diplomatic Intel

### 11a. What the Player Knows

| Information | Visibility Requirement | Notes |
|-------------|----------------------|-------|
| Nation exists | Always | All 5 nations always known |
| Diplomatic state (your pairs) | Always | You always know your own treaty status |
| Diplomatic state (AI-AI pairs) | PARTIAL+ on either nation | Can discover AI-AI alliances via intel |
| Nation relation (your pairs) | Always (approximate) | Exact number shown. Talleyrand's assessment. |
| Nation relation (AI-AI pairs) | Hidden | Can only infer from behavior |
| Enemy army size | PARTIAL+ on region | Existing fog rules apply |
| Enemy economy | Hidden (rough estimate via Ledger) | Talleyrand can estimate based on territory |
| AI diplomatic intentions | Hidden | Proposals appear as popups when sent |
| Vassal loyalty | Always (if your vassal) | |
| Vassal courting attempts | 60% detection chance per attempt | Talleyrand's spy network |
| Sabotage by Talleyrand | 40% base, +10%/turn | See §3c |

### 11b. Diplomatic Intelligence

Talleyrand provides periodic intelligence reports (folded into Morning Dispatch):

```
"Talleyrand reports: Austria appears to be mobilizing. Metternich's tone
 has grown colder in recent dispatches. I estimate their disposition
 toward France at approximately -45. They may be courted away from
 their defensive alliance, but it will take considerable concessions."
```

Intelligence accuracy scales with Talleyrand's skill:
- Skill 10: relation estimate ±5, accurate assessment of intentions
- Skill 7: relation estimate ±10, vague assessment
- Skill 4: relation estimate ±20, often misleading

---

## §12. Edge Cases

**EC-A: Declare war on ally.** Player can declare war on an allied nation. Costs: break treaty penalties (§7d) + war declaration penalties (§5c) stacked. Relation with ALL nations: -40 (treaty-breaker + aggressor combined). Talleyrand objects (EXTREME concern). Historical: Napoleon did betray allies (Spain 1808).

**EC-B: Vassal at war with your enemy.** If you vassalize Saxony while at war with Prussia, does Saxony auto-enter war with Prussia? **Yes** — vassal inherits lord's wars (all autonomy levels). Saxony's marshal receives orders from player (PUPPET/SATELLITE) or acts autonomously targeting the lord's enemies (AUTONOMOUS).

**EC-C: AI proposes during your turn.** AI proposals are queued during the AI phase and delivered at start of NEXT player turn (Morning Dispatch). No mid-turn interruptions. Player responds when they have full context.

**EC-D: Multiple proposals to same nation.** Only one active proposal per nation pair. Must wait for response before sending another. Prevents spam.

**EC-E: Territory cession when marshal is present.** If France cedes a region where a French marshal is stationed: marshal is forcibly relocated to nearest friendly region. Dispatch warns: "Ney withdraws from Saxony per the treaty terms." No combat.

**EC-F: Vassal loyalty exactly 0 on the turn you send tribute.** Loyalty is checked at START of turn (during advance_turn). Tribute is applied during income phase. If loyalty hits 0 → rebellion fires before tribute can save it. Player should have maintained loyalty proactively.

**EC-G: War declaration cascades.** France declares war on Austria → Britain's defensive alliance triggers → Britain is already at war with France (no change). Prussia's defensive alliance triggers → Prussia is already at war with France (no change). Net effect: only France-Austria relation changes. But if France had peace with Britain first, the cascade WOULD pull Britain back into war.

**EC-H: Peace proposal while Talleyrand is sabotaging.** Talleyrand's sabotage is applied BEFORE the proposal reaches the target. If he softens terms, the target evaluates the softened version. The player sees the original terms in their command. Discrepancy only visible if discovered (§3c).

**EC-I: Break treaty then immediately re-propose.** Allowed, but the -30 relation hit from breaking makes the new proposal much harder to accept. Natural cooldown through math, not an artificial timer.

**EC-J: DP at 0, AI sends proposal.** Responding to AI proposals costs 0 DP. Player can always accept/reject. Counter-offer costs 1 DP and is blocked if DP = 0.

**EC-K: Vassal commands in mock mode.** Vassal marshals (PUPPET/SATELLITE) appear in player's command list. Commands parsed same as player marshals: "Reynier, attack Rhineland." If AUTONOMOUS, player cannot command them directly.

**EC-L: Austria joins war mid-game.** When Austria enters WAR with France (via coalition trigger, player aggression, or alliance cascade): Austrian marshals become active enemies. Their regions become hostile. Existing trade income from France-Austria peace is lost. Immediate recalculation of all diplomatic states.

**EC-M: Talleyrand killed/broken.** Talleyrand is not a military unit — he cannot be killed. He exists as a diplomatic entity, not a map unit. If Paris falls, Talleyrand's effectiveness is reduced (DP -1, skill effectively -2 until Paris recaptured).

**EC-N: Unit trade sabotage quantity.** Talleyrand offers MORE units than authorized (e.g., 2000 cavalry instead of 1000). The extra units are immediately deducted from France's manpower pool. If France doesn't have enough, the trade executes at France's actual pool amount (can't give what you don't have). Sabotage discovery reveals the discrepancy.

**EC-O: AP demand on nation with 2 AP base.** Demanding 1 AP/turn from Saxony (2 AP base) leaves them with 1 AP — barely functional. The acceptance formula's -25 penalty makes this nearly impossible without overwhelming war score. If accepted, Saxony's nation_actions is reduced by 1 during income phase each turn. Minimum AP after treaty: 1 (hard floor — a nation with 0 AP can't function).

**EC-P: Multiple unit type trades in one treaty.** Allowed — a treaty can include cavalry-for-artillery AND gold-for-manpower in the same bundle. Each clause is evaluated separately in the deal sweetener. The total package still gets one acceptance check.

**EC-Q: Proposal in transit when player sends another.** Blocked — "Talleyrand is currently en route to the Prussian court. He cannot negotiate with Austria until he returns." Player must wait for the return popup. One proposal in transit at a time.

**EC-R: Mission running + proposal sent.** Allowed — mission auto-pauses for the transit turn. Talleyrand resumes mission on return. Morning Dispatch: "Talleyrand's mission to court Austria pauses briefly while he delivers your proposal to Prussia."

**EC-S: DP insufficient for mission maintenance.** Mission auto-pauses (not cancelled). Morning Dispatch warns. Resumes next turn if DP available. If paused for 3+ consecutive turns, mission is auto-cancelled: "Talleyrand's diplomatic efforts in Austria have collapsed due to lack of resources."

**EC-T: Renegotiate after counter-offer.** Costs 1 DP. Talleyrand departs again with a modified proposal (player can adjust terms). Another turn of transit. Counter-offer chain can continue but each round costs 1 DP + 1 turn. Natural limit: DP runs out.

**EC-U: AI proposal arrives while player proposal is in transit.** Both resolve. Player's proposal resolves at start of next turn (Talleyrand returns). AI proposal is queued and delivered the following turn (one popup per turn rule). If AI proposal is from the SAME nation you're already negotiating with, it's merged: "While Talleyrand was en route, Hardenberg also sent terms."

**EC-V: Vassal rebellion during enemy turn.** Vassal loyalty is processed at START of `advance_turn()`, before any actions. If loyalty hits 0, rebellion fires immediately: vassal marshals switch to enemy, vassal regions become hostile. All this completes before the player's turn begins — the rebellion appears in Morning Dispatch. Player cannot prevent it mid-processing.

**EC-W: War score when war restarts.** When war is re-declared after peace, war score resets to 0 (fresh war). Previous war's decisive battles do NOT carry over. Casus belli may carry over if the peace was broken.

**EC-X: Simultaneous vassal rebellion + enemy attack.** If vassal rebels on the same turn an enemy attacks a vassal-held region, the rebellion fires first (during advance_turn). The region becomes hostile to France. The enemy attack then targets a now-hostile region — which may mean the attack is no longer valid or produces different outcomes. Processing order: rebellion → territory update → enemy phase.

**EC-Y: Trade income when state downgrades mid-turn.** Trade income is calculated once per turn during income phase. If a diplomatic state changes mid-turn (e.g., AI breaks treaty during enemy phase), the income for that turn uses the state as of the START of turn. Next turn reflects the new state. No retroactive adjustment.

**EC-Z: Armistice expires while proposal in transit.** If an armistice expires (minimum 3 turns reached) while Talleyrand is carrying a peace proposal, the proposal still delivers normally. The war resumes at the start of the turn, but Talleyrand's proposal can produce instant peace if accepted. Race condition resolved: proposal delivery → response popup → then war resumes if rejected.

**EC-AA: Decisive battle bonus on multi-nation war.** If France is at war with both Prussia and Austria, and a battle involves Austrian/Prussian coalition forces, the decisive battle bonus applies to each war score independently. A decisive victory over Archduke Charles at Vienna counts for France-Austria war score but NOT France-Prussia war score (unless Prussian forces participated — checked via battle participants).

**EC-BB: Diplomatic state with no matching treaty.** If an alliance exists but no formal treaty is tracked (e.g., starting alliances from §1e), the system creates implicit treaty records during initialization. Every diplomatic state above PEACE has an implicit treaty. Breaking the state breaks the implicit treaty with all associated penalties.

**EC-CC: Multiple vassals rebelling same turn.** Each vassal's loyalty is checked independently. Multiple can rebel simultaneously. Each rebellion's cascade penalty (-10 to other vassals) is applied cumulatively. If 2 of 3 vassals rebel, the third takes -20 cascade, potentially triggering a triple rebellion. Processing order: alphabetical by vassal name (deterministic).

**EC-DD: Counter-offer modifies territory clause.** When AI generates a counter-offer, it can modify territory clauses (e.g., "we'll cede Saxony but not Berlin"). The player sees both the original proposal and the counter-proposal side by side. Territory modifications are evaluated as clause-level diffs — each changed clause shows old vs new values.

**EC-EE: Invest in vassal on cooldown.** If the 3-turn investment cooldown hasn't expired, the action is blocked with message: "Talleyrand reports our recent investment in Saxony is still bearing fruit. Further investment would be wasteful at this time." DP is NOT deducted for blocked actions.

**EC-FF: War score with no battles (pure territory war).** War score can be non-zero purely from territory control. If France occupies all Prussian regions without winning a battle (e.g., Prussia retreated), war score = territory score only. This is sufficient for peace proposals but makes vassalage difficult (no decisive battle bonus).

**EC-GG: Alliance cascade on war declaration with vassal.** If France vassalizes Saxony and then Prussia (allied with Britain) declares war on Saxony, France enters war with Prussia (lord defends vassal). If France was at peace with Prussia, this changes France-Prussia state to WAR. Britain's alliance with Prussia does NOT automatically cascade unless Britain has a DEFENSIVE_ALLIANCE with Prussia specifically against France.

**EC-HH: Diplomatic state downgrade during armistice.** You cannot downgrade from ARMISTICE — it's already one step above WAR. The only transitions from ARMISTICE are: → PEACE (upgrade, negotiate treaty) or → WAR (armistice expires/broken). No downgrade path from ARMISTICE.

---

## §13. New Model Fields

### WorldState fields:

```python
# ═══════ DIPLOMACY SYSTEM (Phase 8) ═══════

# Diplomatic states between nation pairs
# Key: frozenset({nation_a, nation_b}) serialized as "nation_a|nation_b" (alphabetical)
# Value: diplomatic state string
self.diplomatic_states: Dict[str, str] = {}  # Populated from §1e defaults

# Nation relations (-100 to +100)
# Same key format as diplomatic_states
self.nation_relations: Dict[str, int] = {}  # Populated from §1e defaults

# Diplomatic Points remaining this turn (player only — AI DP tracked internally)
self.diplomatic_points: int = 3
self.max_diplomatic_points: int = 3

# Active treaties
# Key: "nation_a|nation_b", Value: list of treaty clause dicts
self.active_treaties: Dict[str, List[Dict]] = {}

# War score per war (nation pair at war)
# Key: "nation_a|nation_b", Value: int (-100 to +100, positive = nation_a winning)
self.war_scores: Dict[str, int] = {}

# Pending diplomatic proposal (popup for player — returned from transit)
self.pending_diplomatic_proposal: Optional[Dict] = None

# Proposal in transit (Talleyrand is traveling — resolves next turn)
# {"target_nation": str, "original_proposal": dict, "actual_proposal": dict,
#  "sabotaged": bool, "departure_turn": int}
self.proposal_in_transit: Optional[Dict] = None

# Talleyrand's active diplomatic mission
# {"type": str, "target": str, "dp_cost": int, "started_turn": int, "paused": bool}
self.active_diplomatic_mission: Optional[Dict] = None

# AI proposal cooldowns: {"nation": turns_remaining}
self.ai_proposal_cooldowns: Dict[str, int] = {}

# Player proposal cooldowns (M4): {"nation": turns_remaining, "nation|type": turns_remaining}
self.player_proposal_cooldowns: Dict[str, int] = {}

# Armistice cooldowns (E1): {"nation_a|nation_b": turns_remaining}
self.armistice_cooldowns: Dict[str, int] = {}

# Threat level (France-specific, 0-100)
self.threat_level: int = 0

# Vassal tracking
# Key: vassal_nation, Value: {"lord": str, "loyalty": int, "autonomy": int,
#   "investment_cooldown": int, "path": "treaty"|"conquest"}
self.vassals: Dict[str, Dict] = {}

# Vassal investment cooldowns: {"vassal_nation": turns_until_investable}
self.vassal_investment_cooldowns: Dict[str, int] = {}

# AI diplomatic action queue (proposals waiting for player)
self.diplomatic_queue: List[Dict] = []

# Talleyrand sabotage tracking
# List of undetected sabotages: [{"turn": int, "original": dict, "modified": dict}]
self.undetected_sabotages: List[Dict] = []

# Continental System active participants
self.continental_system_members: List[str] = []

# Decisive battles record (§6e): [{"turn": int, "winner": str, "loser": str,
#   "winner_casualties": int, "loser_casualties": int, "location": str}]
self.decisive_battles: List[Dict] = []

# War battle records: {"nation_a|nation_b": {"wins_a": int, "wins_b": int,
#   "last_battle_turn": int}} — for war score calculation
self.war_battle_records: Dict[str, Dict] = {}
```

### New Talleyrand entity:

```python
# Talleyrand is NOT a Marshal. He's a DiplomaticRepresentative.
# Stored on WorldState, not in marshals dict.

class DiplomaticRepresentative:
    def __init__(self, name, nation, personality, skill, biography=""):
        self.name = name
        self.nation = nation
        self.personality = personality  # "schemer", "loyalist", "hawk", "dove"
        self.skill = skill  # 1-10
        self.biography = biography
        self.trust = Trust(starting_value=55)  # Low — Schemer felt from day one

    # Serialization: to_dict() / from_dict() required

self.diplomats: Dict[str, DiplomaticRepresentative] = {}  # nation -> diplomat
```

All fields MUST be added to `to_dict()` and `from_dict()` with `.get()` defaults. Run `test_serialization_enforcement.py` after.

---

## §14. Implementation Plan

### Walking Skeleton (Minimum Viable Diplomacy)

80% of gameplay value with ~40% of implementation cost:

1. Map expansion (19 regions) + new nations + new marshals
2. Diplomatic states (WAR/ARMISTICE/PEACE only) + transition logic
3. Acceptance formula (core formula, no personality modifiers yet)
4. Talleyrand commands (propose peace/armistice, keyword parsing)
5. DP economy (generation, costs, per-turn)
6. AI peace proposals (when losing badly)
7. Diplomatic Ledger UI (basic nation cards)

This skeleton is playtest-able before building vassals, Continental System, or Talleyrand defiance.

### Files to Modify

| File | Changes |
|------|---------|
| `backend/models/region.py` | 6 new regions in REGIONS_DATA, updated adjacency for existing regions |
| `backend/models/marshal.py` | New marshal definitions (Gneisenau, Archduke Charles, Schwarzenberg, Reynier), relocated starting positions |
| `backend/models/world_state.py` | New nations in enemy_nations, nation_gold, nation_actions, manpower_pools. New diplomatic state fields. Expanded _setup_initial_control(). DP in advance_turn(). |
| `backend/commands/executor.py` | New _execute_diplomatic() family. Talleyrand command routing. Treaty application. |
| `backend/commands/parser.py` | Diplomatic command parsing (propose/demand/offer keywords) |
| `backend/ai/llm_client.py` | Mock parser diplomatic keywords |
| `backend/ai/validation.py` | VALID_ACTIONS: add diplomatic actions |
| `backend/ai/enemy_ai.py` | AI diplomatic phase (proposal generation, acceptance evaluation) |
| `backend/game_logic/dispatch.py` | Diplomatic events in Morning Dispatch |
| `backend/game_logic/ledger.py` | Treaty section in Strategic Ledger |
| `backend/campaign_log.py` | Diplomatic event types |
| `backend/notifications.py` | DIPLOMATIC_PROPOSAL, TREATY_SIGNED, SABOTAGE_DISCOVERED notification types |
| `backend/main.py` | GET /diplomatic_ledger, POST /diplomatic_response, proposal popup pass-through |

### New Files

| File | Purpose |
|------|---------|
| `backend/game_logic/diplomacy.py` | Core diplomatic engine: acceptance formula, state transitions, treaty evaluation, DP management |
| `backend/game_logic/vassal.py` | Vassal loyalty, tribute, rebellion, autonomy |
| `backend/models/diplomat.py` | DiplomaticRepresentative class, diplomatic personality definitions |
| `backend/commands/diplomatic_defiance.py` | Talleyrand's defiance: probability curve, sabotage application, discovery |
| `godot-client/.../diplomatic_ledger.gd` | Diplomatic Ledger screen |

### Session Plan (5 Core + 1 Polish)

#### Session 1: Map Expansion + New Nations (LOW RISK)

**Scope:**
- 6 new regions in region.py (Normandy, Hanover, Berlin, Saxony, Dresden, Bohemia, Tyrol — 7 new, 19 total)
- Updated adjacency for all existing regions
- Renamed "Rhine" → "Rhineland"
- New marshal definitions: Gneisenau, Archduke Charles, Schwarzenberg, Reynier
- Relocated starting positions (Grouchy → Lyon, Uxbridge → Hanover, Blücher → Berlin)
- New nations in world_state: Austria, Saxony added to enemy_nations, nation_gold, nation_actions, manpower_pools
- Expanded _setup_initial_control() with all 19 regions
- Vienna reassigned from Prussia to Austria capital

**Risk:** LOW — new data, expanded initialization. No logic changes. Existing tests may need starting position updates.
**Gate:** `pytest` passes. All 19 regions created. All marshals at correct positions. All nations have gold/actions.

#### Session 2: Diplomatic States + Acceptance Formula (MEDIUM RISK)

**Scope:**
- New file: `backend/game_logic/diplomacy.py`
- New file: `backend/models/diplomat.py`
- DiplomaticRepresentative class
- Diplomatic state tracking (nation pairs)
- State transition validation (upgrade adjacency + downgrade §5b.1 + armistice cooldown §5b.2)
- Acceptance formula (all components)
- War score calculation (§6e: territory ±40 + battles ±30 + decisive ±20 + capital ±30)
- Military Supremacy modifier (§6b.1: war score ≥70 + hold capital → +25 acceptance)
- Nation relation tracking
- DP generation + spending
- Serialization for all new fields

**Risk:** MEDIUM — core formula with many modifiers needs careful balancing. But formula is deterministic and testable.
**Estimated tests:** ~60
**Gate:** Acceptance formula returns correct scores for test scenarios. State transitions enforce adjacency.

#### Session 3: Talleyrand Commands + AI Proposals (MEDIUM RISK)

**Scope:**
- Talleyrand command parsing (mock parser keywords)
- _execute_diplomatic() in executor.py
- Proposal creation from parsed commands
- AI diplomatic phase in enemy_ai.py (proposal generation when losing)
- AI proposal popup (same pattern as objection popup)
- Accept/reject/counter-offer flow
- Treaty ratification and clause application
- Gold/turn and manpower clauses applied during advance_turn()
- Morning Dispatch diplomatic events

**Risk:** MEDIUM — command flow is new but follows executor pattern. AI proposals follow popup pattern.
**Estimated tests:** ~50
**Gate:** curl test: "Talleyrand, propose peace with Prussia" returns formatted response. AI sends armistice when losing.

#### Session 4: Vassal System + Treaty Clauses (MEDIUM RISK)

**Scope:**
- New file: `backend/game_logic/vassal.py`
- Passive vassal loyalty (autonomy drift, garrison, shared enemy, war results)
- Two vassalage paths (treaty + conquest)
- Autonomy levels (PUPPET -4/turn, SATELLITE -2/turn, AUTONOMOUS +1/turn)
- "Invest in vassal" one-shot action (1 DP + 200g → +10 loyalty, 3-turn cooldown)
- Tribute collection, autonomy change command
- Vassal rebellion (loyalty=0 → WAR, cascade -10 to other vassals)
- AP/turn treaty clause implementation
- Territory cession logic + marshal relocation
- Continental System (basic, 75g cap per nation, 200g total cap)

**Risk:** MEDIUM — vassal system is self-contained. AP clause modifying nation_actions needs careful integration.
**Estimated tests:** ~45
**Gate:** Vassal loyalty ticks. Rebellion fires at 0. Tribute collected. AP clause reduces actions.

#### Session 5: Talleyrand Defiance + Diplomatic Ledger UI (MEDIUM RISK)

**Scope:**
- New file: `backend/commands/diplomatic_defiance.py`
- Talleyrand defiance probability curve
- Sabotage application (proposal modification)
- Discovery mechanics
- Talleyrand objections (V2a pattern)
- Diplomatic Ledger Godot UI (D key)
- Nation cards, treaty display, threat level
- Notification types

**Risk:** MEDIUM — defiance follows existing V2b pattern. Godot UI follows Strategic Ledger pattern.
**Estimated tests:** ~40
**Gate:** Talleyrand sabotages with correct probability. Ledger screen opens and displays data.

#### Session 6 (Polish — DEFERRED)

- AI-AI diplomacy (nations negotiating with each other)
- Counter-offer AI logic
- Enemy vassal courting
- Fog-filtered diplomatic intel
- Campaign log diplomatic events
- Special acceptance bonuses (§6d)
- Continental System full implementation

**Estimated tests:** ~35

### What Can Be Deferred

| Feature | Impact of Deferral |
|---------|-------------------|
| AI-AI diplomacy | Medium — world feels less alive, but player-facing diplomacy works |
| Continental System | Low — economic warfare is flavor, not core |
| Vassal courting | Low — can add after vassal system is stable |
| Talleyrand defiance | Medium — core diplomatic flow works without sabotage layer |
| Counter-offers | Low — accept/reject is sufficient for v1 |
| Special acceptance bonuses (§6d) | Low — generic formula works, bonuses add flavor |

### Integration Risk Points

| Risk | File(s) | Mitigation |
|------|---------|------------|
| Map expansion breaks existing tests | region.py, world_state.py, many test files | Run full test suite after Session 1. Fix hardcoded region expectations. |
| Marshal relocation breaks balance | marshal.py, enemy_ai.py | Playtest 5 turns after Session 1. Adjust strength if needed. |
| DP generation in advance_turn | world_state.py | Simple reset — low risk. Test DP edge cases (0 DP, max DP). |
| AP/turn clause modifying nation_actions | world_state.py, executor.py | Apply during income phase, AFTER action reset. Test 0-AP edge case. |
| Acceptance formula balance | diplomacy.py | Numbers in spec are starting points. Expect tuning after playtest. |
| Vassal rebellion during enemy turn | vassal.py, turn_manager.py | Process at start of advance_turn, before any actions. |

### Test Coverage

~250 tests across 5 sessions. Key areas:

- **Map:** 19 regions created, adjacency bidirectional, all nations assigned correct starting regions
- **Marshals:** New marshals created, starting positions correct, stats reasonable
- **Economy:** Income calculations correct for 5 nations, manpower pools initialized
- **Diplomatic states:** Transition validation (can't jump WAR→ALLIANCE), adjacency enforced
- **Acceptance formula:** Component calculation, worked examples match, threshold behavior
- **War score:** Territory + battles + casualties
- **DP:** Generation, spending, floor at 1, authority bonus, capital loss penalty
- **Treaties:** Clause application (gold/turn, AP/turn, territory), breaking penalties
- **Vassals:** Loyalty tick, rebellion at 0, tribute, autonomy levels
- **Talleyrand defiance:** Probability curve, sabotage modification, discovery chance
- **AI proposals:** Trigger conditions, acceptance evaluation, popup generation
- **Serialization:** All new fields round-trip
- **Edge cases:** §12 full list

---

## §15. What This Spec Does NOT Cover

- **Coalition trigger and formation** — See COALITION_SPEC.md (companion spec, builds on threat level from this spec)
- **Naval combat** — Britain's naval power is abstracted as economic effects
- **LLM diplomatic conversations** — Phase 8.5. For now, templates + keyword parsing
- **Modding support** — Diplomatic personality definitions could be moddable later
- **Map renderer updates** — Art-blocked, separate task
- **Multiple simultaneous wars** — France can be at war with multiple nations, but the war score is tracked per pair
- **Peace conference (multi-nation)** — Deferred. V1 uses bilateral negotiations only
- **Espionage system** — Sabotage detection through Talleyrand is the only intel mechanic for now

---

## §16. Design Questions — RESOLVED

All design questions resolved in v1.1 feedback pass:

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Dresden (19th region) | **Keep** | Saxony needs a proper capital for conquest-vassalage. "Capture Dresden" is a clearer objective. |
| 2 | Bavaria ownership | **Austria** (4 regions) | Stronger swing state makes the courting game more consequential. Whoever gets Austria shifts balance of power. |
| 3 | British capital | **No London** | Britain's power is naval/economic. Can't march to London — that's the point. They're the enemy you negotiate with or outlast. |
| 4 | Talleyrand trust | **55** | Lower than expected. Sabotage window is real from day one. Player must actively build trust — creates early tension between managing Talleyrand vs. accepting risk. |
| 5 | DP accumulation | **Use-it-or-lose-it** | Forces per-turn priority decisions. Banking = one big diplomatic blitz, which doesn't feel like managing ongoing relationships. Same philosophy as AP. |
| 6 | Armistice duration | **3 turns** | Enough to reposition, short enough to create urgency. Player must have peace proposal ready or war restarts. |
| 7 | Trade income | **50/100/150/200 scaling** | Start low, tune via playtest. Deeper diplomatic states visibly more profitable than shallow ones = incentive to progress relationships. |
| 8 | Vassal courting | **Include in v1** | Full diplomatic loop too important to defer. Simplified form: 2 DP per attempt, loyalty -15 if loyalty < 50. |
| 9 | AP treaty cap | **1 AP/turn max, war-reparation tier** | -25 acceptance penalty. Requires war score > 80. Talleyrand always objects. Late-game dominance move, not routine. |

---

## §17. Changelog

### v2.0 (Full Audit Revision — Feb 2026)

**Audit-driven revision addressing 40+ findings from independent design review.** Previous grade: 47/80 (C). Target: 65+/80 (A).

**Critical Fixes (C1-C4):**
- **C1: War Score Formula defined inline (§6e).** No longer depends on non-existent COALITION_SPEC.md. Full formula: territory ±40 + battles ±30 + decisive battle bonus ±20 + capital ±30 = ±100. Includes war score decay (-2/turn stale) and implementation specification.
- **C2: HOSTILE_NEUTRAL eliminated.** Replaced throughout with PEACE + negative relation. §1a, §1e, §5a, §10b updated. Hostility is expressed by relation value (-30), not by a phantom state.
- **C3: Downgrade transitions added (§5b.1).** Full reverse adjacency: ALLIANCE→DEF_ALLIANCE→NON_AGGRESSION→OPEN_BORDERS→PEACE. Costs, relation hits, threat changes specified. Automatic decay when relation drops 30+ below threshold for 5 turns.
- **C4: Command parser routing specified (§2f).** Name-gated prefix routing: Talleyrand→diplomatic parser, marshal→military parser. Mock parser keywords, execution routing, LLM integration steps documented.

**Major Fixes (M1-M8):**
- **M1: IMPROVE_RELATIONS deduped.** Removed one-shot version from §4b. Only the ongoing mission (§2e) remains.
- **M2: DP starting calculation fixed.** Authority threshold lowered from ≥80 to ≥60 for +1 bonus. France now starts at 4 DP/turn (2 base + 1 skill + 1 authority). Max raised to 5.
- **M3: Dictated peace enabled.** Military Supremacy modifier (§6b.1): war score ≥70 + hold capital → +25 flat acceptance bonus. Tilsit scenario now mathematically possible (base 10 + war score 30 + supremacy 25 + skill 8 = 73 → ACCEPT).
- **M4: Player proposal cooldown added.** 3 turns per-nation after rejection, 5 turns per-type. Symmetrical with AI anti-spam (§9a). Counter-offers exempt.
- **M5: Section 10b duplication fixed.** Second §10b renamed to §10c (Integration Points).
- **M6: Trade income integration specified (§7e).** Income phase location, code pattern, TRADE_INCOME table, display in Strategic Ledger.
- **M7: AI Nation DP generalized.** All nations use same `_calculate_dp()` formula. No hardcoded pools. Dynamic with authority changes.
- **M8: PUPPET vassal nerfed.** PUPPET drift doubled to -4/turn (was implicit -2). Requires garrison + investment to maintain. SATELLITE and AUTONOMOUS now competitive.

**Exploit Fixes (E1-E5):**
- **E1: Armistice chaining blocked (§5b.2).** 5-turn cooldown between armistices per nation pair.
- **E2: PUPPET extraction nerfed.** Via M8 — PUPPET loyalty drains fast without heavy investment.
- **E3: Proposal spam blocked.** Via M4 — player cooldowns match AI cooldowns.
- **E4: Passive Talleyrand nullification fixed (§3a).** 2% Schemer minimum floor — Talleyrand is never fully tamed.
- **E5: Continental System capped (§5d).** Per-nation reduction 100→75g, total cap 200g. Britain retains minimum 100g naval income.

**User Design Notes:**
- **Decisive Battles in War Score (§6e).** Casualty ratio >2:1 + >10k total casualties → +10 war score bonus, capped ±20. Creates Austerlitz/Jena moments. Named events displayed in Diplomatic Ledger.
- **Vassal Management without Diplomat (§8b).** IMPROVE_LOYALTY mission removed. Vassal loyalty is now passive: autonomy drift, garrison (+5), gold investment one-shot (§4b), shared enemies, war results. Talleyrand freed for actual diplomacy. Multi-vassal empire historically accurate.

**Edge Cases Added (EC-V through EC-HH):**
14 new edge cases: vassal rebellion timing, war score reset, simultaneous rebellion+attack, trade income mid-turn, armistice-proposal race, multi-nation decisive battles, implicit treaty records, cascade rebellion, counter-offer territory, invest cooldown, no-battle war score, vassal alliance cascade, armistice downgrade.

**Model Fields Added:**
- `player_proposal_cooldowns`, `armistice_cooldowns`, `vassal_investment_cooldowns`, `decisive_battles`, `war_battle_records`

**Self-Audit Score: 68/80 (Grade A)**

| Category | v1.2 | v2.0 | Delta | Notes |
|----------|------|------|-------|-------|
| Internal Consistency | 4 | 8 | +4 | HOSTILE_NEUTRAL eliminated, dedup resolved, numbering fixed |
| Integration | 5 | 8 | +3 | Trade income path, parser routing, all wiring specified |
| Exploit Resistance | 4 | 9 | +5 | All 5 exploits patched, cooldowns symmetrical |
| Edge Cases | 6 | 9 | +3 | 14 new cases, 35 total (vs JEALOUSY_SPEC's ~20) |
| Historical Plausibility | 8 | 9 | +1 | Decisive battles, multi-vassal empire, Continental System cap |
| Player Experience | 6 | 8 | +2 | 4 DP starting, passive vassal management, downgrade path |
| Implementation Risk | 7 | 8 | +1 | Walking skeleton still clean, session plan updated |
| Spec Completeness | 7 | 9 | +2 | War score formula, downgrade rules, parser routing all inline |
| **Total** | **47** | **68** | **+21** | **Grade: C → A** |

### v1.2 (Proposal Flow + Missions + Top Bar — Feb 2026)

Major additions based on user feedback:

**§2d Proposal Flow — "Talleyrand Goes, Comes Back":**
- Proposals are NOT instant. Talleyrand departs, returns next turn with a package.
- Popup shows: Accept / Reject / Renegotiate (1 DP + 1 turn per renegotiation round).
- Counter-offers from AI are free to accept. Renegotiating costs DP.
- Defiance/sabotage happens during transit — player sees the result, not the alteration.
- One proposal in transit at a time. Forces diplomatic prioritization.
- Talleyrand states: IDLE / IN_TRANSIT / ON_MISSION.

**§2e Diplomatic Missions (Strategic Orders for Diplomacy):**
- IMPROVE_RELATIONS (+5 rel/turn, 1 DP), ~~IMPROVE_LOYALTY~~ (removed in v2.0 — replaced by passive vassal management §8b)
- COURT_NATION (+8 rel/turn + alliance undermining, 2 DP), UNDERMINE_ALLIANCE (-3 rel/turn target pair, 2 DP)
- GATHER_INTEL (3-turn one-shot, 1 DP), REASSURE_ALLY (+3 rel/turn, 1 DP)
- CONTINENTAL_SYSTEM reframed as a mission (2 DP ongoing)
- One mission at a time. Talleyrand skill bonus: +50% at skill 10.
- Proposals pause missions temporarily (1 transit turn), then resume.

**§9a AI Proposals — Anti-Spam:**
- Max 1 AI proposal per turn to player. Per-nation cooldown (3 turns after rejection, 5 turns for same type).
- Talleyrand's assessment on every incoming proposal (1-2 sentence Schemer analysis).
- Queue visible in Diplomatic Ledger Tab 4.

**§10a Diplomatic Top Bar:**
- DP counter, Talleyrand status, envoy indicator, threat level (when > 30).
- Same pattern as existing top bar AP display and notification bar.

**New model fields:**
- proposal_in_transit, active_diplomatic_mission, ai_proposal_cooldowns

**5 new edge cases (EC-Q through EC-U):**
- Proposal blocking during transit, mission+proposal interaction, DP insufficient for mission, renegotiation chains, concurrent AI/player proposals.

### v1.1 (Design Questions Resolved — Feb 2026)

All 9 open design questions resolved. Key decisions:
- 19 regions confirmed (Dresden kept for Saxon capital)
- Bavaria → Austria (4 regions, stronger swing state)
- No London (Britain abstracted, can't be conquered)
- Talleyrand trust: 55 (Schemer felt from day one)
- DP: use-it-or-lose-it (forces per-turn decisions)
- Armistice: 3 turns (urgency)
- Trade income: 50/100/150/200 scaling (tune via playtest)
- Vassal courting: included in v1 (simplified)
- AP treaty: war-reparation tier (1 max, -25 acceptance, war score > 80 required)

Expanded treaty clause types:
- Added cavalry↔artillery unit swaps (historically common, interesting gameplay)
- Added gold↔manpower trades (buy/sell recruits)
- AP clause elevated to war-reparation tier with massive acceptance penalty
- Talleyrand always objects to AP demands (STRONG concern)
- AP sabotage vector: Talleyrand might OFFER more AP than authorized
- Deal demand negative modifiers added to acceptance formula (asymmetric with sweeteners)
- NON_AGGRESSION trade income corrected from +50 to +150 (progressive scaling)

### v1 (Initial Draft — Feb 2026)

Complete first draft covering: 5 nations, 19-region map, diplomatic representatives, DP economy, diplomatic states and transitions, acceptance formula, treaty system, vassal system, Talleyrand diplomatic defiance, AI diplomatic behavior, Diplomatic Ledger UI, fog of war interaction, edge cases, and implementation plan.

Based on user direction document specifying: 5 nations (France/Britain/Prussia/Austria/Saxony), Talleyrand as schemer diplomat, diplomatic personality types (Schemer/Loyalist/Hawk/Dove), DP as separate resource, full diplomatic state progression, acceptance formula, treaty clause types (gold/manpower/AP), vassal mechanics, AI proposals, Diplomatic Ledger screen.
