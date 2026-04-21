# CLAUDE.md

Napoleonic strategy game. Players type commands ("Marshal Ney, attack Wellington") and AI marshals respond based on personality. Godot 4 frontend, FastAPI backend on port 8005. For game vision see `docs/VISION.md`.

## Golden Rules

1. **Combat modifiers: SINGLE SOURCE in `marshal.py`** — `get_attack_modifier()` / `get_defense_modifier()` only. `combat.py` reads them, never recalculates.
2. **All numbers to Godot: `int()`** — Godot crashes on floats.
3. **All marshals in ONE dict:** `world.marshals` (not separate player/enemy).
4. **State clearing: AFTER reading** — get the value, use it, then clear.
5. **Enemy AI uses SAME executor as player** (Building Blocks principle — same systems, different input values. See `docs/SYSTEMS_REFERENCE.md` §23).
6. **LLM never affects mechanics** — parsing only, executor is deterministic.
7. **Port 8005** (not 8000!) — change in BOTH `backend/main.py` AND `godot-client/.../api_client.gd`.
8. **Scale-ready code: NO per-region scans in hot paths** — Map is scaling to full 1805 Europe. Never iterate `world.regions.values()` in loops called multiple times per turn. Use cached helpers (e.g. `get_active_nations()` is per-turn cached, `get_nation_regions()` for region lookups). If adding a new helper that scans regions, cache the result per-turn and invalidate via `invalidate_active_nations_cache()` pattern.

## Current Phase

**Phases 6, 6.5, 7 Core, 7b — COMPLETE.** See `docs/STATUS.md` for full session history.

### Up Next

