# VERDICT — CX5-L5-F3 — **NARROWED**

> "The 13-verb carry-out allowlist refuses 15 natural retreat orders that
> worked before CX-5" — filed P3, `shipped_by_this_row: true`,
> `player_reachable: true`.

**Verdict: NARROWED.** The mechanism reproduces exactly as filed, on my own
probes, end to end, and the attribution to CX-5 is sound — I confirmed it
against the *actual* pre-row tree and not only against the lever. But three
things the row filed do not survive measurement:

1. the **severity is over-stated** — this is P4, not P3;
2. the **reach figure is not a reach figure** — "worked before CX-5" is
   satisfied by *any* string containing the substring, and I measured six
   sentences that are plainly not orders satisfying it;
3. **the prescribed fix ships a regression of CX-5's own defect**, driven end
   to end — and it names no pin, because there is none to name: the whole CX
   test file passes **134/134** and the golden corpus **688/688** with the
   filed fix installed.

Everything below is mine, measured on the shipped 1805 board at the actual
working HEAD, **`f52df77f`** — a docs-only commit sitting on top of the
`727cf88a` the task names, so no production code differs; the tree was clean
before and after. Nothing under `backend/`, `tests/`, `docs/`, `tools/` or
`godot-client/` was modified; the "with the fix" arms are runtime monkeypatches
and a pytest plugin living in the scratchpad. `LLM_MODE=mock` throughout, zero
live calls.

Probes: `probes/p1_parse_lever.py`, `p2_prerow_vs_head.py`, `p3_drive.py`,
`p4_fix_regression.py`, `p5_escalation_and_baseline.py`,
`p6_drive_the_fix_regression.py`, `p7_how_wide_is_the_hole.py`,
`p8_prerow_holes.py`, `patch_filed_fix.py`. Pre-row tree extracted read-only
with `git archive b4a27a15^ | tar -x` (= `f7008582`).

---

## 1. IT REPRODUCES — and the attribution is stronger than filed

The filed report attributed by flipping `A_RETREAT_CAN_BE_A_NOUN`. I did that
too, and then did the thing the task asks for: I ran the same utterances
against a **real checkout of the pre-row tree**.

`git show b4a27a15^:backend/ai/llm_client.py` line 1897 is HEAD's branch minus
exactly the two `_retreat_is_a_noun(...)` conjuncts, so the lever is a faithful
byte-for-byte restoration — but I did not rely on that:

```
                                        PRE-ROW f7008582         HEAD 727cf88a
Lannes, carry out the retreat           retreat/0.9        ->    unknown/0.5  FAIL
Lannes, proceed with the retreat        retreat/0.9        ->    unknown/0.5  FAIL
Lannes, complete the withdrawal         retreat/0.9        ->    unknown/0.5  FAIL
Lannes, finish the withdrawal           retreat/0.9        ->    unknown/0.5  FAIL
Lannes, authorise the retreat           retreat/0.9        ->    unknown/0.5  FAIL
Lannes, authorize the retreat           retreat/0.9        ->    unknown/0.5  FAIL
Lannes, permit the retreat              retreat/0.9        ->    unknown/0.5  FAIL
Lannes, sanction the withdrawal         retreat/0.9        ->    unknown/0.5  FAIL
Lannes, sanction a general retreat      retreat/0.9        ->    unknown/0.5  FAIL
Lannes, approve the withdrawal          retreat/0.9        ->    unknown/0.5  FAIL
Lannes, direct the retreat              retreat/0.9        ->    unknown/0.5  FAIL
Lannes, instruct the retreat            retreat/0.9        ->    unknown/0.5  FAIL
Lannes, effect the withdrawal           retreat/0.9        ->    unknown/0.5  FAIL
Lannes, press on with the retreat       retreat/0.9        ->    unknown/0.5  FAIL
Lannes, get on with the retreat         retreat/0.9        ->    unknown/0.5  FAIL
Lannes, sound his retreat               retreat/0.9        ->    unknown/0.5  FAIL
Lannes, order their retreat             retreat/0.9        ->    unknown/0.5  FAIL
Lannes, begin his withdrawal            retreat/0.9        ->    unknown/0.5  FAIL
Lannes, continue his retreat            retreat/0.9        ->    unknown/0.5  FAIL
--- controls, unchanged both trees ---
Lannes, retreat / sound the retreat / order the retreat / continue the retreat
                                        retreat/0.9        ->    retreat/0.9
```

Driven at `POST /command`, one fresh 1805 board each (`p3_drive.py`):

```
'Lannes, carry out the retreat'
   success=False  AP 4->4  admin 2->2  gold 800->800  turn 1->1  battle=False
   moved: NOTHING
   Berthier adjusts his spectacles. "Sire, I understand this concerns Marshal
   Lannes, but I cannot determine the order. Perhaps: 'Lannes, attack Mack' or
   'Lannes, move to Paris'?"

'Lannes, permit the retreat'      -> "Valid orders include: attack, move, scout,
                                      defend, fortify, recruit."
'Lannes, proceed with the retreat'-> "Might you mean 'Lannes, scout' or
                                      'Lannes, defend'?"
```

