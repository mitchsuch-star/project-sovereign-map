# S14c — "Events and Historical Moments": the gate record

**Status:** ✅ **RULED October 22, 2026 under the user's standing delegation**; **part 1 ✅ LANDED October 22, 2026** (the engine and its transport, unarmed — the landing record §13); **part 2 ✅ LANDED October 22, 2026** in two landings (the client and the instruments — §14; three letters armed — §15) ("make design calls please do research"), on master at `131eeebf`. **Owner:** Pre-Deploy S14c (`docs/PRE_DEPLOY_PLAN.md` §2, sized 4.0), built in four parts (§9). Nothing is built. In code the deck is **moments** — module `backend/game_logic/moments.py`, world field `world.moments`, scenario key `moments`, log type `moment` — because "event" already means `event_log`, `log_event` and `queue_dispatch_event`.

**How it was ruled.** Eight read-only researchers mapped the seed machinery, the content menu, the transports, the seams, the history and the calendar, the drama the game already derives, pacing and caps, and the client, series and pins. Three designers drafted complete proposals from three angles (history-first, player-experience-first, systems-reuse-first); three judges scored them through a historian's, an architect's and a playtester's lens (history-first 8 / 7 / 8, player-first 7 / 8 / 7, systems-first 5 / 5 / 4); a synthesis took the history-first base and grafted the judges' named improvements; two adversarial critics checked it against the repo (with probes on the booted 1805 world) and against the rules and the history, and returned 30 corrections — three blocking — **every one applied below or answered (§12)**. The critics' probes changed the deck: the first synthesis promised consequences the shipped board does not have (the Holland letter's closure, the Decree's bite), and those are now gated on the board that makes them true, or measured as zero and said so.

**No user ruling is reversed.** One reduction of the row's own promise is flagged for the user (A1 — the situational events and two named moments struck because the board already derives them; the user may overrule it at any time, `docs/STATUS.md` ▶ NEXT UP names it). Six amendments of ruled specs, each carried into its spec when its part lands:

| | Amends | What |
|---|---|---|
| **A1** | `PRE_DEPLOY_PLAN.md` §2 S14c row | Trafalgar's news and Tilsit as events, and the three situational examples (a marshal's quarrel, a province's unrest, a court's overture), are **struck** — each already has its covering surface (§11); the answers' seams narrow from "gold, trust, relations, stability, a court's alarm" to the closed op table (§3.2: trust and stability have no safe setter); "two or three answers" reads as two buttons plus the free lapse; "events about AI courts" reads as: every effect on an AI court lands through the shared function, and no AI court is an audience (Q6). **A user-visible reduction, named for the user.** |
| **A2** | `dialogue_manager.py` | a moment letter does not freeze the diplomacy wizard; the end-turn warning counts only letters that will lapse (S14C-X1, X2) |
| **A3** | `AI_INTENT_SPEC.md` §3.8.1 | gains clauses A–G for moments (§5) |
| **A4** | `DESIGN_REFINEMENT.md` the Content Menu row; `ROADMAP.md` "Positive Events" | the menu picked and struck as in Q7 (recorded on the row at this gate) |
| **A5** | `treaty.py` `_letter_kind` | a `moment` letter kind and a non-treaty registry (S14C-X8) |
| **A6** | `VP1_DESIGNS_SPEC.md` §11; `imperial_designs.py` | the hand-off closed by §3.6; `road_state(world, road_id)` becomes the one public reader and every inline "forsworn" test routes through it (S14C-X17) |

Kept as ruled: VP-1 Q6 (no dynasty tag, throne store or "Bonaparte Naples" template); "no mechanic reads the calendar"; IGR-1's lesson (a small authored deck, budgets in the producer); "diplomacy is never typed" (every answer is a button whose command is the executor's); the LLM never affects mechanics.

---

## §0 The gate record

| # | Question | Ruling | Rejected (the historically fuller option named) |
|---|---|---|---|
| 1 | Do events earn their place? | **A moment earns a place only if the record offers Napoleon a real fork, no board system already puts that fork in front of him, and one consequence outlives the fade.** About 40 moments of 1805–1807 were audited; **four qualify**, all letters: the Bavarian Match (no door exists), the Throne of Holland (the lever exists, the moment does not), the Crown of the Reich (no backend mention of the Holy Roman Empire at all), the Decree of Berlin (the law exists, LAWS was opened 0 times — DDB-D7 — and the letter is its door, only when it bites). The board already derives Ulm, Austerlitz, Pressburg, Jena, Eylau, Friedland, the Confederation, Naples, Tilsit, Trafalgar and the principalities (§11). The row's situational examples fail the test: a quarrel is jealousy's petition kinds, an overture is the AI ladder's asks, unrest regrows +5 to +10 a turn so buying it back is a fake choice. | The full calendar (IGR-1's flood was doubled beats). A choice-less beat for the Reich (no consequence; it doubles VP-1's `design_fulfilled` line — critic). A Trafalgar news beat (asserts a fight the board may not have had). *Fuller:* a sustained-unrest mechanic (Masséna's years in Calabria) — a new mechanic, unasked. |
| 2 | The engine's shape | **One store, one trigger rule, one transport, one closed effect table of shared functions** (§3). Transport: the `incoming_proposal` dtype, `proposal_type = "moment_letter"`, the standard `accept_ai_proposal` / `reject_ai_proposal` ids. **Two answers plus the free lapse.** A letter stands **two player turns**; unanswered, it lapses as the decline. It has **no court**: no `target_nation`, no `context.source` (the Cabinet speaks). No `random`, no parser, no LLM; windows resolve at boot. | A new dtype (about ten whitelist sites). The marshal-petition card (single slot, marshal-bound). A log-lookback latch (the 500-row log evicts it). A per-moment module flag (the lever cap is 231 / 231). A third button (Counter costs DP and is hidden for non-bargain letters). |
| 3 | The deck | **Four letters** (§2): the Bavarian Match (T8), the Throne of Holland (T18), the Crown of the Reich (Road I, after the Confederation), the Decree of Berlin (T29, only when it bites). Each answer's consequence is a shared function's, quoted before the choice from the same plan that applies it; **each letter's premise is the board state that makes its fork real, and a falsified premise is passed silently** (G). | Letters whose consequences the board cannot deliver (the first synthesis's Holland closure and Decree bite, refuted by probe). A third answer "annex Holland" (1810, no verb exists). |
| 4 | Caps and pacing | **Authored in the block, not module constants** (§4): one open letter at a time; at least 3 turns between letters; at most one moment per producing turn. **R1:** a letter waits out any foregrounded crisis within its grace; still waiting when the grace ends, it is `passed(crowded)` and ends on screen as a receipt. Arrival has no headline; the rail notice and the mailbox carry it. | A shared foreground (it would double a crisis). Rolling-window caps (slack on a four-letter deck — critic; struck, not deferred). A "wounded morning" rule (it reads the previous morning's lead and is inert in every harness — critic). Silent drops. |
| 5 | Per-seed variation | **Timing only**: M1, M2, M4 dates vary inside authored bands whose `value` is the date's own turn; content, gates and prices are fixed on every seed; `historical` collapses to `value`. The Reich letter is causal and never varies. | Seeding the cast or the outcome (the Oubril "Tsar disowns" die puts a roll inside a quote). |
| 6 | AI symmetry | **The deck is France's content** — an asymmetry of content, not of code (VP-1 §7). No AI court receives or answers a moment. Every effect on an AI court goes through the shared function; the op table is nation-parameterized and a census finds no nation literal in `moments.py`. | AI courts as an audience (a second decision engine beside `intent.py`; `soap_opera_share` is already 0.91–0.98). |
| 7 | The Content Menu | **Join:** R22 (the Match) and R25 (Holland), one dated letter each. **Fold:** R118 (every answer's quote line is the acceptance preview) and R127 (a named foreign voice resolves through `resolve_named_diplomat()`). **Strike:** R27 (owned by AI-3b, `AI_INTENT_SPEC.md` §16.1-2), R35 (DDB-4's haggle shipped), R133 (the threat-40 notice, the brewing card and war-council beat 2 cover it), Gneisenau (not on the roster; a combat modifier belongs in `marshal.py`), R22's standing action, its "block war 5 turns" and AI-court marriages, R25's "3–4 random" quota, the ROADMAP "Positive Events" table. "Imperial Governance Events" stays where `ROADMAP.md` homes it ("Later", behind its own gate). | All eight rows. *Fuller:* a standing marriage bond between houses — a dynasty store VP-1 struck. |
| 8 | The VP-1 hand-off | **Structural, not by review** (§3.6): one gate function over `imperial_designs.road_state`; an op vocabulary that cannot reach VP-1's teeth or verbs; the 3-road × 4-moment matrix pinned in the part that arms each moment. | Per-moment hand-written guards. A Confederation or Tilsit decision (VP-1's proclamation and the Raft are those doors). |
| 9 | The client | **No new modal, no new dtype.** `incoming_proposal_popup.gd` gains an `is_moment` register: the dateline, the record, the board, a "What each answer does" block in the body, the unanswered line. Captions come from the payload; every lapse surface prints a whole sentence (S14C-X15). | A new scene. Tooltip-only consequences (SFR-B11: invisible). |
| 10 | Measurement | **Ceilings on every arm, floors where moments can fire:** the 10-seed 40-turn sweep (`tools/ai_v_sweep.py`) pins the ceilings and that no moment fires outside its premise; the commanded arms and the VP-1 road arms report each moment per seed; `tests/test_moments_pacing.py` holds both; the series lands unarmed, then arms with named function seams and counted reach (§7). | A cap-only pin (IQ-6 N2: green when nothing fires). A floor on the passive board, where three of four premises are false by measurement. A 44-turn arm (no moment is dated past turn 32). |
| 11 | Sizing | **Four parts of about one session** (§9), the client landing before any moment is armed. | One large part. |
| 12 | Siblings | **S14C-X1 … X17** (§10), each reproduced before it is built, each with an owner part. | Building on any unreproduced. |

