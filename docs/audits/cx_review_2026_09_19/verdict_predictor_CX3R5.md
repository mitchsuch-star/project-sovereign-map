# VERDICT: CX3-R5 — **NARROWED to P4, and PRE-EXISTING in its behaviour half**

Filed by lens `predictor` as P3, player-reachable, shipped by row CX.
Re-measured at `master 727cf88a` (clean) with my own probes, on the shipped
1805 board, `LLM_MODE=mock` pinned before every backend import plus a
non-loopback socket guard. Probes:
`scratchpad/cx_review/probes/r5/r5_{a..j}*.py`.

**Verdict in one line: the observation is true and I reproduced it exactly,
but three of the four things the row builds on top of it do not hold — the
exemption hides nothing (measured), the behaviour is eight months old
(measured on the pre-row tree), and the filed fix is RED ON LANDING
(measured).** What survives is a smaller and sharper defect than the title,
and I found a second instance the filed scan missed.

---

## 1. Does it reproduce? **YES, exactly as stated.**

`probes/r5/r5_b_detail.py` — real `CommandParser(use_real_llm=False)` on
`build_world("1805")`:

```
'Bravest of the Brave'           success=False  action=None
'Child of Victory'               success=False  action=None
'Eyes on a Crown'                success=False  action=None
'First Horseman of Europe'       success=False  action=None
'Iron Resolve'                   success=False  action=None
'Roland of the Army'             success=False  action=None
'Drillmaster of Boulogne'        success=True   action='drill'   conf=0.8
    full command dict: {"marshal": null, "action": "drill", "target": null,
                        "confidence": 0.8, "type": "specific",
                        "raw_command": "Drillmaster of Boulogne",
                        "mode": "mock", "key_source": "none"}
```

And through the REAL endpoint (`POST /command`, fresh 1805 board):

```
  state = "awaiting_clarification"     clarification_kind = "marshal_choice"
  message = "Which marshal shall carry out this order, Sire?"
  options = [{"label":"Ney","command":"Ney, Drillmaster of Boulogne"},
             {"label":"Davout","command":"Davout, Drillmaster of Boulogne"}, …]
```

The mechanism is `backend/ai/llm_client.py:2261`:

```python
elif "drill" in command_lower or "train" in command_lower or "exercise" in command_lower:
    action = "drill"
```

— a bare substring, firing on `drill` inside `Drillmaster`. The row's reading
of the mechanism is correct.

### The consequence is slightly WORSE than filed, and I say so

The filed row stops at the clarification. I drove it to the end
(`r5_d_full_chain.py`, `r5_e_terminal.py`) and the ability-name route is
**byte-for-byte the honest verb route**:

```
A: 'Drillmaster of Boulogne' -> 'Murat' -> 'insist'
   "Murat firmly objects…"  then  "You insist on the original order. Murat
   complies reluctantly. (Trust -13 in all — -10 for the order pressed home…)"

B: CONTROL 'Murat, drill' -> 'insist'
   "Murat firmly objects…"  then  the identical -13 trust charge.
```

So it is a live order, not a dead-end: answer the clarification with a marshal
name and you are in the real drill pipeline, objection and all. That does not
rescue the severity (see §3), but the row understates it and the row's own
`reproduction` should have carried it.

---

## 2. ⛔ The load-bearing claim is FALSE: **the exemption hides nothing.**

This is the one I went after hardest, because it is what turns an inaccuracy
into a defect. The row's framing is that the allowlist *exempts* — i.e. that
removing the row would expose something.

`probes/r5/r5_f_exemption_hides.py` runs **both** real census pins
(`test_every_quoted_phrasing_the_manual_teaches_is_typable` and
`test_every_quoted_phrasing_survives_the_EXECUTOR`) with each member removed
in turn, over the 50 quoted strings the help body actually contains:

```
BASELINE (all 7 exempt): 50 quoted strings — 0 parse failures, 0 executor failures

remove 'Bravest of the Brave'      LOAD-BEARING — new parse failure
remove 'Child of Victory'          LOAD-BEARING — new parse failure + executor failure
remove 'Drillmaster of Boulogne'   INERT — removing it changes NOTHING
remove 'Eyes on a Crown'           LOAD-BEARING — new parse failure
remove 'First Horseman of Europe'  LOAD-BEARING — new parse failure
remove 'Iron Resolve'              LOAD-BEARING — new parse failure + executor failure
remove 'Roland of the Army'        LOAD-BEARING — new parse failure
```

`Drillmaster of Boulogne` is the **only** member of the seven whose exemption
is inert. The census is green on it with the exemption and green without it —
because the parse census fails only on strings that *fail* to parse, and the
executor census fails only on the refusal needles, and a clarification carries
none.

