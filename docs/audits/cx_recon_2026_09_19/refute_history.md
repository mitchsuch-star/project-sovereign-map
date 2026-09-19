# REFUTATION — the "history" census (`prior_rulings.md`)

**Read-only adversarial pass, September 19, 2026, at master `f7008582`** (the
working tree carries a concurrent writer — see REFUTE:CX-N6). Default verdict was
REFUTED. Every number below is either a `file:line` I opened myself or the output
of a probe under `probes/refute/`. Nothing under `backend/`, `godot-client/`,
`tests/`, `docs/` or `tools/` was modified; no git-mutating command was run; no
network call was made.

---

## 0. The one-paragraph answer

**The census's arithmetic is good and its diagnosis is not.** Every headline
number I could re-derive reproduced to the row — 111/447, 24.8%, 88.3/6.4/5.4,
8-of-18, 2,860/177/16,582 chars, Haiku 4.5's 4096-token floor. But the headline
claim — *"a CX row's real scope is one client seam … and yesterday's fix opened a
hole in it that the fence's own drift pin is structurally unable to see"* — rests
on a test the census never found. `tests/test_wo_slice7_cabinet_door.py` contains
**`class TestTheCorpusCensus`** (line 285), which runs the fence over the whole
golden corpus **in both directions**, using keyword lists regex-extracted from the
real `.gd`. Measured today: of the 111 claimed rows, **105 are diplomatic orders,
6 are the corpus's own capped "underspecified" bucket, and ZERO are
non-diplomatic** — and **zero** diplomatic-order rows go unclaimed. The fence is
on contract in both directions. IQ10-6's hole is real, but it is **one missing
golden-corpus row**, not a structural blindness: I wrote the row an IQ-10 author
would have written and the existing census turns RED on it. The census looked at
the corpus and at the client and never looked at **the game's own printed copy** —
which is where the two live defects actually are (MISSED-1, MISSED-2).

---

## 1. Verdicts on the filed findings

### REFUTE:CX-N1 — **NARROWED** (mechanism real; magnitude, diagnosis and citation all wrong)

**What reproduces.** `gather intel on` and `gather intelligence on` are both
parser keywords (`backend/ai/llm_client.py:1592` — the census's `:1574` is now
stale by 18 lines, see CX-N6). `DIPLO_FAMILY_KEYWORDS` (`main.gd:1665`) carries
only the short form. Run through the **repo's own mirror**
(`tests/test_wo_slice7_cabinet_door.py::_redirect_verdict`, lists extracted from
the live `.gd`), `probes/refute/r1_fence.py`:

```
'gather intel on Austria'          -> 'cabinet'   (redirected, nothing sent)
'gather intelligence on Austria'   -> ''          (passes to the backend)
```

**Three sub-claims are wrong.**

1. **"the long form … EXECUTES the mission" is FALSE.** Driven at the real
   production seam (`POST /command`, shipped 1805 board;
   `probes/refute/r3_drive.py`, `r5_dialogue.py`): the response carries
   `diplomatic_dialogue.type == "mission"` with options
   `["Begin mission", "Not now"]` and `blocking: false`, and
   `world.active_diplomatic_mission` is **still `None`** afterwards. A follow-up
   bare `yes` does not confirm it (`r4_confirm.py` — Berthier shrugs). Nothing is
   spent and nothing is committed. IQ-10's own pin asserts exactly this shape
   (`test_every_form_reaches_the_mission` asserts `dlg["type"] == "mission"` plus
   a `start_mission` option) — so the census's magnitude is contradicted by the
   commit it is about.
2. **"the fence's own drift pin is structurally unable to see it" is FALSE.** The
   cited `TestTheMirrorAgreesWithTheParser` (78-entry hand list — that detail is
   right) is not the fence's only guard.
   `TestTheCorpusCensus::test_every_family_utterance_is_claimed` (line 287) is a
   corpus-wide census. `probes/refute/r2_iq10.py` builds the row an IQ-10 author
   would have written —
   `{"utterance": "gather intelligence on Austria", "expected": {"type": "diplomatic", "diplo": {"mission_type": "GATHER_INTEL", ...}}}`
   — and measures `_row_class` = **`order`**, `_redirect_verdict` = **`''`**, so
   the existing test **REDs**. The guard is blind only because **IQ-10 added a
   parser keyword without a golden-corpus entry**: the corpus holds
   `gather intel on Austria`, `ambassador, gather intel on Austria` and
   `spy on Prussia`, and no long form.
