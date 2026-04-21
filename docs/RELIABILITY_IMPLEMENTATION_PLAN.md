# Memory and Pressure — Implementation Plan

> **Spec:** `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.4.3 (April 20, 2026 deep-audit fixes on top of v2.4.2 Hegemony refactor + audit cleanup — static concern seed replaced by power-based balance-of-power engine)
> **Created:** April 13, 2026
> **Last Updated:** April 20, 2026 (v2.4.3 plan alignment: `world.nation_power_tiers` runtime map dropped in favor of direct authored-record reads; B-Hegemony test list expanded with recursive vassal-chain + cycle-safety + non-France-hegemon guard; `add_threat` wire-up gated on `hegemon == world.player_nation`; new "Merge ordering — B-B1-lite and B-B4" section in Execution Order)
> **Sessions remaining:** ~1.5 effective on the critical path (B-Hegemony expanded with scenario-data authoring + prerequisite helpers; B-B1-lite + B-B3 + B-B7 fold into the same session; trimmed Slice C-lite may slip to a short follow-up)
> **Est. tests remaining:** ~45-54 (B-Hegemony 18-22 + B-B1-lite 7-8 + B-B3 3 + B-B7 8 + Slice C-lite trimmed 10-12; down from v2.3 ~68-74, up from v2.4 ~35-42 after prerequisite-helper audit)

---

## v2.4 Rewrite Summary

The April 19 design pass collapsed the v2.3 plan around the Napoleonic balance-of-power doctrine. Static concern pairs disappear. A single per-turn hegemony calculation (~60 LOC) drives all the political pressure that the four cancelled v2.3 modifiers were trying to model. See spec v2.4 rescope note for the design rationale.

**Already shipped (in current `master`) — unchanged from v2.3:**

- Slice A1 (data model + serialization): `betrayal_history`, `next_episode_id`, `commitment_event_metadata`, `to_dict` / `from_dict`, save-format reference. ✓
- Slice A2 partial (ledger + preview scaffolding): structured `warnings[]`, breach preview with reliability + applied-vs-intended deltas, `force_break_treaty_confirmation` / `force_declare_war_confirmation` hard-stops with warnings, `commitment_paradox` HARD_STOP type registration (placeholder). ✓
- Slice B2a (third-party anger metadata + breach recording): cascade-rupture fault attribution, episode_id threading, `end_reason_family` / `end_reason_action` / `fault_nation` split, witness_strike_recorded dispatch emit per witness. ✓
- Slice B2b (witness scoping + episode cap + redemption decay + hard-reject): per-witness `scope_reason` precedence, episode-strike cap of 2, severity-scaled bilateral strike decay (strike-removal half), `hard_reject_posture_triggered` / `_cleared` emits with first-cross-only contract, hard-reject acceptance gate. ✓
- AI `decision_reason` subset wired into proposals, counterparty responses, campaign log, popups. ✓

**Cancelled in v2.4 (was in v2.3 plan):**

- ❌ Slice A1-fill — `nation_concerns` static 4-pair seed (replaced by hegemony engine reading current bloc state)
- ❌ Slice B2a-fill — third-party ratification anger loop (captured by hegemony pressure rising naturally when allies join the hegemon's bloc)
- ❌ Slice B6 — redemption tick `actor_honored_turns` +3/5-turn award (invisible to players)
- ❌ Authored Prussia-Saxony escalation triggers (no longer needed without static rivalry seed)
- ❌ Slice C spotlight-tier elevated card variant + split-voice render `attributed_lines[]` + N+1 Talleyrand aside (cut as infra disproportionate to three events)

**This phase ships (v2.4):**

- Slice B-Hegemony (NEW): bloc geometry helpers + hegemony pressure engine + coalition leader selection update + Balance of Europe ledger headline
- Slice B-B1-lite: collapsed acceptance formula — `hegemony_target_mod` + simplified `bilateral_betrayal_mod = -6 * strikes` + reliability narrowing
- Slice B-B3: rename `alliance_paradox` push type to `commitment_paradox` (legacy alias on read) — unchanged from v2.3
- Slice B-B7: Make Amends active-redemption verb — unchanged from v2.1/v2.3
- Slice C-lite: named-diplomat resolution helper + dedicated `commitment_paradox_popup.{tscn,gd}` + committed prose for three live events + Balance of Europe headline render

**§8.8 DG-4 call-to-arms (B-B4) — parallel slice, tightened by v2.4.3.** Tracked in its own slice per the DG-4 amendment in spec §8.8 + `SCALE_READINESS_PLAN.md`. v2.4.3 adds explicit follow-through work for the grievance-variant Make Amends path, same-turn alliance termination on defensive refusal, and the R9/R10/R11 playtest gates. ~25-29 tests, parallel to this slice.

**Moved to `WAR_BARGAIN_SPEC.md` — unchanged from v2.0:**

- Slice C1a / C1b / C2 (war bargains, lifecycle, war-entry integration) → WB-A / WB-B / WB-C
- All bargain-specific tests
- All bargain-specific surface contracts

**Deferred — unchanged:**

- Slice D1 (advisory-first strategic focus + deeper AI integration)
- Slice D2 (coalition buildout + non-French hegemon generalization)

---

## Slice A. Foundations (mostly shipped — unchanged from v2.3)

### A1. Data model + serialization (SHIPPED)

**Files:** `backend/models/world_state.py`, `docs/SAVE_FORMAT_REFERENCE.md`

- ✓ `betrayal_history: Dict[str, Dict]` with `StrikeRecord` shape
- ✓ `next_episode_id: int` allocator counter
- ✓ `to_dict` / `from_dict` round-trip with `.get()` defaults
- ✓ `SAVE_FORMAT_REFERENCE.md` updated
- ✓ Save-migration regression test against pre-commitments fixture

### A2. Ledger + preview scaffolding (SHIPPED partial)

**Files:** `backend/game_logic/diplomatic_ledger.py`, `backend/game_logic/diplomatic_dialogue.py`, `backend/main.py`, `backend/display_names.py`, `godot-client/.../diplomatic_ledger.gd`, `godot-client/.../proposal_confirm_popup.gd`, `godot-client/.../main.gd`

- ✓ Display-name maps for betrayal severity, warning categories
- ✓ Reliability descriptor + bilateral betrayal warning on Talleyrand tab
- ✓ Canonical `warnings[]` / Political Context preview payload scaffolding (`hard_reject`, `betrayal`, `peace_conflict`)
- ✓ Severity ordinals + stable category ordering in shared formatter contract
- ✓ Debug endpoint for betrayal / hard-reject state inspection

**v2.4 deferred (no longer in this phase):**

- ~~Add rivalry display to Diplomatic Ledger Nations tab~~ — replaced by Balance of Europe headline (Slice C-lite)
- ~~Add display-name maps for rivalry intensity~~ — no longer needed

---

## Slice B. Hegemony Pressure (v2.4 rewrite)

### B-Hegemony. Balance-of-power engine (NEW THIS PHASE)

**Files:** `backend/game_logic/coalition.py`, `backend/models/world_state.py`, `backend/game_logic/diplomacy.py` (acceptance formula reader), `backend/game_logic/ai_diplomacy.py`, `backend/game_logic/dispatch.py`, `backend/notifications.py`, scenario config layer (authoring + loader for `power_tier`).

The single biggest new piece. Four prerequisite helpers, three engine helpers, one wire-up, one scenario-data wiring step.

v2.4.3's design-fun refinement keeps the implementation disciplined: **no second continental-politics scalar**. Bloc share remains the only backbone signal. The only new memory allowed in this slice is a tiny threshold-band suppressor so the player does not get the same warning every turn.

**Prerequisite helpers (added because spec §7 consumes them but no equivalent exists):**

- `world.get_power_tier(nation: str) -> Optional[str]` — reads directly from the authored nation record (scenario data) with a `_POWER_TIER_DEFAULT = "secondary"` fallback when the field is missing. **No runtime `world.nation_power_tiers` map is introduced** — per `SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy", the authored scenario config is the single source of truth; runtime code reads from it and does not mutate or shadow it. ~5 LOC accessor, routed through whatever structure currently holds authored nation data (`world.nation_config`, `world.scenario_data`, or equivalent — audit during implementation).
- Scenario config authoring: `power_tier` field added to each nation record in scenario config, colocated with capital / color / starting AP. 1805 roster values per `SCALE_READINESS_PLAN.md` §Phase 0 (France/Britain/Austria/Prussia/Russia = `major`; Spain/Ottoman/Sweden/Naples = `secondary`; Bavaria/Saxony/Portugal/Denmark-Norway = `minor`). ~10 LOC on the scenario-record side (adding the field + default). Authored scenario data is recreated from scenario files on load, not persisted through `to_dict` / `from_dict` — no serialization-enforcement test needed for the field itself.
- `world.last_hegemony_signal_band: int` — tiny presentation-memory field used only to suppress repeat 33/50/67 balance-of-power beats. Defaults to `0`; resets when share falls below `30%`; add `to_dict` / `from_dict` round-trip with missing-field default `0`. This is a dedupe aid, **not** a second pressure meter.
- (Deliberately not adding `world.get_vassals_of` or `world.get_treaty_state` — bloc-member calc iterates `world.vassals` inline and reads `world.get_diplomatic_state(a, b)` directly per spec v2.4.2 §7.1.)
- (Deliberately not adding `world.get_major_powers` — `_calculate_hegemony_pressure` derives majors inline from `get_power_tier(n) == "major"` per spec v2.4.2 §7.3.)

