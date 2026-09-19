# VERDICT: CXR1-3 — PRE-EXISTING

## PRE-EXISTING — real, and WIDER than filed; but its stated cause explains only 7 of its own 10 cases, and its suggested fix ships a measured regression that 279 guard pins and 688 corpus rows are all green about

**Tree:** master `727cf88a` (docs-only `f52df77f` on top), clean.
**Parser:** mock throughout. No key, no network.
**Probes (mine, all run):**
`probes/repro_negint.py` · `probes/cause_split.py` · `probes/prerow_negint.py` ·
`probes/fix_regression.py` · `probes/fix_regression2.py` ·
`probes/breadth_and_confidence.py` · `probes/confidence.py` ·
`probes/raw_response.py` · `probes/cxr13fix_plugin.py`
**Harness:** the row's own — `build_world("1805")` installed as the
`world` / `game_state` / `parser` triple into `backend.main`, a **fresh board
per utterance**, driven at `POST /command`. My footprint adds `fortified`,
`stance` and `strategic_order` to the row's (location, strength) pair; the
first cut of my own fix-probe was **blind to a fortify** and would have
reported the headline regression below as "no change". Corrected in
`fix_regression2.py`.

---

## 1. It reproduces. 10 of 10.

`probes/repro_negint.py`, fresh 1805 board per utterance, `POST /command`:

```
utterance                                    AP      gold      battle  moved
couldn't we attack Mack                     4->3   800->533   True    Davout,Lannes,Napoleon,Ney,Soult
wouldn't it be better to attack Mack        4->3   800->520   True    Davout,Lannes,Murat,Napoleon,Ney,Soult
wouldn't we do better to retreat            4->4   800->800   False   ALL EIGHT CORPS
haven't we enough men to attack Mack        4->3   800->509   True    Davout,Lannes,Murat,Napoleon,Soult
oughtn't we attack Mack                     4->3   800->535   True    Lannes,Murat,Napoleon,Soult
ought we to attack Mack                     4->3   800->537   True    Bernadotte,Davout,Lannes,Murat,Napoleon,Ney,Soult
mightn't we attack Mack                     4->3   800->522   True    Davout,Lannes,Murat,Napoleon,Soult
weren't we going to attack Mack             4->3   800->500   True    Davout,Lannes,Murat,Napoleon,Soult
hasn't Ney attacked Mack                    4->3   800->525   True    Davout,Lannes,Murat,Napoleon,Ney
hadn't we better attack Mack                4->3   800->555   True    Davout,Lannes,Murat,Napoleon,Ney,Soult
```

The `wouldn't we do better to retreat` row spends no AP because a general
retreat is **free by design** (FA-R3) — the finder's "GENERAL RETREAT — all 8
corps fell back" is exactly right and its AP column would have been wrong.

**There is no confirmation of any kind between the musing and the battle.**
`probes/raw_response.py` reads the raw response for `couldn't we attack Mack`:

```
AP: 3   battle_report: True
LIVE gate keys: NONE — nothing to answer
casualty_summary: Soult 30,000 -> 28,754 (1,246 dead)
                  Mack  52,000 -> 36,392 (15,608 dead)
```

And the sentence one apostrophe away, on the same board, in the same probe:

```
'could we attack Mack'   AP: 4   battle_report: False
    "Were you to give the order, Sire:
     MUSTER — Ney (24,000; 78,676 if all march …)"
```

**The positive form gets CX's preview. The negative form gets the battle.**
That pair is the finding in one line, and it is the strongest thing in the row.

---

## 2. PRE-EXISTING — measured, not inferred. Row CX shipped none of it, and improved the neighbourhood.

The finder asserted "not a CX regression" from `is_question` alone. That is
necessary but not sufficient: CX-1 half two (`AN_ADDRESS_NEEDS_NO_COMMA`),
CX-5 and CX-6 all sit downstream of the guard and could have changed the
outcome. So I ran the tree.

`git archive b4a27a15^` (read-only) into the scratchpad, same harness, same
seed — `probes/prerow_negint.py`:

```
PRE-ROW tree at: …/scratchpad/cx_review/prerow/backend
couldn't we attack Mack                 4->3   800->547   battle=True
wouldn't it be better to attack Mack    4->3   800->517   battle=True
wouldn't we do better to retreat        4->4   800->800   ALL EIGHT CORPS
haven't we enough men to attack Mack    4->3   800->494   battle=True
oughtn't we attack Mack                 4->3   800->536   battle=True
ought we to attack Mack                 4->3   800->501   battle=True
mightn't we attack Mack                 4->3   800->504   battle=True
weren't we going to attack Mack         4->3   800->534   battle=True
hasn't Ney attacked Mack                4->3   800->473   battle=True
hadn't we better attack Mack            4->3   800->538   battle=True
```

All ten fought before row CX, identically. **`shipped_by_this_row: false` is
correct.** And the same probe shows row CX made this neighbourhood *better*:

| utterance | pre-row `b4a27a15^` | HEAD |
|---|---|---|
| `couldn't we attack Mack?` | **battle**, AP 4→3 | **inert** (CX-1 arm (e)) |
| `has Ney attacked Mack` | **battle**, AP 4→3 | **inert** (CX-1 arm (c)) |

`probes/cause_split.py` also confirms `is_question` is `False` for all ten
under **both** lever positions and with `MODAL_LEADS_ARE_QUESTIONS` down too.

---

## 3. The stated CAUSE is wrong for 3 of the finding's own 10 cases, and the title over-reaches its body

The finder names one mechanism — `_INTERROGATIVE_LEAD_SRC` ends the lead group
with `\b`, and `n` is a word character. I tested that against every one of its
own cases by pairing each with its **positive sibling**
(`probes/cause_split.py`, and driven in `probes/repro_negint.py`):

| the finder's case | positive sibling | sibling `is_question` | real cause |
|---|---|---|---|
| couldn't we … | could we … | **True** (inert) | ✅ the `\b` |
| wouldn't it be better … | would it be better … | **True** | ✅ the `\b` |
| wouldn't we do better … | would we do better … | **True** | ✅ the `\b` |
| mightn't we … | might we … | **True** | ✅ the `\b` |
| weren't we going … | were we going … | **True** (inert) | ✅ the `\b` |
| hasn't Ney attacked … | has Ney attacked … | **True** (inert) | ✅ the `\b` |
| hadn't we better … | had we better … | **True** (inert) | ✅ the `\b` |
| **haven't we enough men …** | **have we enough men …** | **False — BATTLE** | ❌ `have` is **deliberately excluded** from the lead set (documented: *"have Ney attack Mack"* is the causative imperative) |
| **oughtn't we …** | **ought we …** | **False — BATTLE** | ❌ `ought` is **not a lead at all**, in either polarity |
| **ought we to attack Mack** | — | — | ❌ a **positive, uncontracted** sentence filed as evidence for a contraction bug |

So the headline — *"the negative-interrogative contraction is invisible to the
lead regex"* — is true of seven cases and false of three, one of which carries
no contraction at all. Three distinct causes, presented as one.

This is not pedantry: **the finder's own suggested fix closes only 7 of its own
10** (§5).

---

## 4. It is WIDER than filed, and the "tell" is exactly right

`probes/breadth_and_confidence.py`, 38 interrogative openers scored against the
two guards that could stop them, then driven:

```
UNGUARDED (seen by NEITHER is_question NOR the negation marker): 14 of 38
  couldn't we · wouldn't we · wasn't it · weren't we · hasn't he · haven't we
  hadn't we · mightn't we · oughtn't we · mayn't we · ain't we
  ought we to · ought we · have we

28 of 28 unguarded (opener × verb) cases MOVED THE BOARD
  … × "attack Mack"  → battle=True, AP 4→3, every time
  … × "retreat"      → all eight corps fall back, every time
```

