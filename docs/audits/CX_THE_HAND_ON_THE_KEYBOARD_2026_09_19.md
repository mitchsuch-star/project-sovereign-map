# ROW CX — "THE HAND ON THE KEYBOARD"
## The gate answered, the model ruled, the predictor measured

**September 19, 2026.** Master at `f7008582` when the row opened; landed as
`b4a27a15` (CX-1), `5fc3d5c8` (CX-2), `2c3535b5` (CX-3).
**Owning spec:** `docs/COMMAND_EXPERIENCE_SPEC.md` (the landing records).
**Rules:** `docs/SYSTEMS_REFERENCE.md` §50 · **parse pipeline:**
`COMMAND_ROBUSTNESS_SPEC.md` §10 · **defects:** `BUG_FIXES.md` §Row CX ·
**design rows:** `DESIGN_REFINEMENT.md` §Row CX.
**Recon of record:** the twelve censuses and their eleven refutations are
committed under `docs/audits/cx_recon_2026_09_19/` — every figure below cites
one by name.
**Playtest archives:** `docs/audits/playtest_digests/cx-before-*`,
`cx-after-*` and `cx-typed-road` (the IQ-8 table rule: a figure with no
archive is uncitable).
**Frames:** `docs/audits/CX3_*_2026_09_19.png`, ten, both Interface Scales.
**Parser:** mock throughout. No key, no network, no live API call — the IQ-9
floor holds for every figure in this memo.

The user asked three questions and this memo answers all three in writing:

1. **Is typing fun enough to justify not clicking?** *(allowed to be no)*
2. **Can typing be made efficient — a predictor, or something better?**
3. **Is routing to the LLM worth it, and how is it made better?**

---

## 0. METHOD, AND THE CAVEAT THAT GOVERNS EVERY FREQUENCY NUMBER

Twelve read-only censuses plus a refuter per census (24 agents, 0 errors), then
the build. Every claim below is a `file:symbol`, a probe that was run, or a
frame that was captured. The refuters overturned eight of the censuses' own
headline claims and those corrections are carried here rather than quietly
dropped — they are marked ⚠.

⛔ **No human has ever played a measured campaign in this repository.** All
8,422 typed commands in the archive are **driver** commands from authored
scripts, and 20 of the 23 commanded archives run `commanded_full40.json`,
whose own `_note_d6` key says it exists to *"spend all four military actions
every turn"* — so 68 of its 83 military-AP successes are fortify / unfortify /
drill against **9 marches and 6 attacks in forty turns.** Frequency here is
the best available proxy for what a played France issues. It is not evidence
of human behaviour, and this row does not pretend otherwise.

---

## 1. THE THREE SETS

The brief asked for the click set, the parser set and the executor set, and
for every gap to be a finding. The first finding corrected the framing.

### 1a. The chips ARE typed commands

`region_panel.gd:136-140` emits the literal string a player would type;
`main.gd:6399-6409` sends it through `api_client.send_command`. Of the
client's non-typed affordances, **~70 distinct strings** take that road; 16
POST and 15 GET endpoints take a structured one; the rest are local UI.

So for most intents the two roads **converge at the fast parser**, and a chip
inherits every executor refusal. Measured: `recruit infantry in Paris` fails
at boot (*"No marshal is available to receive reinforcements at Paris"*) and
the Paris Recruit chip sends exactly that string and fails identically.

> **A chip removes naming risk. It never removes gate risk.**

### 1b. But each road is CLOSED on a set the other owns

| | typed road | click road |
|---|---|---|
| **closed to it** | the whole diplomatic family — `main.gd::_redirect_diplomatic_command` intercepts 114 keyword forms **on the typed path and only there**, and when it fires **nothing is sent** | **movement**, and with it retreat / hold / support / garrison |
| **sole road** | move, march, retreat, hold, support, garrison, set war purpose, cancel, and **every question** | propose peace, declare war, break a treaty, send an envoy, invest, autonomy, cede, request terms, read any ledger |

⚠ **Corrected by a refuter:** the census claimed *"the client has no movement
verb anywhere"*. It does — `main.gd:5563-5575` maps `MOVE_TO → "march to"`,
`PURSUE`, `SUPPORT` and `HOLD` to literal strings, and
`clarification.py:311` builds `"<Marshal>, move to <name>"` for up to six
adjacent provinces, one button each. The census's grep looked for two **chip
prefixes** and was blind to both by construction.

**The corrected statement is narrower and stronger:** *the click road has no
movement verb it can OFFER ON ITS OWN.* Every movement button in the client is
raised by an **ambiguous typed order**, so a player who types nothing never
sees one. And there is no marshal-selection gesture at all — `grep
"selected_marshal\|marshal_selected"` over every `.gd` returns **zero hits**;
left-click emits `region_clicked` and the only drag is a camera pan.

