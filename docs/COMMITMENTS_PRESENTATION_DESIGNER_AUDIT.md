# Commitments Presentation Spec — Designer-Eye Audit

> **Date:** Apr 15, 2026
> **Target:** `docs/COMMITMENTS_PRESENTATION_SPEC.md` after audit-findings fold (commit 9721453)
> **Lens:** Narrative / systems designer, not engineering. Prior audit closed 24 contract/routing gaps; this pass judges whether the spec delivers *political drama* or a well-formed routing table.
> **Verdict:** **Not shippable as a narrative pass.** Score 2.1 / 5 across 8 axes. Treat shipped work as `C3a (routing)`; open `C3b (drama)` before approval.

---

## Context for New Sessions

The commitments engine (rivalries, betrayal memory, war bargains, hard-reject posture, counter-bargains, witness strikes, commitment paradox) is specified mechanically in `RELIABILITY_COMMITMENTS_SPEC.md` and `RELIABILITY_IMPLEMENTATION_PLAN.md`. `COMMITMENTS_PRESENTATION_SPEC.md` is the narrow pass that frames those mechanics as felt political moments rather than log lines.

The just-folded audit fixed every routing, payload, and ownership gap. In doing so it hardened the spec's engineering skeleton to the point where its dramatic body never grew in. This designer audit names what the fold left undone.

---

## 8 Findings

### F1 — The spec never writes a line of Talleyrand
**Sections:** §9.1 / §10.1 / §12
Every "example player experience" ends with a feeling bullet ("This alliance meant something") but never drafts the sentence the player will actually read. `CONVERSATIONAL_DIPLOMACY_DESIGN.md` has 27 real-prose templates. C3 has none. A presentation pass that refuses to audition its own voice is a routing spec.

**Required:** At minimum, one full template each for `bargain_breached`, `bargain_fulfilled`, `hard_reject_posture_triggered`, and `commitment_paradox` follow-up — written in the Schemer voice, with slot markup, at the 2-4 line spotlight length §9.1 promises. Otherwise engineering ships placeholder strings and the feeling is whatever lands in the first PR.

---

### F2 — `bargain_breached` is a notification, not an accusation
**Sections:** §8.1, §12.2
The betrayal payoff should be the game's most operatic moment — the player *made* a promise, *broke* it, a witness nation *watched*. Spec delivers it as: spotlight card + notice + ledger line. No accusation beat (who names the perfidy?), no witness reaction beat (who speaks for Austria when Prussia saw France break faith over Hanover?), no posture-shift beat (does the betrayed party's next proposal carry the wound?).

**Required:** §12.2 specifies a three-beat sequence:
1. Betrayed-party voice line on the breach turn
2. One scoped witness reaction drawing on `witness_nations[].scope_reason` ("Vienna notes that Berlin's word was given publicly")
3. Next-morning Talleyrand private aside

Today only beat 1's container exists; no copy committed.

---

### F3 — Witness `scope_reason` is plumbed but dramatically unused
**Sections:** §11 payload, §10.3
The audit added `scope_reason ∈ {ally, rival, shared_enemy, region_observer}` — a gorgeous narrative hook. A rival-witness breach ("Prussia watched this, and Prussia *likes* this") is a fundamentally different political moment from an ally-witness breach ("Austria watched this, and Austria is reconsidering"). The spec then routes all witnesses through `system` voice and never branches presentation on `scope_reason`.

**Required:** §9.1 states spotlight copy varies by dominant witness scope — rival-scope headline family ≠ ally-scope headline family. Otherwise the classification exists only for the ledger to ignore.

---

### F4 — The paradox is the game's best moment and the spec hides it
**Sections:** §8.1 row, §7.1, §12 (absent)
`commitment_paradox` is the one place the engine produces a true tragic collision — the player *cannot* honor two bargains. Spec gives it one table row, defers all copy to `CONVERSATIONAL_DIPLOMACY_DESIGN.md`, includes no §12.5 worked example. Witness strikes get more spec real estate than the paradox.

**Required:** Add §12.5 "Commitment paradox" with a full before/during/after arc — moment of discovery, blocking-dialogue copy, Talleyrand aside *after* the player chooses, whether the next morning dispatch carries a callback. Right now the paradox will feel smaller than a witness strike.

---

