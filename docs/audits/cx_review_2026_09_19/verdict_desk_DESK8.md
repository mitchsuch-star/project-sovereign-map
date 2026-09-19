# VERDICT:DESK-8 — NARROWED

**Row:** DESK-8, filed by lens "desk" at P3.
**Verdict:** **NARROWED** — it reproduces in full, it is player-reachable, and
row CX shipped it; but its TITLE mis-describes two of its own ten rows, its
flagship row has a larger cause it does not name, three surfaces are
structurally unreachable (which it misses), it never states a rate — and
**two of its three prescribed fix arms ship a regression, one of them
severe.**

Tree: master `727cf88a`, clean. Probes: `…/cx_review/probes/desk8/`
(`d8_harness.py`, `p01`…`p08`). Every figure below is from a probe I ran, not
from the filed report. I had to isolate my harness into `probes/desk8/`
mid-run because a concurrent lens overwrote `probes/harness.py`.

---

## 1. Does it reproduce? YES — all ten rows, exactly as filed

Driven through `POST /command` on a fresh shipped 1805 board
(`WorldState.from_scenario(europe_1805.json)`, turn 1, France), module globals
swapped per the production shape (`p01_repro.py`, `p02_allies.py`):

| typed | pointer the game gave |
|---|---|
| `how is the war effort` | the Strategic Ledger's Economy tab (press T, then 3) |
| `is our war effort sustainable` | the Strategic Ledger's Economy tab |
| `why won't Ney fortify` | the Strategic Ledger's Economy tab |
| `why did the charge fail` | the Strategic Ledger's Economy tab |
| `why did Murat's charge fail` | the Strategic Ledger's Economy tab |
| `what are our borders` | the Strategic Ledger's Orders tab (press T, then 6) |
| `why is there disorder in Swabia` | the Strategic Ledger's Orders tab |
| `why did the attack really fail` | the Cabinet (press F1) |
| `why did the assault finally fail` | the Cabinet (press F1) |
| `who are my allies` | **(no pointer line at all)** |

Verbatim, `how is the war effort` (`p08_verbatim.py`):

```
Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
What you want is in the Strategic Ledger's Economy tab (press T, then 3).

What I CAN do today:
  Ney, attack Mack
  ...
For any matter of state, press F1 for the Cabinet.
Type 'help' for the full command reference.
```

**Player-reachable: YES, all ten.** I re-implemented
`main.gd::_redirect_diplomatic_command` by SCRAPING its constants out of
`main.gd` and `utils.gd` rather than retyping them (`p04_client_gate.py`;
7 advisory leads, 115 family keywords, 29 nation forms) — all ten return
`REACHES BACKEND`. Nine are exempted by `DIPLO_ADVISORY_STARTS`
(what/how/why/who); `is our war effort sustainable` matches no family keyword
and names no court, so it fails open.

**Shipped by row CX: YES.** `git show b4a27a15^:backend/commands/meta_executor.py`
contains neither `_QUESTION_TOPICS` nor `_route_unanswered_question`;
`git log -S` puts both in `5fc3d5c8` (CX-2). Dropping the row's own levers
(`QD.QUESTION_DESK_ACTIVE = False`) returns all ten to the pre-CX route —
a **12,720-character COMMAND REFERENCE with no pointer at all**
(`p06_baseline_and_fix.py`).

---

## 2. Where the finding is WRONG about itself

### (a) The title is wrong for 2 of its own 10 rows

`why did the charge fail` / `why did Murat's charge fail` are **not substring
collisions**. `"charge"` is a whole word in the economy row and matches as a
whole word. The finding's body concedes this in passing (*"and the economy row
is scanned before the 'fail'→log row"*) while the title says *"matches
substrings"*. Proof by measurement (`p07`): under word-boundary matching both
still route to `economy`. The mechanism for those two is **row precedence**,
not substring matching — which matters, because the finding's own arm (a) does
not touch them.

### (b) `who are my allies` has a larger cause the finding never names

