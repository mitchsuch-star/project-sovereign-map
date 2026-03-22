# Diplomacy Design Audit — March 2026

**Date:** 2026-03-22
**Methodology:** 4 parallel code-review agents + manual verification of every finding against codebase.
**Previous audit:** `DIPLOMACY_AUDIT_2026_03.md` (code bugs, 43 found/fixed, 112 tests).
**This audit:** Design-level issues — AI behavior, UX feedback, missing features.

> **Review outcome:** 30 original findings reviewed → 17 retracted (factually wrong, overstated, or intentional asymmetries). **12 confirmed issues + 4 new features** organized into 4 implementation sessions.

---

## AI BEHAVIOR (4 findings)

### A1. AI Discards Winning Proposals Instead of Negotiating Down
**PRIORITY: HIGH**
`ai_diplomacy.py:654-670`

P8 (winning, war_score > 40) builds harsh peace with gold demands, checks acceptance score < 20, and silently returns `None`. No retry with softer terms. The player never faces "accept terms or keep fighting" ultimatums when losing.

**EU4 comparison:** EU4 AI aggressively demands provinces, gold, and vassalization when winning. Demands scale with war score — the AI always sends SOMETHING.

**Fix:** When P8 acceptance < 20, enter iterative demand reduction:
1. Halve gold demand, re-check acceptance
2. If still < 20, drop weakest non-gold clause, re-check
3. Up to 2 retries total
4. If nothing scores > 20 after retries, fall back to minimal "white peace + 200g" demand
5. The player should ALWAYS receive demands when losing badly

### A2. AI Ignores Coalition Membership When Proposing Peace
**PRIORITY: HIGH**
`ai_diplomacy.py:596-607`

P1 (losing badly, war_score < -40) proposes peace without checking coalition membership. Coalition members can unilaterally defect mid-war with zero strategic calculation.

**EU4 comparison:** EU4 coalition members cannot sign separate peace — only the war leader can. Your system intentionally allows separate peace (§6a), which is more interesting, but AI should resist defection.

**Fix:** In P1, before proposing peace, check `is_coalition_member(nation, world)`. If true, block peace proposals unless:
- War score < -50 (getting thoroughly beaten — correlates with heavy troop losses), OR
- War exhaustion > 80, OR
- War has lasted 8+ turns AND war_score < -60

War score is used as a proxy for troop losses since it directly reflects battle outcomes. No new tracking fields needed — `get_war_score_for()` and `war_exhaustion` already exist. This makes coalition members fight until desperate rather than defecting at the first setback.

### A4. Harsh Peace Gold Formula Produces Unreachable Demands
**PRIORITY: MODERATE**
`ai_diplomacy.py:465-469`

Formula: `gold_demand = max(500, int(war_score * 8 * gold_mult))`. The 500g floor is too high — it generates ~-16 acceptance penalty which, combined with other factors, almost always pushes total below the score < 20 rejection threshold. Root cause of A1 — even with iterative reduction, the starting point is too harsh.

**Fix:** Lower floor and multiplier: `gold_demand = max(200, int(war_score * 5 * gold_mult))`. This produces achievable demands that the A1 iterative loop can work with.

### A3. War Exhaustion Not Factored Into AI Proposal Timing
**PRIORITY: LOW**
`coalition.py:465-478`, `ai_diplomacy.py` P1-P8

War exhaustion accumulates and affects acceptance formula, but AI decision triggers (P1-P8) don't reference it. AI can't anticipate "my WE is high, peace proposals will be more acceptable."

**Fix:** In P1, lower the war_score threshold by `WE // 20` (high exhaustion makes AI propose peace earlier). In P2, reduce stalemate patience by `max(2, base_patience - WE // 30)` turns (floor of 2 prevents zero/negative patience at extreme WE). ~5 lines.

---

## NEW FEATURES (3 findings)

### N1. AI-AI Preemptive Alliances Against Rising Threat
**PRIORITY: HIGH**
`ai_diplomacy.py:1392-1451` (`_evaluate_ai_ai_proposal`)

