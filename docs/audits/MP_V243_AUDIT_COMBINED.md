# Memory and Pressure v2.4.3 Audit — Combined (Claude + Codex), 2026-04-20

> **Fusion of:**
> - [`MP_V243_AUDIT_CLAUDE.md`](docs/audits/MP_V243_AUDIT_CLAUDE.md) — claude-opus-4-7, spec-to-spec consistency focus (15 findings, 2 BLOCKER / 6 MAJOR / 7 MINOR).
> - [`MP_V243_AUDIT_CODEX.md`](docs/audits/MP_V243_AUDIT_CODEX.md) — GPT-5 Codex, spec-to-live-code reality check (8 findings, 3 BLOCKER / 4 MAJOR / 1 MINOR).
>
> This combined audit deduplicates overlapping findings, promotes Codex's live-code corroborations, and adds an effort / split-recommendation section not present in either source. Each finding tags its provenance (`[C]` = Claude, `[X]` = Codex, `[C+X]` = fused). Live-code anchors are verified against `master` @ 2a9ac4e.

---

## Executive summary

**Combined verdict: REQUEST-CHANGES (3 BLOCKERs, 7 MAJORs, 7 MINORs) across 17 unified findings.**

The two audits are complementary, not redundant. **Claude** reads the spec ensemble top-to-bottom and finds the v0.5.1 "non-normative bulk trim" (v2.4.2 C7) leaked past several sections — the worked examples in presentation §12 still prescribe spotlight/split-voice/N+1 rendering even though §7.2/§8.2/§9.1/§9.4 say those surfaces were cut, and the DG-4 presentation hand-off in `RELIABILITY_COMMITMENTS_SPEC.md §8.8.10` still names the cut spotlight tier. **Codex** reads the specs against `master` and finds that (1) the `commitment_paradox` rename is not canonicalized end-to-end, (2) `diplomatic_treaty_broken` with `family=french_breach` is emitted with the wrong `speaker_attribution`, (3) live code still returns `rival_pressure` instead of the v2.4.3 `hegemony_pressure` enum, and (4) `SAVE_FORMAT_REFERENCE.md` still documents Phase 4 schema.

**The highest-risk failure mode:** two implementers can both "follow the spec" and ship incompatible UIs — one rebuilds cut spotlight/callback infrastructure (reading §12), the other follows the trimmed notice contract (reading §7.2). Downstream of that, the `alliance_paradox` → `commitment_paradox` rename is half-done in code, and `french_breach` would render as an anonymous chancery bulletin instead of Hardenberg's accusation.

**The good news:** every finding is fixable without design change. The hegemony engine design is coherent, shared numeric values agree across specs, the plan slices cover the normative contracts, and `CLAUDE.md` "Up Next" is truthful. This is a **contract-clarity** problem, not an engine-design problem.

### Dimension scorecard (combined)

Counts are unique *unified* findings across the two audits. Rows marked `(C)`, `(X)`, `(C+X)` indicate provenance after dedup.

| Dimension                          | Verdict  | Blocker | Major | Minor |
|------------------------------------|----------|---------|-------|-------|
| 1. Internal consistency            | BLOCKER  | 1       | 3     | 2     |
| 2. UI fidelity                     | BLOCKER  | 2       | 3     | 0     |
| 3. Fuzzy edges                     | RISKY    | 0       | 1     | 3     |
| 4. Code snippet correctness        | RISKY    | 0       | 1     | 1     |
| 5. Implementation plan coverage    | RISKY    | 0       | 1     | 1     |
| 6. Voice / copy fidelity           | BLOCKER  | 1       | 2     | 1     |
| 7. Dangling references             | BLOCKER  | 1       | 2     | 0     |
| 8. Scope drift                     | RISKY    | 0       | 1     | 1     |
| 9. Phase-row truth                 | READY    | 0       | 0     | 0     |

Severity counts sum across unified findings (U1-U17). Some findings cross multiple dimensions; double-counting within a row is intentional.

---

## Event trace matrix (unified)

Claude's 13-row matrix is the base (broader coverage of planned events); Codex's live-code anchors are merged into each row's status column. **Columns:** emit site → payload fields → tier → icon key → label → mock template family → voice resolution → surface → review-route → live-code status.

`MISSING` means the spec does not define that step OR the code does not have what the spec promises. `PARTIAL` means partially implemented with contract drift.

