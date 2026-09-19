# The Teaching Census — every string the game prints that looks like a typed command

**Run:** September 19, 2026 · repo `C:\Users\User\PycharmProjects\project-sovereign-map`
**HEAD:** `f7008582` (IQ-10 "The Client Pass")
**Mode:** `LLM_MODE=mock` throughout — zero network calls, no key. Mock is also the *shipped tester default* (`deploy/launch.bat` writes `LLM_MODE=mock` when no real key is present, pre-build fix pass), so a mock failure is a shipped failure.
**Probes:** `…/scratchpad/cx_recon/probes/p00…p23`, outputs `…/scratchpad/cx_recon/p0*.txt`, `p1*.txt`, `p2*.txt`, `help_live.txt`, `ast_playerfacing.txt`, `gd_scan.txt`.

---

## ⚠ Read this first: the working tree was NOT clean during this run

The session's opening `git status` snapshot said `(clean)`. It is not:

```
 M backend/ai/clause_guards.py   (+146/-…)
 M backend/ai/llm_client.py      (+22/-…)
```

Another agent in this workflow is editing the parse pipeline concurrently (the new code is commented `CX — …`). **Every measurement below was taken against that modified tree, not against `f7008582`.** I did not revert it (read-only brief) and did not `git stash` (forbidden).

**I measured whether the diff can reach any finding, rather than assuming it cannot.** The diff's only behavioural seam is `clause_guards.is_question(text)` gaining a second `subjects` argument, consumed at exactly two `llm_client` call sites (`:1370`, `:1619` in the modified file). A string for which `is_question()` is `False` cannot take the changed branch. Probe `p23_dirtycheck.py` evaluates `is_question` on all fifteen findings-bearing strings under **both** signatures:

> `halt Ney`, `halt Davout`, `halt Soult's march`, `cancel Ney`, `Improve Relations Austria`, `Gather Intel Austria`, `gather intelligence on Austria`, `Talleyrand, assess our situation`, `guard Ney`, `fight to the last`, `attempt a breakout`, `build depot in Paris`, `endow Ney with Swabia`, `propose peace with Kingdom of Italy`, `buy off Papal States` — **`is_question` is `False` for all fifteen, on both signatures.**

So the findings are diff-independent.

**Then I re-verified them on pristine HEAD rather than resting on that argument.** A concurrent agent had already materialised a clean tree at `…/scratchpad/cx_recon/pristine/`; I confirmed both files there are **byte-identical to `git show HEAD:`** (md5 `0f70a21a…` for `llm_client.py`, `b127169e…` for `clause_guards.py`) and re-ran the headline with `sys.path` pointed at it (probe `p24`, asserting the loaded module path):

```
module under test: …/pristine/backend/ai/llm_client.py
'halt Ney'          -> (False, None, …, 'Unknown action: unknown')
'halt Davout'       -> (False, None, …, 'Unknown action: unknown')
'halt Soult'        -> (False, None, …, 'Unknown action: unknown')
'cancel Ney'        -> (True, 'cancel', 'Ney', …)
"halt Soult's march"-> (True, 'move', 'Soult', 'generic', …)
'Ney, halt'         -> (True, 'cancel', 'Ney', …)
HELP quoted command-shaped: 43   FAILS: ['halt Ney']
```

**At `f7008582`, `halt Ney` is the single failure among all 43 command-shaped quoted phrases in the COMMAND REFERENCE.**

**UNVERIFIED:** only the *help* census was re-run on pristine; the other thirteen producers were measured on the modified tree and rest on the `is_question` argument above. Three of the 129 shipped dialogue option labels *are* questions (`What should we do?`, per IQ7-RV31) — those were exercised through `match_dialogue_answer`, which the diff does not touch.

---

## Headline

**≈290 distinct printed strings walked across 14 producers. Two real defects, both in one family: the `halt` verb.**

| | |
|---|---|
| **TC-1 · P2** | **The COMMAND REFERENCE prints `"cancel Ney" / "halt Ney"` as equals. `halt <Marshal>` does not parse.** Confirmed on the real `/command` road: Berthier refuses, the standing order stands. `meta_executor.py:705`. Re-verified on pristine HEAD — it is the **only** failure among the help's 43 command-shaped quoted phrases. |
| **TC-2 · P3** | **`halt <Marshal>'s march` asks whether you want to *march*.** Parses `MOVE_TO` at confidence **0.9** — above the escalation gate, so the LLM is never consulted. Answering `yes` marches the corps and destroys the order it was asked to halt. |
| **INFO** | Everything else passes. The IQ10-6 pattern is otherwise *not* widespread — three families are clean by construction (see "Why the rest holds"). |

Corrections to my own work, recorded rather than buried, are at the end.

---

## The table

`PASS` = the real road reaches the intended action. `N/A` = printed, but not a command by design. Producer paths are repo-relative; line numbers were read at this HEAD.

