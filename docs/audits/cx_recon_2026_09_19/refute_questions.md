# REFUTING THE QUESTION-DESK CENSUS

Adversarial re-derivation of `scratchpad/cx_recon/question_desk.md`.
Default verdict REFUTED; every row below was re-measured on my own harness
(`probes/r_harness.py` and `probes/r01..r12`), never by re-running the
census's probes.

**Headline verdict: the census is right that a question executes, and wrong
about three of the four P1s it filed under that banner.** Of its ten
"execution" rows, the four modal-lead ones are a real defect. The other
three families — `retreat?`, `end turn?`, `attack?` — behave **byte-identically
without the question mark**, so the `?` is inert and the census has filed a
pre-existing bare-verb-safety defect and a documented design decision as
question-road P1s. Meanwhile the trailing-`?` family it *did* find is **more
than twice as wide as it reported**, and includes a marshal relocation and a
300-gold irreversible build it never tested.

---

## 0. METHOD, and why my numbers are citable and the census's moving ones are not

The census discloses (its §0a) that a sibling agent was editing
`backend/ai/clause_guards.py` while it measured, and re-drove its table twice
against two different hashes. **The tree moved four more times during my run**
— I stamped `clause_guards.py` at `41470474…`, `80d64338…`, `95ec659e…` and
finally `5ed30721…`, and the sibling has since added
`tests/test_cx1_a_question_never_orders.py` (untracked). A hash-stamped table
against a file being edited underneath it is not reproducible by anyone.

So I measure **pristine HEAD (`f7008582`)** instead, which is what ships.
`probes/r_harness.py` fetches `git show HEAD:backend/ai/clause_guards.py` and
`…llm_client.py` and `exec`s them over the module objects *before*
`backend.main` imports them, then asserts the patch took
(`is_question.__code__.co_argcount == 1`, the pristine one-arg signature; the
tree's is two). Nothing under `backend/`, `tests/`, `docs/`, `tools/` or
`godot-client/` was written. `LLM_MODE=mock` and
`parser.llm.use_real_api is False` are asserted before every single call —
**zero live API calls**.

Board: `europe_1805.json`, France, turn 1, seed `historical`, a **fresh world
per utterance**, driven through the real `POST /command` with a full state
fingerprint (turn, AP, battles, every marshal's location/strength/morale/
stance/order/fortification, every region controller, log length) diffed before
and after.

---

## 1. VERDICTS ON THE FILED ROWS

### REFUTE:QD-1 — **SURVIVES** (magnitude narrowed 8 → 7)

Reproduced at pristine HEAD on my own harness, four times over
(`probes/r01_HEAD.txt`). `can Ney attack Mack` spends 1 AP, records
`battles_this_turn 0 → 1`, marches Ney Rhineland→Swabia 24,000→22,029 and
drags in Davout, Lannes and **Napoleon**; Mack 52,000→35,820. `may` / `does` /
`is Ney attacking` identical. The mechanism is exactly as filed: at
`clause_guards.py:579` the lead `can` is not in `_MODAL_LEADS`
(`{will, would, shall}`, line 561), the text does not end in `?`, there is no
first person, and `can` is not in `_WH_WORDS` — so `is_question` returns False
and the verb chain reads the imperative. `_SECOND_PERSON_AFTER_LEAD_RE` at
`clause_guards.py:562` is the correct test and is applied only in the
`_MODAL_LEADS` arm (line 711). **All four line numbers are exact** — unusual
for this repo.

Three corrections:

1. **"Eight phrasings" is seven.** The census's own row body lists seven, and
   its §2 table's eighth entry is `Ney, attack Mack?`, which the same table
   marks *"Documented as intended."* Counting an intended behaviour into a
   defect's headline inflates it.
2. **"No confirmation" is true but under-describes the response.** The reply
   is a 1,566-char MUSTER preview — *"MUSTER — Ney (24,000; 78,676 if all
   march…) vs Mack (large force) at Swabia — the balance of force looks
   favorable"* — followed by the battle in the same payload. It is a *report*,
   not a gate. The CA9 muster-confirm deliberately arms only on `unfavorable`
   odds and a `cautious` marshal (CLAUDE.md, CA9 gate answer 2), and these
   odds are favourable, so no gate exists to have failed.
