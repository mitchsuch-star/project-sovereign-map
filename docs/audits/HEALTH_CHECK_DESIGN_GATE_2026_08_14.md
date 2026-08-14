# The Health-Check Design Gate — August 14, 2026

> **Status: ✅ GATE HELD August 14, 2026 under the user's delegated grant**
> ("make decision on design gaps … assure these session are next up and
> ordered well"). **This document is the authoritative gate record and build
> contract for row HC.** The seven design gaps come from the Aug 14
> whole-game health check (record = `docs/STATUS.md` health-check entry;
> evidence = the six-agent audit fleet's integration report). Six are RULED
> here at recommended defaults; ONE (seasons) is deliberately NOT ruled —
> it is promoted to its own user gate, because it is the largest balance
> change since naval and the delegation is read as not covering it.
>
> **Blessed numbers in this record are in-band tunable; structural changes
> escalate.** Every slice ends on the standing gates (suite green, ruff,
> parse harness EXIT=0 where `.gd` is touched, boot smoke, M1–M7 +
> `BASELINE_SERIES` byte-identity checked — HC-4 is the ONE slice allowed a
> conscious re-record, with flip-experiment attribution).

---

## §1 The rulings, one line each

| # | Gap | Ruling |
|---|-----|--------|
| HC-1 | Naval dominance invisible to the war score | **BUILD** — "The Silver Blockade": a capped signed war-score component on the PT-J2 ledger substrate |
| HC-2 | Campaign ledgers feed no narration | **BUILD** — stateless war-room + battle-report lines reading the ledger the war-detail popup already shows |
| HC-3 | Glory never reaches a foreign court | **BUILD the flavor half** (display-only, Voice Bible discipline); the mechanical acceptance term is **DEFERRED with an owner** (`DESIGN_REFINEMENT.md` HC-D1 → the Victory & Objectives Pass gate) |
| HC-4 | RN shore-supply interdiction absent + AI expedition AP asymmetry | **BUILD BOTH as one naval-balance slice** — the lifeline arm reuses the existing 1.5× home-turf multiplier (zero new constants); the AI bills expeditions at the cost-table price |
| HC-5 | Tutorial drift (nothing after July 17 taught) | **BUILD the S half** (step XIV names the new surfaces honestly); "The Congress" second lesson **DEFERRED to the existing Pre-EA Onboarding & Teaching Pass row** (its named owner) |
| HC-6 | Seasons/weather do not exist | **PROMOTED, NOT RULED** — the HC-6 session AUTHORS `docs/SEASONS_WEATHER_SPEC.md` and puts its questions to the USER; build only after that gate |
| HC-0 | *(added by user direction, Aug 14 second session)* No calendar — "Turn N" is timeless | **RULED + BUILD FIRST** — **one turn = HALF A MONTH (~15 days)**, displayed "Early/Late {Month} {Year}", anchor Sept 25, 1805 → turn 1 = "Late September 1805"; §2a below is the full derivation |
| HC-G | *(added by user direction, Aug 14 second session)* The Gazette — cut to post-EA Aug 3 | **UN-CUT + BUILD as slice HC-G** — "Le Moniteur" re-scoped DETERMINISTIC-first (the Aug-3 objection was aimed at the LLM version, and the monetization ruling makes no-LLM-required the product's spine); §7a below is the contract |
| HC-L | *(added by user direction, Aug 14 third session — "slot this after all fixes and weather")* Local model parsing, the memo's v2.1 flagship | **PROMOTED from post-EA into row HC at position 8** — spike-first (ship/no-ship is a measured corpus score), build only on a pass; §7b below is the contract; memo addendum-§9 pins carry (parsing only, never silently replace BYOK) |

**Build order: HC-1 → HC-2 → HC-3 → HC-4 → HC-5 → HC-6(spec) → the played
20-turn campaign → position 10.** Rationale: the three
byte-identity-preserving legibility slices land first so their pins anchor
against the unmoved baseline; HC-4 (the one sanctioned re-record) runs
after them so nothing has to re-verify against a moved series; HC-6's spec
closes the program; the played campaign then evaluates the FIXED naval
game (the A2 strangulation arc would read 0 on the bar today — playing it
before HC-1 would taint the open naval-pillar evidence).

---

## §2a HC-0 — "The Calendar" (how long a turn is — RULED)

**The ruling: ONE TURN = HALF A MONTH (~15 days). Two turns per month,
24 per year. The 1805 boot (Sept 25 anchor) opens on turn 1 = "Late
September 1805".** Derived from the game's own numbers, not taste:

- **March rates pin it.** Infantry `movement_range` is 1 province/turn
  and the 126 provinces are ~200–300 km across — at the historical
  15–25 km/day sustained corps rate, one province IS ~two weeks.
  Cavalry's range 2 works out to ~30–40 km/day over a fortnight
  (historically right); at one week/turn cavalry would need an
  impossible 60–85 km/day, and at one month/turn infantry would crawl
  at 8 km/day.
- **The boot war pins it.** Rhine crossing Sept 25 → Ulm Oct 20 is ~2
  turns; Vienna (Nov 13) ~turn 3–4; Austerlitz (Dec 2) ~turn 5. Played
  campaigns storm Vienna around turns 5–9 — slightly slower than
  history, the right ballpark. At a month/turn the whole Third
  Coalition would be three turns long.
- **Campaign math pins it.** The measured 19–42-turn campaigns become
  10–21 months — Sept 1805 through late 1806/mid 1807, exactly the
  Third-and-Fourth-Coalition canvas. Cooldowns read naturally (the
  5-turn glory window = 2½ months; the 15-turn ultimatum cooldown = 7½
  months).
- **Genre precedent:** AGEOD's Napoleonic titles run 15-day turns.
- **It feeds HC-6 and HC-G:** a season = **6 turns** (the seasons spec
  consumes this, superseding its provisional "~4-turn" sketch); winter
  arrives ~turn 6 of the boot year (Early December — Austerlitz
  weather on time); a Gazette issue carries a real dateline.

**The build contract (small, display-only, FIRST in the queue):**
- A pure derivation (backend, one home — e.g. `calendar.py` or a
  `world_state` helper): `(anchor_date, current_turn) → "Early/Late
  {Month} {Year}"`. **Zero new serialized fields** (derived); the
  scenario may author an optional `start_date` (validator-checked;
  `europe_1805.json` gets Sept 25, 1805; `tutorial_1805.json` the
  same). **A world with no anchor (the legacy fixture) keeps plain
  "Turn N" byte-identically** — the label is additive, never a
  replacement.
- Rendered through the R7 chokepoint discipline: the backend ships a
  `calendar_label` string on the summary/response; Godot renders and
  never computes dates. Surfaces: top bar beside the turn counter, the
  Morning Dispatch header, the strategic-ledger header, save-slot
  metadata display, and (later) the Gazette masthead.
- **Never-do pins:** no mechanic reads the calendar in this slice
  (GR6-style — display only; HC-6 is where seasons would make it
  mechanical, behind the USER gate); `current_turn` stays the single
  source of time.

**Acceptance:** turn 1 renders "Late September 1805", turn 6 "Early
December 1805", turn 25 "Late September 1806"; legacy world
byte-identical; `tests/test_hc0_calendar.py`.

---

## §2 HC-1 — "The Silver Blockade" (naval → war score)

**The defect (measured):** `calculate_war_score` has seven components —
none naval. A pure strangulation campaign (the designed A2 "Britain sues
without invasion" arc) moves the tug-of-war bar not at all, and every
surface priced off score (AUD-c offer direction, harshness, suggested
terms, PT-J1 coalition logic) treats the strangler as achieving nothing.
Naval pressure reaches diplomacy ONLY through war exhaustion (capped 20).

**The contract:**
- A signed component `blockade` (display "Blockade") in
  `calculate_war_score`, **cap ±15** (blessed, in-band), sitting beside
  the PT-J2 `campaign`/`blood` rows on the war-detail popup + HUD
  breakdown + diplomatic ledger (shown = applied, the PT-J2 pattern
  verbatim).
- **Substrate = `world.campaign_ledgers`** (the PT-J2 store): one new
  per-side counter `blockade_turns`, recorded once per turn in the naval
  tick for each war where that side's fleets deny the opponent's trade —
  the predicate is derived from EXISTING state (blockade posture covering
  an opponent dockyard, or CS closure ≥ 40% suffered by the opponent at
  that side's hands). The `from_dict` normalizer gains the third key with
  backfill 0 (old saves read 0 — no migration).
- **Accrual → score: `min(15, blockade_turns // 2)`** (blessed, in-band)
  — sustained pressure, not a light switch; symmetric both directions
  (GR5: Britain strangling France counts for Britain).
- The ledger key survives armistice exactly as `captures`/`casualties` do
  (PT-J2's ruling carries).
- **Never-do pins:** the component must be derivable to zero on fleetless
  worlds (legacy byte-identical); `defender_bonus` and the seven existing
  components untouched; the war-detail row renders only when nonzero.

**Acceptance:** a scripted blockade war shows a nonzero Blockade row whose
figure equals the formula over the recorded counter; M1–M7 byte-identical
(fleetless harness); if `BASELINE_SERIES` moves (score feeds AUD-c offers
on the live Britain war), attribute by flip experiment before any
re-record. Test file: `tests/test_hc1_blockade_war_score.py`.

---

## §3 HC-2 — "The Butcher's Ledger Speaks" (narration)

**The defect:** PT-J2's per-war ledgers are consumed by exactly three
things (war score, pensions, demobilize) — none narrative. The number the
CA9 through-line wanted spoken now EXISTS per-war and is honest, and
nothing says it.

**The contract (stateless by design — ZERO new serialized fields):**
- A war-room (Talleyrand assess) rung per active war reading the ledger:
  *"This war has taken {own dead} of our men and yielded {unique
  captures} provinces, Sire."* — the SAME figures the war-detail popup
  already renders, so no new precision claim is introduced.
- A battle-report closing clause on Europe-scoped battles in wars past a
  dead threshold (**25,000**, blessed, in-band): *"The war's cost now
  stands at N."* Stateless — derived at render from the ledger, no
  latch, no seen-map.
- Copy discipline: the [PTJ-D1] pooled-allied-dead attribution rider
  (EC-2 pass 2) is referenced in the slice record; the lines voice the
  side's OWN recorded dead only, which is the attribution-safe half.

**Acceptance:** the rung renders with live ledger figures; a fresh war
(empty ledger) renders nothing; `tests/test_hc2_ledger_narration.py`.

---

## §4 HC-3 — "The Crowned Name Abroad" (glory → diplomacy, flavor half)

**The defect:** zero references to glory/jealousy in any diplomatic
module; no foreign court has ever heard of Davout. Courts historically
priced Napoleon's marshals into negotiations.

**The contract (display-only, GR6 — the LLM/mechanics never read it):**
- Envoy refusal/capitulation line VARIANTS that name the opposing side's
  crowned (★) marshal when one exists — e.g. a court refusing France
  while the crown sits on Davout: *"…while the Iron Marshal stands on the
  Danube."* Sourced from the existing glory ladder (`world`-derived at
  render), deterministic, added as bank variants at the existing
  suffix/register seams.
- **Voice Bible discipline is mandatory:** read
  `docs/DIPLOMAT_VOICE_BIBLE.md` before authoring; named-diplomat lines
  resolve through `resolve_named_diplomat()`; chancery-fallback courts
  get the register-neutral variant.
- Bank-growth rules follow the XR-5 idiom (append-only, index-0
  anchored where a rotation store exists).
- **The mechanical half is NOT built:** an acceptance/intent term reading
  glory is deferred as `DESIGN_REFINEMENT.md` **HC-D1**, owner = the
  Victory & Objectives Pass gate (positions 12–13), completion = a gate
  ruling that builds or rejects it with a test named there.

**Acceptance:** with a crowned marshal, the variant is reachable; with no
crown, banks behave byte-identically; no raw key leaks (R7);
`tests/test_hc3_crowned_name_abroad.py`.

---

## §5 HC-4 — "The Lifeline and the Bill" (the naval-balance duo)

The ONE slice of this program sanctioned to move measured AI behavior.
`BASELINE_SERIES` may be re-recorded **ONCE**, with the standing
flip-experiment attribution discipline (each half disabled in turn must
reproduce the prior series byte-for-byte before the re-record lands).

### (a) The Royal Navy's lifeline — naval ↔ supply

**The defect:** `process_supply_attrition` is purely land. Britain's
Lisbon expedition is supplied like a home army (the historical RN
lifeline is free and implicit), and symmetrically a coast-dominating
fleet cannot strain a coastal invader.

**The contract:**
- ONE arm in the supply seam, reading EXISTING naval coverage
  predicates, for an AT-WAR army standing in a COASTAL province:
  - adjacent water covered by a FRIENDLY fleet and not contested →
    the army is treated at the home-turf multiplier (the lifeline);
  - covered by a HOSTILE fleet with no friendly coverage → the army
    loses any home-turf treatment it had (the strangled shore).
  - no coverage either way → today's behavior byte-identically.
- **ZERO new constants** — the arm reuses the existing 1.5× home-turf
  multiplier; **zero new serialized fields** (coverage is derived).
- GR5: both boards, same arm; fleetless worlds byte-identical.

### (b) The Admiralty's bill — AI expedition AP parity

**The defect:** the player's `naval_expedition` costs 2 military AP; the
AI's costs 1 generic admin AP from a budget of 2 (Britain sails a
15,000-man descent for half her admin turn while France spends half her
military turn). The dead `EXPEDITION_AP_COST = 2` constant proved the
shared price was intended and never wired.

**The contract:** `execute_admin_phase` bills `naval_expedition` and
`naval_diversion` at the `world._action_costs` table price (2 / 1)
against the AI's admin budget — an AI descent consumes its whole admin
phase, mirroring the player's half-military-turn. Scoped to the two naval
verbs ONLY (re-pricing the whole admin chain is out of scope and would
reopen the admin-economy design).

**Acceptance:** measured before/after probe of Britain's expedition
cadence recorded in the landing record; the NV-5 Lisbon shape must
SURVIVE (Britain still lands — later is acceptable, never never);
attribution experiment per half; `tests/test_hc4_naval_balance_duo.py`.

---

## §6 HC-5 — "The School Names the Fleet" (tutorial honesty)

**The defect:** the School of War teaches nothing landed after July 17 —
zero occurrences of naval/agenda/estate/reward/jealousy; step XIV ("The
Instruments") names four screens and stops.

**The contract (the S half only):**
- Step XIV extended to name, in Berthier's voice, one sentence each: THE
  ADMIRALTY (ledger tab 7), the F1 wizard incl. the Formables button,
  the Generals card's Reward chip, and the ledger's Design rows — honest
  pointers, not new lessons; the R159 self-teaching screens carry the
  depth.
- Any added suggest chip must be T-B1 mock-parse-pinned; `.gd` touch →
  parse harness + boot smoke per the standing XR-1 rule.
- **"The Congress" (a diplomacy/settlement second lesson) is NOT built
  here** — it is recorded as a named candidate ON the existing Pre-EA
  Onboarding & Teaching Pass row (`DESIGN_REFINEMENT.md` §8.EVAL
  Dispositions), which already owns R159's family; completion stays that
  row's.

**Acceptance:** the tutorial drive still passes end to end (the S5 live
harness); `tests/test_hc5_tutorial_names_fleet.py` pins the step-XIV
surface list.

---

## §7a HC-G — "Le Moniteur" (the Gazette, un-cut by user direction)

**History:** cut to post-EA on Aug 3, 2026 with two recorded objections —
it was scoped as the game's FIRST `game_logic` LLM call ("via single LLM
call"), and it read as redundant with the Morning Dispatch. **The user
directed it back into the plan Aug 14. Both objections are honored by
re-scoping, not overridden:**

1. **Deterministic-first.** v1 composes issues from the EXISTING
   fog-filtered event data with zero LLM — which the monetization ruling
   (mock-default, no-AI-required as the product's spine) now makes the
   only coherent choice. An optional LLM-polish pass is a LATER slice
   behind BYOK, owned here, never required.
2. **Not the Dispatch.** The Dispatch is the STAFF BRIEFING — this turn,
   actionable, "what needs my attention." The Gazette is the PERIODICAL —
   retrospective, published every few turns, the continent's story told
   as news, and (the half the Dispatch structurally cannot do) a
   browsable BACK-ISSUE ARCHIVE: campaign memory. Same events, different
   surface, different job.

**The build contract:**
- **Cadence:** an issue every **5 turns** (blessed, in-band), plus a
  forced special edition on: a capital stormed, a nation eliminated or
  proclaimed (NA-6), a great-power war declared or settled, the player's
  marshal killed/captured. One issue max per turn (the special resets
  the 5-turn clock).
- **Composition (deterministic):** masthead "LE MONITEUR — Paris,
  {HC-0 calendar date}"; sections built from events since the last
  issue — The War (battles/captures from the fog-filtered log, HC-2's
  ledger figures for standing wars), The Courts (diplomacy: treaties,
  ultimatums, formations, congress beats), The Army (glory/crown/
  petition beats, in the press's voice not the staff's), and a short
  Bourse line (the treasury/blockade situation). French-press register
  (triumphalist on victories, delicate on defeats — the period voice);
  all copy through the existing display-name/R7 chokepoints; Voice
  Bible discipline where named diplomats are quoted.
- **Eviction-proof by construction:** issues are COMPOSED at generation
  time and STORED — **one new serialized store `world.gazette_issues`**
  (list, capped at the last **20** issues, oldest evicted) — never
  recomposed from the event log later (the 500-cap eviction trap that
  bit IGR-B is the named reason).
- **Surface:** a Gazette screen on the existing screen framework
  (top-bar button or ledger tab — builder's call), rendering the
  current issue with back-issue paging; a one-line "The Moniteur is
  out" notification on issue turns (existing notification rail, no new
  popup class, no queue slot).
- **GR6/GR5:** display-only; no mechanic reads an issue; AI-side
  nothing (the press is player-facing color).
- **Never-do pins:** never blocks the turn; never a modal; no raw keys
  (R7); a fog-hidden event never appears in print (the composition
  reads only the already-filtered surfaces); legacy fixture world =
  feature dormant (no calendar anchor → no gazette) byte-identically.

**Acceptance:** a 12-turn scripted campaign produces ≥2 dated issues
whose battle lines match the campaign log's own rows; a capital storm
forces a special edition; save/load round-trips the archive;
`tests/test_hc_g_gazette.py`. Size M; runs AFTER HC-5 so the played
campaign (queue position 8) evaluates it.

---

## §7b HC-L — "Smart Parsing — Offline" (the local model, slotted by user direction)

**User direction (Aug 14, third session): "slot this after all fixes and
weather."** This PROMOTES the monetization memo's §5-v2.1 flagship
(`docs/audits/LLM_MONETIZATION_RESEARCH_2026_08_14.md`, incl. the
addendum-§9 scope pins) from post-EA into row HC, at queue position 8 —
after HC-6.

**The slice is TWO halves with a mechanical gate between them:**

1. **The spike (one session, no product code):** a standalone script runs
   the golden corpus's live-parse rows through candidate quantized GGUFs
   (Qwen 0.5B/1.5B, Llama-3.2-1B/3B, Gemma-2-2B class) via llama.cpp
   with a grammar constrained from the existing `PARSE_TOOL` schema
   (roster names injected as enums per world). Output = a measured
   score per candidate vs the cloud rows. **Ship/no-ship is that
   number** — if no candidate beats-or-matches the live rows, the build
   half DOES NOT RUN and the row closes with the measurement recorded
   (the game is unaffected; the Portopia failure mode is structurally
   unreachable).
2. **The gated build (only on a passing spike):** a `local` provider on
   the existing `providers.py` seam (the reserved-slot idiom —
   `LLM_MODE` gains `local`); llama-cpp-python CPU-only;
   PyInstaller/native-lib packaging folded with position 10's deploy
   machinery; model delivery = free "Smart Parsing — Offline" DLC or
   optional download so the base build stays lean while "works offline"
   stays true; a Settings rung UNDER the BYOK key (ladder: key > local
   > mock, the player chooses); Steam AI-disclosure line updated.

**Carried pins (memo addendum §9, non-negotiable):** the local model
does **PARSING ONLY** — never the CR-5b flavor line; it **never silently
replaces a connected key**. Named decision at build time (recommended
default recorded now): local counts as "live" for the CR-5 personality
arms ONLY if it also passes the corpus's `live_only` rows — otherwise
those arms keep degrading to ASK exactly as mock does (guardrail (e)
extends, never weakens).

**Acceptance:** spike memo with per-candidate scores committed to
`docs/audits/`; if built — corpus green under `LLM_MODE=local`, parse
latency ≤ the cloud round-trip on a mid CPU, `tests/test_hc_l_local_parsing.py`,
and the keyless-mock experience byte-identical when the rung is off.

---

## §7 HC-6 — Seasons & Weather: the spec-and-gate session

**Deliberately NOT ruled here.** The integration audit's verdict stands:
this is the one large expansion the codebase is structurally ready for (a
turn-indexed global scalar consumed at existing chokepoints — supply,
movement, naval readiness — scale-ready by construction, GR5-symmetric
for free, and the missing half of the 1812 story: Russia's arbiter
posture plus winter is the actual historical deterrent). It is also the
biggest balance change since naval — it will move every band, M1–M7, and
`BASELINE_SERIES`, and it deserves the user's own eyes.

**The HC-6 session's contract:** AUTHOR `docs/SEASONS_WEATHER_SPEC.md` —
research + design + a numbered question list at recommended defaults
(anchors to examine: **seasons CONSUME the HC-0 calendar — a season is 6
turns at the ruled 15-day turn, superseding this record's earlier
"~4-turn" sketch; the Sept 25, 1805 boot opens in autumn and winter
arrives ~turn 6, Early December — Austerlitz weather on time**; winter
multiplying supply attrition and movement cost; a naval-readiness winter
penalty; scenario-authored season anchor under the D7 authored-bounds
idiom; the war-council "campaign season closing" moment term; the
re-record protocol for every touched baseline) — and put the gate to the
USER. No mechanic lands before that gate returns.

---

## §8 Queue placement (the routing this gate sets)

**Row HC opens NOW and runs before the standing owed items**, because
every slice either raises the legibility of evidence the owed items must
gather (HC-1/HC-2 before the played campaign) or is a small honesty fix
(HC-3/HC-5), and HC-4 fixes the balance the campaign should evaluate.

*(Amended Aug 14 second session — HC-0 and HC-G inserted by user
direction: "include gazette as well as part of plan and figure out how
long a turn is".)*

0. **HC-0** The Calendar *(15-day turns — tiny, display-only, first:
   everything downstream carries dates)*
1. **HC-1** The Silver Blockade
2. **HC-2** The Butcher's Ledger Speaks
3. **HC-3** The Crowned Name Abroad
4. **HC-4** The Lifeline and the Bill *(the one sanctioned re-record)*
5. **HC-5** The School Names the Fleet
6. **HC-G** Le Moniteur — the Gazette *(deterministic v1, dated by HC-0)*
7. **HC-6** Seasons & Weather spec → **USER GATE** *(consumes HC-0:
   6-turn seasons)*
8. **HC-L** Smart Parsing — Offline *(slotted by user direction Aug 14
   "after all fixes and weather": the corpus SPIKE first, the build only
   on a passing score — §7b)*
9. → the played 20-turn campaign (PT row-2 arm + naval pillar + the
   standing visual sign-offs — now including HC-1's Blockade row, the
   calendar surfaces, and the Gazette)
10. → **position 10, THE SHIPPABLE BUILD** (the road-to-EA spine resumes)

Landing records accumulate in this file (§9+, one per slice, the
standing pattern).

---

## §9 Landing records

### §9.0 HC-0 "The Calendar" — ✅ LANDED August 14, 2026

`backend/game_logic/calendar.py` (pure `(anchor, turn) → "Early/Late
{Month} {Year}"`, half-month arithmetic, AST-pinned world-free);
`WorldState.start_date` rides the scenario_name from_dict funnel
(**ONE serialized field** — the anchor must survive save/load; the gate's
"zero new serialized fields" is honored for the LABEL, which is derived
by `get_calendar_label()` and never stored); scenario JSONs author
`"start_date": "1805-09-25"` (validator block hard-fails malformed
dates); label rides `get_action_summary` + `get_filtered_game_state_
summary` + the dispatch dict + the ledger payload + save METADATA
(`calendar_label`). Godot: top-bar counter ("Turn 5 — Late November
1805"), dispatch header, per-book ledger dateline (`_dated_line`),
main-menu Continue slot. Legacy world: label "" → every surface renders
byte-identically. Acceptance measured: turn 1 "Late September 1805" /
turn 6 "Early December 1805" / turn 25 "Late September 1806".
`tests/test_hc0_calendar.py` (28).

### §9.1 HC-1 "The Silver Blockade" — ✅ LANDED August 14, 2026

`BLOCKADE_SCORE_CAP = 15` / `BLOCKADE_TURNS_DIVISOR = 2` beside the
PT-J2 constants; the eighth component in `calculate_war_score` +
`calculate_side_war_score` (per-side saturation THEN difference, so a
mutual blockade washes); `WorldState.record_blockade_turn` mirrors
`record_campaign_casualties` (war-gated); accrual =
`naval._record_blockade_pressure` at tick step 5b — arm 1 the
`blockader_against` verdict, arm 2 CS closure ≥ the tier-1 notch (0.40)
with the denier's own ports counted, one credit per (denier, victim)
per turn. **The ledger's third key is serialized SPARSE** (written only
when non-empty) so a land war's ledger round-trips byte-identically to
its pre-slice shape — the PT-J2 round-trip pin holds unmodified.
Rendered: war-detail popup (only-when-nonzero row), war_status both
breakdown sites, diplomatic ledger (conditional key). Boot facts
pinned: Britain credits vs France every tick; the closure arm does NOT
fire at boot (0.385 < 0.40). M1–M7 + `BASELINE_SERIES` byte-identical
WITHOUT re-record (proved again as HC-4's control arm).
`tests/test_hc1_blockade_war_score.py` (19).

### §9.2 HC-2 "The Butcher's Ledger Speaks" — ✅ LANDED August 14, 2026

The war-room rung rides `_assess_situation`'s per-war loop (aggregating
pair ledgers across a collapsed coalition row's opponents); the
battle-report closing clause is `battle_report.compose_campaign_cost_
note` (threshold `CAMPAIGN_COST_NOTE_THRESHOLD = 25000`, Europe-scoped,
own recorded dead only — the [PTJ-D1] attribution-safe half) glued at
the combat executor's after-action seam (the expectation_note pattern,
player side only) and rendered by main.gd after Berthier's observation.
Stateless both halves — zero new fields, no latch; a fresh war says
nothing. `tests/test_hc2_ledger_narration.py` (11).

### §9.3 HC-3 "The Crowned Name Abroad" — ✅ LANDED August 14, 2026

Flavor half only. `jealousy.get_crowned_marshal` (settled-flag
accessor); `diplomatic_templates.CROWNED_SETTLEMENT_CLAUSES` (per-cast
suffix registers + chancery neutral, reported-speech continuations of
the settlement-table frames) + `CROWNED_INCOMING_CLAUSES` (first-person,
register-neutral); wired at (1) the multi-court settlement voice's
HOLDOUT arm only (a signing/leaning court is not refusing) and (2)
`compose_incoming_diplomat_line`'s `war_overload` motive (the
capitulation surface). Append-only banks (XR-5), deterministic turn
rotation, no crown → byte-identical lines (pinned both wires). No
epithet map exists — the clauses name "Marshal {name}" + location.
**The mechanical half is HC-D1** (`DESIGN_REFINEMENT.md`, owner = the
Victory & Objectives Pass gate). `tests/test_hc3_crowned_name_abroad.py`
(16).

### §9.4 HC-4 "The Lifeline and the Bill" — ✅ LANDED August 14, 2026

**(a)** `naval.shore_supply_state` — presence semantics, contract-
literal: friendly afloat + no hostile projecting → 'lifeline'; hostile
projecting (blockade posture) + NO friendly coverage → 'strangled';
both afloat = contested → None. **The water is the abstraction's water**
(one fleet store, no naval map — §12): a fleet reaches a shore by
projecting; a side's pooled fleet convoys in any posture. The
sea-link derivation was tried and REJECTED — Lisbon carries no drawn
link, so the gate's own motivating case would have read None. Boot
facts measured + pinned: French coast CONTESTED (the Combined Fleet is
outmatched but afloat — boot-neutral by construction), Britain ashore
'lifeline', post-Trafalgar France 'strangled'. The arm sits in
`process_supply_attrition`'s marshal loop (coastal + at-war gates,
per-(nation, region) turn cache), granting/stripping the SAME 1.5×
multiplier — zero new constants, GR5 one loop both boards.
**(b)** `enemy_ai.AI_NAVAL_AP_PARITY` — the two naval verbs bill at the
`world._action_costs` TABLE price (2/1) against the AI's 2-AP admin
budget; the expedition rung is affordability-gated (never picked with
1 AP — no overdraw discount). **Correction to this record's §5b:** no
`EXPEDITION_AP_COST = 2` constant ever existed on master — the dead
price was the `_action_costs` table entry itself, which the AI path
never read; the parity now reads THE TABLE (single source).
**The ONE sanctioned `BASELINE_SERIES` re-record, 4-arm flip
experiment:** control (both levers off) reproduces the prior series
BYTE-FOR-BYTE (proving HC-0..HC-3 move nothing); lifeline-only =
byte-identical to control (the ambient board never meets a one-sided
shore in 40 turns); **parity-only reproduces the new series exactly —
SOLE CAUSE, divergence index 12**; both = parity-only. **Cadence probe
(30 turns, both arms): Britain's descents are BYTE-IDENTICAL — lands
turn 12 (Corsica) and 16 (Flanders) under either billing. The NV-5
shape SURVIVES exactly; what moves is the second admin action the flat
bill used to leave room for.** `tests/test_hc4_naval_balance_duo.py`
(15).

### §9.5 HC-5 "The School Names the Fleet" — ✅ LANDED August 14, 2026

Step XIV's body extended in Berthier's voice: THE ADMIRALTY (the
ledger's seventh book), F1 + the Formable Nations button, the Generals
card's Reward chip, the ledger's Design rows. **No new suggest chip**
(the tutorial world has no navy authored — a naval chip would be a
dishonest pointer and T-B1 would rightly refuse it); the T/G/D/R
originals stay named; `docs/TUTORIAL_SCRIPT.md` row 10+ updated. "The
Congress" second lesson stays with its owner (the Pre-EA Onboarding &
Teaching Pass row). Parse harness EXIT=0 (tutorial_overlay.gd already
listed). `tests/test_hc5_tutorial_names_fleet.py` (7).
