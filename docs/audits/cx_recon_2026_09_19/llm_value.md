# Is routing to the LLM worth it?

**Recon, read-only, September 19, 2026.** Every figure below is the output of a
probe committed under `scratchpad/cx_recon/probes/` or a `file:symbol` I opened.
No live API call was made: the network guard from `tests/_parser_replay.py` was
installed in every probe that touches the provider, and the model's answers come
from the committed cassettes.

> ### ⚠ The tree moved under this recon — and every headline was re-measured against pristine HEAD
>
> Midway through, `git status` showed `backend/ai/llm_client.py` and
> `backend/ai/clause_guards.py` **MODIFIED in the working tree** by a concurrent
> sibling agent in this same workflow (the diff is labelled *"CX slice 1 — A
> QUESTION NEVER ORDERS"* and widens `is_question`; the shared scratchpad holds
> other agents' `predictor.md`, `two_roads.md`, `near_miss.md`). **I did not make
> those edits** — my probes only monkeypatch at runtime and I wrote nothing under
> `backend/`.
>
> Because some of my measurements ran against that moving tree, I rebuilt a
> **pristine copy of HEAD** in scratch (`scratchpad/cx_recon/pristine/`, the two
> files restored with `git show HEAD:…` and verified byte-identical) and re-ran
> the load-bearing probes. Results below are **pristine-HEAD figures**. What
> re-verified unchanged: the escalation rate (45/692 = 6.5%, identical
> distribution), sweeps A/B/C, the `live_phrasing_backlog` correction, the
> `Brunswick` residue, and `is Swabia defended`. What changed: the retreat-family
> count (§5b, now stated as a measured range). **Relevant to the ruling: a
> sibling agent is already building part of my recommendation #3** — see §6.

**The one-sentence answer: as shipped, escalation is close to worthless — not
because the model is bad, but because the gate routes the wrong sentences. It
fires on 3.4% of real play, 86% of what it catches is a sentence the corpus says
must be REFUSED, on the one feature it is advertised for the model's entire
answer is discarded, and every confident-and-wrong defect I could reproduce sits
at confidence 0.90–0.95 where the gate never opens.**

---

## 0. The numbers, in one table

| Measurement | Value | Probe |
|---|---|---|
| Escalation rate, golden corpus (447 entries) | **45 / 692 = 6.5%** | p1 |
| Escalation rate, committed playtest scripts (1,416 commands, 31 arms) | **48 / 1,416 = 3.39%** | p1b |
| Escalation rate, the two 40-turn *commanded* arms | **0 / 160 and 0 / 173 = 0.00%** | p1b |
| Escalation rate, the CLIENT'S CHIP road (mouse-only player) | **0 / 22 = 0.00%** | p1b |
| Escalating corpus rows whose `expected` is `success: false` | **25 / 29 = 86%** | p14 |
| "retreat-as-a-noun" phrasings that march the player's own marshal away, all at conf 0.90 | **6–7 of 11** | p9 |
| Escalating corpus rows where the corpus says a NEW ORDER should result | **0 / 29** | p14 |
| Input per parse call, 1805 boot (system + user + tool schema) | **19,619 chars ≈ 4,904 tokens** | p4 |
| Live calls per `/command` request, measured ceiling | **2** (memo claims ≤1) | p10, p11 |
| Distinct outcomes from 4 contradictory model answers on a delegation | **1** (control: 3) | p3 |
| Gate needed to catch the measured defects (conf 0.90) | **> 0.90 → 50.7% of commands escalate** | p15 |

---

## 1. How often does the gate open?

The gate is `LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7` in
`backend/ai/llm_client.py`, consumed by `LLMClient._should_fallback_to_llm`.

**Probe method** (`p1_escalation_rate.py`): the production seam
`CommandParser.parse(utterance, game_state, world=world)` with the live provider
*armed at the gate but stubbed at the call* — `llm.provider_name = "anthropic"`
and a fake key, so `_should_fallback_to_llm` evaluates its real conditions, while
`_parse_with_live_provider` is replaced by a counter that returns the
`fast_result` it was handed (which is exactly what the shipped code treats as
"the provider declined", so downstream behaviour is byte-identical to mock).

### 1a. The golden corpus — 6.5%

```
gate evaluations      : 692
ESCALATED             : 45 / 692 = 6.5%

-- why the gate stayed shut --
  confident            613  (88.6%)
  ESCALATED             45  (6.5%)
  refusal               34  (4.9%)      <- PARSE-NEG terminal refusals

-- confidence distribution --
  conf=0.50   73     conf=0.55    6     conf=0.75    2
  conf=0.80   88     conf=0.90  216     conf=0.95  291     conf=1.00  16
```

Per action: `unknown` 39/73 escalate, `attack` 4/71, `charge` 2/15. **Nothing
else ever escalates.** The distribution is bimodal — 0.50/0.55 (79 evaluations)
and 0.80/0.90/0.95 (595). Only 2 evaluations in the whole corpus sit in
0.56–0.79, so the gate's exact value is nearly irrelevant between 0.6 and 0.79.

`CommandParser.parse` also fires the CR-2 forced retry 5 times over the corpus
(`nay attack wellinton`, `Wittgenstein, attack Mack`, `Murat, attack Wellington`,
`Murat, charge`, `Grouchy, charge`) — 4 of those 5 *also* escalated at the gate,
so those requests would make two calls.

### 1b. Real play — 3.4%, and 0% on a France that is simply being played

`p1b_playtest_distribution.py` over every command string in
`tools/playtest_scripts/*.json` (1,416 commands, 31 arms):

```
ESCALATED: 48/1416 = 3.39%
reasons: {'confident': 1358, 'ESCALATED': 48, 'refusal': 10}
```

Per arm, the escalation is concentrated entirely in the deliberately-odd arms:

| arm | escalation rate |
|---|---|
| `weird_live_voice2` | 15/31 = 48.4% |
| `weird_live_voice` | 11/30 = 36.7% |
| `np_campaign_live` | 5/28 = 17.9% |
| `weird_absurdist` | 10/65 = 15.4% |
| `flagship_1805` | 1/44 = 2.3% |
| **`commanded_full40`** | **0/160 = 0.0%** |
| **`commanded_spender40`** | **0/173 = 0.0%** |
| **`volte_court_austria`** | **0/196 = 0.0%** |
| `weird_tyrant`, `weird_merchant`, `weird_admiral`, `weird_kingmaker`, `weird_pacifist`, `weird_world_burns`, `weird_eagle_in_chains`, all `win_campaign_*`, `np_campaign_{alone,emperor,seat}`, `diplomacy_latewar`, `vassal_probe`, `smoke_battle`, `naval_descent`(1/23) | 0.0% |

The three longest arms — the ones that represent a player *playing the campaign*
— are **529 commands with zero escalations**.

### 1c. The click road — 0%, structurally

`godot-client/project-sovereign/scripts/region_panel.gd:134/138` emits typed
commands (`order:<verb>:<Name>` → `"<Name>, <verb>"`, and `do:<full command>`),
and `strategic_ledger.gd:820` renders the Admiralty chips whose `command`
strings are authored in `backend/game_logic/naval.py:2761–2862`. I transcribed
all 22 verbatim and ran them:

```
=== chips: 22 commands, 22 gate evaluations ===
ESCALATED: 0/22 = 0.00%
  confidence: {'0.8': 4, '0.9': 16, '0.95': 2}
```

**A player who only clicks never reaches the model.** This is by construction —
the chips emit the exact canonical phrasings the fast parser was written around.

---

## 2. What does escalation actually rescue?

### 2a. ⚠ First, a provenance warning that limits every claim in this section

**All 17 committed cassettes are `provenance: "authored"`.** Not one was recorded
from the live API (`MANIFEST.json`, and confirmed per-file in p2). Their
`usage.input_tokens: 5000` is an authored placeholder, not a measurement.

So the cassettes are a **contract about what the pipeline does with a given model
answer**, not evidence of what the live model says. IQ-9's design is explicit
about this (the user promotes recorded cassettes with
`tools/record_parser_cassettes.py`), but it means: **this project has no
committed measurement of live model behaviour at all.** Everything below reads
"if the model answers thus, then…".

### 2b. The comparison, mock chain vs replay-armed chain

`p2_what_llm_rescues.py`, 16 parse cassettes, both worlds:

| category | count | rows |
|---|---|---|
| (a) **rescued** a real order the chain could not read | **10** | get-after, keep-an-eye, make-your-way, hit-the-Prussians-hard, harass-the-Austrians, ask-Austria, and the 3 delegations (but see §2c) |
| (b) same answer the chain already had | **4** | both `cover the retreat` rows, both `fix bayonets` rows — and here the corpus *wants* the refusal |
| (c) made it worse | **0** observed | — |
| (d) model answered correctly and we fell back anyway | **2** | `hunt down mack`, `Zorglub, attack Mack` |

Partial loss worth noting: on `demonym-harass` the model returned
`target="the Austrians"` and the pipeline's own resolution dropped it — final
`target=None`. The order executes against nobody named.

### 2c. ⛔ The headline: on a delegation, the model's answer is discarded entirely

This is the most decision-relevant finding in the report.

`backend/main.py` routes a CR-5 delegation on
`route_arm(_deleg.personality, parse_resolved_to_action(parsed))`. Read the two
executing arms:

- **cautious** → re-issues `f"{_deleg.marshal} scout {_deleg.scout_target}"` and
  re-parses it. The comment at the seam: *"This also corrects the live LLM's
  unreliable target resolution (playtest: 'deal with Kutuzov' mis-scouted
  Algarve); the detector's target is authoritative."*
- **aggressive** → re-issues `f"{_deleg.marshal} pursue {_deleg.target}"`. The
  comment: *"Deterministic (Golden Rule 6 — **the live LLM proved too flaky for
  delegation**, so mirror the cautious re-parse pattern)"*.