**Bloc geometry helpers (no new state fields):**

- `world.get_bloc_members(leader: str) -> List[str]` — per-turn cached helper. Returns leader + any nation whose `_top_overlord(world, nation)` resolves to `leader` + nations whose `world.get_diplomatic_state(leader, other)` is `"ALLIANCE"` or `"DEFENSIVE_ALLIANCE"`. Includes the `_top_overlord` cycle-safe walker so vassal-of-vassal and 3-deep chains surface on the top overlord's bloc list rather than stopping at one hop. ~24 LOC including cache plumbing and the helper.
- `power_score(nation: str, world) -> int` — `region_count * tier_weight` where `tier_weight = {"major": 3, "secondary": 2, "minor": 1}[world.get_power_tier(nation) or "secondary"]`. ~8 LOC. Reads cached `get_nation_regions()`.
- `bloc_power(leader: str, world) -> int` — sum of `power_score(n)` across `get_bloc_members(leader)`. ~5 LOC.
- Cache invalidation: `world._bloc_members_cache` invalidated alongside the existing per-turn caches on treaty ratification, vassal add/remove, war declaration, peace ratification. Audit the four call sites during implementation.

**Engine to add in `coalition.py`:**

- `_calculate_hegemony_pressure(world) -> Dict[str, int]` — per spec §7.3. Derives majors inline; returns `{hegemon_nation: threat_increment}` or `{}` if share < 30%. ~22 LOC.
- `_hegemony_pressure_for_share(share: float) -> int` — 1/3/5/8 ladder. ~5 LOC.
- `_hegemony_signal_band(share: float) -> int` — returns `0` below `33%`, `1` for `33-49%`, `2` for `50-59%`, `3` for `60%+`. Used only for same-turn signal beats and dedupe.
- Wire into `process_coalition_turn`: if `_calculate_hegemony_pressure` returns non-empty **and** `hegemon == world.player_nation`, call `add_threat(world, increment, source_key="hegemony_passive")`. If the hegemon is any other nation (losing-campaign edge case), emit a debug log for telemetry and skip the call — the threat_level scalar remains France-targeted in v0.1; generalizing it is D2 Coalition Generalization scope. ~8 LOC including the guard clause.
- Same-turn signal beat: when the player's bloc crosses a new `33 / 50 / 60` band, emit one `balance_of_europe_shifted` event on existing notice / dispatch surfaces with `band`, `hegemon`, `share`, `speaker_nation`, and `counterplay_hint`. Falling below `30%` resets `world.last_hegemony_signal_band` to `0`. This is the preferred low-complexity answer to the N+1 scalar lag.

