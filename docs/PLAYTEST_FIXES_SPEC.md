# Playtest Fixes — row **PT**

> **v1.0 — queued August 10, 2026 from the 19-turn France/1805 playtest held the
> same session.** Evidence of record = **`docs/audits/PLAYTEST_CA9_2026_08_09.md`
> (authoritative)** + the fleet's verbatim report
> `docs/audits/PLAYTEST_CA9_2026_08_09_FLEET_REPORT.md`. Raw campaign: 108
> request/response pairs, `LLM_MODE=anthropic`, master `26bbcbe`.
>
> **This spec owns what the playtest ROUTED.** Nothing was fixed in-session — the
> pass was deliberately read-only so the campaign state stayed a clean witness.
>
> **The finding is the shape, not the count.** CA9's through-line —
> *every system computes the right answer and then tells the player a different
> one, and the divergence always points the way that makes them commit* — is not
> closed. It **migrated**. **Three of the five P1s are regressions introduced by
> the August 9 fixes**, each one an honest computation destroyed at a seam
> downstream of it. That is the pattern this spec exists to close, and it is why
> **PT-A is first and indivisible**.
>
> **Verification standard.** Every claim below survived a find→refute fleet (47
> agents) that killed five findings and downgraded eight. Where a claim's
> *mechanism* was corrected the corrected mechanism is what is written here; the
> superseded version is in the audit memo §5. **Do not re-derive a fix from the
> audit's first-pass wording — read the row.**
>
> **Reading order:** §1 the shape · §2 the slices in build order · §3 acceptance ·
> §4 what needs a user decision · §5 build order · §6 the traps this playtest paid
> for.
>
> **Baseline at queue time:** suite **17,144 passed / 3 skipped**, ruff clean,
> master `26bbcbe`.

---

## 1. The shape

| # | The honest computation | The seam that destroys it | Row |
|---|---|---|---|
| 1 | `_command_option` returns `enabled: False` + a stated reason | `refresh_petition_affordability` overwrites the flag and pops the reason | **PT-A1** |
| 2 | The resolver rolls each reinforcer for arrival | The preview prices them all in as certain, and the row-2 gate reads that band | **PT-A2** |
| 3 | The executor has a fall-through that lets a typed order escape a hard stop | CA9-N5's rewrite of the failure string made it unreachable for every typed string | **PT-A3** |
| 4 | `check_redemption_threshold` fires the branch correctly | `_route_response_ui` returns on the first match and redemption is last | **PT-B1** |
| 5 | The peace is ratified and the pair leaves `active_diplo_keys` | `opponent_display` is rebuilt from `side_by_nation` with no live-WAR check | **PT-B2** |
| 6 | The executor builds `suggestion: "Try 'move to Rhineland'"` | No consumer in `main.py`; 1 of 108 responses contains the word | **PT-H1** |
| 7 | Four phases fill `pending_dispatch_events` | `advance_turn`'s first act wipes the queue | **PT-E1** |
| 8 | `process_autonomous_attacks` returns a full battle result | It is assigned to a local nothing reads | **PT-F1** |

**Pillar scores from the same campaign** (seven independent judges; calibration in
brackets): marshal drama 7.0 [7.5] · narration 6.5 [6.0] · command 6.5 [7.0] ·
AI aliveness 6.5 [7.0] · combat legibility 6.0 [6.5] · economy 6.0 [6.5] ·
diplomacy 6.0 [6.5]. **Directional ≈6.4 [≈6.9]. Narration is the only pillar that
rose**, and it is held under 7 by *volume*, not quality.

---

## 2. The slices

### PT-A — The three regressions *(no gate; build first, indivisible)*

The August 9 queue landed real work and then lost it at a downstream seam. Each of
these is small; together they are the argument that the seam, not the computation,
is where this codebase's defects now live.

#### PT-A1 — the delivery seam must be subtractive

**Measured.** Turn 2, Murat's jealousy confrontation. Option `command`,
`cost_note: "2 AP"`, **`enabled: true`**, `detail: "There is no enemy within his
reach to send him against."` `POST /marshal_petition_response {"choice":"command"}`
→ `success: false`, the same sentence, **0 AP charged**, and the petition is gone.
**6 of 10 petitions in the campaign shipped the arm enabled with its reason
erased.**

**Mechanism.** `jealousy._command_option` (`:1557-1579`) builds it honestly:
`{… "unavailable_reason": reason, "enabled": False}` when
`command_arm_availability` refuses. `refresh_petition_affordability`
(`:1621-1636`), run unconditionally at delivery (`main.py:1297-1304`), then does
`option["enabled"] = ap >= cost` for anything carrying an `ap_cost` and
`option.pop("unavailable_reason", None)` when affordable. The July-25 IGR-1 fix (AP
baked at zero) over-corrected: it now re-enables arms disabled for reasons that
have nothing to do with AP.

**The fix.**
1. `refresh_petition_affordability` may only ever **downgrade**:
   `option["enabled"] = bool(option.get("enabled", True)) and ap >= cost`, and pop
   `unavailable_reason` **only when affordability was the sole gate**.
2. `handle_petition_response` (`:1954`) must not null
   `world.pending_marshal_petition` until the chosen arm returns `success: True`.
   Today the pop runs before `_apply_confrontation_choice`, so a refusal destroys
   the decision. Same for the popup-queue mirror.

