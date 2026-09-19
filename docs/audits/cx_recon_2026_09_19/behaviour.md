# What players actually do — an empirical intent census

Recon for the cx row (text predictor / parser efficiency / LLM routing).
Read-only pass at `f7008582`, September 19 2026. Every number below is either
a `file:line` or the output of a probe committed under
`scratchpad/cx_recon/probes/` (p1…p11) and re-runnable.

---

## 0. ⛔ READ THIS BEFORE USING ANY NUMBER

**No human has ever played a measured campaign in this repo.** Every one of
the 8,422 typed commands in the archive is a *driver* command, and the driver
types from an authored JSON script plus a fixed popup-answer policy
(`tools/playtest_driver.py`, `POLICY_DEFAULTS` at :~485). That has three
consequences that change how the ranking must be read:

1. **The commanded arms are AP-padding, by the script's own admission.**
   20 of the 23 commanded archives ran `commanded_full40.json`, whose
   `_note_d6` key says in writing it exists to "spend all four military
   actions every turn". Measured on `iq8-cmd-historical` (p11): of the **83
   military-AP successes in 40 turns, 68 (82%) are fortify / unfortify /
   drill** — against **9 successful marches and 6 successful attacks in the
   whole campaign**. That is a harness artefact. Do not rank `drill` above
   `attack` because of it.
2. **The archives have ~one syntactic template per intent.** Measured (p10):
   `march a corps to a province` = **4 templates for 507 commands**, and 454
   of those 507 are literally `<Marshal>, move to <Region>`. `attack` = 16
   templates for 688, of which 626 are `<Marshal>, attack <Enemy>`. The
   variety is entirely in the *slots*, not the grammar. A human is not
   constrained this way.
3. **The `weird-*` arms are adversarial on purpose** (10 role-play personas)
   and are the only place messy phrasing lives — they hold **140 of the 148**
   commands that would escalate to the LLM.

Where a human would sit is **between the archive (1 template/intent) and the
golden corpus (1:1 — 42 distinct templates for `attack` alone, p10)**. That
gap is the single largest open question for the row and it cannot be closed
by another probe.

**Second-order limit:** every command string was classified by running it
through the real parser against the **1805 turn-1 boot world**
(`parser_eval.build_world("1805")`), not the world it was typed in. Verb
classification is world-independent; *name resolution* is not. ≤36 of 8,422
classifications (0.43%) are world artefacts — the `X-unparsed (name not
found)` and `diplomatic error` rows (e.g. `Senarmont, move to Munich` is
valid in the tutorial world and unresolvable in 1805).

---

## 1. Ranked intents

Four independent sources, none authoritative alone:

| col | source | what it measures |
|---|---|---|
| **A** | 8,422 CMD lines / 89 archives / 2,590 turns | what got typed |
| **A-cmd / A-oth** | split of A: the 23 padding commanded arms vs the other 66 | isolates the artefact |
| **#arch** | archives the intent appears in | breadth |
| **tmpl** | distinct *syntactic templates* after blanking marshal/region/nation/number slots (p10) | predictability |
| **B / #sc** | 1,416 commands in 31 authored scripts / how many scripts use it | what a designer writes |
| **C** | 447 golden-corpus entries folded to the same vocabulary | phrasing the project has had to defend |
| **D** | the 15-step tutorial curriculum (`tutorial_overlay.gd` STEPS) | what the game teaches |

`ref%` = share refused by the executor. `esc` = commands that would cross the
0.7 gate into the LLM (`llm_client.py:63`, `_should_fallback_to_llm` at :874).

