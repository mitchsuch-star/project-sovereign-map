# CX recon — the routed backlog, reproduced

**Measured:** September 19, 2026 · repo `C:\Users\User\PycharmProjects\project-sovereign-map`
· HEAD `f7008582` · board = the shipped 126-province 1805 campaign
(`europe_1805.json`, seed `historical`) · `LLM_MODE=mock`, no key, no network.
Live-LLM behaviour measured **keylessly** through the IQ-9 replay tier
(`tests/_parser_replay.py` + the committed cassettes).

Probes live in `<scratchpad>/cx_recon/probes/` (`p_*.py` with their `out_*.txt`).
Every claim below is either a `file:line` or the output of a probe that ran.
Anything I could not settle is marked **UNVERIFIED**.

---

## ⚠ 0. READ FIRST — the tree changed under me, mid-session

`git status` was **clean** at session start. At **09:31:10** it was not:

```
 M backend/ai/clause_guards.py      (643 -> 771 lines, +137/-9)
 M backend/ai/llm_client.py         (+22)
```

A sibling agent is **building on the parse pipeline right now**, and its diff is
tagged `CX` in its own docstrings — the same row this recon serves. What it adds:
`clause_guards.A_QUESTION_NEVER_ORDERS`, `_SUBJECT_WH_WORDS`,
`_THIRD_PERSON_SUBJECTS`, a widened `is_question(command_text, subjects=…)`, and
`llm_client._question_subjects()` feeding it a fog-honest roster.

Consequences you need to know:

1. I caught a **torn read** of `clause_guards.py` — a `NameError: Iterable` raised
   at a line whose own `from typing import Iterable` (:52) was present, i.e. the
   file was being written while Python imported it. Anything that imports the
   backend can fail spuriously while that writer runs.
2. **Every finding below was re-run against the modified tree and reproduced
   identically** (`probes/out_recheck.txt`). None is an artefact of the
   concurrent edit, and the concurrent edit fixes none of them.
3. The sibling's change **is already live and does move behaviour**: on the
   current tree `can Ney attack Mack` routes to HELP while `can you attack Mack`
   marches and spends 1 AP. That is §8 item 6's territory (below). Coordinate
   before touching `clause_guards.py` / `llm_client.py`.

---

## 1. The six routed rows

### IQ9-X1 — the CR-2 forced retry cannot rescue the word-scan family

**CONFIRMED — and the filed completion is the wrong prescription.**

Probes `p_iq9_x1.py`, `p_iq9_x1b.py`:

| stage | result |
|---|---|
| fast parse of `hunt down mack` | confidence **0.90**, gate 0.70 → never escalates on its own |
| the fast parse's marshal field | `marshals: []` — it binds nobody |
| mock-only `parse()` | `Did you mean 'Davout'? ('down' not found)`, `kind=marshal_suggest`, `candidates=['Davout']` |
| live road (cassette `cr2-retry-hunt-down-mack`) | **1 live call**; model returns `marshals: []`, `action: pursue`, `target: Mack` |
| live-road `parse()` | **byte-identical to the mock-only result** |

**The mechanism, measured directly** (`p_iq9_x1b.py`) — I fed
`_apply_fuzzy_matching` the fast dict and the retried dict separately:

```
_apply_fuzzy_matching(FAST)          -> error "Did you mean 'Davout'? ('down' not found)"
_apply_fuzzy_matching(RETRIED live)  -> error "Did you mean 'Davout'? ('down' not found)"
_apply_fuzzy_matching(same, marshal pre-bound to "Ney") -> error None, target Mack
```

So the retry is **structurally incapable** of rescuing this family, not merely
unlucky: the live model returns *no marshal at all*, which is the same marshal
state the fast pass had, and the word scan (`backend/commands/parser.py:1274`,
the `suggest` arm inside `_apply_fuzzy_matching`, `parser.py:964`) re-fires on
identical input. The only field the retry changes — `action` — the word scan
never reads.

⛔ **The row's completion is unbuildable as written.** It says *"the retried live
parse is ADOPTED when it resolves the marshal the fast pass mis-bound"*. Two
corrections:

* the retried parse **does not resolve a marshal** — it declines to name one;
* the fast pass **did not mis-bind** one either — `fast_parse` returns
  `marshals: []`. The mis-binding is invented *inside* `_apply_fuzzy_matching`,
  on both passes.

The behaviour the sentence actually wants is: a marshal-less live parse should
reach the **CR-2 "Which marshal shall pursue Mack, Sire?" clarification**, which
already exists (`backend/commands/clarification.py`). The word scan overwrites
that outcome with a guess.

**Reach — wider than the row implies.** The corpus's own `live_phrasing_backlog`
(18 hand-picked phrasings, authored as *"live-LLM-only capabilities today"*),
measured on the 1805 board (`p_backlog.py`):

* 8 of 18 the deterministic road now handles outright;
* 7 of 18 fall **below** the gate → escalate → the LLM is doing its job;
* **3 of 18 clear the gate at 0.80–0.90 and are then killed by `down` → Davout**
  — `hunt down mack`, `track down the austrians`, `hunt down mack until
  destroyed`.

One sixth of the project's own list of "phrasings we want to support" dies on a
single word, above the gate, where the model cannot help.

**Family width** (`p_wordscan.py`): over a 170-word ordinary-order English
vocabulary, **27 words (16%) survive the shape gate and bind to a French
marshal** — `south` / `soil` / `soul` → Soult, `none` → Ney, `lean` → Lannes as
silent **auto-corrects**; `must`, `need`, `next`, `near`, `should`, `link`,
`less`, `match`, `mount`, `moor`, `dare`, `dash`, `sort`, `split`, `solid`,
`sound` … as `suggest`, which refuses the whole command.
⚠ **That 27 is an upper bound on the vocabulary, not a count of live defects** —
the word scan runs only when no marshal is already bound, and `skip_words`
(`parser.py:1229-1253`) catches many common words. `down` is the proven-live
member.

