# VERDICT: CXR1-1 — **CONFIRMED** at P2, shipped by row CX

**Refuter pass, default verdict REFUTED.** Everything below was measured by a
probe I wrote and ran myself, on the shipped 1805 board, through
`POST /command`, on a **fresh world per utterance**. I did not run the lens's
probes. `LLM_MODE=mock`, no network call, nothing under `backend/`,
`godot-client/`, `tests/`, `docs/` or `tools/` was edited and no git command
mutated anything.

My probes: `probes/refute_CXR11/` —
`h.py` (my own harness), `p1_repro.py`, `p2_prerow.py` (**a tree I extracted
myself with `git archive b4a27a15^`**, not a lever flip),
`p3_effect_sweep.py` + `p3_out.json`, `p4_fixprobe.py`, `p5_fixharm.py`,
`p6_variantB_drive.py`, `p7_severity.py`, `p8_dialogue.py`,
`cxfix_plugin.py`.

---

## 1. Does it reproduce, exactly as stated? — **YES**

`p1_repro.py`, fresh board per line:

```
'Ney, attack Mack?'   AP4->3 gold800->509 battle=True  moved=[Davout,Lannes,Napoleon,Ney]
                      bled={Ney:2112, Davout:1942, Lannes:1344, Napoleon:746}
'Ney attack Mack?'    AP4->4 gold800->800 battle=False moved=[] bled={}
                      'Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."'
'Ney attack Mack'     AP4->3 gold800->511 battle=True  moved=[Davout,Lannes,Napoleon,Ney]
```

The middle line is the defect and the two either side are the controls: half
two works (no comma, no `?` → Ney fights), the comma'd hesitant order works,
and the comma-free hesitant order is swallowed. Same for `Ney retreat?`,
`Ney fortify?`, `Ney scout Swabia?`, `Ney move to Swabia?`,
`Marshal Ney attack Mack?`, `Davout bombard Mack?`.

The mechanism is as filed: `clause_guards._ADDRESSED_LINE_RE` is
`^\s*(?:HONORIFIC)?[A-Za-z][\w'’-]*\s*[,:]` — the comma or colon is
**mandatory** — and arm (e) at `clause_guards.py:720-723` returns True for any
`?`-terminated line it does not match. **Nowhere in `clause_guards.py`, the
spec §3.1 arm (e) text, or `tests/test_cx1_a_question_never_orders.py` is the
comma requirement stated as deliberate**, while the second half of the same
commit is titled *"AN ADDRESS NEEDS NO COMMA"* and exists because a player does
not type the comma. The lens's framing — the row arguing with itself — holds.

## 2. Did row CX ship it? — **YES, and I checked the tree, not the lever**

A lever flip is not the pre-row game. `p2_prerow.py` runs the identical case
set against a tree I extracted with `git archive b4a27a15^` (neither
`A_QUESTION_NEVER_ORDERS` nor `AN_ADDRESS_NEEDS_NO_COMMA` exists in it):

```
PRE-ROW  'Ney attack Mack?'     AP4->3 gold800->503 battle=True moved=[Davout,Lannes,Napoleon,Ney]
PRE-ROW  'Ney retreat?'         Ney retreats from Rhineland to Lorraine
PRE-ROW  'Ney scout Swabia?'    Ney scouts Swabia: ... Mack (Austria): ~52,000 troops
PRE-ROW  'Ney move to Swabia?'  "Cannot move into Swabia - enemy forces present!..."
```

Pre-row these were carried out **by the marshal the player named**. This is a
regression, not an inherited gap.

## 3. Is the SEVERITY right? — **P2 confirmed. Not P1, not P3.**

### The reach, measured on EFFECT rather than on verdict

⚠ **The filed 456/456 is a count of `is_question` VERDICTS that flipped, not
of orders destroyed**, and it overstates the effect reach. `p3_effect_sweep.py`
runs 272 utterances (8 player marshals × 16 order verbs × {comma, no comma},
plus 16 unaddressed) on BOTH trees and joins on the text:

| family | n | pre acted, post inert | both acted | both inert |
|---|---|---|---|---|
| **comma-free, addressed** | 128 | **86** | 0 | 42 |
| **comma'd (the control)** | 128 | **0** | 86 | 42 |
| unaddressed bare order + `?` | 16 | 4 | 0 | 12 |

An exact mirror: the comma is the whole difference and **86 of 128 ordinary
orders are destroyed by its absence**. The 42 were already inert on both trees
(a marshal out of range), so they were never the defect's to lose.

Of the 86 (`p7_severity.py`): **58 changed real state** — AP spent, corps
moved, battles fought, scouts run, stances shifted (`Ney attack Mack?` used to
cost 1 AP and 319 gold and fight; `Napoleon march to Lorraine?` cost 1 AP and
moved the Emperor; `Soult scout Swabia?` bought intelligence) — and **28 raised
a marshal's objection**, a decision point, and now raise nothing.

### What keeps it off P1

Measured, not assumed:

* **Zero cost.** AP 4→4, gold 800→800, no marshal moves, no strength changes,
  on every one of the 86. Fully recoverable by retyping without the `?`.
* **It does not eat a pending dialogue** (`p8_dialogue.py`). With Ney's
  objection live, `Soult attack Mack?` leaves `world.pending_objection` set and
  `proceed` still answers *"Ney awaits your answer, Sire."* FA slice 6's class
  does not fire here.

### What keeps it off P3 — and one correction that makes it WORSE than filed

