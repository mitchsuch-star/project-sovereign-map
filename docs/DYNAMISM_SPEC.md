# DYNAMISM_SPEC.md — The Concert and the Awakening (v0.1, November 7, 2026)

> **The owning spec of the dynamism arc** — the restructure of `PRE_DEPLOY_PLAN.md` §2 row
> S15-R's Tiers 1–8, all pre-deploy since Q1's reversal (§0; Tier 7 gated), authored
> November 7, 2026 in Plan Mode
> (the user's plan file `floating-spinning-cat.md`). ROUTING stays with the plan row and
> `docs/STATUS.md` ▶ NEXT UP; this spec owns the design contracts, the gate record, the
> numbers and the slices. Tier 0 (the review's defects, T0-E…T0-I) is untouched by this
> restructure and keeps its own briefs.
>
> **The user's words, verbatim.** November 6: *"i want the game to be dyanamic are you
> saying its determinsitic?"*, then *"do tiered implementation of all of these make this
> happen after the bugs fixes all these"*. November 7: *"think of ways to make this even
> more interesting like how does eu4 make it so cool maps arise etc but the actors still
> play their roles etc. sometimes even minor powers get big in eu4"*, then *"rereturucture
> plan r making game more dyanmic perhaps we incoporate rising nationalism too and dont
> make rivals an exact copy of euiv? but soemthing for the era other ideas are good too
> make this good and have its own idea and implemntation even with its inpiriations"*.
> Later November 7, reversing Q1's deploy cut: *"we should stop being afraid of adding
> conent to rush deploy cuts keep happening without my consent"* (§0 — the reversal and
> the standing rule on cuts).

---

## §0 The gate record

**Q1 — the deploy cut: ✅ RULED November 7, 2026 ("After the Questions").** S15 deploys
after Tier 5. The Awakening (Tier 6) is the FIRST post-deploy arc, with its own measure
chain; Crowns & Recognition follows it. Nothing of Tiers 6+ is player-promised before it
lands (Rule 9: the rows below are the owners).

**Q1 REVERSED the same day — November 7, 2026, by the user's word, verbatim: "we should
stop being afraid of adding conent to rush deploy cuts keep happening without my
consent".** The ruling above is kept as history and stands SUPERSEDED. S15 deploys after
Tier 8: the Awakening (Tier 6) and Crowns & Recognition (Tier 8) ship BEFORE the deploy,
each with its measure chain, and Rule 9's ownership is unchanged (the §8 rows). The
build order: Tier 0's remainder (T0-I) → 1 the seed → 2 Europe varies + the casting →
3 the strategist → 4 the Alarm + promotion's teeth → 5 the Questions → 6 THE AWAKENING
(DY-4/DY-5) → 8 CROWNS & RECOGNITION (DY-6/DY-7) → Tier 7's bounded timing dice only if
the story-class count still falls short at the gate → S15 THE DEPLOY. Sizing, stated
once as information and not to be re-litigated: the pre-deploy runway is roughly 17–19
sessions (T0-I ≈ 1 · Tier 1 ≈ 0.5 · Tier 2 ≈ 3 · Tier 3 ≈ 4 · Tier 4 ≈ 2 · Tier 5 ≈ 2 ·
Tier 6 ≈ 3–4 · Tier 8 ≈ 4) plus S15's own day. *(Re-cut November 9, 2026 by the user's own word — §2b: the same content in fewer, larger sessions.)*

**The standing rule on cuts (November 7, 2026).** Player-facing content is never
deferred, cut, or moved post-deploy to protect a deploy date without the user's explicit
word on that specific item; the date yields to the content, never the reverse. Sizing is
stated as information, never as pressure. A scope fork is presented with the
content-first option co-equal and no speed option pre-recommended. Rule 9 still applies
to every piece added — owner row, landing slice, done-when, test: the rule bars silent
cuts, not discipline. Any future proposal to defer ANY DY slice goes to the user as an
explicit question with no default. ([[feedback-no-cuts-without-consent]])

**The Tier-2 gate is RULED (November 8, 2026)** — the band catalog and the story class
live in `AI_INTENT_SPEC.md` §3.8.2 (authored at the tier's head in Plan Mode, the plan
approved by the user); DY-0's baseline `tools/_dy_signature_baseline.json`.

**Q2–Q6 stand with defaults** — each is put to the user at its owning tier's head (the
Plan Mode gate the plan row already requires), and each is one line to reverse:

| # | Question | Default | Owner tier |
|---|---|---|---|
| Q2 | The Awakening's grain | **Per-court scalar**, regional expression derived (a per-region store costs save size and Rule 8 care for no v1 behavior the scalar cannot express) | Tier 6 (DY-4) |
| Q3 | Does the ulcer bleed France too? | **Yes** — Spain is the point: the player feels the mechanic they inflict (an AI-only ulcer would be a rule the player reads about but never meets) | Tier 6 (DY-4) |
| Q4 | The Questions list | **Four** (German, Italian, Eastern, Polish); the Maritime Question stays folded into the blockade/CS machinery `NAVAL_SPEC.md` already owns | Tier 5 (DY-2) |
| Q5 | Promotion: teeth at once? | **Yes** — force-limit tier, call-to-arms weight and table standing move with the rank; a display-only rank would be a promise with no teeth | Tier 4 (DY-1b) |
| Q6 | Is alarm ever a number on a player surface? | **No** — alarm is felt through acts (a guarantee given, a brew begun) and read in Talleyrand's words and the Balance tab's sentences ([[feedback-talleyrand-counsel-alive]]: a reading, not a lookup) | Tier 4 (DY-1) |

---

## §1 The thesis, and the inspirations named honestly

EU4's variety engine is six deterministic rules: conquest self-limits (aggressive
expansion breeds coalitions, so minors survive), ambition is scripted per nation
(missions and formables — Brandenburg becomes Prussia by script, not dice), peaces move
land along claims, rivals accelerate each other, a per-campaign bias varies the casting,
and a visible rank ladder gives promotion teeth. None of it needs randomness — which is
why it fits this project's standing laws exactly: dice in battles only, politics
deterministic (AI-0b), the seed moves bars and never choices (pin 14), the historian test
pins every boot.

**The game's own idea** — not a port, a re-expression in this engine's media (letters,
instruments, the table, the Gazette; never a tooltip number):

1. **The Alarm of Europe** (§3) — conquest spends standing with every third court. France
   already pays through threat; now every court does. The Concert's immune system.
2. **The Questions of Europe** (§4) — the era's rivalry is not EU4's declared pairs; it is
   the diplomats' own vocabulary: the German Question, the Italian, the Eastern, the
   Polish. A Question is a named object with CLAIMANTS — a table, not a duel — and a
   claimant's gain quickens the others.
3. **The Awakening** (§5) — the era's genuinely new force: nationhood rising under
   occupation and humiliation. France exports it (the Code, the client crowns) and can
   ride it with generous autonomy or bleed by it — Westphalia against Spain, in one dial.

**Crowns & Recognition** (§6) ties all three to the map at Tier 8, before the deploy: new states
erected at the peace table, marshals crowned, legitimist courts withholding recognition.

