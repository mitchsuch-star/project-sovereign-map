# REFUTING THE PREDICTOR CENSUS

Target: `…\scratchpad\cx_recon\predictor.md`, repo at `f7008582`.
Method: default REFUTED, re-derive every anchor at current line numbers, re-run
every simulation under the *shipped* semantics rather than the census's model.
My probes are `…\probes\r1_fog.py`, `r2_sim.py`, `r3_patience.py`,
`r4_addressee.py`, `r5b.py`, `r6_esc_fog_help.py`, `r7_ghost.py`. Read-only
throughout; nothing under `backend/`, `godot-client/`, `tests/`, `docs/` or
`tools/` was touched.

**Working-tree caveat, same as the census's:** `backend/ai/clause_guards.py`
carries 166 uncommitted lines (a sibling agent's "CX slice 1 — A QUESTION NEVER
ORDERS"). It changes WH-lead and `has`/`had` question detection only. Every
string I parsed is an imperative order with no WH-lead and no auxiliary, so
TP-7's re-derivation is unaffected; my escalation figure sits inside the
census's own stated 0.28pp bound.

---

## THE HEADLINE IS REFUTED

> *"prefix-filtering the up-arrow history that already ships saves 31.7% of
> keystrokes for ~30 lines and no new data"*

**31.7% is measured with an unbounded history.** The census's `p6_sim2.py` feeds
arm F a plain `hist` list, appended once per command, never trimmed — while its
arm B is measured at window 10/25/50 in a different file (`p5_sim.py`). The
17.6-point gap it attributes to *filtering* is mostly *memory*.

Re-run with `main.gd`'s real `_add_to_history` (consecutive-repeat dedupe at
:1043, front-trim to `MAX_HISTORY` at :1049), same corpus, same arithmetic
(`r2_sim.py`):

| window | B unfiltered walk | F prefix, oracle | F, "type the first word then reach up" | F, "type 3 then reach up" |
|---:|---:|---:|---:|---:|
| **10 (shipped)** | **14.8%** | **17.5%** | **8.3%** | **12.6%** |
| 25 | 16.3% | 24.7% | 11.0% | 16.8% |
| 50 | 16.3% | 29.9% | 14.5% | 21.4% |
| ∞ (the census's arm F) | 16.3% | **31.7%** | 16.2% | 23.3% |

At the constant that ships, **prefix-filtering buys 2.7 points** (14.8 → 17.5),
not 17.6. The remaining ~14 points are bought by lengthening the window — which
is the exact thing TP-3 tells the builder not to do. **TP-1 and TP-3 are
mutually inconsistent, and the report never runs the cell where they meet.**

"No new data source at all" therefore fails twice: the figure needs a window
≫ 10, and the census's own v1a asks for cross-session persistence via
`user://ui_settings.cfg` — which is new data, and which fights a discipline the
client already encodes (see MISSED:3).

And the corpus cannot carry the claim. 529 of 1,416 commands (**37.4%**) come
from three AP-burning driver loops that are near-copies of one another
(`commanded_full40` vs `volte_court_austria`: 51 of 52 distinct strings shared,
**98%**). `volte_court_austria` alone contains `Talleyrand, improve relations
with Austria` **36 times** — 1,512 of the 28,997 baseline characters from one
string — and is the single best script for arm F (60.7% at ∞). Drop the three
loops and F@∞ falls 31.7% → **22.0%**, F@10 → **17.0%**.

---

## FINDING-BY-FINDING

### REFUTE:TP-1 — REFUTED
See above. Anchors are all correct (`main.gd:348-350`, `MAX_HISTORY = 10` at
:350, `_history_previous` :1005, `_history_next` :1021, `_add_to_history`
:1037) — the *numbers* are the problem, not the citations. The honest statement
of the row is: *prefix-filtering the walk is worth ~3 points at the shipped
window and ~15 at an unbounded one; the lever is mostly the window.*

Not modelled at all: `_add_to_history` **drops a command equal to the previous
one** (:1043). The census's `hist.append(cmd)` stores it. On a corpus that is
86% exact repeats this systematically inflates the pool arm F walks.

### REFUTE:TP-2 — NARROWED (the facts hold; the argument does not, and the
recommendation escapes the guarantee)

