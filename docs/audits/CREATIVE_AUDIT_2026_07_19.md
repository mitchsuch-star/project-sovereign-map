# Creative Audit — July 19, 2026 (post-NA-6d)

> **What this is.** A play-first creative audit run at master `8dbac27`, after the Nation Agendas arc
> (NA-0..NA-6d) landed build-complete. Method: a live 10-turn France campaign through the real
> backend (`LLM_MODE=anthropic`, real key — live parser, flavor, clarification and diplomat calls),
> plus two headless instrumentation runs (a 40-turn AI-only campaign through the real
> `TurnManager.end_turn` enemy phase, and an agenda/war-status probe) to answer the two questions
> that motivated the session: **do nations act differently now, and do any formables happen?**
>
> **Output discipline.** Every claim below is backed by a live transcript line, a registry read, or a
> code reference. Where a first-pass claim did not survive re-testing it is **corrected in place with
> the correction shown**, not quietly deleted (see §4 P1).
>
> **Status: the correctness defects in §4 were FIXED in the same session** (commit below) — see §9
> for the landing record. The two *design-scale* items (§2.1 agenda-driven war entry, §5 war-economy
> constants) are **escalated, not built**: both are gate decisions under CLAUDE.md GR9, and neither
> is a defect I should resolve unilaterally.

---

## 1. The one-paragraph verdict

**Agendas transformed the nations that were already fighting, and left everyone else exactly as
inert as before.** Within a single enemy phase of turn 1, Britain went straight for the Low
Countries (Flanders, then Amsterdam, then Gelderland, then Brabant — its `low_countries` deny
design, executed without hesitation) and Austria massed Charles *and* John on Milan for
`redeem_italy`, 66,745 men against Massena's 33,070. By turn 3 Britain had what it wanted and sent a
**status-quo settlement offer to lock it in** — a nation achieving its design and then trying to
bank it, which is exactly the behaviour the arc was built to produce. That half of the system is a
genuine success and it is visible in play without reading a tooltip. The other half is not: **an
agenda can only ever influence a nation that is already at war.** Five of the ten nations with decks
boot at war with nobody, and two of those five hold *acquisitive* designs — Prussia wants Hanover,
Sardinia wants Savoy restored — with no mechanism anywhere in the AI to start the war that would
pursue them. Over 40 turns of real AI play, **no nation ever changed its active agenda and no
formable ever formed.** The formables surface is honest and well-built; it is reporting on a chain
that, for the neutral half of Europe, has no first link.

**Pillar scores:** Nation agendas (belligerent) **8** · Nation agendas (neutral) **3** ·
Formables & formation chain **4** · Marshal drama **7** (loud, but noisy) · Combat legibility **7.5** ·
Command & response **7** · War narration **5** · Economy under war **4.5** · Diplomacy **7.5**.

---

## 2. Do nations act differently now? — Yes, if they are at war

**Live evidence, turn 1 enemy phase alone:**

| Nation | Agenda | What it actually did |
|---|---|---|
| Britain | `low_countries` ("They will not suffer France's bloc in Flanders") | Took Flanders (French homeland) and Amsterdam on turn 1; Gelderland by turn 3; Brabant by turn 6 |
| Austria | `redeem_italy` | Massed Charles (48,302) + John (18,443) on Milan turn 1; won *The Great Battle of Milan* |
| Russia | `arbiter_of_europe` | Stance line correctly reads France's hegemony share (39% of Europe's weight) |

The diplomatic layer carries it too. Denmark's envoy opened with *"My master's design is known to all
Europe; Denmark sends this offer in its pursuit"* under `decision_reason: national design` — the
NA-2 `agenda_pursuit` voicing, live. Britain's turn-3 settlement offer bundled Britain+Austria+Russia
on a status-quo term set that hands Britain exactly its design provinces. This is the system working.