3. **The citation is stale.** `:1574` → `:1592`, moved by the concurrent writer
   mid-session. Navigate by symbol.

**Severity P3, not P2. Fix = one corpus row + one `DIPLO_FAMILY_KEYWORDS` entry.**
The census's recommended fix ("replace `CANDIDATE_SENTENCES` with a census derived
from the parser's own vocabulary") would build a second copy of something that
already exists.

**Would the obvious fix ship a regression?** Adding `"gather intelligence on"` to
`DIPLO_FAMILY_KEYWORDS` steals no `read_only` corpus row (measured), so it is safe
— but it makes IQ-10's own stated win, *"the game's own printed sentence is
typable"*, player-invisible in the shipped client, because the short form is
redirected too. That contradiction between R20 and R2/G1 is the real row, and it
is MISSED-1.

---

### REFUTE:CX-N2 — **REFUTED as filed** (the arithmetic survives; the claim it supports does not)

**The number is exact.** `probes/refute/r1_fence.py`, using the repo's own mirror
rather than a re-port: **111 of 447 = 24.8%** claimed (110 cabinet + 1 war_room),
336 passthrough. Identical whether nation forms are built the way the test fixture
builds them (29) or the way the client actually builds them (30).

**The claim is refuted three ways.**

1. **"no test compares the two vocabularies except through a hand list" is FALSE.**
   `TestTheCorpusCensus` holds `test_every_family_utterance_is_claimed`,
   `test_no_non_diplomatic_utterance_is_intercepted`,
   `test_request_terms_goes_to_the_war_room_not_the_cabinet` and
   `test_every_underspecified_row_has_an_explicit_verdict` — four corpus-wide
   assertions over lists regex-extracted from `main.gd` and courts read from
   `utils.gd`. Plus `TestEveryDiplomaticVerbIsDisposed` (line 472), an
   action-level census with its own corpus-witness test. The census report cites
   none of them.
2. **The composition is the contract, not a leak.** Measured class breakdown of
   the 111: **`order` 105 · `underspecified` 6 · `read_only` 0**, and **ORDER rows
   the fence does NOT claim: 0**. Zero false positives, zero backdoors. "Eats a
   quarter of the corpus" is a description of G1 working.
3. **The report contradicts itself.** Its own §4 F2 says *"Not filed as a defect
   here — it may be exactly what G1 intends"*; the finding list files it P2.

**Minor magnitude error.** "156 keyword phrases across 7 tables" undercounts: the
ten tables the fence actually reads hold **189** phrases (no_home 18 / war_room 2 /
family 115 / gated 2 / anywhere 13 / address_names 6 / **address_exempt 20** /
**advisory_starts 7** / **autonomy_verbs 3** / **autonomy_levels 3**). The three
omitted tables are the *exempting* ones — the half that keeps the fence from
over-firing. "30 nation forms" is exactly right for the client.

**What survives, downgraded to INFO:** the golden corpus is not a measure of the
typed road a player walks, because a quarter of it is redirected before it is sent.
That is a sentence for `docs/PLAYTESTING.md`, not a P2 row.

---

### REFUTE:CX-N3 — **SURVIVES**, magnitude cut to P4

The article asymmetry reproduces exactly (`r1_fence.py`):

```
'cede Tyrol to Kingdom of Italy'      -> 'cabinet'
'cede Tyrol to the Kingdom of Italy'  -> ''
'grant Tyrol to Bavaria'              -> 'cabinet'
'Talleyrand, grant the petition'      -> 'cabinet'
'grant relief to Holland'             -> 'cabinet'   <- a case the census missed:
                                                        IQ-7's OTHER answer verb
```

`_names_court_after_to` (`main.gd:2091`) tests `" to " + form`, so `" to the …"`
never matches. The citation checks out: the IQ-7 R1 test does type the
article-bearing form through TestClient
(`tests/test_iq7_review_round.py::TestR1TheDeedFulfilsThePetition::test_the_typed_cede_then_the_lapse_honours_the_petition_once`,
`_cmd(client, "cede Tyrol to the Kingdom of Italy")`).

**Magnitude is over-stated, because CX-N9 is answerable from source.** While any
`_post_hud_response_routes` modal is standing the command input is
`editable = false`, so the typed road and the petition card are mutually exclusive
by construction (see CX-N9 below). The asymmetry is reachable only on the deferred
/ letter-book road, where the petition persists in world state across turns. Real,
small, **P4**.

---

