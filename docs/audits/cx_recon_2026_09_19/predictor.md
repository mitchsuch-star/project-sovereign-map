# THE TEXT PREDICTOR — read-only recon + design

Repo `C:\Users\User\PycharmProjects\project-sovereign-map` at `f7008582`. No file
under `backend/`, `godot-client/`, `tests/`, `docs/` or `tools/` was modified.
Probes live in `…\scratchpad\cx_recon\probes\p1..p8*.py` and every number below
is their output or a `file:line`.

---

## 0. HEADLINE

**A predictor is the third-best thing this row could build, and the best one is
already half-built.**

Measured over 1,416 real played commands (§2), against the keystrokes a player
actually presses:

| arm | keystrokes | % saved | hit rate | new data needed |
|---|---:|---:|---:|---|
| A type it out (today) | 28,997 | — | — | — |
| B up-arrow history, window 10 (**ships today**) | 24,907 | 14.1% | 19.2% | none |
| **F prefix-filtered history** | **19,792** | **31.7%** | 47.5% | **none** |
| D single ghost line (history+templates) | 20,402 | 29.6% | 68.3% | template generator |
| **G ranked top-5 list (history+templates)** | **17,482** | **39.7%** | **68.3%** | template generator |
| E every command by chip (reference ceiling) | 1,416 | 95.1% | 100% | n/a |

Three findings decide the design:

1. **`MAX_HISTORY` must NOT simply be raised.** `main.gd:350` caps history at 10.
   My first instinct was "raise it to 50" — 46.0% of commands repeat something
   within the last 50 (probe 2b). **Measured, that makes the feature worse:**
   window 10 saves 14.1%, window 50 saves **5.1%**, because each Up press costs
   a keystroke and walking 40 entries costs more than typing 20 characters. The
   fix is *filtering* the walk, not lengthening it.
2. **A single ghost line is wrong more often than right.** After 3 characters the
   top-ranked proposal is the intended command 29.1% of the time and something
   else **63.4%** of the time (probe 6). Ghost text that is wrong two times in
   three is visual noise on the one surface the player is concentrating on. The
   shape that works here is a short ranked list, not inline ghost text.
3. **The completer must be client-side, and the fog argument is not close.**
   The client already holds exactly the right set; the backend helper a
   `/completions` endpoint would naturally reuse is omniscient (§3).

---

## 1. WHAT IS THERE TODAY

### 1.1 The command line

| thing | where |
|---|---|
| `LineEdit` node | `scenes/main.tscn:238` `BottomLeftUI/MainMargin/MainLayout/InputSection/CommandInput` — `placeholder_text = "Type command..."`, font size 12, **no `focus_next`, no custom focus mode** |
| `@onready var command_input` | `scripts/main.gd:151` |
| `text_submitted` → `_on_command_submitted` | `main.gd:631-632` |
| `gui_input` → `_on_command_input_gui_input` | `main.gd:643-644`, body at `main.gd:908` |
| **`text_changed` is connected nowhere** | census over `scripts/*.gd` returns empty — the signal a completer needs is free |
| command dispatch | `_execute_command` `main.gd:1528` |

### 1.2 Completion / history that already exists

- **Up/Down arrow history recall exists.** `_history_previous` `main.gd:1005`,
  `_history_next` `main.gd:1021`, `_add_to_history` `main.gd:1037`; state at
  `main.gd:348-350` (`command_history: Array`, `history_index`, `MAX_HISTORY = 10`).
  Per-session only — an in-memory Array, never written to `user://`.
- **No autocompletion of any kind.** A grep for `autocomplet|completion|ghost_text`
  across `scripts/*.gd` + `scenes/*.gd` returns only unrelated hits
  (`proposal_confirm_popup.gd`'s settlement *suggestions*, `strategic_report_popup.gd`'s
  "completions" in a docstring). There is nothing to extend; this is greenfield.
