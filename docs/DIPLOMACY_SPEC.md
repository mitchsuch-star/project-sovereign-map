# Diplomacy System — Design Spec

> **Status:** APPROVED v2.5 — Session 1B readiness audit complete. v2.5: 4 CRITICAL + 3 HIGH findings (PrinceAugust removal, AI PEACE-state gating, marshal stat mismatches, trade income scope). v2.4: 4 CRITICAL + 4 MAJOR (Geneva removal, Berlin income, economy table, Session 1A scope). See §17 changelog.
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

**Britain is special:** No true capital on the map, no London region to conquer. Live `NATION_CAPITALS` uses `"Netherlands"` as Britain's spawn/topology proxy (`backend/models/region.py`) so existing marshal placement, map topology, and runtime nation-support checks have a concrete region. That proxy is not Britain's settlement home capital. British power is projected through continental holdings (Netherlands, Waterloo, Hanover) and naval supremacy (abstracted as economic/strategic effects - see §1d). Britain can lose all continental territory and still be at war. Peace with Britain requires diplomatic resolution, not military conquest. This makes them the diplomatic endgame - you can't just march to London.

**Nation-specific AP:** Reflects administrative capacity. France (4) is the most capable. Austria (3) is bureaucratic. Saxony (2) is tiny. This matters for treaty clauses that cost AP/turn — paying 1 AP/turn when you only have 2 is crippling.

**Terminology (m8):** Throughout this spec, "nation relations" (range -100 to +100, per nation pair) are DISTINCT from "marshal relationships" (range -2 to +2, per marshal pair, existing system). These are separate systems:
- **Nation relations** track diplomatic sentiment between countries (e.g., France-Prussia = -60).
- **Marshal relationships** track personal bonds between commanders (e.g., Ney-Davout = -1).
Winning battles can improve war score (affects nation relations indirectly) AND marshal relationships (directly via Win/Loss formula). But they are independent values stored in different fields. Code should use `nation_relations` for diplomacy and `marshal.get_relationship()` for marshal interactions.

### 1b. Expanded Map (19 Regions)

Expanded from 13 to 19. Goals: French strategic depth, Waterloo deathball broken, Austria on eastern edge, Saxony as central buffer. Layout designed to translate to 1805 full European map.

**Region changes from 13-region map:** Geneva removed (absorbed into Tyrol/Milan corridor — its adjacencies to Marseille, Milan, and Bordeaux are redistributed). Rhine renamed to Rhineland. 7 new regions added (Normandy, Hanover, Berlin, Saxony, Dresden, Bohemia, Tyrol). Net: 13 − 1 (Geneva) + 7 new = **19 regions.**

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
              [Lyon]---[Marseille]

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
| 12 | **Berlin** | capital | urban | 300 | Prussia | NEW — Prussian capital |
| 13 | **Rhineland** | town | river_crossing | 100 | Prussia | Renamed from "Rhine" |
| 14 | **Saxony** | city | plains | 150 | Saxony | NEW — buffer state |
| 15 | **Dresden** | town | hills | 100 | Saxony | NEW — Saxon capital |
| 16 | **Bavaria** | town | hills | 100 | Austria | Austrian sphere |
| 17 | **Vienna** | capital | urban | 300 | Austria | Austrian capital |
| 18 | **Bohemia** | city | forest | 150 | Austria | NEW — northern Austria |
| 19 | **Tyrol** | town | mountains | 100 | Austria | NEW — Alpine barrier |

**19 regions confirmed.** Dresden gives Saxony a proper capital — "capture Dresden" is a clearer objective than "occupy the Saxony region." One extra region is worth it for QA coverage of vassalage gameplay.

**Capital note:** Paris, Berlin, and Vienna use `region_type: "capital"` (300 income, 2 building slots) AND `is_capital: True`. Dresden uses `region_type: "town"` (100 income, 0 building slots) but still has `is_capital: True` — it's a minor nation's capital with capital mechanics (garrison, capture threat) but town-level economy. This is intentional: Saxony is a minor power and shouldn't have capital-tier income.

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
| **France** | Grouchy | Lyon | 28,000 | Literal | Infantry | MOVED from Belgium → Lyon (deathball fix) |
| **France** | Drouot | Paris | 25,000 | Cautious | Artillery | Unchanged |
| **Britain** | Wellington | Waterloo | 52,000 | Cautious | Infantry | Unchanged |
| **Britain** | Uxbridge | Hanover | 24,000 | Aggressive | Cavalry | MOVED from Netherlands → Hanover |
| **Prussia** | Blücher | Berlin | 40,000 | Aggressive | Infantry | MOVED from Rhine → Berlin |
| **Prussia** | Gneisenau | Rhineland | 32,000 | Cautious | Infantry | NEW marshal, Prussian second-in-command |
| **Austria** | Archduke Charles | Vienna | 35,000 | Cautious | Infantry | NEW — Austria's best general |
| **Austria** | Schwarzenberg | Bohemia | 25,000 | Cautious | Infantry | NEW — cautious coalition commander |
| **Saxony** | Reynier | Dresden | 18,000 | Literal | Infantry | NEW — historical Saxon commander. Adjusted from 10k per COALITION_SPEC §16b R1. |

**Force balance:**
- France: 173,000 total (4 marshals, 8 regions)
- Coalition at war: Britain 76,000 + Prussia 72,000 = 148,000 (4 marshals, 5 regions)
- Neutral: Austria 60,000 (2 marshals, 4 regions), Saxony 18,000 (1 marshal, 2 regions)
- **If Austria joins coalition:** 208,000 vs France 173,000 (+ potential Saxony 18,000)

This creates the diplomatic tension: France is stronger than Britain+Prussia alone, but if Austria joins, France is outnumbered. The player MUST either prevent Austrian entry or flip Prussia.

### 1d. Starting Economy

| Nation | Starting Gold | Income (approx) | Upkeep (5g/1000) | Net/Turn | Notes |
|--------|--------------|------------------|-------------------|----------|-------|
| France | 800 | 1,100 | 865 | +235 | 8 regions. Trade income separate (see below). |
| Britain | 1,500 | 200 + 300 naval | 380 | +120 | 3 regions + naval income. Trade income separate. |
| Prussia | 800 | 400 | 360 | +40 | 2 regions, tight economy. Trade income separate. |
| Austria | 600 | 650 | 300 | +350 | 4 regions, not at war (no war costs). Trade income separate. |
| Saxony | 200 | 250 | 90 | +160 | 2 regions, small army. R1: 18k troops. Trade income separate. |

**British Naval Income:** Britain receives +300 gold/turn from naval supremacy (trade dominance, colonial revenue). This is an abstracted effect — no ship-to-ship combat. Can be reduced via Continental System diplomatic action (see §5d). This makes Britain economically resilient despite small continental holdings.

**Starting trade income (from diplomatic states, §7e):** The income column above shows **region income only** (+ British naval). All trade income from §7e diplomatic states is applied separately during `advance_turn()`. Full trade income breakdown at game start:
- **France:** +50 (Austria PEACE) + 100 (Saxony OB) = **+150** neutral trade
- **Britain:** +200 (Prussia ALLIANCE) + 150 (Austria NON_AGG) + 50 (Saxony PEACE) = **+400** alliance trade
- **Prussia:** +200 (Britain ALLIANCE) + 150 (Austria DEF_ALLIANCE) + 50 (Saxony PEACE) = **+400** alliance trade
- **Austria:** +50 (France PEACE) + 150 (Britain NON_AGG) + 150 (Prussia DEF_ALLIANCE) + 50 (Saxony PEACE) = **+400** alliance trade
- **Saxony:** +100 (France OB) + 50 (Britain PEACE) + 50 (Prussia PEACE) + 50 (Austria PEACE) = **+250** mixed trade

**BALANCE NOTE:** Alliance trade income makes breaking enemy alliances a powerful economic weapon. If France flips Prussia to PEACE (losing Britain ALLIANCE), Prussia loses 200g/turn and Britain loses 200g/turn. This is the economic dimension of diplomacy — the §1d table shows the base economy WITHOUT alliance trade to illustrate how vulnerable nations are if isolated.

**Manpower Pools (new nations):**

```python
DEFAULT_MANPOWER_POOLS = {
    "France":  {"infantry": 80000, "cavalry": 15000, "artillery": 10000},
    "Britain": {"infantry": 50000, "cavalry": 8000,  "artillery": 5000},
    "Prussia": {"infantry": 60000, "cavalry": 10000, "artillery": 5000},
    "Austria": {"infantry": 40000, "cavalry": 5000,  "artillery": 3000},
    "Saxony":  {"infantry": 20000, "cavalry": 3000,  "artillery": 2000},
}
```

### 1e. Starting Diplomatic States

| Pair | Starting State | Notes |
|------|---------------|-------|
| France ↔ Britain | WAR | Active war from game start |
| France ↔ Prussia | WAR | Active war from game start |
| France ↔ Austria | PEACE | Not at war, but relation -30 signals hostility. Austria watching. |
| France ↔ Saxony | OPEN_BORDERS (French-leaning) | Historical Confederation of Rhine orbit. Satisfies vassalage prerequisite (E3). See COALITION_SPEC §16b R5. |
| Britain ↔ Prussia | ALLIANCE | Coalition partners |
| Britain ↔ Austria | NON_AGGRESSION | Austria uncommitted — can be courted by France. Adjusted from DEFENSIVE_ALLIANCE per COALITION_SPEC §16b R2. |
| Britain ↔ Saxony | PEACE | Neutral |
| Prussia ↔ Austria | DEFENSIVE_ALLIANCE | Coalition partners |
| Prussia ↔ Saxony | PEACE | Neighbors, Prussia covets Saxony |
| Austria ↔ Saxony | PEACE | Neutral |

**Starting Nation Relations (§6 scale, -100 to +100):**

| Pair | Relation | Why |
|------|----------|-----|
| France ↔ Britain | -80 | Ancient rivals, active war |
| France ↔ Prussia | -40 | At war, but historically flippable. Adjusted from -60 per COALITION_SPEC §16b R4. |
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
| **Schemer** | Best diplomatic stats. May "diplomatically defy" at low authority/trust. Substitutes what HE thinks is best — not betrayal, course correction. | Talleyrand, Metternich |
| **Loyalist** | Moderate stats, never sabotages, always reliable. | Caulaincourt |
| **Hawk** | Penalties to peace proposals, bonuses to demands/ultimatums. Objects to generous terms. | Hardenberg |
| **Dove** | Bonuses to peace/alliance, penalties to harsh demands. Objects to conquest-driven proposals. | Einsiedel |

### 2b. Diplomatic Representatives

| Nation | Representative | Personality | Skill | Biography |
|--------|---------------|-------------|-------|-----------|
| **France** | **Talleyrand** | Schemer | 10 | "The devil's diplomat. Serves France — or rather, serves what he believes France should be. Not always the same thing." |
| **Britain** | **Castlereagh** | Hawk | 7 | "Cold, calculating, implacable. Views any French advantage as a threat to the balance of power." |
| **Prussia** | **Hardenberg** | Hawk | 6 | "Prussian pride dressed in diplomatic language. Demands respect, offers little." |
| **Austria** | **Metternich** | Schemer | 9 | "The spider of European diplomacy. Delays commitment, builds leverage, strikes when the moment is right. Arranged Napoleon's marriage to buy time, then used armed mediation to justify switching sides. Will join whoever seems most likely to prevail — but always extracts a price." |
| **Saxony** | **Count Einsiedel** | Dove | 4 | "A minor court's minor diplomat. Hopes for peace, fears aggression, and prays Saxony survives the storm. Objects to any proposal that might provoke a larger power." |

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
- `what would it take/can we/is it possible/how hard/feasibility` → feasibility request (§2g)
- Target nation parsed from command: "with Prussia", "to Austria", etc.

### 2d. Proposal Flow — "Talleyrand Goes, Comes Back"

Diplomatic proposals are NOT instant. You tell Talleyrand what you want. He travels, negotiates, and returns next turn with a package. This creates tension, forces planning, and is where defiance happens (he alters the proposal during the travel turn).

**The flow:**

```
TURN 1: Player issues proposal command
  "Talleyrand, propose peace with Prussia: they keep Berlin, open borders, 200 gold/turn"
  → DP spent immediately (2 DP for peace proposal)
  → Talleyrand objection check fires (§3e). If player insists, defiance roll (§3a).
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
- **Proposals interrupt missions temporarily.** If you send a proposal while Talleyrand is on a mission, the mission pauses for the transit turn. It resumes when Talleyrand returns to IDLE state — after ALL proposal resolution, including renegotiation rounds. If renegotiation extends the proposal to 2+ turns of transit, the mission stays paused for the full duration.
- **Cancellation is free** (0 DP, same as strategic order cancel).
- **Mission effects are cumulative per turn.** IMPROVE_RELATIONS running for 3 turns = +15 total relation.
- **Enemy diplomats run missions too (Building Blocks).** AI nations assign their diplomats to missions using the same costs and effects. AI mission priorities follow §9 decision tree.

**Talleyrand skill bonus on missions:**
```
Skill 10 (Talleyrand): mission effects +50%, then int(round()) for Golden Rule #2
  Example: IMPROVE_RELATIONS base +5 → 5 * 1.5 = 7.5 → int(round(7.5)) = 8
Skill 7-9: mission effects as listed (no modifier)
Skill 4-6: mission effects -25%, then int(round())
  Example: IMPROVE_RELATIONS base +5 → 5 * 0.75 = 3.75 → int(round(3.75)) = 4
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

### 2g. Diplomatic Feasibility Requests

The player can consult Talleyrand for feasibility assessments before committing DP to proposals. This is the diplomatic equivalent of asking Berthier for a situation report.

**Commands:**
```
"Talleyrand, what would it take to get peace with Prussia?"
"Talleyrand, can we flip Austria?"
"Talleyrand, how hard would it be to vassalize Saxony?"
"Talleyrand, should I focus on sweetening the deal or improving relations first?"
```

**Mechanics:**
- **Cost: 0 DP.** Consulting your diplomat is free — you're asking for advice, not taking action.
- **Talleyrand state: ADVISING** (momentary — resolves same turn, does not block proposals or missions).
- Talleyrand evaluates the acceptance formula behind the scenes and reports in natural language.

**Feasibility report contents:**
1. **Largest negative factor** (maps formula component to natural language — see §6f feedback table)
2. **Most promising lever** ("A decisive military victory would shift the balance" / "Improving relations over 3-4 turns would open the door")
3. **Difficulty assessment:** One of 5 tiers:
   - "Virtually certain" (projected acceptance >= 70)
   - "Achievable with modest effort" (50-69)
   - "Challenging but possible with concessions" (35-49)
   - "Very difficult without military pressure" (20-34)
   - "Nearly impossible under current conditions" (<20)