The measured half reproduces **exactly** (`r1_fog.py`): `game_state.enemies` =
4 (`ArchdukeJohn`, `Brunswick`, `Deroy`, `Mack`); 10 of 14 living foreign
marshals absent, the same list; `get_visible_enemies` = 2; leak test
(map-payload names − wire enemies) = `[]`. I also ran the check the census did
not — advance six turns — and it still holds at turn 7. `parser.py:699`
`_extract_enemy_marshal_names` has no fog filter, called at :878; IQ9-X2 is at
`COMMAND_ROBUSTNESS_SPEC.md:413` verbatim.

Two problems.

**(a) The fog argument is not structural.** "The backend helper an endpoint
would reuse is omniscient" is a claim about what a hypothetical builder would
pick. `WorldState.get_filtered_game_state_summary` is a backend function, 194
lines, and it is **the producer of the very payload the census calls
fog-honest**. An endpoint reusing *it* is at least as natural as one reusing a
fuzzy-matching helper. The client-side verdict may be right (no new endpoint,
no round trip) — but not because the backend has no fog-honest source.

**(b) The guarantee does not cover the census's own top recommendation.** The
structural claim — *"a completer that draws only from `game_state` cannot name a
hidden enemy"* — is about the **template generator**. Arm F, the recommendation,
draws **100% from `command_history`**, which is gated by nothing. Measured
(`r6_esc_fog_help.py`): **67 of 1,416 played commands (4.7%) name a marshal
that is fogged on the 1805 boot board** — `ArchdukeCharles` 37×, `Kutuzov` 28×,
`Buxhowden` 2×. And `Ney, attack Archduke Charles` parses at 0.95 to
`target=ArchdukeCharles` (`r5b` follow-up), so it is not merely displayed, it
executes. v1a's cross-session persistence carries those names into a campaign
that never saw them. **Filed as MISSED:1.**

### REFUTE:TP-3 — REFUTED
"Window 50 saves 5.1% against window 10's 14.1%" is an artifact of
`p5_sim.ks_history`, which returns `i + 1` **uncapped**: at window 50 it charges
a simulated player 48 Up-presses to recall a 12-character command. No player
does that. `r3_patience.py` reproduces their model to the tenth (14.2% / 5.2%),
then caps the walk at `len(cmd)` — the floor any player who can stop pressing
achieves:

| window | census model (uncapped) | may-give-up model |
|---:|---:|---:|
| 10 | 14.2% | **14.8%** |
| 25 | 11.7% | 16.3% |
| 50 | **5.2%** | **16.3%** |
| ∞ | 3.1% | 16.3% |

**The ordering flips.** Raising `MAX_HISTORY` is neutral-to-mildly-positive, not
a 3× regression. This matters because TP-3 is the stated *reason* for "filter,
don't lengthen" — and TP-1's headline needs the length.

### REFUTE:TP-4 — NARROWED (right conclusion, wrong evidence)
The eventual-hit figure reproduces exactly (`r7_ghost.py`: the ghost is ever
right on 967 of 1,416 = **68.3%**), and arm G beating arm D (39.7% vs 29.6%) is
robust in my re-run. So *build a list, not a ghost* stands.

But "wrong 63.4% of the time at three characters" measures the ghost at 3 of a
**19-character median** line — 16% typed. Every completer ever written is wrong
there. Measured by fraction of the line typed:

| typed | right | wrong | no proposal |
|---:|---:|---:|---:|
| 10% | 22.7% | 70.8% | 6.6% |
| 30% | 29.7% | 59.3% | 10.9% |
| 50% | 37.2% | 47.5% | 15.3% |
| **75%** | **57.8%** | **18.7%** | 23.4% |

The ghost first becomes correct at a **median 50%** of the line. "Wrong two
times in three is visual noise on the one surface the player is concentrating
on" is a sentence built on a number that describes a moment nobody accepts at.

### REFUTE:TP-5 — NARROWED (materially — this is the cheapest win only on an
isolated candidate set)

63.9% reproduces exactly (905/1,416, `r4_addressee.py`). But **only 54.6%
address an own marshal**: 8.9 points of that 63.9 is `Talleyrand`, and one line
addresses `Mack`, an enemy the roster does not hold.