- **`_add_to_history` is called from 8 sites** (`main.gd:1474, 1564, 6168, 6258,
  6301, 6324, 6405, 6454`) — the typed route *and every chip pipeline*. So any
  history-based completer learns from chip clicks for free. This is load-bearing
  for the recommendation in §6.

### 1.3 Key census — what the terminal swallows while focused

`_on_command_input_gui_input` (`main.gd:908`) intercepts, in order:

| key | effect |
|---|---|
| `F1` | diplomacy wizard |
| `Alt+L/T/G/D/R/N` | screens (`_SCREEN_HOTKEYS`, `main.gd:901`) |
| `Alt+E/Tab/\`/M/Home/=/-` | game keys (`_alt_game_key`, `main.gd:939`) |
| **`Up` / `Down`** | history prev/next |
| `Esc` | release focus |

Everything else falls through to the `LineEdit`. While the input is **not**
focused, `_unhandled_input` (`main.gd:1059`) additionally binds bare
`L/T/G/D/R/N/E/Tab/Esc/F1`, gated by `_is_hotkey_blocked()` (`main.gd:5793`),
which is literally `command_input.has_focus() or _is_modal_dialog_open()` — i.e.
**every bare letter hotkey is blocked while typing, by design**, which is why the
`Alt+` forms exist (PC15-18, FA-N56).

**Free to bind while typing** (keycode census over the whole client returns no
other use):

- **`Tab` (bare)** — only `Alt+Tab`/`Alt+\`` are bound (`main.gd:963`). Bare Tab
  while focused currently falls through to Godot's focus navigation and moves
  focus to `SendButton`. *UNVERIFIED by execution* — I did not run the engine;
  this is read off `main.tscn` (no `focus_next` override, `SendButton` at
  `main.tscn:244` is a default-focusable Button) plus Godot's `gui_input`-before-
  focus-navigation order. The Godot binary is present at
  `C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64.exe`
  if the build wants to confirm it first — it should.
- **`Right` arrow** — bound only in `scenes/map_renderer_base.gd:2085`, never in
  the input path. At end-of-line `Right` is a no-op inside a `LineEdit`, which
  makes it the zero-cost "accept" key (the fish/zsh idiom).
- `Ctrl+anything` — `ctrl_pressed` appears nowhere in `scripts/*.gd`.
- `Shift+Tab`, `Ctrl+Space`, `PageUp/PageDown`.

`Enter` is taken (`text_submitted`). `Up`/`Down` are taken by history — and a
list UI wants them, which is a real collision to resolve (§4).

---

## 2. THE EVIDENCE BASE — what players actually type

Two corpora, both committed.

**(a) `tests/data/parser_golden_corpus.json`** — 447 entries, mean 24.1 chars /
4.0 words, 46.5% of the `<Name>, <order>` shape. It is a *test* corpus (121 of
447 utterances start with "Ney") and I do not rest anything on its frequencies.

**(b) `tools/playtest_scripts/*.json`** — 31 campaigns, **1,416 commands**,
extracted from each file's `turns` map. This is the closest committed thing to a
transcript of France being played. Probe 2b:

- mean **20.5 chars**, median 19, p90 34, **3.2 words**
- **63.9%** are `<Name>, <order>`
- first token: `ney` 14.2%, `status` 14.1%, `davout` 10.0%, `talleyrand` 8.9%,
  `soult`/`murat` 6.8% each — **the eight own-marshal names plus `status` are
  73% of all first tokens**
- 374 distinct strings for 1,416 instances; **86.2% of instances are an exact
  repeat** of some other instance
- **47.5% exactly repeat an earlier command in the same campaign** — and that
  figure is exactly the hit rate arm F achieves (probe 6), which is the internal
  consistency check that the prefix-history model is measuring the right thing

