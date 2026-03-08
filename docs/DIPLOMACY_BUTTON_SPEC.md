# Diplomacy Button — Design Spec

> **Status:** APPROVED — design decisions finalized March 8, 2026
> **Phase:** 5 (Design Depth)
> **Companion:** DIPLOMACY_SPEC.md, DIPLO_REFINEMENT.md
> **Overlaps:** R117 (Advisory Actionability) — absorbed into this feature

---

## Design Philosophy

"Talleyrand is your Foreign Minister — you should be able to summon him."

Typed commands remain the power-user path. The Diplomacy Button is a guided wizard that makes the full diplomatic toolkit discoverable without memorizing syntax. The player clicks a button, Talleyrand asks two questions (who? what?), and the existing conversational system takes over. No new mechanics — just a front door to existing ones.

---

## §1. UI Placement & Hotkey

### 1a. Button Location

A **[Diplomacy]** button in the `InputSection` HBoxContainer, between `SendButton` (Execute) and `EndTurnButton` (End Turn):

```
[ CommandInput                    ] [Execute] [Diplomacy] [End Turn (E)]
```

- Style: Same font/color as Execute and End Turn buttons
- Text: `"Diplomacy"`
- Disabled + tooltip when: Talleyrand IN_TRANSIT, or modal dialog open

### 1b. Hotkey

