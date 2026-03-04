# Phase 8 Sessions 8A–8D: UI, Debug & Polish

> **Expands the original "Session 8: Diplomatic Ledger UI + Polish" into 4 sub-sessions.**
> **Created:** March 4, 2026 (Pre-Session 8 Audit)
> **Source:** DIPLOMACY_SPEC §14, COALITION_SPEC §9, audit of existing Godot/backend infrastructure.

---

## Why 4 Sessions

The original spec's Session 8 listed 6 UI bullets. A full audit of the spec requirements vs existing infrastructure found **19 UI gaps, 12 backend gaps, and zero debug tools**. This is too much for one session and too important to skip — without these features, the entire diplomacy/coalition system is unplayable in Godot.

---

## Session Dependencies

```
8A (Backend + Debug)  ──→  8B (Ledger UI + Top Bar)
        │                          │
        └──────────→  8C (Popups + Notifications)
                                   │
                      8D (Dispatch + Polish + Deferred)
```

8A is the foundation — everything else depends on it.
8B and 8C can run in parallel (independent Godot scenes).
8D comes last — polish and deferred items benefit from playtesting 8B+8C.

---

## Session 8A: Backend Ledger Builder + Debug Arsenal

**Focus:** All backend data assembly + every debug tool. Nothing touches Godot. This session makes Sessions 8B–8D possible AND makes the entire Phase 8 system inspectable.

**Risk:** LOW (pure backend, patterns established from `ledger.py` and `marshal_overview.py`)

### Scope — Diplomatic Ledger Backend

- **New file `backend/game_logic/diplomatic_ledger.py`** — `build_diplomatic_ledger(world)` assembling 4 tab dicts:
  - **Tab 1 (Nations):** Per nation: diplomatic_state, relation, diplomat (name/personality/skill), army strength (sum of marshals), regions controlled, active treaties, vassal eligibility
  - **Tab 2 (Treaties):** Per active treaty: nation pair, type, clauses, duration, cancel cost (1 DP)
  - **Tab 3 (Threat & Coalition):** threat_level, threat_tier, threat_sources_this_turn, qualifying nations, coalition_brewing (turns remaining), active_coalition (name, leader, members, posture, war exhaustion per member, combined strength)
  - **Tab 4 (Talleyrand):** diplomat trust + label, skill, DP remaining/max, active_diplomatic_mission (type, target, duration, effect, progress), proposal_in_transit (target, type, ETA), pending envoys (from diplomatic_queue), sabotage warnings (from undetected_sabotages)
- **New endpoint `GET /diplomatic_ledger`** in `main.py` — returns `{ success, ledger: { nations, treaties, threat_coalition, talleyrand } }`
- **Surface top-bar fields in `/test` response** — add to `game_state`: `diplomatic_points`, `max_diplomatic_points`, `talleyrand_state`, `talleyrand_mission_summary` (string), `threat_level`, `coalition_brewing` (bool + turns), `pending_envoy_count` (int from diplomatic_queue length)
- **Pass-through wiring in `main.py`** command response for: `coalition_popup`, `diplomatic_sabotage`, `vassal_rebellion_imminent` (same pattern as `glorious_charge_popup`, `redemption_event`)

### Scope — Debug Cheat Commands

10 commands, gated behind `LLM_MODE=mock` or `DEBUG_MODE`:

| Command | Effect | Implementation |
|---------|--------|----------------|
| `cheat set_threat <value>` | Direct-set threat_level (0–100) | `world.threat_level = clamp(value, 0, 100)` |
| `cheat set_relation <nation> <value>` | Set nation_relations for France↔nation | `modify_nation_relation()` or direct set |
| `cheat give_dp <amount>` | Add to diplomatic_points | `world.diplomatic_points += amount` |
| `cheat trigger_coalition` | Instant-form coalition from qualifying nations | `coalition.form_coalition(qualifying, world)` |
| `cheat set_war_exhaustion <nation> <value>` | Direct-set war_exhaustion | `world.war_exhaustion[nation] = value` |
| `cheat set_diplo_state <nation> <state>` | Jump to any diplomatic state | Set `diplomatic_states[key]`, update relations if needed |
| `cheat create_vassal <nation>` | Create treaty vassal instantly | `vassal.create_vassal_treaty(world, "France", nation, 0)` |
| `cheat set_vassal_loyalty <nation> <value>` | Direct-set loyalty | `world.vassals[nation]["loyalty"] = value` |
| `cheat set_talleyrand_trust <value>` | Set diplomat trust | `world.diplomats["France"].trust = value` |
| `cheat queue_ai_proposal <nation> <type>` | Build + queue an AI proposal | Construct proposal dict, append to `diplomatic_queue` |

