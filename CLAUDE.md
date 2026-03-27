# CLAUDE.md

Napoleonic strategy game. Players type commands ("Marshal Ney, attack Wellington") and AI marshals respond based on personality. Godot 4 frontend, FastAPI backend on port 8005. For game vision see `docs/VISION.md`.

## Golden Rules

1. **Combat modifiers: SINGLE SOURCE in `marshal.py`** — `get_attack_modifier()` / `get_defense_modifier()` only. `combat.py` reads them, never recalculates.
2. **All numbers to Godot: `int()`** — Godot crashes on floats.
3. **All marshals in ONE dict:** `world.marshals` (not separate player/enemy).
4. **State clearing: AFTER reading** — get the value, use it, then clear.
5. **Enemy AI uses SAME executor as player** (Building Blocks principle).
6. **LLM never affects mechanics** — parsing only, executor is deterministic.
7. **Port 8005** (not 8000!) — change in BOTH `backend/main.py` AND `godot-client/.../api_client.gd`.

## Current Phase

**Phases 6, 6.5, 7 Core, 7b — COMPLETE.** See `docs/STATUS.md` for full session history.

### Up Next

- **Systems Audit V3 Fix Plan — Sessions 1-9 COMPLETE, Session 10 is NEXT.** 158 bugs across 10 required + 1 optional sessions. Session 1: 8 bugs fixed, 26 tests. Session 2: 14 bugs fixed, 20 tests. Session 3: 17 bugs fixed, 22 tests. Session 4: 15 bugs fixed, 26 tests. Session 5: 12 bugs fixed, 24 tests. Session 6: 11 bugs fixed, 19 tests. Session 7: 13 bugs fixed, 15 tests. Session 8: 14 bugs fixed, 20 tests. Session 9: 13 bugs fixed, 20 tests. See `docs/SYSTEMS_AUDIT_V3_FIX_PLAN.md`. **After each session, update `docs/STATUS.md` to mark it done and indicate which session is next.**
- ~~**Systems Audit V2 Fix Plan — ALL 7 SESSIONS COMPLETE.**~~ 56 bugs fixed, 7,040 tests. See `docs/SYSTEMS_AUDIT_V2_FIX_PLAN.md`.
- **Playtest Bug Fixes (March 2026 Review).** 16-turn playtest found 3 critical + 3 major + 4 minor bugs + 4 balance concerns. Session 1: armistice deadlock, self-combat, turn skip. Session 2: raw state names, parse failures. Session 3: minor fixes + balance. See `docs/PLAYTEST_REVIEW_2026_03.md`.
- **Diplomacy Button — COMPLETE.** Session A (backend) + Session B (Godot wizard UI) + final edge case fixes (2 bugs, 2 hardening). 108 button tests. See `docs/DIPLOMACY_BUTTON_SPEC.md`.
- **Diplomacy Refinement Phase 5: Design Depth.** Waves 1-2, 2.5 DONE. Wave 3 (Player Feedback, 8 items) next. See `docs/DIPLO_REFINEMENT.md`.
- **Diplomacy Design Fixes (DA sessions).** DA-1, DA-2 DONE. DA-4 (N4 War Status Panel) DONE — 3-layer HUD system (war_status_panel + war_detail_popup + wizard handoff), 32 tests. DA-3 (offensive cascade + friction) remaining. See `docs/DIPLOMACY_DESIGN_FIXES.md`.
- **Phase 7b remaining:** V2b COMPLETE. Tactical Triangle COMPLETE. Strategic Order UI COMPLETE. Gates 5+6 PASSED. Jealousy (SPEC v3 DRAFTED — needs design gate approval). Coalition Trigger moved to Phase 8.
- **Phase 6.5 remaining:** Map Renderer only (art-blocked). Tutorial Infrastructure deferred to Pre-EA.
- **Phase 8: Diplomacy — COMPLETE.** ALL 11 sessions done (1A through 8D). ~580 tests. See `docs/SESSION_8_PLAN.md`.
- **Diplomacy Audits — ALL COMPLETE.** Code audit (20 bugs, 145 tests). Creative audit (7.8/10). Comprehensive creative audit (6.5/10, 41 new items → Phase 5). March 2026 deep audit (43 bugs, 112 tests). See `docs/DIPLOMACY_AUDIT_2026_03.md`.
- **Deep Audit Fix Plan — ALL 9 SESSIONS COMPLETE.** 43 bugs fixed, 129 new tests (6,703 total). Session 9: 12 spec doc updates, 6 hardening fixes, ~900 lines dead code removed. See `docs/DEEP_AUDIT_FIX_PLAN.md`.
- **Systems Audit Fix Plan — ALL 12 CORE SESSIONS COMPLETE.** ~148 findings fixed, 193 new tests (6,904 total). Sessions 13-14 optional (architecture refactoring). See `docs/SYSTEMS_AUDIT_FIX_PLAN.md`.
- **Systems Audit V2 Fix Plan — ALL 7 SESSIONS COMPLETE.** 56 confirmed bugs fixed, 7,040 tests. See `docs/SYSTEMS_AUDIT_V2_FIX_PLAN.md`.
- **Diplomacy Refinement Phases 1-4 — COMPLETE.** 55 items done, 326 tests. See `docs/DIPLO_REFINEMENT.md`.

