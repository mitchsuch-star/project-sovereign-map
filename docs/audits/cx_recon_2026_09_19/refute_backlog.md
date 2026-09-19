# REFUTATION of `cx_recon/backlog.md`

**Method.** Default REFUTED. Every claim re-derived from source at `HEAD f7008582`,
or measured by a probe I ran. **The working tree is DIRTY** (a sibling agent is
editing the parse pipeline live), so I did **not** measure on it: I built a
verified byte-for-byte HEAD copy at
`<scratchpad>/cx_recon/probes/head_tree/` — every `backend/**/*.py` diffed against
`git show HEAD:` with line endings normalised, **0 differing** — and every probe
below runs against that tree through the real `POST /command`, `LLM_MODE=mock`,
no key, no network. Harness: `probes/rh.py` (it asserts the imported
`clause_guards` lives under `head_tree` and dies otherwise).

⚠ **I did not reuse the census's own "pristine" tree.** `probes/mypristine/` is
not pristine: `backend/ai/llm_client.py:1806` there carries a hand-added
`"halt "` keyword that is **not at HEAD**. The census patched a defect into its
own control (see MISSED:3).

**Headline verdict.** The report's six routed rows are **not** uniformly
reproduced: three survive, two narrow, one is materially over-stated. Its
answer to your actual question is **directionally right for the wrong reason** —
"the corpus passes 686/686 with zero live calls" is true, but the two numbers it
builds on (**86% never escalate**; *"the live cassette returns `marshals: []`"*)
are both wrong, and the second is a claim about a **hand-written fixture**, not
about any model. And the census's own sampling missed the largest defect in its
scope: **10 of 19 ordinary questions EXECUTE an irreversible action.**

---

## Part 1 — the findings, attacked

### REFUTE:CONCURRENT-WRITE — **SURVIVES, and has escalated**

Re-derived. At my read the tree is dirtier than the census recorded:

```
 M backend/ai/clause_guards.py      643 (HEAD) -> 771 (census) -> 799 (now)
 M backend/ai/llm_client.py
 M backend/commands/executor.py                  <- NEW since the census
 M tests/test_fa_slice7_the_mock_speaks_plainly_2026_09_04.py   <- NEW
 M tests/test_iq7_review_round.py                               <- NEW
?? docs/COMMAND_EXPERIENCE_SPEC.md                               <- NEW (owning spec)
?? tests/test_cx1_a_question_never_orders.py
```

The diff is exactly as described (`A_QUESTION_NEVER_ORDERS`,
`_SUBJECT_WH_WORDS`, `_THIRD_PERSON_SUBJECTS`, `is_question(text, subjects=)` at
`clause_guards.py`; `_question_subjects` at `llm_client.py:536`, consumed at
`:1379` and `:1628`). It is now also editing `executor.py` and **two committed
test files**, and has opened its own spec.

⛔ **The consequence the census under-states is against itself.** Its §0 says
*"Every finding below was re-run against the modified tree and reproduced
identically… None is an artefact of the concurrent edit."* That is false for its
own §8-item-6 table, which is the report's *"single highest-leverage item in the
whole spec"*. See REFUTE:PARSENEG-6.

---

### REFUTE:IQ9-X1 — **NARROWED. Mechanism real; all three supporting claims collapse.**

**What survives (verified in source).** `parser.py:1274` is the `suggest` arm
inside `_apply_fuzzy_matching` (`parser.py:964`), and the CR-1 plausibility
guard at `:1266-1271` demotes a match only when `abs(len(word)-len(match)) > 2`
**or** the first letter differs. `down`(4) vs `Davout`(6) is a length delta of
exactly 2 and shares `d`, so it survives and fires. `hunt` is in `skip_words`
(`:1247`); `down` is not. Measured at HEAD through `POST /command`:
`hunt down mack` → 0 AP, *"I do not find 'down' in the order of battle, Sire.
Did you mean Davout?"* (`probes/rq04_x1_detail.py`).

**Claim 1 — "the live model returns no marshal at all… the retry is
structurally incapable, not merely unlucky." REFUTED as evidence.**
`tests/data/parser_cassettes/cr2-retry-hunt-down-mack.json` carries
`"provenance": "authored"` and its own `recorded.note` reads, verbatim:

> *"authored from the recon prototype's measured shapes — **never a model's
> answer**; the recorder promotes it to provenance 'recorded'"*

and its `notes` field already says *"the retry cannot rescue (recon F2 →
IQ9-X1, pinned as CURRENT behaviour)"*. The census read a fixture that was
**authored to encode IQ9-X1** and reported it as a measurement of the model.
**All 17 cassettes are `authored`; 0 are `recorded`** (`probes/rq09`-adjacent
census, reproduced below in MISSED:2). The honest statement is *"incapable **if**
the model returns no marshal"* — which nobody has measured.

