All measurements done. Report follows.

---

# REFUTATION — FA-42 / FA-N78

Probes under `…/scratchpad/s14/refute_F_tutorial/`: `p1_callgraph.py`, `p2_loose.py`, `p3_path.py`, `p4_matrix.py`, `p5_behav.py`, `p6_seed1.py`, `p7_trials.py`, `p8_n78.py`, `p9_tb1.py`, `p10_escape.py`, `p11_fog.py`. All read HEAD copies (`git show HEAD:…`), not the working tree — see finding 0.

---

## 0. ⚠ The tree is NOT clean, and it moves the reporter's line numbers again

**CLAIM (task framing, and implicitly the report):** HEAD 9ef38da8, clean.

**MY MEASUREMENT:** `git status --porcelain` → **29 modified paths**, including `godot-client/project-sovereign/scripts/main.gd` (+24 lines) and two untracked files (`tests/test_fa_slice14_the_rulings_and_the_singles_2026_09_05.py`). The diff is **FA-R4** (`_strip_desk_address`, inserted at ~line 1400) — unrelated to either row, but it shifts everything below it.

| symbol | report / HEAD | working tree |
|---|---|---|
| `tutorial_overlay.observe(` #1 | 2654 | **2678** |
| `tutorial_overlay.observe(` #2 | 5234 | **5258** |

**VERDICT: the report's `main.gd` numbers are CONFIRMED at HEAD and already STALE (+24) in the tree the builder will edit.** Navigate by symbol. `tutorial_overlay.gd` is unmodified, so all its numbers hold.

---

## FA-42

### 1. "8 seeds" — the arm is not seed-determinised
**CLAIM:** per-seed results (captures on seeds 0/2/4/5, escapes on 6/7, etc.), reported as facts about seeds.

**MY MEASUREMENT (`p5_behav.py`, `SOVEREIGN_SEED=1`, three consecutive runs):**
```
run 1  Kienmayer alive@Franche-Comte 1352   chip refused: "No intelligence…"
run 2  Kienmayer captured@Paris             chip refused: "…our prisoner at Paris…"
run 3  Kienmayer alive@Franche-Comte 415    chip refused: "No intelligence…"
```
**VERDICT: REFUTED (methodology).** `SOVEREIGN_SEED` does not pin this arm's combat RNG. Every "N/8" in the report is a **sample of a stochastic process**, not a seed-indexed fact, and no builder can reproduce "seed N → outcome X". I re-ran everything as repeated trials at a *fixed* seed instead.

### 2. "captures on T2 (4/8) … escapes into Franche-Comte (4/8)"
**MY MEASUREMENT (`p7_trials.py`, 24 trials, seed held at 0):**
```
alive@Franche-Comte  15/24   (62.5%)
captured@Paris        8/24   (33.3%)
ABSENT from world.marshals  1/24
```
**VERDICT: NARROWED.** Escape is the **modal** outcome at nearly 2:1, not a 50/50, and there is a **third fate** (gone from `world.marshals` entirely, `fallen_marshals` empty) the report never saw. The report's "the escape arm is the worse half" is right and *under*-sold.

### 3. ⛔ "clicked on T4 and T5 → refused, **16/16 clicks**"
**MY MEASUREMENT (`p7_trials.py`, 24 clicks at T4):**
```
14/24  refused: no intel
 8/24  refused: prisoner
 1/24  SUCCESS -> "Ney pursues Kienmayer (at Lorraine). Moves to Swab…"
 1/24  SUCCESS -> "…named no foe our maps know — Ney marches on Jellacic at Tyrol, the nearest in sight"
```
**VERDICT: REFUTED.** The chip is **not always dead** — it succeeds ~8% of the time, in two different ways, and one of them is a **wrong-enemy substitution** (the WO-13 / CR-4 family). This matters for the build twice over:

- The report's recommended false arm (`suggest: ""`, "say the screen is broken") would **delete a chip that works**, in the one state where the lesson's own beat is live.
- The report's branch `enemies["Kienmayer"].location == "Swabia"` is FALSE in the working `at Lorraine` case too, so it collapses a live state into the dead arm. The honest predicate is **three-valued**: (a) at Swabia — card correct; (b) elsewhere but reachable — chip works, prose wrong; (c) prisoner/gone/unreachable — chip dead. The project already has an idiom for (b) vs (c): **honest-availability gate terms** (region-panel chips, `/formables` `gate_terms`, the naval Orders view). The report never mentions it.

