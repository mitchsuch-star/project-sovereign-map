# Design Refinement

> **Design items and addons for evaluation.** This is the design-refinement backlog; execution routes through `docs/ROADMAP.md`'s current phase queue. (The old "work begins after `BUG_FIXES.md` is clear" gate cleared April 2026.)
>
> **Last Updated:** August 1, 2026 — **Live-Playthrough design items filed** (PT-D1..D4, from the played-world creative-audit re-measure; memo `docs/audits/AI_V_SWEEP_2026_08_01.md` §10 — PT-D1/D2/D4 share the PT-F6 enemy-phase slice, PT-D3 is copy-level). Prior: July 11, 2026 — **Estate Second Pass deferrals filed** (ESP-1..4, from the ES-7 second-pass design conversation; owner spec `ECONOMY_REVISIT_SPEC.md` §0.6.8). Prior: July 10, 2026 — **Wave 6 APPROVED IN FULL same day it was filed** (+2 gate additions: Dynamic Battle Naming, Literal Doctrine); the build-ready owner is **`docs/WAVE6_FUN_FACTOR_SPEC.md`** (12 slices, blessed default numbers recorded there). Wave 6 items came from `docs/audits/CREATIVE_AUDIT_2026_07_10.md`; live-evidence revisions recorded on R154, R59/R153 (now SUPERSEDED by W6-5), R129/R131/R132, R155/R156, R117 (absorbed into W6-9). Prior: July 2, 2026 present-tense pass. April 16, 2026 rescope context preserved below as history.

---

## CA9 Design Answers — ANSWERED August 9, 2026, BUILD NEXT SESSION

> **Record = `docs/audits/CA9_GATE_ANSWERS_2026_08_09.md` (authoritative).**
> The user answered all three and instructed: document now, build next session,
> then playtest everything including the 31 CA9 rows already landed. **Nothing
> is coded for these three.** GR9 owners, landings and completion definitions:

| Row | Decision | Owner / landing | Done when |
|---|---|---|---|
| **CA9-D1** peace terms | F14 STAYS; the cheese is the cheap SCORE, not the recommendation. Battles + decisive are ±50 of ±100 with zero territory (EU4 caps battles at 25%); no term reads the war's AGE. Recommended: war-age penalty on acceptance FIRST, battle/territory re-weight after the playtest | `diplomacy.calculate_war_score` + `settlement_scoring`; next session | A short war cannot be settled for cash; a genuinely won war still has an exit (watch the TERRITORY arm); acceptance breakdown NAMES the new term; `BASELINE_SERIES` re-recorded with flip-experiment attribution |
| **CA9-D2** attack confirm popup | Arm only when band is `unfavorable` (not `even`) AND the marshal is `cautious`. Preview still prints honest numbers on every attack; only the BLOCK narrows | `combat_executor._execute_attack` muster gate; next session | An aggressive marshal charges bad odds unasked (in character); a cautious one asks; one predicate decides both the popup and the copy; CR-5's own bad-odds gate untouched |
| **CA9-D3** grievances + popups | A REVISIT slice, NOT a TTL on N4. Audit every popup producer, queue slot, blocking class and retirement path, then fix | New slice; next session. Starting list: N4 (P1), N21, N8, IGR-X7 drain family, the 11-slot PopupQueue priority order, the per-surface stash-and-raise discipline | Every producer has a retirement path; nothing blocks a channel indefinitely; the queue order is justified rather than accreted |

**Then ONE playtest** covering the three new slices AND the 31 rows landed
August 9 — which also discharges the owed visual sign-off on `Supply: Unknown`
(region panel + map tooltip) and the per-court fog line.

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Player Feedback (Wave 3 remaining) | 7 | Open — R129/R128 → 8.EVAL triage; R131/R132/R17d-f → queue item 6 (8.EVAL) |
| Nation Rivalry System (EU4-inspired) | 1 | Superseded by Memory and Pressure v2.4.3 (COMPLETE); dynamic-agenda residual → queue item 5 |
| Territorial Promises (Wave 3) | 1 | ✅ LANDED April 2026 as war bargains (`WAR_BARGAIN_SPEC.md`) |
| War System Overhaul (EU4-inspired) | 4 | ✅ LANDED — war_objectives / power cap / forced_alliance / liberation live in code |
| AI Diplomacy Improvements | 3 | N1 verified live; A4 historical note; A3 residual rides queue item 5 (8.EVAL) |
| Gold Sink Options (B4) | 1 | Re-pointed → `docs/ECONOMY_REVISIT_SPEC.md` EC-2 |
| Wave 4 — New Features | 19 | **✅ DISPOSED at 8.EVAL July 16, 2026** (`docs/audits/EVAL_8_2026_07_16.md` §2): R117/R59/R153/R154 already handled; R26 → EC-5, R161 → EC-8, R158 → CR-7, R162 stays gated behind the Nation-Agendas gate; R22/R25/R27/R35/R118/R127/R133 → the Pre-EA Diplomacy & Flavor Content Menu row; R32/power_score/R24/R33/R36 DROPPED with reasons |
| Wave 5 — Game Review Findings | 8 | **✅ DISPOSED at 8.EVAL July 16, 2026** — routed items verified: R155/R157 residuals ride the promoted Nation-Agendas core + landed voice work; R152 residual folds into the closed queue-item-6 record; R158 → `docs/COMMAND_ROBUSTNESS_SPEC.md` CR-7 |
| Jealousy System | 1 | Separate design gate; Marshal Content Pass MC-3 now an effective prerequisite |
| **Wave 6 — Creative Capstone (July 10, 2026)** | 14 | **✅ APPROVED IN FULL July 10** (6 expansions + 6 escalations + 2 gate additions: Dynamic Battle Naming, Literal Doctrine); owner = `WAVE6_FUN_FACTOR_SPEC.md` (12 build slices W6-0..W6-11) |
| **Estate Second Pass deferrals (July 11, 2026)** | 4 | **ESP-1 + ESP-2 + ESP-4 ✅ LANDED July 11, 2026 with the Jealousy v3.2 build** (ESP-4 folded per its own row's fold-in clause; record = `JEALOUSY_SPEC.md` §0.3/§0.4, tests `test_estate_riders_esp.py`); ESP-3 respect-by-treaty → diplomacy gate (unchanged) |
| **Total** | **63** | |

---

## Creative Audit — Design Items (August 4, 2026 — **GATES HELD August 7, 2026**)

> Source: `docs/audits/CREATIVE_AUDIT_2026_08_04.md` (17-turn live France/1805 campaign at
> master `e450b02`, 80-agent find→refute fleet). These are **design calls that need a gate** —
> the defects from the same audit are routed to `BUG_FIXES.md` §Creative Audit.
> Per **GR9** each row names an owner; none may be built inside an audit.
>
> **⚖ CLOSE-OUT August 7, 2026 (user-delegated; gate record =
> `CREATIVE_AUDIT_2026_08_04.md` §10, authoritative): D2, D4 and D6 were HELD and their
> rows BUILT the same session** (landing record `BUG_FIXES.md` §Creative Audit close-out
> block; tests `test_ca8_gate_closeout_2026_08_07.py`, 46). **D1 and D5 transfer to the
> re-planned roadmap's ECON BALANCE position** (the pre-build EC-P3 gate+build the user
> ordered Aug 7 — "econ is still unbalanced"); **D3 attaches to the Marshal Voice Tier 1
> slot's gate** (the next marshal-content gate, now also pre-build).