**Claim 2 — "3 of 18 of the corpus's own live_phrasing_backlog die here."
REFUTED: those three utterances are not in the corpus.** The real
`live_phrasing_backlog.utterances` are `hunt down blucher`, `track down the
prussians`, `hunt down wellington until destroyed`, `make your way to rhine`,
`stand fast at belgium`… The census's probe `p_backlog.py` applies an
undisclosed substitution table (`blucher→mack`, `wellington→mack`,
`prussians→austrians`, `bavaria→swabia`, `rhine→rhineland`, `belgium→flanders`)
and the report then presents the result as *"the corpus's own list… measured on
the 1805 board"*. The substitution is disclosed in a code comment and **nowhere
in the report**.

**Claim 3 — "8 of 18 the deterministic road now handles outright." REFUTED at
the executor.** The census measured `parse()["success"]` at the parser tier.
Measured end-to-end through `POST /command` (`probes/rq03_backlog_real.py`):

| arm | executed | clarification/refusal |
|---|---|---|
| the **real** 18 corpus rows, verbatim | **0** | 18 |
| the census's 18 retargeted rows | **1** (`follow and destroy mack`) | 17 |

Every one of its "8 that work" parses with **`marshal=None`**
(`probes/rq04_x1_detail.py`) and lands in *"Which marshal shall support Davout,
Sire?"*. None commands anybody.

**Severity, restated honestly.** The player-facing harm of IQ9-X1 is a **0-AP
honest refusal that names the wrong marshal** — a legibility wart, not a loss.
The real finding under it is larger and different from the one filed: **0 of 18
of the project's own "phrasings we want to support" work end-to-end on the
shipped board**, and only 3 of the 18 fail for the `down`→Davout reason.

**Would the proposed fix regress?** The census's cut — *"when the parse arrived
from a live provider that explicitly returned no marshal, do not run the marshal
word scan"* — is sound in shape, but note it is live-only by construction and
therefore **unreachable in the shipped mock default**, so it fixes nothing for
the shipped build. Pin it would flip:
`tests/test_iq9_keyless_parser_gate.py::TestCR2Retry::test_retry_cannot_rescue_the_word_scan_family_today` (as filed).

---

### REFUTE:IQ9-X2 — **NARROWED to near-REFUTED. The project has a written rule that says this is not a leak.**

**The counter is in the production source the census itself praises.**
`backend/ai/question_desk.py:290-291`:

> *"Fog on his position, not his name"*

and the desk, run at HEAD, answers `where is Castanos` with *"We have no word of
Castanos's whereabouts, Sire."* — i.e. **the shipped game already confirms a
fogged commander exists, unprompted, by landed design** (FA slice 7). The
sibling agent's live diff (`llm_client.py:542`) restates the same rule
independently: *"naming a commander was never the fogged half (his POSITION
is)"*.

**The other two "leaked" facts are public.** `probes/rq05_x2_counter.py`:
`GET /diplomatic_ledger` returns 25,325 bytes naming Spain, Bavaria, Prussia,
Naples and Russia with their treaty states, and CLAUDE.md's own standing rule is
*"diplomacy has no fog of war"*. So *"he exists · his nation · our treaty state"*
leaks nothing that is not already on a screen.

**The stated mechanism is wrong.** The census attributes the leak to *"the
parse-layer auto-correct binding a fogged name as a target"* and the
*"target auto-correct ladder at `parser.py:1360-1410`"*. Measured, the **exact**
spelling gives the byte-identical reply:

```
'Ney, attack Castanos'   -> "Ney cannot attack Spain - they are our ally, Sire..."
'Ney, attack Castanoss'  -> "Ney cannot attack Spain - they are our ally, Sire..."
'Ney, attack Hohenlohe'  -> "We are not at war with Prussia, Sire - Hohenlohe may not be attacked..."
'Ney, attack Hohenloh'   -> (identical)
```

The typo ladder is **not** the vector; the executor answers about any named
enemy, corrected or not. Removing the auto-correct closes nothing.

**What is actually left.** One un-cited residue I found and the census did not:
`GET /ledger` names **2** fogged commanders (`Deroy`, `Brunswick`) in its own
payload (`probes/rq05_x2_counter.py` §2) — a display surface, unrelated to the
parser.

**Regression risk of the filed fix.** Building the "speakable roster" split
would make `where is <fogged enemy>` stop answering, which reds the question
desk's own doctrine and the FA-slice-7 pins behind it. The census flags the
helpfulness trade; it does **not** flag that the trade contradicts a landed
design decision. State that on the row, or the row is a re-litigation, not a fix.

---

### REFUTE:IQ9-X3 — **SURVIVES on mechanism. NARROWED on consequence.**