**Routing:** Add `_execute_cheat()` to `executor.py`. Mock parser in `llm_client.py` detects "cheat " prefix. Guard: reject if `LLM_MODE != "mock"` and `DEBUG_MODE != True`.

### Scope — Debug Endpoints

8 endpoints, `DEBUG_MODE=True` only:

| Endpoint | Returns |
|----------|---------|
| `GET /debug/diplomatic_status` | All states, relations, treaties, vassals, DP, Talleyrand state — one readable snapshot |
| `GET /debug/war_scores` | Per nation-pair war score WITH component breakdown (territory, battles, decisive, capital) |
| `POST /debug/acceptance_preview` | Acceptance formula for a proposal body — all 10+ components + final outcome |
| `GET /debug/coalition_status` | Threat level, tier, brewing state, qualifying nations, active coalition, war exhaustion per nation |
| `GET /debug/threat_sources` | `threat_sources_this_turn` breakdown |
| `GET /debug/proposal_cooldowns` | `ai_proposal_cooldowns` + `player_proposal_cooldowns` |
| `GET /debug/vassal_loyalty/{nation}` | Loyalty value + per-modifier breakdown (autonomy, garrison, shared_enemy, relations, investment) |
| `GET /debug/proposal_queue` | Queued AI proposals with types, source nations, ETAs |

**Note:** `calculate_war_score()` currently returns int only. Extend to optionally return components dict for the debug endpoint.

### Estimated Tests: ~55

- Ledger builder tests: 4 tabs × ~5 tests each = ~20
- Cheat command tests: 10 commands × ~2 tests each = ~20
- Debug endpoint tests: ~8
- Pass-through wiring tests: ~7

### Gate Criteria

1. `GET /diplomatic_ledger` returns all 4 tabs with correct data for default game state
2. All 10 cheat commands modify state correctly (verified via `/debug/diplomatic_status`)
3. All 8 debug endpoints return structured JSON
4. `coalition_popup` field passes through in `/command` response when coalition forms
5. Top-bar fields present in `/test` response

### Files Touched

| File | Change |
|------|--------|
| `backend/game_logic/diplomatic_ledger.py` | NEW — ledger builder |
| `backend/main.py` | New endpoints (`/diplomatic_ledger`, 8 debug), pass-throughs, `/test` top-bar fields |
| `backend/commands/executor.py` | `_execute_cheat()` routing |
| `backend/ai/llm_client.py` | Mock parser "cheat " prefix detection |
| `backend/game_logic/diplomacy.py` | Extend `calculate_war_score()` to return components (optional param) |
| `godot-client/.../api_client.gd` | New `get_diplomatic_ledger()` method |
| `tests/test_session8a_ledger_debug.py` | NEW — all tests |

---

## Session 8B: Diplomatic Ledger Godot UI + Top Bar

**Focus:** The primary information screen players use to understand diplomacy. Consumes the endpoints from 8A.

**Risk:** MEDIUM (new Godot scene, hotkey conflict resolution)

### Scope — D Key Conflict Resolution

- Rebind Dispatch Re-read from **D → R** (for "Re-read")
- **D key** now opens Diplomatic Ledger
- Update `top_bar.gd` button labels, registration, and hotkey handling
- Update `main.gd` `_unhandled_input()` hotkey map

### Scope — Diplomatic Ledger Scene

New `diplomatic_ledger.gd` + `diplomatic_ledger.tscn` (CanvasLayer 50). Same pattern as `strategic_ledger.gd`:

- BackgroundOverlay (click-to-close) → PanelContainer → VBoxContainer → SubTabRow → ScrollContainer → RichTextLabel (BBCode)
- 4 tabs, number keys **1–4**
- Title: `"DIPLOMATIC LEDGER"` with DP display: `DP: 3/3`

**Tab 1 — Nation Overview** (default):
- Per nation row: name, diplomatic state (color-coded: WAR=red, PEACE=grey, ALLIANCE=green), relation value (color-coded: <-50 red, >+50 green), diplomat name/personality/skill, regions controlled, army strength (comma-formatted), treaty summary
- Source: `ledger.nations`

**Tab 2 — Active Treaties:**
- Per treaty: nation pair, type, clause list, duration (permanent or turns remaining), cancel cost
- Source: `ledger.treaties`

**Tab 3 — Threat & Coalition:**
- Threat bar visualization (green 0–29 / amber 30–59 / red 60+)
- Threat source table (per-turn breakdown)
- Qualifying nations list (who would join next coalition)
- Coalition status: "No coalition" / "Brewing (X turns)" / "Active: [Name]"
- Active coalition card: members, leader, posture, war exhaustion per member (bar), strength per member
- Source: `ledger.threat_coalition`

**Tab 4 — Talleyrand Status:**
- Trust value + label (Loyal/Wary/Suspicious/Treacherous), skill
- DP remaining/max
- Current mission (type, target, duration, effect, progress)
- Proposal in transit (target, type, ETA)
- Pending envoys (count + details)
- Sabotage warning (if any)
- Source: `ledger.talleyrand`

### Scope — Top Bar Extensions

| Field | Display | Data Source |
|-------|---------|------------|
| DP counter | `DP: 2/3` (same style as AP) | `game_state.diplomatic_points` / `game_state.max_diplomatic_points` |
| Threat indicator | Hidden ≤29, amber 30–59, red 60+, pulsing when brewing | `game_state.threat_level`, `game_state.coalition_brewing` |
| Talleyrand status | `Talleyrand: Idle` / `Courting Austria` / `In Transit (Prussia)` | `game_state.talleyrand_mission_summary` |
| Envoy indicator | `[!] 1 envoy` (clickable → triggers first proposal dialogue) | `game_state.pending_envoy_count` |

### Estimated Tests: ~15 (backend tested in 8A; Godot manual)

- Tab rendering tests: ~8 (verify BBCode output for each tab)
- Top bar field tests: ~7 (verify data presence + formatting)

### Manual Test Plan

- Open ledger during WAR / PEACE / ALLIANCE — verify color coding
- Threat indicator appears at 30, turns red at 60, pulses when brewing (use `cheat set_threat`)
- Envoy click opens proposal dialogue (use `cheat queue_ai_proposal`)
- D toggles ledger, R toggles dispatch, no conflicts with T/L/G
- All 4 tabs render correctly, number keys switch them
- Esc closes ledger

### Gate Criteria

1. D opens Diplomatic Ledger with 4 functioning tabs
2. R opens Dispatch Re-read (moved from D)
3. Top bar shows DP counter + threat indicator
4. Ledger data matches backend state (verify with cheat commands)
5. No hotkey conflicts with existing screens

### Files Touched

| File | Change |
|------|--------|
| `godot-client/.../diplomatic_ledger.gd` | NEW — ledger controller |
| `godot-client/.../diplomatic_ledger.tscn` | NEW — ledger scene |
| `godot-client/.../top_bar.gd` | D→R rebind, new button, DP/threat/Talleyrand/envoy fields |
| `godot-client/.../top_bar.tscn` | New UI elements for diplomatic fields |
| `godot-client/.../main.gd` | Ledger instantiation, registration, hotkey update, top bar data wiring |

---

## Session 8C: Popups + Notifications

**Focus:** Every modal dialog and notification template the diplomacy/coalition systems need. Mixed backend wiring + Godot scenes.

**Risk:** MEDIUM (6 new popup scenes, notification wiring across multiple backend files)

### Scope — Popups (6 new dialogs)

