# Refutation of `llm_value.md` — "Is routing to the LLM worth it?"

**Adversarial re-derivation, read-only, September 19, 2026.** Default verdict
REFUTED; a finding survives only where I reproduced it myself.

Every figure below is the output of a probe under `scratchpad/cx_recon/probes/r*.py`
or a `file:symbol` I opened. No live API call was made (network guard installed in
every probe touching the provider; `LLM_MODE=mock`; `ANTHROPIC_API_KEY` popped).

> **On the moving tree.** `backend/ai/llm_client.py` and `backend/ai/clause_guards.py`
> are still MODIFIED in the working tree by a sibling agent. I did **not** use the
> census's `pristine/` directory — I built my own at
> `scratchpad/cx_recon/refute_pristine/`, restored both files with
> `git show HEAD:…`, and verified byte-identity against HEAD programmatically
> (148,941 / 31,700 bytes, `True`). **Every verdict below is measured on that
> verified pristine-HEAD copy at `f7008582`**, through the real
> `CommandParser.parse` and the real `POST /command` endpoint, on the shipped
> 126-province 1805 board. Where the tree state matters I say so.

---

## Scoreboard

| # | Finding | Verdict | One line |
|---|---|---|---|
| 1 | CX-LLM-1 delegation buys one bit | **NARROWED** | Mechanism right; headline false — the model's `flavor` survives and changes the player-visible message. p3 held `flavor` constant at `None` on all four arms. |
| 2 | CX-LLM-2 86% want a refusal | **NARROWED** | Arithmetic reproduces exactly. 11 of the 25 are `mock_only`, whose `expected` is a *mock* contract the live evaluator SKIPS; and "escalation's job is to NOT help" is the wrong reading — on these rows the model is the danger. |
| 3 | CX-LLM-3 retreat-as-a-noun | **SURVIVES (corrected + widened)** | 12/12 at the endpoint across four marshals. The oscillation is the **objection roll**, isolated. But the family SPLITS, and the proposed fix breaks three legitimate orders. |
| 4 | CX-LLM-4 3.4% / 0% / 0% | **NARROWED** | Numbers reproduce exactly. "0% on a campaign actually being played" is circular: that arm is **9 templates repeated 160 times**. Cost half is wrong in the census's own direction. |
| 5 | CX-LLM-5 gate cannot be moved | **SURVIVES (numbers corrected)** | Its curve ignored two of the gate's three exits. True corpus 0.85 → **15.8%** (not 19.5%), 0.91 → **46.2%** (not 50.7%). Conclusion stands. |
| 6 | CX-LLM-6 `is Swabia defended` executes | **SURVIVES** | Reproduced on pristine HEAD, plus `is Rhineland defended`. Narrower than implied in one place: `is Paris garrisoned` does not execute. |
| 7 | CX-LLM-7 retry cannot rescue | **REFUTED (duplicate)** | It is **IQ9-X1**, already filed at **P3**, already routed to CR-6 proper, already pinned as current behaviour with a flip test named. Census grades it P2 and presents the mechanism as new. |
| 8 | CX-LLM-8 no live measurement exists | **NARROWED** | "17/17 authored" is TRUE and verified. "The project has no committed measurement of live model behaviour at all" is **FALSE** — four named sources, one of them in the file the census was auditing. |
| 9 | CX-LLM-9 word collisions | **SURVIVES** | Confirmed as self-corrected. |
| 10 | CX-LLM-10 nine questions hit the help dump | **NARROWED; mechanism wrong** | Not "above the gate". `help`/`status` sit in `NON_ORDER_ACTIONS`, so **no gate setting reaches them** — proved at gate 1.01. This also blocks the census's own recommendation #3. |
| 11 | CX-LLM-11 Brunswick residue | **NARROWED** | Parse-tier residue confirmed. At the endpoint on the shipped board the attack is **REFUSED** by the peace gate. Needs a Prussia war to bite. |
| 12 | CX-LLM-12 the tree moved | **SURVIVES** | Agreed; I rebuilt and verified independently. |

**Six things the census missed** are in §B, including one new mechanical exploit
and the measured answer to the user's actual question about efficiency.

---

# A. Finding by finding

## REFUTE:CX-LLM-1 — **NARROWED**. The model's answer is *not* entirely discarded; the probe held the surviving field constant

**What re-derives.** The routing is as described. `backend/main.py`, the delegation
block: `_arm = route_arm(_deleg.personality, parse_resolved_to_action(parsed))`,
then the cautious arm re-issues `f"{_deleg.marshal} scout {_deleg.scout_target}"`
and the aggressive arm `f"{_deleg.marshal} pursue {_deleg.target}"`, both re-parsed.
`delegation.parse_resolved_to_action` is a `-> bool`. The comments quoted are
verbatim. All confirmed.

**What does not.** Four lines above `route_arm`, the same block reads the model's
answer again:

```python
_delegation_flavor = (parsed.get("command") or {}).get("flavor")
```