### REFUTE:CX-N4 — **SURVIVES on the number, NARROWED on the reasoning**

**Confirmed against the authoritative reference** (the Anthropic prompt-caching
minimum-cacheable-prefix table): **Haiku 4.5 = 4096 tokens**, and the minimum is
non-monotonic — 512 on Opus 5, 1024 on Opus 4.8 / Sonnet 5, 2048 on Opus 4.7,
**4096 on Opus 4.6, Opus 4.5 and Haiku 4.5**. `docs/STATUS.md`'s "2048-token
minimum cacheable prefix" is wrong. The char counts reproduce exactly and
independently (`probes/refute/r15_prompt.py`): PARSE_TOOL **2,860**, system
**177**, user prompt **16,582**.

**But the claim the census says "HOLDS and is confirmed" is FALSE.** It states
that *"the ~15,900-char tail (`## Valid Actions` through `## Examples`) is static
per boot"*. The per-section map says otherwise:

```
@   36 len=  399  ## Your Marshals (French)      <- volatile
@  435 len=  202  ## Enemy Forces                <- volatile
@  637 len= 1248  ## Valid Actions
     ... 11,915 chars of static instruction ...
@12555 len=   43  ## Command to Parse            <- VOLATILE, inside the "static tail"
@12598 len=  561  ## Output
@13159 len= 3423  ## Examples
```

The player's own utterance sits at char 12,555, **inside** the range the census
calls static — and caching is a **prefix** match, so a static *suffix* is not
cacheable at all. Today's genuine cacheable prefix is `tools + system + 36 chars`
= **768–854 est. tokens**, about 5× below the floor. After the full restructure
the census itself admits is needed, the contiguous static prefix is **18,975 chars
= 4,744–5,271 est. tokens**, which clears 4096 — so the direction is right, but
"just over the floor" is reached by a route that does not exist today.

**The argument neither the record nor the census made — and it settles it.**
Priced on `claude-haiku-4-5` at $1.00/MTok input (`r18_final.py`):

| | per escalating call | per 1,000 escalations |
|---|---:|---:|
| 4,905–5,450 est. input tokens | **$0.0049–$0.0055** | **$4.90–$5.45** |

Break-even on the 5-minute TTL is **two requests inside five minutes** (write
1.25× + read 0.1× vs 2× uncached). Escalation is measured at **6.4%** of
utterances (CX-N5), so consecutive escalations inside one TTL window are the
exception, not the rule. The whole prize is single-digit dollars per thousand
escalations, in exchange for a prompt restructure that moves every few-shot
example. **The record's conclusion is not "marginal-but-arguable" — it is correct,
and now for a measured reason rather than an asserted one.** If cost is the goal
the lever is the 16.5K-char prompt itself, not caching it.

---

### REFUTE:CX-N5 — **SURVIVES, exact** (with one readability trap and one unverifiable clause)

Re-derived at the real gate — `LLMClient.fast_parse` → `_should_fallback_to_llm`,
with the pre-parse typo repair applied exactly as `CommandParser.parse` applies it
(`probes/refute/r12_pr.py`):

```
[legacy] rows=300  confident=266 (88.7%)  escalates=21 (7.0%)  refusal_terminal=13 (4.3%)
[1805]   rows=392  confident=346 (88.3%)  escalates=25 (6.4%)  refusal_terminal=21 (5.4%)
   of the 25 escalating rows, expected.success is False for 21
```

Every figure matches the census to the row.

**Trap worth recording on the row:** the two 21s are **different sets** — 21
refusal-terminal rows (which by R3 never escalate) and 21 of the 25 *escalating*
rows that expect failure. The sentence reads like a conflation and is not one.

**One clause is UNVERIFIED and over-stated:** *"each costing two live calls"*. The
second call is the Berthier recovery, which fires only when the LIVE parse also
fails. Rows like `Ney, cover the retreat` and `Ney, fix bayonets` are FA-S7-D1's
case — the live model returns a **wrong action** (a cavalry charge), which is one
call, not two. Only true gibberish (`xyzzy foobar`, `dance with the moon`) pays
twice. Unmeasurable keyless; it should be marked UNVERIFIED, not asserted.

The census's own honest limit stands and is the most important sentence in the
whole report: the corpus was mined from parser tests, so **6.4% is not a
player-input rate**, and no ruling on "is routing to the LLM worth it" can rest on
it.

---

### REFUTE:CX-N6 — **NARROWED / STALE** (a second file has since changed)

The concurrent writer has moved on. `git status --porcelain` now reports **two**
modified files, not one:

```
 M backend/ai/clause_guards.py
 M backend/ai/llm_client.py      (+22/-1)
```

`llm_client.py` gains `_question_subjects(game_state)` — a fog-honest roster built
from `marshals` plus `_askable_enemy_names` (Golden Rule 5) — threaded into
**both** `is_question` call sites, so *"can Ney attack Mack"* asks while *"can you
attack Mack"* commands. The census's "0 of 447 corpus utterances change verdict"
was measured on `is_question` **alone**, before this landed, so the claim needs
re-dating.

**The numbers do survive, re-measured on the current tree:**
`.venv/Scripts/python.exe -m backend.ai.parser_eval` → **686/686 passed**, and my
escalation buckets reproduce the census's figures exactly. So the conclusion holds
— but it is now an independent confirmation rather than the census's measurement,
and the census's own cited line number is a casualty of it.

---

### REFUTE:CX-N7 — **SURVIVES on the count, NARROWED on the conclusion**

`probes/refute/r13_backlog.py` reproduces exactly: **8 of 18 on 1805, 7 of 18 on
legacy**, the same eight utterances.

**But "shipped capability" is not what ships.** Driven through `POST /command` on
the shipped board (`r14_backlog_live.py`):

```
link up with davout           -> "Which marshal shall support Davout, Sire?"
rally to ney                  -> "Which marshal shall support Ney, Sire?"
come to the aid of davout     -> "Which marshal shall support Davout, Sire?"
bolster ney's position        -> "Which marshal shall support Ney, Sire?"
combine with davout           -> "Which marshal shall support Davout, Sire?"
stand fast at belgium         -> "Which marshal shall hold Belgium, Sire?"
hold your ground              -> "Which marshal shall hold, Sire?"
follow and destroy wellington -> FAILS: "Region 'Wellington' not found. Nearby: Berlin, Lisbon, London"
```

Seven of the eight carry `marshal=None` and land on the **CR-2 clarification** —
they ask, they do not execute, which is the designed behaviour for a marshal-less
phrasing (and the SUPPORT semantics genuinely did land: the clarification says
*support*, while the raw parse says `move`). The eighth is legacy-only — Wellington
is not on the 1805 roster — and on the shipped board it degrades into a **region**
lookup that answers a person's name with three cities. So the honest count on the
board that ships is **7, not 8**, and what is unpinned is the clarification path,
not eight executing orders.

P4 stands; the fix (promote the seven into corpus rows) is right.

---

### REFUTE:CX-N8 — **SURVIVES**, and is stronger than filed

- `backend/ai/validation.py:413` still returns
  `"Multi-marshal commands coming in a future update!"`; grep of `tests/` for that
  string returns **zero**.
- **Reachability proved, which the census asserted but did not show:**
  `PARSE_TOOL.input_schema.properties` contains `marshals`, and `marshals` is in
  `required`. Under forced tool use the live model is *obliged* to emit the field,
  so `len(result.marshals) > 1` is genuinely live-reachable — the row is a live
  "coming soon" promise with an owner and no landing slice, as filed.
- **R158 confirmed unbuilt:** `grep -rn "parse_mode\|parse_confidence"` over the
  whole `godot-client/` tree returns nothing, while `backend/main.py:568-569`
  stamps both onto every response.
- **One narrowing:** `parse_multiple` (`backend/commands/parser.py:2204`) is
  production-dead — its only in-`backend/` caller is the `__main__` demo at
  `:2356` — but it is **not untested**:
  `tests/test_command_robustness_cr0_parser_rosters.py:571` and
  `tests/test_systems_audit_v2_session5.py` both drive it, and corpus row
  `ney-and-davout-attack-wellington` documents the path (`world: "legacy"`, so it
  never runs on the shipped board).

---

### REFUTE:CX-N9 — **REFUTED as "unverifiable"; answered from source, no client run needed**

The census says *"whether a petition popup calls `set_input_enabled(false)` could
not be settled without running the Godot client … One client run settles it."* It
is settled by reading three places:

1. `main.gd:1606` — `_execute_command` calls `set_input_enabled(false)` before
   every send, and `set_input_enabled` sets `command_input.editable = enabled`.
2. `scripts/marshal_petition_dialog.gd`, file header, verbatim: *"The card is
   shown from `_post_hud_response_routes`, and EVERY entry there returns before
   `set_input_enabled(true)` — so deferring the petition left the command line,
   Send, End Turn and the diplomacy wizard permanently disabled with no recovery
   path short of reloading."*
