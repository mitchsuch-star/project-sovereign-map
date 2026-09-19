# LENS 1 — ATTACK THE QUESTION GUARD (CX-1, `clause_guards.is_question`)

Review round on row CX at master `727cf88a`. Every claim below was reproduced
by a probe that was actually run on the **shipped 1805 board** through
`POST /command`, on a fresh world per utterance, using the row's own harness
shape (`parser_eval.build_world("1805")` + `TestClient(main.app)` with the
world/game_state/parser triple swapped). `LLM_MODE=mock`; no network call was
made. Probes are committed under
`…/scratchpad/cx_review/probes/` (`harness.py`, `sweep_a_orders.py`,
`sweep_b_leverdiff.py`, `sweep_c_questions_exec.py`, `sweep_e_covered_leads.py`,
`sweep_f_dialogue.py`, `sweep_i_reach_and_roster.py`, `repro_headlines.py`,
`probe_g_live_dialogue.py`, `probe_h_comma_free_address.py`, `probe_j_tail.py`,
`probe_k_2x2.py`), with their raw outputs beside them.

**Headline: there is another one, and it is the row arguing with itself.**
CX-1 landed two halves in one commit. Half two says *an address needs no
comma*. Arm (e) of half one decides "addressed" with a regex that **requires**
a comma. The result is that the row's own documented control — `Ney, attack
Mack?` *is a hesitant order* — holds with the comma and inverts without it.
**456 of 456** (honorific × marshal × verb) comma-free hesitant orders flip;
**0 of 456** comma'd ones do. Nothing in the suite pins the comma-free form,
and the control pin the builder wrote uses the comma in all five of its rows.

---

## ⚠ Tree-state note (not a finding, but read it)

The task states the tree is clean at `727cf88a`. It was when this session
started; **midway through it, eight paths appeared STAGED in the index** and
have since been committed by another agent as **`f52df77f` "docs(cx): correct
the row's own headline figure — it understated its fix by 4x"** (it rewrites
the memo's "30 executing → 9" to "121 → 9" and edits
`tests/test_cx1_a_question_never_orders.py`, `docs/BUG_FIXES.md`,
`docs/STATUS.md` and two new `tools/` files). I touched none of it, and I
mutated no git state.

**`git show --stat f52df77f -- backend/ godot-client/` is empty**, and
`backend/` was unmodified in the working tree throughout, so **every
measurement below is against production code exactly as committed at
`727cf88a`** and is unaffected. Two consequences for whoever reads this next:
`tests/test_cx1_a_question_never_orders.py` moved under this review, so
re-read the control pin before writing new ones; and HEAD is now `f52df77f`,
not `727cf88a`.

---

# FINDINGS

## CXR1-1 — P2 — REGRESSION SHIPPED BY CX-1: an order without a comma that ends in `?` is swallowed as a question

**The row's own documented rule, from `clause_guards.py:687-695` and spec §
CX-1 arm (e):**

> an **unaddressed** line ending in `?` is a question. An addressed one keeps
> its order: `Ney, attack Mack?` is a hesitant order and has been documented
> as one since FA slice 7.

`_ADDRESSED_LINE_RE` is `^\s*(?:HONORIFIC)?[A-Za-z][\w'’-]*\s*[,:]` — a comma
or a colon is **mandatory**. Half two of the very same commit exists because a
player does not type the comma.

### Reproduction (`probe_h_comma_free_address.py`, `out_h.txt`)

Fresh 1805 board per utterance:

```
'Ney, attack Mack?'   is_question=False   AP 4→3, battle=True, moved=[Davout,Lannes,Napoleon,Ney]
                      "MUSTER — Ney (24,000 …) vs Mack (large force) at Swabia …"

'Ney attack Mack?'    is_question=True    AP 4→4, battle=False, moved=[]      ← ORDER SWALLOWED
                      Berthier sets down his pen. "I cannot answer that from the
                      dispatches, Sire."   What I CAN do today:
                        Ney, attack Mack          ← the desk suggests the sentence just typed
                        Ney, march to Lorraine
```

Nine pairs measured, all nine flip. Same result for `Ney retreat?`,
`Ney scout Swabia?`, `Ney move to Swabia?`, `Ney fortify?`,
`Marshal Ney attack Mack?`, `General Ney attack Mack?`,
`Davout bombard Mack?`, `Murat charge Mack?`. Case, double spaces and a space
before the `?` change nothing (`NEY ATTACK MACK?`, `Ney  attack Mack?`,
`Ney attack Mack ?` all swallowed — `probe_j_tail.py`); `Ney, attack Mack ?`
(comma kept) still fights.

### Attribution — clean 2×2 over CX-1's own two levers (`probe_k_2x2.py`)

| | `A_QUESTION_NEVER_ORDERS` | `AN_ADDRESS_NEEDS_NO_COMMA` | `Ney attack Mack?` |
|---|---|---|---|
| shipped | 1 | 1 | **inert — desk shrug** |
| | 1 | 0 | inert — desk shrug |
| | 0 | 1 | AP 4→3, battle |
| | 0 | 0 | AP 4→3, battle |

`A_QUESTION_NEVER_ORDERS` alone causes it. It is a regression this row
shipped, not an inherited gap.

### Measured reach (`sweep_i_reach_and_roster.py`, `out_i.txt`)

3 honorific forms × 8 player marshals × 19 order verbs × {comma, no comma} =
912 cases.

* **WITHOUT the comma, the verdict flipped by CX: 456 / 456.**
* **WITH the comma, flipped: 0 / 456.**

### Why the suite is green about it

`tests/test_cx1_a_question_never_orders.py::TestTheOrdersThatMustStillMarch`
parametrizes five controls and **every one carries the comma**
(`"Ney, attack Mack"`, `"Ney, attack Mack?"`, …). Grepping the whole of
`tests/` for `Ney attack Mack?` returns only `will Ney attack Mack?` (a
different rule). The comma is the one clause the builder held constant.

### Player-reachable: YES

`main.gd::_send_command` → `_redirect_diplomatic_command` returns **false** for
this line (it ends in `?`, so `_is_advisory_question` short-circuits the
redirect, and it carries no Cabinet keyword), so the raw string reaches
`POST /command`. There is no `?` special case anywhere on the send path.
It is also unreachable-by-LLM: the question branch returns
`confidence=0.8/0.9` (`llm_client.py:1810, 1824`), above the 0.7 escalation
gate, so `--llm anthropic` swallows it identically — the original PARSE-NEG
shape, one rule over.

### Suggested fix

Make the two halves read the same definition of "addressed". Either compose
the executor's own comma-free addressee rule into `_ADDRESSED_LINE_RE`, or —
cheaper and testable in one place — pass `is_question` the roster it already
takes and treat a **leading roster name followed by an order verb** as an
address whether or not a comma follows. Pin the pair
(`Ney, attack Mack?` / `Ney attack Mack?`) together so they can never diverge
again.

---

## CXR1-2 — P2 — CX-1's trailing-clause stand-down is defeated by a trailing **vocative**, and the row's own flagship controls then execute

Arms (c) and (d) stand down whenever `_TRAILING_CLAUSE_RE` (`,\s*\S`) matches
the text after the lead, with this reasoning at the site:

> `"Ney, should Mack advance, fortify"` means `"if Mack advances, fortify"` …
> A question of this shape does not carry a trailing main clause.

A **vocative** is not a main clause, and a tag question is not a main clause.
Both are commas. Both disarm the arm.

### Reproduction (`repro_headlines.py` / `probe_j_tail.py`)

```
'can Ney attack Mack'            is_question=True    inert                 ← the row's control
'can Ney attack Mack, Berthier'  is_question=False   AP 4→3 gold 800→521 battle=True
'can Ney attack Mack, sire'      is_question=False   AP 4→3 gold 800→526 battle=True
'may Ney attack Mack, Berthier'  is_question=False   AP 4→3 gold 800→517 battle=True
'can Ney attack Mack, do you think'  is_question=False  AP 4→3 gold 800→516 battle=True
'can Ney attack Mack, or should Davout'  is_question=False AP 4→3 gold 800→524 battle=True
'has Ney attacked Mack, Berthier'    is_question=False  AP 4→3 gold 800→501 battle=True

'is Swabia defended'             is_question=True    inert                 ← the row's control
'is Swabia defended, Berthier'   is_question=False   AP 4→3
                                 "All forces take defensive positions: Ney, Davout, Soult,
                                  Lannes, Murat, Bernadotte, Massena, Napoleon"
'is Swabia defended, and is Vienna'  is_question=False  AP 4→3, whole-army defend
'is Swabia defended, Napoleon'   is_question=False   AP 4→3, Napoleon → DEFENSIVE stance
'does Ney hold Rhineland, Berthier'  is_question=False  **AP 4→2**, a standing HOLD order created
```

`is Swabia defended` is the row's own published headline case — *"a whole-army
DEFEND, 1 AP spent … which no roster of commanders could have reached"*. Add
the chief of staff's name after a comma and it spends the AP again.

### Why the builder's grid could not see it

The arm is **masked whenever the question happens to contain a first-person
word**, because `_FIRST_PERSON_RE` is tested before the stand-down. Measured:
`did we attack Mack, Berthier` and `are we at war with Prussia, Berthier` and
`is Swabia defended, I wonder` are all correctly inert — for that unrelated
reason. The builder's own examples are studded with `we` and `I`, so a grid
built from them shows the hole as closed.

### Player-reachable: YES

No Cabinet keyword, no `?`, straight through to `POST /command`. Addressing
Berthier by name after a comma is this game's own register (`Berthier, status`
is a shipped, pinned road).