| # | intent | A | A-cmd | A-oth | #arch | tmpl | ref% | esc | B | #sc | C | D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **end the turn** | 2590 | 920 | 1670 | 89 | 1 | 0.2% | 0 | 0 | 0 | 3 | 1 |
| 2 | **fortify a corps** | 862 | 828 | 34 | 33 | 1 | 35.3% | 0 | 131 | 11 | 4 | 1 |
| 3 | **read the intelligence report** (`status`) | 785 | 414 | 371 | 70 | 1 | 0.0% | 0 | 200 | **29** | 6 | 0 |
| 4 | **drill a corps** | 713 | 713 | 0 | 23 | 1 | 33.7% | 0 | 93 | 3 | 1 | 0 |
| 5 | **attack an enemy corps** | 688 | 345 | 343 | 48 | 16 | 51.9% | 0 | 206 | **22** | **26** | 3 |
| 6 | **unfortify a corps** | 644 | 644 | 0 | 23 | 1 | 27.8% | 0 | 87 | 6 | 1 | 0 |
| 7 | **march a corps to a province** | 507 | 437 | 70 | 43 | 4 | 59.0% | 0 | 163 | **20** | 0 | 3 |
| 8 | **recruit troops** | 295 | 286 | 9 | 31 | 5 | 31.2% | 0 | 45 | 8 | 4 | 1 |
| 9 | *(unparsed — no known verb)* | 177 | 0 | 177 | 18 | 33 | 75.1% | **139** | 52 | 6 | 47 | 0 |
| 10 | **ask Talleyrand for counsel** | 117 | 0 | 117 | 41 | 2 | 0.0% | 0 | 54 | **21** | 6 | 0 |
| 11 | **standing order: hold position** | 96 | 0 | 96 | 20 | 2 | 17.7% | 0 | 27 | 7 | **27** | 0 |
| 12 | **propose a treaty (peace)** | 89 | 0 | 89 | 11 | 4 | 7.9% | 0 | 26 | 8 | 13 | 0 |
| 13 | **build ships** | 74 | 0 | 74 | 6 | 1 | 1.4% | 0 | 21 | 2 | 3 | 0 |
| 14 | **read the treasury / economy report** | 73 | 0 | 73 | 17 | 3 | 0.0% | 0 | 20 | 6 | 1 | 1 |
| 15 | **build a structure in a province** | 68 | 0 | 68 | 12 | 7 | 51.5% | 0 | 19 | 5 | 1 | 0 |
| 16 | **declare war on a nation** | 64 | 0 | 64 | 8 | 2 | 0.0% | 0 | 16 | 2 | 8 | 0 |
| 17 | **standing order: march to a province** | 58 | 0 | 58 | 18 | 2 | 13.8% | 0 | 42 | 11 | **36** | 3 |
| 18 | **invest in a vassal** | 53 | 0 | 53 | 13 | 1 | 100% | 0 | 19 | 5 | 4 | 0 |
| 19 | **ask for help** | 48 | 0 | 48 | 12 | 7 | 0.0% | 0 | 13 | 3 | 7 | 0 |
| 20 | **ask a court for peace terms** | 44 | 0 | 44 | 17 | 2 | 47.7% | 0 | 16 | 7 | 1 | 0 |
| 21 | **purchase a levy** (substitutes) | 39 | 39 | 0 | 3 | 1 | 38.5% | 0 | 13 | 1 | 3 | 0 |
| 22 | **order a cavalry charge** | 36 | 0 | 36 | 8 | 1 | 97.2% | 0 | 10 | 3 | 7 | 0 |
| 23 | **guarantee a nation** (D5) | 31 | 0 | 31 | 13 | 1 | 32.3% | 0 | 10 | 4 | 1 | 0 |
| 24 | **diplomatic mission: improve relations** | 23 | 0 | 23 | 4 | 1 | 0.0% | 0 | 42 | 2 | 5 | 0 |
| 25 | **revoke a marshal's rente** | 20 | 0 | 20 | 8 | 1 | 10.0% | 0 | 5 | 2 | 4 | 0 |
| 26 | **grant a marshal a rente** | 19 | 0 | 19 | 11 | 1 | 21.1% | 0 | 8 | 4 | 5 | 0 |
| 27 | **change a vassal's autonomy** | 19 | 0 | 19 | 9 | 2 | 100% | 0 | 9 | 4 | 1 | 0 |
| 28 | **launch a naval expedition** | 18 | 0 | 18 | 6 | 4 | 94.4% | 0 | 7 | 2 | 3 | 0 |
| 29 | **order the grand diversion** | 17 | 0 | 17 | 6 | 1 | 52.9% | 0 | 5 | 2 | 5 | 0 |
| 30 | **grant a province to a vassal** | 14 | 0 | 14 | 8 | 1 | 100% | 0 | 5 | 2 | 3 | 0 |
| 31 | **commission a new marshal** | 13 | 0 | 13 | 5 | 3 | 0.0% | 0 | 4 | 2 | 3 | 0 |
| 32 | **make / release a vassal** | 24 | 0 | 24 | 8 | 4 | ~96% | 0 | 7 | 2 | 3 | 0 |
| 33 | **set a fleet's posture** | 10 | 0 | 10 | 6 | 2 | 0.0% | 0 | 3 | 2 | 5 | 0 |
| 34 | **sponsor / buy off a design** (D5) | 18 | 0 | 18 | 5 | 4 | 100% | 0 | 6 | 2 | 4 | 0 |
| 35 | **endow a marshal with an estate** | 5 | 0 | 5 | 3 | 2 | 100% | 0 | 4 | 3 | 2 | 0 |
| 36 | **standing order: pursue an enemy** | 4 | 0 | 4 | 4 | 1 | 25% | 0 | 1 | 1 | **12** | 0 |
| 37 | **scout a province** | 2 | 0 | 2 | 2 | 1 | 50% | 0 | 4 | 4 | 7 | 1 |
| 38 | **retreat a corps** | 0 | 0 | 0 | 0 | — | — | — | 0 | 0 | **9** | 0 |
| 39 | **break a treaty** | 0 | — | — | — | — | — | — | 0 | 0 | **10** | 0 |
| 40 | **issue an ultimatum** | 0 | — | — | — | — | — | — | 0 | 0 | **8** | 0 |
| 41 | **standing order: support** | 0 | — | — | — | — | — | — | 0 | 0 | **12** | 0 |
| 42 | **propose a treaty (alliance)** | 0 | — | — | — | — | — | — | 0 | 0 | **13** | 0 |
| 43 | **cancel a standing order** | 0 | — | — | — | — | — | — | 0 | 0 | 4 | 0 |
| 44 | **form / break square** | 0 | — | — | — | — | — | — | 0 | 0 | 3 | 0 |
| 45 | **diplomatic missions: court / intel / reassure / undermine** | 0 | — | — | — | — | — | — | 0 | 0 | 11 | 0 |

