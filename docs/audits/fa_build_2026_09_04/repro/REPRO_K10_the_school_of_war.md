Both rows reproduce. Report follows.

---

# FA-42 and FA-N78 — reproduction report

Probes (all read-only, all under `…/scratchpad/s14/F_tutorial/`):
`gd_callgraph.py`, `gd_callgraph2.py`, `fa42_trust_arm.py`, `fa42_deep.py`, `fa42_fixshape.py`, `fa42_latch_data.py`, `fa42_event_shape.py`, `fa42_boot_shape.py`, `fan78_blind.py`, `fan78_capture.py`, `fan78_pin_flip.py`.

---

## FA-42 — the tutorial's "trust branch pivot"

### VERDICT: **REPRODUCED, and WIDER than filed** (the row understates the failure and mis-states its evidence)

### What reproduces (numbers)

`fa42_deep.py trust`, 8 seeds, real `TestClient` on `POST /new_game {"scenario":"tutorial"}`, mock parser, card machine ported verbatim from `tutorial_overlay.gd` STEPS:

| measurement | result |
|---|---|
| `trust` produces a Ney→Kienmayer battle on the answer response itself, T2 | **8 / 8** |
| Kienmayer **captured** on T2 | **4 / 8** (not "captures on T2" as stated) |
| Kienmayer **escapes** into Franche-Comte at 639–1,148 men | **4 / 8** |
| card on T4 = `first_battle` (VII), chip `Ney, attack Kienmayer` | **8 / 8** |
| chip clicked on T4 **and** T5 → **refused** | **16 / 16 clicks** |
| overdue line present on T4 | **0 / 8** (only from T5) |
| card releases to `strategic_order` | **T6, 8 / 8** — "sits on that page until turn 6" is exact |

Three distinct refusals, none of them the one the row quotes:

- `Kienmayer is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.` (captured arm)
- `No intelligence on Kienmayer's position, Sire. Scout for him before Ney can give chase.` (escaped arm)
- `Ney is recovering from retreat and cannot attack. Recovery: 3 turn(s) remaining.` (seeds 1, 5 in `fa42_fixshape.py`)

**Wider than filed — the escape arm is the worse half and the row does not mention it.** In 4/8 seeds `regions["Lorraine"].controller == "Austria"` by T4 (`fa42_deep.py`), and by T7 the same 1,000-man remnant has reinforced to **4,137 / 6,633 / 6,972 / 6,972**. So on half the trust runs card VII says *"Kienmayer's screen still stands across the Rhine on allied Bavarian soil — Ney carries three times their number"* while he is standing on **France's own Lorraine, which he has taken**, at 18–35× odds against, invisible to French intelligence. The card is wrong about the province, the soil, the flag and the ratio simultaneously.

### What is false in the row