**Player-reachable: yes, confirmed at the client.** None of the 15 carries a
`DIPLO_*` keyword (`sanction`, `permit`, `direct`, `effect`, `approve` appear in
none of the six keyword lists); `retreat` sits in `DIPLO_ADDRESS_EXEMPT_WORDS`
(`main.gd:1963`); and `withdraw` does not appear in `main.gd` at all. Nothing is
redirected.

**The escalation qualifier is correct, and I verified it rather than took it**
(`p5`, calling `_should_fallback_to_llm` directly; no live call):

```
LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7
Lannes, carry out the retreat   unknown/conf=0.5/refusal=False   escalates with a key = True
Shipped keyless/mock default (provider_name == 'mock')            escalates = False
```

---

## 2. NARROWING 1 — the severity is P4, not P3

Everything the regression costs is a keystroke.

* **Nothing is spent and nothing is lost.** AP 4→4, admin 2→2, gold 800→800,
  turn 1→1, no marshal moves, no battle, on every one of the 19. And the
  retreat verb is itself **free** — `Lannes, retreat` also measures AP 4→4 —
  so there is not even an AP asymmetry to recover from.
* **The road the game teaches works, and is shorter.** The CX-3 predictor's
  `_MARSHAL_VERBS` table ships `["retreat", "", "retreat"]`, i.e.
  `<Marshal>, retreat`, and that row is pinned from Python to resolve through
  the real parser. Nothing in `backend/` or the client teaches any of the 15.
  **The IQ10-6 census this row generalised is not violated**: the game never
  offers a sentence it cannot read.
* **24 of 49** curated retreat phrasings still parse at HEAD (`p7`), including
  every plain form (`retreat`, `fall back`, `pull back`, `retire`, `withdraw`,
  and all the `to <region>` variants) and the entire shipped carry-out
  allowlist (`sound|order|begin|start|commence|call|signal|blow|announce|make|
  continue|resume|execute`).
* **The hole class is not new.** `break off`, `disengage`, `back off`,
  `give ground`, `yield the ground`, `get out of there` all shrugged on the
  **pre-row tree** as well (`p8`) — they never contained the substring, so the
  old branch never claimed them either. CX-5 widened an existing hole; it did
  not open one.
* With an API key the escalation gate fires, as measured above.

That is a recoverable, zero-cost, one-retype shrug, on a family whose taught
and shortest form is unaffected. P4.

⚠ One aggravating factor, recorded and *not* used to hold the severity up
because it belongs to a different row: the shrug never names `retreat` among
its offers (`attack / move / scout / defend / fortify / recruit`), so the rule
is unlearnable from the message. That is lens 5's own **F5**, it is
pre-existing, and fixing it would make this row unambiguously cosmetic.

---

## 3. NARROWING 2 — the magnitude does not survive

### "worked before CX-5" is not a quality criterion

The pre-row branch fired on the **bare substring**, so *every* sentence
containing `retreat`/`withdraw` was `retreat/0.9`. Measured on the real pre-row
tree (`p5 baseline`):

```
Lannes, the retreat was a disgrace          retreat/0.9
Lannes, prevent the retreat                 retreat/0.9
Lannes, stop the enemy retreat              retreat/0.9
Lannes, their retreat is our opportunity    retreat/0.9
Lannes, report on the Austrian retreat      retreat/0.9
Lannes, deny them the retreat               retreat/0.9
```

Each of those "worked before CX-5" by the finding's own criterion, and each
must not retreat. So the **736 of 1,584** combinatorial figure measures the old
branch's promiscuity, not the number of orders a player would type, and it is
not a reach figure for this defect. The lens states this circularity about the
*record's* claim #2 — *"the pre-fix board contains no evidence whatever about
which four are the whole set"* — and then builds its own number on the same
criterion.

### "15 natural retreat orders" is 13 verbs, of which ~6 are unambiguous

* `authorise` / `authorize` is one verb in two spellings; `sanction` is counted
  twice with two objects. 15 utterances → **13 distinct verbs**.
* **Four are permission verbs with a genuinely ambiguous object.**
  `Lannes, permit the retreat` reads at least as readily as *let them go* as it
  does *you may retreat* — which is CX-5's own class, not its complement. Same
  for `sanction`, `approve`, `authorise`. Treating them as carry-out verbs is a
  design ruling, not a bug fix (and §4 shows what it costs).
* `instruct the retreat` is not English — one instructs a *person*. Its natural
  form, `instruct Lannes to retreat`, parses correctly at HEAD.
* The unambiguous core is six: `carry out`, `proceed with`, `complete`,
  `finish`, `press on with`, `get on with`.

---

## 4. THE DECISIVE ATTACK — the filed fix ships a regression, green

The filed fix: *"F3 wants the possessive determiners in
`_ORDER_THE_RETREAT_RE` and either a much longer verb list or — better —
inverting again."* I built both halves and measured them (`p4`, `p6`).