**Acceptance.** A petition whose `command` arm has no legal target, delivered with
4 AP in hand, renders `enabled: False` with its reason intact; and answering any
arm that returns `success: False` leaves `pending_marshal_petition` unchanged and
re-servable. **Re-site the 8 `TestHonestAvailability` assertions through the
refresher (or the `/command` payload)** so they bind where the player reads —
today they pin the builder, which is why this shipped.

**Do not** solve this by deleting the refresher. It exists because the jealousy
pass runs before `advance_turn` refills AP, and removing it re-opens IGR-1.

#### PT-A2 — the muster band must count arrivals, not eligibility

**Measured, turn 15, one terminal message:**

```
MUSTER — Davout (18,874; 39,240 if all march) vs ArchdukeCharles (31,241 men) at Munich
  — the balance of force looks favorable.
  WILL JOIN — Murat: will march to the sound of the guns — but he and Davout are
  at odds; expect about half his weight
[Combat] Davout attacks cautiously at unfavorable odds alone. (Cautious: -10% attack)
~ Murat could not reach the battlefield in time.
~ Massed effective strength: 18,874 (lead) + 12,806 committed (Lannes) = 31,680.
```

A **24% over-promise**, and the outcome was a brutal stalemate at 2,275 French dead.

**Mechanism.** `_build_muster_preview` builds `will_join_marshals` from
`_muster_reason` (`combat_executor.py:692`), a deterministic **eligibility** ladder
— broken / fortified / literal / hostile / grievance — that never consults arrival.
It feeds that list straight into `_committed_reinforcement_strength` (`:327-363`),
`α · strength · effectiveness · attack_mod · rel_scale` — a pure **strength**
haircut with **no arrival term** — and passes the result to
`inferred_attack_odds_band`. Arrival is a *separate* roll in the resolver
(`:1270-1271`): `score = _calculate_arrival_score(...)`,
`threshold = 60 if has_explicit_order else 65`, `arrived = score > threshold`.
`muster_gate_arms` (`objection_v2.py:990`) then keys on the band.

**Consequence — this is why CA9 row 2 reads FAIL.** The gate is built exactly as
ruled and both its terms are load-bearing, and it **never armed once** in 19 turns:
three previews, `favorable` / `even` / `favorable`. The user commissioned it so a
cautious marshal stops before a disaster; an upstream number defeats it. It also
reproduces precisely the bias `_defender_muster`'s own docstring names — *"the
resulting error always pointed at 'favorable', which is the direction that makes
the player commit"* — which CA9-F1 fixed for the defender's term.

**The fix.** Weight each `will_join` contribution by its arrival probability before
the band is computed. One number closes three things. Ship
**`combat.py:424-425`'s inverted `" alone"`** in the same commit — the suffix
prints **iff `committed_attacker > 0`**, i.e. iff he is *not* alone (**PT-D1**).

**Recorded alternatives, if the probability weight proves unstable:** split the
display into *certain / likely / may not come* and band on the certain subset; or
give row 2 a second band computed from certain arrivals only. **Do not** simply
lower the band thresholds — that moves M1–M7 and does not fix the over-promise.

**⚠ Harness.** This changes `committed_attacker`, which feeds the odds band and
therefore CO-2's arithmetic. **Run M1–M7 before and after and attribute any move
by flip experiment.** A `BASELINE_SERIES` move is plausible; if it happens, record
the cause, do not re-record blind.

#### PT-A3 — a hard stop must not swallow an unrelated valid order

**Measured.** A war-purpose hard stop ate `Davout, march to Munich and relieve the
Bavarians` and answered *"I don't understand that choice, Sire."* And the phrase
the engine's **own** raising message offered — *"choose our purpose, or **let the
province stand**"* — is refused by the router that receives it (`back out` works).

**Mechanism.** CA9-N5 rewrote the dialogue failure string and in doing so killed
the executor fall-through that let a typed order escape a hard stop
(`main.py:2147-2153`; `diplomatic_executor.py:3499` vs the live arm at `:3396`).
The fall-through is now **dead for every typed string**.

**The fix.** Make the hard-stop block behave like the objection block: when
`match_dialogue_answer` returns `None` on a hard stop, **do not pass the sentence
to the choice resolver at all** — return the objection-shaped refusal that names
what is waiting, says nothing was relayed, and quotes the words that clear it.
That kills the swallow, retires the dead escape hatch, and stops the game claiming
it misunderstood a sentence it never tried to read. Separately, add the raising
message's own phrase to the router's vocabulary, or stop offering it.

---

### PT-B — The two silent losses *(no gate)*

#### PT-B1 — the redemption branch is destroyed at the moment it is offered

**Measured.** Turn 12, one response carried **both** `awaiting_redemption_choice`
for Bernadotte (trust 2 — Grant Autonomy / Transfer to Staff / Dismiss) **and**
Denmark's standing non-aggression pact. `_route_response_ui`
(`main.gd:1325-1339`) walks `_post_hud_response_routes` and returns on the
**first** match; `incoming_proposal` is index 4 and `redemption_event` is **last**.
The redemption never appeared again in the following 19 responses.

**There is no recovery.** `check_redemption_threshold` returns `None` forever once
`redemption_pending = True` unless trust climbs back above 20 (from 2);
`pending_redemption` is not a PopupQueue slot; and although `GET
/pending_redemption` exists at `main.py:3019`, **`api_client.gd` never calls it**.
The collision is not rare — an unanswered envoy rides the passthrough on every
response until it lapses.