**AI escape-valve work (belongs here, not as later polish):**

- Add an explicit bandwagon P-series rule in `ai_diplomacy.py`: non-bloc minors and exposed secondaries may propose TO the hegemon once bloc share reaches the alarming band (`~45%+` representative target), relations are not hostile, and the nation is not already locked into a rival deep bloc. This is the canonical escape valve that keeps hegemony from reading as a hard ban on growth.
- `counterplay_hint` generation is capability-aware: before B-B7 ships, surface only currently legal hegemony levers (release a vassal, avoid a new major ally, let an alliance lapse, shrink the bloc). `Make Amends` may appear only once the verb is live and legal against the cited court.

**Coalition leader update:**

- `coalition_leadership_score(nation, world)` — add `bloc_share_against` term: `+int((bloc_power(nation, world) / european_power) * 50)`. ~5 LOC. Test must explicitly assert the French-hegemon precondition — the function's `france = world.player_nation` anchor is an existing D2 item, not a v2.4 regression.

**Tests (~24-30):**

- `world.get_power_tier` returns authored tier for each roster tier; returns `None` for unauthored nation
- `world.get_power_tier` reads live from the authored scenario record (not a runtime map); mutation test verifies there is no writable `world.nation_power_tiers` field
- Scenario loader surfaces `power_tier` correctly on the first call after `/new_game`
- `last_hegemony_signal_band` defaults to `0` and survives save/load round-trip
- `get_bloc_members` for various treaty configurations: France alone, France+1 vassal, France+1 ally, France+vassal+ally, vassal-of-vassal cascade (top-overlord walk), sub-vassal-of-vassal cascade (3-deep chain), NON_AGGRESSION does not count, OPEN_BORDERS does not count
- `get_bloc_members` cycle-safety: a vassal data error where A->B and B->A terminates cleanly at `_top_overlord` rather than looping
- `get_bloc_members` cache invalidation: treaty ratification / vassal change / war declaration / peace each invalidate the right entry
- `power_score` with major/secondary/minor tiers
- `power_score` fallback to `"secondary"` default when `get_power_tier` returns `None`
- `bloc_power` aggregation correctness
- `_calculate_hegemony_pressure` returns `{}` when share < 30%, returns hegemon at 35% / 45% / 55% / 65% with correct ladder values
- `_calculate_hegemony_pressure` defensive fallback when no nation is authored `major` — derives from active-nations set
- `process_coalition_turn` integration: passive contribution adds to `threat_level`, decay still drains it, `threat_sources_this_turn` records `"hegemony_passive"` source key
- `process_coalition_turn` non-France-hegemon guard: synthetic test where `_calculate_hegemony_pressure` returns `{Russia: +5}` asserts `threat_level` does NOT change (guard skips `add_threat`); Balance of Europe headline copy still names Russia correctly
- `_hegemony_signal_band` returns 0 / 1 / 2 / 3 at the correct thresholds and only upward crossings emit beats
- `balance_of_europe_shifted` fires exactly once per new band, resets after bloc share falls below `30%`, and chooses deterministic speaker fallback
- same-turn treaty ratification / vassal change that crosses a band emits the signal beat even though passive scalar accrual lands on the next turn
- `coalition_leadership_score` favors highest-bloc-share-against among non-bloc members (France-hegemon precondition asserted)
- France-bloc shrinks (vassal released or ally defects) → next turn pressure stops accruing
- Balance of Europe headline composition across: no hegemon, France at 35%, France at 55% with Brewing coalition
- bandwagon AI trigger: non-bloc minor proposes into the hegemon bloc at high share; blocked when hostile or already in a rival deep bloc