**Current state:** AI-AI alliances only form when both nations are already at war with France (Trigger 1, line 1418). There is no peacetime "threat is rising, let's band together" trigger. The diplomatic landscape is static until the coalition threshold at 60.

Note: P3 at lines 615-628 is a separate system — it handles AI nations proposing alliances **to France** (bandwagoning). What's missing is AI nations allying **with each other against** France.

**EU4 comparison:** EU4 AI actively forms defensive networks when a neighbor becomes threatening. Nations seek alliances BEFORE being attacked, creating a diplomatic web the player must navigate. You can't just pick off isolated nations because they won't stay isolated.

**Design:**

Add **Trigger 5** to `_evaluate_ai_ai_proposal()`:

```
Trigger 5: Preemptive Alliance Against Threat
  Conditions (ALL must be true):
    - world.threat_level > 40 (Murmurs tier — France is visibly aggressive)
    - Neither nation is at war with France (peacetime alliance-building)
    - Neither nation has a treaty with France (NON_AGGRESSION or higher)
    - Both nations have relation with France < 0 (both wary of France)
    - Mutual relation between the two nations > -10 (can work together)
    - Current state between them is not already DEFENSIVE_ALLIANCE or ALLIANCE
  Result: Propose DEFENSIVE_ALLIANCE between the two AI nations
```

**Pacing:** At threat 40, nations start forming alliances. At threat 60, coalition brewing begins. This creates a ~20-threat window where the player sees nations allying against them and must decide: moderate expansion, or push through and face a pre-allied coalition.

**Rate limiting:** Uses existing AI-AI infrastructure:
- 5-turn per-pair cooldown (`ai_ai|{diplo_key}`)
- 2-per-turn max (`_AI_AI_MAX_TREATIES_PER_TURN`)
- Existing acceptance check (`_ai_ai_acceptance >= 50` from both sides)

**Dispatch integration:** When Trigger 5 fires and a treaty is ratified, the existing AI-AI treaty dispatch event fires. Player sees in morning dispatch: "Austria and Prussia have signed a defensive pact."

**Implementation:** ~15 lines added to `_evaluate_ai_ai_proposal()` after Trigger 4. Insert before the `return None`:

```python
# Trigger 5: Preemptive alliance when French threat rising (N1)
# Only nations without treaties with France should form anti-French alliances.
threat = int(getattr(world, 'threat_level', 0))
if threat > 40:
    player = getattr(world, 'player_nation', 'France')
    rel_a_france = world.nation_relations.get(world._make_diplo_key(nation_a, player), 0)
    rel_b_france = world.nation_relations.get(world._make_diplo_key(nation_b, player), 0)
    # Block if either nation has a positive treaty with France (NON_AGGRESSION+)
    _treaty_states = ("NON_AGGRESSION", "OPEN_BORDERS", "DEFENSIVE_ALLIANCE", "ALLIANCE")
    if (rel_a_france < 0 and rel_b_france < 0
            and relation_ab > -10
            and state_ab not in ("DEFENSIVE_ALLIANCE", "ALLIANCE")
            and state_a_france not in ("WAR",) + _treaty_states
            and state_b_france not in ("WAR",) + _treaty_states):
        return {"type": "defensive_alliance", "proposer": nation_a, "target": nation_b}
```

**Test cases:**
- Trigger fires at threat 41 with correct conditions → DEFENSIVE_ALLIANCE proposed
- Trigger blocked when one nation has positive relation with France
- Trigger blocked when either nation has a treaty with France (NON_AGGRESSION+)
- Trigger blocked when nations already have DA/ALLIANCE
- Trigger blocked when either at war with France (falls to Trigger 1 instead)
- Trigger respects per-pair cooldown
- Trigger respects 2-per-turn max
- Integration: threat rises from 35→45, next turn AI-AI alliance forms

### N2. Offensive Alliance Calling on War Declaration
**PRIORITY: MODERATE**
`diplomacy.py:1085-1156` (`_process_war_cascade`)

**Current state:** When Nation A declares war on Nation B, nations allied with **B** (the defender) auto-join against A. But nations allied with **A** (the aggressor) don't join. ALLIANCE is described in the spec as "offensive + defensive" (`DIPLOMACY_SPEC §5a`) but only the defensive half is coded.

