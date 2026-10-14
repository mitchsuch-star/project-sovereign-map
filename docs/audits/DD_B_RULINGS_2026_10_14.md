# DD-B — the design rulings (October 14, 2026, after the S13 close)

*The user's delegation: "make design calls please do research and assure the plan has all errors fixed in coming
sessions and any similar errors they find while working." This memo rules the nine design questions DD-B filed
(`DESIGN_REFINEMENT.md` §DD-B, DDB-D1 … D9) and SFR-B3, the one open defect the plan had homed after the deploy.
It records the research behind each call. The guarantee that every error is fixed before the deploy is §4.*

**Method.**
- **The code.** Four read-only research passes traced each question: the mechanic (file:line), every spec
  sentence and ruling that shaped it (with dates), what the AI does on the same road (Golden Rule 5), what a
  change would touch (tests, byte-pinned series), and how often it bit in DD-B's 1,075 actions.
- **History and comparable games.** Precedent was weighed alongside the code (sources at the end).
- **What is re-opened.** Every earlier ruling a call re-opens is named. Only one was the user's own words (D2);
  the rest were taken under delegation, or are specs the code never built.

## 1. The rulings at a glance

| Row | Ruling | Re-opens | Build row · lands | Scope |
|---|---|---|---|---|
| DDB-D1 | **Ask** before an out-of-reach attack becomes a pursuit | NPC-D4's disclose-only answer (delegate, Oct 2) | DDB-R1 · S13b part 3 | ≈ 0.3 |
| DDB-D2 | **Widen the muster gate to "potential disaster" for any personality, and teach the free preview** | **the user's own CA9-D2 (Aug 9)**, on its own stated condition | DDB-R2 · S13b part 3 | ≈ 0.6 |
| DDB-D3 | **Build FA-D28's open half for detachments:** at ≥ 4:1 an assault takes a detachment whole | nothing (completes FA-D28) | DDB-R3 · S13b part 3 | ≈ 0.6 |
| DDB-D4 | **No auto-end on either pool:** the player ends the turn | AAR-12's scope and §6 row 21(b) (delegate; row 21(b)'s re-open condition met) | DDB-R4 · S13b part 3 | ≈ 0.75 |
| DDB-D5 | **Refuse at no cost, naming both roads** | CN-2 (delegate; its own pre-stated branch) | DDB-R5 · S13b part 3 | ≈ 0.25 |
| DDB-D6 | **Keep the rule; the refusal names the retreat** | nothing | DDB-R6 · S13b part 3 | ≈ 0.15 |
| DDB-D7 | **Keep the rich peace; surface its sink (the laws)** | nothing (SRX-D1 and the user's ES-4 strike stand) | DDB-R7 · S13b part 3 | ≈ 0.25 |
| DDB-D8 | **France is asked** to join an ally's offensive war; a non-leader may make a priced bilateral peace | nothing (builds DG-4's player half, Apr 17) | with DDB-2 · S13b part 1 | ≈ 1.25 |
| DDB-D9 | **A truce pauses the shared war** for a contingent | nothing (a case the VD-C gate never weighed) | with DDB-3 · S13b part 1 | ≈ 0.6 |
| SFR-B3 | **Europe waits on Paris;** the signing spends the alarm to the watch; the page names it | nothing (no gate ever ruled the aftermath) | S14 head (SF-RR7) | ≈ 0.5 |

**What adds scope** (each can be reversed by saying so):
- the muster gate's wider arming (D2);
- the one-assault detachment rule (D3);
- the turn that waits for End Turn (D4);
- the call-to-arms letter and the non-leader exit (D8);
- the truce rule for contingents (D9);
- the Congress hold (SFR-B3).

The rest are text, or refusals that spend nothing.

## 2. Each ruling, with its research

### DDB-D1 — an out-of-reach attack becomes a pursuit → **ask first**