**The fix.** Give redemption the stash the client already has three of
(`_stash_proclamation`, `_stash_envoy_digest`, `_stash_diorama`, whose own comment
reads *"anything that drops the response here loses the moment permanently"*):
stash on arrival, raise on control-return. Wire `GET /pending_redemption` in
`api_client.gd` as the belt-and-braces recovery.

#### PT-B2 — the war HUD outlives the peace

**Measured.** Turn 14: the notification says *"France and Hesse have signed a Peace
Treaty"*, `previous_state: WAR → new_state: PEACE`, and `France|Hesse` is gone from
`active_diplo_keys` — in the **same payload** whose `opponent_display` reads
**"Britain + Austria + Hesse + Russia"**. It stayed wrong for **twelve consecutive
responses**, to the end of the campaign. Separately, from turn 10 the panel showed
a `status: war` row naming Austria *and* a `status: armistice` row for Austria.

**Mechanism.** `war_status.py:500-521` builds `opponent_display` from every nation
on the enemy side of `side_by_nation`, with no check that the nation still has a
live WAR pair with France. `side_by_nation.pop` only fires when a nation has no
remaining active pair **anywhere** — Hesse kept `Hesse|Holland`, so it stayed. Two
lines below, the **score** is aggregated over `row_opponents` only, so the name
list and the number on the same card are computed over different belligerent sets.
The `[A-F5]` comment shows the author solved exactly this for the score and not for
the name.

**The fix.** Filter `enemy_participants` by a live WAR pair with the player, the
same predicate the score already uses. The armistice double-render
(`war_status_panel.gd:268` / `:350`) is the same slice: a court in ARMISTICE is not
a current belligerent row.

---

### PT-C — The numbers on the buttons *(no gate)*

| id | claim | site |
|---|---|---|
| **PT-C1** | Insist quotes **−15** trust and the engine charges **−18** | `objection_dialog.gd:141`; `disobedience.py:1345`; `meta_executor.py:1738-1740`; `defiance.py:249-256` |
| **PT-C2** | The strategic-objection buttons render hardcoded −10/+12/+3 and phantom AP costs | `disobedience.py:2238-2284`; `objection_dialog.gd:222-247`; `strategic_executor.py:2106-2108` |
| **PT-C3** | The end-turn financial line prints **Upkeep unsigned** among signed siblings | `meta_executor.py:294-320` |
| **PT-C4** | The dispatch's `(+N)` treasury change disagrees with the banner Net on **10 of 18 turns**, always overstating | `dispatch.py:1829` vs `meta_executor.py:283`; `combat_executor.py:2192` |

**PT-C1 in detail, because it cost a gameplay branch.** The engine applies the
quoted `insist_penalty` (−15), then — for STRONG/EXTREME concerns, i.e. exactly
where the defiance roll runs — `apply_defiance_outcome(marshal, "failed_roll",
world)` applies a further `modify_trust(-3)` and sums both into `trust_change`. The
failed-roll branch never writes `"defiance": True` (that key is only set in the
roll-*succeeds* dict), and `main.gd:3198` gates the "Trust -18" disclosure on
`response.get("defiance", false)` — so the branch that would disclose it is
unreachable on this path. Measured: Bernadotte at trust 17; at the quoted −15 he
lands at 2, at the real −18 he lands at **0** and fires the redemption event that
**PT-B1** then destroys. *Fix C1 and B1 together or the second bug hides the first.*

**PT-C4 is the definitional half of CA9-N11, which is not fully closed.** Every
*named* component agrees on all 18 turns; only the total differs, because one
surface **measures** the treasury and the other **sums declared components** — and
the EC-W3 `[Materiel]` bill has no declared component. It is charged two different
ways depending on who fought: the player's own turn is outside Net by design, the
enemy-phase copy is inside it by construction and absorbed into the `Other`
residual. Give `[Materiel]` a named component, or make both surfaces measure.

*Positive result to record while here:* a dedicated sweep asserted
`Income + Requisitions + Overseas − Occupation − Contributions − Charges −
Dotations − Rentes − Admiralty − Blockade − Upkeep + Other == Net` on **all 18
turns with zero drift**. **The ledger arithmetic is exact.** These are legibility
defects, not losses.

---

### PT-D — The battle report tells the truth *(no gate)*

| id | claim | site |
|---|---|---|
| **PT-D1** | *"at unfavorable odds **alone**"* prints **iff he is not alone** | `combat.py:424-425` — ship with **PT-A2** |
| **PT-D2** | The muster `withholds` `≤0.0` arm renders a **pair** property as the *joiner's* personal grievance | `combat_executor.py:927-936` reading `:313-325` |
| **PT-D3** | The post-battle reason arm is one-directional, so the same no-show is then blamed on the roads | `combat_executor.py:1316-1319`, copy at `:6039-6048` |
| **PT-D4** | The observation generator has **no arm** for rout / broken morale / province lost | `battle_report.py:840-851` |
| **PT-D5** | Terminal and Berthier's report print two different French casualty figures under the identical label `Casualties:` | `combat_executor.py:1547-1550`; `main.gd:2111` vs `:2211` |
| **PT-D6** | A destroyed army reports more casualties than it had (`Mack 15,815/15,437`) | battle casualty reconcile |