3. `main.gd:2190`'s own comment repeats it, and `main.gd:417-424` connects
   `petition_deferred` **because** of it: *"the shower does not hand control back,
   the dismiss handler does."*

So **while any `_post_hud_response_routes` modal is standing — petition, capture
choice, incoming proposal, incoming settlement offer, commitment paradox,
diplomatic objection — the command input is not editable.** The fence cannot fire
under a modal because nothing can be typed. This is a construction fact, and it is
why CX-N3's severity is P4 and not P2.

---

## 2. What the census MISSED

It measured the corpus and it measured the client. It never measured **the game's
own printed copy** — which is where the live defects are.

### MISSED:1 — **P2. The Berthier shrug, the game's most-seen failure surface, teaches a sentence the client refuses to send.**

`backend/ai/llm_client.py:1259`. Driven live in mock mode
(`probes/refute/r17_help.py`, `POST /command {"command": "xyzzy foobar"}`):

> *"Sire, I must confess this order eludes me," Berthier admits. "Shall I relay an
> order to Ney? Valid actions include: attack, move, scout, defend, fortify,
> recruit. **For diplomatic matters, try 'Talleyrand, propose alliance with
> Austria'**."*

Run through the fence mirror, `'Talleyrand, propose alliance with Austria'` →
**`cabinet`**. So every time a player mistypes anything, the game hands them a
sentence that, typed back verbatim, produces *"Matters of state are conducted at
the table, Sire — not by dispatch"* and sends nothing. This is R20 /
`SYSTEMS_REFERENCE.md` §49 (*a sentence the game PRINTS must be a sentence the
parser knows*) failing one layer out: the **parser** knows it; the **client**
refuses it. No test covers this producer.

### MISSED:2 — **P2. The help's DIPLOMACY block teaches four typed diplomatic orders the fence eats, and the test named `test_it_no_longer_teaches_the_typed_orders` is green about all four.**

Live `help` output (`r17_help.py`), all four claimed by the fence:

```
[cabinet] 'buy off Prussia'                            backend/commands/meta_executor.py:788
[cabinet] 'sponsor Prussia against Austria, 200 gold'  backend/commands/meta_executor.py:792
[cabinet] 'license Prussia against Austria'            backend/commands/meta_executor.py:794
[cabinet] 'guarantee Saxony'                           backend/commands/meta_executor.py:797
```

All four are the AI-2b D5 instrument verbs; all four sit in
`DIPLO_NATION_ANYWHERE_KEYWORDS`; and all four are inside the
`DIPLOMACY … SCREENS & HOTKEYS` block the guard's own fixture reads (verified:
`'buy off'`, `'sponsor'`, `'license'`, `'guarantee'` are all present in that
1,987-char block). The guard —
`tests/test_wo_slice7_cabinet_door.py::TestTheHelpTeachesTheDoor::test_it_no_longer_teaches_the_typed_orders`
— is a hand list of **eight literal strings** (`'"propose peace with'`,
`'"improve relations with'`, `'declare war /'`, `'"invest in Holland"'`,
`'"release Holland"'`, `'"cede Tyrol to Holland"'`, `'break treaty'`,
`'ultimatum'`). None of the four is on it.

**This is the hand-list failure the census went looking for — in the same test
file, at a seam it did not open.** The right fix for MISSED-1 and MISSED-2
together is one census: run every quoted command-shaped phrase the backend PRINTS
through the same `_redirect_verdict` mirror the corpus census already uses. That
is also the guard that would have caught IQ10-6.

### MISSED:3 — **P3. After a NA-6 Proclamation the fence stops recognising the name the game prints.**

`main.gd:2055` `_nation_forms()` builds `_diplo_nation_forms` once
(`if _diplo_nation_forms.is_empty()`) from `Utils.NATION_COLORS` +
`Utils.display_nation_name(tag)`. There is **no invalidation anywhere** —
`grep -n "_diplo_nation_forms" main.gd` returns only the declaration (`:241`) and
that one builder. Meanwhile `Utils.display_nation_name` consults
`formation_overrides` **first**, and `Utils.set_formation_overrides`
(`utils.gd:215`, called from `api_client.gd:317` on every response) flushes
`_flag_path_cache` and nothing else.

The formed display names are authored in `europe_1805.json`: **`Italy`** (from
KingdomOfItaly), **`United Netherlands`** (from Holland), **`Poland`** (from
DuchyOfWarsaw). None is a `NATION_COLORS` key. Measured (`r18_final.py`):

