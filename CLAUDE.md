# CLAUDE.md

Napoleonic strategy game. Players type commands ("Marshal Ney, attack Wellington") and AI marshals respond based on personality. Godot 4 frontend, FastAPI backend on port 8005. For game vision see `docs/VISION.md`.

## Golden Rules

1. **Combat modifiers: SINGLE SOURCE in `marshal.py`** — `get_attack_modifier()` / `get_defense_modifier()` only. `combat.py` reads them, never recalculates.
2. **All numbers to Godot: `int()`** — Godot crashes on floats.
3. **All marshals in ONE dict:** `world.marshals` (not separate player/enemy).
4. **State clearing: AFTER reading** — get the value, use it, then clear.
5. **Enemy AI uses SAME executor as player** (Building Blocks principle — same systems, different input values. See `docs/SYSTEMS_REFERENCE.md` §23).
6. **LLM never affects mechanics** — parsing only, executor is deterministic.
7. **Port 8005 default; `SOVEREIGN_PORT` env overrides BOTH sides at once** (Aug 15, 2026) — `backend/main.py` reads it, every `.gd` derives its origin from `Utils.backend_url()`. Never hardcode the origin in a `.gd` again; run a test pair beside the player's live 8005 session via `SOVEREIGN_PORT=8006`.
8. **Scale-ready code: NO per-region scans in hot paths** — Map is scaling to full 1805 Europe. Never iterate `world.regions.values()` in loops called multiple times per turn. Use cached helpers (e.g. `get_active_nations()` is per-turn cached, `get_nation_regions()` for region lookups). If adding a new helper that scans regions, cache the result per-turn and invalidate via `invalidate_active_nations_cache()` pattern.
9. **No open-ended deferrals** — any hidden, cut, deferred, later, v2, or polish player-facing work must name a concrete owner row/spec, landing slice, completion definition, STATUS tracking line, and behavior test. If the work is not going to land, remove the player-facing promise explicitly. Do not leave "future work" labels, disabled placeholders, or vague backlog notes in active specs.

## Workflow: work directly on master

This is a single-developer project with pre-commit-hook test gating and Codex audits run by commit SHA. Branch-per-slice / worktree-per-slice creates state-drift bugs (the branch falls behind master between slices, the merge back is noisy, and the audit prompt still ends up referencing master after merge anyway). The workflow is intentionally single-threaded: one local master worktree, one active implementation path, and audit/fix follow-ups recorded by master commit SHA. The default is:

- **Commit directly to master.** No `claude/<slice-id>` feature branch, no worktree.
- **The pre-commit hook runs `ruff check backend/` + the full pytest suite, IN PARALLEL** (`-n 8 --dist loadgroup` under pytest-xdist; measured 5:12 on this machine against 26:13 serial — the user's October 9, 2026 ruling "the gate stays, the wait goes"; `tests/conftest.py` keeps each test module on one worker and the Godot-launching / fixed-port modules on a single `engine` group, and gives a worker's child processes `stdin=DEVNULL` so none can eat the execnet channel). If a commit is blocked, fix the underlying lint/test failures — do not bypass with `--no-verify`. The hook source is tracked at `scripts/git-hooks/pre-commit`; since `.git/hooks/` is not version-controlled, install it after a fresh clone with `cp scripts/git-hooks/pre-commit .git/hooks/pre-commit` (PowerShell: `Copy-Item scripts/git-hooks/pre-commit .git/hooks/pre-commit`).
- **Codex audits target master at the slice's commit SHA.** When emitting an audit prompt, write `Audit master at commit <SHA>...` rather than naming a feature branch. The audit prompt should also instruct Codex to verify any follow-up work continues on master.
- **If the harness spawns a worktree on a `claude/...` branch anyway:** finish the slice in the worktree (avoid mid-session churn), push branch-tip-to-master via `git push origin <branch>:master`, and add a note to the session summary recommending the user disable auto-worktree creation in their launcher.
- **Exception:** Use a feature branch only when the slice is genuinely throwaway/experimental and the user explicitly asks for one.

## Current Phase

> **ROUTING AUTHORITY = `docs/PRE_DEPLOY_PLAN.md` §2** (code health → the UX/UI
> review → the deep dives DD-0 / DD-1 → the Score Finish residue → the deploy);
> its plans are `docs/CODE_HEALTH_PLAN.md` and `docs/UX_UI_REVIEW_PLAN.md`.
> **`docs/STATUS.md` ▶ NEXT UP says what is next, what landed last and what the
> user owes — read it first, every session.** The Score Finish residue
> (`docs/SCORE_FINISH_SPEC.md` §3 Step 9) is PAUSED behind the plan until S14.

**▶ LIVE STATE (October 9, 2026).** The three most recent landed rows:
- **S2 step 0 + CODE-4 (October 9, 2026)** — the pre-commit hook runs the full suite in parallel, 26:13 → 5:12 (`78d9653a`); the docs diet (this file 523 KB → 61 KB, STATUS 1.6 MB → 22 KB; `docs/CODE_HEALTH_PLAN.md` §CODE-4). NEXT = CODE-1 batch 1, then S3–S4 DD-0.
- **S1a + S1b (October 9, 2026)** — the readability instrument, the derived Interface Scale, the first-run card, the theme floor, the Settings additions; whole-client census RED 1,565 → 32 (`docs/UX_UI_REVIEW_PLAN.md` §UXR-1 / §S1b).
- **The economy audit + gate (October 5, 2026)** — the books fixed, EAD-1 … EAD-9 ruled and built (`docs/SCORE_FINISH_SPEC.md` §6.7–§6.8).

**Open with the user:** UXR-4 (the eyes-on sign-off at 5120×1440); EG-D1 … EG-D3 (`docs/DESIGN_REFINEMENT.md` §The Economy Audit).

**The whole 2026 record** is archived verbatim: `docs/archive/CLAUDE_CURRENT_PHASE_2026.md` (this section as it stood), `docs/archive/STATUS_2026_Q*.md`, `docs/archive/BUG_FIXES_2026_Q*.md`, `docs/archive/DESIGN_REFINEMENT_2026_Q*.md`. The census tools and the test pins read the archives (`tests/_ledgers.py`), so every count includes them.