**PT-D2/D3 are one bug seen from two ends.** Measured turn 7: the row on **Ney**
read *"but **he** is nursing a grievance and will bring NOTHING"* — Ney held no
grievance; **Bernadotte**, the lead, was `jealous_of: Ney`. `_pair_contribution_scale`
is symmetric (`lead_jealous or ally_jealous`) and the copy renders it as the
joiner's personal state. Then the post-battle classifier assigns
`grievance_withheld` **only** when `candidate.jealous_of == primary.name`, so with
the lead aggrieved the arm cannot fire and it falls through to `low_score` →
*"Ney could not reach the battlefield in time."* The A6 fix that exists precisely
to *"stop narrating character as weather"* is blind to half its own cases.
**Fix:** branch the row copy on which side is jealous; widen `:1316` to the same
symmetric test the preview uses. The `<1.0` arm (*"he and {lead} are at odds"*) is
already symmetric and needs no change — which is itself evidence the sibling is an
oversight.

**PT-D4.** `The Great Battle of Milan` — Massena broken, routed, Milan lost —
observation: *"A standard affair. Nothing unusual to report."* Not bad luck:
Massena took 26.2%, just under the 30% `lost_costly` threshold, and grep confirms
**zero** references to `forced_retreat`, `routed` or `region_conquered` anywhere in
the observation selector.

---

### PT-E — The turn report becomes readable *(no gate)*

The narration pillar is the only one that rose, and it is held under 7 by
**volume**: 101 dispatch lines over 14 turns (7.2 per morning, 45% jealousy, 30%
supply, the identical vassal remedy tail eleven times) and **~149 fog sentences
against 63 real enemy actions**.

#### PT-E1 — the dispatch can never narrate anything that happens during the turn

`advance_turn`'s first act is `self.pending_dispatch_events = []`
(`world_state.py:8057`), and it runs **after** the enemy phase, the AI diplomatic
phase, strategic orders and the jealousy pass have filled that queue. Across **18
consecutive dispatches, not one carried a `nation_eliminated` or war-declaration
line** although three fired. Kingdom of Italy — the player's own vassal — was
destroyed on turn 2 and the turn-3 briefing carried
`['diplomatic_dp_regen', 'paymaster_subsidy', 'agenda_shift']`. The fog rule on
both lost types is `"always"`: this is **ordering, not fog**.

#### PT-E2 — render `diplomatic_events` in the terminal

`main.gd` has **zero** references to `diplomatic_events`; the block exists at
`dispatch_view.gd:317` and is ~14 lines. Paste it into
`_display_morning_dispatch`. This moves every agenda shift, revanche, subsidy
switch, intent change and third-party peace from a screen nobody opens to the one
the player reads every turn. **Pair with PT-E1 or the rail it renders is empty.**

#### PT-E3 — collapse `turn_events` by family at the view seam

Exactly as IGR-B already does for the campaign log: *"supply cost you 2,027 men at
Tyrol and Milan"*, *"three satellites drifted"*. Cap the block. Let the headline
breathe. **The machinery exists and is proven one surface over.**

#### PT-E4 — collapse the per-court fog line

`main.py:976-981` emits one sentence per hidden court and
`enemy_phase_dialog.gd:96-100` prints every one with no cap, dedupe or collapse.
Measured 7–10 per phase, on **16 of 18 phases**. One sentence naming the courts.
*(This is the F7 surface whose visual sign-off is owed — the sign-off would have
caught it.)*

#### PT-E5 — the enemy phase must narrate a bloodless capture of the player's own soil

`_filter_enemy_phase_by_visibility` (`main.py:1427-1444`) shows an AI action only
if a player marshal is in the battle **or** the AI marshal's post-move location is
FULL. Own soil is PARTIAL by construction, so an enemy marching **unopposed** into
a French province is suppressed — measured three times in three turns (Provence,
Languedoc, Rhineland).

**Scope it honestly:** the player *is* told, in the same response, by a
`home_captured` headline at weight 100, and the campaign log names the captor. This
is a **lost theatre beat on the one screen whose job is reporting what Europe did**
— which is precisely why the NV-9 carve-out (`:1376-1387`) and CA8-15 (`:767-781`)
exist in this same function. Showing it leaks nothing: the same payload already
flips the province on the map and names the marshal in `fogged_forces`.

**Also fix the other direction:** keying on `ai_marshal.location` **over-shows** —
a whole three-hop route through PARTIAL regions renders because the traveller
finished on a FULL square.

#### PT-E6 — `construction_complete` is fog-classed wrong

The event omits `nation` (`world_state.py:5707,5727`), so `_filter_tactical_events_by_fog`
falls to the region arm and passes it at PARTIAL (`meta_executor.py:104-106`).
**7 of 11 leaked**, including *"Construction complete: Supply Depot in Berlin!"*
`FOG_OF_WAR_SPEC.md:327` classes buildings **FULL-only on foreign soil**; the
PARTIAL+ threshold is deliberate for *marshal-state* events. Stamp the owning
nation on the event and class it correctly. (It also earns its row on a
self-contradiction: the terminal announces a watchtower the region panel in the
same payload calls `'none'`.) **P3 — do it here because it is one line.**

---

### PT-F — The jealousy channel finishes *(no gate)*

#### PT-F1 — the autonomous attack is a rumour

`turn_manager.py:184,187` assigns `process_autonomous_attacks(...)` to
`jealousy_attack_results` and **nothing ever reads it** (grep-verified). Measured
turn 5→6: the player was told *"Murat, hungry for glory, has attacked Archduke John
on his own initiative."* and nothing else — no battle event, no `battle_report`, no
casualties, no diorama, no `enemy_phase` entry. Murat went **21,384 → 17,997 men,
morale 100 → 81**, with no supply event to explain it. Reproduced on **all four**
autonomous attacks.

