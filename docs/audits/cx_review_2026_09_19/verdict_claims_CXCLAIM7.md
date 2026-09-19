# VERDICT: CX-CLAIM-7 — **CONFIRMED (narrowed in characterisation, strengthened in evidence)**

**Tree:** master `727cf88a` + `f52df77f`, clean. Memo figure introduced in `704df816` (row CX).
**Probes:** `probes/p_verdict7.py`, `probes/p_verdict7b.py` — both run under `.venv/Scripts/python.exe`,
`LLM_MODE=mock`, on the shipped 1805 scenario board (`europe_1805.json`, 22 marshals, player France).

---

## 1. The reproduction I ran (not the one I was given)

### 1a. The counts

`probes/p_verdict7.py` walks `commanded_full40.json` and reports string **leaves** (values),
object **keys**, and the commands as the *driver* reads them (`doc["turns"]` values):

```
string LEAVES (values) in the file : 166
object KEYS in the file            : 48
leaves under /turns (commands)     : 160
leaves NOT under /turns (metadata) : 6
turn keys                          : 40
unique command strings             : 51

the six metadata leaves:
   /name                  commanded-full40
   /seed                  historical
   /llm                   mock
   /_note_d6              FA-S17-D6 (Phase 4, September 12 2026): the COMMANDED arm. E...
   /policy/objection      trust
   /policy/diplomacy      accept
```

Every number the claim asserts reproduces exactly, including the identity of all six
metadata strings. **166 = 160 + 6.**

### 1b. The substantive proposition, through the REAL predicate

The claim asserted the substance survives but re-implemented the test. I ran the production
predicate instead — `backend/ai/clause_guards.is_question(text, roster)`, the CX-1 function
itself, with the live 22-name 1805 roster:

```
over the 160 commands : 0
over all 166 leaves   : 0
```

and the addressee comma, over the 160:

```
commands whose head word is a marshal : 129
of those, WITHOUT a comma             : 0
commands whose head word is NOT a marshal: 31   (18 × "status", 13 × "recruit ... with <name>")
```

Belt and braces: the file contains **0 `?` characters anywhere**, including inside `_note_d6`.

**So the memo's sentence is LITERALLY TRUE as written.** The file does hold 166 strings, and
0 of those 166 are question-shaped or omit an addressee comma. The conclusion it supports —
*"the committed harness structurally cannot reach anything this row changed"* — holds under
**either** denominator. Nothing measured by this row is affected.

---

## 2. Attacking the claim

### 2a. Is it internally inconsistent? — NARROWED

The claim says the document is *"internally inconsistent by 6."* That over-characterises.
Section 4's `0 / 160` measures **escalation rate**, a property only a *parsed command* can
have; section 6b's 166 counts **strings in a file**. Two populations, two properties — not a
contradiction. The precise charge is weaker and different: **166 is a lone outlier against the
memo's own convention.**

### 2b. …and that outlier status is MEASURABLE — this strengthens the finding

`probes/p_verdict7b.py` counts leaves and commands for all 32 committed scripts. Every other
figure in the same ruling table is command-based:

| memo figure | leaves | **commands** | memo cites |
|---|---|---|---|
| `commanded_full40.json` | **166** | **160** | **166** ← the outlier |
| `commanded_spender40.json` | 180 | **173** | **173** ✓ |
| "the 1,416 committed playtest commands" | 1,685 | 1,456 | **1,416** ✓ |

The sibling arm in the *same table row* is quoted at 173 where its file holds 180 leaves — so
the author's unit was commands. And 1,416 reconciles exactly: 1,456 total commands today minus
the **40** in `typed_road.json`, which `git log` shows row CX itself added in `704df816`
("the arm that can see the typed road"). The memo is rigorously command-based in three places
and leaf-based in one.

### 2c. The number is PINNED, not merely preferred

`tests/test_fa_s17_phase4c_2026_09_12.py::TestTheCommandedArmExists`:

```python
assert sum(counts.values()) == 160, sum(counts.values())
```

Verified passing (`6 passed in 0.34s`). The project's committed canonical count for this exact
file is **160**. The memo quotes 166 against a green pin.

### 2d. Severity — P4 is right, and should not be downgraded to INFO

Harm ceiling is low: doc-only, no pin reads the memo (`grep CX_THE_HAND_ON_THE_KEYBOARD
tests/ tools/` → **no hits**), the game is untouched, the conclusion survives. But it is a
reproducible wrong denominator in the row's **authoritative record**, and this project has an
explicit recurring scar for exactly this — `PR-D4`, *"a documented table does not reproduce"*.
A future session computing this arm's escalation rate as *x*/166 publishes a wrong figure.
**P4 holds.**

### 2e. Player-reachable — NO

Trivially false. A figure in an audit memo. No client path, no API path, no popup route.
`main.gd`'s 114-form diplomatic redirect is irrelevant here.

### 2f. Shipped by row CX — YES

`git show 704df816:docs/audits/...` carries **both** figures (`0 / 160` at line 251 and
`166 strings` at line 382) in the same commit. `commanded_full40.json` itself is
**pre-existing** — last touched by `4094eb4a` (FA slice 17 Phase 4, Sept 12) — so the *file*
is not row CX's; the *sentence* is.

### 2g. Would the fix ship a regression? — NO

The fix is one word: `**166 strings**` → `**160 commands**`. No test reads the memo. No pin
cites 166. The sentence's proposition is true at 160 (measured above, through the production
predicate), so the edit strictly *tightens* a true claim. **No pin reds; no sentence breaks.**

⚠ One caution for whoever edits it: do **not** also "fix" 173 or 1,416 to match leaf counts —
those two are already correct as commands, and 1,416 is deliberately the *pre-row* total.

---

## 3. What the claim itself got wrong

1. *"internally inconsistent by 6"* — over-stated; the two figures measure different
   populations for different properties. The real charge is that 166 is a unit outlier.
2. It verified the substance with its own re-implementation of "question-shaped"; I ran
   `clause_guards.is_question` with the live roster instead, which is the stronger check and
   returns 0 over **both** 160 and 166.
3. It did not find the two facts that make the finding stand up: the **sibling 173/180**
   contrast in the same table, and the **committed `== 160` pin**.
4. It did not check whether the conflation spread. It does not — 1,416 and 173 are both clean.

---

## 4. Verdict line

**CONFIRMED · P4 · not player-reachable · shipped by row CX (`704df816`) · fix is a one-word
doc edit that reds nothing.** The sentence is true but quotes the wrong unit, against the
memo's own convention and against a green committed pin.
