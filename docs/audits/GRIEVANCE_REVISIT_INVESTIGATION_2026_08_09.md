<!--
CA9 row 3 — the grievance / marshal-petition / popup revisit.

Commissioned August 9, 2026 by the user's ruling in
docs/audits/CA9_GATE_ANSWERS_2026_08_09.md §3: *"we need to revisit
grievences and popups in general and check for issues"* — explicitly a
REVISIT slice rather than a TTL bolted onto CA9-N4, and the audit half of
that slice comes first.

Method: a 27-agent read-only fleet against master @ 246bcc6 — 8 ground-truth
readers (petition arms / consequence visibility / legibility census / popup
and queue machinery / trigger frequency measured over three deterministic
30-40 turn passive campaigns / the remedy economy / spec-vs-code drift / the
narrative surface), then 6 design lenses (fantasy, comparables, decision
quality, legibility, pacing, and an explicit cut-or-fold counterfactual),
each adversarially refuted twice — once on "does it solve the stated
complaint", once on implementation cost and pin risk. ~7.8M tokens.

AUTHORITATIVE for the row-3 audit. The build has NOT happened: nothing in
this file is implemented except A1, landed the same day (see the landing
note at the end of §4). The five rulings in §5 are open and are the user's.
-->

# Grievance / Marshal-Petition Channel — Investigation Memo

**Read-only investigation. Nothing was changed.** 8 ground-truth readers, 6 design lenses, 12 refuters. Every claim below carries a `file:line` I or a reader/refuter actually read and ran, or is marked UNVERIFIED.

---

## 1. The verdict on fun

**No. Not as it stands.** Six lenses scored it 4 / 3 / 2 / 3 / 3 / 3 (mean 3.0); four answered "is it fun" with *no*, two with *partly*, and **none of the six recommended cutting it.** That combination is the honest reading: the underlying system is worth keeping and the thing the player actually touches is not fun, because the one interactive moment is a menu of three prices for an outcome that does not change.

The disagreement is the useful part, and it is not noise — it is two lenses reading two different halves:

- **Fantasy scored it highest (4)** because the raw material is genuinely good: the nine authored per-personality expressions (`backend/game_logic/jealousy.py:605-622`) are the best character writing in the project, `JEALOUSY_RIVAL_MEMORY` is commented *"THE RIVAL IS A PERSON"* (`jealousy.py:120`), and the autonomous glory-attack is a **complete** beat — fore-warned a turn ahead by name/enemy/province with its counter-lever stated (`jealousy.py:1836-1863`), flagged on the card, cancelled by any order (`:2014-2023`), narrated when it fires (`:1985-1994`).
- **Decisions scored it lowest (2)** because all three arms of the confrontation write the same field, so they *cannot* differ in kind. Measured, holding the glory gap constant over 9 turns with no battles: `acknowledge` / no-answer / `promise` / `rebuke` **all converge** to escalation level 2, stored −2/−2, coordination ×0.0. The costs paid were 0 AP / 0 AP / 7 AP / permanent −5 trust.

Resolve those two and you get the actual diagnosis: **the content is good and the choice structure is empty.** That is exactly what "flat and gamey" describes. Your instinct about Acknowledge is not a small copy complaint — it is the system's whole shape, visible through its default button.

The measurements that carry the argument:

| Measured | Value |
|---|---|
| Player grievances fired / 3 passive 30–40-turn runs | **107** (vs 15 enemy) |
| Share of fires at threshold 1 (hair-trigger) | **66%** (74/107) |
| Marshal-drama dispatch lines / 12 turns | **48**, peak 10–12 in one briefing |
| Drama lines per answerable decision (30-turn probe) | **~15** (118 lines / 8 petitions) |
| Petitions actually SERVED in a passive 40-turn run | **1 of 32** (31 discarded) |
| Same card re-pushed unchanged | turns 4 → 41 |
| Committed strength, aggressive reinforcer, grievance on | **24,840 → 0** |
| Win rate, Ney vs Mack, 8 fixed seeds, one jealous reinforcer | **7/8 → 1/8** (cautious) or **0/8** (aggressive) |

---

## 2. The diagnosis, root cause first

### Root: the arms have no object

Escalation history and level are written **only at fire time** — `jealousy_history` appended at `jealousy.py:705`, and both `_set_escalation_level` call sites are inside `apply_jealousy` (`:790-791`). No petition arm can reach either. So whatever the player picks, the pair marches to permanent −2 on schedule. The three arms write `jealousy_turns_remaining` and nothing else; they can only differ in price. That is the mechanism that makes a modal feel like a vending machine.

It gets worse in one direction: `promise` clears with `resolved_by_action=False` (`jealousy.py:1424`), which forfeits the `+10%` surge that the free battle path grants (`:879-880`). So **the paid arm is strictly worse than ignoring the popup**, and ignoring it is byte-identical to Acknowledge.

### Then: the price is never published, so no arm can be evaluated

