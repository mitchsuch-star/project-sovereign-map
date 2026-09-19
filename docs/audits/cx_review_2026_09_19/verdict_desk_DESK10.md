# VERDICT:DESK-10 — NARROWED

**Row filed by lens "desk" as:** *"The reach answer's turn count double-counts
for cavalry"*, P3, player-reachable, shipped by row CX, fix shape
`ceil(steps / marshal.movement_range)`.

**Verdict: the DEFECT is real and reproduces. The ROW is wrong about its own
arithmetic, wrong about its own reproduction by one turn in the flattering
direction, wrong that the defect is cavalry-only — and its prescribed fix does
not fix the case it reproduces.**

Everything below is from probes I wrote and ran myself
(`…/scratchpad/cx_review/probes/p1`…`p6`), driven through `POST /command` on
the shipped 1805 board built by `parser_eval.build_world("1805")`. I did not
run the lens's `p08b_cavalry_turns.py`.

---

## 1. Does it reproduce AT ALL? — Yes, and on a board the lens did not need to touch

The row's reproduction **relocates Murat to Rhineland**. That relocation is
unnecessary and it weakened the case. On the **untouched shipped boot** Murat
stands at **Franche-Comte**, and the defect is already there (`p4`):

```
> can Murat reach Orleanais
Yes, Sire — Murat can reach Orleanais from Franche-Comte in 2 turns:
Franche-Comte -> Lorraine -> Orleanais.

> Murat, march to Orleanais
Murat begins march to Orleanais. Cavalry charges through Lorraine -> Orleanais.

    Murat.location immediately after the order  ->  Orleanais
    end-turns required to arrive                ->  0
```

**Quoted 2 turns. Arrives before the player can end the turn.** Live board,
ambient war running, no relocation, no quieting.

### 1a. The row under-reported its own drift by one turn

I then reproduced the row's *exact* stated geometry — Murat moved to Rhineland,
quiet board (`p6`):

```
desk : Yes, Sire — Murat can reach Orleanais from Rhineland in 2 turns:
       Rhineland -> Lorraine -> Orleanais.
order: Murat begins march to Orleanais. Cavalry charges through Lorraine -> Orleanais.
QUOTED 2 | REAL 0 end-turn(s)
```

The row says *"ARRIVED after 1 end-turn"*. **It is 0.** The row's own quoted
order message — *"Cavalry charges through Lorraine -> Orleanais"* — already
says he is at Orleanais, so the row's evidence contradicts the row's own count.
This matters, because the 1 it printed is the number its own proposed fix
produces (`ceil(2/2) = 1`), which is how a fix that does not work came to look
like it worked.

---

## 2. "Double-counts for cavalry" is wrong twice over

I measured the whole curve on a quiet board (all French wars → PEACE, enemy
corps removed) for two marshals standing on the **same square**, Franche-Comte,
so `movement_range` is the only variable (`p5`):

| road (provinces) | INFANTRY r=1 quoted → real | CAVALRY r=2 quoted → real |
|---:|---|---|
| 1 | 1 → **0** ✗ | 1 → **0** ✗ |
| 2 | 2 → 2 ✓ | 2 → **0** ✗ |
| 3 | 3 → 3 ✓ | 3 → **2** ✗ |
| 4 | 4 → 4 ✓ | 4 → **2** ✗ |
| 5 | 5 → 5 ✓ | 5 → **3** ✗ |

**(a) It is not a doubling.** Road 2 → 2 vs 0; road 3 → 3 vs 2; road 5 → 5 vs 3.
Only road 4 happens to be exactly double. The row generalised from one cell.

**(b) It is not cavalry-only.** Infantry at road 1 is wrong too: *"can reach
Lorraine … in 1 turn"* for a corps that is standing in Lorraine the moment the
order is given. That is the single most common reach question a player can ask
(an adjacent province) and the row does not mention it.

**(c) Why infantry is right at road ≥ 2 — and it is a coincidence, not a
design.** Two opposite errors cancel. `MOVE_TO` takes its first step **free at
issuance**, up to `movement_range` provinces
(`strategic_executor.py` ~1355, *"Execute first step immediately"*); and the
per-turn processor then **skips the issuing turn** (FA slice 12's `issued_turn`
rule). For a range-1 corps the free step and the skipped pass are worth one
province each and annihilate. For a range-2 corps the free step is worth two,
so nothing cancels and the error grows with the road.

Measured law, matching all ten cells above:

```
real end-turns = 0                                   if road <= range
               = 1 + ceil((road - range) / range)    otherwise
```

`_answer_reach` prints `max(0, len(lawful) - 1)` — the road in **provinces** —
and calls them **turns**.

---

## 3. Severity: P3 is right, and should not be raised

- Nothing is spent to ask, no AP moves, no battle starts (I re-checked on
  every arm: `AP 4 → 4`).
