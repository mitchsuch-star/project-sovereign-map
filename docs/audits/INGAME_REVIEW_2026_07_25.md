# In-Game Review — July 25, 2026

**The queued user in-game review (NA-6c/6d + the AI-3r exposure surfaces), widened to a
cross-element pass.** Played in the real Godot client against the real backend
(`-m backend.main`, port 8005, `LLM_MODE=anthropic`, default `europe_1805.json`), typed
commands in the terminal, F1 wizard, ledgers, popups. `curl` used for debugging only.

- **Main campaign:** France, `SOVEREIGN_SEED=historical`, turns 1–9, ~40 in-client decisions.
- **Variance spot-check:** `SOVEREIGN_SEED=austerlitz`, turns 1–5.
- **Defects:** 5 found by play, **all 5 fixed in-session** (commit `bdeb17c`); 4 routed to
  `BUG_FIXES.md`; 2 design questions routed to `DESIGN_REFINEMENT.md`.
- Suite **14,936/3**, ruff clean, Godot parse harness EXIT=0.

---

## 1. Scores

| Pillar | Score | One-line verdict |
|---|---|---|
| Command parsing / friction | **7.5** | CR-5 delegation works end-to-end; errors are specific; region-vs-nation naming still trips |
| Marshal drama | **8.5** | The strongest pillar — and the paid half of it was dead until this session |
| Combat legibility | **8.0** | Every modifier names its source; the muster preview teaches its own fix |
| Narration / dispatch | **6.0** | The dispatch is excellent; the campaign log is drowned in AI-AI noise |
| Economy | **7.5** | Money genuinely bites now — one petition cut my net surplus by 60% |
| Diplomacy & settlements | **7.0** | Superb per-court table; two promise-breaking defects on the paths out of it |
| Vassals | **6.5** | Drift, levers and hints all legible; the surface is still thin for the depth built |
| Nation agendas & formables | **8.5** | The standout. Decks advance, retarget and vary by seed, live |
| AI aliveness | **7.5** | Britain quietly took six provinces while I looked away; but no AI can start a war |
| UI / UX | **6.5** | Cards and ledgers are beautiful; the terminal couldn't scroll and stacks are illegible |

**Overall ≈ 7.4.**

---

## 2. The three biggest fun-factor gaps

### GAP 1 — The campaign log is unreadable (narration, AI aliveness)

Turn 9's log carried **25 events. Twenty-four of them were `D <X> rebuffs <Y> (open borders)` /
`(non aggression)`.** Screenshot evidence: eighteen consecutive near-identical lines, then seven
more after scrolling.

Buried at the very bottom of that wall, in identical styling, was:

> `D The court of Russia takes up a new design: The Gulf and the Straits`

That is AI-0d activating organically at turn 9 — one of the most interesting things that
happened in the campaign — and it is visually indistinguishable from 23 lines of noise. The
per-turn counts were 37 / 31 / 31 / 40 / 33 / 19 / 25 events, dominated throughout by the same
family.