⚠ **Honest limit.** These are authored scripts, not human play. They are
deliberately repetitive (`commanded_full40.json` spends all four AP for forty
turns) and the `weird_*` family deliberately probes odd phrasings. A human is
probably *less* repetitive than 86% and *more* exploratory. Every "% saved"
below is therefore an **upper bound on the repeat-driven arms (B, F)** and
roughly fair for the template-driven arms (D, G), whose candidates are generated
from world state rather than from the player's own past.

---

## 3. WHERE IT MUST LIVE — **(a) purely client-side**, and the fog decides it

### 3.1 What the client already holds, fog-honestly

Every response carries `game_state` built by
`WorldState.get_filtered_game_state_summary()` (`backend/models/world_state.py:9418`),
which wraps `get_game_state_summary()` (`:9092`). The client stores the map half
in `map_renderer_base.gd:204-209` (`region_controllers`, `region_marshals`,
`region_visibility`, `region_fogged_forces`, `region_garrisons`,
`region_full_data`) via `update_all_regions` (`:2808`), fed from
`game_state.map_data` at `main.gd:853`.

Measured on the live 1805 boot world (probe 3 / probe 4):

| source | on the wire? | boot count | fog status |
|---|---|---:|---|
| `game_state.marshals` — own marshals + location | yes, every response | **8** | player-only by construction (`world_state.py:9337`, `if m.nation == self.player_nation`) |
| `game_state.enemies` — foreign marshals | yes | **4** | **every one at PARTIAL+** (verified); 10 of the 14 living foreign marshals are absent |
| `game_state.map_data` — all region names + controllers | yes | **126 / 126** | "Always public" block, `world_state.py:9466-9470` |
| `map_data[r].marshals[]` | yes | FULL-visibility enemies only | `Deroy` alone at boot |
| `map_data[r].fogged_forces[]` | yes | PARTIAL/STALE, band only | `ArchdukeJohn`, `Brunswick`, `Mack` |
| nations | derivable from controllers | **20** | public |
| adjacency | `GET /map_topology` → `scenes/map.gd:30` `connections[region] = entry.adjacent` | 17 provinces adjacent to a corps at boot | public |
| AP / gold / manpower / levy | yes (`summary` keys) | — | player's own |

The leak test (probe 4 §C): the set of names appearing anywhere in the map
payload, minus the set of foreign marshals at PARTIAL+ visibility, is **`[]`**.

**So a completer that draws only from `game_state` cannot name a hidden enemy.
That is a structural property, not a rule someone has to remember.**

One precision worth writing down: `game_state.enemies` is *not* the same set as
`world.get_visible_enemies()` (`world_state.py:4015`). The helper is "marshals of
nations **at war with us**, at PARTIAL+" (2 at boot: Mack, ArchdukeJohn); the
wire key is "**all** foreign marshals at PARTIAL+" (4: + Brunswick/Prussia,
Deroy/Bavaria, both at peace). Both gate on PARTIAL+, so both are fog-safe — but
a completer built on the wire key will happily offer `Ney, attack Brunswick`,
which is an act of war on a neutral. That is a §4 ranking problem, not a fog
problem, and it must be handled deliberately.

### 3.2 Why option (b), a backend `GET /completions?prefix=`, is the wrong door

There is no such endpoint today (`api_client.gd:79-143` lists all 12 GETs; none
is a lookup). Building one means writing a name list on the backend — and the
helper sitting right there is:

```
backend/commands/parser.py:699
def _extract_enemy_marshal_names(world, player_nation):
    """Return all marshal names in `world` that do NOT belong to player_nation."""
```

No fog filter. It is called at `parser.py:878` for fuzzy matching, and it is
already a routed, open defect — **IQ9-X2**, `docs/COMMAND_ROBUSTNESS_SPEC.md:413`:
*"the fuzzy suggestion can name a FOGGED enemy (`_extract_enemy_marshal_names` is
omniscient; R5; owner CR-6 proper)"*. At boot that is 10 marshals the player has
never seen, including `Kutuzov`, `Moore` and `ArchdukeCharles` (probe 4 §B).