### Design Gates

#### APPROVED — Coalition Spec v1.1:
- Master-audited: 4 CRITICAL + 4 MAJOR findings fixed. `docs/COALITION_SPEC.md`
- **Approved Mar 2, 2026.** Ready for Session 7 implementation.

#### APPROVED — Starting Situation Balance (COALITION_SPEC §16):
- R1: Saxony 18k troops — APPLIED to §1c. R2: Austria-Britain NON_AGGRESSION — APPLIED to §1e. R3: Battlefield Diplomacy +10 — APPLIED to §6b. R4: Prussia -40 — APPLIED to §1e. R5: Saxony OPEN_BORDERS — APPLIED to §1e.
- **Approved Mar 2, 2026.** All 5 changes in DIPLOMACY_SPEC.

#### Jealousy System — v3.1 spec, needs final approval (DO NOT CODE WITHOUT USER APPROVAL):
- Core design settled: Glory Ladder targeting, personality expressions, escalation, confrontation popups
- Literal expression: Candidate B (Vindicated Garrison / Obsessive Competence)
- Top of ladder: +1 all core stats (shock/fire/admin) while #1 — designed, needs approval
- Glory loss: Defeats cost glory (-1 base, modifiers) — keeps ladder dynamic
- §6b Rivalry Confrontation: Deferred to v3.1 implementation
- Full spec: `docs/JEALOUSY_SPEC.md`



---

## File Reference