Both rebuild the order from `detect_delegation`'s own fields. The model's
`action`, `target` and `marshals` are never read. Only
`parse_resolved_to_action(parsed)` — a **boolean** — survives.

**Falsified by experiment** (`p3_delegation_one_bit.py`). Same utterance
`"Davout, deal with Mack"`, four cassettes whose model answers disagree wildly:

```
model says scout/Swabia   -> 'Davout scouts Swabia: ... cautious as ever, will reconnoiter'
model says FORTIFY/None   -> 'Davout scouts Swabia: ... cautious as ever, will reconnoiter'
model says MOVE/Portugal  -> 'Davout scouts Swabia: ... cautious as ever, will reconnoiter'   (marshals=["Ney"]!)
model says ATTACK/Mack    -> 'Davout scouts Swabia: ... cautious as ever, will reconnoiter'

DISTINCT OUTCOMES across 4 wildly different model answers: 1
```

Control — the same three-way disagreement on a NON-delegation
(`"Ney, get after Mack"`) gives **3 distinct outcomes**, so the probe is not
vacuous.

**Therefore: for the CR-5 delegation family — the flagship live-only feature —
a ~4,900-token call is made to produce one bit, and the code says in writing
that this is deliberate because the model was not reliable enough for anything
more.** Delegations are 3 of 27 unique corpus escalations and 5 of 35 unique
script escalations.

