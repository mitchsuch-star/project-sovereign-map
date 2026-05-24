# SC-32 / Slice G2 — Product Decision Document

> **Purpose:** SC-32 is the last unlanded row in `SETTLEMENT_UI_CLEANUP_SPEC.md`. Per spec line 1254, every named agency surface must either **ship with payload/UI/voice/tests** or be **explicitly removed from player-facing scope**. This doc collects the 7 decisions you need to make before any G2-* sub-slice lands. When each row is decided, fold the outcome into the cleanup spec and the DWL ledger, then implementation can start.
>
> **Inputs:** Audit B (`docs/audits/SETTLEMENT_CLEANUP_AUDIT_2026_05_24.md` §B) + `SETTLEMENT_UI_CLEANUP_SPEC.md` §SC-32 + `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md:515-546` + `STATUS.md` DWL ledger.
>
> **Output:** A populated decision table that becomes input to a spec amendment (v0.32) folding the SHIP/CUT outcomes into `SETTLEMENT_UI_CLEANUP_SPEC.md` and the DWL ledger.

---

## Decision summary table (fill in)

| # | Decision | Default recommendation | Cost if SHIP | Cost if CUT | My choice |
|---|---|---|---|---|---|
| 1 | AI counterproposals (G2c) | **CUT** — player already has Request Revision | M (8-10 tests, new producer arm) | S (3 cut-evidence tests) | _____ |
| 2 | Wait-for-Enemy-Offer + Ask-for-Terms (G2d) | **CUT** — orphan flags without lifecycle | M (request_terms_state + cooldown + voice) | S (drop flags + display string) | _____ |
| 3 | Voluntary alignment clause (G2f) | **CUT** — forced_alliance covers most agency | M (clause schema + ratification path) | S (3 cut-evidence tests) | _____ |
| 4 | Ally petitions (G2b) — which types? | Ship 2 (request_open_settlement + warn_against_sellout); cut 4 | M (12-16 tests for 2 types) | n/a (decision is which to ship) | _____ |
| 5 | Conference / veto mechanics | **CUT** (spec line 1256 pre-commits) | L (new system) | None (already cut by default) | _____ |
| 6 | Same-war replace-confirm chooser (G2e) | **SHIP** — bounded and small | S (6-8 tests) | n/a (no orphan exists) | _____ |
| 7 | Petition trigger model | **Solicited** (player rejection triggers ally response) | n/a (design choice within G2b) | n/a | _____ |

If you accept defaults: 1 SHIP (G2e), 1 SHIP partial (G2b: 2 of 6 types), 4 CUT, 1 design-choice (petition trigger model). Total slice budget per spec line 839 is 30-42 tests; default plan lands ~22-30 tests, well within budget.

---

## Decision 1 — AI counterproposals (G2-Slice-G2c)

**Question:** When the AI side-leader rejects a player-staged settlement, should the AI automatically produce a *counter-offer* within N turns? Or does rejection simply emit `settlement_rejection_*` voice and end the round?

### Today's behavior
- Player offers settlement → AI runs acceptance formula → returns `accept` / `near_acceptable` / `reject` band.
- On reject, the popup renders blocker reasons and substitute CTAs (Seek Bilateral Peace, Seek Armistice).
- SC-5 commit 2 (May 17, 2026) shipped the **incoming-offer** lifecycle: AI side-leaders can autonomously *originate* settlement offers to the player. But a rejection-triggered AI counter does NOT exist.
- Player can already counter an AI-originated offer via `Request Revision` (opens counter editor seeded from the offered terms).

### SHIP — Build AI counterproposal arm
- Extension to `process_settlement_offer_phase` in `ai_diplomacy.py`: after a player offer is rejected, the AI generates a counter package within N turns (deterministic delta: lower harshness, swapped clauses, partial coverage variant).
- Reuses incoming-offer producer + mailbox + popup (zero new infrastructure).
- New `counterproposal_origin_offer_id` field on the offer for audit trail.
- Voice: `settlement_counterproposal_arrival_{talleyrand, castlereagh, hardenberg, metternich, einsiedel, chancery}` (6 new families).
- Tests: 8-10 (counter only fires after rejection, counter cooldown shares with regular offers, counter package differs deterministically, side-leader respected).
- Estimated cost: **Medium.**

