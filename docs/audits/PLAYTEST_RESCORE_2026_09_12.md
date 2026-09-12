# PLAYTEST AND RE-SCORE — September 12, 2026

> **Memo of record** for the post-FA-audit playtest. Authoritative where it
> amends `PLAYTEST_FULL_RESCORE_2026_09_11.md` (the September 11 re-score and
> its §11 Phase-4 addendum). Everything filed here is NEW: the FA audit closed
> at `4094eb4` with `tools/fa_row_tally.py` reading 0 defect rows and 0 design
> gates open, of 268 filed.

---

## 0. In one page

Sixteen seeded driver runs on the committed instrument — five 40-turn ambient
seeds, the COMMANDED arm on three seeds, `--diplomacy propose`, the naval
Descent, the tutorial, both committed fixtures, a reload arm, a
`--declare-war proceed` control arm and a repeat-determinism arm. Two arms
could **not** be reached from this environment and are recorded as not run,
not as passes.

**Directional ≈6.9 → ≈7.0.** Diplomacy 6.0 → **6.5** and marshal drama 7.0 →
**7.5**; seven pillars hold; UI/UX could not be reached and its prior 7.5
stands untouched.

**The headline is a P1 the audit never reached: the peace table was a
formality.** On the COMMANDED arm, turn 4, France ratifies Britain's
settlement — seven war pairs go to PEACE and Britain pays a 1,358-gold
indemnity — and **inside the same `end turn`** the coalition machinery
re-enrols Britain, Austria and Russia and declares war for all three. The
peace France signed lasted **zero turns**, and the loop repeated until the
board reached a **tenth** coalition in forty turns. `qualifies_for_coalition`
asked three questions and none of them was *"did this court sign with us
yesterday?"*