Rows 38–45 have **zero archive occurrences and real corpus weight** — they are
intents nobody has ever driven but the parser is pinned to support. `retreat`,
`support`, `alliance`, `ultimatum` and `cancel` are conspicuous: a human
playing a losing campaign would use all five.

### The honest top-10, artefact removed

Discount the padding verbs by their `A-oth` column and weight `#sc` (breadth
across authored scripts) and `C` (phrasing variety):

1. **end the turn** — universal, one string, zero ambiguity
2. **read the intelligence report** (`status`) — 29 of 31 scripts, 70 of 89 archives
3. **attack an enemy corps** — 22 scripts, 26 corpus rows, 42 corpus templates
4. **march a corps to a province** — 20 scripts; **zero corpus rows for the tactical form** and 18 for `strategic:MOVE_TO`
5. **ask Talleyrand for counsel** — 21 of 31 scripts; the widest *non-order* intent
6. **standing order: hold / march / pursue / support** — 27+36+12+12 = **87 corpus rows**, the single largest corpus family
7. **recruit troops** — 8 scripts, admin pool
8. **propose a treaty** (peace / alliance / the other five types) — 8 scripts, ~37 corpus rows
9. **fortify / unfortify / drill** — real, but 96% of their archive volume is padding
10. **read the treasury** (`economy`) — free, 6 scripts, taught first in the tutorial

---

## 2. Routine vs rare-but-important

This is the distinction that decides where a predictor pays. Derived from
per-turn rates on the commanded arms (p3) and archive breadth (p9).

### Per-turn routine (many times a turn, every turn)