A completions endpoint would be IQ9-X2 one layer out, on a surface with **no
filter at all** and a much wider blast radius — a suggestion list is read, a
fuzzy error message is only read after a mistake. Option (b) is rejected.

Option (c), hybrid, is rejected for a simpler reason: it buys nothing. Everything
a completer needs is already on the wire and refreshed on every response. The
only thing the client lacks is adjacency, and it already fetches that once at
boot via `/map_topology`.

**Verdict: (a) purely client-side, `scripts/main.gd` + one new scene. Zero
backend diff, zero new fog surface, zero new endpoint.**

---

## 4. WHAT SHAPE

### 4.1 What to complete

Measured per-slot difficulty on the boot world (probe 3):

- **Addressee (the marshal name)** — 8 candidates, and **every one is unique
  within 1–2 characters**: `D`→Davout, `S`→Soult, `L`→Lannes, `B`→Bernadotte,
  `Ne`→Ney, `Mu`→Murat, `Ma`→Massena, `Na`→Napoleon. This slot is 63.9% of all
  commands and is the cheapest possible win.
- **Target (enemy)** — 4 candidates at boot. Trivial.
- **Destination (province)** — 126 candidates, but **17** if scoped to provinces
  adjacent to one of the player's corps (13% of the map). Scoping matters: the
  worst 3-char province prefix collides 4 ways (`ber` → 4 regions, `nor` → 4).
- **Verb** — ~74 in `VALID_ACTIONS` (`backend/ai/validation.py:29`), but the
  played vocabulary is far narrower (`fortify`/`unfortify`/`drill`/`attack`/
  `move to`/`hold` dominate the repeat table).

### 4.2 The four options, graded

| option | keystrokes saved | discoverability | risk of a wrong order | cost (files) |
|---|---|---|---|---|
| **1. Addressee-only completion** (`C`) | 12.7%, hit 54.6% | low — invisible until you type | **nil**: it completes a name you started typing; the rest is still yours | `main.gd` only, ~40 lines |
| **2. Inline ghost, whole line** (`D`) | 29.6%, hit 68.3% | medium — the ghost teaches phrasing | **low but nagging**: wrong 63.4% of the time at 3 chars; accepting is deliberate (Tab), but the eye is drawn to a wrong sentence constantly | `main.gd` + a ghost `Label` overlaid on the `LineEdit`; fiddly caret-metrics work |
| **3. Ranked top-5 list** (`G`) | **39.7%**, hit 68.3% | **high** — it is a visible menu of legal phrasings, which is the "what can I say?" answer as a side effect | **low**: 5 visible rows, explicit selection, nothing auto-inserted | `main.gd` + one new scene (~2 files, ~200 lines) |
| **4. Prefix-filtered history** (`F`) | **31.7%**, hit 47.5% | low — same invisibility as today | **nil**: only replays sentences the player already sent | `main.gd` only, ~30 lines, **no new data source at all** |

Cost/benefit, `% saved ÷ rough build size`:

- **F: 31.7% for ~30 lines in one function.** By a wide margin the best ratio.
- G: 39.7% for a new scene + a template generator + list navigation.
- D: 29.6% for comparable effort to G and a worse result **and** a noisier surface.
- C: 12.7%, and it is strictly dominated — G subsumes it.

**Ghost text loses on its own measurement.** That is the finding I did not
expect going in.

### 4.3 Mechanics of the recommended shape

- **Candidates, ranked**: (1) this session's `command_history`, most recent first
  — which already includes chip-issued commands (§1.2); (2) generated templates
  from `game_state`. Dedupe by string.
- **Template generator**, client-side, from data already held:
  `"<Own>, <solo verb>"` × 8 marshals; `"<Own>, attack <enemy>"` from
  `game_state.enemies`; `"<Own>, move to <adjacent province>"` from
  `/map_topology` + own marshal locations; the bare verbs (`status`,
  `end turn`, `economy report`, `help`); `"declare war on <nation>"` and the
  Talleyrand forms from the controller set. **306 candidates at boot** with
  destinations scoped to adjacency, versus 1,178 unscoped (probe 5) — scope it.