**Playtest / tuning gates (design contract, not polish):**

- same-turn named-court beats fire at `33 / 50 / 60` before coalition declaration
- peaceful France at `50-55%` share reaches `BREWING` in roughly `12-16` turns if ignored
- `60%+` sustained share feels like an acute crisis, with declaration pressure mounting in roughly another `4-8` turns unless the bloc shrinks
- a cold-start, zero-threat run that still drifts into the mid-20s turns before `BREWING` is a failed tune gate: retune the ladder or coalition decay before closing B-Hegemony

### B-B1-lite. Acceptance formula collapse (THIS PHASE)

**Files:** `backend/game_logic/diplomacy.py`, `backend/display_names.py`

- Add `hegemony_target_mod(asker, target, world)` per spec §9.1. Single negative term: 0 at exactly 30% share, then scales down to -20 with bloc share. Returns 0 when no hegemon, 0 when asker outside hegemon bloc, 0 for intra-bloc proposals.
- Replace existing acceptance formula's `direct_concern_mod` / `concern_conflict_mod` slots (if any partial wiring exists) with single `hegemony_target_mod` call.
- Add `bilateral_betrayal_mod(asker, target, world) = -6 * _get_active_betrayal_strike_count(world, asker, target)` (module function already in `diplomacy.py`; arg order is `(actor, victim)` so asker=actor, target=victim). Flat, no cap (hard-reject at 3 strikes is the door-shut, already shipped).
- Tighten `reliability_modifier` to `clamp(diplomatic_reliability[asker] // 10, -6, +6)` (current code is `// 5` capped ±10 — legacy R34).
- Wire debug breakdown output (`components` dict) and feedback strings (`FEEDBACK_STRINGS`) for the new modifiers.
- Add `hegemony` warning category to the preview pipeline in `build_proposal_commitment_warnings`; warning text must name why Europe is hardening and, when available, one immediate counter-play lever. Legacy `concern` reads as `hegemony` for save-load back-compat.
- Betrayal-derived preview warnings must cite one remembered referent when `commitment_event_metadata` gives one (named nation, broken treaty, abandoned alliance, or witness context), so refusal pressure reads as memory instead of hidden arithmetic.

**Tests (~8-9):**

- `hegemony_target_mod` returns 0 outside hegemon bloc
- `hegemony_target_mod` returns 0 for intra-bloc proposals
- `hegemony_target_mod` returns 0 at the 30% boundary and scales correctly to the -20 clamp at high share
- `bilateral_betrayal_mod` returns -6 / -12 / -18 for 1 / 2 / 3 strikes (hard-reject blocks at 3)
- Reliability narrowing: `// 10` capped ±6, regression check vs prior representative scores
- Composite acceptance score: when both hegemony pressure and betrayal apply, both surface independently in `components` dict
- `hegemony` warning is emitted through the preview pipeline with deterministic category / severity ordering
- Betrayal warning text includes a remembered referent when episode metadata exists
- Warning-category alias round-trip: legacy `concern` warnings on a saved pre-v2.4 save load back as `hegemony` without data loss
- AI `decision_reason` alias round-trip: legacy `concern_pressure` reads as `hegemony_pressure` per spec §10.1