**Mechanism verified at HEAD, in source and by measurement.** The `fuzzy_error`
failure dict (`parser.py:1803-1825`) carries `success`, `error`, `suggestion`,
`raw_input`, `partial_action`, optionally `llm_error`, `kind`, `unknown_name`,
`candidates` — and **no `mode`** — so `str(parsed.get("mode") or "mock")` at
`backend/main.py:2979` stamps `"mock"`. Reader at `main.py:565-569`, contextvar
at `main.py:632`. All three line numbers are **exact**.

Driven through the IQ-9 replay tier on the HEAD tree
(`probes/rq06_replay_x3.py`):

| utterance | live calls made | `parse_mode` stamped |
|---|---|---|
| `flurble the wibble` | `['parse', 'berthier']` | **`mock`** |
| `hunt down mack` | `['parse']` | **`mock`** |
| `Ney, deal with Mack` (control, adopted) | `['parse']` | `anthropic`, conf 0.85 |

**The consequence is over-stated.** The census: *"`parse_mode` is the only
instrument in the product that records whether a model was consulted, and it
counts only the successes… any attempt to answer 'is routing to the LLM worth
it?' from telemetry today will under-count live calls."* Measured:

* `parse_mode` has **no consumer in the product at all**. Grep over the whole
  repo outside `tests/`: one writer (`main.py:568`) and **one** reader —
  `tools/playtest_driver.py:1332`. No `.gd` file reads it.
* Across **every committed playtest run**, `tools/playtest_runs/**/digest.jsonl`
  holds **2,796** `parse_mode` values and **2,796 of them are `"mock"`**. Zero
  non-mock, ever.

So the instrument has never been pointed at a live model. X3 is a **precondition
to measuring**, not a cause of mis-measuring — nothing has been mis-counted
because nothing has been counted. That is a smaller claim than the one filed,
and it is the one that should go on the row.

---

### REFUTE:IQ7-X7 — **SURVIVES, and is worse than filed. One case corrected.**

Independently reproduced at HEAD with a real Portugal `open_borders` letter
built through `deliver_ai_proposal` (`probes/rq07_x7.py`), checking the
**diplomatic state**, not the routing function:

**15 of my 21 lines SIGN THE TREATY** — `France|Portugal: None -> OPEN_BORDERS`,
message *"You have accepted Portugal's proposal. Treaty signed."* Including:

```
'accept it later'  'accept it next turn'  'maybe accept'  'if we accept'
'accept, but not now'  'perhaps accept'  'accept the offer never'
'accept it when Austria signs'  'remind me to accept'  'almost accept'
'consider accepting'  'i would accept'  'we could accept'
'accept tomorrow if the roads hold'          <- NEW, not in the census's set
```

The census measured `match_dialogue_answer` returning an action id. I measured
the **irreversible state change**, which is the thing that matters. The row is
correct and its severity is higher than "a deferred answer resolves".

**One correction.** `accept, unless Ney objects` does **not** resolve
end-to-end: Berthier's condition guard catches it — *"that is a contingency, not
an order"*. The census's 16-of-17 is a **function-tier** count; at the player
surface at least one of its extension lines is already guarded. `accept? later`
and `do not accept` / `never accept` are also guarded, as it reports.

**The fix shape is right and the warning attached to it is the important part.**
`petition_plain_answer` (`dialogue_routing.py:400`) is the closed grammar;
`match_dialogue_answer:1162` is the single routing branch
(`_is_client_petition_dialogue`). The census's ⛔ — *"do not ship a deferral
blocklist here"* — is the correct carry of IQ-7 pass 3's lesson and should stay
in bold on the row.

---

### REFUTE:IQ10-X1 — **SURVIVES. Mechanism confirmed; one line number off; one precedent the census missed.**

Verified in `scenes/top_bar.tscn`: `BarContainer` `anchors_preset = 10` (:19),
`anchor_right = 1.0` (:20), **`grow_horizontal = 2`** (:22) — GROW_DIRECTION_BOTH.
`ScreenButtons` carries six buttons whose `text` embeds the hotkey
(`"Event Log (L)"` … `"Moniteur (N)"`); `MailboxButton`
`custom_minimum_size = Vector2(110, 0)` is at **:108**, not :107; `MenuBtn`
`(28,28)` at :123 ✓. `scripts/top_bar.gd` is **453 lines** ✓ and a grep for
`clamp|scroll|clip_contents|custom_minimum_size` returns only an icon path and
two `threat_label.visible` toggles (:169, :363, :366, :374) — **no shed, no
scroll, no clamp** ✓.

**The census missed the precedent that makes this a one-line diagnosis.**
`Utils.clamp_centered_panel` (`scripts/utils.gd:519`) exists for exactly this,
its docstring states the mechanism verbatim — *"content_scale_factor up to 2.0
halves the logical viewport"* — and it is called by ten popups. It does **not**
cover the top bar, and cannot: its anchor guard (`utils.gd:544-549`)
structurally excludes non-centre-anchored panels, naming `war_status_panel` as
an excluded sibling. So the bar is outside the one remedy the client already has,
**by construction**, and so is `war_status_panel` — worth checking in the same
slice.