and both executing arms spend it — `resolve_live_cautious_prefix(_deleg,
_delegation_flavor)` and `resolve_delegation_flavor(_deleg, "aggressive",
_delegation_flavor)`. That is CR-5b Flavor Echoing, and it is player-visible text.

**Measured** (`probes/r1_delegation_flavor_survives.py`, four cassettes differing
in `flavor` **and nothing else**, cautious arm, `Davout, deal with Mack`):

```
model flavor : None        -> 'Davout scouts Swabia: ... Davout, cautious as ever, will reconnoiter ...'
model flavor : 'As you command, Sire.'
                           -> 'Davout scouts Swabia: ... \n\nAs you command, Sire.\n\nDavout, cautious as ever ...'
model flavor : 'It shall be done, though the ground is poor.'
                           -> '... \n\nIt shall be done, though the ground is poor.\n\n...'
model flavor : "By your leave - the Emperor's will is mine."
                           -> (dropped by the register gate; falls back to the note alone)

>>> DISTINCT MESSAGES across 4 model answers differing ONLY in `flavor`: 3
```

**Why p3 could not see it.** `probes/p3_delegation_one_bit.py` defines
`BASE_INPUT = {..., "flavor": None, ...}` and every one of its four arms is
`dict(BASE_INPUT, action=…, marshals=…, target=…)` — **`flavor` is `None` on all
four**. The probe varied the three fields the code discards and held constant the
one field it reads. "DISTINCT OUTCOMES: 1" is an artefact of the probe's own
construction, and the headline claims built on it — *"the model's **entire**
answer is discarded"*, *"**Only** `parse_resolved_to_action(parsed)` — a
**boolean** — survives"* — are false as written.

**Honest scope of the narrowing.** On the **aggressive** arm I measured 1 distinct
message across the same four flavors — because that case lands on the bad-odds
modal, and aggressive flavour deliberately skips every modal surface (a documented
CR-5b boundary). So: flavour survives on the cautious arm, and on the aggressive
arm only when no modal intervenes. The *mechanical* answer (action/target/marshals)
is genuinely discarded, and that half of the finding stands.

**Severity.** Not P1. Delegations are the census's own 3 of 27 unique corpus
escalations and 5 of 48 play escalations (I re-measured 5). A call that returns one
mechanical bit plus a spoken line, on ~10% of an already 3.4% population, is a P3
efficiency item, not a P1.

**Would the fix regress?** The census's change #1 ("replace that boolean with a
deterministic predicate") flips guardrail (e) — `parse_resolved_to_action`'s
docstring says in terms that the mode gate is the feature, not an accident — and
it would also **delete the flavour channel for the delegation family**, which its
own §4 item 3 lists as a thing the keyless player loses. The census flags the gate;
it does not flag that its fix removes a second live-only feature it elsewhere
counts as a loss.

---

## REFUTE:CX-LLM-2 — **NARROWED**. The arithmetic is exact; the reading of it is a category error, twice

**What re-derives, to the digit** (`probes/r2_gate_and_denominator.py`, pristine HEAD):

```
CORPUS: gate evaluations=692  escalated=45 (6.5%)
CORPUS: UNIQUE escalating entries = 29
ESCALATING rows with expected.success False = 25/29 = 86.2%
```

I also measured what the census did not: the corpus's **base rate** of refusal rows
is 47/447 = **10.5%**. So escalation really does select refusal-shaped sentences
8× above base. That part is sound.

**First category error — `mock_only`.** Of the 25 refusal rows, **11 are tagged
`mock_only`**:

```
break-through-enemy-lines · cr5-deleg-literal-live-retired-note ·
fa-n24-a-land-diversion-is-not-the-grand-diversion · fa-n8-pontoon-bridge-is-not-a-keel ·
fa80-a-hole-is-not-a-hold · money-for-the-troops · ney-cover-the-retreat ·
ney-fix-bayonets · r7-retire-ney-is-not-a-retreat ·
r7-send-the-wounded-forward-is-not-a-march · r7-the-line-held-is-not-an-order
```

`backend/ai/parser_eval.py` **skips every `mock_only` row when `use_real_llm`**
(`skipped_mock_only`). A `mock_only` row's `expected` block is by construction a
statement about the *deterministic chain*, not about what should happen when the
model is consulted. The corpus says so in its own notes — `ney-cover-the-retreat`:
*"FA-73 (FA slice 7): a MOCK contract — the live prompt never promised to refuse a
deed no action models; the live twin pins the real harm instead."* So "the corpus
says must be REFUSED" is supportable for at most 14 of the 29, not 25. **44% of the
evidence for the 86% is mis-read.**

**Second category error, and the bigger one — "escalation's job on them is to NOT
help."** The live twins exist because the model on these sentences is *dangerous*,
not idle. The corpus's own note on `fa73-live-cover-the-retreat-is-not-a-retreat`:

> "Slice 7 measured that **the live parser reads both of these as a cavalry
> CHARGE — a real order the executor can run**, recklessness permitting — so
> `not_action: retreat` passed while the model launched an attack nobody ordered."