- **Scale Readiness Phase 1 — COMPLETE.** 11 new tests, hardcoded `== 19` removed, validator derives from NATION_CAPITALS.
- **Scale Readiness Phase 0 — COMPLETE (7/7 DECIDED).** DG-1 (13 nations, 20+ capable), DG-2 (bilateral + salience filter, 5-row cap), DG-3 (supply deferred), DG-4 (direct-only bilateral call-to-arms, no transitive cascade), DG-5 (raw-count hegemony victory), DG-6 (scenario-configured pacing, `scenario_schema_version: 1`), DG-7 (categorized dispatch). Cross-cutting: `power_tier` is authored scenario data with canonical enum `major / secondary / minor`; `political_status` is runtime state. See `docs/SCALE_READINESS_PLAN.md` §Phase 0 for the canonical taxonomy.
- **Scale Readiness Phase 2 — COMPLETE.** Distance cache, AI spatial-index wiring, live AI fog path, and the `enemy_ai.py` raw scan-conversion pass are landed suite-green. See `docs/STATUS.md` and `docs/SCALE_READINESS_PLAN.md` §Phase 2.
- **Map Readiness Closure Pass — Phase 3 COMPLETE (§§3.1-3.4) + §§4.1-4.4 COMPLETE.** Phase 3: §3.1 (nation config factory — `DEFAULT_NATION_DEFAULTS` fallback + `create_marshals_from_data` / `create_diplomat_from_data` factories; adding a new nation now only needs a capital + diplomat + optional override), §3.2 (shared topology endpoint — backend `GET /map_topology`), §3.3 (centralize nation colors), §3.4 (prompt/parser fallback de-hardcoding). §4.1: province registry schema v2 in `session8_placeholder_provinces.json` — every region carries `province_id`, four per-feature anchors, `wired`/`interactive` flags; renderer parses new fields, gates hover/click on `interactive`, pre-filters `update_all_regions()` on `wired`. §4.2: external bitmap loading — `map_renderer_base.gd` exposes `_get_map_visual_bitmap_path()` / `_get_map_lookup_bitmap_path()` hooks plus `_load_map_images() -> bool`; loader resolves imported bitmap assets via `ResourceLoader`/`Texture2D.get_image()`, validates size + lookup-color compatibility at runtime, latches failures once, and `_build_map_textures()` tries the bitmap loader FIRST before falling back to circle generation. Placeholder `map.gd` does NOT override the hooks — dev mode stays on circles. §4.3: offline color-map validator at `tools/validate_province_map.py` — stdlib-only standalone CLI gating commissioned-art deliveries. Six failure codes (`SENTINEL_COLLISION`, `DUPLICATE_LOOKUP_COLOR`, `SIZE_MISMATCH`, `MISSING_PROVINCE`, `INSUFFICIENT_COVERAGE`, `UNMAPPED_COLOR`) + connected-island `TINY_ISLAND` warning; `--json` and `--strict` CLI modes; header-only visual PNG sizing plus a pure-Python lookup PNG decoder for 8-bit RGB/RGBA + all five scanline filters with malformed-PNG wrapping. 29 tests in `tests/test_province_map_validator.py`. The placeholder JSON is pinned to always pass registry-only checks. §4.4: unwired province support — `_apply_unwired_grey_overlay(visual_image, lookup_image)` lerps `UNWIRED_GREY_COLOR (0.32, 0.32, 0.34)` over unwired lookup pixels by `UNWIRED_GREY_BLEND = 0.7`; called after `province_lookup_image` is set but BEFORE texture creation on BOTH circle-fallback AND bitmap paths, so tint is uniform across art sources. `_is_region_wired()` + `_unwired_lookup_keys()` gate through `province_shapes` (default wired when region is unknown). `MOUSE_BUTTON_LEFT` click handler short-circuits on unwired BEFORE emitting `region_clicked`. `_draw()` routes unwired hovers to `_draw_unwired_region_tooltip()` (renders `"<name>" / "(not yet in play)"` in a dim-panel variant) BEFORE the `region_full_data.has()` branch (which §4.1 excludes unwired regions from). Hover hit-test path (`_lookup_region_from_color_map()`) is unchanged — it still gates only on `interactive`, so unwired-but-interactive provinces remain hoverable. 16 new tests in `tests/test_map_renderer_cutover.py` (source-level) + new `tests/test_map_unwired_overlay.py` (behavioral overlay mirror). All non-art map-readiness items now closed; commissioned art integration + final renderer smoke remain art-blocked. See `docs/STATUS.md` and `docs/SCALE_READINESS_PLAN.md` §§3-4.
- **Memory and Pressure v2.4.3 (Hegemony refactor + deep-audit fixes + fun/edge audit tightening) — implementation pending.** Substrate shipped (betrayal_history, episode_id, witness scoping, hard-reject). v2.4 collapses static concern seed into per-turn hegemony engine reading bloc shares. v2.4.3 deep-audit fixes add: §7.1 recursive vassal-chain walk, §7.3 deterministic hegemon tie-break + non-France-hegemon guard, §7.2 drops runtime `nation_power_tiers` map (reads authored scenario record directly), §8.6.1a grievance-variant Make Amends, §8.8.7a existing-alliance terminates on defensive refusal, §9.3 conditional composite floor (-60 with DG-4), §11.1 Balance-of-Europe five-case state machine (including COOLDOWN). Bloc-naming contract adopted: deterministic `33 / 50 / 60` activation gate (descriptive → proper-noun reveal → crisis persistence), authored hegemon→label taxonomy, Balance headline + threshold beats + proposal warnings + coalition-declaration contrast as required surfaces. **v2.4.3-final audit tightening (April 21, 2026)** applied five fixes: C-01 R11 stale `-1 to -1.8` numbers corrected to `0 → -1 → -18 → -20` integer buckets, C-02 normative `bloc_label = None` at <50% pinned in CPS §8.1a.6, C-03 Case 2/3 naming asymmetry fixed via `{bloc_label or descriptive_label or hegemon}` fallback chain, C-04 relaxation-aside timing locked to end-of-turn evaluation (prevents mid-turn oscillation trap), F-01 Case 4 worked example trimmed with optional qualifying-courts flourish rule added, and headline three-line cap made explicit. **v2.4.3 second-pass audit fixes (April 21, 2026)** applied seven more: D1 pacing honesty — `60%+` is the declared first guaranteed-hardening band; the `50%` beat is the proper-noun reveal, not a hardening promise. D2/E8 voice fallback made authoritative everywhere: **named envoy → Talleyrand advisory → chancery** (table + prose + Voice Bible). D3/E9 hedging language cleaned up — per-row bloc badges ship as **Slice E-Cards, the final Memory and Pressure slice**, fully planned with scope + tests + acceptance gates; no "deferred" / "un-deferred" / "in-scope but last" framing remains anywhere in live specs. E5 decoupled `hegemony_target_mod` from `_calculate_hegemony_pressure` via shared `_identify_max_bloc_share(world)` helper so per-pair friction starts at the 30% boundary while threat accrual stays gated at 33%+. E6 §7.4 "coalition target = current hegemon" gets explicit no-hegemon fallback to `world.player_nation` for event-threat brewing. E7 Balance-of-Europe payload gains `cooldown_turns_remaining` and `residual_pressure_active` fields for Case 5 COOLDOWN. E9 §11.1 non-France-hegemon coalition sub-line changed from "suppress OR retarget" choice to a flat SUPPRESS rule. **Block 1 (doc cleanup) + Block 2 (substrate alignment) COMPLETE. Block 3 audit doc SUPERSEDED** — its bloc-naming contract (D1-D10) and CF1-CF4 closure items were folded back into the owning specs: `COMMITMENTS_PRESENTATION_SPEC.md` §8.1a + `DIPLOMAT_VOICE_BIBLE.md` "Bloc-naming voice contract" + `RELIABILITY_IMPLEMENTATION_PLAN.md` parent slices (B-B4 / B-B7 / C-lite / Slice E-Cards). **Next:** implementation slices in order — B-Hegemony → B-B1-lite → B-B3 → B-B7 → B-B4 (parallel, merge gate: AT or AFTER B-B1-lite) → C-lite → Slice E-Cards (final slice). ~54-63 tests on the critical path, ~79-92 including parallel B-B4, ~2-3 implementation sessions. See `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.4.3 + `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` + `docs/COMMITMENTS_PRESENTATION_SPEC.md` v0.5.2.
- **Session 8 Renderer — ART-BLOCKED.** Slices 1-3 complete. Remaining: commissioned art-backed layers + Godot smoke validation. See `docs/STATUS.md`.
- **Architecture Refactoring — Sessions 1-16 COMPLETE.** R19 (modding) remaining. R14a-d deferred. See `docs/ARCHITECTURE_REFACTORING_PLAN.md`.
- **Design Refinement — full queue.** War bargains deferred to Peace Deals phase (`docs/WAR_BARGAIN_SPEC.md`). Period precision items tracked in `docs/DESIGN_REFINEMENT.md` §Historical Precision.
- **Jealousy System — NEEDS DESIGN GATE.** v3.1 spec drafted. DO NOT CODE WITHOUT USER APPROVAL. See `docs/JEALOUSY_SPEC.md`.

### Design Gates

- **Coalition Spec v1.1** — Approved Mar 2, 2026. `docs/COALITION_SPEC.md`
- **Starting Situation Balance** — Approved Mar 2, 2026. 5 changes applied to DIPLOMACY_SPEC.
- **Jealousy System** — v3.1 spec drafted, NEEDS APPROVAL. DO NOT CODE. `docs/JEALOUSY_SPEC.md`


---

## File Reference

### Backend Core

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI endpoints, response formatting |
| `backend/commands/executor.py` | Action execution, dispatch, objection routing (~1.5k lines) |
| `backend/commands/combat_executor.py` | Combat execution + coordination: attack, bombardment, charge, garrison, form_square, post-combat pipeline, multi-marshal coordination, reinforcements, overwatch, auto-dispatch combat (~4.7k lines, R10A+R10B) |
| `backend/commands/strategic_executor.py` | Strategic order execution: MOVE_TO, PURSUE, HOLD, SUPPORT, cancel, objection messages, target resolution, first-step blocking (~1.8k lines, R11) |
| `backend/commands/diplomatic_executor.py` | Diplomatic execution: proposals, dialogue state machine, missions, trust reactions, AI proposal accept/reject/counter, terms guidance wizard (~2.3k lines, R11) |
| `backend/commands/economy_executor.py` | Economy execution: economy report, recruit, garrison, build, watchtower, repair (~800 lines, R13A) |
| `backend/commands/tactical_executor.py` | Tactical execution: defend, wait, drill, fortify, unfortify, stance_change, restrain, auto_break_square (~715 lines, R13A) |
| `backend/commands/movement_executor.py` | Movement execution: move, scout, auto_assign_scout, retreat, movement attrition (~680 lines, R13B) |
| `backend/commands/meta_executor.py` | Meta/debug/objection: end_turn, status, help, debug, cheat, handle_objection_response, post_objection (~1.9k lines, R13B) |
| `backend/commands/vassal_executor.py` | Vassal management: invest, change_autonomy, make_vassal, release_vassal (~147 lines, R13A) |
| `backend/commands/capture_executor.py` | Post-capture plunder/secure choice handling (~94 lines, R13A) |
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
| `backend/models/cooldown_manager.py` | CooldownManager (5 auto-decrement cooldowns) + PopupQueue (7 priority-ordered popups) (R6) |
| `backend/models/dialogue_manager.py` | DialogueManager (push/pop/peek, priority queue, clear_stale timeout, promote_if_empty) (R12) |
| `backend/display_names.py` | Single source of truth for all internal→display name translations (R7) |
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
| `utils.gd` | Shared color palette (19 COLOR_ consts), NATION_COLORS, bbcode_color/format_number helpers (R15) |
| `popup_base.gd` | Base class for modal popups: close_popup, _disable_all_buttons, _apply_standard_theme (R15) |
| `dialog_manager.gd` | Centralized dialog registry: register, get_dialog, is_any_modal_open, hide_all (R16) |
| `api_client.gd` | Backend communication |
| `game_manager.gd` | Game state coordination |
| `map_renderer_base.gd` | Map renderer base: scene layers, Camera2D+SubViewport, province color-map, hover/click, zoom/pan |
| `map.gd` | Session 8 map: extends renderer base, region positions/connections/colors |
| `main.gd` | Terminal UI, response handling |
| `pause_menu.gd` | Pause menu overlay (Phase 6.5) |
| `campaign_log.gd` | Campaign log overlay (Phase 6.5), CanvasLayer 50 |
| `notification_bar.gd` | Notification bar (Phase 6.5), reparented into top bar |
| `top_bar.gd` | Top bar controller (Session A): screen management, hotkeys, notifications, turn counter |
| `dispatch_view.gd` | Dispatch re-read screen (Session A): CanvasLayer 50, BBCode rendering |
| `strategic_ledger.gd` | Strategic Ledger screen (Session B): CanvasLayer 50, 6 sub-tabs, number key switching, Orders tab cancel buttons |
| `marshal_management.gd` | Marshal Management screen: CanvasLayer 50, card-based marshal view, G key toggle |
| `diplomatic_ledger.gd` | Diplomatic Ledger screen (Session 8B): CanvasLayer 50, 4 sub-tabs (Nations/Treaties/Threat/Talleyrand), D key toggle |
| `*_popup.gd` (7 files) | Modal popups: coalition_declaration, incoming_proposal, talleyrand_objection, sabotage_discovery, talleyrand_redemption, vassal_rebellion, alliance_paradox. CanvasLayer 100-119 |
| `mailbox_panel.gd` | Browsable mailbox inbox: CanvasLayer 119, click-to-activate rows |
| `war_status_panel.gd` | War Status HUD (CanvasLayer 25) + `war_detail_popup.gd` (CanvasLayer 30) |
| `diplomacy_wizard.gd` | Diplomacy Button wizard (Session B): F1 hotkey, 2-step nation→action flow, own HTTPRequest, command handoff, `open_for_nation()` for war panel handoff |

---

## Before Modifying: Required Reading

| If you're modifying... | Read these first |
|------------------------|------------------|
| Combat damage/modifiers | `marshal.py` (get_*_modifier), `combat.py` (resolve_combat), `combat_executor.py` (_execute_attack, _execute_bombardment), `docs/MULTI_MARSHAL_SPEC.md` (coordination bonuses) |
| Multi-marshal coordination | `docs/MULTI_MARSHAL_SPEC.md`, `combat_executor.py` (_calculate_coordination_context, _calculate_reinforcements, _calculate_overwatch), `marshal.py` (transient bonus fields) |
| Combat execution (attack/bombard/charge) | `combat_executor.py` (all _execute_* methods, post-combat pipeline, coordination, reinforcements, overwatch) |
| Marshal abilities | `personality_modifiers.py`, `marshal.py`, `combat.py`, `docs/ADDING_CONTENT.md` (wiring checklist), `marshal_overview.py` (_WIRED_ABILITY_MARSHALS) |
| Fortify/Drill mechanics | `tactical_executor.py` (_execute_fortify/drill), `marshal.py`, `world_state.py` (_process_tactical_states) |
| Disobedience/Trust | `disobedience.py`, `objection_v2.py`, `personality.py`, `docs/V2B_DEFIANCE_SPEC.md` |
| Cavalry limits | `world_state.py` (_check_cavalry_limits), `marshal.py` (cavalry counters) |
| Terrain system | `region.py` (constants, Region class), `combat.py` (_get_terrain_bonus), `combat_executor.py` (resolve_battle calls, charge blocking) |
| Turn processing | `world_state.py` (advance_turn), `meta_executor.py` (_execute_end_turn) |
| Adding new actions | See pattern below |
| Retreat/Broken state | `combat.py` (forced retreat), `marshal.py` (retreat_recovery), `combat_executor.py` (_handle_forced_retreat, _apply_forced_retreat_or_break) |
| Enemy AI behavior | `enemy_ai.py`, `turn_manager.py`, `executor.py` (is_player_action check) |
| Capital garrison | `combat_executor.py` (_resolve_garrison_combat), `world_state.py` (garrison init/regen), `enemy_ai.py` (P4.25) |
| Player garrison | `economy_executor.py` (_execute_garrison), `region.py` (garrison_detachment), `world_state.py` (regen exclusion) |
| Fort degradation | `combat.py` (resolve_combat degradation block), `battle_report.py` (P6c observations) |
| Supply attrition | `world_state.py` (process_supply_attrition), `region.py` (supply_capacity) |
| Strategic commands | `strategic.py`, `strategic_parser.py`, `strategic_executor.py` (_execute_strategic_command, _execute_cancel, objection handling) |
| Objection V2 system | `objection_v2.py`, `docs/OBJECTION_V2.md`, `docs/V2B_DEFIANCE_SPEC.md` |
| Fog of war | `docs/FOG_OF_WAR_SPEC.md`, `intel.py`, `intel_report.py`, `map.gd`. Use `get_visible_enemies()` for player-facing, `get_enemies_of_nation()` for omniscient only |
| Manpower / recruitment | `world_state.py` (manpower constants), `economy_executor.py` (_execute_recruit), `enemy_ai.py` (P1/P4.5/P7) |
| Artillery / bombardment | `marshal.py` (artillery flag), `combat.py` (cavalry counter, fort degradation), `combat_executor.py` (_execute_bombardment, _distribute_casualties), `enemy_ai.py` (_score_artillery_position) |
| Top bar / screen system | `top_bar.gd` (controller), `main.gd` (_on_screen_changed, _is_modal_dialog_open, _is_screen_open, _is_hotkey_blocked), `docs/TOP_BAR_SPEC.md` |
| Morning dispatch / re-read | `dispatch.py` (build + store), `dispatch_view.gd` (render), `main.gd` (_display_morning_dispatch), `world_state.py` (last_morning_dispatch field) |
| Strategic ledger | `ledger.py` (build_strategic_ledger), `strategic_ledger.gd` (render), `world_state.py` (get_manpower_regen_rates), `main.py` (GET /ledger, POST /cancel_order) |
| Marshal management UI | `marshal_overview.py` (build_marshal_overview), `marshal_management.gd` (render), `marshal.py` (biography field), `main.py` (GET /marshal_overview) |
| Win/Loss relationships | `relationship.py` (formulas, participants, process), `combat_executor.py` (_execute_attack wiring), `marshal.py` (modify_relationship, last_relationship_change_turn), `docs/MULTI_MARSHAL_SPEC.md` §9 |
| Square formation / Tactical Triangle | `docs/TACTICAL_TRIANGLE_SPEC.md`, `marshal.py`, `combat.py`, `combat_executor.py`, `tactical_executor.py`, `executor.py` |
| Vassal system | `vassal.py`, `world_state.py` (vassals dict, advance_turn), `diplomacy.py` (AP clause), `turn_manager.py`, `dispatch.py` |
| Diplomatic ledger | `diplomatic_ledger.py` (build_diplomatic_ledger, fog-filtered army strength), `main.py` (GET /diplomatic_ledger, debug endpoints), `world_state.py` (popup fields) |
| Diplomacy wizard / button | `diplomacy_wizard.gd` (wizard UI, `open_for_nation()`), `main.gd` (F1 hotkey, button wiring, command handoff), `main.py` (GET /diplomatic_preview nation list mode), `docs/DIPLOMACY_BUTTON_SPEC.md` |
| War status panel (N4) | `war_status.py` (build_active_wars), `war_status_panel.gd` (HUD), `war_detail_popup.gd` (detail), `main.gd` (_process_active_wars) |
| Suggested terms / smart suggestions | `diplomatic_templates.py` (generate_suggested_terms 5-stage pipeline), `diplomatic_dialogue.py`, `docs/TALLEYRAND_SMART_SUGGESTIONS_SPEC.md` |
| Diplomacy execution | `diplomatic_executor.py` (_execute_diplomatic*, handle_diplomatic_dialogue_response, trust reactions, AI proposal handlers) |
| Dialogue state (R12, PL-27) | `dialogue_manager.py` (push/pop/peek, PL-27 taxonomy: HARD_STOP/SOFT_STOP/HYBRID/LOCAL_PLANNING types), `world_state.py` (transparent properties). Only hard-stop dialogues block commands. Endpoints: `GET /mailbox`, `POST /mailbox/activate` |
| Diplomacy system (Phase 8) | `docs/DIPLOMACY_SPEC.md`, `docs/COALITION_SPEC.md`, `diplomacy.py`, `diplomat.py`, `diplomatic_dialogue.py`, `diplomatic_templates.py`, `ai_diplomacy.py`, `diplomatic_advisory.py`, `vassal.py`, `diplomatic_defiance.py`, `coalition.py` |
| Memory and Pressure substrate (hegemony / betrayal memory / paradox / reliability) | `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v2.4.3 — §8.8 holds the DG-4 call-to-arms episode contract, §8.6.1a authors the Make Amends grievance variant, §8.8.7a authors the existing-alliance termination on defensive refusal; `docs/SCALE_READINESS_PLAN.md` §DG-4 Amendment is the source of truth), `docs/RELIABILITY_IMPLEMENTATION_PLAN.md`, `docs/COMMITMENTS_PRESENTATION_SPEC.md`, `docs/DIPLOMAT_VOICE_BIBLE.md`, `docs/COALITION_SPEC.md`, `diplomacy.py`, `world_state.py` (`betrayal_history`, `next_episode_id`), `commitments` logic within `diplomatic_templates.py`, `campaign_log.py`, `coalition.py` (hegemony engine when landed) |
| War bargains (deferred to Peace Deals phase) | `docs/WAR_BARGAIN_SPEC.md`. Do NOT add bargain logic until Bilateral Peace Hardening + War Purpose specs land first. Substrate seams (`region_observer` witness scope, `bargain_value_mod`, `war_entry_score`, `commitment_paradox` rivalry-driven trigger) are intentionally inert until that phase. |
| C3-lite presentation (Memory and Pressure final slice) | `docs/COMMITMENTS_PRESENTATION_SPEC.md` (v0.5.2 — v2.4.3 hegemony-aligned; §8.1a owns the bloc-naming contract folded from the retired Block 3 audit; non-normative bulk trimmed per v2.4.2 deep-audit C7; Slice C trims cut spotlight-tier card variant, split-voice `attributed_lines[]`, N+1 Talleyrand aside), `docs/COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` (historical), `docs/DIPLOMAT_VOICE_BIBLE.md`, `diplomatic_templates.py` (`commitments_notice_*` family only; `commitments_spotlight_*` family is cut), `notifications.py`, `notification_bar.gd`, `dispatch.py`. Any `speaker="envoy"` / `speaker="foreign_office"` template MUST resolve to a named diplomat per Voice Bible — anonymous voice is disallowed. Three live notice events (not spotlights): `diplomatic_treaty_broken` (french_breach), `hard_reject_posture_triggered`, `commitment_paradox`. |
| Diplomat voice (register rules per named diplomat) | `docs/DIPLOMAT_VOICE_BIBLE.md`, `backend/models/diplomat.py` (cast = Talleyrand, Castlereagh, Hardenberg, Metternich, Einsiedel). Read Voice Bible BEFORE authoring any new line for a named foreign diplomat. |