This is the marquee payoff of the whole Jealousy system — a marshal defying the
Emperor — and it lands as a rumour. **Thread the result through the same
propagation seam every other battle uses**, including the diorama link.

#### PT-F2 — an unopposed capture never clears `idle_turns`

The combat-executor unopposed-capture branch (`:4135-4202`) calls `move_to` and
never touches the counter; `movement_executor.py:497` does. The counter therefore
carries the **entire pre-capture history across the conquest**. Measured: Massena
took Provence on turn 5 and the truthful values at turns 6/7/8 are 0/1/2 — all
below the `idle_restless` gate of `>= 3` — so **all three `idle_restless` renders
were spurious**, and `idle_turns` feeds two jealousy gates.

⚠ `test_objection_v2.py:1730 test_idle_turns_reset_on_attack` is **inert** — it
hand-assigns `idle_turns = 0` under a comment reading *"# Simulate what executor
does after attack"* and never calls the executor. Replace it, don't extend it.

#### PT-F3 — the rivalry petition's arms must be priced like their siblings

The §3 pricing work landed on `jealousy_confrontation` only. The rivalry arms
(`:1784-1793`, outcomes `:2256-2300`) still read: *"They settle into cold war; one
may turn openly discontent"* (it is **20%**, and it costs −3 trust and unlocks
defiance) and *"A public gamble on your authority"* for **2 AP** — where the code
has **authority-banded odds**: ≥80 → 50% success; ≥60 → 30% success with a 20%
chance of **−3 authority**; <60 → 10% success with a 60% chance of **−5
authority**. Next to *"For 2 more turns he brings NONE of his 22,000 men"* it reads
like a different game. State the band, the odds and the failure cost, and state the
outcome in state terms (the measured success moved the pair −2 → −1 and never said
so).

#### PT-F4 — the smaller jealousy honesty rows

| id | claim | site |
|---|---|---|
| **PT-F5** | *"any command would restrain him"* — an objected order, a refused order, and answering the objection **all** fail to stand him down | `jealousy.py:2702-2711`; `executor.py:1854-1866` |
| **PT-F6** | The trust warning at <40 advises "more independence"; `grant_autonomy` is only reachable from the redemption event at trust ≤20 | `world_state.py:10642-10649` |
| **PT-F7** | A ladder-shift resolution is narrated **twice** — the resolved bullet already carries the cause verbatim | `jealousy.py:2550-2564` + `:1081-1083` |
| **PT-F8** | *"he has not seen laurels"* is asserted about the **subject** without ever reading his own windowed glory | `jealousy.py:2667-2678` |
| **PT-F9** | The jealousy attack silently deletes the marshal's standing order — the exact case CA9-F13's own comment says it fixed | jealousy attack path |

⚠ **PT-F8 correction, carry it into the build:** the audit's first wording
(*"names a comparator who is not winning"*) is **refuted** — `find_jealousy_target`
draws only from peers strictly above on the ladder, so the comparator necessarily
banked glory in the window, and at turn 2 the same `turn_events` array crowned him.
The clause that is structurally false is the **subject's**.

---

### PT-G — Voice and naming *(no gate)*

#### PT-G1 — the enemy-voice rotation key makes `bank[1]` the default

`rotation_key = world.battle_counts[location]` (`combat_executor.py:5295`) is
**post-increment**, so the first battle in a province is key 1 — and on a
126-province map most provinces only ever see one battle. For a 2-line bank, index
1 *is* the line and index 0 is decoration. **Archduke Charles said *"Even the
Grande Armée bleeds when pressed at the right hour"* in four of his five attacks.**
Doubling the bank would not fix it; fix the key.

#### PT-G2 — `personality_ack` has no marshal term in its key

`_pick(bank, key)` is `bank[key % len(bank)]` (`marshal_voice.py:49-50`) and
`personality_ack` passes `turn + len(str(target))` (`:450`,
`strategic_executor.py:1447-1449`). **No marshal term exists anywhere in the key**,
so two marshals sent to same-length destinations on the same turn say the same
sentence back to back. Measured, consecutive commands: Lannes then Ney, both
*"Good. An army rots standing still."*; Davout and Bernadotte both *"As ordered. I
keep my flanks as I go."* Add the marshal to the key **and** grow the banks —
Ney, Davout and Murat have **3–4 lines total across five situations**.

#### PT-G3 — every marshal's FIRST petition is pinned to bank index 0, and the body has no bank at all

Which is why Murat's (turn 2) and Massena's (turn 7) petitions were word-for-word
identical in **both** `body` and `speaker_line`.

#### PT-G4 — Talleyrand breaks his own Voice Bible on a blocking modal

*"**Sire!** We have a Non-Aggression Pact with Hesse. Declaring war would
**shatter** that commitment…"* (`diplomatic_executor.py:2121-2124`, the only
`Sire!` in the diplomatic layer). `DIPLOMAT_VOICE_BIBLE.md:36` forbids exclamation
marks; `:38` forbids military vocabulary as metaphor. It is the highest-stakes
sentence he speaks. Two DEF-1 incoming-proposal lines drift from their own register
entries in the same pass.

#### PT-G5 — raw internal keys in player prose