*(Correction to my own first reading: at parse level a literal delegation came
back as a successful `scout`, which looked like the prompt's literal rule being
ignored. It is not — `delegation.classify_arm` forces `ask` for a literal
regardless of what the model said, and `tests/test_iq9_keyless_parser_gate.py`
pins it. The literal arm is defended in code, not only in the prompt.)*

### 2d. The retry cannot reach the family it was built for

`p6` Q2. `"hunt down mack"` parses at **confidence 0.9** — above the gate, so no
escalation — and the fuzzy word-scan turns `down` into a Davout suggestion
(IQ9-X1). The CR-2 forced retry fires. The committed cassette's model answer is
**correct**: `pursue / Mack / PURSUE`.

```
mock outcome : ok=False  "Did you mean 'Davout'? ('down' not found)"
LIVE outcome : ok=False  "Did you mean 'Davout'? ('down' not found)"
live calls made: 1
```

Mechanism: `CommandParser._parse_text` re-runs `_apply_fuzzy_matching(retried,
effective_text, …)` on the **same raw text**, which hits `down` again, so
`retry_error` is non-None and the original error stands. **A paid call is made
and its answer is thrown away.** This is structural, not a tuning problem.

---

## 3. What does it cost?

### 3a. Tokens (`p4_cost.py`, measured on the 1805 boot world)

| component | chars | ~tokens (chars/4) |
|---|---|---|
| system prompt (`build_system_prompt`) | 177 | 44 |
| user prompt, 1805 (`build_parse_prompt`) | 16,582 | 4,145 |
| user prompt, legacy | 14,833 | 3,708 |
| tool schema (`PARSE_TOOL`, 15 properties) | 2,860 | 715 |
| **total input, one 1805 parse call** | **19,619** | **≈ 4,904** |