"Every own marshal is unique within 1–2 characters" is true **of the eight in
isolation** (I confirm: 2-char ambiguity = none). It is false at the surface a
completer presents. The real position-0 candidate set is own marshals +
advisors + the France bench + the 58 distinct non-marshal tokens the corpus
actually opens lines with:

- **1 char: 18 of 20 prefixes ambiguous.**
  `'s'` → Senarmont, Soult, Suchet, send, sponsor, **status**, surrender —
  and `status` is 14.1% of all first tokens, the second most common thing a
  player types, colliding with Soult at 6.8%.
  `'m'` → Marmont, Massena, Mortier, Murat, mack, make, march, marshal (8 ways).
- **2 chars: 12 buckets still ambiguous**, including `'se'` → Senarmont/send,
  `'su'` → Suchet/surrender, `'la'` → Lannes/land, `'be'` → Bernadotte/Berthier.
- 3 chars: still 6, including `'ber'`, `'lan'`, `'mar'`, `'sen'`.

Also: the France bench is **seven**, not six — `Senarmont` is in
`europe_1805.json`'s `marshal_pool` and never appears in the census (nor in
`CLAUDE.md`, which is stale here). He is addressed 4× in the played corpus, so
the bench genuinely reaches the addressee slot; and he is the name that makes
`'se'` collide with `send`.

### REFUTE:TP-6 — NARROWED (one wrong fact, and the proposed key is taken)
The `_on_command_input_gui_input` table (main.gd:908) is correct in order and
content; `_SCREEN_HOTKEYS` at :899; `_alt_game_key` at :939. `ctrl_pressed`
really is absent from the whole client, and `text_changed` really is connected
nowhere — both verified by census.

**"KEY_TAB ×2 (both Alt-gated)" is wrong.** `main.gd:1161` is a **bare** Tab in
`_unhandled_input`, gated on `not command_input.has_focus()`, toggling the
terminal. And `deploy/README_TESTER.txt:92` ships the line
*"Tab / Alt+\` — Collapse/restore the terminal"*.

So Tab is not free — it is the one key this project already had to split into
two forms because of focus (PC15-18 → FA-N56). Binding it to accept-completion
gives it a third meaning that depends on focus, in the teeth of the discipline
`tests/test_fa_slice13_shipping_2026_09_05.py::TestTheAdvertisedKeysAreReachableWhileTyping`
exists to enforce (and whose sibling
`test_the_terminal_toggle_does_not_advertise_alt_tab_alone` writes the rule
down: *"the README must say WHY, or the next reader restores Alt+Tab"*). Not a
red pin — a documented collision the census's own §1.3 table had the pieces for
and did not join.

The `Right`-arrow half survives: one site, `scenes/map_renderer_base.gd:2085`.
The `[input]` section of `project.godot` is empty, so Godot's default
`ui_focus_next` = Tab applies — which supports the census's UNVERIFIED guess
about `SendButton`, and makes the collision worse, not better.

### REFUTE:TP-7 — SURVIVES, strengthened — but the named chokepoint is wrong
I ran the **whole** generated set through the real `CommandParser` on the 1805
world via the repo's own `parser_eval` harness (`r5b.py`), not two samples:

- **306 of 306 templates parse at ≥ 0.7. Zero below the gate.**
- All 17 adjacent destinations parse verbatim at 0.95, `Franche-Comte` included.
- All 4 wire enemies: key form and display form give identical action+target.
- "Eight region keys carry a space or hyphen" is **exactly right**: East Anglia,
  East Frisia, East Prussia, Franche-Comte, Ile-de-France, La Mancha,
  New Russia, White Russia. Zero camelCase region keys.

Two corrections:

- **`Utils.humanize_entity_name` (utils.gd:284) is the wrong chokepoint for
  nations.** It camel-splits to `Kingdom Of Italy`; the game *prints*
  `Kingdom of Italy` via `PROSE_NATION_KEY_SUBSTITUTIONS` (utils.gd:271) /
  `display_names.py:70-71`. A builder following the row inserts a string the
  game never shows. Both parse at 0.95, so this is cosmetic — but "the existing
  chokepoint" names one of two, and the wrong one.
- §4.1's **"~74 in `VALID_ACTIONS`"** is **56** (measured).