All three arms are denominated in "turns of grievance", a currency whose exchange rate appears nowhere. The engine computes it to the digit one function away (`combat_executor.py:325-336` aggressive hard-0.0, `:375-384` the coordination mirror) and then tells the player something else — the muster preview, whose own contract is *"the preview must never lie"* (`combat_executor.py:812`), still prints "marches to the sound of the guns", and a failed arrival is narrated as *"could not reach the battlefield in time"* (`:5921-5922`), i.e. the roads.

Two lenses claimed the preview "has no jealousy arm". **That is wrong and it changes the build:** `_muster_reason` already routes the derived-−2 case through `hostile_refuses` (`combat_executor.py:753-756`, reading the *derived* getter at `marshal.py:706-708`), so the authored-Rival case IS named. The two real holes are (a) the derived-−1 half-scale case, which has no code that can say "marches, at half", and (b) the co-located case: `shares_the_field` returns True at `:679-682` **before** any hostility check and additionally stamps `shared_casualty_note` promising *"his men will absorb part of any losses"* (`:862-866`), while `_get_casualty_participants` drops him entirely (`:1336-1345`).

### Then: the outputs are indistinguishable, so even the arm that works is invisible

`clear_jealousy`'s non-action branch builds its message from escalation level and lifetime fires and **never reads its own `reason` argument** (`jealousy.py:905-939`). A grievance ended by the Emperor's paid 1-AP promise, by a rebuke, and by the rival being routed all print *"cooled with time"*. This is the single cheapest line-for-line fix in the whole channel and it is why "acknowledge does nothing" generalises to "nothing here does anything".

### Now separate the four categories, because they need different fixes

**(a) It is broken.** Not shallow — wrong.
- `_on_later()` is `hide()` with no emit (`marshal_petition_dialog.gd:114-115`); `main.gd:1749-1750` returns before `set_input_enabled(true)`. **The polite button disables the command line, send, end-turn and diplomacy with no recovery path.** P1.
- Answering a petition whose grievance already ended charges and reports success: measured, `promise` spends 1 AP and returns *"His grievance shortens"* with `jealous_of=None`; `rebuke` applies a real −5 trust (`jealousy.py:1413-1428`). This is CA9 N4.
- `queue_war_weary_petition` is the one producer with no pending guard (`diplomatic_executor.py:2219-2239`) while `_push_petition` assigns unconditionally (`jealousy.py:1088`) — declaring war **silently destroys** a pending confrontation whose `pair@Ln` latch is already stamped, deleting that beat for the campaign.
- The flagship rivalry modal **names the wrong man as the sulker**: measured on the 1805 boot, *"Sire, Ney has refused to attend council where Murat is present"* while `Murat.jealous_of == 'Ney'` and `Ney.jealous_of is None`. Cause: `modify_relationship` reads the derived value and writes stored (`marshal.py:734` → `:736`), so the envious man's change returns 0 and is skipped at `jealousy.py:1031-1035`, and the petition is queued from his *target's* change.
- Same cause: a shared victory reports a `+1` that never lands, and `battle_report.py:867-875` narrates it — Berthier congratulates you on a thaw on the very battle where the penalty applied.
- `force_reconciliation` charges **2 AP**, rolls, prints *"Under your eye they shake hands"* and changes nothing any mechanic reads: `_restore(-1)` uses `set_relationship` (`jealousy.py:1467-1469`) and the live grievance re-subtracts it. A second inert paid arm.
- `separation_flagged` is written True at `jealousy.py:1571-1572` and **False nowhere in `backend/`** — a permanent subscription with a per-turn nag and no cooldown (`:1872-1892`). CA9 N8.
- Four state fields are dynamic underscore attributes absent from serialization: `_war_weary_petitions_seen` (`diplomatic_executor.py:2224-2228`), `_fontainebleau_armed` (`jealousy.py:1308-1318`), `_jealousy_rebuked_cycle` and `_literal_intel_paused_turn` (`:1435`, `:1437`). `test_serialization_enforcement.py`'s field derivation skips `_`-prefixed names, which is precisely why they escaped.
- Berthier's two *good* closing arms are gated on `len(jealous) == 1` (`dispatch.py:2441-2452`), unreachable whenever one crowned marshal draws several grievances; the fallback names `jealous[:2]` **in dict order**, not the most aggrieved. 12 of 12 turns fell to it in one trace.