**EU4 comparison:** EU4 offensive wars call allied nations, who can accept (join war) or refuse (alliance breaks, relation penalty). This makes alliances a two-way commitment.

**Design: Aggressor Cascade**

Expand `_process_war_cascade()` to also check the **aggressor's** allies. When the aggressor declares war:

1. **Defensive cascade (existing):** Nations with DA/ALLIANCE with the TARGET join war against the aggressor.
2. **Offensive cascade (new):** Nations with ALLIANCE (not DA) with the AGGRESSOR join war against the target.

This creates a clean mechanical distinction:
- **DEFENSIVE_ALLIANCE:** "I defend you if attacked" (defensive cascade only)
- **ALLIANCE:** "I defend you AND attack with you" (both cascades)

**Implementation in `_process_war_cascade()`:**

Add a second pass after the existing defensive loop:

```python
# ── OFFENSIVE CASCADE: Aggressor's ALLIANCE partners join against target ──
# Only ALLIANCE (not DEFENSIVE_ALLIANCE) triggers offensive calling.
# Skip vassals — they auto-join overlord's wars via separate path.
for nation in all_nations:
    if nation in processed:
        continue
    if nation in getattr(world, 'vassals', {}):
        continue  # Vassal auto-join handled elsewhere

    state_with_aggressor = world.get_diplomatic_state(nation, aggressor)
    if state_with_aggressor == "ALLIANCE":
        if not world.is_at_war(nation, target):
            war_key = world._make_diplo_key(nation, target)
            world.diplomatic_states[war_key] = "WAR"

            # Mirror defensive cascade post-processing (lines 1108-1150):
            # 1. Record war start turn
            cascade_war_starts = getattr(world, 'war_start_turns', {})
            cascade_war_starts[war_key] = int(world.current_turn)
            world.war_start_turns = cascade_war_starts
            # 2. Remove active treaty between cascaded nation and target
            active_treaties = getattr(world, 'active_treaties', {})
            active_treaties.pop(war_key, None)
            # 3. Relation penalty: cascaded nation → target
            world.modify_nation_relation(nation, target, -20)

            processed.add(nation)
            cascade.append({
                "attacker_ally": nation,
                "aggressor": aggressor,
                "target": target,
                "cascade_type": "offensive",
            })

            # 4. Notification
            world.notifications.add(create_notification(
                ALLIANCE_CASCADE_WAR, NotificationPriority.HIGH,
                f"{nation} Joins Offensive!",
                f"{nation} enters the war against {target}, honoring alliance with {aggressor}.",
                int(world.current_turn),
            ))
            # 5. Dispatch event
            queue_dispatch_event(world, "offensive_cascade",
                                {"nation": nation, "aggressor": aggressor, "target": target},
                                "partial_on_nation")

            # Recursive: nation's allies may also cascade
            sub_cascade = _process_war_cascade(world, nation, target, processed)
            cascade.extend(sub_cascade)
```

**Alliance paradox extension:** The existing paradox check (lines 990-1035) must be expanded. Currently it checks if the player is allied with both aggressor and target. Now it must also check: if the player has ALLIANCE with the aggressor but also DA/ALLIANCE with the target, a paradox occurs. The existing popup structure handles this — just expand the condition check.

**Relation penalties for offensive cascade:**
- Cascaded nation → target: -20 relation (same as defensive cascade)
- Offensive cascade is involuntary — the ally is pulled in by treaty obligation

**Dispatch integration:** New dispatch event template:
- `"offensive_cascade"`: "[Nation] has joined [aggressor]'s war against [target], honoring their alliance."

**Edge cases:**
- **Recursive offensive:** If Saxony is pulled into France's war against Austria, and Saxony has ALLIANCE with Bavaria, Bavaria is also pulled in. Uses existing recursive cascade with `processed` set for loop protection.
- **Cross-cascade:** France attacks Austria. Prussia (ALLIANCE with France) is pulled in offensively. Britain (DA with Austria) is pulled in defensively. Both cascades use the same `processed` set — no double-counting.
- **Vassal nations:** Vassals already auto-join their overlord's wars. Offensive cascade should skip vassals to avoid duplicate entries.

