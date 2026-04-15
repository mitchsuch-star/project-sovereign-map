# Commitments Presentation Spec — Audit Findings (Tracked)

> **Status:** Open. Created Apr 15, 2026. Gates approval of `COMMITMENTS_PRESENTATION_SPEC.md` as `C3` in the reliability/diplomacy refinement stack.
> **Method:** 1 initial audit pass + 3 parallel verification agents against ground-truth spec + code. Each finding labeled SURVIVES / WEAKENED / FALSIFIED. New adjacent findings surfaced during verification are appended.

---

## Score

- **Original findings:** 2 Critical, 4 High, 5 Medium = 11.
- **Verification outcome:** 10 SURVIVES, 1 WEAKENED (M-2), 0 FALSIFIED.
- **New adjacent findings (from verification sweep):** 13 — 2 High, 5 Medium-High, 6 Medium/Low.
- **Total tracked items:** 24.
- **Verdict:** Spec is not safe to approve as-placed without addressing all Critical and High items (8 total). Mediums should be folded in before ship but are not blockers.

---

## 1. Critical Findings (Blockers)

### C-1 — Dispatch spotlight surface ownership collides with two live contracts
**Status:** SURVIVES.
**Evidence:**
- `docs/COMMITMENTS_PRESENTATION_SPEC.md:254` §9.1 says "use the existing Morning Dispatch delivery path."
- `backend/game_logic/dispatch.py:33,129` — `build_morning_dispatch()` is called only at turn start, writes `world.last_morning_dispatch`. No mid-turn injection API.
- `godot-client/project-sovereign/scripts/dispatch_view.gd:1-52` — read-only re-read surface.
- `docs/INFORMATIONAL_UI_PLAN.md:94-120` §A — informational diplo feedback already routed to persistent notice rail.
- A mid-turn `bargain_breached` cannot hit either surface.

**Fix direction:** Rewrite §7.2/§9.1 to either (a) route spotlights through the notice rail with an elevated "spotlight" style, reusing `INFORMATIONAL_UI_PLAN` contract, or (b) explicitly defer spotlights to next-turn Morning Dispatch cards with in-turn notice as the immediate surface. Do not leave "existing Morning Dispatch path" ambiguous.

### C-2 — `hard_reject_posture_triggered` is a state, not an event — engine contract missing
**Status:** SURVIVES.
**Evidence:**
- `COMMITMENTS_PRESENTATION_SPEC.md:196,208,228,439-453` treats it as a first-time-fireable spotlight event.
- `RELIABILITY_COMMITMENTS_SPEC.md:447-462,994` describes hard-reject only as posture/state at 3 strikes — "AI hard resistance to deep treaties."
- `RELIABILITY_IMPLEMENTATION_PLAN.md:84` (B2b) is a behavioral rule, no emit contract, no first-time-crossing detector.
- `RELIABILITY_IMPLEMENTATION_PLAN.md:71,137` dispatch event lists do not include `hard_reject_posture_triggered`; `RELIABILITY_COMMITMENTS_SPEC.md:1167-1175` §12.5 "high-signal events" also omits it.

**Fix direction:** Either (a) file an add against B2b ("emit `hard_reject_posture_triggered` with fields on first threshold crossing per victim") and mark C3 blocked on it, or (b) downgrade to a derived notice computed from the strike transition, drop the "state change spotlight" framing.

---

## 2. High Findings

### H-1 — Counter-bargain Accept / Reject / Back Out treated as interchangeable
**Status:** SURVIVES.
**Evidence:**
- `COMMITMENTS_PRESENTATION_SPEC.md:200,236-246` §8.1+§8.4 collapse all three into one row with "no duplicate notice."
- `RELIABILITY_COMMITMENTS_SPEC.md:739-741,754,1156` assigns distinct mechanical outcomes; Back Out cancels `pending_declaration` entirely.