**Two texture notes.** Denmark's line teases the design without naming it ("known to all Europe")
where Portugal's hegemony line is specific — naming the design would cost nothing and land harder.
And Talleyrand's assessment was the generic *"An interesting proposal. I shall study the terms
closely"* on a proposal whose own `decision_reason` was already `hegemony_pressure`; the assessment
has the information and doesn't use it.

### 2.1 The finding: agendas are inert for every nation not already at war

Probe of the boot world (`scratchpad/probe_agendas.py`):

```
Austria     redeem_italy            at_war_with=['France','Bavaria','KingdomOfItaly']
Britain     low_countries           at_war_with=['France','Spain','Holland']
Russia      arbiter_of_europe       at_war_with=['France']
Prussia     hanoverian_prize        at_war_with=NOBODY      <-- acquire_regions ['Hanover']
Sardinia    house_of_savoy_restored at_war_with=NOBODY      <-- acquisitive
Denmark     neutrality_of_the_north at_war_with=NOBODY      (guard_neutrality — peace IS the design)
Ottoman     guard_the_straits       at_war_with=NOBODY      (guard_neutrality — coherent)
Sweden      scourge_of_the_usurper  at_war_with=NOBODY
```

Prussia's deck entry is `hanoverian_prize / type=acquire_regions / regions=['Hanover']`, and Hanover
is controlled by Hanover, adjacent, undefended by any great power. In the 40-turn AI run, Prussia's
marshals logged `Brunswick: wait -> N/A` and `Hohenlohe: wait -> N/A` turn after turn, forever.

**Why.** Every agenda reference in `enemy_ai.py` sits inside target-*choice* biasing —
`_agenda_covet_set`, `_agenda_biased_distance`, `_pick_personality_target` — and the code says so
itself at [enemy_ai.py:2669](backend/ai/enemy_ai.py:2669): *"the ratio/threshold gates already ran."*
There are **zero `declare_war` call sites in `enemy_ai.py` or `ai_diplomacy.py`.** The bias reorders
targets among already-valid attacks. It cannot create a war, so a neutral nation's acquisitive design
is display-only text forever.

This is the single highest-leverage gap in the arc. It is also *why* the answer to the second
question is no.

---

## 3. Do any formables happen? — No, and two of the five cannot

**40 turns, real enemy AI, France passive: `formations/creations: NONE`, and no nation changed its
active agenda.** (Britain did expand hard — 11 → 26 provinces, France 27 → 17 — so the AI was
genuinely running and genuinely aggressive; it simply never crossed a formation predicate.)

The `/formables` payload itself is **excellent** — the honest-availability contract is real, gate
terms are per-clause with `met` flags, and the player's own-soil Normandy row correctly renders the
mirror term *"a clause only a victorious enemy may put before you."* The surface is not the problem.

Status of each:

| Formable | Class | Blocker |
|---|---|---|
| Duchy of Warsaw | C | Needs war with Prussia. Prussia is neutral and (per §2.1) has no way to enter one |
| Roman Republic | C | Needs war with Papal States + war score 90 |
| Duchy of Normandy | C | Coalition-side mirror; correct that it is unavailable to France |
| United Netherlands | T | Dormant while Holland is a French vassal — by design |
| **Italy** | **T** | **Structurally unreachable — see §3.1** |

### 3.1 Italy's formation is blocked by map topology, not by design

`risorgimento` requires KingdomOfItaly to hold **Milan, Piedmont, Savoy, Naples, Rome**. Reading the
registry (`assets/maps/europe.json`):

```
Milan     -> ['Munich', 'Tyrol']
Piedmont  -> ['Corsica', 'Lyonnais', 'Provence', 'Rome', 'Savoy']
Rome      -> ['Cagliari', 'Naples', 'Piedmont']
Savoy     -> ['Bern', 'Burgundy', 'Lyonnais', 'Piedmont']
```

**Milan does not border a single other Italian province.** Its only land neighbours are Munich and
Tyrol — both across the Alps, both north. The Kingdom of Italy cannot march from its own capital to
any province it claims without leaving Italy entirely and re-entering via Lyonnais. The formables
screen honestly reports "2 of 5 provinces held"; the remaining three are on the far side of a
mountain range with no path through Italy.

