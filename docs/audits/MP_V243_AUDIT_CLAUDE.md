# Memory and Pressure v2.4.3 Audit — claude-opus-4-7, 2026-04-20

> **Historical/superseded as of April 25, 2026.** DG-4 event-routing claims in this audit predate the shared commitments routing table, CRITICAL call-to-arms notices, direct-only call-to-arms implementation, Balance of Europe ledger payload, and witness anti-spam fixes. Retained for historical context only; do not treat "DG-4 missing" rows below as live gaps.

## Executive summary

**Overall verdict: REQUEST-CHANGES (2 BLOCKERs, 6 MAJORs, 7 MINORs).**

The v2.4.3 substrate decisions are sound and the plan + spec + presentation-spec skeletons agree on scope. But the v2.4.2 C7 "non-normative bulk trim" that produced v0.5.1 was **incomplete**: `COMMITMENTS_PRESENTATION_SPEC.md` §12 worked examples still prescribe v0.3 spotlight-tier + N+1 + split-voice rendering — directly contradicting §7.2 / §8.2 / §9.1 / §9.4 which all say those surfaces were CUT. Meanwhile `RELIABILITY_COMMITMENTS_SPEC.md` §8.8 (DG-4) still tells implementers to "emit a `call_to_arms_honored_costly` spotlight through C3-lite presentation" — a surface C3-lite no longer builds — and the three B-B4 call-to-arms events are **absent from the presentation spec's §8.1 event-routing table entirely**. The top-3 findings:

1. **[BLOCKER F1]** DG-4 events (`call_to_arms_refused_offensive`, `_refused_defensive`, `_honored_costly`) have no UI surface contract. §8.8.10 says "C3-lite presentation" but presentation spec §8.1 does not route them and §13 core tasks does not add templates for them.
2. **[BLOCKER F2]** Presentation §12 worked examples contradict v0.5.1 §7.2 / §9.1 / §9.4 cuts. Any implementer reading §12 will build the very infra the top-note said was cut.
3. **[MAJOR F3]** §8.8.5 cross-reference points to §8.8.8 (Coalition-formation hook) for presentation; correct target is §8.8.10.

Everything else is fixable without design changes — the hegemony engine design is coherent, the code snippets run cleanly against the helpers they cite, and the plan slices cover the normative contracts. The blockers are all "spec rescope leaked past the trim" problems, not "engine design broken" problems.

## Dimension scorecard

| Dimension | Verdict | Blocker | Major | Minor |
|-----------|---------|---------|-------|-------|
| 1. Internal consistency            | RISKY   | 1       | 2     | 2     |
| 2. UI fidelity                     | BLOCKER | 1       | 2     | 2     |
| 3. Fuzzy edges                     | RISKY   | 0       | 1     | 2     |
| 4. Code snippet correctness        | READY   | 0       | 0     | 1     |
| 5. Implementation plan coverage    | RISKY   | 0       | 1     | 0     |
| 6. Voice / copy fidelity           | RISKY   | 0       | 0     | 2     |
| 7. Dangling references             | BLOCKER | 1       | 1     | 1     |
| 8. Scope drift                     | READY   | 0       | 0     | 0     |
| 9. Phase-row truth                 | READY   | 0       | 0     | 0     |

Severity counts sum across findings; see Findings section.

## Event trace matrix (UI fidelity §2)

Columns: **emit site → payload field(s) present → tier → icon key → label → mock template family → voice resolution → surface → review-route**.
`MISSING` means the spec does not define that step OR the code does not have what the spec promises.