Also fixed in session: nine producers carried internal nation TAGS into
player-facing prose (**"The Fourth Russia Coalition"**, **"A PapalStates
envoy has arrived"**, **"the France fleet"**, **"Vassal KingdomOfItaly joined
France's war"**), the most frequent dispatch headline in the game opened with
a pronoun that had no antecedent, and — answering the standing question about
the **diplomatic mission system** — a completed mission locked the Cabinet's
mission rows **for the rest of the campaign** while the top bar beside it
reported Talleyrand idle.

⚠ **Three defects in the committed test suite meant it did not run at all on
this machine.** `tests/test_notifications.py` used a nested same-type quote
inside an f-string (legal only on Python 3.12), so the file failed to COLLECT
and pytest **interrupted the entire run**; `tools/mutation_sweep.py` hard-coded
`.venv/Scripts/python.exe`, so the sweep tool and the twelve pins that drive it
died on any non-Windows checkout; and three pins depended on a hard-coded
`C:\Users\...` path or an untracked `.env`. All four are fixed. The pre-commit
hook was unusable here until they were.

---

## 1. What ran, and what did not

| arm | seeds | turns | status |
|---|---|---|---|
| ambient | historical, austerlitz, marengo, jena, wagram | 40 | completed ×5, 0 unknown blockers |
| COMMANDED (`commanded_full40.json`, `--diplomacy accept`) | historical, austerlitz, marengo | 40 | completed ×3 |
| `--declare-war proceed` control | historical | 40 | completed |
| repeat-determinism control | historical | 40 | completed, byte-identical |
| scripted-aggressive (`flagship_1805.json`) | historical | 26 | completed |
| `--diplomacy propose` | historical | 30 | completed |
| naval Descent | historical | 24 | completed |
| tutorial | — | 20 | completed, School steps VI → XV |
| fixture t10 / t20 | historical | 12 each | completed |
| reload arm (`--reload-every 4`) | historical | 16 | completed |

Every run above was then **re-run after the fixes** (twelve arms, `fix-*`), so
every claim about a change is a before/after on the same seed.

**NOT RUN, with reasons:**

* **`--llm anthropic`.** No `.env` and no `ANTHROPIC_API_KEY` in this
  environment. The live-parser half of the command pillar is therefore
  **unverified by this session**; the mock arm and the golden corpus are what
  it rests on.
* **Mode C, the client visual pass.** No Godot binary here, and no
  `godot_parse_check.gd` run is possible. **UI/UX is not scored** and its prior
  7.5 stands. The same limit means no `.gd` file was touched by this slice.

---

## 2. Determinism, and a documented table that does not reproduce

Two invocations of the ambient historical arm produced **byte-identical**
digests apart from the run name on line 1. Mode A is deterministic here.

That makes the following a real discrepancy rather than noise. The COMMANDED
arm table published September 12 in `PLAYTESTING.md`, the SLICE 17 (Phase 4)
block in `BUG_FIXES.md` and `DESIGN_REFINEMENT.md` reads 20 / 24 / 22
provinces at turn 40. Measured at the same commit, on this platform:

| seed | documented Fr@40 | measured (pre-fix) | measured (post-fix) |
|---|---|---|---|
| historical | 20 | **23** | **29** |
| austerlitz | 24 | **24** | **20** |
| marengo | 22 | **21** | **21** |

`BASELINE_SERIES` — the 40-turn ambient pin — passes byte-identically here, so
the ambient board is platform-stable and the difference is not a general
engine divergence. I could not test the Windows arm from this environment, so
the cause is **not isolated**. The ruling's conclusion is unchanged on either
reading: **0 of 3 seeds below 20 provinces at turn 40**, so the FA-D27 re-open
condition does not fire on a France that is still being played.

**And the arm spends about half the action points its own record claims.**
`PLAYTESTING.md` and the FA-S17-D6 row say "four military actions every turn,
160 of 160 AP". Measured from the digests' own end-turn warnings:

| seed | orders issued | refused | AP spent of 160 | turns with unused AP |
|---|---|---|---|---|
| historical | 160 | 56 (35%) | **81** | 36 of 40 |
| austerlitz | 160 | 56 (35%) | **77** | 37 of 40 |
| marengo | 160 | 62 (38%) | **75** | 37 of 40 |

The refusals are legitimate — stance locks, fortification state, a court France
has just signed with — but "160 of 160" describes the script's line count, not
the campaign. A France played at half strength still holds 20–29 provinces,
which strengthens rather than weakens the ruling; the supporting claim is
simply wrong and is corrected on the row.

`--declare-war cancel` and `--declare-war proceed` produce **identical**
outcomes on this arm (23 provinces, 81,593 gold either way): the script never
orders an attack on a court France has just signed with, so the dial is inert
here. It is not inert in general.

---

## 3. The P1 — "The Peace That Never Was" (PR-1)

### What was measured

`cmd-historical`, turn 4. France accepts Britain's settlement offer through the
mailbox: *"Settlement Ratified: France vs Austria + Britain + Russia (7 pair(s)
resolved)"*, with a 1,358-gold indemnity **from Britain to France**. Britain
and Austria leave the standing coalition and it dissolves for
`insufficient_members`.

Then, in the same `end turn`, an instrumented replay gives the order exactly:

```
T4  STATE   ... seven pairs WAR -> PEACE ...
T4  LEAVE   Britain
T4  LEAVE   Austria
T4  DISSOLVE  insufficient_members
T5  FORM_COALITION  qualifying=['Austria','Britain','Hanover','Naples',
                                'Ottoman','Russia','Sardinia','Sweden']
       via ... advance_turn < process_coalition_turn
T5  DECLARE Britain -> France
T5  DECLARE Russia  -> France
T5  DECLARE Austria -> France
       ... and five more
```

The rail then reads *"Britain has declared war on France, shattering the Peace
Treaty, with 4 allied courts poised to follow."* Four coalitions formed in
forty turns on that seed; seven on austerlitz.

### The root

