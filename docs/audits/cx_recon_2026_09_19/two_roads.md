# The Two Roads — a measured per-intent comparison

Recon for row CX. Read-only; nothing under `backend/`, `godot-client/`,
`tests/`, `docs/` or `tools/` was touched. Probes live beside this file in
`probes/` and every number below is either a `file:line` or the output of a
probe that was actually run.

**Date of measurement:** September 19, 2026, at `f7008582` (clean tree).

---

## 0. Two corrections to the brief, before anything else

**(a) `backend/ai/parser.py` does not exist.** The parser is
`backend/commands/parser.py` (131,613 bytes). `backend/ai/` holds
`llm_client.py`, `clause_guards.py`, `validation.py`, `question_desk.py`,
`parser_eval.py`, `providers.py`, `prompt_builder.py`, `schemas.py`,
`strategic_parser.py`, `attack_vocabulary.py`, `recruit_arm.py`,
`generic_targets.py`, `nation_names.py`, `feedback.py`, `enemy_ai.py` — but no
`parser.py`. Anything in the row that navigates to `backend/ai/parser.py` will
miss.

**(b) The corpus is 447 entries, not 447 rows of a list.**
`tests/data/parser_golden_corpus.json` is a dict with keys
`version` / `description` / `live_phrasing_backlog` / `entries`; `entries` is
447 long. 242 of the 447 assert an `expected.action`; the other 205 assert
something else (a refusal, a `not_action`, a `strategic_type: null`). Counting
"447 actions" would overstate action coverage by ~1.8×.

---

## 1. The finding that reframes the row

The brief's premise — *"the click road and the typed road converge at the
parser"* — is **true of the chips and false of the client as a whole.**

The chips do converge: `region_panel.gd:136-140` emits the literal string a
player would type, and `main.gd:6399-6409` sends it through
`api_client.send_command`. Same road.

But `main.gd:1602` calls `_redirect_diplomatic_command(command)` **on the typed
path and only there**, and the function's own comment says so
(`main.gd:1595-1600`: *"every chip pipeline … bypasses by construction"*). When
it returns true, **nothing is sent**: Berthier prints a pointer to the F1
Cabinet and the command dies in the client.

So the two roads are **not two ways to do the same thing**. Each road has a set
of intents the other cannot reach at all:

| | typed road | click road |
|---|---|---|
| **closed to it** | the whole diplomatic family — 114 `DIPLO_FAMILY_KEYWORDS` + 13 `DIPLO_NATION_ANYWHERE_KEYWORDS` + the court-word rule + the cede-to-court rule + the diplomat-address rule (`main.gd:1665-1884`, `_matches_cabinet_family` at `main.gd:1982-2014`) | **movement**, and with it retreat / hold / support / garrison — measured below |
| **sole road** | move, retreat, hold, support, garrison, set war purpose, "where is X" | propose peace, declare war, break treaty, envoy missions, invest, autonomy, cede, request terms, read the ledger |

I ported `_redirect_diplomatic_command` faithfully (all seven arms of
`_matches_cabinet_family`, both word-boundary helpers, the nation-form list
built from `Utils.NATION_COLORS`) in `probes/p2b_client_redirect.py`. It
reproduces **9 of 9** cases that `main.gd`'s own comments assert by name
(`court Bavaria's favour` → intercept, `court martial Ney` → send,
`make Holland a puppet` → intercept, `Talleyrand, assess our situation` → send,
`guarantee our supply lines` → send, `grant Ney the duchy of Swabia` → send,
`declare war on Prussia_` → intercept, …). My first port implemented three arms
and **under-counted** interception (it reported `cede Savoy to Holland` as
sent); the faithful port is what the table below uses.

### 1a. And the click road has no movement verb. At all.

A census of every chip the client can emit — `grep -o 'order:[a-z_]*\|do:[a-z ]*'`
over all 44 `.gd` files — returns exactly this set:

```
do:build ships          do:recruit <arm> in <region>
do:build watchtower in  do:repair <region>
do:buy substitutes for  do:repair buildings in <region>
do:land <m> in <region> order:drill  order:fortify  order:scout  order:unfortify
```

