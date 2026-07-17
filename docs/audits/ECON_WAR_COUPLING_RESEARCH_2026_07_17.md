# Economy ↔ War Coupling — Research Memo + Gate Record (July 17, 2026)

> **Pass 3 of the economy.** Pass 1 = the July-9 Economy Revisit (EC build); pass 2 = the
> July-14 Combat-Overhaul Phase 4 (EC-U1/U2/U3 + the EC-U1 reversal). This pass answers
> the July-17 playtest defect: *France's treasury snowballs monotonically and net income
> RISES while the army is destroyed, marshals are lost, and Britain occupies core home soil.*
>
> **Authority:** the user delegated the design gate July 17, 2026 — "you have approval to
> make decisions; consider history, other games, new ideas, balance numbers, all avenues" —
> with ONE binding steer: **"losing soldiers costing less at large makes sense, because
> salaries — but there are maybe expenses or balances missing."** Upkeep therefore stays
> billed on live fielded strength (the reversed EC-U1 stands); this pass adds the MISSING
> expenses and income-side couplings. This §3 is the gate record; the build lands the same
> session.
>
> **Research provenance:** 11-agent grounded workflow (7 code verifiers + 3 design agents +
> synthesis, ~1.29M tokens), every load-bearing claim re-verified firsthand against master
> before decisions. Two synthesis errors caught and corrected in §1/§3 (boot-WE seeds are a
> smoke-preset artifact, not a campaign boot; the flat WE-rate drain is Austria-incompatible).

## §1 Root-cause ledger (verified, ranked by contribution to the playtest table)

| # | Cause | Evidence |
|---|-------|----------|
| 1 | **Enemy presence on owned soil costs the owner nothing.** Income counts every controlled region's full effective income; no marshal-presence term exists anywhere. Stability even keeps GROWING +5/turn under hostile occupation. Moore standing in Orleanais = 0 gold, 0 stability, 0 damage to France. | `world_state.py:3817` income loop; `world_state.py:4437-4457` unconditional stability growth |
| 2 | **Surcharge evaporation amplifies attrition savings.** Of the 2,630→496 upkeep fall, ~1,100 (52%) is the ES-3 over-limit + Grande Armée surcharges vanishing as the army shrinks below 140k/limit — casualties shed the most expensive soldiers first. (Live-strength billing itself is INTENDED — user steer + `test_economy_upkeep_fielded_strength.py` — untouched.) | `world_state.py:3971-3990`, `:141-142` |
| 3 | **Zero recurring cost of being at war.** Every sink is opt-in (recruit/build/endow/commission); passive play even earns +25g per unused admin AP. War exhaustion exists but has NO economic coupling, and structurally cannot reach France: the per-turn loop skips France (`coalition.py:1680-1682`, +8/turn for AI at war with France only) and the battle branch has no "France loses as defender" arm (`combat_executor.py:1523-1563`) — the exact playtest shape accrued France nothing. | `coalition.py:1680-1690`, `combat_executor.py:1523-1563`, `world_state.py:4183-4191` |
| 4 | **Peace terms are economy-blind.** AI offer sizing = `min(2000, 500 + 50×war_age)` — never reads either treasury. The player-authored ask caps at `CONCESSION_BASELINE_GOLD_FLOOR` (300). Britain at +24 war score against a 61k hoard extracts 600g (~1%). | `ai_diplomacy.py:1903-1905, 2025-2048`; `settlement_baseline.py:1654-1668` |
| 5 | **Casualties never touch manpower pools** — unconditional regen toward caps; the only combat write is a credit. Removes the reserve pressure that would force expensive (war-priced ×3) rebuilding. | `world_state.py:4024-4049` |

Also verified: the two levers a "invasion wrecks income" mechanic needs **already exist** —
stability tiers gate income to 0/25/75/100% (`region.py:258-267`) and `war_damage` cuts up
to −50% (`region.py:286-311`) — but only battles write them.

