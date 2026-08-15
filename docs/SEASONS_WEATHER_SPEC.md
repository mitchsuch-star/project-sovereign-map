# Seasons & Weather — "The General Winter" (HC-6)

> **Status: ✅ GATE RETURNED August 14, 2026 — THE BUILD IS DEFERRED
> PAST ROUND 0 (user ruling: "push it out").** The system is approved
> in principle; the slot is not. The session's argued recommendation —
> *"yes to the system, no to the slot: ship first, winter later"* — was
> accepted: seasons is the largest balance mover since naval (every
> band, M1–M7, `BASELINE_SERIES`), it competes directly with the
> shippable build (ROADMAP position 10) and the played campaign, it
> deepens the game's strongest pillar while the weak ones (narration,
> vassals, UI legibility) want the sessions more, and the AI gets only
> one season-sense term — symmetric rules are not symmetric competence.
>
> **The deferral's HOME and LANDING (GR9):** this spec is the owner;
> the landing slot is **the first post-Round-0 content slice — "The
> General Winter" as an EA content-update candidate** (ROADMAP row HC
> carries the ruling; Round 0 = position 11). Q6 is thereby RULED
> beyond its option (a): seasons builds after Round 0, so tester data
> on supply-pressure feel tunes Q1 before it is spent. **The remaining
> §6 questions are NOT ruled** — the recommended defaults stand as
> recommendations and are re-put to the user at the build session
> (tester evidence in hand). Completion = the SW-0..SW-V slices landing
> per §5 with the §4 re-record protocol, or an explicit cut recorded
> here. **Recorded pull-forward option:** SW-0 alone (display-only
> season names in dispatch/war room/gazette) moves no baseline and may
> land in any earlier session on the user's word — it is not blessed to
> land by default.
>
> *(Original gate framing, kept for provenance: this was the one item
> of the health-check program deliberately NOT ruled under the Aug-14
> delegation — gate record
> `docs/audits/HEALTH_CHECK_DESIGN_GATE_2026_08_14.md` §7 — because it
> deserved the user's own eyes. It got them.)*

---

## §1 Why this system, and why now

The August 14 integration audit's verdict: seasons are **the one large
expansion the codebase is structurally ready for**. A turn-indexed
global scalar consumed at existing chokepoints — supply, movement,
naval readiness — is scale-ready by construction (GR8: no per-region
scans; one derived value per turn) and GR5-symmetric for free (the
chokepoints already serve both boards).

It is also the missing half of the game's own story:

- **The campaign season was the strategic clock of the period.** Armies
  went into winter quarters; Napoleon's refusal to (Austerlitz, won in
  December; Eylau, fought in a February blizzard to general horror) was
  itself the shock. Today the game's turns are seasonless — a June turn
  and a January turn are identical, so the historical rhythm (march in
  May, decide by October, pay for winter ambition) cannot exist.
- **Russia's arbiter posture is under-priced.** The AI-intent work gave
  Russia distance and patience; history gave her winter as the actual
  deterrent. Without it, a late-year march on the east is priced like a
  summer walk (the 1812 lesson has no mechanical carrier).
- **HC-0 built the calendar this consumes.** One turn = half a month
  (24/year); the 1805 boot opens **Late September** — autumn — and
  winter arrives ~turn 6 (**Early December — Austerlitz weather
  exactly on time**). The display layer already tells the player what
  month it is; this spec is where the month starts to matter.

## §2 The shape (design summary)

ONE derived value: `season(world) -> "spring" | "summer" | "autumn" |
"winter"`, computed from the HC-0 calendar month (never stored — the
calendar module stays pure, `current_turn` stays the single source of
time). Month → season by the northern calendar: Dec–Feb winter,
Mar–May spring, Jun–Aug summer, Sep–Nov autumn. **A season is 6 turns
at the ruled 15-day turn** (superseding the gate record's provisional
"~4-turn" sketch, as its §7 anchor directs).

Winter (and to a lesser degree the mud seasons) presses on THREE
existing chokepoints, all already GR5-shared:

1. **Supply** (`process_supply_attrition`): winter multiplies effective
   strain — the same loop, one seasonal factor.