### B-B3. Commitment paradox rename (THIS PHASE — unchanged from v2.3)

**Files:** `backend/commands/diplomatic_executor.py`, `backend/game_logic/diplomacy.py`, `backend/models/dialogue_manager.py`, `godot-client/.../main.gd`, `godot-client/.../alliance_paradox_popup.gd` (rename to `commitment_paradox_popup.{tscn,gd}` per Slice C)

- Rename push-side dialogue type from `"alliance_paradox"` to `"commitment_paradox"` in the existing alliance-cross-war paradox flow (`backend/game_logic/diplomacy.py:2135`).
- Keep `"alliance_paradox"` as a read-side alias for save-load back-compat: when loading old saves, treat `alliance_paradox` dialogue type as `commitment_paradox`.
- HARD_STOP_TYPES already lists `commitment_paradox` as a placeholder — this rename activates that registration.
- The dedicated `commitment_paradox_popup.{tscn,gd}` Godot surface ships in Slice C-lite.
- Preserve all existing fallout-preview behavior (`origin_episode_id` continuity, `commitment_paradox_resolved` log + dispatch event with `chosen_nation` / `spurned_nation`).

**Tests (~3):** rename smoke test, alias load test, no double-emit on rename.

### B-B7. Make Amends active-redemption verb (THIS PHASE — unchanged from v2.1/v2.3)

**Files:** `backend/commands/diplomatic_executor.py`, `backend/commands/parser.py`, `backend/game_logic/diplomacy.py`, `backend/models/world_state.py`, `backend/display_names.py`, `backend/campaign_log.py`, `backend/ai/llm_client.py`, `backend/ai/validation.py`

Per spec §8.6.1. Ships the v0.1 standard strike-clearing verb so repaired relationships are a deliberate political gesture. The grievance-clearing variant added in spec §8.6.1a is part of B-B4, not this slice.

- Add `make_amends` to `VALID_ACTIONS` in `validation.py`
- Add `_execute_make_amends(world, command)` in `diplomatic_executor.py`:
  - pre-validate: target has ≥ 1 active victim-side strike from France, non-`WAR` treaty state, cooldown ≤ current turn, gold ≥ 200, DP ≥ 1
  - on success: spend 200g + 1 DP, remove 1 strike (oldest matured first, else lowest-severity active), `diplomatic_reliability["France"]` += 2, `nation_relation` France → target += 5, set `reparations_cooldown[diplo_key] = current_turn + 10`, emit `amends_offered` on the campaign log plus lightweight notice / ledger surfaces, and include one line of named-diplomat acknowledgment in the result text
  - on refusal: return Talleyrand-voiced advisory per spec §8.6.1 refusal conditions
- Parser keywords: `make amends`, `amends`, `offer amends`, `repair relations`, `make amends with {nation}`
- Mock parser keyword mapping in `llm_client.py`
- Display-name maps: `AMENDS_REFUSAL_DISPLAY` in `campaign_log.py`, `ACTION_DISPLAY` entry for "Make Amends"
- Add `reparations_cooldown: Dict[str, int]` field to WorldState, with `to_dict` / `from_dict` round-trip
- Enemy AI does NOT use this action in v0.1

**Tests (~10):** success path, named-diplomat acknowledgment on success, `amends_offered` lightweight surface emit, 4 refusal conditions, serialization round-trip, cooldown enforcement across save/load, strike-selection rule.

---

### B-B4. DG-4 call-to-arms follow-through (parallel slice; v2.4.3 tightened contract)

**Files:** `backend/game_logic/diplomacy.py`, `backend/commands/diplomatic_executor.py`, `backend/commands/parser.py`, `backend/models/world_state.py`, `backend/game_logic/coalition.py`, `backend/campaign_log.py`, `backend/display_names.py`, `backend/notifications.py`

Tracked in the DG-4 amendment slice, but v2.4.3 adds three implementation-defining follow-through items that implementers must see in the plan:

- **Make Amends (grievance variant).** Add the distinct grievance-clearing path from spec §8.6.1a: parser-disambiguated verb (`make amends with {nation} for the abandoned alliance`), `400g + 2 DP` cost, oldest-grievance removal, `+3` reliability / `+8` relation, shared `reparations_cooldown`, and `amends_offered` metadata flagging `grievance_variant: True` on the same lightweight notice / ledger route as the standard variant.
- **Alliance termination on defensive refusal.** On `call_to_arms_refused_defensive`, terminate the existing `ALLIANCE` / `DEFENSIVE_ALLIANCE` to `PEACE` in the same turn, emit `diplomatic_treaty_broken` with `end_reason_family = "defensive_refusal_termination"`, invalidate bloc caches on that treaty-state change, and let `anti_renewal_cooldown` gate re-ratification.
- **Acceptance-formula interaction.** B-B4 owns the `grievance_modifier` term, the per-pair 3-grievance stacking cap, and the debug / warning exposure expected by spec §9.3 when the floor clamps. Merge ordering against B-B1-lite stays mandatory per the section below.

**Tests (~6-9 added on top of DG-4 core coverage):**

- Standard vs grievance-variant Make Amends parse as distinct verbs when both are legal
- Grievance-variant Make Amends shares cooldown with the standard variant and cannot clear ordinary strikes
- `call_to_arms_refused_defensive` terminates an existing alliance to `PEACE` and emits `end_reason_family = "defensive_refusal_termination"`
- Same-turn treaty termination invalidates `get_bloc_members` cache and shrinks bloc membership before later same-turn proposal reads
- `grievance_modifier` saturates at 3 active grievances per pair
- Composite floor debug output surfaces raw hegemony / betrayal / grievance terms plus the synthetic `composite_floor` row when clamped

**Playtest / audit gates from v2.4.3 risks:**

- **R9:** verify repeated Make Amends use in one turn reads as acceptable political cost; if the "repair tour" feels gamey, add a global per-turn cap before closing the slice
- **R10:** verify the canonical `ai_diplomacy.py` bandwagon trigger actually fires in play so non-bloc minors can still bandwagon to the hegemon; if Bavaria / Saxony never propose into a dominant French bloc, tune or fix the trigger before phase close
- **R11:** spot-check exact-30% share states in playtest; if the boundary artifact is visible enough to confuse players, retune the threshold rather than leaving it undocumented

---

## Slice C-lite. Trimmed presentation pass

See `COMMITMENTS_PRESENTATION_SPEC.md` v0.5.1 (trimmed to the shipped scope).

**v2.4 keeps:**

- **Named-diplomat resolution helper** (single backend helper that reads `world.diplomats[nation]` and resolves `speaker="envoy"` to the named diplomat with their personality register, and `speaker="foreign_office"` to "The Chancery of {nation}" per `DIPLOMAT_VOICE_BIBLE.md`)
- **Committed mock prose** for the three live events using Voice Bible registers: `hard_reject_posture_triggered`, `diplomatic_treaty_broken` where `end_reason_family=french_breach`, `commitment_paradox_resolved`
- **Dedicated `commitment_paradox_popup.{tscn,gd}`** — replaces legacy `alliance_paradox_popup` for the renamed type
- **Balance of Europe headline render** (NEW for v2.4) in `diplomatic_ledger.gd` — state-composed headline at top of Nations tab per spec §11.1 (no hegemon, hegemon only, BREWING without leader, DECLARED with leader)
- **Balance of Europe threshold beats** on existing notice / dispatch surfaces at `33 / 50 / 60`, each using a named diplomat or chancery line plus one counter-play hint
- **`amends_offered` lightweight notice family** for both standard and grievance-variant repair gestures, with target-court acknowledgment and ledger trace

**v2.4 cuts:**

- ❌ Spotlight tier elevated card variant on `notification_bar.gd` — three events do not justify the infra
- ❌ Split-voice render `attributed_lines[]` blocks on popup scenes — single-voice with named-diplomat attribution suffices at 5-nation scale
- ❌ N+1 Talleyrand aside callback keyed by `episode_id` — defer to later presentation pass

**Tests (~13-15):** named-diplomat resolution helper for each of 5 nations, three event copy paths render correct named diplomat, paradox popup field wiring, Balance of Europe headline composition for various states (no hegemon, France hegemon at various shares, coalition formed, coalition dissolved), threshold-beat copy / attribution at `33 / 50 / 60`, `amends_offered` copy / attribution.

---

## Slice D. Deferred follow-up (unchanged from v2.3)

### D1. Advisory-first strategic focus + deeper AI integration

- Strategic-focus layer for AI phrasing + Talleyrand recommendations
- Dynamic power scoring (richer `power_score` formula reading manpower / treasury / military strength)
- Richer rival-aware agenda logic
- Performance: no new per-region scans

### D2. Coalition buildout and generalization