The Berthier recovery body is far smaller (~1,798 chars ≈ 450 tokens, from the
recovery cassette).

Growth with command history (`get_command_history_for_prompt`, last-5 window,
supplied at `providers.py:619`): **+355 chars at one command, +475 at six** —
reproducing the replay harness's own recorded +355 figure. The prompt is
essentially flat; it is the 126-province world block that dominates.

### 3b. Calls per request — the memo is wrong by a factor of two

`docs/audits/LLM_MONETIZATION_RESEARCH_2026_08_14.md` §1 states the parser
fallback is *"≤1 call per typed command, only below the confidence gate,
~$0.003 a call"*, and its cost table bills *"One LLM-routed command | 1 |
$0.003"*.

Measured (`p10_calls_per_request.py`, counting every `(kind, utterance, world)`
the replay client is asked for on the real endpoint):

```
'flurble the wibble'   TOTAL_ATTEMPTED=2     (parse + Berthier recovery)
'hunt down mack'       TOTAL_ATTEMPTED=1     (CR-2 retry only)
'Ney, deal with Mack'  TOTAL_ATTEMPTED=1     (parse only)
'Ney, attack Mack'     TOTAL_ATTEMPTED=0     (confident — no call at all)
```

**Any command the parser cannot read costs 2 calls, not 1.** I then tried to
construct 3 (`p11_three_calls.py`) across three shapes — invalid action,
non-existent marshal, gibberish — and got **2 every time**: the third is
prevented by `reparse_with_llm`'s `llm_error` guard plus its
`mode == "mock"` precondition (a successful live parse stamps `anthropic`, so
the retry is ineligible). *I proved the ceiling is 2 in four constructions; I
did NOT prove 3 is unreachable in all cases — mark that UNVERIFIED.*

### 3c. Latency — UNVERIFIED by measurement, bounded by config

I made no live call, so I have no latency measurement. The config
(`backend/ai/providers.py`):

- `REQUEST_TIMEOUT_SECONDS = 5.0`, split as `anthropic.Timeout(5.0,
  connect=2.0, pool=1.0)`;
- `MAX_RETRIES = 1`, and the comment states the measured ceiling: *"At timeout
  5s and one retry the ceiling is ~11s including backoff — noticeable but
  survivable"*, and *"CR-3 measured on claude-haiku-4-5 with the ~5K-token 1805
  prompt: live parse calls complete in 1-3s"*.

**Consequence of §3b that is not documented anywhere:** because an unparseable
command makes two calls, its worst case is **~22s of blocking wall time**, not
the ~11s the constant's own comment asserts. That ceiling lands on exactly the
command the player is most confused by.

### 3d. The memo's cost model, corrected

