# Econ Eval — Fable's Independent Pre-Build Evaluation

> **Date:** July 9, 2026 · **Repo state:** master @ `c5e411e` (clean; same-day as the completed Comprehensive Codebase Audit) · **Produced by:** Fable, single-mind pass per `ECONOMY_REVISIT_SPEC.md` §0.7.
> **Mandate:** an independent concur / dissent+alternative / simplify read of every recorded economy decision (§0 / §0.5 / §0.6 / Appendix A), written *before* any EC code, feeding — not replacing — the EC-2 user design gate. Every load-bearing code claim below was re-verified directly against `c5e411e` in this pass (income/upkeep/regen loops, trust substrate, vassal tribute, CS, AI admin ladder, bankruptcy, `nation_starting_regions`), not inherited from the July-7/8 workflows.
> **Fresh-perspective note (user steer):** this read deliberately does not treat the multi-agent outputs as settled. Where I agree I say why in my own words; where the numbers or shapes don't survive contact with the code or with history/genre precedent, I dissent and give the alternative.

---

## 1. TL;DR + the one thing I'd change

**The recorded plan is directionally right and better-grounded than most multi-agent output I've reviewed** — the diagnosis (sources without proportional sinks, neither currency scarce, treasury walled off from the marshals) reproduces exactly in code, and the ES-2 + ES-7 pass-1 pair is the correct *kind* of answer for this game: this is a character game, not a map-painter, so the flagship sink should touch a marshal's face (Crusader Kings' title-expectation loop is the right genre ancestor here, not EU4's ledger). I concur with most of it.

**But two recorded decisions do not survive arithmetic, and one of them is the flagship:**