### CUT — Settlement rejection produces no AI counter
- Spec records: "AI counterproposals removed from player-facing scope; rejection returns standard `settlement_rejection_*` voice families and no counter is produced. SC-5 / SC-30 `Request Revision` path remains the only counter-flow."
- Drop the unused `counterproposal_*` constants / TODOs from code.
- Tests: 3 cut-evidence (no counter offer is produced after rejection, `Request Revision` still works on incoming offers, spec text says CUT).
- Estimated cost: **Small.**

### Trade-offs
- **SHIP pro:** Closes a "diplomatic deadness" gap. After rejection, the AI feels like an actual negotiator with positions, not a yes/no machine.
- **SHIP con:** Adds complexity to the incoming-offer cooldown logic (counter shares one-active guard with regular offers). The deterministic-delta rule is the hardest design call — what makes a "good" counter without spawning a tuning rabbit-hole?
- **CUT pro:** Player can already counter via `Request Revision`. The asymmetry (player counters, AI doesn't) is defensible: the player drives diplomacy; the AI's role is to accept, reject, or originate.
- **CUT con:** Settlement rejection feels final in a way that historical diplomacy wasn't.

### Recommendation: **CUT.**
The asymmetry argument is strong. SC-5 commit 2 already gave the AI agency (originate offers); rejection is informationally rich (blocker reasons, top-2 components, substitute CTAs). Adding rejection-triggered counters risks turning settlement into a back-and-forth ping pong that the player can't see the end of. The Request Revision path on AI-originated offers is the symmetric primitive.

### Open questions
- If SHIP, how many turns does the AI have to counter? (1? 3?)
- If SHIP, can the counter be on a different `war_id` than the original? (Probably no — one-active per war.)

---

## Decision 2 — Wait-for-Enemy-Offer + Ask-for-Terms (G2-Slice-G2d)

**Question:** Two control flags exist in the popup payload today: `wait_for_enemy_offer_visible=False` and `ask_for_terms_visible=False`. They are emitted with `False` permanently (no `True` path exists in code). Should we ship a real lifecycle for each, or remove the flags?

### Today's behavior
- `settlement_preview.py:5429-5430` emits both flags as structural promises.
- `display_names.py:578` defines `wait_for_enemy_offer_unavailable` as defensive copy.
- No backend logic ever flips either to True. No Godot UI ever renders them. SC-30 DWL ledger Notes column says "their lifecycle would be a future SC-30b/c slice" — no SC-30b/c row exists.

### SHIP — Real Ask-for-Terms + Wait-for-Enemy-Offer lifecycles
- `Ask for terms`: new `request_terms_state[war_id]` dict on world. Click stages a request; AI side-leader returns terms within N turns via incoming-offer pipeline. Cooldown shared with regular offers.
- `Wait for Enemy Offer`: no-cost subscription. Notification fires when AI producer creates a matching offer within N turns. Distinct from passive waiting because it surfaces a UI promise.
- New voice families: `settlement_ask_for_terms_dispatched_talleyrand`, `settlement_wait_for_enemy_offer_subscribed_talleyrand`, refusal families for each cast diplomat.
- Tests invert the existing SC-30 spec-required tests (they currently pin absence; SHIP pins eligibility).
- Estimated cost: **Medium.**

### CUT — Remove the orphan flags entirely
- Spec amendment records: "Wait-for-Enemy-Offer and Ask-for-Terms removed from player-facing scope; the popup payload drops both `_visible=False` fields."
- Delete `wait_for_enemy_offer_visible` / `ask_for_terms_visible` emission from `settlement_preview.py:5429-5430`.
- Delete `wait_for_enemy_offer_unavailable` from `display_names.py:578`.
- Update SC-30 DWL ledger Notes column: "REMOVED in SC-32 / Slice G2-Slice-G2d — no request-terms lifecycle is part of player-facing scope."
- Existing 4 SC-30 hidden-control tests harden the absence (already authored).
- Estimated cost: **Small.**

### Trade-offs
- **SHIP pro:** `Ask for terms` is the player-side mirror of the AI's incoming-offer producer. It rounds out player agency: today the player can author or wait; SHIP lets the player solicit.
- **SHIP con:** Two more dialogue types, two more cooldowns, voice families to author. The Wait-for-Enemy-Offer affordance is especially thin — it's literally "subscribe to a notification you'd get anyway."
- **CUT pro:** Removes orphan promises. The two `_visible=False` flags exist today only to satisfy a structural symmetry that nothing reads. Removal makes the popup payload smaller and the spec contract honest.
- **CUT con:** `Ask for terms` was probably designed to give the player a way to *probe* enemy patience without committing. After CUT, the only way to test enemy receptiveness is to submit a draft and risk rejection.

### Recommendation: **CUT.**
The orphan flags are a perfect example of CLAUDE.md golden rule 9 ("any deferred work must name a concrete owner / landing"). They've been deferred for ~12 days without a real implementation plan. SC-5/SC-30 (incoming-offer) is a fully-shipped primitive; that's enough AI agency. If future product direction wants Ask-for-Terms, it can be reintroduced as a new spec with a real design — not resurrected from a defensive flag.

### Open questions
- If CUT, do we delete `INCOMING_OFFERS_DEFERRED` named flag at `settlement_preview.py:81` too? (Probably not — it's emergency-disable infrastructure for the shipped offer producer, not an orphan promise.)

---

## Decision 3 — Voluntary alignment clause (G2-Slice-G2f)

**Question:** Should the settlement editor support a `voluntary_alliance` clause — a player offering an alliance to an enemy participant as part of settlement (distinct from `forced_alliance`, which compels alliance from the losing side)?

### Today's behavior
- Settlement editor supports `forced_alliance` (Continental System toggle, +15 to +25 threat).
- Spec line 266 says: "any future voluntary alignment offer needs its own product decision and cannot reuse forced-alliance copy."
- No `voluntary_alliance` type exists in `SETTLEMENT_MVP_CLAUSE_TYPES` / `SETTLEMENT_DEPENDENCY_CLAUSE_TYPES` / `SETTLEMENT_RECURRING_GOLD_CLAUSE_TYPES`.

### SHIP — Add voluntary_alliance as a clause type
- New clause in `CLAUSE_CONTROL_SCHEMA`.
- New eligibility helper `evaluate_voluntary_alliance_eligibility` (only on losing side; only offering to enemy participants).
- Ratification path: creates Alliance state via existing `set_diplomatic_state(ALLIANCE)`, sets `alliance_origins[pair] = "voluntary"` (distinct from `"forced"`).
- Acceptance: negative harshness (an offered alliance helps the recipient), affecting `term_harshness_penalty` favorably.
- Voice: `settlement_voluntary_alliance_authored_talleyrand`, `_ratified_talleyrand`, foreign-court acceptance/rejection (5 cast + chancery).
- UI: editor clause control; review surface labels direction "Offered alliance" with `Conceded` badge.
- Tests: 10-12 (clause schema, distinct from forced_alliance, acceptance impact, no CS default, no +15 threat, save/load, no copy reuse).
- Estimated cost: **Medium.**

### CUT — Formally remove the affordance
- Spec amendment at line 266 records the cut: "Voluntary alignment offers removed from player-facing scope. The settlement editor remains forced_alliance-only for alliance authoring. Players who want to align with a peer outside settlement use the bilateral alliance system."
- Tests: 3 cut-evidence (no `voluntary_alliance` in clause schema, no validator path, spec records cut).
- Estimated cost: **Small.**

### Trade-offs
- **SHIP pro:** Closes a gameplay gap. A losing-side player who wants to *concede* alliance (e.g., to buy peace from a rising hegemon) has no current authoring path. Today they can only offer gold + territory + dependency.
- **SHIP con:** Largest clause-system delta in the SC-32 sub-slice plan. Touches validator, ratification, applied-clauses preview, voice, and the popup banner. Risk of subtle acceptance-formula tuning to make it actually accepted.
- **CUT pro:** Forced alliance + dependency clauses + bilateral alliance already cover most alliance-authoring needs. The bilateral path lets a player propose an alliance any time outside settlement.
- **CUT con:** "I'll join your alliance if you let me off easy" is a historically resonant losing-side play. CUT closes that off without a non-settlement alternative.

### Recommendation: **CUT.**
The pattern `forced_alliance` covers is the historical heavyweight — Continental System compulsion. `voluntary_alliance` is interesting design space but it's a new acceptance-formula input and a new UI control; in the SC-32 cleanup context, that's scope inflation. If product later wants this, it can land as a Slice H or its own spec with proper design treatment.

### Open questions
- If SHIP, does voluntary alliance trigger Continental System membership? (Almost certainly no — that's the forced version.)
- If SHIP, can voluntary alliance be offered to a participant who isn't the side-leader? (Probably no — alliances only with side-leaders.)

---

## Decision 4 — Ally petitions (G2-Slice-G2b) — which types to ship?

**Question:** `WSA_IMPLEMENTATION_PLAN.md:533-545` names 6 ally petition types from the original Slice G design. SC-32 inherits them. Which subset ships in G2b? Which are deferred or cut?

### The 6 types
| Type | What it does | Cost | Player payoff |
|---|---|---|---|
| `request_open_settlement` | Ally asks player to open Settlement on a specific war_id | S | High — closes the "ally wants peace but player ignores" gap |
| `request_consultation` | Ally asks player to share/discuss their draft | M | Medium — adds friction; useful if veto exists, less so if not |
| `request_reward_or_restoration` | Ally asks player to include a specific clause (e.g., return a region to the ally) | M | High — gives allies skin in the game |
| `warn_against_sellout` | Ally objects to a player-staged settlement that excludes them | S | High — adds pressure on betrayal-style settlements |
| `demand_bargain_honor` | Ally invokes a prior war-aim commitment from before settlement | L (touches commitments substrate) | High — connects settlement to the Memory & Pressure system |
| `request_redress_after_settlement` | Ally complains about an already-ratified settlement | L (touches cross-war reaction routing) | Medium — post-hoc friction |

### Recommendation: SHIP 2, CUT or DEFER 4
- **SHIP in G2b:** `request_open_settlement` (player gets a nudge with click-to-open) + `warn_against_sellout` (ally objects pre-ratification). Both are highest payoff per cost.
- **DEFER to a future Slice H:** `request_reward_or_restoration` + `demand_bargain_honor` — these are real gameplay but require the commitments substrate to be reliable and a clause-injection contract.
- **CUT in G2b:** `request_consultation` (adds friction without payoff in a no-veto world) + `request_redress_after_settlement` (cross-war reaction routing is a separate refactor).

### Trade-offs
- **Ship-2 pro:** Closes the "ally is silent" gap with minimum substrate. Both adopted types use the existing mailbox + dialogue pattern.
- **Ship-2 con:** Player who expects all 6 may notice the gap. Mitigation: spec line 266 calls out which types ship and which are explicitly deferred to a named future slice.
- **Ship-all-6 pro:** Closes the whole Slice G ally taxonomy at once.
- **Ship-all-6 con:** Doubles the test count (24-32 instead of 12-16), touches commitments and cross-war reaction code, increases regression risk.

### Recommendation: **SHIP 2, DEFER 2, CUT 2.** As above.

### Open questions
- If the DEFERRED 2 (request_reward_or_restoration, demand_bargain_honor) get assigned to "Slice H", they need a real DWL row created now per golden rule 9. Or this spec amendment cuts them too.

---

## Decision 5 — Conference / veto mechanics

**Question:** `SETTLEMENT_UI_CLEANUP_SPEC.md:1256` pre-commits this: "If conference or veto systems are not part of the product direction, the row records that removal and ensures no player-facing copy implies them." Confirm CUT?

### Recommendation: **Confirm CUT.**
- Conference (multi-party round-table negotiation) is a separate game system, not a UI cleanup. It needs its own spec.
- Veto (ally can block a specific clause) is a side-leader-authority violation per spec line 535: "the side leader still chooses."
- `DWL-DIP-CONFERENCE` is already SUPERSEDED in STATUS line 105.

Spec amendment: "Conference and veto mechanics are cut from SC-32 / Slice G2 scope. No player-facing copy implies conference or veto. If a Congress System is added later, it ships as its own spec with its own DWL row."

### Open questions
- None expected — this is a confirmation.

---

## Decision 6 — Same-war replace-confirm chooser (G2-Slice-G2e)

**Question:** `SETTLEMENT_UI_CLEANUP_SPEC.md:465`: "A future chooser/replace-confirm path belongs to SC-32 unless this spec is amended with its payload, voice, and tests." Should G2e ship it?

### Today's behavior
- Same-war different-scope restage returns `same_war_scope_collision` refusal code.
- The May 15, 2026 same-war off-editor smoke pass exercised the merge/preservation path, but not the replace-vs-keep chooser.

### SHIP — Add chooser
- New `settlement_scope_replace_confirm` dialogue type; payload mirrors `settlement_discard_confirm` shape.
- Two options: `Replace current draft`, `Keep current draft`. Outer-cancel = keep (defensive default).
- Click-time revalidation handles scope flips between staging and click.
- New Godot popup variant via `proposal_confirm_popup.gd`; reuses CanvasLayer 100 slot.
- Voice: `settlement_scope_replace_confirm_talleyrand` (1 new family).
- Tests: 6-8 (collision returns chooser, accept-replace clears old draft, accept-keep is no-op, click-time scope-flip handling, outer-cancel = keep, no clobber).
- Estimated cost: **Small.**

### CUT — Leave as today
- Spec amendment records: "Same-war different-scope replace-confirm chooser cut from player-facing scope. Restage with a different scope continues to return `same_war_scope_collision` and require the player to manually clear the existing draft before authoring a new scope."

### Trade-offs
- **SHIP:** Bounded, low-risk, single new popup. Closes a real UX rough edge (player has to remember which scope is staged).
- **CUT:** Adds nothing but does require the spec amendment to explicitly remove the line-465 promise. Player friction remains: they have to manually clear before restaging.

### Recommendation: **SHIP.**
The chooser is the smallest, lowest-risk demo of the SHIP path in SC-32. Doing it second (after G2a) demonstrates the slicing pattern and exercises the dialogue-confirm pattern that subsequent slices (G2b, G2c if shipped) will reuse.

### Open questions
- Should `Replace current draft` show a diff between old and new? (Probably no — that's a future polish item that needs its own design.)

---

## Decision 7 — Petition trigger model (within G2b)

**Question:** Do AI allies generate petitions unsolicited (on their own, periodically), or only in response to player actions (e.g., right after the player rejects an AI settlement offer)?

### Today's behavior
- No petitions exist. This is a design choice for G2b's implementation.

### Solicited model
- Allies only petition in response to a player action: player rejects offer → ally `warn_against_sellout` fires; player opens settlement on War A without their ally → ally `request_open_settlement` for War B fires.
- Pros: petitions never feel intrusive; they're always in response to something the player just did.
- Cons: less of a "diplomatic world has its own life" feel.

### Unsolicited model
- Allies generate petitions on a cooldown when their salience meets a threshold (e.g., they've been at war 5 turns with rising war exhaustion).
- Pros: world feels more agentive.
- Cons: petitions can pile up in the mailbox without the player having any context for why they appeared.

### Hybrid model
- Triggered by either action OR cooldown. Same producer; multiple gating paths.

### Recommendation: **Solicited.**
For the SC-32 cleanup scope, solicited is cheaper and player-friendly. Unsolicited can be a future polish if the diplomatic world feels too quiet.

### Open questions
- If solicited, what's the trigger taxonomy? (Player rejects settlement; player opens settlement excluding ally; player ratifies settlement excluding ally; ally takes territory loss in a battle...)

---

## Implementation order summary (after decisions locked)

Per Audit B's recommendation, with default choices:

1. **G2-Slice-G2a** — Doc-only cut/keep pass. Folds all 7 decisions above into `SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32 and the DWL ledger. Spec-named test `test_settlement_agency_landing_ledger_has_no_unowned_backlog_controls`.
2. **G2-Slice-G2e** — Same-war replace-confirm chooser (SHIP, small).
3. **G2-Slice-G2d** — Wait-for-Enemy-Offer + Ask-for-Terms (CUT per default). Removes two `_visible=False` flags + `display_names.py:578` row + SC-30 DWL Notes update.
4. **G2-Slice-G2b** — Ally petition substrate + 2 types (SHIP). Defers 2 to "Slice H", cuts 2.
5. **G2-Slice-G2c** — AI counterproposals (CUT per default). 3 cut-evidence tests + spec text.
6. **G2-Slice-G2f** — Voluntary alignment (CUT per default). 3 cut-evidence tests + spec text.

Default-path total: ~22-30 new tests across 6 sub-slices, of which 2 are SHIP slices (G2e, G2b) and 3 are CUT decisions (G2c, G2d, G2f) and 1 is a doc pass (G2a). Well under the 30-42 spec budget.

If you decide to SHIP more rows, the budget tightens but the slicing pattern is unchanged.

---

## Next step

Fill in the "My choice" column in the decision summary table at the top. When all 7 rows are decided, I (or you) can author the v0.32 spec amendment folding outcomes into `SETTLEMENT_UI_CLEANUP_SPEC.md` and the DWL ledger. Implementation slices land on master from there.