| Popup | Trigger Field | Spec | Buttons | Complexity |
|-------|--------------|------|---------|------------|
| **Coalition Declaration** | `coalition_popup` in command response | COALITION §9d | [Continue] | Medium — dramatic reveal: coalition name, members, combined strength, posture |
| **AI Proposal Response** | `pending_diplomatic_dialogue` type=`incoming_proposal` | DIPLOMACY §6f | [Accept] [Counter] [Reject] | High — clause list, Talleyrand assessment, acceptance feedback |
| **Talleyrand Objection** | `diplomatic_objection` in dialogue flow | DIPLOMACY §3e | [Proceed] [Modify] [Cancel] | Medium — concern level display, defiance risk |
| **Talleyrand Sabotage Discovery** | `diplomatic_sabotage` in command response | DIPLOMACY §3c | [Confront] [Overlook] | Medium — ordered vs delivered comparison |
| **Talleyrand Redemption** | `talleyrand_redemption` in command response | DIPLOMACY §3d | [Apologize] [Replace] [Continue] | Medium — 3 choices with consequence previews |
| **Vassal Rebellion Imminent** | `vassal_rebellion_imminent` in command response | DIPLOMACY §8d | [Invest] [Garrison] [Accept] | Low — loyalty display, action buttons |

**Implementation pattern (per popup):**
1. Create `.gd` script with `show_[event](data)` method + `[choice]_made` signal
2. Create `.tscn` scene (CanvasLayer 100, modal)
3. In `main.gd _ready()`: instantiate + connect signal to `_on_[choice]_made()`
4. In `_on_[choice]_made()`: disable input, call backend response endpoint, handle result
5. Add to `_is_modal_dialog_open()` check

**Dialog priority order (extends existing):**
1. Objections (existing)
2. Glorious Charge (existing)
3. **Coalition Declaration** (new — before capture choice)
4. Capture Choice (existing)
5. **Talleyrand Objection** (new — before diplomatic actions)
6. **AI Proposal Response** (new — incoming diplomatic proposals)
7. Clarification (existing)
8. **Talleyrand Sabotage Discovery** (new)
9. **Talleyrand Redemption** (new)
10. **Vassal Rebellion Imminent** (new)
11. Redemption (existing marshal)
12. Enemy Phase (existing)

### Scope — Notification Templates (18 types)

**Coalition (7 types):** already have notification constants in `notifications.py` from Session 7 — need firing logic:

| Notification | Priority | Persistence | Trigger Location |
|---|---|---|---|
| `COALITION_THREAT_TENSION` (threat ≥ 30) | NORMAL | Dismissible | `process_coalition_turn()` |
| `COALITION_THREAT_MURMURS` (threat ≥ 40) | WARNING | Persistent until < 30 | `process_coalition_turn()` |
| `COALITION_BREWING` | HIGH | Persistent, updates countdown | `process_coalition_turn()` |
| `COALITION_DECLARED` | CRITICAL | Persistent until dismissed | `form_coalition()` |
| `COALITION_MEMBER_LEFT` | NORMAL | Dismissible | `remove_coalition_member()` |
| `COALITION_DISSOLVED` | NORMAL | Dismissible | `dissolve_coalition()` |
| `COALITION_COOLDOWN_ENDED` | NORMAL | Dismissible | `process_coalition_turn()` |

**Diplomacy (11 types):** need notification constants + firing logic:

| Notification | Priority | Trigger Location |
|---|---|---|
| `DIPLOMATIC_PROPOSAL` | HIGH | `deliver_ai_proposal()` |
| `TREATY_SIGNED` | MEDIUM | `_ratify_treaty()` |
| `TREATY_BROKEN` | HIGH | `break_treaty()` |
| `SABOTAGE_DISCOVERED` | HIGH | dispatch sabotage discovery |
| `VASSAL_REBELLION_IMMINENT` | HIGH | `process_vassal_loyalty()` when loyalty < 10 |
| `VASSAL_REBELLION` | HIGH | `process_vassal_loyalty()` when loyalty = 0 |
| `ALLIANCE_CASCADE_WAR` | HIGH | `_process_war_cascade()` |
| `WAR_DECLARED` | HIGH | `declare_war()` |
| `VASSAL_COURTING_DETECTED` | MEDIUM | `turn_manager` enemy courting |
| `DP_INSUFFICIENT` | MEDIUM | proposal attempt with 0 DP |
| `DEFECTION_CASCADE` | HIGH | `process_vassal_loyalty()` multi-vassal |

