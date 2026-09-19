# VERDICT: CXR1-5 — **NARROWED** (and measured PRE-EXISTING)

**Filed by:** lens `question-guard`, P2, "Arms (a) and (b) are anchored at `^`
behind a five-word filler list, so one unlisted filler re-opens them."
**Verdict:** the defect is **real and reproduces in full** — all eight claimed
utterances, independently, on the shipped 1805 board. Three of the row's
surrounding claims do not survive, and **both of its suggested fixes ship a
regression** — one of them reds a named pin.

Tree: `f52df77f` (HEAD; one docs-only commit past the `727cf88a` named in the
brief — `git show --stat f52df77f` touches no source). Probes:
`probes/verdict_cxr15/` (`h.py` harness, `p1`…`p7`), all written for this
verdict, none inherited from the finder.

---

## 1. Does it reproduce? YES — 8 of 8, exactly as stated

`p1_claimed.py`. Fresh 1805 board per utterance, driven at `POST /command`.
Footprint deliberately **wider** than the finder's (AP, admin AP, DP, gold,
turn, every marshal's location/strength/state/order, **region buildings,
region control, `world.fleets`, `world.vassals`, `world.diplomatic_states`**),
because three of the eight are economy/diplomacy verbs whose effect an
AP/gold/marshal snapshot can only see indirectly.

```
'hmm why not defend'                     ap 4->3                    All forces take defensive positions: Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena, Napoleon
'uh why not defend'                      ap 4->3                    (same)
'hey why not build ships'                admin 2->1, gold 800->400, fleets!   A keel is laid at Bordelais (400g). The fleet stands at 46 sail...
'right why not build a depot in Paris'   admin 2->1, gold 800->500  Construction started: Supply Depot in Paris (2 turns, 300 gold)
'actually what about build ships'        admin 2->1, gold 800->400, fleets!
'honestly what about defend'             ap 4->3
'anyway what about release Holland'      dp 5->4, vassals!, relations!   Holland is released from vassalage... Their tribute of 337 gold a turn ends.
'just wondering why not retreat'         marshals: all 8            General retreat ordered! Ney falling back! ...
```

Controls behave as the finder says: `hmm, why not defend` and `so why not
defend` are both inert.

**What the flagship actually costs** (`p4_regression.py`, measured, not quoted):

```
Bernadotte  Franconia     -> Munich          17000 -> 16830   (-170)
Massena     Milan         -> Munich          42000 -> 39900   (-2100)
Davout/Lannes/Murat/Ney/Soult/Napoleon relocate, strength unchanged
AP spent: 4 -> 4      men lost: 2,270      no confirmation prompt
```

A free, unasked, whole-army retreat: eight corps displaced, 2,270 men to
movement attrition, **0 AP**, from a sentence whose first two words are *just
wondering*.

**And it is worse than filed.** `p5_size.py` / `p6_why_inert.py` found four
openers the finder did not try, each of which is a *more* unambiguous question
than anything on their list, and each of which orders the same general retreat:

```
EXEC  'I wonder why not retreat'        all 8 corps fall back
EXEC  'tell me why not retreat'         all 8 corps fall back
EXEC  'my question is why not retreat'  all 8 corps fall back
EXEC  'we wonder why not retreat'       all 8 corps fall back
```

`_FIRST_PERSON_RE` exists precisely for these and never runs: it is consulted
*after* the lead match, and the lead match is what the leading token destroys.

---

## 2. Is it PRE-EXISTING? YES — measured on a true pre-row tree

`p2_prerow.py`. `git archive b4a27a15^` (the commit before CX-1) extracted
read-only into the scratchpad, driven at its own `POST /command` with its own
1805 map.

```
PRE-ROW (b4a27a15^):  all 8 claimed  EXECUTED
                      all 5 bare forms ('why not defend', 'why not retreat',
                      'what about build ships', 'what about release Holland',
                      'why not build a depot in Paris')  EXECUTED
                      both controls ('hmm, why not defend', 'so why not defend')  EXECUTED
                      -> 15 of 15
HEAD:                 the 5 bare forms and both controls are INERT; the 8
                      filler-fronted forms still execute
                      -> 8 of 15
```