1. **"Under trust, Ney attacks and captures Kienmayer on T2"** — attacks 8/8, captures **4/8**. (Verification's "2 of 6" and my 4/8 are the same stochastic fact under different RNG seeding.)
2. **"clicks the quill, and is told 'Unknown target: Kienmayer'"** — never observed. That copy was killed by slice 7 / FA-48 (`backend/commands/prisoners.py`). The row's `player_consequence` quotes a superseded message; the defect survives, the evidence does not.
3. **`fix_shape`: "`_pred_battle_happened` accepts that battle"** — a no-op. `_pred_battle_happened` (`tutorial_overlay.gd:509`) already accepts *any* `battle_report` or any `battle`/`conquest` event and names no marshal. Nothing to change.
4. **`fix_shape`: latch "when a battle_report/conquest names Kienmayer as the beaten side"** — the beaten side IS named (`events[0].defender.name == "Kienmayer"`, `battle_report.casualty_summary.defender_name`), **but it is named identically in both outcomes**. Measured (`fa42_event_shape.py`): seed 0 (→captured) and seed 1 (→escaped) produce byte-comparable events — `outcome: attacker_tactical_victory`, `victor: Ney`, `enemy_destroyed: **false**`, `defender_forced_retreat: true`, differing only in `defender.remaining` (471 vs 1153). **There is no capture event in that response at all.** A latch built as filed fires on both arms and would print *"the screen is taken"* over a live Austrian corps holding Lorraine.
5. **"The TUTORIAL_SCRIPT.md table is also stale (rows :344-345)"** — understated. Four rows are stale, not two:

| doc | STEPS |
|---|---|
| `:344` First blood **T3**, `Ney, attack Kienmayer` | `first_battle` gate **4**, step **VII** |
| `:345` The guns speak **T4** | `bombardment` gate **2**, step **VI** |
| the doc's **order** blood→guns | STEPS' order **guns→blood** |
| `:347` Conquest `Ney, attack Jellacic`, fallback `Ney, move to Tyrol` | `capture` suggest is **`Davout, move to Bohemia`** |

Line numbers `:112` (`first_battle`), `:93` (trust listed first) and `:365` (`_maybe_catch_up`) are **exact** — this row is in the ~20% that navigates correctly.

### The real seam

- `godot-client/project-sovereign/scripts/tutorial_overlay.gd` — `const STEPS` entry **`first_battle`** (`:112`, `turn_gate: 4`, body `:115`, suggest `:116`). `STEPS` is a `const`, so any branch must be resolved in **`_render()`** (`:383`), which reads `step["suggest"]` at `:409`.
- Latch home: **`_note_observations`** (`:346`).
- Release: **`_maybe_catch_up`** (`:365`) — `_turn > gate + 1 and _turn >= next.turn_gate` → T6 exactly.
- Doc: `docs/TUTORIAL_SCRIPT.md:343-348`.

### What the filed fix would break

1. **The prescribed replacement chip is legality-by-accident.** Measured adjacency (`fa42_fixshape.py`): `Rhineland.adjacent = [Brabant, Frankfurt, Gelderland, Lorraine, Nassau, Swabia]`, `Swabia.adjacent = [Franche-Comte, Franconia, Lorraine, Munich, Nassau, Rhineland]`. **Neither touches Tyrol.** Only `Munich` does. `Ney, attack Jellacic` returned True in 6/6 seeds *only because the trust arm's autonomy had drifted Ney to Munich by T4* — a position the card does not control — and even then it returns a **MUSTER confirmation modal**, not a battle. On any slower player Ney is at Rhineland or Swabia and the row's fix ships a **second dead chip**.
2. **The prescribed latch fires on both outcomes** (item 4 above) — the "screen is taken" copy becomes a new lie in exactly the 50% of runs where the truth is worse.
3. **The prescribed behaviour test cannot see the new chip.** T-B1 (`tests/test_tutorial_position7.py:411`) extracts with `r'"suggest":\s*"([^"]*)"'` and `r'"suggest_action":\s*"([^"]*)"'`. Measured: current file 15/15. Adding `"suggest_alt"` / `"suggest_action_alt"` → still **15/15** — the regex requires the literal keys, so a branch chip added under any new key ships **unpinned**, and the row's own "assert `first_battle` carries a second suggest … (T-B1 idiom)" is vacuous unless T-B1's regex changes with it.
4. **A whole extra STEPS entry is not a free alternative**: `STEPS.size()` is rendered in the badge (`"%d of %d"`, `:387`) and `_derive_step_for_turn` (`:295`) resumes at *the first* step of the highest gate ≤ turn, so two gate-4 variants would make a mid-lesson reload resume on the wrong branch.
5. **FA-42's fix is production-dead without FA-N78.** Under `trust`, the capture/escape happens on the objection-answer response. On the shipped client that response arrives at `_on_objection_response`, which never observes (see below). So the latch would never be set on the only route a real player can take.

### Pins that flip

Baseline green today: `tests/test_tutorial_position7.py` + `test_tutorial_scenario.py` + `test_tutorial_school_fixes_2026_08_08.py` + `test_hc5_tutorial_names_fleet.py` = **78 passed in 2.80s**.

- `test_tutorial_position7.py::TestSuggestCommandsParse::test_b1_every_suggest_mock_parses_to_its_action` — flips if a branch chip is added under `"suggest"` and does not parse; stays **vacuously green** if added under a new key (the hazard).
- No other test reads `first_battle`, the card bodies, or `docs/TUTORIAL_SCRIPT.md`'s table. Regenerating the doc table flips nothing.

### Series / harness risk

**Zero, structurally.** The fix is `.gd` + markdown. `tests/test_combat_sweep_metrics.py` contains no `tutorial` and no `.gd` reference; `tests/test_ai_intent_threat_migration.py`'s only `.gd` hit is a docstring line. The overlay arms only on `scenario_name == "tutorial"`, and `BASELINE_SERIES`/M1–M7 run on `europe_1805` / the legacy fixture. Even a change to `tutorial_1805.json` would not move them.

### Recommended build shape

Branch on the **one structured key the payload actually carries**, and make the false arm chip-less.

- `game_state.enemies` is on every response (measured). Boot: `{"Kienmayer": {"location": "Swabia", "strength": 0, "strength_band": "small force", "fog_level": "partial"}}`. After capture: `{"location": "Paris", "strength": 0, "nation": "Austria"}` — **no band, no fog_level**. After escape: `{"location": "Franche-Comte"/"Lorraine", …, "fog_level": "partial"}`.
- The card's own claim is *"still stands across the Rhine on allied Bavarian soil"*. That is exactly `enemies["Kienmayer"].location == "Swabia"`. Measured false in **8/8** seeds at T4. Use it directly — one key, no prose parsing, no PC-7-class string matching, and it is right in both the captured and the escaped arm.
- False arm: keep `first_battle` at gate 4 but render an honest body and **`suggest: ""`** (T-B1 filters empty suggests by construction, so nothing unpinned ships) — say the screen is broken and, when `fog_level` is present, that he has slipped the net. Do **not** name Jellacic.
- Regenerate `docs/TUTORIAL_SCRIPT.md:343-348` from STEPS (four stale rows).
- Build **FA-N78 first or in the same slice** — otherwise the branch never evaluates on the button route.

---

## FA-N78 — the School of War goes blind at its popup beats

### VERDICT: **REPRODUCED, and WIDER than filed** (two named handlers; six are blind; one route is the *only* route)

### What reproduces (numbers)

`gd_callgraph2.py` — strict call-only closure over `main.gd` (edge = `name(` not preceded by `.`, `.connect(`/`.bind(` excluded), 248 funcs, 6,504 lines:

```
DIRECT observe() callers: ['_on_command_result', '_on_interrupt_response']
main.gd:2654  in _on_command_result (2636-2838)
main.gd:5234  in _on_interrupt_response (5215-5285)
```

Handlers that answer a blocking question, by endpoint:

| endpoint | callback | observes? |
|---|---|---|
| `/command` (incl. typed answers) | `_on_command_result` | ✅ direct `:2654` |
| `/strategic_response` | `_on_interrupt_response` | ✅ direct `:5234` |
| `/marshal_petition_response` | `_on_marshal_petition_result` `:6202` | ✅ calls `_on_command_result` |
| `/respond_to_diplomatic_objection` | `_on_command_result` | ✅ callback is the observer |
| **`/respond_to_objection`** | **`_on_objection_response` `:4231`** (155 lines) | ❌ **BLIND** — tutorial card **V** |
| **`/capture_choice`** | **`_on_capture_choice_response` `:4686`** (47 lines) | ❌ **BLIND** — tutorial card **X** |
| `/respond_to_redemption` | `_on_redemption_response` `:4462` | ❌ BLIND (both the typed site `:1518` and the button site `:4459`) |
| `/respond_to_glorious_charge` | `_on_glorious_charge_response` `:5008` | ❌ BLIND (its response can carry a `battle_report`) |
| `/mailbox/respond` | `_on_mailbox_row_action_result` `:5794` | ❌ BLIND (deliberately isolated, documented in the body) |
| `/mailbox/activate` | `_on_mailbox_activate_result` `:5855` | ❌ BLIND |

Behavioural reproduction — `fan78_blind.py insist`, 3 seeds, typed arm vs button arm on identical seeds:

```
  WHERE                      | TYPED arm (observed)   | BUTTON arm (blind)
  after Ney,defend           | T2  objection_answer   | T2  objection_answer
  after the objection answer | T2  bombardment        | T2  objection_answer   <<< DIVERGES
  after bombard              | T2  first_battle       | T3  bombardment OVERDUE<<< DIVERGES
```
3/3 seeds identical. On the button route the card **stays on V** — *"He objects … Type `trust` … `insist` … `compromise`"* — after the player has already answered, and the guns card then arrives a turn late **already flagged OVERDUE** ("The war has outrun this page").

Capture half — `fan78_capture.py`, 3 seeds each arm:

```
ARM typed : card right after the capture answer -> T3 recruit_build
ARM button: card right after the capture answer -> T3 capture_answer   <<< still asking
```
3/3 seeds. Card **X** — *"now choose its fate. Type `plunder` … or `secure`"* — is still on screen after the province has been secured.

**Wider than filed, and this is the load-bearing correction: on the shipped client the blind route is the ONLY route at beat V.** `Ney, defend` returns `success: True, state: "awaiting_player_choice"` (measured 3/3), which matches `_response_has_objection_route` (`main.gd:2066`) in `_pre_hud_response_routes`; `_route_response_ui` returns true at `:2678` with `return  # Don't re-enable input`, so `set_input_enabled(false)` (set in `_execute_command`) stands and `command_input.editable == false` (`:4155`). `scenes/objection_dialog.tscn` has exactly `TrustButton` / `InsistButton` / `CompromiseButton` — **no close button, no ESC handler**. So the card tells the player to type three tokens they physically cannot type, and the only button that resolves it is on a handler the card cannot see. The row treats typed-vs-button as two routes; measurement says one.

### What is false / imprecise in the row

1. **Line numbers stale** — `main.gd:4010 / 4459 / 2468 / 5004 / 2492-2493 / 2514-2515` → real **4231 / 4686 / 2654 / 5234 / 2678-2679 / 2700-2701** (+186…+230).
2. **The title's "card VI"** is a numbering slip. The row's own body cites `tutorial_overlay.gd:139-142`, which is **`capture_answer` = card X**, not `bombardment` = card VI. (Both `:90-93` and `:139-142` are exact.) Measured, the second surface is card **X**, and what it does is *ask for the choice they just made*.
3. **"the only two observe sites"** — true, but "the two handlers that answer a blocking question" is **six**, of which two more (`redemption`, `glorious_charge`) are genuine blocking modals carrying `game_state` and, for the charge, `battle_report`.
4. `tutorial_overlay.gd:13`'s comment is not quite the lie the row implies: its first clause says "every backend response", its **second clause names the two sites**. The comment is self-disclosing; the code is the gap.

### What the filed fix would break

**The row's fix shape reds two existing pins.** `fan78_pin_flip.py` simulates both readings of *"`main.gd` gets a single `_school_observe(response)` helper … and the two handlers … call it — … join `_on_command_result` and `_on_interrupt_response`"*:

```
--- today (baseline)
   T-G2  count('tutorial_overlay.observe(') >= 2  -> 2 -> PASS
   T-G3  observe before route                     -> PASS
--- READING A: helper replaces BOTH existing call sites   <-- what the row prescribes
   T-G2  count('tutorial_overlay.observe(') >= 2  -> 1 -> FAIL
   T-G3  observe before route                     -> ERROR (ValueError: substring not found)
--- READING B: four literal `tutorial_overlay.observe(` sites
   T-G2  -> 4 -> PASS      T-G3 -> PASS
```
`tests/test_tutorial_position7.py:198` counts the literal string, and `:205-207` calls `.index()` on `_on_command_result`'s body — extracting the call into a helper makes the second **error**, not fail.

**The row's own prescribed test, built naively, is green about the defect.** The row asks for "the transitive closure of functions reaching `tutorial_overlay.observe(`". My first pass (`gd_callgraph.py`) built that closure over *name references*, including Callables handed to `connect()` — and it declared `_on_objection_response` and `_on_capture_choice_response` **REACHES-OBSERVE**, along with 80 other funcs including `_ready`. Only the strict call-only closure (`gd_callgraph2.py`, excluding `.connect(`/`.bind(`) reduces to 10 funcs and correctly marks both as BLIND. **The census must be call-only or the pin is inert by construction.**

**Things that are NOT hazards (measured, so the build need not defend them):**

- *Double-observe:* impossible. The typed answer is handled inside `/command` (`main.py:2685 _respond_to_objection_sync(_pending_answer_token)`) and returns on `_on_command_result`; the button answer returns on `/respond_to_objection`. **The routes are disjoint by endpoint** — no response is delivered to both handlers.
- *Payload shape:* the two routes' responses are **identical** (`fa42_latch_data.py`, same 40 top-level keys, same `battle_report`, same `events`, same `game_state`). observe() on the button route sees exactly what it already handles.
- *Raising a card over a modal:* the overlay is registered `modal=false` at **layer 90**; every modal is 101–119, so a modal always draws over the card. `_render()` only sets label text.
- *Cue over a modal:* `objection_dialog._on_trust_pressed()` calls `hide()` **before** `choice_made.emit()`, and `_on_capture_choice_made` likewise fires after the dialog closed — so `_advance_one()`'s `AudioManager.play("select")` lands with no modal up, exactly as on the typed route.
- *The stash discipline:* the overlay **does not stash**. There is nothing to raise. Do **not** copy the whole stash-first block into the two handlers — `_on_objection_response` already ends in `_show_pending_diorama()`, and `tests/test_pt_b_silent_losses.py::test_the_stash_exists_and_joins_the_other_three` pins the four stashes as **contiguous** at the head of `_on_command_result` (regex verified: still True under both readings, and would break if anything is inserted between them).

**Placement is load-bearing.** `_on_objection_response` has **five** early returns (defiance, disobey, redemption ×2, interrupt); `_on_capture_choice_response` early-returns into `_show_capture_choice_dialog` for the W6-8 estate stage. The call must sit at the **top** of each body, mirroring `_on_command_result`'s stash-first block — anywhere else and the blindest cases stay blind.

### Pins that flip

Baseline green today (measured):

- `test_tutorial_position7.py`, `test_popup_routing_registry.py`, `test_pt_b_silent_losses.py`, `test_godot_parse_harness.py`, `test_fa_slice6_the_popup_queue_2026_09_04.py` → **90 passed in 4.71s**
- `test_ui6_interaction_sweep.py`, `test_fa_slice3r_the_redirect_reads_the_answer_2026_09_04.py`, `test_igr_f_envoy_digest.py` → **173 passed in 2.67s**

Pins that touch the two handlers or `_on_command_result`, and their verdict under READING B:

| pin | verdict |
|---|---|
| `test_tutorial_position7.py:198` T-G2 (`count >= 2`) | PASS at 4 (FAILS at 1 under READING A) |
| `test_tutorial_position7.py:205` T-G3 (observe before route) | PASS (ERRORS under READING A) |
| `test_ui6_interaction_sweep.py:527` (`_on_objection_response` contains `_refresh_open_info_screens()`) | PASS — inserting at the top does not remove it |
| `test_fa_slice3r_…:543` (`_on_capture_choice_response` contains `_return_control_to_player()`) | PASS |
| `test_pt_b_silent_losses.py:171` (four contiguous stashes) | PASS — only breaks if the stash head is reordered |
| `test_popup_routing_registry.py:63,95` (`_on_command_result` delegates / no inline HUD) | PASS — unaffected |
| `test_godot_parse_harness.py` | PASS — file list unchanged |

### Series / harness risk

**Zero.** `.gd`-only; no backend module touched; the ambient 40-turn board never executes GDScript. `tests/test_combat_sweep_metrics.py` has no `.gd`/`tutorial` reference at all.

### Godot verification

`tools/godot_parse_check.gd` already covers `res://scripts/main.gd` (`:27`), `res://scripts/tutorial_overlay.gd` (`:82`) and `res://scenes/tutorial_overlay.tscn` (`:120`) — pinned by `test_g8_parse_harness_covers_the_new_files`. Run from repo root, expect EXIT=0:

```
Godot_v4.4.1-stable_win64.exe --headless --quit --path godot-client/project-sovereign --script ../../tools/godot_parse_check.gd
```
(the exe is nested: `Downloads\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64.exe`), then a boot smoke grepping `SCRIPT ERROR`.

### Recommended build shape

1. **Four literal call sites, not a helper** (READING B). Add, at the top of `_on_objection_response` (`:4231`) and `_on_capture_choice_response` (`:4686`), the same two lines `_on_command_result` uses at `:2653-2654`, with the `typeof(response) == TYPE_DICTIONARY` guard. Leave the two existing sites byte-identical so T-G2 and T-G3 stay binding.
2. **Take the other four while you are here** — `_on_redemption_response` (`:4462`), `_on_glorious_charge_response` (`:5008`), and decide-and-record the two mailbox handlers (`_on_mailbox_row_action_result` documents its own isolation from `_on_command_result`; observing there is still safe because observe() never routes). Redemption and the charge are not reachable in the 12-turn lesson (Ney is not cavalry; trust 75 does not fall to the redemption threshold), so they are defence in depth — say so on the row rather than claiming a player consequence.
3. **Replace T-G2 with a call-only census**, not a reference closure: parse `func` bodies from `main.gd`, build edges only for `name(` not preceded by `.` and not inside a `.connect(`/`.bind(` argument, and assert every handler in the endpoint table above reaches `tutorial_overlay.observe(`. Include a sensitivity check (delete one call → the census reds), or it repeats the inert-pin lesson.
4. **Fix card V's and card X's copy in the same edit.** They name typed tokens (`trust`/`insist`/`compromise`, `plunder`/`secure`) for modals whose buttons read *"Trust Marshal" / "Proceed as Ordered" / "Find Middle Ground"* and whose command line is disabled. Naming the buttons is a one-line change and closes the half of this row that observe() cannot.
5. **Sequence: FA-N78 before (or with) FA-42.** FA-42's branch latch evaluates only on responses the overlay sees, and under `trust` the deciding response arrives exclusively on `/respond_to_objection`.