### Load-bearing operational facts (1805 boot — keep verbatim)

- **THE RUNNING GAME IS THE 126-PROVINCE 1805 CAMPAIGN, frontend + backend** (cutover closed July 2, 2026; plan + deferred rows in `docs/MAP_IMPLEMENTATION_PLAN.md`).
- **Boot precedence:** explicit `SOVEREIGN_SCENARIO` (+ smoke preset = RAISE, never combine) → `SOVEREIGN_SCENARIO=none` sentinel = bare flag world (conftest pins it suite-wide) → `SOVEREIGN_MAP=legacy` = the 19-region rollback (drilled live; no code change) → preset alone → **default = `godot-client/project-sovereign/assets/maps/europe_1805.json`**. Run the backend as `-m backend.main`.
- The **registry** `godot-client/project-sovereign/assets/maps/europe.json` is the single source for renderer AND `create_europe_regions()` (lru_cached — restart the server after edits; NEVER re-run `build_region_key_from_psd.py --adjacency-only`: it clobbers the hand-authored sea-link folds + DEF-7 cuts; `adjacent` = walkability incl. the 18 sea links, `sea_links` = the drawn dashed routes only).
- Europe config is scenario-scoped in `nation_config.py` (never touch the legacy globals — N1); scenario authoring contract in `docs/MODDING_FORMAT.md` (incl. the Slice-8 `region_overrides` key); capital garrisons tier-differentiated on Europe only (majors 25k / secondary 15k / minors 10k, `get_capital_garrison_target`); scenario boots compute fog via `calculate_visibility()` in `from_scenario` (own soil PARTIAL+, marshal locations FULL); Russia honor bias is 1.1 (DG-4 fixture pins re-derived at 1.1); G4 measured: bare-Europe turn 0.49× legacy, 1805 campaign 5.4× (roster workload), tripwires in `test_scale_readiness_phase2.py`.
- Manual settlement smoke shortcut: `SOVEREIGN_SMOKE_START=settlement_multilateral` (never combined with `SOVEREIGN_SCENARIO`); other presets: `settlement_losing`, `settlement_rejected`, `settlement_multiwar_ambiguity`, `settlement_surrender`, `settlement_recurring_gold`.

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
| `backend/models/region.py` | `create_europe_regions()` builds the live 126-province world from `europe.json` (lru_cached); legacy REGIONS_DATA/NATION_CAPITALS survive as the test-fixture world; terrain/region type constants, starting_controller, grid_position |
| `backend/nation_config.py` | Scenario-scoped nation config: EUROPE_ROSTER, EUROPE_NATION_CAPITALS/GOLD/ACTIONS/AUTHORITY, EUROPE_MANPOWER_POOLS, EUROPE_VASSAL_WEB + builders; legacy DEFAULT_* globals (N1: never perturb them) |
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
| `backend/game_logic/marshal_overview.py` | Marshal Management builder (player marshal cards with identity, ability, stats, trust, status, relationships, glory/grievance block) |
| `backend/game_logic/jealousy.py` | Jealousy v3.2: glory ladder, grievance triggers/resolution, crown, escalation, the marshal-petition channel (§6/§6b/ESP-1/ESP-2), autonomous attacks, enemy proxy |
| `backend/game_logic/recruitment.py` | Marshal Recruitment ("The Marshalate"): pool queries, commission gate/effects, AI commission rung, Generals-screen payload |
| `backend/game_logic/naval.py` | DEF-5 "The Wooden Wall": the ONE naval domain module — fleets store/pooling/coverage, crossing gate, blockade + CS 2.0 closure, expedition odds/resolver, fleet action, Descent camp/diversion/window, per-turn tick, AI posture derivation + build rung |
| `backend/commands/naval_executor.py` | Naval verbs: build_fleet, set_fleet_posture, naval_expedition (quote-then-confirm), naval_diversion (~380 lines) |
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
| `backend/game_logic/diplomatic_ledger.py` | Diplomatic Ledger builder (4 tabs: nations, treaties, balance_of_europe, talleyrand) with fog-filtered army strength |
| `backend/game_logic/war_status.py` | War Status Panel data builder: `build_active_wars()` produces war/coalition/armistice data for HUD, embedded in every response via `_include_popup_passthroughs()` |
| `backend/game_logic/vassal.py` | Vassal system: creation, loyalty, rebellion, cascade, tribute, investment, autonomy, marshal assimilation, Continental System |
| `backend/commands/diplomatic_defiance.py` | Talleyrand sabotage: defiance chance, sabotage types, discovery, confrontation, pre-proposal objection, redemption |
| `backend/save_manager.py` | Save/load file I/O, autosave |
| `backend/game_logic/settlement_*.py` | Imperial Settlement package (CH-1 split, June 10, 2026): `settlement_routes` (L0 routing/reopen/recovery) → `settlement_validation` (L1 primitives/eligibility/validator) → `settlement_baseline` (L2 baseline/presets/per-court acceptance) → `settlement_staging` (L3 draft stores/confirm build/stage/guided payload) → `settlement_ratify` (L4 apply/ratify) → `settlement_actions` (L5 dialogue-action dispatch + arms) → `settlement_offers` (L6 offers/petitions/recurring). Each imports lower layers only. `settlement_preview.py` is the public re-export door (production imports true homes). Tests patch the scorer at `settlement_scoring.calculate_common_peace_acceptance` (stable seam). |

### Godot Core

