# VERDICT:DESK-6 — **REFUTED**

> `_answer_reach` promises a march by a prisoner; `_answer_what_if` musters prisoners
> — filed P3 by lens "desk", claimed player-reachable, claimed shipped by row CX.

**Verdict: REFUTED on both halves.** The filed reproduction is a state the game
cannot produce. On every production route the invariant
**`captured_by` ⟹ `strength == 0`** holds, and both desk arms already filter on
`strength > 0` — one through the parser roster, one in the candidate loop
itself. The suggested fix ("reuse `counsel._is_free_to_order` in both arms") is
a **no-op in production**, and would copy a **dead clause** into two more sites.

Tree: master `727cf88a`, clean. Probes: `probes/desk6/` (`d6.py` harness +
`p1`…`p11`), all driven through `POST /command` on `backend.main.app` — i.e.
through main.py's own `get_llm_game_state`, not a mirror.

---

## 1. The filed repro is hand-set state, not game state

The lens's `lens3/p10_edge_answers.py` does exactly this and nothing else:

```python
w2 = boot_1805()
for m in w2.get_player_marshals():
    m.captured_by = "Austria"        # strength and location untouched
```

The game has **one** capture seam. `WorldState.capture_marshal`
(`world_state.py:4957`, the W6-7 §9.1 / NP-4 shared seam) sets the flag **and**:

```python
marshal.captured_by = captor_nation
marshal.captured_turn = int(self.current_turn)
marshal.strength = 0                  # <- world_state.py:4982
...
marshal.location = captor_capital     # held at the captor's capital
```

An AST-free grep over the whole backend finds **three** writers of
`captured_by` and no more:

| site | what it does |
|---|---|
| `world_state.py:4980` `capture_marshal` | sets it — **and zeroes strength** |
| `world_state.py:5091` (release/ransom) | **clears it first**, then `strength = RANSOM_RETURN_STRENGTH` |
| `marshal.py:2050` `from_dict` | restores what was saved (post-capture: 0) |

The release path clears the flag **before** restoring strength, so there is not
even a one-statement window where both are true.

**Measured (`p10`, `p11`)** — the invariant survives every route I could find:

```
WorldState.capture_marshal(Ney,'Austria') -> captured_by='Austria' strength=0 location=Vienna
INVARIANT captured_by => strength==0 HOLDS: True

(a) recruit into him?
  > recruit for Ney            -> FAILED, and already names him:
    "...Ney (a prisoner of Austria); Davout (out of range - 5 regions away)..."
  > recruit infantry in Vienna -> FAILED, same line.   Ney strength still 0
(b) eight end-turns:  turn 2..9  captured_by='Austria' strength=0 loc=Vienna
(c) to_dict -> from_dict round trip: captured_by='Austria' strength=0 loc=Vienna
```

---

## 2. The `_answer_reach` half: the quoted sentence is unreachable — the arm is never entered

The filed line is *"Yes, Sire — Ney can reach Vienna from Rhineland in 4 turns:
Rhineland -> Swabia -> Franconia -> Bohemia -> Vienna."* On a production
capture Ney is at **Vienna** with **0** men, and the question does not even
**classify**:

`backend/main.py::get_llm_game_state`, line 226:

```python
for m in world.get_player_marshals():
    if m.strength > 0:          # <- the roster filter
        marshals[m.name] = {...}
```

so "Ney" is not a marshal subject and `classify_question` returns `None` before
`_answer_reach` exists as a possibility.

**Measured (`p2`, `p11`), same board, the two states side by side:**

```
REVIEWER's hand-set (captured_by only, strength untouched)
   'Ney' in parser marshal roster: True
   classify('can Ney reach Vienna') -> {'kind':'reach','subject':'Ney',...,'place':'Vienna'}

PRODUCTION capture_marshal()
   Ney: captured_by='Austria' strength=0 loc=Vienna
   'Ney' in parser marshal roster: False
   roster = ['Davout','Soult','Lannes','Murat','Bernadotte','Massena','Napoleon']
   classify('can Ney reach Vienna') -> None
   classify('can Ney reach Paris')  -> None

PRODUCTION capture -> to_dict -> from_dict (save/load): classify -> None
```

Driven through `POST /command` on the production-captured board:

```
> can Ney reach Vienna
  "Regarding Vienna, Sire — I need a marshal and an action. For example:
   'Davout, move to Vienna'." Berthier taps the map pointedly.        [AP 4 -> 4]
> can Ney reach Paris
  Berthier studies the map. "Sire, I note the reference to Paris, but which
   marshal should act? ..."                                           [AP 4 -> 4]
```

**No march is promised.** Nothing is spent. The only residue is that the shrug
does not *say he is a prisoner* — see §5.

---

## 3. The `_answer_what_if` half: the loop's existing `strength > 0` already does it

`_answer_what_if`'s candidate loop (`question_desk.py:705`) filters
`int(getattr(marshal, "strength", 0) or 0) <= 0`. That **is** the captivity
filter, in production.

**Measured (`p1` ARM B/C vs ARM C′, `p11`):**