### Backend Core

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI endpoints, response formatting |
| `backend/commands/executor.py` | All action execution (_execute_*) |
| `backend/commands/parser.py` | Command parsing, fuzzy matching |
| `backend/commands/disobedience.py` | V1 objection system, trust values |
| `backend/commands/objection_v2.py` | V2a objection system (ConcernLevel triggers) |
| `backend/commands/defiance.py` | V2b defiance system (chance calc, fallback table, outcomes) |
| `backend/commands/strategic.py` | Strategic order per-turn executor |
| `backend/commands/vindication.py` | Vindication tracker |
| `backend/models/marshal.py` | Marshal class, combat modifiers, states, serialization |
| `backend/models/world_state.py` | Game state, turn processing, action economy |
| `backend/models/region.py` | 19 regions (REGIONS_DATA source of truth), terrain/region type constants, NATION_CAPITALS, starting_controller, grid_position |
| `backend/models/personality.py` | PersonalityType enum |
| `backend/models/personality_modifiers.py` | Combat bonuses by personality |
| `backend/campaign_log.py` | Campaign log fog filter + one-liner formatter |
| `backend/game_logic/combat.py` | Combat resolution, messages |
| `backend/game_logic/battle_report.py` | Post-battle modifier snapshots, report generation, Berthier observations |
| `backend/game_logic/relationship.py` | Win/Loss Relationship Formula (severity, ordered pairs, cooldown) |
| `backend/notifications.py` | Notification system (EU4-style persistent alerts, collector, dismiss) |
| `backend/game_logic/dispatch.py` | Morning Dispatch builder (fog-filtered turn-start briefing), stores last_morning_dispatch on WorldState |
| `backend/game_logic/ledger.py` | Strategic Ledger builder (6 sections: forces, territories, economy, intel, manpower, orders) |
| `backend/game_logic/marshal_overview.py` | Marshal Management builder (player marshal cards with identity, ability, stats, trust, status, relationships) |
| `backend/game_logic/turn_manager.py` | Turn flow, enemy phase |
| `backend/ai/enemy_ai.py` | Enemy AI decision tree (P1-P8) |
| `backend/ai/llm_client.py` | LLM integration (fast parser + Anthropic) |
| `backend/ai/strategic_parser.py` | Strategic command detection |
| `backend/ai/validation.py` | VALID_ACTIONS (single source of truth for LLM) |
| `backend/ai/prompt_builder.py` | Context-aware LLM prompts |
| `backend/intel_report.py` | Berthier Intelligence Report (fog-filtered status view) |
| `backend/models/diplomat.py` | DiplomaticRepresentative class, starting diplomats |
| `backend/game_logic/diplomacy.py` | Diplomacy engine: transitions, war score, acceptance formula, DP, war declaration, cascade, trade income |
| `backend/game_logic/ai_diplomacy.py` | AI proposal generation (P1-P7 triggers), M3 counter-offer, alliance conflict check, anti-spam |
| `backend/game_logic/diplomatic_advisory.py` | Advisory conversations: threat assessment, nation analysis, action recommendations |
| `backend/game_logic/coalition.py` | Coalition system: threat accumulation/decay, formation/brewing/instant, leader/posture, AI friction/convergence, war exhaustion, British subsidy, dissolution/cooldown |
| `backend/game_logic/diplomatic_ledger.py` | Diplomatic Ledger builder (4 tabs: nations, treaties, threat_coalition, talleyrand) with fog-filtered army strength |
| `backend/game_logic/war_status.py` | War Status Panel data builder: `build_active_wars()` produces war/coalition/armistice data for HUD, embedded in every response via `_include_popup_passthroughs()` |
| `backend/game_logic/vassal.py` | Vassal system: creation, loyalty, rebellion, cascade, tribute, investment, autonomy, marshal assimilation, Continental System |
| `backend/commands/diplomatic_defiance.py` | Talleyrand sabotage: defiance chance, sabotage types, discovery, confrontation, pre-proposal objection, redemption |
| `backend/save_manager.py` | Save/load file I/O, autosave |

### Godot Core

| File | Purpose |
|------|---------|
| `api_client.gd` | Backend communication |
| `game_manager.gd` | Game state coordination |
| `map.gd` | Map rendering, fog overlay, fogged enemy icons |
| `main.gd` | Terminal UI, response handling |
| `pause_menu.gd` | Pause menu overlay (Phase 6.5) |
| `campaign_log.gd` | Campaign log overlay (Phase 6.5), CanvasLayer 50 |
| `notification_bar.gd` | Notification bar (Phase 6.5), reparented into top bar |
| `top_bar.gd` | Top bar controller (Session A): screen management, hotkeys, notifications, turn counter |
| `dispatch_view.gd` | Dispatch re-read screen (Session A): CanvasLayer 50, BBCode rendering |
| `strategic_ledger.gd` | Strategic Ledger screen (Session B): CanvasLayer 50, 6 sub-tabs, number key switching, Orders tab cancel buttons |
| `marshal_management.gd` | Marshal Management screen: CanvasLayer 50, card-based marshal view, G key toggle |
| `diplomatic_ledger.gd` | Diplomatic Ledger screen (Session 8B): CanvasLayer 50, 4 sub-tabs (Nations/Treaties/Threat/Talleyrand), D key toggle |
| `coalition_declaration_popup.gd` | Coalition declaration popup (Session 8C): CanvasLayer 100, BBCode, [Continue] |
| `incoming_proposal_popup.gd` | AI proposal popup (Session 8C): [Accept][Counter][Reject] |
| `talleyrand_objection_popup.gd` | Diplomatic objection popup (Session 8C): [Proceed][Modify][Cancel] |
| `sabotage_discovery_popup.gd` | Sabotage discovery popup (Session 8C): [Confront][Overlook] |
| `talleyrand_redemption_popup.gd` | Talleyrand redemption popup (Session 8C): [Apologize][Replace][Continue] |
| `vassal_rebellion_popup.gd` | Vassal rebellion imminent popup (Session 8C): [Invest][Garrison][Accept] |
| `war_status_panel.gd` | War Status Panel HUD (N4a): CanvasLayer 25, bottom-right, coalition/war/armistice cards, click signals |
| `war_detail_popup.gd` | War Detail Popup (N4b): CanvasLayer 30, war/coalition/armistice detail views, negotiate/target buttons, refresh-in-place |
| `alliance_paradox_popup.gd` | Alliance paradox popup (Deep Audit S8): honor/break alliance choice when attacking an ally |
| `diplomacy_wizard.gd` | Diplomacy Button wizard (Session B): F1 hotkey, 2-step nation→action flow, own HTTPRequest, command handoff, `open_for_nation()` for war panel handoff |