### Estimated Tests: ~40

- Popup data flow tests: 6 popups × ~3 tests = ~18
- Notification firing tests: 18 types × ~1 test = ~18
- Integration: ~4

### Gate Criteria

1. Coalition forms → declaration popup appears with correct member/strength/posture data
2. AI proposal arrives → response popup with Accept/Counter/Reject buttons
3. Threat hits 30 → notification appears in notification bar
4. Coalition brewing → persistent notification with countdown that updates each turn
5. Sabotage discovered → confrontation popup with ordered-vs-delivered comparison
6. Vassal loyalty < 10 → rebellion imminent popup

### Files Touched

| File | Change |
|------|--------|
| 6 new `.gd` + `.tscn` pairs | Popup scenes (coalition, proposal, objection, sabotage, redemption, vassal) |
| `godot-client/.../main.gd` | Popup instantiation, signal wiring, dialog priority, `_is_modal_dialog_open()` |
| `backend/notifications.py` | 11 new diplomatic notification constants |
| `backend/game_logic/coalition.py` | Wire 7 notification fire points |
| `backend/game_logic/diplomacy.py` | Wire notification fire points (treaty, war, cascade) |
| `backend/game_logic/vassal.py` | Wire notification fire points (rebellion, courting) |
| `backend/ai/ai_diplomacy.py` | Wire notification on proposal delivery |
| `tests/test_session8c_popups_notifications.py` | NEW |

---

## Session 8D: Dispatch Integration + Polish + Deferred Mechanical

**Focus:** Morning Dispatch diplomatic section, campaign log events, fog filtering, and spec-deferred mechanical items.

**Risk:** MEDIUM (AI-AI diplomacy is new logic, fog edge cases)

### Scope — Morning Dispatch Diplomatic Section

~20 diplomatic event types added to `dispatch.py` builder (per DIPLOMACY_SPEC §10d):

| Event Type | Template | Fog Rule |
|---|---|---|
| `diplomatic_proposal_sent` | "Talleyrand has departed for the {nation} court." | Player always sees |
| `diplomatic_proposal_returned` | "Talleyrand returns from {nation} with a response." | Player always sees |
| `diplomatic_sabotage_discovered` | "Talleyrand altered your proposal to {nation}." | Player always sees |
| `diplomatic_treaty_signed` | "{nation_a} and {nation_b} have signed a {treaty_type}." | PARTIAL+ on either |
| `diplomatic_treaty_broken` | "{nation} has broken the {treaty_type}." | PARTIAL+ on breaker |
| `diplomatic_war_declared` | "{nation} has declared war on {target}." | PARTIAL+ on declarer |
| `diplomatic_vassal_unrest` | "Talleyrand reports unrest in {nation}." | Player's vassal |
| `diplomatic_vassal_rebellion_imminent` | "{nation} is on the verge of rebellion!" | Player's vassal |
| `diplomatic_vassal_rebellion` | "{nation} has rebelled!" | Player's vassal |
| `diplomatic_ai_proposal` | "A {nation} envoy has arrived with a proposal." | Always (triggers popup) |
| `diplomatic_mission_progress` | "Talleyrand's efforts in {nation} continue. Relations now at {value}." | Player's mission |
| `diplomatic_mission_paused` | "Talleyrand's efforts curtailed — insufficient resources." | Player's mission |
| `diplomatic_mission_cancelled` | "Talleyrand's efforts in {nation} have collapsed." | Player's mission |
| `diplomatic_feasibility_report` | "Talleyrand assesses: {difficulty_tier}." | Player's request |
| `diplomatic_alliance_cascade` | "{nation} enters the war via alliance with {ally}." | PARTIAL+ on declarer |
| `diplomatic_vassal_courting` | "Talleyrand reports {enemy} agents in {vassal_capital}." | 60% detection chance |
| `diplomatic_continental_system` | "{nation} has {joined/withdrawn from} the Continental System." | Participant or France |
| `diplomatic_carved_vassal_created` | "The {carved_name} has been established under French protection." | France always |
| `diplomatic_carved_vassal_dissolved` | "The {carved_name} has ceased to exist." | France always |
| `diplomatic_defection_cascade` | "The empire trembles — multiple vassals are wavering!" | France always |