- Generalize `coalition.py` `threat_level` scalar from `int` (France-targeted) to `Dict[str, int]` (per-target)
- Wire formation/dissolution/leader against any hegemon, not just France
- Lift any remaining anti-France hardcoded paths in `diplomacy.py` (~14 sites flagged in spec §R5)

### Slice WB-* (deferred to Peace Deals phase)

War bargain implementation in `WAR_BARGAIN_SPEC.md`:

- WB-A: data model + creation + validation
- WB-B: lifecycle (fulfillment + breach + void)
- WB-C: war-entry integration + Bargain Review + AI rules
- WB-D: bargain-era presentation extension

---

## Execution Order (v2.4)

```text
B-Hegemony (helpers + engine + coalition wire-up)
       -> B-B1-lite (acceptance formula collapse)
       -> B-B3 (paradox rename)
       -> B-B7 (Make Amends)
       -> Slice C-lite (named-diplomat helper + paradox popup + prose + Balance headline)

B-B4 (DG-4 call-to-arms episodes) — parallel slice with ordering constraint against B-B1-lite (see "Merge ordering" below)
```

### Merge ordering — B-B1-lite and B-B4 (DG-4) composite-floor interaction

B-B1-lite's acceptance-formula collapse (spec §9.3 pre-DG-4 clause: "no composite floor needed") is only valid while the only terms are `hegemony_target_mod` (max `-20`) and `bilateral_betrayal_mod` (max `-18` under normal hard-reject blocking). **B-B4's DG-4 `grievance_modifier` (§8.8.9: `-30 per active grievance`, stacking across defensive-call refusals) breaks this invariant.** Three grievances alone reach `-90`; compounded with hegemony `-20` and betrayal `-18` the raw score reaches `-128`.

**Required ordering (one of):**

- **Option A — preferred: B-B4 lands AFTER or SIMULTANEOUSLY with B-B1-lite.** B-B1-lite ships the no-floor collapse; B-B4 then re-introduces the composite floor (`-60`, per spec §9.3 with-DG-4 clause) together with the `grievance_modifier` term and the per-pair grievance stacking cap (3 grievances per pair). The floor is rarely reached in normal play because hard-reject blocks before stacking saturates, but the floor is defensive and non-negotiable once `grievance_modifier` is live.

- **Option B — acceptable if sequencing forces it: B-B4 lands BEFORE B-B1-lite.** B-B1-lite's formula-collapse work must NOT delete the v2.3 composite-floor logic while `grievance_modifier` is already live in code; instead, narrow the floor to exactly the three-term case (`hegemony_target_mod` + `bilateral_betrayal_mod` + `grievance_modifier`) with the same `-60` bound, and remove only the *explanatory surface* of the old composite aggregation.

**Prohibited ordering:** under no circumstance may B-B1-lite ship alone with the no-floor claim while B-B4's `grievance_modifier` term is live in code. This produces unbounded negative scores on the §8.7 survival-exception path and makes the acceptance-formula debug output deceptive (component sums inconsistent with the stored composite value). The v2.4.2 deep audit (`MEMORY_AND_PRESSURE_V2_4_2_DEEP_AUDIT.md` A2) flagged this as a critical cross-slice ordering constraint; treat it as a merge gate, not a style preference.

Recommended playtest gates:

- **After B-Hegemony:** verify France-bloc share calculation tracks treaty/vassal changes correctly; same-turn named-court beats fire at `33 / 50 / 60`; passive threat accrues at 35%+ share; coalition leader emerges as Britain (highest bloc-share-against) when France hits 40%+; pressure stops when France releases a vassal; peaceful `50-55%` France reaches `BREWING` in roughly `12-16` turns if ignored; a cold-start run that drifts into the mid-20s before `BREWING` forces retune before close.
- **After B-B1-lite:** verify proposal acceptance reflects hegemony pressure (Britain refuses deep treaties from Bavaria when France is hegemon; Bavaria-Russia still possible); bilateral betrayal modifier scales correctly; representative regression scores within tolerance band; betrayal-driven warnings cite remembered referents when metadata exists.
- **After B-B4:** verify grievance-variant Make Amends clears only grievance flags at `400g + 2 DP`, defensive refusal terminates the existing alliance with `defensive_refusal_termination`, and the R9/R10/R11 playtest checks are explicitly reviewed before slice close.
- **After B-B3 + Slice C-lite:** verify the renamed paradox surfaces through the new dedicated popup; named-diplomat copy lands for three live events; Balance of Europe headline reads naturally; threshold beats at `33 / 50 / 60` and `amends_offered` notices both resolve the correct court voice.
- **After B-B7:** verify Make Amends succeeds at 200g + 1 DP and removes 1 strike; verify the target court's named acknowledgment appears on success; verify `amends_offered` lands on the lightweight notice / ledger route; verify all four refusal paths deliver Talleyrand-voiced advisory; verify 10-turn cooldown persists through save/load.