**Fix direction:** Add one row per terminal outcome in §8.1 with explicit ledger + campaign-log emission rules; reference `pending_declaration` cancel-vs-continue semantics.

### H-2 — §11 payload missing `episode_id` that §13 collapse rule silently requires
**Status:** SURVIVES.
**Evidence:**
- `COMMITMENTS_PRESENTATION_SPEC.md:373-390` (§11 example) — no `episode_id`.
- `COMMITMENTS_PRESENTATION_SPEC.md:478` (§13) — collapse rule requires root key.
- `RELIABILITY_COMMITMENTS_SPEC.md:375-379` (§8.3) defines `episode_id` as episode-boundary key.

**Fix direction:** Add `episode_id` to §11 payload example; state in §13 that collapse keys off it.

### H-3 — One-turn emphasis cap is commitments-local, ignores rail co-tenants
**Status:** SURVIVES.
**Evidence:**
- `COMMITMENTS_PRESENTATION_SPEC.md:218-234` §8.3 — cap is commitments-scoped.
- `INFORMATIONAL_UI_PLAN.md:96-120,194-200` — notice rail already shared with `coalition_declaration`, `proposal_result`.
- `notification_bar.gd:13` — `MAX_VISIBLE_ICONS := 6`, not co-tenancy-aware.
- `backend/notifications.py:87` — `NOTIFICATION_CAP = 50`, no per-turn budget.

**Fix direction:** Restate §8.3 as "within rail's existing budget"; defer rail-wide cap to `INFORMATIONAL_UI_PLAN` ownership; add non-goal row.

### H-4 — `top_reason_text` / "strongest negative factor" assumed but not in C2
**Status:** SURVIVES strongly.
**Evidence:**
- `COMMITMENTS_PRESENTATION_SPEC.md:348-350,387` (§10.4, §11) rely on these fields.
- `RELIABILITY_IMPLEMENTATION_PLAN.md:170-171` (C2) promises only "hard-block reason surfacing" and `war_entry_score` *inputs* — no top-factor synthesizer.
- `RELIABILITY_COMMITMENTS_SPEC.md:1111-1137` §12.2 — `warnings[]` is severity-sorted, not top-factor-reduced.

**Fix direction:** Either file the add against C2, or drop `top_reason_text` and compose from `warnings[]`.

### NEW-E1 (High) — `fulfillment_snapshot` missing narrative/voice fields
**Evidence:**
- `COMMITMENTS_PRESENTATION_SPEC.md:410` relies on fulfillment data; §12.1 relies on narrative.
- `RELIABILITY_IMPLEMENTATION_PLAN.md:118,130,138` (C1a/C1b) specifies snapshot only as mechanical fields: claim region, beneficiary, target enemy, fulfilled turn, reward deltas, caps.
- §11 payload fields `relation_delta`, `reliability_delta`, `witness_nations` are not all in C1b snapshot contract.

**Fix direction:** Extend fulfillment_snapshot contract in C1b with narrative-ready fields, or specify at emit time.

### NEW-E2 (High) — `pending_declaration` transaction schema undefined
**Evidence:**
- `RELIABILITY_IMPLEMENTATION_PLAN.md:155` (C2) says "serialize staged declaration … primitive `pending_declaration` payload keyed by `declaration_transaction_id`" but enumerates no fields.
- `COMMITMENTS_PRESENTATION_SPEC.md` §12.4 ally-entry hard-block and §8 routing assume enough structured data for inline rendering.
- Save/load resume test at C2:192 depends on an unspecified shape.

**Fix direction:** Enumerate `pending_declaration` fields in C2 before C3 ships.

---

## 3. Medium Findings

### M-1 — Ledger badges §9.3 undefined source of truth
**Status:** SURVIVES.
**Evidence:** `COMMITMENTS_PRESENTATION_SPEC.md:282-291` names "recent-success/recent-breach/closed-door" badges with "short window" but no data source; `backend/game_logic/diplomatic_ledger.py` has no `recent`, `badge`, `emphasis`, or `turn_created` fields.
**Fix:** Specify "derive from campaign log entries with turn >= current_turn - N" with a concrete N.