### F5 — No cross-scene callback architecture
**Sections:** §7-§9, §16
A commitments moment fires on turn N — spotlight, notice, ledger row. Turn N+1 gets Morning Dispatch "Spotlight Carryover." That's one beat. No provision for:
- Talleyrand private aside in N+1's dispatch that isn't a carryover card ("Hardenberg has not forgotten Hanover, Sire")
- Anniversary callback when the same nation is encountered 5-10 turns later
- Voice-infection where the betrayed nation's next `incoming_proposal` body carries one barbed line referencing the breach

§15 explicitly hands these to future phases that refuse them. They will not exist.

**Required:** §9 adds "Scene 2: Aftermath" subsection with at minimum the N+1 private aside and an "episode memory" hook §12.2/12.3 can reference. Without this, `episode_id` is a dedupe key, not a memory.

---

### F6 — Political vocabulary is the engineer's vocabulary
**Sections:** §8.1, §9.2 labels
Default labels shipped in §9.2: "Bargain Breached," "Bargain Fulfilled," "Channel Closed," "Witness Strike," "Declaration Withdrawn." Other surfaces use "courts of Europe," "Hardenberg knows." These labels read like a CI dashboard. "Witness Strike" is industrial-action vocabulary, not 1805.

**Suggested period labels:**
| Current (engineer) | Period (designer) |
|---|---|
| Bargain Breached | Word Broken / Pledge Dishonoured |
| Bargain Fulfilled | Word Kept / The Promise Redeemed |
| Channel Closed | The Chancery Shut |
| Witness Strike | The Courts Noticed / A Dispatch from Vienna |
| Declaration Withdrawn | Ultimatum Recalled |

Internal `event_type` stays. §9.2's *player-facing label* column rewrites. This alone does more for "feels like political drama" than any routing change.

---

### F7 — Talleyrand as default spotlight voice flattens the cast
**Sections:** §10.3
Defaulting spotlights to Talleyrand turns every commitments moment into Talleyrand-on-Talleyrand-on-Talleyrand. Coalition brewing already uses Talleyrand. Morning Dispatch carryover already uses Talleyrand. If *everything* important is Talleyrand, nothing is.

**Required split by event family:**
| Event | Voice | Register |
|---|---|---|
| `bargain_fulfilled` | Talleyrand | quippy vindication — his native register |
| `bargain_breached` | Injured party's envoy | headline; + one private Talleyrand aside below ("They are wounded, Sire. I expected it.") |
| `hard_reject_posture_triggered` | System / foreign-court voice | "The Prussian chancery no longer receives French despatches" |
| `commitment_paradox` | Talleyrand, grave | explicitly *not* quippy |

§10.3 needs this resolution. Right now the spec hasn't committed to *what* Talleyrand is as distinct from *when he speaks*.

---

### F8 — The player has no reactive affordance
**Sections:** §7-§12 (all surfaces)
Across every commitments event the player is a *reader*, not a *responder*. A spotlight card has one action: `Open Ledger`. When Prussia breaks faith over Hanover, the player cannot say "demand explanation," "summon the Prussian envoy," "instruct Talleyrand to comment publicly." This is the game that sold itself on "you talk to your generals" (VISION.md). Commitments is the first system to arrive without a conversational hook.

**Required:** Add §12.6 "Reactive Affordances" naming 2-3 no-cost conversational follow-ups on breach spotlights — e.g. "Speak to Talleyrand about this" quick-action that opens a scoped `advisory` dialogue seeded with `episode_id`. Mechanics stay inert (non-goal preserved). The player becomes an actor again.

---

## Axis Scorecard (1 = flat, 5 = alive)

| Axis | Score | Why |
|---|---|---|
| Emotional legibility | 2 | Events *named* big, never *staged* big. No committed copy. |
| Voice authenticity | 2 | Talleyrand listed as default but never heard. Witness carve-out to system correct but lonely. |
| Moment hierarchy | **4** | §8.3 one-spotlight-per-turn rule is genuinely good. §13 anti-spam solid. |
| Political vocabulary | 2 | Labels are engineering nouns. "Witness Strike" is the worst offender. |
| Overdesign vs underdesign | 2 | Overdesigned as routing, underdesigned as drama. Payload contract longer than all narrative examples combined. |
| Cross-scene coherence | 2 | Carryover is the only committed beat. No aftermath, callbacks, or memory. |
| Paradox treatment | **1** | One table row, no §12 entry, all copy deferred. Best moment in the engine is the least loved in this spec. |
| Missing affordances | 2 | Player passive across whole surface set. No "demand explanation," no anniversary, no voice-infection. |

