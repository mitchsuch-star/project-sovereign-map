# Nation Agendas — "The Designs of the Powers"

**Status:** v1.0 — ✅ **DESIGN GATE HELD July 17, 2026.** The user answered the three gate questions at the recommended defaults (§0). This spec is the gate record AND the build contract for the Phase 8.5 centerpiece.

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
| `deny_regions` | `regions[]` | ≥1 target controlled by the hegemon's bloc (share ≥ 0.33) | no target in hegemon bloc hands | resolve, acceptance, subsidy targeting — never self-conquest |
| `contain_hegemon` | `share_floor` (default 0.33) | hegemon bloc share ≥ floor AND self outside that bloc | share < floor | coalition resolve (fights longer in coalition wars), proposal motive |
| `paymaster` | `treasury_floor` | at war with the hegemon OR active coalition vs hegemon, AND treasury > floor | — (posture, not a quest) | subsidy escalation (§5.7), gold-flavored asks |
| `guard_neutrality` | `guard_regions[]` | self at peace | — (posture) | cheap refusal of coalition asks; the violation trap (§5.9) |

**Built-in survival override — "The Knife at the Throat" (not authored):** for every nation, if the capital is lost or the majority of `nation_starting_regions` is lost (the `get_authority_proxy` 25-band, `jealousy.py:351-374`), the deck is overridden by an implicit survival posture: resolve pushes toward peace (§5.5 `SATISFIED` arm semantics), no target bias, ledger shows "Survival — the dynasty above all." Checked first, before the deck.

### §3.2 Authoring & validation

New scenario key `agendas` in `europe_1805.json`: `{nation: [{id, type, title, blurb, regions?/params…}, …]}`. **Deck order = priority order** — first agenda whose predicate holds is ACTIVE (exactly one active per nation; the rest are latent and visible via the war room). Validator support in `backend/modding/validator.py` on the `marshal_pool` precedent (`validator.py:436-513`): type-check the container, enum-check `type`, cross-validate `regions` against the region registry and nations against the roster (warning-not-error for unknown nations, matching the `relationships` forward-compat stance). New `MODDING_FORMAT.md` row. Nations without authored decks (minors, satellites) get no deck — survival override only; vassals never activate agendas while vassalized.

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

**No decks (survival override only):** France (player — Victory Pass owns player goals), Spain/Naples/Portugal and all minors not listed, and the satellites (Holland, KingdomOfItaly, Switzerland, Bavaria, Saxony, Hesse, Hanover, PapalStates) — vassals never activate agendas while vassalized. **Cut with owner:** Russia `eastern_question` (Constantinople/Rumelia — needs AI-AI war declaration; § 9 → ROADMAP 8c).

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
- **Buy-them-out:** no new machinery — §5.2's `agenda_mod` on separate-peace/settlement offers IS the isolation lever; the existing separate-peace fallout penalties (`diplomacy.py:3865-3941`) already price the betrayal side.
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

For an active `guard_neutrality` agenda: a belligerent nation (at war with anyone, not at war with the guard-holder, not its ally/lord) with a marshal standing in a guard region triggers a one-time violation: relation `AGENDA_VIOLATION_RELATION_PENALTY` between violator and guard-holder + a dispatch/campaign-log beat ("Berlin seethes: foreign columns cross Ansbach."). Latch = bounded event-log lookback (the `_calculate_defensive_refusal_memory_threat` idiom) keyed (violator, guard-holder) — fires once per pair per `AGENDA_VIOLATION_COOLDOWN` turns. Applies to the player and AI alike (GR5): marching the Grande Armée through north Germany costs Prussia's goodwill, exactly as it did Napoleon.

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
| **NA-0 Substrate** | `agendas.py` (types, predicates, cached `get_active_agenda`, resolve/acceptance/bias helpers as pure functions), scenario `agendas` key + authored §4 decks, validator block, `MODDING_FORMAT.md` row, `nation_agenda_seen` serialization (+ SAVE_FORMAT_REFERENCE). No consumer changes. | Boot pins green: Austria active=`redeem_italy`, Prussia=`hanoverian_prize`→`armed_neutrality` (peace predicate), Britain=`low_countries`, Russia=`arbiter_of_europe`; survival override pin (capital lost → override); cache-invalidation pin; serialization round-trip. |
| **NA-1 Legibility** | §5.1 in full: ledger row + `.gd` render, war-room lines + recommendation branch, `agenda_pursuit` motive reason + register bank, dispatch shift beat + campaign-log type. Touches `.gd` → **boot the engine, grep `SCRIPT ERROR`** before landing. | Ledger/war-room/motive/dispatch tests; live curl of `/diplomatic_ledger`; the standing new-dialogue rules do NOT apply (no new popup — existing surfaces only). |
| **NA-2 Diplomacy teeth** | §5.2 `agenda_mod` + full component/label/feedback wiring; covets unification + dead `NATION_DESIRES` territory-row deletion; §5.3 R155 cadence; §5.4 Pressburg arm + courting bias. | Acceptance-component pins both directions; preview shows the term; hawk-persistence pin; coalition-member separate-peace pin; corpus untouched (no new player verbs). |
| **NA-3 War coupling** | §5.5 resolve deltas; §5.6 target bias + `ENEMY_AI_REFERENCE.md` update (incl. drift fixes); §5.7 paymaster generalization + tiers; §5.8 grudge contributor; §5.9 violation trap. | M1–M7 sweep harness **byte-identical or consciously re-blessed** (the harness roster's agenda exposure must be checked first); resolve pins (advancing fights longer / satisfied sues); target-bias pin (Austria corps prefers Milan-ward valid target); paymaster tier pin; grudge + violation pins both sides (GR5). |
| **NA-5 Ultimatums (follow-on)** | §8, built only after NA-0..3 are verified in a live playtest. | §8 completion definition. |

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
| Player-France agendas / goals | None — sandbox stays open-ended | Pre-Ship Victory & Objectives Pass |
| Dynamic agenda *generation* (post-authored decks) | Explicitly rejected at G1 | re-open only via a future user gate |
| Agenda-driven AI settlement-term authoring (beyond direction/indemnity) | Not in pass 1 | Pre-EA Diplomacy Polish Pass (with AUD-d rebuild) |

---

## §10 Test plan (summary)

`tests/test_nation_agendas.py` (NA-0..3) + `test_nation_agendas_ultimatums.py` (NA-5). Pillars: boot-state pins for every authored deck (§7 NA-0); predicate unit tests per type incl. vassal-dormancy and elimination; cache/invalidation + serialization round-trip; acceptance component both signs + preview visibility; resolve deltas at the P1 seam (advancing/satisfied/irrelevant); coalition Pressburg arm; target-bias preference without gate changes; paymaster tiers + GR5 (non-Britain paymaster); derived grudge (fires, caps, expires, disappears when targets returned — the R156 payoff pin: *returning Milan to Austria removes the grudge AND the acceptance penalty*); Ansbach trap both directions (player violator + AI violator); M1–M7 harness stability check at NA-3. Suite + ruff green per slice; the golden corpus gains rows only if NA-5 adds typed responses.