| id | the finding | owner row | the question the gate must answer |
|---|---|---|---|
| **CA8-D1** | The conquest-free gold sink is **13 building slots for the whole game** (`region.py:107-113` × France's 1 capital / 4 major_city / 7 city; `BUILDING_TYPES` tops out at 400g) → lifetime sink 3,250–5,200g, **under two turns of net income**. Measured: treasury 671g → **29,496g** (44×) in 13 turns, with **88% of everything France earned unspendable** | **row EC-P3** (existing econ backlog owner) | What does gold buy after turn 6? Landing slice must define completion. The plunder prompt quoting a flat 600g for every 150-income city is downstream of this, not a separate row |
| ~~**CA8-D2**~~ ✅ **HELD + BUILT Aug 7, 2026** (§10.1: leverage keys to the WAR — `calculate_side_war_score` / `sum_stored_side_score` / `get_side_war_score_for`, three consumers; a cession requires `war_score < -20` STRICTLY) | Settlement leverage keys to a **pair**, not the war. `compute_side_pressure_score` already knew Austria sat at **43** while the war-status row and the offer producer both read the raw France↔Britain **0**. CA8-27 is the outgoing mirror: the peace generator concedes territory whenever `relation < -50`, i.e. in every war | **Pre-EA Victory & Objectives Pass** (existing open gate — war score → terms → ending is exactly its business) | Should the counterparty's leverage key to the war the player is actually fighting, and should a cession require a losing war score rather than hostile relations? Both have blessed-number consequences on acceptance and offer generation |
| ~~**CA8-D3**~~ ✅ **HELD + BUILT Aug 8, 2026 at the position-9 slot** (user-delegated; **gate record = `JEALOUSY_SPEC.md` §0.5, authoritative**): both questions YES — Q1 rival MEMORY in `find_jealousy_target` (a man his envy already fired on is preferred while still above; no history = one-rung-up byte-identical; `JEALOUSY_RIVAL_MEMORY` flip flag; GR5 through the single source) + Q2 the §6 confrontation latch widened to once per (pair, escalation level), keys `A|B@Ln` in the existing seen-list, legacy bare keys = level-0 seen, bounded 4/pair/campaign, level-register body clauses; M1–M7 + `BASELINE_SERIES` byte-identical without re-record; `test_ca8_d3_rival_permanence.py` (19) | The rival is not a person. `find_jealousy_target` (`jealousy.py:268`) recomputes from a rolling 8-turn window with no bias from `jealousy_history`; Murat's rival changed **four times** in twelve turns. One petition per pair per campaign, ever (`jealousy.py:558-563`) — one fired, on turn 1, and was re-served fifteen times | ~~new row, next marshal-content gate~~ **CLOSED** | Should a marshal's grievance object have permanence, and should a petition re-fire when the escalation level rises? **YES + YES** |
| ~~**CA8-D4**~~ ✅ **HELD + bounded build LANDED Aug 7, 2026** (§10.4: three non-fear frames — arithmetic/interest, opportunity, history/law; a third variant in all 24 hegemony banks; full roster authoring across the other four reasons stays DEF-1's) | `hegemony_pressure` monoculture, rotated by `(turn + len(name)) % len(variants)`. **Row corrected Aug 4, 2026 (CA8 sweep 4) — three of its own facts were wrong, and the correction changes what the gate is for.** It is **19 named speakers + 5 registers over 24 banks = 48 lines, of which 38 are bespoke**, not "8 courts" — the authored surface is twice what the row credited and it is good. It is pinned **once**, on one bank (`test_w6_incoming_voice.py:118`), not twice: a third variant injected into all 24 banks runs the FULL suite at `1 failed / 16,280 passed`, so **all 19 bespoke banks grow with zero pin flips** and the "growing the banks is a conscious flip" cost model was false. And the **re-key is cosmetic churn — do NOT build it**: with two variants the key's image is `{0,1}`, so any turn-independent term is a phase shift, and the 19 courts hold DISJOINT banks so `len(nation_name)` decorrelates nothing. The measurement that settles the row is neither lexical nor structural: **72% of all diplomat lines composed in a 40-turn campaign are exact repeats** (Ottoman: 12 asks, 2 distinct lines), so bank SIZE is the only lever. Two gate-free defects were split out and FIXED in sweep 4 (Hardenberg's first line was the generic register line with `{nation}` pre-filled; a named envoy lost his authored attribution — `Araujo, measuring the room:` → `Araujo:` — whenever his reason had no bespoke bank, which is 16 of 19 courts on `agenda_pursuit`) | **DEF-1 Roster Voices** for the authoring; the 6-turn cooldown numbers (`ai_diplomacy.py:49-50`) are W6-10's, blessed, and carry AI-behaviour exposure — not DEF-1's to fold in | **Question rewritten.** The old one (*"Does the enemy phase get its own voice register?"*) aims at `enemy_phase_dialog.gd`, which is CA8-6/CA8-21's surface, not `compose_incoming_diplomat_line`. The open question is: **what else may `hegemony_pressure` sound like besides fear?** 85% of the 48 lines say "France is big"; writing 24 more in that frame spends the budget and measurably changes nothing. Exactly one line already escapes it — Castlereagh's *"London does not negotiate from fear; it negotiates from arithmetic"* — and it is the model |
| **CA8-D5** (→ the pre-build **ECON BALANCE position**, Aug 7, 2026 re-plan; CA8-18 landed Aug 4) | The threat bar sat at **91–97 for all 12 turns**, so position 3.5's new `military_establishment` term (`coalition.py:729-762`) was **unmeasurable in play** — it fired into a bar already at its ceiling | **row EC-P3**, now scheduled as the pre-build econ position | Does anything new need to be measurable on a bar that boots near its ceiling? |
| ~~**CA8-D6**~~ ✅ **HELD + BUILT Aug 7, 2026** (§10.2: the briefing MAY lead with a victory — `enemy_eliminated` 93 / `capital_stormed` 92 / `victory_won` 73 / `region_taken` 68; at equal scale the wound still leads) | **The morning dispatch has no headline class for a French success.** `HEADLINE_WEIGHTS` = 15 classes raised from 17 `_add()` sites; every one is a wound, an opportunity ranked below every wound *by comment* (`dispatch.py:71-73`: *"an opportunity never outranks a wound"*), or another power's business. There is no `region_taken`, `battle_won`, `capital_stormed` or `enemy_eliminated`. **14 of 14 headlines this campaign were misfortunes.** On the turn France stormed Vienna **and** Austria was eliminated, the lead was `stand more men over what Bohemia can feed`. The good news exists, but only in a notification bar where **8 of 20** entries are the same `dotation_erosion` nag — and the best-written sentence of the campaign (*"Austria has seized Carniola, the estate that funded Marshal Ney's honor. He will not forget it, Sire."*) is a notification title | **new row, next narration gate** — pairs with the Aug-3 enemy-phase-as-theater dissent that moved the composition slice to position 3 | Should the briefing be able to lead with a victory, and at what weight against a wound? The decision to revisit is that comment. Note this is the standing explanation for why narration scores 6 while event generation scores 8 — the events are good and the editor only publishes bad news |

**Not deferred, closed at filing:** CA8-20's player half is **XR-4**; its AI half belongs beside
IGR-X4 / IGR-X9 at **EC-P3**'s next econ tuning gate and needs no new row.

---

## Live-Playthrough — Design Items (August 1, 2026 — ✅ ALL FOUR LANDED same day, second session)

From the played-world creative-audit re-measure (memo = `docs/audits/AI_V_SWEEP_2026_08_01.md`
§10). **All four landed August 1, 2026 (second session) under the user's delegated grant,
alongside PT-F1/PT-F6** (whose struck rows in `BUG_FIXES.md` §Live-Playthrough carry their
records). Struck rows below carry these landings.

| ID | Item | Why it matters | Landing / completion |
|---|---|---|---|
| ~~PT-D1~~ ✅ **LANDED Aug 1, 2026** | ~~**Muster one-voice odds.** The muster header states joint-force odds while the personality line in the SAME message states solo odds.~~ | Both frames now labelled. | **Landed exactly as specified:** the header names the committed joint figure ("Ney (24,000; 41,000 with the muster committed) … the balance of force looks favorable" — the figure the CO-2 verdict is actually priced on, `_format_muster_lines`), and the cautious solo line says "at unfavorable odds **alone**" whenever `committed_attacker > 0` (`combat.py` — the −10% stays priced on the solo ratio, which is the blessed mechanic; the copy names its frame). Legacy solo copy byte-stable. Tests: `test_enemy_phase_presentation.py` §TestMusterOneVoiceOdds (5). |
| ~~PT-D2~~ ✅ **LANDED Aug 1, 2026** | ~~**Diorama contingent taxonomy.** Soult (REFUSED to march) rendered `failed_arrive`; Murat (promised, failed his roll) absent entirely.~~ | Refusal, failed roll and silent drop are different dramas. | **Landed as specified:** statuses {refused, failed_arrive, out_of_reach} — refusal keyed on the Session-61a trust-dock taxonomy (`literal_personality`/`eyes_on_a_crown` → `refused`; `low_score`/`fate_intervened` keep `failed_arrive`); **muster-promise parity** via `_inject_muster_promises` (the WILL JOIN rows ride into `build_battle_diorama`; a promised name the resolve ladder silently dropped shelves as `out_of_reach`); `_cap_side` + the two `.gd` predicates read the absence family as a set. Spec vocabulary updated (`BATTLE_DIORAMA_SPEC.md` §7). Tests: `test_battle_diorama.py` §TestContingentTaxonomyPTD2 (5) + 2 flipped pins. |
| ~~PT-D3~~ ✅ **LANDED Aug 1, 2026** | ~~**Letter-book label coherence.** Digest rows titled "Gift of Friendship" whose own clauses read "Proposal: Open Borders Agreement".~~ | Header/body mismatch erodes trust in the letter-book. | **Landed:** the row title follows the terms-derived `proposal_type_display` the payload already carries (falls back to the context label), so the title always matches the lead clause; the STABLE `proposal_type` stays untouched for the batching predicate (the smuggling guard test still pins it). Tests: `test_igr_f_envoy_digest.py` +2. |
| ~~PT-D4~~ ✅ **LANDED Aug 1, 2026** | ~~**Move-chain presentation.** One corps chaining 3–4 moves per enemy phase reads as teleportation.~~ | The loudest contributor to "enemy phase as theater: 5.5". | **Landed as specified:** `main._collapse_enemy_move_chains` — after the fog filter, chains of 3+ hop-continuous moves per marshal collapse into ONE `forced_march` entry (stages named = the destinations today's bullets already disclosed; ORIGIN named only at FULL intel — the one name the old bullets never leaked; attrition summed; conquest events preserved so a recapture chain still lists each fall under the one march line; a marshal's own non-move action or a hop discontinuity breaks the chain; other marshals' interleaved entries don't). Presentation only — runs at the view layer, moves untouched; totals/summary invariants kept. `enemy_phase_dialog.gd` gained the render arm. Tests: `test_enemy_phase_presentation.py` §TestMoveChainCollapse (8). |

---

## In-Game Review — Design Items (July 25, 2026)

From the live NA-6c/6d + AI-3r cross-element pass. Memo:
`docs/audits/INGAME_REVIEW_2026_07_25.md`. Correctness defects went to `BUG_FIXES.md`
§ In-Game Review July 25; these three are design calls, not bugs.

**All three are owned by row IGR, `docs/INGAME_REVIEW_FIXES_SPEC.md` (v1.0, ✅ GATE BLESSED
July 25, 2026 — gate record = spec §5, authoritative):** IGR-D1 is DECIDED at
`PLUNDER_INCOME_MULTIPLIER = 4` (blessed, in-band tunable, with a falsifiable acceptance test and a
recorded dissent that the stability-vs-authority re-cut is the better design if the number fails
twice); IGR-D3 is DECIDED as the `create_client`-carries split. Mapping: IGR-D1 → **IGR-E** (gate Q4) ·
IGR-D2 → **IGR-F** (gate-free) · IGR-D3 → **IGR-D** (gate Q2 — the same question as `BUG_FIXES.md`
IGR-3). **✅ ALL THREE HAVE LANDED** — IGR-D July 25, IGR-F July 26, IGR-E July 26 — and the rows
below are struck accordingly. *(Spec §3 requires routed rows to be struck on landing; IGR-D2 and
IGR-D3 had been left un-struck by their own sessions and are closed here too.)*

| ID | Item | Why it matters | Landing |
|---|---|---|---|
| ~~**IGR-D1**~~ | ~~**Plunder is economically irrelevant.** Plundering Nassau yielded **87 gold** against 3,085/turn income and a 5,177g treasury. Secure (stability 25) is strictly correct in every situation I met, so the post-capture choice has no tension.~~ **✅ LANDED July 26, 2026 as IGR-E** (landing record `INGAME_REVIEW_FIXES_SPEC.md` §2 IGR-E, commits `c7e30b9` + `88e2707`). | ~~A per-conquest decision the game stops to ask about should cost the player something to answer.~~ **Done both ways the row asked for:** priced (`PLUNDER_INCOME_MULTIPLIER` 1.75 → **4.0**; Nassau 87 → 200g, the median province 262 → 600g) **and made legible** — no surface stated what Plunder would pay before the choice; now the modal button, the terminal sentence and both refusal restatements quote it, from the same expression that pays it. ⚠ The gate's worked example ("Nassau ~450–750g") is WRONG and is corrected in the landing record: 450–750 is the MEDIAN province, Nassau is the map minimum. | ✅ LANDED — `tests/test_igr_e_plunder_prompt.py` (30). **⚠ THE RECORDED DISSENT LIVES ON:** option (b), the stability-vs-authority re-cut, is arguably the better *design*; **if the falsifiable acceptance test fails at TWO different multipliers, re-open at (b) rather than tuning a third time. Attempts used: ONE of two (×4, PASSED).** |
| ~~**IGR-D2**~~ ✅ **LANDED July 26 as IGR-F** | **Minor-court envoy spam.** Turns 2–5 delivered ~3–5 near-identical Open Borders / Non-Aggression proposals per turn from minors, each a blocking modal that interrupts a command already in flight (the typed order echoes, then its result is deferred behind the popup). The voices are genuinely good — Reis Efendi, Einsiedel, Consalvi all distinct — but volume flattens them. | The per-nation voice work is some of the best writing in the game and it is being spent on a queue the player learns to click through. | Batch into a single "the small courts write" digest with per-row accept/decline; owner = the next diplomacy polish slice |
| ~~**IGR-D3**~~ ✅ **LANDED July 25 as IGR-D** | **Should identity clauses survive the bilateral substitution?** (mirror of `BUG_FIXES.md` IGR-3.) The blocked-settlement path offers "Make peace with X only", promises the drafted terms carry, and drops `create_client` / vassalage / liberation by design. | This is the difference between the NA-6 carve being a headline feature and a feature most players will never complete. | Needs a user gate — carry identity clauses, or steer back to the joint route when one is drafted |

---

## Econ War-Coupling — Deferred Riders (July 17, 2026)

> From the EC-W research pass + build (gate record `docs/audits/ECON_WAR_COUPLING_RESEARCH_2026_07_17.md` §5;
> the build landed EC-W1..W5 the same session). These riders were considered and
> consciously deferred with owners — not silent scope.

| ID | Pri | Item | Design shape | Owner / landing |
|----|-----|------|--------------|-----------------|
| ~~EWC-D1~~ ✅ **BUILT Aug 7, 2026 at the Econ Balance gate** (EB-5a "Requisitions of War", `ECON_BALANCE_GATE_2026_08_07.md` §3; `REQUISITION_RATE = 0.25` × base income to the STRONGEST disruptor, its own positive "Requisitions" Net component, GR5 both directions — boot: Austria +37 from Mack@Swabia. The snowball objection was structurally dissolved by EB-1: extraction lands in a chest taxed at the war rate while the war lasts. `test_econ_balance_eb.py::TestRequisitions`) | P2 | **Occupier-side extraction** — EC-W1 suspends a disrupted province's income to its owner but credits the invader nothing ("consumed in place"). The historical rider: a fraction flows to the occupier's treasury ("la guerre doit nourrir la guerre") | One constant (e.g. 30% of base income) + a positive "Contributions" ledger component on the invader's side, riding the same `get_disrupted_regions` substrate; deliberately NOT in v1 because crediting the winner accelerates the offensive snowball the pass was correcting | ~~Next econ tuning gate~~ ✅ landed |
| EWC-D2 | P2 | **Casualty→manpower-pool drain** — battle deaths never touch the pools (root-cause 5), so a nation bled white re-raises its army from an untouched reserve | Battle casualties drain the loser's (or both) infantry/cavalry pools at some fraction; needs an AI-impact study first (P1 recruit + P1.75 commission rungs must keep functioning at low pools) | Pre-EA Balance Pass; test = pool depletion + AI-rung survival |
| EWC-D3 | P3 | **Captured-marshal ransom** — Bernadotte sat captured with zero economic consequence; historically ransom/exchange negotiations carried real prices | A ransom demand event on the W6-7 capture substrate (petition/notification channel), priced to the captor's leverage | Future diplomacy/drama gate |
| PTJ-D1 | P3 | **Pooled allied dead bill the primary nations' pensions** (PT-J review round [P3-5], Aug 14 2026) — the campaign ledger's casualty accrual reads the battle producers' POOLED side totals (the CA8-1 whole-army figure incl. allied reinforcements' dead), attributed to the two primary nations, so France's `pensions_of_the_fallen` term can bill Bavarian dead and the blood differential skews with them. Figure shape pre-existing; PT-J2/J3 make it economically visible for the first time | Thread `casualty_distribution` (already computed for the diorama) through `record_campaign_casualties` so each participant nation's ledger row takes its own dead; completion = a coordinated battle's ledger rows sum per-nation to the distribution, pinned both sides | **EC-2 pass 2** (the econ gate that owns ES-4/ES-7b); test lands with the slice |

**Cut with reasons (memo §5):** loans/inflation spiral (anti-sandbox), a separate battle-devastation slice (battles already write `war_damage`), home-front stability drag keyed on war score (double-dips EC-W2 illegibly), flat `WE × rate` drain (Austria's +18 boot margin — superseded by the treasury-fraction form), recurring-rails indemnity restructuring (lump + existing recurring presets suffice).

---

## Sweep-5 — Design Items (July 16, 2026)

> From the Combat Overhaul Sweep-5 12-component review (memo
> `docs/audits/SWEEP_5_2026_07_16.md` §5). CONFIRMED, adversarially verified,
> pre-existing (not Sweep-5 regressions). Correctness-tier siblings live in
> `BUG_FIXES.md` §Sweep-5.
>
> **Dispositions set at 8.EVAL July 16, 2026 (`docs/audits/EVAL_8_2026_07_16.md`):
> S5-D1 → ✅ **BLESSED + LANDED July 16, 2026** via the CR-6 mini-gate (record
> `COMMAND_ROBUSTNESS_SPEC.md` §7) · S5-D2 → KEEP 8.5 Batch Q · S5-D3 → DEFER to the next refactoring
> slice (row in §8.EVAL Dispositions below; VS-4 single-sourcing is the priority
> element).**

| ID | Pri | Item | Design shape | Owner / landing |
|----|-----|------|--------------|-----------------|
| S5-D1 | ✅ **LANDED** | **Bare "attack" bypasses every gate** — with no marshal named, `_execute_general_attack` auto-picks a never-addressed marshal into a real battle, skipping CR-2 clarification, the W6-4 muster gate (no `command` kwarg at the resolve call), AND the objection gate (needs `marshal_name`). Long-standing WAD (pre-CR-2), but by post-CR-2/W6-4 standards the most ambiguous lethal order gets the fewest gates; four independent Sweep-5 reviews converged on the same fix | **✅ BLESSED + BUILT July 16, 2026 via the CR-6 mini-gate.** Resolve-and-rewrite at the dispatch seam (`CombatExecutor.resolve_auto_attack` in `executor.execute`): (a) >1 commandable marshal in enemy contact → `build_contact_attack_clarification`; single-contact keeps the instant pick; (b) rewrite to a named `attack` so the W6-4 muster gate arms; (c) the auto-picked marshal flows through the objection block; E-CA-4 subsumed. GR5 carve-out for AI/strategic/autonomous. NO pins flipped — gating is at the dispatch seam, so `test_auto_assign_attack.py` stays green; new pins in `test_cr6_bare_attack_gating.py`. | ✅ LANDED — gate record `COMMAND_ROBUSTNESS_SPEC.md` §7; `test_cr6_bare_attack_gating.py` (12) |
| ~~S5-D2~~ ✅ **LANDED July 16, 2026** (Batch Q Chunk 1 — `strategic_executor.py`:604, pinned `test_batch_q_fixes.py`) | P2 | **PF-8 issuance-time passability honesty** — "march to Copenhagen" printed a route through neutral Prussia/Sweden; the closed-border stall fires only at the border hop, so the player spends 2 AP + a turn to learn what the game knew at issuance | Issuance rider naming the closed crossings ("via closed Prussian territory — requires open borders or war") when the formed path fails `_region_passable_for`; no pin conflicts | PF-8 follow-on row; lands with the next parser/UX batch |
| S5-D3 | P3 | **Architecture hygiene batch** — duplicated `_edit_distance_le2` (validation.py local vs parser helper, deliberate to avoid a leaf→layer import), the byte-mirrored VS-4 withholding predicate (combat_executor ↔ muster preview), leaf→layer lazy imports (authority→diplomacy) | Consolidation pass: a shared leaf util module for edit-distance; single-source the VS-4 predicate; document-or-lift the lazy imports | Architecture hygiene row; batch with the next refactoring slice |

---

## Vassal Playtest — Design Items (July 14, 2026)

> Routed (not bugs) from the July 14 vassal playtest + 14-agent verification. Bug fixes landed the same session (`docs/BUG_FIXES.md` §Vassal Playtest Findings); memo `docs/audits/VASSAL_PLAYTEST_2026_07_14.md`. These are intent/legibility/enhancement calls, not defects.

| ID | Pri | Item | Detail | Owner / gate |
|----|-----|------|--------|--------------|
| VP-D1 | P3 | ✅ **WIRED July 16, 2026 (Vassal Depth Slice 0)** — Garrison-as-a-real-loyalty lever | Wired **presence-based, flat +2** (`GARRISON_LOYALTY_BONUS`, single-source `lord_garrison_present` in `vassal.py`): a lord-nation corps standing in the vassal capital OR a lord-CONTROLLED capital holding real `garrison_strength`; the vassal's own boot garrison never counts. The authored +5..+8 ladder was deliberately DISCARDED (at −2 drift it made the loyalty economy decorative). Full value in the VS-R spiral band (a deed, not a cheap one-shot). Healthy `recovery_hint` re-advertises it; `/debug/vassal_loyalty` mirrors the same predicate. Tests: `test_vassal_slice0_substrate.py` + 4 reworked garrison test sites. | ✅ done (Slice 0, commit `1082382`) |
| VP-D2 | P3 | **Muster odds band omits the defender baseline edge** | The muster "odds"/"balance of force" band (`objection_v2.inferred_attack_odds_band`) folds terrain + fort but NOT the always-on +20% `defender_bonus`, defender DEFENSE skill, ±10% variance, or the 2d6 — so "favorable" reflects force balance, not the casualty exchange (playtest: a "favorable" attack lost 8,819 to inflict 469 into mountains vs a cautious defender). F2 reworded the label to "the balance of force looks …"; the deeper fix (fold the defender baseline into the ratio, and/or a wider band) touches the CR-5 inferred-attack gate threshold → needs re-tuning + a combat sweep, not a silent change. | Combat legibility pass / next combat sweep (escalate the threshold) |
| VP-D3 | P3 | **Committed defensive reinforcers valued by offensive potential** | `_committed_reinforcement_strength` uniformly uses `get_attack_modifier` (combat_executor.py), incl. for the committed DEFENDER — so a cautious/defensive corps reinforcing a defense is systematically undervalued (folds the defensive-stance ×0.90 + attack personality mods). GR5-symmetric (same fn both sides), so a modeling inconsistency, not an exploit — possibly intended as one generic "combat contribution" metric. **Verify intent first.** | Combat review — confirm intent before any change |
| VP-D4 | trivial | **grip recomputed per enemy in the courting loop** | `attempt_vassal_courting` calls `get_imperial_grip(world, player)` once per enemy-nation call each turn (each re-scans homeland + war scores). `process_vassal_loyalty` already memoizes grip per lord; the courting path doesn't. Bounded by N enemies (not a per-region inner loop) — a GR8 cache-per-turn nit, deliberately NOT micro-optimized (staleness risk on a pure derived read outweighs the negligible gain). | Perf nit — fix only if a scale tripwire flags it |

> Routed from **Sweep 4** (July 15, 2026 — `docs/audits/SWEEP_4_2026_07_15.md`). Vassals cleared 6.0→6.5 (target MET, at the floor); these are the CONFIRMED ceiling items the review named. VP-D1 above is the P0 restated by Sweep 4. **Two fixed same day (July 15):** the "grant X **more** autonomy" parse shrug (`_apply_fuzzy_matching` was matching the direction word "more"→"Murat"; now skips marshal-matching for vassal-family actions, `parser.py`) and **VP-D5 below**.

| ID | Pri | Item | Detail | Owner / gate |
|----|-----|------|--------|--------------|
| VP-D5 | P2 | ✅ **FIXED July 15, 2026 — Autonomy change now surfaces its permanent tribute trade-off** | `change_vassal_autonomy` now shows the tribute DELTA directionally: up = "Tribute rate: 75% → 50% (a permanent income cut)", down = "50% → 75% (you collect more of their income)". The player following the "grant autonomy" recovery hint is told the recurring cost at the decision point. Tests in `test_playtest_fixes_2026_07_14.py::TestAutonomyTributeLegibility`. | ✅ done (copy fix, `vassal.py`) |
| VP-D6 | P2 | ✅ **LANDED July 16, 2026 (Vassal Depth Slice 5)** — Enemy-AI grip-awareness | **P1.6 vassal shore-up rung** in `_pick_admin_action` (between P1.5 dotation and P1.75 commission): triggers when the AI lord's weakest satellite slips under 40 loyalty OR its `get_imperial_grip` spirals (<30); arms in escalating desperation — invest (1 nation-DP + 200g) → **VS-3 land grant** (loyalty <30, via the same lord-neutral `list_grantable_regions`) → autonomy-up (loyalty <25, structured `new_level`). All through the shared executor at player prices (Slice-0 substrate); fees in domain functions; **"subsidize" deliberately dropped** (not an action — same reason the recovery hint stopped naming it). Latent at the 1805 boot; live the moment an AI acquires a vassal. The offensive piece (bribe payer) is VS-6's `attempt_vassal_bribe` in the diplomatic phase. Tests: `test_vpd6_ai_vassal_shore_up.py` (12). | ✅ done (Slice 5) |
| VP-D7 | P3 | **Dual authority-derivation tables risk future divergence** | `get_imperial_grip` (VS-R, graded 75/40/25/15, `authority.py:414`) and `get_authority_proxy` (jealousy, bucketed 75/50/25) are parallel derivations of the same "how strong is the court" idea. Both anchor the shared 30 breakpoint today, so there is **no present divergence** — but two tables of the same concept will drift under future tuning. Reconcile to one graded source, or document the intentional split. Tech-debt, not a defect. | Vassal/jealousy tidy — reconcile before either is retuned |
| VP-D8 | P3 | **AI-authored settlement dependency clauses (VS-5 parity scope-down)** | VS-5 (July 16, 2026) shipped accept-side pricing parity for `vassalage`/`subjugation`/`liberation`/`vassal_transfer` (the AI prices them via the shared scoring seams), but the AI never AUTHORS a dependency clause: `ai_diplomacy.py` offers are peace+gold only and there are no AI↔AI common-peace settlements. An AI demanding the player's vassalage (or claiming the player's satellite at the table) is a NEW fantasy needing its own design gate — victory/defeat framing, player-consent UX, and WPS-B cap policy all open. | Needs its own gate; candidate owner = 8.EVAL war-LLM/diplomacy triage |
| VP-D9 | P3 | **Player-facing defection-bribe verb (VS-6 symmetry)** | VS-6 (July 16, 2026) built `attempt_vassal_bribe` lord-neutral, so the PLAYER bribing an enemy lord's satellite works at the domain layer — but it is structurally latent (no enemy lord holds a satellite at the 1805 boot, and no AI creates one today; VP-D8 or a settlement `vassalage` imposed BY the AI would change that). When enemy satellites become reachable, the player needs a typed/wizard verb ("bribe Saxony away from Prussia"), cost preview copy, and the parser/corpus wiring — a small slice riding the existing helper. | Vassal-depth follow-on once enemy lords hold satellites; pairs with VP-D6/VP-D8 |

---

## Post-Fix Routing Update

The old bug-phase gate is now cleared. Sessions 1-7 in `docs/BUG_FIXES.md` are complete, and the diplomacy contract is now stable enough to plan legitimacy and strategy work on top of it.

### Live foundations now documented

- `PL-27`, `PL-34`, and `PL-32` are complete.
- The Envoys inbox / mailbox panel is live, including `GET /mailbox`, `POST /mailbox/activate`, stable mailbox identity, and `dialogue_manager.get_mailbox_count()` as the badge source.
- `world.diplomatic_queue` is gone; the shipped follow-up refactor replaced the old cross-turn mailbox persistence with current-turn envoy items (`Not Now`, same-turn reopen, end-turn lapse).
- Proposal / clause display ownership is centralized in backend formatters, so popup payloads and reopen flows use the same labels.
- Session 6 contract refactors are complete: `/command` starts from `build_base_response()`, remaining diplomacy popups use typed response paths, and `main.gd` routes modals through the registry/dispatcher layer.

### Historical spec queue (April 16, 2026 rescope; superseded by April 28 status)

This queue records the April 16 diplomacy rescope. It is no longer the live implementation queue. Current status is tracked in `docs/STATUS.md`; items 1-4 below are ALL LANDED — BPH, WPS, and WB landed, and Ally Participation + Common Peace LANDED as the Imperial Settlement system, complete through Slice G1 (July 2, 2026, commit `1a9da53`).

1. `Memory and Pressure` (renamed from `Reliability + Commitments` April 16)
   **✅ COMPLETE — Memory and Pressure v2.4.3, all slices landed (see `docs/RELIABILITY_IMPLEMENTATION_PLAN.md`). The remaining-work list and the "~68-74 tests, ~3 sessions remaining" estimate below are historical v2.2-era text.**
   Substrate (betrayal memory, concern witness scope, hard-reject posture, episode_id, structured warnings) is **shipped**. Remaining work this phase: seed `nation_concerns` (4 authored pairs), wire `direct_concern_mod` + `concern_conflict_mod` + graduated `bilateral_betrayal_mod` into acceptance, wire third-party anger on ratification, redemption tick (`actor_honored_turns` +3 / 5 honored turns at OPEN_BORDERS+), rename `alliance_paradox` → `commitment_paradox`, ship C3-lite presentation pass (spotlight tier, split-voice render, named-diplomat resolution per Voice Bible). See `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.2, `RELIABILITY_IMPLEMENTATION_PLAN.md`, `COMMITMENTS_PRESENTATION_SPEC.md` v0.4 (C3-lite). ~68-74 tests, ~3 sessions remaining (Slice C split into Godot-surfaces + tests/mock-prose sessions; v2.2 renames rivalry→concern for balance-of-power scale architecture + adds auto-downgrade rule + France-Austria concern pair + Make Amends verb).
   **Scale note (v2.2):** `nation_concerns` is named for the target dynamic balance-of-power architecture (see spec §7.7). v0.1 ships static seeded values; dynamic concern evaluation is `Nation Agendas` scope (queue item 5).
2. `Bilateral Peace Hardening`
   **✅ LANDED — shipped per `docs/BILATERAL_PEACE_HARDENING_SPEC.md`.**
   Tighten separate peace / bilateral peace preview, explicit term ownership, promise-breach warnings, and peace-treaty legibility before any ally-aware settlement system exists. **Needs dedicated spec.**
3. `War Purpose + Score Semantics`
   **✅ LANDED — shipped per `docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`; `war_objectives`, forced alliance, and liberation are live in code.**
   Collapse war objectives, ticking war score, vassalage power cap, forced alliance, and liberation into one war-goal / score-legibility spec. **Needs dedicated spec.**
3.5. `War Bargains` — `docs/WAR_BARGAIN_SPEC.md`
   **✅ LANDED April 2026 — the `war_bargain` mechanic shipped per the spec.**
   The named-enemy bilateral promise mechanic split out of `Reliability + Commitments` v1.0 in the April 16 rescope. Adds `war_bargain` clause type, lifecycle (active / triggered / fulfilled / void / breached), `join_opportunity` ally-entry contract, counter-bargains, `war_entry_score`, Bargain Review surface, and the WB-D presentation extension (bargain spotlights, scope-branched copy, response routes). **Depends on items 1-3.** Implementable as a single Peace Deals phase precursor before item 4. ~80-90 tests.
4. `Ally Participation + Common Peace`
   **✅ LANDED — shipped as the Imperial Settlement system, complete through Slice G1 (July 2, 2026, commit `1a9da53`); see `docs/SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32 and `docs/STATUS.md`.**
   Build contribution, consultation, ally beneficiaries, and common peace as a separate wartime-flow system. **Current state:** the dedicated spec and implementation plan now own the active Slice A handoff; this item is no longer merely a later-direction draft.
5. `Nation Agendas + Motive Legibility`
   **✅ DESIGN GATE HELD July 17, 2026 — the agenda core is SPECCED and owned: `docs/NATION_AGENDAS_SPEC.md` (§0 gate record; authored decks + dynamic activation, full coupling in pass 1, R162 owned as slice NA-5). R123/R124/A3/R155-residual/R156 all consume through that spec's §5 seams; this queue item is CLOSED as a routing row.**
   **✅ RE-SCOPED + PROMOTED at 8.EVAL (July 16, 2026 — record `docs/audits/EVAL_8_2026_07_16.md` §1).** The motive-LEGIBILITY half is LANDED piecemeal (W6-9 war room + assess chip, W6-10 register bank + ask variety, UI-6 surfaces, DEF-1 voices; verified with file:line evidence in the gate record) and the `nation_concerns`-to-dynamic sub-item is OBSOLETE (zero code presence — superseded by the live hegemony/bloc-share machinery). **What survives is the AGENDA core — `R123` (econ-strategy triggers), `R124` (isolation/alliance-splitting plays), `A3` (enemy-AI war-vs-diplomacy choice), the `R155` residual (personality-driven timing/persistence/target choice), `R156` (diplomacy strategically optional) — and it is PROMOTED to the Phase 8.5 design-gate centerpiece** (8.5 = Events, Goals & National Identity; the agenda system IS the "Goals & National Identity" diplomacy pillar). Needs its user design gate at 8.5; propose-then-build.
6. `Talleyrand Desk + Explanation Layer`
   **✅ CLOSED at 8.EVAL (July 16, 2026 — DROPPED as landed; record `EVAL_8_2026_07_16.md` §1).** ~6 of the 7 collapsed items shipped piecemeal: R131 cooldown pre-check (`diplomatic_executor.py:270-286`), R132 vassal transparency (W6-3/W6-9 + the UI-6 ledger trend), R17d DP breakdown, R17e trend arrows, R17f mission projection (all in `diplomatic_ledger.py`), R157 voice depth (PL-25 + C3-lite + W6-10 + DEF-1). The sole live residual **R159 (screens should teach mechanics) is RE-HOMED to the Pre-EA Onboarding & Teaching Pass row (§8.EVAL Dispositions below)** — GR9 satisfied, no unowned promise survives.
7. `Economic Diplomacy`
   **RE-POINTED — owner: `docs/ECONOMY_REVISIT_SPEC.md` EC-8 (economic diplomacy, incl. R161). Original text kept as historical context.**
   Collapse `R161` plus diplomacy-facing B4 candidates into one reciprocal-trade / subsidy / pressure spec.

**Diplo-wide ledger rows `DWL-DIP-E7` + `DWL-DIP-METTERNICH`:** ~~their "settlement final gate closes" trigger goes LIVE when the user confirms the Gate 4 visual half~~ **✅ BOTH DECIDED at 8.EVAL July 16, 2026 and ✅ BOTH BUILT + LANDED July 16, 2026 (Batch Q Chunk 2 — see STATUS top entry): E7 = authority-banded defiance floor** — `diplomatic_defiance._defiance_floor_for_authority`: 5% at authority ≥70 (single source `STRONG_EMPEROR_DEFIANCE_FLOOR`), easing to the ordinary 2% below; the whole sabotage arc is reachable again; `DIPLOMACY_SPEC.md §3a` trust-term drift removed in the same slice (`test_session6_diplomacy.py` re-anchored). **Metternich = BUILT small** — `coalition.record_schemer_peace_rejection` at the reject seam plants a once-per-rejection, 5-turn-expiring war-pressure marker (`+2`/marker, cap `+4`) summed in `process_coalition_turn`; anti-stacking (dict keyed by nation); new serialized `WorldState.schemer_rejection_pressure`; `DIPLOMACY_SPEC.md §5c` updated to the landed mechanic; `test_batch_q_metternich_dd8.py` (12). BOTH ROWS CLOSED.

### 8.EVAL Dispositions (July 16, 2026) — the pre-EA rows this gate created

> Gate record = `docs/audits/EVAL_8_2026_07_16.md` (authoritative; §4 = this list's charter). Each row is a GR9 home: owner = the named pass, landing = that pass's build session, completion = the referenced item's own definition.

| Row | Contents | Completion definition |
|-----|----------|----------------------|
| **Pre-EA Balance Pass** | DW-2 war-score-credit calibration (bilateral ×0.3 vs settlement ×0.65 — one constant + dependent-pin retune); co-homed with the STATUS:537 Europe-balance items | Bilateral acceptance credits war dominance consistently with the settlement scorer's felt weight; G4F-9 ladder re-verified |
| **Pre-EA AI Correctness Pass** | AUD-f `_evaluate_marshal` deferred-commit refactor (threat-responder claims + serialized `ai_refortify_cooldown` writes during candidate evaluation) | Evaluation is side-effect-free; M1–M7 harness + `test_ai_audit_2026_07.py` green |
| **Pre-EA AI Depth Pass** | MC-V-4 cautious force-husbanding (design gate FIRST — must coexist with the anti-stagnation machinery); the ROADMAP 8c trio (AI-AI wars, AI vassalization, cross-AI threat) stays at its own 8c row | Gate-blessed design lands with liveness metrics held; **if no pass materializes pre-EA, drop cleanly — no player promise outstanding** |
| **Pre-EA Dialogue Robustness** | S5-4 queue-cap overflow-to-mailbox (push + preempt together) | No dialogue silently dropped at cap; docstring already fixed in Batch Q |
| **Pre-EA Onboarding & Teaching Pass** | R159 (screens teach mechanics) — companion to `TUTORIAL_SCRIPT.md` | Each core screen names the mechanic it displays; new-player path verified |
| **Pre-EA Diplomacy Polish Pass** | AUD-d M3 territory-sweetener rebuild (reuse VS-3 worth-scaling + the BPH `territory_cede` seam; delete the 2 dead `NATION_DESIRES` territory rows either way) | AI counters can cede real regions with correct direction; ratification live-verified |
| **Pre-EA Diplomacy & Flavor Content Menu** | R22 marriage alliances · R25 vassal personality events · R27 secret treaties · R35 player counter-offers on bilateral incoming offers · R118 acceptance preview · R127 nation-specific advisory intel · R133 point-of-no-return popup · Gneisenau Staff Work | Per-item R-row definitions; user picks the menu at the pass's gate |
| **Next refactoring slice** | S5-D3 hygiene batch (edit-distance triplication, VS-4 predicate single-sourcing = priority, lazy-import documentation, AUD-a's dead `QUEUE_MAX_SIZE`) | Byte-identical behavior, existing VS-4/muster pins green |

**DROPPED at 8.EVAL (explicit strikes, reasons in the gate record §1–§2):** DR-6/queue-item-6 as chartered (landed) · AUD-a envoy flood (fixed twice over, measured 4→7) · AUD-e behavior half (shipped sort canonized; Enemy AI 8.0 held — docs reconciled instead) · arch-plan #23 fixed nation order (canonized; harness-load-bearing) · R32 peace conferences · numeric `power_score` · R24 signing ceremonies · R33 puppet rulers · R36 personal summits · the battle/war narration toggle (narration measured 8.0).

### Still lower priority

- `R162: AI Ultimatums to Player` is no longer blocked by the old attention contract, but it should still wait until the commitment and agenda specs above are written. It adds interruption surface before the core diplomacy has enough political weight. **(July 2, 2026: R162 stays gated behind queue items 5-6, which are owned by the 8.EVAL evaluation gate.)**
- Presentation-only diplomacy polish remains downstream of the grouped spec work above, except for the narrow post-commitments presentation pass proposed in `docs/COMMITMENTS_PRESENTATION_SPEC.md`.

---

## Secondary Post-Fix Items

These refine existing systems and are still implementation-ready later, but they should not displace the grouped spec tracks above.

### R119: Nations Remember Betrayal — **COVERED**
- **Category:** Player Feedback
- **Status:** **Fully covered** by the Memory and Pressure substrate (shipped April 15-16, 2026). `world.betrayal_history` with severity-scaled decay, per-episode strike caps, bilateral `bilateral_betrayal_mod` in acceptance formula, hard-reject posture at 3 active strikes, witness scoping, Make Amends active-redemption verb (v2.1). The original R119 design (flat -10/-20/-30 with half-witness, 20-turn redemption) was superseded by the spec's graded model. No further work needed on R119 itself.
- **Files:** `diplomacy.py`

### R131: Cooldown Pre-Check Warning
- **Category:** Player Feedback
- **Summary:** Warn player of proposal cooldowns before opening negotiation dialogue.
- **Details:** Pre-check cooldown before dialogue opens. Show remaining turns + Talleyrand message.
- **Files:** `diplomatic_executor.py`

### R129: Override Feedback in Dispatch
- **Category:** Player Feedback
- **Owner (July 2, 2026):** 8.EVAL triage.
- **Summary:** Add feedback when diplomatic override actions succeed/fail.
- **Details:** Success: +2 trust + dispatch note. Failure: +1 concern boost + dispatch note. Fix timing bug at diplomatic_defiance.py:741.
- **Files:** `diplomatic_defiance.py`, `dispatch.py`

### R128: Sabotage Consequence Feedback
- **Category:** Player Feedback
- **Owner (July 2, 2026):** 8.EVAL triage.
- **Summary:** Track and report sabotage outcomes with Talleyrand feedback.
- **Details:** Track in `world.sabotage_history`. Dispatch note next turn. Trust +3 if Talleyrand was correct.
- **Files:** `diplomatic_defiance.py`, `dispatch.py`

### R132: Vassal Loyalty Transparency — **80/20 LANDED July 10, 2026 (W6-3 `reason` field + W6-9 war-room trend/cause block)**
- **Category:** Player Feedback
- **Summary:** Real-time vassal loyalty deltas and trend tracking.
- **Details:** Lower warning threshold to 30. Show delta when |change| >= 2. Store `prev_loyalty`. Trend arrow in ledger. **Landed shape:** `vassal_loyalty` events carry the dominant-cause `reason` at emission (W6-3 §5.4); the W6-9 assessment renders loyalty + drift trend + the most recent cause per vassal. The residual (ledger trend arrow, threshold tune) stays queue-item-6 (8.EVAL).
- **Files:** `dispatch.py`, `vassal.py`, `diplomatic_ledger.py`, `diplomatic_advisory.py`

### R17d: DP Breakdown Display
- **Category:** QoL
- **Summary:** Show DP source/cost components in ledger.
- **Files:** `diplomatic_ledger.py`

### R17e: Relation Trend Arrows
- **Category:** QoL
- **Summary:** 3-turn history showing direction of relationships in ledger.
- **Files:** `diplomatic_ledger.py`

### R17f: Mission Progress Projection
- **Category:** QoL
- **Summary:** Estimated completion turn for active missions.
- **Files:** `diplomatic_ledger.py`

### Memory and Pressure interaction notes (updated for v2.4.3)

These are not new items — they annotate existing items whose scope or interaction changes now that Memory and Pressure v2.4.3 is the active spec.

- **R162 (AI Ultimatums to Player):** Hard-reject posture (3+ bilateral strikes) still informs ultimatum behavior, but the surrounding political pressure is now hegemony-driven rather than rivalry-seeded. A nation at hard-reject posture toward France is both more likely to issue ultimatums (anger-driven) and less likely to accept French counter-offers. Wire this interaction when R162 ships.
- **R123 / R124 (Economic Strategy & Diplomatic Isolation AI):** These collapse into queue item 5 (Nation Agendas + Motive Legibility). AI should now read `hegemony_target_mod`, `bilateral_betrayal_mod`, and (when DG-4 lands) `grievance_modifier` plus bloc geometry to drive subsidy offers, alliance-breaking proposals, and isolation strategy. Static `nation_rivalries` / `rival_conflict_mod` are no longer the data source.
- **R17d (DP Breakdown Display):** Show the live Memory and Pressure acceptance components individually rather than reviving the old composite term: `hegemony_target_mod`, `bilateral_betrayal_mod`, `reliability_modifier`, and later `grievance_modifier` / `composite_floor` when DG-4 is active.
- **R155 / R157 (AI Proposal Voice / Talleyrand Voice Depth):** The C3-lite presentation pass (`COMMITMENTS_PRESENTATION_SPEC.md` v0.5.1) now commits named-diplomat CRITICAL / NORMAL notices, the paradox popup, Balance-of-Europe threshold beats, and Make Amends acknowledgments per `DIPLOMAT_VOICE_BIBLE.md`. The broader scope (personality-driven proposal timing, AI-initiated proposal voice, deep Talleyrand commentary across all diplomacy) remains open and routes to queue items 5-6.

---

## Focused Audit Validation (Apr 10, 2026)

The focused attention / AI diplomacy audit tightened which diplomacy legitimacy items are already justified, which ones need bug-fix prerequisites, and which old notes are now stale.

### Already justified by current evidence

- **R160: Nation Rivalry System** — confirmed as the highest-leverage legitimacy upgrade. Current diplomacy still lets France drift toward broad friendship without enough forced political choice. *(Since SUPERSEDED by Memory and Pressure v2.4.3 — see the R160 row below.)*
- **R155: AI Proposal Personality Voice** — needs to expand from flavor text into motive legibility. The audit confirmed that AI personality currently changes a few constants, but not enough of proposal timing, persistence, target choice, or player-facing explanation.
- **R156: Diplomacy Strategic Optionality** — confirmed. Proposals happen, but they do not create enough meaningful branching until rivalry / exclusion pressure exists.

### Prerequisites now satisfied (Apr 12)

- **R160 / R155 / R156** are no longer blocked by the old diplomacy contract prerequisites. `PL-27`, `PL-34`, and `PL-32` are closed, and the Envoys inbox / current-turn offer lifetime / typed popup-response foundations are live.
- **R162: AI Ultimatums to Player** no longer waits on the mailbox/recovery transport fix, but it remains intentionally sequenced after the stronger commitment and agenda specs.
- Presentation-only diplomacy polish should still follow the grouped spec work above, not precede it.

### Current legitimacy stack

- Completed foundation: Envoys inbox / same-turn offer lifetime / backend-owned display labels / typed response routing.
- `Reliability + Commitments`: make alliances politically costly, promises meaningful, and betrayal cumulative.
- `Bilateral Peace Hardening`: make separate peace and bilateral settlement review legible before multilateral settlement exists.
- `War Purpose + Score Semantics`: make wars resolve toward recognizable political outcomes instead of generic pressure alone.
- `Ally Participation + Common Peace`: active wartime settlement layer; implementation starts from `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice A.
- `Nation Agendas + Motive Legibility`: make AI motives and strategic branching legible to the player.

---

## Needs Design Gate

### R160: Nation Rivalry System (EU4-Inspired) — **SUPERSEDED BY Memory and Pressure v2.4.3**
- **Category:** Diplomacy — Balance
- **Status:** Static rivalry seed and the old rivalry-specific acceptance terms were dropped in the v2.4 hegemony refactor. The live political-pressure layer is now `hegemony_target_mod` + `bilateral_betrayal_mod`, with `grievance_modifier` joining later via DG-4. The original R160 design is therefore superseded by `RELIABILITY_COMMITMENTS_SPEC.md` v2.4.3 rather than partially awaiting completion.
- **Remaining (unshipped):** any future dynamic rivalry / agenda system must grow out of bloc geometry, betrayal memory, grievance persistence, and AI agendas rather than restoring `nation_rivalries` / `direct_rivalry_mod` / `rival_conflict_mod`. That work still belongs to queue item 5 (`Nation Agendas + Motive Legibility`).
- **Files:** `diplomacy.py`, `ai_diplomacy.py`, `diplomatic_ledger.py`, `world_state.py`

### R151: Territorial Promise Clauses — **LANDED via WAR_BARGAIN_SPEC (April 2026)**
- **Category:** Diplomacy Feature
- **Disposition (July 2, 2026):** ✅ LANDED — the `war_bargain` mechanic shipped April 2026; the "scheduled in the Peace Deals phase" text below is historical.
- **Status:** The broader concept (France makes named-enemy promises to allies, tracking obligation, breach/fulfillment, betrayal consequences) is now fully designed as the `war_bargain` clause type in `docs/WAR_BARGAIN_SPEC.md`. The spec covers creation, validation, lifecycle, fulfillment, breach/void, war-entry integration, and the Bargain Review surface. Scheduled in the Peace Deals phase after `Bilateral Peace Hardening` + `War Purpose + Score Semantics` (queue items 2-3.5).
- **Files:** `diplomacy.py`, `ai_diplomacy.py`, `diplomatic_executor.py`

### Jealousy System (v3.1 spec)
- **Category:** Marshal Feature
- **Summary:** Glory Ladder targeting, personality expressions, escalation, confrontation popups.
- **Details:** Full spec at `docs/JEALOUSY_SPEC.md`. Core design settled. Top of ladder: +1 all core stats while #1. Defeats cost glory. DO NOT CODE WITHOUT USER APPROVAL.
- **Sequencing note July 2, 2026:** the Marshal Content Pass (`docs/MARSHAL_CONTENT_PASS_SPEC.md`, MC-3 relationship authoring) is effectively a prerequisite — the shipped 21-marshal roster has zero authored relationships; a v3.2 addendum must re-derive scenario impact/tuning against that roster before the gate.

---

## War System Overhaul (EU4-Inspired — Design Gate) — **✅ LANDED**

**Disposition (July 2, 2026):** this entire section LANDED via the War Purpose + Score Semantics work (`docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`) — `world.war_objectives` ticking score, the vassalage power cap, the `forced_alliance` clause type, and the liberation mechanic are all live in code. The text below is preserved as historical design intent.

Full design spec in `docs/archive/PLAYTEST_AUDIT_2026_03_29.md` lines 215-722. Addresses core balance problem: defensive play is overwhelmingly superior because no ticking score incentivizes holding territory over time.

### War Objectives + Ticking War Score (5th Component)
- **Summary:** Player-chosen war goals at war declaration (Conquest, Subjugation, Forced Alliance) and auto-assigned goals (Defense, Liberation). Each goal has a ticking target region — holding it accumulates war score over time (±25 cap).
- **Ticking rates:** Conquest +2/turn (enemy capital), Subjugation +3/turn (enemy capital, power cap gated), Forced Alliance +2/turn (enemy capital), Defense +1/turn (any enemy region), Liberation +1/turn per vassal capital.
- **New field:** `world.war_objectives: Dict[str, Dict]` — diplo_key to `{type, target, accumulated}`
- **Files:** `diplomacy.py` (calculate_war_score 5th component), `world_state.py` (field + per-turn accumulation), `war_status.py` + `war_detail_popup.gd` (display), `diplomatic_executor.py` (war goal selection dialogue)
- **Est. sessions:** 2-3, ~20 tests

### Vassalage Power Cap
- **Summary:** Gate vassalization on National Power ratio: target must be ≤ 50% of player's power. Power = sum of base income of controlled regions + partial vassal contribution.
- **Why:** Prevents France from vassalizing Austria at war_score 80 — only small nations should be vassalizable.
- **Files:** `vassal.py`, `diplomacy.py`, `diplomatic_ledger.py`, `diplomatic_templates.py`
- **Est. sessions:** 1, ~10 tests

### Forced Alliance Clause Type
- **Summary:** New clause type — war goal forces enemy into ALLIANCE + Continental System on peace. Follows vassalage pattern for wiring (acceptance values, harshness, keywords, display names, state mapping).
- **Historical:** Napoleon's primary war objective (Austerlitz, Tilsit, Jena).
- **Files:** `diplomacy.py`, `diplomatic_dialogue.py`, `diplomatic_executor.py` (4 state maps), `display_names.py`, `diplomatic_templates.py`, `world_state.py`
- **Est. sessions:** 1-2, ~10 tests

### Liberation Mechanic
- **Summary:** Coalition war goal — liberating vassals. On peace: `release_vassal()` + auto `DEFENSIVE_ALLIANCE` with liberator.
- **Files:** `world_state.py` (_ratify_treaty), `vassal.py` (release reason)
- **Est. sessions:** 1, ~6 tests

---

## AI Diplomacy Improvements (Ready — Small Fixes)

### N1: AI Preemptive Alliance Against Rising Threat
- **Source:** `docs/archive/DIPLOMACY_DESIGN_FIXES.md` lines 69-130
- **Summary:** Trigger 5 in AI-AI diplomatic evaluation. When threat > 40, nations with negative relations toward France form defensive alliances with each other. Creates diplomatic web before coalitions.
- **Audit status (Apr 10):** Already implemented in `ai_diplomacy.py` Trigger 5. Keep as verified reference, not as a pending refinement unless the behavior needs expansion.
- **Files:** `ai_diplomacy.py`
- **Est. tests:** ~7

### A3: AI War Exhaustion Integration
- **Source:** `docs/archive/DIPLOMACY_DESIGN_FIXES.md` lines 55-61
- **Disposition (July 2, 2026):** the proposal-side integration is LANDED in `ai_diplomacy.py`; the residual (the `enemy_ai.py` war-vs-diplomacy choice) rides queue item 5 (`Nation Agendas + Motive Legibility`), per the Memory and Pressure interaction note above.
- **Summary:** Proposal-side war exhaustion integration is already partially landed in `ai_diplomacy.py` (`effective_p1_threshold`, `effective_stalemate_turns`). Remaining work, if any, is broader war-exhaustion integration in `enemy_ai.py` and diplomacy-vs-war choice, so this item now needs re-scope rather than blind implementation.
- **Files:** `ai_diplomacy.py`, `enemy_ai.py`
- **Est. tests:** ~4

### A4: AI Harsh Peace Gold Formula Rebalance
- **Source:** `docs/archive/DIPLOMACY_DESIGN_FIXES.md` lines 47-53
- **Summary:** Historical note only: the focused audit confirmed the live formula already uses `max(200, int(war_score * 5 * gold_mult))` in `ai_diplomacy.py`. Keep this item only if further rebalance is desired.
- **Files:** `ai_diplomacy.py`
- **Est. tests:** ~2

---

## Wave 4 — Decide Gate (Per-Item Approval)

These are new feature designs. Each needs individual approval before implementation.

**July 2, 2026:** per-item user approval is still required. Items already re-pointed above have new owners: R26 → `docs/ECONOMY_REVISIT_SPEC.md` EC-5 (Continental System); R161 → `ECONOMY_REVISIT_SPEC.md` EC-8; R162 → gated behind queue items 5-6 (8.EVAL).

| ID | Item | Summary |
|----|------|---------|
| R22 | Marriage Alliances | Dynastic bonds: +20 rel, block war 5 turns, 3 DP |
| R32 | Peace Conferences | Multi-nation negotiations, 3 DP, +15 acceptance |
| R117 | Advisory Actionability — **✅ LANDED July 10, 2026 via W6-9** (the war-room assessment's ONE recommendation ends in an executable option: `execute_suggestion` / `expand_options`) | Advisory ends with executable options |
| R123 | Economic Strategy AI (P9) | Gold > 600 triggers subsidy offers, trade pressure |
| R124 | Diplomatic Isolation AI (P10) | Split enemy alliances with generous terms |
| R133 | Point of No Return Event | One-time Talleyrand popup at threat 40 |
| R28 | Talleyrand Voice Bank | 5-8 variants per situation type |
| R127 | Nation-Specific Intelligence | Per-nation personality lines in advisory |
| R24 | Treaty Signing Ceremonies | Talleyrand ceremony text on ratification |
| R25 | Vassal Personality Events | 3-4 random loyalty-gated events per game |
| R26 | Continental System Buff | Backend exists, needs player command + creative rebalance |
| R27 | Secret Treaties | Hidden treaties, 10%/turn discovery chance |
| R33 | Puppet Rulers | Named rulers with personality, events |
| R35 | Player Counter-Offer Terms | Player specifies clauses (Godot popup) |
| R36 | Personal Summits | Face-to-face meetings, +15 acceptance 3 turns |
| R59 | ~~Literal Personality Triggers~~ | **SUPERSEDED by W6-5 The Literal Doctrine (user call, July 10, 2026):** literal marshals never object BY DESIGN — the fantasy is "generals who do what they're ordered." Engagement = order echo + fidelity beat + precision captions + muster-preview warnings (`WAVE6_FUN_FACTOR_SPEC.md` §7; triggers converted to a doctrine comment in `personality.py`, pinned by `test_w6_literal_doctrine.py`). |
| R118 | Enhanced Acceptance Preview | Top 3 positive/negative components + Talleyrand hints |
| R161 | One-Time Trade | Trade gold, manpower, territory directly without ultimatum or state change |
| R162 | AI Ultimatums to Player | Building Blocks: AI uses same ultimatum system as player. Needs popup, response flow, AI decision tree |

---

### R161: One-Time Trade (Expanded)
- **Category:** Diplomacy Feature
- **Owner (July 2, 2026):** re-pointed to `docs/ECONOMY_REVISIT_SPEC.md` EC-8 (economic diplomacy, alongside queue item 7). Original design text kept as historical context.
- **Summary:** Voluntary, consensual resource exchange between nations — no state change, no coercion. The "carrot" complement to ultimatums (the "stick").
- **Details:** Player proposes a trade (gold, manpower, territory) to any nation at OPEN_BORDERS or better. Both sides give and receive. Uses existing conversational diplomacy flow with `generate_trade_terms()`. Acceptance via full formula. No threat increase, no relation penalty — pure commerce.
- **Building Blocks principle:** Reuses `_ratify_treaty` clause processing, `calculate_acceptance()`, dialogue enrichment, splash damage (none for trades). Same executor path as proposals but with `type: "trade"` and no state transition.
- **Distinction from ultimatums:** Trades are voluntary (both sides benefit), ultimatums are coercive (one-sided demands with diplomatic cost).
- **Gates needed:** Trade balance formula (what's fair?), AI trade evaluation, frequency limits.
- **Files:** `diplomatic_executor.py`, `diplomatic_templates.py`, `diplomacy.py` (new base disposition for trade), `diplomatic_dialogue.py`
- **Est. sessions:** 1-2, ~8 tests

### R162: AI Ultimatums to Player
- **Category:** AI Diplomacy — Building Blocks
- **Status (July 17, 2026):** ✅ **OWNED — slice NA-5 of `docs/NATION_AGENDAS_SPEC.md` (§8 answers the gate questions: trigger rung, agenda-target terms, rejection → bounded expiring coalition-pressure marker not a free war, mailbox transport + dtype whitelist).** Built after NA-0..NA-3 land and are verified live; no further gate. The details below are historical context.
- **Status (July 2, 2026):** stays gated behind queue items 5-6 (Nation Agendas + Talleyrand Desk), which are owned by the 8.EVAL evaluation gate.
- **Summary:** AI nations issue ultimatums to the player using the same ultimatum system the player uses. Building Blocks principle (§23): same systems, different input values.
- **Details:** AI evaluates ultimatum opportunity in `enemy_ai.py` decision tree (new P-trigger). Conditions: military superiority over player in a region, low relations, not in coalition with player. Generates terms via `generate_ultimatum_terms()` (same function player uses). Delivered as popup with [Accept][Reject] options. Rejection gives AI casus belli. Same splash damage, threat (reduces player threat if AI is aggressor), and cooldown mechanics.
- **Building Blocks reuse:** `generate_ultimatum_terms()`, `calculate_acceptance()` (inverted — player is target), `_ratify_treaty` clause processing, splash damage formula, global cooldown (separate AI cooldown counter).
- **Gates needed:** AI trigger conditions (when is ultimatum better than war declaration?), player response popup design, threat direction (does AI ultimatum reduce or increase player threat?).
- **Files:** `enemy_ai.py` (new P-trigger), `diplomatic_executor.py` (AI ultimatum handler), `main.gd` (new popup), `ai_diplomacy.py`
- **Est. sessions:** 2-3, ~12 tests

### National Power Tiers (Great Power / Secondary / Minor) — Design Gate
- **SUPERSEDED — April 17, 2026.** Canonical `power_tier` is now defined in `docs/SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy". Under the canonical definition, `power_tier` is **authored scenario data** with values `major / secondary / minor` and is **never recomputed at runtime**. The dynamic numeric-tier model below is superseded and must not be implemented. If a numeric strength-derived signal is needed for AI threat weighting, coalition calculations, or dispatch priority, it lives in a separate `power_score` field that does not overwrite `power_tier`. The original text is preserved below as historical design intent.
- **Residual disposition (July 2, 2026):** the tier model stays SUPERSEDED — Phase 0's authored `power_tier` shipped with the real-map cutover. The optional numeric `power_score` idea: evaluate at the 8.EVAL gate, else drop.
- **Category:** Diplomacy + War — Balance + Immersion
- **Summary:** Dynamic numeric power tiers (`great_power / secondary_power / minor_power`) calculated from controlled regions, income, military strength, and partial vassal contribution. Affects acceptance formula (great powers resist vassalization), coalition formation (great powers lead coalitions, minor powers join), war settlement (consultation rights scale with tier), and AI threat assessment (great powers escalate coalition faster).
- **Origin:** Conceptual three-tier model exists in `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §8.3. Data fields (`nation_power_scores`, `nation_power_tiers`) listed as deferred in `RELIABILITY_COMMITMENTS_SPEC.md` §12.3.
- **Design decision from WAR_SETTLEMENT spec (superseded):** "These tiers come from numbers, not authored nation labels. The map can create a new quadrangle if power shifts." — This position is reversed by the Phase 0 canonicalization: tiers are now authored, not numeric. A separate `power_score` may still be derived from numbers for non-tier uses.
- **Interaction with Memory and Pressure:** great powers could have different rivalry intensity defaults (primary only between great powers; secondary between great-and-minor), betrayal tolerance thresholds (great powers hold grudges longer), and Make Amends cost scaling (reparations to a great power should cost more than to a minor).
- **Gates needed:** numeric formula for calculating power scores, threshold ranges (what income/strength makes a "great power"), whether tiers are recalculated per turn or per-war, how tiers interact with the acceptance formula's existing modifier caps.
- **Natural home:** alongside `War Purpose + Score Semantics` (queue item 3) since power tiers inform war objectives and settlement legitimacy. Or as a sub-item of the later `Ally Participation + Common Peace` (queue item 4).
- **Files:** `world_state.py` (data), `diplomacy.py` (formula + tiers), `diplomatic_ledger.py` (display), `ai_diplomacy.py` (threat evaluation)
- **Est. sessions:** 1-2 for the data layer + formula, plus formula-integration touches across existing systems

---

## Gold Sink Options (B4 Balance — Design Gate)

**Priority:** MEDIUM | **Phase:** Pre-EA refinement

**RE-POINTED (July 2, 2026):** owner is `docs/ECONOMY_REVISIT_SPEC.md` EC-2 (the B4 gold-sinks gate). The candidates below are re-cost candidates for the ~3.4k/turn 1805 economy — France income is ~3.4k/turn on 28 provinces, upkeep ~950g, and the whole building stock costs ~1.85k — so this section's "~700g vs ~250g" numbers are legacy (19-region map). Original text kept as historical context.

Gold accumulation is a known design gap (~700g/turn income vs ~250g upkeep). Manpower-gated recruitment means gold piles up with no meaningful spending options. This section tracks candidate gold sinks for evaluation.

**Forced march REJECTED** — trivializes cavalry's 2-region movement advantage, which is cavalry's core identity.

### Leading Candidate: Province Development
- **Cost:** Variable (200-500g per investment)
- **Effect:** Invest gold in controlled region to boost supply cap, income, or repair war damage faster
- **Design appeal:** Creates invest-now-vs-save tension, rewards holding territory, ties gold to strategic positioning
- **Needs:** Investment tiers, per-region cooldown, diminishing returns formula, AI investment priority

### Other Candidates (evaluate after Province Development)

| Option | Cost | Effect | Notes |
|--------|------|--------|-------|
| Diplomatic gifts/bribes | 200g | +5 relation (once/turn/nation) | Gold becomes diplomacy tool |
| Mercenary garrisons | 400g | Defensive garrison without stationing marshal | Frees marshals for offense |
| Recruitment bounties | 300g | Double manpower regen for 1 turn | Accelerates rebuilding |

---

## Enemy AP Rebalancing (Deferred — Post Full Map)

**Priority:** LOW | **Phase:** After full 1805 map implementation

**RE-POINTED (July 2, 2026):** owner is `docs/ECONOMY_REVISIT_SPEC.md` EC-4 (enemy AP). The revisit trigger fired July 2, 2026 — the full 1805 map shipped with the real-map cutover. NOTE: the EC-0 AP-reset defect must land first. Original text kept as historical context.

Enemy AI action budget (currently 4 paid AP per nation) may need rebalancing once the full map is implemented with all nations, regions, and marshal counts at scale. Current 4-nation, 19-region map doesn't stress the action economy the same way a full campaign will. Revisit AP values, per-nation scaling, and aggregate action counts after full map playtesting.

---

## Wave 5 — Game Review Findings (Design Gate)

Cross-system findings from comprehensive review. Needs design gate as a batch.

**July 2, 2026:** per-item user approval is still required. Items already re-pointed above have new owners: R158 → `docs/COMMAND_ROBUSTNESS_SPEC.md` CR-7 (parser confidence feedback).

**Diplomatic Term Novelty — PARTIALLY ABSORBED into PL-25 (BUG_FIXES.md).** PL-25 covers the 80/20: amount jitter, personality-biased pen nudge, nation desire profile bias in `_build_base_terms()`, situational flavor lines. R155/R157 retain the remaining full scope: hawk/dove personality weight table for ALL AI proposals (not just Talleyrand's pen nudge), deep `TALLEYRAND_COMMENTARY` integration, and AI-initiated proposal personality voice.

**Focused audit routing (updated July 2, 2026):** R155 / R156 remain validated by code evidence and route to queue items 5-6 (8.EVAL). R160 is SUPERSEDED by Memory and Pressure v2.4.3 (see its row above) — it is no longer a pending upgrade. The diplomacy mailbox / recovery surface LANDED long since; R162 is not transport-blocked, it stays gated behind queue items 5-6.

| ID | Item | Summary |
|----|------|---------|
| R152 | Authority System UI Visibility | Authority impact not visible enough to players |
| R153 | ~~Literal Personality Triggers~~ | **SUPERSEDED by W6-5 The Literal Doctrine (user call, July 10, 2026)** — see the R59 row; literal never objects by design. |
| R154 | Combat Morale Spiral | Morale death spiral needs circuit breaker |
| R155 | AI Proposal Personality Voice | Partially absorbed into PL-25. Remaining: visible motive / personality in timing, terms, persistence, and player-facing explanation |
| R156 | Diplomacy Strategic Optionality | Diplomacy feels optional vs military path |
| R157 | Talleyrand Voice Depth | Partially absorbed into PL-25 (situational flavor, personality pen nudge). Remaining: deep commentary integration |
| R158 | NL Parser Confidence Feedback | Show parse confidence to player |
| R159 | Information Screen Teaching | Screens don't teach mechanics |

---

## Wave 6 — Creative Capstone (July 10, 2026) — **✅ APPROVED IN FULL; owner = `docs/WAVE6_FUN_FACTOR_SPEC.md`**

> Source: `docs/audits/CREATIVE_AUDIT_2026_07_10.md` (the AUDIT_GUIDELINE §8 fun-factor capstone — live 5-turn 1805 playtest under `LLM_MODE=anthropic` + two code-evidence sweeps). **GATE (July 10, 2026, same day): the user approved EVERY item below in full — plus two additions scoped at the gate: Dynamic Battle Naming (→ spec slice W6-2) and the Literal Doctrine hone (→ W6-5; user steer: literal marshals need not object — the fantasy is "generals who do what they're ordered").** The build-ready plan — slice order, seams, blessed default numbers, tests — is **`docs/WAVE6_FUN_FACTOR_SPEC.md`** (authoritative over the sketches below where they differ). Rows below map: EXP-N1→W6-3 · EXP-M1→W6-7 · EXP-C1→W6-4 · EXP-E1→W6-8 · EXP-M2→W6-6 · EXP-D1→W6-9 · E-CA-1/3→W6-11 · E-CA-2→W6-1 · E-CA-4→W6-4 · E-CA-5/6→W6-10.

### Gate additions (scoped at the July-10 approval; full designs in the spec)

| ID | Item | One-line mechanic | Spec slice |
|----|------|-------------------|------------|
| W6-ADD-1 | **Dynamic Battle Naming** | Serialized per-region battle counts → "Second Battle of Swabia", "The Great Battle of X" at ≥80k engaged; one naming site (`combat_executor` battle_name), consumed everywhere `battle_name` already flows. | W6-2 |
| W6-ADD-2 | **The Literal Doctrine** | Literal = "generals who do exactly what they're ordered": never objects **by design** (supersedes R59/R153's literal-objection TODOs), order echo + completion reports quoting the verbatim order, doctrine tells on card/dispatch/muster, per-turn **fidelity beats** ("Soult holds at Lorraine, per your orders — the guns did not move him"), precision rewards captioned. Builds on the existing Grouchy Rule (`combat_executor._calculate_reinforcements`) and SUPPORT standing orders. | W6-5 |

### Ranked expansions (by depth-per-unit-complexity — full designs in the memo §4; build detail in the spec)

| ID | Item | One-line mechanic | Owner / gate | Est. |
|----|------|-------------------|--------------|------|
| EXP-N1 | **The Dispatch Rewrite — "Berthier tells the story"** | Deterministic narrative-priority layer over existing events: headline selection, per-marshal danger flags, arc memory ("Bernadotte, hunted across three frontiers…"). No LLM, no new mechanics. | Standalone slice; **top-ranked item of the audit** | 1–2 sessions |
| EXP-M1 | **Marshal Fates: capture, parole, last stand** | Forced-retreat fate roll (escape/capture/personality-gated last stand); captured marshals become ransom/exchange clauses in existing settlement machinery; Building Blocks — Mack at Ulm becomes capturable. | Own design gate (thresholds, AI prisoner valuation) | 2–3 sessions |
| EXP-C1 | **March to the Guns, surfaced: muster preview + standing order** | Pre-battle muster block naming WILL JOIN / WILL NOT per marshal *with the personality reason*; cheap `"Soult, support Ney"` standing order; substrate the re-homed **Grouchy Moment** lands on. | Own gate; foundation for the Grouchy Moment gate | 1–2 sessions |
| EXP-E1 | **The Spoils of War: estate confiscation** — **✅ LANDED July 10, 2026 via W6-8** (`WAVE6_FUN_FACTOR_SPEC.md` §10; `test_w6_estate_confiscation.py`) | Conquering an enemy marshal's estate opens confiscate (windfall + grudge + own-cautious-marshal trust cost) vs respect (court acceptance bonus); confiscated estates become grantable (rides ES-7 as landed). Resolves the live "Swabia already sustains Marshal Mack's household" dead end. | ~~EC pass 2 gate (numbers)~~ numbers blessed at the July-10 Wave-6 gate (in-band tunable) | ~1 session |
| EXP-M2 | **Enemy marshals speak** | Deterministic one-liner bank keyed to (enemy personality × outcome × situation) at the battle-report seam; complements DEF-1 (diplomat voices), which does not own enemy marshals. | Content slice; MC-adjacent | <1 session |
| EXP-D1 | **"What does Europe intend?" — strategic assessment verb** — **✅ LANDED July 10, 2026 via W6-9** (`WAVE6_FUN_FACTOR_SPEC.md` §11; `test_w6_assessment_verb.py`) | `assess our situation` (dead-ends live today) returns per-war trajectory, **coalition posture** (computed, never shown), top threat sources, vassal trend + cause, one executable recommendation (absorbs R117's shape). | ~~Recommended first slice of queue item 6 (Talleyrand Desk)~~ landed via W6-9; queue item 6 owns the residual desk items | ~1 session |

### Escalations (gate-owned; no code)

| ID | Finding | Owner |
|----|---------|-------|
| E-CA-1 | Attacker morale-grind asymmetry (defender morale ~static through 15k casualties while attackers/reinforcers bleed to 47) — the live shape of the meat-grinder, post-EC. — **✅ LANDED July 10, 2026 via W6-11** (symmetric casualty-scaled morale in both combat copies, winner delta = bonus − loss; `test_w6_balance_duo.py` incl. the battle-2 replay) | ~~Combat balance gate (user)~~ landed at the blessed W6 numbers (defender curve 1.0, band ≥0.75) |
| E-CA-2 | Retreat agency + direction doctrine (honor stated destination or narrate substitution; homeward bias; never into an at-war nation with alternatives). Mechanical half = BUG-CA-2. | Combat/movement gate |
| E-CA-3 | War-priced recruitment: 10,000 men for 200g keeps gold free mid-war; scale per-soldier gold cost by force-limit ratio + war status. — **✅ LANDED July 10, 2026 via W6-11** (×3 at war composed with ×(1+overage), Europe-scoped, AI same-priced incl. its admin pre-checks; two-sided 1805 solvency pinned; `test_w6_balance_duo.py`) | ~~EC pass 2 (blessed numbers)~~ landed at the blessed W6 numbers (war ×3, band 2–4) |
| E-CA-4 | Explicit bad-odds `attack` gets no warning while vague delegation gets a lethal-odds interrupt — decide whether direct orders deserve a one-line odds note. | CR-6 gate |
| E-CA-5 | Settlement offers must state territorial consequences ("Britain retains Flanders") — "Peace" is illegible while home soil is occupied. — **✅ LANDED July 10, 2026 via W6-10** (`terms_summary` status-quo line; `test_w6_incoming_voice.py`) | ~~Settlement presentation (narrow, post-arc)~~ landed |
| E-CA-6 | Incoming-proposal voice + AI proposal variety (5 identical open-borders/"hegemony pressure" offers in 5 turns; named diplomat never speaks). — **✅ LANDED July 10, 2026 via W6-10** (`diplomat_line` register bank + 6-turn lapse/reject type cooldown + P3 relation-band diversification; `test_w6_incoming_voice.py`). The deeper R155/R156 scope (personality-driven timing/persistence/target choice, strategic optionality) stays with queue items 5–6. | ~~Queue items 5–6 (8.EVAL), with R155/R156~~ voice+variety landed; residual scope stays 8.EVAL |

### Revisions to prior items (live-evidence pass, July 10, 2026)

- **R154 (Combat Morale Spiral) — REVISED:** the claimed missing circuit breaker **exists and works** (`combat.py` FORCED_RETREAT_THRESHOLD=25 floor; +5/+10 victory recovery). The real, live-confirmed issue is the attacker/defender morale **asymmetry** — re-scoped as E-CA-1; do not build a second breaker.
- **R59 / R153 (Literal Personality Triggers) — RESOLVED July 10, 2026: SUPERSEDED by W6-5 The Literal Doctrine (user call at the Wave 6 gate).** Literal marshals never object BY DESIGN; the inert triggers were converted to a doctrine comment and the never-objects behavior is pinned (`test_w6_literal_doctrine.py`). The niche the triggers aimed at is owned by the CR-2/CR-5 clarification arms + the W6-5 fidelity surfaces (order echo, fidelity beat, muster warnings). |
- **R129 / R131 / R132 — LIVE EVIDENCE ADDED:** R132 is the strongest of the three — three vassals bleeding −4/−6/−8 loyalty per turn with no cause attached anywhere was a top-5 confusion of the playtest. Recommend R132 rides EXP-D1/queue-item-6 rather than waiting for a standalone slice.
- **R155 / R156 — CONFIRMED, EVIDENCE UPGRADED:** proposal monotony measured live (5 nations, identical proposal+reason, 5 turns); the *outgoing* surface (terms prep, acceptance estimate, ratification gate, motive commentary) is the register benchmark the incoming surface should be held to. Folded into E-CA-6.
- **R117 (Advisory Actionability) — ABSORBED into EXP-D1** (the strategic-assessment verb ends with an executable option).

---

## Historical Precision (1805 Campaign — Future Refinement)

These items are conscious trade-offs where v0.1 chose recognizability, immersion, or implementation speed over strict period accuracy. Each has an audit trail, not a bug. Track for EA scope when the full 1805 campaign lands. Added April 16, 2026 from the Memory and Pressure creative audit.

### P1: Period-accurate diplomat roster for 1805
- **Summary:** The four foreign diplomats in `backend/models/diplomat.py` (Hardenberg / Metternich / Castlereagh / Einsiedel) are recognizable Napoleonic-era names but historically took their depicted roles **after** the 1805 campaign start: Hardenberg as Prussian chancellor from 1810, Metternich as Austrian foreign minister from 1809, Castlereagh as British foreign secretary from 1812, Einsiedel as Saxon minister from 1813. The actual 1805 ministers were Haugwitz (Prussia), Stadion or Cobenzl (Austria), Mulgrave (Britain), and Bose or Löss (Saxony).
- **Design trade-off (deliberate):** recognizability was prioritized for v0.1 because the four chosen figures are well known to strategy players and the Voice Bible's Hawk / Schemer / Dove register distinctions were drawn from their historical voices. Swapping them in v0.1 would lose the established register voices without adding mechanical value and would force the Voice Bible exemplars to be re-authored before any useful commitments work shipped.
- **When to revisit:** once the full 1805 campaign ships (Early Access) and the game claims period fidelity as a feature. Swap to the 1805-accurate ministers and port the register notes. The Voice Bible's "Characteristic openings" / "Never says" framework should transfer cleanly — Haugwitz was a Prussian Hawk in the Hardenberg mold, Stadion a Schemer adjacent to Metternich, Mulgrave less distinctive than Castlereagh but workable, Bose closer to Einsiedel's dove register.
- **Revisit condition MET July 2, 2026:** the full 1805 campaign shipped (real-map cutover complete). Still EA-scope; interacts with DEF-1 Roster Voices register authoring.
- **Files:** `backend/models/diplomat.py`, `docs/DIPLOMAT_VOICE_BIBLE.md`, `backend/game_logic/diplomatic_templates.py`, any committed breach / hard-reject mock prose
- **Est. sessions:** 1 (cast swap + voice port + test refresh)

### P2: Britain reactive bloc pressure (continental-hegemon pattern)
- **Summary:** The v0.1 rivalry model has Britain as France's direct rival but gives Britain no *reactive* posture when France deepens ties with a continental power. Historically Britain opposed any continental hegemon on principle, paying subsidies to any continental power willing to fight France. Flagged in `RELIABILITY_COMMITMENTS_SPEC.md` v2.1 §7.4.C as the #1 historical-texture debt for Memory and Pressure.
- **When to land:** `Coalition Generalization` (D2, follow-up after Memory and Pressure). D2 should include continental-hegemon reactive threat accumulation — not just bloc-target parameterization — so Britain gains automatic threat against any power approaching continental hegemony, not only France by name.
- **Owner (updated July 2, 2026):** the `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` deferred-ledger D2 row. The previously-named "Coalition Generalization (D2)" is not a landed slice — this item rides that deferred-ledger row.
- **Files:** `backend/game_logic/coalition.py`, `backend/game_logic/diplomacy.py`
- **Est. sessions:** folded into D2 spec work

### P3: Diplomatic Ledger sort / filter at scale
- **Summary:** The Diplomatic Ledger's Nations tab currently renders one row per nation. At 5 nations this is clean; at 6-8 full 1805 nations with multiple rivals each, the list becomes dense. Commitments rows (active rivals, betrayal warnings, posture markers) multiply the cell count.
- **When to land:** Pre-EA polish alongside Map Renderer UX pass, or absorbed into the Talleyrand Desk + Explanation Layer spec (diplomacy queue item 6).
- **Urgency raised (July 2, 2026):** 20 nations render now in the shipped 1805 campaign. Owner: queue item 6 (Talleyrand Desk + Explanation Layer) or pre-EA polish.
- **Files:** `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`
- **Est. sessions:** 1 as a standalone UX slice, or folded into the Talleyrand Desk pass

---

## Estate Second Pass deferrals (July 11, 2026)

Filed at the ES-7 second-pass build (`ECONOMY_REVISIT_SPEC.md` §0.6.8 — the estates+rentes reward portfolio). Historically grounded in the July-11 design conversation (Domaine Extraordinaire rentes/arrears; Fontainebleau April 1814; Murat's January-1814 Austria treaty).

> **✅ ESP-1, ESP-2, and ESP-4 LANDED July 11, 2026** with the Jealousy v3.2 build (`JEALOUSY_SPEC.md` §0.3 rider contracts + §0.4 landing record; `tests/test_estate_riders_esp.py`, 22). ESP-2 landed at the declare-war seam via the marshal-petition channel rather than objection_v2 — recorded deviation, §0.3. ESP-3 remains open with its diplomacy-gate owner below.

### ESP-1: The Fontainebleau beat (collective marshal petition) — ✅ LANDED
- **Summary:** When several marshals are eroding simultaneously (shortfall past grace), the system today runs parallel silent trust bleeds. History says this moment *speaks*: at Fontainebleau the marshals collectively told Napoleon "the army will not march" and forced the abdication. Fire a collective dialogue when ≥3 marshals are eroding on the same turn — a petition demanding estates, rentes, or peace, with real player choices (concede / refuse with trust cost / partial). Converts the death spiral from a punishment into the game's best scene.
- **When to land:** Jealousy v3.1 gate (next queue item) — the gate already owns marshal-collective emotional mechanics; this is its natural marquee event.
- **Completion definition:** the petition fires under the trigger in a live game, is answerable via popup, each arm has deterministic effects and tests, and STATUS records the landing.
- **Files:** `backend/models/world_state.py` (`_process_dotation_state` trigger), `backend/models/dialogue_manager.py`, `backend/game_logic/dotation.py`, Godot dialogue whitelist (per the dialogue-popup-wiring rule).
- **Est. sessions:** 1

### ESP-2: War-weary rich marshals (satisfaction objects to new wars) — ✅ LANDED
- **Summary:** Historically the *endowed* marshals were the peace party — by 1812–13 the men with duchies begged Napoleon to stop. Mechanically: a marshal whose expectation is fully met and large (satisfaction ≥ a floor) gains an objection trigger against NEW aggressive war declarations ("I have my duchy, Sire — why do we march again?"). Rides the existing objection_v2 ConcernLevel machinery; no new dialogue plumbing.
- **When to land:** Jealousy v3.1 gate, same personality/emotion review.
- **Completion definition:** objection fires for a rich marshal on a player war declaration, never for poor marshals, GR5-checked where applicable, behavior tests.
- **Files:** `backend/commands/objection_v2.py`, `backend/game_logic/dotation.py` (satisfaction query), `backend/game_logic/diplomacy.py` (war-declaration seam).
- **Est. sessions:** 0.5 (folded into the Jealousy build)

### ESP-3: Respect-by-treaty (the Murat clause)
- **Summary:** Treaty transfers of estate provinces currently strip silently on the next tick; only military capture offers the confiscate/respect choice (W6-8). Historically treaty-preserved dotations were real furniture — Murat kept Naples by treaty with Austria (Jan 1814). On ratification of a settlement/treaty that hands YOU a province funding an enemy marshal's estate, fire the same confiscate/respect choice (AI uses its existing at-war rule); respect feeds the existing `respected_estate_mod` +5 acceptance term.
- **When to land:** a future diplomacy gate — touches ratification flow and acceptance math, so it must NOT land ad hoc. Candidate venue: 8.EVAL's diplomacy triage or a Settlement addendum gate.
- **Completion definition:** choice fires at the ratify seam for player-received estate provinces, AI symmetric, acceptance term verified, tests for both arms + the third-party-cede no-choice case.
- **Files:** `backend/game_logic/settlement_ratify.py`, `backend/models/world_state.py` (treaty-clause transfer), `backend/game_logic/dotation.py`, `godot-client/.../capture_choice_dialog.gd` (estate stage reuse).
- **Est. sessions:** 1

### ESP-4: Rente arrears/default beat — ✅ LANDED (folded into the Jealousy build per this row's fold-in clause)
- **Summary:** §0.6.8 pass-1 rentes charge like upkeep with no bankruptcy mercy. The historical texture — rentes chronically in arrears, marshals resenting unpaid paper — is a drama beat: when the treasury cannot cover the rente bill, rentes lapse (auto-revoke) with a notification ("the treasury defaults on his rente — he holds worthless paper, Sire") and the shortfall machinery reopens. Cheap, legible, and makes deficit-financing marshal loyalty a real risk.
- **When to land:** Economy pass 2 (EC-1 successor work), or fold into the Fontainebleau slice if the Jealousy gate takes ESP-1.
- **Completion definition:** insolvency lapses rentes deterministically at one defined seam, notification + dispatch line, both sides GR5, tests incl. the recovery case (re-grant after solvency returns).
- **Files:** `backend/models/world_state.py` (income/bankruptcy seam), `backend/game_logic/dotation.py`, `backend/notifications.py`.
- **Est. sessions:** 0.5


## §NA-6d Audit — routed behaviours (July 19, 2026)

Surfaced by the design-coherence lens of the NA-6d audit-of-the-audit
(record `NATION_AGENDAS_SPEC.md` §21.1). Both are KNOWN, deliberate v1
behaviours homed here so neither is an unowned loose end (GR9).

### NAD-1: Named grievances starved to zero by the shared cap
- **Summary:** `formation_grudge:<tag>` rows share `AGENDA_GRUDGE_CAP` (2)
  with `agenda_grudge`, which emits FIRST at its own value. Two denied
  post-peace courts therefore take the whole budget and **every** named
  question ("The Polish Question", "The Roman Question") vanishes from the
  threat panel with no explanation — the turn after the player watched
  them accrue. This is the same legibility failure the audit's D1 fixed,
  one level up, and it is more reachable than the multi-formation case.
  The mechanical split is correct (the cap is a real ceiling); what is
  missing is the player-facing account of WHY a named row disappeared.
- **When to land:** the next diplomacy/coalition legibility pass, or
  alongside NAD-2 (same surface, same fix shape).
- **Completion definition:** a starved-out contributor is either rendered
  at 0 with an honest "outweighed this turn" note, or named in a single
  overflow line; the panel never silently drops a grievance the player
  has already been shown. Test: build a world with `agenda_grudge` at the
  cap plus one standing formation, assert the panel still accounts for the
  formation.
- **Files:** `backend/game_logic/coalition.py` (step 2 budget split),
  `backend/game_logic/diplomatic_ledger.py` (`_build_balance_of_europe`),
  `godot-client/.../diplomatic_ledger.gd`.
- **Est. sessions:** 0.5

### NAD-2: A third formation emits nothing, silently
- **Summary:** With the cap at 2 and a flat +1 per standing formation, a
  campaign carrying three or more live formations drops the surplus. It is
  debug-logged and pinned
  (`test_grievances_beyond_the_cap_are_dropped_not_silently_merged`), so
  the behaviour is deliberate and not a merge-into-a-neighbour bug — but
  the player sees no trace. Unreachable in shipped data (only Poland and
  the Roman Republic author `aggrieved`), so this is a modding-surface and
  future-content row rather than a live defect.
- **When to land:** with NAD-1 (identical surface), or when a scenario
  authors a third `aggrieved` formable — whichever comes first.
- **Completion definition:** either a validator warning when authored
  `aggrieved` formables exceed `AGENDA_GRUDGE_CAP`, or the NAD-1 overflow
  line covering it. Test: three standing formations, assert the third is
  accounted for on the panel rather than absent.
- **Files:** `backend/game_logic/formations.py`
  (`get_formation_grudge_contributions`), `backend/modding/validator.py`.
- **Est. sessions:** 0.25

### NAD-3: The Duchy of Normandy is a flag with no story
- **Summary:** The coalition-side mirror carve lands on the most
  emotionally loaded moment in the campaign — the player's own homeland
  dismembered — and then the game never mentions it again. Its sibling
  templates both carry more: Warsaw has `commonwealth_restored` (→ Poland)
  plus `guard_the_vistula`; the Roman Republic blocks Italy's risorgimento
  and drags two great powers. Normandy has no deck, no `aggrieved`, no
  follow-on. Related: §11.8 authors WITNESS and AUTHOR subtitles for the
  Proclamation, but the Normandy path creates a third perspective —
  VICTIM — with no authored arm, so a player watching a duchy carved out
  of France reads "A new power takes its seat in Europe."
  (The empty `aggrieved` list itself is CORRECT and settled — §21.1 D3.)
- **When to land:** the next content/authoring pass on NA-6, or whenever
  the naval phase brings DEF-5's Free Ireland carve in (same machinery,
  same victim-perspective gap).
- **Completion definition:** a one-entry Normandy deck authored in
  `europe_1805.json` (pure data, no code) AND a victim-perspective
  subtitle arm on `build_proclamation_card` for a carve from the viewing
  player's own soil; both pinned.
- **Files:** `godot-client/project-sovereign/assets/maps/europe_1805.json`,
  `backend/game_logic/formations.py` (`build_proclamation_card` subtitle).
- **Est. sessions:** 0.5


### NAD-4: A Formables deep link can land on the wrong war
- **Summary:** `build_formables_payload` runs the real eligibility
  predicate PER WAR and knows exactly which war a carve qualifies in
  (`deep_link.war_id`). When the player has TWO OR MORE wars with that
  court, following the link lands on step 2 where `open_settlement` is
  disabled with `multi_war_ambiguity` and a per-war picker — and the
  player can pick the war where the carve is refused, immediately after a
  row told them it was available. The NA-6d audit's first attempt threaded
  the qualifying `war_id` through as a fallback; the audit-of-the-audit
  proved that INERT (an available `open_settlement` always carries its own
  war_id, so the fallback never fires) and the dead machinery was removed.
  The gap itself is untouched and real.
- **When to land:** the next diplomacy-wizard pass, or whenever the
  ambiguity picker is next opened for other reasons.
- **Completion definition:** the ambiguity picker, when reached from a
  Formables deep link, MARKS the qualifying war (or orders it first) so
  the player cannot silently pick a war the carve is refused in. Test:
  two live wars with one court, deep link followed, assert the qualifying
  war is distinguishable in the picker payload.
- **Files:** `godot-client/.../diplomacy_wizard.gd` (picker render),
  `backend/game_logic/formations.py` (`deep_link` already carries it).
- **Est. sessions:** 0.5


---

## Source Documents (Archived Reference)

| Document | Items Moved Here |
|----------|-----------------|
| `docs/DIPLO_REFINEMENT.md` | Wave 3-5 open items, all R-IDs |
| `docs/DIPLOMACY_DESIGN_FIXES.md` | Design discussion items, N1/A3/A4 AI fixes |
| `docs/archive/PLAYTEST_AUDIT_2026_03_29.md` | War Objectives, Ticking War Score, Vassalage Power Cap, Forced Alliance, Liberation (lines 215-722) |
| `docs/JEALOUSY_SPEC.md` | Jealousy pointer (spec kept as-is) |