This is the AI-2a `ai_ai_proposal_refused` record (built as AI-3's ladder-gate substrate)
being rendered at full volume into the player's history surface. The mechanism is right; the
presentation defeats it. **Routed IGR-1 (P2).**

### GAP 2 — The paid half of marshal drama was unreachable (marshal drama)

Every AP-priced petition arm — *Promise Glory*, *Reassign*, *Mediate*, *Force Reconciliation* —
arrived **permanently disabled, silently**. Observed live twice: *Promise Glory* holding 4/4 AP,
and *Force Reconciliation [2 AP]* holding 3/4 AP; neither produced a single HTTP request while
*Acknowledge* on the same dialog fired instantly.

Cause: `turn_manager.process_turn` runs the jealousy pass **before** `world.advance_turn()`
refills AP, so `enabled: ap >= cost` was baked against the *spent* turn's zero and then shown to
a player holding a full hand. Any player who ends a turn having used their AP — i.e. essentially
every turn — never saw a working paid option. The headline mechanic of the Jealousy build had a
dead branch, and the greying carried no explanation.

**FIXED** — affordability is now re-derived at the delivery seam, and a disabled arm states what
it would take.

### GAP 3 — The game's most ambitious feature is hard to actually reach (agendas, diplomacy)

Erecting a client state is the marquee NA-6 payoff, and the road to it is genuinely thrilling
right up to the last step. I did the whole arc by real play: declared on Prussia, took Posen,
watched the Formables gate flip from bullets to green ticks, opened the settlement, found
*"Erect Duchy of Warsaw from Prussia's lands"* with Talleyrand's *"Do not annex it, Sire - erect
it"* — and then hit two walls in a row:

1. **Declaring war on a treaty partner was impossible at all** — an infinite modal loop
   (war purpose → treaty warning → Talleyrand objection → war purpose → …), three full cycles
   observed, escapable only by Cancel. **FIXED.**
2. The carve lives on a **whole-war** settlement requiring *all four* coalition courts at 50.
   The game then offers "Make peace with Prussia only" and states **"Your drafted terms for
   Prussia carry into the talks"** — but the G4F-8 carry-over translates money and taken
   territory only; identity clauses are dropped by design. I took the promise and got a bare
   white peace, assessment GENEROUS, the carve gone. **Copy FIXED** to name what will not
   travel; **the design question is routed** (IGR-3).

The result: the feature is reachable in principle, but the only route the game steers you toward
silently discards it. **The Proclamation card did not fire this session** — see §4.

---

## 3. Must-see checklist

| # | Target | Result | Evidence |
|---|---|---|---|
| 1 | Formables button in F1 wizard | **PASS** | Top gold row of step 1, "Formable Nations — states that could yet exist" |
| 2 | Gate terms honest? | **PASS (excellent)** | Warsaw's two terms flipped from `•` to green `✓` the turn I took Posen, and an "↳ Open negotiations — Prussia" button appeared. Italy's row dropped "currently a vassal of France" the turn I released it. Normandy renders the mirror term ("a clause only a victorious enemy may put before you") |
| 3 | create_client carve offered/authored in a settlement | **PASS** | Prussia row → `+ Add demand` → *"Erect Duchy of Warsaw from Prussia's lands"*, added to the draft |
| 4 | The Proclamation card firing | **NOT REACHED** | Blocked by the whole-war ratification bar; the bilateral route drops the clause (GAP 3). Mechanism itself is pinned by `test_nation_agendas_formables.py` |
| 5 | Ledger "→ forms:" watcher | **PASS** | `Design: Risorgimento — … → forms: Italy (2 of 5 provinces held)` on Kingdom of Italy after release |
| 6 | "The Polish Question" grudge label | **NOT REACHED** | Requires the Duchy to exist. Pre-verified structurally: `DuchyOfWarsaw` carries no `aggrieved`; the label rides the `commonwealth_restored` deck entry |
| 7 | Per-court Exposure rows | **PASS** | Austria `Free field army: 104,000 of 126,000 — the rest held against Bavaria`; Prussia `48,601 of 78,000 — the rest held against Russia` (the authored `wary_of Russia 1.4` visible in the arithmetic). Correctly absent for fogged courts |
| 8 | "The Emperor's Own Exposure" | **PASS** | `Free field army: 159,000 of 189,000 — prudence holds the rest against Britain. Advisory only, Sire: your marshals march where you send them.` |
| 9 | Talleyrand's "not free to move" counsel | **ABSENT (explained)** | Ran the war room twice. `designs_in_check` needs `_restraint_block_reason == 'exposed'` on a **non-player → non-player** design; at boot Austria short-circuits on `busy` and Prussia reads `None`. Routed IGR-4 as an unreachable player-facing rung |
| 10 | Beats 2 / 3 / 7 | **DID NOT FIRE (expected)** | Consistent with spec §8.2 (0 crises / 40 turns × 8 seeds) and the pin-20 pass (0/38). Every warlike 1805 design targets the player-hegemon, and v1 excludes player-targeted designs. **Not filed as a regression** |
| 11 | `starved` never renders for exposure/force/treasury | **FAIL → FIXED** | `campaign_log.py` and `dispatch.py` each kept a private 4-cause map; `exposed`/`outmatched`/`penniless` all rendered as *"the moment passed"* — the exact §0.3 lie AI-3r was written to kill. Single-sourced on `war_council.crisis_cause_phrase()` |
| 12 | Stage B mirror block | **PASS** | `Read as: The hegemon of Europe — 40% of the continent's weight … They think he is coming for Hesse` (the §3.5 misreading-by-design) |
| 13 | Stage B intent / design rows | **PASS** | Every decked court; **and they advance live** — Britain's design moved *The Low Countries → The Paymaster of Coalitions* after Britain took Flanders |
| 14 | Weariness rows | **PASS** | `Weariness: National exhaustion across all wars: 8 (rising) — at war with Austria` (Bavaria, turn 2) |
| 15 | Compacts / paymaster purse | **PASS** | `Britain subsidises Austria with 200 gold` in the dispatch, turn 4; `Britain's gold: 300g reaches Austria` in the log by turn 9 |
| 16 | `agenda_pursuit` envoy register | **PASS** | Mareschalchi: *"My master's design is known to all Europe; Kingdom of Italy sends this offer in its pursuit."* |
| 17 | Congress beat 6 | **NOT REACHED** | Campaign ended at turn 9; the exhausted-pair exit needs both WE ≥120 (~T15+) |

---

## 4. Why the Proclamation did not fire — and what I did instead

I reached every prerequisite by honest play: at war with Prussia, Posen held and secured, gate
green, clause authored into the draft. The two remaining routes are:

- **Joint settlement** — needs Austria, Britain, Prussia *and* Russia each at 50/50. At turn 9
  they sat at −31, −24, −18 and −34. That is many more turns of winning a four-power war.
- **Bilateral substitution** — offered by the game, promises the terms carry, and drops the
  carve (GAP 3 / IGR-3).

I did not reach for the debug/cheat path, since the brief was to play for real. The
carve-and-proclaim mechanism itself is not in doubt — `test_nation_agendas_formables.py` (225)
pins it, including the Proclamation firing for creations — but **no in-client sighting of the
Proclamation card was obtained this session, and it should stay on the must-see list.**

---

## 5. Defects

### Fixed in-session (commit `bdeb17c`)

| ID | Sev | Defect |
|---|---|---|
| **IGR-F1** | **P1** | **Declaring war on a treaty partner soft-locked in an infinite modal loop.** `_include_popup_passthroughs` POPS the objection popup when it delivers it, so at answer time `war_objective` and the treaty resolution were unreadable; "Proceed Anyway" re-entered with neither, the treaty gate re-fired, and *its* "Proceed" re-entered via `force_declare_war` without `confirmed_objection`. Three cycles observed; only Cancel escaped. Fixed with a transient context that survives the pop + the mirror flag on `force_declare_war`. Re-verified live: *"France declares war on Prussia, shattering the Open Borders Agreement!"* |
| **IGR-F2** | **P1** | **Every AP-priced marshal-petition arm arrived dead** (GAP 2). Fixed by re-deriving affordability at the delivery seam from an authored `ap_cost`; disabled arms now state the reason. |
| **IGR-F3** | **P2** | **Beat-7 cause copy lied.** `exposed`/`outmatched`/`penniless` rendered as *"the moment passed"*. Single-sourced on `war_council.crisis_cause_phrase()`. |
| **IGR-F4** | **P2** | **The command terminal swallowed the mouse wheel.** `OutputDisplay` is a `RichTextLabel` with `fit_content` inside a `ScrollContainer`: zero scroll range of its own, but it ate the wheel and the parent never saw it. Drag worked, wheel did not; every sibling ledger already sets `scroll_active = false`. Verified live after the fix. |
| **IGR-F5** | **P2** | **The separate-peace promise was not kept** (GAP 3). Copy now names the clauses that will not travel, with a drift guard tying it to the seed function. |

Tests: `tests/test_ingame_review_fixes_2026_07_25.py` (29).

### Routed to `BUG_FIXES.md` § In-Game Review July 25

| ID | Sev | Item |
|---|---|---|
| **IGR-1** | P2 | Campaign log drowned by `ai_ai_proposal_refused` one-liners (24/25 events on turn 9) — needs aggregation, a category filter, or demotion below the fold |
| **IGR-2** | P3 | `no_participation_path` — a raw internal key rendered verbatim in the ally-entry proposal copy (R7 violation) |
| **IGR-3** | P2 | Design: should identity clauses (`create_client`, vassalage, liberation) carry through the bilateral substitution, or should the settlement steer the player back to the joint route? Today the only offered route silently drops the marquee clause |
| **IGR-4** | P2 | Talleyrand's "designs held in check" counsel rung has no reachable trigger in a normal campaign (GR9: a player-facing promise with no landing) |

### Routed to `DESIGN_REFINEMENT.md` § In-Game Review July 25

| ID | Item |
|---|---|
| **IGR-D1** | **Plunder is economically irrelevant.** Plundering Nassau yielded **87 gold** against 3,085/turn income. The Plunder/Secure choice has no tension — Secure is strictly correct. Either price plunder to matter or make it a stability/authority choice rather than a gold one |
| **IGR-D2** | **Minor-court envoy spam.** Turns 2–5 delivered ~3–5 near-identical Open Borders / Non-Aggression proposals per turn from minors, each a modal that interrupts the command in flight. Consider batching them into one "the small courts write" digest |

### Observed, judged NOT defects (recorded so they are not re-filed)

- `48,601 of 78,000` next to rounded neighbours — the authored `wary_of Russia 1.4` arithmetic, correct.
- Britain reading `war (weight 84)` below the 85 fight floor — an at-war pair early-returns `fight`.
- Own soil showing `Intel: Partial (reports only)` — the documented scenario-boot fog rule.
- Map hover tooltip persisting — it clears correctly on leaving the map; my earlier reading was wrong.
- Threat & Coalition tab "not scrolling" — the content fits; I was clipping my own crop.
- End-turn envoy guard "not confirming" — the typed route confirms correctly and produced a proper
  `LAPSED ENVOYS` block; my fixed-coordinate click had hit the *Open Envoys* button, which shifts
  the row when envoys are pending.
- The Fontainebleau petition briefly not surfacing — self-inflicted (a debugging `curl` consumed the
  queue slot). It re-delivered on its own two turns later; not orphaned.

---

## 6. Variance spot-check — `SOVEREIGN_SEED=austerlitz`, turns 1–5

The D7 contract held exactly: **Tier 1 fixed, Tier 2 banded.**

| Reading | `historical` | `austerlitz` |
|---|---|---|
| Alarm (mirror) | 85 | **84** |
| Britain relation | −85 | **−90** |
| Britain intent weight | 84 | **85** |
| Russia weight / hegemon share | 89 / 35% | **90 / 39%** |
| **Austria's opening design** | **Redeem Italy** (→ Kingdom of Italy, Milan) | **Primacy in Germany** (→ Bavaria, Munich) |
| The Emperor's Own Exposure | 159,000 of 189,000 | **159,000 of 189,000** (identical) |
| Austria's exposure | 104,000 of 126,000 | **104,000 of 126,000** (identical) |
| Britain's design | The Low Countries | The Low Countries (identical) |

Austria's deck-order band is the headline: the same scenario produced a materially different war
— Vienna's Italy-first vs Germany-first council debate, exactly as AI-0c authored it. The
variance propagated into marshal drama too: by turn 5 **Ney** wore the crown and the feud was
**Bernadotte↔Davout**, where `historical` had **Davout** crowned and **Murat↔Lannes** feuding.

---

## 7. What played well — evidence worth keeping

- **The muster preview teaches its own fix.** *"Soult: awaits explicit orders and will NOT march
  — order 'Soult, support Davout' and he will march."* I did, and got: *"Soult will march to
  Davout's guns — he holds your written order. 'Soult, support Davout.' No more and no less.
  (1 AP — Soult executes precise orders with fewer couriers.)"*
- **CR-5 delegation, end to end.** `Marshal Ney, deal with Mack` → log
  `[CR-5] Delegation AGGRESSIVE (Ney) -> pursue Mack (inferred, gated)` → the lethal-first-step
  gate → a real battle whose report quoted me back: *"Ney acted on your word: 'Marshal Ney, deal
  with Mack'"*.
- **Reinforcement refusals name their reason.** *"Bernadotte hesitated — the I Corps weighed its
  own ambitions and did not march"* (the MC-3 Davout−Bernadotte −2 edge, live).
- **The autonomous glory-attack executed** — *"Murat, hungry for glory, has attacked Brunswick on
  his own initiative"* — closing an evidence gap Sweep 2 recorded as unfilled.
- **Money bit.** Answering Fontainebleau with *"I will find the means"* granted three rentes and
  moved the ledger from `Projected net: +1817g` to `+740g`, with the 50% fee shown per marshal
  (`Marshal Ney: 222g/turn face -> -333g with fees`).
- **The AI played a real campaign against me.** While I chased Austrians into Germany, Moore's
  expeditionary force took Flanders, Amsterdam, Brabant, Gelderland, **Nivernais and Orleanais** —
  and I only noticed when Britain offered me a status-quo peace that would have kept all six.
- **Decks are alive.** Britain's design advanced *The Low Countries → The Paymaster of Coalitions*
  on taking Flanders; Austria's retargeted onto Kingdom of Italy the moment I released it;
  Russia adopted *The Gulf and the Straits* at turn 9.