| # | Event | Emit | Payload | Tier | Icon | Label | Template | Voice | Surface | Route | Live-code status (verified 2a9ac4e) |
|---|-------|------|---------|------|------|-------|----------|-------|---------|-------|----|
| 1 | `commitment_paradox` push | **Partial** | episode_id, primary_nation, secondary_nation | HARD_STOP | `icon_paradox` | "Conflicting Oaths" | `commitments_notice_*` (NEW) | `talleyrand` | `commitment_paradox_popup.{tscn,gd}` (NEW) | `review_target="ledger_commitments"` | Emitter writes `"type": "alliance_paradox"` at [backend/game_logic/diplomacy.py:2123-2135](backend/game_logic/diplomacy.py:2123); popup field `alliance_paradox_popup` at [world_state.py:497,668-673,3271,3578](backend/models/world_state.py:497); Godot routes `alliance_paradox` at [main.gd:226-228,776-782](godot-client/project-sovereign/scripts/main.gd:226). **Rename pending B-B3.** |
| 2 | `hard_reject_posture_triggered` | ✓ | actor, victim, episode_id, first_cross | CRITICAL | `icon_hard_reject` | "The Chancery Shut" | `commitments_notice_*` (NEW) | `foreign_office` → "The Chancery of {nation}" | notification_bar CRITICAL card | "Open Ledger" | Dispatch payload exists at [diplomacy.py:844-859](backend/game_logic/diplomacy.py:844); uses HIGH dispatch not CRITICAL notice at [dispatch.py:1111](backend/game_logic/dispatch.py:1111). No commitments icon; generic chancery string only. |
| 3 | `hard_reject_posture_cleared` | ✓ | actor, victim, episode_id | NORMAL | `icon_chancery_reopened` | "The Chancery Reopens" | **MISSING** (§12 has no clear-side template) | — | notification_bar NORMAL card | "Open Ledger" | Payload at [diplomacy.py:403-416](backend/game_logic/diplomacy.py:403); MEDIUM dispatch at [dispatch.py:1112](backend/game_logic/dispatch.py:1112); dispatch formatter at [dispatch.py:1253-1258](backend/game_logic/dispatch.py:1253). |
| 4 | `diplomatic_treaty_broken` (`french_breach`) | ✓ | family, action, fault_nation, witnesses, deltas, episode_id | CRITICAL | `icon_treaty_broken` | "Word Broken" | `commitments_notice_*` (NEW) | `envoy` → Hardenberg/Metternich/Einsiedel | notification_bar CRITICAL card | "Review the broken treaty" | Live emitter writes `speaker_attribution: "foreign_office"` at [diplomacy.py:783](backend/game_logic/diplomacy.py:783); generic HIGH notification at [diplomacy.py:786-793](backend/game_logic/diplomacy.py:786); generic BRK icon at [notification_bar.gd:34-35](godot-client/project-sovereign/scripts/notification_bar.gd:34). **Wrong speaker contract for this family.** |
| 5 | `diplomatic_treaty_broken` (other families) | ✓ same | (same) | NORMAL | `icon_treaty_dragged` | "Treaty Dragged Apart" | **MISSING** (§12 only dramatizes french_breach) | `foreign_office`? unstated | notification_bar NORMAL card | "Open Ledger" | Only `obsolescence_or_external` / `counterparty_reversal` get differentiated copy at [dispatch.py:1037-1042](backend/game_logic/dispatch.py:1037), [campaign_log.py:673-687](backend/campaign_log.py:673). Generic BRK/"Treaty Broken" otherwise. |
| 6 | `commitment_paradox_resolved` | ✓ | chosen_nation, spurned_nation, episode_id | NORMAL | `icon_paradox_resolved` | "The Wound Chosen" | §12.3 beat-3 in-popup aside | `talleyrand` (notice) / `system` (campaign log) | reinforced by after-choice aside **in popup**; NORMAL notice | — | Log-only at [diplomatic_executor.py:2781-2792, 2869-2878](backend/commands/diplomatic_executor.py:2781); one-liner at [campaign_log.py:520-530, 689-692](backend/campaign_log.py:520). No `speaker_attribution`. |
| 7 | `witness_strike_recorded` | ✓ | witness, actor, victim, episode_id, scope_reason | NORMAL | `icon_witness_strike` | "Europe Is Aware" | §10.4 skeletal canonical line per scope | `system`/`foreign_office` — spec ambiguous | notification_bar NORMAL card | — | Dispatch payload at [diplomacy.py:814-824](backend/game_logic/diplomacy.py:814); fallback MEDIUM at [dispatch.py:1231-1244, 1300-1303](backend/game_logic/dispatch.py:1231). No icon, label, or priority entry. |
| 8 | `diplomatic_treaty_broken` (`defensive_refusal_termination`) **NEW §8.8.7a** | **MISSING** — not in `END_REASON_FAMILY_*` | (will need new family constant) | **UNSPECIFIED** | **MISSING** | **MISSING** | **MISSING** | **MISSING** | **MISSING** | **MISSING** | Constant absent from [diplomacy.py:198-200](backend/game_logic/diplomacy.py:198); spec-only at [RELIABILITY_COMMITMENTS_SPEC.md:724](docs/RELIABILITY_COMMITMENTS_SPEC.md:724). Scheduled for B-B4 ([plan:196](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:196)). |
| 9a | Make Amends success (§8.6.1) | will emit `amends_offered` | episode_id, cleared_strike_lineage, diplomat | **UNSPECIFIED** | **MISSING** | **MISSING** | **MISSING** | target's named diplomat per Voice Bible | **UNSPECIFIED** surface | — | No `amends_offered` emitter in code; no `reparations_cooldown` on `WorldState`. Scheduled for B-B7 ([plan:177](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:177)). |
| 9b | Make Amends grievance variant (§8.6.1a) | `amends_offered` with `grievance_variant=True` | + origin_episode_id | **UNSPECIFIED** | **MISSING** | **MISSING** | **MISSING** | Talleyrand + target diplomat | **UNSPECIFIED** | "clicking grievance row" (§8.8.4) | Scheduled for B-B4 ([plan:195](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:195)). |
| 10 | Balance of Europe headline (§11.1) | derived per turn (no event) | hegemon, share, threat_level, coalition state, qualifying nations, leader | N/A | N/A | N/A | state-composed (no authored table) | coalition leader's named diplomat (Castlereagh fallback: "The courts of {leader}") | [diplomatic_ledger.gd](godot-client/project-sovereign/scripts/diplomatic_ledger.gd) | Nations tab default view | Builder returns only `nations`/`treaties`/`threat_coalition`/`talleyrand` at [diplomatic_ledger.py:54-60](backend/game_logic/diplomatic_ledger.py:54); Godot renders `NATION OVERVIEW` + separate `COALITION THREAT` tab at [diplomatic_ledger.gd:181-322, 403-485](godot-client/project-sovereign/scripts/diplomatic_ledger.gd:181). **No `balance_of_europe` payload.** |
| 11a | `call_to_arms_refused_offensive` (B-B4) | **not yet in code** | episode_id, breaker, victim, severity, call_context | **UNSPECIFIED** (spec §8.8.10 says "spotlight" but C3-lite cut spotlight) | **MISSING** | **MISSING** | **MISSING** | victim's diplomat per §8.8.10 | **MISSING** | **MISSING** | Spec-only. |
| 11b | `call_to_arms_refused_defensive` | as above | + grievance_flag | **UNSPECIFIED** | **MISSING** | **MISSING** | **MISSING** | victim's diplomat (Voice Bible) | **MISSING** | **MISSING** | Spec-only. |
| 11c | `call_to_arms_honored_costly` | as above (positive episode) | + loyalty_bond | **UNSPECIFIED** | **MISSING** | **MISSING** | **MISSING** | Talleyrand (honorer = France) | **MISSING** | **MISSING** | Spec-only. |
| 12 | `oathbreaker_posture_triggered/cleared` | **not yet in code** | actor, window_turns, episode_id | **UNSPECIFIED** | **MISSING** | **MISSING** | **MISSING** | **MISSING** | **MISSING** | **MISSING** | Candidate per §8.8.6; `N=2, M=15` not locked. |

**13 rows: 0 fully live-correct, 6 partially live, 7 fully MISSING in both spec and code.** All fully-missing rows are B-B4 (DG-4) or §8.6.1/§8.6.1a Make Amends slices. Rows 1-7 are the "three live events" the presentation spec owns; each has at least one contract gap (route, tier, speaker, icon, or label).

---

## Unified findings

Each finding is tagged `[C]` (Claude-only), `[X]` (Codex-only), or `[C+X]` (fused from both). Suggested fix summarizes both auditors' recommendations.

### BLOCKERS

**U1. v0.5.1 trim leaked past §12 worked examples + §8.8 DG-4 hand-off + §8.8.5/§8.8.10 cross-refs.** `[C+X]` — merges Claude F1/F2/F4/F6 + Codex F1. Internal consistency / UI fidelity / voice fidelity / dangling references.
- **Location:**
  - [docs/COMMITMENTS_PRESENTATION_SPEC.md:213-220](docs/COMMITMENTS_PRESENTATION_SPEC.md:213) §8.1 event routing table (DG-4 rows absent)
  - [docs/COMMITMENTS_PRESENTATION_SPEC.md:526-554, 571-603, 615-653](docs/COMMITMENTS_PRESENTATION_SPEC.md:526) §12.1/§12.2/§12.3 worked examples (spotlight, split-voice, N+1 callback)
  - [docs/RELIABILITY_COMMITMENTS_SPEC.md:692](docs/RELIABILITY_COMMITMENTS_SPEC.md:692) §8.8.5 cross-ref to §8.8.8
  - [docs/RELIABILITY_COMMITMENTS_SPEC.md:758-768](docs/RELIABILITY_COMMITMENTS_SPEC.md:758) §8.8.10 "authored spotlight and notice copy" + "Victim's diplomat leads the refusal spotlight"
