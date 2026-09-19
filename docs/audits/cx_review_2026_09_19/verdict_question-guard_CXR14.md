# VERDICT:CXR1-4 — NARROWED (and PRE-EXISTING)

**Lens 1 (`question-guard`) filed it as P2, player-reachable, not shipped by row CX.
Default verdict was REFUTED. It is not refuted — but it is not what its title says
either, and the difference changes the fix.**

Tree: master `727cf88a` (HEAD has since moved to `f52df77f`, which touches no
`backend/` or `godot-client/` path — `git show --stat f52df77f -- backend/ godot-client/`
is empty, so every measurement below is against production code as committed at
`727cf88a`). `LLM_MODE=mock`, network guard installed, no API call made, nothing
under the repo was written.

My probes (mine, not the filed ones) are under `…/scratchpad/cx_review/probes/`:
`refute_harness.py`, `r1_headlines.py`, `r2_prerow.py`, `r3_client_gate.py`,
`r4_framing.py`, `r5_decompose.py`, `r6_fix_regression.py`,
`r7_sweep_and_answers.py`, `r8_confidence.py`, with `out_r*.txt` beside them.
The pre-row tree is a read-only `git archive b4a27a15^` export at
`…/scratchpad/cx_review/prerow/`.

---

## 1. Does it reproduce? YES — 8 of 8, verbatim (`r1_headlines.py`, `out_r1.txt`)

Fresh shipped-1805 board per utterance, driven through `POST /command`:

```
EXECUTED 'maybe defend'                           AP 4->3   "All forces take defensive positions: Ney, Davout, Soult, …"
EXECUTED 'maybe build a depot in Paris'           adm 2->1, gold 800->500
EXECUTED 'perhaps build ships'                    adm 2->1, gold 800->400
EXECUTED 'maybe we should build a depot in Paris' adm 2->1, gold 800->500
EXECUTED 'perhaps we should release Holland'      DP 5->4, vassal released
EXECUTED 'worth attacking Mack'                   AP 4->3, gold 800->526, battle=True, 5 corps moved
EXECUTED 'any reason not to attack Mack'          AP 4->3, gold 800->543, battle=True, 6 corps moved
EXECUTED 'find out whether we can attack Mack'    AP 4->3, gold 800->522, battle=True, 5 corps moved
```

Arm (b)'s four allowlisted forms are inert on the same board, as the row claims.

**Independent reach measurement** (`r7`): 15 hedge openers × 10 orders, each on a
fresh board = **107 EXECUTED of 150**. Every opener I tried fires on 6–9 of 10.
I did not reproduce the filed "100 of 484" — different sampling — so treat the
filed denominator as uncited and mine as the citable one.

---

## 2. Attribution: PRE-EXISTING, and proven with a positive control (`r2_prerow.py`)

The same eight, run against a `git archive b4a27a15^` export (`out_r2_prerow.txt`)
vs the shipped tree (`out_r2_shipped.txt`):

| utterance | pre-row | shipped |
|---|---|---|
| all eight CXR1-4 headlines | **8 of 8 EXECUTED** | **8 of 8 EXECUTED** |
| `what about attack Mack` | EXECUTED (battle, 5 corps) | inert |
| `how about retreat` | EXECUTED (all 8 corps fell back) | inert |
| `is it time to build a depot in Paris` | EXECUTED (adm + 300g) | inert |

The arm-(b) controls are the positive control: they prove the export really is
pre-row. The eight are unchanged across it. **Row CX did not introduce this**
(`shipped_by_this_row: false` — correct).

---

## 3. Player-reachable: YES, verified against the shipped client (`r3_client_gate.py`)

I reimplemented `main.gd::_redirect_diplomatic_command` and `_is_end_turn_phrasing`
**parsing the keyword lists out of `main.gd` itself** (115 `DIPLO_FAMILY_KEYWORDS`,
18 `DIPLO_NO_HOME_KEYWORDS`, 2 war-room, 7 `DIPLO_ADVISORY_STARTS`), never
transcribing them. Sanity: `declare war on Austria` → CABINET, `propose peace with
Prussia` → CABINET. Result:

```
all eight -> SENT to backend
```

`release` is not a Cabinet family keyword (`autonomy` is; `release` is not), so the
vassal release goes over the wire. `_execute_command` has exactly three gates above
`api_client.send_command` — the end-turn phrasing gate, the underscore redemption
tokens, and the Cabinet door — and none claims any of the eight.

---

## 4. ⚠ THE TITLE IS WRONG, AND THE FIX CHANGES BECAUSE OF IT (`r4_framing.py`)

> *"Arm (b) is an allowlist of three musings, and the fourth spends the gold."*

Arm (b) is never reached by any of the eight. `is_question` returns at
`clause_guards.py:727-728` —

```python
lead = _lead_re.match(text)
if not text or not lead:
    return False
```

— **before** `_DELIBERATIVE_OPENER_RE` is consulted at line 746. Measured, per
sentence:

```
'maybe defend'                        lead=None  arm_b_match=False  is_question=False
'maybe build a depot in Paris'        lead=None  arm_b_match=False  is_question=False
'perhaps build ships'                 lead=None  arm_b_match=False  is_question=False
'maybe we should build a depot…'      lead=None  arm_b_match=False  is_question=False
'perhaps we should release Holland'   lead=None  arm_b_match=False  is_question=False
'worth attacking Mack'                lead=None  arm_b_match=False  is_question=False
'any reason not to attack Mack'       lead=None  arm_b_match=False  is_question=False
'find out whether we can attack Mack' lead=None  arm_b_match=False  is_question=False
--- for contrast, the forms arm (b) really does cover ---
'is it worth attacking Mack'          lead='is'  arm_b_match=True   is_question=True
'what about building a depot in Paris' lead='what' arm_b_match=True is_question=True
```

The correct statement is one layer up: **`is_question` requires an interrogative
LEAD before any arm runs, and a hedge is not a lead.** This is not an allowlist
corner of arm (b); it is the gate above every arm.

**Why that matters:** a hedge arm cannot be a wider `_DELIBERATIVE_OPENER_RE`. It
has to sit **above** the lead gate — structurally exactly where arm (e) sits — and
arm (e) is where this same review round's CXR1-1 found a regression. The fix
session must be told it is adding a second arm above the gate, not widening a list
behind it.

### The sharpest evidence is missing from the filed row

Arm (b) *literally enumerates* `is it time to` and `is it worth`. Drop the
two-word matrix and it is defeated:

```
'is it time to build a depot in Paris'   inert
'time to build a depot in Paris'         EXECUTED  (adm 2->1, 300 gold)
'is it worth attacking Mack'             inert
'worth attacking Mack'                   EXECUTED  (AP 4->3, a real battle)
'is there any reason not to attack Mack' inert
'any reason not to attack Mack'          EXECUTED  (AP 4->3, a real battle)
```

That pairing is the row's strongest case and it is not in the report. ⚠ It is also
**not uniform** — `worth building a depot in Paris` is inert while
`worth attacking Mack` fights — which is the same "the family behaves at random"
tell the lens correctly identified in CXR1-3.

---

## 5. One of the eight is a different family (`r5_decompose.py`)

Decomposition — strip the hedge and re-drive — shows the hedge is **decorative in
all eight**: the sentence underneath is a plain order the game executes anyway.
Good; that is the row's substance and it holds. But two members need re-homing:

**`find out whether we can attack Mack` is not a musing.**

```
'find out whether we can attack Mack'  EXECUTED  battle=True
'whether we can attack Mack'           EXECUTED  battle=True
'we can attack Mack'                   EXECUTED  battle=True
'find out whether Mack is strong'      inert
'find out about Mack'                  inert
'find out where Mack is'               inert
```

Neither `find out` nor `whether` is doing anything. The executing shape is the bare
declarative **`we can attack Mack`** — a statement of capability, an uncovered
family of its own. Counting it as a musing inflates the row by one **and hides a
wider hole**: the underlying problem is larger than filed, not smaller.