**What a fix touches:** `parser.py` `_apply_fuzzy_matching` (:964) — the three
`suggest` arms at :1088, :1169, :1274 — plus the retry seam at `parser.py:1789`
and `llm_client.reparse_with_llm` (:984). Pin to flip:
`tests/test_iq9_keyless_parser_gate.py::TestCR2Retry::test_retry_cannot_rescue_the_word_scan_family_today`.
Cheapest honest cut: when the parse arrived from a **live** provider that
explicitly returned no marshal, do not run the marshal word scan — route to the
CR-2 clarification instead.

---

### IQ9-X2 — the fuzzy suggestion can name a FOGGED enemy

**CONFIRMED — and materially bigger than filed. The leak is not the "did you
mean" list; it is a free, zero-AP intelligence oracle on the ordinary attack and
address roads.**

Boot rosters (`p_iq9_x2.py`):

```
parser _get_known_enemies()  : 14   (parser.py:868 -> _extract_enemy_marshal_names, parser.py:699)
world.get_visible_enemies()  :  2   ['ArchdukeJohn', 'Mack']
FOGGED but matchable         : 12   Abdurrahman ArchdukeCharles Armfelt Brunswick
                                    Buxhowden Castanos Damas Deroy Frederick
                                    Hohenlohe Kutuzov Moore
```

Through `POST /command` on the boot board, at **0 AP every time**
(`p_iq9_x2c.py`, `p_iq9_x2d.py`):

| typed | reply | what it leaks |
|---|---|---|
| `Ney, attack Castanoss` | *"Ney cannot attack **Spain** — they are our **ally**, Sire, and we are not at war with them."* | he exists · his nation · our treaty state |
| `Ney, attack Deroi` | *"Ney cannot attack **Bavaria** — they are our **ally** …"* | same |
| `Ney, attack Hohenloh` | *"We are not at war with **Prussia**, Sire — **Hohenlohe** may not be attacked … Declare war on Prussia first"* | same, plus his spelling |
| `Ney, attack Damass` | *"We are not at war with **Naples**, Sire — **Damas** may not be attacked …"* | same |
| `Ney, attack Buxhowdenn` | *"No intelligence on **Buxhowden**'s position, Sire. Scout for him …"* | existence + corrected spelling |
| `Ney, attack Moor` | *"No intelligence on **Moore**'s position, Sire."* | ditto — from a 4-letter English word |
| `Buxhowden, hold` | *"Marshal Buxhowden commands for **Russia**, Sire — he does not answer to us."* | exact-match address; no typo needed |

And the **oracle is clean** — a real-but-unscouted name is distinguishable from
an invented one on all three roads (`p_iq9_x2d.py`):

| road | fogged REAL name | INVENTED name |
|---|---|---|
| `where is X` | *"We have no word of Castanos's whereabouts, Sire."* | dumps the whole COMMAND REFERENCE |
| `X, hold` | *"Marshal Buxhowden commands for Russia…"* | *"There is no Marshal 'Zorglub' in the order of battle, Sire."* |
| `Ney, attack X` | *"cannot attack Spain — they are our ally"* | *"named no foe our maps know … Ney marches on Mack"* (**and spends 1 AP**) |

**Corrections to the row:**

* The exposure is **not** confined to a "did you mean" candidate list. The
  candidate lists I could reach print the *player's own* roster. The real leaks
  are (a) the WO-1 enemy-addressee refusal `_resolve_enemy_addressee`
  (`parser.py:402`), which names the man **and his nation** on an EXACT match,
  and (b) the parse-layer auto-correct binding a fogged name as a target, after
  which the executor narrates it.
* So the filed completion — *"the suggestion list reads `get_visible_enemies()`"*
  — closes the smallest of the three roads.

**The honest register already exists and is good**, which makes this cheap:
`Ney, attack Kutozov` gives *"Your order names no foe our maps know, Sire — Ney
will not charge at a guess. Whom shall he engage?"* at 0 AP, and the question
desk gives *"We have no word of …"*. The precedent for the fix is already in the
tree: `executor._display_candidates` (`backend/commands/executor.py:327`) — the
WO slice-10 shape, *match omniscient, print filtered*, with an explicit
fail-closed arm.

**What a fix touches:** `parser.py` `_get_known_enemies` (:868), split into a
matching roster and a *speakable* roster; `_resolve_enemy_addressee` (:402) and
its caller `_enemy_addressee_refusal` (:925); the target auto-correct ladder at
`parser.py:1360-1410` (`_is_targetable_enemy` is already consulted by the
edit-distance arm — the fog term belongs beside it); and whichever executor arms
compose the *"cannot attack \<nation\>"* / *"No intelligence on \<name\>"*
sentences.

⚠ **Design call, not a bug fix:** making this fog-honest necessarily makes the
game *less* helpful about typos on names you have not scouted. State that trade
on the row before building it.

---

### IQ9-X3 — a live-road failure stamps `parse_mode: "mock"`

**CONFIRMED, and the consequence is bigger than the cosmetic framing.**

`p_iq9_x3.py`, four arms through `POST /command` on the replay tier:

| case | live calls actually made | `parse_mode` reported |
|---|---|---|
| `flurble the wibble` (the pinned case) | `['parse', 'berthier']` | **`"mock"`** |
| `hunt down mack` (the CR-2 retry road) | `['parse']` | **`"mock"`** |
| live API error (timeout) | `['parse']` | **`"mock"`** |
| **control** — `Ney, deal with Mack`, a live parse that SUCCEEDS | `['parse']` | `"anthropic"`, conf 0.85 |

The stamp is not wrong on one failure shape; it is wrong on **every** road where
the model was consulted and did not produce an adopted parse. Writer:
`backend/main.py:2979` (`_PARSE_PROVENANCE.set(...)`, defaulting to `"mock"` when
`parsed["mode"]` is absent). Reader/consumer: `main.py:565-569`. Contextvar
declared at `main.py:632`.

**Why this is not P4 for the question you are actually asking.** `parse_mode` is
the only instrument in the product that records whether a model was consulted,
and it counts **only the successes**. Any attempt to answer *"is routing to the
LLM worth it?"* from telemetry today will under-count live calls by exactly the
set of calls that failed — making escalation look cheaper and more reliable than
it is.