### REFUTE:TP-8 — NARROWED (the inconsistency runs the other way)
Every anchor verified: `region_panel.gd:26` `signal region_command`,
`main.gd:6399` `_on_region_panel_command` → `api_client.send_command`,
`tutorial_overlay.gd:15-16` the FILL doctrine, `main.gd:6721` its handler,
`region_panel.gd:14-16` documenting send.

But **six** chip surfaces SEND — `_on_wizard_command_selected` (:6168),
`_on_wizard_structured_command_selected` (:6454), `_on_reward_command` (:6258),
`_on_vassal_command` (:6301), `_on_naval_command` (:6324),
`_on_region_panel_command` (:6405) — each carrying the same docstring idiom
*"same pipeline as a typed command"*. **One** FILLS: the tutorial, documented as
the teaching exception. "The project already owns the cheaper teaching idiom and
applies it inconsistently" inverts the majority; SEND is the established idiom
and FILL is the deliberate tutorial-only exception.

Named consequence of the flip the census recommends: `_on_region_panel_command`
→ `_on_region_panel_command_result` → `region_panel.refresh_if_open()` is the
in-place refresh UI-6 landed. A chip that FILLS never produces a result, so that
loop is orphaned and the panel goes stale under the click.

The census correctly flags this as a user ruling. Right call — on wrong grounds.

### REFUTE:TP-9 — REFUTED
`_execute_help` is at `meta_executor.py:629`; the literal is **11,633 chars /
217 lines** with zero `{` — all reproduced. And the conclusion drawn from it is
false.