For detailed system docs: `docs/SYSTEMS_REFERENCE.md`
For Enemy AI details: `docs/ENEMY_AI_REFERENCE.md`

---

## Common Modification Patterns

### Adding a new action

1. Add to `VALID_ACTIONS` in `validation.py` (single source of truth for LLM)
2. Add `_execute_[action]()` in the appropriate sub-executor (see file reference table)
3. Add to `valid_actions` list in `parser.py`
4. Add cost to `_action_costs` in `world_state.py`
5. Add keywords to mock parser in `llm_client.py` (~line 416, search "ADD NEW ACTION")
6. Add few-shot example in `prompt_builder.py` if complex
7. If triggerable by objection, add to `objection_actions` in `disobedience.py`
8. Add to_dict/from_dict if new state fields needed
9. Add to `ACTION_DISPLAY` in `display_names.py`
10. Add to `_DEFIANCE_DISPLAY` + `_OBJECTION_DISPLAY` in `campaign_log.py` (lines ~21, ~43)
11. Add event type to `CAMPAIGN_LOG_TYPES` in `campaign_log.py` (line ~83) + format in `format_event_oneliner()`

### Adding a new marshal state

1. Add field to `marshal.py __init__`
2. Add to `to_dict()` and `from_dict()` (with `.get()` default)
3. Process in `world_state.py _process_tactical_states()` if per-turn
4. Add blocking logic in `executor.py` if it prevents actions
5. Run `pytest tests/test_serialization_enforcement.py -v`