| # | Event | Emits? | Payload | Tier | Icon | Label | Template | Voice | Surface | Route |
|---|-------|--------|---------|------|------|-------|----------|-------|---------|-------|
| 1 | `commitment_paradox` (push) | **Partial** — still emitted as `"alliance_paradox"` at [backend/game_logic/diplomacy.py:2135](backend/game_logic/diplomacy.py) pending B-B3 | episode_id, primary_nation, secondary_nation | HARD_STOP | `icon_paradox` | "Conflicting Oaths" | `commitments_notice_*` (NEW) | `talleyrand` | new `commitment_paradox_popup.{tscn,gd}` | `review_target="ledger_commitments"` |
| 2 | `hard_reject_posture_triggered` | ✓ [diplomacy.py:844](backend/game_logic/diplomacy.py:844) | actor, victim, episode_id, first_cross | CRITICAL | `icon_hard_reject` | "The Chancery Shut" | `commitments_notice_*` (NEW) | `foreign_office` → "The Chancery of {nation}" | notification_bar CRITICAL card | "Open Ledger" |
| 3 | `hard_reject_posture_cleared` | ✓ [diplomacy.py:404,411](backend/game_logic/diplomacy.py:404) | actor, victim, episode_id | NORMAL | `icon_chancery_reopened` | "The Chancery Reopens" | **MISSING** (presentation §12 has no clear-side template) | — | notification_bar NORMAL card | "Open Ledger" |
| 4 | `diplomatic_treaty_broken` (`french_breach`) | ✓ [diplomacy.py:796](backend/game_logic/diplomacy.py:796) | family, action, fault_nation, witnesses, deltas, episode_id | CRITICAL | `icon_treaty_broken` | "Word Broken" | `commitments_notice_*` (NEW) | `envoy` → Hardenberg/Metternich/Einsiedel | notification_bar CRITICAL card | "Review the broken treaty" |
| 5 | `diplomatic_treaty_broken` (other families) | ✓ same emit, family varies | (same) | NORMAL | `icon_treaty_dragged` | "Treaty Dragged Apart" | **MISSING** (§12 only dramatizes french_breach) | `foreign_office`? unstated | notification_bar NORMAL card | "Open Ledger" |
| 6 | `commitment_paradox_resolved` | ✓ [diplomatic_executor.py:2782,2870](backend/commands/diplomatic_executor.py:2782) | chosen_nation, spurned_nation, episode_id | NORMAL | `icon_paradox_resolved` | "The Wound Chosen" | §12.3 beat-3 in-popup aside | `talleyrand` (notice) / `system` (campaign log) | reinforced by after-choice aside **in popup**; NORMAL notice | — |
| 7 | `witness_strike_recorded` | ✓ [diplomacy.py:815](backend/game_logic/diplomacy.py:815) | witness, actor, victim, episode_id, scope_reason | NORMAL | `icon_witness_strike` | "Europe Is Aware" | §10.4 skeletal canonical line per scope | `system`/`foreign_office` — spec ambiguous | notification_bar NORMAL card | — |
| 8 | `diplomatic_treaty_broken` (`defensive_refusal_termination`) **NEW in §8.8.7a** | **MISSING** — not in `END_REASON_FAMILY_*` constants at [diplomacy.py:198-200](backend/game_logic/diplomacy.py:198) | (will need new family constant) | **UNSPECIFIED** (CRITICAL or NORMAL?) | **MISSING** icon | **MISSING** label | **MISSING** template | **MISSING** | **MISSING** | **MISSING** |
| 9a | Make Amends success (§8.6.1) | will emit `amends_offered` | episode_id, cleared_strike_lineage, diplomat | **UNSPECIFIED** | **MISSING** icon | **MISSING** label | **MISSING** template | target's named diplomat per Voice Bible | **UNSPECIFIED** surface | — |
| 9b | Make Amends grievance variant (§8.6.1a) | will emit `amends_offered` with `grievance_variant=True` | (as above) + origin_episode_id | **UNSPECIFIED** | **MISSING** | **MISSING** | **MISSING** | Talleyrand + target diplomat | **UNSPECIFIED** | "clicking grievance row" (§8.8.4) |
| 10 | Balance of Europe headline (§11.1) | derived per turn (no event) | hegemon, share, threat_level, coalition state, qualifying nations, leader | N/A (not a notice) | N/A | N/A | state-composed (no authored table) | coalition leader's named diplomat (Castlereagh fallback: "The courts of {leader}") | [diplomatic_ledger.gd](godot-client/project-sovereign/scripts/diplomatic_ledger.gd) | Nations tab default view |
| 11a | `call_to_arms_refused_offensive` (B-B4) | **not yet in code** | episode_id, breaker, victim, severity, call_context | **UNSPECIFIED** (spec §8.8.10 says "spotlight" but C3-lite cut spotlight) | **MISSING** | **MISSING** | **MISSING** (`commitments_notice_*` or new family?) | victim's diplomat per §8.8.10 | **MISSING** | **MISSING** |
| 11b | `call_to_arms_refused_defensive` | as above | + grievance_flag | **UNSPECIFIED** | **MISSING** | **MISSING** | **MISSING** | victim's diplomat (Voice Bible) | **MISSING** | **MISSING** |
| 11c | `call_to_arms_honored_costly` | as above (positive episode) | + loyalty_bond | **UNSPECIFIED** | **MISSING** | **MISSING** | **MISSING** | Talleyrand (honorer = France) | **MISSING** | **MISSING** |
| 12 | `oathbreaker_posture_triggered/cleared` | **not yet in code** | actor, window_turns, episode_id | **UNSPECIFIED** | **MISSING** | **MISSING** | **MISSING** | **MISSING** | **MISSING** | **MISSING** |

