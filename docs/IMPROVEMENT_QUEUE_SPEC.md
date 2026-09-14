# THE IMPROVEMENT QUEUE — row IQ

**Opened September 12, 2026 by user direction:** *"improve everything but win
conditions one by one — let the agents make decisions on how; start with a
comprehensive econ fix that finally makes it work better."*

**This file is row IQ's OWNING SPEC.** The queue's *routing* authority — which
row is taken next, and why — stays in `docs/STATUS.md` ▶ NEXT UP. This file
holds what STATUS cannot: the per-slice **landing records**, the **dissents**,
the **re-open conditions**, and the rulings taken under the row's standing
delegated grant. It exists because the row ran two slices without one, and the
debt was already compounding: SW-0 and SW-1 landed code and tests and touched
**zero** files under `docs/`, so there was nowhere canonical to record either,
and no reader could find out what had been decided except by reading two
commit messages.

> **⚠ SLICE IDS.** The first two slices were committed as `SW-0` and `SW-1`,
> which **collides with `docs/SEASONS_WEATHER_SPEC.md`**, where SW-0..SW-4 (+
> SW-V) are the Seasons & Weather slices and SW-2 is the *winter march bill*.
> **Every remaining IQ-1 slice uses `IQ1-n`.** The two that landed are NOT
> renamed: 49 of their 50 code sites already carry an `IQ-1 ` prefix, the one
> bare site is inside a file named `test_iq1_sw1_*`, the commit messages are
> immutable, and a rename would leave a permanent two-name history that is
> worse for a future `grep` than one recorded alias. The alias is:
> **IQ-1 SW-0 ≡ IQ1-0**, **IQ-1 SW-1 ≡ IQ1-1**. A cross-note is filed in
> `SEASONS_WEATHER_SPEC.md` so the incumbent owner knows.

---

## §0 — ROW IQ-1: "THE ECONOMY THAT BITES"

### §0.1 The row's contract

The contract is the `### IQ-1` block in `docs/STATUS.md`, which is normative
for scope. The row must answer **four questions**, not one:

| | question | state |
|---|---|---|
| (a) | what absorbs gold — something worth tens of thousands, repeatable, that a player WANTS | **ANSWERED on the levy** by IQ1-3 — 85.2% of the surplus, receipts 4.00× (§0.6a); *(was PARTIAL: IQ1-1 alone converted 15%)* |
| (b) | what makes wealth conditional on playing well | **ANSWERED on the levy** by IQ1-3 — the substitute is priced by Europe's alarm; the economy-wide residual is **IQ1-3e**'s |
| (c) | what makes a bad position expensive | **ROUTED OUT** — see §0.6, user ruling of September 13, 2026 |
| (d) | what makes all of it legible on a surface the player reads | **CLOSED for Net and for player purchases** by IQ1-0 + IQ1-2; the recurring obligations are IQ1-3a's |

…and its **four completion items** (i) the treasury is not monotonic on the
commanded arm, (ii) a losing France's per-turn Net is worse than a winning
France's at the same army size, (iii) every gold component the player is
charged appears as a signed line in the Strategic Ledger and sums to the Net
shown, (iv) an acceptance test states the purse-to-price ratio's replacement
as falsifiable arithmetic in both directions.

**⚠ Items (i) and (ii) are RE-STATED — see §0.7.** Both are satisfied by the
shipped engine as literally worded, for reasons the row does not want, so
pinning either verbatim would ship a green test over a live defect.

**✅ ALL FOUR WERE MEASURED AT THE EXIT — §0.6b, September 14, 2026.** (i) MET
(10 qualifying falls against 0 on both other arms) · (ii) **measured FALSE and
worse than filed — a ratchet, not a handicap**, handed to the (c) gate ·
(iii) MET for 18 of 19 gold streams, the nineteenth measured and owned by
IQ1-3a′ · (iv) MET and mutation-proven. **Row IQ-1 is CLOSED.**

### §0.2 THE CRUX, AND THE RULING — September 13, 2026

Two user directives about the same board pointed opposite ways, and the
question was put back to the row with *"do best design possible"*. So it is
ruled here, and it governs everything after IQ1-2.

* **August 7, 2026**, delegating the econ gate: *"economy shouldn't go crazy
  unless you are doing very well and stable."* The gate implemented that
  literally and pinned it three ways — a stable France at peace pays the crown
  term **alone** and may grow *"effectively unbounded — **allowed, that is the
  blessing**"* (`docs/audits/ECON_BALANCE_GATE_2026_08_07.md`).
* **September 12, 2026**, opening this row: that exact board — a peaceful
  France at rate 30 banking **88,556** gold — is measured and called the
  disease.

**RULING: they reconcile, and the blessed rate STANDS.** August blessed a
*rich* France. September measured a *decision-free* one. A treasury of 88,556
that cannot be converted into anything is not a reward, it is a scoreboard —
the defect is not the size of the pile but that **no decision touches it**.
So IQ-1 does not tax a winning, peaceful, stable France. It gives the surplus
somewhere to GO, and prices what it buys by the threat the player's own
success creates — which answers (a) and (b) with one mechanic.

**Marked RULED — FOR USER CONFIRMATION**, per the row's own convention.
Three pinned tests in `tests/test_econ_balance_eb.py` (the golden-peace rate,
the 1.5%-of-chest sweep, and `TestConditionBeatsClock`) encode the August
reading and are **left untouched** by this ruling; the alternative reading —
that golden peace should now pay a size-scaled rate around 117 instead of 30 —
would red all three and is a different game. It remains available.

**DISSENT ON RECORD** (§0.8), because the row had none and its own exit clause
instructs that one be read.

### §0.3 LANDING RECORD — IQ-1 SW-0 (≡ IQ1-0) "The Chest Speaks"

Commit `3686922`. **Zero balance.** Flip lever
`ledger.THE_CHEST_STATES_ITS_CEILING`; the False arm zeroes both new keys and
the rest of the payload is asserted byte-identical.

* Two numbers the game computed every turn and showed nobody reached the
  Strategic Ledger: `gold_spent_this_turn` (serialized since Phase 6, rendered
  on exactly one surface) and the treasury's own **fixed point**, via the new
  single source `ledger.state_charges_ceiling(net, rate)`.
* Both keys are **outside Net** by construction and by test.
* An AST census over every function in `backend/` that subtracts from
  `nation_gold`: **21 subtract, 15 never record**. Pinned as an exact-match
  allowlist with a sensitivity arm. ⚠ *The commit's figure moved after it was
  written:* at HEAD it is **22 subtract / 7 recorded / 15 unrecorded**, because
  SW-1 added a recorded one, and the test survives on a `>= 21` bound. Nobody
  should chase that as a regression.