**The code.** `_attack_range_check` (`combat_executor.py:6772-6926`) upgrades a player's attack on a marshal out
of range into a strategic PURSUE: 2 AP, or 1 for a literal marshal or the sovereign. It calls the strategic
executor directly at ambiguity 15, so no clarification gate runs, and the first march goes at once
(`strategic_executor.py:627-630`). Since NPC-D4 (built October 2) the reply states the pursuit's terms. The AI
never reaches it: the player-nation guard sends AI marshals to the "cannot reach" refusal.

**The record.**
- The upgrade was added January 31, 2026: "player nation only".
- Its 2 AP price closed an exploit.
- NPC-D4 answered "disclose" rather than "consent"; that was a delegate ruling. No ruling of the user's says
  never ask.

**The evidence.** Two upgrades occurred in 1,075 actions; one was filed. Conquest #13: Ney marched alone into
Saxony on a line the player read as an attack.

**The precedent in the game itself.** A literal marshal's bare attack on a distant foe already asks: "Kutuzov is
N regions away, Sire. Shall I pursue?" (`combat_executor.py:6530-6572`). The judge already reads "Shall I" as
ASKED (read right).

**Ruling.**
- **What the ask says.** An attack on a marshal out of reach asks first, at no cost: "Kutuzov stands at Moravia,
  two marches off. Pursue him (2 AP — a standing order; the first march takes him to Dresden, Saxony's soil),
  or cancel?"
- **Answering.** Yes reissues the pursuit with NPC-D4's terms. Typed yes / pursue / no / cancel answer it
  (CR-2's grammar).
- **Which roads ask.** Typed player orders only. The post-objection road, `take <foe>` and strategic execution
  keep today's upgrade. The AI is untouched, so BASELINE_SERIES and M1–M7 stay byte-identical by construction.

### DDB-D2 — the muster as a preview → **widen the gate to "potential disaster", and teach the free preview**

**The code.**
- **The gate.** It is `objection_v2.muster_gate_arms` (`objection_v2.py:1243-1266`: band `unfavorable` AND
  personality `cautious`), read at `combat_executor.py:7449-7458`.
- **The pause already exists.** It is a free Commit / Cancel interrupt (`muster_confirm`, 7478-7511; answered
  by button or typed text), so only the arming condition is in question.
- **A free preview exists, untaught.** "what if Ney attacks Mack" (`question_desk.py:1497-1590`) returns the
  attack's own muster and says "Nothing has been ordered, and nothing spent". No help line teaches it. The
  tutor's card says "Read the MUSTER before every battle", which is impossible today for a non-cautious attack.
- **The AI shares the gate's constants.** `enemy_ai.AI_ATTACKS_OBEY_THE_MUSTER_GATE` (`enemy_ai.py:192-198`)
  reads `MUSTER_GATE_BAND`, and the glory hunt reads it too (`jealousy.py:243-267`). Editing those constants
  would move the AI and the series.

**The record.**
- EXP-C1 (July 10) proposed exactly this: confirm or cancel before any attack.
- W6-4 narrowed it to unfavourable or even odds.
- CR-6 (b)/(d), the user's (July 16): silent on favourable odds.
- **CA9 row 2, the user's own words (August 9):** *"only show popup if they are entering potential disaster and
  general is cautious."* Its record warned: "a non-cautious marshal walking into an unfavorable fight now gets no
  warning at all … it should be checked in play" and "The playtest still owns the feel question."
- WO_EVAL (August 17): do not widen "without re-opening the ruling explicitly".
- NAPOLEON_SPEC §15.9a: the sovereign gets NO CONFIRM.

**The evidence (the playtest CA9 asked for).**
- 28 player attacks were mustered across the three roads. The gate fired once.
- Of the six sightings, three were non-cautious leads walking into unfavourable odds unwarned (Massena twice,
  Lannes). The other three were favourable attacks with a corps left out.
- Every player named the muster among their three biggest confusions.

**Comparable games.** Total War's attack prompt lists the armies that will reinforce before the battle is
fought.

**Ruling.** This re-opens the user's CA9-D2, on its own stated condition.
- **The gate.**
  - It arms on an UNFAVOURABLE band for ANY personality. The user's test, "entering potential disaster", is
    kept; the "and cautious" clause, which the playtest refuted, is dropped.
  - A favourable attack still fires at once (CR-6 (b)/(d) kept).
  - The sovereign keeps NO CONFIRM.
- **How it is built.**
  - It is a new player-only predicate at the gate site. `MUSTER_GATE_BAND` and `MUSTER_GATE_PERSONALITIES` are
    untouched, so the AI and every series hold.
  - A non-cautious marshal does not hesitate. Berthier names the band instead ("the band reads unfavourable —
    Commit or Cancel").
  - The commit's re-issue is exempt from a second objection draw (`executor.py:2284-2296` has no
    `_muster_confirmed` exemption today). The decision is one decision, and the seeded stream draws once.
- **The free preview is taught.**
  - Every muster that rides a result ends with: "Ask 'what if Ney attacks Mack' to read the muster before you
    commit — it costs nothing."
  - The help's battle section and the tutor's muster card name it, so the card's sentence becomes true.
- **Not taken.** An always-preview setting (≈ 0.5 more), and the favourable-but-incomplete arming (about half
  of all attacks would pause).

### DDB-D3 — each assault only halves a garrison → **at ≥ 4:1 an assault takes a detachment whole**

**The code.**
- `garrison_exchange` (`combat_executor.py:4908-4930`, one copy for both boards and the desk's forecast) caps the
  garrison's loss at 0.50 a fight. The cap binds from about 1.43:1, so above that the odds do not matter.
- A detachment under 500 lays down its arms (SR-7a). A capital breaks under 5,000.
- The AI's rung P4.25 never reads the cost, so its decisions are unchanged; its outcomes speed up.

**The record.**
- FA-D28 (ruled and built September 5) took "the LOSS half of the fix shape and not the odds-scaling half".
- "⚠ The ASSAULT-COUNT half stays OPEN on this row." That half was archived with Q3 and never re-homed.
- Its fix shape was "≥ 4:1 → the detachment falls in one assault; the 0.50 cap keeps only for a capital's own
  garrison".

**The evidence.**
- Silesia, a 3,000 detachment assaulted at about 9.6:1, took four actions to fall (3,000 → 1,500 → 750 → 375).
- Posen at 5.4:1 took four as well.
- Vienna's assaults ran 1.0–2.7:1 and would not change. All the value is in detachments.

**History.** Memmingen and Ulm capitulated to overwhelming force in October 1805. Napoleon held up Memmingen's
capitulation as the model for Ulm's.

**Ruling.**
- **The new arm.** At ≥ 4:1 effective odds an assault takes a detachment whole: it capitulates.
- **What is unchanged.**
  - Below 4:1, today's capped exchange stands.
  - A capital's own garrison and a DEF-6 depot keep the 0.50 cap.
- **One arithmetic for both boards (Golden Rule 5).**
- **The seam fix.** A one-blow collapse emits its garrison event; repro K2 found this red.
- **BASELINE_SERIES.** It is re-measured with an attribution arm (the `tools/_step3_series_arms.py` idiom) and
  re-pinned with this row named.
- **The copy.** It names the thresholds (DDB-X2).

### DDB-D4 — the turn ends itself → **no auto-end on either pool**

**The code.**
- `use_action` sets `should_end_turn` when both pools are empty (`world_state.py:11162-11164`). Only the military
  path reads it (`executor.py:3624-3637`), which runs a ~245-line end-turn mirror (`:3639-3884`).
- The admin path never auto-ends (AAR-12).
- The defer (`_auto_end_turn_defer_notice`) checks the capture question and live offers, but not last stands
  (spotted September 4, never filed).
- The client's gate guards envoys and last stands, but only on its own End Turn.
- The AI never auto-ends.

**The record.**
- AAR-12 (September 26) left the military road auto-advancing, with no stated reason. The client comment's
  reason, that the enemy phase must never be skipped, is an old bug an explicit `end turn` never had.
- **§6 row 21(b) (October 4, delegate)** ruled "no modal before an order", with a pre-stated re-open condition:
  "if a played session shows a turn ended by surprise despite the line — then a confirm on the order that will
  end it."

**The evidence.**
- Six auto-advances: conquest 1, sea 5.
- Conquest #27 ended a turn by surprise although the warning line printed. Row 21(b)'s condition is met.

**Ruling.**
- **No auto-end on either pool.** The last order's receipt carries AAR-12's "the last order of the day". The End
  Turn button turns gold, and the player ends the turn.
- **Why not row 21(b)'s remedy.** A confirm on the last order is not taken: a modal on the commonest click taxes
  every turn, whereas no-auto-end costs one press, only on a fully spent turn.
- **What it retires.**
  - the end-turn mirror;
  - WO-22's defer and its missed last-stand case: the client's one gate then guards every end turn;
  - the unread `should_end_turn` keys (`diplomatic_executor.py:5528-5536`, `economy_executor.py:1969-1970`);
  - the `AUTO_END_WARNING` copy.
- **Saves.** The save's `auto_advanced_to_turn` stays readable.
- **Series.** The AI is untouched; BASELINE_SERIES and M1–M7 stay byte-identical. About 15 tests are re-seated.

### DDB-D5 — a named marshal's arm overrides the arm asked for → **refuse at no cost, naming both roads**

**The code.** A named marshal always raises his own arm (`economy_executor.py:1449-1454`). The asked-for arm is
noted after the gold and the admin action are spent (`:1629-1635`). Every AI recruit names its marshal and passes
no arm (census-pinned), so a change is player-only.

**The record.**
- PF-7 (July 15): "surface or reject — never honor an arbitrary arm".
- **CN-2 (September 22, delegate)** pre-stated its own re-open branch: "if the user would rather the named
  mismatch refuse (spending nothing) than surface, that is one branch in `_execute_recruit`".
- SFR-D41 (October 10): "disclosed or refused, never silent".

**The evidence.** Conquest #32: 518g and the last admin action bought 10,000 infantry when artillery was asked for.

**Ruling.**
- "recruit artillery for Augereau" spends nothing and answers: "Augereau commands infantry — 'Augereau, recruit'
  raises foot for him; guns are raised by an artillery corps — <the nearest gun marshal in reach, or 'commission
  Marmont (4,500g)'>."
- PF-7's soft-correction pin flips consciously, as CN-2 named.

### DDB-D6 — an engaged marshal cannot fall back onto an ally's province → **keep the rule, fix the sentence**

**The code.**
- **The move rule.** `move_refusal_probe` (`movement_executor.py:364-407`), shared by player and AI, lets an
  engaged marshal move only onto his own nation's soil.
- **The retreat already allows it.** The `retreat` verb falls back onto ally and vassal soil
  (`retreat_soil_is_friendly`, AAR-D4 / SR-7c, October 2): free, with an effectiveness penalty, once a turn.
- **The refusal is wrong.** NPC-13's sentence, landed the same day with the old own-soil list, says "he must
  fight or stand" when `retreat to Swabia` would have worked.
- **The AI never moves while engaged.** It retreats, already onto allied soil.

**The record.** Since January 23 the rule has read "retreat to friendly only". No ruling says an engaged marshal
may not withdraw onto ally soil; it is withdrawal by `move`, free of the retreat's price, that would be new.

**Ruling.**
- The rule stands: engaged means fight, stand or retreat. A free disengage by `move` would undercut the retreat's
  price and the AI's engagement rung.
- The refusal builds its friendly list with `retreat_soil_is_friendly`, says "withdraw", and names the order and
  its price: "'Davout, retreat to Swabia' — free, −X% effectiveness, once a turn".
- It is display only; no series moves.
- **Its sibling, found while ruling:** the AI's retreat finder's first tier reads own soil only, not AAR-D4's set
  (DDB-X3).

### DDB-D7 — gold piles up on the peace road → **keep the rich peace; surface its sink**

**The code.**
- **The sinks exist.** France's law deck costs about 15,500g up front and 1,050g a turn; there are also
  substitutes, commissions, buildings, ships, buy-offs (every buyable design in Europe totals 4,824g),
  sponsorships, vassal investment, auction bids, and the Congress sweetener (sitting only).
- **The diplomacy player never opened LAWS:** 0 enact orders. The conquest and sea players found it.

**The record.**
- The user, August 7: "economy shouldn't go crazy unless you are doing very well and stable".
- IQ-1 §0.2: "the defect is not the size of the pile but that no decision touches it".
- SR-D1's laws with upkeep are "the economy's peacetime sink".
- **The user struck ES-4 on September 28:** "the peacetime sink it was held for now exists". Its re-open
  condition, "with the laws in force", is not met here, since none were.
- SRX-D1 (delegate): "a golden peace may grow rich".
- SF-ECON-1 "Acts of the Empire" stays behind its own gate (economy C6 reads ✓).

**Ruling.**
- At peace, with a chest above the next law's price, `what can I do` names the first unenacted law the chest can
  buy.
- The morning dispatch's treasury line names it once a turn ("the chest could found the Grand Quartier —
  9,000g").
- It is player-only text; no series moves.
- **Not taken:** the historically fuller Acts of the Empire, which stays on its gate.

### DDB-D8 — an ally's offensive war carries France in → **France is asked**

**The code.**
- **The offensive cascade.** `diplomacy.py:9795-9976` decides for France through `_resolve_offensive_call_path`
  (8817-8839), which never checks for the player: "honored". The override that could refuse is test-only.
- **What follows.** The Congress then charges France for drawing the sword (`game_end.player_drew_the_sword`),
  and as a non-leader France is refused settlement (`not_side_leader`).
- **The refusal machinery exists but never runs for France.** `emit_call_to_arms_refused_offensive` costs
  reliability −6, one betrayal strike and −2 with each witness; it is dead in production for France.
- **An AI ally called by France does choose,** by `compute_war_entry_score`.

**The record. Every spec asks for the choice; the code never built the player's half.**
- DG-4 (April 17): "Player/AI choice: honor or refuse".
- WAR_BARGAIN_SPEC (April 16): "Replace silent offensive cascade with a player-visible ally-entry decision".
- DIPLOMACY_SPEC §5a.
- AI_INTENT §17 (July 24): "the player is never auto-conscripted".
- BILATERAL_PEACE_HARDENING: "The player should be able to make politically costly decisions knowingly".

**Comparable games and history.**
- In EU4 an ally may refuse an offensive call, at a cost in trust and prestige; defensive calls are expected.
- Russia, bound by Tilsit, joined France's 1809 war against Austria reluctantly and only nominally.

**Ruling.**
- **The letter.** For the player as callee, an ally's OFFENSIVE war no longer carries France in. It posts a letter
  on the incoming-proposal transport (the broker idiom): "Prussia calls on her ally to join her war on Hanover".
- **The answers.**
  - **Join** attaches France to the ally's war instance (`note_joined`, the war-entry bargains).
  - **Refuse** emits the existing offensive-refusal episode (≈ −5 reliability against a minor court).
  - **Unanswered** for two turns (`GUARANTEE_GRACE_TURNS`), it is a refusal at the same price, and the letter
    says so up front.
- **The exit.** A court France joined at an ally's call may be offered a bilateral peace: the paradox HARD_STOP
  is lifted for that pair, and the existing separate-peace penalty prices it.
- **Unchanged.**
  - An AI ally of an AI aggressor keeps the DG-4 seam's resolver.
  - The defensive call (DG-4: expected).
- **Not taken:** the historically fuller "join in name only" (Russia, 1809).
- **BASELINE_SERIES.** France's boot allies' design wars no longer cascade the passive France in. The series is
  re-measured with an attribution arm and re-pinned with this row named.

### DDB-D9 — a contingent leaves its post when the war only pauses → **a truce pauses the shared war**

**The code.**
- `shared_enemies` counts WAR only (`contingent.py:118-124`).
- SR-1b moves a client's war into its lord's truce, so a truce empties the shared set, and the contingent turns
  for home (`:798-809`).
- The Road Home then strands any corps outside the home zone during a truce (`withdrawal.py`).

**The record.**
- The VD-C gate (October 3) never weighed the lord's truce; its R8 "armistice exit" means the satellite's own
  independence.
- Everywhere else the war family reads a truce as a pause:
  - RS-2: "a truce is not the war's end";
  - PT-J1: "Pläswitz 1813 paused the whole coalition war";
  - PT-J2: captures and blood are not amnestied;
  - DD1-5: the war instance is suspended, not resolved;
  - the settlement spec §7.3.

**Ruling.**
- **The truce rule.** For a contingent's purposes, a pair in ARMISTICE is still the war it shares; the raise stays
  WAR-only. Dumonceau holds Ulster through Britain's truce. A peace, or the eight homeward turns, releases him.
- **The Road Home.** A serving contingent is exempt from its issuance and judging during its lord's truce, or
  Ulster's garrison would be marched to Normandy or interned instead.
- **Every lord, player or AI** (Golden Rule 5).
- **DDB-3's legibility half adapts.** The PEACE preview names the contingents a peace releases, and the withdrawal
  message recognises a contingent's march home.

### SFR-B3 — the Imperial Peace and a league on the same morning → **Europe waits on Paris**

**The code.**
- The signing (`congress._proclaim`, `congress.py:2202-2247`) touches neither the alarm nor any brew, while a
  dissolution adds +15.
- The coalition tick runs inside the turn's advance (`world_state.py:11576`), before the Congress's own tick
  (`turn_manager.py:670`). So a brew that started at the normal gate declares on the signing's morning.
- The Congress spares only the four great powers, and only while it sits.

**The record.** No gate ever ruled the Imperial Peace's aftermath. The specs cite "a peace buys time, not
immunity" (Pressburg). The row is P2, filed October 5 and homed to ROADMAP 13, after the deploy.

**Ruling.**
- **The hold.** While the Congress sits and fewer than two great powers refuse it, no new league declares against
  France: a brew's countdown holds at its last turn. The lowered gate for two refusers is untouched.
- **The signing** spends Europe's alarm to the Armed Peace watch (45) and dismisses any brew.
- **The page** names what the peace buys: the great powers' signatures, not the lesser courts' grievances ("a
  peace buys time, not immunity").
- **Series.** It is gated on a sitting or signed Congress, so BASELINE_SERIES and M1–M7 stay byte-identical; a
  lever on the new rule gives the dormancy proof (DDB-X4).
- **Not taken:** the historically fuller "minor courts sign with their patron". Tilsit bound Russia to bring
  Sweden in, but that is a rule change to §2.3's four courts.
- **Landing:** S14's head, as SF-RR7 "the morning of the peace".

## 3. Found while ruling — the siblings (`BUG_FIXES.md` §DD-B, found-while-ruling table)

- **DDB-X1.** A naval landing on a detachment under 500 fights it instead of taking its surrender.
  `naval_executor.py:534-540` re-implements "garrison fights" without SR-7a's floor, against "ONE predicate, both
  boards".
- **DDB-X2.** The garrison copy says "a detachment fights to the last man" although under 500 it lays down its
  arms (`garrison_report.py:113-118`, `:186-187`; the works-halt line).
- **DDB-X3.** The AI's retreat finder's first tier reads own soil only, not AAR-D4's ally and vassal set
  (`enemy_ai.py:5699-5762`). This is a Golden Rule 5 drift.
- **DDB-X4.** `tools/_ge3_series_arms.py` flips levers that no longer exist in `congress.py`, so its dormancy arms
  flip nothing.

## 4. The guarantee: every error fixed before the deploy

1. **Every open row has a session.** At this ruling the ledgers hold 139 open rows, every one with a scheduled
   home:
   - the DD-B rows → S13b;
   - the Score Finish residue (SFR, EG, EA rows, UXR3-F11) → S14, which also takes SFR-B3, re-homed from
     ROADMAP 13 by this ruling;
   - the user's UXR-4 marks (UXR3-2, 24, 29, 41, 79 … 81) → S15's head.
2. **The sibling sweep** (plan-wide from S13b on). Every fix ends with a search for its class: the same mechanism
   on the other courts, dialogues, popups and roads, and the AI's side of the same executor.
   - Each sibling found is filed as a found row with its tag and fixed in the same slice, with its own test.
   - A sibling too large for the slice heads the next part. Nothing found is ever homed after the deploy.
3. **The re-measure.** Fresh players re-play the three roads. Its new rows are filed by DD-B's rule. If the done-when
   is not met, they become a fix row sized at that close, before the deploy. *(Moved the same day, after the user
   brought VP-1, the events and the table lesson before the deploy: the re-measure is **S14e**, after them, so it
   reads the game Round 0 will meet, and its rows become **S14f** before S15 — `PRE_DEPLOY_PLAN.md` §2.)*
4. **The deploy gate.** S15's release build does not start while any defect row is OPEN. The UXR-4 marks are read
   and fixed at S15's head, before the build.

## 5. Brought before the deploy (the same day)

After an inventory of everything scheduled after the deploy, weighed against the fresh-eyes evidence, the user ruled ("add events to plan as well and update doc i agree with rest make sure everything reflects future plans"):

| Item | From | Now |
|---|---|---|
| **VP-1 "The Emperor's Designs"** — France's own objectives and a decisive-peace triumph; absorbs WO-D4(b) and SF-ECON-1 | ROADMAP 12 | Pre-Deploy **S14b** (gate + build, ≈ 3.0) |
| **Events and historical moments** — the engine and a first 1805–07 deck; the Diplomacy & Flavor Content Menu picked at its gate | ROADMAP §8.5, the August 3 cut list | Pre-Deploy **S14c** (gate + build, ≈ 4.0) |
| **The table lesson** — R159 (screens name their mechanic) and the School's second lesson | 8.EVAL's Pre-EA Onboarding pass | Pre-Deploy **S14d** (≈ 1.5) |
| **DW-2** — the bilateral scorer's victory weight | 8.EVAL's Pre-EA Balance pass | **DDB-X5**, S13b part 1 |
| **The naval rail alerts** | `NAVAL_SPEC.md` §17.3 / §18.4 | **DDB-X6**, S13b part 4 |
| **Code signing** | ROADMAP 16 | Pre-Deploy **S15** (the user's certificate owed before it) |

DD-B's re-measure moved after them (**S14e**, its rows **S14f**), so it reads the game Round 0 will meet. The plan grows to about 31–32 sessions before the deploy. Everything else after the deploy has its home in `ROADMAP.md` §"Where the future work lives" (reconciled the same day: the road to EA, content update 1 — the LLM narration bundle and DEF-15 — content update 2 — Seasons — and the later ideas, each behind its own gate).

## Sources

- EU4 calls to arms (community discussions): [Steam 1](https://steamcommunity.com/app/236850/discussions/0/135514889557914264), [Steam 2](https://steamcommunity.com/app/236850/discussions/0/4424310987155046567), [Steam 3](https://steamcommunity.com/app/236850/discussions/0/3765608282432387830)
- EU4 sieges (community): [Paradox forum, deepening the siege mechanic](https://admin-forum.paradoxplaza.com/forum/threads/deepening-the-siege-mechanic.1294532), [Steam](https://steamcommunity.com/app/236850/discussions/0/541907867771987233)
- Total War battle interface: [Total War manual — the battle interface](https://r2encv2.totalwar.com/en/manual/single-player/0092_enc_page_battle_play_interface/index.html), [Warhammer forum on reinforcement prompts](https://steamcommunity.com/app/364360/discussions/3/1728711392747829714)
- Russia's 1809 participation: [Lukashevich, "Unreliable ally" (BSU, 2021)](https://journals.bsu.by/index.php/history/en/article/view/3403), [Treaties of Tilsit](https://en.wikipedia.org/wiki/Treaties_of_Tilsit)
- Ulm and Memmingen, 1805: [Napoleon & Empire — Ulm](https://www.napoleon-empire.org/en/battles/ulm.php), [Savary's memoir](https://www.wtj.com/archives/savary/sav010213.htm)
- The 1813 truce: [Truce of Pläswitz](https://en.wikipedia.org/wiki/Truce_of_Pl%C3%A4switz), [History of War — Armistice of Pleischwitz](https://www.historyofwar.org/articles/armistice_pleischwitz.html)