plus two interpolated forms (`build <depot|fort|training ground|market|stables>
in <region>` from `_BUILD_CHIP_DEFS`, `region_panel.gd:516-522`; and
`<marshal>, attack <enemy>` at `region_panel.gd:557`) and the Admiralty's four
backend-supplied commands (`guard home waters`, `blockade the enemy`,
`order the diversion`, `build ships` — `naval.py:2760-2868`).

**Zero chips emit move, march, retreat, hold, support, pursue, charge, bombard,
form_square or recall.** And the map offers no substitute: `map_renderer_base.gd:2041-2055`
maps left-click to `region_clicked.emit()` and nothing else; the only drag in
the file is camera pan on the middle button (`:2020-2022`). There is no
select-a-marshal-then-click-a-destination gesture anywhere in the client.

---

## 2. Method

- **World:** the shipped 1805 boot, `WorldState.from_scenario(europe_1805.json)`
  via `parser_eval.build_world("1805")`. Player France, turn 1, 800 gold,
  8 marshals (Ney/Davout @Rhineland, Soult/Napoleon @Lorraine,
  Lannes/Murat @Franche-Comte, Bernadotte @Franconia, Massena @Milan),
  visible enemies Deroy@Franconia, Mack@Swabia, ArchdukeJohn@Tyrol,
  Brunswick@Berlin.
- **Typed road:** `CommandParser(use_real_llm=False).parse(...)` then
  `CommandExecutor().execute(parse_result, {"world": world})` — the same two
  calls `main.py:3566` makes. `LLM_MODE=mock`, no key, no network.
- **Click road:** read from the `.gd` source. **⚠ UNVERIFIED: I did not run the
  Godot client in this task.** Every click path below is verified to *exist in
  code*; none was verified *on screen*. Click counts assume each scene opens as
  coded.
- **Keystroke proxy:** character count of the canonical phrasing, as the brief
  specifies. It ignores autocomplete and typing speed; it is a proxy, not a
  measurement of effort.
- **Volume weighting:** a census of all 31 `tools/playtest_scripts/*.json`
  (1,416 issued commands) gives the per-turn frequency used in §4. **⚠ These are
  scripted arms, not human play** — they are the best available evidence of what
  a played France issues, not proof of it.

---

## 3. The table

`chars` = canonical typed phrasing length. `clicks` = mouse presses after the
screen is reached; `+key` = one keypress alternative exists.
**Every measured miss below cost 0 AP** — see §3a.

### Military orders