`meta_executor.py:858-864` (IQ-4 S3g, *"the missions, spliced after the `war
terms` entry of the Cabinet block — **every figure the tick's own, read at call
time**"*) does:

```python
help_text = help_text.replace(
    _MISSIONS_HELP_ANCHOR,
    _MISSIONS_HELP_ANCHOR + _missions_help_block(_world), 1)
```

Measured: the block is **1,084 chars**, so the player receives ~**12,717**, not
11,633 — and it **moves with the world**. Set Talleyrand's skill 10 → 1 and the
printed rates go `+8 / +8 / +4` → `+5 / +5 / +3`.

The census's test — *"no `{` format placeholder anywhere in it"* — is
structurally incapable of seeing a `.replace()` splice. This is the repo's own
recurring lesson (a census must count the thing, not a string).

And **"there is no 'what can I say THIS turn' answer anywhere" is contradicted
by the census's own TP-8.** Five client surfaces already emit world-derived,
fog-honest, honest-availability typed commands: `region_panel.gd` (per-province
chips), `diplomacy_wizard.gd` (per-court gate rows), `marshal_management.gd`
(per-marshal order chips), `strategic_ledger.gd` (Admiralty/orders),
`tutorial_overlay.gd` (suggest chips). The row's *ambition* may still be worth
something; its three stated pieces of evidence are wrong.

### REFUTE:TP-10 — NARROWED
Re-derived independently through `CommandParser` on the 1805 world
(`r6_esc_fog_help.py`): **62 of 1,416 instances = 4.4%**, **47 of 374 distinct =
12.6%**, against the census's 4.1% / 11.5%. `LLM_FALLBACK_CONFIDENCE_THRESHOLD =
0.7` at `llm_client.py:63`. Magnitude confirmed.

Two narrowings:

- **The denominator is driver scripts that had to parse in order to run.** On
  the repo's own curated corpus, **41 of 388** mock-runnable 1805/any entries
  (**10.6%**) sit below the gate — 2.4× the census's instance rate.
- **"Mostly from the `weird_*` probe scripts" understates it.** The 19 committed
  IQ-9 cassettes exist *because* they escalate, and they are ordinary speech,
  not absurdism: *"Ney, get after Mack"*, *"Davout, keep an eye on Mack"*,
  *"Lannes, make your way to Swabia"*, *"Ney, cover the retreat"*, *"Ney, fix
  bayonets"*, *"Murat, harass the Austrians"*, *"ask Austria what they want"*.
  Those are what a person types on turn one. The row's own conclusion — that a
  predictor narrows what players try — lands harder than it argues.

### REFUTE:TP-11 — REFUTED on mechanism
Scene anchors all correct (`main.tscn:24` BottomLeftUI PanelContainer at the
root, `:42` MainLayout, `:219` OutputScroll, `:234` InputSection, `:238`
CommandInput; `_apply_ui_scale` at main.gd:1351).

Two errors:

- **`content_scale_factor` is a Window property** — `_apply_ui_scale` does
  `win.content_scale_factor = clamped`. CanvasLayers live in the same viewport
  and scale with it. The distinction the row draws between "a Control in the
  VBox inherits it automatically" and "a CanvasLayer would not" does not exist.
  `content_scale_factor` is what *causes* the 2.0 break (an 800×450 logical
  viewport), not what avoids it.
- **"avoided by construction" is false.** `BottomLeftUI` is a PanelContainer
  that, in main.gd's own words at `_position_resize_grip`, *"clamps up to its
  combined minimum size (header + output + input row), and A+ text scale
  enlarges that min — the grip must follow the real top-right corner… or it
  strands mid-panel."* Meanwhile `_relayout_terminal` clamps the height to
  `size.y − 20 − TOP_BAR_RESERVED_PX`. Adding five suggestion rows to MainLayout
  raises that minimum against a 450px budget at scale 2.0. The failure mode the
  row says is dodged is the one the file already has a workaround comment for —
  and IQ-10's own X1 records the top bar at **x = −26** at 2.0.

The conclusion (put it in the terminal's VBox so it reflows with the panel) is
defensible. Every reason given for it is wrong.

### REFUTE:TP-12 — SURVIVES, bounded
All eight call sites verified byte-exactly (`main.gd:1474, 1564, 6168, 6258,
6301, 6324, 6405, 6454`; definition :1037). Two bounds the row omits and that
change what "for free" is worth:

- `_add_to_history` **drops a consecutive repeat** (:1043) and trims to 10
  (:1049). A 4-AP turn plus `end turn` is 5 entries, so the shipped window holds
  about **two turns** of traffic. Chip learning is evicted almost immediately.
- `_reset_frontend_state_for_world_swap` (`main.gd:4961`) **clears
  `command_history` on every load and new game** (:5021), beside the WO-40
  stash-clearing block. See MISSED:3.

---

## WHAT THE CENSUS MISSED

### MISSED:1 — history is not fog-filtered, and arm F *is* the history
Already argued under TP-2. The structural fog guarantee is proved about the
template generator and then asserted about the whole candidate set. Measured:
**67 of 1,416 played commands (4.7%) name a boot-fogged marshal**
(`ArchdukeCharles` 37×, `Kutuzov` 28×, `Buxhowden` 2×), and
`Ney, attack Archduke Charles` parses at 0.95 to the fogged key. The
recommendation to persist history across sessions makes it cross-campaign. The
§6 test the row proposes — *"the template generator draws only from keys the
filtered summary emits"* — is an AST census over the generator and would stay
green while the history arm proposed `Kutuzov` on turn 1.

### MISSED:2 — a serialized, 50-entry, fog-free command history already exists on the backend, and it is already in the LLM prompt
The census's §1.2 says the history is *"per-session only — an in-memory Array,
never written to `user://`"*. That is true of the **client** array and it looked
no further.

- `WorldState.command_history` — `world_state.py:1334`, **serialized** at
  `to_dict` :7436 and `from_dict` :8083, capped at **50** (`add_to_command_history`
  :9614, trim :9633).
- Written live at `main.py:3042` and `context_carryover.py:566`; it is CR-4's
  whole substrate (`context_carryover.py:221`).
- **Already fed to the LLM**: `get_command_history_for_prompt()` :9640 returns
  the last 5, consumed at `providers.py:619` and `:955`, rendered at
  `prompt_builder.py:598`.

This is the player's own words, so it is fog-free by construction and needs no
`/completions` endpoint and no new fog surface — it rides the response envelope.
It is **5× the client's window**, survives save/load and world swap correctly
(per world, not per user), and is the thing v1a proposes to build badly in
`ui_settings.cfg`. §3.2 rejects "the backend door" without ever finding the door
that is already open.

It also bears on the user's other question: the LLM is *already* being handed
the last five commands, so "is routing to the LLM worth it" has a live
context-carryover half the census's §7 does not mention.

### MISSED:3 — the client clears `command_history` on world swap **by design**, and v1a fights it
`_reset_frontend_state_for_world_swap` (`main.gd:4961`) clears the array at
:5021-5023, sitting in the block whose own comment records WO-40: *"a PREVIOUS
campaign's stashed popup survived a load and raised at the next control return
in the new world."* Persisting `command_history` to `user://ui_settings.cfg`
re-creates exactly that class of leak, on a surface the player reads, and
carries a dead campaign's marshal names (MISSED:1) into a live one. If the row
still wants persistence, the correct home is the backend store in MISSED:2,
which is already scoped per world.

`ui_settings.gd`'s own header states the constraint the census cites as
precedent and reads past: *"Display-only (Golden Rule 6): nothing here touches
game state or serialization."* A command history is not a display preference.

### MISSED:4 — the census read the driver's INPUT files, not the game's committed RECORD, and the gap is 22% of all commands
`tools/playtest_scripts/*.json` are the scripts an author hands the driver. The
game's own record is `docs/audits/playtest_digests/*/digest.jsonl` — **16
archives, 2,906 `kind: "command"` records**, and **89 of the 91 archive
directories carry the IQ-8 `meta.json`** (`seed`, `rng`, `llm`, `policy`,
`transport`, `from_save`, `unknown_blockers`) that IQ-8 landed precisely so a
published figure is citable. The census never opened one.

The difference is not cosmetic:

| | census corpus (scripts) | game's record (archives) |
|---|---:|---:|
| commands | 1,416 | 2,906 |
| **`end turn`** | **0 (0.0%)** | **640 (22.0%)** |
| `status` | 200 (14.1%) | 252 (8.7%) |
| mean chars | 20.5 | **14.9** |

**`end turn` is the single most common command in the game and is completely
absent from the corpus the keystroke tables are built on** — because the driver
issues it itself. It is 8 characters, and it is *already* one keypress (`Alt+E`,
`main.gd:952`) or a button. So roughly a fifth of real command traffic is not a
keystroke problem at all, and the baseline the percentages divide by
(28,997 chars, mean 20.5) is drawn from the sub-population where typing is
hardest. Every "% saved" in the report is a percentage of the wrong denominator.

### MISSED:5 — `text_changed` never fires while a command is in flight
A completer on `text_changed` must live with `set_input_enabled(false)`
(`main.gd`, `command_input.editable = enabled`), which every chip pipeline and
every submit calls, plus the `_chip_command_in_flight` latch that UI-6's review
landed. The census's §4.3 mechanics section covers Tab/Up/Down/Esc and says
nothing about the latch — and the one surface that already fills the line
(`_on_tutorial_suggest_command`, :6721) checks **both** `_chip_command_in_flight`
and `command_input.editable` before touching it. That guard is the pattern a
suggestion row has to copy, and it is unnamed.

### MISSED:6 — arm G's headline is robust; the report's own hedge is not needed
Worth recording *for* the census, since I set out to kill it. I attacked arm G
on the suspicion that its 39.7% comes from a list open at zero characters, which
`text_changed` cannot deliver. It does not: requiring ≥1 char costs 0.1 points
(39.7 → 39.6), ≥2 costs 1.9, ≥3 costs 4.5. Arm G survives its own design
constraint. Given TP-1 collapses to 17.5% at the shipped window and TP-3
reverses, **the ranked list is not the third-best option measured — on my
numbers it is the first**, and the report's ordering is an artifact of the two
model errors above.

---

## WHAT I WOULD TELL THE BUILDER

1. The ranked list (arm G) is the recommendation, not the fallback. Its number
   holds up under attack; arm F's does not.
2. If history is used at all, filter it **and** enlarge it — TP-3's reason for
   not enlarging it does not survive a player who can stop pressing Up — and
   take the window from `world.command_history` (50, serialized, fog-free,
   already on the backend), never from `ui_settings.cfg`.
3. Fog-gate the **history** arm, not just the template arm. 4.7% of played
   commands name a marshal the current board fogs.
4. Do not take Tab. It is advertised in `README_TESTER.txt:92` and is the one
   key this project already split over focus.
5. The test the row proposes (every template parses ≥ 0.7) is a good test and I
   confirm it passes today, 306/306. Add the mirror it is missing: **no
   candidate, from any source, names an entity absent from the filtered
   summary.**
