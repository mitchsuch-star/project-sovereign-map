# VERDICT:DESK-5 — NARROWED

**The reproduction is exact and the defect is real, player-reachable and shipped
by CX-2. The severity is P3, not P2, and two of the row's supporting claims do
not survive. One part of the harm is UNDER-stated, and the lens's own first fix
arm reds a pin.**

Master `727cf88a`, clean tree. Every figure below is from a probe I ran, under a
`LLM_MODE=mock` client with `tests._parser_replay.install_network_guard()`
installed, driven through `POST /command`. Probes:
`…/scratchpad/cx_review/probes/rh_desk5.py` + `r1_repro.py` + `r2_gate_and_pin.py`
+ `r3_share.py`.

⚠ **A harness hazard I hit and am reporting because the next reviewer will hit
it.** `CommandParser`'s first positional is `use_real_llm`, **not the world**
(`parser.py:727`). My first harness passed the world there — truthy — and the
boot log read `provider=ANTHROPIC, key_source=inhouse`. Every number below was
re-taken under `CommandParser(False)` with the network guard installed and the
key popped from the environment. Separately, the committed save's world lives
under `world_state`, not `world`: reading the wrong key makes `from_dict`
silently return a **default legacy 19-region world**, and my first t20 run
"measured" `income 1,100 / upkeep 865 / Net +285` on a board that was not the
fixture. Both probes now assert (`provider == "mock"`, `current_turn > 1`).

---

## 1. Does it reproduce, exactly as stated? YES — to the digit, on both boards

```
### shipped 1805 boot, through POST /command
> what's my income
   The treasury holds 800 gold, Sire. The provinces yield 3,400 and trade 350;
   the army costs 2,630. Net +1,842 a turn. The full account is in the
   Strategic Ledger's Economy tab (press T, then 3).

   components sum = +1,842   econ[net] = +1,842   (the LEDGER reconciles: True)
   NAMED (3,400 + 350 - 2,630) = +1,120   STATED Net = +1,842   GAP = +722
   omitted: vassal_tribute +937, blockade -175, admiralty -90, admin_bonus +50

### committed fixture t20, through POST /command
> what's my income
   The treasury holds 17,487 gold, Sire. The provinces yield 2,350 and trade 350;
   the army costs 980. Net -876 a turn. …

   components sum = -876   econ[net] = -876   (the LEDGER reconciles: True)
   NAMED (2,350 + 350 - 980) = +1,720   STATED Net = -876   GAP = -2,596
   SIGN FLIP = YES
   omitted: state_charges -2,868, vassal_tribute +487, blockade -175,
            admiralty -90, admin_bonus +50
```

Both the +722 and the −2,596 reconcile exactly against the components the row
named. The row's arithmetic is right.

**And the inversion is not a fixture artefact.** Sweeping only the chest on the
boot board, every other value held constant:

| treasury | named | Net | gap | charges | flip |
|---|---|---|---|---|---|
| 800 | +1,120 | +1,842 | +722 | 0 | |
| 17,487 | +1,120 | +1,347 | +227 | 495 | |
| 25,000 | +1,120 | +1,106 | −14 | 736 | |
| 40,000 | +1,120 | +626 | −494 | 1,216 | |
| **88,556** | +1,120 | **−927** | −2,047 | 2,769 | **YES** |

88,556 is not a number I chose: it is the chest `IMPROVEMENT_QUEUE_SPEC` §0.6
measured for a **commanded France at turn 40**. The flip is the ordinary
late-game state of a hoarding France, which IQ-1 measured as the normal one.

**I also measured the third board the row did not, and it argues the row's
case better than the row does** (`r1_repro.py`):

```
[t10] turn=10 gold=16,495
   "…provinces yield 3,352 and trade 350; the army costs 1,512. Net +1,441"
   NAMED = +2,190   Net = +1,441   GAP = -749   SIGN FLIP = no
   omitted: state_charges -1,246, vassal_tribute +712, …
```

