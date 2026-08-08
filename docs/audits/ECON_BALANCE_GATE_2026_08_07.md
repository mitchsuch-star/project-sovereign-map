# THE ECON BALANCE GATE — ROADMAP position 5 (row EC-P3) — August 7, 2026

> **Authority.** The user delegated this gate August 7, 2026: *"do econ pass and make it
> actually engaging and good — you can make decisions, consult history, other game
> concepts, and be creative… economy shouldn't go crazy unless you are doing very well
> and stable, even if we need new modifiers… abstraction is fine, even good — this is
> not a spreadsheet game… we should abstract England's relative wealth — colonies as
> a modifier."* Design authority for shapes AND starting numbers is Fable's under that
> grant; every number below is a blessed STARTING value in the standing in-band idiom
> (retune inside the band = no new gate; a SHAPE change escalates).
>
> **Provenance.** A 7-agent research fleet (~1.6M tokens: full gold-pipeline map ·
> 2×40-turn treasury trajectory probes on two seeds · the threat-bar map · a
> constraints/pin ledger · the sinks inventory · the Britain/colonial decomposition ·
> a history+genre anti-runaway brief), every load-bearing number ⊕-measured against
> master `a6442e2`. Reports archived in the session scratchpad; the decisive tables
> are reproduced below. **This §gate record is authoritative; the landing record is
> appended as §8 when the build closes.**

---

## §1 The measured disease (what this gate is FOR)

1. ⊕ **Treasury runaway is a PEACETIME disease, and it is linear, not superlinear.**
   40-turn ambient probe (seed `historical`): Prussia — at war with nobody — gains a
   constant **+298/turn for 30+ straight turns** (800 → 10,228, unbounded). Spain gains
   **+1,010/turn from the moment it makes peace** (700 → 29,035) and **finishes the run
   richer than France**. The only treasury-coupled brake in the whole game is the EC-W2
   War Effort tax (`treasury × WE // 2500`), and WE decays −5/turn at peace — the brake
   is switched off exactly when a nation is doing well.
2. ⊕ **At war the brake is condition-blind.** Every warring nation converges to the same
   fixed point `T* = net × 2500 / WE` regardless of how the war is GOING: collapsing
   France (army 189k→31k) plateaus at ≈24k while conquering Austria (income ×3.4)
   oscillates at ≈11k. "Doing very well AND stable" is not what the fixed point rewards —
   merely "at war long enough."
3. ⊕ **The audited 44× (CA8-D1) is the climb to that plateau with nothing to spend on:**
   88% of income unspendable, the lifetime conquest-free sink 13 building slots
   (3,250–5,200g), the bench exhaustible, and a market on a `city` **−3/turn forever**
   (+37 gross vs the flat 40g EC-U2 bill).
4. ⊕ **The threat bar cannot show anything** (CA8-D5): boot 85 is AUTHORED
   (`europe_1805.json:66`), cap 100, and a fighting France re-pins it to 91–97 because
   `battle_win` credits **defensive** wins +3 against a decay cap of 3 — so
   `military_establishment` (+1) and every future term lands inside clamp-noise.
5. ⊕ **Britain is the one major that does NOT run away** (oscillates 1.7k–6.2k across 20
   turns — the paymaster floor, treasury-stepped subsidy tiers, and the WE fraction
   self-regulate it), but its purse is a fraction of its historical weight
   (trade_dominance 300 → ⊕184/turn at boot closure) and Spain/Holland/Portugal have
   **zero** overseas representation — blockading Spain costs it 100g of diplomatic
   trade; the 1804 silver-seizure lever does not exist.

## §2 The design principle (the user's sentence, made mechanical)

**The treasury becomes a CONDITIONAL fixed point.** Prosperity requires the state to be
in order; the ceiling rises with how well you are actually doing (rate falls AND net
rises with real success), and collapses when the empire wobbles. Golden peace — stable,
victorious, gripped — pays a token rate and MAY grow genuinely rich (the user's own
carve-out, implemented literally). Genre anchor: HOI4's conditional-fraction logic
applied to EC-W2's own treasury-fraction base at Solium-Infernum abstraction level —
ONE rate, named condition terms, no chores, one Berthier sentence. History anchor: the
franc germinal (stability = cheap money) vs the state whose suppliers price to its
condition; la guerre doit nourrir la guerre; Pitt's gold.