⚠ The pixel figures (x=−26 / −65.5 / 798) remain **UNVERIFIED** — they need the
Godot capture harness, which writes into `docs/audits/` and which I did not run.
The census's recommendation to commit the harness's JSON record beside the PNGs
is correct and I second it.

---

### REFUTE:IQ10-X2 — **SURVIVES. Every cited line is exact.**

`scenes/incoming_proposal_popup.tscn`: `PanelContainer` offsets
`-340/-220/+340/+220` = **fixed 680×440**, centre-anchored (:33-45);
`ContentLabel` `scroll_active = true`, `fit_content = false`,
`size_flags_vertical = 3` (:51-57); four buttons at
`custom_minimum_size = Vector2(140, 45)` (:68, :74, :80, :86).

`scripts/incoming_proposal_popup.gd`: crimson `"Grant unavailable: "` at **:146**,
lapse warning at **:151-159**, `content_label.append_text(...)` at **:164**,
`Utils.clamp_centered_panel($PanelContainer)` at **:197** ✓. And the clamp's own
docstring confirms the census's key point in the source's words:
*"the authored rect (captured on first call) stays the CEILING, so nothing
changes on viewports that already fit"* — **it only ever shrinks.**

The census's own correction (the lapse warning renders *after* the crimson
reason, so the crimson line is not the last line) is verified. Its remedy (b) —
move the crimson reason above the clauses — is the smallest and does not touch
the clamp.

---

### REFUTE:LLM-VALUE — **NARROWED. The conclusion holds; two of the three headline numbers do not.**

**What survives.** `python -m backend.ai.parser_eval` → `686/686 passed (mock
mode)` at HEAD, zero live calls ✓. `LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7` is
at `llm_client.py:63` ✓. The gate-sensitivity reading holds: my histogram over
443 rows is `0.50×42 · 0.55×4 · 0.75×1 · 0.80×52 · 0.90×123 · 0.95×158 · 1.00×8`,
so moving the gate anywhere strictly inside (0.55, 0.75) changes one row at most.

**Number 1 is wrong: "62 / 443 = 14.0% escalate".** That is `confidence < 0.7`,
not escalation. The census never called the real predicate. `_should_fallback_to_llm`
is at **`llm_client.py:900`** (not :891) and carries **five arms besides
confidence**: mock provider · no api_key · `fast_result.refusal` (PARSE-NEG,
terminal by design) · `game_state is None` · `fast_result.action in
NON_ORDER_ACTIONS`. Measured on the census's own denominator with a client that
believes it is live (`probes/rq20_esc_denominator.py`):

| | below the 0.7 gate | **actually escalates** | blocked |
|---|---|---|---|
| all 443 non-`live_only` rows | 62 (14.0%) | **41 (9.3%)** | 21 — *all* PARSE-NEG refusals |
| 1805/`any` rows only (n=388) | 46 (11.9%) | **25 (6.4%)** | 21 |

So *"86% of utterances never escalate"* is really **90.7%**, and the census
over-counts live traffic by **51%**. Worse for its own §8-item-6 recommendation:
`NON_ORDER_ACTIONS` contains `help`, so **a question that routes to `help` can
never escalate** — the model is structurally barred from that family too, and the
census did not notice.

**Number 2 is wrong in kind: "confidently wrong = 1 / 381 = 0.3%".** That counts
rows the pipeline unexpectedly refused. The corpus itself records the class in
its own notes, and the census never read them
(`tests/data/parser_golden_corpus.json`, `mock_only` rows):

> `'Ney, cover the retreat'` — *"NEGATIVE pin. Was silently WRONG at confidence
> 0.9 (**above the LLM-fallback gate, so live mode could never correct it**)"*
> `'Ney, fix bayonets'` — *"the repair branch's bare `fix ` substring executed a
> masonry repair at confidence 0.9."*

Measured (`probes/rq09_corpus_shape.py`): **12** corpus rows whose expectation is
a NEGATIVE pin clear the 0.7 gate — `end the war on any terms` (1.0),
`I want peace` (1.0), `will Ney attack Mack?` (0.8), `would Ney attack Mack` (0.8),
`shall we attack Mack` (0.8), `Ney, fortify and scout Swabia` (0.95), and six
more. Each is a case that *was* confidently wrong and is now held by a
hand-written guard. The historical count is ≥13, not 1.

**Number 3 is a category error: the "live" measurements are fixtures.** See
MISSED:2.

