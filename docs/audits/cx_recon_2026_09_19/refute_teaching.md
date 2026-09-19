# Refutation pass — the teaching census

**Target:** `…/scratchpad/cx_recon/teaching.md`
**Run:** September 19, 2026 · HEAD `f7008582` · `LLM_MODE=mock` throughout, zero network calls.
**Method:** I did not use the other agent's pristine tree or any of its probes. I built **my own** tree
at `probes/mypristine/` (repo copy with `backend/ai/llm_client.py` and `backend/ai/clause_guards.py`
replaced by `git show HEAD:`, md5 `0f70a21a…` / `b127169e…` — verified against `git show` in the same
command), and a second **patched** tree at `probes/patched/` carrying the report's prescribed fix, so
every behavioural claim below is a two-arm flip experiment. Probes `r01`–`r11` in
`…/scratchpad/cx_recon/probes/`.

**Headline of this pass:**

> The census's two findings are real and its line numbers are unusually accurate for this repo. But its
> **prescribed fix is a regression** — measured, five behaviour flips, and the golden corpus is green
> about all five — its **largest clean claim (170/170) is measured on a dialogue shape the router does
> not branch the same way on**, and it never opened the one producer that prints command-shaped strings
> *at the moment the player is lost*: `llm_client._berthier_mock_response`, whose own hardcoded example
> tells a France at peace with Prussia to **declare war on Prussia** (HEAD `llm_client.py:1236`) —
> fifty-two lines below the guard in the same function (`_hostile_first`, HEAD `:1184`, FA-80c) that
> exists to stop exactly that.

---

## Verdicts

| id | verdict | one line |
|---|---|---|
| TC-1 | **SURVIVES** (P2 → **P3**); its **fix REFUTED** | defect reproduces; `"halt "` flips five behaviours and also silently fixes TC-2 |
| TC-2 | **SURVIVES**, mis-framed | same root as TC-1, closed by the same one-line change — not a separate decision |
| TC-3 | **SURVIVES** as filed | 2 of 5 mission row labels fail; design comment is where they say |
| TC-CLEAN-1 | **NARROWED, materially** | 170/170 measured on a bare option list; 10 of 12 lines route differently on the real shape |
| TC-CLEAN-2 | **SURVIVES**, count wrong | 28 wizard commands, not 31; all pass |
| TC-CLEAN-3 | **SURVIVES** | 20/20 re-derived over four nations |
| TC-CLEAN-4 | **SURVIVES** (line cites verified; not re-driven end to end) | |
| TC-PIN | **SURVIVES in shape, NARROWED in four specifics** | 2-of-5 producers, 4-vs-6 naval chips, tutorial body prose unreachable by its own mechanism, dialogue shape wrong |

---

## REFUTE:TC-1 — SURVIVES / magnitude NARROWED both ways / **the prescribed fix is REFUTED**

### What re-derives

Everything textual checks out, which is rare here:

* `backend/commands/meta_executor.py:705` really is `  cancel     - "cancel Ney" / "halt Ney" (1 AP)`, and it is the
  **only** `halt` in that file (`grep -n halt` → one hit). A repo-wide scan finds no other printed
  teaching of `halt <Marshal>` in `.gd` or `deploy/README_TESTER.txt`.
* At HEAD the keyword list is at `llm_client.py:1803`, the leading forms at `:1806`, the bare
  exact-match at `:1809` — all three cites exact.
* **Real `/command` road, my pristine tree, shipped 1805 boot** (probe `r01`):

```
cancel Davout   pre=(MOVE_TO,Franconia)  success=True   post=()
halt Davout     pre=(MOVE_TO,Franconia)  success=False  post=(MOVE_TO,Franconia)
   '"Sire, Marshal Davout awaits your command, but I cannot parse this order.
     Might you mean 'Davout, scout' or 'Davout, defend'?"'
```

* **The help census re-derived independently** (probe `r02`, rendering `MetaExecutor._execute_help`
  on a live 1805 world, not scraping source): 12,717 chars, **50** double-quoted phrases, **7** of them
  marshal epithets → **43 command-shaped**, and **`halt Ney` is the only failure**. Confirmed.
  (Incidental: the epithet `"Drillmaster of Boulogne"` parses as `drill` at 0.8 — an epithet that is
  accidentally a command. Harmless, but it is why the 7-entry allowlist TC-PIN asks for must be an
  allowlist and not a "does it parse" filter.)