The memo assumes **25% routing** ("2-hour session (25% routing) | 30 calls |
$0.09"; "~$0.045 per play-hour"). Measured routing on played commands is
**3.39%**, and **0%** on the arms that play a full campaign.

Adjusting the memo's own model by the two measured corrections
(routing 25% → 3.4%, calls 1 → 2 on a routed command):
0.25 → 0.034 is ×0.136, doubled for the call count is **×0.27** →
**~$0.024 a session, ~$0.012 a play-hour** — estimate, derived from the memo's
own per-call price, not independently measured.

**This cuts both ways and the second half matters more:** escalation is roughly
four times *cheaper* than the plan of record assumed, and also roughly seven
times *rarer*. Cost is not the reason to question it. Value is.

---

## 4. What breaks when it is off?

The shipped default is mock. `deploy/launch.bat` (the tracked launcher) reads
`config.txt`, treats `your_key_here` as absent, and sets `LLM_MODE=mock` when no
key is present, `anthropic` when one is. BYOK is also armable in-client via
`/config/llm`. **So most players never reach the model.** *(Note:
`deploy/dist/ink_iron_server/launch.bat` still hardcodes `LLM_MODE=anthropic` —
that tree is the gitignored March 2026 build, four months stale, and CLAUDE.md
already says so.)*

`p12_keyless_player.py` runs each live-only behaviour at the real endpoint under
both roads:

| utterance | MOCK (shipped default) | BYOK (cassette) |
|---|---|---|
| `Ney, deal with Mack` | ASK clarification, **0 AP**: *"How shall this be done, Sire? … is Mack to be attacked, or observed?"* | aggressive arm: pursue, 1 AP, with a bad-odds warning |
| `Davout, deal with Mack` | same ASK, 0 AP | cautious arm: scouts Swabia, 1 AP |
| `Soult, deal with Mack` | *"Soult will not presume your meaning"* | **identical** (literal arm is code, §2c) |
| `Ney, get after Mack` | Berthier shrug, 0 AP | MUSTER against Mack, 1 AP — **a real rescue** |
| `ask Austria what they want` | shrug naming marshals | diplomatic advisory on Austria — **a real rescue** |
| `Ney, cover the retreat` | shrug | shrug (the corpus WANTS the shrug) |
| `Ney, fix bayonets` | shrug | shrug (same) |
| `flurble the wibble` | deterministic Berthier line | slightly better Berthier line |

**What the keyless player actually loses:**

1. **Nothing at all on the delegation family** — they get a real, in-fiction,
   free question and answer it. One extra round-trip. This is arguably a
   *better* design than the biased arm, because it never guesses.
2. **Real losses, two kinds:** (i) unusual but legitimate order phrasings
   (`get after`, `make your way to`, `keep an eye on`, `hit the Prussians hard`);
   (ii) free-text questions and diplomatic asks (`ask Austria what they want`).
3. **CR-5b flavour echoing** — live-only by construction, cosmetic by design
   (`ParseResult.flavor`, Golden Rule 6), dropped to a deterministic floor by
   `delegation.flavor_passes_register` whenever the line misbehaves.
4. Corpus coverage: **4 `live_only` rows** (2 CR-5 delegation, 2 FA-73), against
   **49 `mock_only`** rows. The corpus's own weight is on the mock chain.

### ⚠ A documented claim that does not reproduce

The corpus carries a `live_phrasing_backlog` block describing 18 phrasings as
*"Marshal-less strategic phrasings the keyword-seam tests cover but the MOCK
action chain cannot parse — live-LLM-only capabilities today."*

Measured (`p5` sweep D): **8 of the 18 are parsed by the mock chain, confidently,
today** — `link up with davout` → move/Davout (0.8), `follow and destroy
wellington` → attack/Wellington (0.9), `stand fast at belgium` → hold/Belgium
(0.9), `hold your ground` → hold (0.8), `rally to ney` → move/Ney (0.9), `come to
the aid of davout` (0.8), `bolster ney's position` (0.8), `combine with davout`
(0.8). All are above the gate, so **those 8 can never reach the model even with
a key** — the backlog is stale and describes capabilities the chain has since
grown. 10 still shrug; 3 of those 10 shrug because of the `down` collision, not
because the phrasing is hard.

---

## 5. Where is the gate wrong? (confident AND wrong)

A parse at or above 0.7 never escalates, so these are the expensive failures.
The golden corpus is green (686/686 mock) — everything below is *outside* its
coverage.

### 5a. Two systematic sweeps came back clean

`p5_confident_and_wrong.py`, on the shipped 1805 world:

- **A) all 126 provinces as a move destination** (`"Ney, move to <Province>"`):
  **0 resolved to the wrong place.**
- **B) every French marshal as an addressee** (`"<Marshal>, fortify"`, both
  worlds): **0 mis-addressed.**

The WO slice-10 hardening holds. Good news worth stating plainly.

### 5b. ⛔ NEW — the "retreat as a noun" family: the player's own marshal marches away

`p9_retreat_noun.py`. `Lannes` starts at Franche-Comte:

```
conf=0.9  RETREATED  'Lannes, cut down the retreat'                 -> Lorraine
conf=0.9  RETREATED  'Lannes, cut off the retreat'                  -> Lorraine
conf=0.9  RETREATED  'Lannes, press the retreat'                    -> Lorraine
conf=0.9  RETREATED  'Lannes, block the retreat'                    -> Lorraine
conf=0.9  RETREATED  'Lannes, exploit the retreat'                  -> Lorraine
conf=0.9  RETREATED  'Lannes, punish the retreat'                   -> Lorraine
conf=0.9  RETREATED  'Lannes, ride down the retreating Austrians'   -> Lorraine
conf=0.9  refused    'Lannes, harry the retreat'
conf=0.5  refused    'Lannes, cover the retreat'          <- the ONLY pinned member
```

