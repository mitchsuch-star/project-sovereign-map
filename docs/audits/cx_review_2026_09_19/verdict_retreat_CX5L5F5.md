# VERDICT: CX5-L5-F5 — **NARROWED**

**Tree:** `master 727cf88a` (+ the docs-only `f52df77f`), **clean throughout** —
`git status --short` empty before and after. Everything below measured by my own
probes on the shipped 1805 board (`parser_eval.build_world("1805")`) driven at
`POST /command` through `TestClient`, one FRESH board per utterance,
`LLM_MODE=mock`, zero live calls. Probes:
`probes/p1_which_group.py`, `p2_do_the_offers_execute.py`,
`p3_vocab_and_fix_cost.py`, `p4_client_reachability.py`, `p5_apply_the_fix.py`,
`p6_edges.py`, `p7_lever.py`, `p8_bare_lever_msgs.py`. Nothing under the repo
was modified; the fix trial ran on a `git archive` copy in the scratchpad,
deleted afterwards.

---

## ONE LINE

The mechanism is real and I reproduced it — but the finding's load-bearing
premise (*"every CX-5 refusal is an ADDRESSED order"*) is **measurably false**,
its title's verdict on the record is **half right** (the record's *claim* is
true; only its *because* is wrong), its own rhetorical centre is **inverted for
the ten cases it reproduces**, and **its suggested fix, applied verbatim, reds a
pin and makes the copy worse**. **P3 → P4.**

---

## WHAT REPRODUCED, EXACTLY AS FILED

**(1) Three template groups, only `else:` calls `_counsel_lines`.** Confirmed by
reading `llm_client.py:1349-1404` and, decisively, by byte-diff:

```
$ git diff b4a27a15^ HEAD -- backend/ai/llm_client.py | grep -c "^[-+].*recognized_marshal"
0
```

**Zero changed lines** in the `recognized_marshal` block across all six row-CX
commits. The block is byte-identical to `b4a27a15^`. So the defect as titled is
**PRE-EXISTING**, and `shipped_by_this_row: false` is right.

**(2) The canned rotation, with Paris hardcoded.** Driven, `random.choice`
forced to each index in turn, `Lannes, cut off the retreat`:

```
[0] Berthier adjusts his spectacles. "Sire, I understand this concerns Marshal
    Lannes, but I cannot determine the order. Perhaps: 'Lannes, attack Mack' or
    'Lannes, move to Paris'?"
[1] Berthier frowns at the dispatch. "I see Marshal Lannes's name, Sire, but the
    instruction is unclear. Valid orders include: attack, move, scout, defend,
    fortify, recruit."
[2] "Sire, Marshal Lannes awaits your command, but I cannot parse this order.
    Might you mean 'Lannes, scout' or 'Lannes, defend'?" Berthier asks carefully.
```

30 driven rows (10 utterances × 3 forced indices): **27 in the
`recognized_marshal` group, 0 in the counsel group, AP 4→4 on every one.**

**(3) The vocabulary arithmetic is exact.** `recovery_action_vocabulary("typed")`
= **53** verbs; `"retreat"` present at sorted index **43**; the rendered sample is
`attack, move, scout, defend, fortify, recruit` and is *exactly* the hardcoded
lead, because `[:max(0, 6 - len(_lead))]` slices `[:0]`. The finding's "53" and
"hardcoded to six that exclude it" are both correct to the digit.

**(4) The word `retreat` never appears in any shrug.** Confirmed across all 30
rows.

**(5) Nothing states the rule.** Confirmed — no message on any road tells the
player a marshal will not act on another army's retreat.

**(6) Player-reachable.** I extracted all twelve `DIPLO_*` const lists out of
`main.gd` (**191 literal forms**) and mirrored `_redirect_diplomatic_command`
over all ten refusals plus the two regressed forms: **12 of 12 fail-open → SENT
TO BACKEND.** `"retreat"` is indeed in `DIPLO_ADDRESS_EXEMPT_WORDS`;
`"withdraw"` appears nowhere in `main.gd`. **Reachability confirmed.**

---

## WHAT DID NOT SURVIVE

### A. ⛔ "Every CX-5 refusal is an ADDRESSED order, so `recognized_marshal` is always set" — **FALSE, and it is the premise the whole finding rests on.**

CX-1 made an address need no comma, and the act-on-retreat family is typeable
**bare**. Those sentences are *also* CX-5 refusals, and they land in the **ELSE /
counsel group** — the one CX-2 rewrote:

```
'cut off the retreat'   -> Berthier clears his throat. "…Our marshals (Ney, Davout,
                           Soult) await clear commands — 'Ney, attack Mack',
                           perhaps? For any matter of state, press F1 for the Cabinet."
'press the retreat'     -> "…A clear order might be: 'Ney, attack Mack' or
                           'Ney, march to Lorraine'. For any matter of state, press F1…"
'exploit the retreat'   -> (same ELSE-group template)
```

Lever-attributed over both arms of `llm_client.A_RETREAT_CAN_BE_A_NOUN`:

| family | HEAD | lever DOWN (pre-CX-5) |
|---|---|---|
| the record's TEN (addressed) | 9/10 canned group, **0/10 counsel** | 7/10 **retreated** |
| the BARE family (6 forms) | **6/6 COUNSEL group** | 6/6 **general retreat** |

And what the bare form did before CX-5 is worse than anything the finding filed:

```
A_RETREAT_CAN_BE_A_NOUN = False,  'cut off the retreat'
  -> "General retreat ordered! Ney falling back! Davout falling back! Soult
      falling back! Lannes falling back! Murat falling back! Bernadotte falling
      back! Massena falling back! Napoleon falling back!"
     moved = all EIGHT French marshals, the Emperor included
```

So **half the CX-5 refusal family reaches the CX-2 road, and on that half the
record's justification is true and live** — with a counsel line derived from the
board and the Cabinet door. The finding measured only the addressed half and
generalised.

### B. ⛔ "Verified for all ten refusals — every observed message is one of those three" — **FALSE. It is 9 of 10.**

`Lannes, harry the retreat` never reaches `_berthier_mock_response` at all
(instrumented: the wrapper is never called). It returns the PURSUE refusal:

```
Lannes, harry the retreat -> "Cannot find 'Retreat' to pursue."
```

The lens's own **F6 and F8 both say this**; F5 contradicts them.

### C. ⛔ The title's verdict — *"the landing record's justification is false for this fall-through"* — **is half right, and the wrong half is the one the title names.**

The record (`COMMAND_EXPERIENCE_SPEC.md:452-455`) says:

> *"Since CX-2 the shrug answers with orders that would actually be carried out,
> so that fall-through is now useful rather than bare."*

**The substantive claim is TRUE.** Driven end to end on the boot board:

```
Lannes, attack Mack    success=True  AP 4->3   MUSTER — Lannes (18,000; 82,340 if all march…)
Lannes, move to Paris  success=True  AP 4->2   marches, Nivernais -> Burgundy -> Limousin -> Paris
Lannes, scout          success=True  AP 4->3   scouts Swabia / Lorraine / Munich
Lannes, defend         success=True  AP 4->4   accepted; Lannes objects (a legitimate beat)
Lannes, fortify        success=True  AP 4->2   complies
Lannes, recruit        success=False AP 4->4   "Need 872 gold, have 800."
```

**5 of 6 execute.** The sixth, `recruit`, is board-refused for 72 gold — and it
appears **verbatim in CX-2's own `else:` template[1]** (*"Valid actions include:
attack, move, scout, defend, fortify, recruit"*), so it is not a contrast
between the two groups at all. The finding concedes this itself
(*"they are not lies"*) and then titles the row as though the justification
failed.

**What IS false is the word "Since".** `_hostile_first` / `BERTHIER_NAMES_AN_ENEMY`
are FA-80(c), **pre-row** (`grep -c "_hostile_first"` on `b4a27a15^` → 3), the
`recognized_marshal` block is byte-identical pre-row, so those offers already
executed before CX-2 existed. The record is guilty of a wrong **because**, not
of a wrong **claim** — and only for the addressed half, since the unaddressed
half really is CX-2's doing.

⚠ **This is the one axis on which the finding is UNDER-stated**: that
half-sentence is row CX's own, so the *documentation* defect **is** shipped by
this row even though the behaviour is not. That is the actionable residue.

### D. ⛔ "The one occasion where the player provably wanted the retreat verb is the one where it is withheld" — **inverted for all ten cases the finding reproduces.**

A player who types `Lannes, cut off the retreat` wants to **attack a retreating
enemy**. They did not want the retreat verb; offering it would be offering the
exact opposite of the intent, and `Lannes, attack Mack` is *nearer* the intent
than `Lannes, retreat` would be. The claim is true only for the **F3/F4**
regressed genuine orders — measured:

```
Lannes, carry out the retreat  [2] -> "Might you mean 'Lannes, scout' or 'Lannes, defend'?"
Lannes, keep retreating        [2] -> "Might you mean 'Lannes, scout' or 'Lannes, defend'?"
```

(and `Lannes, retreat` does work on that board: AP 4→4, he retreats to Lorraine).
But that is **F3/F4's defect**, not F5's — the wrong advice is downstream of the
wrong refusal. F5's own `reproduction` field describes the ten intended refusals,
where withholding `retreat` is correct.

---

## ⛔ THE SUGGESTED FIX SHIPS A REGRESSION AND REDS A PIN

I applied the filed fix verbatim — *"call `_counsel_lines` in the
`recognized_marshal` group too, drop the hardcoded Paris"* — to a private
`git archive` copy of HEAD. Measured output:

```
PATCHED, 'Lannes, cut off the retreat':
  Berthier adjusts his spectacles. "Sire, I understand this concerns Marshal
  LANNES, but I cannot determine the order. Perhaps: 'NEY, attack Mack' or
  'NEY, march to Lorraine'?"
```

**`what_can_i_do(world, nation, limit)` is NATION-scoped, not addressee-scoped** —
`military_counsel` iterates `get_player_marshals()` (boot order `Ney, Davout,
Soult, Lannes, …`) and takes the first that qualifies. The fix makes the shrug
name the marshal the player addressed in the prose and then offer orders for a
**different** marshal. That is the "advisory surface and executor are separate
implementations of one rule" shape row CX exists to close, re-created at the
surface the finding wanted to improve.

**Pin red, on the private copy:**

```
tests/test_fa_slice7_the_mock_speaks_plainly_2026_09_04.py::
    TestTheMockSpeaksPlainly::test_berthier_names_an_enemy_at_war
  AssertionError: lever off = the pre-slice enemies[0]
  assert 'Deroy' in 'Berthier adjusts his spectacles. "…Perhaps: \'Ney, attack
                     Mack\' or \'Ney, march to Lorraine\'?"'
-> 1 failed, 331 passed  (test_berthier_recovery + test_fa_slice7 + cx1 + cx2 + cx3)
```

That is **FA-80(c)'s own lever pin** — the guard the finding's own F5 body cites
approvingly. The sentence it breaks is the `BERTHIER_NAMES_AN_ENEMY = False` arm:
with the offer no longer built from `first_enemy`, the lever has nothing left to
be about.

**And the "drop the hardcoded Paris" half is measured unnecessary.** I staged the
only board on which a hardcoded capital could lie — `Paris.controller = "Austria"`
— and:

```
Paris controller: Austria
'Lannes, move to Paris'  success=True  AP 4->2  moved=['Lannes']
  "Lannes begins marching to Paris (distance: 4). Moved to Nivernais.
   Route: Nivernais -> Burgundy -> Limousin -> Paris."
```

The offer still executes. The hardcode is inelegant; it does not produce a lie.

---

## SEVERITY: **P3 → P4**

Display-only copy on a refusal path that costs **0 AP**, moves nothing, and
offers legal orders that execute. For the family it reproduces the withheld verb
would be the **wrong** advice; its only real bite belongs to F3/F4; and half the
family already gets the good copy. The one durable half — *the shrug never states
the rule* — is a genuine teachability gap and is worth a sentence, at P4.

## WHAT IS WORTH BUILDING FROM THIS ROW

1. **The finding's own third suggestion, and only that one** — carry the
   refusal's reason into the shrug: *"He cannot act on another army's retreat,
   Sire — `Lannes, attack Mack`, or `Lannes, retreat` if you mean his own."*
   It teaches the rule, keeps the **addressed** marshal (which the counsel road
   cannot), and needs no change to `_counsel_lines`, no pin flip.
2. **Correct the record in place**: strike *"Since CX-2"*, which is false for the
   addressed road. The rest of the sentence is measured true. (Shipped by row CX.)
3. **Do NOT** wire `_counsel_lines` into the `recognized_marshal` group as filed,
   and **do not** bother dropping the hardcoded Paris — measured harmless.
4. If the counsel source is ever wanted here, it needs an **addressee parameter**
   first (`military_counsel(world, nation, only_marshal=…)`), or the shrug will
   keep answering about a marshal nobody named.