`coalition.qualifies_for_coalition` asked three questions: relation < −10, not
a vassal, not already at war. A court that ratified a peace seconds earlier
passes all three — its relation is deeply negative *because* of the war it just
ended. `form_coalition` then loops `new_belligerents` and calls `declare_war`
with no gate at all. `armistice_cooldowns`, the store every other war-entry gate
consults, is **not written by any peace path** and **not read by the coalition**.

A court at OPEN_BORDERS with France is enrolled on the same terms — measured,
the Ottoman Empire, `OPEN_BORDERS -> WAR`. That one is the anti-hegemon
mechanic working as designed and is left alone.

### The fix

Derived, no new serialized field, no new write. At the moment
`form_coalition` runs, `world.war_instances` already carries the war's
`ended_turn` and a durable `participant_meta[n]["side"]`. A court whose war
against the target ended inside `FRESH_PEACE_FLOOR_TURNS` is not enrolled as a
NEW belligerent; the already-at-war arm is untouched, the coalition still forms
around whoever is free to fight, threat keeps accruing, and the court joins the
next one once the floor lapses. That is Pressburg: a peace buys time, not
immunity. Opposite sides are required, so two co-belligerents are never
exempted from a coalition against one of them, and a court's own `exited_turn`
outranks the war's end whenever it is present.

⚠ **`FRESH_PEACE_FLOOR_TURNS = 5` — RULED, FOR USER CONFIRMATION.** It is a
new constant with no prior blessing. 5 matches the `armistice_cooldowns` value
the engine already uses and is the smallest number that removes the same-turn
annulment. The natural larger candidate is the **8** that
`settlement_third_party.PAIR_EXIT_TRUCE_FLOOR_TURNS` gives an AI-vs-AI pair
exit — a peace the player negotiates is arguably owed at least as much.

### Measured effect, honestly

The gate's reach was measured, not assumed:

| board | predicate evaluated | enrolments blocked |
|---|---|---|
| ambient historical (passive France) | 39 | **0** |
| COMMANDED historical (`--diplomacy accept`) | 367 | **232** |

That is why `BASELINE_SERIES` and M1–M7 are byte-identical **without a
re-record** — the passive France the harness drives never signs a peace, so no
France pair ever carries a fresh war end. It is a fact about the harness's
answer policy, not evidence that the fix is inert.

Nine of twelve re-run arms are byte-identical. Three move, all COMMANDED — the
only arms where France signs treaties — and they do **not** move in one
direction:

| seed | Fr@40 before | after |
|---|---|---|
| historical | 23 | **29** |
| austerlitz | 24 | **20** |
| marengo | 21 | 21 |

Mean +0.7 provinces. On austerlitz France ends **weaker**: the great powers'
peace holds, so the minors coalition instead and France fights a different war.
The fix changes the shape of a campaign without a systematic balance tilt.

**What it does not fix.** Coalitions still churn — up to **ten** in forty turns,
forming and dissolving as members peace out. That is a design question with an
owner, not a defect I should re-balance blind, and it is filed as **PR-D1**.

---

## 4. The mission system (the standing question)

The diplomatic mission system — `world.active_diplomatic_mission`, Talleyrand
sent abroad on a standing errand — was audited end to end. It is **mechanically
live**: four of five reachable types do real work, and `GATHER_INTEL`'s
five-turn intel grant is genuinely distinct and correctly wired. It was also
**one bug away from being unusable after its first completion**.