3. **The census's own UNVERIFIED caveat is now closed, in its favour.**
   `probes/r08_escalation.py` at HEAD: `can Ney attack Mack` parses at
   confidence **0.95**, above `LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7`
   (`llm_client.py:63`), so `_should_use_llm_fallback` short-circuits at
   `llm_client.py:928`. The battle happens in live mode too. Mode-independent.

**On the proposed fix and its blast radius, the census is wrong about itself.**
Its §2.1 warns the subject test "moves three golden-corpus rows"
(`parseneg-do-not-attack-refuses` etc.) because after the negation guard
blanks the clause the lead word is `do`. That is true of its own roster-free
reimplementation. The roster-scoped siting now in the working tree
(`llm_client._question_subjects` → `is_question(text, subjects)`) passes
**686/686** — I ran `python -m backend.ai.parser_eval` on the tree that carries
it. The regression the census predicted does not occur when the rule asks
*who* the subject is rather than *what word* it is.

Corpus facts corrected: the corpus holds **447 entries / 686 assertions**
(the census's "447" is entries, fine), and **26** are interrogative-lead
shaped, not the "16" it reports. Its substantive point holds: **none** of
`can` / `may` / `does` / `is Ney attack(ing) Mack` is pinned anywhere.

---

### REFUTE:QD-2 — **NARROWED past its own filing: this is not a question defect**

The census never ran the one control that decides the row. I did
(`probes/r03_control.py`, HEAD):

```
PLAIN      'retreat' : moved=9  len=194
QUESTIONED 'retreat?': moved=9  len=194
  SAME SHAPE OF MOVEMENT: True
```

Same nine state changes, same 194-character message, same eight corps to the
same provinces, same attrition (Bernadotte −170, Massena −2,100). **The
question mark does nothing.**

So the census's framing — *"`is_question('retreat?') == False` … so the
trailing `?` is discarded and the general-retreat arm fires"* — is
mechanically true and causally empty. The defect is that **the bare
`retreat` verb orders a general retreat of the whole army at 0 AP with no
confirmation**, and it does so whatever punctuation follows. Filing it as
"a question retreats the army" points the fix at `is_question`, and a fix
there leaves `retreat` — which is what a panicking player actually types —
completely untouched. (`retreat` being free is itself the FA-R3 ruling, so
the "free" half is settled design, not part of this row.)

The right row is *"the general retreat has no gate at all"*, a sibling of
CR-6's bare-attack gate, which was built for `attack` and never extended.
P1 severity is defensible; the title and the seam are not.

---

### REFUTE:QD-3 — **REFUTED as filed**

Same control, same result (`probes/r03_control.py`):

```
PLAIN      'end turn' : moved=19  turn 1->2  len=236
QUESTIONED 'end turn?': moved=19  turn 1->2  len=236
```

Identical. And the punctuation strip is **stated in the function's own
docstring**: `is_bare_end_turn` (`clause_guards.py:148`) opens *"True only
when the command IS an end-turn phrasing and nothing else. **Trailing
punctuation is allowed**, and so is an address to the DESK."* The
implementation is `.rstrip(".!? \t")`, introduced by slice 1 (`0bff0858`) and
re-touched by FA-R4 (`b57f5e14`). The census's sibling attributes the strip to
FA-R4; reading `BUG_FIXES.md:4602`, FA-R4 is about the *address* ("the desk
may be addressed"), and the punctuation rule is older. Either way it is
written down, deliberate, and — measured — pinned by nothing: no corpus row
and no test names `end turn?` in either direction.

A documented design decision that produces byte-identical behaviour with and
without the character the row blames is not a P1 defect. It is a design
question for CR-6, and it should be filed as one. (The counter-argument is
real and worth stating: FA-6 made `what happens next turn` safe, so a player
may reasonably expect `end turn?` to be a query. But that is an argument
about the *rule*, not evidence of a bug, and the rule's authors considered
exactly this — the sibling's in-flight comment records that a `?`-saves-you
rule was itself the defect FA-R4 was written to kill.)

---

### REFUTE:QD-4 — **first half REFUTED, second half NARROWED**

**First half, `attack?` → `Ney`.** Control again:

```
PLAIN      'attack' : moved=0  len=42  "Which marshal shall lead the attack, Sire?"
QUESTIONED 'attack?': moved=0  len=42  "Which marshal shall lead the attack, Sire?"
```

Byte-identical, and **neither moves anything**. This is CR-6's bare-attack
gate operating exactly as blessed (gate record `COMMAND_ROBUSTNESS_SPEC.md`
§7, landed July 16 2026 — *"resolve-and-rewrite at the dispatch seam so a bare
`attack` flows through clarification"*). The player then answering `Ney`
fights, four times out of four (`probes/r10_twostep.py`) — because `attack`
+ `Ney` **is** an attack order. The census's claim that *"the gate that is
supposed to make bare verbs safe is what makes this reachable"* inverts it:
the gate is the only reason `attack?` does not immediately pick a marshal and
charge, which is what `attack Mack` does.

**Second half, `who holds Swabia` → clarification.** Real at HEAD
(`is_question("who holds Swabia")` is False; the string reaches the `hold`
verb). But the magnitude is wrong twice over, measured across 16 fresh boards
(`probes/r10_twostep.py`):

* The census contrasts the two answer formats — *"Answering `Ney` instead of
  `1` produces an objection"*. **That contrast does not exist.** The server
  log shows `[CLARIFICATION] Resolved answer '1' -> 'Ney, who holds Swabia'`:
  both formats resolve to the same command. Both produce both outcomes.
* The stance change is the **minority** outcome, not the result: `1` gave
  2 MOVED / 6 inert, `Ney` gave 1 MOVED / 7 inert. **13 of 16 runs hit Ney's
  objection and changed nothing at all.** The census reports the 19% branch as
  the behaviour.

Still a real defect (a question about the map can become a stance order), but
P1 with a deterministic 1-AP consequence is not what the board does.

---

### REFUTE:QD-5 — **SURVIVES** (one figure corrected)

Every wall reproduced on my own runs: `who is winning`, `what's my income`,
`am I at war with Prussia?`, `how much is a battalion?`, `what can I build
here?` all return **exactly 12,717** characters (`probes/r06_HEAD.txt` §A).
The "the game knows the answer" half verified independently
(`probes/r11_counts.py`): `get_diplomatic_state("France","Prussia")` is
`PEACE`; `build_active_wars` returns 1 war carrying `war_score`;
`get_active_agenda("Austria", w)` returns the `redeem_italy` blurb verbatim as
quoted. Correction: the ledger's `economy` block has **36** keys, not 24.

---

### REFUTE:QD-6 — **SURVIVES**

Reproduced exactly (`probes/r06_HEAD.txt` §E): `Ny, attack Mack` → *"I do not
find 'Ny' in the order of battle, Sire. Did you mean Ney?"* (66 chars);
`where is Ny?` → 12,717. `Wellington, attack` → *"There is no 'Wellington' in
the order of battle, Sire. Whom did you intend?"* (75); `where is Wellington?`
→ 12,717. `where is Masena?` → 12,717. `_resolve`
(`question_desk.py:82`) is exact-form plus whole-word containment with no
fuzzy arm — confirmed by reading it.

---

### REFUTE:QD-7 — **SURVIVES**

`shoud I attack?` → *"I do not find 'shoud' in the order of battle, Sire. Did
you mean Soult?"* Reproduced verbatim.

---

### REFUTE:QD-8 — **NARROWED: behaviour real, BOTH mechanism claims false**

The behaviour reproduces — `where is Napoleon?` → *"Marshal Napoleon stands at
Lorraine with 10,000 men (morale 85)."* — and `display_names.py:**1358**` is
the exact line of `marshal_honorific`, whose docstring does carry the row-NP
finding.

But:

* **"`question_desk.py` does not import it (measured: `False`)" is FALSE.**
  `question_desk.py:136` reads `from backend.display_names import
  humanize_entity_name`. Measured `"display_names" in src` → **True**. The
  desk imports the module and uses a *different* function from it.
* **"hardcodes `Marshal {name}` at 12 sites" is 6.** `grep -n "Marshal {"
  backend/ai/question_desk.py` → lines 250, 252, 255, 261, 264, 265.

A row whose fix is "call this one function at N sites" is weakened when N is
half what is filed and the import it says is missing is already there. The fix
is smaller and safer than advertised — I found no test pinning the literal
`"Marshal Napoleon"` out of the desk, so it should red nothing.

---

### REFUTE:QD-9 — **finding SURVIVES, cited evidence REFUTED**

The behaviour is real and I reproduced all of it: `where is the Emperor?`,
`where is the emperor`, `where is Bonaparte?`, `where is Blucher?`,
`where is Wellington?` → 12,717 each; `where is Napoleon Bonaparte?` → works.

The evidence is wrong:

* **`combat_executor.py:1722` is a COMMENT, not a player-facing literal.**
  Lines 1718–1726 are a `#` block explaining a past defect; the quoted string
  sits inside it. The real player-facing line is **`combat_executor.py:1747`**
  (`f"The Emperor commands in person{_dims} — every corps …"`). The census
  cited the explanation of the string as the string.
* **"80 string literals" matches nothing I can measure.** An AST walk over all
  123 backend `.py` files (`probes/r11_counts.py`) counts **95** occurrences
  inside string constants, **85** on comment lines, **157** raw. 80 is neither.

---

### REFUTE:QD-10 — **SURVIVES**

`who holds Bavaria?`, `who controls Bavaria?`, `who holds Austria?` → 12,717
each, while `who holds Swabia?` → *"Swabia is held by Bavaria."* and
`who holds Paris?` → *"Paris is ours, Sire."* Reproduced exactly.

---

### REFUTE:QD-11 — **SURVIVES**

All three phrasings reproduce, including the third answer without the `?`
(*"Sire, I await your instructions regarding Austria."*), and the agenda blurb
is present in state exactly as quoted.

---

### REFUTE:QD-12 — **SURVIVES, and is slightly stronger than filed**

`question_answered` occurs **once** in all of `backend/`
(`meta_executor.py:619`) and **zero** times in `main.py`. Measured on the wire
(`probes/r12_qd12.py`), the 37-key response to `where is Ney?` carries neither
`question_answered` **nor `intel_report` nor `free_action`** — the builder
whitelists all three away. So the consequence the census asserts is correct
and under-stated: the client has nothing on the wire at all to tell a 61-char
desk answer from the 936-char intel report except the length of the string.

---

### REFUTE:QD-13 — **REFUTED**

The census measured turn 1 with nobody dead and concluded *"structurally
unreachable on the shipped board"* and *"two authored honest refusals that
essentially nobody will ever see."* I staged a death through the production
seam `WorldState.destroy_marshal` (`probes/r07_fallen.py`, HEAD):

```
destroy_marshal(Mack) -> True ; 'Mack' in world.marshals: False
fallen_marshals: ['Mack'] ; 'Mack' in _askable_enemy_names: True

where is Mack?               -> "Mack's corps no longer exists, Sire - it was
                                 destroyed at Swabia on turn 1."      (75 chars)
how many men does Mack have? -> same
where is Kutuzov? (unseen)   -> "We have no word of Kutuzov's whereabouts, Sire."
```

The refusal family is not unreachable — it is **designed, built and correct**,
and it fires the first time an enemy marshal dies.
`llm_client._askable_enemy_names` says so in its own docstring (*"The fallen
are askable too (a seen tombstone answers)"*) and explicitly appends
`fallen_marshals`.

Worse for the row: the census's stated route to the one line that *is* hard to
reach — *"`We have no record of {shown}, Sire` … today, only a fallen
marshal"* — is provably **the one route that cannot reach it**. Reading
`_answer_enemy` (`question_desk.py:268-285`), a marshal absent from
`world.marshals` falls to the tombstone arms first; arm 3 fires only when
there is **no** tomb, and a fallen marshal always has one. I confirmed by
popping the tombstone by hand: the name then leaves the roster entirely and
the reply is the 12,717-char wall, not arm 3.

The meta_executor:613 half is correct in conclusion but not for the stated
reason: reading `answer_question` (`question_desk.py:330`), every one of the
three subject types returns a string, so that refusal fires only when the desk
raises an exception, which the `except` at the bottom swallows.

---

### REFUTE:QD-14 — **SURVIVES; one quoted reply does not reproduce**

`is Ney at Paris?`, `what turn is it?`, `what year is it?`, `how many turns
left?` → 12,717 each. Confirmed. But the census quotes `Ney's location?` as
*"Berthier frowns at the dispatch. 'I see Marshal Ney's name, Sire, but the
instruction is unclear. Valid orders include: attack, move, scout, defend,
fortify, recruit.'"* I measure a different 142-char reply: *"Sire, Marshal Ney
awaits your command, but I cannot parse this order. Might you…"*. Presented as
an exact quote, it is one draw from a rotating bank.

---

### REFUTE:QD-C — **measurements SURVIVE, routing NARROWED**

Every needle count reproduces exactly: 12,717 chars, `status` 0, `where is` 0,
`who holds` 0, `how many men` 0, `question` 0, `war score` 0, `SCREENS` 1,
`ledger` 7, `F1` 4, `Talleyrand` 4. The reply is identical for every walled
question.

But it is **already owned and deliberately deferred**, which the row does not
say. `llm_client.py` states it in the comment block immediately above the
routing seam: *"`help` rather than a refusal because it is the honest answer
to 'how do I …' — it costs no AP and it is what a bare `?` already does. **A
question-answering Berthier belongs to CR-6.**"* I verified the sub-claim:
bare `?` does indeed return the same 12,717-char reply. CR-6 *proper* is a
live ROADMAP row (position 15) that "needs its own design gate". So QD-C is a
good UX observation filed against a decision that has a named owner — it
belongs on the CR-6 gate, not in a defect table.

---

### REFUTE:QD-OK — **SURVIVES, and I extend it**

Everything listed reproduces. Two more things the desk gets right that the
census did not record, and that a fix must not break:

* **The desk is free.** Three questions in a row: AP `4 → 4`
  (`probes/r09_HEAD.txt` §M5).
* **It works behind a pending dialogue.** With two queued dialogues after an
  end turn, `where is Ney?` and `who holds Swabia?` still answer (the log
  shows `[DIPLOMATIC] Soft-stop pass-through`), so the letter-book does not
  shadow the desk.

---

## 2. WHAT THE CENSUS MISSED

### MISSED:1 — The trailing-`?` family is **8 of 19 order verbs**, not three bare verbs, and it spends gold

The census found `retreat?` / `end turn?` / `attack?`, concluded the family was
*"bare verbs with no lead at all"*, and stopped. That characterisation is
wrong — the rule has nothing to do with bareness. `is_question` requires an
interrogative **lead**; *every* order verb lacks one; so *every* order
survives its own question mark. Driven at HEAD (`probes/r05_HEAD.txt`):

| utterance | result |
|---|---|
| `retreat?` | general retreat, 8 corps *(census found)* |
| `end turn?` | turn 1→2 *(census found)* |
| `Ney, attack Mack?` | battle *(census documented as intended)* |
| **`Ney, move to Lorraine?`** | **Ney relocated Rhineland→Lorraine, 1 AP** |
| **`Ney, scout Swabia?`** | **scout executed, 1 AP** |
| **`scout Swabia?`** | **Soult scouts, 1 AP** |
| **`Ney, defend?`** | **stance → DEFENSIVE, 1 AP** |
| **`build a depot in Paris?`** | **"Construction started: Supply Depot in Paris (2 turns, 300 gold)"** |

Five of those eight the census never tested. The last is the sharp one: a
question mark on a construction order **spends 300 gold irreversibly**.

Honest limits, measured not assumed: `declare war on Austria?`,
`propose peace with Austria?` and `make Bavaria a vassal?` came back **inert**
— but *not* because a question guard caught them. Diplomatic routing runs
before the question test (the census's own pipeline diagram is right about
this), so they land in the advisory, and `make Bavaria a vassal?` is refused
for want of a marshal. `grant Ney a rente?` is refused because his expectation
is already met, and `Ney, recruit infantry?` because the treasury is 197 gold
short. Those are board accidents, not guards, and I have not shown what they
do on a board where the preconditions are met.

### MISSED:2 — There are **three** predicates for "is this a question", and the safest one already exists

| predicate | where | rule |
|---|---|---|
| `is_question` | `clause_guards.py:579` | interrogative LEAD + a second signal |
| `line_asks_a_question` | `dialogue_routing.py:820` | **any `?`** OR `is_question` OR subject-auxiliary inversion |
| `_is_advisory_question` | `main.gd:1969` (client) | ends with `?` OR first word in a 7-word WH list |

At HEAD the two backend predicates **diverge on 15 of 29 cases**
(`probes/r04_predicates.py`), and the divergence set is precisely
MISSED:1's family: `retreat?`, `attack?`, `fortify?`, `scout Swabia?`,
`declare war on Austria?`, `recruit infantry in Paris?`, `grant Ney a rente?`,
`make Bavaria a vassal?`, `build a depot in Paris?`,
`propose peace with Austria?`, `cede Milan to Bavaria?`,
`revoke Ney's pension?`, `end the turn?`, `end turn?`, `Ney, attack Mack?`.

The wider, safer rule was written **the day before this census**, by IQ-7's
review round R3-9 (`A_QUESTION_NEVER_ANSWERS`, `dialogue_routing.py:190`,
September 18 2026), for exactly this failure — its own comment records
*"`should i accept?` SIGNED THE TREATY — the keyword arm read `accept` out of
a question."* The dialogue road learned that a question mark alone is
sufficient; the parse road did not. This is the single-source finding the
census should have led with, and it makes MISSED:1 a one-line fix with a
precedent rather than a new rule.

The client predicate (MISSED:5) is a third copy with a fourth vocabulary.

### MISSED:3 — A fallen marshal **of your own** gets the 12,717-char manual

Falling out of the QD-13 refutation. On a board where a player marshal has
died through the production seam (`probes/r07_fallen.py`):

```
where is Bernadotte?                -> 12,717-char COMMAND REFERENCE
how many men does Bernadotte have?  -> 12,717-char COMMAND REFERENCE
```

against a fallen **enemy**'s honest *"Mack's corps no longer exists, Sire."*

Root, read at the call site (`llm_client.py:1639-1642`): `classify_question`
is handed `marshals=list(_game_state_dict(game_state, "marshals"))` — the
**living** player marshals only, since `build_llm_game_state` filters
`m.strength > 0` — and `enemies=_askable_enemy_names(game_state)`, which
appends only tombs where `tomb.get("nation") != player`. Nobody carries the
player's own dead. This is worse than anything the census filed under the
wall, because the player's own fallen marshal is exactly the name they will
type, and the game has the tombstone sitting in `world.fallen_marshals` with
his province and his turn of death.

### MISSED:4 — **Zero** of 22 question-shaped utterances consult the LLM

The census lists this UNVERIFIED and reasons about QD-1 only. Measured
keylessly at HEAD (`probes/r08_escalation.py`), every one of the twelve named
questions plus the executing family plus two order controls parses **at or
above** the 0.7 gate:

```
where is Ney?                 status    0.90     who is winning?    help  0.80
can Ney attack Mack           attack    0.95     retreat?           retreat 0.80
what's my income?             help      0.80     end turn?          end_turn 0.80
...
WOULD ESCALATE: 0 of 22
```

Two consequences the census did not draw. First, **the entire question road is
deterministic** — the 12,717-char wall is chosen at confidence 0.8 without a
model ever being consulted, so buying an API key changes nothing about any of
the twelve questions, and CR-6 cannot be solved by better escalation alone.
Second, QD-1 is **mode-independent**: the battle is fought at 0.95 with or
without a key, so the census's "not measured under `--llm anthropic`" caveat
can be retired in the row's favour.

### MISSED:5 — The client swallows some questions **before they are sent**

The census marked the click road UNVERIFIED and considered only whether a
region-panel chip emits a question (it does not — I grepped
`region_panel.gd`; it emits `"recruit infantry in Paris"`-shaped orders only).
But the client intercepts **typed** lines too. `main.gd:1602` calls
`_redirect_diplomatic_command(command)` and **returns without sending** when it
matches. Inside it, `_is_advisory_question` (`main.gd:1969`) exempts a line
only if it ends in `?` or its first word is in `DIPLO_ADVISORY_STARTS` —
`what, how, where, who, whom, why, which`. **`when` is absent**, while
`clause_guards._WH_WORDS` includes it.

So a line like `when did Austria declare war on us` (no question mark) is not
advisory to the client, contains the family keyword `"declare war on"`, and is
answered with *"Berthier: Matters of state are conducted at the table, Sire —
not by dispatch."* — never reaching the backend, which would have treated it
as a question. A question about the past is answered as if it were an order
for the future.

⚠ **UNVERIFIED as runtime behaviour**: this is derived from reading
`main.gd:1602`, `:1921-1985` and `DIPLO_FAMILY_KEYWORDS`. I did not run Godot.
The predicate and the keyword membership are source facts; the end-to-end
consequence is an inference and should be confirmed in a client pass.

### MISSED:6 — A negative result worth recording: a question does **not** move the CR-4 focus

I expected `where is Davout?` to set the persistent command focus and re-aim
the next bare order. It does not (`probes/r09_HEAD.txt` §M1): with the
question first, bare `attack Mack` still selects Soult and moves the same six
marshals as the control with no question; an explicit `Davout, fortify` first
*does* change the outcome. The desk is read-only with respect to command
history. Worth pinning if QD-8's fix touches `question_desk`.

---

## 3. WHAT I WOULD BUILD, AND WHAT WOULD RED

1. **One question predicate.** Retire the parse road's narrower rule in favour
   of `dialogue_routing`'s shape — a trailing `?` on an unaddressed line is a
   question — and keep the addressed-order exemption (`Ney, attack Mack?`
   stays an order, as both `is_question`'s docstring and the corpus row
   `r7-would-you-scout-question-mark-is-an-order` require). That closes
   MISSED:1 and QD-2/QD-4's first half at one seam. **What it would red:**
   nothing in the corpus that I can find — no entry pins `retreat?`,
   `attack?`, `fortify?` or `build … ?`. `end turn?` must be **excluded by
   name**, or it reds `is_bare_end_turn`'s documented contract and the client
   lapse-confirm gate FA-R4 mirrors word for word.
2. **The subject test for modal leads** (QD-1) is already built in the working
   tree, roster-scoped, and passes 686/686. That is the right siting, and the
   census's own warning against it applies only to the roster-free version.
3. **The player's own dead into the roster** (MISSED:3) — one term in
   `_askable_enemy_names`, or a third roster. The tombstone answers already
   exist and are correct.
4. **`marshal_honorific` at 6 sites** (QD-8), not 12, and the import is
   already there.
5. **Do not** file QD-3, or QD-2 as written. QD-3 is a documented rule; QD-2's
   real subject is the ungated general retreat, and fixing `is_question` does
   not touch it.

---

## 4. LEDGER

| row | verdict |
|---|---|
| QD-1 | SURVIVES (8→7 phrasings; fix-blast-radius warning refuted) |
| QD-2 | NARROWED — not a question defect; `?` measured inert |
| QD-3 | REFUTED — `?` inert; documented rule; nothing pins it |
| QD-4 | half REFUTED (`attack?` ≡ `attack`, CR-6 by design), half NARROWED (13/16 inert) |
| QD-5 | SURVIVES (36 ledger keys, not 24) |
| QD-6 | SURVIVES |
| QD-7 | SURVIVES |
| QD-8 | NARROWED — both mechanism claims false |
| QD-9 | SURVIVES; cited evidence line is a comment; 95/85/157, not 80 |
| QD-10 | SURVIVES |
| QD-11 | SURVIVES |
| QD-12 | SURVIVES, stronger than filed |
| QD-13 | REFUTED |
| QD-14 | SURVIVES; one quote does not reproduce |
| QD-C | SURVIVES on measurement; owned by CR-6, not unowned |
| QD-OK | SURVIVES, extended |

**Probes:** `probes/r_harness.py`, `r01_exec.py`, `r02_text.py`,
`r03_control.py`, `r04_predicates.py`, `r05_qmark_family.py`, `r06_desk.py`,
`r07_fallen.py`, `r08_escalation.py`, `r09_missed.py`, `r10_twostep.py`,
`r11_counts.py`, `r12_qd12.py` (outputs `r01_HEAD.txt`, `r03_out.txt`,
`r05_HEAD.txt`, `r06_HEAD.txt`, `r09_HEAD.txt`, `r10.txt`). All at
HEAD `f7008582`, `LLM_MODE=mock`, zero network.
