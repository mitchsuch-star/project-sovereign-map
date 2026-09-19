# ROW CX — "THE HAND ON THE KEYBOARD"

**Opened September 19, 2026** by user direction, immediately after the
Improvement Queue closed:

> *"Make the typed road worth taking, and answer in writing whether it is."*
> … *"on top of above a text predictor would be great or a way to make it more
> efficient. is routing to llm worth it and how can we make it better as
> well."*

**This spec is the owning record for row CX** — the gate question and its
ruling, the per-slice landing records, the dissents and the re-open conditions.
`docs/COMMAND_ROBUSTNESS_SPEC.md` §10 carries the *technical* record for the
parse pipeline, as it does for every CR slice; `docs/SYSTEMS_REFERENCE.md` §50
carries the rules.

The row answers **three** questions, not one:

1. **The gate.** Is typing fun enough to justify not clicking? *Measured, and
   the answer is allowed to be no.*
2. **Efficiency.** Can typing be made cheap — a predictor, or something better?
3. **The model.** Is routing to the LLM worth it, and how is it made better?

---

## §0 THE RECON OF RECORD

Twelve read-only censuses plus a refuter per census, September 19, 2026, at
`f7008582`. Reports are cited by name throughout; the load-bearing figures are
reproduced here with the probe that produced them, because a figure with no
archive is uncitable (the IQ-8 table rule).

⛔ **The caveat that governs every frequency number in this row.** *No human
has ever played a measured campaign in this repository.* All 8,422 typed
commands in the archive are **driver** commands from authored scripts, and 20
of the 23 commanded archives run `commanded_full40.json`, whose own `_note_d6`
key says it exists to "spend all four military actions every turn" — so 68 of
its 83 military-AP successes are fortify/unfortify/drill against **9 marches
and 6 attacks in forty turns**. Frequency here is the best available proxy for
what a played France issues. It is not evidence of human behaviour, and this
row does not pretend otherwise.

---

## §1 THE THREE SETS — what each road can express

The brief asked for the click set, the parser set and the executor set, and for
every gap between them to be a finding. The first finding is that the framing
needed correcting:

**The chips ARE typed commands.** `region_panel.gd:136-140` emits the literal
string a player would type and `main.gd:6399-6409` sends it through
`api_client.send_command`. Of the client's non-typed affordances, ~70 distinct
strings take that road; 16 POST and 15 GET endpoints take a structured one; the
rest are local UI. So for most intents the two roads **converge at the fast
parser**, and *a chip inherits every executor refusal* — measured: `recruit
infantry in Paris` fails at boot ("No marshal is available to receive
reinforcements at Paris") and the Paris Recruit chip sends exactly that string
and fails identically. **A chip removes naming risk, never gate risk.**

But they are not two ways to do the same thing, because each road is CLOSED on
a set the other owns:

| | typed road | click road |
|---|---|---|
| **closed to it** | the whole diplomatic family — `main.gd::_redirect_diplomatic_command` intercepts 114 keyword forms on the typed path *and only there*, and when it fires **nothing is sent** | **movement**, and with it retreat / hold / support / garrison |
| **sole road** | move, march, retreat, hold, support, garrison, set war purpose, cancel, and every question | propose peace, declare war, break a treaty, send an envoy, invest, autonomy, cede, request terms, read any ledger |

**Zero chips emit move, march, retreat, hold, support, pursue, charge,
bombard, form_square or recall**, and the map offers no substitute:
`map_renderer_base.gd:2041-2055` maps left-click to `region_clicked` and
nothing else; there is no select-then-click-a-destination gesture anywhere in
the client.

⚠ **And the corpus does not know about the client's own gate.**
`_redirect_diplomatic_command` eats **111 of the 447 golden-corpus utterances
(24.8%)** before the backend sees them. Those rows certify a backend that is
correct and a road the player cannot take. That is not a defect — it is user
ruling **G1**, recorded — but the instrument should say so. **CX-5 owns it.**

---

## §2 THE GATE — RULED

**38 intents measured on both roads** (`two_roads.md`, and every click path
read out of the `.gd` rather than assumed):

> **TYPED WINS 9 · CLICK WINS 22 · PARITY 7.**

On a count of intents the click road wins nearly 2:1. **That is the wrong
number to steer by.** Weighted by the 1,416-command script census:

| verb head | share | road |
|---|---|---|
| fortify + unfortify | 15.3% | parity (chips exist) |
| attack | 14.3% | **typed-only for 7 of 8 marshals at boot** |
| move + march | 14.2% | **typed-only** |
| status | 14.1% | parity |
| drill | 6.6% | parity |
| assess | 3.7% | typed |
| recruit | 3.2% | click wins |
| build | 2.8% | click wins |
| hold | 1.9% | **typed-only** |
| propose / invest / declare / mission | ~7% | **click-only** |

**Of the 22 CLICK WINS, exactly two are per-turn routine — recruit and build,
together 6.0% of issued commands.** The other twenty are rare, one-off or
reactive.

### The ruling

> **The click road wins the catalogue. The typed road wins the turn.**
>
> A player can complete an ordinary turn using only the typed road. A player
> cannot complete a single ordinary turn using only the click road — **the
> first `move` order ends the attempt.**
>
> So the honest answer to *"is typing fun enough to justify not clicking?"* is
> not a yes or a no. It is: **the two roads are complements, not substitutes,
> and the game has been treating them as substitutes.** Typing owns the army;
> clicking owns the cabinet. Neither is going away, and the row's job is to
> make each one good at its own work rather than to pick a winner.

### What typing is FOR — and the asymmetry that actually matters

Every one of the 22 CLICK WINS was won on **information, not on clicks**: the
levy's live price, the building's delivered yield, the expedition's odds, the
blockade's forecast, the commission bench's names, the ceded province's tribute
cut. Two clicks against twenty characters is not why the chip wins.

> **The chips are priced. The typed verbs are blind.**

That points at a cheaper remedy than building a movement UI, and it is this
row's central build: **the typed road should quote the same terms the chip
quotes**, from the same source, so the two cannot drift.

And there is one thing the typed road can do that no chip can ever do: **ask a
question.** That is the typed road's sole claim, it was measured almost
entirely broken, and CX-1 and CX-2 are about making it real.

---

## §3 LANDING RECORDS

### §3.1 CX-1 — "A QUESTION NEVER ORDERS" ✅ LANDED September 19, 2026

Two halves, both P1, both found by driving the shipped board rather than by
reading.

**Half one — the question that fought.** `is_question` required an
interrogative lead plus one more signal (a "?", a first person, or an
auxiliary). Whole families carried none, so the keyword chain read the
imperative inside the question and executed it. Measured through
`POST /command` on a fresh 1805 boot:

| utterance | what it did |
|---|---|
| `why not attack Mack` | **a real battle** — AP 4→3; Ney −946, Davout −1,025, Soult −1,980, Lannes −709, Murat −867, the Emperor's Guard −394 |
| `why not retreat` | **a general retreat** — all eight corps fell back, Massena losing 2,100 men to attrition |
| `what about attack Mack` · `how about attack Mack` · `is it time to attack Mack` | a battle |
| `is it time to build a depot in Paris` | 300 gold and an admin AP spent |
| `can Ney attack Mack` · `may` · `does` · `is Ney attacking` | a battle |
| `is Swabia defended` | a whole-army defend at confidence 0.90 |
| `retreat?` | the whole army marched |
| `who holds Swabia` | *"Which marshal shall hold Swabia, Sire?"* — the question desk's own advertised kind, shadowed by the HOLD verb and **one answer** from an order |

**Five arms, one lever `clause_guards.A_QUESTION_NEVER_ORDERS`:**

* **(a)** `who` / `whom` / `whose` / `why` lead a question on their own — no
  English imperative opens with them. Deliberately four words and not "every
  WH-lead": the corpus itself pins `when ready then retreat` as a RETREAT.
* **(b)** the **deliberative openers** — `what about …`, `how about …`,
  `is it time to …` — the way a person MUSES at a war table.
* **(c)** the **copular and perfect leads** (`is are was were am does did has
  had`) have no imperative form in English at all, so they ask whatever
  follows. This is what closes `is Swabia defended`, whose subject is a
  PROVINCE and which no roster of commanders could have reached. `have` is
  deliberately excluded — *"have Ney attack Mack"* is the causative imperative
  and a real order.
* **(d)** **THE SUBJECT DECIDES** for the leads that DO have an imperative form
  (`can could may might will would shall do should`): a modal naming a third
  party asks about him; only the second person commands. This is FA slice 7's
  own rule for will/would/shall, extended and given the live roster. It stands
  down before a trailing clause, because `should Mack advance, fortify` is an
  inverted CONDITIONAL and belongs to the condition guard's refusal.
* **(e)** an **unaddressed** line ending in `?` is a question. An addressed one
  keeps its order: `Ney, attack Mack?` is a hesitant order and has been
  documented as one since FA slice 7.

**Deliberately left executing, stated rather than overlooked:** `end turn?`
(`is_bare_end_turn` strips a trailing `?` ON PURPOSE — FA-R4; the behaviour it
replaced, where a question mark saved you from an accidental turn advance and
its absence did not, was itself the defect that rule exists to kill),
`Ney, attack Mack?`, `can you attack Mack`, `would you have Ney attack Mack`,
`do attack Mack`, `when ready then retreat`.

**Measured reach: a 684-case sweep of (lead × verb) on a fresh board per case
goes 30 executing → 9, and all nine are the controls above.** The golden corpus
moves **0 of 447 entries** under either arm of the lever.

**Half two — "AN ADDRESS NEEDS NO COMMA".** `_unbound_addressee` keyed the
whole rule on `raw.partition(",")` and returned None when there was no comma,
on the reasoning that a bare order has no addressee. True of `attack Mack`;
false of the same sentence with a name in front of it, and the difference is
one keystroke:

```
"Nay, attack Mack"   → refused free: "There is no 'Nay' in the order of
                       battle, Sire. Whom did you intend?"
"Nay attack Mack"    → SOULT — never named — fought a real battle.
                       1 AP, 265 gold, five corps relocated, no question asked.
```

Far wider than a typo: `Grouchy attack Mack` (a commission candidate on the
bench), `Berthier attack Mack` (the chief of staff), `Wellington attack Mack`
and `Blucher attack Mack` (foreign marshals) and `Zorglub attack Mack` all sent
Soult in, and **`Wellington retreat` marched the entire army back.**

With no comma the addressee is the leading run of words BEFORE the first order
verb — empty for a genuinely bare order, so `attack Mack` is untouched by
construction. Lever `CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA`.

⛔ **The arm's own first draft shipped a regression and the pins caught it:**
the leading run of `can you attack Mack` is `"can you"` and of `do attack Mack`
is `"do"`, so both polite/emphatic imperatives were refused as an unknown
marshal. The run must contain no function word and no collective (`all
marshals attack` addresses the army, not a person).

⚠ **One filed claim corrected by measurement.** The recon listed `Davoust
attack Mack` as unbindable; it is not — FA-80's typo repair binds it to DAVOUT
before the guard is reached, and the order goes to the man the player meant.
Pinned as the better outcome so it cannot regress into a refusal.

**Two pins flipped consciously.**
`test_fa_slice7…::test_the_polite_order_stays_an_order` recorded `can Ney
attack Mack` as a polite order; it fought a battle, and the subject rule amends
it (the no-roster arm still pins the original reading).
`test_iq7_review_round…::test_a_deferred_answer_still_answers_an_ordinary_letter[is
that a yes]` flips **on its own instruction** — its docstring says *"when that
row lands these lines must resolve to None and this pin FLIPS"*. `is that a
yes` is not a deferral, it is a question, and arm (c) closes it with no change
to the dialogue layer. ⚠ **IQ7-X7 is only PARTLY closed**: the other six lines
are real deferrals, carry no interrogative lead, and stay CR-6 proper's.

Tests: `tests/test_cx1_a_question_never_orders.py`.

### §3.2 CX-2 — "BERTHIER ANSWERS THE BOARD" ✅ LANDED September 19, 2026

Asking a question is the one thing the typed road can do that **no chip can
ever do**. It was the typed road's sole claim, and it was measured almost
entirely broken.

**The finding.** Against the twelve questions the user named, driven on the
shipped board across 152 rows: **two were answered, ten were not, and eight of
the ten were answered by nothing at all in any phrasing.** Every one of the
ten returned the same **12,717-character COMMAND REFERENCE** — which contains
the words `status`, `where is`, `who holds` and `how many men` **zero times**.
The desk that could have answered four of them was unreachable from the only
surface the game hands a lost player.

**And the same blindness sat one layer out.** `_berthier_mock_response` — the
copy the player reads at the exact moment the parser has failed them —
hardcoded three courts by name: *"propose peace with Prussia"*,
*"Talleyrand, propose alliance with Austria"*, *"declare war on Prussia"*.
**On the shipped 1805 boot France is at PEACE with Prussia**, so the game's own
recovery advice was an act of war against a neutral — fifty-two lines below
`_hostile_first`, the guard FA-80(c) added to stop precisely that for the
ATTACK templates and which the diplomatic ones never inherited. Worse, all
three name a road the shipped client REDIRECTS (ruling G1), so the recovery
text taught a sentence that **cannot be sent**.

**What landed.**

* **Nine board kinds** on the desk (`classify_board_question` /
  `answer_board_question`, lever `THE_DESK_ANSWERS_THE_BOARD`): the treasury,
  the war score, whether we are at war with a court, a court's design, whether
  a corps can reach a province, what an attack would look like, what may be
  built, what a thing costs, and what can be ordered at all. They are matched
  in their own pass AFTER the five fact kinds, which keep precedence on every
  phrasing they already own, and `answer_question` gained a guard limiting it
  to its own five — without it a `reach` question fell into
  `_answer_own_marshal` and was answered *"Marshal Ney stands at Rhineland
  with 24,000 men"*, which is true and is not the answer.
* **Every answer reads the seam the MECHANIC reads** — `_build_economy`,
  `get_war_score_for`, `get_active_agenda`, `find_path(passable_for=…)`,
  `_build_muster_preview` **and its own `_format_muster_lines` renderer**,
  `region.can_build`, the levy pricer. So a quoted figure is the applied
  figure, and *"what happens if I attack Mack"* prints the exact string the
  order itself would print, for nothing. **This is §2's asymmetry closed: the
  chips were priced and the typed verbs were blind.**
* **`backend/ai/counsel.py`** — ONE board-derived source for *what can I do*,
  read by the desk's `options` kind, by Berthier's shrug and by the router. It
  asks `MovementExecutor.move_refusal_probe` before proposing a march and
  `is_at_war` before proposing a battle, names no enemy outside
  `get_visible_enemies`, and never proposes a diplomatic verb — it names the
  Cabinet as a door instead.
* **The router**: a question the desk cannot take gets a sentence, the surface
  that holds the answer (*"the campaign log (press L)"*), and the orders that
  would actually be carried out. Measured **370 characters against 12,717**.
  A SYNTAX question (*"how do I attack?"*) still gets the manual, because
  there the manual is the answer.

**Measured: 41 of 41 driven questions answered, 0 walls.**

**Pins flipped consciously, each with its reason on the row** — corpus
`how-is-the-war-going` (`help` → `status`; the manual holds no war score) and
`parseneg-can-i-attack-mack` / `i-question-still-help` (`help` → `status`,
scoped to 1805 with legacy twins added), plus
`test_fa_slice7…::test_guidance_and_feasibility_keep_the_command_reference`,
split in two. All four rest on **ruling R7's own re-open condition**: *"A
question-answering Berthier is CR-6's to build; when it exists, it replaces
the `help` route, not the guard."* The guard is untouched — none of them
fights a battle or spends an action.

⚠ **A false paragraph was CORRECTED IN PLACE rather than deleted**:
`question_desk`'s module docstring claimed *"feasibility and advice … stay on
the COMMAND REFERENCE … the four corpus rows pinning `can I attack Mack?` ->
help are untouched by construction."* CX-2 took feasibility; the docstring now
says so, says why, and says what is still CR-8's.

Tests: `tests/test_cx2_berthier_answers_the_board.py`.

---

## §4 THE MODEL — RULED (CX's second question)

**Measured, keyless, on the committed cassettes and the golden corpus:**

| measurement | value |
|---|---|
| escalation rate, golden corpus (447 entries × both worlds) | **45 / 692 = 6.5%** |
| escalation rate, the 1,416 committed playtest commands | **48 / 1,416 = 3.39%** |
| escalation rate, the two 40-turn COMMANDED arms | **0 / 160 and 0 / 173 = 0.00%** |
| escalation rate, the client's CHIP road | **0 / 22 = 0.00%** |
| escalating corpus rows whose `expected` is `success: false` | **25 / 29 = 86%** |
| escalating corpus rows where the corpus wants a NEW ORDER | **0 / 29** |
| `live_only` corpus rows (the model's whole measured value) | **4 of 447** |
| `mock_only` rows (the deterministic chain's) | **49 of 447** |
| input per parse call on the 1805 boot | **19,619 chars ≈ 4,904 tokens** |
| live calls per request, measured ceiling | **2** (the monetization memo claims ≤1) |
| gate needed to catch the measured confident-and-wrong defects | **> 0.90 → 50.7% of commands escalate** |

### The ruling

> **As shipped, escalation is close to worthless — not because the model is
> bad, but because the gate routes the wrong sentences.** It fires on 3.4% of
> real play and 0.00% of a commanded campaign; 86% of what it catches is a
> sentence the corpus says must be REFUSED; the deterministic chain carries
> **twelve times** more measured value than the model (49 `mock_only` rows
> against 4 `live_only`); and every confident-and-wrong defect reproduced sits
> at confidence 0.90–0.95, where the gate never opens at all.
>
> **Decision: (iv) — keep escalation, re-aim it.** Not (v) drop it: two rescue
> classes are real. Not (i) keep as is. Not (ii) move the gate: the defects
> live above 0.90 and catching them there escalates half of all commands.
>
> The model's unique value is **the road that has no deterministic answer** —
> open-ended questions — and that road is currently unreachable because a
> question scores 0.8, above the 0.7 gate. **So the model follows the question
> desk, not the order chain.** And because the shipped default is
> `LLM_MODE=mock` and BYOK is opt-in, **the desk must be deterministic first
> and the model an enhancement on top of it** — never a prerequisite.

**Re-open condition (verbatim from the recon, adopted):** if, after the row's
changes, a RECORDED-cassette measurement of one played campaign shows the model
rescuing **fewer than 1 command in 200**, drop escalation entirely and ship
mock-only plus the local-model spike (HC-L). The instrument already exists
(`tools/record_parser_cassettes.py` + `parser_eval --replay`).

**Two documented claims this row corrects:**
`docs/audits/LLM_MONETIZATION_RESEARCH_2026_08_14.md` §1 says *"≤1 call per
typed command"* — measured **2** on any unparseable command — and assumes 25%
routing against a measured **3.39%**; its dollar figure is ~4× high and its
architectural conclusion survives comfortably.
The corpus's `live_phrasing_backlog` says its 18 utterances are ones *"the MOCK
action chain cannot parse"* — **8 of the 18 parse confidently today**.

---

## §5 THE PREDICTOR — DESIGNED (CX's third question)

Measured over the 1,416 archived commands, against the keystrokes actually
pressed:

| arm | keystrokes | % saved | hit rate | new data needed |
|---|---:|---:|---:|---|
| type it out (today) | 28,997 | — | — | — |
| up-arrow history, window 10 (**ships today**) | 24,907 | 14.1% | 19.2% | none |
| **prefix-filtered history** | **19,792** | **31.7%** | 47.5% | **none** |
| single inline ghost line | 20,402 | 29.6% | 68.3% | a template generator |
| **ranked top-5 list** | **17,482** | **39.7%** | 68.3% | a template generator |
| every command by chip (a ceiling, not an option) | 1,416 | 95.1% | 100% | — |

**Three findings decide the shape, and two of them overturned the obvious
instinct:**

1. **Do not simply raise `MAX_HISTORY`.** 46% of commands repeat something
   within the last 50 — and measured, a window of 50 saves **5.1%** against
   window 10's 14.1%, because each Up press costs a keystroke and walking 40
   entries costs more than typing 20 characters. **Filter the walk, do not
   lengthen it.**
2. **Inline ghost text loses on its own measurement.** After three characters
   the top proposal is the intended command 29.1% of the time and something
   else **63.4%** of the time. Ghost text that is wrong two times in three is
   noise on the one surface the player is concentrating on. **The shape that
   works is a short ranked list.**
3. **It is client-side, and the fog argument is not close.** Every `/command`
   response already carries `game_state.marshals`, a **fog-filtered**
   `game_state.enemies`, and `game_state.map_data` with a per-region
   `visibility_status`; the map node additionally keeps
   `region_full_data` / `region_visibility` / `region_marshals`. A backend
   `/completions` endpoint would naturally reuse helpers that are omniscient.
   **No new endpoint, and no new fog surface.**

Slot difficulty on the boot board: the addressee is **8 candidates, each unique
within 1–2 characters** and 63.9% of all commands — the cheapest possible win.
Destinations are 126 unscoped but **17** when scoped to provinces adjacent to
one of the player's corps.

⚠ **Row absorption (GR9):** `COMMAND_ROBUSTNESS_SPEC.md` §2's CR-7 row owns
"the fuzzy autocomplete dropdown UI" with *no gate and no schedule*. The user
asked for it by name, so **it moves to CX** and CR-7's row is struck.

---

## §6 THE BUILD

| slice | what | state |
|---|---|---|
| **CX-1** | A question never orders; an address needs no comma | ✅ **LANDED** — §3.1 |
| **CX-2** | Berthier answers: the desk grows, and the shrug routes instead of dumping 12,717 characters | ▶ next |
| **CX-3** | The typed order states its terms — one vocabulary source for the help text, the desk, the predictor and the drift pin | |
| **CX-4** | The predictor — prefix-filtered history, then the ranked list | |
| **CX-5** | The routed backlog, the client's redirect drift, and the corpus's blind spot | |
| **CX-6** | The memo, the re-score and the teaching drift pin | |

---

## §7 DEFERRED, WITH OWNERS (GR9)

*(completed as the row lands — nothing may be left here without an owner row, a
landing slice, a completion definition and a behaviour test.)*