### Adding a new popup/dialog

```
Backend → Frontend data flow:
  sub-executor → main.py → api_client.gd → main.gd
```

1. Sub-executor (e.g., `meta_executor.py`, `combat_executor.py`): Return field in result dict
2. `main.py`: Add early return to pass through the field (most common wiring gap!)
3. `main.gd`: Check for field in `_on_command_result()`
4. Create dialog scene (.tscn) and script (.gd) — assign unique layer in 101-118 range
5. **R16:** Register in `main.gd _ready()` via `dialog_manager.register()` — set `modal=true` (default) for blocking dialogs, `modal=false` for HUD elements
6. **R4:** All POST handlers use `build_base_response()` which structurally guarantees popup passthroughs. No manual `_include_popup_passthroughs()` calls needed.

**Test with curl BEFORE assuming Godot is broken:**
```bash
curl -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "end turn"}' | python -m json.tool
```

**SERIALIZATION WARNING:** Executor results contain `new_state` (WorldState with circular refs). Strip `new_state` before embedding in API responses.

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
| State cleared too early | Get value, use it, THEN clear (e.g. drill/shock bonus) |
| "No objection pending" | Strategic uses `pending_strategic_objection`, not `pending_objection` |
| Post-objection "Unknown action" | `_execute_post_objection` must handle all actions + strategic routing |
| Enemy AI crash | `game_state` must be dict `{"world": WorldState}`, not WorldState directly |
| Internal names in frontend | Use `display_names.py` maps (R7) — never raw action/state/personality strings. Import from `backend.display_names`, not original files |
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
| "Talleyrand awaiting" stuck state | Only hard-stop dialogues block commands. Check `dialogue_manager.py` HARD_STOP_TYPES |
| New diplomatic state missing | Add to `post_break_map` in diplomacy.py AND `validate_transition()` |
| Popup not showing after early return | Use `build_base_response()` or `_build_result_response()` — they structurally guarantee popup passthroughs (R4) |
| Popup not showing after endpoint | Use `build_base_response()` for ALL POST handlers. Only `/command` main path (enemy_phase deferral) calls `_include_popup_passthroughs()` directly |
| New dialogue type shows in terminal | **TWO things:** (1) Add dtype to `main.gd:697` whitelist so Godot shows popup. (2) If dialogue concludes with a result, set `world.proposal_result_popup` so outcome shows as popup. See PL-14 fix |
| Raw internal keys in popup text | Use display maps (FEEDBACK_STRINGS, DEFIANCE_TYPE_DISPLAY, PROPOSAL_TYPE_DISPLAY) — never expose raw component/enum keys to players |
| Fog leak — player sees fogged enemies | Use `world.get_visible_enemies(nation)` for player-facing queries (R5). `get_enemies_of_nation()` is omniscient — only for combat/AI/mechanics |
| Region attribute returns default silently | Region uses `income_value` (not `income`) and `adjacent_regions` (not `connections`). Check `region.py` for exact names |