**13 rows, 9 fully defined, 4 partially defined, 6 fully MISSING.** All four missing rows are B-B4 (DG-4) or §8.6.1/§8.6.1a Make Amends. Rows 1–7 are the "three live events" the presentation spec owns; of those, `hard_reject_posture_cleared`, cascade-family `diplomatic_treaty_broken`, and `witness_strike_recorded` still read "render goes here but contract unstated."

## Findings

### BLOCKERS

**F1. DG-4 events have no UI surface contract.** [BLOCKER — UI fidelity §2, dimension 7]
- **Location:** [docs/RELIABILITY_COMMITMENTS_SPEC.md:758-768](docs/RELIABILITY_COMMITMENTS_SPEC.md) §8.8.10 vs [docs/COMMITMENTS_PRESENTATION_SPEC.md:213-220](docs/COMMITMENTS_PRESENTATION_SPEC.md) §8.1 event table + §13 core tasks.
- **Observation:** §8.8.10 says *"three new speaker=envoy / speaker=foreign_office event families are needed for C3-lite: `call_to_arms_refused_offensive`, `call_to_arms_refused_defensive`, `call_to_arms_honored_costly`. Each needs authored spotlight and notice copy in `diplomatic_templates.py`"* — but presentation spec §8.1 event routing table does not list any of the three; §9.2 icon/label table omits them; §13 core tasks mentions only the three "live" events (`hard_reject_posture_triggered`, `diplomatic_treaty_broken` (french_breach), `commitment_paradox`). The phrase "authored spotlight … copy" also contradicts C3-lite v0.5.1's §7.2 cut of the spotlight tier.
- **Impact:** B-B4 implementer has no tier assignment, no icon key, no label, no template family, no review route for 3 events (6 fire states counting refused/honored). Either ships without presentation (substrate-only — permitted by §8.8.13 but flagged there as "mechanic fires silently" UX risk), or implementer guesses the mapping — inconsistent across builds.
- **Fix:** Add to presentation spec §8.1 event routing table:

  | Event | Primary surface | Tier | Voice |
  |-------|-----------------|------|-------|
  | `call_to_arms_refused_offensive` | single-voice notice | CRITICAL | `envoy` → victim's diplomat |
  | `call_to_arms_refused_defensive` | single-voice notice | CRITICAL | `envoy` → victim's diplomat |
  | `call_to_arms_honored_costly` | single-voice notice | CRITICAL | `foreign_office` → "The Chancery of France" (Talleyrand register) |

  Add icons + labels to §9.2; add template stubs to §13 core tasks; replace §8.8.10's "authored spotlight and notice copy" with "CRITICAL notice copy (no spotlight tier in C3-lite v0.5.1)".

**F2. Presentation §12 worked examples contradict the v0.5.1 cuts.** [BLOCKER — internal consistency §1, dimension 7]
- **Location:** [docs/COMMITMENTS_PRESENTATION_SPEC.md:526,532,571,575,599](docs/COMMITMENTS_PRESENTATION_SPEC.md).
- **Observation:** The top-note v0.5.1 cut says *"Split-voice render (`attributed_lines[]`, typographic contract, reveal cadence) at §9.1"* and *"N+1 Talleyrand aside callback keyed by episode_id on breach and hard-reject (§9.4)"* are cut. §7.2 / §8.2 / §8.3 / §9.1 / §9.4 / §14 all collapsed to stubs. But §12 worked examples were never retrofitted:
  - §12.1 line 526: *"turn-N spotlight lands as a two-beat split-voice card"*
  - §12.1 line 532: *"Canonical mock spotlight templates"*
  - §12.1 line 552-554: **"Next-morning callback (one new beat, not a restate)"** — the CUT N+1 aside
  - §12.2 line 571: *"one featured spotlight tells the player that this channel is effectively closing"*
  - §12.2 line 575: *"Canonical mock spotlight template"*
  - §12.2 line 599-602: *"Optional N+1 aside (Talleyrand)"* — the CUT N+1 aside