This has consequences past the formation. It is why my retreat order failed in play: ordering
Massena from Milan to Piedmont returned *"Piedmont cannot be reached, Sire — it is not adjacent;
Massena falls back to Munich instead"* — **falling back deeper into Austrian territory**, the
opposite of a retreat. Northern Italy is a cul-de-sac that funnels armies toward the enemy. Austria's
`redeem_italy` and the whole Italian theatre run through this seam.

---

## 4. Confirmed defects (routed, not fixed)

### P1 — Addressing another marshal silently discards a pending decision; the dispatch then reports the halted marshal as marching

> **Correction (recorded, not quietly edited).** My first write-up of this claimed the re-raised
> interrupt was *never surfaced*. That was wrong, and it was wrong because my harness never printed
> `strategic_reports`. Re-tested cleanly: the interrupt **is** re-raised with `requires_input: True`
> on the following turn advance, and `main.gd`'s `_on_strategic_report_dismissed` queues exactly
> those reports into the interrupt popup. The real client would have shown it. What follows is the
> narrower defect that survives verification.

Live: I ordered *"Marshal Ney, march on Swabia and destroy Mack"*, got the bad-odds interrupt, then
typed *"Davout, support Ney"* — and Ney's pending question was **thrown away**. Proof: firing
`/strategic_response` immediately afterwards returned *"Ney has no pending interrupt."*

Mechanism: at [main.py:1240-1255](backend/main.py:1240) the pre-parse loop sees a command naming a
*different* marshal and clears the pending interrupt for any type outside an allow-list of
`("last_stand", "muster_confirm")`. The comment at that seam states its own intent — *"never
silently discard a real pending DECISION the player hasn't answered"* — and then does exactly that
for `contact_bad_odds`, `contact`, `combat_stalemate`, `destination_blocked` and `cannon_fire`. The
allow-list simply drifted out of date as interrupt types were added.

Compounding it, the morning dispatch reported Ney as `status: en_route — "Moving to Swabia."` while
he stood halted awaiting a decision. `_derive_marshal_status` never consulted `pending_interrupt`.

Net effect in play: a one-turn stall plus a dispatch that misreports the marshal's state — not the
permanent silent freeze I first described.

### P2 — Order targets swallow the purpose clause verbatim

*"Murat, march to Milan to reinforce Massena"* stored the destination as the literal string
**`Milan To Reinforce Massena`** — visible in the message, and in the Strategic Ledger's Orders tab as
the order's `target`. The march resolved correctly, so this is presentation, but it is presentation in
the player's own orders screen.

### P2 — Raw camelCase internal names leak to the player from `jealousy.py`

Live: *"Lannes is eyeing **ArchdukeJohn**'s position at Franconia."* Also in the campaign-log battle
one-liner: *"**ArchdukeCharles** (Austria) attacked Massena."* The project has the chokepoint —
`display_names.humanize_entity_name` — and `jealousy.py` calls it **zero times**
([jealousy.py:1527](backend/game_logic/jealousy.py:1527)). Note the same event's `enemy_voice` field
renders "Archduke Charles" correctly, so the two names appear side by side in one dispatch.

### P3 — Grammar bug in the aggressive jealousy line