### 1c. And the corpus does not know about the client's own gate

`_redirect_diplomatic_command` eats **111 of the 447 golden-corpus utterances
(24.8%)** before the backend sees them. Those rows certify a backend that is
correct and a road the player cannot take. **That is not a defect** — it is
user ruling **G1**, recorded — but the instrument should say so. Routed as
**CX-X2**.

---

## 2. THE PER-INTENT COMPARISON — 38 INTENTS, BOTH ROADS

Every click path was read out of the `.gd`; a path that could not be verified
was marked UNVERIFIED rather than invented. **Not one of the 13 measured
near-miss arms charged an action point** — the typed road's downside is a
wasted sentence, never a wasted action, which materially weakens the usual
argument against typing.

### The 38 intents — the verdict sheet

The full rows — the near-miss column, the prerequisite knowledge and
the reasoning behind each verdict — are in the recon's `two_roads.md`.
Every click path here was read out of the `.gd`; a path that could
not be verified was marked UNVERIFIED rather than invented.

| # | intent | typed (chars) | click path | verdict |
|---|---|---|---|---|
| 1 | **Move a marshal** | `Ney, march to Swabia` (20) | **NONE** | **TYPED WINS** |
| 2 | **Attack an enemy in an adjacent province** | `Ney, attack Mack` (16) | **NONE** (chip is co-located only) | **TYPED WINS** |
| 3 | **Attack a co-located enemy** | `Ney, attack Mack` (16) | map→province (1) → `Attack Mack` chip (1) = **2** | **CLICK WINS** |
| 4 | **Scout** | `Ney, scout Swabia` (17) | map→province (1) → `Scout` chip (1) = **2** | **PARITY** |
| 5 | **Fortify** | `Ney, fortify` (12) | map→province (1) → `Fortify` chip (1) = **2** | **PARITY** |
| 6 | **Unfortify** | `Ney, unfortify` (14) | as row 5 (chip swaps by state) = **2** | **PARITY** |
| 7 | **Drill** | `Ney, drill` (10) | map→province (1) → `Drill` chip (1) = **2**; *also* Generals screen: G + `Drill` chip = 1 key + 1 click | **PARITY** |
| 8 | **Retreat** | `Ney, retreat` (12) | **NONE** | **TYPED WINS** |
| 9 | **Hold position** | `Ney, hold` (9) | **NONE** | **TYPED WINS** |
| 10 | **Support another marshal** | `Soult, support Ney` (18) | **NONE** | **TYPED WINS** |
| 11 | **Garrison a province** | `Ney, garrison Rhineland` (23) | **NONE** | **TYPED WINS** |
| 12 | **Recruit troops** | `recruit infantry in Paris` (25) | map→province (1) → `Infantry` chip (1) = **2** | **CLICK WINS** |
| 13 | **Buy substitutes** | `buy substitutes for Ney` (23) | map→province (1) → `Buy Substitutes` chip (1) = **2** | **CLICK WINS** |
| 14 | **Build a structure** | `build depot in Paris` (20) | map→province (1) → `Depot 300g` chip (1) = **2** | **CLICK WINS** |
| 15 | **Build a watchtower** | `build watchtower in Paris` (25) | as row 14 = **2** | **CLICK WINS** |
| 16 | **Repair works / war damage** | `repair Paris` (12) | map→province (1) → `Repair works 150g` / `Repair war damage 150g` (1) = **2** | **CLICK WINS** |
| 17 | **Commission a marshal** | `commission Suchet` (17) | G (+key) → `Commission a Marshal…` (1) → `Commission Suchet — 5,500g` (1) = **2 +key** | **CLICK WINS** |
| 18 | **Grant an estate / rente** | `grant Ney a rente` (17) | G (+key) → `[Reward…]` (1) → option (1) = **2 +key** | **CLICK WINS** |
| 19 | **Revoke a rente** | `revoke Ney's rente` (18) | as row 18 = **2 +key** | **CLICK WINS** |
| 20 | **End turn** | `end turn` (8) | End Turn button (1), or `E` | **PARITY** |
| 21 | **Check status** | `status` (6) | no single button; the same facts are split across Dispatch (R), Ledger (T), Generals (G) | **PARITY** |
| 22 | **Read the strategic ledger** | `show me the ledger` → **REFUSED** (`Unknown action: unknown`) | Ledger button or `T` (1) | **CLICK WINS — sole road.** |
| 23 | **Cancel a standing order** | `Ney, halt` (9) | T (+key) → `6` (Orders tab) → `[Cancel]` (1) = **1–3** | **TYPED WINS** |
| 24 | **Ask where a marshal is** | `where is Davout` (15) | **NONE** (the Generals card shows location, but is not a question) | **TYPED WINS** |
| 25 | **Propose peace** | `propose peace with Austria` (26) | **BLOCKED** — `FAMILY:'propose peace'` | **CLICK WINS — sole road.** |
| 26 | **Declare war** | `declare war on Prussia` (22) | **BLOCKED** — `FAMILY:'declare war on'` | **CLICK WINS — sole road** |
| 27 | **Break a treaty** | `break treaty with Prussia` (25) | **BLOCKED** — `FAMILY:'break treaty'` | **CLICK WINS — sole road** |
| 28 | **Send an envoy / mission** | `gather intel on Austria` (23) | **BLOCKED** — `FAMILY:'gather intel on'` | **CLICK WINS — sole road.** |
| 29 | **Invest in a vassal** | `invest in Holland` (17) | **BLOCKED** — `NATION_GATED:'invest in '` | **CLICK WINS — sole road.** |
| 30 | **Grant autonomy** | `increase autonomy Holland` (25) | **BLOCKED** — `FAMILY:'autonomy'` | **CLICK WINS — sole road** |
| 31 | **Cede a province to a vassal** | `cede Savoy to Holland` (21) | **BLOCKED** — `CEDE_TO_COURT` | **CLICK WINS — sole road** |
| 32 | **Request terms** | `request terms` (13) | **BLOCKED** — `war-room 'request terms'` | **CLICK WINS — sole road** |
| 33 | **Set a fleet posture** | `blockade the enemy` (18) | T (+key) → `7` (Admiralty) → chip (1) = **1–3** | **CLICK WINS** |
| 34 | **Build ships** | `build ships` (11) | Admiralty chip **or** region-panel dockyard chip = **2–3** | **PARITY** |
| 35 | **Naval expedition** | `land Ney in Ulster` (18) | map→coastal province (1) → `Land Ney here` (1) = **2** | **CLICK WINS** |
| 36 | **The Grand Diversion** | `order the diversion` (19) | Admiralty chip = **1–3** | **CLICK WINS** |
| 37 | **Answer a marshal petition** | a closed literal grammar keyed to the petition's subject, fails closed (IQ-7 review, `dialogue_routing.petition_plain_answer`) | the petition modal's buttons (1) | **CLICK WINS** |
| 38 | **Set war purpose** | `set war purpose` (15) | **NONE proactively** — the `war_purpose_selection` popup is raised by the game at a declaration (`proposal_confirm_popup.gd:129`) | **TYPED WINS** |

