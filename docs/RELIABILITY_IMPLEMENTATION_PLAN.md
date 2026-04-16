# Memory and Pressure — Implementation Plan

> **Spec:** `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.0 (renamed from "Reliability + Commitments" to "Memory and Pressure" in the April 16, 2026 rescope)
> **Created:** April 13, 2026
> **Last Updated:** April 16, 2026 (v2.0 rescope — bargain slices moved to `WAR_BARGAIN_SPEC.md`)
> **Sessions remaining:** ~3 effective on the critical path (Slice A/B folds into one session; Slice C splits into one Godot-surfaces session + one tests-and-mock-prose session per §Slice C below)
> **Est. tests remaining:** ~60-66 (slice-level sum: A1-fill 8 + A2-fill 4 + B1 14 + B2a-fill 10 + B6 5 + B3 3 + Slice C 16-22; down from ~200 in v1.0 — bargain test budget moved to bargain spec)

---

## v2.0 Rescope Summary

The April 16 audit established what the substrate had actually shipped vs what the v1.0 spec claimed:

**Already shipped (in current `master`):**

- Slice A1 (data model + serialization): `betrayal_history`, `next_episode_id`, `commitment_event_metadata`, `to_dict` / `from_dict`, save-format reference. ✓
- Slice A2 partial (ledger + preview scaffolding): structured `warnings[]`, breach preview with reliability + applied-vs-intended deltas, `force_break_treaty_confirmation` / `force_declare_war_confirmation` hard-stops with warnings, `commitment_paradox` HARD_STOP type registration (placeholder). ✓
- Slice B2a (third-party anger metadata + breach recording): cascade-rupture fault attribution, episode_id threading, `end_reason_family` / `end_reason_action` / `fault_nation` split, witness_strike_recorded dispatch emit per witness. ✓
- Slice B2b (witness scoping + episode cap + redemption decay + hard-reject): per-witness `scope_reason` precedence, episode-strike cap of 2, severity-scaled bilateral strike decay (strike-removal half), `hard_reject_posture_triggered` / `_cleared` emits with first-cross-only contract, hard-reject acceptance gate. ✓
- AI `decision_reason` subset (5 enum values out of v1.0 set) wired into proposals, counterparty responses, campaign log, popups. ✓

**Not shipped (this plan covers what's left):**

- Slice A1-fill: rivalry seed (`nation_rivalries` dict + 3 authored pairs)
- Slice B1: acceptance formula additions (`direct_rivalry_mod`, `rival_conflict_mod`, graduated `bilateral_betrayal_mod`, composite `political_commitment_mod` with `-40` floor)
- Slice B2a-fill: third-party anger applied at ratification (the relation-hit half of B2a — currently only the breach-time witness payload is emitted)
- Slice B6 (new): redemption tick (`actor_honored_turns` + 5-turn / +3 reliability award)
- Slice B3-rename: rename `alliance_paradox` push type to `commitment_paradox` (legacy alias on read)
- Slice C: C3-lite presentation pass (separate spec — see `COMMITMENTS_PRESENTATION_SPEC.md` v0.3)

**Moved to `WAR_BARGAIN_SPEC.md`:**

- Slice C1a / C1b / C2 (war bargains, lifecycle, war-entry integration) → `WAR_BARGAIN_SPEC.md` slices WB-A / WB-B / WB-C
- All bargain-specific tests (~80-90 tests in v1.0 budget)
- All bargain-specific surface contracts (`fulfillment_snapshot`, `pending_declaration`, `join_opportunity`, `counter_bargain_context`, Bargain Review)

**Deferred (unchanged):**

- Slice D1 (advisory-first strategic focus + deeper AI integration)
- Slice D2 (coalition buildout + generalization)

---

## Slice A. Foundations (mostly shipped)

### A1. Data model + serialization (SHIPPED)

**Files:** `backend/models/world_state.py`, `docs/SAVE_FORMAT_REFERENCE.md`

- ✓ `betrayal_history: Dict[str, Dict]` with `StrikeRecord` shape (severity, turn, episode_id, decays_on_turn)
- ✓ `next_episode_id: int` allocator counter
- ✓ `to_dict` / `from_dict` round-trip with `.get()` defaults
- ✓ `SAVE_FORMAT_REFERENCE.md` updated
- ✓ Save-migration regression test against pre-commitments fixture

### A1-fill. Rivalry seed (THIS PHASE)

**Files:** `backend/models/world_state.py`, `backend/nation_config.py` (or wherever scenario seed lives), `docs/SAVE_FORMAT_REFERENCE.md`

- Add `nation_rivalries: Dict[str, Dict]` to WorldState (key: `diplo_key`; value: `{intensity, source, weight, started_turn, last_changed_turn}`)
- Initialize on world init / `/new_game` reset:
  - `France|Britain` → `{intensity: "active", source: "authored", weight: "primary"}`
  - `Austria|Prussia` → `{intensity: "active", source: "authored", weight: "primary"}` (use canonical sort for diplo_key)
  - `Prussia|Saxony` → `{intensity: "cold", source: "authored", weight: "secondary"}`
- Add `actor_honored_turns: Dict[str, int]` for Slice B6 redemption tick
- `to_dict` / `from_dict` for both new fields
- Update `SAVE_FORMAT_REFERENCE.md`
- Add per-turn cached helper `get_active_rivalries_for(nation)` returning rivals with intensity (per CLAUDE.md golden rule 8)
- ~8 tests (seed shape, serialization round-trip, helper cache invalidation, Prussia-Saxony auto-escalation triggers per §7.1)

### A2. Ledger + preview scaffolding (SHIPPED partial)

**Files:** `backend/game_logic/diplomatic_ledger.py`, `backend/game_logic/diplomatic_dialogue.py`, `backend/main.py`, `backend/display_names.py`, `godot-client/.../diplomatic_ledger.gd`, `godot-client/.../proposal_confirm_popup.gd`, `godot-client/.../main.gd`

- ✓ Display-name maps for betrayal severity, warning categories
- ✓ Reliability descriptor + bilateral betrayal warning on Talleyrand tab
- ✓ Canonical `warnings[]` / Political Context preview payload scaffolding (`hard_reject`, `betrayal`, `rivalry`, `peace_conflict`)
- ✓ Severity ordinals + stable category ordering in shared formatter contract
- ✓ Debug endpoint for betrayal / hard-reject state inspection

**Remaining for this phase:**

- Add rivalry display to Diplomatic Ledger Nations tab (depends on A1-fill)
- Add display-name maps for rivalry intensity (`primary active`, `secondary active`, `secondary cold`)
- ~4 tests (ledger formatting, display-name wiring)

---

## Slice B. Rivalry pressure

### B1. Acceptance formula modifiers (THIS PHASE)

**Files:** `backend/game_logic/diplomacy.py`, `backend/display_names.py`

The biggest single behavior change in this phase. The substrate already counts strikes; the formula must read them.

- Add `direct_rivalry_mod` to `calculate_acceptance()` per spec §9.1 with primary vs secondary weighting
- Add `rival_conflict_mod` per spec §9.2 (treaty-alignment-with-target's-rival; bargain-conflict add-on stays in `WAR_BARGAIN_SPEC.md`)
- Add `bilateral_betrayal_mod = -8 per active strike, cap -24` per spec §9.3 — **replaces the current binary hard-reject-only behavior**
- Group all under `political_commitment_mod = max(-40, raw)` per spec §9.4
- Preserve old static sweeteners only when graded rivalry/betrayal data does not apply
- Wire debug breakdown output (`components` dict) and `feedback` strings (`FEEDBACK_STRINGS`) to surface the new modifiers
- Tighten `reliability_modifier` to spec §10.5 baseline: `clamp(diplomatic_reliability[proposer] // 10, -6, +6)` — current code is `// 5` capped ±10 (legacy R34); narrowing keeps reliability a light input so bilateral memory dominates
- Add regression tests comparing representative pre-change proposal scores against expected tolerance bands so we don't accidentally push prior balance into REJECT/ACCEPT
- ~14 tests (primary vs secondary values, capped stacking, graduated betrayal, composite floor, edge cases, regression coverage)

### B2a. Third-party anger metadata (SHIPPED) + ratification anger (THIS PHASE)

**Files:** `backend/models/world_state.py`, `backend/game_logic/diplomacy.py`, `backend/commands/diplomatic_executor.py`, `backend/game_logic/dispatch.py`

**Already shipped:**

- ✓ Compute witness scope on breach + emit `witness_strike_recorded` dispatch per witness with `scope_reason`
- ✓ Beneficiary-first explicit reversal classified as `counterparty_reversal` metadata
- ✓ French-engineered treaty auto-decay tagged as constructive breach (rather than void)
- ✓ Dispatch entries for rivalry escalation, betrayal recorded, counterparty reversal, reliability change

**This phase ships:**

- **B2a-fill: ratification anger.** On treaty ratification, compute rival anger and apply relation penalties per spec §7.4.B:
  - hit applies to each `active` rival of the deepening target
  - half-value (rounded toward zero) for `cold` rivals
  - `VASSAL`-of-rival's-rival gets immediate full hit, then run authored Prussia-Saxony escalation rule
  - apply rival-reaction relation hit immediately on ratification; let normal downgrade / auto-downgrade rules handle subsequent fallout (no forced instant-break logic)
- ~10 tests (active vs cold scaling, vassal-of-rival's-rival, no-self-reaction, episode_id sharing, dispatch entry shape)

### B2b. Witness scoping + episode cap + decay + hard-reject (SHIPPED)

**Files:** `backend/models/world_state.py`, `backend/game_logic/diplomacy.py`, `backend/game_logic/dispatch.py`

- ✓ Witness penalty logic: only allies of victim, active rivals of betrayer, directly implicated shared-enemy observers; one resolved `scope_reason` per witness using spec precedence
- ✓ Episode boundaries by root-cause `episode_id`, not by whole `advance_turn()`
- ✓ Per-episode victim strike cap of 2 across all consequences from that trigger
- ✓ Severity-scaled bilateral strike decay (strike-removal half)
- ✓ Strike age matures during `WAR` / `ARMISTICE`; actual removal only while non-war treaty restored
- ✓ Hard-reject behavior: 3 victim-side strikes → hard resist deep treaties; survival exception narrow
- ✓ `hard_reject_posture_cleared` emit when pair falls from 3+ active back to 2 or fewer
- ✓ Preview plumbing for `hard_reject` warnings when an action would create strike 3
- ✓ Prussia↔Saxony hardcoded escalation triggers (data-side; activated by §7.1 seed in A1-fill)

### B6. Redemption tick (NEW THIS PHASE)

**Files:** `backend/models/world_state.py`, `backend/game_logic/diplomacy.py`, `backend/game_logic/turn_manager.py`

The substrate decays betrayal strikes (the punishment side). v0.1 also wants the carrot: actors who keep their word should slowly recover global reliability.

- Use the `actor_honored_turns: Dict[str, int]` field added in A1-fill
- During `advance_turn()`:
  - For each actor: if the actor ends the turn with at least one qualifying non-`WAR` treaty honored AND no new betrayal offense created this turn, increment `actor_honored_turns[actor]`
  - When `actor_honored_turns[actor]` reaches 5, award `+3` to `diplomatic_reliability[actor]` and reset the counter to 0
- Once-per-actor on a single global clock (not per-pair)
- Strike decay (the punishment side) stays separate
- ~5 tests (counter increment, qualifying-turn definition, +3 award, reset, no-double-count when multiple non-war treaties exist)

### B3. Commitment paradox (RENAME — THIS PHASE)

**Files:** `backend/commands/diplomatic_executor.py`, `backend/game_logic/diplomacy.py`, `backend/models/dialogue_manager.py`, `godot-client/.../main.gd`, `godot-client/.../alliance_paradox_popup.gd` (rename to `commitment_paradox_popup.{tscn,gd}` per Slice C)

- Spec §7.5 rivalry-driven ratification paradox is **deferred** to `WAR_BARGAIN_SPEC` slice WB-C (it depends on bargain conflicts to feel important; without bargains it would only fire on the legacy condition).
- This phase: rename the push-side dialogue type from `"alliance_paradox"` to `"commitment_paradox"` in the existing alliance-cross-war paradox flow (`backend/game_logic/diplomacy.py:2135`).
- Keep `"alliance_paradox"` as a read-side alias for save-load back-compat: when loading old saves, treat `alliance_paradox` dialogue type as `commitment_paradox`.
- HARD_STOP_TYPES already lists `commitment_paradox` as a placeholder (since April 15 substrate work) — this rename activates that registration.
- The dedicated `commitment_paradox_popup.{tscn,gd}` Godot surface ships in Slice C (presentation pass) — until then, the existing `alliance_paradox_popup` continues to render the renamed type.
- Preserve all the existing fallout-preview behavior (`origin_episode_id` continuity, `commitment_paradox_resolved` log + dispatch event with `chosen_nation` / `spurned_nation`).
- ~3 tests (rename smoke test, alias load test, no double-emit on rename)

---

## Slice C. C3-lite presentation pass

See `COMMITMENTS_PRESENTATION_SPEC.md` v0.3.

This slice lands the four C3a-pre prerequisites and the narrowed drama scope:

1. **Spotlight tier.** `notification_bar.gd` gains an elevated card variant (2-turn persist, action buttons) above ordinary notice tiers.
2. **Split-voice render.** Notice / popup scenes gain support for `attributed_lines[]` blocks (`lead` / `witness` / `aside` regions with distinct visual weight per spec §9.1).
3. **Named-diplomat resolution.** Single backend helper that reads `world.diplomats[nation]` and resolves `speaker="envoy"` to the named diplomat with their personality register, and `speaker="foreign_office"` to "The Chancery of {nation}". Per `DIPLOMAT_VOICE_BIBLE.md`.
4. **Dedicated `commitment_paradox_popup.{tscn,gd}`.** Replaces the legacy `alliance_paradox_popup` for the renamed type. Three regions for the staged paradox (Talleyrand framing → blocking body → after-choice aside).

Spotlight routed on (this phase): `hard_reject_posture_triggered`, `diplomatic_treaty_broken` where `end_reason_family=french_breach`, `commitment_paradox_resolved`. Three events.

Other deferred-from-v1.0 contract items (per `COMMITMENTS_PRESENTATION_SPEC.md` v0.3):

- One N+1 Talleyrand aside keyed by `episode_id` for hard-reject and breach
- Committed mock prose for the three live events using Voice Bible registers
- Cut response routes (`Propose redress` etc.) — defer to `WAR_BARGAIN_SPEC` slice WB-D

Estimated ~16-22 tests across **two sessions**:

1. **Godot surfaces session** — new `commitment_paradox_popup.{tscn,gd}`, split-voice render capability in `notification_bar.gd`, elevated-card spotlight tier, HARD_STOP dtype whitelist routing for the renamed type.
2. **Tests + mock prose session** — named-diplomat resolution helper, committed prose for the three live events (`hard_reject_posture_triggered`, `diplomatic_treaty_broken` french_breach, `commitment_paradox_resolved`), ledger emphasis wiring, N+1 aftermath callback.

Detailed breakdown in `COMMITMENTS_PRESENTATION_SPEC.md` §14.

---

## Slice D. Deferred follow-up (unchanged)

### D1. Advisory-first strategic focus + deeper AI integration

Same as v1.0:

- Strategic-focus layer for AI phrasing + Talleyrand recommendations
- Dynamic power scoring and tiers
- Richer rival-aware agenda logic
- Performance: no new per-region scans, use cached rivalry and bargain lookups

Not counted in the v0.1 commitments session budget.

### D2. Coalition buildout and generalization

Same as v1.0:

- Lift current anti-France coalition assumptions into generic coalition identity / target tracking
- Build on the `(actor, victim)` parameterized helpers shipped in Memory and Pressure substrate
- Define coalition-vs-alliance overlap hooks for powers other than France
- Keep coalition loyalty / separate-peace logic distinct from treaty acceptance and bargain sweetening

Not counted in the v0.1 commitments session budget.

### Slice WB-* (deferred to Peace Deals phase)

War bargain implementation moved to `WAR_BARGAIN_SPEC.md`:

- WB-A: data model + creation + validation
- WB-B: lifecycle (fulfillment + breach + void)
- WB-C: war-entry integration + Bargain Review + AI rules
- WB-D: bargain-era presentation extension

---

## Execution Order (this phase)

```text
A1 (✓) -> A1-fill (rivalry seed) -> B1 (formula) -> B2a-fill (ratification anger)
                                  -> B6 (redemption tick)
                                  -> B3 (paradox rename)
A2 (partial ✓) -> A1-fill -> A2 ledger rivalry display
B3 (rename) -> Slice C (C3-lite presentation, including dedicated paradox popup)
```

Recommended playtest gates:

- **After A1-fill + A2 fill:** verify rivalry display appears in ledger; rivalry data round-trips through save/load.
- **After B1:** verify proposal acceptance reflects rivalry pressure and graduated betrayal; representative regression scores within tolerance band.
- **After B2a-fill:** verify ratifying a deep treaty with Britain triggers Prussia-Austria-rival anger relations dropping; cold rivals scale to half.
- **After B6:** verify keeping all treaties for 5 honored turns awards +3 reliability once.
- **After B3 + Slice C:** verify the renamed paradox surfaces through the new dedicated popup; mock prose lands; spotlight tier reads as different from notice tier.

Slice D stays deferred unless playtest proves the v0.1 pressure layer still lacks political texture or coalition overlap remains too muddy in play.

---

## Code-Fix Tasks (no implementation in this rescope; queued for the implementation session)

These are small fixes the April 16 audit flagged. Not gating the rescope; gathered here so the implementation session picks them up.

| ID | Description | File |
|----|-------------|------|
| F1 | Tighten `determine_ai_offer_decision_reason` / `determine_counterparty_decision_reason` fallback from `rival_pressure` catch-all to `unknown_baseline` (new enum value per spec §10.1) when no real pressure is computed | `backend/game_logic/diplomacy.py` |
| F2 | Verify `next_episode_id` resets cleanly on `/new_game` (currently relies on `WorldState.__init__`; `/new_game` should re-init or explicitly reset) | `backend/main.py` (new_game handler), `backend/models/world_state.py` |
| F3 | Replace text-sort tie-break in `_sort_structured_warnings` with stable emit-sequence index | `backend/game_logic/diplomacy.py:263-272` |
| F4 | Vassal strike-decay edge: ensure strike memory follows the nation when a vassal is released or assimilated | `backend/game_logic/vassal.py`, `backend/game_logic/diplomacy.py` |
| F5 | Drop the `applied_reliability_delta == 0` warning case where text reads "Reliability would fall from 10 to 10" — show "(no penalty applied — cascade)" instead | `backend/game_logic/diplomacy.py:_build_breach_warnings` |

---

## C3 Cross-Cutting Contract Additions (preserved from v1.0)

These additions were filed against existing slices to unblock the C3 presentation pass. They are already shipped:

### Against B2a (SHIPPED)

- ✓ `witness_strike_recorded` dispatch event with `episode_id`, `victim_nation`, `perpetrator_nation`, `witness_nation`, `scope_reason` (one of `ally` / `rival` / `shared_enemy` / `region_observer`), `relation_delta`, `reliability_delta = 0`, `turn`
- ✓ `counterparty_reversal_recorded` metadata for beneficiary-first explicit reversals

### Against B2b (SHIPPED)

- ✓ `hard_reject_posture_triggered` first-cross-only emit per `(victim_nation, perpetrator_nation)`
- ✓ `hard_reject_posture_cleared` matching emit on first fall back to ≤2 strikes

### Against C1b (`fulfillment_snapshot` extension) — DEFERRED

Moved to `WAR_BARGAIN_SPEC.md` along with the bargain mechanic.

### Against C2 (`pending_declaration` enumeration) — DEFERRED

Moved to `WAR_BARGAIN_SPEC.md` along with the war-entry contract.

---

## Key Dependencies

| Session | Depends On | Why |
|---------|-----------|-----|
| A1-fill | A1 (✓) | Adds new fields next to existing substrate |
| A2 fill | A1-fill | Ledger reads new rivalry data |
| B1 | A1, A1-fill | Acceptance reads rivalry + betrayal stores |
| B2a-fill | A1-fill | Rival anger needs rivalry data |
| B6 | A1, A1-fill (`actor_honored_turns`) | Redemption tick needs the per-actor counter |
| B3 (rename) | A1 | Pure rename, no new state |
| Slice C | B3, A1-fill | Presentation reads renamed type and rivalry data; landing the dedicated paradox popup is part of this slice |
| Slice WB-* | This phase complete + Bilateral Peace Hardening + War Purpose | See `WAR_BARGAIN_SPEC.md` |
| D1 / D2 | This phase complete | Deferred follow-up only |

---

## Test Budget Comparison

| Slice | v1.0 estimate | v2.0 estimate | Notes |
|-------|---------------|---------------|-------|
| A1 | 18 | shipped | Done |
| A2 | 14 | 4 (fill only) | Display-name + ledger row addition |
| A1-fill (NEW) | — | 8 | Rivalry seed |
| B1 | 24 | 14 | Trimmed: no `bargain_value_mod` test paths |
| B2a | 14 | shipped + 10 (fill) | Half shipped (metadata); fill is ratification anger |
| B2b | 24 | shipped | Done |
| B6 (NEW) | — | 5 | Redemption tick |
| B3 | 16 | 3 | Trimmed: rivalry-driven paradox deferred; this is pure rename |
| C1a / C1b / C2 | 22 + 32 + 44 = 98 | moved | → `WAR_BARGAIN_SPEC.md` |
| Slice C (C3-lite) | (covered by C3a + C3b ~30) | 16-22 | One slice, narrower scope |
| Slice D | deferred | deferred | Same |
| **Total** | **~200** | **~60-66 remaining** | Plus ~98 moved to `WAR_BARGAIN_SPEC.md` |
