# Diplomacy Design Audit — March 2026

**Date:** 2026-03-22
**Methodology:** 4 parallel code-review agents + manual verification of every finding against codebase.
**Previous audit:** `DIPLOMACY_AUDIT_2026_03.md` (code bugs, 43 found/fixed, 112 tests).
**This audit:** Design-level issues — AI behavior, UX feedback, missing features.

> **Review outcome:** 30 original findings reviewed → 17 retracted (factually wrong, overstated, or intentional asymmetries). **14 confirmed items** (10 fixes + 4 new features) organized into 4 implementation sessions.
>
> **Progress:** DA-1 COMPLETE (5 items, 79 tests). DA-2 COMPLETE (6 items, 37 tests). **2 sessions remaining (DA-3, DA-4).**

---

## AI BEHAVIOR (4 findings)

### A1. AI Discards Winning Proposals Instead of Negotiating Down
**PRIORITY: HIGH**
`ai_diplomacy.py:654-670`

P8 (winning, war_score > 40) builds harsh peace with gold demands, checks acceptance score < 20, and silently returns `None`. No retry with softer terms. The player never faces "accept terms or keep fighting" ultimatums when losing.

**EU4 comparison:** EU4 AI aggressively demands provinces, gold, and vassalization when winning. Demands scale with war score — the AI always sends SOMETHING.

**Fix:** Insert iterative reduction **inside the P8 block** (after `_make_proposal` at line 658, before the proposal reaches the global score < 20 filter at line 669). The loop calls `calculate_acceptance()` locally on the P8 proposal:
1. Halve gold demand, re-check acceptance
2. If still < 20, drop weakest non-gold clause, re-check
3. Up to 2 retries total
4. If nothing scores > 20 after retries, fall back to minimal "white peace + 200g" demand and set `proposal["_force_send"] = True`
5. The global score < 20 check (line 669) must respect the flag: `if score < 20 and not proposal.get("_force_send"): return None`
6. The player should ALWAYS receive demands when losing badly — the `_force_send` flag guarantees this

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

    # Skip player if alliance paradox popup is pending (they choose manually)
    if nation == world.player_nation and has_paradox:
        continue

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

**Alliance paradox extension:** The existing paradox check (lines 990-1035) must be expanded. Currently it checks if the player is allied with both aggressor and target. Now it must also check: if the player has ALLIANCE with the aggressor but also DA/ALLIANCE with the target, a paradox occurs. The existing popup structure handles this — just expand the condition check. **Critical:** The offensive cascade loop must skip the player when `has_paradox` is true (see `has_paradox` guard in code sample above), identical to how the defensive cascade uses `cascade_skip`. Otherwise the player gets auto-pulled in AND receives a choice popup.

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
`REVISED — 2026-03-22 design review + three-layer model (HUD → Detail → Wizard)`

**Current state:** Active wars are only visible in the Diplomatic Ledger (D key → Nations tab), buried alongside all nation relationships. There's no at-a-glance indicator of ongoing wars, war scores, or quick access to peace actions. The player must open a full screen to see war status.

**Design model:** EU4's bottom-right war shield icons — three-layer interaction:

```
Layer 1: HUD Cards         Layer 2: War Detail Popup      Layer 3: Wizard (actions)
(always visible,           (click to inspect,             (click to negotiate,
 bottom-right)              lightweight popup)              existing screen)
```

Key EU4 lessons applied: (1) compact icons on HUD, full detail on click; (2) war score BREAKDOWN is shown in the detail view, not crammed into the HUD; (3) coalition wars are a single grouped entry; (4) war exhaustion tells you when to negotiate.

**Scale consideration:** The current game has 5 nations. Eventually it will be a full map of Europe with 15-20+ nations. The three-layer model scales: the HUD stays compact (icon + score + trend), the detail popup handles arbitrarily rich data per war, and the wizard handles actions. War score breakdowns, battle history, WE, and coalition context are already compiled in the Diplomatic Ledger and Morning Dispatch — the detail popup aggregates them into a single focused "everything about THIS war" view.

---

#### N4a. Layer 1 — HUD Cards (Always Visible)

A compact always-visible panel anchored to the bottom-right corner. Cards are intentionally minimal — just enough to glance at. Detail lives in Layer 2.

**Bilateral war card:**

```
                                    ┌──────────────────────────┐
                                    │  ⚔ ACTIVE WARS           │
                                    ├──────────────────────────┤
                                    │ ■ Britain   +35 ▲   T:8  │
                                    │ █████████░░░              │
                                    └──────────────────────────┘
                                                     Bottom-right
```

Each bilateral war card shows:
- **Row 1:** Nation color swatch (■) + name + war score (+35) + trend arrow (▲▼—) + duration (T:8)
- **Row 2:** Score bar (green/red from center)
- **Click** → opens War Detail Popup (Layer 2) for that nation

**Coalition group (when `active_coalition` active):**

```
                                    ┌──────────────────────────┐
                                    │  ⚔ ACTIVE WARS           │
                                    ├──────────────────────────┤
                                    │ ⚔ BRITISH COALITION       │
                                    │  ■ Britain  +35 ▲        │
                                    │  ■ Prussia  -12 ▼        │
                                    │  ■ Austria  +5  —        │
                                    ├──────────────────────────┤
                                    │ ■ Saxony    +10 ▲   T:2  │
                                    │ █████░░░░░                │
                                    └──────────────────────────┘
```

