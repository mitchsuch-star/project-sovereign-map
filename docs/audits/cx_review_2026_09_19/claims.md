# ROW CX — LENS 6: ATTACK THE ROW'S OWN CLAIMS

**Read-only adversarial re-derivation, September 19 2026, at master `727cf88a` (clean).**
Default verdict on every claim: WRONG until reproduced. Every figure below is the
output of a probe under
`…/scratchpad/cx_review/probes/` that I ran, on the shipped 126-province 1805 board,
`LLM_MODE=mock`, no key, no network. Nothing under `backend/`, `godot-client/`,
`tests/`, `docs/` or `tools/` was modified; no git-mutating command was run.

A pre-CX control tree was extracted with `git archive f7008582` into
`…/scratchpad/cx_review/pre_cx/` (read-only copy) so "did this row move the number?"
could be answered by experiment rather than by argument.

---

## 0. SCOREBOARD

**16 load-bearing claims re-derived. 9 reproduce exactly. 2 are materially wrong and
change the row's own ruling. 5 are wrong in magnitude, provenance or citation.**
Plus **2 behaviour findings** found by attacking the fix.

| # | claim | verdict |
|---|---|---|
| 1 | escalation `45/692 = 6.5%` "through the REAL predicate" | **WRONG — it is 50/692 = 7.2%, which the memo attributes to the re-implementation it discards** |
| 2 | "escalating rows where the corpus wants a NEW ORDER — **0/29**" | **WRONG on its own denominator (≥1/29; 5/34 overall)** |
| 3 | refuter's narrowing of the 86% | **DROPPED from the memo (measured: exactly 11 of 25 are `mock_only`)** |
| 4 | "a 684-case sweep, 30 executing → 9" | grid is **114 cases**; "9" ✓, "30" is **49–51**; and the row publishes **two** sizes (684 / 677) |
| 5 | three `.gd` line citations in §1 | **all three stale** (5563 / 6399 / 1778) |
| 6 | "the 22 click wins are ~6% of issued commands" | **WRONG in `SYSTEMS_REFERENCE` + `STATUS` — measured 17.44%** (memo/spec state it correctly) |
| 7 | "166 strings in `commanded_full40.json`" | **160**; 166 counts 6 metadata strings |
| 8 | "of 447" corpus entries | **449 at HEAD** — stale by 2 from this row's own CX-2 |
| 9 | "12,717-character COMMAND REFERENCE" | **12,720 at HEAD**; two NEW code comments state it in the present tense; a third names 9,630 |
| 10 | "two of the user's twelve answered" | ✓ on the test's twelve; **3 of 12** on the memo's own twelve |
| 11 | predictor table (14.8/17.5/21.4/29.6/39.7/95.1) | **2 of 7 reproducible**; the simulator is not committed (breaks the IQ-8 table rule the memo cites) |
| 12 | "intercepts 114 keyword forms" | 114 is **one of six** gating lists; 152 across them |
| 13 | "8 of the 18 `live_phrasing_backlog` parse confidently" | measured **11 of 18** |
| 14 | `48/1,416 = 3.39%`, `0/160`, `0/173` | ✓ **exact** |
| 15 | 38 intents TYPED 9 / CLICK 22 / PARITY 7 | ✓ **exact** |
| 16 | baseline 28,997 keystrokes; 8,422 archive commands; 1,416 script commands | ✓ **exact** |

---

## 1. ⛔ THE TWO THAT CHANGE THE RULING

### CX-CLAIM-1 (P2) — the escalation headline has its two measurements the wrong way round

`COMMAND_EXPERIENCE_SPEC.md:512` and `CX_THE_HAND_ON_THE_KEYBOARD…:249`, verbatim:

> escalation rate, golden corpus (447 entries × both worlds) | **45 / 692 = 6.5%** —
> through the REAL `_should_fallback_to_llm`. ⚠ A hand-written re-implementation of
> the same predicate, run first, gave 50 / 692 = 7.2%; **the real-predicate figure is
> the one cited**, and the discrepancy is recorded rather than averaged

**Measured through the real `LLMClient._should_fallback_to_llm`**, on the real
`main.get_llm_game_state()` payload (not `{"world": w}` — with the wrong shape every
marshal but Ney drops to `UNRESOLVED_ADDRESS_CONFIDENCE = 0.55` and the rate reads
35%; that is the trap here):