---

## Before Modifying: Required Reading

| If you're modifying... | Read these first |
|------------------------|------------------|
| Combat damage/modifiers | `marshal.py` (get_*_modifier), `combat.py` (resolve_combat), `docs/MULTI_MARSHAL_SPEC.md` (coordination bonuses) |
| Multi-marshal coordination | `docs/MULTI_MARSHAL_SPEC.md`, `executor.py` (_calculate_coordination_context), `marshal.py` (transient bonus fields) |
| Marshal abilities | `personality_modifiers.py`, `marshal.py`, `combat.py`, `docs/ADDING_CONTENT.md` (wiring checklist), `marshal_overview.py` (_WIRED_ABILITY_MARSHALS) |
| Fortify/Drill mechanics | `executor.py` (_execute_fortify/drill), `marshal.py`, `world_state.py` (_process_tactical_states) |
| Disobedience/Trust | `disobedience.py`, `objection_v2.py`, `personality.py`, `docs/V2B_DEFIANCE_SPEC.md` |
| Cavalry limits | `world_state.py` (_check_cavalry_limits), `marshal.py` (cavalry counters) |
| Terrain system | `region.py` (constants, Region class), `combat.py` (_get_terrain_bonus), `executor.py` (5 resolve_battle calls, charge blocking) |
| Turn processing | `world_state.py` (advance_turn), `executor.py` (_execute_end_turn) |
| Adding new actions | See pattern below |
| Retreat/Broken state | `combat.py` (forced retreat), `marshal.py` (retreat_recovery), `executor.py` |
| Enemy AI behavior | `enemy_ai.py`, `turn_manager.py`, `executor.py` (is_player_action check) |
| Capital garrison | `executor.py` (_resolve_garrison_combat), `world_state.py` (garrison init/regen), `enemy_ai.py` (P4.25) |
| Player garrison | `executor.py` (_execute_garrison), `region.py` (garrison_detachment), `world_state.py` (regen exclusion) |
| Fort degradation | `combat.py` (resolve_combat degradation block), `battle_report.py` (P6c observations) |
| Supply attrition | `world_state.py` (process_supply_attrition), `region.py` (supply_capacity) |
| Strategic commands | `strategic.py`, `strategic_parser.py`, `executor.py` |
| Objection V2 system | `objection_v2.py`, `docs/OBJECTION_V2.md`, `docs/V2B_DEFIANCE_SPEC.md` |
| Fog of war | `docs/FOG_OF_WAR_SPEC.md`, `backend/models/intel.py`, `backend/intel_report.py`, `map.gd` (fog overlay + fogged icons) |
| Strategic commands + fog | `docs/FOG_OF_WAR_SPEC.md` §5, `backend/commands/strategic.py` |
| Manpower pools / recruitment | `world_state.py` (manpower constants, `_process_manpower_regen`), `executor.py` (`_execute_recruit`), `enemy_ai.py` (P1/P4.5/P7 pool checks) |
| Artillery mechanics | `marshal.py` (artillery flag, moved_this_turn, defense modifier), `combat.py` (cavalry counter, fort degradation), `executor.py` (attack block, no advance, charge ban, `_execute_bombardment` collateral, `_distribute_casualties` 50% reduction with non-artillery), `enemy_ai.py` (`_score_artillery_position` frontline penalty + behind-screen bonus) |
| Bombardment collateral | `executor.py` (`_execute_bombardment` collateral loop), `trust.py` (modify), `disobedience.py` (_create_redemption_event), `main.py` (redemption pass-through) |
| Top bar / screen system | `top_bar.gd` (controller), `main.gd` (_on_screen_changed, _is_modal_dialog_open, _is_screen_open, _is_hotkey_blocked), `docs/TOP_BAR_SPEC.md` |
| Morning dispatch / re-read | `dispatch.py` (build + store), `dispatch_view.gd` (render), `main.gd` (_display_morning_dispatch), `world_state.py` (last_morning_dispatch field) |
| Strategic ledger | `ledger.py` (build_strategic_ledger), `strategic_ledger.gd` (render), `world_state.py` (get_manpower_regen_rates), `main.py` (GET /ledger, POST /cancel_order) |
| Marshal management UI | `marshal_overview.py` (build_marshal_overview), `marshal_management.gd` (render), `marshal.py` (biography field), `main.py` (GET /marshal_overview) |
| Win/Loss relationships | `relationship.py` (formulas, participants, process), `executor.py` (_execute_attack wiring), `marshal.py` (modify_relationship, last_relationship_change_turn), `docs/MULTI_MARSHAL_SPEC.md` §9 |
| Square formation / Tactical Triangle | `docs/TACTICAL_TRIANGLE_SPEC.md`, `marshal.py` (square_formation, overwatch_penalty), `combat.py` (cavalry -40%, artillery +50%), `executor.py` (form_square, auto-bombardment, overwatch calc) |
| Vassal system (Phase 8 S5) | `vassal.py` (all vassal mechanics), `world_state.py` (vassals dict, advance_turn steps 5-7, tribute), `diplomacy.py` (AP clause, Continental System), `turn_manager.py` (enemy courting), `dispatch.py` (Trigger 3 loyalty warnings) |
| Diplomatic ledger | `diplomatic_ledger.py` (build_diplomatic_ledger, fog-filtered army strength), `main.py` (GET /diplomatic_ledger, debug endpoints), `world_state.py` (popup fields) |
| Diplomacy wizard / button | `diplomacy_wizard.gd` (wizard UI, `open_for_nation()`), `main.gd` (F1 hotkey, button wiring, command handoff), `main.py` (GET /diplomatic_preview nation list mode), `docs/DIPLOMACY_BUTTON_SPEC.md` |
| War status panel (N4) | `war_status.py` (build_active_wars), `war_status_panel.gd` (HUD Layer 1), `war_detail_popup.gd` (detail Layer 2), `main.gd` (_process_active_wars, _on_war_card_clicked, _update_war_panel_visibility), `main.py` (_include_popup_passthroughs embeds active_wars), `docs/DIPLOMACY_DESIGN_FIXES.md` §N4 |
| Suggested terms / smart suggestions | `diplomatic_templates.py` (NATION_DESIRE_PROFILES, TALLEYRAND_COMMENTARY, generate_suggested_terms 5-stage pipeline, _build_base_terms, _validate_economic_feasibility, _get_smart_commentary), `diplomatic_dialogue.py` (_enrich_proposal_summary commentary wiring), `docs/TALLEYRAND_SMART_SUGGESTIONS_SPEC.md` |
| Diplomacy system (Phase 8) | `docs/DIPLOMACY_SPEC.md` (v2.2), `docs/CONVERSATIONAL_DIPLOMACY_DESIGN.md` (v1.2), `docs/COALITION_SPEC.md` (v1.1), `diplomacy.py` (acceptance formula, state transitions, war score), `diplomat.py` (DiplomaticRepresentative), `diplomatic_dialogue.py` (conversation state machine), `diplomatic_templates.py` (37 mock templates + T28-T34 coalition, slot resolvers, NATION_DESIRE_PROFILES, TALLEYRAND_COMMENTARY, 5-stage suggestion pipeline), `ai_diplomacy.py` (AI proposal generation, M3 counter-offer, alliance conflict), `diplomatic_advisory.py` (advisory conversations), `vassal.py` (loyalty, rebellion), `commands/diplomatic_defiance.py` (Talleyrand sabotage), `coalition.py` (threat, formation, AI, breaking, dissolution) |