- **Coalition header row:** Coalition name (clickable → opens Coalition Detail Popup)
- **Per-member rows:** Swatch + name + score + trend (compact — no WE on HUD, that's in the detail popup)
- **Click member row** → opens War Detail Popup for that member
- **Non-coalition wars** display as normal bilateral cards below

**Armistice card:**

```
│ ■ Austria  ⚖ 3 turns  │
```

- Dimmed styling. Single row: swatch + name + ⚖ + turns remaining
- **Click** → opens War Detail Popup (armistice variant)

**When no wars or armistices are active, the panel hides entirely.**

#### N4b. Layer 2 — War Detail Popup (Click to Inspect)

Clicking any HUD card opens a lightweight popup showing everything about that war. This is the "war overview" — the EU4 equivalent of clicking the war shield.

**Bilateral War Detail Popup:**

```
┌─ WAR WITH BRITAIN ─────────────────────┐
│                                         │
│  War Score: +35  ▲                      │
│  ┌─ Score Breakdown ──────────────────┐ │
│  │ Territory:  +20  (4 regions held)  │ │
│  │ Battles:    +9   (3 won, 1 lost)  │ │
│  │ Decisive:   +10  (1 victory)      │ │
│  │ Capital:    -4   (contested)      │ │
│  └────────────────────────────────────┘ │
│                                         │
│  Duration: 8 turns (since Turn 3)       │
│  Enemy WE: 28                           │
│                                         │
│  Recent Battles:                        │
│   ★ Decisive Victory at Waterloo (T:3)  │
│     Victory at Belgium (T:5)            │
│     Defeat at Netherlands (T:7)         │
│                                         │
│  ┌──────────────────────────────┐       │
│  │     [ Negotiate Peace ]      │       │
│  └──────────────────────────────┘       │
│                              [Close: X] │
└─────────────────────────────────────────┘
```

**Data shown:**
- **War score + trend** — large, colored, prominent
- **Score breakdown** — 4 components with context labels (territory: regions held, battles: W/L count, decisive: victory count, capital: held/contested/safe)
- **Duration** — turns at war + which turn it started
- **Enemy war exhaustion** — fog-filtered (shows "Unknown" at < PARTIAL visibility). Color: white <40, amber 40-79, red 80+
- **Recent battles** — last 3-5 from `battle_records[diplo_key]`, starred (★) if decisive. Shows location + turn
- **[Negotiate Peace] button** → opens Diplomacy Wizard (Layer 3) pre-focused on this nation

**Coalition Detail Popup (click coalition header):**

```
┌─ THE BRITISH COALITION ────────────────────┐
│                                             │
│  Leader: Britain   Posture: Aggressive      │
│                                             │
│  ■ Britain  +35 ▲  WE:12   ~76k men        │
│  ■ Prussia  -12 ▼  WE:28   ~45k men        │
│  ■ Austria  +5  —  WE:8    ~52k men        │
│                                             │
│  Coordination:                              │
│   Britain-Prussia: Good                     │
│   Britain-Austria: Good                     │
│   Prussia-Austria: Strained                 │
│                                             │
│  Weak link: Prussia (highest WE)            │
│                                             │
│  ┌──────────────┐  ┌──────────────┐         │
│  │[Target Prussia]│  │[Target Austria]│       │
│  └──────────────┘  └──────────────┘         │
│                                  [Close: X] │
└─────────────────────────────────────────────┘
```

**Data shown:**
- **Coalition name + leader + posture** (Aggressive/Defensive/Cautious)
- **Per-member rows:** Swatch + name + score + trend + WE + army strength (fog-filtered via `_format_army_strength`)
- **Coalition leader** indicated by bold/underline
- **Coordination quality** — derived from `get_coalition_friction()` between member pairs. Labels: "Good" (≥0.75), "Strained" (0.5), "Poor" (0.25). Tells the player which pairs have friction — a wedge target
- **Weak link** — the member with the highest WE. Highlighted. This teaches the coalition-splitting mechanic directly in the UI
- **[Target X] buttons** — one per non-leader member → opens Wizard for that nation. This is the "separate peace" entry point for coalition splitting (COALITION_SPEC §6a-c)

**Armistice Detail Popup (click armistice card):**

```
┌─ ARMISTICE WITH AUSTRIA ───────────────┐
│                                         │
│  Status: Armistice (3 turns remaining)  │
│  Relations: -15 (Hostile)               │
│  Trend: Rising ▲                        │
│                                         │
│  ┌──────────────────────────────┐       │
│  │   [ Diplomatic Options ]     │       │
│  └──────────────────────────────┘       │
│                              [Close: X] │
└─────────────────────────────────────────┘
```

- Shows remaining turns, current relations + trend
- **[Diplomatic Options] button** → opens Wizard with armistice-valid actions (Improve Relations, etc.)

#### N4c. Layer 3 — Diplomacy Wizard (Existing, Add Entry Point)

The wizard already exists (`diplomacy_wizard.gd`). Add `open_for_nation()` method that skips step 1:

```gdscript
func open_for_nation(nation: String):
    """Open wizard directly at Step 2 for a specific nation.
    Called from war detail popup [Negotiate Peace] and coalition [Target X] buttons."""
    _current_step = 2
    _selected_nation = nation
    back_button.visible = true
    title_label.text = "DIPLOMACY — " + nation
    assessment_panel.text = "[color=#" + COLOR_INFO + "]Loading assessment...[/color]"
    _clear_content_list()
    _add_loading_label()
    show()
    _fetch_preview(nation)
```

Reuses existing `_on_nation_selected()` flow. Wizard step 2 already shows state-appropriate actions: "Propose Armistice"/"Propose Peace" for WAR, "Improve Relations" for ARMISTICE, etc.

---

#### N4d. State Transitions & Cleanup

The panel must handle all war lifecycle transitions cleanly:

| Transition | HUD Effect | Detail Popup Effect |
|---|---|---|
| **War starts** (declaration/cascade) | Card appears in panel | N/A |
| **War → Armistice** (peace signed) | War card transitions to armistice card | If open, close and show brief "Armistice signed" then reopen as armistice variant |
| **War → Peace** (full peace) | Card removes entirely | If open, close with "Peace concluded" |
| **Armistice expires** (→ PEACE) | Armistice card removes | If open, close |
| **Coalition forms** | Individual cards re-group under coalition header | N/A — cards were already showing |
| **Coalition dissolves** | Coalition group collapses, remaining bilateral wars revert to individual cards | If coalition popup open, close |
| **Separate peace (coalition member)** | Member row removes from coalition group. If <2 members remain, coalition group collapses | If that member's detail is open, close with "Peace concluded" |
| **Nation eliminated** (0 regions + 0 marshals) | Card removes entirely | If open, close |
| **All wars + armistices end** | Panel hides | All popups close |
| **Enemy turn ends** (turn advances) | Full refresh from new `active_wars` data | If open, refresh data in place (don't close — player might be reading) |

**Implementation:** `update_wars()` in `war_status_panel.gd` does a full rebuild every call. Since it's called on every `/command` response, transitions happen naturally. For the detail popup:

```gdscript
func update_wars(data: Dictionary) -> void:
    # ... rebuild cards ...

    # If detail popup is open, check if its war still exists
    if _detail_popup_open and _detail_popup_nation != "":
        var still_exists = false
        for w in data.get("wars", []):
            if w.get("opponent") == _detail_popup_nation:
                still_exists = true
                _refresh_detail_popup(w)  # Update in place
                break
        if not still_exists:
            _close_detail_popup()  # War ended while popup was open
```

#### N4e. Trend Arrow (Momentum)

Each card shows a trend arrow: ▲ (improving), ▼ (declining), — (stable).

```python
prev_scores = getattr(world, 'previous_war_scores', {})
prev = prev_scores.get(diplo_key, 0)
# Flip sign if France is not alphabetically first
if france != diplo_key.split("|")[0]:
    prev = -prev
if score > prev + 2:
    trend = "rising"    # ▲ green
elif score < prev - 2:
    trend = "falling"   # ▼ red
else:
    trend = "stable"    # — white
```

`previous_war_scores` already exists on WorldState (line 427) — used for Talleyrand Trigger 2 delta detection. No new fields needed.

---

#### N4f. Backend: `build_active_wars()` Helper

**No separate endpoint.** Embed `active_wars` in the POST `/command` response. Data is ~200 bytes per war. Panel refreshes on every command response anyway.

```python
# backend/game_logic/war_status.py (NEW FILE — ~100 lines)

"""War Status Panel data builder. Produces active_wars dict for HUD + detail popup."""

from typing import Dict, Any, List

ARMISTICE_DURATION = 5  # Must match diplomacy.py


def build_active_wars(world) -> Dict[str, Any]:
    """Build active wars data for the war status panel.

    Returns {wars: [...], coalition: {...} | None}.
    Each war entry includes HUD-level data (score, trend) AND
    detail-popup data (breakdown, battles, WE).
    All numbers int()-wrapped per Golden Rule #2.
    """
    from backend.game_logic.diplomacy import (
        calculate_war_score, get_war_score_for,
    )
    from backend.game_logic.diplomatic_ledger import (
        _get_nation_visibility, _format_army_strength,
    )
    from backend.models.intel import PARTIAL, VISIBILITY_PRIORITY

    france = world.player_nation
    wars = []
    coalition = getattr(world, 'active_coalition', None)
    coalition_members = set(
        coalition.get("members", [])
    ) if coalition else set()
    prev_scores = getattr(world, 'previous_war_scores', {})

    # ── Active wars ──
    for key, state in world.diplomatic_states.items():
        if state != "WAR":
            continue
        nations = key.split("|")
        if france not in nations:
            continue
        opponent = nations[0] if nations[1] == france else nations[1]

        # Skip eliminated nations (0 regions + 0 living marshals)
        opp_regions = sum(
            1 for r in world.regions.values()
            if r.controller == opponent
        )
        opp_marshals = sum(
            1 for m in world.marshals.values()
            if m.nation == opponent and m.strength > 0
        )
        if opp_regions == 0 and opp_marshals == 0:
            continue

        diplo_key = world._make_diplo_key(france, opponent)

        # War score + components
        score = int(get_war_score_for(world, france, opponent))
        components = calculate_war_score(
            france, opponent, world, return_components=True
        )
        breakdown = {
            "territory": int(components["territory"]),
            "battles": int(components["battles"]),
            "decisive": int(components["decisive"]),
            "capital": int(components["capital"]),
        }

        # Duration
        started = int(world.war_start_turns.get(diplo_key, 0))
        duration = int(world.current_turn) - started

        # Trend (compare to previous turn)
        prev = prev_scores.get(diplo_key, 0)
        if france != diplo_key.split("|")[0]:
            prev = -prev
        if score > prev + 2:
            trend = "rising"
        elif score < prev - 2:
            trend = "falling"
        else:
            trend = "stable"

        # Battle history (for detail popup)
        all_records = getattr(world, 'battle_records', {})
        records = all_records.get(diplo_key, [])
        battles_fought = int(len(records))
        # Recent battles (last 5, newest first)
        recent_battles = []
        sorted_records = sorted(
            records, key=lambda r: r.get("turn", 0), reverse=True
        )[:5]
        decisive_set = set()
        d_records = getattr(
            world, 'decisive_battles', {}
        ).get(diplo_key, [])
        for d in d_records:
            decisive_set.add(
                (d.get("turn", 0), d.get("winner", ""))
            )
        decisive_won = int(sum(
            1 for d in d_records if d.get("winner") == france
        ))
        for rec in sorted_records:
            turn = int(rec.get("turn", 0))
            winner = rec.get("winner", "")
            location = rec.get("location", "unknown")
            is_decisive = (turn, winner) in decisive_set
            won = winner == france
            recent_battles.append({
                "turn": turn,
                "location": location,
                "won": won,
                "decisive": is_decisive,
            })

        # War exhaustion + army strength (fog-filtered)
        raw_we = world.war_exhaustion.get(opponent, 0) or 0
        vis = _get_nation_visibility(opponent, world)
        vis_priority = VISIBILITY_PRIORITY.get(vis, 0)
        partial_priority = VISIBILITY_PRIORITY.get(PARTIAL, 3)
        if vis_priority >= partial_priority:
            war_exhaustion = int(raw_we)
        else:
            war_exhaustion = None

        opp_strength = sum(
            m.strength for m in world.marshals.values()
            if m.nation == opponent and m.strength > 0
        )
        army_strength = _format_army_strength(opp_strength, vis)

        # Coalition tagging
        in_coalition = opponent in coalition_members
        is_coalition_leader = bool(
            coalition and coalition.get("leader") == opponent
        )

        wars.append({
            "opponent": opponent,
            "war_score": score,
            "breakdown": breakdown,
            "duration": duration,
            "started_turn": started,
            "trend": trend,
            "battles_fought": battles_fought,
            "decisive_won": decisive_won,
            "recent_battles": recent_battles,
            "war_exhaustion": war_exhaustion,
            "army_strength": army_strength,
            "status": "war",
            "in_coalition": in_coalition,
            "is_coalition_leader": is_coalition_leader,
        })

    # Sort: coalition leader first, then alphabetical
    wars.sort(key=lambda w: (
        not w.get("is_coalition_leader", False),
        not w.get("in_coalition", False),
        w["opponent"],
    ))

    # ── Coalition metadata ──
    coalition_info = None
    if coalition and any(w["in_coalition"] for w in wars):
        # Coordination quality between members (for detail popup)
        from backend.game_logic.coalition import get_coalition_friction
        members = [w["opponent"] for w in wars if w["in_coalition"]]
        coordination = []
        for i, m1 in enumerate(members):
            for m2 in members[i + 1:]:
                friction = get_coalition_friction(m1, m2, world)
                if friction >= 0.75:
                    quality = "Good"
                elif friction >= 0.5:
                    quality = "Strained"
                else:
                    quality = "Poor"
                coordination.append({
                    "nation_a": m1,
                    "nation_b": m2,
                    "quality": quality,
                })

        # Weak link: highest WE among members with known WE
        weak_link = None
        max_we = -1
        for w in wars:
            if w["in_coalition"] and w["war_exhaustion"] is not None:
                if w["war_exhaustion"] > max_we:
                    max_we = w["war_exhaustion"]
                    weak_link = w["opponent"]

        coalition_info = {
            "name": coalition.get("name", "Unknown Coalition"),
            "leader": coalition.get("leader", ""),
            "posture": coalition.get("strategic_posture", "defensive"),
            "coordination": coordination,
            "weak_link": weak_link,
        }

    # ── Armistice nations ──
    armistice_turns_dict = getattr(world, 'armistice_turns', {})
    for key, state in world.diplomatic_states.items():
        if state != "ARMISTICE":
            continue
        nations_in_key = key.split("|")
        if france not in nations_in_key:
            continue
        opponent = (
            nations_in_key[0]
            if nations_in_key[1] == france
            else nations_in_key[1]
        )
        diplo_key = world._make_diplo_key(france, opponent)
        elapsed = int(armistice_turns_dict.get(diplo_key, 0))
        remaining = int(max(0, ARMISTICE_DURATION - elapsed))

        # Relation + trend for armistice detail popup
        relation = int(
            world.nation_relations.get(diplo_key, 0) or 0
        )
        from backend.game_logic.diplomacy import get_relation_descriptor
        relation_desc = get_relation_descriptor(relation)
        relation_history = getattr(
            world, 'relation_history', {}
        ).get(diplo_key, [])
        if len(relation_history) >= 2:
            delta = relation - relation_history[-1]
            rel_trend = (
                "rising" if delta > 2
                else "falling" if delta < -2
                else "stable"
            )
        else:
            rel_trend = "stable"

        wars.append({
            "opponent": opponent,
            "war_score": 0,
            "breakdown": None,
            "duration": 0,
            "started_turn": 0,
            "trend": "stable",
            "battles_fought": 0,
            "decisive_won": 0,
            "recent_battles": [],
            "war_exhaustion": None,
            "army_strength": None,
            "status": "armistice",
            "armistice_remaining": remaining,
            "relation": relation,
            "relation_descriptor": relation_desc,
            "relation_trend": rel_trend,
            "in_coalition": False,
            "is_coalition_leader": False,
        })

    return {
        "wars": wars,
        "coalition": coalition_info,
    }
```

**Wiring in `main.py`:** Add `active_wars` to every POST `/command` response that includes `game_state`:

```python
# At top of execute_command(), and in each response path:
from backend.game_logic.war_status import build_active_wars
response["active_wars"] = build_active_wars(world)
```

Also add to `GET /status` response so the panel initializes on page load.

---

#### N4g. Godot Architecture

| Component | Detail |
|-----------|--------|
| **HUD Scene** | `war_status_panel.tscn` — PanelContainer anchored bottom-right |
| **HUD Script** | `war_status_panel.gd` |
| **Detail Scene** | `war_detail_popup.tscn` — PanelContainer, positioned dynamically |
| **Detail Script** | `war_detail_popup.gd` |
| **HUD Layer** | CanvasLayer 25 (above map at 0, below screens at 50) |
| **Detail Layer** | CanvasLayer 30 (above HUD at 25, below screens at 50) |
| **HUD Position** | `anchor_right=1, anchor_bottom=1`, offset 10px from corner |
| **Detail Position** | Anchored to the LEFT of the clicked card (slides out from HUD) |
| **HUD Visibility** | Hidden when: no active wars/armistices, OR any layer-50 screen open, OR any modal dialog open |
| **Detail Visibility** | Hidden by default. Shown on card click. Hidden on: close button, click elsewhere, screen opens, modal opens |
| **Update trigger** | Both refresh from `active_wars` in every `/command` response |
| **HUD Signals** | `card_clicked(nation: String, status: String)` |
| **Detail Signals** | `negotiate_clicked(nation: String)`, `target_clicked(nation: String)` |

**HUD scene tree:**

```
WarStatusPanel (CanvasLayer, layer=25)
  └─ PanelContainer (anchored bottom-right, max_width=220px)
      └─ ScrollContainer (max 4 cards visible)
          └─ VBoxContainer
              ├─ HeaderLabel ("⚔ ACTIVE WARS")
              ├─ CoalitionGroup (VBoxContainer, visible only when coalition)
              │   ├─ CoalitionHeaderBtn (Button, flat, clickable)
              │   │   └─ "⚔ BRITISH COALITION"
              │   ├─ MemberRow_0 (Button, flat, clickable)
              │   │   └─ "■ Britain  +35 ▲"
              │   ├─ MemberRow_1 ...
              │   └─ MemberRow_2 ...
              ├─ BilateralCard_0 (Button, flat, clickable)
              │   ├─ Row1: "■ Saxony  +10 ▲  T:2"
              │   └─ Row2: "█████░░░░░"
              ├─ ArmisticeCard_0 (Button, flat, clickable, dimmed)
              │   └─ "■ Austria  ⚖ 3 turns"
              └─ ...
```

**Detail popup scene tree:**

```
WarDetailPopup (CanvasLayer, layer=30)
  └─ PanelContainer (positioned left of HUD card)
      └─ VBoxContainer
          ├─ HeaderLabel ("WAR WITH BRITAIN")
          ├─ CloseButton (top-right "X")
          ├─ ScoreSection (VBoxContainer)
          │   ├─ ScoreLabel ("+35 ▲", large, colored)
          │   └─ BreakdownPanel (RichTextLabel, BBCode)
          ├─ InfoSection (VBoxContainer)
          │   ├─ DurationLabel ("Duration: 8 turns (since Turn 3)")
          │   └─ WELabel ("Enemy War Exhaustion: 28")
          ├─ BattleSection (VBoxContainer)
          │   ├─ BattleSectionHeader ("Recent Battles:")
          │   └─ BattleList (RichTextLabel, BBCode)
          ├─ CoalitionSection (VBoxContainer, only for coalition detail)
          │   ├─ MemberTable (RichTextLabel, BBCode)
          │   ├─ CoordinationLabel
          │   └─ WeakLinkLabel
          ├─ HSeparator
          └─ ButtonRow (HBoxContainer)
              ├─ NegotiateButton ("[Negotiate Peace]")
              └─ (or TargetButtons for coalition detail)
```

**Styling** (matches existing UI):
- Dark panel background: `Color(0.08, 0.08, 0.12, 0.9)`
- Gold border: `Color(0.85, 0.7, 0.3)`
- Score color: green (`#4a4`) positive, red (`#a44`) negative, white at 0
- Trend: ▲ green, ▼ red, — white
- WE color: white <40, amber (`#e0a040`) 40-79, red (`#cc4444`) 80+
- Decisive battles: ★ gold prefix
- Coalition header: slightly brighter background, bold
- Coalition leader: underlined name
- Armistice cards/popup: dimmed text `Color(0.5, 0.5, 0.5)`
- Nation colors: reuse `COLORS` dict from `map.gd`
- HUD max width: 220px. Detail popup max width: 320px
- Detail popup: slight drop shadow for depth vs HUD

---

#### N4h. Godot: Click Flow Wiring

```gdscript
# war_status_panel.gd
signal card_clicked(nation: String, status: String)

func _on_card_pressed(nation: String, status: String):
    card_clicked.emit(nation, status)


# main.gd
func _on_war_card_clicked(nation: String, status: String):
    # Find the war data for this nation from cached active_wars
    var war_data = _find_war_data(nation)
    if war_data == null:
        return
    war_detail_popup.show_war(war_data, _cached_coalition_data)


func _on_coalition_header_clicked():
    war_detail_popup.show_coalition(_cached_coalition_data, _cached_wars)


# war_detail_popup.gd
signal negotiate_clicked(nation: String)
signal target_clicked(nation: String)

func show_war(war_data: Dictionary, coalition_data) -> void:
    """Show bilateral or coalition-member war detail."""
    _current_nation = war_data.get("opponent", "")
    _render_war_detail(war_data)
    show()

func show_coalition(coalition_data: Dictionary, wars: Array) -> void:
    """Show coalition overview detail."""
    _current_nation = coalition_data.get("leader", "")
    _render_coalition_detail(coalition_data, wars)
    show()

func _on_negotiate_pressed():
    hide()
    negotiate_clicked.emit(_current_nation)

func _on_target_pressed(nation: String):
    hide()
    target_clicked.emit(nation)


# main.gd — connect detail popup to wizard
func _on_negotiate_clicked(nation: String):
    diplomacy_wizard.open_for_nation(nation)

func _on_target_clicked(nation: String):
    diplomacy_wizard.open_for_nation(nation)
```

**`open_for_nation()` in `diplomacy_wizard.gd`:**

```gdscript
func open_for_nation(nation: String):
    """Open wizard directly at Step 2 for a specific nation.
    Called from war detail popup buttons."""
    _current_step = 2
    _selected_nation = nation
    back_button.visible = true
    title_label.text = "DIPLOMACY — " + nation
    assessment_panel.text = "[color=#" + COLOR_INFO + "]Loading assessment...[/color]"
    _clear_content_list()
    _add_loading_label()
    show()
    _fetch_preview(nation)
```

---

#### N4i. Integration with Screen System

- HUD panel registered with `main.gd` (NOT top_bar — persistent HUD, not toggleable)
- Detail popup registered with `main.gd`
- `main.gd` connects `top_bar.screen_changed` to hide both HUD and detail popup when screens open
- Both hide when modal dialogs open
- HUD does NOT have a hotkey (always visible)
- Detail popup closes on: close button click, Escape key, click outside popup, screen/modal opens
- Neither consumes keyboard focus (terminal input unaffected)

```gdscript
# main.gd
func _on_screen_changed():
    _update_war_panel_visibility()

func _update_war_panel_visibility():
    var should_show = (
        not _is_screen_open()
        and not _is_modal_dialog_open()
        and _has_active_wars
    )
    if war_status_panel:
        war_status_panel.visible = should_show
    if not should_show and war_detail_popup:
        war_detail_popup.hide()

func _on_command_result(response: Dictionary):
    # ... existing response handling ...
    var active_wars_data = response.get("active_wars", null)
    if active_wars_data and war_status_panel:
        war_status_panel.update_wars(active_wars_data)
        _cached_wars = active_wars_data.get("wars", [])
        _cached_coalition_data = active_wars_data.get("coalition", null)
        _has_active_wars = not _cached_wars.is_empty()
        # Refresh detail popup if open (in-place update, don't close)
        if war_detail_popup and war_detail_popup.visible:
            war_detail_popup.refresh_if_open(active_wars_data)
        _update_war_panel_visibility()
```

---

#### N4j. Test Cases (Backend)

1. `build_active_wars()` returns empty wars list when no wars or armistices
2. Returns correct opponent, war_score, duration, started_turn for each active war
3. War score sign is from France's perspective (positive = winning)
4. All numbers are `int()` (Godot golden rule)
5. `breakdown` contains all 4 components that sum to `war_score`
6. `trend` is "rising" when score increased >2, "falling" when decreased >2, else "stable"
7. `battles_fought` matches count of battle_records for that diplo_key
8. `decisive_won` counts only France's decisive victories, not opponent's
9. `recent_battles` returns last 5, newest first, with correct won/decisive/location/turn
10. `war_exhaustion` is None when opponent visibility < PARTIAL (fog filter)
11. `war_exhaustion` is correct int when opponent visibility >= PARTIAL
12. `army_strength` is fog-filtered string ("Unknown" / "~45,000 men" / "72,000 men")
13. `in_coalition` is True for coalition members, False otherwise
14. `is_coalition_leader` is True only for the coalition leader
15. `coalition.coordination` shows correct friction quality between all member pairs
16. `coalition.weak_link` identifies the member with highest known WE
17. `coalition` is None when no coalition is active
18. Armistice: correct `armistice_remaining`, `relation`, `relation_descriptor`, `relation_trend`
19. Eliminated nations excluded (0 regions + 0 living marshals)
20. Wars sorted: coalition leader first, then coalition members, then bilateral, then armistice
21. Works correctly with 0, 1, 2, 3, 4+ simultaneous wars
22. Mixed state: 2 coalition wars + 1 bilateral war + 1 armistice all in one response
23. War that ends (WAR → ARMISTICE) between calls: war entry disappears, armistice entry appears
24. All wars end: returns `{"wars": [], "coalition": null}`

#### N4k. Test Cases (Godot — Manual)

**HUD Panel:**
1. Panel appears when war starts, disappears when all wars and armistices end
2. Panel hides when D/T/L/G/R screens are open
3. Panel hides when any modal dialog is open
4. Coalition group appears when coalition forms, collapses when it dissolves
5. Score colors update correctly (green positive, red negative)
6. Trend arrows update after battles (▲ green, ▼ red)
7. Armistice card appears after signing armistice, countdown decrements each turn
8. Panel handles 4+ simultaneous wars with ScrollContainer
9. Panel does not block keyboard input to terminal

**Detail Popup:**
10. Click bilateral card → war detail popup opens with breakdown, battles, WE, duration
11. Click coalition member → war detail popup opens for that member
12. Click coalition header → coalition detail popup opens with all members, coordination, weak link
13. Click armistice card → armistice detail popup opens with relation info
14. Close button (X) closes popup
15. Escape key closes popup
16. Click outside popup closes popup
17. Screen/modal opening closes popup
18. Popup refreshes in-place when new data arrives (doesn't close mid-read)
19. War ends while popup is open → popup closes gracefully
20. WE labels: white <40, amber 40-79, red 80+
21. WE shows "Unknown" when fog-filtered (insufficient intel)
22. Decisive battles marked with ★ in battle list
23. Coalition coordination labels match friction values (Good/Strained/Poor)
24. Coalition weak link highlights the correct member

**Full Flow:**
25. Click card → detail popup → [Negotiate Peace] → wizard opens at step 2 for that nation
26. Click coalition header → coalition popup → [Target Prussia] → wizard opens for Prussia
27. Click armistice card → armistice popup → [Diplomatic Options] → wizard opens for that nation
28. War ends during enemy turn → card removes, popup closes if open, panel hides if no wars remain

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

**Fix:** After `modify_nation_relation()` calls that produce large swings (≥ ±10 cumulative in a turn), fire a dispatch event: "Relations with [nation] have [worsened/improved] significantly."

**Implementation:** Add a transient dict `_relation_deltas_this_turn: Dict[str, int]` on WorldState (no serialization — cleared at turn start in `advance_turn()`). In `modify_nation_relation()`, accumulate: `self._relation_deltas_this_turn[nation] = self._relation_deltas_this_turn.get(nation, 0) + amount`. At end of turn processing (after all modifications), iterate the dict, fire dispatch for any nation with `abs(delta) >= 10`. Filter via existing fog rules (`partial_on_nation`).

**Note:** The dispatch does NOT attribute a specific reason — `modify_nation_relation()` only receives a delta, not a reason string. Adding reason tracking would require changing every callsite. The unattributed dispatch still tells the player *something changed* and they can check the diplomatic ledger for details.

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

### Session DA-1: AI Diplomatic Intelligence (Backend Only) — COMPLETE
**Scope:** 5 items, 79 tests
**Prerequisite:** None — all fixes are in existing code paths

| # | Item | Files | Complexity |
|---|------|-------|------------|
| A4 | Fix gold demand formula (floor 200, mult 5) | `ai_diplomacy.py` | Small — 2 lines |
| A1 | Iterative demand reduction loop for P8 | `ai_diplomacy.py` | Medium — new function, ~30 lines |
| A2 | Coalition loyalty check before P1 peace | `ai_diplomacy.py` | Small — ~15 lines guard clause |
| A3 | WE modifier on P1/P2 thresholds | `ai_diplomacy.py` | Small — ~5 lines |
| N1 | AI-AI preemptive alliances (Trigger 5) | `ai_diplomacy.py` | Small — ~15 lines in `_evaluate_ai_ai_proposal` |

### Session DA-2: Player Feedback & UX (Backend Only) — COMPLETE
**Scope:** 6 items, 37 tests
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

| Category | Items | Session | Status |
|----------|-------|---------|--------|
| AI behavior fixes (A1-A4) | 4 | DA-1 | DONE (79 tests) |
| New feature: preemptive alliances (N1) | 1 | DA-1 | DONE |
| UX feedback (S1-S5, U2) | 6 | DA-2 | DONE (37 tests) |
| New feature: offensive cascade (N2) | 1 | DA-3 | — |
| Enhancement: friction in attacks (N3) | 1 | DA-3 | — |
| New feature: war status panel (N4) | 1 | DA-4 | DONE (32 tests) |
| **Total** | **14** | **4 sessions** | **12/14 done, 1 session remaining** |

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

---

## N4 WAR STATUS PANEL — DESIGN REVIEW

> **Reviewer context:** Web research across EU4, CK3, Vic3, Total War Napoleon/Empire, Old World war screens + full backend data audit of `diplomacy.py`, `coalition.py`, `world_state.py`, `diplomatic_ledger.py`. Review date: 2026-03-22.

---

### 1. War Screen Examples — What the Best Games Do

#### Europa Universalis 4 (most relevant reference)

**Bottom-right HUD:** Each active war = a small shield icon (enemy coat of arms) in the bottom-right. Multiple wars stack vertically. Clicking opens a dedicated War Overview Window.

**War Overview Window:**
- War name at top (casus belli + participants).
- Two columns: Attacker shields (left) vs Defender shields (right). **War leader marked with a star.**
- **War score prominently centered** (-100% to +100%), color-coded green/red.
- **Ticking war score arrow** (green up / red down / neutral dash) — shows momentum.
- **War score breakdown tooltip on hover:** Battles + Occupation + Ticking War Score. This is the key insight — players hover to understand *why* they're winning or losing.
- **Individual nation shields** — hover to see per-nation war score (for separate peace math).
- **"Sue for Peace" button** per participant. For coalition wars, separate peace is blocked with individual coalition members — you negotiate with the war leader only.

**Coalition war specifics:** Coalition displays as a single war with all members on the defender side. No separate peace with individual members. The coalition functions as a bloc under the war leader.

**Peace deal screen:** Province selection on map, each demand has a war score cost, **acceptance modifier tooltip** (all factors listed with weights), and a **coalition warning icon** showing which nations would join a new coalition if terms are too harsh.

**What works:** Information-dense tooltips reward curiosity. War score breakdown = actionable intelligence. Coalition warning on peace screen prevents mistakes.
**What's cluttered:** 10+ participant wars overflow the overview window.

#### Crusader Kings 3

**Bottom-right HUD:** Active wars as coat-of-arms icons with a **percentage number underneath** (green = winning, red = losing). Audio horn when you reach victory threshold.

**War overview:** Two-side display (attacker/defender) with character portraits + allies. Single 0-100% war score. Three sources: battles, territory occupation, capturing prisoners (capturing war leader = instant forced surrender).

**Peace options:** Three buttons: Enforce Demands / White Peace / Surrender. Simple and dramatic.

**What works:** Character-focused, clean. Single percentage is immediately readable. Audio cue is satisfying.
**What's cluttered:** Large alliance wars overflow portraits. War contribution opaque.

#### Victoria 3

**War UI:** Front-based system. War overview lists active fronts (border lines on map), battalions on each front, assigned generals. Fronts physically push across the map as sides win/lose.

**War Support bar:** -100 to +100 per nation. Declines over time with casualties and territorial loss. Hits -100 = forced capitulation.

**Peace deals:** All war goals listed as toggleable items. Mixed deals possible (both sides concede something). Allied consent required.

**What works:** Front system is visual and intuitive for macro-level wars. War Support is clear.
**What's cluttered:** Players feel disconnected from combat. Large multi-front wars hard to manage.

#### Total War Napoleon/Empire

**Diplomacy button** in bottom-right opens a three-panel screen (faction list / relations / map). No dedicated "war screen" — war status shown through color-coded faction relations and tooltips. Strength comparison bar shows relative military power. Negotiation table with offer/demand building and color-coded acceptance likelihood.

**What works:** Strength comparison bar is immediately useful. Color-coded map showing how factions view each other.
**Limitation:** No war score system at all. War management through generic diplomacy panel feels unfocused.

#### Old World

Fundamentally different: mission-based diplomacy. Ambassador assigned to peace/truce missions that take multiple turns. Event popups with 2-3 options influenced by Ambassador stats. No war score, no battle tracking in UI.

**What works:** Diplomacy feels weighty and consequential (can't spam offers). Character stats matter.
**Limitation:** Too abstract for our game's needs. No granular war tracking.

#### Cross-Game Summary

| Feature | EU4 | CK3 | Vic3 | TW:N | Old World |
|---|---|---|---|---|---|
| Bottom-right war icons | Shield per war | CoA + % | Front list | Diplomacy button | None |
| Score visualization | -100 to +100, 3-component tooltip | 0-100% single | War Support bar | None | None |
| Score breakdown on hover | Battles + Occupation + Ticking | Battles + Territory + Prisoners | Front advance + decay | N/A | N/A |
| Coalition display | Single war, all members shown, no separate peace | N/A | Alliance blocs | N/A | N/A |
| Action from war screen | Sue for Peace button | Enforce/White Peace/Surrender | Press/unpress war goals | Offer/demand table | Event popup |

**Key takeaway:** The *breakdown* is what makes war screens useful, not just the number. EU4's hover-to-see-components is the gold standard. Our game's war score has 4 clean components (territory/battles/decisive/capital) that map perfectly to this pattern.

---

### 2. Backend Data Inventory

Every piece of war-related data currently available in the backend:

#### War Score Data
| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `war_scores` | `world_state.py` | Dict[str, int] | diplo_key → score (-100 to +100) |
| `calculate_war_score()` | `diplomacy.py:321` | function | Computes from 4 components |
| — `return_components=True` | `diplomacy.py:388` | option | Returns {total, territory, battles, decisive, capital} |
| `get_war_score_for()` | `diplomacy.py:451` | function | Perspective-adjusted canonical helper |
| `apply_war_score_decay()` | `diplomacy.py:399` | function | -2/turn when no battles for 3+ turns |
| `recalculate_war_scores()` | `diplomacy.py:439` | function | Called during advance_turn for all active wars |

#### Battle Records
| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `battle_records` | `world_state.py:368` | Dict[str, List] | diplo_key → [{winner, turn, ...}] |
| `decisive_battles` | `world_state.py:371` | Dict[str, List] | diplo_key → [{winner, turn, winner_casualties, loser_casualties, location}] |

#### War Timing
| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `war_start_turns` | `world_state.py:459` | Dict[str, int] | diplo_key → turn war began |
| `current_turn` | `world_state.py` | int | Current game turn |

#### Armistice
| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `armistice_cooldowns` | `world_state.py:374` | Dict[str, int] | diplo_key → turns remaining (5 max) |
| `armistice_turns` | `world_state.py:377` | Dict[str, int] | diplo_key → turns elapsed since armistice |

#### War Exhaustion
| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `war_exhaustion` | `world_state.py:458` | Dict[str, int] | nation → 0-200 |
| `_prev_war_exhaustion` | `world_state.py:3703` | Dict[str, int] | Snapshot for trend calculation |

#### Coalition Data
| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `active_coalition` | `world_state.py` | Dict or None | {name, leader, strategic_posture, members} |
| `coalition_brewing` | `world_state.py` | Dict or None | {turns_remaining, qualifying_nations} |
| `coalition_cooldown` | `world_state.py` | int | Turns until new coalition can form |
| `threat_level` | `world_state.py` | int 0-100 | Current French threat level |
| `threat_sources_this_turn` | `world_state.py` | List[Dict] | [{source, amount}] for UI breakdown |
| `get_qualifying_nations()` | `coalition.py` | function | Which nations would join a coalition now |
| `get_coalition_friction()` | `coalition.py` | function | Coordination quality between coalition members |

#### Diplomatic State
| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `diplomatic_states` | `world_state.py` | Dict[str, str] | diplo_key → WAR/PEACE/ARMISTICE/etc. |
| `nation_relations` | `world_state.py` | Dict[str, int] | diplo_key → -100 to +100 |
| `nation_starting_regions` | `world_state.py` | Dict[str, List] | Which regions each nation started with |

#### Military (relevant to war display)
| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `marshals` | `world_state.py` | Dict | All marshals with strength, location, nation |
| `regions` | `world_state.py` | Dict | All regions with controller field |

#### Already Exposed in Diplomatic Ledger
| Data | Where | Notes |
|------|-------|-------|
| Per-nation war_score_breakdown | `diplomatic_ledger.py:220-231` | Full 4-component breakdown, already computed |
| Armistice remaining | `diplomatic_ledger.py:353-358` | Per-treaty calculation |
| Coalition member strength + WE + trend | `diplomatic_ledger.py:427-454` | Fog-filtered, with trend |
| Threat sources with labels | `diplomatic_ledger.py:394-410` | Human-readable labels |
| Nation army strength (fog-filtered) | `diplomatic_ledger.py:159-171` | Band/approximate/exact by visibility |

---

### 3. Gap Analysis — N4 Spec vs Reality

#### Per-UI-Element Classification

| Spec Element | Classification | Notes |
|---|---|---|
| Nation name | **READY** | Parsed from diplomatic_states keys |
| Nation color swatch | **READY** | Existing nation colors in map.gd |
| War score (single number) | **READY** | `get_war_score_for()` exists |
| War score bar (green/red fill) | **READY** | Score maps directly to ProgressBar 0-100 |
| Duration (turns at war) | **READY** | `war_start_turns` exists, simple subtraction |
| Click → diplomacy wizard | **READY** | Wizard already supports nation pre-selection |
| Armistice cards | **READY** | `armistice_cooldowns` field exists |
| Hide when no wars | **READY** | Trivial empty-check |
| Hide when screens/modals open | **READY** | Existing `is_screen_open()` / `_is_modal_dialog_open()` patterns |
| `/active_wars` endpoint | **READY** | Spec's code is correct, data exists |

#### What's DERIVABLE (data exists, spec doesn't use it)

| Missing Element | Source | Complexity |
|---|---|---|
| War score components (territory/battles/decisive/capital) | `calculate_war_score(return_components=True)` | 1 line — already exists |
| Coalition membership flag per war | `active_coalition.members` check | Trivial |
| Coalition war leader | `active_coalition.leader` | Trivial |
| Coalition posture | `active_coalition.strategic_posture` | Trivial |
| Enemy war exhaustion | `world.war_exhaustion[opponent]` | Trivial, fog-filter needed |
| Number of battles fought | `len(battle_records[diplo_key])` | Trivial |
| Decisive battle count | `len(decisive_battles[diplo_key])` | Trivial |
| Last battle turn (recency) | `max(turn for r in battle_records)` | Trivial |
| Score trend / momentum | Compare current score to last-turn snapshot | Medium — need to store prev score |
| Coalition total members + strength | `active_coalition.members` + marshal strength sum | Already in diplomatic_ledger.py |

#### What's MISSING (would need new backend work)

| Missing Element | What's Needed |
|---|---|
| Who declared war (aggressor/defender) | Not currently tracked. Would need a `war_aggressors` dict |
| War name / casus belli | We don't have EU4-style casus belli. Not needed for our game |
| Per-nation separate peace availability in coalition | Logic exists in coalition.py but not surfaced as a simple flag |

#### OVER-DESIGNED elements

| Element | Issue |
|---|---|
| Armistice "not clickable" | Overly restrictive — player may want to open Diplomatic Ledger or see treaty details for the armistice nation. Consider making it click to wizard with reduced options instead of no click. |

#### UNDER-DESIGNED elements (our data supports it, best games show it, spec ignores it)

| Element | Why It Matters | Data Source |
|---|---|---|
| **War score component breakdown** | EU4's #1 feature. Player can't act on a score they don't understand. "You're at +35" means nothing without "territory +20, battles +9, decisive +10, capital -4" | `calculate_war_score(return_components=True)` — already built |
| **Coalition war grouping** | A coalition war is ONE coordinated threat, not 3 separate wars. Spec shows individual 1v1 cards which undersells the danger | `active_coalition` with members, leader, posture |
| **Battle count / last engagement** | Answers "is this a hot war or a cold one?" — critical for deciding when to propose peace | `battle_records` + `decisive_battles` |
| **War exhaustion** | Directly indicates when an enemy is ready to negotiate. EU4's acceptance tooltip equivalent | `war_exhaustion[opponent]` |
| **Momentum indicator** | EU4's ticking war score arrow. "Am I trending toward victory or defeat?" | Derivable from score change between turns |

---

### 4. Critique vs EU4/CK3/Vic3

#### Layout density: Too sparse for what we have

The spec shows 3 fields per war card: name, score, duration. Our backend has 15+ data points per war. This is like EU4 showing only the shield icon with no war score — technically functional but strategically useless. The spec's cards are *decorative* rather than *actionable*.

**Recommendation:** Add a hover/tooltip state showing war score components, battles fought, decisive battles, and war exhaustion. Keep the card compact at-a-glance, but reward hovering with the breakdown (exactly the EU4 pattern). In Godot, this can be a RichTextLabel tooltip or a small expanding panel.

#### Coalition war display: Needs fundamental rethink

The spec treats coalition wars as N separate bilateral cards. But a coalition IS the game's dramatic crisis. EU4 shows coalition wars as a single entry with all participants on one side.

**What the spec shows during a 3-nation coalition war:**
```
│ ■ Britain    +35    │
│ ████████░░░  T:8    │
├─────────────────────┤
│ ■ Prussia    -12    │
│ ░░░████████  T:3    │
├─────────────────────┤
│ ■ Austria    +5     │
│ █████░░░░░░  T:3    │
```

**What it SHOULD show:**
```
│ ⚔ THE BRITISH COALITION │
│ Leader: Britain          │
│ Posture: Aggressive      │
│ ■ Britain    +35  WE:12  │
│ ■ Prussia    -12  WE:28  │
│ ■ Austria    +5   WE:8   │
│ Combined: ~188k          │
```

This groups the coalition as a single strategic challenge with per-member detail. The posture tells the player whether the coalition is advancing or defending. War exhaustion per member identifies the "weak link" for diplomatic splitting (the core coalition-breaking mechanic from COALITION_SPEC §6).

Bilateral wars (non-coalition) keep the original compact card format.

#### Click → wizard handoff: Sufficient but could be richer

The diplomacy wizard handoff works. But EU4's "Sue for Peace" button is more direct — it skips the wizard's step 1 entirely and goes to peace terms. Our spec proposes this (`open_for_nation(nation)`), which is correct.

**One addition:** During coalition wars, clicking a member should show a tooltip "Coalition member — separate peace may be possible if war exhaustion is high" to teach the coalition-splitting mechanic. Clicking the coalition header should open the wizard targeting the coalition leader.

#### `/active_wars` endpoint vs embedding in `/state`

The spec correctly notes the alternative: embed `active_wars` in the existing `/state` response. **This is the better approach.** Reasons:
1. The panel updates on every command response anyway (same cadence as `/state`).
2. The data is tiny (~50 bytes per war).
3. A separate HTTP call adds latency and complexity for no benefit.
4. The diplomatic ledger already computes war_score_breakdown — reuse that code path.

**Recommendation:** Add `active_wars` to the `/state` response dict. Remove the separate endpoint.

#### Armistice display: Mostly correct, one issue

Showing armistice nations is good — the player should see the full war picture. But "not clickable" is wrong. The player may want to:
- Check treaty terms (what they gave up for the armistice).
- See when the armistice expires (already shown, but wizard could show more detail).
- Prepare a follow-up diplomatic action for when armistice ends.

**Recommendation:** Make armistice cards clickable but show the wizard with armistice-appropriate options (e.g., "Improve Relations", "Prepare Alliance" — whatever's valid for an ARMISTICE state). Gray out the card styling but don't block interaction.

#### Top 3 things EU4 shows that our spec doesn't address (and our data supports)

1. **War score component breakdown on hover.** EU4 shows Battles/Occupation/Ticking. We have Territory/Battles/Decisive/Capital — arguably MORE interesting. `calculate_war_score(return_components=True)` already returns this. The ledger already computes it. Not showing it in the HUD panel is the spec's biggest miss.

2. **Coalition as a single strategic entity.** EU4 groups coalition wars under one war entry with all members listed on the opposing side. The spec treats them as independent bilateral wars, which misrepresents the threat and misses our rich coalition data (posture, leader, per-member war exhaustion, friction).

3. **Acceptance likelihood hint / "when to negotiate" indicator.** EU4's peace screen shows a detailed acceptance modifier tooltip. We don't need the full formula on the HUD, but showing enemy war exhaustion (our closest equivalent to "willingness to negotiate") would tell the player WHEN to click. Without it, the player has to open the Diplomatic Ledger, navigate to the Threat tab, and find the member's WE — that's exactly the buried-information problem N4 is supposed to solve.

---

### 5. Honest Assessment

**Readiness: 5/10**

The spec correctly identifies the problem (wars invisible without opening full screen), picks the right solution pattern (EU4 bottom-right icons), and proposes sound Godot architecture. But the information density is too low to be strategically useful, and the coalition war display is flat-out wrong for our game's signature mechanic.

#### Top 3 Things the Spec Gets Right

1. **Bottom-right persistent HUD placement.** Exactly the EU4 pattern. CanvasLayer 25 between map (0) and screens (50) is correct. Hiding when screens/modals are open is correct. This is the right architectural call.

2. **Click → diplomacy wizard handoff with `open_for_nation()`.** This leverages existing infrastructure elegantly. The wizard already has the two-step flow, and adding a direct-to-step-2 entry point is clean. No new screens needed.

3. **Armistice inclusion.** Showing armistice nations keeps the full war picture visible. Most games only show active wars — including the cooling-off period helps the player plan ahead.

#### Top 3 Gaps / Risks

1. **No war score breakdown = decorative, not actionable.** The single number tells the player nothing they can ACT on. "You're at +35 vs Britain" — great, but is that from holding territory (keep holding) or from battles (keep fighting) or from holding their capital (defend it)? The backend already has `calculate_war_score(return_components=True)` — the data is literally sitting there unused. **This is the gap that would make players ignore the panel.**

2. **Coalition wars displayed as individual cards = misrepresents the game's signature mechanic.** Coalition formation is a dramatic, multi-session event with its own spec, popup, posture system, and breaking mechanics. Showing it as "3 separate wars" in the HUD undermines the design. The player needs to see "THE BRITISH COALITION" as a single grouped threat with per-member war exhaustion (the key to splitting them). Without grouping, the panel actively misinforms the player about what they're facing.

3. **Missing war exhaustion = player can't time their diplomacy.** The entire coalition-breaking strategy revolves around targeting high-WE members (COALITION_SPEC §6a-c). The spec gives the player NO way to see WE from the HUD — they must open Diplomatic Ledger → Threat/Coalition tab → find the member. That's 3 clicks into a full-screen overlay to get the single most important number for coalition diplomacy. If the war panel is supposed to surface war information, WE belongs here.

#### Verdict: Needs a revision pass before implementation

The architectural foundation (scene tree, layering, visibility rules, wizard handoff) is solid and should be kept. The data model needs enrichment:
- Add `war_score_breakdown` to each war entry (reuse ledger code).
- Add `war_exhaustion` per opponent (fog-filter via `_get_nation_visibility`).
- Add coalition grouping: when `active_coalition` is active, group member wars under a coalition header showing leader + posture.
- Add `battles_fought` and `decisive_battles_won` counts.
- Consider hover-to-expand for the compact card format.
- Embed in `/state` response instead of separate endpoint.

These changes add ~30 lines of backend code (the data already exists) and ~50 lines of Godot rendering (coalition header + tooltip). The spec's core architecture doesn't change — it's an enrichment pass, not a rewrite.