```
HEAD 727cf88a        50 / 694 = 7.20%   (entries = 449)
pre-CX f7008582      50 / 692 = 7.23%   (entries = 447)   <- probes/p15
```

`45` is not a different predicate. **`45 = 50 − 5`, and the five are exactly the
escalating corpus rows that declare no `expected.success`:**

```
soutl-attack-mack                     expected {'marshal': 'Soult'}
fa80-attak-reads-as-attack            expected action 'attack'
fa80-mvoe-reads-as-move               expected action 'move'
fa80-scuot-reads-as-scout             expected action 'scout'
r7-hodl-lorraine-is-a-standing-hold   expected action 'hold'
```

So the published figure silently drops five rows, **four of which are the rescue
class** — a typo the corpus wants turned into a real order. The exclusion is not
neutral: it removes precisely the evidence that argues *for* escalation, and the
memo's ⚠ note then tells the reader the higher number came from a worse instrument.

The row's CX levers do not move this (`probes/p07`: 50 at every combination of
`A_QUESTION_NEVER_ORDERS` × `A_RETREAT_CAN_BE_A_NOUN`), and the pre-CX control
reproduces 50. **This is a reporting defect, not a behaviour change.**

*Suggested fix:* cite `50 / 692 = 7.2%`, state the row filter if one is wanted, and
retract the ⚠ note — the re-implementation and the real predicate agreed.

---

### CX-CLAIM-2 (P2) — "0 / 29 escalating rows want a NEW ORDER" is false on its own denominator

`SPEC:517` / `MEMO:254`: `| escalating corpus rows where the corpus wants a NEW ORDER | **0 / 29** |`

Measured at HEAD **and** at `f7008582` — 34 distinct escalating rows, of which
**five carry an order verb in `expected.action`**:

```
emperor-address               'Emperor, attack Mack'      expected {success: TRUE, action: attack}   <- NOT mock_only
fa80-attak-reads-as-attack    'Ney, attak Mack'           -> attack    (mock_only)
fa80-mvoe-reads-as-move       'Ney, mvoe to Lorraine'     -> move      (mock_only)
fa80-scuot-reads-as-scout     'Ney, scuot Swabia'         -> scout     (mock_only)
r7-hodl-lorraine-is-a-standing-hold 'Davout, hodl Lorraine' -> hold    (mock_only)
```

`emperor-address` has `expected.success = true`, so it is **inside the memo's own 29**.
The claim is therefore false without any argument about the excluded five: it is at
best **1 / 29**, and **5 / 34** on the honest denominator.

This matters because the ruling is argued on it:

> **86% of what it catches is a sentence the corpus says must be REFUSED** … the
> deterministic chain carries **twelve times** more measured value than the model

The corrected reading — 74% of escalating rows want a refusal, 5 want an order —
still supports decision (iv) *keep and re-aim*, but not at the strength published.

*Suggested fix:* restate as `5 / 34` (or `1 / 29` on the filtered set) and say in one
line why four of them being `mock_only` does or does not excuse them.

---

## 2. A REFUTER CORRECTION THE MEMO DROPPED

### CX-CLAIM-3 (P3)

`MEMO §0`: *"The refuters overturned eight of the censuses' own headline claims and
those corrections are **carried here rather than quietly dropped** — they are marked ⚠."*

`docs/audits/cx_recon_2026_09_19/refute_llmvalue.md:27`, scoreboard row 2:

> CX-LLM-2 86% want a refusal | **NARROWED** | Arithmetic reproduces exactly.
> **11 of the 25 are `mock_only`**, whose `expected` is a *mock* contract the live
> evaluator SKIPS; and "escalation's job is to NOT help" is the wrong reading — on
> these rows the model is the danger.

**I reproduced the narrowing exactly: 25 rows with `expected.success: false`, of
which 11 are `mock_only`** (`probes/p06`). The memo publishes `25 / 29 = 86%` with no
⚠ and no mention of it. That is the one narrowing that bears directly on the ruling
it feeds.

