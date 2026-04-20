# Commitments Presentation Pass — C3-lite Spec

> **Status:** v0.5 (Hegemony alignment pass)
> **Date:** April 19, 2026 (v0.5 — v2.4 hegemony alignment); April 16, 2026 (v0.4 audit); v0.3 rescope; v0.1 April 15, 2026
> **Phase placement:** Final slice of `Memory and Pressure` track (formerly `Reliability + Commitments`).
> **Depends on:** `RELIABILITY_COMMITMENTS_SPEC.md` v2.4.2 (hegemony engine + Balance of Europe headline + paradox rename), `RELIABILITY_IMPLEMENTATION_PLAN.md` v2.4, `DIPLOMAT_VOICE_BIBLE.md`, `CONVERSATIONAL_DIPLOMACY_DESIGN.md`, `INFORMATIONAL_UI_PLAN.md`
> **Bargain-era continuation:** `WAR_BARGAIN_SPEC.md` slice WB-D (presentation extension that adds bargain spotlights, scope-branched copy, response routes — only after `WAR_BARGAIN_SPEC` ships).

---

## v0.5 Rescope Note (April 19, 2026) — Hegemony alignment

The April 19 `RELIABILITY_COMMITMENTS_SPEC.md` v2.4 hegemony refactor cancelled several Slice C items this spec had specified as live. v0.5 aligns the presentation surface list with what v2.4 actually ships.

**v0.5 CUT (was live in v0.2-v0.4, cancelled by v2.4):**

- ❌ **Spotlight tier on the notification rail** (elevated card, 2-turn persist, action buttons) — three events do not justify the infra. Live events route through the existing notification system with named-diplomat copy carrying the dramatic lift. §7.2 and §8.2 below describe infrastructure that is NOT built in this phase.
- ❌ **Split-voice render `attributed_lines[]` with `lead` / `witness` / `aside` regions** — single-voice with named-diplomat attribution suffices at 5-nation scale. §9.1 typographic contract for split-voice rendering is NOT authoritative for v0.5 ship.
- ❌ **N+1 Talleyrand aside callback keyed by `episode_id`** — deferred to a later presentation pass if playtest shows the gap. §9.4 aftermath architecture reduces to the required after-choice aside on `commitment_paradox` only.
- ❌ **A1-fill, A2 fill, B2a-fill, B6** upstream dependencies in §2 Phase Placement — all cancelled in v2.4.

**v0.5 KEEPS (v2.4 ship list):**

- ✓ **Named-diplomat resolution helper** — `speaker="envoy"` resolves to the nation's named diplomat per Voice Bible; `speaker="foreign_office"` resolves to "The Chancery of {nation}". §10.3 is authoritative.
- ✓ **Committed mock prose** for the three live events using Voice Bible registers: `hard_reject_posture_triggered`, `diplomatic_treaty_broken` (`end_reason_family=french_breach`), `commitment_paradox_resolved`. §12 worked examples remain authoritative.
- ✓ **Dedicated `commitment_paradox_popup.{tscn,gd}` surface** — replaces legacy `alliance_paradox_popup` for the renamed type.
- ✓ **Balance of Europe headline** — new for v2.4. Three dynamically composed lines at the top of Diplomatic Ledger Nations tab per `RELIABILITY_COMMITMENTS_SPEC.md` §11.1. Rendering lives in `diplomatic_ledger.gd`.
- ✓ **Period-vocabulary icons / labels** and **priority tiers** per §9.2.

**Reading order for implementers:** treat any section below that describes infrastructure on the CUT list as non-normative. Build only the v0.5 KEEPS items. When this spec and v2.4 disagree, v2.4 wins.

**Estimated tests:** ~10-12 (named-diplomat resolution for each of 5 nations, three event copy paths, paradox popup field wiring, Balance of Europe headline composition for various states).

---

## v0.3 Rescope Note (April 16, 2026)

The April 16 audit established that the v0.2 spec was specced two audit rounds deep (`C3a` routing + `C3b` drama) for events the engine cannot produce. War bargains were never implemented, and the `bargain_*` events the spec dramatized — `bargain_fulfilled`, `bargain_breached`, `bargain_triggered`, `bargain_voided`, `bargain_ratified` — cannot fire in the current build.

The rescope:

