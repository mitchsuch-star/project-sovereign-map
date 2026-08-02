# NAVAL_SPEC.md — "The Wooden Wall": the naval abstraction, the blockade war, and the liberation of Ireland (DEF-5)

> **v1.0 — AUTHORED August 1, 2026. STATUS: DRAFT FOR USER GATE (§12).**
> **v1.0.1 — August 2, 2026, pre-gate Q&A amendments (user questions):** the §3.2 admiral-talent
> ruling (structural, not a stat — with the one-number option recorded), the §4.4 trigger
> enumeration (battles fire in exactly two situations, never ordered), the §9 **Crossings
> verdict line** + `strait_open`/`strait_shut` flip beats (closes the "do we SEE when the
> Channel becomes crossable?" gap), and gate **Q7** (texture options, default OUT).
> **v1.0.2 — August 2, 2026 (user: "it should be tough to increase fleet"):** the §3.5
> **three-brakes** statement of record (time is the wall, gold is deliberately the weakest
> brake), **green-crew dilution** (new ships join at readiness 40 — crash-building buys
> hulls, only sea-time buys a navy), and the **no-prize ruling** (conquering a dockyard
> grants the YARD, never ships; an eliminated nation's fleet disperses; seizure = the
> NV-D2 Copenhagen family). The fast road to naval weight is DIPLOMACY (§5.3 pooling),
> with its authored discount — exactly the historical Combined-Fleet answer.
> **v1.0.4 — August 2, 2026, THE ASSURANCE PASS (user-directed; record = §13.6):** the §9
> **legibility contract table** — one named answer per naval state to "where do I SEE it?"
> — adding the two MAP render arms the spec had missed (sea-link verdict tint + port
> blockade glyph: the map is where movement decisions are made) and the Admiralty
> **Blockade board** (who blockades whom, effects quoted both directions); the §10 GR9
> tightening (every deferral row now carries a falsifiable test — NV-D5 gained the
> copy-scan pin; the no-player-facing-promise rule stated as the standing preamble); §8's
> appended campaign-log type list reconciled with the beats §9 actually names.
> **v1.0.3 — August 2, 2026, THE CODE-GROUNDED FEASIBILITY & COST REVIEW (user-directed;
> full record = §13):** every claimed seam verified against master and named; **measured
> boot economy** (France net +2,107/turn) re-blessed `SHIP_COST` 150→**400g** (a ship must
> out-price a fortification, not undercut a depot); **shipyards confirmed NOT a building**
> — the dockyard ruling is recorded (§13.3, deferral NV-D9); and TWO structural
> corrections the arithmetic forced: the blockade is now **untargeted** (covers/pins ALL
> at-war enemies — the RN's simultaneous Brest/Ferrol/Cadiz/Texel watch; a targeted
> blockade let Spain drill to 100 untouched and broke anchor A4) and readiness gained the
> **war drill ceiling 75** vs a superior hostile fleet (unbounded recovery let the Descent
> oscillate open whenever Britain massed the Channel). §5.3's worked math restated at the
> ceiling; A4 holds; the boot-rush variant recorded as live-by-design at the diversion's
> 45%. Nothing in this
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
#   "posture": "guard" | "blockade",   # v1.0.3: UNTARGETED — blockade covers all at-war enemies
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
| Spain | 30 | 65 | Gravina | 3 | Galicia (Ferrol) + Toledo (the Cádiz stand-in — v1.0.3: the map's southern carve is Morocco/Aragon/Leon/Galicia/La Mancha/Asturias/Toledo/Madrid/Balearics; Toledo is the southern seat) |
| Denmark | 18 | 80 | Bille | 2 | Copenhagen |
| Ottoman | 15 | 60 | — | 3 | Constantinople |
| Holland | 12 | 70 | Verhuell | 2 | Holland (the Texel) |
| Russia | 20 | 65 | Senyavin | 2 | Estonia |
| Portugal | 10 | 70 | — | 2 | Lisbon (province verified on the map) |
| Sweden | 10 | 70 | — | 2 | Scania |
| Naples | 5 | 60 | — | 1 | Naples |
| *ports-only rows (v1.0.3)* | 0 | — | — | Austria 1 (Trieste) · Prussia 1 · Hanover 1 · KingdomOfItaly 1 · PapalStates 1 | — (no fleet record created at ships 0; the row exists so §5.1's closure denominator is authored, not derived) |

France's 70 readiness at boot **is** the Brest/Toulon rot (H2) — Britain's boot blockade
(§6) pins it there until the pressure lifts. Admirals are strings for dispatch flavor,
never objects. `ports` is the CS closure weight (§5.1) — authored precisely so the broad
`is_coastal` flag is never consumed (DEF-8 stays un-triggered). Numbers are gate-blessed
defaults (§12 Q6), in-band tunable.

**The admiral-talent ruling (v1.0.1, recorded):** British admiral quality is carried
STRUCTURALLY, not as a stat — the 100-ship mass, boot readiness 100 vs France's 70, and
the H2 asymmetry (blockade duty trains the blockader while the blockaded rots) *are* the
talent model. That is the historically honest attribution: Trafalgar's edge was sea-time
and gunnery cadence, not a hero bonus — Nelson's genius was knowing his fleet could cash
a melee the enemy's couldn't. So "Nelson" stays a display string, and the system already
produces his outcomes. If the gate wants the *name* to carry a number anyway, the recorded
option is ONE authored `admiral_quality` multiplier (Britain 1.1, France 0.95, default
1.0) applied in §4.4 fleet actions only — never coverage — gate **Q7**, default OUT.

### 3.3 Readiness (the whole H2 economy in four rules — v1.0.3 shape)

- Blockading fleet: holds 100 (sea time drills crews).
- **The blockade is untargeted (v1.0.3):** a blockade-mode fleet covers and pins EVERY
  nation its owner is at war with, judged per target by the same ratio — blockaded means
  *some at-war enemy in blockade mode has effective ≥ 1.25× yours*. This is what the RN
  actually did (Brest, Ferrol, Cadiz and the Texel watched simultaneously — the reason
  Britain carries 100 hulls), and it closes the hole the review found: a France-targeted
  blockade left Spain free to drill to 100 and walk the §5.3 math open.
- Blockaded fleet: −5/turn, floor 50. It may still sortie/fight — at that readiness.
- Otherwise: +5/turn — toward **`NAVY_DRILL_CEILING = 75` while at war with a superior
  hostile fleet** (crews drill in the roadstead; only sea room makes a 100), toward 100
  in peace or for the superior fleet itself. v1.0.3: without this ceiling, Britain
  massing the Channel against a staged descent lapsed its own blockade and let the
  Combined Fleet recover to parity — the Descent oscillated open by procedure, no gamble
  needed.
- **Green crews (v1.0.2):** newly commissioned ships join at readiness **40** and fold in
  by weighted average. At the honest drip (2/turn into 45 hulls) the dilution is gentle;
  a sustained crash program visibly drags the fleet down toward green — you can see your
  navy getting bigger and worse at once, which is Villeneuve's Spanish problem made
  mechanical.
### 3.4a Ships change hands by NO other door (v1.0.2 ruling)

Fleets are national, never provincial. Conquering a dockyard province grants the **yard**
(a build site) — never ships. An eliminated nation's fleet **disperses** (removed; no
prize-taking in v1 — seizing an intact fleet is the NV-D2 Copenhagen family, owned there).
Vassalization/alliance contributes ships only through §3.2 pooling at ×0.8. Net: the fast
road to naval weight is diplomatic (Spain, the Batavian squadron), priced at the allied
discount and the partner's own readiness — the Combined Fleet, with its historical flaws
intact.

### 3.5 The three brakes on fleet growth (v1.0.2 statement of record)

Gold is deliberately the **weakest** brake. In order of bite: **(1) TIME** — the 2/turn
rate cap means 45→90 ships is ~23 turns *minimum* regardless of treasury (anchor A1: you
cannot crash-build a navy, which is the fact Napoleon ran into); **(2) PRESSURE** — a
blockaded nation builds at 1/turn, so escaping RN pressure is a prerequisite of
out-building it, not a result; **(3) WORK-UP** — green crews (§3.3) mean new hulls arrive
at 40 readiness and only uncontested sea-time turns them into a navy. Cost (**400g** + 1
admin AP per ship — the §13.2 measured re-bless; the full-rate drip is ~38% of France's
boot net) makes the program a real budget rivalry with recruitment without ever becoming
the wall.

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
- A **blockade** fleet covers every sea link touching the provinces of ANY nation its
  owner is at war with (v1.0.3 — untargeted, the simultaneous watch).

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

A nation is UNDER BLOCKADE when an at-war enemy in blockade mode has effective ≥ 1.25×
its own (per-target test, untargeted posture — §3.3). Effects, all ledger-legible:

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

**Triggers, enumerated (v1.0.1 — the complete list):** a fleet action fires in exactly
two situations, both "you gambled and lost the roll" — **(1)** an expedition fails its
slip check and is intercepted (§4.3); **(2)** a Grand Diversion fails and is caught
coming home (§5.3). It is never orderable, never ambient, and the AI never initiates one
in v1 — a campaign sees a handful at most, each one a named event. (A deliberate "sortie
/ offer battle" verb is the recorded gate option **Q7**, default OUT: historically the RN
sought battle and France's whole problem was declining it — the collision model carries
that truth.)

When those collide: `naval.resolve_fleet_action`
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
  coalition decay bonus stays). **The boot fact (v1.0.3, computed from the §3.2 authored
  weights):** France 4 + Holland 2 + KingdomOfItaly 1 + at-war-with-Britain Spain 3 = 10
  of 26 continental ports ≈ **38% — one diplomatic move short of the first WE tier**. The
  System opens as an achievable early goal, not a distant abstraction.
- Britain's `trade_dominance` income scales **×(1 − closure)**, floor ×0.4 (smugglers and
  licences — the system leaked, historically and here).