That reframes the 86% completely. These are not wasted calls; they are the calls
where the model is the hazard and the corpus is the fence. Which also kills the
census's §2b line **"(c) made it worse: 0 observed"** — see MISSED:4, where I
measure a 17,264-man loss on exactly one of these rows.

**Third problem — the denominator is swapped mid-argument.** The headline reads
*"86% of what it catches is a sentence the corpus says must be REFUSED"* and is
carried into the ruling as a claim about escalation's value **in play**. But the
census's own §1b established that the corpus is not play. I pulled the 48 play
escalations (`probes/r3_play_escalations.py`) and read them. A large share are
**real orders the chain cannot read**: `Ney, take Vienna` · `send somebody,
anybody, to take Munich` · `no, forget that, press on to Vienna` · `Murat, ride at
the enemy` · `Murat, you magnificent idiot, ride at them` · `Ney and Davout
together, break the Austrians …` · `Murat, ride down the Austrians at Swabia` ·
`Oudinot, march to Bordelais` · `Senarmont, move to Munich` · `Senarmont, bombard
Jellacic` · `reward whoever fought best last turn` · `I will offer an alliance to
Prussia myself` · six delegations. That is the opposite population to the corpus's,
and it is the one the ruling is about. The census's own §2b found 10 of 16
cassettes "rescued a real order" — its two sections contradict each other and the
86% is the one that got into the headline.

---

## REFUTE:CX-LLM-3 — **SURVIVES**, corrected in three places and widened in one

**The core is real and I reproduce it.** `backend/ai/llm_client.py` at HEAD fires
the retreat branch on `("retreat" in command_lower and not
_mentions_screening_idiom(command_lower))`, and `_mentions_screening_idiom` is a
four-verb allowlist `(?:cover|screen|protect|shield)\s+(?:the|our|his|their|her)\s+…`.
Confirmed by reading `git show HEAD:backend/ai/llm_client.py`.

**Endpoint truth, pristine HEAD, 12 runs per row** (`probes/r6_retreat_stochastic.py`):

```
'Lannes, cut down the retreat'      -> {'MOVED': 12}   Franche-Comte -> Lorraine, eff 1.5 -> 0.825, AP 4->4
'Davout, cut down the retreat'      -> {'MOVED': 12}   Rhineland -> Lorraine
'Soult, cut down the retreat'       -> {'MOVED': 12}   Lorraine -> Franche-Comte
'Bernadotte, cut down the retreat'  -> {'MOVED': 12}   Franconia -> Munich, 170 men lost to the march
```

So the harm is real, free, and not marshal-specific. **SURVIVES.**

**Correction 1 — I isolated the oscillation the census marked UNVERIFIED.** It is
not in the parse. `probes/r4_retreat_noun.py` runs the family six times (three
repeats × fresh-world and shared-world) and returns **7/11 every single time**,
`conf=0.9` on every member. The variability is at **execution**: the marshal
objection is a roll. `Lannes, retreat` measured `{'OBJECTION': 2, 'MOVED': 10}` over
12 runs. A single-shot endpoint sweep will therefore label one or two rows
differently between runs — which is exactly the 6↔7 the census saw. Not ambient
conditions; the disobedience roll.

**Correction 2 — two of the census's own rows measure differently here.** I get
`Lannes, harry the retreat` → **attack** (`Cannot find 'Retreat' to pursue`), not
"refused"; and `pursue the retreating enemy` → attack. Minor, but the "6–7 of 11"
population is not the one I measured.

**Correction 3, and it matters for the fix — the family SPLITS.** Members that also
carry `strategic_type = PURSUE` do **not** retreat. `Ney, run down the retreating
enemy` parses `action=retreat, strategic_type=PURSUE` and at the endpoint
**pursues Mack and fights**, 6/6. The harmful members are the `strategic_type=None`
ones: `cut down / cut off / press / block / exploit / punish the retreat`, `cut off
their retreat`, `cut off his retreat`, `ride down the retreating …`.

**The proposed fix would ship a regression, and I can name what it breaks.**
The census proposes *"demote any `retreat`-bearing sentence with a transitive verb
before it to below-gate."* Measured at the endpoint on pristine HEAD:

```
'Ney, order the retreat'   -> MOVED Rhineland->Lorraine  x6   (correct behaviour)
'Ney, sound the retreat'   -> MOVED Rhineland->Lorraine  x6   (correct behaviour)
'Ney, begin the retreat'   -> MOVED Rhineland->Lorraine  x6   (correct behaviour)
```

Those are three legitimate retreat orders with a transitive verb before the noun.
The rule as written refuses all three. And in the corpus it reds
**`hound-the-retreating-forces`** (`expected.strategic_type: PURSUE`) and
**`fa-d20-cover-the-retreat-under-an-attack-is-still-an-attack`**
(`'Ney, attack Mack and cover the retreat'` → `attack`). The workable shape is
narrower: *`retreat` as a bare noun object with no pursuit verb and no strategic
upgrade*, which is the discriminator the board already computes.

**Widened**: see **MISSED:1** — one member of this family is not a wrong retreat at
all but a free battle, and it is the sentence the game itself prints.

---

