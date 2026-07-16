# Save Format Reference

## Overview

This document defines the serialization format for all game objects in Project Sovereign.
A future save/load system should use this as the specification.

**Serialization validation:** All roundtrip tests pass (33 tests in `tests/test_serialization.py`).

## Version

- **Format version:** 3 (`save_manager.FORMAT_VERSION` — v3 since Map Slice 5's Europe cutover, July 1, 2026; pre-cutover v1/v2 saves fail with a clear versioned message, see the Version-3 migration paragraph near the end of this doc)
- **Last updated:** 2026-07-02 (Map Slice 9 header reconciliation; the example blocks below are LEGACY-shaped — 19-region world, `max_turns: 40`, 5-nation tables — kept as compact illustrations; a Europe-world save carries `"sovereign_map": "europe"`, 126 name-keyed regions, the 20-nation tables, `max_turns: 60`, and per-region `grid_position`/`is_coastal`)
- **Compatible with:** Memory and Pressure v2.4.3 substrate (nation-level `diplomatic_reliability`, `betrayal_history`, `next_episode_id`, `commitment_paradox_popup`, `anti_renewal_cooldown`, `oathbreaker_posture`, `call_to_arms_loyalty_bonds`) + Diplomacy Button Session A + Peace Deals WPS-A (`war_objectives`) + WPS-C (`alliance_origins`) + WB-A (`diplomatic_commitments`, `next_commitment_id`) + WB-C (`next_join_opportunity_id`, `war_entry_reroll_memory`, `pending_ally_entry_opportunities`) + Imperial Settlement Slices A1/A2/A3 (`next_war_instance_id`, `war_instances`, `archived_war_instances`, plus bargain `war_id`/`side_at_creation`/`side_leader_at_creation` snapshot fields and `participant_meta[nation].exited_turn`/`exit_path` elimination stamps) + Imperial Settlement Slice B1 + B2 (`war_contribution_scores` episode-scoped per-nation records with B2 emitter dedupe state `seen_occupation_event_ids`, `seen_support_event_ids`, `support_caps`) + pending Imperial Settlement Slice C/D fields documented below

> Slice A3 post-review fix `d5bcefc` extends merge rewrite and invariant coverage to nested event-log / ledger payload `war_id` fields in addition to bargains, pending dispatch events, and no-op-safe future Slice B/C containers.

## Top-Level Structure (WorldState)

```json
{
  "format_version": "1.1",

  "player_nation": "France",
  "current_turn": 1,
  "max_turns": 40,
  "gold": 800,
  "nation_gold": {"France": 800, "Britain": 1500, "Prussia": 800, "Austria": 600, "Saxony": 200},
  "manpower_pools": {
    "France": {"infantry": 80000, "cavalry": 15000, "artillery": 10000},
    "Britain": {"infantry": 50000, "cavalry": 8000, "artillery": 5000},
    "Prussia": {"infantry": 60000, "cavalry": 10000, "artillery": 5000},
    "Austria": {"infantry": 40000, "cavalry": 5000, "artillery": 3000},
    "Saxony": {"infantry": 20000, "cavalry": 3000, "artillery": 2000}
  },
  "game_over": false,
  "victory": null,

  "max_actions_per_turn": 4,
  "actions_remaining": 4,
  "bonus_actions": 0,
  "admin_actions_remaining": 2,
  "max_admin_actions": 2,

  "nation_bankruptcy_turns": {"France": 0, "Britain": 0},
  "gold_spent_this_turn": {"France": 0, "Britain": 0, "Prussia": 0},

  "regions": { ... },
  "marshals": { ... },

  "authority_tracker": { ... },
  "vindication_tracker": { ... },
  "pending_objection": null,
  "pending_redemption": null,
  "pending_capture_choice": null,

  "mild_concerns_this_turn": [],
  "objection_popups_this_turn": [],

  "enemy_nations": ["Britain", "Prussia", "Austria", "Saxony"],
  "nation_actions": {"Britain": 4, "Prussia": 4},
  "diplomatic_states": {"Austria|Britain": "NON_AGGRESSION", "Austria|France": "PEACE", ...},
  "nation_relations": {"Austria|Britain": 0, "Austria|France": -20, ...},
  "diplomats": {"France": {"name": "Talleyrand", "nation": "France", "personality": "schemer", "skill": 10, "trust": 55, "biography": "..."}, ...},
  "diplomatic_points": 4,
  "max_diplomatic_points": 5,
  "nation_authority": {"Britain": 60, "Prussia": 60, "Austria": 60, "Saxony": 60},
  "war_scores": {},
  "battle_records": {},
  "decisive_battles": {},
  "armistice_cooldowns": {},
  "armistice_turns": {},
  "nation_dp": {},
  "previous_treaties": {},
  "turns_below_threshold": {},

  "pending_diplomatic_dialogue": null,
  "active_diplomatic_mission": null,
  "intel_grants": {},
  "talleyrand_state": "IDLE",
  "proposal_in_transit": null,
  "player_proposal_cooldowns": {},
  "active_treaties": {},

  "ai_proposal_cooldowns": {},
  // "diplomatic_queue" REMOVED — legacy items migrated to dialogue_manager on load
  "proactive_suggestion_cooldowns": {},
  "ai_stalemate_counters": {},
  "ai_proposal_metadata": {},
  "previous_war_scores": {},
  "relation_history": {},

  "talleyrand_defiance_cooldown": 0,
  "pending_talleyrand_sabotage": null,
  "talleyrand_override_history": [],

  "threat_level": 0,
  "threat_sources_this_turn": [],
  "active_coalition": null,
  "coalition_brewing": null,
  "coalition_cooldown": 0,
  "coalition_count": 0,
  "war_exhaustion": {},
  "we_dispatched_thresholds": {},
  "war_start_turns": {},

  "casus_belli": {},
  "ultimatum_global_cooldown": 0,
  "diplomatic_reliability": {"France": 0, "Britain": -10},
  "betrayal_history": {},
  "next_episode_id": 1,
  "diplomatic_history": [],
  "commitment_paradox_popup": null,
  "peace_ratification_log": [],
  "war_objectives": {},
  "alliance_origins": {},
  "diplomatic_commitments": {},
  "archived_diplomatic_commitments": [],
  "next_commitment_id": 1,
  "next_war_instance_id": 1,
  "war_instances": {},
  "archived_war_instances": [],
  "war_contribution_scores": {},
  "archived_war_contribution_scores": {},
  "reparations_cooldown": {},
  "anti_renewal_cooldown": {},
  "oathbreaker_posture": {},
  "call_to_arms_loyalty_bonds": {},
  // legacy alias: "alliance_paradox_popup" is accepted on load and migrated to "commitment_paradox_popup"

  "active_battles": {},
  "battle_history": [],

  "battles_this_turn": [],
  "command_history": [],

  "event_log": [],

  "notifications": [],
  "last_bankruptcy_notification_tier": 0,
  "eliminated_nations_notified": [],

  "coordination_tutorial_shown": false,
  "delegation_hint_shown": false,

  "nation_starting_regions": {
    "France": ["Paris", "Belgium", "Normandy", "Lyon", "Brittany", "Bordeaux", "Marseille", "Milan"],
    "Britain": ["Netherlands", "Waterloo", "Hanover"],
    "Prussia": ["Berlin", "Rhineland"],
    "Austria": ["Vienna", "Bavaria", "Bohemia", "Tyrol"],
    "Saxony": ["Saxony", "Dresden"]
  },

  "last_morning_dispatch": {},

  "intel": {
    "Paris": { ... },
    "Belgium": { ... }
  }
}
```

### WorldState Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `format_version` | string | "1.1" | Save format version for compatibility |
| `player_nation` | string | "France" | Nation controlled by player |
| `sovereign_map` | string | "legacy" | Which map the world was built on: "legacy" (19-region fixture) or "europe" (126-province game map). `from_dict` rebuilds the matching region set + roster (Map Slice 4/5). |
| `current_turn` | int | 1 | Current turn number |
| `max_turns` | int | 40 | Maximum turns before game ends |
| `gold` | int | 800 | Player's treasury (backward compat, reads from nation_gold) |
| `nation_gold` | dict | {"France": 800, ...} | Per-nation treasury |
| `manpower_pools` | dict | DEFAULT_MANPOWER_POOLS | Per-nation infantry/cavalry/artillery reserve pools |
| `game_over` | bool | false | Whether game has ended |
| `victory` | string\|null | null | "victory", "defeat", or null |
| `max_actions_per_turn` | int | 4 | Base actions per turn |
| `actions_remaining` | int | 4 | Actions left this turn |
| `bonus_actions` | int | 0 | Extra actions from admin role |
| `admin_actions_remaining` | int | 2 | Admin actions left this turn (Phase 6.2.B) |
| `max_admin_actions` | int | 2 | Max admin actions per turn (Phase 6.2.B) |
| `nation_bankruptcy_turns` | dict | {} | Per-nation bankruptcy counter {nation: int} (Phase 6.2.B) |
| `gold_spent_this_turn` | dict | {} | Per-nation gold spending tracker for turn summary. Records all gold spent this turn (recruit, build, repair). Reset at start of each turn. |
| `regions` | dict | {} | Map of region_name -> Region |
| `marshals` | dict | {} | Map of marshal_name -> Marshal |
| `authority_tracker` | dict | {} | AuthorityTracker state |
| `vindication_tracker` | dict | {} | VindicationTracker state |
| `pending_objection` | dict\|null | null | Objection awaiting response |
| `pending_redemption` | dict\|null | null | Redemption event awaiting response |
| `pending_capture_choice` | dict\|null | null | Plunder/secure choice awaiting response: `{region, capturer, previous_controller}` (Phase 6.2.E) |
| `pending_marshal_petition` | dict\|null | null | **Jealousy v3.2:** the marshal-petition channel — kind-discriminated (`jealousy_confrontation`/`rivalry_confrontation`/`fontainebleau`/`war_weary`) with `title/body/speaker/options[]/context`. Answered via POST `/marshal_petition_response`; re-pushed to the popup queue each turn while unanswered. |
| `jealousy_confrontations_seen` | list[str] | [] | First-time §6 confrontation pairs already shown (sorted `"A\|B"` keys). |
| `rivalry_transitions_seen` | list[str] | [] | §6b transitions already fired (`"A\|B@-1"` keys — once per transition per pair). |
| `fontainebleau_last_turn` | int | -999 | ESP-1 cooldown anchor (last collective-petition turn). |
| `marshal_pool` | dict | {} | **Marshal Recruitment:** authored candidate bench per nation `{nation: [entries]}` — entries removed as commissioned (`MARSHAL_RECRUITMENT_SPEC.md`). |
| `mild_concerns_this_turn` | list | [] | V2a: MILD concerns for turn log (cleared each turn) |
| `objection_popups_this_turn` | list | [] | V2a: Per-marshal popup cap tracking (cleared each turn) |
| `ai_failed_action_cooldowns` | dict | {} | AI failed action retry cooldowns {marshal: {action: turns}} |
| `ai_refortify_cooldown` | dict | {} | Per-marshal re-fortify cooldown turns {marshal_name: int}. Set to 2 when stagnation forces unfortify, decremented each turn. Blocks P5/P8 fortify while active. |
| `enemy_nations` | list | ["Britain", "Prussia", "Austria", "Saxony"] | AI-controlled nations |
| `nation_actions` | dict | {} | Actions per nation |
| `diplomatic_states` | dict | {} | Bilateral diplomatic state per nation-pair. Keys alphabetically sorted ("Austria\|Britain"). Values: WAR, PEACE, NON_AGGRESSION, OPEN_BORDERS, DEFENSIVE_ALLIANCE, ALLIANCE. Empty dict for legacy saves. |
| `nation_relations` | dict | {} | Bilateral relation score per nation-pair (-100 to +100). Same key format as diplomatic_states. Empty dict for legacy saves. |
| `diplomats` | dict | (5 starting) | DiplomaticRepresentative per nation. Keys: nation name. Values: {name, nation, personality, skill, trust, biography}. Empty dict → creates defaults. |
| `diplomatic_points` | int | 4 | Player's diplomatic points (non-accumulating, reset each turn). |
| `max_diplomatic_points` | int | 5 | Maximum DP per turn. |
| `nation_authority` | dict | {each: 60} | AI nation authority levels (0-100). Affects DP generation. |
| `war_scores` | dict | {} | War score per active war. Keys: "NationA\|NationB". Values: -100 to +100 (positive = first nation winning). |
| `battle_records` | dict | {} | Battle records per war for war score. Keys: diplo_key. Values: list of {turn, winner, attacker, defender, casualties}. |
| `decisive_battles` | dict | {} | Decisive battle records (max 2 per war). Keys: diplo_key. Values: list of {turn, winner, total_casualties, ratio}. |
| `battle_counts` | dict | {} | **W6-2 Dynamic Battle Naming.** Region → count of NAMED field battles fought there ("Battle of X" → "Second Battle of X" → …). Garrison assaults/bombardments never increment. `compose_battle_name` is the single writer. |
| `muster_hint_shown` | bool | false | **W6-4.** First-use standing-orders tutorial line on the muster preview — latch-on-surface (set the first time a muster block renders, even if that attack is then cancelled). |
| `armistice_cooldowns` | dict | {} | Turns remaining before same pair can re-enter armistice. Keys: diplo_key. Values: int (decrements each turn). |
| `armistice_turns` | dict | {} | **Phase 2A.** Turns elapsed in current armistice per pair. Keys: diplo_key. Values: int (0-5). After 5 turns, armistice expires to PEACE (or WAR if relation < -60). Cleared on expiration or when pair leaves ARMISTICE state. |
| `nation_dp` | dict | {} | **Phase 2A.** AI nation diplomatic points per turn. Keys: nation name. Values: int. Stored during DP regeneration. Player DP uses `diplomatic_points` field. |
| `previous_treaties` | dict | {} | Past treaty records per pair for escalating harshness. Empty for now. |
| `turns_below_threshold` | dict | {} | Auto-downgrade tracking: consecutive turns relation is 30+ below state threshold. |
| `pending_diplomatic_dialogue` | dict/null | null | **Session 3.** Active Talleyrand dialogue awaiting player response. Contains type, target_nation, options, context. |
| `pending_dialogue_queue` | list[dict] | [] | **V2-89.** Queue of dialogues generated during advance_turn. Popped to pending_diplomatic_dialogue by priority: `commitment_paradox` > `vassal_rebellion` > `sabotage` > `ai_proposal` (legacy `alliance_paradox` loads as `commitment_paradox`). **Session 2 follow-up:** Mailbox items now carry `mailbox_id`, `mailbox_order`, `mailbox_priority` metadata. `next_mailbox_id` (int, default 1) tracks the monotonic ID sequence. Legacy items without `mailbox_id` are auto-stamped on load. **W6-0 (BUG-CA-7):** every dialogue is stamped with a `dialogue_id` (monotonic identity, mirrored onto `popup_payload`); `next_dialogue_id` (int, default 1) serializes on the dialogue manager. Legacy dialogues without `dialogue_id` are auto-stamped on load. Responses carrying a `dialogue_id` that no longer matches the current top are refused (`stale_dialogue`). |
| `active_diplomatic_mission` | dict/null | null | **Session 3.** Talleyrand's ongoing mission: {type, target, turns_active, paused, paused_turns}. UNDERMINE_ALLIANCE adds `target_ally`. |
| `intel_grants` | dict | {} | **BF4.** Temporary intel grants from GATHER_INTEL: {region_name: expiry_turn}. Prevents decay while active. |
| `talleyrand_state` | str | "IDLE" | **Session 3.** "IDLE", "IN_TRANSIT", or "ON_MISSION". |
| `proposal_in_transit` | dict/null | null | **Session 3.** Proposal sent and awaiting resolution next turn: {target, proposal, turn_sent}. |
| `player_proposal_cooldowns` | dict | {} | **Session 3.** Cooldowns per nation (3 turns) and per type (5 turns) after rejection. |
| `active_treaties` | dict | {} | **Session 3.** Active treaties keyed by diplo pair key. Contains nations, type, clauses, turn_signed, harshness. |
| `ai_proposal_cooldowns` | dict | {} | **Session 4.** AI proposal cooldown timers. Keys: "nation\|nation" or "nation\|type". Values: int (turns remaining). Prevents AI from spamming proposals to the same target or of the same type. |
| `diplomatic_queue` | ~~list~~ | ~~[]~~ | **REMOVED (Session 2 follow-up).** Legacy saves with this field are auto-migrated: items delivered into `dialogue_manager` on load. All pending diplomacy now lives in `dialogue_manager.queue` with `mailbox_id`, `mailbox_order`, `mailbox_priority` metadata. |
| `proactive_suggestion_cooldowns` | dict | {} | **Session 4.** Proactive suggestion cooldowns. Keys: "nation\|trigger_type". Values: int (turns remaining). Prevents repeated advisory suggestions for the same diplomatic opportunity. |
| `ai_stalemate_counters` | dict | {} | **Session 4.** Consecutive stalemate turns per nation. Keys: nation name. Values: int (turn count). Used by AI to detect prolonged wars and trigger peace proposals. |
| `ai_proposal_metadata` | dict | {} | **R126.** Tracks war_score at time of last AI proposal per nation. Keys: nation name. Values: {war_score_at_proposal: int, turn: int}. Used for urgent re-proposal detection (bypasses nation cooldown when war score drops 20+). |
| `previous_war_scores` | dict | {} | **Audit 4.** End-of-turn war score snapshot. Keys: diplo key ("Nation1\|Nation2"). Values: int. Used by Talleyrand Trigger 2 to compute per-turn delta. Snapshotted at end of advance_turn(). |
| `war_score_history` | dict[str,list[int]] | {} | **BPH-B.** Last three end-of-turn war score snapshots per active war. Keys: diplo key. Values use canonical storage perspective (positive = first nation winning). Used by peace preview trend arrows. |
| `previous_nation_relations` | dict[str,int] | {} | Snapshot of nation_relations from previous turn for Trigger 4 threshold crossing detection |
| `relation_history` | dict | {} | **N7 Diplo Screen.** Relation trend history (last 3 snapshots). Keys: diplo key ("Nation1\|Nation2"). Values: list of int. Snapshotted at start of advance_turn() before diplomatic processing. Used for trend arrows in diplomatic ledger. |
| `vassals` | dict | {} | **Session 5.** Vassal state per nation. Keys: nation name. Values: {lord, loyalty, autonomy (0=puppet/1=satellite/2=autonomous), path (treaty/conquest), created_turn, tribute_rate, carved_from, regions}. **VS-3 (July 16, 2026) adds two OPTIONAL nested keys** riding the wholesale row copy: `granted_regions` (list[str] — provenance for reclaim-on-rebellion; cleared on VS-5 transfer) and `grant_cooldown` (int, popped at 0). Old saves lack them (`.get()` reads); the serialization-enforcement suite cannot see inside plain dicts, so the round-trip is pinned in `test_vassal_land_grant.py::TestSerialization`. |
| `vassal_investment_cooldowns` | dict | {} | **Session 5.** Investment cooldown per vassal. Keys: nation name. Values: int (turns remaining). 3-turn cooldown after invest_in_vassal(). |
| `vassal_release_cooldowns` | dict | {} | **Phase 3 R14.** Release cooldown per nation. Keys: nation name. Values: int (turns remaining). 5-turn cooldown after release_vassal() — blocks treaty re-vassalization. |
| `cascade_triggered` | list→set | [] | **Session 5.** Defection cascade keys already fired. Serialized as list, deserialized to set. Each key: "vassal\|diplo_key". Prevents cascade from firing twice per war. |
| `continental_system_members` | list | [] | **Session 5.** Nations participating in the Continental System. PUPPET/SATELLITE vassals auto-join if lord is a member. Members lose trade income with Britain. |
| `talleyrand_defiance_cooldown` | int | 0 | **Session 6.** Turns remaining on Talleyrand defiance cooldown. Blocks new sabotage when > 0. Decremented in advance_turn(). Set to 5 on confrontation. |
| `pending_talleyrand_sabotage` | dict\|null | null | **Session 6.** Active sabotage record. Keys: original_proposal, modified_proposal, defiance_type, discovery_chance, turns_hidden, discovered, target_nation. Cleared after confrontation resolution. |
| `talleyrand_override_history` | list | [] | **Session 6.** Last 5 override records. Each: {proposal_type, override_result ("good"/"bad"), turn}. Used by dispatch honesty note ("pessimistic"/"prescient"). Capped at 5 entries. |
| `threat_level` | int | 0 | **Session 7.** Coalition threat level (0-100 clamped). Accumulates from aggressive player actions (battles +3, decisive +5, capital +15, war declaration +20, vassalization +5/+25, annexation +8/region). Decays per turn. |
| `threat_sources_this_turn` | list | [] | **Session 7.** Per-turn threat source log. Each entry: {source: str, amount: int}. Cleared at turn start. Used by dispatch for threat breakdown. |
| `active_coalition` | dict\|null | null | **Session 7.** Active coalition state. Keys: name, members (list), leader, strategic_posture, formed_turn, war_exhaustion (per-member). null = no active coalition. |
| `coalition_brewing` | dict\|null | null | **Session 7.** Brewing coalition state. Keys: qualifying_nations, turns_remaining (3→0 countdown), started_turn. null = not brewing. |
| `coalition_cooldown` | int | 0 | **Session 7.** Post-dissolution cooldown (5 turns). Prevents new coalition formation while > 0. Decremented in process_coalition_turn(). |
| `coalition_count` | int | 0 | **Session 7.** Total coalitions formed this game. Used for naming ("First Coalition", "Second Coalition", etc.). |
| `war_exhaustion` | dict | {} | **Session 7.** War exhaustion per nation, intentionally shared across simultaneous wars in v0.1. Keys: nation name. Values: int 0-200. +casualties//1000 per battle (cap 20), +8/turn at war, -5/turn at peace. Affects coalition loyalty penalty and pending common-peace acceptance. |
| `we_dispatched_thresholds` | dict | {} | **Session 5 audit.** Highest WE threshold dispatched per nation. Keys: nation name. Values: int (20/40/60/80). Prevents double-firing of WE threshold dispatch events. Cleared on coalition dissolution. |
| `war_start_turns` | Dict[str, int] | {} | **R142.** diplo_key → turn war began (R142 war weariness tracking). Cleared by `cleanup_war_end()`. |
| `casus_belli` | dict | {} | **Phase 4.** Casus belli flags per nation-pair. Keys: diplo_key ("Nation1\|Nation2"). Values: bool. Set true when ultimatum rejected — halves war declaration relation penalties. |
| `ultimatum_global_cooldown` | int | 0 | **PL-14 Session 12.** Global ultimatum cooldown (replaces per-target dict). Blocks all ultimatums while > 0. Starts at 5 on use, decremented in `advance_turn()`. Migration: if old `ultimatum_cooldowns` dict exists and new field absent, takes `max()` of old dict values. |
| `diplomatic_reliability` | dict | {} | **Memory and Pressure v2.4.3.** Diplomatic reliability score per nation. Keys: nation name. Values: int. Read as a light global reputation scalar (`// 10`, capped `-6..+6`) rather than a per-pair ledger. Legacy v1.0 saves may still carry diplo-keyed values; load-side migration normalizes them to the nation-keyed shape. |
| `betrayal_history` | dict | {} | **Memory and Pressure.** Directional `actor|victim` betrayal memory store tracking active strikes, grievance flags, witness scoping, and episode lineage. Do not sort these keys; they are distinct from sorted diplomatic pair keys. Values: structured per-pair history records. Per-pair shape: `{strikes: list[StrikeRecord], grievance_flags: list[GrievanceFlag], categories: list[str], last_turn: int}`. **B-B4 §8.8.4** adds `grievance_flags` to the canonical record shape (durable victim-grade flags; do NOT decay under §8.6 passive rules; cleared only via Make Amends grievance variant). Each grievance flag: `{grievance_type: str, episode_id: str, turn: int, source_episode_type: str}`. Pre-B-B4 saves load with `grievance_flags: []` defaulted. |
| `next_episode_id` | int | 1 | **Memory and Pressure.** Monotonic allocator for commitment / betrayal episode lineage. Missing-field default is `1`. |
| `diplomatic_history` | list | [] | **Phase 4.** Diplomatic event log (max 20 entries). Each entry: `{type, from_nation, to_nation, turn, details?}`. Types: "proposal", "war_declaration", "treaty_break", "ultimatum_accepted", "ultimatum_rejected". Displayed in Talleyrand tab. |
| `commitment_paradox_popup` | dict\|null | null | **Memory and Pressure v2.4.3.** Pending paradox popup for the renamed `commitment_paradox` hard stop. Legacy `alliance_paradox_popup` remains accepted on load and is migrated to this canonical field. |
| `peace_ratification_log` | list | [] | **Peace Deals BPH-D (landed).** Last 5 peace ratification summaries. Each entry: `{target_nation, previous_state, new_state, turn, war_duration_turns, war_outcome, territory_gained, territory_lost, gold_received, gold_paid, casualties_france, casualties_enemy, final_war_score, terms_ratified, political_aftermath, target_capital}`. Capped at 5 entries. Pre-BPH-D saves load with `[]` defaulted. |
| `war_objectives` | dict | {} | **Peace Deals WPS-A (landed).** Diplo-key → nation → objective record. Each record: `{type, declaring_nation, target_nation, target_regions, accumulated_ticking, created_turn, ticking_active, objective_met_turn, concluded_turn?}`. Types: conquest/subjugation/forced_alliance/defense/liberation. Liberation adds `vassal_nations`. Ticking caps at 25. Pre-WPS-A saves load with `{}` defaulted. |
| `alliance_origins` | dict | {} | **Peace Deals WPS-C (landed).** Diplo-key → `"forced"` or `"voluntary"`. Set on treaty ratification containing a `forced_alliance` clause; cleared when the diplomatic state drops below ALLIANCE, enters WAR, or becomes VASSAL. Drives the -10/turn forced-alliance relation drift in `process_diplomacy_turn` step 12a. Pre-WPS-C saves load with `{}` defaulted. |
| `diplomatic_commitments` | dict | {} | **Peace Deals WB-A (landed).** Stringified commitment-id → war bargain record dict. Each record carries `id`, `type`, `promiser`, `beneficiary`, `target_enemy`, `entry_term`, `claim_term`, `status`, `source_pair`, `cooldown_key`, lifecycle timestamps, and terminal-state fields. **Imperial Settlement Slice A3 (landed)** adds three war-instance snapshot fields populated by `create_war_bargain_commitment` when an active war_instance covers the (promiser, target_enemy) pair: `war_id` (rewritten on merge to point to the surviving instance via `_rewrite_absorbed_war_id_in_bargains`), `side_at_creation` (`"attackers"` / `"defenders"` / `None`; **PRESERVED through merges** per spec §11.3 line 1573), and `side_leader_at_creation` (nation name at bargain birth; **also preserved through merges**). Pre-A3 records default those fields to `None` via `dict.get()` semantics — no migration needed. Pre-WB-A saves load with `{}` defaulted. |
| `archived_diplomatic_commitments` | list | [] | **Peace Deals WB scale hardening (landed).** Terminal war bargain records moved out of `diplomatic_commitments` after a 10-turn grace period. Each archive entry preserves the bargain record and adds `archived_turn` plus `archived_commitment_id`. Pre-hardening saves load with `[]` defaulted. |
| `next_commitment_id` | int | 1 | **Peace Deals WB-A (landed).** Monotonic commitment-id allocator. Pre-WB-A saves load with `1` defaulted. |
| `next_join_opportunity_id` | int | 1 | **Peace Deals WB-C (landed).** Monotonic join-opportunity-id allocator. Pre-WB-C saves load with `1` defaulted. |
| `war_entry_reroll_memory` | dict | {} | **Peace Deals WB-C (landed).** Reroll-key (`"{beneficiary}\|{named_enemy}\|{request_type}\|{turn}"`) -> `{score_inputs_hash, counter_bargain}` for deterministic counter-bargain reroll. Cleared when the score-input hash changes between evaluations. Pre-WB-C saves load with `{}` defaulted. |
| `pending_ally_entry_opportunities` | list[dict] | [] | **Peace Deals WB-C (landed).** Queue of unresolved ally-entry join opportunities surfaced by `build_declaration_preview()`. Each carries `id`, `beneficiary`, `named_enemy`, `request_type`, `promiser`, `origin_episode_id`, nested `war_entry_score`, `hard_blocks`, and optional `counter_bargain` for the 25-49 band. Consumed by the ally-entry review flow or `resolve_join_opportunity()`. Pre-WB-C saves load with `[]` defaulted. |
| `next_war_instance_id` | int | 1 | **Imperial Settlement Slice A1 (landed).** Monotonic allocator for `war_id = f"war_{n}"` per `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §7.2. A2 declaration / cascade / direct-entry seams call `_allocate_war_id` and increment this counter; never derive ids from turn / sides / `diplo_key`. Pre-A1 saves load with `1` defaulted. |
| `war_instances` | dict | {} | **Imperial Settlement Slices A1 + A2 + A3 (landed).** Active war-level container records keyed by `war_id` per spec §7.1. Each record carries `created_turn`, `created_sequence`, `originator`, `origin_target`, `origin_diplo_key`, `objective_keys`, `active_diplo_keys`, `resolved_diplo_keys`, `diplo_key_meta` (per-pair `pair_status` of `war`/`armistice`/`resolved`), side leaders + `leader_source_by_side`, `attackers`/`defenders`/`side_by_nation`, `active_participants` + `participant_meta`, `separate_peaced`, `war_bargains`, and terminal `ended_turn`/`end_reason`. A2 wires every WAR seam to allocate / reuse via `ensure_war_instance_for_pair`. **A3** owns the transitive merge transaction (`merge_war_instances` consolidates connected components, picks oldest `created_sequence` as survivor, unions participant/pair/episode/objective_keys data, runs side-scoped leader replacement, rewrites absorbed `war_id` on `diplomatic_commitments` + `pending_dispatch_events`, and asserts `assert_war_instance_invariants(..., context="post_merge")` always-on). A3 also stamps `participant_meta[nation].exited_turn` + `exit_path = "eliminated"` on elimination via `mark_participant_eliminated_in_all_wars`, and stamps `ended_turn` + `end_reason = "all_pairs_resolved"` when the last active pair resolves. Transient `war_instances_by_leader` / `war_instances_by_participant` indexes are NOT serialized; they are rebuilt lazily after load via `invalidate_war_instance_indexes()` + dirty-flag rebuild. Pre-A1 saves load with `{}` defaulted. |
| `archived_war_instances` | list[dict] | [] | **Imperial Settlement Slices A1 + A3 (landed).** Terminal `war_instance` records moved out of `war_instances` after the §7.5 10-turn retention window (`ARCHIVE_RETENTION_TURNS = 10`). A3 wires the active→archived transition: `archive_terminal_war_instances(world)` runs once per turn at the start of `_advance_turn_internal`, deep-copying every `(current_turn - ended_turn) >= 10` instance into this list and removing it from active `war_instances`. Each archived entry preserves the original record (including `ended_turn` / `end_reason`). Archived `war_id`s remain valid references for ledger / log readers; the post-merge invariant treats them as resolved (not absorbed). Pre-A1 saves load with `[]` defaulted. |
| `reparations_cooldown` | dict | {} | **Memory and Pressure v2.4.3 (B-B7 — landed).** Pair-key (sorted `"A\|B"`) -> turn number at which Make Amends (spec §8.6.1) is next available for that pair. Absent / `0` = immediately available. Shared cooldown across the standard variant (live) and the grievance variant that ships with B-B4. |
| `anti_renewal_cooldown` | dict | {} | **Memory and Pressure v2.4.3 (B-B4 — landed).** Pair-key (sorted `"A\|B"`) -> turn number at which new ALLIANCE / DEFENSIVE_ALLIANCE ratification is available again for that pair after a `call_to_arms_refused_defensive` episode per spec §8.8.7. Absent / `0` = no block. Default authored window is 15 turns. Gated by `diplomacy.is_anti_renewal_active` in `calculate_acceptance`; NON_AGGRESSION / OPEN_BORDERS / PEACE proposals are unaffected. Pre-B-B4 saves load with `{}` defaulted. |
| `oathbreaker_posture` | dict | {} | **Memory and Pressure v2.4.3 (DG-4 completion audit - landed).** Nation-keyed posture store for repeated defensive-call refusals. Each record tracks posture start/expiry, refusal count, and source episode lineage. Active records mechanically block incoming ALLIANCE / DEFENSIVE_ALLIANCE acceptance through `diplomacy.is_oathbreaker_auto_reject_active`; missing or expired records behave as `{}`. Pre-DG-4-completion saves load with `{}` defaulted. |
| `call_to_arms_loyalty_bonds` | dict | {} | **Memory and Pressure v2.4.3 (DG-4 completion audit - landed).** Nation-keyed list of costly-honor loyalty-bond records emitted by `call_to_arms_honored_costly`. Records preserve honorer, ally, turn, episode id, relation bonus, and expiry metadata for future UI/AI consumption. Pre-DG-4-completion saves load with `{}` defaulted. |
| `cascade_profile` | dict | direct-only DG-4 defaults | **Scale Readiness DG-4 amendment (landed).** Authored direct-only cascade settings consumed by call-to-arms resolution and DG-4 severity/cooldown helpers. Includes `mode`, `qualifying_treaty_states`, `include_vassals`, event-family names, `impossibility_threshold`, `defensive_refusal_severity_multiplier`, `oathbreaker_posture`, and `anti_renewal_window_turns`. Missing saves load with the default direct-only profile. |
| `coalition_popup` | dict\|null | null | **Session 8A.** Pending coalition popup data for Godot frontend. Set by coalition formation, cleared after read in /command response. |
| `diplomatic_sabotage_popup` | dict\|null | null | **Session 8A.** Pending Talleyrand sabotage popup data. Set by sabotage discovery, cleared after read in /command response. |
| `vassal_rebellion_imminent_popup` | dict\|null | null | **Session 8A.** Current vassal rebellion warning popup (popped from list). Set by loyalty check, cleared after read in /command response. |
| `vassal_rebellion_imminent_popups` | list[dict] | [] | **V2-90.** Queue of vassal rebellion popups. Multiple vassals can trigger simultaneously. Auto-pops to singular field in _include_popup_passthroughs. |
| `talleyrand_redemption_popup` | dict\|null | null | **Session 8C.** Pending Talleyrand redemption popup. Set by trust<=20 check, cleared after read in /command response. |
| `diplomatic_objection_popup` | dict\|null | null | **Session 8C.** Pending diplomatic objection popup. Set by pre-proposal objection, cleared after read in /command response. |
| `incoming_proposal_popup` | dict\|null | null | **Session 8C.** Pending AI proposal popup data. Set by deliver_ai_proposal, cleared after read in /command response. |
| `diplomatic_trust_applied` | dict | {} | **V2-16.** Per-turn cap tracking for diplomatic trust changes. {marshal_name: amount_applied}. Cleared at start of each turn. Replaces dynamic attrs that didn't survive save/load. |
| `last_advanced_turn` | int | 0 | **R20.** Idempotency guard for advance_turn(). Stores the pre-increment turn number of the last successful advance_turn call. Prevents double-processing (double income/attrition) on retry after crash. |
| `ai_stagnation_turns` | dict | {} | **Enemy AI.** Per-marshal stagnation counter. Keys: marshal name. Values: int (consecutive turns with no action). At 2+, AI forces aggressive fallback. Decrements on action taken. |
| `ai_attack_futility` | dict | {} | **Enemy AI.** Per-target-pair attack futility counter. Keys: "attacker\|defender". Values: int (consecutive failed attacks). At 2, AI avoids that target. Decays per turn. |
| `last_redemption_turn` | int | 0 | **Diplomatic defiance.** Turn when last Talleyrand redemption event fired. 5-turn cooldown between redemption events. |
| `active_battles` | dict | {} | Currently ongoing battles |
| `battle_history` | list | [] | Completed battle records |
| `battles_this_turn` | list | [] | Battles this turn (Phase 5.2) |
| `base_nation_actions` | dict | world-scoped | **EC-0.** Per-nation BASE action points, snapshotted at construction (`build_europe_nation_actions`/`build_default_nation_actions` or a scenario's own `nation_actions`). `advance_turn` resets `nation_actions` from this each turn before treaty AP clauses apply. from_dict defaults to the loaded `nation_actions` when absent (pre-fix saves / fresh scenarios). |
| `command_history` | list | [] | Last 50 parsed commands (sliding window). Each entry: `{raw_input, marshal, action, target, turn}`. Recorded in BOTH mock and live modes (CR-4). Feeds the live LLM repetition prompt AND CR-4 context carryover ("again"/"same target"/"him"/"there"/"not you, X"). `target` added CR-4. Round-trips as a shallow dict-copy list — no per-field schema enforcement. |
| `event_log` | list | [] | Structured game event history. Each entry is a dict with `type`, `turn`, and event-specific fields. Accumulates across full game, never cleared. Used by Campaign Log, Gazette. DG-4 `call_to_arms_refused_defensive` entries may include `coalition_threat_partners_at_refusal` and `severity_factors`; these are event payload fields, not separate top-level save keys. Future Ally Participation `settlement_summary` entries store one common-peace log record with `war_id`, `terms_summary`, and structured `participant_reactions`, not one event per participant. |
| `notifications` | list | [] | Pending notification alerts. Each entry: `{id, type, priority, title, message, turn_created, details}`. Persists until player dismisses. Serialized via `NotificationCollector.to_list()/from_list()`. Commitments notices carry §8.1 routing metadata in `details` (`template_key`, `icon`, `label`, `speaker`, `review_target`, `review_label`). |
| `last_bankruptcy_notification_tier` | int | 0 | Last bankruptcy tier for which a notification was fired (0-3). Prevents per-turn spam. Resets to 0 when bankruptcy ends. |
| `eliminated_nations_notified` | list | [] | Nation names already notified as eliminated. Prevents per-turn spam. Serialized as list, deserialized to set. |
| `last_morning_dispatch` | dict | {} | Last morning dispatch dict for dispatch re-read screen (Session A). Stored by `build_morning_dispatch()`. Contains turn, situation, marshals, intelligence, turn_events, berthier_note, diplomatic_events. All primitives, no circular refs. |
| `pending_dispatch_events` | list | [] | **Session 8D.** Queue of diplomatic dispatch events awaiting delivery. Each entry: `{type, template_vars, fog_rule}`. Cleared at start of `advance_turn()`, consumed by `build_morning_dispatch()`. DG-4 witness rows retain individual `episode_id` entries in this substrate; presentation collapses same-episode witness rows when building dispatch output. |
| `coordination_tutorial_shown` | bool | false | Whether the first-time coordination tutorial has been shown (Session 66). Set to true after first player combined arms attack. |
| `delegation_hint_shown` | bool | false | CR-5 (§6.7): whether the once-per-campaign delegation discoverability hint has fired. Set true the first time the player issues a delegation verb ("deal with X"). |
| `nation_starting_regions` | Dict[str, list] | {} | Starting regions per nation at game start, used by AI homeland defense. Key: nation name, Value: list of region names. Empty dict for legacy saves. |
| `intel` | dict | {} | Map of region_name -> RegionIntel. Fog of war intel store. Empty dict for backward compat (old saves populate via `calculate_visibility()` on load). |

### Pending Imperial Settlement WorldState Fields

These fields are specified for `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.21 but are not live until their implementation slices land. They should be added to `WorldState.to_dict()` / `WorldState.from_dict()` with the listed defaults in the owning slice. Slice A1 owns `next_war_instance_id`, `war_instances`, and `archived_war_instances` as part of the foundation gate before any behavioral settlement work starts.

| Field | Type | Default | Owning slice |
|-------|------|---------|--------------|
| `next_war_instance_id` | int | 1 | Slice A: monotonic war-instance allocator; `war_id = "war_{next_war_instance_id}"`, stored as `created_sequence`, then incremented. |
| `war_instances` | dict | {} | Slice A: active/recent political war containers keyed by `war_id`, grouping existing pairwise war state through pair keys, leaders, participant episodes, objective references, and terminal metadata. |
| `archived_war_instances` | list[dict] | [] | Slice A: compact terminal war records moved out of `war_instances` after the 10-turn live retention window. |
| `war_contribution_scores` | dict | {} | **Slice B1 + B2 + B3 (landed).** Episode-scoped contribution store keyed by `war_id` then by nation. Each per-nation record carries `current_episode_id`, `episodes` (dict of `episode_id` → `{joined_turn, exited_turn, battle, occupation, staying_power, support, total}` plus B3 staying-power counters `staying_power_credited_turns`, `last_staying_power_turn`), `historical_total`, plus B2 emitter dedupe state: `seen_occupation_event_ids: list[str]`, `seen_support_event_ids: list[str]`, and `support_caps: {access: int, supply: int}` (per-`(war_id, supporter, support_kind)` raw cap of 5 per spec §9.2 line 674; re-entry into the same `war_id` does not reset the cap). Episode ids follow the canonical `{nation}_{war_sequence}_{episode_index}` form. B1 ships the data shape, episode helpers, share/standing math, the §9.6 old-record adapter, and the §8.2 standing classifier. B2 ships `accrue_battle_contribution` (called BEFORE the 1000-casualty war-score gate), `detect_battle_theater` (one-hop adjacency), `accrue_occupation_event` + `emit_capture_occupation_event` (enemy_region_captured 20 / enemy_capital_captured 40 / allied_region_restored 15 / liberated_region_restored 15 / treaty_transfer 0), `accrue_support_event` (gold|subsidy //100, ap *5, manpower //500, access|supply 1/turn capped at 5) with episode-id dedupe, plus `resolve_british_subsidy_war_id` (deterministic war attribution: unique_eligible / matching_coalition_target / highest_overlap / oldest_sequence / unattributed_subsidy). Wired call sites: `world_state.capture_region` (occupation), `world_state._ratify_treaty` (gold_lump support + territory_cede `allied_region_restored` + liberation `liberated_region_restored`), `world_state._process_treaty_clauses` (per-turn gold/manpower/AP), `coalition._process_british_subsidy` (subsidy). B3 wires `_open_contribution_episode_for_participant` / `_close_contribution_episode_for_participant` into every WAR-entry / exit seam in `settlement_helpers.py`, adds `accrue_staying_power_for_war` / `accrue_staying_power_all_wars` (+5/turn capped at 10 turns / 50 raw, idempotent per `(war_id, nation, current_turn)`) wired as step 7b in `process_diplomacy_turn`, and routes `cleanup_war_end(conclude_objectives=True)` through `resolve_pair_to_resolved` so PEACE outcomes close the contribution episode. Pre-B1 saves load with `{}` defaulted; pre-B2 saves load without the new dedupe / cap fields and they default empty on first emission; pre-B3 saves load without `staying_power_credited_turns` / `last_staying_power_turn` and the per-turn helper sets them on first invocation. |
| `archived_war_contribution_scores` | dict | {} | **Slice B3 (landed).** Compact per-nation totals from `war_contribution_scores[war_id]` once the owning `war_instance` clears the 10-turn retention window in `archive_terminal_war_instances`. Keyed by `war_id`; each entry carries `archived_turn` and `per_nation_totals[nation]` with `battle`, `occupation`, `staying_power`, `support`, `material_total`, `total`, `episode_count`, `first_joined_turn`, `last_exited_turn`, and `historical_total`. Episode detail is intentionally dropped (spec §9.5 line 178). Pre-B3 saves load with `{}` defaulted. |
| `ai_settlement_cooldowns` | dict[str, int] | {} | Slice C2 + SC-5 reversal: common-peace AI anti-spam cooldowns AND the AI settlement-offer producer per-`war_id` cooldown (next-allowed turn). After SC-5 commit 1 (`2a1f9d7`) the producer in `ai_diplomacy.process_settlement_offer_phase` writes `cooldowns[war_id] = current_turn + SETTLEMENT_OFFER_COOLDOWN_TURNS` after each offer; survives save/load so cooldowns persist across sessions. Separate from bilateral proposal cooldown namespaces. |
| `settlement_terms_requests` | dict[str, dict] | {} | **SC-30 / Slice G1 (landed July 2, 2026).** The Request Terms lifecycle store, keyed by `war_id`. Each entry: `{"status": "requested"|"granted"|"refused", "requested_turn": int, "resolved_turn": int|null, "resolve_reason": "" | "terms_granted" | "offer_already_available" | "winning_side_refuses" | "war_changed", "cooldown_until_turn": int, "answering_leader": str}`. Written by `DiplomaticExecutor._execute_request_terms` (1 DP); resolved each AI phase by `ai_diplomacy._resolve_settlement_terms_requests` — a GRANT emits a real `incoming_settlement_offer` tagged `requested_by_player: true` through the shared producer emission and writes BOTH cooldowns; a court refusal (`get_war_score_for(answering_leader, player) >= REQUEST_TERMS_REFUSAL_WAR_SCORE`) voices through `settlement_request_terms_refused_court` and quiets the periodic producer for the same window. Pre-G1 saves load with `{}` defaulted. |
| `ally_petition_state` | dict[str, dict] | {} | **Slice H (landed July 3, 2026).** Ally petition resolution state, keyed by `f"{war_id}|{ally}"`. Each entry: `{"last_petition_turn": int, "cooldown_until_turn": int, "declined_types": [str], "granted_types": [str]}`. Written by the `settlement_offers` Slice H handlers (`grant_ally_petition_clause` / `decline_ally_petition` / `honor_bargain_in_settlement` — any resolution stamps the 5-turn `ALLY_PETITION_COOLDOWN_TURNS` absolute cooldown; queueing stamps `last_petition_turn` only); read by the Slice H petition finders' cooldown gate. Decline memories ride the existing `settlement_memories` store (`memory_type="petition_declined"`, expiring) — no parallel store. Pre-Slice-H saves default to `{}`. |
| `pending_settlement_dialogues` | list[dict] | [] | Slice C2 + SC-5 reversal commit 1/2: settlement-owned producer staging list for `incoming_settlement_offer` entries written by `ai_diplomacy.process_settlement_offer_phase` and for legacy locked `settlement_confirm` payloads. After SC-5 commit 2 (May 17, 2026) the `promote_pending_settlement_offers(world)` helper drains `incoming_settlement_offer` entries into the dialogue_manager mailbox queue (idempotent across save/load); the drain runs once per turn after the producer, and once per `/mailbox` / `/pending_envoy` / `/mailbox/activate` request so save-loaded saves drain cleanly. Each `incoming_settlement_offer` entry carries `offer_id` (stable `settlement_offer:{war_id}:{turn}:{seq}`), `war_id`, `proposer_nation`, `proposer_side`, `accepting_side`, `accepting_leader`, `covered_enemy_participants`, `settlement_terms`, and `turn_created`. |
| `pending_settlement_drafts` | *(removed — CH-3, June 10, 2026)* | — | **Deleted field.** The legacy war_id-keyed draft store is gone; `pending_settlement_drafts_by_key` is the ONE draft store. `from_dict` migrates an old save that carries a draft ONLY under this key into the scoped store (keyed `compute_settlement_draft_key(war_id, None, [])`, which the war-prefix reopen fallback restores), then ignores the key. New saves never write it. |
| `pending_settlement_drafts_by_key` | dict[str, list[dict]] | {} | **SC-5R-1 scoped draft store; PF-2 made it the reopen store; CH-3 (June 10, 2026) made it the ONE draft store — the legacy `pending_settlement_drafts` is deleted everywhere (writers, end-turn discard notices, war-merge re-key, ratify/back-out cleanup).** Authored settlement draft clauses keyed by `compute_settlement_draft_key(war_id, selected_target_nation, covered_enemy_participants)` (`settlement_draft:{war_id}:{selected}:{scope_hash}`). Written by `save_scoped_settlement_draft` on every restage/suspend; read by `load_scoped_settlement_draft` with the PF-2 fallback chain (exact key → `(war, target)` prefix → war prefix, most recent wins). End-turn discard notices (SC-28) now derive from this store (one notice per war, the most recently saved entry — the draft a reopen would have restored). War-instance merge re-keys absorbed-war entries to the surviving war id (survivor wins on exact-key collision). Clauses are the canonical settlement clause dicts; **GT-Slice-1 (Guided Terms §3.5, landed June 10, 2026) adds the optional `authored_by` clause field** (`"player"` = hand-authored via the guided demand verbs or hand-set magnitude; absent = Talleyrand-suggested baseline/seed) — registered as an optional key on every `CANONICAL_CLAUSE_TYPES` entry, it rides these plain-dict stores and the staged dialogue payload through save/load unchanged and drives the §3.5 dial-protection rule. Old saves default to `{}`; untagged clauses keep full legacy dial semantics. |
| `pending_settlement_draft_notices` | list[dict] | [] | **Settlement UI Cleanup SC-28 / G2-Slice-6 (landed).** One-shot player notices for non-empty settlement drafts discarded at end turn. Each entry carries `war_id`, `turn_discarded`, `draft_clause_count`, `selected_target_nation`, and `message_display`; notices survive save/load until `build_base_response` drains them once through `drain_settlement_draft_notices()`, then clear. They never restore a discarded draft or permit ratification from stale data. Old saves default to `[]`. |
| `settlement_route_seq` | dict[str, dict[int, int]] | {} | **Settlement UI Cleanup G2-Slice-3 SC-14c (landed).** Per-`war_id`, per-turn settlement route sequence used to produce stable `settlement:{war_id}:{turn}:{seq}` route ids. The staged dialogue mints the id; reaction event, dispatch, ledger, notification meta, and result feedback consume it verbatim. Serialized keys may round-trip through JSON strings and must be normalized back to integer turn keys on load; old saves default to `{}`. |
| `settlement_reopen_attempts` | dict[str, dict[int, int]] | {} | **Settlement UI Cleanup G2-Slice-3 SC-14b (landed).** Per-`(war_id, turn)` reopen attempt counter. Attempts 1..3 may reopen when the target is valid; the next attempt returns `must_reopen=False` with the SC-14b "We cannot reopen this settlement review - choose from war detail" copy. The counter resets at every `world.advance_turn` because a new turn can legitimately change war eligibility, acceptance, participants, or hard stops. Old saves default to `{}`. |
| `recurring_settlement_payments` | list[dict] | [] | **Settlement UI Cleanup G2-Slice-9 SC-33 / DWL-SET-SC33 (landed).** Active recurring `gold_per_turn` obligations ratified through settlement. Each record: `{payment_id: str, from: str, to: str, amount_per_turn: int, turns_remaining: int, total_turns: int, war_id: str, ratified_turn: int, settlement_route_id: str, source_clause_index: int}`. `payment_id` is `f"recurring_gold:{from}:{to}:{ratified_turn}:{seq}"` where `seq` is a per-ratified-turn monotonic counter so multiple obligations created on the same turn remain distinct. Processed once per income phase by `process_recurring_settlement_payments` after vassal tribute and before bankruptcy check: transfers `min(amount_per_turn, payer_balance)` from payer to recipient (never negative), decrements `turns_remaining`, emits `settlement_recurring_gold_paid` / `settlement_recurring_gold_partial` dispatch events as appropriate. On `turns_remaining == 0` the record is removed and a `settlement_recurring_gold_completed` event is queued. Cancellation conditions (record removed, `settlement_recurring_gold_cancelled` event queued): payer eliminated (no active regions outside vassalage; legacy absence from `nation_gold` remains a fallback), payer vassalized (present in `world.vassals`), recipient eliminated, renewed war between payer and recipient (active WAR/ARMISTICE in `diplomatic_states`). Pre-G2-Slice-9 saves default to `[]`. |
| `respected_estates` | list[dict] | [] | **W6-8 The Spoils of War (landed July 10, 2026).** Titles the conqueror chose to HONOR on occupied estate soil. Entries `{region, marshal, nation, respecter}` — `nation` = the estate-holder's nation, `respecter` = the occupying nation that made the choice. A LIVE entry (respecter still controls the region, the estate still on the marshal's `dotation_regions` rolls) keeps the estate out of the ES-7 prune, keeps it counting toward the marshal's satisfaction (`dotation.get_satisfaction`), and grants the respecter a +5 acceptance term with the holder's nation (`dotation.respected_estate_mod`, cap one per nation, consumed in `calculate_acceptance`). Pruned by `dotation.prune_respected_estates` at turn advance. The estate CAPTURE choice itself rides `pending_capture_choice` with `stage: "estate"` plus a `dialogue_id` minted from the dialogue manager's W6-0 counter (`mint_dialogue_id`), so the pending dict and the id counter round-trip together. Pre-W6-8 saves default to `[]`. |
| `settlement_memories` | dict | {} | **Slice D1/D2 (landed).** Per-pair settlement memories keyed by `f"{actor}|{subject}"`, value list of memory dicts `{actor, subject, memory_type, episode_id, turn, expires_on_turn, payload}`. `memory_type` ∈ {`they_chose_us` (durable), `settlement_gratitude` (10-turn transient, refreshable, gates `settlement_gratitude_mod` acceptance hook), `sold_out_by_war_leader` (10-turn transient, refreshable, payload includes burdens / leader / severity_score / relation deltas), `settlement_context` (durable, attaches standing_share / severity / cross_war context for ledger), `settlement_shut_out` (durable mirror of the same-name `betrayal_history.grievance_flags` entry)}. Per-turn pruning runs in `prune_expired_settlement_memories` from `world.advance_turn`; durable records (`expires_on_turn` is `None`) are never auto-pruned. Negative acceptance penalties remain on `betrayal_history[pair]["grievance_flags"]` per spec §14.1 line 1449. |

Reserved future `event_log` payloads:

```json
{
  "type": "settlement_summary",
  "turn": 24,
  "war_id": "war_12",
  "covered_enemy_participants": ["Austria", "Bavaria"],
  "terms_summary": ["territory_cede:Saxony->Prussia"],
  "route_id": "settlement:war_12:24:1",
  "acceptance_at_staging": {"total": 54, "threshold": 50, "band": "near_acceptable"},
  "acceptance_snapshot": {"total": 58, "threshold": 50, "band": "accept"},
  "participant_reactions": [
    {
      "nation": "Prussia",
      "standing_level": "consult",
      "reaction_type": "settlement_gratitude",
      "relation_delta": 5,
      "grievance_type": null
    }
  ],
  "warnings": []
}
```

---

## Marshal Format

```json
{
  "name": "Ney",
  "location": "Belgium",
  "strength": 72000,
  "starting_strength": 72000,
  "personality": "aggressive",
  "nation": "France",
  "spawn_location": "Paris",
  "movement_range": 2,
  "tactical_skill": 8,

  "skills": {
    "tactical": 7,
    "shock": 9,
    "defense": 4,
    "logistics": 5,
    "administration": 4,
    "command": 8
  },

  "ability": {
    "name": "Bravest of the Brave",
    "description": "...",
    "trigger": "when_attacking",
    "effect": "+2 Shock skill when attacking"
  },
  "biography": "The Bravest of the Brave. Charges before his orders are read...",

  "morale": 100,
  "orders_overridden": 0,
  "battles_won": 0,
  "battles_lost": 0,

  "trust": {"value": 75},
  "vindication_score": 0,
  "recent_battles": [],
  "recent_overrides": [],

  "autonomous": false,
  "autonomy_turns": 0,
  "autonomy_reason": "",
  "redemption_pending": false,
  "autonomous_battles_won": 0,
  "autonomous_battles_lost": 0,
  "autonomous_regions_captured": 0,
  "trust_warning_shown": false,

  "dotation_regions": ["Swabia"],
  "expectation_grace_turn": -1,
  "pension": 0,
  "last_expectation_seen": 0,

  "relationships": {"Davout": -2, "Grouchy": 0},

  "co_location_turns": {"Davout": 3},
  "last_relationship_change_turn": {},

  "drilling": false,
  "drilling_locked": false,
  "drill_complete_turn": -1,
  "shock_bonus": 0,
  "strategic_combat_bonus": 0,
  "strategic_defense_bonus": 0,

  "precision_execution_active": false,
  "precision_execution_turns": 0,

  "strategic_order": null,
  "pending_interrupt": null,

  "in_combat_this_turn": false,
  "last_combat_turn": null,
  "last_combat_result": null,
  "last_combat_location": null,

  "fortified": false,
  "defense_bonus": 0.0,

  "retreating": false,
  "retreat_recovery": 0,
  "retreated_this_turn": false,
  "_recovery_destination": null,

  "broken": false,
  "broken_recovery": 0,

  "stance": "neutral",

  "cavalry": true,
  "artillery": false,
  "moved_this_turn": false,
  "turns_in_defensive_stance": 0,
  "turns_fortified": 0,
  "cumulative_fortification_turns": 0,

  "counter_punch_available": false,
  "counter_punch_turns": 0,
  "counter_punch_ready": false,
  "iron_resolve_stacks": 0,

  "holding_position": false,
  "hold_region": "",

  "recklessness": 0,
  "pending_glorious_charge": false,
  "pending_charge_target": "",

  "attacks_this_turn": 0,

  "bombardments_this_turn": 0,

  "idle_turns": 0,

  "last_battle_turn": -1,

  "square_formation": false,

  "occupation_region": null,
  "occupation_turns_held": 0,
  "occupation_turns_required": 0
}
```

### Marshal Fields Reference

#### Core Identity
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Marshal's name |
| `location` | string | Current region name |
| `strength` | int | Current army size |
| `starting_strength` | int | Original army size |
| `personality` | string | "aggressive", "cautious", "literal", "balanced" |
| `nation` | string | "France", "Britain", "Prussia", "Austria", "Saxony" |
| `original_nation` | string/null | Pre-vassalage nation. Cleared on rebellion. (Phase 1 R61) |
| `spawn_location` | string | Capital/respawn region |
| `movement_range` | int | 1 (infantry) or 2 (cavalry) |
| `tactical_skill` | int | Legacy skill rating 0-12 |
| `cavalry` | bool | Whether marshal commands cavalry |
| `artillery` | bool | Whether marshal commands artillery (mutually exclusive with cavalry) |
| `moved_this_turn` | bool | Whether artillery moved this turn (blocks attack, -25% defense) |
| `biography` | string | Marshal biography text for Marshal Management UI |

#### Skills (6-Skill System)
| Skill | Range | Description |
|-------|-------|-------------|
| `tactical` | 1-10 | Combat rolls, flanking bonuses |
| `shock` | 1-10 | Attack damage, pursuit effectiveness |
| `defense` | 1-10 | Defender bonus, retreat casualties |
| `logistics` | 1-10 | Supply range, attrition resistance |
| `administration` | 1-10 | Recruitment speed, desertion prevention |
| `command` | 1-10 | Morale management, discipline |

#### Game State
| Field | Type | Description |
|-------|------|-------------|
| `morale` | int | 0-100, affects combat effectiveness |
| `orders_overridden` | int | Times player insisted over objections |
| `battles_won` | int | Victories counter |
| `battles_lost` | int | Defeats counter |

#### Disobedience System
| Field | Type | Description |
|-------|------|-------------|
| `trust` | dict | {"value": 0-100} Trust object |
| `vindication_score` | int | -5 to +5, affects objection boldness |
| `recent_battles` | list | Last 3 battle results |
| `recent_overrides` | list | Last 5 override events (bool) |
| `last_objection_turn` | int | Turn of last objection (V2b vindication decay timer) |
| `defiance_cooldown_until` | int | Turn when defiance becomes available again (V2b) |

#### Autonomy System
| Field | Type | Description |
|-------|------|-------------|
| `autonomous` | bool | Marshal acting independently |
| `autonomy_turns` | int | Turns remaining in autonomy |
| `autonomy_reason` | string | "redemption", "communication_cut" |
| `redemption_pending` | bool | Redemption event triggered |
| `redemption_cooldown_until` | int | Turn when redemption can next fire (5-turn cooldown, V2b) |
| `autonomous_battles_won` | int | Wins during autonomy |
| `autonomous_battles_lost` | int | Losses during autonomy |
| `autonomous_regions_captured` | int | Captures during autonomy |
| `trust_warning_shown` | bool | Warning shown at trust < 40 |

#### Estate Endowments (ES-7, Economy Revisit S7 + §0.6.8 second pass)
| Field | Type | Description |
|-------|------|-------------|
| `dotation_regions` | list | Provinces endowed to this marshal — their full effective income redirects to his household; pruned when a province leaves the nation's hands. Default `[]`. |
| `expectation_grace_turn` | int | Turn an unmet reward expectation was first observed (-1 = none). Erosion fires after the 2-turn grace window. Save-compat: absent → -1, so old saves take no retroactive erosion. |
| `pension` | int | ES-7 second pass (§0.6.8): the rente FACE in g/turn. Counts fully toward satisfaction; the treasury pays `ceil(1.5 × face)`/turn through the income phase. Neither pays nor counts while captured (W6-7). Default `0`. |
| `last_expectation_seen` | int | Last expectation value announced in the Morning Dispatch's expectation-rise lines; reconciled at dispatch build. Default `0`. |

#### Relationships & Co-Location (Phase 4 / Phase 7 S59)
| Field | Type | Description |
|-------|------|-------------|
| `relationships` | dict | Marshal name → relationship level (-2 to +2). **Jealousy v3.2:** a live grievance's temporary −1 is DERIVED in `get_relationship` and never written here. |
| `co_location_turns` | dict | Marshal name → turn when co-location streak started |
| `last_relationship_change_turn` | dict | Marshal name → last turn relationship changed (S64 cooldown) |

#### Jealousy System (v3.2, July 11, 2026 — docs/JEALOUSY_SPEC.md §0)
| Field | Type | Description |
|-------|------|-------------|
| `jealous_of` | str\|null | Grievance target marshal name (`null` = content). Drives the derived −1, expressions, and resolution arc. Default `null`. |
| `jealousy_turns_remaining` | int | Grievance countdown (2–5, delta-scaled). Default `0`. |
| `jealousy_surge_turns` | int | "I showed them" surge countdown (+10% attack/defense or lingering Literal intel for 1 turn after ACTION resolution). Default `0`. |
| `jealousy_autonomous_warned` | bool | Aggressive advance-warning latch — the attack fires at end-turn unless the player orders him. Default `false`. |
| `glory_events` | list[dict] | Rolling glory record `[{turn, points}]`, pruned to the 5-turn window each evaluation. Default `[]`. |
| `jealousy_history` | dict | Lifetime fires per target `{name: [turns]}` **plus** the `"__levels__"` key → `{name: escalation_level}` dict (mixed-shape — serialization copies each value by its true shape). Default `{}`. |
| `consecutive_hold_turns` | int | Literal sidelining counter (HOLD/no-order while peers actively engaged). Default `0`. |
| `separation_flagged` | dict | §6b "Separate Them" `{marshal_name: true}` — dispatch warns when a flagged pair stands within reach. Default `{}`. |
| `glory_crowned` | bool | Crowned with Glory: #1 on the nation's ladder (+1 shock/defense/administration via `get_effective_skill`/`get_admin_with_crown`). Recomputed every evaluation; serialized so a mid-turn save keeps the buff live. Default `false`. |

#### Tactical State
| Field | Type | Description |
|-------|------|-------------|
| `drilling` | bool | Currently drilling (turn N) |
| `drilling_locked` | bool | Locked in drill (turn N+1) |
| `drill_complete_turn` | int | Turn when drill completes |
| `shock_bonus` | int | +2 = +20% attack from drill |
| `fortified` | bool | Currently fortified |
| `defense_bonus` | float | 0.0-0.20, decimal (0.16 = 16%) |
| `square_formation` | bool | In square formation (Session 67). +5% def, cavalry -40%, artillery +50% |

#### Strategic Order System (Phase 5.2)
| Field | Type | Description |
|-------|------|-------------|
| `strategic_order` | dict\|null | StrategicOrder if active |
| `pending_interrupt` | dict\|null | Interrupt awaiting response |
| `strategic_combat_bonus` | int | % bonus from inspiring commands |
| `strategic_defense_bonus` | int | % bonus from clear orders |
| `precision_execution_active` | bool | +1 to all skills active |
| `precision_execution_turns` | int | Countdown (3 turns) |

#### Combat Tracking
| Field | Type | Description |
|-------|------|-------------|
| `in_combat_this_turn` | bool | Fought this turn |
| `last_combat_turn` | int\|null | Turn of last combat |
| `last_combat_result` | string\|null | "victory", "defeat", "stalemate" |
| `last_combat_location` | string\|null | Region of last combat |

#### Retreat/Broken State
| Field | Type | Description |
|-------|------|-------------|
| `retreating` | bool | In retreat recovery |
| `retreat_recovery` | int | 0-3 recovery stage |
| `retreated_this_turn` | bool | Retreated this turn (ally cover) |
| `_recovery_destination` | str/null | AI retreat destination cache |
| `broken` | bool | Army shattered |
| `broken_recovery` | int | 0-4 recovery stage |

#### Stance System
| Field | Type | Valid Values |
|-------|------|-------------|
| `stance` | string | "neutral", "defensive", "aggressive" |

#### Cavalry Limits
| Field | Type | Description |
|-------|------|-------------|
| `turns_in_defensive_stance` | int | Counter (triggers at 3) |
| `turns_fortified` | int | Counter (triggers at 3) |
| `cumulative_fortification_turns` | int | Total fortification turns across unfortify/refortify cycles. Used for decay calculation to prevent exploit. |

#### Ability State
| Field | Type | Description |
|-------|------|-------------|
| `counter_punch_available` | bool | Cautious free attack earned (personality trait) |
| `counter_punch_turns` | int | Turns to use counter-punch |
| `counter_punch_ready` | bool | Davout Counter-Punch Mastery: +20% next attack after defending |
| `iron_resolve_stacks` | int | Iron Resolve (MC-1c): coiled fortify stacks, max 3 — next attack consumes all for +8% each; survive unfortify, clear on move/retreat/broken. Load default 0 |
| `holding_position` | bool | Grouchy Immovable active |
| `hold_region` | string | Region where holding |

#### Recklessness System
| Field | Type | Description |
|-------|------|-------------|
| `recklessness` | int | 0-4, builds from wins |
| `pending_glorious_charge` | bool | Popup pending |
| `pending_charge_target` | string | Target of pending charge |

#### Exhaustion
| Field | Type | Description |
|-------|------|-------------|
| `attacks_this_turn` | int | Attacks made this turn |

#### Bombardment Tracking (Sessions 2, 48)
| Field | Type | Description |
|-------|------|-------------|
| `bombardments_this_turn` | int | Number of bombardments fired this turn (max 2, reset at turn start) |
| `cannon_fire_ignored_turn` | int\|null | Turn when marshal ignored cannon fire (personality trigger, null if never) |

#### Idle Tracking (V2a)
| Field | Type | Description |
|-------|------|-------------|
| `idle_turns` | int | Consecutive turns without attack or move (V2b: triggers idle objections) |
| `last_battle_turn` | int | **W6-1 (BUG-CA-9).** Turn this marshal last fought a field battle (primary or arrived reinforcer); -1 = never. Feeds W6-3 dispatch arc memory. |
| `captured_by` | str | **W6-7 Marshal Fates.** Captor nation ("" = free). A captured marshal sits at the captor's capital with strength 0 (never swept by the attrition elimination), excluded from rosters/muster/reinforcement scans; ES-7 expectations freeze. |
| `captured_turn` | int | **W6-7.** Turn of capture; -1 = never captured. |

#### Contested Capture (Phase 6.2.F)
| Field | Type | Description |
|-------|------|-------------|
| `occupation_region` | string\|null | Region being occupied (null if not occupying) |
| `occupation_turns_held` | int | Turns held so far |
| `occupation_turns_required` | int | Turns needed to complete capture (1 = ungarrisoned, 2 = garrisoned) |

#### Reinforcement (Phase 7 S61a)
| Field | Type | Description |
|-------|------|-------------|
| `reinforced_this_turn` | bool | Whether marshal already reinforced this turn (blocks double-reinforcement, cleared at turn start) |

---

## StrategicOrder Format

```json
{
  "command_type": "MOVE_TO",
  "target": "Belgium",
  "target_type": "region",
  "started_turn": 3,
  "original_command": "march to Belgium",
  "path": ["Paris", "Belgium"],
  "follow_if_moves": true,
  "join_combat": true,
  "target_snapshot_location": null,
  "attack_on_arrival": false,
  "delegation_inferred": false,
  "condition": null,
  "last_combat_enemy": null,
  "last_combat_turn": null,
  "last_combat_result": null,
  "last_contact_enemy": null,
  "last_contact_turn": null
}
```

### StrategicOrder Fields

| Field | Type | Description |
|-------|------|-------------|
| `command_type` | string | "MOVE_TO", "PURSUE", "HOLD", "SUPPORT" |
| `target` | string | Region name, marshal name, or "generic" |
| `target_type` | string | "region", "marshal", "battle", "generic" |
| `started_turn` | int | Turn when order was issued |
| `original_command` | string | Raw command text |
| `path` | list | Planned route as region names |
| `follow_if_moves` | bool | (SUPPORT) Follow if ally moves |
| `join_combat` | bool | (SUPPORT) Join ally's combat |
| `target_snapshot_location` | string\|null | For "Move to Ney" - where Ney was |
| `attack_on_arrival` | bool | (MOVE_TO) Attack on reaching destination |
| `delegation_inferred` | bool | CR-5: action inferred from an aggressive marshal's personality off a delegation verb (not explicitly typed). Gates EVERY auto-attack seam this order can reach (per-turn MOVE_TO arrival + all PURSUE sites + both first-step PURSUE seams) on fortification-aware bad odds; explicit typed orders stay gate-free. When set, `original_command` holds the player's VERBATIM delegation phrase (rider d "words become the record") rather than the synthetic reissue |
| `condition` | dict\|null | StrategicCondition if set |
| `last_combat_enemy` | string\|null | Combat loop prevention |
| `last_combat_turn` | int\|null | Combat loop prevention |
| `last_combat_result` | string\|null | "victory", "defeat", "stalemate" |
| `bombardment_target` | string\|null | Locked target for artillery HOLD |
| `arrived_turn` | int\|null | (SUPPORT) Turn when marshal first reached ally. Timed SUPPORT counts from this, not started_turn. |
| `last_contact_enemy` | string\|null | (PURSUE) Last enemy contacted during pursuit (fog-of-war tracking) |
| `last_contact_turn` | int\|null | (PURSUE) Turn of last enemy contact |

---

## StrategicCondition Format

```json
{
  "max_turns": 10,
  "until_marshal_arrives": "Davout",
  "until_marshal_destroyed": null,
  "until_battle_won": true,
  "until_relieved": false
}
```

### StrategicCondition Fields

| Field | Type | Description |
|-------|------|-------------|
| `max_turns` | int\|null | Maximum turns for order |
| `until_marshal_arrives` | string\|null | End when marshal arrives |
| `until_marshal_destroyed` | string\|null | End when enemy destroyed |
| `until_battle_won` | bool | End when battle won (or stalemate) |
| `until_relieved` | bool | End when relieved by ally |

---

## Region Format

```json
{
  "name": "Paris",
  "adjacent_regions": ["Belgium", "Lyon", "Brittany", "Waterloo"],
  "income_value": 300,
  "is_capital": true,
  "terrain": "urban",
  "region_type": "capital",
  "controller": "France",
  "garrison_strength": 0,
  "garrison_detachment": false,
  "stability": 100,
  "war_damage": 0.0,
  "plundered": false,
  "buildings": [{"type": "supply_depot", "damaged": false}],
  "building_under_construction": null,
  "watchtower": "none",
  "watchtower_turns_remaining": 0
}
```

### Region Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Region name |
| `adjacent_regions` | list | Names of bordering regions |
| `income_value` | int | Gold per turn when controlled |
| `is_capital` | bool | Whether this is a capital |
| `terrain` | string | Terrain type: plains, forest, hills, mountains, urban, river_crossing. Default "plains" for backward compat. |
| `region_type` | string | Region type: capital, major_city, city, town, rural. Default "town" for backward compat. |
| `is_coastal` | bool | Whether the region borders the sea. Default false for backward compat. |
| `grid_position` | list\|null | `(row, col)` for direction resolution — authored for the legacy 19, centroid spatial-rank for the 126 Europe provinces (Map Slice 4). Default null for backward compat. |
| `controller` | string\|null | Nation controlling region |
| `garrison_strength` | int | Garrison troops (capital: 15k start, player-placed: 3k detachment) |
| `garrison_detachment` | bool | True if garrison was placed by marshal detachment — player or AI (no regen, no 5k collapse). Default false. Backward compat: `from_dict` also reads old `garrison_player_placed` key. |
| `stability` | int | 0-100, affects income via tiered modifier. Default 100 for backward compat. (Phase 6.2.C) |
| `war_damage` | float | 0.0-0.5, reduces income. Default 0.0 for backward compat. (Phase 6.2.C) |
| `plundered` | bool | True if region was plundered on capture. Clears when stability > 50. Default false. (Phase 6.2.E) |
| `buildings` | list | Built buildings: `[{"type": str, "damaged": bool}]`. Default []. (Phase 6.2.E) |
| `building_under_construction` | dict\|null | Active construction: `{"type": str, "turns_remaining": int}`. Default null. (Phase 6.2.E) |

### Computed Properties (not serialized)

| Property | Derived From | Description |
|----------|-------------|-------------|
| `defense_bonus` | terrain | Defender bonus (0.0-0.25) |
| `movement_cost` | terrain | Attrition multiplier (1.0-2.0) |
| `supply_modifier` | terrain | Supply capacity modifier (0.5-1.2) |
| `cavalry_effectiveness` | terrain | Cavalry combat multiplier (0.3-1.2) |
| `get_effective_income()` | stability, war_damage, buildings | Actual income: `int(int((income_value + depot_bonus) * market_mult) * stability_mod * (1 - war_damage))`. Market mult = 1.25 if functional market, else 1.0. |
| `get_stability_label()` | stability | "Hostile" / "Unrest" / "Settling" / "Stable" |
| `max_building_slots()` | region_type | Capital: 2, major_city/city: 1, town/rural: 0 |
| `has_building(type)` | buildings | True if functional (undamaged) building of that type exists |

---

## Trust Format

```json
{
  "value": 75
}
```

### Trust Fields

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `value` | int | 0-100 | Trust level (81+ Loyal, 61-80 Reliable, 41-60 Questioning, 21-40 Strained, 0-20 Broken) |

---

## AuthorityTracker Format

```json
{
  "authority": 100,
  "recent_responses": [
    {"choice": "trust", "turn": 1},
    {"choice": "insist", "turn": 2},
    {"choice": "compromise", "turn": 3}
  ],
  "_crossed_thresholds": [70]
}
```

### AuthorityTracker Fields

| Field | Type | Description |
|-------|------|-------------|
| `authority` | int | 0-100, Napoleon's authority |
| `recent_responses` | list | Last 10 enriched responses. Each entry: `{"choice": str, "turn": int}`. V2b format — backward-compatible from_dict accepts bare strings. |
| `_crossed_thresholds` | list | Threshold events already triggered (70, 50, 30) |

---

## VindicationTracker Format

```json
{
  "pending": {
    "Ney": {
      "choice": "insist",
      "original_order": {"action": "attack", "target": "Wellington"},
      "alternative": {"action": "defend"},
      "turn_recorded": null
    }
  },
  "history": [
    {
      "marshal": "Ney",
      "choice": "trust",
      "result": "victory",
      "vindication_change": 1,
      "trust_change": 3,
      "authority_change": 0,
      "message": "...",
      "new_vindication": 1,
      "new_trust": 78
    }
  ],
  "pending_defensive_vindication": {
    "Davout": {
      "order": {"action": "defend", "target": "Belgium"},
      "timestamp": 5
    }
  }
}
```

### VindicationTracker Fields

| Field | Type | Description |
|-------|------|-------------|
| `pending` | dict | marshal_name -> pending vindication data |
| `history` | list | List of resolved vindication events |
| `pending_defensive_vindication` | dict | marshal_name -> pending defensive vindication (V2a) |

---

## RegionIntel Format (Fog of War)

```json
{
  "region_name": "Belgium",
  "visibility": "partial",
  "known_marshals": [
    {"name": "Wellington", "nation": "Britain", "band": "large force"}
  ],
  "strength_band": "large force",
  "exact_strength": null,
  "morale": null,
  "stance": null,
  "last_scouted_turn": 0,
  "last_updated_turn": 1,
  "intel_source": "adjacent"
}
```

### RegionIntel Fields

| Field | Type | Description |
|-------|------|-------------|
| `region_name` | string | Region this intel applies to |
| `visibility` | string | Current visibility level: "full", "partial", "stale", "last_known", "unknown" |
| `known_marshals` | list | Snapshot of marshals last seen: `[{name, nation, strength?, band?}]`. Frozen during decay. |
| `strength_band` | string | Aggregate strength band: "no forces", "screening force", "small force", "substantial force", "large force", "massive force" |
| `exact_strength` | int\|null | Exact total troop count. Only set at FULL visibility. |
| `morale` | int\|null | Morale value. Only set at FULL visibility. |
| `stance` | string\|null | Stance value. Only set at FULL visibility. |
| `last_scouted_turn` | int | Turn when last scouted via scout action. Default 0. |
| `last_updated_turn` | int | Turn when intel was last refreshed by any source. Default 0. |
| `intel_source` | string | Best source: "own_territory", "marshal_present", "scout", "battle", "watchtower", "adjacent", "transit" |

### Visibility Levels (priority order)

| Level | Priority | Data Available |
|-------|----------|----------------|
| `full` | 4 | Exact strength, morale, stance, marshal names |
| `partial` | 3 | Marshal names + strength band, no morale/stance |
| `stale` | 2 | Frozen snapshot from last refresh, aging |
| `last_known` | 1 | Old snapshot, "last seen X turns ago" |
| `unknown` | 0 | Never scouted, no intel |

### Strength Bands

| Threshold | Band |
|-----------|------|
| 0 | "no forces" |
| 1 - 4,999 | "screening force" |
| 5,000 - 14,999 | "small force" |
| 15,000 - 39,999 | "substantial force" |
| 40,000 - 69,999 | "large force" |
| 70,000+ | "massive force" |

### Decay Timeline

| Turns since update | Effect |
|--------------------|--------|
| 0-2 | Stays at current level (fresh) |
| 3-4 | Degrades to STALE (exact data cleared, snapshot frozen) |
| 5+ | Degrades to LAST_KNOWN (persists indefinitely) |

---

## Validation Checklist

When implementing save/load, verify:

- [ ] All fields listed here are saved
- [ ] All fields listed here are restored
- [ ] Nested objects are proper instances, not plain dicts
  - `marshal.trust` is `Trust`, not `dict`
  - `marshal.strategic_order` is `StrategicOrder`, not `dict`
  - `marshal.strategic_order.condition` is `StrategicCondition`, not `dict`
  - `world.authority_tracker` is `AuthorityTracker`, not `dict`
  - `world.vindication_tracker` is `VindicationTracker`, not `dict`
  - All regions are `Region`, not `dict`
  - All intel entries are `RegionIntel`, not `dict`
- [ ] None values are handled correctly (field present with null value)
- [ ] Enum values are stored as strings, restored as enums (e.g., Stance)
- [ ] Unknown fields in save file are ignored (forward compatibility)
- [ ] All integer fields use `int()` wrapper (Godot compatibility)
- [ ] All float fields (defense_bonus) preserve precision

## Test Coverage

Serialization is validated by `tests/test_serialization.py`:

| Test Class | Tests | Coverage |
|------------|-------|----------|
| TestStrategicConditionSerialization | 3 | All condition fields |
| TestStrategicOrderSerialization | 5 | All order types |
| TestMarshalSerialization | 6 | All 50+ marshal fields |
| TestTrustSerialization | 3 | Value roundtrip |
| TestRegionSerialization | 3 | All region fields |
| TestAuthorityTrackerSerialization | 3 | Authority and thresholds |
| TestVindicationTrackerSerialization | 3 | Pending and history |
| TestWorldStateSerialization | 4 | Complete game state |
| TestParseResultSerialization | 2 | Command parsing |

**Total: 33 roundtrip tests, all passing**

---

## Future Considerations

### Version Migration

When format changes:
1. Increment `format_version`
2. Add migration function for old -> new format
3. Support reading old versions

**Version 2 (Session 1A):** Map expanded from 13 to 19 regions. Hard break — version 1 saves are rejected with a clear message. No migration path (map structure changed too fundamentally).

**Version 3 (Map Slice 5, July 1, 2026):** The 126-province Europe cutover (`save_manager.FORMAT_VERSION = 3`). Region keys changed wholesale, so pre-cutover (v1/v2) saves are rejected with a clear versioned message naming both formats (DEF-2 — no silent crash, no migration path). The `metadata.format_version` written by `save_manager.py` is the integer 3; new fields `sovereign_map` (WorldState) and `grid_position`/`is_coastal` (Region) are documented above.

### Save File Structure (Pre-EA)

Suggested file structure for actual save/load:

```json
{
  "metadata": {
    "format_version": "1.1",
    "game_version": "0.8.0-dev",
    "saved_at": "2026-01-28T12:34:56Z",
    "save_name": "Campaign Turn 15",
    "playtime_seconds": 3600
  },
  "world_state": { ... }
}
```

### Compression

For large save files (200+ regions), consider:
- JSON with gzip compression
- Binary format (msgpack)

### Checksums

For corruption detection:
```json
{
  "checksum": "sha256:abc123...",
  "world_state": { ... }
}
```