(Two other refuter corrections WERE carried and reproduce: the movement-verb
correction in §1b, and the predictor's 31.7 → 17.5 correction in §5. Credit where
due — those are carried faithfully.)

---

## 3. THE SWEEP

### CX-CLAIM-4 (P3) — a 684-case sweep does not exist; the committed grid is 114

| where | figure |
|---|---|
| `COMMAND_EXPERIENCE_SPEC.md:218` | "a **684-case** sweep of (lead × verb)" |
| memo ×3 (`:350`, `:401`, `:413`) | "**684-case** sweep" |
| `BUG_FIXES.md:12869` | "a **684-case** (lead × verb) sweep" |
| CX-1 commit message | "a **684-case** (lead x verb) sweep" |
| CX-6 commit message | "the **684-case** question sweep still 9 executing" |
| `tests/test_cx1_a_question_never_orders.py:62` | "A **677-case** sweep … 668 clean, 9 executing" |
| **the committed test** (`TestTheSweep`) | **15 leads × 7 verbs = 105, + 9 controls = 114** |

Re-run of the committed grid (`probes/p10`, same footprint predicate as the test):

```
A_QUESTION_NEVER_ORDERS = True    9 executing of 114   (0 outside the controls)   <- reproduces
A_QUESTION_NEVER_ORDERS = False  49 executing of 114   (40 outside the controls)  <- NOT 30
                                 51 on a second run    (the lever-down arm is not deterministic)
```

So **the "9, all nine intended controls" reproduces exactly and is good evidence.**
The "30" before-figure and both published grid sizes do not reproduce from anything
committed, and the row is not internally consistent about its own number.

⚠ A second, smaller point about the same pin: **two of the nine "intended controls"
execute with a marshal the player never named** — `do attack Mack` and
`can you attack Mack` both commit **Soult** (`probes/p12`, group B). "All nine are
intended controls" is true about the sweep's own allowlist; it is weaker than it
reads as a safety statement.

*Suggested fix:* publish **114** (or commit the 684-case probe as the archive the
IQ-8 table rule requires), and re-measure or drop the "30".

---

## 4. CITATIONS

### CX-CLAIM-5 (P3) — three stale `.gd` citations, all inside §1's load-bearing claims

Checked by navigating to the SYMBOL. 14 `file:line` citations across the spec, the
memo and the new code; 3 are wrong, and all three sit under the row's central
"the chips ARE typed commands / the client does have a movement verb" argument.

| citation | prose says | what is actually there | real site |
|---|---|---|---|
| `main.gd:5563-5575` | "maps `MOVE_TO → "march to"`, `PURSUE`, `SUPPORT`, `HOLD`" | the `redemption_event` / capture-routing block | **`main.gd:5654`** (`"MOVE_TO": "march to",`) |
| `main.gd:6399-6409` | the region-panel chip string "sent through `api_client.send_command`" | the tail of `_on_vassal_command_result` + the head of `_on_naval_command` | **`main.gd:6485`** `_on_region_panel_command`, send at **`:6495`** |
| `main.gd:1778` | "the client intercepts `vassalize`" (CX-X3) | `"abrogate",` — a treaty-break keyword | **`main.gd:1864`** |

Correct and verified: `region_panel.gd:136-140` (the `do:` branch),
`clarification.py:311`, `proposal_confirm_popup.gd:129`.

Two `main.py:NNNN` citations inside `dialogue_routing.py` were not checkable from a
bare filename (several `main.py` in tree) and are not counted either way.

---

### CX-CLAIM-9 (P4) — the help is 12,720 at HEAD, and the row states three different numbers for it

* Rendered `help` reply on the 1805 board **at HEAD: 12,720 chars / 236 lines**.
* **12,717 is the correct PRE-CX-3 figure** — CX-3 itself changed
  `"Davout, hold Ulm"` → `"Davout, hold Swabia"` (+3 chars). Verified by diffing
  `2c3535b5 -- backend/commands/meta_executor.py`.
