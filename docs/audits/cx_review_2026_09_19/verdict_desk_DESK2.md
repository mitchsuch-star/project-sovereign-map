# VERDICT:DESK-2 — **CONFIRMED, and wider than filed**

Refutation pass at master `727cf88a`, clean. Default verdict was REFUTED; the
row survives it. My probes are in
`…/scratchpad/cx_review/probes/r_desk2/` (`rh.py` + `r01`…`r06`), independent
of lens 3's harness. Every figure below is one I measured, on a **fresh**
shipped 1805 board per arm, driven through `POST /command` (the production
surface) unless stated.

**Verdict in one line:** the defect is real, is CX-2's, reaches the player, and
is **larger than the row says** — but **three of the row's own statements do not
reproduce**, and **one limb of its fix shape would ship a regression**, so it
must not be built as written.

---

## 1. Does it reproduce? Yes — the core, exactly

`r01_reproduce.py`, fresh boot board per arm:

```
POST /command  "how much is a battalion"
  654 gold for 10,000 infantry, Sire, at Rhineland. The price rises at war
  and above the force limit.                              [AP 4 -> 4, gold unchanged]

POST /command  "recruit infantry in Rhineland"
  Davout recruits 3,000 infantry for Rhineland (field levy — no depot;
  capped at 3,000) - Cost: 741 gold (Davout's intendance: -15%)
  CHARGED 741   delivered {'Davout': 3000}

POST /command  "recruit infantry in Paris"     # the province 654 IS the price of
  FAILED — "No marshal is available to receive reinforcements at Paris, Sire."
```

`get_levy_status(w,"France")` key list measured:
`['army_strength','capital_held','closed_reason','force_limit','headroom',
'infantry_amount','infantry_pool','infantry_price','open','over_by',
'recipient_in_range','substitutes']` — **no `region` key**, so
`counsel._levy_terms`'s `levy.get("region")` is always `None` and the fallback
always fires. Confirmed.

Price decomposition (`r02`), which the row asserts but never shows:

| where | marshal | price |
|---|---|---|
| Paris (capital) | — | **654** ← what the desk quotes |
| Rhineland | — | 872 |
| Rhineland | Davout (−15%) | **741** ← what the executor charges |
| Rhineland | Ney (+15%) | **1003** |

The legacy end-to-end reproduces **verbatim** (`r03a`): counsel prints
`recruit infantry in Belgium — 150g for 10,000 men`; typing it returns
*"Berthier notes: 'Marshal Ney commands cavalry, Sire.'"* and **charges 300 for
3,000 cavalry**.

---

## 2. Three filed statements that do NOT reproduce

**(a) "`recruit for Ney` → charges 1003 gold for 3,000".** It does not charge.
On a fresh boot board France holds **800 gold**, so the order is *refused*:
`"The treasury cannot support this, Sire. Need 1003 gold, have 800."`
(`r01`). 1003 is the quoted need, not a charge. Correcting this **strengthens**
the finding — a player budgeting on the desk's 654 against an 800-gold chest is
refused outright — but the sentence as filed is wrong.

**(b) "`get_levy_status` already knows about the arm … and neither consumer
reads `open` or `closed_reason`"** — the implied remedy does not work on the
row's own flagship case. Measured on **legacy**, the board the row's end-to-end
uses (`r05a`): `closed_reason` is **`None`**, and contains neither "cavalry" nor
"horse". `LEVY_NAMES_ITS_RECIPIENT_ARM` inspects the **capital's** recipient
(Paris → Davout, infantry), while the counsel names **Belgium**, whose recipient
is Ney, cavalry. Reading `closed_reason` would **not** have caught the Belgium
case.

**(c) The mechanism is mis-stated as "no `region` key".** That is true but
secondary. `question_desk._first_own_region_with_a_corps` walks
`get_player_marshals()` in **roster order** and returns the first own-soil
location — it is not about the levy at all (`r04b`: roster order
`['Ney','Davout','Soult',…]` → `'Rhineland'`, while the levy's own recipient at
the capital is `None`). Supplying a `region` key would not fix it; the locative
is arbitrary **and** the price is wrong even when the locative accidentally
lands (see §3).

---

## 3. It is WIDER than filed — two things the lens never asked

**(i) The decisive arm: an OPEN levy is priced wrong too.** The row only ever
measures the closed-at-boot board, which invites the narrowing "it is only
wrong while shut". It is not. `r04`, standing one corps at Paris so
`recipient_in_range` is True:

| staged | desk says | the executor charges at the capital | at the province the desk NAMED |
|---|---|---|---|
| Davout @ Paris | 654 … at **Rhineland** | **556** (−15%) | 1003 for **3,000** |
| Soult @ Paris | 654 … at **Rhineland** | 654 ✔ | 741 for **3,000** |
| Ney @ Paris | 654 … at **Paris** ✔ | **752** (+15%) | 752 |

Shown ≠ applied in **all three**. When the locative is right the price is
wrong; when the price is right it is attached to the wrong province.

**(ii) The cavalry arm is worse, and untested.** `_answer_price` does
`levy.get(f"{what}_price") or levy.get("infantry_price")`, and `get_levy_status`
has no `cavalry_price`/`cavalry_amount` — so the fallback silently supplies the
**infantry** figures while the sentence still says "cavalry" (`r02`, `r05c`):