**Average: 2.1 / 5**

---

## Final Verdict

**Not shippable as a narrative pass.** Well-formed routing table that will produce bloodless play. Ship the routing work as `C3a` if engineering pressure demands. Do not let this document stand in for the presentation pass.

**`C3b` must follow with:**
1. Committed template prose (F1)
2. Three-beat betrayal sequence (F2)
3. Scope-branched copy (F3)
4. Full paradox experience entry §12.5 (F4)
5. Aftermath/callback architecture §9 Scene 2 (F5)
6. Period-voice label rewrites §9.2 (F6)
7. Voice-by-event-family mapping §10.3 (F7)
8. Conversational reactive affordances §12.6 (F8)

Without these the commitments engine will compute perfect political drama and deliver it as a changelog.

---

## Pass 2 — 4-Lens Review (Apr 15, 2026, post-F1-F8 fold)

> F1-F8 were folded into spec v0.2. This pass re-reviewed the spec with four distinct lenses — narrative/systems, UX/dramaturgy, player-agency, implementation-reality — to judge whether the folded fixes delivered political drama or a better-decorated routing table. Verdict: better, not there.

### Methodology

Four reviewers read `COMMITMENTS_PRESENTATION_SPEC.md` v0.2, `CONVERSATIONAL_DIPLOMACY_DESIGN.md` v1.2, and `VISION.md` in parallel. Implementation-reality reviewer additionally read `dialogue_manager.py`, `diplomatic_executor.py`, `main.gd`, `notification_bar.gd`, `alliance_paradox_popup.gd`. No reviewer timed out.

### Findings — High Severity

#### P2-H1. `commitment_paradox` is not registered as a hard-stop
**Lens:** Implementation-reality | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:217,309,764-774`; `dialogue_manager.py:38-41` (`HARD_STOP_TYPES = frozenset({"force_declare_war_confirmation", "alliance_paradox"})`)
Spec declares paradox "blocking" with required before-choice framing, body, after-choice aside, and N+1 callback. Taxonomy does not list it; Godot dtype whitelist does not list it. With current wiring, the grave "France may choose which wound it opens" beat auto-lapses on end-turn like a regular `proposal_confirm`. The best prose in the spec lands on a non-blocking surface. Fix is mechanical but must be explicit in §14.

#### P2-H2. Split-voice `attributed_lines[]` has no render surface
**Lens:** Implementation-reality | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:292-309,555-597`; `notification_bar.gd:99-155`; `alliance_paradox_popup.gd:36-49`
Spec mandates breach spotlights render `lead` / `witness` / `aside` blocks with distinct visual weight. No `attributed_lines` or `speaker_attribution` field exists in backend or Godot. Notice rail renders single icon+tooltip; the nearest multi-line surface (`alliance_paradox_popup`) is one label with one hardcoded "Talleyrand:" tag. The core dramatic device for betrayal has no surface to land on.

#### P2-H3. "Dispatch spotlight" tier does not exist as a surface
**Lens:** Implementation-reality | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:172-186`; `notification_bar.gd:18-28`
Spec promises an elevated 2-turn-persisting card with per-notice review/follow-up action buttons. Rail has three priority tiers (0/1/2) of identical 38×28 icons with color rings, no action buttons, `MAX_VISIBLE_ICONS := 6`. `dispatch.py` has no "Spotlight Carryover" section. Without a real tier, every spotlight-worthy event lands indistinguishable from a DP warning icon.

#### P2-H4. Betrayal is accused by an anonymous "envoy" — the named cast is benched
**Lens:** Narrative / systems designer | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:493,557,665`
`CONVERSATIONAL_DIPLOMACY_DESIGN.md` §6 gives us Hardenberg (Hawk), Metternich (Schemer), Einsiedel (Dove), Castlereagh with distinct registers. When France breaks faith, the lead speaker is the abstract role `envoy`. The player hears "France gave its word on Hanover; today that word is spent elsewhere" — chancery minutes, not a prideful Prussian's accusation. VISION's "people, not systems" fails at the single most operatic moment in the system. `hard_reject_posture_triggered` has the same problem with `foreign_office`.

