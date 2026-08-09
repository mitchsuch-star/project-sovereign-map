# Live play notes — creative audit, Aug 8 2026

## T1
- **[CA9-?] Muster preview over-promises.** Preview: "82,072 with the muster committed",
  "WILL JOIN — Murat: will march to the sound of the guns". Result: "Murat could not reach the
  battlefield in time." Actual massed = 70,687. The preview's headline number is the one the
  player decides on, and it was wrong by 11,385 (16%). Preview has no "if the roads allow"
  hedge on Murat — it *does* hedge Davout ("is willing to march if the roads allow") and Davout
  DID arrive. So the hedged one came and the unhedged one didn't.
- **[CA9-?] Two casualty figures on one screen, again.** Terminal: "Casualties: Ney's army 2,592".
  Berthier's after-action `casualty_summary.attacker_casualties`: **914**. Both true (2,592 =
  whole army incl. allies; 914 = Ney's own corps) but neither says which it is. CA8-1 fixed the
  terminal-vs-log pair; the Berthier report was not brought along.
- **[CA9-?] "Odds unfavorable" with no numbers.** contact_bad_odds interrupt names no strength on
  either side. Post-battle the game freely prints Mack = 52,000. Pre-battle, the number the
  decision needs is withheld; the muster preview says only "Mack (large force)".
- GOOD: muster preview naming WHO will/won't march and the exact command to fix it ("order
  'Soult, support Ney'") is excellent — best affordance seen so far.
- GOOD: marshal_voice + enemy_voice both fired and are in character.
- GOOD: expectation_note ties victory → reward expectation immediately.

- **[CA9-P1] THE MUSTER PREVIEW ONLY MODELS MY SIDE — AND SAYS "FAVORABLE" WHEN I AM OUTNUMBERED 2:1.**
  Order: "Massena, advance into Tyrol". Preview: *"Massena (42,000) vs ArchdukeJohn (substantial
  force) at Tyrol — the balance of force looks favorable."* Result: ArchdukeJohn was reinforced by
  ArchdukeCharles — **massed 83,028 vs 42,000**. Massena lost 8,157 to their 1,973 and was beaten.
  The preview is the game's single best affordance and it computed a verdict ("favorable") from my
  muster only, against a fogged label ("substantial force"). It is not a fog problem — the verdict
  word is the lie, not the missing number. Same family as CA8-1 one level up: the defending army is
  invisible, and here the invisibility is laundered into a recommendation.