* `tools/playtest_driver.py` learned to record **every nation's purse** per
  turn (jsonl only — it is omniscient data, and the markdown digest is written
  to read like a player's eye view). That is what made it visible that a
  neutral Ottoman Empire ends a 40-turn ambient run as the richest state in
  Europe while France holds 1.4% of Europe's cash.
* `tests/test_iq1_sw0_chest_speaks.py` (18); sweep `tools/_sweep_iq1_sw0.json`
  13 killed / 0 INERT.
* **Completion item served:** part of (d).
* ⚠ **Deferred without a slice id**, which IQ1-2 closes: the per-row judgement
  of the 15 unrecorded outflows was left to *"a later slice"*.

### §0.4 LANDING RECORD — IQ-1 SW-1 (≡ IQ1-1) "The Substitute Market"

Commit `c3d74fa`. The first purchase in the game bounded by **gold**.

* `purchase_levy` buys infantry with gold and draws **nothing** from
  `manpower_pools`. The fiction is exact: under the conscription law a
  called-up man could pay a *remplaçant* to serve in his place, and the price
  rose as the class emptied.
* Priced `base × LEVY_SUBSTITUTE_MULT × (1 + LEVY_SCARCITY_MULT × scarcity)`
  and handed to the EXISTING `_calculate_recruit_cost` as its base, so the
  capital discount, the war ×3, the ES-3 over-limit ladder and MC-2b's
  Intendance all compose on top exactly as they do for a draft — one helper,
  player and AI alike (GR5), shown = applied by construction.
* Ceiling = `FORCE_LIMIT_SEVERE_BAND × force limit`, the same line above which
  the ES-3 ladder stops charging half rate. Replacements, not expansion.
* `tests/test_iq1_sw1_substitute_market.py` (50); sweep 23 killed / 0 INERT;
  corpus 686/686; `CAMPAIGN_LOG_TYPES` 162 → 163.
* **Completion item served:** part of (a).

> **⛔ THE COMMIT'S HEADLINE ABSORPTION FIGURE IS WRONG AND IS CORRECTED HERE.**
> *"58,992 gold at turn 40 against a baseline 88,556, i.e. 29,564 absorbed — a
> THIRD of the surplus"* is a **cross-script difference, not a spending
> measurement**. Read off the archived spender digest:
> * **6 of 13** scripted buys succeeded, for **18,852 gold**
>   (7,257 + 2,400 + 2,400 + 2,040 + 2,400 + 2,040);
> * **6 were refused** — *"We do not hold Munich / Piedmont ×4 / Franconia,
>   Sire"* — on an own-soil gate, and 1 on price;
> * every success delivered **9,000** men, never the 30,000 asked;
> * the arm ends on **24 provinces against the baseline's 29**, so the rest of
>   the gap is a smaller empire and an indemnity.
>
> **Never cite 29,564 again.** Cite the three numbers separately — purchases,
> lever-isolated difference, province divergence — and measure absorption
> **lever-off on the same script**. The lever-off control arm does not exist
> yet; IQ1-2 commits one.
>
> **⛔ AND A SECOND CLAIM IS CORRECTED:** *"CO-4 does not prohibit, it CAPS.
> The same rule now applies here, identically."* The commit removed the
> **depot** requirement only; `_execute_purchase_levy` still hard-refuses on
> `region.controller != acting_nation`, and that gate killed 6 of 13 scripted
> purchases. It also sits against `WorldState.ALLY_SUPPLY_STATES` (PC15-D2),
> under which a vassal's soil *feeds* a guest army at `HOME_SUPPLY_MULTIPLIER`
> — so Massena at Milan, his own vassal's capital, with a depot, is refused
> substitutes. Whether that gate is right is **IQ1-3's** question, on the row.

**Checklist debt recorded rather than left to be re-found as a bug:**
* **Step 6 was skipped.** There is no `purchase_levy` few-shot in
  `prompt_builder.py` and `batches` appears in no LLM tool schema; the
  executor recovers the count by regex over `raw_command`. This is now a
  **recorded decision** — the count is recovered from raw text, which works on
  both paths because `raw_command` is always populated — not a silent gap.
* **Step 7 asymmetry:** `purchase_levy` is absent from `objection_actions`
  while `recruit` is present. Deliberate (a purchase is not an order a marshal
  can refuse), recorded here so it is not rediscovered as a defect.
* **`substitutes_purchased` is dropped for every non-player court.**
  `campaign_log.filter_campaign_log` has no economy branch and no default arm,
  so an event type absent from the player-court whitelist is filtered out —
  which means the twelve `len(CAMPAIGN_LOG_TYPES) == 163` pin comments
  asserting the row exists *"because an AI nation buying 30,000 men had no
  persistent surface"* are green about something that does not happen. Its
  producer also emits no region key, so the docstring's promised *"Enemy
  economy events: region PARTIAL+"* arm has nothing to test on. **Homed on
  IQ1-3** with the discoverability rider below; fixing it means changing the
  producer.

### §0.5 LANDING RECORD — IQ1-2 "The Chest Tells the Truth"

**Zero balance.** Flip lever `ledger.THE_CHEST_TELLS_THE_TRUTH`.

⚠ **WHAT THE LEVER ACTUALLY COVERS** — corrected by the review round, which was
right that the first wording claimed more than it can do. The False arm restores
the **post-charge ceiling argument**, the **single `bounded` sentinel**, the
**player-scoped `treasury` / `bankruptcy_turns` keys** and the **player-scoped
levy** — parts (1) and (2), and with them (6), because lever-down hands the
client the old int and the old state, which is the arm the previous `.gd`
rendered. The player's own payload is asserted byte-identical key by key. It
does **not** revert part (3) (the seven `record_gold_spent` calls), part (4) (the
canonical component map) or part (5) (the driver). **A considered decision, not
an omission:** those three are additive — a display record, a de-duplicated
constant and a dev instrument — with no prior *reading* to restore, and a lever
threaded through four files for a figure that changes no mechanic would be
ceremony. The allowlist is a TEST constant, is not levered at all, and is now
**10 entries, not 8** (§0.5.2).

It goes before the sink because **three of the row's four completion items
could not be measured at all**, and because the instrument was lying in three
separate ways a reader of the Strategic Ledger would have believed.

**(1) The ceiling was not a fixed point.** `_build_economy` fed
`state_charges_ceiling` the net that had **already** had `state_charges`
subtracted. The fixed point is defined against the gold coming *in*, so a
number whose whole content is *"the treasury this is steering toward,
independent of where the treasury is now"* slid with the chest. Measured on
ONE unchanged 1805 boot world at ONE unchanged rate (80), varying only the
treasury:

| chest | shipped `ceiling` | true fixed point |
|---|---|---|
| 800 | 59,562 | 59,562 |
| 5,000 | 56,562 | 59,562 |
| 20,000 | 41,562 | 59,562 |
| 40,000 | 21,562 | 59,562 |
| 60,000 | **0** | 59,562 |
| 88,556 | **0** | 59,562 |

**Two faces, both real, and the record states both.** At rate 80 (the boot, at
war) the line **disappears** at a large chest — `strategic_ledger.gd` renders
`if ceiling > 0` and the GR2 sentinel swallowed it once the charge exceeded the
gross. At rate 30 — the turn-40 peace board this row was opened over — it
renders **252,000 against a true 338,500**, so on the disease arm the player
was told the brake was **86,500 gold closer** than it is. The single honest
statement: the shipped figure **always** understated, and vanished exactly when
the chest was largest.

**(2) The economy tab answered for France when asked about Austria.**
`"treasury": int(world.gold)` and `bankruptcy_turns` read `player_nation`-scoped
properties while the function takes a `player` argument every other key
honours. Measured on the boot: asked about **Austria** it reported **800**
against a real **700**; about **Britain**, 800 against **2,000**. No GR5 claim
about an AI court's economy was readable — and this row is going to make
several.

**(3) The fifteen outflows are judged, row by row, into three dispositions
with a written reason each** (GR9 — SW-0 deferred this with no slice id, and it
sits directly on completion item (iii)). The exact-match allowlist shrinks
**15 → 10**; the sensitivity arm stays, so a NEW unrecorded outflow still reds.
*(⚠ It read 15 → 8 on first publication. The review round found the census
could not see a LOCAL ALIAS, so two real outflows had been escaping it entirely
— the coverage claim was 22 of 24 — and both are disposition (B). §0.5.2.)*

* **(A) PLAYER PURCHASE → records into `Spent`** (7 sites):
  `naval_executor._execute_build_fleet`,
  `diplomatic_executor._execute_buy_off_design` / `_execute_make_amends` /
  `_execute_make_amends_grievance_variant` / `_apply_ultimatum_demands`,
  `vassal.invest_in_vassal`, `vassal.attempt_vassal_bribe` (all three arms).
  The ultimatum is recorded against **whoever yielded**, never the
  beneficiary; the buy-off records the **payer** only.
* **(B) RECURRING OBLIGATION → a signed Net LINE, not `Spent`. Owner IQ1-3a:**
  `coalition._process_british_subsidy`, `diplomacy.apply_continental_system`,
  `instruments.process_instruments`, `world_state._ratify_treaty`,
  `world_state._process_treaty_clauses`.
* **(C) NOT A PLAYER SPEND → stays permanently, reason at the call site:**
  `combat_executor._post_combat_pipeline` (the EC-W3 Butcher's Bill, charged at
  the battle, documented outside Net, already its own `materiel` row and on the
  same end-turn banner line as `Spent` — recording it would name one bill
  twice), `world_state._process_reckless_cavalry_turn_start`, and
  `vassal.process_vassal_tribute` (it debits the **vassal**; the lord's side is
  income).

> **⚠ ONE DISPOSITION WAS CORRECTED BY READING THE CODE.**
> `_process_reckless_cavalry_turn_start` was dispositioned *"a penalty, not a
> purchase"* on the strength of the function's **name**. The expression is
> `_m_cas * MATERIEL_RATE`, tallied into `materiel_spent_this_turn` three
> lines below — it is the **same EC-W3 bill** as the combat pipeline's, for the
> auto-resolved charge. Same disposition, different and correct reason.

**(4) The digest reconciles.** `tools/playtest_driver.NET_COMPONENTS` was a
**fourth** hand-maintained copy of the ledger's net expression and had drifted:
`admin_bonus` was missing, so the printed NET sub-line under-counted by
**exactly 50 on 40 of 40 rows** of both post-SW-0 arms (re-measured at HEAD
from the archive). The ledger is now the single source — new
`ledger.NET_GOLD_COMPONENTS` — and both the reconciliation test and the driver
import it; the driver's signs are **derived**, not restated. The digest keeps
its display labels and its folded `upkeep` row (`total == base + surcharge` is
a pinned ES-3 invariant, so the fold sums identically and the archived digests
stay diff-comparable), and a standing gate asserts the display set covers the
canonical map with that one declared fold. The residual is now **recorded**
(`net_residual` in the jsonl), so a future drift is falsifiable from any
archived run instead of needing a bespoke probe. ⛔ *Not* derived from
`tests/` — that has no `__init__.py`, imports pytest at module scope, and would
invert a dependency the reconciliation test's own docstring settles the other
way.

**(5) `spent` and `army_strength_total` reach the digest row.** `spent`
rendered on **ZERO** rows of all three archived IQ-1 digests — including the
spender arm that bought 18,852 gold — because `_advance_turn_internal` clears
`gold_spent_this_turn` and the driver's only two `/ledger` reads were the turn
header and post-end-turn. A **third** read now sits in the turn loop, after
the turn's commands and before `POST /command {end turn}`, behind a new
`Digest.turn_spend`. ⛔ *Not* inside `Digest.ledger_line` — the module comment
records that `ledger_line` **is** borrowed by a stub, which is why its
constants were moved to module scope in the first place.
`army_strength_total` was already on the payload the driver fetched and is
completion item (ii)'s only possible instrument; it is on the LEDGER row now.
⚠ *Found while building:* the key lives in the **`economy`** section, not
`forces`, and the first cut of this slice read `forces` — pinned.

**(6) The client renders all three ceiling states.** The sentinel said one word
for two facts (*"nothing is drawing on the chest"* vs *"the chest is not
growing"*), and the fix makes a **third** state *correctly* reachable — a
chest already **past** its own fixed point.

⚠ **SYNTHESIS-ROUND CORRECTION.** This used to read "which had no copy at all
because it could not previously be rendered", and that is **false**, measured:
on the pre-slice post-charge argument, **29 of 58 probed chests from 31,000 to
59,000 at rate 80 DID render** the above-the-ceiling case — with the *bounded*
copy at the calm DIMMED colour (chest 31,000 read ceiling 30,562; chest 59,000
read 2,562). Only above roughly **60,000**, where the post-charge net went
non-positive, did the line vanish. What was unreachable was a ceiling below the
chest that is also **correct**. `CEILING_BOUNDED` / `CEILING_NO_RATE` /
`CEILING_NO_SURPLUS`; `ceiling` stays an int for Godot (GR2) and
`ceiling_state` says which sentence to print. ⚠ `CEILING_NO_RATE` is reachable
on exactly one board: `get_state_charges_rate` returns rate 0 for any world
whose `sovereign_map` is not `"europe"` (N1, the 19-region rollback). On a
Europe world the crown term is unconditional, so the rate is never 0 there.

**(7) A player can learn the sink exists.** Measured before this slice:
`purchase_levy` had **zero** mentions in the help text, the tutorial, the
ledger, the dispatch, the region panel, or any `.gd` or `.tscn` — the row's
headline gold sink could only be found by typing a phrase nothing told the
player, and `_execute_help`'s own `recruit` entry uses the word *"levy"* to
mean the **draft**, which actively hid it. The help now carries a
`substitutes` entry, and every command phrasing it quotes is a pinned
golden-corpus row (derived from the block, so a fourth phrasing cannot escape
the gate). The rest — a `substitutes` field on `get_levy_status` so the ledger,
map summary and region panel inherit it from one source, plus a region-panel
chip — is a **named rider on IQ1-3** (§0.6), not an open deferral.

**Two stale claims about `gold_spent_this_turn` corrected**, because they are
the basis for *"byte-identical by construction"*: SW-0's commit body and
`backend/save_manager.py` both say it is *"read by the recruit pricing"*. It
is not. The only readers are `ledger.py`, `economy_executor.py`'s typed
economy report, and the two end-turn banner snapshots;
`_calculate_recruit_cost` does not read it. `SAVE_FORMAT_REFERENCE.md`'s
*"(recruit, build, repair)"* is corrected in the same slice that shrinks the
allowlist.

**Tests** `tests/test_iq1_iq1_2_chest_tells_the_truth.py` (**65** at close);
sweep `tools/_sweep_iq1_iq1_2.json` (**40** mutations) **40 killed / 0 INERT /
0 BROKEN**. ⚠ These read *(44)* and *21 killed* until the synthesis round: the
review round added 14 tests and 12 mutations and updated neither figure. The
class of error is a number restated in prose, so
`test_the_instrument_counts_are_not_stale` now DERIVES both from the collected
test count and `len()` of the sweep file — if you change either, that pin tells
you which line to edit.

**Series.** `BASELINE_SERIES` and M1–M7 **byte-identical without re-record**,
and for this slice that is a **property of the fix**, not a fact about the
harness: no gold amount changes anywhere. `record_gold_spent` appends only to
a display dict whose readers were censused; the ceiling, both treasury keys
and `ceiling_state` are display; the driver and the scripts are not production.

> **⚠ M1–M7 BEING GREEN IS WORTH NOTHING AS EVIDENCE FOR THIS ROW, and every
> IQ-1 slice must say so.** `tests/test_combat_sweep_metrics.py` contains zero
> references to gold, income, stability, upkeep or turn advance. It is
> structurally blind to every economy change. `BASELINE_SERIES` is the only
> real instrument here.

> **⚠ NO GODOT BINARY IN THIS CONTAINER**, so the parse harness and the boot
> smoke **DID NOT RUN** on the one `.gd` this slice touches
> (`strategic_ledger.gd`). That is recorded as NOT RUN, not as a pass. The
> file is pinned by source census with a sensitivity arm, and the render arm
> carries **IQ-10**'s open visual sign-off with it — IQ-10 is blocked on
> exactly this.

**Completion items served:** (iii) for Net and for player purchases; the
**instrument** for (i), (ii) and (iv).

#### §0.5.2 THE REVIEW ROUND — six lenses, 41 findings, and I republished the
#### very error I had just struck

Held at `ba90d19`, immediately after the slice landed. Six read-only lenses,
each finding refuted by an independent agent. **Everything below was fixed in
the follow-up commit.** Three findings were reached by two or three lenses
independently, which is what makes them certain.

**⛔ THE HEADLINE IS MINE. "Purchases 18,312" IS A CROSS-SCRIPT DIFFERENCE, NOT
A PURCHASE MEASUREMENT** — the exact mistake this slice's record struck SW-1
for, one paragraph after striking it. 18,312 is `spender total spend − control
total spend`, and the two arms' RECRUIT prices diverge with their boards, so
the difference is not the purchases. Read off the receipts themselves — which
state each price — the true figure is **18,852 gold across 6 successful
purchases** (7,572 + 2,400 + 2,400 + 2,040 + 2,400 + 2,040). **Corrected
everywhere. The method rule that follows from it, stated so the third
occurrence is harder: a spend is measured from the RECEIPT, never from a
difference between two boards.**

**THE FIX TOUCHED TWO OF THREE PLAYER-SCOPED READS IN THE SAME FUNCTION**
(found by two lenses). `_levy_block(world)` took no nation and
`get_levy_status` defaults to `world.player_nation`, so after part (2)
`_build_economy(world, "Austria")` returned **Austria's treasury beside
France's force limit, army total and infantry pool** — a payload contradicting
itself. This repo's own lesson, for the sixth time: *a fix that touches one
reader of a pipeline must be checked against every other reader in the same
function.* Fixed; the levy is nation-scoped and levered with the rest.

**THE OUTFLOW CENSUS COULD NOT SEE TWO REAL OUTFLOWS.** It matched only
`<x>.nation_gold[...]`, so a function that takes a **local alias** first —
`nation_gold = world.nation_gold; nation_gold[payer] = balance - transfer` —
was invisible. `settlement_offers.process_recurring_settlement_payments` and
`settlement_ratify._apply_settlement_terms` were escaping it, so the coverage
claim was **22 of 24**, and a new unrecorded outflow written that way would
have red nothing. The census now sees both idioms, the allowlist is **10 not
8**, both new rows carry their reason (disposition (B), IQ1-3a's), and the
sensitivity arm synthesises a module in each idiom and requires both to be
found.

**THE CEILING LADDER ASKED THE RATE BEFORE THE GROSS**, so a legacy world
(rate 0 by construction) that was *bleeding money* was told *"nothing is drawing
on the chest."* The gross is asked first now. And two copy defects with it: that
sentence names the **charges** rather than "the chest" — it printed twenty lines
under an `Upkeep: -865g` line that **is** drawing on it — and the `no_surplus`
arm, the worst state the tab can report, was rendered in the **calmest colour in
the palette**. It is an error colour now.

**A FALSE CLAIM IN PRODUCTION `.gd` SOURCE, repeated in a pin's docstring.**
*"It had no copy because it could not previously be rendered at all"* is wrong:
the above-the-ceiling case **was** rendered, by the generic arm, with the wrong
sentence and often the calm colour. What was unreachable was a ceiling below the
chest that is also *correct*.

⚠ **AND "CORRECTED IN BOTH PLACES" WAS ITSELF A FALSE COMPLETENESS CLAIM —
this repo's own named failure mode, committed in the sentence that fixed the
first instance of it.** The phrase was in **FOUR** places: the `.gd`, the pin
docstring, **`ledger.py`'s `THE_CHEST_TELLS_THE_TRUTH` lever header** (the
canonical in-code statement of what the lever does) and **§0.5 item (6)**
itself. Two were corrected and two — one of them production source — were not.
All four are corrected now, and a claim census pins that the phrase cannot
return anywhere without a `FALSE`/`CORRECTION` marker beside it. *The rule: a
completeness statement over a multi-site correction must be derived from a
census, not written from memory of the sites you happened to edit.*

**THE INSTRUMENT LOST A PURCHASE MADE WITH THE LAST ACTION POINT.** `/command`
auto-ends the turn when the last AP is spent, and the engine clears the tally
then — so the new pre-`end turn` read missed it. `turn_spend` is a **high-water
mark** now, fed by a read after each command.

⚠ **AND THE "STATED LIMIT" WAS A FALSE MITIGATION — the synthesis round killed
it.** The record said the auto-advance figure "is in the end-turn banner the
digest already prints". `Digest.command` prints `first_line(message)` **only**,
and the banner is on a later line: measured, the archived spender digest
contains **zero** occurrences of `| Spent:`, `| Treasury:`, `| Upkeep:` or
`Income:`, and the 7,572-gold buy turn's end-turn line reads in full *"Turn 3
ended. (Warning: 2 action(s) unused) Turn 4 begins!"*. So the figure was
recoverable from **no archive at all** — a silent hole wearing a limit's
clothes. **It is CLOSED rather than restated:** both end-turn producers already
stamp a structured `spent` on the `turn_end` event, which rides the response,
so `observe_end_turn_spend` folds that into the peak and the flush moved after
the end turn. *The rule: do not name an alternative source without checking
that the instrument captures it.* ⚠ And factoring the peak out immediately broke the
**borrowed-method** rule this repo documents — a stub Digest that borrows only
`turn_spend` died on a `self.observe_spend` call, caught by this slice's own
pin. The peak update is inlined, and a `Lone` stub pins it.

**THE DIGEST RECORDED A FALSE ZERO AND AN AMBIGUOUS ONE.** `ledger_line`'s
`spent` is structurally dead on that read, so it wrote `spent: 0` into the jsonl
beside `turn_spend`'s true figure — worse than writing nothing; the key is gone.
And `ceiling` 0 meant two different facts with no way to tell them apart in an
archive, so `ceiling_state` is recorded now. **`net_residual`'s sign was the
opposite of every prose statement of it** — `printed_net − component_sum` now,
so a positive residual means the sub-line under-counts, which is the direction
"+50" is quoted in.

**THE LEVER'S COVERAGE WAS OVERSTATED, and the record is corrected rather than
the code.** `THE_CHEST_TELLS_THE_TRUTH` reverts parts **1, 2 and 6** (the
ceiling argument, the three-state sentinel, the per-nation reads and the levy
scoping — and part 6's client half reverts with them, because lever-down
restores the old int and the old `bounded` state, which is the arm the previous
`.gd` rendered). It does **not** revert part 3 (the seven `record_gold_spent`
calls), part 4 (the canonical map) or part 5 (the driver). **That is a
considered decision, not an omission:** those three are additive — a display
record, a de-duplicated constant and a dev instrument — with no prior *reading*
to restore, and a lever over four files for a figure that changes no mechanic
would be ceremony. §0.5's contract is re-worded to say exactly this.

**PART 2 IS PRODUCTION-DEAD TODAY** (found by three lenses). All three callers —
`build_strategic_ledger`, `_execute_economy_report`, `dispatch` — pass
`world.player_nation`, for whom the property and the dict read are identical by
definition. So no rendered figure moves. **It is kept, as defence in depth**,
because this row is about to make GR5 economy claims about AI courts and the
next caller that asks about one would have been silently wrong; and the levy
half of the same defect was NOT dead — it would have shipped a
self-contradicting payload the moment anything asked. Recorded honestly rather
than sold as a live fix.

**THE GR5 HALF OF PART 3 IS UNOBSERVABLE IN THE DIGEST.** Every AI-side
`record_gold_spent` is cleared by `advance_turn` inside the same `end_turn`, so
an AI purchase never reaches a `SPENT` row. The calls are correct and symmetric
(GR5 is satisfied in the engine); the *instrument* cannot show it. Stated, not
fixed — IQ1-3 can carry an AI-side probe if it needs one.

**NINE VACUOUS PINS, ALL REWRITTEN.** The worst three: the `.gd` sensitivity arm
was a `str.replace` tautology that executed zero production code and was the
**only** claimed sensitivity arm for the slice's only `.gd`; `test_the_reasons
_are_not_vacuous` asserted that two function *names* exist in `vassal.py` and
nothing about the markers its docstring said it guarded; and the new-outflow
census pin was two **lower bounds**, which a new unrecorded outflow satisfies
happily. Also: the signs pin could not tell derived from restated and passed
with a set that wrongly negated a positive component; the help census matched a
**comment** and survived deleting the whole entry; the seven recorder sites had
no behavioural pin at all (now two drive the production functions, including the
**refusal** case and the **clamped** ultimatum); and `net_residual`, the slice's
own drift detector, had neither a pin nor a sweep mutation. ⚠ Two of my
*replacement* pins were then wrong about the code in turn — an absolute-indent
assertion that `invest_in_vassal`'s early-returning gates disprove, and a
fixture that never reached the spend because the boot vassals sit at
`LOYALTY_MAX` and the verb refuses there by design. Both rewritten; the refusal
became the better half of the pin.

**Two smaller corrections:** the new import of `NET_GOLD_COMPONENTS` inherited
`campaign_log`'s *"pure data with no game state"* licence, which it does not
deserve — it pulls 23 more backend modules including `world_state` — so the
comment now states why it is nonetheless safe (`backend.main` is not among them
and exactly one module-scope env read exists, for a variable the driver never
sets). And the archive note claimed `turn_spend` is jsonl-only; it prints to the
markdown too, `--archive` still copies md + meta only, and **teaching
`--archive` to carry the jsonl is now a named IQ1-5 landing.**

#### §0.5.3 THE SYNTHESIS ROUND — the review round's own record was wrong five
#### ways, and one of its "limits" was a silent hole

The 48-agent fleet's synthesiser returned **"shippable as it stands — no
behavioural defect survives"**, and then took six more. Every one is an error
in the RECORD rather than in the code, which is its own lesson: *by the third
pass the defects stop being in the game and start being in what you wrote
about the game.*

**⛔ "CORRECTED IN BOTH PLACES" WAS A FALSE COMPLETENESS CLAIM — written in the
sentence that fixed the first instance of exactly that failure mode.** The
claim *"could not previously be rendered"* was in **four** places, not two:
the `.gd`, the pin docstring, **`ledger.py`'s lever header** — the canonical
in-code statement of what the lever does — and **§0.5 item (6)** itself. Two
were corrected. All four are now, and
`test_the_false_claim_cannot_return_unmarked` derives the completeness rather
than asserting it: every surviving occurrence of the phrase must sit beside a
`FALSE`/`CORRECTION` marker. **The rule: a completeness statement over a
multi-site correction must come from a census, not from memory of the sites you
happened to edit.**

**⛔ AND THE CLAIM'S REPLACEMENT NEEDED A MEASUREMENT, WHICH IT NOW HAS.** On
the pre-slice post-charge argument, **29 of 58 probed chests from 31,000 to
59,000 at rate 80 DID render** the above-the-ceiling case — chest 31,000 read
ceiling 30,562, chest 59,000 read 2,562 — with the *bounded* copy at the calm
DIMMED colour. Only above roughly 60,000 did the line vanish.

**⛔ THE AUTO-ADVANCE "STATED LIMIT" WAS A SILENT HOLE WEARING A LIMIT'S
CLOTHES.** The review round wrote that the lost figure "is in the end-turn
banner the digest already prints". It is not: `Digest.command` prints
`first_line(message)` **only**, and the banner is on a later line — measured,
the archived spender digest contains **zero** occurrences of `| Spent:`,
`| Treasury:`, `| Upkeep:` or `Income:`, and the 7,572-gold buy turn's end-turn
line reads in full *"Turn 3 ended. (Warning: 2 action(s) unused) Turn 4
begins!"*. So the figure was recoverable from **no archive at all**. **CLOSED,
not restated:** both end-turn producers already stamp a structured `spent` on
the `turn_end` event, so `observe_end_turn_spend` folds it into the peak and
the flush moved after the end turn. **The rule: do not name an alternative
source without checking that the instrument captures it.**

**THE RECORD'S OWN INSTRUMENT COUNTS WERE STALE** — *(44)* tests and *21
killed* against a real 65 and 40, because the review round added 14 tests and
12 mutations and updated neither. The class of error is *a number restated in
prose*, so `test_the_instrument_counts_are_not_stale` **derives** both from the
collected test count and `len()` of the sweep file. It earned its keep within
the hour: it red on this very round's seven new mutations, and the sweep tool
then refused to run on a red baseline (FA-92's guard) — two gates catching one
slip, in the right order.

**THE NEW TRIPWIRE'S DIAGNOSTIC NAMED NO KEY on the one failure mode it exists
for.** Its "re-signed" clause was built inside an f-string with **escaped
braces**, so on a re-sign — where `added` and `removed` are both empty — it
printed the comprehension's own source text. Computed properly now, with
`(was, now)` per key.

**SIX OF THE SEVEN RECORDER SITES STILL HAD NO PER-SITE PIN** — one behavioural
pin on `invest_in_vassal` plus an indent census, neither of which reads the
ARGUMENTS. Now every call's `(amount, nation)` pair is asserted by name against
the subtraction beside it, extracted by **AST** — a line parser read the
grievance-variant call as empty, because it wraps across two lines, which is
how the first cut of that pin failed. Plus a structural GR5 pin: not one of the
nine calls may name `player_nation`.

**A PRE-EXISTING FALSE CLAUSE THIS SLICE HAD TOUCHED AND LEFT.**
`save_manager.load_game` says `gold_spent_this_turn` "is saved/restored around
post-objection" — false twice over, and it sat **four lines above** IQ1-2's own
correction of the neighbouring claim. There is no RESTORE (the only writers are
`from_dict` and the `advance_turn` clear; all four `saved_gold_spent` sites are
one-way `.copy()`), and the siting is **turn advance**, not post-objection —
`handle_objection_response`'s own PT-F5 comment records that that path never
re-enters `CommandExecutor.execute`. Inherited verbatim from slice 16c.

**One finding the synthesiser corrected against its own fleet, worth keeping:**
two lenses reported the levy defect as still live and four flagged the "every
other key honours" phrasing. The levy is fixed at HEAD and §0.5.2 discloses the
two-of-three miss honestly. The one key still sensitive to `world.player_nation`
is **`admin_bonus`** — measured, holding `player="Austria"`: 0 vs 50, carrying
`net` 405→455 and `ceiling` 14,656→16,218 — and that is **deliberate and
documented** at `world_state._calculate_admin_bonus`, to avoid double-counting
the AI's own admin phase. Not a defect, and recorded here so the next reader
does not "fix" it.

**Restored:** the cross-file forcing function the canonical map had removed.
Production reads only `ledger.NET_GOLD_COMPONENTS`; `EXPECTED_NET_SIGNS` in the
reconciliation test is a **tripwire** asserted equal to it, so adding or
re-signing a component reds in a second file and has to be done on purpose.

#### §0.5.1 THE PAIRED MEASUREMENT, AND TWO FINDINGS IT PRODUCED

The row had no attribution vehicle — which is how a cross-script difference
came to be published as an absorption figure. There is one now.
`commanded_spender40.json` is **repaired**: each of its 13 buy orders used to
**replace** the `recruit` line the substitute market competes with, so the arm
differed from `commanded_full40` by two changes at once. The buy is now an
**additional** order on the same turn (recruit + buy = 2 admin actions, exactly
`max_admin_actions`), so the arm differs from its parent **by the purchase and
nothing else**, and `commanded_full40` on the same seed is its control.

Both arms archived with their jsonl at
`docs/audits/playtest_digests/iq12-{control,spender}-cmd-historical/`
(and the reason the jsonl is there is filed beside them).

**40 turns, seed `historical`, `--diplomacy accept`:**

| | control | spender |
|---|---|---|
| treasury at turn 40 | **88,556** | **54,443** |
| treasury FALLS in 40 turns | **0** | **7** |
| provinces at turn 40 | 29 | **24** |
| army at turn 40 | 81,453 | **118,735** |
| recorded spend, all turns | 5,046 | 23,358 |
| of which substitute purchases | — | **18,852** (6 receipts) |
| NET sub-line residual | **0** | **0** |

**The control reproduces the row's disease figure to the gold** — 88,556, and
**perfectly monotonic: zero falls in forty turns.** So the three numbers, stated
separately as they must be from now on:

* **purchases: 18,852 gold**, read off the six receipts themselves
  (7,572 + 2,400 + 2,400 + 2,040 + 2,400 + 2,040). ⚠ This read **18,312**
  on first publication — `spender total spend − control total spend`, which
  is a CROSS-SCRIPT DIFFERENCE and the exact error this record strikes SW-1
  for two paragraphs above. See §0.5.2.
* **treasury difference: 34,113 gold** — NOT absorption, see below;
* **province divergence: −5.**

**FINDING 1 — THE SINK IS CURRENTLY SELF-DEFEATING, and this is the material
one for IQ1-3.** The spender arm ends with **+37,282 more men and 5 FEWER
provinces**, on scripts that differ only by the purchase. The mechanism is in
the receipt the game prints: *"Morale 89% → 75% (bought men muster at 25%)"*,
*"81% → 69%"*. Buying substitutes **dilutes the corps' morale**, so a player in
a good position who spends gold gets a bigger, weaker army and loses ground.
That is why the treasury difference is not absorption: part of it is a smaller
empire. **A sink the player WANTS (question (a)) cannot be one that makes the
position worse for using it** — IQ1-3 must decide whether the dilution is the
intended price (a defensible design: green conscripts *were* worse) or whether
it needs a counterweight the player can pay for, e.g. drill restoring the
morale it costs (the EB-era "drill restores morale" mechanic already ships).

**FINDING 2 — THE OWN-SOIL GATE AND THE FIELD CAP BOTH BITE HARD.** Of 13
scripted purchases: **SIX refused** *"We do not hold Munich / Piedmont, Sire.
Substitutes are received at our own depots"*, **1 refused on price** early
(*"The treasury holds 3,850"* — correct and good), and **every success
delivered 9,000 men against the 30,000 asked**, because the field batch cap
binds. So the dearest purchase on this board is ~2,400–7,572 gold, not the
24,840 the design's own worked example quotes. **Both are IQ1-3's to rule on**,
and the own-soil gate still stands against `ALLY_SUPPLY_STATES` (§0.4).

### §0.6a LANDING RECORD — IQ1-3 "The Granary and the Alarm"

**⛔ THIS IS NOT §0.6's RETAINER, and the recommendation is overturned on a
measurement, not on taste.** The decision fleet drove the entire
diplomacy-instrument channel through the real `_execute_buy_off_design` on the
1805 boot at a 1,000,000-gold chest: Denmark 600 + Ottoman 600 + Prussia 1,008
+ Sardinia 1,248 + Sweden 1,368 = **4,824 gold, one-shot, for every buyable
design in Europe** (three courts refuse on "We are at WAR"). That is **5.4% of
the disease chest** for a 15-turn term — **322 g/turn**. And after the sweep,
`coalition.get_qualifying_nations` returns `['Ottoman','Sweden','Naples',
'Hanover','Sardinia']` **identically**: `qualifies_for_coalition` reads relation
< −10, not-a-vassal, not-already-at-war and PR-1's fresh-peace floor, and
**nothing monetary at all**.

Three more things killed the shape, each read off a symbol:

* **Its payoff has no consumer.** `intent._derive_weight` reads
  `diplomatic_guarantees` and `has_renege_grievance` and **never**
  `directed_sponsorships`. The nearest consumer is shut by construction —
  `war_council`'s design coercion is `AI-vs-AI only` by its own comment, so a
  retainer on a France-aimed design **can never open**.
* **§0.6's "cancel verb" does not exist.** A grep for
  cancel/revoke/withdraw/release/rescind/terminate over `instruments.py`
  returns only the guarantee's `abandoned` renege path. A minted compact runs
  its full term; the only player exits route through `_renege` and cost −25
  relation plus a grievance.
* **A retainer is dominated 8–10× by a verb that already ships.**
  `_execute_buy_off_design` has NO `aim == player` refusal — only its
  `_execute_sponsor_design` sibling twelve lines away does — and its own
  docstring reads "buy off a design aimed at France('s sphere)". It buys the
  STRONGER product (full suspension, honoured at `agendas.py`'s chokepoint).

**So §0.8's DISSENT is MOOT, not overruled** — "paying Europe to stay quiet
makes a winning game easier rather than a losing game more expensive" was an
argument against a mechanic that no longer ships. Recorded rather than left
standing.

#### What IS built

| arm (cumulative) | ok | RECEIPTS | men | treasury@40 | prov | army |
|---|---|---|---|---|---|---|
| control (no buy orders) | — | 0 | 0 | 88,556 | 29 | 81,453 |
| HEAD | 6/13 | **18,852** | 54,000 | 54,443 | 24 | 118,735 |
| + A the granary | 12/13 | **65,916** | 129,000 | 23,937 | **26** | 161,830 |
| + A2 the host's price | 12/13 | **67,572** | 129,000 | 23,412 | 26 | 161,830 |
| + C the alarm | 12/13 | **75,486** | 129,000 | 19,577 | 26 | 161,830 |

**18,852 → 75,486 = 4.00×, and 85.2% of the 88,556-gold surplus** — with the
board ending BETTER, not worse, and the one surviving refusal on PRICE, which is
the market working. Every figure is a **receipt read at the executor**, never a
difference between two boards (§0.5.1's rule, and this row has broken it twice).
Re-measured at HEAD by me after the build: **75,486 in 12 purchases**, 19,577 at
turn 40, 26 provinces, army 161,830 — the fleet's arithmetic to the gold. Both
arms archived at `docs/audits/playtest_digests/iq13-{control,spender}-cmd-historical/`,
with their jsonl.

**A — THE GRANARY OF AN ALLY.** `_execute_purchase_levy` refused on OWNERSHIP
while the engine's own supply DECISION — `world_state._supply_multiplier`,
landed as PC15-D2 "The Ally's Table" — already feeds a guest army on
ALLIANCE / DEFENSIVE_ALLIANCE / VASSAL soil at `HOME_SUPPLY_MULTIPLIER`, and
`dispatch.py`'s depot-remedy arm says so out loud on the identical fact. Two
seams, one question, opposite answers — and **all six** own-soil refusals on
the archived arm (Munich ×1, Piedmont ×4, Franconia ×1) were on soil PC15-D2
feeds. Now ONE extracted predicate, `economy_executor.region_feeds_nation`,
read by the levy, the AI rung and (as its origin) the supply multiplier.
NON_AGGRESSION and OPEN_BORDERS hosts still refuse — the Ansbach line, for free
and by construction, because neither state is in `ALLY_SUPPLY_STATES`.

⚠ **PIN BERNADOTTE AT FRANCONIA, NOT MASSENA AT MILAN.** §0.4's own example is
wrong twice: Milan has no depot (the map holds **zero** in all 126 provinces) —
it is `region_type == "capital"` — and at boot, *with the gate open*, a purchase
there is STILL refused, by the establishment: 195,000 ceiling − 189,000 standing
= **6,000 of room** against the 10,000 a capital batch needs. A pin on Milan
would red while the fix works. Franconia (Bavaria/ALLIANCE/major_city → a 3,000
field batch) succeeds, and that is the pin.

**A2 — THE HOST'S PRICE.** The moment the gate opened,
`_calculate_recruit_cost`'s 25% capital discount became newly REACHABLE on an
ALLY's capital, because that function never read `region.controller`. Measured
at Munich: a full batch for 4,959 gold = **165 g per 1,000 men** against the
same arm's dearest at 1,074. A host's magazines feed your battalion; its
treasury does not subsidise your recruiting. Suppressed via a **default-off**
`foreign_soil` kwarg, so all nine existing call sites are byte-identical by
construction — measured cost, +1,656 gold of absorption for identical men.

**B — THE BOUGHT MEN ARE NOT PUNISHED TWICE.** The designed premium is
`LEVY_MORALE_PREMIUM` = 15 points below a draft. But the purchase path wrote a
FLAT `LEVY_MORALE_BASE` while the draft path reads `training_ground` (an
absolute 70) and Moore's Shorncliffe System (a floor of 60) — so the real gap
was **45 and 35** at those rungs, and **the one counterweight a player can
already BUY was void for substitutes**. `substitute_arrival_morale` mirrors the
draft's RUNG at the premium: **25 / 55 / 45**, the bare rung byte-identical to
what shipped. ⚠ Deliberately NOT one shared ABSOLUTE arrival function, which
two candidate designs prescribed and which would hand a substitute the draft's
70 — *better* than a bare draft's 40 — destroying the premium it exists to
protect. Plus the missing rout-line warning: `LEVY_MORALE_BASE`,
`FORCED_RETREAT_THRESHOLD` and the global rout threshold are all 25, so a big
batch into a tired corps leaves it one reverse from breaking and the receipt
said nothing. It is per-marshal, through `get_rout_threshold` (Charles sits at
15).

**C — THE ALARM PRICES THE LEVY.** §0.2's own words — "priced by the threat the
player's own success creates" — and it is question (b), answered on the levy.
`1 + max(0, threat − LEVY_ALARM_ANCHOR)/100` on `levy_substitute_price`. A
frightened continent does not sell its sons cheaply to the power frightening it.
**Boot-dormant on every seed BY CONSTRUCTION**, not by one measurement: the
authored `threat_level_band` is [65, 75] and the anchor is **75**, so the
multiplier is exactly ×1.00 at both endpoints — pinned, along with a pin that
reds if the authored band ever reaches past the anchor. `max(0, …)` also means
an absent threat slot is ×1.00 and never a DISCOUNT. ⚠ It prices SUBSTITUTES
only: putting the term in `_calculate_recruit_cost` would move every recruit
price in the game and red blessed pins, so a France that ignores the substitute
market pays no alarm — deliberate, and left on the row as an honest question for
the econ owner.

**D — THE RIDERS.** All three of §0.6's, plus a fourth of the same kind.
(1) `get_levy_status` gains a `substitutes` sub-dict — price, amount, batch cap,
ceiling, room, alarm premium, arrival morale, open — so the ledger, the map
summary and the region panel inherit the market's terms from ONE source; and a
region-panel **chip** that names the marshal, quotes the per-province
per-marshal price, and is **present-but-dimmed with its reason** when gated,
never absent. ⚠ The chip quotes a NEW `substitute_price_here`, not
`recruit_price_here`: the latter passes no `marshal=` and is Intendance-blind
while the charge is not, so reusing it would quote a figure the executor does
not charge — the Aug-30 lesson, one verb over. (2) `substitutes_purchased`
reaches the campaign log for non-player courts. ⚠ **The fleet reported the
filter as having "NO economy branch and no default arm"; half right, and the
correction is the smaller fix** — the branch has been there since Session 8 and
the TYPE was missing from it, while the producer emitted no `region` key for the
"region PARTIAL+" rule to read. Both fixed, so the twelve
`len(CAMPAIGN_LOG_TYPES) == 163` pin comments stop being green about something
that cannot happen. (3) The three shipped instrument verbs — buy off, sponsor /
licence, guarantee — are **named in the help text** for the first time, the
identical hole IQ1-2 closed for `purchase_levy`, and every phrasing taught is a
pinned golden-corpus row. (4) `--archive` now carries the **jsonl**: `purses`
and `net_residual` live only there, so every archived arm had been losing the
only instrument that makes a GR5 economy claim falsifiable.

#### The rulings §0.4, §0.5.1 and §0.6 handed to this row

| question | ruling |
|---|---|
| the morale dilution | **CORRECT PRICE, STANDS.** §0.5.1 FINDING 1's causal sentence is STRUCK — see below. What is built is the second penalty nobody designed. |
| the own-soil gate | **OPENED** to `ALLY_SUPPLY_STATES`. The single largest measured gain in the row, 3.50×. |
| the ally CAPITAL | full BATCH granted (PC15-D2's granary); the 25% DISCOUNT suppressed. |
| the 9,000-of-30,000 batch cap | **KEPT, UNTOUCHED** — and §0.5.1's framing is half wrong. `gold_cost = per_batch × batches` with `batches` capped at 3 either way, so the gold per admin action is identical (8,280); the cap is a MEN cap that makes men 3.33× dearer, and RAISING it would SHRINK lifetime absorption, because `levy_purchase_ceiling` bounds purchases by men rather than gold. What ships instead is copy. |
| the IQ-3 boundary | **DISCHARGED.** IQ1-3 touches ZERO coalition symbols, so the boundary is a fact and not a promise, and §0.6's "the two rows must land together" no longer holds. |

**⛔ §0.5.1 FINDING 1's CAUSAL SENTENCE IS STRUCK — the third occurrence of the
error this row has already struck twice.** "A player in a good position who
spends gold gets a bigger, weaker army and loses ground" was a **cross-board
difference presented as a mechanism**. Measured: 18 of 19 French battles are
byte-identical across the arms and all five province losses were unopposed
marches; a bigger-greener corps measures **stronger** (54.9% vs 47.9%
defensive win rate); and with **3.5× more** substitutes the board ends on **26**
provinces, not 22. The arithmetic: effective strength is `S × (0.5 + m/100)`, so
adding `n` men at quality `q` changes it by `n × (0.5 + q/100)` — positive, and
independent of the corps' own size and morale.

**The method rule this extends, and it is the useful part: A PROVINCE COUNT IS A
BOARD DIFFERENCE TOO. Paired arms stop being an isolation at the first AI
decision that reads the board.** ⚠ And a pin written on the multiplier alone
reproduces the same confusion — my own first cut compared
`get_combat_effectiveness()` values (1.5 → 1.29) and red, which is the
multiplier correctly FALLING while the product rises.

#### Completion item (iv) — the 590× ratio is RETIRED

Replaced by two clauses in ONE predicate, `the_chest_is_convertible(gross, rate,
chest, receipts, turns)`, shared by every arm AND by the negative control (the
IGR-E pattern):

* the unconverted hoard in **turns of the empire's entire gross income**, ceiling
  **12** — control **21.9**, HEAD 17.3, the positive arm **8.1**;
* the share of lifetime gross actually **converted**, floor **0.40** — control
  0.000, HEAD 0.150, the positive arm **0.783**.

⚠ **NOT §0.7's obligation-based fixed point**, which three candidate contracts
proposed: `state_charges_ceiling` returns 0 for `net <= 0` and `_build_economy`
renders that as `CEILING_NO_SURPLUS` — the state IQ1-2's review round
deliberately repainted in an ERROR colour — so a predicate treating that 0 as a
PASS scores **over-commitment as success** and is satisfiable by any obligation
large enough. This slice's sink is `Spent`, not Net, so no obligation term is
needed. ⚠ And not the ratio itself: the same pricer returns 150 at the capital
at peace and 654 at the boot (a 4.4× ambiguity in the denominator), while the
modal DELIVERED purchase across every archive is 3,000 men for 200 gold.

**A rump is excluded, not scored.** `GROSS_FLOOR = 1842` (the boot's own gross)
plus the growing-chest guard decline to grade a collapsed France — which is what
the newly archived ambient baseline is FOR: it ends on **5 provinces and 2,593
gold with 23 treasury falls**, non-monotonic for the wrong reason.

**Series.** `BASELINE_SERIES` and M1–M7 **byte-identical without re-record**,
and the reason is measured: the AI substitute rung is unreachable on the shipped
board — 18 of 20 nations hold an infantry pool ≥ 10,000 at boot, and
`_find_weakest_marshal_for_admin` skips a marshal whose pool covers a draft — so
the granary changes no AI decision there. ⚠ M1–M7's greenness is worth nothing
here regardless (zero references to gold, income, stability, upkeep or turn
advance).

**Tests** `tests/test_iq1_iq1_3_the_granary.py` (**63** at close); sweep
`tools/_sweep_iq1_iq1_3.json` (**35** mutations) **35 killed / 0 INERT /
0 BROKEN**. ⚠ **Five came back INERT first and every one was a real coverage
gap** — nothing DROVE a purchase in a training-ground province (so the seam
consuming the morale helper was unpinned while the helper was pinned), nothing
drove a purchase onto the rout line, the archive pin matched the guard line one
above the copy it meant to check, and neither clause of item (iv) was isolated
on an arm where only it bites. A sixth lesson landed with them: **the
`GROSS_FLOOR` guard's real case is a collapsed rump that spent its last coin** —
tiny gross, tiny chest, conversion 1.00 — which PASSES without it.

**⚠ NO GODOT BINARY IN THIS CONTAINER**, so the parse harness and the boot smoke
**DID NOT RUN** on `region_panel.gd`. Recorded as NOT RUN, not as a pass; the
chip carries **IQ-10**'s visual sign-off with it.

**Deferred with owners, GR9-clean:** **IQ1-3a′** the recurring-obligation Net
line (re-scoped — this slice ships no new per-turn producer and its sink is
`Spent`-recorded, so item (iv) does not depend on it; the measured urgency it
does have is that a player using the shipped 200 g/turn sponsor chip moves
`net` by 0 while the chest drains); **IQ1-3e** the (b) residual, economy-wide —
IQ1-3 answers (b) **on the levy** and says so in writing.

---

### §0.6b LANDING RECORD — IQ1-5 "The Exit"

**September 14, 2026. ZERO production code**, as the slice defines itself.
The four completion items measured against the re-stated predicates of §0.7
on committed archived arms, the (iv) acceptance test verified in both
directions, the pillar re-scored and the §0.8 re-open condition resolved.

**⚠ Two of the exit's own probes were wrong before they were right**, and the
mistake is the one the row keeps making: `advance_turn` calls
`process_income_phase` internally, so a probe that calls BOTH charges France
twice. The first two item-(iii) probes did exactly that and read their own
double charge as a growing unnamed residual of 590 → 1,061 gold/turn. It does
not exist. Recorded because the row's rule is to reproduce before filing, and
the first two reproductions were the thing being measured.

#### Item (i) — MET, and the predicate refuses the arm's bad turns by itself

Re-stated: *a treasury fall whose largest single term is a player-initiated
spend recorded in `gold_spent_this_turn`, with province count non-decreasing
across that turn.*

| arm | falls | qualifying |
|---|---|---|
| `iq13-spender-cmd-historical` | 12 | **10** — turns 6, 12, 15, 18, 21, 24, 27, 30, 36, 39 |
| `iq13-control-cmd-historical` | **0** | 0 |
| `iq1-ambient-baseline-historical` | 23 | **0** |

The two falls it rejected are exactly the two turns the spender arm lost
ground — turn 9 (29 → 28) and turn 33 (29 → 27). So §0.6's ⛔ *"do not grade
the exit on `commanded_spender40.json`, it would score a collapse as a sink"*
is honoured **by the predicate**, not by excluding the arm: the re-statement
was written to make a shrinking board unscoreable and it does that on the
first arm it meets. The control arm has **no treasury fall at all in forty
turns**, which is the disease stated as a measurement; the ambient arm has 23
and not one is a purchase.

#### Item (ii) — measured **FALSE**, and it is a ratchet, not a handicap

Re-stated: the army must be allowed to **fall** and the engine's own recovery
ticks must run. Two boards from the same scenario and seed, one whole
(189,000 men, 28 provinces), one beaten (94,500 men, 23 provinces, war damage
and −45 stability on every survivor), **both held at PEACE before every tick**
so the gap is the upkeep asymmetry and not a war rate.

**⛔ A CLAIM OF THIS EXIT'S OWN WAS STRUCK BY ITS OWN PIN, before publication.**
The first measurement built the beaten board by making peace **before**
applying the losses, and reported the loser **ahead by +534 on turn 0**. It
does not reproduce. Making peace first runs the war-end cleanup, which hands
occupied territory back, so France keeps a **richer** 23 provinces — gross
income **2,056 against 1,256**, a difference of exactly 800 — and the turn-0
reading is an artefact of construction order. Built the other way the *whole*
France leads turn 0 by **266**. The `+534` is withdrawn; the table below is
the conservative order (beat first, then make peace), and the pins are written
on the half that reproduces **identically under both orders**.

| turn | winner Net | loser Net | loser − winner | beaten army |
|---|---|---|---|---|
| 0 | +784 | +518 | −266 | 94,500 |
| 1–4 | +750 … +650 | +534 … +602 | −216 … −48 | 94,500 |
| **5** | +619 | **+1,253** | **+634** | **69,500** |
| 6 | +588 | +1,258 | **+670** | 69,500 |
| 7 | +558 | +1,264 | **+706** | 69,500 |
| 8 | +538 | +1,269 | **+731** | 69,500 |

The other order gives +625 / +662 / +697 / +723 on those same four turns — the
two constructions agree to within **ten gold a turn** on the late arm and
disagree only at turn 0, which is why only the late arm is pinned.

The row's contract recorded this as a fixed handicap (*"+325 g/turn rising to
+1,717"*). It is **a ratchet**, and the mechanism is worse than "the army is
smaller": **the peace ceded the ground two corps were standing on.** Ney and
Davout are both at Rhineland, one of the five provinces handed over — 12,000 +
13,000 = the whole 25,000 — and the engine warns them three times
(`evacuation_lapsing`, turns_left 2 → 1 → 0) and then interns them
(`marshal_destroyed`, `cause: "interned"`, `victor: "Austria"`). The loser's
upkeep falls **again**, and the gap inverts and widens every turn after.

**So losing territory cuts the loser's bill twice** — once for the men lost in
the fighting, and again for the corps left standing on the ground it gave away.
Underneath it the shapes are opposite: **the victor's Net decays 784 → 538
while the beaten one's grows 518 → 1,269**, so the gap does not close on its
own at any horizon.

⚠ **The mechanism was NAMED by a mutation, not by me.** The first sweep entry
for this pinned supply attrition and came back **INERT** — disabling
`process_supply_attrition` entirely changed nothing, because attrition is not
what removes the men. The pins now read the engine's own internment event
rather than inferring it from two corps disappearing; renaming that event had
left every one of them green.

**Not fixed here.** Question (c) was **ROUTED OUT to its own design gate by
user ruling, September 13, 2026**, and this is its evidence, strengthened.
IQ1-5 records the item as **measured-open and handed off** rather than
closing it — the row does not get to fudge its own grade.

#### Item (iii) — MET for 18 of 19 streams; the nineteenth is owned and now measured

Method: trace **every** write to France's purse across ten real turns
(`advance_turn` only), on a board carrying a live 200 g/turn
`directed_sponsorship`, and classify each write by the production call site
that made it.

| production site | writes | total gold | named on the ledger? |
|---|---|---|---|
| `world_state.process_income_phase` | 10 | −11,430 | **yes** — its 14 terms are all declared Net components |
| `vassal.process_vassal_tribute` | 30 | +9,370 | **yes** — `vassal_tribute` |
| `diplomacy.process_trade_income` | 10 | +1,750 | **yes** — delivers `trade_income − blockade` as ONE net write; both declared |
| `instruments.process_instruments` | 10 | **−2,000** | **NO** |

Plus the structural half, already pinned: Net **==** the signed sum of its 18
declared components, and every one of the 18 is asserted present in
`strategic_ledger.gd` (`tests/test_economy_ledger_reconciliation.py`, the
`NET_GOLD_COMPONENTS` tripwire).

So the one unnamed stream is `process_instruments` — **IQ1-3a′'s gap, now
measured at face value instead of argued**: a standing 200 g/turn sponsorship
moves the chest by 200 and Net by **exactly 0**, every turn, for as long as it
stands. Carried to IQ1-3a′ with its number.

#### ▶ NEW FINDING — IQ1-5-1: the Charges of Empire are quoted one tick stale

Found while reconciling item (iii), and it is not the instruments gap. With
**no** obligation on the board the projection still misses by a constant, and
term-by-term it is all in one place:

| term | ledger quote | charged | moved |
|---|---|---|---|
| income | 3,400 | 3,400 | 0 |
| admin_bonus | 50 | 50 | 0 |
| admiralty | 90 | 90 | 0 |
| upkeep_base / surcharge | 1,512 / 1,118 | 1,512 / 1,118 | 0 |
| **state_charges** | **1,216** | **1,337** | **+121** |

Cause, confirmed by reading the rate on both sides of the advance:
`get_state_charges_rate` carries a `war_exhaustion` term that ticks **+8 per
turn at war** (0 → 8 → 16 → 24 → 32 over four turns), and the ledger's economy
tab is a **forward projection by contract** (CA9-N11, stated in
`_build_economy`'s own docstring) — so it prices the charge at *today's* war
effort and the income phase levies it at *tomorrow's*. Quoted 1,216 / paid
1,337; quoted 1,355 / paid 1,478; quoted 1,492 / paid 1,616.

The gap is `(treasury − CHARGES_HOARD_FLOOR) × 8 // WAR_EFFORT_DIVISOR` —
**121 gold/turn at a 40,000 chest and 277 at the control arm's 88,556** — and
it sits on the ledger's single largest discretionary term, whose own
docstring claims *"the SINGLE source … (shown = applied)"*. **Not fixed here**
(IQ1-5 ships no production code); filed in `BUG_FIXES.md` §Improvement Queue.

#### Item (iv) — MET, closed, and mutation-proven

`the_chest_is_convertible(gross, rate, chest, receipts, turns)` — ONE function
shared by every arm and by the negative control (the IGR-E pattern), asserted
in both directions:

* control `(4038, 30, 88_556, 0, 40)` → **False** (hoard 21.9 turns of gross);
* HEAD-after-IQ1-1 `(3142, 30, 54_443, 18_852, 40)` → **False** (conversion 0.150);
* the slice `(2409, 30, 19_577, 75_486, 40)` → **True** (hoard 8.1, conversion 0.783);
* negative control: roll the positive arm's receipts back to 18,852 → **False**;
  roll its chest back to 88,556 → **False**.

`tests/test_iq1_iq1_3_the_granary.py` 63 green; the three item-(iv) mutations
(IQ13-33/34/35) **killed** in the re-run sweep.

#### The row's four questions at the exit

| | question | state at close |
|---|---|---|
| (a) | what absorbs gold | **ANSWERED on the levy** — the first purchase in this game bounded by gold rather than by slots, benches, keels or pools; receipts 18,852 → 75,486 = **4.00×**, **85.2% of the surplus** |
| (b) | what makes wealth conditional on playing well | **ANSWERED on the levy** — the substitute price rises with Europe's alarm, which the player's own success creates. Economy-wide residual → **IQ1-3e** |
| (c) | what makes a bad position expensive | **ROUTED OUT** to its own design gate (user ruling, Sept 13). Item (ii) is its evidence and is **worse than filed** |
| (d) | legibility | **CLOSED** for Net and for player purchases; ONE stream open (**IQ1-3a′**, measured 200 of 200 gold invisible) plus the new **IQ1-5-1** |

#### The pillar re-score — economy **6.0 → 6.5**

The rise is for what is measured, and it is held below 7 for what is measured
too.

**Up, because:** the chest is convertible on the arm that engages with it
(85.2% of the surplus, 4.00× receipts, hoard 21.9 → 8.1 turns of gross); the
treasury stops being monotonic for the *right* reason for the first time (10
qualifying falls against 0 on both other arms); and the player can finally
read what they are charged — 18 signed components that provably sum to Net,
every one rendered, plus `Spent` and the chest's own `Ceiling`.

**Held below 7, because:** a France that simply does not buy reproduces the
September 12 disease board **exactly** — `iq13-control-cmd-historical` ends on
**88,556 gold, 29 provinces, 81,453 men and zero treasury falls in forty
turns**, which is the same 88,556 the row opened on. The sink is a *choice*,
by the §0.2 ruling, so the disease survives declining it. And **(c) is not
merely unbuilt, it is measured widening** — the beaten France out-earns the
victorious one by +723 g/turn and rising.

**⚠ RULED — FOR USER CONFIRMATION**, per the row's convention: the score is
mine, taken on the evidence above, and a user who reads the control arm as the
governing case would hold the pillar at 6.0.

#### §0.8's re-open condition — **does not fire**

Stated in advance: *"if the economy pillar does not move off 6.0 after IQ1-3
lands, the re-open is the stability ratchet."* It moved, so the ratchet is not
re-opened — but the condition's own caveat is worth keeping on the record
rather than discarding with it: on the disease arm **28 of France's 29
provinces are homeland**, so a homeland/conquest split would have had almost
nothing to bite on there. The dissent of §0.8 stands unretracted and is now
carried by IQ1-3e and by the (c) gate.

#### Limits of this exit, stated rather than implied

* **No new arm was driven.** The exit grades committed archives, as specified.
* **No `--llm anthropic` arm and no Godot client pass** — no API key and no
  Godot binary in this container. The region-panel levy chip that IQ1-3 landed
  is **unverified on screen** and carries **IQ-10**'s sign-off.
* **The AI substitute rung is still measured unreachable on the shipped
  board** (18 of 20 nations boot holding an infantry pool ≥ 10,000), so the
  ambient arm is untouched by this row and `BASELINE_SERIES` needs no
  re-record — which is a fact about the board, not evidence the rung works.

#### The exit's own pins

`tests/test_iq1_iq1_5_the_exit.py` (**24**) — the grade made falsifiable, so
that the day any of it stops being true something reds instead of a document
going stale. Sweep `tools/_sweep_iq1_iq1_5.json` (**23** mutations) **23 killed
/ 0 INERT / 0 BROKEN** at close.

⚠ **It took four rounds to get there, and every INERT was worth having:**

* **item (i)'s `spend > residual` clause was unpinned** — dropping it changed
  no arm's answer, because every big-spend turn on the spender arm happens to
  be spend-dominated. Answered with the case it exists for: a turn where the
  player spent and lost far more to everything else.
* **item (ii) had the wrong mechanism**, above.
* **both record pins were a bare `in` over a whole file** and were satisfied by
  a different occurrence — `6.0 → 6.5` occurs three times in this spec,
  `war_exhaustion` six times in `BUG_FIXES.md` — so deleting the sentence under
  test left them green. Scoped to §0.6b's body and the §Improvement Queue block.
  Same class as the FA dead-name pin whose fixed scrape overshot into the next
  endpoint's body.
* **three of my own mutations were invalid**, all the same shape: *weakening an
  assertion cannot make a test fail.* A mutation has to change behaviour, not
  delete a check. Recorded because I wrote that shape three separate times.
* **one mutation DETONATED** — renaming `NET_GOLD_COMPONENTS` breaks every
  importer at collection time, so no pin is ever evaluated. Re-sign a component
  instead of renaming the map.

**ROW IQ-1 IS CLOSED.** Four slices landed (IQ1-0, IQ1-1, IQ1-2, IQ1-3), the
exit held, three of four completion items MET, the fourth measured-open with a
named owner, GR9-clean.

---

### §0.6 THE REMAINING SLICES

**IQ1-3 — "The Recurring Obligation": the sink is a rate the player chooses
and WANTS.** The one surviving design of three, and the only shape measured
capable of absorbing a rate: **only a rate can absorb a rate.** Every purchase
in the game is capped by a non-gold quantity — **97** building slots on the
whole 126-province map (France 13; 49 of 126 provinces are town/rural with
**zero** slots), a 30,000-gold commission bench each hirable once, ships at
1–2 keels a turn, and `max_admin_actions` a hardcoded **2**, which caps the
*tempo* of buying rather than the menu. **Shape:** a per-turn
**subsidy / retainer** — France pays a court to stay out of the coalition or
into the field — riding `instruments.py`, which already ships a directed
per-turn payment with a renege path, a lapse path and a cancel verb, and whose
ceiling is *courts × what they will take* rather than slots, pools or
provinces. It answers **(a)** because it is what a player with 88,556 gold,
threat 77 and a coalition brewing actually wants, and **(b)** because the
price rises with the threat the player's own success creates.
⚠ **It prices the coalition, which is IQ-3's row** — the two must be sequenced
together or the second will re-tune the first.
**Riders, each with a completion definition so neither becomes an open
deferral:** the `get_levy_status` discoverability field + region-panel chip
(§0.5-7), and `substitutes_purchased` reaching the campaign log for non-player
courts (§0.4).
**Rejected with reasons, so they are not re-proposed:** an Establishment that
raises stability (circular with the slice meant to lower it, and refused
outright by `region.can_build`'s `stability <= 50` gate on exactly the
provinces that need it); Grand Works selling artillery/cavalry ceilings (the
pools sit AT `MAX_*_POOL`, and there are **zero artillery marshals** on the
board — counted, all eleven nations; cavalry = 1, Murat — while
`marshal.artillery` is set by no backend code path and `_execute_recruit`
picks the arm *from* the marshal); magazines (**729 gold over 40 turns across
all twenty nations**, France 0 on 40 of 40).

**IQ1-3a — "The Compacts Line": the recurring obligations become signed Net
lines.** Closes the rest of (iii). Deliberately out of IQ1-2 because it is
harder than it looks: granting a 200g/turn `directed_sponsorship` moves
`_build_economy`'s Net by exactly **0** while `process_instruments` debits the
chest, and the only surface that names it is prose on the Diplomatic Ledger.
But `process_instruments` is a **transfer**, not a debit, it **clamps** to
`min(amount, max(0, payer_gold))`, and it runs **after** `process_income_phase`
— so a payer-only forecast component ships shown ≠ applied on its first partial
payment and leaves the recipient's rise unnamed. It must use the
`_applied_income_transfers` idiom that `treaty_gold`, `vassal_tribute` and
`settlement_gold` already use, on **both** sides. ⚠ It must **not** reuse the
label *"Compacts"* — `instruments.build_instruments_line` already produces a
`Compacts:` line on the Diplomatic Ledger (R7 collision).

**IQ1-4 — question (c): ROUTED OUT TO ITS OWN DESIGN GATE.** *User ruling,
September 13, 2026.* (c) is real and measured: at identical territory and
identical army a wrecked France and a winning France pay **identical** costs,
and after a peace a beaten France (94,500 men, 23 provinces) **out-earns** a
victorious one (189,000 men, 28 stable provinces) by **+325 g/turn**, rising to
**+1,717 g/turn** eight turns later, because the upkeep relief for losing half
the army is 1,878 g/turn while the whole condition-charge handicap is **0 gold
at the treasury floor**. On the commanded arm France's military bill fell
**2,224 → 592** as its army bled ~111,000 men while income **rose** 3,400 →
3,550. Every route measured closed: the upkeep seam is the **user-directed
EC-U1 reversal**; a rate term is worth **zero gold to a broke loser by
construction** (`(treasury − 2000) × rate // 2500`, and the maximum boot chest
anywhere is exactly `CHARGES_HOARD_FLOOR`); retaining `campaign_ledgers` past
the peace is a **P1 regression** (§0.9); and a flat chest-independent charge is
a new SHAPE the PT-J3 gate already rejected on this very term, the first drain
the E6 bankruptcy mercy was not designed for, and — with `sandbox_mode`
suppressing defeat — the mechanical half of a defeat condition arriving before
IQ-2 has built the honest surface for it. **The one live candidate is pricing
RECOVERY rather than position** — replacing what a defeat destroyed should be
dear — which needs a design answer before a build contract. **IQ-1 closes on
(a), (b), (d) with (c) handed off, owner named, GR9-clean.**

~~**IQ1-5 — "The Exit": the ratio's replacement and the pillar re-score.**~~
✅ **HELD September 14, 2026 — landing record §0.6b.** No production code. The
four completion items measured on committed archived arms with the re-stated
predicates of §0.7, plus the acceptance test for (iv) written as arithmetic
over the production formulas with a **negative control that FAILS at the
pre-row value** (the IGR-E pattern). Economy pillar **6.0 → 6.5**; §0.8's
re-open condition does not fire. The brief below is kept for its two
instrument cautions, both of which the exit honoured.
⚠ Two instrument facts it must respect: there is **no post-SW-0 archived
AMBIENT arm**, so the ambient half of the completion definition has no
baseline until one is taken; and `--archive` copies `digest.md` and
`meta.json` only, **never `digest.jsonl`**, so SW-0's per-nation `purses` — the
GR5 falsifiability instrument — reaches no committed archive.
⛔ **Do not grade the exit on `commanded_spender40.json`**: its arm loses five
provinces and pays an indemnity the lever-shut control does not, so it would
score a collapse as a sink.

### §0.7 THE RE-STATED COMPLETION ITEMS

**⚠ Both are RULED — FOR USER CONFIRMATION**, because each grades the row.

**▶ MEASURED AT THE EXIT, September 14, 2026 — §0.6b is the record.**
**(i) MET** · **(ii) measured FALSE**, and the row does not close it: it is a
**ratchet**, the beaten France out-earning the victorious one by **+723 g/turn
and rising** by turn 8, handed to question (c)'s design gate · **(iii) MET for
18 of 19 gold streams**, `process_instruments` measured moving the chest 200
and Net 0, owned by IQ1-3a′ · **(iv) MET**, `the_chest_is_convertible` with a
negative control that fails in both directions, mutation-proven.

**(i) "the treasury is not monotonic"** — already satisfied, for the wrong
reasons. It measured true on arms where France was **losing** (the pre-PR-1
commanded arm), **broke** (the ambient arm, 23 drops) and on a **lever-shut**
spender control (one drop, zero purchases). **Re-stated:** *at least N turns
whose treasury fall's largest single term is a **player-initiated spend
recorded in `gold_spent_this_turn`**, with province count non-decreasing
across those turns.* Which is why it depends on IQ1-2 making `spent` readable
at all. *First evidence, on a 6-turn spender probe at HEAD: 15,412 → 11,722 on
the turn a 7,257-gold purchase landed, provinces 29 → 29.*

**(ii) "a losing France's Net is worse than a winning France's AT THE SAME
ARMY SIZE"** — already true at every treasury, in both independent measurement
fleets (magnitudes differed, sign did not), because **holding army size
constant holds constant the one thing a defeat changes**. A pin written to that
wording ships **green over a live defect**. **Re-stated:** the replacement must
let the army **fall** and must run the engine's own recovery ticks — the
inversion only appears from about turn +2 after the peace.

**(iv) the denominator is ambiguous and must be decided before the test is
written.** The same pricer returns **150** at the capital, at peace, under the
force limit, and **654** at the shipped boot — a 4.4× ambiguity — and a census
of all archived digests finds the modal *delivered* purchase is **3,000 men for
200 gold**, with *"10,000 men for 150 gold"* occurring **once**. A purse : price
ratio is a weak instrument. The stronger replacement is the treasury's own
**fixed point** read through `state_charges_ceiling` (now that IQ1-2 makes it
correct) **plus the standing obligations**, against the chest the arm actually
reaches.

### §0.8 THE ROW'S DISSENT AND ITS RE-OPEN CONDITION

The row had **neither**, which is a GR9 breach on the row itself — and its own
exit clause instructs that *"the row's dissent is read and its re-open
condition taken"*. Both are filed here.

**DISSENT.** One of three independent designers argued against the IQ1-3
subsidy/retainer shape on the ground that paying Europe to stay quiet *"makes
a winning game easier rather than a losing game more expensive."* It is a real
objection and it is **overruled** — because it is the only shape measured
capable of absorbing a rate, and because it makes wealth conditional on the
threat the player's own success creates. Recorded so it can be re-opened if
the mechanic fails **once**.

**RE-OPEN CONDITION, stated in advance.** If the economy pillar does not move
off **6.0** after IQ1-3 lands, the re-open is the **stability ratchet** this
row deliberately does not touch — with its own measured caveat that on the
disease arm **28 of France's 29 provinces are homeland**, so a
homeland/conquest split has almost nothing to bite on there.

**▶ RESOLVED September 14, 2026 — it does NOT fire.** The exit re-scored the
pillar **6.0 → 6.5** (§0.6b), so the ratchet is not re-opened. Two things are
kept rather than discarded with the condition: the homeland caveat above,
which would have blunted the ratchet anyway, and **the dissent itself, which
stands unretracted** — the control arm ends on the same **88,556 gold** the row
opened on, which is exactly the dissent's point that a sink a winning player
may decline leaves a winning game easy. It is now carried by **IQ1-3e** (the
(b) residual, economy-wide) and by the **(c) design gate**.

### §0.9 CLAIMS KILLED BY MEASUREMENT — do not rebuild these

Each was proposed by a designer and killed by a refuter or by me reading the
symbol. They are recorded so the next session does not re-propose them.

1. **"Make the pension memory survive the peace / stop popping
   `campaign_ledgers`."** A **P1 regression**, and the line documents why: its
   own comment records that the typed vassalization arm once failed to pop and
   was *"leaking pensions forever AND PRELOADING A FUTURE REBELLION WAR WITH
   THE DEAD WAR'S CAPTURES AND BLOOD"*. `calculate_war_score` reads
   `campaign_ledgers[diplo_key]` for **three** live components — captures,
   casualty differential and HC-1's blockade score — keyed on the **pair**, and
   the writers `setdefault` and append. Three more consumers depend on the pop.
   Retaining it opens the next France–Austria war with the last one's score
   already on the board.
2. **"Add an always-on province-count / extent term to
   `get_state_charges_rate`."** Reds three blessed pins whose class docstring
   quotes the user's own sentence, and reverses the August carve-out. Any
   always-on term is a **shape** change that escalates (§0.2).
3. **"Key a recruit/substitute scarcity price on men lost in battle."**
   **Combat never touches `manpower_pools`** — `grep manpower` over
   `combat.py` and `combat_executor.py` returns nothing. `scarcity` measures
   cumulative **recruiting**, not losses, so *"the men you lost cost more
   because you lost them"* is false as a mechanism. And
   `_calculate_recruit_cost` takes no arm type while the three pools are
   separate, so an infantry-keyed scarcity would price a cavalry batch by the
   infantry class's emptiness.
4. **"A Foundry raises the artillery ceiling, so gold finally buys guns."**
   **Zero artillery marshals on the board** (see §0.6). The binding constraint
   is `MAX_CAVALRY_POOL` / `MAX_ARTILLERY_POOL`, not the regen ceiling. And
   `naval.check_build_fleet` already prints *"Time, not gold, builds a navy"* —
   a gold-bought keel rate contradicts a line the game says out loud.
5. **"IGR-X9 (a ruin bills nothing) is still open."** It was **decided and
   fixed** at the August 7 Econ Balance gate (EB-3.2) and does not reproduce at
   HEAD: `calculate_turn_income` counts only `not b.get('damaged')` buildings
   and a watchtower only at `== 'active'`. **Struck from the row's Absorbs
   list.** The still-open neighbour is **CA8-D1** (the building-slot ceiling),
   whose measurement reproduces exactly: France holds **13 of the map's 97**
   slots.
6. **"ES-4 'development' is absorbed by this row."** Recorded on one side only
   — `ECONOMY_REVISIT_SPEC.md` still assigns it to *"EC-2 pass 2 … USER DESIGN
   GATE"* and never mentions IQ-1. **Handed back**, because it *raises* income
   and is a want, not a recurring drain.

### §0.10 THREE FIGURES IN THE ROW'S OWN CONTRACT THAT DO NOT REPRODUCE

Corrected in `docs/STATUS.md` in the same slice, because one of them is a
**completion criterion**.

1. **457×** appears three times in STATUS, once as *"an acceptance test states
   the 457× ratio's replacement"*. The memo STATUS itself names authoritative
   (`PLAYTEST_RESCORE_2026_09_12.md`) says **590×**; 88,556 / 150 = **590.4**,
   82,524 / 150 = 550.2, and 457 × 150 = 68,550 — a treasury in no published
   figure. **Corrected to 590×, derivation shown.** ⚠ Confirming the figure,
   not merely the correction, is the user's, because it grades the row.
2. **"upkeep falls 2,224 → ~450"** — the 40-turn minimum on the commanded arms
   is **592** and turn 40 reads **624**; ~450 occurs only on collapsing arms.
3. **"Threat FALLS 68 → 44"** is the `--diplomacy propose` arm, while **88,556**
   is the **commanded** arm — whose threat goes **76 → 77** and which ends with
   a coalition brewing at 77. The four disease bullets silently mixed two
   boards.

---

## §1 — ROWS IQ-2 … IQ-10

Their scope, evidence and completion definitions live in `docs/STATUS.md`
▶ NEXT UP and are normative there; their landing records are filed here as
each is taken.

### §1.1 LANDING RECORD — IQ-2 "The Collapse Is Legible" (✅ September 14, 2026)

**Authoritative record = `docs/BUG_FIXES.md` §Collapse Legibility (IQ-2)**
(the rows, the review round, the sweeps); rules = `docs/SYSTEMS_REFERENCE.md`
§41. Commits `87f5459a` (build) → `f586484f` (review round) → `5c41532d`
(lens 7) → the merge with row IQ, which added the war-purpose fix below.
⚠ This row was BUILT in a session whose local master predated the queue's
opening; its contract came from the user's own description, which matched
this row, and the two were reconciled at the merge.

- **The completion item is MET and pinned.** On a staged zero-province board
  driven through one real `end turn`, the briefing's lead is the new standing
  class `empire_reduced` (*"France holds no province of her own…"*), no
  producer claims a holding France does not hold (situation, ledger
  territories, levy, and a Defence war-purpose line that now names only what
  is HELD or says *"the homeland is lost"* — `WAR_PURPOSE_LISTS_ONLY_WHAT_IS_HELD`),
  and Talleyrand no longer tells an annihilated France the winds favour it —
  `test_iq2_collapse_integration.py::TestTheIQ2CompletionDefinition`.
- **The scope note held.** `sandbox_mode` is untouched; nothing ends, blocks
  or shortens the campaign, and no sentence promises an ending. The one
  sentence that answers "does this end the game?" is
  `collapse.CAMPAIGN_CONTINUES`.
- **A mechanical P1 sat underneath, found by the row's census:** at zero
  provinces France fell off `get_active_nations()` and fielded a FREE army —
  no upkeep, bankruptcy or desertion, recurring settlement gold cancelled as
  "payer_eliminated". `world_state.PLAYER_NEVER_LEAVES_THE_ROSTER` closes it;
  it interacts with IQ-1's economy only by making the landless realm pay the
  bill every other realm pays (the IQ-1 suites are green on the merged tree).
- **One source** — `backend/game_logic/collapse.py` — feeds every collapse
  surface. **Not built, owned:** a collapse is not a terminal state (the
  Victory & Objectives Pass, ROADMAP 12–13); IQ-10 carries the visual
  sign-off on the IQ-2 client surfaces (the collapse line on the turn banner,
  THE EMPIRE IN EXTREMIS, the no-field-army sentence, the closed-depot and
  tier-side renders) — the parse harness and a boot smoke passed in this
  session, the eyes-on pass is IQ-10's. **IQ-10 is blocked on environment** — no Godot
binary in this container — and carries every open visual sign-off with it,
including IQ1-2's `strategic_ledger.gd` render arm.

**⛔ Win conditions are excluded from every row by user direction.**
`sandbox_mode` suppresses victory *and* defeat on every Europe world, and that
belongs to the Victory & Objectives Pass, ROADMAP positions 12–13. No IQ row
builds it or half-builds it. IQ-2 makes the collapse *legible* without making
it *terminal*, and its scope note says so in writing.