| File | Purpose |
|------|---------|
| `utils.gd` | Shared color palette (COLOR_ consts + map-layer colors), NATION_COLORS (20-nation Europe set, Slice 7.5 re-authored), `display_nation_name()`/`humanize_nation_keys_in_text()` render-time key translation (July 2 UI Cleanup — R7 chokepoints), bbcode_color/format_number helpers (R15) |
| `popup_base.gd` | Base class for modal popups: close_popup, _disable_all_buttons, _apply_standard_theme (R15) |
| `dialog_manager.gd` | Centralized dialog registry: register, get_dialog, is_any_modal_open, hide_all (R16) |
| `api_client.gd` | Backend communication |
| `game_manager.gd` | Game state coordination |
| `map_renderer_base.gd` | Map renderer base: scene layers, Camera2D+SubViewport, province color-map, hover/click, zoom/pan |
| `map.gd` | The Europe GAME map (Slice 7 rewrite): game glue on the chain `map_renderer_base.gd` → `europe_map.gd` → `map.gd`; name-keyed `/map_topology` handoff, Utils colors |
| `europe_map.gd` / `europe_map_smoke.gd` | Shared Europe renderer (asset paths, Region_NNN→name re-key, registry anchors) / the smoke-scene subclass (seed + owner-cycle demo) |
| `map_label_layer.gd` | Screen-space zoom-LOD map labels (nation/province tiers, occupied-rect avoidance) |
| `main.gd` | Terminal UI, response handling |
| `pause_menu.gd` | Pause menu overlay (Phase 6.5) |
| `campaign_log.gd` | Campaign log overlay (Phase 6.5), CanvasLayer 50 |
| `notification_bar.gd` | Notification bar (Phase 6.5), reparented into top bar |
| `top_bar.gd` | Top bar controller (Session A): screen management, hotkeys, notifications, turn counter |
| `dispatch_view.gd` | Dispatch re-read screen (Session A): CanvasLayer 50, BBCode rendering |
| `strategic_ledger.gd` | Strategic Ledger screen (Session B): CanvasLayer 50, 6 sub-tabs, number key switching, Orders tab cancel buttons |
| `marshal_management.gd` | Marshal Management screen: CanvasLayer 50, card-based marshal view, G key toggle |
| `diplomatic_ledger.gd` | Diplomatic Ledger screen (Session 8B): CanvasLayer 50, 4 sub-tabs (Nations/Treaties/Balance of Europe/Talleyrand), D key toggle |
| `*_popup.gd` (7 files) | Modal popups: coalition_declaration, incoming_proposal, talleyrand_objection, sabotage_discovery, talleyrand_redemption, vassal_rebellion, alliance_paradox. CanvasLayer 100-119 |
| `mailbox_panel.gd` | Browsable mailbox inbox: CanvasLayer 119, click-to-activate rows |
| `war_status_panel.gd` | War Status HUD (CanvasLayer 25) + `war_detail_popup.gd` (CanvasLayer 30) |
| `region_panel.gd` | Region Action Panel (UI-6, CanvasLayer 26): map province click → fog-honest info + typed-command chips (recruit/build/repair/negotiate/marshal orders) |
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
| Jealousy / glory / marshal petitions | `docs/JEALOUSY_SPEC.md` (§0 build record FIRST), `jealousy.py`, `marshal.py` (get_relationship derived −1, get_effective_skill crown, JEALOUSY_* constants), `combat_executor.py` (pipeline 9.5/10.5), `turn_manager.py` (process_turn + autonomous attacks), `cooldown_manager.py` (marshal_petition queue slot), `main.py` (/marshal_petition_response) |
| Marshal recruitment | `docs/MARSHAL_RECRUITMENT_SPEC.md`, `recruitment.py`, `economy_executor.py` (_execute_recruit_marshal), `enemy_ai.py` (P1.75 rung), `europe_1805.json` (marshal_pool), `modding/validator.py` |
| Naval / fleets / blockade / expeditions | `docs/NAVAL_SPEC.md` (§14 landing record FIRST; §18 for yards, coasts and port anchors), `naval.py`, `naval_executor.py`, `europe_1805.json` (navies block), `movement_executor.py` + `combat_executor.py` + `enemy_ai.py` (crossing-gate seams), `diplomacy.py` (process_trade_income blockade arm), `ledger.py` (Admiralty block), `modding/validator.py` (_validate_navies), `tools/gen_port_anchors.py` (the coast audit: run `--audit` and `--check` after any map-art, `is_coastal` or dockyard change) |
| Square formation / Tactical Triangle | `docs/TACTICAL_TRIANGLE_SPEC.md`, `marshal.py`, `combat.py`, `combat_executor.py`, `tactical_executor.py`, `executor.py` |
| Vassal system | `vassal.py` (loyalty/tribute/invest/autonomy/grants/transfer/defection), `world_state.py` (vassals dict, advance_turn), `diplomacy.py` (AP clause, war-cascade vassal arms + VS-4 refusal, wizard vassal actions), `turn_manager.py` (courting + VS-6 bribe), `dispatch.py`, `enemy_ai.py` (P1.6 shore-up; P1.2 walks a contingent home), `contingent.py` (VD-C "The Contingent" — a loyal satellite's men in a shared war: size, commander, raise, stand-down/lose/walk-out, the four exit hooks; `WorldState.stand_down_marshal`; `world.vassal_contingents`); **`docs/VASSAL_DEEPENING_SPEC.md` — the whole depth queue BUILT July 16, 2026 (§8 build record; §1.3/§5/§6/§7 landing records); VD-C LANDED October 3, 2026 (§9.1 gate record, §9.2 landing record)** |
| Diplomatic ledger | `diplomatic_ledger.py` (build_diplomatic_ledger, fog-filtered army strength), `main.py` (GET /diplomatic_ledger, debug endpoints), `world_state.py` (popup fields) |
| Diplomacy wizard / button | `diplomacy_wizard.gd` (wizard UI, `open_for_nation()`), `main.gd` (F1 hotkey, button wiring, command handoff), `main.py` (GET /diplomatic_preview nation list mode), `docs/DIPLOMACY_BUTTON_SPEC.md` |
| War status panel (N4) | `war_status.py` (build_active_wars), `war_status_panel.gd` (HUD), `war_detail_popup.gd` (detail), `main.gd` (_process_active_wars) |
| Suggested terms / smart suggestions | `diplomatic_templates.py` (generate_suggested_terms 5-stage pipeline), `diplomatic_dialogue.py`, `docs/TALLEYRAND_SMART_SUGGESTIONS_SPEC.md` |
| Diplomacy execution | `diplomatic_executor.py` (_execute_diplomatic*, handle_diplomatic_dialogue_response, trust reactions, AI proposal handlers) |
| Dialogue state (R12, PL-27) | `dialogue_manager.py` (push/pop/peek, PL-27 taxonomy: HARD_STOP/SOFT_STOP/HYBRID/LOCAL_PLANNING types), `world_state.py` (transparent properties). Only hard-stop dialogues block commands. Endpoints: `GET /mailbox`, `POST /mailbox/activate` |
| Diplomacy system (Phase 8) | `docs/DIPLOMACY_SPEC.md`, `docs/COALITION_SPEC.md`, `diplomacy.py`, `diplomat.py`, `diplomatic_dialogue.py`, `diplomatic_templates.py`, `ai_diplomacy.py`, `diplomatic_advisory.py`, `vassal.py`, `diplomatic_defiance.py`, `coalition.py` |
| Memory and Pressure substrate (hegemony / betrayal memory / paradox / reliability) | `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v2.4.3 — §8.8 holds the DG-4 call-to-arms episode contract, §8.6.1a authors the Make Amends grievance variant, §8.8.7a authors the existing-alliance termination on defensive refusal; `docs/SCALE_READINESS_PLAN.md` §DG-4 Amendment is the source of truth), `docs/RELIABILITY_IMPLEMENTATION_PLAN.md`, `docs/COMMITMENTS_PRESENTATION_SPEC.md`, `docs/DIPLOMAT_VOICE_BIBLE.md`, `docs/COALITION_SPEC.md`, `diplomacy.py`, `world_state.py` (`betrayal_history`, `next_episode_id`), `commitments` logic within `diplomatic_templates.py`, `campaign_log.py`, `coalition.py` (hegemony engine when landed) |
| Peace Deals / Imperial Settlement | **The settlement arc is COMPLETE (July 2, 2026)** — package: `settlement_routes/validation/baseline/staging/ratify/actions/offers.py` + the `settlement_preview.py` public door (CH-1 split); tests patch the scorer at `settlement_scoring.calculate_common_peace_acceptance`. **NO live successors** — Gate 4 passed in full and Slice H landed July 3, 2026 (`docs/SETTLEMENT_SLICE_H_ALLY_PETITIONS_SPEC.md` v1.0). Normative contracts: `SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` v0.6 (per-court gate), `SETTLEMENT_GUIDED_TERMS_SPEC.md` v0.2 (guided authoring — the freeform editor is retired), `SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32 (SC rows; SC-32 CLOSED). `SETTLEMENT_GATE4_PREFLIGHT_AUDIT.md` owns the surviving CH-6/CH-7 + DW ledger rows. Do not route active work to v0.19-v0.27, Slice F/E, or a fresh G2 start. |
| C3-lite presentation (Memory and Pressure final slice) | `docs/COMMITMENTS_PRESENTATION_SPEC.md` (v0.5.2 — v2.4.3 hegemony-aligned; §8.1a owns the bloc-naming contract folded from the retired Block 3 audit; non-normative bulk trimmed per v2.4.2 deep-audit C7; Slice C trims cut spotlight-tier card variant, split-voice `attributed_lines[]`, N+1 Talleyrand aside), `docs/COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` (historical), `docs/DIPLOMAT_VOICE_BIBLE.md`, `commitments_routing.py`, `diplomatic_templates.py`, `notifications.py`, `notification_bar.gd`, `dispatch.py`. Any `speaker="envoy"` / `speaker="foreign_office"` template MUST resolve through `resolve_named_diplomat()` or chancery fallback per Voice Bible. Live notice families include treaty breach, hard-reject posture, Make Amends, Balance of Europe, DG-4 call-to-arms, witness strike, and paradox popup/resolution metadata. |
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
5. Add keywords to mock parser in `llm_client.py` (search "ADD NEW ACTION KEYWORDS HERE" — do not trust line numbers), then **regenerate the addressee rule's verb set**: `python -m tools.gen_routed_order_words` (CX-R1 — `backend/ai/routed_order_words.py` is generated from the router's branches; the census in `tests/test_cx_r1_the_unbound_name_spends_nothing.py` fails until you do)
6. Add few-shot example in `prompt_builder.py` if complex
7. If triggerable by objection, add to `objection_actions` — ⚠ **it is in `executor.py`, NOT `disobedience.py`** (corrected IQ1-2, Sept 13 2026; navigate by the symbol). A verb that is a PURCHASE rather than an order is deliberately absent from it (e.g. `purchase_levy`); record that judgement on the slice.
8. Add to_dict/from_dict if new state fields needed
9. Add to `ACTION_DISPLAY` in `display_names.py`
10. Add to `DEFIANCE_DISPLAY` + `OBJECTION_DISPLAY` — ⚠ **both are in `display_names.py`, with NO leading underscore** (corrected IQ1-2, Sept 13 2026: the old row named the wrong file, the wrong names and two stale line numbers; `campaign_log.py` holds only import aliases)
11. Add event type to `CAMPAIGN_LOG_TYPES` in `campaign_log.py` (line ~83) + format in `format_event_oneliner()`
12. Add a golden-corpus entry in `tests/data/parser_golden_corpus.json` (CR-1) — the eval harness's action-coverage gate fails CI for any mock-reachable action with zero corpus coverage

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