* But two comments **written by this row** state it in the present tense and are
  already stale: `backend/ai/counsel.py:19` (*"The COMMAND REFERENCE — 12,717
  characters"*) and `backend/ai/question_desk.py:394`.
* And `backend/ai/question_desk.py:20` names **9,630** for the same document (a
  dated Sept-4 measurement, but the file now carries two different figures).

**What DOES reproduce exactly:** the four needles (`status`, `where is`, `who holds`,
`how many men`) occur **0 times each** ✓, and the router's *"370 characters against
12,717"* — `why did that fail` returns **exactly 370** ✓.

---

## 5. MAGNITUDE AND PROVENANCE

### CX-CLAIM-6 (P3) — "the 22 click wins are ~6% of issued commands" is false, and the false version is the one in the rules doc

The memo (`:173`) and spec (`:118`) state it **correctly**: *"Of the 22 CLICK WINS,
exactly two are per-turn routine — recruit (3.2%) and build (2.8%), 6.0% of issued
commands together."* Measured: recruit **3.18%**, build **2.82%**, sum **6.00%** ✓ exact.

`docs/SYSTEMS_REFERENCE.md:5915` and `docs/STATUS.md:19` compress this into:

> **the 22 click wins are ~6% of issued commands**

Measured over the same 1,416 commands, the verbs whose 38-intent row is CLICK WINS:

```
247 / 1,416 = 17.44%
  recruit 3.18 · build 2.82 · propose 1.84 · invest 1.34 · buy 1.13 · request 1.13
  declare 1.20 · grant 0.71 · guarantee 0.71 · land 0.49 · order 0.49 · increase 0.42
  cede 0.35 · endow 0.35 · revoke 0.35 · commission 0.28 · release 0.21 · sponsor 0.21 …
```

The spec's own table two lines above already contradicts it —
`| propose / invest / declare / mission | ~7% | click-only |` — so 6% + 7% ≥ 13% by
the row's own arithmetic. And row 3 (*attack a co-located enemy*) is a CLICK WIN
inside the 14.34% attack share, which the 6% figure does not touch at all.

*Suggested fix:* in `SYSTEMS_REFERENCE` §50.1 and `STATUS`, restore the memo's
wording — "two of the 22 are per-turn routine, together 6.0%" — or publish 17.4%.

---

### CX-CLAIM-7 (P4) — "166 strings in `commanded_full40.json`"

`MEMO §6b`: *"of the **166 strings** in `commanded_full40.json`, **0 are
question-shaped and 0 omit the addressee comma**."*

Measured: the file holds **160 command strings (51 unique)** across 40 turn keys. A
walk over ALL JSON string leaves gives 166 — the extra six are the script's own
metadata: `"commanded-full40"`, `"historical"`, `"mock"`, the `_note_d6` prose block,
and the two `policy` values. The memo's **own §4 table uses 160** (`0 / 160`).

**The substantive claim reproduces over the real 160: 0 question-shaped, 0 addressed
without a comma.** ✓ Only the denominator is wrong.

### CX-CLAIM-8 (P4) — "of 447"

Corpus entries by commit: `f7008582` 447 → **CX-2 `5fc3d5c8` 449** (two `legacy`
twins added) → 449 at HEAD. The memo was written at `704df816`, i.e. **after** CX-2,
and still says "447" in three places, including the escalation denominator
`692` (which is `245×2 + 55 + 147`, the 447 arithmetic; at HEAD it is 694).

`live_only = 4` ✓ and `mock_only = 49` ✓ reproduce exactly — against 449.

### CX-CLAIM-12 (P4) — "intercepts 114 keyword forms"

`DIPLO_FAMILY_KEYWORDS` has exactly **114** members ✓. But
`_redirect_diplomatic_command` (`main.gd:2007`) gates on six lists plus two extra
rules:

```
DIPLO_FAMILY_KEYWORDS          114
DIPLO_NO_HOME_KEYWORDS          18
DIPLO_NATION_ANYWHERE_KEYWORDS  13
DIPLO_WAR_ROOM_KEYWORDS          2
DIPLO_NATION_GATED_PREFIXES      2
DIPLO_AUTONOMY_VERBS × LEVELS    3 × 3 = 9 forms
                          total 152+  · plus the bare `court` rule and DIPLO_ADDRESS_NAMES (6)
```

"114" is the biggest list, not the gate. It **understates** the client's interception.

### CX-CLAIM-13 (P4) — "8 of the 18 `live_phrasing_backlog` parse confidently today"

Measured with the obvious predicate (`fast_parse` confidence ≥ 0.7 and a non-`unknown`
action, real `game_state`): **11 of 18**. The memo does not state its predicate, so
this is a discrepancy rather than a kill — but it is 3 higher than published, i.e. the
backlog is even more stale than the memo says.

### CX-CLAIM-10 (P4) — "two of the user's twelve questions answered, ten walled"

Reconstructed by flipping `question_desk.THE_DESK_ANSWERS_THE_BOARD` (not a perfect
pre-CX reconstruction — CX-2 also added a guard to `answer_question`):

| list | lever down | lever up |
|---|---|---|
| the twelve in `TestTheTwelveQuestions` | **2 answered / 10 walls** ✓ | 12 / 0 |
| the twelve named in `SPEC §3.2` + `typed_road.json` | **3 answered / 9 walls** | 12 / 0 |

So "two of twelve" holds for the TEST's list and not for the list the prose calls
"the twelve questions the user named". The **"0 walls" half reproduces on both.**

### CX-CLAIM-11 (P4) — the predictor table is 2 of 7 reproducible, and its instrument is not committed

| memo figure | verdict |
|---|---|
| baseline **28,997** keystrokes | ✓ **exact** (`sum(len(c))` over the 1,416) |
| **95.1%** "every command by chip" | ✓ **exact** (1 keystroke/command: `1416/28997`) |
| 14.8% / 17.5% / 21.4% / 29.6% / 39.7% | **not reproducible from anything committed** |

The simulator behind the four middle rows is not in the repo — CX-3's diff is
`main.gd` + a test + a screenshot scene. My own oracle model of the shipped history
semantics (`_add_to_history` dedupe + trim, `_history_pool` case-insensitive
prefix, `MAX_HISTORY = 50`) gives **31.3% saved / 56.3% hit** at the shipped
constants, close to the memo's stated **oracle 29.9%** but not to its **21.4%**.

**This is the row breaking the IQ-8 table rule it cites in its own header**
(*"a figure with no archive is uncitable"*). The `cx-*` playtest archives are
committed; the keystroke simulator is not.

### INFO — the typed-road archive predates two of the six commits, and CX-5's citation to it shows nothing

`docs/audits/playtest_digests/cx-typed-road/meta.json` records
`git_commit: 704df816…`, **`dirty: true`**, `dirty_scope: ["backend", …]`. CX-5
re-shot it: the diff is **four lines, all provenance** (engine sha, content hash,
timestamp) — **the digest body is byte-identical**.

CX-5's commit message says: *"the MUSING forms now get their muster … **Read on the
typed-road archive: four musings, four real musters, 4 of 4 action points unused.**"*
The four musters were already printing in the archive shot at CX-3 (`digest.md:65-68`),
so the archive cannot evidence what CX-5 changed. Either the change was already live
or the digest's one-line truncation hides it; either way the citation is not proof.

### INFO — `SYSTEMS_REFERENCE §50.2` does not carry CX-6's correction

§50.2 arm (d) still reads *"**the subject decides** for leads that DO have an
imperative form"* with no mention that CX-6 removed the object pronouns. CX-6 touched
`clause_guards.py`, `BUG_FIXES`, `COMMAND_EXPERIENCE_SPEC`, the test and the sweep —
**not the rules doc §50 that the memo names as the rules of record.**

---

## 6. TWO BEHAVIOUR FINDINGS — FROM ATTACKING THE FIX

### CX-BEHAV-1 (P3) ⛔ — the manual still teaches two sentences the board refuses, and CX-3's census is blind to both

CX-3's headline is *"a census so it cannot recur"* (spec §3.3, §50.7:
**THE GAME MUST NOT OFFER A SENTENCE IT CANNOT READ**). I ran my own census over the
50 double-quoted phrasings in the rendered `help` (`probes/p16`), independently of
the committed test. **Two are still broken, and one is the identical class CX-3b was
built from:**