[jealousy.py:517](backend/game_logic/jealousy.py:517) supplies `"restless for glory"` into the
template `f"he has {expression}"`, producing **"he has restless for glory."** The cautious and
literal expressions are past participles ("grown cold and withholding", "thrown himself into his
post") and read correctly. `campaign_log.py:984` has the right form — "grows restless for glory".
This line fired in six of my ten turns.

### P3 — Jealousy narration is three lines saying one thing, and cools and re-fires in the same turn

A single grievance emits three near-identical dispatch entries:

```
* Berthier reports that Murat appears envious of Davout's laurels — he has restless for glory.
* Berthier notes that Davout's recent victories have attracted... attention among the marshals.
  Murat in particular seems restless.
* Sire, the rivalry between Murat and Davout has become a matter of concern among the general staff.
```

With 2–3 live grievances that is 6–9 lines per dispatch, every turn. Worse, turn 8 carried **both**
*"Davout's resentment of Murat has cooled with time"* and *"Berthier reports that Davout appears
envious of Murat's laurels"* — cooled and re-fired in the same dispatch. The pairs cycle on a
2-turn loop (Murat/Davout fired turns 3, 6, 8; Murat/Lannes 5, 7, 9). The *system* is working
beautifully underneath — Murat's autonomous glory-attack on Nassau was forewarned by Berthier and
then executed exactly as promised, which is a superb beat — but the volume buries it.

### P3 — Headlines repeat verbatim across turns

"Sire — Flanders has fallen" led turns 5 and 6 identically; "Marshal Ney's household goes unpaid" led
7 and 8. A headline that does not change reads as a broken screen rather than a standing crisis.

---

## 5. The economy under war is still the July-17 defect

EC-W was built to kill "treasury climbs while the army melts." Measured this run, France passive:

| | Turn 1 | Turn 10 | Change |
|---|---|---|---|
| Treasury | 800g | **20,131g** | **+2,416%** |
| Army | 189,000 | **143,089** | **−24.3%** |

The EC-W components are present and correctly signed — War Effort grew −12 → −660, Occupation −40,
Contributions 0 — but against +3,320 gross income they are a rounding error. Net was **+2,500/turn,
every turn, while four corps bled ~4,000 men a turn to supply shortage at Nassau.** Losing the war
materially and getting rich doing it is the exact shape EC-W targeted.

**One honest caveat:** I played passively for the sampled turns (the log shows "4 action(s) unused"),
so I was not spending as a real player would. The direction of the defect is unaffected — the passive
hoard is precisely what EC-W2 was aimed at — but the magnitude is a worst case, and I would want a
second measurement from an actively-spending run before tuning against this number.

Related legibility gap: those four corps bled ~24,000 men over six turns at Nassau and **nothing ever
told me to disperse them.** Supply shortage lines report the loss without once naming the cause or
the remedy.

---

## 6. What is working, and should not be touched

- **The muster preview** is the best single surface in the game. `WILL JOIN / WILL NOT` per marshal,
  each with a reason *and the exact command that would change it* — *"order 'Soult, support Ney' and
  he will march"*. It turns the multi-marshal system from opaque to playable in one screen.
- **Battle reports** carry modifier breakdown, casualty summary, an in-character enemy voice
  (Mack, beaten: *"A temporary derangement of the arithmetic. Vienna will understand."*) and the ES-7
  expectation note. Combat legibility is no longer the weak pillar it was in the July-10 audit.
- **The jealousy arc end-to-end** — Berthier's warning that Murat would not wait for orders, followed
  by Murat taking Nassau autonomously, followed by *"Murat's grievance is satisfied — he has surpassed
  Davout in glory"* — is the best emergent story the game told me.
- **`/formables`** honest-availability is a model for how gated content should be surfaced.

---

## 7. Recommended sequencing

1. **P1 interrupt stall** — a marshal frozen while the dispatch says he is marching is the worst
   class of bug: it makes the player distrust the information layer.
2. **Agenda-driven war entry for neutral acquisitive designs** — the one change that would make the
   whole NA arc pay off, and the prerequisite for any formable ever firing organically.
3. **Milan's adjacency** — a registry fix that unblocks Italy's formation, Austria's `redeem_italy`,
   and retreat sanity in the Italian theatre. (Registry edits require a server restart; per CLAUDE.md,
   never re-run `build_region_key_from_psd.py --adjacency-only`.)
4. **Jealousy narration budget** — one line per grievance per turn, the cooled/re-fire contradiction
   resolved, `humanize_entity_name` applied, the "he has restless" template fixed.
5. **Re-measure the war economy** from an actively-spending run before tuning constants.

---

## 8. Method notes / reproducibility

- Live campaign: 10 turns, `LLM_MODE=anthropic`, backend `-m backend.main` on 8005, default
  `europe_1805.json` boot.
- Headless 40-turn run drove `TurnManager(w, executor=ex).end_turn(gs)` — **not** `advance_turn()`,
  which does not run the enemy phase ([world_state.py:6739](backend/models/world_state.py:6739)). An
  earlier pass of this audit used `advance_turn()` and produced a false "borders never move" result;
  it was discarded and re-run.
- Scratchpad harnesses: `play.py`, `run_turns.py`, `sim_formations.py`, `probe_agendas.py`,
  `repro_stall.py`.

---

## 9. Landing record — fixes applied this session

Suite **14,374 → 14,409/3**, ruff clean, M1–M7 byte-identical 11/11, live-verified against a
restarted backend (the registry is `lru_cached` — an edit needs a server restart to take effect).
Pins: `tests/test_creative_audit_2026_07_19.py` (35).

| # | Defect | Fix | Live proof |
|---|---|---|---|
| 1 | Pending decision discarded when addressing another marshal | `main.py` guard inverted from a hand-kept type allow-list to a **derived** rule — an interrupt that offers `options` is a decision and is preserved; only option-less (informational) interrupts are dropped. New types inherit the right behaviour. | `/strategic_response` after "Davout, support Ney" now answers Ney's question instead of "no pending interrupt" |
| 2 | Dispatch reported a halted marshal as marching | `_derive_marshal_status` consults `pending_interrupt` first and returns `awaiting_decision` — *"HALTED at Swabia — Mack bars the way. Awaiting your word."* | dispatch marshal card |
| 3 | Purpose clause swallowed into the destination | `_clean_target_text` cuts a trailing infinitive (`to`/`in order to`/`so as to`/`so that`) that is followed by a word | "Murat begins march to **Milan**"; ledger `MOVE_TO -> 'Milan'` |
| 4 | camelCase marshal keys leaked | `_name_tag` humanized (single campaign-log chokepoint) **and** `attacker`/`defender` humanized at binding — the outcome clause interpolated them directly and bypassed the tag; `jealousy.py` now imports and uses the chokepoint | "Massena is eyeing **Archduke John**'s position"; no `[a-z][A-Z]` run in 7 turns of jealousy lines |
| 5 | "he has restless for glory" | aggressive expression → `"grown restless for glory"`; fallback → `"grown resentful"`; all three slots are now past participles | "he has **grown restless for glory**" |
| 6 | One grievance emitted two near-identical lines | `jealousy_target_notice` retired (its content — both men, who holds the laurels — is already in `jealousy_fired`); removed from the dispatch allow-set too | 7-turn run shows one line per grievance |
| 7 | Headline repeated verbatim across turns | state-based candidates could re-win the lead forever; when the top candidate equals yesterday's headline a distinct one is promoted and the repeat is **demoted to a sub-beat** (never suppressed). Reads the already-serialized `last_morning_dispatch` — no new state | falsifiability-checked: removing the block fails the pin with "headline repeated verbatim" |
| 8 | `"…but obeys.Massena retreats…"` | mild-concern prefix joined with a space | — |
| 9 | Milan severed from Italy | registry edge **Milan ↔ Piedmont** added symmetrically (the real Lombardy–Piedmont border). All five risorgimento provinces now form a connected sub-graph | *"Massena retreats from Milan to **Piedmont**"* — previously forced to Munich, deeper into Austria |

**Deliberately NOT fixed** (escalated to their gates): agenda-driven war entry for neutral
acquisitive designs (§2.1) — a new AI mechanic, not a defect; and the war-economy constants (§5) —
balance numbers, which under CLAUDE.md escalate rather than being retuned in an audit, and which I
want re-measured from an actively-spending run first.
