# VERDICT:CX5-L5-F2 — NARROWED (and PRE-EXISTING, confirmed)

**Row CX-5 · lens "retreat" F2 · tree `master 727cf88a`, clean · nothing under
the repo modified.**

Everything below was measured by my own probes
(`probes/refute_L5F2/{h,p1_repro,p2_conf,p3_lever,p4_fix,p5_client,p6_reach,
p7_harm,p8_corpus,p9_narrow}.py`), on the shipped 1805 board
(`parser_eval.build_world("1805")`) driven at `POST /command` through
`TestClient`, one fresh world per utterance, `LLM_MODE=mock`, key popped,
zero live calls. I did not reuse the lens's probes.

---

## THE ONE-LINE ANSWER

**The defect is real, reachable, and pre-existing — and the finding's own
prescribed fix ships fourteen regressions that nothing in this project can
see.** The substance survives; three of its claims are corrected; the
severity holds at P2 for the third-party half only.

---

## 1. DOES IT REPRODUCE? — YES at the parser, 11 of 12 at the board

All twelve parse as `retreat`, at exactly the confidences filed
(`p2_conf.py`, gate threshold read from
`llm_client.LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7`):

```
conf=0.95  act=retreat  escalates=False | Lannes, cut down Mack's retreat
conf=0.9   act=retreat  escalates=False | Lannes, cut off their line of retreat
conf=0.95  act=retreat  escalates=False | Lannes, cut off Mack's line of retreat
conf=0.9   act=retreat  escalates=False | Lannes, block that retreat
conf=0.9   act=retreat  escalates=False | Lannes, exploit this withdrawal
conf=0.9   act=retreat  escalates=False | Lannes, block your retreat
conf=0.9   act=retreat  escalates=False | Lannes, press the Austrians' retreat
conf=0.9   act=retreat  escalates=False | Lannes, exploit Austria's withdrawal
conf=0.9   act=retreat  escalates=False | Lannes, cut off Kutuzov's withdrawal
conf=0.9   act=retreat  escalates=False | Lannes, punish the disorderly Austrian retreat
conf=0.9   act=retreat  escalates=False | Lannes, cut off the Austrian army's retreat
conf=0.95  act=retreat  escalates=False | Lannes, take advantage of Mack's retreat
```

`escalates` is not asserted — it is **`_should_fallback_to_llm` itself**, asked
on a client whose `provider_name`/`api_key` are set as if a key were present,
so the "no key in any mode can correct them" claim is measured at the gate
rather than inferred from the number. It is **False on all twelve**. The
control is in the same table: the ten phrasings CX-5 *did* fix sit at `0.5 /
unknown / escalates=True`.

**⚠ CORRECTION 1 — "12 of 12 … still retreat" is 11 of 12 on the shipped
board.** Driven end to end (`p1_repro.py`), eleven produced *"Lannes bristles
at the retreat order but obeys. Lannes retreats from Franche-Comte to
Lorraine"*, AP 4→4. The twelfth, `Lannes, block your retreat`, hit the
marshal's objection instead: *"Lannes respectfully raises concerns: 'Retreat?
We can still fight!'"* — a blocking modal with the retreat order behind it and
a Proceed button. The sentence is still READ as a retreat; it is the board that
did not move.

Measured over **40 fresh boards** for one representative
(`Lannes, cut off their line of retreat`, `p7_harm.py`):

```
{'retreated': 34, 'objection': 6, 'other': 0}
```

So: read as a retreat on **40/40**, moves him with no confirmation on
**34/40**, and on 6/40 the game's own objection stands in the way. The honest
statement is *"read as a retreat on every board, executed silently on ~85% of
them"* — not *"12 of 12"*.

The two non-sequitur messages reproduce verbatim:

```
Lannes, cut off Mack's line of retreat
 -> "Lannes bristles at the retreat order but obeys. Lannes retreats from
     Franche-Comte to Lorraine. Mack cannot be reached, Sire — no such
     province is known to the staff; Lannes falls back to Lorraine instead."
```

---

## 2. IS THE SEVERITY RIGHT? — P2 HELD, for the third-party half only

The harm, measured (`p7_harm.py`):

```
Lannes before : ('Franche-Comte', 18000, None, None)
Lannes after  : ('Lorraine',      18000, None, None)
AP 4 (unchanged)
"Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns."
```

and the recovery question, which the finding did not ask:

```
'Lannes, move to Franche-Comte' -> AP=3, loc=Franche-Comte      (he can walk back)
'Lannes, attack Mack'           -> "Lannes is recovering from retreat and
                                    cannot attack. Recovery: 3 turn(s) remaining."
```

**The displacement is undoable for 1 AP; being unable to attack for three
turns is not.** A sentence whose whole purpose is to destroy the enemy's
retreat takes your own corps out of the fight for three turns, free, silently,
and with no road to an LLM correction. That is the same harm CX-5 was built to
close, on the same board, so P2 is consistent with the row's own framing.