- **Insert the DISPLAY form, not the key.** Probe 8 measured both through the
  real parser: `Ney, attack Archduke John` → `action=attack target=ArchdukeJohn
  conf=0.95`, identical to the key form. Only two 1805 marshals differ
  (`ArchdukeCharles`, `ArchdukeJohn`), but the corpus shows the spaced form *is*
  what players type (8× `Ney, attack Archduke Charles` in the missed-commands
  table), and `Utils.humanize_entity_name` (`scripts/utils.gd:284`) is the
  existing chokepoint. Eight province names contain a space or hyphen
  (`Franche-Comte`, `Ile-de-France`, `White Russia`, …) — insert verbatim; probe
  8 confirms `Ney, move to Franche-Comte` parses at 0.95.
- **Keys**: `Tab` accepts the highlighted row (free, §1.3). `Up`/`Down` currently
  own history — resolve it as *list-open takes them, list-closed keeps history*,
  so nothing is lost. `Esc` closes the list before it releases focus (add an arm
  above the existing `KEY_ESCAPE` branch at `main.gd:935`).
- **Where it draws**: as a Control inside `BottomLeftUI/MainMargin/MainLayout`
  (`main.tscn:42`) between `OutputScroll` (`:219`) and `InputSection` (`:234`) —
  **not** a `CanvasLayer`. `BottomLeftUI` is a plain `PanelContainer` at the
  scene root (`main.tscn:24`), so every CanvasLayer ≥ 25 (war HUD 25, region
  panel 26, screens 50, top bar 75) draws over it; a popup would have to pick a
  layer and fight that ladder. A child row inside the terminal's own VBox
  reflows with the panel, is bounded by a terminal the player can already resize,
  and **inherits `content_scale_factor` automatically** — which is the IQ-10
  trap (`_apply_ui_scale`, `main.gd:1352`) avoided by construction rather than by
  a clamp. Fixed-size surfaces are exactly what broke at Interface Scale 2.0.

---

## 5. THE HONEST ALTERNATIVES, RANKED

Ranked by `(keystrokes saved × frequency) ÷ build cost`.

1. **Prefix-filtered history — 31.7%, ~30 lines, no new data.**
   Today `_history_previous` (`main.gd:1005`) walks the whole list. Make it walk
   only entries whose lowercase starts with what is already typed (the standard
   shell idiom), and keep the typed prefix on screen. Nothing new is stored,
   nothing new is fetched, no fog surface is created, and it learns from chips
   for free. **This is the single best keystroke-per-line-of-code in the whole
   analysis.** Pair it with *not* raising `MAX_HISTORY` — and if it is raised,
   raise it only because filtering makes the walk cheap, never on its own.
2. **Make the region-panel chips FILL the line instead of sending it — near-zero
   cost, and it is the project's own established idiom.**
   `scripts/tutorial_overlay.gd:15-16` already does exactly this and says why:
   *"NEVER sends a command — the suggest chip FILLS the command line via the
   suggest_command signal (muscle memory for a typed-command game)"*; handler at
   `main.gd:6721`. The region panel does the opposite: `region_panel.gd:26`
   emits `region_command`, and `_on_region_panel_command` (`main.gd:6399`)
   sends it straight to the API. The chips already carry well-formed typed
   strings (`region_panel.gd:134` builds `"<Name>, <verb>"`;
   `region_panel.gd:517-521` build `"build depot in %s"` etc.). Teaching the
   phrasing is free; a Shift-click-to-fill, or fill-for-orders/send-for-purchases,
   costs a handful of lines. ⚠ This is a **UX behaviour change on a shipped
   surface** and needs the user's word, not mine — `region_panel.gd:14-16`
   documents send-immediately as the deliberate design.
3. **The ranked top-5 completer — 39.7%, one new scene.** The real predictor.
   Worth building *after* 1 and 2, and its own measurement says build it as a
   list.