### Suggested fix

Narrow the stand-down to what it was written for: a trailing clause that
**contains a verb** (an inverted conditional always does; a vocative and a tag
never do), or scope it to the ADDRESSED form, which is the shape of the pinned
case `Ney, should Mack advance, fortify`. Keep
`test_an_inverted_conditional_is_refused_not_answered` green, and add the
vocative twin of each control beside it.

---

## CXR1-3 — P1 — the negative-interrogative contraction is invisible to the lead regex, and it fights a real battle

`_INTERROGATIVE_LEAD_SRC` ends each lead with `\b`. In `couldn't`, the
character after `could` is `n`, so there is no boundary and **no lead
matches at all** — the whole of `is_question` is skipped, and the keyword
chain reads the imperative inside the question. This is the single most
idiomatic English way to propose something tentatively.

### Reproduction (`repro_headlines.py`, `repro_headlines.txt`)

```
"couldn't we attack Mack"             AP 4→3  gold 800→508  battle=True
                                      moved=[Davout, Lannes, Murat, Napoleon, Soult]
"wouldn't it be better to attack Mack"  AP 4→3  gold 800→547  battle=True
"wouldn't we do better to retreat"    GENERAL RETREAT — all 8 corps fell back
"haven't we enough men to attack Mack"  AP 4→3  gold 800→532  battle=True
"oughtn't we attack Mack"             AP 4→3  gold 800→549  battle=True
"ought we to attack Mack"             AP 4→3  gold 800→543  battle=True
"mightn't we attack Mack"             AP 4→3  gold 800→469  battle=True
"weren't we going to attack Mack"     AP 4→3  gold 800→551  battle=True
"hasn't Ney attacked Mack"            AP 4→3  gold 800→510  battle=True
"hadn't we better attack Mack"        AP 4→3  gold 800→538  battle=True
```