Against the severity: it is **pre-existing** (§4), the objection intercepts
~15% of the time, and **the game never prints any of these phrasings**, so
CX-3's census rule is not breached — a census over `backend/` and the client
finds zero occurrences of `line of retreat`, and the only third-party retreat
prose the game emits is `"<name>'s rearguard screens the retreat"` and
`"runs down the retreating enemy"` (`combat.py:926,931`), **both of which
CX-5 already covers**. The player composes these sentences; the game does not
teach them.

Not over-stated. Not raised either.

---

## 3. PLAYER-REACHABLE? — YES, 12 of 12

`p5_client.py` ports `main.gd::_redirect_diplomatic_command` **reading every
keyword list out of `main.gd` at run time** (`family=115 war_room=2
no_home=18 anywhere=13 exempt=20`) rather than re-typing them, so the port
cannot drift from the shipped lists. It carries a self-test of four sentences
the client is documented to claim and four it is documented to pass:

```
port self-test: 8/8 agree with documented client behaviour
```

Result: **12 of 12 reach `POST /command` unredirected.** None carries a
`DIPLO_FAMILY_KEYWORDS` entry, none is diplomat-addressed, and the
nation-bearing ones (`Austria's withdrawal`, `the Austrians' retreat`, `the
Austrian army's retreat`) clear the gate because `DIPLO_NATION_ANYWHERE_KEYWORDS`
is the D5 instrument set (`guarantee|sponsor|subsidize|…`) and contains no
retreat vocabulary. The lens's reachability claim holds, and now by
construction rather than by inspection.

---

## 4. DID ROW CX SHIP IT? — NO. PRE-EXISTING, by two independent measurements

**(a) The lever** (`p3_lever.py`). With `A_RETREAT_CAN_BE_A_NOUN = False`, all
twelve retreat, `moved=['Lannes']`, objection False — and so do the two
controls CX-5 fixed.

**(b) The pre-row file.** I took `git show b4a27a15^:backend/ai/llm_client.py`,
loaded it as a module under `backend.ai` so its relative imports resolve, and
drove its own `_parse_with_mock` on the same board:

```
prerow act=retreat conf=0.95 | Lannes, cut down Mack's retreat
prerow act=retreat conf=0.9  | Lannes, cut off their line of retreat
…
=== of the finding's 12, 12 already retreated BEFORE row CX ===
```

Identical actions, identical confidences. **`shipped_by_this_row: false` is
correct.** Row CX narrowed this defect (it removed `the|our|his|her|their|its|
a|an|enemy|enemy's` from its reach and moved those cases into the escalation
band, `0.9 → 0.5`); it did not close it.

⚠ One fair criticism of the row survives: `COMMAND_EXPERIENCE_SPEC.md` §3.4
states the rule as *"'retreat' after a determiner is a NOUN"* while the code
implements *"after one of six determiners"*. The row does **not** list any of
these twelve as fixed, so it did not over-claim its cases — it over-stated its
**rule**. That is worth a sentence in the record, not a defect row.

---

## 5. IS THE REACH RIGHT? — reproduces, but 22% of it is not a defect

My own sweep (`p6_reach.py`, act-verb × determiner × noun, plus `line of`)
gives **312/632** against the finding's 308/628 — the same measurement, four
extra rows because I added a `your` arm to the `line of` family. Every bucket
matches:

```
that 32/32 · this 32/32 · these 32/32 · those 32/32
Mack's 32/32 · Austria's 32/32 · the Austrians' 32/32
your 32/32 · my 32/32 · line-of 24/24
the|our|his|her|their|its|a|an|enemy|the enemy's : 0/32 each   (CX-5's work)
```

**⚠ CORRECTION 2 — `your` and `my` are not third-party possessives.** Addressed
to Lannes, *"your retreat"* is **Lannes's own**, and *"my retreat"* is the
Emperor's own army. Counting them as "somebody else's retreat" is a category
error, and the shipped code already agrees with me: `_mentions_screening_idiom`'s
own determiner set is `the|our|his|their|her` — **`your` is deliberately absent**,
which is exactly why `Lannes, cover your retreat` retreats today and should.

So the finding's nine determiner buckets are really **seven**:

```
ALL BUCKETS TOGETHER (the finding's count) : 312/632
THIRD-PARTY ONLY  (the real defect)        : 244/564
your/my rows counted as defects            :  68  (22% of the claimed reach)
```

244 is still a large number and the finding's substance is untouched. But the
headline reach is inflated by a fifth, and the inflation is in the one place
that matters for the fix.

---

## 6. WOULD THE SUGGESTED FIX SHIP A REGRESSION? — **YES. FOURTEEN.**

The finding prescribes: *"Match the shape instead — a possessive/`'s` token or
a determiner-class word before a retreat noun, and allow the noun to be reached
through `line of`, `route of`, `path of`, or 1–3 intervening words"*, having
named `your` and `my` in the omission list.

I built exactly that and ran it (`p4_fix.py`, `p9_narrow.py`):