**Schemer bias (Talleyrand's personality colors his advice):**
- When threat_level > 50, Talleyrand overstates difficulty of aggressive proposals by one tier ("Challenging" reported as "Very difficult") — he wants to restrain French expansion.
- When relation with target > +20, Talleyrand understates difficulty by one tier — he favors deals with nations he respects.
- Bias is NOT applied to the actual acceptance formula — only to the reported tier. The player can learn to calibrate Talleyrand's assessments over time.
- In mock mode: bias applied deterministically based on threat/relation thresholds.
- In LLM mode: formula components passed as context, LLM generates the assessment with personality coloring.

**Discovery:** If the player acts on a biased assessment and the result differs from what Talleyrand predicted, a Morning Dispatch note hints at the discrepancy: "Talleyrand's assessment of the Prussian court appears to have been... optimistic." This trains the player to question Talleyrand's advice without explicitly revealing the bias mechanic.

**Edge cases:**
- Feasibility for a nation you're already negotiating with: returns "A proposal is already in transit. Talleyrand suggests patience."
- Feasibility for vassalage when OPEN_BORDERS not yet achieved (E3 fix): "Talleyrand notes that formal diplomatic relations must be established first."
- Feasibility during IN_TRANSIT: allowed (momentary ADVISING doesn't conflict with transit).
- **Multi-step transitions:** If the requested goal requires multiple state transitions (e.g., WAR → ALLIANCE requires WAR → ARMISTICE → PEACE → OPEN_BORDERS → NON_AGGRESSION → DEFENSIVE_ALLIANCE → ALLIANCE = 6 transitions), Talleyrand reports the FIRST achievable step AND the total number of steps. Example: "An alliance with Prussia requires 6 diplomatic steps, beginning with an armistice. The first step — armistice — would require [feasibility assessment for armistice]. Each step requires its own proposal and transit time." This prevents misleading feasibility scores for distant goals while giving the player a sense of the total investment required.

**Mock mode implementation:** Keyword detection for "what would it take", "can we", "is it possible", "how hard", "feasibility", "realistic", "should I focus". Returns template keyed to the largest formula component:
```python
# Template selection based on largest negative component:
if abs(relation_modifier) > abs(all_others):
    hint = "Relations are the key obstacle" if negative else "Goodwill is our strongest asset"
elif abs(war_score_modifier) > abs(all_others):
    hint = "Military position drives this negotiation"
elif abs(hegemony_target_mod) > abs(all_others):
    hint = "Bloc pressure is the barrier"
# ... etc for each component
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

**E7 DEFERRED — Defiance floor redesign:** The audit recommended considering raising the floor to 5% for more gameplay visibility. This decision is deferred to the next design session. The defiance system should align with the Building Blocks principle — diplomatic defiance should mirror the combat defiance pattern (V2b) in its probability structure. A comprehensive review of the Schemer minimum floor, the probability curve, and how it integrates with the objection system (V2a pattern) will be conducted before implementation. For now, 2% remains the spec value.

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

### 3d. Talleyrand's Redemption Event (Trust ≤ 20)

When Talleyrand's trust drops to 20 or below, a redemption event fires — same V2b pattern as combat marshals. However, Talleyrand **cannot be dismissed** (EC-M: he's not a military unit; losing him disables the entire diplomacy system). His redemption options are diplomat-specific:

| Option | Effect | Notes |
|--------|--------|-------|
| **Apologize** | Trust +15, Authority -5 | Napoleon admits he pushed too hard. Relationship stabilizes. |
| **Replace with Loyalist aide** | Personality changes from Schemer to Loyalist. Skill drops to 6 (from 10). Trust resets to 50. | France gets a compliant diplomat at the cost of brilliance. Schemer bias disappears — no more sabotage, but no more genius either. Irreversible. After replacement, Talleyrand uses Loyalist personality for ALL mechanical effects: §6b personality modifier (Loyalist +0 instead of Schemer +5), mission skill tier (6 = skill 4-6 bracket → -25% mission effects, +1 DP cost per §4b), Schemer bias in DESIGN templates disabled, defiance floor drops to 0% (standard Loyalist — no Schemer minimum). DESIGN template system must read `diplomat.personality` dynamically, not hardcode "schemer". |
| **Continue with strained relations** | Trust stays at current value. Authority -10. | Napoleon refuses to bend. The working relationship is damaged but functional. |

**Narrative:** Each option is presented as a dramatic conversation scene (DESIGN layer handles the text). The choice reveals the player's leadership style — conciliatory, pragmatic, or stubborn.

**Repeat redemption:** If trust drops to ≤20 again after Apologize or Continue, the same event fires again. After Replace with Loyalist, the new personality prevents further redemption events (Loyalist trust dynamics follow the standard V2b pattern, and a Loyalist with skill 6 rarely triggers defiance).

### 3e. Talleyrand's Objections (Pre-Proposal)

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
Base DP per turn: 3

Talleyrand skill bonus:
  Skill >= 8 (Talleyrand): +1 bonus DP
  Skill 7:                 +0
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

**France at game start: 3 base + 1 (Talleyrand skill ≥8) + 1 (authority ~100, well above ≥60 threshold) = 5 DP/turn.**

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
| Britain | 2 | +1 (Castlereagh 7+) | +0 | **3** | No true home capital on map; Netherlands is only a runtime proxy |
| Prussia | 2 | +0 (Hardenberg 6) | +0 | **2** | Tight economy, tight diplomacy |
| Austria | 2 | +1 (Metternich 9) | +0 | **3** | Metternich compensates for bureaucracy |
| Saxony | 2 | +0 (Einsiedel 4) | +0 | **2** | Minor power, -1 skill penalty → effective 1 DP (costs +1) |

AI DP generation uses `_calculate_dp(diplomat, nation_authority)` — same function as player. No hardcoded pools. AI nations that gain/lose authority (from losing wars, breaking treaties) see DP change dynamically.

**AI Nation Authority:** AI nations track their own authority value (`world.nation_authority: Dict[str, int]`, default 60 for all AI nations, range 0-100). AI authority changes:
- Losing a battle: -3
- Losing a region: -5
- Breaking a treaty: -10
- Winning a battle: +2
- Signing a favorable treaty: +5
- AI authority starts at 60 (neutral — no DP bonus at game start)
- Only France (player) uses the existing `world.authority` field from AuthorityTracker

---

## §5. Diplomatic States & Transitions

### 5a. State Definitions

States between each nation pair, from most hostile to most friendly. **Hostility within a state is expressed by relation value, not by a separate state** — there is no "HOSTILE_NEUTRAL." Austria at PEACE with relation -30 behaves differently from Saxony at PEACE with relation +40, but both are mechanically at PEACE.

| State | Movement | Combat | Economy | Other |
|-------|----------|--------|---------|-------|
| **WAR** | Cannot enter enemy territory without attacking | Full combat | Pillage/plunder enabled | Default hostile state |
| **ARMISTICE** | Cannot enter enemy territory | No combat (ceasefire) | No trade | 5-turn minimum duration. Either side can end it (returns to WAR) |
| **PEACE** | Cannot enter each other's territory | No combat | Trade (+50 gold/turn bilateral) | Stable state, breaking requires war declaration |
| **OPEN_BORDERS** | Can move through each other's territory | No combat | Trade (+100 gold/turn bilateral) | No military access — can move THROUGH, not station troops |
| **NON_AGGRESSION** | Cannot enter each other's territory | No combat | Trade (+150 gold/turn bilateral) | Breaking pact = severe relation hit (-40) and threat spike |
| **DEFENSIVE_ALLIANCE** | Open borders + military coordination | Defend ally if attacked | Trade (+150 gold/turn bilateral) | If ally is attacked by third party, you enter WAR with the attacker |
| **ALLIANCE** | Full military coordination | Joint wars, coordinated attacks | Trade (+200 gold/turn bilateral) | Offensive + defensive. Current engine still auto-enters full allies on offensive declarations; the commitments follow-up replaces only that offensive auto-entry path with a player-visible ally-entry decision, while defensive honor remains automatic unless commitments hard blocks apply. |
| **VASSAL** | Lord controls vassal movement | Lord can order vassal troops | Tribute flows to lord | See §8 for full vassal mechanics |

### 5b. Transition Rules

The guided diplomacy UI presents adjacent upgrades, but the engine supports non-adjacent upward jumps with cumulative DP cost per R98. Downgrades still follow reverse adjacency one step at a time unless a domain-specific rule says otherwise. Direct `WAR` → `ALLIANCE` is valid only through explicit ratification effects that own their side effects, such as `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md` `forced_alliance`.

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
  VASSAL → PEACE (voluntary release — lord grants independence, costs 1 DP)
    Relation with former vassal: +20 (grateful for freedom)
    Relation with all nations: +5 (France seen as magnanimous)
    Threat: -5 (reduced empire)
    Former vassal retains current territory. Loyalty/tribute end immediately.
  OPEN_BORDERS/above → VASSAL (negotiated vassalage — requires OPEN_BORDERS minimum + acceptance formula. Prevents Turn-1 vassalage exploit — E3 fix)
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
| WAR → ARMISTICE | 1 | None (war exhaustion drives this) | 5-turn minimum |
| ARMISTICE → PEACE | 2 | Relation > -60 | May require treaty clauses |
| PEACE → OPEN_BORDERS | 1 | Relation > -20 | |
| OPEN_BORDERS → NON_AGGRESSION | 1 | Relation > 0 | |
| NON_AGGRESSION → DEF_ALLIANCE | 2 | Relation > +20 | |
| DEF_ALLIANCE → ALLIANCE | 2 | Relation > +40 | |
| OPEN_BORDERS/above → VASSAL (treaty) | 3 | Relation > +20 OR war score > 60. Requires OPEN_BORDERS minimum (E3). | |
| Any → WAR | 1 | None | PLUS relation -30 target, -15 all others, threat +20 (see §5c for full costs) |

**Commitments-era defensive honor rule:** The old defensive cascade bypass for armistice cooldowns is superseded once the commitments ally-entry layer ships. Forced defensive entry remains the baseline expectation, but explicit commitments-layer hard blocks (including armistice / cooldown with the attacker) may still suppress entry. The cooldown only prevents voluntary armistice-chaining; commitments now decide whether a blocked defensive honor call can legally resolve into war entry.

### 5b.3. Conflicting Alliance Obligations (M5)

A nation cannot maintain ALLIANCE or DEFENSIVE_ALLIANCE with two nations that are at WAR with each other. This is the most historically significant diplomatic scenario — Napoleon constantly tried to separate coalition members.

**When a new alliance creates a conflict:**
- The conflicting nation must choose which alliance to maintain.
- **AI resolution:** Choose the alliance with the higher-relation partner. If tied, choose the alliance with the more powerful partner (higher total army strength).
- **Player resolution (if player alliance causes conflict):** Confrontation popup: "Sire, our alliance with Prussia conflicts with their existing alliance with Britain, whom we are at war with. Prussia must choose." (Player observes the outcome — the choice is Prussia's.)
- The dropped alliance follows standard downgrade penalties (§5b.1).

**Commitments follow-up precedence:** If the newer commitments layer detects an active-opposition-pair paradox at ratification time, `commitment_paradox` resolves first and this M5 flow does not also fire for the same ratification. M5 remains the fallback for conflicts introduced later by war declaration or by legacy treaty states that were not intercepted at ratification.

**Timing:** Conflict check runs immediately when a new alliance is ratified or when war is declared. The conflicting nation resolves the conflict on their next turn (AI phase).

**Edge case:** If France allies with Prussia (who has DEFENSIVE_ALLIANCE with Britain), and France is at WAR with Britain: Prussia must choose between France and Britain. Given starting relations (Prussia-Britain +60 vs France-Prussia starting negative), Prussia would choose Britain in most scenarios. The player must improve France-Prussia relations ABOVE the Britain-Prussia level before attempting this.

### 5b.4. Strategic Order Auto-Cancellation on Diplomatic State Change

When a diplomatic state transitions FROM WAR to any non-WAR state (ARMISTICE, PEACE, etc.), all active strategic military orders targeting that nation's marshals are automatically cancelled:

- **PURSUE** orders targeting enemy marshals of the now-peaceful nation: cancelled.
- **MOVE_TO** orders with `attack_on_arrival=True` targeting regions controlled by that nation: cancelled.
- **HOLD** orders in border regions adjacent to that nation: NOT cancelled (marshal may be holding against multiple nations), but sally behavior is restricted — the marshal will NOT sally against the now-peaceful nation's forces. Sally targets are recalculated to exclude marshals of the peaceful nation.
- **SUPPORT** orders supporting attacks against that nation's forces: cancelled.

**Campaign log entry:** "[Marshal]'s orders cancelled — peace with [nation]."
**Morning Dispatch:** "Following the diplomatic resolution with [nation], the following orders have been cancelled: [list]."

**Reverse case (peace → war):** When a diplomatic state transitions TO WAR (war declaration, alliance cascade), existing strategic orders are NOT auto-cancelled. The player may want their marshals to continue current operations. However, HOLD orders in border regions now allow sally behavior against the newly hostile nation.

**Territory cession path invalidation (M5):** When territory controller changes (via treaty cession or conquest), all active strategic orders whose planned paths include the changed region are invalidated. The system attempts re-pathfinding through friendly territory. If no valid path exists, the order is cancelled with notification: "[Marshal]'s route to [destination] is no longer viable — order cancelled."

### 5c. War Declaration Rules

Declaring war on a neutral/friendly nation:
- Costs 1 DP
- Relation with target: -30 immediately
- Relation with ALL other nations: -15 ("aggressor" penalty)
- Threat level: +20 (tracked on WorldState, feeds into COALITION_SPEC coalition formation)
- Talleyrand will object (STRONG concern) if target is neutral and threat > 50
- If target has allies: defensive responders may enter WAR with you, subject to the commitments-era defensive-honor arbitration and hard-block rules

**Casus Belli (reduces penalties):**
If the target broke a treaty, attacked your ally, or controls your core territory, the aggressor penalty is halved (-15 → -7 relation with others, but threat is always +20 — casus belli does not reduce threat). Casus belli is tracked automatically from treaty breaks and attacks.

**Metternich's Armed Mediation (DD8 — Schemer-specific AI behavior):** When Metternich (Schemer personality) proposes peace to France and the proposal is REJECTED, Austria gains +5 to their next war declaration's coalition bonus (if they declare war within 5 turns). This captures Metternich's historical tactic of using failed peace talks as a casus belli — his "armed mediation" at Dresden (1813) presented deliberately harsh terms, and when Napoleon rejected them, Metternich used the rejection to justify joining the Sixth Coalition. This is an AI-only behavior — it does not apply to Talleyrand (who doesn't declare wars on France's behalf).

**In-transit proposal cancellation on war cascade:** When a war declaration cascade (via defensive alliance trigger) creates a WAR state with a nation that has an in-transit proposal (player proposal being carried by Talleyrand), the in-transit proposal is auto-cancelled immediately:
- DP refunded to the player.
- `proposal_in_transit` cleared.
- Talleyrand returns to IDLE.
- Notification (HIGH): "War with [nation] has been declared — your pending proposal is void."
- Morning Dispatch: "Talleyrand's mission to [nation] is moot — hostilities have commenced."
- This also applies when the player declares war directly on a nation they have a proposal in transit to.
- If Talleyrand was on a diplomatic mission targeting the now-hostile nation, that mission also auto-cancels (per EC-NN).

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

  Participation check (m4 — specifies which formula applies):
    This is NOT the full §6 acceptance formula. It's a simplified check
    applied to each participating nation EXCLUDING France (France is the
    organizer, not a participant — France runs the system, others join):
      continue_participating = (relation_with_france > +10)
                             AND (relation_with_britain < +30)
                             AND (NOT at_war_with_france)
    If any condition fails: nation withdraws. No personality modifier,
    no deal_sweetener, no diplomat skill — those apply to PROPOSALS only.
    Participation is binary: you're in or you're out, based on relations.
    Check runs at start of turn, before trade income processing.
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
                 + war_weariness
                 + stalemate_duration
                 + political_subtotal_clamped
                 + settlement_gratitude_mod  # optional Imperial Settlement upside, +5
                 + deal_balance           # sweetener (positive) + demands (negative)
                 + diplomat_skill_bonus
                 + personality_modifier
                 + situational_bonus       # max(military_supremacy, battlefield_diplomacy, military_pressure)
                 + special_desire_bonus
                 + harshness_penalty
                 + harshness_bonus
                 + reliability_modifier
                 + ultimatum_bonus

political_subtotal_clamped = max(
    -60,
    hegemony_target_mod
    + bilateral_betrayal_mod
    + grievance_modifier
    + bargain_conflict_penalty
    + bargain_value_mod
)

deal_balance = deal_sweetener + deal_demands
  (Sweetener: sum of positive modifiers from offered clauses, capped at +60.
   Demands: sum of negative modifiers from demanded clauses, uncapped.
   These are a SINGLE component in the formula — listed separately in §6b
   for clarity, but summed into one value before adding to acceptance_score.)

Final score: acceptance_score = int(round(raw_score))
  (Golden Rule #2: all numbers to Godot must be int(). Round before truncating
   to avoid systematic bias — e.g., 49.7 rounds to 50, not truncates to 49.
   All components are summed as floats. Round ONCE after summing all components.)

# Hard posture gates (`hard_reject_posture`, `oathbreaker_posture`, and
# `anti_renewal_block`) are applied after the normal score is calculated.
# They clamp deep treaty proposals when Memory and Pressure hard-stop rules require it.

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

**R141 Wartime dampening:** During WAR, relation modifier is dampened: `max(-10, min(10, relation / 4))` instead of peacetime `max(-30, min(30, relation / 2))`. Prevents deep hatred from making wartime peace mathematically impossible.

**R142 War weariness:** `+2 per turn at war, cap +20`. Uses `war_start_turns` dict (diplo_key → turn war began). Cleared by `cleanup_war_end()`.

**R143 Stalemate duration:** `+1 per stalemate turn, cap +15`. Uses `ai_stalemate_counters`. Rewards patience in prolonged conflicts.

**R144 Territory sweetener:** Value raised from +5 to +8 per region ceded (see Deal Sweetener table below).

**R145 Gold lump sweetener:** Rate doubled from +1/200 to +1/100 gold offered.

**R146 Sweetener cap:** Raised from +30 to +60 maximum from all sweetener clauses combined.

**Political Pressure Subtotal (Memory and Pressure v2.4.3 + War Bargains):**
```
political_subtotal_raw = (
    hegemony_target_mod
    + bilateral_betrayal_mod
    + grievance_modifier
    + bargain_conflict_penalty
    + bargain_value_mod
)
political_subtotal_clamped = max(-60, political_subtotal_raw)
```

- `hegemony_target_mod`: cross-bloc friction from the hegemony engine, capped at `-20`.
- `bilateral_betrayal_mod`: `-6` per active victim-side betrayal strike.
- `grievance_modifier`: `-30` per active durable grievance, capped at 3 contributing grievances per pair.
- `bargain_conflict_penalty`: `-8` when a live war bargain targets the nation or contested territory.
- `bargain_value_mod`: `+10` / `+15` / `+25` when a proposal fulfills the appropriate war-bargain value band.
- `composite_floor`: synthetic debug row shown when the raw political subtotal is clamped to `-60`.

Threat pressure is not a standalone acceptance component in live code. Coalition threat and hegemony pressure affect diplomacy through their owning systems and through `hegemony_target_mod`.

**Imperial Settlement amendment:** `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` is the authoritative source for `settlement_gratitude_mod`. When Ally Participation / Common Peace lands, it is an optional positive `+5` component for eligible later deep-treaty, war-entry, and war-bargain / ally-entry proposals to an ally that has an active `settlement_gratitude` memory from France; that memory is created only by a current-episode material contribution reward. It is added outside `political_subtotal_clamped`, cannot bypass hard posture gates or political floors, and refreshes rather than stacks.

**Implementation status:** `settlement_gratitude_mod` is pending Imperial Settlement Slice D1. Until that slice lands, live `calculate_acceptance()` behaves as if this component is `0` and may omit it from debug output; Slice D1 must add the live component, proposal-preview row, and regression coverage.

**Deal Sweetener (treaty clauses offered by proposer):**
```
Gold lump sum:            +1 per 100 gold offered (R145: was 200)
Gold per turn:            +3 per 100 gold/turn offered
Manpower per turn (NEW):  +2 per 2000 infantry/turn offered (ongoing recruitment commitment)
Infantry manpower:        +2 per 5000 troops offered (one-time)
Cavalry manpower:         +4 per 2500 cavalry offered (precious)
Artillery manpower:       +5 per 1500 artillery offered (rare)
Unit swap (offered):      +3 per unit trade favorable to target
AP per turn (offered):    +18 per AP/turn offered (most valuable sweetener)
Territory:                +8 per region ceded (R144: was 5)
Open borders:             +3
Protection:               +5 (guarantee of defense — reduced to +3 when guarantor
                               already at war with all of target's enemies, per E8)
```

**DEAL SWEETENER CAP: +60 maximum** (R146: was +30) from all sweetener clauses combined. Prevents gold-dumping exploits where a wealthy France overwhelms the formula with raw concessions. The cap forces the player to address the actual diplomatic obstacles (relations, threat, war score) rather than just throwing gold at the problem. Per-turn commitments count toward the cap at the listed values.

**Per-turn commitments are more valuable:** Per-turn clauses (gold/turn, manpower/turn, AP/turn) represent ongoing commitments — reliable income streams for the recipient, ongoing drains for the giver. This makes them inherently more interesting tradeoffs than lump sums. Per-turn clauses can be broken (treaty-break mechanic applies — see §7d).

**Deal Demands (clauses demanded — NEGATIVE modifiers):**
```
Gold/turn demanded:       -5 per 100 gold/turn
Manpower/turn demanded:   -3 per 2000 infantry/turn (ongoing drain)
Territory demanded:       escalating PL-20 penalty via analyze_territory_demands()
AP/turn demanded:         -25 per AP/turn (WAR REPARATION — nearly impossible)
Unit swap (demanded):     -2 per unit trade unfavorable to target
```

Territory demands use the shared `analyze_territory_demands()` helper: base costs escalate by demanded-region order (`-5`, `-8`, `-11`, ...), multiply by region income weight, double for capital regions, and add elimination guards (`-60` for annexation, `-30` for rump-state reduction). Value-only legacy proposals use the same escalation sequence without region weights.

**Diplomat Skill Bonus:**
```
(proposer_skill - target_skill) * 2

Example: Talleyrand (10) vs Hardenberg (6) → +8
         Count Einsiedel (4) vs Metternich (8) → -8
```

**Personality Modifier:**

| Target Personality | Peace/Alliance Proposals | Harsh Demands/Ultimatums |
|-------------------|--------------------------|--------------------------|
| Dove (Einsiedel) | +10 | -10 |
| Hawk (Castlereagh, Hardenberg) | -5 | +5 |
| Loyalist | +0 | +0 |
| Schemer (Talleyrand, Metternich) | +5 (pragmatic openness) | +5 (respects boldness) |

**Battlefield Diplomacy Bonus (COALITION_SPEC §16 R3):**
```
When war_score > 20 (proposer winning): +10 acceptance.
Only applies to peace/armistice proposals during active war.
Historical basis: military pressure makes diplomacy more persuasive.
Does NOT stack with Military Supremacy modifier (§6b.1) — use whichever is higher.
```

**Military Pressure Bonus (R8):**
```
if war_score > 0:
    military_pressure = int(min(15, war_score * 0.15))
else:
    military_pressure = 0

situational_bonus = max(military_supremacy, battlefield_diplomacy, military_pressure)
```

Military Supremacy, Battlefield Diplomacy, and Military Pressure never stack; the acceptance formula uses only the largest of the three.

### 6c. Worked Example

**France proposes peace with Prussia. War score +25 (France ahead). Relation -60. The war has lasted 4 turns. Memory and Pressure contributes `hegemony_target_mod = -8`, `bilateral_betrayal_mod = -6`, and `grievance_modifier = 0`. Talleyrand (10) proposes. Hardenberg (6) receives. France offers: Prussia keeps Berlin, open borders, 200 gold/turn.**

```
Base disposition (peace):        30
War score (+25 * 0.3):          +7.5
Relation (-60 / 4, cap ±10):   -10
War weariness (4 turns * 2):    +8
Political subtotal:             -14
Deal sweetener:
  Open borders:                 +3
  200 gold/turn:                +6
Diplomat skill (10-6)*2:        +8
Personality (Hawk, peace):      -5
Situational bonus:              +10

Total:                          43.5 → 44 → COUNTER_OFFER
```

Prussia does not accept the first offer outright. France needs better terms, a stronger military position, or more time for war weariness to push the court toward peace.

**Same proposal but France also offers Saxony (territory):**
```
Previous total:                  43.5
+ Territory (Saxony):           +8
+ Extra sweetener (Saxony is
  what Prussia wants):          +10 (special bonus — see §6d)

Total:                          61.5 → 62 → ACCEPT
```

With the wartime relation dampening (relation/4, cap ±10), the relation penalty is much smaller. Adding territory Prussia desires tips the balance — diplomacy rewards understanding what the other side wants.

### 6c.1. Harshness Value Table (C2 Resolution)

The `harshness` score in §7b requires each clause type to have a defined **value** so harshness can be calculated deterministically. Value represents the strategic weight of a clause — how much it "costs" the recipient.

**Clause Value Table:**

| Clause Type | Value (per unit) | Notes |
|-------------|-----------------|-------|
| Gold lump sum | 1 per 200 gold | Low value — one-time, easy to absorb |
| Gold/turn | 3 per 100 gold/turn | Higher — ongoing drain |
| Manpower/turn | 4 per 2000 infantry/turn | Ongoing recruitment commitment |
| Infantry (one-time) | 2 per 5000 troops | Moderate — recoverable |
| Cavalry (one-time) | 4 per 2500 cavalry | Precious — slow to rebuild |
| Artillery (one-time) | 5 per 1500 artillery | Rare — very slow to rebuild |
| Unit swap | 3 per trade | Moderate — depends on direction |
| AP/turn | 10 per AP/turn | Extremely high — sovereignty cost |
| Territory | 8 per region | High — permanent loss |
| Open borders | 2 | Low — reversible |
| Military access | 3 | Moderate — security risk |
| Protection guarantee | 4 | Moderate — commitment risk |
| Continental System | 3 | Moderate — economic cost |

**Harshness calculation (single source: `diplomacy.py`):**
The `calculate_harshness()` function lives in `diplomacy.py` alongside `_calculate_acceptance()` — both are single-source formula functions. DESIGN's template layer reads the harshness value from `diplomacy.py`; it never recalculates independently.

```python
def calculate_harshness(clauses):
    """Returns harshness score -1.0 to +1.0."""
    value_demanded = sum(clause_value(c) for c in clauses if c.direction == "demand")
    value_offered = sum(clause_value(c) for c in clauses if c.direction == "offer")
    total = value_demanded + value_offered
    if total == 0:
        return 0.0  # No clauses — neutral
    return max(-1.0, min(1.0, (value_demanded - value_offered) / total))
```

**Worked example:**
```
France proposes peace with Prussia:
  Demands: Rhineland (territory, value 8) + 200 gold/turn (value 6)
  Offers:  Open borders (value 2) + 5000 infantry (value 2)

  value_demanded = 8 + 6 = 14
  value_offered = 2 + 2 = 4
  total = 14 + 4 = 18
  harshness = (14 - 4) / 18 = 0.56

  Result: Moderate harshness (0.56). Dove bonus does not apply (needs < 0.3 generosity).
  Hawk bonus does not apply (needs > 0.6 harshness). Close to the Hawk threshold.
```

**Current proposal harshness penalty (PL-12-A):** `harshness_penalty = -min(40, max(0, int((current_harshness - 0.2) * 150)))`. Light or balanced proposals avoid the penalty; harsh packages rapidly become harder to accept.

**Escalating treaty harshness (DD8-4 / PL-12-D):** If the target nation was previously defeated and had a harsh treaty imposed on them, acceptance of another harsh package is `-5` harder. Harsh history breeds resentment rather than obedience in the live formula. Tracked via `world.previous_treaties` — if the target appears as treaty recipient with `harshness > 0.3`, the `harshness_bonus` component is `-5`.

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
war_score = (
    territory_score
    + battle_score
    + decisive_battle_bonus
    + capital_score
    + ticking_score
)

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

Ticking score (max ±25 per side):
  From War Purpose + Score Semantics objectives.
  Adds accumulated objective ticking for nation_a minus accumulated objective
  ticking for nation_b.
  Does not decay.

Total capped at ±100.
```

**War score updates automatically** at the end of each turn based on current territory control, cumulative battle record, decisive battle record, capital control, and War Purpose ticking. Territory score recalculates from scratch each turn (current holdings vs starting holdings). Battle score is cumulative but subject to quiet-turn decay. Decisive battle bonus and ticking are cumulative and do not decay.

**Battle score decays toward 0** at -2/turn when no battles have occurred for 3+ turns. Represents fading military momentum — a victory from 10 turns ago carries less diplomatic weight than a fresh one. Decay applies only to the battle component; territory score, capital score, decisive battle bonuses, and any future ticking score do not decay.

**Implementation:** `calculate_war_score(nation_a, nation_b, world)` in `diplomacy.py`. Called during `advance_turn()` for all active wars. Stored in `world.war_scores`. `apply_war_score_decay()` prunes battle records older than 10 turns and recomputes active war scores; it must not subtract decay from the stored total.

### 6f. Acceptance Formula Player Feedback (DD4)

When a proposal succeeds or fails, the player needs to know WHY. Every proposal response includes a natural-language hint mapping the largest formula component to actionable feedback. This is the diplomatic equivalent of Berthier's battle report observations.

**Response feedback by outcome:**
- **REJECT responses include:** "Talleyrand reports the key obstacle was [largest negative component]."
- **COUNTER_OFFER responses include:** "The sticking point appears to be [second-largest negative component]."
- **ACCEPT responses include:** "The decisive factor was [largest positive component]." (reinforces what worked)

**Component-to-natural-language mapping:**

| Component | Negative Phrasing | Positive Phrasing |
|---|---|---|
| relation_modifier | "deep-seated hostility" | "goodwill between our nations" |
| war_score_modifier | "our military position is weak" | "our military dominance" |
| war_weariness | "the war is still fresh" | "exhaustion from prolonged war" |
| stalemate_duration | "the enemy still expects movement" | "stalemate fatigue" |
| hegemony_target_mod | "balance-of-power resistance" | "limited bloc opposition" |
| bilateral_betrayal_mod | "remembered betrayal" | "a clean bilateral record" |
| grievance_modifier | "durable grievances" | "no active grievance" |
| composite_floor | "stacked political resistance" | "political penalties are bounded" |
| deal_balance | "insufficient concessions" | "generous terms" |
| personality_modifier | "personal opposition from their diplomat" | "diplomatic rapport" |
| diplomat_skill_bonus | "their diplomat outmaneuvered us" | "Talleyrand's superior skill" |
| military_supremacy | "no decisive battlefield leverage" | "military supremacy" |
| battlefield_diplomacy | "limited battlefield pressure" | "battlefield pressure" |
| military_pressure | "weak coercive position" | "military pressure" |
| special_desire_bonus | "terms ignore their core interests" | "terms answer their core interests" |
| harshness_penalty | "terms are too harsh" | "terms avoid punitive excess" |
| harshness_bonus | "resentment from prior harsh treaties" | "no prior harshness resentment" |
| reliability_modifier | "our diplomatic reputation is poor" | "our diplomatic reputation helps" |
| ultimatum_bonus | "the ultimatum lacks force" | "credible ultimatum pressure" |
| base_disposition | "fundamental resistance to this type of agreement" | "natural willingness to negotiate" |

**Implementation:**
```python
def get_formula_feedback(components, outcome):
    """Return natural-language feedback for the largest contributor."""
    trackable = {k: v for k, v in components.items() if k in NEGATIVE_PHRASING}
    if outcome == "REJECT":
        # Find largest negative component
        worst = min(trackable.items(), key=lambda x: x[1])
        return NEGATIVE_PHRASING[worst[0]]
    elif outcome == "ACCEPT":
        # Find largest positive component
        best = max(trackable.items(), key=lambda x: x[1])
        return POSITIVE_PHRASING[best[0]]
    else:  # COUNTER_OFFER
        sorted_neg = sorted(trackable.items(), key=lambda x: x[1])
        return NEGATIVE_PHRASING[sorted_neg[1][0]] if len(sorted_neg) > 1 else NEGATIVE_PHRASING[sorted_neg[0][0]]
```

**Mock mode:** Template strings keyed to the component name. No LLM needed.
**LLM mode:** Components passed as context, LLM generates a 1-2 sentence Talleyrand-flavored assessment.

---

## §7. Treaty System

### 7a. Treaty Clause Types

| Clause | Direction | Mechanical Effect | Notes |
|--------|-----------|-------------------|-------|
| **Gold lump sum** | Either | One-time gold transfer | Paid on treaty ratification |
| **Gold/turn** | Either | Recurring payment each turn | Checked at income phase |
| **Manpower/turn (infantry)** | Either | Recurring recruitment commitment (2000 infantry/turn) | Per-turn drain on manpower pool. Breakable via treaty-break. |
| **Manpower (infantry)** | Either | One-time troop transfer to infantry pool | Specified amount |
| **Cavalry for artillery** | Either | Unit type swap — cavalry pool → artillery pool | Historically common (nations had different strengths) |
| **Artillery for cavalry** | Either | Reverse unit swap — artillery pool → cavalry pool | Austria had great cavalry, France great artillery |
| **Gold for manpower** | Either | Buy recruits from ally (gold → infantry/cav/art pool) | Rate: 200g per 5000 infantry, 300g per 2500 cavalry, 400g per 1500 artillery. Deal sweetener: use manpower value only (gold cost is implicit). |
| **Manpower for gold** | Either | Sell recruits for treasury (pool → gold) | Reverse of above. Deal sweetener: use gold value (1 per 200g received). |
| **AP/turn** | Either | Lose/gain AP each turn | WAR REPARATION TIER when demanded (§7c). Can also be OFFERED as a sweetener (+18 per AP/turn, most valuable). |
| **Territory** | Either | Cede specific regions | Controller changes, stability drops to 50 |
| **Open borders** | Mutual | Movement through territory | Cannot station troops (must keep moving) |
| **Military access** | One-way | Their troops can enter your territory | Stronger than open borders |
| **Continental System** | France→target | Target closes ports to Britain | See §5d |
| **Protection guarantee** | One-way | Guarantor enters WAR if target is attacked | |

**Vassal territory in treaties:** Ceding vassal territory in a peace treaty depends on autonomy level:
- **PUPPET/SATELLITE:** Allowed — the lord controls their territory. Loyalty penalty: -20 per region ceded. Morning Dispatch: "Saxony protests the cession of Dresden — loyalty has dropped significantly."
- **AUTONOMOUS:** Blocked — autonomous vassals have independent territory that cannot be traded without their consent (which they won't give). Talleyrand: "Sire, Saxony governs its own territory. We cannot cede what we do not control."

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
The formula uses a `harshness` score derived from clause balance. **Clause values defined in §6c.1 (Harshness Value Table).**
```
harshness = (value_demanded - value_offered) / total_deal_value
  0.0 = perfectly balanced
  1.0 = all take, no give
  -1.0 = all give, no take (extremely generous)

Dove targets get +10 acceptance for harshness < 0.3 (generous)
Hawk targets get +5 acceptance for harshness > 0.6 (respects strength)
Schemer targets get +5 for any harshness (respects boldness — see §6b personality table)
```

### 7c. AP Treaty Clauses — War Reparation Tier

AP is the most valuable resource in the game. Treaty AP reflects that:

**Demanding AP:** Requires overwhelming war score (> 80) OR conquest-vassalage. You only get AP tribute from a nation you've utterly defeated. Prussia isn't giving you command capacity unless you're standing in Berlin.

**Offering AP:** Almost never rational. Only makes sense as desperate war reparations to stop total conquest. "We'll cripple our command to buy survival."

**Cap:** 1 AP/turn max per treaty. Even in total defeat, more than 1 AP/turn would be game-breaking.

**Acceptance formula:** Massive negative modifier. AI nations treat AP demands as extreme:
```
AP demand penalty in acceptance formula: -25 per AP/turn demanded
(vs the +18 sweetener for OFFERING AP — asymmetric by design)

Only achievable with: max war score + territory held + other concessions
```

**Talleyrand reaction:** Talleyrand ALWAYS objects (STRONG concern) to AP demands unless war score > 80. "Sire, demanding their command capacity will ensure eternal enmity. No nation forgets such humiliation."

**AP as sabotage vector:** Talleyrand might offer more AP than authorized in a deal where France is PAYING AP ("I offered them 1 AP/turn instead of the gold you suggested — they were far more amenable"). This is his most dangerous sabotage — it directly cripples French command capacity.

This makes AP in treaties a late-game dominance move, not a routine negotiation tool. Historically accurate — Napoleon demanded troops and resources from vassals, but demanding sovereignty is how coalitions are born.

### 7d. Treaty Duration & Breaking

- Treaties have no expiration by default (permanent until broken or superseded)
- Armistice: minimum 5 turns, then either side can end
- Breaking a treaty:
  - Costs 1 DP
  - Relation with target: -30
  - Relation with all nations: -10 (treaty-breaker reputation)
  - Threat level: +15
  - Casus belli granted to victim
  - If breaking alliance/defensive alliance: more severe (-40 relation, +25 threat)
  - **Post-break state (E11):** Breaking a treaty drops **two levels** below the broken treaty (2-level drop per design). Breaking ALLIANCE → NON_AGGRESSION. Breaking DEFENSIVE_ALLIANCE → OPEN_BORDERS. Breaking NON_AGGRESSION → PEACE. Breaking PEACE → WAR. Breaking ARMISTICE → WAR. This creates meaningful consequences — breaking a high-level treaty loses significant diplomatic progress.

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
# VASSAL: No bilateral trade income — replaced by tribute (§8c).
# Vassal tribute is a separate income stream, not trade.
```

**Treaty clause gold/turn** is applied in the same income phase, immediately after trade income. Gold lump sums are applied on treaty ratification turn only.

**Display:** Trade income appears in the Strategic Ledger Economy tab as a separate line item: "Trade income: +150 (Prussia NON_AGGRESSION, Austria PEACE)".

### 7f. Diplomatic Processing Order in advance_turn()

All diplomatic per-turn processing runs WITHIN `advance_turn()` in this strict order:

```
1.  DP regeneration — calculate new DP from formula (§4a)
2.  Mission DP deduction — deduct active mission costs (§2e)
    (If DP insufficient after regeneration, mission pauses — EC-S)
3.  Mission effects — apply relation changes, intel collection, etc.
4.  War objective ticking + score recalculation — accumulate War Purpose ticking, then recalculate stored war scores from territory + quiet-turn-decayed battles + decisive + capital + ticking (§6e; WAR_PURPOSE_SCORE_SEMANTICS_SPEC §7)
5.  Defection cascade check — if war score < -30, check vassals (§8d)
6.  Vassal loyalty processing — autonomy drift, garrison, passive modifiers (§8b)
7.  Vassal rebellion check — loyalty = 0 → rebellion fires (§8d)
8.  Armistice expiration — minimum 5 turns reached (§5b.2)
9.  Cooldown decrements — ai_proposal_cooldowns, player_proposal_cooldowns,
    armistice_cooldowns, vassal investment cooldowns (all -1/turn)
9a. War exhaustion update — +8/turn at war with France, -5/turn at peace (COALITION_SPEC §10a)
9b. Threat accumulation — apply battle/capture/control sources from this turn (COALITION_SPEC §2a)
9c. Threat decay — apply the canonical peace-count decay formula from COALITION_SPEC §2b
9d. Coalition check — brewing countdown, formation threshold, instant ≥80 (COALITION_SPEC §3c)
10. Income phase — region income, trade income (§7e), treaty clause gold/turn
11. Treaty obligation checks — gold/turn defaults (EC-MM)
12. Continental System participation check (§5d)
13. Automatic downgrade check — relations 30+ below threshold for 5 turns (§5b.1)
14. Proactive suggestion evaluation — triggers for Morning Dispatch (DESIGN §5d)
```

This order ensures: DP is available before mission deduction, war score is fresh before cascade checks, loyalty is processed before rebellion, threat is fresh before coalition checks (decay applies BEFORE threshold — see COALITION_SPEC §3c), and income is calculated with current diplomatic states.

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
  Garrison strength bonus:                        +min(garrison_troops // 5000, 3)
  Gold investment treaty (gold/turn TO vassal):   +1 per 100 gold/turn
  Shared enemy (both at war with same nation):    +2 (common cause)
  Lord winning wars:                              +1 per battle won this turn (max +3)
  Lord losing wars:                               -2 per battle lost this turn (max -6)
  Relation with lord:                             nation_relation(vassal, lord) / 20 (can be negative)
    (Uses nation_relations between vassal nation and lord nation. Vassal nations
     retain their nation_relations through vassalage — see §12 EC-K.1.)

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

**Tribute calculation rounding (Golden Rule #2):** `tribute = int(vassal_income * tribute_rate)`. Example: Saxony income 250, SATELLITE rate 0.75 → `int(250 * 0.75)` = `int(187.5)` = 187. Use `int()` truncation (not `round()`), consistent with gold calculations elsewhere.

**Autonomy can be changed** by the lord (1 DP cost, takes effect next turn). Upgrading autonomy (PUPPET→SATELLITE) gives +10 loyalty bonus. Downgrading (SATELLITE→PUPPET) gives -15 loyalty penalty. Choose wisely.

**Vassal nation relations persist:** A vassalized nation retains its `nation_relations` entries. These affect vassal loyalty (§8b "Relation with lord") and enemy courting effectiveness (§8e). France conquering Saxony's ally could worsen Saxony-France relations → loyalty drop. This creates a rich interconnection between diplomacy and vassal management.

### 8d. Vassal Rebellion

When loyalty hits 0:
- Vassal declares independence (returns to WAR with former lord)
- Vassal army turns hostile — all vassal marshals become enemies
- Threat level: -10 (other nations see France weakened)
- Relation with former vassal: -50
- **Cascade risk:** If lord has other vassals, they each get -10 loyalty ("if Saxony can break free...")

**Cascade tipping point (DD8 — Leipzig moment):** When France's war score drops below -30 against ANY enemy, all vassals with loyalty < 50 make a simultaneous loyalty check. Each vassal rolls: if `random.random() < (50 - loyalty) / 100`, the vassal rebels immediately regardless of current loyalty (as long as loyalty < 50). This creates a dramatic "the empire crumbles" moment rather than slow individual rebellions. Historically, Bavaria's defection at Ried triggered a cascade — Wurttemberg, Saxony, and others defected at Leipzig within days.
- The tipping point fires at MOST once per war (tracked per war pair). A second war score drop below -30 in the same war does not re-trigger.
- Vassals with loyalty >= 50 are immune to the cascade check (they're loyal enough to hold).
- The cascade check runs during `advance_turn()`, after war score recalculation, before normal loyalty processing.

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

### 8f. Vassal Carving from Conquered Territory (DD1)

After conquering enemy regions, France can **carve new vassal entities** from that territory — turning conquered regions into new minor vassal states. This mirrors Napoleon's creation of the Confederation of the Rhine, Kingdom of Westphalia, and Duchy of Warsaw.

**Requirements:**
- Hold the target region(s)
- War score > 40 against the original owner
- 2 DP cost (diplomatic action — creating a new political entity)
- Region must be a non-capital enemy region (cannot carve from capitals — those are for full-nation vassalization)

**Commands:**
```
"Talleyrand, carve a vassal from Rhineland"              → Auto-named "Duchy of Rhineland"
"Talleyrand, create vassal from Rhineland, Bavaria"       → Multi-region carved vassal
"Talleyrand, rename Duchy of Rhineland to Confederation"  → Player rename (polish feature)
```

**What a carved vassal IS:**
- A territory + tribute source + buffer zone + rebellion risk
- Gets: a name (auto-generated "Duchy of [Region]" or player-chosen), controlled regions, autonomy level (defaults to SATELLITE), starting loyalty based on conquest conditions
- Starting loyalty: 15 + (5 × turns held before carving). Longer occupation → more stable.
  Minimum case: carving immediately after conquest (0 turns held) → loyalty 15. Very
  unstable — rebellion in ~4-8 turns without garrison+investment. Intentional: freshly
  conquered territory is inherently rebellious. Hold the region for 3-5 turns before carving
  for a more stable vassal (30-40 starting loyalty).
- Receives tribute obligations per §8c (75% income at SATELLITE)

**What a carved vassal is NOT:**
- NOT a full nation — no diplomat, no DP, no independent treaty capability
- NOT represented in the acceptance formula as a negotiating party
- Does NOT get its own marshals initially (garrison units only — controlled by nearest French marshal or by AI as detachment)
- Does NOT contribute to the diplomacy UI beyond a line in the Diplomatic Ledger Vassal tab

**Scaling by nation size (user requirement — can't fully vassalize huge nations):**
- Small nations (1-2 regions, e.g., Saxony): Can be vassalized whole via treaty or conquest. Standard paths.
- Medium nations (3-4 regions, e.g., Austria): Can be vassalized whole via conquest (hold capital + war score > 60), but carving is cheaper. Carving 1-2 regions costs 2 DP each. Full vassalization costs 3 DP + overwhelming war score.
- Large nations (5+ regions, e.g., theoretical expanded Prussia): Cannot be fully vassalized in one action. Must either: (a) carve regions piecemeal (2 DP per carve), or (b) reduce them to 2-3 regions via carving THEN vassalize the rump state. This prevents "conquer Berlin → vassalize all of Prussia instantly" exploits.

**Granting carved regions to existing vassals:**
- "Talleyrand, grant Rhineland to Saxony" — transfers carved vassal territory to an existing vassal nation.
- The carved vassal entity dissolves; its regions merge into the recipient's territory.
- Recipient vassal: +10 loyalty ("France rewards faithful service")
- Recipient vassal: inherits the region's income
- Cost: 1 DP
- Requirement: recipient must be a current vassal of France

**Contiguity break on partial region loss:** If region loss breaks contiguity (e.g., carved vassal has regions A-B-C, enemy retakes B), the carved vassal retains the largest contiguous chunk. Disconnected regions revert to the original owner's control (contested status). Morning Dispatch: "The Duchy of Rhineland has been split — [region] has been lost to [nation] control." If multiple chunks are equal size, retain the chunk containing the region with the highest income.

**What happens when carved regions are liberated?**
- If the original owner (or any enemy) captures a carved vassal's region: the carved vassal loses that region.
- If ALL regions of a carved vassal are liberated: the carved vassal entity dissolves. Morning Dispatch: "The Duchy of Rhineland has ceased to exist."
- The original owner regains the region. Their war score improves.
- Liberation does NOT automatically grant the region back to the original nation in peace talks — it must be negotiated or held militarily.

**What if the parent nation demands carved regions back in peace talks?**
- Territory demands in peace proposals (§7a) can target carved vassal regions.
- "Prussia demands: return of Rhineland" → acceptance formula applies normally.
- If France accepts: carved vassal loses the region (or dissolves if it was the last region).
- If carved vassal region is demanded AND France's war score is negative: the demand gets +5 bonus ("returning stolen territory").
- Carved regions ceded in peace return to the original nation's direct control (not as a new vassal).

**Interaction with existing vassal loyalty:**
- Carving from a nation you're at war with: +5 threat level per carve (expanding empire).
- Existing vassals: no direct loyalty impact from carving enemy territory. But cascade applies if carved vassals rebel (§8d).
- Carved vassals ARE subject to enemy courting (§8e) — enemies can destabilize your creations.

**Serialization:**
```python
# Carved vassals are stored in the SAME self.vassals dict as nation-vassals,
# distinguished by "path": "carved". This is the SINGLE source of truth for
# all vassals (Golden Rule #3 pattern — one dict).
# Key: carved vassal name (e.g., "Duchy of Rhineland")
# Value: {"lord": "France", "loyalty": int, "autonomy": 1, # SATELLITE default
#   "investment_cooldown": int, "path": "carved",
#   "carved_from": "Prussia",  # Original nation
#   "regions": ["Rhineland"],  # Controlled regions
#   "created_turn": int}
#
# Nation-vassals have "path": "treaty" or "path": "conquest".
# Use: [v for v in vassals.values() if v["path"] == "carved"] to filter carved vassals.
```

**Edge cases:**
- Carving the same region twice: blocked ("This territory is already administered as the Duchy of Rhineland").
- Carving while at peace with the original owner: blocked (requires war score > 40, which implies active war or recent war).
- Carved vassal with 0 loyalty: rebellion — regions become contested (no nation controls them until occupied). Unlike full vassals, carved vassals don't "return to their nation" on rebellion — they become neutral/contested.
- Multiple carved vassals rebelling simultaneously: each processed independently per §8d cascade rules.

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
  Suppressed proposals are NOT queued — AI re-evaluates conditions each turn.
  If conditions still hold next turn, the AI may generate the same proposal again.

Queue size limit: maximum 3 proposals in diplomatic_queue at any time.
  If a 4th would be queued, the lowest-priority proposal is dropped.
  Proposals expire after 3 turns in the queue (conditions may have changed).

Queue visible in Diplomatic Ledger Tab 4:
  "Pending envoys: Austria (alliance proposal, arrives next turn)"
```

**Blocking dialogue priority — same-turn conflicts:** When multiple blocking diplomatic events occur on the same turn (e.g., AI proposal + sabotage discovery), only one can occupy `pending_diplomatic_dialogue` at a time. Resolution order:
1. AI proposals are delivered first (during AI phase, before Morning Dispatch).
2. Sabotage discovery is checked during Morning Dispatch building (after AI proposals).
3. Whichever fires first sets `pending_diplomatic_dialogue`. The other is queued in `diplomatic_queue` and delivered on the next turn after the first is resolved.
4. If the player resolves the first blocking dialogue mid-turn, the queued event fires immediately.

**Talleyrand's assessment:** Every incoming AI proposal includes a 1-2 sentence assessment from Talleyrand. This is flavor text shaped by his personality (Schemer — strategic calculation). In mock mode, keyed to proposal type + war score + relation. Talleyrand might recommend accepting a bad deal if it serves his long-term vision, or rejecting a good deal if it makes France look weak.

**Enemy diplomat personality asymmetry (design note):** Talleyrand can sabotage AGAINST the player (defiance alters outgoing proposals). Enemy Schemer diplomats (Metternich) can only sabotage against their OWN nation's proposals — modifying AI proposals to be softer than the AI decision tree intended. There is no mechanism for enemy diplomats to sabotage proposals RECEIVED from France. This is intentional: the player doesn't control enemy internal politics, and making enemy sabotage affect incoming proposals would create invisible unfairness. The asymmetry creates distinct gameplay: the player manages Talleyrand's loyalty (personal challenge), while enemy Schemer behavior is observable but not controllable (strategic intel). See DESIGN §10e for how this manifests.

**AI proposal triggers (decision tree):**

| Condition | Proposal | Priority |
|-----------|----------|----------|
| Losing badly (war score < -40) | Armistice/peace | P1 (survival) |
| War stalemate (war score -10 to +10 for 5+ turns, R149: raised from <= 0 to <= 10) | Armistice | P2 |
| Threat level > 60 AND not allied with France | Seek alliance with other anti-France nations | P3 |
| Relation > +30 AND at peace | Propose non-aggression/alliance upgrade | P4 |
| Economy struggling (gold < 200 and declining) | Trade deal / tribute offer | P5 |
| Vassal loyalty < 40 (if courting) | Court vassal | P6 |
| Opportunism: enemy distracted by another war | Propose terms that favor them | P7 |

### 9b. AI Response to Player Proposals

Uses the same acceptance formula (§6). The AI doesn't cheat — it evaluates proposals identically to how the player's proposals would be evaluated in reverse.

**Counter-offer generation algorithm (M3 — deterministic for Building Blocks):**

When acceptance_score is 30-49 (COUNTER_OFFER range), the AI generates a modified proposal using this algorithm:

```
Step 1: Calculate per-clause acceptance impact using deal_sweetener values (§6b).
Step 2: Identify the single clause with the largest NEGATIVE impact on the AI's acceptance.
Step 3: Remove that clause from the proposal.
Step 4: Recalculate. If still in counter-offer range (30-49), add the clause with the
        lowest deal_sweetener cost (from §6b values) that the AI desires (from the
        per-nation desire table below). "Cheapest" = smallest positive acceptance impact.
Step 5: If modified proposal score >= 50: present as counter-offer.
        If modified proposal score still < 30: REJECT instead (counter-offer impossible).

Per-nation desire table (what each nation wants in counter-offers):
  Prussia: Territory (Saxony > any other), Gold lump sum
  Austria: Open borders, Protection guarantee, Gold/turn
  Britain: Continental System lifted, Gold lump sum, Territory (continental holdings)
  Saxony:  Protection guarantee, Gold/turn, Survival (no territory demands)
```

Counter-offers are free for the AI (same as player — responding costs 0 DP). The algorithm is fully deterministic — mock mode produces identical counter-offers to LLM mode.

### 9c. AI-AI Diplomacy

> **DEFERRED TO SESSION 8 (Ledger UI + Polish).** AI-AI diplomacy is not part of the Walking Skeleton. The core experience works without it — nations only interact with the player in Sessions 1-6. AI-AI diplomacy adds immersion but is not mechanically required. The system described below is the target design for Session 8.
>
> **Impact of deferral:** The world feels less alive without AI-AI diplomacy. Alliance shifts between AI nations won't happen dynamically. The player won't see "Britain and Austria have signed a defensive alliance" events. This is acceptable for initial playtesting — the player's own diplomatic choices are the priority.

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

**AI-AI acceptance:** Same formula, both sides. Metternich's Schemer personality and high skill (9) gives Austria an advantage in AI-AI negotiations — he "course-corrects" Austrian proposals toward strategic advantage, just as Talleyrand does for France. Castlereagh's Hawk personality makes British alliance proposals slightly harder to reject (aura of strength).

**British Subsidy Mechanic (DD8 — historical):** Britain historically financed coalitions with subsidies of 1.25M pounds per 100,000 troops/year. As an AI diplomatic behavior, Britain spends gold to improve relations with coalition partners:
- When Britain is at WAR with France AND has gold > 500: Britain allocates 200 gold/turn to the coalition partner with the lowest relation to Britain (minimum relation > -20).
- Effect: +5 relation/turn with that partner (cheaper than a full IMPROVE_RELATIONS mission because Britain's wealth IS its diplomatic tool).
- This is a passive AI behavior, not a proposal — no DP cost, no acceptance check. It represents Britain's structural economic advantage.
- Player can counter by: winning militarily (reduces British continental holdings → less gold), Continental System (reduces naval income), or diplomatic outreach to the subsidy target.

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
│     Metternich (Schemer)    Skill: 9    │
│     Regions: 4              Army: 60k   │
│     Treaties: Def.Alliance (Brit, Prus) │
│                                         │
│ [4] SAXONY    FRENCH_PEACE   Rel: +40   │
│     Einsiedel (Dove)        Skill: 4    │
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
| **Authority** | Low authority → Talleyrand defiance chance increases. Authority >= 60 → +1 DP. |
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

### 10d. Dispatch Event Types (M1)

Following the JEALOUSY_SPEC pattern, all diplomatic dispatch events are enumerated:

| Event Type | When | Template | Priority |
|---|---|---|---|
| `diplomatic_proposal_sent` | Talleyrand departs with proposal | "Talleyrand has departed for the {nation} court." | LOW |
| `diplomatic_proposal_returned` | Talleyrand returns with response | "Talleyrand returns from {nation} with a response." | HIGH |
| `diplomatic_sabotage_discovered` | Sabotage detected (§3c) | "Talleyrand altered your proposal to {nation}. He {change_description}." | HIGH |
| `diplomatic_treaty_signed` | Treaty ratified | "{nation_a} and {nation_b} have signed a {treaty_type}." | MEDIUM |
| `diplomatic_treaty_broken` | Treaty broken | "{nation} has broken the {treaty_type}." | HIGH |
| `diplomatic_war_declared` | War declaration | "{nation} has declared war on {target}." | HIGH |
| `diplomatic_vassal_unrest` | Vassal loyalty < 40 | "Talleyrand reports unrest in {nation}." | MEDIUM |
| `diplomatic_vassal_rebellion_imminent` | Vassal loyalty < 10 | "{nation} is on the verge of rebellion!" | HIGH |
| `diplomatic_vassal_rebellion` | Vassal loyalty = 0 | "{nation} has rebelled!" | HIGH |
| `diplomatic_ai_proposal` | AI sends proposal to player | "A {nation} envoy has arrived with a proposal." | HIGH |
| `diplomatic_mission_progress` | Ongoing mission tick | "Talleyrand's efforts in {nation} continue. Relations now at {value}." | LOW |
| `diplomatic_mission_paused` | DP insufficient for mission | "Talleyrand's diplomatic efforts curtailed — insufficient resources." | MEDIUM |
| `diplomatic_mission_cancelled` | Mission auto-cancelled (3+ paused turns) | "Talleyrand's diplomatic efforts in {nation} have collapsed." | HIGH |
| `diplomatic_feasibility_report` | Feasibility request result (§2g) | "Talleyrand assesses: {difficulty_tier}. {hint}." | LOW |
| `diplomatic_alliance_cascade` | Alliance triggers war entry | "{nation} enters the war via alliance with {ally}." | HIGH |
| `diplomatic_vassal_courting` | Enemy courting detected (60% chance) | "Talleyrand reports {enemy} agents in {vassal_capital}." | MEDIUM |
| `diplomatic_continental_system` | Nation joins/leaves Continental System | "{nation} has {joined/withdrawn from} the Continental System." | MEDIUM |
| `diplomatic_carved_vassal_created` | Vassal carved from enemy territory | "The {carved_name} has been established under French protection." | MEDIUM |
| `diplomatic_carved_vassal_dissolved` | Carved vassal lost all regions | "The {carved_name} has ceased to exist." | HIGH |
| `diplomatic_defection_cascade` | Tipping point triggered (DD8-2) | "The empire trembles — multiple vassals are wavering!" | HIGH |

Events are added to the dispatch whitelist in `dispatch.py`. Fog-filtered per existing rules (§11).

### 10e. Notification Templates (M2)

Following the existing notification system pattern (V2b), all diplomatic notification types with priority levels:

| Notification Type | Priority | Template | Dismiss |
|---|---|---|---|
| `DIPLOMATIC_PROPOSAL` | HIGH | "{nation} envoy: {proposal_type}" | On response |
| `TREATY_SIGNED` | MEDIUM | "Treaty with {nation}: {treaty_type}" | Manual |
| `TREATY_BROKEN` | HIGH | "{nation} broke {treaty_type}" | Manual |
| `SABOTAGE_DISCOVERED` | HIGH | "Diplomatic discrepancy detected" | Manual |
| `VASSAL_REBELLION_IMMINENT` | HIGH | "{nation}: IMMINENT REBELLION" | Manual |
| `VASSAL_REBELLION` | HIGH | "{nation} has broken free!" | Auto (5 turns) |
| `ALLIANCE_CASCADE_WAR` | HIGH | "{nation} enters war via alliance" | Auto (3 turns) |
| `WAR_DECLARED` | HIGH | "{nation} declares war" | Auto (3 turns) |
| `VASSAL_COURTING_DETECTED` | MEDIUM | "{enemy} agents in {vassal}" | Manual |
| `DP_INSUFFICIENT` | MEDIUM | "Diplomatic resources low" | Auto (1 turn) |
| `DEFECTION_CASCADE` | HIGH | "Multiple vassals wavering!" | Manual |

Priority determines display order and persistence. HIGH notifications persist until dismissed or auto-expire. MEDIUM notifications are shown once in the notification bar.

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

**EC-K.1: Vassal Marshal Assimilation (M4).** When Saxony becomes a French vassal, Reynier (and any other vassal nation marshals at PUPPET/SATELLITE level) transitions to player control. Specific mechanics:
- **Trust:** Starts at 40 (reluctant service — below default 60, reflecting forced allegiance).
- **Dict membership:** Joins `world.marshals` dict immediately (Golden Rule #3 — all marshals in ONE dict).
- **Relationships:** Existing relationships with Saxony entities preserved. Relationships with all French marshals set to Professional (0) — no history of working together. **Intentional design:** Assimilated vassal marshals start with a clean diplomatic slate. Previous battle-earned hostilities are forgiven — vassalage represents a political fresh start, not a continuation of wartime grudges.
- **Personality:** Unchanged (Reynier stays Literal).
- **Biography:** Updated to note vassalage: "Now serving France as Saxony's contribution to the alliance."
- **Commands:** Player can command Reynier identically to French marshals ("Reynier, attack Rhineland").
- **Objections:** Use Reynier's personality for objection evaluation (Literal = rarely objects).
- **Can attack former allies:** Yes. Loyalty is mechanical (follows orders), not emotional.
- **AUTONOMOUS vassals:** Their marshals remain AI-controlled. Player cannot command them directly. They act as autonomous allies targeting the lord's enemies.
- **Serialization:** Marshal's `nation` field changes to vassal nation name (still "Saxony") but `is_player_controlled` flag set to True. Survives save/load.

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

**EC-Z: Armistice expires while proposal in transit.** If an armistice expires (minimum 5 turns reached) while Talleyrand is carrying a peace proposal, the proposal still delivers normally. The war resumes at the start of the turn, but Talleyrand's proposal can produce instant peace if accepted. Race condition resolved: proposal delivery → response popup → then war resumes if rejected.

**EC-AA: Decisive battle bonus on multi-nation war.** If France is at war with both Prussia and Austria, and a battle involves Austrian/Prussian coalition forces, the decisive battle bonus applies to each war score independently. A decisive victory over Archduke Charles at Vienna counts for France-Austria war score but NOT France-Prussia war score (unless Prussian forces participated — checked via battle participants).

**EC-BB: Diplomatic state with no matching treaty.** If an alliance exists but no formal treaty is tracked (e.g., starting alliances from §1e), the system creates implicit treaty records during initialization. Every diplomatic state above PEACE has an implicit treaty. Breaking the state breaks the implicit treaty with all associated penalties.

**EC-CC: Multiple vassals rebelling same turn.** Each vassal's loyalty is checked independently. Multiple can rebel simultaneously. Each rebellion's cascade penalty (-10 to other vassals) is applied cumulatively. If 2 of 3 vassals rebel, the third takes -20 cascade, potentially triggering a triple rebellion. Processing order: alphabetical by vassal name (deterministic).

**EC-DD: Counter-offer modifies territory clause.** When AI generates a counter-offer, it can modify territory clauses (e.g., "we'll cede Saxony but not Berlin"). The player sees both the original proposal and the counter-proposal side by side. Territory modifications are evaluated as clause-level diffs — each changed clause shows old vs new values.

**EC-EE: Invest in vassal on cooldown.** If the 3-turn investment cooldown hasn't expired, the action is blocked with message: "Talleyrand reports our recent investment in Saxony is still bearing fruit. Further investment would be wasteful at this time." DP is NOT deducted for blocked actions.

**EC-FF: War score with no battles (pure territory war).** War score can be non-zero purely from territory control. If France occupies all Prussian regions without winning a battle (e.g., Prussia retreated), war score = territory score only. This is sufficient for peace proposals but makes vassalage difficult (no decisive battle bonus).

**EC-GG: Alliance cascade on war declaration with vassal.** If France vassalizes Saxony and then Prussia (allied with Britain) declares war on Saxony, France enters war with Prussia (lord defends vassal). If France was at peace with Prussia, this changes France-Prussia state to WAR. Britain's alliance with Prussia does NOT automatically cascade unless Britain has a DEFENSIVE_ALLIANCE with Prussia specifically against France.

**EC-HH: Diplomatic state downgrade during armistice.** You cannot downgrade from ARMISTICE — it's already one step above WAR. The only transitions from ARMISTICE are: → PEACE (upgrade, negotiate treaty) or → WAR (armistice expires/broken). No downgrade path from ARMISTICE.

**EC-II: Player cedes Paris in a treaty (Audit EC-1).** Allow with EXTREME Talleyrand objection (Schemer personality — "Sire, this is MADNESS"). If ceded: -1 DP permanent (capital loss penalty from §4a), Talleyrand skill effectively -2 until Paris is recaptured (reduced effectiveness without a seat of power). Talleyrand relocates to nearest French-controlled city. All French marshals: trust -5 ("the Emperor gave away our capital").

**EC-JJ: Cross-proposal race condition (Audit EC-2).** If France sends a proposal to Prussia while Prussia simultaneously sends a proposal to France (both in transit same turn): first-to-resolve wins. Processing order: player proposals resolve first (during Morning Dispatch), then AI proposals. If both are from AI nations (AI-AI), alphabetical by proposing nation. The second proposal is auto-cancelled with message: "Negotiations are already underway — your envoy returns."

**EC-KK: Breaking armistice penalties (Audit EC-4).** Treat as treaty-break (§7d) with additional "armistice violator" penalty: -30 relation with target (standard), -10 all nations (standard), PLUS -20 additional relation with all nations ("breaking a ceasefire is worse than breaking a trade deal"). Threat +15 (standard) + +10 additional. Total: -50 target, -30 all, +25 threat. Morning Dispatch: "The armistice has been violated. The courts of Europe condemn this act."

**EC-LL: French treaties apply to vassal territory (Audit EC-5).** Yes — France's OPEN_BORDERS with Austria applies to Saxony (French vassal) territory. But PUPPET/SATELLITE vassals cannot independently grant military access. AUTONOMOUS vassals can grant access independently (free diplomacy per §8c). Vassal territory is treated as French-controlled for treaty purposes unless the vassal is AUTONOMOUS with independent treaty rights.

**EC-MM: Nation goes bankrupt from treaty obligations (Audit EC-6).** Gold floor at 0 — nations cannot go negative. If a nation cannot pay a gold/turn clause: the clause defaults (payment stops), relation with recipient -5 per defaulted turn, treaty clause auto-suspended after 3 consecutive defaults. Morning Dispatch: "{nation} has defaulted on treaty payments." The defaulting nation can resume payments if gold recovers above the clause amount.

**EC-NN: Mission target declares war on France (Audit EC-7).** Active diplomatic mission targeting that nation auto-cancels immediately. DP investment lost (sunk cost). Morning Dispatch: "Talleyrand's courtship of {nation} is moot — they have declared war." Talleyrand returns to IDLE state.

**EC-OO: Decisive battle records after peace and re-war (Audit EC-8).** Records persist in `world.decisive_battles` for Diplomatic Ledger display (historical record). But per-war decisive_bonus counter resets to 0 for war score calculation (per EC-W: fresh war = fresh war score). Old decisive battles are visible in the ledger but don't affect the new war's diplomacy.

**EC-PP: Continental System member conquered by Britain (Audit EC-10).** Conquered nation exits Continental System automatically. `continental_system_members` list updated when nation sovereignty changes (during territory processing in `advance_turn()`). Morning Dispatch: "{nation} has been removed from the Continental System following British occupation."

**EC-QQ: Talleyrand sabotage produces better outcome (Audit EC-11).** "Successful sabotage" — player wanted harsh terms, Talleyrand softened, target accepted. Discovery confrontation still fires (§3c). Player choice: Confront (trust -10, authority +5, "I didn't want peace on THOSE terms") or Overlook (trust +3, sabotage validated — "perhaps Talleyrand was right"). Key insight: the player may DISAGREE with a good outcome if it wasn't their intent.

**EC-RR: All vassals deteriorate simultaneously from military losses (Audit EC-12).** Intended behavior. Lord losing wars: -2 loyalty per loss per vassal per turn (§8b). Multiple vassals amplify the consequences of military failure. The cascade risk (§8d) is the price of empire. No mitigation beyond winning battles or investing in vassals.

**EC-SS: DP generation drops below mission cost (Audit EC-13).** When DP generation drops, Morning Dispatch warns on the turn BEFORE the first mission pause: "Talleyrand warns: our diplomatic capacity is declining. Current mission may be interrupted next turn." This gives the player 1 turn to cancel the mission or address the DP shortfall. If they don't act, the mission auto-pauses per EC-S.

**EC-TT: Defensive alliance cascade creates infinite loop (Audit EC-14).** Termination condition: each nation processes alliance cascade ONCE per war declaration. A nation already processed (already at war or already checked this cascade) is skipped. Prevents A→B→C→A loops. Implementation: maintain a `cascade_processed` set during each war declaration event, cleared after the cascade resolves.

**EC-UU: Continental System member's sovereignty changes (Audit EC-15).** Membership is per-sovereign-nation. Conquered regions don't participate (§EC-PP). Vassalized nations: PUPPET/SATELLITE auto-join if lord (France) is running the Continental System. AUTONOMOUS vassals: independent choice — check relation with France > +10 AND relation with Britain < +30 (same criteria as voluntary participation in §5d).

**EC-VV: Vassal carving from non-adjacent territory.** Player can only carve vassals from regions they currently occupy and control. The carved region must be contiguous (if multi-region carve, all regions must be adjacent to each other). Non-contiguous carved vassals are not allowed — creates supply and control problems.

**EC-WW: Carved vassal granted to non-adjacent vassal.** Allowed — the granted regions don't need to be adjacent to the recipient vassal's existing territory. This enables strategic buffer zone creation (granting distant territory to a loyal vassal). The recipient simply gains control of those regions.

---

## §13. New Model Fields

### WorldState fields:

```python
# ═══════ DIPLOMACY SYSTEM (Phase 8) ═══════

# Diplomatic states between nation pairs
# Key: frozenset({nation_a, nation_b}) serialized as "nation_a|nation_b" (alphabetical)
# Value: diplomatic state string
self.diplomatic_states: Dict[str, str] = {}  # Populated from §1e defaults

# Nation relations (-100 to +100, CLAMPED — all modifiers must clamp after applying)
# Same key format as diplomatic_states
# Use: nation_relations[key] = max(-100, min(100, new_value))
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

# Pending diplomatic dialogue (from CONVERSATIONAL_DIPLOMACY_DESIGN §2b).
# All proposal presentation routes through this field.
# Dict or None. Serialization: already primitive-only (str, int, bool, list, dict).
# Commitments follow-up requirement: pending paradox / counter-bargain / join-opportunity
# payloads must preserve reroll identity and originating episode lineage across save/load.
# Canonical context keys for commitments-generated payloads:
# - context.origin_episode_id
# - context.reroll_key
# - context.join_opportunity
# - context.counter_bargain_context (when applicable)
# - context.declaration_transaction_id (when tied to a pending offensive declaration)
# - context.pending_declaration (primitive staged offensive declaration snapshot for that transaction)
# - context.opposition_pair_key (for commitment_paradox follow-ups)
# See CONVERSATIONAL_DIPLOMACY_DESIGN §2b for full schema.
self.pending_diplomatic_dialogue: Optional[Dict] = None

# NOTE: pending_diplomatic_proposal was removed — superseded by the above.
# Raw proposal data lives in proposal_in_transit (outgoing) or
# diplomatic_queue (incoming AI proposals awaiting presentation).

# Proposal in transit (Talleyrand is traveling — resolves next turn)
# {"target_nation": str, "original_proposal": dict, "actual_proposal": dict,
#  "sabotaged": bool, "departure_turn": int}
# CLEAR TIMING (Golden Rule #4): Cleared AFTER the player responds to the
# return popup (accept/reject/renegotiate), not when the popup first displays.
# If renegotiating, a NEW proposal_in_transit is created for the next round.
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

# Threat level (France-specific, CLAMPED 0-100 — cannot go negative)
# Use: threat_level = max(0, min(100, new_value))
self.threat_level: int = 0

# Vassal tracking
# Key: vassal_nation, Value: {"lord": str, "loyalty": int, "autonomy": int,
#   "investment_cooldown": int, "path": "treaty"|"conquest"}
self.vassals: Dict[str, Dict] = {}

# NOTE: Vassal investment cooldowns are tracked per-vassal inside self.vassals
# as the "investment_cooldown" field. No separate dict needed.

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

```python
# DiplomaticRepresentative serialization (m6):
def to_dict(self):
    return {
        "name": self.name,                    # str
        "nation": self.nation,                # str
        "personality": self.personality,        # str: "schemer"|"loyalist"|"hawk"|"dove"
        "skill": self.skill,                   # int: 1-10
        "biography": self.biography,           # str
        "trust": self.trust.to_dict(),         # Trust object serialization
    }

@classmethod
def from_dict(cls, data):
    rep = cls(
        name=data["name"],
        nation=data["nation"],
        personality=data["personality"],
        skill=data.get("skill", 5),
        biography=data.get("biography", ""),
    )
    if "trust" in data:
        rep.trust = Trust.from_dict(data["trust"])
    return rep
```

All fields MUST be added to `to_dict()` and `from_dict()` with `.get()` defaults. Run `test_serialization_enforcement.py` after.

**WorldState getter methods (required by DESIGN §4c slot resolvers):**
```python
def get_war_score(self, nation_a, nation_b) -> int:
    """Return war score for pair. Key is alphabetical. Positive = nation_a winning."""
    key = "|".join(sorted([nation_a, nation_b]))
    return self.war_scores.get(key, 0)

def get_nation_relation(self, nation_a, nation_b) -> int:
    """Return relation between two nations."""
    key = "|".join(sorted([nation_a, nation_b]))
    return self.nation_relations.get(key, 0)

def get_diplomatic_state(self, nation_a, nation_b) -> str:
    """Return diplomatic state between two nations."""
    key = "|".join(sorted([nation_a, nation_b]))
    return self.diplomatic_states.get(key, "PEACE")

def get_diplomat(self, nation) -> Optional[DiplomaticRepresentative]:
    """Return diplomat for nation, or None for carved vassals."""
    return self.diplomats.get(nation)

def get_nation_capital(self, nation) -> Optional[str]:
    """Return runtime capital/proxy region name for topology and spawns."""
    return NATION_CAPITALS.get(nation)

def get_settlement_home_capital(self, nation) -> Optional[str]:
    """Return true settlement capital; Britain is off-map even though NATION_CAPITALS uses a proxy."""
    if nation == "Britain":
        return None
    return NATION_CAPITALS.get(nation)

def get_known_nations(self) -> List[str]:
    """Return list of all nation names (for validation)."""
    return list(self.nation_authority.keys()) + ["France"]
```

```python
# ═══════ v2.1 NEW FIELDS ═══════

# NOTE: Carved vassals are stored in self.vassals (above) with "path": "carved".
# No separate dict — single source of truth. See §8f serialization note.

# AI nation authority (§4a — DP generation depends on this)
# Key: nation name. Value: int 0-100. Default 60 for all AI nations.
self.nation_authority: Dict[str, int] = {
    "Britain": 60, "Prussia": 60, "Austria": 60, "Saxony": 60
}

# Proactive suggestion cooldowns (DESIGN §5d — serialization required)
# Key: "nation|trigger_type" (e.g., "Austria|relation_threshold").
# Value: turns remaining until trigger can fire again.
self.proactive_suggestion_cooldowns: Dict[str, int] = {}

# Previous treaties for escalating harshness (DD8-4)
# List of {"target": str, "harshness": float, "turn": int}
self.previous_treaties: List[Dict] = []

# Defection cascade tracking (DD8-2)
# {"war_pair": turns_triggered} — max once per war
self.defection_cascade_fired: Dict[str, int] = {}

# ═══════ COALITION FIELDS (from COALITION_SPEC §10a) ═══════
# These fields are defined in COALITION_SPEC.md — listed here for completeness.
# Canonical definition: COALITION_SPEC §10a-d.
self.threat_sources_this_turn: List[Dict] = []  # UI breakdown of threat changes
self.active_coalition: Optional[Dict] = None     # See COALITION_SPEC §10b
self.coalition_brewing: Optional[Dict] = None    # See COALITION_SPEC §10c
self.coalition_cooldown: int = 0                 # Turns until new coalition can form
self.coalition_count: int = 0                    # Total coalitions formed this game

# War exhaustion per nation (COALITION_SPEC §6a + §10a)
# Key: nation name. Value: int 0-200 CLAMPED.
# +casualties_taken//1000 per battle (cap +20), +8/turn at war with France, -5/turn at peace.
# Used in coalition loyalty penalty formula: penalty = min(-15 + war_exhaustion // 10, 0)
self.war_exhaustion: Dict[str, int] = {}

# Player proposal cooldowns — v2.1 adds per-type tracking
# Format: {"nation": turns_remaining, "nation|proposal_type": turns_remaining}
# (already defined in v2.0, noting the expanded key format)

# Feasibility request (§2g) — no persistent state needed (momentary ADVISING state)

# Nation starting regions (m5 — source of truth for war score territory calculation)
# Populated from §1b initial table during world initialization. Static data.
self.nation_starting_regions: Dict[str, List[str]] = {
    "France": ["Paris", "Normandy", "Brittany", "Bordeaux", "Lyon", "Marseille", "Belgium", "Milan"],
    "Britain": ["Netherlands", "Waterloo", "Hanover"],
    "Prussia": ["Berlin", "Rhineland"],
    "Austria": ["Bavaria", "Vienna", "Bohemia", "Tyrol"],
    "Saxony": ["Saxony", "Dresden"],
}
```

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
| `backend/models/region.py` | 7 new regions, 1 removed (Geneva), 1 renamed (Rhine→Rhineland), updated adjacency for all regions |
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

| File | Purpose | Session |
|------|---------|---------|
| `backend/game_logic/diplomacy.py` | Core diplomatic engine: acceptance formula, state transitions, treaty evaluation, DP management | 2 |
| `backend/models/diplomat.py` | DiplomaticRepresentative class, diplomatic personality definitions | 2 |
| `backend/game_logic/diplomatic_dialogue.py` | Dialogue state machine, classify_intent, build_dialogue | 3 |
| `backend/game_logic/diplomatic_templates.py` | Template library, slot resolvers, personality modifiers | 3 |
| `backend/game_logic/diplomatic_advisory.py` | Strategic conversation handlers, "what if" engine | 4 |
| `backend/game_logic/vassal.py` | Vassal loyalty, tribute, rebellion, autonomy | 5 |
| `backend/commands/diplomatic_defiance.py` | Talleyrand's defiance: probability curve, sabotage application, discovery | 6 |
| `godot-client/.../diplomatic_ledger.gd` | Diplomatic Ledger screen | 8 |

### Unified Session Plan (8 Sessions)

> **Unified with CONVERSATIONAL_DIPLOMACY_DESIGN.md §14 and COALITION_SPEC.md.** The conversation layer sessions (A-D) are merged into the mechanical sessions below where they share dependencies. Coalition (Session 7) added per ROADMAP. This is the single implementation timeline for all of Phase 8.

#### Session 1A: Map Expansion + Region Migration (HIGH RISK — DD6)

**Pre-session (MANDATORY):**
1. Read `docs/ADDING_CONTENT.md` completely — follow its patterns for adding regions, marshals, nations
2. Audit the ENTIRE codebase for hardcoded region references (list every file and line)
3. Audit all test files for region-specific assertions
4. Plan save-breaking version bump
5. Estimate test migration scope (likely 100+ test updates)

**Scope:**
- 7 new regions in REGIONS_DATA (Normandy, Hanover, Berlin, Saxony, Dresden, Bohemia, Tyrol)
- 1 region **removed:** Geneva (adjacencies redistributed to Tyrol/Milan/Marseille/Bordeaux corridors)
- 1 region **renamed:** Rhine → Rhineland (all references including mock parser, prompt_builder, docstrings)
- **Existing region changes:**
  - Vienna: income 200→300, major_city→capital, is_capital=True, controller Prussia→Austria, adjacency adds Bohemia+Tyrol
  - Bavaria: controller Prussia→Austria, adjacency adds Saxony+Tyrol, removes Lyon
  - Paris: adjacency adds Normandy+Bordeaux, removes Waterloo
  - Waterloo: adjacency removes Paris, adds Netherlands+Hanover
  - Brittany: adjacency removes Paris, adds Normandy
  - Bordeaux: adjacency removes Geneva, adds Paris+Lyon+Marseille
  - Lyon: adjacency removes Bavaria, adds Bordeaux+Rhineland(was Rhine)
  - Marseille: adjacency removes Geneva, adds Bordeaux+Milan
  - Belgium: adjacency adds Normandy+Rhineland(was Rhine)
  - Milan: adjacency removes Geneva, adds Marseille+Tyrol
  - Netherlands: adjacency adds Waterloo+Hanover
- Updated `NATION_CAPITALS`: Prussia "Rhine"→"Berlin", add Saxony→"Dresden"
- `_setup_initial_control()` auto-derives from REGIONS_DATA — no manual expansion needed
- **Victory threshold:** Update `turn_manager.py` enemy victory from `>= 10` to `>= int(total * 0.75)` (scales with region count)
- **Hardcoded reference cleanup:** prompt_builder.py (geographic layout, fallback region list), llm_client.py (mock parser region targets), executor.py (docstring examples), world_state.py (economic balance comments), region.py (header comment "13 regions")
- Fix ALL broken tests from region expansion
- Save format version bump (old saves incompatible — M7)

**Austria/Saxony controller note:** Session 1A sets `starting_controller` to "Austria"/"Saxony" on regions, but these nations aren't added to `enemy_nations`/`nation_gold`/`nation_actions` until Session 1B. This is safe — controller strings are just strings, and the AI only processes nations in `enemy_nations`. These regions sit inert until Session 1B activates them. *(Resolved in Session 1B — nations fully activated with AI turns, diplomatic data, and is_at_war() gating.)*

**Risk:** HIGH — Changes foundational data model. Every existing test that references specific regions, starting positions, or adjacency will break. AI decision tree (enemy_ai.py) has hardcoded region references. Garrison combat changes (capital regions). Supply attrition recalculation. Fog of war adjacency patterns. Estimated 100+ test updates.
**Gate:** `pytest` passes (100%). All 19 regions created with correct adjacency. No hardcoded Geneva/Rhine references remain. Victory threshold scales with region count.

#### Session 1B: New Nations + Marshals + Economy (HIGH RISK — DD6)

**Pre-session (MANDATORY):**
1. Audit codebase for hardcoded `["Britain", "Prussia"]` references (world_state.py init, from_dict defaults, executor debug commands)
2. Verify REGIONS_DATA starting_controller values match §1c (Austria/Saxony regions correct from 1A)
3. Confirm PrinceAugust is NOT in §1c — removal is intentional (see below)
4. **Fix Session 1A adjacency bug:** Rhineland↔Saxony connection missing from REGIONS_DATA. Spec §1b says both are adjacent. Code has Rhineland: `[Belgium, Bavaria, Lyon]` (missing Saxony) and Saxony: `[Hanover, Berlin, Bavaria, Dresden, Bohemia]` (missing Rhineland). Add "Saxony" to Rhineland's adjacent list and "Rhineland" to Saxony's adjacent list. Critical for crossroads design.

**Scope:**

*Marshals:*
- **Remove** PrinceAugust (Prussian artillery placeholder). Not in §1c. Prussia = 2 marshals / 72k total per spec. Keeping breaks force balance math the entire diplomacy system was designed around. Clean removal from `create_enemy_marshals()`, parser, mock parser, prompt_builder.
- **New** marshal definitions: Gneisenau (Prussia, Rhineland, 32k, cautious), Archduke Charles (Austria, Vienna, 35k, cautious), Schwarzenberg (Austria, Bohemia, 25k, cautious), Reynier (Saxony, Dresden, 18k, literal)
- **Relocated** starting positions: Grouchy Belgium→Lyon, Uxbridge Waterloo→Hanover, Blücher Netherlands→Berlin
- **Strength adjustments** to match §1c: Uxbridge 18k→24k, Blücher 55k→40k, Gneisenau 45k→32k
- **Spawn locations** fixed to NATION_CAPITALS: Wellington/Uxbridge→Netherlands (British proxy), Blücher/Gneisenau→Berlin, Archduke Charles/Schwarzenberg→Vienna, Reynier→Dresden
- **Cross-nation relationships:** New marshals default to 0 (Professional) with all existing marshals. No hand-crafted cross-nation opinions needed — organic relationships emerge through combat in Session 2+.

*Nations:*
- Austria, Saxony added to `enemy_nations`, `nation_gold`, `nation_actions`, `manpower_pools`
- Vienna already reassigned from Prussia to Austria capital (Session 1A)
- Nation starting regions dict populated (auto-derived from REGIONS_DATA)
- Update `from_dict()` backward-compat defaults to include Austria/Saxony for: `enemy_nations`, `nation_gold`, `nation_actions`, `manpower_pools`

*Economy:*
- Starting economy for all 5 nations per §1d region income
- **British naval income:** Wire +300 gold/turn flat bonus in `calculate_turn_income()`. This is base economy, not diplomacy. Britain runs a massive deficit without it (3 continental regions = 200 income vs 380 upkeep).
- **Trade income: DEFERRED to Session 2.** The §1d trade income breakdown (France +150, Britain +400, etc.) requires diplomatic state mechanics to calculate. Session 1B economy will be lower than the §1d "Net/Turn" column until trade is wired. Add comment in code and STATUS.md.

*Minimal diplomatic data (required for AI safety):*
- Add `diplomatic_states: Dict[str, str]` to WorldState per §13 — key format `"NationA|NationB"` (alphabetical order). Pre-populated from §1e (10 nation pairs). Example: `{"Austria|France": "PEACE", "Britain|France": "WAR", "France|Saxony": "OPEN_BORDERS", ...}`.
- Add `nation_relations: Dict[str, int]` to WorldState per §13 — same key format. Pre-populated from §1e. Example: `{"Austria|France": -30, "Britain|France": -80, "France|Saxony": 40, ...}`.
- Add `is_at_war(nation_a, nation_b) -> bool` helper — builds key from sorted pair, checks `diplomatic_states` for WAR state.
- Add `get_diplomatic_state(nation_a, nation_b) -> str` getter — returns state string, defaults to "PEACE" for unknown pairs.
- Add `modify_nation_relation(nation_a, nation_b, delta) -> int` helper — applies delta, clamps to [-100, +100] per §13.
- **Fix `get_enemies_of_nation()`** — add `and self.is_at_war(nation, marshal.nation)` filter. CRITICAL: without this, Austria/Saxony AI attacks France on turn 1 despite being at PEACE.
- Serialization: `diplomatic_states` and `nation_relations` in `to_dict()`/`from_dict()` with empty-dict defaults for backward compat. Key format is already string (no tuple serialization needed).
- **NO diplomatic mechanics:** No proposals, transitions, acceptance formula, Talleyrand, DP system. Data structures only. Session 2 builds on this foundation.

*Debug:*
- Update `/debug ai_turn` validation to accept all 5 nations (was hardcoded Britain/Prussia)
- Update `/debug set_controller` help text for 5 nations

**Risk:** HIGH — Multiple new marshals + nations touching marshal.py, world_state.py, enemy_ai.py, parser.py. Balance implications from force redistribution. PrinceAugust removal touches tests, docs, and AI bombardment references. Diplomatic data structures are new state that must serialize correctly.

**Gate:**
- `pytest` passes (100%). All broken PrinceAugust references cleaned up.
- All 11 marshals at correct positions per §1c (not 12 — PrinceAugust removed).
- All nations have gold/actions/manpower matching §1d.
- `is_at_war("France", "Britain")` returns True. `is_at_war("France", "Austria")` returns False.
- Austria/Saxony marshals do NOT attack France during 5-turn smoke test (PEACE nations idle or reposition within own territory).
- Britain/Prussia AI behavior unchanged from pre-1B (attacks France normally).
- British income includes +300 naval.
- Save/load round-trip preserves all new fields (diplomatic_states, nation_relations, new marshals).
- 5-turn smoke test: all 5 nations process turns without crash.

#### Session 2: Diplomatic States + Acceptance Formula (MEDIUM RISK)

**Builds on Session 1B:** `diplomatic_states` dict, `nation_relations` dict, `is_at_war()`, and `get_diplomatic_state()` already exist from 1B. Session 2 adds MECHANICS on top of the data structures: transitions, validation, formulas, and diplomat objects. Trade income from §1d trade breakdown is wired here (not 1B).

**Scope:**
- New file: `backend/game_logic/diplomacy.py`
- New file: `backend/models/diplomat.py`
- DiplomaticRepresentative class (Talleyrand + 4 enemy diplomats per §2b)
- State transition validation (upgrade adjacency + downgrade §5b.1 + armistice cooldown §5b.2)
- Acceptance formula (all live components per §6)
- War score calculation (§6e: territory ±40 + battles ±30 + decisive ±20 + capital ±30 + ticking ±25 per side)
- Military Supremacy modifier (§6b.1: war score ≥70 + hold capital → +25 acceptance)
- Nation relation modification mechanics (relation change from battles, treaties, etc.)
- Trade income wiring: diplomatic state → gold/turn per §5a trade values, applied in `advance_turn()`
- DP generation + spending (§4)
- Movement restrictions for PEACE/WAR states (§5a: cannot enter territory without attacking in WAR, cannot enter at all in PEACE)
- Player war declaration mechanics (attacking a PEACE nation → auto-declares WAR, applies relation/threat penalties per §5b.1)
- DEFENSIVE_ALLIANCE cascade: if France attacks Austria, Prussia auto-enters WAR with France (§5a)
- Serialization for all new fields (diplomat objects, DP pool, war score, armistice cooldowns)

**Risk:** MEDIUM — core formula with many modifiers needs careful balancing. But formula is deterministic and testable.
**Estimated tests:** ~60
**Gate:** Acceptance formula returns correct scores for test scenarios. State transitions enforce adjacency. Trade income applied correctly. War declaration triggers state change + cascades.

#### Session 3: Talleyrand Commands + Conversational Dialogue Foundation (HIGH RISK)

> **Merges:** DIPLOMACY_SPEC Session 3A + CONVERSATIONAL_DIPLOMACY_DESIGN Session A

**Scope (mechanical):**
- Talleyrand command parsing (mock parser keywords)
- _execute_diplomatic() family in executor.py
- Proposal creation from parsed commands
- Feasibility request implementation (§2g)
- Treaty ratification and clause application (including per-turn clauses)
- Gold/turn and manpower/turn clauses applied during advance_turn()
- Morning Dispatch diplomatic events (using §10d event types)
- Acceptance formula feedback (§6f)

**Scope (conversation layer — from CONV_DESIGN Session A):**
- New file: `backend/game_logic/diplomatic_dialogue.py` (~300 lines)
- New file: `backend/game_logic/diplomatic_templates.py` (~500 lines)
- Dialogue state machine + `pending_diplomatic_dialogue` field
- 10 core templates (T1-T10) covering proposal_options, proposal_confirm, proposal_execute
- `/respond_to_diplomatic_dialogue` endpoint
- Specificity routing: vague/medium/specific all work
- Fast-track for specific+agree (skip dialogue, execute directly)
- Serialization enforcement for `pending_diplomatic_dialogue`

**Risk:** HIGH — Modifies parser.py, executor.py, llm_client.py, main.py — the most critical backend files. Diplomat-vs-marshal routing in the parser is novel code with high regression risk. Dialogue state machine adds new blocking behavior.
**Estimated tests:** ~55
**Gate:** curl test: "Talleyrand, propose peace with Prussia" returns dialogue with options. "Talleyrand, what would it take to get peace with Prussia?" returns feasibility assessment. Vague/medium/specific commands route correctly. Dialogue serializes through save/load.

#### Session 4: AI Proposals + Advisory Conversations (HIGH RISK)

> **Merges:** DIPLOMACY_SPEC Session 3B + CONVERSATIONAL_DIPLOMACY_DESIGN Session B

**Scope (mechanical):**
- AI diplomatic phase in enemy_ai.py (proposal generation when losing)
- AI proposal popup (same pattern as objection popup)
- Accept/reject/counter-offer flow (using M3 counter-offer algorithm)
- Notification types (§10e templates)
- Conflicting alliance resolution (§5b.3)

**Scope (conversation layer — from CONV_DESIGN Session B):**
- New file: `backend/game_logic/diplomatic_advisory.py` (~200 lines)
- Advisory conversations ("What about Austria?", "Who's the threat?")
- Proactive suggestions (Talleyrand notices opportunity → Morning Dispatch)
- Remaining templates T11-T20 (incoming_proposal, advisory, feasibility, proactive)
- Question detection in mock parser
- Morning Dispatch integration (Talleyrand's Report section)

**Risk:** HIGH — AI proposal logic + popup flow in enemy_ai.py and main.py. Counter-offer algorithm is new deterministic logic. Advisory conversations add depth.
**Estimated tests:** ~40
**Gate:** AI sends armistice when losing. Counter-offer generates correctly. "What about Austria?" returns advisory dialogue. Proactive suggestions appear in Morning Dispatch.

#### Session 5: Vassal System + Treaty Clauses (MEDIUM RISK)

**Scope:**
- New file: `backend/game_logic/vassal.py`
- Passive vassal loyalty (autonomy drift, garrison, shared enemy, war results)
- Two vassalage paths (treaty + conquest)
- Autonomy levels (PUPPET -4/turn, SATELLITE -2/turn, AUTONOMOUS +1/turn)
- "Invest in vassal" one-shot action (1 DP + 200g → +10 loyalty, 3-turn cooldown)
- Tribute collection, autonomy change command
- Vassal rebellion (loyalty=0 → WAR, cascade -10 to other vassals)
- Enemy vassal courting (§8e — simplified v1, assigned per m3)
- Vassal carving from conquered territory (§8f — DD1)
- AP/turn treaty clause implementation
- Territory cession logic + marshal relocation
- Continental System (basic, 75g cap per nation, 200g total cap)

**Risk:** MEDIUM — vassal system is self-contained. AP clause modifying nation_actions needs careful integration.
**Estimated tests:** ~45
**Gate:** Vassal loyalty ticks. Rebellion fires at 0. Tribute collected. AP clause reduces actions.

#### Session 6: Talleyrand Defiance + Diplomatic Objections/Confrontation (MEDIUM RISK)

> **Merges:** DIPLOMACY_SPEC Session 5 + CONVERSATIONAL_DIPLOMACY_DESIGN Session C

**Scope (mechanical):**
- New file: `backend/commands/diplomatic_defiance.py`
- Talleyrand defiance probability curve
- Sabotage application (proposal modification)
- Discovery mechanics
- Talleyrand objections (V2a pattern)
- Notification types

**Scope (conversation layer — from CONV_DESIGN Session C):**
- Merged diplomatic objections into conversation flow (not separate popups)
- Sabotage confrontation popup (template T17 + discovery logic)
- Enemy diplomat voices (personality-keyed response variations)
- Talleyrand defiance trigger point wiring into dialogue state machine
- Templates T21-T27 (sabotage_confrontation, objection variants)

**Risk:** MEDIUM — defiance follows existing V2b pattern. Conversation integration adds complexity but builds on Session 3 dialogue foundation.
**Estimated tests:** ~50
**Gate:** Talleyrand sabotages with correct probability. Sabotage discovery triggers confrontation dialogue. Diplomatic objections merge into conversation flow. Enemy diplomat voices vary by personality.

#### Session 7: Coalition System (HIGH RISK)

> **Implements:** COALITION_SPEC.md (full). Builds on threat_level from Session 2.

**Scope:**
- Threat accumulation from all 9 sources (COALITION_SPEC §2a)
- Threat decay formula (COALITION_SPEC §2b)
- War exhaustion tracking per nation (COALITION_SPEC §10a — new field)
- Coalition brewing (3-turn countdown) + instant formation at threat ≥80
- Coalition structure: leader selection, strategic posture, coordination bonus
- Coalition AI behavior: coordinated attacks, resource sharing
- Coalition breaking: separate peace with loyalty penalty (§6a), decisive victory impact (§6b)
- Coalition dissolution conditions (§7)
- British subsidy mechanic (COALITION_SPEC §4e / DIPLOMACY_SPEC §9c) — **moved from Session 8 deferred list**
- Integration: steps 9a-9d in §7f processing order
- Serialization: 6 new fields (threat_sources_this_turn, active_coalition, coalition_brewing, coalition_cooldown, coalition_count, war_exhaustion)

**Risk:** HIGH — threat + formation + AI coordination + posture. Many moving parts. war_exhaustion is new field.
**Estimated tests:** ~55
**Gate:** Threat accumulates from battles/captures. Coalition forms after 3-turn countdown at threat ≥60. Instant at ≥80. Separate peace reduces coalition. Coalition dissolves when <2 members. War exhaustion tracks correctly.

#### Session 8: Diplomatic Ledger UI + Polish (MEDIUM RISK)

> **Merges:** DIPLOMACY_SPEC Session 6 (old 7) + CONVERSATIONAL_DIPLOMACY_DESIGN Session D

**Scope (UI):**
- Diplomatic Ledger Godot UI (D key) — nation cards, treaty display, threat level
- Godot diplomatic dialogue popup rendering and input handling
- Schemer bias calibration (playtesting)
- Blocking/auto-dismiss dialogue behavior
- DP cost display in dialogue options
- Ledger cross-references from dialogue

**Scope (deferred mechanical items — DD7):**

| Deferred Item | Why Deferred | Gameplay Impact |
|---|---|---|
| AI-AI diplomacy (§9c) | Not required for player-facing diplomacy loop | World feels less alive, but all player interactions work |
| Full Continental System | Economic warfare is flavor, not core combat loop | Minor diplomatic tool missing |
| Fog-filtered diplomatic intel | Existing fog system works; diplomatic fog is polish | Player sees slightly more diplomatic info than intended |
| Campaign log diplomatic events | Campaign log works; diplomatic entries are display-only | Diplomatic events don't appear in campaign log history |
| Special acceptance bonuses (§6d) | Generic formula works for all proposals | Nation-specific desires not reflected |
| Metternich armed mediation (DD8-3) | Schemer-specific AI polish | Metternich doesn't gain coalition bonus |

**Estimated tests:** ~45

### What Can Be Deferred

| Feature | Impact of Deferral |
|---------|-------------------|
| AI-AI diplomacy | Medium — world feels less alive, but player-facing diplomacy works |
| Continental System | Low — economic warfare is flavor, not core |
| Vassal courting | Low — can add after vassal system is stable |
| Talleyrand defiance | Medium — core diplomatic flow works without sabotage layer |
| Counter-offers | Low — accept/reject is sufficient for v1 |
| Special acceptance bonuses (§6d) | Low — generic formula works, bonuses add flavor |
| Vassal carving (DD1) | Medium — territory management missing, but full-nation vassalage works |
| Feasibility requests (§2g) | Low — player can still propose without pre-assessment |
| Formula feedback (§6f) | Medium — player doesn't know WHY proposals fail, trial-and-error frustration |

### Integration Risk Points

| Risk | File(s) | Mitigation |
|------|---------|------------|
| Map expansion breaks existing tests | region.py, world_state.py, many test files | Run full test suite after Session 1. Fix hardcoded region expectations. |
| Marshal relocation breaks balance | marshal.py, enemy_ai.py | Playtest 5 turns after Session 1. Adjust strength if needed. |
| PrinceAugust removal breaks references | marshal.py, llm_client.py, combat.py, enemy_ai.py, tests, docs (SYSTEMS_REFERENCE, MULTI_MARSHAL_SPEC, TACTICAL_TRIANGLE_SPEC, JEALOUSY_SPEC, STATUS) | Grep for "PrinceAugust"/"Prince August"/"prince_august" across entire codebase and docs. Update all references. |
| PEACE nations attacking France | enemy_ai.py, world_state.py | `is_at_war()` gate on `get_enemies_of_nation()`. Smoke test: Austria/Saxony must NOT attack France in 5-turn test. |
| DP generation in advance_turn | world_state.py | Simple reset — low risk. Test DP edge cases (0 DP, max DP). |
| AP/turn clause modifying nation_actions | world_state.py, executor.py | Apply during income phase, AFTER action reset. Test 0-AP edge case. |
| Acceptance formula balance | diplomacy.py | Numbers in spec are starting points. Expect tuning after playtest. |
| Vassal rebellion during enemy turn | vassal.py, turn_manager.py | Process at start of advance_turn, before any actions. |
| Save format incompatibility | save_manager.py | Add version check that rejects pre-Phase-8 saves with clear error message (M7). Increment save format version. |
| Godot int() wrapping on new fields | All API response formatting | All new numeric fields (DP, relations, war score, loyalty, threat) must use int() before API response (m7). Add to response formatting checklist. |

### Test Coverage

~365 tests across 8 sessions. Key areas:

- **Map:** 19 regions created, adjacency bidirectional, all nations assigned correct starting regions
- **Marshals:** New marshals created, starting positions correct, stats reasonable
- **Economy:** Income calculations correct for 5 nations, manpower pools initialized
- **Diplomatic states:** Transition validation supports R98 upward jumps with cumulative DP; guided UI remains adjacency-first; downgrades enforce reverse adjacency
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
| 6 | Armistice duration | **5 turns** | Matches live code and `PEACE_DEALS_UMBRELLA_SPEC.md` §4.1. Enough to reposition and negotiate without enabling armistice chaining. |
| 7 | Trade income | **50/100/150/200 scaling** | Start low, tune via playtest. Deeper diplomatic states visibly more profitable than shallow ones = incentive to progress relationships. |
| 8 | Vassal courting | **Include in v1** | Full diplomatic loop too important to defer. Simplified form: 2 DP per attempt, loyalty -15 if loyalty < 50. |
| 9 | AP treaty cap | **1 AP/turn max, war-reparation tier** | -25 acceptance penalty. Requires war score > 80. Talleyrand always objects. Late-game dominance move, not routine. |

---

## §17. Changelog

### v2.5 (Session 1B Readiness Audit — Mar 2026)

**Session 1B pre-implementation review. 4 CRITICAL + 3 HIGH findings resolved.**

**Critical Fixes:**
- **C1: AI attacks PEACE nations** — Session 1B now includes minimal `diplomatic_states` dict, `nation_relations` dict, `is_at_war()` helper, and `get_enemies_of_nation()` filter. Without this, adding Austria/Saxony to `enemy_nations` causes their AI to attack France immediately despite PEACE state.
- **C2: PrinceAugust not in §1c** — Session 1B scope now explicitly says "Remove PrinceAugust." Was a pre-Phase-8 artillery placeholder. Not in §1c marshal table. Keeping breaks force balance (Prussia 72k → 92k).
- **C3: 7 marshal stat mismatches** — Session 1B scope now explicitly lists strength changes (Uxbridge 18k→24k, Blücher 55k→40k, Gneisenau 45k→32k) alongside location changes. Previous scope only mentioned locations.
- **C4: Wrong spawn locations** — Session 1B scope now includes spawn_location fixes for all enemy marshals to use NATION_CAPITALS.

**High Fixes:**
- **H1: Trade income scope confusion** — Session 1B scope now explicitly states "Trade income: DEFERRED to Session 2" with rationale. Session 2 scope updated to include trade income wiring.
- **H2: British naval income missing** — Session 1B scope now includes +300/turn naval income as base economy (not diplomacy).
- **H3: Session 2 boundary unclear** — Session 2 scope now says "Builds on Session 1B" and clarifies it adds mechanics (transitions, formulas, DP) on top of 1B data structures.

**Other:**
- Integration Risk Points table: added PrinceAugust removal risk and PEACE-nation attack risk with mitigations.
- Session 1A "inert" note: marked as resolved in Session 1B.
- Session 1B gate criteria expanded: is_at_war() correctness, Austria/Saxony non-aggression, naval income, save/load round-trip.

### v2.4 (Pre-Implementation Audit — Mar 2026)

**Session 1A readiness audit. 4 CRITICAL + 4 MAJOR findings resolved.**

**Critical Fixes:**
- **C1: Geneva removal undocumented** — §1b now explicitly states Geneva is removed (13 − 1 + 7 = 19). Design rationale added.
- **C2: Berlin income 250 vs REGION_TYPE_INCOME["capital"]=300** — Berlin income changed to 300 to match the capital type invariant. §1d Prussia income updated (350→400, net −10→+40).
- **C3: §1d economy table inconsistent with §7e trade income** — Table now shows region income only (no trade). Trade income breakdown added below with per-nation totals. Balance note explains alliance trade as diplomatic weapon.
- **C4: Victory threshold hardcoded at 10** — Session 1A scope now includes victory threshold recalibration to `>= int(total * 0.75)`.

**Major Fixes:**
- **M1: Session 1A scope understated** — Expanded to list ALL changes: Geneva removal, Rhine rename, Vienna/Bavaria controller changes, all adjacency rewrites, NATION_CAPITALS update, hardcoded reference cleanup list, victory threshold.
- **M2: Austria/Saxony controller note** — Added note that Session 1A sets controller strings before nations exist in world_state (safe — controller is just a string).
- **M3: Dresden capital note** — Added clarification that Dresden uses `region_type: "town"` with `is_capital: True` (minor nation capital with town-level economy).
- **M4: Files to Modify table** — Fixed "6 new regions" to "7 new regions, 1 removed (Geneva), 1 renamed".

### v2.3 (Master Audit — Mar 2026)

**Final pre-implementation master audit across all 3 specs. 4 CRITICAL + 4 MAJOR findings resolved.**

**Critical Fixes:**
- **C1: `war_exhaustion` undefined** — Defined in COALITION_SPEC §10a (Dict[str,int], 0-200, +casualties//1000 per battle, +8/turn at war with France, -5/turn at peace) and cross-referenced in §13.
- **C2: Session plan mismatch** — §14 updated from 7→8 sessions. Session 7 = Coalition (NEW), Session 8 = Ledger UI (was 7). CONV_DESIGN §14c updated.
- **C3: §7f missing coalition processing** — Added steps 9a (war exhaustion), 9b (threat accumulation), 9c (threat decay), 9d (coalition check) between steps 9 and 10.
- **C4: Coalition fields missing from §13** — Added cross-reference block for 6 COALITION_SPEC fields (threat_sources_this_turn, active_coalition, coalition_brewing, coalition_cooldown, coalition_count, war_exhaustion).

**Major Fixes:**
- **M1: "Coalition war score" undefined** — Defined in COALITION_SPEC §4c as weighted average of member war scores, weighted by army size.
- **M2: CONV_DESIGN §14c wrong session** — Fixed D→Session 8 (was Session 7). Also fixed main.gd file table.
- **M3: British subsidy dependency** — Moved from Session 8 deferred list to Session 7 (Coalition) scope.
- **M4: Battlefield Diplomacy missing from §6b** — Added as new acceptance component: +10 when war_score > 20. Non-stacking with Military Supremacy.

**Stale Reference Fixes:**
- §9c: "DEFERRED TO SESSION 6 (Polish)" → "DEFERRED TO SESSION 8 (Ledger UI + Polish)"
- DD8-1 changelog: "deferred to Session 6" → "implemented in Session 7 — Coalition"
- DD7 changelog: "Session 6 deferred table" → "Session 8 deferred table"
- Test count: ~310 → ~365 across 8 sessions

### v2.1 (Audit Resolution + New Mechanics — Feb 2026)

**Responding to independent audit (DIPLOMACY_AUDIT_RESULTS.md). Score: 58/80 → 73/80. All Critical/Major findings resolved or explicitly deferred.**

**Critical Fixes:**
- **C1: DP Authority Threshold** — Fixed §10c to match §4a (≥60, not >80).
- **C2: Harshness Formula** — Added §6c.1 Harshness Value Table with per-clause values and worked example.
- **C3: Session 1 Risk** — Split into Session 1A (regions) + 1B (marshals/nations), both rated HIGH. Added mandatory pre-session codebase audit (DD6).

**Major Fixes:**
- **M1: Dispatch Event Types** — Added §10d with 21 enumerated event types following JEALOUSY_SPEC pattern.
- **M2: Notification Templates** — Added §10e with 11 notification types, priorities, and templates.
- **M3: Counter-Offer Algorithm** — Defined deterministic 5-step algorithm in §9b with per-nation desire table.
- **M4: Vassal Marshal Transition** — Added EC-K.1 specifying Trust (40), dict membership, relationship initialization.
- **M5: Conflicting Alliance Obligations** — Added §5b.3 with explicit resolution rule (higher-relation partner wins).
- **M6: Session 3 Risk** — Split into Session 3A (parser routing) + 3B (AI proposals), both rated HIGH.
- **M7: Save Migration Plan** — Added save-breaking version bump note to Session 1A + Integration Risk Points.
- **M8: AI-AI Diplomacy Scope** — §9c explicitly marked DEFERRED TO SESSION 8 with impact assessment.

**Minor Fixes:**
- **m1:** Fixed "authority ~60" annotation to "authority ~100" in §4a example.
- **m2:** Added trade income from starting PEACE states to §1d economy notes.
- **m3:** Assigned vassal courting to Session 4 scope.
- **m4:** Specified Continental System participation check formula (simplified, not full acceptance).
- **m5:** Defined `nation_starting_regions` in §13 as static data populated from §1b.
- **m6:** Added field-by-field `to_dict()`/`from_dict()` for DiplomaticRepresentative in §13.
- **m7:** Added Godot int() wrapping note to Integration Risk Points in §14.
- **m8:** Added terminology clarification (nation relations vs marshal relationships) in §1a.

**Exploit Fixes:**
- **E3:** Added OPEN_BORDERS minimum requirement before vassalage proposals (§5b transition rules).
- **E4:** Added +30 deal sweetener cap (§6b).
- **E7:** Deferred — flagged for Building Blocks-aligned redesign next session.
- **E8:** Reduced protection guarantee bonus from +5 to +3 when guarantor already at war with target's enemies.
- **E11:** Clarified post-treaty-break state: returns to one level below the broken treaty (§7d).

**New Mechanics (Design Decisions):**
- **DD1: Vassal Carving** — New §8f. Carve vassals from conquered enemy territory. Auto-generated or player-chosen names. Size scaling (can't vassalize huge nations in one action). Grant carved regions to existing vassals. Full edge cases.
- **DD2: Metternich → Schemer** — Metternich reclassified as Schemer (skill 9, upgraded from Dove/8). Einsiedel (Saxony) reassigned to Dove. All 4 personality types now in active use.
- **DD3: Feasibility Requests** — New §2g. Free (0 DP) consultation with Talleyrand before proposals. Difficulty tiers, Schemer bias, discovery mechanic.
- **DD4: Formula Feedback** — New §6f. Every proposal response includes natural-language hint mapping the largest formula component. REJECT/COUNTER/ACCEPT all get feedback.
- **DD5: Sweetener Changes** — +30 cap on deal sweeteners. Per-turn manpower and AP offer variants added. Protection guarantee reduced contextually (E8).
- **DD6: Session Plan** — Session 1 split into 1A/1B. Session 3 split into 3A/3B. All four rated HIGH.
- **DD7: Deferred Items** — Session 8 now has explicit table with rationale, impact, and target for every deferred item.
- **DD8: Historical Suggestions** — Evaluated all 4 from Audit Appendix B:
  - DD8-1: British subsidy → added to §9c as AI behavior (implemented in Session 7 — Coalition)
  - DD8-2: Vassal defection cascade → added to §8d as tipping point mechanic
  - DD8-3: Metternich armed mediation → added to §5c as Schemer-specific AI behavior
  - DD8-4: Escalating treaty harshness → added to §6c.1 as +5 modifier

**Edge Cases Added (EC-II through EC-WW):**
17 new edge cases (15 from audit + 2 for vassal carving): Paris cession, cross-proposal race, armistice breaking, vassal territory treaties, bankruptcy, mission-target war, decisive battle persistence, Continental System conquest, successful sabotage, simultaneous vassal deterioration, DP warning, alliance cascade loops, sovereignty changes, vassal carving adjacency, carved vassal granting.

**New Model Fields:**
- `carved_vassals`, `previous_treaties`, `defection_cascade_fired`, `nation_starting_regions`
- DiplomaticRepresentative `to_dict()`/`from_dict()` specified

**Self-Audit Score: 73/80 (Grade A)**

| Category | v2.0 | v2.1 | Delta | Notes |
|----------|------|------|-------|-------|
| Internal Consistency | 8 | 9 | +1 | C1 fixed, m1 fixed, terminology standardized |
| Integration | 8 | 9 | +1 | Dispatch events, notifications, serialization all enumerated |
| Exploit Resistance | 9 | 10 | +1 | E3/E4/E8/E11 fixed, sweetener cap, OPEN_BORDERS gate |
| Edge Cases | 9 | 10 | +1 | 51 total (34 original + 17 new). All audit EC-1 through EC-15 resolved |
| Historical Plausibility | 9 | 9 | 0 | Metternich Schemer, British subsidy, armed mediation, escalating harshness |
| Player Experience | 8 | 9 | +1 | Feasibility requests, formula feedback, Schemer bias discovery |
| Implementation Risk | 8 | 9 | +1 | Sessions split, all HIGH risk, pre-session audit, save migration |
| Spec Completeness | 9 | 8 | -1 | E7 deferred, Opportunist dropped. But harshness table and counter-offer algorithm fill bigger gaps |
| **Total** | **68** | **73** | **+5** | **Grade: A (maintained)** |

### v2.0 (Full Audit Revision — Feb 2026)

**Audit-driven revision addressing 40+ findings from independent design review.** Previous grade: 47/80 (C). Target: 65+/80 (A).

**Critical Fixes (C1-C4):**
- **C1: War Score Formula defined inline (§6e).** No longer depends on non-existent COALITION_SPEC.md. Full formula: territory ±40 + battles ±30 + decisive battle bonus ±20 + capital ±30 + War Purpose ticking ±25 per side, with final score capped at ±100. Includes war score decay (-2/turn stale battle component only) and implementation specification.
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
- Armistice: 5 turns (canonical; matches live code)
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

### v2.2 (Final Audit — Feb 2026)

**Independent final audit across both DIPLOMACY_SPEC.md and CONVERSATIONAL_DIPLOMACY_DESIGN.md. 43 findings resolved (7 Critical, 19 Major, 17 Minor). Previous score: 91/100. New score: 97/100.**

See §18 for full audit summary.

---

## §18. Final Audit Summary

### 18a. Findings Table

| ID | Severity | Description | Fix Applied | Section |
|----|----------|-------------|-------------|---------|
| F1 | Major | ASCII map shows Milan twice | Removed duplicate Milan from diagram | §1b |
| F2 | Critical | Einsiedel labeled "Loyalist" in Ledger; should be "Dove" | Fixed to "Dove" | §10b |
| F3 | Major | DESIGN references `world.nations` — non-existent field | Changed to `world.get_known_nations()` | DESIGN §2d |
| F4 | Major | `_suggest_gold_per_turn` returns tuple, template expects int | Added `[0]` unpacking in slot resolver | DESIGN §4c |
| F5 | Major | AI nation authority tracking unspecified | Added `nation_authority` dict with starting values, change rules | §4a, §13 |
| F6 | Minor | Transition cost table hybrid preconditions | No change — clear enough in context | §5b |
| F7 | Minor | COURT_NATION 20% random element | No change — consistent with existing combat randomness | §2e |
| F9 | Major | deal_sweetener vs deal_demands ambiguous in formula | Renamed to `deal_balance`, clarified as single component | §6a |
| F10 | Major | `/respond_to_diplomatic_dialogue` endpoint incomplete | Added full request/response specification with error handling | DESIGN §9d |
| F11 | Major | Vassal loyalty "relation with lord" unspecified | Clarified: uses `nation_relation(vassal, lord)` | §8b |
| F12 | Critical | `carved_vassals` contradicts §8f (same dict vs separate) | Removed separate dict from §13, use `vassals` with `path: "carved"` | §8f, §13 |
| F13 | Critical | Redundant vassal investment cooldown tracking | Removed `vassal_investment_cooldowns` dict, use per-vassal field | §13 |
| F16 | Minor | VASSAL trade income not listed in TRADE_INCOME | Added comment: VASSAL uses tribute, not bilateral trade | §7e |
| F18 | Major | Region count mismatch (text says 6, list has 7) | Fixed to "7 new regions" | §14 |
| F19 | Major | Replace-with-Loyalist personality interaction unspecified | Added comprehensive note: all Schemer effects disabled, Loyalist values used | §3d |
| F20 | Minor | `turn_created` field purpose unclear | Added inline comment explaining auto-dismiss behavior | DESIGN §2b |
| F21 | Minor | Schemer +5 for both peace and harsh — unclear | Added "(pragmatic openness)" clarification | §6b |
| F22 | Major | Template T23 shows wrong DP cost (2 instead of 1) | Fixed to "Costs 1 DP" for open borders | DESIGN §4b |
| F27 | Minor | DESIGN §3a reference to "existing §2d mechanics" unclear | Added explicit clarification: transit mechanics unchanged, presentation redesigned | DESIGN §3a |
| F29 | Critical | Same as F2 — Einsiedel "Loyalist" in Ledger (second instance) | Fixed with F2 | §10b |
| F30 | Minor | Skill bonus float intermediate (7.5) | Added explicit `int(round())` example | §2e |
| F31 | Major | WorldState getter methods referenced but undefined | Added 6 getter method specifications to §13 | §13 |
| F33 | Major | Template system hardcodes "schemer" personality | Changed to dynamic parameter with fallback | DESIGN §4d |
| F34 | Critical | Harshness worked example confuses Dove/Hawk thresholds | Fixed: Dove < 0.3 bonus, Hawk > 0.6 bonus | §6c.1 |
| F35 | Minor | DESIGN §11a lists §10b as replaced but it's unchanged | Fixed header to remove §10b from replacement list | DESIGN header |
| F36 | Minor | Proactive suggestion cooldowns not serialized | Added `proactive_suggestion_cooldowns` field to §13 | §13, DESIGN §5d |
| F39 | Major | DP regeneration vs mission deduction ordering unclear | Resolved by §7f processing order (step 1 before step 2) | §7f (new) |
| F40 | Major | Nation relation clamping unspecified | Added CLAMPED note with `max(-100, min(100, ...))` | §13 |
| F43 | Major | Threat level clamping unspecified (can go below 0) | Added CLAMPED 0-100 note | §13 |
| F44 | Minor | Carved vassal instant-carve loyalty note missing | Added explicit minimum case note (loyalty 15) | §8f |
| F45 | Minor | modify_generous no iteration cap | Added 2-iteration cap matching modify_harsh | DESIGN §9b |
| F46 | Major | DESIGN templates need int() for numeric slots | Added Golden Rule #2 note + int() wrapping in resolvers | DESIGN §4c |
| F47 | Critical | `proposal_in_transit` clear timing unspecified | Added CLEAR TIMING note: after player responds, not on display | §13 |
| F49 | Critical | advance_turn() diplomacy processing order unspecified | Added §7f with full 14-step processing order | §7f (new) |
| F51 | Major | Inconsistent directory structure between SPEC and DESIGN | Aligned DESIGN to `backend/game_logic/` (matching SPEC pattern) | DESIGN §14a, §11c |
| F52 | Major | Counter-offer "cheapest clause" undefined | Clarified: lowest deal_sweetener acceptance impact | §9b |
| F54 | Major | Skill bonus "rounded down" ambiguous | Added explicit `int(round())` examples for both tiers | §2e |
| F55 | Minor | Garrison bonus integer division unclear | Changed to `min(garrison_troops // 5000, 3)` formula | §8b |
| F56 | Major | Clause-selection save/load unspecified (N1 from previous audit) | Added `clause_selection` dialogue type with serialization schema | DESIGN §3b |
| F57 | Minor | War declaration transition cost table incomplete | Added "see §5c for full costs" reference | §5b |
| F58 | Minor | Enemy diplomat personality asymmetry undocumented | Added design note explaining intentional asymmetry | §9a |
| F59 | Major | No voluntary vassal release transition | Added VASSAL → PEACE path (1 DP, +20 relation) | §5b |
| F60 | Minor | Acceptance formula rounding instruction | Added "round ONCE after summing" note | §6a |
| F61 | Minor | Vassal nation relations persist through vassalage | Added explicit note in §8c | §8c |
| F62 | Minor | Tribute calculation rounding unspecified | Added `int()` truncation specification | §8c |
| F63 | Minor | Gold-for-manpower deal sweetener ambiguous | Added sweetener calculation note to clause table | §7a |
| F64 | Minor | Template T23 references non-existent "trade agreement" | Added note: option proposes OPEN_BORDERS, not "trade agreement" | DESIGN §4b |
| F65 | Critical | `pending_diplomatic_dialogue` missing from SPEC §13 | Added field definition with cross-reference to DESIGN §2b | §13 |
| F66 | Major | Proactive suggestion cooldown field missing | Added `proactive_suggestion_cooldowns` to §13 | §13 |
| F70 | Minor | Continental System France exclusion unclear | Added "excluding France" specification | §5d |
| F71 | Minor | AI proposal queue size limit missing | Added max 3 queue, 3-turn expiration | §9a |
| F72 | Minor | Feasibility step count not reported | Added step count to feasibility response | §2g |

**Not fixed (intentional design):** F6 (transition table is clear in context), F7 (random element consistent with combat), F8 (defiance variance mirrors V2b).

### 18b. Dimensional Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Mechanical Completeness** | 10/10 | All state transitions defined. All formulas have ranges and edge cases. No TBD/TODO remaining. Processing order specified (§7f). |
| **Cross-Document Consistency** | 9/10 | All §-references verified. Field names aligned. Directory structure aligned. One remaining friction: DESIGN occasionally references SPEC section numbers that could shift if sections are added (-1). |
| **Edge Case Coverage** | 10/10 | 51+ edge cases in SPEC. All 2-system interactions traced (diplomacy × combat, × fog, × strategic orders, × save/load). Boundary values clamped. Same-turn ordering defined. |
| **Golden Rule Compliance** | 10/10 | All 7 rules verified. int() wrapping explicit. Single source of truth for all formulas. State clearing after reading. Building Blocks for AI. |
| **Implementability** | 10/10 | All function signatures specified. Getter methods defined. Directory structure aligned. Endpoint fully specified. Serialization complete for all fields. |

**Subtotal: 49/50**

| Additional | Score | Notes |
|------------|-------|-------|
| **Session Plan Risk** | 10/10 | Sessions split (1A/1B, 3A/3B), all rated HIGH, mandatory pre-session audits, save migration planned. |
| **Balance & Exploits** | 10/10 | Sweetener cap, OPEN_BORDERS gate, armistice cooldown, proposal spam prevention, PUPPET nerf, queue limits. |
| **Historical Plausibility** | 10/10 | Continental System, decisive battles, Metternich armed mediation, British subsidies, Treaty of Tilsit scenario. |
| **Spec Prose Quality** | 9/10 | Clear, well-organized, good worked examples. §17 changelog is comprehensive. One minor deduction: spec is very long (~2600 lines) — consider summary index for developers. |
| **Deferred Items Clarity** | 9/10 | All deferred items have rationale and target session. E7 defiance floor redesign still vague on timeline (-1). |

**Subtotal: 48/50**

### 18c. Overall Score

**97/100**

Deductions:
- -1: Cross-doc section references are fragile (renumbering would break them)
- -1: Spec length (~2600 lines) may cause implementation fatigue; consider a developer quick-reference
- -1: E7 defiance floor redesign deferred without concrete timeline

### 18d. Fun & Innovation Scores

| Dimension | Score | Commentary |
|-----------|-------|------------|
| **Fun Factor** | 9/10 | The "talk to Talleyrand" loop is genuinely novel — no strategy game has done conversational diplomacy with a character who has opinions and might go behind your back. The MEDIUM path (player says "deal with Prussia," Talleyrand fills in details) is the fun sweet spot. The Schemer bias creates a trust-calibration meta-game that rewards experienced players. The -1 is for potential template fatigue in long campaigns — 27 templates with slot variants is good but may feel mechanical after 40+ turns in mock mode. LLM mode largely solves this. |
| **Innovation** | 10/10 | No strategy game has ever done this. Diplomacy in every 4X (EU4, Civ, TW) is a menu. Here it's a conversation with a brilliant, untrustworthy advisor. The three-layer design (diplomatic game + advisory game + relationship game) creates depth that UI-based diplomacy cannot match. The mock-first design constraint forces structural fun rather than relying on AI generation. |
| **Replayability** | 8/10 | 5 nations with distinct personalities, 4 diplomat types, multiple victory paths (military conquest, diplomatic mastery, vassalage empire). The swing state (Austria) creates different games depending on whether you court or fight them. The -2: starting positions are fixed, so the opening diplomatic situation is always the same. Consider: random starting relations within ±10 band for replayability. Saxony's path (vassal/ally/buffer) adds variety but is predictable. |
| **Narrative Impact** | 9/10 | Sabotage discovery is a genuine dramatic moment. The confrontation popup ("You ordered X, Talleyrand delivered Y") creates player stories. The defection cascade (Leipzig moment) can create dramatic empire-crumbling narratives. Vassal rebellion after a military defeat chain-reacts beautifully. The -1: narrative moments are mostly reactive (things going wrong). Consider: proactive narrative beats for things going right (alliance celebration, vassal loyalty milestone). |
| **Strategic Depth** | 9/10 | DP as separate economy forces real tradeoffs (court Austria vs. negotiate with Prussia vs. maintain Saxony). The acceptance formula creates a genuine optimization puzzle. The tension between military and diplomatic paths (combined approach is strongest but costs both AP and DP) is excellent. The -1: the formula is transparent via the Ledger, which might reduce strategic mystery. Consider: hiding some formula components behind intel (require GATHER_INTEL to see personality modifier). |

### 18e. Ready for Implementation?

**YES — with two advisory notes:**

1. **Session 1A remains the highest-risk session.** Map expansion (13 → 19 regions) will break 100+ tests. The mandatory pre-session codebase audit in the spec is essential — do not skip it.

2. **E7 defiance floor redesign** should be scheduled for Session 5 or deferred explicitly to post-Phase-8 polish. The current 2% floor works mechanically but the audit recommends reconsidering 5% for gameplay visibility. This is a balance decision, not a spec gap.

**Both specs are implementation-ready.** All Critical/Major findings resolved. No ambiguity that would block a developer. Every formula, field, transition, and edge case is specified.