- **Observation:** v0.5.1 §7.2/§8.2/§9.1/§9.4 cut the spotlight tier, split-voice `attributed_lines[]` render, and N+1 Talleyrand callback. But:
  - §12.1 line 526 still says *"turn-N spotlight lands as a two-beat split-voice card"*; line 532 *"Canonical mock spotlight templates"*; lines 552-554 *"Next-morning callback (one new beat, not a restate)"*; §12.2 line 571 *"one featured spotlight tells the player"*; line 575 *"Canonical mock spotlight template"*; lines 599-602 *"Optional N+1 aside (Talleyrand)"*.
  - §8.8.5 says *"Emits `call_to_arms_honored_costly` spotlight through C3-lite presentation (see §8.8.8)"* — wrong cross-ref target (§8.8.8 is Coalition-formation hook; correct is §8.8.10) AND wrong tier (spotlight was cut).
  - §8.8.10 says *"three new speaker=envoy / speaker=foreign_office event families … Each needs authored spotlight and notice copy"* — contradicts the v0.5.1 cut of the spotlight tier, AND presentation §8.1 event routing table does not list any of the three DG-4 events; §9.2 icon/label table omits them; §13 core tasks mentions only the three "live" non-DG-4 events.
- **Impact:** Two implementers reading the same spec ensemble will ship incompatible UIs — one rebuilds spotlight/split-voice/N+1 infrastructure from §12, the other ships single-voice notices from §7.2. B-B4 specifically has no tier assignment, no icon key, no label, no template family, no review route for 3 events (6 fire states counting refused/honored). Template slot names (`spotlight`/`lead`/`aside`) will leak into `commitments_notice_*` template keys, reintroducing the schema drift v2.4.2 C7 was supposed to eliminate.
- **Suggested fix (doc-only, pre-implementation):**
  1. Add DG-4 routing to presentation §8.1:

     | Event | Primary surface | Tier | Voice |
     |-------|-----------------|------|-------|
     | `call_to_arms_refused_offensive` | single-voice notice | CRITICAL | `envoy` → victim's diplomat |
     | `call_to_arms_refused_defensive` | single-voice notice | CRITICAL | `envoy` → victim's diplomat |
     | `call_to_arms_honored_costly` | single-voice notice | CRITICAL | `foreign_office` → "The Chancery of France" (Talleyrand register) |
  2. Add DG-4 icons + labels to §9.2; add template stubs to §13 core tasks.
  3. Retrofit §12.1/§12.2/§12.3 to single-voice-notice framing — relabel "spotlight" → "CRITICAL notice"; collapse "two-beat split-voice card" to "single-voice card with named-diplomat inline attribution"; delete the `Next-morning callback` and `Optional N+1 aside` blocks (preserve verbatim in `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` per the §14 historical-note pattern).
  4. Replace §8.8.10 "authored spotlight and notice copy" with "CRITICAL notice copy (no spotlight tier in C3-lite v0.5.1)"; replace §8.8.5 "spotlight through C3-lite presentation (see §8.8.8)" with "CRITICAL notice through C3-lite presentation (see §8.8.10)".
  5. After edits: `grep -n spotlight docs/RELIABILITY_COMMITMENTS_SPEC.md docs/COMMITMENTS_PRESENTATION_SPEC.md` should return only historical/changelog/stub references.

**U2. `commitment_paradox` rename not canonicalized end-to-end.** `[X]` — Codex F2. UI fidelity / dangling references / scope drift.
- **Location:** live-code mismatch spanning 6 surfaces.
  - Backend: [diplomacy.py:2123-2135](backend/game_logic/diplomacy.py:2123) still writes `"type": "alliance_paradox"`; [world_state.py:497,668-673,3271,3578](backend/models/world_state.py:497) stores `alliance_paradox_popup` attribute + serializes it under that key.
  - Godot: [main.gd:100,226-228,726,776-782,2997](godot-client/project-sovereign/scripts/main.gd:226) registers `alliance_paradox_popup.tscn` and routes under `alliance_paradox` dtype; [alliance_paradox_popup.gd](godot-client/project-sovereign/scripts/alliance_paradox_popup.gd:27) is still the only paradox popup on disk.
  - Specs: [COMMITMENTS_PRESENTATION_SPEC.md:19,214,709,746](docs/COMMITMENTS_PRESENTATION_SPEC.md:214) say canonical type is `commitment_paradox` on `commitment_paradox_popup.{tscn,gd}`.
- **Observation:** The docs say `commitment_paradox` is canonical; live code ships `alliance_paradox` everywhere. B-B3 is scheduled in the plan but the rename touches save schema, Godot routing, payload naming, popup field names, and the three-beat popup scene — the current state is "half-renamed" without a migration-compatibility story documented.
- **Impact:** Save migration, Godot routing, payload naming, and popup field schema are all ambiguous at the point where B-B3 implementers need a single source of truth. Without a locked alias contract, saves produced mid-migration are at risk.
- **Suggested fix (code + spec):**
  1. Lock the payload schema for the three-beat popup (fields: `episode_id`, `primary_nation`, `secondary_nation`, `attacker`, `defender`, `ally`, `_preview` snapshots).
  2. Rename emitter `"type": "alliance_paradox"` → `"commitment_paradox"` + attribute `alliance_paradox_popup` → `commitment_paradox_popup` everywhere; keep `alliance_paradox_popup` as a **read-only alias-on-load** in `from_dict()` for save compatibility.
  3. Create `commitment_paradox_popup.tscn` + `.gd` under Godot `scripts/`; delete or alias-register `alliance_paradox_popup.tscn`.
  4. Document the alias policy in `SAVE_FORMAT_REFERENCE.md` (see U7) and in a short §8.8 note in `RELIABILITY_COMMITMENTS_SPEC.md`.

**U3. `diplomatic_treaty_broken` with `family=french_breach` emits `speaker_attribution="foreign_office"`; spec requires victim's `envoy`.** `[X]` — Codex F4. UI fidelity / voice fidelity.
- **Location:**
  - Live: [diplomacy.py:775-783](backend/game_logic/diplomacy.py:775) writes `"speaker_attribution": "foreign_office"` at line 783 (verified).
  - Spec: [COMMITMENTS_PRESENTATION_SPEC.md:216, 403-413](docs/COMMITMENTS_PRESENTATION_SPEC.md:216) says family=french_breach → `speaker="envoy"` → victim's named diplomat (Hardenberg / Metternich / Einsiedel per Voice Bible).