---

## Don't Do

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
- Use `get_enemies_of_nation()` for player-facing queries — use `get_visible_enemies()` instead (R5). `get_enemies_of_nation()` is omniscient and leaks fog
- Add a new nation without updating `NATION_DESIRE_PROFILES` + `TALLEYRAND_COMMENTARY` in `diplomatic_templates.py`
- Iterate `world.regions.values()` in hot paths — use `get_active_nations()` (cached), `get_nation_regions()` instead
- Use `[world.player_nation] + list(world.enemy_nations)` — use `world.get_active_nations()` instead

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
| **Open bugs (consolidated)** | **`docs/BUG_FIXES.md`** |
| **Design refinement items** | **`docs/DESIGN_REFINEMENT.md`** |
| Phase timeline | `docs/ROADMAP.md` |
| Game systems (combat, trust, disobedience, LLM, cavalry, strategic) | `docs/SYSTEMS_REFERENCE.md` |
| Enemy AI decision tree | `docs/ENEMY_AI_REFERENCE.md` |
| Combat specs (V2b, Multi-Marshal, Tactical Triangle) | `docs/V2B_DEFIANCE_SPEC.md`, `MULTI_MARSHAL_SPEC.md`, `TACTICAL_TRIANGLE_SPEC.md` |
| Diplomacy specs (system, coalition, wizard, suggestions, jealousy) | `docs/DIPLOMACY_SPEC.md`, `COALITION_SPEC.md`, `DIPLOMACY_BUTTON_SPEC.md`, `TALLEYRAND_SMART_SUGGESTIONS_SPEC.md`, `JEALOUSY_SPEC.md` |
| Memory and Pressure (substrate + presentation) | `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v2.4.3), `RELIABILITY_IMPLEMENTATION_PLAN.md`, `COMMITMENTS_PRESENTATION_SPEC.md` (v0.5.2 C3-lite hegemony-aligned; §8.1a owns bloc-naming contract post-Block-3 fold), `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` (historical) |
| War bargains (deferred — Peace Deals phase) | `docs/WAR_BARGAIN_SPEC.md` (depends on Bilateral Peace Hardening + War Purpose specs) |
| Diplomat voice bible / playtest | `docs/DIPLOMAT_VOICE_BIBLE.md`, `COMMITMENTS_PLAYTEST_SCRIPT.md` |
| UI specs (top bar, fog) | `docs/TOP_BAR_SPEC.md`, `FOG_OF_WAR_SPEC.md` |
| Save format / serialization | `docs/SAVE_FORMAT_REFERENCE.md` |
| Adding content / modding | `docs/ADDING_CONTENT.md`, `MODDING_FORMAT.md` |
| Vision, future design, manual tests | `docs/VISION.md`, `FUTURE_DESIGN.md`, `MANUAL_TEST_PLAN.md`, `TUTORIAL_SCRIPT.md` |
| Architecture (audit + refactoring) | `docs/ARCHITECTURE_AUDIT_REPORT.md`, `ARCHITECTURE_AUDIT_SPEC.md`, `ARCHITECTURE_REFACTORING_PLAN.md` |
| Archived specs & session history | `docs/archive/` |

## Documentation Rules

**If you changed behavior, update the doc that describes it.** Session ends → STATUS.md. Phase completed → ROADMAP.md + STATUS.md. System changed → SYSTEMS_REFERENCE.md. New fields → SAVE_FORMAT_REFERENCE.md.

CLAUDE.md "Current Phase" must always list remaining items. Completed items get brief summaries. Never mark a phase complete when items remain in ROADMAP.md.

---

## Environment

`.env`: `LLM_MODE=mock|anthropic|groq`, `ANTHROPIC_API_KEY` if anthropic. Server: `127.0.0.1:8005`, CORS enabled.