**(b) It is invisible.** The cost is enormous and unattributed; the only well-lit consequence is the reward.
- The `+15%` solo-attack bonus (`marshal.py:1063-1064`, constant `:1231`, stamped `combat_executor.py:4490-4491`) is on **no surface anywhere**, and the code itself calls it *"an INTENDED strategy, not an exploit"* (`marshal.py:1058-1060`). This is the cheapest fun win available: "send him alone and he fights like a demon, send him beside his rival and he brings nothing" is a real tactical fact today, and it is 100% hidden.
- The one sentence in the entire product that states the causal rule is wrong twice: `marshal_management.gd:225` says *"glory, last 5 turns — the man above draws the envy of the man below"*, against `GLORY_WINDOW = 8` (`jealousy.py:49`, pinned at 8 by `test_drama_glory_from_attrition.py:148`) and against rival memory (`:120`, `:330-351`), which re-fixes envy on a remembered man, not the adjacent rung.
- `help` never uses the words glory, jealousy, grievance, ladder or petition (`meta_executor.py:472-655`), while teaching the sibling ES-7 reward loop in ~24 lines (`:540-556`).
- The card contradicts the engine on the same screen: `_build_relationships` iterates the raw stored dict (`marshal_overview.py:479-492`), so it prints "Ney: Friendly" two lines under "GRIEVANCE: envious of Ney".
- `marshal_management.gd:202` tells the player to *"reward them before they ask"* — false twice: `_threshold_for` (`jealousy.py:478-503`) reads relationship/idle/authority and no satisfaction/expectation/estate/pension term, and the chip is gated shut until he **has** asked.
- The cure exists only as past-tense `reason=` strings (`jealousy.py:997`, `:1005`, `:1022`). The one forward-looking hint is **arithmetically unreachable** for the pairs that fire most: `delta == threshold - 1` (`:1824`) needs delta 0, while `find_jealousy_target` only returns peers strictly above (`:324-325`).
- The battle report **deliberately** omits the entire coordination system, deferring to a Battle History screen (`battle_report.py:146-153`) that Phase 8.5 closed without building.

**(c) It is shallow by design** — and the design is on record, which matters.
- Acknowledge was authored as a no-op from v2 onward. It is not a bug.
- v3 deleted Promise Glory's 2-turn deadline with its reason recorded (`JEALOUSY_SPEC.md:434-437`, `:813`, `:1204`). See §6 — that reason still holds.
- `JEALOUSY_SPEC.md:983` excludes *"Council command ('to my tent')"* with **no owner row** (a GR9 orphan) — and it is exactly what the petition body asks for: *"He requests a command worthy of his talents."*
- §6's own heading has claimed *"all options have randomness"* since v3 (`spec:424`) while the table beneath it and the code are fully deterministic. The randomness went to §6b instead.
- −2 Hostile is a **one-way trapdoor**: at rel −2 a shared victory maxes at 35 against a strict `> 50` (`relationship.py:88-104`), and the only escape queues solely on a *downward* transition (`jealousy.py:1036-1058`), so the pairs authored at −2 at boot can never produce one.
- No headline class for any grievance event (0 of 22 in `dispatch.py:55-129`), and `_build_marshal_arcs` (`:1078-1345`) is blind to them — verified empirically: a marshal who fired twice into an entrenched feud produces **no arc entry at all**.
- `marshal_voice.py` holds 45 first-person battle lines and **zero** about envy (`:192-195`), while each personality gets exactly one confrontation body, forever.

**(d) It fires too often — and it also fires too rarely, and conflating those is how this gets built wrong.**
- The **cause** is hot: 66% of fires at threshold 1, inherited from the *authored* boot web (7 of 21 French pairs at Rival or worse), and DR-3 exempts precisely those hair-trigger pairs from the authority calm (`jealousy.py:496-502`). Turn 3 of a fresh campaign already produces grievances the player had no chance to avoid.
- The **narration** is unbounded: `_build_turn_events` appends every whitelisted event unranked and uncapped (`dispatch.py:2280-2347`), while `intent.py:469` ships `INTENT_DISPATCH_CAP = 2` and arcs cap at 3 (`dispatch.py:1337`). Jealousy caps *fires* only (`:82`).
- The **channel is starved**: 1 petition served of 32 in a passive 40-turn run; even answering every turn, 13 queued / 7 blocked / 6 latched.
- And **half the volume is duplication, not breadth.** Measured: 24 of 40 turns carry both a clear and a fire in the same pass, and 4 of 4 cooling turns re-fired the same pair in the same briefing — one page saying a resentment *"has cooled"* and, two lines later, that it flared *"for the fourth time"*. `_check_escalation` also co-emits with the fire that caused it (`jealousy.py:755`). **De-duplicate before capping**, or a cap preserves the wrongness and collapses the correct lines.

---

## 3. Acknowledge

It is an unconditional no-op. Measured on a real 1805 world with a state snapshot diff across AP, authority, gold and every marshal's trust / `jealous_of` / timers / relationships / pension / latches, the only mutation is `n_events: 0 -> 1`. The code is a bare `else` at `jealousy.py:1444-1452` that sets a message string and logs an event. It is listed **first**. The Aug-8 fix made its copy honest and left it in place.

**What it should be: the honest refusal, priced.** Not deleted, not given a fourth price.

- **Not deleted.** Two arms that both only decrement a hidden timer is still a vending machine, and deletion has a coercion hazard: at 0 AP the only working arm becomes Rebuke (−5 trust), with a Later button that is currently dead. It also reverses a one-day-old landed honesty fix pinned by three tests (`test_tutorial_school_fixes_2026_08_08.py:196-212`).
- **Not given teeth.** A fourth price on a menu whose problem is that all prices buy the same outcome makes it worse.
- **Renamed and priced.** Rename to **"Let it stand"** — §6b already ships *"Let be"* as the same idiom, so it is the system's own vocabulary, and unlike "Acknowledge" it is honest about being a refusal to act. "Acknowledge" is the *dismiss* verb elsewhere in the client (`proclamation_popup.gd:11,15,22`; `notification_bar.gd:437,508-511`), which is why as the first button on a decision modal it frames the whole card as an inbox receipt. Then state what standing costs: "he brings none of his 24,000 men to any battle Davout leads, for four turns" is a decision. "Souring his ties and coordination" is not.
- **Do not move it out of first position yet.** Moving it makes `promise` the reflex click, and `promise` is measurably the worst arm on the card. Revisit the order after the ratchet ruling (Q1).