| where | what |
|---|---|
| `enemy_phase_dialog.gd:133,308,311,315,330,352` | camelCase marshal keys **~84 times**, with the correctly spaced name three lines below in `enemy_voice` |
| `dialogue_manager.py:392` | mailbox row reads **`Armistice Losing`** while the popup for the same item reads `Armistice` |
| `settlement_offers.py:2588` | *"the offered terms for **war_1**"* — `war_label` sits beside it in the payload |
| `disobedience.py:2252-2254` → `objection_dialog.gd:233` | raw marshal key on a **Button label**, where the terminal's humanizer cannot reach it |
| `emergent_designs.py:306-307` | *"Bohemia **and 1 more provinces**"* — the **modal** rendering, since `EMERGENT_DESIGN_MIN_LOST = 2` |
| Berthier's battle observations | *"ArchdukeCharles"*, *"ArchdukeJohn"* in his own mouth |

*(`Murat pursues ArchdukeCharles` and its campaign-log sibling are **already open
rows in `BUG_FIXES.md`** — do not double-file, fix them here and close those.)*

#### PT-G6 — the live-LLM fallback emits markdown into a BBCode terminal

*"\*Adjusts spectacles nervously\* Sire, I… Might you intend, for example:
`**Marshal Ney attacks Deroy at Swabia**`"* — reachable only in
`LLM_MODE=anthropic`, i.e. the shipping BYOK path, and `main.gd` renders `message`
as BBCode so the asterisks show literally. Constrain the format in
`prompt_builder.py:877-933`.

---

### PT-H — Parser and affordance honesty *(no gate)*

| id | claim | site |
|---|---|---|
| **PT-H1** | The executor **builds** `suggestion: "Try 'move to Rhineland'"` and it never leaves the backend — 1 of 108 responses contains the word at all | producers `combat_executor.py:3909,4219…`; **no consumer** in `main.py` |
| **PT-H2** | *"cannot reach… Range: 1, Distance: 2"* is a dead end that a synonym clears — `Ney, retake Rhineland` refuses, `Ney, march to Rhineland` paths in two hops | `combat_executor.py:3843-3910` |
| **PT-H3** | `Murat, attack the Austrians` sent him at **Shrapnel** (British), one turn after signing an armistice with Austria, and never said so | `parser.py:854-855` |
| **PT-H4** | The levy headline's `open` predicate checks headroom and pool but never the executor's actual gate (a marshal in range); the escalated variant drops the condition the base template carries | `economy_executor.py:1664-1669` vs `:487-495`; `dispatch.py:205-207` |
| **PT-H5** | The clause-guard refusal path bypasses N5's option-naming helper | `main.py:2249-2271` |
| **PT-H6** | Counter-punch says "within 2 turns" in the notification and "immediately after defending" at expiry; measured **one** usable turn | `combat_executor.py:1692` vs `world_state.py:10453-10468` |

**PT-H1 is PT-H2's root cause** — fix H1 and H2 mostly disappears. ⚠ **PT-H3's
mechanism is not what the audit first said:** `parser.py` drops a nation demonym to
`None` **by design** (it is the fix for the earlier "Austrians"→Asturias fuzz), and
auto-targeting then never re-applies the named nation. Do not revert the demonym
rule; carry the nation through to the target filter.

---

## 3. Acceptance

A slice is done when:

1. **The player-facing sentence is the acceptance criterion**, not the field. Every
   row above quotes what the player read; the test asserts the corrected sentence
   reaches the surface named in the row, through the real endpoint.
2. **The pin binds where the player reads.** PT-A1 exists because eight assertions
   pinned the builder while the defect lived in the refresher. Any new pin that can
   pass while the delivered payload is wrong is not a pin.
3. **Mutation-swept.** Every new test must fail when its production line is
   reverted. Report the sweep count and any inert pin found.
4. `ruff check backend/` clean · full suite green · **Godot parse harness EXIT=0**
   for any `.gd`-touching slice · **boot smoke 0 `SCRIPT ERROR`** (the XR-1 rule:
   any `.gd`-touching slice boots the engine once).
5. **M1–M7 recorded before and after.** PT-A2 is the one slice expected to move
   them; if `BASELINE_SERIES` moves anywhere, **attribute by flip experiment** and
   re-record once, consciously, with the cause written down.

**Definition of done for the row:** the three regressions cannot recur — the
delivery seam is subtractive, the band counts arrivals, and the hard stop cannot
swallow — and a played 20-turn campaign shows the row-2 gate arming at least once.

---

## 4. What needs a user decision

Nothing in §2 does. These do:

- **PT-I1 — the armistice is announced as "a separate peace".** It permanently
  ejects the court from the coalition with a −15 betrayal penalty, and the collapse
  never re-adds it (`world_state.py:9666-9670`; `coalition.py:1818,1823`). This is
  **mechanics**, not copy — it changes coalition composition. Measured live: my
  Austrian armistice collapsed back to war five turns later with the ejection
  standing.
- **PT-I2 — give the war a memory.** `calculate_war_score` is a live board read, so
  losing four provinces and retaking them nets to zero. Measured
  `settlement_tier_display: "White Peace"` on **every single sample across 18
  turns** — dials, holdout actions, harshness and the entire per-court authoring
  screen all resolve to the peace Britain offered for free on turn 3. The proposal
  is one monotone leverage term that ratchets on captures and decisive victories
  and decays slowly. **This is the deep version of the CA9 row-1 conversation**, and
  it is the option-A retune that row deliberately deferred until after a playtest.
  The playtest has now happened.