No sign flip at t10 — and the defect is still there, because the **largest
single outgoing is the one the sentence does not name.** That holds on both
played fixtures (`r3_share.py`):

| board | outgoings | what "the army costs N" names | biggest outgoing | named? |
|---|---|---|---|---|
| 1805 boot | 2,895 | 2,630 = **90.8%** | upkeep_base 1,512 | yes |
| t10 | 3,023 | 1,512 = **50.0%** | state_charges 1,246 | **NO** |
| t20 | 4,113 | 980 = **23.8%** | state_charges 2,868 | **NO** |

**This is the better statement of the harm, and the row under-states it.** The
row leads on the sign flip, which fires on one board. The misdirection fires on
every played board: the sentence names the army as the only cost, and by t20 the
army is 23.8% of the outgoings while the term it hides is 2.9× larger. A player
trying to fix a deficit is pointed at his army.

## 2. Player-reachable? YES — confirmed by re-implementing the client gate

`r2_gate_and_pin.py` parses the three keyword arrays out of `main.gd`
(115 family + 18 no-home + 2 war-room) and runs
`_redirect_diplomatic_command` / `_is_advisory_question` over the utterances:

```
"what's my income"          -> reaches backend  (no family match -> fail-open)
'what is my income'         -> reaches backend  (advisory question -> fail-open)
'how much gold do we have'  -> reaches backend  (advisory question -> fail-open)
"what's our revenue"        -> reaches backend  (no family match -> fail-open)
'how much money do we make' -> reaches backend  (advisory question -> fail-open)
```

Not one of the 135 redirect keywords mentions gold, income, treasury, money,
revenue or finance (measured, not assumed). Four of the five then reach the arm;
`how much money do we make` gets Berthier's shrug (a classification gap, not
this row's).

## 3. Shipped by row CX? YES — and it is NOT a regression

`git log -S "_answer_treasury" -- backend/ai/question_desk.py` returns exactly
one commit: **`5fc3d5c8` (CX-2)**. `git show b4a27a15^:backend/ai/question_desk.py`
is 353 lines and contains **zero** occurrences of treasury / income / economy;
its `_KINDS` table is `where / who_holds / who_at / doing / how_many` only, none
of which matches "what's my income".

So pre-row the utterance got Berthier's shrug — which is what
`how much money do we make` still gets today, down the same path. **The row
replaced no answer with a partial one.** That is context a builder needs and the
row does not give: nothing was lost here, something incomplete was gained.

## 4. Why P3 and not P2

The row's own label is *"a false account."* **No figure in the sentence is
false.** Treasury, income, trade, upkeep and Net are all `_build_economy`'s own
applied values; the ledger reconciles on all three boards (`components sum ==
econ[net]`, measured True everywhere).

The closest precedent in this codebase is **CA8-10, rated P2**
(`CREATIVE_AUDIT_2026_08_04.md:508`) — *"the two screens reporting income
disagree by 124%"*. The decisive difference: **CA8-10's Net was itself wrong**
(`+926` against a true `+2,073`), so a player acting on the headline acted
wrongly. Here the headline Net is the ledger's own reconciled figure and is
printed in the same breath. To conclude he is making money on t20 a player must
ignore the sentence's own stated conclusion (`Net -876 a turn`).

That also separates it from its three P2 siblings in the same report. DESK-1
(fogged province), DESK-3 (yes across a barred crossing) and DESK-4 (muster
against an ally) each end with the player **acting and being refused**. DESK-5
has no such act.

What survives at P3 is real and worth building: the player asks *why* and the
answer cannot tell him, while pointing at the wrong culprit.

## 5. Two supporting claims that do not survive