### 1 · The COMMAND REFERENCE — `meta_executor._execute_help`, `backend/commands/meta_executor.py:629`

The help body is one literal beginning at `:639`; the missions block is spliced at runtime by `_missions_help_block` (`:166`). I extracted from the **rendered** text (12,717 chars, `help_live.txt`), not from source — probes `p01`, `p02`.

**50 quoted phrases · 43 command-shaped · 42 bare column labels also tested.**

| Printed string | Producer | Verdict |
|---|---|---|
| `Ney, attack Mack` | `meta_executor.py:645` | PASS `attack`/Ney/Mack |
| `attack` (nearest) | `:645` | PASS |
| `Davout, defend` | `:648` | PASS `defend` |
| `hold` (alias) | `:648` | PASS `hold`, strategic `HOLD` |
| `Soult, move to Bavaria` | `:651` | PASS `move`→Bavaria |
| `Ney, retreat` | `:654` | PASS `retreat` |
| `recruit` · `recruit for Davout` · `recruit at Paris` | `:657` | PASS ×3 |
| `buy substitutes for Ney` · `purchase a levy for Ney` · `hire replacements for Ney` | `:663-664` | PASS ×3 → `purchase_levy` |
| `bombard Swabia` | `:681` | PASS → `attack`/Swabia |
| `Davout, fortify` | `:689` | PASS |
| `Soult, drill` | `:692` | PASS |
| `scout Tyrol` · `Davout, scout` | `:693` | PASS ×2 |
| `Ney, go aggressive` | `:700` | PASS `stance_change` |
| `Ney, march to Vienna` | `:704` (approx.) | PASS strategic `MOVE_TO` |
| `Murat, pursue Kutuzov` | `:705` region | PASS strategic `PURSUE` |
| `Lannes, support Ney` | `:706` region | PASS strategic `SUPPORT` |
| `Davout, hold Ulm` | `:707` region | PASS strategic `HOLD` |
| `cancel Ney` | **`:705`** | PASS `cancel` |
| **`halt Ney`** | **`:705`** | **FAIL — TC-1, below** |
| `economy` · `treasury` | `:709` | PASS ×2 |
| `build market at Paris` | `:711` | PASS |
| `repair Lyon` | `:712` | PASS |
| `Endow Ney with the Duchy of Swabia` | `:713` | PASS → `grant_dotation`/Swabia |
| `Grant Ney a rente` · `Revoke Ney's rente` | `:722` | PASS ×2 |
| `build ships` · `lay down a ship` | `:741` | PASS ×2 → `build_fleet` |
| `blockade the enemy` | `:745` | PASS `set_fleet_posture` |
| `guard home waters` | `:752` | PASS `set_fleet_posture` |
| `land Soult in Munster` | `:754` | PASS `naval_expedition` |
| `order the diversion` | `:764` | PASS `naval_diversion` |
| `Talleyrand, assess our situation` · `Talleyrand, assess Austria` | `:775-777` | PASS ×2 `diplomatic_advisory` |
| `buy off Prussia` | `:786` region | PASS `buy_off_design`/Prussia |
| `sponsor Prussia against Austria, 200 gold` | `:790` region | PASS `sponsor_design` |
| `license Prussia against Austria` | `:794` | PASS `sponsor_design` |
| `guarantee Saxony` | `:796` region | PASS `guarantee_nation` |
| `"Bravest of the Brave"` + 6 more epithets | `:822-829` | **N/A** — quoted *names*, not commands |
| **Bare column labels** (`attack`, `defend`, `move`, `retreat`, `recruit`, `bombardment`, `garrison`, `fortify`, `unfortify`, `drill`, `scout`, `form square`, `break square`, `aggressive`, `defensive`, `neutral`, `march`, `pursue`, `support`, `hold`, `cancel`, `economy`, `endow`, `rente`, `blockade`, `substitutes`, `help`, `end turn`, `wait`, `status`, `buy off`, `sponsor`) | help left column | PASS ×32 |
| Bare `build`, `repair`, `land`, `diversion`, `assess`, `vassals`, `missions`, `war terms`, `guarantee` | help left column | **N/A** — these are *entry headings* whose quoted example beside them is the command. The bare word is not printed as a command. Worth one note: bare `guard` parses as strategic `HOLD` and `guard Ney` as `SUPPORT` — the heading's word is live in a different sense (INFO, below). |
| The **missions** block (`missions`, `Improve Relations`, `Court`, `Gather Intel`, `Undermine Alliance`, `Reassure Ally`) | `_missions_help_block`, `meta_executor.py:166` | **N/A by explicit design** — the block routes to F1 ("F1, a court, then its mission row"), and the code comment at `:154-159` states that teaching a typed mission verb "would teach a dead route". See INFO-2. |

### 2 · The tutorial — `godot-client/project-sovereign/scripts/tutorial_overlay.gd`

