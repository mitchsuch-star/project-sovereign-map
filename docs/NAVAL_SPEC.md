# NAVAL_SPEC.md — "The Wooden Wall": the naval abstraction, the blockade war, and the liberation of Ireland (DEF-5)

> **v1.0 — AUTHORED August 1, 2026. STATUS: DRAFT FOR USER GATE (§12).** Nothing in this
> document is built. Owner rows consumed: `MAP_IMPLEMENTATION_PLAN.md` **DEF-5** (+ the
> Free Ireland rider), **DEF-6** (Channel edge — demotes to the naval-gated crossing here),
> **DEF-8** (explicitly NOT consumed — §3.4); ROADMAP **Phase 11** (Britain naval/subsidy
> pressure "needs DEF-5") is this spec's spine home.
>
> **The user's standing directive for this spec (Aug 1, 2026):** *build the naval spec — it
> can be abstracted; look into history; balance fun with lean design and usability.* Every
> section below answers to those four clauses, in that order of authority.
>
> **Why now (the played-world evidence):** the August-1 re-measure
> (`docs/audits/AI_V_SWEEP_2026_08_01.md` §10.5, rank 2) upgraded DEF-5 urgency — **Spain
> besieged London on turn 5** and the Channel walks both ways. The wooden wall that defined
> the period does not exist in the game, and its absence is now the believability ceiling.

---

## §0. Scope guard — what "abstracted" means here

**There is NO naval map layer.** No sea zones, no fleet pieces on the war table, no admiral
roster objects, no naval movement orders, no port sieges. A nation's navy is **one record**:
ships, readiness, posture. The sea exists in this game only through its four consequences on
the land war (§4). One new serialized field. Two postures. Four verbs. Zero new screens.

What the player experiences: the Channel finally *means something* (both ways), Britain can
be strangled or descended upon but never walked into, and Ireland becomes the mid-game naval
story the DEF-5 rider contracted. What the player never sees: hex-by-hex frigates.

Out-of-scope items each carry an owner in §10 (GR9) — nothing below is silently dropped.

---

## §1. History → mechanics (the "look into history" clause)

Each row is a load-bearing historical fact, its source anchor, and the ONE mechanic that
carries it. If a mechanic can't cite its row, it gets cut.

| # | The fact | Anchor | The mechanic |
|---|----------|--------|--------------|
| H1 | RN supremacy was **structural**, not tactical: ~100+ ships-of-the-line and the yards/crews to sustain them vs France's ~45 and Spain's ~30. No continental power could out-build it inside a war | 1805 orders of battle; the Trafalgar campaign | Authored fleet sizes (§3.2); build rate capped so parity-by-build takes ~25+ turns (anchor A1) |
| H2 | **Blockade rots the blockaded, not the blockader.** Cornwallis off Brest and Nelson off Toulon kept RN crews at sea and drilled; French crews sat in port and decayed — that gap, not ship quality, decided Trafalgar | The close blockade, 1803–05 | Readiness: blockading fleet holds 100; a blockaded fleet decays −5/turn to floor 50 and sorties at that readiness (§3.3) |
| H3 | The invasion of England needed the Channel **for a window, not forever**: "Let us be masters of the Strait for six hours, and we are masters of the world." The Boulogne camp waited two years for a window that never came; Villeneuve's West-Indies diversion was the attempt to make one, and Trafalgar was its price | Boulogne 1803–05; the Trafalgar campaign | The Descent chain (§5.3): a visible camp + a **window** (diversion gamble, fleet action, or pooled parity) — never permanent naval parity |
| H4 | **Small expeditions slip past.** Bantry Bay (Dec 1796) put 43 sails and ~15,000 men off Ireland unintercepted — the weather, not the RN, stopped the landing; Humbert landed ~1,100 at Killala in 1798 | Bantry Bay 1796; the 1798 rising; Emmet 1803 | Expedition evasion odds scale with size, not courage (§4.3): Ireland at Bantry scale is genuinely reachable; a Grand Army is not |
| H5 | **The real war was economic.** After Trafalgar, Napoleon's answer was the Berlin Decree — close the Continent's ports and bleed Britain's trade; Britain answered with Orders in Council. Neither side could touch the other's soldiers, so they besieged each other's ledgers | Continental System 1806–; Orders in Council 1807 | Blockade + CS 2.0 as income/war-weariness warfare (§5.1) — a real path to make Britain sue WITHOUT invasion, which the game today lacks entirely |
| H6 | **Coalition fleets pooled badly.** The Combined Fleet at Trafalgar was a Franco-Spanish patchwork — signal friction, undermanned Spanish ships, mutual distrust | Trafalgar, Oct 21, 1805 | Allied/vassal fleets pool at ×0.8 (§3.2) — Spain and the Batavian squadron matter, at a discount |
| H7 | Britain's counterstroke was the **descent** — Hanover 1805, Copenhagen 1807, the Peninsula — possible only because the RN owned the crossing | British expeditionary practice | The crossing gate (§4.1) is ratio-based, not France-literal: Britain's landings keep working at boot because their ratio clears; Spain's London walk dies because theirs doesn't |