### M-2 — Talleyrand voice ownership clarity gap (not a true conflict)
**Status:** WEAKENED.
**Evidence:** `CONVERSATIONAL_DIPLOMACY_DESIGN.md:392-433` owns template library at `diplomatic_templates.py:1795`; spec §10.1-10.2 already cedes authority to templates; task list `:486-497` names `diplomatic_templates.py`. No hard conflict — just missing template-family id.
**Fix:** Name the commitments template family explicitly (e.g. `commitments_spotlight_*`) in §10 or the task list.

### M-3 — §15 Future Handoff implicitly makes this pass own the router
**Status:** SURVIVES (not re-verified; stands on initial reading).
**Fix:** Decide commitments-specific router (drop §15 handoff) vs diplomacy-presentation router (widen scope + rename).

### M-4 — Priority ranking tilts spotlight negative
**Status:** SURVIVES as written (§8.3 ranks hard-reject above fulfilled). Design call, not bug; justify or reorder.

### M-5 — §14 test list omits Back Out suppression test
**Status:** SURVIVES. Add test: "Back Out does not generate 'Prussia refused' line."

### NEW-S1 — `notification_bar.gd` TYPE_ICONS missing commitments types
**Evidence:** `notification_bar.gd:30-42` has no icons for `bargain_breached`, `bargain_fulfilled`, `hard_reject_posture_triggered`, `commitment_paradox`, `witness_strike_recorded`.
**Fix:** Enumerate icon/label mappings for all 7 new commitments types in §9.2 or a UI subsection.

### NEW-S2 — `review_target: "ledger_commitments"` has no backing sub-tab
**Evidence:** §11 payload names `review_target: "ledger_commitments"`; `diplomatic_ledger.gd` has 4 tabs (Nations/Treaties/Threat/Talleyrand) per CLAUDE.md — no commitments tab.
**Fix:** Either add a commitments sub-tab to the ledger as part of C3 scope, or retarget review action to an existing tab (Treaties most likely).

### NEW-S3 — Talleyrand voice has no render slot in rail detail panel
**Evidence:** `notification_bar.gd:265-304` uses generic posture/outcome formatting; §10.3 prescribes speaker-driven framing.
**Fix:** Add a speaker/attribution slot to notification detail render contract.

### NEW-S4 — Backend `NOTIFICATION_CAP` trims NORMAL first; CRITICAL priority alignment missing
**Evidence:** `notifications.py:87` trims oldest NORMAL; no priority rule for commitments events.
**Fix:** Specify priority tier per commitments event type in §9.2.

### NEW-E3 (Medium) — `witness_nations` flat list loses scoping classification
**Evidence:** §11 payload `:385` is flat; `RELIABILITY_COMMITMENTS_SPEC.md:394-404` §8.4 classifies witnesses by three scoping reasons.
**Fix:** Preserve scoping classification in payload (list of {nation, scope_reason}).

### NEW-E4 (Medium) — `witness_strike_recorded` event emission not contracted
**Evidence:** Spec references it at `:195,232,478`; `RELIABILITY_IMPLEMENTATION_PLAN.md:71` B2a promises only "rivalry escalation, betrayal recorded, reliability change" dispatch entries.
**Fix:** File emission contract against B2a or B2b.

### NEW-E5 (Low) — `relation_delta` / `reliability_delta` not sourced to any producer
**Evidence:** §11 payload fields; C1b dispatch events `:137` don't contractually carry numeric deltas.
**Fix:** Name source (strike delta field on record, or computed from snapshot).

### NEW-V1 — `campaign_log.py` missing 7 new event types
**Evidence:** `backend/campaign_log.py` has no entries for `bargain_fulfilled|breached|ratified|triggered|voided|witness_strike_recorded|hard_reject_posture_triggered`. CLAUDE.md pattern requires `CAMPAIGN_LOG_TYPES` registration.
**Fix:** Add to §14 task list explicitly.