## REFUTE:CX-LLM-4 — **NARROWED**. The numbers are right; the inference is circular and the cost half is wrong

**Reproduced exactly** (`probes/r3_play_escalations.py`): `PLAY: commands=1416 gate
evals=1416 escalated=48 = 3.39%`, and the per-arm table matches the census row for
row, including `commanded_full40 0/160`, `commanded_spender40 0/173`,
`volte_court_austria 0/196`.

**The inference does not follow.** *"0% on a campaign actually being played"* treats
those three arms as a sample of a player typing. They are not. Measured:

| arm | commands | unique strings | **templates** (proper nouns masked) |
|---|---|---|---|
| `commanded_full40` | 160 | 51 | **9** |
| `commanded_spender40` | 173 | 56 | **10** |
| `volte_court_austria` | 196 | 52 | **10** |
| `weird_live_voice2` | 31 | 30 | **28** |

`commanded_full40` is `status` ×18, `<Marshal>, fortify`, `<Marshal>, drill`,
`<Marshal>, unfortify`, `<Marshal>, attack Mack`, `<Marshal>, move to <Region>`,
`recruit 10000 infantry with <Marshal>`. Its own header note says it was authored to
spend all four action points every turn for the FA-D27 balance measurement. **Nine
templates repeated 160 times escalate 0% because they were written by an author who
could read the parser** — that is a fact about the instrument, not about a played
campaign. The census's §1b sentence *"the ones that represent a player playing the
campaign"* is the load-bearing step and it is unsupported.

**The cost half is wrong, in the census's own direction.** It corrects the
monetization memo's `$0.003`/call by scaling routing and call count but never checks
the price — while the very file it was auditing carries a measured one,
`backend/ai/providers.py` (AnthropicProvider docstring):

> *"Per parse: ~5K input + ~300 output ≈ **$0.0065** (measured on the 126-province
> 1805 boot, CR-3 live probe)"*

That is ~2.2× the memo's figure and matches the skill-table rate for
`claude-haiku-4-5` ($1.00/MTok in, $5.00/MTok out) against the census's own
measured 4,904-token prompt. So the census's corrected *"~$0.024 a session"* is
itself ~2× low; the honest number using its own method is ~**$0.05**. The
directional conclusion (cost is not the reason to question escalation) survives —
but the census published a correction to a documented figure while inheriting the
error it was correcting.

**The click-road half is under-sampled and, more importantly, not probative.** The
census transcribed 22 chips from three producers. There are at least **seven** `.gd`
producers of typed commands (`region_panel.gd`, `marshal_management.gd`,
`strategic_ledger.gd`, `main.gd`, `map_renderer_base.gd`,
`incoming_proposal_popup.gd`, `objection_dialog.gd`). That said, more chips would not
move 0%: chips emit the canonical phrasings by construction. The real objection is
that "a mouse-only player never reaches the model" is not evidence about whether
*typing* should reach it, and this is a game whose core fantasy is typing.

---

## REFUTE:CX-LLM-5 — **SURVIVES**, with every number in its table corrected

The census's curve was arithmetic over the measured confidence distribution. The
real gate has three exits — confidence, `fast_result.refusal`, and
`fast_result.action in NON_ORDER_ACTIONS` — and the last two are checked *after* the
confidence test, so they never appear in a distribution-only calculation.

I moved the real constant `llm_client.LLM_FALLBACK_CONFIDENCE_THRESHOLD` and counted
real escalations (`probes/r14_true_gate_curve.py`):

| gate | corpus (census) | **corpus (measured)** | **play (measured)** |
|---|---|---|---|
| 0.55 | 5.6% | **5.6%** (39/692) | **3.0%** (43/1416) |
| **0.70 shipped** | 6.5% | **6.5%** (45/692) | **3.4%** (48/1416) |
| 0.85 | 19.5% | **15.8%** (109/692) | **6.2%** (88/1416) |
| 0.91 | 50.7% | **46.2%** (320/692) | **43.8%** (620/1416) |
| 0.96 | 92.8% | **88.3%** (611/692) | **82.5%** (1168/1416) |

**The conclusion is unchanged and if anything better supported**: to reach a
0.90-confidence defect you escalate ~44–46% of everything, ~13× today's play rate.
**But 0.85 is materially cheaper than the census's table claims** — 6.2% of play,
not 19.5% — which is worth knowing if anything ever does sit at 0.80–0.84. Today
nothing in the measured defect set does.

---

## REFUTE:CX-LLM-6 — **SURVIVES** on pristine HEAD

`probes/r12_batch_verify.py`, real endpoint, verified pristine copy:

```
ap=4->3 ok=True  'is Swabia defended'     'All forces take defensive positions: Ney, Davout, Soult, Lannes, Murat, Bernad...'
ap=4->4 ok=True  'is Swabia defended?'    <COMMAND REFERENCE help dump>
ap=4->3 ok=True  'is Rhineland defended'  'All forces take defensive positions: ...'
```

Confirmed, and one member wider than filed (`is Rhineland defended`). One narrowing:
the family is not "copular lead with no `?`" in general —