## §3 DECISIONS

### EB-1 — "THE CHARGES OF EMPIRE" (the spine; absorbs EC-W2's War Effort)

`calculate_war_effort_cost` generalizes to **`calculate_state_charges(nation)`** —
one rate over the existing divisor, each term a named condition reading:

```
rate = WE                                   (existing 0–200 war-exhaustion term)
     + CROWN_BASE      30   always          "the household, the pensions, the ministries"
     + WAR_RATE        50   any active war  "the war establishment" (bites turn 1, no WE ramp wait)
     + ILL_RATE        75   any war with side war-score < −20        "the wars go ill"
     + UNREST_RATE     75   ≥1 owned province disrupted or stability ≤ 50   "the interior is restless"
     + GRIP_RATE       50   get_imperial_grip(nation) < 70           "the Emperor's grip falters"

charge = int(max(0, treasury − HOARD_FLOOR) × rate // 2500),   HOARD_FLOOR = 2000
```

- **The component is RENAMED**: dict/API key `war_effort` → **`state_charges`**, ledger
  line "War Effort" → **"Charges of Empire"** — required for honesty, because the line
  now fires at peace (CROWN_BASE). Full EC-U2 recipe rethread (income phase, ledger +
  `NET_GOLD_COMPONENTS`, treasury report, dispatch, `strategic_ledger.gd`, `main.gd`
  banner). The named terms ride the breakdown so the tooltip explains itself.
- **Boot byte-identical by construction**: max boot treasury anywhere is Britain's
  exactly 2,000 = the floor; every nation charges 0 on the boot turn. Austria's +18
  wall untouched (a fraction of a positive chest above a floor cannot touch a flow
  margin and can never push a treasury negative). No bankruptcy mercy needed —
  self-limiting, the EC-W2 argument, pinned.
- **Computed on the pre-income treasury via the ONE helper** (shown = applied), all
  nations, same seam (GR5) — ⊕ it finally caps the Ottoman's +1,808/turn idle wagon too.
- **Conditional fixed points** (net ≈ 2,000): golden peace (rate 30) → τ≈83 turns,
  effectively unbounded — *allowed, that is the blessing*; ordinary expansion war
  (WE ~100 + WAR + UNREST) → **≈ 20k**; collapse (WE 200 + ILL + UNREST + GRIP) →
  **≈ 11k and falling with net**. The July-17 shape (+7,500% while Britain stood in
  Orleanais) now bleeds through UNREST + ILL from the first turn of trouble.
- **EC-W2 pin re-bless (conscious):** `test_econ_war_coupling.py`'s WE-only formula
  and CurveInverts staging re-pin to the new composition; `WAR_EFFORT_DIVISOR = 2500`
  and the treasury-fraction SHAPE are unchanged.
- **Why this does not re-litigate the EWC cut list:** the cut was a stability drag
  *keyed on war score* (double-dips WE) and a *flat* WE×rate drain (Austria-incompatible).
  This keys on the state of the REALM (stability/territory/grip), stays a
  treasury-fraction, and ABSORBS the WE term into one line instead of stacking beside it.
- Berthier: *"The chest bears the Empire's charges, Sire — light while France stands
  stable and victorious, heavy while the interior seethes or the wars go ill."*

### EB-2 — "THE WEALTH OF NATIONS" (the user's colonies-as-modifier, Shape A)

Authored **`overseas_income`** on `navies` rows (validator clamp [0, 1200]; the
validator is the gate, runtime never re-clamps): **Britain 500 · Spain 250 ·
Holland 150 · Portugal 150 · France 0** (France's "overseas" arm is continental
extraction — EB-5, matching history). A new **positive signed Net component
"Overseas Trade"** (NOT folded invisibly into income — the NV-5 decoration lesson).
Modulation, all derived, zero new serialized fields:

- **Dominance holder** (Britain, via the existing `trade_dominance_nation`):
  `× (1 − closure)`, floor ×0.4, **×0 under blockade** — the same rules the authored
  `trade_dominance` already obeys. `trade_dominance: 300` itself is untouched (its
  184-family pins stand).