**What a fix touches:** the failure dicts built in `parser.py` (the `fuzzy_error`
failure block at `parser.py:1802-1825` already copies `llm_error`; `mode` belongs
beside it) and the one stamp at `main.py:2979`. Pin to flip:
`TestBelowGatePhrasings::test_a_live_road_failure_still_stamps_mock_provenance`.

---

### IQ7-X7 — a deferred answer still signs an ordinary letter

**CONFIRMED on the live board — and the fix is already written elsewhere in the
tree.**

With Portugal's `open_borders` letter current (`p_iq7_x7.py`, `p_iq7_x7c.py`),
**7 of 7 filed lines resolve** — and I extended the family: **16 of 17 additional
lines I wrote resolve too**, including `accept the offer never`,
`accept, unless Ney objects`, `accept it when Austria signs`,
`remind me to accept`, `almost accept`, `consider accepting`, `i would accept`,
`we could accept`. The only one that failed was `accept? later` — and it failed
because of the `?`, i.e. because of pass 3's question rule, not because of any
deferral rule.

The open road is not the letter's alone. The same three shapes (`… later`,
`maybe …`, `if we …`) resolve on **`settlement_review`** (→ `ratify`),
**`ally_petition`** (→ `grant`) and **`vassal_rebellion`** (→ `accept risk`).

**The contrast that makes this cheap** — a REAL client petition built from the
live board through `deliver_ai_proposal` (`p_iq7_x7c.py`):

```
REAL PETITION (Switzerland, relief)          ORDINARY LETTER (Portugal)
  'grant it'            -> accept_ai_proposal  'accept'              -> accept
  'yes, grant it'       -> accept_ai_proposal  'accept it later'     -> accept
  'we shall grant it'   -> accept_ai_proposal  'accept it next turn' -> accept
  'refuse it'           -> reject_ai_proposal  'maybe accept'        -> accept
  'grant it later'      -> None                'if we accept'        -> accept
  'maybe grant it'      -> None                'accept, but not now' -> accept
  'if we grant it'      -> None                'perhaps accept'      -> accept
  'is that a yes'       -> None                'is that a yes'       -> yes
```

Both dialogues are `type: "incoming_proposal"` and **both offer the same two
actions** (`accept_ai_proposal` / `reject_ai_proposal`). The only difference is
that `match_dialogue_answer` (`backend/commands/dialogue_routing.py:1074`) routes
to `petition_plain_answer` (:400) when `vassal.is_client_petition(dialogue)`
(`backend/game_logic/vassal.py:2251`) says so, and to the open road otherwise.

⚠ **Correction to my own first probe, recorded because it nearly became a
finding:** my first synthetic petition fixture used
`context: {"petition_kind": "relief"}` and showed `grant it later` resolving —
i.e. it appeared the petition was *not* protected. That fixture was wrong:
`is_client_petition` keys on `context.proposal_type == "client_petition"`
(`vassal.py:2255-2260`). Build petition fixtures from `vassal.petition_terms` +
`deliver_ai_proposal`, as the IQ-7 tests do
(`tests/test_iq7_review_round.py::_make_proposal`, :296).

**What a fix touches:** `petition_plain_answer` is a working closed grammar with
a documented contract (its docstring, :400-439). The row is *generalising its
allowlist assembly per family* — each family needs its own subject nouns
(`_PLAIN_PROVINCE_SUBJECT_WORDS` / `_PLAIN_RELIEF_SUBJECT_WORDS` are the pattern)
— plus a routing table at `match_dialogue_answer:1162`, plus the free-text third
copy in `diplomatic_executor.handle_diplomatic_dialogue_response`. Existing
levers to extend rather than replace: `A_PETITION_IS_ANSWERED_PLAINLY`,
`THE_MATTER_GUARD_READS_THE_TABLE`, `A_QUESTION_NEVER_ANSWERS`. Pin to flip:
`tests/test_iq7_review_round.py::TestIQ7X7TheDeferralLimitOnOtherFamilies`.

⛔ **Carry pass 3's lesson across with the code.** The IQ-7 record states it
plainly: a rule built by *stripping what you recognise* is only as safe as the
strip list. Three passes each found a new phrasing; the loop ended only when the
rule became an allowlist that **fails closed**. My 16-of-17 extension above is
the same demonstration on the un-fixed families. Do not ship a deferral blocklist
here.

---

### IQ10-X1 — the top bar sheds buttons at Interface Scale 2.0

**Mechanism CONFIRMED structurally at HEAD. Pixel figures NOT re-measured here.**

`godot-client/project-sovereign/scenes/top_bar.tscn`:

* `BarContainer` (:19-23) — `HBoxContainer`, `anchors_preset = 10`,
  `anchor_right = 1.0`, **`grow_horizontal = 2`** (:22).
* `BarLayout` holds `ScreenButtons` (6 buttons, natural width) + `Spacer`
  (`size_flags_horizontal = 3`) + `RightSection` (5 items, natural width).
* Button texts carry their hotkey hints: `"Event Log (L)"`, `"Ledger (T)"`,
  `"Generals (G)"`, `"Diplomacy (D)"`, `"Dispatch (R)"`, `"Moniteur (N)"`.
* `RightSection` fixed costs: `MailboxButton` `custom_minimum_size = (110, 0)`
  (:107), `MenuBtn` `(28, 28)` (:123), plus `DPLabel`, `ThreatLabel`,
  `TalleyrandLabel` (up to `TALLEYRAND_SUMMARY_MAX_CHARS = 34` chars,
  `top_bar.gd:51`, applied at :406-409), `TurnLabel`, separation 8.

`grow_horizontal = 2` is **GROW_DIRECTION_BOTH**: when the container's minimum
width exceeds its anchored rect, it grows from the centre in *both* directions,
so the left edge goes negative. That is the whole mechanism, and the memo's own
numbers are self-consistent with it: `EventLogBtn` at x=−26 with `MenuBtn`
left-edge at x=798 (+28 wide = 826) describes an **852-logical-px bar centred in
an 800-logical-px viewport**, hanging 26 px off each edge; the mission board's
−65.5 describes 931 px.