### §0.1 The disagreements, resolved

| Disagreement | Ruled | Because |
|---|---|---|
| Base: history-first vs player-first | **History-first** | Totals 23 / 22 / 14; player-first's faults (arming before the client; a sender-less letter with unlisted seams) are graftable, history-first's engine discipline is not |
| The Reich: a beat, or a fork | **A letter** (the critic's challenge upheld) | A choice-less beat has no consequence and repeats VP-1's fulfilment line; the record offers a real fork — Napoleon's ultimatum of 22 July 1806 that Francis lay down the crown — with a durable price on each side |
| The Match: dominated? | **Durable both ways** | Accept's lasting effects were all costs; now a vassal Bavaria's loyalty rises (persistent) and declining slights Munich (relation −5) — a plan-dependent fork, judged again at S14e |
| Holland's closure | **Derived from the real predicate, printed even at zero** | Holland boots at war with Britain, so her ports count whatever her autonomy (critic probe: 10 → 10 of 26); the letter's fork is tribute against loyalty, and it arrives only when Holland is slipping |
| The Decree's bite | **The letter arrives only when enacting it would shut ports** | On the shipped board no client is both Autonomous and at peace with Britain (critic probe: `decree_clients` = []); a letter selling a law that buys nothing would be a trap |
| Letter life: 1 turn vs 2 | **2 turns** | A once-in-a-campaign fork should not die on one hurried morning; the residence across an AI phase is counted by arm MK (§7) |
| Sender: a real court vs none | **None — the Cabinet** | The Reich and the Decree have no sender; a real court lets an ignored moment silence that court's genuine proposals through the cooldown loop |
| Closed Accept | **A `moment` kind and arm in `treaty`** | `refresh_letter_verdict` restamps every accept option from `can_sign`; a fall-through erases the closure |
| Caps | **One open letter, a 3-turn gap, one per turn, R1** | The rolling-window caps and the wounded-morning rule bind nothing on a four-letter deck (critic); struck rather than shipped as decoration |
| Module name; `seeded_tiebreak`; sweep length | **`moments`**; **no caller**; **40 turns** | `event` collides with `event_log`; there is no casting draw, so ties fall to authored order; the last window closes at turn 32 |

---

## §1 Why (measured)

**The board derives almost everything** (Q1). The calendar is display-only and the scenario holds no turn-scheduled content but the Verdict (`campaign_end.verdict_turn: 44`), so this deck is the first; windows resolve to turns at boot and the calendar stays display-only (the inverse `calendar.turn_for_date` is validator-side only, pinned). The turn map (one turn a half-month from 25 September 1805): Ulm and Trafalgar T3, Austerlitz T6, Pressburg T7, Eugène's wedding T8, Louis's crown T18, the Confederation T20, Napoleon's ultimatum to Francis T21, the Reich's end T22, Jena T26, the Berlin Decree T29, Eylau T34, Friedland T42, Tilsit T44 (the Verdict's own turn).

**The passive board, measured** (passive France, `historical` seed, a scratch probe and the critics' re-probes; the repo untouched):
- **Bavaria:** ALLIANCE at boot (relation 60), **PEACE with 0 provinces and not an active nation from turn 5** on the series harness; alive under other harnesses. The Match is a played-board moment.
- **Holland:** France's Satellite throughout, **at war with Britain from boot** (`starting_wars`); loyalty 74 (T14) → 66 (T18) → 72 (T22) → 91 (T31) — a dip and a recovery, not a slide. Granting autonomy moves the closure 10 → 10 of 26 (her ports count through the at-war branch of `naval.ports_by_court_against`).
- **The Decree:** `law_refusal("berlin_decree")` reads enactable from turn 1; enacted, the closure stays 10 → 10 (`naval.decree_clients(world, "Britain")` = []): it bites only on an Autonomous client at peace with Britain.
- **The queue:** an `incoming_settlement_offer` stands as the current dialogue from turn 11 to turn 32; no foregrounded crisis at turns 8, 18, 29.
- **France:** points at the cap of 7 from turn 4; chest 8,835 (T18) and 7,690 (T29); provinces 28 → 17 (T18).

So on the passive board three of four premises are false (Bavaria gone, no Road I, no bite) and Holland's holds where its loyalty dips: **the moments are a played-board layer**, and the pins measure them where they can fire (§7).

---

## §2 The deck

**The copy contract (every letter).** Five parts, validator-limited (title ≤ 40, record ≤ 240, caption ≤ 36 characters): the **dateline** (the in-game `calendar_label`, never a historical date); **the record** (authored, past tense, "historically" where it names a date or a city the board may not have); **the board** (derived lines: diplomatic facts and the player's own state, never an AI court's chest, stability or army); **the answers** (a "What each answer does" block — the plan's own lines); **the unanswered line** ("If unanswered by {label}: {the decline}"). A window is eligible from its resolved turn to `turn + grace`; the validator checks each `date` against its turn. Every `when` is a named, parameterized predicate; the code holds no nation literal. **A premise false for the whole window is `passed(premise)`: silent, no row — nothing was promised.**

### M1 `bavarian_match` — The Bavarian Match (letter; R22)
- **Window:** 14 January 1806; turn `{value 8, band [8,10]}`, grace 2. **Roads:** any. **Voice:** the Cabinet (Napoleon's family council).
- **When:** `court_warm{court: Bavaria, min_relation: 30}` — Bavaria is active and is France's ally or vassal, or at peace with France at relation ≥ 30.
- **Record:** Eugène, adopted by Napoleon, wed Augusta of Bavaria at Munich (historically 14 January 1806); she had been promised to Baden's heir, and Munich yielded to the Emperor's pressing.
- **Accept, "Seal the match":** 2 DP (`vassal._charge_dp`); 1,000 gold (a purchase: charged and `record_gold_spent`, the `imperial_designs.decree` model); Bavaria relation +20 (`modify_nation_relation`, delivered after the clamp); **if Bavaria is France's vassal, her loyalty +15** (the vassal row, clamped — persistent); Europe's alarm +3 (`coalition.add_threat`, source `moment_bavarian_match`, label "A Bonaparte match").
- **Decline, "Let Baden keep her":** Bavaria relation −5 (Munich had agreed; the slight is remembered).
- **Quote:** "Seal the match: 2 DP and 1,000 gold (you hold N). Bavaria's goodwill R → R′ (it cools about a point a turn); {as your vassal, her loyalty L → L′ | — }; Europe's alarm A → A+3 (a Bonaparte dynasty). Let Baden keep her: Bavaria's goodwill R → R−5."
- **The weakest row, said plainly:** the fork is plan-dependent (a Road I player values a loyal Bavaria). S14e's three players judge it: kept, or its one block entry deleted with its count pin (§11).

### M2 `throne_of_holland` — The Throne of Holland (letter; R25)
- **Window:** 5 June 1806; turn `{18, [17,19]}`, grace 2. **Roads:** any. **Voice:** Holland's minister Schimmelpenninck through `resolve_named_diplomat()` (loyalist register).
- **When:** `vassal_slipping{court: Holland, below_autonomy: 2, loyalty_at_most: 70}` — Holland is the owner's vassal, not yet Autonomous, and its loyalty is at or below 70 **or** its forecast net drift (`vassal.forecast_vassal_loyalty`) is negative.
- **Record:** the Batavian Republic asked for a king and was given Napoleon's brother Louis (historically 5 June 1806); the alternative was annexation, which came in 1810 when Louis would not enforce the System.
- **Accept, "Crown Louis":** `vassal.change_vassal_autonomy(Holland → Autonomous)` through one `vassal.autonomy_change_plan` the executor itself now reads (S14C-X10): 1 DP, loyalty +int(10 × the grip multiplier) clamped, tribute 75% → 50%, the drift term −2 → +1 (`AUTONOMY_DRIFT`), and the closure **derived**: `naval.closed_ports_against` before and after on the plan.
- **Decline, "Keep the Republic":** nothing.
- **Quote (derived):** "Holland becomes Autonomous: loyalty L → L′ (the grip-blunted gain); its autonomy drift −2 → +1 a turn; tribute 75% → 50%, about −G gold a turn; {its 2 ports leave the count against Britain, C → C−2 of 26, unless the Berlin Decree stands | its ports stay counted — Holland is herself at war with Britain}." Declining: "Holland stays a Satellite: tribute 75%; her loyalty forecast L → L″ next turn."
- **The fork:** tribute against loyalty, offered when Holland is slipping; the closure line is the board's truth (usually unchanged on the 1805 board, where Holland fights Britain).

### M3 `crown_of_the_reich` — The Crown of the Reich (letter)
- **When:** `design_fulfilled{design: rhine.confederation}` and Austria active and not the owner's vassal; fires **lag 1** turn after the fulfilment turn, grace 2. **Roads:** `["rhine"]`. No band and no calendar floor (causal fidelity beats date fidelity; an early Confederation earns an early ultimatum). Resolving at or past `verdict_turn`, it is `passed(verdict)`.
- **Record:** with the Confederation signed, Napoleon told Francis II to lay down the crown of the Holy Roman Empire (historically 22 July 1806); Francis did so on 6 August, and the Reich of a thousand years ended.
- **Accept, "Demand the abdication":** each member of the Confederation that is the owner's vassal, loyalty +10 (the vassal rows, clamped — persistent); Austria relation −15; Europe's alarm +3 (source `moment_reich`, label "The Reich's end"). Le Moniteur's special "THE EMPIRE IS NO MORE" (81) prints in the next issue on this answer only.
- **Decline, "Let Francis keep his crown":** nothing.
- **Quote:** "Demand the abdication: the Confederation's princes are the Emperor's alone — {member L → L′ for each vassal}; Austria's goodwill R → R−15; Europe's alarm A → A+3. Let Francis keep his crown: no change — the Reich survives in name."
- **Not a double:** VP-1's fulfilment already costs Austria and Prussia −30 and +10 alarm; this is a later act with its own small price, and the op table cannot reach a VP-1 source (§3.6).

### M4 `decree_of_berlin` — The Decree of Berlin (letter; a second door)
- **Window:** 21 November 1806; turn `{29, [28,30]}`, grace 2. **Roads:** `["none","system"]`. **Voice:** Talleyrand through `resolve_named_diplomat()`, as the sceptic: cost first, the objection in a clause.
- **When:** `law_bites{law: berlin_decree}` — the law exists for the owner and is not in force, the owner is at war with `naval.trade_dominance_nation`, **and enacting it would shut at least one port** (a client Autonomous and not at war with the target: `naval.decree_clients` read as if enacted is non-empty).
- **Record:** historically, from Berlin after Jena (21 November 1806), Napoleon declared the British Isles in a state of blockade and shut every port of his allies to British goods.
- **Accept, "Sign the Decree":** op `enact_law` = **the full verb** — `reforms.law_refusal` passes, `reforms.enact_law`, then `world.use_admin_action()` (the executor's own charge — critic): 15 authority, 150 gold a turn, 1 administrative action.
- **Decline, "Not yet":** nothing; the Decree stays in the LAWS book.
- **Quote:** "Sign the Decree: {`reforms.terms_line`} and 1 administrative action; every client shuts its ports to British goods whatever its autonomy — closure C → C′ of 26. Not yet: no cost, the Decree stays in the LAWS book."
- **Measured:** passed(premise) on the passive board (no bite); it arrives on a board where a client is Autonomous and at peace with Britain — the Holland-Decree chain the history records. Reported per seed, never forced.

---

## §3 The engine

### 3.1 The block
`europe_1805.json` gains a `moments` key: `owner`, `pacing` (§4) and `deck[]`; an entry carries `id`, `kind` (`letter`; the engine keeps no beat kind until a deck needs one — struck, not deferred), `title`, `date` (check-only ISO), `turn {value, band}` or `lag`, `grace`, `when` (a predicate name with parameters), `roads`, `voice`, `record`, `accept` and `decline` (`{caption, ops}`). **Predicates and ops are code, named by the deck:** `PREDICATES` (pure `(world, owner, params) → bool`, reading named courts through cached helpers, never `regions.values()`) and `OPS`, a closed vocabulary. `_validate_moments` checks every name.

### 3.2 The ops (closed)
`gold` (a purchase: charge + `record_gold_spent`, shown as Spent), `dp` (`vassal._charge_dp`), `relation` (`modify_nation_relation`), `alarm` (`coalition.add_threat`, each source with a `_THREAT_SOURCE_LABELS` row), `loyalty` (a vassal row of the owner, clamped `LOYALTY_MIN … LOYALTY_MAX`, through one `vassal.adjust_loyalty` helper this row adds — the 17 raw writes stay), `autonomy` (`change_vassal_autonomy`), `enact_law` (the full verb, admin action included). **Out, each for a stated reason:** trust and glory (no clean setter; AI trust is read by nothing), war exhaustion (no delta setter), manpower (truncated at the next regen), AI authority (a zero-caller wrapper, defaults 60 / 75 / 0), war score (derived only), stability (self-heals, no setter), and any VP-1 source or verb.

### 3.3 Shown = applied
`moments.plan(world, moment, answer)` returns the delivered, clamped figures, the refusal and the lines, once. The letter renders the plan; the answer applies the same plan. A battery pin compares plan and before / after on three boards (rich, poor, clamped) for every op. A closed Accept is stamped `enabled False` with the executor's words: the letter stands.

### 3.4 The transport (ten seams)
A moment letter has **no court**: no `target_nation`, no `context.source`; `context.proposal_type = "moment_letter"`; `moments.is_moment_letter(dialogue)` is the one predicate every reader asks.
1. **Delivery.** `moments.deliver_letter` builds and pushes the dialogue, writes one `moment` / `arrived` row and one rail notice; it does **not** use `deliver_ai_proposal` (which indexes `proposal["source"]` and writes court-named rows).
2. **Verdict.** `treaty._letter_kind` returns `"moment"` before the generic context test; `can_sign` gains a `moment` arm calling `moments.answer_verdict`; `refresh_letter_verdict` accepts the kind.
3. **Answer.** One branch at the head of `_handle_accept_ai_proposal` and `_handle_reject_ai_proposal` calls `moments.answer`: re-derive the refusal, apply the plan, write the store and one `moment` / `answered` row. The counter handler refuses.
4. **Recovery.** `main._build_pending_envoy_popup_from_dialogue` calls `moments.refresh_letter`, re-planning and restamping at every read.
5. **Lapse.** `lapse_pending_offers` consults `moments.keeps_open` beside `call_to_arms.keeps_open` and `moments.lapse_default` (applies the decline plan); `_extract_lapse_info` returns `nation: ""` for a moment letter (its `"Unknown"` fallback would write cooldown keys for a court called Unknown — S14C-X9), both cooldown writes stay `if nation`-guarded.
6. **Lapse surfaces.** `dispatch._lapsed_offer_row`, `main.gd`'s LAPSED ENVOYS block, `dispatch_view.gd` and the `offer_lapsed` one-liner each print the moment's own sentence ("The Throne of Holland was left unanswered: Holland stays a Satellite."), the way petitions do (S14C-X15).
7. **Notice.** The rail notice carries a stable detail key and the two unfiltered `dismiss_by_type(DIPLOMATIC_PROPOSAL)` sites spare a still-open moment letter (S14C-X14); its button activates the letter (one click beside a standing settlement offer).
8. **Mailbox.** `_make_summary` labels the row by title, source "The Cabinet"; `MAILBOX_SUMMARY_LABELS` and `PROPOSAL_TYPE_DISPLAY` rows; `mailbox_priority` ahead of routine small-court letters.
9. **Wizard.** `has_current_turn_offers` skips moment letters; `get_lapsing_count(current_turn)` becomes `keeps_open`-aware, its five `main.py` callers passing the turn (S14C-X1).
10. **AI readers.** `_has_pending_proposal_from`, `_covered_members_envoy_pending` and the other `iter_queue` readers key on source / target, both absent; a census over the reader sites pins that a standing moment letter changes no AI decision.

### 3.5 State, tick, saves
- **State:** `world.moments = {"block": {...}, "state": {id: {"status", "turn", "answer"?, "reason"?}}}`, status ∈ `fired | answered | lapsed | passed` (pending is the absence of a row). The latch lives in the store, never the 500-row log.
- **Tick:** `moments.tick(world)` runs in `_advance_turn_internal` between `process_intent_movements` and `process_gazette`; `current_turn` is already the new morning. It expires closed windows, lists eligible moments in (turn, authored order), applies §4 and fires at most one. No draw at tick time.
- **Saves:** `to_dict` / `from_dict` through one `store_from_data` (the `imperial_designs` idiom); **`to_dict` stays at 500 lines** — the key folds into an existing line (the ratchet's over-500 count stays 28, S14C-X16). No block means unarmed: the tutorial, the bare flag world, the legacy rollback. A pre-S14c Europe save is backfilled from the shipped block with its saved seed; a windowed entry whose `hi + grace` is past, or a causal entry whose trigger turn + lag is at or before the save turn, is written `passed(before_save)` — nothing fires retroactively. `tests/test_serialization_enforcement.py`, the played-world census, `SAVE_FORMAT_REFERENCE.md` and `MODDING_FORMAT.md` are updated.

### 3.6 The VP-1 hand-off, exactly
- **Reads:** only the public `imperial_designs.armed`, `proclaimed_road`, `is_fulfilled`, `fulfilled_turn` (amended at part 1: the Reich's lag counts from a turn `is_fulfilled` cannot give — §13.2) and the new `road_state(world, road_id)` → `proclaimed | forsworn | open` (every inline "forsworn" test in `imperial_designs.py`, the dispatch and the executor routes through it — S14C-X17).
- **The gate:** `roads` contains `"any"`, or the proclaimed road, or `"none"` when no road is proclaimed; any other proclaimed road is forsworn: the moment is `passed(forsworn)`, silent, no row.
- **Never doubles a proclamation, structurally:** the op table has no `proclaim_design`, `decree_act` or `imperial_designs` write; the validator rejects the alarm sources `act_of_confederation`, `schonbrunn`, `blockade`, `acts_of_the_empire`, `decisive_peace`; a pin asserts every moment's op sources are disjoint from VP-1's teeth.
- **The matrix (3 roads × 4 moments, 12 cells):** M3 only on Road I; M4 with no road and on Road III, silent on I and II; M1 and M2 road-agnostic. **Each moment's cells are pinned in the part that arms it** (critic: never a landing with an armed moment and its cells unpinned).
- **Tilsit and the Raft:** struck as moments (the Raft is VP-1's Act; turn 44 is the Verdict's own turn).

---

## §4 Caps and pacing

**The authored `pacing` block** (validator-clamped): `max_open 1 · min_gap 3`. A validator rule proves the unperturbed schedule keeps the gap: for consecutive windowed letters `hi + grace + min_gap ≤ next lo` (10 + 2 + 3 = 15 ≤ 17; 19 + 2 + 3 = 24 ≤ 28); the causal M3 falls between them or is deferred by the gap at runtime.

**Rules.**
- **R1 (crisis).** A letter does not arrive while any war-intent record is foregrounded (`war_council.foreground_in_tenure(world)` — "a foregrounded record exists", the soft and hard stalls included; one pure pair beside the rule, `record_in_tenure(record, turn)`, which the inline test in `war_council.py` now calls); it waits within its grace.
- **R2 (nothing silent).** A letter still waiting when its grace ends is `passed(crowded)`, its decline plan applied, with one receipt: a `moment` / `passed` log row and a `moment_receipt` rail row (no headline).
- **R3.** One moment per producing turn; moments never take or set the foreground.
- **R4.** An unanswered letter ends on screen through the lapse surfaces (§3.4 seam 6).

**Rows.**
- **Log:** one `moment` type, phases `arrived | answered | passed`; tier NOTABLE; `CATEGORY_MAP` diplomacy; a branch inside an existing `_oneliner_*` stage (the twelve stay pinned); it rides `_is_player_event` (`filter_campaign_log` stays at 499 lines). `CAMPAIGN_LOG_TYPES` 179 → 180 across the 14 pin files and the IQ-7 provenance census.
- **Dispatch:** no headline class (arrival rides ENVOYS AWAITING, the mailbox badge and the rail notice; an answer's consequences land in their own rows — the relation, the alarm, the law); `moment_receipt` joins `_DIPLOMATIC_EVENT_TEMPLATES` and `_DIPLOMATIC_EVENT_PRIORITY`, fog rule `"always"` (diplomacy has no fog).
- **Le Moniteur:** `moment` joins `_COURT_TYPES`; one special, "THE EMPIRE IS NO MORE" (81, free in `_SPECIAL_WEIGHTS`), on M3's Accept only.

---

## §5 Per-seed bands (D7)

**What varies.** Only M1, M2 and M4 dates, by `seeded_int(seed, "moment::{id}::turn", lo, hi)` in a new branch of `apply_scenario_variance` (the relations-band idiom); it resolves at boot, strips the band and serializes a concrete int, so a later edit to the authored band cannot disturb a save. On `historical` each date is its `value`: T8, T18, T29. M3 is causal and has none.

**What is fixed on every seed** (extends AI_INTENT §3.8.1, pinned like its six clauses):
- **A.** Deck content (ids, predicates, ops, prices, grace, roads, copy) is byte-identical across `SWEEP_SEEDS`.
- **B.** Every resolved turn lies in its band; `historical` resolves to `value`.
- **C.** The unperturbed schedule keeps `min_gap` on every seed — a pure function of (seed, deck).
- **D.** Every windowed moment closes before the Verdict (`hi + grace < verdict_turn`); a causal one resolving at or past it is `passed(verdict)`.
- **E.** Eligibility reads the board and `imperial_designs`, never the seed.
- **F.** An unbanded entry has the same turn on every seed.
- **G.** A moment the board contradicts is `passed`, never forced.
- **Teeth controls:** `_variance_signature` gains `moment_turns`; the same seed twice compares EQUAL; variance forced off compares EQUAL to `historical`.

**The validator (`_validate_moments`).** `turn.value == calendar.turn_for_date(start_date, date)` (validator-side only); each band contains its value; windowed entries are pairwise disjoint and spaced; predicate and op names exist; ids are unique and collide with no law id; `roads` is valid; no op uses a VP-1 source; a decline carries no `gold`, `dp`, `autonomy` or `enact_law` op (the popup cannot grey a priced Reject — `incoming_proposal_popup.gd` greys accept-shaped actions only); the copy limits hold; every `voice` resolves.

---

## §6 The surfaces and the client

- **Popup.** `incoming_proposal_popup.gd` gains `is_moment` beside `is_petition` and `is_call_to_arms`: the header "A MOMENT OF HISTORY — {label}", the record, the board, the "What each answer does" block in the body, the unanswered line; Counter hidden; captions from the payload; `enabled` / `reason` read as for any letter; every figure `int()`.
- **Mailbox and notices.** `mailbox_panel.gd` labels the row from the title; the rail notice's button activates the letter; `main.gd`'s `_on_mailbox_activate_result` gains its missing else branch (S14C-X11).
- **Driver.** `tools/playtest_driver.py` gains `--moment accept|decline` (absent: `decline`, set in the policy only when passed, so every archived header is unchanged), plus a payload discriminator so unattended runs answer by intent, not option order (S14C-X3).
- **IQ-10 and the harness.** `cap_moment()` from `cap_petition()`; SHOTS rows for the Match and the Decree (the longest quote) at Interface Scale 1.0 and 2.0 with `must_show`, both answers above the fold; the parse harness gains `incoming_proposal_popup.gd` and exits 0; a census: no moment copy tells the player to type a diplomatic order.

---

## §7 The series and the arms

**Part 1 lands unarmed** (no `moments` block in the shipped scenario): `BASELINE_SERIES` byte-identical by construction. **Part 2 arms M1, M2, M4.** On the passive path the Match is `passed(premise)` (Bavaria gone), the Decree `passed(premise)` (no bite), and Holland arrives where its loyalty dips, stands two turns and lapses as an empty decline. **Byte-identical is the prediction, not a guarantee:** the new reach is a letter's two-turn residence across an AI phase, the `offer_lapsed` row with `nation ""`, the tick, the wizard exclusion.

- **Arms:** `tools/_s14c_series_arms.py`, a child-process tool in the `tools/_vp1_series_arms.py` style, chained from `tools/_vp1_series_arms_final.json` into `tools/_s14c_series_arms_final.json`. Each seam a **function**, held down and up with `REACH=` counted: **M0** the tick; **MW** the window resolver (a no-op on `historical`); **ML** the lapse default; **MK** the queue residence and lapse-loop side effects; **MN** the notice and log rows; **MH** the wizard exclusion; **MR** the crowd-out receipt. Arm 0 reproduces the prior record byte for byte; ALL is the shipped tree. Any movement is attributed and re-pinned as `SERIES_BEFORE_S14C`, naming this row.
- **The suite beyond the series** (critic): Part 2's head arms the block on a scratch tree, runs the suite, and lists every test that reads the dialogue queue, the mailbox counts, `lapsed_offers`, the `offer_lapsed` rows or the Gazette past turn 17; each is re-seated consciously or kept dormant by a conftest pin like `SOVEREIGN_SCENARIO=none`, and the choice recorded.
- **Archived arms** (CMD-A / H / M, DL, FLD, LAW, OP, VOLTE, FC) re-run with every AI-read field byte-identical; digest text attributed by `tools/_s14c_arm_attribution.py`.
- **The sweep:** `tools/ai_v_sweep.py`, the 10 `SWEEP_SEEDS` × 40 turns; `derive_metrics` gains `moments_arrived`, `moments_passed` (by reason), `moments_max_per_producing_turn`, `open_letters_max`, `letters_during_foreground`, `fire_turns`; `RunCapture` counts by object identity and learns the moment rows (S14C-X3).
- **Pins** (`tests/test_moments_pacing.py`, the ceilings read from the authored block). *Ceilings, every arm:* ≤ 1 moment per producing turn; ≤ 1 open letter; 0 letters during a foregrounded crisis; no moment fires with its premise false. *Floors, where moments can fire:* on the commanded arms and the VP-1 road arms (`tools/_vp1_road_arms.py`: VP1-RH reaches the Confederation, so M3) every moment whose premise holds in its window arrives in it or ends on screen as a receipt; each moment's reach is reported per seed — seeded paths, not laws. *The accept arm* (`--moment accept`): every delivered figure equals its quote.

---

## §8 Numbers (in-band tunables, all ints)

| Tunable | Value | Band |
|---|---|---|
| Match: DP / gold / relation / vassal loyalty / alarm / decline | 2 / 1,000 / +20 / +15 / +3 / −5 | 1–3 / 500–2,000 / 10–20 / 10–20 / 2–5 / −10 to 0 |
| Holland's gate (loyalty at most) | 70 | 65–75 (or the negative forecast) |
| The Reich: member loyalty / Austria / alarm | +10 / −15 / +3 | 5–15 / −20 to −10 / 2–5 |
| The Decree | the law's own price + 1 admin action | not tuned here |
| Windows | M1 `{8,[8,10]}`, M2 `{18,[17,19]}`, M4 `{29,[28,30]}`; grace 2; M3 lag 1, grace 2 | grace 1–3; lag 1–3 |
| `max_open` / `min_gap`; answer window | 1 / 3; 2 player turns | 1 / 2–5; fixed |
| Moniteur special | 81 | a free slot, not tuned |
| Copy limits (title / record / caption); `CAMPAIGN_LOG_TYPES` | 40 / 240 / 36; 179 → 180 | fixed |

---

## §9 The build — four parts, each about one session, each landing green

**Part 1 — the engine and its transport, unarmed** (no `moments` block in the shipped scenario) — ✅ LANDED October 22, 2026 (§13)
- *Head (reproduce first):* §1's measurements on ten seeds; S14C-X8 (the restamp erases a closure) and X9 (the `"Unknown"` fallback) on boards.
- *Scope:* `moments.py` (store, predicates, ops, `plan`, tick, lifecycle, R1–R4), `vassal.adjust_loyalty`, `war_council.record_in_tenure` / `foreground_in_tenure`; `_validate_moments`; `calendar.turn_for_date` (validator-only); the variance branch; serialization (S14C-X16) and backfill; the ten transport seams (§3.4) at their backend halves; `imperial_designs.road_state` and its callers (S14C-X17); the `moment` log type, its pin flips and the dispatch and gazette tables; S14C-X4, X6, X7, X8, X9, X13, X16, X17.
- *Done when:* on a staged armed fixture (`tests/fixtures/moments_block.json`) each letter arrives at its resolved turn when its premise holds and is `passed` when it does not; each answer applies exactly its plan on three boards; a closed Accept leaves the letter standing; lapse equals decline and writes no cooldown key; every status survives a save round trip; bands resolve (`historical` = `value`, ten seeds in band, unbanded never varies); the validator refuses each bad block; the shipped boot is **unarmed**; `BASELINE_SERIES` byte-identical with each seam's reach counted at 0; the ratchet's counts unchanged (functions over 500 lines 28, levers 231); the full suite green through the hook; `CLAUDE.md` under its cap.

**Part 2 — the client, the instruments, and three letters armed** (two landings)
- *First landing:* S14C-X1, X2, X3, X10, X11, X14, X15; the `is_moment` register, the lapse surfaces, the notice, the mailbox label, the driver dial, IQ-10 frames, parse-harness coverage. — ✅ LANDED October 22, 2026 (§14; X2 closed by ruling, §14.2; the finds X21, X22)
- *Second landing:* the shipped block with M1, M2, M4; the M1 / M2 / M4 matrix cells; the suite-reach head (§7); `tools/_s14c_series_arms.py`; the re-pin if any arm bites. — ✅ LANDED October 22, 2026 (§15; the series byte-identical, no re-pin)
- *Done when:* each letter arrives on a staged board at its resolved turn (M2 also on the `historical` passive board where Holland's loyalty dips) and is `passed(premise)` where its premise fails; each answer applies exactly its quote through `/respond_to_diplomatic_dialogue`; the Holland closure line equals `closed_ports_against` after the op (at war with Britain: unchanged, said so; at peace: −2); the Decree arrives only where `decree_clients` would be non-empty, and its line equals `terms_line` plus the admin clause and the real closure delta; every lapse surface prints a whole sentence; a standing letter's notice survives an unrelated lapse; the `iter_queue` census green; frames at 1.0 and 2.0 show both answers above the fold; the parse harness exits 0; the series byte-identical or re-pinned naming S14c.

**Part 3 — the Reich, the windows, the rest of the matrix**
- *Scope:* M3 and its Moniteur special; the M3 matrix cells (the full 12 green); R1 and R2 on staged crisis and crowd boards; clauses A–G over `SWEEP_SEEDS`; the backfill's `passed(before_save)` marks on the T10 and T20 fixtures (a causal entry included).
- *Done when:* on a staged Road I board the Confederation fulfils and the Reich letter arrives a turn later; Accept raises each vassal member's loyalty, costs Austria 15 and the alarm 3, and the special runs in the next issue; on Roads II and III it never arrives; all 12 cells pass; a staged crisis defers a letter and a crowded-out letter ends on screen; the same seed twice compares EQUAL and variance forced off compares EQUAL to `historical`.

**Part 4 — measurement, the walk, the close**
- *Scope:* the 10-seed sweep with `tests/test_moments_pacing.py`; the archived arms attributed; the VP-1 road arms re-read for M3's reach; the accept arm; the Mode C walk on `SOVEREIGN_PORT=8007`; the sibling sweep; docs (`SYSTEMS_REFERENCE.md` §147, `MODDING_FORMAT.md`, `SAVE_FORMAT_REFERENCE.md`, `ROADMAP.md`'s 8.5 rows, the S14c row text per A1, STATUS).
- *Done when:* ceilings green on every arm, floors green where moments can fire, each moment's reach reported per seed; the walk shows a letter answered and one lapsed; the census reads 0 open S14C rows.

---

## §10 Risks, re-open conditions, siblings

**Risks and re-open conditions**
- **The moments are a played-board layer:** three of four premises are false on the passive board by measurement (§1). That is the board's truth, not a defect; the floors read the commanded and road arms (§7).
- **A two-turn residence crosses an AI phase.** Arm MK counts it; a bite is attributed and re-pinned, never hidden.
- **Reachability beside a standing settlement offer** (turns 11–32 passively): Part 2's head reproduces whether a letter mounts or is one click away; the rail notice's button is the guarantee, and S14C-X14 keeps it standing.
- **A thin deck** (four letters in 44 turns) is deliberate (IGR-1). A new entry after the deploy is a scenario-file change under the validator — not owed work.

**Siblings (Rule 10)** — filed in `BUG_FIXES.md` §S14C with this record; each reproduced on a board before it is built.

| Row | Finding | Fix | Part |
|---|---|---|---|
| S14C-X1 | `get_lapsing_count` (`dialogue_manager.py`) takes no turn and counts a kept-open letter on its first turn, so the end-turn warning says a call to arms will lapse when `keeps_open` keeps it | `get_lapsing_count(current_turn)`, `keeps_open`-aware; its five `main.py` callers pass the turn | 2 |
| S14C-X2 | A standing two-turn letter (call to arms) blocks the wizard and the ledger for its whole window | One shared `blocks_wizard(letter)` predicate — or the row closes by DDB-2's ruling if the lock was intended (reproduce and read the ruling first) | 2 |
| S14C-X3 | Silent-zero blind spots: `RunCapture`'s dtype filter, `BEAT_TYPES` (`ai_v_sweep.py`), `AI_AI_LOG_TYPES` (`playtest_driver.py`), option-order answering | Fix before arming | 2 |
| S14C-X4 | An unlabelled `add_threat` source prints its raw key (`diplomatic_ledger.py`); no test catches it | A census: every `add_threat` source literal has a label | 1 |
| S14C-X6 | The calendar inverse could become a mechanic | A pin: no mechanic imports `turn_for_date` | 1 |
| S14C-X7 | 14 count-pin files flip 179 → 180; the IQ-7 provenance census needs a token | Mechanical | 1 |
| S14C-X8 | `treaty._letter_kind` reads any `context` dialogue as a treaty: `refresh_letter_verdict` erases a closed stamp, and a pair at PEACE closes its own Accept as a "downgrade" | A `moment` kind and a non-treaty registry; a census over every `proposal_type` the builders emit | 1 |
| S14C-X9 | `_extract_lapse_info` falls back to `"Unknown"`: a letter with neither source writes junk cooldown keys | Audit every `incoming_proposal` builder; guard the fallback | 1 |
| S14C-X10 | `change_vassal_autonomy` computes its figures inline; the wizard's grant-autonomy row never says the client leaves the Continental System, or which ports leave the count | One `autonomy_change_plan` read by the executor, the wizard row and the letter; the closure derived from `closed_ports_against` | 2 |
| S14C-X11 | `main.gd _on_mailbox_activate_result` has no else branch: an unknown dtype opens nothing and says nothing | Add it | 2 |
| S14C-X13 | `CLAUDE.md` sits at about 61,900 of 62,000 bytes | The new file-reference row paid for by a trim | 1 |
| S14C-X14 | The rail notice is typed `DIPLOMATIC_PROPOSAL` and dismissed wholesale (`turn_manager.py`'s lapse hook, and the answer sites) — a standing two-turn letter (call to arms today) loses its notice at the first unrelated lapse | A stable detail key; the dismissal sites spare a still-open letter | 2 |
| S14C-X15 | The lapse surfaces build "{nation}'s {type} offer lapsed unanswered" from `lapse["nation"]` (`dispatch._lapsed_offer_row`, `main.gd`, `dispatch_view.gd`) — a nation-less letter prints a broken sentence | Each surface prints the letter's own line when it carries one (the petition idiom); a census over every reader of `lapse["nation"]` | 2 |
| S14C-X16 | `WorldState.to_dict` is exactly 500 lines; one more line trips the ratchet (functions over 500: 28 / 28) | The `moments` key folds into an existing line; a done-when line pins the count | 1 |
| S14C-X17 | "Forsworn" is computed inline in at least three places (`imperial_designs.py`'s road payload and Acts rows, the dispatch, the executor) | One `road_state` reader; a census that no module re-derives it | 1 |

*Not filed, by their own evidence:* the first synthesis's X5 (a relation move announcing itself twice) did not reproduce — the answer-time delta is cleared before the morning dispatch reads it (critic probe), so no row; its X12 (the Decree's display date and no date gate) is closed by ruling (the calendar is display-only, and M4's premise reads no date).

---

## §11 Deferrals and hand-offs (Rule 9) and what is struck

| Item | Owner / landing | Completion | Test | STATUS line |
|---|---|---|---|---|
| Teaching the letter's register (S14d's row already names "an event letter") | S14d — a hand-off line written into its row with this record | the first moment letter names the mechanic when it first opens | S14d's own | "S14c landed; S14d teaches the letter" |
| The Match's keep-or-delete | S14e (three players) | kept, or its one block entry deleted with its count pin | `tests/test_moments_pacing.py` | "S14e — judge the Match" |
| The VP-1 hand-off line | closed by §3.6 and the matrix (parts 2–3) | the 12 cells pass | `tests/test_moments_the_hand_off.py` | "VP-1 §11 hand-off closed by S14c" |

**Struck from every surface, not deferred** (each with its covering surface):
- **Trafalgar's news** — `naval.fleet_action_banner` names it when it happens; a date-keyed line would assert a fight the board did not have. No re-open.
- **Ulm, Austerlitz, Pressburg, Jena, Eylau, Friedland, the principalities, Fox's death** — derived (battles, the prologue, the table, the war council, ES-7), or no choice. **The Confederation and Tilsit** — VP-1's proclamation, the Raft, the decisive peace and the Verdict (turn 44 is the Verdict's own turn).
- **Warsaw** — a peace-table `create_client` clause. **Oubril** — peace machinery owns it; the disowning is a die in a quote. **The Ottoman embassy** — its consequence is a war declaration. **Saxony at Posen** — Road I. **Ansbach** — the `agenda_violation` beat. **Finckenstein** — no Persian court.
- **The situational class (A1):** Calabria, the Tyrol, unrest — a self-healing stat, and the capture choice covers a province's fate; **the quarrel** — the marshal-petition channel; **a court's overture** — the AI ladder's asks.
- **Not built:** a beat kind and a moment headline class (no deck entry needs them), rolling-window caps and a wounded-morning rule (§4), a sustained-unrest mechanic, a standing marriage action or bond, AI-court marriages, an AI-court audience, a third answer button, the `compose_battle_name` alias, Moniteur specials for M1, M2, M4.
- **R27, R35, R133, Gneisenau, R25's quota, the Positive Events table** — Q7.

---

## §12 The critics' corrections, applied or answered

Two adversarial critics — one against the repo (probes on the booted world), one against the rules and the history — returned 30 corrections (3 blocking, 13 major, 14 minor).

| # | Severity | Correction | Disposition |
|---|---|---|---|
| R1 | blocking | The Holland letter's closure claim is false on the shipped board (Holland at war with Britain; 10 → 10) | **Applied** — the line derives from `closed_ports_against` and prints "unchanged" at zero; §1's "cost the board hides" paragraph removed; the fork restated as tribute against loyalty (§2 M2) |
| R2 / P5 | major | The Decree is inert at its window (`decree_clients` = []) | **Applied** — `law_bites` gates on a port it would shut; the quote prints the real delta; measured passed(premise) passively (§2 M4) |
| R3 / P1 | blocking | `enact_law` never spends the admin action; shown ≠ applied | **Applied** — the op is the full verb (`law_refusal`, `enact_law`, `use_admin_action`); the quote names the action; a pin on `admin_actions_remaining` |
| R4 | major | The Reich beat has no consequence and doubles `design_fulfilled` | **Applied** — the beat struck; the Reich is a letter with a durable fork (the ultimatum, §2 M3) |
| R5 / P4 | major | Holland's loyalty recovers; "drifting −2" misstates the net forecast | **Applied** — gated on loyalty ≤ 70 or a negative forecast; the decline line reads `forecast_vassal_loyalty` |
| R6 | major | The Match's Accept is dominated | **Applied** — a vassal Bavaria's loyalty +15 (durable) and a −5 slight on Decline; S14e still judges it |
| R7 / P7 | major | The lapse surfaces print a broken sentence for a nation-less letter | **Applied** — seam 6 and S14C-X15 |
| R8 / P6 | major | The wounded-morning rule reads the previous morning and is inert in every harness | **Applied** — struck (§4); R1 alone defers |
| R9 / P14 | minor | R1's tenure test is the 2-turn forewarn only; the events source unnamed | **Applied** — R1 reads "a foregrounded record exists"; the same-tick emission clause dropped |
| R10 / P8 | minor / major | The rail notice is dismissed wholesale | **Applied** — seam 7 and S14C-X14 |
| R11 | minor | The Decree's record asserts Berlin; the Reich's record a date | **Applied** — every record is past-tense history marked "historically"; the dateline is the in-game label |
| R12 | minor | Proportion: caps decorative, the brief's situational class struck | **Applied in part** — the slack caps struck; the situational strike kept with its covering surfaces and **flagged to the user as A1** |
| R13 / P15 | minor | Half-strikes (Trafalgar's re-open, the thin-deck re-open); the seam narrowing unlisted | **Applied** — both plain strikes (no owed work); A1 lists the narrowing |
| R14 | minor | M4 armed before its matrix cells | **Applied** — each moment's cells pinned in the part that arms it |
| R15 | minor | `road_state` converts one site; "forsworn" is recomputed elsewhere | **Applied** — S14C-X17 routes every site and census-pins it |
| P2 | blocking | `to_dict` is exactly 500 lines; the new field trips the ratchet | **Applied** — S14C-X16, a Part 1 done-when line |
| P3 | major | (Holland's closure — as R1) | **Applied** (R1) |
| P9 | minor | A settlement offer stands from turn 11, not 28 | **Applied** — §1 corrected; Part 2's head checks every letter's reach beside it |
| P10 | minor | The relation double-line sibling does not reproduce | **Answered** — not filed (§10) |
| P11 | minor | `get_lapsing_count` needs a turn; five callers | **Applied** — S14C-X1's fix names the signature and the callers |
| P12 | minor | Arming fires letters in every test that boots 1805 and plays past turn 17 | **Applied** — the suite-reach head (§7) |
| P13 | minor | The causal entry escapes the backfill; the Reich's record carries a date | **Applied** — §3.5 covers causal entries; R11 |

---

## §13 Part 1 — the landing record (October 22, 2026)

**✅ LANDED October 22, 2026** — the engine and its transport, UNARMED (the hand-over's scope, built straight through). Rules `SYSTEMS_REFERENCE.md` §147; rows `BUG_FIXES.md` §S14C; pins `tests/test_moments_engine.py`; the series `tools/_s14c_series_arms.py` (`_final.json`); the staged deck `tests/fixtures/moments_block.json` (the deck exactly as ruled).

### 13.1 The head, reproduced first

- **§1 on ten seeds** (the `SWEEP_SEEDS`, passive France, the series' ambient K): the historical seed reproduces §1 exactly (Holland 74 / 66 / 72 / 91 at T14 / T18 / T22 / T31; France 28 → 17 provinces by T18; the chest 8,835 / 7,690; a settlement offer current from T11; no foreground at T8, T18, T29), and the probe's threat series equals `BASELINE_SERIES[:35]`. **Bavaria** is warm in T8–12 on **0 of 10** seeds (PEACE, 0 provinces, inactive from T5 on six seeds and from T7 on four; ALLIANCE, never France's vassal — M1's loyalty arm needs a staged board); RNG-fragile, not settled — three other ambient bases make it warm on one or two of three. **Holland** slips (loyalty ≤ 70 or a negative forecast) in T17–21 on **7 of 10** (not ulm, austerlitz, friedland; the forecast clause adds no seed while Holland fights Britain). **The Decree** would shut a port on **0 of 10** in T28–32 (`decree_clients` empty, Holland a Satellite); its Accept would be closed by the authority price on marengo (from T30) and lodi (T32). **The queue:** a settlement offer stands as the current dialogue from T9 (queued) or T11 through T35 on every seed — every moment letter in M2's or M4's window mounts behind it (§10's reachability risk confirmed; part 2 owns the one-click route, S14C-X14). **The foreground:** Prussia–Hanover only, at T4–14; none inside M2's or M4's window.
- **S14C-X8 reproduced on the booted world** — a moment-shaped letter's closed Accept (`closed_clause: gold`) was erased by the first `/pending_envoy` read (`_letter_kind` → "treaty", `proposal_of` → {}, `can_sign` → ok), and the answer then reached `_handle_accept_ai_proposal`, which popped the letter as "proposal data missing". **And its second half is LIVE on shipped code:** every AI ultimatum (a PEACE pair, by its producer) had its Yield closed "We already have Peace with Prussia. A Peace treaty would be a downgrade." on the first read, and the typed Yield was refused; every offered crown (`offer_vassalage`, Sweden at PEACE) was stamped closed at build; a broker's ask was judged as a peace between the belligerents. Filed and fixed as **S14C-X18, X19, X20**.
- **S14C-X9 reproduced:** `_extract_lapse_info` read a `context.source` no builder writes; every builder sets `target_nation` (the audit: `build_ai_proposal_dialogue`, the petition, the call to arms, the ultimatum, the counter and its response), so only a court-less letter reached the fallback — and wrote `Unknown|nation` and `Unknown|moment_letter` cooldown keys. Its twins: `_make_summary` (the mailbox row's source "Unknown") and `main._build_pending_envoy_popup_from_dialogue`'s `expected_nation`.

### 13.2 Built

- **`backend/game_logic/moments.py`** — the store `world.moments` ({block, state}; `store_from_data`, one shape for the scenario key and the save; `{}` = unarmed); `PREDICATES` (`court_warm`, `vassal_slipping`, `design_fulfilled`, `law_bites`) with `PREDICATE_PARAMS` and `ANCHORS` (a causal entry's anchor); the board's derived lines; the closed `OPS` (gold, dp, relation, alarm, loyalty, autonomy, enact_law — each a plan and an apply over the shared function); `plan` (shown = applied); the windows and `road_gate`; the transport (`is_moment_letter`, `build_letter`, `refresh_letter`, `answer_verdict`, `answer`, `counter_refusal`, `keeps_open`, `lapse_default`); the tick (R1 the foreground, R2 the crowd-out receipt, R3 one a morning, `max_open`, `min_gap`); `backfill_store`.
- **The shared helpers:** `vassal.adjust_loyalty` (clamped, delivered figures; the 17 raw writes stay); `vassal.autonomy_change_plan` — the executor's figures, now read by `change_vassal_autonomy` itself and by the `autonomy` op (S14C-X10's backend half; the wizard row and the closure line stay part 2's); `war_council.record_in_tenure` / `foreground_in_tenure` (the promotion and the open-crisis slot test route through it, byte-identical); `naval.decree_clients` / `closed_ports_against` / `ports_by_court_against` gain `decree_by` (the as-if-enacted read M4's premise and quote need — the live law untouched); `calendar.turn_for_date` (validator-side only); `campaign_variance.resolve_moment_turns` (the boot's branch of `apply_scenario_variance` and the backfill's resolver, one function); `imperial_designs.road_state` and **`fulfilled_turn`** (amendment: §3.6's readers gain `fulfilled_turn` — the Reich's lag counts from a turn `is_fulfilled` cannot give).
- **`_validate_moments`** — every name the deck uses, the date against its turn, the copy limits, the pacing and op bands, windows spaced by `min_gap` and closed before the Verdict, no VP-1 source (every `alarm_source` the designs' block authors, the Acts', the decisive peace's), a labelled `moment_` source, no priced decline.
- **Serialization:** `self.moments` (init), the `to_dict` key folded onto the designs' line (S14C-X16 — 500 lines, the over-500 count 28), `from_dict`, `save_manager._backfill_moments` (the save's own seed; `passed(before_save)`).
- **The ten seams at their backend halves:** 1 `deliver_letter`; 2 `treaty.NON_TREATY_LETTERS` / `non_treaty_kind`, `_letter_kind` "moment", `can_sign`'s moment arm, `refresh_letter_verdict` accepts the kind (S14C-X8); 3 the head branches of the accept, reject and counter handlers; 4 `main._build_pending_envoy_popup_from_dialogue` and the popup hand-over; 5 `lapse_pending_offers` (`moments.keeps_open`, `lapse_default`), the lapse row's `moment` key (S14C-X9); 6 `dispatch._lapsed_offer_row` and the `offer_lapsed` one-liner print the moment's own sentence (S14C-X15's backend half; the two Godot renderers and the census stay part 2's); 7 the rail notice with the stable `moment_id` detail (S14C-X14's 18 dismissal sites stay part 2's); 8 the mailbox row (the title, "The Cabinet"), `MAILBOX_SUMMARY_LABELS` / `PROPOSAL_TYPE_DISPLAY` rows, `mailbox_priority` 2; 9 `has_current_turn_offers` skips a moment letter (S14C-X1's `get_lapsing_count` stays part 2's); 10 the AI readers find no court (pinned).
- **The log type** `moment` (arrived / answered / passed; NOTABLE; diplomacy; a stage-4 arm), the 14 count pins 179 → 180 and the IQ-7 census (S14C-X7); the dispatch's `moment_receipt` ("{line}", HIGH, `always`); Le Moniteur's `_COURT_TYPES` gains `moment` (the special waits for M3 in part 3).
- **The siblings:** S14C-X4 (every `add_threat` / `reduce_threat` source labelled — 23 rows and the `broke_<type>` family; the combat executor's alarm line routed through the one resolver), X6, X7, X8 with X18–X20, X9, X13, X16, X17 — FIXED.

### 13.3 Measured

`BASELINE_SERIES` byte-identical on every arm (0, M0, X8, ALL) with every reach counted and zero — the tick never finds an armed store, no letter is delivered, lapsed or crowded out, no non-treaty letter is read and no court-less lapse is written on the ambient series (`tools/_s14c_series_arms_final.json`); the nine commanded arms (CMD-H, CMD-A, CMD-M, OP, FLD, DL, LAW, VOLTE, FC) equal S14b part 3's measured tree record for record (`tools/_s14c_arm_attribution_final.json`); the code-health ratchet unchanged (functions over 500 lines 28, `to_dict` at 500; levers 231; silent handlers 6); the full suite green.

### 13.4 The done-when, item by item

| §9 Part 1 done-when | Landed |
|---|---|
| each letter arrives at its resolved turn when its premise holds and is `passed` when it does not | the Match at T8, Holland at T19 when she slips and not at 90, the Reich a turn after the Confederation is told, the Decree only where it would shut a port; `passed(premise)` silent, `passed(forsworn)` on another road, `passed(verdict)` at the Verdict (`TestArrival`) |
| each answer applies exactly its plan on three boards | rich and clamped (every simple op), poor (refused, nothing charged), the autonomy op equal to the executor's plan, the Decree the full verb with its admin action (`TestShownIsApplied`) |
| a closed Accept leaves the letter standing | across two `/pending_envoy` reads and the answer endpoint (`test_a_closed_accept_keeps_its_stamp_across_every_read`) |
| lapse equals decline and writes no cooldown key | through two real end turns (`test_a_real_end_turn_lapse_writes_no_cooldown_and_tells_its_own_sentence`) |
| every status survives a save round trip | `TestSaves` (every status and pass reason; the backfill at T10 and T20, a causal entry, the save's own seed, a carried store kept) |
| bands resolve | `historical` = `value`, the ten seeds in band, the band spreads, unbanded never varies, idempotent (`TestTheStore`) |
| the validator refuses each bad block | 21 refusals (`TestTheValidator`) |
| the shipped boot is unarmed | `TestUnarmed` |
| `BASELINE_SERIES` byte-identical with each seam's reach counted at 0 | §13.3 |
| the ratchet's counts unchanged | functions over 500: 28; levers: 231; silent handlers: 6; `to_dict` at 500 |
| S14C-X4, X6, X7, X8, X9, X13, X16, X17 FIXED | and the finds X18, X19, X20 |
| the full suite green through the hook | the commit |

---

## §14 Part 2, first landing — the client and the instruments (October 22, 2026)

**✅ LANDED October 22, 2026** — the client, the instruments and the part's seven siblings, with three letters still unarmed (the shipped scenario authors no `moments` block until the second landing). Rules `SYSTEMS_REFERENCE.md` §147.7–§147.9; rows `BUG_FIXES.md` §S14C; pins `tests/test_moments_transport.py`, `tests/test_moments_letters.py`, `tests/test_moments_client.py`, `tests/test_moments_pacing.py`; frames `docs/audits/IQ10_MOMENT_LETTER_{BAVARIAN_MATCH,DECREE_OF_BERLIN}{,_X2}_2026_10_22.png`.

### 14.1 Reproduced first

On the booted 1805 world with the two-turn letter that exists today — Spain's call to arms against Portugal: **X1** `get_lapsing_count()` read 1 on the call's first turn though `keeps_open` holds it; **X2** `has_current_turn_offers()` held and `get_available_diplomatic_actions(Prussia)` was empty for the call's whole window; **X14** a Swedish open-borders letter lapsed and the end-turn hook's wholesale `dismiss_by_type(DIPLOMATIC_PROPOSAL)` took Spain's notice while the call still stood. **The dismissal sites are 18, not 2** (the gate's count): the lapse hook, the call's own (dead) close and 16 in the executor. Read from the client, two finds: **X21** — the popup's route matcher compares the payload's `from_nation` with the "Not Now" key, both "" for a court-less letter, so every moment letter on a `/command` response was swallowed; **X22** — the answer's terminal lines read "Responding to 's proposal". And the driver's answerer, under `--diplomacy accept` with a closed Accept, filtered the Accept out and pressed the first enabled option — the Decline — in silence (folded into X3). The sibling sweep of X14 found **X23**: an open allegiance auction's rail row — its Bid chip, standing three turns — went at any unrelated answer or lapse (reproduced: Denmark's auction, Sweden's lapse).

### 14.2 Ruled — S14C-X2

DDB-2's ruling (`docs/audits/DD_B_RULINGS_2026_10_14.md` DDB-D8) is silent on the wizard; the lock is `DIPLOMATIC_OFFER_LIFETIME_SPEC.md`'s ("avoids the obvious exploit where the player can freeze a favorable proposal while changing the board state"), which DDB-2's two-turn `keeps_open` stretched over the call's window. **Ruled under the standing delegation: the call keeps the lock** — its hazard is concrete (a wizard act that makes the call moot — a fresh peace, a dropped alliance — dodges its refusal price, `call_status`: "Neither is priced"); **the moment letter never takes it** (the Cabinet's letter, no court to game, landed in part 1). The row closes by this ruling; the user may overrule it.

### 14.3 Built

- **S14C-X1** — `DialogueManager.item_lapses(item, current_turn)` is THE lapse predicate; `lapse_pending_offers` and `get_lapsing_count(current_turn=None)` both ask it (no turn: the old reading); the five `main.py` callers pass `int(world.current_turn)`.
- **S14C-X14** — `notifications.dismiss_letter_notices(world)`: every envoy row goes as before EXCEPT a standing letter's, keyed by `letter_notice_key` (a moment's `moment_id`, a call's `call_ally` / `call_enemy` — the call's notice now carries them, with `counterpart` so two calls from one ally keep distinct rows); all 18 sites route through it (a census pins none re-implements it); an open allegiance auction's row is kept the same way (`auction_court`, X23). A moment's notice opens its own letter in one click (`review_target` `moment_letter`, `route_id` its mailbox id → `main.gd` → `/mailbox/activate`).
- **S14C-X10** — `vassal.autonomy_change_plan` carries its consequence: the tribute in gold (`_vassal_tributable_income`, the collection's own sum) and the ports against the trade-dominant power, read through `naval.closed_ports_against(…, autonomy_as={court: level})` (the live row untouched) — "its ports stay counted — Holland is herself at war with Britain" on the boot, "its ports leave the count against Britain: 10 → 8 of 26" at peace; its `line` is the wizard row's `effect_text`, the ledger chip's `autonomy_up_line` / `autonomy_down_line` and the moment's `autonomy` quote.
- **The client** — `incoming_proposal_popup.gd`'s `is_moment` register (the header "A MOMENT OF HISTORY — {dateline}", the title and the voice, the record, the board, "What each answer does" with each quote's caption in bold, the unanswered line; no Counter; the authored captions on the buttons, the quotes in their tooltips; backend copy escaped); `main.gd` — X21 (`_proposal_dismiss_key`: a moment's id), X22 (the letter named when answered or set aside), X11 (the activate result's missing else says what it could not open and hands the terminal back), the moment row's review target, X15's renderer (a carried line prints for any letter); `dispatch_view.gd`'s twin; `mailbox_panel.gd` labels the row "Moment"; `diplomatic_ledger.gd` prints the plan's line on the autonomy chips.
- **S14C-X3** — the sweep: `MOMENT_TYPES`; letters seen by object identity (`_moment_letters`, held like REV-X1's events), never counted as a court's courting; `capture_turn` gains `moment_letters`, `moments_open`, `foreground_in_tenure`; `capture_final` the store's silent passes; `derive_metrics` the §7 metrics (`moments_arrived`, `moments_passed` by reason, `moments_lapsed`, `moments_max_per_producing_turn`, `open_letters_max`, `letters_during_foreground`, `fire_turns`); a receipt is never a soap line; arm C reports each moment per seed. The driver: `--moment accept|decline` (absent = decline, never the diplomacy dial; appended to `POLICY_FLAG_KEYS`, so every archived header is unchanged), the letter answered by its action, a closed Accept left standing with its reason, the `moment` rows and a moment's lapse printed in the campaign log, a lapsed moment's own sentence in the envoy line.
- **The copy** — the Decree's quote "…; 1 administrative action; ports shut against Britain 8 → 10 of 26."; its board "Enacted, the Decree shuts the ports of Holland too, whatever its autonomy."; the unanswered line "If unanswered by {label}: {caption} — {effect}" (the plan's `effect`, no double colon).
- **The frames** — `cap_moments` (the Match and the Decree delivered by the production tick on the staged deck, read off `GET /pending_envoy`) and two `SHOTS` rows; at Interface Scale 1.0 and 2.0 the whole letter stands above the fold, both answers' buttons and quotes and the unanswered line (the body's two blank lines removed for 2.0). The Godot parse harness EXIT 0, its staleness list gains the popup and `dispatch_view.gd`.

### 14.4 Measured

`BASELINE_SERIES` byte-identical on every arm (0, M0, X8, ALL) with every reach zero (`tools/_s14c_series_arms_final.json`); the nine commanded arms equal part 1's tree record for record (`tools/_s14c_arm_attribution_final.json`); the Godot parse harness EXIT 0; the IQ-10 frames at 1.0 and 2.0; the code-health ratchet unchanged (functions over 500 lines 28; levers 231; silent handlers 6); the full suite green.

---

## §15 Part 2, second landing — three letters armed (October 22, 2026)

**✅ LANDED October 22, 2026** — the shipped 1805 scenario carries the `moments` block with the Bavarian Match, the Throne of Holland and the Decree of Berlin, pinned equal to the staged deck's entries (the Crown of the Reich arms in part 3). Rules `SYSTEMS_REFERENCE.md` §147.10; pins `tests/test_moments_armed.py`; the series `tools/_s14c_series_arms.py` (MW, ML, MK, MN, MH, MR added); the commanded arms `tools/_s14c_arm_attribution_final.json`.

### 15.1 The suite-reach head, first

The block armed on a scratch tree (`git archive` of the first landing's commit), the full suite run there: three tests reacted — `tests/test_moments_engine.py`'s unarmed pins, which asserted the shipped scenario authored no block; **re-seated consciously** on a world with no block (the bare flag world) and a pin that the boot arms exactly part 2's three. No test reading the dialogue queue, the mailbox counts, `lapsed_offers`, the `offer_lapsed` rows or the Gazette past turn 17 moved, so no conftest dormancy pin is needed (the choice recorded). The scratch tree's other fourteen failures and its 444 errors were its own (Godot-driven harnesses with no import cache, untracked art, no `.git`).

### 15.2 Shipped and pinned

- **The block:** `europe_1805.json` gains `_moments_comment` and `moments` (owner France, pacing one open letter and a 3-turn gap, the three entries byte-for-byte the fixture's); the validator passes it; the boot resolves 8, 18, 29 on `historical`.
- **The matrix:** M1 and M2 ride every road; M4 rides no road and Road III, and is `passed(forsworn)` on Roads I and II (the Reich's three cells are part 3's).
- **Holland through the endpoint:** at peace with Britain and slipping, "Crown Louis" applies exactly its quote — Autonomous, the plan's loyalty, and `closed_ports_against` after the op equal to the quote's `ports_after`.
- **The passive `historical` board** (the series' own loop, 31 end turns): the Match `passed(premise)` (Bavaria gone), the Decree `passed(premise)` (no port to shut), the Throne of Holland delivered on turn 18 where her loyalty dips, kept across one AI phase behind the standing settlement offer, lapsed at the end of turn 19 as its empty decline with no nation and no cooldown key.
- **The backfill:** the archived `fixture_t10_ambient` (turn 10) and `fixture_t20_ambient` (turn 20) saves, written before S14c, load armed — the Match (and, at turn 20, Holland) `passed(before_save)` on the save turn; nothing fires retroactively.

### 15.3 Measured

`BASELINE_SERIES` byte-identical on every arm (0, M0, X8, MW, ML, MK, MN, MH, MR, ALL) — now with real reach: the armed store ticks 40 times, the Throne of Holland is delivered once (turn 18), kept across one AI phase, lapses once as its empty decline (one court-less lapse, no cooldown key), one row; the Match and the Decree pass on their false premises; nothing reaches the threat series (`tools/_s14c_series_arms_final.json`). Of the nine commanded arms, seven meet the Bavarian Match (turn 8; turn 10 on austerlitz, its band) and five the Throne of Holland, none the Decree; the driver declines each, and the Match's decline (Bavaria −5) parts CMD-A's game stream at turn 31 (the chest −18) and CMD-M's at turn 29 (−50) — the other arms part only by the letters' own rows; with the tick held down CMD-A, CMD-M and CMD-H equal the first landing's tree record for record (`tools/_s14c_arm_attribution_final.json`). The suite-reach head: on a scratch tree armed with the block, three tests reacted — the engine's unarmed pins, re-seated consciously on a world with no block — and no reader of the queue, the mailbox counts, the lapse rows or the Gazette moved (the other fourteen failures were a scratch tree's own: no Godot import cache, no untracked art, no .git).