Slice D stays deferred unless playtest proves the v0.1 pressure layer still lacks political texture or non-French hegemon scenarios become possible sooner than expected.

---

## Code-Fix Tasks (carried from v2.3 — implementation session picks up)

| ID | Description | File |
|----|-------------|------|
| F1 | Tighten `determine_ai_offer_decision_reason` / `determine_counterparty_decision_reason` fallback from `rival_pressure` catch-all to `unknown_baseline` (per spec §10.1) | `backend/game_logic/diplomacy.py` |
| F2 | Verify `next_episode_id` resets cleanly on `/new_game` | `backend/main.py` (new_game handler), `backend/models/world_state.py` |
| F3 | Replace text-sort tie-break in `_sort_structured_warnings` with stable emit-sequence index | `backend/game_logic/diplomacy.py:263-272` |
| F4 | Regression test only — `_betrayal_key(actor, victim)` keys by nation, so strikes already follow vassal release/assimilation. Add a test asserting strikes survive the vassal transition. | `tests/`, `backend/game_logic/vassal.py`, `backend/game_logic/diplomacy.py` |
| F5 | Drop the `applied_reliability_delta == 0` warning case where text reads "Reliability would fall from 10 to 10" — show "(no penalty applied — cascade)" instead | `backend/game_logic/diplomacy.py:_build_breach_warnings` |

---

## Test Budget Comparison

| Slice | v1.0 estimate | v2.3 estimate | v2.4 estimate | v2.4.3 estimate | Notes |
|-------|---------------|---------------|---------------|-----------------|-------|
| A1 | 18 | shipped | shipped | shipped | Done |
| A2 | 14 | 4 (fill only) | shipped (fill cancelled) | shipped | Replaced by Balance headline in Slice C-lite |
| A1-fill (v2.0) | — | 8 | **0 (cancelled)** | **0 (cancelled)** | Replaced by hegemony engine |
| **B-Hegemony (v2.4 rescope)** | — | — | 12 | **24-30** | + threshold beats, tiny band-memory field, and bandwagon AI trigger |
| B1 | 24 | 14 | 6 (B1-lite) | **8-9 (B1-lite)** | + preview-pipeline hegemony warning test |
| B2a | 14 | shipped + 10 (fill) | shipped (fill cancelled) | shipped | Captured by hegemony pressure naturally |
| B2b | 24 | shipped | shipped | shipped | Done |
| B6 (v2.0) | — | 5 | **0 (cancelled)** | **0 (cancelled)** | Redemption tick cut; risk R7 tracks re-opening |
| B7 (v2.1) | — | 8 | 8 | 9 | + named-diplomat acknowledgment on success |
| B3 | 16 | 3 | 3 | 3 | Paradox rename — unchanged |
| C1a / C1b / C2 | 22 + 32 + 44 = 98 | moved | moved | moved | → `WAR_BARGAIN_SPEC.md` |
| Slice C (C3-lite) | (covered by C3a + C3b ~30) | 16-22 | 10-12 (trimmed) | 12-14 | + Balance-of-Europe threshold-beat copy / attribution |
| §8.8 DG-4 (B-B4) | — | 25 | 25 | **25-29** | Parallel slice; v2.4.3 adds grievance-variant Make Amends, defensive-refusal termination, and R9/R10/R11 gate coverage |
| Slice D | deferred | deferred | deferred | deferred | Same |
| **Total this phase** | **~200** | **~68-74** | **~35-42** | **~53-62** | (+25-29 DG-4 if shipped together = ~78-91) |

---

## Key Dependencies

| Session | Depends On | Why |
|---------|-----------|-----|
| B-Hegemony | A1 (✓), `coalition.py` threat ladder (✓) | Adds passive contribution to existing scalar |
| B-B1-lite | B-Hegemony | Acceptance formula reads bloc geometry |
| B-B3 (rename) | A1 (✓) | Pure rename, no new state |
| B-B7 (Make Amends) | A1 (✓), B-B1-lite (formula reads `reparations_cooldown`) | Standalone verb |
| Slice C-lite | B-B3, B-Hegemony | Needs renamed paradox + bloc data for Balance headline |
| B-B4 (DG-4) | A1, A2, B2a, B2b (all ✓), merge ordering with B-B1-lite | Parallel slice, but no longer independent once `grievance_modifier` and the composite-floor interaction are live |
| Slice D1 / D2 | This phase complete | Deferred follow-up |
| Slice WB-* | This phase complete + Bilateral Peace Hardening + War Purpose | See `WAR_BARGAIN_SPEC.md` |