1. **⚠ HEADLINE — the E5 constants make ES-7 mathematically broken as specced.** `EXPECTATION_CAP ≈ 300 g/turn` cannot be met: satisfaction is defined as `Σ 0.30 × eff_income(estate)`, capitals are grant-ineligible, and the best non-capital province yields 200 base (250 with a market). Two of the best estates in Europe ≈ **105–150 satisfaction vs a 300 cap** → an 8-win marshal has a *permanent* ~150+ shortfall → **−3 trust/turn forever, and no payment can stop it**. That directly falsifies the reframe's core promise ("paying stops the bleed") for exactly the marshals the mechanic is about — your best ones. Ney at 8 victories, endowed with the two richest duchies you own, still slides from Loyal to Broken in ~24 turns. It would read as a bug, and it would poison the one mechanic that makes this pass special. **Fix (recommended): make the endowment a full-income redirect** — satisfaction = the estate's full `eff_income`, and the nation loses the same (it's *his* duchy now). One top province ≈ one legendary marshal's cap, matching the spec's own "~one province tier" gloss and the "0–2 dotations per marshal" non-goal; the 0.30 constant is deleted outright. Detail in §3.

2. **The E1 band's first anchor is unreachable by the blessed pass-1 pair.** "Starting-army France absorbs ~55–70% of net" is a **turn-1** anchor — but at turn 1 France has zero fresh conquests (ES-2 contributes ~0) and zero battles won (ES-7 contributes 0). Only ES-3 (army upkeep) can move the turn-1 number, and ES-3 is currently sequenced in Track 3, *after* the pair. As recorded, the gate would bless a band its own pass-1 set cannot hit, and the band would have to be tuned twice (once for the pair, again when ES-3 lands). **Fix: promote ES-3 into the EC-2 pass-1 landing** and tune the band once against the stacked set — which is how §0.6.4 already defines the band test anyway. Detail in §4.

**If I could change one thing:** the ES-7 satisfaction scale (item 1). Everything else in this memo is refinement; that one is a broken-as-shipped flagship.

---

## 2. Verdict table — every recorded decision

| # | Recorded decision | Verdict | One-line reason |
|---|---|---|---|
| 1 | Core diagnosis ("mechanically sound, emotionally inert"; sources without sinks) | **CONCUR** | Reproduced in code myself: flat `(strength//1000)*5` upkeep, free re-recruits, zero trust references in `economy_executor.py`. |
| 2 | ES-1 manpower fix as gate-free prereq; re-key + rate-drop ONE commit | **CONCUR** (simplify one sub-item, §5.1) | The +15,400/turn naive-rekey trap is real (77 qualifying provinces × 200); the ordering principle (manpower first) is right — no gold sink bites while re-recruiting is free. |
| 3 | ES-1 pool-cap scaling (`MAX_CAVALRY_POOL` etc. scale with nation size) | **SIMPLIFY — CUT from pass 1** | Once the *rates* are fixed, the caps are ceilings nobody reaches; scaling them is a tuning surface with no behavior behind it. §5.1. |
| 4 | ES-2 Occupation Upkeep in pass 1 | **CONCUR on intent; SIMPLIFY the shape** | The structural anti-snowball sink is right; the `integration_turns` ramp duplicates the existing stability ramp. Stability-tier-keyed cost on non-homeland soil does the same job with zero new serialized fields. §6. |
| 5 | ES-7 reframe ("Cost of Success"; endow estate + title; no trust on grant) | **CONCUR — enthusiastically** | Historically exact (post-victory dotation waves; the marshalate got *more* expensive as it won) and the CK title-expectation precedent proves the loop is fun. The reframe rejection of the bribe is the single best design call in the record. |
| 6 | ES-7 E5 constants (30% skim; cap 300; REP_STEP 40; grace 1) | **DISSENT — scale incoherence** | See §1 item 1 / §3. Recommended: full-income redirect, grace 2, REP_STEP validated against measured win rates. |
| 7 | ES-2 + ES-7 as the matched pass-1 pair | **CONCUR, + promote ES-3 into the same landing** | The pair is the personality; ES-3 is the genre-proven workhorse the band arithmetic requires. §4. |
| 8 | §0.6.3 order (Track 1 gate-free → gate → pair → Track 3 ES-3) | **DISSENT on ES-3's position only** | Track 1 (S1–S4) concur as-is. ES-3 moves from Track 3 into Track 2. §4. |
| 9 | Band E1 (~55–70% of total net incl. diplomatic economy; doubled empire → break-even) | **CONCUR with the range; clarify the anchor** | 55–70% is genre-consistent (NTW/TW mid-game upkeep, EU4 army+forts norms). The turn-1 anchor must be measured with ES-3 in the set (§4), and "total net incl. diplomatic economy" is the right denominator. |
| 10 | ES-4 Province Development → pass 2, hard-capped | **CONCUR** | Right call; at that gate consider the "Grand Works with faces" reframe (§7.3) before building a generic dev track. |
| 11 | ES-10 Corruption — CUT | **CONCUR** | Dominated on every axis; second Jealousy collision; the cut is clean GR9. |
| 12 | EC-6 sandbox (victory/defeat disabled; 7 surfaces incl. display readers) | **CONCUR** | The 60-turn defeat-from-dominance reads as a bug; the 7-surface completeness list (incl. `_build_turn_limit_warning` + `get_turn_summary`) is correct and I verified the hidden `_check_victory_conditions` region-scan is real. |
| 13 | EC-1 (registry income field preferred) / EC-4 (enemy AP retune) | **CONCUR** | Income is map data, not scenario data; EC-4 is pure config post-EC-0. |
| 14 | EC-5 self-cost = Option B (symmetric, solvency-gated, fallback A) | **CONCUR + two riders** | Authentic (Berlin-Decree self-harm gutted Bordeaux/Marseille). Riders: an activation surface, and the Britain-treasury→subsidy coupling that gives the CS a strategic *point*. §7.1–7.2. |
| 15 | EC-7 / ES-6 = dated trigger post-pair; ES-2 owns gold, ES-6 owns manpower | **CONCUR** | Right split, right timing; `get_distance` is a cached BFS so the reuse is genuinely GR8-safe. |
| 16 | Soft goal = keep pure open-ended | **CONCUR** | The new drains ARE the near-term directional pressure; goals belong to the Victory pass. |
| 17 | E6 bankruptcy-mercy extension to new drains | **CONCUR** | Mercy is upkeep-only today (verified); a bankrupt 800g minor AI facing unmerciful new drains death-spirals via the existing 5%/turn desertion. Extend mercy to ES-2 + ES-3; ES-7 structurally floors at 0 (it redirects income that exists). |
| 18 | AI-admin `_pick_admin_action` rung; fee deducted in-executor | **CONCUR** | Verified the double-count hazard myself: `_calculate_admin_bonus` returns 0 for AI because `execute_admin_phase` applies the leftover-AP bonus directly — a bonus-path fee WOULD double-count. |
| 19 | Ledger both-halves (SC-33) blocking on each new stream | **CONCUR** | Non-negotiable; the PRE-EC floor precedent proves the failure mode is real. My ES-2 simplification makes this *easier* (a cost line, not an income multiplier — §6). |
| 20 | Double-count guards (dotation/vassal disjoint; ES-2/vassal; ES-2/ES-6 per-currency) | **CONCUR** | `get_nation_regions` keys on controller so vassal soil is already outside the lord's set; the grant-time predicate closes the rest. One new guard needed under my §3 variant: estate-exempt-from-occupation is deliberate and must be pinned by a test. |
| 21 | §0.6.1 refinements (6 upkeep callers; vassal rate is 50% not 30%; EC-6a 7 surfaces; `_process_dotation_state` placement post-income/pre-bankruptcy; `_get_marshals_in_region_indexed` not `_has_marshal_in_region`) | **CONCUR** | All five re-verified; the bankruptcy-ordering comment in `process_income_phase` confirms the placement constraint is real. |
| 22 | ES-9 emergency levies stay in the pool (unowned) | **CONCUR** | Correctly dependent on ES-1; revisit after the pair proves the pool actually runs dry in play. |
| 23 | EC-8 economic diplomacy (optional row) | **CONCUR** | Leave owned-but-unscheduled; do not let it ride pass 1. |

Audit-escalation triage (§0.7.2): **the July-9 correctness sweep's §6.5 economy chunk found no code defects and produced zero economy escalations** — there is nothing to fold in beyond what §0/§0.5 already record. The one ledger-adjacent defect it did fix (vassal dispatch misattribution) doesn't touch balance.

---

## 3. Headline dissent — ES-7's satisfaction scale (E5)

**The arithmetic.** Grant-eligible provinces are non-capital, so the ceiling is `major_city` = 200 base income (250 with a market). Spec satisfaction = `0.30 × eff_income` → **60–75/turn per best-case estate**. The spec's own non-goal caps dotations at 0–2 per marshal → max satisfaction ≈ **150**. Expectation cap = **300**. A marshal at 8+ career wins (`REP_STEP 40 × 8`, and note `battles_won` increments for *defensive* wins and for *every coordination participant* — I verified the seams at `combat.py:582/594` and `combat_executor.py:3144/3153` — so 8 wins arrives fast for a front-line marshal) therefore carries a permanent ≥150 shortfall → `min(3, ceil(150/50))` = **−3 trust/turn, forever, fully endowed**. From trust 70 that's Broken (≤20) in ~17 turns — for the marshal who won you the war, *after* you gave him your two best duchies. The falsifiable heart of the reframe — "paying stops the bleed" — is false above ~4 wins.

**Recommended fix — full-income redirect (delete the 0.30):**
- `satisfaction(m) = Σ eff_income(r)` over held estates; the nation's ledger loses the same full amount (`Dotations` line). The duchy's revenue is *his* — which is also the cleaner fiction: under the 30% skim the state keeps 70% of "his" duchy, which invites the question the mechanic can't answer.
- One `major_city` estate (200) + one `city` (150) ≥ cap 300 → "0–2 dotations per marshal" and "~one province tier" both become *true* statements.
- The sink gets real: 4–5 honored marshals mid-game ≈ 800–1,200 g/turn of redirected income — a proper contribution to the band, and each grant is a chunky, visible, regrettable decision (exactly the Sid Meier bar).
- Fallback if the band test shows over-drain: satisfaction = full `eff_income`, national cost = a fraction — but keep **satisfaction** on the full value regardless; the incoherence lives entirely on the satisfaction side.

**Second-order recommendations on the same mechanic:**
- **Grace turn 1 → 2.** With grace 1, a marshal whose expectation just jumped +40 from a *victory* can begin eroding two turns after the win — "I won and he's already bitter" is the exact un-fun beat the debounce exists to kill. Two turns of grace keeps the pressure while letting the player answer at their next admin window.
- **Validate REP_STEP against measured win counts** in the band-test fixture (log `battles_won` across a 20-turn France run). Coordination-participant increments mean roster-wide expectation grows faster than "battles fought" intuition suggests; pick REP_STEP so a typical active marshal reaches cap around turn 15–20, not turn 6.
- **Grant scope: prefer "conquered (non-homeland) provinces only" over "co-located/adjacent."** This is *more* historically faithful (the Domaine Extraordinaire drew exclusively from conquered lands — never metropolitan France), it removes the odd UI case of endowing from deep in enemy territory, and it composes with ES-2 into the best decision this pass can produce — see §6.1.
- Define the prune path for a marshal leaving play (capture/removal) alongside the region-loss prune, so `dotation_regions` can't orphan.
- Everything else in §0.6.2 — expectation from the flat `battles_won` counter, `modify_trust`-only, no-bribe negative assertion, erosion self-limiting with no snowball, AI-side gold consequence carrying GR5, save-compat grace on load — **concur as written**. The `modify_trust` seam lands the erosion exactly where the game already has teeth: below 40 the obedience curve (70%→40%) and the objection stack take over, so "a stiffed marshal becomes unreliable" emerges from existing systems with zero new code.

**History note (fresh grounding for the gate):** the reframe is better supported than the spec claims. Beyond the dotation waves (post-Tilsit 1807–08 was effectively a scheduled reckoning of accumulated expectation), the *later* dynamic — Napoleon complaining his marshals had grown too rich and comfortable to campaign hungrily — is the same mechanic's second act. That second act (wealth → caution) belongs to the Marshal Content Pass / Jealousy territory, not EC; but it means ES-7's state (estates held) is a substrate those approved-later specs can build on. Worth noting at the gate; not scope.

---

## 4. Sequencing dissent — ES-3 belongs in the pass-1 landing

The recorded plan defers ES-3 (super-linear per-corps upkeep + force limit) to Track 3. Three reasons to promote it into the EC-2 landing:

1. **Band arithmetic (the hard one).** E1's first anchor is "starting-army France absorbs ~55–70% of net." At campaign start ES-2 ≈ 0 (no fresh conquests) and ES-7 = 0 (no wins). The only pass-1 drain that exists at turn 1 is upkeep — ES-3. As recorded, the gate blesses a band the blessed set cannot reach, and the two-sided golden-band test would pass trivially at turn 1 while measuring nothing.
2. **Tune once, not twice.** §0.6.4 already defines the band as the *combined* effect of ES-2 + ES-7 + ES-3 (plus the diplomatic economy). Landing ES-3 later forces a re-tune of everything after the pair has already been balanced without it.
3. **Risk asymmetry.** ES-3 is the genre-proven workhorse (army upkeep is the dominant drain in every Total War; force limits are EU4's oldest anti-snowball tool) and mechanically the smallest of the three — one function rewrite plus the 6-caller/ledger/dispatch threading §0.6.1 already scoped. It is the *safest* drain in the set; the two novel mechanics are the risky ones. Shipping the safe drain last inverts the risk order.

**Recommended order:** Track 1 unchanged (S1–S4) → EC-2 gate (now also blessing E3's numbers, which were already escalated there) → Track 2 = **S5 ES-3 → S6 ES-2 → S7 ES-7**, one band test over the stacked set as the slice acceptance. Trade-off acknowledged: Track 2 grows from two slices to three and lands as one balanced unit; mitigation is that ES-3 is independently testable and its numbers were already at this gate.

---

## 5. Track 1 refinements (gate-free set)

### 5.1 ES-1 — concur, with two simplifications

- **Re-key + rate-drop as ONE commit: concur.** Verified the trap: `terrain=='urban'` matches zero provinces; `region_type ∈ {city, major_city, capital}` matches ~77; a strict re-key at rate 200 is a fresh runaway strictly worse than dead code.
- **Cut pool-cap scaling from pass 1.** With cavalry at 150/plains + summed cap and artillery at ~80/cap 600, France's regen lands ~1,750 cav/turn and ~750 art/turn — refilling the 30k/20k pools takes 17–27 turns. The caps stop being reachable in normal play; scaling them buys no behavior and adds a formula to bless. Revisit only if the band test shows caps binding.
- **Leave `INFANTRY_BASE_REGEN` flat — deliberately.** The EC-3 row flags "flat infantry regen vs nation size" as a defect. Fresh read: **flat regen is secretly an anti-snowball rubber band.** France at 80 provinces regenerating the same 2,500/turn as a 3-province minor is *pro-underdog* — exactly the direction every other lever in this pass pushes. War exhaustion already scales it downward for the belligerent. Scaling infantry regen with nation size would *help* the leader. Recommend recording it as intended behavior, not a defect.

### 5.2 S3 (ledger GR8 fix) and S4 (EC-6a) — concur as written

Nothing to add beyond §0.6's own completeness notes, which I verified (the hidden victory-check region-scan; both display readers).

---

## 6. ES-2 — concur on intent, simplify the shape

**What the spec's shape costs:** a new serialized `Region.integration_turns` field (+ save-compat + recapture-reset logic + the name-collision dodge), an autonomy multiplier 0.35→1.0 *stacked under* the existing stability multiplier (two invisible ramps on the same income number — the player sees a small income and can't tell why), and a marshal-pacification check that needs the indexed-marshal plumbing called out in §0.6.1 #5.

**What the code already has:** capture drops stability to Hostile (0% income) and it climbs through Unrest (25%) / Settling (75%) / Stable (100%) at +5/turn, +10 with a marshal present — *the integration ramp already exists*. What's genuinely missing is the **permanent** cost of holding foreign soil.

**Recommended shape — occupation cost keyed to existing state, zero new fields:**

- Every controlled province **not in the nation's `nation_starting_regions`** (serialized, scenario-populated at construction, save-compat fallback already in `from_dict` — verified) pays a per-turn occupation cost as a fraction of its **base** `income_value`, stepped by its current stability tier: Hostile ~50% · Unrest ~35% · Settling ~20% · **Stable ~10% floor, permanent** (fractions are E-numbers for the gate).
- Computed inside the existing `calculate_turn_income` per-nation loop (GR8-clean), surfaced as a single signed **"Occupation"** ledger line (SC-33 both-halves as specced).

Why this is better, not just smaller:

1. **Fresh conquest is a real "digest before you bite" bind** — a 300-income city yields 0 while Hostile *and* costs ~150/turn to hold. The spec's fraction-of-*reduced*-income garrison cost inverts this: it charges ~0 exactly when occupation should hurt most.
2. **One mechanism, fully legible.** The player sees full income minus a named cost line — no second invisible multiplier inside the income figure. The stability label the UI already renders *is* the integration progress display.
3. **Recapture-reset is free** (recapture drops stability — no reset code), **marshal-pacification is free** (the +10 garrisoned stability growth already exists), and **plunder gets a real price** (plundered regions sit at low stability longer → pay the high occupation tiers longer — the sack-vs-secure choice finally has a recurring consequence).
4. **A permanent floor is the actual anti-snowball property.** The spec's ramp ends; its persistent piece (the garrison fraction) is the load-bearing part anyway. Keying the floor to non-homeland soil makes empire size itself the drag, which is the point.
5. **It creates the empire's defining choice with zero extra code — see 6.1.**

Honest trade-offs: (a) no explicit "integration completes" moment — a conquest is never free; mitigation: that *is* the Napoleonic experience (Spain never integrated), the floor is small, and the game's existing answer to "make it stop" is vassalization; (b) old saves grandfather conquered-at-save-time provinces as homeland via the `from_dict` derived fallback — an acceptable mercy, worth one doc line; (c) if a future pass wants true naturalization, "N consecutive Stable turns promotes to homeland" can be added *then*, with its field, behind its own row.

### 6.1 The triangle this buys (and why the pair + this shape is the right pass 1)

With stability-keyed occupation cost + conquered-only estates (§3) + the existing vassal system, **every conquest becomes a standing three-way decision**:

- **Hold it** — keep its income, pay occupation forever;
- **Vassalize it** — no occupation cost, 50% tribute, autonomy/loyalty risk (all existing code);
- **Endow it** — zero income, zero occupation cost (his household administers it), one marshal's expectation met and his title on the map.

That is "Territory as Command Dilemma" stated as a game rule — every province on the map has a face-shaped question attached, and all three answers are real. The endow arm even produces emergent flavor for free: a freshly conquered estate satisfies poorly until pacified (eff_income low), and the marshal himself garrisoning his own duchy pacifies it faster — "go govern your estate, Marshal" falls out of existing stability rules. I recommend the gate adopt the estate-exempt-from-occupation rule (one predicate + one named test) precisely because it completes this triangle.

---

## 7. Expansions (per the wide-aperture steer — recommendations, not scope creep)

### 7.1 EC-5a rider: close the CS → subsidy → coalition loop (small, high-leverage)

Option B gives the CS a *fiscal* consequence; this rider gives it a *strategic* one. `_process_british_subsidy` today pays a flat 200g to one recipient regardless of Britain's treasury. When EC-5a lands the Britain income-bite, **scale subsidy capacity to Britain's actual treasury/income** (e.g. subsidy = min(200, some fraction of Britain's net)). Then the Continental System does what the Berlin Decree was *for*: squeezing Britain visibly starves coalition funding — the player can watch Pitt's gold thin out in the diplomatic ledger. One formula + one test; converts EC-5 from a numbers patch into a strategy. (Historically exact: subsidy volume tracked Britain's fiscal capacity — Pitt's £1.25M-per-100k-men treaties of 1805.)

### 7.2 EC-5a completeness: the CS needs an activation surface

`continental_system_members` boots empty; membership is reachable only via puppet auto-join and a settlement term, and the whole function early-returns on empty. Balancing Option B's numbers against a mechanic no campaign activates is balancing dead code. **5a's completion definition should include the player-facing decree/join-leave surface** (the R26 promise) — or the row must explicitly record that the CS remains settlement-term-only and trim the promise (GR9 either way).

### 7.3 ES-4 at its pass-2 gate: consider "Grand Works" framing

When ES-4 returns, consider replacing the generic 5-level dev track with a handful of **named, one-per-category Grand Works** (Code Napoléon, the Arc, a Grande Armée depot) with chunky costs and visible faces/authority hooks. Same sink, same cap, but it reads as "what did I build this campaign" rather than a spreadsheet column. Recommendation to *that* gate, not this one.

### 7.4 ES-7 second act (recorded for the MC/Jealousy gates, NOT EC scope)

A peace-treaty "reckoning" beat — expectation accrued during a war coming due when peace is signed (the post-Tilsit wave) — would concentrate the ES-7 dilemma at the game's existing dramatic peak (the settlement flow). It needs no new state (expectation and the settlement seam both exist after pass 1). Explicitly not pass-1 scope; parked here with a name so it isn't an unowned deferral: candidate for the Marshal Content Pass gate as **MC-ES7b "The Reckoning."**

---

## 8. Recommended blessed numbers (E1–E6) — the gate's decision sheet

| # | Knob | Recommendation | Delta vs §0.6.5 |
|---|---|---|---|
| **E1** | Band | **~55–70% of total net (incl. diplomatic economy) — concur** — measured with ES-3 IN the set (§4); doubled empire → break-even; never unrecoverable; two-sided France + 800g-minor test. | Anchor clarified: turn-1 point requires ES-3. |
| **E2** | ES-1 | Cavalry: plains 500→**150**, summed plains+stables cap **~1,500**. Artillery: re-key + rate **~80**, summed cap **~600**, one commit. **Pool-cap scaling: CUT from pass 1. Infantry regen: keep flat (intended rubber band, §5.1).** | Two cuts; rates concur. |
| **E3** | ES-3 | Base 5→**8**; force limit `= base + k×regions` (suggest base 60k, k ≈ 2.5k/region for France-scale sanity — escalated numbers, tune in the band test); over-limit ladder 1.5×/2.0× — **and promoted to pass 1 (§4).** | Position changed; numbers concur. |
| **E4** | EC-5 | Option B magnitudes concur (~−30g/coastal member region, Britain bite −40g/member cap ~400) **+ the subsidy-coupling rider + the activation surface (§7.1–7.2).** | Two riders. |
| **E5** | ES-7 | **Full-income redirect (delete the 0.30 skim constant — §3).** REP_STEP 40 provisional, validated against measured win counts; CAP 300 concur; fee ~200 concur; EROSION_MAX −3 concur; SHORTFALL_PER_POINT 50 concur; **grace 1→2**; **grant scope = conquered (non-homeland) provinces, estate exempt from occupation cost (§6.1)**; confer_title stays pass 2. | Headline change + three refinements. |
| **E6** | Bankruptcy mercy | Extend halving to ES-2 occupation + ES-3 surcharge; ES-7 floors at 0 structurally — **concur.** | None. |

---

## 9. Completeness (no-silent-caps)

Every recorded decision in §0.5/§0.6/§0.6.6 and every Appendix-A candidate received an explicit verdict (§2 table; ES-5/ES-6/ES-9 via rows 14–15/22). The two dissents are §3 (E5 scale) and §4 (ES-3 position); the two simplifications are §5.1 (pool caps, infantry flat) and §6 (ES-2 shape); expansions are §7 and are recommendations to their respective owners, not new unowned rows. July-9 audit economy escalations: none existed to triage. Per §0.7.3, if the user accepts any change here, §0.6 must be updated to match **before** the build session.
