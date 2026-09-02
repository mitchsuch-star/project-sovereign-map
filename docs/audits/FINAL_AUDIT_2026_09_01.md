# FINAL WHOLE-GAME AUDIT — September 1, 2026

> **What this is.** The last audit before ROADMAP position 10 (the shippable
> build), run at master `ccf5f111` on the evening row WO closed. The user's
> brief, verbatim: *"see if the game is missing anything, if anything is
> working poorly, if commands work well, ai works well, if anything can be
> added to make things tie better … a last nice audit … assure audit results
> are documented well enough for opus to fix them or add them."*
>
> **Report-only for the game.** No production behaviour was changed by the
> audit. Two commits precede it and are not part of it: `96c4c896` (WO-41, the
> row's last unowned residue) and `ccf5f111` (the playtest driver learning to
> answer a redemption audience, plus the nine archived arms below).
>
> **Routing.** Every finding is filed: `BUG_FIXES.md` §Final Whole-Game Audit
> (FA-1..FA-102) and `DESIGN_REFINEMENT.md` §FA-D (FA-D1..FA-D26). The
> untruncated machine record — every field of every finding, including the ones
> trimmed for readability here — is committed beside this memo as
> **`final_audit_2026_09_01_findings.json`**. §3 is written so an engineer who
> has never read this session can act on any row: seam, reproduction, the one
> seam to change, and the behaviour test to write.

## 0. Evidence and method

**Evidence — nine seeded campaigns, ~200 played turns, all archived** (a memo
may only cite an archived digest; `docs/PLAYTESTING.md`). Under
`docs/audits/playtest_digests/`:

| arm | what it drove | turns | how it ended |
|---|---|---|---|
| `audit-flagship-mock` | the flagship fighting script, mock parser, objection policy INSIST | 24 | 26 provinces · 41 battles · 111 popups · **Ney a prisoner of Austria (t23)** · Napoleon's corps broken (t24) |
| `audit-flagship-live` | the same script on the LIVE Anthropic parser | 12 | 29 provinces · 22 battles · 37/37 commands identical to the mock arm — **and only ONE Anthropic call in twelve turns** (§0.1) |
| `audit-propose` | France sues for peace every turn (`--diplomacy propose`) | 24 | Austria signed on t22 **while holding Swabia, Lyonnais, Languedoc and Provence** · 22 provinces · +2,234g/turn at peace |
| `audit-ambient40` | France issues no orders; Europe acts | 40 | **6 provinces** · Lannes at trust 0 · a petition queued on t3 still undelivered at t41 |
| `audit-ambient-ulm` | the same, seed `ulm` | 24 | 13 provinces |
| `audit-ambient-austerlitz` | the same, seed `austerlitz` | 24 | 8 provinces |
| `audit-latewar-t20` | from the committed turn-20 fixture, late-war diplomacy script | 10 | 6 provinces · Paget walked the west three provinces a turn · Paris still French |
| `audit-naval` | the Descent script | 20 | 23 provinces · the Grand Diversion spent on t5 · no expedition ever sailed |
| `audit-tutorial` | the School of War (`--scenario tutorial`) | 10 | completed · 5 battles · Kienmayer captured t2, "Unknown target: Kienmayer" t3 |

Plus the parser golden corpus: **548/548 under the mock parser, 527/531 live**
(the four misses are two rows × two worlds — FA-73).

**Method.** Evidence first, then a find → refute → report fleet at the
committed SHA. Sixteen lens finders (parsing · executor/dialogue/popup channel ·
combat · strategic orders · marshal drama · enemy AI military · AI diplomacy ·
player diplomacy · economy+vassals · naval · narration · client UI · save/turn
boundary · onboarding/build · missing-and-tie-ins · the harness itself), each
required to open the file it cites and to reproduce runtime claims by snippet or
driver probe. Plain-code dedupe by seam and title. Then adversarial refuters
(mechanism and reachability), each told to default to REFUTED. **207 raw
findings → 130 after dedupe → 128 live (2 refuted) + 41 working-well notes.**

**⚠ What this audit did NOT do, stated plainly.** The run hit the session usage
limit three times. The finders all completed; the refuter pass did not, and the
ten pillar scorers, the completeness critic and the machine synthesis never ran
at all. Consequences, each visible per finding in §3:

- **There is no pillar re-score in this memo.** The Aug-16 priors (`Command &
  parsing 6.5 · Marshal drama 7.5 · Combat legibility 7.0 · Narration 6.5 ·
  Economy 6.5 · Diplomacy 6.0 · AI aliveness 7.5 · Vassals 6.5 · Naval 6.5 ·
  UI/UX 7.0 · directional ≈6.8`) stand un-refreshed. §1 gives a qualitative
  read, argued from evidence, and does not pretend to be a score.
- **36 findings carry a refuter verdict; 46 are UNVERIFIED** and say so in their
  own block. UNVERIFIED means *nobody tried to kill it*, not *it survived*.
  Treat an UNVERIFIED row as a lead with cited evidence, and reproduce before
  building. **The two REFUTED rows (§4) are the calibration**: where refuters
  did run, they killed real claims with real probes.
- The critic's gap round never ran, so the audit's own blind spots are unnamed.

**Verdict vocabulary used in §3:** CONFIRMED (two refuters agreed — *no row
reached this bar; the budget allowed at most one refuter per row*) · NARROWED
(a refuter corrected the claim; the corrected reading is the one printed) ·
PLAUSIBLE (one refuter) · AUTHOR-VERIFIED (hand-reproduced by the session
author, independently of the fleet) · HARNESS (author-checked) · UNVERIFIED (as
above).

### 0.1 One correction to this session's own evidence

I reported mid-session that the live-parser arm matched the mock arm on all 37
commands and offered it as parser-quality evidence. **That reading is wrong and
is corrected here rather than dropped.**
`tools/playtest_runs/audit-flagship-live/server_console.log` records exactly
**one** Anthropic call in twelve turns — `Soult, deal with the Austrians` →
`action=unknown, ambiguity=72`, the CR-5 delegation ASK. The other 36 commands
cleared the fast parser's 0.7 confidence gate and never reached the LLM. So the
identity measures fast-parser determinism, not live-parser equivalence. What it
does show is worth keeping: **the shipped scripts never exercise the escalation
path**, and the two parsing defects below (FA-7, P1; FA-6, P2) are exactly the sentences that
path would have had to see.

## 1. The verdict — the user's five questions, answered

**Is anything missing?** Nothing structural that is not already owned. The
holes are *joins*, not systems: 26 of them are filed as FA-D. The pattern is
that a value is computed correctly and no other system reads it — a captured
marshal is priced at the peace table but no generator ever offers his release
(FA-D3); the player's `garrison` verb feeds no stability while the tooltip
recommends garrisoning (FA-D19); a war purpose ticks the coalition score and the
war panel cannot show it (FA-D2); Trafalgar cannot lead a morning dispatch
(FA-66). Seven true absences are filed as `missing` in §3 — the largest being
that **the administrative role promises "future restoration" and only a debug
cheat can grant it** (FA-71).

**Is anything working poorly?** Yes, and the through-line is the one CA9 named
in August and it has moved one seam further down: **the engine computes the
right answer and a surface tells the player something else.** A vassal's
rebellion is briefed as *"Switzerland has ceased to exist"* while Switzerland is
alive and at war with you (FA-2). A bombardment campaign that killed thousands
narrates as nothing at all (FA-25). A marshal cornered and asked to make a last
stand is asked once and then ground to nothing over eleven battles because the
standing question suppressed his retreat (FA-1). The end-turn-only player is
never shown a marshal's petition (FA-5). None of these is a regression from a
recent slice; they are what a 200-turn evidence base loads that a 9-turn one
cannot.

**Do commands work well?** Mostly, with **two exceptions that a first-time
player will hit in their first hour — one of them a P1 — both hand-reproduced,
both live in the shipped mock-default build, and neither rescued by the live
parser** (measured:
the LLM is never consulted for either, because the fast parser is confident):

- `what happens next turn` **ends the turn** and runs the enemy phase (FA-6).
  So does `we will decide next turn`. A question mark saves you; the same
  sentence without one does not. *(Amended Sept 2: downgraded to P2 — action
  points do not carry over, so nothing is banked or stolen. The defect is that a
  non-command irreversibly advances the turn, inconsistently.)*
- `Ney, delay the attack` / `attack Mack later` **fight the battle immediately**
  (FA-7). PARSE-NEG taught the guards negation and contingency; it never taught
  them deferral.

Add `Ney, blockade Vienna` re-tasking the fleet (FA-11) and a compound order's
second clause vanishing without a word (FA-50), and the shape is clear: the fast
parser matches keywords, not meaning, and its confidence is highest exactly when
it is wrong. Everything else the lens tried — negation, pronouns, carryover,
nation demonyms, refusals — answered honestly, and the corpus is 548/548.

**Does the AI work well?** Strategically yes, tactically no. Europe is alive:
designs promote, coalitions hold, Britain runs a real Peninsular campaign at
Lisbon on every seed (§5), and Austria fights a coherent war. But three
measured behaviours would read as dumb to a Paradox player. **P4.25 prices a
garrison and never looks at the field army standing on it** (FA-8), which is why
Austria's corps suicide into the French stack at Munich turn after turn — 48
attacks across nine digests where the attacker lost ≥1,000 men. **P4 has no
target-worth floor**, so the AI spends a whole action budget on a remnant under
a thousand men (FA-35) — eleven attacks over four turns on a 100-man Massena in
the late-war arm. And **one corps flips a homeland province per action point
with nothing to stop it** (FA-D14): Paget walked ten French provinces in eight
turns because an unfortified, ungarrisoned province is an instant capture.

**What would tie things together?** The join I would build first is argued in
§7; the rest are grouped into the eight slices of §6 (slice 7 is FA-26's own
neighbourhood). The cheapest one that changes the most: **make the neglect arc end.**
Reward erosion drives a marshal's trust to zero (measured: **three of France's
seven marshals** — Lannes, Bernadotte and Massena — at trust 0 by turn 41 of the
ambient arm, none ever endowed, Lannes with eleven battles won) and nothing ever
asks the redemption question, because the erosion seam does not consult
`check_redemption_threshold` (FA-26). One call turns forty turns of a marshal
quietly rotting into the audience the system was built to deliver. *(⚠ Sept 2,
2026: this read "**the** one trust-writing seam" and "one call, at one seam".
Both over-claimed — see the FA-N1 amendment at §7: there are four unchecked
families, and the fix should be a shared helper.)*

## 2. What the campaigns actually were

**The flagship (mock, 24 turns).** France opens historically, masses on Mack and
wins every battle it starts until t19, when Murat's assault on a fortified
Buxhowden is repulsed for 4,328 men against 807 — Bernadotte on t1, Ney and
Davout through t5, Murat
taking 26,371 Austrians for 348 of his own on t3. Vienna is pressed and the arc turns on t23 when **Ney is taken prisoner** (`Marshal Ney is
a prisoner of Austria, Sire — no order can reach him until his release`) and
Napoleon's own corps is broken on t24. Treasury peaks at 20,333 and falls to
15,735; provinces 28 → 26. Sixteen marshal petitions arrive and are answered.
Britain offers an armistice on t23 and the policy declines it.

**The same script on the live parser (12 turns).** Byte-identical decisions;
one LLM call (§0.1).

**France sues for peace (24 turns).** Every turn France proposes to a court she
is at war with. The alliance-paradox wall refuses her twice — *"Making peace
with Austria while allied with Bavaria … creates a diplomatic contradiction"* —
and names no road through (FA-D17). On t22 **Austria signs** — while, in the same
enemy phase, Archduke John walks into Provence and Languedoc unopposed. The
peace freezes an occupation of four provinces including three homeland ones, and
the treasury turns from −687/turn to +2,270 the moment it is signed.

**Ambient, 40 turns, France passive.** The control arm, and the most useful. The
economy converges exactly as EB-1 designed: +1,961/turn at t1, +839 by t15,
negative from t16, and the homeland collapse from t29. France ends on **six
provinces** with 4,683 gold. Britain storms the Flanders garrison on t38. And
across all forty turns **not one marshal petition is delivered** (FA-5) while a
grievance ages to 34 turns.

**Two more seeds (24 turns each).** A passive France ends on 13 provinces
(`ulm`) and 8 (`austerlitz`) against the historical seed's trajectory — the D7
variance contract doing its job.

**Late war, from the committed t20 fixture (10 turns).** The bleakest arm, and
the one that produced the most findings. Paget takes Gascony, Guyenne and Anjou
in a single enemy phase, then Maine and Brittany, then Normandy, Artois, Picardy
and Ile-de-France. Massena's corps is ground from 21,067 men to 32 over eleven attacks in four
turns and destroyed (FA-1's own trace; the digest's `Massena (lost 41)` is one
battle's casualties, not his remaining strength). France falls 16 → 6 provinces. Britain and the
coalition offer peace, and the accept path stages a review the offering court
itself rejects (FA-3).

**The naval Descent (20 turns).** France lays a keel every turn while readiness
falls 69 → 63 → 58, and the message blames green crews for what is blockade rot
(FA-45). The Grand Diversion is drawn up and spent on t5; its outcome is
narrated nowhere the digest can see (a harness blind spot, FA-76). No expedition
ever sails, because the corps was never at a dockyard and the refusal only says
so after the order is given (FA-51).

**The School of War (10 turns).** The lesson completes. It also, played exactly
as Berthier counsels, loses six French homeland provinces by turn 10 to a
1,218-man retreating remnant (FA-9), tells the player Kienmayer
"is our prisoner" and then answers `Unknown target: Kienmayer` when they attack
him (FA-48), and promises a trust-branch pivot the scenario never delivers
(FA-42).

## 3. Findings

> Every row carries its seam, a reproduction, the ONE seam to change and the
> behaviour test to write. Ids are the filed row ids (`FA-n` in `BUG_FIXES.md`,
> `FA-Dn` in `DESIGN_REFINEMENT.md`). Read the verdict line before building:
> UNVERIFIED means no refuter tried to kill it.

### 3a. Defects — P1 (fix first) (8, plus FA-6, downgraded to P2 on Sept 2 and left in place)

#### FA-1 [P1 · defect] A standing last-stand ASK suppresses the retreat on every re-attack: the marshal is ground to nothing over 11 battles and DESTROYED, never asked, never captured

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/commands/combat_executor.py:3195`
**Already filed:** PS-7 (closed, P3) covers only that the enemy-phase last-stand decision never pops; PC-9 covers the duplicated 'is cornered' rail rows. Neither files the re-attack grind, the victor advancing onto an un-retreated defender, or the DESTROYED-instead-of-captured outcome. NEW.

**What it is.** W6-7's fate arm (`_check_marshal_fate`, combat_executor.py:3195) fires on EVERY forced retreat with no guard for an already-standing `pending_interrupt`. For an aggressive player marshal whose only exit is tier-5 at-war soil (`desperation_only`, :3233-3240) it sets `pending_interrupt=last_stand` (:3313-3328) and returns a message, which `_apply_forced_retreat_or_break` treats as 'retreat consumed' (:3484-3486) — so the marshal does NOT move. The victor then advances INTO his province because `can_advance = victor == marshal.name` ignores that the defender still stands (:6689-6698, 'MOVING Mack: Milan -> Piedmont' in the console with `defender_fled=False`). Every co-located enemy corps is then FORCED to attack him by the P0 engagement rung (enemy_ai.py:1615 weakest-enemy, :1674 attack) before anything else, and each new attack re-runs the fate arm, re-raises the same ask and again suppresses the retreat. Verified by running: the driver reproduction of audit-latewar-t20 shows Massena at Piedmont, `pending_interrupt=last_stand`, `retreating=False`, strength 21,067 → 8,848 (turn 25) → 702 (turn 26) → 58 (turn 27) → `[DESTROYED] Massena reduced to rubble (32 -> 0)` (server_console.log:5…

**What the player sees.** The player's aggressive marshal (Massena, Ney, Lannes, Murat) is 'CORNERED — awaiting your word' during the enemy phase, but the enemy phase does not wait: every other adjacent enemy corps attacks him in the same phase, so a 15,000-man corps is destroyed piecemeal before the player can type an answer. He gets neither the +25% last stand nor a capture (which would have returned 50% of his men to the manpower pool and made him ransomable) — the two outcomes the W6-7 promise names. The flagship digest shows the same shape for Lannes (turn 13: 3,673/2,654/1,056/496 in one phase, DESTROYED at Munic…

**Evidence.** combat_executor.py:3195-3240 (fate trigger, no pending_interrupt guard), :3313-3345 (player-aggressive ask, returns message), :3484-3486 (message = retreat consumed), :6689-6698 (`defender_fled`/`can_advance`), :6743-6744 (MOVING/move_to); enemy_ai.py:1615, :1674 (P0 engagement attacks the weakest co-located enemy); probe run server_console.log lines 3106-3124 ('[RETREAT RESULT] Massena retreats to Lyonnais (DESPERATION into at-war soil)' → '[ATTACK MOVEMENT] MOVING Mack: Milan -> Piedmont' → '[P0 ENGAGEMENT] Mack vs Massena … -> ATTACK Massena' → '[P0 ENGAGEMENT] ArchdukeJohn … -> ATTACK Mass…

**Reproduce.** C:/Users/User/PycharmProjects/project-sovereign-map/.venv/Scripts/python.exe tools/playtest_driver.py --from-save tests/fixtures/playtest_saves/fixture_t20_ambient.json --script tools/playtest_scripts/diplomacy_latewar.json --llm mock --turns 10 --name probe-combat-latewar --fresh --save-at 5,6,7,8,9 --out <scratch> ; then load saves/probe-combat-latewar_t7.json → world_state.marshals.Massena has pending_interrupt.interrupt_type == 'last_stand', retreating False, strength 8848; the digest's turn…

**Fix shape (one seam).** ONE seam: at the top of `_check_marshal_fate` (combat_executor.py:3208-3215), if `marshal.pending_interrupt` is already a `last_stand` ask, do NOT re-ask — resolve it by the AI rule already written for aggressive marshals (:3346-3374: last stand on home/capital-adjacent ground via `_resolve_last_stand_fight`, else the breakout roll at 0.60-0.10) so a second attack in the same phase ends in capture-with-teeth or a fighting withdrawal, never a standing target. (Optional second half, same function: an ask should only be raised when the player can answer it — i.e. never during the enemy phase; but the deterministic resolution alone closes the grind.)

**Behaviour test.** Extend tests/test_w6_marshal_fates.py: build a player-aggressive marshal with only a tier-5 retreat, force a defeat so the ask is raised (pending_interrupt.interrupt_type == 'last_stand'), then resolve a SECOND defeat against him with the escape roll forced to fail; assert he is captured (captured_by == attacker nation, strength 0, a marshal_captur…

#### FA-2 [P1 · defect] A vassal rebellion is briefed as 'X has ceased to exist' — the real line is fog-filtered by construction, and the campaign log has no rebellion type

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/game_logic/vassal.py:860`
**Already filed:** PC15-17 (adjacent — 'no rebellion narrative existed in the ambient log'; its fix retired stale popups only) · WO-32 (the popup arm, P1 OPEN owner PC15-10) · PC-9 (fixed the article on this exact sentence). NEW here: the fog-rule-reads-the-deleted-row mechanism, the false 'ceased to exist' fact, and…

**What it is.** check_vassal_rebellion deletes the vassal row (vassal.py:860) BEFORE queueing `diplomatic_vassal_rebellion` with fog_rule 'player_vassal' (vassal.py:1005-1007); the fog rule looks the nation up in world.vassals at render time (dispatch.py:4231-4236), finds nothing, and drops the line. What survives is the 'always' event queued at vassal.py:855-856 whose template (dispatch.py:3832) reads '{carved_name} has ceased to exist.' The event is also absent from CAMPAIGN_LOG_TYPES (verified by running), so neither the dispatch nor the log ever says 'rebelled'.

**What the player sees.** The morning after Switzerland turns on France and declares war, the briefing's diplomatic rail says 'Switzerland has ceased to exist.' plus 'Relations with Switzerland have worsened significantly (-50 this turn)' — a live, hostile state announced as dissolved; the campaign log holds no row for the rebellion or its war; only the notification rail carries 'Switzerland REBELLED!'. PC-9 (BUG_FIXES.md:2227) fixed the definite article on exactly this sentence live without noticing the fact was wrong.

**Evidence.** Verified by opening: backend/game_logic/vassal.py:855-860 (`queue_dispatch_event(... 'diplomatic_carved_vassal_dissolved' ... 'always')` then `del world.vassals[vassal_name]`), :1005-1007 (`queue_dispatch_event(world, 'diplomatic_vassal_rebellion', {'nation': vassal_name}, 'player_vassal')`), backend/game_logic/dispatch.py:4231-4236 (`vassal_state = vassals.get(nation) ... return False`), :3832 template. Verified by running: from_scenario(europe_1805) → vassals['Switzerland']['loyalty']=0 → advance_turn() → build_morning_dispatch → diplomatic_events contains {'type':'diplomatic_carved_vassal_d…

**Reproduce.** .venv/Scripts/python.exe -c "import os;os.environ['LLM_MODE']='mock';from backend.models.world_state import WorldState;w=WorldState.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json');w.vassals['Switzerland']['loyalty']=0;w.advance_turn();from backend.game_logic.dispatch import build_morning_dispatch;print([e['text'] for e in build_morning_dispatch(w)['diplomatic_events'] if 'Switzerland' in e['text']], w.get_diplomatic_state('France','Switzerland'))" → ['Switzerland has…

**Fix shape (one seam).** ONE seam: check_vassal_rebellion — queue the rebellion event with fog_rule 'always' (the lord's own satellite breaking away is never fogged), and do NOT queue `diplomatic_carved_vassal_dissolved` on the rebellion path (reserve it for actual dissolution). Add 'vassal_rebellion' (+ 'vassal_rebellion_independent' / 'vassal_rebellion_armistice') to CAMPAIGN_LOG_TYPES with a one-liner and call world.log_event at vassal.py:1002 beside the notification; the 158→159+ log-type pins move consciously.

**Behaviour test.** Drive the REAL path: build the 1805 world, set a French vassal's loyalty to 0, call advance_turn(), then assert build_morning_dispatch(world)['diplomatic_events'] contains a text with 'rebelled' naming the vassal and NO text containing 'ceased to exist'; assert a `vassal_rebellion` row exists in world.event_log for that turn and renders through for…

#### FA-3 [P1 · defect] Accepting the AI's own incoming settlement offer stages a review the AI itself rejects — the coalition-peace route is a dead affordance

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/game_logic/settlement_offers.py:2696`
**Already filed:** EWC-F1 (P2, OPEN, 'a winning-arm settlement offer can stage un-ratifiable' — narrower: indemnity harshness only; this widens it to every offer probed incl. white peace and the losing arm, and adds the offer-destroyed consequence). CA8-3 (✅ Aug 7) fixed the leverage half; its 'scorer charges that whi…

**What it is.** `accept_settlement_offer` re-scores the OFFERING courts as the accepting side of a package France 'proposed' (settlement_offers.py:2696-2716 forwards the terms with `actor_nation=player`, deliberately dropping the offer's `proposer_side`), and the settlement scorer charges a white/status-quo peace a −10 tier base (settlement_scoring.py:466-471, 731-780) plus agenda −8, so no offering court reaches the 50 threshold and the staged `settlement_confirm` arrives with `ratify_blocked_reason` and NO ratify option. Verified by running in four states: fresh 1805 boot at turn 4 (Britain's first offer: Austria −1/50, Britain −4/50, Russia −4/50, top blocker `settlement_tier_legitimacy`), historical seed turn 15 with France ahead (+13 stored; Austria 2/50, Britain 2/50, Russia 'no terms can move them' because Russia had ALREADY made peace at turn 12 yet is still in the turn-3 offer's `covered_enemy_participants`), the late-war fixture turn 23 (Switzerland's own white peace: Switzerland 5/50 'the terms claim a victory the field has not delivered') and turn 24 (Britain's offer while France is at −78: 'cannot be ratified now: the terms claim a victory the field has not delivered'). The producer n…

**What the player sees.** France cannot END the 1805 coalition war by accepting the coalition's own peace — winning or losing. In audit-latewar-t20 France fell 16 → 6 provinces over 10 turns while Britain offered peace twice; a human clicking 'Review Settlement Offer' gets 'cannot be ratified… the terms claim a victory the field has not delivered', the offer vanishes, and the only exits are Back Out / bilateral peace (paradox-blocked for Austria and Britain at boot) / armistice.

**Evidence.** verified by running: scratchpad probe_accept_offer.py (boot+3: `court Austria -1 / 50 reject | top: settlement_tier_legitimacy`; t15: `carry_verdict_display: Will NOT carry as drafted — every court must reach 50. Holding out: Austria 2/50, Britain 2/50, Russia (no terms can move them)`; options `[seek_bilateral_peace, seek_armistice_instead, open_war_detail, back_out_settlement]`, no ratify) and probe_lw2.py (t4: `Sire, a white peace for France vs Switzerland cannot be sealed as it stands: the terms claim a victory the field has not delivered.`; t5: `Sire, the settlement of France vs Austria +…

**Reproduce.** cd repo; INK_IRON_SAVE_DIR=<scratch> LLM_MODE=mock python: TestClient(backend.main.app); POST /new_game {}; POST /command 'end turn' ×3 (Britain's settlement offer becomes current at turn 4); POST /respond_to_diplomatic_dialogue {choice:'accept_settlement_offer', dialogue_id:<current id>} → response.diplomatic_dialogue.type=='settlement_confirm', ratify_blocked_reason=='Settlement legitimacy', every per_court_acceptance row 'reject', no confirm option. Same with tests/fixtures/playtest_saves/fix…

**Fix shape (one seam).** ONE seam: the accept branch of `handle_incoming_settlement_offer_action` (settlement_offers.py:2696-2745). The offering side's consent is given by construction — stage the review with the OFFER's own `proposer_side`/courts marked pre-consenting (or ratify the offered package directly through `settlement_ratify` on the player's confirm), and only pop/remove the offer after staging succeeds. Optionally have `_emit_settlement_offer_for_war` pre-score its package (the EWC-F1 shape) so the AI never offers what its own scorer rejects.

**Behaviour test.** Boot europe_1805.json, `end turn` until an `incoming_settlement_offer` is current (turn 4 on seed historical); accept it and press the staged confirm; assert `world.get_diplomatic_state('France','Britain') in ('PEACE','ARMISTICE')` and war_1 resolved. Second arm: load fixture_t20_ambient, drive 3 turns with --diplomacy accept, accept Britain's offe…

#### FA-4 [P1 · defect] Accepting the settlement offer on screen pops it BEFORE staging, so the next queued offer (another war) trips the cross-war collision and the offer the player clicked is destroyed

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/game_logic/settlement_offers.py:2714`
**Already filed:** none — SC-26 (the collision guard) is design; no BUG_FIXES/DESIGN_REFINEMENT row covers pop-before-stage or the destroyed offer (grep 'cross_war_settlement_collision|SC-26' returned nothing).

**What it is.** The accept branch removes the pending entry and pops the dialogue first (settlement_offers.py:2714-2716), `dialogue_manager.pop()` promotes the next queued item (dialogue_manager.py:347-351, 779-793), and only THEN `stage_settlement_confirm` runs its SC-26 collision check against `_mounted_settlement_dialogue` = the CURRENT dialogue (settlement_staging.py:3388-3405; settlement_routes.py:359-371, whose docstring says queued items must NOT count). With Britain's war_1 offer current and Switzerland's war_2 offer queued, accepting the offer ON SCREEN returns `cross_war_settlement_collision` — 'the settlement of war_2 is already on the table; resolve it before opening a separate review for war_1' — naming an offer the player has never seen, and Britain's offer is gone (current becomes Switzerland's). The archived late-war digest shows exactly this at T23, and the raw war ids leak into the sentence.

**What the player sees.** A losing France (13 provinces, Paget walking the homeland) clicks Review on the coalition leader's peace offer and is told a different, invisible war is 'on the table'; the offer disappears; the collision copy prints `war_2`/`war_1`. Peace with the court that is actually beating France cannot be accepted until the unrelated rebel war's offer is dealt with — and that one is itself un-ratifiable (FA-3).

**Evidence.** verified by running: scratchpad probe_slot_and_collision.py part B — load probe-latewar-dip_t3 (turn 22), end turn → `CURRENT=incoming_settlement_offer#8 war=war_1 from=Britain | queue=[('incoming_settlement_offer', 29, 'Switzerland'), …]`; accept #8 → `False | Sire, the settlement of war_2 is already on the table; resolve it before opening a separate review for war_1. | error: cross_war_settlement_collision`; afterwards `CURRENT=incoming_settlement_offer#29 war=war_2` and #8 absent. verified by opening: backend/game_logic/settlement_offers.py:2714-2716; backend/game_logic/settlement_staging.p…

**Reproduce.** python tools/playtest_driver.py --from-save tests/fixtures/playtest_saves/fixture_t20_ambient.json --script tools/playtest_scripts/diplomacy_latewar.json --turns 4 --diplomacy accept --save-at 3 --name x --fresh; then TestClient: POST /load {filename:'x_t3.json'}; POST /command 'end turn'; accept the CURRENT settlement offer by its dialogue_id → error `cross_war_settlement_collision`, and `world.dialogue_manager.peek()` no longer holds it.

**Fix shape (one seam).** ONE seam: reorder the accept branch — run `stage_settlement_confirm` first (or evaluate the collision against the offer's own war before touching the queue) and pop/remove the offer only when staging succeeds; on any refusal leave the offer current. Also humanize the two `{war_label}` slots in `settlement_collision_active_review_talleyrand` via `_war_label_for_id` (diplomatic_templates.py:1755-1758; settlement_staging.py:173-177 passes raw ids).

**Behaviour test.** Build a world with two `incoming_settlement_offer` dialogues (war_1 current, war_2 queued); call `handle_incoming_settlement_offer_action(action='accept_settlement_offer', dialogue=current)`; assert no `cross_war_settlement_collision`, a `settlement_confirm` for war_1 is staged, and if staging is refused for any reason the war_1 offer is still `dia…

#### FA-5 [P1 · defect] An end-turn-only stretch never delivers the marshal petition, and the undelivered card starves Fontainebleau and every later petition

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published AUTHOR_VERIFIED) · **Seam:** `backend/main.py:1355`
**Already filed:** PC15-10 / docs/PETITION_POPUP_REVISIT_SPEC.md §1.2 ('1 petition served of 32 produced, the single slot permanently occupied') and F1 'The Antechamber' (B1–B5 unbuilt). NEW: the enemy_phase deferral + absent client poll is the delivery mechanism on a FRESH boot (the spec's S9/N4b row covers only the…

**What it is.** `_apply_command_popup_contract` (main.py:1353-1361) calls `_include_popup_passthroughs` only when the response has NO `enemy_phase`, so the end-turn response never carries `marshal_petition`; the card waits for the player's next non-end-turn `/command`. The client's post-enemy-phase tail (`_on_enemy_phase_dismissed` main.gd:4340-4392 → `_return_control_to_player` main.gd:2261-2280) polls only `GET /pending_redemption` (main.py:3625-3626) — there is no `/pending_petition` poll and no GET route delivers `pending_marshal_petition` (`_fill_popup_keys_without_draining`, main.py:1509, sets the key to None). While the card sits, `_push_petition` returns BLOCKED for any OTHER petition (jealousy.py:1861-1862) and `check_fontainebleau` returns without stamping (jealousy.py:2269) — so the collective petition is unreachable for as long as the player only presses End Turn. Verified by running the in-process probe: `pending_marshal_petition=jealousy_confrontation` from world turn 5 through turn 24, `jealousy_confrontations_seen` frozen at ['Murat|Ney@L0'], every end-turn response `popups: []`; five marshals eroding from turn 10 (≥ `FONTAINEBLEAU_MIN_ERODING`=3, jealousy.py:114) yet `fontaineblea…

**What the player sees.** Press End Turn through three quiet turns waiting for a march and the marshal who 'seeks an audience' is never seen; type the next order and a card arrives about a quarrel that may already be over (the A3 guard then answers 'The moment has passed', jealousy.py:2688). The Fontainebleau collective petition — the one beat that turns five bitter marshals into a scene — cannot fire at all during such a stretch.

**Evidence.** main.py:1355-1361 (`if not response.get('enemy_phase'): … _include_popup_passthroughs(response, world); return`); jealousy.py:1861-1862 (`if pending is not None and pending is not petition: return PETITION_BLOCKED`); jealousy.py:3175 (per-turn re-push of the same object); jealousy.py:2269 (`if status != PETITION_QUEUED: return`); main.gd:2276-2278 (`_show_pending_redemption` / `_maybe_recover_dropped_redemption` only). Probe logs scratchpad/probe_endturn24.log and probe_status14.log.

**Reproduce.** TestClient as in FA-75; loop `end turn` 8×; after turn 5 `mm.world.pending_marshal_petition` is a dict and no response contained a `marshal_petition` key; then POST `/command` `{'command':'status'}` — that response carries it. Archive check: `grep -c POPUP docs/audits/playtest_digests/audit-ambient40/digest.md` → 0.

**Fix shape (one seam).** ONE seam: in `_apply_command_popup_contract` (main.py:1353) treat `marshal_petition` like `redemption_event` — when `enemy_phase` is present, attach `refresh_petition_affordability(world.pending_marshal_petition, world)` (jealousy.py:1870) to the response and let the client stash-and-raise it at `_return_control_to_player` (mirror of `pending_redemption_data`, main.gd:222/2276). (The tier split F1 'The Antechamber' in PETITION_POPUP_REVISIT_SPEC.md fixes the starvation of the OTHER petitions; this delivery hole exists independently of it and is one line on the backend plus one stash on the client.)

**Behaviour test.** tests/test_petition_delivered_on_end_turn.py: TestClient boot, queue a confrontation (`jealousy.queue_confrontation_petition`), POST `end turn` → assert the response's `marshal_petition` is not None while `enemy_phase` is present; second pin: with a standing unanswered confrontation and ≥3 eroding marshals, after the fix (or under F1) `check_fontai…

**Author note.** HV-2 end-turn-only player starves the popup queue

#### FA-6 [P2 · defect] A sentence containing "next turn" advances the turn irreversibly — including a QUESTION ("what happens next turn")

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published AUTHOR_VERIFIED (amended 2026-09-02)) · **Seam:** `backend/ai/llm_client.py:1411`

**What it is.** The mock chain's end_turn arm is a bare substring test that sits above every order verb: llm_client.py:1411 `elif "end turn" in command_lower or "end_turn" in command_lower or "next turn" in command_lower: action = "end_turn"` (verified by opening). A qualifier on an order ("…next turn", "…and end turn") therefore becomes the end-turn command itself, and meta_executor.py:164-167 only WARNS about unused AP ("PT-6: Warn about unused AP (informational — turn still ends)", verified by opening). Mock is the shipped EA default, so no LLM ever sees these.

**What the player sees.** Verified by running on the 1805 boot via POST /command: `Davout, attack next turn` → "Turn 1 ended. (Warning: 4 action(s) unused) Turn 2 begins!", world.current_turn 2, enemy phase ran, Davout never moved. Same for `recruit next turn`, `next turn Ney attacks Mack`, `Ney, scout Swabia and next turn attack`, and `Ney attack Mack and end turn` (the attack is LOST and the turn ends). The player loses a whole turn of orders silently and cannot undo the enemy phase. BUG_FIXES.md:268 (REV row) only adds the envoy-lapse warning for bare "next turn" — with no envoy waiting, nothing intercepts.

**Evidence.** verified by opening backend/ai/llm_client.py:1411 (end_turn arm), :1442 (attack arm below it), backend/commands/meta_executor.py:164-167 (warn-only); verified by running probe POST /command on WorldState default 1805 boot (turn 1→2, actions_remaining 4 unused, response keys ['enemy_phase','turn_ended']).

**Reproduce.** LLM_MODE=mock; POST /command {"command":"Davout, attack next turn"} on a fresh /new_game → response turn_ended=true, world.current_turn==2, actions_remaining==4 (unused). Also `Ney attack Mack and end turn`, `recruit next turn`.

**Fix shape (one seam).** ONE seam, llm_client.py:1411: gate the end_turn arm on the BARE form — `command_lower.strip() in {"end turn","end the turn","next turn","end_turn"}` (or a fullmatch allowing trailing punctuation) — and let any sentence carrying a marshal name or another order verb fall through the chain; a trailing "next turn"/"later" qualifier then reaches the clause_guards contingency refusal instead of advancing the turn.

**Behaviour test.** tests: for each of `Davout, attack next turn`, `recruit next turn`, `Ney attack Mack and end turn`, `next turn Ney attacks Mack`: after POST /command, world.current_turn unchanged, actions_remaining unchanged, no `turn_ended` key, and the message names no turn advance; bare `next turn` and `end turn` still advance (keep the existing REV pin).

**Author note.** HV-15 'next turn' anywhere ends the turn (mock AND live)

> **⚠ AMENDED September 2, 2026, and DOWNGRADED P1 → P2 — the owner challenged
> the framing and was right.** Two things in the original write-up were wrong.
> (1) **"Forfeits all 4 AP" implies a resource is stolen. It is not.**
> `actions_remaining` is reset to `calculate_max_actions()` at every turn start
> (`world_state.py:9608`) — action points never carry over — so ending a turn
> with four unused is exactly what pressing End Turn does. There is no banking
> and no cheat vector, and the fix must NOT be "queue the attack for next turn":
> a deferred-order system does not exist, and inventing one here would hand the
> player free actions. (2) **"Davout, attack next turn" is not a sentence a real
> player types**, so it is a poor headline case. The end_turn substring arm is
> also *deliberate synonym handling*, not an oversight — the client's own gate
> was widened on Aug 30, 2026 to mirror it (`main.gd:1292-1302`, comment: "a
> client-side gate on a server-side vocabulary has to speak that vocabulary").
>
> **What survives, re-measured September 2, 2026 on the 1805 boot via
> POST /command, and it is still a real defect:** a sentence that is not a
> command at all advances the turn and runs the enemy phase, with no
> confirmation unless envoys happen to be lapsing.
>
> | typed | result |
> |---|---|
> | `what happens next turn` | **turn 1 → 2, enemy phase ran** |
> | `we will decide next turn` | **turn 1 → 2, enemy phase ran** |
> | `Ney, hold here and attack next turn` | **turn 1 → 2, enemy phase ran** |
> | `Davout, attack next turn` | **turn 1 → 2, enemy phase ran** |
> | `what should we do next turn?` | help screen (turn held) |
> | `can Davout attack next turn?` | help screen (turn held) |
>
> The last two rows are the reason this is worth fixing rather than shrugging
> at: **the behaviour is inconsistent**, so it cannot be learned. A question
> ending in a question mark is safe; the same question without one ends your
> turn. And the loss is irreversible without a reload — the enemy phase resolves
> battles and can take provinces.
>
> **The fix shape is unchanged and still one seam** (bare-form match at
> `llm_client.py:1411`, mirrored at `main.gd:1292`), but the *right* fallthrough
> for an order-shaped sentence is the existing clarification or refusal, never a
> deferred order.


#### FA-7 [P1 · defect] Deferral orders launch the attack NOW — "Ney, delay the attack" / "attack Mack later" / "wait for Davout then attack Mack" all fight a battle immediately

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published AUTHOR_VERIFIED) · **Seam:** `backend/ai/clause_guards.py:77`
**Already filed:** PARSE-NEG (COMMAND_ROBUSTNESS_SPEC.md §8 / BUG_FIXES §PARSE-NEG) is the family — the deferral class is not covered by any row

**What it is.** PARSE-NEG's negation guard (clause_guards.py:77-104 `_NEGATION_MARKER_RE`, verified by opening) knows never/do not/refrain/rather than/instead of/without/avoid but no deferral verb (delay, postpone, defer, put off, hold off) or deferral adverb (later, for now); `_REFUSING_CONDITION_WORDS` (:148) has if/when/once/after but not later/next turn. So "delay the attack" survives to the chain, where `attack` (llm_client.py:1442) outranks `wait` (:1475). For "wait for Davout then attack Mack", parser.py:53-66 `_ATTACK_ON_ARRIVAL_TAIL_RE` deliberately refuses to split a tail that starts with attack, so the whole sentence is one parse and attack wins. With no named foe, the guessed-target arm (combat_executor.py:172-200, `auto_resolved=True`) PROCEEDS with a disclosure rather than refusing.

**What the player sees.** Verified by running: `Ney, delay the attack` → "Your words named no foe our maps know, Sire — Ney marches on Mack at Swabia, the nearest in sight…" + MUSTER + battle_report; Ney moved Rhineland→Swabia, 24,000→22,831, Mack 52,000→37,978 — a real battle the player explicitly said NOT to fight yet. `Ney, postpone the attack` identical; `Ney, attack Mack later` → battle (Ney 22,891, Mack 36,747); `Ney, wait for Davout then attack Mack` → battle now without Davout; `Ney, hold off on attacking Mack` → parse action attack + strategic HOLD with target "Off On Attacking Mack" → an objection popup. The…

**Evidence.** verified by opening backend/ai/clause_guards.py:77-104 and :148-160, backend/commands/parser.py:45-66, backend/ai/llm_client.py:1442 and :1475, backend/commands/combat_executor.py:172-200; verified by running POST /command on the 1805 boot (battle_report present, marshal positions/strengths read from world).

**Reproduce.** POST /command {"command":"Ney, delay the attack"} on a fresh 1805 /new_game → success true, battle_report present, world.get_marshal('Ney').location=='Swabia'. Also `Ney, attack Mack later`, `Ney, wait for Davout then attack Mack`.

**Fix shape (one seam).** ONE seam, clause_guards.py `_NEGATION_MARKER_RE`: add a DEFERRAL arm — `delay(?:s|ed|ing)?|postpone|defer|put\s+off|hold\s+off(?:\s+on)?` blanking the clause like a negation, plus a trailing-adverb refusing condition (`\b(?:later|for now|next turn|tomorrow)\s*[.!]?$`) so the caller emits the existing contingency refusal ("that is a contingency, not an order"). For "wait for X then <attack>", exempt `_ATTACK_ON_ARRIVAL_TAIL_RE` when the first clause's verb is wait/hold, so it becomes the pinned HOLD-until-arrival shape.

**Behaviour test.** for `Ney, delay the attack`, `Ney, postpone the attack`, `Ney, attack Mack later`, `Ney, hold off on attacking Mack`: parse success False with a refusal (no battle_report, Ney at Rhineland at 24,000, AP unchanged); `Ney, wait for Davout then attack Mack` → strategic HOLD with until_marshal_arrives=Davout, no battle this turn; existing pins `Ney, wa…

**Author note.** HV-15 deferral orders launch now (mock AND live)

#### FA-8 [P1 · defect] P4.25 garrison assault prices the garrison and ignores the field army standing in the province (the Munich suicide loop)

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/ai/enemy_ai.py:3521`
**Already filed:** WO-3 (P4.25 has no futility guard — consciously not built at the seam) and CA9-N6 (field pricing landed on P0/P4 only); CA8-19 owns the garrison RESOLVER's parity. The decision rung's blindness to the field army is unfiled.

**What it is.** `_find_garrison_attack` (backend/ai/enemy_ai.py:3502-3571) scans adjacent garrisoned provinces and gates the assault on `marshal.strength / garrison_effective` (line 3558, garrison x terrain x fort) — it checks garrison size, controller, war state, the crossing gate and terrain, but NEVER whether enemy marshals stand in the target region. Its siblings do: P4.5 skips a defended province at :3447 and P3.7 checks `defenders` before the garrison arm at :3175. The executor then resolves the 'garrison assault' as a field battle against whoever is in the region (combat_executor.py:4818 `get_enemy_at_location_for_nation(resolved_target)`), so a cautious 29k corps that computed 2.32:1 against a 10k garrison walks into 53k Frenchmen at 0.5:1. The futility brake does not guard P4.25 (WO-3 records it was consciously not built) and the CA9-N6 field-pricing fix landed on P0/P4 only, so the same marshal repeats the assault every recovery cycle. The sibling seam in P7.5's stagnation arms (:3842-3876, ratio against ONE marshal, no futility, no crossing gate) carries the same defender-blindness and should be swept in the same slice.

**What the player sees.** In every ambient/naval/propose campaign Austria's three field corps destroy themselves against the French stack at Munich every other turn: the digest census (verified by grep over the nine digests) finds 48 enemy attacks where the AI attacker lost >=1,000 men and the French defender <1,000 — ambient-ulm t14 9,360 vs 79, t19 4,599 vs 74 and 8,675 vs 80, t21 9,143 vs 45, t23 7,433 vs 48; ambient40 t4 Mack 9,513 vs 97; ambient-austerlitz t10 Mack 11,282 vs 245, t13 11,290 vs 122. The coalition collapses without the player lifting a finger, and the French marshals farm glory, crowns, estates and…

**Evidence.** Verified by running: an in-process re-run of Austria's enemy phase from a seed-ulm turn-14 snapshot (`tools/playtest_driver.py --turns 14 --seed ulm --save-at 13,14 --name probe-enemyai-ulm-save --fresh`, then `EnemyAI(CommandExecutor()).process_nation_turn('Austria', w, {'world': w})` on `saves/probe-enemyai-ulm-save_t14.json`) printed `[GARRISON ASSAULT] ArchdukeCharles attacking garrison at Munich (ratio 2.32 >= 1.33)` while Munich held Ney 15,503 + Lannes 10,354 + Bernadotte 6,863 + Massena 20,825 (53,545 French) plus its 10,000 garrison; the archived digest's line for that same phase is `…

**Reproduce.** From the repo root: `.venv/Scripts/python.exe -c "from backend.models.world_state import WorldState as W; from backend.ai.enemy_ai import EnemyAI; from backend.commands.executor import CommandExecutor as C; w=W.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json'); [setattr(w.marshals[n],'location','Munich') for n in ('Ney','Lannes','Bernadotte','Massena')]; [setattr(w.marshals[n],'location','Paris') for n in ('Davout','Soult','Murat','Napoleon')]; [setattr(w.marshals[n],'…

**Fix shape (one seam).** ONE seam: in `_find_garrison_attack`'s candidate loop (enemy_ai.py:3521, before the ratio at :3558) add the gate its siblings already carry — `if world.get_live_visible_enemies_in_region(adj_name, nation): continue` — so a garrisoned province with a field army in it is P4's business (which prices the whole field since CA9-N6). Expect `BASELINE_SERIES` to move (conscious one-time re-record with the flip-lever attribution idiom) and re-verify the tutorial's authored Munich beats (audit-tutorial t3/t5 Schwarzenberg breaking on Ney) still fire through P4. Sweep the two P7.5 arms at :3842-3876 onto `_defending_strength_in_region` in the same slice.

**Behaviour test.** `tests/test_ai_garrison.py`: (1) boot 1805, Charles 29k at Franconia, Munich garrison 10,000 and one hostile 15k marshal in Munich → `_find_garrison_attack(charles, 'Austria', w) is None`; (2) positive control, Munich empty of marshals → returns `{'action':'attack','target':'Munich'}`; (3) mutation: delete the new gate → (1) fails. Plus a driver pi…

#### FA-9 [P1 · defect] The School of War, played exactly as Berthier counsels, loses six French homeland provinces by turn 10 to a 1,218-man retreating remnant

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/commands/movement_executor.py:588`
**Already filed:** CA8-14 (FIXED — covers only the same-phase P-1 rung via `retreated_this_turn`; this is the next-phase recovery window and the walk-in seam); PC15-D1 (ruled: the retreat scan obeys the movement law, which is exactly why tier 5 sends him into France); PT-D4 (LANDED — presentation-only collapse of the…

**What it is.** Under the card's own INSIST counsel (tutorial_overlay.gd:93), Ney beats Kienmayer at Swabia on T3 (8,000 -> 1,218, retreating=True, morale 20). The W6-1 retreat doctrine's tier 5 sends the beaten corps INTO French war soil (world_state.py:4368 `at_war_soil.append`, :4433 "DESPERATION into at-war soil") because the lesson's own beats (Senarmont to Munich T1, Davout reinforcing at Swabia) empty Lorraine/Rhineland/Franche-Comte of marshals. From Franche-Comte the still-retreating corps (t4 save: retreating=True, retreat_recovery=1/3) MOVES into ungarrisoned Lorraine and captures it (movement_executor.py:588-596 — the walk-in capture predicate checks controller/war/enemies/fortification/garrison>=5000 and never `retreating`, `broken` or a strength floor; `move` is on the executor's allowed-during-retreat list, executor.py:1490). Recovered, it takes Rhineland T8 and Orleanais+Flanders+Picardy+Artois in ONE enemy phase T10 (Austria's world.nation_actions = 4, verified by running, all spent on one corps; `_find_undefended_capture` enemy_ai.py:3388-3394 guards only drilling/fortified). The tutorial's own premise and pin — "a beaten Kienmayer breaks in place or dies" (tests/test_tutorial_sc…

**What the player sees.** A first-time player following the lesson step by step watches 'Lorraine has fallen. Enemy colours fly over French homeland soil' on turn 4, then Rhineland on turn 8, then four provinces in one enemy phase on turn 10 (provinces 28 -> 22), while step XI's suggest chip `build watchtower in Lorraine` (tutorial_overlay.gd:151) is refused 'not controlled by France' and step XIII tells him to fortify at Munich. The README's 'FIRST TIME? take the School of War' (deploy/README_TESTER.txt:53) leads straight here.

**Evidence.** Verified by running: `tools/playtest_driver.py --script tools/playtest_scripts/tutorial_lesson.json --scenario tutorial --turns 10 --name probe-onboarding-insist --fresh --objection insist` -> digest T3 'Kienmayer has crossed into Franche-Comte', T4 'Kienmayer moves from Franche-Comte to Lorraine. Lorraine falls to Austria!', T7 'Cannot build in Lorraine — not controlled by France', T8 'Rhineland has fallen', T10 four 'marches ... unopposed! Captured: France -> Austria' rows, provinces 27->26->22. Snapshots (`--save-at 3,4`): t3 Kienmayer location Franche-Comte strength 1218 retreating True re…

**Reproduce.** From C:/Users/User/PycharmProjects/project-sovereign-map: `.venv/Scripts/python.exe tools/playtest_driver.py --script tools/playtest_scripts/tutorial_lesson.json --scenario tutorial --turns 10 --name probe-x --fresh --objection insist --save-at 3,4`; read tools/playtest_runs/probe-x/digest.md turns 4/8/10 and the t4 save's marshals.Kienmayer.retreating. Deterministic sibling: `WorldState.from_scenario(tutorial_1805.json)`, set Senarmont.location='Munich', Davout.location='Swabia', Ney.location='…

**Fix shape (one seam).** ONE seam, GR5 both sides: the shared capture predicate that both the PF-3 move-capture (movement_executor.py:588-596) and `_attempt_region_capture` consult refuses a walk-in capture by a corps that is `retreating`/`broken` or under the existing 1,000-man 'army' threshold (the EC-W1 Contributions floor), leaving the march itself legal (the CA8-14 idiom extended from `retreated_this_turn` to the whole recovery). Authoring alternative if the rule is ruled design: garrison Lorraine and Rhineland in tutorial_1805.json `region_overrides` like Franche-Comte, and retire the 'breaks in place or dies' premise from the pin.

**Behaviour test.** tests/test_tutorial_scenario.py: boot the tutorial, place Kienmayer at Franche-Comte with strength 1218, retreating=True, retreat_recovery=1; run `TurnManager.end_turn` once; assert regions['Lorraine'].controller == 'France' and Kienmayer captured nothing. Mirror: a player marshal in the same state ordered `move to <undefended Austrian province>` d…

### 3b. Defects — P2 (25)

#### FA-11 [P2 · defect] "blockade" anywhere in a sentence sets the FLEET to blockade — "Ney, blockade Vienna", "lift the blockade" and "raise the blockade" all put the navy to sea for 1 AP

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published AUTHOR_VERIFIED) · **Seam:** `backend/commands/naval_executor.py:95`

**What it is.** llm_client.py:1564 `elif (re.search(r'\bblockade\b', command_lower) …): action = "set_fleet_posture"` claims the word regardless of an addressed marshal or an inland target, and naval_executor.py:91-99 derives the posture from the raw text with `if "blockade" in raw … posture = "blockade"` — no negation, no lift/raise verb, no check that the target is a sea or a nation (verified by opening). France boots at posture 'guard' (verified by running `world.fleets['France']['posture']`).

**What the player sees.** Verified by running: `Ney, blockade Vienna` (an inland Austrian city — a siege phrasing), `Davout, blockade the city`, `Ney, blockade Mack`, `Ney, besiege and blockade Vienna`, `blockade Britain`, and — the inverted ones — `lift the blockade`, `raise the blockade` ALL → "The fleet stands out to sea on blockade. Austria and Russia are closed — their ports watched and their trade halved…", fleet posture guard→blockade, AP 4→3. A player trying to invest Vienna, or trying to STAND DOWN a blockade, changes the naval posture the opposite way and pays for it; the message never mentions the marshal or…

**Evidence.** verified by opening backend/ai/llm_client.py:1564-1566 and backend/commands/naval_executor.py:78-125; verified by running seven /command probes on the 1805 boot (posture read from world.fleets before/after, actions_remaining 4→3).

**Reproduce.** fresh 1805 /new_game (France posture 'guard'); POST /command {"command":"lift the blockade"} → world.fleets['France']['posture']=='blockade', AP 3. Also {"command":"Ney, blockade Vienna"}.

**Fix shape (one seam).** ONE seam, `_execute_set_fleet_posture` raw-text arm (naval_executor.py:91-99): read lift/raise/end/stand down + blockade as posture 'guard'; refuse with the existing "Give the Admiralty a posture" line when the command carries a marshal or a target that is a province/marshal rather than a nation or 'the enemy' (a land siege is not a naval order). Optionally also gate the llm_client.py:1564 arm on no addressed player marshal.

**Behaviour test.** `lift the blockade` from posture blockade → guard; from guard → no-op refusal, AP unchanged; `Ney, blockade Vienna`, `Davout, blockade the city`, `Ney, blockade Mack` → success False, posture and AP unchanged; `blockade the enemy` and `blockade Britain` still → blockade (existing naval tests green).

**Author note.** HV-15 'blockade' in any sentence sets fleet posture

#### FA-12 [P2 · defect] 'N turns now with enemy colours on French soil' resets to 3 whenever the leading province changes — the briefing lies about how long France has been invaded

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published AUTHOR_VERIFIED) · **Seam:** `backend/game_logic/dispatch.py:919`
**Already filed:** none — PC-7 (FIXED) and CA9-N9/N47 (FIXED) fixed verbatim repetition and made the ladder fire; the identity-keyed reset is new.

**What it is.** The standing candidate is keyed per PROVINCE: `_add("enemy_on_our_soil", identity=f"enemy_on_our_soil:{region_name}", ...)` (dispatch.py:919) with `break` after the first intel region that qualifies (:922), and `_select_headline` rebuilds `runs` only from identities PRESENT this turn (:1149) — so when the first-in-dict province is captured (controller != player → skipped) or another province leads the iteration, the run restarts at 1, the base template 'X has crossed into Y' re-fires as fresh news, and the escalation ladder (`_STANDING_ESCALATION["enemy_on_our_soil"]`, :238-241) counts from 3 again. Reproduced on the legacy world: T3 '3 turns now with enemy colours on French soil', T4 'Wellington has crossed into Belgium. Ney stands in his path.' (province A captured, enemy still on B), T6 '3 turns now…' again — the enemy never left. Digest: ambient40 turn 28 'the enemy has stood on our ground 11 turns' (:271) → turn 34 'Paget has crossed into Flanders. No French corps stands in his path.' (:331 — byte-identical to turn 18, :186) → turn 36 '3 turns now with enemy colours on French soil' (:345) → turn 37 '4 turns' (:350), while France lost a homeland province on every one of turns 2…

**What the player sees.** After eighteen consecutive turns of enemy armies on French soil the briefing announces a sixteen-turn-old crossing as this morning's news and tells the Emperor it has been three turns. The sentence claims a France-wide fact ('enemy colours on French soil') from a per-province counter.

**Evidence.** verified by opening backend/game_logic/dispatch.py:238-241, :896-922, :1149; verified by running the 7-turn repro (output T3 '3 turns now', T4 base template, T6 '3 turns now'). Digest: docs/audits/playtest_digests/audit-ambient40/digest.md:186,271,331,345,350 verbatim.

**Reproduce.** C:/Users/User/PycharmProjects/project-sovereign-map/.venv/Scripts/python.exe -c "import os;os.environ.pop('SOVEREIGN_SCENARIO',None);from backend.models.world_state import WorldState;from backend.game_logic.dispatch import _build_headline;from backend.models.intel import PARTIAL;w=WorldState();p=w.player_nation;e=[n for n in w.enemy_nations if w.is_at_war(p,n)][0];em=next(m for m in w.marshals.values() if m.nation==e);A,B=[r for r in w.intel if w.regions[r].controller==p][:2] for t in range(1,8)…

**Fix shape (one seam).** ONE seam — dispatch.py:919: key the standing identity on the CLASS (`identity="enemy_on_our_soil"`, keep `region`/`enemy` in `fields`) so the run counts turns-with-any-enemy-on-home-soil; or derive `turns` from a `first_turn` read off `headline_lead_memory['runs']` rather than the per-identity counter. Either way the base template must never re-fire while the run is open.

**Behaviour test.** tests/test_dispatch_headline.py::test_enemy_on_our_soil_run_survives_a_province_switch — enemy stands on A for 3 turns, A falls, enemy stands on B: turn 4 renders the escalation variant with `turns == 4`, never the base 'has crossed into' template; and a turn with NO enemy on home soil resets the run.

**Author note.** HV-16/20 enemy-colours streak keyed on the leading region

#### FA-13 [P2 · defect] 'march to X' plots its route without the movement law when a legal corridor exists — wrong route announced, first hop refused silently, and the PF-8 reroute costs a second turn

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/commands/strategic_executor.py:837`
**Already filed:** PF-8 (stall feedback) and S5-D2 (issuance-time no-corridor refusal) are landed and cover the neighbours; the corridor-exists issuance seam and the no-step reroute are unfiled.

**What it is.** At issuance `_execute_strategic_command` computes `path = pathfinder(marshal.location, dest)` with no `passable_for` (backend/commands/strategic_executor.py:837; the cautious branch :822-835 likewise). The S5-D2 block (:846-881) then calls `pathfinder(..., passable_for=marshal.nation)` only as a boolean 'does a corridor exist' and discards it — so when a legal corridor exists the order is accepted, 2 AP charged, the ILLEGAL route printed, the first hop refused by the diplomatic movement law (movement_executor.py:197-230) with the reason dropped at :1306 ('Move FAILED' print only). At the next end turn the PF-8 stall arm (strategic.py:1088-1108) reroutes but returns `order_status: continues` WITHOUT executing a step (:1098-1108). The typed verb decides the outcome: 'move to X' (auto-upgrade, movement_executor.py:384-387) routes with `passable_for` and marches correctly.

**What the player sees.** Ney at Flanders, 'march to London' (turn 6 of the archived naval run): 'Route: Flanders -> Westphalia -> Artois -> Normandy -> London' — Westphalia is Hanover soil at PEACE (impassable) — no 'Moves to' clause, 2 AP gone, Ney does not move; next end turn 'Ney reroutes around Hanover territory toward London.' and STILL does not move; he first steps on turn 3 of a 4-hop march that 'move to London' would have started immediately via Picardy. Archived: audit-naval digest line 80 (`Ney begins march to London. Route: Flanders -> Westphalia -> Artois -> Normandy -> London.` with no Moves-to) and line…

**Evidence.** Verified by running: `w._region_passable_for('Westphalia','France',mover_location='Flanders') == False`, `w.get_diplomatic_state('France','Hanover') == 'PEACE'`, `find_weighted_path('Flanders','London')` = via Westphalia, `find_weighted_path(..., passable_for='France')` = ['Flanders','Picardy','Artois','Normandy','London']; probe_strategic.py B: `variable_action_cost: 2`, message with the Westphalia route, `location: Flanders`, then `END-TURN REPORT: continues | Ney reroutes around Hanover territory toward London.` with `location after: Flanders`. Verified by opening strategic_executor.py:837/…

**Reproduce.** Boot 1805; `ney=w.get_marshal('Ney'); ney.location='Flanders'; w.calculate_visibility()`; parse+execute 'Ney, march to London' → assert `ney.strategic_order.path[0]=='Westphalia'` and `ney.location=='Flanders'` and 2 AP spent; set `issued_turn = current_turn-1`, run `process_strategic_orders` → report 'reroutes around Hanover territory' and `ney.location` still 'Flanders'.

**Fix shape (one seam).** ONE seam: at strategic_executor.py:837 (and the cautious fallback :835) compute the player's path with `passable_for=marshal.nation` first and fall back to the raw terrain path only when none exists (so the S5-D2 refusal at :862-881 still fires on 'no corridor'). Companion one-liner: the reroute arm at strategic.py:1098 should call `self._execute_movement_step` after setting `order.path` so the reroute turn is not lost (the go_around handler at :670-690 already does exactly this).

**Behaviour test.** tests: Ney at Flanders, 'march to London' → `order.path == ['Picardy','Artois','Normandy','London']`, `ney.location == 'Picardy'` after issuance, message names Picardy; and a marshal whose stored path crosses closed soil gets rerouted AND moved one province in the same `process_strategic_orders` tick.

#### FA-14 [P2 · defect] A REFUSED strategic auto-attack is narrated as an inconclusive battle and raises a combat_stalemate interrupt

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/commands/strategic.py:2940`
**Already filed:** WO-28 (FIXED, WO slice 17) is the same class — a refused attack narrated as fought — at the jealousy producer only; WO-33 (FIXED) touched this exact function but only to carry `battle_report`. This seam is unfiled.

**What it is.** `StrategicOrderProcessor._handle_combat_result` (backend/commands/strategic.py:2860-2965) derives the outcome only from `result["events"]`/`result["battle_result"]` and never reads `result["success"]` (outcome defaults to "unknown" at :2886 → the `else: # stalemate / unknown` arm at :2940). When the aggressive destination-blocked arm (:2670-2700, ratio 0.8 ≥ 0.7) auto-attacks via `_strategic_execution` and the executor REFUSES the attack (here the naval crossing gate, naval.py:1025-1036), the refusal dict is treated as a stalemate: `combat_attempts` becomes 1 (so the next try is suppressed by `_should_auto_attack` :2966-2982), a `combat_stalemate` interrupt is armed, and the player reads "Ney attacked Moore during march but the battle was inconclusive. Continue move to?" — no battle was fought, nobody lost a man. Verified by running (Ney 24,000 at Normandy with MOVE_TO London, Moore 30,000 at London, RN covering): report interrupt_type=combat_stalemate, `battle_details.success == False` carrying the crossing refusal text, 0 rows in `world.battles_this_turn`, strengths unchanged, `order.combat_attempts == 1`. The `Continue move to?` tail is the raw `order.command_type.replace('_','…

**What the player sees.** Any 'march to London' (the most natural naval order in the game) ends in a phantom battle report and a popup asking whether to continue a fight that never happened; the honest naval refusal (which the direct 'move to London' shows) is buried inside `battle_details` where no client surface renders it. Archived: docs/audits/playtest_digests/audit-naval/digest.md line 159 (turn 11): `POPUP strategic_interrupt: Ney, combat_stalemate, Ney attacked Moore during march but the battle was inconclusive. Continue move to? → continue_order`, after line 199-200 (turn 14) the same order re-asked as contact_…

**Evidence.** Verified by opening strategic.py:2860-2965 (no `success` read; :2886 default "unknown"; :2940 stalemate arm; :2961 copy) and :2670-2700 (aggressive auto-attack at the destination); verified by running the scratchpad probe (probe_strategic2.py E2) — output: `REPORT status: None | interrupt: combat_stalemate | msg: Ney attacked Moore during march but the battle was inconclusive. Continue move to?` / `battle_details.success: False | battle_details.message: The crossing from Normandy to London is barred — the Royal Navy commands the water with 100 sail…` / `battles recorded: 0 | Ney 24000 -> 24000…

**Reproduce.** Boot `WorldState.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json')`; `ney=w.get_marshal('Ney'); ney.location='Normandy'; w.calculate_visibility()`; `ney.strategic_order = StrategicOrder(command_type='MOVE_TO', target='London', target_type='region', started_turn=0, issued_turn=0, path=['London'])`; `StrategicOrderProcessor(CommandExecutor()).process_strategic_orders(w, {'world': w})` → the report carries interrupt_type 'combat_stalemate' and `len(w.battles_this_turn)==0…

**Fix shape (one seam).** ONE seam: at the top of `_handle_combat_result` (strategic.py:2860) branch on `not result.get("success")` — do not touch `combat_attempts`, do not arm an interrupt; break the order with the executor's refusal message using the PF-8/naval idiom already at :1118-1125 (`_break_order(marshal, world, f"{marshal.name}'s march halts — {result['message']}")`), and carry the refusal keys (`blocked_naval`/`blocked_diplomatic`) on the report. While there, humanize the `Continue {command_type}?` tail at :2961 via `get_strategic_display`.

**Behaviour test.** tests: aggressive marshal at Normandy, MOVE_TO London, enemy marshal in London, `world.fleets` covering the Channel → after `process_strategic_orders`: no `combat_stalemate` in any report, `marshal.pending_interrupt is None`, `len(world.battles_this_turn)==0`, the report's `order_status=='breaks'` and its message contains 'crossing' (the naval.py r…

#### FA-15 [P2 · defect] A march into a SHUT crossing is narrated as an inconclusive battle; the contact question offers a dead 'attack'

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/commands/strategic.py:2583`
**Already filed:** WO-25 (FIXED, slice 17 — the jealousy autonomous-attack seam only; this is the strategic-march contact seam, same 'refused attack narrated as fought' shape); PC15-5(c) modal-of-theater family. NEW seam and NEW repro.

**What it is.** `_execute_move_to` checks for enemies in the next region BEFORE attempting the move (strategic.py:1014), so with Moore standing at London the aggressive branch auto-attacks (strategic.py:2763) and `_execute_attack`'s crossing gate (combat_executor.py:4839) refuses with `blocked_naval`; `_handle_combat_result` reads no `events`/`battle_result`, sets outcome `unknown` (strategic.py:2886) and falls into the stalemate arm (strategic.py:2946-2961): 'Ney attacked Moore during march but the battle was inconclusive', `combat_attempts` += 1, no battle fought. The cautious first-step twin (strategic_executor.py:1272 → 2194) asks 'Enemy at London. How shall I proceed?' before consulting the crossing at all; the answered `attack` then prints the naval refusal wrapped as 'Davout attacks Moore. … Assault failed — orders cancelled'. The honest `blocked_naval` break arm (strategic.py:1119) is unreachable whenever an enemy stands on the far shore — which for London is always.

**What the player sees.** In audit-naval the player marched Ney four turns Flanders→Normandy toward a crossing the Admiralty tab already called SHUT, was told on turn 11 that Ney fought Moore to a draw (no casualties, no battle report, no diorama), and on turn 14 that 'Odds unfavorable' — when the real reason was 100 sail against 54. The player learns the Channel is barred only after a false battle report and a cancelled order.

**Evidence.** Verified by running: Ney at Normandy under a MOVE_TO London issued the prior turn → process_strategic_orders returns {action: combat, outcome: stalemate, interrupt_type: combat_stalemate, message: 'Ney attacked Moore during march but the battle was inconclusive. Continue move to?'}; Moore 30000→30000, Ney 24000→24000, combat_attempts 0→1, zero battle events; the gate for the same pair reads verdict=shut ratio=0.54. `_respond_blocked_path('attack')` for Davout → 'Davout attacks Moore. The crossing from Normandy to London is barred — the Royal Navy commands the water with 100 sail (100 effective…

**Reproduce.** python -c: WorldState.from_scenario(europe_1805.json); ney=get_marshal('Ney'); ney.location='Normandy'; ney.strategic_order=StrategicOrder(command_type='MOVE_TO', target='London', target_type='region', started_turn=0, original_command='Ney, march to London', issued_turn=0); StrategicOrderProcessor(CommandExecutor()).process_strategic_orders(w, {'world': w}) → combat_stalemate with Moore's strength unchanged. In-game: 'Ney, march to Normandy' then 'Ney, march to London' and end turn.

**Fix shape (one seam).** In `_handle_blocked_path` (strategic.py:2583) — the ONE seam both the per-turn step and, via `resolve_order_destination`'s NPC-5 'one source' idiom, the first-step twin funnel into — call `naval.crossing_check_reach(world, marshal.nation, marshal.location, blocked_region, marshal.strength)` before the personality branch; when `not allowed`, return the existing `_break_order(... 'march halts at the water's edge — <message>')` arm instead of attacking or asking. Never mount `contact`/`contact_bad_odds` for a region the gate refuses.

**Behaviour test.** test_strategic_march_shut_crossing_is_refused_not_fought: Ney at Normandy, MOVE_TO London, RN 100 vs France 45 → the row's order_status is 'breaks', its message contains 'barred' and 'Royal Navy', no `combat_stalemate` interrupt is mounted, combat_attempts stays 0, Moore's strength unchanged, no 'battle' event logged; mirror for Davout (cautious) a…

#### FA-16 [P2 · defect] A parked last-stand question on an order-less marshal is never surfaced as a popup, does not stop him acting, and fires stale turns later against the enemy recorded when he was cornered

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/commands/strategic.py:874`
**Already filed:** WO-35 (load re-attach, FIXED), PC-9 (rail dedupe/retire, FIXED), NPC-20 (own_ground keys, FIXED) touch the same interrupt but none covers surfacing without an order or stale firing; NEW.

**What it is.** `_marshal_fate` parks an aggressive player marshal's last stand on `marshal.pending_interrupt` (`backend/commands/combat_executor.py:3313-3322`, options ['fight_to_the_last','attempt_breakout'] at :3320) with a rail notice, but the per-turn processor only emits a `requires_input` report for a marshal WITH a standing order (`backend/commands/strategic.py:874 if not order: return None` runs before the :878 pending-interrupt check), `clear_order_bound_interrupt` deliberately never drops order-free decisions (:112-140), and nothing re-validates the question. Verified by opening the flagship run's console: line 9505 '[!] Ney is CORNERED at Bohemia — awaiting your word' during turn 16's end turn (Ney's PURSUE had just been voided by the Franconia defeat, so no order). The digest then shows Ney charging autonomously on turn 17 (beats Paget, captures Carniola), being ordered 'march to Vienna' on turn 21, and the last-stand popup surfacing only on turn 22 ('Ney, last_stand, Ney awaits your orders → fight_to_the_last'), resolved via `_resolve_last_stand_fight(marshal, pending['enemy'])` against Archduke Charles as recorded on turn 16 — Ney a prisoner on turn 23.

**What the player sees.** A cornered aggressive marshal keeps fighting and marching for turns as if nothing happened; the only signal is a rail line ('type fight to the last…'); if the player later gives him any strategic order the six-turn-old question pops with its old enemy and, answered 'fight to the last', can hand the game a capture that no longer matches the map. The driver's `interrupt: first` policy makes this the shape of Ney's captivity in the flagship, but the staleness is the game's.

**Evidence.** backend/commands/combat_executor.py:3313-3322 (park + notice), :3320 (option order); backend/commands/strategic.py:874-886 (order-gated surfacing), :112-140 (never cleared); tools/playtest_runs/audit-flagship-mock/server_console.log:9505 (turn 16 CORNERED), :12774 (turn 22 orders processing); docs/audits/playtest_digests/audit-flagship-mock/digest.md turns 16 (no interrupt), 17 (AUTONOMOUS Ney vs Paget, capture Carniola), 21 (Ney marches to Vienna), 22 (last_stand popup), 23 ('Ney is a prisoner of Austria').

**Reproduce.** In-process on the 1805 world: give an aggressive player marshal `pending_interrupt = {'interrupt_type':'last_stand','enemy':'ArchdukeCharles','options':[...]}` and NO strategic_order; advance a turn — no `strategic_reports[i].requires_input` and no `pending_interrupt` in the end-turn response; move him one province and win a battle; then issue `march to X` and end turn — the report now carries requires_input with the turn-old enemy; POST /strategic_response fight_to_the_last resolves against tha…

**Fix shape (one seam).** ONE seam: `strategic.py:874` — check `marshal.pending_interrupt` BEFORE `if not order` so an order-free `last_stand`/`muster_confirm` is reported every tick (the client already derives popups from that list), and at the same seam re-validate: if the marshal is no longer cornered (moved, won, enemy gone/not adjacent) retire the parked question with a one-line report instead of surfacing it stale.

**Behaviour test.** tests/test_strategic.py (or a new test_last_stand_liveness.py): (1) parked last_stand + no order → end turn → response.pending_interrupt names the marshal (currently absent); (2) parked last_stand, then the marshal moves one province → end turn → pending_interrupt is None and a report says the encirclement passed; (3) the sovereign arm (:3269) inhe…

#### FA-17 [P2 · defect] A persistent settlement offer starves every answer behind it: France's own peace overture returns a COUNTER-OFFER that is queued unseen and lapses at the next end turn — 3 DP per turn, no popup, no cooldown

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/models/world_state.py:10116`
**Already filed:** none for the starvation/lapse; BUG_FIXES.md:3123 records the 'active popup-cache ownership' rule this rides on (IGR-F class) but no row covers a counter-offer lapsing unseen behind a persistent offer.

**What it is.** `incoming_settlement_offer` is persistent (mailbox priority 2, dialogue_manager.py:183-193) and `_promote` sorts by priority (:779-793), so while one sits in the slot every current-turn item pushed behind it — `counter_offer_response` (priority 3) and AI `incoming_proposal` letters — never becomes current, never writes `incoming_proposal_popup` (the IGR-F conditional write, ai_diplomacy.py:2057-2063; world_state.py:10129-10130), and is lapsed by `lapse_pending_offers` at the start of the next end_turn whether or not it was ever shown (dialogue_manager.py:558-580). The COUNTER_OFFER branch of `_process_proposal_in_transit` writes no `proposal_result_popup` and no cooldown (world_state.py:10060-10132 vs the REJECT branch :10194-10201), and the dispatch line is contentless ('Talleyrand returns from {nation} with a response.', dispatch.py:3803). In the archived propose campaign this happened on SEVEN consecutive turns (13,15,17,18,19,20,21: 'Talleyrand departs for the Austria court… (3 DP spent)' with no result ever shown) because Britain's turn-3 settlement offer held the slot for 21 turns.

**What the player sees.** The player sues for peace, pays 3 DP, reads 'expect a response by next turn', and next turn hears only 'Talleyrand returns from Austria with a response.' Austria's actual answer — 'France offers 1000 gold' as a counter — is visible only as a mailbox badge for one turn and then silently lapses; no cooldown fires, so the player can (and the archived run did) repeat the same futile overture every turn.

**Evidence.** verified by running: scratchpad probe_counter.py on the probe-diplomacy-propose turn-15 autosave — `propose peace with Austria` → `est 40 COUNTER_OFFER`; confirm → `DP=2`, in transit; end turn → event `"outcome": "COUNTER_OFFER", "message": "Talleyrand returns from Austria with a counter-proposal… France offers 1000 gold"`; state `CURRENT=incoming_settlement_offer#11 (turn 3) queue=[('incoming_proposal', 26, 15), ('counter_offer_response', 27, 16)] cooldowns={} result_popup=False popup_slot=None`; end-turn response carried no popup key; second end turn → `queue=[]`, log `offer_lapsed` ×2. veri…

**Reproduce.** Load tools/playtest_runs/<propose run>/saves/autosave.json (any state with an incoming_settlement_offer current, e.g. seed historical after turn 4); POST /command 'propose peace with Austria'; POST /respond_to_diplomatic_dialogue confirm; POST /command 'end turn' → inspect world.dialogue_manager: counter_offer_response queued behind the settlement offer, proposal_result_popup None, player_proposal_cooldowns {}; 'end turn' again → queue empty, event_log has offer_lapsed.

**Fix shape (one seam).** ONE seam: the COUNTER_OFFER branch of `_process_proposal_in_transit` (world_state.py:10060-10132) must deliver the answer the way REJECT/ACCEPT do — set `proposal_result_popup` with the counter summary (outcome COUNTER_OFFER) and set the per-court cooldown — so the reply reaches the player regardless of the mailbox slot. Secondary: `lapse_pending_offers` should not lapse a current-turn item that was never current (or promotion should rank lapsing items above persistent ones).

**Behaviour test.** With an `incoming_settlement_offer` current, send a peace proposal whose `calculate_acceptance` lands in 30–49; advance one turn; assert `world.proposal_result_popup` names the counter (outcome COUNTER_OFFER, the gold figure in the message) and `player_proposal_cooldowns[target] > 0`; advance again and assert the counter is still answerable or was…

#### FA-18 [P2 · defect] A queued proposal's popup is re-shown after a preempt + priority promotion, so the player's answer bounces with 'another matter has arrived since' — 4 of 24 turns in the flagship, mock and live

**Verdict:** DUPLICATE — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/models/dialogue_manager.py:779`
**Already filed:** IGR-F (BUG_FIXES §IGR-F, FIXED July 26 — delivery-time conditional write) and the Aug-30 review's counter-offer sibling (world_state.py:10118 comment) each closed one PRODUCER; grep of BUG_FIXES.md for 'another matter has arrived' returns no row. NEW: the priority-promotion-after-preempt producer, r…

**What it is.** Three surfaces write `world.incoming_proposal_popup`; IGR-F made the DELIVERY write conditional on the dialogue being current (ai_diplomacy.py:2045-2061) and the Aug-30 review fixed the counter-offer sibling (world_state.py:10118-10127). A third producer of the same stale-slot class remains: `DialogueManager.preempt` (dialogue_manager.py:322-346) re-queues the current dialogue behind a player-initiated one (the Assess advisory is mounted with `preempt`, diplomatic_executor.py:774), and when that is dismissed `pop` → `_promote` (dialogue_manager.py:347-352, :779-791) promotes by DIALOGUE_PRIORITY — `incoming_settlement_offer` 2 outranks `incoming_proposal` 3 (:185, :191). The settlement offer becomes current, but the popup slot still holds the proposal payload written when the proposal WAS current, and `_include_popup_passthroughs` (main.py:1594-1643) emits it; the client renders Russia's offer while Britain's settlement offer is active, and the id-bound answer hits the W6-0 stale guard (diplomatic_executor.py:3410-3432).

**What the player sees.** The Russia armistice popup is on screen; clicking Reject (or Accept) returns 'Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered'; the player must answer Britain's offer, and Russia's proposal is never re-presented in that run — it is '(left standing)' and lapses at end of turn, applying the 6-turn lapse cooldown. The player's decision never reaches the court. Reproduced on 4 of 24 turns of the flagship campaign, identically under the live parser.

**Evidence.** Archived: docs/audits/playtest_digests/audit-flagship-mock/digest.md:127-135 (turn 9: `Talleyrand, assess our situation` → `advisory #20 → dismiss` → `Russia, armistice_losing #17 → reject` → `↳ refused: Sire, another matter has arrived since — this concerns Britain…` → `incoming_settlement_offer #19 → reject_settlement_offer` → `Russia, armistice_losing #17 → (left standing)`); same shape at :226-231 (Prussia #31), :262-267 (Britain #36 vs settlement #39), :338-343 (Prussia #51); audit-flagship-live/digest.md:129-135 identical. Verified by opening: dialogue_manager.py:322-346 (preempt re-queu…

**Reproduce.** 1805 boot via TestClient: deliver an AI `incoming_proposal` so it is current (slot written); `promote_pending_settlement_offers` pushes an `incoming_settlement_offer` (queued); POST /command 'Talleyrand, assess our situation'; POST /respond_to_diplomatic_dialogue dismiss on the advisory; read the response's `diplomatic_dialogue.dialogue_id` vs `world.dialogue_manager.peek()['dialogue_id']` — they differ; POST reject with the rendered id → `stale_dialogue: True`, message 'another matter has arriv…

**Fix shape (one seam).** ONE seam: `DialogueManager._promote` (dialogue_manager.py:779) — after promoting, re-sync the blocking-modal slot from the promoted dialogue's own `popup_payload` (or clear it when the promoted dialogue is a letter-book row), so the slot can never describe a queued dialogue; equivalently, have `_include_popup_passthroughs` derive `diplomatic_dialogue` from `peek()` and retire the slot. The delivery and counter-offer guards stay as they are.

**Behaviour test.** tests/test_w6_dialogue_identity.py: the sequence above asserts `response['diplomatic_dialogue']['dialogue_id'] == dm.peek()['dialogue_id']` after the advisory is dismissed, and that Reject on the rendered id succeeds (no `stale_dialogue`); a second case with two queued proposals of different priority after a `preempt`.

#### FA-19 [P2 · defect] A refused Channel crossing is narrated as a fought stalemate and stamps the marshal in-combat

**Verdict:** DUPLICATE — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/commands/strategic.py:2860`
**Already filed:** none found — PT-D4 (move-chain presentation, LANDED, "the naval gate itself stays") and WO-33 (battle_report carry, FIXED) are adjacent seams, not this one

**What it is.** When a strategic MOVE_TO's contact auto-attack is REFUSED by the crossing gate (executor result success=False, blocked_naval=Britain, no events, no battle_result), `_handle_combat_result` falls into its 'stalemate / unknown' arm and reports "Ney attacked Moore during march but the battle was inconclusive. Continue move to?" — no battle happened. The sibling `_respond_blocked_path` (strategic.py:612-658) composes "Davout attacks Moore. <the barred sentence> Assault failed — orders cancelled" for the same refusal.

**What the player sees.** The player is told his marshal fought and drew a battle that never took place, is asked whether to continue, and the same false stalemate re-fires every turn the order stands; the marshal is stamped in_combat_this_turn=True / last_combat_result='stalemate' / combat_attempts+1 (read by world_state.py:11966 idle tracking and jealousy.py:707).

**Evidence.** Verified by opening docs/audits/playtest_digests/audit-naval/digest.md:159 — verbatim "POPUP strategic_interrupt: Ney, combat_stalemate, Ney attacked Moore during march but the battle was inconclusive. Continue move to? → continue_order". Verified by running: the turn-13 snapshot's event_log has NO battle with attacker or defender Ney at turn 11 (its turn-11 battles are Charles/Lannes, Charles/Massena, Castanos/Paget ×2); server_console.log:6885 "[STRATEGIC MOVE] Ney: Normandy -> London" at turn 11. Reproduced on the t10 snapshot: `CommandExecutor().execute({'command': {'marshal':'Ney','action…

**Reproduce.** Load tools/playtest_runs/probe-naval/saves/probe-naval_t10.json (or any 1805 world with Britain's fleet blockading), put Ney (aggressive) at Normandy with a MOVE_TO London order whose path is ['London'] and Moore at London, run the end-turn strategic step (or call the executor attack + `_handle_combat_result` as above) — observe the combat_stalemate interrupt and no battle event.

**Fix shape (one seam).** ONE seam: at the top of `_handle_combat_result` (strategic.py:2860) treat `result.get('success') is False` with no `events`/`battle_result` as NO BATTLE — return `_break_order` (or the PF-8 `blocked_naval` stall wording already at strategic.py:1120, "march halts at the water's edge — …barred…") without touching combat_attempts / in_combat_this_turn / last_combat_result; mirror the same guard in `_respond_blocked_path` so the copy reads "cannot attack — the crossing is barred" rather than "attacks Moore … Assault failed".

**Behaviour test.** 1805 world, Britain blockading, Ney at Normandy with MOVE_TO London path ['London'], Moore at London: process the strategic step → assert no interrupt of type combat_stalemate, the report message contains 'barred', no 'battle' event is appended, Ney.in_combat_this_turn is False and order.combat_attempts is 0; then answer a contact interrupt with 'a…

#### FA-20 [P2 · defect] A refused first-step attack leaves a PHANTOM standing order on the marshal (0 AP charged, order lives on)

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/commands/strategic_executor.py:2153`
**Already filed:** none found (grep 'phantom order|left standing|stale order|first-step attack' in BUG_FIXES.md / DESIGN_REFINEMENT.md).

**What it is.** `_execute_strategic_command` assigns `marshal.strategic_order = order` at backend/commands/strategic_executor.py:1216 BEFORE executing the first step; when the first hop is enemy-held, `_handle_first_step_blocked` (:2030) runs and its aggressive favourable arm (:2131-2153) auto-attacks and, on a refused/failed executor result, does `return result` (:2153) — the raw refusal dict — without clearing the order it just created (contrast the literal arm at :2064-2081, which clears the order and returns `order_cleared: True`). The loop at :1278 returns that dict as the command's result, so the player sees a refusal (success False, no AP charged) while a MOVE_TO order is silently standing and fires at the next end turn (→ the phantom-battle finding above).

**What the player sees.** 'Ney, march to London' from Normandy prints the honest naval refusal and charges nothing, so the player believes nothing happened — but Ney now carries a hidden 'march to London' that re-fires every end turn, producing the 'attacked Moore … inconclusive' popup, incrementing `combat_attempts`, and showing in the Orders ledger as a march the player never saw accepted.

**Evidence.** Verified by opening strategic_executor.py:1216 (order assigned), :1263-1308 (first-step loop; failure only prints 'Move FAILED' and breaks), :2131-2153 (`if favorable:` → attack → `return result` when not success), :2064-2081 (literal arm clears). Verified by running probe_strategic2.py E2: `result success: False | keys: ['action_info','action_summary','blocked_naval','message','naval_ratio','success']` and `order standing: True ['London']`; probe_strategic.py E: `AP charged: 0`, `order: ('MOVE_TO','London',['London'],'issued',1)`.

**Reproduce.** Boot the 1805 scenario; `ney=w.get_marshal('Ney'); ney.location='Normandy'; w.calculate_visibility()`; parse+execute 'Ney, march to London' with `CommandParser(use_real_llm=False)` / `CommandExecutor()`; assert the result is `success: False` with `blocked_naval` set AND `ney.strategic_order is not None` (it is). Then `process_strategic_orders` next turn → combat_stalemate popup.

**Fix shape (one seam).** ONE seam: in the aggressive arm of `_handle_first_step_blocked` (strategic_executor.py:2143-2153), when `not result.get("success")` mirror the literal arm — `marshal.strategic_order = None; clear_order_bound_interrupt(marshal); marshal.holding_position=False; marshal.hold_region=''` — and return the refusal with `order_cleared: True`, `first_step_blocked: True`, `variable_action_cost: 0`. (The movement_executor auto-upgrade path at :413-416 returns the same `blocked_result`, so it inherits the fix.)

**Behaviour test.** tests: aggressive marshal adjacent to an enemy-held destination whose attack the executor refuses (Channel covered by `world.fleets`, or the marshal `fortified`) → typed 'march to <dest>' returns success False AND `marshal.strategic_order is None`; a following `process_strategic_orders` yields no report for him; AP unchanged.

#### FA-21 [P2 · defect] AI harsh-peace demands are purse-blind on the bilateral P8 path — 270g against a 17,487g treasury at +54 war score, bypassing the gate-blessed EC-W4 pricing

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/game_logic/ai_diplomacy.py:896`
**Already filed:** DESIGN_REFINEMENT.md A4 (:983-985) records the same formula as a 'historical note only' — it documents, not files, the defect; EC-W4 (memo row 4) and BUG_FIXES have no row for the bilateral P8 arm. NEW: the bilateral channel was outside EC-W4's rewrite, measured 270 vs 6,233 on one state.

**What it is.** EC-W4 'Peace with Teeth' re-priced only the multilateral settlement-offer builder (`_settlement_offer_build_terms`, ai_diplomacy.py:3236-3247 constants, :3379-3389 purse-scaled formula). The bilateral P8 'Aggressive Dominance' arm (ai_diplomacy.py:1550-1554, fires at war_score > 40) still builds its demand as `gold_demand = max(200, int(war_score * 5 * gold_mult))` (ai_diplomacy.py:896), never reading either treasury, and `_reduce_p8_demands` (:914-935) can only lower it further toward a flat 200 floor. Verified by running on tests/fixtures/playtest_saves/fixture_t20_ambient.json: Britain's war score vs France +54, France treasury 17,487, P8 terms `[{'type':'gold_lump','value':270}]`, acceptance score 53, unchanged after `_reduce_p8_demands`; the EC-W4 settlement path on the SAME state prices 6,233 (cap 6,994, war age 19). The fixture also carried `Britain|harsh_peace: 5` in `ai_proposal_cooldowns`, i.e. a harsh_peace had been sent in the ambient run one turn before turn 20 — the arm fires in ordinary play.

**What the player sees.** A decisively beaten France (coalition leader at +54, Paget/Moore across the homeland in audit-latewar-t20) receives a 'Harsh Peace Treaty' that costs ~1.5% of the treasury; accepting ends the war for pocket change and re-declaration is priced only in DP/relations (WO-D8). The July-17 absurdity the memo fixed ('Britain at +24 extracts 600g of a 61k hoard', ECON_WAR_COUPLING_RESEARCH_2026_07_17.md:28) survives verbatim on the bilateral channel, and GR5 is broken in the other direction too: an AI at +54 never dictates a real indemnity, so the AI's own 'winning' has no economic teeth.

**Evidence.** Verified by opening: backend/game_logic/ai_diplomacy.py:893-897 (harsh_peace builder), :1550-1554 (P8 gate), :914-935 (`_reduce_p8_demands` halving to floor 200), :3236-3247 (`SETTLEMENT_OFFER_TREASURY_FRACTION=0.15`, `MAX_TREASURY_FRACTION=0.40`, `PER_WAR_SCORE=40`), :3379-3389 (purse formula lives only in the settlement builder); docs/audits/ECON_WAR_COUPLING_RESEARCH_2026_07_17.md:28 and :171 ('`_settlement_offer_build_terms` rewritten' — the landing names only that builder). Verified by running (scratch probe_t20c.py on the committed t20 fixture): P8 demand 270 / acceptance 53 / post-reduc…

**Reproduce.** cd repo; .venv/Scripts/python.exe -c "import os,json,sys; os.environ.pop('SOVEREIGN_SCENARIO',None); from backend.models.world_state import WorldState; from backend.game_logic import ai_diplomacy as ad; w=WorldState.from_dict(json.load(open('tests/fixtures/playtest_saves/fixture_t20_ambient.json',encoding='utf-8'))['world_state']); ws=ad._get_war_score_for_nation('Britain','France',w); t=ad._build_proposal_terms('Britain','harsh_peace',ws,w,gold_mult=1.0); print(ws, w.gold, t['demands'])" → 54 1…

**Fix shape (one seam).** ONE seam: the `harsh_peace` arm of `_build_proposal_terms` (ai_diplomacy.py:893-897). Extract the EC-W4 purse formula (base + war-age + |score|×PER_WAR_SCORE + payer_treasury×FRACTION, capped at payer_treasury×MAX_FRACTION, empty chest → no lump) into one helper that BOTH `_settlement_offer_build_terms` and the P8 arm call with `payer = recipient`; make `_reduce_p8_demands` halve relative to that figure instead of flooring at 200. No new fields; AI-side acceptance already scores the lump.

**Behaviour test.** tests/test_econ_war_coupling.py: load fixture_t20_ambient, build Britain `harsh_peace` vs France; assert gold_lump ≥ 0.15×France treasury and ≤ 0.40×; assert it equals `_settlement_offer_build_terms` on the same state within the war-age term; negative control: set France treasury 0 → no gold_lump demand; pin that `_reduce_p8_demands` never lowers t…

#### FA-22 [P2 · defect] An addressee the roster cannot resolve is silently DROPPED and the attack auto-assigned to whoever is nearest — "the Iron Marshal, attack Mack" / "Berthier, attack Mack" send Soult

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/commands/parser.py:1074`
**Already filed:** CR-2 (f) silent-marshal-drop (COMMAND_ROBUSTNESS_SPEC.md:29) covers single-token addressees on META actions only

**What it is.** Two gaps in one seam. (a) ADDRESS_TOKEN_RE (llm_client.py:71-72, verified by opening) captures a SINGLE word before the comma, so multi-word addressees ("the Iron Marshal,", "Prince of Moskowa,", "the cavalry,") never reach `_unresolved_address_token` (:291-320) or CR-2's did-you-mean. (b) A single-word addressee that merely RESEMBLES a region is skipped rather than refused: in the parser word-scan below parser.py:1074 (`was_addressed`), a marshal 'error' falls to `target_check` against regions+enemies and the word is skipped as 'might be a target' — verified by running FuzzyMatcher: 'Berthier' vs marshals = error, vs targets = suggest 'Bern' at 75. Either way marshal=None, `_classify_command` (parser.py:1915-1945) returns `auto_assign_attack`, and `resolve_auto_attack`'s auto_assign arm (combat_executor.py:8748ff) names the nearest marshal instantly (blessed by the CR-6 gate for a BARE 'attack Mack', but here the player DID name someone).

**What the player sees.** Verified by running: `the Iron Marshal, attack Mack`, `Iron Marshal, attack Mack`, `Berthier, attack Mack`, `Prince of Moskowa, attack Mack`, `the cavalry, attack Mack`, `the reserve, attack Mack` → all "MUSTER — Soult (30,000; 101,499 if all march) vs Mack" + a battle_report (Mack strength 0 afterwards). The player asked for Davout (Iron Marshal) / Ney (Prince of the Moskowa) / the cavalry (Murat) and the literal-personality Soult marched; the only disclosure is the marshal's name inside the MUSTER line. `the Guard, attack Mack` → the hold keyword 'guard' (llm_client.py:1485) makes it a HOLD/…

**Evidence.** verified by opening backend/ai/llm_client.py:71-72, :80-97 (ADDRESS_NON_NAME_WORDS includes cavalry/guard), :291-320; backend/commands/parser.py:1074-1176 word-scan, :1915-1945 `_classify_command`; backend/commands/combat_executor.py:8636-8649 and :8748-8797; verified by running the /command probes and a FuzzyMatcher probe.

**Reproduce.** POST /command {"command":"the Iron Marshal, attack Mack"} or {"command":"Berthier, attack Mack"} on the 1805 boot → MUSTER led by Soult + battle_report; {"command":"the Guard, attack Mack"} → message "Error: No target or world state".

**Fix shape (one seam).** ONE seam — the addressee extraction: make ADDRESS_TOKEN_RE capture the whole pre-comma phrase (`^\s*(?:the\s+)?([A-Za-z][\w'’ -]{1,40}?)\s*,`) so `_leading_addressed_token` sees multi-word addressees, and in the parser word-scan treat `was_addressed and marshal_result['action']=='error'` as `marshal_not_found` regardless of `target_check` (a comma-addressed token is never a target). Then an unbound addressed attack raises the CR-2 'Whom did you intend?' question and never reaches `_classify_command`'s auto-assign.

**Behaviour test.** each of the six phrasings → success False, kind marshal_not_found/marshal_suggest, no battle_report, Soult still at Lorraine at 30,000; bare `attack Mack` keeps the CR-6 instant pick (test_cr6_bare_attack_gating stays green); `the Guard, attack Mack` never returns a string starting with 'Error:'.

#### FA-23 [P2 · defect] An enemy garrison assault on French soil is invisible on every surface unless the assaulter's own province is FULL

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/commands/combat_executor.py:3148`
**Already filed:** CA8-19 / CA8-25 (RULED/CLOSED) record only that the garrison path emits no `battle` event for the DIORAMA; WO-3 (FIXED) notes the futility tracker cannot see a hold. The fog suppression, the missing client arm and the missing log event are NOT filed.

**What it is.** `_resolve_garrison_combat` (backend/commands/combat_executor.py:2857-3157) calls `world.log_event` zero times (verified by awk over the whole function) and returns only a private `events: [{"type": "garrison_assault", ...}]` row (:3148) or `garrison_destroyed`/`occupation_started` (:3051-3061). The enemy-phase fog filter `_filter_enemy_phase_by_visibility` (backend/main.py) treats a row as involving the player only for `battle`/`bombardment` events (:1749), an `ai_action.target` that is a player MARSHAL, or an event stamped `captured_from == player` (:1798) — a `garrison_assault` on a player-controlled region satisfies none, so the row falls to the region check and is suppressed when the assaulter stands on a PARTIAL province (the ordinary P4.25 case: `_find_garrison_attack` picks an ADJACENT garrison, enemy_ai.py:1981-1989). Verified by running: Mack at Swabia (vis `partial`) assaulting the Rhineland garrison on the 1805 boot board → `survives filter: 0`. Even when a row survives, `enemy_phase_dialog.gd::_format_action` (:121, events loop :248-272) has arms only for `battle`/`bombardment`/`conquest`, so the line renders as a bare `- Mack attacks Milan`. `garrison_assault` is in ne…

**What the player sees.** The enemy can grind the Paris/Milan garrison from 25,000 to 5,000 over several turns and the player learns nothing from the enemy-phase dialog, the morning dispatch, the campaign log or Le Moniteur — the only trace is the garrison number on the region panel if he happens to click it. The digest line `Mack assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). Mack loses 2,723 troops. Garrison holds` (audit-ambient40 digest.md:259) is the backend `message` the client never reads; the rows that were fogged never even reached the digest.

**Evidence.** verified by opening backend/commands/combat_executor.py:2857-3157 (no log_event), :3051-3061, :3148-3153; backend/main.py:1741-1810; godot-client/project-sovereign/scripts/enemy_phase_dialog.gd:121-272; backend/campaign_log.py:94-160; backend/game_logic/gazette.py:32-36; backend/ai/enemy_ai.py:1981-1989 + `_find_garrison_attack` ('for adj_name in marshal_region.adjacent_regions'). Verified by running the filter with a constructed P4.25 row on `WorldState.from_scenario(europe_1805.json)` → 0 rows survive. Digest: docs/audits/playtest_digests/audit-ambient40/digest.md:259 verbatim.

**Reproduce.** C:/Users/User/PycharmProjects/project-sovereign-map/.venv/Scripts/python.exe -c "import os;os.environ.pop('SOVEREIGN_SCENARIO',None);from backend.models.world_state import WorldState;from backend.main import _filter_enemy_phase_by_visibility;w=WorldState.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json');w.calculate_visibility();m=w.get_marshal('Mack');row={'nation':'Austria','success':True,'message':'Mack assaults the Rhineland garrison!','ai_action':{'marshal':'Mack',…

**Fix shape (one seam).** ONE producer seam: `_resolve_garrison_combat` should `world.log_event` its `garrison_assault`/`garrison_destroyed` event stamped with `nation` = the assaulted region's controller and `captured_from`-style ownership keys, so the three existing consumers can read it with one-line arms each — main.py's PT-E5 own-soil arm (:1798) extended to `evt.get("type") in ("garrison_assault","garrison_destroyed") and region controller == player` (leaks nothing: the garrison and the soil are ours), a 5-line `garrison_assault` arm in `_format_action` ("Mack assaults the Milan garrison — 5,000 of 10,000 defenders fall; Mack loses 2,723; the garrison holds"), and `CAMPAIGN_LOG_TYPES` + `format_event_oneliner`…

**Behaviour test.** tests/test_enemy_phase_presentation.py: build the 1805 world, run Mack's P4.25 row (assaulter at PARTIAL) through `_filter_enemy_phase_by_visibility` and assert the row SURVIVES; assert `world.event_log` contains a `garrison_assault` event after `_resolve_garrison_combat`; assert `format_event_oneliner` renders it with both loss figures; a Godot pa…

#### FA-24 [P2 · defect] Attacking a marshal France holds prisoner answers 'Unknown target' one turn after the dispatch called him 'our prisoner' — and the parser comment claiming PC15-4 covers it is false

**Verdict:** DUPLICATE — Sept 2 verification (confidence high; the audit published AUTHOR_VERIFIED) · **Seam:** `backend/commands/executor.py:719`
**Already filed:** NPC-7 (open — the region-misread and executing arms), NPC-19 (open — pursue accepts, bare attack says destroyed), NPC-6 (open — target-side twin of PC15-4). NEW here: the bare 'Unknown target' arm, the false parser comment at parser.py:1380, the pursue marching to the last-known province with '(at u…

**What it is.** Archived digest: T2 'Marshal Kienmayer of Austria is taken at Swabia — he is our prisoner' (audit-tutorial/digest.md:23), T3 `Ney, attack Kienmayer` -> 'Unknown target: Kienmayer' (:26). Mechanism verified by opening: `_fuzzy_match_enemy` (executor.py:719-748) looks the name up through `get_enemy_by_name_for_nation` which requires strength > 0 (world_state.py:3750-3755), so a prisoner (strength 0 at the captor's capital) is 'not found'; the honest 'Enemy X not found. Available: …' error is then DISCARDED by combat_executor.py:4596-4601 (returned only when it carries 'Did you mean' or `refused_marshal_correction`), the region fuzzy finds nothing, and the bare fall-through at combat_executor.py:5095-5098 prints 'Unknown target'. parser.py:1380-1381 asserts 'a PRISONER is not a target … PC15-4 already refuses him by name', but `_addressed_lost_marshal_refusal` (main.py:894-925) reads only the LEADING addressed token against the PLAYER's roster and tombs — an enemy prisoner as a TARGET is never seen. Three surfaces give three different answers to one question.

**What the player sees.** The player copies the game's own sentence and is told the man does not exist. `attack Kienmayer` (bare) says 'Kienmayer has already been destroyed!' of a living prisoner; `Ney, pursue Kienmayer` is ACCEPTED, charges 2 AP, prints '(at unknown)' and physically marches Ney to Swabia toward a man sitting in Paris. In the School of War this is the suggest chip of step VII when the player took the card's first-listed answer (trust).

**Evidence.** Verified by running (scratch script over TestClient, INK_IRON_SAVE_DIR sandboxed): /new_game {scenario: tutorial}; set Kienmayer strength=0, captured_by='France', location='Paris'; then `Ney, attack Kienmayer` -> False 'Unknown target: Kienmayer'; `attack Kienmayer` -> False 'Kienmayer has already been destroyed!'; `Ney, pursue Kienmayer` -> True 'Ney pursues Kienmayer (at unknown). Moves to Swabia.' Verified by opening: executor.py:719-748, world_state.py:3737-3755, combat_executor.py:4563-4601 and :5095-5098, parser.py:1370-1385, main.py:894-925, strategic_executor.py:1509-1517 (`_pursue_kno…

**Reproduce.** Boot any world, capture an enemy marshal (or set `m.strength=0; m.captured_by='France'; m.location='Paris'`), POST /command 'Ney, attack <name>', 'attack <name>', 'Ney, pursue <name>'.

**Fix shape (one seam).** ONE seam: at the top of `_fuzzy_match_enemy` (executor.py:719), before the strength>0 lookup, resolve `world.marshals.get(enemy_name)`; if `captured_by` is set return a prisoner refusal that names the captor and location ('Kienmayer is our prisoner at Paris, Sire — he leads no army'), with a `prisoner` key so combat_executor.py:4596 returns it verbatim and the bare-attack 'destroyed' copy at combat_executor.py:8080 branches on it; have strategic_executor's PURSUE target filter (:599) call the same helper so pursue refuses at 0 AP.

**Behaviour test.** In tests/test_npc_cluster-style file: capture Kienmayer, assert all three of `Ney, attack Kienmayer` / `attack Kienmayer` / `Ney, pursue Kienmayer` return success False, mention 'prisoner' and the captor, charge 0 AP, and leave Ney's location unchanged; negative control: the same commands against a living Kienmayer still fight/pursue.

**Author note.** HV-1 the game forgets its prisoners

#### FA-25 [P2 · defect] Bombardment casualties never reach the morning dispatch or Le Moniteur — seven turns of daily shelling narrate as a 29-turn-old grievance

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/game_logic/dispatch.py:742`
**Already filed:** none — grep 'bombard' in docs/BUG_FIXES.md and docs/DESIGN_REFINEMENT.md hits only PC15-9 (tutorial anchor), CA8-19 (mechanics), S5-5 (gate bypass).

**What it is.** `_build_headline` derives `own_mauled` only under `elif etype == "battle"` (backend/game_logic/dispatch.py:742-770); the executor logs bombardments as `{"type": "bombardment", ...}` (backend/commands/combat_executor.py:3965-3981), a type absent from `_DISPATCH_EVENT_TYPES` (dispatch.py:2718-2790) and from the gazette's `_WAR_TYPES` (gazette.py:32-36). Reproduced: Ney loses 28,800 of 72,000 men (40%) to Wellington's guns in one shot → `_build_headline` returns None and the whole dispatch payload contains neither 'bombard' nor the casualty figure; the campaign log alone prints 'Wellington (Britain) bombarded Belgium — 28,800 casualties'. In the ambient40 campaign the enemy phase of turns 34, 35, 36, 39 and 40 is `2 actions, 2 attacks — ======================================== · ========================================` (digest.md:328,335,342,362,369) — the `'=' * 40` banner is combat_executor.py:3932's bombardment message, the only production `'=' * 40` in the backend (all other hits are `print` in `__main__` blocks) — while the dispatch of those mornings leads with 'Paget has crossed into Flanders' (:331), 'Marshal Lannes's grievance is 29 turns old' (:338), '3 turns now with enemy…

**What the player sees.** A corps being shelled twice a turn for seven turns produces no headline, no sub-beat, no turn-event line and no Gazette row; the player reading the briefing believes the front is quiet while his army bleeds under the guns.

**Evidence.** verified by opening dispatch.py:742-770, :2718-2790; combat_executor.py:3932, :3965-3981; gazette.py:32-36. Verified by running the repro (headline None, no mention). Digest: docs/audits/playtest_digests/audit-ambient40/digest.md:328-372 verbatim; audit-flagship-mock/digest.md:233,313,355 carry the same banner.

**Reproduce.** C:/Users/User/PycharmProjects/project-sovereign-map/.venv/Scripts/python.exe -c "import os;os.environ.pop('SOVEREIGN_SCENARIO',None);from backend.models.world_state import WorldState;from backend.game_logic.dispatch import _build_headline,build_morning_dispatch;w=WorldState();p=w.player_nation;e=[n for n in w.enemy_nations if w.is_at_war(p,n)][0];pm=next(m for m in w.marshals.values() if m.nation==p);em=next(m for m in w.marshals.values() if m.nation==e);w.current_turn+=1;cas=int(pm.strength*0.4…

**Fix shape (one seam).** ONE seam — the battle arm of `_build_headline` (dispatch.py:742): also accept `etype == "bombardment"`, summing the turn's `defender_casualties` per player marshal (two shots a turn is the AI's pattern) into the existing `own_mauled` identity `own_mauled:{name}` with a 'shelled' phrasing ('Ney stood under Moore's guns at Flanders: 2,269 men lost to the batteries'), so the WO-16 floor, CA8-5 dedupe and the reversal absorption all apply unchanged; add `"bombardment"` to gazette `_WAR_TYPES`.

**Behaviour test.** tests/test_dispatch_headline.py: log one `bombardment` event costing ≥25% of a player marshal's pre-strength and ≥ OWN_MAULED_MIN_CASUALTIES → `_build_headline(...)['class'] == 'own_mauled'` and the text names the marshal, the gunner and the figure; two sub-floor shots in one turn against the same corps aggregate above the floor; `compose_issue` li…

#### FA-26 [P2 · defect] Dotation erosion bleeds trust to 0 with no terminus, no petition and no redemption — the seam never reaches the trust<=20 channel

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published AUTHOR_VERIFIED) · **Seam:** `backend/models/world_state.py:6206`
**Already filed:** Adjacent only: UX23-D1..D4 (DESIGN_REFINEMENT — the expectation CURVE), PC-7 (dispatch repetition, FIXED), N3 (erosion notice dismissal, FIXED). No row covers the erosion->redemption seam gap or the single-eroding-marshal case.

**What it is.** `_process_dotation_state` applies `marshal.modify_trust(-points)` every eroding turn (world_state.py:6203-6206) and never calls `check_redemption_threshold`; the only per-turn sweep is `_check_trust_warnings` (world_state.py:12051-12107), which fires ONE terminal line at <40 and nothing else. The collective Fontainebleau petition needs >=3 eroding marshals (jealousy.py:114 `FONTAINEBLEAU_MIN_ERODING = 3`), so a single unpaid marshal has no voice at all. Verified by running: 1805 boot, Lannes battles_won=3 (expectation 120, satisfaction 0, `list_eligible_estates` = []): trust 85 -> 82 (turn 6, grace elapsed) -> 52 (t16) -> 37 (t21, the single warning) -> 22 (t26) -> 7 (t31) -> 0 (t36) and stays 0; 'redemption produced by erosion seam over 44 turns: 0' while `check_redemption_threshold` returns an event the moment it is asked. The archived ambient40 digest shows exactly this arc: lines 193/338/372 'Marshal Lannes's grievance is 13/29/34 turns old ... It is now a question of the army' — a headline whose escalation copy (dispatch.py:229-235) names an army-wide consequence that has no mechanic behind it; `dotation.py:56-57` states 'Trust's native floor at 0 is the only floor'.

**What the player sees.** An unpaid marshal the player never orders (a garrison, a reserve, a second-line corps) silently goes Loyal -> Broken over ~30 turns with one terminal line and a standing rail row; nothing ever escalates into the decision the trust system promises ('at 20 he will ask to be released', world_state.py:12097-12100 — false: he asks only when a command/objection seam is next touched). The first time the player DOES order him, the objection lands at HOSTILE tone (-15 insist, objection_v2.py:74-77), severity x1.6 (severity.py:118-125) and defiance +0.15 (defiance.py:97-99) with no arc the player could…

**Evidence.** verified by opening world_state.py:6022-6240 (no redemption call in the erosion branch; only `post_erosion_notice`), world_state.py:12051-12107, dotation.py:54-57 + 86 (EROSION_MAX 3, GRACE_TURNS 4), jealousy.py:114 + 2246-2280, dispatch.py:229-235 + 926-935; verified by running scratchpad/probe_erosion.py (output quoted in summary); archived digest audit-ambient40/digest.md lines 193, 338, 372 verbatim 'Sire — Marshal Lannes's grievance is 34 turns old and has stopped being a household matter. It is now a question of the army.'

**Reproduce.** from backend.models.world_state import WorldState; from backend.game_logic import dotation; w=WorldState.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json'); m=w.marshals['Lannes']; m.battles_won=3 for t in range(44): w.current_turn+=1; w._process_dotation_state(); w._check_trust_warnings() print(m.trust.value, w.pending_redemption, m.redemption_pending) # -> 0 None False

**Fix shape (one seam).** ONE seam: in `_process_dotation_state`, immediately after `marshal.modify_trust(-points)` (world_state.py:6206), when `marshal.nation == self.player_nation and marshal.trust.value <= 20`, call `self.disobedience_system.check_redemption_threshold(marshal, self)` and append `{'type':'redemption_event','redemption_event':ev}` to the same `tactical_events` list `_check_trust_warnings` extends (world_state.py:9754-9756) so the existing WO-41 `hoist_tactical_redemption` (disobedience.py:691) carries it to the response with zero new client wiring. (A dotation-specific single-marshal petition through `_push_petition` would be the richer answer, but the redemption channel already exists and is latche…

**Behaviour test.** tests/test_dotation_erosion_reaches_redemption.py: 1805 world, one French marshal battles_won=3, no orders; advance via `_process_dotation_state` until trust <= 20; assert the tick's tactical events carry a `redemption_event` for him and `world.pending_redemption` is latched (WO-41 predicate `standing_redemption` non-None); negative arm: a marshal…

**Author note.** HV-3 erosion to trust 0 with no redemption audience

#### FA-27 [P2 · defect] Infantry forms square (1 AP) and then attacks — breaking the square — in the same enemy phase, every phase

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/ai/enemy_ai.py:1835`
**Already filed:** PT-F6 (FIXED Aug 1, 2026 — the form/break/re-form thrash within a phase); this is the narrower surviving shape its latch permits by design.

**What it is.** P2.5 (enemy_ai.py:1795-1840) forms square whenever enemy cavalry is adjacent, no artillery is adjacent and the cooldown/latch permit (condition at :1835), and it is evaluated BEFORE P4; the same marshal is then re-selected, P4 finds his attack, and the attack breaks the square via `_auto_break_square` (tactical_executor.py:461-485), which sets no `ai_square_cooldown`, so the square is formed again next phase. `form_square` costs 1 AP (world_state.py:942). PT-F6's latch stops the form/break/RE-form thrash within a phase and deliberately leaves 'attack breaks legal', which is exactly the surviving waste: one paid action per infantry marshal per phase on a formation he discards seconds later.

**What the player sees.** One to two of the nation's four actions per turn evaporate whenever French cavalry stands next to Austrian infantry — audit-ambient40 Turns 21-26 show `form_square×2` plus `[Square broken — ArchdukeCharles breaks formation to attacks]` six turns running (Turn 23 both John and Charles), audit-naval t4/t13/t14, audit-ambient-austerlitz t9 `form_square×3`. Combined with the garrison loop and the remnant hammering the Austrian phase is mostly wasted motion, and the enemy-phase dialog reads 'forms square, then charges' as farce.

**Evidence.** Verified by running (probe C): boot 1805, Charles (cautious infantry) at Tyrol in DEFENSIVE stance, Murat (cavalry, 20,000) at Munich, Mack/John parked at Hungary: phase 0 actions = `form_square, stance_change(John), drill(Mack), attack Deroy`; after `advance_turn()` phase 1 = `attack Deroy, fortify(John), form_square, unfortify(John), attack Murat` — `square_formation` False and `ai_square_cooldown` 0 after each phase. Verified by opening: enemy_ai.py:1795-1840 (the form rung runs before P4 at :1968 and asks nothing about an attack), tactical_executor.py:461-485 (`_auto_break_square` writes n…

**Reproduce.** `.venv/Scripts/python.exe -c "import random; from backend.models.world_state import WorldState as W; from backend.models.marshal import Stance; from backend.ai.enemy_ai import EnemyAI; from backend.commands.executor import CommandExecutor as C; w=W.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json'); w.marshals['Mack'].location='Hungary'; w.marshals['ArchdukeJohn'].location='Hungary'; c=w.marshals['ArchdukeCharles']; c.location='Tyrol'; c.stance=Stance.DEFENSIVE; mu=w.ma…

**Fix shape (one seam).** ONE seam: gate the form condition at enemy_ai.py:1835 on the marshal having no strike this phase — `and self._find_attack_opportunity(marshal, nation, world) is None` (a corps that will attack does not first pay for a square it will break) — or, equivalently, evaluate P4 before P2.5 for infantry with an attackable target. Keep the PT-F6 latch and stance guard as they are.

**Behaviour test.** Extend `tests/test_ai_square_thrash.py`: probe-C shape → in one phase no `form_square` by Charles precedes an `attack` by Charles; positive control: with Murat at 60,000 (no attack meets the cautious threshold) the square still forms; control arm with the gate disabled must reproduce form→attack.

#### FA-28 [P2 · defect] Popup queue and dialogue stack disagree after any re-promotion: the envoy popup the game shows is refused as stale when clicked

**Verdict:** DUPLICATE — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/main.py:1620`
**Already filed:** BUG-CA-7 (FIXED — landed the W6-0 identity guard that now refuses these clicks); IGR-F note at ai_diplomacy.py:2043-2056 fixed the sibling last-write-wins variant. The re-promotion desync between the two queues is NOT filed in BUG_FIXES.md or DESIGN_REFINEMENT.md (grepped 'another matter has arrived…

**What it is.** PopupQueue.PRIORITY_ORDER delivers `incoming_proposal_popup` ABOVE `incoming_settlement_offer_popup` (backend/models/cooldown_manager.py:158-159, verified by opening) while DialogueManager.DIALOGUE_PRIORITY ranks a settlement offer (2) ABOVE a proposal (3) (backend/models/dialogue_manager.py:185,191) and `_promote()` re-sorts the queue by that priority on every pop (dialogue_manager.py:779-793). A proposal arrives first (current, its popup payload written at ai_diplomacy.py:2058-2064 because `peek() is dialogue`), a settlement offer arrives second (queued, its popup pushed at turn_manager.py:621-623). Any preempt-then-pop in between — a Talleyrand `advisory` (assess), a CR-2 clarification, a delegation ASK, a hard stop — promotes the SETTLEMENT to active, but `_include_popup_passthroughs` (main.py:1594-1699) pops the PROPOSAL payload (main.py:1620) without checking it against the active dialogue's id. The W6-0 guard (diplomatic_executor.py:3404-3432) then correctly refuses the click as stale. Verified by running (scratch repro_desync.py): after arrivals active=incoming_proposal#1; after advisory preempt+pop active=incoming_settlement_offer#2 while the delivered popup is `{'from_nat…

**What the player sees.** The game itself puts Russia's envoy on screen; the player presses Reject (or Accept) and is told their answer was not delivered because 'this concerns Britain', then must answer Britain first and Russia re-appears afterwards. Measured 4 times in the 24-turn flagship: audit-flagship-mock/digest.md:129-135 (turn 9, Russia armistice #17 vs settlement #19), :226-231 (t14, Prussia #31 vs #33), :262-267 (t16, Britain #36 vs #39), :338-343 (t21, Prussia #51 vs #53) — every one the verbatim line `↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not del…

**Evidence.** cooldown_manager.py:145-163 PRIORITY_ORDER (proposal :158 above settlement :159); dialogue_manager.py:175-194 DIALOGUE_PRIORITY (settlement 2, proposal 3), :322-345 preempt, :347-353 pop→_promote, :779-793 _promote re-sort; main.py:1620 pop_highest delivered unconditionally, :1666-1685 safety valve gated on `winner_attr is None`; ai_diplomacy.py:2043-2064 popup written only while current; turn_manager.py:619-623 settlement popup push; diplomatic_executor.py:3404-3432 stale refusal. Digest lines cited above. Runtime repro output quoted in summary.

**Reproduce.** python snippet: TestClient(/new_game); dm=world.dialogue_manager; dm.push(incoming_proposal dict for Russia with popup_payload); world.incoming_proposal_popup=copy(payload); dm.push(incoming_settlement_offer dict for Britain); world._popup_queue.push('incoming_settlement_offer_popup', payload); dm.preempt({'type':'advisory',...}); dm.pop(); resp={}; main._include_popup_passthroughs(resp, world) → resp['incoming_proposal']['dialogue_id']==1 while dm.peek()['dialogue_id']==2; executor.handle_diplo…

**Fix shape (one seam).** ONE seam, `_include_popup_passthroughs` (backend/main.py:1620-1640): after `pop_highest`, if `winner_key in ('incoming_proposal','incoming_settlement_offer')` and `winner_value.get('dialogue_id')` differs from `world.dialogue_manager.peek().get('dialogue_id')`, push the winner back (`world._popup_queue.push(winner_attr, winner_value)`) and instead deliver the popup derived from the ACTIVE dialogue — `_build_pending_envoy_popup_from_dialogue` (main.py:4374) for proposals, `build_incoming_settlement_offer_popup` (the /pending_envoy arm, main.py:4460-4467) for settlement offers. Do not touch DialogueManager priorities or the W6-0 guard.

**Behaviour test.** tests/test_response_pipeline.py: push proposal A then settlement B on a boot world (popups queued as the producers do), `dm.preempt(advisory)`, `dm.pop()`, then `_include_popup_passthroughs(resp, world)`; assert the ONE non-None envoy key carries `dialogue_id == dm.peek()['dialogue_id']`, and `handle_diplomatic_dialogue_response('reject', gs, dialo…

#### FA-29 [P2 · defect] Shipped build: when the server is down the menu and the in-game connection failure tell the stranger to run a Python command that does not exist in the zip

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `godot-client/project-sovereign/scripts/main_menu.gd:527`
**Already filed:** ROADMAP row 10 remainder names 'honest boot screen' (owned, not built); EAS-3 (FIXED Aug 3) fixed only the dev spelling of the same string. NEW: the exact shipped strings, the README contradiction, and the pin at test_main_menu_and_ux_pass.py:129 that blocks a naive fix.

**What it is.** main_menu.gd:527 status line: 'The war office does not answer — start the backend: .venv\Scripts\python.exe -m backend.main'; main.gd:745: 'Start the Python server: python -m backend.main'; main_menu.gd:346 version line 'Ink & Iron — development build'. No script anywhere branches on OS.has_feature('editor'/'template') (grep across main_menu.gd/main.gd/utils.gd/settings_panel.gd/api_client.gd: zero hits), so the exported client shows the developer command verbatim. README_TESTER.txt:207-209 promises the opposite: 'The main menu names the launch command when the server is down; use launch.bat rather than starting the exe alone'. The dev string is pinned by tests/test_main_menu_and_ux_pass.py:129 (`assert "-m backend.main" in gd`), so a naive rewrite reds the suite — the fix must branch, not replace.

**What the player sees.** The most likely ten-minute failure for a stranger — double-clicking InkAndIron.exe instead of launch.bat, or the server window dying — ends on a screen that says '.venv\Scripts\python.exe -m backend.main' and 'development build'. They have no Python and no .venv; the README told them the menu would name the launcher.

**Evidence.** Verified by opening: godot-client/project-sovereign/scripts/main_menu.gd:527, :346; scripts/main.gd:744-745; deploy/README_TESTER.txt:207-209; tests/test_main_menu_and_ux_pass.py:129. Verified by running: grep -rn 'has_feature|is_debug_build' over the five client scripts returns nothing.

**Reproduce.** Export the client (export_presets.cfg preset 0), run InkAndIron.exe with no server on 8005: the footer reads the .venv command; or in the editor, run main_menu.tscn with the backend stopped.

**Fix shape (one seam).** ONE seam: a Utils.launch_hint() static that returns the dev command under OS.has_feature('editor') and 'Close this window and double-click launch.bat (the server window must stay open)' on export templates; both main_menu.gd:527 and main.gd:745 read it; the version line reads a build tag. Keep the dev string so test_main_menu_and_ux_pass.py:129 holds, and add the template arm to the same pin.

**Behaviour test.** tests/test_main_menu_and_ux_pass.py: assert utils.gd contains both strings and that main_menu.gd/main.gd no longer embed '-m backend.main' directly (only via Utils.launch_hint); a headless SceneTree check (tools/godot_parse_check.gd pattern) that Utils.launch_hint() under a stubbed has_feature('template') contains 'launch.bat'.

#### FA-30 [P2 · defect] The /command question-bearing early returns still DRAIN the PopupQueue into a response the client renders only one route of — deferred one-shot popups are destroyed, petitions delayed, and the question itself can go unrendered

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/main.py:3028`
**Already filed:** IGR-X7 (FIXED July 31, 2026 — capture arms only) and the Aug-2026 health-check's five non-draining endpoints; PC15-10 B0 F7 covered /load, /strategic_response, /mailbox/activate. The objection/charge/clarification/interrupt/dialogue early returns of /command are not covered by any row (grepped BUG_F…

**What it is.** `_build_result_response(result, world)` drains by default (main.py:462-500) and is used unchanged on the /command early returns for a tactical objection (main.py:3028), strategic objection (:3032), clarification (:3044), glorious charge (:3051), strategic interrupt (:3059), diplomatic dialogue (:3075), the typed interrupt route (:2263) and /marshal_petition_response (:3203). Only the capture arm was converted to `drain_popups=False` (:3068, IGR-X7). On the client, `_on_command_result` returns at the FIRST matching route: pre-HUD objection/glorious-charge routes at main.gd:2492 (`_show_objection_dialog` main.gd:3945 reads no popup key — grep verified), post-HUD table at main.gd:1924-1937 with `marshal_petition` idx 2 ahead of `proposal_confirm` idx 6, `clarification` idx 7, `interrupt` idx 8, returning at main.gd:2514. Verified by running: (a) repro_objdrain.py — a queued `diplomatic_sabotage_popup` was delivered INSIDE Bernadotte's objection response (`state awaiting_player_choice`, `diplomatic_sabotage` non-None), the queue was empty afterwards and the key was None on `/respond_to_objection` and on the next `/command`; (b) repro_stack2.py — 'propose peace with Austria' with a queu…

**What the player sees.** Every choice popup deferred behind the enemy phase (main.py:1353-1362) rides the FIRST command of the next turn. When that command draws an objection — the commonest first-command outcome (audit-flagship-mock:8, :179, :207; audit-tutorial:15) — the popped popup vanishes: a sabotage discovery or rebellion-imminent card is never seen (its hybrid dialogue stays answerable only by typed 'confront'/'overlook' words the player was never shown), and a marshal petition is silently pushed to next turn. When the first command instead raises a wizard step or a 'Which marshal?' question while a petition i…

**Evidence.** main.py:462-500 (_build_result_response default drain), :3028/:3032/:3044/:3051/:3059/:3075/:2263/:3203 (draining early returns), :3068 (the one converted arm), :1509-1533 (_fill_popup_keys_without_draining ready-made), :1353-1362 (enemy-phase deferral makes the first command the delivery slot); main.gd:1924-1937 route table, :2492 pre-HUD return, :2514 post-HUD return, :3945 _show_objection_dialog; jealousy.py:3174-3175 petition re-push. Runtime outputs: 'OD … diplomatic_sabotage delivered in the OBJECTION response: True / still queued after: False / after trust: None / next command: None'; '…

**Reproduce.** TestClient(/new_game); world._popup_queue.push('diplomatic_sabotage_popup', {...}); POST /command 'Bernadotte, attack Brunswick' (Bernadotte at Franconia objects: too strong) → response carries state=awaiting_player_choice AND diplomatic_sabotage; world._popup_queue.get('diplomatic_sabotage_popup') is None; POST /respond_to_objection trust → no popup; POST /command status → no popup. In-game: any turn whose deferred popup is a sabotage discovery, then open the turn with an order the marshal obje…

**Fix shape (one seam).** ONE seam: pass `drain_popups=False` on every question-bearing /command early return in main.py (:3028, :3032, :3044, :3051, :3059, :3075, :2263) exactly as :3068 already does — the queued popup then rides the next ordinary response, after the question is answered. (Do not fix it client-side by re-running routes: the popup is already popped server-side.)

**Behaviour test.** tests/test_response_pipeline.py: (1) queue a `diplomatic_sabotage_popup`, POST a command that raises a tactical objection; assert the objection response has `diplomatic_sabotage is None` and the queue still holds it; answer 'trust'; POST any command; assert the popup is delivered there. (2) Same with `pending_marshal_petition` and a command that re…

#### FA-31 [P2 · defect] The Grand Diversion is quoted blind: by the time the camp is staged, a WON roll leaves London–Normandy SHUT

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/game_logic/naval.py:2091`
**Already filed:** WO-D3 (carried design row — 'naval a strategy or a wall'). NEW and narrower: a measured, deterministic window-ratio mechanism absent from NV-D1..D9 and from the §14/§15 landing records (which measured only the boot 1.07/0.74/0.53 shape).

**What it is.** `crossing_check` during a window uses coverage×0.5 against floor 0.9 (naval.py:958ff). At boot the pooled Combined Fleet (France 31.5 + Spain + Holland = 53.8) against the RN's halved 55.2 gives 0.97 → OPEN. But staging the camp takes ≥4 turns of marching, and four turns of blockade rot (−5/turn, naval.py:1573) drop France/Spain/Holland to readiness 50: pooled 41.3 vs 55.2 = 0.75 → SHUT even inside the window. Nothing computes this: `diversion_terms` (naval.py:2091) are three booleans (fleet / at war / not yet spent), the chip note (naval.py:2293) says '45% — and once only', and the typed confirm (naval_executor.py:518-527) quotes the roll and the failure readiness. The 45% is not the chance of an open strait.

**What the player sees.** In audit-naval the player did exactly what the surfaces suggest — built ships turns 1–4, ordered the diversion turn 5 — and had the roll succeeded, Ney/Davout/Soult at Normandy would still have been refused at 0.75; the once-per-war card was spent (it failed, costing 24 sail) on a window that could not have opened. The Descent's marquee arc is dead on the natural timing and the player is never told why.

**Evidence.** Verified by running on the 1805 boot: crossing_check France Normandy→London: no window ratio 0.54 SHUT; window_turns=2 + derive_ai_postures → coverage 55.2, mover 53.8, ratio 0.97 verdict=window (OPEN); with France 49@50, Spain readiness 50, Holland readiness 50 (the digest's turn-5 state, reproduced by the fold+rot arithmetic 70→69→64→63→58→58→53→50) + window → 41.3/55.2 = 0.75 verdict=shut. `build_admiralty_report(w)['diversion_terms']` = [fleet in commission, at war with a naval power, diversion not yet spent] — no ratio term. Verified by opening naval.py:958-1030 (floor/window arms), :2091…

**Reproduce.** python -c: w=from_scenario(europe_1805.json); fr=naval.get_fleet(w,'France'); fr['ships']=49; fr['readiness']=50; naval.get_fleet(w,'Spain')['readiness']=50; naval.get_fleet(w,'Holland')['readiness']=50; fr['window_turns']=2; naval.derive_ai_postures(w); print(naval.crossing_check(w,'France','Normandy','London')) → ratio 0.75, allowed False, verdict shut. In-game: build ships turns 1-4, order the diversion on turn 5.

**Fix shape (one seam).** Add ONE pure forecast `naval.window_forecast(world, actor, link)` (the `blockade_forecast` idiom: evaluate `crossing_check` with the actor's window flag forced and the island fleet's derived-guard posture, on a copy of the two records, never mutating) and make it a fourth `diversion_terms` row — '+ a success would open London–Normandy (41.3 vs 55.2 needs 0.9)' / 'x even a success leaves it shut — recover readiness first' — read by the Admiralty terms, the chip note and the typed confirm alike.

**Behaviour test.** test_diversion_forecast_matches_live_window: at boot the forecast says OPEN with ratio == crossing_check(window_turns=2)['ratio'] (0.97); after four `_readiness_tick`s under the boot blockade it says SHUT (0.75) and the typed confirm message contains 'would not open'; then actually resolving a forced-success diversion yields the same verdict the fo…

#### FA-32 [P2 · defect] The W6-7 'Prisoners' dispatch line is built and never rendered — a captured marshal vanishes from every daily surface

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `godot-client/project-sovereign/scripts/main.gd:3295`

**What it is.** `build_morning_dispatch` emits `dispatch['prisoners']` (`dispatch.py:2080-2090`) and drops prisoners from the roster (`dispatch.py:2503-2506`, comment: 'they appear in the dispatch's Prisoners line instead'). Neither `main.gd._display_morning_dispatch` (`main.gd:3295-3540`) nor `dispatch_view.gd` reads a `prisoners` key (grep: only a comment at `main.gd:1608`); `notifications.py` has no capture type (grep 'captured|prisoner' → 0 hits) and `capture_marshal` adds no rail row (`world_state.py:4597-4652`). The only pin is backend-side (`tests/test_w6_marshal_fates.py:223-230`). Verified by running: after `capture_marshal(Ney,'Austria')` the same-turn headline is 'Sire — Marshal Ney has been taken. Austria holds him prisoner.'; two turns later the dispatch has headline None, Ney absent from `marshals`, and no 'Ney' anywhere in the payload except the unrendered key. Compounding it: the suggested-terms pipeline auto-inserts `prisoner_return` ONLY for a sovereign (`diplomatic_templates.py:3606-3608`), the wizard/dialogue has zero 'prisoner' hits, and the parser corpus has 0 'ransom' rows — a non-sovereign prisoner has no player-facing authoring route to the ransom W6-7 §9.2 promises.

**What the player sees.** In audit-flagship-mock Ney was taken at the end of turn 22 (digest line 358 last_stand → line 364 'Marshal Ney is a prisoner of Austria'); the next morning's dispatch led with Orleanais (line 378) and from then on the briefing, the rail and the campaign feed never mention him — the player learns he is missing when an order is refused. The Generals card is the only screen that says 'held prisoner' (`marshal_management.gd:556-558`).

**Evidence.** verified by opening backend/game_logic/dispatch.py:2080-2090 and :2500-2506; godot-client/project-sovereign/scripts/main.gd:3295-3330 and :3485-3525 (no prisoners key); backend/notifications.py:25-152 (type list, no capture type); backend/models/world_state.py:4597-4652; backend/game_logic/diplomatic_templates.py:3604-3620; docs/WAVE6_FUN_FACTOR_SPEC.md:233 (the promise); verified by running the capture→dispatch probe (output above); docs/audits/playtest_digests/audit-flagship-mock/digest.md:356-378.

**Reproduce.** .venv/Scripts/python.exe -c "from backend.models.world_state import WorldState; from backend.game_logic import dispatch as D; w=WorldState.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json'); w.capture_marshal(w.marshals['Ney'],'Austria','probe'); w.current_turn+=2; d=D.build_morning_dispatch(w); print(d.get('headline'), d.get('prisoners'), any(m['name']=='Ney' for m in d['marshals']))" → None, [{'name':'Ney','captor':'Austria',...}], False; then grep -n prisoners main.g…

**Fix shape (one seam).** ONE seam: render `data.get('prisoners', [])` in `_display_morning_dispatch` (and mirror in `dispatch_view.gd`) as a PRISONERS block under MARSHAL STATUS ('Ney — held by Austria since turn 22'). Separately worth a row: a standing `MARSHAL_CAPTURED` rail notification created in `capture_marshal` and dismissed in `release_captured_marshal` (`world_state.py:4691-4711`), whose CTA deep-links the F1 wizard with a `prisoner_return` demand for non-sovereigns.

**Behaviour test.** tests/test_w6_marshal_fates.py: a regex pin that `main.gd` and `dispatch_view.gd` reference `"prisoners"` (the XR-1/TUT-F1 regex idiom); plus a backend test that `capture_marshal` adds exactly one rail notification carrying `details.marshal` and that release dismisses it.

#### FA-33 [P2 · defect] The WIN-D3 road-home order loses its first turn, so a corps that marches home is warned 'no nearer home — 2 turns of safe passage left' every turn, the morning after the beat promised 7

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/game_logic/withdrawal.py:691`
**Already filed:** none in BUG_FIXES.md/DESIGN_REFINEMENT.md; WO-17 (FIXED) addressed the corridor's direction, not the lost first turn. WAR_WITHDRAWAL_SPEC §7a's walkthrough documents the T1/T2 number contradiction as accepted for a standing corps.

**What it is.** `_issue_road_home_orders` stamps the free MOVE_TO with `issued_turn=int(world.current_turn)` (withdrawal.py:691) but executes NO first step, while `process_strategic_orders` skips any order whose `issued_turn == world.current_turn` because 'first step already executed by executor.py' (strategic.py:260-264) — true for the executor's issuance (strategic_executor.py:1300+), false for the treaty's. `advance_turn` increments the turn (world_state.py:9388) and then ticks the corridor (:9789): expiry = t + dist + slack(3), so after the lost turn surplus = 2 = `EVACUATION_WARNING_MARGIN` (withdrawal.py:120, :797-800) and, because a steadily marching corps keeps its surplus constant by design, he is warned EVERY turn until home. Verified by running (probe F): peace France–Austria at turn 1 with Davout at Vienna → grant beat 'Berthier has given them the road home — Davout to Franche-Comte. They have safe passage for 7 turns while they march.'; same-turn strategic pass reports only 'Davout is marching to Franche-Comte (5 turn(s) remaining)' (skipped); tick turn 2 (still at Vienna): 'Davout is no nearer home — 4 march(es) still to go from Vienna, and 2 turn(s) of safe passage left before his c…

**What the player sees.** The dispatch says 'safe passage for 7 turns' and the very next morning 'no nearer home … 2 turns of safe passage left before his corps is interned' — then repeats it every turn while the corps IS marching home. The player either panics and re-issues a 2-AP order that changes nothing, or learns to ignore the internment warning, which is the one warning the design needs him to believe.

**Evidence.** verified by running scratchpad probe_lens.py probe F on the 1805 boot (set_diplomatic_state France/Austria PEACE, Davout at Vienna); verified by opening backend/game_logic/withdrawal.py:120, :543, :683-698, :797-800, :859; backend/commands/strategic.py:260-264; backend/models/world_state.py:9388, :9789; docs/WAR_WITHDRAWAL_SPEC.md:379-386; tests/test_win_d3_road_home.py:302-320

**Reproduce.** 1805 boot; dav=w.marshals['Davout']; dav.location='Vienna'; set_diplomatic_state(w,'France','Austria','PEACE') → dav.strategic_order MOVE_TO Franche-Comte issued_turn 1, grants {'Austria|France': 8}; StrategicOrderProcessor(executor).process_strategic_orders(w, gs) → 'active … (5 turn(s) remaining)' (no move); w.advance_turn() → w._last_tactical_events contains evacuation_lapsing '… 2 turn(s) of safe passage left' with Davout still at Vienna; repeat process+advance → the same warning while he cl…

**Fix shape (one seam).** ONE seam: `_issue_road_home_orders` — either execute the first hop at issuance the way the executor's issuance does (so the skip's premise holds) or stamp `issued_turn = current_turn - 1` so the same end turn's processor walks him; then the surplus a marching corps carries is the full slack (3) and the warning fires only for a genuine dawdler. Optionally make the beat and the warning quote the same quantity (turns of slack, not total passage).

**Behaviour test.** tests/test_win_d3_road_home.py: open a corridor via `set_diplomatic_state` for a corps with a walkable road home, run `StrategicOrderProcessor.process_strategic_orders` then `advance_turn` for N turns WITHOUT moving him by hand → zero `evacuation_lapsing` events for him and he arrives home; and the first tick's surplus equals `EVACUATION_SLACK_TURN…

#### FA-34 [P2 · defect] The combat_stalemate popup asks 'Continue move to?' and its 'Continue as Ordered' button cancels the order

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published PLAUSIBLE) · **Seam:** `backend/commands/strategic.py:817`

**What it is.** strategic.py:2961 builds the stalemate-interrupt message via `order.command_type.replace('_',' ').lower()` ("Continue move to?"), offering `["continue_order","hold_position","cancel_order"]` (options list at 2950/2962). `_respond_combat_stalemate` (strategic.py:812-865) makes ALL THREE options null `marshal.strategic_order` and end the march — `continue_order`/`attack_again` (817-826) does so at zero trust cost with the message "…cannot break through. Orders cancelled — awaiting new instructions," while `hold_position`/`cancel_order` do the same at −3 trust. The client (interrupt_popup.gd:27-30) labels `continue_order` "Continue as Ordered," so the one free-looking button is the one that silently cancels the standing order — confirmed independently by audit-naval/digest.md Turns 11→14 (Turn 11 answers `continue_order`; Turn 14's identical "march to London" command creates a fresh order rather than reporting "already carrying out that order," proving the prior march had been cancelled). This is not required for loop-prevention: `order.combat_attempts` + `_should_auto_attack` (strategic.py:2966-2982, six call sites, every personality) already gate re-attack on the same enemy independ…

**What the player sees.** Every button on the popup ends the march; two cost −3 trust and the one labelled 'Continue as Ordered' is the free one that also cancels — the player who wants the march to continue after an inconclusive battle cannot have it, and is told his marshal 'cannot break through' when he chose to press on.

**Evidence.** verified by running scratchpad probe_lens2.py (A2/A3); verified by opening backend/commands/strategic.py:812-865, :2937-2963, interrupt_popup.gd:22-36; digest line quoted verbatim from docs/audits/playtest_digests/audit-naval/digest.md Turn 11

**Reproduce.** Any standing MOVE_TO whose blocked-path auto-attack returns no victor (probe A: Ney at Normandy vs Moore at London under the RN, or any real inconclusive battle) → `process_strategic_orders` raises combat_stalemate; `StrategicOrderProcessor.handle_response('Ney','combat_stalemate','continue_order', w, gs)` → `order_cleared True`, `ney.strategic_order is None`.

**Fix shape (one seam).** ONE seam: `_respond_combat_stalemate` — `continue_order` keeps the order standing (the existing `combat_attempts`/`_should_auto_attack` guard at strategic.py:2966-2982 already stops a free re-attack and routes the next turn into the 'still blocks the path. Previous assault was inconclusive' ask), while `cancel_order` stays the cancel; build the message with `_strategic_command_flavor(order.command_type)` ('Continue his march?').

**Behaviour test.** tests/test_strategic_bugfixes.py: after a stalemate interrupt, answering `continue_order` leaves `marshal.strategic_order` standing, charges 0 trust and the message does not contain 'cancelled'; the next `process_strategic_orders` does not auto-attack the same enemy (loop guard) and asks with `combat_attempts > 0` copy; the stalemate message reads…

**Refuter (mechanism → CONFIRMED).** Opened every cited seam and it matches exactly. strategic.py:812-826 (`_respond_combat_stalemate`, `continue_order`/`attack_again` branch): sets `marshal.strategic_order = None`, clears holding state, returns "cannot break through... Orders cancelled — awaiting new instructions" with `trust_change: 0`; the sibling `hold_position`/`cancel_order` branches (827-861) also null the order at −3 trust each — all three buttons end the march, confirmed by reading the whole function, not just the cited li…

#### FA-35 [P2 · defect] The enemy AI is pinned on a doomed stub: P4 has no target-worth floor and the aggressive pick maximises the ratio, so three Austrian corps spent four turns killing 58 men while Paris stood empty

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/ai/enemy_ai.py:2739`
**Already filed:** WO-D1 (the whole army reinforces / battles are not decisions) is adjacent but does not cover the stub-pinning; XR-3/PC-1 are capture-copy rows. NEW.

**What it is.** P4 admits any enemy with `enemy.strength > 0` (enemy_ai.py:2739) and the aggressive pick is `max(attackable, key=ratio)` (:3017-3021); P0 forces an attack on the weakest co-located enemy whenever the ratio clears the threshold (:1615, :1674). A 702-man or 58-man corps therefore has the best ratio on the board and is attacked first, every action, by every co-located corps. Measured (verified by running the latewar reproduction and reading the saves): Charles 24,724 + John 7,058 + Mack 22,589 all stood ON Piedmont at turns 27-28 attacking Massena's 702→58 men (digest lines 112-115, 125: 'Archduke John (lost 0) vs Massena (lost 163)', 'Archduke Charles (lost 1) vs Massena (lost 58)'); only AFTER he was destroyed (turn 28) did John march — 'Archduke John has crossed into Paris. No French corps stands in his path' (digest line 135, turn 29). The casualty formula guarantees the stub survives: `_calculate_casualties` is proportional and capped at 60% (combat.py:1165-1170), and `take_casualties` only zeroes below 50 men (marshal.py:1425-1430), so a beaten corps decays geometrically (Lannes: 3673/2654/1056/496/382/158/69/31 across 8 attacks, flagship digest lines 214-217, 236-237, 251-252)…

**What the player sees.** The enemy army looks stupid and harmless at once: four enemy phases of 'Archduke Charles (lost 3) vs Massena (lost 41)' rows while the road to the capital is open, and the campaign log/battle count fills with skirmishes (15 'battles' in the late-war digest, 11 of them against Massena's remnant). AI aliveness reads as farce; France is spared an attack it should have received.

**Evidence.** enemy_ai.py:2739 (`enemy.strength > 0` — only floor), :3017-3021 (aggressive max-ratio pick), :1615/:1674 (P0 weakest-enemy attack), :2882-2898 (engagement rule: must attack same-region enemy first); combat.py:1165-1170 (rate cap 0.6, `max(1, …)`); marshal.py:1425-1430 (`< 50 → 0`); probe save t8/t9 (Charles/John/Mack all at Piedmont, Massena 702/58); audit-latewar-t20/digest.md lines 108-115, 122-125, 135; audit-flagship-mock/digest.md lines 210-217, 233-237, 248-255. Verified by opening/running.

**Reproduce.** Same driver reproduction as the P1 finding; read server_console.log for turns 26-28: every '[P0 ENGAGEMENT] … -> ATTACK Massena' line for Mack/ArchdukeJohn/ArchdukeCharles while Massena < 1,000; or in-process: place three at-war AI corps and a 500-man player corps in one region, run EnemyAI.process_nation_turn twice and count actions spent on the stub.

**Fix shape (one seam).** ONE seam: a shared target-worth predicate consulted by the P0 rung (:1615) and the P4 filter (:2739) — an enemy below a floor (e.g. < 1,000 men, the same floor war-score already uses at diplomacy.py:9418-9420) is not a battle target but a CAPTURE: the co-located corps secures the province (the existing `_attempt_region_capture`/capitulation path) and the rest of the nation's actions fall through to P4.5/P7. Pair with the P1 fix so the stub itself resolves to capture rather than standing.

**Behaviour test.** tests/test_enemy_ai_*: three at-war AI corps co-located with a 500-man player stub and an undefended player capital one hop away; assert the nation's action list contains at most ONE attack on the stub and at least one move/capture toward the capital; negative control with the stub at 15,000 keeps the current behaviour.

### 3c. Missing (7)

#### FA-38 [P2 · missing] Losing a satellite can never lead the briefing — three vassals lost in one morning were headlined by a province, and the archived digests cannot show it

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/game_logic/dispatch.py:119`
**Already filed:** WO-D6 (the `capital_lost` precedent — same shape, built at 100) · IGR-A A4 (STATUS.md:6256 — release copy only). NEW: no headline class for any involuntary vassal loss; enemy-elimination template reused for our own satellite.

**What it is.** The dispatch headline table has 26 `_add` classes (dispatch.py:100-160 weights; grep of `_add("` verified) and none is a vassal loss: defection, rebellion, transfer and elimination all ride the diplomatic rail only. In the deterministic ambient re-run of the archived audit-ambient40 board, world turn 29 lost KingdomOfItaly (eliminated), and Switzerland (bribed by Austria, `vassal_defected` outcome transfer) in ONE tick; the headline was 'Sire — Provence has fallen'. The elimination line for the player's OWN satellite reuses the enemy template 'KingdomOfItaly has been eliminated from the war.' (dispatch.py:4015).

**What the player sees.** The empire's client web can collapse without ever being the morning's lead; a player reading the headline (which is what the digest, the top bar and the enemy-phase close show first) learns of it only if they scroll the diplomatic rail. The archived audit-ambient40 digest prints headline-only, so its 40 turns contain zero mention of Switzerland/Holland/KingdomOfItaly (grep verified) despite all three being lost.

**Evidence.** Verified by running (scratch econ_probe2.py, driver reseed scheme, headlines byte-match the archived digest through turn 12): turn 29 EVENTS [nation_eliminated KingdomOfItaly], [vassal_transferred Switzerland], [vassal_defected Switzerland briber Austria outcome transfer]; RAIL ['KingdomOfItaly has been eliminated from the war.', "Switzerland passes from France's suzerainty to Austria's.", "THE DEFECTION: Austria's gold turns Switzerland against France."]; headline 'Sire — Provence has fallen. Enemy colours fly over French homeland soil.' Verified by opening: dispatch.py:100-160 (no vassal cla…

**Reproduce.** Run tools/playtest_driver.py --turns 14 --name probe --fresh from tests/fixtures/playtest_saves/fixture_t20_ambient.json is NOT enough (Switzerland already gone there); instead: from_scenario(europe_1805), set world.vassals['Holland']['loyalty']=30 and force a bribe via vassal.attempt_vassal_bribe(world,'Britain') with random patched to land, then build_morning_dispatch(world)['headline'] → not about Holland.

**Fix shape (one seam).** ONE seam: add a `vassal_lost` headline class in dispatch.py's weights table (between `region_lost` 75 and `own_broken` 90 — a satellite is worth more than a province) fed from the three producers' events (vassal_defected / vassal_rebellion / nation_eliminated-where-nation-was-our-vassal), with a template naming the cause ('Switzerland has gone over to Austria — bought') and a `nation_eliminated` arm that says 'our satellite' when the eliminated nation had lord == player.

**Behaviour test.** Build a world where a French vassal defects (patch random in attempt_vassal_bribe) on a turn that also loses one ordinary province; assert build_morning_dispatch(world)['headline'] names the vassal, not the province; and assert the template for an eliminated player-vassal contains 'our' / 'satellite'.

#### FA-42 [P2 · missing] The tutorial's promised 'trust branch pivot' does not exist: step VII asserts 'Kienmayer's screen still stands' for two turns after he is a prisoner

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `godot-client/project-sovereign/scripts/tutorial_overlay.gd:112`
**Already filed:** TUT-F4c (FIXED — the overdue line, which fires only from gate+1); PC15-9 (FIXED — widened beat VI only). The pivot itself is promised in TUTORIAL_SCRIPT.md and unowned.

**What it is.** docs/TUTORIAL_SCRIPT.md:343 promises 'Trust branch = Ney attacks early and the next card pivots'. tutorial_overlay.gd STEPS has no such arm: `first_battle` (:112-115, turn_gate 4) always renders 'Kienmayer's screen still stands across the Rhine…' with the chip `Ney, attack Kienmayer`, and `_maybe_catch_up` (:365-371) releases a stuck step only at gate+2. The card names `trust` FIRST among the three answers (:93). Under trust, Ney attacks and captures Kienmayer on T2 (archived digest :14-23), so on T4 the card teaches a refused order and the 'overdue' line (TUT-F4c) only appears from T5. The TUTORIAL_SCRIPT.md table is also stale against the STEPS (rows :344-345 say First blood T3 / guns T4; the overlay gates VI at 2 and VII at 4).

**What the player sees.** A player who takes the card's first option sees Berthier insist an enemy 'still stands' whom the same morning's dispatch reported captured, clicks the quill, and is told 'Unknown target: Kienmayer'; the school then sits on that page until turn 6.

**Evidence.** Verified by opening: tutorial_overlay.gd:93, :112-115, :341-347 (`observe` advances one step), :365-371; docs/TUTORIAL_SCRIPT.md:343-345. Verbatim archived lines: audit-tutorial/digest.md:14-17 ('Ney, defend' -> objection -> trust -> Ney vs Kienmayer battle), :23 ('he is our prisoner'), :26 ('Ney, attack Kienmayer -> Unknown target: Kienmayer').

**Reproduce.** Launch the School of War, at step V type `trust` (Ney attacks and captures Kienmayer), end turn twice, read step VII's card and click its chip.

**Fix shape (one seam).** ONE seam: the `first_battle` step gets a branch keyed on a new latch `_kienmayer_gone` (set in `_note_observations` when a battle_report/conquest names Kienmayer as the beaten side or a dispatch event of type capture names him) — body/chip re-target to Jellacic ('the screen is taken; the Tyrol pass is next: Ney, attack Jellacic') and `_pred_battle_happened` accepts that battle; regenerate the TUTORIAL_SCRIPT.md table from STEPS.

**Behaviour test.** tests/test_tutorial_position7.py: regex-extract STEPS and assert `first_battle` carries a second suggest for the trust branch that mock-parses (T-B1 idiom); plus a driver-level pin: tutorial_lesson under `--objection trust` for 6 turns has zero refused chip commands.

#### FA-43 [P2 · missing] The zip ships CC-BY assets without THIRD_PARTY_LICENSES.md — both in-game credit surfaces point the player at a file that is not in the build

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `deploy/build.bat:61`
**Already filed:** ROADMAP row 10 (the shippable build) owns packaging but its remainder list (fresh export, JSONs in the .pck, LLM touchpoints, supervision, clean-machine run) does not name the license file.

**What it is.** build.bat:52-61 copies exactly three files into deploy/dist/ink_iron_server (config.txt, launch.bat, README_TESTER.txt); ink_iron.spec datas add only the three map JSONs (:134-139). THIRD_PARTY_LICENSES.md (repo root, 16,254 bytes) is never copied. Yet settings_panel.gd:309-312 credits 'Unit icons by Lorc, Delapouite & contributors (game-icons.net, CC BY 3.0) ... Musket volley: aaronsiler & Benboncan (CC BY 4.0) ... Full terms: THIRD_PARTY_LICENSES.md' and README_TESTER.txt:246-247 says 'see THIRD_PARTY_LICENSES.md in the source tree'. CC BY requires the attribution + license notice to travel with the distribution; the tester zip is a distribution.

**What the player sees.** A tester (or a Steam reviewer) opening Settings → CREDITS is pointed at a file that does not exist in what they received; the project's own license discipline (THIRD_PARTY_LICENSES.md is otherwise meticulous) breaks at the last step, the packaging.

**Evidence.** Verified by opening: deploy/build.bat:49-61 (three copy lines, no licenses); deploy/ink_iron.spec:124-140 (datas = uvicorn/fastapi/starlette + three JSONs); godot-client/project-sovereign/scripts/settings_panel.gd:305-316; deploy/README_TESTER.txt:243-247; ls -la THIRD_PARTY_LICENSES.md (present at repo root, not in deploy/dist_template). Verified by running: ls deploy/dist/ink_iron_server shows no licenses file in the existing March build either.

**Reproduce.** Run deploy\build.bat (or read it): the output folder contains config.txt, launch.bat, README_TESTER.txt, the server, and (after export) the client — no THIRD_PARTY_LICENSES.md; open Settings → CREDITS in the exported client and look for the named file.

**Fix shape (one seam).** ONE seam: build.bat gains `copy /y "THIRD_PARTY_LICENSES.md" "deploy\dist\ink_iron_server\THIRD_PARTY_LICENSES.md"` beside the README copy, and README_TESTER.txt:247 drops 'in the source tree' for 'in this folder'.

**Behaviour test.** tests/test_prebuild_fixes_2026_08_14.py: extend test_build_bat_demands_fresh_export_and_mock_smoke with `assert 'THIRD_PARTY_LICENSES.md' in build_bat` and assert README no longer says 'source tree'.

#### FA-71 [P3 · missing] Administrative role is a one-way door: the promised 'future restoration' exists only as a debug cheat — an unowned GR9 deferral inside player-facing copy

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published AUTHOR_VERIFIED) · **Seam:** `backend/commands/disobedience.py:1512`
**Already filed:** WO-36 drive-by fixed the CLIENT echo of `administrative_role`; nothing owns the restoration verb.

**What it is.** The redemption arm's description promises 'Troops frozen for future restoration' (disobedience.py:1512) and its handler comments 'Store data for future restoration (Phase 4)' (disobedience.py:1698); the marshal's strength goes to 0 and location to None (1701-1704). Verified by grepping: the ONLY write of `marshal.administrative = False` in backend/ is meta_executor.py:1541, inside `_execute_debug` (function head at meta_executor.py:742, the next `def` is `_execute_cheat` at 2256) — a debug-mode-only branch. No parser verb, executor action, corpus row, or DESIGN_REFINEMENT/ROADMAP/FUTURE_DESIGN row owns the restoration (grep 'future restoration|administrative staff|Transfer .* to Staff' across the four docs: zero hits).

**What the player sees.** A player who chooses 'Transfer to Staff' to save a broken marshal loses that corps (e.g. 20,000 men) for the rest of the campaign; the +1 action/turn is permanent but the promised way back never arrives, and the roster shows a marshal at strength 0 with no order that can reach him.

**Evidence.** verified by opening disobedience.py:1503-1530 and 1690-1720, meta_executor.py:742, 1533-1560, 2256; verified by running `grep -rn 'administrative = False' backend/ --include=*.py` (one hit) and the four-doc grep (no hits).

**Reproduce.** ev=w.disobedience_system.check_redemption_threshold(m,w) after m.trust.set(15); w.disobedience_system.handle_redemption_response(ev,'administrative_role',{'world':w}); print(m.administrative, m.strength, m.administrative_strength) # True 0 <old strength> Then try any typed order for him through /command with DEBUG_MODE off — nothing restores him.

**Fix shape (one seam).** Either (a) ONE new admin action `recall_marshal` (1 admin AP, at the capital) mirroring the debug branch meta_executor.py:1536-1560 (restore `administrative_strength` at `administrative_location`/capital, decrement `bonus_actions`, recompute max actions) wired through the 12-step new-action checklist, or (b) delete the promise from the copy at disobedience.py:1512 and 1698 and state that the transfer is permanent — and file the owner row either way (Golden Rule 9).

**Behaviour test.** tests/test_recall_from_staff.py: after `administrative_role`, the typed recall returns him at his frozen strength and `world.calculate_max_actions()` drops by exactly 1; refusal when AP is short; the debug branch stays byte-identical. Or, for (b): the option `description` contains 'permanent' and never 'restoration'.

**Author note.** HV-33 the administrative role has no player road back

#### FA-80 [P3 · missing] Mock-default vocabulary refuses the plainest hold/move phrasings and verb typos, and every refusal suggests attacking an ALLY ("Perhaps: 'Ney, attack Deroy'")

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published PLAUSIBLE) · **Seam:** `backend/ai/llm_client.py:899`
**Already filed:** NP-X9 (inflection tolerance → CR-6 proper, BUG_FIXES.md:809) is adjacent; stay/remain, verb typos and the ally suggestion are unfiled

**What it is.** In mock mode (no LLM fallback) the keyword chain (backend/ai/llm_client.py:1440-1620) has no stay/remain/rest keyword for hold or wait, no generic verb-typo tolerance (only four hard-coded 'build' misspellings at :1610 and ad hoc scout typos), and is missing 'advance on / push on to / onward to' move forms even though 'advance to' works — verified by direct reproduction of all eleven listed phrasings against the real 1805 boot world via TestClient, every one refused as 'Unknown action.' Separately, Berthier's mock recovery template (backend/ai/llm_client.py:897-899, `_berthier_mock_response`) picks its example enemy as `list(game_state['enemies'].keys())[0]`; `game_state['enemies']` is built in `get_llm_game_state()` (backend/main.py:211, dict at :236-244) filtered only by fog visibility (PARTIAL+), never by `is_at_war` — confirmed by opening `WorldState.get_enemy_marshals()` (backend/models/world_state.py:3543-3548), which excludes only the player's own nation, versus the unused `get_hostile_marshals()` (:3556) which does filter by war. On the shipped 1805 boot, `get_enemy_marshals()[0]` is Deroy of Bavaria — France's ALLIANCE partner, `is_at_war(France, Bavaria)` is False — repro…

**What the player sees.** Verified by running: `Ney, stay put`, `Ney, stay where you are`, `Ney, remain in Rhineland`, `Ney, don't move`, `Ney, rest your men`, `Soult, atack Mack`, `Ney, attak the austrians`, `Ney, advance on Swabia`, `Ney, push on to Munich`, `Ney, onward to Munich`, `Ney, forward!`, `Ney, take Swabia`, `ask Austria for a ceasefire` → all 'Unknown action'; the recovery copy reads "Perhaps: 'Ney, attack Deroy' or 'Ney, move to Paris'?" — and `Ney, attack Deroy` is itself refused: "Ney cannot attack Bavaria — they are our ally, Sire" (verified by running). Refusing is better than guessing, but the first…

**Evidence.** verified by opening backend/ai/llm_client.py:897-899 and :1475-1500 (wait/hold arms), :1500-1530 (move list), :1610; backend/main.py:237; verified by running the /command probes on the 1805 boot.

**Reproduce.** POST /command {"command":"Ney, stay put"} → 'Unknown action' with 'Perhaps: Ney, attack Deroy'; then {"command":"Ney, attack Deroy"} → 'they are our ally'.

**Fix shape (one seam).** Three small arms, one file: (a) add `stay|remain|stay put|don't move|rest` → hold/wait and `advance on|push on to|onward to|forward to <region>` → move to the chain; (b) an edit-distance-1 pass over the verb keyword set for a single unknown token (reuse parser `_edit_distance_at_most`); (c) `generate_berthier_recovery` picks its example enemy as the first entry whose nation `world.is_at_war_with(player)` (fall back to the strongest visible belligerent).

**Behaviour test.** each listed phrasing resolves to the intended action with the right marshal; `Soult, atack Mack` → attack; the recovery text never names a marshal of a non-belligerent nation (Deroy at boot) — pinned against the live `enemies` payload.

**Refuter (mechanism → CONFIRMED).** Every mechanism claim was independently reproduced. (1) grep of llm_client.py for 'stay'/'remain' returns zero keyword matches (only comments) — confirmed by opening the hold/wait branches at llm_client.py:1479-1489 (hold family: 'hold at all costs'...'guard'...'protect') and :1470-1473 (wait family: 'wait'/'stand by'/'pass'); no stay/remain form anywhere. (2) grep for edit_distance/fuzzy/levenshtein/typo in llm_client.py shows no generic verb-typo pass; the only misspelling handling is the four…

#### FA-81 [P3 · missing] README and the School never mention the embodied Emperor — the tester meets an eighth French piece called Napoleon that nothing teaches

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published PLAUSIBLE) · **Seam:** `deploy/README_TESTER.txt:100`
**Already filed:** ROADMAP row 10 owns README_TESTER.txt (rewritten before NP); DESIGN_REFINEMENT 'Pre-EA Onboarding & Teaching Pass' owns teaching content; neither names the Emperor. Victory (ROADMAP 12-13 'The Emperor's Designs') is a known deferral and is not this.

**What it is.** README_TESTER.txt:100 ('Seven marshals stand ready in the east') and the YOUR MARSHALS block :103-130 list only the 7 non-sovereign French marshals; the 1805 boot has 8 (verified live: Ney/Davout/Soult/Lannes/Murat/Bernadotte/Massena + ('Napoleon','Lorraine','sovereign')). README_TESTER.txt's last edit (5b37de07, 2026-08-15 00:11:36) predates NP-0 landing that same day (bb849b20, 17:20:42) and has not been touched since. TUTORIAL_SCRIPT.md has zero Napoleon/Emperor content despite its own Update Policy (:28, 'Adding 3-5 table rows when a feature ships'), and NAPOLEON_SPEC.md:216 confirms the tutorial scenario is deliberately sovereign-free. Not covered by any open row in BUG_FIXES.md or DESIGN_REFINEMENT.md's Pre-EA Onboarding row. Additional finding: an existing test, tests/test_prebuild_fixes_2026_08_14.py:241 test_current_roster_present, hardcodes the stale 7-marshal tuple and passes despite the gap — the recommended behaviour test should strengthen this test in place (derive the roster from europe_1805.json) rather than add a duplicate.

**What the player sees.** A Round-0 tester sees a piece named Napoleon beside Soult, does not know he can be marched (or captured), does not know why battles near him go better, and the README they were told to read says there are seven marshals.

**Evidence.** Verified by opening: deploy/README_TESTER.txt:6, :100-130 (no Napoleon entry); docs/TUTORIAL_SCRIPT.md (grep -i 'napoleon|emperor|guard' matches nothing relevant); docs/NAPOLEON_SPEC.md:61 ('the tester README opens "You are Napoleon."' cited as prior intent, no README task), :216 ('The tutorial scenario is untouched (no sovereign)'). Verified by running: WorldState.from_scenario(europe_1805.json) → French marshals = 8: Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena, ('Napoleon','Lorraine','sovereign').

**Reproduce.** Boot the default 1805 campaign and press G: eight cards, the last 'Napoleon'; open README_TESTER.txt: 'Seven marshals', no Napoleon paragraph.

**Fix shape (one seam).** ONE seam: README_TESTER.txt YOUR MARSHALS gains a THE EMPEROR paragraph (he marches like a marshal, never objects, the Guard is his, capture ends wars on the enemy's terms, Paris +1 DP when he sits) and 'Seven' → 'Seven marshals and the Emperor himself'; TUTORIAL_SCRIPT.md gains the NP inventory rows so the Pre-EA Onboarding pass can build the beat.

**Behaviour test.** tests/test_prebuild_fixes_2026_08_14.py::test_current_roster_present: derive the French roster from europe_1805.json at test time and assert every name (incl. 'Napoleon') appears in README_TESTER.txt; a TUTORIAL_SCRIPT.md pin that a row mentions 'sovereign' or 'Napoleon'.

**Refuter (mechanism → CONFIRMED).** Reproduced every load-bearing claim myself. (1) Ran WorldState.from_scenario on the shipped europe_1805.json: French roster is exactly 8 marshals — Ney/Davout/Soult/Lannes/Murat/Bernadotte/Massena (7) plus ('Napoleon','Lorraine','sovereign') as the 8th, appended last (dict-insertion order matches the repro's 'last card' claim). (2) Opened deploy/README_TESTER.txt:100 verbatim: 'Seven marshals stand ready in the east', and the YOUR MARSHALS block :103-130 lists exactly those seven combat marshals…

#### FA-82 [P3 · missing] Skip or Conclude latches the School of War off forever; the menu button then boots a silent, card-less Danube scenario

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `godot-client/project-sovereign/scripts/main_menu.gd:409`
**Already filed:** none found (grep BUG_FIXES/DESIGN_REFINEMENT for 'tutorial_done'/'Skip' returns nothing).

**What it is.** `_conclude` writes `UiSettings.set_tutorial_done(true)` (tutorial_overlay.gd:452; ui_settings.gd:109-115, per-machine cfg) and `on_world_swap` disarms whenever the latch is set (:280). No surface ever writes false (grep: the only setter call is :452), and `_on_tutorial_pressed` (main_menu.gd:409-419) still launches the scenario without touching the latch.

**What the player sees.** A tester who clicks Skip -> Confirm by mistake (or finishes once and wants to show a friend) picks 'The School of War' again and gets the Danube map with no Berthier card and no explanation — the lesson looks broken.

**Evidence.** Verified by opening: tutorial_overlay.gd:275-292 and :448-455, ui_settings.gd:105-115, main_menu.gd:409-419; grep of scripts/*.gd shows `set_tutorial_done(` called only at tutorial_overlay.gd:452.

**Reproduce.** Start the School, click Skip -> Confirm, return to the main menu, click 'The School of War' again.

**Fix shape (one seam).** ONE line: `_launch('tutorial')` (or `_on_tutorial_pressed`) calls `UiSettings.set_tutorial_done(false)` — choosing the School is the consent; keep the latch only for the plain-entry/Continue arms.

**Behaviour test.** Parse-harness regex pin that main_menu.gd's tutorial launch path calls `set_tutorial_done(false)`; manual: the repro above shows step I again.

### 3d. Tie-ins — what would make the systems cohere (routed FA-D) (7)

#### FA-D1 [P2 · tie_in] 'The interior is restless' fires on every fresh conquest (capture sets stability 25) and taxes the whole chest without naming the province

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/models/world_state.py:5399`
**Already filed:** CA9 §Q3 'Should conquest pay?' (BUG_FIXES.md:1468, design question) · N19 (requisitions). NEW: the capture-baseline → unrest-term interaction and its un-attributed rendering.

**What it is.** capture_region sets stability = 25 (world_state.py:3877); get_state_charges_rate flags `restless_interior` (+75 rate) when ANY held province sits at/below CHARGES_UNREST_STABILITY 50 (world_state.py:5395-5410, :260). Growth is +5/turn (+10 with a marshal present, :6329-6332), so every conquest opens 3-6 turns of +75 rate on the entire treasury above 2,000. Measured: at a 20,000 chest taking Tyrol raised the Charges of Empire 576 → 1,116 (+540/turn) while the province yielded 0 and billed 75 occupation. The term carries no region (:5407-5409 dict has only key/label/amount) and strategic_ledger.gd:455-460 renders labels only.

**What the player sees.** The turn the player takes a province, Net falls by ~500-700g with the ledger saying only 'the interior is restless +75'. The visible cost of the conquest is the 75g occupation line; the invisible one is ~7x larger and cannot be traced to the province. In the ambient probe the same term flipped on at turn 12 when an autonomous attack took one province (charges 1,489 → 2,268).

**Evidence.** Verified by running: from_scenario(europe_1805); nation_gold['France']=20000; charges rate 80 / charge 576 → capture_region('Tyrol','France') → stability 25, rate 155, charge 1116, terms [crown 30, war_establishment 50, restless_interior 75], occupation line 75, effective income 0; 6 turns to clear without a garrison, 3 with. Verified by opening: world_state.py:3861 ('Sets stability to 25'), :5395-5410, :6329-6332, :255-260; docs/audits/ECON_BALANCE_GATE_2026_08_07.md:75 defines the term as 'stability ≤ 50' with no fresh-conquest discussion; tests/test_econ_war_coupling.py:325-335 pins only a…

**Reproduce.** .venv/Scripts/python.exe -c "import os;os.environ['LLM_MODE']='mock';from backend.models.world_state import WorldState;w=WorldState.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json');w.nation_gold['France']=20000;print(w.calculate_state_charges('France'));w.capture_region('Tyrol','France');print(w.calculate_state_charges('France'), w.get_state_charges_rate('France')['terms'])" → 576 then 1116

**Fix shape (one seam).** ONE seam: get_state_charges_rate — collect the triggering region names while scanning (`restless_regions`) and put them on the term dict + label ('the interior is restless — Tyrol'); render in strategic_ledger.gd:455-460 and the end-turn banner. Design half for the EC-2 pass-2 gate: exempt provinces captured within the growth window (stability rising from the capture baseline), or count only homeland/settled provinces, so a conquest's cost is the occupation line the player can read.

**Behaviour test.** After capture_region of a stable enemy province, assert the restless_interior term dict carries that region's name and the ledger's state_charges_terms label contains it; a second test asserts the charge delta from ONE conquest at a 20,000 chest is reported (shown) as a named component and, if the exemption is adopted, that the term does not fire f…

#### FA-D2 [P2 · tie_in] A war purpose set against Austria ticks into the coalition war score but is invisible on the panel — the row resolves the objective through the LEADER pair only

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/game_logic/war_status.py:157`

**What it is.** `calculate_side_war_score` sums the `ticking` component across EVERY opponent pair of a coalition war (`diplomacy.py:3259-3281`), but `build_active_wars` resolves the row's `objective`/`enemy_objective` through `diplo_key = _make_diplo_key(france, opponent)` where `opponent` is the coalition leader (`war_status.py:56`, `:157`). Verified by running: `set war purpose` vs Austria → `war_objectives == {'Austria|France': ['France']}` and the row still shows `objective None`; vs Britain (the leader) → `objective {'type':'conquest','target_regions':['London'],...}` renders. So the only renderable French purpose in the 1805 coalition targets London — the province the Wooden Wall (A5) makes unreachable — while the historically correct aim (Vienna) is computed and hidden.

**What the player sees.** A player who does discover `set war purpose against Austria` (FA-D4) sees nothing change on the War Status panel: no Objective block, no Enemy Objective, no ticking progress line, even though the score is moving. Two implementations of 'which pair carries the war' disagree — the CA9 through-line (the executor computes one answer and the surface shows another).

**Evidence.** verified by running: after `ex._diplomatic._set_war_purpose_inner('Austria','conquest',w)` → `build_active_wars(w)['wars'][0]` has `opponent='Britain'`, `opponents=['Britain','Austria','Russia']`, `objective=None`; after `_set_war_purpose_inner('Britain','conquest',w)` → `objective={'type':'conquest','type_display':'Conquest','target_regions':['London'],'ticking_rate':2,'ticking_active':False}`. verified by opening: `backend/game_logic/war_status.py:56` (row diplo_key from the leader opponent), `:152-172` (objective block read from `world.war_objectives.get(diplo_key)`), `:237-238`; `backend/g…

**Reproduce.** cd repo; LLM_MODE=mock .venv/Scripts/python.exe -c "import os; os.environ.pop('SOVEREIGN_SCENARIO',None); from backend.models.world_state import WorldState; from backend.commands.executor import CommandExecutor; from backend.game_logic.war_status import build_active_wars; w=WorldState.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json'); ex=CommandExecutor(); ex._diplomatic._set_war_purpose_inner('Austria','conquest',w); print(w.war_objectives.keys(), build_active_wars(w)…

**Fix shape (one seam).** ONE seam: `war_status.py:152-172` — for a coalition row, walk `row['opponents']` (the pair set the score already sums) and take the first non-concluded player objective, labelling the court it targets (`objective['against']`), and likewise the first enemy objective; single-opponent rows reduce byte-identically. `war_detail_popup.gd:395-407` renders the extra 'against <court>' word.

**Behaviour test.** `tests/test_war_status_coalition_objective.py`: on the 1805 boot, set purpose vs Austria → `wars[0]['objective']['target_regions'] == ['Vienna']` and `objective['against'] == 'Austria'`; set vs Britain → unchanged from today; a bilateral (single-opponent) war row is byte-identical to the current payload.

#### FA-D3 [P2 · tie_in] An ordinary captured marshal is priced at the peace table and applied by a ratified clause, but no producer ever puts him on it — only a sovereign is

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published AUTHOR_VERIFIED) · **Seam:** `backend/game_logic/diplomatic_templates.py:3607`
**Already filed:** EWC-D3 (P3, 'captured-marshal ransom' as a future ransom-demand EVENT at a diplomacy/drama gate) and NP-X2 (prisoner rescue). NEW here: the terms/pricing/apply chain already exists and only the producer is sovereign-gated — a one-line widening, no event system needed.

**What it is.** The `prisoner_return` clause is complete end to end: registered (`diplomacy.py:246`, `:327`), priced per held marshal at 500g / 800g for a major's marshal at the gold-lump rate (`diplomacy.py:7266-7281`), applied on ratification (`world_state.py:10633-10645`) and auto-returned at peace. But the ONLY producer is the NP-4 Brétigny arm in `generate_suggested_terms` (`diplomatic_templates.py:3598-3620`), which `continue`s past every marshal that is not `is_sovereign`. Verified by running: with `ArchdukeJohn.captured_by='France'`, `generate_suggested_terms('Austria','peace',w)` carries zero `prisoner_return` clauses; grep finds no other `"prisoner_return"` producer in `backend/` or `godot-client/`. In the flagship digest France holds Archduke John from t9 (line 147) to the end and Ney is Austria's prisoner from t22 (line 364) — 15 turns of leverage the formula would pay for and no surface ever offers.

**What the player sees.** Capturing an enemy commander (the game's own headline: 'their order of battle is one commander shorter') changes nothing at the negotiating table; a captured French marshal's card says only 'held prisoner — his rewards await his release' (`marshal_management.gd:558`) with no route named. The player's one move is full peace, which returns everyone for free — so the prisoner is neither a bargaining chip nor a cost, and the W6-7 fate machinery's drama has no payoff before the war ends.

**Evidence.** verified by running: probe on the 1805 boot — `m=w.marshals['ArchdukeJohn']; m.captured_by='France'; m.strength=0; m.location='Paris'; generate_suggested_terms('Austria','peace',w)` → no `prisoner_return` in `demands` or `sweeteners`. verified by opening: `backend/game_logic/diplomatic_templates.py:3598-3620` (`if not getattr(_held,'is_sovereign',False): continue`); `backend/game_logic/diplomacy.py:7266-7281` (ransom_worth 500/800/SOVEREIGN for ANY `held`); `backend/game_logic/diplomacy.py:327`; `backend/models/world_state.py:10633-10645`; `godot-client/project-sovereign/scripts/marshal_manage…

**Reproduce.** cd repo; .venv/Scripts/python.exe -c "import os; os.environ.pop('SOVEREIGN_SCENARIO',None); from backend.models.world_state import WorldState; from backend.game_logic.diplomatic_templates import generate_suggested_terms; w=WorldState.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json'); m=w.marshals['ArchdukeJohn']; m.captured_by='France'; m.strength=0; m.location='Paris'; t=generate_suggested_terms('Austria','peace',w); print([c for k in ('demands','sweeteners') for c in…

**Fix shape (one seam).** ONE seam: the loop at `diplomatic_templates.py:3607` — drop the sovereign gate and insert a `prisoner_return` for every held marshal of the two courts (sovereign FIRST, then majors' marshals, then the rest, so the Brétigny ordering pin holds); the acceptance formula already prices each one. Optionally mirror in the AI's incoming-offer generator so Austria asks for John back. No new state, no new clause type, no `.gd` change (the clause already renders via `display_names.py:330`).

**Behaviour test.** `tests/test_prisoner_return_producer.py`: (1) with an ordinary Austrian marshal captured by France, `generate_suggested_terms('Austria','peace',w)['sweeteners']` contains `{'type':'prisoner_return','marshal':'ArchdukeJohn'}`; (2) with a French marshal captured by Austria it appears under `demands`; (3) the sovereign still comes first when both are…

**Author note.** HV-36 only a sovereign's captivity reaches the peace table

#### FA-D4 [P2 · tie_in] The campaign's spine war has no purpose — the shipped War Purpose machinery is never staged for the boot coalition war, and the only verb that could set one has no UI home and no counsel

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/models/world_state.py:8419`
**Already filed:** WIN-D1 / ROADMAP 12–13 (Victory & Objectives) own the campaign objective; this is narrower — it reuses the SHIPPED WPS dialogue on the boot war and adds nothing new. Not filed anywhere as such (grep 'war purpose' in DESIGN_REFINEMENT/BUG_FIXES: only the landed WPS rows and WO-4/WO-25 typed-route row…

**What it is.** WPS (war objectives + ticking 5th component + the Objective/Casus-belli block on the war-detail popup) is live for wars the player DECLARES, but `starting_wars` are seeded through `ensure_war_instance_for_pair` without ever calling `create_war_objective` or stamping `stated_reason`, so the Third Coalition — the war every 1805 campaign is about — boots with `world.war_objectives == {}`, `objective: None`, `enemy_objective: None`, `stated_reason: ''` and `ticking: 0` (verified by running `build_active_wars` on the 1805 boot). The player CAN repair this by typing `set war purpose against Austria` (0 AP, `world_state.py:944`; the dialogue opens and populates `war_objectives['Austria|France']` — verified by running through `CommandExecutor`), but `main.gd:1454-1457` keeps that typed route alive precisely BECAUSE it has 'NO wizard/panel home' (comment at `main.gd:1751`), the help text never mentions it (grep of `meta_executor.py` for 'war purpose' returns nothing), the corpus has one row (`parser_golden_corpus.json:2907`), and no dispatch/Talleyrand rung suggests it. Cheaper and earlier than Victory (ROADMAP 12–13, WIN-D1): zero new mechanics, one loader seam.

**What the player sees.** For 24 turns the War Status panel of the campaign's only war shows no objective, no enemy objective and no casus belli (the popup renders those blocks only when present, `war_detail_popup.gd:395-421`), the war score has no ticking component toward anything, and 'what would winning look like' is never stated. In the flagship digest the player asks `Talleyrand, request terms from Austria` at t15 (line 245) for a war that has no declared aim on either side; Austria's `redeem_italy` design is active but the boot war carries no stated reason while an AI-declared war would (`war_council.py:578`).

**Evidence.** verified by running: `WorldState.from_scenario(europe_1805.json)` → `world.war_objectives == {}`; `build_active_wars(w)['wars'][0]` → `objective None`, `enemy_objective None`, `stated_reason ''`, breakdown `ticking 0`. verified by opening: `backend/models/world_state.py:8419-8440` (starting_wars loader — only `ensure_war_instance_for_pair`, no objective; `grep create_war_objective settlement_helpers.py` → none); `backend/game_logic/diplomacy.py:3880-3899` (`_auto_assign_defense_objective` reached only from `declare_war`); `backend/commands/diplomatic_executor.py:2463-2510` (`_set_war_purpose_i…

**Reproduce.** cd repo; .venv/Scripts/python.exe -c "import os; os.environ.pop('SOVEREIGN_SCENARIO',None); from backend.models.world_state import WorldState; from backend.game_logic.war_status import build_active_wars; w=WorldState.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json'); r=build_active_wars(w)['wars'][0]; print(w.war_objectives, r['objective'], r['enemy_objective'], repr(r['stated_reason']), r['breakdown'].get('ticking'))" → `{} None None '' 0`. In the client: open the War…

**Fix shape (one seam).** ONE seam: the `starting_wars` loader at `world_state.py:8419-8440`. For each entry, (a) when the player is a belligerent, stage the existing `war_purpose_selection` dialogue on turn 1 by calling `_set_war_purpose_inner(target, '', world)`'s open_flow path (the client already renders it via `proposal_confirm_popup.gd:1277`), and give the AI belligerents `_auto_assign_defense_objective`; (b) stamp `war_instances[...]['stated_reason']` from each AI belligerent's active agenda `want_title` (the `war_council.py:578` idiom) or an optional authored `reason` key on the starting_wars entry (`MODDING_FORMAT.md:79`, validator `modding/validator.py:1516`). Do NOT build a France deck — that stays Victory…

**Behaviour test.** `tests/test_boot_war_purpose.py`: (1) on the 1805 boot the dialogue manager's head is `war_purpose_selection` naming the coalition war, and answering Conquest makes `build_active_wars(w)['wars'][0]['objective']` non-None with `type == 'conquest'`; (2) after N turns holding the objective's target regions, `breakdown['ticking'] > 0`; (3) `stated_reas…

#### FA-D5 [P2 · tie_in] The redemption audience cannot address its own cause: no arm settles an unpaid expectation, and 'grant autonomy' (+40) is eroded back below 20 in 7 turns

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/commands/disobedience.py:1490`
**Already filed:** WO-41 / WO-36 (redemption DELIVERY, FIXED) and PT-F6 (the <40 warning copy) are adjacent; no row joins redemption to the dotation shortfall.

**What it is.** `_get_available_redemption_options` (disobedience.py:1490-1530) offers only grant_autonomy / administrative_role / dismiss and the event message reads 'trust in you has broken completely. The relationship must be addressed.' (disobedience.py:1561-1564) — it never reads `dotation.get_shortfall` and never offers the rente that `rente_action_keys` (dotation.py:1042) already knows how to build for the rail. Verified by running: after the erosion probe drove Lannes to 0, simulating the spectacular autonomy outcome (`trust.modify(+40)`, turn_manager.py:811) put him at 40 and the unpaid 120g shortfall (3 pts/turn) returned him to 19 in 7 turns; `redemption_cooldown_until = turn + 5` (disobedience.py:1667) then re-arms the same three-way question. The two grievance systems compute the same man's loyalty and neither reads the other at the decision point.

**What the player sees.** The player is handed the game's gravest marshal decision (dismiss him permanently, shelve him, or release him for three turns) about a cause the card never names and none of the arms can fix; the 'right' answer — pay him — is on a different screen. Choosing autonomy replays the audience within ~12 turns; choosing dismiss deletes a marshal whose only fault was an unpaid estate.

**Evidence.** verified by opening disobedience.py:1490-1564, 1640-1670 (cooldown), 1670-1700 (grant_autonomy sets autonomy_turns=3), turn_manager.py:790-830 (+40/+25/+15/+5 arms), dotation.py:1042-1110 (`rente_action_keys` — a one-line rente command already exists for the rail); verified by running scratchpad/probe_erosion.py: 'after autonomy spectacular +40: 40' / 'turns to fall back to <=20 with the shortfall unpaid: 7 trust 19'.

**Reproduce.** w=WorldState.from_scenario(<europe_1805.json>); m=w.marshals['Lannes']; m.battles_won=3; m.trust.set(15) ev=w.disobedience_system.check_redemption_threshold(m,w); print([o['id'] for o in ev['options']], ev['message']) # ['grant_autonomy','administrative_role','dismiss'] — shortfall 120 unmentioned w.disobedience_system.handle_redemption_response(ev,'grant_autonomy',{'world':w}); m.trust.modify(40) for t in range(7): w.current_turn+=1; w._process_dotation_state() print(m.trust.value) # 19

**Fix shape (one seam).** ONE seam: `_get_available_redemption_options` — when `dotation.is_dotation_world(world)` and `dotation.get_shortfall(marshal, world) > 0` and `not dotation.rente_grant_would_not_help(marshal, world)`, prepend a `settle_account` arm whose detail quotes `build_rente_offer` (face + treasury cost) and whose handler in `handle_redemption_response` dispatches the same `{'action':'grant_pension','marshal':name}` dict the UX23-A rail and the AI rung send (GR5, shared executor); and make the event `message` state the shortfall when one exists.

**Behaviour test.** tests/test_redemption_names_its_cause.py: marshal at trust 15 with shortfall 120 -> event carries `settle_account` quoting the rente face; answering it sets `pension`, clears `redemption_pending`, and 10 further `_process_dotation_state` ticks leave trust unchanged; a marshal at trust 15 with NO shortfall gets the unchanged three arms (pin the lega…

#### FA-D6 [P2 · tie_in] The treaty's road-home order is abandoned by the cannon-fire redirect and never re-issued — a stranded corps wanders and is interned

**Verdict:** VERIFIED — Sept 2 verification (confidence high; the audit published AUTHOR_VERIFIED) · **Seam:** `backend/commands/strategic.py:2262`
**Already filed:** WIN-D3 (built, DESIGN_REFINEMENT.md:360) and WO-17 (FIXED) own the corridor; neither covers the interrupt interaction. Unfiled.

**What it is.** WIN-D3 hands every stranded corps an ordinary MOVE_TO (withdrawal.py:654-704, `original_command == ROAD_HOME_COMMAND`). It is an ordinary order to the interrupt system too: `_check_interrupts` (backend/commands/strategic.py:2247-2296) has no `is_road_home_order` exemption and no belligerent filter, and the aggressive redirect (:2298-2307) sets `marshal.strategic_order = None` and marches him toward ANY battle within 2 provinces. The WO-17 direction term (withdrawal.py:141-192, keyed on `is_stranded_at`) admits any step by a corps stranded where it stands, so the 'rush' can go DEEPER into the partner's territory. The corridor tick `process_evacuation_grants` (:719-830) warns and interns but never calls `_issue_road_home_orders` again. The AI's corps are immune (P1.2 recomputes `next_step_home` each turn, :624-651) — the asymmetry is against the player.

**What the player sees.** Verified by running (probe_strategic3.py R): Lannes stranded at Volhynia, peace with Russia → road-home MOVE_TO Franche-Comte (7 marches, grant expiry 11). A Prussia-vs-Russia battle at Estonia (both at PEACE with France): 'Lannes hears cannon fire! Abandoning orders — rushing to Estonia! Lannes moves from Volhynia to White Russia (180 lost to march)'; order None; +1 'Lannes is no nearer home — 8 march(es) still to go from White Russia, and 1 turn(s) of safe passage left'; +2 '0 turn(s)'; +3 'Lannes's corps failed to quit Russia soil before its safe passage expired. It has been disarmed and in…

**Evidence.** Verified by opening strategic.py:2247-2307 (no road-home check; order nulled at :2307), withdrawal.py:141-192, :624-651, :654-704, :719-830 (no re-issue), :844-890 (warn/intern). Verified by running probe R — output quoted above verbatim.

**Reproduce.** Boot 1805; set `w.regions['Volhynia'].controller='France'`; park other French marshals at Paris and Russians at their capital; `lannes.location='Volhynia'`; `set_diplomatic_state(w,'France','Russia','WAR')` then `'PEACE'` (issues the road-home order); `lannes.strategic_order.issued_turn -= 1`; `w.record_battle('Estonia','Hohenlohe','Kutuzov','victory')`; `process_strategic_orders` → order None, Lannes at White Russia; then `W.process_evacuation_grants(w)` per turn → interned at +3.

**Fix shape (one seam).** ONE seam: in `_check_interrupts` (strategic.py:2262, beside the literal exemption) `if is_road_home_order(marshal.strategic_order): return None` — the treaty's road is literal by nature. (Belt: have `process_evacuation_grants` re-issue via `_issue_road_home_orders` for an order-less stranded PLAYER corps, so a player-cancelled road is offered again rather than silently lapsing.)

**Behaviour test.** tests: stranded aggressive player marshal with the road-home order + a third-party battle within 2 → after `process_strategic_orders` the order still stands (`is_road_home_order`), the marshal moved one province HOMEWARD, no `cannon_fire` report; corridor tick over `expiry` turns produces no `evacuation_lapsing`/`marshal_interned` event.

**Author note.** HV-32 cannon fire is nation-blind

#### FA-D7 [P2 · tie_in] `propose peace with X` ignores the coalition's settlement offer already on the desk that covers X — drafts, estimates and charges 3 DP while `request terms` refuses for exactly that reason

**Verdict:** NARROWED — Sept 2 verification (confidence high; the audit published UNVERIFIED) · **Seam:** `backend/game_logic/diplomatic_dialogue.py:858`

**What it is.** `evaluate_request_terms_affordance` returns `offer_already_pending` and the typed route answers 'Their terms are already on the desk, Sire — answer the offer in the mailbox' (settlement_routes.py:318-325; display_names.py:877-884; audit-latewar-t20 T21 verbatim). The bilateral `proposal_confirm` mount (diplomatic_dialogue.py:760-898) checks cooldowns, DP, the ratify gate and the alliance paradox but never `_settlement_offer_already_pending` for the war covering the target, and the send gate (diplomatic_executor.py:680-696, 3919-3936) doesn't either — so with Britain's settlement offer covering Austria current since turn 3, 'propose peace with Austria' at turn 15 mounted at 40% COUNTER_OFFER, confirmed, and spent 3 DP (probe: DP 5 → 2).

**What the player sees.** Two verbs for 'end this war' disagree: one tells the player the answer is in the mailbox, the other takes their DP and sends Talleyrand to Vienna for a bilateral treaty the coalition's own offer already covers. Under the driver's propose policy this cost 3 DP on 12 of 22 turns; a human doing the same is never pointed at the mailbox.

**Evidence.** verified by running: scratchpad probe_counter.py — `[loaded] CURRENT=incoming_settlement_offer#11 (turn 3, covers Britain, Austria, Russia)`; `propose: True | dtype proposal_confirm #25 | est 40 COUNTER_OFFER | block: ''`; confirm → `Talleyrand departs… (3 DP spent)`, `DP=2`. verified by opening: backend/game_logic/settlement_routes.py:318-325; backend/display_names.py:877-884; backend/game_logic/diplomatic_dialogue.py:760-898 (no pending-offer check); backend/commands/diplomatic_executor.py:680-696, 3919-3936. Digest: docs/audits/playtest_digests/audit-latewar-t20/digest.md T21 `Talleyrand, r…

**Reproduce.** Seed historical: /new_game, end turn ×3 (Britain's settlement offer covering Austria arrives), then POST /command 'propose peace with Austria' → dialogue mounts with execute_proposal enabled and no mention of the offer; confirm → 3 DP deducted.

**Fix shape (one seam).** ONE seam: at the `proposal_confirm` mount (diplomatic_dialogue.py ~858, beside the paradox block) call `_settlement_offer_already_pending(world.pending_settlement_dialogues, war_id=<war covering target>)` / the dialogue-manager equivalent and, when true, disable `execute_proposal` with the same `offer_already_pending` copy the request-terms route uses (honest availability, WIN-1 pattern).

**Behaviour test.** With an `incoming_settlement_offer` current whose `covered_enemy_participants` includes Austria, build the peace `proposal_confirm` for Austria; assert the `execute_proposal` option has `enabled False` and its reason contains 'already on the desk', and that confirming does not change `world.diplomatic_points`.

### 3e. Tie-ins — P3/P4 (19)

**FA-D8 [P3 · tie_in] 'Gascony has fallen' names no lever while the game has one: an unopposed march captures a homeland province instantly and only a >= 5,000 garrison detachment makes the AI stop**  
`backend/game_logic/dispatch.py:273` · NARROWED (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
CONFIRMED mechanism: an unfortified province is captured instantly (combat_executor.py:8287 `_attempt_region_capture`, instant-capture branch at :8328-8330), the AI's march-capture rung already refuses a target with `garrison_strength >= 5000` OR any nonzero `garrison_detachment` (enemy_ai.py ~:3449-3453 — the detachment check makes the counter cheaper than stated), and the player's `garrison` command (economy_executor.py:940-953) is that lever. `home_captured`'s template (dispatch.py:273, sole…  
*Repro:* Load fixture_t20_ambient.json, end turn once: Paget's three captures arrive with the bare home_captured headline; then type 'Ney, garrison' in a province adjacent to Paget and end turn — the AI's P4.5 skips it.  
*Fix:* ONE seam: the `home_captured` template (dispatch.py:273) gains a lever clause built the way VS-1's recovery_hint is — name the enemy corps' strength (fog-banded) and the two counters ('a 5,000-man garrison holds a province against a march; a corps standing there forces a battle').  
*Test:* tests/test_dispatch_*: the home_captured headline for a province lost to an unopposed march contains the word 'garrison'; a province lost by battle keeps the current sentence.

**FA-D9 [P3 · tie_in] A corps can stand at morale 0 for eight turns with no cue to the remedy — and then breaks at first contact**  
`backend/game_logic/dispatch.py:1690` · NARROWED (Sept 2 verification), was PLAUSIBLE (one refuter)  
A player-standing corps parked at morale 0 gets the same toothless dispatch line every turn forever, with no auto-recovery and no named remedy. Verified: marshal.py has no per-turn morale regen (only combat.py:704/716 victory bonus and world_state.py:4503-4515 _apply_drill_morale restore it — plus a third, narrower path, backend/ai/feedback.py:126-150's live-mode-only strategic-order bonus, which never fires for an idle/unaddressed marshal). A victor is never routed by the fight he wins (combat.…  
*Repro:* json.load(fixture_t20_ambient.json)['world_state']['marshals']['Massena'] → morale 0, strength 21067, retreating False; end three turns with no orders and re-read: unchanged.  
*Fix:* ONE seam: dispatch.py:1690-1691 appends the lever ('— two turns of drill would steady them' or, with a training ground present, the +15 figure) using the same constants the drill executor applies, shown = applied.  
*Test:* tests/test_dispatch_*: a standing player marshal with morale < 40 and no drill state produces a status line containing 'drill'; one already drilling does not.

**FA-D10 [P3 · tie_in] Ally standing rows (contribution_share) live only in the HUD hover tooltip; the War Detail screen never shows them**  
`godot-client/project-sovereign/scripts/war_detail_popup.gd:349` · NARROWED (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
war_status.py:241-247 (not 244-249) ships contribution_share/contribution_overflow_count/standing_status_display on every war row; war_status_panel.gd:302-341 (_build_war_tooltip, wired at line 242 as row_btn.tooltip_text) is the ONLY reader; war_detail_popup.gd's _render_war_detail (line 350), which receives the identical war_data dict via show_war() at line 91, never reads these keys despite docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md §16.2 explicitly listing "contribution shares" as requir…  
*Repro:* Boot 1805, hover the Third Coalition HUD row → tooltip lists 'Standing (top 5)' with five courts; click it → War Detail shows score breakdown, objective, duration, fleet, recent battles — no standing block.  
*Fix:* ONE seam: war_detail_popup.gd `_render_war_detail` — add a 'Standing' block built from `contribution_share`/`standing_status_display`, extracting the tooltip's row formatter into a shared Utils helper so both surfaces read the same rows.  
*Test:* .gd regex pin that war_detail_popup.gd reads 'contribution_share' inside `_render_war_detail`; backend pin already exists for the producer cap (WAR_SETTLEMENT_ALLY_PARTICIPATION §16.2).

**FA-D11 [P3 · tie_in] Balance of Europe computes the threat projection (wars until a coalition brews/instant-forms) and never shows it**  
`godot-client/project-sovereign/scripts/diplomatic_ledger.gd:846` · VERIFIED (Sept 2 verification), was PLAUSIBLE (one refuter)  
diplomatic_ledger.py:1041 (war_exhaustion_trend build), :1061-1074 (threat_projection dict, matches coalition.py:41-42 THREAT_BREWING_MIN=60/THREAT_INSTANT_MIN=80), and :1115 (dissolution_threat_threshold, not :1096-1103 as originally cited) build threat_projection/wars_until_brewing/wars_until_instant/war_exhaustion_trend/hegemony_band/power_basis and a duplicate top-level coalition_posture key that godot-client/project-sovereign/scripts/diplomatic_ledger.gd's _render_balance_of_europe() (func…  
*Repro:* Open the Diplomatic Ledger (D) → Balance of Europe tab on any 1805 campaign; compare with `curl :8005/diplomatic_ledger | jq .balance_of_europe.threat_projection` — the payload carries wars_until_brewing/wars_until_instant, the tab does not.  
*Fix:* ONE seam: diplomatic_ledger.gd `_render_balance_of_europe`, after the threat bar (~:846): one line from `threat_projection` ('Next war of conquest: 47 → 67 · brews at 60 (1 war away) · forms at once at 80 (2) · dissolves below 20') and a ▲/▼/– glyph from `war_exhaustion_trend` beside each member's WE bar. Before rendering `after_next_war`, confirm the +20 literal at diplomatic_…  
*Test:* Backend pin: `build_diplomatic_ledger(world)['balance_of_europe']['threat_projection']['wars_until_brewing'] == max(0, ceil((60-threat)/20))` and `brewing_threshold == coalition.THREAT_BREWING_MIN`; c…

**FA-D12 [P3 · tie_in] No headline class for the player's OWN peace — the war's end leads the briefing only when a corps happens to be stranded**  
`backend/game_logic/dispatch.py:806` · VERIFIED (Sept 2 verification), was PLAUSIBLE (one refuter)  
CONFIRMED and strengthened. `_build_headline`'s event-window loop (backend/game_logic/dispatch.py:429-1050ish, scanning `world.event_log`) has no `elif etype == ...` branch for `diplomatic_treaty_signed`, `peace_ratified`, or `armistice_expired_peace` — verified by reading the whole loop (region_captured/nation_eliminated/marshal_captured/marshal_destroyed/retreat/battle/war_declaration/evacuation_granted/evacuation_lapsing/crisis_brewing/crisis_passed/third_party_peace/coalition_formed are the…  
*Repro:* Drive `tools/playtest_driver.py --turns 14 --diplomacy propose --fresh --name probe-narration` and compare the turn after 'has accepted our Peace Treaty' in digest.md: the DISPATCH line is a province/supply line, never a peace line, unless a French corps was o…  
*Fix:* ONE seam — `_build_headline`: raise a `peace_signed` class (weight ≈70, the mirror of `war_touches_us`) from the same `peace_ratification_log` entry `_build_peace_settlement_section` already reads (dispatch.py:3661-3672) or the treaty event, when the pair includes the player and the new state is PEACE/ARMISTICE; let `road_home` absorb it by identity when both exist.  
*Test:* tests/test_dispatch_headline.py: ratify a bilateral PEACE with no French corps abroad and no other events → `_build_headline` returns class `peace_signed` naming the counterpart; with a stranded corps…

**FA-D13 [P3 · tie_in] No per-corps march cadence: one AI corps captures three homeland provinces per enemy phase while the player's own standing march moves one**  
`backend/ai/enemy_ai.py:1039` · DUPLICATE (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
DUPLICATE-ADJACENT to PT-D4 (`DESIGN_REFINEMENT.md`, LANDED Aug 1 2026, `backend/main.py:1020 _collapse_enemy_move_chains`): P4.5's undefended-capture chain (enemy_ai.py:1039 round-robin loop → `_find_undefended_capture` enemy_ai.py:3380, single-hop scan of `adjacent_regions`, returns `{"action":"attack",...}` at :3498; prose at combat_executor.py:5034 inside `_execute_attack` def :4112) is mechanically confirmed and reproducible (player chain of 3 tactical `move`s costs AP 4→1 with no per-hop c…  
*Repro:* 1805 boot; run('Ney, move to Lorraine'); run('Ney, move to Franche-Comte'); run('Ney, move to Lorraine') → all success, actions_remaining 4→1. AI side: tools/playtest_driver.py --from-save tests/fixtures/playtest_saves/fixture_t20_ambient.json --turns 3 reprod…  
*Fix:* A design ruling, then ONE seam either way: (a) cap tactical relocations per marshal per turn at `movement_range` in `_execute_move` and the unopposed-attack arm using the existing `acted_this_turn`/`moved_this_turn` flags (both sides inherit, P4.5 falls through to the next marshal); or (b) extend `occupation_started` (the fortified-province cadence at combat_executor.py:5037) t…  
*Test:* tests/test_enemy_ai_*: an AI nation with 4 AP and one corps adjacent to three undefended enemy provinces ends its phase having captured at most `movement_range` of them; player mirror: the third chain…

**FA-D14 [P3 · tie_in] One corps flips a homeland province per AP with no resistance — Paget's 3-province walks are the game's capture cadence, symmetric for the player**  
`backend/commands/combat_executor.py:8313` · DUPLICATE (Sept 2 verification), was UNVERIFIED (refuter budget exhausted; the finder's own cited evidence stands)  
An `attack` on an empty at-war province is `move_to` + instant `_attempt_region_capture` (backend/commands/combat_executor.py:5006-5051; :8306-8330 — instant unless a `fortification` building), costing 1 AP and ~1% march attrition. The enemy AI's P4.5 (`_find_undefended_capture`, enemy_ai.py:3380-3470) is re-evaluated every action of the nation's 4-AP loop (:945, :1039-1215) whose `sort_key` (:1409-1418) is fairness-only — no per-marshal cap — so Britain's single continental corps spends all fou…  
*Repro:* Boot 1805; `lannes=w.get_marshal('Lannes'); lannes.location='Franconia'`; type 'Lannes, attack Bohemia', answer secure/respect, then 'attack Hungary', 'attack Moravia', 'attack Ukraine' → four provinces change hands in one turn. AI mirror: `--from-save tests/f…  
*Fix:* A design ruling first, then ONE seam: `_attempt_region_capture` (combat_executor.py:8313-8326) already owns a 1–2-turn occupation timer for fortified provinces; key that same timer on a high-stability province (`region.stability >= 76` is already 'friendly stable' at movement_executor.py:75-78) or on homeland/capital-adjacent soil, so a stable province takes a turn to fall (bot…  
*Test:* tests (after the ruling): a corps attacking an empty stability-80 enemy province gets `occupation_started` (1 turn) rather than an instant flip, for the player AND for an AI marshal through the shared…

**FA-D15 [P3 · tie_in] Settlement-unavailable reason is computed for the War Detail row and never rendered — 'Open Settlement' just vanishes**  
`godot-client/project-sovereign/scripts/war_detail_popup.gd:108` · VERIFIED (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
war_status.py:250-264 attaches settlement_eligibility/settlement_disabled_reason/settlement_disabled_reason_display/war_detail_actionability to every war row, and no .gd file (0 of 55) reads any of them; war_detail_popup.gd:108-109's `if settlement_available: _add_settlement_button(...)` has no else, so the button silently vanishes with no rendered reason (confirmed against the Request Terms disabled+tooltip idiom at :556-569, which the settlement button lacks). BUT the reason this fires is neve…  
*Repro:* In a coalition war, open the settlement review for war A (proposal_confirm popup mounted), then open War Detail for a second settlement-tier war B: no Open Settlement button and no reason; backend `build_active_wars(world)['wars'][i]['settlement_disabled_reaso…  
*Fix:* ONE seam: war_detail_popup.gd `show_war` — in the else-branch of :108, when `settlement_tier_display` is non-empty (settlement-tier war) render a disabled 'Open Settlement' button whose tooltip_text is `settlement_disabled_reason_display` (the :561-567 Request Terms idiom); keep bilateral codes (`one_to_one_war`, `not_at_war`) absent since Negotiate is their route.  
*Test:* Backend: `build_active_wars` on a coalition war with an active settlement dialogue → row.settlement_available False and settlement_disabled_reason_display == 'Resolve the current settlement review fir…

**FA-D16 [P3 · tie_in] The 15,000 lift makes the Emperor's Guard the only French expedition corps — and the Marshalate, the real road, is never named**  
`backend/game_logic/naval.py:597` · NARROWED (Sept 2 verification), was UNVERIFIED (refuter budget exhausted; the finder's own cited evidence stands)  
At boot every French corps but Napoleon (10,000) exceeds the lift, so `over_lift_refusal` (naval.py:597 `eligible`) says 'Send a corps of 15,000 or fewer instead — Napoleon stands at 10,000' and the Admiralty expedition term (naval.py:2157-2168) says 'march Napoleon (10,000) to a yard'; the comment at :2160 promises the copy 'says plainly when the only one is the sovereign' but no code does, and the executor has no sovereign gate. Meanwhile `recruit_marshal` fields a 5,000-man corps (recruitment…  
*Repro:* python -c: w=from_scenario(...); print(naval.over_lift_refusal(w, w.get_marshal('Soult'))); print(naval.build_admiralty_report(w)['expedition_terms'])  
*Fix:* In the ONE builder both surfaces read (`over_lift_refusal` and the `_under` list feeding term 2), exclude `personality == sovereign` from the offered corps and append the commission road from `recruitment.first_affordable_commission(world, nation)` ('commission Mortier — 5,000 men for 4,000g — and march him to Brittany'); optionally the same helper on the Generals bench chip ('…  
*Test:* test_expedition_counsel_names_the_marshalate_not_the_emperor: at boot the over-lift refusal and expedition term never name Napoleon, and name the cheapest affordable bench marshal with '5,000'; with a…

**FA-D17 [P3 · tie_in] The alliance-paradox block names a route France cannot execute and omits the one the executor exempts; the Cabinet's 'Propose Peace' row stays green while its send is structurally blocked**  
`backend/game_logic/diplomatic_dialogue.py:870` · NARROWED (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
CONFIRMED core mechanism, NARROWED framing: propose_peace never appears as a wizard action while state=="WAR" (diplomacy.py:10987 shows propose_armistice is the ONLY proposal row added in that branch; verified by running get_available_diplomatic_actions on the 1805 boot). The real gap is one state later: once the player follows the game's own counsel and signs an ARMISTICE (Bavaria remaining allied to France and at war with Austria), get_available_diplomatic_actions's `elif state == "ARMISTICE":…  
*Repro:* 1805 boot; `propose peace with Austria` (or Cabinet → Austria → Propose Peace): the mount dialogue's `commitment_block_warning` names the settlement table and 'resolve Bavaria's war first' but not the armistice; `GET /diplomatic_preview?nation=Austria` → the `…  
*Fix:* ONE seam: the block-text builder at diplomatic_dialogue.py:868-873 — name the armistice explicitly ('propose an armistice — a truce carries no contradiction, and its expiry makes the peace — or settle jointly at the table') and drop the non-executable 'resolve X's war first'. Companion (same discipline as the settlement row): `_proposal_action('propose_peace')` marks the row un…  
*Test:* tests/test_bph_c_fallout_conflicts.py: with Bavaria allied to France and at WAR with Austria, the peace mount's `commitment_block_warning` contains 'armistice'; `get_diplomatic_preview(world,'Austria'…

**FA-D18 [P3 · tie_in] The armistice preview promises a peace the thaw arithmetic cannot deliver: from the boot relations a single 5-turn truce always collapses back into war**  
`backend/game_logic/diplomacy.py:4370` · NARROWED (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
backend/game_logic/diplomacy.py:4368-4410 (build_war_context_snapshot's armistice_mechanics block) AND backend/game_logic/war_status.py:373-374 (armistice_projected_outcome, feeding war_status_panel.gd:359 / war_detail_popup.gd:511, the per-turn HUD) both project an armistice's outcome from relation_now >= ARMISTICE_AUTO_PEACE_RELATION alone, ignoring the turns remaining and the ARMISTICE_THAW_PER_TURN=3 thaw that runs every turn a truce is active (diplomacy.py:10411). Verified live: 3 turns int…  
*Repro:* Boot europe_1805.json; `build_war_context_snapshot(world,'France','Austria','armistice')` → `armistice_mechanics.projected_outcome == 'war'` with display line 'unless they heal to −60 or better'; sign the armistice (cheat or play), end 5 turns → `armistice_exp…  
*Fix:* ONE seam: the projection block at diplomacy.py:4368-4380 — compute `projected = relation_now + ARMISTICE_THAW_PER_TURN * ARMISTICE_DURATION`, set `projected_outcome` from it, and say it: 'Relations stand at −80 and will thaw to −65 by expiry — short of −60; the war resumes unless relations improve by other means, or a second truce follows.'  
*Test:* For relation −80 the armistice snapshot's `projected_outcome` is 'war' and a display line contains '-65'; for −72 it is 'peace' (−72 + 15 = −57 ≥ −60); pin `ARMISTICE_THAW_PER_TURN * ARMISTICE_DURATIO…

**FA-D19 [P3 · tie_in] The player's `garrison` verb feeds no stability — the 'garrison bonus' in stability growth reads marshals only, while the vassal-loyalty garrison predicate DOES count a detachment**  
`backend/models/world_state.py:6330` · NARROWED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
`process_stability_growth` documents 'Garrison bonus: +5 if a friendly marshal is present' and implements it via `_has_marshal_in_region` (`world_state.py:6330`, `:6648-6653`), which ignores `region.garrison_detachment` — the flag the `garrison` verb sets (`economy_executor.py:976-979`). VP-D1's `lord_garrison_present` (`vassal.py:444-452`) explicitly counts 'a real garrison (`garrison_strength` > 0 — the detachment corner)'. Verified by running on the 1805 boot: a France province at 40 with a 5…  
*Repro:* cd repo; .venv/Scripts/python.exe -c "import os; os.environ.pop('SOVEREIGN_SCENARIO',None); from backend.models.world_state import WorldState; w=WorldState.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json'); a=w.regions['Berry']; a.st…  
*Fix:* ONE seam: `world_state.py:6330` — `garrison_bonus = 5 if (self._has_marshal_in_region(...) or (region.garrison_detachment and region.garrison_strength > 0)) else 0`, sharing the detachment arm with `lord_garrison_present` (extract one `has_friendly_garrison(world, region, nation)` predicate both read). Mechanic change on both sides: expect a `BASELINE_SERIES` attribution run (f…  
*Test:* `tests/test_stability_garrison_detachment.py`: a detachment-only France province grows +10/turn; the same for an Austria province (GR5); a detachment with `garrison_strength == 0` grows +5; the vassal…

**FA-D20 [P3 · tie_in] The strategic parser knows join / link up with / aid / assist / bolster as SUPPORT, but the mock chain only fires on reinforce/support — so "Ney, join Davout" is Unknown and "Ney, protect Davout" becomes a 2-AP HOLD 'at' a man**  
`backend/ai/llm_client.py:1598` · NARROWED (Sept 2 verification), was PLAUSIBLE (one refuter)  
strategic_parser.py:302-308 (dict key at 302, verb entries 304-308) lists \"come to the aid of\"/\"link up with\"/\"assist\"/\"aid\"/\"bolster\"/\"join\"/\"back up\"/\"shore up\"/\"rally to\"/\"combine with\" under SUPPORT, and the near-identical SUPPORT_OBJECT_PREFIX_RE (llm_client.py:101-105, not 104-109) recognizes the same verbs for CR-2 object-prefix stripping — but the mock action chain's only SUPPORT arm, llm_client.py:1598 (`elif \"reinforce\" in command_lower or re.search(r'\\bsupport\\…  
*Repro:* POST /command {"command":"Ney, join Davout"} → Unknown action; {"command":"Ney, protect Davout"} → 'Ney will hold Davout.' with 2 AP charged.  
*Fix:* ONE seam: make the llm_client.py:1598 arm read the SAME verb tuple strategic_parser's SUPPORT table uses (export it from strategic_parser and reference it), and let the hold arm yield to SUPPORT when the object after guard/protect/cover is a friendly marshal name.  
*Test:* each of join/link up with/aid/assist/bolster/come to the aid of/cover/screen + Davout → strategic_type SUPPORT, target Davout; `Ney, protect Davout` → SUPPORT not HOLD; `Ney, protect Rhineland` / `gua…

**FA-D21 [P3 · tie_in] Trafalgar cannot lead the Morning Dispatch**  
`backend/game_logic/dispatch.py:57` · DUPLICATE (Sept 2 verification), was PLAUSIBLE (one refuter)  
Naval beats ('trafalgar'/'fleet_action', logged by `naval._log_fleet_action`, naval.py:1246-1261) reach the player ONLY through `queue_dispatch_event` → `world.pending_dispatch_events` → `_build_diplomatic_events_section` (dispatch.py:4339) as a DIPLOMATIC EVENTS rail line at priority HIGH (`_DIPLOMATIC_EVENT_PRIORITY["trafalgar"]`, dispatch.py:4073). The separate headline scorer `_build_headline` (dispatch.py:429) has no `_add()` call site for either event type and `HEADLINE_WEIGHTS` (dispatch.…  
*Repro:* Force a decisive fleet action against the player (`naval.resolve_fleet_action(w,'France','Britain')` with France at readiness 40), build the next morning's dispatch — the headline is not the Trafalgar line.  
*Fix:* ONE seam: add a `trafalgar` headline class to HEADLINE_WEIGHTS (~90, between region_lost 75 and marshal_captured 95) built by `_add` from the `trafalgar` event when the loser is the player's side; keep the rail line as the sub-beat.  
*Test:* After a decisive fleet action lost by the player, `build_morning_dispatch(world)['headline']['text']` contains 'TRAFALGAR'; after a non-decisive action it does not.

**FA-D22 [P4 · tie_in] 'Grievance' means two different things on two adjacent surfaces**  
`backend/game_logic/dispatch.py:233` · VERIFIED (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
The dispatch's terminal ES-7 dotation-shortfall escalation line (dispatch.py:234-235, the THIRD variant in `_STANDING_ESCALATION[\"estate_eroding\"]`, reached and then clamped-persistent for any neglect streak >=5 turns per the selector at dispatch.py:1172-1180) says \"Marshal {marshal}'s grievance is {turns} turns old\" for a dotation/pension shortfall — reusing jealousy's established term-of-art: \"grievance is satisfied/settled\" (jealousy.py:1188,1340; campaign_log.py:1466) and the Generals…  
*Repro:* Any ambient run past turn ~12: read the dispatch headline, press G, compare.  
*Fix:* ONE seam: the three `estate_eroding` escalation strings in dispatch.py:229-235 — use the dotation vocabulary the rail already uses ('arrears', 'unrewarded', 'claim') and reserve 'grievance' for jealousy.  
*Test:* tests/test_dispatch_vocabulary.py: render the third `estate_eroding` variant and assert 'grievance' is absent; render a jealousy confrontation title and assert the word is present there.

**FA-D23 [P4 · tie_in] AI marshals' trust is read by nothing on the AI path, yet the AI pays rentes and gives away provinces to stop an erosion that never bites it**  
`backend/ai/enemy_ai.py:5722` · VERIFIED (Sept 2 verification), was UNVERIFIED (refuter budget exhausted; the finder's own cited evidence stands)  
`_process_dotation_state` erodes ALL nations' marshals (world_state.py:6075 loop, GR5) and enemy_ai.py spends on `grant_dotation`/`grant_pension` to close shortfalls (enemy_ai.py:5722-5760; ambient40 digest lines 37, 47, 232 show the AI verbs firing). But trust's only mechanical readers are player-side: objections skip enemy marshals (`is_player_action_check`, executor.py:1130-1175), defiance rides objections (defiance.py:41-47), severity.py:118-125 feeds objections, and `grep -n trust backend/a…  
*Repro:* w=WorldState.from_scenario(<europe_1805.json>); mack=w.marshals['Mack']; mack.trust.set(0); then run any enemy-AI turn / battle — no branch changes for him (grep confirms no reader).  
*Fix:* Give trust ONE consequence both sides share, at the seam that already scales a marshal's contribution by his grievance: `CombatExecutor._pair_contribution_scale` (the jealousy weight the petition card quotes) gains a HOSTILE-tier (trust<30, objection_v2.get_trust_tier) factor, so a Broken marshal brings less to a colleague's field on either side; the AI rung then buys something…  
*Test:* tests/test_trust_contributes_both_sides.py: two-marshal reinforcement, Austria: the committed effective strength with the reinforcer at trust 10 is lower than at 70; identical for France; M1-M7 harnes…

**FA-D24 [P4 · tie_in] Berthier's battle observation is drawn with unseeded `random.choice`, so one enemy phase can print the same observation twice while enemy voice rotates**  
`backend/game_logic/battle_report.py:748` · VERIFIED (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
`_pick_observation` (backend/game_logic/battle_report.py:617, invoked from combat.py:1022/1463 inside the world-independent `CombatResolver.resolve_battle`) draws Berthier's after-battle line via unseeded `random.choice` across ~30 priority-branch banks, causing verbatim repeats within one enemy phase when the same priority branch fires twice for the same marshal pair — reproduced in docs/audits/playtest_digests/audit-latewar-t20/digest.md:112 and :115, identical "lost_despite_terrain" line agai…  
*Repro:* Load tests/fixtures/playtest_saves/fixture_t20_ambient.json with the driver (`--from-save … --turns 8 --script tools/playtest_scripts/diplomacy_latewar.json`) and read the ⚔ tails of any turn with 3+ attacks on one marshal; or call `_pick_observation` twice wi…  
*Fix:* ONE seam: pick by index `(world.battle_counts.get(pair_key,0)) % len(bank)` through a small `_rotate(bank, key)` helper in `_pick_observation`, the XR-5 idiom, passing the existing `battle_result` pair key.  
*Test:* tests/test_marshal_voice_tier1.py (or a new battle_report test): two consecutive battles between the same pair with the same outcome yield two different observations from the same bank, and the sequen…

**FA-D25 [P4 · tie_in] Every question dumps the whole COMMAND REFERENCE — "where is Mack?" / "who is at Swabia?" / "what is Davout doing?" get help text although `status` already answers them**  
`backend/ai/llm_client.py:1258` · DUPLICATE (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
DUPLICATE of CR-8/CR-6 (COMMAND_ROBUSTNESS_SPEC.md:57 and :317-319): backend/ai/llm_client.py:1258 routing every question to `help` is a documented, INTENTIONAL, gated design decision, not an overlooked join — the spec states verbatim that a question-answering Berthier (CR-8's advisory desk, or CR-6's classifier) is what replaces the `help` route, and both sit behind their own USER DESIGN GATE, still unbuilt. Verified live: all 7 repro questions ('where is Mack?' through 'should Ney attack Mack?…  
*Repro:* POST /command {"command":"where is Mack?"} → message begins with the COMMAND REFERENCE; {"command":"will Ney attack Mack?"} → a battle.  
*Fix:* Cheap join at the same seam: when `is_question` fires AND the sentence names a known marshal/enemy/region, return action `status` (or the intel report filtered to that name) instead of `help`; keep `help` for questions naming nothing. The CR-8 two-way channel remains the full answer.  
*Test:* `where is Mack?` → action status and a fog-honest line naming Swabia at boot; `how do I attack?` still → help; `will Ney attack Mack?` is treated as a question (no battle).

**FA-D26 [P4 · tie_in] The Ledger economy tab's Net omits the Materiel bill — the only component the applied identity needs, and the ledger screen has no row for it**  
`backend/game_logic/ledger.py:411` · NARROWED (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
DUPLICATE-IN-SUBSTANCE of N11/PT-C4 (docs/BUG_FIXES.md:1399, tier-2-landed per :1360; docs/PLAYTEST_FIXES_SPEC.md:242 "not fully closed"), narrowed to the one surface that fix left untouched. `backend/game_logic/dispatch.py:2271-2290` already fixed the identical gap for the Morning Dispatch by calling `_build_economy` in APPLIED mode and labeling the result `treasury_delta_label = "by the accounts"`, with an explicit comment that the EC-W3 Materiel bill is "charged outside Net by design (the plu…  
*Repro:* Boot backend.main under LLM_MODE=mock, POST /command 'end turn' three times; each turn compare nation_gold['France'] delta with _build_economy(world,'France',income_data=world._income_phase_results['France'])['net'] and world.materiel_spent_this_turn['France']…  
*Fix:* ONE seam: _build_economy returns `materiel` (read from world.materiel_spent_this_turn in applied mode, 0 in projection mode) as a signed informational line; strategic_ledger.gd renders 'Materiel (last turn): -Ng' under Net with the note that it is charged at the battle, not in the accounts.  
*Test:* After one fought turn, _build_economy(world, player, income_data=applied)['materiel'] equals world.materiel_spent_this_turn[player], and treasury delta == net − materiel exactly.

### 3f. Defects — P3/P4 (36)

**FA-44 [P3 · defect] 'Even the favorable ground could not save Massena' at 1 vs 58 casualties: Berthier's terrain verdict has no scale gate**  
`backend/game_logic/battle_report.py:836` · NARROWED (Sept 2 verification), was PLAUSIBLE (one refuter)  
`_pick_observation` selects `lost_despite_terrain`/`lost_terrain_disadvantage` purely on `we_lost and terrain-bonus modifier >= 15` (backend/game_logic/battle_report.py:832-838, banks at :333-342) with no floor on battle size — reproduced directly: a 1-vs-58-casualty exchange with a defender terrain-bonus modifier of 20 returns 'Even the favorable ground could not save Massena, Sire. Archduke Charles overcame the terrain.', matching digest line 125 verbatim. The same sub-1000-casualty engagement…  
*Repro:* generate_battle_report({'outcome':'attacker_victory','defender':'Massena','defender_nation':'France','attacker':'ArchdukeCharles','attacker_casualties':1,'defender_casualties':58,'defender_strength_before':58, … with a defender terrain modifier >= 15}) → obser…  
*Fix:* ONE seam: at the top of the loss ladder in `_pick_observation` (before :818), branch on the same 1,000-casualty floor war score uses — a sub-floor loss against a remnant gets a 'skirmish' bank ('The remnant of {marshal}'s corps was brushed aside — {n} men, Sire; there was no battle to speak of') instead of any terrain/stance verdict.  
*Test:* tests/test_battle_report_*: a defeat with total casualties < 1,000 and a terrain modifier >= 15 must NOT draw from lost_despite_terrain; the same inputs at 5,000 casualties must.

**FA-45 [P3 · defect] 'build ships' blames green crews for a readiness fall that is 5/6 blockade rot — the player concludes building makes the fleet worse**  
`backend/commands/naval_executor.py:63` · VERIFIED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
`lay_down_ship` folds one 40-readiness hull into the fleet (naval.py:1941): at 46 sail that costs ~1 point. `_readiness_tick` (naval.py:1573) then rots a BLOCKADED fleet −5/turn. The build result (naval_executor.py:60-66) prints the post-fold readiness with the clause '(new crews come aboard green at 40; only sea-time makes a navy)' and never names the blockade, so four consecutive keels read 69→63→58→53 as if each keel cost five points.  
*Repro:* In-game on the 1805 boot: 'build ships' on four consecutive turns; compare the quoted readiness against `naval.lay_down_ship`'s pre/post and `blockade_forecast(w,'France')['self_blockaded_by']` (Britain).  
*Fix:* Have `lay_down_ship` return `readiness_before`; the build message quotes the fold delta and, when `blockade_forecast(world, actor)['self_blockaded_by']` is set, adds the rot clause from the same single source the blockade order uses ('a green crew costs 1 point; the Royal Navy's blockade rots her 5 a turn — that is the number to fix').  
*Test:* test_build_message_attributes_readiness_honestly: blockaded boot → message names the blockader and quotes delta == before − after (1); after Britain flips to guard (staged camp) → no rot clause; the q…

**FA-46 [P3 · defect] A MOVE_TO whose last leg is a SHUT sea link is accepted with a route and no warning**  
`backend/commands/strategic_executor.py:1507` · VERIFIED (Sept 2 verification), was PLAUSIBLE (one refuter)  
CONFIRMED as filed, with one refinement to the fix_shape: order-issuance route-building in `_execute_strategic_command` (backend/commands/strategic_executor.py:1507, message built from `route_str = \" -> \".join([marshal.location] + order.path)`) never consults naval state — `world.find_weighted_path`/`find_path` (backend/models/world_state.py:4943-5070) walk `adjacent_regions` unconditionally and the only passability gate they call, `_region_passable_for` (world_state.py:4919), is diplomatic-on…  
*Repro:* Fresh 1805 boot (Britain blockading): type `Ney, march to London` — the acceptance names a route ending in London and says nothing about the Royal Navy.  
*Fix:* ONE seam: in `_execute_strategic_command` before the response is built (strategic_executor.py ~1495-1507), walk `order.path` pairwise, call `naval.crossing_check(world, marshal.nation, a, b, marshal.strength)` on each `naval.is_sea_link` leg, and append the leg's verdict to the message ("— the Normandy–London leg is SHUT today, the Royal Navy at 3.1×; the march will halt at Nor…  
*Test:* 1805 boot: `Ney, march to London` → response message contains 'SHUT' and 'Normandy' and 'London'; zero Britain's ships → the same order's message carries no naval clause.

**FA-47 [P3 · defect] A marshal DISMISSED by the player is later refused as 'his corps was destroyed at <location>' — the tombstone stores the cause, the refusal ignores it**  
`backend/main.py:931` · VERIFIED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
`destroy_marshal` writes `{'nation','turn','location','cause'}` into `fallen_marshals` (world_state.py:2631-2636) and the redemption `dismiss` arm calls it with `cause='dismissed'` (disobedience.py:1756); `_addressed_lost_marshal_refusal` (main.py:893, sentence at 929-933) formats every player tomb as 'Marshal {name} is lost to us, Sire — his corps was destroyed at {location}. His name cannot lead the army again.' with no branch on `cause`. The flagship-mock digest shows the dismiss path is live…  
*Repro:* m=w.marshals['Bernadotte']; m.trust.set(15); ev=w.disobedience_system.check_redemption_threshold(m,w); w.disobedience_system.handle_redemption_response(ev,'dismiss',{'world':w}) from backend.main import _addressed_lost_marshal_refusal # or drive /command print…  
*Fix:* ONE seam: `_addressed_lost_marshal_refusal` reads `tomb.get('cause')` and renders a `dismissed` arm ('Marshal {name} was relieved of command by your own order on turn {turn}; his name cannot lead the army again.') — the Marshalate hand-off that follows (main.py:936-945) stays identical.  
*Test:* tests/test_lost_marshal_refusal_names_the_cause.py: dismiss via `handle_redemption_response` then assert the refusal contains 'relieved' and not 'destroyed'; a `destroy_marshal(cause='destroyed', ...)…

**FA-48 [P3 · defect] Attacking a CAPTURED enemy marshal answers 'Unknown target: Kienmayer' — the prisoner arm exists for our own marshals and destroyed enemies, not for enemy prisoners**  
`backend/commands/executor.py:727` · DUPLICATE (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
Verified by opening backend/commands/executor.py:727 — `_fuzzy_match_enemy` builds its roster from `world.get_enemy_marshals()` with `m.strength > 0`, which excludes a captured enemy (held at strength 0 at the captor's capital), so the attack falls through every arm to combat_executor.py:5097 `Unknown target: {target}`. PC15-4 (docs/BUG_FIXES.md:1028-1030) covers 'a PRISONER refuses with his captor' (own side) and 'the enemy-side attack <destroyed name> answers from the tombstone' — not an enemy…  
*Repro:* Tutorial scenario, mock: turn 2 `Ney, defend` (trust) → Kienmayer captured at Swabia; turn 3 `Ney, attack Kienmayer` → 'Unknown target: Kienmayer'. Or in-process: set an enemy marshal's captured_by='France', strength=0, then execute attack on his name.  
*Fix:* ONE seam: the enemy-not-found branch in `_fuzzy_match_enemy` (executor.py:727 area) — before returning not-found, check `any(m.name matches and getattr(m,'captured_by','') for m in world.marshals.values())` and return the refusal 'X is our prisoner, held at <captor capital> — there is no army to attack' (the same idiom PC15-4 uses for own prisoners).  
*Test:* tests/test_pc15_fix_slice_2026_08_15.py (PC15-4 family): capture an enemy marshal via the fate arm, then `Ney, attack <name>` → success False and message contains 'prisoner', not 'Unknown target'; neg…

**FA-49 [P3 · defect] Cannon-fire interrupt options carry hidden trust costs (Continue −2, Hold −3) that the popup never shows; a HOLDING marshal pays them every other turn**  
`godot-client/project-sovereign/scripts/interrupt_popup.gd:23` · VERIFIED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
`_respond_cannon_fire` charges `trust_change = -2` for `continue_order` (backend/commands/strategic.py:568, 'Non-literal acting literal') and `-3` for `hold_position` (:596); the blocked-path handlers charge −3 on hold/cancel after the first step (:795-799, :834-838, :850-854). The popup renders bare labels only — interrupt_popup.gd:23-30 `OPTION_LABELS` ('Continue as Ordered', 'Hold Position', 'March to the Guns') — and the report builders (:2380-2390, :2600-2860) carry no per-option numbers, u…  
*Repro:* Boot 1805; 'Davout, hold Rhineland'; set `issued_turn -= 1`; `w.record_battle('Swabia','Ney','Mack','victory')`; `process_strategic_orders` → cannon_fire ask; `t0=davout.trust.value; handle_response('Davout','cannon_fire','continue_order',...)`; `davout.trust.…  
*Fix:* ONE seam: the interrupt report builders in strategic.py (cannon-fire ask at :2380-2390; blocked-path builders) emit `option_costs: {option_id: trust_change}` (the PT-C2 idiom) and `interrupt_popup.gd:69` appends '(trust −2)' from it — numbers on the buttons, same source as the payment. (Whether 'continue as ordered' on a HOLD should cost trust at all is a design question to put…  
*Test:* tests: the cannon_fire report carries `option_costs == {'investigate': 0, 'continue_order': -2, 'hold_position': -3}` and `handle_response` moves trust by exactly the quoted amount; a regex pin that i…

**FA-50 [P3 · defect] Compound two-marshal orders silently drop the second clause — "Ney, attack Mack and Davout scout Swabia" scouts nothing and says nothing**  
`backend/commands/parser.py:45` · VERIFIED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
`_SEQUEL_SPLIT_RE` (parser.py:45) splits only on "then"; the split-and-warn at parser.py:1484-1492 is the only compound handling, and `parse_multiple` (the 'Ney and Davout' splitter) has no production caller — its sole call is the `__main__` demo at parser.py:2109 (verified by grep and by opening). CR-2 (g) reports a dropped tail ONLY for the 'then' shape, so an 'and <Marshal> <verb>' or ';'-joined second order vanishes without a word.  
*Repro:* POST /command {"command":"Ney, attack Mack and Davout scout Swabia"} → response message contains no mention of Davout/scout; Davout's turn unchanged.  
*Fix:* Minimal, ONE seam: extend `_split_sequential_orders` to also split on `;` and on `\s+and\s+<PlayerMarshalName>,?\s+<verb>`, routing the tail through the EXISTING dropped-sequel Berthier warning so the second order is at least declared dropped; the full fix is CR-7's wiring of `parse_multiple` (or a loop over the split clauses at the main.py dispatch seam).  
*Test:* the 'and Davout scout Swabia' reply carries the dropped-tail warning naming Davout; the ';' form executes clause one and warns about clause two; `Ney, attack Bern, then hold your positions` (existing…

**FA-51 [P3 · defect] Expedition gate order sends a 30,000-man corps to a yard where it will then be told it cannot sail; 'with 12,000 men' is silently dropped**  
`backend/commands/naval_executor.py:207` · VERIFIED (Sept 2 verification), was PLAUSIBLE (one refuter)  
`_execute_naval_expedition` (backend/commands/naval_executor.py) checks whether the marshal stands at a controlled dockyard (line 207) strictly before checking `troops > naval.EXPEDITION_MAX_TROOPS` (line 225), even though `naval.over_lift_refusal` (naval.py:567) depends only on `marshal.strength`, not location — so an over-sized corps not at a yard is told only 'must stand at one of our yards' and learns the real, location-independent problem (that no verb can ever lighten this corps enough to…  
*Repro:* On the 1805 boot: 'land Soult in Munster with 12,000 men' → yard refusal; then set Soult's location to Brittany and repeat → over-lift refusal.  
*Fix:* Reorder in `_execute_naval_expedition`: evaluate the lift (the un-marchable-around gate) before the embark position, and when the raw text carries 'with N men' echo it in the refusal ('the transports take a whole corps; there is no verb to embark 12,000 of 30,000').  
*Test:* test_expedition_refusals_in_gate_order: Soult (30,000) inland → the refusal is the over-lift sentence, not the yard sentence; a 12,000-man corps inland → the yard sentence; 'with 12,000 men' on an ove…

**FA-52 [P3 · defect] Obeying a cannon-fire question is taxed: 'continue_order' costs −2 trust and 'hold_position' −3 while abandoning the order is free, and a HOLDing marshal 'reluctantly continues the march'**  
`backend/commands/strategic.py:568` · NARROWED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
`_respond_cannon_fire` charges `trust_change = -2 # Non-literal acting literal` on `continue_order` (strategic.py:568-570) and −3 on `hold_position` (:594-596); only `investigate` — which cancels the order — is free. The copy is a fixed 'reluctantly continues the march, ignoring cannon fire at X' (:581) regardless of order type. Verified by running (probe E3–E5): Davout under `hold Rhineland` (2 AP), a battle recorded two regions away → 'Davout: Cannon fire at Franconia, Sire. Investigate?'; ans…  
*Repro:* 1805 boot; run('Davout, hold Rhineland'); dav.strategic_order.issued_turn -= 1; w.record_battle(<region at distance 2>, 'Blucher','Hohenlohe','victory'); process_strategic_orders → cannon_fire ask; handle_response('Davout','cannon_fire','continue_order') → tru…  
*Fix:* ONE seam: `_respond_cannon_fire` — `continue_order` charges 0 for HOLD/SUPPORT and for battles with no enemy participant (or drop the tax entirely: the personality cost of ignoring guns already lives in the aggressive auto-redirect), and the sentence keys on `_strategic_command_flavor(order.command_type)` ('keeps his position'/'continues the march').  
*Test:* tests/test_strategic_bugfixes.py: cautious marshal under HOLD, nearby battle → answer continue_order → trust unchanged, order standing, message contains 'holds' and not 'march'; the aggressive auto-re…

**FA-53 [P3 · defect] On a multi-province day the dispatch drops provinces entirely and never names the captor**  
`backend/game_logic/dispatch.py:1212` · NARROWED (Sept 2 verification), was UNVERIFIED (refuter budget exhausted; the finder's own cited evidence stands)  
The page holds a headline plus `SUB_BEAT_SLOTS = 2` (dispatch.py:209) and `region_captured` is not in `_DISPATCH_EVENT_TYPES` (:2718-2790), so any province beyond the third vanishes from the briefing. Reproduced: five homeland provinces lost in one turn on the legacy world → 'Paris HAS FALLEN' + Belgium + Lyon; Milan and Marseille appear nowhere in the dispatch payload (`turn_events` empty of them). In ambient40 turn 31 France lost EIGHT provinces (`provinces 15 (-8)`, digest.md:301) and the dis…  
*Repro:* C:/Users/User/PycharmProjects/project-sovereign-map/.venv/Scripts/python.exe -c "import os;os.environ.pop('SOVEREIGN_SCENARIO',None);from backend.models.world_state import WorldState;from backend.game_logic.dispatch import _build_headline,build_morning_dispatc…  
*Fix:* ONE seam — `_select_headline` (dispatch.py:1212): when ≥2 candidates share class `home_captured`/`region_lost`, collapse them into ONE candidate built from the events' structured fields via the existing `_join_place_names` (:2933) — 'Savoy, Burgundy, Champagne and 5 more have fallen — Shrapnel (Britain) and Mack (Austria) walk the homeland unopposed' — keeping `capital_lost` se…  
*Test:* tests/test_dispatch_headline.py: five `region_captured` events in one turn → every province name appears on the page (headline + sub-beats) and each captor nation is named; one province → the single l…

**FA-54 [P3 · defect] Real-world exonyms auto-correct into the wrong province and the strategic march never says so — "Ney, march to Mainz" marches six provinces WEST to Maine; "march to Bayern" heads for Bern**  
`backend/commands/parser.py:525` · VERIFIED (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
CONFIRMED defect, WRONG SEAM in fix_shape. `backend/commands/parser.py:1761-1794` (the strategic-target fuzzy-match arm inside `CommandParser.parse()`'s MOVE_TO/HOLD/PURSUE/SUPPORT detection block, region case at :1768-1779) silently rewrites a strategic order's target (e.g. Mainz→Maine, Bayern→Bern) and stamps the corrected name into `result[\"command\"][\"target\"]` at :1794 — BEFORE `strategic_executor.py` ever runs. `strategic_executor.py:748-800`'s phrase-resolution branch (cited as the fix…  
*Repro:* POST /command {"command":"Ney, march to Mainz"} on the 1805 boot → strategic order to Maine, reply contains no 'Our maps read'; {"command":"Ney, move to Mainz"} → reply contains 'Our maps read Maine'.  
*Fix:* ONE seam: give the strategic MOVE_TO/HOLD reply the same raw-text grounding note the movement path builds (movement_executor.py:343-353) at the strategic_executor.py:779 resolve site — any auto-corrected destination is disclosed on every route. Secondary (in-band): in `_plausible_name_typo` allow 2 edits only when the CANDIDATE is also ≥6 letters (bayern→bern then suggests inst…  
*Test:* `Ney, march to Mainz` reply contains 'Our maps read Maine'; `Ney, march to Bayern` either asks 'Did you mean Bern?' or discloses; `Ney, march to Berne`/`Berri`/`Britany`/`Milano` keep auto-correcting…

**FA-55 [P3 · defect] The AI's in-place capture rung charges march attrition for a march it never makes, every turn it stands on undefended soil**  
`backend/commands/combat_executor.py:5028` · DUPLICATE (Sept 2 verification), was UNVERIFIED (refuter budget exhausted; the finder's own cited evidence stands)  
XR-3 filed the player-typed case at P4 as cosmetic. The archive shows it is an AI rung: PRIORITY −1 (backend/ai/enemy_ai.py:1578-1582) returns `{'action': 'attack', 'target': marshal.location}` for any marshal standing on undefended enemy soil; the attack path then calls `_calculate_movement_attrition(marshal, resolved_target, world)` (combat_executor.py:5028) with `resolved_target == old_location` — `movement_executor.py:45-95` has no origin==destination guard — and narrates 'marches from {old_…  
*Repro:* grep -rhoE '[A-Za-z]+ marches from ([A-Za-z-]+) into ([A-Za-z-]+) unopposed' docs/audits/playtest_digests/audit-*/digest.md | awk '$4==$6' — six rows, each with a '(N lost to march)' clause; or run `tools/playtest_driver.py --turns 12 --fresh --name probe-narr…  
*Fix:* ONE seam — combat_executor.py:5028: when `old_location == resolved_target`, skip `_calculate_movement_attrition` and emit 'secures {region}' instead of the march clause; the AI rung and the typed route both inherit it (GR5).  
*Test:* tests/test_capture_pipeline.py: an AI marshal standing on undefended enemy soil captures it with `march_losses == 0` and a message without 'marches from'; the adjacent-capture case still charges attri…

**FA-56 [P3 · defect] The Rebuke's intel pause is dead: the writer stamps `literal_intel_paused_turn`, the fog pass reads `_literal_intel_paused_turn`**  
`backend/models/world_state.py:2884` · VERIFIED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
JEALOUSY_SPEC.md:466-468 promises that rebuking a jealous literal marshal pauses his obsessive-patrol fog lift for one turn. `jealousy.py:2724` writes `marshal.literal_intel_paused_turn = current_turn + 1` (the serialized field, marshal.py:663/1661/1857) but `calculate_visibility` at world_state.py:2884 checks `getattr(marshal, "_literal_intel_paused_turn", None) == turn` — the pre-CA9-A10 underscore spelling, which the A10 pin `tests/test_ca9_row3_phase_a.py:376` asserts is NEVER on the marshal…  
*Repro:* w = WorldState.from_scenario('godot-client/project-sovereign/assets/maps/europe_1805.json'); s = w.get_marshal('Soult'); s.jealous_of='Ney'; s.literal_intel_paused_turn = w.current_turn; w.calculate_visibility(); print([r for r in [s.location]+w.regions[s.loca…  
*Fix:* ONE seam: change world_state.py:2884 to read `getattr(marshal, "literal_intel_paused_turn", -1) == turn`. The writer already stamps turn+1 so the pause lands on the following turn's visibility pass; no serialization or client change.  
*Test:* tests/test_jealousy_v32.py: arm Soult jealous → calculate_visibility lifts his sector (source 'scout'); set `literal_intel_paused_turn = world.current_turn` → recalc → no sector region carries source…

**FA-57 [P3 · defect] The School of War's confirm row and boot line warn that the campaign autosave is replaced — the backend has not touched it since TUT-F2**  
`godot-client/project-sovereign/scripts/main_menu.gd:444` · VERIFIED (Sept 2 verification), was PLAUSIBLE (one refuter)  
CONFIRMED as filed, no correction needed. main_menu.gd:444 and main.gd:6238 tell the player the tutorial 'replaces'/'will be replaced' their campaign autosave; menu_boot.gd:19-21's comment says the same. But backend/main.py:4040-4051 (skip branch at 4043-4046) and backend/save_manager.py's autosave() (tutorial no-op ~256-269) leave the campaign autosave completely untouched for scenario_name=='tutorial', and say so in the response message ('Your campaign autosave is untouched.') — confirmed live…  
*Repro:* Main menu with an existing save → click 'The School of War' → read the confirm row; then confirm and read the terminal's first two lines (client 'will be replaced' vs backend 'is untouched').  
*Fix:* ONE seam per surface, copy only: main_menu.gd:444 → 'Enter the School of War? Your running campaign leaves the table (its autosave is kept — Continue restores it).'; main.gd:6238 → 'Convening the School of War. Your campaign autosave is kept.'; menu_boot.gd:19-21 comment corrected.  
*Test:* tests/test_tutorial_position7.py TestClientStructural: assert 'autosave' + 'replaced' do not co-occur in the tutorial confirm/boot strings of main_menu.gd and main.gd, and that the tutorial confirm na…

**FA-58 [P3 · defect] The blockade 'floor' RAISES a beaten fleet: readiness 40 after Trafalgar becomes 50 next tick**  
`backend/game_logic/naval.py:1573` · VERIFIED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
`_readiness_tick` rule 1 is written `readiness = max(READINESS_BLOCKADE_FLOOR, readiness − READINESS_TICK)` (naval.py:1573). For any fleet already below 50 — the diversion's failure arm docks readiness to max(40, r−10) and the fleet fights there — the 'rot' lifts it to 50.  
*Repro:* python -c: w=from_scenario(...); fr=naval.get_fleet(w,'France'); fr['readiness']=40; naval._readiness_tick(w); print(fr['readiness']) → 50.  
*Fix:* One line: `readiness = max(min(readiness, READINESS_BLOCKADE_FLOOR), readiness − READINESS_TICK)` so the floor stops the fall and never lifts.  
*Test:* test_blockade_rot_never_raises: readiness 40 blockaded → 40 after the tick; 52 → 50; 70 → 65; a fleet docked to 40 by a failed diversion does not read 50 on the following turn. Mutation: restore the b…

**FA-59 [P3 · defect] The fleet-action loss line sums the pooled allies' losses under the loser's name ('loses 49 sail' with 45 in commission)**  
`backend/game_logic/naval.py:1516` · VERIFIED (Sept 2 verification), was PLAUSIBLE (one refuter)  
CONFIRMED as filed, line numbers exact (naval.py:1516 `resolve_diversion`, naval.py:1264 `_log_fleet_action`'s `loser_ships_lost`, naval_executor.py:370 expedition-intercept message). Live-reproduced: forcing a diversion loss on the 1805 boot (France allied to Spain, Holland its vassal, all three at war with Britain) drove France's own fleet 45→20 (25 ships) while the game's own message read "loses 49 sail" — the sum of France's 25 + Spain's 17 + Holland's 7. Scope is slightly WIDER than filed:…  
*Repro:* python -c: w=from_scenario(...); naval._pct_roll=lambda *a: False; print(naval.resolve_diversion(w,'France')['message'], naval.get_fleet(w,'France')['ships']) → 'loses 49 sail' / 20.  
*Fix:* At `resolve_fleet_action` (the one seam both consumers read), add `own_lost = losses[loser].get(loser, 0)` and `allied_lost` to the result; the diversion message and `_log_fleet_action`'s `loser_ships_lost` use the principal's own figure and name the allies' separately ('France loses 25 sail; Spain 17 and Holland 7 beside her'); pass `display_nation(loser)`/`nation_adjective` i…  
*Test:* test_fleet_action_loss_line_is_the_losers_own: forced failure at boot → message figure == 45 − France ships after; dispatch `loser_ships_lost` == the same; allies' losses appear under their own names;…

**FA-60 [P3 · defect] The letter-book re-asks the identical declined pact every 4 turns forever — `friendly_gift` and `open_borders` are two cooldown keys for one displayed 'Open Borders Agreement'**  
`backend/game_logic/ai_diplomacy.py:323` · DUPLICATE (Sept 2 verification), was PLAUSIBLE (one refuter)  
For a court at relation<0, `_hegemony_ask_candidates` (ai_diplomacy.py:1005-1055) orders `["friendly_gift","open_borders"]`; `friendly_gift`'s terms (built at :802-819) set `terms["type"]="open_borders"` (or `"non_aggression"` at relation>=0), so it IS the same letter as the literal ask of that base state — `envoy_digest.py:101-112` titles the letter-book row from `terms["type"]`, not the internal label. `_cooldown_keys` (ai_diplomacy.py:305-323) keys the anti-monotony cooldown on the raw `propo…  
*Repro:* .venv/Scripts/python.exe tools/playtest_driver.py --turns 10 --name probe-letters --fresh → digest shows LETTER Ottoman 'Open Borders Agreement' at turns 2, 6, 10 with policy decline; or the scratch probe printing `world.ai_proposal_cooldowns` at turns 2 and 6…  
*Fix:* ONE seam: `_cooldown_keys` (ai_diplomacy.py:305-325) — key the TYPE cooldown on the ask's base target state (`_ASK_TARGET_STATE[base]`, i.e. the pact the letter proposes: open_borders for a relation<0 gift, non_aggression otherwise) so `friendly_gift` and its base share one key; `apply_rejection_cooldowns`/`_is_on_cooldown` inherit. Optionally raise the re-ask window after an e…  
*Test:* tests/test_igr_f_envoy_digest.py: deliver an Ottoman `friendly_gift` at relation < 0, reject it through POST /mailbox/respond, advance 4 turns; assert no Ottoman row whose `proposal_type_display` equa…

**FA-61 [P3 · defect] The muster's '… if all march' figure is an arrival-probability EXPECTATION, and the resolved commitment can EXCEED it with half the corps absent**  
`backend/commands/combat_executor.py:1493` · NARROWED (Sept 2 verification), was PLAUSIBLE (one refuter)  
`_format_muster_lines` (combat_executor.py:1487-1496, not 1493-1498) prints `committed_strength` (built at combat_executor.py:1177-1178/1212 via `_committed_reinforcement_strength(..., expected_at=battle_region)`, combat_executor.py:445-496) under the label 'N if all march', but since PT-A2 that call weights every eligible joiner by its arrival-roll PROBABILITY (`_expected_arrival_weight`, combat_executor.py:1590-1611) rather than summing them at full weight — so the printed number is a probabil…  
*Repro:* LLM_MODE=mock python -c: TestClient(backend.main.app); POST /new_game {}; POST /command {'command':'Marshal Ney, attack Mack'}; regex the response JSON for 'if all march' and 'Massed effective strength' and compare the two totals.  
*Fix:* ONE seam, `_format_muster_lines` (:1493-1498): render the expectation honestly ('~78,676 expected; up to 96,000 if every corps arrives') by also passing a ceiling — the same `_committed_reinforcement_strength` call with `expected_at=None` over `will_join_marshals` — as `preview['attacker']['ceiling_strength']` from `_build_muster_preview` (:1206).  
*Test:* Extend tests/test_pt_*muster*: for a lead with two eligible adjacent joiners at arrival probability < 1, assert the rendered line contains both the expected and the ceiling figures, that expected < ce…

**FA-62 [P3 · defect] The shipped client tells a stranger with no Python to run `python -m backend.main` when the server is down**  
`godot-client/project-sovereign/scripts/main.gd:745` · DUPLICATE (Sept 2 verification), was UNVERIFIED (refuter budget exhausted; the finder's own cited evidence stands)  
main.gd:745 prints 'Start the Python server: python -m backend.main' on connection failure; main_menu.gd:527 prints 'start the backend: .venv\Scripts\python.exe -m backend.main'; the README claims 'The main menu names the launch command when the server is down; use launch.bat' (deploy/README_TESTER.txt:208-209). In the zip there is no Python and no .venv; the correct instruction is 'close everything and run launch.bat'. Same audience slip: settings_panel.gd:194 button 'Clear (use .env)' and :237…  
*Repro:* Launch InkAndIron.exe from the dist folder without the server (or kill ink_iron_server.exe mid-game) and read the terminal / menu status line.  
*Fix:* ONE source: `Utils.backend_down_hint()` returning 'Run launch.bat (it starts the war office)' when `OS.has_feature('template')` and the module command in the editor; both surfaces and the settings copy read it; README stays as is.  
*Test:* Parse-harness regex pin: no `.gd` outside utils.gd contains 'backend.main' or '.venv'; a GDScript unit under the harness asserts the exported-build branch text names launch.bat.

**FA-63 [P3 · defect] The tutorial's authored timing premise is false: the Vienna reserve attacks Munich on turn 2, not turn 8+**  
`godot-client/project-sovereign/assets/maps/tutorial_1805.json:1` · NARROWED (Sept 2 verification), was UNVERIFIED (refuter budget exhausted; the finder's own cited evidence stands)  
tutorial_1805.json:1 (_comment) says starting Charles at Hungary 'delays the combined-strength attack into the designed turn-8+ free-play window', and TUTORIAL_SCRIPT.md:350-351 teach the counter-blow as ~T8-10 (step XII/XIII). In both the archived digest and my insist probe Archduke Charles attacks Senarmont at Munich in the T2 enemy phase and again at T3/T5, with Schwarzenberg attacking Ney at T3 — before the lesson has taught 'first blood'. No pin covers the pair's timing (tests/test_tutorial…  
*Repro:* Run the tutorial script for 3 turns under either policy and read the T2 enemy phase.  
*Fix:* ONE authored change: start Charles one march further east (or give the Vienna pair an authored HOLD/fortify posture until the P3.7 pull) so their first attack lands in the T8+ window the cards describe; alternatively rewrite steps XII/XIII to say the reserve is already on you.  
*Test:* tests/test_tutorial_scenario.py: seed the combat RNG (the PC15-9 idiom), walk `TurnManager.end_turn` for turns 1-6 with no player orders and assert no Austrian attack on Munich before T7 across 3 seed…

**FA-64 [P3 · defect] The typed Grand Diversion confirm omits the 'no army is staged' warning the Admiralty chip carries**  
`backend/commands/naval_executor.py:518` · NARROWED (Sept 2 verification), was UNVERIFIED (refuter budget exhausted; the finder's own cited evidence stands)  
The chip note (naval.py:2293) appends '; no army is staged to use the open water' when `camp_staged` is False; the typed quote-then-confirm (naval_executor.py:518-527) states only the roll, the window length and the failure readiness. The once-per-war card can be spent from the terminal with no warning that nothing will use the window.  
*Repro:* On the 1805 boot type 'order the diversion' with no corps in Flanders/Artois/Normandy/Brittany → the confirm text lacks any camp clause; open the Admiralty tab → the chip note says 'no army is staged to use the open water'.  
*Fix:* Build the confirm sentence from the same source as the chip note — factor the chip's note builder into `naval.diversion_note(world, actor)` and have `_execute_naval_diversion` append it (and the window-forecast row once it exists).  
*Test:* test_typed_diversion_confirm_carries_the_chip_note: unstaged → the clarification message contains 'no army is staged'; staged (camp_turns=2) → it does not; both strings byte-equal the Admiralty chip n…

**FA-65 [P3 · defect] The vassal recovery hint is attached only while loyalty >= 40 — it disappears exactly when the bribe window opens**  
`backend/game_logic/vassal.py:711` · NARROWED (Sept 2 verification), was PLAUSIBLE (one refuter)  
vassal.py:711 `if delta < 0 and new_loyalty >= 40:` gates recovery_hint on the POST-delta loyalty, so it can vanish the same turn loyalty first drops below 40. Verified live: Switzerland drifting 39→37 emits 'satellite drift' with recovery_hint=='' and the paired dispatch.py:3808 'diplomatic_vassal_unrest' template ('Talleyrand reports unrest in {nation}.') carries no hint at all. Tracing the sibling producer shows the gap is a full dead zone, not merely cooldown-limited: Talleyrand's <35 adviso…  
*Repro:* from_scenario(europe_1805); world.vassals['Switzerland']['loyalty']=36; run vassal.process_vassal_loyalty(world) → the event's recovery_hint == '' while attempt_vassal_bribe(world,'Austria') is already eligible one tick later at <35.  
*Fix:* ONE seam: vassal.py:711 — attach the hint whenever loyalty is falling (drop the >= 40 clause) or at least while loyalty < BRIBE_SPIRAL_LOYALTY, and let the 'diplomatic_vassal_unrest' template carry recovery_hint_for_grip(grip).  
*Test:* process_vassal_loyalty on a satellite at 38 with a negative delta yields an event whose recovery_hint is non-empty and whose message contains a lever named by recovery_hint_for_grip; and the queued di…

**FA-66 [P3 · defect] Trafalgar cannot lead the dispatch — no naval headline class; the turn France lost half her fleet led with a counter-punch expiry**  
`backend/game_logic/dispatch.py:429` · DUPLICATE (Sept 2 verification), was UNVERIFIED (refuter budget exhausted; the finder's own cited evidence stands)  
`_build_headline` (dispatch.py:429) has 25 `_add` classes (capital_lost … marshal_reversal) and none is naval; the `trafalgar`/`fleet_action`/`expedition_intercepted` beats ride `queue_dispatch_event` and render only in `diplomatic_events` at priority HIGH (dispatch.py:4073, :4400). So a decisive fleet action — the campaign-defining naval moment the spec names — can never be the briefing's first line.  
*Repro:* python -c: w=from_scenario(...); import backend.game_logic.naval as naval; naval._pct_roll=lambda *a: False; naval.resolve_diversion(w,'France'); d=dispatch.build_morning_dispatch(w); print(d['headline'], [e for e in d['diplomatic_events'] if 'TRAFALGAR' in e[…  
*Fix:* In `_build_headline`, add a `fleet_shattered` class from the `trafalgar` (and player-losing `fleet_action`) event on `world.event_log` for the current turn, identity `fleet_shattered:<battle_name>`, weighted between `own_broken` and `marshal_destroyed`, with the loser's OWN ships lost in the sentence (see the loss-attribution finding).  
*Test:* test_trafalgar_leads_the_dispatch: log a trafalgar event with loser == player and a counter_punch_expired tactical event in the same turn → headline class 'fleet_shattered', text names the sail lost;…

**FA-67 [P3 · defect] Trust-warning remedy 'give him a battle he can win' names a lever that does not exist — no combat seam adds trust, and for an eroding marshal a win RAISES his expectation**  
`backend/models/world_state.py:12097` · NARROWED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
The one-time <40 warning (world_state.py:12094-12100) says 'Trust his judgment when he objects, and give him a battle he can win — at 20 he will ask to be released', and its comment (12084-12089) asserts 'a won battle is the reliable earner'. Verified by grepping every positive trust write in backend/: objection 'trust'/'compromise' (disobedience.py:1382/1412), vindication (vindication.py:194), literal order completion +5 (strategic.py:2522), autonomy end (turn_manager.py:811-824), petition arms…  
*Repro:* m=w.marshals['Lannes']; m.trust.set(38); print(w._check_trust_warnings()[0]['message']) # '...give him a battle he can win — at 20 he will ask to be released.' m.battles_won+=1; print(dotation.get_expectation(m)) # +40 — the win deepens the shortfall  
*Fix:* ONE seam: `_check_trust_warnings` — build the remedy from what is true: 'trust his judgment when he objects' (kept), and when `dotation.is_eroding(marshal, self)` append `dotation.reward_remedy_phrase(self, marshal.nation, marshal)`; delete the battle clause; say 'he will ask to be released the next time you order him' unless FA-26 lands.  
*Test:* tests/test_trust_warning_names_real_levers.py: eroding marshal at 38 -> message contains the reward remedy phrase and never 'battle he can win'; non-eroding marshal at 38 -> no reward clause; pin that…

**FA-68 [P3 · defect] Two marshals raising interrupts in one end turn: only the first is asked, the rest silently lose the turn and their question**  
`backend/commands/strategic.py:315` · VERIFIED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
`process_strategic_orders` (backend/commands/strategic.py:284-320) defers every marshal with a pending or new interrupt (:299-302) and pass 2 `break`s after the first report with `requires_input` (:315). The remaining deferred marshals are never passed to `_execute_strategic_turn`: no movement, no report row, no `pending_interrupt` stored (`_check_interrupts` in pass 1 only computes it). Next turn `clear_turn_battles` (world_state.py:9495) has wiped the battle, so a cannon-fire question is gone…  
*Repro:* Boot 1805; issue 'Davout, march to Nassau' and 'Bernadotte, march to Nassau'; set both `issued_turn = current_turn-1`; `w.record_battle('Swabia','Ney','Mack','victory')`; `process_strategic_orders` → exactly one report, Davout unmoved and un-asked.  
*Fix:* ONE seam: replace the `break` at :315 with 'continue processing but store' — for each further deferred marshal call `_execute_strategic_turn` and let `requires_input` results latch `marshal.pending_interrupt` (step 0a at :880-890 already renders any number of pending marshals as `awaiting_response` rows); the client queue and the driver's `_interrupt_report` both consume a list…  
*Test:* tests: two cautious marshals within 2 of one recorded battle, both with MOVE_TO issued last turn → `process_strategic_orders` returns two rows with `requires_input` (or both marshals have `pending_int…

**FA-69 [P3 · defect] W6-8 estate-stage modal and terminal print the raw marshal key ('Marshal ArchdukeCharles's household')**  
`backend/commands/capture_executor.py:225` · NARROWED (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
DUPLICATE of N27 (an unenumerated instance, not a new bug class): capture_executor.py:225 stamps `estate_holder: holder.name` (raw camelCase) into `capture_data`; the sentence at capture_executor.py:236 interpolates it raw ('Marshal ArchdukeCharles's household') while the SAME function already routes the nation through `formed_display_name` two lines later — an inconsistency within one function. capture_choice_dialog.gd:60 (region_label, not the static title at :59) renders `estate_holder` verba…  
*Repro:* python -c: build WorldState.from_scenario(europe_1805.json); world.marshals['ArchdukeCharles'].dotation_regions=['Bohemia']; teleport Ney adjacent (Dresden), strength 120000; executor.execute({'action':'move','command':{'marshal':'Ney','target':'Bohemia','acti…  
*Fix:* ONE producer seam: `_maybe_mount_estate_choice` keeps `estate_holder` as the machine key (handle_capture_choice:256 re-reads it) and adds `estate_holder_display = humanize_entity_name(holder.name)` + `estate_holder_nation_display = formed_display_name(...)`, using the display forms in the :236 sentence; capture_choice_dialog.gd:56-57 reads the `_display` keys with fallback to t…  
*Test:* tests/test_igr_e_plunder_prompt.py family: mount the estate stage with holder ArchdukeCharles; assert 'ArchdukeCharles' not in result['message'], result['capture_data']['estate_holder_display'] == 'Ar…

**FA-70 [P3 · defect] War Detail prints 'Enemy War Exhaustion' twice for fleetless enemies and never for fogged fleet-holders (NV-12 regression)**  
`godot-client/project-sovereign/scripts/war_detail_popup.gd:439` · VERIFIED (Sept 2 verification), was PLAUSIBLE (one refuter)  
In war_detail_popup.gd, the `else: bbcode += \"Enemy War Exhaustion: ... Unknown\"` at line 439-440 is attached to `if naval_line != \"\":` (line 437) instead of to `if we != null:` (line 424, whose block ends unclosed at 431 with no else). NV-12 (commit cd1be00e) inserted the fleet-line block between the WE `if` and its original `else`. Fleetless courts (naval_line==\"\", e.g. Austria/Prussia/Hanover/KingdomOfItaly/PapalStates per europe_1805.json's `ships:0` rows) with known (unfogged) WE prin…  
*Repro:* Play or load any campaign where France is at war bilaterally with a fleetless court (e.g. Austria after the coalition dissolves; SOVEREIGN_SMOKE_START=settlement_losing also yields bilateral rows), open the War Status HUD row → War Detail: body shows 'Enemy Wa…  
*Fix:* ONE seam: war_detail_popup.gd `_render_war_detail` — move the `else: … Unknown` back under `if we != null:` (lines 423-431) and make the naval block (436-438) a standalone `if naval_line != ""` with no else.  
*Test:* Add a regex pin in the existing .gd-structure test family (e.g. tests/test_ui_visual_foundation.py idiom): read war_detail_popup.gd, assert the `Enemy War Exhaustion: [color=" + COLOR_DIMMED` line lie…

**FA-93 [P4 · defect] '[Square broken — Ney breaks formation to attacks]' — the square-break prefix conjugates its verb wrong on the player's own terminal**  
`backend/commands/tactical_executor.py:480` · VERIFIED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
`_auto_break_square` builds `f"[Square broken — {marshal.name} breaks formation to {display}]"` with `display = action_display_name(action_name)` (backend/commands/tactical_executor.py:480-481), and `ACTION_DISPLAY` is the third-person-present map ('attack': 'attacks', 'move': 'moves to', 'fortify': 'fortifies', display_names.py:16-19). `executor.execute` prepends it to the result message (executor.py:2493-2494) and `main.gd::_display_result` (:2653) prints that message. Verified by running: '[S…  
*Repro:* C:/Users/User/PycharmProjects/project-sovereign-map/.venv/Scripts/python.exe -c "import os;os.environ.pop('SOVEREIGN_SCENARIO',None);from backend.models.world_state import WorldState;from backend.commands.executor import CommandExecutor;w=WorldState();ex=Comma…  
*Fix:* ONE seam — tactical_executor.py:480: a tiny infinitive map beside `ACTION_DISPLAY` in display_names.py ('attack'→'attack', 'move'→'march', 'fortify'→'fortify', …) used only here, or rephrase to '[Square broken — Ney breaks formation and {display}]'.  
*Test:* tests/test_square_formation.py: `_auto_break_square(m, 'attack')` == '\n[Square broken — Ney breaks formation to attack]' and the 'move' form contains no dangling 'to'.

**FA-94 [P4 · defect] Browsable/informational modals (letter-book, Proclamation, sabotage discovery, vassal rebellion, capture choice) have no ESC — and main.gd's ESC ladder refuses to act while any modal is up**  
`godot-client/project-sovereign/scripts/popup_base.gd:40` · NARROWED (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
DUPLICATE IN SPIRIT of UI-2d-1 (docs/BUG_FIXES.md:2870), narrowed and corrected: only mailbox_panel.gd (the letter-book, godot-client/project-sovereign/scripts/mailbox_panel.gd — CanvasLayer, already wires a background-overlay click to `_on_close` at :314-321) and proclamation_popup.gd (extends PopupBase but PopupBase itself has no input handler, popup_base.gd:1-80; single Acknowledge button at proclamation_popup.gd:22-105) are genuine read-and-dismiss surfaces missing an ESC binding to their EX…  
*Repro:* Reason from source (Godot not run here): end a turn with ≥2 routine minor-court letters queued → letter-book raises (main.gd:2640) → press ESC: main.gd:_unhandled_input reaches the `elif not _is_modal_dialog_open()` arm and returns having done nothing; only th…  
*Fix:* ONE seam: popup_base.gd gains `func _unhandled_input(event)` mapping `ui_cancel` to an overridable `esc_control()` (default: the single/rightmost non-destructive button; decision modals override to null to keep UI-2d-1's intent); mailbox_panel.gd (not a PopupBase) wires `ui_cancel` → `_on_close`.  
*Test:* A scripts census pin (the PC15-18 wheel-eater idiom): every scene registered modal in main.gd either extends PopupBase, defines its own ESC handler, or is on an explicit 'decision modal' allowlist; pl…

**FA-95 [P4 · defect] Cooldown refusal prints the turns REMAINING as 'turns ago' ('rejected our last proposal only 1 turns ago') and names no wait**  
`backend/commands/diplomatic_executor.py:686` · VERIFIED (Sept 2 verification), was PLAUSIBLE (one refuter)  
`_execute_diplomatic_propose`'s cooldown refusal (backend/commands/diplomatic_executor.py:686 and the per-type sibling at :695) prints the DECREMENTING "turns remaining until re-proposal is allowed" value as if it were elapsed time since the rejection: `f"...{target_nation} rejected our last proposal only {remaining} turns ago."` The cooldown is set to 4 on rejection at world_state.py:10179 (:10182 for the `{target}_{ptype}` key — corrected from the cited 10186-10190, which lands a few lines bel…  
*Repro:* Seed historical, propose peace with Russia on turn 3, confirm, end turn (rejected), end turn, then 'propose peace with Russia' on turn 6 → message says '1 turns ago'.  
*Fix:* ONE seam: the two f-strings at diplomatic_executor.py:686 and :695 — 'Talleyrand advises patience, Sire — Russia refused us; the court will not receive another envoy for N more turn(s).' using `remaining` for what it is.  
*Test:* Set `world.player_proposal_cooldowns['Russia'] = 1`; the refusal message contains '1 more turn' and not 'ago'; with 3 it contains '3 more turns'.

**FA-96 [P4 · defect] Dead popup channel on both sides: `coalition_popup` is PopupQueue priority 0, a serialized world property, and has neither a producer nor a client reader**  
`backend/models/cooldown_manager.py:146` · DUPLICATE (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
CONFIRMED core defect, NARROWED fix scope: `world.coalition_popup` (the PopupQueue-backed property at `backend/models/world_state.py:2159-2164`, serialized at `:7295`/round-tripped at `:8147`, and ranked top-priority in `cooldown_manager.py:145-163`'s `PRIORITY_ORDER`/`RESPONSE_KEYS`) has zero live producers — the only write anywhere is a defensive `= None` at `turn_manager.py:443` — and zero `.gd` readers (`grep -rn coalition_popup godot-client/project-sovereign/scripts/` = 0 hits). The similar…  
*Repro:* `grep -rn coalition_popup godot-client/project-sovereign/scripts/` → 0 hits; `grep -rn 'coalition_popup = ' backend/` → only turn_manager.py:443 `= None`.  
*Fix:* ONE seam: cooldown_manager.PopupQueue — drop `coalition_popup` from PRIORITY_ORDER/RESPONSE_KEYS (keep from_dict tolerant of the old key), delete the world property + to_dict line and the dead main.gd:2669 `marshal_switched` branch.  
*Test:* Promote the scratch key-join script into tests/: every PopupQueue.RESPONSE_KEYS value has a `.gd` reader, and every `.gd` `response.get("x")` key has a backend emitter or is on a short allowlist of cl…

**FA-97 [P4 · defect] The C3 auto-advance guard rides the autosave: the first End Turn after Continue is absorbed with a message about 'your last action point'**  
`backend/save_manager.py:217` · REFUTED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
When the last AP triggers an auto-advance, executor.py:2533 stamps `world._auto_advanced_to_turn = world.current_turn` and the autosave at :2717 is written AFTER that stamp; to_dict/from_dict carry it (:7318/:8210) and neither `load_game` (save_manager.py:136-247) nor `/load` (main.py:4065-4143) zero it. `TurnManager.end_turn` (turn_manager.py:128-140) then absorbs the first `end turn` of the resumed session and returns 'The turn already advanced to N when your last action point was spent. Order…  
*Repro:* w = WorldState.from_scenario(<europe_1805.json>); w._auto_advanced_to_turn = w.current_turn; save_game(w,'p',filepath=tmp/'p.json'); w2 = load_game(tmp/'p.json')['world']; r = TurnManager(w2, CommandExecutor()).end_turn({'world': w2}); assert w2.current_turn =…  
*Fix:* ONE line in `load_game`'s transient-clear block (save_manager.py:217): `world._auto_advanced_to_turn = 0` — a loaded world has no in-flight duplicate press to absorb. (Keep it serialized so to_dict stays complete.)  
*Test:* tests/test_save_load.py: stamp the flag, save, load → `_auto_advanced_to_turn == 0` and the first `TurnManager.end_turn` advances `current_turn` by one with a normal 'Turn N ended' message.

**FA-98 [P4 · defect] The crown beat leaks into the lesson: 'Ney, crowned four turns ago, has been beaten in the field' on turn 6 of the School**  
`backend/game_logic/dispatch.py:1313` · VERIFIED (Sept 2 verification), was PLAUSIBLE (one refuter)  
CONFIRMED as filed, with one framing correction: this is not "TUT-F5 missed a seam" — TUT-F5's jealousy_dormant (jealousy.py:204-212) deliberately gates only apply_jealousy (:883) and _push_petition (:1853), and its docstring explicitly says glory/crowns must keep accruing so "the Generals screen stays honest." recompute_crowns (jealousy.py:529, called unconditionally at :3428 inside process_turn) is correctly ungated by design. The defect is that dispatch.py's reversal-arc builder (_build_marsh…  
*Repro:* Run the tutorial script for 6 turns (--objection trust): turn-6 dispatch leads with the crown line.  
*Fix:* ONE seam: the crown-fall headline producer in dispatch.py consults the same jealousy_dormant predicate (jealousy.py:212) before emitting; optionally the same for the 'crowned' arc beats in campaign_log.  
*Test:* tests/test_tutorial_school_fixes_2026_08_08.py: tutorial world, set a crown on Ney and a defeat event, build_morning_dispatch → assert no headline contains 'crowned'; campaign world with the same fixt…

**FA-99 [P4 · defect] `/load` drains `settlement_draft_notices` into a response the world-swap handler never renders (the same drain PC15-10 B0 fixed for the popup queue)**  
`backend/main.py:4079` · VERIFIED (Sept 2 verification), was UNVERIFIED (refuter budget exhausted; the finder's own cited evidence stands)  
`build_base_response` (main.py:446-449) unconditionally calls `world.drain_settlement_draft_notices()` (world_state.py:2008-2016: returns AND clears). `/load` (main.py:4079-4085) builds its response through it with only `include_popup_passthroughs=False`. The client's load handler `_apply_world_swap_response` (main.gd:4600-4665) reads message/HUD/wars/capture/interrupt/redemption only; `settlement_draft_notices` is rendered solely in `_on_command_result` (main.gd:2452 func, :2496). The notice is…  
*Repro:* w.pending_settlement_draft_notices=[{'war_id':'war_1','turn_discarded':3,'draft_clause_count':2,'selected_target_nation':'Austria','message_display':'x'}]; save; TestClient POST /load {'filename': ...}; assert main_module.world.pending_settlement_draft_notices…  
*Fix:* ONE seam: give `build_base_response` a `drain_draft_notices: bool = True` kwarg and pass `False` from `/load` (mirroring `include_popup_passthroughs=False`), so the notice rides the player's first `/command` exactly as the popups now do.  
*Test:* tests/test_save_load.py::TestApiEndpoints: world with one draft notice → save → POST /load → `world.pending_settlement_draft_notices` still has 1 entry and the next POST /command response carries `set…

**FA-100 [P4 · defect] `load_game` still wipes `threat_sources_this_turn` (and two siblings) that `from_dict` restores — the Balance-of-Europe tab reads 'No new threats' for the rest of any loaded turn**  
`backend/save_manager.py:240` · NARROWED (Sept 2 verification), was NARROWED (refuter corrected it; the corrected reading is what follows)  
world_state.py:7718-7725 (the `WorldState.from_dict` DialogueManager restore, right after the existing `conflict_alert` stale-item removal) is the correct seam, not save_manager.py:217-240. The underlying save/load defect is real — verified by direct reproduction via FastAPI TestClient (`/command` "fortify" → `/save` → `/load` → `/command` "Ney" silently reissues/objects to the pre-save fortify order) — but it is a BACKEND/API contract gap, not a live player-facing bug: `clarification_popup` is…  
*Repro:* w = WorldState.from_scenario(<europe_1805.json>); TurnManager(w, CommandExecutor()).end_turn({'world': w}); from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger; n0 = len(build_diplomatic_ledger(w)['balance_of_europe']['threat_sources_this_…  
*Fix:* Delete save_manager.py:240 (and :217/:218) as the sixth, seventh and eighth deliberate NON-clears, citing the same contract the block already documents: serialized under the mid-turn-save contract, restored by from_dict, cleared at the real boundary by `_advance_turn_internal` (:9253/:9257/:9263).  
*Test:* tests/test_save_load.py: `add_threat(world, 3, 'battle_win', target=world.player_nation)` → save → load → `build_diplomatic_ledger(loaded)['balance_of_europe']['threat_sources_this_turn']` equals the…

**FA-101 [P4 · defect] `pending_objection` at load: the KNOWN_SILENT remainder's named owner (WO slice 12) landed without it, and row WO is closed — but the state is unreachable through the UI**  
`backend/main.py:4120` · NARROWED (Sept 2 verification), was UNVERIFIED (refuter budget exhausted; the finder's own cited evidence stands)  
main.py:4120-4122 and WEIRD_OUTCOMES_SPEC.md:4414-4420 declare the tactical-objection-at-load legibility gap 'owned by slice 12'; slice 12's landing record (spec §3 Slice 12, lines 3291-3613) contains no mention of an objection (grep), the DoD at spec:4570 records slice 12 landed Sept 1, and CLAUDE.md declares row WO build-complete — an unowned deferral (Golden Rule 9). Reachability check for a future engineer: the objection dialog is modal (dialog_manager.gd:44 default `modal=true`) with only t…  
*Repro:* grep -n 'owner = row WO slice 12' backend/main.py; awk '/^### Slice 12/,/^### Slice 14/' docs/WEIRD_OUTCOMES_SPEC.md | grep -ci objection # 0  
*Fix:* Docs-only: strike 'owner = row WO slice 12' at main.py:4121 and BUG_FIXES.md WO-35, and record KNOWN_SILENT as ACCEPTED-UNREACHABLE with the modal/end-turn reachability argument above (or, if an owner is wanted, the 3-line attach guarded by `response.get('objection', {}).get('options')` so the buttonless strategic modal the memo feared cannot render).  
*Test:* A docs pin in tests/test_wo_slice15*.py's census: every KNOWN_SILENT entry either names an OPEN owner row in BUG_FIXES.md or carries an 'accepted-unreachable' reason string (grep both files).

### 3g. Harness — the instrument, not the game (25)

**FA-10 [P1 · harness] The driver's refused-choice memory turns a transient stale_dialogue refusal into a permanent ban — four flagship offers were never answered and an accept-policy run answered a settlement with 'request revision'**  
`tools/playtest_driver.py:932` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
`Answerer.scan` memorizes ANY reply with success False under the dialogue's identity (`tools/playtest_driver.py:932-935`) and `_dialogue_choice` never re-offers it. But the backend's W6-0 guard returns success False with `stale_dialogue: True` (`backend/commands/diplomatic_executor.py:3417-3431`) purely because a DIFFERENT dialogue is on top at that instant ('Sire, another matter has arrived since'); when the same dialogue is promoted again the driver has blacklisted its only sane answer, and a…  
*Repro:* Run the flagship script (tools/playtest_scripts/flagship_1805.json) with --objection insist --diplomacy decline --turns 10; on turn 9 observe '#17 → reject ↳ refused: another matter has arrived since' followed by '#17 → (left standing)' on the next command of…  
*Fix:* ONE seam: the refusal-memory write at tools/playtest_driver.py:932 — skip memorizing when the reply carries `stale_dialogue` (or any reply whose message is an ORDERING refusal rather than an executor refusal), i.e. `if reply.get('success') is False and not reply.get('stale_dialogue')`. Optionally re-scan the reply's own `diplomatic_dialogue` (the guard returns the dialogue actu…  
*Test:* tests/test_playtest_driver_instrument.py: StubTransport whose first POST /respond_to_diplomatic_dialogue reply is {success:false, stale_dialogue:true, diplomatic_dialogue:{...#19}} and whose second re…

**FA-36 [P2 · harness] An order-free last-stand ask is invisible to the end-turn response, so the playtest driver never answered Massena's question — and the shipped client only has the rail**  
`tools/playtest_driver.py:621` · VERIFIED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
At end turn only ORDER-BOUND interrupts surface: `_execute_strategic_turn` returns None for a marshal with no `strategic_order` (strategic.py:875-876) and re-emits `requires_input` only below that (:878-886); main.py:1316-1321 promotes only a strategic report; turn_manager.py and meta_executor.py contain no `pending_interrupt` handling at all (grep verified). The WO-35 marshal-level lift exists ONLY on `/load` (main.py:4122-4129). The driver reads exactly those two sources (`_interrupt_report`,…  
*Repro:* Run the latewar reproduction; compare `grep -c strategic_interrupt <run>/digest.md` (0) against the t7 save's marshals.Massena.pending_interrupt (last_stand).  
*Fix:* Backend half, ONE seam: apply the WO-35 marshal-level attach (main.py:4122-4129) at the end-turn response build too (the `if not response.get('pending_interrupt')` block at :1316), so an order-free decision rides the same key the client and driver already read. Driver half: none needed once the backend attaches it; until then, after each end turn the driver should GET the marsh…  
*Test:* tests/test_wo35_*.py sibling: raise a last_stand on an order-free player marshal during an enemy attack, POST 'end turn' through TestClient, assert `response['pending_interrupt']['interrupt_type'] ==…

**FA-37 [P2 · harness] Harness: the digest prints only the headline and treasury/net/provinces, so vassal losses and every Net component are invisible in all nine archived digests**  
`tools/playtest_driver.py:525` · VERIFIED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
Digest.ledger_line (tools/playtest_driver.py:525-545) prints treasury · net · threat · provinces from GET /ledger (driver:1379-1390 `dig(ledger,'treasury','gold')`, `dig(ledger,'net_gold','net')`), and dispatch() prints first_line(text) only (driver:551). The diplomatic rail (where defections, transfers, rebellions and eliminations land) and the signed components (Charges of Empire, Contributions, Requisitions, Blockade, Admiralty, Tribute) are never written.  
*Repro:* Run tools/playtest_driver.py --turns 14 --name probe-vassal --fresh --from-save tests/fixtures/playtest_saves/fixture_t20_ambient.json and read digest.md: no line ever says which Net component moved or that Holland/KingdomOfItaly changed status.  
*Fix:* ONE seam: Digest.ledger_line gains the signed components from ledger['economy'] (income/upkeep/charges/contributions/requisitions/blockade/admiralty/tribute) and Digest.dispatch prints every HIGH-priority diplomatic_events row (dtype + text) beneath the headline.  
*Test:* A driver run in which a French vassal is lost (patch the bribe RNG in a fixture-based script) produces a digest.md containing the vassal's name on that turn; and a run's LEDGER line contains 'charges'…

**FA-39 [P2 · harness] The 'live parser' arm measured nothing and no digest can tell: flagship-live is byte-identical to flagship-mock through turn 12, the LLM was consulted once in 37 commands, and neither parse mode nor the script path is recorded**  
`tools/playtest_driver.py:1271` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
Verified by running diff on the two archived digests (turns 1-12): zero differing lines. Verified by opening the live run's console (tools/playtest_runs/audit-flagship-live/server_console.log:1736 'LLM fallback: Soult, deal with the Austrians (confidence=0.5)', :1742 'LLM parse successful: unknown') — one escalation in 37 commands, and it returned 'unknown' exactly as mock's ASK arm does. The wire carries no provenance: ParseResult has `mode: 'mock' or 'live'` and `confidence` (`backend/ai/schem…  
*Repro:* diff <(sed -n '1,/^## Turn 13/p' docs/audits/playtest_digests/audit-flagship-mock/digest.md) <(sed -n '1,/^## Turn 13/p' docs/audits/playtest_digests/audit-flagship-live/digest.md) → only the 'Turn 13' header differs; grep -c 'LLM fallback' tools/playtest_runs…  
*Fix:* Two small seams, one each side: backend/main.py /command stamps display-only `parse_mode` + `parse_confidence` from the ParseResult onto the response (GR6-clean, read by nothing mechanical); tools/playtest_driver.py `Digest.command` records them and `meta` gains `script` (the resolved path) and `llm_source` ('cli'|'script'|'default'); take `threat_level` for the LEDGER row from…  
*Test:* tests/test_playtest_driver_instrument.py: run a 2-turn stub with --script → meta.json['script'] equals the path and the command records carry parse_mode; tests for main.py: a mock parse of 'Ney, attac…

**FA-40 [P2 · harness] The archived tutorial digest cannot evidence the lesson: the driver script fires beat VI outside its own window and its policy contradicts the card's counsel; the PC15-9 pin is ambient-only**  
`tools/playtest_scripts/tutorial_lesson.json:9` · VERIFIED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
tools/playtest_scripts/tutorial_lesson.json:9 fires `Senarmont, bombard Jellacic` at loop 4, but PC15-9 moved the beat's gate to 2 (tutorial_overlay.gd `bombardment` step; tests/test_pc15_fix_slice_2026_08_15.py:41-49) because Jellacic's hold is guaranteed only through T3. The archived digest ran with policy `objection: trust` (audit-tutorial/digest.md:3) while the card advises INSIST (overlay:93). So the archived T4 refusal 'Target out of range' (digest:35) reproduces the PC15-9 symptom outside…  
*Repro:* Run the tutorial script under either policy for 6 turns and read T4/T6; compare to the overlay's gate of 2 for beat VI.  
*Fix:* ONE seam: re-author tutorial_lesson.json to the STEPS gates (bombard at loop 2 or 3, `policy.objection: insist`) and add a sibling `tutorial_lesson_trust.json`; extend the PC15-9 pin into a TestClient-driven lesson walk that issues every chip at its gate under insist and asserts zero refusals — then re-archive the audit-tutorial digest from the corrected script.  
*Test:* tests/test_tutorial_scenario.py: drive /new_game tutorial + the STEPS chips in gate order via TestClient (objection answered 'insist'), assert every chip response has success True; a second parametriz…

**FA-41 [P2 · harness] The playtest digest never records what an answered popup DID — the campaign's Trafalgar, camp and lifted blockade are invisible in the archived record**  
`tools/playtest_driver.py:1176` · DUPLICATE (Sept 2 verification), was HARNESS (author-checked, no refuter)  
`drain` scans follow-up responses (the '1' clarification answer, `/strategic_response` answers) for further blockers but never writes their `message`; `digest.command` is called only for script commands (driver:1330/1350/1360); `dispatch` rows carry only the headline (driver:548). So the naval run's decisive fleet action (46 coalition sail lost on turn 5), the boulogne_camp beat (73,483 men, turn 6), `blockade_broken` for France/Holland/Spain (turn 7) and the refused Davout/Ney attacks all left…  
*Repro:* `.venv/Scripts/python.exe tools/playtest_driver.py --script tools/playtest_scripts/naval_descent.json --llm mock --turns 6 --name probe-x --fresh` then grep digest.jsonl for 'caught coming home' / 'TRAFALGAR' / 'THE CAMP' — zero hits, while the run's saves/eve…  
*Fix:* ONE seam: in `drain` (driver:1176), after `followups = answerer.scan(current)`, write each follow-up's `message` as a command row (`digest.command(f"↳ answer {choice}", followup)`), and extend `Digest.dispatch` to also record the HIGH-priority DIPLOMATIC EVENTS lines of the morning dispatch payload so beats that never lead (TRAFALGAR, THE CAMP, blockade broken) reach the digest…  
*Test:* Instrument test in tests/test_playtest_driver_instrument.py: drive naval_descent.json 6 turns in-process; assert a jsonl `command` row at turn 5 contains 'caught coming home' and a `dispatch` row at t…

**FA-72 [P3 · harness] Answer-policy artifacts the memo must not file as game behaviour — and one latent policy bug (the 'no' needle matches honor_defender, so a paradox declares war under decline)**  
`tools/playtest_driver.py:1100` · VERIFIED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
Each default is a decision with a measured consequence in the archived arms, verified by opening the option producers: (a) `interrupt: first` picks options[0] — `fight_to_the_last` for a last stand (combat_executor.py:3320) and `attack_anyway` for contact_bad_odds (strategic.py:1166) — so Ney's captivity (flagship 22→23) and the bad-odds attacks are the driver's choices; (b) `petition: first_enabled` picks `concede` on Fontainebleau (jealousy.py:2223 — rentes granted to every eroding marshal; fl…  
*Repro:* python: import tools.playtest_driver as pd; a=pd.Answerer(None,None,pd.POLICY_DEFAULTS,False); a._pick_dialogue_choice({'type':'commitment_paradox','options':[{'action':'honor_defender'},{'action':'break_defender_alliance'}]}) → 'honor_defender' under diplomac…  
*Fix:* ONE seam: `_pick_dialogue_choice` — match needles against `_`-split tokens of the option id, not substrings, and add explicit policy keys for the standalone decisions (`paradox`, `last_stand`, `contact`, `petition` per kind) whose defaults are the least state-changing arm (attempt_breakout / hold_position / acknowledge); document in PLAYTESTING.md §policy that 'first' means the…  
*Test:* tests/test_playtest_driver_instrument.py: `_pick_dialogue_choice` on the paradox shape under decline returns 'break_defender_alliance' (or the new paradox default), never 'honor_defender'; a last_stan…

**FA-73 [P3 · harness] Corpus rows 'Ney, cover the retreat' / 'Ney, fix bayonets' pin a fast-parser refusal as a LIVE contract the prompt never made — the 527/531 live result is a corpus error, and the real PS18-5 harm has no live pin at all**  
`tests/data/parser_golden_corpus.json:3462` · NARROWED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
tests/data/parser_golden_corpus.json:3460-3481 assert `success:false` + 'Unknown action' on `world: any` with NO `mock_only` flag (verified by opening), while the eleven sibling rows that pin V2-55 fast-parser refusal shapes (e.g. :261-270 'break through enemy lines') carry `mock_only: true` with the note that the live LLM 'legitimately interprets the utterance'. The live layer cannot refuse these: PARSE_TOOL (providers.py:164-172) allows 'unknown' only 'when the prompt's rules forbid guessing',…  
*Repro:* .venv\Scripts\python.exe -m backend.ai.parser_eval --live --id ney-cover-the-retreat --id ney-fix-bayonets → both FAIL on 'success' while every mock_only sibling is skipped.  
*Fix:* Mark both rows `mock_only: true` and add two `live_only` twins with `not_action: "retreat"` and `not_action: "repair"` respectively (the harness already supports both flags and `not_action`); optionally one prompt line under Valid Actions: 'an order naming a deed no listed action models (screening, drill, restoring order) → unknown'.  
*Test:* `parser_eval --live` reports 531/531; the twins turn red if the live parser ever returns retreat for 'cover the retreat' or repair for 'fix bayonets'; the mock harness keeps the refusal pins.

**FA-74 [P3 · harness] Harness: a REFUSED dialogue answer is recorded as answered, so the driver never retries an offer after its blocker clears — the digest under-reports the AI's offers and cannot tell a stale-order refusal from a real one**  
`tools/playtest_driver.py:909` · DUPLICATE (Sept 2 verification), was HARNESS (author-checked, no refuter)  
tools/playtest_driver.py:906-909 adds `did` to `_answered_dialogue_ids` BEFORE the POST reply is read; :931-935 then adds the refused word to `_refused_choices` keyed by dialogue id; `_dialogue_choice` (:987-1005) returns None once the only known word is refused → '(left standing)' (:904). So after the FA-28-style stale refusal the SAME offer, now legitimately active and re-derived by the safety valve on every response, is logged '(stale passthrough — #17 already answered this chain)' (audit-flags…  
*Repro:* Run any scripted arm where a proposal and a settlement offer are both pending and a petition/advisory precedes them (flagship script turn 9); read digest.md for '(stale passthrough' followed by '(left standing)' on the same dialogue id.  
*Fix:* In the dialogue arm (driver:906-935): only add `did` to `_answered_dialogue_ids` and `_refused_choices` when `reply.get('stale_dialogue')` is falsy; on a stale refusal, leave the id un-answered so the next passthrough of that id is answered again (one retry per chain).  
*Test:* Driver unit test with a fake transport: first POST returns `{'success': False, 'stale_dialogue': True}`, the re-derived dialogue with the same id appears on the next response, and the driver POSTs aga…

**FA-75 [P3 · harness] Harness: ambient runs never see major-court proposals — the deferral rule plus a letter-book-only mailbox read means Prussia's recurring open-borders overture and Britain's settlement offer are invisible in every 'Europe acts' digest**  
`tools/playtest_driver.py:1323` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
`_apply_command_popup_contract` (main.py:1353-1362) defers every choice popup on an `enemy_phase` response, so an end-turn-only run never receives `incoming_proposal`/`incoming_settlement_offer` on the wire; the driver's only mailbox read is `answer_envoy_digest((GET /mailbox).envoy_digest)` (driver:1320-1324, :939-970), which walks digest rows only — `is_routine_small_court` excludes majors by tier (envoy_digest.py:78-82) — and it never calls /pending_envoy or /mailbox/activate (grep: no such c…  
*Repro:* Loop 10×: GET /mailbox (items minus envoy_digest ids) → POST /command 'end turn' → check `incoming_proposal`, `incoming_settlement_offer`, `lapsed_offers` on the response. Or read audit-ambient40/digest.md: no POPUP line in 40 turns.  
*Fix:* Driver (one loop site, :1320-1324): after answering the digest, walk the remaining `/mailbox` items, `POST /mailbox/activate {mailbox_id}` each and answer the returned payload through the existing dialogue arm; log each. Backend (one tuple, main.py:554): add 'lapsed_offers' to `_COMMAND_RESULT_SIMPLE_FIELDS` so the digest can print lapses.  
*Test:* Driver test with a fake transport whose /mailbox returns one digest row and one major-court row: assert one /mailbox/respond AND one /mailbox/activate + /respond_to_diplomatic_dialogue are posted. Bac…

**FA-76 [P3 · harness] Harness: follow-up answers' responses are never digested — the run's Trafalgar left no line**  
`tools/playtest_driver.py:816` · DUPLICATE (Sept 2 verification), was HARNESS (author-checked, no refuter)  
`scan()` answers a clarification by posting `{'command': '1'}` (tools/playtest_driver.py:816) and `drain()` (:1176) only re-scans the follow-up for further blockers; `digest.command()` (:383) is called for scripted commands only. The reissued 'order the diversion confirmed' (and every answered strategic_interrupt / objection follow-up) resolves off-record.  
*Repro:* tools/playtest_driver.py --script tools/playtest_scripts/naval_descent.json --turns 6 --llm mock --fresh --name probe-x; grep -c 'caught coming home' tools/playtest_runs/probe-x/digest.md → 0 while server_console.log shows the resolved answer.  
*Fix:* In `drain()`, after `answerer.scan(current)` returns follow-ups, record each follow-up's response through `digest.command(f'↳ {answer}', response)` (one new indented row kind 'followup') so the outcome message lands beside the answer.  
*Test:* Driver self-test: a scripted 'order the diversion' under mock with a forced-fail seed produces a digest row containing 'caught coming home' and the sail figure; a strategic_interrupt answered 'attack'…

**FA-77 [P3 · harness] Harness: the digest records no end-turn strategic-order progress, so stalls, reroutes, silent lost turns and 'Order cancelled' lines are invisible to every archived run**  
`tools/playtest_driver.py:699` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
`Answerer` (tools/playtest_driver.py:695-706) reads `strategic_reports` only to count `battle_details`/`action=='combat'` rows, and `_interrupt_report` (:620-631) takes the FIRST awaiting row; a report's `message` ('Ney marches to Munich. 2 region(s) to Vienna.', 'Ney reroutes around Hanover territory…', 'Order cancelled: …halts at the water's edge…') is never digested. The default `interrupt: first` policy answers `investigate` to cannon fire — i.e. ABANDON the scripted march — and `attack` to…  
*Repro:* `tools/playtest_driver.py --script <a script with 'Ney, march to Vienna' on turn 1> --turns 6 --fresh --name probe-strat` → digest shows the issuance echo and nothing about turns 2–5 of the march.  
*Fix:* ONE seam: in the same loop at :699, digest every non-input report's `message` (and `order_status`) as a bullet under the enemy-phase block, and stamp the chosen interrupt answer's meaning ('investigate = abandon order') next to the popup line.  
*Test:* harness test: a driver run with a 4-hop march produces four progress lines and, on a covered crossing, the 'halts at the water's edge' line; the digest for the naval script line-80 case shows the rero…

**FA-78 [P3 · harness] Harness: the driver ignores `enabled: false` on dialogue options, so the propose arm pressed a disabled 'Send as suggested' twelve times and its refusals are artifacts — WIN-1 holds in the game**  
`tools/playtest_driver.py:1069` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
`_pick_dialogue_choice` (driver:1007-1069) resolves `proposal_confirm` through the type table and returns the literal 'confirm' (:1069-1070) without consulting `_enabled` (:592-594, used only by the petition/interrupt arms at :738/:824). Verified by running at ccf5f111: 'propose peace with Austria' returns `execute_proposal` with `enabled: False` and the remedy in `description` ('I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria … Settle the war jointly at the set…  
*Repro:* TestClient: POST /command 'propose peace with Austria' at boot; inspect `diplomatic_dialogue.options[0]` → enabled False; POST /respond_to_diplomatic_dialogue {choice:'confirm', dialogue_id} → refused. Then run `playtest_driver.py --turns 2 --diplomacy propose…  
*Fix:* In `_pick_dialogue_choice` (driver:1007): filter `options` through `_enabled` before the type table and keyword scans; if the policy's word maps to a disabled option, log '(disabled: <description>)' and take the first enabled option or leave standing.  
*Test:* Driver unit test: a proposal_confirm dialogue whose `execute_proposal` is `enabled: False` → the driver never posts 'confirm'/'execute_proposal' and the digest line names the disabled reason.

**FA-79 [P3 · harness] Harness: the driver's default redemption policy DESTROYS the marshal, its petition policy always takes the free first arm, and the redemption outcome is never logged — no archived campaign exercises the paid or recoverable arcs**  
`tools/playtest_driver.py:152` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
tools/playtest_driver.py:152 sets `"redemption": "dismiss"` (permanent `destroy_marshal`, disobedience.py:1756) and :155 `"petition": "first_enabled"`; lines 820-829 pick the first `_enabled` option, which by construction is the free 'Let it stand' (jealousy.py:2044-2046), 'Accept the Breach' (2153), 'Give him a front' (2338) or 'concede' (2214); lines 866-871 post `/respond_to_redemption` but record only the choice, never the result message. Archived consequence: audit-flagship-mock has 10 `jea…  
*Repro:* Run `tools/playtest_driver.py --turns 14 --script tools/playtest_scripts/flagship_1805.json --fresh --name probe-marshal` and grep the digest: every marshal_petition line ends in the first option; the redemption line has no outcome sentence; the dismissed mars…  
*Fix:* ONE seam, the policy table + step 4/6b of `_answer_popups`: default `redemption` to `grant_autonomy` (non-destructive), add `petition` values `rotate` (cycle enabled arms per kind) and `paid_first` (prefer arms with `ap_cost`), and write the `/respond_to_redemption` and `/marshal_petition_response` result `message` into the digest like every other answer (`self.d.popup(...)` al…  
*Test:* tests/test_playtest_driver_policies.py: a scripted world where a marshal crosses 20 -> under the default policy no `fallen_marshals` entry appears and the digest contains the redemption outcome messag…

**FA-83 [P3 · harness] The `--diplomacy accept` arm never completes an incoming settlement acceptance — every accept is refused as stale/queued, so no archived digest shows France accepting an AI peace offer**  
`backend/commands/diplomatic_executor.py:3421` · NARROWED (Sept 2 verification), was AUTHOR-VERIFIED(hand-reproduced this session)  
In the late-war digest (accept policy) the driver answered `incoming_settlement_offer #29 → accept_settlement_offer` and was refused 'Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered' (t23), then `#8` was refused 'the settlement of war_2 is already on the table' (t23), then `#30 → accept` was refused again for Switzerland and `#29 → request_settlement_revision` produced a review-table restatement (t24). The refusal is the W6-0 stale-dialogue g…  
*Repro:* .venv/Scripts/python.exe tools/playtest_driver.py --from-save tests/fixtures/playtest_saves/fixture_t20_ambient.json --turns 6 --diplomacy accept --name probe-accept --fresh → grep the digest for 'accept_settlement_offer' and 'another matter has arrived since'…  
*Fix:* Driver: in `tools/playtest_driver.py`'s `drain()`, after any refusal carrying `stale_dialogue: True`, re-read the current dialogue from `GET /mailbox` (or the refusal's attached `diplomatic_dialogue`) and answer THAT id, then record whether the originally delivered popup id ever became answerable — which also yields the measurement that decides whether a human is affected (the…  
*Test:* `tests/test_playtest_driver_stale_dialogue.py`: two incoming offers queued in one turn on the t20 fixture → the accept policy ratifies the head offer and the digest shows one `accept_settlement_offer…

**FA-84 [P3 · harness] The archived digest is blind to AI-vs-AI diplomacy — 'did an AI war open, did a coalition form or dissolve' cannot be answered from the nine arms, and the enemy-phase summary prints the counter-punch banner**  
`tools/playtest_driver.py:1392` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
`Digest.dispatch` records only `first_line(text, 200)` of `/dispatch` (playtest_driver.py:548-552, called at :1392); nothing reads `GET /campaign_log`. So the only AI-AI beat in the whole archive is the propose arm's headline 'Britain and Spain have made peace without us' (audit-propose:161), which survived only because it happened to be the headline. A 14-turn in-process probe on the same 1805 boot recorded 127 `ai_ai_proposal_refused`, 2 `diplomatic_ai_ai_treaty`, 3 `design_promoted` (Austria→…  
*Repro:* .venv/Scripts/python.exe tools/playtest_driver.py --turns 8 --name probe-aidiplo --fresh, then compare digest.md against `GET /campaign_log` on the run's autosave: design_promoted / diplomatic_ai_ai_treaty / nation_eliminated rows are absent from the digest; g…  
*Fix:* ONE seam: the driver's per-turn loop after `/dispatch` (playtest_driver.py:1392): read `GET /campaign_log` for the just-ended turn (already fog-filtered and IGR-B-collapsed) and print an allowlist of diplomatic types (crisis_brewing/coercive_demand/crisis_passed/diplomatic_ai_ai_treaty/design_promoted/volte_face/coalition_formed/coalition_dissolved/nation_eliminated/third-party…  
*Test:* A driver-level test (tests/ for tools/playtest_driver.py): a world whose log carries one `design_promoted` and one `diplomatic_ai_ai_treaty` → the digest contains matching EVENT lines; an enemy-phase…

**FA-85 [P3 · harness] The committed naval script stages its expedition marshal at Normandy — not a French yard — so the archived naval digest carries zero expedition evidence**  
`tools/playtest_scripts/naval_descent.json:7` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
`tools/playtest_scripts/naval_descent.json` marches Soult to Normandy on turn 2 and types `land Soult in Munster with 12,000 men` on turns 12–13; `naval_executor._execute_naval_expedition` refuses unless the marshal stands at a controlled dockyard (`naval_executor.py:205-212`) and France's authored yards are Brittany/Provence/Flanders/Bordelais (`europe_1805.json:918`) — Normandy is not one. The archived naval digest therefore records two refusals ('Soult must stand at one of our yards: Brittany…  
*Repro:* .venv/Scripts/python.exe tools/playtest_driver.py --script tools/playtest_scripts/naval_descent.json --turns 14 --name probe-naval-yard --fresh → read `tools/playtest_runs/probe-naval-yard/digest.md` turns 12–13: the `land` command is refused both times; grep…  
*Fix:* Script edit: turn 2 → `Soult, march to Brittany` (or use Ney, already at Flanders, as the landing marshal) and move the `land` command to a loop index after arrival; plus a driver guard in `tools/playtest_driver.py` that marks a run `⚠ SCRIPT PRECONDITION` when every `land`/`naval_expedition` command in a script is refused, so a naval digest cannot silently carry no naval evide…  
*Test:* `tests/test_playtest_scripts_preconditions.py`: for every committed script containing a `land X in Y` command, a dry-run on the mock world confirms marshal X's scripted position at that loop index is…

**FA-86 [P3 · harness] The playtest digest prints a 40-character '=' banner in place of every bombardment, hiding seven turns of British artillery fire**  
`tools/playtest_driver.py:236` · DUPLICATE (Sept 2 verification), was HARNESS (author-checked, no refuter)  
The bombardment result message begins with `'=' * 40` on its own line (combat_executor.py:3931-3934: banner, `BOMBARDMENT: A → B`, banner, prose) and the driver's `first_line` (tools/playtest_driver.py:236-244) returns the first non-empty line, so both the enemy-phase summary (:445-449) and the per-action rows render `========================================` for every artillery attack.  
*Repro:* `.venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'tools'); from playtest_driver import first_line; print(repr(first_line('='*40+'\n BOMBARDMENT: Shrapnel → Massena\n'+'='*40+'\nguns thunder')))"` → `'========================================'`.  
*Fix:* ONE seam: `first_line` skips lines containing no alphanumeric character (so the `BOMBARDMENT: A → B` line surfaces); alternatively drop the banner from the message at combat_executor.py:3931, which also cleans the enemy-phase dialog.  
*Test:* `first_line('='*40 + '\n BOMBARDMENT: A → B\n' + '='*40)` returns `'BOMBARDMENT: A → B'`; a driver digest containing an AI bombardment never contains a row whose text is only '=' characters.

**FA-87 [P3 · harness] The playtest digest shows backend message noise ('====', '[Shield]…', '[Square broken…]') the client never renders, and archives only the dispatch's first line**  
`tools/playtest_driver.py:446` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
`Digest.enemy_phase` summarises each attack by `first_line(a.get('message'))` (tools/playtest_driver.py:446-447): for a bombardment that is the `'=' * 40` banner (combat_executor.py:3932), for a field battle the tactical prefix `\n[Shield] …`/`[Combat] …` (combat.py:35-48), for a square-breaker the `[Square broken — …]` prepend (tactical_executor.py:481) — and the `🏴` capture detector greps 'captur' in the same prose (:462), which is why '[Combat] ArchdukeJohn's DEFENSIVE stance hampers…' is lis…  
*Repro:* grep -c '========================================' docs/audits/playtest_digests/audit-ambient40/digest.md → 6; open enemy_phase_dialog.gd and search for `message` inside `_format_action` → none.  
*Fix:* ONE seam — `Digest.enemy_phase`: summarise from `ai_action` (marshal/verb/target) plus event types the way the client does (bombardment → 'Moore bombards Ney (2,269 casualties)'; garrison_assault → losses; battle → the ⚔ row it already emits), and `Digest.dispatch` → record `headline.class`, `headline.text`, `sub_beats` and `len(turn_events)` from the JSON instead of the first…  
*Test:* tests/test_playtest_driver.py: a synthetic enemy-phase row with `bombardment_result` and a `'='*40` message summarises as 'X bombards Y (N casualties)'; a dispatch with two sub-beats archives all thre…

**FA-88 [P3 · harness] The playtest driver records which interrupt button it pressed but never what happened next, so refused attacks and cancelled orders read as if the march continued**  
`tools/playtest_driver.py:745` · DUPLICATE (Sept 2 verification), was HARNESS (author-checked, no refuter)  
`Answerer.scan` digests a strategic interrupt as 'POPUP strategic_interrupt: … → <choice>' and posts `/strategic_response` (tools/playtest_driver.py:732-753), but the follow-up reply is only re-scanned for further popups and `battle_report`/`battle_details` (:681-716); unlike the diplomatic arm's '↳ refused:' line (:914-921) its `message`/`order_cleared` are never written. The `interrupt: first` policy (:158) always takes the first option, which for `combat_stalemate` is the cancelling `continue…  
*Repro:* tools/playtest_driver.py --script tools/playtest_scripts/naval_descent.json --turns 14 --name probe-orders --fresh; read digest.md Turn 14: the `attack_anyway` answer has no result line, and the run's jsonl carries the `/strategic_response` reply with 'Assault…  
*Fix:* ONE seam: in `scan()` right after the `/strategic_response` post, write `↳ result: <first_line(reply['message'])>` and append ' (order cleared)' when `reply.get('order_cleared')`, mirroring the diplomatic '↳ refused:' arm; optionally add an `--interrupt` policy value so `combat_stalemate` is answered `cancel_order` explicitly rather than by position.  
*Test:* tests/test_playtest_harness_*: feed a `/strategic_response` reply `{success: True, message: 'X cannot break through. Orders cancelled…', order_cleared: True}` through the answerer → the digest carries…

**FA-89 [P3 · harness] The tutorial arm cannot see the School: beats and advancement live in tutorial_overlay.gd, so the audit-tutorial digest proves only that the scenario boots and its script still teaches the beat-IV refusal**  
`godot-client/project-sovereign/scripts/tutorial_overlay.gd:297` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
Verified by opening godot-client/project-sovereign/scripts/tutorial_overlay.gd: STEPS (:52), `_derive_step_for_turn` (:297), `observe` (:313), `_advance_one` (:354) — the tutor card's progression is computed client-side from response payloads; the backend exposes no tutorial state (backend/main.py:120-122 only allowlists the scenario). The driver therefore cannot assert that a beat fired, and the archived audit-tutorial digest is a plain scripted run. Its script (tools/playtest_scripts/tutorial_…  
*Repro:* .venv/Scripts/python.exe tools/playtest_driver.py --scenario tutorial --script tools/playtest_scripts/tutorial_lesson.json --turns 10 --fresh → digest.md turn 4 shows the bombard refusal; nothing in the digest names a tutorial step.  
*Fix:* ONE seam: a display-only `GET /tutorial_state` (or a `tutorial_step` field on /command responses when scenario_name == 'tutorial') derived from the SAME payload predicates `_derive_step_for_turn`/`observe` read, so the overlay and the driver consume one source; the driver logs `SCHOOL: step N (<beat name>)` per turn and `--strict` fails when a scripted beat's precondition is re…  
*Test:* tests/test_tutorial_position7.py: for each STEPS entry, an in-process run of tutorial_lesson.json asserts the backend-reported step advances on the turn the script's suggest fires and that the suggest…

**FA-90 [P3 · harness] Three driver arms that do not exist and would answer the questions the archived arms cannot: the Negotiator, the Emperor Pays, and the Defended Homeland / LLM gauntlet**  
`tools/playtest_driver.py:129` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
Derived from what the eight archived arms structurally could not reach (each gap verified above): (1) THE NEGOTIATOR — `--diplomacy negotiate`: polls /pending_envoy and /mailbox items every turn, ACCEPTS counter-offers and settlement offers, walks `accept_settlement_offer` → settlement_confirm → confirm_settlement to ratification, and digests `peace_ratification_summary` (backend/main.py:588-600, a key the driver never reads) so a digest finally says WHAT was signed; today no unattended run has…  
*Repro:* grep -n 'peace_ratification_summary\|"notifications"\|pending_envoy' tools/playtest_driver.py → no matches; ls tools/playtest_scripts/ → no homeland-defence or sub-gate LLM script.  
*Fix:* Add three policy/script arms to tools/playtest_driver.py: `--diplomacy negotiate` (the /pending_envoy + mailbox/activate loop of FA-75 plus the settlement_confirm→confirm_settlement ladder and a RATIFIED digest line from peace_ratification_summary), `--reward pay|ignore` (rail-driven typed reward commands + rail-driven fate words), and two committed scripts `homeland_defenc…  
*Test:* tests/test_playtest_driver_instrument.py: (1) StubTransport settlement ladder: incoming_settlement_offer → accept → settlement_confirm → confirm → reply carrying peace_ratification_summary produces a…

**FA-91 [P3 · harness] test_serialization_enforcement.py cannot see the field classes that have actually bitten (private, lazily-created, load-cleared) and never round-trips a played world**  
`tests/test_serialization_enforcement.py:389` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
The enforcement suite is the standing gate for "if it exists on the object, it must serialize", but (1) `get_instance_attributes` drops every `_`-prefixed name (tests/test_serialization_enforcement.py:31-38), so `_recovery_destination` — the IGR-X1 P1 save crash — and the six serialized `_capital_proximity_last_alert`-style privates were and are invisible to it; (2) the WorldState test asserts to_dict KEYS on a fresh legacy `WorldState(player_nation='France')` (:389-440) and never calls from_dic…  
*Repro:* Run the probe: PYTHONHASHSEED=0 .venv/Scripts/python.exe <scratch>/probe_roundtrip.py — the census section prints the transient names; comment out one `to_dict` key of a live field and only the probe (not the suite's world test) sees the from_dict divergence.  
*Fix:* Add ONE test file `tests/test_serialization_played_world_census.py` that boots the 1805 scenario, drives 3 turns through TestClient `/command` (orders + end turns), then asserts (a) `w.to_dict() == WorldState.from_dict(w.to_dict()).to_dict()` and `load_game(save_game(w)).to_dict()` equal modulo a named allow-set, and (b) for every marshal/region/world, `set(vars(obj)) - to_dict…  
*Test:* The file above; mutation checks: (i) add `self._probe = 1` to Marshal.__init__ → test must fail; (ii) stamp `marshal.foo = 1` inside `_execute_attack` → must fail; (iii) remove `"_recovery_destination…

**FA-92 [P3 · harness] tools/mutation_sweep.py reports a mutation that CRASHES the module as KILLED — a broken `new` string makes every named test error and the sweep prints perfect health**  
`tools/mutation_sweep.py:84` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
Verified by opening tools/mutation_sweep.py:73-87: after applying the mutation the harness runs pytest and classifies solely on `proc.returncode != 0` → KILLED. `_baseline_green` (:29-47, added Aug 23) only guards the PRE-mutation state; a `new` that introduces a SyntaxError/NameError at import, or that breaks the boot path every test in the file shares, makes all tests ERROR and is counted as a kill. The record already knows the failure mode by hand ('eight bad mutations' across slice 10's five…  
*Repro:* Write a one-entry sweep JSON whose `new` replaces a function's first line with `raise RuntimeError('boom')` at module scope for any backend module the target test imports; run `python -m tools.mutation_sweep that.json` → prints KILLED for a mutation no asserti…  
*Fix:* ONE seam: the classification at :84 — run pytest with `-rA`/`--junitxml` and require at least one test to have PASSED or FAILED (not ERROR) in the run; if every outcome is ERROR or collection failed, report BROKEN (a bad mutation) instead of KILLED and return non-zero.  
*Test:* tests/test_mutation_sweep_harness.py: a fixture repo dir with a tiny module + test; mutation A flips an assertion (expect KILLED), mutation B inserts a module-level `raise` (expect BROKEN), mutation C…

**FA-102 [P4 · harness] No archived arm ever saves and reloads mid-campaign — every save-transparency defect is invisible to the driver**  
`tools/playtest_driver.py:1353` · NARROWED (Sept 2 verification), was HARNESS (author-checked, no refuter)  
tools/playtest_driver.py can snapshot (`--save-at` → POST /save at :1353-1355) and boot from a fixture (`--from-save` → POST /load at :1283-1290, drained at :1296 so re-attached questions ARE read) but has no in-run reload. All nine archived arms are fresh boots except audit-latewar-t20, whose only load is the boot line (digest.md line 4: 'loaded save `fixture_t20_ambient.json` → Loaded: fixture-gen_t20'), a turn-boundary snapshot carrying no pending question. REV-F1, WO-23 and the three finding…  
*Repro:* grep -n 'reload' tools/playtest_driver.py # nothing; grep -l 'loaded save' docs/audits/playtest_digests/*/digest.md # only audit-latewar-t20, at boot  
*Fix:* ONE flag `--reload-every N`: after every Nth `end turn`, POST /save to the run's sandboxed SAVE_DIR then POST /load the same file (drained through the existing `drain()` so re-attached questions are answered by policy), and stamp the round trip in the digest. The contract: with `--reload-every 1` the digest must be byte-identical to the no-reload run of the same script and seed…  
*Test:* tests/test_playtest_driver*.py: run tools/playtest_scripts/smoke_battle.json for 4 turns with and without `--reload-every 1` → digests identical after stripping the 'loaded save' lines; then a negativ…

## 4. Corrections — what the refuters killed

Only two claims were put to a refuter and died; both died to a probe the
refuter ran itself, and both are recorded here rather than dropped. (The small
number is a budget fact, not an accuracy claim — see §0.)

- **Britain guards the Channel against a descent that can no longer happen — the blockade lever is switched off by a spent camp** (`backend/game_logic/naval.py:1548`) — [REFUTED] Both halves of the claimed mechanism are real code behavior but neither is a defect — both are explicit, deliberately-designed rules the spec states in plain prose and defends with reasoning, so the finding mischaracterizes intended design as an AI blind spot / broken promise. (1) `derive_ai_postures` (naval.py:1537-1557, verified by reading) does exactly what the finding describes mechanically: it flips an island nation to 'guard' whenever ANY enemy's `camp_turns >= DESCENT_CAMP_STAGED_TURNS` (2) OR `window_turns > 0`, with no read of `diversion_used` or any crossing ratio. But NAVAL_SPEC.md:…
- **Conquests are never held: the AI cannot garrison a fresh capture, so provinces ping-pong and a 4,700-man corps walks sixteen French provinces** (`backend/ai/enemy_ai.py:4086`) — [REFUTED] The stated causal mechanism does not match what the code does, and I falsified it empirically. I ran an 8-turn ambient probe (`playtest_driver.py --turns 8 --fresh`, AI_DEBUG=1) and captured all 252 `P6.75` evaluations from `tools/playtest_runs/probe-mechanism-garrison2/server_console.log`. The rejection-reason breakdown is: fortified 77, already-garrisoned 58, at-cap-3/3 24, drilling 19, fully-surrounded 18, too-weak(<20k) 50, already-in-region 1 — and ZERO rejections for 'enemy in region' or 'enemy adjacent' (the two branches at enemy_ai.py:4148 and :4151-4154, confirmed by opening the file…

## 5. What is working

Forty-one working-well notes came back with the findings; they are the reason
the verdict above is "joins, not systems". Deduped:

- **Working well: petitions arrive with honest arms — non-AP gates keep their reason, AP-only gates are re-derived at delivery** — The lens question 'are petitions arriving with disabled arms?' is answered No by construction: `_command_option` bakes `available: False` + `unavailable_reason` for a non-AP refusal (jealousy.py:1779-1795) while `refresh_petition_affordability` (1870-1950) is subtractive and re-derives only `ap_cost` arms against live AP at the delivery seam (main.py:1657-1659), and a refused answer hands back the refreshed card rath… (`backend/game_logic/jealousy.py:1870`)
- **Working well: the Marshalate closes the roster loop — a lost marshal's name routes to the bench only when the commission gate would pass, and the AI commissions unprompted** — `_addressed_lost_marshal_refusal` (main.py:893-945) refuses by tombstone and appends the bench hand-off only when `first_affordable_commission` (recruitment.py:114) would grant it now — the archived flagship shows the exact sentence at line 311 ('...His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission...'), and `check_commission` (recruitment.py:157-184) states gold / pool /… (`backend/game_logic/recruitment.py:157`)
- **Working well: the typed pending-question channel never lands on the wrong question, and every block names its own answer words** — Across all nine archived digests every '↳ refused' dialogue line is a refusal, never a misapplied answer (the W6-0 id binding, diplomatic_executor.py:3404-3432; the CA9 court-name binding :3435-3440). The typed router (main.py:2202-2262) answered 'trust'/'insist' correctly in audit-flagship-mock:8,179,207 and audit-tutorial:15; capture tokens route stage-aware (capture_executor.py:63-87, 312-320); the interrupt match… (`backend/main.py:2202`)
- **Working well: the non-draining discipline now covers the endpoints whose client callbacks ignore popup keys, and /load re-attaches the three plain-field questions** — `_fill_popup_keys_without_draining` (main.py:1509-1533) is applied at /capture_choice (:3538-3546), /respond_to_objection (:3254-3263), /respond_to_redemption (:3601-3618), /respond_to_glorious_charge (:3684-3697), /strategic_response (:3753), /load (:4083-4090), /save (:3996-4004), /notifications/dismiss (:5047-5057), /cancel_order (:4977) and /mailbox/respond (:4670-4673); /load additionally re-attaches `pending_ca… (`backend/main.py:1509`)
- **The enemy-phase dialog is robust to backend message noise — none of the three digest artefacts reaches the player** — Because CA8-6 sourced every enemy line from STRUCTURED fields and deliberately never pipes the server `message` (enemy_phase_dialog.gd:121-272, comment block at the `grant_dotation` arm), the '========================================' bombardment banner (combat_executor.py:3932) renders as 'Moore bombards Ney' + the Bombardment Report (`_format_bombardment_report`, :406-428), '[Shield] Massena is at his best with his… (`godot-client/project-sovereign/scripts/enemy_phase_dialog.gd:121`)
- **Direction-aware capture headlines, the repeat-aware rout clause and the standing-crisis escalation ladder all fire live** — `enemy_marshal_captured` (dispatch.py:652-660) led with 'Sire — Marshal Archduke John of Austria is taken at Tyrol — he is our prisoner, and their order of battle is one commander shorter.' (audit-flagship-mock digest.md:147) — the CA9-F12 direction split working as built; the `victory_won` rout clause rotates on `battle_counts` (:1017-1022, `_rout_clause` :1737): 'Paget's corps breaks a second time on this ground an… (`backend/game_logic/dispatch.py:652`)
- **Save round trip is byte-identical on the played 1805 board; the dynamic census finds only the documented transients** — After three full TurnManager turns on the shipped 1805 scenario (enemy AI, AI diplomacy, strategic orders, jealousy pass), `json(to_dict())` → `from_dict` → `json(to_dict())` is identical (sort_keys), and a vars()-vs-to_dict census over every live marshal, region and the world finds no unserialized public state beyond the documented set: marshals carry only `COORDINATION_TRANSIENT_FIELDS` (marshal.py:677-686, all 0.0… (`backend/models/world_state.py:6851`)
- **The pending-question table: every question the player can be mid-answering round-trips, and the load path either re-attaches it or lets the first command re-mount it** — Table (store → round-trips → raised at load): tactical objection `world.pending_objection` (world_state.py:6928/:7527) → yes → NO, deliberate (see the WO-35 row; the executor block names the answer words, executor.py:961-991). Strategic objection `pending_strategic_objection` (:6930/:7529) → yes → NO, but it blocks nothing and LAPSES at the boundary with a told `strategic_objection_lapsed` event (:9337-9370, WO-38).… (`backend/main.py:4094`)
- **launch.bat + README_TESTER: mock-default, honest health poll and stale-server guard are exactly right for a stranger** — launch.bat reads config.txt only if present, treats the placeholder as no key and runs LLM_MODE=mock (deploy/launch.bat:17-36), refuses to double-start when port 8005 already answers (:52-56), polls GET /test for 30 s with a stated failure branch naming the server window (:66-84), and kills the server by window title on exit. README_TESTER.txt leads with 'Nothing else. No account, no key, no internet' and the School… (`deploy/launch.bat:35`)
- **Main menu honesty: buttons disabled with the reason, Continue shows the calendar label, Settings reports the parser state truthfully** — main_menu.gd polls GET /test and /saves and disables Begin/School/Continue/Load with the war-office status shown (:493-533; Continue renders 'Continue · Early October 1805' from the save's calendar_label :512-518). settings_panel.gd's parser status distinguishes OFF / YOUR key / .env key / no key (:236-252) and the key never echoes (:170-173). (`godot-client/project-sovereign/scripts/main_menu.gd:493`)
- **The camp lever and the crossing gate both did their jobs: 40,000 men at Normandy pulled the Royal Navy home, and Moore never crossed** — `derive_ai_postures` flips an island fleet to GUARD when the enemy camp is staged; the re-run shows France unblockaded from end of turn 6 (readiness 50→55→60→65, build rate back to 2, trade restored) purely from massing Ney/Davout/Soult on the authored camp provinces — with the authored `boulogne_camp` beat telling the player to expect it. On the other side, Britain's AI took the historical road: Paget put 5,000 men… (`backend/game_logic/naval.py:1560`)
- **WORKING WELL — the nation-name arm and the enemy-addressee refusal answer honestly and teach the map** — Verified by running: `Ney, march to Saxony/Bavaria/Austria/Prussia/Switzerland/Hesse/Holland/Denmark/Sweden/Portugal/Spain` → "X is a nation, not a province. Name a province, Sire — theirs are Dresden." (nation_names.py:95, `resolve_typed_nation` :44, checked before the typo gate at parser.py:1276-1290 — verified by opening), which matters because `saxony→savoy` PASSES `_plausible_name_typo` (verified by running) and… (`backend/ai/nation_names.py:95`)
- **WORKING WELL — negation, contingency and CR-4 context carryover resolve to what the player meant** — Verified by running on the 1805 boot: `Ney, I don't want you to attack Mack` → "Then no order goes out, Sire — I have relayed nothing. If a standing order is to be stood down, say 'cancel his order'…"; `Ney, attack Mack only if the odds are good` → "that is a contingency, not an order — I have no way to hold a dispatch until the enemy moves"; `Ney, do not attack, just hold` → HOLD Rhineland; `Ney, attack Mack, not De… (`backend/commands/context_carryover.py:353`)
- **Working well: the naval crossing refusal is honest, numeric and remedial on the direct move, and the strategic stall arm reuses the same sentence** — `move_refusal_probe` sites the crossing gate first (backend/commands/movement_executor.py:153-170) and `crossing_check` (naval.py:1025-1036) names the gap and both remedies; the PF-8-style naval stall arm carries it into `Order cancelled: …'s march halts at the water's edge — …` (strategic.py:1118-1125) and the pursuit twin (:1596-1603). (`backend/commands/movement_executor.py:161`)
- **Working well: the SUPPORT acceptance line states the order's own reach, roll and lapse rules** — `_execute_strategic_command`'s SUPPORT branch (backend/commands/strategic_executor.py:629-668) tells the player exactly what the standing order buys: 'holds your written order: when X leads a battle within reach, he will march to the guns' + 'The order lapses of itself once X is out of danger — name a duration to hold him to it', plus Berthier's fortified/square caveat — matching the mechanic at strategic.py:2049-213… (`backend/commands/strategic_executor.py:647`)
- **The Grouchy moment is delivered deterministically by personality — and the literal's silence is narrated** — VISION's signature beat is fully implemented at one seam: `_check_interrupts` returns nothing for a literal marshal ('LITERAL NEVER GETS INTERRUPTED BY CANNON FIRE'), auto-redirects an aggressive one toward the guns (attack if in range, else march), and asks a cautious one — and the literal's non-reaction is not silent: `emit_literal_fidelity_events` logs a `literal_fidelity` beat ('Soult holds at Lorraine, per your… (`backend/commands/strategic.py:2257`)
- **A fallen marshal's refusal points straight at the Marshalate bench with a live, affordable commission — death and recruitment are tied** — When the player addresses a destroyed marshal, the pre-parse lost-marshal guard refuses by tombstone AND appends the first commission the executor's own gate would grant right now, with its price (`first_affordable_commission`), so the loss immediately names its remedy. Flagship t19: 'Lannes, attack Buxhowden → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Munich. His name cannot lead the army aga… (`backend/main.py:945`)
- **Petitions arrive with honest arms — AP re-derived at delivery, the command arm shut with a stated reason** — Verified by running the status-mode probe: the turn-5 confrontation arrived with all four arms enabled (`acknowledge/promise/rebuke/command`), and on turns 8 and 11 the command arm arrived disabled with 'Munich is held in force — sending him there needs an order of its own.' — the executor's own gate (`_command_option` jealousy.py:1779-1810 → `command_arm_availability`), delivered through the subtractive `refresh_pet… (`backend/game_logic/jealousy.py:1870`)
- **The glory ladder is legible: the rule, the window and the crown are stated where the player reads them** — Verified by opening marshal_management.gd:261-293: the Generals header renders 'THE LAURELS OF THE ARMY (glory, last {N} turns — a marshal envies the man above him, and keeps that rival while he stays above)' with the window interpolated from the backend constant (`cached_glory_window`, :62/:197 ← `jealousy.GLORY_WINDOW`), a 10-wide bar, ★ crown and 'Crowned with Glory (+1 shock/defense/administration)'; each card ca… (`godot-client/project-sovereign/scripts/marshal_management.gd:276`)
- **Working well: the order-bound last-stand arc is legible end to end, and overkill casualties are clamped for display** — When the fate ask CAN surface (an order-holding marshal), the arc reads cleanly: the flagship shows 'POPUP strategic_interrupt: Ney, last_stand → fight_to_the_last' (audit-flagship-mock/digest.md line 357), and the next turn's order is refused with 'Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release' (line 364) — the PC15-4 tombstone/prisoner guard works, and the 'Marshal Lannes is… (`backend/commands/combat_executor.py:1460`)
- **Order-bound interrupts die with their order at every seam — the NPC-2 single source holds under probing** — `clear_order_bound_interrupt` (strategic.py:111-145) is the one rule, called from the executor's override-cancel (executor.py:1403-1428), the strategic issuance (strategic_executor.py:1217, :1874), the literal first-step arms (:2066, :2101), the road-home issuer (withdrawal.py:695) and the corridor tick (:764). In every probe an order replaced by another (probe F: the treaty's MOVE_TO; probe A: the refused march) lef… (`backend/commands/strategic.py:111`)
- **A standing march stopped by the sea breaks with the full naval reason and remedy — PF-8's stall feedback works for the crossing gate** — When a per-turn MOVE_TO/PURSUE hop is refused by `crossing_check`, `_execute_move_to`/`_execute_pursue` read the structured `blocked_naval` flag and break the order with the gate's own sentence (strategic.py:1118-1125, :1596-1603) rather than re-stalling silently. Verified by running (probe C2): 'Order cancelled: Lannes's march halts at the water's edge — The crossing from Normandy to London is barred — the Royal Nav… (`backend/commands/strategic.py:1118`)
- **Working well: the launcher and README make keyless mock mode the honest default with a real health poll** — launch.bat:20-39 treats a missing or placeholder key as 'no key' and states 'The full game works this way'; :50-57 reuses an already-running server instead of stacking a second; :63-86 polls GET /test for up to 30 s and on failure tells the tester exactly where the error is (the minimized server window) instead of silently opening a client that cannot connect. README_TESTER.txt:17-31 leads with 'Nothing else. No acco… (`deploy/launch.bat:63`)
- **Working well: the School of War cannot damage a campaign and its chips are provably parseable** — The overlay is observe-only and never sends (tutorial_overlay.gd:12-18, enforced by tests/test_tutorial_position7.py:191-208), every suggest chip is mock-parse-pinned against the tutorial roster (test_tutorial_position7.py:410 test_b1_every_suggest_mock_parses_to_its_action), the lesson never writes the campaign autosave (save_manager.py:266-269; main.py:4043-4046), the step is derived from the turn so a reload resum… (`godot-client/project-sovereign/scripts/tutorial_overlay.gd:365`)
- **The AI-vs-AI design substrate is alive and honest even though council wars never open: emergent revanches promote on the ambient board, third-party peaces fire, and restraints name true causes** — Emergent designs fire organically on the shipped boot: `design_promoted` 'Austria swears revanche … Bavaria the loss of Bohemia' (t1), Bavaria vs Austria (t3), Spain vs Britain (t6) — verified by running. Beat 6 fired in a played arm ('Britain and Spain have made peace without us', audit-propose:161). At turn 20 the one AI-vs-AI coveter at `fight` (Sweden, contain_hegemon vs Austria, weight 90) is refused by the expo… (`backend/game_logic/war_council.py:521`)
- **Honest availability holds end to end on the two diplomacy surfaces this lens exercised: the paradox-blocked send arrives disabled with its reason, and the letter-book can never accept a weighty treaty with one click** — The peace confirm popup disables an `available:false` option and shows the backend's reason as its tooltip (proposal_confirm_popup.gd:211-223) and renders the mount warnings (:367-375); `POST /mailbox/respond` is scoped to `is_routine_small_court` rows and refuses anything weightier with 'Open it in full' (main.py:4628-4680, envoy_digest.py:32-70 positive allowlist). The P1 losing-armistice sweetener is priced to the… (`godot-client/project-sovereign/scripts/proposal_confirm_popup.gd:221`)
- **The naval verb grammar, its honest refusals and the quote-then-confirm all held on the mock parser** — Every naval order in the 20-turn script parsed and answered honestly: `build ships` ×5 (named the yard, the rate and the remaining keels), `blockade Britain` (named who it closes and who is beyond reach with the numbers — the WO-14 fix live), `order the diversion` ×3 (the once-per-war refusal twice, verbatim), `land Soult in Munster …` ×2 (a yard list), and the diversion's quote-then-confirm fired and was answered —… (`backend/ai/llm_client.py:1554`)
- **NV-5's Peninsular shape fires unprompted: Britain lands at Lisbon and Spain fights back** — With no script driving Britain, Paget was commissioned at London, put ashore at Lisbon (Portugal, the host at relation 40) on turn 5 with 5,000 men, took Leon (T6), Asturias (T7), Bordelais (T10), Aragon and Toledo, and Spain's Castanos brought him to battle at Aragon on turns 11/13/14 and retook Leon — the 1808 story the NV-5 landing record promised, in miniature, while Moore's 30k stayed home over the lift. (Note f… (`backend/game_logic/naval.py:2576`)
- **Britain's descent works as NV-5 intended: a real amphibious campaign on every seed** — The naval expedition rung (`find_ai_expedition`, backend/game_logic/naval.py:2576, P1.85 in the admin phase) lands Paget in Iberia early and reliably, Castanos contests the beachhead, and Paget then exploits the emptiness inland; Moore's 30,000 stay home over the lift as designed. The AI's use of the sea is legible and historically shaped. (`backend/game_logic/naval.py:2576`)
- **P3.7 homeland recapture answers a raid the turn after it happens** — When Bavaria's Deroy raids Austria's undefended interior in the opening turn, `_find_homeland_defense` (enemy_ai.py:3052, the undefended-recapture arm at :3188) sends the nearest available Austrian corps straight back: the AI does not leave its own soil in enemy hands while it fights forward. (`backend/ai/enemy_ai.py:3188`)
- **The serialized round trip of a played 1805 world is lossless** — After three real turns through the HTTP surface (attacks, moves, scouts, fortify, three enemy phases with AI diplomacy, a marshal petition, two incoming proposals and a settlement offer queued), `to_dict()` → `from_dict()` → `to_dict()` produced ZERO differences across 126 regions, 22 marshals, the dialogue manager, fleets, agendas, formables and every settlement/instrument store; the save file written by `save_game`… (`backend/models/world_state.py:7322`)
- **The /load re-attach discipline is coherent end to end, and every pending question is now classified (table)** — `/load` re-attaches the capture question (main.py:4086-4089), a STANDING marshal's interrupt with the tombstone guard (:4104-4111) and the redemption via the ONE liveness predicate (:4131-4137); the client raises them through the SAME predicates the command path uses with capture→interrupt→redemption precedence (main.gd:4634-4680); from_dict re-primes the petition slot (world_state.py:7558-7560) and sweeps stale rebe… (`backend/main.py:4065`)
- **Working well: the ledger identity is exact — treasury delta equals the applied ledger Net minus the Materiel bill on every probed turn** — Every signed component (income, upkeep+surcharges, occupation, contributions, requisitions, overseas, state charges with named terms, dotations, rentes, infrastructure, admiralty, blockade, trade, tribute, treaty and settlement gold, admin bonus) reconciles to the chest to the gold; the end-turn banner names the one outside-Net flow. The SC-33 / EC-U2 recipe held through EB-1..EB-5, EC-W1..W5 and the naval lines. (`backend/game_logic/ledger.py:411`)
- **Working well: the war-coupled economy fires both ways and the AI spends through the shared rungs** — Contributions (income suspended by an enemy standing on our soil) and Requisitions (we eat a province the enemy still holds) both fired in the ambient probe without any French order — requisitions +75..+100/turn to France on turns 11-19 (French corps standing on Austrian-recaptured Bavaria), contributions −300 on turns 24-26 and 33-35 (Paris/Normandy occupied) — and the AI's admin rungs recruit, grant_dotation, grant… (`backend/models/world_state.py:5308`)
- **The stash-and-raise discipline closes a whole class of 'popped server-side, dropped client-side' losses** — main.gd:2452-2461 stashes the Proclamation, letter-book digest, diorama and redemption BEFORE any route can early-return, and :2620-2645 raises them in a fixed order (diorama → Proclamation → letter-book → redemption) only at control-return, each dismissal continuing the chain; `_maybe_recover_dropped_redemption` (:2036-2049) additionally polls `/pending_redemption` once per turn as a backstop for routes the stash do… (`godot-client/project-sovereign/scripts/main.gd:2452`)
- **The R7 nation-name chokepoints honour formation overrides first, so a formed nation cannot show its dead name on any surface** — utils.gd:163-170 `display_nation_name` consults `formation_overrides` before the static NATION_DISPLAY_NAMES map and before the camelCase split; :232-245 `humanize_nation_keys_in_text` applies the overrides BEFORE the authored prose substitutions (with the load-bearing ordering comment); api_client.gd adopts `nation_display_overrides`/`nation_flag_overrides` from every response and `set_formation_overrides` (:150-160… (`godot-client/project-sovereign/scripts/utils.gd:163`)
- **Working well: the enemy phase is a scene — antagonist voice, our marshal's answer, Berthier's observation, jealousy/expectation notes, and the escalation ladders vary the standing crises** — `_format_berthier_report` renders `enemy_voice` → `marshal_voice` → `expectation_note` → `jealousy_note` → observation → campaign cost in a fixed dramatic order (`enemy_phase_dialog.gd:436-503`), and the standing-class ladders read as a rising voice rather than a repeat: audit-ambient40 turns 36-37 print '3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.' then 'the e… (`godot-client/project-sovereign/scripts/enemy_phase_dialog.gd:436`)
- **Working well: the success and arc headline classes fire in a played campaign with distinct, specific sentences** — In the 24-turn flagship campaign the CA8-9 reversal arc, the CA9-F12 enemy-capture mirror, the CA8-26 victory/conquest classes and the PC15-1 destruction arm all led on their own days with non-template prose: 'Marshal Archduke John of Austria is taken at Tyrol — he is our prisoner, and their order of battle is one commander shorter.' (line 147), 'Marshal Lannes's corps has been DESTROYED at Munich. He will not return… (`backend/game_logic/dispatch.py:1012`)
- **Working well: the alliance-paradox block arrives disabled at mount with its reason AND two named routes** — *(⚠ Sept 2, 2026, verification pass: this note and **FA-D17**, a filed P2 in slice 3, describe the same surface and disagree. Both are partly right: the block IS disabled with its reason — that half works — but FA-D17 shows the two routes it names are wrong, one being unexecutable and the one the executor actually exempts being omitted. Read them together; do not take this note as evidence the surface needs no work.)* — The BPH-C paradox no longer dead-ends silently: the `proposal_confirm` mount disables `execute_proposal` and sets `unavailable_reason` = 'I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is still at war with Austria) creates a diplomatic contradiction. Settle the war jointly at the settlement table, or resolve Bavaria's war first.' while modify/adjust/reconsider stay live (diplom… (`backend/game_logic/diplomatic_dialogue.py:868`)
- **Working well: the peace vocabulary is coherent — 'offer peace', 'propose peace', 'request terms' each resolve to the right instrument and the redirects explain themselves** — `offer peace to Austria` (audit-flagship-mock T18) and `propose peace with Austria` (audit-propose T1) both parse to the Peace Treaty proposal_confirm; `Talleyrand, request terms from Austria` under a coalition war explains the substitution ('Austria fights under Britain's lead in …, Sire — the coalition's terms are the leader's to name, not each court's own. I shall ask Britain's chancery to speak for their alliance… (`backend/game_logic/diplomatic_templates.py:2138`)
- **Working well: Mode A determinism is real and auditable — a fresh replay reproduced an archived 24-turn arm byte-for-byte through turn 13, and refusals are printed in the engine's own words** — Verified by running: `playtest_driver.py --turns 13 --diplomacy propose` and diffing against docs/audits/playtest_digests/audit-propose/digest.md — zero differing lines through the turn-13 block, exactly as PLAYTESTING.md promises (the sha256 per-turn reseed at tools/playtest_driver.py:90-96 plus the PYTHONHASHSEED re-exec at :1433-1437, both recorded in meta.json's `rng` block). This is what made every finding above… (`tools/playtest_driver.py:90`)

## 6. Routing and the build order for Opus

**Filed:** `BUG_FIXES.md` §Final Whole-Game Audit — FA-1..FA-102 (defects,
absences, harness). `DESIGN_REFINEMENT.md` §FA-D — FA-D1..FA-D26 (tie-ins and
design-shaped absences; each names its two seams and a one-session build shape).
The untruncated record is `docs/audits/final_audit_2026_09_01_findings.json`.

**Standing rule for whoever builds these.** 46 rows are UNVERIFIED (§0). For
any of them: reproduce first with the row's own `Reproduce` line, then build.
Where a refuter left a `NARROWED` note, **the note is the truth and the title is
not** — twice the refuter kept the defect and moved the seam.

Eight slices, ordered so the cheapest player-visible wins land first and the
shippable build is unblocked by slice 4.

| # | slice | rows | size | why here |
|---|---|---|---|---|
| 1 | **"The Two Words"** — the fast parser stops acting on keywords it does not understand | FA-6, FA-7, FA-11, FA-50, FA-22, FA-54 | ~0.5 session | The parsing family a first-time player hits in an hour: FA-7 (P1, an order inverted), plus FA-6/FA-11/FA-22 (P2) and FA-50/FA-54 (P3). All one-seam. **⚠ Amended Sept 2, 2026 (verification pass): the rest of this sentence was wrong.** Not all six are hand-reproduced — FA-22 and FA-54 carry no author check — and **there are ZERO golden-corpus rows for any deferral phrasing** (measured: 0 entries of 345 contain `delay`, `later`, `postpone`, `tomorrow`, `hold off`, `defer` or `next turn`). The regression pins this slice needs do not exist yet and must be written as part of it. *(Amended Sept 2: this row read "two P1s" before FA-6 was downgraded.)* |
| 2 | **"The Question Reaches the Player"** — a pending question is delivered, once, and answerable | FA-5, FA-1, FA-16, FA-36, FA-28, FA-30 | ~1 session | The end-turn deferral (FA-5) is the widest: on a quiet stretch the player is shown nothing at all. FA-1 destroys a marshal while asking about him. |
| 3 | **"The Peace Can Be Signed"** — the settlement route stops refusing itself | FA-3, FA-4, FA-17, FA-D7, FA-D17, FA-21 | ~1 session | France cannot end the 1805 war by accepting the coalition's own offer, winning or losing. This is the arc the whole diplomacy layer exists to close. |
| 4 | **"It Runs on a Stranger's Machine"** — the position-10 blockers this audit found | FA-29, FA-43, FA-62, FA-81, FA-82, FA-9, FA-42, FA-57, FA-63 | ~1 session | Every row here is something a Round-0 tester meets in ten minutes: a Python command they cannot run, missing licence text for CC-BY assets, and a tutorial that loses six provinces when followed. **Do this before the export.** |
| 5 | **"The AI Stops Suiciding"** — three rungs that read as dumb | FA-8, FA-35, FA-27, FA-55, FA-D13, FA-D14 | ~1 session | 48 measured attacks where the attacker lost ≥1,000 men to a garrison it never checked for a field army; a whole action budget spent on a 100-man remnant; a corps flipping a homeland province per AP. |
| 6 | **"The Briefing Tells the Truth"** — the narration layer stops contradicting the engine | FA-2, FA-25, FA-12, FA-23, FA-32, FA-53, FA-38, FA-D12 | ~1 session | A live rebelling vassal announced as dissolved (FA-2) is the worst single sentence in the game. |
| 7 | **"The Neglect Arc Ends"** — the marshal systems close their own loops | FA-26, FA-D5, FA-67, FA-47, FA-56, FA-71, FA-D23 | ~1 session | The single highest-leverage change in the audit is FA-26 (§7 below), and the rest of the row is its neighbourhood. |
| 8 (**see the ordering note below — this arguably belongs FIRST**) | **The instrument** — fix the harness before the next audit trusts it | FA-10, FA-74, FA-76, FA-41, FA-39, FA-86, FA-87, FA-92, FA-102 | ~0.5 session | Every one of these silently degraded THIS audit's evidence. FA-92 is the worst: `tools/mutation_sweep.py` reports a mutation that crashes the module as KILLED. |

**Coverage, stated so nobody mistakes this for a complete plan (re-measured
Sept 2, 2026 by the verification pass — the three figures first published here
were wrong and are corrected in place):** the eight slices name **57 of the 128
filed rows**. All 9 P1s are covered; **17 of the 50 P1/P2 rows are not in any
slice**, and **19 of the 26 FA-D tie-ins sit outside them**. The uncovered rows are not lower value by
construction — they are what did not group cleanly. Take an FA-D join
opportunistically when a slice is already open in the file it names, and decide
explicitly whether the 17 unslotted P1/P2 rows need a ninth slice.

> **⚠ ORDERING NOTE, added September 2, 2026 by the verification pass.** Four
> problems with the order as published, each found by an independent reader:
>
> 1. **Slice 8 is last, and it is the instrument every other slice depends on.**
>    The standing rule six lines above tells the builder to reproduce each
>    UNVERIFIED row before building it — and slice 8 is precisely the set of
>    harness defects that corrupt reproduction (FA-10, the only P1 harness row,
>    turns a transient refusal into a permanent one). Do slice 8 FIRST, or accept
>    that every reproduction before it runs on a known-faulty instrument.
> 2. **Slice 8 says "FA-92 is the worst".** FA-92 is P3. On the evidential ladder
>    this memo uses for harness rows, FA-10 (P1) is the worst, and it is in the
>    same slice. The slice also omits both P2 harness rows, FA-37 and FA-40.
> 3. **Slice 4 is labelled "packaging — do this before the export" but carries
>    FA-9**, whose own fix shape is a scenario/design change, not packaging.
> 4. **Slice 5 is sized at ~1 session with no gate step**, but FA-D13's own fix
>    shape opens "A design ruling…" — it cannot be built until that ruling is
>    taken. Size it with the gate, or move the gated rows out.
>
> Also unslotted and worth deciding on: **FA-24 and FA-48 are one defect filed
> twice** (both `_fuzzy_match_enemy`, `executor.py:719` and `:727`).

## 7. The single highest-leverage recommendation

**Make the neglect arc end — FA-26, one call, at four seams.**

> **⚠ AMENDED September 2, 2026 (verification pass, FA-N1).** This section
> originally read "one call at one seam" and claimed `world_state.py:6207` was
> *the only* trust-writing seam that does not consult
> `check_redemption_threshold`. **The word "only" is wrong.** An AST census
> over the whole backend, covering BOTH trust-write APIs (`modify_trust()` and
> `trust.modify()` — a `modify_trust`-only grep misses the cavalry seams the
> paragraph itself cites), finds 49 trust writes, 16 negative, and **four
> unchecked families, not one**: the erosion tick; `_execute_attack`
> (combat_executor.py:7316) while its sibling `_execute_bombardment` checks at
> :3839; `_handle_strategic_objection_response` (strategic_executor.py:1691) on
> the typed route while the endpoint route checks at :2502/:2657; and
> `jealousy.py`'s eight confrontation/rivalry docks (:2717, :2832-2875), in a
> module containing **zero** calls to the checker. There is no global per-turn
> sweep. The five families named below ARE covered — the list is right, the
> quantifier is not. **FA-26's own row is clean and claims no uniqueness; this
> was the memo's editorial framing.** The recommendation gets *better*: more
> marshals rot silently than stated, and the fix should be a shared helper
> applied at all four families.

`world_state.py:6207` is the ES-7 erosion tick: it is one of four trust-writing
seams in the backend that do not consult `check_redemption_threshold`. The
families that DO consult it are objection, defiance, the cavalry limits,
bombardment friendly fire, and the strategic-objection endpoint route. So a marshal whose reward expectation goes unmet
bleeds trust every turn to zero and is never asked, never petitions, never
leaves — the arc simply stops. Measured on the ambient board: Lannes, eleven
battles won, expectation 300 unmet since turn 4, trust 0 at turn 41, and
`check_redemption_threshold(Lannes)` returns a live event the moment it is
called by hand.

The fix is the cavalry-limit idiom, already written three lines away: after
`marshal.modify_trust(-points)`, call the checker and append
`{"type": "redemption_event", "redemption_event": ...}` to the tick's tactical
events. WO-41 (landed the same evening, `96c4c896`) already made the delivery
side reliable — the question now survives the autosave, both turn-advance paths
hoist it, and `/load` re-attaches it. So this one call converts forty turns of a
marshal quietly rotting into the audience the ES-7 economy was designed to
produce, on machinery that is already built and already tested.

Two rows in its neighbourhood make it land properly rather than merely fire:
**FA-D5** (the redemption audience has no arm that settles the unpaid
expectation that caused it — the player is offered autonomy, an administrative
role or dismissal, none of which is "pay him") and **FA-67** (the trust warning
tells the player to "give him a battle he can win", and for a dotation-eroding
marshal a victory RAISES the expectation that is eroding him —
`battles_won` increments at `combat.py:706/718/733/746` and
`dotation.expectation_for_wins` is `min(REP_STEP * battles_won,
EXPECTATION_CAP)`).

> **⚠ AMENDED September 2, 2026 (verification pass).** This paragraph
> originally continued *"and no combat seam anywhere raises trust — measured:
> the backend's only positive trust writes are a vindicated defiance, a literal
> completing an order, and the autonomy-return outcomes"*. **That clause is
> wrong, and it contradicts its own list.** A *vindicated defiance* IS resolved
> by a battle: answering `trust` to an objection arms a pending vindication
> (`disobedience.py:1421`), `combat_executor.py:2632-2644` calls
> `resolve_battle` after every non-bombardment battle, and
> `vindication.py:117-121` sets `trust_change = +3` on `trust`+`victory`,
> applied at `:194`. So a won battle DOES raise trust — conditionally, when a
> vindication is pending. FA-67 is therefore **NARROWED, not confirmed**: its
> first clause falls, its second (the expectation half, kept above) stands. The
> advice is conditionally correct, not a phantom lever.

## 8. Method notes

- **Evidence before agents.** The nine arms were driven, archived and read
  before the fleet was briefed, so every lens argued from the same committed
  digests rather than from its own probe. Two findings were killed by refuters
  who ran their own probes against a claim the digests seemed to support (§4).
- **A budget cut is a finding about the audit, not a reason to round up.**
  Three usage limits cost the refuter pass, the pillar scorers and the critic.
  The memo says so at the top, marks every unverified row, and declines to print
  a pillar table it did not measure. An audit that hides its own gaps is worth
  less than one that names them.
- **The author's hand-verification ran in parallel with the fleet, not after
  it** — 37 notes, and it caught the fleet's two parsing claims (both filed P1 at the time)
  independently
  as well as producing rows the fleet missed (the prisoner family, the
  letter-book's two-vocabulary cooldown, the Low-Countries coastline).
- **One of my own claims was wrong and is corrected in §0.1, not deleted.** The
  live-parser arm's 37/37 identity is fast-parser determinism, not live-parser
  agreement: the run made exactly one Anthropic call.
- **Findings whose fix is "make the second site call the first" keep appearing.**
  FA-26, FA-D19, FA-67, FA-8 and FA-56 are all one rule with two implementations
  and only one maintained. That is the same through-line the Aug-30 whole-systems
  review named, one layer down.
- **What a future audit should do differently:** run the refuters at a smaller
  fleet size but always to completion, and run the scorers FIRST (they are ten
  agents and produce the number the reader wants), rather than last where a
  budget cut removes them.