2. **Movement** (movement AP/attrition seam): winter marches cost more.
3. **Naval readiness** (`naval._readiness_tick`): winter caps the
   drill ceiling — fleets ride at anchor.

Plus TWO legibility surfaces (no mechanic): the war-council "campaign
season" moment term, and the dispatch/gazette naming the season's turn.

**Deliberately NOT in v1:** per-region climate zones (a Spanish winter
≠ a Russian winter — v2, needs authored bands per province), weather
EVENTS (storms, the Berezina crossing — post-EA), attrition to
FORTIFIED defenders in quarters (winter quarters are the shelter — see
Q3), and any combat-modifier arm (winter battles were rare because
CAMPAIGNING was hard, not because muskets misfired — the pressure
belongs on supply/movement, not on `get_attack_modifier`).

## §3 The mechanics, precisely

### §3.1 The season derivation (display + predicate)

- `backend/game_logic/calendar.py` gains `season_of(start_date, turn)`
  → season string or `""` without an anchor (the same dormancy as the
  label: **the legacy fixture world has no seasons**, byte-identical by
  construction — every seasonal arm gates on a non-empty season).
- `WorldState.get_season()` mirrors `get_calendar_label()`.
- The scenario may author `season_anchor` overrides ONLY through
  `start_date` (one anchor, one truth — no second date field). D7
  authored-bounds discipline: fidelity is reviewable by reading the
  scenario file; no formula invents a season the calendar cannot see.

### §3.2 Winter supply strain (the big one)

In `process_supply_attrition`, after the HC-4a shore arm:

- **winter:** effective capacity × `WINTER_SUPPLY_FACTOR` (Q1 default
  **0.75**) for every marshal NOT in shelter. Shelter = the region is
  home-controlled AND (capital OR has `supply_depot`) — "winter
  quarters": the army that goes home to a depot city is safe; the army
  that stands in the field pays.
- **mud (the two shoulder turns — the first turn of spring and the
  last of autumn):** factor `MUD_SUPPLY_FACTOR` (Q1 default **0.9**) —
  the rasputitsa nod, mild in v1.
- Summer/rest of spring/autumn: factor 1.0 — byte-identical.

### §3.3 Winter movement (the march bill)

At the movement-attrition seam (`movement_executor`, the existing
march-attrition arm): a winter march pays `WINTER_MARCH_ATTRITION`
(Q2 default **+1%** of the moving corps, additive to existing march
attrition). NO AP change (an AP change would reprice every plan the
AI's P-rungs cost out — too deep for v1; recorded as the Q2
alternative).

### §3.4 Winter at sea

`naval._readiness_tick`: in winter the drill ceiling drops by
`WINTER_READINESS_CEILING_DELTA` (Q4 default **−15**: 75 → 60, floors
untouched). Blockades loosen in winter the way they historically did —
through the READINESS number every naval predicate already reads
(coverage, crossings, HC-4a shore verdicts all inherit; zero new
seams).

### §3.5 The council reads the calendar

- War-council/exposure: a "the campaign season is closing" moment term
  — in autumn's last two turns, AI war-opening weight takes
  `SEASON_CLOSING_DELTA` (Q5 default **−4**, a decaying reading in the
  AI-3r idiom); in spring's first two turns, `+2` (the season opens).
  This is the ONE AI-behavior arm in v1 (and the main
  `BASELINE_SERIES` mover).
- Dispatch + war room + gazette name the season when it turns
  ("The army enters winter quarters weather"), via the existing beat
  registers — display strings only.

### §3.6 What every arm must respect (structural pins)

- **Dormancy:** empty season (no anchor) → every factor 1.0 / every
  delta 0 — the legacy world and all fixture tests byte-identical.
- **GR5:** all three mechanical arms sit in shared chokepoints — never
  a player-only or AI-only branch.