A refusal with a stated price is a real choice. That is the whole fix, and it costs no mechanics.

---

## 4. The recommendation

### Phase A — mechanical, no ruling needed, ship in this order

| # | Item | Cost | What changes for the player |
|---|---|---|---|
| A1 | **Fix the Later soft-lock.** `_on_later` emits a dismiss signal; `main.gd` re-enables input. `marshal_petition_dialog.gd:114-115`, `main.gd:365-367`, `:1749-1753` | trivial (3 lines .gd) | The deferral affordance stops bricking the turn. P1. Ship alone, first. |
| A2 | **Thread `reason` into `clear_jealousy`'s non-action branch** as a clause *inside* the existing three-variant ladder (`jealousy.py:905-939`), keeping `reason="time"` rendering "cooled with time" so both CA8-8 pins hold; entrenched outranks reason | small | The paid arm stops being narratively identical to patience. Highest value per line in the memo. |
| A3 | **Stale-answer guard + retirement**, scoped to `jealousy_confrontation` only: compare `context['target']` to `marshal.jealous_of` before spending AP or trust; on mismatch change nothing, write no latch, **and retire the card** (`jealousy.py:1413-1428`). Do NOT touch war_weary — it carries the assembled declare-war command at `diplomatic_executor.py:2229-2233`, so retiring one silently cancels a declaration | small | The game stops charging an action point for a quarrel that is already over and reporting success. CA9 N4's fixable half. |
| A4 | **War_weary producer guard, done right**: move the `_ww_seen.add()` stamp (`diplomatic_executor.py:2228`) to *after* a successful push, skip the card when a petition is pending, and let the declaration proceed | small | A declare-war stops silently destroying a marshal's audience. |
| A5 | **The muster preview stops lying.** Site a derived-hostile check **above** `shares_the_field` (`combat_executor.py:679-682`) and suppress `shared_casualty_note` (`:862-866`) for a marshal `_get_casualty_participants` will drop (`:1336-1345`). For the half-scale case carry a **`withholds` row field** on the existing `standing_order_hint` pattern (`:845-864`) — do NOT flip `will_join`, and do NOT put a `{placeholder}` in `MUSTER_REASON_DISPLAY` (`display_names.py:637-663`; it is consumed as `.get(code, code)` at `:847`). Cover the third caller `_bad_odds_muster_note` (`:965`) and add the parallel `battle_diorama.py:57` row. **Ship a band-invariance pin** (arm on/off → `odds_band` and `committed_strength` byte-identical) | small | The screen read before every attack names the quarrel that is deleting a corps from the odds. This is the largest single legibility win. |
| A6 | **Stop narrating character as weather.** Reclassify the grievance-driven arrival failure out of `reason="low_score"` (`combat_executor.py:1206-1207` → `:5921-5922`) into a character code beside its two siblings (`:5903-5904`, `:5908-5911`). Deliberately leave the new code OUT of the Session-61a exempt tuple (`:6031-6035`) so the trust dock is byte-unchanged, and say so at the guard | small | A corps that did not march is attributed to ambition, not the roads. |
| A7 | **`jealousy_note` reaches every battle.** Add it to `_format_berthier_report`'s field whitelist (`enemy_phase_dialog.gd:376+` — the payload is already there, `:259-260` reads `battle_report`), and lift the composition out of `_execute_attack` (`combat_executor.py:5809-5851`) onto the shared post-combat seam. Name which of the three `check_battle_resolution` call sites get an arm (`combat_executor.py:1830`, `:5239`, `world_state.py:10968` — the last has no `battle_report` in scope). **Pick one surface** and suppress the next-morning bullet, closing N36 | small–medium | A grievance healed on defence or in the enemy phase is finally reported where it happened. |
| A8 | **Queue the rivalry petition from the man who is actually jealous** (`jealousy.py:1027-1058`), and stop `battle_report.py:867-875` narrating an improvement whose derived value did not move (`relationship.py:186-197`) | small | The flagship modal stops telling the story backwards, and Berthier stops congratulating you on a reconciliation that did not happen — **without** touching relationship values or the harness. |
| A9 | **`separation_flagged` gets a retirement path and the warning gets a cooldown** (`jealousy.py:1571-1572`, readers `:1875`, `:2058`) | small | The one honest arm stops being a permanent subscription. CA9 N8. |
| A10 | **Serialize the four dynamic latches** (`diplomatic_executor.py:2224-2228`; `jealousy.py:1308-1318`, `:1435`, `:1437`) + `SAVE_FORMAT_REFERENCE.md` | small | Once-per-campaign promises become true across a reload. **Prerequisite** for trusting any new promise mechanic. |
| A11 | **Fix the three sentences that teach the system.** `marshal_management.gd:225` — add `glory_window` to `build_glory_ladder_payload` (`jealousy.py:2064-2075`) and interpolate it rather than re-hardcoding, plus state the rival-memory rule; `marshal_management.gd:202` — conscious flip of `test_tutorial_position7.py:251` and re-word the R159 row; card relationships read `get_relationship` (`marshal_overview.py:479-492`); a six-line `help` block (`meta_executor.py:614-627`) whose load-bearing sentence is **that estates and rentes cannot touch jealousy**, with the solo bonus stated as *"with no marshal of yours counted on the field beside him"* (`combat_executor.py:4489-4491` drops derived-hostile marshals before the count) and the defeat + out-bled-stalemate halves included (`jealousy.py:52-58`, `:159-180`). Pin by source grep, precedent `test_naval_ui_clarity.py:208` | small | The player can finally reason about the ladder from correct rules, and stops reaching for gold. |
| A12 | **De-duplicate the briefing.** Suppress the same-turn cool-then-refire for a pair (`jealousy.py:1706-1734` vs `:1739-1789`, whose only exclusion is `if marshal.jealous_of: continue`), drop the duplicate escalation line, stop level-1 escalation co-emitting with its own fire. Fix `dispatch.py:2441-2452`'s dict-order `jealous[0]`/`jealous[:2]`, make the ranking key total, and add a **positive-reach pin** — the rung is wrapped in a bare `try/except: pass` at `:2429`/`:2454-2455`, so a ranking bug silently swallows it and the suite stays green | small, **own commit + flip experiment** | The system stops contradicting itself on the same page. Touches enemy `jealous_of`, so it can move `BASELINE_SERIES`. |