```
help prints:   repair     - "repair Lyon" (1 AP, 150g)
typed:         repair Lyon                 -> "Unknown region: Lyon"      success=False

help prints:   move       - "Soult, move to Bavaria"
typed:         Soult, move to Bavaria      -> "Bavaria is a nation, not a province."  success=False
```

**`Lyon` is a LEGACY-map region and does not exist on the shipped 126-province
board** — measured `'Lyon' in world.regions`: `1805 False / legacy True`. That is
exactly `Ulm`'s story, eleven lines down the same manual.

**Why the census cannot see them.** `tests/test_cx3_the_predictor.py:281`:

```python
refusals = ("not found", "cannot parse", "Unknown target",
            "I cannot interpret", "no such", "eludes me")
```

The executor says **`"Unknown region: Lyon"`** — one word off `"Unknown target"` — and
the move refusal matches no needle at all. Measured needle hits:

```
'repair Lyon'            success=False  census needle hits = []      <- green
'Soult, move to Bavaria' success=False  census needle hits = []      <- green
'Davout, hold Ulm'       success=False  census needle hits = ['not found']  <- the one it caught
```

The whole CX test file is green at HEAD (202 passed). **The pin that exists to stop
this recurring is passing while two instances ship.**

*Suggested fix:* stop hand-listing refusal phrases. Assert `success is True` for every
non-exempt quoted phrase and keep a second explicit allowlist for the phrases that
are legitimately *gated* on the boot board (`recruit`, `bombard Swabia`,
`buy substitutes for Ney`, `land Soult in Munster`, `buy off Prussia`, …) — an
allowlist of gates, the same shape as `NOT_COMMANDS`, so a new unreadable phrasing
fails until somebody classifies it. Then fix the two: `repair Lyon` → a 1805 province,
`Soult, move to Bavaria` → a province (the executor itself suggests Franconia /
Munich / Swabia).