- Coalition section already wired (Session 7) — verify and polish
- `dispatch_view.gd` renders new diplomatic section with color-coded event types

### Scope — Campaign Log Diplomatic Events

- Add diplomatic event types to `campaign_log.py` fog filter whitelist
- Turn-grouped display in campaign log overlay

### Scope — Fog-Filtered Diplomatic Intel

- Filter diplomatic events by visibility tier before surfacing in dispatch/log
- Enemy treaty changes only visible at PARTIAL+ on relevant nation
- Per FOG_OF_WAR_SPEC rules

### Scope — Deferred Mechanical Items (from DIPLOMACY_SPEC §14 DD7)

| Item | Description | Spec Ref |
|------|-------------|----------|
| **AI-AI diplomacy** | AI nations propose to each other (shared enemies, relation thresholds). Events surface through dispatch. | §9c |
| **Special acceptance bonuses** | Nation-specific desires: Prussia wants territory, Austria wants guarantees, Britain wants gold. | §6d |
| **Schemer bias calibration** | Playtest Talleyrand sabotage rates, adjust probability curve if needed. | §3a |

### Scope — Test Fixtures

- Pre-built world states for key scenarios: "coalition about to form", "vassal about to rebel", "peace achievable", "brewing countdown at 1"
- Acceptance formula edge case parametrize tests

### Estimated Tests: ~50

- Dispatch diplomatic events: ~20 event types × ~1 test = ~20
- Campaign log integration: ~5
- Fog filtering: ~8
- AI-AI diplomacy: ~10
- Special acceptance bonuses: ~5
- Test fixtures: ~2 (fixture validation)

### Gate Criteria

1. Morning dispatch shows diplomatic events (proposal sent/returned, treaty signed, war declared)
2. Campaign log includes diplomatic entries with correct turn grouping
3. AI-AI treaty event appears in dispatch ("Britain and Prussia have signed a defensive alliance")
4. Fog properly hides enemy diplomatic activity at NONE/STALE visibility
5. Special acceptance bonuses affect formula (verify with `/debug/acceptance_preview`)
6. Schemer sabotage rate feels fair across 10-turn playtest (manual)

### Files Touched

| File | Change |
|------|--------|
| `backend/game_logic/dispatch.py` | ~20 diplomatic event type builders, fog filtering |
| `godot-client/.../dispatch_view.gd` | Render new diplomatic section |
| `backend/campaign_log.py` | Diplomatic event types added to whitelist |
| `godot-client/.../campaign_log.gd` | Diplomatic event rendering |
| `backend/game_logic/diplomacy.py` | AI-AI diplomacy logic, special acceptance bonuses |
| `backend/ai/ai_diplomacy.py` | AI-AI proposal triggers (extend existing P1-P7) |
| `backend/models/intel.py` | Diplomatic fog filtering helpers |
| `tests/test_session8d_dispatch_polish.py` | NEW |
| `tests/conftest.py` or `tests/fixtures/` | Scenario fixtures |

---

## Total Estimates

| Session | Tests | Risk | Focus |
|---------|-------|------|-------|
| 8A | ~55 | LOW | Backend ledger + debug tools |
| 8B | ~15 + manual | MEDIUM | Godot ledger + top bar |
| 8C | ~40 | MEDIUM | Popups + notifications |
| 8D | ~50 | MEDIUM | Dispatch + polish + deferred |
| **Total** | **~160** | | |

Phase 8 total: ~525 tests across 12 sessions (1A through 8D).

---

## Document References

| Doc | What to update after each session |
|-----|----------------------------------|
| `STATUS.md` | Session summary, test count, "Next Steps" |
| `ROADMAP.md` | Phase 8 session table status |
| `CLAUDE.md` | "Current Phase" → "Up Next" |
| `SYSTEMS_REFERENCE.md` | If new cheat commands or debug endpoints added |
| `SAVE_FORMAT_REFERENCE.md` | If new serialized fields |
| `MANUAL_TEST_PLAN.md` | Session 8B/8C manual test items |