**What the corpus's green actually asserts** (`probes/rq09_corpus_shape.py`,
n=447): **54.1%** positive action assertions · **34.2%** partial/other ·
**11.6%** negative-only refusal pins. "686/686 passed" is therefore not
686 demonstrations that the deterministic road understands a sentence; for a
measurable slice it is a demonstration that a guard refuses correctly.

**Where I agree, unreservedly.** The census's ordering — *fix the thing that
prevents escalation, then instrument, only then tune the gate* — is right, and
its refusal to tune 0.7 without an instrument is right. Its note that PARSE-NEG
§8 item 4 forbids a refusal from escalating is the key structural fact, and my
measurement above shows that rule alone accounts for **every** blocked
below-gate row.

---

### REFUTE:PREDICTOR — **NARROWED. The diagnosis is right; the proposed primitive is the wrong one, measurably.**

**What survives, verified.** The command line is a bare `LineEdit`
(`scenes/main.tscn:238-242`, `placeholder_text = "Type command..."`);
assistance is up/down history only (`main.gd:347-349`, `:929-934`); `Tab` is
unbound in `_on_command_input_gui_input` (`main.gd:908-937`). There is **no
dry-run parse endpoint** — my own route census of `backend/main.py` finds
**53** routes (31 GET / 22 POST; the census said 52), and the only parse-bearing
POST is `/command`, which executes. `fast_parse` at `llm_client.py:976` is
documented as *"Deterministic keyword-parser pass only — never calls the LLM"*.
And it **is** pure: 6 `fast_parse` calls leave `world.to_dict()` byte-identical
(209,196 chars).

⛔ **But `fast_parse` is not the parse the executor obeys, and a preview built
on it would lie.** Measured side by side (`probes/rq10_predictor.py`):

| typed | `fast_parse` — i.e. what the preview would show | what actually happens |
|---|---|---|
| `hunt down mack` | `None → attack → Mack (0.90)` | **refused**, "Did you mean Davout?" |
| `why not attack Mack` | `None → attack → Mack (0.90)` | **Soult fights a real battle**, 1 AP |
| `attack Mack` | — | **Soult fights**, a marshal the player never named |
| `Ney, attack Castanos` | `Ney → attack → **None**` | *"cannot attack Spain — they are our ally"* |
| `Soult and Lannes, attack Mack` | `Soult → attack → Mack` | Soult **and Lannes and four more** move |
| `stand fast at flanders` | `None → hold → Flanders` | *"Which marshal shall hold Flanders?"* |

**The preview matched the executed outcome on 5 of 12.** It is wrong precisely
on `hunt down mack` — the family the row exists to fix — and it names no marshal
on two sentences that commit an army.

**The right primitive is already there and the census walked past it.**
`parser.parse()` **is also pure**: 12 calls over the same world leave
`to_dict()` byte-identical (`probes/rq10_predictor.py` §2). So `/parse_preview`
should wrap `parse()` on a `CommandParser(use_real_llm=False)` — full fuzzy
matching, CR-4 carryover and validation, still keyless, still mock-safe under
§5, still no world mutation. Wrapping `fast_parse` buys a docstring and loses
the answer.

**And recommendation #3 inverts.** *"Echo the resolution, not the confidence"* —
measured, the resolution is wrong on 7 of 12 and silently omits the marshal the
game is about to commit. Showing a wrong *resolution* teaches a worse lesson
than showing a wrong *number*. Either echo `parse()`'s resolution (correct), or
echo nothing.

---

### REFUTE:NPC-12 — **SURVIVES. Exact.**

`grep -c humanize_entity_name` → **0** in both `backend/game_logic/combat.py`
and `backend/game_logic/ledger.py`; `grep -c '\.name}'` in `combat.py` → **71**.
Both figures reproduce to the digit. The round-trip caveat (`ArchdukeJohn`,
`Archduke John`, `the Archduke John` all parse) is also right, so this is a
display row, not a parse row — as filed.

---

### REFUTE:CR7-MULTI — **NARROWED. The flagship example's claim is false at HEAD.**

The census: *"`Soult and Lannes, attack Mack` **executes for Soult alone**,
dAP=−1, and **Lannes is never acknowledged**."* Measured
(`probes/rq11_misc.py`):

```
'Soult and Lannes, attack Mack'  AP=-1
   named in the reply: Ney, Davout, Soult, LANNES, Murat, Bernadotte
   marshals whose state changed: Bernadotte, Davout, LANNES, Mack, Murat, Napoleon, Soult
```

Lannes **is** named and **does** march — the MUSTER machinery brings every
willing corps to the guns, so the second addressee arrives by a different road.
The defect that survives is narrower: the second name is dropped **as an
addressee**, which shows on the verbs the muster does not cover —
`Ney and Davout, fortify` acts on Ney alone, does not contain "Davout", and
costs **2 AP** (not the 1 the census implies for the family).