**(a) The SC-33 appeal is an over-reach.** The row says this is *"the one place
the desk departs from the SC-33 contract the ledger holds to."* SC-33 is scoped
in writing to the ledger screen — `ECONOMY_REVISIT_SPEC.md:361` binds
*"the **rendered** strategic ledger economy tab (Godot `strategic_ledger.gd
_render_economy`, not merely the backend `ledger.py:_build_economy` dict)"*,
pinned by `tests/test_economy_ledger_reconciliation.py`. The desk is a different
surface and was never inside that contract.

**(b) The row implies CX-2 broke its own promise. It did not.** The spec's
promise (`COMMAND_EXPERIENCE_SPEC.md:313-316`) is *"Every answer reads the seam
the MECHANIC reads … So a quoted figure is the applied figure."* Every one of
the four quoted figures **is** the applied figure. The defect is that the
sentence's grammar — *"yields X and trade Y; the army costs Z. Net N"* — implies
a closure the promise never made. That is a copy defect, not a broken contract,
and saying so correctly is what keeps it at P3.

## 6. Would the suggested fix ship a regression? Arm (a) YES

The row offers two arms. There is exactly **one** pin over this sentence —
`tests/test_cx2_berthier_answers_the_board.py::test_the_treasury_figures_are_the_ledger_s`
(:205–212):

```python
message = ask("what's my income").get("message") or ""
assert f"{int(economy['treasury']):,}" in message
assert f"{int(economy['income']):,}"   in message      # <- line 211
assert f"{int(economy['net']):,}"      in message
```

Simulated against both arms (`r2_gate_and_pin.py`):

| | treasury | income | net | |
|---|---|---|---|---|
| SHIPPED | ✓ | ✓ | ✓ | GREEN |
| **arm (a)** "drop the derivation, give treasury + Net + a pointer" | ✓ | **✗** | ✓ | **RED (income)** |
| arm (b) "name the top signed component by magnitude" | ✓ | ✓ | ✓ | GREEN |

**Arm (a) reds line 211.** Arm (b) is pin-free and is the one to build.

Two riders for whoever builds it:

* **The pin that should have caught this never checks reconciliation.** It
  asserts the *presence* of 3 of the 4 figures and nothing about whether they
  sum — it is green about the defect, and would stay green if `upkeep` were
  hardcoded to 0. This is the repo's own recorded failure mode. A fix that does
  not add the reconciliation assertion leaves the next truncation to land the
  same way.
* **"Name the top signed component" is wrong at boot.** The largest omitted
  component there is `vassal_tribute **+937**` — an inflow, not a cost — and
  `state_charges` is 0 below `CHARGES_HOARD_FLOOR = 2,000`. An arm that names
  the Charges unconditionally prints "Charges of Empire 0" on turn 1, which is
  the wart the typed report already has (measured: *"Charges of Empire: -0g"*).
  Rank by magnitude over the omitted set, sign included, or say the account is
  partial.

## 7. Worth knowing: the correct surface already exists and is two keys away

The typed `economy` / `treasury` verb reads the same `_build_economy` and names
**every** signed component, reconciling to the gold (`v3b_out.txt`):

```
  Trade: +350g      Blockade: -175g      Vassal tribute: +937g
  Charges of Empire: -0g   Admiralty: -90g
  Upkeep: -2630g (8 marshals) … Over force limit (189,000 / 130,000): -1118g surcharge
  Admin bonus: +50g        Projected net: +1842g       Treasury: 800g
```

That surface was fixed for **exactly this defect class** in CA8-10, August 2026,
with a comment that reads *"A new player literally cannot answer 'how much money
do I make.'"* CX-2 re-introduced the truncation in a new surface answering the
same question. The recurrence is the strongest argument for building it — and
the cheapest fix is to make the desk's sentence say the two things the typed
report already says.

---

**Verdict: NARROWED. Reproduces exactly; real; player-reachable; shipped by
CX-2; not a regression. Severity P3 (not P2) — every figure is true and the
actionable Net is correct. The SC-33 and broken-promise sub-claims are struck.
The harm is better stated as coverage of outgoings falling 90.8% → 50.0% →
23.8%, with the largest outgoing unnamed on both played boards. Build arm (b);
arm (a) reds `test_the_treasury_figures_are_the_ledger_s:211`, and the pin needs
a reconciliation assertion either way.**