### The headline count

> **TYPED WINS 9 · CLICK WINS 22 · PARITY 7.**

On a count of intents the click road wins nearly 2:1. **That is the wrong
number to steer by.** Weighted by the 1,416-command script census:

| verb head | share | road |
|---|---|---|
| fortify + unfortify | 15.3% | parity (chips exist) |
| attack | 14.3% | **typed-only for 7 of 8 marshals at boot** |
| move + march | 14.2% | **typed-only to initiate** |
| status | 14.1% | parity |
| drill | 6.6% | parity |
| assess | 3.7% | typed |
| recruit | 3.2% | click wins |
| build | 2.8% | click wins |
| hold | 1.9% | **typed-only** |
| propose / invest / declare / mission | ~7% | **click-only** |

**Of the 22 CLICK WINS, exactly two are per-turn routine — recruit (3.2%) and
build (2.8%), 6.0% of issued commands together.** The other twenty are rare,
one-off or reactive: a peace is signed a handful of times a campaign, a
marshal is commissioned once or twice, a province is ceded almost never.

### The asymmetry that actually matters

Every one of the 22 CLICK WINS was won on **information, not on clicks**: the
levy's live price, the building's delivered yield, the expedition's odds, the
blockade's forecast, the commission bench's names, the ceded province's
tribute cut. Two clicks against twenty characters is not why the chip wins.

> **The chips are priced. The typed verbs are blind.**

---

## 3. ⚖ THE RULING ON THE GATE

> ### The click road wins the catalogue. The typed road wins the turn.
>
> A player can complete an ordinary turn using only the typed road. **A player
> cannot complete a single ordinary turn using only the click road — the first
> `move` order ends the attempt.**
>
> So the honest answer to *"is typing fun enough to justify not clicking?"* is
> not yes and not no. It is: **the two roads are complements, not substitutes,
> and the game has been treating them as substitutes.** Typing owns the army.
> Clicking owns the cabinet. Neither is going away.

### What typing is FOR — and what this row built

**(a) The army.** Movement, concentration, standing orders, the whole
manoeuvre vocabulary. There is no click path to initiate any of it, it is
~30% of everything a played France issues, and building a movement UI is a
far larger project than making the sentence good.

**(b) The question.** The one thing no chip can ever do. It was the typed
road's sole claim and it was measured almost entirely broken — **two of the
user's twelve questions answered, ten walled** behind a 12,717-character
manual that contains the words `status`, `where is`, `who holds` and `how many
men` **zero times**. CX-2 answers **41 of 41**.