For detailed system docs: `docs/SYSTEMS_REFERENCE.md`
For Enemy AI details: `docs/ENEMY_AI_REFERENCE.md`

---

## Common Modification Patterns

### Adding a new action

1. Add to `VALID_ACTIONS` in `validation.py` (single source of truth for LLM)
2. Add `_execute_[action]()` in `executor.py`
3. Add to `valid_actions` list in `parser.py`
4. Add cost to `_action_costs` in `world_state.py`
5. Add keywords to mock parser in `llm_client.py` (~line 416, search "ADD NEW ACTION")
6. Add few-shot example in `prompt_builder.py` if complex
7. If triggerable by objection, add to `objection_actions` in `disobedience.py`
8. Add to_dict/from_dict if new state fields needed

### Adding a new marshal state

1. Add field to `marshal.py __init__`
2. Add to `to_dict()` and `from_dict()` (with `.get()` default)
3. Process in `world_state.py _process_tactical_states()` if per-turn
4. Add blocking logic in `executor.py` if it prevents actions
5. Run `pytest tests/test_serialization_enforcement.py -v`

### Adding a new popup/dialog

```
Backend → Frontend data flow:
  executor.py → main.py → api_client.gd → main.gd
```

1. `executor.py`: Return field in result dict
2. `main.py`: Add early return to pass through the field (most common wiring gap!)
3. `main.gd`: Check for field in `_on_command_result()`
4. Create dialog scene (.tscn) and script (.gd)
5. **CRITICAL:** Verify ALL POST response handlers in `main.py` call `_include_popup_passthroughs(response, world)` before returning — otherwise diplomatic popups are silently lost. See Bug 5 in `docs/BUGFIX_PLAN_PROPOSAL_FLOW.md`.