### Phase B — after A, and only after A12 measures clean

**A13. Cap the routine drama lines, in the producer, AI-6 shape.** Needs a prerequisite the lenses missed: an earned resolution and a timer expiry are **both** `type: "jealousy_resolved"` with no discriminator (`jealousy.py:897-905` vs `:940-945`; only the campaign-log event at `:882` carries `by_action`). Add `by_action` as a new key on the existing dispatch event — house pattern, no `CAMPAIGN_LOG_TYPES` change — and key the exemption on `(type, by_action)`, with a mutation-tested never-collapsed pin. Exempt the crown, the escalation-to-permanent, the autonomous warning and the petition arrival. Note `test_jealousy_v32.py:823` asserts `jealousy_separation_warning` is present, so a naive cap reds it.

**A14. The petition modal renders the marshal.** Render the `speaker` field the backend already sets at four sites (`jealousy.py:1179`, `:1246`, `:1270`, `:1360`) and **zero `.gd` files read**, with `objection_dialog.gd:47-52`'s tone-scaled header idiom, plus first-person bodies authored **in `jealousy.py:1147-1165`** — not `marshal_voice.py`, whose banks are keyed to five battle situations (`:192-195`) with no consumer joining them to the petition. `war_weary` already does this (`jealousy.py:1356-1359`, *"I have my duchy, Sire. Why do we march again?"*) and is the only petition that reads as drama. Do **not** duplicate a stat block — the Generals card owns the character sheet; unblock the lookup instead (the modal registers `modal=true` at `main.gd:365-367`, which gates KEY_G at `:4337-4339`). The portrait is a separate layout slice: `portrait_locket.gd` is a shader-bearing diorama `Control`, `marshal_management.gd:626` is a BBCode `[img]` emitter for a `RichTextLabel`, and the panel is a fixed 680×480 needing the IGR-G `clamp_ceiling_override` treatment.

### Explicitly OUT of this slice, with reasons (GR9-homed)

- **Moving the petition off `_post_hud_response_routes`.** The complaint is real — every entry returns before `_display_result` (`main.gd:1295-1308`, `:1749-1750`), so the card swallows the output of the command just typed, and the Proclamation (`:1375-1384`) and letter-book (`:1534-1543`) were both explicitly moved out for that reason. But 5 of 12 entries are unbidden surfaces, `_return_control_to_player` (`:1514-1532`) is called from only 3 of 8 control-return tails (`:3301`, `:3627`, `:3881`, `:4092` raise the diorama alone), and the war_weary arm attaches directly to the declare-war response over a suspended declaration (`:1364-1369`). Moving one entry into a 37%-adopted chokepoint is how the Proclamation became undeliverable twice. **File as a list-wide contract question**, not a petition fix.
- **The enemy mirror.** No player-facing surface exists at all; `campaign_log.py:934-945` cites §9b routes that do not exist as its *reason* for filtering enemy jealousy out, and 8 of 10 nations field one standing marshal so the ladder can never fire for them. **Docs-only now:** retire the §9b promise (`JEALOUSY_SPEC.md:670-694`) and correct that comment. Building it changes nothing the player can feel.
- **§6's "all options have randomness" heading** (`spec:424`) — amend the spec to match the code, or own it as a build row.

---

## 5. What needs your ruling