Strategic orders (MOVE_TO, PURSUE, HOLD) cost 2 AP (1 for literal and the sovereign); **SUPPORT costs 1 AP for every marshal** (SR-2e, Sept 26, 2026). One source: `Marshal.strategic_order_ap(order_type=…)` — pass the order's type at every site that prices or quotes a strategic order. Key patterns:

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
| New dialogue type shows in terminal | Add the dtype to the `main.gd` popup whitelist (search the dtype list — do not trust the line number) so Godot renders it. **Do NOT reach for `world.proposal_result_popup`** — FA-S17-D9 (Sept 12, 2026) retired its orphan scene: that field is a legacy INFORMATIONAL channel whose payload rides the response as `proposal_result` and lands on the notice rail, never as a modal. A dialogue that concludes with a CHOICE needs its own popup per the "Adding a new popup" recipe. |
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
".venv\Scripts\python.exe" -m backend.main    # Runs on port 8005 (MUST be -m module form post-cutover)

# Tests (MUST use Windows paths — see note above)
cd "C:\Users\User\PycharmProjects\project-sovereign-map"
".venv\Scripts\python.exe" -m pytest tests/ -q -n 8 --dist loadgroup   # Full suite, parallel (what the hook runs; ~5:12)
".venv\Scripts\python.exe" -m pytest tests/ -v                          # Full suite, serial (~26 min)
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
| **THE PRE-DEPLOY PLAN (routing authority from Oct 8, 2026)** — code health, the UX/UI review, the three deep dives, the order to the deploy | **`docs/PRE_DEPLOY_PLAN.md`** §2 the order · `docs/CODE_HEALTH_PLAN.md` · `docs/UX_UI_REVIEW_PLAN.md` · `tools/_code_health_census.py` |
| **THE PLAN TO THE FINISH (routing authority from Sept 28, 2026)** — every open defect, every pillar, and how a pillar is scored | **`docs/SCORE_FINISH_SPEC.md`**: §3 the build order, §4 the instrument, Appendix A the checklist. To count the ledgers: `.venv/Scripts/python.exe tools/defect_census.py --open` |
| **The Improvement Queue (row IQ) — landing records, rulings, dissents** | **`docs/IMPROVEMENT_QUEUE_SPEC.md`** — row IQ's OWNING SPEC. STATUS stays the ROUTING authority (which row is next); this holds the per-slice landing records, the crux ruling, the filed dissent and re-open condition, and the re-stated completion items. Slice ids are `IQ1-n` (the first two shipped as `SW-0`/`SW-1`, which collides with `SEASONS_WEATHER_SPEC.md`; the alias is recorded). |
| **PLAYTEST / live-verify / evaluate the game (START HERE for any of those)** | **`docs/PLAYTESTING.md`** — Mode A `tools/playtest_driver.py` (in-process, seeded, popup-answering, digest output) is the default; Mode B live-HTTP (`SOVEREIGN_PORT`), Mode C client visual pass; fixtures in `tests/fixtures/playtest_saves/` |
| **UI Visual Foundation Sweep (▶ NEXT — take slices UI-0→UI-3 in order)** | **`docs/UI_VISUAL_FOUNDATION_SPEC.md`** (queued July 12, 2026; assets in `assets/` + credits at repo-root `THIRD_PARTY_LICENSES.md`) |
| Wave 6 fun-factor build (✅ COMPLETE July 10, 2026) | `docs/WAVE6_FUN_FACTOR_SPEC.md` (§15 DoD; audit evidence in `docs/audits/CREATIVE_AUDIT_2026_07_10.md`) |
| **Open bugs (consolidated)** | **`docs/BUG_FIXES.md`** |
| **Row REV follow-ups (the Aug 30, 2026 review's open items)** | **`docs/REV_FOLLOWUPS.md`** — **ALL FOUR CLOSED**: three on Aug 31, 2026 (REV-V3 the rail census, REV-F1 the `battles_this_turn` wipe, REV-V4 both flow fixes staged and shot), and **UX23-R9 on Sept 1, 2026** — the bugles' fade, not their cap, was the lever. Landing records = `BUG_FIXES.md` §THE FOLLOW-UPS and §UX23-B |
| **Design refinement items** | **`docs/DESIGN_REFINEMENT.md`** |
| **AI Intent (next systems phase — ✅ DESIGN GATE HELD July 20, 2026; ✅ VERIFICATION PASS v1.3 July 21, 2026; ✅ STRUCTURE & CREATIVE PASS v1.4 July 24, 2026; build order = spec §11 Stages A–G)** | **`docs/AI_INTENT_SPEC.md` v1.4 — §11 is the PHASED BUILD PLAN (builders START THERE: Stages A–G with per-stage scope/entry/exit + the living cut list); §6 is the authoritative gate record; §10 is the v1.3 correction table (read it before building anything); §3.4 is the great-power aliveness contract; §9/§9a/§12 are the review records.** **v1.2 (creative/gameflow review, §6 untouched):** **§4.2b the participation surface** — when an AI-vs-AI war brews *both sides court France* (join / sell neutrality / sponsor / broker / refuse *having been asked*), turning pin 3 from a limit into a mechanic, + the third-party war-exhaustion display; **§3.6 where the surprises live** — the fog boundary re-drawn as *no fog on dispositions, fog on agreements and timing* (the **sealed article**, discoverable per pin 12), plus **emergent designs** (a humiliated nation promotes a grievance into a new deck design — Prussia after Jena) and the **volte-face** (a beaten-then-courted power reverses — Tilsit); **§4.6a the six beats + the one-foregrounded-crisis tempo rule** (the narration cap **amended** to govern routine lines only — beats are events, exempt); **§3.7 Britain as a contested subsidy auction** rather than a wall; **§3.5 the mirror** — France's own ledger row shows Europe's derived reading of France, and the player can be wrong about how they are seen; **§7a the seven historical scenes** as a falsifiable ≥5-of-7 reachability list; pins 11–13 (surprise is never a lie / sealed articles are discoverable / a living Europe must not become a soap opera, measured); **§3.8 VARIANCE** — the self-correction that surprise-within-a-playthrough ≠ variance-across-playthroughs: `agendas.py`/`ai_diplomacy.py`/`coalition.py` contain **zero** `random` calls and **no campaign seed exists**, so every campaign would open identically → a **serialized campaign seed** perturbing *the bars, not the choices* (weight/opportunism/dwell/cooldowns + tie-breaks, weighted late, character fixed per §3.4, D4 intact — it invalidates memorisation not understanding), **order-constrained to land with AI-1** (row AI-0b), pin 14, and the AI-V acceptance run promoted to an **N-seed sweep** because every §7 number had been specified against a single deterministic trace; **✅ D7 DECIDED July 20, 2026 — the 1805 OPENING is seeded too, within authored historical bounds** (gate record §6 D7 + envelope §3.8.1): the bounds are **authored content, not a formula** — every varying value carries an authored range in `europe_1805.json` and **no band → no variance**, so fidelity is reviewable by reading the scenario file, enforced in `modding/validator.py`, and ahistorical drift is structurally impossible; **Tier 1 FIXED on every seed** (province ownership, roster, capitals, `starting_wars`, deck CONTENT, marshals+skills+relationships, treasury/manpower/force, the §3.4 statecraft profiles), **Tier 2 BANDED** (relations per pair, deck ORDER among equally-live designs, initial ladder readiness, small real grudges, the minors' lean, Britain's first client, `threat_level` narrowly — widening escalates), **Tier 3 derived**; the **historian test** pins every seed (Third Coalition exists · France at war with Austria/Britain/Russia and **at peace with Prussia** · turn-0 designs from the nation's own deck · nobody holds a province it didn't hold in 1805); **`historical`/unset reproduces today's boot byte-for-byte**, pinned suite-wide in conftest like `SOVEREIGN_SCENARIO=none` → zero test churn, pins 1 + 14 **narrowed not deleted**; row **AI-0c** order-constrained to the front with AI-0b. *(v1.3: the seed's default lives in `WorldState.__init__`, NOT in `main.py`'s scenario-path selector — 75 `from_scenario` calls across 42 test files bypass main.py, including the M7 world, so siting it there would red pin 2 on day one.)* New rows AI-0b/0c/1b/2d/2e/3b/5b/6b with scope triage in §8 (Austria the patient coalition-builder / Prussia the bandwagoner who reneges / Russia the distant arbiter / Britain the paymaster who never marches — a derived per-nation `statecraft` weighting, no LLM, no new serialized object; the majors must feel like distinct statesmen conducting politics WITH EACH OTHER, asserted by AI-V's in-character + homogeneity-guard pins) (ROADMAP row AI; motivating evidence `docs/audits/CREATIVE_AUDIT_2026_07_19.md` §2.1/§3 — **no AI nation can decide to go to war, ever**: the coalition is a *global anti-France threat scalar*, not a decision). Decisions: **D1** cap 2 simultaneous AI-initiated wars (40-turn acceptance band 1–4) · **D2** AI wars may eliminate minors, never a great power's last capital · **D3** France stays the gravitational centre — machinery generalises, but a non-player coalition forms only when that hegemon's share exceeds France's · **D4** ladder fully open (diplomacy has no fog), only *timing* uncertain · **D5** three counter-instruments ship WITH AI-2 (compensation / sponsorship / guarantee; a bought-off design becomes a standing expectation and reneging is the strongest casus belli — Schönbrunn → Jena) · **D6** BD first, AI-1+AI-2 as a playable increment, re-check before AI-3. **Four v0.1 claims corrected in §0.1 and they change the build:** the AI-vs-AI `war_objective` branch DOES have callers (`combat_executor.py:3482` — so AI-3 reuses that seam and adds **no new PEACE→WAR edge**); threat generalisation is a serialized scalar → per-target migration across 16 backend modules + 10 `.gd` (contract §4.4a, the phase's long pole); a bandwagon rung and an AI-vs-AI diplomacy path already exist but are narrow/near-untested; and ~~`_agenda_cache` is NOT invalidated~~ **← WITHDRAWN by v1.3**. **▶ v1.3 (July 21, 2026) — THE VERIFICATION PASS** (fresh-mind review: 10 ground-truth readers + 10 design lenses + 2 refuters per finding; **§6 D1–D7 all survived, untouched**; 19 corrections tabled in **spec §10**). **Three corrections change the build: (1) §0.1 Correction D is WITHDRAWN and row AI-0 is DELETED** — `_agenda_cache` IS cleared (`invalidate_bloc_members_cache`'s last statement, `world_state.py:1695`, the NA-0 fix; `invalidate_active_nations_cache:1619` chains into it and `set_diplomatic_state` reaches it directly; pinned twice in `test_nation_agendas.py`) and **following the old instruction would have re-opened the P1 NA-0 closed**; (2) **the historian test's "no minor boots at war" clause is FALSE on the shipped scenario** — Spain/Holland/Bavaria/KingdomOfItaly all boot at war, as they did in 1805, so the pin contradicted its own Tier 1 and would red on the `historical` seed; §3.8.1 now carries **six** corrected clauses; (3) **third-party war exhaustion is NOT "a display wire"** — it never accrues and **decays −5/turn**, making it the **fourth** France-literal system to generalise (new row **AI-4c**, must not be cut). **Three structural additions answer the brief:** **§3.1a the DESCENT** (the ladder only ever climbed — how a want cools, a design is abandoned, a war ends; the three seams that lower it are dead for AI-vs-AI, which is why §4.4's own "one-way ratchet" risk was live), **§3.9 HISTORICAL ATTRACTORS** (turn 0 was falsifiable and turn 40 was not — resolved as **assure the shapes, vary the casting**: D3's gravity + Tier-1 content + statecraft + the compensation/renege loop are why a forked campaign still rhymes; a Fourth Coalition against Austria in 1809 over Silesia is a *better* outcome than reproducing 1806), and **§2 principle 9 REACTIVITY** (a change in the world must change what somebody wants, will pay, or can do — with a four-row obligation table). **Four contracts written that v1.2 asserted in a sentence:** §4.3a declaration (the `OPEN_MOVEMENT_STATES` path lets an AI capture with NO war declared; `war_objective` cannot carry a design — the enum rejects it), §4.4a **steps 5–6** (producer migration + decay; without them every non-player threat slot is permanently 0 and D3's eclipse clause is unreachable), §4.4b coalition de-anchoring (**nine** France bindings, not one), §4.2c delivery (`MAX_BANDWAGON_PER_TURN=2` silently eats intent asks). **The phase had NO Godot work at all** → §4.6b client surfaces + row **AI-6c** + pin 20. New rows **AI-2a** (diplomacy-path convergence — six seams incl. the missing AI-AI refusal record, without which AI-3's ladder gate is unsatisfiable), **AI-4c**, **AI-6c**; AI-5b splits into (i) emergent designs **Core** / (ii) volte-face may slip. Six new pins **15–20**; AI-V becomes a **three-arm** sweep (control/variance/acceptance) + a scripted-France arm; §7a gains an arm map. Build order now **BD → AI-0b/0c → AI-1 → AI-2 → re-check → AI-3 → AI-4 → AI-5/6 → AI-V**, and the D6 re-check carries a **written cut list** (§9a). **▶ v1.4 (July 24, 2026) — THE STRUCTURE & CREATIVE PASS (Fable, fresh-mind):** **§11 is now the phased build plan** — Stages A (dice & bounds) → B (Europe shows its hand) → C (the bargaining table) → ⛩ re-check → D (war & peace, INDIVISIBLE — a war that can start must be able to end) → E (consequence & character) → F (the stage) → G (AI-V) — collating scope/entry-exit/beat-ownership/cut-list into one place (**the living cut list moved to §11.2**; §9a's copy is the record); **§12 records six gameplay additions, none reopening §6:** (1) **the deterrence receipt** — beat 7 "The Crisis Passes" + pin 21 (a foregrounded crisis always ends on screen, cause named + instrument credited — D5's success case was invisible, the worst reward loop a strategy game can ship; Ochakov 1791); (2) **Russia's second design** `gulf_and_straits` (`acquire_regions` [Finland, Rumelia], authored BEHIND arbiter, row **AI-0d**, pin 22 boot-inactive-on-every-seed) — **§7a scene 4 was structurally unsatisfiable**: a volte-faced Russia had nothing to advance to, the "aimed at a third party" aim had no object; also gives AI-3 its natural far-from-France war (the Finnish War / Russo-Turkish 1806), the licence its marquee use, and AI-0c authors the deck-order band over AUSTRIA's existing pair instead (Italy-first vs Germany-first — the real Vienna war-council debate); (3) **the licence** — D5-2's own word, defined: directed sponsorship at `amount_per_turn: 0` whose consideration is committed non-interference, pin 23 (a licence is a bond; Tilsit's green-lights; ONE record with sell-neutrality, not two); (4) **the purchased dispatch + the player's own seal** — AI-3b's principle-7 half, pin 24 (active discovery verb via Talleyrand's network; France may seal its own articles for a premium — masking defers third-party reads at the intent-derivation chokepoint, never deletes consequence; cut-list #1 takes both halves); (5) **the Arbiter's Offer** (row **AI-5c**, may slip, cut-list #2) — armed mediation gives `arbiter_of_europe` its missing behaviour (refusal consequence DERIVED only — the weight rise feeds the existing ladder and statecraft does the rest = Prague 1813 by machinery); (6) **the allegiance auction** (inside AI-2d) — a minor's flip announced as in-play and biddable by both sides (Bavaria/Bogenhausen 1805, signed in secret — a sealed-article natural). Pins **21–24**; the beats are **seven**; header rebuilt as a reading map + version table. |
| **AI war decision / exposure calculus (✅ GATED + BUILT July 25, 2026)** | **`docs/AI_WAR_DECISION_SPEC.md` v1.0 — gate record §6.1 + rulings §6.2 + landing record §8 (authoritative)**; probe/measure memo `docs/audits/AI_3R_PROBE_2026_07_25.md`. D1's global cap is DELETED, replaced by the HOI4-style exposure calculus (`war_council.get_exposure_view`/`get_free_strength` — free strength = standing − the rear-security reserve against the worst armed neighbour, max-not-sum, 60% cap; only free strength counts toward the 1.25× ratio); §2.2 moment terms in `intent._derive_weight`; beat-7 causes exposed/outmatched/penniless; authored `wary_of` via the scenario `statecraft` key (validator-clamped); suite guard `SWEEP_WAR_ALARM`. Amended `AI_INTENT_SPEC.md` §6 **D1 only**; the D1 band measurement rides AI-V arm (a). Tests: `test_ai_war_decision_ai3r.py`. |
| **Naval abstraction / Free Ireland / the Descent (DEF-5 — ✅ SPEC AUTHORED Aug 1, 2026, USER GATE PENDING)** | **`docs/NAVAL_SPEC.md` v1.0 "The Wooden Wall" — §12 is the gate (Q1–Q6, recommended defaults; Q5 = promote naval v1 into EA scope).** One-store abstraction (`world.fleets`: ships/readiness/posture — NO naval map layer, no ship pieces), authored `navies` block in `europe_1805.json` (fleets/ports/dockyards — never the over-true `is_coastal`, DEF-8 untouched). Four consequences: §4.1 crossing gate at BOTH movement seams (A5: Spain can never again walk to London; Britain's descents pass on ratio), §4.2 blockade (trade ×0.5, island-clause WE, "Blockade"/"Admiralty" ledger components), §4.3 expedition (≤15k, Bantry odds; Free Ireland via NA-6c carve + `erin_free` + "The Irish Question"), §4.4 fleet action (Trafalgar resolver, seeded jitter). Arcs: §5.1 Strangulation (CS 2.0 closure → Britain sues without invasion), §5.2 Free Ireland (per the MAP-plan DEF-5 rider verbatim), §5.3 the Descent (camp/diversion/window — re-derives the 1805 Combined-Fleet math). Slices NV-0..NV-V; history H1–H7; numbers N1–N11 + anchors A1–A5; deferrals NV-D1..D8 all owned. |
| **Seasons & Weather (HC-6 — SPEC AUTHORED Aug 14, 2026, ⚠ USER GATE PENDING at §6)** | **`docs/SEASONS_WEATHER_SPEC.md`** (consumes the HC-0 calendar; nothing lands before the gate returns) |
| **Reforms of State — laws with upkeep, the Staff (the fifth action), diplomatic-point banking (SR-D1 — RULED Sept 27, 2026; built at Chunk 5's head as SR-5r)** | **`docs/REFORMS_SPEC.md`**: §0 gate record (authoritative) and §0.1 readings FOR USER CONFIRMATION; the build contract — effect types §4, draft catalogue §6, AI §7, acceptance §11, slices §12 |
| **National doctrines — a strength and a flaw per great power, each cured by a reform law (SR-D2's doctrine half — RULED Sept 27, 2026; built at Chunk 7 as SR-7d)** | **`docs/DOCTRINES_SPEC.md`**: §0 gate record (authoritative) and §0.1 readings FOR USER CONFIRMATION; the five doctrines §2, seams §3, acceptance §6, slices §7 |
| **War withdrawal / the Emperor's start (WIN-D3 + WIN-D5 — SPEC AUTHORED Aug 16, 2026, ⚠ USER GATE PENDING at §7)** | **`docs/WAR_WITHDRAWAL_SPEC.md`** "The Road Home" — ending a war grants a temporary right of transit on the ONE `can_enter_territory` predicate + free 0-AP march orders home, both sides; §9 boots Napoleon at Lorraine. Nothing lands before the gate returns |
| **The Gazette / calendar (HC-G + HC-0, LANDED Aug 14, 2026)** | `backend/game_logic/gazette.py` + `calendar.py`, gate record §9.0/§9.6; `gazette_view.gd`, top_bar (N) |
| Phase timeline | `docs/ROADMAP.md` |
| Game systems (combat, trust, disobedience, LLM, cavalry, strategic) | `docs/SYSTEMS_REFERENCE.md` |
| Enemy AI decision tree | `docs/ENEMY_AI_REFERENCE.md` |
| Combat specs (V2b, Multi-Marshal, Tactical Triangle) | `docs/V2B_DEFIANCE_SPEC.md`, `MULTI_MARSHAL_SPEC.md`, `TACTICAL_TRIANGLE_SPEC.md` |
| Diplomacy specs (system, coalition, wizard, suggestions) | `docs/DIPLOMACY_SPEC.md`, `COALITION_SPEC.md`, `DIPLOMACY_BUTTON_SPEC.md`, `TALLEYRAND_SMART_SUGGESTIONS_SPEC.md` |
| Jealousy + Marshal Recruitment (LANDED July 11, 2026) | `docs/JEALOUSY_SPEC.md` (§0 = gate+build record), `docs/MARSHAL_RECRUITMENT_SPEC.md`, SYSTEMS_REFERENCE §26–§27 |
| Vassal Deepening (✅ **BUILT COMPLETE July 16, 2026** — VS-R + Slice 0 + VS-3..VS-6 + VP-D1/VP-D6) | `docs/VASSAL_DEEPENING_SPEC.md` (§8 build record + per-slice landing records) + memo `docs/audits/VASSAL_AUTHORITY_COUPLING_RESEARCH_2026_07_14.md` |
| Memory and Pressure (substrate + presentation) | `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v2.4.3), `RELIABILITY_IMPLEMENTATION_PLAN.md`, `COMMITMENTS_PRESENTATION_SPEC.md` (v0.5.2 C3-lite hegemony-aligned; §8.1a owns bloc-naming contract post-Block-3 fold), `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` (historical) |
| Peace Deals (umbrella + sub-specs) | **COMPLETE July 2, 2026** — routing: `docs/ROADMAP.md` §Current Phase Queue + `docs/STATUS.md`. Live: Slice H draft spec (`SETTLEMENT_SLICE_H_ALLY_PETITIONS_SPEC.md`, user gate pending) + Gate 4 visual half. Normative: `SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` v0.6, `SETTLEMENT_GUIDED_TERMS_SPEC.md` v0.2, `SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32; `SETTLEMENT_GATE4_PREFLIGHT_AUDIT.md` owns the surviving ledger rows. Historical anchors: `PEACE_DEALS_UMBRELLA_SPEC.md`, `BILATERAL_PEACE_HARDENING_SPEC.md`, `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`, `WAR_BARGAIN_SPEC.md` (LANDED April 2026), `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` + its implementation plan. |
| Diplomat voice bible / playtest | `docs/DIPLOMAT_VOICE_BIBLE.md`, `COMMITMENTS_PLAYTEST_SCRIPT.md` |
| UI specs (top bar, fog) | `docs/TOP_BAR_SPEC.md`, `FOG_OF_WAR_SPEC.md` |
| Save format / serialization | `docs/SAVE_FORMAT_REFERENCE.md` |
| Adding content / modding | `docs/ADDING_CONTENT.md`, `MODDING_FORMAT.md` |
| Vision, future design, manual tests | `docs/VISION.md`, `FUTURE_DESIGN.md`, `MANUAL_TEST_PLAN.md`, `TUTORIAL_SCRIPT.md` |
| Architecture (audit + refactoring) | `docs/ARCHITECTURE_AUDIT_REPORT.md`, `ARCHITECTURE_AUDIT_SPEC.md`, `ARCHITECTURE_REFACTORING_PLAN.md` |
| **Component-by-component audit playbook (fix-as-you-find)** | **`docs/AUDIT_GUIDELINE.md`** |
| Archived specs & session history | `docs/archive/` |

## Documentation Rules

**If you changed behavior, update the doc that describes it.** Session ends → STATUS.md. Phase completed → ROADMAP.md + STATUS.md. System changed → SYSTEMS_REFERENCE.md. New fields → SAVE_FORMAT_REFERENCE.md.

**Deferred work must have a HOME and a LANDING.** Any item marked hidden, cut, deferred, later, v2, polish, or backlog must name its owner spec/row, landing slice, completion definition, STATUS tracking line, and behavior test in the same table or bullet. If no owner row or landing slice exists, create that contract before implementation continues. Never leave deferred work as vague "later polish," "future work," disabled placeholder copy, or an unowned player-facing promise.

CLAUDE.md "Current Phase" must always list remaining items. Completed items get brief summaries. Never mark a phase complete when items remain in ROADMAP.md.

---

## Environment

**LLM layer:** the Anthropic path goes through the official `anthropic` SDK
(`providers.py`), NOT raw HTTP — that migration July 18, 2026 is what gives it
retries with backoff, typed errors and the request id. Model pin
`claude-haiku-4-5`; forced tool-use structured output at temperature 0; a `stop_reason`
check catches a `max_tokens`-truncated tool call (which is otherwise
indistinguishable from a complete parse). The LLM is consulted ONLY for
fast-parse results below the 0.7 confidence gate. Prompt caching is
deliberately NOT used — see STATUS.md for why, so it is not re-litigated.
(Sept 26, 2026: L-1 made the parse prompt static-first, so the structural
reason recorded there no longer holds; caching stays off until the user decides.)

`.env`: `LLM_MODE=mock|anthropic|groq` (`groq` is an unimplemented stub — degrades to fast-parser-only; Pre-EA item), `ANTHROPIC_API_KEY` if anthropic. Server: `127.0.0.1:8005`, CORS enabled.