Chips FILL the command line; they never auto-send (`:15-16`). Probe `p09`, run against `tutorial_1805.json` — the world the chips actually render in.

| Printed string | Producer | Verdict |
|---|---|---|
| `economy` | `:58` | PASS |
| `Senarmont, move to Munich` | `:67` | PASS |
| `end turn` | `:76` | PASS |
| `Ney, defend` | `:85` | PASS |
| `Senarmont, bombard Jellacic` | `:112` | PASS |
| `Ney, attack Kienmayer` (×2, incl. the `alt` branch) | `:121`, `:147` | PASS ×2 |
| `Davout, march to Franconia` | `:167` | PASS |
| `Davout, move to Bohemia` | `:176` | PASS |
| `Soult, recruit troops` | `:197` | PASS |
| `Davout, scout Bohemia` | `:206` | PASS |
| `Ney, fortify` | `:215` | PASS |

**12/12.** Already pinned by `tests/test_tutorial_position7.py:414 test_b1_every_suggest_mock_parses_to_its_action` — this is the existing model for the drift pin I recommend below.

### 3 · Region panel & Generals chips — typed-command echoes

Probe `p08`. `region_panel.gd:128-143` turns `order:<verb>:<Name>` into `"<Name>, <verb>"` and sends `do:<full command>` verbatim.

| Printed string | Producer | Verdict |
|---|---|---|
| `recruit {infantry,cavalry,artillery} in <Region>` | `region_panel.gd:272` | PASS ×3 |
| `buy substitutes for <Marshal>` | `region_panel.gd:332` | PASS |
| `build depot in <R>` · `build fort in <R>` · `build training ground in <R>` · `build market in <R>` · `build stables in <R>` | `_BUILD_CHIP_DEFS`, `region_panel.gd:516-521` | PASS ×5 |
| `build watchtower in <R>` | `:379`, `:382` | PASS |
| `repair buildings in <R>` · `repair <R>` | `:412`, `:424` | PASS ×2 |
| `build ships` | `:441` | PASS |
| `land <Marshal> in <Region>` | `:461` | PASS |
| `<Name>, unfortify` · `, fortify` · `, drill` · `, scout` | `:545-550` | PASS ×4 |
| `<Name>, attack <Enemy>` | `:557` | PASS |
| `<Name>, {unfortify,fortify,drill}` (Generals card) | `marshal_management.gd:650-654` → `:172` | PASS ×3 |
| `commission <Candidate>` | `main.gd:6221` ← `marshal_management` `commission_requested` | PASS `recruit_marshal` |
| `Talleyrand, assess our situation` | `main.gd:6357` (Talleyrand tab chip) | PASS |
| `or type: 'endow <M> with <R>'` | `marshal_management.gd:568` | PASS |

### 4 · Reward dialog & notice rail

| Printed string | Producer | Verdict |
|---|---|---|
| `endow <M> with <Region>` | `reward_dialog.gd:113` | PASS |
| `grant <M> a rente` | `reward_dialog.gd:134` **and** `dotation.rente_action_keys` → `action_command`, `backend/game_logic/dotation.py:1104` | PASS |
| `revoke <M>'s rente` | `reward_dialog.gd:146` | PASS |
| `Talleyrand, cancel mission with <Nation>` | `diplomatic_dialogue.mission_recall_command` → `details["action_command"]`, `:611` | PASS (key form **and** display form — probe `p17`) |

### 5 · Diplomacy wizard — `diplomacy_wizard.gd::_build_command`

31 literal `return` strings; every one tested (probe `p08`). **31/31 PASS.**

`sponsor_design` (both arms) · `buy_off_design` · `guarantee_nation` · `propose_armistice` · `propose_peace` · `open_settlement` · `propose_white_peace` · `propose_open_borders` · `propose_non_aggression` · `propose_defensive_alliance` · `propose_alliance` · `propose_vassal` · `declare_war` · `break_treaty` · `downgrade` · `send_ultimatum` · `invest_vassal` · `increase_autonomy` · `decrease_autonomy` · `release_vassal` · `grant_region_to_vassal` · `mission_improve_relations` · `mission_court` · `mission_gather_intel` · `mission_reassure` · `mission_undermine` · `cancel_mission`.

One INFO: `propose white peace with X` parses as a **generic `peace` proposal**, not a white peace. That is stated in the wizard's own comment ("the typed string is display copy only — the backend parser does not auto-classify 'white peace'"; the structured payload routes the real action). It is deliberate, but it is the one echo in the wizard whose *typed* meaning differs from its *clicked* meaning.

### 6 · The Admiralty — `backend/game_logic/naval.py` chips

| Printed string | Producer | Verdict |
|---|---|---|
| `blockade the enemy` | `naval.py:2800`, `:2816` | PASS |
| `guard home waters` | `naval.py:2761` | PASS |
| `order the diversion` | `naval.py:2826`, `:2843` | PASS |
| `build ships` | `naval.py:2864` | PASS |
| `order the diversion confirmed` | `naval_executor.py:721` (confirm chip) | PASS |