**6–7 of 11 phrasings, measured on pristine HEAD across four runs.** The listing
above is the working-tree run; on pristine HEAD `cut down`, `cut off`, `press`,
`block`, `exploit`, `punish` and `ride down the retreating Austrians` all retreat
at 0.9, while the total oscillates 6–7 between runs — one row's retreat is
sometimes refused and **I did not isolate which ambient condition decides it**
(mark that UNVERIFIED; the confidence, 0.9 on every row, is stable). Full effect
(`p8_two_cases.py`, working tree; the same sentence retreats on pristine too):

> `'Lannes, cut down the retreat'` — conf 0.9, model never asked, **success=True**,
> Franche-Comte → Lorraine, **"Army begins recovery (currently at -45%
> effectiveness). Will recover over 3 turns."**, at **0 AP**.

The seam is exact. `backend/ai/llm_client.py:1897` fires on the bare substring
`"retreat"`, guarded only by `_mentions_screening_idiom` (`:616`), whose regex is
an **allowlist of four verbs**: `\b(?:cover|screen|protect|shield)\s+(?:the|our|
his|their|her)\s+(?:retreat|withdrawal|rear|army|corps|flank)\b`.

That guard's own docstring predicted this exactly:

> *"The retreat branch fired on the bare substring 'retreat'/'withdraw' and
> stamped confidence 0.9, **which is above the LLM-fallback gate, so live mode
> could never correct it**: the player asked Ney to screen the army and Ney
> retreated, spending the AP."*

The July-18 fix understood the failure mode and closed it with four verbs.
`cut down`, `cut off`, `press`, `block`, `exploit`, `punish` and
`ride down the retreating` are the same defect one word over. FA-73 (`BUG_FIXES.md:7581`)
pins `cover the retreat` — the *below-gate* member — and nothing pins the rest.

**Confirmed identical with a key:** a replay client holding zero cassettes (any
call would raise) completes the request unchanged, so BYOK does not help.

### 5c. ⛔ NEW — a question commits the whole army

`p17_question_executes.py`:

```
EXECUTED  conf=0.9   AP 4->3  'is Swabia defended'
  'All forces take defensive positions: Ney, Davout, Soult, Lannes, Murat,
   Bernadotte, Massena, Napoleon'
answered  conf=0.8   AP 4->4  'is Swabia defended?'
```

**The question mark is load-bearing.** Without it, an eight-marshal army-wide
defend executes at 1 AP. FA slice 7 landed a subject rule for
`will`/`would`/`shall`; `is`/`are`/`has`/`did` are not covered, and the guard
that does fire needs the `?`.

Second observation from the same probe: **nine `?`-terminated questions all
return the COMMAND REFERENCE help dump** at confidence 0.8 — `will Ney attack
Mack?`, `is Ney fortified?`, `has Davout drilled?`, `is Paris garrisoned?`, `did
Ney retreat?`, `should we recruit more infantry?` … That is FA slice 7's designed
refusal ("polite modal orders sent to the manual"), but it is above the gate, so
neither the FACT desk nor the model is ever consulted. `backend/ai/question_desk.py`
does answer `where is Mack`, `how strong is Ney`, `how many men does Mack have`
(all → `status`, 0.9) — so the desk works, it just isn't reached by these forms.

### 5d. Word collisions — real, but narrower than they look

`p6`, 93 ordinary military-English words in the marshal-less frame
`"hunt <word> mack"`:

```
down  conf=0.9  -> "Did you mean 'Davout'?"
near  conf=0.9  -> "Did you mean 'Ney'?"
sit   conf=0.9  -> "Did you mean 'Soult'?"
slow  conf=0.9  -> "Did you mean 'Soult'?"
soon  conf=0.9  -> "Did you mean 'Soult'?"
```

All five above the gate. **But `p7` corrects the severity**: with an addressed
marshal the collision does not fire — `"Ney, hunt down Mack"` parses correctly
at 0.95 and pursues Mack. The family needs a *marshal-less* sentence. Its harm
is a wrong-but-honest refusal, not a wrong order. One addressee-position hit,
`"south, attack Mack"` → commands **Soult** at 0.55 — below the gate, so live
mode *would* consult the model; in mock it executes. I grade this P4: the
sentence is unnatural.