### (a) The determiner half alone re-opens CX-5, because `make` is already in the shipped list

Driven end to end at `POST /command`, determiner half installed:

```
======== SHIPPED (HEAD) ========
'Lannes, make their retreat impossible'  AP 4->4  moved: NOTHING   (correct shrug)
'Lannes, make their withdrawal costly'   AP 4->4  moved: NOTHING   (correct shrug)
'Lannes, make his retreat impossible'    AP 4->4  moved: NOTHING   (correct shrug)

======== WITH the filed fix's determiner half ========
'Lannes, make their retreat impossible'
   AP 4->4  moved: {'Lannes': (('Franche-Comte',18000), ('Lorraine',18000))}
   "Lannes bristles at the retreat order but obeys. Lannes retreats from
    Franche-Comte to Lorraine. Army begins recovery (currently at -45%
    effectiveness). Will recover over 3 turns."
'Lannes, make their withdrawal costly'   -> same retreat
'Lannes, make his retreat impossible'    -> same retreat
```

`signal`, `call`, `order`, `continue`, `start` ride the same hole
(`signal their retreat`, `order their retreat`, `continue his retreat` …).

### (b) The verb half alone re-opens it on the permission verbs

```
Lannes, permit the enemy retreat        HEAD: refused  ->  with fix: *** ORDER ***
Lannes, sanction the enemy withdrawal   HEAD: refused  ->  with fix: *** ORDER ***
```

### (c) Both halves together add the third-party objects

```
Lannes, permit their retreat       refused -> ORDER
Lannes, sanction their withdrawal  refused -> ORDER
Lannes, approve their withdrawal   refused -> ORDER
Lannes, direct their retreat       refused -> ORDER
```

Every one of these lands at **confidence 0.9**, which is above the 0.7 gate —
so the fix trades a recoverable shrug for the exact **unrecoverable** class
CX-5 exists to kill. That is a strictly worse trade than the defect.

### (d) And nothing goes red

```
tests/test_cx1_a_question_never_orders.py, filed fix (verbs + determiners) installed
   134 passed
   (incl. all ten SOMEBODY_ELSES, test_the_noun_rule_and_the_carry_out_set,
    test_the_lever, test_the_pursuit_of_a_retreating_enemy_is_untouched)

golden corpus, filed fix installed      688/688 passed  (HEAD: 688/688)
```

So the answer to *"name the pin it would red"* is: **none, and that is the
finding.** The row's own pins are all about the *verb* side of the rule; not
one of them holds a possessive object, so the whole regression is invisible to
them and to the corpus. This is exactly the shape the row's own §50.10 warns
about, one layer out.

One worry I checked and can rule out: adding `press on with` does **not** red
`test_he_does_not_march_away[Lannes, press the retreat]` — the alternation has
no bare `press`, and I measured `press the retreat` staying refused under all
four variants. The hazard is the **object**, not the verb.

---

## 5. WHAT THE OWNER SHOULD DO

Keyed on the object, not on a longer verb list:

* Extend the carry-out set only where the object is **first-person or
  articled** — `the | our | a | an` — which is what ships today, and add the
  six unambiguous verbs (`carry out`, `proceed with`, `complete`, `finish`,
  `press on with`, `get on with`) as multiword alternatives.
* **Do not add the possessive determiners to `_ORDER_THE_RETREAT_RE`.** A
  possessive object is the third-party reading by construction, and `make` /
  `signal` / `order` / `continue` are already in the set.
* Leave `permit` / `sanction` / `approve` / `authorise` out, or take them as a
  recorded design ruling with the ambiguity stated — they are not obviously on
  the carry-out side of the line.
* If any of this is built, the new pin must include **`Lannes, make their
  retreat impossible`** asserting a shrug. That is the sentence the current
  ten cannot see.
* `Lannes, sound his retreat` / `order their retreat` are best left refused:
  they are the ambiguous overlap, and the player has `Lannes, retreat` and
  eleven working carry-out phrasings.

---

## 6. MEASURED FALSE CLAIMS

1. **`COMMAND_EXPERIENCE_SPEC.md` §3.4 / the CX-5 commit message / the code
   comment: "`sound`, `order`, `begin` and `call` … are the whole set a player
   reaches for."** Measured false — six unambiguous natural carry-out verbs
   shrug at HEAD (`carry out`, `proceed with`, `complete`, `finish`,
   `press on with`, `get on with`). (This half of lens 5's claim #2 stands; its
   "15 natural" half does not — see §3.) The shipped regex also names **13**
   verbs, not 4, so the record's own arithmetic is off.
2. **CX5-L5-F3's "15 natural retreat orders"** — 13 distinct verbs, four of
   them ambiguous permission verbs and one ungrammatical.
3. **CX5-L5-F3's "736 of 1,584 worked before CX-5 and are refused now"** —
   true as arithmetic over the old bare-substring branch, false as a measure of
   this regression's reach; six plainly-not-an-order sentences satisfy the same
   criterion on the same tree.