**(c) The sentence a button cannot hold.** A chip is one order with fixed
parameters. A sentence carries a marshal, a verb, a target, a condition and a
tone in one keystroke-efficient line.

### Where typing was strictly worse — and what was done

The brief's rule: *where typing is strictly worse, either make the typed road
better in this row or state that the chip IS the road.*

| case | measured | disposition |
|---|---|---|
| The typed verb is blind where the chip is priced | every CLICK WINS verdict | **FIXED** — CX-2's desk answers `what can I build here` / `how much is a battalion` / `what's my income` from the same pricers the chips read, and the counsel quotes prices |
| A question executed an order | `why not attack Mack` fought a real battle | **FIXED** — CX-1 |
| A one-keystroke slip fought a battle | `Nay attack Mack` sent Soult in | **FIXED** — CX-1 |
| The game taught sentences it could not read | `halt Ney`, `Davout, hold Ulm` | **FIXED** + a census so it cannot recur — CX-3 |
| The recovery text taught a war on a neutral | `declare war on Prussia` at a France at peace with Prussia | **FIXED** — CX-2 |
| Typing is slower than clicking for a repeated order | 14.8% of keystrokes recoverable by history | **IMPROVED** — CX-3, filtered history + completer |
| **The diplomatic family** | 114 forms intercepted client-side; the wizard prices every option and the typed verb cannot | **THE CHIP IS THE ROAD, and it is stated.** Ruling G1 retired those verbs as a player surface. CX-2 stops the game *teaching* them: the shrug and the counsel now name the Cabinet as a door instead of printing a sentence that cannot be sent |
| **Reading a ledger** | no typed phrasing opens a screen | **THE CHIP IS THE ROAD.** The router now names the screen and its key (*"the Strategic Ledger's Economy tab (press T, then 3)"*) rather than pretending otherwise |

### Re-open condition

**If a played human session shows a player completing turns without typing a
movement order — i.e. a proactive movement affordance has been added to the
click road — this ruling is re-opened**, because its load-bearing fact is that
the click road cannot start a march. Nothing else in it depends on a number
that can drift.

---

## 4. ⚖ THE RULING ON THE MODEL

| measurement | value |
|---|---|
| escalation rate, golden corpus (447 entries × both worlds) | **45 / 692 = 6.5%** — through the REAL `_should_fallback_to_llm`. ⚠ A hand-written re-implementation of the same predicate, run first, gave 50 / 692 = 7.2%; the real-predicate figure is the one cited, and the discrepancy is recorded rather than averaged |
| escalation rate, the 1,416 committed playtest commands | **48 / 1,416 = 3.39%** |
| escalation rate, the two 40-turn **commanded** arms | **0 / 160 and 0 / 173 = 0.00%** |
| escalation rate, the client's **chip** road | **0 / 22 = 0.00%** |
| escalating corpus rows whose `expected` is `success: false` | **25 / 29 = 86%** |
| escalating corpus rows where the corpus wants a NEW ORDER | **0 / 29** |
| `live_only` corpus rows — the model's whole measured value | **4 of 447** |
| `mock_only` rows — the deterministic chain's | **49 of 447** |
| input per parse call on the 1805 boot | **19,619 chars ≈ 4,904 tokens** |
| live calls per request, measured ceiling | **2** (the monetization memo claims ≤1) |
| gate needed to catch the measured confident-and-wrong defects | **> 0.90 → 50.7% of commands escalate** |

> ### As shipped, escalation is close to worthless — and not because the model is bad.
>
> **The gate routes the wrong sentences.** It fires on 3.4% of real play and
> **0.00% of a campaign actually being played**; 86% of what it catches is a
> sentence the corpus says must be REFUSED; the deterministic chain carries
> **twelve times** more measured value than the model (49 `mock_only` rows
> against 4 `live_only`); and every confident-and-wrong defect that reproduces
> sits at confidence 0.90–0.95, where the gate never opens at all.
>
> **Decision: (iv) — KEEP escalation, and RE-AIM it.** Not (v) drop it: two
> rescue classes are real. Not (i) keep as is. Not (ii) move the gate — the
> defects live above 0.90 and catching them there escalates half of all
> commands.
>
> The model's unique value is **the road that has no deterministic answer** —
> open-ended questions — and that road was unreachable because a question
> scores 0.8, above the 0.7 gate. **So the model follows the question desk,
> not the order chain.** And because the shipped default is `LLM_MODE=mock`
> with BYOK opt-in, **the desk is deterministic first and the model an
> enhancement on top of it** — never a prerequisite. CX-2 built the
> deterministic half; the escalation seam is untouched and is now pointed at
> the only thing it is better at.

### Re-open condition (adopted verbatim from the recon)

**If, after these changes, a RECORDED-cassette measurement of one played
campaign shows the model rescuing fewer than 1 command in 200, drop escalation
entirely and ship mock-only plus the local-model spike (HC-L).** The
instrument exists: `tools/record_parser_cassettes.py` + `parser_eval
--replay`.

### Two documented claims this row corrects

1. `docs/audits/LLM_MONETIZATION_RESEARCH_2026_08_14.md` §1 says *"≤1 call per
   typed command"* — **measured 2** on any unparseable command — and assumes
   25% routing against a measured **3.39%**. Its dollar figure is ~4× high;
   its architectural conclusion survives comfortably.
2. The corpus's `live_phrasing_backlog` says its 18 utterances are ones *"the
   MOCK action chain cannot parse"* — **8 of the 18 parse confidently today.**

---

## 5. THE PREDICTOR — MEASURED BEFORE IT WAS BUILT

Baseline: **28,997 keystrokes** to type all 1,416 commands out.

⚠ Two models are in play and the memo keeps them apart rather than averaging
them. The **census** charged one keystroke per Up press with no cap; the
**refuter** capped the walk at the command's own length (the floor any player
who can stop pressing achieves) and re-measured against `_add_to_history`'s
real semantics. Where they differ, the refuter's figure is used and the
census's is shown beside it.

| arm | % saved | hit rate | new data |
|---|---:|---:|---|
| up-arrow history, window 10 (**ships today**) | **14.8%** *(census 14.1%)* | 19.2% | none |
| prefix-filtered history, window 10 | **17.5%** | 47.5% | none |
| **prefix-filtered, window 50 — what shipped** | **21.4%**, oracle 29.9% | — | none |
| single inline ghost line | 29.6% | 68.3% | a template generator |
| ranked top-5 list | 39.7% | 68.3% | a template generator |
| every command by chip (a ceiling, not an option) | 95.1% | 100% | — |

⚠ **The first census claimed prefix-filtering was worth 31.7% for thirty
lines. A refuter measured it at the SHIPPED constant and it is 2.7 points**
(14.8 → 17.5) — the other fourteen come from a longer window, which the same
census told the builder not to touch. **Both were right about the cell they
measured and wrong about the conclusion:** lengthening an *unfiltered* walk
costs keystrokes, and filtering makes lengthening free. CX-3 changes **both**,
which is the cell neither had run.

⚠ **And ghost text lost on its own numbers** — wrong 63.4% of the time at
three characters. The row built a ranked list instead, which was not the
instinct it started with.

**What shipped:** a grammar-aware completer (the slot the prefix says you are
in, the roster the verb chooses), Tab to accept, drawn **inside the terminal's
own VBox** so it inherits `content_scale_factor` rather than fighting the
CanvasLayer ladder — IQ-10's two P3s were both fixed-size surfaces that did
not fit Interface Scale 2.0, and this one cannot be a third. Proven at both
scales: `docs/audits/CX3_*_2026_09_19.png`.

---

## 6. THE DEFECT TABLE

### Fixed in this row

| id | sev | defect | where |
|---|---|---|---|
| **CX-1a** | **P1** | `why not attack Mack` **fought a real battle** — AP 4→3, six corps bled incl. the Emperor's Guard. `why not retreat` marched the **whole army**. `what about attack Mack`, `how about retreat`, `is it time to build a depot in Paris` (300 gold), `can/may/does/is Ney attacking Mack`, `is Swabia defended`, `retreat?` — one 684-case grid run under BOTH arms went **121 executing → 9**, all nine of them intended controls — 112 defects to zero | CX-1 |
| **CX-1b** | **P1** | `Nay attack Mack` — one keystroke from `Nay, attack Mack` — sent **Soult, never named**, into a real battle. So did `Grouchy`, `Berthier`, `Wellington`, `Blucher` and `Zorglub`; `Wellington retreat` marched the entire army. The guard keyed on a **comma** | CX-1 |
| **CX-1c** | P2 | `who holds Swabia` — the desk's own advertised kind — raised *"Which marshal shall hold Swabia, Sire?"*, one answer from an order | CX-1 |
| **CX-2a** | P2 | **Ten of the user's twelve questions returned a 12,717-character manual** containing none of the answers. Now 41 of 41 answered | CX-2 |
| **CX-2b** | P2 | **Berthier's shrug taught an act of war against a neutral** — `declare war on Prussia` at a France at PEACE with Prussia, fifty-two lines below the guard that exists to stop it — and all three of its diplomatic examples name a road the client redirects | CX-2 |
| **CX-2c** | P3 | A `reach` question was answered with the marshal's position: *"Marshal Ney stands at Rhineland with 24,000 men"* — true, and not the answer | CX-2 |
| **CX-3a** | P3 | The help documents `"halt Ney"` and the cancel keyword list held every form of the word **except** that one | CX-3 |
| **CX-3b** | P3 | The help teaches `"Davout, hold Ulm"`; it **parses** and the executor refuses *"Region 'Ulm' not found"* | CX-3 |
| **CX-5** | **P2** | **`Lannes, cut down the retreat` marched the player's OWN marshal away** — free, 0 AP, the retreat's −45% effectiveness penalty, at confidence 0.90, ABOVE the escalation gate so no key could ever have corrected it. Six more with it (`cut off`, `press`, `block`, `exploit`, `punish`, `ride down the retreating Austrians`). The July-18 guard that exists for exactly this closed it with an **allowlist of four verbs** | **FIXED** — the allowlist is INVERTED: "retreat" after a determiner is a NOUN unless the verb means *carry out* one. 10 of 10 now refuse free; 8 of 8 genuine retreats still retreat |

### Routed, with owners (GR9)

| id | sev | defect | owner / landing slice |
|---|---|---|---|
| **CX3-X1** | P3 | The campaign narrates in Ulm, Austerlitz and Jena and none is typable | **CR-6 proper**, beside IQ9-X2. Done when `march to Ulm` reaches Swabia or refuses by naming it |
| **CX-X1** | P2 | **The wh-word Cabinet backdoor.** `_is_advisory_question` exempts any sentence opening `what/how/where/who/whom/why` from the diplomatic redirect, so `why not declare war on Prussia` is SENT and stages a war-purpose dialogue. The const's own comment says *"A wh-word cannot begin an order, so only those exempt"* — which this row measured false. Its sibling, `DIPLO_NO_HOME_KEYWORDS`, bails on a match **anywhere**, so appending a no-home verb opens the door: `propose peace with Austria, then make amends with Russia` is sent | **CR-6 proper** (it is a client-gate rule, and ruling R7 keeps the ADVISORY arms deliberately open — the fix must distinguish an advisory arm from an action arm, not close the door) |
| **CX-X2** | P3 | 111 of 447 corpus rows are client-blocked and the corpus does not say so; and **14 of 46 chip templates have ZERO corpus coverage** — if the click road is a typed road, that is its only regression net | **CR-6 proper**. Done when each chip template has a row and the blocked rows carry a `client_blocked` marker |
| **CX-X3** | P2 | `vassalize Austria` / `Britain` / `Russia` on turn 1 — free, no AP, no confirm, no objection — subjugates three great powers and hands France six marshals. ⚠ **NARROWED: unreachable in the shipped client**, which intercepts `vassalize` (`main.gd:1778`). Reachable over the API, by a driver, or after any change to that list | **the vassal/Cabinet owner** (`VASSAL_DEEPENING_SPEC`). Done when the backend gates it independently of the client |
| **CX-X4** | P3 | The region panel renders raw camelCase (`Attack ArchdukeCharles`) — it is the one click surface that never calls `humanize_entity_name`; and its Cavalry/Artillery chips are cosmetic where a single-arm corps holds the province | the next UI slice |
| **IQ9-X1** | P3 | the CR-2 retry cannot rescue the word-scan family | **CR-6 proper** — unchanged. Done when the retried live parse is ADOPTED where it resolves the marshal the fast pass mis-bound |
| **IQ9-X2** | P3 | the fuzzy suggestion can name a FOGGED enemy | **CR-6 proper** — unchanged, and CX3-X1 now sits beside it as the region half of the same vocabulary question |
| **IQ9-X3** | P4 | a live-road failure stamps `parse_mode: "mock"` | **CR-6 proper** — unchanged |
| **IQ10-X1** | P3 | the top bar sheds buttons at Interface Scale 2.0 | **the next UI slice** — unchanged, and CX-X4 joins it there |
| **IQ10-X2** | P4 | the petition popup's disabled-Grant reason sits below the fold | **the next UI slice** — unchanged |
| **IQ7-X7** | — | **PARTLY CLOSED here**: `is that a yes` is a question, not a deferral, and CX-1's copular arm closes it. The six real deferrals stay CR-6's | CR-6 proper |

---

## 6b. THE EVIDENCE, AND WHAT IT CANNOT SHOW

**Before/after, three seeds, same script, archived** — and the digests are
**byte-identical except the provenance stamp.** That is not a claim about
safety; it is a fact about the instrument, and it was measured rather than
assumed: of the **166 strings** in `commanded_full40.json`, **0 are
question-shaped and 0 omit the addressee comma**. The committed harness
structurally cannot reach anything this row changed.

So the row added the arm that can — `tools/playtest_scripts/typed_road.json`,
which types the way a person does: it asks, it muses, it misspells a name, it
drops a comma, it names a place the map does not have. Read on the archive
(`docs/audits/playtest_digests/cx-typed-road`):

| turn | what was typed | what happened |
|---|---|---|
| 1–2 | ten questions | ten answers with real figures — *"Swabia is held by Bavaria"*, *"654 gold for 10,000 infantry"*, *"Ney can reach Vienna … Rhineland → Swabia → Franconia → Bohemia → Vienna"* — and **4 of 4 action points unused, both turns** |
| 3 | the musings: `what happens if I attack Mack`, `why not attack Mack`, `what about attack Mack`, `is it time to attack Mack` | all four print the **real muster**, *"Were you to give the order, Sire…"*, and **4 of 4 action points unused** |
| 4 | `Nay attack Mack`, `Zorglub attack Mack`, `Wellington retreat` | three refusals, free, each naming the miss: *"There is no 'Nay' in the order of battle, Sire. Whom did you intend?"* — and `Davoust, fortify` is still repaired to **Davout** |
| 5 | `halt Ney`, `Ney, march to Swabland` | the first works; the second answers *"Did you mean 'Swabia'?"*. ⚠ `Davout, hold Ulm` still refuses — **CX3-X1, routed** |
| 8 | `flurble the wibble` | the shrug offers *"'Ney, march to Lorraine'"* — an order from the counsel — and names the Cabinet. Not a war on Prussia |

**The three rules the brief asked to be proved, each with a pin:** a question
never executes (one 684-case grid, both arms: 121 → 9, all nine intended controls;
`TestTheQuestionsThatFought` asserts AP, gold, turn, every marshal's position
and strength, and the absence of a battle report — not merely `success is
False`, which a refusal AFTER a mutation satisfies); a question the game can
answer gets a SENTENCE (`TestTheTwelveQuestions`, each asserting a figure or a
name the board actually holds, and `len(message) < 2000`); and one it cannot
answer names the surface that holds it (`TestTheRouter`).

## 7. RE-SCORE

**Command & parsing 7.5 → 8.0. ⚠ FOR USER CONFIRMATION.**

Raised on named evidence: a question no longer executes an order (one
684-case grid measured under both arms: 121 → 9, and all nine are the
intended controls); a one-keystroke slip no longer fights a
battle; the game's own printed sentences are now a census rather than a hope;
and the typed road answers 41 of 41 driven questions where it answered 2 of
12. Held below 8.5 because **the diplomatic family is still closed to typing
by ruling** — which is correct, and is still a limit — and because the
conditional-order system (`Ney, retreat if outnumbered`) remains refused by
design and owned by CR-6/CR-7.

**UI/UX — NOT re-scored.** IQ-10's 7.5 stands. This row added one client
surface and proved it at both scales; that is not a pass over the other
seventy-nine.

⛔ **What this row does NOT claim.** No human played a campaign for it. The
completer's keystroke figures are simulations over driver archives, and the
one thing a harness cannot measure is whether the list *feels* helpful or
noisy at speed. **A live session is owed**, and the honest test is narrow:
type a turn's orders with the completer on, and say whether Tab saved you
anything.

---

## 8. THE ONE THING THE USER ASKED FOR MOST

> *"Do not make the typed road prettier while leaving it worse."*

Nothing in this row is decoration. The question desk answers from the pricers
and resolvers the mechanics themselves read, so a quoted figure is the applied
figure — `what happens if I attack Mack` prints the **exact string the order
would print**, for nothing. The completer offers only lines a census has run
through the real parser. The help text was corrected where it taught a
sentence the game refuses. And the two P1s this row closed were both cases of
the typed road doing something **irreversible** that the click road cannot do
at all.

If clicking wins for most of what players do — and by a count of intents it
does, 22 to 9 — then the answer to *what should typing be FOR* is:
**the army, and the question.** That is what was built.

---

## 9. THE REVIEW ROUND — what it took back

**Held September 19, 2026, at `727cf88a`.** 63 agents: lenses to find,
refuters to kill. Every refuter defaulted to REFUTED, wrote its own probes,
and proved attribution against a tree extracted with `git archive b4a27a15^`
rather than a lever flip — which matters, because CX-2, CX-3 and CX-5 all
touched the mock parser and a lever restores one branch of one function.

**It confirmed two defects this row had itself shipped, and the fix for them
exposed a third.** Landing record: `COMMAND_EXPERIENCE_SPEC.md` §8. Rows:
`BUG_FIXES.md` §Row CX. Rules: `SYSTEMS_REFERENCE.md` §50.11–§50.13.

### 9.1 The row argued with itself

CX-1 landed two rules about the same sentence in one commit. One half was
titled **AN ADDRESS NEEDS NO COMMA** and existed *because a player does not
type the comma*. The other half read a line as addressed **only** through a
regex that requires one. So:

    Ney, attack Mack?   →  Ney fights. 1 AP, 291 gold, four corps move.
    Ney attack Mack?    →  "Berthier sets down his pen. I cannot answer
                            that from the dispatches, Sire."

Of 128 comma-free addressed orders, **86 acted before and are inert now**; 58
changed real state, 28 raised an objection that now raises nothing. Nothing
is spent and nothing is corrupted — which is what keeps it off P1 — and it is
wide, silent, and on the road §2 of this memo calls *the road that wins the
turn*.

⚠ And the shrug it fell to **points somewhere else**: `Ney fortify?` was
answered with the Economy tab, `Marshal Ney attack Mack?` with the Generals
screen. The counsel prints its top two picks whatever was typed, so the
player is told confidently that an order was a question and then sent to an
unrelated surface.

### 9.2 The blocklist failed open — 256 of 261 cells

The other half asked *is this leading run NOT a name?* against a hand-written
list of grammar words. English has more adverbs than that list will ever
hold, so everything unlisted was claimed as somebody's name and the order
refused. Filed at 23 shapes across 2 doors; **measured at 9 marshal-less doors
× 29 natural leading runs, 256 newly refused** — `quickly attack Mack`,
`cavalry attack Mack`, `ok retreat`, `Marshal attack Mack`, and the sharpest
of them, `someone attack Mack`, which is the plain English for the very thing
`auto_assign_attack` does.

⚠ **The finding's own prescribed fix closes 0 of 23.** The refuter
implemented it verbatim and measured it: every one of those heads is a
CONTENT word, so a head-token test claims them exactly as the whole-run test
does — and it adds one refusal (`quickly and at once attack Mack`). A builder
following the report would have closed two findings, believed he closed a
third, and shipped a new one. **This is the single most useful thing the
review produced**, and it is why the fix is a different shape.

### 9.3 What §8 actually built, and what the suite then found

One predicate, asked the other way round, failing CLOSED, shared by both
rules. Then the full suite — not the review — found the third defect: putting
the singular title in the new class list made **`the Iron Marshal, attack
Mack` send Soult**, FA-22's own flagship case, caught by FA-22's own pin.

That forced the ruling that makes the whole thing coherent, and it was in the
punctuation all along: **a comma is the player's own mark of address.** With
one, the game answers for the run the player marked (FA-22, unchanged); with
none, it claims a run only if it looks like a name (CX-7). Collectives and
interjections stand down either way.

Measured, both lever arms, end to end on a fresh 1805 board per cell:
**221 of 261 refused → 9**, and the 9 belong to a different producer
(CX7-X1).

### 9.4 The instrument was built on the geometry of its own finding

§6b of this memo was honest that `commanded_full40.json` is blind to row CX
and said the new arm, `typed_road.json`, *"types the way a person does… it
drops a comma."* The review read it: **it drops the comma only in front of a
NAME** — never an adverb, an interjection, an arm noun or an indefinite
pronoun. The arm built to catch this class could not see the 256-cell
regression shipped beside it.

That is this project's recorded lesson arriving on schedule — *the reviewers'
first move is to change the one parameter the builder held constant* — and it
is now four rows in a row. Turns 9–12 of the script type the runs a person
actually puts in front of an order. Archived before/after on the same seed:

| | unbound refusals | wrong |
|---|---|---|
| before | 15 | 12 |
| after | 5 | 0 |

⚠ **`cmd_refused` barely moves (23 → 25), and that is the honest number.**
The twelve sentences are not refused less; they are refused **differently** —
`quickly attack Mack` now returns *"Massena is fortified at Munich and cannot
attack. Order 'unfortify' first to make the army mobile"*, a reason with a
next step, instead of an insult. The two new refusals are `Zorglub`'s, and
they are correct.

### 9.5 A name the game prints must be a name the game reads

Filed by the review as a false CLAIM in a docstring; measured here as a live
defect. `can Archduke Charles attack Mack` **fought** while `can Mack attack
Ney` asked, because the roster arm read one token after the lead **and** the
roster held the scenario key (`ArchdukeCharles`) where the game prints
`Archduke Charles`. The commanders the game shows the player were exactly the
ones the guard could not match — the NPC-cluster through-line one layer out.
Both halves fixed; the second through R7's own chokepoint.

### 9.6 What the sweep found that no reviewer did

Three rounds, **six INERT results, every one real**: two mutations that could
not bite (one sited below the check it meant to delete; one written with `or`,
where `frozenset() or X` is X), three pins about the wrong thing, and **one
piece of genuinely dead code** — a longest-first sort I had written and
commented, which cannot matter because the test is `startswith` and the answer
is a boolean. Deleted, not pinned. Final: **27 mutations, 27 killed, 0
INERT.**

### 9.7 The gate ruling is unchanged, and the review strengthens it

Nothing in §2 moves. But the round sharpens the one thing the user asked for
most. Both shipped defects made the typed road **worse than it had been the
day before** — one refused ordinary orders as unknown officers, the other
silently dropped hesitant ones — and both shipped behind green pins, a green
23,000-test suite, and a memo that measured the right things in the wrong
places. The row's ruling was that typing wins the turn; **a row that makes
typing win the turn owes its regressions a harder look than its features.**