4. **An explicit "what can I say?" verb — small, and it fixes a real hole.**
   `help` today is `_execute_help` (`backend/commands/meta_executor.py:629`): a
   **static 11,633-character, 216-line** block with *no* world-derived content
   (probe: no `{` placeholder anywhere in it). It is a reference manual, not an
   answer to "what can I do this turn". A short world-derived list — *these eight
   marshals, these four visible enemies, these seventeen provinces you can reach,
   you have N AP* — is genuinely different and would take the pressure off the
   predictor. `backend/ai/question_desk.py` is the existing precedent for a
   fog-honest FACT answer and states the discipline in its docstring.
5. **Single-line ghost text — 29.6%, and it is wrong 63% of the time.** Do not
   build this.
6. **Raising `MAX_HISTORY` 10 → 50 — measured NEGATIVE (14.1% → 5.1%).** Do not
   do this on its own.

---

## 6. RECOMMENDED v1

**Build, in this order, all in `scripts/main.gd` + one new scene:**

**v1a — Prefix-filtered history recall.** Modify `_history_previous` /
`_history_next` (`main.gd:1005-1035`) to filter on the typed prefix, preserve the
prefix while walking, and dedupe repeats. Persist `command_history` across
sessions through `UiSettings` (`scripts/ui_settings.gd:30`, `user://ui_settings.cfg`)
— it already stores terminal size, UI scale and the API key, so the pattern
exists. **31.7% of keystrokes, one function, no new data, no fog surface.**

**v1b — The ranked suggestion row.** A `Control` inside `MainLayout` between
`OutputScroll` and `InputSection`, driven by a new `text_changed` connection
(`main.gd:643` neighbourhood), showing up to 5 candidates from
`history ∪ client-side templates`, `Tab` to accept, `Up`/`Down` to move while
open, `Esc` to close. Templates generated from `game_state.marshals`,
`game_state.enemies`, `game_state.map_data` controllers and the `/map_topology`
adjacency the client already holds. Display form inserted, adjacency-scoped
destinations. **Takes the total to ~39.7%, hit rate 68.3%, and cold-starts at
25.0% / 58.1% on the first four commands of a campaign with an empty history
(probe 5) — so it works on turn 1.**

**Ranking rule that must be written down:** a neutral nation's marshal
(`Brunswick`, `Deroy` at boot) may appear as a *target* only below every
at-war target, or not at all. Offering `Ney, attack Brunswick` as the top
proposal invites an accidental war on Prussia. The client can tell: it holds
`war_status` via `build_active_wars` (`backend/game_logic/war_status.py`,
embedded in every response) — the same data the war HUD renders.

**One test file**, `tests/test_predictor_*.py`, pinning the two things that can
silently rot: (i) the template generator draws only from keys the filtered
summary emits — an AST/source census in the spirit of the IQ-9 keyless pins, so
that a future edit reaching for an omniscient source reds; (ii) every generated
template parses at ≥ 0.7 through the mock parser, so the completer can never
propose a sentence the fast parser then escalates or refuses. (ii) is cheap and
is the guarantee that makes the feature safe to accept blind.

### Deferred, with owners

| deferred | owner | why |
|---|---|---|
| Chips fill instead of send | **the user** (a UX ruling on a shipped surface) | `region_panel.gd:14-16` documents send-immediately as deliberate; the tutorial's fill idiom argues the other way. Not mine to flip. |
| A world-derived "what can I say?" | **CR-6 proper** (ROADMAP 15) | it is an advisory/question-desk surface, and `question_desk.py:17-19` already homes advice there |
| Backend `/completions` | **struck, not deferred** | §3.2 — it recreates IQ9-X2 on a wider surface |
| Learning across campaigns / n-gram model | **none — do not build** | the vocabulary is 374 strings; a prefix match over generated templates is already at 68.3% hit rate |

---