Player-reachable: **yes.** `help` is the first thing a lost player types; both strings
are printed in it; `help` is not in the client's diplomatic-redirect lists.

---

### CX-BEHAV-2 (P3) — CX-1b's P1 is narrowed, not closed, and the residue is undisclosed (pre-existing)

CX-1b is filed as a **FIXED P1**: *"`Nay attack Mack` — one keystroke from
`Nay, attack Mack` — sent **Soult, never named**, into a real battle."* Measured on
the boot board, `probes/p12` / `p13`:

```
'Nay attack Mack'      REFUSED free  "There is no 'Nay' in the order of battle, Sire."   <- fixed ✓
'quickly attack Mack'  REFUSED free  "There is no 'quickly' in the order of battle"      <- fixed ✓

'now attack Mack'      AP 4->3, 285g, 6 corps moved, REAL BATTLE   -> MUSTER — SOULT
'please attack Mack'   AP 4->3, 258g, 5 corps moved, REAL BATTLE   -> MUSTER — SOULT
'he attack Mack'       AP 4->3, 259g, 6 corps moved, REAL BATTLE   -> MUSTER — SOULT
'she attack Mack'      AP 4->3, 282g, 4 corps moved, REAL BATTLE   -> MUSTER — SOULT
'they attack Mack'     AP 4->3, 251g, 6 corps moved, REAL BATTLE   -> MUSTER — SOULT
'it attack Mack'       AP 4->3, 247g, 5 corps moved, REAL BATTLE   -> MUSTER — SOULT
```

**Attribution, by experiment:** identical at `AN_ADDRESS_NEEDS_NO_COMMA = False`
(`probes/p13`), so **this row did not ship it** — it is pre-existing and the fix
narrowed the class rather than closing it. CX-1's commit message states the mechanism
(*"The run must contain no function word and no collective"*) — that exclusion, added
to rescue `can you attack Mack` and `do attack Mack`, is exactly what leaves the
pronoun and adverb leads open.

The objection this row should answer is not "why wasn't it fixed" but **"why does
nothing on the row say it is still there"**: the memo's §6b evidence table shows three
refusals as proof the P1 is closed, and `he attack Mack` / `they attack Mack` commit an
unnamed marshal to an irreversible battle exactly as `Nay attack Mack` did.