**Test with curl BEFORE assuming Godot is broken:**
```bash
curl -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "end turn"}' | python -m json.tool
```

**SERIALIZATION WARNING:** Executor results contain `new_state` (WorldState with circular refs). NEVER embed raw executor results in dicts that reach the API response. Strip first:
```python
cleaned = {k: v for k, v in result.items() if k != "new_state"}
```

### Adding a new combat modifier

1. Add state field to `marshal.py __init__`
2. Apply in `marshal.py get_attack_modifier()` or `get_defense_modifier()` ONLY
3. Add message in `combat.py` (DO NOT recalculate modifier)
4. Clear state in `combat.py` if consumable (AFTER get_*_modifier call)

---

## Serialization Enforcement (MANDATORY)

**"If it exists on the object, it must serialize."**

For ANY new field on ANY model class:
1. Add to `to_dict()` method
2. Add to `from_dict()` method (with `.get(key, default)`)
3. Run: `pytest tests/test_serialization_enforcement.py -v`
4. Update `docs/SAVE_FORMAT_REFERENCE.md`

Serializable classes: Marshal, StrategicOrder, StrategicCondition, WorldState, Region, Trust, AuthorityTracker, VindicationTracker, RegionIntel

---

## Key Code Patterns

```python
# Early returns over deep nesting
if not world:
    return {"success": False, "message": "No world state"}

# getattr for optional fields
recklessness = getattr(marshal, 'recklessness', 0)

# Trust modification
marshal.trust.modify(+10)   # Relative change
marshal.trust.value          # Read-only property

# Enemy actions don't consume player budget
if executing_marshal.nation != world.player_nation:
    is_player_action = False
```

---

## Strategic Commands

Strategic orders (MOVE_TO, PURSUE, HOLD, SUPPORT) cost 2 AP (1 for literal). Key patterns:

- **Tactical objection:** `world.pending_objection` — for per-action objections
- **Strategic objection:** `world.pending_strategic_objection` — for order-issuance objections (different field!)
- **Strategic execution flag:** `command["_strategic_execution"] = True` skips AP cost + objections
- **Cancel:** "cancel/halt/stop/abort" → `_execute_cancel()`, costs 1 AP

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Godot float→int error | Wrap all numeric returns with `int()` |
| Modifier applied twice | Check single source in marshal.py, not combat.py |
| State cleared too early | Get value, use it, THEN clear (e.g. drill/shock bonus) |
| Display shows wrong % | `* 100` not `* 10` for percentage |
| "No objection pending" | Strategic uses `pending_strategic_objection`, not `pending_objection` |
| Post-objection "Unknown action" | `_execute_post_objection` must handle all actions + strategic routing |
| Enemy AI crash | `game_state` must be dict `{"world": WorldState}`, not WorldState directly |
| Internal names in frontend | Use `_ACTION_DISPLAY_NAMES` or `_action_display_name()` — never raw action strings |
| Response key mismatch | curl test the endpoint to verify key names match what Godot reads |
| None crash on parse field | Guard `.lower()`/`.strip()` — parser may return None for optional fields |
| `.get('key', '')` returns None | Use `(d.get('key') or '')` — `.get()` default only applies for MISSING keys, not `None` values |
| Objection on impossible action | Pre-validate BEFORE objection check — see bypass hierarchy in executor.py |
| AP error after objection proceed | AP must be checked in pre-validation BEFORE objection fires, not after |
| Data cleared before capture | Save per-turn lists (e.g. mild_concerns) BEFORE calling advance_turn |
| "build" parsed as drill | Mock parser keyword order matters — "build " must be checked BEFORE "train" (substring in "training") |
| Fog leaks enemy info | Filter to PARTIAL+ visibility for attack suggestions, move destinations, event reports |
| PURSUE/SUPPORT path error | `order.target` is marshal name — resolve to `target_marshal.location` before pathfinding |
| Godot null "pressed" on startup | `@onready` node paths must match FULL scene tree in .tscn — verify intermediate nodes |
| Vassal loyalty unexpected | Check `nation_relations` default — France/Saxony=40, adds +2/turn via relation//20 modifier |
| AP clause wrong nation | `from_nation` is the penalized nation (loses AP), not `to_nation` |
| "Talleyrand awaiting" stuck state | Executor dialogue guard blocks ALL commands. Dialogue keywords routed in main.py BEFORE executor — update `_DIALOGUE_RESPONSE_KEYWORDS` for new response types |
| New diplomatic state missing | Add to `post_break_map` in diplomacy.py AND `validate_transition()` — both must cover all states |
| Popup not showing after early return | All response paths must call `_include_popup_passthroughs()` — check diplomatic early return in main.py |
| Popup not showing after endpoint | Every POST handler in `main.py` MUST call `_include_popup_passthroughs(response, world)` before returning — including error paths. See `docs/BUGFIX_PLAN_PROPOSAL_FLOW.md` Bug 5 |
| Raw internal keys in popup text | Use display maps (FEEDBACK_STRINGS, DEFIANCE_TYPE_DISPLAY, PROPOSAL_TYPE_DISPLAY) — never expose raw component/enum keys to players |
| Counter-offer popup broken/empty | Popup data must match `incoming_proposal_popup.gd` fields: `from_nation`, `diplomat_name`, `diplomat_personality`, `clauses` (list), `talleyrand_assessment`, `is_counter_offer` |

---

## Don't Do

- Return floats to Godot (always `int()`)
- Separate player/enemy marshal dicts
- Add features outside current phase scope
- Change port without updating api_client.gd
- Make executor LLM-dependent (keep deterministic)
- Store API keys in code (use .env)
- Skip serialization for new fields
- Bypass executor for state changes
- Run objection evaluation before action validation (check bypass hierarchy in executor.py)
- Show raw internal action names to players (use `_ACTION_DISPLAY_NAMES` translation)
- Use `.get('key', default)` when value may be `None` — use `(d.get('key') or default)` instead
- Skip AP check before objection evaluation — player should never see objection then AP failure
- Add a new nation without updating `NATION_DESIRE_PROFILES` + `TALLEYRAND_COMMENTARY` in `diplomatic_templates.py` (falls back to defaults but loses nation-specific intelligence). See `docs/ADDING_CONTENT.md` validation checklist

---

## Commands

**IMPORTANT (Windows/WSL):** Use Windows-style paths with the venv Python. Unix-style `python -m pytest` silently fails on this WSL setup.

