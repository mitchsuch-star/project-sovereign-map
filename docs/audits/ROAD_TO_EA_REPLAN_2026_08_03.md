# The Road to Early Access — the re-plan (August 3, 2026)

> **Status: RECOMMENDED SEQUENCE. Not a gate record — the user asked for a
> plan ("re-jigger the plan as you see fit, steam page doesn't have to be
> next"), and this is it. Positions 6 and 11 still carry their own design
> gates; everything else is buildable.**
>
> **Method:** a backlog survey, four independent plans from four lenses
> (ship-soonest / weakest-pillar / player-arc / risk-first), three
> adversarial judges scoring on ship-speed, quality and feasibility, then a
> synthesis that picks a spine and grafts. 9 agents.
>
> **Verified by the orchestrator before adoption** (the load-bearing claims
> were checked against the repo, not taken on trust):
> - `europe_visual.png` (6.5 MB) + `europe_lookup.png` — **UNTRACKED**,
>   caught by `.gitignore:40`. Confirmed and **FIXED in the same commit as
>   this memo**; they are the only two referenced-but-untracked assets in
>   the client.
> - `deploy/ink_iron.spec:125` — `all_datas = uvicorn_datas + fastapi_datas
>   + starlette_datas`. Confirmed: **a packaged build ships no world.**
>   Analysis entry is `backend/main.py`, which the cutover invalidated.
> - `turn_manager.py:1099` — `if self.world.sandbox_mode: return
>   {"game_over": False, ...}`. Confirmed: **the game cannot end.**
> - `AI_V_SWEEP_2026_08_01.md:472` — **a twelfth pillar, "the enemy phase
>   as theater: 5.5"**, below narration, diagnosed at `:482` as *"it was
>   never the dispatch prose, it is the enemy-phase composition."*
>   Confirmed. This is the plan's own strongest dissent.
>
> The map's SOURCE PSD (`map final1.psd`, named in `europe.json`'s `source`
> field) is **not in the repo** — only two small UI PSDs are. Locating and
> backing it up is a user action; it cannot be automated from here.

---

# RECOMMENDED SEQUENCE

**Spine: RISK FIRST (Plan 4)** — it won two of three judges and both of those judges independently recommended it as the graft base. Grafted onto it: Plan 1's tester loop and code-signing catch, Plan 2's measure-before-you-narrate rule and its Gazette costing, Plan 3's Victory-gate questions and replay frame.

**Everything load-bearing below is verified against the repo, not read off a doc.** Specifically confirmed this session: `deploy/ink_iron.spec:125` sets `all_datas = uvicorn_datas + fastapi_datas + starlette_datas` (no project JSON — a packaged build ships **no world**) and its Analysis entry is `backend/main.py`, contradicting the post-cutover `-m backend.main` requirement; `deploy/launch.bat` hard-exits without an `ANTHROPIC_API_KEY` in `config.txt` while `llm_client.py:346` defaults `LLM_MODE` to `"mock"`; `europe_visual.png` (6.2 MB) and `europe_lookup.png` are **untracked** (`git ls-files --error-unmatch` → "did not match any file(s) known to git"); `sandbox_mode`/`game_over` appear in **42 test files, 115 assertions**; `marshal_voice.py` is 160 lines exposing only `literal_ack`/`literal_completion`/`literal_no_march`/`emit_literal_fidelity_events`; the client has **one** `AudioStreamPlayer` (`battle_diorama.gd`), no `[autoload]` block at all, and `project.godot` still reads `config/name="Project Sovereign"` with `config/icon="res://icon.svg"`; there is no tutorial file in the client; and `AI_V_SWEEP_2026_08_01.md:472` records a **twelfth pillar — "the enemy phase as theater: 5.5"** — below narration, with `:482` diagnosing it as *"it was never the dispatch prose, it is the enemy-phase composition."*

---

## 1. THE CALL