### 7 · Backend prose that quotes a command

Found by an AST walk over every non-docstring string literal under `backend/` (probe `p05`, 148 hits; `ast_playerfacing.txt`). Excluding `prompt_builder.py` (LLM prompt, not player copy) and parser-internal vocabulary, the player-facing set is:

| Printed string | Producer | Verdict |
|---|---|---|
| `move to <Region>` | `combat_executor.py:5659` ("No enemies within range. Try 'move to X'") | PASS |
| `bombard <Region>` / `bombard <Enemy>` | `combat_executor.py:10146` | PASS ×2 |
| `unfortify` | `executor.py:1473`, `:1738`; `movement_executor.py:419`; `tactical_executor.py:462` | PASS |
| `move` | `executor.py:1930`; `movement_executor.py:1210`; `combat_executor.py:10252` | PASS |
| `attack` | `tactical_executor.py:825` | PASS |
| `recruit 10000 infantry with Ney` | `economy_executor.py:318` | PASS |
| `buy substitutes for Ney` | `economy_executor.py:1211` | PASS |
| `build supply depot at Lyon` | `economy_executor.py:2152` | PASS |
| `repair Lyon` | `economy_executor.py:2312` | PASS |
| `sponsor Prussia against Austria, 200 gold` | `diplomatic_executor.py:311` | PASS |
| `buy off Prussia` | `diplomatic_executor.py:450` | PASS |
| `guarantee Saxony` | `diplomatic_executor.py:538` | PASS |
| `blockade the enemy` / `guard home waters` | `naval_executor.py:218`, `:224`, `:231` | PASS ×2 |
| `land Soult in Munster` | `naval_executor.py:332` | PASS |
| `land Soult in Munster with the transports` | `naval_executor.py:584` | PASS |
| `hold until Davout arrives` | `main.py:3451` (conditional refusal — "a standing order I can hold is…") | PASS strategic `HOLD` |
| `end turn` | `main.py:3466`; `turn_manager.py:267` | PASS |
| `hold` | `main.py:3466` ("If the marshal is to sit still meanwhile, say 'hold'") | PASS |
| `cancel his order` | `main.py:3475` | PASS `cancel` |
| `support X` | `marshal_overview.py:84` (literal-personality card copy) | PASS |
| `defend` | `strategic_executor.py:1808` ("For a single-turn tactical hold, order 'defend'") | PASS |
| `Say "<M>, attack <target_display>"` | `delegation.py:422` (the CR-5 cautious-delegation ASK arm) | **PASS** — and this is the IQ10-6 family. Probe `p12` proves it for the only two 1805 marshals whose display ≠ key: `Archduke Charles`/`ArchdukeCharles`, `Archduke John`/`ArchdukeJohn`. Both display forms resolve to the key. |

### 8 · Answers to the game's own questions (pending-state road, not the parser)

These are printed as typable answers but are routed **before** the parser — by `main._interrupt_choice_from_text` (`main.py:985`, table at `:960`), `_typed_capture_answer`, or the W6-0 token router (`main.py:2841`). Testing them through the bare parser would be a false negative. Probe `p07` drives the real matcher.

| Printed string | Producer | Verdict |
|---|---|---|
| `fight to the last` | `combat_executor.py:4018`, `:4081`; `strategic.last_stand_question_line:247`; `main.gd:1516` | PASS → `fight_to_the_last` |
| `attempt breakout` | `combat_executor.py:4081` | PASS → `attempt_breakout` |
| `attempt a breakout` | `strategic.py:247`; `strategic_executor.py:2542`; `main.gd:1516` | PASS → `attempt_breakout` |
| `attack anyway` · `cancel order` | `strategic_executor.py:2545` | PASS ×2 |
| `press on` | `_INTERRUPT_KEYWORDS`, `main.py:970` | PASS → `continue_order` |
| `continue as ordered` | FA-slice-3 button label | PASS → `continue_order` |
| `plunder` · `secure` · `plunder <Region>` | `world_state.capture_choice_prompt:798`, `:802`; `capture_executor._pending_prompt:217`, `:219` | PASS via `_typed_capture_answer` (`main.py:2884`) — **bare-parser FAIL is expected and is not a defect** |
| `trust` · `insist` · `compromise` | `dialogue_routing.format_answer_words:682`, printed by `main.py:3371`, `meta_executor.py:1809` | PASS via the W6-0 router (`main.py:2841`) while an objection stands — bare-parser FAIL expected |
| `Type 'charge'` · `Type 'restrain'` | `main.gd:5180-5181` | PASS ×2 (real parser) |

