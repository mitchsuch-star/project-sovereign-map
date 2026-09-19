# VERDICT — L2-4 (lens "addressee")

**Tree:** `master 727cf88a` … `f52df77f` (docs-only on top), clean, read-only.
**Board:** the shipped 1805 scenario, **a fresh world per utterance**, driven at
`POST /command` through `backend.main`'s TestClient with the
world / game_state / parser triple swapped.
**My probes** (written from scratch, not the lens's):
`.../cx_review/probes/refute_L24/{_h,r1_repro,r2_mechanism,r3_ordinary,
r4_fix_sim,r5_fix_full,r6_patched_drive,r7_reach,r8_prerow,r9_retreat,
patchplugin}.py`. Nothing under `backend/`, `tests/`, `docs/`, `tools/` or
`godot-client/` was touched; the simulated fix lives on the class object inside
my own process.

---

## THE VERDICT IN ONE LINE

> **PRE-EXISTING.** The defect reproduces **exactly** as filed — and is
> **wider and worse** than filed (59 of 66 filler words, not 8; and the
> `retreat` arm marches eight corps at **zero AP**). But **row CX did not ship
> it**: across all 66 filler words the outcome class is **identical at both
> positions of the row's own lever, 0 differences**, while the control the row
> *did* close flips. The filed severity **P2 is under-stated — it is P1**, on the
> row's own scale (its sibling L2-1, same harm, is P1). The prescribed fix does
> **not** red a pin (full suite **23,656 passed / 4 skipped** with it installed),
> but the finding's claim that it also closes L2-5 is **FALSE**, measured.

---

## 1. DOES IT REPRODUCE, EXACTLY AS STATED?  **YES — all eight.**

`probes/refute_L24/r1_repro.py`, fresh 1805 board per line:

```
inert    | Zorglub attack Mack          ap [4,4] gold [800,800]  "There is no 'Zorglub' in the order of battle, Sire."
BATTLE   | Zorglub just attack Mack     ap [4,3] gold [800,524]  moved Davout,Lannes,Murat,Napoleon,Soult
BATTLE   | Zorglub now attack Mack      ap [4,3] gold [800,531]
BATTLE   | Zorglub then attack Mack     ap [4,3] gold [800,539]
BATTLE   | Zorglub first attack Mack    ap [4,3] gold [800,548]
BATTLE   | Zorglub still attack Mack    ap [4,3] gold [800,512]
BATTLE   | Zorglub you attack Mack      ap [4,3] gold [800,503]
BATTLE   | Zorglub please attack Mack   ap [4,3] gold [800,493]
BATTLE   | Zorglub's corps attack Mack  ap [4,3] gold [800,503]
```

Every one carries a real `battle_report`, "MUSTER — Soult … vs Mack at Swabia",
and the control is refused free. The filed reproduction is accurate to the
digit class.

**The mechanism is the one filed**, and I pinned it with a negative control
(`r2_mechanism.py`). A filler **not** in `_NOT_AN_ADDRESS_RE` is refused:

```
inert  | Zorglub quickly attack Mack      "There is no 'Zorglub quickly' in the order of battle"
inert  | Zorglub immediately attack Mack  "There is no 'Zorglub immediately' …"
inert  | Zorglub of Paris attack Mack     "There is no 'Zorglub of Paris' …"
```

and **"anywhere" is literal** — the filler need not be adjacent to the verb:

```
BATTLE | Zorglub the elder attack Mack
BATTLE | Zorglub of the north attack Mack
```

One narrowing the finding does not state: the **honorific** form is protected by
a different path, so the hole is bare-name only —
`Field Marshal Zorglub please attack Mack` and `Commander Zorglub still attack
Mack` are both refused ("There is no Marshal 'Zorglub'").

---

## 2. IS THE SEVERITY RIGHT?  **NO — it is UNDER-stated. P1, not P2.**

Two measurements the lens did not take.

### (a) The reach is 59 of 66, with a name the GAME ITSELF prints

`r7_reach.py` drives `Grouchy <word> attack Mack` for each of the 66
alternation members of `_NOT_AN_ADDRESS_RE`, fresh board each. `Grouchy` is
**row CX's own pin case** ("a commission candidate on the bench") and is refused
free when typed alone.

```
control  inert   | Grouchy attack Mack   "There is no 'Grouchy' in the order of battle"
TALLY over 66 filler words: {'BATTLE': 59, 'inert': 7}
EXECUTED: 59 of 66
```

The seven that stand down do so through *other* guards (`does`/`must`/`should`/
`next` → CX-1 arm (c); `if`/`when` → the condition guard; `while` → a shrug).
The same holds for the other names in the row's own pin table — measured
(`r3_ordinary.py`): `Grouchy now`, `Grouchy's corps`, `Berthier now`,
`Berthier's corps`, `Wellington now` **all send SOULT into a real battle**,
while the bare form of each is refused free.

⚠ **A hazard I checked and it is CLEAN:** a *bound* name survives the stand-down,
because the roster arm still runs. `Ney's corps attack Mack`, `Ney now attack
Mack` and `Ney and Davout attack Mack` all muster **NEY**, not Soult. The
misdirection is confined to names the roster cannot bind.

### (b) The `retreat` arm is the spec's own worst case, alive, at ZERO AP

`r9_retreat.py`. `COMMAND_EXPERIENCE_SPEC.md` §3.1 closes on the sentence
**"`Wellington retreat` marched the entire army back."** That is now refused.
One filler word over, it is not:

```
inert       | Wellington retreat        ap [4,4]  moved=0   "There is no 'Wellington' …"
MOVED-BOARD | Wellington now retreat    ap [4,4]  moved=8   "General retreat ordered! Ney falling back! …"
MOVED-BOARD | Grouchy now retreat       ap [4,4]  moved=8
MOVED-BOARD | Berthier just retreat     ap [4,4]  moved=8
MOVED-BOARD | Grouchy's corps retreat   ap [4,4]  moved=8
MOVED-BOARD | Wellington you retreat    ap [4,4]  moved=8
```

**Eight corps relocated, 0 AP, no confirm, with movement attrition.** The
executor's own FA-22 comment calls exactly this shape out ("`Berthier, retreat`
ran a WHOLE-ARMY retreat — eight marshals, 2,270 men, ZERO AP, no confirm").
The scout arm spends 1 AP the same way (`Wellington now scout Swabia`,
`Grouchy's corps scout Swabia` → Soult scouts).

On the review's own scale this is L2-1's harm by a different axis, and L2-1 is
filed P1. **P2 is not defensible beside it.**

---

## 3. PLAYER-REACHABLE?  **YES — confirmed at the client, not assumed.**

`main.gd::_execute_command` (line 1613) runs exactly three gates before
`api_client.send_command`: the underscore redemption tokens, `_is_end_turn_phrasing`,
and `_redirect_diplomatic_command`. For `Grouchy now attack Mack`:

* not a bare underscore token;
* not end-turn phrasing;
* `_is_advisory_question` → false (no trailing `?`; first word `grouchy` is not
  in `DIPLO_ADVISORY_STARTS = [what, how, where, who, whom, why, which]`);
* `DIPLO_NO_HOME_KEYWORDS` / `DIPLO_WAR_ROOM_KEYWORDS` / `DIPLO_FAMILY_KEYWORDS`
  → no member is a substring; no nation is named (`Mack` is a marshal), so
  `_mentions_a_nation` and the nation-gated prefixes cannot fire.

Fail-open: the line goes to the backend verbatim. **The 114 diplomatic redirect
forms do not touch it.**

The one mitigation, and it holds: **the game never teaches this shape.** The
CX-3 completer composes `marshal + ", " + verb` from `_own_marshal_names()`
(`main.gd:7048`), so every offered line carries the comma and a bindable name.
The defect is reachable only by the player typing it himself — which is the
same standing as the row's own headline case.

---

## 4. DID ROW CX SHIP IT?  **NO. The filed `shipped_by_this_row: true` is FALSE.**

Two independent measurements.

**(a) Source.** `git show b4a27a15^:backend/commands/executor.py` →
`_unbound_addressee` opened with `head, sep, _tail = raw.partition(","); if not
sep: return None`. Every comma-less sentence stood down — the eight filler
forms *and* the control alike. The shipped comment's claim that the lever
restores the pre-row rule byte-for-byte checks out against that text.

**(b) Behaviour.** `r8_prerow.py` runs the whole 66-word sweep at **both**
positions of `AN_ADDRESS_NEEDS_NO_COMMA`:

```
lever ON  executed: 59 of 66
lever OFF executed: 59 of 66
words whose OUTCOME CLASS differs between the arms: 0  []
control 'Grouchy attack Mack'  lever=True  -> inert (refused)
control 'Grouchy attack Mack'  lever=False -> BATTLE
```

**Zero of 66.** The row moved the control and moved nothing else. L2-4 is
FA-22's residue, not CX-1's regression.

⚠ **But the RECORD over-claims, and that part of the lens's complaint is
justified one row over.** `COMMAND_EXPERIENCE_SPEC.md` §3.1 lists
`Grouchy attack Mack`, `Berthier attack Mack`, `Wellington attack Mack`,
`Blucher attack Mack`, `Zorglub attack Mack` and `Wellington retreat` as closed,
without qualification — and **all six are still open one filler word over**
(measured above). The spec states the rule ("The run must contain no function
word and no collective") but never states its cost. That is the fix this row
owes even if the behaviour predates it.

---

## 5. WOULD THE PRESCRIBED FIX SHIP A REGRESSION?  **No pin reds — but its own claimed scope is wrong.**

I implemented the finding's prescription verbatim ("strip a leading article; the
run is not a name if its **first token** is a function word or a collective")
and measured it three ways.

**(a) Full suite, fix installed** (`patchplugin.py`, `pytest tests/ -q`):
**23,656 passed, 4 skipped** — *it reds nothing*. The three files that own the
seam (`test_cx1…`, `test_fa_slice1…`, `test_cx3_the_predictor.py`) are
**306 passed** on their own.

**(b) End to end, shipped vs prescribed** (`r6_patched_drive.py`). It does what
it says:

```
                                          SHIPPED            PRESCRIBED
Zorglub just attack Mack                  BATTLE       ->    refused "There is no 'Zorglub just'"
Grouchy now attack Mack                   BATTLE       ->    refused "There is no 'Grouchy now'"
the Iron Marshal attack Mack  (= L2-3)    BATTLE       ->    refused "There is no 'Iron Marshal'"
all marshals attack / the army attack     "Which marshal…"  unchanged
every corps retreat / retreat / attack    unchanged
can you attack Mack / do attack Mack      BATTLE (order)    unchanged
Ney attack Mack / Davoust attack Mack     unchanged
```

**(c) The regression surface, over 1,692 recorded utterances** — the whole
golden corpus plus every string in `tools/playtest_scripts/*.json`
(`r5_fix_full.py`, full predicate incl. the comma path and the roster arm):
**10 flagged, 0 reachable.** Every one of the ten is stopped by the *type* gate
or by CX-1's question guard before `_unbound_addressee` runs — I drove the
dangerous-looking ones to be sure, and `order the entire army to fall back to
Paris and dig in` is a `move`, not a `general_retreat`, so it is untouched
either way.

**Three corrections to the fix shape, all measured:**

1. ⛔ **"The head-token fix in L2-4 closes [L2-5] in the same edit" is FALSE.**
   All twelve L2-5 shapes are unchanged by it — `quickly attack Mack`,
   `cavalry attack Mack`, `ok attack Mack`, `Marshal attack Mack`, `okay
   retreat`… are refused before and after, because their head token is not in
   the set either. Measured in `r4_fix_sim.py` and again end to end.
2. It **enlarges** L2-5 rather than closing it: two natural sentences flip from
   executing to refused — `right now attack Mack` → *"There is no 'right now'"*
   and `the cavalry attack Mack` → *"There is no 'cavalry'"*. Both invisible to
   23,656 tests.
3. ⚠ **L2-3's companion prescription is wrong on a fact.** It says to drop `the`
   from the set because *"the collective words already cover `the army` /
   `the cavalry` on their own"*. They do not: the alternation is
   `all|every|everyone|everybody|each|both|any|army|armies|corps|marshals|
   generals|commanders|men|troops|soldiers|forces|everything|the|…` — **there is
   no `cavalry`**, and no `infantry`, `artillery`, `guard` or `guards` either
   (L2-5's own list proves it, by listing them as currently refused).

**One quality caveat the fix shape omits:** the refusal it produces quotes the
run *including* the filler — *"There is no 'Zorglub just' in the order of
battle"*, *"There is no 'Grouchy now'"*. That names back at the player something
he did not offer as a name, which is FA-54's class. The phrase should be trimmed
of trailing set-words before it is quoted.

---

## 6. ONE DEDUPE NOTE

**L2-3 is a strict sub-case of L2-4**, not a sibling: `the` is one of the 66
alternation members, and `the Iron Marshal attack Mack` stands down by the same
`.search()` over the same run. One predicate, one `.search`, one stand-down. The
lens says as much in passing ("Same root as L2-3") but files them as two P2s and
prices the work twice. Build them as one row.

---

## WHAT THE BUILD SHOULD CARRY FORWARD

* The behaviour is **real, reproducible, and P1** — `Wellington now retreat`
  marches eight corps at zero AP.
* It is **not row CX's regression**; it is the part of FA-22 the row narrowed
  and did not close. File it under the same head as L2-1 ("the rule is one verb
  wide"): *the record over-claims*, and §3.1 of the spec should name the residue.
* The head-token rule is a **safe** change (23,656 green) and closes L2-3 + L2-4
  together — but it closes **neither** L2-5 nor L2-1, and it needs the refusal
  copy trimmed.