The finding files it as a missing plural (*"'allies' does not contain
'ally'"*). Measured (`p06` part 3):

```
surfaces defined : admiralty courts diplomacy dispatch economy forces
                   gazette log marshals orders war
topics in table  : admiralty diplomacy economy forces gazette log
                   marshals orders
UNREACHABLE      : courts, dispatch, war
```

**`_QUESTION_TOPICS` has no `courts` row, no `war` row and no `dispatch`
row at all.** An AST-free census of `surface_pointer(` callers shows the only
literal call sites are `"economy"`, `"war"` and `"courts"` inside
`question_desk.py`'s own *answered* kinds — so from the router,
**the Diplomatic Ledger, the war banner and the morning dispatch can never be
named, whatever plurals are added.** `"dispatch"` is reachable from nowhere in
the backend at all.

### (c) Two more instances of the same family, not filed

Measured on the same board (`p05_rate.py`):

* `who are my enemies` → **no pointer** (`"enemy"` ⊄ `"enemies"` — the same
  class as `allies`, which the finding presents as a singleton).
* `what is the war score`, `who is ahead in the war`, `how long has this war
  run` → **the Cabinet (press F1)**, because `"war"` lives in the *diplomacy*
  row and the `war` surface has no row of its own. Whole-word matches; not a
  substring bug.
* `what is our standing with Prussia` → **the Orders tab** (`"standing"`).

### (d) It states no rate, and the rate is much lower than ten hand-picked rows imply

I wrote five natural questions per topic *per topic, before routing any of
them* (50 total, `p05_rate.py`), and drove them through `POST /command`:

```
reached the ROUTER: 39   (the desk answered the other 11)
  right pointer : 26  (67%)
  WRONG pointer :  5  (13%)
  no pointer    :  8  (21%)
```

So the shipped router points **correctly two times in three**. The filed table
is ten collisions with no denominator, which reads as though the table were
broadly wrong. It is not.

---

## 3. Severity: P3 is right — hold it

Arguments for LOWER: the wrong pointer is one line of ten; it costs no AP
(`free_action`), starts nothing, and the rest of the answer — the counsel, the
Cabinet door, the help hint — is intact and correct. The player presses T,3,
sees nothing, presses L. And **pre-row these ten sentences got a 12,720-char
manual with no pointer at all**, so this is a new line that is sometimes
wrong, not a regression of something previously right.

Arguments for holding at P3: the row's own comment at the table states the
standard it fails (*"a wrong pointer is worse than none"*), and the
unreachable-surface half (§2b) is a genuine structural gap the finding
under-states rather than over-states.

**Held at P3.**

---

## 4. Would the suggested fix ship a regression? YES — two of three arms

No pin reds. The only pin that reads a router pointer is
`tests/test_cx2_berthier_answers_the_board.py::TestTheRouter::
test_an_unanswerable_question_is_short_and_names_a_surface`
(`why did that fail` → `"campaign log"` + `"press L"`) — plus the same
utterance in `TestTheTwelveQuestions`. **Both survive all three arms.** So the
fix would break *sentences no pin covers*, which is exactly why it has to be
measured.

### Arm (c) *"move the `why`/`fail` log row above the economy row"* — SEVERE

`"why"` is **a member of the log row**:

```
(("fail", "failed", "refuse", "refused", "rejected", "why"), "log")
```

So putting that row first routes **every sentence containing the word "why"**
to the campaign log — arithmetic, not a corpus artefact. Measured over 16
natural "why" questions (`p07_fix_arms_combined.py`): **14 of 16 broken.**

```
why am I losing money        economy -> log     <-- BROKEN
why is my treasury falling   economy -> log     <-- BROKEN
why can't I afford this      economy -> log     <-- BROKEN
why is the upkeep so high    economy -> log     <-- BROKEN
why are we bankrupt          economy -> log     <-- BROKEN
why did my income drop       economy -> log     <-- BROKEN
why won't the fleet sail     admiralty -> log   <-- BROKEN
why is my manpower pool empty forces -> log     <-- BROKEN
why did the coalition form   diplomacy -> log   <-- BROKEN
why is Davout jealous        marshals -> log    <-- BROKEN
```

**The sentence it breaks:** `why am I losing money` is answered today with
*"the Strategic Ledger's Economy tab (press T, then 3)"* and would be answered
*"the campaign log (press L)"* — the one screen that cannot tell him. That is
a strictly worse table than the one filed as defective.

### Arm (a) *"match on word boundaries (`\bfort\b`)"* — LOSES MORE THAN IT FIXES

The table's words are **stems**, and word-boundary matching un-matches every
inflection. `\bfort\b` in particular stops matching **`fortification`**, which
is the building that row exists for.

Measured on the unbiased 50 (`p06`): right **34 → 31**, no-pointer **10 → 13**
(`how many conscripts remain`, `is Ney still marching`, `which courts are
hostile` all fall to *no pointer*). On the hand-labelled 35 of `p03` the loss
is larger — right **22 → 14**, no-pointer **2 → 13**: `how many depots do we
hold`, `are our markets damaged`, `what are the charges of empire`, `how many
ships do we have`, `what are our alliances`, `which courts have designs on
us`, `how are my marshals`, `who are my generals`, `what is a fortification
worth`, `is Rhineland fortified` all go from a correct pointer to none.

And it **fixes only 2 of the finding's own 10 rows** (`really` / `finally`);
the other eight are untouched or still wrong (`p07` part iii).

### Arm (b) *"add the plurals the table means (`allies`, `orders`)"* — safe, but does not do what the finding asks

`"ally"` lives in the **diplomacy** row, so an added `"allies"` points at
**the Cabinet (press F1)**. The finding's own table says the player wants
**the Diplomatic Ledger (press D)**. Arm (b) swaps a *no* pointer for a
*different wrong* pointer (`p07` part ii). It cannot do better without the
missing `courts` row from §2b.

---

## 5. What a correct fix looks like (measured, not asserted)

1. **Add the three missing rows** — `courts` (`allies`, `enemies`, `nations`,
   `relations`, `standing`, `neutral`), `war` (`war score`, `winning`,
   `losing`, `war effort`), `dispatch` — and move `war`/`court`/`ally` out of
   the diplomacy row where they belong to those surfaces. This is the half the
   finding misses and it closes `who are my allies`, `who are my enemies`,
   `what is the war score` and `how is the war effort` in one edit.
2. **Do NOT move the log row.** Drop `"why"` from the log row instead and keep
   the row last — a "why" question is about *whatever noun follows it*, which
   is what the later rows already read.
3. **Do NOT switch to `\b…\b` wholesale.** If stem-vs-word precision is wanted,
   it has to be per-word (`\bfort\w*\b` for the stems, `\beffort\b` as an
   explicit non-match), and the acceptance test must be a corpus written
   per-topic before routing — otherwise the change trades 10 wrong pointers
   for 13 silent no-pointers.
4. Whatever lands, **pin a corpus, not an example**: this row's ten sentences
   sat under a green 23,618-test suite because the only router pin in the
   codebase is a single utterance.