`pre-row has A_QUESTION_NEVER_ORDERS: False` — the arms did not exist. The
`^`-anchored five-filler prefix is **older than row CX**: `git log -S` puts
`ok(?:ay)?\s*,?\s*` in `cff23e9e` (PARSE-NEG, Aug 3 2026), and `git show
b4a27a15 -- backend/ai/clause_guards.py` shows CX-1 never touched
`_INTERROGATIVE_LEAD_SRC`.

**Row CX did not open this hole; it closed 7 of 15 doors in it and left 8.**
The finder's own `shipped_by_this_row: false` is correct, and is now measured
rather than asserted.

---

## 3. NARROWING (a) — player-reachable is **7 of 8**, not 8

`anyway what about release Holland` **cannot be typed into the shipped
client**. `main.gd::_redirect_diplomatic_command` (the only pre-send gate, at
`_execute_command`, after the end-turn and redemption-token blocks) claims it:
`DIPLO_NATION_GATED_PREFIXES` contains `"release "`, and
`_names_a_nation("holland")` is true (`Holland` is a `Utils.NATION_COLORS`
key). The player gets *"Matters of state are conducted at the table, Sire"* and
a Cabinet link. **Nothing is sent and nothing is spent.**

The irony is exact and worth recording: `_is_advisory_question` reads only
`words[0]`, so the client is anchored at `^` in the same way the backend is —
and here the two blindnesses **cancel**. Bare `what about release Holland`
opens with `what`, is exempted as advisory, is sent, and the backend's
`is_question` catches it. Add a filler and the client claims it instead. The
vassal is safe on both roads, for opposite reasons.

The other seven carry no diplomatic keyword, no nation, no diplomat address and
no end-turn phrasing, so `_matches_cabinet_family` fails open and they reach
`api_client.send_command` verbatim. **Reachable.**

---

## 4. NARROWING (b) — "one unlisted filler re-opens them" is verb-dependent

`p5_size.py`: 34 openers × 2 verbs, fresh board per cell, **36 of 68 executed**
— but not evenly.

| tail | executed | inert |
|---|---|---|
| `what about defend` | **27 of 34** (every opener but the 7 allowlisted) | 7 |
| `why not retreat` | **9 of 34** | 25 |

`p6_why_inert.py` shows why, and it is **not** the guard: `is_question` is
`False` for *every* filler-fronted line in both columns. The 18 extra retreat
cases are stopped downstream, by accident, at the retreat route's marshal
resolution —

```
'hmm why not retreat'            -> "There is no 'hmm why not' in the order of battle, Sire."
'quick question why not retreat' -> "There is no 'quick question why not' in the order of battle, Sire."
'tell me why not retreat'        -> GENERAL RETREAT   (the openers made of pronouns and
'I wonder why not retreat'       -> GENERAL RETREAT    `_EMPTY_RESIDUE_WORDS` are stripped,
'now why not retreat'            -> GENERAL RETREAT    so the bare verb survives)
```

So the finder's **cause is right** (the lead never matches; nothing in
`is_question` runs) and their **width is not**: the flagship verb is shielded
against most openers by a refusal that is about something else, and the ones
that get through are the *pronoun* openers — the most question-like of all.
Their "43 executing in the filler arm" is their grid, not mine; I did not
reproduce their count, and my grid says the rate depends on the verb.

*(Aside, not filed: `There is no 'hmm why not' in the order of battle` quotes
three words as a marshal's name. FA-54's class, one seam over.)*

---

## 5. NARROWING (c) — **both suggested fixes ship a regression**

`p3_fixcost.py` classifies 619 unique sentences the game itself produces or
pins (449 golden-corpus utterances + the live-phrasing backlog + scenario
`suggest` chips + every typed echo in `scripts/*.gd`) under HEAD and under each
candidate.