## T2
- **[CA9-P1 #2] TYPED "Portugal" SIGNED A PERMANENT TREATY WITH PRUSSIA.**
  Typed verbatim: `accept Portugal's open borders proposal`.
  Response: *"You have accepted **Prussia's** proposal. Treaty signed: PEACE -> OPEN_BORDERS with
  Prussia."* Verified in `/diplomatic_ledger`: `{"nation_a":"Prussia","nation_b":"France",
  "treaty_type":"open_borders","duration":"permanent","turn_signed":2,"involves_player":true}`.
  Portugal's letter remained WAITING. Prussia was never named by me, was not in the digest, and had
  no live proposal on screen. Fuzzy nation-matching Por->Pru executed a binding, permanent,
  irreversible diplomatic act with a great power with **no disclosure and no confirmation** — and
  Prussian neutrality is the single most consequential diplomatic variable in 1805.
  Same family as CA8-28 (silent fuzzy auto-correct) but on a *nation* in a *diplomatic executor*,
  where the blast radius is a treaty rather than a wasted move.
- Letter-book (IGR-F) renders well; Reis Efendi and Araujo are both strongly in character.
- Cosmetic: `proposal_type` is `friendly_gift` while `proposal_type_display` is "Open Borders
  Agreement" — internal/display divergence, display is correct.
- **[CA9-P1 #3] The mis-routed accept ALSO destroyed both pending letters.** After the Prussia
  mis-accept, `GET /mailbox` returns `{"items":[],"count":0,"envoy_digest":null}` and
  `POST /mailbox/respond` answers *"That letter is no longer among the pending envoys, Sire."* for
  both ids. Ottoman's and Portugal's letters were never answered and can no longer be answered.
  One fuzzy nation match cost a treaty with the wrong great power AND two silently-voided courts.
- **[CA9-?] THREE casualty numbers for one battle.** The Great Battle of Swabia, French losses:
  terminal `2,592` · Berthier's after-action `casualty_summary` `914` · campaign log
  `attacker_casualties: 2,730`. Austrian losses: terminal `11,131` · log `11,402`.
  CA8-1 closed the 15x terminal-vs-log gap; the surfaces still do not agree (delta 138 / 271), and
  Berthier is a third number again.
- **[CA9-?] The campaign log is missing three of the four battles fought on turn 1.** Turn 1's
  `events` array holds exactly two entries: the Swabia battle and one relationship_change. Absent:
  the Tyrol battle I fought and lost (Massena, -8,157), the Second Battle of Swabia (Mack routed
  attacking Lannes, -14,512) and the Milan battle (Charles broke Massena). TO VERIFY across more
  turns — may be a deferred-write rather than a drop.

## ⚠ CORRECTION — contamination event, and what it invalidates
The user's own Godot client (PID 28048, "Ink & Iron (DEBUG)") was live on 127.0.0.1:8005 and its
main menu fired `POST /new_game` **mid-session**, resetting my world to turn 1. Backend log line
792. Everything I observed after that point was read from a FRESH world, not my campaign.

Findings that stand (all occurred BEFORE the reset — treaty ratification is logged at line ~786,
`/new_game` at line 792):
  - muster preview over-promise (Murat)
  - muster preview verdict "favorable" while outnumbered 2:1 at Tyrol
  - three casualty numbers for the Great Battle of Swabia
  - **Portugal -> Prussia permanent treaty** (log: `DIPLO STATE: Prussia-France: PEACE ->
    OPEN_BORDERS (treaty_ratification)`, immediately after the LLM parsed my Portugal sentence)

Findings WITHDRAWN as artifacts of the reset, not of the game:
  - ~~"the mis-routed accept destroyed both pending letters"~~ — the mailbox was empty because the
    world was new. NOT caused by the accept.
  - ~~"Davout/Ney frozen by a stale engagement with an absent Mack"~~ — in the fresh world Mack
    genuinely was at Swabia. Correct behaviour.
  - ~~"campaign log missing three of turn 1's four battles"~~ — I was reading the fresh world's log.

Carried forward TO RE-VERIFY on the clean run:
  - the `pursue`-into-contact battle that produced `events: []`, no `battle_report`, no
    `battle_diorama`, no reinforcement lines (real observation, fresh world, must reproduce)
  - campaign-log completeness vs battles actually fought

The audit now runs on an isolated backend, **port 8015**, so nothing external can reset it.

## CLEAN RUN (port 8015)

### T1
- **[CA9-P2] A strategic order reports `cost=1` and charges 2 AP.** Traced from `action_info`:
  `Soult, support Ney` cost=1, remaining 4->3 (correct: literal discount, and the message SAYS
  "1 AP — Soult executes precise orders with fewer couriers").
  `Bernadotte, support Ney` **cost=1, remaining 3->1** — charged 2, reported 1.
  `Ney, attack` cost=1, remaining 1->0 (correct).
  Consequence in play: I budgeted a fourth action, issued it, and got *"Not enough actions! Need 1,
  have 0."* The action economy is the game's core per-turn resource and its advertised price is
  wrong for the ordinary case; it is right only for the special-case marshal.
- **[CA9-?] Casualty double-count REPRODUCES cleanly.** Great Battle of Swabia: terminal *"Ney's
  army 1,940"*, Berthier `casualty_summary.attacker_casualties` **316**, `attacker_original` 24,000.
  316 = Ney's own corps; 316 + 1,624 allied = 1,940 = the whole army. Both figures are correct and
  neither is labelled, on the same screen, one directly under the other.
- Muster preview was ACCURATE here (all six marshals had orders/were adjacent; 107,722 predicted
  and 107,722 committed). So the T1-dirty over-promise is specifically about a marshal who cannot
  reach in time — distance is not modelled in the WILL JOIN verdict.
- GOOD: Soult's literal voice + the AP discount + "No more and no less" is the best character
  writing in the game so far.
- GOOD: "Swabia remains Bavaria's soil — we drove the enemy from our ally's province; it is not
  ours to take."

### T2 — the muster/supply trap
- **[CA9-P1 #4] THE GAME'S BEST AFFORDANCE FEEDS ITS WORST PUNISHMENT, SILENTLY.**
  The muster preview and the `support` order exist to make me concentrate. I did exactly that:
  six marshals, 107,722 men, one province. Result on the very next tick:
  Ney -1,396 · Davout -1,539 · Soult -2,368 · Lannes -1,065 · Murat -1,302 · Bernadotte -1,006
  = **8,676 men starved at Swabia in one turn, against 1,940 lost taking it. 4.5x more men died of
  hunger than of the enemy**, in the province the game's own affordance told me to fill.
  Nothing in the muster preview mentions supply. Nothing warned before the order. And:
- **[CA9-P1 #5] The supply capacity of a province you do not own is UNLOOKUPABLE.**
  `/ledger.territories` carries `supply_capacity` for my 28 provinces only. `/map_topology`'s
  region record has `adjacent / terrain / region_type / is_capital / starting_controller /
  grid_position` and **no supply field at all** — so the region panel cannot show it either.
  Swabia is Bavarian soil. An army campaigns abroad by definition, so the number that governs the
  single largest source of French casualties is unavailable exactly where it applies.
  (CA8-2 named "the capacity nobody could look up"; it is still true off own soil.)
- **[CA9-P2] The `supply_strain` headline did not fire on the turn supply did its worst.**
  Headline was `victory_won` w=73 ("Marshal Ney holds the field at Swabia"), `sub_beats: []`. The
  8,676 losses appear as **six separate identically-shaped "warning" lines** in flat `turn_events`,
  interleaved with jealousy gossip — no aggregate, no total, no capacity, no remedy.
  A victory costing 1,940 outranked a famine costing 8,676 *and suppressed it entirely*.
- **[CA9-P2] Jealousy fires and escalates on the same tick, twice.** T1->T2 produced
  `jealousy_fired` Murat->Ney AND `jealousy_escalation` Murat->Ney, plus `jealousy_fired`
  Bernadotte->Ney AND `jealousy_escalation` Bernadotte->Ney. A grievance that is "a matter of
  concern among the general staff" the same turn it is first noticed has no escalation curve;
  the tier-2 language is spent before tier 1 has landed. (CA8-8 family, still live.)
- **[CA9-P3] `treasury_delta` is wrong.** Dispatch reports `treasury_delta: 2249`. Net line said
  `+1881`; treasury moved 800 -> 2,584 = **+1,784** (= 1881 - 97 materiel, which reconciles).
  2,249 matches neither.
- GOOD: headline led with a VICTORY (CA8-26/D6 landed and is visible).
- GOOD: `jealousy_autonomous_warning` — "Murat is eyeing Mack's position at Nassau. I cannot
  guarantee he will wait for orders" — excellent fore-warning.
- **[CA9-P1 #6] THE WAR-PURPOSE PROMPT IS AN INVISIBLE HARD STOP.** Murat's pursuit halted at
  Hesse's border. The battle response's `message` said *"...choose our purpose, or let the province
  stand"* — and carried **no dialogue key at all** (non-empty keys were action_info, action_summary,
  active_wars, battle_diorama, battle_report, coordination_tutorial, diplomatic_points,
  envoy_digest, events, game_state, marshal_petition, ..., message). The client renders modals from
  `response.diplomatic_dialogue` (`main.gd:1603/1617/1620`) and `war_purpose_selection` IS in the
  dtype whitelist (`main.gd:32`) — so the popup exists, is renderable, and was never sent.
  Meanwhile a HARD-STOP dialogue was live server-side: my next two orders — `Ney, march on Bohemia`
  and `Davout, move to Franconia` — were both swallowed and answered with
  *"I don't understand that choice, Sire. Options: 1=Conquest, 2=Forced Alliance, 3=Subjugation,
  4=Back Out"* — an options list the player was never shown, for a question they were never asked
  in a form they could answer. No AP was charged (AP held at 3), so the cost is lost orders and
  total confusion rather than lost resources. Typing `4` cleared it.
  This is the recurring "new dialogue type not wired to a popup" family, on a Stage-D verb.
- GOOD: "WILL NOT — Bernadotte: will not lift a finger for this marshal" — the MC-3 relationship
  web showing through the muster preview with real mechanical bite.
- GOOD: Murat's 'First Horseman of Europe' annihilation (+5,000 pursuit) and the Hesse
  war-purpose *concept* ("To seize it is to make war on Hesse") are both excellent.
- NOTE: terminal prints Mack's casualties as 23,011 pre-pursuit, then "+5,000" separately; the
  event/log carry 28,011. Disclosed, but the summary line is again not the total.
- CORRECTION to my T1 note: terminal AND event both carry the WHOLE-army figure consistently
  (Swabia 1,940 = 316 lead + 1,624 allies; Nassau 878 = 215 + 663). The mismatch is specifically
  that **Berthier's `casualty_summary` is lead-only and unlabelled**, printed under the terminal
  line that just gave the army total. One defect, not two.

### T3
- **[CA9-P1 #7] THE FOG FALLBACK IS ALL-OR-NOTHING, AND THAT IS WHY EUROPE READS AS EMPTY.**
  `main.py:944-952`: `fog_hidden_summary` is emitted **only if `cleaned_phase.total_actions == 0`**
  — i.e. only when every enemy action in the entire world was hidden. Measured this turn: Austria
  `action_count: 3`, one survived the filter, `total_actions: 1`. The two hidden Austrian actions
  and **every completely silent nation (Russia, Britain, Prussia, Spain, Ottoman ...) are absent
  from `nations` entirely**, with no acknowledgement of any kind. One visible action anywhere in
  Europe suppresses the fog line everywhere.
  This is verbatim the Aug-4 audit's highest-converged remediation ("make the fog fallback
  per-nation, not per-phase" — CA8-15, chosen independently by BOTH the narration and aliveness
  scorers). It is **still not built.** Silence continues to read as "nothing happened" on the exact
  turn three provinces are changing hands elsewhere.
- **[CA9-P3] `action_count` is read by the client and never rendered** (`enemy_phase_dialog.gd:78`
  assigns it, nothing consumes it) — so the 3-vs-1 discrepancy is invisible rather than confusing.
  Dead read; the honest fix is to render it as the fog line above.
- **[CA9-P2] The crown passes to nobody.** `glory_crown_lost`: *"Ney is no longer the army's most
  celebrated commander — the laurels have passed."* No paired `glory_crowned` event names the new
  holder. The sentence raises the question it refuses to answer, on the turn the answer is the
  whole point.
- **[CA9-P2] Jealousy fires + escalates on the same tick — third occurrence in three turns**
  (Murat->Ney T2, Bernadotte->Ney T2, Lannes->Murat T3). Meanwhile Davout has been "restless" three
  turns running with the identical sentence, only the envied name changing.
- GOOD: `jealousy_resolved` — "Murat's grievance is satisfied — a victory against a worthy foe"
  (+10% attack). The loop CLOSES, and closing it by giving him the Nassau attack felt like real
  man-management.
- GOOD (drama): Milan fell with `defender order of battle: Massena 32,962(routed); Soult
  34,876(refused)`. Soult sat one province away and refused because he held no written order. That
  is the literal doctrine producing a genuine disaster, and the order of battle SHOWS it.
- **[CA9-P3] March attrition is large, unexplained and wildly uneven.** Soult Swabia->Munich
  (adjacent): **-2,226**. Davout Nassau->Franconia: -422. Lannes Nassau->Rhineland: **0**. The
  message is only "(2,226 lost to march)" — no cause, no rate, no way to anticipate.
- **[CA9-P1 #8] THREE "SHOULD I ATTACK?" ADVISORS, THREE DIFFERENT MODELS OF ENEMY STRENGTH,
  OPENLY CONTRADICTING EACH OTHER.** On the same target (Tyrol) within two turns:
    1. `[HINT] Tyrol is undefended — attack to capture it!` (appended to two separate move results)
    2. the MUSTER preview, which sums only MY side and then renders a verdict ("the balance of
       force looks favorable") against a fogged label
    3. Davout's objection: *"Sire, the enemy is too strong. We need reinforcements."*
  Ground truth from `/ledger.intel`: **no enemy field army is in Tyrol** — Charles (46,573) and
  John (17,784) are both at Milan, which is *adjacent*. So the hint is literally true and
  strategically false; Davout is substantively right; and the muster preview would have called it
  favorable, exactly as it did at Tyrol on the dirty run right before Massena was destroyed there.
  The three advisors never reconcile and the player is given no way to tell which one models
  adjacent reinforcement. This is the single most consequential legibility failure I have hit:
  it is the same root as CA9-P1 (defender invisibility) surfacing as *contradictory advice*.
- **[CA9-P2] A pending objection blocks free, read-only commands.** With Davout's objection live,
  `status` (cost 0, pure read) returns *"Davout awaits your answer, Sire — settle the objection
  before issuing new orders."* The objection asks the player to make a judgement and simultaneously
  denies them the board. (`GET /ledger` still works, so a client player can press the ledger key —
  the terminal player cannot.)
- GOOD: the jealousy confrontation petition now STATES ITS TERMS on every arm ("Free, and it fixes
  nothing: the grievance stands 3 more turns... then cools on its own" / "1 AP"). Big improvement.
- GOOD: Hardenberg's hegemony-pressure line, and the digest re-titling itself "THE SMALL COURTS
  WRITE" when the senders are minor.
- **[CA9-P2] The objection never states its options, and rejects plain English that plainly means
  one of them.** `/pending_objection` -> `choices: ["trust","insist"]`. The player-facing text is
  only *"Davout respectfully raises concerns: 'Sire, the enemy is too strong...'"* and then
  *"Davout awaits your answer, Sire — settle the objection before issuing new orders."* Neither
  names `trust` or `insist`. I typed **"Davout is right, cancel that attack"** — an unambiguous
  *trust* — and it was not understood; the same block message repeated. (The client popup has
  buttons; the typed player, which is this game's whole premise, has to guess two magic words.)
  Compare the war-purpose prompt, which at least prints its option list — on rejection.

### T4 — the invisible hard stop, second occurrence, worse
- **[CA9-P1 #6, ESCALATED] The unrendered war-purpose stop recurs from an action the player did
  not order, and it swallows `end turn`.** Chain, from `audit_backend.log:1246-1278`:
  `jealousy_autonomous_attack` — *"Lannes, hungry for glory, has attacked Mack on his own
  initiative"* — Mack retreats to Berlin, Lannes halts at Hesse's frontier (`PT-F1 frontier halt`),
  and a hard-stop war-purpose dialogue is armed. The turn-4 end-turn response carries **no
  `diplomatic_dialogue` key and no key containing "dialog" at all**, so the popup cannot render.
  My next command — `end turn` — was answered with *"I don't understand that choice, Sire. Options:
  1=Conquest, 2=Forced Alliance, 3=Subjugation, 4=Back Out"*.
  So: a marshal acts on his own initiative, walks the army to a neutral's border, and the game
  silently stops accepting orders — including ending the turn — over a question it never asked.
  **CORRECTION to my own first reading:** the turn report was NOT swallowed by the game. My harness
  crashed while rendering it; the payload was complete. The defect is the invisible stop, not a
  lost dispatch. Verified by re-rendering the stored payload.
- GOOD, and the best writing of the run: `jealousy_escalation` — *"Bernadotte resents Ney's laurels
  **again, 2 turns after the last**"* then *"...has become **entrenched**. The wound will not close
  on its own."* The CA8-8 recurrence register is working and it reads like a novel.
- GOOD: Soult "has thrown himself into his post with obsessive diligence" -> four
  `intel_updated ... source: "obsessive_patrols"` reveals. Character expressed as a mechanic.
- **[CA9-P2] Supply: I dispersed on purpose and the muster re-stacked them.** Munich now holds
  Soult+Murat+Bernadotte+Massena, -5,559 this tick. Running non-combat total by T4:
  **T1 8,676 · T2 2,648 march · T3 1,950 · T4 5,559.** The convergence the game rewards is the
  convergence that starves it, and there is still no warning at order time.
- **[CA9-P1 #9] THE GAME'S OWN ACCEPTANCE BREAKDOWN PROVES THE LEVERAGE BUG.** Britain offered a
  white peace on T4. I chose "Request Revision" and got the per-court review — the best surface in
  the game. Austria's verdict: **total 8 against a threshold of 50**, `band: reject`, top blocker
  "Settlement legitimacy" (-10), then "National design" (-8). And the component that is supposed to
  represent *how badly Austria is losing* — `base_side_pressure` — is **+1**.
  State of the war at that moment: Mack's army destroyed from 52,000 to ~6,000 across three
  defeats, four of five battles won, one decisive, and my ally Bavaria holding **Hungary and
  Moravia**. `active_wars` reports `war_score: 6`, `territory: 0`, `decisive: 0` (while the very
  same object reports `decisive_won: 1`), `settlement_tier: "white_peace"`.
  Winning the war is worth +1 out of 50 at the table. This is CA8-3/CA8-D2's family, and the D2
  build (Aug 7) did collapse the HUD to one war-level row — but the *number that row carries* still
  does not reflect the war being fought.
- **[CA9-P3] `decisive: 0` and `decisive_won: 1` in the same `active_wars` object.**
- **[CA9-P3] Raw internal nation key in the mailbox row.** `summary: "PapalStates — Open Borders"`
  (the envoy digest correctly says "Papal States"). R7 chokepoint missed on `mailbox.summary`.
  (CORRECTION: I first suspected `from_nation` was null on every row — wrong, the key is
  `source_nation` and it is populated. My probe used the wrong key.)
- **[CA9-P3, verify] The counter-draft may be delivered exactly once.** After "Request Revision"
  the `settlement_confirm` PROPOSE payload arrived on that one response; no subsequent `/command`
  carries `diplomatic_dialogue`, and it is not in `/mailbox` (which lists 4 other waiting items).
  In the client the popup is on screen, so this only bites a player who dismisses it — flagged for
  code verification rather than asserted.
- GOOD, genuinely: the per-court component breakdown (11 named components, each with a display
  label and a signed value, plus `top_blocker_display`) is excellent design. The problem is not the
  surface, it is one of the numbers feeding it.

### T5-T6
- **[CA9-P1 #10] THE SUPPLY HEADLINE STILL PRESCRIBES A BUILDING THE GAME THEN REFUSES — the
  Aug-4 CA8-2 defect, still shipping, in a fresh instance.**
  Dispatch T6: *"Sire — Ney, Murat and Massena stand 56,647 men at Tyrol, which feeds 30,000.
  26,647 too many. 2,922 men lost in 2 turns. **A supply depot at Tyrol would ease it**; dispersing
  a corps would end it."*
  `build a supply depot at Tyrol` -> *"Cannot build in Tyrol — region stability too low (35/100).
  Need 51+."*
  Systemically worse than a copy bug: securing a conquest sets stability to 25, so a **just-taken
  province can never accept a depot** — and a just-taken province is exactly where a campaigning
  army stands. The recommended remedy is structurally unavailable in the situation that generates
  the problem. (The refusal itself is honest and names the threshold — that half is good.)
- **[CA9-P1 #11] THE GAME PROMISES "SOULT WILL MARCH TO NEY'S GUNS" AND THEN HE REFUSES.**
  Order confirmation: *"Soult moves to support Ney (at Franconia). ... **Soult will march to Ney's
  guns** — he holds your written order."*  Two turns later Ney fights at Tyrol and the order of
  battle reads `Soult 28,202(refused)`, with `literal_fidelity`: *"Soult holds at Franconia, per
  your orders — the guns at Tyrol did not move him."*
  The support order is bound to the location Ney occupied at issue time, not to Ney — but the
  confirmation text promises the opposite in so many words, and the muster preview's whole pitch is
  *"order 'Soult, support Ney' and he will march"*. 28,202 men sat out the battle I bought them for.
- GOOD: `literal_fidelity` as a named event, and the order of battle printing `(refused)`, mean the
  betrayal is at least legible after the fact. The problem is the promise, not the silence.
- GOOD: the T6 supply headline is a model of its kind — names the marshals, the mass, the capacity,
  the overage, the cumulative cost, and both remedies.
- NOTE: `glory_crown_lost` (T3, no successor named) is followed by `glory_crowned` for Murat at T5.
  The crown is announced eventually; the gap is only at the moment of loss.

### T7-T8
- **[CA9-P1 #11 CONFIRMED x3] Soult refused a third time**, again after the exact command the
  muster preview prescribes. `literal_fidelity: "Soult holds at Tyrol, per your orders — the guns
  at Franconia did not move him."` Three separate turns, three different battles, same broken
  promise ("Soult will march to Ney's guns"). The support order binds to the supported marshal's
  location at issue time; the confirmation text and the muster preview both say it binds to the man.
