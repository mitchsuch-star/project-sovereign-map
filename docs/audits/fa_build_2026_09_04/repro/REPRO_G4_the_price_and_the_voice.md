# REPRO G4 -- "the price and the voice" (FA-N16, FA-N43, FA-N45, FA-21)

Agent tag `g4`, read-only, master `a1ed5c9d`, Sept 5, 2026. Probes under
`<scratchpad>\repro\g4\`. All measurements on the shipped 1805 boot or the
committed `tests/fixtures/playtest_saves/fixture_t20_ambient.json` (turn 20,
France at WAR with Britain/Austria/Russia in `war_1`, France gold 17,487,
Britain gold 9,425, Britain's diplomat a HAWK).

Direction vocabulary used below, everywhere: "France pays" = the clause's
`from` is France (a DEMAND on France); "AI pays" = `from` is the AI court (a
SWEETENER / concession to France). "Burden on X" = the harshness sum over the
clauses whose `from` is X.

## Summary

- **FA-N16 -- REPRODUCED, in full, through the real producer.** `build_incoming_settlement_offer_popup` reads only the first `gold_indemnity` clause's `amount`, never its `from`/`to`, and every one of the six `settlement_incoming_offer_arrival_*` templates is demand-shaped, so the boot white peace reads "They ask 0 gold" / "London asks 0 gold", and an offer in which Britain PAYS France 1109 (the AUD-c concession arm, produced live on the boot board with France at +60) reads "London asks 1109 gold" on the popup and "Asking 1109 gold." on the notification.
- **FA-N43 -- REPRODUCED for the label, NARROWED on the mechanism: the number is not "inverted", it is the wrong number for that line.** `build_war_context_snapshot`'s `harshness` is, by its outgoing definition, the burden on the ENEMY (what the target is asked to bear); the oriented mirror terms preserve that definition, which is why the fallout warnings that consume the same number are CORRECT today (an offer that pays the enemy is soft on him, allies are doubly angry: Spain -20 vs -10). Only the "Assessment" label misreads it as burden on France. The row's one-keyword fix (un-oriented terms for `harshness`) flips the fallout warnings in BOTH directions -- measured.
- **FA-N45 -- REPRODUCED (405g moved, record stores 0.0), NARROWED on the fix: the clause loop is direction-blind.** `_ratify_treaty` turns sweeteners AND demands into clauses and prices all of them; mirroring the four demand rates into that loop makes a treaty in which Britain PAYS France 500 store 0.4 and trip DD8-4's -5 on the pair, and flips the ally-penalty doubling the wrong way for a France-pays peace. The stored value's only live consumer is DD8-4; the ledger and `peace_ratified` copies are dead data.
- **FA-21 -- NARROWED (defect real, three load-bearing parts wrong, re-derived by measurement).** (1) The headline 270 is the `gold_mult=1.0` figure; Britain is a hawk (x1.5) and the shipped P8 demand is 405 -- what `process_diplomatic_phase` actually emits. (2) "6,233 on the SAME state" is not the same instrument nor the same read: the settlement producer reads the SIDE score (-80, three covered courts) and would price 7,273 -> capped 6,994, scored by a different, capped acceptance formula. (3) The fix shape is regressive: any purse figure collapses through `_reduce_p8_demands` to the 200 floor with `_force_send` because `calculate_acceptance` prices `gold_lump` linearly, uncapped and treasury-blind (FA-N51) -- measured 6,994 -> 200 (below today's 405). The P8 envelope IS player-addressed (the cooldown key grammar proves it), and "bypassing the gate-blessed EC-W4" over-reaches: EC-W4's landing scope named only the settlement builder.

## Per row

### FA-N16 -- the incoming offer's voice and notification invert the indemnity's direction

**Ran:** `probe_1_fa_n16.py` (boot, end turn x4, read the boot offer; AI-pays / France-pays / four-court copies through the builder; the producer's direction table on t20), `probe_1b_fa_n16_promote.py` (the REAL producer -> promote -> notification -> mailbox path with France seeded to +60 vs Britain).

**Evidence (probe 1, shipped boot, turn 5):**
```
settlement_terms: [{'type': 'peace'}]
popup_payload.amount: 0
talleyrand_text: Sire, Britain has dispatched a settlement of France vs Britain. They ask 0 gold to close the war; ...
proposer_voice: His Majesty's Government offers terms for France vs Britain. London asks 0 gold and a return to peace; ...
[AI-PAYS] terms [{peace},{gold_indemnity from Britain to France 1358}] -> amount: 1358
[AI-PAYS] talleyrand_text: ... They ask 1358 gold to close the war; ...
[AI-PAYS] proposer_voice: ... London asks 1358 gold and a return to peace; ...
[AI-PAYS] terms_summary: ['Peace', '1358 gold (Britain -> France)', 'Status quo: ...']   <- the arrow is direction-correct
[AI-PAYS Austria] Metternich asks 1358 gold ... / [Prussia] Hardenberg names 1358 gold as the close / [Russia] The terms ask 1358 gold / [Saxony] Einsiedel asks 1358 gold
[PRODUCER] accepter_war_score=+60 -> [{peace},{gold_indemnity from Britain to France 3770}]   (t20 purse math)
[PRODUCER] accepter_war_score=-54 -> [{peace},{gold_indemnity from France to Britain 6233}]
```
**Evidence (probe 1b, the real path):** after rejecting the standing white peace, clearing `ai_settlement_cooldowns`, and seeding France +60 vs Britain, one `end turn` produced:
```
OFFER terms: [{'type': 'peace'}, {'type': 'gold_indemnity', 'from': 'Britain', 'to': 'France', 'amount': 1109}]
NOTIFICATION title: Settlement offer from Britain | message: Britain has offered terms to settle France vs Britain. Asking 1109 gold. | details.amount: 1109
OFFER proposer_voice: ... London asks 1109 gold and a return to peace; ...
OFFER talleyrand_text: ... They ask 1109 gold to close the war; ...
```
1109 = 0.40 x Britain's 2,773g chest -- Britain is paying France the most it can, and every headline surface says France is being dunned.

**Verdict: REPRODUCED.** Both arms of the row and the producer really emits the AI-pays direction (AUD-c, `SETTLEMENT_OFFER_DECISIVE_WAR_SCORE=20`).

**Seam by symbol:** `backend/game_logic/settlement_offers.py::build_incoming_settlement_offer_popup` (the `amount` loop and the two `resolve_settlement_voice_line(...)` calls with `amount=str(amount or 0)`); templates `settlement_incoming_offer_arrival_{talleyrand,castlereagh,hardenberg,metternich,einsiedel,chancery}` in `backend/game_logic/diplomatic_templates.py`; consumer `backend/game_logic/turn_manager.py` (the `promoted_offers` loop: `f" Asking {amount} gold." if amount else ""`). The same builder is re-run by `backend/main.py` at the mailbox-activate and `/pending_envoy` arms, so all three surfaces agree once the builder is fixed.

**What the filed fix would break / miss:**
- "emit `amount` as WHAT FRANCE IS ASKED TO PAY ... which makes turn_manager's `if amount` guard drop the false line for free" -- true for the notification, but it also makes the AI-pays notification say NOTHING about gold ("Britain has offered terms to settle ...") while the offer's whole point is 1109g of concession. Silent is honest but is a legibility loss; the notification should be able to say "Offering N gold." (one extra payload key, e.g. `amount_offered`, and a one-line arm in turn_manager -- NOT the zero-edit the row promises).
- The `details.amount` on the notification and the `amount` on the `settlement_offer_arrival` dispatch event are DEAD DATA: no `.gd` reads `details.amount` (grep `"amount"` in `notification_bar.gd`/`main.gd`: none), and `settlement_offer_arrival` has no template in `_DIPLOMATIC_EVENT_TEMPLATES` and is not in `SETTLEMENT_ROUTES`, so `_format_dispatch_event_text` returns `""` for it (`.get(event_type, "")`). The row's "the dispatch event for free" is a no-op either way.
- New voice families: `tests/test_incoming_offer_deferral_no_leaks.py` (the two family-list tests, ~lines 343-402) pin that every listed family resolves with no `{` left AND is named in `docs/DIPLOMAT_VOICE_BIBLE.md`. Any `settlement_incoming_offer_arrival_*_concession` family added to that list needs the Voice Bible entry or the pin reds.
- The AI-5c mediator arm PREPENDS to `proposer_voice` ("Under the good offices of ...") and APPENDS to `talleyrand_text` ("... an arbiter scorned remembers it."); `tests/test_ai_intent_mediation.py::test_mediated_offer_names_the_arbiter` (asserts "good offices"/"Russia"/"Arbiter of Europe" in `proposer_voice`, "arbiter scorned" in `talleyrand_text`) must keep passing -- select the family BEFORE the mediator wrap, never replace the wrap.

**Minimal correct fix:** in `build_incoming_settlement_offer_popup`, read the first `gold_indemnity` clause's `from`/`to` against `world.player_nation`: `player_pays = (from == player)`, `amount = amount if player_pays else 0` (keeps turn_manager's guard honest for free), `amount_offered = amount if to == player else 0`. Three-way family select: player pays -> the existing demand families unchanged; AI pays -> new `*_concession` families ("London offers {amount} gold to close the war ..."); no indemnity -> new white-peace families ("London asks no indemnity ..."), Voice Bible 16.1 amended for the twelve new keys. Optionally `f" Offering {amount_offered} gold."` in turn_manager. `terms_summary` already carries the arrow and needs nothing.

**Pins that flip:** none assert "asks N gold". Pins that must be preserved: `test_incoming_offer_deferral_no_leaks.py` ("vienna" in Austria's `proposer_voice`; no `{` in `talleyrand_text`; the family lists), `test_ai_intent_mediation.py` (mediator strings), `test_settlement_tier3_code_polish.py` (terms_summary strings), `test_w6_incoming_voice.py::test_offer_popup_appends_status_quo`.

### FA-N43 -- the incoming "Assessment" label is computed on the swapped orientation

**Ran:** `probe_2_fa_n43.py` (t20, Britain's cooldowns zeroed, `process_diplomatic_phase("Britain", w)` -> `build_ai_proposal_dialogue`; the inverse AI-pays arm; the penalty table; the outgoing control; the ratify-time value), `probe_2b_fa_n43_fallout_flip.py` (a real allied warning on the board under the shipped and the row-fixed harshness).

**Evidence (probe 2):**
```
proposal_type: harsh_peace recipient: France   demands: [{'type': 'gold_lump', 'value': 405}]  sweeteners: []
SHIPPED snapshot.harshness: 0.0 label: generous
SHIPPED annotated_terms: [('gold_lump', 'concession', 'France', 'Britain', 'France pays 405 gold to Britain')]   <- client renders "France concedes: France pays 405 gold to Britain" (direction-correct)
SHIPPED acceptance_hint: natural willingness to negotiate | rejection_hint: the harshness of current demands   <- same popup says GENEROUS and "harshness of current demands"
RECOMPUTED harshness on AI demands: 0.324 label: harsh
[INVERSE: Britain PAYS France 300/turn] shipped harshness: 0.3 label: harsh
[OUTGOING CONTROL France demands 405 of Britain] harshness: 0.32 harsh
[FALLOUT] harshness<0.2 doubles: 0.0 -> -30 / 0.2 -> -15 (ally ws 0, 6 turns, 6000 dead)
```
**Evidence (probe 2b, Spain made France's ally and put at WAR with Britain):**
```
[AI DEMANDS 405 of France]  shipped: harshness=0.0 label=generous fallout=[('Spain', -20)]
                            row fix (one keyword feeds label AND fallout): harshness=0.324 fallout=[('Spain', -10)]
[AI PAYS France 300/turn]   shipped: harshness=0.3 label=harsh fallout=[('Spain', -10)]
                            row fix: harshness=0.0 fallout=[('Spain', -20)]
```

**Verdict: REPRODUCED for the label; NARROWED on mechanism.** The snapshot's `harshness` is defined on the OUTGOING path as "what the target (the enemy) is asked to bear" (`calculate_treaty_harshness` over the proposer's `demands`); `_orient_incoming_terms_for_player` previews the incoming offer as France's mirror proposal and so preserves that definition exactly. Every consumer inside the snapshot that WANTS burden-on-the-enemy is therefore right today: `get_separate_peace_fallout_warnings` -> `_compute_separate_peace_penalty` doubles the ally penalty when `harshness < 0.2` -- a peace that pays the common enemy is soft on him, and Spain is twice as angry (-20). The only wrong reader is the "Assessment" label, which a player reads as burden-on-France. So the row's sentence "an AI demand for 405 gold reads GENEROUS and an AI gift of 300 gold/turn reads HARSH" is true of the LABEL, and false of the number.

**Seam by symbol:** the LABEL leak is in `backend/game_logic/mailbox_payloads.py::build_pending_envoy_popup_from_terms` (hands `preview_terms` to `build_war_context_snapshot` and copies its `harshness_label` out unchanged); `backend/game_logic/diplomacy.py::build_war_context_snapshot` (`harshness = calculate_treaty_harshness(harshness_terms)` -> `get_harshness_label`, and the same `harshness` into `get_separate_peace_fallout_warnings`); rendered by `incoming_proposal_popup.gd` ("Assessment: GENEROUS/HARSH"). The two outgoing sites that must stay byte-identical: `backend/game_logic/diplomacy.py` inside `get_diplomatic_preview`'s `peace_snapshots` loop (`build_war_context_snapshot(world, player, target_nation, ptype, terms=terms)`) and `backend/game_logic/diplomatic_dialogue.py::_enrich_proposal_summary` (`dialogue["war_context_snapshot"] = build_war_context_snapshot(...)`).

**What the filed fix would break:** "a `harshness_terms` keyword ... mailbox passes the UN-oriented `terms` for harshness" -- if that one number also reaches `get_separate_peace_fallout_warnings` (it does, `diplomacy.py` ~4294), the ally warnings flip in BOTH directions (measured above: -20 -> -10 for the P8 squeeze, -10 -> -20 for the AI gift), and the ratification-time `apply_separate_peace_penalties` (which recomputes from the treaty clauses, not the snapshot) would then DISAGREE with the preview the player was shown. The row's own truncated "Knock-on to measure while fixing: diplomacy.py:4294 feeds the same `harshness` into..." is this knock-on; the fix text does not resolve it.

**Minimal correct fix:** two numbers, not one. Keep `harshness` (burden on the enemy) untouched -- it feeds the fallout warnings and the OUTGOING label correctly. For the incoming route only, in `build_pending_envoy_popup_from_terms` AFTER the snapshot returns, overwrite `snapshot["harshness"]`/`snapshot["harshness_label"]` (and the payload copies) with `calculate_treaty_harshness({"clauses": [], "demands": terms["demands"]})` computed on the UN-oriented AI demands = burden on France. Zero `diplomacy.py` change, zero `.gd` change, the two outgoing sites untouched by construction, `annotated_terms`/`fallout_warnings` untouched.

**Pins that flip:** none assert the incoming label (`test_bph_b_peace_preview.py::test_snapshot_harshness_label_present` only requires membership in the four labels on the OUTGOING snapshot; `test_bph_c_fallout_conflicts.py::test_generous_peace_doubles_penalty` / `test_harsh_peace_no_doubling` / `test_generous_severe_penalty` pin `_compute_separate_peace_penalty` on explicit values and are exactly the pins the row's fix would silently defeat on the incoming route). New pins: (a) P8 405 -> label "harsh", fallout Spain -20; (b) AI gift 300/turn -> label "generous", fallout Spain -10.

### FA-N45 -- gold_lump / manpower_* / ap_per_turn score 0.0 in the clauses dialect

**Ran:** `probe_3_fa_n45.py` (t20, `w._ratify_treaty` with a 405 `gold_lump` demand; the mirrored-branch table; the sweetener direction case; DD8-4 fire on the next proposal; the ally-penalty seam; the settlement-path comparison), `probe_3b_fa_n45_direction.py` (three record recipes on three ratified shapes), `probe_3c_shape4.py`.

**Evidence (probe 3):**
```
ratify result type: diplomatic_treaty_signed | France gold: 17487 -> 17082 | Britain gold: 9425 -> 9830 | state after: PEACE
STORED harshness: 0.0 | clauses: [{'type': 'gold_lump', 'from': 'France', 'to': 'Britain', 'amount': 405}]
recompute demands-dialect: 0.324
peace_ratified event harshness: 0.0 gold_paid: 405 gold_received: 0 war_outcome: enemy_victory
[MIRROR] gold_lump 375: mirrored=0.3 DD8-4(>0.3)=no | 376: 0.301 YES | 405: 0.324 YES     (DD8-4 threshold = 375g strictly greater)
[MIRROR] ally-penalty doubling threshold (<0.2) = 250g
[SWEETENER 500 Britain->France] stored today: 0.0 | mirrored fix would store: 0.4 -> DD8-4 -5 on every later France|Britain proposal: True
[TODAY gold_indemnity AI pays France 1358] clause-dialect harshness: 1.0 (direction-blind: same as France paying)
[DD8-4] next France->Britain proposal harshness_bonus TODAY: 0 | with the record at 0.324: -5 (score 1 -> -4)
[ALLY PENALTY] harshness 0.0 (today): -30 | 0.324 (fixed): -15
[SETTLEMENT] package raw harshness (direction-aware, AI pays): 0.0 | the ratify record's clauses-dialect on the same terms: 1.0
```
**Evidence (probe 3b):**
```
[Britain demands 405 of France]   (A) today=0.0  (B) mirrored=0.324  (C) burden on France=0.324 / on Britain=0.0
   ally-penalty doubles (should read burden on the ENEMY Britain): A=True B=False C(on Britain)=True
[Britain PAYS France 500]         (A) 0.0  (B) 0.4  (C) on France=0.0 / on Britain=0.4
   DD8-4 fires: A=False B=True C(on target France)=False
[France cedes Savoy as sweetener] (A) 0.3  (B) 0.3  (C) on France=0.3 / on Britain=0.0   <- direction-blindness is PRE-EXISTING for territory_cede
```

**Verdict: REPRODUCED**, with a direction hazard inside the filed fix. `_ratify_treaty` (`backend/models/world_state.py`) builds `treaty_clauses` from sweeteners (`from`=proposer) AND demands (`from`=target) and stores `calculate_treaty_harshness({"clauses": treaty_clauses})` -- a sum over everybody's burden. Today the four types fall through, so a 405g squeeze stores 0.0 and DD8-4 (`calculate_acceptance` in `backend/game_logic/diplomacy.py`, the `prev_treaties ... > 0.3 -> harshness_bonus = -5` loop) never fires on a bilateral gold peace; the ratification ally penalty (`apply_separate_peace_penalties`, fed `calculate_treaty_harshness(treaty)` at `_ratify_treaty`'s BPH-C block) is ALWAYS doubled for a gold-only bilateral peace regardless of who paid.

**Seam by symbol:** `backend/game_logic/diplomatic_templates.py::_accumulate_raw_treaty_harshness` (the clause loop has no `gold_lump` / `manpower_infantry|cavalry|artillery|manpower` / `ap_per_turn` branch); the record writer `world_state.py::_ratify_treaty` (`"harshness": calculate_treaty_harshness({"clauses": treaty_clauses})`); consumers: DD8-4 in `diplomacy.py::calculate_acceptance` (`harshness_bonus`), `_ratify_treaty`'s `apply_separate_peace_penalties(... calculate_treaty_harshness(treaty))`, `diplomatic_ledger.py::_build_treaties` via `get_treaty_harshness_for_consumer` (the client NEVER renders it -- no `harshness` in `diplomatic_ledger.gd`), and the `peace_ratified` event's `harshness` field (no reader found in `campaign_log.py`/`dispatch.py`/`gazette.py`). The settlement path stores its OWN record in `settlement_ratify.py::_record_common_peace_treaties` with the same direction-blind clause dialect (an AI-pays 1358 `gold_indemnity` stores 1.0), while its ACCEPTANCE is direction-aware (`settlement_scoring.compute_settlement_package_raw_harshness` excludes proposer-paid clauses).

**What the filed fix would break:** mirroring the four rates into the direction-blind clause loop (a) makes a treaty in which the AI PAYS France 500 store 0.4 -> DD8-4 -5 forever on the pair (the concession is booked as harshness); (b) flips the ally-penalty doubling the WRONG way for a France-pays peace: France paying Britain 405 is soft on Britain and should keep the doubled -30, the mirrored record gives 0.324 -> -15; (c) the 250g doubling threshold and the 375g DD8-4 threshold become live cliffs on every bilateral gold peace with no direction check. The row's "DIRECTION-4 WARNING: this changes ca..." (truncated) names the class but the fix is still the mirror.

**Minimal correct fix:** make the RECORD direction-aware rather than the loop richer. Store `harshness` = burden on the proposal's TARGET, computed in the demands dialect that already prices all four types: `calculate_treaty_harshness({"clauses": [], "demands": proposal.get("demands", [])})`; feed `apply_separate_peace_penalties` the burden on the ENEMY (`penalty_target`): the demands-dialect sum over `treaty_clauses` whose `from == penalty_target`. Adding the four clause branches is still worth doing for the settlement record (`settlement_ratify` prices `gold_indemnity` there already) but MUST be paired with a `from` filter; the census pin the row asks for should be written as "every demands-dialect type prices in the clause dialect when `from` is the burdened party" -- i.e. a direction-aware parity pin, not a bare type-set subtraction. Conscious flip to record: a France-proposed peace that cedes a province as a SWEETENER stores 0.3 today (direction-blind) and 0.0 under burden-on-target; no test pins it.

**Pins that flip:** none pin the stored bilateral value (the `"harshness": 0`/`0.5` records in `test_phase2b_diplomacy.py`, `test_bph_d_ratification_summary.py` are hand-built). Preserved-by-construction: `test_bugfix_session_a.py::TestHarshness` (demands dialect), `test_bugfix_session_b.py::test_territory_clause_harshness_0_3` (clause dialect, unchanged if branches are added not removed), `test_bugfix_session11.py::test_harshness_bonus_inverted` (hand-set record 0.5 -> -5), `test_common_peace_harshness.py` (clamp/raw helpers), `test_bph_c_fallout_conflicts.py` penalty pins.

### FA-21 -- AI harsh-peace demands are purse-blind on the bilateral P8 path

**Ran:** `probe_4_fa_21.py` (the row's exact repro; Britain's real `gold_mult`; the multi-party war read; EC-W4 in both signs; the acceptance/reduction table; formula census; `process_diplomatic_phase` on the fixture), `probe_4b_fa_21_tail.py` (the SIDE-score EC-W4 figure; the settlement scorer's capped term vs the bilateral linear term; the P8 gate; the P8 popup; the row's fix end to end).

**Evidence:**
```
Britain ws vs France: 54 | France gold 17487 | Britain gold 9425 | Britain diplomat: hawk, gold_demand_mult 1.5
Britain cooldown keys: {'Britain|nation': 1, 'Britain|harsh_peace': 5, ...}       <- `{nation}|{type}` IS the recipient=player arm (`_cooldown_keys`); TYPE cooldown 6 -> written turn 19 by rejection/lapse
war war_1: France=attackers, opposing=['Britain','Austria','Russia'] | pair France vs Britain: -54 | SIDE score: -80
[P8] gold_mult=1.0 (the row): 270   | with Britain's real gold_mult: 405
[PHASE] process_diplomatic_phase('Britain') on t20 (cooldowns zeroed): ('harsh_peace', 'France', [{'gold_lump': 405}], _force_send None) acceptance 33 COUNTER_OFFER
[EC-W4] accepter_war_score=-54 (pair): 6233 (scaled 6233, cap 6994)   | with the SIDE score -80 (the producer's real read): 6994 (scaled 7273, cap 6994)
[EC-W4 SIGN-FLIPPED +54]: Britain PAYS France 3770   <- a mis-signed `payer = recipient` call ships a concession, not a squeeze
[ACCEPT] 270: 53 (deal -8.1, harsh -2) -> unchanged | 500: 18 -> halved to 250 | 1000: -7 -> 200 _force_send | 6233: -164 (deal -187, harsh -40) -> 200 _force_send
[FORMULA] calculate_acceptance reads treasury/nation_gold: False | gold_mult reads a purse: False
settlement term_harshness_penalty for 6233g = -45 (capped)  vs  bilateral deal_balance -187.0 + harshness_penalty -40 (linear, uncapped)
ROW FIX end-to-end: purse 6994 -> after _reduce_p8_demands: [{'gold_lump': 200}] _force_send True   (shipped today: 405)
P8 gate: is_at_war True | ws>40 True | effective_p1_threshold -61 | Britain WE 154
P8 popup: 'Demand: Gold payment - 405' | terminal: 'Britain demands 405 gold' | snapshot label: generous (FA-N43)
```

**Verdict: NARROWED.** The defect stands -- the P8 arm never reads a treasury and demands ~2.3% of France's chest at +54 -- but three load-bearing parts of the row are wrong in ways that change the build (re-derived; the Sept-2 record is truncated at ~300 chars and the memo table says "five corrections", the first two of which "make it larger"):
1. **The headline number is wrong for the shipped board.** 270 is `gold_mult=1.0`; Britain's diplomat is a hawk and `process_diplomatic_phase` emits **405**. The severity (purse-blind) is the same; the figure the player sees is 1.5x the row's.
2. **"6,233 on the SAME state" is apples to oranges twice over.** The settlement producer reads the WAR (`sum_stored_side_score`, -80 across Britain+Austria+Russia), not the pair (-54), so it would price 7,273 -> **6,994** at the cap; and that figure is a MULTI-PARTY instrument scored by `settlement_scoring` (term harshness capped at -45), not a bilateral pair scored by `calculate_acceptance`. The bilateral channel is not "bypassing" EC-W4: EC-W4's landing (memo row 4, `_settlement_offer_build_terms rewritten`) never named the P8 arm. This is an un-scoped sibling -> a design gap that needs the acceptance seam gated first, not a copy-the-formula bug fix.
3. **The fix shape ships a SMALLER demand (FA-N51).** `calculate_acceptance` prices `gold_lump` at -3/100 linearly, uncapped and treasury-blind, then `_reduce_p8_demands` halves ONCE and falls to `{gold_lump: 200}` + `_force_send`. Any purse figure on this board collapses to 200 -- below today's 405. "Make `_reduce_p8_demands` halve relative to that figure" cannot pass the `score < 20` filter either (500g already scores 18). The fix is dead as written.
Also confirmed FOR the row: the P8 envelope is player-addressed (recipient France; the fixture's `Britain|harsh_peace: 5` is the player-arm key), so "fires in ordinary play" holds; and `gold_mult` is personality-only (hawk 1.5 / dove 0.75), nothing purse-like scales it.

**Seam by symbol:** `backend/game_logic/ai_diplomacy.py::_build_proposal_terms` (the `harsh_peace` arm: `gold_demand = max(200, int(war_score * 5 * gold_mult))`), `::_reduce_p8_demands` (one halving, `max(200, ...)`, then the hard-coded 200 fallback + `_force_send`), the P8 gate in `::process_diplomatic_phase` (`is_at_war and war_score > 40`), the `score < 20 and not _force_send` filter just below it; the pricing that must move FIRST is `backend/game_logic/diplomacy.py::calculate_acceptance`'s `DEMAND_VALUES["gold_lump"] = -3/100` into `deal_balance` (and `harshness_penalty` capped at -40).

**What the filed fix would break:** measured above -- 405 -> 200 with `_force_send`, i.e. the AI's winning teeth get SHORTER; and a mis-signed `payer = recipient` (the row's own phrasing, with `_settlement_offer_build_terms`'s `accepter_war_score` semantics being the ACCEPTER's perspective) ships Britain paying France 3,770 at +54 -- the exact inversion the preamble warns about. `tests/test_da1_ai_intelligence.py::TestA1GoldFormula` (test_floor_200, test_scaling_at_50/80/100, test_hawk_multiplier, test_dove_multiplier, test_floor_with_low_war_score, test_old_formula_would_give_different_values) and `tests/test_diplo_refinement_wave2.py::test_gold_scales_with_war_score` (asserts 250/400) all pin `war_score * 5 * gold_mult` and red on any repricing; `TestA1Reduction::test_gold_halved_floor_200` / `test_fallback_sets_force_send` pin the 200 floor and `_force_send`.

**Minimal correct fix (order matters):** (i) FA-N51 first -- price `gold_lump` in `deal_balance` as a fraction of the PAYER's treasury (or cap it, mirroring the settlement path's -45), so a purse-proportional lump costs a purse-proportional amount of acceptance; (ii) then one shared purse helper (base + war-age + |score| x 40 + 0.15 x payer treasury, cap 0.40 x payer treasury, empty chest -> no lump) called by BOTH `_settlement_offer_build_terms` and the P8 arm with `payer = the recipient of the demand` (for a player-addressed P8 that is France; write the sign as "the DEMAND's payer", never as a war-score sign); (iii) `_reduce_p8_demands` halves toward a purse floor (e.g. 0.15 x payer treasury) instead of 200. Precondition pin per FA-N51: after `_reduce_p8_demands` on t20 the surviving lump >= 0.15 x France's treasury and `_force_send` is falsy (fails today at 200/True). Re-bless the `TestA1GoldFormula` numbers consciously.

## Cross-row findings

1. **The incoming P8 popup contradicts itself on one screen (FA-N43 corollary):** `Assessment: GENEROUS` (the mirror number) beside `rejection_hint: the harshness of current demands` (the un-oriented acceptance). Two acceptance readings ride the same popup payload: `acceptance_hint`/`rejection_hint` from `calculate_acceptance(terms)` on the AI's real terms, and `war_context_snapshot.acceptance_preview` (21, REJECT) on the MIRROR terms -- the latter is dead data (`incoming_proposal_popup.gd` reads only the hints), so harmless, but any future `.gd` that renders the snapshot preview on the incoming route would show Britain's own offer as "REJECT".
2. **Direction-blindness of the treaty record is pre-existing and wider than FA-N45:** `gold_indemnity` and `territory_cede` clauses are already priced without a `from` check, so the settlement record for an AI-pays 1358 stores 1.0 and a France-cedes-as-sweetener bilateral stores 0.3. The settlement ACCEPTANCE is direction-aware (`compute_settlement_package_raw_harshness`, G4F-1), its RECORD is not. DD8-4 is itself pair-symmetric ("harsh history" regardless of who was harsh to whom) -- any direction-aware record needs a ruling on which side's history DD8-4 should read.
3. **Dead data census:** `notification.details.amount` (no `.gd` reader), the `settlement_offer_arrival` dispatch event (no template, no route -> renders `""`), the Treaties-tab `harshness` (computed by `diplomatic_ledger.py`, never rendered by `diplomatic_ledger.gd`), and `peace_ratified.harshness` (no reader found). The only LIVE consumers of stored treaty harshness are DD8-4's -5 and the ratification ally penalty (which recomputes from clauses).
4. **The settlement path's own indemnity direction on the boot board:** at boot Britain's offer is a white peace ("They ask 0 gold" is the FA-N16 zero arm, exercised on every fresh campaign by turn 5); the AI-pays arm needs France at >= +20 vs the opposing leader, reached in ordinary play only after victories -- so the false "Asking N gold" is a mid-campaign surface, the "0 gold" one is a turn-5 surface.
5. **A France-proposed peace carrying an `ap_per_turn` demand returns `diplomatic_treaty_failed` on the t20 fixture** (probe_3c; `gold_lump` alone ratifies). Not investigated (time-box); noted because the FA-N45 row treats `ap_per_turn` as a reachable bilateral clause.
6. **Harness trap:** grep filters of the form `grep -v "^\[AI"` eat a probe's own `[AI-PAYS]` lines -- prefix probe output (`G4|`) and grep for the prefix instead.
7. **Row-text availability:** the FA-N16/N43/N45 rows exist ONLY as truncated table cells in `BUG_FIXES.md` / the Sept-2 memo (no JSON record), and FA-21's `corrected_reading` in `final_audit_2026_09_01_findings.json` is truncated at ~300 chars in the machine record itself; the "three load-bearing parts" above are re-derived, and the memo's own table line says "five corrections".

## Probe inventory

- `repro/g4/probe_1_fa_n16.py` -- boot offer voice/amount; AI-pays / France-pays / four-court copies; the producer's direction table on t20.
- `repro/g4/probe_1b_fa_n16_promote.py` -- the real producer -> promote -> notification path with France seeded +60 (Britain pays 1109, notification says "Asking 1109 gold.").
- `repro/g4/probe_2_fa_n43.py` -- t20 P8 proposal through `build_ai_proposal_dialogue`; shipped vs recomputed harshness/label; inverse AI-pays arm; penalty table; outgoing control; ratify-time value.
- `repro/g4/probe_2b_fa_n43_fallout_flip.py` -- a real allied fallout warning under the shipped and the row-fixed harshness, both directions.
- `repro/g4/probe_3_fa_n45.py` -- bilateral ratify of a 405 `gold_lump` demand; mirrored-branch table with the 375g / 250g cliffs; sweetener direction case; DD8-4 fire; ally-penalty seam; settlement comparison.
- `repro/g4/probe_3b_fa_n45_direction.py` -- three record recipes (today / mirrored / burden-on-party) on three ratified shapes.
- `repro/g4/probe_3c_shape4.py` -- why the fourth shape did not ratify (`ap_per_turn` demand -> `diplomatic_treaty_failed`).
- `repro/g4/probe_4_fa_21.py` -- the row's repro; real `gold_mult`; multi-party read; EC-W4 both signs; acceptance/reduction table; formula census; `process_diplomatic_phase` on the fixture.
- `repro/g4/probe_4b_fa_21_tail.py` -- side-score EC-W4 figure; capped vs linear pricing; P8 gate; P8 popup; the row's fix end to end (6,994 -> 200 + `_force_send`).