### NEW-V2 — Back Out semantics undefined
**Evidence:** `RELIABILITY_COMMITMENTS_SPEC.md:741` says "pending war-state mutation is cancelled" but neither spec defines DP/AP refund behavior or re-entrancy.
**Fix:** Define in C2 or DIPLOMACY_SPEC before C3 ships Back-Out-specific tests.

### NEW-V3 — Speaker attribution for third-party witness events ambiguous
**Evidence:** §10.3 assigns Talleyrand default to spotlights, "neutral system headline" to notices. Witness strikes are by definition third-party-observer events — Talleyrand attribution risks voice bleed.
**Fix:** Carve out witness events explicitly.

### NEW-V4 — `commitment_paradox` routing conflicts with existing dialogue
**Evidence:** `COMMITMENTS_PRESENTATION_SPEC.md:199` routes paradox to "blocking hard-stop"; `CONVERSATIONAL_DIPLOMACY_DESIGN.md:126` already classifies it as a blocking dialogue type with its own hard-stop.
**Fix:** State whether paradox text is re-rendered via template or reused from existing dialogue.

---

## 4. Phase Placement Verdict

`post-C2 / pre-Bilateral-Peace-Hardening` is correct, but `C3` is not reflected in `RELIABILITY_IMPLEMENTATION_PLAN.md:222-232` execution order, and `DESIGN_REFINEMENT.md:44` references it only as playtest-gated optional. **Approval must include an edit to the implementation plan's execution-order block.**

---

## 5. Disposition (to be filled during fix pass)

| ID | Status | Spec section / file to change | Notes |
|----|--------|-------------------------------|-------|
| C-1 | CLOSED | §7.2, §9.1 | Pick surface; rewrite |
| C-2 | CLOSED | §8.1, §8.2, §12.3 + B2b | Downgrade or file engine add |
| H-1 | CLOSED | §8.1, §8.4 | Per-terminal rules |
| H-2 | CLOSED | §11, §13 | Add `episode_id` |
| H-3 | CLOSED | §8.3 | Rail-budget restatement |
| H-4 | CLOSED | §10.4, §11, C2 | Drop or file add |
| NEW-E1 | CLOSED | C1b `fulfillment_snapshot` | Extend contract |
| NEW-E2 | CLOSED | C2 `pending_declaration` | Enumerate fields |
| M-1 | CLOSED | §9.3 | Name source + N |
| M-2 | CLOSED | §10 or task list | Template family id |
| M-3 | CLOSED | §15 | Router ownership decision |
| M-4 | CLOSED | §8.3 | Justify or reorder |
| M-5 | CLOSED | §14 | Add test |
| NEW-S1 | CLOSED | §9.2 | Icon mappings |
| NEW-S2 | CLOSED | §9, §11 | Sub-tab or retarget |
| NEW-S3 | CLOSED | §10.3 | Render slot |
| NEW-S4 | CLOSED | §9.2 | Priority tier per type |
| NEW-E3 | CLOSED | §11 | Scoped witness payload |
| NEW-E4 | CLOSED | §8.1 + B2a/B2b | Emission contract |
| NEW-E5 | CLOSED | §11 | Source deltas |
| NEW-V1 | CLOSED | §14 task list | Register 7 types |
| NEW-V2 | CLOSED | C2 or DIPLOMACY_SPEC | Back Out semantics |
| NEW-V3 | CLOSED | §10.3 | Carve out witness events |
| NEW-V4 | CLOSED | §8.1 or §10.4 | Paradox re-render rule |
| Plan-sync | CLOSED | `RELIABILITY_IMPLEMENTATION_PLAN.md:222-232`, `DESIGN_REFINEMENT.md:44` | Name C3 in execution order |