### Option (i), "skip a bounded leading run of tokens" — reds a named pin

2 verdict flips, both to QUESTION, and the first is a **pinned corpus row**:

```
'I will march to Lorraine'   corpus id `first-person-march`, expected action `move`
                             pinned again at tests/test_napoleon_np1_hand.py:407
'we will decide next turn'   corpus id `fa6-we-will-decide-next-turn-is-not-a-command`
```

Driven end to end (`p4_regression.py`), the damage is a whole feature family —
**NP-1, "the Emperor's Hand"** — not one row:

```
'I will march to Lorraine'  HEAD  ap 4->3, Napoleon moves   "Napoleon begins march to Lorraine. (1 AP - the Emperor commands in his own name.)"
                            FIX   (nothing)                 "Berthier sets down his pen. I cannot answer that from the dispatches, Sire."
'I will attack Mack'        HEAD  ap 4->3, gold 800->534, 5 corps   MUSTER - Napoleon (10,000; 112,324 if all march...)
                            FIX   (nothing)                 the same shrug
'we will hold Lorraine'     HEAD  "Which marshal shall hold Lorraine, Sire?"   (the CR-2 clarification)
                            FIX   the same shrug
```

Mechanism: skipping the leading `I` exposes `will` as a **modal lead**, and the
modal arm exempts only the *second* person (`_SECOND_PERSON_AFTER_LEAD_RE`), so
every `I will <verb>` becomes a question. The finder listed this option first.

### Option (ii), "the interrogative word anywhere", which the finder calls low-risk — is not

0 flips against the 619 game-produced sentences — which is exactly the trap,
because the corpus contains none of the shapes at risk. Against 33 hand-built
ordinary sentences (`p7_safe_fix.py`) it flips **6**, including a dialogue
answer, where `A_QUESTION_NEVER_ANSWERS` makes a false question **fail closed**:

```
B-FLIP  'Ney, attack Mack and tell Davout why'
B-FLIP  'hold the line, no matter who comes'
B-FLIP  'attack Mack, whose corps is weakest'
B-FLIP  'Ney, hold - who knows what Mack does next'
B-FLIP  'Davout, take Swabia, I do not care how about the cost'
B-FLIP  'refuse - who do they think they are'        <- a dialogue answer
```

### The shape that does work

Arms (a)/(b) only, after a bounded run of leading tokens separated by
**whitespace** (never a comma), never re-running the lead machinery — so it
cannot expose a modal lead, which is what killed option (i):

```
^\s*(?:[A-Za-z][\w'-]*\s+){0,3}(?:why|who|whom|whose|(?:what|how)\s+about|
                                  is\s+it\s+(?:time|wise|worth|…)|(?:what|how)\s+say)\b
```

Measured: **0 flips of 449 corpus rows · 0 flips of the 33 adversarial
sentences · closes 12 of 12** (the eight filed plus the four I found).
Build the pins on `tell me why not retreat` and `I wonder why not retreat`
first — they are the cases that carry a first person the guard never reaches —
and keep `I will march to Lorraine`, `I will attack Mack` and `attack Mack,
whose corps is weakest` as the controls.

---

## 6. Severity: **P2 holds**

Up-arguments: free, destructive, unconfirmed, 0 AP, 2,270 men, seven of eight
reachable, and the worst openers are the most question-like English has.
Down-arguments: it is **not a regression**, it is not a soft-lock and it is not
an irreversible priced answer given on someone else's behalf; row CX left it
strictly better than it found it; and the most destructive verb is accidentally
shielded against 18 of 27 unlisted openers. P2, at the top of the band.

## 7. What the finder got right

The cause, stated precisely at the guard; the eight cases, every one; the two
controls; `shipped_by_this_row: false`; and the closing observation that every
finding in this family is a comma or a boundary. The corrections are the width,
one case's reachability, and the fact that **the prescription — either of them
— is the dangerous part.**