**Note the copy inconsistency, not a defect:** the same question is printed as `attempt breakout` in `combat_executor` and `attempt a breakout` in `strategic.py`/`main.gd`. Both resolve (the keyword is the substring `breakout`), so it costs nothing today — but it is exactly the kind of two-spellings-one-question drift the pin below should freeze.

### 9 · Dialogue option labels — the largest family, clean by construction

`dialogue_routing.py:1692` prints the active dialogue's own option **labels** through `format_answer_words` so the player can type them verbatim. I harvested them mechanically rather than by hand (probes `p10`, `p11`):

- **129 unique literal `{label, action}` pairs** across `backend/`, every one claimed by `match_dialogue_answer` when typed verbatim — **0 failures**.
- **67 complete literal option *sets*** (list literals of ≥2 such dicts), **170 in-set checks**, each label resolving to its **own** option inside its own set — **0 failures**.

Verdict **PASS ×170**. Honest limit: the harvest only sees *literal* dicts; labels built by f-string (`f"Endow {region} — {income}g/turn"`) are not covered, and I did not build the cross-set adversarial cases IQ-7's review round covered (`IQ7-RV31` is the precedent — three shipped labels *are* questions).

### 10 · MISSION_DESCRIPTIONS — the IQ10-6 generalisation

The game prints `"Sire, I shall begin efforts to {MISSION_DESCRIPTIONS[t]} {nation}."` at `diplomatic_dialogue.py:1966`. IQ-10 pinned one of the five. Probe `p15` runs all five, × two nations (one single-word, one multi-word display form):

| Printed sentence | Verdict |
|---|---|
| `improve relations with <N>` | PASS → `IMPROVE_RELATIONS` |
| `court and charm <N>` | PASS → `COURT_NATION` |
| `gather intelligence on <N>` | PASS → `GATHER_INTEL` *(the IQ10-6 fix; holds)* |
| `undermine alliances with <N>` | PASS → `UNDERMINE_ALLIANCE` |
| `reassure <N>` | PASS → `REASSURE_ALLY` |

**10/10**, including `Papal States` → `PapalStates` on every one.

### 11 · README_TESTER — `deploy/README_TESTER.txt` (git-tracked)

| Printed string | Line | Verdict |
|---|---|---|
| `Ney, attack Mack` | `:65`, and again `:239` | PASS |
| `Davout, move to Bavaria` | `:66` | PASS |
| `Soult, hold Lorraine` | `:67` | PASS |
| `Talleyrand, assess our situation` | `:68` | PASS |
| `end turn` | `:69` | PASS |

### 12 · Nation and marshal DISPLAY forms inside printed commands

Because so much copy interpolates a display name into a command, I tested the display↔key axis directly (probes `p12`, `p13`, `p14`, `p17`).

- The three 1805 nations whose display ≠ key (`KingdomOfItaly`→`Kingdom of Italy`, `Ottoman`→`Ottoman Empire`, `PapalStates`→`Papal States`) resolve correctly for `propose peace with` / `declare war on` / `gather intel on` / `buy off` / `guarantee` / `sponsor` / `Talleyrand, cancel mission with` — **both** display and key spellings. **PASS.**
- The two marshals whose display ≠ key resolve both ways. **PASS.**

---

## The two defects

### TC-1 · P2 — `halt <Marshal>` is printed beside `cancel <Marshal>` and does not work

**Printed:** `meta_executor.py:705`
```
  cancel     - "cancel Ney" / "halt Ney" (1 AP)
```

**Proven on the real `/command` road** (probe `p21`, fresh `/new_game`, no pending interrupt):

```
A1  "Davout, march to Franconia"  -> success, order = (MOVE_TO, Franconia)
A2  "halt Davout"                 -> success=False
    'Sire, Marshal Davout awaits your command, but I cannot parse this
     order. Might you mean 'Davout, scout' or 'Davout, defend'?'
    order STILL = (MOVE_TO, Franconia)
A3  "cancel Davout"               -> success
    'Davout halts his march and awaits new orders.'   order = ()
```

Reproduced for Ney, Soult, Lannes, Bernadotte, Davout, Murat (probes `p03`, `p18`).

**Root cause** — `backend/ai/llm_client.py:1802-1807`, the cancel keyword list:
```python
elif any(kw in command_lower for kw in [
    "cancel order", "cancel orders", "cancel ", "halt order", "halt orders",
    "abort order", "abort orders", "abort mission",
    "belay that", "belay",
    " halt", ", halt",
]):
```
`cancel` carries the **trailing-space** form `"cancel "`, so `cancel Ney` matches. `halt` carries only the **leading**-space/comma forms `" halt"` and `", halt"`, so `Ney, halt` and `Ney halt` match — but `halt Ney` (halt in first position) matches nothing. The exact-match arm one line below (`:1809`) only catches a **bare** `halt`. Same asymmetry hits `stop Ney` and `abort Ney`, neither of which is printed anywhere.