### 4. "sits on that page until turn 6, 8/8"
**MY MEASUREMENT (`p5_behav.py` 8-run sweep):** released at **T6 on 6/8**; on the two runs where the chip succeeded, `_pred_battle_happened` fired and the card released at **T4**.
**VERDICT: NARROWED** — a consequence of finding 3.

### 5. "invisible to French intelligence"
**MY MEASUREMENT (`p11_fog.py`, 6/6 trials, escaped arm at T4):**
```
TRUTH                       ('Lorraine', 972)
payload enemies['Kienmayer'] {"location":"Lorraine","strength":0,"nation":"Austria",
                              "strength_band":"screening force","fog_level":"partial"}
in get_visible_enemies('France')?  True
executor says: "No intelligence on Kienmayer's position, Sire."
```
**VERDICT: REFUTED.** He is **visible at PARTIAL**, he is in `get_visible_enemies("France")`, and his true province is in the payload. The refusal is a PURSUE-specific gate, not blindness.

**And this is a hazard in the recommended fix.** The report's chosen key exposes a PARTIAL-fog province and a fog-masked `strength: 0` (truth 932–1477). Their `== "Swabia"` test is fog-safe *by luck* (it only suppresses), but their own recommended copy — *"when `fog_level` is present, that he has slipped the net"* — is one step from rendering a location the executor refuses to act on. **A builder must not print `location` or `strength` from that entry.**

### 6. "by T7 … reinforced to 4,137 / 6,633 / 6,972 / 6,972"
**MY MEASUREMENT (`p10_escape.py`, 12 trials):** T7 strengths **1,151 · 2,957 · 3,465 · 3,633 · 3,633 · 3,633 · 4,230**.
**VERDICT: NARROWED** — over-stated by ~1.7× at the top.

### 7. "`Ney, attack Jellacic` returned True in 6/6 **only because** Ney had drifted to Munich — on any slower player Ney is at Rhineland or Swabia"
**MY MEASUREMENT (`p10_escape.py`, 12 trials):** Ney at **Munich 12/12**; the chip **SUCCESS with a muster modal 12/12**.
**VERDICT: NARROWED.** Within the trust arm, Munich is not a drift — it is deterministic, so the alternative chip is far more robust than credited. The report's caveat is **unmeasured** and its stated cause ("a slower player") is wrong; the real caveat is the **insist/compromise** arms — which is Berthier's own advice on card V (*"I advise INSIST"*) and which the report never tests. The muster-modal half is CONFIRMED 12/12.