#### P2-H5. Paradox is narrated, not dramatized — both courts never speak
**Lens:** Narrative / systems designer | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:780-804`
Talleyrand owns every line of the paradox scene. Vienna and Berlin exist as template slots and are never heard. The player experiences a handsome rhetorical structure from one voice, not two parties in contradictory demand. The dilemma is announced rather than staged. Compare: if Hardenberg's envoy demanded the old pledge in one beat and Metternich's envoy the new, THEN Talleyrand framed the impossibility, the player would feel the vise instead of the narration.

#### P2-H6. Three-beat breach collapses to one card
**Lens:** UX / dramaturgy | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:302-308,654-657`
Spec frames breach as a "three-beat sequence" (accusation → witness → aside) but §9.1 emits all three beats simultaneously inside one `attributed_lines[]` card. That is a paragraph, not a sequence. Without reveal cadence or surface separation, the witness's judgment and Talleyrand's privacy arrive at the same instant as the accusation. The opera compresses to a stanza.

#### P2-H7. Spotlight shares the notification rail with ordinary notices
**Lens:** UX / dramaturgy | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:177-179`
Spotlight is described as "a larger card, top-stacked" on the same rail "persistent notice" uses. "Word Broken Before Prussia" and "Articles Agreed with Bavaria" share visual vocabulary, distinguished only by size and stack order. Players trained on the rail dismiss reflexively. The spec has a tier name without a tier experience.

#### P2-H8. One-spotlight-per-turn cap silently starves climactic turns
**Lens:** UX / dramaturgy | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:240,834`
The turn where Austria fulfills, Prussia breaches, and Britain enters hard-reject posture should feel like a three-front political earthquake. Spec shows one spotlight and quietly demotes the other two to ordinary notices. The demoted events get no signal that they are the second- and third-biggest political moments of the year. Closure and vindication become indistinguishable from a void.

#### P2-H9. Reactive affordances are cosmetically uniform, not event-specific
**Lens:** Player-agency | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:814-829`
The three reactive buttons — `Speak to Talleyrand about this`, `Summon the envoy`, `Review the pledge` — are explicitly no-cost, no state change, no DP/AP, no relation delta. On a betrayal, the player's only verb is "talk about it in a menu that cannot change anything." This is the VISION firewall failure: "every input gets a response" inverts to "every event gets a toast." Compression of agency wearing the skin of agency.

#### P2-H10. Paradox, hard-reject, and Back Out have no in-fiction response verb
**Lens:** Player-agency | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:764-808,709-741,220,744-762`
Paradox: pick A or B; no delay, buyoff, renegotiate, or Talleyrand pleading route. Hard-reject: door slams; no attempt-to-reopen route. Back Out: silent cancellation with no "Ally refused" notice, no denunciation, no reframe. Three separate high-drama moments where the player is strictly a reader. The drama was computed and then hidden from action.

### Findings — Medium Severity

#### P2-M1. Fulfillment prose delivers "France behaved correctly," not "this alliance meant something"
**Lens:** Narrative | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:629-642`
Canonical template is elegant Talleyrand-as-narrator but emotionally cold. No gratitude from the fulfilled party, no gesture, no softened posture. Positive reward becomes sophisticated aphorism.

#### P2-M2. Period labels leak modern vocabulary
**Lens:** Narrative | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:352-361`
`witness_strike_recorded → "The Courts Noticed"` is modern journalistic idiom. `declaration_backed_out → "Ultimatum Recalled"` reads as UI status line. Alternatives: "Europe Is Aware" / "Dispatches Travel"; "The Demand Withdrawn."

#### P2-M3. Witness scope is tone-adjective swap, not structural reaction
**Lens:** Narrative / Player-agency | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:324-330,503-512`
Four witness-scope tones change one line of prose and nothing else. A rival-witness breach should let the rival propose to us on the back of the breach; an ally-witness breach should surface a reassurance-gesture affordance. Computes politics, renders tone-color.

#### P2-M4. Witness collapse mutes the crowd
**Lens:** UX | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:312-331,837`
Four courts reacting to the same breach render as one named witness plus ledger silence. Europe-as-chorus never reaches the surface. A compact "and three other courts took note" trailer with flags would preserve the anti-spam guarantee and restore plurality.

#### P2-M5. Callbacks silently expire when no eligible surface appears
**Lens:** UX | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:404-411,420-425`
If the injured party sends no `incoming_proposal` and the player opens no advisory within 10 turns, the callback evaporates. Colder relationships → less memorable betrayals, which is backwards. A Morning Dispatch "unresolved grievance" fallback at N+5 closes the gap.

#### P2-M6. Split-speaker attribution is structural but visually uncommitted
**Lens:** UX | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:298-302,500-501`
`lead` / `witness` / `aside` roles are defined in prose but no typographic contract exists. Three paragraphs with speaker labels ≠ distinct registers. Commit font, color, indent, and divider per role before C3b.