- **The ROAD is correct.** On every case I drove, the road the desk prints is
  the road the executor walks (`Murat@Rhineland → Vienna`: desk
  `Rhineland -> Swabia -> Franconia -> Bohemia -> Vienna`; order
  `Route: Franconia -> Bohemia -> Vienna. Cavalry charges through Swabia ->
  Franconia`). The count drifts; the plan does not.
- Largest absolute error measured is **2 turns** (cavalry, road 4 and 5).

P3. Display-only drift against the row's own *"a quoted figure is the applied
figure"* promise. Not P2 — no decision is priced off it and nothing is charged.

---

## 4. Player-reachable: YES — confirmed, not assumed

I re-implemented `main.gd::_redirect_diplomatic_command` in Python from the
`.gd` source (`p6`, reading the `const` tables out of `main.gd` rather than
retyping them). `can <marshal> reach <place>` is **not claimed** by the client:
the first word `can` is not in `DIPLO_ADVISORY_STARTS` (wh-words only), so it
falls to `_matches_cabinet_family`, which finds no family keyword, no
`court`, no autonomy verb+level, no nation-gated prefix, and no
`DIPLO_NATION_ANYWHERE_KEYWORDS` hit.

```
reaches backend    can Murat reach Orleanais
reaches backend    can Murat reach Orleanais?     (the "?" advisory arm)
reaches backend    could Ney reach Vienna
reaches backend    can Ney get to Vienna
reaches backend    can Murat make it to Naples    (place that is also a court)
reaches backend    can Massena reach Rome
```

All six reach the backend. **The row's reachability claim holds.**

---

## 5. Shipped by row CX: YES — confirmed structurally and behaviourally

- `git show b4a27a15^:backend/ai/question_desk.py` is 353 lines and its
  function list has **no** `_answer_reach` and **no** `classify_board_question`.
- First appearance: **`5fc3d5c8` (CX-2)**. Present unchanged at HEAD.
- `git grep "can reach" b4a27a15^ -- backend/` returns only unrelated comments.
  **No pre-row surface anywhere in the backend prints a march ETA.** A
  `find_path` census over `backend/` confirms `_answer_reach` is the only
  consumer that converts a path into a number of turns.

So there is no sibling to inherit a correct formula from — and none to blame.
The row's "shipped by this row" claim holds.

---

## 6. ⛔ The prescribed fix ships a wrong number — in the row's own reproduction

`ceil(steps / marshal.movement_range)`, evaluated against the measured law:

| case | road | range | real | **lens fix** | verdict |
|---|---:|---:|---:|---:|---|
| **the row's own reproduction** | 2 | 2 | **0** | **1** | ✗ still wrong |
| Murat → Lorraine | 1 | 2 | 0 | 1 | ✗ still wrong |
| adjacent infantry march | 1 | 1 | 0 | 1 | ✗ **unchanged** |
| infantry, any road ≥ 2 | N | 1 | N | N | = unchanged (already right) |
| Murat → Vienna | 4 | 2 | 2 | 2 | ✓ fixed |
| Murat → Normandy | 5 | 2 | 3 | 3 | ✓ fixed |

Two consequences the row does not state:

1. **`ceil(N/1) == N`, so the fix is a cavalry-only edit.** It leaves every
   infantry sentence byte-identical, including the wrong one at road 1.
2. **It is wrong by exactly one for every road within the corps' own range** —
   which is the boundary where the honest answer is *"this turn"*, not a number
   at all. That set includes the case the row reproduces to justify itself.

**And nothing would catch it.** The row's own slice pin,
`test_cx2_berthier_answers_the_board.py::test_the_reach_answer_obeys_the_movement_law`,
asserts only that `" -> ".join(lawful)` appears in the message — it never reads
the count. A corpus scan finds **0** rows carrying `reach` or `get to`. A grep
for `"in N turn(s)"` across `tests/` finds no pin on this string. So the fix
would red **no pin, break no sentence, and ship** — with the row's own
reproduction still misquoted.

**Fix shape I would build instead:** the measured law above, with the
sub-range case saying so in words rather than in a number —
*"Yes, Sire — Murat reaches Orleanais this turn: Franche-Comte -> Lorraine ->
Orleanais."* — and a pin that drives the real march to arrival and compares,
rather than asserting a string.

---

## 7. What I could not break

- The road is never wrong relative to the executor on any case I drove.
- Asking costs no AP and starts no battle on any arm.
- The `end turn` confound is real but is not this defect: on the **live**
  board long marches stall or reverse (ambient battles and forced retreats —
  `p4` shows Murat walking Burgundy → Franche-Comte → Lorraine). That makes the
  quote soft in practice for long roads, but the quiet-board curve in §2 is the
  movement law alone and is what the desk should be quoting.

---

### Summary line

The defect is **CONFIRMED and reproduces on the untouched boot**, but the row
is **NARROWED**: it is not a doubling, it is not cavalry-only, its own
reproduction is off by one turn in its own favour, and its `fix_shape` is a
cavalry-only edit that leaves the reproduced case — and every adjacent-province
march — still wrong, with no pin standing in its way.