Kept inviolate throughout: D2 (a great power never loses its last capital to an AI war),
D3 (France the gravitational centre; a non-player league only when another hegemon's
share exceeds France's), pin 13 (not a soap opera — `soap_opera_share` stays measured),
pin 14 and AI-0b (no dice in politics), the historian test on every seed, Golden Rule 8
(no per-region scans in hot paths — every new write below is event-driven at an existing
chokepoint), Rule 9 (every row below carries its owner, landing, done-when and test), and
the commanded arms' France band 23–28 as the difficulty guard.

---

## §2 The restructured tiers (replaces the plan row's Tiers 1–4)

| Tier | Content | Size | Signature change when it lands |
|---|---|---|---|
| 0 | The review's defects — ✅ COMPLETE November 7, 2026, nine slices (T0-A … T0-I; `SYSTEMS_REFERENCE.md` §178–§184). T0-F, the eclipse brew, is the first Alarm stone: the league must bite the blob. | done | — |
| 1 | The seed at New Game (unchanged from the old plan) — ✅ LANDED November 8, 2026 (`SYSTEMS_REFERENCE.md` §185): a bare New Game ROLLS a readable seed (`roll_campaign_seed()`, adjective-noun-NN, `secrets`-fed — the ambient RNG untouched) and SHOWS it (the reply's message, the first morning's briefing line, the save rows, the menu box prefilled from GET /test's `suggested_seed`); precedence explicit > SOVEREIGN_SEED env > roll, so the suite (conftest pins the env), every harness arm and every rig keeps today's boot byte for byte and never rolls; a School lesson never rolls (a lesson's beats are identical for every player). Pins `tests/test_tier1_the_seed.py`. | 0.5 | — |
| 2 | **Europe varies** (gate `AI_INTENT_SPEC.md` §3.8.2, authored at this tier's head): T2-1 the story signature FIRST and its baseline archived — carrying the NEW columns of §7 from day one; T2-2 ✅ LANDED November 8, 2026 (peace closes the theatre — `SYSTEMS_REFERENCE.md` §188); T2-3 ✅ LANDED November 8, 2026 (Prussia's hook — `SYSTEMS_REFERENCE.md` §189); T2-4 ✅ LANDED November 8, 2026 (Russia's two shores — the quiet-window sleep, derived never dice, pin 22 untouched — `SYSTEMS_REFERENCE.md` §190); T2-5 ✅ LANDED November 8, 2026 (Prussia's second design — Swedish Pomerania as the drawn Stralsund, seated BEHIND the guard so the Ansbach trap stands — `SYSTEMS_REFERENCE.md` §191); **T2-6 ✅ LANDED November 8, 2026 — the casting band, TIER 2 COMPLETE** (the seed casts ONE understudy from (Saxony, Bavaria, Denmark, Naples): its first ACQUIRE boots at its deck's head — the live-first ruling, a guard stepping behind IS being cast, satisfaction restores it — with the bold dial (8, band [4, 12]) over its lean; Bavaria's and Naples' decks authored (the Tyrol boot-live — the Pressburg war aim; the September Treaty then the Roman Expedition); historical casts nobody, structurally; marengo's cast Saxony joins the fight and Switzerland SURVIVES; the DD-1 twin-letter catch fixed at the ratify chokepoint, all ten committed arms at A=0 — `SYSTEMS_REFERENCE.md` §192). The lawful lucky nation. | ≈3 | which minor stirs varies by seed — ✅ delivered |
| 3 | **The strategist** (gate record `AI_INTENT_SPEC.md` §13.2 ✅ RULED November 8, 2026 in Plan Mode at the tier's head — the aim-set deliberately narrow, the metric first, ONE war_aim read, the leash with AI-3c folded in, the aim-held sue, "chains C and D" resolved, the scope guards): **T3-1 ✅ LANDED November 8, 2026** — the march metric (`captures_outside_aim` offline from the digest; the dated baseline `tools/_t3_march_baseline_2026_11_08.json` reads the tier's starting DEBT: **397 ambient captures outside aim** across the ten seeds, 22–72 per seed, Austria the chief offender on every one — `SYSTEMS_REFERENCE.md` §193); **T3-2 ✅ LANDED November 8, 2026** — `war_council.war_aim`, one read spoken in words (the derivation moved home, the instrument delegates; the line speaks the OUTSTANDING object — a held province is no object, a lost one joins the line; three surfaces fold, zero client changes — `SYSTEMS_REFERENCE.md` §194); **T3-3 ✅ LANDED November 8, 2026** — the leash and its conduct rule (the at-war pull toward the stated object; the conduct half by the user's word — an at-war court annexes only its pull or an enemy's seat; AI-3c found already built at Stage D; the debt falls 386 → 208 on every seed, story classes 10 → 8 the honest cost — `SYSTEMS_REFERENCE.md` §195); **T3-4 ✅ LANDED November 9, 2026** — the terms (a court holding its aim offers peace on it: AI–AI the aim's provinces ceded by treaty along authored aims — an AI-only war ending whole on its leaders' aims, a pair inside France's war exiting on its own; AI–player P8-Aim at 25, P8 found already built and the aim letter its first arm; "held" = a delivered gain; ten aim peaces, story classes held at 8, the debt 208 → 228 a purse butterfly on austerlitz, Hanover saved on marengo — `SYSTEMS_REFERENCE.md` §196); **T3-5 ✅ LANDED November 9, 2026 — TIER 3 COMPLETE** — the terms made consistent by the user's "do what's best" (the victor's lenient aim peace only for a loser still standing; a broken loser sues and pays, and every peace signs a held aim over by name), the conduct rule binding the harness France (a marshal under the player's independent command left exempt), chain C (the final tree reproduces T3-3's world-lines byte for byte; against T2-6 nine of ten world-lines moved, story classes 10 → 8, the debt 386 → 208) and chain D (France's entry 245 → 194 with the harness bound; the march toward Estonia still taken as the road to St. Petersburg) — `AI_INTENT_SPEC.md` §13.3, `SYSTEMS_REFERENCE.md` §197; **T3-6 ✅ LANDED November 9, 2026** — occupation is not annexation (an AI peace keeps its aims and hands the rest of the loser's homeland back; the gate measures `annexations_outside_aim`; the kept debt 42 → 7 ambient, the residual Tier 4's — `SYSTEMS_REFERENCE.md` §198). | ≈4 | maps diverge in role-true directions |
| 4 | **The Alarm of Europe** (§3, DY-1) + **promotion's first teeth** (§3b, DY-1b) — and the deploy gate's T3-6 residual (the spoils of eliminated minors kept outside aims: 7 ambient, 8 in the AI-France harness) to 0. **The gate ✅ RULED November 9, 2026 (§3c)** — five census corrections; the erasure rule "sign at the last" added as row DY-1c; Q5 teeth at once, Q6 words only (each the user's "your call"). **T4-1 ✅ LANDED November 9, 2026** — the Alarm (an AI court's capture alarms Europe against its house — 6 a province, 12 a capital, 8 a third court's client — and an alarmed neighbour gives its word for the next victim, only where it binds against the conqueror alone; Prussia's word for Bavaria against Austria at turn 7 on austerlitz, lodi and ulm; story classes 8 → 10; the kept debt 7 unchanged, T4-2's; the AI-France harness's AI courts 8 → 7; `SYSTEMS_REFERENCE.md` §199). **T4-2 ✅ LANDED November 9, 2026** — sign at the last (row DY-1c; `SYSTEMS_REFERENCE.md` §200): a court at its last province signs with every AI court holding homeland it may not keep and lives on; the kept debt 7 → 0 on the ambient seeds and 7 → 0 for the AI courts of the AI-France harness; eight courts sign ambient (Bavaria on every seed where she fell), ten in the harness; story classes 10 → 9 and the fallen-courts column CONVERGES (the Kingdom of Italy alone on all ten seeds, only its turn varying) — the honest cost, reported. **Session A ✅ LANDED November 10, 2026 — TIER 4 COMPLETE** (`SYSTEMS_REFERENCE.md` §201): T4-2b the court removes (a court whose seat a treaty of its own house titles to another AI court removes to the richest homeland province in its hands and returns with its authored capital; the moved seat rides `Region.is_capital`, no field — Bavaria to Franconia on all ten ambient seeds, Hanover to Brunswick on six) and T4-3 promotion (rank DERIVED from a `rank` law in force; the five crowns of 1806 authored on their designs' grounds; `rank_promotion` the one new log type). ONE sweep, three arms: arm 0 reproduces the T4-2 records byte for byte on both surfaces; the seat alone moves every seed (story classes 9 → 10; Prussia's word for Bavaria honoured on seven seeds; Switzerland falls on ulm); **the crowns move nothing — no court held its grounds six turns on either surface** (the nearest: Bavaria in the Tyrol on friedland, two turns); the France band holds on the commanded arms (28 / 27 / 26); the standing series does not move; one province left on the annexation line for the user (Bern, kept by Bavaria on ulm — a fallen client's spoils). | ≈2 | eliminations vary; `guarantees_given` > 0; a minor can rise |
| 5 | **The Questions of Europe** (§4, DY-2). | ≈2 | a second great-power war appears; the war column stops reading Prussia–Hanover alone |
| 6 | **The Awakening** (§5, DY-4/DY-5). | ≈3–4 | occupiers bleed; a liberation war surges; a client rebellion names its cause |
| 7 | **Bounded timing dice** (the old Tier 4) — evaluated at the deploy gate on the story-class count; built only if the count falls short of 4. | gated | — |
| 8 | **Crowns & Recognition** (§6, DY-6/DY-7) — the marquee. | ≈4 | `formations` stops reading "none"; the map gains states history gained |
| — | **S15 THE DEPLOY** (Q1 as REVERSED November 7, 2026 — after Tier 8; §0). Deploy gate: 0 open GR rows, story classes ≥ 4 of 10 (the raise question sits at Tier 6's head — §7), `annexations_outside_aim` 0 (amended at T3-6 — annexation, not occupation; `captures_outside_aim` the war's footprint), France band 23–28, historian test green on every seed. | — | — |

### §2b The session plan — the same content in fewer sessions (✅ RE-CUT November 9, 2026)

**The user's words**, verbatim: "can next session combine some of these steps they seem small",
then "cool resturcture remaining plan so we can do it in less sessions". Nothing below cuts,
defers or moves a single row of §8 — the standing rule on cuts (§0) is untouched. What changes
is the UNIT OF WORK: a session is a tier or a tier-half, not a slice.

**Why it is possible — measured at T4-2, not assumed:** the ten-seed ambient chain runs in 49
seconds and the AI-France chain in about three minutes; the slow parts of a slice are the
pre-commit hook (10:51) and the landing record. A commit a slice paid those once per rule; a
commit a session pays them once.

**The batching rules:**

1. **The gate opens the session and the build follows in it.** A tier's Plan Mode gate no
   longer costs a session of its own. Its open questions (§0) go to the user ONCE, in one
   batch, at the session's head — and are listed in that session's prompt beforehand, so they
   can be answered before the session starts.
2. **One switch a rule, one sweep a session.** Every rule keeps its own named seam. The
   session's measure is ONE sweep with ARMS: arm 0 holds every new seam down and must
   reproduce the prior record byte for byte; each further arm raises one more seam. A moved
   seed is still attributed to exactly one rule — without a commit per rule.
3. **The hook IS the session's one full-suite run.** Commit when the touched families are
   green; if the hook is red, its failure list is the re-pin list. *(Corrected the same day:
   T4-2 ran the suite by hand to find its eight re-pins and then paid the hook again — eleven
   minutes for nothing. Measured: the suite's wall time was the Godot lane — 28 files on one
   worker, 10.0 of its 10.8 minutes. November 10: the lane split in three and ten workers,
   8:49 measured; what binds now is the suite's total work on eight cores.)*
4. **One commit, one landing record, one review a session** — one STATUS entry, one
   `SYSTEMS_REFERENCE.md` section, one series attribution (an arm per seam), one memory.
5. **A rule that is not finished is not committed.** It rolls whole to the next session's
   head; no rule ships dark behind a lowered seam (Rule 9).

**What does NOT change:** every §8 row's done-when and test; each tier's gate is the user's;
the measure chains run alone; Tier 6's gate still opens with the raise-the-gate question, no
default (§7); the deploy gate; no cuts without consent.

| Session | What lands | Opens with | Commit |
|---|---|---|---|
| **A** ✅ LANDED November 10, 2026 (`SYSTEMS_REFERENCE.md` §201) | **Tier 4 closes:** T4-2b the seat (a court whose capital is signed away moves its seat — the user's "use best judgment but focus on utmost quality") + T4-3 promotion (DY-1b, §3c G6) + the tier's close (the France band re-read on the commanded arms, `rank_promotions`). Arms: 0 / seat / seat + promotion. | nothing to rule — both are ruled | one |
| **B** | **Tier 5 whole:** the gate + DY-2 the Questions (the `questions` block and its validator, the latch, the envy term, the beat, the Balance panel, the guarantee rung's Question arm) + DY-3 the Congress rules a Question. Arms: 0 / the Questions / + the Congress. | Q4 (the four Questions) and the latch's store, one batch | one |
| **C** | **The Awakening, first half:** the gate + DY-4 (the store, the raises and cools, the ulcer, the letters — the three decks in lockstep, the pacing chain re-recorded). | Q2, Q3 and **the raise-the-gate question (no default)**, one batch | one |
| **D** | **The Awakening, second half:** DY-5 (the levée, the client dial, the interplays) + the tier's measure chain and close. | nothing new | one |
| **E** | **Crowns:** Tier 8's gate + DY-6 (the crown erected as a guided settlement term, the marshal king — Naples under Murat end to end). | Tier 8's questions, one batch | one |
| **F** | **Recognition and the gate's reading:** DY-7 + Tier 8's close + **Tier 7 evaluated** (the story-class count against the gate; the bounded dice built only if it falls short). | nothing new, unless Tier 7 is needed | one |
| **G** | **S15 the deploy:** the gate checks, the build, the clean-environment run, the release record. Signing waits on the user's certificate. | the user's own walk | — |

**Seven sessions (A–G) where the count read twelve to thirteen.** Two named places it may
take one more, said now so a split is a plan and not a slip: **B**, if the Questions panel's
client pass does not fit beside the engine (the split: engine and words first, the panel
second); **E**, if the guided terms UI needs its own visual pass (the split: the engine and
the AI's road first, the guided UI second). Sizing is information, never pressure (§0).

---

## §3 The Alarm of Europe (DY-1, Tier 4)

**The defect it answers:** Austria eats Bavaria by turn 7 on seven of ten seeds and the
Kingdom of Italy on nine, for free. Minors never live long enough for any ambition to
matter, so every campaign converges. France pays for conquest through threat; no other
court pays anything.

**The contract.** At the ONE capture chokepoint (the same event that already calls
`invalidate_active_nations_cache()`), an AI court's annexation writes threat against the
CONQUEROR through the existing generalized store: `coalition.add_threat(world, amount,
source_key="alarm:<region>", target=<conqueror>)` (`coalition.py:1220`; `target` is the
party who gains threat; `world.threat_by_target` is already serialized). The player's
captures write NOTHING here — France's existing threat machinery is untouched, so nothing
double-charges. Decay is the store's own.

**Numbers (N-DY1, authored, tuneable at the gate):** an ordinary province 6; a capital
12; a province of a court that is some third court's vassal or formation-peer 8. *(Ruled at the gate, §3c: the formation-peer arm removed — no such relation exists; the write is an ADDEND to what every conqueror already paid (census correction C1); the guarantee rung's victim, guarantor and anti-spam defined (G2); the residual's mechanism is row DY-1c, "sign at the last" (G5), because no guarantee reaches the war Bavaria declared (C2).)*

**The instruments — alarm is only ever FELT through acts that already exist:**
- the brew and the eclipse read `threat_by_target` exactly as today
  (`qualifies_for_coalition:1838`, `brewing_gate:3321`, `process_coalition_turn:3416`);
  D3's clause stands — a league against a non-France hegemon only past France's share;
- a NEW guarantee rung in the AI's diplomatic phase: a court with high alarm toward the
  conqueror, bordering the victim's remnant or sharing a §4 Question with it, issues the
  EXISTING D5 guarantee for the likely next victim (anti-spam as every proposal rung);
- Talleyrand's reading and the Balance of Europe tab say it in WORDS (Q6): "Vienna's
  appetite is remarked in Berlin and St. Petersburg." No number anywhere player-facing.

**Done when:** an AI annexation raises the conqueror's `threat_by_target` slot and the
player's captures do not take the new write; on an authored board a conquering court
draws a guarantee letter against it and, past the gates, a brew; the ambient sweep's
eliminations column varies across seeds where it read "Bavaria 6" seven times; Rule 8
pin — the write is event-driven, zero new scans; and the deploy gate's T3-6 residual — provinces KEPT outside a court's authored aims as the spoils of an eliminated minor (`annexations_outside_aim`: 7 ambient, Franconia on seven seeds; 8 for the AI courts of the AI-France harness) — reads 0 on both surfaces (owned here by Rule 9: the Alarm is what makes eating Bavaria cost). **Test:** `tests/test_dy1_the_alarm_of_europe.py`.
**STATUS line at landing:** "Tier 4 the Alarm — conquest pays in standing" with the sweep columns.

### §3b Promotion — a minor that wins may rise (DY-1b, Tier 4, lands with DY-1)

The rank already exists as a static tier (`get_power_tier`, `world_state.py:3675`,
feeding `FORCE_LIMIT_BASE_BY_TIER:419` and the capital-garrison tiers). The change: a
minor that FULFILLS an ambition design and holds its grounds for K turns (N-DY1b: K=6)
unlocks its **promotion law** — the Porte's `nizam_i_cedid` generalized (authored per
ambitious minor in the scenario's reform decks, effect `{type: force_limit, tier:
secondary}` plus call-to-arms weight and settlement-table standing; Q5 default: teeth at
once). Demotion when the grounds are lost. A promotion is a beat and a Gazette line.

**Done when:** on an authored board a Saxony that holds the Wettin grounds enacts its
promotion and its force limit, call weight and table standing move; losing the grounds
demotes; the sweep carries `rank_promotions`. **Test:** rides `tests/test_dy1_the_alarm_of_europe.py`
(one file for the tier). **Dependency honestly stated:** promotion is mostly invisible
until the Alarm keeps minors alive; the two land together for that reason.

### §3c The Tier-4 gate record (✅ RULED November 9, 2026, in Plan Mode at the tier's head)

**The user's words at the gate**, verbatim, on each of the three questions put: on the erasure rule
— "make best decision for immpersion and design dont do whats easy"; on Q5 — "your call make
smartest call for quality"; on Q6 — "your call". The calls below are Claude's under that
delegation, approved with the plan (the user's plan file `majestic-fluttering-eagle.md`).

**Census corrections — what the survey found that §3 did not know** (the Tier-3 gate's idiom):
- **C1.** Every conqueror ALREADY pays threat at capture, AI courts included: `capture_region`'s
  +2 a province (AI-4a step 5) and the combat pipeline's +15 a capital, +3 a battle won and +5 a
  decisive one. What was missing is anything that READS a non-France slot short of D3's eclipse
  (slot ≥ 60 and a bloc share above France's). The Alarm's write is therefore an ADDEND; its
  teeth are the guarantee rung.
- **C2.** A guarantee marches its AI guarantor into a ward's DEFENSIVE war (the instruments tick,
  `instruments.honour_on_road`) and never into a war the ward declared (`_pair_aggressor`). The
  1805 scenario seats Bavaria among the attackers of Austria — it marched beside France — so no
  guarantee can save Bavaria in the opening war; the residual needs a rule about erasure itself.
- **C3.** The only AI guarantee producer (`war_council._run_ai_instrument_producers`) runs on a
  foregrounded design crisis alone; `guarantees_given` read empty on all ten ambient seeds.
- **C4.** Rank is static (`NATION_POWER_TIERS`, never mutated; a pin asserts no world field); a
  law raises only the force-limit floor and carries no prerequisite; no design has a hold clock;
  the call-to-arms tier term reads the ENEMY's tier; the capital garrison reads the static dict
  directly.
- **C5.** Every residual province is the spoils of an ERASURE (Franconia, Bavaria erased by
  Austria in France's war; the AI-France harness's eight, France's allies holding the spoils of
  Austria, Holland and Switzerland erased in France's wars) — and no peace ever reaches an
  erased court's spoils.

**G1 — the Alarm's write (DY-1).** At `WorldState.capture_region`, beside the existing +2 and
under its three skips (own soil, a recovered title, a liberation): an AI conqueror's capture
writes `coalition.add_threat(amount, "alarm:<region>", target=<its house leader>)` — a client's
conquest alarms Europe against its lord's house. N-DY1: a province 6, a capital 12, a province of
a court that is some third court's client 8. **The formation-peer arm is removed, explicitly**: no
such relation exists in the engine; a crown erected at Tier 8 is a client and takes the client
arm. The player's house writes nothing new — France's machinery is untouched. The reckless
auto-charge, the one conquest outside the chokepoint, mirrors the write (the sibling sweep).
Decay is the store's own; the existing readers feel it unchanged (the eclipse, `menace_for`'s
shelter rung, the levy price).

**G2 — the guarantee rung.** `alarm.process_alarm_guarantees`, in the AI-AI diplomatic phase
beside the sponsorships (before the war council, so the deterrent lands before the crisis poll;
before the instruments tick, so an honour marches the same turn). An alarming conqueror is an AI
house leader with a slot ≥ `THREAT_TENSION_MIN` (30). Its likely next victim: (a) a standing
court whose homeland it holds — one at war with it first, then the remnant at peace — read off
its own regions' boot owners; (b) else its defenceless prize. Never the player's house, a client,
or a court already under a live guarantee. The guarantor: an AI court of major or secondary rank
(a minor never promises), not a client, at peace, relation to the conqueror ≤ 0 and to the victim
≥ 0, bordering the victim's remnant, able to march lawfully (`guarantee_join_refusal`), the
strongest such — *(amended by the measure the same day: and only where the word binds against
the conqueror alone — a pledge whose exposure, `instruments.guarantee_exposure`, names any other
court is refused; the first final's Porte gave its word for Austria against Prussia and the
tick marched it on France, `SYSTEMS_REFERENCE.md` §199)*. One AI guarantee a turn world-wide
(the crisis producer's stamp, shared); the
guarantor rests 12 turns (`ai_proposal_cooldowns`). The pledge is `instruments.pledge_guarantee`
(it now carries `against` on the logged event), so all that follows is the instruments' own
machinery. **The Question arm** ("or sharing a §4 Question with it") is DY-2's — added to its §8
row.

**G3 — the brew.** Unchanged; D3 stands. Pinned reachable on an authored board whose conqueror's
bloc already out-shares France.

**G4 — words only (Q6, Claude's call).** `alarm.alarm_line` — "Vienna's appetite is remarked in
Berlin and St. Petersburg." — the remarking courts the conqueror's victims' guarantors, then the
great powers cold toward it, then its cold neighbours, two at most; a victim complains, it does
not remark; the player is never named (Talleyrand speaks for Paris). Talleyrand's situation and
per-court readings, the Balance tab (`alarm_lines`, up to three, one `diplomatic_ledger.gd`
block) and Le Moniteur (`guarantee_pledged` — "Prussia guarantees Bavaria against Austria's
appetite"). No surface carries an AI court's alarm as a figure.

**G5 — sign at the last (new row DY-1c; Claude's call on the erasure question).** The residual's
mechanism, its principle: **a crown falls by treaty, never by the sword alone**. At
`capture_region`'s elimination check (the one military erasure point; erasures by treaty are
untouched), a court whose last province falls is erased only when no AI court at war with it
holds its homeland outside that holder's keepable set (`war_council.keepable_regions`).
Otherwise it signs: the homeland those holders occupy outside their aims goes home
(`game_end._return_home`), and it signs a pair peace with each holder — reason `last_refuge`,
added to `SIGNED_PEACE_REASONS`, so the titling pass, T3-5's lock (the held aim signed over by
name), the declared articles, the eight-turn truce floor, the Road Home corridor and
`follow_the_lord` all apply — and lives on ("Bavaria signs at the last — Austria keeps Munich and
Swabia by treaty; Austria evacuates Franconia."). Its other wars go on, any with the player
among them. Exempt: a client victim (its war is its lord's) and the player's house on either
side — the player's holdings are never moved. **D2 is narrowed, not deleted**: an AI war may
still erase a court whose whole homeland lies in hands that may keep it (the Kingdom of Italy,
inside Austria's Redeem Italy). Why not "a court in exile": courts with no province would be new
to every system (their armies, the AI turn, the table) for a few turns of a homeless army; the
engine's own grammar (T3-6 — the peace decides) says the hour of the last province is the hour a
peace is forced; courts brought to the brink signed rather than vanished — Austria at Pressburg
with Vienna occupied (1805), Prussia at Tilsit reduced to the Memel (1807). **Done when:** on a
crafted board Bavaria lives on in Franconia at peace while the Kingdom-of-Italy shape still
erases; `annexations_outside_aim` reads 0 on the ambient seeds and for the AI courts of the
AI-France harness (or each remaining province goes to the user); the eliminations column varies;
the movers are named. **Test:** rides `tests/test_dy1_the_alarm_of_europe.py`.

**G5 landed (T4-2, November 9, 2026; `SYSTEMS_REFERENCE.md` §200).** Built as ruled, with four
things the build found: (1) both capture arms act on the province AFTER the capture — an AI
capturer whose capture went home by the peace skips plunder, secure and the estate rule
(`world_state.capture_was_signed_home`); (2) the reckless auto-charge, the one conquest outside
the chokepoint, never asked the erasure question at all — a court could be left alive without
ground; it asks now, under the same seam (`_settle_a_court_without_ground`); (3) the pair close
is ONE body, `settlement_third_party._close_the_pair`, factored out of the exits; (4) a
conqueror with no authored aim on its victim hands everything back (Prussia taking both of
Hesse's provinces ends the war with Hesse keeping both) — the rule as ruled, stated because it
shows. **The measure:** the control reproduces T4-1 byte for byte; the kept debt 7 → 0 ambient
and 7 → 0 for the AI courts of the AI-France harness — nothing left to put to the user
province by province. **The one clause of the done-when not met as written:** "the eliminations
column varies" — it CONVERGES by set (the Kingdom of Italy alone on all ten seeds, at turns
7–23; four different sets before), and story classes read 10 → 9. Reported as the slice's
honest cost; the variety is T4-3's and Tier 5's. **The seat** — what the gate did not cover —
was put to the user at the slice's plan ("use best judgment but focus on utmost quality"): a
court whose capital is signed away moves its seat; its own rule and seam, T4-2b (§2b, session
A).

**The seat landed (T4-2b, session A, November 10, 2026; `SYSTEMS_REFERENCE.md` §201; row DY-1d).**
The rule as built, every call Claude's under that delegation: a court whose SEAT a treaty of
its OWN house titles to another holder removes to the richest homeland province in its hands
(authored order breaks a tie) and returns the day its authored capital comes home — "The court
of Bavaria removes to Franconia — Munich is Austria's by treaty." ONE writer
(`game_end._seat_the_court`: the capital map AND the region flag), called from the two arms of
the treaty-title chokepoint (`record_province_title`), the carve's sibling writer and a fallen
court's reset; NO new serialized field — the moved seat rides `Region.is_capital` and is
re-read at load. **Four boundaries, each stated because it shows:** (1) only a SIGNATURE moves
a seat — an occupied capital stays the capital; (2) a treaty between two other courts moves no
third court's seat; (3) **the player's house is exempt on either side** (T4-2's own exemption) —
the player's court never removes, and a court whose capital the PLAYER's house holds by treaty
does not remove either: the Congress's recognition by defeat (RS-D1) reads that capital in the
Emperor's hands, so the rule binds between the AI courts (one line to reverse; reversing it
needs the Congress's reads moved to the authored capital first); (4) the capital whose LOSS is
a court's grievance stays the authored one (`game_end.historic_capital` — the punitive bar, the
partition manner, the Revanche), kept apart from the seat where it sits. **Its measure:** the
seat ALONE moves all ten seeds on both surfaces — a seat is a capital, so Franconia becomes a
lawful object for Bavaria's enemies and Prussia's word for her, never once called on at T4-2,
is honoured on seven seeds; story classes 9 → 10; Switzerland falls on ulm.

**G6 — promotion (DY-1b; Q5, Claude's call: teeth at once).** Rank DERIVED: `get_power_tier` =
the higher of the authored tier and an in-force law's new `rank` clause (`{"tier": "secondary"}`
— no court rises to major by law); no new store, the "no world field" pin stands; the capital
garrison routed through it. A law may carry `requires_design: <id>` — `law_refusal` refuses it
until every province of that design is held by the court with title age ≥ K (N-DY1b: 6; the title
record's `since`, which the quiet clock resets in war — no hold clock added); demotion = a lapse
with reason `grounds_lost` once any of them is lost. The authored laws are the 1806 crowns:
Bavaria the Royal Crown (the Tyrol), Saxony the Royal Dignity (Posen — the Peace of Posen),
Hesse the Grand Ducal Title (Westphalia), Denmark both shores of the Sound (Scania), Sardinia the
mainland restored (Piedmont and Savoy) — price 3,000 gold, upkeep 100; the AI enacts through the
existing 1.78 rung. What moves at once — everything that reads rank: force limit 15k → 30k,
capital garrison 10k → 15k, table standing (consult), bloc weight, a call to arms against it
weighs more (C4: the tier term reads the enemy), no longer vassal-eligible. The event: a new
campaign log type `rank_promotion` (DY-0's column; +1, the census pins flipped knowingly), a beat
and a Gazette line; the validator learns `rank` and `requires_design`, and a deck of promotion
laws alone stands without a warning.

**G6 landed (T4-3, session A, November 10, 2026; `SYSTEMS_REFERENCE.md` §201).** Built as ruled.
What the build decided inside the ruling: a design the boot's seams struck leaves its crown
unenactable and WARNS, never errors (the T2-6 lesson); a grounds lapse refunds nothing and
stamps `lapsed_turn`, so the Arrears price restores the crown once the grounds have stood six
turns again; the AI enacts through the 1.78 rung with NO promotion arm (its purse test stands —
a court whose Net cannot carry 100 a turn waits); the beat is the crown's own (`rank_promoted`,
in place of the routine law line) and the demotion's is `rank_lost`. **Its measure, said
plainly: no court took a crown.** On neither surface did any court hold its design's grounds
six turns in forty — the arm with the crowns is the arm without them, byte for byte, and
`rank_promotions` reads empty on every seed. The nearest: Bavaria in the Tyrol on friedland,
two turns of the six. The rule is pinned on an authored board (Saxony holding Posen); whether
it is SEEN before the deploy is Tier 5's wars to decide — or the user's, by the numbers (K = 6,
the price 3,000) — and is listed among the questions session B opens with.

**G7 — the slices**, each its own commit and the user's review after: **T4-1** the Alarm (G1–G4);
**T4-2** sign at the last (G5); **T4-3** promotion (G6) and the tier's close — the France band
re-read on the commanded arms, the landing record, `rank_promotions`. *(Amended by §2b: T4-2b
and T4-3 landed together as session A, one sweep with an arm a seam and one commit.)*

**G8 — the gates restated.** Tier 4's signature change (§2): eliminations vary, `guarantees_given`
> 0, a minor can rise. The deploy gate is unchanged.

**The tier's close (session A, November 10, 2026).** Read against the final records: the
guarantees are given AND kept (11 alarm guarantees on the ambient seeds, 7 honoured — none was
at T4-2); the eliminations vary on ONE seed of ten (Switzerland on ulm; the Kingdom of Italy
alone on the other nine); a minor CAN rise and none did. Story classes 10 of 10. The France
band on the commanded arms: 28 / 27 / 26 (historical / austerlitz / marengo), inside 23–28.
`annexations_outside_aim`: 0 for the AI courts of the AI-France harness and **1 on the ambient
seeds — Bern, kept by Bavaria on ulm, the spoils of a CLIENT that fell in its lord's war (G5's
own exemption)** — put to the user by the done-when's own way out; the deploy gate's 0 is the
gate's to read.

---

## §4 The Questions of Europe (DY-2, Tier 5)

**Deliberately not EU4's rivals.** No symmetric picker, no declared pair. The era's own
vocabulary: a **Question** is a named object — provinces in dispute — with CLAIMANT
courts seated at it. Austria's deck already carries the id `the_eastern_question`; this
tier names the table that design sits at.

**Authoring.** A new scenario block `questions` (validator-checked: every province
exists, every claimant boots active, at least two claimants):

```
"questions": [
  {"id": "german_question",  "title": "The German Question",
   "provinces": ["Hanover", "Munich", "Swabia", "Saxony", "Frankfurt"],
   "claimants": ["Austria", "Prussia", "France"],
   "voice": "Who speaks for Germany?"},
  {"id": "italian_question", "provinces": ["Milan", "Piedmont", "Venetia", "Naples"],
   "claimants": ["France", "Austria"], ...},
  {"id": "eastern_question", "provinces": ["Rumelia", "Albania", "Moldavia", "Wallachia"],
   "claimants": ["Russia", "Austria", "OttomanEmpire", "Britain"], ...},
  {"id": "polish_question",  "provinces": ["Posen", "Warsaw", "Galicia"],
   "claimants": ["Russia", "Prussia", "Austria", "France"], ...}
]
```
(Final province lists authored at the slice against the live map; Q4 default: these four.)
*(Read against the live map on November 10, 2026, for session B's gate: `Saxony` is drawn as
`Dresden`; `Venetia`, `Moldavia`, `Wallachia` and `Warsaw` are not drawn; `Galicia` on this map
is SPAIN's. As drafted, the Polish Question holds `Posen` alone and the Eastern Question
`Rumelia` and `Albania` — the lists are to be re-authored with the user at the gate.)*

**The latch.** At the same capture chokepoint as §3: if the region belongs to a Question
and the conqueror is a claimant, latch `{question_id: {nation, turn}}`. The latch is
durable (serialized inside an EXISTING store — `WorldState.to_dict` stands at 497 of its
500-line cap, so no new top-level field; the build picks the store at the slice's head
and says so).

**The envy term.** One deterministic addend in `intent._derive_weight`
(`intent.py:393` — beside the statecraft, relation, opportunism and congress terms
already there): if the design's regions intersect a Question's provinces AND the latch
names ANOTHER claimant within the window (N-DY2: `ENVY_WINDOW=8` turns,
`WEIGHT_QUESTION_ENVY=+15`), the design quickens. A court not seated at the table feels
nothing. O(questions) per derivation; zero dice.

**The beat.** When a latch write makes its gainer the plurality holder of the Question's
provinces where it was not before, "the Question turns" — a beat (exempt from the
narration cap, as all beats are) in the Question's own authored voice.

**The Congress may rule a Question** (DY-3 — the tier's cut-first tail, per the
living-cut-list idiom): while a Congress sits, a ruling recognizes the present holder —
the latch clears (envy relief), the unseated claimants take a relation write (grievance).
Prague by machinery, not script.

**Surfaces:** the Balance of Europe tab gains a Questions panel — sentences, no bars:
"The German Question: open. Prussia gains; Vienna watches." (R7 names throughout.)

**Done when:** the latch writes at capture and nowhere else; the envy term raises a
claimant's design weight inside the window, not outside it, and never a non-claimant's;
the beat fires once per turn-of-the-Question; the validator refuses a Question naming an
unknown province or a dead court; the sweep carries `questions_turned`. **Test:**
`tests/test_dy2_the_questions_of_europe.py`. **STATUS line:** "Tier 5 the Questions —
the era's rivalry at the table", with the second-war count per seed.

---

## §5 The Awakening (DY-4 and DY-5, Tier 6 — PRE-deploy by Q1's reversal, §0)

**The era's own force, and the game's answer to "rising nationalism".** A per-court
scalar 0–100 (Q2 default; no per-region store — regional expression is DERIVED), living
inside an existing serialized store (the `to_dict` cap again; the build names the store).

**It RISES from** (all event-driven writes at existing chokepoints):
- home provinces under foreign occupation: a counter per court, maintained at
  capture/liberation off the boot owner (`world._starting_controllers`;
  `is_own_soil_recapture`, `world_state.py:1014`); the turn tick adds by band
  (N-DY4: 1–2 occupied +1/turn, 3–5 +2, 6+ +3) — O(nations), never O(regions);
- a dictated peace against the court (the settlement ratify writes +15, tier-scaled);
- the sovereign captured (+10); a client squeezed — autonomy lowered or tribute raised
  (+5, written by the vassal action itself).

**It COOLS by** −1/turn with no home province occupied; −10 lump on home rule restored
(liberation term, autonomy raised, occupation ended by treaty).

**Three expressions first (the teeth), each riding a named seam:**

| Expression | The history | The seam | The rule (N-DY4/5, authored) |
|---|---|---|---|
| **The ulcer** | Spain, 1808– | `_supply_multiplier` (`world_state.py:8949`), where home 1.5×, war damage and doctrine already compose | an occupier's effective supply cap on soil whose boot owner stands at `AWAKE_RISEN` (70): ×0.75. **Q3 default: France bleeds too** |
| **The liberation levée** | 1813 | `get_manpower_regen_rates:8261` (war exhaustion already scales it; laws apply last via `reforms.apply_manpower_regen`) | the awakened court (≥ `AWAKE_STIRRING`, 40), at war, home soil contested: infantry regen ×1.5, recruit cost ×0.75 |
| **Client drag — or the tiger ridden** | Westphalia vs Spain | `process_vassal_loyalty` (`vassal.py:1144`) + `AUTONOMY_DRIFT:39` | a client whose nation is awakened: loyalty −2/turn at autonomy ≤ 1; **+1/turn at autonomy ≥ 2** — France can ride the force it exports, by paying in control |

**Letters** ride the affairs engine (`affairs.py:711` `PREDICATES` + `PREDICATE_PARAMS`;
the three-deck lockstep — scenario + the two fixtures — and the standing trap: a moments
op added reds `test_moments_pacing.py` until the chain re-records). The Gazette names
the stirring; "events appear" — the letters' conditions are the scalar's own thresholds,
never rare gates, and the affairs engine's repetition rules apply. (`alarm` is a BARRED
affair op — the Awakening's letters carry their own ops and never write §3's alarm.)

**Interplays, named now so they are designed once:** awakening ≥ `AWAKE_RISEN` is the
concrete trigger variable the emergent-designs contract (§3.6 of the intent spec —
Prussia after Jena) has been missing; an awakened nation lowers coalition friction among
its would-be liberators; an unrecognized crown (§6) on awakened soil drifts worse.

**Done when:** the AI-France sweep's march to Estonia bleeds (the ulcer measured against
the review's own baseline); an authored 1813 board surges (the levée); a client rebellion
on some ambient seed names awakening as its cause while a high-autonomy client converts
it to loyalty; the sweep carries `awakening_events`; Rule 8 pin on the tick. **Tests:**
`tests/test_dy4_the_awakening.py`, `tests/test_dy5_the_tiger_ridden.py`. **Slices:**
DY-4 the store, the raises/cools, the ulcer, the letters; DY-5 the levée, the client
dial, the measure chain. **STATUS lines** at each landing.

---

## §6 Crowns & Recognition (DY-6 and DY-7 — Tier 8, the pre-deploy marquee, after §5)

The era's cool maps were NEW states: the Confederation, Warsaw, Westphalia. The table
machinery half-exists: `CANONICAL_CLAUSE_TYPES` (`settlement_scoring.py:100`) already
registers `create_client`, `liberation` and `vassal_transfer`.

- **DY-6 The crown erected:** the `create_client` term promoted to a first-class guided
  settlement term ([[feedback-settlement-guided-ux]]): carve named ceded provinces into a
  new client court. **The marshal king:** optionally crown a marshal (Murat in Naples) —
  the roster loses its man (the stand-down machinery exists), his glory is satisfied
  permanently (the jealousy ladder's release valve), the client's loyalty seeds from his
  trust, and the passed-over marshals take authored grievances. History with teeth: a
  crown costs you your best sword.
- **DY-7 Recognition:** a new crown is recognized or not, per court — the legitimist
  courts (authored: Austria, Russia, Britain while unbeaten) withhold it; an unrecognized
  crown pays at the table and in trade, and on awakened soil drifts worse (§5); a Congress
  may grant recognition (the same instrument that rules a Question). A recognition
  granted or refused is a beat.

**Done when:** a peace erects Naples under Murat end-to-end through the guided terms UI
(never typed — [[feedback-settlement-typed-command-not-player-facing]]); the jealousy
ladder reflects the crown; recognition moves acceptance and trade and the Congress can
grant it; `formations` on the sweep stops reading "none" on seeds where a crown rises.
**Tests:** `tests/test_dy6_the_crown_erected.py`, `tests/test_dy7_recognition.py`.

---

## §7 The instrument (DY-0 — lands WITH T2-1 at Tier 2's head, before anything builds)

The measure precedes the build, as every row here has. DY-0 extends the sweep's derived
metrics (`tools/ai_v_sweep.py:445` `derive_metrics`) and the one-definition signature
(`:1248` `_variance_signature`) with: `questions_turned`, `awakening_events`,
`rank_promotions`, `guarantees_given`, and `formations` promoted from the digest's final
block to a derived column. **The story-class count** — the deploy gate's number — is the
count of distinct signature classes across the ten ambient seeds, computed by the
signature tool itself; the pre-build baseline is archived
(`tools/_dy_signature_baseline.json`, written by a chain run that runs ALONE).
**DY-0 ✅ LANDED November 8, 2026** (`SYSTEMS_REFERENCE.md` §186): the baseline reads
**9 of 10 story classes** pre-band — the floor the tiers must beat.

**The gates, restated in one place:** the DEPLOY gate (after Tier 8 — Q1 as reversed,
§0) is unchanged in substance — 0 open GR rows, story classes ≥ 4 of 10 with the
historian test green on every seed, `annexations_outside_aim` 0 (amended at T3-6), France band 23–28. Whether
the story-class GATE should RISE now that the Awakening and the Crowns ship pre-deploy
is a question for Tier 6's head, put to the user with NO default marked; until the user
rules, ≥ 4 of 10 stands, and the post-Awakening reading — ≥ 6 of 10, at least one seed
with a minor at secondary rank, the eliminations column varying — stays an aspiration,
not a gate. (One line of color, not a gate's evidence: T0-E/F/G's after-sweep
hand-grouping read 10 of 10 story classes on the war columns alone,
`SYSTEMS_REFERENCE.md` §182.5 — but DY-0's own signature is the instrument, and it lands
at Tier 2's head.) Tier 7's dice are built only if the deploy-gate count falls short of
4 — variance must first be earned by content, dice are the last resort and stay bounded
by pin 14.

---

## §8 The slices (Rule 9 — every row owned, landed, tested)

| Slice | Tier | Scope (owner §) | Done-when | Test |
|---|---|---|---|---|
| T1 | 1 — ✅ LANDED November 8, 2026 | the seed at New Game (§2 Tier 1) | a bare New Game rolls and names a readable seed; explicit > env > roll; the env never rolls (the suite's law); shown on the reply, the first morning, the save rows and the menu box | `tests/test_tier1_the_seed.py` |
| T2-B | 2 — ✅ LANDED November 8, 2026 | the gate's new bands (§3.8.2): readiness, the minors' lean (banded `weight_mod`), the three seams | authored + validator-clamped; historical byte-identical; the dated re-record reads 10 of 10 classes | `tests/test_t2b_the_new_bands.py` |
| T2-2 | 2 — ✅ LANDED November 8, 2026 | peace closes the theatre (§2 Tier 2): the fresh-peace clause in the ONE coveting predicate (`coalition.fresh_peace_turns_left`, no second constant) | the design sleeps DERIVED and wakes at the floor's lapse or the war's return; dormancy never satisfies (no phantom crown, no +10 resolve); the grudge keeps its subject; the dated re-record holds 10 of 10 with historical byte-identical (`SYSTEMS_REFERENCE.md` §188) | `tests/test_t2_2_peace_closes_the_theatre.py` |
| T2-3 | 2 — ✅ LANDED November 8, 2026 | Prussia's hook (§2 Tier 2): the bandwagoner joins the stronger side of a live AI-vs-AI war (statecraft-derived, the ally-entry join idiom), reneges once a campaign when the scales turn | the gates all existing reads (relation < 0, `can_declare_war`, free strength, the player on neither side, no rejoin); the quota a `participant_meta` stamp, no new world field; the dated re-record holds 10 of 10 — marengo alone moves (Prussia joins Hesse's war at T20, Hanover falls T23), historical byte-identical (`SYSTEMS_REFERENCE.md` §189) | `tests/test_t2_3_prussias_hook.py` |
| T2-4 | 2 — ✅ LANDED November 8, 2026 | Russia's two shores (§2 Tier 2): a contain design sleeps once the court's own war with its hegemon has been over for the quiet window (`AGENDA_QUIET_WINDOW_TURNS` 8; the clause in `_contain_active` beside the SF-LB-1 sibling; the clock `coalition.pair_war_quiet_turns` over BOTH war stores — the archive the witness's keeper) — the arbiter stands down and `gulf_and_straits` wakes | not belligerent (WAR/ARMISTICE wakes at once) + the ended-war WITNESS (never-fought stays armed — Sweden's boot-peace scourge the shipped proof; a new hegemon re-arms the watch) + 8 turns past; dormancy never satisfies; pin 22 untouched (derived, never dice — no scenario line moved); the dated re-record holds 10 of 10 with ZERO ambient movers, historical byte-identical — the road to the second shore is the player's own peace (`SYSTEMS_REFERENCE.md` §190) | `tests/test_t2_4_the_quiet_window.py` |
| T2-5 | 2 — ✅ LANDED November 8, 2026 | Prussia's second design (§2 Tier 2): `swedish_pomerania` (`acquire_regions`, ["Stralsund"] — the drawn province of Swedish Pomerania, verified Sweden's and coveted) authored in the scenario, seated BEHIND `armed_neutrality` — the guard's seat is load-bearing (`_active_guard_map` prices ACTIVE guards only; the Ansbach trap and the S14k posture stand), so the claim speaks only when Prussia is already at war with the Hanover question settled (1715 Stettin; 1815 the shore itself) | authored content, no new rule, no seam (the T2-B precedent); boot-invisible on every seed (the prize leads — the pin-22 sibling); no order band (the §3.8.2 gate ruled none; the acquires are now non-contiguous, recorded) and no readiness (the `gulf_and_straits` second-design precedent); one pin re-seated with its cause (`test_guard_inactive_at_war` — the deck no longer runs out); the §12.7 restraint annotated, recorded not silently edited; validator at the same 11 warnings (`SYSTEMS_REFERENCE.md` §191) | `tests/test_t2_5_swedish_pomerania.py` |
| T2-6d | 2 — ✅ LANDED November 8, 2026 | The owed decks (§3.8.2's "Bavaria and Naples carry no decks today — T2-6 authors them"): Bavaria's `the_tyrol` (["Tyrol"], deliberately BOOT-LIVE — at war with Austria, the Pressburg war aim: 1805, not drift) and Naples' `september_treaty` (guard, ["Naples"] — the real 1805 treaty, priced from boot) + `roman_expedition` (["Rome"], Ferdinand's '98 precedent, speaks only at war) | content on every seed; Spain alone the deckless armed court (the S14k-3 residue, the strict xfail's reason updated); six deckless-court pins re-seated by STAGING the designless board; the sr8c §7a scene-1 record amended (an acquire on the Habsburg is no Confederation design); chain A moved every world-line, historical included, classes 10 of 10, the two class movers named (Naples and Bavaria join fight rosters) (`SYSTEMS_REFERENCE.md` §192) | `tests/test_t2_6_the_casting.py` (TestTheDecks) |
| T2-6 | 2 — ✅ LANDED November 8, 2026 — **TIER 2 COMPLETE** | The casting band (§3.8.2's last ruled band): `cast_understudy` + `_resolve_casting` in `campaign_variance` (the key popped — the band-strip idiom), the cast court's first ACQUIRE at its deck's head (the live-first ruling: the guard steps behind, satisfaction restores it) + the bold dial (8, [4, 12]) over its lean; `_validate_casting` (shape hard, seam-trimmed shortlist courts WARN — from_scenario validates the board that boots); the envelope order pin learned the second lawful source | historical casts NOBODY (structural; byte-identical A↔B, pinned); the ten seeds cast all four courts (pinned per seed); the casting's own movers austerlitz + marengo — cast Saxony at fight and SWITZERLAND SURVIVES; the DD-1 twin-letter catch fixed at `_ratify_player_events` (`restamp_pending_treaty_letters` — the S6 idiom at the moment staleness is born), all ten committed arms A=0; classes 10 of 10 on both records (`SYSTEMS_REFERENCE.md` §192) | `tests/test_t2_6_the_casting.py` |
| DY-0 | 2 (with T2-1) — ✅ LANDED November 8, 2026 | the signature columns + baseline (§7; §3.8.2's event-type contract) | columns derived, baseline archived by a lone chain (story classes 9 of 10 pre-band) | `tests/test_dy0_the_signature.py` |
| T3-1 | 3 — ✅ LANDED November 8, 2026 (with the §13.2 gate) | the march metric (§13.2 R1/R2): each war's aim-sets read ONCE at its opening onto the digest (`aims` on the opened rows; the boot wars' on `boot.wars` — `_war_ids` pre-seeds), `derive_metrics` joins the `region_captured` rows offline — the ambient total excludes the player, the per-court map keeps everyone (the AI-France surface reads its France entry; one instrument, two surfaces) | instrument-only, no engine line moved; the signature carries the column, `story_class` does not; the assurance controls green on the widening; the compatibility pin — the baseline's signatures minus the column byte-identical to the T2-6 record's; the dated baseline is the tier's starting DEBT: **397 ambient outside-aim captures** (22–72 per seed; Austria 11–26 on every seed, Britain 6–16 — the blob's spread captures, the Estonia-march class made a number) (`SYSTEMS_REFERENCE.md` §193) | `tests/test_t3_1_the_march_metric.py` |
| T3-3 | 3 — ✅ LANDED November 8, 2026 | the leash and its conduct rule (§13.2 R4; the conduct half by the user's "Extend with conduct rule"): `aim_pull_set` — the design's unmet targets ∪ the OUTSTANDING stated object at war, the recapture riding the aim — consulted by the one covet memo (GR5); `annexation_permitted` — an at-war court deliberately annexes (P4.5, P4.25) only its pull or an ENEMY'S SEAT, binding only where a live war record stands; R1's capital default restored PER PAIR as a metric credit and conduct permission, the words and the pull reading the stated object alone; the instrument's boot wars moved to the first row (the IQ-7 graft control's catch) | arm 0 reproduces the prior byte for byte; the conduct rule ALONE moves the standing series (re-pinned at [10], prior kept as `SERIES_BEFORE_T3_3`); the control chain reads zero world-line movers against T3-2 (debt 386 under the corrected metric); the final reads the debt **386 → 208 on every seed**, story classes **10 → 8** (eylau and jena converge on wagram — Holland spared, Spain kept out) — the deploy gate's ≥ 4 holds; AI-3c found built at Stage D, Q1 re-verified (`SYSTEMS_REFERENCE.md` §195) | `tests/test_t3_3_the_leash.py` |
| T3-4 | 3 — ✅ LANDED November 9, 2026 | the terms (§13.2 R5): ONE predicate, `war_council.aim_sue_due` — a DELIVERED gain from this enemy (`war_aim_delivered`, the designs' provinces in its house's homeland wholly in hand), nothing still owed (the seat skipped — the capital default read never), war score ≥ 25; AI–AI the aim's provinces ceded by treaty, no indemnity, the loser signing inside `AIM_TERMS_BAND` of its own peace line — an AI-only war ends whole on its leaders' aims (`attempt_aim_held_settlement`, the existing machinery verbatim), a pair inside France's war exits on its own (`held_aim_suit`, reason `aim_held_sue` in `SIGNED_PEACE_REASONS`); AI–player P8-Aim (`aim_peace`; P8 found already built — the census correction) | the control chain reproduces T3-3's final record byte for byte (the seams cover the slice); the final reads ten aim peaces — Prussia on Hanover on every seed, the same turns, the terms changed (the province by treaty instead of ~2,610 gold); two aim letters to France; two world-lines move through that gold — marengo (Hanover survives) and austerlitz (a purse butterfly re-times the league war on Austria); story classes held at 8; the debt 208 → 228, the rise austerlitz's alone (`SYSTEMS_REFERENCE.md` §196) | `tests/test_t3_4_the_terms.py` |
| T3-5 | 3 — ✅ LANDED November 9, 2026 — TIER 3 COMPLETE | chains C and D and the landing record (§13.2 R6, §13.3) — with two changes the session found: the terms made consistent by the user's "do what's best" (`aim_terms_signable` signs only while the loser stands — `line ≤ score ≤ line + band`; a broken loser sues on its own road and pays; `held_aim_lock` signs a held aim over by name in the loser's suit, the broker road and both pair exits) and the conduct rule binding the harness France (`the_conduct_binds_every_runner`; `annexation_permitted` takes the acting marshal — independent command stays exempt) | chain C reproduces T3-3's world-lines byte for byte (T3-4's purse butterfly removed; the lock signed on every seed — "Prussia takes Hanover. Hanover pays … gold."); against T2-6 nine of ten world-lines moved, story classes 10 → 8, the debt 386 → 208; chain D: France's entry 245 (exempt) → 194 (bound), the Estonia road still taken, 41 of France's 213 captures liberations (`SYSTEMS_REFERENCE.md` §197) | `tests/test_t3_5_the_tier_closes.py` |
| T3-6 | 3 — ✅ LANDED November 9, 2026 | occupation is not annexation (the residual debt ruled — the user's "make best call, best design not easiest"): at a peace between AI courts the winner keeps what the treaty cedes and what it may keep (`war_council.keepable_regions` — its house's authored aims, its declared articles) and hands the rest of the loser's homeland back (`game_end.aim_evacuations` in the one titling pass; the player's peaces keep SR-1a; a corps left standing walks home by the Road Home corridor); the gate measures annexation — `war_council.annexations_outside_aim`, recorded at the run's end, a new signature column, never the story class | the control reproduces T3-5's chain C (the column the instrument's); the final: the kept debt 42 → 7 (Franconia alone — Bavaria's elimination spoils on seven seeds), fifteen handbacks named, four world-lines moved (Saxony survives on austerlitz, Hanover on marengo), story classes held at 8; the AI-France harness's AI courts keep 8; the residual owned by Tier 4 (§3's done-when) (`SYSTEMS_REFERENCE.md` §198) | `tests/test_t3_6_the_residual_debt.py` |
| T3-2 | 3 — ✅ LANDED November 8, 2026 | `war_council.war_aim` (§13.2 R3): `war_aims_of_instance` is THE derivation, moved home VERBATIM — the instrument delegates (one body, divergence impossible, the delegation pinned); `war_aim` unions the pair's live wars; `war_aim_clause`/`war_aim_line` speak the OUTSTANDING object (the boot DEFENSE records rightly sit in the metric's set and are noise as words — a held province is no object, a lost one joins the line the turn it falls) | three surfaces in words, zero client changes (the enemy block's PC-R7 fold + `aim_display`; the peace table's per-court "object in this war" lines; the intent summary's at-war fold, the defenceless-prize twin); no new store/log type/seam; one re-seat with cause (PC-X38 `endswith` → `in` — the articles still named, the aim trails them); the chain reads ZERO movers, the debt 397 unchanged, historical byte-identical (`SYSTEMS_REFERENCE.md` §194) | `tests/test_t3_2_the_war_aim.py` |
| DY-1 | 4 — ✅ LANDED November 9, 2026 (T4-1) | the Alarm (§3; the gate §3c G1–G4): `alarm.sound_the_alarm` at the one capture chokepoint (an AI court's capture writes 6 / a capital 12 / a third court's client 8 against its house, on top of the +2; the player's house nothing new; the auto-charge mirror), `alarm.process_alarm_guarantees` in the AI-AI phase (the existing D5 guarantee for the likely next victim; one a turn world-wide, the guarantor resting 12), the words (`alarm_line` — Talleyrand, the Balance tab, Le Moniteur; never a figure) | the control reproduces the T3-6 record byte for byte (the seams cover the slice); the final: three alarm guarantees (Prussia for Bavaria against Austria at turn 7 — austerlitz, lodi, ulm; never marched: Bavaria declared her war), story classes 8 → 10, eight world-lines moved and named (the write alone on eylau, historical, jena, marengo and wagram — Saxony erased at turn 39 on wagram; the rung alone on lodi; both on austerlitz and ulm), the kept debt 7 unchanged in total (T4-2's); the AI-France harness's AI courts keep 7 (8), Prussia's word for Bavaria honoured against Switzerland on three seeds; `BASELINE_SERIES` re-pinned (the write alone — Mack's two more crushed assaults on Lorraine); two siblings fixed in the slice — the word bound to the conqueror alone, the page's lone filler (`SYSTEMS_REFERENCE.md` §199) | `tests/test_dy1_the_alarm_of_europe.py` |
| DY-1c | 4 — ✅ LANDED November 9, 2026 (T4-2) | sign at the last (§3c G5 — the erasure rule the T3-6 residual needs): a court whose last province falls is erased only when no AI court at war with it holds its homeland outside that holder's keepable set; otherwise it signs a pair peace with each such holder (reason `last_refuge` in `SIGNED_PEACE_REASONS` — the titling pass, T3-5's lock, the declared articles, the truce floor, the Road Home corridor, `follow_the_lord`) and its off-aim homeland goes home; a client victim and the player's house exempt; D2 narrowed, not deleted (its annotation in `AI_INTENT_SPEC.md` §6 lands here) | on a crafted board Bavaria lives on in Franconia at peace while the Kingdom-of-Italy shape still erases; `annexations_outside_aim` reads 0 ambient and for the AI courts of the AI-France harness (or each remaining province goes to the user); the eliminations column varies; movers named — **measured:** the crafted board ✓ (Bavaria in Franconia, the Kingdom of Italy erased); `annexations_outside_aim` 0 on BOTH surfaces, nothing left for the user; the movers are exactly the seven seeds where Bavaria fell; **the eliminations column does NOT vary by set** (the Kingdom of Italy alone on all ten, turns 7–23) — the honest cost, reported (§3c, G5 landed) | rides `tests/test_dy1_the_alarm_of_europe.py` (`TestSignAtTheLast`, `TestTheT42Measure`) |
| DY-1d | 4 — ✅ LANDED November 10, 2026 (T4-2b, session A) | the court removes (§3c "The seat" — the user's "use best judgment but focus on utmost quality"): a court whose seat a treaty of its own house titles to another holder removes to the richest homeland province in its hands, and the seat returns with the authored capital; ONE writer (`game_end._seat_the_court`), the two arms of `record_province_title`; the moved seat rides `Region.is_capital` — no new serialized field; the player's house exempt on either side; `historic_capital` keeps the grievance's read apart; the static-table readers audited | on a crafted board Bavaria's court sits in Franconia, guarded, and returns with Munich; a save reloads it off the flag; arm 0 reproduces the T4-2 records — **measured:** all met; the seat ALONE moves all ten seeds on both surfaces (story classes 9 → 10; Prussia's word honoured on seven seeds; Switzerland falls on ulm); the standing series does not move; **one province on the annexation line for the user** (Bern — a fallen client's spoils) (`SYSTEMS_REFERENCE.md` §201) | rides `tests/test_dy1_the_alarm_of_europe.py` (`TestTheCourtRemoves`, `TestTheSessionAMeasure`) |
| DY-1b | 4 — ✅ LANDED November 10, 2026 (T4-3, session A) — **TIER 4 COMPLETE** | promotion's teeth (§3b; the gate §3c G6 — rank DERIVED from an in-force `rank` law, `requires_design` held K=6 by title age, demotion a `grounds_lost` lapse, the 1806 crowns authored, `rank_promotion` the new log type) | Saxony's promotion on an authored board; demotion; the beat; the France band re-read on the commanded arms and the tier's landing record — **measured:** the authored board ✓ (Saxony holding Posen six turns: force limit 15,000 → 30,000, the capital's guard 10,000 → 15,000, bloc weight, no longer vassal-eligible; Posen lost, the Dignity lapses); the France band 28 / 27 / 26, inside 23–28; `rank_promotions` on the signature — **empty on every seed of both surfaces: no court held its grounds six turns, and the arm with the crowns is the arm without them** (the nearest, Bavaria in the Tyrol on friedland, two turns) — reported, and put to the user at session B's head (`SYSTEMS_REFERENCE.md` §201) | rides DY-1's file (`TestPromotion`, `TestTheSessionAMeasure`) |
| DY-2 | 5 | the Questions (§4) — and the Alarm's guarantee rung's Question arm (§3c G2: a court seated at a Question with the victim may guarantee it, not only a neighbour) | the latch, the envy term, the beat, the panel, the validator; the rung's Question arm pinned | `tests/test_dy2_the_questions_of_europe.py` |
| DY-3 | 5 (cut-first tail) | the Congress rules a Question (§4) | a sitting Congress recognizes the holder; relief and grievance written | rides DY-2's file |
| DY-4 | 6 | the store, raises/cools, the ulcer, the letters (§5) | the AI-France march bleeds; the letters appear by condition | `tests/test_dy4_the_awakening.py` |
| DY-5 | 6 | the levée, the client dial, the measure chain (§5) | 1813 surges; the tiger ridden at autonomy ≥ 2 | `tests/test_dy5_the_tiger_ridden.py` |
| DY-6 | 8 | the crown erected + the marshal king (§6) | Naples under Murat, end to end, guided UI | `tests/test_dy6_the_crown_erected.py` |
| DY-7 | 8 | Recognition (§6) | recognition moves acceptance/trade; the Congress grants | `tests/test_dy7_recognition.py` |

*(Amended November 9, 2026 by §2b: one commit and one review a SESSION; each rule keeps its own seam and its own arm of the session's one measure.)* Each slice: its own commit through the hook, the user's review after, Plan Mode at each
tier's gate (§0's open questions put there). The measure chains run alone. **CLAUDE.md:**
untouched today (19 bytes of headroom); DY-1's landing adds this spec's one Document Map
row and pays for it by trimming an equal weight in the same commit — that debt is owned
HERE, not left vague.

---

## §9 Deliberately not copied, and the laws kept

**Not copied from EU4:** the aggressive-expansion tooltip number (alarm is felt, never
read — Q6); the symmetric rival picker (the Questions are tables, not pairs); monarch
mana; random lucky nations (the seed CASTS from an authored shortlist — T2-6); pop-based
nationalism (a court-scalar with derived regional teeth — Q2); dice anywhere in politics.

**Kept:** D2, D3, pins 13 and 14, AI-0b, the historian test, Golden Rules 8 and 9, the
France band 23–28, `BASELINE_SERIES` discipline (every series-moving slice lands with its
re-measure; the chains run alone), and the three-deck lockstep for every authored letter.