#### P2-M7. No cross-event sequencing rule
**Lens:** UX | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:242-250,256-265`
Priority covers which event gets spotlight, not the order in which a paradox + breach turn presents. Drama benefits from "the paradox happens, then the consequence arrives." Without rule, implementation may sequence arbitrarily.

#### P2-M8. No ultimatum beat family
**Lens:** Narrative | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:203-221`
Commitments drama with nothing to say about "comply or I act" misses a signature Napoleonic move. `declaration_backed_out` + `hard_reject_posture_triggered` gesture but do not frame as ultimatums.

#### P2-M9. `foreign_office` and `envoy` speaker roles have no router in code
**Lens:** Implementation-reality | **File:** `COMMITMENTS_PRESENTATION_SPEC.md:490-502`; `diplomatic_templates.py` (no `speaker` field)
Tonal differentiation the spec demands (formal closure for hard-reject, accusation for breach) requires a speaker-selector. Without it, every spotlight falls back to Talleyrand's urbane register. Closure sounds like vindication sounds like grievance.

#### P2-M10. Advisory flow is a universal sink that dilutes scoped follow-ups
**Lens:** Player-agency | **File:** `CONVERSATIONAL_DIPLOMACY_DESIGN.md:§8` + `COMMITMENTS_PRESENTATION_SPEC.md:817`
`Speak to Talleyrand about this` passes `origin_episode_id` as context, but the advisory flow ends with "Thank you / What should we do / How do we improve relations" — none change the betrayer's trust, injured ally's relation, or paradox's spurned court. The scope is a narrative hook, not a gameplay hook.

### Findings — Low Severity

- **P2-L1** (UX): Headlines use `{event label} in {nation}` pattern — foregrounds event type over moment. `COMMITMENTS_PRESENTATION_SPEC.md:350-360`
- **P2-L2** (UX): Two quick-actions on breach can fragment one scene into four surfaces. `:815-828`
- **P2-L3** (Narrative): `system` as speaker breaks 1805 veneer; "chancery observer" / "court intelligencer" preferable. `:496,499`
- **P2-L4** (Narrative): Scene 1 / Scene 2 theatrical metaphor is flourish, not organizer.
- **P2-L5** (Player-agency): Proactive-suggestion routing (CONVERSATIONAL §8) is the positive example the commitments pass never copied.

### Convergence

All four reviewers independently converge on a single root problem:

> **The spec is a routing and payload specification, not a dramaturgy specification.** It builds excellent slots (spotlight tier, `attributed_lines[]`, scope branching, `episode_id` memory, follow-up actions) and then fills them with generic content (anonymous envoy, Talleyrand narrator, non-specific quick actions, cosmetic witness branching). Implementation-reality shows the slots themselves are mostly unbuilt, so the spec writes a check the engine cannot cash.

Secondary convergence: the spec's self-imposed firewall ("no new outcomes, no new action costs, no mechanical change") is load-bearing for Non-Goals §5 but fatal for player agency. The fix is not to break the firewall but to widen the router — route reactive affordances into EXISTING action surfaces (proposal wizard, advisory, mission), where existing costs apply. The firewall bars inventing; it does not bar routing.

### Disagreements between reviewers

- **Narrative M5 (flavor affordances)** vs **Player-Agency H9 (state-changing verbs):** narrative argued for "Send gift of consolation" (flavor only, no state), player-agency argued this is still reader-only and demanded at least one state-changing verb per spotlight family. **Resolution:** both. Flavor affordances are welcome, but at minimum one verb per spotlight family must route to an existing action surface (not invent a new action), so the player can respond in-fiction.
- **UX M4 (carryover vs aftermath distinction)** vs **Narrative H4 (N+1 vague):** UX wants structural clarity on whether the N+1 aftermath replaces or sits alongside the carryover card. Narrative wants a concrete example of a good N+1 beat. **Resolution:** both needed. §9.4 gets a visual rule (aftermath replaces carryover when both present) and a concrete exemplar ("Hardenberg canceled the trade delegation to Lyon this morning").
- No contradictions on implementation-reality findings — all reviewers treated those as ground truth.

### Score: 3.0 / 5 (up from 2.1 Pass 1)