| id | what was wrong | P |
|---|---|---|
| **MS-1** | `active_diplomatic_mission` is never cleared when a mission COMPLETES (that is what lets the ledger say what was achieved). Three consumers checked `completed`; the Cabinet's own availability gate did not. After the first intelligence mission finishes, **every mission row for every court reads "Mission already active" for the rest of the campaign** — while the top bar beside it says Talleyrand is idle. The dict is serialized, so the lockout survives save/load. | **P1** |
| **MS-3** | Every displayed effect figure was the raw table constant while the tick multiplies by the diplomat's skill. The shipped Talleyrand is skill 10, i.e. ×1.5 **always** — so the game advertised "+5 relation per turn" beside a tick paying **+8**, on every surface, in the player's favour. | P2 |
| **MS-5** | The undermine mission's only per-turn feedback used a template naming `{nation}` and `{value}` while its producer sent `ally` and `delta` — so `_format_dispatch_event_text` caught the KeyError and printed the template **raw**, braces and all, every turn it ran. | P2 |
| **MS-2** | The DP-collapse cancellation carried the `player_mission` fog rule, which asks — at dispatch-build time — whether the world still holds a mission aimed at that court. The branch had just deleted it. The mission died after three starved turns and the briefing **could never say so**. The elimination exit queued no dispatch event at all. | P2 |
| **MS-7** | An `UNDERMINE_ALLIANCE` mission moves target↔ally; the ledger's progress readout read **player↔target**. Ten turns of undermining Austria\|Prussia from 60 to 10 rendered as *"Hostile → Wary (+10, 10 turns)"* — a positive delta on a pair the mission never touches. | P2 |
| **MS-9** | `IMPROVE_RELATIONS`, `COURT_NATION` and `REASSURE_ALLY` have no duration and no completion arm, and relations clamp at ±100. At the ceiling the mission drew 1–2 DP a turn **forever** for a relation change of zero, with the ledger still printing its full effect and "Ongoing". DP does not accumulate and regen is 5/turn, so that is a silent permanent tax of up to 40% of the diplomatic budget. | P2 |
| **MS-10** | Two call sites pause a mission while Talleyrand carries a proposal abroad. The resume arm had no `talleyrand_state` guard, so the next tick un-paused, charged the DP and applied the full effect while the diplomat was provably elsewhere. Both writes were inert. | P3 |
| **MS-6** | The undermine row was the only row in the diplomacy list that did not state its gate: enabled at 2 DP against a court with no alliances at all, dead-ending in a Dismiss-only refusal. | P3 |
| **MS-4** | Four of five mission descriptions carry their own preposition. The flagship one did not: *"begin efforts to improve relations Austria"*. | P4 |
| **MS-8** | `CONTINENTAL_SYSTEM` was priced in two tables and reachable from none — no parse keyword, no description, no wizard row, no effects entry. Removed (GR9). The one test that named it asserted a dict literal and executed no production code; it is now a reachability census over every priced type. | P4 |

All ten are fixed. **What is still missing is exposure, not machinery** — and
that is filed as design, not as defects: the system is absent from the Strategic
Ledger, the notification rail, the campaign log's live events, the tutorial and
the help text, and `COURT_NATION` is strictly dominated by `IMPROVE_RELATIONS`
per DP. See `DESIGN_REFINEMENT.md` §Playtest Re-Score, rows **PR-D2** and
**PR-D3**.

---

## 5. "The Nation Is Not An Adjective" (PR-2, PR-4)

Measured across nine 40-turn boards: 68 × *"A Prussia envoy has arrived"*, 67 ×
*"A Denmark envoy"*, 65 × *"A Hesse envoy"*, 29 × *"A PapalStates envoy"* — the
last a raw camelCase tag reaching the player, which R7 forbids outright. Plus
*"the France fleet"* in the Trafalgar headline, *"Talleyrand has departed for
the Russia court"*, *"Vassal KingdomOfItaly joined France's war"*, *"Portugal,
Saxony and PapalStates rebuff Prussia"*, and settlement rails listing
`France + Spain + Holland + Bavaria + KingdomOfItaly vs …`.

`COALITION_SPEC` §3f authors **"The Coalition of [Leader Nation]"** rendered as
the adjective — "The British Coalition", "The Second Austrian Coalition". The
code interpolated the raw tag: **"The Fourth Russia Coalition"**, **"The
Seventh Austria Coalition"**, and once the ordinal map ran out at seven, **"The
8th Austria Coalition"**. `display_names.nation_adjective` had held the correct
form all along and no producer called it.