Re-verified on the pristine HEAD tree (probe `p24`): `halt Ney`, `halt Davout`, `halt Soult` all fail; `cancel Ney` and `Ney, halt` both pass.

**Two honest caveats.**
1. `halt Ney` parses at confidence **0.5**, which is *below* the 0.7 escalation gate (`llm_client.py:63`), so under `LLM_MODE=anthropic` it **would** be handed to the model and might be rescued. I could not test that (no key; the conftest network guard forbids it) — **UNVERIFIED in live mode.** It fails in mock, which is what ships to testers.
2. `halt <Marshal>` *does* succeed when that marshal has a **pending strategic interrupt** — `_interrupt_choice_from_text`'s `("hold","stay","stop","wait","halt")` row claims it first and resolves `hold_position`. I hit this by accident in probe `p20` and it briefly looked like a pass. It is not: it works only while a question is open, and the help text does not say so. The clean-room arm above is the real behaviour.

**Smallest fix:** add `"halt "` to the list at `llm_client.py:1803`. `stop ` and `abort ` deliberately excluded — `stop Davout's pension` is a revoke and `stop the war with Britain` is a peace proposal, both pinned in the golden corpus; `halt` has no such collision.

### TC-2 · P3 — `halt <Marshal>'s march` asks whether you want to march

**Not a printed string** — found in TC-1's neighbourhood, and worth the row because it is the natural thing a player types after `halt Ney` shrugs.

Probe `p22`, real road, fresh game:
```
pre   Soult order = (MOVE_TO, Munich)
ask   "halt Soult's march"  -> 'You wish me to march to Swabia, Sire?'
yes   "yes"                 -> cost=1, Soult marches to Swabia
post  Soult order = ()      # the Munich order is gone
```

The possessive `'s march` puts the word `march` in the sentence; the strategic upgrade wins the keyword chain, target resolves to `generic`, and the CR-2 clarification asks the player to confirm **the opposite of what they asked for**. Its Munich order is then destroyed.

**Severity is P3, not P2, and I want to be precise about why:** it *asks*. It does not silently march. The system is legible — but the question it asks is the inverse of the request.