## 7. THE OTHER HALF THE USER ASKED — "is routing to the LLM worth it?"

Not my assigned scope, but the predictor bears directly on it, so here is the one
measurement (probe 7, mock mode, no network).

Gate: `LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7`, `backend/ai/llm_client.py:63`.
Running all 374 distinct played strings through the fast parser against the live
1805 world:

- **11.5% of distinct strings** fall below the gate (43 of 374)
- **4.1% of issued commands** (58 of 1,416) would consult the LLM
- confidence histogram: 0.95 → 165, 0.9 → 140, 0.8 → 22, 0.55 → 3, 0.5 → 40

**The escalating 4% is almost entirely natural/exploratory phrasing** —
`Ney, deal with Mack`, `Soult, deal with the Austrians`, `send somebody, anybody,
to take Munich`, `burn Munich to the ground`, `Ney, take Vienna`, and a bare
`Ney` (conf 0.5 → `unknown`). These come overwhelmingly from the `weird_*`
scripts, which exist to probe odd phrasing, so **4.1% is an over-estimate of a
scripted board and probably an under-estimate of a human**, who improvises more.

The connection to this row: **every command reached by accepting a proposal is by
construction a string the fast parser already scores ≥ 0.7** (that is test (ii)
above). A completer does not just save keystrokes — it moves traffic off the
escalation path. But it also *narrows what players try*, and the sentences in
that 4% list are the game's best moments (`Murat, you magnificent idiot, ride at
them`). **A predictor should make the canonical phrasing cheap without making the
improvised phrasing feel wrong** — which is another argument for a dismissable
list over ghost text that overwrites what you were saying.

---

## 8. VERIFICATION LEDGER

| claim | status |
|---|---|
| all `file:line` anchors | verified by reading at current line numbers |
| 1,416 played commands, all distributions | probe 2b |
| live boot world: 8 own / 4 wire enemies / 10 hidden / 126 regions / 17 adjacent | probe 3, probe 4 |
| no name in the map payload is below PARTIAL+ | probe 4 §C, result `[]` |
| `_extract_enemy_marshal_names` is omniscient | read at `parser.py:699` + IQ9-X2 at `COMMAND_ROBUSTNESS_SPEC.md:413` |
| every keystroke table and hit rate | probe 5, probe 6 |
| ghost wrong 63.4% at 3 chars | probe 6 |
| display form parses to the key at 0.95 | probe 8 |
| escalation 4.1% by instance / 11.5% by distinct string | probe 7 |
| `help` is 11,633 static chars, no world data | probe over `meta_executor.py` |
| **bare `Tab` currently moves focus to SendButton** | **UNVERIFIED by execution** — read off `main.tscn` + Godot focus semantics; confirm on the engine before binding |
| human play resembles the scripted corpus | **UNVERIFIED** — authored scripts, not human play; stated as an upper bound for the repeat-driven arms in §2 |
| **the working tree was NOT clean when I measured** | **flagged, and bounded** — `backend/ai/clause_guards.py` carries 71 uncommitted lines ("CX slice 1 — A QUESTION NEVER ORDERS"). **I did not write it** (I was read-only throughout; `git status` is otherwise clean) — it is a sibling agent's in-progress work in this same workflow, and nobody should revert it thinking it is mine. Impact on my numbers, measured not assumed: probes 2b/5/6 (every keystroke table in §0 and §4) are pure string arithmetic and never load the parser, so they are **unaffected**. Probes 7 and 8 do load it: of 1,416 played commands, **4 (0.28%)** match the changed leads (`who is winning?`, `who is the traitor among my marshals`), so the 4.1% escalation figure moves by at most 0.28pp; none of probe 8's eight sentences match at all. |
| my own first simulation | **was wrong and is corrected** — probe 6 initially omitted `hist.append(cmd)`, so arm F measured 0.0%; caught by cross-checking against probe 5's independently-computed D0 = 25.0%. The table in §0 is the fixed run. |