### 8. Claims that reproduce exactly (CONFIRMED)
- **Battle on the trust-answer response: 24/24** (report said 8/8).
- **Adjacency**: `Rhineland = [Brabant, Frankfurt, Gelderland, Lorraine, Nassau, Swabia]`, `Swabia = [Franche-Comte, Franconia, Lorraine, Munich, Nassau, Rhineland]`; only `Munich` touches Tyrol. Exact.
- **Lorraine Austrian at T4: 6/12** (report 4/8). Swabia's controller is `Bavaria`, so the card's "allied Bavarian soil" is right *at boot only*.
- **`_pred_battle_happened` (`tutorial_overlay.gd:513`) accepts any `battle_report` or any `battle`/`conquest` event and names no marshal** → the row's `fix_shape` is a no-op. Confirmed by reading.
- **The filed latch would fire on both outcomes**: captured-arm `events[0]` is `type=battle, outcome=attacker_tactical_victory, enemy_destroyed=False, defender=Kienmayer` — no capture event in the response at all.
- **Four stale doc rows** at `docs/TUTORIAL_SCRIPT.md:344-348` (blood T3 vs gate 4; guns T4 vs gate 2; inverted order; `Ney, attack Jellacic`/`Ney, move to Tyrol` vs STEPS' `Davout, move to Bohemia`). Exact.
- **`tutorial_overlay.gd` line numbers** `:90 :99 :112 :139 :297 :313 :346 :365 :386 :513`. All exact.
- **Series/harness risk zero**: `test_combat_sweep_metrics.py` = 0 hits for `tutorial`/`.gd`; `test_ai_intent_threat_migration.py`'s single `.gd` hit is a docstring (line 9).

### 9. T-B1 — CONFIRMED but the conclusion is wrong
**CLAIM:** a branch chip under a new key "ships unpinned"; the report therefore recommends `suggest: ""`.

**MY MEASUREMENT (`p9_tb1.py`, and `pytest … -q` → **78 passed**, matching their baseline exactly):**

| build shape | suggests | pairs | alt chip pinned? |
|---|---|---|---|
| baseline | 15 | 11 | — (dead chip **IS** in the pinned set) |
| `"suggest_alt"` / `"suggest_action_alt"` | 15 | 11 | **No** |
| **nested dict reusing `"suggest"`/`"suggest_action"`** | 16 | 12 | **Yes** |
| false arm `"suggest": ""` | 15 | 10 | `>= 10` guard still met |

**VERDICT: NARROWED.** The regex hazard is real for a *new key name*, but **a nested dict that reuses the same key names is pinned for free, with zero change to T-B1**. That shape strictly dominates the report's recommendation on the pinning axis and keeps a working chip alive.

**And a bigger point the report misses: T-B1 is green *today* about the very chip FA-42 says is dead.** `("Ney, attack Kienmayer", "attack")` is in the pinned set and the test passes — because T-B1 asserts **parseability**, not board legality. No pin in the repo can see FA-42's defect class.

`STEPS.size() == 15` (badge "N of 15") and `_derive_step_for_turn(4) → index 6 = first_battle` — the two-gate-4-entries hazard is CONFIRMED.

---

## FA-N78

### 10. The call graph — CONFIRMED exactly, by an independent implementation
`p1_callgraph.py` (my own parser, different edge rule): **248 funcs, 6,504 lines**; direct holders `['_on_command_result' @2654, '_on_interrupt_response' @5234]`; closure size **10**.

| handler | line (HEAD) | reaches observe |
|---|---|---|
| `_on_command_result` | 2636 | DIRECT |
| `_on_interrupt_response` | 5215 | DIRECT |
| `_on_marshal_petition_result` | 6202 | via `_on_command_result` |
| `_on_objection_response` | **4231** | **NO** |
| `_on_capture_choice_response` | **4686** | **NO** |
| `_on_redemption_response` | 4462 | NO |
| `_on_glorious_charge_response` | 5008 | NO |
| `_on_mailbox_row_action_result` | 5794 | NO |
| `_on_mailbox_activate_result` | 5855 | NO |

**VERDICT: CONFIRMED**, every line number and every verdict.

### 11. The behavioural divergence — CONFIRMED, but "goes blind" is over-stated
**MY MEASUREMENT (`p8_n78.py`, 3 trials per arm):**
```
typed  3/3: card before=objection_answer  after answer=bombardment      -> T3 bombardment
button 3/3: card before=objection_answer  after answer=objection_answer -> T3 bombardment
```
**VERDICT: CONFIRMED for the defect, NARROWED for the severity.** The card is stuck on V (*"He objects — type trust/insist/compromise"*) for the **remainder of the turn** after the player has answered — but it **self-heals on the next `/command` response**, and *not* by the catch-up the report credits: at T3, `_maybe_catch_up`'s `_turn > gate + 1` is `3 > 3` = false. It recovers because **`_pred_objection_resolved` reads the latch `_saw_objection`**, which stays true. So the damage is "one beat stale + the next card arrives flagged OVERDUE", not "the School goes blind".

### 12. ⛔ The census hazard — the stated cause is REFUTED and both prescribed guards are INERT
**CLAIM:** "my first pass … including Callables handed to `connect()` … declared both handlers REACHES-OBSERVE. Only the strict call-only closure (excluding `.connect(`/`.bind(`) reduces to 10." → prescribed guard: *"edges only for `name(` not preceded by `.` and not inside a `.connect(`/`.bind(` argument."*

**MY MEASUREMENT (`p4_matrix.py`, all 16 guard combinations):**

| call-syntax | dot-excl | strip-`#` | connect-excl | closure | correct? |
|---|---|---|---|---|---|
| **True** | any | any | any | **10** (all 8 rows) | YES |
| False | any | True | any | 44 | YES |
| False | any | **False** | any | **85** | **NO (inert)** |

And `p3_path.py` names the actual bridging edge:
```
_on_objection_response -> _display_result -> _display_battle_result -> _on_command_result
   _display_battle_result line 3065:  "# _on_command_result. A real attack frequently resolves through a"
```
`_on_objection_response` contains **no `connect(`, no `.bind(`, and never mentions `_on_command_result` at all**.

**VERDICT: REFUTED.** The false positive came from an **unstripped comment**, not from a `connect()` Callable. Measured consequences for the builder:
- **`.connect(`/`.bind(` exclusion: completely inert** — closure is 10 with it and 10 without it, in every combination.
- **Dot-exclusion: also inert** here — 10 either way, 44 either way.
- The only load-bearing guard is **use call-syntax (`name(`)**, which alone gives the right answer in all 8 of its rows. If a builder writes a reference-based census instead, **strip comments**.

The report's *conclusion* ("must be call-only") survives; its *reason* and its two named guards do not.

### 13. Pins — CONFIRMED
- `tests/test_tutorial_position7.py:198` T-G2 = `assert gd.count("tutorial_overlay.observe(") >= 2` — literal count.
- `:205` T-G3 = `body.index("tutorial_overlay.observe(") < body.index("_route_response_ui(")` — `.index()` **raises `ValueError`**, so READING A (a helper replacing both sites) **errors**, it does not fail. CONFIRMED.
- Baseline `pytest tests/test_tutorial_position7.py tests/test_tutorial_scenario.py tests/test_tutorial_school_fixes_2026_08_08.py tests/test_hc5_tutorial_names_fleet.py` → **78 passed in 3.65s**. Exact.

### 14. "The typed route is unreachable" — CONFIRMED
`_execute_command` calls `set_input_enabled(false)` (HEAD `:1537`) → `_route_response_ui(response, _pre_hud_response_routes)` matches `_response_has_objection_route` (`:2066`) and `return  # Don't re-enable input` (`:2678`) → `set_input_enabled` (`:4153`) sets `command_input.editable = enabled`. `scenes/objection_dialog.tscn` node list is exactly `TrustButton` / `InsistButton` / `CompromiseButton`; `scripts/objection_dialog.gd` has **no `_input`/`_unhandled_input`/`ui_cancel`** — only the three handlers, each calling `hide()` **before** `choice_made.emit()`. CONFIRMED, including the `hide()`-before-`emit()` cue argument.

### 15. "Routes disjoint by endpoint, no double-observe" — CONFIRMED
Typed answers go through `/command` → `main.py:2685 _respond_to_objection_sync(_pending_answer_token)`; button answers through `POST /respond_to_objection` (`main.py:3668`) → the *same* `_respond_to_objection_sync` (`:3697`). Different client callbacks; no response reaches both.

---

## What the reporter MISSED that a builder must know

1. **The latch asymmetry decides which blind handlers actually matter.** `_pred_objection_resolved` and `_pred_capture_resolved` read latches (`_saw_objection`, `_saw_capture`), so the two *named* beats self-heal on the next `/command`. **`_pred_battle_happened` and `_pred_bombardment` have no latch** — they read only the response in hand. So a battle delivered on a blind handler is **lost forever**, releasing card VII only at the gate+2 catch-up. `_on_glorious_charge_response` renders `battle_report` and a battle event (HEAD ~5092/5097). It is therefore **not "defence in depth"** — it is the one blind handler that can permanently desync a card. Rank it above the mailbox pair.

2. **T-B1 cannot see FA-42's defect class at all** — it pins parse success, not legality, and `("Ney, attack Kienmayer","attack")` passes it today. Any new pin must drive the **executor**, not the parser.

3. **A nested dict reusing `"suggest"`/`"suggest_action"` is pinned by T-B1 for free** (measured 16/16, alt chip pinned). Prefer it to a new key name *or* to an empty false-arm chip.

4. **The chip is live ~8% of the time**, in two modes, one of them a wrong-enemy substitution. A binary `location == "Swabia"` branch suppresses a working chip; use a three-valued honest-availability gate.

5. **`enemies[…]` is fog-masked** — `strength: 0` against a truth of 932–1,477, and `fog_level: "partial"` on a location the executor refuses to pursue. Read it for a negative test only; never render `location` or `strength` from it.

6. **Nothing in this arm is seed-reproducible.** Any acceptance test must assert over repeated trials or over a state the tutor can *read*, never over "seed N gives outcome X".

7. **The working tree is dirty and `main.gd` is +24.** Re-derive every `main.gd` line number before editing.