```
> how much does cavalry cost
  654 gold for 10,000 cavalry, Sire, at Rhineland.

> recruit for Murat            # Murat is France's only horse
  Murat recruits 3,000 cavalry at Franche-Comte … Cost: 1504 gold
> recruit cavalry in Rhineland # the province the desk named
  "Marshal Davout commands infantry, Sire." → 3,000 INFANTRY for 741
```

Price understated **2.3×** (654 vs 1504), amount overstated **2×** (10,000 vs a
5,000 cavalry batch), **and the named province holds no horse at all**, so a
levy there raises the wrong arm. `artillery` sits in the same tuple but the
classifier never produces it (`how much is artillery` → the shrug), so two of
the three arms are live and both are wrong.

---

## 4. Player-reachable? **Yes** — verified from `main.gd` source, not assumed

`main.gd:1688` is the only pre-send gate besides the redemption-token block.
`_redirect_diplomatic_command` calls `_is_advisory_question` **before** any
family match, and `DIPLO_ADVISORY_STARTS` (`main.gd:1997-2005`) contains
`"how"` and `"what"` — so `how much is a battalion`, `how much does cavalry
cost`, `what does a battalion cost` all return `false` = fail-open to
`api_client.send_command`. Confirmed live through `POST /command` (`r01`, `r03b`).

The **rider** is a different matter: `_levy_terms` returns `None` on 1805 boot,
fixture `t10` **and** fixture `t20` (`recipient_in_range` False on all three,
`r02`), so the counsel's priced line is **not** player-reachable in ordinary
1805 play — it renders only on legacy. The row's own test file already says so
at lines 422-423. Rider holds at **P3**.

---

## 5. Shipped by row CX? **Yes — definitively, commit `5fc3d5c8` (CX-2)**

`git show b4a27a15^:backend/ai/question_desk.py` has **no**
`classify_board_question`, no `_answer_price`, and zero occurrences of
`price`/`levy`/`infantry`/`battalion`; `backend/ai/counsel.py` does not exist at
`b4a27a15^`. Occurrence count of `_answer_price` by commit: `b4a27a15` → 0,
`5fc3d5c8` → 2. Both consumers are new in CX-2. Pre-row, `how much is a
battalion` was not classified at all.

---

## 6. Severity: **P2 holds, at the floor** — not P1

For: it is a money quote the player acts on with **no confirm step** (typing the
order charges immediately), the gap is 13–53% on infantry and 2.3× on cavalry,
and at boot it flips an affordability decision (quoted 654 against an 800-gold
chest; the corresponding order is refused at 1003).

Against P1: display-only — asking costs 0 AP and moves no gold (measured
`AP 4→4`, gold unchanged); no mechanic moves; the executor states its own true
price in the same breath as charging it; and the ledger's `cost_note` still
discloses *"Live price at the capital"*. Nothing is silently charged.

---

## 7. ⛔ The fix shape would ship a regression — one limb must not be built

**Do not gate the answer on `levy["open"]`.** Measured (`r05b`): with Davout or
Soult standing at Paris on the shipped board, `open` is **False**
(`headroom=0`, `over_by=59000`) and the typed levy nonetheless **succeeds and
delivers a full 10,000 batch** for 556 / 654 gold. `open` is the headline's
"worth announcing" bar, not a refusal — `economy_executor.py`'s own IQ-2 comment
says so in writing (*"the force limit prices the overage, it never refuses"*).
Gating on it would silence a correctly-priceable, working levy on every
over-establishment board, which at 1805 boot is **every** board.

**The pin the correct fix WILL red — and it is the row's own.**
`tests/test_cx2_berthier_answers_the_board.py::TestTheGuardsWhereTheyBite::
test_the_levy_line_is_PRICED_where_the_levy_is_open` (lines 536-557) asserts
`f"{levy['infantry_price']:,}g" in line` and
`f"{levy['infantry_amount']:,} men" in line` — i.e. it asserts the counsel
prints the **capital, marshal-less** price and the **full batch**. Pricing at
the named province with the receiving marshal, or quoting the delivered amount,
reds both assertions.

And that pin is **green about the defect**. Running its own staging and then
typing the line it asserts (`r06`):

```
staged recipient at the capital: Ney (intendance 1.15)
levy['infantry_price']  : 450
counsel line asserted   : recruit infantry in Paris — 450g for 10,000 men
TYPED "recruit infantry in Paris"
  Ney recruits 10,000 infantry … Cost: 518 gold (capital discount)
                                       (Ney's intendance: +15%)
>>> QUOTED 450g / CHARGED 518g
```

The slice's own "shown = applied" pin passes on a 15% gap, because it compares
the renderer against **the same weak source the renderer reads** — never against
the executor. The re-pin must drive `POST /command` and compare the quoted
figure to the gold actually taken.

`tests/test_cx2_berthier_answers_the_board.py:137`
(`("how much is a battalion", ("gold","infantry"))`) is a substring pin and
survives any correct fix.

**Safe fix shape:** price through `_calculate_recruit_cost` at the province the
sentence names, passing the marshal `find_nearest_marshal_to_region` would
actually hand the recruits to; quote that marshal's **arm** and the amount
`_execute_recruit` would deliver there (the CO-4 field cap); leave `open`
alone. That closes the infantry arm, the cavalry arm and the locative in one
seam, and it is a read of the same functions the executor calls — no new state,
no gate.