**The interesting part for the parser road:** this parses at confidence **0.9** (probe `p19`), which is *above* the escalation gate, so `_should_fallback_to_llm` returns **False** and the LLM is never consulted. This is the "confidently wrong" class that CR-2's forced retry was built for, and the retry only fires on a *downstream fuzzy failure*, which this does not produce. No model, cheap or expensive, can help here. `halt Murat's advance` fails honestly (no `march` token), which confirms the mechanism.

---

## Two INFO rows

**INFO-1 · mission ROW labels read as imperatives and are not typable.** `MISSION_ROW_DISPLAY` labels appear in the help's missions block and the Talleyrand ledger tab as `Improve Relations - 2 DP a turn`, `Gather Intel - 1 DP a turn`. Typed bare with a nation they fail (probe `p15`):

| Typed | Verdict |
|---|---|
| `Improve Relations Austria` | **FAIL** (`unknown`, conf 0.5 → would escalate in live) |
| `Gather Intel Austria` | **FAIL** |
| `Court Austria` · `Undermine Alliance Austria` · `Reassure Ally Austria` | PASS |

The missing preposition is the whole difference — `improve relations **with** Austria` and `gather intel **on** Austria` both pass. **I am not calling this a defect:** `meta_executor.py:154-159` states in writing that the missions block routes to F1 on purpose, because a typed mission verb "would teach a dead route". It is a row for the *copy* owner, not the parser owner: two of five labels read like commands that do not work, in a block that never claims they are commands.

**INFO-2 · two stale teaching surfaces name marshals the 1805 game does not have.**
- `backend/commands/parser.py:2272 get_help()` — a second, complete help text (`"Ney, attack Wellington"`, `"Grouchy, scout the area"`, `"Retreat to Paris"`, `"attack!"`). **Dead:** its only caller is the `__main__` demo at `:2388`. Not player-facing; worth deleting so nobody revives it.
- `deploy/dist/ink_iron_server/README_TESTER.txt` — the March build's tester readme, **not git-tracked**, teaching `"Ney, attack Wellington"` and `"Drouot, bombard the enemy at Belgium"`. Harmless while nobody ships that folder; a hazard the day someone does. The tracked `deploy/README_TESTER.txt` is correct.
- `docs/TUTORIAL_SCRIPT.md` likewise names Wellington and Drouot, but its own header says the live script is `tutorial_overlay.gd` STEPS. Design doc, N/A.

**INFO-3 · `guard` is live in a sense the help does not mean.** The Admiralty heading `guard - "guard home waters"` sits beside a parser in which bare `guard` is a strategic `HOLD` and `guard Ney` is a strategic `SUPPORT` (it is a documented delegation synonym, `prompt_builder.py:432`). The quoted example works; the heading word means something else. No action needed, recorded so it is not rediscovered.

---

## Why the rest holds — three families are clean *by construction*, and that is the design to copy

The census found far less rot than the IQ10-6 precedent suggested, and the reason is structural, not luck:

1. **The chip families send the string, they do not describe it.** `region_panel.gd:136-140` and `marshal_management.gd:172` carry the full typed command in the `meta` and emit it verbatim. There is no second spelling to drift from.
2. **The option-label family has one resolver.** Every producer's label goes through `format_answer_words` for display and `match_dialogue_answer` for resolution, so 170/170 pass without any producer knowing about the parser.
3. **The display-name family has one humaniser.** `display_names.humanize_entity_name` / `display_nation` are the R7 chokepoints, and `_resolve_target` learned the spaced form (CR-5, comment at `delegation.py:419-421`). Both directions resolve.

**Where drift lives is where a producer *retypes* the command in prose** — the help text, which is a 12,717-character hand-maintained literal with a `MAINTENANCE NOTE` at `meta_executor.py:632` asking the next editor to keep it in sync by hand. Both defects are in it. That is the thing to automate.

---

## The drift pin

### Shape

One test module, `tests/test_teaching_census.py`, with **one rule**:

> Every command-shaped string the game prints must reach its intended action through the same road a player's keystrokes take, under `LLM_MODE=mock`.

Mock is non-negotiable: it is the shipped default, and IQ-9's discipline is that the escalation path must not be what makes a pin green. TC-1 would have gone undetected by a live-mode pin.

The pin has **two halves, and the second is what makes it a drift pin rather than a coverage test**:

- **(a) the census** — derive the printed set from the producers at test time;
- **(b) the closure** — assert the derived set *exactly equals* a committed classification. A newly-added quoted phrase reds the test until somebody classifies it as `COMMAND`, `SPEECH` or `INTERNAL`. This is the two-directional census idiom the project already uses for `notifications.RAIL_EXEMPT_TYPES` (REV-V3), and it is the only part that survives contact with new copy.

Without (b) the pin freezes today's strings and silently ignores tomorrow's — which is precisely how the help text drifted in the first place.

### Producers a census can enumerate mechanically

| Producer | Mechanism | Notes |
|---|---|---|
| **COMMAND REFERENCE** | Call `MetaExecutor(None)._execute_help({}, {"world": w})` on a real 1805 world; `re.findall(r'"([^"\n]+)"', flat)` over the **rendered** text | Proven: 50 phrases, probe `p01`. Must render, not scrape source — the missions block is spliced at runtime. Needs a 7-entry epithet allowlist (see below). |
| **`tutorial_overlay.gd` suggests** | Regex `"suggest"`/`"suggest_action"` pairs | **Already exists** — `test_tutorial_position7.py:414`. Extend with a `>= 10` floor (it has one) and run the pairs against the tutorial world. |
| **`diplomacy_wizard.gd::_build_command`** | Regex the `return "…"` lines of the `match` block, substitute a fixture nation / aim / amount | 31 rows, **no pin today**, richest client producer. Build this one. |
| **`region_panel.gd` `_BUILD_CHIP_DEFS`** | Parse the `const` array at `:516-521`, `% region` | 5 rows, trivially mechanical. |
| **Backend dialogue option labels** | AST: every `ast.List` of `{label, action}` dict literals → assert `match_dialogue_answer(set, label.lower())` is not None | 67 sets / 170 checks, probe `p11`. Fails closed on new labels. |
| **`MISSION_DESCRIPTIONS`** | Iterate the dict; `f"{desc} {nation}"` must yield that `mission_type` | Generalises the existing IQ-10 pin from 1 of 5 to 5 of 5. Fails closed on a new mission type. |
| **Admiralty chips** | AST: `chips.append({"command": "…"})` literals in `naval.py` | 4 rows. |
| **Single-producer f-strings** (`dotation.rente_action_keys`, `mission_recall_command`) | **Call the function** with a real world and parse its output — do not scrape | 2 rows; the most robust form of all, since the pin exercises the producer. |
| **`deploy/README_TESTER.txt`** | Regex the indented quoted lines under `TYPE ORDERS` | 5 rows; also assert every marshal/region named exists in the boot world (which is what would have caught the dist readme). |
| **Answer-token drift** | AST-extract every literal `choices` list shipped to `format_answer_words` (`executor.py:2282`, `main.py:3862`) and assert each value is in the router's tuple at `main.py:2841` | Not a parse pin — a **two-list drift pin**. Today both lists are `("trust","insist","compromise")`; nothing stops a producer shipping a fourth. |

### Producers that need an allowlist, and why

| Producer | Why it cannot be derived |
|---|---|
| **Prose refusal / advisory copy** (~22 rows in §7) | The AST scan *finds* them (148 non-docstring hits, probe `p05`) but cannot decide what they are. `'unfortify'` is a command; `"Hold? The enemy is RIGHT THERE!"` (`disobedience.py:2102`) is a marshal speaking; `'PURSUE'` (`objection_v2.py:1434`) is an internal enum. No regex separates those — the distinction is authorial intent. **Recommended: run the AST scan as the census and commit `tests/data/teaching_allowlist.json` mapping every harvested phrase to `COMMAND` / `SPEECH` / `INTERNAL`.** The pin asserts (i) every `COMMAND` row parses, (ii) the harvested set equals the allowlist keys exactly. New copy reds the test with a one-line classification as the fix. |
| **Concatenated `.gd` chips** (`"do:recruit " + arm + " in " + _region`) | The command is assembled from runtime variables; a test cannot evaluate GDScript. **Allowlist the ~8 templates, then add a source census** asserting the count of `"do:` occurrences in `region_panel.gd` equals the number of covered templates — so a NEW chip reds the pin even though its string cannot be derived. |
| **Interrupt answer phrases** | The printed phrase lives in prose (`combat_executor.py:4081`, `strategic.py:247`, `main.gd:1516`) while the acceptor is a keyword table (`main.py:960`). Neither side names the other. **Allowlist `(phrase → options)` pairs** and assert `_interrupt_choice_from_text(phrase, options)` is not None. Must carry **both** spellings of the breakout answer. |
| **f-string option labels** | `f"Endow {region} — {income}g/turn"` cannot be harvested as a literal. Allowlist by producer function, or accept the stated gap. |