(Gold deltas vary with the combat rolls; the AP spend, the corps movement and
`battle=True` do not.) The same lines executed across every verb tail tried —
34 hits in the `tense` arm of `sweep_c_questions_exec.py` alone.

### The family behaves at random, which is the tell

`shouldn't we attack Mack` and `can't we attack Mack` are **inert** — but not
because `is_question` caught them. `should\s*n[o']t` and `ca\s*n[o']t` happen
to be entries in `_NEGATION_MARKER_RE`, so those sentences are blanked as
*prohibitions*. `couldn't`, `wouldn't`, `haven't`, `hasn't`, `hadn't`,
`weren't`, `oughtn't`, `mightn't` are not in that list, so they fall through
and fight. **Whether a negative-interrogative is safe currently depends on
which contractions PARSE-NEG happened to enumerate for a different purpose.**

### Player-reachable: YES. Not a CX regression (`is_question` returns False under both lever positions) — but it is squarely inside CX-1's contract: *"a question never orders."*

### Suggested fix

Two characters, not a new arm: allow the lead to be followed by an
apostrophe-`n't` before the boundary (e.g. append `(?:n['’]t)?` to the lead
group, or run the match against a copy with `n't` → ` not`). Note the
interaction — once the lead matches, `couldn't we` hits the first-person arm
and is a question immediately — and re-check that
`shouldn't we attack Mack` still refuses rather than executing.

---

## CXR1-4 — P2 — arm (b) is an allowlist of three musings, and the fourth spends the gold

Arm (b) was added precisely because *"they are the way a person MUSES — the
single most natural thing to type at a war table — and every one of them
committed the deed."* It closed that with `what about`, `how about`,
`is it time to`, `what say`. The rest of the musing vocabulary still commits
the deed. This is the shape CX-5's own commit message names: *"a guard that
understood its failure mode exactly and closed it with an allowlist."*

### Reproduction (`repro_headlines.py`; 100 hits in the `musing` arm of `sweep_c_questions_exec.py`, of 484 probed)