Beyond the finder's list and measured by me: **`wasn't Ney ordered to attack
Mack` → battle, AP 4→3** (and `was` *is* a documented never-imperative lead, so
this is the arm-(c) case one apostrophe out of reach), plus `mayn't`, `ain't`,
`ought we`, `have we`. Orthography does not save you either: **`couldn’t`
(curly apostrophe) and `couldnt` (no apostrophe) both fought.**

The finder's "tell" reproduces exactly. I enumerated `_NEGATION_MARKER_RE`
directly:

```
markers:     shouldn't can't isn't aren't don't didn't won't mustn't shan't doesn't
NOT markers: couldn't wouldn't haven't hasn't hadn't weren't wasn't oughtn't mightn't
```

Whether a negative-interrogative is inert depends on which contractions
PARSE-NEG happened to enumerate for prohibitions. That is the real indictment
and it stands.

---

## 5. ⛔ THE SUGGESTED FIX SHIPS A REGRESSION, and no committed pin can see it

I applied the finder's fix **exactly as written** — append `(?:n['’]t)?` before
the boundary — recompiled both lead regexes, and re-drove everything
(`probes/fix_regression.py`, `probes/fix_regression2.py`,
`probes/cxr13fix_plugin.py`).

**(a) It closes 7 of the 10.** `haven't we enough men`, `oughtn't we` and
`ought we to` still fight — because their leads are *missing from the set*, not
hidden behind a boundary. The "two characters, not a new arm" framing does not
close the finding's own list.

**(b) It destroys PARSE-NEG's surviving order.** `is_question` is the **OUTER
gate** at `llm_client.py:1519` — a sentence it calls a question is exempt from
`strip_negated_clauses`, `strip_condition_clauses` **and**
`strip_deferred_clauses`. Widening the lead to swallow `n't` makes any
prohibition carrying a first-person token (`our`, `we`, `my`, `us` — all in
`_FIRST_PERSON_RE`) a "question", so the rule *remove the negation and re-read
what is left* stops running. Measured, full footprint:

```
"Davout, don't advance on our left, fortify"
  HEAD   ap 4→2 · Davout: fortified=True, Stance.DEFENSIVE at Rhineland
         "[Auto-shifted to DEFENSIVE stance first — cost 2 AP] Davout fortifies…"
  FIXED  ap 4→4 · nothing changed
         Berthier: "I cannot answer that from the dispatches, Sire."

"Ney, don't advance on our position, fortify"
  HEAD   ap 4→2 · Ney: fortified=True, Stance.DEFENSIVE
  FIXED  ap 4→4 · nothing changed — shrug

"Ney, don't attack Mack, hold our position"
  HEAD   ap 4→2 · Ney: strategic_order = HOLD
  FIXED  ap 4→4 · nothing changed — shrug
```

The one-word swap to `on your left` is **inert under both arms** — so a pin
written on the tidy phrasing proves nothing, which is this row's own recorded
lesson one layer out.

**(c) It reds no pin.** Under the patch, via a scratchpad pytest plugin:

```
tests/test_parse_negation.py
tests/test_cx1_a_question_never_orders.py
tests/test_cx2_berthier_answers_the_board.py     →  279 passed

golden corpus, HEAD           688/688
golden corpus, SUGGESTED FIX  688/688
```

**279 guard pins and 688 corpus rows are green about a fix that silently drops
a fortify order the player typed.** Nothing pins a prohibition-plus-surviving-
order carrying a first-person possessive.

---

## 6. Severity P1 is RIGHT. Player-reachable: YES.

**P1 is consistent with this row's own precedent** — CX-1's headline
`why not attack Mack` is the identical shape (a musing that fights), was filed
P1 and was built. The act is irreversible, uncconfirmed, spends an AP and costs
1,246 men on the measured run.

**Player-reachable through the shipped client: YES, verbatim.**
`main.gd::_execute_command` (1614) intercepts exactly three things before
`api_client.send_command`: `_is_end_turn_phrasing`, the three bare underscore
redemption tokens, and `_redirect_diplomatic_command`. The redirect fires only
on `DIPLO_*` keyword lists (all diplomatic: *declare war on*, *break treaty*,
*ultimatum to*, *request terms*, …) or on `_is_advisory_question`, which is
`lower.ends_with("?")` plus a first-word allowlist. None of these sentences
matches. The shipped launcher defaults to **mock**, so for most players the
fast parser is the only parser.

**The finder's "no escalation rescue" conclusion is right but its mechanism is
wrong.** It cites the *question route's* 0.8/0.9 at `llm_client.py:1810,1824` —
but for these sentences `is_question` is False and the question route is never
taken. Measured `fast_parse` confidence (`probes/confidence.py`, gate 0.7):

```
couldn't we attack Mack              action=attack   conf=0.8   no escalation
wouldn't we do better to retreat     action=retreat  conf=0.8   no escalation
oughtn't we attack Mack              action=attack   conf=0.8   no escalation
hasn't Ney attacked Mack             action=attack   conf=0.9   no escalation
wasn't Ney ordered to attack Mack    action=attack   conf=0.9   no escalation
```

It is the **attack parse's own action-verb confidence** that clears the gate.
Right answer, wrong route.

---

## 7. One correction to ROW CX's own record, measured rather than argued

The landing record (`COMMAND_EXPERIENCE_SPEC.md` §3.1) says:

> 684 cases, 121 executing before … and 9 after — every one of the nine a
> control, and **zero defects left**.

I read the committed grid,
`docs/audits/cx_recon_2026_09_19/sweep_both_arms_measurement.txt`:

```
grep -ci "n't"                     →  0
grep -ciE "'(ought|have) "         →  0
```

**All 684 cases are positive, uncontracted interrogative leads.** "Zero defects
left" is true of that grid and false of the family it generalises to. The claim
should be scoped to the grid — that is a record fix, not a code fix, and it is
the only thing here row CX is answerable for.

---

## 8. What I would build instead

1. **Do not widen `is_question`.** The outer-gate exemption is what makes that
   dangerous, and the danger is invisible to the suite.
2. **Add the nine missing contractions to `_NEGATION_MARKER_RE`** — the
   mechanism that *already* makes `shouldn't we attack Mack` and `can't we
   attack Mack` inert, for nine contractions, today. One line, no new arm, the
   outer exemption untouched, and it cannot drop a surviving order because
   `strip_negated_clauses` is exactly the thing that recovers one. The cost is
   voice only: a musing is answered in the prohibition register — the same
   wrong-but-inert voice `shouldn't we attack Mack` already gets, so it adds no
   new class of wrongness. Route the register properly in CR-6 with the rest of
   the conversational layer.
3. **Separately: `ought` belongs in the lead set**, and the `have` exclusion
   should be narrowed to the causative shape (`have <marshal> <verb>`) —
   `have we …` is never causative. Neither is a contraction problem and neither
   is closed by the finder's fix.
4. **Build the pin on `Davout, don't advance on our left, fortify` FIRST** —
   comma-free where it can be, apostrophe-carrying, first-person — and add the
   tidy `on your left` form as the control, never the other way round.