| intent | rate | note |
|---|---|---|
| end the turn | **1.00 / turn** | exactly once, always |
| the 4 military-AP orders (attack / march / fortify / drill / unfortify / scout / charge) | **≤4 / turn, ~2.1 actually spent** | see §3 |
| `status` | 0.45 / turn (commanded), appears in 70/89 archives | free |
| answering a `diplomatic_dialogue` popup | **0.85 / turn** across all archives, 0.46 on commanded (p4) | unavoidable |
| answering a letter-book letter | **0.44 / turn**, 1,133 total (p4) | unavoidable |
| answering a `marshal_petition` | **0.28 / turn** (p4) | unavoidable |
| viewing a `battle_diorama` | 0.11 / turn | display-only |
| recruiting | 0.31 / turn (commanded) | admin pool |

Total *answer* load: **≈1.6 popups + letters per turn**, against ≈2.1 spent
military AP. **A player answers about as often as they order.** That is the
most under-appreciated number in this report — and none of it goes through
the parser today (see §5).

### Rare but campaign-defining (≤ a handful per campaign)

`declare war on a nation` (64 across 8 archives) · `propose a treaty` ·
`ask a court for peace terms` · `issue an ultimatum` (0 archive, 8 corpus) ·
`break a treaty` (0 archive, 10 corpus) · `commission a new marshal` ·
`endow a marshal with an estate` / `grant a rente` / `revoke a rente` ·
`grant a province to a vassal` · `make / release a vassal` ·
`launch a naval expedition` · `order the grand diversion` ·
`sponsor` / `buy off` / `guarantee` (the D5 instruments) ·
`purchase a levy` · `set a fleet's posture` · the settlement wizard.

**The asymmetry to exploit:** the routine intents are the ones with **one
template and two slots** (`<Marshal>, move to <Region>`, `<Marshal>, attack
<Enemy>` — 126 regions × 22 marshals × 20 nations, p10). The rare ones are
the ones with **many templates and high stakes** (`break a treaty`: 10 corpus
rows, 10 distinct templates, all one-offs). A cheap slot-filling predictor
covers the routine; only the rare ones have genuine phrasing spread, and they
are exactly the ones where a wrong parse is expensive and un-undoable.

---

## 3. The AP economy — measured

### The pools (`file:line`, all verified)

| pool | size | source |
|---|---|---|
| **military** | **4 / turn** | `world_state.py:1117-1118`; `calculate_max_actions()` = `4 + bonus_actions`; France's authored value is also 4, `nation_config.py:512` (`EUROPE_BASE_ACTIONS`) |
| **administrative** | **2 / turn** | `world_state.py:1128-1129` |
| **free** | unlimited | `executor.py:1273` — `status, help, end_turn, unknown, retreat, wait, debug, cheat, economy, treasury, finances, break_square` **plus every `diplomatic_*` verb and every vassal verb** |
| **admin-routed** | from the 2 | `meta_executor.py:30` `ADMIN_ACTIONS` = recruit, build, repair, grant_dotation, grant_pension, revoke_pension, recruit_marshal, recall_marshal, purchase_levy, build_fleet |

Two facts that reframe the question:

- **Diplomacy and vassal verbs cost ZERO action points.** They are gated by
  diplomatic points and gold, not AP (`executor.py:1273`, comment R72). A
  player may issue arbitrarily many per turn. Any "AP is the bottleneck"
  reasoning applies only to the 4 military + 2 admin.
- **A refused order costs nothing.** `executor.py:2664` charges only
  `if result.get("success", False) and action_costs_point and ...`. Spamming
  guesses at the parser is free in AP terms.

Per-action costs are `world_state.py:1151+`: everything is 1 except
`garrison` 2, `naval_expedition` 2, and 0 for the free set. A **strategic
order is 2 AP (1 for a literal marshal)** — so 4 AP is only two standing
orders.

### Measured spend and refusal — the three IQ-8 archives

These are the only archives whose `meta.json` carries the counters
(`docs/audits/playtest_digests/README.md` says so; the driver's
`ActionPointMeter` is `tools/playtest_driver.py:406`, `cmd_refused` at :1323).