| # | Item | Size | Why here | Unlocks |
|---|---|---|---|---|
| **1** | **The long quiet-France played campaign** — 30+ turns, France passive mid-game. **Extended brief (graft, Plan 2):** also score the *enemy-phase-as-theater* pillar and narration, because PT-D1/D2/D3/D4 and PT-F6 landed Aug 1 (`3c85242`, `41b03f2`) and **have never been re-measured** — narration 6.0 is stale evidence. Answer the `Normandy↔Berry` / `Flanders↔Orleanais` adjacency ruling **from what the campaign shows**, not from the doc. | play session | Fixed. It is the only vehicle for six open evidence items and it produces the transcript everything downstream reads. | Naval pillar score · played A2 sue-path · NV-P1 wheel check · NV-4..11 visual sign-off · NV-V remainder (A1–A5, NV-D7/D8, Q7) · living-balance/D1 band · **the re-measure that decides whether position 9 is narration content or another composition slice**. DEF-5/DEF-6 close. |
| **2** | **LLC + Steamworks onboarding** — entity, EIN, bank, Steam Direct $100, tax interview, app entry. **Parallel track. Starts the same week as position 1. Blocks nothing and is blocked by nothing.** | non-coding | The only item with weeks of *calendar* lead time and zero code dependency. Bundling it behind "gazette working" converts legal latency into lost wishlists for no engineering reason. | The Steam page at 10. Nothing else on the board can run in parallel with coding at zero cost to the coding. |
| **3** | **Asset backup + campaign triage + the adjacency ruling** — force-add (or off-machine backup + a CLAUDE.md record for) `europe_visual.png` and `europe_lookup.png`; confirm the source PSD still exists; then dispose of everything position 1 found. | session | **From Plan 4, and it is the find of the exercise.** The commissioned map (2–4 week lead time) and the province lookup mask that every click samples exist in exactly one place, and CLAUDE.md itself records that the registry is not safely regenerable (`--adjacency-only` clobbers the hand-authored sea-link folds and DEF-7 cuts). Five minutes caps a total-loss downside; the triage rides the same slice. | A clean board before anything is built on top of it. Closes the one user decision formally due. |
| **4** | **THE SHIPPABLE BUILD — "it runs on someone else's computer"** *(new row; no roadmap owns it)*. (a) frozen-bundle data path so `region.py` / `main.py` resolve `europe.json` + `europe_1805.json` under PyInstaller; (b) regenerate the spec against today's deps (it predates the July-18 anthropic-SDK migration); (c) **first-ever Godot client export**; (d) client supervises the backend — child process, negotiated port instead of `api_client.gd`'s hardcode, honest boot screen, die together; (e) saves/config under `%APPDATA%`; (f) **the front door (graft, Plan 1)** — a real main menu (New Game / Continue / Settings / Quit), in-client optional API-key field replacing the `config.txt` ritual, and set the shipping name/icon (`project.godot` still says "Project Sovereign" with the stock Godot icon while VISION and the export preset say *Ink and Iron*); (g) run it on a second machine with no Python, no venv, no repo. **Done = a stranger unzips it and plays in mock mode without editing a text file.** | multi-session (the plan's largest variance) | This is the biggest un-estimated item between here and EA and it is on no roadmap row. `deploy/` is dated March 10, 2026 — pre-cutover — and would ship a server with no world behind a launcher demanding a key the game does not need. Its true size could be one session or two weeks of antivirus, port and export-template trouble. **That variance is the schedule, and it must be measured while nothing is promised.** | Every downstream date: real-build screenshots, trailer capture, external testing, depot upload. Also collapses the "Monetization CRITICAL" row — with mock as the default and a key field in the UI, BYOK is finished here. |
| **5** | **Playtest Round 0** — 3–5 testers on the exported build, scored on exactly two questions: *could you launch it*, and *did you know what to do in the first ten minutes*. | non-coding | **From Plan 1, and it closes Plan 4's single worst gap.** Every measurement in this project's history has been the developer or an agent. This is the cheapest possible falsification of my own ordering of positions 6–12, placed at the first moment it becomes possible. Expect the unsigned-executable SmartScreen/Defender flag here — no test in the 15,901-suite can see it. | Evidence-based re-ordering below. If Round 0 says comprehension beats the missing ending, swap 6 and 12. |
| **6** | **Victory & Objectives — GATE, then VP-1 "The Emperor's Designs"** (France's own agenda deck on the NA substrate). **Bring Plan 3's five gate questions verbatim**, with these recommendations: objective-shaped, **not** a region race; two-to-three paths; the branch **irreversible**; **mark the triumph and continue** (protects EC-6); defeat rides existing W6-7 capture attrition if it can, which makes Phase 10 Marshal Death cleanly cuttable. **Carry Plan 4's churn number into the gate: 42 test files, 115 `game_over` assertions.** | gate + multi-session | The game cannot end — `turn_manager.py:1099` returns `game_over: False` as its mandatory first statement on every Europe world. It is the largest un-specced item on the board and a hard EA blocker. **And Plan 3 caught that it was unblocked one day ago:** `NATION_AGENDAS_SPEC` §9's stated blocker was *"design the pass after DEF-5 lands"* — DEF-5 landed Aug 2. Chaining rides deck priority for free; only **branching** is new machinery. | Three structurally-blocked rows at once: All-Dead Loss, Napoleon Comparison, 8.5 Campaign Objectives. And **honest store copy** — you cannot describe a campaign whose shape is undecided. |
| **7** | **VP-2 "The Ending"** — un-gate `_check_victory_conditions` for **design satisfaction only** (region race and max-turns defeat stay dead by contract), the triumph screen, the keep-playing arm, Napoleon Comparison, the loss condition the gate chose. **Surface the replay frame (graft, Plan 3):** Stage A's campaign seed and authored variance bands already make every Europe open differently within historical bounds and the game has never told anyone — say so on the new-campaign screen. | multi-session | The arc closes. Split from VP-1 so each lands green separately against those 115 assertions. | The trailer's payoff shot. Difficulty settings become meaningful. Achievements get a substrate. **Three replay drivers — branching, seed variance, the scoreboard — two of them already paid for.** |
| **8** | **Music & Sound (Core)** — audio-manager autoload (there is none), Master/Music/SFX/UI buses, volume sliders, wire the two orphaned parchment WAVs, extract and license-verify the three unopened zips into `THIRD_PARTY_LICENSES.md`. **Sourcing starts at position 4** (calendar lead time). **Carry Plan 2's licensing catch:** the cleared CC0 packs are SFX, not orchestral — public-domain *scores* and public-domain *recordings* are separate questions and must be resolved before a note ships. | multi-session | There is **no music in this game**: one `AudioStreamPlayer`, two battle SFX, no bus, and the entire Settings box is a UI-scale slider plus one checkbox. Largest perceived-quality jump per session available, and the **true** trailer blocker. | The trailer. The audio half of the Settings menu. The first-session impression, which is where a refund is decided. |
| **9** | **Marshal Voice Tier 1 + XR-5** — author the aggressive and cautious banks against the existing literal pattern; `enemy_voice.py` is the exact proven template (deterministic bank keyed by personality × situation, serialized counter, no RNG, display-only, mock-safe). **Conditional (graft, Plan 2): only if position 1's re-measure shows composition is fixed.** If the enemy phase still reads as farce, this slot becomes a second composition slice instead. | session–multi | The named deliverable file exists and is **one-third built** (literal only). Cheapest lever on the weak pillar, zero LLM cost, fully mock-safe. Absorbs XR-5 (Mack's 2-line quip pool repeating verbatim three times in one grind). | The quotable half of "they talk back" — trailer lines, and the launch-day answer if CR-6 slips. |
| **10** | **STEAM PAGE GOES LIVE** — copy, tags, screenshots from the *real* export. | non-coding | All four real prerequisites now exist: a Steamworks account (position 2, cleared weeks ago), a build that runs elsewhere (4), a sentence about what a campaign is *for* (6–7), and screenshots from the shipping build (4). | Wishlist compounding — the one resource that is strictly worse the longer you wait. |
| **11** | **CR-6 *proper* — Conversational Objection Negotiation.** Gate first: may the LLM classify a free-text rebuttal into the **existing deterministic** Insist/Trust/Compromise buckets with a bounded trust modifier? That is the Golden Rule 6 boundary case and it is the user's call. Mock fallback = today's three buttons, unchanged. Riders (tone parsing, pre-battle councils, the mechanical delegation incentive) come to the same table and I recommend cutting all three. | gate + multi-session | **The most VISION-central unbuilt feature in the repo** — ROADMAP's own row calls it *"the game's 'talk to your generals' fantasy fully realized."* Placed after 8–9 deliberately: if the gate returns *no*, the trailer is already made of positions 7–9 and nothing is stranded. Note the CR-6 gate slot was consumed once by the S5-D1 bare-attack mini-gate; **this is the other CR-6.** | The store page's central claim actually being in the build. |
| **12** | **Tutorial System + Short Waterloo Scenario + R159** — build `TutorialManager` (deferred from 6.5, never built), populate from the maintained `TUTORIAL_SCRIPT.md`, and use the legacy 19-region world (`SOVEREIGN_MAP=legacy`, drilled, zero code change) for a 10–15 turn on-ramp. | multi-session | Late on purpose, not deprioritized: a tutorial teaches *final* mechanics, and everything that changes mechanics is above this line. It also needs position 4's real build to be tested against. | Refund-rate control. For a 126-province natural-language game this is the difference between "impenetrable" and "unlike anything else." |
| **13** | **Pre-EA hardening + Playtest Round 1** — **UI-2d-1 first** (only open soft-lock class), then IGR-X9, EWC-F1, EWC-F2, S5-4; sweep NAD-1..4, VP-D2/D3, S5-D3; complete Settings (display/controls/LLM on-off); **code signing (graft, Plan 1)** so an unsigned PyInstaller server does not trip SmartScreen; 8–12 external testers on the near-final build. | multi-session | The open defect list is genuinely five rows, all P2/P3 — this codebase is in unusually good repair, so this is small. Round 1 is the last chance to find a launch-blocker cheaply. | Release candidate. |
| **14** | **Trailer** — commissioned at position 9, delivered here, added to a page that has been accumulating wishlists since 10. | non-coding | Its true prerequisites — audio, personality lines, a payoff moment, a validated loop — are all now landed. Commissioning earlier buys footage of a game that no longer exists by delivery. | The launch beat. |
| **15** | **EARLY ACCESS** | — | Ships a game that runs on a stranger's computer, ends, teaches itself, has sound, whose marshals speak in three voices and can be argued with in your own words. | Revenue, reviews, and a real signal about which cut items to patch first. |

**Honest total: ~22–30 build sessions plus two non-coding tracks.** At this project's demonstrated cadence, two to four months. The largest single variance is position 4 and that is exactly why it sits at 4.

---

## 2. THE THREE DECISIONS THIS ENCODES

### Decision 1 — Packaging goes before content, at position 4, before a single feature.

**Reasoning.** Almost everything left in this backlog is content on an engine that has proven itself across ~a hundred landing slices; its size is knowable within a session. Exactly one item's size is genuinely unknown, and it is invisible to every planning document in the repo: **nobody has ever produced a build of this game.** The one pipeline that exists bundles no project data (verified: `all_datas` is uvicorn+fastapi+starlette only), targets an entrypoint the cutover invalidated, and ships a `.bat` that demands an API key `llm_client.py` proves the game does not need. Whether that is one session or two weeks of antivirus, port-collision and export-template debugging **is the schedule**. Measure it while nothing is promised.

*To overrule:* if you already know the export works — if you have exported this client before and it ran elsewhere — drop position 4 to a single verification session and pull the Victory Pass to 4. Everything else holds.

### Decision 2 — The ending comes before all content polish, and it is mark-and-continue, never a race.

**Reasoning.** Two separate arguments converge. Commercially, a strategy game that cannot end is not shippable and the store copy at position 10 has to *say* what a campaign is; writing that copy against an undecided shape is a promise you owe strangers. Structurally, three other backlog rows are not merely unbuilt but **blocked** behind `sandbox_mode` — All-Dead Loss, Napoleon Comparison, Campaign Objectives — and unblocking them costs one gate. And Plan 3 caught the thing that makes it cheap: `NATION_AGENDAS_SPEC` §9's own blocker (*"design the pass after DEF-5 lands"*) was met on **August 2**. Chaining rides deck priority for free; only branching is new. The mark-and-continue shape is non-negotiable because the alternative — a 60-turn / 0.75-region race — is precisely what EC-6 killed to protect four passes of economy work.

*To overrule:* if you want the sandbox preserved as the shipping identity, say so at the gate and the pass becomes objectives-and-score-without-termination. That is a legitimate design, it still fixes the store-copy problem, and it is smaller. What is **not** available is shipping with no objectives at all.

### Decision 3 — The narrative budget goes to the pitch (CR-6, Marshal Voice), not to the newspaper (Gazette) or the stat block (Advisors).

**Reasoning.** Plan 2 costed the Gazette correctly and the costing is decisive: `backend/game_logic/` contains **zero LLM calls today** — the entire narration layer is deterministic templates and the only LLM is the parser plus CR-5b's flavor field riding it. The first LLM feature to enter game logic is not a content slice, it is an **architecture slice** dragging per-feature toggles, model selection, cost display, fallback discipline and mock parity with it, and it pulls three Pre-EA rows forward. Meanwhile the Aug-1 sweep diagnosed the weak pillar as **composition, not volume** — so a newspaper on top of a garbled enemy phase is more surface, not better surface. Advisors falls to the same test from the other side: the felt half (named voices, distinct registers) already shipped via DEF-1, Talleyrand's advisory system and the 15-diplomat roster; what remains is 2–3 stats touching five formulas, which no player feels. Those sessions buy CR-6, which is the sentence on the store page.

*To overrule:* if you'd rather ship the newspaper than the argument, swap 11 and a Gazette slice — but do it knowing you are also signing up for the LLM-infrastructure slice underneath it, and that EA would then launch with a three-button modal behind a "talk to your generals" tagline.

---

## 3. STEAM PAGE + LLC

**Placement: split the row in three and run the pieces at positions 2, 10 and 14.** All four plans reached this independently and all three judges endorsed it; treat it as settled.

- **LLC + Steamworks onboarding → position 2. No entry condition at all. Start this week.**
- **Steam page → position 10.**
- **Trailer → commissioned at 9, delivered at 14.**

### The entry condition: **rewrite it.**

`ROADMAP.md:658` reads: *"After Phase 8.5. Marshal voice, gazette, audio, and EU4-style map all working. This is when the game is trailerworthy."*

I checked all four. EU4-style map — **met** (cutover + U1–U6 + war-table pieces + shader hover + serif labels). Marshal Voice T1 — **one third built** (literal bank only, verified). Gazette — **zero** (its only trace is two forward-comments in `world_state.py:816` and `:2189`). Audio — **effectively zero** (one `AudioStreamPlayer`, no autoload, no bus).

So the condition is not *false* — it is internally consistent. It is stale in a more damaging way, and in three respects:

1. **It bundles three incompatible kinds of work behind one gate** — one legal item with weeks of external lead time, one marketing item, three build items. Gating an LLC on a narration feature costs months for nothing.
2. **It omits the two things that actually gate a Steam page** — a legal entity and a build that runs on a machine that is not yours. Neither appears in the condition.
3. **It names the wrong build item.** The four were chosen when they *were* the content plan. Since then the game grew a carved-wood Battle Diorama, a naval theatre with its own Trafalgar tableau, the Proclamation ceremony, formable nations, and a living AI diplomatic layer — every one more trailerworthy than a newspaper screen. **A gazette is not trailer footage.** It is the one named item that gates neither a page nor a trailer, and it is the item that has kept the page waiting.

### Replacement text — paste over `ROADMAP.md:656-664` as three rows

> **STEAM: LLC + Steamworks entity**
> *Entry condition: none. Start immediately; it gates the page, not the reverse.*
> Legal entity → EIN → business bank → Steam Direct app fee → tax/banking interview → app entry. Weeks of external lead time, zero code dependency. Nothing in the build queue may be sequenced ahead of this.
>
> **STEAM: Store page**
> *Entry condition: (a) a completed Steamworks account; (b) an exported build that runs on a machine that is not the developer's; (c) one sentence stating what a campaign is FOR — i.e. the Victory & Objectives Pass has landed.*
> Screenshots come from the shipping export, not a dev run. Existing evidence packs (`BD_TABLEAU_*`, `IGR_G*`, `NV7_NAVAL_DIORAMA_TRAFALGAR`) are already page-quality. Publish without the trailer; it can be added to a live page.
>
> **STEAM: Trailer**
> *Entry condition: Music & Sound (Core) + Marshal Voice Tier 1 + one polished 60-second loop with a payoff moment.*
> ~~Gazette~~ — struck. A newspaper screen is not trailer footage and gates nothing a trailer needs. ~~EU4-style map~~ — satisfied July 2026; stop citing it.

**While that section is open, fix two more things it contaminates:** the Critical Path list at `ROADMAP.md:920` repeats the same bundle verbatim, and the Phase Dependencies Graph at `:927-955` is obsolete on its face (it still gates Pre-EA on "Wire Regions + Balance," superseded July 2, and shows Phase 11 as future work when six of its seven rows have landed). Fix all three together or the contradiction regrows.

---

## 4. WHAT I AM CUTTING OR DEFERRING

Every row below lands in a named owner with a landing slice. Nothing becomes "future work."

### Cut to the first EA content updates — these are the patch cadence, and they are the best headlines this game will ever have

| Item | Reason | Owner row / landing |
|---|---|---|
| **Events System** (`ROADMAP:541`) | Largest unbuilt 8.5 row, needs its own gate, 4–6 sessions — and the evidence points the other way. The July-25 headline defect was **IGR-1: the campaign log drowned in machine-generated rows (24 of 25 events on turn 9)**, and IGR-F had to build a letter-book specifically to *reduce* interruption volume. Adding an authored deck to a game whose measured problem is interruption, and whose selling point is *derived* drama, is depth on depth. | New row **Post-EA: Events System**. Landing = EA content update 2. Completion = a gate that first asks whether the derived layer (petitions, ultimatums, proclamations, rivalry events, mediation offers) already covers it. |
| **Gazette "Le Moniteur"** (`:549`) | See Decision 3. Not a cheap feature riding an existing feed — the first LLM call ever to enter `backend/game_logic/`, dragging toggles/model-selection/cost-display/fallback/mock-parity with it. Least trailerworthy of the trio, and it is the item holding the Steam page hostage. | New row **Post-EA: LLM Narration Layer** (below). Landing = EA content update 1, as the *first* member built against that layer's contract. |
| **Imperial Governance** (duplicated at `:548` and `:725`, no spec) | The cut that costs most — it is VISION's own "Territory as Command Dilemma" and the substrate is unusually ready (ES-7 estates, The Steward, `respected_estates`, the petition channel). But it is multi-session, needs a gate, and it is *depth*, not shape. It lands better on a live audience already invested in their marshals. | **Merge `:548` and `:725` into ONE row under Phase 11** — they are the same feature written twice — then defer. Landing = EA content update 2–3. Completion = a spec exists before any code. |
| **Voice-to-Text** (`:770`) | Genuinely a killer feature for the fantasy, and genuinely four new unknowns (Whisper or browser SpeechRecognition, a cost line, a permission surface, a mic hardware matrix) bolted onto a text input that already works. Best EA-update announcement on the board; gates nothing. | Pre-EA row → **Post-EA**, paired with CR-6's follow-ups in the same marketing beat. Landing = EA content update 1. |
| **All LLM Tier-2+ narration** — Marshal Voice T2, Full Flavor T3, Napoleon's Desk LLM, Grouchy Moment LLM, Intercepted Dispatches, Marshal Memory, the five Diplomatic LLM Features | Cut as **one bundle**, because they share one uncosted dependency: the architecture slice above. Individually charming; collectively 5–8 sessions of atmosphere that changes no decision, for players who may have no key. | New row **Post-EA: LLM Narration Layer**. Landing = EA content update 1. Completion = the toggle/cost/fallback/mock-parity contract written **once**, then every member built against it. |

### Cut to post-EA outright

- **Phase 9 Advisors.** The felt half already shipped (Talleyrand's advisory system + war room + Assess verb; Berthier's reports; 15 bespoke diplomat registers post-DEF-1). What remains is an advisor object with 2–3 stats and five bonus seams — and the VISION promise (action gating) is *already* Post-EA by the roadmap's own design. **Rename the surviving pre-EA fragment "Advisor identity polish" (session, copy)** and be honest in the roadmap that Layer 1 is a post-launch promise rather than shipping a stat block and calling the layer done. → **Phase 9 becomes an EA-update phase.**
- **Token tiers + payment processing.** `LLM_MODE` defaults to `mock` and every slice ships mock-safe by standing rule — **the game is fully playable with no key**. That collapses the "CRITICAL" row: BYOK finishes inside position 4's key field. → **Pre-EA Monetization row re-scoped in place to "BYOK only"; payment → Post-EA revenue work.**
- **EC-2 pass 2 (ES-4 + ES-7b)**, and **strike `ROADMAP:544` "Light Tech/Reforms"** outright — it is the same mechanic as ES-4 with two owners and two gates. Economy is 7.5 after four passes and VISION never mentions it. → **`ECONOMY_REVISIT_SPEC.md`, post-EA.**
- **Battle Gallery + Battle History Screen** — two names for one feature. → **Merge into one row with the persistence question as its gate; post-EA.**
- **Phase 10 Marshal Death** — *conditionally* cut at position 6's gate. If defeat can ride existing W6-7 capture attrition ("your marshals are all in enemy hands," with the Marshalate bench as the recovery path), it is pure optional flavour — and death-by-percentage-roll sits badly against design philosophy #3, *personality over randomness*. → **Phase 10; post-EA unless the gate needs it.**
- **Steam achievements + cloud saves · difficulty settings · LLM cost display · per-feature model UI · Historical Moments beyond the Proclamation · ESP-3 · the Pre-EA Diplomacy & Flavor Content Menu** → post-EA, existing owner rows.
- **EC-P3** — keep the row, empty it mostly: pull **IGR-X9 only** into position 13 (razing wins at *any* plunder multiplier including ×0 — a player-discoverable dominant strategy, therefore a launch-balance defect). EWC-D1, NV-D3, NV-D9 stay for post-EA; the row's completion definition is disposition *in writing*, which this satisfies.

### Dropped at the gate, in writing

- **DEF-12 full map modes** — the cheap 3-position toggle shipped in Slice 7.5; the row's own completion definition explicitly permits "explicitly dropped at the gate." Take the exit and close it.
- **Pre-EA AI Depth Pass (MC-V-4)** — its charter authorizes this verbatim: *"if no pass materializes pre-EA, drop cleanly — no player promise outstanding."*

### Accounting strikes — no work, but the docs lie without them

Six of seven Phase 11 rows (`:721-727`) have landed — the Quick Status row already says so, the table was never updated · National Goals (`:542`) says NA-0+NA-1; the arc ran to NA-6d · Campaign Objectives (`:545`) duplicates the Victory Pass · Marshal Voice T1 (`:550`) and Command Echoing (`:557`) both understate what exists · "20+ Marshals" (`:817`) is done at 21 + 22 pooled · **AI Fog of War (`:823`) is already BUILT** — ROADMAP's own April-19 resolution note is correct; do not plan it again · `ROADMAP:15` cites "R19," defined nowhere in the live doc set (a GR9 violation inside the roadmap) · `DESIGN_REFINEMENT:402` R162 landed as NA-5 · `DESIGN_REFINEMENT:542` P2 Britain reactive bloc is probably delivered by AI-4a per-target threat + NA-3 §5.7 paymaster generalization — **needs a verification read, not a build.**

---

## 5. THE DISSENT

**The strongest argument against this sequence is Plan 2's, and it is this:**

> You have put the shippable build at position 4 and the ending at 6, and you have justified both as risk retirement. But **the risk you have actually retired is your own uncertainty, not the player's disappointment.** The measured floor of this game is not packaging — it is `AI_V_SWEEP_2026_08_01.md:472`, *"the enemy phase as theater: 5.5,"* the lowest score any pillar has ever received, diagnosed at `:482` as a composition failure and never re-measured since its five fixes landed. Your plan touches it once, at position 1, as a *side brief* on a campaign whose stated purpose is naval evidence — and then, if the news is bad, you have allotted it a single conditional slot at 9, thirteen positions before launch, behind a store page you have already published.
>
> Meanwhile you have spent positions 4 through 8 — the plan's entire middle — on work no player will ever describe. A frozen-bundle data path, a port negotiation, a `%APPDATA%` migration, a triumph screen, an audio bus. All necessary. **None of it makes the game better to play.** You will arrive at Early Access with a beautifully packaged product whose single worst-scoring surface is the one the player sees every single turn, for the whole campaign, forever.
>
> And your CR-6 placement compounds it. You keep the pitch feature — correctly — but you put it at 11, *after* the store page has already sold it. If that gate returns "no," or returns "yes, four sessions," you will have published a page promising a conversation and shipped three buttons.

**This is a serious argument and I want to be clear that I do not think it is wrong about the diagnosis — only about the ordering.** My answer has two parts. First, position 1 is a 30-turn played campaign in which the enemy phase runs 30 times; it is not a side brief, it is the best possible instrument for that pillar, and it costs zero extra sessions. Second, and decisively: an improvement nobody can install is not an improvement. Position 4 is not polish, it is the difference between shipping and not shipping, and `deploy/` proves it is currently broken in a way five months of green test suites never caught.

**What would make me switch to the dissent's ordering, concretely:**

1. **Position 1's re-measure comes back below 6.5 on the enemy phase.** Then the composition defect survived its own fix, it is a systemic problem rather than a residue, and it moves to position 3 — ahead of the shippable build — because at that point it is not polish, it is a broken core loop.
2. **Playtest Round 0 (position 5) says testers launched fine but described the turn as confusing, noisy or incoherent.** Round 0 exists precisely to arbitrate this, and if launch is easy and comprehension is broken, the dissent was right and positions 6–9 re-order behind a composition slice.
3. **Position 4 comes in at one or two sessions.** If packaging is easy, its early placement bought little and the risk-first argument for it evaporates; the sessions saved go to the enemy phase, not to the schedule.
4. **The CR-6 gate returns "yes, and it is large."** Then it moves ahead of the store page — I would rather delay the page by three sessions than publish a promise I have not yet built. This is the one item where I would let the marketing wait for the build.

**Two things I would not reorder on any evidence:** the LLC starting now (it is free and it is pure calendar), and the asset backup (five minutes against total loss of a paid commission that exists on exactly one disk).
---

## AMENDMENTS — the EA-scope refund test (August 3, 2026, same day)

The user pressure-tested three of this plan's calls: *"we have no sound and
such is that an issue?"*, *"and llm integration not set up for users etc"*,
*"and no news reel etc"*. A four-probe / four-refuter panel answered them.
**Two of the orchestrator's own claims were corrected, and the panel found
something worse than all three questions.**

**Sound — NOT an issue; the premise was wrong.** I had said the game is
"silent except during a battle tableau". `battle_diorama.py:344` sets
`significant = decisive or player_involved or great_battle`, and
`player_involved` is true for **any battle the player fights** — which fires
the cannon (`battle_diorama.gd:1229`) within minutes and constantly
thereafter. The honest model is **"battle audio, no soundtrack"**, which is
ordinary for EA strategy. Position 8 holds. Only the *shell* (autoload, bus
layout, sliders) moves to 4, because that is where the main menu, Settings
and `%APPDATA%` work already is.

**News reel — NOT an issue; the cut stands, and it is more redundant than
this memo argued.** The Morning Dispatch (`dispatch.py`, 2,552 lines)
already builds a scored newspaper every turn: `_build_headline` weighs
fog-visible events across 13 classes, wrapped in a situation column, a
foreign-affairs column, and a signed headline-aware editorial. Decisively,
`ROADMAP:601` scopes the EA gazette as *"written from French perspective"* —
single-voice, French, periodic prose. **That is the Dispatch.** The
architecture reason is KEPT, not demoted: the cut row says "via single LLM
call", so the objection targets exactly what is being cut.

**LLM for users — an issue, but the named half was already owned** (the
in-client key field is position 4, with the right Done criterion). The
unowned half is far worse and is now filed as **PARSE-NEG**.

### PARSE-NEG — the finding that outranks all three questions

`should_use_llm` escalates only **below** confidence 0.7. Reproduced
first-hand on the shipped board, keyless:

- `Ney, never attack Mack` → **attack**, 0.90
- `Ney, don't attack` → **attack**, 0.90
- `how do I attack?` → **attack**, 0.80
- `Ney, hold until Davout arrives then attack` → **attack now**, 0.90
- `Ney, if Mack advances fall back to Alsace` → **move now**, 0.95

All above the gate, so **the LLM is never consulted — buying a key does not
fix it**. Negation contains the same keywords as its affirmative, so it
scores *higher* and is structurally shielded from the one component that
could catch it. Full row, four sub-defects and the bounded fix:
`BUG_FIXES.md` §PARSE-NEG. It is a correctness bug, not a scope decision,
and it does not wait for position 11.

**Also found:** making mock the shipped default **arms the cheat console** —
`meta_executor.py:2037-2043` refuses cheats only when `live_client_armed`,
which is false without a key. Not a code bug; a design assumption ("mock
means dev") that position 4's own mock-default decision invalidates.
Re-gate on explicit debug, in that same slice (~1 hour).

**Dismissed as non-gaps** (checked, not assumed): save/load UI exists;
save migration is sane (`FORMAT_VERSION=3`, hard-reject with a clear
message); turn latency 23.1ms under a 15× tripwire; main menu is 4(f);
tutorial is 12; code signing is 13.

**Net plan change: positions 3, 4, 5, 8 and 10 amended. No 16th position.
Nothing moves in front of Victory.**