```
'maybe defend'                          AP 4→3   whole-army defensive positions
'maybe build a depot in Paris'          admin 2→1, gold 800→500  "Construction started: Supply Depot in Paris"
'perhaps build ships'                   admin 2→1, gold 800→400  "A keel is laid at Bordelais (400g)"
'maybe we should build a depot in Paris'  admin 2→1, gold 800→500
'perhaps we should release Holland'     DP 5→4
'worth attacking Mack'                  AP 4→3  gold 800→521  battle=True
'any reason not to attack Mack'         AP 4→3  gold 800→504  battle=True   ← contains the word "not"
'find out whether we can attack Mack'   AP 4→3  gold 800→542  battle=True
```

`any reason not to attack Mack` is worth its own line: the player writes the
word *not* and the army attacks. `_NEGATION_MARKER_RE` deliberately excludes a
bare `not`, and `not to attack` matches none of its phrases.

`maybe we should attack Mack` and `I wonder if we should attack Mack` are
inert — but only because a bare `attack Mack` with no marshal named hits CR-6's
bare-attack clarification, which spends nothing. The same sentence with a
buildable verb spends the gold.

### Player-reachable: YES (no Cabinet keyword; `maybe`/`perhaps`/`worth`/`find` are not in `DIPLO_ADVISORY_STARTS`). Not a regression; an uncovered part of the row's own family.

### Suggested fix

Stop enumerating openers. The common shape is **a hedge word or a hedged
matrix clause in front of an order verb** — `maybe`, `perhaps`, `possibly`,
`worth`, `any reason`, `any point`, `I wonder`, `find out whether`,
`thoughts on`. A single "hedged lead" arm (hedge token at position 0, or
`wonder|whether|worth|reason|point` before the verb) covers the measured set;
whatever is chosen, pin the four measured non-allowlist openers as behaviour,
not as strings in a list.

---

## CXR1-5 — P2 — arms (a) and (b) are anchored at `^` behind a five-word filler list, and one unlisted filler re-opens them

The lead regex tolerates exactly `so |and |but |ok/okay|well` before the
lead, plus one comma-terminated address. Any other filler word, without a
comma, means no lead matches and nothing in `is_question` runs.

### Reproduction (43 hits in the `filler` arm of `sweep_c_questions_exec.py`)

```
'hmm why not defend'               AP 4→3  whole-army defensive positions
'uh why not defend'                AP 4→3
'hey why not build ships'          admin 2→1, gold 800→400
'right why not build a depot in Paris'   admin 2→1, gold 800→500
'actually what about build ships'  admin 2→1, gold 800→400
'honestly what about defend'       AP 4→3
'anyway what about release Holland'  DP 5→4
'just wondering why not retreat'   GENERAL RETREAT — all 8 corps fell back
```

Controls, same board: `hmm, why not defend` (one comma — the filler is eaten
as an address) and `so why not defend` (a listed filler) are both **inert**.
One keystroke decides whether the army retreats.

`just wondering why not retreat` is the row's own published flagship
(`why not retreat` → *"a GENERAL RETREAT: all eight corps fell back"*) with
two words in front of it.

### Player-reachable: YES. Not a regression; the same allowlist shape as CXR1-4.

### Suggested fix

Either skip a leading run of non-verb filler tokens before looking for the
lead (bounded — two or three tokens), or anchor arms (a)/(b) on the
interrogative word **anywhere before the first order verb** rather than at
`^`. Arms (a) and (b) are already the two that need no extra signal, so
widening their anchor is low-risk; pin `hmm why not retreat` and
`just wondering why not retreat` against `why not retreat`.

---

## CXR1-6 — P3 — a question now pre-empts an open envoy letter and the refusal never mentions it

`A_QUESTION_NEVER_ANSWERS` reads `is_question(text)` with **no roster**, so
arms (a)(b)(c)(e) apply to dialogue answers. Ten answer forms flipped across
all ten shipped dialogue families (`sweep_f_dialogue.py`); driving them against
a **live** `incoming_proposal` (`probe_g_live_dialogue.py` — end turns on a
fresh board until Prussia's letter is current) shows three with a real
end-to-end delta:

```
'is accepted'       lever OFF → "You have accepted Prussia's proposal. Treaty signed: PEACE → OPEN_BORDERS"
                    lever ON  → Berthier: "I cannot answer that from the dispatches, Sire."
'had better accept' lever OFF → treaty signed
                    lever ON  → the same shrug
'why not accept'    lever OFF → treaty signed
                    lever ON  → the same shrug
```

**I am not filing the tightening itself as a defect.** Refusing `why not
accept` is the IQ-7 rule working (*an irreversible priced answer fails
closed*), and the dialogue stays current, so `accept` on the next line still
signs. The filable half is the **copy**: with an unanswered letter from
Prussia on the desk, the player gets a counsel list of *orders* —

> Berthier sets down his pen. "I cannot answer that from the dispatches,
> Sire."  What I CAN do today:  Ney, attack Mack …

— and nothing anywhere says the letter is still waiting, nor that an answer
was discarded. Every sibling refusal in this codebase names the matter
("Portugal's letter waits in Envoys — …"), and IQ-7's own rule is that an
unaccepted phrasing is re-prompted **in place**. Here the question desk
(CX-2) wins the route and answers a different question.

Lowest-value member, recorded for completeness: a bare `why not` — English for
*yes, go on* — now gets *"What you want is in the campaign log (press L)."*

### Suggested fix

When `is_question` claims a line and a dialogue is current, the desk's answer
should carry the standing matter's one-line reminder (the `waits in Envoys`
idiom already exists and is a pure function of the current dialogue).