1. **War bargain presentation moves to `WAR_BARGAIN_SPEC.md` slice WB-D**, where it lands when the bargain mechanic itself ships in the Peace Deals phase.
2. **`C3a` + `C3b` collapse into one `C3-lite` slice** that ships alongside the rest of `Memory and Pressure`.
3. **Three live events get the full spotlight + split-voice + named-diplomat treatment**: `hard_reject_posture_triggered`, `diplomatic_treaty_broken` (where `end_reason_family = french_breach`), and `commitment_paradox_resolved`.
4. **Paradox §12.5 staging simplifies from 5 beats to 3 beats** — Talleyrand framing → blocking body → spurned-envoy + Talleyrand after-choice. The five-beat scene with envoys from both spurned nations speaking before Talleyrand requires bargains-driven multi-conflict ratification (which doesn't exist in v0.1) to feel justified.
5. **Reactive affordances cut to advisory routes only**. Response routes (`Propose redress`, `Deepen the bond`, `Attempt to reopen the chancery`, `Denounce the refusal`) move to WB-D — they depend on bargain templates and on proposal_options seed defaults that don't exist yet.
6. **N+5 fallback grievance slot cut** as edge-case polish.
7. **Overflow spotlight digest cut** — multi-spotlight turns are rare on the 5-nation map; revisit if playtest shows the cap is starving climactic turns.

**Preserved from v0.2 (the flavor that matters):**

- Spotlight tier on the notification rail (elevated card, 2-turn persist, action buttons)
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
- concern pressure (direct + third-party anger on ratification — when the seed and B1/B2a-fill ship)
- commitment paradox hard stops (renamed alliance-cross-war; `commitment_paradox_resolved` log + dispatch event)

What it does **not** yet do is make those moments feel important in play. They land as one-liner notification rows.

This spec defines the narrow presentation pass that delivers political weight for the events that *do* fire today, without inventing drama for events that don't (those go to WB-D).

The pass remains **mechanically inert**. It owns framing, pacing, and surfacing. It does not own any diplomatic outcome.

---

## 2. Phase Placement

Final slice of `Memory and Pressure`. Sits after the spec/plan code work (concern seed, formula additions, paradox rename). Before any bargain work.

```text
A1 (✓) → A1-fill (concern seed) → A2 fill (ledger concern display)
                                → B1 (acceptance formula additions)
                                → B2a-fill (ratification anger)
                                → B6 (redemption tick)
                                → B3 (paradox rename)
                                → C3-lite (this spec)
                                → END OF MEMORY AND PRESSURE PHASE
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

Notification rail has three priority tiers rendered as identical 38×28 icons with color rings. There is no spotlight tier. Popup scenes have one text region. There is no split-voice render.

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

This pass uses four existing surface tiers, plus one new tier (the spotlight tier).

### 7.1 Blocking hard-stop

Use only when the player must decide **now**.

Already exists:

- `commitment_paradox` (renamed in B3 from `alliance_paradox`)
- `force_declare_war_confirmation`, `force_break_treaty_confirmation`

This spec does not create new hard-stop mechanics. It improves copy, emphasis, and fallout framing on `commitment_paradox` only (the other two already render their warnings via `proposal_confirm_popup`).

### 7.2 Dispatch spotlight (NEW tier — this spec ships)

Use for the three largest live political moments.

**Spotlight surface:** rendered on the **persistent notice rail** using an elevated "spotlight" style — a larger card, top-stacked above ordinary notices, persisting for 2 turns before decaying to a normal notice. The rail is the immediate in-turn surface.

**Relationship to Morning Dispatch:** Morning Dispatch owns a "Spotlight Carryover" section that replays any spotlight events raised during the previous turn as NEXT-TURN dispatch cards. In-turn spotlight display is the rail; next-turn reinforcement is the dispatch. Mid-turn commitments events never inject directly into `build_morning_dispatch()` — the rail is the mid-turn delivery path.

The dispatch spotlight should feel like:

- "something politically important just happened"
- "here is why it matters"
- "here is where to inspect it further"

### 7.3 Persistent notice

Existing tier. Used for medium-weight events. Remains visible and reviewable, does not stop play.

### 7.4 Ledger / campaign log reference

Every commitments event still appears in the durable reference layer. Ledger and log remain the source of truth.

---

## 8. Event Routing

### 8.1 Core event table (v0.3 — only live events)

| Event | Primary surface | Supporting surfaces | Notes |
|------|------------------|---------------------|-------|
| `commitment_paradox` | blocking hard-stop | ledger, campaign log, required after-choice aside | Renamed in B3. Three-beat staged scene per §12.5. |
| `hard_reject_posture_triggered` | dispatch spotlight | ledger, campaign log, optional N+1 aftermath | Door-closing moment. Voice = `foreign_office` resolved to "The Chancery of {nation}" with register from that nation's named diplomat. |
| `diplomatic_treaty_broken` (where `end_reason_family=french_breach`) | dispatch spotlight | ledger, campaign log, optional N+1 aftermath | Sharpest negative payoff in the live engine. Split-voice: lead = injured-party named diplomat, aside = Talleyrand. |
| `commitment_paradox_resolved` | persistent notice (reinforced by after-choice aside in §7.1 surface) | ledger, campaign log | Reinforces closure of the paradox. Not its own spotlight — the paradox itself was the spotlight moment. |
| `hard_reject_posture_cleared` | persistent notice | ledger, campaign log | Reopening should feel like cool-down, not its own spotlight. |
| `witness_strike_recorded` | persistent notice | ledger, campaign log | Default route for ordinary witness fallout. |
| `diplomatic_treaty_broken` (other end_reason families) | persistent notice | ledger, campaign log | Cascade ruptures don't get spotlights — France isn't at fault. |

**Bargain events routed to WB-D:**

`bargain_ratified`, `bargain_triggered`, `bargain_fulfilled`, `bargain_breached`, `bargain_voided`, `hard_block_surfaced` (ally-entry), `ally_refused_free_join`, `declaration_backed_out`, counter-bargain Accept/Reject/Back Out flows. None of these are addressed here — they ship with the bargain mechanic in `WAR_BARGAIN_SPEC.md` slice WB-D.

### 8.2 Spotlight threshold rules

Dispatch spotlight is reserved for:

- `hard_reject_posture_triggered` (first-time per pair only — emit contract enforces)
- `diplomatic_treaty_broken` where `end_reason_family = french_breach`

That's the v0.3 set. The paradox is its own blocking surface (§7.1) and consumes the spotlight slot on the turn it fires.

Do **not** spotlight:

- every witness strike
- every void
- every cascade-caused treaty break
- every paradox resolution after the player has chosen (the choice was the moment)

### 8.3 One-turn emphasis rule

Commitments items consume at most 1 spotlight slot and 2 non-spotlight notice slots **within the rail's existing budget**. Rail-wide budget is owned by `INFORMATIONAL_UI_PLAN.md`.

If multiple high-value commitments events occur together:

1. `commitment_paradox` (always wins — blocking)
2. `hard_reject_posture_triggered`
3. `diplomatic_treaty_broken` (french_breach)

The rest enter persistent-notice tier or ledger / campaign log.

**Multi-spotlight overflow:** v0.3 cuts the v0.2 "spotlight-lite + overflow digest" rule as edge-case polish. On the 5-nation map, two spotlight-worthy events on the same turn are rare. If playtest shows climactic turns are losing political weight to the cap, revisit.

### 8.4 No duplicate-surface rule

If an event already occupied a blocking surface this turn:

- do not also raise it as a separate persistent notice
- do not spawn a redundant dispatch line repeating the same information

Instead:

- fold the aftermath into the blocking result text
- write the durable record to ledger / campaign log

---

## 9. Surface Contracts

### 9.1 Dispatch spotlight card

Spotlight delivery uses the rail-elevated "spotlight" style described in §7.2 as the in-turn surface, and the Morning Dispatch "Spotlight Carryover" section as the next-turn reinforcement. Spotlights are not injected mid-turn into `build_morning_dispatch()`.

Each spotlight is "Scene 1" of a political moment, not a headline-only notice. Card contract:

- short player-facing period headline
- 2-4 lines of committed prose
- 1 compact consequence line naming the main political effect
- one obvious review action (`Open Ledger` or `Review Treaties`)
- one no-cost advisory follow-up action when the event family allows it (see §12.6)
- optional lower-weight secondary aside line with its own speaker attribution

Do **not** overload it with:

- full formula breakdowns
- five witness names
- exhaustive tooltip content

That belongs in the ledger and log.

Spotlight rendering must support both:

- single-voice cards using `speaker_attribution` plus body text
- split-voice cards using ordered `attributed_lines[]` blocks when the scene requires more than one speaker

`attributed_lines[]` role weighting is part of the contract:

- `lead` renders as the card's dominant line block
- `witness` renders as a subordinate middle line
- `aside` renders as a visually separated lower-weight strip or footer line

**Typographic contract for split-voice rendering.** The three roles must read as three registers, not three paragraphs with labels:

| Role | Weight | Size vs body | Treatment |
|---|---|---|---|
| `lead` | bold | 110% | left-aligned, speaker sigil + named attribution above the line (e.g. "— Hardenberg, at court") |
| `witness` | regular | 100% | indented 1 step, muted color, speaker sigil inline or trailing |
| `aside` | italic | 90% | visually separated by a thin divider above, muted warm color, speaker sigil in corner; reads as a note slipped sideways into the scene |

The three lines must not share a single text block. They are three distinct rendered regions in a single card.

**Reveal cadence.** On initial spotlight render, the lines fade in at a 400-600ms stagger so the witness reaction and Talleyrand's privacy arrive AFTER the lead, not simultaneously. A player who dismisses the card early sees all lines immediately — cadence is ornament, not gate.

`diplomatic_treaty_broken` (french_breach) uses a split-voice spotlight:

- lead line: injured-party named diplomat accusation (per Voice Bible register)
- aside line: private Talleyrand aside

Witness scope branching is **deferred to WB-D**. v0.3 ships single-tone breach copy. Once bargains exist, scope-branched copy lights up.

`hard_reject_posture_triggered` uses a single-voice card with `speaker="foreign_office"` resolved per §10.3.

### 9.2 Persistent notice card

Each commitments notice should show:

- event headline (using period vocabulary)
- main nation affected
- one-line consequence summary
- optional review action

Notice cards should be concise enough that three of them do not feel like a second dispatch.

#### Icon and label contract (v0.3 — only live events)

`notification_bar.gd` `TYPE_ICONS` extended with commitments types. Icon keys are proposed names; actual art is commissioned later.

Player-facing labels use period vocabulary. Internal `event_type` values remain unchanged.

| Event type | Icon key | Player-facing label |
|-----------|---------|---------------|
| `diplomatic_treaty_broken` (french_breach) | `icon_treaty_broken` | Word Broken |
| `diplomatic_treaty_broken` (other families) | `icon_treaty_dragged` | Treaty Dragged Apart / Articles Lapsed |
| `hard_reject_posture_triggered` | `icon_hard_reject` | The Chancery Shut |
| `hard_reject_posture_cleared` | `icon_chancery_reopened` | The Chancery Reopens |
| `commitment_paradox` | `icon_paradox` | Conflicting Oaths |
| `commitment_paradox_resolved` | `icon_paradox_resolved` | The Wound Chosen |
| `witness_strike_recorded` | `icon_witness_strike` | Europe Is Aware |

Bargain icons (`Word Kept`, `Articles Agreed`, `The Pledge Comes Due`, etc.) are deferred to WB-D.

#### Priority tier contract

Each commitments event maps to a `backend/notifications.py` priority tier. CRITICAL retained, NORMAL trimmed first under cap.

| Event type | Priority tier |
|-----------|---------------|
| `commitment_paradox` | CRITICAL |
| `diplomatic_treaty_broken` (french_breach) | CRITICAL |
| `hard_reject_posture_triggered` | CRITICAL |
| `commitment_paradox_resolved` | NORMAL |
| `diplomatic_treaty_broken` (other families) | NORMAL |
| `hard_reject_posture_cleared` | NORMAL |
| `witness_strike_recorded` | NORMAL |

### 9.3 Ledger emphasis

This pass should add emphasis, not a new ledger family.

Recommended emphasis rules:

- breached treaties (where France is at fault) get a recent-breach badge for a short window
- nations in hard-reject posture display a clear closed-door marker
- the latest commitments event should be easy to spot in the related ledger section

**Badge data source:** recent-breach badges derive from `backend/campaign_log.py` entries where `turn >= current_turn - 3` and `event_type == "diplomatic_treaty_broken"` with `end_reason_family == "french_breach"`. The closed-door marker reads from `has_hard_reject_posture(world, France, nation)` — not from log scanning.

**Review target routing:** the `review_target: "ledger_commitments"` action routes to the existing **Treaties** tab of the Diplomatic Ledger with a memory-and-pressure section filter applied. A dedicated commitments sub-tab is **out of scope** for v0.3.

(Recent-success / fulfillment badges deferred to WB-D — they need bargain fulfillment events that don't fire yet.)

### 9.4 Aftermath: minimum viable callback architecture

`episode_id` is not only a dedupe key. For spotlight-worthy or blocking commitments events, it is the memory hook for one aftermath beat.

Minimum contract by family (v0.3 — narrowed):

| Event family | Immediate result beat | N+1 aftermath | Later callback |
|-----------|---------|---------|---------------|
| `diplomatic_treaty_broken` (french_breach) | optional private aside inside the breach spotlight | optional private Talleyrand aside in next Morning Dispatch | deferred to WB-D |
| `hard_reject_posture_triggered` | none | optional Talleyrand aside in next Morning Dispatch | deferred to WB-D |
| `commitment_paradox` | required after-choice aside (in the popup, after the player chooses) | required next-turn dispatch callback | none |

Beats are short: 1-2 lines, not a second essay.

Caps:

- no more than 1 immediate result aside per `episode_id`
- no more than 1 N+1 aftermath beat per `episode_id`

Aftermath metadata may be stored on the originating surface payload or campaign-log entry keyed by `episode_id`; do **not** create a second authoritative commitments state store.

Escalation rule:

- a turn-`N+1` Talleyrand aside may not merely restate the turn-`N` aside; it must add one new beat such as a prediction, a posture read, or a named downstream consequence.

**N+5 fallback grievance slot, later-callback arbitration, and competing-callback priority** are all deferred — they are polish that depends on having more than one aftermath callback per episode (which v0.3 doesn't have).

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

Every commitments event that receives spotlight or notice treatment has:

- a deterministic headline template
- a deterministic body template
- slot values pulled from structured payloads

For v0.3 (mandatory committed templates):

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
| `diplomatic_treaty_broken` (french_breach) | `envoy` (named diplomat per §10.3) | `talleyrand` private aside | accusation first, private counsel second |
| `hard_reject_posture_triggered` | `foreign_office` (resolved as "The Chancery of {nation}") | optional Talleyrand N+1 aftermath aside | formal closure, no quips |
| `witness_strike_recorded` | `system` or `foreign_office` | none | terse third-party observation |
| campaign log | `system` | none | neutral declarative summary |

**Render contract:** single-voice notice detail uses `speaker_attribution` (valid values: `system`, `talleyrand`, `envoy`, `foreign_office`) as a field separate from body text. Split-voice spotlight/detail cards may instead provide ordered `attributed_lines[]` blocks, each with its own `speaker`.

Spotlight cards and expanded notice detail must support `speaker_attribution` and `attributed_lines[].speaker` values `system`, `talleyrand`, `envoy`, and `foreign_office` as structured attribution, not fake quoted text.

**Named-diplomat resolution (mandatory for envoy / foreign_office).** Abstract speaker roles are routing hints, not render values. At render time:

- `speaker="envoy"` MUST resolve to the named diplomat of the nation in context (Hardenberg, Metternich, Einsiedel, Castlereagh — the v0.1 cast from `diplomat.py`) and render with that diplomat's personality register per `DIPLOMAT_VOICE_BIBLE.md`. Hawk registers are blunt and prideful. Schemer registers are cold and calculating. Dove registers are wounded and bewildered.
- `speaker="foreign_office"` MUST render as "The Chancery of {nation}" — never as the generic string "foreign_office". Register derives from that nation's dominant diplomat's personality.
- `speaker="system"` is reserved for campaign-log summaries ONLY. On any rail or spotlight surface, `system` is disallowed — route to `foreign_office` or a named observer instead. The word "system" must never reach the player.
- **Loyalist fallback.** `backend/models/diplomat.py` permits a fourth personality value `loyalist` with no `DIPLOMAT_VOICE_BIBLE.md` entry. The v0.1 cast (Talleyrand / Castlereagh / Hardenberg / Metternich / Einsiedel) is schemer/hawk/dove only, so this is latent, not a current bug. If a future diplomat (new scenario, mod content) uses `loyalist`, the resolver MUST fail loudly (assert or explicit warning) rather than silently rendering unkeyed — pick a default register only after the Voice Bible adds a loyalist entry or a modding author supplies one.

For each breach lead-line template committed in §12.2, the mock template library should ship at least one register variant per nation that can be a victim of French breach. **v0.3 minimum cast coverage:**

- Prussia (Hardenberg, Hawk) — breach lead-line + hard-reject Chancery line
- Austria (Metternich, Schemer) — breach lead-line
- Saxony (Einsiedel, Dove) — breach lead-line
- Britain (Castlereagh, Hawk) — hard-reject Chancery line (Britain rarely receives a French breach since France-Britain is a primary concern and rarely deepens)

The previous v0.2 nine-line cast coverage requirement (3 nations × 3 personality registers) was sized for bargain breach scenarios. v0.3 minimum is **4 lines** (one per nation likely to be wronged in this phase).

### 10.4 Witness scope as dramatic input

`scope_reason` is not ledger garnish. It is the narrative selector for witness reactions.

- `ally` witnesses sound disappointed, wary, or reconsidering.
- `rival` witnesses sound pleased, amused, or opportunistic.
- `shared_enemy` witnesses sound calculating; they smell a strategic opening.
- `region_observer` witnesses sound gossipy or reputational; the story is spreading. (Inactive in v0.3 — region_observer scope only fires when bargains exist.)

**v0.3 application:** full scope-branched witness reaction copy with **named-diplomat registers** is deferred to WB-D (where bargain breaches justify that depth of cast work). But v0.3 ships **one skeletal canonical line per scope** so witness payloads do not all render identically on the rail:

| Scope | Skeletal canonical line (mock mode, v0.3 required) |
|---|---|
| `ally` | *"The court of {witness_nation} received the news in silence, and that silence is the register to note."* |
| `rival` | *"{witness_nation} has noted the news with the practiced calm of a court that has long been expecting it."* |
| `shared_enemy` | *"{witness_nation} has taken note; they understand France's hand was elsewhere this week, and they have drawn their own strategic reading."* |
| `region_observer` | *(inactive in v0.3 — no line authored until WB-D reactivates the scope)* |

These lines are **deliberately unvoiced** — no named diplomat, no personality register. They are the minimum visible difference between scopes. WB-D replaces each row with the full per-nation Hawk/Schemer/Dove voiced variant sourced from the Voice Bible cast. The skeletal v0.3 lines prevent the flatness failure ("every witness strike reads the same on the rail") without committing the full register work that belongs with the bargain era.

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
    "primary_surface": "dispatch_spotlight",
    "primary_nation": "Prussia",
    "secondary_nation": "France",
    "injured_party": "Prussia",
    "source_treaty_type": "alliance",
    "end_reason_family": "french_breach",
    "end_reason_action": "war_declaration",
    "fault_nation": "France",
    "attributed_lines": [
        {
            "speaker": "envoy",
            "role": "lead",
            "text": "Prussia was given France's word in clear terms..."
        },
        {
            "speaker": "talleyrand",
            "role": "aside",
            "text": "They are wounded, Sire. Worse, they are entitled to be."
        }
    ],
    "dominant_witness_scope": "ally",  # passed through but not branched on in v0.3
    "aftermath_mode": "private_aside_optional",
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

Required rules:

- all fields primitive-only
- no live object references
- no duplicate authority over commitment state
- `episode_id` is the episode-boundary key (see `RELIABILITY_COMMITMENTS_SPEC.md` §8.3); collapse, dedupe, and aftermath callback logic key off it
- `witness_nations` entries carry `scope_reason in {"ally", "rival", "shared_enemy", "region_observer"}` — `region_observer` inactive until WB-D
- `speaker_attribution` is optional shorthand for single-voice surfaces and must satisfy `speaker_attribution in {"talleyrand", "envoy", "foreign_office"}` (`system` reserved for campaign log only)
- `attributed_lines` is optional for split-voice surfaces; if present it overrides single-speaker render and may contain at most 3 ordered blocks
- `attributed_lines[].speaker in {"talleyrand", "envoy", "foreign_office"}`
- `attributed_lines[].role in {"lead", "witness", "aside"}`
- `aftermath_mode in {"none", "private_aside_optional", "private_aside_required"}`
- `follow_up_actions` entries are UI routing hints only; they may reference only existing **no-cost** advisory or inspection surfaces in v0.3 (response routes deferred to WB-D)
- `relation_delta` / `reliability_delta` are sourced from breach metadata
- `review_target: "ledger_commitments"` routes to the Treaties tab of the Diplomatic Ledger with a commitments section filter

If a field is not known deterministically, omit it rather than improvising it in presentation.

---

## 12. Example Player Experience

### 12.1 Treaty broken (French breach)

Engine outcome:

- France voluntarily breaks an alliance / DA / NA with Prussia (manual break, war declaration, paradox choice, or constructive breach via auto-decay)
- breach metadata applied; reliability and bilateral strike penalties applied per Memory and Pressure §8.3
- `dominant_witness_scope` computed (passed through to presentation but not branched on in v0.3)

Player experience:

- turn-N spotlight lands as a two-beat split-voice card:
  1. injured-party named diplomat accusation
  2. private Talleyrand aside
- next-morning dispatch optionally carries a private callback keyed by `episode_id`
- ledger and log preserve the exact fallout

Canonical mock spotlight templates (per Voice Bible registers):

- Headline: `Word Broken Before {injured_party}`

**Hardenberg (Prussia, Hawk) lead:**

> "Prussia was given France's word in clear terms. That word is now spent elsewhere. Tell your Emperor that Berlin does not ask twice. The army remembers the insult. So does the King."

**Metternich (Austria, Schemer) lead:**

> "Vienna has received word of the French disposition. Austria notes, with the customary patience of a court accustomed to the shifting weather of French commitments, that the article agreed between us has not been honored. There will be, naturally, no public reply. One simply adjusts."

**Einsiedel (Saxony, Dove) lead:**

> "Sire, His Majesty asked only that France's word be kept. We arranged Saxon affairs around it. We told our people that France had given assurance. It is not our place to accuse France, whose friendship Saxony values above all others. It is only that we had believed, and now we must explain to a small court that we were mistaken."

**Talleyrand (private aside, all variants):**

> "They are wounded, Sire. Worse, they are entitled to be. Force is often forgiven; ridicule is remembered."

**Next-morning callback (one new beat, not a restate):**

> "Hardenberg has not forgotten the matter, Sire. He need not mention it each morning for it to sit at table."

Desired feeling:

- "Europe noticed. The named court that I wronged has spoken in their own register."

(Scope-branched witness lines from v0.2 — Vienna-disappointed vs London-satisfied vs Italian-courts-gossiping — defer to WB-D when bargain breach gives them more political weight.)

### 12.2 Hard-reject posture triggered

Engine outcome:

- a nation crosses 3 active bilateral strikes and will now hard-resist deep treaties
- `hard_reject_posture_triggered` emitted (first-time-per-pair contract enforces single emission)

Player experience:

- one featured spotlight tells the player that this channel is effectively closing
- the next relevant preview / refusal reinforces the state
- the ledger makes it obvious the posture is active

Canonical mock spotlight template:

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

- Optional N+1 aside (Talleyrand):

  "Doors in Europe rarely slam, Sire. They close with a servant's politeness
  and a statesman's memory."

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
- next-turn dispatch carries one callback naming the spurned court

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

**Next-turn callback (Morning Dispatch):**

  "{spurned_nation} has received the news with the composure of a court
  counting knives."

Desired feeling:

- "I had to choose which to betray, and the spurned court spoke before Talleyrand named what I'd done."

**Implementation contract:**

- `commitment_paradox` is registered as HARD_STOP (already done in `dialogue_manager.py`); B3 activates it on the push side
- requires dedicated `commitment_paradox_popup.{tscn,gd}` surface (one of the four Slice C Godot prerequisites in §14)
- existing `alliance_paradox_popup.gd` is single-label and **cannot host** the three-beat scene; it must be replaced

(The five-beat scene from v0.2 — envoys from BOTH spurned nations speaking before Talleyrand frames — is **deferred to WB-D** when rivalry-driven multi-conflict ratification fires the paradox from new triggers.)

### 12.4 Reactive affordances (advisory routes only in v0.3)

Commitments surfaces may not leave the player as a reader only. v0.3 ships **advisory routes** (no cost, inspect / discuss). Response routes (`Propose redress`, `Deepen the bond`, `Attempt to reopen the chancery`, `Denounce the refusal`) are **deferred to WB-D** because they depend on bargain-era proposal templates and `proposal_options` seed defaults that don't exist yet.

**Advisory routes (v0.3 — no cost, inspect / discuss):**

| Action | Availability | Route | Mechanical effect |
|-----------|---------|---------------|---------------|
| `Speak to Talleyrand about this` | all commitments spotlights + paradox aftermath | opens scoped `advisory` dialogue with `context.origin_episode_id = episode_id` | none |
| `Summon {named_envoy}` | breach spotlight only | reuses advisory shell; opener is one-exchange foreign-court response in the named envoy's register, seeded by `episode_id`, then hands back to Talleyrand | none |
| `Review the broken treaty` | breach spotlight + paradox resolution | routes to filtered Treaties tab | none |

Rules:

- advisory routes remain no-cost, no state change, no notice on dismiss
- every spotlight family must expose at least one advisory route so the player can engage in-fiction within one click
- on the breach spotlight, both `Speak to Talleyrand` and `Summon {named_envoy}` may appear together; the named-envoy summon takes primary visual emphasis
- the paradox itself remains a strict binary — the player MUST choose. v0.3 has no `Offer redress to {spurned_nation}` next-turn affordance (that depended on bargain templates).

---

## 13. Anti-Spam Rules

- No more than 1 commitments dispatch spotlight per turn.
- No more than 2 above-the-fold commitments notices per turn.
- Blocking hard-stops suppress duplicate notice-generation for the same root event.
- Multiple witness strikes from one root event collapse into one summarized presentation event when surfaced outside the ledger. Witness-collapse keys off `episode_id`, not event-type heuristics.
- If a commitments event is unrelated to the current blocking popup, queue it into the normal notice/dispatch path instead of interrupting the player mid-resolution.
- No more than 1 immediate result aside and 1 N+1 aftermath beat may fire per `episode_id`.
- Quick-action follow-ups do not generate their own notices if opened and dismissed without state change.

(Later-callback arbitration, N+5 fallback grievance slot, and competing-callback priority rules are deferred — v0.3 has no later callbacks to arbitrate.)

---

## 14. Implementation Slice

### C3-lite. The single slice

**Files:** `backend/game_logic/dispatch.py`, `backend/game_logic/diplomatic_templates.py`, `backend/game_logic/diplomatic_dialogue.py`, `backend/game_logic/diplomatic_ledger.py`, `backend/campaign_log.py`, `backend/notifications.py`, `backend/models/dialogue_manager.py`, `backend/main.py`, `godot-client/.../main.gd`, `godot-client/.../notification_bar.gd`, `godot-client/.../diplomatic_ledger.gd`, `godot-client/.../campaign_log.gd`, new `commitment_paradox_popup.{tscn,gd}`, notice/dispatch surfaces already used by diplomacy

**Prerequisite work (must land before render contracts work):**

1. **Dedicated `commitment_paradox_popup.{tscn,gd}` surface.** Existing `alliance_paradox_popup` is single-label; cannot host three-beat staged scene. Build new popup on a CanvasLayer in the 101-118 range per CLAUDE.md "Adding a new popup/dialog" pattern. Re-uses HARD_STOP machinery, does NOT share scene with `alliance_paradox_popup`.
2. **HARD_STOP type activation.** B3 (paradox rename) ships push-side alias; this slice ensures Godot dtype whitelist (~main.gd line 697) routes `commitment_paradox` to the new popup.
3. **Split-voice render capability.** Extend notice/spotlight card scene to render three distinct regions (`lead` / `witness` / `aside`) with the typographic contract in §9.1. Extend `backend/notifications.py` payload dataclass to carry `attributed_lines[]` and `speaker_attribution`.
4. **Spotlight tier.** Add elevated 2-turn-persisting card variant to `notification_bar.gd` priority tiers, with per-notice review/follow-up action buttons. Without this, every event spec-routed to "dispatch spotlight" lands as a color-ringed icon.

**Core tasks:**

- Define commitments event routing rules across blocking / dispatch / notice / ledger per §8.1
- Add commitments-specific spotlight and notice templates under the `commitments_spotlight_*` / `commitments_notice_*` template family in `diplomatic_templates.py`
- Commit canonical mock prose for `diplomatic_treaty_broken` (french_breach), `hard_reject_posture_triggered`, and `commitment_paradox` (framing, blocking body, after-choice aside)
- Add player-facing period labels per §9.2
- Resolve `speaker="envoy"` and `speaker="foreign_office"` to named diplomats per §10.3 — single helper in backend that reads `world.diplomats[nation]` and returns `{name, register}`
- Commit minimum 4-line cast coverage per §10.3
- Stage `commitment_paradox` as 3-beat scene per §12.3 (Talleyrand framing → blocking body → spurned-envoy + Talleyrand asides)
- Add ledger emphasis rules for recent breach and active hard-reject posture (§9.3)
- Wire duplicate suppression so one event does not surface three times (§8.4)
- Keep campaign-log summaries compact but more specific
- Turn `episode_id` into a minimal memory hook for one N+1 aftermath beat per §9.4
- Inject N+1 callback lines into the next Morning Dispatch without changing mechanics
- Add advisory-route reactive affordances per §12.4 (`Speak to Talleyrand about this`, `Summon {named_envoy}`, `Review the broken treaty`)

**Suggested tests (~16-22):**

- Spotlight priority ordering across multiple same-turn commitments events
- No duplicate notice after blocking paradox resolution
- Hard-reject posture gets one featured moment, not a repeated every-turn notice
- Witness-strike collapse into one medium surface event per `episode_id`
- Save/load safety for any new transient surface payload
- Mock-mode template coverage for all spotlight-worthy commitments events
- `attributed_lines[]` rendering: lead / witness / aside as distinct regions
- Named-diplomat resolution: `envoy` → Hardenberg/Metternich/Einsiedel/Castlereagh per nation context, with correct register
- `foreign_office` → "The Chancery of {nation}"
- `system` speaker disallowed on rail surfaces
- Paradox 3-beat staging: framing renders before choice, after-choice aside renders post-choice
- N+1 aftermath beat fires once per `episode_id` and adds new content (escalation rule)
- N+1 aside does not restate the originating beat
- Advisory routes are no-cost: `Speak to Talleyrand` opens advisory dialogue with `context.origin_episode_id`; dismiss leaves no state change

**Estimated budget:**

- **two implementation sessions:**
  1. *Godot surfaces* — new `commitment_paradox_popup.{tscn,gd}` (3-beat staged scene per §12.3, on its own CanvasLayer in the 101-118 range), split-voice render capability in `notification_bar.gd` (three distinct regions for `lead` / `witness` / `aside` per §9.1 typographic contract), elevated-card spotlight tier (2-turn persist, action buttons, per-notice review/follow-up), HARD_STOP dtype whitelist routing in `main.gd` for the renamed `commitment_paradox` type.
  2. *Tests + mock prose* — named-diplomat resolution helper (`speaker="envoy"` / `speaker="foreign_office"` per §10.3), committed prose for the three live events using Voice Bible registers, ledger emphasis rules (§9.3), N+1 aftermath callback wiring, advisory-route reactive affordances (§12.4).
- approximately 16-22 tests total across the two sessions

---

## 15. Future Handoff

This pass should hand off cleanly to later systems:

- **`Bilateral Peace Hardening`**
  - owns its own spotlight events for peace settlement theatrics; the commitments router is commitments-specific and does not extend to peace fallout. Bilateral Peace Hardening may copy patterns, but it does not reuse the commitments router.
- **`WAR_BARGAIN_SPEC.md` slice WB-D (bargain presentation extension)**
  - extends this pass with `bargain_fulfilled` / `bargain_breached` / `bargain_voided` / `bargain_ratified` / `bargain_triggered` / `declaration_backed_out` spotlights and notices
  - adds scope-branched witness reaction copy (uses `dominant_witness_scope` payload that this pass already passes through)
  - adds response routes (`Propose redress`, `Deepen the bond`, `Attempt to reopen the chancery`, `Denounce the refusal`)
  - adds N+5 fallback grievance slot
  - adds five-beat paradox staging when rivalry-driven ratification paradox fires the new triggers
- **`Talleyrand Desk + Explanation Layer`**
  - can absorb the same commitments payloads into richer advisory surfaces later, but it does **not** own inventing the first breach/paradox aftermath beats from scratch. C3-lite already commits the minimum callback architecture.
- **Generalized coalition work**
  - may later reuse the same spotlight principles for bloc pressure and split events.

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
- `episode_id` supports one bounded N+1 aftermath beat per spotlight event
- at least one no-cost conversational follow-up exists on every spotlight family
- all of the above work identically in mock mode without LLM dependency
- no commitments presentation surface changes any underlying outcome

Bargain-era acceptance criteria (`bargain_breached` 3-beat sequence, scope-branched copy, response routes, etc.) move to `WAR_BARGAIN_SPEC.md` WB-D.

---

## 17. Changelog

- **April 16, 2026 — v0.4 audit fixes.** Removed stale Godoy/Spain reference from §10.3 named-diplomat list (only 5 diplomats exist in v0.1 cast: Talleyrand, Castlereagh, Hardenberg, Metternich, Einsiedel). Fixed `commitment_paradox_resolved` speaker from `system` to `talleyrand` on notice surfaces — `system` is disallowed on rail surfaces per §10.3's own rule. Aligned terminology with `RELIABILITY_COMMITMENTS_SPEC.md` v2.2 rename: "rivalry" → "concern" where referenced.
- **April 16, 2026 — v0.3 rescope.** War bargain presentation moved to `WAR_BARGAIN_SPEC.md` slice WB-D. Collapsed `C3a` + `C3b` into one `C3-lite` slice. Three live events get spotlight + split-voice + named-diplomat treatment. Paradox simplified from 5-beat to 3-beat (framing → blocking body → after-choice aside). Reactive affordances cut to advisory routes only; response routes deferred to WB-D. N+5 fallback grievance slot cut as edge-case polish. Multi-spotlight overflow digest cut as edge-case polish. Witness scope-branching deferred to WB-D. Cast coverage minimum reduced from 9 lines (3 nations × 3 registers) to 4 lines (one per likely-victim nation). Acceptance criteria narrowed accordingly.
- **April 15, 2026 (Pass 2)** — folded 4-lens review findings per Pass 2 of `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md`. Changes: §8.3 overflow spotlight digest for climactic turns; §9.1 typographic contract + reveal cadence for split-voice; §9.2 period-label fixes; §10.3 named-diplomat routing mandatory; §12.5 paradox restaged as five-beat scene; §12.6 reactive affordances split into advisory routes and response routes; §13 N+5 fallback Morning Dispatch grievance slot; §14 new `C3a-pre` slice. **Most of these audit folds were narrowed back in the v0.3 rescope; they remain documented in the audit file as design history.**
- **April 15, 2026** — split `C3` into `C3a` routing and `C3b` drama, and folded designer-eye audit findings F1-F8 per `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md`. **Collapsed back into C3-lite in v0.3 rescope.**
- **April 15, 2026** — folded audit findings C-1..C-2, H-1..H-4, M-1..M-5, NEW-S1..S4, NEW-E1..E5, NEW-V1..V4 per `COMMITMENTS_PRESENTATION_AUDIT_FINDINGS.md`.