**Q1 — May a petition arm touch the escalation ratchet?** Today none can (`jealousy.py:705`, `:790-791`), which is why the outcome is invariant to the choice.
- (a) No — the arms only ever buy time. (b) One arm **holds** the current level for N turns at a cost. (c) One arm buys a rung back.
- **Recommend (b).** A hold cannot un-write history, so it is the cheap version, and it is the smallest change that makes the modal compound. It needs one serialized int — so order it **after A10**.
- Consequence of (a): the modal can never be a decision and the honest move is to shrink it to a notice. (c) is the strongest fix and the largest blast radius (`_restore` currently overwrites, see Q4).

**Q2 — Build the excluded "Council command / to my tent" arm?** `JEALOUSY_SPEC.md:983` defers it with no owner row, and it is literally what the body text asks for.
- (a) Build it: the arm gives him a named objective, and resolution then flows through the existing per-personality predicate he already satisfies (`jealousy.py:950-1022`) **and pays the `+10%` surge**, so the paid arm stops being dominated. (b) Retire the promise in the spec and re-word the body to ask for something the menu can grant.
- **Recommend (a) if only one design item is built this slice.** It is the only proposal that makes the modal a decision *and* answers "why does this exist" in the same stroke: he asks for a command, you give or refuse a command. The cheapest shape is for the arm to issue an **existing** strategic order (PURSUE/MOVE_TO) at its existing AP price rather than invent a verb — *UNVERIFIED that the `strategic_executor` seam is that clean; verify before scoping.*
- Consequence of (b): cheap and honest, and the card stays a price list permanently.

**Q3 — Does the first grievance on an authored-Rival pair get a first act?** Today `qualifies = stored_rel <= -1 or fires >= 3` (`jealousy.py:783`), so 12 of 17 authored French edges reach escalation level 1 on fire 1 and the player's very first card opens with *"this is no longer a passing mood"*.
- (a) Leave it — the board opens hot on purpose. (b) Require a second fire when `stored_rel == -1`, keeping `<= -2` immediate. (c) Raise hair-trigger pairs to threshold 2.
- **Recommend (b).** It moves the level, the card register and the `pair@Ln` latch together, which is the only version that actually delivers a first act.
- Consequence: (b) shifts the CA8-D3 latch sequence, tier-2 timing and probably `BASELINE_SERIES`. (c) re-opens the DR-3 Phase-3 decision that flipped M7 from *never* to *turn 1* and risks re-starving marshal drama. **Do not** ship the "gate the level-1 announcement on `fires >= 2`" version — see §6.

**Q4 — Is permanent Hostile intended, and may the mend arms erase authored character?** At rel −2 a shared victory maxes at 35 against a strict `> 50` (`relationship.py:88-104`); `_restore` uses `set_relationship` (`jealousy.py:1467-1469`), so a free 60%-hit arm can launder Davout–Bernadotte's authored −2 (the Auerstedt no-show) back to neutral.
- (a) Trapdoor intended: state it at the guard, clamp `_restore` to the authored floor, and make `force_reconciliation` either clear `jealous_of` on success or stop claiming success. (b) Add a repair path.
- **Recommend (a).** (b) is a new AP-priced verb whose cheap version defuses the whole system, and it is player-only by construction — `mediate` at authority ≥70 is 70% restore with *no downside arm* (`jealousy.py:1487-1495`) at boot authority 100 and 4 AP, so an unrestricted verb becomes a re-rollable overwriting repair.

**Q5 — When do we fix `modify_relationship`?** It reads the derived value and writes stored (`marshal.py:734` → `:736`), against a docstring three lines above asserting the opposite (`:701-703`).
- (a) Fix the writer now. (b) Fix the writer **and** rule on the readers (`relationship.py:50` keys `rel_mod` off derived; `:135-146` gates participation on derived −2). (c) Fix only the two visible symptoms at their own seams — already A8 — and defer the writer.
- **Recommend (c) now, (b) after the playtest.** A refuter **ran** the flip experiment: control reproduces `BASELINE_SERIES` byte-for-byte; with the writer fixed the series **diverges at index 20**, 21 of 41 readings change, and the tail collapses to 0 by index 35 against the recorded 13 — Europe's alarm about France dies six turns early, and two of the five leaking calls are Russian. It also makes the WIN arm reachable at stored −1 (`rel_mod` −20 → 0, max 35 → 55). That is a balance change in the *flatter* direction shipping on the slice immediately before the playtest that is supposed to read this row.
- Correct the framing when you take it: for stored −1 pairs the final stored value is **identical** under both arms (both clamp to −2); only the returned change differs (0 vs −1), which is what gates the rivalry petition. The stored divergence exists only for stored-0 pairs, which today skip Rival and land on Hostile.

---

## 6. What I recommend NOT doing