```
ap=4->4 ok=False 'is Paris garrisoned'    'Berthier studies the map. "Sire, I note the reference to Paris, but which marshal..."'
```

so the executing case is specifically **`is <Region> defended`**, where `defend`
is a whole-army verb with no addressee. That is the shape a fix must key on.

---

## REFUTE:CX-LLM-7 — **REFUTED as a finding: it is an owned, routed, pinned row**

`docs/BUG_FIXES.md:281`:

> **IQ9-X1** | **P3** | The CR-2 forced retry cannot rescue the word-scan family.
> `hunt down mack` → the fast pass binds `down` → Davout at 0.9, the retry fires
> exactly once, the marshal-less live parse comes back — and is re-run through the
> fuzzy pass, whose word-scan re-reads `down` → Davout again; one live call,
> discarded, the original error stands. Pinned as CURRENT behaviour:
> `TestCR2Retry::test_retry_cannot_rescue_the_word_scan_family_today`.
> **ROUTED to CR-6 proper** (ROADMAP position 15).

The mechanism the census describes (`_apply_fuzzy_matching(retried, effective_text,
…)` re-running on the same raw text, `backend/commands/parser.py` lines 1797–1801)
is the row's own text. The census does say "this is IQ9-X1's root", so it is not
concealed — but it files it at **P2** against a row already graded **P3** with an
owner, a landing slice and a completion definition, and presents "it is structural
rather than a tuning problem" as a conclusion the row already states. Nothing new
survives.

---

## REFUTE:CX-LLM-8 — **NARROWED**. The narrow fact is true; the inference built on it is false

**True and verified**: `tests/data/parser_cassettes/MANIFEST.json` lists 17
cassettes, `provenance: "authored"` on all 17 (measured). The
`usage.input_tokens: 5000` placeholder claim is fair.

**False**: *"this project has no committed measurement of live model behaviour at
all."* Four committed sources, found by grepping the repo the census was auditing:

1. **`backend/ai/providers.py`**, the AnthropicProvider docstring — *"Per parse:
   ~5K input + ~300 output ≈ $0.0065 (**measured** on the 126-province 1805 boot,
   **CR-3 live probe**)"*. In the file the census measured token counts from.
2. **`docs/BUG_FIXES.md:8557`, the PC15-8 live-probe session** — *"The live probe
   REPRODUCED the flagship failure (**live parse → `attack` at 0.85** for literal
   Soult)"*, and then *"**Live compliance measured, not assumed** (temp-0 probes:
   **2/3 unknown + 1/3 scout** on the resolvable case, **2/2 unknown** on the
   unresolvable case, never attack)"*. That is a recorded live non-determinism rate
   at temperature 0, which is decision-relevant to this exact question and which the
   census's ruling would have wanted.