```
'cede Tyrol to Italy'              -> ''         (passes the fence)
'cede Tyrol to Kingdom of Italy'   -> 'cabinet'
'cede Posen to Poland'             -> ''         (passes)
'cede Posen to DuchyOfWarsaw'      -> 'cabinet'
'guarantee Italy'                  -> ''         (passes)
'guarantee Kingdom of Italy'       -> 'cabinet'
```

After the Proclamation the player is shown "Italy" on the flag, the ledger, the war
room and the campaign log — and **that** spelling is the one that bypasses the
Cabinet. Same shape as CX-N3 but produced by a landed feature rather than an
article, and structurally invisible to the drift pin, whose `nation_forms` fixture
parses a static `const` out of `utils.gd`. (The fence's own `_names_a_nation`
docstring records the *carve* residual — a runtime-minted client — but not this
*rename* case, which is different because the tag survives and only the printed
name changes.)

### MISSED:4 — **P4. The drift pin's court list is not built from the source the client uses.**

The test's `nation_forms` fixture builds display forms with
`re.sub(r"(?<!^)(?=[A-Z])", " ", tag)`; the client calls `display_nation_name`,
which reads `NATION_DISPLAY_NAMES` first. Today the symmetric difference is exactly
one form — **`'ottoman empire'`**, present in the client, absent from the fixture —
and it is behaviourally inert on all 447 corpus rows (measured: both form sets give
the identical 111/336 split). But `NATION_DISPLAY_NAMES` exists precisely to
diverge from the camelCase split, so the next row added to it silently unpins the
mirror. One-line fix: parse `NATION_DISPLAY_NAMES` in the fixture too.

### MISSED:5 — INFO. The cost question behind the row has an answer, and it is small.

See REFUTE:CX-N4. At the measured 6.4% escalation rate and 4,905–5,450 est. input
tokens per call, **1,000 escalations cost $4.90–$5.45 on `claude-haiku-4-5`**.
Prompt caching cannot pay at that volume and TTL. If "make it more efficient" is
the goal, the measurable levers are, in order:

1. **the 16,582-char user prompt itself** — `## Examples` alone is 3,423 chars and
   sits *after* the command, where it contributes nothing to a cacheable prefix;
2. **the 21-of-25 escalating rows that expect failure** — R3 already terminates the
   21 refusal-terminal rows without a call; the open question is whether the
   Berthier-shrug family (`xyzzy foobar`, `dance with the moon`, `the warden
   watches`) can join them, since those are the rows that pay twice;
3. **a client-side predictor / autocomplete**, which has an owner row (CR-7) and no
   gate — but which is constrained hard by R2: **an autocomplete that suggests a
   diplomatic verb would suggest a sentence the client then refuses to send**, so
   it inherits MISSED-1 and MISSED-2 before it inherits anything else. Any
   predictor must be fed from the *sendable* vocabulary — i.e. from
   `_redirect_verdict(...) == ""` — not from the parser's keyword tables.

---

## 3. Probe index (`probes/refute/`)

| file | what it establishes |
|---|---|
| `r1_fence.py` | 111/447 re-derived through the repo's OWN mirror; class composition 105 order / 6 underspecified / **0 read_only**; **0** unclaimed order rows; 189 phrases across ten tables; 30 client forms vs 29 fixture forms |
| `r2_iq10.py` | a synthetic long-form corpus row REDs the existing `TestTheCorpusCensus`; `CANDIDATE_SENTENCES` = 78, long form absent, short form present |
| `r3_drive.py`, `r5_dialogue.py` | the long form stages a non-blocking two-option mission dialogue; `active_diplomatic_mission` stays `None` |
| `r4_confirm.py` | a bare `yes` does not confirm that dialogue |
| `r12_pr.py` (+ `r12.json`) | escalation at the real gate: 1805 346/25/21, legacy 266/21/13, 21-of-25 expect failure |
| `r13_backlog.py`, `r14_backlog_live.py` | 8-of-18 and 7-of-18 reproduce; 7 land on the CR-2 clarification, 1 fails as a region lookup |
| `r15_prompt.py` (+ `r15_prompt.txt`) | independent prompt anatomy; `## Command to Parse` measured at char 12,555 |
| `r16_taught.py`, `r17_help.py` | the printed-copy census: the Berthier shrug and four help verbs the fence claims |
| `r18_final.py` | formed-nation bypass, fixture/client form drift, the cost table |