---

# WHAT I COULD NOT BREAK — negative results, each measured

These are reported so the ratio is visible: the row's covered contract is
strong, and four separate attacks on it returned nothing.

1. **`is_question` does not steal a single order the GAME ITSELF produces.**
   650 strings — all 449 golden-corpus utterances + the corpus's live-phrasing
   backlog + all 12 tutorial `suggest` chips + every `region_panel.gd` chip
   (`do:` / `order:` / `_BUILD_CHIP_DEFS`, with real names) + all 28
   `diplomacy_wizard._build_command` outputs + 61 dialogue answer forms + 60
   hand-written natural orders. **24 flagged as questions; all 24 are corpus
   rows that are questions** (plus `do as I ordered` and `may I suggest Ney
   attack`, both caught by the pre-existing first-person arm, under both lever
   positions). `sweep_a_orders.py`.

2. **The CX lever moves nothing across 42,687 generated ordinary lines.**
   53 order templates × marshals/enemies/regions/nations × 17 prefixes × 9
   suffixes, plus 60 answer forms in the same envelope, classified with
   `A_QUESTION_NEVER_ORDERS` both ways: **0 verdict changes**
   (`sweep_b_leverdiff.py`). The method is validated — it *would* have caught
   CX-6's own `do it` regression, which lived in arm (d) behind this lever.

3. **The under-sampled verbs are clean.** Every lead family the row claims to
   cover (arms a/b/c/d/e, plus first-person) × 36 naval / economy / reward /
   vassal / diplomacy / meta / military verbs = **1,064 cases driven end to
   end, 1 executing** — and that one is `end turn?`, which the row documents
   and pins as deliberately left executing (`sweep_e_covered_leads.py`,
   `out_e.txt`).

4. **The 126-province roster arm breaks no order.** 147 subjects (8 player
   marshals + enemy commanders + 126 provinces). **Zero** collide with any word
   in `validation.VALID_ACTIONS`. The 14 that are ordinary English words
   (`Bern`, `Berry`, `Crete`, `Egypt`, `Leon`, `Maine`, `Milan`, `Oran`,
   `Oslo`, `Posen`, `Rome`, `Savoy`, `Syria`, `Wales`) are never the token
   immediately after a modal lead in any order the game teaches. 846 of 1,323
   (lead × subject) pairs become questions and all 846 are of the intended
   `<modal> <third party> <verb>` shape (`sweep_i_reach_and_roster.py`).
   ⚠ One residual worth stating rather than filing: `_question_subjects` is
   deliberately omniscient over enemy names, so the *verdict* differs between a
   board where a commander exists and one where he does not. The docstring
   claims "no fog is leaked … a boolean prints nothing" — true of the boolean,
   and the observable difference (desk answer vs. shrug) is the same one the
   question desk already exposes by design. Not a finding; do not let a later
   slice widen it.

5. **Punctuation, case, spacing and the honorific do not re-open arm (a)/(b).**
   `why not attack Mack.` / `!` / trailing space, `what about attack Mack.`,
   `is Swabia defended.`, ALL CAPS and Title Case forms, and
   `Berthier, …` / `Marshal Ney, …` / `General Ney, …` fronted questions are
   all inert (`probe_j_tail.py`, `sweep_c` `caps` and `addressed` arms — 0
   executing of 235).

---

# ONE METHOD NOTE FOR THE FIX SESSION

Every one of CXR1-1…CXR1-5 is a **comma or a boundary**: a comma that should
not have mattered (CXR1-1, CXR1-5), a comma that should not have disarmed
anything (CXR1-2), and a word boundary that an apostrophe destroys (CXR1-3).
CX-1 put punctuation at the centre of five rules and the punctuation is
exactly what a hurried player omits — which is the premise half two of the
same commit was written on. When the fixes land, build the pins on the
**comma-free, apostrophe-carrying, filler-fronted** form first, and add the
tidy form as the control, not the other way round.