| archive | turns | ap_available | ap_spent | **% spent** | commands | cmd_refused | **% refused** |
|---|---|---|---|---|---|---|---|
| `iq8-cmd-historical` | 40 | 160 | **85** | **53.1%** | 200 | **52** | **26.0%** |
| `iq8-cmd-austerlitz` | 40 | 160 | **80** | **50.0%** | 200 | **51** | **25.5%** |
| `iq8-cmd-marengo` | 40 | 160 | **76** | **47.5%** | 200 | **57** | **28.5%** |

**⚠ `ap_available` is the MILITARY pool only.** The meter's own docstring
(`playtest_driver.py:~425`) states "admin actions (a separate pool) are not
counted at all". The real per-turn allowance is 4+2 = 6, so 160 understates
the campaign's budget by 80 admin AP. **Nobody has ever measured admin-AP
utilisation.**

**Reconciliation (p11), which proves what `ap_spent` counts.** Re-deriving
from the digest's own CMD lines for `iq8-cmd-historical`: 200 commands → 52
refused, 58 free (40 `end turn` + 18 `status`), 7 admin-pool (`recruit`), and
**83 military-pool successes** against a recorded `ap_spent` of 85.
`iq8-cmd-austerlitz` reconciles **80 = 80 exactly**. The ±2 residual is
strategic orders at 2 AP and post-objection re-execution. Conclusion:
`ap_spent` ≈ successful military-pool commands; refusals are free.

### Refusal rate across all 89 archives

| class | commands | refused | rate | cmds/turn |
|---|---|---|---|---|
| commanded (padding script) | 4,626 | 1,273 | **27.5%** | 5.03 |
| weird (adversarial personas) | 2,893 | 629 | **21.7%** | 2.82 |
| other (flagship / aggressive) | 195 | 35 | **17.9%** | 2.71 |
| naval | 89 | 12 | 13.5% | 2.02 |
| tutorial | 55 | 3 | 5.5% | 1.83 |
| propose | 156 | 6 | 3.8% | 1.73 |
| ambient / fixture | 408 | 0 | 0% | 1.00 |

**A plausible human refusal rate is 15–25%.** The 27.5% figure is inflated by
the padding script; the 3.8–5.5% figures are arms that issue almost nothing.

### ⛔ What refusals actually are — and it is not the parser

The refusal *reasons*, classified over all 8,422 commands (p7):

| reason | n |
|---|---|
| already in that state / place | 167 |
| "cannot fortify/drill while in AGGRESSIVE stance" | 156 |
| "is locked in drill exercises and cannot receive orders" | ~110 |
| "is not currently fortified" | ~175 |
| "not at war with them" | 90 |
| "is fortified and cannot drill" | ~121 |
| region/marshal name not found | 65 |
| "We do not control X" / "controlled by Austria (diplomatic state)" | ~95 |
| "recovering from retreat and cannot attack" | 32 |
| "No intelligence on X's position — scout for him first" | 30 |
| out of range / no road | 21 |
| "Not enough actions! Need 1, have 0" | 21 |
| "X is a nation, not a province" | 18 |

Measured precisely (p7 + a follow-up classifier): **8,422 commands, 1,958
refused (23.2%).** Of those refusals, **201 (10.3%) are parse or
name-resolution failures** — the Berthier "I cannot interpret that order" /
"bewildered" / "frustratingly vague" family plus `Region 'X' not found`,
`Marshal 'X' not found` and `X is a nation, not a province`. The other
**1,757 (89.7%) are *legality* refusals**: the parser understood perfectly and
the executor said no. Parse failures are **2.39% of all commands typed**.