The un-modelled remainder of history (weather, Copenhagen's fleet seizure, privateers,
colonies) is owned in §10, not forgotten.

---

## §2. Design principles (the "lean design and usability" clause)

1. **One store.** `world.fleets` is the only new serialized field (§8). Absent → all naval
   logic dormant (legacy world, bare flag world, every existing test: boot-zero by
   construction — the EC-W idiom).
2. **Consequences, not simulation.** The fleet record does exactly four things: gates
   crossings, blockades economies, carries expeditions, fights when those collide. If a
   proposed feature isn't one of the four, it goes to §10.
3. **Shown = applied.** Every odds figure, blockade cost, and readiness number the player
   sees is the number the resolver uses (the Q3/IGR-E discipline). Refusals name the gap
   ("The Royal Navy commands the Strait — 100 sail against our 31 effective").
4. **GR5 everywhere.** One predicate gates player and AI movement alike; the AI prices
   ships, postures, and expeditions through the same executor verbs. No France-literal
   naval logic (the existing Britain `naval_income` literal is *absorbed*, §5.1).
5. **Deterministic under `campaign_seed`.** Every roll (evasion, diversion, battle jitter)
   uses the AI-0b sha256 helpers. Same seed, same Trafalgar.
6. **Europe-scoped (N1).** Legacy fixture world authors no `navies` block; every legacy pin
   stays byte-identical.
7. **Authored, not derived (D7 discipline).** Fleet sizes, ports, dockyards are scenario
   content in `europe_1805.json`, validator-clamped — reviewable by reading the file.
   **Never** derived from the over-true `is_coastal` flag (§3.4).

---

## §3. The model

### 3.1 The fleet record

```python
world.fleets: Dict[str, dict]  # keyed by nation, present only for nations with authored navies
# {
#   "ships": int,            # ships-of-the-line equivalent (the only strength number)
#   "readiness": int,        # 40..100, the H2 mechanic
#   "posture": {"mode": "guard" | "blockade", "target": str | None},
#   "camp_turns": int,       # §5.3 Descent prep counter (France-side; 0 for everyone else)
#   "diversion_used": bool,  # §5.3 — one Grand Diversion per war
#   "window_turns": int,     # §5.3 — turns of open Channel remaining (0 = shut)
# }
```

**Effective strength** = `ships × readiness/100 × pooling`. Pooling: co-belligerent allies
and vassals whose fleets share the same mode+target add at **×0.8** each (H6). The pool is
computed at read time from diplomatic state — no pool object, nothing new serialized.

### 3.2 Authored 1805 navies (scenario `navies` block, validator-clamped)