| Axis | Pass 1 | Pass 2 | Why |
|---|---|---|---|
| Emotional legibility | 2 | 3 | Prose committed; still aphoristic and single-voiced |
| Voice authenticity | 2 | 2 | Talleyrand real, enemy cast benched at the critical beats |
| Moment hierarchy | 4 | 3 | Hierarchy exists; one-spotlight cap and shared rail erode felt difference |
| Political vocabulary | 2 | 4 | Most labels fixed; two leaks remain |
| Overdesign vs underdesign | 2 | 3 | Payload contract now has prose peers; still overweight on plumbing |
| Cross-scene coherence | 2 | 3 | Aftermath architecture present; expiration is silent, N+1 vague |
| Paradox treatment | 1 | 2 | §12.5 exists; still one-voice narration and implementation contracts missing |
| Missing affordances | 2 | 2 | Three no-cost buttons is affordance in name only |
| Implementation contracts | — | 2 | New axis — spec promises surfaces that do not exist |

### Verdict: **close, not shippable**

- **`C3a` routing slice:** close to shippable provided §14 is expanded to explicitly stand up the four missing surface contracts (paradox HARD_STOP registration, spotlight tier, `attributed_lines[]` render surface, envoy/foreign_office speaker router). Without these, `C3a` is a backend-only pass that routes payloads into nothing.
- **`C3b` drama slice:** not shippable. Cast discipline, paradox dramatization, and player-agency require material rework. The prose exists; the staging does not.

### Top 3 Fixes Next

1. **Promote paradox to real hard-stop AND stage it as two-voice.** Register `commitment_paradox` in `HARD_STOP_TYPES` and `main.gd` dtype whitelist. Build a dedicated `commitment_paradox_popup` — do not reuse `alliance_paradox_popup`, which is single-label and cannot host before-choice framing + blocking body + after-choice aside. Revise §12.5 so envoys from both spurned nations deliver their demands before Talleyrand frames the contradiction. Addresses P2-H1, P2-H5, P2-M4 (implementation).

2. **Name the envoy. Name the chancery.** Extend §10.3 render contract: when `speaker="envoy"`, resolve to the injured party's named diplomat (Hardenberg/Metternich/Einsiedel/Castlereagh) with per-personality register (Hawk/Schemer/Dove) per `CONVERSATIONAL_DIPLOMACY_DESIGN.md` §6. When `speaker="foreign_office"`, render as "The Chancery of {nation}" with register derived from that nation's dominant diplomat. Commit at least three breach lead-lines (one per personality register). Addresses P2-H4, P2-M9.

3. **Widen the firewall to permit routing, not inventing.** Revise §12.6 so reactive affordances may route into existing action surfaces at their existing costs. Add one state-changing route per spotlight family: breach → `Propose redress to {injured_party}` (opens proposal_options seeded with protection/reparation defaults); fulfillment → `Deepen the bond with {primary_nation}` (opens proposal_options seeded with alliance upgrade); hard-reject → `Attempt to reopen the chancery` (opens proposal_confirm with low-acceptance preview); Back Out → `Denounce the refusal` (routes to existing proposal_options as a public-posture gesture). The spec's Non-Goal firewall stays intact — nothing new is invented, existing actions are reused. Addresses P2-H9, P2-H10, P2-M10.

### Follow-Up Fixes (Medium Priority)

- §8.3: Add overflow rule for multi-high-value turns (second and third events get demoted "spotlight-lite" treatment with a brief overflow digest card, not undifferentiated notice).
- §8.5 new: Cross-event sequencing rule — paradox resolves before same-turn breach/fulfillment spotlights.
- §9.1: Commit typographic contract for `lead` / `witness` / `aside` (font size, color, divider).
- §9.2: Fix two period-label leaks.
- §13: Add N+5 Morning Dispatch "unresolved grievance" fallback for callbacks with no natural surface.
- §12.2: Commit concrete N+1 aftermath exemplar.
- §14: Flag the four missing surface contracts as explicit prerequisite work.

### Appendix: Implementation Contracts That ARE Supported

Implementation-reality reviewer confirmed these work with existing code:
- Soft-stop / local-planning dialogue taxonomy is correctly expressed for non-paradox follow-ups.
- Campaign log emission pattern hosts the eight new event types trivially.
- Hard-stop machinery itself is sound — paradox only needs registration, not invention.
- Counter-bargain `Accept` / `Reject` / `Back Out` routes cleanly through existing `proposal_confirm` blocking mode.