Per-intent worst offenders: `march` 59% refused (76 ×
"already there", 24+18 × "controlled by Austria"), `attack` 52% (81 × "not at
war", 30 × "no intelligence"), `fortify` 35%, `cavalry charge` 97%,
`invest in a vassal` / `change autonomy` / `grant province` 100%.

The design implication is blunt: **a text predictor that predicts *strings*
would keep proposing orders the executor refuses.** What pays is a predictor
that knows what is *legal right now* — which the backend already computes for
the region panel's honest-availability chips.

---

## 4. Canonical typed phrasing, and the click path

Canonical typed form = the most frequent archive string for that intent
(p9/p10, slots shown as `<M>`/`<R>`/`<N>`/`<#>`).

| intent | canonical typed | click path |
|---|---|---|
| end the turn | `end turn` | **End Turn button + hotkey** (`main.gd:154`, `:634`) |
| status | `status` | top-bar screen (hotkey) |
| economy | `economy report` | top-bar / ledger |
| attack an enemy corps | `<M>, attack <M>` (626/688) | **PARTIAL** — region panel chip `do:<M>, attack <enemy>` **only for enemies standing in the clicked province, capped at 2** (`region_panel.gd:557`). Its own comment at `:553-556` says the enemy list "ride[s] region_marshals at FULL visibility only" — so the chip is absent under PARTIAL fog. Not confirmed in a live client (see §7). |
| march a corps to a province | `<M>, move to <R>` (454/507) | **⛔ NONE.** Census of every `do:` and `order:` chip in the client (p-grep over `scripts/*.gd`) finds no move/march chip anywhere. Typed-only. |
| standing order: march / hold / pursue / support | `<M>, march to <R>` · `<M>, hold position` | **⛔ NONE** for issuing. Cancelling has one: `[Cancel]` in the ledger Orders tab (`strategic_ledger.gd:1090`, `:1153`) |
| fortify / unfortify / drill | `<M>, fortify` etc. | **YES ×2** — region panel (`region_panel.gd:545-549`) and Generals card (`marshal_management.gd:650-654`), both via `order:<verb>:<Marshal>` → `"<Name>, <verb>"` (`region_panel.gd:130-134`) |
| scout | `<M>, scout` | **YES** — region panel `order:scout:<M>` (`:550`) |
| recruit troops | `recruit <#> infantry with <M>` (264/295) | **YES** — region panel chip, but a **different phrasing**: `do:recruit <arm> in <Region>` (`:272`) |
| purchase a levy | `buy <#> substitutes for <M>` | **YES** — `do:buy substitutes for <M>` (`:332`), with a disabled-with-reason arm at `:341` |
| build a structure | `build market in <R>` | **YES** — `_BUILD_CHIP_DEFS` (`:516-522`) → `do:build depot/fort/training ground/market/stables in <R>`, plus watchtower (`:379`) |
| repair | — | **YES** — `do:repair buildings in <R>` / `do:repair <R>` (`:412`, `:424`) |
| build ships | `build ships` | **YES ×2** — region panel (`:441`) and the Admiralty ledger tab (`naval.py:2862` → `strategic_ledger.gd:820`) |
| set a fleet's posture | `blockade <N>` / `guard home waters` | **YES** — Admiralty chips (`naval.py:2761`, `:2801`) |
| grand diversion | `order the diversion` | **YES** — Admiralty chip (`naval.py:2825`) |
| naval expedition | `land <M> in <R> with <#> men` | **YES** — region panel `do:land …` (`:462`), with `No landing here` disabled arm (`:475`) |
| **every diplomatic and vassal intent** | see below | **YES — the F1 diplomacy wizard**, 2-step nation → action, `_build_command()` in `diplomacy_wizard.gd` emits the canonical typed echo for all 24 action ids |
| ask Talleyrand for counsel | `Talleyrand, assess our situation` (110/117) | **YES** — `Assess the Situation` chip (`diplomatic_ledger.gd:1067`) |
| commission a marshal | `commission <name>` | **YES** — Generals bench (`marshal_management.gd:362`) |
| grant/revoke a rente, endow an estate | `grant <M> a rente` · `revoke <M>'s rente` · `endow <M> with the Duchy of <R>` | **YES** — `Reward — estate or rente…` chip (`marshal_management.gd:564`) + the UX23-A notice-rail one-click rente |

The wizard's full typed vocabulary (`diplomacy_wizard.gd::_build_command`):
`propose peace/armistice/white peace/open borders/non aggression/defensive
alliance/alliance with <N>` · `propose vassalization to <N>` · `propose common
peace with <N>` · `declare war on <N>` · `break treaty with <N>` · `downgrade
relations with <N>` · `send ultimatum to <N>` · `invest in <N>` ·
`increase/decrease autonomy <N>` · `release <N>` · `cede territory to <N>` ·
`improve relations with <N>` · `court <N>` · `gather intel on <N>` ·
`reassure <N>` · `sponsor <N> against <aim>, <#> gold` · `buy off <N>` ·
`guarantee <N>`.

**The load-bearing finding for the row:** the click road and the typed road
converge at the parser by construction — `region_panel.gd:136-140` and
`strategic_ledger.gd:1157-1160` both carry "the same string a player would
type; the executor owns every gate". But **the #1 and #4 ordering intents
(march a corps; issue a standing order) have no click path at all.** They are
typed-only, they are the most frequent orders a real campaign issues, and
`march` carries the highest refusal rate of any large intent (59%). A
predictor on the typed road pays *exactly* where the click road is missing.

---

## 5. Supporting measurements for "is routing to the LLM worth it?"

Not my brief, but it fell out of the census and the numbers are load-bearing.

**The gate** (`llm_client.py:63`, `_should_fallback_to_llm` at :874): escalate
iff live provider **and** an API key **and** fast confidence `< 0.7` **and**
not a PARSE-NEG refusal **and** `game_state` present **and** the action is not
in `NON_ORDER_ACTIONS` (`validation.py:188` — help, status, debug, cheat,
economy, treasury, finances, end_turn, meta_command).

**Measured escalation rate over all 8,422 archive commands (p2):**

| | commands | would escalate | rate |
|---|---|---|---|
| **all archives** | 8,422 | **148** | **1.76%** |
| excluding bare `end turn` / `status` | 5,047 | 148 | **2.93%** |
| by distinct string | 383 | 36 | 9.4% |
| commanded arms | 4,626 | **0** | **0.00%** |
| weird (adversarial) arms | 2,893 | 140 | 4.84% |
| naval / other / tutorial | 339 | 8 | 2.4% |

Fast-parser confidence histogram over the same 8,422: `0.95`×1,542,
`0.9`×3,041, `0.8`×3,634, `1.0`×19 — and only **186 below the gate**
(`0.5`×181, `0.55`×5).

**What the 148 actually are:** 139 are `unknown action` at confidence 0.5
(`Ney, deal with Mack` ×24, `send somebody, anybody, to take Munich`,
`burn Munich to the ground`, `Ney, take Vienna`, plus prompt-injection
attempts), and 9 are an unresolved leading address at 0.55
(`UNRESOLVED_ADDRESS_CONFIDENCE`, `llm_client.py:67`) — of which several are
the world artefact noted in §0 (`Senarmont, move to Munich` is valid in the
tutorial world).

**The project's own statement of the LLM's job** is the 17 IQ-9 cassettes
(`tests/data/parser_cassettes/MANIFEST.json`) plus the 4 `live_only` corpus
rows. Every one is the same shape: **delegation** (`Ney/Davout/Soult, deal
with Mack`), **military idiom** (`Ney, cover the retreat`, `Ney, fix
bayonets`), **colloquial pursuit** (`hunt down mack`, `Ney, get after Mack`,
`Davout, keep an eye on Mack`), a demonym (`harass`), a diplomatic ask, and
gibberish recovery. The corpus also carries an explicit
`live_phrasing_backlog` of 18 more — `link up with davout`, `press on to
bavaria`, `rally to ney`, `shore up the defense`, `stand fast at belgium`,
`hold your ground` — marked "live-LLM-only capabilities today", owner CR-3.

**Read together:** the LLM is consulted on **under 3% of non-trivial
commands**, and the set it is consulted on is **enumerable** — one closed
family of ~35 idioms covering delegation, pursuit, rally/support and
stand-fast, against ~15 verbs that the keyword parser already resolves at
0.8–0.95. That is a finding the row should test directly rather than assume
either way; note that the archive rate is a **floor**, because the driver
types from scripts written to parse.

---

## 6. Corpus reconciliation (a stale number in the docs)

`tests/data/parser_golden_corpus.json` holds **447 entries**. `CLAUDE.md`
says 686 and the task brief says 447 — **both are right and they are
different things**: `worlds_for_entry` (`parser_eval.py:138`) evaluates a
`world: "any"` entry against *both* worlds. Measured: 245 `any` + 147 `1805`
+ 55 `legacy` = **692 entry×world evaluations**, minus the 6 evaluations of
the 4 `live_only` rows (skipped under mock) = **686**. 49 rows are
`mock_only`.

---

## 7. Open, unverified, and for other agents

- **UNVERIFIED — the human gap.** Everything here is driver behaviour. The
  archive's 1-template-per-intent and its 1.76% escalation rate are both
  floors. A single recorded human session would be worth more than every
  probe in this report.
- **UNVERIFIED — admin-AP utilisation.** Never measured by any instrument
  (the meter excludes the pool by construction). 80 of the campaign's 240 AP
  are unobserved.
- **UNVERIFIED — the popup/letter answer road.** 4,199 popups + 1,133 letters
  were answered by the driver through dedicated endpoints, not by typing, so
  the archive says nothing about how a human phrases an answer. IQ-7 (RV
  round) established a **closed, fail-closed typed grammar** for client
  petitions; whether players use it is unmeasured. This is ~1.6 decisions
  per turn and is invisible to every number in §1.
- **Left for the click-road agent:** I marked click paths from a census of
  every `do:` / `order:` chip and the wizard's `_build_command`. I did **not**
  run the client (no Godot binary invoked in this pass), so the *reachability*
  of each chip in a live session is unconfirmed — in particular whether the
  region panel's attack chips ever show, given they require FULL visibility
  on the clicked province.
- **⚠ The probes did not run against a clean HEAD.** `git status` during this
  pass showed one uncommitted sibling change in the tree:
  `backend/ai/clause_guards.py` (+71/−2), a CX slice-1 build adding the
  `A_QUESTION_NEVER_ORDERS` rule (`who`/`whom`/`whose`/`why` may not open an
  imperative). I did not write it and did not revert it. **Blast radius on
  this census, measured:** exactly 2 distinct strings / 15 archive
  occurrences begin with one of those four words (`who is winning?`, `who is
  the traitor among my marshals`), and both classify as `help` under either
  rule — `help` is in `NON_ORDER_ACTIONS`, so neither the intent ranking nor
  the escalation count moves. Every other number here is independent of the
  change. Re-run p1→p2→p3 on a clean tree if you want the belt-and-braces.

- **Provenance caveat on 63 archives:** `meta.json.script` is empty for every
  archive predating IQ-8's provenance fix, so my "(ambient)" label in p8 means
  *not recorded*, not *no script*. `weird-admiral` plainly ran
  `weird_admiral.json`. Only the three `iq8-cmd-*` archives carry full
  `requested`/`resolved`/`platform`/`engine_revision` provenance, and per
  `playtest_digests/README.md` a figure without an archive is **uncitable**.

## Probes (all re-runnable, `.venv/Scripts/python.exe <path>`)

`scratchpad/cx_recon/probes/` — `p1_extract.py` (raw CMD/POPUP/LETTER/script
extraction) · `p2_parse.py` (383 distinct strings through the real parser +
the real escalation gate) · `p3_intents.py` (intent mapper + archive census) ·
`p4_popups.py` (answer load) · `p5_scripts.py` (31 authored scripts) ·
`p6_corpus.py` (golden corpus) · `p7_refusals.py` (refusal rates and reasons)
· `p8_ap.py` (per-archive AP and refusal) · `p9_rank.py` (the ranked table) ·
`p10_templates.py` (syntactic template variety) · `p11_ap_reconcile.py`
(proves what `ap_spent` counts). Run `p1` → `p2` → `p3` first; the rest depend
on their JSON output.