- **PT-I3 — EB-1's condition terms.** The brake **is** converging (Charges 0 →
  2,643 while Net decayed +2,191 → +626; pre-charge surplus +74.5% and plateaued;
  fixed point ≈32,600g around turn 30–35). But Net was positive **18 of 18** turns,
  the treasury rose **×34.5**, and **losing 76,361 men was worth +1,236g/turn** —
  the second-largest structural swing in the campaign. Pricing on the chest means
  the Emperor pays least exactly when he is losing. The lever is the rate's
  **condition terms** (they respond to play — the rate dropped 273 → 206 the turn
  the Austrian armistice was signed), not the fraction.
- **PT-I4 — surface marshal commissioning.** France's bench holds six men at
  3,500–6,000g — the only sink whose price matches the chest, and the only one that
  converts gold into the thing the campaign actually lacked. The word "commission"
  appears **zero times in 108 responses**. An army at 48% strength sitting on
  24,415g should be told it can buy a marshal, not nagged for 450g it cannot spend.

**UNDETERMINED, not a row:** whether the `foreign_wars` HUD panel is reachable at
all on this scenario — empty in **102 of 102** payloads carrying `active_wars`, but
nobody read the producer's skip condition, so "structurally unreachable at boot" is
a hypothesis.

---

## 5. Build order

**PT-A** (indivisible — the three regressions) → **PT-B** (the two silent losses;
B1 must land with **PT-C1**) → **PT-E** (the turn report; E1+E2 together or E2 is
empty) → **PT-D** (the battle report; D1 ships inside A2) → **PT-C** (the rest of
the numbers) → **PT-F** → **PT-G** → **PT-H**.

Gates in §4 whenever the user chooses; **PT-I2 is the one with real design weight**
and it wants its own sitting.

**A visual sign-off is owed and this queue should discharge it** — F7's per-court
fog line (**PT-E4**) and F5's `Supply: Unknown` on the region panel and the map
tooltip. Note that `region_panel.gd:182-184` has the sentinel and **no map tooltip
reads `supply_capacity` at all**.

---

## 6. The traps this playtest paid for

Written down because the next session will meet them.

1. **An HTTP transcript is not what the player sees.** `enemy_phase_dialog.gd`
   rebuilds each line from `action.ai_action.action`, not `action_type`;
   `proposal_result_popup.gd` is an **orphan scene, never registered or routed**
   (`dialog_manager.gd:30`). Check the consuming `.gd` before believing a
   player-visible claim — and before *dis*believing one.
2. **Read the code before filing.** Five findings were refuted and eight downgraded
   by a fleet that did exactly that. `war_age_penalty` reads 0 for a white peace
   **by design**; Milan is not endowable because it is a **capital**; the
   entrenched cooling line's ellipsis is **grammatical**; the roster's six-turn
   memory is a **documented decision with a test pinning it**.
3. **The refuter's job is to attack your own strongest finding.** Two of the
   corrections that changed this spec came from refuters attacking findings I was
   confident in — including the whole mechanism of PT-A1.
4. **Two of your agents will disagree.** One filed the entrenched cooling line as a
   P1; another refuted it. Arbitrate in writing; do not pick silently.
5. **A fix's own test can pass on the wrong side of the seam.** PT-A1 and PT-F2
   both shipped past pins that never touched the executed path.

---

## 7. Landing record — **ROW PT IS BUILD-COMPLETE** (August 12, 2026)

> **This section is the authoritative record of what was built.** All eight
> slices landed in spec order across eight commits, `297b939`..`769a3cb` on
> master. Suite **17,144 → 17,347 / 3 skipped**, ruff clean, Godot parse
> harness EXIT=0, boot smoke 0 `SCRIPT ERROR`, **M1–M7 and `BASELINE_SERIES`
> byte-identical throughout — no re-record, on any slice.**

### 7.1 What shipped

| Slice | Commit | Rows | Tests |
|---|---|---|---|
| **PT-A** | `297b939` + `e0b7f23` | A1, A2, A3 (+D1) | 31 |
| **PT-B/C** | `7129f08` | B1, B2, C1–C4 | 15 + 23 |
| **PT-E** | `8bf7aae` | E1–E6 | 29 |
| **PT-D** | `898b636` | D2, D3, D4, D5, D6 | 19 |
| **PT-F** | `63716f8` | F1, F2, F3, F5–F9 | 24 |
| **PT-G** | `e20b5cc` | G1–G6 | 32 |
| **PT-H** | `769a3cb` | H1, H3, H4, H5, H6 | 19 |

**192 new tests. Mutation sweeps: 19 + 7 + 17 + 16 + 12 + 19 + 19 + 13 = 122
mutations, 122 killed, 0 inert at close.** The harness is committed at
`tools/mutation_sweep.py`; per-slice mutation sets are `tools/_sweep_pt_*.json`.

### 7.2 The through-line closed

The spec's §1 table listed eight honest computations destroyed at a downstream
seam. All eight are closed, and the three regressions PT-A owns cannot recur:
the delivery seam is **subtractive**, the band **counts arrivals**, and the hard
stop **cannot swallow**.

⚠ **The one acceptance clause NOT discharged: "a played 20-turn campaign shows
the row-2 gate arming at least once."** That needs a played campaign, not a
build. What *is* proven is that the gate's input was the thing defeating it —
pricing the roll can only ever move the band toward `unfavorable`, pinned as a
monotonicity property in `TestRow2GateBecomesReachable`.

### 7.3 Scope taken deliberately, and stated

Four rows were **narrowed on evidence**, each with a negative pin:

* **PT-D3's filed fix is REFUTED and not built.** The audit asked for the
  post-battle classifier to be made symmetric; the arrival score reads
  `candidate.get_relationship(primary)` and the derived −1 applies only when the
  CANDIDATE is jealous, so a jealous lead cannot depress the candidate's score.
  The *hostile* case survives and is what shipped.
* **PT-D4 shipped one arm of three.** The province and the broken-corps arms
  would be dead code at that seam — `generate_battle_report` runs inside
  `combat.py`, where conquest is not yet decided and `broken` lives on the
  Marshal, never on the payload. The measured case (Massena) is the rout.
* **PT-F8's first wording is REFUTED** — the comparator necessarily banked
  glory. The subject's clause is what was false.
* **PT-D6 clamps the RENDER, not the mechanical figure**, which feeds war
  exhaustion, the DR-1 out-bled predicate and the score.

**PT-C's `suggestion` row and PT-H2 collapsed into one fix** (H1 is H2's root
cause, as §2 says). **PT-F4's table rows F5–F9 all landed.**

### 7.4 Pins flipped consciously

Each is annotated at the assertion with the reason:

1. `test_enemy_phase_presentation` — `" alone"` → `" on his own numbers"` (D1).
2. `test_session8d_dispatch_polish::test_cleared_on_advance_turn` → **both
   directions** of the prune (E1).
3. `test_ca8_d3_rival_permanence` + `test_jealousy_v32` — `jealousy_ladder_shift`
   **retired**; it had exactly one producer, so its two `dispatch.py` entries went
   with it rather than becoming dead code (F7).
4. `test_battle_report::test_fill_handles_ally_placeholder` — asserted the RAW
   camelCase key reached Berthier's mouth (G5f).
5. `test_ec_levy_and_camp` ×4 — the fixture asserted an offer the executor
   refuses; it now stations a marshal at the capital, which is the player's own
   remedy (H4).
6. `test_objection_v2` — the two inert `idle_turns` tests **replaced, not
   extended**, exactly as §2 PT-F2 demands.

### 7.5 What the mutation sweep caught that review did not

Nine pins passed their own test suite and proved nothing. Recorded because the
pattern is this row's subject:

* **Four file-wide greps matched an import or a comment** rather than the call
  (PT-C1 ×2, PT-C2, PT-F5).
* **Three `expected_at=` producer call sites** could be deleted with every
  assertion green — the pins bound the helper, not the seam (PT-A2).
* **Two prefix matches** let a renamed function through (PT-B1, PT-G5a).
* **Two fixtures never reached the code they claimed to test**: PT-B2's
  reinforcer was `engaged`, and PT-D3's classifier never saw a no-show.
* **Two "inert pins" were INVALID MUTATIONS** — both no-ops — and are recorded
  as such rather than counted as passes (PT-E3).

And two production bugs were found by the sweep's own failures rather than by
reading: **the PT-G2 name key did not distribute** (a sum of code points put
Lannes and Ney on one line; a `*31` polynomial collapsed back to that sum mod 3
and five of six French marshals still shared a line), and **PT-E5's first draft
read a `region_captured` event that never reaches the executor's `events` list**.

### 7.5a The review round — nine more seams, and the row's own joke on itself

A **76-agent find→refute fleet** over the whole diff (commit `87bc137`).
35 findings, ~21 distinct; those below survived two refuters each and several
were reproduced by live probe. **Every one is this row's own subject** — a right
computation dropped at a seam — which is the argument for running the fleet
after the build as well as before it.

* **P1 — PT-F1 shipped PRODUCTION-DEAD.** `_execute_end_turn` does not forward
  `turn_result`; it builds a fresh dict and hand-copies a fixed key set, and
  `jealousy_attacks` was not in it. **Five green pins missed it because they
  asserted the producer, the forwarder and the renderer as source text in three
  separate files and nothing exercised the joint.** The auto-advance mirror had
  the identical hole.
* **P1 — PT-E1 double-rendered.** The prune ran one frame early: it fires BEFORE
  the increment, so an event queued by a system *inside* `advance_turn` carries
  the new turn and survived the next cycle's prune too. The queue is now retired
  **where it is consumed**, which is exact by construction.
* **P1 — PT-D6's clamp was inert on every coordinated battle.** `combat.py` has
  two `log_battle_event` builders; only the solo one was stamped.
* **P2** — `route_fogged` was a flag nothing read; PT-A1's own re-serve handed
  back the RAW petition and re-created IGR-1 on the way out; PT-C2 still split
  shown from applied in two places; and three raw-key renders survived **in
  blocks this row had just fixed**.

### 7.6 Still open, unchanged by this row

* **§4's four items still need a user ruling** — PT-I1 (the armistice ejects the
  court from the coalition permanently), PT-I2 (give the war a memory: the deep
  version of CA9 row 1, now that the playtest has happened), PT-I3 (EB-1's
  condition terms — losing 76,361 men was worth +1,236g/turn), PT-I4 (surface
  marshal commissioning: "commission" appears zero times in 108 responses).
* **The three owed visual sign-offs stand**, and this row adds surfaces to them:
  F7's per-court fog line is now ONE sentence (PT-E4), the terminal has a
  DIPLOMATIC EVENTS rail (PT-E2), turn events collapse (PT-E3), the autonomous
  attack draws a battle (PT-F1), and the redemption raises on control return
  (PT-B1). `region_panel.gd:182-184`'s `Supply: Unknown` sentinel is untouched.
* **UNDETERMINED, not a row:** whether `foreign_wars` is reachable on this
  scenario.