`top_bar.gd` (453 lines) contains **no shed, no scroll, no clamp** — grep for
`clamp` / `scroll` / `custom_minimum_size` returns only an icon path and two
`threat_label.visible` toggles (:169, :363).

⚠ **UNVERIFIED here:** x=−26 / x=−65.5 / x=798. They come from
`docs/audits/IQ10_CLIENT_PASS_2026_09_19.md:56`. The harness's machine record
(`buttons_offscreen`, written by `tools/iq10_surface_screenshot.gd:550,615`) goes
to a run directory that is **not committed** — only the PNGs are
(`docs/audits/IQ10_TOP_BAR_BOOT_X2_2026_09_19.png`,
`IQ10_TOP_BAR_MISSION_COURT_X2_2026_09_19.png`). Re-measuring needs
`tools/iq10_run_captures.py` and the Godot binary, which I did not run (it writes
into `docs/audits/`). **Recommendation: commit the harness's JSON record beside
the PNGs**, or the next slice re-derives the numbers from a screenshot.

**What a fix touches:** `top_bar.tscn` layout + `top_bar.gd`. Cheapest honest
options, in order of how little they cost the player: (a) drop the "(L)"-style
hints from the button text at narrow logical widths — they duplicate tooltips and
the pause-menu reference; (b) `clip_contents` + a `ScrollContainer` on
`ScreenButtons`; (c) change `grow_horizontal` to 0 so overflow is at least
predictable on one side. The row's completion is already well stated: *no
`BaseButton` of the bar lies outside the logical viewport at 2.0 on either
board.*

---

### IQ10-X2 — the petition popup's "why Grant is disabled" line sits below the fold

**Mechanism CONFIRMED structurally, body measured. One correction to the row.**

Geometry (`godot-client/project-sovereign/scenes/incoming_proposal_popup.tscn`):

* `PanelContainer` (:33-42) — **fixed 680 × 440**, centred (`offset_left -340 /
  offset_right 340 / offset_top -220 / offset_bottom 220`).
* `ContentLabel` (:51-57) — `RichTextLabel`, `scroll_active = true`,
  **`fit_content = false`**, `size_flags_vertical = 3`.
* Buttons are `custom_minimum_size = (140, 45)` (:67-86), plus an `HSeparator`
  and `separation = 8`. Usable body ≈ **370 px**.
* `incoming_proposal_popup.gd:197` calls `Utils.clamp_centered_panel(...)`, which
  **shrinks to fit a small viewport — it never grows to fill a large one.**

Body assembly order (`incoming_proposal_popup.gd:50-164`): header → diplomat line
→ *"The petition:"* → clauses → Talleyrand → **crimson "Grant unavailable: …"**
(:141-147) → **lapse warning** (:152-155) → `content_label.append_text(...)`
(:164).

Real payload from the live board with the lord starved of DP (`p_iq10_x2.py`,
`p_iq10_x2b.py`) — Switzerland, subject `relief`:

```
grant_reason (139 chars incl. the label):
  "France cannot spare the diplomatic point — the petition stands until the
   turn ends; keep 1 DP to grant it, or refuse it."
clauses: 217 + 140 + 82 chars ; talleyrand_assessment: 183 chars
```

⚠ **My line arithmetic is an ESTIMATE** (78-char wrap, ~19 px/line): ~23 wrapped
lines against ~19 visible, putting the crimson block at lines 19–20 and the lapse
warning at line 22. The authoritative measurement is the committed frame
`docs/audits/IQ10_PETITION_POPUP_NO_DP_2026_09_19.png`.

**Correction to the row:** it says the crimson reason is *"the LAST line of a
scrollable body"*. It is not — **the lapse warning renders after it**
(:152-155), so **two** lines are below the fold, and the second is the sentence
that makes the decision urgent (*"This petition will lapse at end of turn."*). A
fix that only clears the crimson line leaves the lapse warning hidden.

**What a fix touches:** one of — (a) grow the panel toward available height (it
is 440 tall inside a 900-tall window at scale 1.0, so ~460 px is simply unused);
(b) move the crimson reason **above** the clauses, where the consequence is read
before the terms; (c) pin the crimson line + lapse warning outside the scrolling
region, under the separator. (b) is the smallest and also reads better.
Completion as filed: *the reason is visible without scrolling on a 1600×900
window at Interface Scale 1.0.*

---

## 2. `COMMAND_ROBUSTNESS_SPEC.md` — everything still open

Read: §2 (slice plan, :23-39), §3 (:40-48), §4 (parked candidates, :49-63), §5
(non-goals, :64-71), §7 (:245-279), §8 (:280-325), §9 (:326-421).

### §2 — open slices

| item | state | in scope for "make the typed road worth taking"? |
|---|---|---|
| **CR-6 (feature)** — Conversational Objection Negotiation: the player argues back, an LLM classifies into the existing deterministic Insist/Trust/Compromise buckets with a trust modifier | **USER DESIGN GATE, unbuilt.** The gate *slot* was consumed by the bare-attack mini-gate (§7) — the feature's own gate has never been held | **Needs its own gate.** It is the one item that gives the LLM a *mechanical* consequence (trust), which §5 forbids without a gate |
| **CR-7 (backlog)** — five distinct things bundled under one id | never scoped | **Split it.** Three of the five are in scope; two are not — see below |

**CR-7's five items, measured separately:**

1. **Conditional / compound orders; wire or replace `parse_multiple`; owns the
   `validation.py` "coming soon" string** (the row's stale `:195` is now
   `backend/ai/validation.py:313-314`).
   ⛔ **Measured live, and it is worse than a backlog item** (`p_multi.py`,
   `p_multi2.py`): `Soult and Lannes, attack Mack` **executes for Soult alone at
   1 AP** and Lannes is never acknowledged as an addressee; `Ney and Davout,
   fortify` acts on Ney alone and the reply does not contain the string "Davout"
   anywhere; the `warning` response key is `None` on both. `parse_multiple` exists
   (`parser.py:2204`) but its only non-test caller is `parser.py:2356`; it is not
   on the `/command` road. `everyone fortify` and `all marshals, hold position`
   both answer *"Which marshal …?"* at 0 AP.
   **In scope, and I would promote it out of "backlog"** — a sentence that
   silently performs half of itself is the same class as the rows above.