3. **`docs/audits/CA9_CAMPAIGN_DIGEST_2026_08_08.md` + `PLAYTEST_CA9_2026_08_09.md`**
   — a 19-turn France/1805 campaign driven live over HTTP with `LLM_MODE=anthropic`,
   which filed **PT-54** against live model output (*"The live-LLM unparseable
   fallback emits markdown and stage directions into a BBCode terminal"* — since
   fixed: `prompt_builder.py` now carries *"Reply in plain prose only. Never use
   markdown: no asterisks…"*).
4. **The corpus's own note** on `fa73-live-cover-the-retreat-is-not-a-retreat` —
   *"Slice 7 **measured** that the live parser reads both of these as a cavalry
   CHARGE."*

The defensible claim is the much narrower one: **no cassette has been recorded from
the live API**, so the *replay harness* encodes authored contracts. That is worth
saying. "No measurement exists" is not.

---

## REFUTE:CX-LLM-9 — **SURVIVES**

Reproduced at the endpoint: `hunt down mack` → *"I do not find 'down' in the order
of battle, Sire. Did you mean Davout?"* (0 AP, honest refusal); `hunt near mack` →
Ney; `hunt sit mack` → Soult. And the self-correction holds: `Ney, hunt down Mack`
→ pursues Mack correctly at 2 AP. `south, attack Mack` does command Soult (1 AP,
muster preview). The row's own P3/P4 grading is right.

---

## REFUTE:CX-LLM-10 — **NARROWED, and its stated mechanism is wrong**

**Narrowing first**: 6 of the sampled forms return the help dump, not all 9 —
`has Davout drilled?` returns a drill refusal (*"Davout cannot drill with enemy
forces nearby!"*), not the manual. And the desk does answer `where is Mack` /
`how strong is Ney` / `how many men does Mack have`, as the census says.

**The mechanism is wrong, and this is the load-bearing part.** The census says the
forms are unreachable *"because 0.8 > 0.7"*, implying a threshold could reach them.
It cannot. `help` and `status` are members of `validation.NON_ORDER_ACTIONS`
(`{'cheat','debug','economy','end_turn','finances','help','meta_command','status','treasury'}`),
and `_should_fallback_to_llm` checks that set **after** the confidence test.

Proved by raising the real constant to 1.01 — "escalate everything the gate
permits" (`probes/r13_gate_cannot_reach.py`):

```
--- gate = 1.01 ---
esc=False conf=0.8 action=help    'will Ney attack Mack?'
esc=False conf=0.8 action=help    'is Ney fortified?'
esc=False conf=0.8 action=help    'did Ney retreat?'
esc=False conf=0.8 action=help    'should we recruit more infantry?'
esc=False conf=0.8 action=help    'is Paris garrisoned?'
esc=False conf=0.9 action=status  'where is Mack'
esc=False conf=0.9 action=status  'how strong is Ney'
esc=True  conf=0.9 action=defend  'is Swabia defended'
```

**No gate setting reaches this family.** Which has a direct consequence the census
did not draw: its **recommendation #3** — *"Route questions to the desk, then to the
model … escalate only what the desk cannot answer"* — is **structurally blocked**,
because the FACT desk lives behind `status` and `status` is in the skip list.
Building #3 means editing `NON_ORDER_ACTIONS`, a set whose own comment (FA-N9) says
it is **ONE list** shared with the parser's strategic gate, and which feeds
`NEVER_STRATEGIC_ACTIONS`. That is a blast radius, not a copy change, and the
census costs #3 at "~0.75 session" without it.

---

## REFUTE:CX-LLM-11 — **NARROWED**. Real at the parse tier, gated at the endpoint on the shipped board

The parse-tier residue is confirmed. But at the endpoint on the shipped 1805 boot:

```
ok=False 'Ney, attack Brunswick'  'We are not at war with Prussia, Sire - Brunswick may not be
                                   attacked while the peace holds. Declare war on Pru...'
ok=False 'Ney, move to Brunswick' 'Cannot enter Brunswick - it is controlled by Hanover
                                   (diplomatic state: PEACE)...'
ok=False 'Brunswick, fortify'     'Marshal Brunswick commands for Prussia, Sire - he does not
                                   answer to us...'
```

So on the board a player actually boots into, the wrong resolution is caught by the
diplomatic gate one layer down and the player is told something true. The harm needs
France to be at war with Prussia. The census reports it as "CONFIRMED STILL LIVE"
without that guard — which is the distinction this repo's audit history says kills
findings. (The `move to` line also confirms the documented split is intact:
addressee → province, target → marshal.)

---

## REFUTE:CX-LLM-12 — **SURVIVES**

Agreed and independently done. `git status` still shows both files modified plus
`tests/test_cx1_a_question_never_orders.py` untracked. I built my own pristine copy
rather than trust the census's, and verified byte-identity to HEAD.

---

# B. What the census missed

## MISSED:1 — **[P2, NEW] The game's own printed sentence, typed back, buys a free battle**

The census graded the retreat-noun family as "the marshal marches away". Half of it
does the opposite, and that half is the sentence **the game prints to the player
after a cavalry pursuit**:

- `backend/game_logic/combat.py:926` and `backend/commands/combat_executor.py:7032`
  — *"cavalry **runs down the retreating enemy**! (+N pursuit casualties)"*

Type it back (`probes/r9_free_pursuit.py`, pristine HEAD, fresh world, N=3 each):

```
'Ney, pursue Mack'                    price={'4->2 (cost 2)'} battle=True
'Ney, hound the retreating forces'    price={'4->2 (cost 2)'} battle=True     <- the pinned twin
'Ney, run down the retreating enemy'  price={'4->4 (cost 0)'} battle=True     <- FREE
'Ney, attack Mack'                    price={'4->3 (cost 1)'} battle=True
```

And it repeats within one turn:

```
ap 4->4  ok=True  battle=True   'Ney pursues Mack (at Swabia). Mack spotted at Swabia! Engaging!'
ap 4->4  ok=True  battle=True   'Ney pursues Mack (at Swabia). Mack spotted at Swabia! Engaging!'
ap 4->4  ok=False battle=False  'Ney is engaged with Mack and cannot begin a strategic march.'
```

**Two free battles per marshal per turn**, stopped only by the engaged-guard, not by
the action economy. Cause: `action = "retreat"` is free by design (FA-R3, and
`_action_costs` has no `retreat` entry so `action_costs_point` is False), while the
strategic layer upgrades the deed to PURSUE. `backend/commands/executor.py` already
documents this exact hazard for a different route — *"Waiving the gate for it let
`Davout, pursue Wellington` at 0 AP attach a standing PURSUE and march him a
province"* — so the doctrine exists and this route slips under it.

This is a mechanical exploit at `conf=0.9`, above the gate, reachable by copying the
game's own words. It sits inside the family the census filed and it is more serious
than the filed half. It is also squarely an IQ-10 rule violation ("the game's own
printed sentence was not typable") one grade worse: here it *is* typable, and it
cheats.

## MISSED:2 — **[P2] The recorded reason for rejecting prompt caching is measurably wrong, and the real blocker is a different number**

This is the user's actual question ("a way to make it more efficient"), and the
census's §3 measured only totals.

`docs/STATUS.md:10464` records the decision *"so it is not re-litigated"*:

> *"tools+system is ~700 tokens, below Haiku 4.5's **2048**-token minimum cacheable
> prefix, and **the volatile game state sits at the TOP** of the ~3.7K-token user
> prompt."*

**Both clauses are wrong.**

*Where the volatile content sits* (`probes/r10_prompt_cacheability.py`, five
different commands, same 1805 world):

```
prompt chars: [16582, 16585, 16591, 16587, 16579]
longest common PREFIX across 5 prompts : 12,576 chars (75.8%, ~3,144 tokens)
identical content between two prompts  : 16,579/16,582 = 100.0%
first differing line: 187/234 -> 80% down the prompt, and it is the COMMAND TEXT
section map: ## Command to Parse @12,555 (75.7% down)
```

The volatile element is **the command**, and it is three-quarters of the way down.
Under an actual world change (`probes/r11_prompt_stability_across_turns.py`, marshal
moved + strength changed):

```
STABLE under a marshal move   : 14,615 chars (~3,653 tokens) = 88.1%
VOLATILE under a marshal move :  1,967 chars (~491 tokens)  = 11.9%
  -> ## Your Marshals (French)                399 chars  @offset 36
  -> ## Cardinal Directions & Generic Targets 1,568 chars @offset 7,960 (48% down)
```

So **88.1% of every parse call is byte-stable**, in two blocks totalling 1,967 chars
that would have to move to the bottom.

*The minimum.* The authoritative table (claude-api skill, `shared/prompt-caching.md`
§ API reference) gives the minimum cacheable prefix for **`claude-haiku-4-5` as
4,096 tokens**, not 2,048 — and notes the minimums are **not monotonic** (512 on the
newest models, 4,096 on Haiku 4.5, which is the model
`backend/ai/providers.py:484` pins).

Which produces a sharp, actionable result and a trap:

- Render order is `tools` → `system` → `messages`. Measured: `PARSE_TOOL` = 2,860
  chars ≈ **715 tokens**; system prompt = 177 chars ≈ **44 tokens**.
- **Naive fix (breakpoint before `## Command to Parse`, no reorder):** 715 + 44 +
  3,144 ≈ **3,903 tokens — below 4,096. It would silently not cache**, no error,
  `cache_creation_input_tokens: 0`. This trap is the real reason the rejection was
  right, and it is not the reason recorded.
- **With the reorder (move the two volatile blocks below the stable body):**
  715 + 44 + ~3,643 ≈ **4,402 tokens — above the floor**, caching ~74% of a
  ~4,904-token call at ~0.1× on reads.

⚠ Those token figures are chars÷4 estimates. The margin over 4,096 is thin enough
that **this must be confirmed with `client.messages.count_tokens` before anyone
builds it** — and that is a free, keyless call shape the repo does not currently
make. Mark the 4,402 UNVERIFIED.

Two smaller notes for the same question: the parse call is correctly pinned
`temperature: 0` (`providers.py`, CR-5 guardrail (b)) — so identical input is
genuinely cacheable/memoizable — while the `ProviderConfig` default `temperature=0.3`
applies only to the Berthier narrative call. And a **local response memo** keyed on
`(utterance, world-digest)` would be cheaper than caching and needs no prompt
restructure, since temperature is 0 and 88% of the context is stable anyway.

## MISSED:3 — **[P2] "(c) made it worse: 0 observed" is an artefact of well-behaved cassettes; I measured 17,264 men**

The census's §2b table reports zero cases of the model making things worse, across
16 cassettes it acknowledges are all authored. The repo's own reproduction says
otherwise — `docs/audits/fa_build_2026_09_04/repro/REPRO_K5_the_unknown_action_prompt.md`
records a faked live provider answering `charge` for `Murat, fix bayonets`
destroying 18,160 men — and the census never opened it.

Re-measured here, independently, on the shipped 1805 board
(`probes/r15_made_it_worse.py`, one adversarial cassette, keyless, network guard on):

```
-- Murat reckless=10, co-located with Mack
   live_calls=1 ok=True  strength 22,000 -> 4,736  (lost 17,264)
   '[Cavalry][Combat] GLORIOUS CHARGE! Murat leads a devastating cavalry assault! ...'

-- boot Murat (recklessness as shipped)
   live_calls=1 ok=False strength 22,000 -> 22,000 (lost 0)
   'Murat needs to build momentum first! ... (currently 0).'
```

`Murat, fix bayonets` contains no verb the game models and no target. With a key and
a wrong answer it costs 78% of a corps; without a key it is a Berthier shrug. The
gate is not merely low-yield on this family — it is the only route by which the
sentence can do harm at all. That belongs in the ruling, and it changes the shape of
the recommendation from "re-aim it" toward "fence it".
(The control arm — model answers `unknown` — raised inside the TestClient call and
did not complete; recorded UNVERIFIED, not used.)

## MISSED:4 — **[P3] The "2 calls, not 1" correction is already pinned in the repo, a day earlier**

The census presents *"the memo is wrong by a factor of two"* as a discovery.
`docs/IMPROVEMENT_QUEUE_SPEC.md` §1.8, the IQ-9 landing record, lists among that
row's test tiers: *"**Berthier's second call (2 calls, tool-mode then text-mode)**"*
— an existing pin in `tests/test_iq9_keyless_parser_gate.py`. Correcting the
monetization memo's prose is still worth doing; calling the behaviour a new finding
is not.

## MISSED:5 — **[P3] The corpus's own `live_phrasing_backlog` correction is real but under-stated**

The census reports 8 of 18 backlog phrasings now parse in mock. I confirm the
direction. What it does not draw out: three of the remaining ten shrug because of
the `down` collision (IQ9-X1), so the *genuine* live-only phrasing backlog is
**seven**, not eighteen — and the ruling's "unusual order phrasings" rescue class,
one of the two reasons it keeps escalation, rests on those seven plus the free-text
question class that MISSED:6 shows is unreachable.

## MISSED:6 — **[P2] Both of the census's surviving rescue classes have a structural blocker it did not check**

The ruling keeps escalation for two measured rescue classes. Each has a blocker one
layer away that the census did not look at:

1. **Free-text questions and diplomatic asks** — unreachable at any gate setting
   (§CX-LLM-10 above): `help` and `status` are in `NON_ORDER_ACTIONS`. Its
   recommendation #3 is not a 0.75-session change.
2. **Unusual order phrasings** — the class is seven phrasings after MISSED:5, and
   the corpus's live twins (`fa73-live-*`) exist because the model, measured, turns
   two of them into a cavalry charge.

That does not make the ruling's option (iv) wrong. It does mean its two load-bearing
justifications are thinner than stated, and that option **(v) drop it** is closer
than the census allows — which is worth putting to the user plainly, since the
census's re-open condition ("if a recorded-cassette measurement shows fewer than 1
rescue in 200") requires an instrument run nobody has scheduled.

---

# C. Bottom line for the user's question

**Is routing to the LLM worth it?** The census's answer ("re-aim it") survives, but
for different reasons than it gives, and the evidence is more two-sided:

- **Escalation's downside is real and measured, not zero** (MISSED:3, 17,264 men).
  The 86% of "refusal rows" the census reads as wasted calls are the rows where the
  model is dangerous and the prompt had to be hardened against it.
- **Both surviving upsides are smaller and more blocked than stated** (MISSED:5,
  MISSED:6).
- **Cost is ~2× what the census says and ~2× under-reported by the memo** — the
  measured number has been sitting in `providers.py` all along at **$0.0065/call**.
- **The confident-and-wrong defects the census found are real** (CX-LLM-3, CX-LLM-6)
  and the gate genuinely cannot reach them (CX-LLM-5, numbers corrected). Those are
  deterministic-chain fixes and should be built regardless of what happens to
  routing. **Do not build CX-LLM-3's fix as filed** — it breaks `order/sound/begin
  the retreat` and reds two corpus pins.
- **The efficiency ask has a concrete, measured answer** (MISSED:2): 88.1% of the
  parse prompt is byte-stable; the recorded rationale for rejecting caching is wrong
  about where the volatile content sits and understates the Haiku 4.5 floor
  (**4,096**, not 2,048). A breakpoint alone silently misses the floor; a two-block
  reorder clears it. Confirm with `count_tokens` first.
- **A "text predictor" is the wrong framing for this codebase**: with
  `temperature: 0`, 88% context stability, and a 3.4% routing rate, the cheap win is
  a **response memo keyed on `(utterance, world-digest)`** plus the prompt reorder —
  not a second model.

---

## Probes

All under `scratchpad/cx_recon/probes/`, all keyless, all against the verified
pristine-HEAD copy at `scratchpad/cx_recon/refute_pristine/` unless noted:
`_rf.py` (harness) · `r1_delegation_flavor_survives.py` · `r2_gate_and_denominator.py` ·
`r3_play_escalations.py` · `r4_retreat_noun.py` · `r5_retreat_endpoint.py` ·
`r6_retreat_stochastic.py` · `r7_game_own_words.py` · `r8_endpoint_family.py` ·
`r9_free_pursuit.py` · `r10_prompt_cacheability.py` ·
`r11_prompt_stability_across_turns.py` · `r12_batch_verify.py` ·
`r13_gate_cannot_reach.py` · `r14_true_gate_curve.py` · `r15_made_it_worse.py`
(this one runs against the working tree, since it only exercises the executor).

## Stated limits

- No live API call. Every "the model said X" is an authored or adversarial cassette,
  mine included — the same limit the census states about itself.
- Token counts are chars÷4. The 4,402-token figure in MISSED:2 is **UNVERIFIED** and
  must be confirmed with `messages.count_tokens` before it is built on.
- MISSED:1's free-PURSUE: I measured two free battles before the engaged-guard bit.
  I did not establish the maximum per turn across multiple marshals.
- CX-LLM-3's objection roll: I measured the distribution over 12 runs per row; I did
  not read the roll's implementation to confirm the mechanism is the disobedience
  RNG rather than some other per-request variation.
- I did not exhaustively enumerate the client's dynamic chips; I counted producers.