- **Observation:** The sharpest breach event cannot render the required voice with today's payload. A French breach against Prussia would read like an anonymous chancery bulletin rather than Hardenberg's accusation — a material presentation mismatch. `hard_reject_posture_triggered` at [diplomacy.py:844-850](backend/game_logic/diplomacy.py:844) correctly uses `foreign_office` (this is the family the spec assigns to Chancery-voice events). It's specifically the breach family that is mis-attributed.
- **Impact:** B-B1-lite or C-lite implementing the `commitments_notice_*` family will either (a) hardcode a family-to-speaker map in the template renderer (duplicating the emitter's job and splitting contract ownership), or (b) ship with the generic chancery voice, which is a regression against the Voice Bible's named-envoy contract.
- **Suggested fix (code):**
  1. In `_record_treaty_broken()` at [diplomacy.py:775](backend/game_logic/diplomacy.py:775), set `speaker_attribution="envoy"` when `end_reason_family==FRENCH_BREACH`; keep `foreign_office` for `counterparty_reversal`/`obsolescence_or_external`/`defensive_refusal_termination`.
  2. Add `victim_nation` to payload so the downstream resolver can pick the named diplomat without re-deriving it.
  3. Add a central `resolve_named_diplomat(speaker: str, nation: str) -> str` helper (scheduled C-lite §13 — name it now, wire in B-B1-lite) so notices, logs, and popups do not guess differently.

### MAJORS

**U4. `decision_reason` enum drift — live code returns `rival_pressure`; spec requires `hegemony_pressure` + `unknown_baseline`.** `[X]` — Codex F5. Internal consistency / code snippet correctness.
- **Location:**
  - Live: [diplomacy.py:1828-1829, 1858](backend/game_logic/diplomacy.py:1828) all three return paths emit `"rival_pressure"` (verified); [display_names.py:344](backend/display_names.py:344) exposes `"rival_pressure": "rival pressure"` (verified).
  - Spec: [RELIABILITY_COMMITMENTS_SPEC.md:964-967](docs/RELIABILITY_COMMITMENTS_SPEC.md:964) — v2.4.3 enum is `hegemony_pressure` + `unknown_baseline`; `concern_pressure` kept as read-alias only.
  - Plan: [RELIABILITY_IMPLEMENTATION_PLAN.md:154](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:154) confirms alias note.
- **Observation:** Tests, campaign-log explanations, save compatibility, and advisory/presentation code will disagree on the allowed enum set. This is precisely the kind of string drift v2.4.3 was supposed to stop before B-Hegemony lands.
- **Impact:** B-Hegemony tests that assert `decision_reason == "hegemony_pressure"` will all fail against master until this is flipped. The display mapping will show `"rival pressure"` to players even after the engine is landed, because nothing else reads the new enum.
- **Suggested fix (code, 1 hour):**
  1. Change all three emit sites at [diplomacy.py:1828, 1829, 1858](backend/game_logic/diplomacy.py:1828) to return `"hegemony_pressure"`.
  2. Update [display_names.py:344](backend/display_names.py:344): rename key to `"hegemony_pressure": "hegemony pressure"`; add read-alias `"rival_pressure"` → same display for save compatibility.
  3. Add deserialization alias in whoever reads `decision_reason` off saves (if any) to accept both values.

**U5. Commitments notice pipeline has no single source of truth (priority/icon/label/template/speaker resolver).** `[X]` — Codex F3. UI fidelity / implementation plan coverage.
- **Location:**
  - Spec promises: [COMMITMENTS_PRESENTATION_SPEC.md:215-220, 281-309, 410-417, 717, 720](docs/COMMITMENTS_PRESENTATION_SPEC.md:215).
  - Current rails: [notifications.py:24-62](backend/notifications.py:24) only has generic types; [notification_bar.gd:30-42](godot-client/project-sovereign/scripts/notification_bar.gd:30) only has generic icons; [diplomatic_templates.py](backend/game_logic/diplomatic_templates.py) has no `commitments_notice_*` family; `witness_strike_recorded` falls back to default MEDIUM at [dispatch.py:1231-1244, 1300-1303](backend/game_logic/dispatch.py:1231).
- **Observation:** Even if the engine emits the right events, the UI cannot render the promised commitments vocabulary consistently without one explicit routing table shared across notifications/dispatch/campaign log/ledger/popup.
- **Impact:** Without the table, the player-facing layer degrades to generic treaty/chancery strings with no stable icon or attribution contract — defeating the purpose of `commitments_notice_*` being its own namespace.
- **Suggested fix (doc, pre-C-lite):** Add one explicit routing table to presentation §8.1 that maps `event_family → priority → icon_key → player_label → template_key → speaker_resolver → review_target`. Make it the single source of truth that `commitments_notice_*` templates (C-lite §13), `notification_bar.gd` commitments icon set (C-lite §14), and the dispatch formatter all read from. (The spec already has sub-tables for each column; this is a join-table edit.)

**U6. Balance of Europe headline has no live surface path.** `[C+X]` — Codex F6 reinforces what Claude's matrix row 10 flagged as "planned." Implementation plan coverage / scope drift.
- **Location:**
  - Spec: [RELIABILITY_COMMITMENTS_SPEC.md:1006-1046](docs/RELIABILITY_COMMITMENTS_SPEC.md:1006) §11.1 four-case state machine (no hegemon / hegemon without coalition / coalition BREWING / coalition DECLARED).
  - Plan: [RELIABILITY_IMPLEMENTATION_PLAN.md:222-225](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:222) places the headline in C-lite.
  - Live: [diplomatic_ledger.py:54-60](backend/game_logic/diplomatic_ledger.py:54) returns only `nations`/`treaties`/`threat_coalition`/`talleyrand`; [diplomatic_ledger.gd:181-322, 403-485](godot-client/project-sovereign/scripts/diplomatic_ledger.gd:181) renders `NATION OVERVIEW` and a separate `COALITION THREAT` tab.
- **Observation:** The spec and plan treat Balance of Europe as a shipped surface, but the ledger builder has no `balance_of_europe` field and the Godot ledger has no top-of-Nations-tab headline. Claude-F8 additionally notes the B-Hegemony test bullet undersells state-case coverage (3 of 4 cases, not the 4 §11.1 requires).
- **Impact:** Builders have to invent the payload shape and rendering rules instead of implementing a settled contract. One of the new hegemony-era player readouts has no validated surface path. If the state-case tests only land in B-Hegemony (with 3 cases) and never expand in C-lite, the DECLARED case ships untested.
- **Suggested fix (plan + doc, then code in B-Hegemony / C-lite):**
  1. Lock the `balance_of_europe` payload block schema in presentation §11 (hegemon, share, threat_level, coalition_state, qualifying_nations, leader).
  2. Expand B-Hegemony test bullet in [RELIABILITY_IMPLEMENTATION_PLAN.md:132](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:132) to all four §11.1 cases OR explicitly move all four state-case tests to C-lite (since the renderer lives there per plan line 747).
  3. During B-Hegemony implementation: `build_diplomatic_ledger()` adds the `balance_of_europe` block. During C-lite: Godot renders it at the top of the Nations tab; keep the Threat tab for coalition detail only.

**U7. `SAVE_FORMAT_REFERENCE.md` is stale — still documents v1.0, Phase 4 schema.** `[X]` — Codex F7. Dangling references.
- **Location:** [docs/SAVE_FORMAT_REFERENCE.md:12-14, 107-109, 190, 224-226, 874-875](docs/SAVE_FORMAT_REFERENCE.md:12).
  - Line 12: "Format version: 1.0"
  - Line 14: "Compatible with: Phase 4 Commands/QoL/Popups + Diplomacy Button Session A"
  - Line 107: `"diplomatic_reliability": {}` (documents per-pair, but master has nation-level)
  - Line 109: `"alliance_paradox_popup": null` (no note about upcoming rename)
  - Line 224-226: says "per nation-pair" and "+5 per 10-turn honored treaty"
- **Observation:** Live `WorldState` stores nation-level `diplomatic_reliability`, `betrayal_history`, `next_episode_id`, and the pending dispatch queue — none of which the reference covers. The shipped v2.4.3 substrate is not documented, and the upcoming B-B7 `reparations_cooldown` field has no reserved slot.
- **Impact:** Anyone using the save reference as the migration or serialization contract will write the wrong tests and the wrong compatibility logic — this is a direct spec/live-code mismatch, not stale commentary. When B-B3 rename lands (U2), there will be no documented alias-on-load contract.
- **Suggested fix (doc, 1 hour):**
  1. Bump `format_version` to 1.1 in the docs; document the v2.4.3 substrate fields (`betrayal_history`, `next_episode_id`, nation-level `diplomatic_reliability`).
  2. Add legacy-alias note for `alliance_paradox_popup` pointing at U2's alias policy.
  3. Reserve a documented slot for B-B7's `reparations_cooldown` once its shape is locked (can be a "Planned" row, not a live one).
  4. Update the Session 1A migration notes to cover the v2.4.3 transitional schema.

**U8. Voice Bible header cites v0.3 of presentation spec; current is v0.5.1.** `[C]` — Claude F5. Internal consistency / voice fidelity.
- **Location:** [docs/DIPLOMAT_VOICE_BIBLE.md:4, 6, 201, 203, 205](docs/DIPLOMAT_VOICE_BIBLE.md:4).
  - Line 4/6: references "v0.3 scope note (Apr 16, 2026)" and "`COMMITMENTS_PRESENTATION_SPEC.md` v0.3 §10.3 requires only 4 lead-line templates"
  - Line 203 heading: "Required for C3-lite (v0.3 — must land in this phase)"
- **Observation:** The 4-line minimum *still matches* v0.5.1 §10.3 — so the count is fine, only the version label is wrong. But a contributor comparing Voice Bible cast requirements to presentation §10.3 sees the version skew and may assume the Voice Bible is outdated.
- **Impact:** False signal that cast minimums changed. May trigger unnecessary "update Voice Bible" churn.
- **Suggested fix (doc, 10 min):** Bump Voice Bible status header to "v1.1 — v0.5.1 aligned"; replace all `v0.3` references with `v0.5.1`; add a one-line changelog entry pointing at the v0.5.1 trim.

**U9. `NotificationPriority.HIGH` exists in code but is undocumented in presentation §9.2.** `[C]` — Claude F7. Internal consistency.
- **Location:** [backend/notifications.py:19-21](backend/notifications.py:19) defines `NORMAL=0`, `HIGH=1`, `CRITICAL=2`. Presentation [§9.2](docs/COMMITMENTS_PRESENTATION_SPEC.md) priority tier table uses only CRITICAL and NORMAL. `MARSHAL_DEFIED_ORDER` already uses HIGH.
- **Observation:** It is not clear whether commitments events may use HIGH (between NORMAL and CRITICAL), and what the caller contract is.
- **Impact:** A future triage decision ("bump this to HIGH so it sorts above a cluttered NORMAL queue") has no documented constraint. Easy to accidentally split commitment events across two tiers in code review.
- **Suggested fix (doc, 5 min):** Add a one-line note in presentation §9.2: *"Commitments events use CRITICAL or NORMAL only; the HIGH tier (used by `MARSHAL_DEFIED_ORDER`) is intentionally not used by this pass to keep the three live events visually distinct from military urgency."*

**U10. Plan B-Hegemony test list undersells Balance of Europe case coverage.** `[C]` — Claude F8. Implementation plan coverage.
- **Location:** [docs/RELIABILITY_IMPLEMENTATION_PLAN.md:132](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:132) lists 3 cases; spec [§11.1](docs/RELIABILITY_COMMITMENTS_SPEC.md:1006) has 4 cases; plan line 741 (C-lite) names all 4.
- **Observation:** Ownership is split — B-Hegemony tests 3 cases, C-lite names 4 cases but may assume the test already exists. DECLARED state case risks sliding through the gap.
- **Impact:** See U6's implementation risk; this is the test-coverage sibling.
- **Suggested fix (doc, 5 min):** Pick one slice to own all four cases (recommend C-lite since the renderer lives there); delete the B-Hegemony bullet.

### MINORS

**U11. §11.1 Case 1 self-contradicts: "no line follows … line appears below."** `[C]` — Claude F10. Fuzzy edges.
- **Location:** [docs/RELIABILITY_COMMITMENTS_SPEC.md:1018-1021](docs/RELIABILITY_COMMITMENTS_SPEC.md:1018).
- **Observation:** *"No coalition line follows (coalition brewing still possible from event-based threat; if active, its line appears below)."* Ambiguous.
- **Suggested fix:** Rewrite: *"The equilibrium line is standalone. If a coalition is independently brewing from event-based threat (battles, captures) a BREWING line from Case 3 may still render below it; the equilibrium and BREWING lines are composable."*

**U12. §11.1 Case 2 flavor line gated only for `30 ≤ threat_level < 40`; `threat_level < 30` unspecified.** `[C]` — Claude F9. Fuzzy edges.
- **Location:** [docs/RELIABILITY_COMMITMENTS_SPEC.md:1026](docs/RELIABILITY_COMMITMENTS_SPEC.md:1026).
- **Suggested fix:** Add: *"When `threat_level < 30` with a hegemon present, render only the hegemon line; the flavor line is suppressed."*

**U13. `hegemony_target_mod` comment vs code: bucket edge off-by-one.** `[C]` — Claude F11. Code snippet correctness.
- **Location:** [docs/RELIABILITY_COMMITMENTS_SPEC.md:843-848](docs/RELIABILITY_COMMITMENTS_SPEC.md:843). Comment says clamp kicks in at 63.33%, but integer truncation puts it at ~63.34%.
- **Suggested fix:** Change comment to *"clamped at -20 from ~63.34%+ onward (integer truncation of raw = 20 clamps to max ceiling)"*.

**U14. §10.3 self-reference.** `[C]` — Claude F12. Prose.
- **Location:** [docs/COMMITMENTS_PRESENTATION_SPEC.md:402](docs/COMMITMENTS_PRESENTATION_SPEC.md:402). *"`system` is disallowed on rail surfaces per §10.3"* — appears inside §10.3.
- **Suggested fix:** Either drop the `per §10.3` qualifier, or move the rule into §10.3 proper and reference it from the table without the circular cite.

**U15. Runtime-behavior contracts are verbal-only (logging channel, fail-loud shape, bloc-cache home).** `[C+X]` — Claude F13 + Codex F8. Fuzzy edges.
- **Location:**
  - [docs/RELIABILITY_COMMITMENTS_SPEC.md:319](docs/RELIABILITY_COMMITMENTS_SPEC.md:319): "emit a debug log for telemetry" — no channel/level/message format.
  - [docs/COMMITMENTS_PRESENTATION_SPEC.md:415](docs/COMMITMENTS_PRESENTATION_SPEC.md:415): "loyalist fallback … fail loudly" — no exception type or log shape.
  - [docs/RELIABILITY_COMMITMENTS_SPEC.md:996](docs/RELIABILITY_COMMITMENTS_SPEC.md:996): per-turn bloc cache — no `WorldState` field named.
- **Observation:** Two implementers will land different telemetry and failure behavior while both believing they followed the spec. The bloc-cache invalidation pattern (`invalidate_active_nations_cache`) is a golden-rule reference in `CLAUDE.md`, so there is a canonical pattern to follow — just not named.
- **Suggested fix (doc, 15 min):** Add one compact runtime-behavior note:
  - Logger: `backend.game_logic.coalition`, level INFO (matches existing coalition.py telemetry), message `[hegemony] non-France hegemon detected ({hegemon_nation} @ {share:.2f}); skipping add_threat (threat scalar France-targeted in v0.1)`, rate: once per turn per actor (not per call).
  - Fail-loud shape: raise `ValueError(f"loyalist register unsupported: {nation}/{personality}")` — so unit tests can assert on it instead of matching log output.
  - Cache home: `WorldState._bloc_members_cache: Dict[str, Set[str]]`, invalidated via `invalidate_bloc_members_cache()` called from the same seams as `invalidate_active_nations_cache()`.

**U16. Diplomat resolver fallback for non-cast nations specced but not v0.1-implementable.** `[C]` — Claude F14 + partial Codex F8. Voice / copy fidelity / scope drift.
- **Location:** [docs/COMMITMENTS_PRESENTATION_SPEC.md:413, 415](docs/COMMITMENTS_PRESENTATION_SPEC.md:413), [docs/RELIABILITY_COMMITMENTS_SPEC.md:378](docs/RELIABILITY_COMMITMENTS_SPEC.md:378).
- **Observation:** §10.3 says `speaker="envoy"` MUST resolve to a named diplomat; §7.7 scale table mentions "13+ named diplomats or generic-register fallback." Current cast: 5 nations. Non-cast nation events have no fallback.
- **Impact:** Latent — today's 5-nation map doesn't trigger this. When the map scales, cascade breaks on non-majors will hit it.
- **Suggested fix (doc, 5 min):** Add to §10.3: *"v0.1 scope assumes the 5-nation roster (France + Britain + Austria + Prussia + Saxony). If a future event targets a non-cast nation, the render falls back to `foreign_office` → 'The Chancery of {nation}' with no personality register until the cast expands."*

**U17. Plan test budget total arithmetic: rows sum to 46-53, total row says 45-54.** `[C]` — Claude F15. Internal consistency.
- **Location:** [docs/RELIABILITY_IMPLEMENTATION_PLAN.md:329](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:329).
- **Suggested fix:** Correct to "~46-53" or flag the cell as approximate.

---

## Missing artifacts (merged)

Files / helpers / events the specs name but which do not exist in `master`:

| Artifact | Scheduled by | Spec reference | Status |
|----------|--------------|----------------|--------|
| `commitment_paradox_popup.tscn` | C-lite §14 | [COMMITMENTS_PRESENTATION_SPEC.md:746](docs/COMMITMENTS_PRESENTATION_SPEC.md:746) | Absent (only `alliance_paradox_popup.tscn` exists). **Blocked by U2.** |
| `commitment_paradox_popup.gd` | C-lite §14 | Same | Absent. **Blocked by U2.** |
| `commitments_notice_*` template family | C-lite §13 | [COMMITMENTS_PRESENTATION_SPEC.md:215-220](docs/COMMITMENTS_PRESENTATION_SPEC.md:215) | Absent; not in `diplomatic_templates.py`. **Blocked by U5.** |
| Named-diplomat resolver helper | C-lite §13 | [COMMITMENTS_PRESENTATION_SPEC.md:410-417](docs/COMMITMENTS_PRESENTATION_SPEC.md:410) | Absent. **Blocked by U3/U16.** |
| `world.get_power_tier`, `world.get_bloc_members`, `_top_overlord`, `_calculate_hegemony_pressure` | B-Hegemony | [RELIABILITY_IMPLEMENTATION_PLAN.md:93-109](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:93) | Absent; plan covers. |
| `WorldState._bloc_members_cache` + invalidate helper | B-Hegemony | [RELIABILITY_COMMITMENTS_SPEC.md:996](docs/RELIABILITY_COMMITMENTS_SPEC.md:996) (implicit) | Absent; no field name specified. **Blocked by U15.** |
| `WorldState.reparations_cooldown` | B-B7 | [RELIABILITY_COMMITMENTS_SPEC.md:547-559](docs/RELIABILITY_COMMITMENTS_SPEC.md:547) | Absent; not in schema. **Blocked by U7.** |
| `amends_offered` emitter | B-B7 / B-B4 | [RELIABILITY_IMPLEMENTATION_PLAN.md:177,195](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:177) | Absent; plan covers. |
| `END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION` constant | B-B4 | [RELIABILITY_COMMITMENTS_SPEC.md:724](docs/RELIABILITY_COMMITMENTS_SPEC.md:724) | Absent from `diplomacy.py:198-200`; plan covers. |
| Balance of Europe payload block in ledger | C-lite / B-Hegemony | [RELIABILITY_COMMITMENTS_SPEC.md:1006-1046](docs/RELIABILITY_COMMITMENTS_SPEC.md:1006) | Absent. **Blocked by U6.** |
| Icon art for `icon_treaty_broken`, `icon_paradox`, etc. | Art (commissioned later) | [COMMITMENTS_PRESENTATION_SPEC.md:§9.2](docs/COMMITMENTS_PRESENTATION_SPEC.md) | Not a spec gap — art-commissioned. |

**No blocking missing artifacts beyond the audits' scope.** Everything the specs name is either (a) shipped substrate, (b) explicitly scheduled by a plan slice, or (c) stubbed as deferred to `WAR_BARGAIN_SPEC`. The issues above are all "scheduled but contract unclear" problems, which the findings resolve.

---

## Cross-spec value table (merged)

All shared *numeric* values agree across specs. Mismatches are labeled with the responsible finding.

| Shared value | Location | Status | Finding |
|--------------|----------|--------|---------|
| Pressure ladder `1/3/5/8` | Spec §7.3 / §11.1 / COALITION_SPEC §2a / plan B-Hegemony | ✓ spec; absent in live code | — (scheduled B-Hegemony) |
| Hegemony share buckets `30/40/50/60%` | Spec §7.3 / §9.5 / plan §B-Hegemony tests | ✓ spec; absent in live code | — |
| `bilateral_betrayal_mod = -6 per strike` | Spec §9.2 / plan §B-B1-lite | ✓ spec; live formula still uses old reliability contribution at [diplomacy.py:1634-1668](backend/game_logic/diplomacy.py:1634) | — (scheduled B-B1-lite) |
| Hard-reject threshold `3 strikes` | Spec §8.7 / §9.2 / live `has_hard_reject_posture` | ✓ | — |
| Episode cap `+2 victim strikes per episode` | Spec §8.3 / §8.7 | ✓ | — |
| Make Amends standard `200g + 1 DP`, +5 relation, +2 reliability, 10-turn cooldown | Spec §8.6.1 / plan §B-B7 line 177 | ✓ spec; absent in live code | — (scheduled B-B7) |
| Make Amends grievance variant `400g + 2 DP`, +8 relation, +3 reliability | Spec §8.6.1a / §8.8.4 / plan §B-B4 | ✓ | — (scheduled B-B4) |
| Grievance stacking cap `3 per pair` | Spec §8.8.4 / §9.3 | ✓ | — |
| Composite floor `-60` (DG-4) | Spec §9.3 / plan merge-ordering §275-285 | ✓ spec; absent in live formula | — (scheduled B-B1-lite + B-B4) |
| `grievance_modifier = -30 per grievance` | Spec §8.8.9 / §9.3 | ✓ | — |
| `decision_reason` enum (`hegemony_pressure` + `unknown_baseline` + alias `concern_pressure`) | Spec §12.2 / plan §154 | Live returns `rival_pressure` at [diplomacy.py:1828-1858](backend/game_logic/diplomacy.py:1828) + [display_names.py:344](backend/display_names.py:344) | **U4 MISMATCH** |
| `end_reason_family` enum (adds `defensive_refusal_termination`) | Spec §8.8.7a / plan §B-B4 | Absent from [diplomacy.py:198-200](backend/game_logic/diplomacy.py:198); plan covers | — (scheduled B-B4) |
| Speaker enum (`talleyrand`/`envoy`/`foreign_office`/`system`) | Presentation §10.3 / §11 | ✓ spec; french_breach emits `foreign_office` where spec wants `envoy` | **U3 MISMATCH** |
| Paradox popup type (`commitment_paradox`) | Presentation §12.3 | Live emits `alliance_paradox` at [diplomacy.py:2135](backend/game_logic/diplomacy.py:2135); live field `alliance_paradox_popup` at [world_state.py:497](backend/models/world_state.py:497); Godot routes legacy at [main.gd:226-228](godot-client/project-sovereign/scripts/main.gd:226) | **U2 MISMATCH** |
| Save format version | [SAVE_FORMAT_REFERENCE.md:12](docs/SAVE_FORMAT_REFERENCE.md:12) says 1.0 Phase 4; master has v2.4.3 substrate fields | — | **U7 MISMATCH** |
| Anti-renewal cooldown (15 turns) | Spec §8.8.7 "candidate" | — | Intentionally unlocked |
| Oathbreaker `N=2, M=15` | Spec §8.8.6 "authored — candidate" | — | Intentionally unlocked |
| Honor bias default `1.0` | Spec §8.8.12 | ✓ | — |
| `_POWER_TIER_DEFAULT = "secondary"` | Spec §7.2 / plan §B-Hegemony | ✓ | — |
| BREWING / DECLARED state names | Spec §11.1 / COALITION_SPEC §3-§4 | ✓ | — |
| Voice Bible cast coverage (4-line minimum) | Voice Bible / Presentation §10.3 | ✓ count; version header stale | **U8 label-only** |
| Test budget total | Plan §329: "~45-54"; sum = 46-53 | Close approximate | **U17 trivia** |
| Test budget B-Hegemony | Plan §318: 18-22; spec §13 line 1190 agrees | ✓ | — |
| Test budget C-lite | Plan §326: 10-12; presentation §14 line 748 agrees | ✓ | — |
| Test budget B-B4 | Plan §327: 25-29; spec §8.8.13 says "~25" | Close approximate | Trivia |

**Mismatch summary:** 3 live-code mismatches (U2, U3, U4), 1 doc-drift mismatch (U7), 1 label-only (U8), 1 trivia (U17). All shared *numeric* values still agree across specs — the problems are identifier/string drift.

---

## Effort estimate

Broken down by work type. Times assume a single focused session per block. Hours do not include review passes.

### Block 1 — Doc-only trim cleanup (pre-implementation)

**~2-3 hours, one session.** All edits, no code. Unblocks B-Hegemony / B-B1-lite / B-B3 / B-B4 / B-B7 / C-lite.

| # | Finding | Files touched | Est. |
|---|---------|---------------|------|
| 1 | U1 DG-4 routing + §12 retrofit + §8.8.5/§8.8.10 cross-ref sweep | `COMMITMENTS_PRESENTATION_SPEC.md` §8.1/§9.2/§12.1/§12.2/§12.3/§13; `RELIABILITY_COMMITMENTS_SPEC.md` §8.8.5/§8.8.10; `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` (preserve cut prose) | 90 min |
| 2 | U5 commitments routing table | `COMMITMENTS_PRESENTATION_SPEC.md` §8.1 (new join-table) | 20 min |
| 3 | U7 save format refresh | `SAVE_FORMAT_REFERENCE.md` lines 12, 14, 107-109, 190, 224-226, 874-875 | 30 min |
| 4 | U8 Voice Bible v0.3 → v0.5.1 | `DIPLOMAT_VOICE_BIBLE.md` lines 4, 6, 201, 203, 205 | 10 min |
| 5 | U9 HIGH-tier note | `COMMITMENTS_PRESENTATION_SPEC.md` §9.2 | 5 min |
| 6 | U10 B-Hegemony test bullet | `RELIABILITY_IMPLEMENTATION_PLAN.md` line 132 | 5 min |
| 7 | U11 §11.1 Case 1 rewrite | `RELIABILITY_COMMITMENTS_SPEC.md` lines 1018-1021 | 5 min |
| 8 | U12 §11.1 Case 2 gate | `RELIABILITY_COMMITMENTS_SPEC.md` line 1026 | 5 min |
| 9 | U13 hegemony_target_mod comment | `RELIABILITY_COMMITMENTS_SPEC.md` lines 843-848 | 2 min |
| 10 | U14 §10.3 self-ref | `COMMITMENTS_PRESENTATION_SPEC.md` line 402 | 2 min |
| 11 | U15 runtime-behavior note | `RELIABILITY_COMMITMENTS_SPEC.md` §319/§996; `COMMITMENTS_PRESENTATION_SPEC.md` §415 | 15 min |
| 12 | U16 non-cast nation fallback | `COMMITMENTS_PRESENTATION_SPEC.md` §10.3 | 5 min |
| 13 | U17 arithmetic | `RELIABILITY_IMPLEMENTATION_PLAN.md` line 329 | 2 min |

**Subtotal: ~3 hours.** This block is independent of every live-code change — it ships as one doc-only commit and unblocks the other blocks.

### Block 2 — Substrate alignment (doc + code)

**~2-3 hours, one session.** Small code changes + their doc echoes. Each change is narrow and testable in isolation.

| # | Finding | Work | Est. |
|---|---------|------|------|
| 14 | U4 `rival_pressure` → `hegemony_pressure` | 3 line changes in [diplomacy.py:1828,1829,1858](backend/game_logic/diplomacy.py:1828) + 1 change + alias in [display_names.py:344](backend/display_names.py:344) + 2-3 new unit tests | 45 min |
| 15 | U3 `french_breach` speaker_attribution fix | 1 conditional in [diplomacy.py:775-783](backend/game_logic/diplomacy.py:775) + 2 unit tests + sketch central resolver signature | 45 min |
| 16 | U2 `commitment_paradox` rename (if advancing B-B3 here) | Rename attribute + emit type; add alias-on-load in `from_dict`; create `commitment_paradox_popup.{tscn,gd}` (new Godot scene + script); update `main.gd` registration/routing; update `SAVE_FORMAT_REFERENCE.md` alias row | 90-120 min |

**Subtotal: ~3 hours if U2 is included; ~1.5 hours without.**

**Note:** U2 is scheduled for B-B3. If B-B3 is imminent in the plan, pulling it into this block is efficient (it unblocks U5 and the missing `commitment_paradox_popup.{tscn,gd}` artifacts). If B-B3 is further out, leave it in its slot.

### Block 3 — Already covered by plan (no audit-driven effort)

U5 (commitments notice pipeline implementation) and U6 (Balance of Europe payload + renderer) are already scheduled:

- **U5** → C-lite §13/§14 (plan row 326, ~10-12 tests)
- **U6** → B-Hegemony landing + C-lite surfacing (plan rows 222-225, 747)

The audit does not add new work here — it adds *clarifying contracts* (via Block 1 edits) that the scheduled slices need to read. Once Block 1 lands, these slices can proceed as planned.

### Total effort

| Block | Scope | Est. hours |
|-------|-------|------------|
| Block 1 | Doc-only trim cleanup (U1, U5 table, U7, U8, U9, U10, U11, U12, U13, U14, U15, U16, U17) | **~3 h** |
| Block 2 (partial) | Substrate alignment without U2 (U3, U4) | **~1.5 h** |
| Block 2 (full) | Substrate alignment with U2 (U3, U4, U2 rename) | **~3 h** |

**Recommendation: run Block 1 and Block 2-partial in one session (~4.5 h), defer U2 to B-B3.** Rationale below.

---

## Split recommendation

**Do not split Block 1.** It's a single consistent doc pass — all edits anchor on the same v0.5.1 trim decision. Splitting would create a window where §12 and §8.8.10 disagree with §7.2, the exact failure mode F1/F2 describe. Ship it as one atomic commit titled *"v2.4.3 trim cleanup: §12 retrofit + DG-4 routing + save format refresh + Voice Bible version bump"*.

**Split Block 2 based on plan timing:**

- **If B-B3 is the next coding slice:** fold U2 into Block 2 (one session covers Block 1 + Block 2-full = ~5-6 hours, done in one focused pass).
- **If B-B1-lite or B-Hegemony is the next coding slice:** ship Block 1 + Block 2-partial (U3 + U4 only) in one session (~4.5 hours). Leave U2 for its scheduled B-B3 slot — the work is well-scoped and any implementer who reads the updated specs from Block 1 will land it correctly.

**Don't split U3 and U4 across sessions.** Both are 3-4 line code changes; coupling them in one commit makes the "v2.4.3 enum + speaker discipline" boundary legible in `git log`.

**Absorb the minors (U9-U17) into Block 1 even if the blockers/majors split.** All minors are < 15 min each; separating them adds coordination cost exceeding the work itself. Two exceptions that can slide to later without harm: U13 (comment off-by-one, cosmetic) and U17 (arithmetic trivia).

### Proposed merge order if combining Blocks 1 + 2

1. Block 1 doc edits (single commit).
2. Run: `grep -n spotlight docs/RELIABILITY_COMMITMENTS_SPEC.md docs/COMMITMENTS_PRESENTATION_SPEC.md` — must return only historical/changelog/stub refs.
3. U4 enum change + 2 unit tests + display_names alias (single commit).
4. U3 speaker_attribution change + 2 unit tests (single commit).
5. (Optional) U2 paradox rename + alias-on-load + `commitment_paradox_popup` scene/script (single commit, ships B-B3).
6. Full test suite (expect pre-existing count + 4-6 new from U3/U4, +4-6 more if U2 is in).

---

## Recommendation

**REQUEST-CHANGES.** The spec ensemble is not yet implementation-ready, but every finding is fixable in a single focused doc-cleanup pass plus two small code changes (three if B-B3 is pulled forward). No design changes required.

**Pre-merge gate for B-Hegemony:** Block 1 must land. U1 and U5 are load-bearing for template authoring in C-lite; U4 is load-bearing for B-Hegemony unit tests; U8/U9/U10/U15 stabilize the contracts downstream slices read from.

**Pre-merge gate for B-B4:** U3 must land (otherwise the victim-envoy voice cannot be rendered by the new commitments_notice_* family).

**Not a pre-merge gate for anything:** U11, U12, U13, U14, U16, U17 — ship them in Block 1 for hygiene but they don't block downstream slices.

Once Block 1 lands and Block 2-partial (U3, U4) lands, the spec ensemble is implementation-ready. Engine design is coherent; code snippets run cleanly against the helpers they cite; plan slices cover the normative contracts; `CLAUDE.md` phase-row is truthful.

---

## Appendix — Provenance map

Cross-reference for anyone tracking which original finding became which unified finding.

| Unified | Claude | Codex | Notes |
|---------|--------|-------|-------|
| U1 | F1, F2, F4, F6 | F1 | Four Claude findings + Codex F1 all trace to v0.5.1 trim leak — fused |
| U2 | — (matrix row 1 noted "rename pending B-B3") | F2 | Codex-unique; Claude flagged it in trace matrix but not as a finding |
| U3 | — | F4 | Codex-unique live-code check Claude did not perform |
| U4 | — | F5 | Codex-unique live-code check Claude did not perform |
| U5 | — | F3 | Codex-unique; Claude partially touched via F1 (DG-4 events) |
| U6 | F8 (partial) | F6 | Claude flagged the test bullet; Codex flagged the render surface — complementary |
| U7 | — | F7 | Codex-unique |
| U8 | F5 | — | Claude-unique |
| U9 | F7 | — | Claude-unique |
| U10 | F8 | — | Claude-unique (paired with U6) |
| U11 | F10 | — | Claude-unique |
| U12 | F9 | — | Claude-unique |
| U13 | F11 | — | Claude-unique |
| U14 | F12 | — | Claude-unique |
| U15 | F13 | F8 | Fused — same family of runtime-contract gaps |
| U16 | F14 | F8 (partial) | Fused |
| U17 | F15 | — | Claude-unique |

**Deduplication:** Claude had 15 findings, Codex had 8. The union after dedup is 17 unified findings. Overlap: 4 Claude + 1 Codex → U1 (the v0.5.1 trim leak family); 1 Claude + 1 Codex → U6 (Balance of Europe); 1 Claude + 1 Codex → U15 (runtime contracts); 1 Claude + ½ Codex → U16 (fallback scope). Other Codex findings (U2, U3, U4, U5, U7) are entirely new live-code checks Claude did not run.