1. **Do not restore v3's Promise Glory deadline on the DR-1 argument.** Three lenses used it; it is a category error. `STALEMATE_GLORY` (`jealousy.py:52-58`) feeds `get_glory_score` — how glory *accrues*. Resolution runs through `check_battle_resolution` (`:948-1021`), which enters only on `attacker_won`/`defender_won`, so an inconclusive out-bleed and a bloodless province capture resolve **nothing**. The recorded v3 reason (`spec:434-437`, `:1204`) stands unchanged. Separately, the arithmetic defeats it: duration is `2 + (delta - threshold)` bounded 2..5 (`:83-84`) and 66% of fires are threshold 1 with a small delta, so a 3-turn deadline outlives most grievances — the broken arm would almost never fire and the paid arm would flip from dominated to **dominant**. It also re-adds a field the spec records as removed to reduce serialization footprint (`:813`).
2. **Do not add a campaign-wide petition rarity budget.** It re-creates by construction the defect CA8-D3 was held to fix, since the latch is keyed `pair@L{level}` (`:764-773`) precisely so each level gets an audience. And the measured problem is starvation (1 of 32 served), not frequency.
3. **Do not cap the drama lines as the first move.** Half the volume is duplication and self-contradiction, so a cap preserves the wrongness and collapses the correct lines. Also, those lines are currently the system's **only** recurring surface: `_derive_marshal_status` has no jealousy branch (`dispatch.py:2065-2151`), the two declared notification types are dead code (`notifications.py:111-112`, zero emitters), help is silent, the tutorial is dormant (`jealousy.py:123-131`). And the repo already ran this play — PC-7 on `estate_eroding` cut its share 51% → 30%, and the recorded read was that it reduced the nagging rather than making the choice matter.
4. **Do not delete Acknowledge.** See §3.
5. **Do not gate the level-1 escalation announcement on `fires >= 2`.** It is inert and backwards: `jealousy_history` is appended at `:705` **before** `_check_escalation` at `:755`, so fire 1 already has `_lifetime_fires == 1`, and `qualifies` is already true on fire 1 for the authored Rival edges — so the gate makes the *mild* announcement unreachable and leaves *"the wound will not close on its own"* as the player's first spoken escalation. The card is untouched either way (`:1166-1178` reads the level fetched at `:768`). The real seam is Q3.
6. **Do not change the SUPPORT/hostile mechanic.** The "strictly dominated" claim is false: casualties distribute proportionally by strength (`combat_executor.py:1355-1414`) and a zero-contribution participant is skipped at `:342`, so a SUPPORT order does not change the resolution but **does** lower the lead's casualty share — same dead, spread over two corps. That is a grim Napoleonic tradeoff, not a trap. A buy-back would also be dual-site (`:327-336` and `:375-384`) and would make M1b's pin **inert rather than red**, since `measure_m1b` feeds `_contribution` a hardcoded `rel_factor` (`test_combat_sweep_metrics.py:207-219`).
7. **Do not add a typed "reconcile X and Y" verb.** See Q4. Also GR5: one refuter found no `StrategicOrder(` construction anywhere in `enemy_ai.py`, making several "give the player a verb" proposals player-only by construction (*UNVERIFIED by me*).

### The cut / fold case, and its verdict

Made honestly, the cut case wins on almost every count: the ratio (~15 lines of prose per decision offered), a no-op default listed first plus a second inert *paid* arm, inverted visibility (the biggest consequence unlabelled, the crown well-lit), no player agency over a trigger inherited from authored boot values, redundancy with `objection_v2` + `disobedience` + `defiance` — ~4,454 lines the player touches on **every order**, already relationship-aware (`objection_v2.py:1608`, `combat_executor.py:756`) — and cheapness, because the good parts are separable: `recompute_crowns` (`jealousy.py:367`) reads only `get_nation_ladder` → `get_glory_score` → `glory_events` with **zero** reference to `jealous_of`, and ESP-1/ESP-2 read only `dotation` state and merely *ride* the petition transport. Cutting the grievance layer keeps glory, the crown, the +1 skills and 2 of the 4 petition kinds, and drops 7 of 9 serialized marshal fields.

**Verdict: keep — on one argument, which I think is decisive.** This is the only system in the game where **success costs cohesion**. EC-P3 made success cost gold; ES-7 made success cost gold. Nothing else makes it cost anything social, and that is the most Napoleonic idea in the codebase. There is no substitute; delete it and winning has no price the player can feel.

But keep is **conditional**, and I would defend the condition harder than the verdict: it is only right if Phase A actually lands. A 2,076-line system emitting ~15 lines per decision, with a no-op default and an invisible headline consequence, is not neutral — it is spending the trust pillar CA9 says regressed. If Phase A will not be built, the honest move is to cut the grievance layer, keep glory + crown + the ESP riders, and re-home the autonomous glory-attack to personality + idle — which is *more* legible, because it reads off the marshal's character instead of an invisible ladder.

---

## 7. Risks and pins

**`BASELINE_SERIES`.** Moves on anything that touches enemy marshals' `jealous_of`, stored relationships, or the escalation formula — because `_check_escalation` has no `is_player` gate on the write and the ambient runner fights AI-vs-AI battles through the same `_RELATIONSHIP_SCALING`. Specifically at risk: A12 (24 of 40 turns carry a cool+fire pair, including Russian and British marshals), Q3, Q5 (**measured**: diverges at index 20, 21/41 readings change, tail 13 → 0 by index 35), and A3's retirement (freeing the slot makes `check_rivalry_transitions` at `jealousy.py:1054` and `check_fontainebleau` at `:1315` newly reachable, both of which write serialized state and log events). Every one of these needs its own commit with a multi-arm flip experiment. Everything else in Phase A should be byte-identical — **verify, do not assume**.