**F1** — works even when CommandInput has focus (LineEdit doesn't consume function keys). Tooltip on button: `"Diplomacy (F1)"`.

Rationale: Letters are blocked (user types in command box). Ctrl+combos risk OS conflicts. F1 is universally "help/assistant" — fitting for summoning your Foreign Minister.

### 1c. Hotkey Wiring

```
# In main.gd _on_command_input_gui_input():
if event is InputEventKey and event.pressed and event.keycode == KEY_F1:
    _open_diplomacy_wizard()
    command_input.accept_event()

# In main.gd _unhandled_input():
if event.keycode == KEY_F1 and not _is_hotkey_blocked():
    _open_diplomacy_wizard()
```

---

## §2. The Wizard Flow

Three-step guided flow. Each step is a popup (CanvasLayer 100, modal).

### Step 1: Nation Selection

**Trigger:** Player clicks [Diplomacy] button or presses F1.

**Talleyrand says:**
> "Your Excellency, which nation requires our diplomatic attention?"

**Options:** Buttons for each known nation, filtered:
- Only nations with PARTIAL+ fog visibility (player has met them)
- Exclude player's own nation
- Each button shows nation name + current diplomatic state as subtitle
- Example: `[ Prussia — AT WAR ]` `[ Austria — Peace ]` `[ Saxony — Vassal ]`
- **[Cancel]** button to dismiss

### Step 2: Action Selection

The action popup is split into two visual sections and topped with Talleyrand's assessment panel.

#### 2a. Talleyrand's Assessment (Top Panel)

A read-only info panel at the top of the popup, shown for every nation. This IS the "Assess Relations" feature — free, always visible, no action needed.

**Content (from `/diplomatic_preview` endpoint):**

```
┌─────────────────────────────────────────────┐
│  TALLEYRAND'S ASSESSMENT — PRUSSIA          │
│                                             │
│  Status: AT WAR    Relation: -45 (Hostile)  │
│                                             │
│  "Prussia bleeds, Your Excellency, but her  │
│   pride remains intact. An armistice may    │
│   find receptive ears — peace, less so."    │
│                                             │
│  Recommendation: Propose Armistice          │
└─────────────────────────────────────────────┘
```

**Assessment includes:**
- Current diplomatic state + relation score with descriptor (Hostile/Wary/Neutral/Friendly/Loyal)
- 1-2 sentence Talleyrand-voiced situational read (template-driven, not LLM)
- Recommendation: The highest-likelihood available proposal action, or strategic advice if no proposals are favorable

**Relation descriptors:**
| Range | Word |
|-------|------|
| 60+ | Loyal |
| 30-59 | Friendly |
| 0-29 | Neutral |
| -29 to 0 | Wary |
| -30 or below | Hostile |

#### 2b. Foreign Affairs Section

Actions for non-vassal nations. Context-filtered by current diplomatic state. Wizard shows only the **next upward step** — guided interface, not full jump menu.

**Available actions per state:**

| Current State | Available Actions |
|---------------|-------------------|
| WAR | Propose Armistice (1 DP), Send Ultimatum (2 DP) |
| ARMISTICE | Propose Peace (2 DP) |
| PEACE | Propose Open Borders (1 DP), Declare War (1 DP), Send Ultimatum (2 DP) |
| OPEN_BORDERS | Propose Non-Aggression (1 DP), Propose Vassal (3 DP), Declare War (1 DP), Break Treaty (1 DP), Downgrade (1 DP), Send Ultimatum (2 DP) |
| NON_AGGRESSION | Propose Defensive Alliance (2 DP), Propose Vassal (3 DP), Declare War (1 DP), Break Treaty (1 DP), Downgrade (1 DP), Send Ultimatum (2 DP) |
| DEFENSIVE_ALLIANCE | Propose Alliance (2 DP), Propose Vassal (3 DP), Declare War (1 DP), Break Treaty (1 DP), Downgrade (1 DP) |
| ALLIANCE | Declare War (1 DP), Break Treaty (1 DP), Downgrade (1 DP) |

**State progression** (matches `_UPGRADE_ORDER` in `diplomacy.py`):
`WAR → ARMISTICE → PEACE → OPEN_BORDERS → NON_AGGRESSION → DEFENSIVE_ALLIANCE → ALLIANCE`

**DP costs are dynamic** — wizard reads from `get_transition_dp_cost()`, not hardcoded. Values above reflect current `TRANSITION_RULES`. Typed commands can still propose jumps (skipping steps) — the wizard just guides through one step at a time.

Each proposal action shows its likelihood descriptor (see §3).

#### 2c. Vassal Management Section

Shown instead of Foreign Affairs when the selected nation is the player's vassal. Step 1 lists vassals alongside other nations — tagged with `[Vassal]` subtitle. Click a vassal → Step 2 shows vassal management actions below the assessment panel.

| Action | Cost |
|--------|------|
| Invest in Vassal | 1 DP + 200g |
| Increase Autonomy | 1 DP |
| Decrease Autonomy | 1 DP |
| Release Vassal | 1 DP |

**Assessment panel for vassals** shows:
- Current loyalty (numeric + bar) and autonomy level (Puppet/Satellite/Autonomous)
- Loyalty trend arrow (rising/falling/stable based on per-turn drift)
- Tribute income from this vassal
- Investment cooldown if active

With multiple vassals (up to 4 in current game), Step 1 shows all of them in the nation list. The flow is always: pick vassal → see its specific status + actions. No bulk management — one vassal at a time.

#### 2d. Action Filters

Actions are hidden or grayed based on game state:
- Armistice cooldown active → hide Declare War, tooltip shows remaining turns
- DP insufficient → action grayed out with "(Insufficient DP)" label
- Gold insufficient (Invest) → action grayed out with "(Insufficient Gold)" label
- Talleyrand IN_TRANSIT → entire wizard disabled (button grayed)
- Nation is eliminated → not shown in Step 1
- Proposal cooldown active → hide that proposal type, tooltip shows "Cooldown: N turns"
- Investment cooldown active → hide Invest, tooltip shows remaining turns
- Ultimatum cooldown active → hide Send Ultimatum, tooltip shows "Cooldown: N turns"
- Autonomy at extreme → gray out (already Puppet: can't Decrease; already Autonomous: can't Increase)
- Release cooldown active → gray out Propose Vassal for recently-released nations, tooltip shows "Released recently: N turns"
- Relation requirement not met → gray out proposal with "(Relations too low)" label

**[Back]** button returns to Step 1. **[Cancel]** dismisses wizard.

#### 2e. Edge Case Handling

When the wizard opens but the player can't do much:

**0 DP available:** All actions grayed. Assessment panel adds: *"Our diplomatic reserves are spent, Your Excellency. We must wait for the next turn."* Show DP regeneration info ("You will gain N DP next turn").

**All cooldowns active:** No proposals available for any nation. Assessment panel adds: *"Our recent overtures must settle before new proposals, Your Excellency. Patience."*

**All proposals Hopeless/Unlikely:** No proposal has Favorable+ likelihood. Assessment panel recommendation changes from a specific proposal to strategic advice: *"Relations must improve before any proposal will find purchase. A battlefield victory or released vassal would change their calculus."*

**Single nation remaining:** Step 1 shows one button. This is fine — click it, see options. No special handling needed.

### Step 3: Handoff to Existing System

Player clicks an action → wizard closes → existing system takes over:

| Action Type | What Happens |
|-------------|--------------|
| Propose X | Constructs command `"propose [treaty] with [nation]"` → sends to `/command` → existing conversational dialogue flow starts |
| Declare War | Constructs `"declare war on [nation]"` → sends to `/command` → existing Talleyrand objection flow |
| Break Treaty | Constructs `"break treaty with [nation]"` → sends to `/command` |
| Downgrade | Constructs `"downgrade relations with [nation]"` → sends to `/command` |
| Send Ultimatum | Constructs `"send ultimatum to [nation]"` → sends to `/command` |
| Propose Vassal | Constructs `"propose vassalization to [nation]"` → sends to `/command` → existing conversational dialogue flow |
| Invest | Constructs `"invest in [nation]"` → sends to `/command` |
| Change Autonomy | Constructs `"increase/decrease autonomy [nation]"` → sends to `/command` |
| Release Vassal | Constructs `"release [nation]"` → sends to `/command` |

The wizard is purely a command builder. No new backend endpoints needed for the core flow (only the preview endpoint for assessment + likelihood).

---

## §3. Likelihood Descriptors

Proposal actions show a thematic likelihood word instead of numeric acceptance scores. Computed by calling a lightweight preview endpoint.

### 3a. Word Scale

| Score Range | Descriptor | Color |
|-------------|-----------|-------|
| 70+ | "Almost Certain" | Green |
| 50-69 | "Favorable" | Light green |
| 40-49 | "Uncertain — may counter" | Yellow |
| 30-39 | "Doubtful — expect counter" | Orange |
| 15-29 | "Unlikely" | Light red |
| < 15 | "Hopeless" | Red |

### 3b. Display Format

```
[ Propose Alliance (1 DP) — Favorable ]
[ Propose Peace (1 DP) — Doubtful ]
```

### 3c. Backend: Preview Endpoint

```
GET /diplomatic_preview?nation=Prussia
```

Returns available actions with acceptance previews for proposal types:

```json
{
  "nation": "Prussia",
  "current_state": "WAR",
  "current_state_display": "At War",
  "relation": -45,
  "relation_descriptor": "Hostile",
  "dp_available": 2,
  "is_vassal": false,
  "assessment": "The war with Prussia grinds on without decisive result. Both sides bleed. An armistice may find receptive ears.",
  "recommendation": "Propose Armistice",
  "section": "foreign_affairs",
  "actions": [
    {
      "action": "propose_armistice",
      "display_name": "Propose Armistice",
      "dp_cost": 1,
      "available": true,
      "likelihood": "Favorable",
      "likelihood_score": 55
    },
    {
      "action": "send_ultimatum",
      "display_name": "Send Ultimatum",
      "dp_cost": 2,
      "available": true,
      "likelihood": "Doubtful",
      "likelihood_score": 35
    }
  ]
}
```

Vassal example:
```json
{
  "nation": "Saxony",
  "current_state": "VASSAL",
  "current_state_display": "Vassal",
  "relation": 40,
  "relation_descriptor": "Friendly",
  "dp_available": 3,
  "is_vassal": true,
  "vassal_loyalty": 65,
  "vassal_autonomy": "SATELLITE",
  "vassal_loyalty_trend": "rising",
  "vassal_tribute": 150,
  "assessment": "Saxony serves faithfully. Tribute flows, the garrison keeps order. A reliable vassal.",
  "recommendation": "No urgent action needed",
  "section": "vassal_management",
  "actions": [
    {
      "action": "invest_vassal",
      "display_name": "Invest in Vassal",
      "dp_cost": 1,
      "gold_cost": 200,
      "available": true
    },
    {
      "action": "increase_autonomy",
      "display_name": "Increase Autonomy",
      "dp_cost": 1,
      "available": true
    },
    {
      "action": "decrease_autonomy",
      "display_name": "Decrease Autonomy",
      "dp_cost": 1,
      "available": true
    },
    {
      "action": "release_vassal",
      "display_name": "Release Vassal",
      "dp_cost": 1,
      "available": true
    }
  ]
}
```

The `likelihood_score` field is for internal use (sorting, debugging). Godot only displays the `likelihood` word and applies color.

### 3d. Preview Calculation

Reuses `calculate_acceptance()` from `diplomacy.py` with a hypothetical base proposal (no sweeteners/demands). This gives the "baseline" likelihood before the player adds clauses in the conversational flow.

### 3e. Unified Likelihood Words

The same word scale is used everywhere likelihood is shown:
- Diplomacy wizard action buttons (this spec)
- R118 Enhanced Acceptance Preview (conversational flow)
- Any future acceptance display

Single source: `get_likelihood_descriptor(score)` in `diplomacy.py`.

### 3f. Assessment Templates

Talleyrand's assessment text is template-driven (no LLM). Templates appear in the **Step 2 popup assessment panel** — the gray box at the top, above the action buttons. All contained within the popup.

Templates keyed by `(diplomatic_state, relation_range)`. War state also keys on war score. Vassal state keys on loyalty range instead of relation.

**v1 Template Set (15 templates):**

| Key | Template Text |
|-----|---------------|
| `war_winning` (war score > 20) | "{Nation} falters, Your Excellency. Our armies press the advantage — an armistice now would be accepted from a position of strength." |
| `war_losing` (war score < -20) | "The campaign goes poorly against {Nation}. An armistice may be wise — though they will sense our weakness and demand terms." |
| `war_stalemate` (-20 to 20) | "The war with {Nation} grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." |
| `armistice_wary` (relation < 0) | "The guns are silent, but the wound festers. Peace may be achievable with {Nation}, though they will demand terms." |
| `armistice_neutral` (relation >= 0) | "The armistice holds. {Nation} appears open to permanent peace — the moment may be favorable." |
| `peace_hostile` (relation < -29) | "Relations with {Nation} remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." |
| `peace_wary` (-29 to 0) | "{Nation} maintains a cautious distance. Vienna watches our moves with calculating eyes. Open borders would test their appetite." |
| `peace_neutral` (0 to 29) | "{Nation} is neither friend nor foe. Opportunity exists for closer ties — open borders would be a natural first step." |
| `peace_friendly` (relation >= 30) | "{Nation} is well-disposed toward us. The time is ripe for open borders, perhaps more." |
| `open_borders_neutral` (relation < 30) | "Our borders with {Nation} are open, but trust remains shallow. A non-aggression pact would formalize the thaw." |
| `open_borders_friendly` (relation >= 30) | "{Nation} trades freely with us. The foundation is strong — a non-aggression pact or deeper ties are within reach." |
| `non_aggression_to_alliance` | "We have {Nation}'s word they will not strike. A defensive alliance would bind us closer — if the relation bears it." |
| `alliance_stable` (relation >= 50) | "Our alliance with {Nation} stands firm. There is little to gain from change, and much to lose." |
| `alliance_strained` (relation < 50) | "Our alliance with {Nation} holds, but the bond frays. Tread carefully — a break now would cost us dearly." |
| `vassal_loyal` (loyalty >= 50) | "{Nation} serves faithfully. Tribute flows, the garrison keeps order. A reliable vassal." |
| `vassal_restless` (loyalty 25-49) | "Unrest simmers in {Nation}. The burden of tribute grows heavy — investment would forestall rebellion." |
| `vassal_rebellious` (loyalty < 25) | "{Nation} teeters on the edge of rebellion, Your Excellency. Urgent investment or increased autonomy may be our only recourse." |

**Fallback** (no matching template): *"Talleyrand considers the situation with {Nation}."* + recommendation only.

**Recommendation logic:** Pick the highest-likelihood available proposal action. Tiers:
- Favorable+ likelihood → recommend that action: *"Talleyrand recommends: Propose Armistice"*
- All Doubtful/Unlikely → strategic advice: *"Relations must improve before proposals will find purchase. A battlefield victory would change their calculus."*
- 0 DP → resource advice: *"Our diplomatic reserves are spent. We must wait."*
- Vassal low loyalty → *"Talleyrand recommends: Invest to strengthen loyalty"*

---

## §4. Validation Hardening (Companion Work)

The wizard guarantees only valid actions are shown. But typed commands bypass the wizard. These executor-level validation gaps must be fixed so BOTH paths are safe:

### 4a. Proposal for Current/Lower State — FIX

**Problem:** Player can type `"propose peace with Austria"` when already at PEACE. DP spent, fails silently at acceptance.

**Fix in `executor.py (_execute_diplomatic_proposal)`:**
```python
# Before DP deduction, check proposal isn't at/below current state
current_state = world.get_diplomatic_state(world.player_nation, target)
if target_state in _UPGRADE_ORDER and current_state in _UPGRADE_ORDER:
    if _UPGRADE_ORDER.index(target_state) <= _UPGRADE_ORDER.index(current_state):
        return {"success": False,
                "message": f"We already have {display_state} with {target}. "
                           f"Talleyrand sees no purpose in proposing what we already possess."}
```

### 4b. Ultimatum Cooldown — FIX

**Problem:** No cooldown on ultimatums. Player can spam ultimatums every turn.

**Fix:** Add `ultimatum_cooldowns` dict to WorldState (same pattern as proposal cooldowns). 5-turn cooldown per target nation. Serialize in to_dict/from_dict.

### 4c. Break Treaty Without Treaty — IMPROVE

**Problem:** `_execute_diplomatic_break` defers to diplomacy layer which returns generic error.

**Fix:** Pre-validate in executor with Talleyrand-voiced message:
```
"There is no treaty with [Nation] to break, Your Excellency."
```

### 4d. Downgrade at Minimum State — IMPROVE

**Problem:** `_execute_diplomatic_downgrade` defers to diplomacy layer for minimum-state check.

**Fix:** Pre-validate in executor:
```
"Our relations with [Nation] are already at their most basic level."
```

### 4e. Declare War During Armistice — IMPROVE

**Problem:** Blocked by diplomacy layer but error message doesn't say how many turns remain.

**Fix:** Include remaining cooldown turns in executor message:
```
"The armistice with [Nation] holds for [N] more turns. We cannot declare war until it expires."
```

---

## §5. Implementation Plan

### 5a. Backend

| Task | File | Est. |
|------|------|------|
| `GET /diplomatic_preview` endpoint | `main.py` | 30 min |
| `get_available_diplomatic_actions()` helper | `diplomacy.py` | 45 min |
| `get_likelihood_descriptor()` word mapper | `diplomacy.py` | 15 min |
| Assessment template system (15 templates + fallback) | `diplomacy.py` or new `assessment_templates.py` | 30 min |
| §4a: Proposal state pre-check | `executor.py` | 15 min |
| §4b: Ultimatum cooldown + serialization | `executor.py`, `world_state.py` | 30 min |
| §4c-4e: Error message improvements | `executor.py` | 20 min |
| Tests | `tests/test_diplomacy_button.py` | 60 min |

### 5b. Godot

| Task | File | Est. |
|------|------|------|
| [Diplomacy] button in InputSection | `main.tscn`, `main.gd` | 20 min |
| F1 hotkey wiring (both focus modes) | `main.gd` | 15 min |
| Nation selection popup scene | `diplomacy_wizard.gd/.tscn` | 45 min |
| Action selection popup (dynamic buttons + assessment panel) | `diplomacy_wizard.gd` | 60 min |
| Vassal assessment panel (loyalty bar, trend, tribute) | `diplomacy_wizard.gd` | 20 min |
| `get_diplomatic_preview()` in api_client | `api_client.gd` | 10 min |
| Likelihood color mapping | `diplomacy_wizard.gd` | 15 min |
| Edge case displays (0 DP, all cooldowns) | `diplomacy_wizard.gd` | 15 min |
| Integration with existing command flow | `main.gd` | 20 min |

### 5c. Scope

- **Backend:** ~4 hours (including tests + validation fixes + templates)
- **Godot:** ~3.5 hours
- **Total:** ~1 session (tight). If Godot popups run long, split: Session A = backend + validation + tests, Session B = Godot wizard UI.

---

## §6. Scalability Note

Current game has 5 nations (4 non-player). The wizard handles this trivially — Step 1 shows 4 buttons max. If nations are added via modding or DLC:

- **6-8 nations:** Still fine as flat button list
- **9+ nations:** Switch Step 1 to categorized sections: "At War (2)" / "Allied (1)" / "Vassals (3)" / "Neutral (4)" — each collapsible. Not needed now, but the popup layout should use a VBoxContainer that can accept section headers later.

Vassal management scales the same way — each vassal is one nation in the list, clicked individually. No bulk management needed.

---

## §7. What This Does NOT Change

- No new diplomatic mechanics — wizard builds commands the backend already understands
- Typed commands still work — wizard supplements, never replaces
- No new diplomatic states or transitions
- No LLM dependency — wizard is entirely deterministic
- Existing conversational dialogue flow unchanged — wizard hands off to it
- Mock mode works identically — same command strings

---

## §8. Design Decisions (Resolved March 8, 2026)

1. **Button text:** "Diplomacy" — clear and functional.
2. **Assess Relations:** Not a separate action. Talleyrand's assessment is always visible at the top of the action popup (§2a) — free, always shown, no click needed.
3. **Action sections:** Two sections in the popup — **Foreign Affairs** (proposals, war, treaties) and **Vassal Management** (invest, autonomy, release). Section shown depends on whether the nation is a vassal.
4. **Likelihood words:** Unified across all systems. Same word scale in wizard, R118 acceptance preview, and any future likelihood display. Single source function in `diplomacy.py`.