**Two sub-explanations in the filed row are wrong.** It says `maybe we should attack
Mack` and `I wonder if we should attack Mack` are inert "only because a bare `attack
Mack` with no marshal named hits CR-6's bare-attack clarification". Measured:

```
'maybe we should attack Mack'        -> "I do not find 'should' in the order of battle, Sire. Did you mean Soult?"
'I wonder if we should attack Mack'  -> "Sire, that is a contingency, not an order — I have no way to hold a dispatch until the enemy moves."
```

The first is a fuzzy **marshal-name** failure on the word `should`; the second is
the **conditional** guard firing on `if`. Neither is CR-6. The row's conclusion
("the same sentence with a buildable verb spends the gold") survives, but for
neither of the reasons given — and that matters, because a fix session that
believed the CR-6 story would expect those two to start executing once a marshal is
named, and they will not.

---

## 6. Severity: P2 stands, but the row's own evidence UNDERSTATES it

The filed line for the vassal case reads `'perhaps we should release Holland' DP 5->4`.
The actual response (`r4_framing.py`, full message captured):

> Holland is released from vassalage and stands a free court again. Their tribute of
> **337 gold a turn** ends. They will no longer answer France's call to arms. Europe's
> alarm at France eases (**70 → 62**). **They cannot be brought back under the yoke for
> 5 turns.** Freed, they take up a design of their own: The Seventeen Provinces. Should
> they see it through they would proclaim United Netherlands — 0 of 1 province held.

A musing performs a strategically decisive act that is **explicitly irreversible for
5 turns** and wakes a dormant formation deck. `perhaps build ships` spends **400 of
the boot purse's 800 gold**. So the severity is under-stated by its own footprint
column, not over-stated.

I still hold it at **P2, at the top of the band**: no corps and no province is lost,
and `perhaps build ships` / `maybe defend` are survivable. It is not a P1 because
nothing here is unrecoverable in the way a lost corps is.

**Recorded, not filed as part of this row:** bare `release Holland` executes
identically (`r5`), so the hedge is not bypassing a confirmation — **`release_vassal`
has no confirmation at all**. That is its own item and does not belong to the
question guard.

---

## 7. ⚠ THE PROPOSED FIX: safe where the row looked, and the row looked in the wrong place (`r6`, `r7`)

Filed fix: *"a hedge token at position 0, or `wonder|whether|worth|reason|point`
before the verb."* I implemented it literally and ran it over everything:

| surface | claimed by the proposed fix |
|---|---|
| golden corpus, 449 utterances | **0** |
| sentences the game itself offers (counsel + tutorial `suggest` chips + region-panel chips), 28 | **0** |
| hand-written natural orders carrying `point` / `reason` / `worth` / `whether` | **0** (they all sit *after* the verb, so the "before the verb" scan never sees them) |
| the eight it was written for | 8 of 8 |

So on the surfaces the row considered, it is low-risk. **But `is_question` has four
production readers and the row names only one.** Two of them are the
DIALOGUE-ANSWER predicate — `dialogue_routing.line_asks_a_question`, read at
`dialogue_routing.py:451`, `dialogue_routing.py:1134` and
`diplomatic_executor.py:3859`, behind `A_QUESTION_NEVER_ANSWERS`. With the hedge arm
bolted on (`r7`, measured through the real predicate):

```
'maybe accept'               today=False  with-fix=True   <-- stops answering
'perhaps accept'             today=False  with-fix=True   <-- stops answering
'maybe we should accept'     today=False  with-fix=True   <-- stops answering
'perhaps we should accept'   today=False  with-fix=True   <-- stops answering
'possibly accept'            today=False  with-fix=True   <-- stops answering
'maybe decline'              today=False  with-fix=True   <-- stops answering
'worth accepting'            today=False  with-fix=True   <-- stops answering
'any reason to accept'       today=False  with-fix=True   <-- stops answering
--- controls, unchanged ---
'accept' / 'accept their terms' / 'yes' / 'decline'   False -> False
```

**8 of 8 hedged dialogue answers flip.** That is arguably *right* under IQ-7's
fail-closed rule — an irreversible priced answer should not be signed on a musing —
but it is a behaviour change on an unrelated surface, on the exact family IQ-7's
review round spent four passes on, and it must be decided consciously rather than
discovered. Name it on the row.

**And the corpus cannot pin any of this, in either direction.** Measured: of the 449
corpus utterances, **0** contain `maybe`, `perhaps`, `possibly`, `worth`,
`any reason`, `any point`, `wonder`, `whether`, `thoughts on` or `find out`. The
corpus is structurally blind to the whole family, so it can validate neither the
defect nor the fix. Every pin here has to be a behaviour pin driven through
`POST /command` — which is what the lens's own closing method note asks for, and it
is right.

---

## 8. One measurement the row does not carry, and the fix session needs it (`r8_confidence.py`)

All eight land **above** the 0.7 escalation gate, so no LLM in any mode is ever
consulted and no key could ever correct them:

```
'maybe defend'                        action='defend'          conf=0.8
'maybe build a depot in Paris'        action='build'           conf=0.9
'perhaps build ships'                 action='build_fleet'     conf=0.8
'maybe we should build a depot…'      action='build'           conf=0.9
'perhaps we should release Holland'   action='release_vassal'  conf=0.9
'worth attacking Mack'                action='attack'          conf=0.9
'any reason not to attack Mack'       action='attack'          conf=0.9
'find out whether we can attack Mack' action='attack'          conf=0.9
```

Same shape CX-5's own commit message names for the retreat family. This must be
caught deterministically; routing it to the LLM is not an option that exists.

---

## VERDICT

**NARROWED, and PRE-EXISTING. Severity P2 held; player-reachable confirmed.**

Survives: the symptom (8 of 8, verbatim), player reachability (verified against the
shipped client's own parsed keyword lists), the attribution (`shipped_by_this_row:
false`, proven with a pre-row export and a positive control), and the shape of the
fix (name the hedge, do not enumerate openers).

Re-stated: it is **not arm (b)** — it is the interrogative-lead gate above every
arm, so the fix is a new arm above that gate and carries arm (e)'s hazard class,
not an allowlist widening. One of the eight (`find out whether we can attack Mack`)
is a bare declarative `we can attack Mack` and belongs to a wider uncovered family.
Two of the row's sub-explanations (the CR-6 story for both "inert" cases) are wrong
on measurement. The severity evidence understates the vassal release, which is
explicitly irreversible for five turns. And the proposed fix's real blast radius is
the dialogue-answer predicate — 8 of 8 hedged answers stop answering — a surface the
row never names, on a family the golden corpus cannot see at all.