### 5e. Confirmed still live, already documented

`"Ney, attack Brunswick"` at conf 0.95 targets the Prussian **marshal**
Brunswick (standing at Berlin) rather than the province. This is the one
survivor WO slice-10 recorded by name ("every survivor the exact `Brunswick`") —
reported as **confirmed**, not new.

### 5f. ⛔ Moving the gate cannot fix any of this

`p15_gate_sensitivity.py` walks the gate over the measured distribution:

| gate | escalating | % of all commands | catches the 0.90 defects? |
|---|---|---|---|
| 0.55 | 39 | 5.6% | no |
| **0.70 (shipped)** | **45** | **6.5%** | **no** |
| 0.76 | 47 | 6.8% | no |
| 0.85 | 135 | 19.5% | no |
| **0.91** | **351** | **50.7%** | **YES** |
| 0.96 | 642 | 92.8% | YES |

Every defect in §5b/5c/5e sits at 0.90–0.95. **To reach them the gate must
exceed 0.90, which escalates half of all commands — an ~8× increase in calls,
latency and cost, to catch a family that widening one regex fixes for free.**
And lowering the gate is nearly a no-op: only 2 of 692 evaluations lie between
0.56 and 0.79.

---

## 6. The ruling

### Recommendation: **(iv) — keep escalation, but re-aim it, and stop paying for the delegation bit.**

Not (v) drop it: two rescue classes are real and measured (§4) — unusual order
phrasings, and free-text questions/diplomatic asks. Not (i) keep as is: 86% of
what the gate catches is a sentence that should be refused, and the flagship
consumer discards the answer. Not (ii): §5f shows the gate cannot reach the
defects at any survivable setting.

| option | build cost | measured expected gain | verdict |
|---|---|---|---|
| **(i) keep as is** | 0 | 3.4% of commands routed; 86% of them want a refusal; the delegation call buys 1 bit | **no** |
| **(ii) raise/lower the gate** | ~0.25 session | lower: +0.3% routing (2 rows). raise past 0.90: 50.7% routing for the §5b/5c family | **no** — §5f |
| **(iii) escalate on ambiguity, not confidence** | ~1.5 sessions | would have to *raise* the score of `cut down the retreat`, which is keyword-unambiguous — it is confidently wrong, not ambiguous. Does not reach the measured defects | **no** |
| **(iv) re-aim at what the chain cannot do** | **~1.5–2 sessions** (see below) | removes ~1 call per delegation; makes the two real rescue classes reachable; ends "a paid call whose answer is discarded" | **YES** |
| **(v) drop it** | ~0.5 session | loses §4's two rescue classes; keyless play already works | not yet — see the re-open condition |

### The four changes, in order of measured value per session

1. **Stop calling the model for a delegation** (~0.25 session). `detect_delegation`
   already owns the marshal, the target and the scout target;
   `classify_arm`/`route_arm` own the personality. The only thing the call
   supplies is `parse_resolved_to_action`'s boolean, and §2c proves nothing else
   survives. Replace that boolean with a deterministic predicate (the delegation
   was detected and its target resolved) and the aggressive/cautious arms become
   available to the **keyless** player too — which is a *feature gain*, not just
   a saving. ⚠ This changes player-visible behaviour for mock players (guardrail
   (e) currently forces ASK in mock **by design**, `delegation.parse_resolved_to_action`
   docstring) — so it is a design decision, not a refactor, and needs the CR gate.
2. **Fix the two confident-and-wrong families first** (~0.5 session, no LLM
   involved). §5b: widen `_mentions_screening_idiom` from an allowlist of four
   verbs to the shape *"a verb + `the retreat/withdrawal` as an OBJECT"*, or
   better, demote any `retreat`-bearing sentence with a transitive verb before
   it to below-gate. §5c: extend FA slice 7's subject rule from
   `will/would/shall` to `is/are/was/has/have/did/does`, with and without the
   `?`. Both are worth more than any routing change: they are wrong *orders*,
   not wrong refusals.
3. **Route questions to the desk, then to the model** (~0.75 session). §5c shows
   nine question forms hitting the help dump at 0.8 while
   `backend/ai/question_desk.py` exists and answers the `where/how strong/how
   many` forms. Give the desk the copular and perfect forms; escalate only what
   the desk cannot answer. This is the one place where a model adds something
   the chain structurally cannot do — open-ended questions — and it is currently
   unreachable because 0.8 > 0.7.