### Where it over-states

**P2 is too high.** The failure is a **0-AP honest refusal**; the standing order survives; the primary
spelling works; the string is printed in exactly one place. Set against the census's own INFO-1 —
`Improve Relations Austria`, also a printed-looking imperative that fails — the only thing separating
them is that the help's cancel row prints `halt Ney` as a command and the missions block does not.
That is worth a row; it is not worth P2. **P3.**

### Where it under-states, and the census said so only half-way

The report notes "same asymmetry hits `stop Ney` and `abort Ney`". It missed the other axis. Full
verb × position grid on the shipped board (probe `r02`, real `llm_game_state`):

| | `V Ney` | `Ney, V` | `Ney V` | bare `V` |
|---|---|---|---|---|
| `cancel` | **cancel** 0.9 | ✗ unknown 0.5 | ✗ unknown 0.5 | cancel 0.8 |
| `halt` | ✗ unknown 0.5 | cancel 0.9 | cancel 0.9 | cancel 0.8 |
| `stop` | ✗ | ✗ | ✗ | cancel 0.8 |
| `abort` | ✗ | ✗ | ✗ | cancel 0.8 |
| `belay` | cancel 0.9 | cancel 0.9 | cancel 0.9 | cancel 0.8 |

Six broken cells, not one. The one that matters is **`Ney, cancel`** — the help's left column prints
`cancel`, and every other row of that help teaches `<Marshal>, <verb>` (`Davout, defend`,
`Soult, drill`, `Ney, fortify`, `Ney, retreat`). A player who has read fourteen rows of that idiom and
types `Davout, cancel` gets the shrug. The census counted bare `cancel` as one of its "PASS ×32" column
labels and never composed it with the address form the same page teaches everywhere else.
And `belay` — a word the game prints nowhere — works in all four positions.

### The prescribed fix ships a regression — measured

The report proposes adding `"halt "` to `llm_client.py:1803`, and states: *"`stop ` and `abort `
deliberately excluded … `halt` has no such collision."* The exclusion reasoning for `stop`/`abort` is
**correct** (`es7sp-stop-davouts-pension` and `wo11-stop-the-war-with-britain-bare` are real corpus
rows). The claim about `halt` is **false**.

The arm is `any(kw in command_lower for kw in [...])` — a substring test over the whole line — and
`halt` is a member of `llm_client.STAND_STILL_ALTERNATION` (`:186`), the ONE stand-still vocabulary
`backend/commands/parser.py:88-89` builds its sequential-split gate from. The cancel arm sits *above*
the wait/hold arms, so `"halt "` claims every halt-initial sentence before they are reached.