**And the census left its own open question unanswered when the answer was one
probe away.** Its §8 records *"⚠ whether the CR-2 dropped-tail warning fires…
the `warning` response key is `None`, but I did not search the message body."*
It does fire, inside the body (`probes/rq19_tail.py`):

> `Ney, fortify and scout Swabia` → *"Berthier: **'One order at a time, Sire — I
> have relayed the first. "scout Swabia" must follow as its own command.'**"*

So the `warning` key being `None` is a key-placement fact, not evidence of
silence. `everyone fortify` / `all marshals, hold position` → *"Which marshal…?"*
at 0 AP ✓, and `validation.py:313-314` is the current home of the "coming soon"
string ✓.

---

### REFUTE:PARSENEG-6 — **REFUTED AS STATED. Measured on the sibling's half-fixed tree; the real defect is one severity class higher.**

The census's table is taken *"current tree — the sibling's edit is active"* and
concludes *"**Eight of nine** reasonable questions dump the full COMMAND
REFERENCE… **Verdict: in scope, and the single highest-leverage item**"*, with
the remedy *"routing more question shapes to the desk and replacing the help
dump."*

The same nine lines at **HEAD** (`probes/rq01_parseneg6_head.py`):

| utterance | census (dirty tree) | **HEAD** |
|---|---|---|
| `can Ney attack Mack` | `[HELP DUMP]` | **fights a real battle, 1 AP** |
| `can you attack Mack` | marches | marches |
| `is Mack stronger than Ney` | `[HELP DUMP]` | Berthier "instruction is unclear" |
| the other six | as reported | as reported |

So at HEAD it is **5 of 9 help dumps, 2 of 9 that execute an attack**, not 8 of
9. The census recorded the sibling's *fix* as HEAD behaviour, flagged the one
row it noticed as *"new, from the CX edit"*, and then built a scope
recommendation — *legibility* — on the fixed reading. The correct priority is one
class higher: **a question must never execute.** See MISSED:1 for the measured
family.

---

### REFUTE:PARSENEG-5 — **SURVIVES, and the family is wider than the one pinned exception.**

Reproduced exactly (`probes/rq11_misc.py`): `Ney, retreat if outnumbered` →
**0 AP, "Ney retreats from Rhineland to Lorraine"**;
`Ney, attack when Davout arrives` → honestly refused;
`Ney, hold until Davout arrives` → 2 AP, the real `until` StrategicCondition.

**New, and it corrects the census's mechanism.** `Ney, fortify if attacked`
also **EXECUTES, at 2 AP**. So the census's characterisation — *"`retreat`
survives the clause blanking as **a bare free verb**"* — is wrong: `fortify`
costs 2 AP and is not free. The family is *"an if-clause whose main clause is a
complete, addressed order"*, which is at least two members wide and is not
bounded by the free-verb list. Anyone scoping "one guard, not a system" should
scope it to that predicate, or the second member ships unfixed.

(Refused for comparison: `Ney, move to Swabia if the roads are clear`,
`Ney, scout Swabia if you can`. So the split is not simply "if" vs "when".)

---

### REFUTE:EAS-1-STALE — **SURVIVES. Verified both ends.**

`grep -n live_client_armed backend/commands/meta_executor.py` → **no match**.
The gate now reads `game_state["debug_mode"]` / `DEBUG_MODE=true`
(`meta_executor.py:2426-2428`, comment: *"cheats require an EXPLICIT debug
opt-in (Aug 2026 health-check shippable-build P0)"*), and the row at
`BUG_FIXES.md:10300` still cites the retired `key_source != "none"` computation
at a line number that no longer holds it. Strike it with a pointer to that
landing, as recommended.

---

### REFUTE:NOT-DEFECTS — **SURVIVES. Both are executor-gated; the two paid cases are exactly as described.**

`Ney, fall back and dig in` and `Ney, march at dawn` → **0 AP, no state change**,
*"I could not make out a destination in that order, Sire - name a province"* ✓.
`Ney, hold the line` → 2 AP with the disclosure *"(Our maps read Rhineland as the
province nearest your order, Sire.)"* ✓. `Ney, press the attack` → 1 AP,
*"Your words named no foe our maps know, Sire — Ney marches on Mack at Swabia,
the nearest in sight."* ✓. Recording these as not-to-file was the right call.

---

## Part 2 — what the census MISSED

### MISSED:1 — **A QUESTION EXECUTES. 10 of 19 ordinary questions committed an irreversible action at HEAD.** (P1)

The census's §8-item-6 probe set contains nine questions, and every one of them
happens to be in the *harmless* half. It never asked whether a question can
**act**. Measured at HEAD through `POST /command` on a fresh 1805 board
(`probes/rq02_questions_execute.py`):