**Test cases:**
- France (ALLIANCE with Saxony) declares war on Austria → Saxony enters war against Austria
- France (DEFENSIVE_ALLIANCE with Saxony) declares war on Austria → Saxony does NOT enter war (DA is defense-only)
- Offensive cascade respects `processed` set — no infinite loops
- Offensive + defensive cascades in same declaration work correctly
- Alliance paradox: player has ALLIANCE with both aggressor and target → popup, player chooses
- Vassal not double-cascaded
- Recursive offensive cascade (ally's ally pulled in)

### N3. Coalition Friction in Attack Coordination
**PRIORITY: LOW**
`enemy_ai.py:2177-2180`, `coalition.py:409-426`

**Current state:** Coalition friction (0.25-1.0 based on mutual relation) only affects the P4.75 ally-support movement bonus (`enemy_ai.py:5268-5272`). The P4 attack scoring has a coordination estimate (+8% per co-located ally, line 2177) but the co-location check (`enemy_ai.py:2125-2130`) only counts **same-nation** allies (`a.nation == nation`). Cross-nation coalition allies in the same region contribute **zero** to the attack decision — they're excluded entirely, not just unmodulated.

**EU4 comparison:** EU4 coalition members coordinate poorly in practice — they often occupy each other's war goals and fight separately. Your friction system is a better abstraction but needs wider application.

**Design:** Expand the co-location check to include cross-nation allies, then modulate their bonus by friction. Same-nation allies keep full `+8%`. Cross-nation allies get `+8% * friction`.

**Implementation in `_find_attack_opportunity()` at line 2177:**

Replace the current flat bonus:

```python
# Current (line 2177-2180):
if co_located_ally_count > 0:
    effective_ratio += 0.08 * co_located_ally_count

# New: Friction-modulated coordination
if co_located_ally_count > 0:
    coord_bonus = 0.0
    for ally_marshal in co_located_allies:
        if ally_marshal.nation != nation:
            friction = get_coalition_friction(ally_marshal.nation, nation, world)
            coord_bonus += 0.08 * friction
        else:
            coord_bonus += 0.08  # Same-nation allies: full bonus
    effective_ratio += coord_bonus
```

This requires two changes at the co-location check (`enemy_ai.py:2125-2130`):
1. **Expand filter:** Remove `a.nation == nation` to include cross-nation allies
2. **Store list:** Replace `len([...])` with a stored list so we can iterate marshals for per-nation friction lookup

**Effect on gameplay:**
- Coalition members at relation +30: full +8% per ally (friction 1.0)
- Coalition members at relation 0-29: +6% per ally (friction 0.75)
- Coalition members at relation -20 to -1: +4% per ally (friction 0.5)
- Coalition members at relation < -20: +2% per ally (friction 0.25)

Low-friction coalitions are weaker in coordinated attacks, incentivizing the player to drive wedges between coalition members diplomatically.

**Test cases:**
- Same-nation allies always get full +8% (friction not applied)
- Cross-nation allies at relation +30 get full +8%
- Cross-nation allies at relation -25 get +2% (0.25 friction)
- Mixed: 1 same-nation + 1 cross-nation at low relation → correct split bonus
- Non-coalition cross-nation allies (shouldn't exist, but guard against)

### N4. War Status Panel (Bottom-Right HUD)
**PRIORITY: HIGH**
`NEW — No existing implementation`

**Current state:** Active wars are only visible in the Diplomatic Ledger (D key → Nations tab), buried alongside all nation relationships. There's no at-a-glance indicator of ongoing wars, war scores, or quick access to peace actions. The player must open a full screen to see war status.

**EU4 comparison:** EU4 shows war shield icons in the bottom-right corner. Each icon represents an active war with a colored war score bar. Clicking opens a war overview with: score breakdown, participants on each side, battle history, and a "Sue for Peace" button. Wars are always visible — you never forget you're fighting someone.

**Design: Persistent War Status Panel**

A compact always-visible panel anchored to the bottom-right corner showing all active wars. Clicking a war opens the diplomacy wizard pre-targeted to that nation for peace actions.

**Layout:**

```
                                          ┌─────────────────────┐
                                          │  ⚔ ACTIVE WARS      │
                                          ├─────────────────────┤
                                          │ ■ Britain    +35    │
                                          │ ████████░░░  T:8    │
                                          ├─────────────────────┤
                                          │ ■ Prussia    -12    │
                                          │ ░░░████████  T:3    │
                                          └─────────────────────┘
                                                    Bottom-right
```

Each war card shows:
- **Nation color swatch** (■) + nation name
- **War score** as number (+35 = winning, -12 = losing) + colored bar
- **Duration** (T:8 = 8 turns at war)
- **Click** → opens diplomacy wizard (F1) pre-focused on that nation

When no wars are active, the panel hides entirely (no empty frame).

**Godot Architecture:**

| Component | Detail |
|-----------|--------|
| **Scene** | `war_status_panel.tscn` — PanelContainer anchored bottom-right |
| **Script** | `war_status_panel.gd` |
| **Layer** | CanvasLayer 25 (above map at 0, below screens at 50) |
| **Position** | `anchor_right=1, anchor_bottom=1`, offset from corner by 10px. Above the terminal's restore button area |
| **Visibility** | Hidden when: no active wars, OR any layer-50 screen is open, OR any modal dialog is open |
| **Update trigger** | Refreshes on every command response + turn start (same data flow as top bar) |

**Scene tree structure:**

```
WarStatusPanel (CanvasLayer, layer=25)
  └─ PanelContainer (anchored bottom-right)
      └─ VBoxContainer
          ├─ HeaderLabel ("⚔ ACTIVE WARS")
          ├─ WarCard_0 (HBoxContainer, clickable)
          │   ├─ ColorRect (nation color, 12x12)
          │   ├─ VBoxContainer
          │   │   ├─ HBoxContainer
          │   │   │   ├─ NationLabel ("Britain")
          │   │   │   └─ ScoreLabel ("+35", green/red based on sign)
          │   │   └─ HBoxContainer
          │   │       ├─ ScoreBar (ProgressBar, 0-100, green left / red right)
          │   │       └─ DurationLabel ("T:8")
          │   └─ (clickable area → emit war_clicked(nation))
          ├─ WarCard_1 ...
          └─ ...
```

**Styling** (matches existing UI):
- Dark panel background (`Color(0.08, 0.08, 0.12, 0.9)`)
- Gold border (`Color(0.85, 0.7, 0.3)`)
- Score color: green (#4a4) when positive, red (#a44) when negative, white at 0
- Bar: two-tone — green fills from center-left (player winning), red fills from center-right (enemy winning)
- Nation color swatch uses existing nation colors from `map.gd`
- Max width: ~200px. Cards stack vertically. Max 4 visible (scroll if more, unlikely)

**Backend: New endpoint `GET /active_wars`:**

```python
@app.get("/active_wars")
def get_active_wars():
    """Lightweight endpoint for war status panel. Returns only active wars."""
    world = game_state.get("world")
    if not world:
        return {"wars": []}

    france = world.player_nation
    wars = []
    for key, state in world.diplomatic_states.items():
        if state != "WAR":
            continue
        nations = key.split("|")
        if france not in nations:
            continue
        opponent = nations[0] if nations[1] == france else nations[1]
        diplo_key = world._make_diplo_key(france, opponent)

        war_score = get_war_score_for(world, france, opponent)
        started = world.war_start_turns.get(diplo_key, 0)
        duration = int(world.current_turn) - started

        wars.append({
            "opponent": opponent,
            "war_score": int(war_score),
            "duration": int(duration),
        })

    return {"wars": wars}
```

Alternatively, include `active_wars` in the existing `/state` response to avoid an extra HTTP call. The data is tiny (~3 fields per war) and the panel updates on every command response anyway.

**Godot: Click → Diplomacy Wizard handoff:**

When a war card is clicked, emit `war_clicked(nation_name)` signal. In `main.gd`:

```gdscript
func _on_war_clicked(nation: String):
    # Open diplomacy wizard pre-focused on this nation
    # Wizard already supports nation pre-selection via step 2 direct open
    diplomacy_wizard.open_for_nation(nation)
```

The diplomacy wizard already has a two-step flow: step 1 (nation list) → step 2 (actions for nation). Add an `open_for_nation(nation)` method that skips step 1 and goes directly to step 2 with the war nation selected. The wizard's step 2 already shows: "Propose Armistice", "Propose Peace", war score, Talleyrand's assessment.

**Integration with screen system:**

- Register with `main.gd` (NOT with top_bar — it's a persistent HUD, not a toggleable screen)
- `main.gd` connects `top_bar.screen_changed` to show/hide the war panel
- Panel hides when any screen is open: `war_status_panel.visible = !top_bar.is_screen_open()`
- Panel hides when modal dialogs are open (check `_is_modal_dialog_open()`)

**Armistice display:** When a nation is in ARMISTICE (not WAR), show a different card style:

```
│ ■ Austria  ⚖ ARMISTICE │
│ 3 turns remaining       │
```

Armistice cards are grayed out, not clickable (no actions available during armistice). Show turns remaining until peace (5 - armistice_turns). Include armistice nations so the player sees the full war picture.

**Test cases (backend):**
- `/active_wars` returns empty list when no wars
- Returns correct opponent, war_score, duration for each active war
- War score sign is from France's perspective (positive = winning)
- All numbers are `int()` (Godot golden rule)
- Armistice nations included with armistice data
- Eliminated nations excluded (0 regions + 0 marshals)

**Test cases (Godot — manual):**
- Panel appears when war starts, disappears when all wars end
- Panel hides when D/T/L/G/R screens are open
- Panel hides when modal dialogs are open
- Click war card → diplomacy wizard opens on that nation
- War score updates after battles
- Duration increments each turn
- Armistice card shows correctly after signing armistice
- Panel handles 1, 2, 3, 4 simultaneous wars without overflow

---

## UX FEEDBACK (6 findings, 1 retracted)

### S1. DP Regeneration Is Silent
**PRIORITY: HIGH**
`diplomacy.py:1486-1518`

DP resets every turn. No notification of how much was generated or what factors contribute. If player loses capital (-1 DP/turn), they discover it by noticing the counter changed.

**Fix:** Add morning dispatch line via `queue_dispatch_event()`: "Talleyrand reports: [X] diplomatic points available (base 3, +1 skill, +1 authority, -1 no capital)."

**Implementation note:** `calculate_dp()` currently returns a single `int`. To produce the breakdown, replicate the component logic inline in `_process_dp_regen()` for the player nation only (base 3, skill_bonus, authority_bonus, capital_penalty are all computed there already before calling `calculate_dp()`). Pass the breakdown as template vars to the dispatch event. No need to refactor `calculate_dp()` itself — the 4-line calculation is simple enough to inline.

### S2. Significant Relation Changes Have No Dispatch Events
**PRIORITY: HIGH**
`coalition.py:624`, `diplomacy.py:2051-2074`

Relations can shift from coalition penalties, reliability decay, or treaty-breaking cascades with zero player-facing explanation. Player sees nations become hostile with no context.

**Fix:** After `modify_nation_relation()` calls that produce large swings (≥ ±10 cumulative in a turn), fire a dispatch event: "Relations with [nation] have [worsened/improved] due to [reason]."

**Implementation:** Add a transient dict `_relation_deltas_this_turn: Dict[str, int]` on WorldState (no serialization — cleared at turn start in `advance_turn()`). In `modify_nation_relation()`, accumulate: `self._relation_deltas_this_turn[nation] += amount`. At end of turn processing (after all modifications), iterate the dict, fire dispatch for any nation with `abs(delta) >= 10`. Filter via existing fog rules (`partial_on_nation`).

### S4. War Exhaustion Not Displayed
**PRIORITY: MODERATE**
`coalition.py`, `diplomatic_ledger.py`

War exhaustion affects acceptance formula but appears only as a per-member number buried in the coalition tab. No trend, no explanation, no dispatch mention.

**Fix:** (a) Add WE trend indicator to coalition tab (rising/stable/falling based on last turn delta). (b) Add dispatch line when WE crosses thresholds (20, 40, 60, 80): "War exhaustion grows among the coalition — [nation] grows weary of the fight."

**Threshold dispatch cooldown:** Track `_last_we_dispatch_threshold: Dict[str, int]` (transient, no serialization). Only fire dispatch when a nation's WE crosses a threshold it hasn't dispatched for yet. Example: WE goes from 18→22 (crosses 20, dispatch fires, stores 20). Next turn WE is 25 (still above 20 but below 40, no new dispatch). WE reaches 41 (crosses 40, new dispatch). Reset tracking when coalition dissolves.

### S5. Threat Projection Missing
**PRIORITY: MODERATE**
`diplomatic_ledger.py:394-410`

Ledger shows current threat and this-turn sources but no projection. Player must do mental math.

**Fix:** Add to coalition tab: "Next war declaration: +20 threat (→ [projected]). Brewing at 60. Instant at 80." Simple arithmetic from current threat value. ~10 lines in `diplomatic_ledger.py`.

### ~~U1. Acceptance Component Labels Missing for Military Factors~~
**RETRACTED** — All three keys (`military_supremacy`, `battlefield_diplomacy`, `military_pressure`) already have entries in both `_COMPONENT_LABELS` (lines 2626-2628) and `FEEDBACK_STRINGS` (lines 192+). No change needed.

### U2. Wizard vs Terminal Show Different Blocking Reasons
**PRIORITY: LOW**
`diplomacy.py:2433`

Wizard shows "Insufficient DP" when armistice is the real blocker. Terminal correctly shows "Armistice: X turns remaining."

**Fix:** In wizard disabled-reason logic, check armistice cooldown BEFORE DP check. Return armistice reason when active.

### S3. Vassal Loyalty Warning Threshold Could Be Earlier
**PRIORITY: LOW**
`vassal.py:761-789`, `dispatch.py:601-619`

`vassal.py` already fires warnings at <40 (warning), <20 (urgent), <10 (critical) — these appear in the strategic ledger. But the **morning dispatch** (`dispatch.py:607`) only triggers at loyalty < 20. A vassal at 45 losing -6/turn gets no dispatch warning until loyalty drops below 20.

**Fix:** Add "concern" tier at loyalty < 35 in dispatch: "Talleyrand notes growing discontent in [vassal]." Severity: info (not warning). This bridges the gap between the ledger's <40 tier and the dispatch's current <20 tier.

---

## IMPLEMENTATION PLAN

### Session DA-1: AI Diplomatic Intelligence (Backend Only)
**Scope:** 5 items, ~80-100 tests estimated
**Prerequisite:** None — all fixes are in existing code paths

| # | Item | Files | Complexity |
|---|------|-------|------------|
| A4 | Fix gold demand formula (floor 200, mult 5) | `ai_diplomacy.py` | Small — 2 lines |
| A1 | Iterative demand reduction loop for P8 | `ai_diplomacy.py` | Medium — new function, ~30 lines |
| A2 | Coalition loyalty check before P1 peace | `ai_diplomacy.py` | Small — ~15 lines guard clause |
| A3 | WE modifier on P1/P2 thresholds | `ai_diplomacy.py` | Small — ~5 lines |
| N1 | AI-AI preemptive alliances (Trigger 5) | `ai_diplomacy.py` | Small — ~15 lines in `_evaluate_ai_ai_proposal` |

### Session DA-2: Player Feedback & UX (Backend + Minor Godot)
**Scope:** 6 items, ~30-40 tests estimated
**Prerequisite:** None

| # | Item | Files | Complexity |
|---|------|-------|------------|
| S1 | DP regen dispatch event | `diplomacy.py`, `dispatch.py` | Small |
| S2 | Significant relation change dispatch | `diplomacy.py`, `coalition.py`, `dispatch.py` | Medium |
| S4 | War exhaustion display + dispatch | `diplomatic_ledger.py`, `dispatch.py` | Small |
| S5 | Threat projection in ledger | `diplomatic_ledger.py` | Small |
| U2 | Wizard armistice reason priority | `diplomacy.py` | Small |
| S3 | Vassal loyalty warning at 35 | `dispatch.py` | Small |

### Session DA-3: Offensive Alliance Cascade (Backend + Godot Popup)
**Scope:** 2 items, ~40-60 tests estimated
**Prerequisite:** DA-1 (N1 creates alliances that N2 makes meaningful offensively)

| # | Item | Files | Complexity |
|---|------|-------|------------|
| N2 | Offensive alliance cascade in `_process_war_cascade` | `diplomacy.py`, `dispatch.py` | Medium — ~30 lines + paradox extension |
| N3 | Friction in P4 attack coordination | `enemy_ai.py` | Small — ~15 lines, refactor co_located count to list |

**Dependency:** N2 makes ALLIANCE strictly better than DEFENSIVE_ALLIANCE (defense + offense vs defense-only). N1 creates AI-AI **defensive** alliances at threat 40 — these don't trigger offensive cascade directly. However, existing Trigger 3 (relation > 40, both at peace) upgrades treaties one step, so DA→ALLIANCE upgrades happen naturally over time. Together: N1 seeds the alliance network, Trigger 3 upgrades some to full ALLIANCE, and N2 makes those full alliances pull nations into offensive wars. N2 is also independently valuable for any existing ALLIANCE relationships (e.g., player-created alliances that later break).

### Session DA-4: War Status Panel (Backend + Godot)
**Scope:** 1 feature (N4), ~15-20 backend tests + manual Godot testing
**Prerequisite:** None (can run in parallel with DA-1/DA-2)

| # | Item | Files | Complexity |
|---|------|-------|------------|
| N4a | Backend: `GET /active_wars` endpoint (or embed in `/state`) | `main.py`, `diplomacy.py` | Small — ~25 lines |
| N4b | Godot: `war_status_panel.tscn` + `.gd` — persistent bottom-right HUD | New scene + script | Medium — new CanvasLayer 25 scene, war card rendering, click handling |
| N4c | Godot: Click → diplomacy wizard handoff | `diplomacy_wizard.gd`, `main.gd` | Small — add `open_for_nation()` method, connect signal |
| N4d | Godot: Screen/modal visibility integration | `main.gd` | Small — hide panel when screens/modals open |

**This is a Godot-heavy session.** Backend is ~25 lines. Godot work is: new scene, new script, styling, signal wiring, visibility logic, wizard integration. Estimate ~200 lines of GDScript.

---

## Summary

| Category | Items | Sessions |
|----------|-------|----------|
| AI behavior fixes (A1-A4) | 4 | DA-1 |
| New feature: preemptive alliances (N1) | 1 | DA-1 |
| UX feedback (S1-S5, U2) | 6 | DA-2 |
| New feature: offensive cascade (N2) | 1 | DA-3 |
| Enhancement: friction in attacks (N3) | 1 | DA-3 |
| New feature: war status panel (N4) | 1 | DA-4 |
| **Total** | **14** | **4 sessions** |

### Session Dependencies

```
DA-1 (AI intelligence) ──→ DA-3 (offensive cascade)
DA-2 (UX feedback)     ──→ (none)
DA-4 (war panel)        ──→ (none)
```

DA-1 and DA-2 and DA-4 can all run in parallel. DA-3 depends on DA-1.

### Priority Ranking

1. **A1 + A4** (DA-1): AI can't demand terms when winning. Biggest single gap.
2. **A2** (DA-1): Coalition members defect too easily. Undermines coalition threat.
3. **N1** (DA-1): Static diplomatic landscape until coalition threshold.
4. **N4** (DA-4): Wars invisible without opening full screen. Core EU4-style UX gap.
5. **S1 + S2 + S4** (DA-2): Silent systems cause player confusion.
6. **N2** (DA-3): ALLIANCE has no offensive benefit over DEFENSIVE_ALLIANCE.
7. **N3, S3, S5, U2** (DA-2/3): Polish and enhancement.