⚠ **The lens's own reproduction implies a mitigation that does not exist.** It
reads the shrug as *"the desk suggests, with a comma, the very sentence just
typed."* That is a **coincidence of the counsel's top pick, not a mechanism**:
`counsel.py` prints `Ney, attack Mack` / `Ney, march to Lorraine` *whatever was
typed*. Measured in `p1_repro.py`, `Davout bombard Mack?` is answered with an
offer about **Ney**, and `Ney fortify?` adds *"What you want is in the Strategic
Ledger's Economy tab (press T, then 3)"* while `Marshal Ney attack Mack?` adds
*"What you want is in the Generals screen (press G)"* — both wrong surfaces for
the order that was given. So the player is told, confidently, that an order was
a question, and pointed somewhere unrelated.

P2 is right: a wide, reachable, silent refusal of ordinary orders on the road
this row's own §2 ruling calls *"the road that wins the turn"*, with nothing
spent and nothing corrupted.

## 4. Player-reachable? — **YES, verified in the client, and under BYOK too**

`main.gd::_execute_command` (1614) → `_redirect_diplomatic_command` (2007).
The redirect's **second** test is `_is_advisory_question` (2055), whose first
line is `if lower.ends_with("?"): return true` — so the redirect returns
**false** and the raw string goes to `api_client.send_command` untouched. I read
the whole send path from 1614 to 1688: the only other gates are the redemption
tokens and `_is_end_turn_phrasing`. **There is no `?` handling anywhere on it.**

Also reachable with a key: the question branches return `confidence=0.9`
(`llm_client.py:1810`) and `0.8` (`1824`), both above
`LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7` (`llm_client.py:63`, gate at `1049`),
so the fast parser never escalates and `--llm anthropic` swallows it
identically.

## 5. Would the suggested fix ship a regression? — **Option one: no. Option two: yes, and it is the wrong roster.**

The lens offered two. They do not behave the same and the report does not say
so.

**Option two (the one it calls "cheaper") is the worse one.** "Pass
`is_question` the roster it already takes" means `_question_subjects`, which is
*deliberately* wide — player marshals **plus every enemy commander plus all 126
province names** (147 entries at boot). `p4_fixprobe.py` / `p5_fixharm.py`: it
fixes `Ney attack Mack?` and moves 0 of 449 corpus rows, but it also
un-questions `Mack attack Ney?`, `Kutuzov retreat?` and `Swabia hold?`. Driven,
the two enemy lines are harmless (the enemy-name arm answers identically either
way) — but the rule is keyed on the wrong list and would bind a province as an
addressee.

**Option one — its first suggestion, "compose the executor's own comma-free
addressee rule" — is clean, and I built and ran it** (`cxfix_plugin.py`
VariantB: a comma/colon, OR an order verb with a non-empty head before it that
contains no `_NOT_AN_ADDRESS_RE` function word or collective; roster-free, so
the wide list cannot poison it):

* fixes all six defect lines end to end — `Ney attack Mack?` fights,
  `Ney march to Lorraine?` marches (`p6_variantB_drive.py`);
* keeps **every** arm-(e) and CX-1 control: `retreat?`, `attack?`,
  `why not attack Mack`, `who holds Swabia`, `is Swabia defended`,
  `can Ney attack Mack`, `what about attack Mack`, `where is Mack?`,
  `end turn?`, `do attack Mack?`, `can you attack Mack?`,
  `all marshals attack?` — all unchanged;
* **moves 0 of the 449 golden-corpus rows**;
* **445/445 green** across `test_cx1_a_question_never_orders.py`,
  `test_cx2_berthier_answers_the_board.py`, `test_cx3_the_predictor.py`,
  `test_parse_negation.py` and
  `test_fa_slice7_the_mock_speaks_plainly_2026_09_04.py`, identical to baseline.

Its only side effect is that a PROVINCE-led order (`Vienna attack Mack?`) is
now refused as an unknown addressee — *"There is no 'Vienna' in the order of
battle, Sire. Whom did you intend?"* — which is half two's own designed
refusal, and better than the shrug it replaces.

**So: no pin is redded and no sentence is broken. I could not make the fix
fail.** Whatever is built, pin the pair `Ney, attack Mack?` / `Ney attack
Mack?` together, and pin `retreat?` beside them, or the two halves can diverge
again.

---

## Found in passing — NOT my finding, but the review should know

`tests/test_cx1_a_question_never_orders.py::TestTheRetreatIsSometimesANoun::test_the_lever`
**FAILS** when run as
`pytest tests/test_cx1_a_question_never_orders.py tests/test_parse_negation.py`,
reproducibly and with `-p no:randomly`:

```
AssertionError: ('lever off = the defect reproduces',
 "Lannes respectfully raises concerns: 'Retreat? We can still fight!'")
```

It passes alone, and passes in a five-file run. It is cross-file state
pollution (Lannes objects instead of retreating), so the pin is
order-dependent rather than a production defect — but a lever pin that is green
only in some orders is not binding.

## Corrections to the filed row

1. `456/456` counts verdict flips, not destroyed orders. The effect reach is
   **86 of 128**, of which **58** changed real state.
2. *"the desk suggests, with a comma, the very sentence just typed"* is
   accidental — the counsel prints the same two Ney lines whatever was typed.
   The finding is slightly worse than filed, not better.
3. The two suggested fixes are not equivalent; the roster option is keyed on a
   deliberately-wide list and the roster-free option is the one that measures
   clean.
