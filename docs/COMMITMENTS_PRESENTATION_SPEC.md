# Commitments Presentation Pass — C3-lite Spec

> **Status:** v0.5.3 (D3 per-row bloc stamps landed after C-lite closeout; Block 3 bloc-naming contract folded in; audit doc superseded)
> **Date:** April 20, 2026 (v0.5.2 — bloc-naming contract folded from Block 3 audit; v0.5.1 — non-normative bulk trimmed); April 19, 2026 (v0.5 — v2.4 hegemony alignment); April 16, 2026 (v0.4 audit); v0.3 rescope; v0.1 April 15, 2026
> **Phase placement:** Final slice of `Memory and Pressure` track (formerly `Reliability + Commitments`).
> **Depends on:** `RELIABILITY_COMMITMENTS_SPEC.md` v2.4.3 (hegemony engine + Balance of Europe headline + paradox rename + deep-audit fixes), `RELIABILITY_IMPLEMENTATION_PLAN.md` v2.4.3, `DIPLOMAT_VOICE_BIBLE.md`, `CONVERSATIONAL_DIPLOMACY_DESIGN.md`, `INFORMATIONAL_UI_PLAN.md`
> **Bargain-era continuation:** `WAR_BARGAIN_SPEC.md` slice WB-D (presentation extension that adds bargain showpiece beats, scope-branched copy, response routes — only after `WAR_BARGAIN_SPEC` ships).

**Repo reality check (April 25, 2026 supersedes the April 22 historical note below).** The `balance_of_europe_shifted` notice family, Balance of Europe ledger payload/headline, DG-4 call-to-arms routing rows, and D3 Nations-tab row stamps are now live in code. `threat_coalition` remains as a compatibility payload while `balance_of_europe` is the normative presentation owner. Remaining polish is authored prose/named-diplomat depth for future copy passes, not a missing substrate.

---

## v0.5.1 Scope Note (April 20, 2026) — Non-normative bulk trimmed

v0.5.1 trims the sections the v0.5 top-note disclaimed (v2.4.2 deep-audit C7 action). The spec no longer documents infrastructure that v2.4 cancelled; cut sections are collapsed to short stubs pointing to the historical design in `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md`.

**v0.5.1 ship list (the only content now considered authoritative):**

- ✓ **Named-diplomat resolution helper** — `speaker="envoy"` resolves to the nation's named diplomat per Voice Bible; `speaker="foreign_office"` resolves to "The Chancery of {nation}". §10.3 is authoritative.
- ✓ **Committed mock prose** for the three live events using Voice Bible registers: `hard_reject_posture_triggered`, `diplomatic_treaty_broken` (`end_reason_family=french_breach`), `commitment_paradox_resolved`. §12 worked examples remain authoritative.
- ✓ **Dedicated `commitment_paradox_popup.{tscn,gd}` surface** — replaces legacy `alliance_paradox_popup` for the renamed type. All three paradox beats (framing → blocking body → after-choice aside) render in the popup itself.
- ✓ **Balance of Europe headline** — five base composition cases per `RELIABILITY_COMMITMENTS_SPEC.md` §11.1 (no hegemon, hegemon without coalition, coalition BREWING without leader, coalition DECLARED with leader, coalition COOLDOWN), plus the legal `NO_HEGEMON + BREWING` composite. Rendering lives in `diplomatic_ledger.gd`.
- ✓ **Same-turn `balance_of_europe_shifted` notice family** — the 33% / 50% / 60% hegemony threshold beat fires before coalition declaration can become the player's first clue, using named-diplomat or chancery voice per the routing table in §8.1. Turn 1 does **not** emit a beat for inherited opening share: `world.hegemony_signal_high_water` and `world.hegemony_signal_hegemon` bootstrap from scenario-start bloc geometry, so the first beat fires on the first **new** band crossing after play begins. Scenarios that open above `33%` therefore do not stage the noticed beat unless share first drops below `33%` and later rises back through it (see `RELIABILITY_COMMITMENTS_SPEC.md` §7.3 for the bootstrap rule).
- ✓ **`amends_offered` lightweight notice family** — successful repair gestures must surface as public political theater, not only as result text or campaign-log bookkeeping.
- ✓ **Period-vocabulary icons / labels** and **priority tiers** per §9.2.
- ✓ **Bloc-naming contract** — `33 / 50 / 60` activation gate, authored hegemon→label taxonomy, surface routing, and terminology guard per §8.1a. Authoritative for the adopted naming language in v2.4.3. The in-scope naming-layer surfaces are the Balance of Europe headline, `balance_of_europe_shifted` threshold beats, proposal-preview `hegemony` warnings, and coalition-declaration contrast copy — four surfaces, no more.
- ✓ **Member badges / per-row bloc stamps** — opened after v2.4.3 closeout as D3. Nations rows now carry transient `nations[*].bloc_stamp` payloads and the Godot Nations tab renders them beside court names. The stamp surface remains subordinate to the Balance headline and reuses `describe_hegemon_bloc(...)`.

**Cut from v0.3/v0.4 (now collapsed to stubs in place):**

- ❌ **Elevated rail tier** on notification rail (§7.2, §8.2, §8.3)
- ❌ **Split-voice render** (`attributed_lines[]`, typographic contract, reveal cadence) at §9.1
- ❌ **N+1 Talleyrand aside callback** keyed by `episode_id` on breach and hard-reject (§9.4)
- ❌ **A1-fill, A2 fill, B2a-fill, B6** upstream dependencies (all cancelled in v2.4)

**Reading order:** sections below are normative except for the dated historical notes and changelog entries. Prior v0.3/v0.4 content that was non-normative has been removed from the live contract rather than disclaimed in place. For design history on the cut infrastructure (why it was specced, how it rendered), see `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md`.

**Historical repo reality check (April 22, 2026; superseded by April 25 note below).** The surfaces specced below — `balance_of_europe_shifted` notice family, Balance of Europe headline, proposal-preview `hegemony` warnings with private-tally / descriptive / proper-noun wording, coalition-declaration contrast copy — are **not yet built**. Live code still ships the older `threat_coalition` ledger payload (`backend/game_logic/diplomatic_ledger.py`), the legacy `NATION OVERVIEW` Nations tab, and the anonymous `Diplomatic Tension` / `European Courts Concerned` notifications (`backend/game_logic/coalition.py:1098-1132`). Meanwhile `backend/display_names.py` + `backend/game_logic/diplomacy.py` already relabel AI `decision_reason` to `hegemony_pressure`, but the mechanical `hegemony_target_mod` acceptance term and the preview `hegemony` warning construction are still pending B-Hegemony + B-B1-lite — so "hegemony pressure" is currently a **label over legacy coalition-threat math**, not the new mechanic. Slice C-lite lands as the substrate swap that retires the legacy anonymous clue chain and the Threat & Coalition ledger tab, replacing them with the headline + beats + warnings owner contract below. Do not read this spec as describing something already live; read it as the target contract for the swap.

**Estimated tests:** ~10-12 for the original C-lite pass (named-diplomat resolution for each of 5 nations, three live-event copy paths plus `balance_of_europe_shifted`, `amends_offered` attribution, paradox popup field wiring, Balance of Europe headline composition across the five base cases plus the legal `NO_HEGEMON + BREWING` composite). D3 row-stamp follow-up coverage later landed in the ledger focused suites.

---

## v0.3 Rescope Note (April 16, 2026)

The April 16 audit established that the v0.2 spec was specced two audit rounds deep (`C3a` routing + `C3b` drama) for events the engine cannot produce. War bargains were never implemented, and the `bargain_*` events the spec dramatized — `bargain_fulfilled`, `bargain_breached`, `bargain_triggered`, `bargain_voided`, `bargain_ratified` — cannot fire in the current build.

The rescope:

1. **War bargain presentation moves to `WAR_BARGAIN_SPEC.md` slice WB-D**, where it lands when the bargain mechanic itself ships in the Peace Deals phase.
2. **`C3a` + `C3b` collapse into one `C3-lite` slice** that ships alongside the rest of `Memory and Pressure`.
3. **Three live events get the full named-diplomat treatment on existing surfaces**: `hard_reject_posture_triggered`, `diplomatic_treaty_broken` (where `end_reason_family = french_breach`), and `commitment_paradox_resolved`.
4. **Paradox §12.3 staging simplifies from 5 beats to 3 beats** — Talleyrand framing → blocking body → spurned-envoy + Talleyrand after-choice. The five-beat scene with envoys from both spurned nations speaking before Talleyrand requires bargains-driven multi-conflict ratification (which doesn't exist in v0.1) to feel justified.
5. **Reactive affordances cut to advisory routes only**. Response routes (`Propose redress`, `Deepen the bond`, `Attempt to reopen the chancery`, `Denounce the refusal`) move to WB-D — they depend on bargain templates and on proposal_options seed defaults that don't exist yet.
6. **N+5 fallback grievance slot cut** as edge-case polish.
7. **Overflow emphasis digest cut** — multi-climax turns are rare on the 5-nation map; revisit if playtest shows the cap is starving climactic turns.

**Preserved from v0.2 (the flavor that matters):**

- Elevated fourth-tier rail card on the notification bar (2-turn persist, action buttons)
- Split-voice render (`attributed_lines[]` with `lead` / `witness` / `aside` regions)
- Typographic + cadence contract for split-voice (§9.1)
- Named-diplomat resolution mandatory for `envoy` and `foreign_office` per Voice Bible (§10.3)
- Committed mock prose for the three live events
- Period labels in player-facing notice icons (§9.2)
- One N+1 Talleyrand aside keyed by `episode_id`
- Dedicated `commitment_paradox_popup.{tscn,gd}` surface
- Anti-spam rules, no-duplicate-surface rule, dispatch carryover

The v0.2 audit findings (F1-F8, P2-H1 through P2-H10) and prior version of this spec are preserved in `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` for design history; they should not be re-read as live requirements.

---

## 1. Purpose

The Memory and Pressure substrate now creates real political moments:

- betrayal memory (graded acceptance impact + hard-reject posture)
- hegemony pressure (bloc-share friction + Balance of Europe headline)
- commitment paradox hard stops (renamed alliance-cross-war; `commitment_paradox_resolved` log only, with no cross-surface dispatch callback)

What it does **not** yet do is make those moments feel important in play. They land as one-liner notification rows.

This spec defines the narrow presentation pass that delivers political weight for the events that *do* fire today, without inventing drama for events that don't (those go to WB-D).

The pass remains **mechanically inert**. It owns framing, pacing, and surfacing. It does not own any diplomatic outcome.

---

## 2. Phase Placement

Final slice of `Memory and Pressure`. Sits after the spec/plan code work (B-Hegemony, B-B1-lite, B-B3, B-B7) and alongside the tightened DG-4 slice when those events need presentation follow-through. Before any bargain work.

```text
A1 (✓) → B-Hegemony (bloc helpers + Balance of Europe)
      → B-B1-lite (collapsed acceptance formula)
      → B-B3 (paradox rename)
      → B-B7 (standard Make Amends)
      → C3-lite (this spec)
      → END OF MEMORY AND PRESSURE PHASE
[Parallel: B-B4 DG-4 call-to-arms follow-through, including grievance-variant Make Amends and defensive-refusal termination]
[Peace Deals phase later: Bilateral Peace Hardening → War Purpose → WAR_BARGAIN_SPEC → WB-D bargain presentation]
```

What this is **not**:

- not `D1` strategic-focus AI work
- not common peace
- not coalition generalization
- not generic diplomacy polish
- not a new screen-family project
- not the bargain presentation pass (that is WB-D in `WAR_BARGAIN_SPEC.md`)

---

## 3. Problems To Solve

### P1. The three live commitments events land as accounting

`hard_reject_posture_triggered`, `diplomatic_treaty_broken` (french_breach), and `commitment_paradox_resolved` all emit rich payloads. Players see them as one-liner notification icons indistinguishable from "Relations with Prussia have worsened."

### P2. Existing surfaces are not commitments-aware

Notification rail has three priority tiers rendered as identical 38×28 icons with color rings. There is no elevated fourth tier. Popup scenes have one text region. There is no split-voice render.

### P3. The named cast is benched at the critical beats

`speaker="envoy"` and `speaker="foreign_office"` are emitted in metadata but resolve nowhere. The Voice Bible defines five named diplomats with distinct registers; none reach the player.

### P4. Player needs felt closure without new mechanics

The presentation layer should make the substrate's existing events feel alive without reopening engine rules, timing, or AI outcomes.

---

## 4. Goals

- Make the three live events feel memorable.
- Keep all mechanics deterministic and unchanged.
- Reuse existing surfaces rather than inventing a new diplomacy UI family.
- Ensure mock mode stays fully valid without LLM prose.
- Commit canonical mock-mode prose templates for each live event.
- Stage the paradox across more than one beat so it feels remembered, not just emitted.
- Restore one no-cost player advisory hook so the player isn't only a reader.
- Keep the pass narrow enough to ship as a single focused slice.

---

## 5. Non-Goals

- Does **not** change betrayal numbers, paradox rules, hard-reject thresholds.
- Does **not** redesign Morning Dispatch globally.
- Does **not** redesign the broader Talleyrand desk / trend / explanation surface.
- Does **not** add common peace, settlement allocation, or beneficiary spoils theatrics.
- Does **not** add new screen families, cinematic cutscenes, or map animations.
- Does **not** make LLM prose mandatory. Mock templates remain authoritative.
- Does **not** own coalition UI generally.
- Does **not** set rail-wide notice caps. Rail-wide budget ownership stays with `INFORMATIONAL_UI_PLAN.md`; this spec only defines commitments-local usage within that existing budget.
- Does **not** add new commitment outcomes, negotiation branches, or action costs.
- Does **not** dramatize bargain events (deferred to `WAR_BARGAIN_SPEC.md` slice WB-D).
- Does **not** add response-route reactive affordances (deferred to WB-D).

---

## 6. Design Principle

The voice layer is a **render layer over deterministic engine output**.

For commitments events:

- the engine decides what happened
- the presentation router decides how prominently it should be surfaced
- templates or LLM prose decide how it sounds

Golden rules:

- no presentation layer may change score, state, cooldown, or outcome
- every dramatic line must be traceable to an existing deterministic payload
- one political moment should feel like one moment, not five duplicated notifications

---

## 7. Presentation Model

This pass uses existing surfaces only: blocking popups, CRITICAL/NORMAL notices, and the durable ledger / campaign log reference layer. There is no new elevated rail tier in v0.5.1.

### 7.1 Blocking hard-stop

Use only when the player must decide **now**.

Already exists:

- `commitment_paradox` (renamed in B3 from `alliance_paradox`)
- `force_declare_war_confirmation`, `force_break_treaty_confirmation`

This spec does not create new hard-stop mechanics. It improves copy, emphasis, and fallout framing on `commitment_paradox` only (the other two already render their warnings via `proposal_confirm_popup`).

### 7.2 Dispatch spotlight — CUT in v0.5

**Status: not built in this phase.** v2.4 (see top-note) cut the elevated spotlight tier on the notification rail (larger card, 2-turn persist, `Spotlight Carryover` dispatch section). Three live events do not justify the infra; named-diplomat copy on the existing notification system carries the dramatic weight instead.

Live events route through the existing `notification_bar.gd` priority tiers: `hard_reject_posture_triggered` and `diplomatic_treaty_broken` (french_breach) both render as CRITICAL-priority notices with named-diplomat attribution. No new rail tier, no `Spotlight Carryover` section on Morning Dispatch, no 2-turn persist.

(Prior v0.2-v0.4 content that specified the spotlight tier infrastructure was removed in v0.5.1. See `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` for the historical design.)

### 7.3 Persistent notice

Existing tier. Used for medium-weight events. Remains visible and reviewable, does not stop play.

### 7.4 Ledger / campaign log reference

Every commitments event still appears in the durable reference layer. Ledger and log remain the source of truth.

---

## 8. Event Routing

### 8.1 Routing join-table (v0.5.1 ship list)

| Event family | Priority | Icon key | Player label | Template key | Speaker resolver | Review target |
|------|------|------|------|------|------|------|
| `commitment_paradox` | `HARD_STOP` (popup) | `icon_paradox` | Conflicting Oaths | `commitments_notice_paradox` | `talleyrand` | `ledger_commitments` |
| `balance_of_europe_shifted` | `NORMAL` at `33%`; `CRITICAL` at `50%` / `60%` | `icon_balance_of_europe` | Balance of Europe Shifts | `commitments_notice_balance_of_europe_shifted` | **Fallback chain (authoritative):** `envoy` -> named diplomat for `speaker_nation`; else Talleyrand advisory (his bloc-naming register per `DIPLOMAT_VOICE_BIBLE.md`); else `foreign_office` -> `The Chancery of {nation}` | `Open Ledger` |
| `amends_offered` | `NORMAL` | `icon_amends_offered` | Amends Offered | `commitments_notice_amends_offered` | `envoy` -> target court's named diplomat | `Open Ledger` |
| `hard_reject_posture_triggered` | `CRITICAL` | `icon_hard_reject` | The Chancery Shut | `commitments_notice_hard_reject_triggered` | `foreign_office` -> `The Chancery of {nation}` | `Open Ledger` |
| `hard_reject_posture_cleared` | `NORMAL` | `icon_chancery_reopened` | The Chancery Reopens | `commitments_notice_hard_reject_cleared` | `foreign_office` -> `The Chancery of {nation}` | `Open Ledger` |
| `diplomatic_treaty_broken` (`french_breach`) | `CRITICAL` | `icon_treaty_broken` | Word Broken | `commitments_notice_breach_french` | `envoy` -> injured party's named diplomat | `Review the broken treaty` |
| `diplomatic_treaty_broken` (other families) | `NORMAL` | `icon_treaty_dragged` | Treaty Dragged Apart | `commitments_notice_breach_other` | `foreign_office` -> context nation | `Open Ledger` |
| `commitment_paradox_resolved` | `NORMAL` | `icon_paradox_resolved` | The Wound Chosen | `commitments_notice_paradox_resolved` | `talleyrand` (notice) / `system` (campaign log) | — |
| `witness_strike_recorded` | `NORMAL` | `icon_witness_strike` | Europe Is Aware | `commitments_notice_witness_strike` | `system` / `foreign_office` per scope | — |
| `call_to_arms_refused_offensive` | `CRITICAL` | `icon_call_refused_offensive` | Pact Dishonoured | `commitments_notice_call_refused_offensive` | `envoy` -> victim's diplomat | `Open Ledger` |
| `call_to_arms_refused_defensive` | `CRITICAL` | `icon_call_refused_defensive` | Ally Abandoned | `commitments_notice_call_refused_defensive` | `envoy` -> victim's diplomat | `Open Ledger` |
| `call_to_arms_honored_costly` | `CRITICAL` | `icon_call_honored_costly` | Oath Kept | `commitments_notice_call_honored_costly` | `foreign_office` -> `The Chancery of France` | `Open Ledger` |

Single source of truth: notifications, dispatch formatting, campaign log labels, popup routing, and ledger review actions MUST derive priority / icon / label / template / voice / review-target from this table. Do not hardcode a second copy elsewhere.

`balance_of_europe_shifted` is the same-turn 33% / 50% / 60% hegemony preview beat from `RELIABILITY_COMMITMENTS_SPEC.md` §7.3 / §11.1 and `RELIABILITY_IMPLEMENTATION_PLAN.md` B-Hegemony. It exists so coalition declaration is never the player's first clue. The `50%` proper-name reveal and `60%` crisis beat are intentionally `CRITICAL`; the `33%` notice may remain `NORMAL`. **Speaker fallback chain on this family is strictly three-step and identical across all consumers** (notification rail, dispatch, campaign-log render, and any preview warning that repeats the voice): (1) `envoy` -> named diplomat for `speaker_nation`; (2) else Talleyrand advisory in his bloc-naming register; (3) else `foreign_office` -> `The Chancery of {nation}`. Talleyrand is ALWAYS preferred over a generic non-cast chancery so the beat stays voiced rather than bureaucratic; the chancery is the last resort. This rule is also the authoritative source for `RELIABILITY_COMMITMENTS_SPEC.md` §7.3 speaker selection and `DIPLOMAT_VOICE_BIBLE.md` Bloc-naming voice contract — the three docs do not disagree. In v2.4.3 this family keeps its locked review target only: rail notice + dispatch/log presence + `Open Ledger`. It is explicitly exempt from the generic CRITICAL advisory-route rule in §12.4 so Block 3 scope does not silently widen.

Both standard and grievance-variant Make Amends route through `amends_offered`. The target court's named acknowledgment is mandatory so apology reads as public politics rather than a quiet stat purchase.

### 8.8 DG-4 call-to-arms presentation closure

DG-4 call-to-arms event families are the three rows in §8.1: `call_to_arms_refused_offensive`, `call_to_arms_refused_defensive`, and `call_to_arms_honored_costly`. They must remain `CRITICAL`, must route to `Open Ledger`, and must derive icon / label / template / speaker metadata from the §8.1 table. Defensive and offensive refusals use `envoy -> victim's diplomat`; costly honor uses `foreign_office -> The Chancery of France` unless a later voice pass explicitly authors a narrower court-specific resolver.

`witness_strike_recorded` rows caused by one DG-4 root episode collapse to one summarized presentation row outside the exact ledger, keyed by `episode_id`; individual witness records may remain in the saved event/dispatch substrate for auditability.

### 8.1a Bloc-naming contract (normative for v2.4.3)

v2.4.3 adopts deterministic bloc naming. This section is the single normative owner of the bloc-label contract; earlier drafts lived in `docs/audits/MP_V243_BLOCK3_BLOC_NAMING.md` and have been folded here.

#### 8.1a.1 Terminology guard (BLOCKER)

- Reserve the word `coalition` for the **formal anti-hegemon war structure** in `backend/game_logic/coalition.py`.
- Hegemon-side peace-time camps use `bloc`, `alignment`, `system`, `circle`, or `interest` depending on surface.
- Never show "French Coalition," "British Coalition," etc. for a hegemon-side camp — a "coalition" label reads as war already declared.
- Any future grep of player-facing strings must show `coalition` only on the anti-hegemon side, never on hegemon-bloc labels.

#### 8.1a.2 Activation gate — `33 / 50 / 60`

Proper bloc names do not appear at the first visibility threshold. The player feels the *gravitation* first, then hears the *name*.

| Bloc share | State | Label behavior |
|---|---|---|
| `< 30%` | not surfaced | no bloc-naming layer at all; no per-pair friction, no preview warning |
| `30% - 32%` | pre-noticed (preview only) | no bloc label; proposal-preview `hegemony` warnings use private-tally wording only (*"courts are tallying allies privately"*) — per-pair friction begins one band before continental consensus per RCS §7.8.1 |
| `33 - 49%` | `noticed` band | descriptive phrase only (*"French-led alignment"*); no sticky proper noun |
| `50 - 59%` | `alarming` band | authored proper bloc name unlocks across eligible surfaces |
| `60%+` | `crisis` band | same proper name persists; crisis copy intensifies (no renaming) |

The `30-32%` pre-noticed band is the private-tally prelude to the `33%` public reveal — erasing it collapses the arc from "courts are counting" to "Europe names the thing" and saps the `50%` reveal of its snap. Preview warnings in this band must remain **label-free**; descriptive phrases and proper nouns both wait until `_hegemony_signal_band(share) >= 1`.

`_hegemony_signal_band` in `coalition.py` is the authoritative **current-share** source for this band; `describe_hegemon_bloc` reads it. Beat/advisory dedupe does **not** read from this helper blindly — that logic is owned by the stored public-memory pair in `RELIABILITY_COMMITMENTS_SPEC.md` §7.3 / `RELIABILITY_IMPLEMENTATION_PLAN.md` B-Hegemony. Band gates always read the raw share float; player-facing share display on bloc-naming surfaces floors to the whole percent so rendered numerals never outrun the label contract.

#### 8.1a.3 Naming taxonomy (deterministic, authored)

LLM prose may not invent bloc names. Name selection is deterministic from the hegemon, not from a variable member list.

| Hegemon | Proper bloc name (`50%+`) | Descriptive phrase (`33-49%`) | Adjective stem |
|---|---|---|---|
| France | `French System` | `French-led alignment` | `French` |
| Britain | `British Interest` | `British-led alignment` | `British` |
| Austria | `Vienna System` | `Austrian-led alignment` | `Austrian` |
| Prussia | `Berlin Alignment` | `Prussian-led alignment` | `Prussian` |
| Saxony | `Saxon Circle` | `Saxon-led alignment` | `Saxon` |
| Russia | `Russian Alignment` | `Russian-led alignment` | `Russian` |
| Spain | `Spanish Alignment` | `Spanish-led alignment` | `Spanish` |
| Ottoman Empire | `Ottoman Alignment` | `Ottoman-led alignment` | `Ottoman` |
| Sweden | `Swedish Alignment` | `Swedish-led alignment` | `Swedish` |
| Fallback / future nation | `{Adjective} Alignment` if adjective is authored, else `{Nation} Alignment` | `{Nation}-led alignment` | explicit authored adjective if available, else nation name |

Rules:

- One hegemon → one authored proper label. No ideology names, congress names, or continent-spanning "orders" yet.
- Labels are derived from the hegemon, not from a variable member list. No member-list-generated names like *"Franco-Bavarian League"* in v0.1.
- The fallback row holds at 5 nations, 13 nations, and 20-nation scenarios alike; member-list compound names do not land until a later Europe-scale pass proves they are needed.

#### 8.1a.4 Surface contract (required owners in v2.4.3)

Bloc naming rides existing surfaces only. No new UI family in this phase.

- **Balance of Europe headline** (Nations tab of Diplomatic Ledger): first-class owner of the bloc label.
- **`balance_of_europe_shifted` threshold beats** at `33 / 50 / 60`: `33%` beat uses descriptive language only; `50%` beat is the proper-noun reveal; `60%` beat reuses the proper name and makes camps feel hardened.
- **Downward `60 -> 59` / `50 -> 49` acknowledgments** are advisory-only in Talleyrand's voice, not a second rail family. The label regression must still be named, but quietly. These advisories fire only on the first downward crossing out of a surfaced band in the current equilibrium epoch; they do not repeat on every edge oscillation. They land as a one-line same-turn dispatch aside, not as a rail notice, popup, or headline. They use the current-share label after the drop, so `50 -> 49` speaks of the descriptive alignment, while `60 -> 59` keeps the proper noun and relaxes only the frame.
- **Proposal-preview `hegemony` warnings** (Political Context preview): once unlocked at `50%+`, warnings reference the proper bloc name so treaty friction reads politically.
- **Coalition declaration contrast copy**: if the formal coalition forms, the declaration copy contrasts the coalition against the named hegemon bloc (e.g. *"Britain's coalition marches against the French System"*). This is the **peak dramatic moment** of the bloc-naming contract — louder than the Case 4 ledger line, which is steady-state presence. Author the declaration copy with at least the same voice budget as `breach_lead_*` lines (named diplomat, single committed sentence, no hedging); do not let the ledger echo and the declaration popup read at equal weight. COALITION_SPEC §3e / §3f / §9d must embed this contrast line — a bare *"THE COALITION OF BRITAIN"* popup without the *"against the French System"* counterbeat loses the reveal payoff at the moment the whole mechanic is cashing in.
- **Same-band hegemon swap is a fresh beat, not a silent handoff.** If the hegemon identity changes while share stays in the same surfaced band (for example France `52%` → Russia `52%` after a treaty / vassal transfer), a fresh `balance_of_europe_shifted` beat MUST fire for the new arrangement per `RELIABILITY_COMMITMENTS_SPEC.md` §7.3. The headline must never become the first clue just because the band number stayed the same.

v0.1 forward-compat note: the bloc-label owner surfaces above may still name a non-player hegemon descriptively if the bloc geometry produces one, even though passive scalar accrual remains player-targeted until D2 Coalition Generalization. This does **not** authorize Balance-of-Europe coalition-pressure sub-lines to retarget away from `world.player_nation`; those stay suppressed when `hegemon != world.player_nation` per `RELIABILITY_COMMITMENTS_SPEC.md` §11.1. **The same guard applies to the declaration contrast copy**: when `coalition.target == world.player_nation` (per RCS §7.4) but `hegemon != world.player_nation`, the declaration copy targets the coalition target — bare `world.player_nation`, no bloc contrast — not the named hegemon bloc. Rendering *"Britain's coalition marches against the Russian Alignment"* while the scalar and coalition target are actually anti-France would publish the same visible lie the ledger sub-line suppression prevents. Bloc-contrast form returns with D2 Coalition Generalization.

Per-row / badge scope after D3:

- **Nation badges / ledger-row bloc stamps are live** as the D3 follow-up. The original v2.4.3 naming layer still concentrates the dramatic reveal on the four surfaces above; row stamps are subordinate steady-state tags.
- Live stamp contract: proper noun at `50%+`, descriptive phrase at `33-49%`, no hegemon-bloc stamp below `33%`, deterministic single-owner priority `[Coalition Member] > [{Proper Bloc Name}] > [{Descriptive} bloc] > [Vassal of {Overlord}] > [Neutral]`, with `[Coalition Member]` dominating hegemon-bloc labels during declared-coalition turns so hegemon blocs do not blur into the formal anti-hegemon coalition.
- Retroactive renaming of old campaign-log rows remains out of scope. This contract is about live legibility, not archive polish.

#### 8.1a.5 Worked-copy examples (tone reference, not committed prose)

- `33-49%` (noticed): *"France leads a widening French-led alignment (37%)."*
- `50-59%` (alarming, reveal): *"The French System commands 52% of Continental power."*
- `60%+` (crisis, brewing war): *"The French System commands 61%; hostile courts are hardening into camp against it."*
- `70%+` (crisis intensified, no new beat): *"The French System now approaches a continental completeness; hostile courts speak as if the map is already being redrafted around it."*
- `DECLARED` (coalition contrast): *"Britain's coalition marches against the French System."*

The `70%+` line is a Case-2 / Case-4 headline intensifier, not a fourth beat family. It reuses the existing proper noun and crisis register rather than introducing a new reveal.

Final committed prose lives in `commitments_notice_balance_of_europe_shifted` templates plus the Balance-of-Europe headline composition in `diplomatic_ledger.gd`. Register per foreign court is defined in `DIPLOMAT_VOICE_BIBLE.md` §Minimum cast coverage (the `hegemony_beat_*_{noticed,alarming,crisis}` family).
No separate `balance_of_europe_relaxed` rail family is introduced in this phase; downward relaxations reuse Talleyrand's existing bloc-naming register as a quiet advisory aside.

**Voice constraints (load-bearing — see Voice Bible before authoring):**

- **Talleyrand on French-bloc naming:** *dry acknowledgment, never pride.* Talleyrand may name the French System as an instrument of policy, but he must not narrate it as a boast — see `DIPLOMAT_VOICE_BIBLE.md` §Bloc-naming voice contract for the exact register. This guardrail is load-bearing: a single Talleyrand line that reads as triumphalism re-frames the entire mechanic as French-glory rather than European-balance.
- **Forbidden jargon:** the Voice Bible's no-modern-strategy-game list (`meta`, `sphere control`, `stack`, `synergy`, `faction lock`, `alignment graph`, `coalition math`, naked percentage-speak as the entire sentence) applies to every bloc-naming template authored against this contract. See `DIPLOMAT_VOICE_BIBLE.md` §Bloc-naming voice contract for the full list.

#### 8.1a.6 Implementation constraint

- One derived helper in `backend/game_logic/coalition.py`: `describe_hegemon_bloc(world, hegemon, share) -> {bloc_label, descriptive_label, adjective, is_proper_bloc_name}`.
- Callers must gate on `share >= 0.33`. Below that threshold the helper return is unspecified; surfaces should not call it.
- **`bloc_label` presence contract (normative).** `bloc_label` is non-empty (a `str` from the authored taxonomy) only when `is_proper_bloc_name == True`, which requires `share >= 0.50`. At `0.33 <= share < 0.50` the helper MUST return `bloc_label = None` and `is_proper_bloc_name = False`; `descriptive_label` is always populated whenever the helper is called. Consumers rendering headline or warning copy at the noticed band must fall through `bloc_label` (None) to `descriptive_label` — bare hegemon name is a last-resort fallback for unauthored / unknown hegemons only. This pins the `{bloc_label or descriptive_label or hegemon}` fallback chain used by `RELIABILITY_COMMITMENTS_SPEC.md` §11.1 Case 3 / Case 4 and the proposal-preview warning copy in §11.2.
- `adjective` follows the same `33%` gate as `descriptive_label` — populated whenever the helper is called, stable across band transitions (France stays `French` at both `41%` and `55%`). `is_proper_bloc_name` is the sole flag callers should branch on.
- No serialized `bloc_names`, `bloc_identity`, or `alignment_store` field.
- No new membership mechanic; membership still derives from existing bloc helpers / treaty state per `RELIABILITY_IMPLEMENTATION_PLAN.md` B-Hegemony.

#### 8.1a.7 Playtest feel gates

Bloc naming lands only if it clears all four:

- The player can answer at a glance **what camp is forming** and **who it is forming around**.
- The `50%` beat feels like a reveal, not a redundant restatement of what the player already inferred.
- Players do **not** confuse the named bloc with a declared war coalition.
- The naming layer increases drama without making the map feel over-labeled or gamey.

**Fail condition:** if playtest still shows repeated "bloc vs. coalition" confusion, re-open proposal-warning wording and coalition-declaration contrast copy (the loudest surface carrying both terms in the same sentence) before broadening the stamp layer. D3 row stamps are live, but they should stay subordinate rather than become the primary dramatic owner.

**Bargain events routed to WB-D:**

`bargain_ratified`, `bargain_triggered`, `bargain_fulfilled`, `bargain_breached`, `bargain_voided`, `hard_block_surfaced` (ally-entry), `ally_refused_free_join`, `declaration_backed_out`, counter-bargain Accept/Reject/Back Out flows. None of these are addressed here — they ship with the bargain mechanic in `WAR_BARGAIN_SPEC.md` slice WB-D.

### 8.2 Spotlight threshold rules — CUT in v0.5

Not applicable. Spotlight tier infrastructure was cut (§7.2). Events that v0.3 routed to "dispatch spotlight" — `hard_reject_posture_triggered`, `diplomatic_treaty_broken` (french_breach) — route to CRITICAL-priority notices in §9.2's priority-tier table, same visual surface as other CRITICAL events. Named-diplomat copy carries the weight.

### 8.3 One-turn emphasis rule — CUT in v0.5

No spotlight-slot budget to enforce. Commitments notices consume rail-wide budget per `INFORMATIONAL_UI_PLAN.md`; priority ordering (paradox > hard_reject > breach) is preserved via the `notifications.py` priority tier assignment, not a separate spotlight-slot counter.

### 8.4 No duplicate-surface rule

If an event already occupied a blocking surface this turn:

- do not also raise it as a separate persistent notice
- do not spawn a redundant dispatch line repeating the same information

Instead:

- fold the aftermath into the blocking result text
- write the durable record to ledger / campaign log

---

## 9. Surface Contracts

### 9.1 Notice card contract (spotlight tier cut — see §7.2)

v0.5.1 collapses the v0.3/v0.4 spotlight card contract and split-voice render into the existing CRITICAL-priority notice surface. Live events use a single-voice notice card with named-diplomat attribution — no new tier, no typographic split, no reveal cadence.

**Notice card contract (applies to both CRITICAL and NORMAL commitments events):**

- short player-facing period headline (see §9.2 icon/label contract)
- 1-2 lines of committed prose (down from v0.3 2-4; single-voice constrains body length)
- 1 compact consequence line naming the main political effect
- one obvious review action (`Open Ledger` or `Review Treaties`)
- named-diplomat attribution as body-inline attribution text (e.g. *"— Hardenberg, at court"* rendered at the end of the quote block), NOT as a separate `attributed_lines[]` structure

**`diplomatic_treaty_broken` (french_breach):** single-voice CRITICAL notice. The injured-party named diplomat's accusation is the body; Talleyrand's private aside is **not rendered inline** in v0.5.1 (aside concept moved to the N+1 aftermath CUT, §9.4). If playtest shows the notice reads flat without the aside, re-open §9.4 first.

**`hard_reject_posture_triggered`:** single-voice CRITICAL notice, `speaker="foreign_office"` resolved per §10.3 to "The Chancery of {nation}."

**Split-voice render infrastructure (`attributed_lines[]`, typographic contract, reveal cadence) — CUT in v0.5.** Prior v0.3/v0.4 content that specified the `lead` / `witness` / `aside` typography, 400-600ms stagger, and multi-region card layout was removed in v0.5.1. Single-voice with named-diplomat attribution suffices at 5-nation scale; the infrastructure is a deferred item for bargain-era expansion (WB-D).

### 9.2 Persistent notice card

Each commitments notice should show:

- event headline (using period vocabulary)
- main nation affected
- one-line consequence summary
- optional review action

Notice cards should be concise enough that three of them do not feel like a second dispatch.

#### Icon and label contract

`notification_bar.gd` `TYPE_ICONS`, player-facing labels, and review-action captions derive from the §8.1 routing join-table. Reuse those strings directly rather than restating a second copy here.

Bargain icons (`Word Kept`, `Articles Agreed`, `The Pledge Comes Due`, etc.) are deferred to WB-D.

#### Priority tier contract

Each commitments event maps to a `backend/notifications.py` priority tier. CRITICAL retained, NORMAL trimmed first under cap.

| Event type | Priority tier |
|-----------|---------------|
| all `CRITICAL` / `NORMAL` commitments events | derive from §8.1 join-table |

Commitments events use `CRITICAL` or `NORMAL` only. `HIGH` tier (used elsewhere for events like `MARSHAL_DEFIED_ORDER`) is intentionally not used in this pass.

### 9.3 Ledger emphasis

This pass should add emphasis, not a new ledger family.

Recommended emphasis rules:

- breached treaties (where France is at fault) get a recent-breach badge for a short window
- nations in hard-reject posture display a clear closed-door marker
- the latest commitments event should be easy to spot in the related ledger section

**Badge data source:** recent-breach badges derive from `backend/campaign_log.py` entries where `turn >= current_turn - 3` and `event_type == "diplomatic_treaty_broken"` with `end_reason_family == "french_breach"`. The closed-door marker reads from `has_hard_reject_posture(world, France, nation)` — not from log scanning.

**Review target routing:** the `review_target: "ledger_commitments"` action routes to the existing **Treaties** tab of the Diplomatic Ledger with a memory-and-pressure section filter applied. A dedicated commitments sub-tab is **out of scope** for v0.5.1.

(Recent-success / fulfillment badges deferred to WB-D — they need bargain fulfillment events that don't fire yet.)

### 9.4 Aftermath: minimum viable callback architecture (mostly CUT in v0.5)

`episode_id` remains the dedupe key for all commitments events (required for anti-spam §13). v0.5 retains exactly **one** aftermath beat from the v0.3 callback architecture:

- **`commitment_paradox` — required after-choice aside.** Rendered inside the paradox popup after the player chooses which promise to honor. Uses `speaker="envoy"` resolved to the spurned nation's named diplomat per §10.3. See §12.3 for the canonical 3-beat scene.

**All other aftermath paths — CUT in v0.5:**

- ❌ N+1 Talleyrand aside on `diplomatic_treaty_broken` (french_breach)
- ❌ N+1 Talleyrand aside on `hard_reject_posture_triggered`
- ❌ N+1 dispatch callback on `commitment_paradox_resolved`
- ❌ Aftermath metadata payload keyed on `episode_id` for future callback lookups
- ❌ Escalation rule (callback must add new content, not restate)
- ❌ N+5 fallback grievance slot
- ❌ Later-callback arbitration + competing-callback priority

Rationale: three live events and single-voice cards do not justify a persistent callback architecture. The paradox's post-choice aside is rendered inline in the popup, not through a deferred-callback system. If playtest shows the breach or hard-reject notices land too flat without an N+1 beat, re-open the breach aftermath first (it's the sharpest negative moment).

### 9.5 Campaign log

Campaign log entries remain compact.

This pass may improve:

- wording quality
- event naming consistency
- metadata-driven summaries

It should **not** turn the campaign log into a second dispatch essay surface.

Eight new campaign-log event types from v0.2 are now narrowed to the **three live ones**:

- `commitment_paradox_resolved` (already shipped)
- `hard_reject_posture_triggered` (already shipped)
- `diplomatic_treaty_broken` with `end_reason_family` field (already shipped)

The five bargain types (`bargain_ratified`, `bargain_triggered`, `bargain_fulfilled`, `bargain_breached`, `bargain_voided`) and `declaration_backed_out` are deferred to WB-D.

---

## 10. Voice Contract

### 10.1 Template-first

Mock mode must remain fully authoritative.

Every commitments event that receives blocking-popup or notice treatment has:

- a deterministic headline template
- a deterministic body template
- slot values pulled from structured payloads

For v0.5.1 (mandatory committed templates):

- `commitment_paradox` framing, blocking body, after-choice aside
- `hard_reject_posture_triggered` (with named-diplomat resolution)
- `diplomatic_treaty_broken` (french_breach) lead + aside

The worked examples in §12 are not decorative. They are the acceptance fixtures for tone, slot usage, and surface length.

### 10.2 LLM mode

LLM mode may vary prose only.

It may: enrich tone, vary wording, sharpen diplomatic flavor.

It may **not**: invent new facts, imply uncomputed motives, contradict the structured payload.

### 10.3 Speaker rules

Talleyrand is **not** the default speaker for every important commitments moment.

| Event | Lead speaker | Supporting speaker | Register |
|-----------|---------|---------------|---------------|
| `commitment_paradox` | `talleyrand` | spurned-envoy aside after choice (named diplomat) | grave, tragic, explicitly not quippy |
| `commitment_paradox_resolved` | `talleyrand` (notice), `system` (campaign log) | none | Talleyrand reflective on notice surfaces; neutral declarative in campaign log. `system` is disallowed on rail surfaces per §10.3 — the resolution of a paradox should carry Talleyrand's voice, not feel like a system message. |
| `diplomatic_treaty_broken` (french_breach) | `envoy` (named diplomat per §10.3) | none | accusation first; no inline Talleyrand aside in v0.5.1 |
| `hard_reject_posture_triggered` | `foreign_office` (resolved as "The Chancery of {nation}") | none | formal closure, no quips |
| `witness_strike_recorded` | `system` or `foreign_office` | none | terse third-party observation |
| campaign log | `system` | none | neutral declarative summary |

**Render contract:** single-voice notice/detail surfaces use `speaker_attribution` (valid values: `system`, `talleyrand`, `envoy`, `foreign_office`) as a field separate from body text. v0.5.1 does not ship split-voice `attributed_lines[]` on live surfaces.

**Named-diplomat resolution (mandatory for envoy / foreign_office).** Abstract speaker roles are routing hints, not render values. At render time:

- `speaker="envoy"` MUST resolve to the named diplomat of the nation in context (Hardenberg, Metternich, Einsiedel, Castlereagh — the v0.1 cast from `diplomat.py`) and render with that diplomat's personality register per `DIPLOMAT_VOICE_BIBLE.md`.
- If a cast-nation `speaker="envoy"` path cannot resolve a supported register, raise `ValueError(f"loyalist register unsupported: {nation}/{personality}")` rather than silently falling back to `system`.
- `speaker="foreign_office"` MUST render as `The Chancery of {nation}` — never as the generic string `foreign_office`. Register derives from that nation's dominant diplomat's personality.
- `speaker="system"` is reserved for campaign-log summaries ONLY. On any rail or notice surface, `system` is disallowed — route to `foreign_office` or a named observer instead. The word `system` must never reach the player. **Render-time guard (mandatory):** the rail/notice render path MUST raise `ValueError(f"system speaker disallowed on rail surface: {event_type}")` when `speaker == "system"` reaches it. Documentation is not enforcement; without the guard, one missed `else:` in a template author's branch leaks the modern-jargon failure mode the Voice Bible exists to prevent.
- v0.1 scope assumes the 5-nation roster (France, Britain, Austria, Prussia, Saxony). If a future event targets a non-cast nation, render falls back to `foreign_office` -> `The Chancery of {nation}` with no personality register until the cast expands. The fail-loud `ValueError` fires only for the cast-nation `speaker="envoy"` path; it does not fire on this non-cast fallback.

**Minimum live cast coverage.** `DIPLOMAT_VOICE_BIBLE.md` §Minimum cast coverage is authoritative for v0.5.1. The old v0.3 four-line minimum is retired. Live coverage now includes:

- breach / hard-reject lead lines for the named foreign cast
- `balance_of_europe_shifted` warning families for Castlereagh, Hardenberg, Metternich, and Einsiedel (`noticed` / `alarming` / `crisis`)
- `amends_offered` acknowledgment lines for the same four foreign courts

### 10.4 Witness scope as dramatic input

`scope_reason` is not ledger garnish. It is the narrative selector for witness reactions.

- `ally` witnesses sound disappointed, wary, or reconsidering.
- `rival` witnesses sound pleased, amused, or opportunistic.
- `shared_enemy` witnesses sound calculating; they smell a strategic opening.
- `region_observer` witnesses sound gossipy or reputational; the story is spreading. (Inactive in v0.3 — region_observer scope only fires when bargains exist.)

**Current application:** full scope-branched witness reaction copy with **named-diplomat registers** is deferred to WB-D (where bargain breaches justify that depth of cast work). For v0.5.1 this phase ships **one skeletal canonical line per scope** so witness payloads do not all render identically on the rail:

| Scope | Skeletal canonical line (mock mode, v0.5.1 required) |
|---|---|
| `ally` | *"The court of {witness_nation} received the news in silence, and that silence is the register to note."* |
| `rival` | *"{witness_nation} has noted the news with the practiced calm of a court that has long been expecting it."* |
| `shared_enemy` | *"{witness_nation} has taken note; they understand France's hand was elsewhere this week, and they have drawn their own strategic reading."* |
| `region_observer` | *(inactive in v0.5.1 — no line authored until WB-D reactivates the scope)* |

These lines are **deliberately unvoiced** — no named diplomat, no personality register. They are the minimum visible difference between scopes. WB-D replaces each row with the full per-nation Hawk/Schemer/Dove voiced variant sourced from the Voice Bible cast. The skeletal v0.5.1 lines prevent the flatness failure ("every witness strike reads the same on the rail") without committing the full register work that belongs with the bargain era.

### 10.5 Refusal and hard-block explanations

If the engine provides:

- structured `warnings[]` (per `RELIABILITY_COMMITMENTS_SPEC.md` §11.2)

then the presentation layer should use it. Explanation is composed from `warnings[]` sorted by severity, with the first entry used as the lead line. There is no engine-side "strongest negative factor" or `top_reason_text` synthesizer.

If the engine does **not** provide enough structured explanation, prefer a short, honest explanation; do not let the voice layer invent causal detail.

---

## 11. Payload Contract

Do **not** create a second long-lived commitments presentation store.

This pass builds on:

- existing dispatch metadata
- campaign-log metadata
- response payloads already produced by commitments systems

Where one normalized surface payload is needed, use a transient structure:

```python
commitment_surface_event = {
    "event_type": "diplomatic_treaty_broken",
    "episode_id": "ep_1805_breach_001",
    "severity": "high",
    "primary_surface": "critical_notice",
    "primary_nation": "Prussia",
    "secondary_nation": "France",
    "injured_party": "Prussia",
    "source_treaty_type": "alliance",
    "end_reason_family": "french_breach",
    "end_reason_action": "war_declaration",
    "fault_nation": "France",
    "speaker_attribution": "envoy",
    "notice_priority": "CRITICAL",
    "dominant_witness_scope": "ally",  # passed through but not branched on in v0.3
    "follow_up_actions": ["talk_talleyrand", "open_ledger"],
    "relation_delta": -10,
    "reliability_delta": -10,
    "applied_reliability_delta": -10,
    "intended_reliability_delta": -10,
    "witness_nations": [
        {"nation": "Austria", "scope_reason": "ally"},
    ],
    "review_target": "ledger_commitments",
}
```

Balance of Europe payload block (used by the Nations-tab headline in C-lite §14):

```python
balance_of_europe = {
    "hegemon": Optional[str],
    "share": float,  # 0.0-1.0
    "bloc_label": Optional[str],  # None at 33-49%; authored proper name at 50%+; see §8.1a.6 presence contract
    "descriptive_label": Optional[str],  # "{Adjective}-led alignment" when share >= 0.33; None otherwise
    "adjective": Optional[str],  # stable across bands once the helper is called (e.g. "French")
    "is_proper_bloc_name": bool,  # True iff share >= 0.50; sole branch flag for consumers
    "threat_level": int,  # 0-100; v0.1 anti-world.player_nation coalition scalar
    "coalition_state": Literal["NONE", "BREWING", "DECLARED", "COOLDOWN"],
    "qualifying_nations": List[str],  # nations currently meeting the coalition threshold
    "leader": Optional[str],  # coalition leader when DECLARED
    "cooldown_turns_remaining": Optional[int],  # populated iff coalition_state == "COOLDOWN"; turns left in the dissolution cooldown; None otherwise
    "residual_pressure_active": bool,  # True iff coalition_state == "COOLDOWN" AND threat_level >= THREAT_TENSION_MIN (COALITION_SPEC §3a, currently 30) AND the cooldown turn received positive threat this turn. Both conditions required — threat_level alone would fire the line on every quiet cooldown turn that happens to sit above Tension while decaying, which RELIABILITY_COMMITMENTS_SPEC §11.1 Case 5 explicitly forbids ("the line must not loop every quiet turn once Europe has stopped actively counting"). `build_diplomatic_ledger()` computes the "positive threat this turn" predicate from `world.positive_threat_delta_this_turn` and ANDs it into this flag; the delta is not exposed as a separate payload field, so renderers branch on the single boolean only.
}
```

Populated by `build_diplomatic_ledger()` from B-Hegemony engine output and rendered by the Nations-tab headline per `RELIABILITY_COMMITMENTS_SPEC.md` §11.1, including the COOLDOWN state case. `cooldown_turns_remaining` and `residual_pressure_active` are the two fields that drive Case 5 rendering — the cooldown line reads `cooldown_turns_remaining`, and the residual-flavor line conditions on `residual_pressure_active`. `residual_pressure_active` bakes in BOTH the `threat_level >= THREAT_TENSION_MIN` threshold AND the `world.positive_threat_delta_this_turn` anti-spam gate from §11.1 Case 5 so the renderer branches on a single flag and quiet cooldown turns with legacy decaying threat do not loop the residual line. When `hegemon != world.player_nation` in v0.1, the renderer MUST suppress the coalition-pressure sub-line entirely per §11.1 — do not retarget it to France. The `threat_level` scalar still populates for the player-nation case; the foreign-hegemon case simply renders no pressure sub-line until D2 Coalition Generalization makes the scalar per-target.

**Dual-`cooldown_turns_remaining` synchronization rule (normative).** The ledger-state `balance_of_europe.cooldown_turns_remaining` (L612) and the beat-transient `balance_of_europe_shifted.cooldown_turns_remaining` (L651 below) MUST hold the same value whenever both are populated on the same turn. `build_diplomatic_ledger()` is the single owner of the cooldown snapshot each turn; beat payloads emitted at ratification seams read from that snapshot (or from `world.coalition_cooldown` directly when the ledger has not yet been requested this turn), not from a separately derived value. The ledger-state field drives Case 5 headline rendering every COOLDOWN turn; the beat-transient field drives only the `60%` crisis-beat copy when that beat fires during cooldown. `world.coalition_cooldown` decrements in `process_coalition_turn` at end-of-turn, so mid-turn beats and end-of-turn ledger always agree within a single turn by construction.

Per-row bloc-stamp payload (`nations[*].bloc_stamp`) is live as the D3 follow-up. Each Nations row may carry a transient display-only dict `{label, kind, priority}`. It is never serialized and is derived by `build_diplomatic_ledger()` from live Balance/coalition/vassal state. Renderers may branch on this populated field; if it is absent or null, they should simply omit the tag.

`balance_of_europe_shifted` transient event payload (single owner across rail notice, dispatch/log echo, and any preview reuse of the same beat):

```python
balance_of_europe_shifted = {
    "band": Literal[1, 2, 3],  # 1 = noticed (33%), 2 = alarming reveal (50%), 3 = crisis (60%)
    "hegemon": str,
    "share": float,  # post-change share, 0.0-1.0
    "speaker_nation": Optional[str],  # selected foreign court whose named diplomat would speak if authored; None only on the Talleyrand-only fallback when no non-bloc major exists
    "bloc_label": Optional[str],  # None when band == 1; authored proper name at 50%+
    "descriptive_label": str,  # always populated once the helper is called
    "adjective": Optional[str],
    "is_proper_bloc_name": bool,
    "counterplay_hint": Optional[str],  # REQUIRED on upward beats when hegemon == world.player_nation; omitted only on non-player-hegemon descriptive variants
    "cooldown_turns_remaining": Optional[int],  # present only for the 60% crisis beat during coalition cooldown. NOTE: this is the beat-transient field. The ledger-state `balance_of_europe` payload above (L612) carries a separate, identically named field that populates whenever `coalition_state == "COOLDOWN"` regardless of whether a beat fires. The two fields are deliberately distinct: the ledger-state version drives Case 5 headline rendering every turn; the beat-transient version drives only the 60% crisis beat copy. Do not conflate.
}
```

Multi-band same-turn jumps still populate this payload from the **highest** newly reached band only; do not emit stacked `33%` + `50%` copies on one seam. Consumers reuse this schema as-is rather than inventing an ad-hoc second payload for one surface.

Required rules:

- all fields primitive-only
- no live object references
- no duplicate authority over commitment state
- `episode_id` is the episode-boundary key (see `RELIABILITY_COMMITMENTS_SPEC.md` §8.3); collapse and dedupe logic key off it
- `witness_nations` entries carry `scope_reason in {"ally", "rival", "shared_enemy", "region_observer"}` — `region_observer` inactive until WB-D
- `speaker_attribution` is optional shorthand for single-voice surfaces and must satisfy `speaker_attribution in {"talleyrand", "envoy", "foreign_office"}` (`system` reserved for campaign log only)
- `follow_up_actions` entries are UI routing hints only; they may reference only existing **no-cost** advisory or inspection surfaces in v0.5.1 (response routes deferred to WB-D)
- `relation_delta` / `reliability_delta` are sourced from breach metadata
- `review_target: "ledger_commitments"` routes to the Treaties tab of the Diplomatic Ledger with a commitments section filter
- `bloc_label` / `descriptive_label` / `adjective` / `is_proper_bloc_name` are transient display helpers derived from hegemon + share, never serialized state. `bloc_label` is `None` when `is_proper_bloc_name == False` (i.e. share < 50%) per §8.1a.6 presence contract; renderers must fall through to `descriptive_label` at the noticed band

If a field is not known deterministically, omit it rather than improvising it in presentation.

---

## 12. Example Player Experience

### 12.1 Treaty broken (French breach)

Engine outcome:

- France voluntarily breaks an alliance / DA / NA with Prussia (manual break, war declaration, paradox choice, or constructive breach via auto-decay)
- breach metadata applied; reliability and bilateral strike penalties applied per Memory and Pressure §8.3
- `dominant_witness_scope` computed (passed through to presentation but not branched on in v0.3)

Player experience:

- turn-N CRITICAL notice lands as a single-voice named-diplomat accusation
- ledger and log preserve the exact fallout

Canonical mock CRITICAL-notice templates (per Voice Bible registers):

- Headline: `Word Broken Before {injured_party}`

**Hardenberg (Prussia, Hawk) lead:**

> "Prussia was given France's word in clear terms. That word is now spent elsewhere. Tell your Emperor that Berlin does not ask twice. The army remembers the insult. So does the King."

**Metternich (Austria, Schemer) lead:**

> "Vienna has received word of the French disposition. Austria notes, with the customary patience of a court accustomed to the shifting weather of French commitments, that the article agreed between us has not been honored. There will be, naturally, no public reply. One simply adjusts."

**Einsiedel (Saxony, Dove) lead:**

> "Sire, His Majesty asked only that France's word be kept. We arranged Saxon affairs around it. We told our people that France had given assurance. It is not our place to accuse France, whose friendship Saxony values above all others. It is only that we had believed, and now we must explain to a small court that we were mistaken."

Desired feeling:

- "Europe noticed. The named court that I wronged has spoken in their own register."

(The deferred v0.3 private-aside and next-morning callback prose now live in `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` Appendix "v0.3 deferred prose". Scope-branched witness lines still defer to WB-D when bargain breach gives them more political weight.)

### 12.2 Hard-reject posture triggered

Engine outcome:

- a nation crosses 3 active bilateral strikes and will now hard-resist deep treaties
- `hard_reject_posture_triggered` emitted (first-time-per-pair contract enforces single emission)

Player experience:

- one featured CRITICAL notice tells the player that this channel is effectively closing
- the next relevant preview / refusal reinforces the state
- the ledger makes it obvious the posture is active

Canonical mock CRITICAL-notice template:

- Headline: `The Chancery Shut` (or `The Court of St. James Closes Its Doors` for Britain)
- Speaker: `foreign_office` resolved per §10.3
- Body:

  "The chancery of {primary_nation} no longer receives French dispatches on matters
  of alliance, guarantee, or common cause.
  Courtesies may continue. Trust will not."

For Britain (Castlereagh's voice):

  "The Court of St. James is not in receipt of further French dispatches on
  matters of alliance. His Majesty's Government will weigh French undertakings
  by the conduct, not the assurance, of the French chancery."

For Prussia (Hardenberg's voice):

  "Berlin will not entertain further French overtures. Prussia has Prussia's
  own memory of what French signatures have been worth, and Prussia keeps her
  own counsel from this day forward."

- Consequence line: `{primary_nation} will hard-refuse deep treaty asks until posture cools.`

Desired feeling:

- "That nation is not just numerically colder. They are diplomatically shut."

### 12.3 Commitment paradox (3-beat staged)

Engine outcome:

- ratification or war declaration would force the player into both sides of an existing alliance (legacy alliance-cross-war trigger; type renamed to `commitment_paradox` in B3)
- the existing blocking hard-stop pauses resolution until the player chooses which promise survives

Player experience:

- Talleyrand frames the contradiction in grave register
- the blocking body lays out the binary choice
- the player chooses
- the spurned nation's named envoy responds first; then Talleyrand's closing aside

Canonical staged template (3 beats: framing → blocking body → after-choice aside):

**Beat 1 — Talleyrand framing** (grave, explicitly not quippy):

  "Sire, we have arranged our promises so artfully that Europe now insists on
  arithmetic. If we honor {primary_nation}, we break faith with
  {secondary_nation}. There is no language in which both vows remain true."

**Blocking body text (canonical, renders in the popup between framing and choice):**

  "One pledge must now be withdrawn.
  To honor {primary_nation} is to betray {secondary_nation}.
  To honor {secondary_nation} is to betray {primary_nation}.
  France may choose which wound it opens. It may not call both injuries honor."

**Beat 2 — Spurned envoy aside (after choice — register from spurned nation's named diplomat):**

  *Hawk (Hardenberg, Castlereagh):* "{spurned_diplomat} has left court without taking leave."
  *Schemer (Metternich):* "{spurned_diplomat} received the news with a small, exact smile."
  *Dove (Einsiedel):* "{spurned_diplomat} asked only whether France had understood what was being withdrawn."

**Beat 3 — Talleyrand closing aside (after choice):**

  "We have preserved one promise by choosing which wound to open. Europe
  forgives necessity sooner than contradiction, but it will call this necessity
  ours."

Desired feeling:

- "I had to choose which to betray, and the spurned court spoke before Talleyrand named what I'd done."

**Implementation contract:**

- `commitment_paradox` is registered as HARD_STOP (already done in `dialogue_manager.py`); B3 activates it on the push side
- requires dedicated `commitment_paradox_popup.{tscn,gd}` surface (one of the four Slice C Godot prerequisites in §14)
- the legacy `alliance_paradox_popup.gd` scene is single-label and **cannot host** the three-beat scene; it must be replaced by `commitment_paradox_popup.{tscn,gd}`

(The five-beat scene from v0.2 — envoys from BOTH spurned nations speaking before Talleyrand frames — is **deferred to WB-D** when rivalry-driven multi-conflict ratification fires the paradox from new triggers.)

### 12.4 Reactive affordances (advisory routes only in v0.5.1)

Commitments surfaces may not leave the player as a reader only. v0.5.1 keeps **advisory routes** (no cost, inspect / discuss). Response routes (`Propose redress`, `Deepen the bond`, `Attempt to reopen the chancery`, `Denounce the refusal`) are **deferred to WB-D** because they depend on bargain-era proposal templates and `proposal_options` seed defaults that don't exist yet.

**Advisory routes (v0.5.1 — no cost, inspect / discuss):**

| Action | Availability | Route | Mechanical effect |
|-----------|---------|---------------|---------------|
| `Speak to Talleyrand about this` | all CRITICAL commitments notices except `balance_of_europe_shifted` + paradox aftermath | opens scoped `advisory` dialogue with `context.origin_episode_id = episode_id` | none |
| `Summon {named_envoy}` | french-breach CRITICAL notice only | reuses advisory shell; opener is one-exchange foreign-court response in the named envoy's register, seeded by `episode_id`, then hands back to Talleyrand | none |
| `Review the broken treaty` | french-breach notice + paradox resolution | routes to filtered Treaties tab | none |

Rules:

- advisory routes remain no-cost, no state change, no notice on dismiss
- every CRITICAL commitments notice family must expose at least one advisory route so the player can engage in-fiction within one click, **except** `balance_of_europe_shifted`, which is intentionally `Open Ledger` only in v2.4.3
- on the breach notice, both `Speak to Talleyrand` and `Summon {named_envoy}` may appear together; the named-envoy summon takes primary visual emphasis
- the paradox itself remains a strict binary — the player MUST choose. v0.5.1 has no `Offer redress to {spurned_nation}` next-turn affordance (that depended on bargain templates).

---

## 13. Anti-Spam Rules

- No more than 2 above-the-fold commitments notices per turn.
- Blocking hard-stops suppress duplicate notice-generation for the same root event.
- Multiple witness strikes from one root event collapse into one summarized presentation event when surfaced outside the ledger. Witness-collapse keys off `episode_id`, not event-type heuristics.
- If a commitments event is unrelated to the current blocking popup, queue it into the normal notice/dispatch path instead of interrupting the player mid-resolution.
- No more than 1 post-choice aside may fire per `commitment_paradox` `episode_id`; v0.5.1 ships no N+1 aftermath beats.
- Quick-action follow-ups do not generate their own notices if opened and dismissed without state change.

(Later-callback arbitration, N+5 fallback grievance slot, and competing-callback priority rules are deferred — v0.3 has no later callbacks to arbitrate.)

---

## 14. Implementation Slice

### C3-lite. The single slice

**Files:** `backend/game_logic/dispatch.py`, `backend/game_logic/diplomatic_templates.py`, `backend/game_logic/diplomatic_dialogue.py`, `backend/game_logic/diplomatic_ledger.py`, `backend/campaign_log.py`, `backend/notifications.py`, `backend/models/dialogue_manager.py`, `backend/main.py`, `godot-client/.../main.gd`, `godot-client/.../notification_bar.gd`, `godot-client/.../diplomatic_ledger.gd`, `godot-client/.../campaign_log.gd`, new `commitment_paradox_popup.{tscn,gd}`, notice/dispatch surfaces already used by diplomacy

**Prerequisite work (must land before render contracts work):**

1. **Dedicated `commitment_paradox_popup.{tscn,gd}` surface.** Existing `alliance_paradox_popup` is single-label; cannot host three-beat staged scene. Build new popup on a CanvasLayer in the 101-118 range per CLAUDE.md "Adding a new popup/dialog" pattern. Re-uses HARD_STOP machinery, does NOT share scene with `alliance_paradox_popup`.
2. **HARD_STOP type activation.** B3 (paradox rename) ships push-side alias; this slice ensures Godot dtype whitelist (~main.gd line 697) routes `commitment_paradox` to the new popup.
3. ~~**Split-voice render capability.**~~ **CUT in v0.5.** Single-voice notices with named-diplomat attribution replace the `lead` / `witness` / `aside` three-region card layout. `backend/notifications.py` payload requires only `speaker_attribution`, not `attributed_lines[]`.
4. ~~**Elevated rail tier.**~~ **CUT in v0.5.** Events route through existing CRITICAL/NORMAL priority tiers per §9.2. No elevated 2-turn-persisting card variant, no per-notice review/follow-up action buttons beyond what existing notices carry.

**Core tasks (v0.5.1 — trimmed to shipped scope):**

- Define commitments event routing rules across blocking / notice / ledger per §8.1 (no elevated rail tier)
- Add commitments-specific notice templates under the `commitments_notice_*` template family in `diplomatic_templates.py` (no separate elevated-tier template family beyond `commitments_notice_*`)
- Add DG-4 notice-template stubs explicitly: `commitments_notice_call_refused_offensive`, `commitments_notice_call_refused_defensive`, and `commitments_notice_call_honored_costly`
- Commit canonical mock prose for `diplomatic_treaty_broken` (french_breach), `hard_reject_posture_triggered`, and `commitment_paradox` (framing, blocking body, after-choice aside)
- Add player-facing period labels per §9.2
- Resolve `speaker="envoy"` and `speaker="foreign_office"` to named diplomats per §10.3 — single helper in backend that reads `world.diplomats[nation]` and returns `{name, register}`
- Commit the Voice Bible minimum live coverage required by §10.3
- Stage `commitment_paradox` as 3-beat scene per §12.3 (Talleyrand framing → blocking body → spurned-envoy + Talleyrand asides, all rendered in the popup — not split across surfaces)
- Add ledger emphasis rules for recent breach and active hard-reject posture (§9.3)
- Wire duplicate suppression so one event does not surface three times (§8.4)
- Keep campaign-log summaries compact but more specific
- Add advisory-route reactive affordances per §12.4 (`Speak to Talleyrand about this`, `Summon {named_envoy}`, `Review the broken treaty`)
- **CUT in v0.5:** ~~Turn `episode_id` into a minimal memory hook for one N+1 aftermath beat per §9.4~~ ~~Inject N+1 callback lines into the next Morning Dispatch without changing mechanics~~ — aftermath callback architecture deferred.

**Suggested tests (~10-12, v0.5.1 trimmed):**

- CRITICAL-priority ordering across multiple same-turn commitments events (paradox > hard_reject > breach via `notifications.py` priority tier, not a separate highlight-slot system)
- No duplicate notice after blocking paradox resolution
- Hard-reject posture gets one featured notice, not a repeated every-turn notice (first-cross emit contract)
- Witness-strike collapse into one medium surface event per `episode_id`
- Mock-mode template coverage for all three live commitments events
- Named-diplomat resolution: `envoy` → Hardenberg/Metternich/Einsiedel/Castlereagh per nation context, with correct register
- `foreign_office` → "The Chancery of {nation}"
- `system` speaker disallowed on rail surfaces
- `review_target` routing opens the intended ledger view and does not drift from the §8.1 join-table
- Paradox 3-beat staging: framing renders before choice, after-choice aside renders in the popup post-choice (all beats in the popup — no cross-surface dispatch callback)
- Advisory routes are no-cost: `Speak to Talleyrand` opens advisory dialogue with `context.origin_episode_id`; dismiss leaves no state change
- Balance of Europe headline composition for the full state machine per `RELIABILITY_COMMITMENTS_SPEC.md` §11.1 (the five base cases plus the legal `NO_HEGEMON + BREWING` composite)
- Same-turn `balance_of_europe_shifted` notice copy for the 33% / 50% / 60% threshold crossings, including deterministic named-diplomat / chancery fallback and counterplay-hint wiring. D3 later added Nations-tab row-stamp payload/render coverage using `nations[*].bloc_stamp`.
- `amends_offered` lightweight notice copy for both standard and grievance-variant repair gestures, led by the target court's named diplomat

**Estimated budget (v0.5.1 trimmed):**

- **one implementation session** (down from v0.3/v0.4 two sessions — elevated rail tier and split-voice infra cut reduces Godot scope):
  1. *Godot surfaces* — new `commitment_paradox_popup.{tscn,gd}` (3-beat staged scene per §12.3, on its own CanvasLayer in the 101-118 range, with the after-choice aside rendering in-popup post-choice), HARD_STOP dtype whitelist routing in `main.gd` for the renamed `commitment_paradox` type, named-diplomat attribution inline in existing notice cards (no new split-voice tier, no separate elevated-card variant).
  2. *Backend + mock prose* — named-diplomat resolution helper (`speaker="envoy"` / `speaker="foreign_office"` per §10.3), committed prose for the three live events using Voice Bible registers, `balance_of_europe_shifted` threshold-beat prose for 33% / 50% / 60%, `amends_offered` acknowledgment prose, ledger emphasis rules (§9.3), advisory-route reactive affordances (§12.4), Balance of Europe headline render in `diplomatic_ledger.gd`.
- approximately 10-12 tests total

---

## 15. Future Handoff

This pass should hand off cleanly to later systems:

- **`Bilateral Peace Hardening`**
  - owns its own showpiece peace-settlement events; the commitments router is commitments-specific and does not extend to peace fallout. Bilateral Peace Hardening may copy patterns, but it does not reuse the commitments router.
- **`WAR_BARGAIN_SPEC.md` slice WB-D (bargain presentation extension)**
  - extends this pass with `bargain_fulfilled` / `bargain_breached` / `bargain_voided` / `bargain_ratified` / `bargain_triggered` / `declaration_backed_out` headline events and notices
  - adds scope-branched witness reaction copy (uses `dominant_witness_scope` payload that this pass already passes through)
  - adds response routes (`Propose redress`, `Deepen the bond`, `Attempt to reopen the chancery`, `Denounce the refusal`)
  - adds N+5 fallback grievance slot
  - adds five-beat paradox staging when rivalry-driven ratification paradox fires the new triggers
- **`Talleyrand Desk + Explanation Layer`**
  - can absorb the same commitments payloads into richer advisory surfaces later, but it does **not** own inventing the first breach/paradox aftermath beats from scratch. C3-lite already commits the minimum callback architecture.
- **Generalized coalition work**
  - may later reuse the same emphasis principles for bloc pressure and split events.

This spec should **not** pre-own those future systems.

---

## 16. Acceptance Criteria

C3-lite is successful if:

- a player can tell the difference between routine diplomacy bookkeeping and a major commitments moment
- breach (where France is at fault) feels materially different in presentation weight from cascade
- hard-reject posture feels like a diplomatic state change, not just an invisible threshold
- witness fallout is legible without becoming spam
- when France breaks faith with Prussia, the player hears Hardenberg's accusation in Hardenberg's register, not "envoy"
- when Britain closes its chancery, the player hears Castlereagh's institutional finality, not Talleyrand's wit
- the paradox lands as a staged scene with grave Talleyrand framing, committed blocking body, and a spurned-court reaction after the choice
- `episode_id` dedupes repeated commitments fallout from one root event across blocking / notice / ledger surfaces
- `balance_of_europe_shifted` fires before the Balance-of-Europe headline can become the player's first clue on every new upward band crossing after play begins; inherited opening share uses the §7.3 bootstrap exception, and multi-band same-turn jumps emit only the highest newly reached beat
- **same-band hegemon swap** (e.g. France `52%` → Russia `52%`) emits a fresh `balance_of_europe_shifted` beat for the new arrangement and updates `world.hegemony_signal_hegemon`; the headline is never allowed to be the first clue just because the band number stayed the same
- the `33 / 50 / 60` naming contract holds across the headline, threshold beats, and proposal-preview warnings: **no bloc label at all below `33%`** (pre-noticed `30%-32%` preview warnings use private-tally wording only — "courts are tallying allies privately", no descriptive alignment phrase, no proper noun), descriptive phrase at `33-49%`, proper noun at `50%+`, same proper noun carried into `60%+` crisis framing
- `balance_of_europe_shifted` and the related Balance-of-Europe surfaces obey the strict fallback chain `named envoy -> Talleyrand advisory -> chancery`, with no anonymous `system` speaker on the notice family
- when a non-player hegemon appears in the v0.1 forward-compat edge case, bloc-label owner surfaces may still name them, but coalition-pressure sub-lines (both Case 3 brewing and Case 4 formal-coalition) remain suppressed rather than retargeted away from the player, and the coalition-declaration contrast copy targets the bare player nation — not the named hegemon bloc — to avoid a visible lie against the anti-`world.player_nation` scalar
- at least one no-cost conversational follow-up exists on every CRITICAL commitments notice family except `balance_of_europe_shifted`, which intentionally routes `Open Ledger` only in v2.4.3
- all of the above work identically in mock mode without LLM dependency
- no commitments presentation surface changes any underlying outcome

Bargain-era acceptance criteria (`bargain_breached` 3-beat sequence, scope-branched copy, response routes, etc.) move to `WAR_BARGAIN_SPEC.md` WB-D.

---

## 17. Changelog

- **April 20, 2026 — v0.5.2 Block 3 bloc-naming fold.** §8.1a expanded from a 12-line decision stub to the full normative bloc-naming contract (terminology guard, `33 / 50 / 60` activation gate, hegemon→label taxonomy with fallback, required surface owners, worked-copy examples, implementation constraint, playtest feel gates). Ship list in §v0.5.1 Scope Note now cites §8.1a as authoritative. `docs/audits/MP_V243_BLOCK3_BLOC_NAMING.md` is superseded by this fold plus the matching fold in `RELIABILITY_IMPLEMENTATION_PLAN.md` / `DIPLOMAT_VOICE_BIBLE.md`; the CF1-CF4 leftovers from that audit now sit in their parent slices (B-B4 / B-B7 / C-lite) rather than in an audit orphanage.
- **April 20, 2026 — v0.5.1 Non-normative bulk trim (v2.4.2 deep-audit C7).** v0.5 top-note disclaimed roughly half the file as non-normative but left the disclaimed sections intact. v0.5.1 trims the disclaimed content in place rather than requiring readers to mentally ignore it. Edits by section:
  - **§7.2 Dispatch spotlight** — collapsed to a short `CUT in v0.5` stub explaining that spotlight tier infrastructure (elevated card, 2-turn persist, `Spotlight Carryover` Morning Dispatch section) is not built; live events route through existing CRITICAL-priority notices.
  - **§8.2 Spotlight threshold rules** — collapsed to a short stub; priority ordering preserved via `notifications.py` priority tiers, not a spotlight-slot counter.
  - **§8.3 One-turn emphasis rule** — collapsed to a short stub; no spotlight-slot budget.
  - **§9.1 Notice card contract** — rewritten around single-voice notice with named-diplomat body-inline attribution. Removed split-voice `attributed_lines[]` typography table (bold/regular/italic, 110%/100%/90%, reveal cadence 400-600ms stagger). Prior content preserved in `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` for design history.
  - **§9.4 Aftermath architecture** — retained only the `commitment_paradox` in-popup after-choice aside. Removed N+1 Talleyrand aside on breach and hard-reject, `commitment_paradox_resolved` dispatch callback, aftermath metadata payload lookup, escalation rule, N+5 fallback slot, later-callback arbitration, competing-callback priority.
  - **§14 C3-lite slice** — Prerequisite-work items 3 (split-voice render) and 4 (spotlight tier) struck through. Core tasks list trimmed of spotlight-specific templates and N+1 callback wiring. Test count reduced from ~16-22 to ~10-12. Session count reduced from 2 to 1.
  - **Top-note** — cut-list moved above the content rather than documenting obsolete sections as "non-authoritative." Cold readers no longer have to mentally ignore sections.
  - **Dependency version** — `RELIABILITY_COMMITMENTS_SPEC.md` reference bumped v2.4.2 → v2.4.3 (deep-audit fixes).
- **April 19, 2026 — v0.5 Hegemony alignment.** Aligned presentation surface list with `RELIABILITY_COMMITMENTS_SPEC.md` v2.4 ship list. Cut spotlight tier, split-voice `attributed_lines[]`, and N+1 Talleyrand aside callback from the authoritative ship list; added Balance of Europe headline as a required v2.4 presentation. Disclaimed cut sections in a top-note (content remained in place; v0.5.1 trims the disclaimed content).
- **April 16, 2026 — v0.4 audit fixes.** Removed stale Godoy/Spain reference from §10.3 named-diplomat list (only 5 diplomats exist in v0.1 cast: Talleyrand, Castlereagh, Hardenberg, Metternich, Einsiedel). Fixed `commitment_paradox_resolved` speaker from `system` to `talleyrand` on notice surfaces — `system` is disallowed on rail surfaces per §10.3's own rule. Aligned terminology with `RELIABILITY_COMMITMENTS_SPEC.md` v2.2 rename: "rivalry" → "concern" where referenced.
- **April 16, 2026 — v0.3 rescope.** War bargain presentation moved to `WAR_BARGAIN_SPEC.md` slice WB-D. Collapsed `C3a` + `C3b` into one `C3-lite` slice. Three live events get spotlight + split-voice + named-diplomat treatment. Paradox simplified from 5-beat to 3-beat (framing → blocking body → after-choice aside). Reactive affordances cut to advisory routes only; response routes deferred to WB-D. N+5 fallback grievance slot cut as edge-case polish. Multi-spotlight overflow digest cut as edge-case polish. Witness scope-branching deferred to WB-D. Cast coverage minimum reduced from 9 lines (3 nations × 3 registers) to 4 lines (one per likely-victim nation). Acceptance criteria narrowed accordingly.
- **April 15, 2026 (Pass 2)** — folded 4-lens review findings per Pass 2 of `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md`. Changes: §8.3 overflow spotlight digest for climactic turns; §9.1 typographic contract + reveal cadence for split-voice; §9.2 period-label fixes; §10.3 named-diplomat routing mandatory; §12.5 paradox restaged as five-beat scene; §12.6 reactive affordances split into advisory routes and response routes; §13 N+5 fallback Morning Dispatch grievance slot; §14 new `C3a-pre` slice. **Most of these audit folds were narrowed back in the v0.3 rescope; they remain documented in the audit file as design history.**
- **April 15, 2026** — split `C3` into `C3a` routing and `C3b` drama, and folded designer-eye audit findings F1-F8 per `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md`. **Collapsed back into C3-lite in v0.3 rescope.**
- **April 15, 2026** — folded audit findings C-1..C-2, H-1..H-4, M-1..M-5, NEW-S1..S4, NEW-E1..E5, NEW-V1..V4 per `COMMITMENTS_PRESENTATION_AUDIT_FINDINGS.md`.