So the harm is **not** concealment. The defect that survives is narrower and
I would state it this way:

> The allowlist's comment asserts something false about one of its seven
> rows, and that row is dead weight.

Which is a P4 accuracy defect in a test, not a P3.

### The sharper defect the row did not name

Three lines above the set (`tests/test_cx3_the_predictor.py:236`):

```python
# Quoted strings in the help body that are NOT commands, each with the
# reason it is exempt. An allowlist, so a NEW non-command string fails
# the census until somebody says what it is.
NOT_COMMANDS = {
    "Bravest of the Brave", "Child of Victory", "Eyes on a Crown",
    "First Horseman of Europe", "Iron Resolve", "Roland of the Army",
    "Drillmaster of Boulogne",
}
```

**"each with the reason it is exempt" — and not one reason is written.** That
is the real hole, and it is the thing that would have caught the Drillmaster
row: writing the reason forces you to look. The row files the symptom and
misses the cause sitting in the same three lines.

---

## 3. Severity: **over-stated. P3 → P4.**

* The filed subject is a **test allowlist**. It is not shipped to anyone.
* Its inaccuracy changes **no test outcome**, measured seven ways (§2).
* The census's own stated rule — *"the game must not offer a sentence it
  cannot read"* — is **not violated** by this string. The manual prints
  `Soult "Drillmaster of Boulogne" - sharpens his corps in a day` in a
  `YOUR MARSHALS` roster block: it is a **display label beside a name**, not
  a sentence the manual teaches. The parser reading it as *something* is a
  false positive, not a broken promise.
* The behaviour half needs a player to type a display label as an order **and
  then** answer a clarification with a marshal name. Berthier's shrug is
  replaced by a question. That is a blemish, not a trap.

---

## 4. Player-reachable? **The behaviour half yes; the filed subject no.**

* The filed subject (a `NOT_COMMANDS` set in a pytest file) is not reachable
  by anybody.