Two-arm flip, `probes/mypristine` (HEAD) vs `probes/patched` (report's fix), probe `r04`:

| utterance | HEAD | with the fix |
|---|---|---|
| `halt here, then attack Mack` | **attack** 0.9 | cancel 0.9 |
| `halt Ney, then attack Mack` | **attack** 0.95 | cancel 0.95 |
| `halt and wait for Davout` | **wait** 0.9 | cancel 0.9 |
| `halt and hold the bridge` | **hold** 0.8 | cancel 0.8 |
| `halt recruitment` | **recruit** 0.8 | cancel 0.8 |
| `halt Ney` | unknown 0.5 | cancel 0.9 ✔ |
| `halt Soult's march` | move 0.9 | **cancel 0.9** ✔ |
| `halt the war with Britain` | diplomatic_proposal 0.95 | unchanged ✔ |

Five flips. A cancel and a HOLD are not interchangeable — cancel destroys a standing order at 1 AP,
HOLD creates a 2-AP strategic order — and `halt … then attack` is precisely the compound shape FA
slice 7's `STAND_STILL_ALTERNATION` work exists to govern.

**The corpus cannot see any of it.** `tests/data/parser_golden_corpus.json` has **447 entries** (686
eval checks across both worlds). Nine mention the cancel family; **none contains the word `halt`**.
`parser_eval` returns **686/686 on both arms** (probe: run under `probes/mypristine` and
`probes/patched`). This is the project's own recurring lesson one layer over: a green sweep proves the
pin binds, not that it is about the right thing.

**A bounded fix exists** and the report did not consider it: anchor on the roster rather than on a
substring — a `^halt\s+<known marshal>$`-shaped arm, or an extension of the `:1809` exact-match arm —
which fixes all six broken grid cells without touching the stand-still family. I did not build it;
flagging that the "one list entry, smallest fix" framing is what makes the row look cheap.

### The live-mode caveat is resolvable, and I resolved half of it

The report records TC-1's live behaviour as **UNVERIFIED**. The *routing decision* is measurable
without a key. With a real `llm_game_state` (`main.get_llm_game_state()`) and a stubbed anthropic
provider (probe `r02`):

```
halt Ney       action=unknown conf=0.5 refusal=None   ESCALATES=True
stop Ney       ...                                     ESCALATES=True
Ney, cancel    ...                                     ESCALATES=True
cancel Ney     action=cancel  conf=0.9                 ESCALATES=False
halt Soult's march action=move conf=0.9                ESCALATES=False
```

So under `LLM_MODE=anthropic` the whole broken half of the grid **does** reach the model
(`_should_fallback_to_llm`, `llm_client.py:874` at HEAD: not mock, key present, conf < 0.7, `refusal` None,
action not in `NON_ORDER_ACTIONS`). Whether the model then answers `cancel` is still **UNVERIFIED** (no
key; conftest network guard). ⚠ Note the trap the report's first cut of this fell into and mine did
too: with `game_state=None` the gate returns False for *everything*, so a bare-parser probe "proves"
nothing escalates. The defect is mock-fatal — and mock is the shipped tester default — but it is not
unconditionally fatal, which is another reason P2 is too high.

---

## REFUTE:TC-2 — SURVIVES, but the row is mis-framed as independent

Reproduces exactly (probe `r01`, real road, fresh game): `Soult` holding `(MOVE_TO, Munich)`,
`halt Soult's march` → `"You wish me to march to Swabia, Sire?"`, `yes` → cost 1, Soult marches, the
Munich order is gone. Confidence **0.9** with a real `llm_game_state` (0.8 without — worth knowing,
since the report's `p19` figure is only reproducible on the game_state road), above the 0.7 gate, so
`_should_fallback_to_llm` is False. All correct.

**What is wrong is the sequencing.** The report says *"Decide TC-2 and INFO-1 as copy/parser rows
separately — neither blocks the pin."* Measured above: the TC-1 fix moves `halt Soult's march` from
`move` to `cancel`. TC-2 is not a neighbour of TC-1, it is the **same root seen from the other side**
— the cancel arm's failure to claim a halt-initial line — and any fix for one decides the other.
Landing TC-1 as prescribed and then "deciding TC-2 separately" would be deciding a question already
answered, in the direction a five-flip regression answered it.

---

## REFUTE:TC-3 — SURVIVES exactly as filed

Re-derived (probe `r09`) against `backend/display_names.MISSION_ROW_DISPLAY` — note the report does not
say where that table lives; it is `display_names.py`, not `diplomatic_dialogue.py`:

```
Improve Relations Austria   -> unknown 0.5      FAIL
Gather Intel Austria        -> unknown 0.5      FAIL
Court Austria               -> COURT_NATION 0.95
Undermine Alliance Austria  -> UNDERMINE_ALLIANCE 0.95
Reassure Ally Austria       -> REASSURE_ALLY 0.95
```

2 of 5, prepositions are the whole difference, and the design comment really is at
`meta_executor.py:150-159` (`MISSION_HELP_BLOCK`, "teaching them would teach a dead route"). INFO is
the right tier.

---

## REFUTE:TC-CLEAN-1 — **NARROWED, materially.** The 170/170 is measured on the wrong road for at least one shipped family

This is the census's largest claim and the one I can most nearly kill.

`match_dialogue_answer` (`backend/commands/dialogue_routing.py:1074`) branches on the **dialogue**,
not only on its options. At `:1162-1164`:

```python
if (A_PETITION_IS_ANSWERED_PLAINLY and _is_client_petition_dialogue(dialogue)):
    return petition_plain_answer(dialogue, typed)
```

and the comment says the arms below are *"unreachable for such a dialogue by construction"*. There are
**three** such dialogue-level branches: `_is_client_petition_dialogue`, `_dialogue_is_petition_family`
(HEAD `:633`, which also covers `ally_settlement_petition`) and `_dialogue_is_ultimatum_family` (HEAD `:642`).

The census harvested `{label, action}` dict literals and, in its own words, ran
`match_dialogue_answer(set, label.lower())`. A bare option list carries no `context.proposal_type`, so
every one of those branches is **False** and the labels resolve through the ordinary arms. Probe `r11`
compares the census's shape against the shape `ai_diplomacy._build_client_petition_dialogue` actually
ships (IQ-7, landed three days before this census):

```
is_client_petition(census shape): False      is_client_petition(real shape): True

typed                          census shape           REAL shape
grant the petition             'grant the petition'   'accept_ai_proposal'   DIFFERENT
grant                          None                   'accept_ai_proposal'   DIFFERENT
grant it                       None                   'accept_ai_proposal'   DIFFERENT
yes                            'yes'                  'accept_ai_proposal'   DIFFERENT
grant the petition later       'grant the petition'   None                   DIFFERENT
...
disagreements: 10/12
```

The fifth row is the indictment: **`grant the petition later` PASSES the census's harness and is
REFUSED by the game** — deliberately, by IQ-7's closed fail-closed grammar, whose whole landing record
is "an irreversible priced answer is a closed allowlist". A census that reports PASS on a line the
product refuses is not measuring the product.

The census's own correction #4 shows how this got past it: the harvest first asserted `got == action`,
got 126 failures, and was weakened to "the line is claimed by this dialogue". That weaker assertion is
exactly what a wrong-shape harness needs to go green.

Two further holes, measured by AST over `backend/` (probe `r06`):

* **30 non-literal (f-string) labels**, 11% of the family, concentrated in the most irreversible
  dialogues: 11 in `settlement_staging.py`, 5 ultimatum demand builders, and
  `diplomacy.py:8601/8607` `f'Honor alliance with {target}'` / `f'Side with {aggressor}'`. To the
  census's credit, I typed eleven of these verbatim through `match_dialogue_answer` and **all eleven
  resolve**, including sibling-in-one-set cases (`Offer 500 gold` vs `Offer 1500 gold`;
  `Demand 5000 infantry` vs `Demand 5000 cavalry`) — so the stated gap is narrower than admitted, on
  the arms I could test. But they were tested on the same wrong shape.
* **143 dicts carry a `label` and no `action` key at all** and were silently skipped by the harvest,
  including families that carry a full typed command: `clarification.py:153/249`
  (`('command','label','target','value')`, 13 dicts — the very file TC-2's clarification comes from),
  `naval.py:2861` (6), `naval_executor.py:445` (3), `jealousy.py:2343/2346` (17 marshal-petition arms).

**Verdict: the family may well be clean; the census has not shown it.** "170/170, clean by
construction" should read "170/170 of the literal-label subset, against a synthetic dialogue shape that
disables three of the router's own branches".

---

## REFUTE:TC-CLEAN-2 — SURVIVES on substance, count wrong

`region_panel.gd:130-143` really does emit the chip's own string verbatim
(`region_command.emit(meta_str.substr("do:".length()))`) and `_BUILD_CHIP_DEFS` really is at `:516`.
The claim that chips send rather than describe is confirmed.

The number is not. `diplomacy_wizard.gd::_build_command` has **29 `return` statements, 28 of them
commands** (one returns `""`), not 31. I substituted a fixture nation/aim/amount and ran all 28 —
**28/28 pass** (probe `r09`), with the classifications the wizard expects
(`propose_common_peace`, `grant_region_to_vassal`, `change_autonomy`, five mission types, …).

The census's own INFO stands and is worth keeping: `propose white peace with Austria` parses as a
generic `peace` (`proposal_type=peace`), identical to `propose peace with Austria`. The wizard's
comment covers it, but it is the one wizard echo whose typed meaning differs from its clicked meaning.

---

## REFUTE:TC-CLEAN-3 — SURVIVES

Re-derived over **four** nations rather than two (probe `r09`): all five `MISSION_DESCRIPTIONS`
sentences × {Austria, Papal States, Kingdom of Italy, Ottoman Empire} → **20/20**, each resolving to
its own `mission_type` and to the right canonical tag (`PapalStates`, `KingdomOfItaly`, `Ottoman`).

The claim that this generalises the IQ-10 pin from 1 of 5 to 5 of 5 is correct: `tests/test_iq10_client_pass.py:282-305`
pins `GATHER_INTEL` only, and the other existing pin
(`tests/test_playtest_rescore_2026_09_12.py:715` `test_improve_relations_carries_its_preposition`) is a
grammar assertion (`assertNotIn("relations Austria")`) that executes no parse.

---

## REFUTE:TC-CLEAN-4 — SURVIVES (line cites verified; not re-driven)

I verified every cite rather than the behaviour: `main.py:960` `_INTERRUPT_KEYWORDS = (`,
`:970` `"push on", "push through"),`, `:985` `def _interrupt_choice_from_text(...)`,
`:2841` `if _pending_answer_token in ("trust", "insist", "compromise")`,
`:2884` `_cap_token, _cap_region = _capture_answer`, `:3862` the objection `choices` list. All correct.
**UNVERIFIED by me:** the end-to-end resolution of each printed answer phrase — I did not re-drive
probe `p07`. The reasoning ("bare-parser FAIL is a false negative here") is sound and is the mirror
image of the flaw I found in TC-CLEAN-1.

---

## REFUTE:TC-PIN — SURVIVES in shape, NARROWED in four specifics

The two-halves design (derive + two-directional closure, the `RAIL_EXEMPT_TYPES`/REV-V3 idiom) is the
right shape and the "must run under `LLM_MODE=mock`" argument is not only right but **stronger than
stated**: I measured that `halt Ney` escalates in live mode, so a live-mode pin would have been green
on the row's own headline. Corrections:

1. **The two-list drift pin is written over 2 of 5 producers.** It names `executor.py:2282` and
   `main.py:3862` — **both cites are correct at HEAD** (see the retraction box below; I first called
   `:2282` stale and was wrong). But there are **five** producers shipping `choices` into
   `format_answer_words`, all HEAD line numbers: `executor.py:1143/1146`, `executor.py:2282`,
   `strategic_executor.py:2685/2686`, `meta_executor.py:1809/1810`, `main.py:3371/3862`. I checked all
   five: every one ships only `trust`/`insist`/`compromise`, so the drift it fears is **not live
   today** — but a pin written over 2 of 5 producers would not notice when it becomes live.
2. **The naval chips are 6 and 4, not 4.** AST over `backend/` for dicts carrying a `command` key
   (probe `r08`) finds **6** literal command chips in `naval.py` (`:2760, :2800, :2813, :2824, :2844,
   :2861`) and **4** more in `naval_executor.py` (`:442, :445, :720, :723`).
3. **The tutorial mechanism cannot see two of its own printed commands.** TC-PIN proposes regexing the
   `"suggest"`/`"suggest_action"` pairs — correct, and the 12/12 count is right (I briefly
   over-counted 18 by conflating `suggest_action` ids with chip text; recorded so it is not repeated).
   But two commands are printed inside step **body** prose, inside `[color=…]` spans, and are not
   suggest chips (probe `r10`): **`Ney, move to Swabia`** and **`build watchtower in Lorraine`**. Both
   parse today, so no live defect — but the proposed mechanism is structurally blind to them, which is
   the row's entire purpose.
4. **The dialogue-label mechanism must build the real dialogue**, not a bare `ast.List` of option
   dicts — see TC-CLEAN-1. As written, the pin would freeze the wrong behaviour for three families.

Confirmed correct in TC-PIN: render-don't-scrape for the help (the missions block really is spliced at
runtime by `_missions_help_block`, `meta_executor.py:166`), the 7-entry epithet allowlist, the
call-don't-scrape rule for `dotation.rente_action_keys` / `mission_recall_command`, and the
`disobedience.py:2102` / `objection_v2.py:1434` argument that prose refusal copy needs an allowlist.

---

# What the census missed

## MISSED:1 — `llm_client._berthier_mock_response`: eight command-shaped strings printed at the exact moment the player is lost, and one of them is an act of war against a neutral

The census walked fourteen producers. This is a fifteenth, and it is arguably the most important one in
the game: `backend/ai/llm_client.py:1164` `_berthier_mock_response` is what the player reads **when the
parser has already failed**. It prints eight command-shaped strings across three template groups
(HEAD `:1202-1240`). The census's §7 AST walk excluded `prompt_builder.py` by name and never reaches
`llm_client.py` at all; the file appears nowhere in its tables.

Rendered on the shipped 1805 boot and parsed (probe `r05` — 200 samples per group to defeat
`random.choice`): **every one parses.** The defects are semantic.

**(a) `'declare war on Prussia'` — the guard and its violation in one function.**
`:1183-1184` calls `_hostile_first(game_state, enemy_names)`, whose docstring reads:

> *FA-80 (c): the shrug proposed attacking enemies[0] — Deroy of Bavaria on the 1805 boot, a court
> France is NOT at war with (measured: 2 of 12 shrugs).*

Fifty-two lines later (HEAD `:1236`), the no-recognition template hardcodes:

```
"A clear order might be: 'Ney, attack Mack' or 'end turn'.
 For diplomacy: 'declare war on Prussia' or 'propose peace with Austria'."
```

France boots at **PEACE** with Prussia (measured; and the AI-0c historian test pins it). Driven on the
real road at turn 1:

```
REAL ROAD 'declare war on Prussia'  success=True  'Choose your war purpose against Prussia.'
```

The game's "I did not understand you, here is an example" message offers, as its worked example, an
irreversible act against a neutral great power — and the road accepts it and opens the war-purpose
dialogue. The marshal half of this exact rule was fixed in FA slice 7; the diplomatic half was never
covered by the guard.

**(b) `'propose peace with Prussia'` is a dead command at boot.** Same group, different template:

```
REAL ROAD 'propose peace with Prussia'  success=False
  'We already have Peace with Prussia. Talleyrand sees no purpose in proposing
   what we already possess.'
```

**(c) `'Talleyrand, propose alliance with Austria'`** refuses at boot for DP (`costs 9 DP, we only
have 5`) — softer, but still an example that does not work when it is printed.

So of the four hardcoded diplomatic examples Berthier offers a lost player on turn 1: one works, one is
a no-op refusal, one is a DP refusal, one starts a war with a neutral.

**(d) `'{marshal}, move to Paris'`** (`:1207`) is a hardcoded region in a function that reads real
marshal and enemy names from `game_state`. It is correct only because the player is France; the
scenario format makes `player_nation` authorable. Latent, P4, but it is the same class as the census's
own INFO-2 ("stale teaching surfaces name marshals the 1805 game does not have") — one noun over.

**(e) a raw camelCase key can reach the copy.** `recognized_target` is
`parsed["command"]["target"]` (`main.py:3696`, unmodified at HEAD), i.e. the canonical key, echoed verbatim into
`'{first_marshal}, move to {recognized_target}'`. Rendered with `ArchdukeCharles` it prints
`'Ney, move to ArchdukeCharles'` — parses, but violates R7. (`first_enemy` is safe at HEAD:
`_hostile_first` humanises. With `BERTHIER_NAMES_AN_ENEMY=False` the raw key `ArchdukeJohn` is
first.) ⚠ **UNVERIFIED:** I did not construct a real typed sentence that lands `ArchdukeCharles` in
`recognized_target` on the live road; I rendered the template with that value directly.

## MISSED:2 — `Ney, cancel` and the other five broken cells

Detailed in TC-1 above. Short version: the census tested bare `cancel` (PASS, as a column label) and
`cancel Ney` (PASS, as the printed string) and never tested `Ney, cancel`, the form the same help page
teaches in fourteen other rows. It fails. So do `Ney, stop`, `Ney, abort`, `stop Ney`, `abort Ney`.
`belay`, printed nowhere, works in every position.

## MISSED:3 — the instrument the row proposes to trust is blind to the row's own family

`tests/data/parser_golden_corpus.json` is 447 entries. Nine mention the cancel family. **Zero contain
the word `halt`.** `parser_eval` reports **686/686 on both arms of the flip experiment** — green with
the fix, green without it, green while the fix flips five behaviours. The census sequences "Fix TC-1
… otherwise the pin lands red" as step 1 and the drift pin as step 2; on this evidence the fix needs
its own falsifiable pins *in the stand-still family*, and the corpus is not that instrument.

## MISSED:4 — the census's own §7 mechanism, generalised, finds 142 command-carrying entries, not five

The census scanned `backend/` for non-docstring string literals (148 hits) and separately looked at
`naval.py chips.append` literals ("4 rows"). A different and better census — every dict in `backend/`
carrying a `command` / `action_command` key, which is what the client re-sends verbatim
(`region_panel.gd:138`, `strategic_ledger.gd:820`/`:1160`) — finds **142 entries across 20 modules**
(probe `r08`): `strategic.py` 72, `marshal.py` 13, `strategic_executor.py` 12, `clarification.py` 8,
`naval.py` 6, `naval_executor.py` 4, `delegation.py` 2, `dotation.py` 1, …

Two things fall out that bear on TC-PIN:

* `clarification.py:157/200/253/311` build full reissue commands
  (`f'{m.name}, {order_text}'`, `f'{marshal.name}, attack {enemy.name}'`,
  `f'{marshal.name}, move to {name}'`) — the file TC-2 lands in, never opened.
* `marshal_overview.py:99` is `{"command": "rally & recovery (fast 8+, poor 3-)"}` — the marshal
  card's *skill* row. A census keyed on the `command` key alone mis-files it as a typed command. That
  is the same hazard the census correctly identifies for `'PURSUE'` and `"Hold? The enemy is RIGHT
  THERE!"`, so the allowlist it proposes must cover this family too.

## MISSED:5 — tutorial card body prose

Two printed commands live in step **bodies**, not in `suggest`:
`Ney, move to Swabia` and `build watchtower in Lorraine` (probe `r10`, from
`tutorial_overlay.gd` `"body"` strings inside `[color=#e8d4a8]…[/color]`). Both parse on the tutorial
world, so nothing is broken — but the existing pin
(`tests/test_tutorial_position7.py` extracting `(suggest, suggest_action)` pairs) and the mechanism
TC-PIN proposes are both structurally unable to see them.

---

## ⛔ A correction to THIS report, recorded rather than buried

I first filed TC-PIN correction #1 as *"a stale cite: `executor.py:2282` is prose about a neglected
marshal; the real list is `executor.py:2330`."* **That was wrong and is retracted.** At HEAD,
`git show HEAD:backend/commands/executor.py | grep -n '"choices": \["trust"'` returns **2282** — the
census's cite is exact. I had read the number off the **working tree**, and while this pass was
running the concurrent agent began modifying `backend/commands/executor.py` as well (`git status`
went from two modified files to four mid-session, and that line moved 2282 → 2330 → 2343 inside an
hour).

Two consequences worth carrying forward:

* **Every line number in this report is a `git show HEAD:` number**, re-derived after I caught this.
  The ones I had taken from the working tree and have now corrected: `_should_fallback_to_llm`
  (874, not 900), `_missions_help_block` (166, not 167), the `clarification.py` reissue f-strings
  (157/200/253/311, not 153/196/249/307), `format_answer_words(_choices)` (`executor.py:1143`).
* **The census's own line numbers are accurate at HEAD** — which, given this repo's stated ~80%
  stale-line rate, is worth saying out loud rather than only attacking. I found one wrong cite in the
  whole report and it was mine.

---

## On the census's own process notes

Two things I checked rather than accepted:

* **The dirty-tree argument holds.** The concurrent diff is live and still growing; its only
  behavioural seam is `clause_guards.is_question(text, subjects)` at two `llm_client` call sites. I did
  not rely on the argument: every measurement above was taken on my own `git show HEAD:`-materialised
  tree with a module-path assertion in each probe, and the md5s match.
* **"≈290 distinct printed strings across 14 producers"** is not auditable from the report — the tables
  enumerate roughly 130 rows plus "170 in-set checks" plus "32 column labels", and the in-set checks
  are not distinct strings. **UNVERIFIED**; I did not attempt to reconstruct the 290.

## What I would change about the row before it is built

1. **TC-1's fix must be bounded to the roster**, not a `"halt "` substring, and must land with pins in
   the stand-still family (`halt here, then attack Mack`, `halt and hold`, `halt recruitment`) — the
   corpus will not red for them.
2. **TC-2 is not a separate decision.** State on the row that it closes with TC-1.
3. **Widen TC-1 to the grid** (`Ney, cancel` above all) or the row fixes the printed example and leaves
   the idiom the same page teaches still broken.
4. **TC-CLEAN-1 must be re-measured on real dialogue shapes** before "clean by construction" is
   written down anywhere a future session will trust it; on the shape the player meets, 10 of 12 lines
   route differently and one line the game refuses reads as a PASS.
5. **Add `_berthier_mock_response` to the census as its own producer.** It is the one surface whose
   whole job is teaching, and its diplomatic examples are ungoverned by the guard sitting in the same
   function.