- **[CA9-P2] `pursue` only accepts the RAW INTERNAL KEY.**
    `Murat, pursue Archduke Charles and destroy him` -> "Cannot find 'Archduke Charles' to pursue."
    `Murat, pursue Charles`                          -> "Cannot find 'Charles' to pursue."
    `Murat, pursue ArchdukeCharles`                  -> works.
  Every intel surface in the game prints **"Archduke Charles"**. The player must type the
  camelCase internal key the project's own R7 rule exists to hide. Note `attack` resolved "Charles"
  fine earlier — so the two verbs use different resolvers and only one is display-name aware.
- **[CA9-P3] The pursuit silently became a different battle.** `pursue ArchdukeCharles` answered
  *"Murat: 'Mack bars the way!' Engaging!"* and fought **Mack**. Blocking is a fine mechanic, but on
  turn 1 an equivalent situation raised a `contact_bad_odds` interrupt and ASKED; here it committed
  the army without asking. Two paths, two behaviours.
- **[CA9-P3] Silent retarget:** `Ney, attack Charles at Bohemia` was executed at **Franconia**
  (where Charles actually stood). Disclosed in the muster line, so mild — but it is a third
  instance of the engine quietly rewriting a named target.
- ECONOMY, GOOD: conceding the Fontainebleau petition granted 6 rentes totalling 1,340g/turn and
  Net fell **+2,316 -> +98** in one turn, with a signed "Rentes: -2010g" line in the income
  breakdown. The reward economy has real teeth and the ledger names them honestly.