*Suggested fix (routed, not this row's):* treat a bare subject **pronoun** as an
unresolved addressee rather than a function word — `he`/`she`/`they`/`it` with no
antecedent in `command_history` should reach CR-2's "Which marshal, Sire?" the way
`everyone attack` already does, not pick the default corps. `please` / `now` are
defensible as politeness on a bare order. Owner: **CR-6 proper**, beside IQ9-X1.

---

### INFO — a CX-5 commit claim that does not hold for the unaddressed form

CX-5's commit message: *"`sound`, `order`, `begin` and `call` "the retreat" all
retreated correctly before the fix and **still do**, and they are the whole set a
player reaches for."*

```
'Ney, sound the retreat'   -> Ney retreats ✓
'order the retreat'        -> general retreat ✓
'begin the retreat'        -> general retreat ✓
'call the retreat'         -> general retreat ✓
'sound the retreat'        -> "I do not find 'sound' in the order of battle, Sire. Did you mean Soult?"
```

The unaddressed `sound the retreat` is read as an address to **Soult**. Identical at
both `AN_ADDRESS_NEEDS_NO_COMMA` positions, so **pre-existing, not shipped here** —
but it is the first verb the commit message names, and the claim is stated without the
qualifier.

---

## 7. WHAT REPRODUCES EXACTLY — the row's arithmetic is mostly very good

Stated plainly because 9 of 16 load-bearing claims survived a hostile re-derivation:

```
1,416 script commands (excl. typed_road)                     ✓ exact
8,422 archived driver commands (89 non-CX digests)           ✓ exact
20 of 23 commanded archives run commanded_full40.json        ✓ exact
recruit 3.18% · build 2.82% · sum 6.00%                      ✓ exact
attack 14.34% · status 14.12% · fortify+unfortify 15.32%
  · drill 6.57% · hold 1.91%                                 ✓ exact (move+march 13.98 vs 14.2 published)
38 intents: TYPED 9 / CLICK 22 / PARITY 7                    ✓ exact
commanded_full40: 0 question-shaped, 0 missing comma         ✓ (over the real 160)
escalation 48 / 1,416 = 3.39%                                ✓ exact
escalation 0 / 160 and 0 / 173 on the commanded arms         ✓ exact
live_only 4 · mock_only 49 · 25 success:false                ✓ exact
11 of the 25 are mock_only (the refuter's narrowing)         ✓ exact
help needles: status/where is/who holds/how many men = 0     ✓ exact
router reply 370 chars vs the manual                         ✓ exact
baseline 28,997 keystrokes · 95.1% chip ceiling              ✓ exact
sweep: 9 executing, all nine controls                        ✓ exact
CX-2b: the three hardcoded courts are gone from the shrug    ✓ verified against f7008582
CX-3a: `halt Ney` works · CX-3b: help no longer prints Ulm   ✓ verified
CX-5: act-on-someone-else phrasings refuse free; genuine
  addressed retreats still retreat                           ✓ verified (7 refuse / 8 retreat in my sample)
41-of-41 / 0 walls: every question I drove (12 + 12 + 7
  router + typed_road's own ~20) is answered, AP untouched   ✓ substantively, though the list of 41 is not committed
tests/test_cx{1,2,3}*.py                                     ✓ 202 passed
```

---

## 8. PROBES

All under `…/scratchpad/cx_review/probes/`, runnable as-is:

| probe | what it measures |
|---|---|
| `p01_scripts_census.py` | 1,416 / 160 / 166 / verb shares / question-shape + comma census |
| `p02_help_length.py` | help length at HEAD, the four needles, the twelve questions |
| `p05`, `p06_escalation_real_gs.py` | escalation through the real predicate, wrong vs right `game_state` |
| `p07_corpus_escalation_arms.py` | escalation under every CX lever combination |
| `p10_sweep.py` | the committed 114-case grid at both lever positions |
| `p11_keystrokes.py` | baseline 28,997, the chip ceiling, the shipped history model |
| `p12_attack_the_fix.py` | 80 ordinary sentences driven end to end |
| `p13_attribute.py` | the same cases with `AN_ADDRESS_NEEDS_NO_COMMA` up and down |
| `p14_desk_and_router.py` | the "2 of 12" before-figure and the 370-char router |
| `p15_precx_escalation.py` | the same escalation measurement on a `git archive f7008582` copy |
| `p16_help_census.py` | an independent census of every quoted help phrasing |
| `p08_citations.py` | every `file:line` in the spec, memo and new code |
| `p09_client_gate.py` | the DIPLO_* list sizes and the endpoint counts |