```
FILED FIX : closes 12/12, regressions 14
```

The fourteen, each measured `retreat` at HEAD and `unknown` under the fix —
every one an ordinary order to fall back:

```
Lannes, begin your retreat          Lannes, call your retreat
Lannes, sound your retreat          Lannes, execute your withdrawal
Lannes, start your withdrawal       Lannes, make your retreat
Lannes, begin your withdrawal       Lannes, continue your retreat
Lannes, order your retreat          Lannes, resume your retreat
Lannes, signal your retreat         Lannes, cover your retreat
Lannes, commence your withdrawal    Lannes, cover your withdrawal
```

**The pin it reds: none. The corpus row it moves: none.**

```
corpus, HEAD             : 688/688
corpus, FILED FIX        : 688/688     rows newly failing: 0
corpus, FIX + carry-out  : 688/688
CX pins under FILED FIX  : 201 passed
```

The golden corpus has 449 entries, 19 of which mention retreat/withdraw, and
**not one uses a possessive retreat noun** — so it is structurally blind to
both the defect and to this regression. That is the important sentence in this
verdict: *nothing in the project distinguishes the right fix from the one that
breaks fourteen ordinary orders.*

F3's symmetric widening of `_ORDER_THE_RETREAT_RE` rescues twelve of the
fourteen but not `cover your retreat` / `cover your withdrawal`, because
`cover` is not a carry-out verb — so widening the carry-out set is a patch on
the symptom, not the rule.

### The correction, measured

Keep the demonstratives and the proper possessives; **leave the second and
first person alone**; reach the noun through `line|route|path|road of`:

```python
_RETREAT_NOUN_RE = re.compile(
    r"\b(?:the|our|his|her|their|its|an?|that|this|these|those"
    r"|enemy|\w+['’]s|\w+s['’])\s+"
    r"(?:\w+\s+|(?:line|route|path|road)\s+of\s+){0,3}"
    r"(?:retreat|retreats|withdrawal|withdrawals)\b"
    r"|\bretreating\b", re.IGNORECASE)
```

```
NARROW : closes 11/12, regressions 0
         corpus 688/688 · CX pins 201 passed
```

The one it leaves open is `Lannes, block your retreat` — which is not a
third-party defect at all, and is the very utterance that behaved differently
in §1.

⛔ **A trap I fell into and am recording, because the next builder will hit
it.** My first narrow arm dropped the leading `\b` from the determiner group,
and `our` then matched **inside `your`** — which silently made the
"third-party only" arm behave exactly like the filed one and produced a clean,
wrong table of 14 regressions for it. Production has the `\b`, and that `\b`
is the only reason `your retreat` reaches the retreat branch at HEAD. Any
patch here must be probed on `your`/`my` specifically, with the boundary in.

---

## 7. FOUND WHILE MEASURING — the row's own lever pin is flaky at HEAD

Not part of F2, and not something the lens filed (its F6 names a *different*
pin, `test_he_does_not_march_away`). `TestTheRetreatIsSometimesANoun::
test_the_lever` asserts `"retreats from" in message` after flipping the lever
off — and the objection RNG intercepts. Run standalone at HEAD, six times, no
plugin, no source change:

```
1 failed · 1 failed · 1 failed · 1 passed · 1 passed · 1 passed
```

It passes when the whole class runs (different RNG state) and fails 3 of 6
times alone. Same hazard the lens describes — a retreat pin whose only
discriminator is defeated by an objection — sitting on the row's **attribution**
pin. Worth folding into whatever fixes F6.

---

## WHAT I CHECKED AND COULD NOT KILL

* the twelve confidences — exact, to the digit, including the 0.95/0.90 split
  (0.95 where a marshal name raises it)
* `escalates=False` — asked of the real gate, not inferred
* client reachability — 12/12, on a port self-tested against eight documented
  client behaviours
* pre-existence — proven twice, once by lever and once by executing the
  pre-row file
* the reach — reproduced to within four rows, with the same bucket structure

## WHAT I CORRECTED

1. **"12 of 12 still retreat"** → 12/12 are *read* as a retreat; 11/12 moved
   the marshal on the shipped board, and over 40 boards a representative case
   splits 34 silent retreats / 6 objection modals.
2. **"308 … in nine determiner buckets"** → reproduces (my 312/632), but
   `your` and `my` are the addressee's and the speaker's own retreat, not a
   third party's; 68 rows, 22% of the claimed reach, are not defects. True
   third-party reach **244/564**.
3. **The prescribed fix** → closes all twelve and **breaks fourteen ordinary
   second-person retreat orders**, with the golden corpus and all 201 CX pins
   green in both arms. The measured correction (third person only) closes
   eleven with zero regressions.

**Recommendation to the owner: build it, at P2, on the NARROW shape in §6 —
not on the shape as filed — and add `Lannes, sound your retreat` and
`Lannes, cover your retreat` to the corpus in the same commit, because today
nothing would have caught their loss.**