- **Impact:** Implementer reading §12 committed-prose templates will absorb the v0.3 `spotlight` / two-beat / N+1 architecture and build it. The template slot names (`spotlight` / `lead` / `aside`) will leak into `commitments_notice_*` template keys, producing schema drift that the v2.4.2 C7 trim was supposed to eliminate.
- **Fix:** Retrofit §12.1 / §12.2 / §12.3 to single-voice-notice framing — relabel "spotlight" → "CRITICAL notice"; collapse "two-beat split-voice card" to "single-voice card with named-diplomat inline attribution"; delete the `Next-morning callback` and `Optional N+1 aside` blocks (they're CUT per §9.4); keep the canonical body prose per named diplomat. (The Hardenberg / Metternich / Einsiedel exemplars themselves are fine — just the staging and next-morning callback need to go.)

### MAJOR

**F3. §8.8.5 cross-reference to §8.8.8 is wrong.** [MAJOR — internal consistency]
- **Location:** [docs/RELIABILITY_COMMITMENTS_SPEC.md:692](docs/RELIABILITY_COMMITMENTS_SPEC.md:692): *"Emits `call_to_arms_honored_costly` spotlight through C3-lite presentation (see §8.8.8)"*.
- **Observation:** §8.8.8 is "Coalition-formation hook" (adds a threat signal); presentation surface for the honored-costly event lives in §8.8.10 ("Presentation surface (C3-lite event families)").
- **Impact:** Reader clicks through the cross-ref and lands on the wrong section.
- **Fix:** Change `see §8.8.8` → `see §8.8.10`. Also replace `spotlight` with `CRITICAL notice` per F1.

**F4. §8.8.10 names the wrong presentation tier.** [MAJOR — internal consistency, UI fidelity]
- **Location:** [docs/RELIABILITY_COMMITMENTS_SPEC.md:758,764,766](docs/RELIABILITY_COMMITMENTS_SPEC.md:758).
- **Observation:** *"three new speaker=envoy / speaker=foreign_office event families are needed for C3-lite"* + *"Each needs authored spotlight and notice copy in `diplomatic_templates.py`"* + *"Victim's diplomat leads the refusal spotlight"*. C3-lite v0.5.1 cut the spotlight tier entirely; the only live tiers are HARD_STOP (paradox only), CRITICAL, NORMAL.
- **Impact:** Both specs claim the same surface but describe it differently. B-B4 test authoring cannot pin the tier.
- **Fix:** Replace all three occurrences of "spotlight" with "CRITICAL notice" (or rewrite §8.8.10 against the CRITICAL/NORMAL routing from presentation §9.2). Verify with `grep -n spotlight docs/RELIABILITY_COMMITMENTS_SPEC.md` after the fix (expected: only historical / changelog / §7.2-stub / §12-stub references remain in presentation spec after F2).

**F5. Voice Bible header cites v0.3 of presentation spec; current is v0.5.1.** [MAJOR — internal consistency]
- **Location:** [docs/DIPLOMAT_VOICE_BIBLE.md:4,6,201,203,205](docs/DIPLOMAT_VOICE_BIBLE.md:4).
- **Observation:** Lines 4 and 6 reference "v0.3 scope note (Apr 16, 2026)" and "`COMMITMENTS_PRESENTATION_SPEC.md` v0.3 §10.3 requires only 4 lead-line templates". Header status line 3 still says "v1 draft — Apr 15, 2026". Line 203 heading: "Required for C3-lite (v0.3 — must land in this phase)".
- **Impact:** A contributor comparing Voice Bible cast requirements to presentation §10.3 sees version skew and may assume the Voice Bible is outdated and the cast minimum has changed. In fact the count (4 lines) still matches v0.5.1 §10.3 — so the version labels are the only problem.
- **Fix:** Bump Voice Bible status header to "v1.1 — v0.5.1 aligned"; replace `v0.3` references with `v0.5.1`; add a one-line changelog entry pointing at the v0.5.1 trim.

**F6. Presentation §12.1 §12.2 §12.3 templates are load-bearing but stale by voice-bible check.** [MAJOR — voice/copy fidelity]
- **Location:** [docs/COMMITMENTS_PRESENTATION_SPEC.md:534-554](docs/COMMITMENTS_PRESENTATION_SPEC.md:534) (Hardenberg / Metternich / Einsiedel leads + Talleyrand aside + Next-morning callback).
- **Observation:** The Hardenberg / Metternich / Einsiedel lead lines match their Voice Bible exemplars verbatim — good. The Talleyrand private aside "*They are wounded, Sire. Worse, they are entitled to be…*" matches Voice Bible line 43 (Talleyrand exemplar). But the "Next-morning callback" (line 552-554) and the "Optional N+1 aside" (line 599-602) reference the CUT N+1 architecture; they'll ship into a codebase that has no callback mechanism for them.
- **Impact:** Template text exists in spec; render plumbing does not. Either implementer builds the plumbing (contradicts cut), or they discard the lines (information loss — these lines are the *purpose* of committing prose).
- **Fix:** Delete the "Next-morning callback" and "Optional N+1 aside" blocks from §12.1 and §12.2 (they go to WB-D per §9.4 + §15 handoff). OR move them to a dedicated "Deferred to WB-D" appendix section so the lines are preserved as design intent without being mistaken for live contracts.

**F7. HIGH notification tier is undocumented in the spec but exists in the code.** [MAJOR — internal consistency]
- **Location:** [backend/notifications.py:19-21](backend/notifications.py:19) defines `NORMAL=0`, `HIGH=1`, `CRITICAL=2`. Presentation spec §9.2 priority tier table uses only CRITICAL and NORMAL.
- **Observation:** `MARSHAL_DEFIED_ORDER` already uses HIGH. It is not clear whether commitments events may use HIGH (between NORMAL and CRITICAL), and what the caller contract is.
- **Impact:** A future triage decision ("bump this to HIGH so it sorts above a cluttered NORMAL queue") has no documented constraint. Easy to accidentally split commitment events across two tiers in code review.
- **Fix:** Add a one-line note in presentation §9.2: *"Commitments events use CRITICAL or NORMAL only; the HIGH tier (used by `MARSHAL_DEFIED_ORDER`) is intentionally not used by this pass to keep the three live events visually distinct from military urgency."*

**F8. Plan B-Hegemony test list understates Balance of Europe case coverage.** [MAJOR — implementation plan coverage]
- **Location:** [docs/RELIABILITY_IMPLEMENTATION_PLAN.md:132](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:132): *"Balance of Europe headline composition across: no hegemon, France at 35%, France at 55% with Brewing coalition"*. Only three cases; spec §11.1 has four (no hegemon, hegemon without coalition, coalition BREWING, coalition DECLARED).
- **Observation:** Slice C-lite §14 line 741 does name all four ("the four state cases ... no hegemon, hegemon without coalition, coalition BREWING without leader, coalition DECLARED with leader"). So the test exists — but at C-lite, not B-Hegemony. B-Hegemony is the slice that lands the headline renderer in diplomatic_ledger.gd per plan line 225 C-lite claim. Ownership is split.
- **Impact:** An implementer splitting the work across B-Hegemony and C-lite may ship B-Hegemony without the DECLARED case tested (since it sits in C-lite), then never add it in C-lite (test already "exists" — but only 3 cases).
- **Fix:** Expand B-Hegemony test bullet to all four cases, OR explicitly state the DECLARED case is C-lite's. Remove the duplication by owning all four state-case tests in C-lite (since the renderer sits there per line 747 / §14 line 741) and dropping the B-Hegemony bullet.

### MINOR

**F9. §11.1 Case 2 fuzzy edge: flavor line only fires for `threat_level ≥ 30 and < 40`.** [MINOR — fuzzy edges]
- **Location:** [docs/RELIABILITY_COMMITMENTS_SPEC.md:1026](docs/RELIABILITY_COMMITMENTS_SPEC.md:1026).
- **Observation:** Case 2 is "Hegemon exists, no coalition." Flavor line ("*European courts have taken note…*") fires only in the 30–40 Tension band. Hegemon with `threat_level < 30` gets what?
- **Impact:** The renderer will either show bare hegemon line alone (likely intended), or accidentally hide the Case 2 block.
- **Fix:** Spell out: *"When `threat_level < 30` with a hegemon present, render only the hegemon line; the flavor line is suppressed."*

**F10. §11.1 Case 1 internally contradicts.** [MINOR — fuzzy edges]
- **Location:** [docs/RELIABILITY_COMMITMENTS_SPEC.md:1018-1021](docs/RELIABILITY_COMMITMENTS_SPEC.md:1018).
- **Observation:** *"No coalition line follows (coalition brewing still possible from event-based threat; if active, its line appears below)."* No line follows, then a line appears below. Which is it?
- **Impact:** Ambiguous; the implementer will pick either and the playtest will be the decider.
- **Fix:** Rewrite: *"The equilibrium line is standalone. If a coalition is independently brewing from event-based threat (battles, captures) a BREWING line from Case 3 may still render below it; the equilibrium and BREWING lines are composable."*

**F11. `hegemony_target_mod` comment vs code: bucket edge.** [MINOR — code snippet correctness]
- **Location:** [docs/RELIABILITY_COMMITMENTS_SPEC.md:843-848](docs/RELIABILITY_COMMITMENTS_SPEC.md:843).
- **Observation:** Comment says *"clamped at -20 from 63.33%+ onward."* Numeric check: share=0.6333 → raw = int((0.6333 − 0.30) × 60) = int(19.998) = 19, so mod = −19. Share=0.6334 → raw = int(20.004) = 20, mod = −20. The clamp actually kicks in at 63.34%, not 63.33%. Off-by-one in the prose comment.
- **Impact:** Trivial — only affects someone reasoning about the exact boundary pixel. Playtest will round to 63% anyway.
- **Fix:** Change "from 63.33%+ onward" → "from ~63.34%+ onward (integer truncation of raw = 20 clamps to max ceiling)".

**F12. §10.3 has a self-reference.** [MINOR — prose]
- **Location:** [docs/COMMITMENTS_PRESENTATION_SPEC.md:402](docs/COMMITMENTS_PRESENTATION_SPEC.md:402).
- **Observation:** *"`system` is disallowed on rail surfaces per §10.3"* — appears inside §10.3.
- **Fix:** Either drop the `per §10.3` qualifier, or move the rule into §10.3 proper and reference it from the table without the circular cite.

**F13. Non-France-hegemon guard logging channel is undefined.** [MINOR — fuzzy edges]
- **Location:** [docs/RELIABILITY_COMMITMENTS_SPEC.md:319](docs/RELIABILITY_COMMITMENTS_SPEC.md:319) + [docs/RELIABILITY_IMPLEMENTATION_PLAN.md:109](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:109).
- **Observation:** *"emit a debug log for telemetry and skip the `add_threat` call this turn"*. No log channel / level / message-format named.
- **Impact:** Implementer will choose a channel; it may differ from the rest of coalition.py's telemetry.
- **Fix:** Add to plan B-Hegemony helper: *"Log message: `[hegemony] non-France hegemon detected ({hegemon_nation} @ {share:.2f}); skipping add_threat (threat scalar France-targeted in v0.1)`. Channel: stdlib `logging` at INFO, same as existing `coalition.py` telemetry."*

**F14. Named-diplomat resolver fallback for nations beyond the 5-cast roster is specced but not implementable until cast expands.** [MINOR — voice/copy fidelity]
- **Location:** [docs/COMMITMENTS_PRESENTATION_SPEC.md:413,415](docs/COMMITMENTS_PRESENTATION_SPEC.md:413), [docs/RELIABILITY_COMMITMENTS_SPEC.md:378](docs/RELIABILITY_COMMITMENTS_SPEC.md:378).
- **Observation:** §10.3 says `speaker="envoy"` MUST resolve to a named diplomat; §10.3 also mentions a "loyalist fallback" that should "fail loudly." Spec §7.7 scale table mentions *"13+ named diplomats or generic-register fallback for unnamed minors"* — but the fallback is a scale-item, not a v0.1 contract. Current cast: 5 nations (France + Britain + Austria + Prussia + Saxony). Ottoman / Sweden / Spain / Portugal etc. have no diplomats; if an event fires for one of those nations (no immediate path in v0.1, but possible with `diplomatic_treaty_broken` cascade on a non-major), the resolver has no fallback.
- **Impact:** On today's 5-nation map this is latent. Not a blocker.
- **Fix:** Add to §10.3: *"v0.1 scope assumes the 5-nation roster. If a future event targets a non-cast nation, the render falls back to `foreign_office` → 'The Chancery of {nation}' with no personality register until the cast expands."*

**F15. Plan Test Budget total arithmetic.** [MINOR — internal consistency]
- **Location:** [docs/RELIABILITY_IMPLEMENTATION_PLAN.md:329](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:329).
- **Observation:** v2.4.3 total row: "~45-54". Sum of rows: B-Hegemony 18-22 + B1-lite 7-8 + B7 8 + B3 3 + Slice C-lite 10-12 = 46-53. Close but not an exact match to "45-54" (off by 1 on the low end). Trivia.
- **Fix:** Correct to "~46-53" for arithmetic exactness, or leave as "~45-54" since the ranges are approximate anyway and flag the cell as "approx."

## Missing artifacts

Files / helpers / events the specs name but which do not exist and are not scheduled by the plan:

- **None blocking.** Everything the specs name is either (a) already in `master` (the shipped substrate), (b) explicitly scheduled by a plan slice (B-Hegemony / B-B1-lite / B-B3 / B-B7 / B-B4 / C-lite), or (c) stubbed as deferred to WAR_BARGAIN_SPEC.
- **`commitment_paradox_popup.{tscn,gd}`** — correctly scheduled by C-lite §14. Existing `godot-client/project-sovereign/scripts/alliance_paradox_popup.gd` must not be reused per presentation spec §12.3 implementation contract. Currently `alliance_paradox_popup.{tscn,gd}` is the only paradox popup on disk. [OK — expected; C-lite builds the replacement.]
- **Icon art for `icon_treaty_broken`, `icon_paradox`, etc.** — presentation spec §9.2 explicitly flags *"Icon keys are proposed names; actual art is commissioned later."* [OK — not a spec gap.]
- **`END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION`** — spec §8.8.7a introduces the new family; [backend/game_logic/diplomacy.py:198-200](backend/game_logic/diplomacy.py:198) currently defines only `FRENCH_BREACH`, `COUNTERPARTY_REVERSAL`, `OBSOLESCENCE_OR_EXTERNAL`. Needs a constant + an add to `_derive_end_reason_family()`. Plan B-B4 §196 correctly names it; not missing from the plan, just not yet coded.

## Cross-spec value table

| Shared value | Location in each spec | Match? |
|--------------|-----------------------|--------|
| Pressure ladder `1/3/5/8` | `RELIABILITY_COMMITMENTS_SPEC` §7.3 line 307 / §11.1 cross-ref / `COALITION_SPEC` §2a line 69 / `RELIABILITY_IMPLEMENTATION_PLAN` §B-Hegemony | ✓ |
| Hegemony share threshold `30%` | Spec §7.3 / §9.5 table / §11.1 equilibrium boundary / `COALITION_SPEC` §2a passive-row trigger | ✓ |
| Share buckets `30 / 40 / 50 / 60` | Spec §7.3 `_hegemony_pressure_for_share` / §9.5 table | ✓ |
| `bilateral_betrayal_mod = -6 per strike` | Spec §9.2 / plan §B-B1-lite | ✓ |
| Hard-reject threshold `3 strikes` | Spec §8.7 / §9.2 / already shipped in `diplomacy.py:has_hard_reject_posture` | ✓ |
| Episode cap `+2 victim strikes per episode` | Spec §8.3 / §8.7 | ✓ |
| Make Amends standard cost `200g + 1 DP` | Spec §8.6.1 / plan §B-B7 line 177 | ✓ |
| Make Amends grievance-variant cost `400g + 2 DP` | Spec §8.6.1a line 593 / §8.8.4 line 678 / plan §B-B4 line 195 | ✓ |
| Make Amends standard relation +5 / reliability +2 | Spec §8.6.1 line 556-557 / plan §B-B7 line 177 | ✓ |
| Grievance-variant relation +8 / reliability +3 | Spec §8.6.1a line 607-608 | ✓ (plan §B-B4 line 195 says "+3/+8" matches) |
| Make Amends cooldown 10 turns (shared) | Spec §8.6.1 line 558 / §8.6.1a line 592 / plan §B-B7 line 177 | ✓ |
| Grievance stacking cap `3 per pair` | Spec §8.8.4 line 679 / §9.3 line 901 | ✓ |
| Composite floor `-60` (with DG-4) | Spec §9.3 line 894 / plan Merge-ordering §275-285 | ✓ |
| `grievance_modifier = -30 per grievance` | Spec §8.8.9 line 751 / §9.3 line 898 | ✓ |
| Anti-renewal cooldown window | Spec §8.8.7 "candidate 15 turns" — NOT locked | **Candidate only.** Not a v2.4.3 gap; §8.8.7 explicitly authored as tunable. |
| Oathbreaker `N=2, M=15` | Spec §8.8.6 "authored — candidate" | **Candidate only.** Same. |
| Honor bias default `1.0` | Spec §8.8.12 | ✓ |
| `_POWER_TIER_DEFAULT = "secondary"` | Spec §7.2 line 246 / plan §B-Hegemony line 93 | ✓ |
| BREWING / DECLARED state names | Spec §11.1 Cases 3/4 / `COALITION_SPEC` §3-§4 | ✓ (cross-ref in §11.1 correct) |
| `end_reason_family` enum values | Spec §8.8.7a introduces `defensive_refusal_termination`; [backend/game_logic/diplomacy.py:198-200](backend/game_logic/diplomacy.py:198) has `french_breach`, `counterparty_reversal`, `obsolescence_or_external` | **Spec-only** — constant not yet in code (expected; B-B4 adds) |
| Speaker enum (`talleyrand`/`envoy`/`foreign_office`/`system`) | Presentation spec §10.3 / §11 payload | ✓ |
| Test budget (total) | Plan §329 row: "~45-54". Arithmetic sum: 46-53. | Off by 1 (see F15) |
| Test budget (B-Hegemony) | Plan §318 row: 18-22. Spec §13 line 1190: ~18-22. | ✓ |
| Test budget (C-lite) | Plan §326 row: 10-12. Presentation §14 line 748: 10-12. | ✓ |
| Test budget (B-B4) | Plan §327 row: 25-29. Spec §8.8.13 line 807: ~25 new. Spec §13 line 1195: ~25-29. | Close but §8.8.13 and plan disagree in the range (25 vs 25-29). Trivia. |
| CLAUDE.md "Up Next" | v2.4.3, ~45-54 tests, merge gate B-B4 at/after B-B1-lite, DG-4 parallel | ✓ |
| Voice Bible cast coverage | Voice Bible §Minimum 4 lines / Presentation §10.3 4-line minimum | ✓ (but see F5 version label) |

**Mismatch summary:** all shared *numeric* values agree across specs. Version-label mismatches (F5), cross-reference wrong target (F3), and the §8.8.10 spotlight-vs-CRITICAL wording (F4) are the real consistency issues, not numeric drift.

## Recommendation

**REQUEST-CHANGES.**

Two blockers (F1, F2) and F3–F6 ship from the same root cause: the v2.4.2 C7 "non-normative bulk trim" missed §12 of the presentation spec and missed the §8.8 DG-4 presentation hand-off. These are straightforward doc-level edits — no design thinking needed, just retrofitting the trim decision into the sections that didn't get it.

Recommended pre-merge sequence (pure doc work, one session):

1. Fix F1 — add the three DG-4 events to presentation §8.1 event-routing table + §9.2 icon/label table + §13 core task list; replace "spotlight" with "CRITICAL notice" in §8.8.10 and §8.8.5.
2. Fix F2 — retrofit §12.1/§12.2/§12.3 to single-voice framing; delete Next-morning callback and Optional N+1 aside blocks (content preserved in `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` per the §14 historical-note pattern).
3. Fix F3 — cross-ref §8.8.5 from §8.8.8 → §8.8.10.
4. Fix F4 — sweep RELIABILITY_COMMITMENTS_SPEC.md for remaining `spotlight` live references; the only permitted remaining use is historical changelog prose.
5. Fix F5 — bump Voice Bible version header and replace v0.3 refs with v0.5.1.
6. Fix F6 — delete or relocate the Next-morning callback / N+1 aside prose in §12.
7. Fix F7 — add HIGH-tier clarifying note in §9.2.
8. Fix F8 — collapse Balance-of-Europe case-test ownership to C-lite.

Minors (F9-F15) can land in the same pass or the next — none are merge-gating.

Once F1–F8 land, the spec ensemble is implementation-ready. Engine design is coherent; code snippets run; plan slices cover the normative contracts; CLAUDE.md phase-row is truthful.