```
ARM B — capture_marshal(Ney) only
  > what happens if I attack Mack
    MUSTER — Davout (26,000; ...) vs Mack at Swabia ...      <- Ney absent, correct

ARM C — EVERY French marshal captured, PRODUCTION path
  > what happens if I attack Mack
    "No corps of ours stands within reach of Mack at Swabia, Sire —
     there is no battle to weigh."                            <- correct
  > what can I do
    "Nothing can be ordered this turn, Sire."                 <- correct

ARM C' — EVERY French marshal captured, the LENS's hand-set path
  > what happens if I attack Mack
    MUSTER — Ney (24,000; 78,676 if all march ...)            <- the filed claim,
      WILL JOIN — Davout / Lannes / Murat ...                    reproducible ONLY here
  > what can I do
    build supply depot in Rhineland — 300g                    <- the filed contrast,
    build fortification in Rhineland — 400g                      also only here
```

The lens's own crux — *"one slice, two answers, one guard"* — **inverts on the
production board**: in ARM C both answers agree, and they agree for the same
reason (`strength > 0`), not because one has the captivity clause.

---

## 4. The suggested fix would ship a dead line, and fix nothing

`counsel._is_free_to_order` has three clauses. Census against the shipped
`Marshal` and the shipped production writers (`p5`, `p11`):

| clause | production reality |
|---|---|
| `strength <= 0` | **the only live one** — and both desk arms already have it |
| `captured_by` | **subsumed**: the one capture seam zeroes strength (§1) |
| `administrative` | **subsumed**: both writers (`disobedience.py:1904`, `meta_executor.py:1802`) also set `strength = 0` |
| `is_drilling` | **DEAD** — `Marshal` has no such attribute |

```
hasattr(Marshal,'is_drilling') = False   (real flags: drilling, drilling_locked
                                          — marshal.py:427-428)
_is_free_to_order(a LOCKED-IN-DRILL marshal) = True    <- the clause is dead
_is_free_to_order(strength 0)                = False
```

So in production **`_is_free_to_order` ≡ `strength > 0`**. Copying it into
`_answer_reach` changes nothing (the roster filtered him one layer up) and into
`_answer_what_if` changes nothing (the loop already has the same test) — while
propagating a clause that reads a non-existent attribute to two more call sites.

**Would it red a pin?** No — `tests/test_cx2_berthier_answers_the_board.py`
pins the reach arm only against the movement law
(`test_the_reach_answer_obeys_the_movement_law`, line 220) and has no prisoner
case. That is *worse* than redding a pin: the change would be invisible, inert
and load-bearing-looking.

---

## 5. What is actually true in the neighbourhood (both smaller, neither DESK-6)

**(a) P4, NEW, shipped by CX-2 — `counsel._is_free_to_order`'s drilling clause
is dead.** `counsel.py` is created by `5fc3d5c8` (verified: `git show
b4a27a15^:backend/ai/counsel.py` does not exist), so this line is the row's.
It should read `drilling` / `drilling_locked`. **But repairing it produces no
desk-vs-executor divergence on the arms DESK-6 names** — measured on the
committed `t20` fixture (`p8`, `p9`), with Ney at `drilling=True,
drilling_locked=True`:

```
> can Ney reach Swabia        -> "Yes, Sire — Ney can reach Swabia ... in 1 turn"
> Ney, march to Swabia        -> "Ney begins march to Swabia. Route: Rhineland -> Swabia."
                                 SUCCEEDED, AP 4 -> 2
```

The desk did not lie; the executor carried the order out (the drill block at
`executor.py:1779` is `and not is_strategic_execution`, and the strategic march
path does not reach it). File it as a code-hygiene row against `counsel.py`, not
as a shown≠applied defect. *(No French marshal can be put on drill at the 1805
boot at all — every one has an enemy one region away, `p7`.)*

**(b) P4, legibility, not DESK-6's seam.** `can Ney reach X` for a captured Ney
gets Berthier's generic shrug rather than `_answer_own_marshal`'s prisoner line.
PC15-4's guard (`main.py::_addressed_lost_marshal_refusal`) keys on
`_leading_addressed_token`, and a question has no leading address, so it does
not fire either. Nothing is promised and nothing is spent — the owner is
PC15-4's reach, not `_is_free_to_order`.

---

## Answers to the four attack questions

* **Does it reproduce as stated?** **No.** Only with `captured_by` hand-set and
  `strength`/`location` left untouched — a state with no producer in the
  backend.
* **Is the severity right?** No — filed P3, measured **INFO**: no defect
  survives. The residues in its neighbourhood are P4 and are different rows.
* **Player-reachable?** Moot, and **no**. `can …` is not claimed by
  `main.gd::_redirect_diplomatic_command` ("can" is absent from
  `DIPLO_ADVISORY_STARTS`, but the sentence matches no cabinet family either,
  so it fails open) and `what …` is exempted as advisory — both sentences reach
  the backend. They just do not produce the filed behaviour.
* **Shipped by row CX?** The two **functions** are (`git show
  b4a27a15^:backend/ai/question_desk.py` has neither `_answer_reach` nor
  `_answer_what_if`). The **defect** is not, because there is none. The one
  thing the row did ship here is the dead `is_drilling` clause, §5(a).
* **Would the fix regress?** Not by redding a pin — by being inert while
  reading as a guard, and by spreading a dead attribute read.

---

## The lesson this verdict is an instance of

The row's own recorded discipline is *construct the ORDINARY case*. DESK-6 did
the opposite of the usual failure: it constructed a state **more** convenient
than the game's, by setting one field of a five-field transition. **When a
finding depends on an object being in a particular state, reach that state
through the production seam that writes it** — here `WorldState.capture_marshal`,
whose second statement is the whole refutation.