- ALIVENESS, GOOD: enemy phase reached **13 actions** across Austria, Bavaria and Spain by T8
  (Castanos winning twice at Aragon, and being granted a rente by his own crown).

### T9-T10
- **[CA9-P1 #12] FRANCE'S MORNING DISPATCH LEADS WITH A FOREIGN POWER'S PRISONER.**
  T10 headline, `class: marshal_captured`, **weight 95** — the highest weight observed all campaign:
  *"Sire — Marshal Paget has been taken. Spain holds him prisoner."* Paget is British; Spain took
  him; **France is not a party.** It outranked, as sub-beats:
    - *"Marshal Massena holds the field at Tyrol — Archduke John's corps is broken and flees"* (a
      French victory), and
    - *"...83,212 men at Tyrol, which feeds 30,000 ... 10,718 men lost in 3 turns."*
  The Aug-7 D6 build established "a third party's kill is never our triumph" for `enemy_eliminated`;
  `marshal_captured` carries a higher weight than any French event and was given no such guard.
- **[CA9-P1 #4, cumulative] Non-combat losses now dominate the campaign.** Running total of men
  lost to hunger and marching, T1-T10: **~40,000**, against roughly 12,000 lost in all battles
  combined. The army sits at 83,212 in a province that feeds 30,000 because every muster
  re-concentrates it and no order-time surface mentions supply.

### T13 — the offensive dissolves
- **[CA9-P1 #13] AUTO-REINFORCEMENT DRAGGED THREE CORPS INTO A NEUTRAL COUNTRY AND SILENTLY
  CANCELLED A STANDING STRATEGIC ORDER.** Britain's Shrapnel, beaten, retreated to **Albania**
  (`controller=Ottoman`, `dist_to_capital=9`). My marshals followed the battle. Result at T13:
  **Davout, Murat and Massena all standing in Ottoman Albania** — the far south-east Balkans —
  while my war is in Austria. Murat had a live `MOVE_TO Vienna` order (`[STRATEGIC] Creating
  MOVE_TO order for Murat -> Vienna`, issued turn 10). After the pull, `/ledger.orders` reports
  `order_type: "No active orders", has_order: false` for him, and **no event of any kind announced
  the cancellation**. My attack order then failed with *"Murat cannot reach Vienna from Albania!
  Range: 2, Distance: 3"* — the first time the game told me where he was.
  The muster is the game's signature system and its pull is unbounded: any battle anywhere
  re-tasks the army, overrides written strategic orders, and reports nothing.
- **The campaign's shape at T13:** France has won almost every engagement and the army is
  disintegrating anyway. Ney 24,000 -> **9,377** (morale 40), Murat 22,000 -> **10,671** (morale
  38), Massena 42,000 -> **13,048** (morale 0). Trust falling everywhere (Bernadotte 22, Massena
  44, Ney 56). ~40,000 lost to hunger and marching vs ~12,000 to the enemy. Kutuzov (24,875) has
  arrived at Bohemia. **Nothing in the game ever connected these facts to each other**, which is
  the same verdict the Aug-4 audit reached by a different road.

### T16 — the best moment in the campaign
- **HIGHLIGHT (this is the game at its best).** Talleyrand's assessment reports:
  *"Austria's design: **Revanche** — Their court will not rest while **Russia** holds Bohemia.
  Their price: prepared to go as far as an ultimatum — Russia stands in the way (weight 72)."*
  Verified in the server log: Bohemia went **Austria -> France** (my conquest, T10) **-> Russia**
  (`[RETREAT DEBUG] Checking Bohemia: controller=Russia`, line 7872). So Russia took from France a
  province Austria regards as its own, and **Austria's national design has flipped to revenge
  against its own coalition partner.** Nothing scripted this. The emergent-designs system produced
  a real, exploitable political fracture inside the Third Coalition, and the advisor reported it
  accurately and actionably. This is the single best thing I saw in 16 turns.
- **Talleyrand's "assess our situation" is the best surface in the game.** Per-court design, the
  weight, how far each will go, the coalition's leader and posture, the turn's threat accounting
  ("Natural threat decay (-3); Hegemony Passive (+1)"), vassal loyalties, and then *executable*
  counsel: *"Britain's war has a purpose we can price — 'The Low Countries'. We hold what their
  court wants; offer it at the table and their reason to fight goes with it."*
- DESIGN NOTE (not a defect): rentes do not scale with expectation. Davout, 19-0 in battles, saw
  his expectation rise 240 -> 300 while his granted rente stayed 240, so he is "eroding" again
  four turns after I paid. Over a long campaign the reward loop is a treadmill the player must
  re-run manually. Intended by ES-7 ("the cost of success"), but worth a designer's eye.
- **[CA9-P1 #14] THE DEFAULT PEACE OFFER PAYS TRIBUTE TO THE COURT I AM BEATING.**
  `propose peace to Austria` at **war score +13 in my favour**, holding Tyrol and Carniola, with
  Mack captured and his army destroyed. Talleyrand's *recommended* option, "Send as suggested",
  carries: `sweeteners: [{"type":"gold_per_turn","value":77}], demands: []`.
  I offer Austria **77 gold a turn and ask for nothing**, while winning. The option directly beneath
  it reads *"Harsher terms: Demand more — **we can afford to push**"* — so the generator knows the
  military situation and still opens by paying. This is CA8-27's family surviving the Aug-7 D2 fix
  (which covered *cessions*, not *sweeteners*).
- **[CA9-P2] "Even harsher" is a dead option.** "Harsher terms" -> `demands: [{gold_per_turn: 300}]`.
  "Even harsher" -> **`demands: [{gold_per_turn: 300}]`, byte-identical.** No escalation.
- **[CA9-P1 #14b] AND NO DRAFT, AT ANY HARSHNESS, CAN DEMAND TERRITORY.** Both harsh drafts ask
  only for gold, while I occupy two Austrian provinces. Combined with finding #9 (battlefield
  dominance is worth `base_side_pressure: +1` out of a 50-point threshold), this is the campaign's
  central failure and the three findings are one story:
  **the war cannot be converted into terms.** You win every battle, the leverage number does not
  move, so the table offers you tribute-paying white peace and the map never changes hands by
  treaty. 16 turns of victory bought exactly nothing at the negotiating table.

### FINAL ACCOUNTING (T19) — and a correction to my own earlier claim
Computed from every battle event and supply event in the transcript, French side only:
  - lost to SUPPLY (hunger): **52,677**
  - lost in BATTLE:          **38,016**
  - ratio 1.39 : 1
**CORRECTION.** Earlier in these notes I wrote "~40,000 to hunger vs ~12,000 to the enemy" and
"4.5x more men died of hunger than of the enemy". That was WRONG — I was totalling only the
terminal lead-corps figures for battles while totalling all supply events, which is precisely the
lead-vs-whole-army confusion finding F2 is about. I made the same mistake the game makes.
The honest claim is: **hunger killed 1.39 times as many French soldiers as the enemy did**
(52,677 vs 38,016), and that is still the single loudest fact in the campaign.
(The "7,260 lost to march" figure I also quoted is unreliable — that regex swept the digest and
caught enemy marches too. Dropped rather than corrected.)

Army at T19: 189,000 -> 86,573. Trust: Bernadotte **10**, Massena 26, Ney 53, Soult 53, Murat 53,
Davout 60, Lannes 75. Morale: Massena 0, Ney 20, Murat 23, Davout 35.
France won nearly every engagement it fought and ended turn 19 with a wrecked, resentful army,
31 provinces of 126, and a war it cannot end.

### ROOT-CAUSE CORRECTION — the "Portugal signed Prussia" defect
I originally attributed this to fuzzy nation-matching (Por -> Pru). **That is wrong.** Read the
seam: `backend/main.py:2046-2110`.

When any diplomatic dialogue is pending, the router matches the raw command against dialogue
options / a keyword list and calls `handle_diplomatic_dialogue_response(matched_keyword, ...)`.
**The nation the player named is never consulted at any point.** So
`accept Portugal's open borders proposal`, with Prussia's proposal active, matches the verb
`accept` and answers **Prussia's** dialogue. Backend log:
`[DIPLOMATIC] Routing dialogue response: accept` -> `DIPLO STATE: Prussia-France: PEACE ->
OPEN_BORDERS (treaty_ratification)`.
The real defect is therefore broader and simpler than I claimed: **an answer verb binds to
whichever dialogue is active, never to the court the player addressed** — in a game whose
letter-book exists precisely because several courts write at once.

**And the hard-stop branch is worse still.** `main.py:2067-2071`: for
`dialogue_manager.HARD_STOP_TYPES` (which includes `war_purpose_selection`, the dialogue finding
F6 shows is INVISIBLE) the matcher is a **bare substring scan, first match wins**, over
`_DIALOGUE_RESPONSE_KEYWORDS` — a list containing **"no", "yes", "send", "more", "garrison",
"invest", "demand", "review", "consider", "side", "start", "begin", "continue"**.
So while an unrendered war-purpose stop is pending, `Ney, march on **No**rmandy` contains "no" and
`Murat, **garrison** Paris` contains "garrison": ordinary orders silently answer an invisible
question about whether to conquer a neutral country. The soft-stop branch was hardened against
exactly this (its comment reads *"to avoid capturing unrelated commands like 'garrison'"*) — the
hard-stop branch was not.
Verified live that the SOFT path is safe: with a `proposal_confirm` open, `Ney, march on Normandy`
passed through to the executor correctly.

### THE 21-TURN HEADLINE SEQUENCE (measured, T2-T22)
- **"Sire — Marshal Davout's household goes unpaid. His patience erodes with his purse."**
  appears as headline or sub-beat on **T11, T12, T14, T15, T16, T17, T18, T19, T21, T22 — TEN
  times, verbatim identical.** PC-7's repeat-demotion cooldown is not holding this class.
- The `levy_open` line appears **7 times** (T12,14,15,16,17,19,22), identical but for its numbers.
- **"X holds the field at Bohemia — Y's corps is broken and flees"** leads on T11, T17, T19, T21,
  T22 — five near-identical leads, same province, over twelve turns in which the map did not move
  (regions frozen at 31/95 from T16 to T22).
- **Real news is buried under smaller news, repeatedly:**
    T13 headline = *"Marshal Shrapnel has been taken. France holds him prisoner"* (w95), with
      *"Bohemia has been taken by Russia"* — a new belligerent seizing a province I held — as a
      sub-beat.
    T20 headline = *"Murat's corps has been broken"* (w90), with *"Carniola has been taken by
      Britain"* as a sub-beat.
    T15/T16 = **"Austria and Bavaria have made peace without us"** — a coalition partner leaving
      the war, the single most consequential diplomatic event of the campaign — appears **only as
      a sub-beat, twice, and is never mentioned again.**
- NOT a defect, checked: Munich's stated capacity rises 25,000 -> 30,000 between T4 and T5 because
  a depot completed ("Munich already has its depot"). Consistent.

**The pattern:** the dispatch is excellent at *sentences* and poor at *editing*. Every individual
line is well written; the selection and ranking between them is what fails.

### T16-T24 — THE CAMPAIGN REACHES A LOOP IT CANNOT LEAVE
Measured across the last nine turns:
  - **regions frozen at 31/95** (T16 through T24, unchanged)
  - treasury flat: 16,130 -> 15,542; Net oscillating -199 .. +1
  - headline `victory_won` at **Bohemia** on T17, T19, T21, T22, T23, T24 — six of eight turns,
    same class, same province, different marshal's name
  - supply bleeding ~1,500/turn the entire time
  - `unmet 5` marshals every single turn since T11
France is winning a battle at Bohemia forever. There is no territorial progress, no path to peace
(finding F14: the table offers to pay Austria while I hold their provinces), no victory condition
that can fire, and no economic pressure (net ~0 at 15.5k in the bank). **The game does not end and
does not change.** After turn ~15 the only thing that varies is which marshal's name is in the
sentence. This is the most important "not fun" observation of the whole audit and it is a
*consequence* of the leverage defect rather than a separate bug.

**NUANCE, checked before claiming.** `turn_manager.py:1097-1099` — `if self.world.sandbox_mode:
return {"game_over": False, ...}` disables every victory/defeat branch, with the comment *"Real
victory conditions -> Pre-Ship Victory & Objectives Pass."* So **"the game cannot end" is a
deliberate, documented, owned gap** (ROADMAP positions 12-13), not a defect, and I must not file
it as one.
What IS a defect is the reason the open-ended middle feels *dead* rather than *open*: with the
leverage number frozen (F9) and the peace generator offering to pay the loser (F14), there is no
non-military way for the state of the world to change either. Remove the victory condition and you
have a sandbox; remove the victory condition AND the ability to convert victory into terms, and
you have a treadmill. The Victory Pass will not fix that on its own.

### REGRESSION CHECKS AGAINST THE AUG-4 AUDIT (things that are now FIXED)
My harness stamps `<<<RAW-FALLBACK>>>` wherever `enemy_phase_dialog.gd::_format_action` would fall
through to `action_type.replace("_"," ")` and print a raw internal verb.
  - **0 hits across the whole 24-turn campaign.** CA8-6 is holding (Aug-4 measured raw snake_case
    on 12% of that campaign's AI actions — "Deroy grant dotation Bohemia", "Castanos form square").
  - CA8-26/D6: the dispatch **does** now lead with French victories (`victory_won` led 9 of 21
    turns). The class exists and fires.
  - CA8-1: terminal and campaign-log casualty figures agree (both carry the whole-army total);
    only Berthier's report is still lead-only (F2).
  - IGR-E: the plunder prompt states its price on every capture route ("Plunder it for 800 gold")
    and the figure quoted is the figure paid.
  - IGR-F: the letter-book renders, batches minor courts, re-titles itself "THE SMALL COURTS
    WRITE", and answers correctly through its own panel route.
  - CA8-8: the recurrence register is live and good — *"Bernadotte resents Ney's laurels again,
    2 turns after the last"* -> *"...has become entrenched. The wound will not close on its own."*

### ROOT CAUSE — the three contradictory advisors (my finding #8)
`movement_executor.py:661-669`. The `[HINT] X is undefended` test is:
```
enemies_there = world.get_marshals_in_region(adj_name)      # <-- TARGET REGION ONLY
enemy_marshals = [m for m in enemies_there if ... strength > 0 and at war]
has_garrison   = adj_region.garrison_strength >= 5000 or (...)
if not enemy_marshals and not has_garrison: capture_hints.append(adj_name)
```
It never looks at provinces **adjacent to the target** — which is precisely where the
reinforcement that decides the battle comes from. At Tyrol the hint fired while Charles (46,573)
and John (17,784) stood in **Milan, adjacent to Tyrol**.
So the game's three "should I attack?" advisors each use a different neighbourhood:
  - `[HINT]`      : target region only            -> said "undefended"
  - the objection : includes adjacent strength    -> said "the enemy is too strong" (correct)
  - MUSTER preview: player's own side only        -> would have said "favorable"
This hint has already been narrowed once for a different false-positive class (the in-code comment
records it urging an attack on Bavaria's Franconia, a French ally). The adjacent-reinforcement
class is the same bug one step out.

### T24 RE-MEASURE — F9/F14 NARROW (and are more useful narrowed)
Re-ran `propose peace to Austria` at T24 and re-read `active_wars`:
  - war_score **6 (T4) -> 13 (T16) -> 22 (T24)**; tier `white_peace` -> **`favorable_terms`**
  - breakdown now `{territory: 15, battles: 27, decisive: 0, capital: -20, ticking: 0}`
  - recommended terms are now `sweeteners: [], demands: [{gold_per_turn: 107}]`
**So the leverage number is NOT frozen and the generator does NOT always pay the winner.** Both of
my earlier statements were too strong and I am correcting them rather than shipping them.
The accurate, and still serious, findings are:
  1. **The threshold at which the default flips from paying to demanding is far too high.** At T16
     I held two Austrian provinces, had captured Mack and destroyed his army, and Talleyrand
     recommended paying Austria 77g/turn. It took until T24 — nine battles and 24 turns — for the
     default to become a 107g/turn demand.
  2. **Territory is never demandable at any harshness, at any score I reached** (both harsh drafts
     at T16 and the default at T24 ask only for gold), while I occupied Austrian provinces
     throughout. The map cannot change hands by treaty in a winning war.
  3. **`decisive: 0` while `decisive_won: 1`, still, at T24** — the decisive-victory component has
     contributed nothing for 24 turns.
  4. **`capital: -20`** is a 20-point penalty I cannot account for and which no surface explains;
     it is the second-largest term in the breakdown and it is working against the winning side.
     Flagged for code verification rather than asserted.
**`capital: -20` — WITHDRAWN as a defect, before filing.** `diplomacy.py:2881-2902`: the term is
-20 when the opposing side controls a capital on my side. My vassal **Kingdom of Italy's capital
is Milan, and Austria has held Milan since turn 3**. Paris is French-held (checked). So the term is
correct and the D2 war-level aggregate is doing its job.
It leaves only a **legibility** note, P3: the breakdown prints `capital: -20` with no label, and
nothing anywhere tells the player it means "an ally's capital is occupied" — so the second-largest
term working against them is unexplained. Not a bug; a missing sentence.

### FINAL NARRATION TALLY (25 turns of dispatches, T2-T26) — hard numbers
Most-repeated player-facing dispatch lines (headline or sub-beat), verbatim:
  **x14** "Sire — Marshal Davout's household goes unpaid. His patience erodes with his purse."
   x2  "Sire — Austria and Bavaria have made peace without us."   <- the campaign's biggest
       diplomatic event, and it appears exactly twice, both times as a sub-beat, never as a lead
   x2  "Sire — Marshal Davout holds the field at Bohemia — Archduke Charles's corps is broken..."
   x2  "Sire — Marshal Soult holds the field at Bohemia — Archduke Charles's corps is broken..."
   x2  "Sire — Marshal Ney holds the field at Bohemia — Schwarzenberg's corps is broken..."
   x2  "Sire — our ally's marshal Deroy was broken at Hungary. Bavaria reels."
Headline class distribution over 25 turns — only **seven distinct classes ever fired**:
  victory_won 11 · own_broken 4 · marshal_captured 4 · supply_strain 2 · estate_eroding 2 ·
  ally_broken 1 · levy_open 1
Regions were frozen at **31/95 from T16 to T26** (eleven consecutive turns).

### ROOT CAUSE — the line that appeared 14 times
`dispatch.py:789-815` (PC-7, the standing-class lead cooldown). `estate_eroding` IS in
`STANDING_HEADLINE_CLASSES` and the cooldown DOES work — after `STANDING_LEAD_MAX` turns it yields
the lead to any other candidate. But the code's own comment says what happens next:
  *"the standing one falls to a **sub-beat** through the loop below, so it is reported, never
  deleted."*
So the cooldown stops a standing condition **leading** every turn; nothing stops it **appearing**
every turn, and it appears in the identical words. Measured: 14 occurrences of the same sentence
across 25 dispatches (2 as headline, 12 as sub-beat).
There is even machinery for the missing half — `_STANDING_ESCALATION` supplies "says something new
about how long it has gone unanswered" variants — but it is consulted **only on the branch where
the standing class keeps the LEAD** because it is the only news. A demoted sub-beat gets no
variant, no counter, and no suppression.
**This is a design gap, not a broken cooldown**, and it is the largest single contributor to the
narration pillar reading as repetitive.

### F5 SELF-REFUTED AND REPLACED — "supply capacity is unlookupable" is WRONG
I checked the client before shipping this and it does not hold.
`region_panel.gd:179` renders `"   Supply: " + format_number(data.supply_capacity)`, and
`world_state.py:7592-7599` DOES emit `supply_capacity` in the map summary — for own regions **or a
foreign region at FULL visibility**. A marshal's presence sets FULL, so **the province my army is
standing in always shows its capacity in the region panel.** My claim that the number is
unavailable where it applies is false, and I withdraw it.

**What is actually there, and it is a real defect (P2):**
`world_state.py:7606-7616` — below FULL visibility the backend sends `income_value: 0`,
`stability: 0`, `war_damage: 0`, **`supply_capacity: 0`** as "safe defaults so Godot doesn't crash
on missing keys". But `region_panel.gd:176-179` prints Income / Stability / Supply
**unconditionally** in the visible branch, with no "unknown" arm. So a scouted-but-not-occupied
province renders:
    `Income: 0g   Stability: 0%   Supply: 0`
— three fabricated zeroes presented as facts about a province that may feed 40,000 men. The panel
already knows the visibility (it prints "Intel: Partial (reports only)" two lines above), so it has
everything it needs to say "unknown" instead. **Fog defaults are being rendered as data.**

The play-level complaint that generated the false claim survives in a better form and belongs to
F4, not F5: **nothing at ORDER time mentions supply.** The number is on a panel the player must
think to open, on a province they must already occupy; the muster preview that talks them into
concentrating never mentions it.