- Britain war-weariness: closure ≥40% → +1/turn, ≥60% → +2, ≥80% → +3 — feeding the
  existing WE → `effective_peace_threshold` → sue-for-peace machinery. **This is the new
  win path: Britain can be brought to the table without a single soldier crossing water**
  (anchor A2). It compounds for free (v1.0.3): Britain already boots at WE 60
  (`world_state.py:1354`), and the EC-W2 war-effort skim is treasury × WE — so every
  closure tier also deepens Britain's own gold bleed through machinery that already
  ships.
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
   Consequence the player can exploit: the blockade of Brest/Toulon LAPSES — French and
   allied readiness starts climbing, but only to the war drill ceiling of 75 (§3.3); the
   two-front tension is automatic, no scripting, and waiting alone can never open the
   Strait (v1.0.3 — the oscillation hole is closed).
3. **The window** — any one of: **(a) The Grand Diversion** (`naval_diversion`, once per
   war): the fleet sails to draw the RN west — seeded 45%: success halves Britain's Channel
   coverage for 2 turns (`window_turns`, shown in the Admiralty block: "The Strait lies
   open — 2 turns"); failure = intercepted returning = §4.4 at bad readiness = **Trafalgar,
   as it happened**. **(b)** Win a fleet action outright. **(c)** Pooled parity (H6).
4. **The crossing:** during a window the §4.1 MOVE floor drops to **0.9×**. The math,
   worked at the v1.0.3 drill ceiling (fleets recovered to 75 while Britain guards):
   France 45×0.75 = 33.75; + Spain (30×0.75×0.8 = 18.0) + Batavia (12×0.75×0.8 = 7.2) ≈
   **59 effective** vs Britain's 100 — hopeless (0.59); vs **50 during a diversion
   window** → ratio **1.18** → the Strait opens at the 0.9× floor. Without Spain the
   pool is 41 → 0.82 — **shut. The Combined Fleet with a successful diversion opens the
   Strait, and nothing less does.** (The pre-rot boot-rush variant — readiness ~70/65/70
   before the blockade bites → ≈54 vs 50 = 1.08 — is also live behind the diversion's
   45%, telegraphed two turns by the camp: accepted as the H3 truth, since this is
   precisely what Napoleon believed possible in the summer of 1805; measured at NV-3.)
   The mechanics *re-derive the actual 1805 plan*, including why it needed Spain and why
   Trafalgar ended it.
5. **The landing:** London, its 25k tier garrison, and everything after is the existing
   land game (the DEF-6 pins flip consciously at NV-3, recorded).

Failure at any rung is a story, not a whiff: a lost diversion is a named Trafalgar beat
with war-weariness and a gutted fleet; history's actual outcome is one of the reachable
endings.

---

## §6. Enemy AI (GR5, derived, no new decision phase)

One cheap per-turn posture derivation in `naval.py` (iterates the ~10-entry fleets dict —
GR8-trivial), same executor verbs as the player:

- **Britain:** at war → `blockade` (untargeted, v1.0.3 — the simultaneous watch pins
  every enemy fleet); a staged descent camp or live window → `guard` (the §5.3.2
  feedback). Peace → `guard`.
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
| N2 | `SHIP_COST` / `SHIP_BUILD_RATE` / `NEW_SHIP_READINESS` | **400g** + 1 admin AP / 2 per turn (1 if every dockyard blockaded) / joins at 40 | §13.2 measured re-bless (a ship out-prices a fortification, never undercuts a depot); 45 ships to RN parity ≈ 18,000g + 23 turns → anchor A1; the §3.5 three brakes |
| N3 | `SHIP_UPKEEP_WAR` | 2g/ship/turn **at war only** | "Laid up in ordinary" at peace; France boot +90g/turn, Britain +200 (offset by trade_dominance); signed "Admiralty" Net component |
| N4 | `BLOCKADE_RATIO` | 1.25× effective, judged per at-war target (untargeted posture, v1.0.3) | Same threshold as the crossing pass — one number to learn |
| N5 | Blockade effects | trade ×0.5 · island WE +2/turn · trade_dominance ×(1−closure), floor ×0.4 | §4.2/§5.1 |
| N6 | Readiness tick | ±5/turn, floor 50; recovery caps at `NAVY_DRILL_CEILING=75` while at war with a superior hostile fleet, 100 otherwise (v1.0.3) | §3.3 |
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
- **A4 (restated v1.0.3):** the §5.3.4 worked example holds on the shipped scenario AT
  THE DRILL CEILING: Combined-Fleet pool + successful diversion ≥ 0.9× (measured shape:
  59 vs 50 = 1.18) — and no proper subset of it is (no-Spain 41 → 0.82, shut). The
  pre-rot boot-rush at ~1.08 is live-by-design behind the 45% diversion, camp-telegraphed.
- **A5 (the headline):** `test_naval_channel_gate` — a hostile army can NEVER walk
  London↔Flanders below ratio; **Spain besieging London turn 5 becomes structurally
  impossible** while Britain's own boot descents still pass.
- **Boot deltas** (conscious, MEASURED — §13.2): France −175 trade (350 × 0.5 under the
  boot blockade) − 90 ship upkeep ≈ **−265/turn ≈ 12.6% of the measured +2,107 net** —
  re-blessed at NV-1 with the E1-family discipline; `BASELINE_SERIES` re-records ONCE,
  attributed (the IGR-X4 discipline); M1–M7 byte-identical throughout (no navies in
  harness worlds).

---

## §8. Serialization & modding

- `world.fleets` — ONE new field: to_dict/from_dict (absent → `{}`),
  `SAVE_FORMAT_REFERENCE.md` row, `test_serialization_enforcement.py`.
- Scenario `navies` block + `Ireland` formable + `erin_free` deck: `modding/validator.py`
  schema (ships 0–150, readiness 40–100, ports ≥0, dockyards must be owned provinces,
  island bool) + `MODDING_FORMAT.md` rows.
- No new dialogue types, no popup-queue slots, no campaign-log renumbering beyond appended
  types (`trafalgar` · `blockade_begins`/`blockade_broken` · `expedition_landed`/
  `expedition_intercepted` · `boulogne_camp` · `strait_open`/`strait_shut` (v1.0.1) ·
  `cs_tier_shift` (v1.0.4) — pins flip consciously at each slice).

## §9. Surfaces — the legibility contract (the "usability" clause — all existing patterns)

**The contract table (v1.0.4): every naval state has ONE named answer to "where do I see
it?", every figure shown is the figure applied, and every surface is an existing pattern.**

| Naval state | Where the player sees it |
|---|---|
| **Can this army cross this link?** | **The map**: the drawn dashed sea-link routes tint by live verdict — normal = open/uncontested · crimson + anchor glyph = shut to your movement · gold = window open — so the answer is visible where the move is being considered · the Admiralty **Crossings verdict line** (ratio quoted) · and if a move is ordered anyway, the refusal names both numbers |
| **Is a nation under blockade — and where?** | **The map**: a blockade glyph on the blockaded nation's dockyard provinces (the watchtower-glyph idiom) · the Admiralty **Blockade board** — one row per blockaded nation, blockader named, effects quoted ("France — trade halved (−175/turn); the fleet pinned in port") · the region panel info block on any of its coastal provinces · the war-room belligerent line |
| **What is MY blockade doing to them?** | The Blockade board's own-squadron rows ("Our squadrons close Britain's ports — their trade halved, weariness +2/turn") · the enemy's weariness row in the war-detail popup (the AI-4c labelled row, already rendered) |
| **What is being blockaded costing ME?** | The signed **"Blockade"** Net component in the strategic ledger and the dispatch treasury delta — the EC-U2 recipe, same family as Contributions/War Effort |
| **The Continental System** | Admiralty closure % · the ledger CS line naming the live tier ("62% of the Continent's ports closed — Britain's weariness +2/turn") · the `cs_tier_shift` beat when a tier is crossed |
| **The window / the camp** | `strait_open`/`strait_shut` beats · the WINDOW verdict row with its countdown · the gold map tint; the camp: the French side reads the counter in the Admiralty, Britain's side gets the `boulogne_camp` beat |
| **Expedition / descent availability** | Honest gate terms IN ORDER in the Admiralty (the §11.6 idiom) · odds quoted on the confirm (shown = applied) |
| **AI symmetry** | The same predicate gates AI movement silently; a notable AI turn-back at a strait renders as an ordinary campaign-log line, never a popup |

- **Strategic Ledger — "THE ADMIRALTY" block:** own fleet (ships/readiness/posture/
  admiral), the **Blockade board** (both directions, per the contract table), CS closure
  %, expedition/descent availability as honest gate terms IN ORDER (the §11.6 idiom).
- **The Crossings verdict line (v1.0.1):** the Admiralty block lists every sea link
  touching the player's provinces or armies with a live verdict quoting the SAME ratio
  the §4.1 predicate reads (shown = applied): "OPEN — uncovered" / "OPEN — ours 1.3×
  theirs" / "SHUT — the Royal Navy at 3.2× (blockade)" / "WINDOW — open 2 more turns".
  When a verdict FLIPS, the **`strait_open` / `strait_shut` dispatch beats** fire
  (state-change only, never per-turn repetition; beat-exempt from the narration cap like
  the others). The player never has to *derive* crossability from fleet arithmetic — the
  game announces the moment the Channel opens, which is the §5.3 window's whole drama.
- **Verbs** (4, through the shared executor + the full 12-step new-action checklist +
  corpus rows): `build_fleet` · `set_fleet_posture` · `naval_expedition` ·
  `naval_diversion`. Typed grammar: "build ships", "blockade Britain", "guard home
  waters", "land Soult in Munster with 12,000 men", "order the diversion".
- **Region panel:** "Lay down ships (400g)" chip on owned dockyard provinces (the price
  quoted from the live constant, never hardcoded — the honest-chip idiom); the info block
  on any coastal province of a blockaded nation states the blockade and its effect
  (fog-clean — Q4 public data).
- **Dispatch beats** (existing transport, NARRATION_EXEMPT additions): blockade begins/
  broken · expedition sailed/landed/intercepted · trafalgar · boulogne_camp ·
  strait_open/strait_shut · cs_tier_shift — all state-change-only, never per-turn.
- **War room:** one naval line per belligerent with a fleet. **Fog ruling (recorded):**
  fleet counts and postures are PUBLIC (period newspapers printed orders of battle; the
  §3.6 "no fog on dispositions" precedent). The only uncertainty is outcome timing —
  seeded, like everything else.
- **Godot cost:** ledger block + one chip + beat lines + the two map render arms
  (sea-link verdict tint + port blockade glyph) on the EXISTING map layers — the data
  rides the map summary payload the client already consumes. No new scenes. XR-1 boot
  rule applies to any touched `.gd`.

## §10. Deferred, with owners (GR9 — none of these are promises in v1 copy)

**The standing rule (v1.0.4, audited — §13.6):** no row below appears in v1 player-facing
copy — no disabled affordances, no "coming soon" strings, no dead references; refusal and
advisory text names present-tense facts only. Every row carries an owner, a landing, and
a falsifiable test.

| Row | What | Owner / landing | Test on landing |
|-----|------|-----------------|-----------------|
| NV-D1 | CS neutral coercion — the Portugal ultimatum, the Peninsula trap | NA follow-on gate (rides the NA-5 ultimatum machinery), post-NV-V | `test_cs_coercion.py` |
| NV-D2 | Copenhagen 1807 — Britain's pre-emptive fleet seizure of a neutral | Same NA follow-on gate (it is an agenda behavior, not a naval one) | seizure event pins |
| NV-D3 | Privateers / commerce-raid posture | Econ pass 3 successor, if the blockade layer measures thin | raid-income pins |
| NV-D4 | Naval battle presentation (diorama-class) | `BATTLE_DIORAMA_SPEC.md` Tier-B/C gate | visual pack |
| NV-D5 | Colonies / Egypt / the wider world — referenced NOWHERE in v1 copy | Post-EA expansion table (ROADMAP) — its own future gate defines scope + completion | copy-scan pin at NV-0: no colonial strings ship on any v1 surface |
| NV-D6 | DEF-8 full `is_coastal` re-derivation | Stays at DEF-8, **not triggered** (§3.4 — v1 reads authored data only) | DEF-8's own row |
| NV-D7 | Weather/season on expeditions (Bantry's gale) | NV-V verdict decides if the odds curve needs it | curve re-bless |
| NV-D8 | Ambient AI expeditions/diversions (an AI France invading Ireland unprompted) | The first post-naval AI review (AI-V cadence) | predicate → ambient pins |
| NV-D9 | A buildable "Naval Yard" structure — unlocks a SITE where none is authored, NEVER raises the national build rate (§13.3: the rate cap is the time wall and stays national) | Econ pass 3 successor, opened only if NV-V measures site scarcity as dull | yard-site pins |

## §11. Build slices (each lands whole, suite-green, with its record)

- **NV-0 — The Admiralty (substrate):** `navies` authoring + validator + `world.fleets`
  boot + serialization + upkeep/ledger component + `build_fleet` + `set_fleet_posture` +
  readiness tick + boot postures (Britain blockades — untargeted, §3.3) + N1 legacy/dormancy pins +
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
- **Q7 — Texture options (v1.0.1), both DEFAULT OUT [RECOMMENDED: neither in v1].**
  (a) `admiral_quality` one-number multiplier in fleet actions (§3.2 ruling — the
  structural model already carries British talent); (b) a deliberate "sortie / offer
  battle" verb (§4.4 — the collision model carries the RN-seeks/France-declines truth).
  Re-open either at NV-V only if the played battles measure flat.

---

## §13. Feasibility & cost review (v1.0.3 — code-grounded, docs-only; August 2, 2026)

User-directed pre-gate pass: *"evaluate cost; see if shipyards are even a building; fully
review the spec for feasibility."* Every number below was measured on master (world booted
via `WorldState.from_scenario` on the shipped `europe_1805.json`, historical seed).

### 13.1 Measured boot economy (what costs are priced against)

**France:** income 3,400 + trade 350 + admin 50 + vassal tribute 937 ≈ 4,737 gross;
upkeep 2,630 (incl. the Grande-Armée surcharge 882) → **net +2,107/turn**, treasury 800.
**Britain:** 11 provinces at 1,500 income + trade 350 + the 300 naval read ≈ 2,150 gross,
treasury 2,000 — and **war_exhaustion already boots at 60** (`world_state.py:1354`), so
the §5.1 closure tiers push an already-weary belligerent, not a fresh one.

### 13.2 The cost re-bless (150 → 400g)

At 150g a ship-of-the-line undercut a supply depot (300g) and cost less than half a
fortification (400g) — wrong against history and against the game's own price ladder
(buildings 250–400g · war-priced recruits · marshal commissions 3,500–6,000g). Re-blessed
**`SHIP_COST` = 400g** (the fortification price, top of the building band): the full-rate
drip is 800g/turn ≈ **38% of France's measured net** — a genuine budget rivalry with
recruitment — and the 45-ship parity program ≈ 18,000g + 23 turns. Time remains the
binding brake (§3.5); the gold brake now at least engages. Upkeep stands at 2g/ship at
war (France 90, Britain 200 — Britain's fully offset by the absorbed `trade_dominance`
300). **Boot delta, concrete:** the boot blockade costs France −175 trade (measured 350 ×
0.5) − 90 upkeep ≈ **−265/turn ≈ 12.6% of net** — conscious, in-band, re-blessed at NV-1.

### 13.3 Shipyards are NOT a building today — the ruling of record

Verified: `BUILDING_TYPES` (`economy_executor.py`) is supply_depot 300g/2t · fortification
400g/3t · training_ground 250g/2t · watchtower 250g/2t — **no naval structure exists**,
and buildings are REGION-SLOTTED with per-region construction timers while `build_fleet`
is a NATIONAL order. The ruling: dockyards stay **authored scenario data**
(`navies.dockyards`), deliberately OUTSIDE the building family — a buyable yard would
sell the §3.5 time wall, because the build rate is national, not per-yard. The
region-panel chip on a dockyard province is a convenience entry to the national order and
consumes no building slot. **NV-D9** (§10) owns the only sanctioned future: a buildable
Naval Yard that unlocks a SITE, never rate.

### 13.4 Seam verification (every load-bearing claim → the code that carries it)

| Claim | Seam, verified on master | Verdict |
|---|---|---|
| §4.1 crossing gate | `movement_executor.py` adjacency validation (the `adjacent_regions` membership checks, e.g. :948 "it is not adjacent") + the strategic first-step gates (the CR-5 `_inferred_first_step_gate` precedent) + enemy-AI movement scoring | FITS — one predicate at named seams |
| §4.2 trade ×0.5 | `diplomacy.calculate_trade_income` (:9158) is the single chokepoint (ledger, dispatch, income phase all call it) | FITS |
| naval_income absorption | `world_state.py:4400` (income) + `diplomacy.py:3128` (power score) — both sites found; both retire onto authored `trade_dominance` | FITS |
| WE coupling | `world.war_exhaustion: Dict[str,int]` 0–200 (`world_state.py:1016`) + the EC-W2 treasury skim + `effective_peace_threshold` (`ai_diplomacy.py:500`) | FITS — and compounds free: closure raises Britain's WE, WE scales Britain's war-effort gold bleed |
| "Admiralty"/"Blockade" ledger rows | the SC-33 `NET_GOLD_COMPONENTS` guard + the `ledger.py` economy dict (war_effort/contributions siblings measured live this pass) | FITS — two more family members |
| §5.2 Ireland | `formations.py` catalogue (`formable_nations` serialized on the world; template = provinces + display_name + optional flag/aggrieved, class-blind identity normalization) + the `create_client` clause | FITS — Ireland is one authored row |
| Dispatch beats | `queue_dispatch_event(world, type, payload, "always")` — verified live inside `apply_continental_system` | FITS |
| `world.fleets` name | zero collisions in `backend/` (measured) | CLEAN |
| Expedition marshal placement | precedent: captured marshals are relocated cross-map by executor code today | FITS |
| Geography | Portugal's `Lisbon` province exists; Spain's southern carve has no Andalusia → Toledo named the Cádiz stand-in (§3.2) | CORRECTED IN PLACE |

### 13.5 The two structural corrections the arithmetic forced

1. **The untargeted blockade** (§3.1/§3.3/§4.1/§6): with a France-targeted blockade,
   Spain and the Batavian squadron drilled to 100 unmolested and the pooled §5.3 math
   opened the Channel with no gamble at all — anchor A4 was FALSE as first written.
   Untargeted matches what the RN actually did (Brest, Ferrol, Cadiz, the Texel — watched
   simultaneously; the reason Britain carries 100 hulls) and makes the record SMALLER
   (the target field is deleted).
2. **The war drill ceiling** (`NAVY_DRILL_CEILING = 75`, §3.3): unbounded +5/turn
   recovery meant Britain's own defensive reaction (guard on a staged camp) un-pinned
   every enemy fleet toward 100 — stage a camp, wait, and the Strait opened by procedure.
   With the ceiling the §5.3.4 math holds at steady state (pool 59 vs windowed 50 = 1.18
   ≥ 0.9; the no-Spain subset 41 → 0.82, shut), and the pre-rot boot-rush (~1.08) stays
   live strictly behind the diversion's 45% — recorded as the H3 truth, measured at NV-3.

**Verdict: FEASIBLE as specced.** No claim in §3–§9 requires machinery that does not
exist; every coupling lands on a verified seam; the two holes the review found are closed
above; costs are now priced against measured income rather than assumption. The remaining
unknowns are tuning (the expedition odds curve, the CS pace), and both are owned by their
slices' measured-table discipline.

### 13.6 The GR9 + legibility assurance pass (v1.0.4 — user-directed)

**Deferral audit — CLEAN.** Every deferral-family phrase in the body ("v1", "deferred",
"stays", "owned", "may slip") was swept: each resolves to an owned §10 row or an explicit
§12 gate option (Q2's slip clause writes its owner row at decision time; Q7's texture
options re-open only at NV-V). All nine §10 rows now carry owner + landing + a
falsifiable test — NV-D5, the one bare row, gained the copy-scan pin. The standing rule
is stated in the §10 preamble: **nothing deferred appears in v1 player-facing copy** — no
disabled affordances, no "coming soon" strings; refusals name present-tense facts (a
crossing is refused because "the Royal Navy commands the Strait — 100 sail against 31",
never because a feature is missing).

**Legibility audit — one gap found and closed.** The §9 surfaces were ledger-complete but
MAP-silent: the player weighs movement on the war table, and the spec's only crossing
answers lived in the Admiralty text block and the refusal message. Closed by the two map
render arms (sea-link verdict tint + port blockade glyph, riding the existing map summary
payload) and the Admiralty **Blockade board** (who blockades whom, effects quoted in both
directions). The §9 contract table is now the normative answer to "where do I see it" for
every naval state; §8's appended campaign-log type list was reconciled with the beats §9
actually names (`strait_open`/`strait_shut`, `cs_tier_shift` added).

---

*Companion reading: `MAP_IMPLEMENTATION_PLAN.md` DEF-5/6/7/8 (the map contracts this spec
consumes), `NATION_AGENDAS_SPEC.md` §11.4/§20/§21 (the creation machinery Ireland rides),
`ECONOMY_REVISIT_SPEC.md` + EC-W (the ledger recipe every naval component threads).*