Fixed at the single source in every case: a derived `{x_display}` /
`{x_adjective}` suffix resolved at the dispatch fill site, `nation_adjective`
in the coalition namer, the ordinal map extended through twelve, and
`display_nation` at the three producers the template fix did not reach.

A **fifth** producer survived that pass and was found by re-measuring rather
than by reading: the settlement rail's war label, composed by several
functions in two shapes (`X vs Y` and `A + B + C vs D + E`), every one of them
joining tags. Rather than chase each producer, `humanize_war_label` runs at the
**render** chokepoint — the one place a war label becomes prose — splitting only
on the separators the producers use, so a display name containing a space
survives and an unknown token is left exactly as it was.

Fresh digests now read *"An envoy from the Papal States has arrived with a
proposal."*, *"The Eighth Austrian Coalition"*, *"the French fleet"*,
*"Britain tears up the Peace Treaty to do it."* and *"Settlement of France +
Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria + Russia"*.
A 40-turn commanded run on the shipped tree contains **zero** raw nation tags
in game prose; the one remaining occurrence is a driver-side digest line
(`LETTER PapalStates:`), filed with PR-X5.

`nation_adjective` was also **inventing demonyms for the NA-6c carve tags** —
"Duchyofwarsawian", "Romanrepublician", "Polandian" — which are real runtime
nations. The table gained the four carve rows, and the derivation now refuses
to coin a word for any compound tag, degrading to the display name instead.
Without that, the envoy fix would have shipped *"An envoy from the
Duchyofwarsawian court"*.

**PR-4.** The most frequent dispatch headline on the board — 13 of the distinct
headlines across twelve runs — is *"Sire — Britain and France are at war. He
tears up the Peace Treaty to do it."* The cause clause, landed in FA slice 17
Phase 4 the day before, opens with a pronoun that reads only if the sentence
before it named one court. It names two. The clause now names the declarer.

---

## 6. The five rulings under play

Each was observed, and the two that a digest cannot show were probed directly.

| ruling | observed | evidence |
|---|---|---|
| **FA-D29 / FA-S17-1** — a reinforced side bleeds by the men it commits | ✅ firing | 101 battle lines carry the `own corps` label, e.g. `⚔ Ney (lost 1850, own corps) vs Mack (lost 15045) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte …` ⚠ the label is stamped for the **attacker only**; a reinforced defender's figure is his own corps and carries no label, so a digest-only reading understates his field |
| **FA-D4** — every boot war carries the declaration's defensive purpose | ✅ firing | at turn 1, **7** `war_objectives` entries, both sides of every `starting_wars` pair at `defense`, and `build_active_wars` carries the objective hint. Structurally invisible in a Mode-A digest (the driver prints the headline only) — probed |
| **FA-S2-D1** — the enemy waits one turn for a cornered corps | ✅ firing | 29 `last_stand` questions reached the player across the runs, e.g. *"Lannes is cornered at Franconia with 3,842 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout."* |
| **FA-D23** — a Broken marshal brings half his weight | ✅ firing | probed: `_pair_contribution_scale(Ney, Davout)` is `1.0` at trust 100 and **`0.5`** at trust 0. ⚠ invisible in play — the only copy that fires is slice 4's *"he and {lead} are at odds"*, which names the **relationship**, not trust |
| **the FA-D27 re-open** (dated by FA-S17-D6) | **does not fire** | commanded arm, post-fix: Fr@40 = 29 / 20 / 21, Fr@30 = 29 / 23 / 26. 0 of 3 seeds below 20 |

**The three declined rulings** — evidence noted, none re-opened:

* **FA-S17-D1** (defence tick model; re-opens on *"a measured campaign in which
  the cap binds on a majority of at-war pairs"*). Not observed binding on any
  arm. No change.
* **FA-S17-D2** (the gold sink, owner EC-2 pass 2). **The strongest measurement
  yet.** `--diplomacy propose`, turn 30: **82,524 gold**, risen monotonically
  from 2,485 while France held 26 of 28 provinces and threat FELL 68 → 44. The
  commanded arm ends at **88,556**. On the same boards the dispatch headline
  reads *"the levy has stood open 25 turns. 150 gold puts 10,000 foot in the
  line at Paris"* — a purse **590×** the price of the only thing it names. The
  brake works (state charges spike to 2,887/turn during a war) and then
  releases at peace, exactly as EB-1 blessed. There is nothing to spend it on.
* **FA-S17-D7** (vassal tension for a competent Emperor, owner the FA-D27
  balance owner). Reproduced exactly: **10** rebellion events across the five
  unattended ambient arms, **0** across the three commanded arms.

---

## 7. The re-score

Scored against the September 11, 2026 baseline. Every figure below is from a
run this session produced; a pillar I could not reach keeps its prior score and
says so.

| pillar | Sept 11 | now | evidence |
|---|---|---|---|
| command & parsing | 7.5 | **7.5** | golden corpus **681/681** mock; every refusal names its reason AND a remedy (*"Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais."*, *"Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table."*). ⚠ the live-parser arm could not run |
| marshal drama | 7.0 | **7.5** | 113 marshal petitions across twelve runs in three kinds — six named marshals' `jealousy_confrontation`, the `fontainebleau` collective, `rivalry_confrontation`; 29 last-stand questions reaching the player; reinforcement observations that name who came and who did not. The Sept-11 drop was attributed to a harness defect (the driver never read `deferred_marshal_petition`) fixed in Phase 3; with the fix the channel is the densest source of drama on the board |
| combat legibility | 7.0 | **7.0** | battle lines carry committed-strength attribution and a named reinforcement sentence; 31 diorama popups. Held down by the attacker-only `own corps` label — there is no `defender_casualties_scope` anywhere in the backend |
| narration | 7.0 | **7.0** | held, not raised: the pillar's measured defects this session (nine raw-tag producers, the dangling-pronoun headline, the coalition naming) were **fixed in session** and re-measured on fresh digests. Residual: an annihilated France is told *"the diplomatic winds favor us"*, and `intent_hardens` / `intent_eases` fired **0 times in twelve runs** |
| economy | 6.0 | **6.0** | see FA-S17-D2 above. The arithmetic is sound and the brake is real; the sink is not |
| diplomacy | 6.0 | **6.5** | PR-1: a ratified settlement now survives instead of being annulled inside the same `end turn`; 232 enrolments blocked on the commanded board. Held down by coalition churn (up to ten in forty turns) and by the settlement machinery's own frequency |
| AI aliveness | 7.5 | **7.5** | 48 third-party peace beats (*"THE CONGRESS: Spain and Switzerland make peace without France"*), 52 `design_promoted` (Stage E emergent designs), AI expeditions landing at Lisbon and Munster unprompted. ⚠ `volte_face` 0 and the Stage-F intent lines 0 in twelve runs |
| vassals | 6.5 | **6.5** | 10 rebellion events on the unattended arms, 0 on the commanded arms — the FA-S17-D7 shape reproduced |
| naval | 7.0 | **7.0** | one TRAFALGAR (*"Nelson's line has shattered the French fleet — 23 sail lost in a decisive action"*), 35 expedition landings, and a Grand Diversion that quotes its own odds AND its own trap: *"even a success leaves London-Normandy shut — 41 effective against 50, and 45 is the least that opens it"* |
| UI/UX | 7.5 | **not reached** | no Godot binary in this environment. Prior score stands untouched; no `.gd` file was changed |

**Directional ≈6.9 → ≈7.0.**

---

## 8. Byte-identity, stated with its reason

* **`BASELINE_SERIES`: byte-identical, no re-record.** Measured reason: the
  PR-1 predicate is evaluated 39 times on the ambient historical board and
  blocks **0** enrolments, because the driver's answer policy declines every
  incoming offer, so no France pair ever carries a fresh war end. PR-2 and PR-4
  touch prose only. MS-* touch a system no AI nation runs
  (`_process_mission_effects` is hard-coded to the player).
* **M1–M7: byte-identical, no re-record.** The harness has no coalition
  formation, no settlement and no diplomatic mission in it.
* Nine of twelve re-run playtest arms are byte-identical; the three that move
  are the three that sign treaties, and the attribution is in §3.

---

## 9. Method notes

* **A mutation sweep caught two of my own defects before they shipped.** The
  applied-figure helper used `int()` where the tick uses `int(round(...))` —
  the same shown-vs-applied gap one rounding mode down, caught by a standing
  pin on its first run. And six of my own pins came back INERT; four were real
  weaknesses (one **vacuous**: it asserted against three courts while the
  engine picks the coalition leader from ALL members, which on this board is a
  fourth), one was a bad mutation, and one was unpinnable by value and was
  re-pinned structurally. Final: **29 mutations, 29 killed, 0 INERT**.
* **A local import shadows a whole function.** The first cut of the vassal
  call-to-arms fix used a function-scoped `from backend.display_names import
  display_nation` inside one arm of `format_event_oneliner`, which made the
  name local for **every** arm and raised `UnboundLocalError` six hundred lines
  away. Three endpoint pins caught it.
* **My first cut of MS-2 was wrong and its own pin said so.** I moved the
  cancellation event above the line that deletes the mission, reasoning that
  the fog rule could then see its subject. The fog is evaluated when the
  **dispatch is built**, a turn later — queue order is irrelevant. The fix is
  the fog rule, not the ordering.
* **Do not edit backend sources while the suite is running.** Two full-suite
  runs failed on *different* `inspect.getsource` census pins, each of which
  passed in isolation; the third run, with no concurrent edits, was clean. The
  structural-census idiom is not robust to a file changing mid-run.

---

## 10. Routed, not fixed

Defects → `BUG_FIXES.md` §Playtest Re-Score (**PR-X1..PR-X5**).
Design → `DESIGN_REFINEMENT.md` §Playtest Re-Score (**PR-D1..PR-D4**).

### The top five missing features

1. **A gold sink** (FA-S17-D2, owner EC-2 pass 2) — a peaceful France banks
   88,556 gold against a 150-gold levy. Nothing in the game can absorb it.
2. **A defeat condition.** `sandbox_mode` suppresses victory *and* defeat on
   every Europe world. Measured: ambient-marengo holds **0 provinces** from
   turn 37 and the campaign runs four more turns, with the briefing telling an
   annihilated France that *"the diplomatic winds favor us"*. Owned by the
   Victory & Objectives pass (ROADMAP 12–13) — but the *legibility* of the
   collapse is PR-X1 and is not owned there.
3. **Missions on the surfaces the player actually reads** (PR-D2) — absent from
   the Strategic Ledger, the notification rail, the campaign log, the tutorial
   and the help text.
4. **A reason for coalitions to be rare** (PR-D1) — ten in forty turns is a
   revolving door, and each one costs the settlement system its meaning.
5. **A live-parser regression gate that runs without a key.** The
   `--llm anthropic` arm is the only check on the escalation path and it cannot
   run in CI or in a keyless environment.

### The top five broken things (after this session's fixes)

1. **Coalition churn** — up to ten coalitions in forty turns, each forming and
   dissolving as members peace out (PR-D1).
2. **The collapse state is not legible** — a France at zero provinces is told
   the diplomatic winds favour it, and the war-purpose line lists twenty
   provinces it no longer holds (PR-X1).
3. **`defender_casualties_scope` does not exist** — a reinforced defender's
   casualty figure is his own corps and is not labelled, so FA-S17-1's own case
   is the one a reader cannot see (PR-X2).
4. **FA-D23 has no copy of its own** — a Broken marshal's halved contribution is
   reported as the pair being "at odds", which is the relationship vocabulary,
   not trust (PR-X3).
5. **The Stage-F intent narration never fires** — `intent_hardens` /
   `intent_eases` produced zero lines in twelve 40-turn runs (PR-X4).
