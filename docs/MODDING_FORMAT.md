# Modding Guide for Project Sovereign

This document describes how to create custom scenarios, marshals, and regions for Project Sovereign using JSON files.

## Quick Start

The simplest mod is a scenario file with just one line:

```json
{
    "player_nation": "France"
}
```

This creates a game with default map and marshals, playing as France.

## Validation Tool

Before loading your mod, validate it:

```bash
python -m backend.modding.validator path/to/your/scenario.json
```

This will report any errors or warnings in your JSON file.

## Loading Scenarios

In Python code:

```python
from backend.models.world_state import WorldState

world = WorldState.from_scenario("mods/examples/battle_of_waterloo.json")
```

---

## Scenario Format

A scenario file is a JSON object with the following structure:

```json
{
    "scenario_schema_version": 1,
    "scenario_name": "Battle of Waterloo",
    "scenario_description": "June 18, 1815",
    "player_nation": "France",
    "current_turn": 1,
    "max_turns": 40,
    "gold": 1200,
    "regions": { ... },
    "marshals": { ... }
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| None | - | All fields are optional! Defaults are applied. |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `scenario_name` | string | - | Display name — **since POSITION 7 (Aug 8, 2026) it is SERIALIZED as `WorldState.scenario_name`**. **Corrected October 23, 2026 (S14D-X16):** it is NOT display-only — since TUT-F5 it selects a scenario's CARVE-OUTS: `tutorial_state.is_school_world()` is the ONE predicate by which a School lesson switches a subsystem off wholesale (jealousy and glory, the dotation, the client petitions, the campaign autosave); it is world-scoped and never an input to a formula. The client's School of War overlay arms on the names in `tutorial_state.SCHOOL_SCENARIOS` (`"tutorial"` the Danube, `"tutorial_table"` the Table), so a scenario using one of those ids opts into the tutor card; any other value is inert identity. Allowlisted names may be requested over `POST /new_game {"scenario": <name>}` (see `SCENARIO_ALLOWLIST` in `backend/main.py`). |
| `scenario_description` | string | - | Description (metadata only) |
| `scenario_schema_version` | integer | 1 | Scenario schema version. `1` is the current scale-readiness era shape. |
| `player_nation` | string | "France" | Nation the player controls |
| `current_turn` | integer | 1 | Starting turn number |
| `max_turns` | integer | 40 | Game length in turns |
| `gold` | integer | 1200 | Starting gold |
| `regions` | object | (default map) | Custom map regions |
| `marshals` | object | (default marshals) | Custom marshals |
| `enemy_nations` | array | ["Britain", "Prussia"] | AI-controlled nations |
| `nations` | object | {} | Optional authored nation records. In schema v1, this is where static nation metadata like `power_tier` belongs. Runtime `political_status` is not authored here. |
| `start_date` | string | "" | **HC-0 "The Calendar":** the display anchor (`"YYYY-MM-DD"`); turn 1 is its half-month and each turn is half a month (`backend/game_logic/calendar.py`). Validated as a real date. `""` = plain "Turn N" labels. GE-1's Verdict names its date from it (turn 44 of `1805-09-25` = "Early July 1807"). |
| `campaign_end` | object | - | **GE-1 "The Verdict and the Fall" (`GAME_END_SPEC.md` R7, `ENDGAME_PLAN.md` §3):** the block whose PRESENCE arms the campaign's endings — the Fall (two warned clocks plus the Emperor's death), the Verdict of History, the Humbled Peace. A new derived flag, never `sandbox_mode`. Keys: `verdict_turn` (REQUIRED when the block is present; int 2–400 — at the END of that turn the Verdict is rendered and the campaign continues), `fall_grace_turns` (int 1–60, default 5 — "The Empire Without Soil or Sword"), `captivity_grace_turns` (int 1–60, default 10 — "The Eagle in Chains"), `title_turns` (int 1–120, default 12 — the quiet possession after which a conquest is titled). **GE-3 "The Congress of Paris" (`ENDGAME_PLAN.md` §2.7), every one optional with the ruled default:** `hold_titled` (int 1–126, 50 — titled provinces to summon and to hold), `congress_turns` (int 1–40, 8 — the sitting), `recognition_threshold` (int 0–200, 50 — the at-peace formula's bar), `refuser_weight_per_turn` (int 0–100, 15 — a refuser's intent against the summoner per turn of refusal), `congress_alarm_gate` (int 0–100, 40 — the coalition's brewing gate while two great powers refuse), `hold_alarm_ceiling` (int 1–100, 80 — the hold breaks at this alarm), `cs_shutout_pct` (int 1–100, 50 — the Continental System closure that shuts the trade-dominance court OUT; an integer percentage, the block being int-only), `sue_score` (int −100–0, −40 — the pair war score at which a court at war sues), `sweetener_per_1000` (int 0–100, 10) and `sweetener_cap` (int 0–100, 20) — the table's gold, `dissolve_alarm` (int 0–100, 15) and `congress_cooldown` (int 0–60, 10) — a dissolution's price. Booleans are rejected; out-of-range is an ERROR; an unknown key is a WARNING (a scenario for a newer build must still boot). A block on a legacy-map scenario warns (never read there). Absent = the campaign is open-ended (the tutorial, the bare flag world). Never give a key a variance band (D7: no band, no variance). |
| `sovereign_map` | string | "legacy" | Which world the scenario targets: `"legacy"` (19-region fixture) or `"europe"` (the 126-province Europe world). Selects the default map/roster injected for omitted fields AND which nation roster the runtime-support validator checks against (1805 Loader pre-slice). |
| `starting_wars` | array | [] | ORDERED list of `{"attacker": str, "defender": str}` pairs. Seeded through the live `ensure_war_instance_for_pair` machinery after load — the first entry naming a side fixes the war instance's leaders, and later entries sharing a participant attach to the same instance (so France-first ordering yields ONE shared coalition war). Also sets the pair's diplomatic state to WAR and seeds `war_start_turns`. Do NOT hand-author raw `war_instance` JSON. |
| `region_overrides` | object | {} | Per-province shallow field overrides applied AFTER the default-map injection (Map Slice 8 / DEF-6): `{"Flanders": {"garrison_strength": 12000}}` stamps fields onto the named region dict without inlining the whole map. Keys must name existing provinces — an unknown name fails the load loudly. Works with authored `regions` too (merge wins). The shipped 1805 scenario uses it for the Flanders and Normandy Channel-coast depots and, since SR-5a (September 28, 2026), for the ruled economy balance: every French homeland province's `income_value` at three-quarters of the registry figure and five English provinces raised (`_economy_balance_comment` documents it). An `income_value` override is scenario-scoped — the registry and every other scenario keep their figures. |
| `marshal_pool` | object | {} | **Marshal Recruitment (Jealousy v3.2 — `MARSHAL_RECRUITMENT_SPEC.md`):** `{nation: [candidates]}` commissionable bench. Candidates are marshal entries WITHOUT `location`/`strength` (spawn-derived: capital, or the richest held homeland province; 5,000-man corps drawn from the infantry pool) plus a REQUIRED positive-int `cost` (gold). Personality must be an implemented type (the MC-4 boot guard extends here — retired types hard-fail validation). `relationships` seeds apply symmetrically to marshals in service; seeds may reference roster OR pool names (author pool-to-pool pairs on BOTH entries — arrival order must not matter). A candidate name colliding with the starting roster is a validation ERROR. Nations without a pool simply cannot recruit. |
| `contingents` | object | {} | **VD-C "The Contingent" (Score Finish Step 5, October 3, 2026 — `VASSAL_DEEPENING_SPEC.md` §9.1):** `{nation: [commanders]}` — the generals a satellite sends at the head of its contingent when it shares its lord's war: the first who is not serving, fallen or on any bench; past the list the contingent is named "<Adjective> Contingent". Commanders are the bench's candidate shape (`name`, `personality`, `skills`, `tactical_skill`, `trust: {"value": N}`, `biography`) with NO `cost` (a commander is sent, never commissioned — a `cost` is a validation ERROR) and no `location`/`strength` (both derived at the raise: the satellite's muster province; `income × 15 × loyalty / 100`, rounded to 500, in [3,000, 12,000]). The MC-4 personality guard extends here (a retired or unknown personality hard-fails; a `sovereign` is refused); a name must be new against the roster, every bench and every other commander, and the WO-13 collision check reads these names too. Optional — a nation without an authored list still raises a contingent under the generic name. |
| `agendas` | object | {} | **Nation Agendas (NA-0 — `NATION_AGENDAS_SPEC.md`):** `{nation: [agenda]}` authored historical decks. **Deck order = priority** — the first agenda whose predicate holds is ACTIVE (exactly one per nation). Each entry: REQUIRED `id` (unique per deck), `type` (one of `acquire_regions`/`deny_regions`/`contain_hegemon`/`paymaster`/`guard_neutrality`), `title` (player-facing); the three region-typed kinds REQUIRE a non-empty `regions` list (names cross-checked against the region set when present); `contain_hegemon` takes optional `share_floor` (number in (0,1], default 0.33), `paymaster` optional `treasury_floor` (non-negative int); optional `blurb`. Unknown nation keys WARN (deck never activates). Vassals never activate agendas while vassalized — a satellite MAY carry a dormant deck that wakes on independence. Nations without decks get the built-in survival override only. **NA-6 formables:** an entry may carry an optional `forms` object — REQUIRED non-empty `display_name` (the new name on every player surface), optional `flag` (heraldry asset tag; defaults to `display_name` with spaces stripped), optional `blurb` (the Proclamation's engraved line), optional `aggrieved` list of nations that take a one-time −30 relation blow with both the formed nation and its sponsor, then feed a standing threat contributor; optional `grudge_label` (NA-6d — the threat panel's name for that standing wound, e.g. "The Polish Question"; string; only meaningful beside `aggrieved`, and absent it falls back to the generic "Nations raised from their lands" row). When that entry's SATISFACTION condition holds while the nation is free (never vassalized), it forms once and permanently: +2,000 gold, +2 stability in every owned region (capped), and deck priority natively activates the NEXT authored entry as the post-formation goal — so author that entry too. `forms` is only valid on `acquire_regions`/`deny_regions`/`contain_hegemon`; the postures (`paymaster`/`guard_neutrality`) never reach a satisfied state, so a `forms` block on one is a validation ERROR rather than a formable that can never fire. Unknown `aggrieved` nations WARN. **Authoring note:** the "N of M provinces held" progress marker is only meaningful for `acquire_regions` — `deny_regions` and `contain_hegemon` satisfy on hegemon-bloc share rather than on self-control, so their marker will read 0-of-M while the design is genuinely advancing. Prefer `acquire_regions` for anything a player is meant to watch approach. A nation whose forming entry is ALREADY satisfied when the scenario boots would proclaim on turn 1; author conditions the starting world does not meet. **AI-0c deck-order band:** entries sharing a positive-int `order_group` value (a CONTIGUOUS run — a split group is a validation ERROR, a single-member group a no-op WARNING) are equally-live designs the campaign seed may reorder; the `historical` seed keeps authored order, and the key is stripped at load so the serialized deck is shaped exactly as before. Author it only where deck order was genuinely contested (the shipped file bands Austria's Italy-first/Germany-first pair; Russia's deck is deliberately unbanded — pin 22). |
| `nation_relations` | object | {} | `{"NationA\|NationB": value}` — pair keys MUST be alphabetically sorted (an unsorted key is unreachable at runtime and is a validation ERROR). A value is a bare int in [-100, 100] (fixed), or — **AI-0c variance bands (`AI_INTENT_SPEC.md` §3.8.1, D7)** — a band-carrying object `{"value": int, "band": [lo, hi]}` (the trust `{"value": N}` authoring idiom): the campaign seed resolves the relation inside `band`; the `historical` seed (or unset `SOVEREIGN_SEED`) ALWAYS resolves to `value`, byte-identical to a bare int. **No band = no variance** — the engine cannot invent a range it was not given. Clamps (validation ERRORs): the band must contain `value`; a band on a pair appearing in `starting_wars` must sit entirely below the −60 armistice-first line (`ARMISTICE_AUTO_PEACE_RELATION`) so no seed can flip a boot war's truce-expiry behaviour. Bands are resolved at `from_scenario` — the save file and `from_dict` only ever see plain ints. |
| `threat_level_band` | array | - | **AI-0c:** sibling `[lo, hi]` band for the top-level `threat_level` (0 ≤ lo ≤ hi ≤ 100, must contain the authored value). The seed resolves the campaign's central pressure inside it; `historical` keeps the authored value. Narrow by design — widening the envelope escalates (D7). |
| `statecraft` | object | {} | **AI War Decision AI-3r (`AI_WAR_DECISION_SPEC.md` §2.6, gate ruling R1):** `{nation: {"wary_of": {neighbour: multiplier}}}` — authored rear-security posture. `wary_of` multiplies that neighbour's MENACE in the war council's reserve calculus (`get_rear_reserve`): a fear the relations number alone would understate (the shipped file authors the German dualism both ways, Prussia's dread of Russia, the Russo-Turkish menace, Sweden's fear for Finland). **v1 authors `wary_of` ONLY** — any other sub-key is a validation ERROR; the statecraft PROFILE table (style/reaches_first/coercion/weight_mod/haggles) stays code-authored in `nation_config.NATION_STATECRAFT`. Clamps: values must be numbers in **[0.5, 2.0]** (ERROR), a self-reference is an ERROR, an unknown target nation is an ERROR, an unknown top-level nation WARNs (the posture is never read). Absent pair → 1.0; absent block → every posture 1.0. D7's principle: the bounds are authored content, reviewable in the scenario file — ahistorical paranoia is structurally impossible. |
| `navies` | object | {} | **DEF-5 naval (`NAVAL_SPEC.md` §3.2/§8):** the authored Wooden Wall — `{nation: row}`. A FLEET row: `ships` int 1–150 + REQUIRED `readiness` 40–100, optional `admiral` (display string, never an object), `ports` (non-negative int — the Continental System closure weight; island rows are excluded from the denominator), `dockyards` (non-empty list of COASTAL provinces the nation CONTROLS at boot — the build sites; an inland yard is a validation ERROR (NUI-2, Sept 24, 2026: the fleet, the keel chip and the blockade glyph stood on land), and on the Europe registry so is a yard with no registry `port_anchor` — no open water to moor at, the Estonia case, coastal as a sea-link end but with no sea; conquest grants yards at runtime, §3.4a), `island` (bool — the blockade war-weariness clause + the blockade-at-war AI doctrine), `trade_dominance` (non-negative int — absorbs the old Britain coastal naval_income; scaled ×(1−closure), floor ×0.4, suspended under blockade), `overseas_income` (int 0–1200, validator-clamped — **EB-2, the Econ Balance gate Aug 7 2026, `ECON_BALANCE_GATE_2026_08_07.md` §3:** the authored colonial/overseas pool, colonies as a MODIFIER never map objects; the trade-dominance HOLDER scales it ×(1−closure) floor ×0.4 and loses it under blockade; a NON-holder colonial power loses it while blockaded, keeps ×0.25 while at war with the dominance holder, full otherwise; renders as its own positive "Overseas Trade" ledger component; on the 1805 boot Britain 500 / Spain 250 / Holland 150 / Portugal 150 and France deliberately authors NONE — its overseas arm is continental Requisitions), `camp_provinces` (the §5.3 Descent staging shores). A `ships: 0` row is PORTS-ONLY — it authors the closure denominator and may NOT carry `readiness` or `dockyards` (both are validation errors). Omitting the whole block keeps the naval layer dormant (no crossing gate, no blockade, no Admiralty). The registry `is_coastal` flag is never read for coverage/closure/building — coverage keys off the registry's hand-authored `sea_links`, closure off `ports`, building off `dockyards` — but it IS read for the shore itself (landing targets, embarking from a foreign shore, shore supply, the AI's beach search), and since NUI-2 it follows the painted map: `python -m tools.gen_port_anchors --audit` checks every flag against the art (recorded exceptions carry their reasons), and every coastal province carries a registry `port_anchor` where the map draws its fleet. |
| `formable_nations` | object | {} | **Nation Agendas NA-6c (`NATION_AGENDAS_SPEC.md` §11.4):** the CATALOGUE of client states a conquering side may carve out of a defeated party's soil at the settlement table via the `create_client` clause. `{tag: template}` — the KEY is the new nation tag and must NOT collide with a live nation (that is an ERROR: erecting a state that already exists is incoherent and would silently re-home a live court's regions). Each template: REQUIRED non-empty `display_name` (the tag is never shown to the player) and a REQUIRED non-empty `provinces` list (the whole carve eligibility predicate — every province must be held by the carver's bloc AND have belonged to the court being carved, per its registry `starting_controller`); optional `flag` (heraldry asset tag, defaults to `display_name` with spaces stripped), `blurb` (the Proclamation's engraved line), `aggrieved` (nations taking the §11.9 one-time −30 relation blow with both the new state and its sponsor — roster misses WARN), `grudge_label` (NA-6d — the threat panel's name for the standing wound; string), `seeds` (`gold` non-negative int, default 500; optional `manpower`, `actions`, `authority`, and a `diplomat` record in the `{name, personality, skill, biography}` shape), and `deck` (the client's own agenda deck, held to the IDENTICAL schema as an authored `agendas` deck — it lies dormant while the client answers to a lord, and a deck entry carrying a `forms` block makes the client itself formable later, the C-to-T chain). **Nothing in this block exists at boot** — it is a catalogue of what MAY be erected, not a roster. Any side may carve (GR5): the shipped Duchy of Normandy is the coalition-side mirror, carved from French home soil. A new tag also needs its companion rows — `NATION_DESIRE_PROFILES` + `TALLEYRAND_COMMENTARY` (both degrade SILENTLY), `NATION_POWER_TIERS` (unauthored = `secondary`, a middle power), `Utils.NATION_COLORS` (unauthored = bug-magenta) and a heraldry SVG with its `.import` sibling. |
| `doctrines` | object | {} | **SR-7d "The Doctrines" (`DOCTRINES_SPEC.md` §1, §9):** `{court: doctrine}` — one per great power. Each: REQUIRED `name`, `says` (printed verbatim), `strength` and `flaw` (each `{"type", "value", "name"[, "arm": "all" | "stripped_at"]}` from the closed set `arrival_bar` (int ±20, the BAR), `attack` / `defense` (0–0.25), `recruit_price` (×0.5–1.5, `"arm": "all"`, the draft only), `defeat_morale` (×0.25–2.0), `supply` (×0.5–1.0 with `stripped_at` 0.1–0.5)); OPTIONAL `cured_by` (a law id in the SAME court's `reforms` deck carrying a `cures` clause naming this flaw; the deck must carry a Staff) and `shared_on_purpose` (two courts sharing an identical clause without it is a WARNING). A value that does nothing (0, 1.0) and any key the seam does not read are ERRORS. A court beyond the five great powers is a WARNING. |
| `poor_country` | array | [] | **SR-7d (D-R1):** the authored poor-country list — province names where a supply-clause army draws its reduced share outside its homeland (stripped country is read from war damage, never authored). Every name must exist (ERROR). |
| `reforms` | object | {} | **SR-5r "The Laws" (`REFORMS_SPEC.md` §1, §4, §5):** `{court: [law]}` — each great power's authored reform deck; **list order = the AI's enactment order** (§7). Each law: REQUIRED `id` (unique per deck), `name` (display), `date` (the historical act), `currency` (`gold` or `authority`), `price` and `upkeep` (ints ≥ 0; upkeep is gold a turn, political laws included — R2), `effects` (1–2 clauses, each `{"type": …}` from §4's closed set: `actions`, `manpower_regen`, `recruit_price`, `recruit_morale`, `drill_morale`, `supply_capacity`, `satellite_loyalty`, `cs_closure`, `blockade_denial`, `cures`) and `says` (the one sentence the ledger prints verbatim). **Only effect types WIRED in this build validate** (`reforms.WIRED_EFFECT_TYPES` — every type since SR-7d DC-2 wired `cures`: `{"type": "cures", "flaw": "<the court's doctrine flaw name>"}`): a law must do what it says the day it ships ("strike, never invent"). **Each type's parameters are closed** (`reforms.CLAUSE_SHAPES`): `manpower_regen` `{pool: "infantry", value: int 1–100}` (+%); `recruit_price` `{arm: infantry|cavalry|artillery|all, value: float 0.5–1.5}` (×, the draft only); `recruit_morale` `{arm, value: int −30–30}`; `drill_morale` `{value: int 1–20}`; `supply_capacity` `{value: float 1.0–2.0}` (× the fed multiplier); `satellite_loyalty` `{value: int 1–5}` (a turn, every client); `cs_closure` `{rule: "every_client"}`; `blockade_denial` `{value: float 1.0–2.0}` (× the loss of a court the law's holder blockades). A float of 1.0 is refused (it does nothing), and so is any key the seam does not read. An unknown or unwired type, a third clause, an unknown currency or a missing field is an ERROR. **Each court's deck carries exactly ONE `actions` law — the Staff — and every court's Staff shares one price and one upkeep** (§5, GR5): a second Staff or an unequal one is an ERROR. **Nothing is in force at boot:** a scenario may not author `enacted_turn` or `lapsed_turn` (ERROR). Keys starting with `_` are comments. v1 authors five decks (France, Austria, Prussia, Russia, Britain — R6); a minor court has no laws. |
| `imperial_designs` | object | absent | **VP-1 "The Emperor's Designs" (`VP1_DESIGNS_SPEC.md` §2, §3, §8):** the player's roads. REQUIRED `owner` (a nation) and `roads` — a list of roads, each with `id` (one of `rhine`, `crowns`, `system`), `title`, `proclamation`, `alarm_source`, a `gate` (`type` one of `ally_or_vassal`, `vassal` (both naming a `court`), `at_war_with_trade_dominance`; a `reason`), `teeth_proclaim` (`alarm` int, `relations` {court: int}), optional `aliases` (a list of strings — the plain words the road is named by: "the Rhine", "Italy") and exactly two `designs` — one `role: construction`, one `role: seal`. Each design: `id`, `title`, `role`, `type` (`clients` with `courts` and `need`; `brought_to_terms` with `courts`; `titled` with `provinces`; `titled_and_terms` with `provinces` and `courts`; `shut_ports`; `britain_signs`), REQUIRED `hint` (one line: what the design asks, in the Cabinet's nouns) and `control` (the Cabinet row that does it, beginning "F1 →" — never a typed order), an optional `hold` (end turns, int ≥ 1), a construction's `reward` (`drift_shield`, `order_decay` with `amount`, `authority` with `amount` — never gold) and optional `teeth_fulfil`. Courts are checked against the roster, provinces against the map; `backend.modding.validator._validate_imperial_designs`. **Optional `acts`** (S14b part 3, `VP1_DESIGNS_SPEC.md` §5 — the Acts of the Empire, the road page's Decree rows): a list, each with `id`, `title`, `road` (`any` or a road id), `price` (gold, 1000..20000), `alarm` (0..5, source `acts_of_the_empire`), `effects` — a non-empty list from the closed set `authority`, `relation` (`courts`, or `pick: beaten` for the precondition's court), `client_loyalty` (`courts`; the owner's vassals among them), each with an `amount` 1..30 — never income, never war score — an optional `precondition` (`vassal` with `courts`; `great_power_beaten` with `courts` and `war_score`), optional `date`, `says` and `aliases`; `_validate_imperial_acts`. Each Act is decreed once (`state.acts`); a save whose store predates the list gains it at load. Absent = unarmed. **The shipped 1805 scenario carries the block** (S14b part 2, the Cabinet's road page); `tests/fixtures/vp1_imperial_designs_block.json` is the same block without its comments (pinned equal). |
| `moments` | object | absent | **S14c "Events and Historical Moments" (`EVENTS_SPEC.md` §2, §3, §5):** the authored letters of the record. `owner` (a nation), `pacing` {`max_open` 1, `min_gap` 2–5} and `deck` — each entry `id` (unique, never a law id), `kind` `letter`, `title` (≤ 40), `record` (≤ 240, past tense, "historically" where it names a date), EITHER a dated window `date` (ISO; checked against the turn by `calendar.turn_for_date`) + `turn` `{value, band: [lo, hi]}` (resolved per campaign seed; `historical` = `value`) OR a causal `lag` 1–3 (counted from its predicate's anchor), `grace` 1–3, `when` {`predicate`: `court_warm` | `vassal_slipping` | `design_fulfilled` | `law_bites`, its parameters}, `roads` (`any`, `none` or road ids), `voice` {`speaker`: `cabinet` | `talleyrand` | `envoy` (+ `nation`)}, `accept` / `decline` {`caption` (≤ 36), `ops`: [{`op`: `gold` | `dp` | `relation` | `alarm` | `loyalty` | `autonomy` | `enact_law`, …}]}. A decline is never priced (no gold, dp, autonomy or law); an alarm source starts `moment_`, is labelled on the Balance of Europe and is never a VP-1 source; windowed letters are spaced by the gap and close before the Verdict. Absent = unarmed; the shipped 1805 scenario authors the whole deck — the Bavarian Match, the Throne of Holland, the Crown of the Reich and the Decree of Berlin (S14c parts 2–3). The shipped deck is measured (`tools/_s14c_sweep_record.py` → `tools/_s14c_sweep_final.json`, which carries the deck's hash): an edit to it reds `tests/test_moments_pacing.py` until the sweep and the arms are re-run (S14c part 4). The staged deck: `tests/fixtures/moments_block.json`. |
| `war_scores` | object | {} | **S14D-X14 (measured October 24, 2026, on the Table board) — the stored pair score, and it is NOT cosmetic on turn 1.** `{"A\|B": int}`, each in [-100, 100]; pair keys alphabetically sorted, and the stored value is the FIRST court's view — France +86 against Austria is stored as `"Austria\|France": -86` (`get_war_score_for` flips the sign for the second court). Until the first end turn the stored figure is what EVERYTHING reads: the settlement table's per-court `direct_score` (`compute_direct_scores_by_enemy`), Talleyrand's suggested-terms sizing (`get_side_war_score_for`), and the bilateral verdict's war-score term (`war_score × bilateral_war_score_weight()`) with the military-supremacy / battlefield / pressure terms keyed to it. `acceptance_reads_the_field` swaps in the live figure only on a turn a battle of the pair moved it. The first end turn then REWRITES every WAR pair to the live `calculate_war_score` figure (`recalculate_war_scores`), so a scenario authors the figure its own board computes (its `battle_records`, `decisive_battles`, `campaign_ledgers`, the provinces held against `nation_starting_regions`, the capitals): the Table's `-86` is exactly the live value (territory -15, battles -15, decisive -15, capital -20, campaign -6, blood -15). A lone `war_scores` with no memory behind it reverts at the first end turn (63 → 10, probed). Unauthored = 0, and then a beaten court's table row reads 0 on turn 1. `tools/_table_board_probe.py` prints the stored and the live figure side by side. Only WAR pairs are recomputed; a war that ends pops its pair. The live components: territory (±5 per province of the other side's starting regions held, cap ±40), battles (cap ±15), decisive (cap ±15), capital (±20 held, ±10 besieged, cap ±30), campaign (cap ±10), blood (cap ±15), blockade (cap ±15), a captive sovereign (±15) and the ticking objective; total clamped ±100. |
| `war_exhaustion` | object | {} | **S14D-X14 — the war's weariness at the boot.** `{nation: int}`, each 0–200 (`coalition.WAR_EXHAUSTION_MAX`; outside it is a validation ERROR). Per NATION, not per pair. Absent = 0 for everyone. It feeds the settlement table's war-exhaustion component for the court that must accept, `min(20, we // 3)` (floor division — `settlement_scoring.calculate_war_exhaustion_component`), so Austria at 60 brings 20 points to her own row on turn 1. It is only the boot value of a figure that moves every end turn: +8 for each turn the nation is at war plus the named terms (+1 per own home province the enemy holds, +2 while the chest is under a turn of upkeep, a subsidy −2 to its recipient and +2 to its paymaster — `coalition.next_war_exhaustion`), held under a truce, −5 a turn at peace. |
| `war_start_turns` | object | {} | **S14D-X14** `{"A\|B": turn}` — the turn each pair's war began (an int; may be at or below 0 for a war begun before the scenario's turn 1). Pair keys sorted. A pair named in `starting_wars` but not here is stamped with `current_turn` (`setdefault` — an authored value wins). The war's age is `current_turn − start`, never negative, and the bilateral scorer (`diplomacy.calculate_acceptance`) reads it twice: the weariness term `min(20, 2 × turns at war)` added to any proposal made at war, and the war-age penalty on value-taking peaces and armistices (`war_age_acceptance_mod`: −65 at age 0, falling in a straight line to 0 at age 8; a white peace carries none). A start of `current_turn − 7` is age 8: weariness 16 and no penalty. The war panel's duration and the coalition members' break-ranks clause (the AI's long-war arm) read it too. |
| `battle_records` | object | {} | **S14D-X14** `{"A\|B": [record]}` — the pair's recorded battles. Each record: `turn` (int; at or below 0 for a battle before turn 1), `winner` (one of the pair — a third court's win scores for neither side), `attacker`, `defender`, `attacker_casualties`, `defender_casualties` (ints), `location` (a province) and optional `battle_name`. Live, only an engagement of at least 1,000 dead earns a row (`battle_scale.MIN_BATTLE_CASUALTIES`). The war score's battle component is net wins × 3 (`BATTLE_SCORE_PER_WIN`), DECAYED on quiet turns (from the third turn after the latest record, `(quiet − 2) × 2` points) and THEN capped at ±15 (`battle_score_from_records`). Records older than 10 turns are pruned on the end-turn pass (`apply_war_score_decay`), and a record dated the CURRENT turn makes the bilateral formula read the live score (`acceptance_reads_the_field`). The war panel's recent battles read them; they are cleared when the war ends. |
| `decisive_battles` | object | {} | **S14D-X14** `{"A\|B": [{"turn", "winner", "total_casualties", "ratio", "location"}]}`. Each win is worth 10 (`DECISIVE_SCORE_PER_WIN`), netted between the two sides, capped at ±15 (`DECISIVE_SCORE_CAP`) and NOT decayed. Live, a decisive is an exchange over 10,000 dead in which the winner bled the loser by more than 2:1 (`battle_scale.decisive_credit`) and the recorder keeps at most two per war; the loader enforces neither, so author honest rows (`total_casualties` and `ratio` are display). Give every row a `location`: a row without one whose twin battle record would not credit it is dropped at load (`drop_misbooked_decisives`). |
| `campaign_ledgers` | object | {} | **S14D-X14** `{"A\|B": {"captures": {nation: [provinces]}, "casualties": {nation: int}, "blockade_turns": {nation: int}}}` — the war's memory (`blockade_turns` optional, naval). `captures` lists every province a side has taken by force this war, each ONCE (a duplicate is a validation ERROR); `casualties` is each side's OWN dead; nation keys must be one of the pair, provinces known. They feed the war score: campaign 2 per capture, differenced between the sides and capped at ±10 (`CAMPAIGN_CAPTURE_SCORE`); blood = (the enemy's dead − one's own) / 2,500, truncated and capped at ±15 (`BLOOD_DIFF_DIVISOR`); blockade 1 per 2 turns of denial per side (cap 15 each). Berthier's cost note (own dead from 25,000) and Talleyrand's advisory line ("This war has taken N of our men and yielded M provinces") read the same ledger. It survives a truce and is dropped when the pair leaves the WAR/ARMISTICE family (a concluding peace, a forced alliance, an elimination). |
| `nation_starting_regions` | object | derived | **S14D-X14** `{nation: [province]}` — each nation's homeland. When absent (or empty) it is DERIVED from the loaded controllers — at a scenario start current control is starting control — which is wrong the moment `region_overrides` or authored `regions` hands a province to another nation: Vienna held by France would be listed as French soil and the war score's territory component (±5 per province of the OTHER side's list held, cap ±40) reads 0 for Austria's loss (measured: territory -15 with the key, 0 without; the pair score -86 → -71). **Author it whenever a scenario starts with conquered soil.** Every homeland read follows it: that component, the income pass's occupation cost (a province held outside the holder's own list pays it), campaign pay on foreign soil, and the AI's homeland defence and homeward retreat bias. Nations and provinces must be known. |
| `diplomatic_points` / `max_diplomatic_points` | integer | the world's own (5) / 5 | **S14D-X14** The PLAYER's diplomatic points: `diplomatic_points` is the pool turn 1 opens with, `max_diplomatic_points` the printed base ceiling (the HUD adds the Emperor's Seat and the carried points — `displayed_dp_ceiling`). Non-negative integers. Every end turn the pool is REFILLED to the court's regen plus up to one regen of unspent points, capped at `DP_BANK_CAP` (7) — `diplomacy._process_dp_regen` — so the authored figure governs turn 1 and the first carry only. |
| `nation_dp` | object | {} then seeded | **S14D-X14** `{nation: int}` — each AI court's DP purse (non-negative). It REPLACES the whole dict, and its PRESENCE skips `diplomacy.seed_boot_purses` (VP1-X13): absent, every AI court opens with the purse its regen writes (4 on the shipped courts) and can court, counter or renege on turn 1; present, a court it does not name opens with 0 until the first end turn's regen (`{}` is every court at 0). **Author every court or none.** |
| `ai_proposal_cooldowns` | object | {} | **S14D-X14** `{"<Nation>\|nation": turns}` — the nation-level anti-spam hold on a court's unsolicited letters to the player (`ai_diplomacy._is_on_cooldown`): while positive the court proposes nothing (the war-score-collapse and opportunism valves aside). Decremented once per end turn and removed at 0 (`CooldownManager.decrement_all`). The store also holds per-type, courting and AI-to-AI keys the engine writes at runtime; a scenario authors only the `<Nation>\|nation` form (anything else is a validation ERROR), values non-negative integers. A lesson board holds every court off the lesson: the Table authors 6 for each court but Austria. |
| `first_opens` | object | {} | **S14D-X14 (S14d, `TABLE_LESSON_SPEC.md` §3)** `{screen_id: turn}` — the first-open latches. A screen present in the store has shown its one-line "first open" and is latched; ids are those of `backend/game_logic/first_open.SCREENS` (`cabinet`, `designs`, `formables`, `settlement`, `separate_peace`, `laws`, `admiralty_camp`, `moment_letter`), an unknown id is a validation ERROR, and a value that is not an integer is dropped at load. The line shows while a screen is unlatched and on the stamped turn only (`first_open.line_for`), so a lesson whose own cards teach a screen pre-sets it to `0` (the Danube: `{"cabinet": 0, "laws": 0}`) and the line never prints. Absent or `{}` = every line unlatched. Display-only: no mechanic reads it. |
| `diplomatic_states` | object | {} | **S14D-X14** `{"A\|B": state}` — the pair standings at boot: `WAR`, `ARMISTICE`, `PEACE`, `OPEN_BORDERS`, `NON_AGGRESSION`, `DEFENSIVE_ALLIANCE`, `ALLIANCE`, `VASSAL` (`diplomacy.DIPLOMATIC_STATES`; anything else is a validation ERROR). Pair keys sorted — an unsorted key is unreachable at runtime, the `nation_relations` lesson. A pair not named reads `PEACE`. Wars are authored through `starting_wars` (the live war machinery), not here. |
| `coordination_tutorial_shown`, `opening_attack_guidance_shown`, `delegation_hint_shown`, `muster_hint_shown`, `commission_hint_shown` | boolean | false | **S14D-X14** The five one-shot engine hints, each a latch: the first combined-arms bonus (the coordination lesson), the opener guidance that holds the naive first attack long enough to surface the first-hour preparation line, the first delegation verb, the muster preview's standing-orders line, the first affordable commission. `true` pre-latches a hint so it never fires — the School of War lessons set all five (their cards carry the teaching). Booleans only (a validation ERROR otherwise). |

### Europe-map scenarios (1805 Loader pre-slice)

With `"sovereign_map": "europe"`:

- Omitting `regions` injects the validated 126-province Europe world (`create_europe_regions()`) — you do not inline 126 region dicts.
- Omitting `marshals` yields an **army-less** start (the legacy marshal roster is never injected — its locations don't exist on the Europe map).
- Omitted roster surfaces (`nation_gold`, `nation_actions`, `nation_authority`, `diplomats`, `manpower_pools`, `enemy_nations`, `vassals`) keep the Europe world's own construction-time values, including the 3 seeded French satellite vassals.
- `max_turns` defaults to **60** on the Europe world (legacy stays 40).
- Nation references validate against the 20-nation Europe roster (`EUROPE_NATION_CAPITALS` + the Europe diplomat cast).
- To boot the backend directly into a scenario, set the `SOVEREIGN_SCENARIO` environment variable to the file path — the import-time bootstrap and `/new_game` both load it via `WorldState.from_scenario` (missing/invalid files fail loudly).

### Nations in schema v1

When a scenario defines nation records, keep authored static taxonomy separate from runtime diplomatic state:

- `power_tier` is authored scenario data: `major`, `secondary`, or `minor`
- `political_status` is runtime state (`independent`, `vassal`, `protectorate`, etc.) and should not be hardcoded into the scenario taxonomy as a substitute for `power_tier`

---

## Marshal Format

Marshals represent commanders on the map.

### Minimal Marshal (Required Fields Only)

```json
{
    "name": "Murat",
    "location": "Lyon",
    "strength": 45000
}
```

### Full Marshal (All Fields)

```json
{
    "name": "Murat",
    "location": "Lyon",
    "strength": 45000,
    "personality": "aggressive",
    "nation": "France",
    "cavalry": true,
    "movement_range": 2,
    "tactical_skill": 7,
    "morale": 80,
    "stance": "neutral",
    "skills": {
        "tactical": 6,
        "shock": 9,
        "defense": 3,
        "logistics": 4,
        "administration": 3,
        "command": 7
    },
    "ability": {
        "name": "King of Naples",
        "description": "Charismatic cavalry leader"
    }
}
```

### Marshal Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | **REQUIRED** | Marshal's name. **Do not name a marshal after a province** (WO-13, Sept 1, 2026): the resolution seams fuzzy-match a query onto a marshal, so a marshal within a typed mistake of a province name silently answers when that province is named, and an *identically* named one is unreachable by any gate. The validator WARNS on both (never errors — `europe_1805.json` ships exactly one, `Brunswick`, and must keep booting). For an identical name the **positional rule** decides: **the name means the MAN wherever a man can be meant** — addressing him (`"Brunswick, hold"`) is refused as a foreign commander, attacking him (`"attack Brunswick"`) targets him — and the **PROVINCE is reached by the region-only verb** `move to <name>`, which can mean nothing else. (An earlier version of this row said the addressee is the province. That was false in both halves: there is no province-addressee route, and the rule as written was letting the player command a foreign marshal.) |
| `location` | string | **REQUIRED** | Region name where marshal starts |
| `strength` | integer | **REQUIRED** | Number of troops (e.g., 50000) |
| `personality` | string | "balanced" | One of: `aggressive`, `cautious`, `literal` — the ONLY valid authoring values (MC-4, July 10, 2026: `balanced`/`loyal` are retired reserved values, a hard validation ERROR — a scenario authoring one cannot boot). Omitting the field falls back to the inert save-compat default `"balanced"` (no objection triggers ever fire) and logs a boot warning — author the field explicitly. |
| `nation` | string | "France" | Nation this marshal belongs to |
| `cavalry` | boolean | false | If true, has cavalry movement/abilities |
| `artillery` | boolean | false | If true, an artillery marshal — bombardment, +damage, fort degradation; cannot melee-attack. Mutually exclusive with `cavalry`. A commissioned artillery candidate raises its corps (`RECRUIT_ARTILLERY_CORPS`, 3,000) from the nation's `artillery` manpower pool, not infantry. See `docs/ARTILLERY_GAP_SPEC.md`. |
| `movement_range` | integer | 1 | Regions can move per turn (cavalry often 2) |
| `tactical_skill` | integer | 5 | Overall tactical rating (1-10) |
| `morale` | integer | 70 | Starting morale (0-100) |
| `stance` | string | "neutral" | One of: `neutral`, `defensive`, `aggressive` |
| `skills` | object | null | Individual skill ratings |
| `ability` | object | null | Special ability |
| `trust` | object | `{"value": 70}` | Starting trust in the player, `{"value": 0-100}` (MC-2: the shipped 1805 roster authors this per marshal) |
| `relationships` | object | `{}` | Starting relationships with other marshals by name, `{"Name": -2..2}`. −2 Hostile (coordination ×0.0, refuses unordered reinforcement) · −1 Rival (×0.5) · +1 Friendly (×1.25) · +2 Devoted (×1.5); also ±10/step on the reinforcement arrival score. Values outside −2..+2 are a validation ERROR (loaded raw, never clamped); a target not in the roster is a validation warning (the edge is never read). Author both directions if you want a symmetric pair — marshals load independently (MC-3: the shipped 1805 roster authors 13 symmetric pairs) |

### Personality Types

| Personality | Behavior |
|-------------|----------|
| `aggressive` | Prefers attacking, objects to defensive orders |
| `cautious` | Prefers defense, objects to risky attacks |
| `literal` | Follows orders exactly, never objects (the Literal Doctrine) |

`balanced` and `loyal` are RETIRED reserved values (MC-4, July 10, 2026) — no shipped marshal uses them, they carry no objection triggers or combat modifiers, and the validator rejects them. They survive only as save-load fallbacks.

### Skills Object

```json
{
    "tactical": 7,       // General tactics
    "shock": 9,          // Offensive power
    "defense": 4,        // Defensive ability
    "logistics": 5,      // Supply management
    "administration": 4, // Administrative skill
    "command": 8         // Leadership
}
```

All skills range from 1-10. If not specified, defaults are applied.

Wired seams (what a point buys): `tactical` — combat dice (+1 per 3 pts);
`shock` — attack damage (+5%/pt); `defense` — damage resistance (−5%/pt);
`logistics` — reinforcement muster score (+5/pt); `command` — The Rally
(recovery 2 stages/turn at 8+, retreat penalties 10pp deeper at 3−).
`administration` is accepted and serialized but currently UNWIRED (reserved
for the MC-2b slice) — the marshal card hides it until its mechanic lands.

### Ability Object

```json
{
    "name": "Cavalry Charge",
    "description": "Can attack 2 regions away"
}
```

Abilities are currently informational. Future versions may add mechanical effects.

---

## Region Format

Regions represent territories on the map.

### Minimal Region (Required Fields Only)

```json
{
    "name": "Tuscany",
    "adjacent_regions": ["Milan", "Rome", "Venice"]
}
```

### Full Region (All Fields)

```json
{
    "name": "Paris",
    "adjacent_regions": ["Belgium", "Lyon", "Brittany"],
    "income_value": 300,
    "is_capital": true,
    "terrain": "urban",
    "region_type": "capital",
    "controller": "France",
    "garrison_strength": 5000,
    "stability": 100,
    "war_damage": 0.0
}
```

### Region Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | **REQUIRED** | Region's name |
| `adjacent_regions` | array | **REQUIRED** | List of connected region names |
| `income_value` | integer | 100 | Gold per turn when controlled |
| `is_capital` | boolean | false | If true, losing this loses the game |
| `terrain` | string | "plains" | Terrain type (see below). Affects defense, movement cost, cavalry, supply |
| `region_type` | string | "town" | Region type (see below). Determines income. Valid: capital, major_city, city, town, rural |
| `controller` | string | null | Nation that controls this region |
| `garrison_strength` | integer | 0 | Troops defending (not marshal) |
| `stability` | integer | 100 | Region stability (0-100). Affects income via tiers: 0-25=Hostile (0%), 26-50=Unrest (25%), 51-75=Settling (75%), 76-100=Stable (100%). Set to 25 on capture. |
| `war_damage` | float | 0.0 | War damage (0.0-0.5). Reduces income multiplicatively. Applied by battles, recovers -0.02/turn. |
| `plundered` | boolean | false | True if region was plundered on capture. Clears when stability > 50. |
| `buildings` | array | [] | Built buildings: `[{"type": "supply_depot", "damaged": false}]`. Types: supply_depot, fortification, training_ground. |
| `building_under_construction` | object\|null | null | Active construction project: `{"type": "supply_depot", "turns_remaining": 2}`. |

### Terrain Types

The `terrain` field controls combat bonuses, pathfinding costs, and cavalry effectiveness. Valid values:

| Terrain | Defense Bonus | Movement Cost | Cavalry Eff. | Charge Blocked |
|---------|-------------|---------------|-------------|----------------|
| `plains` | +0% | 1.0x | 1.2x | No |
| `forest` | +10% | 1.3x | 0.5x | Yes |
| `hills` | +15% | 1.2x | 0.8x | No |
| `mountains` | +25% | 2.0x | 0.3x | Yes |
| `urban` | +20% | 1.0x | 0.5x | Yes |
| `river_crossing` | +15% | 1.5x | 0.6x | No |

- **Defense Bonus**: Defender gets this bonus in combat
- **Movement Cost**: Dijkstra weight for MOVE_TO pathfinding (higher = costlier to enter)
- **Cavalry Eff.**: Multiplier on cavalry combat bonuses (lower = weaker cavalry)
- **Charge Blocked**: If yes, Glorious Charge (recklessness 3+) downgrades to normal attack

The `terrain` field is separate from `region_type`. Terrain affects combat/movement; region type affects income. Both default if omitted (`terrain` → "plains", `region_type` → "town").

### Region Types

The `region_type` field determines base income:

| Region Type | Income | Description |
|-------------|--------|-------------|
| `capital` | 300 | National capital |
| `major_city` | 200 | Large strategic city |
| `city` | 150 | Medium city |
| `town` | 100 | Small settlement (default) |
| `rural` | 50 | Countryside/village |

### Adjacency Rules

**Important:** Adjacency should be bidirectional. If Paris lists Belgium as adjacent, Belgium should list Paris as adjacent.

```json
{
    "regions": {
        "Paris": {
            "name": "Paris",
            "adjacent_regions": ["Belgium"]
        },
        "Belgium": {
            "name": "Belgium",
            "adjacent_regions": ["Paris"]
        }
    }
}
```

The validator will warn if adjacency is not bidirectional.

---

## Complete Example: Custom Scenario

```json
{
    "scenario_name": "Battle of Waterloo",
    "player_nation": "France",
    "current_turn": 1,
    "max_turns": 10,
    "gold": 500,

    "regions": {
        "Waterloo": {
            "name": "Waterloo",
            "adjacent_regions": ["Brussels", "Charleroi"],
            "controller": "Britain"
        },
        "Brussels": {
            "name": "Brussels",
            "adjacent_regions": ["Waterloo"],
            "income_value": 150,
            "is_capital": true,
            "controller": "Britain"
        },
        "Charleroi": {
            "name": "Charleroi",
            "adjacent_regions": ["Waterloo", "Paris"],
            "controller": "France"
        },
        "Paris": {
            "name": "Paris",
            "adjacent_regions": ["Charleroi"],
            "income_value": 200,
            "is_capital": true,
            "controller": "France"
        }
    },

    "marshals": {
        "Napoleon": {
            "name": "Napoleon",
            "location": "Charleroi",
            "strength": 73000,
            "personality": "aggressive",
            "nation": "France"
        },
        "Wellington": {
            "name": "Wellington",
            "location": "Waterloo",
            "strength": 68000,
            "personality": "cautious",
            "nation": "Britain"
        }
    }
}
```

---

## Tips for Modders

### 1. Start Minimal

Begin with the smallest possible scenario and add complexity gradually:

```json
{
    "player_nation": "France",
    "gold": 5000
}
```

### 2. Use the Validator

Always validate your JSON before testing in-game:

```bash
python -m backend.modding.validator your_scenario.json
```

### 3. Marshal Locations Must Match Regions

If you define custom regions, ensure all marshal locations exist:

```json
{
    "regions": {
        "CustomCity": { ... }
    },
    "marshals": {
        "MyMarshal": {
            "location": "CustomCity",  // Must exist in regions!
            ...
        }
    }
}
```

### 4. Bidirectional Adjacency

Always make adjacency go both ways:

```json
{
    "regions": {
        "A": { "adjacent_regions": ["B"] },
        "B": { "adjacent_regions": ["A"] }  // Don't forget!
    }
}
```

### 5. Default Map + Custom Marshals

You can use the default map but with custom marshals:

```json
{
    "player_nation": "France",
    "marshals": {
        "Napoleon": {
            "name": "Napoleon",
            "location": "Paris",
            "strength": 100000
        }
    }
}
```

The default regions will be loaded automatically.

### 6. Custom Nations

You can use any nation names - they don't have to be historical:

```json
{
    "player_nation": "Gondor",
    "enemy_nations": ["Mordor"],
    "marshals": {
        "Aragorn": {
            "nation": "Gondor",
            ...
        },
        "Sauron": {
            "nation": "Mordor",
            ...
        }
    }
}
```

---

## Example Files

See the `mods/examples/` directory for complete examples:

- `minimal_scenario.json` - Simplest possible scenario
- `custom_marshal.json` - How to define a marshal
- `custom_region.json` - How to define a region
- `battle_of_waterloo.json` - Full historical scenario
- `custom_nations_scenario.json` - Custom nations example

---

## Troubleshooting

### "Required field is missing"

Check that your marshals have `name`, `location`, and `strength`.
Check that your regions have `name` and `adjacent_regions`.

### "Marshal location X is not a defined region"

Either:
1. Add the region to your `regions` object
2. Remove your custom `regions` to use the default map
3. Change the marshal's location to an existing region

### "References non-existent region"

A region's `adjacent_regions` lists a region that doesn't exist. Add the missing region or fix the typo.

### "non-bidirectional adjacency"

Region A says it's adjacent to B, but B doesn't say it's adjacent to A. Add the missing adjacency to region B.

---

## Version Compatibility

Scenario files are forward-compatible. Fields added in future versions will be ignored by older game versions. However, older scenarios may not have access to newer features.

Current format version: **1.1**