2. **Command-surface shortcuts** — in scope, small.
3. **Map-driven command context** — in scope; note the click road already
   converges here (§4).
4. **Fuzzy autocomplete dropdown UI** — **this is the "text predictor"**; see §5.
5. **R158 parse-confidence display** — in scope, but I would *not* build it as
   filed: showing `0.90` beside `hunt down mack`, which is confidently wrong,
   teaches the player to trust the wrong number.

**Deferred out of the phase (unchanged owners):** the anti-memorization /
creative-phrasing bundle (gated behind CR-4/CR-5 per ROADMAP) and the Groq
implementation (Pre-EA BYOK; `.env` documents `groq` as an unimplemented stub
that degrades to fast-parser-only). Voice-to-Text shipped as ROADMAP position 8
v1 (OS dictation) and rides this pipeline unchanged — so **every parser defect
above is also a dictation defect.**

### §4 — the parked candidates (the CR-6 half of the review is still open)

| candidate | recorded state | verdict |
|---|---|---|
| **Two-way channel** (*"Ney, what do you see?"*, *"Berthier, can we take Vienna before winter?"*) | HELD for CR-8 | **In scope in part, already half-built.** `backend/ai/question_desk.py` (353 lines) is the FACT desk behind `status`, shipped by FA slice 7 and fog-honest. §8 item 6 names the same thing. The un-built half is *advice*. Finish the FACT half inside a typed-road row; gate the ADVICE half |
| **Commander-intent orders** (*"Take Vienna"* → Berthier proposes an assignment, one confirm) | HELD as a CR-2 extension | **In scope.** The machinery exists — §7's `resolve_auto_attack` + `build_contact_attack_clarification` is exactly this shape for one verb. Generalising it is an extension, not a gate |
| **Tone parsing** (brusque vs flattering → trust modifier) | HELD for the CR-6 gate | **Needs its own gate** — mechanical trust effect, §5 non-goal |
| **Pre-battle councils** | HELD for its own mini-gate after CR-6 | **Needs its own gate** |
| **Autonomous "Grouchy Moment"** | RE-HOMED OUT of CR-5 | **Not a parser row at all.** Marshal-autonomy gate |
| **Mechanical delegation incentive** | PARKED for CR-6/CR-7 | **Needs its own gate** (mechanical). ⚠ But the *admission* on the row is in scope and unaddressed: this phase is on record declaring delegation **feel-first, mechanically optional** — i.e. the game currently gives a player no reason to type the interesting sentence instead of the safe one |

### §5 — non-goals (constraints, not work)

Three, all still binding: no LLM influence on mechanics (GR6); no phrasing
bonuses/penalties (CR-5b Flavor Echoing exempt as cosmetic); **mock mode stays
fully playable, every slice ships mock-safe fallbacks**. The third is the hard
constraint on any "text predictor" design — see §5.

### §7 — the bare-attack mini-gate: landed, two accepted residues

§7.4 records findings 3a/3b *"accepted as minor/pre-existing"*: a clarification
could list a retreating marshal (now an honest block message), and provenance
drops on the objection-confirm round-trip. Both are residue, neither is filed as
a row. The second compounds IQ9-X3.

### §8 — PARSE-NEG: items 1–4 are constraints, 5 and 6 are open

**Items 1–4 are what CR-6 must not undo**, and item 4 is the one that matters for
your question:

> 4. **A refusal does not escalate to the LLM** (`_should_fallback_to_llm`,
>    `backend/ai/llm_client.py:891`). *"If CR-6's gate returns yes on free-text
>    classification, this is the boundary that gets re-opened — with the
>    constraint that a model must never be able to re-derive an action the player
>    explicitly forbade."*

**Item 5 — conditional orders are refused, not executed.** Measured live
(`p_recheck.py`):

```
'Ney, retreat if outnumbered'       dAP=+0   EXECUTES: "Ney retreats from Rhineland to Lorraine."
'Ney, attack when Davout arrives'   dAP=+0   refused: "that is a contingency, not an order"
'Ney, hold until Davout arrives'    dAP=-2   the `until` exception: a real StrategicCondition
```

The pinned exception is real and reproduces: `Ney, retreat if outnumbered`
**executes the retreat** (pin `parseneg-retreat-if-outnumbered-executes`),
because `retreat` survives the clause blanking as a bare free verb.
**Verdict: needs its own gate.** A real conditional-order system means new
`StrategicCondition` types, a per-turn evaluator and a save-format change — not a
command-experience row. ⚠ But the *specific* pinned exception is a correctness
wart that could be closed inside a typed-road row: an `if`-clause that blanks to
a bare free verb should be refused like its siblings, not executed. That is one
guard, not a system.

**Item 6 — a question routes to `help`, after diplomatic routing.** The spec: *"A
question-answering Berthier is CR-6's to build; when it exists, it replaces the
`help` route, not the guard."*