### The ambitious alternative — worth proposing, not worth building today

The allowlist exists only because the printed string and the parsed string are two independent pieces of text. A `backend/teaching.py` registry — one module holding every command the game teaches, with producers importing rather than retyping — would delete the allowlist problem entirely and make the pin a one-line iteration. It would also have made TC-1 impossible: `cancel Ney` and `halt Ney` would be two entries under one action, each parse-checked.

The cost is real (the help text alone is 12,717 characters of hand-written prose that interleaves commands with explanation, and the §7 prose rows are woven into sentences). I would **not** fold it into the pin slice. I would build the pin with its allowlist first, let the allowlist show how often it actually churns, and revisit the registry only if it does.

### Sequencing

1. Fix TC-1 (`"halt "`, one list entry) — otherwise the pin lands red.
2. Land the pin with the nine mechanical producers **and** the two-directional allowlist. The mechanical half alone is ~250 of the ~290 strings.
3. Decide TC-2 and INFO-1 as copy/parser rows separately — neither blocks the pin.

---

## An aside on the relayed question (text prediction / LLM routing)

Not this task's scope, but two measurements here bear on it directly and would otherwise be lost:

- **The confidence gate's failure mode is asymmetric, and the census found one of each.** `halt Ney` scores 0.5 and *would* reach the model (recoverable). `halt Soult's march` scores **0.9** and never does (unrecoverable by any model, cheap or expensive). Routing more traffic to an LLM does nothing for the second class; only a better *scoring* rule — or a guard that notices a stand-down word and a march word in the same clause — does. That is the class worth attacking.
- **A teaching census is, for free, the corpus an autocomplete needs.** The ~250 mechanically-derivable strings are exactly the set a text predictor should offer, they already carry their intended action, and they are producible at runtime from a live world (with real marshal, region and nation names substituted). If a predictor is built, it should read the same census the pin reads — otherwise there will be three spellings to keep in sync instead of two.

---

## Corrections to my own work

Recorded because each one would otherwise read as a finding.

1. **`buy off Kingdom of Italy` is not broken.** My first nation probe asserted the court lands in `diplomatic_data.target_nation`; the compact verbs (`buy_off_design`, `sponsor_design`, `guarantee_nation`) carry it in `command.target`. Re-run with the right field (probe `p14`): all pass, key and display spellings alike. The first result was a probe artefact.
2. **`halt Ney` briefly looked like a PASS.** Probe `p20` ran it against a Ney who held a pending bad-odds interrupt, where the interrupt router claims `halt` before the parser sees it. The clean-room arm (`p21`) is the honest measurement. Stated on the row.
3. **TC-2 is not a silent march.** My first read of the parse output (`action=move`, `strategic=MOVE_TO`) implied the order executed. Driving it (`p22`) shows a CR-2 clarification asks first. Downgraded P2 → P3 and the row says why.
4. **The 129-label harvest first reported 126 failures.** My assertion was `got == action`; `match_dialogue_answer` returns the matched *label* for its verbatim arm. With the real contract (the line is claimed by this dialogue) it is 0 failures, and the stronger in-set version is 170/170.
5. **The bare help-column words are not printed commands.** My first pass counted `land`, `assess`, `vassals`, `war terms`, `missions`, `build`, `repair`, `guarantee`, `diversion` as nine failures. They are entry *headings*; the quoted example beside each is the command, and every one of those passes. Reclassified N/A.