```bash
# Backend
".venv\Scripts\python.exe" backend/main.py    # Runs on port 8005

# Tests (MUST use Windows paths — see note above)
cd "C:\Users\User\PycharmProjects\project-sovereign-map"
".venv\Scripts\python.exe" -m pytest tests/ -v                          # Full suite
".venv\Scripts\python.exe" -m pytest tests/ -v --tb=no -q              # Quick count
".venv\Scripts\python.exe" -m pytest tests/test_objection_v2.py -v     # V2 tests only

# Coverage
".venv\Scripts\python.exe" -m pytest tests/ --cov=backend --cov-report=term-missing -v --tb=no -q

# Lint
ruff check backend/                     # Check for issues
ruff check backend/ --fix               # Auto-fix safe issues

# Validate mod
".venv\Scripts\python.exe" -m backend.modding.validator path/to/mod.json
```

---

## Document Map

| Need | Read |
|------|------|
| Session state / what's next | `docs/STATUS.md` |
| Phase timeline | `docs/ROADMAP.md` |
| Game systems (combat, trust, disobedience, LLM, cavalry, strategic) | `docs/SYSTEMS_REFERENCE.md` |
| Enemy AI decision tree | `docs/ENEMY_AI_REFERENCE.md` |
| V2b defiance/vindication/authority spec | `docs/V2B_DEFIANCE_SPEC.md` |
| Multi-marshal coordination spec (Phase 7) | `docs/MULTI_MARSHAL_SPEC.md` |
| Tactical Triangle (Square + Auto-Bombardment + Overwatch) | `docs/TACTICAL_TRIANGLE_SPEC.md` |
| Diplomacy system (Phase 8) | `docs/DIPLOMACY_SPEC.md`, `diplomat.py`, `diplomacy.py` |
| Diplomacy button wizard spec | `docs/DIPLOMACY_BUTTON_SPEC.md` |
| Diplomacy refinement plan | `docs/DIPLO_REFINEMENT.md` |
| Smart suggestions pipeline | `docs/TALLEYRAND_SMART_SUGGESTIONS_SPEC.md` |
| Diplomacy creative audit | `docs/DIPLOMACY_CREATIVE_AUDIT.md` |
| Diplomacy design fixes + war panel spec | `docs/DIPLOMACY_DESIGN_FIXES.md` (N4 spec, DA session plan) |
| Coalition system (Phase 8) | `docs/COALITION_SPEC.md` |
| Jealousy system (Phase 7b) | `docs/JEALOUSY_SPEC.md` |
| Session 8A-8D plan (UI + debug) | `docs/SESSION_8_PLAN.md` |
| Save format / serialization | `docs/SAVE_FORMAT_REFERENCE.md` |
| Top bar + ledger + dispatch spec | `docs/TOP_BAR_SPEC.md` |
| Fog of war spec | `docs/FOG_OF_WAR_SPEC.md` |
| Modding guide | `docs/MODDING_FORMAT.md` |
| Adding marshals or strategic commands | `docs/ADDING_CONTENT.md` |
| Future design concepts | `docs/FUTURE_DESIGN.md` |
| Game vision | `docs/VISION.md` |
| Systems Audit V2 fix plan | `docs/SYSTEMS_AUDIT_V2_FIX_PLAN.md` |
| Playtest review + bug fix plan | `docs/PLAYTEST_REVIEW_2026_03.md` |
| Manual test plan | `docs/MANUAL_TEST_PLAN.md` |
| Tutorial content / what to teach | `docs/TUTORIAL_SCRIPT.md` |
| Archived specs, prompts & session history | `docs/archive/` |

## Documentation Rules

**If you changed behavior, update the doc that describes it.** Session ends → STATUS.md. Phase completed → ROADMAP.md + STATUS.md. System changed → SYSTEMS_REFERENCE.md. New fields → SAVE_FORMAT_REFERENCE.md.

CLAUDE.md "Current Phase" must always list remaining items. Completed items get brief summaries. Never mark a phase complete when items remain in ROADMAP.md.

---

## Environment

```bash
# .env
LLM_MODE=mock              # mock | anthropic | groq
ANTHROPIC_API_KEY=sk-ant-... # Required if LLM_MODE=anthropic
```

Server: `127.0.0.1:8005`, CORS enabled for Godot client.