- **Single source:** the factors live in ONE constants block (owner
  file per arm's home module, cross-referenced), shown = applied
  (the supply event message names the season when a seasonal factor
  bit; the movement warning names the winter bill BEFORE the order
  confirms — the CA9 through-line discipline).
- **No calendar mechanics outside this spec:** HC-0's never-do pin
  ("no mechanic reads the calendar") is AMENDED by this gate, not
  deleted — the amendment enumerates exactly the arms above; anything
  else reading the season is a new gate question.

## §4 What it will move (the re-record protocol)

This build WILL move measured baselines — that is its point, and the
reason it is user-gated:

| Baseline | Expected movement | Protocol |
|---|---|---|
| `BASELINE_SERIES` (40-turn ambient) | The boot year's winter (turns ~6–11, ~30–35) changes AI supply losses + the §3.5 war-weight term | ONE re-record, multi-arm flip experiment per arm (§3.2/§3.3/§3.4/§3.5 each disabled in turn; control must reproduce the prior series byte-for-byte) |
| M1–M7 | Should HOLD (the combat harness is calendar-less — no anchor, no season) | Verify byte-identical; if it moves, a season leaked into a fixture — that is a bug, not a re-record |
| E1 band / EB probes | Winter upkeep-vs-attrition interplay shifts absorption on winter turns | Re-measure, re-bless only in-band; out-of-band → back to this gate |
| Tutorial (16-turn lesson) | Boots Late September; winter arrives mid-lesson | The lesson must stay winnable; if winter strain breaks a beat precondition, the tutorial scenario authors shelter (a depot) rather than the system making an exception |

## §5 Slices (build order, post-gate)

- **SW-0** the derivation + dormancy pins (display-only; season named
  in dispatch/war room/gazette) — byte-identity everywhere.
- **SW-1** winter supply strain + shelter (the §3.2 arm) + shown=applied
  copy. The FIRST baseline mover; the re-record rides this slice.
- **SW-2** winter march bill (§3.3).
- **SW-3** winter at sea (§3.4).
- **SW-4** the council's season sense (§3.5) + the season-turn beats.
- **SW-V** the assurance pass: per-arm flip levers verified, a played
  winter (the 20-turn campaign crosses turn 6 — it evaluates this for
  free if SW lands first; the gate may also rule the campaign runs
  BEFORE seasons, in which case SW waits — Q6).

## §6 THE QUESTIONS (the user gate — recommended defaults marked ◆)

1. **Winter supply factor.** ◆ (a) 0.75 effective capacity, shelter
   exempt (mud 0.9) · (b) harsher 0.6 (the 1812 number, brutal in
   1805-6) · (c) softer 0.85 (barely felt at current stack sizes).
2. **Winter movement.** ◆ (a) +1% march attrition, AP untouched ·
   (b) +1 AP on winter marches (deep repricing — NOT recommended in
   v1; it reaches every AI plan cost) · (c) no movement arm (supply
   only).
3. **Shelter definition.** ◆ (a) home-controlled AND
   (capital OR supply_depot) — winter quarters are a PLACE ·
   (b) home-controlled alone (softer; all home soil shelters) ·
   (c) fortified status also shelters anywhere (rewards digging in on
   foreign soil — historically wrong for supply, right for cover;
   NOT recommended).
4. **Winter at sea.** ◆ (a) drill ceiling −15 · (b) also readiness
   tick −2/turn in winter (fleets decay at anchor) · (c) no naval arm.
5. **The council's season sense.** ◆ (a) war-weight −4 closing / +2
   opening (decaying readings) · (b) display-only (the AI ignores the
   calendar — cheaper, but the player exploits November declarations
   forever) · (c) also gate AI EXPEDITIONS on season (the Channel in
   December — defer to v2 unless ruled now).
6. **Sequencing.** ◆ (a) seasons build AFTER the played 20-turn
   campaign (the campaign evaluates the CURRENT balance; seasons then
   land on measured ground) · (b) before it (the campaign evaluates
   winter too, but nothing else gets a clean read).
7. **Scope of v1.** ◆ (a) as specced — global scalar, no climate
   zones, no events · (b) add a Russia-band (the eastern provinces
   winter at Q1's harsher number — the 1812 hook, +1 authored region
   list) · (c) also weather events (post-EA per the audit; NOT
   recommended).

**Answering §6 at the defaults blesses §2–§5 as the build contract;
each numbered answer is in-band tunable after landing, structural
changes re-escalate. The HC-0 never-do amendment (§3.6) lands WITH
SW-0, not before.**