**M1–M7.** Measured byte-identical under the Q5 patch — and that is a fact about the harness, not a safety proof. `M1`/`M1b` feed `_contribution` a hardcoded `rel_factor` (`test_combat_sweep_metrics.py:207-219`, ~`:180-193`), so a production change to the scaling would leave M1b **green while it stops tracking anything**; if the scaling is ever touched, `measure_m1b` must be rewritten to read production. M7 (`1 <= first <= 8`, `:519-586`) is exposed by any trigger-threshold change. No petition arm can reach the harness at all, because no harness answers a petition — **the only verification for the arms is the playtest.**

**Suite pins that will flip, by name.** `test_jealousy_v32.py:720` (exact option-id set `{acknowledge, promise, rebuke}` — the *id* is the POST value, so rename the label only), `:724`/`:766` (post `acknowledge`, assert success), `:755-760` (a rejected choice leaves the petition pending — **flipped by A3's retirement**), `:823` (`jealousy_separation_warning` present — reds a naive cap). Note `:668-679` and `:328-335` pass under **both** arms of Q5 and therefore protect nothing here. `test_tutorial_school_fixes_2026_08_08.py:196-212` (three tests on the acknowledge detail; `:199` is on option **detail**, so body edits are safe). `test_creative_audit_ca8_2026_08_04.py:1008` (negative) / `:1022` (positive) for A2, `:1049-1058` (recurrence must contain "again" — reds a naive `campaign_log.py:1407-1419` reorder), `:520-523` (every headline class needs a template and a note). `test_tutorial_position7.py:251` (literal *"reward them before they ask"* — conscious flip + R159 re-word). `test_drama_glory_from_attrition.py:148` (`GLORY_WINDOW == 8`). `test_ca9_row2_muster_gate_scope.py:185/224/234/389` (exact odds bands) and `test_creative_audit_ca9_2026_08_08.py:711` (source-pins that `_defender_muster` calls `self._muster_reason(`). Safe: `test_w6_muster_preview.py:125-134` and `test_marshal_content_mc3_relationships.py:235-242` reach `hostile_refuses` via stored −2 with **no** grievance. `test_naval_reach_gate.py:234-235` pins `"_" not in MUSTER_REASON_DISPLAY["sea_barred"]` but there is **no count pin**, so a new key is free. `test_battle_diorama.py:302`/`:354` pin contingent status via `_REFUSAL_REASONS` (`battle_diorama.py:66`); the parallel `_REASON` table at `:57` is what a new code must join.

**Serialized fields.** Four existing holes (A10) should be paid before a fifth is added — and note `test_serialization_enforcement.py` derives Marshal fields from `__init__` and **skips `_`-prefixed names**, which is exactly why all four escaped. Any new field also needs `docs/SAVE_FORMAT_REFERENCE.md`.

**Popup slots and log types.** Nothing here needs a new slot — `len(PopupQueue.PRIORITY_ORDER) == 11` is pinned at `test_cooldown_popup_manager.py:452` and `test_igr_f_envoy_digest.py:818`, with order pins at `test_nation_agendas_formables.py:951-956`. Nothing here needs a new campaign-log type either, provided A13 adds `by_action` as a key on an **existing** dispatch event: the count is pinned in **five** files (`test_campaign_log.py:138`, `test_bph_a_term_ownership.py:303`, `test_igr_a_honest_copy.py:197`, `test_igr_b_campaign_log_readable.py:546`, `test_igr_f_envoy_digest.py:824`). **Discrepancy to resolve by reading:** CLAUDE.md says 156, every refuter that ran the pins reported 157. `_DISPATCH_EVENT_TYPES` (`dispatch.py:2230`/`:2263`) is an unpinned set, so a new overflow-tail type is cheap there.

**Godot.** Items A1, A5's display half, A7 and A11 touch `.gd` → the XR-1 rule (boot the engine, grep `SCRIPT ERROR`) plus regeneration of the **tracked** `tools/godot_parse_report.json` (asserted by `test_godot_parse_harness.py:70-98`). Be aware the stale-report guard is scoped to `SETTLEMENT_CRITICAL_SCRIPTS` (`:30-42`), which does **not** include `marshal_management.gd` or `marshal_petition_dialog.gd` — the suite would stay green over a broken card edit.

**Working tree.** The session-start snapshot said clean at `246bcc6`, but a refuter later observed uncommitted CA9 row-2 work in `combat_executor.py` (+27), `objection_v2.py` (+56), `marshal_voice.py` (+29), `tests/test_w6_muster_preview.py` (155 changed) plus an untracked `tests/test_ca9_row2_muster_gate_scope.py`. **Verify before touching `_muster_reason` or `objection_v2.py`** — A5 and A6 edit exactly those files, and row 2 owns the odds band A5 must leave byte-identical.