- **Non-holder colonial powers**: **×0 while blockaded** · **×0.25 while at war with
  the dominance holder** (the RN sits on the sea lanes — the 1804 frigate seizure,
  the post-Trafalgar silver collapse, one derived condition) · ×1.0 otherwise.
- ⊕ Boot deltas: Britain **+307** (500 × 0.6154 closure) · Spain **0** (blockaded) ·
  Holland **0** (blockaded) · Portugal **+150** (at peace — conscious, solvent) ·
  France **0**. Britain's boot-turn subsidy stays OFF (pre-income treasury still
  exactly 2,000 — the NA-3 re-bless holds).
- **Subsidy co-tune (the blessed-but-never-landed E4 rider (i))**: paymaster tiers gain
  a fourth rung — 200 / 300 > 4k / 400 > 8k / **500 > 15k**, `AGENDA_SUBSIDY_CAP`
  400 → **500**. Pitt's gold flows at historical relative scale, and the counterplay
  attacks the SOURCE: closure 0.38 → 0.80 strips ~53% of Britain's pool AND +3 WE/turn
  AND drops the tier. The Continental System becomes an economic weapon, not only a
  WE clock.

### EB-3 — WHAT GOLD BUYS (CA8-D1 answered and closed)

1. **Tier-scaled infrastructure upkeep**: `EUROPE_INFRASTRUCTURE_UPKEEP` flat 40 →
   **per region tier: capital 40 · major_city 30 · city 20** (watchtower rides its
   region's tier). A market on a city flips −3 → **+17/turn**; every one of the 13
   slots becomes a rational want. EC-U2's sink intent is not lost — the Charges of
   Empire replace it as the structural drain, and buildings move from tax to want.
2. **IGR-X9 DECIDED — a ruin bills nothing.** Damaged structures (and damaged
   watchtowers) are exempt from infrastructure upkeep until repaired; repair (150g)
   restores function AND the bill. Securing a built province is no longer strictly
   dominated by razing at every multiplier; the published razing pin flips WITH the
   fix (its docstring now points here), and the plunder acceptance test is re-run as
   the judge — **the dissent counter is NOT spent unless it fails at ×4 post-slice**
   (then that is attempt TWO → option (b), per the five-place dissent).
3. **XR-4**: the endow confirm gains a pre-flight line when the estate currently
   yields 0g, plus the recovery clause ("revenues recover as stability does").
4. **The recorded answer to "what does gold buy after turn 6":** the Marshalate bench
   (30,000g of people with drama payloads) · naval keels (≤800g/turn standing want) ·
   diplomatic instruments (DP-priced, 1,000–1,400g one-shots + standing sponsorships) ·
   vassal subsidies/investment · rentes and estates · war-priced recruitment — all now
   under a treasury that **leaks when the empire wobbles**, so holding gold is a choice
   with a price instead of a default with none. **ES-4 Province Development remains the
   pass-2 anchor sink at its own EC-2 pass-2 gate** (the Q5 fixed-point argument
   survives: a stock sink cannot fix a stock disease; EB-1 fixes the stock, ES-4 can
   later serve the flow-engagement side).
5. **Scored and NOT built, with reasons:** a gold→manpower remount program (undercuts
   the blessed E2 scarcity — cavalry is the bottleneck BY DESIGN, and history agrees:
   Napoleon could not buy horses after Russia) · C2 literal Domaine-Extraordinaire
   second ledger (a second currency on screen = the spreadsheet direction; its
   function — paying the marshalate — already ships as estates/rentes) · C5 Invalides
   pension roll (subsumed by CROWN_BASE) · C4 "The Sacre" ceremonial verb (a real
   candidate — gold → grip recovery → lower rate, escaping the Q5 objection by moving
   the RATE not the stock — but it is a new 12-step verb brushing the Victory pass's
   scope; **homed as a named candidate at the Victory & Objectives gate**, positions
   12–13).

### EB-4 — THE THREAT BAR GETS HEADROOM (CA8-D5 answered and closed)

The gate question was *"does anything new need to be measurable on a bar that boots
near its ceiling?"* — the answer is YES, and the fix is option (d) of the threat map
plus one credit exemption:

1. **Authored boot threat 85 → 70** (band [80,90] → **[65,75]**) in `europe_1805.json`.
   Boot stays > 60 (P3 shelter asks, hegemony-pressure motive, the war-declaration
   objection gates all unchanged) and drops below INSTANT 80 (irrelevant at boot — the
   Third Coalition is authored-active, not threshold-formed).
2. **The dead territorial gates recenter to the 126-province map**: `region_control`
   thresholds 60/70/80% → **30/40/50%** (38/51/63 provinces) at the same +1/+2/+3 —
   a conquering France now stays high HONESTLY instead of by clamp.
3. **Defensive battle wins no longer feed the alarm**: the `battle_win` +3 credit fires
   on ATTACKER-side wins only (both combat copies); `decisive_victory` keeps both arms
   (a crushing field victory alarms Europe whoever started it). Europe fears the
   conqueror, not the defender — and the quiet-France floor stops being unreachable
   during a defensive war.
4. **Mirror honesty rider**: with boot 70 the §3.5 mirror would read "coerce" while
   the Third Coalition is literally at war with France — the mirror gains an arm: an
   active anti-France coalition AT WAR forces the "fight" rung. (`intent.py`;
   `test_ai_intent_layer` re-pins consciously.)
5. Consequence: `military_establishment` (+1/turn at >40% share) and every future
   contributor become measurable in play; the bar moves through its tiers during a
   campaign instead of residing at 91–97.

### EB-5 — THE DOCKET CLOSURES

1. **EWC-D1 BUILT — "Requisitions of War"** (la guerre nourrit la guerre, the owed
   half): each region a nation disrupts (EC-W1's own predicate) pays the DISRUPTOR
   `int(0.25 × base income_value)`/turn as a new positive signed component
   **"Requisitions"** (strongest-presence nation when multiple disruptors share a
   region). The July-17 deferral reason — "crediting the winner accelerates the
   snowball" — is structurally dissolved by EB-1: extraction lands in a chest taxed
   at WAR_RATE + WE while the war lasts. ⊕ Boot delta: Austria +37 (Mack in Swabia —
   the historically exact case), consciously re-blessed; every other boot number holds.
2. **EWC-F2 FIXED**: `get_estate_income` gains `ignore_disruption` for
   `compute_rente_face` ONLY (a one-turn hostile presence at grant time no longer
   locks an oversized pension); satisfaction display keeps the disruption rule. The
   two estate-second-pass face pins flip consciously.
3. **XR-4 / IGR-X4 residuals**: XR-4 lands in EB-3; IGR-X4's AI half was landed
   July 31 (the windfall re-base covers both sides) — row closed.
4. **The plunder dissent**: not touched, re-verified post-slice (EB-3.2).

## §4 Blessed starting numbers (in-band tunable; SHAPE changes escalate)

| # | Constant | Value | Band |
|---|---|---|---|
| B1 | `CROWN_BASE` | 30 | 20–50 |
| B2 | `WAR_RATE` | 50 | 30–75 |
| B3 | `ILL_RATE` | 75 | 50–100 |
| B4 | `UNREST_RATE` | 75 | 50–100 |
| B5 | `GRIP_RATE` | 50 | 30–75 |
| B6 | `HOARD_FLOOR` | 2000 | 2000 fixed (boot-neutrality anchor — raising it is a retune, lowering it below Britain's boot 2,000 is a SHAPE change) |
| B7 | `overseas_income` | Britain 500 · Spain 250 · Holland 150 · Portugal 150 | ±40% per nation; France 0 is a design pin |
| B8 | `OVERSEAS_WAR_FACTOR` (non-holder at war with holder) | 0.25 | 0.0–0.4 |
| B9 | subsidy tiers | 200/300>4k/400>8k/500>15k, cap 500 | tier boundaries ±50% |
| B10 | infra upkeep by tier | 40/30/20 | each ±10, ordering capital ≥ major ≥ city structural |
| B11 | `EXTRACTION_RATE` (requisitions) | 0.25 | 0.15–0.35 |
| B12 | boot threat / band | 70 / [65,75] | must stay in (60, 80) — the consumer-threshold window |
| B13 | region_control gates | 30/40/50% | ±5pp each, ordering structural |

## §5 The falsifiable acceptance test (the slice's judge)

On the 40-turn ambient probe (both seeds), post-slice:
1. **No nation grows unboundedly**: every nation's last-10-turn mean treasury delta
   is < 40% of its first-10-turn mean delta, OR its treasury is below 1.5× its
   measured conditional fixed point. (Kills the Prussia/Spain linear runaway.)
2. **Condition beats clock**: a staged collapsing France (the EC-W CurveInverts
   staging: WE 150, Britain on home soil, war score < −20) has a strictly LOWER
   fixed point than a staged prospering France (at war, winning, interior quiet) —
   the brake finally reads performance.
3. **The blessing survives**: a staged golden-peace France (no wars, all provinces
   stable, grip ≥ 70) pays ≤ 1.5% of treasury per turn — doing very well and stable
   MAY grow rich.
4. **Boot byte-neutrality**: every E1 boot anchor unchanged; the only conscious boot
   deltas are Britain +307 / Portugal +150 overseas and Austria +37 requisitions.
5. **The plunder acceptance test passes at ×4 unchanged** (the dissent counter stays
   at ONE of two).

## §6 Pin flips authorized in advance (each dated in-file at build)

EC-W2 formula/CurveInverts re-pins (EB-1) · `test_naval_blockade_cs` boot-solvency
extension (overseas) · paymaster tier pins (B9) · infra-rate pins + the plunder
break-even model + the razing pin (EB-3, the model is parameterized and re-derived) ·
boot-threat 85 pins ×6 + variance band + mirror rung (EB-4) · estate face pins
(EWC-F2) · **`BASELINE_SERIES` ONE conscious re-record with flip-experiment
attribution** (candidate causes: charges moving AI treasuries; overseas moving
paymaster timing; threat re-center moving coalition cadence — the experiment isolates
which; if more than one contributes, the record names them all with a per-cause flip).
M1–M7 expected byte-identical (the harness never runs the income phase) — recorded as
a fact about the harness; the behaviours are pinned directly instead.

## §7 Out of scope, recorded

ES-4 development (pass-2 gate) · "The Sacre" ceremony verb (→ Victory gate candidate) ·
EWC-D2 casualty→pool drain (Pre-EA Balance Pass, unchanged owner) · EWC-D3 ransom
(diplomacy/drama gate) · garrison-cap retune (measured: garrisons are gold-POSITIVE
today — detaching removes upkeep — so the cap is not an econ lever; the EC-3 row note
stands for a future garrison pass with its own design question) · any change to
upkeep-on-fielded-strength (user-ruled July 14, structural) · the AI +25 admin bonus
faucet (Q4's declared AP↔gold rate, kept) · **NV-D3/NV-D9** (the naval-econ deferral
residue EC-P3 carried — RE-HOMED to EC-2 pass 2's gate, which now owns them beside
ES-4/ES-7b; recorded in CLAUDE.md's open-gates line).

## §8 LANDING RECORD — BUILT August 7, 2026 (same session as the gate)

**Everything in §3 landed; zero new serialized fields anywhere in the slice.**
Suite **16,427 / 3** (+40 over the pre-slice 16,387; the new file is
`tests/test_econ_balance_eb.py`, 36, plus the re-blessed families) · ruff clean ·
golden corpus untouched (no parser change) · Godot parse harness EXIT=0 (42
scripts) · boot smoke 0 SCRIPT ERROR / 0 missing files.

- **EB-1 Charges of Empire**: `calculate_state_charges` + `get_state_charges_rate`
  (named terms) replace `calculate_war_effort_cost` — the `war_effort` key is GONE
  from every seam (`state_charges` everywhere; a named test pins the old seam's
  absence). Full EC-U2 recipe rethread: income phase, ledger + `NET_GOLD_COMPONENTS`,
  treasury report (rate + terms render even at charge 0 — the CA8-10 rule), executor
  auto-advance banner, meta end-turn, dispatch, `strategic_ledger.gd` (+ the terms
  tooltip line), `main.gd` banner. **Two rate-term wiring traps caught IN-SLICE and
  the lesson is coded**: the first cut imported grip from a wrong module path inside
  a try/except and called the war score with a wrong signature — both terms were
  silently DEAD; the excepts are removed (a condition term that cannot fire must
  fail loudly) and `test_the_ill_term_fires_on_a_real_stored_score` is the
  falsifiability guard. The ILL term reads `sum_stored_side_score` (the CA8-D2
  score-CONSUMING seam) — the live aggregate blew the G4 perf tripwire and the
  tripwire's catch is recorded here as the enforcement working.
- **EB-2 Wealth of Nations**: authored `overseas_income` (Britain 500 / Spain 250 /
  Holland 150 / Portugal 150; France none by design) on the navies rows +
  validator clamp [0,1200] + `naval.overseas_trade_income` + the boot-fleet copy
  (the record-copy miss was caught by the boot probe: the fleets store copies only
  known keys). Boot deltas measured exactly as gated: Britain +307, Portugal +150,
  Spain/Holland 0 (blockaded), France 0. Subsidy tier 4 (500 > 15k) + cap 400→500.
- **EB-3**: tier-scaled infrastructure (40/30/20 — a market on a city flips −3 →
  +17/turn) · **a ruin bills nothing** (damaged buildings + damaged watchtowers
  exempt until repaired — the IGR-X9 decision; the razing-dominance inverts) ·
  XR-4 (war_torn flag on reward options + the recovery clause in the endow result).
- **EB-4**: boot threat 70 / band [65,75] · region_control gates recentered
  30/40/50% **Europe-scoped** (the legacy 19-region fixture keeps 60/70/80 — the
  first cut would have switched a standing +1/turn ON for every legacy coalition
  test, caught pre-commit) · defensive `battle_win` credit removed (both combat
  copies; decisive_victory keeps both arms) · the mirror's coalition-at-war "fight"
  arm.
- **EB-5**: Requisitions (0.25 × base income to the strongest disruptor — boot:
  Austria +37 from Mack@Swabia, the historically exact case) · EWC-F2
  (`ignore_disruption` face computation) · the plunder acceptance test re-ran GREEN
  at ×4 (the dissent counter stays at ONE of two).

**`BASELINE_SERIES` re-recorded ONCE with a THREE-cause attribution verified by a
two-arm flip experiment** (record in `test_ai_intent_threat_migration.py`): the
authored boot (index 0 by definition) · the defensive-win exemption (Arm B: boot
restored alone still loses the sporadic +3s from index 5) · the econ components
(Arm C: boot AND credit restored still diverges — Britain's deepened purse crosses
the subsidy tiers earlier; Austria requisitions +37/turn). The tail now reaches 0
and STAYS: a quiet France finally decays to the honest floor, which the old bar
structurally could not do while France won defensive battles. M1–M7 untouched
(the harness never runs the income phase — a fact about the harness; the
behaviours are pinned directly).

### §8.1 THE REVIEW ROUND — a 44-agent find→2-refuter fleet took THIRTEEN
confirmed findings (24 raw), ALL FIXED same session (second commit):

- **[0] P2 — the ILL term read bare PAIR scores, not the war-level side score**
  its own comment and this record specify: a nation WINNING its coalition war
  still paid +75 because one pair lagged (probed live: war-level +15, term
  firing). Fixed to `get_side_war_score_for` (the war-instance resolver); the
  new discrimination test stages both directions — and its own first fixture
  had the stored-score ORIENTATION backwards (France|Russia stores France's
  OWN perspective), which is worth a sentence here because it is exactly the
  trap the production code fell into.
- **[1] P2 — shown ≠ applied on every solvent end turn**: both financial
  banners RECOMPUTED `calculate_turn_income` after the phase, so the Charges
  figure shown was priced on the POST-income chest (probed: applied 96 vs
  shown 104), the error silently absorbed into the meta banner's "Other"
  plug. `_advance_turn_internal` now caches the APPLIED per-nation results
  transiently (`_income_phase_results`, display cache, never serialized) and
  both banners prefer it; E2E pin quotes the banner string.
- **[12] P2 — pre-EB-2 saves would NEVER receive the colonial pool** (fleets
  round-trip verbatim; the scenario transform runs only at from_scenario).
  `from_dict` backfills MISSING `overseas_income` keys from
  `naval.OVERSEAS_INCOME_BACKFILL` (the IGR-E precedent), whose DRIFT PIN
  asserts it equals the scenario's authored values; an authored/modded value
  round-trips untouched.
- **[8] P2 — the defensive-win pin's combat_executor half was INERT**: the
  scrape anchored at the FIRST of the file's five `elif defender_won:`
  occurrences, 13,000 chars short of the removal site — re-adding the credit
  passed the pin. Re-pinned as a comment-stripped whole-file CALL-SITE census:
  every battle_win `add_threat` call in both combat copies is enumerated and
  must credit the ATTACKER.
- **[3] P3** — requisitions attributed to the strongest single MARSHAL, not
  the strongest NATION (two 5,000-man French corps lost to one 6,000-man
  Austrian): per-nation presence summed before the winner is chosen.
- **[2] P3** — the auto-advance banner's net omitted the Admiralty bill its
  meta sibling reconciles (90g overstatement on every wartime auto-advance at
  the naval boot): folded in + carried on the event.
- **[4] P3** — the XR-4 copy promised the WRONG recovery mechanism for a
  DISRUPTED estate ("recovers as stability does" while disruption drains
  stability −2/turn): the two 0g causes now carry different flags
  (`occupied` vs `war_torn`) and different sentences on all three surfaces.
- **[5] P3** — the dispatch `treasury_delta` was still hand-assembled (the
  CA8-10 class; omitted vassal tribute 712g + admin bonus at boot — the
  briefing and the ledger disagreed about the same turn): now reads
  `_build_economy`'s reconciled net; three older hand-formula pins re-pinned
  to the ledger identity.
- **[6] P3** — the Godot turn banner never rendered admiralty/blockade/other
  though the event carried them and Net included them (visible lines did not
  sum to the Net beside them): three renders added.
- **[9]/[10]/[11] P3 (test rigor)** — the recentered-gate test pinned source
  presence but no AMOUNTS (the +1/+2/+3 ladder, the ordering, and the
  per-nation arm are now pinned across three tests); the XR-4 estate test's
  `if estate in rows:` guard became a hard assert; the CurveInverts staging
  still encoded the RETIRED WE-only bound (passed by slack — this §6's
  "re-pin" claim was ahead of the code) and now derives its bound from the
  live rate composition.
- **[7] — the exploit lens returned CLEAN with computations on the record**:
  no charge-immune liquid gold park exists (every spend is a real sink;
  spend-to-floor is the design working — the chest converted to army/works
  is the point), requisition farming with commissioned corps is a wash
  against upkeep, and vassal tribute cannot capture a vassal's overseas pool
  (tribute reads province income only). Recorded so the trail shows they
  were checked.

Post-fix: suite **16,436 / 3** (+9), ruff clean, parse harness EXIT=0, boot
smoke 0 SCRIPT ERROR.

**§5 acceptance, measured on the re-run 40-turn probe (seed `historical`):**
1. *(no unbounded growth)* France **converges at 22.1k** (last-10 delta +163/turn
   vs first-10 +1,536 — the fixed point forming), Austria 13.4k, Russia 14.7k —
   PASS outright. Britain 22.0k sits at ~95% of its computed conditional fixed
   point (~23.3k) — PASS by the criterion's second arm. Prussia 12.6k and Spain
   38.8k pass the second arm (both far below 1.5× their conditional fixed points).
   **Honest note, not buried**: Spain — at TOTAL peace with the silver flowing,
   i.e. the blessed doing-very-well-and-stable case, literally — still
   accumulates fast (τ≈83 turns at the crown rate). If a future review finds the
   idle-neutral hoard too rich, the FIRST dial is `CHARGES_CROWN_BASE` 30 → up to
   50 in-band; the SECOND is an opulence band (a marginal rate above ~20k),
   which is a shape change and escalates.
2. *(condition beats clock)* pinned in `TestConditionBeatsClock` — the collapsing
   empire's ceiling sits strictly below the prospering one's at equal WE.
3. *(the blessing survives)* golden-peace France pays ≤1.5%/turn — pinned.
4. *(boot byte-neutrality)* France's boot net +730 and E1 absorption 0.5552
   byte-identical; the only boot deltas are the gated four.
5. *(plunder dissent)* untouched — the acceptance test passed at ×4 unchanged.