## §2 Design grounding (history + comparative games, condensed)

- **Contributions/requisitions:** Napoleonic armies lived off occupied territory ("la guerre
  doit nourrir la guerre") — an enemy army standing in your province meant your tax revenue
  was being eaten in place. The occupied province paying its OWNER normally (the current
  code) is the least historical possible model.
- **Crushing indemnities:** Pressburg (1805) and Tilsit (1807) levied indemnities measured
  in significant fractions/multiples of the loser's ANNUAL revenue; Prussia's post-Tilsit
  extraction ran to several times its yearly state income. Austria's four lost wars ended in
  the 1811 state bankruptcy. A 1%-of-treasury indemnity is not a peace term, it is a tip.
- **War chests:** wars were financed from accumulated coin (France's Domaine Extraordinaire
  — already in-game as dotations — was built FROM extraction; Austria/Prussia burned their
  chests and then their credit). A long war consuming the hoard is the historical norm.
- **Materiel:** rebuilding after Ulm/Jena cost fortunes in guns, horses, and stores beyond
  soldiers' pay — capital destruction, not salary.
- **EU4/Vic pattern fit:** occupation suspending income to the owner (EU4) is the single
  highest-impact, cheapest-fit mechanic for this defect; war exhaustion as an economic drag
  (Vic/EU4 war taxes inverted) second; devastation third (already ~exists as war_damage).

## §3 GATE RECORD — the decided design (built this session)

**Shape rules honored by all five slices:** boot-byte-neutral by construction (presence-,
WE-, battle-, and settlement-gated — all zero at the fresh 1805 boot); GR5 symmetric through
the shared income/battle/settlement seams; GR8 (iterate marshals, never regions, in hot
paths — the presence map is one pass over `world.marshals`); **zero new serialized fields**
(WE, stability, war_damage already serialize; materiel/indemnities are instant flows);
every recurring term a signed, named Net ledger component (EC-U2 recipe).

### EC-W1 — "Contributions of War" (presence disrupts income)
A controlled region with ≥1 enemy-nation marshal present (`strength ≥ DISRUPTION_MIN_STRENGTH
= 1000`, gated strictly on `is_at_war(region.controller, marshal.nation)`) yields **nothing**
to its owner that turn: its effective income is withheld as a new signed **"Contributions"**
Net component; an endowed estate on that soil collects nothing (the household's satisfaction
falls — the marshal-anger interlock is intended and tested); ES-2 occupation cost and EC-U2
infrastructure stay billed (being contested relieves nothing). While so occupied the region
takes **−2 stability/turn instead of any growth** (`DISRUPTION_STABILITY_DRAIN = 2`, floor 0)
— multi-turn occupations degrade income tiers and linger after liberation (recovery via the
existing +5/turn). **Suspension, NOT transfer:** the invader consumes it in place; crediting
the occupier's treasury would accelerate the winner's snowball — extraction-to-invader is
deferred as EWC-D1. Boot: the only case is historically perfect — Mack's Austrian army
stands in Bavarian Swabia (the actual Sept-1805 occupation), Bavaria +474 → ~+324, solvent;
France/Austria/Britain/Prussia boot numbers byte-identical.

### EC-W2 — "The War Effort" (war exhaustion gains teeth, symmetrically)
(i) **WE symmetry:** France enters the existing WE system — +8/turn while at war with anyone,
−5/turn decay at peace (same constants as the AI loop, GR5), and the missing battle branch is
added (France loses as defender → France accrues `casualties//1000` capped 20, completing
"the loser accrues" for every France-involved battle). `cleanup_war_end` gains a multi-war
guard: a nation's WE resets to 0 only when it has NO remaining active wars.
(ii) **The drain:** a new signed **"War Effort"** Net component =
`int(max(0, treasury) × WE / WAR_EFFORT_DIVISOR)`, `WAR_EFFORT_DIVISOR = 2500` (WE 200 → 8%
of the hoard per turn; WE 50 → 2%), computed on the pre-income treasury via ONE helper so
report = ledger = applied. **Why treasury-fraction, not the flat WE×rate the synthesis
proposed:** Austria's binding +18 boot margin means any flat per-turn war cost > 18 puts the
AI major in permanent wartime deficit; a fraction of a positive treasury attacks the actual
defect (the passive hoard), costs a poor nation ~nothing, can never push anyone negative by
itself, and self-limits as the chest drains. The player sees it as the war consuming the war
chest — dodgeable only by SPENDING the gold on the war, which is the design working.

### EC-W3 — "The Butcher's Bill" (materiel of the fallen)
Every resolved battle charges each side a one-time `int(own_casualties × MATERIEL_RATE)`,
`MATERIEL_RATE = 0.05` (50g per 1,000 casualties — guns, horses, and stores lost with the
men; ≈6 turns of those soldiers' salaries). Deliberately BELOW the war recruit price
(60g/1,000) so replacing men still costs more than replacing kit (hierarchy pinned). One-time
flow outside Net (plunder-gold precedent — no NET_GOLD_COMPONENTS churn); surfaced on the
battle report and both sides' treasuries. Makes battle itself an economic event.

### EC-W4 — "Peace with Teeth" (indemnities priced to the purse)
AI settlement offers (`_settlement_offer_build_terms`) rescale:
`amount = min( int(loser_treasury × 0.15) + |war_score| × 40 + 500 + 50 × war_age,
int(loser_treasury × 0.40) )` — the old flat 2,000 cap is replaced by the
40%-of-the-purse cap (a court can no longer be dunned past what it can plausibly pay, and a
rich loser can finally be dunned at all). Playtest turn 17: Britain's demand on France
becomes ≈9,900g (~19% of the hoard), not 600g. The player-authored ask floor (300) scales
the same way: `max(300, int(court_balance × 0.25))`, still capacity-capped by the existing
`court_balance − RESERVE` math. Direction logic (AUD-c) unchanged; both directions GR5. The
exact-amount test pins are consciously re-blessed.

### EC-W5 — fix-in-passing pair (verified real)
(a) **Plunder gold GR5 violation:** AI auto-plunder pays ×1.0 base income
(`world_state.py:2966`) vs the player's ×1.75 (`combat_executor.py:5631`) — aligned via one
shared constant. (b) **Economy report net omits infrastructure**
(`economy_executor.py:83-84`) — the treasury report's net ≠ the applied net whenever
structures exist; fixed + rendered, with the new components threaded through the same report.

## §4 Numbers check (playtest counterfactual, A+B+C live; D at settlement)

| Turn | Observed net | EC-W1 | EC-W2 (WE→drain) | EC-W3 | New net ≈ | Treasury ≈ |
|-----:|-------------:|------:|-----------------:|------:|----------:|-----------:|
| 1  | +2,107 | 0 | 0 (WE 0) | 0 | **≈+2,105** | 800 — the boot INSTANT is byte-identical (E1 measures the fresh world); the first advance's WE tick (+8) charges int(800×8//2500)=2g |
| 6  | +2,590 | 0 | ~−240 (WE≈55) | ~−200 | **≈+2,150** | ~11k |
| 12 | +3,461 | ~−200 | ~−1,040 (WE≈118) | ~−300 | **≈+1,900** | ~22k |
| 17 | +3,369 | ~−450 (Orleanais+1) | ~−1,790 (WE≈160) | ~−350 | **≈+780** | ~28k |
| 20 | +3,300 | ~−450 | ~−2,150 (WE≈185) | ~−300 | **≈+400 and falling** | plateau ~29k |

The curve inverts: net now declines as the war worsens, the hoard plateaus near 29k instead
of 61k, and Britain's settlement demand against it is ≈6.5k (~22%) instead of 600g. Boot:
every E1 anchor byte-identical (WE dict boots empty — the Britain-60/Prussia-35 seeds the
research flagged live in the settlement SMOKE presets, `world_state.py:1031-1032`, not the
campaign boot); Bavaria is the sole boot delta (EC-W1, +324 > 0, pinned). A winning war
stays profitable (short, decisive, low WE, indemnities flowing IN) — the Napoleonic shape.

## §5 Deferrals (owned — GR9) and cuts

| ID | Item | Owner / landing |
|----|------|-----------------|
| EWC-D1 | Occupier-side extraction (contributions credited to the invader's treasury, on the EC-W1 substrate) | next econ tuning gate; one constant + component; test = transfer sums |
| EWC-D2 | Casualty→manpower-pool drain (reserve pressure; root-cause 5) | Pre-EA Balance Pass — needs an AI-recruit-rung impact study first |
| EWC-D3 | Captured-marshal ransom demands (ties the W6-7 capture fates) | future diplomacy/drama gate |

**Cut with reasons:** loans/inflation/bankruptcy-spiral (anti-sandbox); a separate
battle-devastation slice (battles already write war_damage `combat_executor.py:1106`);
home-front stability drag keyed on war score (double-dips EC-W2 through a less legible
channel); the synthesis's flat `WE × 5` drain (Austria +18 incompatible — superseded by the
treasury-fraction form); recurring-rails indemnity restructuring (lump + existing recurring
presets suffice).

## §6 Build landing record (July 17, 2026 — same session)

All five slices landed as decided in §3, zero deviations of substance:

- **EC-W1:** `WorldState.get_disrupted_regions()` + the disrupted branch in
  `calculate_turn_income` (income stays GROSS; `contributions` key; per-region
  `disrupted`/`contributions_cost` detail; ES-2 occupation + infrastructure still
  bill) + the `process_stability_growth` −2 branch + the `get_estate_income`
  interlock (a disrupted estate feeds nobody). Constants
  `DISRUPTION_MIN_STRENGTH=1000` / `DISRUPTION_STABILITY_DRAIN=2`.
- **EC-W2:** the coalition §10a France arm (+8/−5, `get_nations_at_war_with`
  keyed); the missing France-defender-loses battle arm in BOTH combat copies
  (`combat_executor._post_combat_pipeline` + the world_state auto-charge block);
  `calculate_war_effort_cost` single source (`WAR_EFFORT_DIVISOR=2500`), ridden by
  `calculate_turn_income` → every consumer. The R49 multi-war peace guard already
  existed (`diplomacy.cleanup_war_end`) — only its stale docstring was fixed.
- **EC-W3:** pipeline step 13b + the auto-charge mirror (`MATERIEL_RATE=0.05`,
  Europe-scoped, display-name-humanized "[Materiel]" line threaded to the attack
  + charge messages; one-time flow outside Net).
- **EC-W4:** `_settlement_offer_build_terms` rewritten (payer-treasury read via the
  new `world` param; constants `SETTLEMENT_OFFER_TREASURY_FRACTION=0.15` /
  `MAX_TREASURY_FRACTION=0.40` / `PER_WAR_SCORE=40`; empty chest → white peace;
  no-world fallback preserves the legacy flat sizing) +
  `CONCESSION_BASELINE_TREASURY_FRACTION=0.25` on the player-ask baseline.
- **EC-W5:** plunder single source `world_state.PLUNDER_GOLD_MULTIPLIER=1.75`
  (AI branch aligned; combat_executor class attr re-exported for test compat);
  the treasury report's net now includes infrastructure + renders its line.
- **Threading:** both new components through `process_income_phase`,
  `ledger._build_economy`, the `NET_GOLD_COMPONENTS` registry, the treasury
  report (disrupted provinces named; WE named on the War Effort line), the
  morning-dispatch projection + keys, the turn-end message + `turn_end` event,
  and `strategic_ledger.gd` (the session's one `.gd` touch — headless load-check
  `parse_ok=true can_instantiate=true`, full parse harness exit 0, report
  regenerated).
- **Tests:** `tests/test_econ_war_coupling.py` (33 — disruption gates/GR5
  mirror/estate interlock/stability bleed/boot pins incl. the Bavaria case/war
  effort formula + accrual arms/materiel both-sides + N1 + hierarchy pin/plunder
  parity/report-net fix/the curve-inversion acceptance) + EC-W4 re-blessed pins
  in `test_settlement_incoming_offers.py` (+1 purse-cap test). Full suite
  **13,663 passed / 3 skipped** (was 13,627/3), ruff clean.
- **Research workflow:** 11 agents / ~1.29M tokens; synthesis corrections
  recorded in the header.

### §6.1 Pre-push adversarial review (6-area find→verify, 7 agents / ~1.01M tokens)

Initial verdict **NO-SHIP** — 10 confirmed findings (6 refuted). Dispositions,
all resolved before commit:

- **#1 HIGH (FIXED):** the France WE tick + both new battle arms lacked the
  Europe gate — the legacy fixture world BOOTS at war, so legacy France
  accrued WE (empirically +24 over 3 advances) and its pinned infantry regen
  drifted (N1 breach). Three gates added; legacy byte-behavior restored and
  pinned (`test_legacy_world_france_we_tick_gated`).
- **#2 MED (FIXED):** elimination ends wars without `cleanup_war_end`, so WE
  lingered ~30 decay-turns after the last belligerent fell — the R49 rule is
  now mirrored in `_eliminate_nation` (pinned).
- **#3 MED (RECORDED AS INTENDED + PINNED):** the pre-existing WE→infantry-
  regen penalty (100 WE = halved / 200 = the 1,000 floor, `world_state.py
  get_manpower_regen_rates`) now reaches France. Kept deliberately: it is the
  manpower half of war-weariness, symmetric with the AI nations that always
  had it, self-healing at peace — and it delivers part of EWC-D2's reserve
  pressure through an existing dial. Pinned
  (`test_we_infantry_regen_coupling_recorded_as_intended`).
- **#4 MED (FIXED):** materiel was billed but not SHOWN on garrison assaults
  (both collapse/hold paths discarded `pipeline_out`) and the auto-kill
  message — all three sites now append the "[Materiel]" line (shown=applied).
- **#5 MED (ROUTED → BUG_FIXES EWC-F1):** a winning-arm offer's purse-priced
  indemnity can score as accepting-side harshness and stage un-ratifiable —
  pre-existing saturation at the old cap; step-down fix designed, owned.
- **#6 MED (FIXED):** the executor AUTO-ADVANCE turn banner omitted
  contributions/war_effort (+ the pre-existing infrastructure gap) from its
  net, and `main.gd`'s banner rendered neither line — both fixed (+ source
  pins).
- **#7 MED-LOW (ACCEPTED, pre-existing pattern):** the turn-end report
  recomputes components post-turn while Net is the true delta ("Other"
  absorbs drift) — the same F6 tradeoff occupation/dotations already live
  with.
- **#8 LOW (ROUTED → BUG_FIXES EWC-F2):** rente face can size against a
  disruption-zeroed estate income at grant time.
- **#9 LOW (FIXED):** vassal tribute now skips disrupted vassal provinces in
  BOTH the processor and the ledger mirror (the lord cannot tithe revenues
  the invader eats; pinned).
- **#10 bundle:** (h) **FIXED** — the player-ask baseline retries at the
  pre-EC-W4 floor when the purse-scaled ask fails acceptance (a marginal
  rich court yields 300g again instead of 0); (c) **FIXED** — §4's turn-1
  wording corrected (boot instant byte-identical; first advance ≈2g);
  (d) **RECORDED** — the plunder ×1.75 parity applies on the legacy world
  too (a GR5 correctness fix on the same choice, no legacy pin broke);
  (a/b/e/f/g/i) accepted as cosmetic/pre-existing, noted here.

Post-fix: full suite re-run green, ruff clean, `main.gd` re-verified through
the committed Godot parse harness (exit 0).