4. **Make the CR-2 retry able to win** (~0.25 session). §2d: the retry re-runs
   fuzzy matching over the *same raw text*, so the collision that caused the
   error recurs and the model's correct answer is discarded. If the retried
   parse names a valid marshal explicitly, the fuzzy pass should trust it rather
   than re-scanning the raw words. Otherwise delete the retry — it currently
   costs calls it cannot convert.

### ⚠ Overlap with work already in flight

A sibling agent in this workflow has `backend/ai/clause_guards.py` +
`backend/ai/llm_client.py` modified in the working tree under the banner
**"CX slice 1 — A QUESTION NEVER ORDERS"**: it adds `has`/`had` to
`_INTERROGATIVE_LEAD_SRC`, deliberately excludes `have` (the causative
imperative "have Ney attack Mack"), makes `who|whom|whose|why` a question on
their own, and threads a fog-honest third-party roster through `is_question` so
*"can Ney attack Mack"* asks while *"can you attack Mack"* commands. Their
recorded findings (`why not attack Mack` fighting a real battle; `why not
retreat` retreating the whole army) are the same class as my §5c.

**Two things follow.** (1) Recommendation #3's question half is largely theirs —
do not build it twice; my §5c case should be handed to that slice. (2) **Their
change as it stands in the working tree does NOT fix my case**: I re-ran `p17`
against the modified tree and `is Swabia defended` (no `?`) still EXECUTES a
whole-army defend at conf 0.9, spending 1 AP. A copular lead with no `?` and a
PROVINCE (not a marshal) as subject is outside their rule. Worth one line in
their slice.

### The re-open condition

**If, after changes 1–4, a recorded-cassette measurement (not an authored one)
of one played campaign shows the model rescuing fewer than 1 command in 200, drop
escalation entirely and ship mock-only + the local-model spike (HC-L).** The
instrument for that measurement already exists — `tools/record_parser_cassettes.py`
plus `parser_eval --replay` — and using it once would also retire the
provenance warning in §2a, which is the single biggest gap in this report.

### Two documented claims this recon corrects

1. `docs/audits/LLM_MONETIZATION_RESEARCH_2026_08_14.md` §1: *"≤1 call per typed
   command"* → **measured 2** on any unparseable command (§3b), and its 25%
   routing assumption measures **3.39%** (§1b). The dollar conclusion
   ("$0.09/session") is ~4× high and its architectural conclusion survives
   comfortably.
2. `tests/data/parser_golden_corpus.json` → `live_phrasing_backlog`: *"the MOCK
   action chain cannot parse"* → **8 of 18 are parsed confidently today** and can
   never reach the model (§4).

### Method notes / limits (stated, not buried)

- **No live call was made.** Every "the model said X" is an authored cassette.
- **I could not measure latency.** §3c is config plus the code's own recorded
  CR-3 measurement.
- **My own probe-4 text claimed a 3-call worst case** from reading the code;
  `p11` then measured 2 in four constructions and found the guard that prevents
  the third. The claim is corrected above; "3 is impossible" stays UNVERIFIED.
- **My first taxonomy of escalating utterances was crude** (a regex mis-filed
  `"Ney, take Vienna"` as a non-command), so §2/§5 use the corpus's own
  `expected` blocks as ground truth instead (`p14`) — non-subjective.
- The 0% chip-road figure covers the 22 chip strings I transcribed from
  `region_panel.gd` / `marshal_management.gd` / `naval.py`; I did not
  exhaustively enumerate every dynamic chip the client can build.

### Probes (all runnable, all keyless)

`scratchpad/cx_recon/probes/` — `p1_escalation_rate.py`,
`p1b_playtest_distribution.py`, `p2_what_llm_rescues.py`,
`p3_delegation_one_bit.py`, `p4_cost.py`, `p5_confident_and_wrong.py`,
`p6_retry_cannot_rescue.py`, `p7_realistic_sentences.py`, `p8_two_cases.py`,
`p9_retreat_noun.py`, `p10_calls_per_request.py`, `p11_three_calls.py`,
`p12_keyless_player.py`, `p13_escalation_taxonomy.py`,
`p14_what_should_happen.py`, `p15_gate_sensitivity.py`, `p16_questions.py`,
`p17_question_executes.py`.