| typed | what happened |
|---|---|
| `why not attack Mack` | **a real battle**, 1 AP, 5 corps marched, gold 800→535 |
| `why not retreat` | **GENERAL RETREAT** — all eight corps fell back. **0 AP.** |
| `what about attack Mack` | **a real battle**, 1 AP |
| `how about retreat` | **GENERAL RETREAT** of the whole army. **0 AP.** |
| `retreat?` | **GENERAL RETREAT** of the whole army. **0 AP.** |
| `is it time to build a depot in Paris` | **300 gold + 1 admin AP** spent on a Supply Depot |
| `is Swabia defended` | **whole-army DEFEND**, 1 AP |
| `may Ney attack Mack` | **a real battle**, 1 AP |
| `does Ney attack Mack` | **a real battle**, 1 AP |
| `is Ney attacking Mack` | **a real battle**, 1 AP |

The three retreat cases are the worst of these precisely **because they are
free**: a question moves eight corps across the map at 0 AP, and reversing it
costs the player AP they were never charged to lose.

This sits squarely in the census's own scope (PARSE-NEG §8 item 6) and changes
its remedy: routing questions to `question_desk` and replacing the help dump is
the *second* job. The first is a gate that refuses.

⚠ **Attribution.** The sibling agent has independently found this family and is
building `A_QUESTION_NEVER_ORDERS` for it — its docstrings name nine of these ten
cases. I verified all ten myself at HEAD rather than taking its word. The point
against the census stands: it ran the probe adjacent to this and drew a
legibility conclusion.

### MISSED:2 — **Every "live-LLM" measurement in the report is a measurement of hand-written fixtures.** (P1 for your question)

The report's masthead reads *"Live-LLM behaviour measured **keylessly** through
the IQ-9 replay tier."* Measured: `tests/data/parser_cassettes/` holds 17
cassettes and **17 of 17 carry `"provenance": "authored"`; none is `"recorded"`**
(`probes/` census over the cassette files). The recorder that would promote them
(`tools/record_parser_cassettes.py:225,243`) has never been run against this set.

The replay tier exercises the **code path** keylessly — which is exactly what
IQ-9 shipped it to do — but it cannot measure **model behaviour**, because no
cassette contains a model's answer. Combined with MISSED:4 and with the 2,796
all-`mock` `parse_mode` readings under REFUTE:IQ9-X3, the honest statement of
the project's position is stronger and simpler than the census's:

> **There is not one recorded observation of this game's live parser anywhere in
> the repository.** Not in the corpus (4 `live_only` rows, all served by authored
> cassettes), not in the cassettes, not in 2,796 logged playtest commands. The
> last real live probe on record is the CR-3 landing note of **July 4, 2026**
> (four API calls), i.e. before the whole IQ queue.

That is the answer to *"is routing to the LLM worth it?"*: **nobody can say, and
the reason is not the 0.7 gate or `parse_mode` — it is that the project has
never recorded the model.** The cheapest honest first step is not a fix but a
measurement: run `tools/record_parser_cassettes.py` once, with a key, over the
below-gate family, and promote the cassettes to `recorded`.

### MISSED:3 — **The COMMAND REFERENCE — what 5 of 9 questions return — teaches commands that do not work on the shipped board.** (P2)

The census states *"Nothing open anywhere about: the help text itself."*
Measured by harvesting every quoted example out of `help` and typing each one
back (`probes/rq13_help_typable.py`, `rq14_help_stale.py`):

* `backend/commands/meta_executor.py:704` — `hold — "Davout, hold Ulm"` →
  typed back: **"Region 'Ulm' not found."** `Ulm` is not a province on the
  126-province board (checked against `world.regions`).
* `backend/commands/meta_executor.py:712` — `repair — "repair Lyon" (1 AP, 150g)`
  → typed back: **"Unknown region: Lyon."** `Lyon` is not a province either.
* `backend/commands/economy_executor.py:2312` repeats it inside a **refusal**:
  *"Specify a region. Example: 'repair Lyon'"* — so a player who fails at repair
  is corrected toward a province that does not exist.

Both are legacy-19-region names. CLAUDE.md records the MC exit review (July 11,
2026) as *"help command modernized to the 1805 campaign incl. all econ verbs"*;
these two survived it. This is IQ-10's own drift rule — *the game's own printed
sentence must be typable* — on a surface the census read and declared clean.

**A second, related asymmetry.** CLAUDE.md's Strategic Commands section states
*"Cancel: 'cancel/halt/stop/abort' → `_execute_cancel()`"*. Measured:

```
'cancel Ney' -> works    'Ney, halt'  -> works
'halt Ney'   -> SHRUG    'stop Ney'   -> SHRUG    'abort Ney' -> SHRUG
```