| Nation | Ships | Readiness | Admiral (display only) | Ports weight | Dockyards (build sites) |
|--------|-------|-----------|------------------------|--------------|-------------------------|
| Britain | 100 | 100 | Nelson | — (island) | London, Wessex, Cornwall |
| France | 45 | 70 | Villeneuve | 4 | Brittany, Provence, Flanders, Bordelais |
| Spain | 30 | 65 | Gravina | 3 | Galicia + the Cádiz stand-in province (fixed at NV-0 against the map's southern carve) |
| Denmark | 18 | 80 | Bille | 2 | Copenhagen |
| Ottoman | 15 | 60 | — | 3 | Constantinople |
| Holland | 12 | 70 | Verhuell | 2 | Holland (the Texel) |
| Russia | 20 | 65 | Senyavin | 2 | Estonia |
| Portugal | 10 | 70 | — | 2 | Lisbon province |
| Sweden | 10 | 70 | — | 2 | Scania |
| Naples | 5 | 60 | — | 1 | Naples |

France's 70 readiness at boot **is** the Brest/Toulon rot (H2) — Britain's boot blockade
(§6) pins it there until the pressure lifts. Admirals are strings for dispatch flavor,
never objects. `ports` is the CS closure weight (§5.1) — authored precisely so the broad
`is_coastal` flag is never consumed (DEF-8 stays un-triggered). Numbers are gate-blessed
defaults (§12 Q6), in-band tunable.

### 3.3 Readiness (the whole H2 economy in three rules)

- Blockading fleet: holds 100 (sea time drills crews).
- Blockaded fleet (an enemy blockade-mode fleet targeting you at effective ≥ **1.25×**
  yours): −5/turn, floor 50. It may still sortie/fight — at that readiness.
- Otherwise (guard, uncontested): +5/turn toward 100.

### 3.4 What this deliberately does NOT read

The registry `is_coastal` flag (image-derived, over-true — Savoy and Anjou are flagged
coastal today). DEF-8's full re-derivation is **not** triggered: coverage keys off the 18
hand-authored `sea_links`, closure keys off authored `ports`, building keys off authored
`dockyards`. The one pre-existing consumer (Britain's `naval_income` coastal count,
saturating at 3) is absorbed by §5.1 and its read retired.

---

## §4. The four consequences

### 4.1 The crossing gate — kills "the Channel walks both ways"

Moving an army across a `sea_links` pair is free **unless a hostile fleet covers it**.
Coverage (derived at read time, ~10 fleets, GR8-trivial):

- A **guard** fleet covers every sea link touching its own nation's provinces.
- A **blockade** fleet covers every sea link touching its *target's* provinces.

One predicate — `naval.crossing_check(world, mover_nation, from, to)` — consulted at BOTH
movement seams (player executor validation + enemy-AI movement gates, the AI-3c pattern):

| Mover's effective ÷ best hostile coverage | Result |
|---|---|
| No hostile coverage | **free** (unchanged behavior — the Danish straits, Naples–Sicily, the Baltic at peace all keep working) |
| ≥ 1.25× | **passes** (Britain's descents at boot: 100 vs France's ~31.5 effective — H7 preserved) |
| < 1.25× (or ≥ 0.9× only during a §5.3 window) | **refused, honestly**: the message names both numbers and the two real answers (build/pool a fleet, or the expedition gamble). No dice on ordinary MOVE — a player never loses 40,000 men to a movement order |

Boot truths this single table produces: Spain can no longer walk to London (**the headline
regression test**); France cannot walk to London; Britain can still land in Flanders;
nothing changes on any uncontested link; the legacy world (no fleets) changes nowhere.

### 4.2 Blockade — the economic siege

A nation is UNDER BLOCKADE when a hostile blockade-mode fleet targets it at effective
≥ 1.25×. Effects, all ledger-legible:

- Trade income (`TRADE_INCOME` pairs) **×0.5** for the blockaded nation — applied at the
  `calculate_trade_income` chokepoint, shown as a signed **"Blockade"** Net component
  threaded the full EC-U2 ledger recipe (dispatch, ledger.py, strategic_ledger.gd,
  `NET_GOLD_COMPONENTS`).
- **Island clause (H5):** war-weariness +2/turn applies only to a blockaded nation whose
  `navies` entry authors `island: true` (Britain). Continental economies were
  import-resilient — that asymmetry is *why* the Continental System existed, and it keeps
  France's boot WE untouched.
- Britain's abstracted `naval_income` (absorbed into the navies block as authored
  `trade_dominance: 300`) scales by CS closure (§5.1) and suspends entirely while Britain
  is blockaded.

### 4.3 The expedition — the H4 verb

`naval_expedition(marshal, target_region, troops ≤ 15,000)` — a deliberate, priced gamble
from a friendly dockyard province to a coastal province with **no walkable route** (Ireland)
or across a covered link. Resolves the same turn (no in-flight limbo state):

- **Slip odds quoted before confirmation** (shown = applied): scale down with expedition
  size and hostile coverage-vs-escort ratio, up during a window (+25pp). Anchored, not
  formula-blessed: Bantry-scale Ireland run ≈ 55–65% at boot; a 15,000-man Channel run with
  no window ≈ ≤15% (anchor A3; exact curve fixed at NV-2 with the measured table in the
  landing record — the IGR-E discipline).