| # | Intent | Typed (chars) | Click path (clicks) | Must know, to type | Must know, to click | On a slight miss |
|---|---|---|---|---|---|---|
| 1 | **Move a marshal** | `Ney, march to Swabia` (20) | **NONE** | verb, marshal, province spelling | — | typed: `Ney, march to Swabland` → *"Region 'Swabland' not found. Did you mean 'Swabia'?"* + `suggestion: Swabia`, 0 AP. `Ny, …` → refused with the full roster, 0 AP. | **TYPED WINS** — it is the only road, and it is 11.7%+2.5% of all commands issued. |
| 2 | **Attack an enemy in an adjacent province** | `Ney, attack Mack` (16) | **NONE** (chip is co-located only) | verb, both names | — | `Ney, attack Makk` → the executor **refuses**: *"Your order names no foe our maps know, Sire — Ney will not charge at a guess."* 0 AP. It does not attack a guess. | **TYPED WINS** — sole road. At boot **7 of 8** French marshals are in this case. |
| 3 | **Attack a co-located enemy** | `Ney, attack Mack` (16) | map→province (1) → `Attack Mack` chip (1) = **2** | verb, both names | where the province is | click cannot miss; typed as row 2 | **CLICK WINS**, narrowly — but at boot it serves **1 of 8** marshals (Bernadotte/Deroy @Franconia), and reached that state on 12 of 12 ambient turns. |
| 4 | **Scout** | `Ney, scout Swabia` (17) | map→province (1) → `Scout` chip (1) = **2** | verb, marshal, province | where the province is | `Ney, scout Swabiaa` → **silently auto-corrects to Swabia and succeeds, charging 1 AP.** A benign silent correction, but silent. | **PARITY** — with a caveat: the chip sends a *bare* `Ney, scout` (no target, `region_panel.gd:134`). Aiming a scout at a named province is typed-only. |
| 5 | **Fortify** | `Ney, fortify` (12) | map→province (1) → `Fortify` chip (1) = **2** | verb, marshal | where he is | `Ney, fortifi` → repaired to `fortify`, executes. 0 AP either way. | **PARITY** |
| 6 | **Unfortify** | `Ney, unfortify` (14) | as row 5 (chip swaps by state) = **2** | verb, marshal | where he is | as row 5 | **PARITY** |
| 7 | **Drill** | `Ney, drill` (10) | map→province (1) → `Drill` chip (1) = **2**; *also* Generals screen: G + `Drill` chip = 1 key + 1 click | verb, marshal | where he is | `Ney, train the men` also parses to `drill` | **PARITY** |
| 8 | **Retreat** | `Ney, retreat` (12) | **NONE** | verb, marshal | — | `Ney, fall back` also parses to `retreat` | **TYPED WINS** — sole road |
| 9 | **Hold position** | `Ney, hold` (9) | **NONE** | verb, marshal | — | — | **TYPED WINS** — sole road; 1.9% of scripted commands |
| 10 | **Support another marshal** | `Soult, support Ney` (18) | **NONE** | verb, both marshals | — | — | **TYPED WINS** — sole road. Note the muster preview *tells* the player to type it: *"order 'Soult, support Ney' and he will march"* (measured, row 2's output). |
| 11 | **Garrison a province** | `Ney, garrison Rhineland` (23) | **NONE** | verb, marshal, province | — | `Ney, garrison Rhinland` → auto-corrected to Rhineland, then refused for the real reason (3-garrison cap), 0 AP | **TYPED WINS** — sole road |

### Economy

| # | Intent | Typed (chars) | Click path (clicks) | Must know, to type | Must know, to click | On a slight miss | Verdict |
|---|---|---|---|---|---|---|---|
| 12 | **Recruit troops** | `recruit infantry in Paris` (25) | map→province (1) → `Infantry` chip (1) = **2** | verb, arm, province | where the province is | typed `…in Parris` **silently drops the province** (`target: None`) and answers about *marshals*: *"No marshal is available to receive reinforcements, Sire."* The near-miss is never named. 0 AP. | **CLICK WINS** — and not on clicks: the chip carries the live price and the ordinance headroom (`region_panel.gd:279-300`, e.g. *"3,193 under — 654g per 3,000 foot here"*). The typed road makes you look that up elsewhere. |
| 13 | **Buy substitutes** | `buy substitutes for Ney` (23) | map→province (1) → `Buy Substitutes` chip (1) = **2** | verb + marshal | where he stands | typed `…for Ny` → honest refusal + full roster, 0 AP | **CLICK WINS** — chip states price, batch size, alarm premium and room under the establishment; disabled-with-reason when shut (`region_panel.gd:320-347`). |
| 14 | **Build a structure** | `build depot in Paris` (20) | map→province (1) → `Depot 300g` chip (1) = **2** | verb, building word, province | where the province is | typed `build depot in Rhinland` → **drops the province and says only *"Specify a region. Example: 'build supply depot at Lyon'"*** — it does not name the misspelling, unlike the move arm which does. 0 AP. | **CLICK WINS** — chip states cost *and* delivered yield per building (`_build_terms_text`, `region_panel.gd:574-599`). |
| 15 | **Build a watchtower** | `build watchtower in Paris` (25) | as row 14 = **2** | verb, province | where the province is | as row 14 | **CLICK WINS** |
| 16 | **Repair works / war damage** | `repair Paris` (12) | map→province (1) → `Repair works 150g` / `Repair war damage 150g` (1) = **2** | verb, province | where the province is | province typo drops the target | **CLICK WINS** — two distinct chips for two distinct orders, each with its effect stated; the typed road offers one verb and no cue that war damage is repairable at all. |
| 17 | **Commission a marshal** | `commission Suchet` (17) | G (+key) → `Commission a Marshal…` (1) → `Commission Suchet — 5,500g` (1) = **2 +key** | verb **and the candidate's name** | nothing — the bench is listed | typed `commission Suchett` → *"No candidate named 'Suchett' awaits a commission. Candidates: Mortier, Grouchy, Suchet, Oudinot, Augereau, Marmont, Senarmont."* 0 AP — an honest refusal that also *teaches the bench*. | **CLICK WINS** — the bench names are not guessable; the click road enumerates them and prices each. |
| 18 | **Grant an estate / rente** | `grant Ney a rente` (17) | G (+key) → `[Reward…]` (1) → option (1) = **2 +key** | verb, marshal, instrument word | which marshal | typed `grant Ny a rente` → honest refusal + roster, 0 AP | **CLICK WINS** — the dialog states each instrument's terms side by side (`reward_dialog.gd:121-155`); the typed verb commits blind. |
| 19 | **Revoke a rente** | `revoke Ney's rente` (18) | as row 18 = **2 +key** | verb, marshal | which marshal | as row 18 | **CLICK WINS** — the dialog names the saving and whether the shortfall reopens. |

### Meta / reading

| # | Intent | Typed (chars) | Click path | Verdict & why |
|---|---|---|---|---|
| 20 | **End turn** | `end turn` (8) | End Turn button (1), or `E` | **PARITY** — both first-class (`main.gd:634`, `:953`). |
| 21 | **Check status** | `status` (6) | no single button; the same facts are split across Dispatch (R), Ledger (T), Generals (G) | **PARITY** — typed is one word; the click road is several screens, but each is richer. |
| 22 | **Read the strategic ledger** | `show me the ledger` → **REFUSED** (`Unknown action: unknown`) | Ledger button or `T` (1) | **CLICK WINS — sole road.** Measured: no typed phrasing opens a screen. `economy report` (14) reaches the *economy* action, which is not the ledger. |
| 23 | **Cancel a standing order** | `Ney, halt` (9) | T (+key) → `6` (Orders tab) → `[Cancel]` (1) = **1–3** | **TYPED WINS** — 9 characters against a screen, a tab and a link. ⚠ But see §5.1: `Ney, cancel` — the obvious phrasing — **is refused**. |
| 24 | **Ask where a marshal is** | `where is Davout` (15) | **NONE** (the Generals card shows location, but is not a question) | **TYPED WINS** — routed to `status` / the question desk; wh-words are exempted from the diplomatic redirect (`main.gd:1912-1919`). |

### Diplomacy — the typed road is closed on all of these

Every row here was **measured BLOCKED** by `probes/p2b_client_redirect.py`: the
sentence parses perfectly at the backend, and the client never sends it.

| # | Intent | Typed (chars) | Client verdict | Click path (clicks) | Verdict |
|---|---|---|---|---|---|
| 25 | **Propose peace** | `propose peace with Austria` (26) | **BLOCKED** — `FAMILY:'propose peace'` | F1 (+key) → nation (1) → action (1) = **2 +key** | **CLICK WINS — sole road.** Wizard states DP/gold cost + likelihood colour (`diplomacy_wizard.gd:566-607`). |
| 26 | **Declare war** | `declare war on Prussia` (22) | **BLOCKED** — `FAMILY:'declare war on'` | F1 → nation → action = **2 +key** | **CLICK WINS — sole road** |
| 27 | **Break a treaty** | `break treaty with Prussia` (25) | **BLOCKED** — `FAMILY:'break treaty'` | F1 → nation → action = **2 +key** | **CLICK WINS — sole road**; `break the alliance with Prussia` blocked too. |
| 28 | **Send an envoy / mission** | `gather intel on Austria` (23) | **BLOCKED** — `FAMILY:'gather intel on'` | F1 → nation → action = **2 +key** | **CLICK WINS — sole road.** ⚠ But see §5.2: the *longer* phrasing escapes the block. |
| 29 | **Invest in a vassal** | `invest in Holland` (17) | **BLOCKED** — `NATION_GATED:'invest in '` | F1 → nation → action = **2 +key** | **CLICK WINS — sole road.** ⚠ §5.3: the possessive form escapes. |
| 30 | **Grant autonomy** | `increase autonomy Holland` (25) | **BLOCKED** — `FAMILY:'autonomy'` | F1 → nation → action = **2 +key** | **CLICK WINS — sole road** |
| 31 | **Cede a province to a vassal** | `cede Savoy to Holland` (21) | **BLOCKED** — `CEDE_TO_COURT` | F1 → nation → action (1) → **province picker** (1) = **3 +key** | **CLICK WINS — sole road**, and the picker prices each province (*"income 250g, loyalty +12, they remit 75%"*, `diplomacy_wizard.gd:664`). |
| 32 | **Request terms** | `request terms` (13) | **BLOCKED** — `war-room 'request terms'` | war HUD card (1) → `Request Terms` (1) = **2** | **CLICK WINS — sole road** (`war_detail_popup.gd:601-611`). |

### Naval

| # | Intent | Typed (chars) | Click path (clicks) | Verdict |
|---|---|---|---|---|
| 33 | **Set a fleet posture** | `blockade the enemy` (18) | T (+key) → `7` (Admiralty) → chip (1) = **1–3** | **CLICK WINS** — the chip carries an honest forecast the typed road never prints: *"closes Austria, Russia — not Britain (31.5 against her, 125.0 needed)"* (`naval.py:2786-2805`). |
| 34 | **Build ships** | `build ships` (11) | Admiralty chip **or** region-panel dockyard chip = **2–3** | **PARITY** — 11 characters is cheap; the chip adds the price and names the yard. ⚠ `build shipps` falls into the *building* branch and answers *"Specify a region"* (§5.4). |
| 35 | **Naval expedition** | `land Ney in Ulster` (18) | map→coastal province (1) → `Land Ney here` (1) = **2** | **CLICK WINS** — the chip quotes the odds the resolver will roll (*"12,000 men from Brittany · 64 in 100 slip past"*) and, when blocked, states the executor's own reason instead of vanishing (`region_panel.gd:452-478`). |
| 36 | **The Grand Diversion** | `order the diversion` (19) | Admiralty chip = **1–3** | **CLICK WINS** — chip states the 45%, the once-per-war cost, whether a camp is staged, and the window forecast. |

### Reactive

| # | Intent | Typed | Click path | Verdict |
|---|---|---|---|---|
| 37 | **Answer a marshal petition** | a closed literal grammar keyed to the petition's subject, fails closed (IQ-7 review, `dialogue_routing.petition_plain_answer`) | the petition modal's buttons (1) | **CLICK WINS** — the modal is the designed road; the typed grammar deliberately re-prompts anything it does not recognise, because the answer is priced and irreversible. |
| 38 | **Set war purpose** | `set war purpose` (15) | **NONE proactively** — the `war_purpose_selection` popup is raised by the game at a declaration (`proposal_confirm_popup.gd:129`) | **TYPED WINS** — it is one of three verbs `main.gd:1635` calls "no UI home" and deliberately exempts from the redirect so the typed route survives. |

### 3a. One clean result across every miss arm

**Not one of the 13 measured near-miss arms charged an action point.**
(`probes/p4_miss_cost.py`, `AP_spent=0` on every MISS row.) The typed road's
downside is a wasted sentence, never a wasted action. That materially weakens
the usual argument against typing.

---

## 4. Aggregate — and the honest headline

**38 intents: TYPED WINS 9 · CLICK WINS 22 · PARITY 7.**

On a count of intents the click road wins comfortably, nearly 2:1. That is the
wrong number to steer by, and here is why.

Weighting by the 1,416-command census of `tools/playtest_scripts/*.json`:

| verb head | share | road |
|---|---|---|
| attack | 14.3% | typed-only for 7 of 8 marshals at boot |
| status | 14.1% | parity |
| move + march | **14.2%** | **typed-only** |
| fortify + unfortify | 15.3% | parity (chips exist) |
| drill | 6.6% | parity (chip exists) |
| assess | 3.7% | typed |
| recruit | 3.2% | click wins |
| improve (mission) | 3.0% | click-only |
| build | 2.8% | click wins |
| hold | 1.9% | **typed-only** |
| propose | 1.8% | click-only |
| invest | 1.3% | click-only |
| declare | 1.2% | click-only |

**Of the 22 CLICK WINS, exactly two are per-turn routine — recruit (3.2%) and
build (2.8%), together 6.0% of issued commands.** The other twenty are rare,
one-off, or reactive: a peace is signed a handful of times a campaign, a marshal
is commissioned once or twice, a province is ceded almost never, a petition is
answered when the game raises it.

**The typed-only set — move, attack-at-range, hold, retreat, support, garrison —
is roughly 30% of everything a played France issues.**

> **Headline: the click road wins 22 of 38 intents and about 6% of the volume.
> A player can complete an ordinary turn using only the typed road. A player
> cannot complete a single ordinary turn using only the click road — the first
> `move` order ends the attempt.**

The corollary matters as much for the row: **the click road is not a faster way
to issue routine orders, it is a richer way to issue rare ones.** Every CLICK
WINS verdict above was won on *information*, not on clicks — the levy price, the
building's yield, the expedition's odds, the blockade's forecast, the bench's
names, the province's tribute cut. The chips are priced; the typed verbs are
blind. That is the actual asymmetry, and it points at cheaper remedies than
building a movement UI: the typed road could quote the same terms back.

And one architectural note that constrains any "just add chips" instinct:
because a chip sends a typed command, **a chip inherits every executor refusal.**
Measured: `recruit infantry in Paris` fails at boot (*"No marshal is available
to receive reinforcements at Paris"*) — and the region panel's Paris Recruit
chip sends exactly that string, so it fails identically. **A chip removes naming
risk, never gate risk.**

---

## 5. Defects found while measuring

**5.1 — `Ney, cancel` is refused, and the refusal lists `cancel` as valid.**
`probes/p4_miss_cost.py`: parse fails with `Unknown action: unknown`, and the
`suggestion` string enumerates `… restrain, cancel, build, repair …`. The
synonym `Ney, halt` (9 chars) works and cancels the order. A player who reads
the refusal is told the word they just used is valid. P2 in my judgement; it is
the game's own printed vocabulary failing to be typable — the IQ-10 class.

**5.2 — the same mission intent takes opposite roads depending on phrasing.**
`gather intel on Austria` is **BLOCKED** to the Cabinet
(`FAMILY:'gather intel on'`). `gather intelligence on Austria` is **SENT** to the
backend, where it parses to `diplomatic_mission / GATHER_INTEL` and would
execute. IQ-10 made the long form typable in the backend parser and the client's
mirror list was not updated — so the short form is redirected and the long form
is not. The client's own comment (`main.gd:1664`) calls that list *"mirrored
from the parser's keyword blocks"*; the mirror has drifted. P2.

**5.3 — the possessive escapes the vassal gate.** `invest in Holland` is BLOCKED;
`invest in Holland's defenses` is **SENT**, and the backend parses it to
`invest_vassal / Holland` (probe 1). Cause: `_names_a_nation`
(`main.gd:2071-2083`) prefix-matches `form`, `form + " "` or `form + ","`, so an
apostrophe falls through — while the sibling helper `_contains_word`
(`main.gd:2034-2051`) treats a possessive as a word boundary *by design*, and
its comment says so. Two helpers in one file disagree about what a possessive is.
P3, but it is a hole in a rule the codebase calls "the Cabinet is the only door".

**5.4 — two province-typo arms answer the wrong question.** `build depot in
Rhinland` and `recruit infantry in Rhinland` both **silently drop the province**
and then answer about something else (*"Specify a region"* / *"No marshal is
available to receive reinforcements"*), while the movement arm on the same board
names the miss and suggests the fix (*"Region 'Swabland' not found. Did you mean
'Swabia'?"*). `build shipps` is worse still: it falls into the *building* branch
and asks for a region. The good behaviour already exists one verb over. P3.

---

## 6. What is UNVERIFIED

- **No Godot client was run.** Every click path is verified to exist in `.gd`
  source and none was verified on screen. Click counts assume each scene opens
  and renders as coded.
- **The "mouse hunt" cost is a judgement, not a measurement.** I note it because
  `map_label_layer.gd:24` sets `PROVINCE_LABEL_MIN_ZOOM = 1.1` — below that zoom
  only nation labels draw, so the click road's "you don't need the spelling"
  advantage requires zooming in first. I did not measure how often a player is
  below that zoom.
- **The 1,416-command census is of scripted playtest arms**, not human play. It
  is the best available proxy for issue frequency and should not be quoted as
  human behaviour.
- **Character count is a proxy for keystrokes**, as the brief specifies. It
  ignores typing speed, autocomplete and the up-arrow history recall that
  `main.gd:929-934` provides (which materially cheapens repeated typed orders —
  `Ney, attack Mack` on turns 1–4 of `commanded_full40.json` is one keypress
  after the first).
- **Row 3's boot figure (1 of 8 co-located) is a boot measurement**, extended
  over 12 ambient turns on the `historical` seed. I did not measure co-location
  frequency on a *played* board, which is the case that matters; a player who
  attacks and advances creates co-location deliberately.
- I did **not** verify that every wizard action in `_build_command`
  (`diplomacy_wizard.gd:739-806`) is reachable at boot — the availability gate is
  backend-supplied per court and I did not enumerate it.

---

## 7. Rider — how often does the typed road actually reach the LLM?

Not in the brief, but it bears directly on the row's framing (and on the
request that opened it), and the data fell out of the same harness.
`probes/p6_escalation.py`, gate `LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7`
(`llm_client.py:63`, read at `:902`):

| set | n | answered by the fast parser (no LLM call) | would escalate |
|---|---|---|---|
| my probe cases (canonical + near-miss) | 64 | **95.3%** | 4.7% |
| golden corpus, 1805-applicable, non-`live_only` | 388 | **88.1%** | 11.9% |

**⚠ Both escalation figures are an UPPER BOUND.** The probe calls
`LLMClient._parse_with_mock` directly, which bypasses
`repair_leading_verb_typo` — applied one layer up at `parser.py:1608`. That is
why `Ney, fortifi` shows here at 0.50 while the end-to-end probe (§3) has it
executing as `fortify`. Production escalates less than these numbers say; I did
not measure by how much.

Two observations that matter more than the rate:

**(a) The confidence distribution is bimodal, so the 0.7 gate is nearly a free
parameter.** Corpus histogram: `{0.5: 42, 0.55: 4, 0.75: 1, 0.8: 52, 0.9: 123,
0.95: 158, 1.0: 8}`. **Five of 388 utterances sit between 0.55 and 0.75.**
Moving the gate anywhere in 0.6–0.79 reclassifies at most those five. The fast
parser is not expressing graded uncertainty — it is saying *"I know this"* (0.8+)
or *"I have no idea"* (0.5). So tuning the threshold is not a lever; the only
real decision is what to do with the 0.5 bucket.

**(b) A large share of that 0.5 bucket is stuff the LLM should not be asked.**
Of the 46 escalating corpus entries, the sample includes `xyzzy foobar`,
`dance with the moon`, `the warden watches` (nonsense, correctly unknown) and
`Ney, never attack Mack`, `Ney, don't attack` — which `llm_client.py:911-920`
deliberately makes **terminal**, precisely because forced tool-use would make the
model name an action for a sentence whose verb the player forbade. The
genuinely LLM-shaped residue is small and recognisable: `Soult, deal with the
Austrians`, `Ney, cover the retreat`, `Ney, fix bayonets`,
`break through enemy lines`, `check the status of Davout` — idiom and
delegation, not typos.

That is an argument about *where* prediction would pay. Neither a text predictor
nor the LLM helps the 0.8+ mass (already right) or the nonsense (correctly
refused). Both would pay on the same narrow band: **idiomatic delegation, and
the names** — and the names are exactly what §4 shows the click road already
solves by enumeration. I have not costed either option; that is the row's call,
not this recon's.

---

## 8. Provenance of these measurements — the tree was not pristine

`git status` at the end of this recon is **not clean**: a sibling agent in this
same workflow landed `backend/ai/clause_guards.py` (+71/−2, *"CX slice 1 — A
QUESTION NEVER ORDERS"*, adding `A_QUESTION_NEVER_ORDERS` and
`_SUBJECT_WH_WORDS = {who, whom, whose, why}`). **I did not write it and did not
revert it.** Recording it because it bears on whether my numbers reproduce:

- **§3's typed-road and miss-cost measurements are unaffected by construction.**
  `p1_out.json` (09:18:50) and `p4_out.txt` (09:22:44) both predate the edit
  (`clause_guards.py` mtime 09:28:23). They measured the pristine tree.
- **§7's figures reproduce identically on both trees.** Re-run after the edit:
  64 cases 95.3%/4.7%, 388 corpus 88.1%/11.9%, byte-identical histograms.
  Expected — only two corpus utterances lead with a word in the new set
  (`who holds Swabia?`, `who holds Brunswick?`) and both already carry a `?`.
- I caught the file mid-edit in a state that raised
  `NameError: name 'Iterable' is not defined` at `:673`. **That was transient**
  — `from typing import Iterable, …` is present at `:52` now and
  `import backend.main` succeeds. **It is not a defect and should not be filed
  as one;** I note it only so a reader who sees it in a log knows it was a
  half-second of someone else's edit, not a landed breakage.

Anyone re-running these probes should expect §3 to reproduce only on a tree
where `clause_guards.py` matches `f7008582`, and §7 to reproduce on either.
