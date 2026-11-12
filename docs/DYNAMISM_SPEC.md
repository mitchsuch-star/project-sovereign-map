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
| Q2 | The Awakening's grain | **Per-court scalar**, regional expression derived (a per-region store costs save size and Rule 8 care for no v1 behavior the scalar cannot express) — **✅ RULED November 10, 2026 at session C's head, under the user's delegation ("rule yourself be rigorous make it good"): the per-court scalar, the store `world.moments["awakening"]` (§5a)** | Tier 6 (DY-4) |
| Q3 | Does the ulcer bleed France too? | **Yes** — Spain is the point: the player feels the mechanic they inflict (an AI-only ulcer would be a rule the player reads about but never meets) — **✅ RULED November 10, 2026 at session C's head (delegated): YES, with no player exemption anywhere in the module, and the corollary — the player's own people stir when invaded (§5a)** | Tier 6 (DY-4) |
| Q4 | The Questions list | **Four** (German, Italian, Eastern, Polish); the Maritime Question stays folded into the blockade/CS machinery `NAVAL_SPEC.md` already owns — **✅ RULED November 10, 2026 at session B's head: "Four on the drawn map" (§4a)** | Tier 5 (DY-2) |
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
| 5 | **The Questions of Europe** (§4, DY-2) — **✅ COMPLETE November 10, 2026, session B** (`SYSTEMS_REFERENCE.md` §202; the gate §4a): DY-2 the Questions, DY-3 the Congress rules a Question, and the three leftovers — DY-1e Bern's road home, DY-1f the Emperor's gift, DY-1g the Emperor's treaty moves a seat. ONE sweep, six arms: arm 0 reproduces session A on both surfaces; the Questions ALONE move all ten ambient seeds (story classes held 10 of 10); the tables turn 26 times — the German for Austria at turn 2 on every seed, the Italian on every seed, once for Prussia; **no second great-power war appears** (the war column unchanged on eight seeds; rivoli gains the Hanover war where the honour war stood; ulm calms) — the 1805 board's tables turn for Austria, who is at war already, and the only envious design with an army is Prussia's — put to the user at session C's head; Bern's road clears the annexation line (1 → 0, Switzerland lives on ulm); no crown taken; the band 28 / 27 / 26 on every arm; the standing series unmoved. | ≈2 (one session) | a second great-power war appears; the war column stops reading Prussia–Hanover alone — ❌ NOT MET ambiently on the 1805 board (reported; the reason and the levers in §4a) |
| 6 | **The Awakening** (§5, DY-4/DY-5) — **session C ✅ LANDED November 10, 2026 (the gate §5a ruled under the user's delegation; THE DEPLOY GATE RAISED, §7; DY-4: the store, the derived count with the boot-web house read, the bands, the cools, the lumps, the dictated peace by rank, the sovereign taken, the client squeezed, the beats, the ulcer, the two letters and the `awakening` op — `SYSTEMS_REFERENCE.md` §203)**; **session D ✅ LANDED November 10, 2026 (DY-5: the liberation levée and the National Guard, the client dial — the tiger ridden —, a risen people's revanche, the liberators' friction, the third letter *The Nation in Arms* and the `national_guard` op — `SYSTEMS_REFERENCE.md` §204; the landing record §5b) — TIER 6 COMPLETE**. | ≈3–4 | occupiers bleed; a liberation war surges; a client rebellion names its cause — **measured at C: the peoples stir and rise on every surface (France's own ambiently, Austria's and Russia's under the AI-France march); the march does NOT visibly bleed (the ulcer taxes the cap, a corps under it pays nothing — reported, the lever to the user); the letters appear by their own conditions on the frozen board and on no measured arm; measured at D: every DY-5 seam bites where its condition holds — the levée rises on every ambient seed and on eight harness seeds, the letter arrives on the scripted France — and NOT ONE measured world-line moves in forty turns (reported; the levers to the user: the letter's floor, the AI rungs' reading of the levée, the dial's ambient road); the gate's clauses 2 and 3 still UNMET, Tier 8's** |
| 7 | **Bounded timing dice** (the old Tier 4) — evaluated at the deploy gate on the story-class count; built only if the count falls short of 6 (§7, as raised). **✅ EVALUATED November 10, 2026 at session F (§6c): the count reads 10 of 10 after DY-6 and DY-7 — NOT built.** | evaluated | — |
| 8 | **Crowns & Recognition** (§6, DY-6/DY-7) — the marquee. **Session E ✅ LANDED November 10, 2026** (the gate §6a ruled under the user's delegation; DY-6: the `crown` block on the ONE catalogue — six crowns authored —, the teeth at the one apply site, the marshal king and the prince, the AI's road, the `crowns` block — `SYSTEMS_REFERENCE.md` §205; the landing record §6b); **Session F ✅ LANDED November 10, 2026 — TIER 8 COMPLETE** (DY-7: the legitimists' condition at the three peace chokepoints, the Congress's grant and refusal, the `recognition` beat, the three prices; Tier 7 evaluated and NOT built — `SYSTEMS_REFERENCE.md` §206; the landing record §6c). | ≈4 | `formations` stops reading "none"; the map gains states history gained — **measured at E: arm 0 reproduces session D byte for byte, the band and the classes hold, the series unmoved; NO crown is erected on any measured arm (reported — the AI road's live case waits on wars the idle France never frees the courts to fight; the player's Naples under Murat and the AI's Finland under Russia proved on crafted boards); clauses 2 and 3 still UNMET, session F's reading; **measured at F: arm 0 reproduces session E byte for byte, nothing is recognized and no price bites on any measured arm (no crown rises ambiently), the band and the classes hold, the series unmoved — clauses 2 and 3 UNMET on every record since Tier 4, TO THE USER with no default (§6c, §7) — earned by session G, November 11, 2026 (§7a)** |
| — | **S15 THE DEPLOY** (Q1 as REVERSED November 7, 2026 — after Tier 8; §0). Deploy gate — **RAISED November 10, 2026 at Tier 6's head (§7, ruled under the user's delegation):** 0 open GR rows; story classes **≥ 6 of 10**; **at least one ambient seed with a minor at secondary rank by promotion** (`rank_promotions`); **the map's roster varying** — at least two distinct (fallen courts, formed states) readings across the ten seeds (`eliminations` ∪ `formations`); `annexations_outside_aim` 0 (amended at T3-6 — annexation, not occupation; `captures_outside_aim` the war's footprint); France band 23–28; historian test green on every seed. The second and third clauses are UNMET today and are content's to earn (§7); a clause still unmet after session F goes to the user as an explicit question with no default — never a silent cut (§0). **Session F read both UNMET (§6c, November 10, 2026) — the question is the user's now, beside the deploy (session G).** **The user's word: "Earn them first" — ✅ EARNED November 11, 2026 by session G (§7a): clause 2 on lodi and marengo (Hesse's Grand Ducal Title), clause 3 on wagram (the Papal States fall to the cast Naples) — the gate reads MET in full on the ambient record; the deploy is session H.** | — | — |

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
| **B** ✅ LANDED November 10, 2026 (`SYSTEMS_REFERENCE.md` §202; the gate record §4a) | **Tier 5 whole:** the gate + DY-2 the Questions (the `questions` block and its validator, the latch, the envy term, the beat, the Balance panel, the guarantee rung's Question arm) + DY-3 the Congress rules a Question — and the three leftovers session A put to the user: DY-1e Bern's road home, DY-1f the Emperor's gift (both roads), DY-1g the Emperor's treaty moves a seat. Arms: 0 / Q / QC / BERN / GIFT / ALL. | Q4 (the four Questions) and the latch's store, Bern, the crowns, the seat's boundaries — one batch | one |
| **C** ✅ LANDED November 10, 2026 (`SYSTEMS_REFERENCE.md` §203; the gate record §5a; the gate raised §7) | **The Awakening, first half:** the gate + DY-4 (the store, the raises and cools, the ulcer, the letters — the three decks in lockstep, the pacing chain re-recorded). Arms: 0 / STIR / ULCER / ALL. | Q2, Q3 and **the raise-the-gate question (no default)**, one batch — the user's "rule yourself be rigioprous make it good" | one |
| **D** ✅ LANDED November 10, 2026 (`SYSTEMS_REFERENCE.md` §204; the landing record §5b) | **The Awakening, second half:** DY-5 (the levée, the client dial, the interplays) + the third letter + the tier's measure chain and close. Arms: 0 / LEVEE / DIAL / REVANCHE / LIBERATORS / ALL. | nothing new — none was | one |
| **E** ✅ LANDED November 10, 2026 (`SYSTEMS_REFERENCE.md` §205; the gate record §6a; the landing record §6b) | **Crowns:** Tier 8's gate + DY-6 (the crown erected as a guided settlement term, the marshal king — Naples under Murat end to end). Arms: 0 / CROWN / AI / ALL. | Tier 8's questions, one batch — the user's "code commit and push what it tells you is next" (delegated) | one |
| **F** ✅ LANDED November 10, 2026 (`SYSTEMS_REFERENCE.md` §206; the landing record §6c) | **Recognition and the gate's reading:** DY-7 + Tier 8's close + **Tier 7 evaluated** (10 of 10 — the bounded dice NOT built). Arms: 0 / RECOG / ALL. | nothing new — Tier 7 was not needed; the gate's clauses 2 and 3 to the user, no default | one |
| **G** ✅ LANDED November 11, 2026 (`SYSTEMS_REFERENCE.md` §207; the landing record §7a) | **The gate earned** (the user's "Earn them first" at session F's close — the content session the raised gate's clauses 2 and 3 asked for): the pact with the coveted (no defensive alliance or alliance between a coveter and the coveted — the defect that defused the cast Naples' Roman Expedition at turn 3 and Hesse's Westphalian Duchy at turn 16) + a crown bought with the whole chest (the promotion law's AI purse bar is its price). Arms: 0 / PACT / ALL. | nothing new to rule — the user's word at the fork | one |
| **G2** ✅ LANDED November 11, 2026 (`SYSTEMS_REFERENCE.md` §208; the landing record §7b) | **The played campaign** (the user's "fix and playtest … play well see derivations see dynamism test like humna" — a session the plan did not hold, opened by the review of the arc): a France played by hand on a fresh seed, and what it found fixed at the cause — the king's carry on the separate peace, the war names the beaten, a court at `fight` still asks, the ladder outlasts the rest, a backed design dares; the marshals' side and the screens. Arms: 0 / ASK / LADDER / ALL. | nothing to rule — drafted in Plan Mode and approved | one |
| **G3** ✅ LANDED November 11, 2026 (`SYSTEMS_REFERENCE.md` §209; the landing record §7c) | **A client swears no pact of its own** (the user's "Rule on clients first", then "make best cal for game" — session G2's open reading (a), ruled under the delegation): a client's foreign policy is its lord's — no defensive alliance or alliance is proposed to or from a court that answers to a lord, every court alike; the Vassals card says it. Arms: 0 / CLIENT. | the ruling itself — delegated, drafted in Plan Mode and approved | one |
| **G4** ✅ LANDED November 11, 2026 (`SYSTEMS_REFERENCE.md` §210; the landing record §7d) | **The open readings, ruled and built** (the user's "evaluate options choose the best", then "and decide and do these" — session G3's three readings and the rest of session G2's list, fourteen rulings in one plan): a nation proclaimed on what it holds at its authored bar (Italy at three of five, Rome first), an ally's soil is not won, a pact lapses at the vassalage, a backer is no menace, the people drive out a foreign king, a commission reads the arming ceiling, the Emperor's ally takes no separate peace while it wins, no guns from a sanctuary, a bandwagoner joins a neighbour's war, a client joins no war against a house it is at peace with; the dispatch, the crown row and the chip. Arms: 0 / FORM / WON / LAPSE / REAR / CEILING / ALLY / GUNS / WAGON / HOUSE / ALL. | the rulings themselves — delegated, drafted in Plan Mode and approved | one |
| **G5** ✅ LANDED November 11, 2026 (`SYSTEMS_REFERENCE.md` §211; the landing record §7e) | **A client rallies against the house** (the user's "do what you deem best then tell me what next" at session G4's close — its five readings ruled under the delegation): the commission ceiling, the band and Italy's numbers stand; the neutral client is re-cut — where her lord already fights the aggressor's house a client takes up his war with it and marches on its client, and stays out only where her lord is at peace with that house; the gate's annexation read counts a house's authored aims though it stands under the knife (the sweep's catch). Arms: 0 / RALLY / ALL. | nothing new to rule — the delegation | one |
| **H** | **S15 the deploy:** the gate checks, the build, the clean-environment run, the release record. Signing waits on the user's certificate. | the user's own walk | — |

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
the price 3,000) — and is listed among the questions session B opens with. *(Ruled at session
B's head, November 10, 2026 — §4a: the levers stand, they never bit; the road is the Emperor's
gift, both roads built as row DY-1f.)*

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

### §4a The Tier-5 gate record (✅ RULED November 10, 2026, in Plan Mode at session B's head)

**The user's words at the gate**, verbatim, on the four questions put in one batch (the §2b
idiom — the rulings listed in the session's prompt beforehand): on Q4 and the provinces —
**"Four on the drawn map"** (the authored lists below, the proposed seats included); on Bern —
**"Road home"**; on the crowns' levers — **"best solution no corner cutting"**; on the seat's
two boundaries — **"reason best solution for gameplay"**. The last two are delegations; the
calls below are Claude's under them, approved with the plan (the user's plan file
`structured-kindling-starfish.md`).

**Census corrections — what the survey found that §4 did not know** (the Tier-3 and Tier-4
gates' idiom):
- **C1.** The draft lists did not fit the map: `Saxony` is drawn as `Dresden`; `Venetia`,
  `Moldavia`, `Wallachia` and `Warsaw` are not drawn; `Galicia` here is Spain's; `Vilna` is
  Russia's SEAT. The Porte's key is `Ottoman`, not `OttomanEmpire`.
- **C2.** The latch's store: `WorldState.to_dict` stands at 497 of 500 lines, so the latch
  lives inside an EXISTING store. Surveyed: `world.congress` is out (its None-ness is
  load-bearing — the summons pins read `world.congress is None`); `campaign_totals` is
  display-only by charter; `formable_nations`, `nation_formations`, `statecraft`, `war_intents`
  and `province_title` are iterated by readers expecting one shape per key. The one store that
  already carries a sibling engine's runtime beside its own is `world.moments` — the affairs
  engine keeps its streaks and latch masks in `world.moments["affairs"]` (RE-1). The Questions
  follow that precedent: `world.moments["questions"] = {block, latch, turned, ruled}`,
  written only where a table is authored (the bare flag world's `moments` stays `{}`).
- **C3.** The crowns' levers were not the lock: session A's own measure read no court holding
  its grounds longer than two turns in forty on any seed, so K = 6 and the 3,000 price never
  bit — moving them would be a false lever. In history four of the five crowns came by the
  EMPEROR'S TREATY (Pressburg gave Bavaria the Tyrol; Posen crowned Saxony). The road existed
  in the played game and had two gaps: the ally petition's prevalidation asked only for what
  the payer STILL HELD (stricter than the validator's own `occupied_homeland_cession_ok`), so
  the bill branch's own Pressburg case — France holds the Tyrol, Austria cedes it to Bavaria —
  could never fire; and the desire profiles named no grounds for Saxony's, Hesse's or Denmark's
  crowns, so three of five could never be asked for.
- **C4.** Bern (ulm): Switzerland, bribed over to Britain, attacked Bavaria's seat; Prussia
  honoured its word; Bavaria took Bern, Switzerland's last province. A CLIENT victim signed
  nothing (T4-2's exemption — its war is its lord's), so it fell and the spoils met no peace.

**Q4 — the four tables, as authored** (every province drawn, every claimant a standing court;
the `questions` block of `europe_1805.json`, validated by `_validate_questions`):

| id | title / voice | provinces | claimants |
|---|---|---|---|
| `german_question` | The German Question — "Who speaks for Germany?" | Hanover, Munich, Swabia, Dresden, Frankfurt | Austria, Prussia, France |
| `italian_question` | The Italian Question — "Whose is Italy?" | Milan, Piedmont, Naples, Rome | France, Austria, Sardinia, Naples |
| `eastern_question` | The Eastern Question — "Who inherits the Porte?" | Rumelia, Albania, Epirus, Constantinople, New Russia | Russia, Austria, Ottoman, Britain |
| `polish_question` | The Polish Question — "Is Poland to rise again?" | Posen, Lithuania, Volhynia, Podolia | Russia, Prussia, Austria, France, Saxony |

Sardinia and Naples at the Italian table and Saxony at the Polish were Claude's proposal,
accepted with the ruling — their designs sit on Piedmont, Rome and Posen. The claimants'
designs that touch a table today: Austria's `primacy_germany`, `redeem_italy` and
`the_eastern_question`; Prussia's `hanoverian_prize`; Russia's `gulf_and_straits`; the Porte's
`the_black_sea_shore`; Sardinia's `house_of_savoy_restored`; Naples' `roman_expedition`;
Saxony's `the_wettin_crown`. Britain and France feel the words and the latch, not the envy.
The numbers (N-DY2) stand: `ENVY_WINDOW` 8, `WEIGHT_QUESTION_ENVY` +15; N-DY3, named here:
`QUESTION_RULING_GRIEVANCE` −10 (each unseated claimant's relation to the recognized holder).

**DY-2 as built** — `backend/game_logic/questions.py`, seam `the_questions_of_europe` (row
T5-Q): the latch at `WorldState.capture_region` beside the Alarm's write and at the reckless
auto-charge's mirror (the sibling sweep), the capturer's HOUSE the claimant read (a client's
conquest is its lord's — the Alarm's own idiom), the turn's intent cache NOT flushed at the
write (intent is turn-granular by `intent.py`'s staleness contract; the envy reads from the
next derivation — a mid-turn flush moved the historical Prussia's crisis from turn 5 to 9 on
the sweep's first run);
the envy term one addend in `intent._derive_weight` outside the `against` block (a court not
seated feels nothing; a court's own gain quickens nobody of its house; once, not per table) —
**and the ladder is honoured** (the session's own catch, found on the sweep's first run and
the driven board's): a court climbs its ladder by ASKING — asks are made at the ask, buy,
align and bandwagon rungs, and of an AI court nothing is asked at the ultimatum — and the
council's patient-ask gate (`_ladder_climbed`, two refused asks on record) opens its crisis; a
court the envy carried straight to the ultimatum stopped asking (the driven austerlitz lost
its Hanover crisis), and one carried to `fight` never fought (the historical Prussia sat at
`fight` ten turns and never fought Hanover). The addend is therefore applied AFTER the seeded
jitter (the cap reads the figure the ladder reads — on austerlitz the jitter pushed a capped 84
to 85) and capped in three stages (`questions._below_the_floors`): below the COERCE floor
until the court's ladder against its object has climbed, below the FIGHT floor until its
crisis stands (`world.war_intents`), the whole addend once it stands or once the court is at
war with its object — the envy hastens what the fore-warning already promised (beat 2: no
cold-open wars);
the beat when a latch write makes its house the STRICT plurality holder among the CLAIMANT
houses where it was not before THIS capture (a table held from the boot does not turn for its
holder; a tie turns nothing) — ONE `question_turns` row (`question` is what DY-0's column
reads; the log census 182 → 183, the fourteen pins flipped) and a HIGH line in the table's own
voice: "THE GERMAN QUESTION TURNS: Prussia holds Hanover; Vienna watches. Who speaks for
Germany?"; the Balance of Europe tab's sentences (`question_lines` — open: who gains and who
watches, the player's house never named as a watcher; ruled; quiet), one `.gd` block; the
Alarm's guarantee rung's Question arm (`alarmed_guarantor`: a court seated with the victim may
give its word, not only a neighbour — `share_a_table`).

**DY-3 as built** — seam `the_congress_rules_a_question` (row T5-C): on the sitting's tick,
after the signatures are taken and before the answers, each Question with a live latch and no
ruling this sitting is RULED — its present plurality holder recognized, the latch cleared
(envy relief), every other standing claimant's relation to the holder −10 (the player's house
takes no grievance: the Congress is his), one `congress` row (phase `ruling`, no new type), one
HIGH beat ("The Congress rules the German Question: Prussia is recognized in what it holds;
Vienna takes it ill."). A table nobody holds is not ruled; a later capture re-latches it.

**Bern — "Road home" (row DY-1e, seam `settlement_third_party.a_lord_signs_for_its_client`,
T5-BERN).** T4-2's own principle carried to clients: a client at its last province does not
fall by the sword either — **its LORD signs for it.** The pair closed with each holder is the
lord's where the client's war with that holder is the lord's (`client_pair_is_the_lords_war`
and a live record on the lord's pair; SR-1b: a vassal's pair never exits on its own account —
`follow_the_lord` inside `_close_the_pair` carries the client out), else the client's own; the
homeland outside the holders' keepable sets goes home first, as T4-2 does it. Exempt, as
before: the player's house on either side (his clients that fall are his to liberate by
treaty; his holdings never move). "Britain signs for Switzerland at the last — Saxony
evacuates Bern." The event carries `signed_by`.

**The crowns — "best solution no corner cutting" (row DY-1f).** The levers stand (K = 6, the
price 3,000 — C3). The road is the Emperor's gift, completed on both sides: **(i) the player's
road** — the ally petition asks for the ally's AUTHORED designs' provinces
(`settlement_offers._coveted_regions_of_ally`: the designs first, the desire profile after —
one source for every road that asks what an ally wants; Saxony asks for Posen, Hesse for
Westphalia, Denmark for Scania, Sardinia for Piedmont and Savoy, Bavaria for the Tyrol), and
the petition's prevalidation reads the validator's own occupied-homeland rule
(`_occupied_homeland_ok`), so Pressburg's Tyrol — France holds it, Austria cedes it — is
asked for, granted, titled by treaty, and six quiet turns later the AI's own rung enacts the
Royal Crown (pinned end to end); **(ii) the AI's road** — seam
`settlement_third_party.a_leader_signs_for_its_allies` (T5-GIFT): an AI war's aim peace carries
each co-belligerent's DELIVERED aim that the winner's SIDE holds, ceded to that ally by the
same treaty (`war_council.side_aim_cessions`; never the player's house, never a great power's
capital, never a province the leader's own cessions name; "Russia takes Finland. Denmark takes
Scania." — the consequence names each receiver). Down, a junior's aim in its leader's hands
went home to the loser by T3-6.

**The seat's boundaries — "reason best solution for gameplay" (row DY-1g, seam
`game_end.the_emperors_treaty_moves_a_seat`, T5-SEAT).** Boundary (1), the player's own court
never removes, is KEPT: Paris signed away is the campaign's own catastrophe and the Fall owns
that story. Boundary (2), a court whose capital the PLAYER's house holds by treaty does not
remove, is REVERSED: the player's own Pressburg is the most-played road, and every read that
follows the seat (the guard, the AI's "enemy's seat" object, the war-score component, the
homing) read a province the court did not hold — the inconsistency T4-2b removed between AI
courts, left on the road the player walks most. The one reader the boundary protected — the
Congress's recognition by defeat (RS-D1) — asks "did they lose the capital", the grievance's
read by definition, and `game_end.historic_capital` already answers it: the Congress's capital
reads moved to it (`congress._historic` — `_capital_taken`, the latch's `capital`, the
recognition lines and preview, the sue reasons, the war lever; `game_end`'s `capital_kept`
producer, which reads the map AFTER the clauses apply). With no seat removed every read is
byte-identical. "The court of Austria removes to Bohemia — Vienna is France's by treaty."

**What the session keeps whole under §2b rule 5:** nothing rolled — DY-2, DY-3, DY-1e, DY-1f
(both roads) and DY-1g all land in session B's one commit; the sweep's six arms are 0 / Q / QC
/ BERN / GIFT / ALL.

**The session landed (November 10, 2026; `SYSTEMS_REFERENCE.md` §202; the pins
`tests/test_dy2_the_questions_of_europe.py` `TestTheSessionBMeasure`).** ONE sweep, six arms on
three surfaces (`tools/_t5_measure.py`), run ALONE — three times: the first run and the hook's
first run named three defects, fixed at the cause before the record (the envy carrying a court
past the ultimatum before its crisis stood; a mid-turn flush of the turn's intent cache at the
latch; the envy lifting a court off its asking rungs, with the jitter applied after the cap). **Arm
0 reproduces session A's records byte for byte on both surfaces.** **The Questions ALONE move all
ten ambient seeds** — on seven of them only the new column and the turn Prussia first reaches
`fight` (the envy hastens a climb already under way: historical 11 → 9, jena 11 → 9, marengo 12 →
10, friedland 14 → 12, eylau 15 → 13), the whole signature on rivoli alone — and one of the
harness's (ulm); story classes **10 of 10 on every arm**. **The tables turn 26 times:** the German
Question for AUSTRIA at turn 2 on every seed (her Munich and Swabia in the opening war) and again on
austerlitz, friedland, lodi and ulm (6–10); the Italian for Austria on every seed (7–23 — Milan and
Piedmont from the Kingdom of Italy); the German once for PRUSSIA (jena, 41); the Polish and the
Eastern tables never (the Porte holds four of its five from the boot, Russia three of her four, and
no claimant takes from them in forty turns). **The tier's signature change is NOT met — said
plainly:** no second great-power war appears. The war column stands where session A left it on
eight seeds (the historical war turns [11, 12, 27, 27, 37] unchanged); rivoli gains the Hanover war
where Prussia's honour war for Bavaria stood (her crisis at 13 comes before the word is called on,
`ai_war_count` 0 → 1; Spain's word for the Porte at 29 not given); ulm's late Saxon cluster calms
(13 → 5 pairs). The reason is the 1805 board, not the term: the tables turn for Austria, who is at
war already, and the only envious design with an army behind it is Prussia's Hanover — Austria's
rivals at the Italian table (Sardinia, Naples) are armyless minors, at the Polish table nobody takes
from Russia, and the Eastern table never turns. Put to the user at session C's head (the prompt's
item 5). **Bern's road clears the annexation line:** `annexations_outside_aim` 1 → 0 ambient at arm
BERN (ulm alone moves — Switzerland, Britain's client at war with Bavaria on its OWN account, signs
its own pair at the last at turn 14 and lives on; the eliminations column reads the Kingdom of
Italy alone on all ten again), 0 for the harness's AI courts on every arm. **No crown:**
`rank_promotions` 0 on every seed and arm (the Grand Ducal Title the first run saw on lodi came
with the defect's re-timing and is gone with it); the levers stand and the gift's roads are pinned
on their boards. The Congress's ruling, the gift's AI road and the seat under the Emperor's treaty
move NO ambient or harness seed — no Congress sits, no co-belligerent's delivered aim meets an aim
peace, no player treaty cedes a capital in forty ambient turns; each is pinned on its authored
board. The totals: the last refuges 22 → 22, the Alarm's guarantees 11 → 10 (honoured 7 → 6 —
rivoli), `captures_outside_aim` 252 → 258 (Q) → 248 (BERN); the harness's France entry 119 → 118
(reported, never gated). **The France band holds** on the commanded arms: 28 / 27 / 26 on every
arm, inside 23–28. **The standing series does not move** (`tools/_t5_series_arms.py` →
`_t5_series_arms_final.json`, an arm per seam with each seam's reach counted): all six arms
reproduce HEAD's `BASELINE_SERIES` byte for byte — the Questions' seam read 2,215 times on that
loop, eight latches and two turns of a table, no ruling, no lord's refuge, no ally's cession;
`BASELINE_SERIES` stands, no re-pin, no re-link.

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
dial, the measure chain. **STATUS lines** at each landing. **Both landed November 10,
2026 — DY-4 in session C (§5a's landing note), DY-5 in session D (§5b): TIER 6 COMPLETE.**

**Amended at the gate (§5a, November 10, 2026 — the census corrections, each binding on
the build):** the occupied-home count is DERIVED once a turn, never a maintained counter
(C1); "foreign-held" is a HOUSE read against the court's live house AND its BOOT house
(C2); every court of the boot roster carries the scalar, eliminated ones and the player's
house included (C3); "the sovereign captured" is the marshal event, not the capital (C4);
"a dictated peace" rides the one punitive writer, tier-scaled by the court's DERIVED rank
(C5); "tribute raised" is the autonomy write (C6); the two thresholds are AUTHORED in the
scenario's `awakening` block, the raises, cools and the ulcer's factor code constants (Q2).

---

### §5a The Tier-6 gate record (✅ RULED November 10, 2026, in Plan Mode at session C's head)

**The user's words at the gate**, verbatim, on the three questions put in one batch (the §2b
idiom — the rulings listed in the session's prompt beforehand): **"rule yourself be rigioprous
make it good"** — a delegation of all three. The calls below are Claude's under it, approved
with the plan (the user's plan file `transient-hatching-kurzweil.md`). Each is one line to
reverse.

**Q2 — the grain: a PER-COURT scalar 0–100, regional expression DERIVED.** A per-region store
would cost save size and Rule 8 care for no v1 behavior the scalar cannot express; the
regional teeth are derived — the ulcer reads the province's boot owner, the count reads the
boot homeland. **The store** is `world.moments["awakening"] = {"block": {stirring, risen},
"houses": {client: boot lord}, "courts": {court: {"level", "occupied"}}}` — the T5 precedent
(`questions.py`: `install` beside the moments line on `from_dict`; `moments.store_from_data`
drops unknown keys, so the sibling re-adds itself; `save_manager._backfill_moments` carries
both siblings across a rebuild; `_backfill_awakening` arms a pre-Tier-6 save of the 1805
campaign, every people at 0, the save's own web as the boot web — nothing retroactive).
Sparse: a court's row exists once its level or its count is nonzero. `WorldState.to_dict`
gains no line (497 of 500 stands). **Armed by the scenario's top-level `awakening` block**
`{"stirring": 40, "risen": 70}` — the two thresholds the letters and the teeth read, authored
content validator-clamped (`_validate_awakening`: integers in [1, 99], `stirring` below
`risen`, an unknown key an ERROR — the `statecraft` idiom; an empty object arms the code
defaults; D7's principle: a hotter or colder era is a mod's dial, reviewable in the file).
The bare flag world, the tutorials and the legacy rollback author none and write nothing
(`moments == {}` pinned). The raises, the cools and the ulcer's factor stay code constants
(N-DY4, the `ENVY_WINDOW` idiom).

**Q3 — the ulcer bleeds France too: YES, with no player exemption anywhere in the module.**
Spain is the point; an AI-only ulcer is a rule the player reads about and never meets.
Corollary, ruled with it: the player's own house carries the scalar like every court — when
Austria stands on French soil the French people stir and the invader bleeds (1814's question,
answered symmetrically — Building Blocks: the same systems, different input values).

**THE RAISE-THE-GATE QUESTION — ruled in §7: THE GATE RISES** (the three clauses, their
columns and their owners are recorded there; §2's deploy row carries the gate as ruled).

**Census corrections — what the survey found that §5 did not know** (the Tier-3, -4 and -5
gates' idiom):
- **C1.** A maintained occupied-home counter would drift. Fifteen writers set
  `region.controller` outside `capture_region` — the three treaty roads
  (`settlement_ratify._apply_settlement_terms`, `_ratify_one_time_clauses`, the surety
  return), `compensation`'s paid territory, `diplomacy.hand_back_province`,
  `game_end._return_home` (the status quo's and T3-6's evacuations), `formations`' client
  carve, the vassal grants and reclaims, the transfer to the player, the debug cheats. The
  count is therefore DERIVED once a turn at the tick: the court's boot homeland
  (`nation_starting_regions`, serialized) against the holders' HOUSES — O(Σ homeland), 126
  lookups a turn on the 1805 map, no `regions.values()` walk (the Rule-8 source pin). The
  capture chokepoint writes nothing for DY-4.
- **C2.** "Foreign-held" is a HOUSE read: the holder's live house (`_top_overlord`, the
  Alarm's and the Questions' read) is outside the court's HOME houses (`awakening.
  home_houses`) — the court itself, and its BOOT lord while the court is still (or again)
  that lord's client or has been erased: the web the court was born into, snapshotted into
  the store once the vassals are final (the Europe boot seeds its web in `__init__`; the
  file carries no `vassals` key). So a boot client's soil under its lord is home; the
  Kingdom of Italy's under France is home though the court was erased, under Austria
  occupied; Spain's under France is occupied though Spain marched beside France in 1805
  (the ulcer's own case); Hanover's under Prussia is occupied though a treaty signed it.
  **A court SUBJUGATED later keeps its boot house** — its new lord's holdings are foreign
  (Spain under Joseph; Austria under the Emperor's own Pressburg): the people rise against
  the garrisons of the lord imposed on them, and DY-5's client dial reads the same scalar
  (the first sweep's read — a vassalized court's soil "home" to its new lord — would have
  left the player's most-played road without an ulcer and the dial without a road; refined
  before the final record). A client that broke free reads its old lord's holdings as
  foreign from then on. An empty controller is nobody's garrison.
- **C3.** Every court of the boot roster carries the scalar — ELIMINATED ONES INCLUDED (a
  people outlives its court: Poland; the Kingdom of Italy's soil under Austria stirs on
  every ambient seed) and the player's house. The letters bind ACTIVE hosts only (the
  display slots assume a court); an erased court's people act through the ulcer and the beat.
- **C4.** "The sovereign captured" is a marshal event, not the capital: `WorldState.
  capture_marshal` (the ONE capture seam, W6-7 / NP-4) with `marshal.is_sovereign` — Bayonne:
  Ferdinand taken, Spain rises (+10). On the 1805 roster the sovereign marshal is Napoleon's
  own: the Emperor taken raises the French people (Q3's corollary, pinned).
- **C5.** "A dictated peace" already has ONE writer: `emergent_designs.record_punitive_cessions`
  (the three ratify roads call it; the punitive bar = homeland cessions ≥ N or the historic
  capital, compensation netted). The Awakening's write rides inside it, scaled by the court's
  DERIVED rank (`get_power_tier` — a promoted minor feels it as a secondary): major +15,
  secondary +10, minor +5 — a great power's people feel a partition more (Tilsit → 1813;
  Pressburg → 1809). A peace below the bar writes nothing.
- **C6.** "Tribute raised" is the same write as autonomy lowered (`TRIBUTE_RATES[level]`; no
  separate tribute verb exists): `change_vassal_autonomy` down = the squeeze (+5), up = home
  rule restored (−10); `release_vassal` is the lump's other road — every road to a release
  passes it (the liberation term on both ratify roads, the voluntary release, the rebellion).
- **C7.** The affairs deck's mechanical hash (`deck_sha` descends into `affairs`) is pinned by
  `test_moments_pacing.py`, `test_affairs_reach.py` and `test_affairs_pacing.py`: two letters
  and one op re-record the reach and the probe (the au4 chain's phases 1–3 and `record`, run
  ALONE after the sweep — `tools/playtest_runs/t6_pacing_2026_11_10/chain.sh`).
- **C8.** `since` rows arm a template by seam (`affairs.row_armed`): the letters carry
  `since: "DY-4"` → `awakening.the_people_write()`; arm 0 holds them out of the deck whole.

**DY-4 as built** — `backend/game_logic/awakening.py`, three seams (`tests/_t3_seams.py`
rows T6-STIR, T6-ULCER, T6-LETTERS): **the scalar** (seam `the_people_stir`) — the tick sited
in `_advance_turn_internal` right before `moments.tick` so the morning's letters read the
fresh scalar: per boot court the derived count, +band (N-DY4: 1–2 foreign-held +1 a turn,
3–5 +2, 6 or more +3) or −1 with none held, the lump −10 on the transition occupied → none;
the event writes at their one sites (C4–C6); ONE writer `move` for every change, clamped
0–100, the beat on a phase crossing — one `awakening` log row (`phase` quiet / stirring /
risen, `direction`, `occupied`, `cause`; the log census 183 → 184, the fifteen pins flipped;
DY-0's `awakening_events` column reads the prefix, the `awakened` class the nations named)
and a HIGH dispatch line in the courts' register, in WORDS ("THE PEOPLE OF SPAIN STIR: 4
home provinces under foreign garrisons; couriers are waylaid and requisitions refused." /
"THE PEOPLE OF SPAIN HAVE RISEN: an occupier's columns bleed on their roads — the country is
an ulcer." / "The people of Spain are quiet again — home rule is theirs."), never a figure
of the scalar (Q6's spirit); Le Moniteur's courts column names the stirring. **The ulcer**
(seam `the_ulcer_bleeds`) — `_supply_multiplier`'s read after the naval verdict and BEFORE
the doctrine's step (SF-DC-1's "last step" contract kept): ×0.75 when the province's boot
owner stands at `risen`, the soil is foreign-held and the army's house is outside the
owner's; the owner's own army never bleeds, nobody bleeds on home-held soil, an ally beside
the occupier bleeds; shown = applied by construction (`get_effective_supply_cap` feeds the
bill, the dispatch's strain headline, the ledger and the depot chip). **The letters** (seam
`the_people_write`) — two templates in the affairs deck, the scenario and the fixture in
lockstep: *The People Stir* (predicate `people_stir`: the most-occupied ACTIVE court at
`stirring` below `risen` whose homeland the lord's house holds; Fouché writes; Accept
"Proclaim the liberties" 600 gold, an action, the people −15; Decline "Let the prefects
manage" authority −2 / −3 / −4 by tier beside the host's goodwill and loyalty −3, `bites:
"clamp"` — the Host's shape, the user's "Clamp it first": a people's rising arrives on a
bled board too) and *The Ulcer* (`people_risen`;
Berthier writes; Accept "An amnesty and a charter" 1,000 gold, an action, the people −20;
Decline "The sword answers" authority −3 / −4 / −5 beside goodwill and loyalty −5, clamped
the same); the `awakening` op — the twelfth
(`moments.OPS` 11 → 12, the four pins flipped) — Accept-only, bounds −30..−1, quoted in
words ("the people of Bavaria quieten (risen → stirring)"), applied through the one writer;
the dated deck's vocabulary stays closed (not in `OP_BOUNDS`). The lord's own clients never
bind (their soil under him is home); another house's garrisons are not the Emperor's affair.
**What DY-5 (session D) owns from here:** the levée, the client dial, the interplays, and the
third letter — *The Nation in Arms* (the player's own people risen against an invader, the
levée's own letter), named here so it has a home (Rule 9).

**The session landed (November 10, 2026; `SYSTEMS_REFERENCE.md` §203; the pins
`tests/test_dy4_the_awakening.py` `TestTheSessionCMeasure`).** ONE sweep, four arms (0 / STIR /
ULCER / ALL) on three surfaces (`tools/_t6_measure.py`), run ALONE — twice: the first run's read of
a subjugated court's soil as "home" to its new lord was refined before the record (§5a C2), and the
second run reproduces the first on every surface. **Arm 0 reproduces session B's records byte for
byte on both surfaces**; the France band holds at 28 / 27 / 26 on every arm; story classes **10 of
10 on every arm**; **the standing series does not move** (`tools/_t6_series_arms_final.json`: every
arm reproduces HEAD's `BASELINE_SERIES`; on that loop the scalar's seam is read 180 times with 139
raises, one cool and three beats, the ulcer's 3,427 times with 145 bites, the letters' predicates
never hold — no re-pin, no re-link). **The scalar ALONE moves every ambient seed, by the
`awakening_events` column and nothing else** — no war column, no elimination, no capture moves; 25
beats across the ten seeds: the FRENCH people stir on every seed (turns 25–33 — the idle France
loses 5–18 home provinces to the coalition) and rise on seven (32–41); the Bavarians stir on seven
seeds (36–41: Munich and Swabia under Austria, two provinces at +1 a turn) and quieten on marengo at
41 (home rule — Austria's peace hands them back); no other people reaches 40 in forty turns (the
Kingdom of Italy's two provinces under Austria climb to about 31, Hanover's one under Prussia the
same — the bands are the pace, and the ambient board occupies little). **The ulcer alone moves ulm**
(`captures_outside_aim` 248 → 251 — Austria's corps bleed on risen French soil and the war's spread
captures shift) and no class; the supply bill rises on six seeds (ulm +3,522 men, wagram +1,085,
jena +345, friedland +287, historical +182, lodi +66; 1,190,952 → 1,196,439 across the ten, +0.46%),
the French bill unchanged (an idle France is never an occupier), Austria's +5,152, Spain's +260,
Russia's +75 — the invaders of a risen France. **The letters move nothing ambiently** (the idle France
holds no stirring people's soil). The totals: `annexations_outside_aim` 0 on every arm; the tables
turn 26 times; the Alarm's guarantees 10, honoured 6; last refuges 22; `rank_promotions` 0 on every
seed (the raised gate's second clause unmet, as reported); the eliminations column the Kingdom of
Italy alone on all ten (the third clause unmet). **The AI-France harness** (`tools/
_t6_chain_d_2026_11_10.json`): arm 0 reproduces session B's arm ALL on its keys; the scalar alone
moves no world-line but the column — Austria's people stir on every seed at 19–21 and rise at 29–31
(the march holds six and more Austrian provinces from turn 10, +3 a turn), Russia's stir on eight
seeds at 26–30 and rise at 36–40 (the Estonia road; on eylau and friedland the march never reaches
Estonia and Russia's people never stir); **the ulcer moves austerlitz and eylau** (France's final
provinces 47 → 48, 34 → 36; its captures 29 → 31, 11 → 13 — re-routed world-lines), the Estonia
turns unchanged on every seed, France's supply bill 499,833 → 488,612 (−2.2%: up on friedland,
marengo, ulm and wagram, down on austerlitz, eylau, jena and rivoli, unchanged on historical and
lodi). **The march does not visibly bleed — said plainly:** the ulcer taxes the CAP, a corps under
the reduced cap pays nothing, and the AI-France's corps crowd on risen soil late and briefly; §5's
done-when ("the AI-France march to Estonia bleeds") is NOT met as written, and the lever is below.
The harness's France received neither letter: the desk's own rules (RE §7 — the pick by the
longest-standing premise, the crowding past grace, the cooldown re-armed) seat a people's
late-arising stir behind the bills that have stood longer. The AI courts' annexations 0 on every
arm; France's own entry 178 → 181 (reported, never gated). **The letters' reach** — the pacing chain
re-recorded (the deck changed: `tools/_s14c_sweep_final.json`, `tools/_affairs_first_arrival.json`):
on the 53 measured arms *The People Stir*'s premise never held on 52 (the commanded arms end with
France's 28 boot provinces and hold no foreign soil; the passive runs' France is idle; the Danube
script returns Austria's soil at its peace) and held one morning on the hand-played DDB-25 conquest
board; *The Ulcer*'s never — no measured arm holds a people's soil fourteen turns; the frozen-board
pin is the letters' proof. **The pacing record moved — attributed, not assumed:** forty-eight of the record's fifty-five arms read different letter timings against the November 7 record (T0-H's, the last run). The attribution arms (`tools/playtest_runs/t6_pacing_2026_11_10/attrib_*`: the commanded and accept families and the 21 sweep runs under the Awakening's seams) read the Awakening out of it — with the scalar and the ulcer held down and the letters up, every row reproduces the shipped record row for row; with every seam down, or the letters alone down, the rows differ by the two letters' "held out" label alone; the Throne road at austerlitz ends at 36 against its control's 40 on the letters arm with every Awakening seam down too. What moved is four tiers of world-lines since November 7 — the seed, the Questions' envy, the Alarm, the seat, the terms — read by the pacing record for the first time because the deck change forced the re-record; the pins that read its seeded figures are re-seated to the record's truth with that cause (`test_affairs_reach.py`, `test_affairs_pacing.py`, `test_moments_pacing.py`, `test_vp1_the_decisive_peace.py`; the road record `tools/_vp1_road_arms_final.json` re-recorded from the same armed run, T0-H's kept as `tools/_vp1_road_arms_2026_11_07.json`). One chain correction, recorded: Road I answered runs with `--moment accept --affair accept` (the measure tool's own form — the copied au4 chain lacked `--moment accept`, and the Crown read "declined" on the accept arms until it was restored). **The levers for the user, reported and none pre-recommended
(§0):** (a) the ulcer's teeth — a tax on the cap bites crowded corps only; a flat attrition on risen
soil ("every convoy needs a brigade") would bite a lone corps too — session D's option if wanted;
(b) the desk's seat for a people's rising — RE §7's ruled pick seats it behind the standing bills; a
crisis-class priority, or the letters recast as causal moments anchored on the beat, would bring it
forward — RE's design, the user's call; (c) the bands' pace on the ambient board (two provinces at
+1 a turn: Bavaria stirs at 36–41, the Kingdom of Italy never in forty) — N-DY4's numbers, tuneable.

### §5b The session D landing record — DY-5 the levée, the client dial, the interplays, The Nation in Arms (✅ LANDED November 10, 2026 — TIER 6 COMPLETE)

**Nothing new was ruled at the head** (the prompt pre-decided it; the user's word "code commit push"). Five rules
behind their own zero-arg seams (`tests/_t3_seams.py` rows T6-LEVEE, T6-DIAL, T6-REVANCHE, T6-LIBERATORS, T6-ARMS),
ONE sweep with six arms on three surfaces (`tools/_t6b_measure.py`: 0 / LEVEE / DIAL / REVANCHE / LIBERATORS /
ALL), the pacing chain re-recorded (the deck changed), the standing series (`tools/_t6b_series_arms.py`), ONE
commit. The rules in full: `SYSTEMS_REFERENCE.md` §204; the pins `tests/test_dy5_the_tiger_ridden.py`.

**DY-5 as built** (`backend/game_logic/awakening.py`, the DY-5 half):
- **The liberation levée** (`the_levee_rises`; `levee_holds`, `levee_terms`): a court ≥ `stirring`, AT WAR, home
  soil contested (the last tick's derived count — the store's figure, never a scan) regenerates infantry ×1.5 and
  prices the DRAFT ×0.75 — ONE read at `get_manpower_regen_rates` (after the war exhaustion, before the laws) and at
  `_recruit_cost_terms` (after the doctrine's term, before the laws; the AI's P1 rung reads the same pricer, the
  substitute market never does); the player's house like every court. **The National Guard** (the third letter's
  Accept) doubles it (×2.0 / ×0.5) for a term of 3–12 mornings (the row's `guard`), read only while the levée holds.
  **A beat** — ONE `levee` log row (raised / stood_down / guard; the census 184 → 185) and a HIGH dispatch line, in
  words; the tick settles the levée AFTER the scalar's move. The court row gains `levee` and `guard`; `to_dict`
  gains no line.
- **The client dial — the tiger ridden** (`the_tiger_is_ridden`; `client_dial`, `rebellion_cause`): an awakened
  client's loyalty −2 a turn at autonomy ≤ 1, +1 at autonomy ≥ 2 — ONE read for the tick (the term named), the
  forecast (`awakening_drift`) and the debug breakdown; a rebellion of an awakened client names its cause on every
  exit (`vassal_broke_free.cause`, the dispatch line's second sentence, the one-liner). **The boot-web boundary
  (§5a C2) needed no new rule:** a court subjugated later keeps its boot house, so its new lord's garrisons raise
  the count and the dial reads the same scalar (Spain under Joseph); a boot client's soil under its lord is home;
  a client re-vassalized by its boot lord reads home again — pinned.
- **A risen people's revanche** (`a_risen_people_swears_revanche`; `risen_grievance` in
  `emergent_designs.process_emergent_designs`): a court at `risen` promotes its grievance with ANY lost homeland —
  the partition bar waived; the event carries `cause: awakening` and the words "The people have risen, and the court
  swears what they demand." only where the rising was the deciding clause.
- **The liberators hold together** (`liberators_hold_together`; `friction_eased`, `coalition_friction_step` in
  `coalition.apply_coalition_friction`): while the league's target holds an awakened people's soil, the members
  fray 1 a turn instead of 2.
- **The Nation in Arms** (`the_nation_writes`, row DY-5 of `affairs.SINCE_ROWS`): predicate `nation_in_arms` (the
  lord's own people at `risen`, at war, home soil contested, the Guard not standing; the enemy house holding the
  most of the homeland bound as `host`); Moncey writes; Accept "Arm the National Guard" 800 gold, an action, the
  `national_guard` op (`turns` 6 — the thirteenth op, 12 → 13, Accept-only, no court, refused while the Guard
  stands); Decline "The line will hold" authority −3 / −4 / −5 — **`bites: "floor"`**, the validator's rule for an
  authority-alone Decline (clamped it would cost nothing), so the letter is silent on a bled board; the frozen
  board: the people stir and the levée rises at the 15th morning, risen at the 25th, the letter at the 30th, the
  Accept lifts France's infantry regen 3,750 → 5,000.
- The third interplay named in §5 — an unrecognized crown on awakened soil drifts worse — is DY-7's (Tier 8).

**The session landed (the record `SYSTEMS_REFERENCE.md` §204; the pins `TestTheSessionDMeasure`).** Arm 0 reproduces session C byte for byte on both surfaces; the band 28 / 27 / 26 on every arm; classes 10 of 10 on every arm; the series unmoved. **Every DY-5 seam bites where its condition holds and not one measured world-line moves in forty turns:** the levée rises on every ambient seed (France's at 25–33 under the coalition's garrisons, Bavaria's on five seeds at 36–41, fifteen beats) and on eight harness seeds (Russia's at 26–39; Austria's never — erased by turn 11, and a levée needs a standing court) — but the idle France recruits nothing, Bavaria's levée comes with turns to spare in single figures, and Russia's last recruit falls before its levée rises; the dial, the revanche and the liberators' ease never bite on a measured arm (no client awakened, no AI court at `risen`, the idle France holding no awakened soil); the pacing record re-recorded with no arm's timings moved and the road record standing; *The Nation in Arms* arrived on the scripted France alone (T38, grip 100 — "Authority 100 → 97") and was never due on seventeen arms whose premise held: the floor, the idle France's grip at 22. The raised gate: clause 1 MET (10 of 10), clauses 2 and 3 UNMET (no crown, the Kingdom of Italy alone on all ten) — Tier 8's.

**Levers for the user, none pre-recommended (§0):** the letter's floor (a second Decline price is the honest road to `"clamp"`); the levée's reach (an AI rung that recruits MORE while the levée holds); the dial's ambient road (no AI court vassalizes another ambiently); session C's three stand.

---

## §6 Crowns & Recognition (DY-6 and DY-7 — Tier 8, the pre-deploy marquee, after §5)

> **The gate record §6a (✅ RULED November 10, 2026), the session E landing record §6b (DY-6 ✅ LANDED) and the session F landing record §6c (DY-7 ✅ LANDED — TIER 8 COMPLETE, Tier 7 evaluated) follow this section.**

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

### §6a The Tier-8 gate record (✅ RULED November 10, 2026, at session E's head)

**The user's word at the head**, verbatim, on the prompt that listed the five questions in one
batch (the §2b idiom): **"code commit and push what it tells you is next"** — a delegation, the
session-C precedent ("rule yourself be rigioprous make it good"). The calls below are Claude's
under it, each one line to reverse; the readings honest, nothing pre-recommended where the
prompt said the taste was the user's.

**Q1 — the crowns that may be erected: THE AUTHORED LIST, inside ONE catalogue.** A crown is a
`formable_nations` template that carries a `crown` sub-block — never a second catalogue (the
`create_client` term, its eligibility predicate, its ratify arm and its bilateral carry are ONE
body already; a parallel `crowns` block would have re-earned every NA-6c review). The block
authors the royal style (`title`) and the houses whose AI may erect it at its own peace
(`ai_carvers`; the player's hand is free among the authored crowns — GR5); the first province
listed is the seat (the catalogue's standing convention — no `seat` key). The authored list
keeps the historian test (no state the era could not have made); D7's principle — content
reviewable in the file, validator-clamped (`_validate_crown_block`: `title` ≤ 60, `ai_carvers`
known nations WARN / repeats ERROR, `since` the authoring slice, an unknown key ERROR). **Six
crowns authored for 1805, each ONE court's soil:** the Kingdom of Naples (Naples — a one-province
court: "the dynasty has ceased to reign", the decisive-score road), the Kingdom of Westphalia
(Hanover's Brunswick / Westphalia / Osnabruck / Hanover — the seat Brunswick), the Kingdom of
Hungary (Austria's Hungary — the Schönbrunn proclamation of 1809, "elect a king of your own
choosing"), the Illyrian Provinces (Austria's Carniola and Croatia — the seat Laibach; the style
Marmont held, "Duke of Ragusa, Governor-General of Illyria"), the Grand Duchy of Finland
(Sweden's Finland — the Diet of Porvoo, 1809; `ai_carvers` Russia), the Duchy of Milan (the
Kingdom of Italy's Milan — the Habsburg duchy restored; `ai_carvers` Austria). Six original
flags in the set's style. The four plain carves (the Duchy of Warsaw, Normandy, the Roman
Republic, Ireland) stay crownless, byte-identical — Warsaw's duke was the King of Saxony, a crown
given to a reigning king, neither a marshal's throne nor a prince's (a block was drafted and
withdrawn the same session: it would have put the IGR-D fixture's Proclamation card one line
over the fold at UI scale 2.0 for no history gained).

**Q2 — the marshal king: BOTH IN THE POOL.** Who may reign: a marshal of the carver's roster with
laurels — glory at or above `KING_MIN_GLORY` (3, jealousy's own laurels floor) in the window, or
the crown of glory itself; never the sovereign, a prisoner or a client's general — or a prince
of the Imperial house (the scenario's `crowns.princes`: Joseph, Louis, Jérôme; a prince reigns
in one place at a time, derived from the vassal rows, and may reign again where his crown has
fallen — Joseph went from Naples to Spain). **History with teeth — a crown costs you your best
sword:** the marshal is re-homed to the client's colours WITH HIS CORPS (the Army of Naples:
Murat took French divisions south; `doctrines.set_marshal_nation`, THE setter), seated at the
crown's seat, off the roster, the glory ladder (his glory satisfied permanently — the release
valve) and the petitions, the removal's hygiene paid (his reward rows, his standing question,
the orders aimed at him); the client's loyalty seeds from HIS TRUST (clamped 30–95 — crown your
trusted Davout for a loyal kingdom, your glorious Bernadotte for a shaky one); every marshal
with laurels passed over takes the authored grievance — envy toward the king (the ladder's own
grievance, `apply_jealousy` forced) and trust −5. **A prince costs no sword:** the client seeds
at `PRINCE_LOYALTY` 50 (the brothers were their own men — Louis went Dutch), and the passed-over
marshals' slight is the sharper, trust −8 (the blood over the sword — Murat's fury when Joseph
took Naples first); a prince is no object of a marshal's envy. A regency where no king is
named (loyalty 60, the carve default). The AI's crown seats nobody — a regency.

**Q3 — the AI's road: YES.** The same guided term in the AI–AI peace writer: the victor's AI
erects an authored crown out of the soil its aim's terms cede — the first crown of the
catalogue whose `ai_carvers` name the winner, every province the loser's and all riding this
treaty's cessions, eligible by THE predicate (`evaluate_create_client_eligibility` — never a
second rule); those cessions become ONE `create_client` clause (the title; a regency) on both
aim roads (`attempt_aim_held_settlement`; the pair exits' lock through `_cede_the_held_aim`).
Bounded by the authored crowns and by the Alarm (a carve alarms Europe like a capital taken —
`ALARM_CAPITAL` 12 on the carver's house slot, the player's included: the coalition's threat).
**The honest reading before the sweep:** the 1805 board's ambient AI peaces are Prussia's over
Hanover (annexed in 1806, no crown) and the courts' Russian and Austrian crowns (Finland, Milan)
wait on wars the idle France never frees them to fight — the AI road's live case is the
player's own road (a peace with Russia, then Finland), and clause 3 stays content's to earn
unless the sweep says otherwise (§6b).

**Q4 — recognition's price: THE SHAPE RULED, THE TEETH DY-7's (session F).** The scenario's
`crowns.recognition` block names the legitimists (Austria, Russia, Britain) and the condition
(`until: "beaten"` — the closed set DY-7 reads); the crown's row carries `recognized_by` (empty
at erection); `crowns.withholding_courts` reads them; DY-6 SPEAKS the list on the Proclamation
card ("Austria, Russia and Britain withhold recognition of the crown") and nothing bites yet —
owner row DY-7, landing slice session F, done-when: the table's malus with a withholding court,
the client's trade with it halved, the dial −3 on awakened soil (the §5 interplay), the
Congress's grant, a grant or refusal a beat; test `tests/test_dy7_recognition.py`.

**Q5 — recorded, not re-opened:** Tier 7's bounded dice are built at F ONLY if the story-class
count falls short of 6 after DY-6 and DY-7; a clause still unmet after F goes to the user with
NO default (§7).

**Census corrections — what the survey found that §6 did not know:**
- **C1.** The `create_client` term was already first-class and guided end to end (NA-6c/NA-6d,
  July 2026: the row, the add verb, the eligibility predicate, the ratify arm, the Formables
  page, IGR-D's bilateral carry). "Promoted to a guided term" meant the CROWN's teeth on it, not
  the term.
- **C2.** Naples is a ONE-province court on the drawn map (no Sicily), so the Kingdom of Naples
  is a total-annexation carve: the Bourbon court is erased by the treaty — a crown falls by
  treaty, never by the sword alone (T4-2's law kept) — and the Neapolitan PEOPLE live on in the
  Awakening's store (an erased court's people keep their scalar; §5a) and count the new crown's
  soil foreign under the French house (the Calabrian insurgency by machinery).
- **C3.** A carved client's boot house was never written into the Awakening's web — its own
  people would have counted their own soil occupied under the lord that made them. The sibling
  fix lands with DY-6 for EVERY carve (`awakening.adopt_court`): the new court's house is its
  carver; the carved people keep THEIR boot house. Unseamed — no measured arm carves — and
  pinned.
- **C4.** The Formables page keyed a flag per template; six new SVGs and their `.import`
  sidecars ride `git add -f` (the ignored `assets/`), credited in `THIRD_PARTY_LICENSES.md`.
- **C5.** The gift's own pin (DY-1f) crafted the AI road's live case — Russia's aim peace on
  Sweden with Finland delivered; re-seated with the crown's seam held down, with cause; the
  crown's reading of that board pinned in DY-6's file.

### §6b The session E landing record — DY-6 the crown erected and the marshal king (✅ LANDED November 10, 2026)

**The gate ruled at the head under the user's delegation (§6a).** Three rules behind their own zero-arg seams
(`tests/_t3_seams.py` rows T8-CROWN, T8-KING, T8-AI), ONE sweep with four arms on three surfaces
(`tools/_t8_measure.py`: 0 / CROWN / AI / ALL), the standing series (`tools/_t8_series_arms.py`), ONE commit. The
rules in full: `SYSTEMS_REFERENCE.md` §205; the pins `tests/test_dy6_the_crown_erected.py`.

**DY-6 as built** (`backend/game_logic/crowns.py`; the seams' sites in `formations`, `settlement_actions`,
`settlement_staging`, `settlement_third_party`, `world_state.from_dict`, `save_manager`):
- **The crown** (`a_crown_is_erected`): the `crown` sub-block on the ONE catalogue (six crowns; `_validate_crown_block`);
  the teeth at the one apply site — the title and `recognized_by` on the row, the boot house written for EVERY carve
  (`awakening.adopt_court`, the C3 sibling fix), the Alarm's 12 on the carver's house, the beat (`nation_formed` + `crown`
  / `king` / `reign`; the dispatch `crown_erected`; the card's lines; the one-liner); the Formables page names the
  throne; seam down the crown templates are struck at load (`strike_crowns`, `since: "DY-6"`) and no store is installed.
- **The marshal king** (`a_marshal_may_reign`): `king_candidates` (laurels ≥ 3 or the crown of glory; the princes of
  the store); the guided row's `king_options` / `king_labels` / `terms_display`, the confirm popup's picker, the add
  verb's `king` through `stamp_king_on_clause` (the refusals in words); `enthrone` — the marshal re-homed with his
  corps to the seat (THE nation setter), the removal's hygiene, loyalty = his trust (30–95), the passed-over's
  grievance (envy toward the king + trust −5), a prince at loyalty 50 (trust −8, no envy); a regency otherwise.
- **The AI's road** (`a_victor_erects_a_crown`): `erect_a_crown_in_the_terms` on both aim roads — the first authored
  crown the winner's house may erect, its soil all among the treaty's cessions, eligible by THE predicate, becomes
  one `create_client` clause (a regency); `_cede_the_held_aim` returns it, `_ceded_regions` keeps its soil from T3-6's
  evacuation, `_consequence_line` speaks it.
- **The `crowns` block** (the princes, the recognition rule) in `world.moments["crowns"]` — `install`, `backfill`,
  the sibling carry; `withholding_courts` and the card's line are DY-6's words, the teeth DY-7's (session F).

**The session landed (the record `SYSTEMS_REFERENCE.md` §205; the pins `TestTheSessionEMeasure`).** ONE sweep, four arms (0 / CROWN / AI / ALL) on three surfaces (`tools/_t8_measure.py`), the standing series (`tools/_t8_series_arms.py`), run alone. **Arm 0 reproduces session D byte for byte on both surfaces** (the ten ambient signatures and the census's every total; the harness on session D's keys), the band 28 / 27 / 26 and story classes 10 of 10 on EVERY arm, the series unmoved on every arm with the crown's and the AI road's seams READ on the rig (2 and 1 a run) and no carve on it. **Said plainly: the seams are reached on every arm and NO crown is erected on any measured arm in forty turns** — the ambient board's AI peaces are Prussia's over Hanover (no crown authored for Prussia: 1806 annexed it) and the crowns the courts may erect (Russia's Finland, Austria's Milan) wait on wars the idle France never frees them to fight; the harness France's wars are the player's, which the AI–AI road never runs; the scripted France authors no carve. The harness record gains the `formations` column (the Class T dreams the march lets form — Holland's on four seeds, the Kingdom of Italy's on six — on every arm alike; none a crown). **The crown's proof is the test file's crafted boards:** Naples under Murat end to end through the guided terms (the row offers the throne, the verb stamps the king, the applier re-homes him with his 22,000, the loyalty his trust 75, Ney envious and −5, the Alarm +12, the Neapolitans counting the crown's soil foreign, the beat and the card), Joseph's Naples (loyalty 50, Murat −8), the regency, and Finland under Russia on both AI roads (the aim peace and the lock). **The raised gate:** clause 1 MET (10 of 10); clauses 2 and 3 UNMET (no crown taken; the Kingdom of Italy alone on all ten, no ambient formation) — session F's reading (DY-7, Tier 8's close, Tier 7 evaluated), then the user's with no default (§7).

**Levers for the user, none pre-recommended (§0):** (a) **the AI road's ambient silence** — a crown for Prussia's Hanover peace (ahistorical; or a North German client) would put a formation on every seed and vary nothing; the honest road to clause 3 is a court whose war the idle France does not own — the content levers of §4a (a second great-power war) carry it; (b) **the marshal king's corps** — the whole corps goes with him (the Army of Naples); a royal guard of a fixed size with the rest returned to the depots is one line; (c) **the prince's loyalty** 50 against a king's trust — the brothers as a cheaper, shakier crown; (d) session D's three and session C's five stand.


### §6c The session F landing record — DY-7 Recognition, Tier 8's close, Tier 7 evaluated (✅ LANDED November 10, 2026 — TIER 8 COMPLETE)

**Nothing new ruled at the head** (the prompt's word: the shape §6a Q4's, the numbers N-DY7 tuneable). Two rules behind their own zero-arg seams (`tests/_t3_seams.py` rows T8-RECOG, T8-PRICE), ONE sweep with three arms on three surfaces (`tools/_t8b_measure.py`: 0 / RECOG / ALL), the standing series (`tools/_t8b_series_arms.py`), ONE commit. The rules in full: `SYSTEMS_REFERENCE.md` §206; the pins `tests/test_dy7_recognition.py` (43).

**DY-7 as built** (`backend/game_logic/crowns.py`, the DY-7 section; the seams' sites in `settlement_ratify`, `world_state._ratify_treaty`, `diplomacy`, `congress`, `settlement_scoring`, `awakening`, `ledger`, `diplomatic_ledger`, `diplomatic_advisory`, `campaign_log`, `dispatch`, `gazette`, the two Godot ledgers):
- **The legitimists withhold** (`the_legitimists_withhold`): the condition `until: "beaten"` read at the peace chokepoints — a legitimist that signs a peace as the LOSER with the house of a crown's lord recognizes it (`note_peace_signed`: the loser is the court whose burden under the clauses is the greater, `peace_loser`, the DEMANDS dialect that knows every type; a white peace beats nobody). The three signed roads call it — the common peace's record (`_record_common_peace_treaties`: the table and the AI's third-party ratify, a truce excluded), the bilateral ratify (stage 6, after the carve of stage 5 — the crown this very treaty erects is recognized by it: Pressburg recognized the Kingdom of Italy), the dictated truce exit (the sibling, Rule 10); `recognized_by` on the row is the record, never a scan. **The Congress grants** (`congress_grants`, beside `questions.congress_rules` in the sitting's tick): every withholding legitimist among the great powers that answers the Congress RECOGNIZES (its treaty latch) or is GONE into the Emperor's house grants the Emperor's crowns; on the sitting's last tick a court that REFUSES the Congress refuses the crown — once a sitting (`recognition_refused[court]` = the summons turn; a later Congress asks again); a shut-out or suing court has not answered and keeps withholding. The Congress is the Emperor's instrument — an AI house's crown is recognized by the peace that beats a legitimist, never here. **The beat:** ONE log row `recognition` (the census 185 → 186 — the seventeen pins and `test_iq7`'s rationale moved together; family diplomacy, the lead tier, court knowledge, the Gazette's court types), a HIGH dispatch line (`{line}`, a `courts_treaties` row of 88), the words by the courts' seats and never a figure: "Vienna recognizes the Kingdom of Naples and its crown, by the peace that beat her." / "The Congress recognizes the Kingdom of Naples: Vienna acknowledges its crown." / "Vilna and London refuse the Kingdom of Naples its crown — the Congress rises without their word." (Russia's seat on the drawn map is Vilna — the Alarm's own naming.)
- **An unrecognized crown pays** (`an_unrecognized_crown_pays`), the AI's crowns the same (GR5): **at the table** — `crown_recognition`, a component on the settlement scorer (step 12d, the bond's seat) and on the bilateral formula: −5 for each crown of the proposing side's houses the court withholds, capped at −15 (`table_component` / `bilateral_component`; the label "A crown unrecognized", the spoken blocker "they do not acknowledge the crown our house has raised", the feedback strings; the three component-set pins re-seated with cause); **in trade** — the LORD's trade with each withholding court halved (`trade_loss` at `process_trade_income` beside the blockade's arm; one halving a court however many crowns; the Strategic Ledger's signed "Recognition" Net component — `NET_GOLD_COMPONENTS`, the economy report's line, `strategic_ledger.gd`; the cross-file tripwire re-pinned). **The spec's letter said the client's income: a vassal pair trades nothing in this engine (tribute replaces trade — `calculate_trade_breakdown` skips every vassal pair), so the client's rows are an empty set and the price would have been a promise with no teeth. It falls where a crown's trade price can be felt — on the house that raised it; the user may move it back or strike it, one line each.** **On awakened soil** — the client dial's −2 becomes −3 while unrecognized (`dial_extra` in `awakening.client_dial`; the label "the people's awakening — the crown unrecognized"; the tick, the forecast and the breakdown share the read).
- **The words:** the Diplomatic Ledger's nations tab — a crown client's row names the title, who reigns and who withholds (`crown`), a legitimist's row names the crowns of ours it withholds and the price (`recognition`; both rendered by `diplomatic_ledger.gd` under the Laws and Doctrine lines); the Vassals card's `crown_line`; Talleyrand's counsel on the advisory (`counsel_line`, a reading in his register — "Vienna does not acknowledge the Kingdom of Naples, Sire — she prices every peace we put to her for it (−5) and trades with us at half, until she is beaten or signs at a Congress."); the Proclamation card (DY-6).
- **Found on the way (a sibling, unseamed and pinned — no measured arm carves):** a carved client's dial read only its OWN Awakening row, which is empty — the carved people's scalar lives under the court they were carved from (§5a C2: the Neapolitans under "Naples" while the Kingdom of Naples reigns over them), so the people a crown sat on could rise without its dial ever moving. `awakening.client_people_level` reads the higher of the two (`carved_from`) for the dial and the rebellion's cause.

**The session landed (the record `SYSTEMS_REFERENCE.md` §206; the pins `TestTheSessionFMeasure`).** ONE sweep, three arms (0 / RECOG / ALL) on three surfaces, the standing series, run alone. **Arm 0 reproduces session E byte for byte on both surfaces** (the ten ambient signatures and the census's every total; the harness on session E's keys); (the hook's first run then added the driver's `recognition` Net display column — a digest column no record reads — and made the beat's `log_event` a literal for the Gazette's census; neither touches a measured value); the band 28 / 27 / 26 and story classes 10 of 10 on every arm; the series unmoved on every arm with the price's seam read on the rig (8,256 table reads a run, the peace chokepoint once) and nothing to bite. **Said plainly: no measured arm erects a crown (session E's reading stands — the AI road's live case waits on wars the idle France never frees the courts to fight, the harness France's wars are the player's, the scripted France authors no carve), so nothing is recognized and no price bites on any arm — the recognitions column reads 0 everywhere and the three arms are byte-identical.** The §6 done-when's last clause ("`formations` stops reading none on seeds where a crown rises") is conditional and no seed rises a crown — reported, not claimed. **The teeth's proof is the crafted boards:** Naples under Murat withheld by Vienna, Vilna and London — Austria beaten by a gold peace recognizes it (the common peace's record, the bilateral ratify after the carve), the Congress's grant on the first tick and the last tick's refusal once a sitting, the table −5 / −10 / −15 capped on the scorer and on the formula (the control with the seam down: +5 on the score), France's open-borders trade with Austria halved and shown in the ledger, the dial −3 and −2 again when all three recognize; Russia's Finland pays at Vienna and is recognized by the peace that beats Austria with Russia's house.

**Tier 8 ✅ COMPLETE. Tier 7 evaluated (§7; Q5 of §6a — a rule, not a question):** the story-class count after DY-6 and DY-7 reads **10 of 10** → clause 1 MET by margin, **the bounded dice are NOT built**. **Clauses 2 and 3 — UNMET on every record since Tier 4** (no `rank_promotion` on any seed; the Kingdom of Italy alone on all ten, no ambient formation) — **go to the user as an explicit question with NO default** (§0's standing rule; §7). The content levers, none pre-recommended: §4a's (a second great-power war on the 1805 board — the courts' crowns and their promotions wait on wars the idle France never frees them to fight), §6b's (a) (the AI road's ambient silence), the promotion crowns' six-turn hold (`SYSTEMS_REFERENCE.md` §201), the levée's reach (§5b). The deploy (session G) may proceed with the gate read as it stands, or wait on content — the user's call, no default.

**Levers for the user, none pre-recommended (§0):** (a) **the trade price's seat** — on the lord's rows (built; the only rows a crown's trade price can reach) or struck; (b) **N-DY7** — −5 a crown, the cap −15, the trade factor 0.5, the dial's −1; (c) **the Congress's grant** — the courts that answer RECOGNIZES (built) or every sitting great power whatever its answer; (d) session E's four, session D's three and session C's five stand.


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
§0) — 0 open GR rows, the story-class clause below with the historian test green on every
seed, `annexations_outside_aim` 0 (amended at T3-6), France band 23–28. Whether the
story-class GATE should RISE now that the Awakening and the Crowns ship pre-deploy was
the question for Tier 6's head, put to the user with NO default marked (the reading as it
stood: ≥ 4 of 10, the post-Awakening reading — ≥ 6 of 10, at least one seed with a minor at
secondary rank, the eliminations column varying — an aspiration, not a gate; one line of
color, not a gate's evidence: T0-E/F/G's after-sweep hand-grouping read 10 of 10 story
classes on the war columns alone, `SYSTEMS_REFERENCE.md` §182.5 — DY-0's own signature is
the instrument).

**✅ RULED November 10, 2026 at session C's head — THE GATE RISES** (put to the user with
no default; the user's word, verbatim: *"rule yourself be rigioprous make it good"* — the
ruling Claude's under that delegation, approved with the plan). A gate at 4 while the
record has read 8–10 on every tier since Tier 2 is a gate that cannot fail, and a gate
that cannot fail is not a gate. The post-Awakening reading becomes THE gate, each clause
tied to an instrument column and an owner:

1. **story classes ≥ 6 of 10** (`story_class_count`) — margin below the measured 10,
   above Tier 3's honest 8; MET today;
2. **at least one ambient seed with a minor at secondary rank by promotion**
   (`rank_promotions` non-empty on ≥ 1 seed) — the user's own words made a gate
   (*"sometimes even minor powers get big"*); UNMET today on every seed (no crown taken,
   sessions A and B); owners: session D's levée (a court at war on contested home soil
   keeps its ground), Tier 8's crowns, session B's content levers (§4a's landing note); **session D read it UNMET on every seed
   (§5b) — the levée moved no roster; Tier 8's;**
3. **the map's roster varies** — at least two distinct (fallen courts, formed states)
   readings across the ten seeds (`eliminations` ∪ `formations`): Tier 8's own signature
   ("the map gains states history gained") folded in — the honest reading of the user's
   "cool maps arise" where "the eliminations column varying" alone fought T4-2's own
   design (a crown falls by treaty, never by the sword alone); UNMET today (the Kingdom
   of Italy alone on all ten seeds, no formation); owners: session D's levée (a client at
   war on its own soil may hold), Tier 8's formations. **Session D read it UNMET (the Kingdom of Italy
   alone on all ten, no formation — §5b); Tier 8's.**

Tier 7's bounded dice may satisfy clause 1 alone and never 2 or 3; they are built only if
the count falls short of **6** (variance must first be earned by content, dice are the
last resort and stay bounded by pin 14). A clause still unmet after session F goes to the
user as an explicit question with NO default — never a silent cut (§0's standing rule).

**✅ SESSION F'S READING (November 10, 2026; §6c):** clause 1 **MET** — 10 of 10 after DY-6 and
DY-7, so Tier 7's bounded dice are NOT built; clauses 2 and 3 **UNMET on every record since
Tier 4** — no `rank_promotion` on any seed, the Kingdom of Italy alone on all ten seeds and no
ambient formation (no crown rises on the measured arms: the courts' crowns and their
promotions wait on wars the idle France never frees them to fight). **THE QUESTION IS THE
USER'S NOW, WITH NO DEFAULT:** deploy with the gate read as it stands, or earn the clauses by
content first — §4a's second great-power war, §6b's (a), the promotion crowns' six-turn hold
(`SYSTEMS_REFERENCE.md` §201), the levée's reach (§5b). Put beside session G, the deploy.

**✅ EARNED November 11, 2026 — SESSION G (the user's "Earn them first"; the record §7a):** on the
shipped tree's ambient record (`tools/_dy_signature_gate_2026_11_11.json`) clause 1 reads 10 of 10;
clause 2 is MET — Hesse at secondary rank by the Grand Ducal Title on **lodi** (turn 33) and **marengo**
(turn 40); clause 3 is MET — the roster reads {Kingdom of Italy} on nine seeds and {Kingdom of Italy,
Papal States} on **wagram** (the Pope erased by the cast Naples at turn 31), two distinct readings. The
deploy gate stands met in full; the deploy is session H (§2b). No clause was lowered.

### §7a The gate earned — session G's landing record (✅ LANDED November 11, 2026)

**The user's word at session F's close, verbatim:** *"Earn them first"* — the content fork of §7 taken over the
deploy-as-read. One session, two rules behind their own zero-arg seams (`tests/_t3_seams.py` rows G-PACT, G-CHEST),
ONE sweep with three arms on three surfaces (`tools/_gate_measure.py`: 0 / PACT / ALL), the standing series
(`tools/_gate_series_arms.py`), ONE commit. The rules in full: `SYSTEMS_REFERENCE.md` §207; the pins
`tests/test_session_g_the_gate_earned.py` (19). Drafted in Plan Mode and approved.

**The diagnosis (two read-only explorations of the gates and four in-process probes of the ambient seeds, before
anything was built).** The unattended board's France signs nothing for forty turns, so the Third Coalition war never
ends: every belligerent court is `busy` (a court at war opens no second design war), Austria holds her Italian aim
and waits on a letter nobody answers, and every built road to a formation or a promotion runs through that peace —
Russia's second shore (the quiet window, T2-4), Prussia's Pomerania (the corridor, T2-5), the Emperor's gift
(DY-1f), Austria's Duchy of Milan (the Kingdom of Italy falls by capture; the player's client never signs). The cast
understudies are the one road the idle France does not own: Denmark (austerlitz, lodi) reaches `fight` but Sweden
outgrows her (12,000 → 76,000 against Denmark's 47,747 — the force gate holds, rightly); Saxony (Posen against
78,000) and Sardinia (no army) cannot win. **Two things stood in the roads left, and neither was a mechanic missing:**
(1) **the pact with the coveted** — an AI court signed a DEFENSIVE ALLIANCE with the very court whose province its
live design covets, the ally clause (`agendas._held_by_an_allys_bloc`) then read the province as not coveted, the
design read SATISFIED and the crisis passed with the words "the want is won" (false): the cast Naples with the Pope
at turn 3 on jena and wagram (her Roman Expedition defused by her own diplomacy — exactly what T2-6's live-first
ruling said being cast must not mean), Hanover with Hesse at turn 16 on marengo, one turn after Hesse's final
demand; (2) **the purse bar of a crown** — the AI's bar for any law is price + `AI_PURSE_RESERVE` 1,000 + five turns'
upkeep, 4,500 for a 3,000 promotion law on a court booting at 800.

**The rules as built.**
- **G-PACT — a court swears no alliance with the court it covets** (`ai_diplomacy.no_pact_with_the_coveted`): no
  defensive alliance or alliance between two AI courts while either's live acquire design covets a province of the
  other — the holder itself or the house it serves (`pact_with_the_coveted`, ONE read over `agendas.get_agenda_covets`
  and the holder's top overlord). The poll's gate: `_evaluate_ai_ai_proposal` now wraps the triggers
  (`_evaluate_ai_ai_triggers`) and returns None for a pact between a covetous pair; the recipient-addressed road's
  guard in `_resolve_ai_ai_proposal` returns the existing `ai_ai_proposal_refused` event with `reason: covets`. A NAP
  is untouched (the breach machinery prices it). No new log type, no new field.
- **G-CHEST — a crown is bought with the whole chest** (`reforms.a_crown_is_bought_with_the_whole_chest`): the AI's
  purse bar for a promotion law (`is_promotion`) is the price and arrears alone; every other law keeps the reserve;
  the Net test and the shared gate `law_refusal` stand. Two pins re-seated with cause (`test_dy1`'s rung buys at
  4,000 and waits at 2,900; `test_sf_lb2`'s caller census names the triggers' body).

**The session landed (the record `SYSTEMS_REFERENCE.md` §207; the pins `TestTheSessionGMeasure`).** ONE sweep,
three arms on three surfaces, run alone; the series beside it. **Arm 0 reproduces session F byte for byte on both
surfaces.** **Arm PACT alone moves four seeds** (jena, lodi, marengo, wagram; six byte-identical) and earns both
clauses: on **lodi** Hesse's crisis survives, she takes Westphalia (turn 25), Hanover signs the aim peace (26 —
"Hesse takes Westphalia. Hanover pays 2,250 gold."), the treaty title's six quiet turns pass and **the Grand Ducal
Title is enacted at turn 33**; on **wagram** the cast Naples asks the Pope thrice (4, 16, 27), opens her crisis at 27
(coerce — a defenceless prize), delivers the demand at 28, declares at 29, Damas storms Rome (10,000 → 5,000 →
3,500) and **the Papal States are erased at turn 31** — then the understudy's war runs on: Sardinia's Cagliari (32–33,
Sardinia signs at the last), a war on Austria (33), Piedmont, Lyonnais and Limousin plundered from Austria's hands
and Provence from Britain's (35–37), two retaken by Britain by 40; on **marengo** Prussia takes Westphalia (23),
Hanover signs at the last with Prussia (24 — Prussia evacuates it), Hesse takes it (25) and signs the aim peace the
same turn ("Hanover pays 243 gold") — her chest never reaches 4,500 inside forty turns; on **jena** Naples stands at
`fight` from turn 8 with two refusals (6, 18) and **Austria takes the Pope under her wing by a defensive alliance at
turn 23** (Austria covets none of his soil) — Naples outmatched, no crisis: the deterrence D5 means. **Arm ALL (the
shipped tree) adds marengo's crown:** with the bar at its price Hesse enacts the Grand Ducal Title at **turn 40** —
the chest rule's own seed. Story classes **10 of 10 on every arm**; `captures_outside_aim` 251 → 269 (the
understudies' wars), `annexations_outside_aim` 0, no crown erected, nothing recognized, the Awakening's beats 25 →
24.
*(Erratum, November 11, 2026, session G2 — §7b: that 0 is the AMBIENT record's. The harness's shipped arm read 2 —
the cast Naples keeps Milan and Piedmont on wagram, the soil of the Kingdom of Italy, the player's house's erased
client — and the reference record's "0 on both surfaces" was wrong; no pin held the figure. Corrected and pinned.)* **The France band:** 28 / 27 / 26 on arm 0, **28 / 27 / 25 on PACT and ALL** (the commanded middle arm moved one
province — inside 23–28, reported). **The harness (chain D):** arm 0 reproduces session F; PACT and ALL move six
seeds (friedland, historical, jena, lodi, marengo, wagram; `captures_outside_aim` 117 → 130), promote nobody, erect
no crown — reported, never gated. **The standing series does not move** on any arm: the pact's seam read 6,640 /
6,573 times on the rig, biting 105 times on PACT and ALL (the rig's pacts refused) with the series unmoved; the
chest's seam read 303 times, no promotion law reaching the bar there.

**The gate's reading (§7): clause 1 MET (10 of 10), clause 2 MET (Hesse on lodi and marengo), clause 3 MET (wagram's
roster differs) — EARNED, no clause lowered.** The deploy is session H.

**Levers for the user, none pre-recommended (§0):** (a) **the understudy's reach** — the cast Naples, Rome taken,
goes on to Sardinia and Austria and plunders the French soil Austria holds (her war with Austria has no authored
aim, so the conduct rule leaves her free; `captures_outside_aim` +18): a reading on a court at war without an aim;
(b) **the chest's number** — the price alone (built), or a half-reserve; (c) **the commanded middle arm** 26 → 25;
(d) **jena's Pope under Vienna's wing** — the deterrence working, or an understudy whose ask-ladder was one refusal
short (`REFUSAL_MEMORY_TURNS`); (e) session F's three, session E's four, session D's three, session C's five stand.


### §7b The played campaign — session G2's landing record (✅ LANDED November 11, 2026)

**The user's words, verbatim:** *"review to see if dyna mism worked and is fully done"*; then *"fix and playtest do full
session of fixing and real life testing make it workm and make it work well and when i say playtest i mean play well
see derivations see dynamism test like humna"*; and at the plan *"make sure ux and ui works for all of this too, things
dont need to be typed if they dont make sense like making someone kind for example should use ui! and how does it
impact marshals etc."* Drafted in Plan Mode and approved. The rules in full: `SYSTEMS_REFERENCE.md` §208; the pins
`tests/test_session_g2_the_played_campaign.py`; the seams `tests/_t3_seams.py` rows G2-RECOG / G2-ASK / G2-LADDER /
G2-BACKED; ONE sweep with four arms on three surfaces (`tools/_g2_measure.py`), the standing series
(`tools/_g2_series_arms.py`), ONE commit.

**The review's verdict, which opened the session.** The arc was built whole, every seam up, the gate's record
reproducible to the byte — and only its first half was shown to change a game. Three things the record had not said:
(1) **no measured France plays** — the ambient arm is idle, the commanded script fights thirteen turns and drills for
twenty-seven, the harness annexes Austria in a dozen turns and never signs; (2) the story-class clause read 9 of 10
BEFORE the tiers were built, so it cannot tell the arc from its absence; (3) the reference record of session G
misstated the harness's annexation line (§7a's erratum). So a France was played.

**The campaign (`tools/playtest_scripts/played_emperor.json`; `docs/audits/playtest_digests/played-emperor/`).**
Seed `distant-bivouac-95`, rolled for the session (Naples the understudy). Played turn by turn from each morning's
board: Mack taken at Ulm (1); Charles driven from Franconia (2–3) and broken in Bohemia (4); Kutuzov met before
Vienna and beaten three times (5–7); Bohemia, Tyrol, Carniola and Hungary taken; the table at 10 — the Kingdom of
Hungary demanded UNDER SOULT, the joint table set aside for the separate peace with Austria (London unbeaten),
Austria's counter of 2,800 gold accepted at 12; a peace with Russia at 16 that licenses her Finnish design; a
sponsorship of Prussia's Hanoverian Prize at 20; then the Emperor watches. **On session G's tree** that campaign read:
a regency for Hungary; Vienna, Petersburg and London all withholding (the −5 and the halved trade real at the next
table); the Austrian people stirring at 25; and from turn 17 to 30 **nothing** — Naples "prepared to go as far as
war" for Rome since turn 2, Russia licensed and unmoved, Prussia paid 4,000 gold and unmoved. **On this tree:** Naples
asks, is refused twice, opens her crisis at 11 and the Papal States fall at 18; Soult takes the crown at 12 with
14,571 men and Vienna recognizes it "by the peace that beat her"; the sponsorship opens Prussia's crisis on Hanover
the same turn, she declares at 23 and holds it by 25 (the German Question turns; Hanover's court removes to
Brunswick; Hesse opens her own crisis on what is left); Russia, licensed, puts her gold behind Prussia against Sweden
(25); the Austrian people stir (25), a league strikes France at 35, the levée rises, and Soult's kingdom falls to
Austria at 38.

**A second seed, the same first orders** (`played_occupier.json`, `distant-hussar-64`, Denmark the understudy):
Charles takes Munich on day three (the German Question turns; Prussia's word for Bavaria at 4), Massena is broken at
Milan, the client's general is taken — then John (5), Charles (6) and Liechtenstein (9) are prisoners, France holds
Tyrol, Bohemia and Carniola, and 45,000 Russians sit entrenched before Vienna; Prussia's Hanover crisis opens at 8
with no French gold behind it. Played by hand through turn 10. (Its unattended tail is not recorded as play: five
careless assaults with the Emperor in the column lost the army and the Emperor — the Fall of the Empire at 38.)

**The rules as built** (§208 has each in full).
- **G2-KING** — `settlement_staging._pair_substitute_seed_terms` carries `crowns.CROWN_CLAUSE_KEYS`. No seam.
- **G2-RECOG** — `crowns.the_war_names_the_beaten`: `war_loser` (the pair's score past 30, the ratification
  record's own bar) before the clause burden, at the three chokepoints; the ceding court recognizes the crown its
  treaty erects; the card speaks the reception as the treaty leaves it.
- **G2-ASK** — `ai_diplomacy.a_court_at_fight_still_asks`: the design ask at `fight` while the ladder is unclimbed.
- **G2-LADDER** — `ai_diplomacy.the_ladder_outlasts_the_rest`: the ladder gate reads 24 turns of refusals (T0-F's
  escalating rest had left it climbed six turns in eighteen).
- **G2-BACKED** — `intent.a_backed_design_dares`: `WEIGHT_BACKED_DESIGN` 10 on an acquire design a live sponsorship
  or licence aims at (ONE record, `world.directed_sponsorships`); never an aim in the player's house; said at the
  choice and on the Intent row. **The one rule that adds a mechanic — one line to reverse.**
- **The marshals' side** — the pick's price in words (`king_notes`, `king_footnote`), REIGNING on the Generals
  screen (`crowns.reigning_rows`), the rebel king named (`rebel_king_words`), the formation record keeping the
  crown's keys.
- **The screens** — the crown row's name opens the king list; the counter and the mailbox name the kingdom and its
  king; the status-quo review names a client's province once. Walked in the running client by clicking (38 actions,
  0 script errors): nothing in the slice needs typing.

**The session landed (the record `SYSTEMS_REFERENCE.md` §208; the pins `TestTheSessionG2Measure`).** ONE sweep, four
arms on three surfaces, run alone; the series beside it; the shipped arm re-run on the final tree, byte-identical.
**Arm 0 reproduces session G byte for byte on both surfaces.** **ASK moves jena and wagram** (the Papal States fall
on jena at 26 and on wagram at 17, not 31); **LADDER moves lodi; ALL moves lodi** (Denmark at `fight` from 13, an AI
backer's push). Story classes **10 of 10 on every arm**; `captures_outside_aim` 269 → 266; `annexations_outside_aim` 0
ambient; no crown, no recognition on a measured arm. **The band: 28 / 27 / 25 on every arm.** **The series does not
move**; on the rig the ladder's memory bites 14 times and the backing 10 (Russia behind Prussia against Sweden).

**The gate's reading (§7) on the shipped arm:** clause 1 MET (10 of 10); clause 2 MET (Hesse on lodi at 33 and
marengo at 40); clause 3 MET on TWO seeds (jena and wagram); the ambient annexation line 0; the band inside 23–28.
**The harness's annexation line reads 4** (jena and wagram: the cast Naples keeps Milan and Piedmont — session G's
tree read 2). Reported, pinned at what it reads, never gated, never again read as 0.

**Out of sample — six fresh rolled seeds, France idle** (reported, never gated; per seed, before → after):

| Seed | Understudy | AI wars | Fallen courts | Promoted | Formed |
|---|---|---|---|---|---|
| distant-bivouac-95 | Naples | 0 → 1 | Kingdom of Italy (10) → + Papal States (19) | none | none |
| distant-hussar-64 | Denmark | 1 → 1 | Kingdom of Italy (9) | none | none |
| scarlet-salient-30 | Naples | 1 → 1 | Kingdom of Italy (10), Papal States (20) | none | none |
| thundering-courier-34 | Denmark | 0 → 0 | Kingdom of Italy (7) | none | none |
| wintry-bastion-23 | Denmark | 0 → 0 | Kingdom of Italy (7) | none | none |
| burning-caisson-85 | Naples | 2 → 2 | Kingdom of Italy (10), Papal States (28) | none | none |

Six of six story classes before and after. The Pope falls on all three seeds that cast Naples now (two before). **No
promotion and no formation on any fresh seed**: the gate's clause 2 rests on Hesse on two of the ten measured seeds
and is not seen out of sample, and the tier-8 signature ("`formations` stops reading none") is unmet on every idle
board read — sixteen seeds. Every fresh seed opens alike: the German Question at turn 2, the Kingdom of Italy's fall
by 10, Prussia's word for Bavaria at 6–7. With the commanded script on the same six (before the fixes): six different
stories — Prussia's Hanover crisis on five, Naples on Rome on two, Bavaria's Royal Crown on one, a client rebellion on
one.

**For the user, none pre-recommended (§0):**
(a) **your clients and "sign at the last"** — the harness's 4: let a client of the player's house sign at the last
for itself (it lives on; the AI holder hands its off-aim homeland back), or keep the boundary you drew at T4-2
*(RULED November 11, 2026 — session G3, §7c: neither; the cause is cured — a client signs no alliance of its own,
T4-2's boundary stands, the harness reads 0)*;
(b) **the licence and an exposed rear** — Russia, licensed for Finland and now at `fight`, is still held by her
reserve against an unbeaten Prussia (era-true; a licence could also quiet the licensee's rear toward its licensor);
(c) **the marshal king's fate** — he keeps his crown and fights when his kingdom rebels (built, told); or he comes
home at high trust;
(d) **the push's number** (10) and whether an AI backer's push should be weaker than the Emperor's;
(e) seen in play and not touched: armies outgrow their force limits in a long peace (Naples 53,000 on one
province); an ally stormed Vienna under the player's siege, made its own peace and handed it back; the dispatch
said the tricolor flew over Vienna on a morning Austria had retaken it; a 2,000-man British landing bombarded the
army for fifteen turns from soil at peace with France; Prussia's bandwagon chose the Papal States; the crown row sits
eighth in a short scrolling list; "(§3.3)" stands in the sponsor chip's player-facing text;
(f) session G's four, session F's three, session E's four, session D's three, session C's five stand.

*(RULED November 11, 2026 — session G4, §7d: (b) the backer's house is struck from the rear, Prussia's hold stays; (c) the cause
decides the king's fate; (d) 10 for every backer; (e) the commission ceiling, the ally's separate peace, the stale dispatch
line, the sanctuary guns, the bandwagon's reach, the crown row and the chip — each ruled and built; (f) stands.)*

### §7c A client swears no pact of its own — session G3's landing record (✅ LANDED November 11, 2026)

**The user's words, verbatim:** *"Rule on clients first"*; then, at the question, *"make best cal for game"*. Drafted
in Plan Mode and approved. The rule in full: `SYSTEMS_REFERENCE.md` §209; the pins
`tests/test_session_g3_a_client_swears_no_pact.py`; the seam `tests/_t3_seams.py` row G3-CLIENT; ONE sweep with two
arms on three surfaces (`tools/_g3_measure.py`), the standing series (`tools/_g3_series_arms.py`), the pacts read off
the kept runs (`tools/_g3_client_pacts.py`), ONE commit.

**What was put to the user (§7b (a)) and how it was ruled.** The AI-France harness kept 4 provinces outside aim: the
cast Naples holding Milan and Piedmont, the soil of the Kingdom of Italy. Read to its cause on the kept run (jena):
the kingdom — the Emperor's client — signs a DEFENSIVE ALLIANCE with the Pope at turn 7 through the court-to-court
poll; Naples declares the Roman Expedition at 14; the pact calls the kingdom into a war its lord is not in; Milan is
stormed and the kingdom erased at 20. Two cures stood on the table: let a client of the player's house "sign at the
last" for itself (the consequence softened), or stop the treaty that causes it. Ruled under the delegation: **a
client's foreign policy is its lord's** — the cause and not the consequence; the Emperor's agency (a treaty that can
destroy his kingdom is not signed behind his back); the era (Napoleon was King of Italy — a client's diplomacy was its
patron's); every court alike (an AI lord's clients are bound the same way, nothing special-cased for the player).
T4-2's boundary stands as drawn.

**The rule as built (G3-CLIENT, `ai_diplomacy.a_client_swears_no_pact_of_its_own`).** `client_in_the_pair(world, a,
b)` — the court of the two whose row in `world.vassals` names a lord, or none; none where the two are of one house (a
lord and its client, two clients of one lord). Read at the two sites session G's pact rule stands at: the poll
(`_evaluate_ai_ai_proposal`) proposes no defensive alliance and no alliance to or from a client; the
recipient-addressed road (`_resolve_ai_ai_proposal`) refuses one with the existing `ai_ai_proposal_refused` event,
`reason: client`. No new log type, no new field, no new store. **Untouched:** open borders and a non-aggression pact
(no war follows them — the warm pair still climbs to the pact below the alliance); the player's own proposals to any
court (the read has two callers, both court-to-court); a client following its lord into the lord's wars; a pact
already standing when a court becomes a client (a gate on signing, never a dissolution). The Alarm had said it of
guarantees already ("not a client — its lord answers for it", T4-1). **Said on screen:** each card of the Diplomatic
Ledger's Vassals tab carries one backend-composed line under the name — "Its wars are yours: it signs no alliance of
its own." (`diplomatic_ledger.CLIENT_POLICY_LINE`; empty with the seam down).

**The session landed (the pins `TestTheSessionG3Measure`).** ONE sweep, two arms (0 / CLIENT) on three surfaces, run
alone; the series beside it.
- **Arm 0 reproduces session G2 byte for byte on both surfaces** (the ambient signature and census; arm ALL of the
  harness record).
- **Ambient — not one seed moves** (signature and census, ten seeds): the idle France's kingdom falls to Austria in
  the Emperor's own war by turn 7–23 on every seed, before a client's pact matters. Story classes 10 of 10;
  `annexations_outside_aim` 0; `captures_outside_aim` 266.
- **The AI-France harness — `annexations_outside_aim` 4 → 0.** Seven seeds move (friedland, historical, jena, lodi,
  marengo, rivoli, wagram). On jena and wagram the kingdom is never called into the Roman war (Sardinia alone answers
  the Pope's call); Rome falls at 26 on jena (19 without the rule; the crisis opens twice, at 12 and 19) and at 17 on
  wagram; the Kingdom of Italy is erased on neither. Read off the kept runs (`_g3_client_pacts_2026_11_11.json`):
  **nineteen client pacts on session G2's tree — the kingdom with Rome on all ten seeds (turns 7–9), with Bavaria on
  nine — and none with the rule.** Russia buys the kingdom on eylau and lodi and Switzerland on lodi, on both arms: an
  AI lord's clients, bound alike. `captures_outside_aim` 133 → 135; France's own entry 189 → 187; France ends two
  provinces up on jena (40 → 42) and one on marengo (45 → 46); no promotion and no crown on either arm.
- **The band: 28 / 27 / 25 on both arms.** **The series does not move** on either arm; on the rig the poll answers a
  pact for a client's pair 735 times (of 3,339 pacts polled — the courts' offers to Switzerland and Holland), every
  one stopped at the gate on the shipped arm.

**A consequence, reported (no gate clause reads it).** On session G2's tree a Kingdom of Italy that broke free of the
harness's neglectful France **proclaimed ITALY the same turn on four seeds** (friedland, historical, marengo,
rivoli): its Risorgimento (Milan, Piedmont, Savoy, Naples, Rome) read as gathered with two provinces in hand, because
Rome, Naples and Savoy stood in the blocs of the pacts it had signed as a client — the ally clause reading the want
as won, session G's defect through a door its read does not watch (a client's deck sleeps, so
`pact_with_the_coveted` reads nothing on the day the pact is signed). With the rule the kingdom leaves its vassalage
with no pact and the Risorgimento is a live want: **no measured seed proclaims Italy in forty turns.** The United
Netherlands, whose Flanders is taken by arms, still forms (four seeds → five). Put to the user below.

**The gate's reading (§7) on the shipped arm — every clause as session G2 left it:** clause 1 MET (10 of 10); clause
2 MET (Hesse on lodi at 33 and marengo at 40); clause 3 MET (jena and wagram); the ambient annexation line 0; the
band inside 23–28. **The harness's line reads 0 too now** — no court but the harness's own France keeps a province
outside aim.

**Played (reported, never gated).**
- *The hand-played campaign* (`played_emperor.json`, replayed on this tree): identical to the archived run through
  turn 17; from 18 the one difference in forty turns is that Bavaria and the Kingdom of Italy sign no defensive
  alliance and Saxony's two offers to the kingdom are never made. Every beat and the last ledger row are the same.
- *A commanded France on the two seeds that cast Naples* (`commanded_full40.json`, the rule up and down): on jena,
  without the rule the kingdom is called into Naples' war through Rome ("Defensive cascade: KingdomOfItaly joins war
  via PapalStates") and fights it to a white peace at 24; with the rule it never enters. On both arms it later joins
  FRANCE's war when the league strikes at 30 and falls at 34 — the script's France is beaten there (20 provinces);
  that war is its lord's. On wagram the two arms end alike.
- *The same script on six fresh seeds*: France's provinces at 40 identical on all six; four digests differ — Rome's
  pact with the kingdom unsigned (distant-hussar-64), the kingdom no longer dragged into a war through its Bavarian
  pact at 31 (scarlet-salient-30).
- *Six fresh seeds, France idle*: byte-identical to session G2's reading on all six.
- *In the running client* (`tools/dd_b_play.py`, the turn-10 save): Diplomacy → VASSALS — each card reads "Its wars
  are yours: it signs no alliance of its own." under the name; 8 actions, 0 script errors.

**For the user, none pre-recommended (§0):**
(a) **Italy by pacts** — whether a freed kingdom should be able to proclaim Italy without arms: the rule ends the
hollow road (four harness seeds → none); if you want it reachable the levers are the design's own list (Milan and
Piedmont alone, or with Rome) or a proclamation at a share of the list — never the client pact;
(b) **a pact a court brings into a vassalage** stands (a gate on signing; no measured seed has one) — or it lapses
at the subjugation;
(c) **a client's non-aggression pacts and open borders** stay its own (no war follows them) — or go to the lord too;
(d) §7b's (b)–(f) stand; its (a) is ruled here.

*(RULED November 11, 2026 — session G4, §7d: (a) Italy is proclaimed on what she HOLDS, at three of her five, Rome
first; (b) the pact LAPSES to a non-aggression pact; (c) they stay its own — nothing built, pinned; §7b's (b)–(e)
are ruled there too.)*


### §7d The open readings, ruled and built — session G4's landing record (✅ LANDED November 11, 2026)

**The user's words, verbatim:** at session G3's close, to the Italy question, *"Show me options"* — interrupted —
*"evaluate options choose the best"* — interrupted — *"and decide and do these"*, over the list left with him: a
pact a court brings into a vassalage, a client's non-aggression pacts, the rest of session G2's list. Each item was
read to its cause first; fourteen rulings were drafted in Plan Mode and approved. The rules in full:
`SYSTEMS_REFERENCE.md` §210; the pins `tests/test_session_g4_the_open_readings.py`; the seams `tests/_t3_seams.py`
rows G4-*; ONE sweep with eleven arms on three surfaces (`tools/_g4_measure.py`), the standing series
(`tools/_g4_series_arms.py`), ONE commit.

**The rulings.**

| # | The item | The ruling | Seam |
|---|---|---|---|
| 1 | Italy by pacts (§7c (a)) | a nation is proclaimed on what it HOLDS, at an authored bar: Italy at **three of her five** provinces (`forms.at`), reaching for Rome first (`forms.first`); the rest stay her claims | G4-FORM |
| 2 | the same fault, wider | an acquire design is WON only on land the court or its clients hold; an ally's soil makes it sleep | G4-WON |
| 3 | a pact brought into a vassalage (§7c (b)) | it lapses to a non-aggression pact at the treaty, the conquest or the transfer; no breach | G4-LAPSE |
| 4 | a client's lesser pacts (§7c (c)) | they stay its own — the lord's war overrides them without a broken word; nothing built | — |
| 5 | the licence and an exposed rear (§7b (b)) | a court holds no rear reserve against the house that backs it; a third court on the flank holds it as before | G4-REAR |
| 6 | the marshal king's fate (§7b (c)) | the cause decides: his people rise and he comes home with half his corps; his court turns and he keeps the crown | G4-KING |
| 7 | the push's number (§7b (d)) | 10, the same for every backer; nothing built | — |
| 8 | armies past their limits (§7b (e)) | the AI's commission of a general reads the ceiling its arming reads | G4-CEILING |
| 9 | the ally who handed Vienna back (§7b (e)) | the Emperor's ally takes no separate peace, as its pair's winner, from a court he still fights | G4-ALLY |
| 10 | guns from soil at peace (§7b (e)) | no bombardment out of a province whose owner is a third court not at war with the target — every court | G4-GUNS |
| 11 | Prussia's bandwagon on Rome (§7b (e)) | a bandwagoner joins only against a neighbour of its house | G4-WAGON |
| 12 | the tricolor over a Vienna already lost (§7b (e)) | the dispatch drops a capture or loss line the province's latest change of hands has overtaken | — |
| 13 | the crown row eighth (§7b (e)) | an available crown row leads the demands, under the war's declared articles | — |
| 14 | "(§3.3)" in the chip (§7b (e)) | removed | — |

**What the played checks added (each fixed at its cause, in the same commit).**
- **Italy's pursuit.** Played out with the bar alone, a freed Kingdom of Italy fixed on Savoy — third in her list,
  and France's — and never turned to Rome. `forms.first` leads the order the obstacle is read from.
- **The king named in the treaty.** Replaying the hand-played campaign, Soult — demanded as King of Hungary at
  glory 3 — stood at 2 when the treaty was ratified two turns on, and the kingdom erected "under Soult" was a
  regency. `crowns.enthrone` seats the king a signed treaty names while he is still the Emperor's to seat; the
  laurels are the pick's test.
- **HOUSE — the DD-1 treaty fuzzer's catch** (its own seam and arm). On the fuzzed board a court France had
  subjugated defected to Britain and marched on France; neutral Switzerland — at peace with Britain since the boot —
  auto-joined against it, leaving a client at war with a court its own lord was at peace with (the fuzzer's I2, a
  class held at zero since S7). A client called to its lord's defence joins no war against a client of a FOREIGN
  lord it is at peace with.
- **The counter's dry run** raised `KeyError: 'clauses'` on a draft with no clauses list (session G3's tree too).
- **A save made before the bar** kept the old rule — the deck rides the save. `formations.backfill_forms` copies
  the two authored keys onto the saved entry at load (keys on an existing entry; no entry is ever added — the
  AI-0d precedent stands for goals).

**The session landed (the pins `TestTheSessionG4Measure`).** ONE sweep, eleven arms, three surfaces, run alone; the
series beside it; the shipped arm re-run on the final tree after the last edits, byte-identical.
- **Arm 0 reproduces session G3 byte for byte on both surfaces.**
- **Ambient (ten seeds), arm by arm:** FORM, WON, LAPSE, REAR, ALLY and KING move no seed. **CEILING moves five**
  (friedland, lodi, marengo, rivoli, ulm); **GUNS moves rivoli; WAGON moves jena** (Prussia leaves Rome alone — the
  Pope falls at 19, not 26, and the seed opens seven wars for five); **HOUSE moves friedland and historical** (on
  friedland Britain buys Switzerland at 9 and she marches on France; the Kingdom of Italy, at peace with Britain, no
  longer joins — and is not erased at 23). Story classes **10 of 10 on every arm**; `annexations_outside_aim` 0;
  `captures_outside_aim` 266 on the shipped arm.
- **The AI-France harness:** `annexations_outside_aim` 0 on every arm. FORM moves five seeds (a freed kingdom turns
  on Rome and Naples answers for the Pope; on ulm she is beaten to her last province and signs at 40); CEILING two;
  ALLY four; WAGON two; HOUSE lodi (Holland, no longer called against Britain's bought Swiss, drifts from the
  harness's France and rises at 32 — France ends at 38, not 46, on that seed). No promotion, no crown.
- **The band: 28 / 27 / 25 through CEILING; 26 / 27 / 25 with ALLY; 26 / 26 / 25 from GUNS on — the shipped arm,
  inside 23–28.** On the commanded historical arm Bavaria took Austria's suit at turn 5 and handed Hungary back
  (the played campaign's own fault); with the rule she stands, and France ends two provinces down at 31.
- **The series does not move** on any arm; on the rig the backer's rear bites 76 times and the house rule once.

**The gate's reading (§7) on the shipped arm:** clause 1 MET (10 of 10); **clause 2 MET on ONE seed — lodi, Hesse
at 33** (marengo's crown at turn 40, the window's last, no longer falls inside it: CEILING's arm — the cast Saxony,
at her band, commissions no second general and the seed's wars re-time); clause 3 MET in **three** readings now
({Kingdom of Italy} on seven seeds, {Kingdom of Italy, Papal States} on jena and wagram, nobody on friedland); the
annexation line 0 on both surfaces; the band inside 23–28. **No clause is lost; clause 2's margin is thinner and
the band two provinces lower — both said to the user, each one switch to reverse.**

**Played (reported, never gated).**
- *A freed Kingdom of Italy, played out unattended on five seeds:* she asks the Pope for Rome, is refused twice,
  opens her crisis and marches. **Italy is proclaimed on three** (marengo at 32 and eylau at 31, each the turn
  after Rome falls; jena, where she then loses a great war with Austria and is erased at 40) and not on two
  (historical and lodi — Naples answers for the Pope and beats her). On marengo and eylau the new Italy then asks
  Naples for the south and is refused: the claims live on.
- *The hand-played campaign, replayed:* the British guns fire twice (17 before) and fall silent at France's peace
  with Austria; Bavaria takes no separate peace; Vienna, held by Bavaria, goes home by the Emperor's own treaty,
  which did not demand it.
- *In the running client, by clicking* (`tools/dd_b_play.py`, the turn-10 save; 24 actions, 0 script errors): the
  crown row leads "Demands of Austria"; its name opens the king list, each pick's price beneath it, and the
  footnote reads "If his court ever turns on you he keeps his crown and fights for it; if his people rise and drive
  him out, he comes home with half his corps." The Formable Nations page, on a save made before the bar and loaded
  by the real road, reads "2 of 5 provinces held — 3 proclaim it".

**For the user, none pre-recommended (§0):**
(a) **the commission ceiling** costs marengo's crown (clause 2 on one seed, not two) — one switch brings it back,
and with it a cast minor that arms to twice its limit;
(b) **the band** reads 26 / 26 / 25 (the ally's rule −2 on one commanded arm, the guns' −1 on another);
(c) **Italy's bar and order** — three of five, Rome then Naples (the numbers are authored, `europe_1805.json`);
(d) **a neutral client** (HOUSE) no longer marches against a foreign lord's client: the Kingdom of Italy survives
on friedland; on the harness's lodi an uncalled Holland drifts and rises;
(e) **the older sessions' readings** (C to G) were not in this session's list and stand.

*(RULED November 11, 2026 — session G5, §7e, under the user's "do what you deem best then tell me what next": (a), (b) and (c) stand as shipped; (d) is re-cut — a client takes up her lord's war with the house and rallies; (e) stands open, none built.)*


### §7e A client rallies against the house — session G5's landing record (✅ LANDED November 11, 2026)

**The user's word**, at session G4's close, to the five readings left with him: *"do what you deem best then tell me
what next."* A delegation; the rulings are the author's under it. The rules in full: `SYSTEMS_REFERENCE.md` §211; the
pins `tests/test_session_g5_a_client_rallies.py`; the seams `tests/_t3_seams.py` rows G5-RALLY and G5-AIMS.

**Ruled, nothing built — four of session G4's five readings:**
- **(a) the commission ceiling stands.** It bites where it was built to bite (a cast minor already at one and a half
  times its force limit adding a general past it). Dropping it buys back a promotion and a minor armed to twice its
  limit with it. (The rally's world-line brings marengo's promotion back by itself — below.)
- **(b) the band stands at 26 / 26 / 25**, inside 23–28: the price of an ally who no longer hands back the capital
  the Emperor is besieging, and of guns that no longer fire from neutral ground.
- **(c) Italy's numbers stand** — three of five, Rome then Naples. Played on five seeds she proclaims on three and
  loses the war for Rome on two: reachable, and not given.
- **(e) the older sessions' readings (C to G) stand open.** Each is a content lever, not a defect; none blocks the
  deploy; none is built or cut here (§0).

**Ruled and built — reading (d), the neutral client.** Session G4 closed the treaty fuzzer's I2 (a client at war
with a court its lord is at peace with) by keeping a client at peace with the aggressor's lord OUT of her own lord's
defence. Played on the real road — the bribe's transfer, `vassal._client_takes_the_field` — that reads badly:
Britain buys Holland, Holland marches on France, the Emperor's ALLIES (Spain, Bavaria) fight her, and his own two
clients stand by because neither had fought Britain. A turncoat with a foreign patron was safer than a plain rebel,
whom the loyal clients do march on. The fault was the HALF war, not the rally.

**The rule (`diplomacy.a_client_rallies_against_the_house`, row G5-RALLY; the read `_rally_against_the_house`, at
the cascade's defensive auto-join behind session G4's read):** a client called to its lord's defence against a
client of a FOREIGN lord it stands at peace with takes up its lord's war with that lord — her pair with the house
attached to the LORD's own war instance with it, on his side — and then marches on the house's client as before.
Three boundaries: where her lord is himself at peace with that house she stays out (no half-war — session G4's
answer, kept); where the war record refuses the pair she stays out; an ALLY's policy is its own and is untouched
(Bavaria answers the alliance against the client and keeps her peace with its lord — the fuzzer reads that clean,
the bought client leading its own war). The way out is her lord's peace: the pairs she took up are among the client
pairs that follow him out (`client_pairs_that_follow`; the offer surface already says "Our clients follow us out of
the war"). The two seams nest: session G4's down is session G3's tree whatever this one reads. No new saved field,
no new screen: the declaration's story gains a second line ("Switzerland follows France into the war against
Britain!") and the campaign log a second `vassal_auto_join_war` row.

**The gate's read — the sweep's catch (`war_council.the_gate_reads_the_authored_aims`, row G5-AIMS).** The first
sweep read `annexations_outside_aim` 2 on marengo with the rally up — a deploy-gate number. Read to its cause before
it was believed (a replay of both arms, the read's inputs side by side): the SAME two provinces (Milan, Piedmont),
the same holder (Austria), the same conquest at turn 20 in her war with France stand on both arms. What differs is
Austria's last turn: with the rally she ends on two of her seven homeland provinces, and a court under the survival
override has no design VOICE — `agendas.acquire_design_regions` returns nothing — so the read called two provinces
of her own authored Italian design "outside aim". An instrument's fault, not sprawl. The read now asks the deck AS
WRITTEN (`acquire_design_regions(authored=True)`); sprawl is still counted under the knife (Bern, in no Austrian
design, is). The TERMS' read (`keepable_regions`) keeps the voice: a court fighting for its life keeps at a peace
only what it declared. The read is called by the instrument alone (nothing under `backend/` calls it), so the seam
moves no world. It is behind its own switch and its own arm so the record shows both readings.

**The session landed (the pins `TestTheSessionG5Measure`).** ONE sweep, three arms (0 / RALLY / ALL), three
surfaces, run alone on the final tree (`tools/_g5_measure.py`); the series beside it (`tools/_g5_series_arms.py`).
- **Arm 0 reproduces session G4's shipped arm byte for byte on both surfaces.** Arm RALLY on the final tree is the
  first sweep's arm RALLY byte for byte (the seam down IS the read before).
- **Ambient, arm RALLY moves six seeds.** On each a coalition court buys Switzerland from the idle France and she
  marches on him — Austria on eylau, jena and rivoli (turn 14), Russia on historical (11) and marengo (19), Britain
  on friedland (9) — and the client that had kept its peace with the buyer now rallies (Holland on five; the Kingdom
  of Italy on friedland and marengo). **friedland:** the Kingdom of Italy, which sat out on session G4's tree and
  lived, is erased at 23 — the roster reads two ways again, not three. **marengo:** Hesse's Grand Ducal Title at 39
  — the promotion clause on TWO seeds again (lodi 33, marengo 39); Switzerland signs at the last with Austria at 34
  and ends the forty turns free. Story classes **10 of 10 on every arm**; `captures_outside_aim` 266 → 290.
- **Arm ALL (the gate's read) moves one number and no world:** marengo's `annexations_outside_aim` 2 → 0; the
  signature's every other key, the census and the story class are arm RALLY's; the harness arm is byte-identical.
- **The AI-France harness:** lodi alone moves — Holland is called against the bought Swiss again, does not drift
  and rise at 32 (no United Netherlands), and France ends at 46, not 38. `annexations_outside_aim` 0 on every arm;
  no promotion, no crown.
- **The band: 26 / 26 / 25 on every arm. The series does not move**; on the rig the rule's occasion arises once and
  the rally bites once.

**The gate (§7), read off arm ALL:** clause 1 MET (10 of 10); clause 2 MET on two seeds (Hesse on lodi at 33 and on
marengo at 39); clause 3 MET in two readings ({Kingdom of Italy} on eight seeds, {Kingdom of Italy, Papal States} on
jena and wagram); `annexations_outside_aim` 0 on both surfaces — on the ambient record by the corrected read (the
voice's read counts 2 on marengo: arm RALLY, kept in the record); the band inside 23–28.

**Played before the sweep** (session G4's lesson, kept): the bribe's own road on the booted board with Holland
bought and with Switzerland bought — the fuzzer's invariants clean with the rally up, down, and with session G4's
seam down; the declared-war road; the way out (France's peace with Britain carries the five pairs); the treaty
fuzzer's two seeds; the full suite once (39,480 passed) before the first sweep.

**For the user, none pre-recommended (§0):**
(a) **Switzerland is bought on six of ten unattended seeds** (Austria, Russia or Britain, turns 9 to 19). The idle
France answers no petition and pays no court; a commanded France keeps her on all three band arms. The rally makes
each purchase a wider war — the rule working; whether the bribe's price or reach wants a second look is a content
question;
(b) **friedland's Kingdom of Italy falls again** — the roster two ways, not three; the clause reads MET either way;
(c) **the gate's read was corrected in the session that tripped it** — the cause is above and the old read is one
switch away (`G5-AIMS`); on it marengo counts 2 and the rally is the rule to weigh;
(d) **an ally of the attacked lord** still answers against the bought client alone and keeps her peace with its
lord — an ally's policy is its own;
(e) **the older sessions' readings** (C to G) stand open.


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
| DY-2 | 5 — ✅ LANDED November 10, 2026 (session B) | the Questions (§4; the gate §4a — the four tables as ruled, "Four on the drawn map"): `questions.py` — the block and `_validate_questions`, the latch at the chokepoint and its auto-charge mirror (the house read), the envy term in `intent._derive_weight`, the beat `question_turns` (182 → 183), the Balance tab's `question_lines`, the store inside `world.moments` (the affairs precedent) — and the Alarm's guarantee rung's Question arm (§3c G2: `share_a_table`) | the latch writes at capture and nowhere else; the envy inside the window, never a non-claimant's, never a court's own gain; the beat once per turn-of-the-Question; the validator refuses an unknown province and a one-seat table and WARNS on an unknown claimant (the shipped file keeps its eleven warnings); the sweep carries `questions_turned`; the rung's Question arm pinned — **measured:** see §4a's landing note and `SYSTEMS_REFERENCE.md` §202 | `tests/test_dy2_the_questions_of_europe.py` |
| DY-3 | 5 — ✅ LANDED November 10, 2026 (session B, built whole under the standing rule on cuts) | the Congress rules a Question (§4; `questions.congress_rules` on the sitting's tick, seam `the_congress_rules_a_question`) | a sitting Congress recognizes each open table's present holder; the latch clears, the unseated claimants −10 toward the holder (the player's house takes none), one `congress` row (phase `ruling`), one beat; once a sitting; a table nobody holds is not ruled; a capture reopens it | rides DY-2's file (`TestTheCongressRulesAQuestion`) |
| DY-1e | 5 — ✅ LANDED November 10, 2026 (session B; the user's "Road home" for Bern) | the lord signs for its client at the last (§4a): a client at its last province signs through its AI lord's pair with each holder of its homeland outside that holder's keepable set (SR-1b — the client follows its lord out; `_signs_for_the_client`), the homeland going home first; the player's house exempt on either side; seam `settlement_third_party.a_lord_signs_for_its_client` | on a crafted board Britain signs for Switzerland against Saxony and Bern goes home, the client living on as Britain's; the seam down falls as T4-2 did; the player's client still falls; a client at war on its own account signs its own; `annexations_outside_aim` 0 on both surfaces — **measured:** see §4a's landing note | rides DY-2's file (`TestTheLordSignsForItsClient`) |
| DY-1f | 5 — ✅ LANDED November 10, 2026 (session B; the user's "best solution no corner cutting") | the Emperor's gift (§4a): (i) the player's road — the ally petition asks for the ally's authored designs (`_coveted_regions_of_ally`) and its prevalidation reads the validator's occupied-homeland rule (`_occupied_homeland_ok`); (ii) the AI's road — an aim peace carries each co-belligerent's delivered aim the side holds, ceded to that ally (`war_council.side_aim_cessions`), seam `settlement_third_party.a_leader_signs_for_its_allies`; the levers K = 6 and 3,000 stand | Pressburg's Tyrol to Bavaria pinned end to end (the petition, the cession, the treaty title, six quiet turns, the AI's own rung, the `rank_promotion` row); Russia's aim peace cedes Scania to Denmark and her crown's refusal clears; the seam down is T3-4's leaders-only peace; five crowns askable where three were not — **measured:** `rank_promotions` on the sweep, see §4a's landing note | rides DY-2's file (`TestTheEmperorsGift`) |
| DY-1g | 5 — ✅ LANDED November 10, 2026 (session B; the user's "reason best solution for gameplay") | the Emperor's treaty moves a seat (§4a): boundary (1) kept, boundary (2) reversed — a court whose capital the player's house takes by treaty removes like any other; the Congress's recognition-by-defeat reads the historic capital (`congress._historic`, `game_end`'s `capital_kept`); seam `game_end.the_emperors_treaty_moves_a_seat` | Vienna's cession removes Austria's court to Bohemia while the Congress reads Vienna in the Emperor's hands and the `capital` latch names it; the Emperor's client takes a seat too; the player's own court never removes; the seam down is session A's boundary; no `get_nation_capital(court)` read left in `congress.py` — **measured:** the France band on the commanded arms, see §4a's landing note | rides DY-2's file (`TestTheEmperorsTreatyMovesASeat`); `test_a_capital_in_the_emperors_hands_moves_the_seat_too` re-seated with cause in DY-1's file |
| DY-4 | 6 — ✅ LANDED November 10, 2026 (session C) | the store, raises/cools, the ulcer, the letters (§5; the gate §5a): `awakening.py` — the store inside `world.moments` armed by the scenario's `awakening` block, the DERIVED occupied count with the boot-web house read (C1, C2), the bands and cools, the one writer `move` and the beats (`awakening`, 183 → 184), the dictated peace by rank, the sovereign taken, the client squeezed, the ulcer at `_supply_multiplier`, the two letters and the `awakening` op; three seams (T6-STIR / T6-ULCER / T6-LETTERS) | the AI-France march bleeds; the letters appear by condition — **measured:** arm 0 reproduces session B byte for byte on both surfaces; the scalar alone moves every ambient seed by the new column (the French people stir on every seed, the Bavarians on seven); the ulcer alone moves ulm and the harness's austerlitz and eylau; **the march does NOT visibly bleed** — the ulcer taxes the cap and a corps under it pays nothing (reported; the lever to the user); **the letters never arrive on a measured arm** (no measured France holds a people's soil fourteen turns; the desk seats a late premise behind the standing bills) and appear by their own conditions on the frozen board (stir 15, the letter 18, risen 25, The Ulcer 30 — the pin); the band holds; the series unmoved; the pacing record re-recorded and its drift attributed to Tiers 1–5, not the Awakening (§5a's landing note) | `tests/test_dy4_the_awakening.py` |
| DY-5 | 6 — ✅ LANDED November 10, 2026 (session D) | the levée, the client dial, the measure chain (§5) — and, from session C's gate (§5a), the third letter *The Nation in Arms* and the boot-web boundary of C2: `awakening.py`'s DY-5 half — `levee_terms` (×1.5 regen / ×0.75 the draft; the National Guard ×2.0 / ×0.5 for a term; the `levee` beat, 184 → 185), `client_dial` (−2 at autonomy ≤ 1, +1 at ≥ 2; the rebellion's cause), `risen_grievance` (the partition bar waived at `risen`), `coalition_friction_step` (1 a turn, not 2, while the league frees an awakened people), `nation_in_arms` + the `national_guard` op (12 → 13); five seams (T6-LEVEE / T6-DIAL / T6-REVANCHE / T6-LIBERATORS / T6-ARMS); the boundary needed no new rule (pinned) | 1813 surges; the tiger ridden at autonomy ≥ 2 — **measured:** arm 0 reproduces session C byte for byte; classes 10 of 10 and the band 28 / 27 / 26 on every arm; the series unmoved; the levée rises on every ambient seed (France 25–33, Bavaria on five) and on eight harness seeds (Russia 26–39), the letter arrives on the scripted France (T38) and is never due on seventeen arms whose premise held (the floor); not one world-line moves — the idle France recruits nothing, Russia's last recruit falls before its levée, no client is awakened, no AI court reaches `risen` (§5b's levers) | `tests/test_dy5_the_tiger_ridden.py` |
| DY-6 | 8 — ✅ LANDED November 10, 2026 (session E) | the crown erected + the marshal king (§6; the gate §6a): `crowns.py` — the `crown` sub-block on the ONE catalogue (six crowns authored, the validator), the teeth at the one apply site (the title and `recognized_by` on the row, the boot house written for every carve — the C3 sibling fix —, the Alarm's 12, the beat `nation_formed` + `crown` / the dispatch `crown_erected`), the marshal king and the prince (the picker on the guided row — `king_options` / `king_labels` —, the add verb's `king`, the marshal re-homed with his corps, the loyalty seed from his trust, the passed-over grievance), the AI's road (`settlement_third_party.erect_a_crown_in_the_terms` on both aim roads), the `crowns` block (the princes, the recognition rule) in `world.moments`; three seams (T8-CROWN / T8-KING / T8-AI) | Naples under Murat end to end through the guided terms (the row offers the throne, the verb stamps the king, the applier seats him — pinned); the ladder reflects the crown (Murat off it, Ney envious); the AI erects Finland under Russia on the crafted board — **measured:** see §6b | `tests/test_dy6_the_crown_erected.py` |
| DY-7 | 8 — ✅ LANDED November 10, 2026 (session F) — **TIER 8 COMPLETE** | Recognition (§6; the shape §6a Q4): `crowns.py`'s DY-7 section — the condition `until: beaten` at the three peace chokepoints (`note_peace_signed`, the loser by burden; the common peace's record, the bilateral ratify after the carve, the dictated truce exit), the Congress's grant and refusal (`congress_grants`, beside the Questions' ruling), the `recognition` beat (the census 185 → 186), the three prices (`crown_recognition` on both scorers, −5 a crown capped −15; the lord's trade with a withholding court halved — the client's rows are empty in this engine —, the Strategic Ledger's signed component; the dial −3), the ledger's lines, the Vassals card, Talleyrand's counsel; the carved client's dial reads the people it sits on (a sibling fix); two seams (T8-RECOG / T8-PRICE) | recognition moves acceptance and trade and the Congress can grant it — pinned on the crafted boards (Naples under Murat; Russia's Finland); **measured:** see §6c (arm 0 reproduces session E; nothing recognized ambiently — no crown rises) | `tests/test_dy7_recognition.py` |
| G-PACT | the gate — ✅ LANDED November 11, 2026 (session G) | the pact with the coveted (§7a): `ai_diplomacy.no_pact_with_the_coveted` — no defensive alliance or alliance between two AI courts while either's live acquire design covets a province of the other (the holder itself or the house it serves; `pact_with_the_coveted`, one read): the poll's gate (`_evaluate_ai_ai_proposal` over the triggers) and the recipient-addressed road's guard (`_resolve_ai_ai_proposal`, the refusal event's `reason: covets`); a NAP untouched | the cast Naples keeps her Roman Expedition on jena (the four-turn board, pinned both ways); Hesse's design cannot be read "won" by Hanover's pact; the upgrade ladder stops below a pact; the seam down signs as before — **measured:** see §7a | `tests/test_session_g_the_gate_earned.py` |
| G-CHEST | the gate — ✅ LANDED November 11, 2026 (session G) | a crown is bought with the whole chest (§7a): `reforms.a_crown_is_bought_with_the_whole_chest` — the AI's purse bar for a promotion law (`is_promotion`) is the price and arrears alone (no `AI_PURSE_RESERVE`, no five turns' upkeep); every other law keeps the reserve; the Net test and `law_refusal` stand | the five crowns' bars read their price (3,000 — 4,500 with the seam down); Prussia's Staff keeps its reserve; the rung buys at 4,000 and waits at 2,900 (T4-3's pin re-seated with cause) — **measured:** see §7a | `tests/test_session_g_the_gate_earned.py` |
| G2-KING | the played campaign — ✅ LANDED November 11, 2026 (session G2) | the king survives the separate peace (§7b): `settlement_staging._pair_substitute_seed_terms` carries `crowns.CROWN_CLAUSE_KEYS` (the builder copied four keys and dropped the crown and its king on the one road open while London is unbeaten) | Soult is King of Hungary through the joint table, the separate peace and a counter-offer; a regency carries no king — **measured:** the played campaign's turn 12 on the fixed build; the client walk | `tests/test_session_g2_the_played_campaign.py` (`TestTheKingTravels`) |
| G2-RECOG | the played campaign — ✅ LANDED November 11, 2026 (session G2) | the war names the beaten (§7b): `crowns.the_war_names_the_beaten` — `war_loser` (the pair's score past the ratification record's bar) before the clause burden at the three peace chokepoints; the ceding court recognizes the crown its treaty erects; the card speaks the reception as the treaty leaves it | Vienna recognizes the kingdom she signed over for 2,800 gold; a drawn war still binds the ceding court; a peace bought from an unbeaten court recognizes nothing; the seam down is session F's withholding — **measured:** no crown stands on a measured arm (the seam read 0 times on the rig); the proof on the played board | `TestTheWarNamesTheBeaten`; `test_dy7_recognition.py` re-seated with cause |
| G2-ASK | the played campaign — ✅ LANDED November 11, 2026 (session G2) | a court at `fight` still asks (§7b): `ai_diplomacy.a_court_at_fight_still_asks` — trigger 0a's rungs include `fight` while the ladder is unclimbed | the cast Naples at `fight` asks the Pope; the seam down she never does; a climbed ladder stops the asking — **measured:** arm ASK moves jena and wagram, see §7b | `TestACourtAtFightStillAsks` |
| G2-LADDER | the played campaign — ✅ LANDED November 11, 2026 (session G2) | the ladder outlasts the rest (§7b): `ai_diplomacy.the_ladder_outlasts_the_rest` — `war_council._ladder_climbed` counts `get_ladder_refusals` (24 turns) and the write keeps them; every other reader keeps 12 | refused at 7 and 13, the ladder stands climbed at 24 (unclimbed seam-down); the weight's hardening still reads 12 — **measured:** arm LADDER moves lodi; 14 bites on the rig, the series unmoved | `TestTheLadderOutlastsTheRest` |
| G2-BACKED | the played campaign — ✅ LANDED November 11, 2026 (session G2) | a backed design dares (§7b): `intent.a_backed_design_dares` — `WEIGHT_BACKED_DESIGN` 10 on an acquire design a live sponsorship or licence aims at (`design_backing`, ONE record); never an aim in the player's house; `backing_forecast` at the choice, `backing_words` on the Intent row | France's gold and her licence each move Prussia's design 10; the paymaster's subsidies against France move nothing; the push ends with the compact; the words — **measured:** arm ALL moves lodi; 10 bites on the rig, the series unmoved; the band 28 / 27 / 25 | `TestABackedDesignDares` |
| G3-CLIENT | a client swears no pact — ✅ LANDED November 11, 2026 (session G3) | a client's foreign policy is its lord's (§7c): `ai_diplomacy.a_client_swears_no_pact_of_its_own` — `client_in_the_pair` the one read, at the poll's gate (`_evaluate_ai_ai_proposal`) and the recipient-addressed road's guard (`_resolve_ai_ai_proposal`, `reason: client`); a defensive alliance and an alliance only; the Vassals card's line (`diplomatic_ledger.CLIENT_POLICY_LINE`) | the read (a client either way, two free courts, one house, every lord alike, a court set free); the poll stops both pact types and passes the rungs below; the road's refusal names the client; a standing pact stands; the player's road untouched; the card's line — **measured:** arm 0 == session G2; ambient no seed moves; the harness's annexation line 4 → 0, nineteen client pacts → none; the band 28 / 27 / 25; the series unmoved, 735 bites on the rig | `tests/test_session_g3_a_client_swears_no_pact.py` |
| G4-FORM | the open readings — ✅ LANDED November 11, 2026 (session G4) | a nation is proclaimed on what it holds, at its bar (§7d): `formations.a_nation_is_proclaimed_on_what_it_holds` — `proclamation_due` reads `held_provinces` against `proclamation_bar` (`forms.at`; Italy 3 of 5); `forms.first` leads the pursuit order (`agendas._entry_regions`); `backfill_forms` at load; the validator's `_validate_forms_bar` | the marker names the bar; the hollow road closed; Rome makes Italy and the rest stay her claims; a client proclaims nothing; she reaches for Rome first; a save made before the bar gains it — **measured:** ambient no seed moves; the harness five seeds; played out, Italy on three of five | `TestANationIsProclaimedOnWhatItHolds` |
| G4-WON | the open readings — ✅ LANDED (session G4) | an ally's soil is not won (§7d): `agendas.an_allys_soil_is_not_won` — `_entry_satisfied`'s acquire arm reads possession | the design sleeps and is not satisfied; held is won either way — **measured:** no seed moves on any surface | `TestAnAllysSoilIsNotWon` |
| G4-LAPSE | the open readings — ✅ LANDED (session G4) | a pact lapses at the vassalage (§7d): `vassal.a_pact_lapses_at_the_vassalage` — `_vassalage_entry_decision`'s third answer, applied at `_reconcile_vassal_diplomacy` | the decision; no breach; the transfer; the conquest's quote — **measured:** no seed moves (no measured court carries a pact into a vassalage) | `TestAPactLapsesAtTheVassalage` |
| G4-REAR | the open readings — ✅ LANDED (session G4) | a backer is no menace (§7d): `war_council.a_backer_is_no_menace` — `backers_of` struck from `get_exposure_view`'s threats | the licensor struck; his own house only; the compact ended; at war he menaces — **measured:** no seed moves; 76 bites on the rig | `TestABackerIsNoMenace` |
| G4-CEILING | the open readings — ✅ LANDED (session G4) | a commission reads the arming ceiling (§7d): `recruitment.a_commission_reads_the_arming_ceiling` — `commission_over_the_ceiling` in `find_ai_commission` | the played board's leak; under the band she still commissions; the player's own commission ungated — **measured:** ambient five seeds, marengo's crown at 40 lost; the harness two | `TestACommissionReadsTheArmingCeiling` |
| G4-ALLY | the open readings — ✅ LANDED (session G4) | the Emperor's ally takes no separate peace while it wins (§7d): `settlement_third_party.the_emperors_ally_takes_no_separate_peace` — `ally_stands_by_the_emperor` in `sub_pair_loser_sues` and `held_aim_suit` | Vienna sues Munich and is referred to the Emperor; a beaten ally may be knocked out; his own peace frees the pair — **measured:** ambient none; the harness four; the band's H arm 28 → 26 | `TestTheEmperorsAllyTakesNoSeparatePeace` |
| G4-GUNS | the open readings — ✅ LANDED (session G4) | no guns from a sanctuary (§7d): `combat_executor.no_guns_from_a_sanctuary` — `fires_from_a_sanctuary` at `_execute_bombardment`, the AI's P4 and P7 | the read; the refusal's words; the Emperor's guns bound alike — **measured:** ambient rivoli; the band's A arm 27 → 26; the replay 17 bombardments → 2 | `TestNoGunsFromASanctuary` |
| G4-WAGON | the open readings — ✅ LANDED (session G4) | a bandwagoner joins a neighbour's war (§7d): `war_council.a_bandwagoner_joins_a_neighbours_war` — `bandwagon_in_reach` in `_bandwagon_join` | reach is the house's frontier; the join itself — **measured:** ambient jena; the harness two | `TestABandwagonerJoinsANeighboursWar` |
| G4-KING | the open readings — ✅ LANDED (session G4) | the people drive out a foreign king (§7d): `crowns.the_people_drive_out_a_foreign_king` — `king_at_the_rebellion` at `check_vassal_rebellion`; `enthrone` reads `marshal_free_to_reign` | his people rise and he comes home; his court turns and he keeps the crown; the words; a king named in the treaty is seated though his laurels fade — **measured:** no seed moves (no crown on a measured arm) | `TestThePeopleDriveOutAForeignKing` |
| G4-HOUSE | the open readings — ✅ LANDED (session G4) | a client joins no war against a client of a house it is at peace with (§7d): `diplomacy.a_client_joins_no_war_against_a_house_at_peace` — `client_keeps_its_peace_with_the_house` at the cascade's defensive auto-join | the boot fact; the read (a rebel of her own house excluded); the neutral client stays out — **measured:** ambient friedland and historical; the harness lodi; the fuzzer's two seeds clean | `TestAClientKeepsItsPeaceWithAHouse` |
| G5-RALLY | the readings' close — ✅ LANDED November 11, 2026 (session G5) | a client rallies against the house (§7e): `diplomacy.a_client_rallies_against_the_house` — `_rally_against_the_house` at the cascade's defensive auto-join, behind session G4's read | the bought client marched on by the clients it left (both roads); her pair on the lord's own war, beside him; the way out; the words; the seam down; her lord at peace with the house; the record refusing; an ally's policy its own — **measured:** six ambient seeds, the harness lodi; the fuzzer's two seeds clean | `TestAClientRalliesAgainstTheHouse`, `TestWhereSheStillStaysOut` |
| G5-AIMS | the gate's read — ✅ LANDED (session G5) | the annexation read counts a house's authored aims under the survival override (§7e): `war_council.the_gate_reads_the_authored_aims` — `_house_aims(authored=True)` in `annexations_outside_aim`; the terms keep the voice | under the knife the authored aims stay in the count; sprawl is still counted; the terms' read unchanged; no rule of play calls it — **measured:** marengo's 2 → 0, no world moves | `TestTheGateReadsTheAuthoredAims` |


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