Measured live (`p_recheck.py`, current tree — the sibling's edit is active):

```
'can we take Vienna before winter'   [HELP DUMP]
'what should I do'                   [HELP DUMP]
'can Ney attack Mack'                [HELP DUMP]      <- new, from the CX edit
'can you attack Mack'                dAP=-1, MARCHES  <- the polite-order arm
'is Mack stronger than Ney'          [HELP DUMP]
'who is winning'                     [HELP DUMP]
'what does Austria want'             [HELP DUMP]
'where is Mack'                      answered: "Mack of Austria was reported at Swabia"
'where is Zorglub'                   [HELP DUMP]
```

Eight of nine reasonable questions dump the full COMMAND REFERENCE, and
`where is <X>` is answered only because `question_desk.py` exists behind `status`.
**Verdict: in scope, and the single highest-leverage item in the whole spec for
"make the typed road worth taking"** — the desk is already built and fog-honest;
the work is routing more question shapes to it and replacing the help dump with
an honest *"I cannot answer that, Sire"*. The LLM-phrases-only half stays
GR6-safe. ⚠ The *advisory* half (*"can we take Vienna before winter"* = a
judgement) is the part that needs the gate.

### §9 — IQ-9: the three routed rows, all reproduced above

Also recorded there: `_StubResolvingParser`'s mode omission (recon F4) left in
place deliberately.

**Corpus count, corrected:** the task brief says 447.
`tests/data/parser_golden_corpus.json` has **447 `entries`** (4 `live_only`, 49
`mock_only`) — and `python -m backend.ai.parser_eval` reports **686/686**,
because that is entries × applicable worlds. Both numbers are right; they count
different things. The spec's §1 "681 → 686" note refers to the pair count.

---

## 3. Other OPEN rows whose subject is the typed road

Census script `p_openrows2.py` over `BUG_FIXES.md` + `DESIGN_REFINEMENT.md`, then
hand-verified. (My first pass over-reported badly: rows whose final cell describes
the *fix* carry no ✅, so a naive status scan calls them open.)

**Genuinely open and in scope:**

| row | filed text (abridged) | verified? |
|---|---|---|
| **IQ9-X1 / X2 / X3** | above | ✅ reproduced |
| **IQ7-X7** | above | ✅ reproduced |
| **IQ10-X1 / X2** | above | ✅ mechanism confirmed |
| **NPC-12** (P2, `BUG_FIXES.md:8421`) | *"Raw camelCase enemy keys reach the terminal on at least seven player-facing surfaces (`Ney pursues ArchdukeCharles`), while the morning dispatch spells the same man `Archduke Charles`. This is how the player learns the spelling NPC-1 then punishes."* Header says the pursue/support lines were fixed but **"the wider census is NOT closed"** — ~426 enemy-reachable interpolations; `game_logic/combat.py` and `ledger.py` have never imported the humaniser | ✅ **CONFIRMED at HEAD.** `grep -c humanize_entity_name` = **0** in both `backend/game_logic/combat.py` and `backend/game_logic/ledger.py`; `combat.py` has **71** raw `.name}` interpolations (e.g. :61, :296, :359, :384, :414). Live (`p_npc12.py`): one battle vs ArchdukeJohn produced **4 player-facing lines carrying the raw key and 0 carrying "Archduke John"** — the MUSTER line, the `[Shield]` line, the combat result line, the rout line. `battle_report` is clean (0). ⚠ **The round-trip is OK** (`p_typable.py`): `ArchdukeJohn`, `Archduke John` and `the Archduke John` all parse. So this is a display defect, not a parse defect — but it is exactly the IQ10-6 class (*the game's own printed sentence must be typable*) one step upstream |
| **XR-2** (P4, `BUG_FIXES.md:10497`, *"routed → CR backlog (owner: the standing parser-eval harness; add a corpus row when touched)"*) | *"A bare verb-phrase reply to the CR-5 literal ASK ('give battle') typed into the terminal parses as a fresh command and can surface a raw `'generic'` placeholder ('Region "generic" not found') — the live LLM hallucinates a target for target-less verb phrases."* | ⚠ **UNVERIFIED** — needs a live-mode CR-5 literal ASK in flight; the cassette set does not cover it |
| **EAS-2** (P3, `BUG_FIXES.md:10301`) | *"The campaign log has no importance tier. `campaign_log.gd` renders every row at the same size, coloured by category, never by weight."* Disposition routes it to *enemy-phase composition* work | not re-measured; tangential to the typed road (it is the output surface, not the input) |
| **CA9 N4** (P1, `BUG_FIXES.md:8892`) | *"The pending marshal petition never expires, never re-validates, and is answered against live state — a turn-11 card served on turn 16 would have spent 1 AP on the wrong quarrel."* CLAUDE.md records it as *"a P1 that is NOT fixed — memo §9 Q8 makes it a design question"* | not re-measured; **needs its own gate** (owned by `PETITION_POPUP_REVISIT_SPEC.md`, slices B1–B5) |

**⛔ One STALE open row, found by reading the code:**

| row | why it is stale |
|---|---|
| **EAS-1** (P2, `BUG_FIXES.md:10300`) — *"Making mock the shipped default ARMS THE CHEAT CONSOLE … `meta_executor.py:2037-2043` computes `live_client_armed = key_source != "none"` … a keyless build leaves the cheat surface OPEN"*, disposition *"Re-gate on explicit debug alone, in the same slice that makes mock the default (ROADMAP position 4)"* | **Already done.** `backend/commands/meta_executor.py:2421-2438` now reads: *"cheats require an EXPLICIT debug opt-in (Aug 2026 health-check shippable-build P0). The old CR-3(d) gate armed cheats whenever no live key was configured…"* — the gate is `game_state["debug_mode"] or DEBUG_MODE=true`, and `live_client_armed` no longer appears in the file. CLAUDE.md's Aug 15 pre-build entry records the same landing. **The row was never struck.** Recommend striking it with a pointer to that landing |

**False positives from my first census, recorded so nobody re-chases them:**
FA-28 / FA-41 / FA-55 / FA-76 (all marked *DUPLICATE (Sept 2 verification)*;
`tools/fa_row_tally.py` reports **0 open of 268**), FA-N78, PC-0, PS18-4, WO-D12,
IQ7-X5, IQ7-RV2, IQ-2.2, IQ-2.9, IQ4-4, IQ4-R13, IQ5-11, IQ5-RV2, IQ5-RV6 — all
fixed or disposed.

**Nothing open anywhere about:** the help text itself, the tutorial's typed road,
or a region-panel chip. (§4 explains why the chips are quiet.)

---

## 4. Two things worth knowing before the row is scoped

### The click road IS the typed road

`godot-client/project-sovereign/scripts/region_panel.gd:26` declares
`signal region_command(command: String)` and every action chip emits a **typed
command string** — `do:recruit infantry in <region>`,
`do:build watchtower in <region>`, `do:repair buildings in <region>`,
`do:build ships`, `do:buy substitutes for <marshal>`, `do:land …` (:272,
:372-382, :412-441). I ran each concretised template through `POST /command`
(`p_chips.py`): all parse, none is refused *by the parser* — refusals are honest
executor gates (*"No war damage to repair in Paris"*, *"No marshal is available
to receive reinforcements at Paris"*).

⚠ One artefact of my own fixture, not a defect: I concretised
`buy substitutes for <marshal>` with a region name and got *"Marshal 'Paris' not
found"*. That is my probe being wrong, not the chip.

**Implication:** every parser defect above is reachable from a button, not only
from the keyboard — and conversely, a "text predictor" can be seeded from the
chip vocabulary, which is already a curated list of canonical sentences.

### Two parser artefacts that do NOT reach the player — do not file them

While sweeping natural phrasings I saw the parser mint phantom targets:
`Ney, fall back and dig in` → `retreat` with `target="And Dig In"`, and
`Ney, march at dawn` → `move` with `target="Dawn"`. **Through `POST /command`
both are refused honestly at 0 AP** (`p_phantom.py`): *"I could not make out a
destination in that order, Sire - name a province (e.g. 'Ney, move to
Rhineland')."* They are parser-level artefacts, executor-gated. Not the WO-13
class. Recorded so the next reader does not re-file them.

Two that *do* cost the player something, both self-announcing:
`Ney, hold the line` → a 2-AP standing HOLD on Rhineland with *"(Our maps read
Rhineland as the province nearest your order, Sire.)"*, and
`Ney, press the attack` → 1 AP and Ney marches on Mack with *"Your words named no
foe our maps know, Sire — Ney marches on Mack at Swabia, the nearest in sight."*
Honest, but paid.

---

## 5. The two questions behind the brief

You asked two things the backlog does not answer directly. Both are now measured.

### "Is routing to the LLM worth it?"

**On everything the project currently measures: no — and that is a statement
about the instrument, not about the model.**

| measurement | value | probe |
|---|---|---|
| Golden corpus, mock mode, zero live calls | **686 / 686 passed** | `python -m backend.ai.parser_eval` |
| Corpus utterances that clear the 0.7 gate (no live call) | **381 / 443 = 86.0%** | `p_escalation.py` |
| Corpus utterances that escalate | **62 / 443 = 14.0%** | " |
| Of those 62, how many the deterministic road already gets right | **all of them** (the corpus is 686/686 in mock) | " |
| "Confidently wrong" — cleared the gate, then the pipeline refused | **1 / 381 = 0.3%** (`Attack Marshal Blucher`) | " |
| Confidence histogram | 0.50 ×44 · 0.55 ×18 · 0.75 ×1 · 0.80 ×53 · 0.90 ×142 · 0.95 ×177 · 1.00 ×8 | " |

⚠ **The corpus is biased and I am not going to pretend otherwise.** It was seeded
from the parser's own tests (§2 CR-1), so it measures what the deterministic road
handles. The honest reading: *the LLM adds nothing the project's own regression
gate can see, and the project has no instrument that looks anywhere else.*

The un-biased sample that does exist is the corpus's own
`live_phrasing_backlog` — 18 phrasings authored as "live-LLM-only capabilities
today". Measured on the 1805 board (`p_backlog.py`): **8 already work without the
model · 7 escalate properly (the model earns its keep) · 3 are killed above the
gate by IQ9-X1.**

**The three levers, in order of measured value:**

1. **Fix IQ9-X1.** Today a whole class of natural phrasing is *prevented* from
   reaching the model. Escalation is worth nothing on sentences that never
   escalate.
2. **Fix IQ9-X3, then instrument.** `parse_mode` is the only telemetry that
   exists and it counts successes only. Until a failed live call is recorded as a
   live call, "is it worth it" is unanswerable from data. Add: live calls per
   session, escalations that changed the outcome, escalations that failed.
3. **Only then tune the gate.** 0.7 (`llm_client.py:63`) has never been measured
   against outcomes. The histogram shows a hard cliff — 62 utterances sit at
   0.50/0.55 and 381 sit at ≥0.75; **exactly one row sits at 0.75**. So the gate
   could move anywhere in (0.55, 0.75] and change nothing on the corpus. The
   interesting move is the opposite one: escalate some *high*-confidence parses,
   because that is where the measured failure lives.

⚠ **One structural note for CR-6's gate:** PARSE-NEG §8 item 4 forbids a refusal
from escalating. That is the right rule, and it is also why the model cannot
rescue `hunt down mack` — the word scan produces a *refusal*, and refusals do not
escalate. Any fix to IQ9-X1 must be careful not to re-open item 4's boundary by
accident.

### "A text predictor / a way to make it more efficient"

Measured facts about the surface it would live on:

* The command line is a **bare `LineEdit`** —
  `godot-client/project-sovereign/scenes/main.tscn:238-242`,
  `placeholder_text = "Type command..."`. No completion, no ghost text, no
  suggestion list.
* Input assistance today is **up/down history only** — `main.gd:347-349`
  (`command_history`, `history_index`) and `main.gd:929-934` (`KEY_UP` →
  `_history_previous`, `KEY_DOWN` → `_history_next`). `Tab` is not bound in
  `_on_command_input_gui_input` (`main.gd:908-937`).
* **There is no dry-run parse endpoint.** Full endpoint census of
  `backend/main.py` (52 routes): `POST /command` is the only parse road, and it
  **executes**. A predictor cannot ask "what would this parse to?" without
  running it.
* **But the capability already exists in-process:** `LLMClient.fast_parse`
  (`backend/ai/llm_client.py:976`) — *"Deterministic keyword-parser pass only —
  never calls the LLM. Used for cheap trial parses"*, already used by CR-2's
  clause split. It is 86 %-accurate on the corpus, sub-millisecond, and needs no
  key.
* CR-7 already owns this as *"fuzzy autocomplete dropdown UI"* — unscoped,
  unbuilt.

**What I would put in front of the user, given the measurements:**

1. **A `POST /parse_preview`** wrapping `fast_parse` — pure, no AP, no world
   mutation, no live call. Returns the resolved `{marshal, action, target}`, the
   confidence, and whether the road would escalate. This is the missing
   primitive; everything else is a client on top of it.
2. **Ghost-text completion in the `LineEdit`**, seeded from three lists the game
   *already* has and keeps current: the live marshal roster
   (`_get_player_marshals`), the live region roster (`_get_known_regions`), and
   the **chip vocabulary** from `region_panel.gd` (§4 — already canonical
   sentences). ⚠ **Must respect fog**: the completion list is a *speakable*
   roster, which is the same distinction IQ9-X2 needs. Build that split once and
   both rows consume it.
3. **Echo the resolution, not the confidence.** R158 proposes showing the
   confidence number; the measurements argue against it (0.90 on `hunt down
   mack`). Show what it *resolved to* — *"Ney → attack → Mack"* — which is
   falsifiable by the player and does not teach them to trust a bad number.
4. ⚠ **The §5 non-goal binds:** *"Mock mode remains fully playable: every slice
   ships mock-safe fallbacks."* A predictor built on `fast_parse` satisfies it by
   construction. One built on a live model does not, and would need the gate.

**Efficiency, separately:** the project already banked the big win — 86 % of
commands never touch the network, and CR-3(c)'s `llm_error` guard caps a request
at **one** blocking live call (`reparse_with_llm`, `llm_client.py:984`;
`ParseResult.llm_error`). Prompt caching is deliberately not used and CLAUDE.md
says why, so it is not re-litigable here. The remaining efficiency item is not
latency, it is **waste**: on the corpus, 62 escalations bought 0 corrections —
and we cannot see the real number because of IQ9-X3.

---

## 6. Scope recommendation

**In scope for a row about making the typed road worth taking** (no new gate
needed; all correctness or legibility on existing machinery):

* IQ9-X1 — with the corrected prescription (route a marshal-less live parse to
  the CR-2 clarification; do not "adopt a marshal" it never returned)
* IQ9-X2 — the *speakable roster* split, on the `_display_candidates` shape.
  ⚠ State the helpfulness trade on the row
* IQ9-X3 — and the telemetry that depends on it
* IQ7-X7 — generalise `petition_plain_answer`'s closed grammar per family.
  ⛔ allowlist, never a strip list
* IQ10-X1, IQ10-X2 — client layout, both small
* NPC-12's remainder — `combat.py` + `ledger.py` at the humaniser
* **CR-7 item 1** (the silently-halved multi-marshal sentence) — promote it out
  of "backlog"; it is a correctness defect, not a feature
* **§8 item 6** — route more question shapes to `question_desk.py` and replace
  the COMMAND REFERENCE dump. Highest leverage in the spec
* **§8 item 5's pinned exception only** — an `if`-clause that blanks to a bare
  free verb should be refused like its siblings
* **CR-7 item 4** — the predictor, built on a new `/parse_preview` over
  `fast_parse`
* §4 **Commander-intent orders** — generalise §7's `resolve_auto_attack` shape
* EAS-1 — strike the stale row

**Needs its own gate:**

* **CR-6 proper** (Conversational Objection Negotiation) — an LLM picking a
  bucket that moves trust; §5 non-goal
* §4 **Tone parsing**, **Pre-battle councils**, **Mechanical delegation
  incentive** — all mechanical
* §4 **Autonomous "Grouchy Moment"** — marshal autonomy, not parsing
* §4 **Two-way channel**, *advice* half only — the FACT half is built and in scope
* **§8 item 5 proper** — a real conditional-order system (new
  `StrategicCondition` types + evaluator + save format)
* **CA9 N4** — owned by `PETITION_POPUP_REVISIT_SPEC.md` slices B1–B5
* Any change to the 0.7 gate not preceded by the IQ9-X3 instrument

---

## 7. Corrections this recon makes to the record

1. **IQ9-X1's completion is unbuildable as written** — the retried parse resolves
   no marshal and the fast pass mis-bound none; the mis-binding is internal to
   `_apply_fuzzy_matching`.
2. **IQ9-X2 is not a suggestion-list defect.** It is a 12-name existence +
   nation + treaty-state oracle on the ordinary attack and address roads, at
   0 AP. The filed completion closes the smallest road.
3. **IQ9-X3 is not confined to a no-parse failure** — it is every non-adopted
   live road, including the CR-2 retry and API errors; the control case proves
   the stamp is correct only on success.
4. **IQ10-X2's crimson line is not the last line** — the lapse warning renders
   after it and is also below the fold.
5. **EAS-1 is stale** — re-gated on explicit debug at
   `meta_executor.py:2421-2438`; the row was never struck.
6. **The corpus is 447 entries / 686 entry-world pairs** — both figures in the
   record are right, about different things.
7. **`validation.py:195`** (the CR-7-owned "coming soon" string) is now
   `backend/ai/validation.py:313-314`.
8. **My own first IQ7-X7 petition fixture was wrong** and briefly suggested the
   petition grammar was not protecting anything. It is. Build petition fixtures
   from `vassal.petition_terms` + `deliver_ai_proposal`.
9. **Two phantom-target parses are executor-gated** and should not be filed.

---

## 8. What I could not verify

* **IQ10-X1's pixel figures** (x=−26 / −65.5 / 798) — need the Godot capture
  harness; the machine record is not committed, only PNGs. Mechanism confirmed
  structurally instead.
* **IQ10-X2's exact fold position** — my ~23-lines-vs-~19-visible is an estimate;
  the committed frame is authoritative.
* **XR-2** — needs a live CR-5 literal ASK in flight; no cassette covers it.
* **Whether the CR-2 dropped-tail warning fires on `Ney, attack Mack, then
  fortify`** — the `warning` response key is `None`, but I did not search the
  1,674-char message body for the sentence.
* **Real-world escalation value** — structurally unmeasurable today, which is
  IQ9-X3's real cost.
* **EAS-2, CA9 N4** — read, not re-measured.