- **Success:** the marshal + corps land. Everything downstream is the existing land game —
  combat, capture-choice, EC-W1 Contributions against Britain's Irish income, supply
  attrition (Ireland has no depot: Humbert's fate is in the machine for free), glory,
  jealousy, the diorama.
- **Failure:** turned back (small attrition, readiness −10) or intercepted at sea on a
  decisive coverage ratio — corps loses 30%, and the fleet fights §4.4.
- Return trip is the same verb from the beachhead, same odds shape (stranding is real).

### 4.4 The fleet action — Trafalgar in one resolver

When escort meets interceptor, or a diversion fails (§5.3): `naval.resolve_fleet_action`
compares effective strengths (readiness already inside). Ship losses by ratio
(lanchester-lite): loser 20% + 15%×min(r−1, 1), winner 8%/max(r, 1), seeded jitter ±10%.
Ratio ≥ 1.5 → **decisive**: loser an extra −20%, the **"trafalgar"** dispatch beat fires
(named battle line, both admirals), loser war-weariness +8. No land-combat code is touched
— M1–M7 byte-identical **by construction**.

---

## §5. The three arcs (the "fun" clause)

### 5.1 Arc 1 — The Strangulation (CS 2.0)

Today's Continental System is a 200g pinch (`apply_continental_system`: −75g/member trade
cap). It becomes the H5 siege while keeping every existing seam:

- **Closure** = Σ authored `ports` of (France + vassals auto-joined + CS members + allies
  at war with Britain) ÷ Σ all continental `ports`. Existing membership machinery untouched
  (settlement clause writes members; puppet/satellite auto-join; autonomous drop-out; the
  coalition decay bonus stays).
- Britain's `trade_dominance` income scales **×(1 − closure)**, floor ×0.4 (smugglers and
  licences — the system leaked, historically and here).
- Britain war-weariness: closure ≥40% → +1/turn, ≥60% → +2, ≥80% → +3 — feeding the
  existing WE → `effective_peace_threshold` → sue-for-peace machinery. **This is the new
  win path: Britain can be brought to the table without a single soldier crossing water**
  (anchor A2).
- Ledger line: "The Continental System — 62% of the Continent's ports closed; Britain's
  war-weariness rising +2/turn." Neutral coercion (Portugal, the Peninsula trap) is
  **NV-D1, deferred with an owner** (§10).

### 5.2 Arc 2 — Free Ireland (the DEF-5 rider, contract already standing)

The owner row's completion definition is honored verbatim: *invade → clause → created
client with active `erin_free` deck*, GR5, `test_naval_free_ireland.py`.

1. **Invade:** §4.3 expedition into Ulster or Munster (both British at boot; Ireland's only
   map connection is Ulster↔Highlands, INSIDE Britain — which is why this was structurally
   impossible pre-naval and why the rider lives here).