* The behaviour is reachable. I checked the client redirect the brief names:
  `main.gd:2007 _redirect_diplomatic_command` is **fail-open** and scoped to
  `DIPLO_*_KEYWORDS` verb heads (*"a sentence that does not clearly match a
  family head goes to the backend exactly as before"*). `Drillmaster of
  Boulogne` matches no family head, so it reaches `/command` verbatim.
* ⚠ **The CX-3 completer can never offer it.** `main.gd:6882 _MARSHAL_VERBS`
  and `:6897 _BARE_COMMANDS` are the only proposal sources, and neither
  contains an ability name. So the predictor does not propose the string —
  this is not the predictor teaching an unreadable sentence.

---

## 5. Shipped by row CX? **The mislabel yes. The defect no — PRE-EXISTING by eight months.**

`probes/r5/r5_g_preexisting.py`, run against the committed pre-row tree
`scratchpad/cx_review/tree_f7008582` (= `b4a27a15^`, verified pre-CX: no
`tests/test_cx3_the_predictor.py`, no `A_RETREAT_CAN_BE_A_NOUN`):

```
TREE = …/tree_f7008582
  parse('Drillmaster of Boulogne') -> success=True action='drill' conf=0.8
  help body prints the quoted ability name ? True
  POST /command -> success=True state='awaiting_clarification'
     msg='Which marshal shall carry out this order, Sire?'
```

Identical, before a line of row CX was written. And the keyword itself:

```
$ git log -1 -S'"drill" in command_lower or "train" in command_lower' -- backend/ai/llm_client.py
17bb8776 2026-01-16 fix: Code review fixes for disobedience system and tactical actions
```

So CX-3 shipped the *label* ("this is not a command") on a string that had
been read as a command since January. `shipped_by_this_row` is half true and
the row states it as whole.

---

## 6. ⛔ **The filed fix is RED ON LANDING.**

The row says: *"one line in the existing test — every `NOT_COMMANDS` member
must ALSO fail to parse as an action. It turns the allowlist from an assertion
into a proof."*

`probes/r5/r5_j_fix_cost.py` evaluates that exact predicate through the same
real parser the test uses:

```
=== FIX A: 'every NOT_COMMANDS member must ALSO fail to parse' ===
  members that would RED the new assertion TODAY: [('Drillmaster of Boulogne', 'drill')]
  => the filed fix is RED on landing
```

It does not turn the allowlist into a proof. It turns
`tests/test_cx3_the_predictor.py` red — today, on the shipped board — and
there are only two ways to green it:

**(a) delete the Drillmaster row.** Safe: §2 measured it INERT, so the census
stays green with 6 members. This is the fix I would take, *together with*
writing the six missing reasons the comment already promises.

**(b) close it at the parser.** ⛔ **This does not work in the shape the row
implies, and the row should have checked.** CX-5's precedent is a *determiner*
rule ("retreat after a determiner is a noun"), and it does not transfer:
`Drillmaster` is a compound noun, not a verb after a determiner. The only
available lever is a word boundary, and I measured both variants:

```
sentence                                     today  \b..\b  \bstem\w*
'Soult, drill'                                True    True     True
'Soult, drills'                               True   False     True
'Soult, start drilling'                       True   False     True
'Soult, begin training'                       True   False     True
'Soult, start training the recruits'          True   False     True
'Soult, retrain the corps'                    True   False    False
'Soult, exercises'                            True   False     True
'Soult, put the men through their exercises'  True   False     True
'Drillmaster of Boulogne'                     True   False     True   <<<
'Strained'                                    True   False    False
```

The stem variant `\b(drill|train|exercis)\w*` — the only one that keeps the
real vocabulary — **still matches `drillmaster`**, because `Drillmaster`
begins at a word boundary. It closes nothing. The strict `\bword\b` variant
does close it, and the sentences it breaks are these, all of which parse
correctly today:

> `Soult, drills` · `Soult, start drilling` · `Soult, begin drilling the
> corps` · `Soult, begin training` · `Soult, start training the recruits` ·
> `Soult, exercises` · `Soult, put the men through their exercises`

So the parser route costs seven live phrasings to remove one false positive.
**It should not be built**, and I would put that on the row rather than leave
a future session to discover it.

### Rider, found while measuring: a pinned corpus row is safe by ORDERING ONLY

`tests/data/parser_golden_corpus.json` pins
`{"id": "restrain-murat", "utterance": "restrain Murat", "expected": {"action": "restrain"}}`
— and `restrain` **contains `train`**. It survives only because
`llm_client.py:2259` checks `restrain` on the line immediately above the drill
branch:

```python
elif "restrain" in command_lower:
    action = "restrain"
elif "drill" in command_lower or "train" in command_lower or "exercise" in command_lower:
```

Measured: `restrain Murat` → `action='restrain'` today. Move those two
branches and the corpus row inverts. Not a defect now; a named fragility, and
one more reason not to touch this predicate casually.

---

## 7. ⚠ The row's scoping claim is TOO NARROW — I found a second instance

The row states: *"I scanned every name the game prints — 126 provinces + 8
marshals + 4 visible enemies + the 7 ability names … `Drillmaster of Boulogne`
is the ONLY one."*

Two corrections, both measured.

**(i) The board has ELEVEN ability names, not seven** (the seven are the
French ones the help body quotes). `probes/r5/r5_i_abilities.py` ran all
eleven; the conclusion happens to survive:

```
'Habsburg Resolve'   success=False   'Shorncliffe System' success=False
'The Old Fox'        success=False   'The Presence'       success=False
'Drillmaster of Boulogne'  success=True  action='drill'  <== the only hit
```

**(ii) But the class is wider than "names", and there is a second member.**
Scanning the Generals card's own printed strings turned up:

```
'Strained'  -> action='drill'  conf=0.8
```

`Strained` is a **trust-tier label** printed to the player at
`backend/models/trust.py:64` (the marshal card's `trust_label`,
`backend/main.py:4560`) and at `backend/game_logic/war_status.py:362`. It is a
one-word label — exactly the kind of short printed string a player might type
— and it fires the same `train` substring. The other four tiers are clean:

```
'Broken' / 'Loyal' / 'Reliable' / 'Questioning'  ->  success=False
```

`Strained` is outside the census's domain (not a quoted string in the help
body) and outside the row's stated scan scope, and it is pre-existing on the
same January keyword. It is not a reason to raise this row; it is a reason not
to trust its "only one" as a closed census.

Also measured, offered without explanation because I did not chase it:
`'drillmaster of boulogne'` → `drill`, but `'DRILLMASTER OF BOULOGNE'` →
`success=False`. The behaviour is not even consistent across casing.

---

## 8. What I would actually do

P4, and worth taking only because it is three lines:

1. **Delete `"Drillmaster of Boulogne"` from `NOT_COMMANDS`** (measured INERT
   — the census stays green at 6 members).
2. **Write the six reasons the comment already promises**, one per row, as a
   dict rather than a set. That is the change that makes the next one
   impossible, and it is the one the row missed.
3. **Do not** add the filed assertion as written (red on landing), and **do
   not** word-boundary the drill keywords (seven live phrasings lost).
4. Record `Strained` and the `restrain`-by-ordering fragility as pre-existing
   observations against the parser's bare-substring family, not against row CX.

Suite state confirmed: `tests/test_cx3_the_predictor.py` — **17 passed** at
`727cf88a`.