Cause, in source: the cancel keyword list (`llm_client.py:1802-1806` at HEAD)
holds `"cancel "` (trailing space — matches `cancel Ney`) but for the others only
`"halt order"`, `"halt orders"`, `" halt"`, `", halt"`, `"abort order"`,
`"abort orders"`, `"abort mission"`, and nothing at all for a leading `stop`. So
three of the four documented synonyms work in one word order only.
⛔ **The census hit this and patched around it**: its `probes/mypristine/` copy
of `llm_client.py` carries a hand-added `"halt "` that is not at HEAD. A control
tree with a fix in it is not a control.

### MISSED:4 — **The escalation seam itself was never opened.** (P2)

The report's entire §5 is built on `confidence < 0.7`. The function that decides
escalation — `LLMClient._should_fallback_to_llm`, `llm_client.py:900` — is never
called by any census probe. Measured against it (see REFUTE:LLM-VALUE), real
escalation is **41/443 (9.3%)**, not 62/443 (14.0%), and **all 21 of the
difference are PARSE-NEG refusals** that are terminal by design. Two consequences
the census could not have seen from the confidence number alone:

1. `NON_ORDER_ACTIONS` contains `help`, so **a question can never escalate** — the
   §8-item-6 family is barred from the model by the same seam.
2. Any future gate-tuning that only moves `0.7` is moving the smaller of the two
   levers. The refusal arm gates 21 rows; the gate itself, over (0.55, 0.75),
   gates one.

### MISSED:5 — **`attack <enemy>` with no marshal commits an unnamed marshal's whole army.** (P2)

CR-6's bare-attack gating (landed July 16, 2026) makes bare `attack` ask
*"Which marshal shall lead the attack, Sire?"* at 0 AP ✓. But **`attack Mack`**
— bare verb, named enemy, no marshal — **fights**: Soult leads, 1 AP, six corps
move (`probes/rq18_body.py`). The reply is a full MUSTER that never says *"you
did not name a commander; I chose Soult."* This is the same seam
`why not attack Mack` falls through (byte-identical MUSTER, same Soult), and it
is the seam the census's own IQ9-X1 remedy wants to route marshal-less parses
*into*. Scope it before routing more traffic there.

### MISSED:6 — a negative result, reported because I went looking for it

I expected a dictation gap: ROADMAP position 8 shipped OS dictation (Win+H) as
the supported voice road, dictation emits no comma after an address and often no
final `?`, and the census asserts *"every parser defect above is also a dictation
defect"* without testing dictation's own text shape. **Measured, there is no
gap** (`probes/rq15_dictation.py`): 10 typed/dictated pairs
(`Ney, attack Mack` vs `ney attack mack`, …) behave **identically on 10 of 10**,
same AP, same outcome; hyphenated provinces resolve spoken-apart
(`Lannes, move to Franche Comte` → Franche-Comte). Recorded so nobody re-chases
it. (The question family is the one dictation risk, and MISSED:1 shows it fires
with *and* without the `?`, so it is not dictation-specific either.)

---

## Part 3 — my own corrections, stated

* My first help-text sweep reported *"9 of 46 sentences the reference teaches are
  not understood."* **That number is wrong and I am striking it.** Six of the
  nine (`Bravest of the Brave`, `Iron Resolve`, `Roland of the Army`, …) are
  ability names my regex harvested as if they were commands, and one is a
  wrapped-line artefact. **The real count is 2** (`Davout, hold Ulm`,
  `repair Lyon`) plus the `halt/stop/abort` asymmetry.
* My first clarification probe reported `command_clarification: False` on every
  seed and I nearly filed it. It is wrong: the structured question ships as
  flattened top-level keys (`clarification_kind`, `clarification_registered`,
  `options`, `original_command`, `type`, `marshal`) — verified in
  `probes/rq18_body.py`. **The CR-2 clarification road works**: answering `Ney`
  to *"Which marshal shall hold, Sire?"* spends 2 AP and holds; to *"Which
  marshal shall lead the attack?"* spends 1 AP and fights
  (`probes/rq16_clarify.py`). The census's #1 remedy routes into working
  machinery.
* My escalation denominator (388) differs from the census's (443) because I
  filtered to `world in (any, 1805)`. I re-ran on its denominator so the
  comparison is apples-to-apples; both rows are published above.

## Part 4 — still UNVERIFIED

* IQ10-X1's pixel figures — need the Godot capture harness (writes to
  `docs/audits/`; not run).
* IQ10-X2's exact fold position — the committed frame is authoritative.
* XR-2 — no cassette covers a live CR-5 literal ASK. Unchanged.
* Whether a **real** model rescues `hunt down mack` — unmeasurable today for the
  reason in MISSED:2. This is the one open question that decides IQ9-X1's
  prescription, and it costs one API call to settle.
* The census's claim that `… later` / `maybe …` / `if we …` also resolve on
  `settlement_review`, `ally_petition` and `vassal_rebellion` — mechanism is
  sound (those families fall to the ordinary road at
  `dialogue_routing.py:1162`), but I measured only the `incoming_proposal`
  family end-to-end.