2. **Clause:** holding both Irish provinces at war with Britain flips the availability gate
   on a `create_client` settlement clause for the authored formable **Ireland** — the NA-6c
   §11.4 machinery, zero new creation code. The Formables button lists Ireland with honest
   gate terms from day one ("Hold Ulster (held) · Hold Munster (not held) · At war with
   Britain (yes)").
3. **Created client:** carve pricing, CARVE_LOYALTY/patron seams, the Proclamation popup,
   campaign-log — all inherited. Authored: template `Ireland {regions: [Ulster, Munster]}`,
   deck `erin_free` (guard_neutrality Ulster+Munster, per the owner row), and the NA-6d
   per-formation `grudge_label: "The Irish Question"` — Britain's grudge machinery already
   knows what to do with it.
4. **GR5 pin:** the eligibility predicate is nation-neutral — the test proves an AI
   France-equivalent could run the same path (predicate-reachable, the AI-3r honest-zero
   discipline; no ambient AI expeditions in v1).

Free wins already in the machine: the liberator earns conquest glory (ladder/jealousy), his
corps starves without a depot unless supplied, estates on Irish soil hit the capture-choice
pipeline, and Britain's Irish income bleeds through EC-W1 while he stands there.

### 5.3 Arc 3 — The Descent on England (the campaign-defining gamble)

The full H3 chain, every step visible to both sides:

1. **The camp:** ≥40,000 men standing in an authored Channel-port province (Flanders,
   Artois, Normandy, Brittany) sets `camp_turns` ticking. At 2, the descent is *staged* —
   and Britain has seen it coming since turn one (**"boulogne_camp"** beat, Britain-side).
2. **Britain reacts (derived, §6):** posture flips blockade→guard, massing the Channel.
   Consequence the player can exploit: the blockade of Brest/Toulon LAPSES — French
   readiness starts climbing. The two-front tension is automatic, no scripting.
3. **The window** — any one of: **(a) The Grand Diversion** (`naval_diversion`, once per
   war): the fleet sails to draw the RN west — seeded 45%: success halves Britain's Channel
   coverage for 2 turns (`window_turns`, shown in the Admiralty block: "The Strait lies
   open — 2 turns"); failure = intercepted returning = §4.4 at bad readiness = **Trafalgar,
   as it happened**. **(b)** Win a fleet action outright. **(c)** Pooled parity (H6).
4. **The crossing:** during a window the §4.1 MOVE floor drops to **0.9×**. The boot math,
   worked: France 45×0.70 = 31.5; + Spain (30×0.65×0.8 = 15.6) + Batavia (12×0.70×0.8 =
   6.7) ≈ **53.8 effective** vs Britain's 100 — hopeless; vs **50 during a diversion
   window** → ratio 1.08 → **the Combined Fleet with a successful diversion opens the
   Strait, and nothing less does**. The mechanics *re-derive Napoleon's actual 1805 plan*,
   including why it needed Spain and why Trafalgar ended it.
5. **The landing:** London, its 25k tier garrison, and everything after is the existing
   land game (the DEF-6 pins flip consciously at NV-3, recorded).

Failure at any rung is a story, not a whiff: a lost diversion is a named Trafalgar beat
with war-weariness and a gutted fleet; history's actual outcome is one of the reachable
endings.

---

## §6. Enemy AI (GR5, derived, no new decision phase)

One cheap per-turn posture derivation in `naval.py` (iterates the ~10-entry fleets dict —
GR8-trivial), same executor verbs as the player:

- **Britain:** at war with France → `blockade France`; a staged descent camp or live window
  → `guard` (the §5.3.2 feedback). Peace → `guard`.
- **Everyone else:** `guard` home waters. Fleet-holding minors never bankrupt on upkeep
  because peacetime upkeep is zero (§7 N3).
- **AI build rung:** at war + treasury > 2× cost + a live naval want (blockaded, or its
  blockade outmatched) → `build_fleet` through the same priced verb (the P1.75 idiom).
- **No ambient AI expeditions/diversions in v1** — predicate-reachable, pinned honest
  (AI-3r §8.2 discipline), owner for ambition = NV-D8.

---

## §7. Numbers (gate-blessed defaults — §12 Q6; all in-band tunable)

| # | Constant | Default | Note |
|---|----------|---------|------|
| N1 | Authored navies | §3.2 table | Tier-1 content, fixed per seed (D7: no band, no variance) |
| N2 | `SHIP_COST` / `SHIP_BUILD_RATE` | 150g / 2 per turn (1 if every dockyard blockaded) | 45 ships to RN parity ≈ 6,750g + 23 turns → anchor A1 |
| N3 | `SHIP_UPKEEP_WAR` | 2g/ship/turn **at war only** | "Laid up in ordinary" at peace; France boot +90g/turn, Britain +200 (offset by trade_dominance); signed "Admiralty" Net component |
| N4 | `BLOCKADE_RATIO` | 1.25× effective | Same threshold as the crossing pass — one number to learn |
| N5 | Blockade effects | trade ×0.5 · island WE +2/turn · trade_dominance ×(1−closure), floor ×0.4 | §4.2/§5.1 |
| N6 | Readiness tick | ±5/turn, floor 50, cap 100 | §3.3 |
| N7 | `POOL_ALLIED` | 0.8 | H6 |
| N8 | Expedition | max 15,000 men · Ireland boot slip 55–65% · corps loss 30% on interception | anchors A3/A4; curve fixed at NV-2, measured table published |
| N9 | Diversion / window | 45% · 2 turns · MOVE floor 1.25×→0.9× · expedition +25pp | §5.3 |
| N10 | Fleet action | loser 20%+15%×min(r−1,1) · winner 8%/max(r,1) · decisive ≥1.5× → extra −20%, WE +8 | §4.4 |
| N11 | CS closure WE tiers | ≥40% +1 / ≥60% +2 / ≥80% +3 per turn | §5.1 |

**Falsifiable anchors** (the E1 discipline — measured at build, re-blessed consciously):

- **A1:** France cannot reach RN effective parity by building alone before turn ~25 at
  sustained spend.
- **A2:** ≥80% closure + blockade brings Britain to sue within 12–18 turns absent a
  continental war revival.
- **A3:** boot Ireland expedition (12k, unescorted) lands 55–65% of seeds; boot Channel
  crossing without a window: refused (not a roll).
- **A4:** the §5.3.4 worked example holds on the shipped scenario: Combined-Fleet pool +
  successful diversion ≥ 0.9× — and no proper subset of it is.
- **A5 (the headline):** `test_naval_channel_gate` — a hostile army can NEVER walk
  London↔Flanders below ratio; **Spain besieging London turn 5 becomes structurally
  impossible** while Britain's own boot descents still pass.
- **Boot deltas** (conscious, recorded at NV-0/NV-1): France −90 upkeep and a measured
  trade-cut under the boot blockade; `BASELINE_SERIES` re-records ONCE, attributed (the
  IGR-X4 discipline); M1–M7 byte-identical throughout (no navies in harness worlds).

---

## §8. Serialization & modding

- `world.fleets` — ONE new field: to_dict/from_dict (absent → `{}`),
  `SAVE_FORMAT_REFERENCE.md` row, `test_serialization_enforcement.py`.
- Scenario `navies` block + `Ireland` formable + `erin_free` deck: `modding/validator.py`
  schema (ships 0–150, readiness 40–100, ports ≥0, dockyards must be owned provinces,
  island bool) + `MODDING_FORMAT.md` rows.
- No new dialogue types, no popup-queue slots, no campaign-log renumbering beyond appended
  types (`trafalgar`, `blockade_begins/broken`, `expedition_landed/intercepted`,
  `boulogne_camp` — pins flip consciously at each slice).

## §9. Surfaces (the "usability" clause — all existing patterns)

- **Strategic Ledger — "THE ADMIRALTY" block:** own fleet (ships/readiness/posture/
  admiral), hostile blockade line with its cost, CS closure %, expedition/descent
  availability as honest gate terms IN ORDER (the §11.6 idiom).
- **Verbs** (4, through the shared executor + the full 12-step new-action checklist +
  corpus rows): `build_fleet` · `set_fleet_posture` · `naval_expedition` ·
  `naval_diversion`. Typed grammar: "build ships", "blockade Britain", "guard home
  waters", "land Soult in Munster with 12,000 men", "order the diversion".
- **Region panel:** "Lay down ships (150g)" chip on owned dockyard provinces.
- **Dispatch beats** (existing transport, NARRATION_EXEMPT additions): blockade begins/
  broken · expedition sailed/landed/intercepted · trafalgar · boulogne_camp.
- **War room:** one naval line per belligerent with a fleet. **Fog ruling (recorded):**
  fleet counts and postures are PUBLIC (period newspapers printed orders of battle; the
  §3.6 "no fog on dispositions" precedent). The only uncertainty is outcome timing —
  seeded, like everything else.
- **Godot cost:** ledger block + one chip + beat lines through existing renderers. No new
  scenes. XR-1 boot rule applies to any touched `.gd`.

## §10. Deferred, with owners (GR9 — none of these are promises in v1 copy)

| Row | What | Owner / landing | Test on landing |
|-----|------|-----------------|-----------------|
| NV-D1 | CS neutral coercion — the Portugal ultimatum, the Peninsula trap | NA follow-on gate (rides the NA-5 ultimatum machinery), post-NV-V | `test_cs_coercion.py` |
| NV-D2 | Copenhagen 1807 — Britain's pre-emptive fleet seizure of a neutral | Same NA follow-on gate (it is an agenda behavior, not a naval one) | seizure event pins |
| NV-D3 | Privateers / commerce-raid posture | Econ pass 3 successor, if the blockade layer measures thin | raid-income pins |
| NV-D4 | Naval battle presentation (diorama-class) | `BATTLE_DIORAMA_SPEC.md` Tier-B/C gate | visual pack |
| NV-D5 | Colonies / Egypt / the wider world | Post-EA table (ROADMAP) | — |
| NV-D6 | DEF-8 full `is_coastal` re-derivation | Stays at DEF-8, **not triggered** (§3.4 — v1 reads authored data only) | DEF-8's own row |
| NV-D7 | Weather/season on expeditions (Bantry's gale) | NV-V verdict decides if the odds curve needs it | curve re-bless |
| NV-D8 | Ambient AI expeditions/diversions (an AI France invading Ireland unprompted) | The first post-naval AI review (AI-V cadence) | predicate → ambient pins |

## §11. Build slices (each lands whole, suite-green, with its record)

- **NV-0 — The Admiralty (substrate):** `navies` authoring + validator + `world.fleets`
  boot + serialization + upkeep/ledger component + `build_fleet` + `set_fleet_posture` +
  readiness tick + boot postures (Britain blockades France) + N1 legacy/dormancy pins +
  corpus rows + the Admiralty ledger block. `test_naval_substrate.py`. BASELINE_SERIES
  conscious re-record lands HERE, once.
- **NV-1 — The Blockade War:** coverage/blockade predicate + trade/trade_dominance/WE
  coupling + CS 2.0 closure + beats + Britain sue-path measured (anchor A2) + boot-delta
  record. `test_naval_blockade_cs.py`.
- **NV-2 — Crossings & Free Ireland:** the §4.1 gate at BOTH movement seams + A5 headline
  pin + `naval_expedition` + fleet action resolver + measured odds table + Ireland
  formable/deck/grudge_label + Formables row + Proclamation reachability +
  **`test_naval_free_ireland.py`** (creation + deck activation + once-only, per the DEF-5
  row) + `test_naval_channel_gate.py`.
- **NV-3 — The Descent:** camp + Britain's derived reaction + diversion/window + the A4
  worked-example pin + England landing end-to-end + the trafalgar beat + DEF-6 pin flips.
  `test_naval_descent.py`.
- **NV-V — The Reckoning:** live playthrough of all three arcs, anchors A1–A5 measured in
  the played world, naval pillar scored, NV-D7/NV-D8 verdicts written. Closes DEF-5,
  DEF-6's "demoted to a naval-gated edge" arm, and the MAP plan rows.

## §12. THE GATE (user decisions — recommended defaults marked)

- **Q1 — Model granularity.** (a) **One national fleet record + posture [RECOMMENDED —
  the "it can be abstracted" directive made structural]** · (b) 2–3 stationed squadrons
  per nation · (c) fleet pieces on the map. (b)/(c) buy simulation nobody asked for and
  cost the lean budget.
- **Q2 — v1 scope.** (a) **All three arcs, England as the final slice NV-3 [RECOMMENDED]**
  · (b) Strangulation + Ireland only, Descent to v1.1. Note: NV-3 may slip without
  orphaning anything — NV-0..2 already close DEF-5's contract and the believability
  defect; if it slips, its §10-style owner row is written at that moment.
- **Q3 — CS neutrals.** (a) **Vassals/allies/clause members only; neutral coercion stays
  NV-D1 [RECOMMENDED]** · (b) full coercion arc in v1 (drags NA-5 machinery into scope).
- **Q4 — Fleet fog.** (a) **Public counts/postures [RECOMMENDED — §9 ruling]** · (b)
  fogged behind port intel (adds intel plumbing for information the era's newspapers
  printed).
- **Q5 — EA scope.** ROADMAP currently lists naval as post-EA; the played-world defect
  says otherwise. (a) **Promote naval v1 into EA scope, amending ROADMAP [RECOMMENDED]**
  · (b) keep post-EA and accept the Channel absurdity through EA.
- **Q6 — The numbers.** Bless N1–N11 + anchors A1–A5 as defaults (in-band tunable;
  structural changes escalate) [RECOMMENDED].

---

*Companion reading: `MAP_IMPLEMENTATION_PLAN.md` DEF-5/6/7/8 (the map contracts this spec
consumes), `NATION_AGENDAS_SPEC.md` §11.4/§20/§21 (the creation machinery Ireland rides),
`ECONOMY_REVISIT_SPEC.md` + EC-W (the ledger recipe every naval component threads).*
