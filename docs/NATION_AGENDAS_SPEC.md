# Nation Agendas — "The Designs of the Powers"

**Status:** v1.3 — ✅ **DESIGN GATE HELD July 17, 2026; NA-0 + NA-1 LANDED July 17, 2026** (landing record §12); ✅ **NA-2 Diplomacy Teeth LANDED July 17, 2026** (landing record §13); ✅ **NA-3 War Coupling LANDED July 17, 2026** (landing record §14); ✅ **NA-0..3 live verification PASSED July 17, 2026** (§15); ✅ **NA-5 Ultimatums LANDED July 18, 2026** (landing record §16); ✅ **NA-6a formation core + NA-6b The Proclamation LANDED July 18, 2026 — the build PAUSES for user review before NA-6c/NA-6d** (landing record **§17**, authoritative where it records conscious deviations from §11.10); ✅ **WHOLE-PHASE REVIEW HELD July 18, 2026 — record §18**: a 21-agent arc-level sweep found ONE P1 that three slice-scoped reviews had all missed (the anti-hegemon designs deleted themselves the moment the coalition out-massed France) plus two P2/P3, all FIXED. **v1.3 amendment (July 18, 2026):** §11.10 — the **NA-6 build plan of record** (sub-slices NA-6a..NA-6d, seam map, pinned decisions), added so the build session can execute §11 without design judgment calls; plus the §7 numbering note (there is no NA-4). The user answered the three gate questions at the recommended defaults (§0). This spec is the gate record AND the build contract for the Phase 8.5 centerpiece. **v1.1 amendment (July 17, 2026, same day — user-blessed):** dormant satellite decks (KingdomOfItaly, Holland) authored at NA-0 (§4), the owned follow-on slice **NA-6 "Formable Dreams"** (§11 — formation rewards + post-formation goals + the Duchy-of-Warsaw new-tag creation pathfinder), **Free Ireland homed to DEF-5** (naval phase; §9/§11.5), and the player-France Victory-Pass seed note (§9). **v1.2 amendment (July 17, 2026, user-directed with the NA-0/NA-1 landing):** the Warsaw→**Poland** formation chain WITH political implications (§11.2 row + §11.9 aggrieved-powers contract), the **Roman Republic** formable (§11.2 row — the 1798 carve from the Papal States, with the risorgimento interplay and the one-province-elimination pin), and the assured **Formables button for France** (§11.6-8). All three are NA-6 scope — documented here per the phasing, not built at NA-0/NA-1.

**Owner queue position:** Phase 8.5 "Events, Goals & National Identity" — the re-scoped Nation Agendas core promoted at 8.EVAL (`docs/audits/EVAL_8_2026_07_16.md` §1/§3). Consumes: **R123** (econ-strategy triggers), **R124** (isolation/alliance-splitting), **A3** (enemy-AI war-vs-diplomacy choice), **R155 residual** (personality-driven timing/persistence/target choice), **R156** (diplomacy strategic optionality). **R162** (AI ultimatums) is owned here as the follow-on slice NA-5 (§8) — its gate questions are answered in this document; no further gate.

---

## §0 Gate record (July 17, 2026 — authoritative)

Three questions asked; all three answered at the recommended option:

| # | Question | Decision |
|---|----------|----------|
| G1 | Architecture | **Authored decks + dynamic activation.** 1–3 hand-authored historical agendas per nation (scenario JSON, validator-checked); the ACTIVE agenda is derived each turn from live state. Rejected: single static agenda (no posture shifts); fully emergent goals (ahistorical, illegible, untestable). |
| G2 | Mechanical teeth | **Full coupling in pass 1.** Acceptance term + war resolve + AI target bias + paymaster subsidies + agenda-driven separate peace + derived post-peace grudge. Rejected: diplomacy-only (armies wouldn't march on what their court claims to want); legibility-first (repeats W6-10 — voice without intent — and leaves R156 unmoved). |
| G3 | R162 ultimatums | **Owned follow-on slice NA-5.** Gate questions answered in §8; built AFTER NA-0..NA-3 land and are verified live. Rejected: fold into pass 1 (adds popup/Godot surface to the first landing's risk); keep gated (weakest GR9 shape). |

Blessed numbers live in §6 — in-band tunable per the standing rule; structural changes escalate.

---

## §1 Problem & scope

**The gap (verified July 17, 2026 against master):** nations have no strategic intent. Austria, Prussia, and Britain run the identical per-marshal enemy-AI tree (`enemy_ai.py` P0–P8); the only objective-driven behaviors are the liberation war-objective (P3.8, `enemy_ai.py:1705`) and jealousy glory (P3.9, `:1715`). Per-nation variation today is authored *stats* (gold, power tier, honor bias, diplomat personality) — never a *goal*. `docs/ENEMY_AI_REFERENCE.md`'s own TODOs (":805/:813") reserve "Phase 8.5 National Goals / Tiered Nation AI" for exactly this system.

**What already landed (do NOT rebuild):** the motive-LEGIBILITY half of old queue item 5 — W6-9 war room + assess chip, W6-10 `diplomat_line` register bank + ask variety + 6-turn type cooldowns, UI-6 surfaces, DEF-1 voices. This spec adds *intent behind the voice*, reusing those surfaces.

**Explicitly OUT of scope (GR9 homes, §9):** player-France goals (→ Pre-Ship Victory & Objectives Pass; the sandbox stays open-ended), AI-AI war *declaration* (→ ROADMAP 8c AI Strategic Depth — agendas may bias an *existing* war, never start an AI-AI one), naval-flavored Britain agendas (→ DEF-5), trade-pressure verbs (→ EC-8 economic diplomacy).

---

## §2 Design rationale (history · gameplay value · dynamism)

**History.** In 1805 every great power's aims were common knowledge — that's why the system carries no fog (standing project rule: diplomacy has no fog). Austria fought to redeem Italy and its position in Germany (the Italian theater under Charles was the *priority* theater; Mack's Swabia thrust the secondary). Prussia sat in armed neutrality coveting Hanover — Napoleon dangled it at Schönbrunn, and Bernadotte's march through Ansbach nearly brought Prussia in; both are mechanics here (§4, §5.9). Britain's two constants were the Low Countries out of French hands and Pitt's subsidy millions. Russia campaigned as the arbiter of the European order — while British gold flowed. Authored decks encode these *specific, recognizable* intents; a goal generator would produce plausible-but-anonymous wants.

**Gameplay value.** Agendas make AI behavior *explainable* (Austria refuses your peace because it doesn't return Milan — and the acceptance breakdown says so), and diplomacy *strategically real* (R156): you can now buy Prussia's neutrality with Hanover instead of garrisoning the north, satisfy Austria at the table to crack a coalition (the Pressburg pattern), or watch a denied Austria carry its grudge into the next coalition (1809). Enemy armies march toward what their court demands, so the map finally *shows* intent.

**Dynamism.** The deck is authored; the ACTIVE agenda and its pursuit intensity are derived per-turn from live state — war score, territory control, bloc share, treasury, exhaustion. A nation whose agenda is satisfied mid-war sues to lock its gains; one whose homeland burns drops its ambitions for survival; one denied at the table feeds the next coalition. Derived-not-stored follows the `get_authority_proxy` idiom (`jealousy.py:351`) — reconstructed from world state, (almost) nothing new serialized, save/load-safe by construction.

---

## §3 Architecture

### §3.1 Agenda types (code-owned predicate semantics)

A small closed set of parameterized types in a new `backend/game_logic/agendas.py`. The scenario authors *instances*; the code owns each type's activation predicate, satisfaction condition, and consumption hooks. All predicates are pure reads of live state (relations, `get_nation_regions`, bloc share via `coalition._identify_max_bloc_share`, treasuries, war state) — deterministic, GR6-clean.

| Type | Params | Active while… | Satisfied when… | Primary expressions |
|------|--------|---------------|-----------------|---------------------|
| `acquire_regions` | `regions[]` | ≥1 target not controlled by self (and holder is not self's vassal) | all targets self-controlled | target bias, acceptance, resolve, ultimatum subject |
| `deny_regions` | `regions[]` | ≥1 target controlled by the hegemon's bloc (share ≥ 0.33) | every target held by self/own client, **or** by a below-major power outside the hegemon's bloc (§19) | resolve, acceptance, subsidy targeting — never self-conquest |
| `contain_hegemon` | `share_floor` (default 0.33) | hegemon bloc share ≥ floor AND self outside that bloc | share < floor | coalition resolve (fights longer in coalition wars), proposal motive |
| `paymaster` | `treasury_floor` | at war with the hegemon OR active coalition vs hegemon, AND treasury > floor | — (posture, not a quest) | subsidy escalation (§5.7), gold-flavored asks |
| `guard_neutrality` | `regions[]` (the guard set) | self at peace | — (posture) | cheap refusal of coalition asks; the violation trap (§5.9) |

**Built-in survival override — "The Knife at the Throat" (not authored):** for every nation, if the capital is lost or the majority of `nation_starting_regions` is lost (the `get_authority_proxy` 25-band, `jealousy.py:351-374`), the deck is overridden by an implicit survival posture: resolve pushes toward peace (§5.5 `SATISFIED` arm semantics), no target bias, ledger shows "Survival — the dynasty above all." Checked first, before the deck.

### §3.2 Authoring & validation

New scenario key `agendas` in `europe_1805.json`: `{nation: [{id, type, title, blurb, regions?/params…}, …]}`. **Deck order = priority order** — first agenda whose predicate holds is ACTIVE (exactly one active per nation; the rest are latent and visible via the war room). Validator support in `backend/modding/validator.py` on the `marshal_pool` precedent (`validator.py:436-513`): type-check the container, enum-check `type`, cross-validate `regions` against the region registry and nations against the roster (warning-not-error for unknown nations, matching the `relationships` forward-compat stance). New `MODDING_FORMAT.md` row. Nations without authored decks (minors, satellites) get no deck — survival override only; vassals never activate agendas while vassalized. **A satellite MAY carry an authored deck that lies dormant under that rule and wakes on independence — the v1.1 formable hooks (KingdomOfItaly, Holland; §4, §11).**

### §3.3 Derivation & caching (GR8)

`agendas.get_active_agenda(nation, world) -> Optional[AgendaView]` — per-turn cached on the `_active_nations_cache` idiom (`world_state.py:1549-1579`): cache + `cache_turn`, rebuilt when `current_turn` moves, invalidated from `invalidate_active_nations_cache()` (region control changes activation). One evaluation per nation per turn; predicates use only cached helpers (`get_nation_regions`, `get_active_nations`) — no per-region scans in hot paths.

### §3.4 Serialization

**ONE new world field:** `world.nation_agenda_seen: Dict[str, str]` (nation → last-announced agenda id) — powers the shift dispatch beat exactly like `last_expectation_seen` (dedup across save/load). Full serialization checklist applies. The post-peace grudge (§5.8) is **derived** from `war_instances` `ended_turn` + current agenda state — no field. The neutrality-violation latch (§5.9) rides the event log like `_calculate_defensive_refusal_memory_threat` — no field.

### §3.5 Golden-rule statements

- **GR5:** every seam takes a nation parameter; nothing is Britain/Austria-hardcoded (Britain merely *authors* `paymaster`; the paymaster machinery generalizes `_process_british_subsidy` — any authoring nation works).
- **GR6:** activation, resolve, targeting, acceptance are deterministic; the LLM only ever *voices* an agenda (motive lines).
- **GR8:** one cached evaluation per nation per turn; grudge/violation scans are bounded event-log lookbacks.
- **GR9:** every cut is homed in §9.

---

## §4 The authored 1805 decks

Region names verified against the live registry (there is no "Lombardy"/"Venetia" — Milan/Piedmont/Savoy are the Italian provinces). Deck order = priority. Titles are the player-facing display strings.

| Nation | # | id | Type | Targets/params | Historical grounding |
|--------|---|----|------|----------------|----------------------|
| **Austria** | 1 | `redeem_italy` | acquire | Milan, Piedmont, Savoy | The priority theater of 1805 — Charles held the main army in Italy; Campo Formio/Lunéville losses. |
| | 2 | `primacy_germany` | acquire | Munich, Swabia | Mack's thrust to the Iller; contesting Bavaria's defection to France. (Boot-active pin: Mack@Swabia — but `redeem_italy` outranks it while Milan is French-bloc.) |
| **Prussia** | 1 | `hanoverian_prize` | acquire | Hanover | Schönbrunn: Napoleon's bait; Prussia occupied it in 1806. The buy-Prussia lever. |
| | 2 | `armed_neutrality` | guard_neutrality | Hanover, Westphalia, Brunswick, Berlin, Brandenburg | Ansbach: a belligerent marching through north Germany enrages Berlin (§5.9). |
| **Britain** | 1 | `low_countries` | deny | Flanders, Brabant, Amsterdam | The Scheldt obsession — the invasion coast may not be French. Britain won't rest while the bloc holds them. |
| | 2 | `paymaster` | paymaster | treasury_floor 2000 | Pitt's gold: £1.25M per 100k men, 1805 subsidy conventions. |
| **Russia** | 1 | `arbiter_of_europe` | contain_hegemon | share_floor 0.33 | Alexander as guardian of the European order; fights the hegemon while the coalition stands. |
| **Sweden** | 1 | `scourge_of_the_usurper` | contain_hegemon | share_floor 0.33 | Gustav IV's personal anti-Napoleon zeal. |
| **Ottoman** | 1 | `guard_the_straits` | guard_neutrality | Constantinople, Rumelia | Porte neutrality; the Straits inviolate. |
| **Sardinia** | 1 | `house_of_savoy_restored` | acquire | Piedmont, Savoy | The court in Cagliari wants its mainland back — instant flavor for a minor. |
| **Denmark** | 1 | `neutrality_of_the_north` | guard_neutrality | Jutland, Copenhagen | Armed neutrality; the fleet is the state. |
| **KingdomOfItaly** *(dormant satellite deck — v1.1)* | 1 | `risorgimento` | acquire | Milan, Piedmont, Savoy, Naples, Rome | Latent while vassalized (§3.2 rule); WAKES on independence (rebellion or VS-6 defection) — the freed vassal marches with a national dream. NA-6 formation entry: satisfying it while free forms **Italy** (§11). |
| **Holland** *(dormant satellite deck — v1.1)* | 1 | `the_seventeen_provinces` | acquire | Flanders | Latent while vassalized. A free Holland reaching for the Austrian-Netherlands inheritance. Deliberate interplay: an INDEPENDENT Netherlands holding Flanders *satisfies* Britain's `low_countries` deny agenda (the province leaves the hegemon's bloc) — freeing Holland is a diplomatic lever against London's war. NA-6 formation entry → **United Netherlands** (§11). |

**No decks (survival override only):** France (player — Victory Pass owns player goals; v1.1 seed note §9), Spain/Naples/Portugal and all minors not listed, and the satellites Switzerland/Bavaria/Saxony/Hesse/Hanover/PapalStates. **KingdomOfItaly and Holland carry authored DORMANT decks (v1.1, rows above)** — vassals never activate agendas while vassalized, so both lie latent until independence; the formation layer on top of them is NA-6 (§11). **Cut with owner:** Russia `eastern_question` (Constantinople/Rumelia — needs AI-AI war declaration; § 9 → ROADMAP 8c).

---

## §5 Consumption seams (all file:line refs verified July 17, 2026)

### §5.1 Legibility (slice NA-1)

- **Nations tab:** add `agenda: {id, title, stance_line}` to the per-nation row dict (`diplomatic_ledger.py:370-388`, beside `bloc_stamp`); `diplomatic_ledger.gd` renders one line. Un-fogged like relations (DPF-1). Stance line states the *live* posture, e.g. "Vienna will not rest while the French sit in Milan."
- **War room (W6-9):** per-nation agenda line in the wars loop (`diplomatic_advisory.py:304-317`) + an **agenda-driven recommendation branch** in `_build_situation_recommendation`'s priority ladder (`:176`): when a war opponent's active agenda could be satisfied at the table, the ONE recommendation becomes "satisfy their design" with an executable `request_terms`/`open_proposal` option (existing `execute_suggestion` plumbing).
- **Motive lines:** new decision reason `"agenda_pursuit"` in `_MOTIVE_REASONS` (`diplomatic_templates.py:526`), register-bank rows for all 5 registers (`:75`) + named overrides (Metternich, Hardenberg, Castlereagh) (`:165`); returned from `determine_ai_offer_decision_reason` (`diplomacy.py:7182`) when a proposal is agenda-driven. Composer falls back cleanly for unknown reasons — forward-safe.
- **Dispatch beat on shift:** compare `get_active_agenda` vs `world.nation_agenda_seen`; on change, one dispatch line ("Austria's court turns its eyes to Italy.") + update the seen map. Campaign-log event type registered per the new-action checklist steps 10–11.

### §5.2 Acceptance term `agenda_mod` (NA-2)

New bounded helper `agendas.agenda_acceptance_mod(proposal, world) -> int`, computed in `calculate_acceptance` and added as a **standalone additive term outside the composite floor** — the `respected_estate_value` precedent (`diplomacy.py:6834-6847`, sum at `:6849`). An offer whose clauses **advance** the target's active agenda (cedes/returns a target region, or ends a war denying one): `+AGENDA_ACCEPT_ADVANCE`. An offer that **entrenches denial** (asks the nation to accept/legitimize the loss of its targets): `AGENDA_ACCEPT_ENTRENCH`. Wire: `components` dict (`:6923`), `_generate_feedback` trackable set (`:6980`), `_COMPONENT_LABELS` in `get_diplomatic_preview` (`:10448`) — so it appears in the R17d top-3 breakdown and the player can *see* "Advances their design: +12".

Also in NA-2: **unify the covets source** — `generate_suggested_terms` / `_has_bargain_strategic_interest` read `NATION_DESIRE_PROFILES.covets_regions` (`diplomatic_templates.py:2626`, `diplomacy.py:4643`); active-agenda targets become the authoritative first source with the profile as fallback, and the **two dead `NATION_DESIRES` territory rows are deleted** (`ai_diplomacy.py:78-82`, `:99-100` — unreachable since the territory branch was removed; the 8.EVAL AUD-d disposition said delete either way).

### §5.3 Proposal timing / persistence / target choice — R155 residual (NA-2)

Agenda-matching proposal types (asks that would advance the active agenda) get: hawk diplomats re-ask with per-type cooldown reduced by `AGENDA_PERSISTENCE_COOLDOWN_DELTA`; the P3 relation-band candidate list (`ai_diplomacy.py:690`) prefers agenda-flavored asks when one qualifies; the proposal carries `decision_reason="agenda_pursuit"` so the register bank voices WHY. Doves/loyalists get no cadence change — personality stays the governor (hawk persists, dove asks once).

### §5.4 Isolation & separate peace — R124 (NA-2)

- **The Pressburg arm:** the P1 coalition-loyalty override (`ai_diplomacy.py:830-838`) gains one arm — a coalition member whose active agenda is **satisfied** (or whose survival override is active) may sue at `war_score < AGENDA_SEPARATE_PEACE_SCORE` instead of the stock −50. A nation that got what it wanted — or is fighting for its life — breaks ranks.
- **Buy-them-out:** no new machinery — §5.2's `agenda_mod` on separate-peace offers IS the isolation lever; the existing separate-peace fallout penalties (`diplomacy.py:3865-3941`) already price the betrayal side. *(NA-2 landing note: the lever is live on the BILATERAL chokepoint; the multilateral settlement scorer's per-court term is the owned NA-3 rider (a) in §7 — found by the NA-2 adversarial review.)*
- **Courting bias (small rider):** a nation whose acquire/deny targets lie in a player-vassal's territory prioritizes that vassal in the existing courting machinery — bias only, no new verbs.

### §5.5 War resolve — A3 (NA-3)

Single source `agendas.get_agenda_resolve_delta(nation, opponent, world) -> int`, applied to `effective_p1_threshold` (`ai_diplomacy.py:805-811`):

- War **advances** the agenda (opponent's side holds target regions): `AGENDA_RESOLVE_ADVANCING` (more negative threshold → fights longer).
- Agenda **satisfied** during the war (targets secured), or survival override active: `AGENDA_RESOLVE_SATISFIED` (sues sooner — locks gains / saves the dynasty).
- War irrelevant to the agenda: **0** — deliberately no change, protecting the freshly-tuned AUD-b/P2 armistice behavior.

`contain_hegemon` treats coalition wars against the hegemon as advancing while the share stays ≥ floor. This IS the A3 war-vs-diplomacy choice, expressed at the exact seam where sue-vs-fight is already decided.

### §5.6 Enemy target bias (NA-3)

Per the substrate finding, integrate as **target-selection bias, not a new rung** — the survival tree (P0–P3.7) is inviolate:

- `_get_strategic_enemy_regions` (`enemy_ai.py:575`): order agenda target regions first for the marshal's nation (memoized per nation/turn already).
- P4 pick (`:2598-2605`) and P7 nearest-target pick (`:3771-3779`): prefer an agenda target when it is otherwise valid (ratio/threshold gates unchanged) — implemented as a sort tiebreak plus `AGENDA_TARGET_DISTANCE_BONUS` distance-equivalent credit.

Result: Austria's corps drift toward Milan/Munich rather than the nearest anonymous province — the map shows the court's intent. `docs/ENEMY_AI_REFERENCE.md` is updated in the same slice (and its known drift fixed: the missing P3.8/P3.9 rows, the P4.78→P7.4 relabel).

### §5.7 Paymaster — R123 (NA-3)

Generalize the British subsidy pair (`coalition.py:1006` recipient / `:1040` processor) to key off "coalition member with an active `paymaster` agenda" instead of the Britain literal (GR5). Amount escalates with treasury: base 200/turn, `AGENDA_SUBSIDY_TIER_2 = 300` above 4,000 treasury, `AGENDA_SUBSIDY_TIER_3 = 400` above 8,000; cap `AGENDA_SUBSIDY_CAP = 400`. The +5 relation nudge and `war_support_delivered` contribution event ride unchanged. (EC-W2's treasury-fraction War Effort cost makes hoarding expensive; the paymaster gives Britain's hoard its historical outlet.) Trade pressure explicitly NOT built (→ EC-8).

### §5.8 The post-peace grudge — derived (NA-3)

A nation at peace with France whose active `acquire`/`deny` agenda remains denied (targets still in France's bloc), and whose war with France ended within `AGENDA_GRUDGE_TURNS`, contributes `+1` threat/turn via a new standing contributor in `process_coalition_turn` step 2 (`coalition.py:1657-1666` — the fourth sibling of hegemony pressure, defensive-refusal memory, and DD8 markers), capped at `AGENDA_GRUDGE_CAP` total across all nations, source-keyed `agenda_grudge` so the threat panel names it. **Fully derived** from `war_instances` `ended_turn` + live agenda state — zero new fields. This is 1809 in machinery: the peace that denies the design feeds the next coalition.

### §5.9 The neutrality violation — the Ansbach trap (NA-3)

For an active `guard_neutrality` agenda: a belligerent nation (at war with anyone, **not at war *or armistice* with the guard-holder** — §19 amendment; an armistice is a pause in a war, not a restoration of neutrality, so it neither wakes the paused opponent's guard nor strips the exemption from the army standing there because of that war — not its ally/lord) with a marshal standing in a guard region triggers a one-time violation: relation `AGENDA_VIOLATION_RELATION_PENALTY` between violator and guard-holder + a dispatch/campaign-log beat ("Berlin seethes: foreign columns cross Ansbach."). Latch = bounded event-log lookback (the `_calculate_defensive_refusal_memory_threat` idiom) keyed (violator, guard-holder) — fires once per pair per `AGENDA_VIOLATION_COOLDOWN` turns. Applies to the player and AI alike (GR5): marching the Grande Armée through north Germany costs Prussia's goodwill, exactly as it did Napoleon.

---

## §6 Blessed numbers (in-band tunable; structural changes escalate)

| Constant | Value | Bound sanity |
|----------|-------|--------------|
| `AGENDA_ACCEPT_ADVANCE` | +12 | vs respected_estate +5, hegemony −20, composite floor −60; one active agenda caps exposure at ±12 |
| `AGENDA_ACCEPT_ENTRENCH` | −8 | |
| `AGENDA_RESOLVE_ADVANCING` | −8 | on `effective_p1_threshold` (base −40; WE + ticking already reach ±20) |
| `AGENDA_RESOLVE_SATISFIED` | +10 | |
| `AGENDA_SEPARATE_PEACE_SCORE` | −30 | vs stock coalition-loyalty −50 |
| `AGENDA_PERSISTENCE_COOLDOWN_DELTA` | −2 turns | hawks only; W6-10 type cooldown is 6 |
| `AGENDA_TARGET_DISTANCE_BONUS` | 2 | distance-equivalent credit in target picks |
| `AGENDA_SUBSIDY_TIER_2 / _3 / _CAP` | 300 / 400 / 400 | base 200 unchanged; Britain boots richest |
| `AGENDA_GRUDGE_TURNS` | 10 | matches war-objective cleanup horizon |
| `AGENDA_GRUDGE_CAP` | +2/turn | vs defensive-refusal cap 3, DD8 cap 4 |
| `AGENDA_VIOLATION_RELATION_PENALTY` | −25 | one-time per pair per cooldown |
| `AGENDA_VIOLATION_COOLDOWN` | 10 turns | |
| `PAYMASTER_TREASURY_FLOOR` | 2,000 | authored per-instance param |

---

## §7 Build slices & cadence

Per the standing slice-review cadence: **land NA-0 + NA-1, then pause for user review** before the teeth slices.

| Slice | Content | Completion definition |
|-------|---------|----------------------|
| **NA-0 Substrate** | `agendas.py` (types, predicates, cached `get_active_agenda`, resolve/acceptance/bias helpers as pure functions), scenario `agendas` key + authored §4 decks **incl. the v1.1 dormant satellite decks (KingdomOfItaly `risorgimento`, Holland `the_seventeen_provinces`)**, validator block, `MODDING_FORMAT.md` row, `nation_agenda_seen` serialization (+ SAVE_FORMAT_REFERENCE). No consumer changes. | Boot pins green: Austria active=`redeem_italy`, Prussia=`hanoverian_prize`→`armed_neutrality` (peace predicate), Britain=`low_countries`, Russia=`arbiter_of_europe`; survival override pin (capital lost → override); cache-invalidation pin; serialization round-trip; **v1.1 dormancy pins: both satellite decks INACTIVE while vassalized, ACTIVE the turn the nation is free (unit-level independence flip — no formation layer yet).** |
| **NA-1 Legibility** | §5.1 in full: ledger row + `.gd` render, war-room lines + recommendation branch, `agenda_pursuit` motive reason + register bank, dispatch shift beat + campaign-log type. Touches `.gd` → **boot the engine, grep `SCRIPT ERROR`** before landing. | Ledger/war-room/motive/dispatch tests; live curl of `/diplomatic_ledger`; the standing new-dialogue rules do NOT apply (no new popup — existing surfaces only). |
| **NA-2 Diplomacy teeth** | §5.2 `agenda_mod` + full component/label/feedback wiring; covets unification + dead `NATION_DESIRES` territory-row deletion; §5.3 R155 cadence; §5.4 Pressburg arm + courting bias. | Acceptance-component pins both directions; preview shows the term; hawk-persistence pin; coalition-member separate-peace pin; corpus untouched (no new player verbs). |
| **NA-3 War coupling** | §5.5 resolve deltas; §5.6 target bias + `ENEMY_AI_REFERENCE.md` update (incl. drift fixes); §5.7 paymaster generalization + tiers; §5.8 grudge contributor; §5.9 violation trap. **Plus two NA-2-review riders (homed July 17, 2026):** (a) the **settlement per-court agenda term** — §5.4's "buy-them-out" lever exists today only on bilateral separate-peace offers; the multilateral settlement scorer (`settlement_scoring.calculate_common_peace_acceptance`) gains the same bounded ±12/−8 per-court term so a common-peace package ceding Milan prices Austria's satisfaction (pin: a settlement clause ceding a design target raises that court's acceptance by `AGENDA_ACCEPT_ADVANCE`); (b) **preview positive-row legibility** — the R17d `acceptance_preview` scores a bare mock, so "+12 Advances their design" never appears there; NA-3 scores the peace-class preview on `generate_suggested_terms` output (which now injects the design cession), making the positive row reachable (pin: preview positives contain `agenda_mod` when the suggested peace carries a design cession). | M1–M7 sweep harness **byte-identical or consciously re-blessed** (the harness roster's agenda exposure must be checked first); resolve pins (advancing fights longer / satisfied sues); target-bias pin (Austria corps prefers Milan-ward valid target); paymaster tier pin; grudge + violation pins both sides (GR5); the two rider pins above. |
| **NA-5 Ultimatums (follow-on)** | ✅ **LANDED July 18, 2026** — §8 built at the gate answers; landing record **§16**. | §8 completion definition — MET (`test_nation_agendas_ultimatums.py`, 35). |
| **NA-6 Formable Dreams (follow-on, v1.1+v1.2)** | §11: the formation layer — Class T transforms (KingdomOfItaly→**Italy**, Holland→**United Netherlands**: identity + one-time reward + post-formation goals via deck order) + **generalized Class C carve-out creation** (ANY conquering side carves a client from the defeated party's soil — **Duchy of Warsaw** from Prussian Posen, the **Duchy of Normandy** coalition-side mirror from French home soil, and the v1.2 **Roman Republic** from Papal Rome) + the v1.2 **Warsaw→Poland C→T chain with §11.9 political implications** (aggrieved partitioners: relation blow + the "Polish Question" grudge) under the **§11.6 UX contract** (wizard-first honest-availability clause, full-bargain preview, legible incoming offers, immediate flag/ledger, "forms:" progress marker, **the §11.6-8 Formables button for France**). Built after NA-5. **Build plan of record = §11.10 (v1.3): sub-slices NA-6a → NA-6b → user-review pause → NA-6c → NA-6d, with the seam map and pinned decisions — follow it in order.** | §11.7 completion definition (incl. the v1.2 additions), distributed across the §11.10 sub-slice completion bars; `tests/test_nation_agendas_formables.py`. |

**Numbering note (July 18, 2026):** there is **no NA-4** and never was — the gate-day table numbered the core build NA-0..NA-3 and the follow-ons NA-5/NA-6; the unnumbered §15 live-verification step occupies the sequence slot between them. The identifiers are frozen (they anchor gate records, landing records, commits) — do not renumber.

Every slice: ruff clean, full suite green, `tests/test_nation_agendas.py` grows with the slice; NA-1's `.gd` touch follows the XR-1 boot-smoke rule. Docs: SYSTEMS_REFERENCE gains §28 Nation Agendas at NA-3; STATUS/ROADMAP per landing.

---

## §8 R162 — AI ultimatums to the player (gate answers; owned slice NA-5)

Answered here so NA-5 needs no further gate:

- **Trigger (when is an ultimatum better than war?):** a new ai_diplomacy rung between P7 opportunism and P8 — fires when: active `acquire` agenda targeting player-bloc regions · at peace with the player · relation < 0 · nation not in the player's bloc · fog-free national strength ≥ 1.25× the player's (the diplomatic-ledger strength basis) · cooldown 15 turns per nation, max one live ultimatum world-wide. Building Blocks: terms via the player's own `generate_ultimatum_terms` with the agenda target as the demand; acceptance direction inverted.
- **Threat direction:** issuing does NOT reduce the player's threat level (an AI demand is not exculpatory). Player **rejection** plants a bounded expiring pressure marker (DD8 `schemer_rejection_pressure` idiom) — the aggrieved court pushes the next coalition harder. **No unilateral AI declare-war path** in NA-5 (that machinery belongs to ROADMAP 8c); the coalition system remains the war-maker.
- **Player surface:** the existing incoming-proposal/mailbox transport + typed Accept/Reject. Per the standing dialogue-popup rule: new dtype in the `main.gd` whitelist + `proposal_result_popup` on conclusion. Accepting cedes per normal ratification (existing clause processing).
- **Completion:** `test_nation_agendas_ultimatums.py` — trigger gates (each condition falsified), terms carry the agenda target, rejection marker capped + expiring, popup dtype wired, GR5 (any authored nation can issue), corpus rows for any new typed responses.

---

## §9 Deferrals & cuts (GR9 — every one homed)

| Item | Disposition | Owner |
|------|-------------|-------|
| Russia `eastern_question` deck row | CUT from pass 1 — needs AI-AI war declaration | ROADMAP **8c AI Strategic Depth** (row already owns AI-AI declaration; the deck row is authored there when it lands) |
| AI-AI war declaration driven by agendas | Not built — agendas only bias existing wars | ROADMAP 8c |
| Britain naval-flavored agendas (blockade, Trafalgar) | Not authorable pre-naval | DEF-5 naval spec |
| Trade pressure (R123's second half) | Not built | `ECONOMY_REVISIT_SPEC.md` EC-8 economic diplomacy |
| Player-France agendas / goals | None — sandbox stays open-ended. **v1.1 seed note for the owner pass:** build France's goals ON the agenda substrate (GR5 — France simply has no deck today). Two CHAINED paths ride deck-priority for free (satisfy #1 → #2 activates natively); the only new machinery France needs is **branching** (a player *choice* between mutually-exclusive paths — not a predicate) + player-facing rewards (reuse the NA-6 §11.3 reward shape). The anti-Britain path ("Break Perfidious Albion") is unauthorable pre-naval — design the pass after DEF-5 lands, mirroring the Britain naval-agenda cut. | Pre-Ship Victory & Objectives Pass |
| **Free Ireland** (naval liberation → created Irish client + authored deck) | Deferred to the naval phase (user-directed July 17, 2026) — the invasion is unreachable without naval movement | **DEF-5 rider** in `MAP_IMPLEMENTATION_PLAN.md` (owner row updated July 17, 2026); reuses NA-6 Class C machinery (§11.5); test named in the rider |
| A "Unite Germany" formable | **REJECTED** — post-period (1871; no 1805–1815 actor pursued a unified Germany — the Confederation of the Rhine is French *clientage*, already modeled by vassalage) | re-open only via a future user gate |
| Dynamic agenda *generation* (post-authored decks) | Explicitly rejected at G1 | re-open only via a future user gate |
| Agenda-driven AI settlement-term authoring (beyond direction/indemnity) | Not in pass 1 | Pre-EA Diplomacy Polish Pass (with AUD-d rebuild) |

---

## §10 Test plan (summary)

`tests/test_nation_agendas.py` (NA-0..3) + `test_nation_agendas_ultimatums.py` (NA-5) + `test_nation_agendas_formables.py` (NA-6, §11.6). Pillars: boot-state pins for every authored deck (§7 NA-0) **incl. the v1.1 dormancy pins (satellite decks latent while vassalized, live on independence)**; predicate unit tests per type incl. vassal-dormancy and elimination; cache/invalidation + serialization round-trip; acceptance component both signs + preview visibility; resolve deltas at the P1 seam (advancing/satisfied/irrelevant); coalition Pressburg arm; target-bias preference without gate changes; paymaster tiers + GR5 (non-Britain paymaster); derived grudge (fires, caps, expires, disappears when targets returned — the R156 payoff pin: *returning Milan to Austria removes the grudge AND the acceptance penalty*); Ansbach trap both directions (player violator + AI violator); M1–M7 harness stability check at NA-3. Suite + ruff green per slice; the golden corpus gains rows only if NA-5 adds typed responses.

---

## §11 NA-6 — "Formable Dreams" (v1.1 amendment; owned follow-on slice)

**User direction (July 17, 2026):** more formables with *rewards for forming* and *their own goals when formed*; plus a possibility for a **free Ireland**, deferred to the naval phase. Blessed same day as the gate; this section is the build contract. **Sequenced after NA-5** (single-threaded queue discipline; NA-0..3 must be live-verified first).

### §11.1 The mechanic

A deck entry may carry an optional **`forms` key**: `{display_name, flag, blurb}` (validator-checked like the rest of the `agendas` schema). When that entry's satisfaction condition holds **while the nation is free** (not vassalized — the §3.2 dormancy rule already guarantees a vassal can't reach this), formation fires ONCE:

1. **Identity transform.** The internal nation tag **never changes** (serialization/save safety, GR-hard). The *display* name resolves through the existing R7 chokepoints — `backend/display_names.py` + `Utils.display_nation_name()` — keyed off the formation record; the flag swaps to the formation asset. "Kingdom of Italy" becomes **Italy** on every player surface; the save file never notices.
2. **One-time reward** (§11.3).
3. **Formation beat — "The Proclamation" (§11.8).** *Amended July 17, 2026 (user-directed "what would forming a new country look like"):* a nation forming is a once-per-campaign landmark, so the moment gets ONE ceremonial popup card (§11.8 stage 2) **plus** notification + dispatch line + campaign-log event (new type per the checklist steps 10–11). The original "no new popup" caution is retired **consciously**, with the full dialogue-wiring checklist pinned in §11.8 — the recurring wiring-bug class is handled by following the standing pattern, not by avoiding the surface.
4. **Post-formation goals for free.** The nation's *own goals when formed* are simply the deck entries authored AFTER the forming entry — once the forming agenda satisfies, deck-priority activates the next entry natively (§3.2). **Zero new goal machinery.**

**ONE new serialized world field:** `world.nation_formations: Dict[str, str]` (tag → formation id; full serialization checklist + SAVE_FORMAT_REFERENCE). Formation is permanent — losing provinces later does not un-form (the grudge/resolve machinery handles decline). **Amended by the §21.1 audit (D2):** permanence binds the LIVING state — a tag erased from the map entirely and genuinely re-carved may proclaim again, but the windfall is once per tag ever (`rewarded`).

### §11.2 The v1 roster

| Class | Nation | Forming entry | Forms | Post-formation deck (authored after it) | Grounding |
|-------|--------|---------------|-------|------------------------------------------|-----------|
| **T** (transform) | KingdomOfItaly | `risorgimento` (§4: Milan, Piedmont, Savoy, Naples, Rome) | **Italy** | `guard_the_peninsula` — guard_neutrality [Milan, Piedmont, Savoy, Naples, Rome] | The dream the vassal wakes with; a formed Italy consolidates and guards, it doesn't rampage. |
| **T** | Holland | `the_seventeen_provinces` (§4: Flanders) | **United Netherlands** | `merchants_peace` — guard_neutrality [Amsterdam, Brabant, Flanders] | The 1815 kingdom, reachable early by a Holland that frees itself; its formation *satisfies* Britain's `low_countries` deny agenda. |
| **C** (create) | — (new tag `DuchyOfWarsaw`) | created, not formed (§11.4) | **Duchy of Warsaw** | `commonwealth_restored` — acquire [Lithuania, Volhynia] (dormant while a client, §3.2 — it marches on the old Commonwealth lands only if it wins independence). ***v1.2: the entry carries a `forms` key → POLAND*** — a free Duchy that takes the old Commonwealth lands proclaims the Kingdom of Poland (the C→T chain: created as a client, forms a nation). **Forming Poland has POLITICAL implications (user-directed):** `aggrieved: [Prussia, Russia]` per §11.9 — the partitioning powers are enraged at the partitions avenged (Austria omitted: no Austrian Galicia on this map, pinned note below). Post-formation deck: `guard_the_vistula` — guard_neutrality [Posen, Lithuania, Volhynia]. | Tilsit 1807: Napoleon carves the Duchy from Prussia's Polish partition (Posen here); 1812 was declared the "Second Polish War." The restoration of Poland was THE red line for the partitioning courts — Napoleon deliberately never spoke the word in 1807; a player who does pays §11.9's price. (No Austrian Galicia exists on this map — the registry's Galicia is Spanish.) |
| **C** | — (new tag `Normandy`) | created, not formed (§11.4) | **Duchy of Normandy** | *(none authored — a pure client; deck-less tags get the survival override like any minor, §3.2)* | The coalition-side mirror (user example, July 17, 2026): a victorious enemy of France carves a client from French home soil — proves GR5 carve symmetry against the PLAYER's homeland. |
| **C** *(v1.2, user-directed "make Rome formable")* | — (new tag `RomanRepublic`) | created, not formed (§11.4) | **Roman Republic** | *(none authored v1 — a pure client, the Normandy pattern; a later pass may author a deck via the normal scenario data)* | The 1798 precedent: France deposed Pius VI and proclaimed the Roman Republic on the Patrimony of St Peter. Template provinces **[Rome]** — carved from the defeated **Papal States**. **Two pinned interplays:** (1) the Papal States are a ONE-province polity, so the carve is also their **elimination** — the §11.4 machinery must compose with the existing nation-elimination path (pin: carving a nation's entire remaining soil eliminates it AND creates the client in one ratification); (2) a standing Roman Republic holding Rome **blocks Italy's `risorgimento` formation** (Rome is a risorgimento target no longer takeable from a mere minor) — erecting Rome is a deliberate anti-Italy lever, and both sides can play it. `aggrieved: [Austria, Spain]` per §11.9 — the great Catholic monarchies answer the sacrilege (the 1798 scandal). |
| **C** | — (new tag `Ireland`) | created via naval liberation | **Ireland** | `erin_free` — guard_neutrality [Ulster, Munster] | Bantry Bay 1796, the 1798 expedition, Emmet 1803. **NOT built in NA-6 — the DEF-5 rider owns it (§11.5).** |

**Bounded roster.** "Unite Germany" REJECTED (§9 — post-period); Iberia has no in-window formation dream. The `forms` key is scenario data, so modders can author their own formables — the validator, not this roster, is the boundary.

### §11.3 Rewards for forming (in-band tunable)

| Constant | Value | Rationale |
|----------|-------|-----------|
| `FORMATION_GOLD` | +2,000 one-time treasury grant | the consolidation windfall — meaningful vs the §6 subsidy scale, below war-indemnity scale |
| `FORMATION_STABILITY_BONUS` | +2 stability, every owned region, one-shot (capped at max) | the national moment |

Plus the identity transform itself and the post-formation deck activation (§11.1). Applied through existing mutation paths (treasury add, stability setter) — no new economy plumbing.

### §11.4 Class C — carve-out client creation (generalized; the Duchy of Warsaw pathfinder)

**Amended July 17, 2026 (user-blessed, same session): creation is GENERAL, not a Warsaw one-off.** Any conquering side in a war — the player OR any AI lord, GR5 — can carve a client state out of the defeated party's soil at the settlement table. Warsaw is the pathfinder build; Normandy is the coalition-side mirror proving the symmetry; Ireland reuses the machinery at DEF-5.

- **Templates:** scenario `formable_nations` block (validator-checked): `{tag, display_name, flag, provinces[], deck, seeds}`. v1 authored set: **DuchyOfWarsaw** (provinces [Posen] — France's historical carve from Prussia, Tilsit 1807), **Duchy of Normandy** (provinces [Normandy] — the mirror: a victorious enemy of France carves a client from French home soil; 1-province symmetry with Warsaw is deliberate), **Ireland** ([Ulster, Munster] — naval-gated, §11.5). Templates are data — modders author their own; the validator is the boundary.
- **Eligibility (code-owned):** the war's settlement may carry a `create_client` clause when the proposing side controls ALL template provinces AND those provinces belong to the war's enemy party (you carve the *defeated*, never your own ally's soil, never your own homeland). The created tag becomes the carver's client/vassal.
- **Route:** the VS-5 `transfer_vassal`/creation seam precedent (`vassal.py`) + the settlement clause lifecycle. Player surface = the existing F1 wizard settlement flow; **no new verbs** (settlement authoring is wizard-first — standing rule).
- **Machinery:** dynamic roster addition (nations dict, relations rows, DP/treasury seed), flag asset per template (the U6 authored-flag pattern — Hanover/Hesse/KingdomOfItaly/Switzerland precedent), and — per the standing Don't-Do rule — `NATION_DESIRE_PROFILES` + `TALLEYRAND_COMMENTARY` rows for every creatable tag, authored up front.
- **Boot-zero by construction:** no template tag exists at boot; Italy/Holland boot vassalized. **Nothing can form or be created at boot — pinned.**

### §11.5 Free Ireland — DEF-5 rider (deferred to the naval phase, user-directed)

Owner row = `MAP_IMPLEMENTATION_PLAN.md` DEF-5 (updated July 17, 2026). At war with Britain, a naval expedition into Ulster/Munster (both British at boot) creates the `Ireland` client tag via §11.4 machinery, with the `erin_free` deck. Unreachable pre-naval — that's the whole deferral reason. Completion + behavior test (`test_naval_free_ireland.py`) live in the DEF-5 row.

### §11.6 Creation & formation UX contract (added July 17, 2026 — user-directed "assure the UX is good for creating these")

The creation flow must be *good*, not merely reachable. Binding requirements, all on EXISTING surfaces (no new popup, §11.1 holds):

1. **Wizard-first authoring.** The `create_client` clause lives in the existing F1 wizard settlement flow (the guided-terms surface — typed `propose` stays debug-only per the standing rule). It appears as a named option — **"Erect the Duchy of Warsaw"** — following the **honest-availability chip idiom** (U6): shown with its gate terms when close ("requires Posen — currently Prussian-held"), never a silent absence, never a dead button.
2. **Preview states the full bargain.** The wizard confirm/review step names exactly what happens BEFORE the player commits: which provinces leave whose control, the new client's loyalty seed (30, the VS-5 reset), tribute expectations, and the ES-7 **estate-cession warnings** ride the same territory-surface pattern already landed on every other cession path.
3. **Incoming offers are legible.** An AI settlement offer carrying `create_client` renders as a plain-language clause line in settlement review ("Britain proposes to erect the **Duchy of Normandy** from your provinces: Normandy") — display copy through the R7 chokepoints, never a raw tag.
4. **The world shows it immediately.** On ratification: map flag at once (authored asset per template), a VASSALS-ledger row for the carver, a row in the F1 nation list, dispatch beat + campaign-log event (checklist steps 10–11).
5. **Formation is watchable (Class T).** The Nations-tab/war-room agenda line for a forming entry carries a **"forms: Italy"** marker with live progress ("3 of 5 provinces held") — the player can see the dream approaching, both as the freed vassal's ex-lord and as a bystander.
6. **GR5 both directions.** AI lords author the clause via the VS-5 accept-side pricing pattern; the **Normandy mirror is the proof** — a winning coalition can put the carve-out clause in front of the PLAYER, and the player's Accept/Reject flows through the normal incoming-settlement surface.
7. **The moment is ceremonial.** Every formation and creation fires **The Proclamation** (§11.8 stage 2) — the one place the game stops for a landmark; everything else in this contract stays on existing surfaces.
8. ***(v1.2, user-directed "assure there is a button for France")* The Formables button.** France gets ONE assured, always-reachable browser for the formable world — not just the mid-negotiation wizard clause of §11.6-1. The **F1 diplomacy wizard's top level gains a "Formable Nations" entry** (surface of record; the NA-6 build may co-list it as a diplomatic-ledger view, but the wizard entry is the completion bar) listing EVERY Class C template and Class T watcher: each row shows the flag, the display name, and its **honest-availability gate terms** in the U6 chip idiom — *"Erect the Duchy of Warsaw — requires: at war with Prussia; Posen held at the settlement table (currently Prussian-held)"*, *"Italy — forms when a free Kingdom of Italy holds all five: 3 of 5 held"*. Rows are never hidden and never dead: an unavailable row states exactly what is missing; an available row deep-links into the settlement flow that can author the clause. This is the discoverability half of the reactive-but-discoverable standing rule — the gate stays where it is; the button makes it findable.

### §11.7 Completion definition

Class T lands first, Class C second, each with pins. DONE when: both T-formables form live (Italy: freed + peninsula held → renamed on ledger/map/diplomacy surfaces, reward applied once, `guard_the_peninsula` active next turn; Netherlands mirror incl. the Britain-deny satisfaction pin); formation is once-only + save/load-stable (`nation_formations` round-trip) — **as amended by §21.1 D2: once-only per LIVING state; a re-carved tag may proclaim again but banks the windfall once**; no formation while vassalized (dormancy pin); **Warsaw creatable via the wizard settlement clause by player AND AI lord (GR5), boots as client with dormant `commonwealth_restored`; the Normandy mirror exercised — an AI victor offers the carve against France and the player can accept/reject through the normal incoming surface**; **every §11.6 UX requirement pinned (honest-availability clause chip + gate terms, preview names provinces/loyalty/tribute + estate warnings, incoming clause line in display language, immediate flag/ledger/dispatch, the "forms:" progress marker)**; **The Proclamation wired per the standing dialogue checklist** (§11.8 stage 2: backend field passthrough, `main.gd` dtype whitelist, dialog_manager registration, PopupQueue slot, engine boot-smoke 0 `SCRIPT ERROR` — the slice touches `.gd`, so the XR-1 rule applies) and fired in test for a player-observed formation AND a player-authored creation; boot-zero pin; Don't-Do rows exist for every creatable tag; `tests/test_nation_agendas_formables.py` green; suite + ruff green.

**v1.2 additions to DONE:** the free Duchy of Warsaw taking Lithuania+Volhynia proclaims **Poland** through the same §11.1 machinery (C→T chain pin) with the §11.9 political implications live (Prussia+Russia one-time relation blow + the named "Polish Question" grudge contributor, both GR5); the **Roman Republic** carve exercised against the Papal States incl. the one-province **elimination-and-creation-in-one-ratification pin** and the **risorgimento-block pin** (a standing Roman Republic holding Rome keeps Italy unformed); the **§11.6-8 Formables button** exists at the F1 wizard top level, lists every template + watcher with honest gate terms and live progress, and has NO hidden or dead rows (source-scrape + payload pins); §11.9's own test list.

### §11.8 The formation moment — what forming a new country looks like (added July 17, 2026)

The worked example is the campaign's biggest version of the beat: the freed Kingdom of Italy takes **Rome**, the last of its five provinces, and **Italy** is proclaimed. Every stage below names its real surface; Class C creations (Warsaw, Normandy, Ireland) share stages 2–4 identically — creation and formation are the same moment in UX terms.

**Stage 0 — the dream is visible (turns before).** The Nations tab and war room carry the §11.6-5 progress marker: *"Risorgimento — forms: Italy (4 of 5 provinces held)."* Talleyrand's assess line names the stakes when relevant: *"Sire, the Italians hold all but Rome. A nation is one march from existing."* The player is never ambushed by a formation — they watched it approach, whether rooting for it or dreading it.

**Stage 1 — the tipping event (the turn it happens).** The last predicate flips on the normal turn tick (province taken, or the carve clause ratifies). The dispatch leads with it — this outranks routine lines: *"The tricolore rises over Rome. The peninsula is one."* Campaign log gets the event (new type, checklist steps 10–11).

**Stage 2 — The Proclamation (the moment).** ONE ceremonial popup card — `proclamation_dialog.tscn/.gd`, PopupBase, dialog_manager-registered, next free layer in 101–118, its own PopupQueue slot, shown once per formation via the standard priority queue (after any battle resolution, before routine notices). Content, top to bottom:
- the NEW FLAG, large, above the old flag struck through or fading — the visual "a country ended, a country began";
- the proclamation line in the engraved register: *"By the will of the nation and the fortune of arms — the KINGDOM OF ITALY is no more. ITALY stands."* (template-per-formation, authored in the `forms` blurb);
- the terms of its birth, stated plainly: rewards applied (*"+2,000 gold to its treasury; its provinces exult (+2 stability)"*), and the new design (*"Its court now guards the peninsula"* — the post-formation agenda title);
- ONE **[Acknowledge]** button. No choices — the moment is a fact, not a decision (decisions happened at the settlement table or on the battlefield). Perspective-aware subtitle: the player-as-witness sees *"A new power takes its seat in Europe"*; the player-as-author (you ratified the carve) sees *"By your hand"* — same card, one line differs.

**Stage 3 — the world has changed (same turn, no further input).** Map: flag + label repaint via the display chokepoints; the war-table pieces recoat on next refresh. Ledgers: the Nations/VASSALS/F1 rows re-title to *Italy* everywhere at once — no surface may show the dead name (R7 pin). Diplomacy: relations, wars, treaties, and grudges carry over seamlessly because the internal tag never changed (§11.1-1) — *Italy inherits the Kingdom's friendships and its enemies*, which is historically and mechanically the right answer.

**Stage 4 — living with it (turns after).** The new agenda line replaces the old on every intent surface; the notification remains dismissable-late (EU4-style persistent alert) for players who clicked past the card; the campaign-log entry is the permanent record. Nothing else lingers — no modal debt, no follow-up chores.

**What the moment must never do (pinned):** fire twice for one formation; fire at boot; show a raw tag or the dead display name anywhere post-formation; interrupt an unresolved battle/objection modal out of queue order; or block the turn (Acknowledge is the only path and it is always available).

### §11.9 Political implications — "The Partitions Avenged" (v1.2, user-directed)

*(section inserted by v1.2; see the amendment note in the masthead)*

A formation is not just a reward moment — for some powers it is a **casus foederis**. The user's direction: *"assure Warsaw becoming Poland has political implications."* The contract, generalized so any formation can carry it:

- **Authoring.** The `forms` block (Class T / the C→T chain) and the `formable_nations` template (Class C) gain an optional **`aggrieved: [nations]`** list, validator-checked against the roster (warning-not-error for unknowns, the standing stance). v1 authored rows: Warsaw→**Poland** aggrieves `[Prussia, Russia]` (the partitioning powers); **RomanRepublic** aggrieves `[Austria, Spain]` (the Catholic monarchies, 1798).
- **The one-time blow.** At the Proclamation, each aggrieved power still active takes `FORMATION_AGGRIEVED_RELATION_PENALTY = −30` relation with BOTH the new/formed nation AND its sponsor/lord (if any) — one-time, applied through the normal relation mutation path. The Proclamation card (§11.8 stage 2) carries one fury line naming the courts: *"Berlin and St Petersburg receive the news as a declaration."*
- **The standing wound.** While the formation stands and ≥1 aggrieved power remains active and unvassalized, a derived threat contributor `formation_grudge` adds `+1/turn` to coalition threat (source-keyed so the threat panel names it — **"The Polish Question"** for Warsaw), sharing the §5.8 sibling slot in `process_coalition_turn` step 2 and the `AGENDA_GRUDGE_CAP` ceiling with the post-peace grudge (the two grudge families never stack past the cap). **Fully derived** from `world.nation_formations` + the authored `aggrieved` list — zero new serialized fields.
- **GR5 both directions.** A coalition victor erecting Normandy or the Roman Republic against France's interests pays the same machinery where an `aggrieved` list names France's friends; the player erecting Poland pays it toward Prussia/Russia. Constants in-band tunable; structural changes escalate.
- **Tests** (named in §11.7): the Poland proclamation drops Prussia+Russia relations exactly once (no re-fire on save/load); the grudge contributor accrues while Poland stands and names its source on the threat panel; it ends only via the aggrieved power's own elimination or vassalization (formation itself is permanent, §11.1); the cap is shared with §5.8.

### §11.10 NA-6 build plan of record (v1.3, July 18, 2026 — follow in order)

§11.1–§11.9 say WHAT; this section pins HOW, so the build session makes zero design judgment calls. Facts below marked *(measured)* were verified against master at `7fcfd8e`. Where a seam must be re-verified at build time, the plan names the verification instead of guessing. Sub-slice order is **NA-6a → NA-6b → PAUSE for user review (the standing slice-review cadence: the first player-visible half lands, then stop) → NA-6c → NA-6d.** Every sub-slice: suite + ruff green; XR-1 boot-smoke + parse-harness regeneration whenever `.gd` is touched; `tests/test_nation_agendas_formables.py` grows per slice.

**Pinned decisions (authoritative — deviations must be recorded as conscious, like every landing record):**

1. **The formation record.** `world.nation_formations: Dict[tag → {"id": <forming entry/template id>, "sponsor": <lord-or-carver tag at the moment, "" if freestanding>}]` — a **conscious v1.3 amendment of §11.1's `Dict[str, str]`**: §11.9's standing grudge must know the sponsor AFTER the lord link dissolves (a freed Duchy that proclaims Poland has no current lord, but Berlin blames Paris), and sponsorship is not derivable later. Still ONE serialized key; full serialization checklist + SAVE_FORMAT_REFERENCE row. Formation is permanent — the record is the once-only latch (§11.8 never-do: no double fire, no boot fire). **Amended by the §21.1 audit (D2):** permanence binds the LIVING state — a tag erased from the map entirely and genuinely re-carved may proclaim again, but the windfall is once per tag ever (`rewarded`).
2. **The poll.** New `backend/game_logic/formations.py` owns everything in this plan (formation + creation + identity + payloads — keep `agendas.py` pure derivation). `process_formations(world)` runs from `_advance_turn_internal` immediately **before** `process_agenda_shifts` (so the shift beat announces the POST-formation deck entry, never the dead forming entry) **and** is called a second time from the settlement-ratification apply path after territory clauses land (§11.8 stage 1: a carve/cession-completed formation proclaims **the turn it happens**, not next tick). Idempotent via the latch; both call sites pinned by test (the NA-3 `advance_turn`-wiring-pin pattern).
3. **Identity (the R7 mechanism, both sides).** Backend: `formations.get_display_identity(world, tag) → {display_name, flag_tag} | None` reading the authored `forms`/template block through the latch; `display_names.display_nation_name` **stays static** — payload builders do NOT individually adopt the helper. Instead the base response / world summary gains ONE field `nation_display_overrides: {tag: display_name}` (empty dict = zero behavior change, boot-zero by construction). Godot: `Utils` gains a static `formation_overrides` store set from that field each response; `Utils.display_nation_name()`, `humanize_nation_keys_in_text()`, and `nation_flag_path()` *(measured: `utils.gd` — `nation_flag_path`/`bb_flag`/`apply_flag_icon` with `_flag_path_cache`)* consult it FIRST (flag lookup resolves `flag_tag`, e.g. `Italy.svg`; **the caches must be flushed when the override store changes** — the path cache is keyed by nation string and would otherwise serve the dead flag forever). This makes "no surface may show the dead name" (§11.8 stage 3) a two-chokepoint property instead of an N-call-site sweep. Flag assets: author SVGs in the U6 authored-flag pattern (`assets/ui/heraldry/`) for **Italy, UnitedNetherlands, Poland, DuchyOfWarsaw, Normandy, RomanRepublic**; credit rows if sourced.
4. **Rewards.** §11.3 constants live in `formations.py`. One-shot at proclamation: `nation_gold[tag] += FORMATION_GOLD`; every currently-owned region `stability = min(cap, stability + FORMATION_STABILITY_BONUS)` (single pass, existing mutation paths, never per-turn). Post-formation goals are FREE via deck priority (§11.1-4) — pin only, no code.
5. **The Proclamation is a PopupQueue popup, NOT a dialogue.** It has no choices, so it follows the `coalition_popup` precedent, not the dialogue-manager path: PopupQueue slot `proclamation_popup` inserted in `PRIORITY_ORDER` directly below `vassal_rebellion_imminent_popup` (a landmark outranks routine mail, yields to crises) with `RESPONSE_KEYS` row `nation_proclamation`; `proclamation_dialog.tscn/.gd` (PopupBase, dialog_manager-registered modal, **CanvasLayer 117** — *measured July 18, 2026: the only free slot in 101–118*); `main.gd` routes on the `nation_proclamation` response key. `[Acknowledge]` is client-side dismiss only — **no response endpoint** (the queue pops on delivery per Golden Rule 4; the EU4-style notification is the §11.8 stage-4 click-past recovery). Campaign-log type `nation_formed` (+ the two count pins flip, dated in-test); dispatch leads with a `fog_rule="always"` line. Card content per §11.8 stage 2 incl. the §11.9 fury line and the witness/author subtitle (author = the player ratified the carve or is the formed nation's sponsor).
6. **Class C roster addition.** `formations.create_client_nation(world, template, carver)` mutates: region controllers → new tag; vassal row via the existing creation seam with VS-5's `TRANSFER_LOYALTY_RESET`-shaped loyalty 30 under `carver`; `nation_gold[tag]` = template `seeds.gold` (default 500); `world.nation_capitals[tag] = template.provinces[0]`; `world.agendas[tag] = template.deck` (dormant while a client — §3.2 is already the law); relations/diplomatic rows only where seeds name them (verify missing-key defaults at build time rather than pre-writing rows). **The completeness contract is a shape-parity test, not an enumeration:** after creation, the new tag must appear in every world-level dict/list membership where the boot-authored satellite `KingdomOfItaly` appears (derived from the live boot world in-test, so the pin cannot drift). Created tags deliberately take the `_POWER_TIER_DEFAULT` fallback (`NATION_POWER_TIERS` is authored scenario data with no writable map — the standing Scale-Readiness taxonomy pin; do not fight it, record it). Don't-Do rows (`NATION_DESIRE_PROFILES` + `TALLEYRAND_COMMENTARY`) + `Utils.NATION_COLORS`/`NATION_DISPLAY` sync are needed **only for the three NEW tags** (DuchyOfWarsaw, Normandy, RomanRepublic) — Class T formables keep their tags, so their rows already exist.
7. **The `create_client` clause.** Settlement term type `create_client` with `{tag}` (template id). Eligibility (code-owned, honest-availability): every template province **currently controlled by the proposing side's bloc** AND its registry `starting_controller` belongs to **the war's defeated/enemy party** — this single predicate encodes "carve the defeated, never an ally's soil, never your own homeland" (§11.4). **No capital guard on carves — deliberate asymmetry with NA-5's ultimatum capital guard, pinned:** the settlement table may do what a peacetime demand may not; Rome IS the Papal capital and the one-province elimination-and-creation-in-one-ratification is a §11.2 pin, so the elimination path (R81 derived) must simply compose (test: carving a one-province polity eliminates it AND creates the client in the same ratification, no crash, both events logged). Surfaces per §11.6: wizard guided-terms row with U6 chip gate terms; incoming AI offers render the plain-language clause line; AI accept-side pricing per the VS-5 pattern.
8. **§11.9 mechanics.** "Sponsor/lord (if any)" = the formed nation's **current lord at proclamation, else the stored `sponsor` from the formation record** (decision 1). The `formation_grudge` contributor joins `process_coalition_turn` step 2 beside `agenda_grudge`, **sharing `AGENDA_GRUDGE_CAP`** (the two families' sum is clamped together — pinned). **v0.1 threat-scalar caveat (the D2 pattern, recorded not fought):** the scalar is France-targeted, so the standing grudge contributes only when the player is the recorded sponsor/current lord; an AI-erected Roman Republic aggrieving Austria costs the relation blows but feeds no France-threat — debug-log the skip like the hegemony non-France branch.
9. **The Formables button.** New `GET /formables` → `formations.build_formables_payload(world)`: one row per Class C template AND Class T watcher — `{tag, display_name, flag, cls, gate_terms[], available, progress ("3 of 5 provinces held"), deep_link}`; unavailable rows state exactly what is missing (§11.6-8: never hidden, never dead). `diplomacy_wizard.gd` gains the top-level "Formable Nations" entry rendering the rows in the U6 chip idiom; an available row deep-links into the settlement flow for the qualifying war. Source-scrape + payload pins per §11.7.

**NA-6a — Formation core (Class T, backend only).** Author the `forms` keys (risorgimento→Italy, the_seventeen_provinces→United Netherlands) + validator support (`forms` shape, `aggrieved` roster-check WARN); decisions 1–4 minus the popup (the beat ships as dispatch + campaign log + notification first — the card is NA-6b); §11.9 relation blow + `formation_grudge` for the T-formables (aggrieved lists ride the `forms` block). Completion: Italy forms live in test (freed + five provinces → latch + rewards once + `guard_the_peninsula` active next turn + display overrides in the payload); the Netherlands mirror incl. the **Britain-deny satisfaction pin** (a free Holland holding Flanders satisfies `low_countries` — derived, no code); no formation while vassalized; save/load round-trip; boot-zero; **M1–M7 harness byte-identical** (the poll rides the turn tick — cheap insurance, the NA-3 precedent).

**NA-6b — The Proclamation + identity surfaces (Godot).** Decision 5's popup + decision 3's Godot half (override store, flag/label swap, cache flush). Completion: the card fires in test-harness terms for a player-observed formation (backend popup payload pinned; Godot side by source-scrape + boot-smoke per the standing rule); no dead name on ledger/map/wizard surfaces (live check); XR-1 clean. **Then PAUSE for user review.**

**NA-6c — Class C carve-out creation.** Decisions 6–7 + templates (`formable_nations` scenario block: DuchyOfWarsaw [Posen] deck `commonwealth_restored` + `forms`→Poland, Normandy [Normandy] deckless, RomanRepublic [Rome] deckless aggrieved [Austria, Spain]) + the wizard/incoming/AI-side surfaces + the Proclamation firing for creations (shares stages 2–4, author-subtitle arm). Completion: Warsaw creatable by player AND AI lord (GR5); the Normandy mirror exercised through the normal incoming surface; the Papal elimination pin; shape-parity test green; boot-zero (no template tag exists at boot).

**NA-6d — The Poland chain + the Formables button.** The C→T chain (a FREE Duchy taking Lithuania+Volhynia proclaims Poland through the §11.1 machinery — the §11.7 C→T pin) with §11.9 live both directions (decision 8; "The Polish Question" panel label); decision 9's button. Completion: the §11.7 v1.2 additions in full + the §11.9 test list + button source-scrape/payload pins; final sweep of the §11.7 DONE bar — anything still unmet is finished here, not deferred.

---

## §12 Landing record — NA-0 + NA-1 (July 17, 2026)

**Both phase-1 slices LANDED in one session; the build is PAUSED for user review per the §7 cadence before NA-2/NA-3 (the teeth slices).** Suite green + ruff clean + boot smoke 0 `SCRIPT ERROR` + parse harness EXIT=0 + live `/diplomatic_ledger` curl verified.

**NA-0 Substrate:**
- `backend/game_logic/agendas.py` — the five §3.1 types as code-owned predicates, `AgendaView`, cached `get_active_agenda(nation, world)` (per-turn `_agenda_cache` keyed on `current_turn`, flushed from `invalidate_active_nations_cache()`), the survival override, the §6 blessed constants, and the pure NA-2/NA-3 feeders (`get_agenda_resolve_delta`, `agenda_concerns_player_bloc`, `agenda_satisfiable_by_player`, `is_agenda_satisfied`) — **no consumer wiring of the resolve/acceptance feeders yet**, per the NA-0 "no consumer changes" bar.
- Scenario `agendas` key authored in `europe_1805.json` — all §4 decks incl. the dormant KingdomOfItaly/Holland satellites. Boot pins measured live: Austria=`redeem_italy`, Prussia=`hanoverian_prize`, Britain=`low_countries`, Russia=`arbiter_of_europe`, France hegemon at 0.396 share.
- **TWO serialized world keys, not one** (conscious deviation from §3.4's count): `world.agendas` (the authored deck store — scenario DATA, the `marshal_pool` precedent; decks must survive save/load) + `world.nation_agenda_seen` (the §3.4 state field). Both in `to_dict`/`from_dict` with pre-NA-save defaults; SAVE_FORMAT_REFERENCE rows added; enforcement suite green.
- Validator `agendas` block (the `marshal_pool` precedent): type-enum hard-fail, per-deck duplicate-id hard-fail, region-typed entries require non-empty `regions` cross-checked when a regions block is present, unknown nations WARN. `MODDING_FORMAT.md` row added.

**NA-1 Legibility (§5.1 in full):**
- Nations tab: `agenda: {id, title, stance_line}` beside `bloc_stamp` (null-omit contract), single source `agendas.build_agenda_payload`; `diplomatic_ledger.gd` renders a gold "Design:" line after Treaties.
- War room: per-belligerent design lines in the wars loop (**coalition rows name EVERY participant's design** via `opponents` — beyond the spec's per-nation line, the R156 payoff) + the rung-1.5 "Satisfy their design" recommendation (below losing-war, above coalition-shoring; leader-with-terms-route → `request_terms`, any other satisfiable member → `open_proposal` — satisfying a NON-leader member is the Pressburg crack).
- Motive: `agenda_pursuit` in `_MOTIVE_REASONS` + all 5 register rows (hard-KeyError contract pinned) + Metternich/Hardenberg/Castlereagh named overrides + `DECISION_REASON_DISPLAY` "national design"; `determine_ai_offer_decision_reason` arm keyed on `agenda_concerns_player_bloc` (below the peace-family `war_overload` override, above the generic fallbacks).
- Shift beat: `process_agenda_shifts(world)` polled once per turn late in `_advance_turn_internal` (after coalition/AI-AI diplomacy, before fog) — first observation records SILENTLY (announce shifts, not bookkeeping; boot would spam 9 lines), deactivation records silently, genuine shifts queue ONE `agenda_shift` dispatch line (`fog_rule="always"`, diplomacy has no fog) + campaign-log event; seen-map dedup survives save/load. Campaign-log type count pin flipped 116→117.
- Consciously flipped pins: `test_bph_a_term_ownership`/`test_campaign_log` type counts; `test_w6_assessment_verb` wars-context shape (+`agendas` key) and the invest-rung test now also quiets rung 1.5 (`world.agendas = {}`) — the boot coalition war legitimately draws the satisfy-their-design counsel first.

**Tests:** `tests/test_nation_agendas.py` (90) — boot pins, dormancy + independence-wake pins, deck priority, per-type predicates (incl. vassal-holder satisfaction, self-bloc deny/contain exclusions, paymaster floor exclusivity + the coalition-membership arm), survival override (capital-lost AND majority-homeland arms, player-France, elimination), cache invalidation incl. the PRODUCTION diplomatic seam, round-trips, validator arms (type/regions/nation/duplicate-id/reserved-survival-id/floor bounds incl. explicit null), ledger/war-room/motive/dispatch/campaign-log pins.

**Pre-ship adversarial review (32 agents, 6 lenses → refute-verify): 25 confirmed findings, ALL FIXED before landing.** Headline P1s: (1) the `_agenda_cache` flush moved to `invalidate_bloc_members_cache` — war/alliance changes alter activation, and `set_diplomatic_state` reaches only that seam (a declared war now updates the ledger/war-room agenda same-turn; production-seam test added); (2) the F8 bandwagon throttle (`turn_manager` MAX_BANDWAGON_PER_TURN) now counts `agenda_pursuit` alongside `hegemony_pressure` — the new reason outranks it in the ladder and is the same pressure-flood shape. P2 semantics: `_entry_satisfied` computed per type (deny/contain's self-in-bloc gate is DORMANCY, never satisfaction — allying into the hegemon's bloc no longer reads as a fulfilled design); `_war_advances_agenda` + `agenda_concerns_player_bloc` deny arms re-anchored on the HEGEMON's bloc per §3.1; `get_agenda_resolve_delta` vassal/elimination-gated like the chokepoint; deck serialization deep-copies (nested region-list aliasing); the None-floor `.get()` trap closed at all four runtime sites AND the validator now rejects explicit-null/out-of-band floors, the reserved id `survival`, and reads scenario `controller` (not just registry `starting_controller`) for the nation cross-check. P3 copy: survival title de-dashed ("Survival" + stance "The dynasty above all."), the shift beat re-worded to the colon shape ("The court of Austria takes up a new design: Redeem Italy."), the "foreign holds" stance fallback and Castlereagh's doubled "matter" fixed, spec §3.1 `guard_regions[]`→`regions[]`.

---

## §13 Landing record — NA-2 Diplomacy Teeth (July 17, 2026)

**Landed after the §7-cadence user review resumed the build ("look in game then do na-2"). The in-game review PASSED** — ledger Design lines, war-room per-belligerent design lines, and the rung-1.5 "Satisfy their design (Britain)" executable counsel all verified live at ≥2560; one copy wart found ("Their court will not rest while Hanover holds Hanover") and fixed in-slice (eponymous holder==region arm in `_stance_line`, pinned).

**§5.2 — the acceptance term:**
- `agendas.agenda_acceptance_mod(proposal, world)` — `+AGENDA_ACCEPT_ADVANCE` (+12) when the offer's territorial content moves an unmet design target into satisfaction position (acquire: target region ceded TO the nation via `territory_cede`/`territory` sweetener dicts or the `territory_<lower>` string-clause form; deny: a listed region ceded OUT of the hegemon's bloc); `AGENDA_ACCEPT_ENTRENCH` (−8) when a demand strips a HELD design region (**priced on ANY proposal type** — an armistice that takes Milan is a real ask; conscious scope of the "armistice never entrenches" language, pinned) or a formal PEACE from **WAR or ARMISTICE state** (the armistice-first route still ends in "the peace that does not return Milan" — review fix) ends a conflict that was advancing the design without returning anything. A BARE armistice never entrenches (AUD-b protected). Survival/deckless/player-target = 0 by construction — every legacy fixture pin byte-identical (full suite green on first run).
- Wired per the `respected_estate_mod` recipe: standalone additive term OUTSIDE the composite floor, `components["agenda_mod"]`, `_generate_feedback` trackable + `FEEDBACK_STRINGS` row, sign-aware R17d preview label ("Advances their design" / "Entrenches their denial"), **and the crafted-terms confirm-popup labels** (`build_war_context_snapshot` largest-positive/negative — the raw-"Agenda Mod" leak the review caught; this snapshot is the live surface for the positive arm's copy). **Score-coupling pinned at the score level** (deleting the sum term fails `test_term_is_coupled_into_the_score`, not just a components read — review fix).
- **Covets unification:** `get_agenda_covets` (acquire = unmet targets, deny = bloc-held listed regions, postures/dormant = []) is the authoritative first source in `generate_suggested_terms` stage 2a AND `_has_bargain_strategic_interest` (any-active-nation arm), profile fallback intact; the two dead `NATION_DESIRES` territory rows deleted (8.EVAL AUD-d) + negative pin. **Stage-4 Talleyrand commentary made region-accurate for agenda-sourced tags** (the review's headline P2: the bespoke rows named stale profile regions — "Bavaria is Austria's natural sphere" while the terms ceded Savoy, and Prussia's conquer-Saxony advice was a dead end; agenda-sourced tags now compose "Savoy is the very object of Austria's design…" / "Their court's design fixes on Hanover, Sire — which we do not hold…", profile-sourced tags keep the authored voice — legacy worlds unchanged). `settlement_offers.py` deliberately untouched (§9 defers settlement-term authoring).
- Explicitly deferred with owners (§7 NA-3 riders a+b): the settlement scorer's per-court term ("buy-them-out" is bilateral-only today) and the preview positive-row reachability (the R17d mock is bare, so +12 surfaces today as the score delta + confirm-popup copy, not a preview row).

**§5.3 — R155 cadence:** hawk persistence as a CHECK-TIME type-cooldown reduction in `_is_on_cooldown` (a hawk court re-asks an agenda-advancing type 2 turns sooner — covers rejection AND lapse cooldowns with zero stored-state change; nation cooldown untouched; dove/loyalist full wait, boundary pinned at remaining 2 vs 3); `ask_advances_agenda` = guard_neutrality × non_aggression only (territorial asks don't exist pre-NA-5 — the seam is NA-5-ready); `_hegemony_ask_candidates` leads with the design ask (Prussia's armed neutrality asks for its non-aggression pact first — order-only, legality gates unchanged); `determine_ai_offer_decision_reason` voices `agenda_pursuit` for design-advancing asks (conscious flip of the NA-1 Denmark negative control, documented in-test).

**§5.4 — Pressburg + courting:** the P1 coalition-loyalty override gains `pressburg_ready` — `agenda_separate_peace_ready` (survival override OR deck[0] satisfied, the `_court_design_satisfied` helper shared with `get_agenda_resolve_delta`) AND `war_score < AGENDA_SEPARATE_PEACE_SCORE` (−30) — so a satisfied member sues where the stock −50 gate held it (pin pair: satisfied Austria at −49 sues `armistice_losing`; denied boot Austria stays loyal). **The survival arm deliberately needs no authored deck** — the Knife at the Throat is universal, so a capital-lost coalition member breaks ranks on ANY world incl. legacy (review finding accepted as spec-faithful, `test_deckless_survival_still_ready`). NOTE: until NA-3's resolve delta (+10 satisfied) reaches `effective_p1_threshold`, the outer P1 gate (≈−40) bounds how early the −30 constant bites — coherent at NA-2, completed by NA-3. Courting bias: `attempt_vassal_courting` stable-sorts candidates by `vassal_holds_agenda_target` (defined on `get_agenda_covets`, so the deny arm is hegemon-bloc-scoped like every other consumer — review fix; Austria courts the Kingdom of Italy that holds Milan; eligibility/cost/cooldowns/one-per-turn untouched, GR5).

**Adversarial review:** 6-lens find → 2-refuter verify workflow (28 agents; 13 verifiers lost to a session usage limit — their raw findings were verified by hand in the main loop). 11 raw findings → **8 acted on** (headline P2s: the stage-4 commentary contradiction; the unpinned score coupling), 1 accepted-and-pinned (deckless survival Pressburg), 2 homed as the NA-3 riders. All fixes pinned in-suite.

**Tests:** `tests/test_nation_agendas.py` 90 → **134** (acceptance both directions + exclusivity + armistice scoping + ARMISTICE-state peace + survival/deckless zeros; wiring components/score/feedback/preview-label/snapshot-label; covets by type + bargain-interest first-source/fallback/negative + suggested-terms preference + commentary region-accuracy both tags; dead-rows negative pin; hawk boundary ×4 + P3 lead + motive; Pressburg predicate ×4 + the breaks-ranks pin pair; courting bias ×3; stance-copy ×2). Suite **13,799/3 → green**, ruff clean, backend restarted + stance fix and preview live-verified over HTTP. No `.gd` files touched (XR-1 boot rule n/a; NA-1's boot smoke stands).

---

## §14 Landing record — NA-3 War Coupling (July 17, 2026)

**Landed same day as NA-2, harness-checked FIRST per the §7 completion bar: the M1–M7 sweep harness ran green before the first edit AND after the last — byte-identical (11/11; the harness recon confirmed M1–M6 boot no world at all and M7's jealousy loop touches no agenda/coalition/diplomacy path).** All five §5.5–§5.9 seams plus both §7 riders landed; backend-only (no `.gd`).

**§5.5 resolve deltas (consumer wiring):** `get_agenda_resolve_delta(nation, player, world)` added to `effective_p1_threshold` inside the existing `is_at_war` block (`ai_diplomacy.py`, beside the WPS-D ticking term). Pins: advancing Austria at −45 fights on (threshold −48) while the deck-stripped control sues; satisfied Austria at −35 sues THROUGH the boot coalition — the §5.4 Pressburg arm (−35 < −30) unlocks the loyalty gate the same turn the +10 delta opens the P1 gate, closing NA-2's "completed by NA-3" note. The survival arm is deck-independent by design (the §3.1 override is universal — the NA-2 deckless-survival-Pressburg precedent); every legacy P1 pin re-ran green.

**§5.6 target bias:** three seams, all through two new `EnemyAI` helpers reading **`get_agenda_military_targets` — the ACQUIRE-ONLY military half of the covets source** (review fix: §3.1 pins deny's expressions to "never self-conquest", so Britain's `low_countries` deny never marches its own corps on Flanders; diplomatic consumers keep the full `get_agenda_covets`; empty targets ⇒ byte-identical, pinned): `_get_strategic_enemy_regions` stable-sorts design targets first (its min-by-distance callers — P7 strategic arm + stagnation breaker — resolve ties to first-seen); the P4 personality pick (default + cavalry duplicate, unified into `_pick_personality_target`) breaks aggressive equal-ratio ties toward a design region and credits the cautious nearest-pick `AGENDA_TARGET_DISTANCE_BONUS` (2 hops); the P7 nearest-target choice (aggressive arm + cautious-advance copy) uses `_agenda_biased_distance` — credit lives ONLY in target-choice keys, never in the hop loop's must-reduce-distance gate; the covet set is memoized per (nation, turn) on the `_strategic_enemy_regions_cache` idiom (GR8 — the pick keys consult it per candidate). Ratio/threshold gates untouched; the engaged-combat and artillery doctrines untouched. **Both CALL-SITES are spy-pinned** (review fix: reverting the P4 pick or the P7 distance key to the pre-NA-3 inline code fails the flow tests, not just the helper tests). `ENEMY_AI_REFERENCE.md` updated in-slice incl. the named drift fixes (P3.8/P3.9/P2.5 rows, P4.78→P7.4 relabel + footer, admin-chain rows 1.5/1.6/1.75/6.5 + the +25g fix, the new ai_diplomacy P-namespace section).

**§5.7 paymaster:** `get_paymaster_nation` + `get_paymaster_subsidy_amount` (agendas.py) generalize the subsidy pair — the Britain literal survives ONLY as the deckless-legacy arm (500-gold gate, flat 200, byte-identical: every legacy subsidy pin green untouched). Deck worlds: first coalition member (member order) with a live `paymaster` POSTURE — the posture is deliberately read independently of deck priority (§3.1 "posture, not a quest"; Britain's gold flowed while `low_countries` stayed its announced design) — excluding vassals/eliminated/survival-override courts. Tiers 200 / 300 (>4,000) / 400 (>8,000), cap 400; `war_support_delivered` + the +5 relation nudge ride unchanged; the event keeps `type: "british_subsidy"` for wire-compat and gains `payer`. **The attribution resolver was generalized too** (review fix — the last Britain literal): `resolve_british_subsidy_war_id` gains a `supporter` param (default `"Britain"`, legacy byte-identical) so a non-Britain paymaster's contribution accrues against the war IT shares with the recipient instead of silently dropping (pinned: Russia's subsidy attributes to `war_1`). **One conscious re-bless:** Britain boots at EXACTLY its authored 2,000 floor and the NA-0 floor pin is exclusive (`> floor`), so the boot turn itself pays nothing — the first gold above the floor opens the purse (`test_british_subsidy_flows_to_austria` re-blessed to pin both arms; Austria stays the recipient).

**§5.8 grudge:** `get_agenda_grudge_nations` (agendas.py, fully derived) + `_calculate_agenda_grudge_threat` (coalition.py) as the fourth standing step-2 contributor, source-keyed `agenda_grudge` ("Denied national designs" on the threat panel via `_THREAT_SOURCE_LABELS`). **"Ended" is PER-NATION off `participant_meta`** (the review's headline P1 fix: the war-end path strips `side_by_nation` as participants exit, so the first cut — which read it — was structurally dead on every real resolution path; `participant_meta[nation]["side"]` survives exit and `exited_turn` gives a separate-peace court its OWN window — the Pressburg exiter grudges from ITS peace while the instance fights on, not from the whole war's distant end; `side_by_nation` stays a hand-authored-instance fallback). The lookback needs no archive scan by construction: `ARCHIVE_RETENTION_TURNS == AGENDA_GRUDGE_TURNS == 10` and a separate-peace exit precedes the instance end, so live `war_instances` covers every per-nation window. Pins: fires (Austria post-peace, Milan French), **fires through the REAL `resolve_pair_to_resolved` path on the boot Third-Coalition instance both ways** (full end with `side_by_nation == {}`; Austria's separate-peace exit while Britain/Russia fight on), reaches `threat_sources_this_turn` through `process_coalition_turn`, caps at 2 across three grudged courts, expires at the horizon, dissolves the turn the targets come home (Sardinia single-entry deck — the R156 payoff), and never fires for an unended (armistice-shaped) or resumed war.

**§5.9 the Ansbach trap:** `process_agenda_violations` (agendas.py) — one marshal-pass (the EC-W1 `get_disrupted_regions` idiom) over the ≤3 ACTIVE guard courts' region sets, called from `_advance_turn_internal` beside the NA-1 shift poll (after both sides' final moves, before fog). Guards: strength ≥ `DISRUPTION_MIN_STRENGTH` (a courier is not an army), not captured, violator belligerent, **not standing on its own or a client's soil** (review fix: a garrison on a legally-held, e.g. treaty-ceded, province is no transit — the old owner's reactivated guard cannot bleed the new owner −25 forever), not at war with / allied to / lord-or-client of the holder. Latch = event-log lookback keyed (violator, holder) at `AGENDA_VIOLATION_COOLDOWN` (10) — zero new serialized fields; within-pass pair dedup (two corps in two guard regions = ONE beat); **rolling-cap fail-safe** (review fix: if the capped 500-event log has evicted events INSIDE the window, a prior latch may be gone — suppress rather than re-fire; a missed violation is benign, a duplicate −25 is not). Fires −25 both-directions relation + `agenda_violation` dispatch (HIGH, fog "always" — diplomacy has no fog) + campaign-log event (type count 117→118, both count pins bumped). Pins: player violator (France in Jutland), AI violator (Britain in Jutland — GR5), ally/at-war/peaceful/own-soil exemptions, the rolled-log fail-safe both arms, the LATENT-guard negative (Berlin under Prussia's deck-latent `armed_neutrality` prices nothing — deck priority is the chokepoint), cooldown refire, sub-army no-op, **and the `advance_turn` wiring itself** (review fix: deleting the world_state call now fails a pin, not just the helper tests). Boot-inert: fires only once someone belligerent stands on an active guard's soil.

**§7 rider (a) — the settlement per-court term:** `agenda_settlement_mod(court, settlement_terms, world, proposer_side_participants)` (agendas.py) walks the SETTLEMENT term vocabulary (`territory`/`territory_cede`/`territory_return`, `from`/`to`, `region`/`regions`) with the shared ±12/−8 constants; wired as the ELEVENTH component `agenda_settlement_mod` of `calculate_common_peace_acceptance` (components + component_debug + `ACCEPTANCE_COMPONENT_DISPLAY` "National design" — the per-court breakdown renders it with zero further wiring). First-match-wins ordering: ADVANCE (cede a design target TO the court / move a deny target out of the hegemon bloc) → ENTRENCH demand-strip (a HELD design region taken FROM the court) → ENTRENCH peace-arm (the package ends a design-advancing war returning nothing — the common peace that does not return Milan). Zero on deckless worlds by construction — the scorer's exact-number fixture pins are byte-stable; the 10-key component-set pin consciously became 11. Tests patch the whole scorer at the stable seam, so every patched settlement suite is untouched.

**§7 rider (b) — the preview positive row:** `get_diplomatic_preview`'s R17d block scores PEACE-CLASS best actions on `generate_suggested_terms` output (which injects the design cession) instead of the bare mock; non-peace actions keep the bare mock. ONE memo serves the R17d row AND the BPH-B snapshot loop — the terms pipeline jitters gold ±20% per call, so generate-once-reuse keeps the two surfaces describing the same bargain (**pinned with a counting wrapper** — review fix: clause identity is deterministic across independent calls, so only a call-count pin can detect a memo revert). Live pin: the designed armistice-first route (ARMISTICE + recovered relations + France losing) puts "+12 Advances their design" in the preview positives — the row NA-2 documented as unreachable.

**Conscious pin flips (all dated in-test):** campaign-log type count 117→118 (`test_campaign_log` + `test_bph_a_term_ownership`); the settlement component set 10→11 keys (`test_common_peace_acceptance` + `test_settlement_guided_terms_slice3`); the boot-subsidy pin re-blessed to the floor-exclusive shape (`test_europe_1805_scenario`). Everything else in the at-risk sweep (wartime-peace-rebalance thresholds, legacy subsidy kit, DD8/hegemony/DG-4 contributors, W6 incoming voice, enemy-AI pick suites) ran green UNCHANGED.

**Pre-commit adversarial review (6-lens find → 2-refuter verify, 46 agents):** 20 raw findings → **10 confirmed, ALL FIXED in-slice** (each fix named in the seam paragraphs above), 10 refuted. Headline P1: the grudge was structurally dead on every real war-end path (`resolve_pair_to_resolved` strips `side_by_nation` as it stamps `ended_turn` — the synthetic test fixtures had masked it); the fix re-derives per-nation from `participant_meta`, which also fixed the separate-peace Pressburg court grudging from its OWN exit. The other confirmed rows: the attribution resolver's surviving Britain literal (§5.7), the §3.1 deny/"never self-conquest" contract on the military bias (§5.6 — military targets are now acquire-only), the own-soil violation hole + the rolling-cap latch eviction (§5.9), and four test-falsifiability gaps (the resolve negative-control tautology, the unpinned `advance_turn` violation wiring, the unpinned P4/P7 call-sites, the vacuous memo pin) — every one now carries a discriminating pin.

**Tests:** `tests/test_nation_agendas.py` 134 → **177** (+43: resolve wiring ×2 w/ deck-stripped control; target bias ×9 incl. deny-never-self-conquest, deckless byte-identity, and the P4/P7 call-site spies; paymaster ×7 incl. GR5 non-Britain payer + attribution + survival-closes-the-purse + legacy literal; grudge ×8 incl. the two real-resolution-path pins; Ansbach ×10 incl. own-soil, rolled-log, and the advance_turn wiring; settlement term ×5; preview row ×2 w/ the counting memo pin). Zero new serialized fields anywhere in the slice. Docs: SYSTEMS_REFERENCE §28 added; ENEMY_AI_REFERENCE patched; STATUS/ROADMAP updated. **NEXT per the §7 queue: live verify → NA-5 (§8) → NA-6 Formable Dreams (§11).**

---

## §15 Live verification — NA-0..3 playtest (July 17, 2026)

Mock-mode live drive of the default `europe_1805.json` campaign (backend HTTP, `LLM_MODE=mock` — deterministic, and Nation Agendas is a code-owned system so mock is the correctness-verification mode). France boots already at war with the Third Coalition, so every war-gated seam was exercisable on turn 1. **Verdict: PASS, zero defects.**

- **NA-0 dynamic activation — live + organic.** Every nation's agenda resolved at boot to the §12 pins (`/diplomatic_ledger`: Austria=`redeem_italy`, Prussia=`hanoverian_prize`, Britain=`low_countries`, Russia=`arbiter_of_europe`, Sweden=`scourge_of_the_usurper`, France=`None`, survival/guard neutrals). The **survival override fired *unprompted* on turn 3** — dispatch beat "The court of Bavaria takes up a new design: its own survival" (Bavaria, at war with Austria, crossed the threshold) — proving `get_active_agenda` + the shift poll end-to-end.
- **NA-1 legibility — all four surfaces live.** `nations[].agenda` present at boot and persisted **byte-stable across 8 turns**; the Talleyrand war room named all three coalition designs with correct stance text; the rung-1.5 counsel rendered ("Britain's war has a purpose we can price — 'The Low Countries'… offer it at the table and their reason to fight goes with it"); the dispatch shift beat printed **exactly once** on the genuine Bavaria flip (no turn-1 spam). Denmark (`guard_neutrality`) sent an agenda-consistent `non_aggression` proposal, deterministically voiced.
- **NA-2 acceptance mod — full archetype battery via `/debug/acceptance_preview`.** Cede Milan→Austria = **+12** (acquire advance); bare peace→Austria = **−8** (entrench); bare **armistice**→Austria = **0** (AUD-b protected); Britain bare = **−8** / +cede Flanders = **+12** (deny both directions); Russia bare = **−8**, correctly gated on hegemon share ≥ 0.33 (would flip to 0 if France's 0.40 share fell — verified against `_war_advances_agenda`).
- **NA-3 + covets — pinned green, not live-triggered this session.** The emergent hard-stop dialogue queue (jealousy petition → Denmark proposal → Britain settlement offer → capture choice) made a clean multi-turn military/diplomatic campaign impractical; the resolve delta, target bias, paymaster tiers, grudge, Ansbach trap, Pressburg arm, settlement mod, and covets suggested-terms are confirmed by `test_nation_agendas.py` + the M1–M7 sweep harness = **188/188 green on master**, with end-to-end wiring confirmed live where reachable. Named coverage: `TestResolveWiring`/`TestResolveFeeders`, `TestTargetBias` (P4/P7 call-site routing), `TestPaymasterTiers`, `TestAgendaGrudge` (×7, incl. the production war-end path), `TestNeutralityViolation` (Ansbach), `TestPressburgArm`, `TestCovetsUnification.test_suggested_terms_prefer_agenda_target`.
- **Stability.** 0 server errors across 8 turns + multiple emergent captures/petitions/proposals/offers.
- **Non-NA observations (no defect).** Stance-line em-dash (U+2014) renders as `�` only in the Windows console — the JSON is valid UTF-8. The plunder/secure capture-choice was a legitimate French marshal (Murat securing Swabia), not misattribution. **Candidate UX note for a frontend fun-read session (not an NA defect, no owner yet):** hard-stop dialogues can *stack* (petition → proposal → offer → capture) and freeze turn-advance — mechanically correct, but worth feeling in the real Godot popup pacing before judging whether it reads as drama or inbox-triage.

---

## §16 Landing record — NA-5 Ultimatums (July 18, 2026)

Built to the §8 gate answers, no further gate. `tests/test_nation_agendas_ultimatums.py` (35). Suite + ruff green; XR-1 honored (parse harness EXIT=0, report regenerated; headless main-scene boot 0 `SCRIPT ERROR`).

**The rung (`ai_diplomacy._generate_agenda_ultimatum`, between P7 and P8 in `process_diplomatic_phase`).** Fires only when ALL hold (each falsified in tests): at peace with the player · relation < 0 · active **acquire** design with an unmet target the player **directly** controls · nation outside the player's bloc · fog-free national strength (`_national_strength`, the diplomatic-ledger marshal-sum basis) ≥ `AI_ULTIMATUM_STRENGTH_RATIO` (1.25) × the player's · per-nation `AI_ULTIMATUM_COOLDOWN_TURNS` (15) clear · no other live ultimatum world-wide (`_has_live_ultimatum` scans the dialogue slot + mailbox queue). Two conscious tightenings recorded: **(a)** §8's "player-bloc regions" trigger is narrowed to player-DIRECT-held targets — the cession arms transfer only what `region.controller == payer` says the payer can sign away, so demanding vassal-held soil (e.g. Kingdom-of-Italy Milan) would be a dishonest no-op bargain; **(b)** the player's **capital is never demandable** (generator guard, pinned). The rung is **exempt from the turn-manager bandwagon throttle** — a deferred delivery would silently eat the court's one ultimatum for 15 turns (the cooldown is set at ISSUE, so an ignored/lapsed demand does not return next turn).

**Building Blocks honored.** Terms via the player's OWN `generate_ultimatum_terms`, now parametrized (`issuer=`, `demand_regions=`) — both kwargs omitted = the player-issued path, byte-compatible (existing PL-14 pins untouched). The design target rides the `territory_cede` demand; `_force_send` bypasses the player-side acceptance filter (extortion scores terribly by construction — the send is the point). Yield applies demands player→issuer through the SAME `_apply_ultimatum_demands` arms (new `beneficiary` param, GR5; the `add_threat` calls fire only for a player beneficiary — an AI annexing French soil is not French aggression).

**Transport + surface.** New dtype `incoming_ultimatum` in `CURRENT_TURN_OFFER_TYPES` (lapses at end of turn — a lapse is NOT a rejection, pinned), mailbox priority 2 ("Ultimatum" row label), delivered via the standard `deliver_ai_proposal` (its own "Ultimatum from X" notification headline). Popup = the existing `incoming_proposal_popup.gd` with an `is_ultimatum` branch: crimson ULTIMATUM header, **Demands:**, Counter hidden (an ultimatum is not a negotiation), buttons **Yield/Defy**. Dtype routed in `main.gd` (pending-envoy + mailbox-activate) and `backend/main.py` (`/pending_envoy`, `/mailbox/activate`, the popup-passthrough safety valve). Typed responses ride the existing dialogue-response path (labels + `action_map` aliases yield/defy/refuse/accept/reject) — **no new typed player commands, corpus deliberately untouched** (pinned: the actions are dialogue actions, absent from `VALID_ACTIONS`).

**Consequences.** Yield: demands transfer (incl. the tribute clause player→issuer), acceptance cooldown, `proposal_result_popup` outcome, campaign-log `ai_ultimatum_accepted`; the issuer's design then derives as satisfied on its own (resolve/grudge machinery follows for free). Defy: NO war (no unilateral AI declare-war path — the coalition system remains the war-maker, pinned), `coalition.record_ultimatum_rejection` plants the DD8-idiom marker (`ULTIMATUM_REJECTION_PRESSURE_TURNS=8` / `AMOUNT=2` / `CAP=4`; anti-stacking refresh) feeding the threat scalar as the **fifth standing contributor** ("Defied an ultimatum" on the threat panel; drive-by: the DD8 `schemer_peace_rejection` source also gained its missing label), plus `apply_ultimatum_rejection_cooldowns` (floors the type key at 15 — `apply_rejection_cooldowns` would clobber it to 6, the overwrite trap inverted). Issuing **never reduces the player's threat** (pinned). ONE new serialized world field: `ultimatum_rejection_pressure` (nation → expires_on_turn; full checklist + SAVE_FORMAT_REFERENCE).

---

## §17 Landing record — NA-6a + NA-6b (July 18, 2026)

**Both phase-1 formable slices LANDED in one session; the build PAUSES here for user review per the §11.10 cadence, before NA-6c (Class C carve creation) and NA-6d (the Poland chain + the Formables button).** Suite **13,890 → 13,997/3** (+105 `tests/test_nation_agendas_formables.py`, +3 conscious pin flips), ruff clean, Godot parse harness EXIT=0, headless boot **0 `SCRIPT ERROR`**, M1–M7 sweep harness byte-identical 11/11 before AND after. NA-6a committed at `9a559f8`.

### The structural fact that shaped the whole slice

`get_active_agenda` **cannot** be the formation predicate. An `acquire_regions` entry is ACTIVE only while UNMET (`_acquire_active`), so activation is the exact complement of satisfaction: on the tick `risorgimento` satisfies, the derivation chokepoint already returns the NEXT deck entry. `process_formations` therefore scans the **raw deck** `world.agendas[tag]` via a new public `agendas.entry_satisfied`, and walks the WHOLE deck (unlike `_court_design_satisfied`, which inspects only `deck[0]` — a formable authored at index ≥1 must still fire). Both properties are pinned.

### NA-6a — the formation core (backend)

- **`backend/game_logic/formations.py`** (NEW): `process_formations` (the poll), `get_forms_block`, `get_display_identity` / `build_nation_display_overrides` / `build_nation_flag_overrides` / `formed_display_name`, `get_formation_watch` (the §11.6-5 progress marker), `build_proclamation_card`, and the §11.9 grudge derivation. §11.3 constants live here.
- **`world.nation_formations`** — ONE new serialized key, `{tag: {id, sponsor, turn}}`. **Conscious extension of §11.10 decision 1:** `turn` added (the once-only audit trail, and the durable stamp a ratify-path beat needs since the dispatch QUEUE is cleared at the top of the next tick). deepcopy on both arms — NOT the flat `str()` arm `nation_agenda_seen` uses, which would stringify the record.
- **Both §11.10-2 call sites, both pinned by test:** `_advance_turn_internal` immediately BEFORE `process_agenda_shifts` (so the shift beat announces the POST-formation entry), and the settlement ratification apply path AFTER the three cache invalidations (agenda activation reads the region control and war geometry the clauses just moved). Idempotent via the latch.
- **Authored roster:** `risorgimento` → **Italy**, `the_seventeen_provinces` → **United Netherlands**. **Both decks were single-entry**, so §11.1-4's "post-formation goals for free" had nothing to fall through to — `guard_the_peninsula` and `merchants_peace` were authored in the same pass. The §11.2 Britain-deny mirror is pinned and fully derived (a free Netherlands holding the Low Countries takes them out of the hegemon's bloc, which IS Britain's deny condition — zero formation-aware code).
- **Rewards** one-shot through existing mutation paths; the card reports `regions_lifted` honestly so it never claims a stability lift the cap swallowed.
- **§11.9** relation blow + the `formation_grudge` threat contributor. **Conscious deviation from decision 8's "joint clamp":** implemented as a deterministic **budget split** — `agenda_grudge` emits first at its own unchanged value, `formation_grudge` takes only the remainder. A single merged `add_threat` would have destroyed §11.9's "source-keyed so the threat panel names it" requirement, and this leaves `_calculate_agenda_grudge_threat` byte-identical so both NA-3 pins stay put. Order-dependence is real, deliberate, and documented at the helper. **The per-formation label ("The Polish Question") is homed to NA-6d** — a static `dict[str,str]` cannot express it, and NA-6d lands the Poland chain the label exists to name.
- **Validator:** `forms` shape, and `forms` on a POSTURE type is an **ERROR** (paymaster/guard_neutrality never satisfy, so it would be a formable that can never fire — the dead promise GR9 forbids). `aggrieved` roster-checked as WARN against `VALID_NATIONS`, deliberately NOT the locally-derived `known_nations` (which is built from region controllers + marshal nations, so exactly the landless courts most likely to be aggrieved would warn spuriously).
- **Identity payload:** `nation_display_overrides` / `nation_flag_overrides` on `build_base_response` — stamped AFTER `response.update(extra)` so an executor key cannot clobber it — **and on the seven hand-rolled GET payloads** (conscious extension: a player who LOADS a save with formations and opens a ledger before issuing any command would otherwise read the dead name).

### NA-6b — The Proclamation + the identity surfaces (Godot)

- **`proclamation_popup.tscn/.gd`** on **CanvasLayer 117** (re-measured at build time: 101–116 + 118–120 occupied, 117 the only free slot — the spec's claim holds). PopupBase, dialog_manager-registered, PopupQueue slot `proclamation_popup` directly below `vassal_rebellion_imminent_popup` with `RESPONSE_KEYS` row `nation_proclamation`. Choice-less; `[Acknowledge]` is a client-side dismiss with **no response endpoint** (pinned). Campaign-log `nation_formed` + HIGH dispatch line + notification. Card content per §11.8 stage 2: new flag large over the struck old name, the engraved line, honest terms, the §11.9 fury line, and the perspective-aware witness/author subtitle.
- **The two Godot R7 chokepoints:** `Utils.formation_overrides` / `formation_flag_overrides`, consulted FIRST by `display_nation_name` (before the static map AND the camelCase split) and by `nation_flag_path`; `set_formation_overrides` **flushes `_flag_path_cache`**, which is nation-keyed, caches the NEGATIVE result, and had no `clear()` call anywhere in the codebase. Adopted at `api_client._adopt_formation_overrides` — the single chokepoint that sees every 200-OK body from every endpoint, running BEFORE the callback so the response that proclaims a nation already renders under the new name.
- **`_is_prose_safe_nation_key`:** only multi-token camelCase tags are substring-substituted in prose. `Normandy` and `Rome` are PROVINCE names on this map, so a blind replace would corrupt every sentence naming them — the documented `Ottoman` exclusion, which the NA-6c carve tags walk straight into.
- Flag assets `Italy.svg` + `UnitedNetherlands.svg` authored in the U6 flat-SVG idiom, `.import` sidecars generated and force-added (`assets/` is gitignored).

### The live visual check — what it caught that the tests did not

Driven in the real client at 5120×1440 against the running backend, staged one tick before Italy's formation. **Six defects found by looking, all fixed in-session:**

1. **The flag did not render** — a `.svg` with no `.import` sibling does not resolve through `ResourceLoader.exists()`. Now pinned by test.
2. **Dead space** — the card was a fixed 680×500 panel; now sizes to its content.
3. **A dead-name leak on the ledger** — Austria's design line still read *"while **Kingdom of Italy** holds Milan"* after the proclamation. `display_nation` is static, so the backend bakes the dead name into the sentence, and because the result is already humanized (no raw tag survives) Godot's prose substitution cannot repair it downstream. Fixed at the agenda + war-room prose seams via `formed_display_name`; four regression pins added.
4. **P1 — the entire end-turn report was swallowed.** A formation fires inside `advance_turn`, so its response is the one carrying `enemy_phase`; every entry in `_post_hud_response_routes` returns from `_on_command_result` BEFORE the enemy-phase dialog, the turn result text, strategic reports and the Morning Dispatch.
5. **P1 — the terminal soft-locked.** That same early return skips `set_input_enabled(true)`, and the card had no `dismissed` connection because it was (correctly) reasoned to need no backend response — but the connect is what hands control back on the CLIENT.
6. **A rump state could proclaim a triumph.** The raw-deck scan bypasses `get_active_agenda`, which ranks the survival override above the deck — so the override had to be re-applied in the poll, or a Holland reduced to one province would proclaim, bank the windfall, and take up "Survival" on the same card. Formation is permanent, so it could never be undone.

Defects 4 and 5 were found by the pre-ship adversarial review (8 lenses → 2 independent refuters each, 17 agents) and independently confirmed by the live drive; defect 6 came from the same review. **The architecture changed as a result:** the Proclamation is deliberately NOT a pre-empting route. It is STASHED the moment the response arrives — ahead of all routing, so a higher-precedence modal (capture choice, objection) cannot destroy it either — and shown at the points where the player regains control, after the dispatch, last before the turn resumes. The command-tail seam is guarded on `enemy_phase` (a residual caught on the second live pass: unguarded, it swallowed the very tail it was added to preserve). Final live sequence verified end to end: **enemy-phase report → Morning Dispatch → The Proclamation → Acknowledge → terminal accepts commands.**

### Conscious pin flips (all dated in-test)

`CAMPAIGN_LOG_TYPES` 120 → **121** (×2 files) · `PopupQueue.PRIORITY_ORDER` / `RESPONSE_KEYS` 10 → **11**.

### Deferred with owners

~~Per-formation threat label ("The Polish Question") → **NA-6d**~~ ✅ CLOSED July 19, 2026 (§21). ~~The §11.6-5 watcher payload (`get_formation_watch` incl. `blocked_by_vassalage`, and the `agenda.forms` progress marker) is computed and pinned but has no `.gd` consumer yet → **NA-6d**~~ ✅ CLOSED July 19, 2026 (§21 — ledger Design-line marker + war-room marker + the Formables browser). Five further mid-turn region-control transfer paths (bilateral `_ratify_treaty`, `_apply_ultimatum_demands`, VS-3 grant and reclaim ×2) resolve formations on the NEXT tick rather than same-turn; the spec names only settlement ratification, and extending the set is **NA-6c** scope (it adds the carve clause those paths would interact with).

**✅ THE NA-6 ARC IS BUILD-COMPLETE (July 19, 2026): NA-6a + NA-6b + NA-6c + NA-6d all landed — landing records §17, §20, §21. Next per ROADMAP: user in-game review of NA-6c+NA-6d, then the Battle Diorama (Tier A) slice.**

### §17.1 Addendum — the in-game review + second adversarial sweep (July 18, 2026)

The §11.10 review pause was run as a delegated in-game review plus a second 19-agent
adversarial sweep (9 lenses → 2 independent refuters each). Between them they found
**one P1 and five P2s, all fixed**. Two were caught by driving the game, four by the sweep.

**P1 — the Proclamation was 100% undeliverable on the settlement-ratify path.**
`_respond_to_dialogue_sync`'s PL-14 safety net REBUILDS the response to pick up a
newly-set `proposal_result_popup`. The first build had already run
`_include_popup_passthroughs`, which POPS the winning popup off the queue *and clears
the world field* — so the rebind destroyed it, and the formation latch guaranteed it
could never fire again. The ratify call site exists solely to serve this beat and
delivered it zero percent of the time. Fixed generically with
`_capture_popup_passthroughs` / `_restore_popup_passthroughs`: the defect silently ate
**any** popup type, not just this one.

**P2 — two formations on one tick lost the second card.** Found by driving a staged
double formation: both nations formed for real (latch, rewards, overrides, campaign log,
notification) but the PopupQueue holds ONE slot per type, so the second landmark was
swallowed. Overflow now rides `nation_proclamation_popups`, the
`vassal_rebellion_imminent_popups` precedent, drained one per response at both delivery
seams; `_on_proclamation_dismissed` chains so the second card follows the first
immediately rather than waiting for an unrelated command.

**P2 — the card was stranded on the DOMINANT path whenever the tick produced strategic
reports.** `_on_enemy_phase_dismissed` returns early for `strategic_reports` and
`redemption_event`, both *above* the seam the first sweep had added. Formations are
triggered by conquest — i.e. by marshals under standing orders — which is exactly what
populates `strategic_reports`, so this was the normal shape, not an edge case. The tail
is now factored into ONE `_return_control_to_player()` called from all four
control-returning seams. Hanging a landmark off a single hand-picked seam was the
mistake; the helper is the fix.

**P2 — the command-tail seam swallowed the whole response.** The first sweep's fix sat
above `_display_result`, `_process_active_wars` and the dispatch, so a player who
ratified a settlement saw the Proclamation and never learned the settlement had been
ratified, with the ended war still in the HUD. The card now comes LAST, after everything
has rendered.

**P2 — five more dead-name seams.** `display_nation` and `humanize_entity_name` are both
formation-blind, and the client cannot repair them because the strings are already
humanized. Fixed at the battle Materiel line (`combat_executor`), the `region_lost` and
`war_touches_us` dispatch beats, and the coalition war-HUD row (`war_status`) — the last
being permanently on screen. `humanize_entity_name` was additionally *mangling* the name
("Kingdom Of Italy", capital O) via its camelCase split.

**P2 — the campaign log rendered post-formation events under the dead name.** Found in
the review: turn 3 read *"The court of Kingdom of Italy takes up a new design"* after the
turn-2 proclamation. The log re-derives names from the stored raw tag with the static
`display_nation`. Fixed at the one endpoint chokepoint with
`apply_formation_names_to_history`, which **respects history**: only events at or after
the formation turn are renamed, and the `nation_formed` entry is exempt entirely —
renaming its first half would turn *"Kingdom of Italy is no more — Italy is proclaimed"*
into nonsense.

**Verified live after the fixes** (fresh backend — an earlier pass read a stale server
process that had outlived a failed restart, briefly showing an already-fixed leak):
a full dead-name sweep over `/status`, `/ledger`, `/diplomatic_ledger`,
`/marshal_overview`, `/dispatch` and `/campaign_log` three turns past the formation
returns **no present-tense dead names** — the only surviving mention is the proclamation
line that is supposed to carry it. The end-to-end sequence re-verified in the client:
enemy-phase report → Morning Dispatch → The Proclamation → Acknowledge → terminal
accepts commands.

**Also confirmed by the review, working as designed:** Britain retook Flanders and
Amsterdam during the enemy phase of the double-formation run, so Holland lost both its
target province and its capital and correctly did **not** form — organically exercising
the survival-override gate added by the first sweep.

Suite **13,997 → 14,011/3**. ruff clean, M1–M7 byte-identical, parse harness EXIT=0,
headless boot 0 `SCRIPT ERROR`.

**Residual risk, stated plainly (unchanged by these fixes):** no formation has yet
occurred *organically* through played conquest — every exercise to date has staged the
provinces directly; the formed nation has never been used as a diplomatic counterparty
(it cannot be addressed by its new name — the name→tag resolver is unpatched, homed to
NA-6c with the carve tags); and `deny_regions` / `contain_hegemon` formables are blessed
by the validator and documented for modders but never authored or run.

---

## §18 Phase review — the whole arc, NA-0 → NA-6b (July 18, 2026)

A 21-agent phase-level review (10 lenses → independent refuters → synthesis) over
`712550b..564bd9b`, scoped to the ARC rather than any one slice: cross-slice
interaction, accumulated drift, and whether the phase delivers what §0 promised.
It found **one P1 root defect that three slice-scoped reviews had all missed**, because
it only manifests in a geometry no single slice owns.

### P1 — the anti-hegemon designs deleted themselves at the moment they succeeded

`agendas._hegemon` consumed `coalition._identify_max_bloc_share` raw — "who is the
largest bloc". That is the wrong question for an ANTI-hegemon design. Once the
anti-France bloc out-massed France the raw answer became **a co-belligerent**, and
every predicate keyed on it inverted at once:

> ⚠️ **CORRECTION (July 18, 2026, §19).** This section originally read "Coalition
> formation produces real `ALLIANCE` states, so … the raw answer became Britain's own
> *ally*." **That is factually false** and it was load-bearing: it is the entire
> justification for scoping deny satisfaction to bloc membership.
> `coalition.form_coalition` writes `active_coalition`, calls `declare_war`, and
> nudges relations +10 — and **no diplomatic states at all**. The boot Third Coalition
> is allied only because `europe_1805.json` authors those rows. A coalition formed in
> play therefore left the denier in a bloc of one, the guard below silent, and the
> design reading SATISFIED. Pinned by `TestCoalitionIsNotABloc`.

- `_deny_active` / `_contain_active` short-circuit on `nation in bloc` → **Britain's
  `low_countries` and Russia's `arbiter_of_europe` went inactive for the rest of the
  war they were being fought over.** Every §5 consumer went silent with them: the
  ledger Design row, the war-room line, the rung-1.5 counsel, `agenda_acceptance_mod`,
  `get_agenda_covets`, the `agenda_pursuit` voicing.
- `_paymaster_active` needs at-war-with-the-hegemon; the hegemon was now Britain's own
  ally, so **the subsidy stopped exactly when the coalition it funds existed** — a
  regression against the NA-3 Britain literal it replaced, which would have kept paying.
- Worst: the deny SATISFACTION check then read **TRUE while France still held the
  Scheldt** (France's provinces are not "in Austria's bloc"), handing Britain
  `AGENDA_RESOLVE_SATISFIED` (+10) and `agenda_separate_peace_ready` — **an early
  separate peace for Britain because France was winning the thing Britain denies.**

Reproduced from the shipped scenario, then fixed and re-verified across four
geometries (boot / Britain allies France / coalition out-masses France / Britain takes
the Scheldt).

**The fix, in two parts, both contained:**

1. `coalition.identify_ranked_bloc_shares` — the ranked form of
   `_identify_max_bloc_share`, which becomes its `[0]`. Same basis, same tie-break;
   the max-only caller and its two non-agenda consumers are byte-identical.
2. `agendas._hegemon(world, nation=None)` — **court-relative resolution**: with a
   court, the largest bloc that court is NOT in. Threaded through all 14 anti-hegemon
   call sites. Boot-identical on the shipped scenario, because France is the largest
   bloc and no anti-France court sits inside it; the two forms only diverge once the
   geometry inverts.

Plus a satisfaction correction with two guards, each earned from a defect: sitting
inside the DOMINANT bloc is dormancy and never satisfaction (this preserves the
existing "allying into the hegemon's camp does not fulfil the design" pin AND covers
the inverted geometry), and **the share floor gates ACTIVATION, never SATISFACTION** —
an earlier arm returned satisfied below the floor ("the hegemon fell"), which is false
while the cut-down power still holds the targets. Britain's design is the Scheldt, not
France's overall size.

### P2 — the war room advised a cession the player could not make

`agenda_satisfiable_by_player` gated on BLOC control while `generate_suggested_terms`
filters coveted regions to `world.get_nation_regions(player)` — the player's DIRECT
holdings. With every target sitting in a VASSAL's hands, the phase's single executable
agenda recommendation still fired: it cost an action, opened talks, offered an
unrelated province, and scored the design term at ENTRENCH — **strictly worse than
ignoring the advice.** Now gated on direct control, mirroring the narrowing §16 had
already applied to NA-5's ultimatum trigger for exactly this reason. Textbook
cross-slice drift: the same lesson learned in one slice and not carried back.

### P3 — AI ultimatum prose named the issuer `Unknown`

`generate_ultimatum_terms` was the one AI proposal builder that did not stamp
`proposer_nation`, so the fallback prose read *"Unknown demands 300 gold per turn"*.
Latent behind the structured payload, but one guard from a live surface.

### What the review did NOT find — worth recording

- **GR8 is clean.** Measured on the real 126-province world: `advance_turn` 9–24 ms/turn
  with agenda work ≈1 ms of it; the per-turn cache runs 837 hits / 179 misses over 10
  turns with no thrash. The substrate carries six slices of consumers without strain.
- **Serialization is clean** across all six phase fields — round-trip, pre-phase
  defaults, doc rows, and no cross-save contamination on either the backend or the
  Godot static stores.
- **No duplicated-with-divergent-semantics defect** in the display-identity set, and no
  constant defined twice. The satisfaction-helper family (`_entry_satisfied` /
  `_court_design_satisfied` / `is_agenda_satisfied` / `entry_satisfied`) is layered, not
  drifted.
- All six §0 G2 "full coupling" pillars have real production call sites and are
  reachable in the shipped campaign.

### Known limitation, recorded rather than papered over

A court that is INSIDE the dominant bloc reads its deny design as not-satisfied even
when it holds the targets itself (Britain takes the Scheldt while leading the winning
coalition). This is **pre-existing behavior, unchanged by this fix** — under the old
code the targets counted as "in hegemon bloc hands" because Britain was in that bloc.
Correcting it means deciding what deny satisfaction means when the denier and the
hegemon are allies, which is an authoring decision rather than a defect. **Homed to
NA-6c**, which touches the same predicates for the carve tags.

> **CLOSED July 18, 2026 by §19.** The phase audit ruled the semantics: own soil is
> denied outright, whatever the bloc rankings say. The "held by the hegemon's bloc"
> arm no longer sees a court's own provinces at all.

Suite **14,011 → 14,017/3** (+6: `TestInvertedHegemonyGeometry`, plus the counsel-honesty
pin). ruff clean, M1–M7 byte-identical.

---

## §19 Phase-audit fixes — the whole arc re-reviewed (July 18, 2026)

Fifth review of the phase, 112 agents, 29 raw findings → 8 survived triple
adversarial refutation. Memo: `docs/audits/NATION_AGENDAS_PHASE_AUDIT_2026_07_18.md`
(authoritative). Four fix families landed; the memo's §11.9 assessment
(GR9-compliant deferral) and its six-pillar observability arithmetic stand
unchanged as findings, not work.

### P1 — deny satisfaction was anchored on bloc membership; a coalition is not a bloc

§18's fix resolved the hegemon **court-relatively** — necessary, but it left the
satisfaction question keyed on `get_bloc_members`, which admits only vassal chains and
formal `ALLIANCE`/`DEFENSIVE_ALLIANCE` states. **`coalition.form_coalition` writes no
diplomatic states at all.** A coalition formed in play left the denier in a bloc of
one, the "am I inside the dominant bloc" guard silent, and — once any third bloc
out-massed the holder — the design reading SATISFIED while the enemy held every listed
province: `+10` resolve, `agenda_separate_peace_ready` True, and no player-facing
surface able to explain it (active view `None` ⇒ no covets, no acceptance term, no
ledger Design row).

**The ruling: satisfaction is a statement about the provinces, not about bloc
rankings.** A province counts as denied when, and only when, it is held by

1. **self or one's own client** — outright, whatever the geometry, *or*
2. **a power below the `major` tier that is not inside the hegemon's bloc** — the
   buffer state.

Any other great power holding it denies nothing. This is the doctrine the design was
always written in: Britain tolerated the Dutch Republic and the Austrian Netherlands
on the Scheldt, and would not tolerate France there.

Four recorded rulings had to survive simultaneously, and do:

| Ruling | Status |
|---|---|
| §11.2 — the formed United Netherlands **satisfies** Britain's design | **preserved** by arm 2. Deny means "not theirs", never "mine". Two earlier drafts broke this: one keyed on own-bloc membership, one on "at war with the holder" (Britain is still at WAR with the freed Dutch). |
| D68 — allying **into** the camp that holds the Scheldt is dormancy | **preserved**. An allied great power is still a great power. |
| guard 2 — a cut-down France still holding the targets satisfies nothing | **preserved** by keying on tier rather than share. A beaten great power is still a great power. |
| D70 — a court holding its **own** targets read not-satisfied | **FIXED** by arm 1, and the §18 known-limitation paragraph is closed above. |

Boot is byte-unchanged: Flanders (France, major) and Brabant/Amsterdam (Holland, a
French client inside the hegemon bloc) all fail both arms.

**Two mistakes were made inside this fix and caught by its own pre-push review — both
re-opened the P1, and both are now pinned:**

1. The exclusion set was built from the **raw** hegemon and gated on the share floor.
   The floor governs ACTIVATION, never SATISFACTION, and the raw form is exactly the
   question §18 proved wrong. Now court-relative, ungated.
2. The **literal** `region.controller` was read where arm (a) two lines above resolves
   the vassal chain. A French *satellite* is a minor power on paper, so
   Holland-holding-Amsterdam passed as a neutral buffer while it was still Napoleon's
   client — the P1 through the back door, reproduced on boot-adjacent state (Britain
   takes Flanders, coalition out-masses France → satisfied, +10, separate peace).
   Both the effective overlord and the literal controller are now tested.

`test_a_french_satellite_is_not_a_buffer_state` pins it. The lesson generalizes: any
predicate that asks "who holds this province" in a world with vassals must resolve
`_top_overlord`, and any predicate that asks "who is the threat" must be court-relative.

### Coherence — a won design could not be priced at ENTRENCH

Both acceptance scorers gated on the ACTIVE view, which for a satisfied acquire is
`None` (activation is its complement) — **or is a different, later deck entry**:
Austria holding Milan flies `primacy_germany`, so a demand for Milan matched no
target at all. More complete success bought *less* defence of the very province won,
and line 39's "sues to lock its gains" shipped its "sues" half (+10 resolve,
Pressburg) with nothing delivering "lock".

New `_satisfied_views()` returns **every** satisfied deck entry (not just the first —
a court that wins its *whole* deck otherwise let the later design's provinces fall out
of the strip arm entirely: Austria holding all five design provinces priced Milan at
−8 and Munich at 0, and Munich had priced −8 before Swabia was taken). Both
ENTRENCH-strip arms now price against the live design **and** every won one. ADVANCE
deliberately still fires only from the live design — paying +12 for handing a court
what it already holds is free acceptance for nothing.

### P3 — an armistice is a pause in a war, not a restoration of neutrality

An armistice simultaneously **woke** the paused opponent's `guard_neutrality` design
(`_guard_active` read only `get_nations_at_war_with`, strict `WAR`) and **stripped**
the war exemption from the army standing on that soil because of that very war —
outrage priced at −25 for holding still, and −70 relation crosses
`ARMISTICE_AUTO_PEACE_RELATION`, resuming the war instead of maturing it to peace.
The codebase already disagreed with itself here: `diplomacy.py` states the doctrine
outright and the NA-2 entrench arm already pairs `("WAR", "ARMISTICE")`.

New `_belligerent` / `_has_belligerency` helpers; `_guard_active` and the violation
exemption both consume them. §5.9's written predicate is amended above — the code had
matched the spec, so this was a shared gap rather than an implementation slip.

### P2 — a demand overtaken by war is not a bargain

The ultimatum dialogue is non-blocking and lapses only at the *start* of the next
`end_turn`, so it survived arbitrary state change across the whole of the player's
turn. Yielding after the pair fell to WAR still transferred the province, wrote a
perpetual tribute treaty, marched off the conscripts and reported *"The peace holds"*;
yielding to an issuer eliminated during the turn **resurrected** it. Reachable with
zero player action — a third party's alliance cascade drags the issuer into an
existing war between the AI diplomatic phase and the player's answer.

`_ultimatum_void_reason` gates both arms. Yield transfers nothing and says so; defy
plants no pressure marker and re-arms no cooldown — a court cannot bank a grievance
for a refusal that cost nothing. New campaign-log type `ai_ultimatum_void` (both count
pins 121 → 122). Three dead-name repairs rode the same handlers.

The pre-push review caught the defy arm still logging `ai_ultimatum_rejected`
unconditionally: the popup read *"the demand has lapsed of its own accord"* while the
campaign log, same turn, read *"we defied them — their court will not forget"*. The
**durable record has to agree with the popup**, or the fix only moves the
contradiction somewhere less visible. Both void paths now log the lapse, and
`test_the_live_arms_still_log_their_own_types` guards the ordinary path.

### Landed with

`tests/test_nation_agendas_phase_audit.py` (27) — including `TestCoalitionIsNotABloc`,
which pins the false premise itself so it cannot silently become true again. The
inverted-geometry arms deliberately leave co-belligerents at PEACE rather than
hand-writing ALLIANCE rows: hand-writing them is exactly what hid this geometry from
three prior slice reviews. Suite **14,018 → 14,047/3**, ruff clean. Falsifiability verified by reverting both production files: 17 of the 27 fail against pre-fix code.


---

## §20 Landing record — NA-6c Class C carve-out creation (July 19, 2026)

Commit `6e87654`. Suite **14,218 → 14,278/3**, ruff clean, M1–M7 sweep harness
byte-identical 11/11 before AND after, Godot parse harness `EXIT=0`, headless boot
**0 `SCRIPT ERROR`**, live-verified over HTTP. `tests/test_nation_agendas_formables.py`
105 → **179**.

### The structural fact that shaped the slice

**`process_formations` can never announce a creation.** The poll skips every vassal
(`formations.py` — `if _is_vassal(world, nation): continue`, the §3.2 dormancy gate), and a
Class C client is a vassal from its first instant. So the carve emits its own Proclamation
rather than waiting for a tick that would never fire. NA-6a's `_resolve_sponsor` docstring
had already anticipated exactly this ("the lord arm is dead for Class T today and lives for
the NA-6c creation record").

The second structural fact, and the one most likely to have shipped silently:
**`_forms_block_for_record` resolves identity by scanning the nation's DECK**, and two of the
three authored templates are deckless. Without the new template arm, Normandy and the Roman
Republic would have had no display name, no flag, and no standing §11.9 grudge — and every
one of those failures is a silent `None`, not an error. The template arm is checked FIRST for
that reason, and `test_deckless_client_still_has_an_identity` is the pin.

### What landed

- **The catalogue.** Scenario key `formable_nations` (validator-checked) + `world.formable_nations`,
  serialized like `agendas` because it is read at RUNTIME: the carve eligibility predicate needs
  `provinces`, and a created client re-derives its identity from its template on every load.
  Authored: **DuchyOfWarsaw** [Posen] with a dormant `commonwealth_restored` deck whose `forms`
  block makes it POLAND (aggrieved Prussia + Russia — the C→T chain NA-6d completes);
  **Normandy** [Normandy], the coalition-side mirror; **RomanRepublic** [Rome], aggrieved
  Austria + Spain.
- **`formations.create_client_nation`** — the first code in the project to add a nation at
  RUNTIME. `world.enemy_nations` had only ever been built in `__init__` and restored from save.
  Shape parity is a test **derived from the live boot world** (every dict/list where the
  boot-authored satellite `KingdomOfItaly` appears), so the pin cannot drift as new
  nation-keyed state is added — and it immediately earned its keep by catching a missing
  `nation_authority` row.
- **The `create_client` clause** through all seven settlement layers, priced in **both**
  harshness dialects (`0.3 × provinces + 0.15`: above a plain cession `0.3`, below vassalage
  `0.5`). Registering the type in only one dialect is the shipped G4F-1 bug class and is
  pinned against.
- **Eligibility** (`evaluate_create_client_eligibility`) encodes the whole §11.4 rule in ONE
  predicate: every template province currently held by the carver's bloc **AND** its registry
  `starting_controller` equal to the court being carved. The second half is what makes it
  honest — holding a province is not enough, the soil must have *belonged* to the court paying
  the price, which is simultaneously the "never an ally's soil" and "never your own homeland"
  rule.
- **The Proclamation** for creations, sharing §11.8 stages 2–4 with the Class T beat, with the
  author/witness subtitle arm already GR5-symmetric from NA-6b.
- **§11.6 honest availability** — the carve row is SHOWN when unavailable, carrying its gate
  terms ("requires Posen") and the refusal's own reason string, rendered as **inert text rather
  than a link** so it is structurally un-clickable. This is the FIRST option on the settlement
  authoring surface to do this: that surface's own documented rule was "ineligible options
  simply do not appear", which is wrong for a formable specifically — a standing ambition of
  the campaign that silently vanishes reads as "this game has no such thing".

### Conscious decisions (the spec left these open)

| # | Decision | Why |
|---|----------|-----|
| Q2 | Total annexation obeys the same war-score-90 rule as `territory_cede`, but as a **LOUD refusal at the authoring seam** rather than `territory_cede`'s silent `continue` at ratification. | Rome IS the Papal capital and their only province, so the Papal carve is also their elimination — allowed, and pinned, but only at a decisive score. A silent skip is the wrong feedback shape either way. The literal `90` became the shared `TOTAL_ANNEXATION_WAR_SCORE`. |
| Q3 | Carved provinces take `stability = 50` (the hostile-cession idiom), not VS-3's stability-preserving grant idiom. | The soil changes hands under duress at a settlement table. |
| Q5 | The three tags are authored into `NATION_POWER_TIERS` as `minor`. | Decision 6 rules out a *runtime writable* tier map; it does not rule out authoring known tags in the authored one. Unauthored, a one-province client would enter coalition threat math at `secondary` — Spain's weight. |
| Q6 | **Revised during the build**: the carved provinces DO seed `nation_starting_regions`. | Measured rather than assumed: with home `[Posen]` and Posen held, `capital_held` is True and `held*2 >= len(home)`, so `survival_override_active` stays False and a newborn never proclaims Survival over its own erection. If the client is later overrun, survival firing is exactly right. Also gives clean shape parity with zero exemptions. |
| Q8 | Clause shape follows VS-5: `from` = the carved court, `to` = the carver, `tag` = the template. Joins `_CROSS_SIDE_TRANSFER_CLAUSE_TYPES`. | Preserves every burden/coverage/straddle assumption and buys the cross-side check free. |
| Q10 | Carved capitals are **re-derived in `from_dict`** from `formable_nations` + `nation_formations`. | `nation_capitals` is project-wide unserialized (rebuilt at construction, hence its `KNOWN_EXCLUSIONS` entry). Re-deriving matches that philosophy without adding a field or touching the enforcement gate. Left unfixed, a carved client silently pays −1 DP every turn forever. |
| Q13 | The AI authoring arm is IN scope, unlike VS-5's accept-side-only scope-down (VP-D8). | §11.7's completion bar explicitly names "AI lord (GR5)" and "an AI victor offers the carve against France". |

### Fixed in passing (in blast radius)

- **GAP G1** — the region double-promise check could not see a carve's template-resolved soil,
  so a `create_client` of Posen plus a `territory_cede` of Posen both validated and whichever
  apply-step ran second silently won. New refusal code `carve_region_double_promised`.
- **GAP G2** — `agenda_settlement_mod` gated on the territory family, so a court whose design
  province was *carved* away scored the package as indifferently as a white peace. Now scores
  identically to the cession it effectively is (pinned as an equality, not just `< 0`).
- **`_MATERIAL_LOSS_TYPES`** was missing VS-5's `vassal_transfer` as well as the new
  `create_client`; both added, so an ally sold out either way gets its
  `sold_out_by_war_leader` reaction.
- **Refusal-ordering fix found by a test**: "whose soil is this" is a STATIC map property and is
  now checked BEFORE "do you hold it". Checked second, a template belonging to an entirely
  different country refused with `carve_provinces_not_held` — indistinguishable from a real,
  one-conquest-away opportunity, which put the Roman Republic on Prussia's negotiation row.
- **Validator refactor**: the per-entry agenda validation was extracted to `_validate_agenda_deck`
  so a template's `deck` is held to the identical schema as an authored `agendas` deck (it IS
  one; it merely lies dormant), and the `aggrieved` checker to `_validate_aggrieved_list`.

### Recorded, not fixed

- The intra-package elimination **ordering** hazard (a later clause returning a province to a
  nation an earlier clause eliminated, resurrecting it as a landholding ghost with no teardown
  reversal) is **pre-existing for `territory_cede`** and out of this slice's scope. A carve
  inherits it. A generalized post-loop elimination sweep would fix it for all clause types and
  is the obvious future shape.
- The player is exempt from elimination, so an AI carve taking France's last region would leave
  a zero-region player. Unreachable with the v1 roster (Normandy is 1 of ~28 French provinces).
- `_eliminate_nation` has no idempotence latch.

### Session hazard worth recording

A review subagent ran `git stash` to "compare against baseline" and **destroyed the entire
uncommitted working tree** (23 files, 2,167 insertions). It was recovered intact from
`stash@{0}`. Two standing lessons: land a large slice to a commit BEFORE handing it to a
review fleet, and give review agents a pre-snapshotted diff plus an explicit read-only
prohibition rather than letting them reach for git themselves.

### §20.1 Addendum — the adversarial review and its 12 fixes (July 19, 2026)

A 12-lens find→refute review ran against commit `6e87654`: **136 agents, 41 candidate
findings, 24 refuted, 17 survivors** (2-of-3 refuters, default REFUTED), merged to **12 distinct
defects**. Every one was verified by hand before fixing. Suite **14,278 → 14,293/3**; M1–M7
byte-identical throughout.

**No lens came back clean.** The slice's own tests were green and the live HTTP drive passed —
the review found what both missed, which is the argument for running it.

| # | Sev | Defect | Fix |
|---|-----|--------|-----|
| 1 | P1 | **A carved capital had no garrison, forever.** Both garrison seams key off `region.is_capital`, not `world.nation_capitals` — the carve set only the map. Posen sat at 0 while every peer minor held 10,000, and the regen loop skipped it permanently: an undefended province the enemy retakes for free, destroying the tribute the carve was bought for. | `_seed_client_roster` sets the region flag and seeds straight to `get_capital_garrison_target`, matching the boot seeder. |
| 2 | P2 | **A carved Duchy of Normandy rewrote history prose.** `apply_formation_names_to_history` did a naked substring replace; NA-6c makes `Normandy` the first formation key that is also a PROVINCE. "Ney was broken at Normandy" became "...at Duchy of Normandy" on every entry after the formation turn, permanently. Godot has carried this guard since NA-6b — the backend twin did not. | New `_is_prose_safe_name` (multi-token AND not a live region key). Multi-word renames still fire, pinned both ways. |
| 3 | P2 | **The first end turn after a Proclamation announced the new nation as eliminated.** The tick reports any marshal-less nation gone unless pre-seeded into `eliminated_nations_notified`; `from_scenario` does this for army-less boot courts, the carve did not. | Seeded at birth. |
| 4 | P2 | **Duplicate elimination announcements** — and the §11.2 pin was untestable in play. The carve arm re-checked "is this court landless" unconditionally, but eligibility *requires* the carver to already hold every template province, so the court is landless BEFORE the carve and `capture_region` already eliminated it. The old test only passed because its helper wrote `region.controller` directly, bypassing that path. | Session-scoped re-entry latch on `_eliminate_nation` (deliberately NOT `eliminated_nations_notified`, which means "already announced marshal-less" and is pre-seeded for exactly the Papal States); carve-arm elimination gated on soil actually having moved from the carved court. The pin was **rewritten through `capture_region`** and now asserts the elimination fires exactly ONCE. |
| 5 | P2 | **A carve stripped a marshal's estate with no ES-7 warning on any surface** — a direct §11.6-2 violation. Three separate loops guarded on `!= "territory_cede"`, and a carve's soil rides `provinces`. | One shared `cession_shaped_regions` + `CESSION_SHAPED_CLAUSE_TYPES` in `settlement_scoring`, consumed by all sites. Patching the three loops separately was rejected: **the divergence was the bug** — they had already drifted before NA-6c gave them a fourth shape to miss. Parity is pinned by asserting carve warnings == cede warnings. |
| 6 | P2 | **Adding the types to `_MATERIAL_LOSS_TYPES` was a complete no-op.** That frozenset is only the early-out gate; the per-type ladder that returns a reason was never extended. The strictly harsher clause (0.45 vs 0.30) produced strictly *less* diplomatic fallout than the milder one, and the first commit message's claim about the reaction was false as shipped. | Ladder extended for `create_client` **and** `vassal_transfer` (a live VS-5 gap). |
| 7 | P2 | **A bankrupt losing player could never be carved.** The EC-W4 empty-purse arm returned a white peace ABOVE the carve gate, coupling a territorial clause to the payer's coin balance — so the most decisively beaten France, exactly the state §11.4 models with the Duchy of Normandy, was the one state immune, and got gentler terms than a solvent loser. | The indemnity now appends conditionally instead of returning; control falls through to the carve gate. Pinned at treasury 0 and −500. |
| 8 | P2 | **The player's actual click path had zero coverage.** Every ratification test hand-built the clause dict. The add-verb chain ends in a bare `else: # liberation`, so a create_client arm that is moved or unreached silently stages a LIBERATION — ratification would free a Prussian vassal and erect no Duchy. | A test driving the real `settlement_demand_add` verb through the GT-Slice-1 dialogue harness, asserting the staged clause is a carve and that nothing fell through to liberation. |
| 9 | P3 | **A malformed template crashed mid-mutation and left a phantom nation.** Only `provinces` was pre-checked; `seeds` was consumed at mutation time, so a diplomat block missing `skill` raised `KeyError` out of ratification *after* the tag was in `enemy_nations` — and `enemy_nations` serializes. | Total `_validate_seeds` hoisted into the pre-mutation block, honouring the docstring's existing promise. |
| 10 | P3 | **The `from_dict` capital re-derivation wrote through the legacy module global.** Its creation-time twin has a copy-on-write guard; this one relied on "the catalogue is empty on a legacy world", which is an assumption about DATA, not a guard. | Shared `_ensure_owned_capitals`, called from both sites; pinned by a test asserting `region.NATION_CAPITALS` is unmutated. |
| 11 | P3 | **The pre-commit preview omitted the loyalty seed and tribute** §11.6-2 enumerates. Both first appeared at ratification and on the Proclamation card — strictly after the decision. A client boots at loyalty 30, already inside the under-35 band VS-6's defection check reads. | `loyalty_after`, `tribute_rate` and a `client_terms_display` line on the preview row. |
| 12 | P3 | **Three untested seams**: the `nation_created` dispatch beat (flip the branch and the suite stayed green while the line rendered "— is no more."), the VS-5 `vassal_transfer` guided-line arm, and #8. | Pinned, including the rendered dispatch text and its `fog_rule`. |

**Falsifiability verified**: reverting fixes 1, 2, 3 and 6 fails exactly the four corresponding
new tests and nothing else.

**Left unfixed, deliberately** (recorded in §20 already): the pre-existing intra-package
elimination *ordering* hazard, the player's exemption from elimination, and the AI's ongoing
treatment of a carved client as a diplomatic actor beyond turn 1 — the last is the natural
subject of the NA-6d live verification rather than a code change here.

### §20.2 Visual check — held July 19, 2026

Self-served against the rendered assets and the real backend payload, in the pattern the
U2/U3/U5 sign-offs used.

**The four heraldry assets.** Rendered at full size and at in-game chip size. Three passed
first look — Warsaw (white over red), Poland (the same bicolour under a gold crown, so the
C→T chain reads as a promotion rather than a different country), and the Roman Republic
(the 1798 black-white-red vertical tricolour). **Normandy FAILED and went through five
drafts**, each rejected on sight for a different reason worth recording, because the failure
modes are general to hand-authored figurative heraldry:

1. *centipede* — blocky body, identical bar legs, unreadable head blob;
2. *cartoon cub* — everything built from circles: round head, dot eyes, a **smile**;
3. *spiky sun* — a literal mane rendered as a regular star, and the raised forepaw reading
   as a trunk hanging off the chest;
4. *housecat* — coherent at last (maneless, four articulated legs, thick curled tail, a
   forward-REACHING foreleg rather than a dangling one) but unmistakably domestic;
5. **shipped** — broader jaw, small rounded ears set low and wide (tall triangular ears on a
   round skull are the single strongest "cat" tell), deeper chest, scalloped ruff.

The technique that finally produced a coherent figure is worth keeping: paint the whole
animal TWICE — a fattened dark pass for the outline, then solid gold on top — so overlapping
sub-shapes leave no internal seams and no hairline element can vanish at chip size.
Deliberately **maneless**: in French heraldry a *léopard* IS a lion passant guardant, and the
medieval Norman rendering is routinely drawn without one; draft 3 proves what adding a mane
costs.

**Resolution — the Hanover precedent was taken (user-directed, same day).** All five drafts
were discarded. `Normandy.svg` now adapts **"Flag of Normandie.svg"** (Wikimedia Commons,
uploaded 2009-04-02 by Saebhiar, released into the **public domain worldwide** — PD-self),
exactly as `Hanover.svg` adapts the PD `Flag_of_Twente.svg` Saxon Steed. Licence verified
against the live source page before fetching; credit row in `THIRD_PARTY_LICENSES.md`.

Adapted for this project: the source 3:2 canvas re-fitted to the set's 500×300 (centred,
scale 1.889764, dx 25), the source's own field rect replaced by one in the game palette red
`#c8102e`, and the gold recoloured `#fcd41c` → `#e8b923` to match the rest of the heraldry
set. The **azure tongue and dark outline are kept** — "armed and langued azure" is the
correct blazon, and the outline is precisely what lets the charge read at 44px. The source's
`<g id="a">` + `<use>` structure is preserved, so the second leopard is still one reference
rather than a duplicated path.

The result is real heraldry: manes, claws, tongues, articulated paws, correct passant
guardant attitude — and it still reads cleanly at chip size, distinct from Warsaw's and
Poland's bicolours and Rome's tricolour.

**The lesson worth keeping:** the five drafts were not wasted so much as diagnostic. Coherent
figurative heraldry is past what hand-authored path data reaches reliably, and the project
already had a documented answer for that. When an asset class has a sourcing precedent in
`THIRD_PARTY_LICENSES.md`, reach for it before the fifth redraw, not after.

**The honest-availability carve row.** Rendered from the live `_court_demand_suggestions`
payload through the exact BBCode `_build_suggestion_lines` builds:

```
UNAVAILABLE  [color=#808080]Erect Duchy of Warsaw from Prussia's lands — unavailable (requires Posen)[/color]
               [i][color=#909098]— Your armies do not hold every province the new state would be made of.[/color][/i]
AVAILABLE    [url=sugg:0:0][color=#80b0e0]Erect Duchy of Warsaw from Prussia's lands[/color][/url]
               [i][color=#909098]— Do not annex it, Sire - erect it. …[/color][/i]
```

The unavailable arm contains **no `[url=`** — structurally un-clickable rather than a dead
button, which is the §11.6-1 requirement. Both sign-off rows opened in §20 are CLOSED.

---

## §21 Landing record — NA-6d The Poland chain + the Formables button (July 19, 2026)

**THE NA-6 FORMABLE DREAMS ARC IS BUILD-COMPLETE** — NA-6a → NA-6b → NA-6c → NA-6d all landed.
Suite green (`tests/test_nation_agendas_formables.py` 196 → **225**), ruff clean, M1–M7 sweep
harness byte-identical 11/11, Godot parse harness `EXIT=0`, headless boot **0 `SCRIPT ERROR`**,
`GET /formables` live-verified over HTTP against the boot 1805 world.

### The structural finding the slice turned on

**A created client could never proclaim.** `process_formations` skipped ANY nation carrying a
`nation_formations` record ("once-only"), and NA-6c's creation writes one at birth — so the C→T
chain was structurally dead: a freed Duchy of Warsaw holding Lithuania + Volhynia would sit
silent forever. The same latch also killed the §11.6-5 watcher for created clients
(`get_formation_watch` returned None on any record), so the dormant Poland dream was invisible
too. Every failure silent, none reachable by NA-6c's tests because no test freed a client.

**The fix is a QUARTET in `formations.py`, all keyed on one distinction** — new
`_is_creation_record` (a creation stamps `id == template`; a formation stamps the forming deck
entry's id):

1. `process_formations` skips only NON-creation records — birth is not formation.
2. `_proclaim` PRESERVES the record's `template` key across the formation — the `from_dict`
   capital re-derivation (§20 Q10) keys off it, and dropping it would cost a reloaded Duchy its
   capital (−1 DP forever, garrison seams intact only until the next load).
3. `_forms_block_for_record` resolves the DECK-entry arm FIRST (by record `id`), template arm as
   fallback — with `template` now preserved, a template-first read would have resolved a formed
   Poland back to "Duchy of Warsaw". A pure creation record's id matches no deck entry, so
   deckless clients (Normandy, Roman Republic) keep their identity — the NA-6c pin holds.
4. `get_formation_watch` retires the watch only for FORMED records — a carved Duchy's dormant
   dream is precisely what the watcher exists to show.

`_resolve_sponsor`'s prior-record arm (dead code since NA-6a, written for exactly this) went
live: the freed Duchy has no lord at proclamation, so **Berlin blames Paris** through the stored
creation sponsor — pinned as the double relation blow (Prussia+Russia −30 vs BOTH Poland and
France, exactly once, no re-fire on save/load).

### "The Polish Question" (§11.9 per-formation threat label — the NA-6a deferred row CLOSED)

- `get_forms_block` gains optional **`grudge_label`**; authored: "The Polish Question"
  (`commonwealth_restored.forms`), "The Roman Question" (RomanRepublic template). Validator
  string-shape check both places; MODDING_FORMAT rows.
- New `get_formation_grudge_contributions(world, budget)` → `[{source:
  "formation_grudge:<tag>", label, amount}]` — per-formation source keys, court-deduped across
  formations in (formation turn, tag) order, clamped inside the SHARED `AGENDA_GRUDGE_CAP`
  remainder. `get_formation_grudge_nations`/`get_formation_grudge_threat` are now views over it
  (every NA-6a pin byte-green).
- `process_coalition_turn` step 2 emits per-formation keys (**conscious source-key flip**:
  `formation_grudge` → `formation_grudge:<tag>`; pinned that the merged key is never emitted).
- Label resolution: new `diplomatic_ledger._threat_source_label(world, key)` — the
  `formation_grudge:` prefix arm resolves the authored label via
  `formations.formation_grudge_source_label`, generic "Nations raised from their lands" as
  fallback; the advisory's what-stirred-Europe list shares the same helper. The France-scoped
  scalar caveat (§11.10-8) is re-pinned on the REAL carve path: a Britain-erected Roman Republic
  costs the relation blows but feeds no France-targeted threat.

### The Formables button (§11.6-8 / decision 9)

- `formations.build_formables_payload(world)` + **`GET /formables`**: one row per Class C
  template AND Class T watcher — `{tag, display_name, flag, cls, gate_terms[{text, met}],
  available, progress, deep_link}`. Availability is the REAL settlement predicate
  (`evaluate_create_client_eligibility` per active war — a drift pin asserts row availability
  equals `_carve_templates_for_court`'s answer for the same war). Rows never hidden, never
  dead: boot Warsaw states "at war with Prussia" + "Posen held at the settlement table
  (currently Prussia-held)", both unmet; an erected Duchy's C row reads "already stands" while
  a NEW T watcher row appears for its dormant Poland dream ("0 of 2 provinces held", "currently
  a vassal of France"); a formed Italy reads "Italy already stands". **The player's own-soil
  row (Normandy, from_court == player) renders the MIRROR term** — "a clause only a victorious
  enemy may put before you" — rather than the absurd "at war with France" (found in the live
  HTTP check).
- `diplomacy_wizard.gd`: step-1 top button **"Formable Nations — states that could yet exist"**
  → step 3 (`_fetch_formables`/`_render_formables`, own `_pending_request` arm, back-button
  returns to step 1), rows in the U6 chip idiom (flag via `Utils.bb_flag` on the row's flag
  TAG, ✓/• met marks, gold-vs-header name by availability); an available row's deep link is a
  gold "↳ Open negotiations — <court>" button into `_on_nation_selected(court)` — the honest
  landing is the defeated court's action list where Open Settlement authors the clause.

### The watcher's `.gd` consumer (§11.6-5 — the NA-6b deferred row CLOSED)

- `diplomatic_ledger.gd` Nations tab: the Design line now appends
  **"→ forms: Poland (1 of 2 provinces held)"** from the agenda payload's `forms` block.
- The war room (`_assess_situation` per-belligerent design lines) appends the same marker
  backend-side — "(forms: Danubia — 1 of 2 provinces held)" pinned through a real boot-war
  opponent.

### Also closed here (the §11.7 final sweep)

- **The risorgimento-block pin** (§11.7 v1.2): a standing Roman Republic holding Rome keeps
  Italy unformed and the watcher honestly reads 4 of 5 — derived behavior, now pinned.
- Watcher copy: a one-province claim reads "holds its claimed province", not "all 1".
- §20.1's "AI treatment of a carved client beyond turn 1" note stays a live-verification item
  for the next played session (no code owed).

**Tests (+29):** the C→T chain (creation-record non-latch, identity transform, vassal dormancy,
permanent latch + save/load, template-key preservation + capital re-derivation, Berlin-blames-
Paris double blow, post-formation `guard_the_vistula`, Duchy-era history respected), the §11.9
list (named contribution, panel label resolution + fallback + static-arm, coalition source-key
emission, wound ends on vassalization/elimination, shared cap, AI-erected no-France-threat,
forms-block normalization, validator), the Formables payload (5 boot rows, never-hidden/never-
dead, honest boot gates, mirror row, qualifying-war deep link + drift pin, erected-and-watching
double row, formed row, endpoint source pin), and the watcher consumers (war-room marker,
nations-tab payload, both `.gd` source-scrapes).

---

## §21.1 Post-landing audit — NA-6d (July 19, 2026)

A six-lens adversarial review of commit `1055a02`, held immediately after
landing on the user's instruction ("audit NA-6d commit and push fixes").
Lenses: the C→T chain, the grudge source-key flip, the Formables payload,
the Godot client, test falsifiability, and cross-cutting Golden-Rule
compliance. **Ten defects confirmed and FIXED; every one was reproduced
live against the 1805 boot world before the fix and re-verified after.**
Regression pins: `tests/test_na6d_audit.py` (23), mutation-checked — each
headline pin was confirmed to FAIL against the pre-fix behavior.

### Fixed

| # | Sev | Defect | Fix |
|---|-----|--------|-----|
| A1 | P2 | The availability scan walked ALL `war_instances`, including CONCLUDED ones (retained `ARCHIVE_RETENTION_TURNS`). For up to 10 turns after any peace where the player kept the template soil, the row read `available: true` with a deep link the settlement layer refuses as `war_archived` — beside its own "at war ✗" gate term. The §11.6-8 "never dead" contract, broken. | Filter through the shared `_iter_active_war_instances`, as every other settlement consumer does. |
| A2 | P2 | The total-annexation refusal had **no gate term**. The Papal States are a one-province polity, so the Roman Republic row showed two green ✓ and no button, naming nothing the player could act on. | New gate term stating the war-score floor and the current score. Also added the soil-provenance term (`carve_not_defeated_soil`) for multi-province templates. |
| A3 | P2 | The Class C row rendered the template's BIRTH identity, so a Duchy of Warsaw that had gone on to proclaim Poland showed the **dead name** — while `Utils.bb_flag` DID resolve the override, drawing Poland's flag beside the label "Duchy of Warsaw" — and the Class T pass emitted a **second row for the same tag**. | Resolve through `get_display_identity`; dedup the redundant formed arm (the unformed watcher row is deliberately kept). |
| A4 | P2 | **A re-carve un-latched a "permanent" formation.** A carved client conquered out of `get_active_nations()` could be re-carved; `_proclaim_creation` overwrote the FORMED record with a creation record, so the nation proclaimed a SECOND time — second card, second +2,000 gold, doubled −30 against every aggrieved court. | `_proclaim_creation` preserves the `formed` marker across re-erection. |
| A5 | P3→ | **Unbounded reward loop.** `_is_creation_record` inferred "created" from `id == template`, coupling the `agendas` and `formable_nations` namespaces. A deck entry id equal to a formable tag made a FORMED record read as a creation record: the poll never latched and the nation re-proclaimed **every turn** — +2,000 gold and a fresh −30 per tick, forever (verified live: 500 → 2,500 → 4,500 → 6,500). | Explicit `formed: true` marker stamped by `_proclaim` (the equality is now only a pre-marker fallback) **plus** a validator error on the collision. |
| A6 | P3 | `coalition._calculate_formation_grudge_threat` lost its only production caller in this commit; the test that "pinned the wiring" called the dead wrapper and would have stayed green if coalition step 2 were deleted outright. | Helper deleted; the stale test replaced with a pre-NA-6d-save label-fallback pin. (The real wiring pin, `test_coalition_step_two_emits_the_named_source`, drives `process_coalition_turn` and stands.) |
| A7 | P3 | `progress` hardcoded the plural in two places, both newly rendered by this slice: **"0 of 1 provinces held"** for Holland→United Netherlands, live at boot, on the Formables browser, the ledger Design line and the war room. §21 had claimed this copy fix landed — it landed only in the gate-term composition. | Single source `formations.format_progress`, shared by the watcher and `agendas.build_agenda_payload`. |
| A8 | P3 | The wizard iterated `row.get("gate_terms", [])` with no `is Array` guard — the project's own documented `.get()`-returns-null footgun, and the one spot in the new code breaking the file's idiom. | Type-guarded. |
| A9 | P3 | An empty catalogue (the maintained `SOVEREIGN_MAP=legacy` rollback authors none) routed through `_show_error`, which resets to step 1 and hides Back — stranding the player on a screen still titled FORMABLE NATIONS with no way back. | Render the empty state in place; Back keeps working. |
| A10 | P3 | `build_formables_payload` computed the exact qualifying `war_id` per row and the wizard **discarded it**, so a player in two wars with the same court fell into the multi-war ambiguity picker and could choose the war where the clause is refused — right after a row promised availability. | **WITHDRAWN — the fix was inert and was removed.** It threaded the war_id in as a fallback for an empty `action_payload["war_id"]`, but `diplomacy.py` forces `available: false` for BOTH the multi-war-ambiguity and no-common-war cases, so an available `open_settlement` always carries its own war_id and the fallback could never fire. It was pure leakable state (it had already needed three separate clears to stay safe), so it was deleted rather than left looking like a fix. The underlying gap is real and untouched: routed as `DESIGN_REFINEMENT` **NAD-4**, with the backend invariant that makes removal safe pinned by `test_the_backend_invariant_that_makes_it_inert_still_holds`. |

Documentation defects fixed in the same pass: `SAVE_FORMAT_REFERENCE.md`
described the `template` key's ownership and the identity-resolution order
**backwards** (NA-6d inverted both), and `SYSTEMS_REFERENCE.md` §28 still
documented a `formation_grudge` threat key that is no longer emitted. The
`formations.py` module docstring's "nothing is nation-hardcoded" claim was
narrowed to the mechanics helpers (the two display builders are named
exceptions), and `_resolve_sponsor`'s comment corrected — its lord arm is
unconditionally dead, not "live for the creation record".

### Verified clean under adversarial probing

Save compatibility across the source-key flip (threat sources are per-turn
display telemetry only — no accumulation store, no per-source decay);
`AGENDA_GRUDGE_CAP` arithmetic (cannot be exceeded, negative budgets
degrade to zero); `add_threat` in a loop being total-identical to one
merged call; the court-level dedup and its `(turn, tag)` ordering; fog (a
province's controller is public political knowledge per
`FOG_OF_WAR_SPEC.md` §2, consistent with `region_panel.gd`); crashes on
legacy / `SOVEREIGN_SCENARIO=none` / attribute-less worlds; GR2 `int()`;
GR8 (no new region scans; `/formables` is on-demand, measured 3.84 ms);
serialization round-trip; R7 display names; the GET-endpoint convention.

### The three design calls — DECIDED July 19, 2026

Escalated at first report, then delegated back ("fix things and make own
calls"). All three are settled; no blessed number moved.

**D1 — one grievance, one voice: the flat +1 §11.9 already blessed.
FIXED, cap untouched.** The diagnosis was right, and both proposed
remedies were wrong. Raising `AGENDA_GRUDGE_CAP` would have moved two
NA-3 pins to buy what allocation gives free. A first fix made allocation a
floor-first fair share — which restored the naming but left the amount
**context-dependent**: a lone Poland showed +2 and silently dropped to +1
the moment an unrelated republic was erected, on a panel whose entire job
is explaining grievances. Re-reading §11.9 settled it: the spec blesses
`+1/turn` per contributor, flat. NA-6a's per-aggrieved-court scaling was
never blessed at all, and it was the actual root cause — one formation
with two courts consumed the whole cap. `get_formation_grudge_contributions`
now emits a flat **+1 per standing formation**, so `AGENDA_GRUDGE_CAP`
reads as what it is: how many named questions can weigh on Europe at
once. **"The Polish Question" renders beside "The Roman Question"**,
verified live on real data. Consciously flipped pin:
`test_the_standing_wound_names_itself` 2 → 1. Grievances beyond the
budget emit nothing and are debug-logged — real, deliberate, and pinned,
because a silent drop on this surface is the failure mode the slice
exists to remove.

**D1b — the wound now lapses with the nation it names. FIXED.** §11.9
stands the grievance up "**while the formation stands**", but the
derivation never checked that the formed nation was still alive, and
`_eliminate_nation` deliberately does not prune `nation_formations` (the
record is the permanent historical latch). A Poland conquered out of
existence therefore kept pushing "The Polish Question" +1/turn forever,
naming a country no longer on the map — a dead-name defect on the very
panel this slice was cleaning. `_formation_grudges` now skips a formed
nation absent from `get_active_nations()`. Berlin and St Petersburg got
what they wanted; the grievance is answered.

**D2 — a state raised twice may dream twice, but the world pays once.
FIXED.** The audit's own A4 patch took the conservative arm (latch the
formation shut forever), which removed the exploit but left a real wart: a
Poland liberated, lost to reconquest, and liberated again would read
"Duchy of Warsaw" forever with no path back — a dead name by a different
route. Re-formation is now ALLOWED; what does not repeat is the **windfall**.
A new `rewarded` record key (serialized, pay-once, carried across
re-erection, read through the single source `_has_been_rewarded` so both
proclamation paths agree) makes `_proclaim` skip
`_apply_formation_rewards` on a repeat. The second Proclamation still
fires — it is a real moment — and the card omits the gold line entirely
rather than claiming "+0 gold".

The **aggrieved blow, by contrast, DOES re-fire**, on both the formation
and the creation path. This is the direct consequence of D1b: the wound
lapses when the nation dies, so a Poland raised a second time is a second
outrage and Berlin is entitled to feel it. The first cut of D2 suppressed
the repeat blow on the reasoning that the wound "never lapsed" — which
was true of the code as it then stood and false of the spec; fixing D1b
inverted it. Never farmable: the blow costs the carver relations rather
than paying them, and `modify_nation_relation` clamps at −100, so a
re-carve loop damages only the player who runs it.

**D3 — `Normandy`'s empty `aggrieved` list is CORRECT. No change.** The
original finding compared Normandy to the Roman Republic and called the
difference an asymmetry. The right comparison is the Duchy of Warsaw:
both are "carve a client from a great power's soil", and **neither
aggrieves anyone at creation** — the ceded-from court signed the clause at
the table; the outrage comes later, if and when the client proclaims
something bigger (Warsaw → Poland aggrieves Prussia and Russia). The Roman
Republic is the deliberate exception for an authored reason: a *republic*
in Rome is an ideological affront to Catholic monarchies, so Austria and
Spain resent its existence itself. France is not a third party to the
Normandy carve — it is the victim, already at war with the carver and
already paying the territorial loss; adding it to `aggrieved` would
double-count. Recorded here so the question is not re-raised.
