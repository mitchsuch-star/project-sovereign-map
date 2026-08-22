# WEIRD OUTCOMES — Row WO Build Contract ("The Instrument First")

**v1.0 · authored August 21, 2026 · Status: BUILD-READY.**

**Authority chain.** The gate record is `docs/audits/WO_EVAL_2026_08_17.md` §6 —
authoritative for the three RULINGS (G1/G2/G3), which this spec carries but does
not re-open. **This spec is authoritative for the BUILD**: slice scope, seams,
acceptance, pins, and order. Where this spec's §2 verification record corrects a
line number or a claim in the eval memo, **this spec wins** (the memo carries a
header pointer). The evidence memo is
`docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md`, read WITH the eval's §8
kill list. Correctness rows = `docs/BUG_FIXES.md` §Weird-Outcomes Playtest
(WO-1..WO-16, WO-H1..H3); design rows = `docs/DESIGN_REFINEMENT.md`
§Weird-Outcomes (WO-D1..D7).

**Verification method for this spec (August 21, 2026).** Every seam cited in a
slice contract was re-verified against master `bd0be0c` by a six-agent
read-only pass (four claim-verification agents + two fresh defect hunts) plus
direct hand checks by the session author. §2 is the verification record; §4
carries the new findings the hunt returned. Where the eval memo's citation
drifted or omitted something load-bearing, the §2 row says so.

**Reading map.** §1 the gate rulings, carried · §2 the verification record ·
§3 the seventeen slices (build contracts — the eval's twelve, verified and
hardened, plus five born from this session's defect hunt: 13 the Trojan
Corridor · 14 the clock and the flag · 15 the capture question · 16 the
objection channel · 17 the frontier halt) · §4 new findings + routing · §5
order and the row's definition of done · §6 never-do.

---

## §1 The gate record, carried (G1 / G2 / G3)

Held and answered August 17, 2026 (memo §6, authoritative). Restated here so a
builder never needs the memo open to know what is ruled:

- **G1 — the typed diplomatic verbs are RETIRED as a player surface.** User
  ruling, verbatim: *"the diplo screen should be only path for these actions
  typing commands should just have it tell them to go to the diplo room or
  something thematic."* Not priced, not routed — redirected in character.
  **Buildability constraint (load-bearing, found after the ruling):** the
  diplomacy wizard itself executes by sending typed commands through
  `api_client.send_command` with no marker, so the redirect must land on the
  **terminal input path in `main.gd` only**, never as a backend refusal.
  Verified at `bd0be0c` (§2 rows G1-1..G1-4): the terminal choke point is
  `_execute_command()` (`main.gd:1298`), whose only callers are the send
  button (`:832`) and `_on_command_submitted` (`:836`); every chip pipeline
  (wizard, Vassals tab, region panel, reward/commission, war-detail
  request-terms at `main.gd:5295-5311`) sends via `api_client.send_command` /
  `send_structured_command` directly and is structurally unaffected. Slice 7
  builds this. **This ruling absorbs WO-4 and most of WO-5** (slice 11 shrinks
  to the non-diplomatic residue).
- **G2 — neither wealth arm now.** No economic term in `power_score`, no
  town-slot raise. WO-D4's written requirement list goes to the Victory pass
  (ROADMAP 12–13). **Re-open condition, written:**
  `BUILDING_SLOT_LIMITS["town"] = 1` is the shelf-held cheap first purchase
  **if slice 1b's re-measured funnel still shows the non-military arms
  collapsing** (the 1b protocol in §3 defines "still shows").
- **G3 — every corps in the battle province fights, BY DESIGN, and the game
  says so.** The muster preview states it; the free exclusion is taught for
  *adjacent* corps only (1 AP, permanent). WO-D1 Option 3 ("Name the March")
  is CLOSED BY RULING; CA9-D2's verbatim popup ruling is not re-opened. The
  honest sentence lands in slice 8.

**Recorded residual on G1 (honest, and part of this contract):** the redirect
closes the +37,000-man turn-1 vassalize opening *as a typed player surface*.
It does NOT close it (a) over raw HTTP, (b) in the playtest driver — which
must keep executing typed diplomacy or every unattended evaluation loses the
domain (eval §7.12) — or (c) **for live-parser synonym phrasings the client
list cannot anticipate** (a live LLM can resolve "subjugate the Bavarians" to
`make_vassal`; the client intercepts verb heads, not intents). (c) is this
spec's addition to the record. Full closure of the free-executor price is the
original G1(a) — *route the typed verb through the priced proposal path* —
which layers on top independently if the user later wants it. Do not build it
uninvited.

---

## §2 The verification record — every cited seam at master `bd0be0c`

Legend: ✅ = confirmed at the cited line · Δ = confirmed, line drifted (current
line given) · ⚠ = confirmed with a material addition the eval omitted ·
✚ = new fact established by this pass.

**The five MATERIAL corrections to the eval memo (everything else is line
drift):**
1. **WO-1's seam** — the recognise-and-strip is `parser.py:688-702` +
   `:1575-1576`; the eval's `executor.py:1794-1805` is only the routing hop
   (H-8). Slice 2 is contracted on the real seam.
2. **WO-5's attribution** — bare `sue for peace`/`make peace` hit the honest
   FINAL-21 target ask (`llm_client.py:2041`), NOT the declare-war
   clarification; the declare-war ask is reached because *"end the war ON
   any terms"* contains the war keyword `"war on "` (H-15). The BUG row's
   story is corrected accordingly.
3. **`sovereign_captured: 101`** sits above `home_captured: 100` (NP-4) and
   the eval's WO-D6 ordering reasoning never mentions it (D-5); slice 4's
   ordering pin includes it.
4. The **WE settlement formula's executable line** is
   `settlement_scoring.py:1518` (`:1467` is its docstring), and the
   stalemate-patience "saturates at 150" holds only for bonus-0
   personalities at the floor-2 boundary from WE 90 (D-4).
5. **WO-H3's wording** — the driver DOES answer a bare-`True` capture prompt;
   what it loses is the sibling `capture_data` (stage / `dialogue_id` /
   detail), which is what makes the ESTATE stage unanswerable (H-14).

### Combat / muster / garrison (slices 3, 8)

| id | seam | verdict |
|---|---|---|
| C-1 | `_build_muster_preview` `combat_executor.py:959` (body 959–1188); rows `:976`/`:1077`, odds band `:1095-1098`, presence `:1176`, hint `:1184`; **no supply term anywhere in the function** | ✅ |
| C-2 | `get_effective_supply_cap` `world_state.py:6146`; `ALLY_SUPPLY_STATES` `:6139`, `HOME_SUPPLY_MULTIPLIER = 1.5` `:6141`, allied-soil arm `:6162-6167` | ✅ |
| C-3 | attacker casualty base = LEAD corps' own strength: `combat.py:268-272`; whole-muster credit in `_calculate_effective_strength` `combat.py:1095`, decisive line **`:1125`** (`effective += max(0.0, committed)`) — eval cited `:1126`, which is the `return` | Δ |
| C-4 | `_get_casualty_participants` `combat_executor.py:1717`, filter `:1736-1745`: region/nation/strength/broken/retreated — **no `fortified` / `holding_position` arm**. One precision caveat: a rel −2 hostile pair without an active SUPPORT order IS excluded (`:1748-1757`); no order-type filter exists otherwise | ⚠ |
| C-5 | reinforcements both sides: `combat_executor.py:5000-5002` / `:5003-5005` (committed defender = CA9-F1, shipped) | ✅ |
| C-6 | WO-3: garrison loss floor `int(garrison × 0.10)` `combat_executor.py:2697` (attacker 2% floor `:2696`); detachment collapse `<= 0` `:2714-2715` (non-detachment `< 5000` `:2717`); damage ratio cap 0.50 `:2690`; P4.25 no futility guard `enemy_ai.py:3483-3546` (never reads `ai_attack_futility`); futility tracker reads `type == "battle"` `enemy_ai.py:1220` while a garrison hold emits `"garrison_assault"` (`combat_executor.py:2879-2880`) | ✅ |
| C-7 | raw-vs-effective supply split: `ledger.py:187` (verdict) + `:202` (figure) raw; map summary `world_state.py:8361` raw; render `region_panel.gd:195-197` (`Supply:` prints at `:197`; `-1` → "Unknown" branch `:196`); `get_filtered_game_state_summary` `world_state.py:8425` with the **PC15-16 `-1` fog sentinel at `:8494-8499`** — every surface ships RAW `supply_capacity`, none ships the effective cap | ✅ |
| C-8 | muster preview is player-gated: `combat_executor.py:4808-4811` (`_strategic_execution` / `_autonomous_execution` / player-nation guard); `_build_muster_preview` has exactly ONE call site (`:4812`) → preview changes are structurally unable to move `BASELINE_SERIES` | ✅ |
| C-9 | `GARRISON_DETACHMENT_SIZE = 3000` `economy_executor.py:95` (mirror `executor.py:162`), placed `:958-959` | ✅ |

### Peace / counsel / dispatch / gazette (slices 4, 5, 12)

| id | seam | verdict |
|---|---|---|
| D-1 | advisory rung 1: gate STRICT `war_score < 0` at `diplomatic_advisory.py:184`; kind `request_terms` `:191`; copy `:196-198` verbatim | ✅ |
| D-2 | `generate_advisory` has exactly ONE production caller — `diplomatic_executor.py:824` inside `_execute_diplomatic_advisory` (`:809`), action-dispatched at `:95-96`; reached by the W6-9 assessment verb and question-form diplomatic commands (`llm_client.py:2050-2051`, `:2103-2108`); **no caller on the turn path** | ✅ |
| D-3 | exhausted-pair predicate: `_process_exhausted_pair_exits` `settlement_third_party.py:425`, condition `:453-462`; constants `PAIR_EXIT_WE_FLOOR = 120` (`:48`), `PAIR_EXIT_MIN_TURNS = 10` (`:49`), `PAIR_EXIT_STAGNANT_SCORE = 15` (`:50`); `PAIR_EXIT_TRUCE_FLOOR_TURNS = 8` (`:62`) | ✅ |
| D-4 | WE settlement component: executable formula at `settlement_scoring.py:1518` (`min(20, we // 3)` via `WAR_EXHAUSTION_DIVISOR` `:528` / `WAR_EXHAUSTION_CLAMP` `:529`) — eval's `:1467` is the DOCSTRING; scores the ACCEPTING leader (`:1486`). Coalition loyalty penalty neutralizes at WE 150 (`coalition.py:1414`, base −15 `:65`). Stalemate patience `ai_diplomacy.py:1361`: the `we//30` term cancels the base at 150, but the floor of 2 is already reached at WE 90 for bonus-0 personalities | Δ |
| D-5 | `HEADLINE_WEIGHTS` `dispatch.py:57+`: **`sovereign_captured` 101 (`:61`, NP-4)** · `home_captured` 100 (`:62`) · `marshal_destroyed` 96 · `marshal_captured` 95 · `enemy_eliminated` 93 · `capital_stormed` 92 · `own_broken` 90 · `enemy_marshal_destroyed` 89 · `enemy_marshal_captured` 88 · `own_mauled` 85 · `victory_won` 73 · `region_taken` 68. **The eval's D6 reasoning never mentions `sovereign_captured` 101** — slice 4's ordering pin must include it | ⚠ |
| D-6 | direction-blind `home_captured`: `dispatch.py:428-435` — `:432` tests only the captor; sibling `:435` correctly keys on `captured_from` | ✅ |
| D-7 | `own_mauled`: proportional predicate, no absolute floor `dispatch.py:665-666`; template prints the absolute figure `:255` | ✅ |
| D-8 | sub-beat machinery: stable sort `:996` (equal-weight order = event-log insertion order); dedupe on `(class, identity)` `:1122-1128`; budget 1 + 2 `:1130-1131` | ✅ |
| D-9 | gazette capital predicate direction-blind: `gazette.py:94-104` (`world.get_nation_capital(prev) == region` at `:103`, no captor test) → Paris's fall captions "a capital stormed" | ✅ |
| D-10 | CA8-5 pins that must stay green through slice 4: `tests/test_creative_audit_ca8_2026_08_04.py::TestCA85DispatchStutter::test_two_different_marshals_still_get_two_beats` (`:263`, the falsifiable negative), `test_three_battles_by_one_marshal_take_one_slot` (`:253`), `TestCA89::test_another_marshals_break_is_not_absorbed` (`:859`) | ✅ |
| D-11 | WO-15 "(dead)": `world_state.py:4907-4908` in `find_nearest_marshal_to_region`, rendered into the recruit refusal via `economy_executor.py:61-65` (call sites `:468`/`:487`) | ✅ |
| D-12 | WO-12 mislabel: `world_state.py:6232-6237` (under-capacity stacking arm), message `:6257-6260`; second surface `dispatch.py:1587-1588` (cause-blind collector `:1592-1604`) | ✅ |
| D-13 | WO-9: `main.py:1734` carve-out keys `captured_from`; both conquest producers omit it — `combat_executor.py:2805-2810` (`old_controller` live at `:2803`) and `:4697-4702` (`:4693`) | ✅ |
| D-14 | WO-10: ratio sentence `dispatch.py:2151-2156`, estimator `:2226` (docstring `:2230-2232`); `diplomatic_ledger.py:175-204` `_format_army_strength` has **no LAST_KNOWN arm** while `LAST_KNOWN` is a real tier (`models/intel.py:26`) → exact-aggregate fall-through at `:203-204` | ✅ |
| D-15 | headline classes are display vocabulary, not event types: `CAMPAIGN_LOG_TYPES` (`campaign_log.py:94`) contains `region_captured`, never `home_captured`/`capital_stormed` → slice 4 moves **zero** log-type pins | ✅ |

### G1 / wizard / vassal (slice 7)

| id | seam | verdict |
|---|---|---|
| G1-1 | terminal choke point: `command_input.text_submitted` → `_on_command_submitted` (`main.gd:834-836`) → `_execute_command()` (`:1298`); only other caller `:832` (send button). Both are player-typed-text paths | ✅ ✚ |
| G1-2 | chip pipelines bypass by construction: `_on_reward_command` (`main.gd:4973-4983`), `_on_vassal_command` (`:5016-5026`), war-detail request-terms (`:5295-5311`, `send_structured_command`), all behind the shared `_chip_command_in_flight` latch (`:5002`) — none calls `_execute_command()` | ✅ ✚ |
| G1-3 | boot states: `France\|Spain` and `Bavaria\|France` are `ALLIANCE` in `europe_1805.json` (diplomatic_states block) — the missing ALLIANCE-branch `propose_vassal` row really does exclude the two flagship courts | ✅ ✚ |
| G1-4 | `executor.py:711` free-actions list contains `make_vassal` (0 military AP; the R72 comment *"they cost DP/gold, not military AP"* is FALSE for this verb — the executor path charges neither) — plus `invest_vassal`, `change_autonomy`, `release_vassal`, `grant_region_to_vassal`, `request_terms`, `sponsor_design`, `buy_off_design`, `guarantee_nation`, `propose_common_peace`, `propose_white_peace` (each of those prices in its own executor; `make_vassal` is the one that doesn't) | ✅ |
| G1-5 | `diplomacy.py` `_proposal_action("propose_vassal", …, "VASSAL")` emitted at `:11001` (OPEN_BORDERS), `:11025` (NON_AGGRESSION), `:11049` (DEFENSIVE_ALLIANCE); **absent from the `elif state == "ALLIANCE"` branch at `:11072-11092`**; `_proposal_action` (`:10718-10805`) consults cooldowns/armistice/relations/power-cap/DP but **never `VASSAL_MIN_STATES`** | ✅ |
| G1-6 | **`VASSAL_MIN_STATES` already EXISTS** at `diplomacy.py:127` — `{"WAR", "OPEN_BORDERS", "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE"}` (**includes ALLIANCE**) — and is enforced at the acceptance seam (`diplomacy.py:2922`, `vassal.py:132-133`). The eval's "add a guard" is really "make the wizard emitter consult the existing single source" | ⚠ ✚ |
| G1-7 | `invest_in_vassal` `vassal.py:1076`: validates existence/lordship/cooldown/gold/DP, **no loyalty ceiling**; charges then clamps — `:1135-1138` `gain = int(INVEST_LOYALTY_GAIN * mult)` … `min(LOYALTY_MAX, …)`; message `:1148-1149` still claims *"+10 loyalty (100 → 100)"*. Costs `INVEST_DP_COST = 1`, `INVEST_GOLD_COST = 200` (`:44-45`) | ✅ |
| G1-8 | the help block is `meta_executor.py:652-662` — and the eval's "seven verbs" UNDERCOUNTS: it also teaches *break treaty* and *ultimatum* (`:659`), and `:656-657` promises a **"trade" proposal that does not exist** (not in `PROPOSAL_TYPE_KEYWORDS`, not a wizard action) — a stale promise the rewrite must not preserve | ⚠ ✚ |
| G1-9 | the insertion point inside `_execute_command()` must sit BELOW the redemption typed-token block (`main.gd:1333-1340` — exact tokens `grant_autonomy`/`dismiss`/`demand_obedience` go to `send_redemption_response`, never `send_command`); a loose "grant…autonomy" family pattern placed above it would eat the redemption answer | ✚ |
| G1-10 | dialogue-answer vocabulary (`dialogue_routing.py:38-114` + option labels/ids) contains **no verb+nation sentences** — an interception scoped to sentence-shaped diplomatic orders cannot eat a typed dialogue answer; the server consumes clarification/objection/interrupt answers BEFORE the parse (`main.py:2092-2239`) and dialogue answers before execution (`:2523-2545`) | ✅ ✚ |
| G1-11 | wizard coverage census (`diplomacy_wizard.gd _build_command :739-809`): declare_war ✓ ultimatum ✓ break_treaty ✓ downgrade ✓ peace/armistice ✓ alliance-family ✓ propose_vassal ✓ open_settlement ✓ white_peace ✓ missions ✓ invest/autonomy/release ✓ cede ✓ sponsor/buy-off/guarantee ✓ — **but `request_terms`, `make_amends`, `set_war_purpose`, `repudiate_bargain` have NO wizard case** (request_terms has the war-detail chip; the other three have no UI home at all) | ⚠ ✚ |
| G1-12 | tutorial suggest chips: all 15 steps enumerated (`tutorial_overlay.gd` step table; `tutorial_1805.json` is scenario-only) — **zero diplomatic suggests**; step XIV already teaches "F1 opens the diplomacy wizard" | ✅ |
| G1-13 | producers whose emitted command is diplomatic AND travels the terminal path: **NONE** — every diplomatic UI producer (wizard rows, VASSALS-tab chips, Assess chip, war-detail Settlement/Request-Terms incl. the `must_reopen` machine reissue at `main.gd:1942`, proposal-confirm fallback `:4515-4542`) sends via api_client directly; the region-panel/war-panel "Negotiate" chips send NOTHING (they open the wizard) | ✅ ✚ |

### Parser / executor / harness (slices 1, 2, 10, 11)

| id | seam | verdict |
|---|---|---|
| H-1 | driver RNG: `grep -c random tools/playtest_driver.py` = **0**; `random.seed` in `backend/` = **0**; **20** backend modules import `random`; **zero `random.Random()` instances in `backend/`** (only a benchmark tool) → per-turn module-level seeding is sufficient, no instance plumbing needed | ✅ ✚ |
| H-2 | `.gitignore:89` ignores `tools/playtest_runs/` | ✅ |
| H-3 | golden corpus = **333 entries** (+2 `live_phrasing_backlog`) in `tests/data/parser_golden_corpus.json` | ✅ |
| H-4 | driver `meta.json` already records seed/mode/args (`playtest_driver.py:269`, `:284`); `SOVEREIGN_SEED` set at `:231` | ✅ ✚ |
| H-5 | an ambient RNG draw inside the courting tick (`vassal.py:2030-2031`, 60% dispatch detection) — a concrete producer of the measured run-to-run divergence | ✅ ✚ |
| H-6 | WO-8 loop: head `vassal.py:1976`, per-COURTIER cooldown `court\|{nation}\|{vassal}` `:1983` (3 turns), per-nation `break` `:2039`, 2 DP `:1990-1993`, reduction 5/15 × grip scale `:1998-1999`; **no per-TARGET throttle, no `nation == vassal_name` guard, no fellow-vassal guard** — the self-court and the 19-court pile-on are both visible in the loop head | ✅ ✚ |
| H-7 | WO-14 producer 1: `naval_executor.py:107-115` — "currently:" = at-war courts with any fleet record, never intersected with `blockaded_nations()`; the "their crews rot at anchor while ours drill" line. Producer 2 at `naval.py:1885-1899` (eval said 1886-1898 — Δ1). The real pin set: `blockaded_nations` applied at `naval.py:1273-1280` (def `:377-387`) | Δ |
| H-8 | **WO-1's real seam is NOT the eval's `executor.py:1794-1805`** — that is only the routing hop (`general_retreat` → `_execute_general_retreat` at `:1802-1803`). The recognise-and-strip happens at **`parser.py:688-702`**: an extracted "marshal" that IS a known enemy is demoted to a target (`llm_result["marshal"] = None` at `:700`, target backfill `:701-702`), then `_classify_command` (`:1560-1576`) reads `marshal is None` + `retreat` → `general_retreat` (`:1575-1576`), which never reads the demoted name. `Kutuzov, scout Swabia` → Soult via the same strip + auto-assign sibling. Roster confirmed: Mack/Kutuzov/Buxhowden/Moore all enemy-roster in `europe_1805.json` | ⚠ ✚ |
| H-9 | WO-2 parser arms: the two ungated `auto_correct` arms at `parser.py:983-986` exactly; `_plausible_name_typo` at `:349` (first-letter match `:361`, edit distance ≤2/1 `:363-364`); **the gate has FOUR sibling application sites, not three** (`parser.py:1098`, `:1413`, `strategic_executor.py:136`, `:178`); ungated strategic-marshal arm `:1421-1422`; the region match is COMPUTED at `:968-971` and APPLIED at `:985-986` | ⚠ |
| H-10 | WO-2 executor backstop: `executor.py:299-304` inside `_fuzzy_match_region` (def `:253`) — ungated `auto_correct` over ALL regions (`:290`); "Morocco" is a real registry region, so `move to the Moon` has a live wrong target | ✅ |
| H-11 | WO-13: `executor.py:432-441` (`_fuzzy_match_enemy`, def `:381`, ungated arm `:435-441`); absorber `_broad_fuzzy_diplomatic_check` `:364-371` over ALL non-allied marshals; fifth seam `:230-235` over ALL marshals (`:221`); reach path `combat_executor.py:4224-4249` is ENEMY-FIRST (region only tried after the enemy match fails). `Brunswick` = marshal (Prussia, `europe_1805.json`) AND live registry province — exact collision on both ladders, uncloseable by a typo gate | ✅ |
| H-12 | WO-6: `llm_client.py:1313-1315` — bare `"wait"`/`"stand by"` substring (plus a guarded `\bpass\b`); branches BELOW it in the same chain: hold `:1321`, defend `:1330`, retreat `:1335`, move `:1342`, scout `:1381`, build `:1447`, restrain `:1450`, drill `:1452` | ✅ |
| H-13 | WO-7: the dialogue wall opens at `main.py:2523`; soft-stop pass-through `:2591-2593`; the `else:` at `:2594`; the three recovery arms inside it — CR-2 `:2660`, PARSE-NEG `:2685`, Berthier `:2749`. The clarification pop is `main.py:2098` (eval said `:2097`) and is **unconditional before the `resolution["kind"]` check** — `{"kind": "pass"}` destroys the pending clarification (reachable by driver/raw HTTP; the client holds a modal over it) | Δ ⚠ |
| H-14 | driver: `_option_id` `:449-452` reads `id`/`choice`/`keyword` (an `action`-only option → None); fallback literal "confirm" `:120` + `:659-660`; blind chain `:726-730`; battles `:519-520` top-level only while autonomous attacks ship on `jealousy_attacks` (`turn_manager.py:405-415`) — 0 driver reads; `"state"` 0 reads (the Grand Diversion confirm rides exactly `"state": "awaiting_clarification"`, `naval_executor.py:413`); `envoy_digest` 0 reads. **Capture-arm precision: the driver DOES answer on bare `True`** (`:569-579` posts `/capture_choice`) — what it loses is the sibling `capture_data` (`main.py:3413-3415`: stage / summary / `dialogue_id`), so the ESTATE stage is undetectable → wrong policy token → the WO-H3 wedge | ⚠ |
| H-15 | WO-5's filed attribution is HALF WRONG. Bare `sue for peace` / `make peace` hit the FINAL-21 missing-target guard at **`llm_client.py:2041`** (*"which nation should I direct this proposal to?"*) — NOT the declare-war ask. The declare-war clarification (`diplomatic_executor.py:2026-2030`) is reached because **"end the war on any terms" contains the war keyword `"war on "`** (`llm_client.py:1018`, checked BEFORE the proposal keywords at `:1055`) — a peace request parses as a war declaration via a three-word substring, the WO-6 class at the diplomatic tier. Nation-suffixed forms (`sue for peace with Austria`) already reach the working proposal arm | ⚠ ✚ |
| H-16 | `corps_detail` builder: `naval.py:1805-1838` (embark predicate `:1813-1818`; three arms — ready `:1828-1831`, over-limit `:1832-1836`, else march-to-a-yard `:1837-1838`), feeding `expedition_terms[1]["detail"]` `:1846-1848` — the "fourth arm" (at a yard but failing another gate) slots here. The "MARSHAL ASKS:" default: `clarification_popup.gd:32`/`:39` reads `data.get("marshal", "Marshal")`; the Grand Diversion payload (`naval_executor.py:410-433`) carries no `marshal` key | ✅ ✚ |
| H-17 | "CR-1 524/524" = the parametrized corpus cases: `test_command_robustness_cr1_eval_harness.py:84-98` expands 333 entries × applicable worlds into 524 params | ✅ |

---

## §3 The slices

Numbering preserved from the eval's §5 ranked plan. Each slice: scope → seams →
contract → done-when → harness impact → pins. Estimates are sessions.

### Slice 1 — WO-H "The Instrument" (est 1, zero production code)

**Scope.** The playtest driver stops being blind and starts being
deterministic. Fixes WO-H1, WO-H2, WO-H3 and the three blind spots the eval
added (`state`, `envoy_digest`, the unseeded RNG), plus digest preservation.

**Contract.**
1. `_option_id` widened to read `id` / `choice` / `keyword` / `action` /
   `command` / `value` — **not `label`** (labels are display strings; matching
   them would couple the driver to copy).
2. `pending_capture_choice` arriving as bare `True` → the driver reads the
   co-shipped `capture_data` payload, **with its `dialogue_id`** so the W6-0
   stale-answer guard arms. The estate stage answers with a VALID token (the
   measured wedge: answering `"plunder"` to the estate stage is refused
   without clearing, and every later command returns *"You must decide the
   fate of…"* — WO-H3 is indivisible with WO-H1).
3. `battles` counted from `result["jealousy_attacks"][*]`
   (`turn_manager.py:405`) AND every enemy-phase battle row, not just
   top-level `battle_report`.
4. An `awaiting_clarification` arm: the driver reads `response["state"]` and
   answers clarification questions by stated policy (default: first offered
   option; policy logged per answer like every other popup policy).
5. An `envoy_digest` arm: rows answered through `POST /mailbox/respond` by
   stated policy (default `decline`, unchanged — but now EXPLICIT and
   counted in the digest instead of silently lapsing).
6. **Determinism:** the driver seeds the module RNG at every turn boundary —
   `random.seed(sha256(f"{campaign_seed}:{world_turn}"))` or equivalent
   derivation, recorded in `meta.json`. Sufficiency is established (§2 H-1: no
   `random.Random()` instances in backend). **PYTHONHASHSEED must also be
   pinned** — the `BASELINE_SERIES` runner pins `PYTHONHASHSEED=0`
   (`tests/test_ai_intent_threat_migration.py:532`, `:777`) precisely because
   hash order is load-bearing; the in-process driver re-execs itself with
   `PYTHONHASHSEED=0` when the variable is unset (and records the value in
   `meta.json` either way). *This item is this spec's addition — the eval's
   slice-1 contract omitted hash seeding entirely (§4 N-1).*
7. **Mode scope, stated in `PLAYTESTING.md`:** determinism guarantees apply to
   Mode A (in-process) only. `--http` drives a separate server process whose
   RNG the driver cannot reach — Mode B digests carry a "nondeterministic"
   banner in `meta.json` (§4 N-2).
8. **Digest preservation:** a `--archive` flag copies `digest.md` + `meta.json`
   (not the raw jsonl) to `docs/audits/playtest_digests/<run-name>/`, which is
   committed. A memo may only cite an archived digest. The digests the WO
   memos cite are archived retroactively in this slice.
9. `docs/PLAYTESTING.md` *Known-bad digests* gains WO-H1/H2/H3 **and**
   run-to-run nondeterminism, plus the §4 method rule from the eval: *a
   passing full test suite is not evidence that a change leaves
   `BASELINE_SERIES` alone* (the pin runs in a fresh hash-seeded subprocess;
   byte-identity claims require a real source-edit run through
   `_run_series_subprocess`).
10. The falsified *"causally inert"* refutation on the NPC harness row in
    `BUG_FIXES.md` §Napoleon Campaign is corrected (WO-H1 proved it
    load-bearing by experiment).

**Done when:** a run answers an estate prompt without wedging;
`capture_choice[estate]` appears in a digest for the first time; declare-war
ceremonies declare (A/B was `0 → 8` in 8 turns); two invocations of the same
script at the same seed produce identical `provinces`/`treasury` series;
`meta.json` records module-RNG scheme + PYTHONHASHSEED; the archived-digest
directory exists with the cited runs.

**Harness impact:** zero production code. M1–M7, `BASELINE_SERIES`, corpus —
untouched by construction.

**Pins:** the driver's diplomacy verbs keep working (eval §7.12 — gating typed
diplomacy in the DRIVER would delete the domain from every future unattended
evaluation); no `random.seed` lands in `backend/` production code (it would
collide with the BASELINE runner's own seeding discipline and constitute a
behavior change).

> **✅ LANDED August 21, 2026 — landing record.** All ten contract items
> built in `tools/playtest_driver.py`; zero production code — the slice's
> own commit touches only `tools/`, `tests/` and `docs/` (slices 2 and 3
> landed the same day as SEPARATE commits and own every `backend/` line;
> check per-commit, not the day's combined diff). Unit pins =
> `tests/test_playtest_driver_instrument.py` (23 — `_option_id` preference
> order incl. the never-`label` negative, the capture arm's `capture_data`
> fallback with `dialogue_id`, the clarification arm's four branches, the
> envoy arm's decline/accept/noop, battle counting from enemy-phase rows +
> `jealousy_attacks` + strategic-report combat rows (the review round's
> WO-33 recovery), sha256-not-hash seed derivation, and the precedence
> rule below). **Acceptance, measured:**
> - **Determinism:** two invocations of an 8-turn ambient run at
>   `historical` produced **byte-identical `digest.jsonl`** (and `digest.md`
>   identical but for the run name); pre-fix the same script at the same
>   seed ended 30/28/27. `meta.json` records `rng.scheme`,
>   `rng.deterministic` and `rng.pythonhashseed` (the driver re-execs with
>   `PYTHONHASHSEED=0` when unset). The 1b sweep then reproduced every
>   mock (arm, seed) triple identically — 72/72.
> - **WO-H1:** the re-run World Burns arm ends at **14 France WAR pairs**
>   (the original ended at the 3 boot wars — fifteen ceremonies, zero
>   declarations).
> - **WO-H3:** the estate stage is answered at the driver seam (unit pin)
>   and the re-run tyrant arm completes 30/30 turns; the stage-1 capture
>   popup now names its province ("Bohemia, Soult" where the old digest
>   read "(no summary fields)"). `capture_choice[estate]` in a live digest
>   is confirmed by the 1b sweep (see the 1b record).
> - **WO-H2:** the 5-turn smoke counts 10 battles where the old driver
>   counted 0.
> - **Archive:** `docs/audits/playtest_digests/` exists, committed, with
>   the surviving cited runs archived retroactively.
>
> **Two deviations, recorded honestly:**
> 1. **The Aug-16 `weird-tyrant` and `weird-world-burns` original digests
>    were DESTROYED before archiving** — by this slice's own acceptance
>    re-runs. The script's `name` key silently overrode `--name`, so the
>    re-runs landed in the originals' canonical dirs and `--fresh` deleted
>    them. Root cause fixed in the same landing as a contract addition:
>    **explicit CLI flags beat the script's own keys, which beat defaults**
>    (`--name`/`--seed`/`--llm` default to `None` so "explicitly passed" is
>    distinguishable — the old rule also silently ignored `--seed`, which
>    would have made 1b's seed sweep a silent no-op sweep of `historical`
>    nine times per arm). The archive therefore holds 9 of the 11 cited
>    runs; the two lost ones are represented by their fixed-driver re-runs,
>    marked as such.
> 2. The clarification arm answers with the typed index **"1"** rather than
>    re-posting the option's `command` string — the server's own
>    `interpret_clarification_answer` resolves it to the first ACTIONABLE
>    option's command, so the driver never guesses at copy; a question with
>    no actionable options (or `clarification_registered: false`) is left
>    standing and logged, because a blind token would be parsed as a fresh
>    command through the H-13 unconditional pop.

### Slice 1b — re-run the ten arms (est 0.25, machine time)

**Protocol (written here so "still shows collapsing" in G2 is decidable):**
each committed `weird_*.json` arm runs **3 seeds (`historical` + 2 banded
variance seeds) × 3 repeats** on the fixed driver. Report per-arm median final
provinces + min–max. **The funnel claim STANDS only if the worst
fighting-arm median exceeds the best non-military-arm median AND the min–max
bands do not overlap.** Otherwise the STATUS/`DESIGN_REFINEMENT` funnel
sentence is formally withdrawn and G2(b) (`BUILDING_SLOT_LIMITS["town"] = 1`)
stays shelved. A script arm that wedges on a variance seed reports as
`blocked`, never silently dropped. Results land as an addendum table in the
weird-outcomes memo + a STATUS line.

> **✅ RUN August 21, 2026 — landing record. THE FUNNEL CLAIM IS
> WITHDRAWN and G2(b) STAYS SHELVED.** Runner = `tools/wo_1b_sweep.py`
> (committed; `--reassemble` rebuilds the table from run dirs); seeds =
> `historical` + the banded `ulm` and `austerlitz`; full table + verdict
> = the memo's §9 addendum, dataset = `wo_1b_results.json` +
> representative digests in `docs/audits/playtest_digests/`. Headlines:
> every mock (arm, seed) repeat-triple **byte-identical** (the
> instrument's determinism proven at scale); the worst fighting-arm
> median does NOT exceed the best non-military-arm median and the bands
> overlap massively under every defensible grouping; **the SEED, not the
> strategy, dominates ambient-driven outcomes** (the same fighting
> script ends at 30 / 27 / 7 provinces across the three seeds). The
> live-parser arms ran per protocol and are excluded from the funnel
> bands (parse variance, both fighting-shaped). Method notes, recorded:
> five children froze in **asyncio's Windows socketpair fallback** under
> ~25 concurrent python processes (killed + re-run; determinism verified
> by byte-prefix diff against the completed sibling — NOT a game or
> driver defect; the runner now records a timeout row instead of
> crashing); and the first sweep ran while slices 2/3 landed, so the
> definitive dataset was re-swept ONCE on the final committed tree —
> *do not measure while the code moves.*

### Slice 2 — WO-N "The Names" (est 1)

**Scope.** WO-1 (enemy name executes army-wide) + WO-2 (unknown target
auto-corrects and marches). The two P1s are one defect on two name registers:
*the player names a thing and the game acts on something else.*

**Seams — corrected by this spec's verification (§2 H-8; the eval's cited
`executor.py:1794-1805` is only the routing hop).** WO-1's mechanism: the
CR-1 demotion at **`parser.py:688-702`** turns an extracted "marshal" that IS
a known enemy into a *target reference* (`llm_result["marshal"] = None` at
`:700`, target backfill `:701-702`) — a heuristic that is RIGHT for
target-position extraction misfires (`attack Kutuzov`) and WRONG for an
ADDRESSEE (`Kutuzov, retreat` / `Kutuzov retreat` — byte-identical, so the
fix keys on the resolved-name register, never the comma). With `marshal`
stripped, `_classify_command` (`:1560-1576`) routes the bare verb army-wide
(`general_retreat` `:1575-1576`) or into auto-assign (`Kutuzov, scout Swabia`
→ Soult), and `executor.py:1802-1803` executes. **Fix contract:** an enemy
name resolved in the ADDRESSEE slot refuses by name for ALL verbs (*"Kutuzov
commands for the Tsar, Sire"* — in-voice, names the man's side); the CR-1
demotion survives ONLY for target-position extraction (`attack Kutuzov` keeps
working). `Mack, attack Vienna` therefore refuses — it no longer sends the
whole army at Swabia.
WO-2: the two ungated `auto_correct` arms `parser.py:983-986` + the
strategic-marshal sibling `:1421-1422`, gated with the project's own
`_plausible_name_typo` (`:349`) exactly as its FOUR gated siblings are (§2
H-9); AND the live executor backstop `executor.py:299-304` — gate BOTH (gate
the parser alone and `move to the Moon` still marches ten provinces to
Morocco).

**Done when:** `Kutuzov, retreat` AND `Kutuzov retreat` both refuse by name;
`Mack, attack Vienna` refuses instead of attacking Swabia; `Kutuzov, scout
Swabia` no longer makes Soult scout; `attack Kutuzov` still resolves as a
targeted attack (the demotion's legitimate case, pinned); `Ney, move to
Avalon` answers *"Did you mean 'Leon'?"* (or refuses) instead of marching;
plausible typos (`Swabai`, `viena`) still march; corpus 333 unchanged and the
CR-1 eval harness green (524/524); **`BASELINE_SERIES` byte-identity proven
by a real source-edit subprocess run** (the player-direction guard should not
move it — prove, don't assert; the ENEMY direction is deliberately out of
scope here and owned by slice 10, which re-records).

**Docs task in-slice:** correct NPC-7's "three siblings are gated" claim on
its row (flagged in WO-2's seam column) — the parser arms at `:983`/`:985`
are ungated too.

**Pins:** the invented-name guard (`Zorblax` refusal) and the fallen/prisoner
guards (PC15-4) stay byte-identical; verbs with no bare form
(`fortify`/`drill`/`wait`) keep asking *"Which marshal, Sire?"*.

> **✅ LANDED August 21, 2026 — landing record.** Tests =
> `tests/test_wo_slice2_names.py` (21). Every done-when line measured green:
> both `Kutuzov, retreat` forms refuse by name and in voice (*"Marshal
> Kutuzov commands for Russia, Sire — he does not answer to us"*), `Mack,
> attack Vienna` refuses, `Kutuzov, scout Swabia` no longer makes Soult
> scout, `attack Mack` / `Soult, pursue Kutuzov` still target (pinned),
> `Avalon` no longer marches while `Swabai`/`viena` still do, corpus
> entries unchanged and the CR-1 harness green (535/535 — the param count
> grew with the corpus since the spec was written; entries untouched),
> `BASELINE_SERIES` byte-identical **proven by the real source-edit
> subprocess run** (`TestStep4SeriesPin` post-edit) and M1–M7 green.
>
> **One seam correction to this spec's own §2 H-8, discovered by building:**
> on the MOCK path the enemy addressee never binds as `marshal` at all —
> the CR-0 word-scan excludes enemy names from marshal candidates, so
> `Kutuzov, retreat` reached execution as marshal-less `retreat` with
> `target=Kutuzov` (the demotion fires only on the LIVE path, where the
> LLM extracts the addressee as marshal). A rider on the demotion would
> therefore have missed the mock path entirely. The fix is a standalone
> pre-check, `parser._resolve_enemy_addressee`, run before ANY extraction:
> the raw command's leading token (comma or not, honorific stripped,
> possessives excluded) resolved against the live enemy roster incl.
> camelCase split forms. Both extraction layers inherit one guard.
> Deliberate boundaries recorded at the helper: a lead that is also a
> REGION name is never an enemy (`Vienna, hold` stays a region address;
> `Brunswick` resolves as the province — the WO-13 collision rule ahead of
> slice 10); the TYPO arm requires the explicit comma-address shape, so a
> bare common word can never fuzzy-bind (`more cavalry` is not Moore) —
> residual: a typo'd addressee WITHOUT a comma (`Kutuzof retreat`) falls
> through to the old target shape, accepted and recorded.
>
> **One collision found by the suite and fixed in-slice:** the strategic
> phrase seam `_suggest_region_for_phrase` was written against the
> backstop's OLD silent contract, so the new demoted error leaked
> *"Did you mean 'Nassau'?"* into `Davout, hold the pass` — violating
> CA8-28's own pin that ordinary English never becomes a province, *not
> even as a guess*. The demoted class now carries
> `implausible_correction: True` and that seam swallows exactly it, while
> native suggest-band errors keep flowing (`Venetia` → *"Did you mean
> 'Vienna'?"*, CA8-28's same-answer-whatever-the-verb behaviour, its own
> pins green).
>
> **The find-then-refute fleet then took THREE MORE holes, all fixed
> in-slice** (each pinned in `TestReviewFindingsOnTheWire` /
> `TestGuardBoundaries`):
> 1. **P1 — the refusal was production-dead on /command.** It carried
>    `candidates: []`, so the CR-2 clarification arm skipped it and the
>    generic Berthier recovery replaced it — every enemy-addressee refusal
>    reached the player as a random shrug. Fixed with a verbatim-surface
>    arm in `main.py` beside the PARSE-NEG refusal arm (same wall as its
>    siblings — slice 11's WO-7 owns the soft-stop wall for all of them).
> 2. **P1 — the vassal/recruit early-returns bypassed the guard**:
>    `Kutuzov, grant Holland more autonomy` EXECUTED a permanent tribute
>    cut. The guard moved ABOVE every family early-return.
> 3. **P2 — the diplomatic route bypassed the guard entirely**: `Mack,
>    declare war on Prussia` staged the war-purpose ceremony. The
>    diplomatic branch now consults the same builder
>    (`_enemy_addressee_refusal` — ONE builder, the register cannot fork).
>
> **And three false-positive boundaries from the same round:** a lead
> followed by a third-person/auxiliary form is NARRATION
> (`_NARRATION_NEXT_WORDS`, closed-class: forms an imperative can never
> take — `Mack is at Swabia, Ney attack him` keeps its fully-correct
> parse); the typo arm screens ordinary English via the existing
> `_NON_TARGET_WORDS` (`More, cavalry to the front` is not Moore — the
> dictation risk the reviewer named); and the PLAYER roster gets right of
> first refusal on typo'd addresses (`Mark, attack Vienna` stays in the
> CR-2 did-you-mean flow). The refusal's suggestion line also names the
> intel road (*"for word of him, ask 'where is Mack'"*) — an enemy-name
> lead can be a question, not an order. **Accepted residuals, recorded:**
> a typo'd addressee with NO comma (`Kutuzof retreat`) falls through to
> the old target shape; the typo gate narrows live-mode tolerance on
> display-form multi-word enemy names by one edit (the space consumes a
> budget point) — degrades to an ASK, never a wrong action, which is the
> gate's whole design.

### Slice 3 — WO-3 the garrison floor (est 0.5)

**Scope.** A detachment garrison can fall. One-line class of fix at the floor:
`garrison_losses = max(garrison_losses, 1)` when the assault lands (the
measured shape: `garrison_losses >= 1` collapses the 3,000-detachment at
assault ~13; today it is 49 attackers dead by assault 500 with the garrison
still at 1 at assault 2,000).

**Seams.** `combat_executor.py:2697` (the truncated 10% floor beside the
attacker's 2% floor at `:2696`); collapse thresholds `:2714-2717` unchanged.

**Done when:** a 3,000-man detachment garrison falls by ~assault 13 under the
measured constants; a 25,000 major-capital garrison's arithmetic is unchanged
above 10 men (the floor only binds below `int(g×0.10) == 0`); the Bavarian
futility case is bounded (21 assaults → the garrison actually falls).

**Consciously NOT built:** the P4.25 futility guard (`enemy_ai.py:3483-3546`)
and the garrison-shaped futility-tracker arm (`:1220` reads `"battle"`, a
garrison hold emits `"garrison_assault"`). With the floor fixed, the
unbounded-futility case cannot recur (every assault now progresses), so the
guard is not needed; recorded so a later reader does not "complete" it
unprompted. **Post-fix arithmetic (this spec's verification, computed from
the real constants):** stripping a 3,000 detachment is NOT trivially cheap —
a 20k attacker pays ≈4,900 men (~24%) across the ~13 assaults, a 40k
attacker ~9,300 (the 2% floor scales with attacker size) — so the fix does
not hand P4.25 free garrison-stripping. **Harness impact:** ambient AI
garrison assaults now progress → run the M1–M7 harness; if
`BASELINE_SERIES` moves, this slice takes a flip-attributed re-record
(flip = the one-line floor).

> **✅ LANDED August 21, 2026 — landing record.** The one term
> (`max(…, 1)` beside the truncating 10% floor,
> `combat_executor.py` `_resolve_garrison_combat`) with the
> consciously-not-built futility guard recorded AT the seam. Measured
> through the real executor (`tests/test_wo_slice3_garrison_floor.py`,
> 5): the 3,000-man detachment falls at assault **13** exactly (spec's
> predicted shape), the frozen 1-man terminal state falls on the next
> assault, a 15,000 capital garrison still takes its full 10% floor, and
> the inertness-at-≥10 claim is pinned as arithmetic. **M1–M7 AND
> `BASELINE_SERIES` byte-identical WITHOUT re-record** — proven by the
> real subprocess run, and recorded as a fact about the harness (the
> 40-turn ambient board never assaults a sub-10-man garrison), not as
> proof of inertness; the behavioral tests carry that weight.

### Slice 4 — WO-D6 "The Capital Speaks" + WO-11 (est 1)

**Scope.** The fall of the player's OWN capital gets its own voice; an ally
liberating it does not fire the wound; a weight-95 capture can no longer be
crowded off the page; the Gazette stops captioning Paris's fall in the
victor's words.

**Contract.**
1. New headline class `capital_lost` at weight **100**; `home_captured`
   demoted to **99**. **Ordering pin (this spec's correction — the eval never
   mentions the top of the table):** `sovereign_captured 101 > capital_lost
   100 > home_captured 99 > marshal_destroyed 96 > marshal_captured 95` —
   the NP-4 ruling (*the Eagle in Chains outranks even a fallen homeland
   province*, `dispatch.py:59-62`) stays intact ABOVE the new class.
2. The class predicate keys **structurally** on
   `world.get_nation_capital(player_nation)` — never the literal "Paris".
3. **WO-11 in the same edit:** both `capital_lost` and `home_captured` gain
   the direction guard the sibling arm at `dispatch.py:435` already has —
   fired only when the player's side LOST the province (an ally's liberation
   of Paris must not raise the game's most ceremonial wound).
4. **The Gazette caption** (`gazette.py:94-104`): when the stormed capital is
   the PLAYER's own, the special edition captions the loss in the loser's
   voice, not "a capital stormed" (one `if`, one string; the sovereign
   special-case at `:105-111` is untouched).
5. **The diverse-tail rule** (~4 lines, no new templates): the LAST sub-beat
   slot is reserved for a class not yet on the page. Measured shape:
   `PARIS HAS FALLEN / Limousin / Marshal Soult has been taken` instead of
   three `home_captured` rows with Paris absent.
6. `own_mauled` floor is NOT here — it is slice 12's (WO-16).

**Done when:** Paris's fall leads with its own sentence on a four-province +
two-capture turn (the eval's deterministic probe reproduces md5-identical
under `PYTHONHASHSEED=1` and `=2`); an ally's liberation fires neither class;
a weight-95 capture reaches the page via the diverse tail; **all three CA8-5
pins green and byte-identical** (§2 D-10 — the naive per-class collapse reds
`test_two_different_marshals_still_get_two_beats`; the diverse-tail rule must
not); zero movement on `CAMPAIGN_LOG_TYPES` pins (§2 D-15 — headline classes
are display vocabulary, not event types).

**Harness impact:** dispatch is display; M1–M7 / `BASELINE_SERIES` unreachable
(weights documented "display only, tunable freely"). Zero `.gd`, zero fields.

### Slice 5 — WO-D5 "Berthier Names the Peace" — ✅ LANDED August 22, 2026

**Scope.** The one strict inequality that hides an ACCEPT-able peace for
thirty turns. Rung 1 of `_build_situation_recommendation` widens from
`war_score < 0` to *losing OR mutually exhausted*, where "mutually exhausted"
is a pure predicate **lifted out of `_process_exhausted_pair_exits`**
(`settlement_third_party.py:453-462`: both sides ≥ `PAIR_EXIT_WE_FLOOR` 120,
war age ≥ `PAIR_EXIT_MIN_TURNS` 10, |war score| ≤ `PAIR_EXIT_STAGNANT_SCORE`
15) so both readers share one source. Arithmetic check: WE accrues +8/turn →
both sides cross 120 at ~t15, which is exactly the measured "ACCEPT from t16".

**Post-G1 copy contract (this spec's addition, §4 N-7):** the counsel must
name a SURFACE the player can still press, not a typed verb — after slice 7,
"ask for terms" as a typed sentence may be family-redirected. The rung's copy
points at the war room's Request Terms affordance (`war_detail_popup.gd`
button → `main.gd:5295`, verified live) and/or F1. Copy names the court and
the ask; never instructs the player to type a diplomatic sentence.

**Also in-slice:** a `--diplomacy propose` driver arm (Mode A) so future
unattended runs can exercise the bilateral-peace path the WO campaigns never
pressed.

**Done when:** at t16 of the Long Quiet reproduction the counsel names Russia
as a court that would sign; the advisory is provably off the turn path (§2
D-2: one caller, player-command only) — M1–M7 / `BASELINE_SERIES` untouched
without re-record; no new dtype, no queue arrival, no field, no `.gd`.

**Pins:** do NOT un-saturate war exhaustion (the component scores the
ACCEPTING leader — a France that never sues arrives at WE 200 and dictates;
grind-to-cap-then-dictate must stay impossible); do NOT build the congress
(its transport is war-level — `_emit_settlement_offer_for_war` has no pair
dimension; a France|Russia pair peace through it becomes a whole-coalition
settlement fronted by Britain); `request_terms` ships already — the counsel
NAMES it, nothing replaces it.

> **Landing record — authoritative. LIFTED AHEAD OF SLICE 4 by user
> direction** (August 22, 2026): the two are independent — slice 4 is the
> dispatch's headline ordering, slice 5 is the war room's counsel — and
> nothing in 4 blocks 5. **Slice 4 stays next**; only slice 5's position
> moved, recorded here rather than absorbed (the §5 amendment idiom).
> `tests/test_wo_slice5_berthier_names_the_peace.py` (56); mutation sweep
> `tools/_sweep_wo5.json` — **23 mutations, 23 killed, 0 inert** (one
> INERT pin found and replaced, below); M1–M7 and `BASELINE_SERIES`
> byte-identical, **measured, and the series pin itself proved live by
> mutating it** (index 0 recomputes to 70; a planted 71 reds it) — slice
> 15's lesson taken literally; zero `.gd`.
>
> **The mechanism was reproduced before a line was written**, and it is
> worse than the row describes. An 18-turn ambient Mode-A run at seed
> `austerlitz` (the Long Quiet's seed), snapshotting turns 12/16/18, then
> probed off the saves:
>
> | turn | France\|Russia | WE France / Russia | pair score | predicate | Russia's plain peace |
> |---|---|---|---|---|---|
> | 12 | age 11 | 104 / 98 | 0 | **False** | COUNTER_OFFER (49) |
> | 16 | age 15 | 136 / 130 | 0 | **True** | **ACCEPT (54)** |
> | 18 | age 17 | 152 / 146 | 0 | **True** | ACCEPT (55) |
>
> The predicate's own turn-on and the court's willingness arrive together
> — the spec's "+8 WE/turn → both cross 120 at ~t15" arithmetic, confirmed
> by measurement rather than assumed. **And the war row France was looking
> at read `+26`**: `build_active_wars` COLLAPSES a coalition into one row
> whose `war_score` is the WAR-level side score (CA8-D2), so the dead
> France|Russia pair was hiding inside a row France is *winning*. The old
> `war_score < 0` gate could never have fired on this board no matter how
> long the stalemate ran. Turn 16's counsel, before: *"Britain's war has a
> purpose we can price — 'The Low Countries'…"*. After: *"the war with
> Russia has gone still — 15 turns, and the ground has not moved; both
> courts are spent. Nothing more will be won here by fighting; a court
> this weary will hear an offer. Open talks with Russia below, or take
> your seat in the Cabinet (F1)."* Turn 12 is untouched.
>
> **The single-source lift** is
> `settlement_third_party.pair_is_mutually_exhausted(world, a, b, joined_turn)`
> — the three comparisons in ONE pure function, and
> `_process_exhausted_pair_exits` now asks it rather than owning it (same
> short-circuit order, same answers; `exhaustion` and the
> `get_war_score_for` import dropped as dead locals). `joined_turn` stays
> the CALLER's on purpose: the turn-path reader has the war instance's own
> `joined_turn` off `diplo_key_meta`, the advisory has
> `world.war_start_turns` (what `build_active_wars` measures `duration`
> from). Re-deriving one of them inside a function the turn path calls
> would have been a behaviour change wearing a refactor's coat. Three pins
> hold the shape, and one is an AST census asserting each of the three
> constants is read inside `pair_is_mutually_exhausted` and nowhere else.
>
> **Rung 1b reads PER COURT, not per row** — the collapsed-row finding
> above makes that mandatory, and rung 1.5 already walks `opponents` for
> the same reason. Ordering is |pair score| ascending then name: the most
> stagnant pair is the one where neither court has anything left to gain,
> and on the measured board it is also the better counsel by the game's
> own scorer (Russia at |0| scores ACCEPT 54; Britain, next at |7|, is
> still COUNTER_OFFER 42). Losing still outranks stuck. A pair with no
> recorded war start is skipped rather than read as ancient.
>
> **The copy contract (§4 N-7) is applied to the whole rung, both new arms
> AND the two pre-existing losing arms** — the eval's *"ask, Sire"* that
> N-7 objects to IS the losing arm's shipped text. Every arm now names a
> pressable surface in the vocabulary slice 7 already taught the player
> (`main.gd:1687` *"open the war banner and press Request Terms"*,
> `main.gd:1693` *"Take your seat in the Cabinet"* / F1), and a falsifiable
> negative forbids any arm from dictating a sentence to type.
>
> **The `--diplomacy propose` driver arm** (Mode A) sends ONE bilateral
> overture per turn, round-robin over the courts France is at war with,
> choosing `request terms from X` / `propose peace with X` off the game's
> OWN `request_terms_state` rather than a copy of its rules (both are
> golden-corpus phrasings; the driver keeps typed diplomacy per §6
> never-do 12 — the Cabinet redirect is client-side and `POST /command` is
> the surface under test). It answers incoming as `accept` does, because
> an arm that sues for peace and then declines the peace it is handed
> measures nothing.
>
> **Building it found two driver defects that no previous policy could
> reach, and the arm could not have worked without fixing them:**
>
> 1. **The AI's own peace offer was unanswerable.** It arrives as the
>    incoming-proposal POPUP payload
>    (`mailbox_payloads.build_incoming_proposal_popup`) — a rendering of a
>    real `incoming_proposal` dialogue carrying its `dialogue_id` but
>    neither the `type` key nor an options list — so the driver's type
>    table and both keyword searches missed it and it was logged
>    `(left standing)`: **7 times in 18 turns**, including Russia's answer
>    to France's own overture. Now answered exactly as the client answers
>    it (`main.gd _on_incoming_proposal_choice`): a bare keyword from the
>    router's own table plus the payload's `dialogue_id`.
> 2. **A stale passthrough was answered twice.** Every POST rebuilds the
>    popup passthroughs, so a response generated BEFORE an answer lands
>    re-carries the dialogue that answer popped. When one command raises
>    two surfaces — a marshal petition AND a proposal confirm, ordinary on
>    a turn France sues for peace — dialogue #27 was answered once for
>    real and once against whatever the stack had promoted since (the CA9
>    typed-router shape, from the harness side), and the cycle guard then
>    STOPPED THE CHAIN, leaving real blockers standing. **9 of 18 turns;
>    zero under every other policy, which is why it had never been seen.**
>    `Answerer.begin_post()` plus a per-post answered-`dialogue_id` set
>    fixes it at the identity, not the symptom.
>
> With both fixed the arm works end to end: **turn 16 WAR → ARMISTICE with
> Austria, turn 18 WAR → PEACE with Britain** (*"the war with Britain is
> over. The peace grants safe passage home."*) — the bilateral-peace path
> the WO campaigns never once pressed. One `ANSWER CYCLE` warning survives,
> on a turn whose legitimate five-stage ceremony ends in two DIFFERENT
> `proposal_confirm`s: the guard's `(key, summary, choice)` signature
> cannot tell them apart. Left alone deliberately — it is the documented
> reading trap, it stops one chain after the ceremony completed, and the
> turn ended clean.
>
> **Determinism and regression, both measured:** the default-policy
> 18-turn digest is **byte-identical before and after every driver edit**,
> and two `--diplomacy propose` invocations at the same seed produce
> byte-identical digests.
>
> **Consciously touched pins:** three answerer doubles in
> `test_playtest_harness_win_campaign_2026_08_16.py` gained a no-op
> `begin_post` (behaviour of those pins unchanged — the double was simply
> incomplete once `drain()` opened each chain).
>
> **One INERT pin found and replaced by the sweep:** the first
> single-source check read `inspect.getsource(_mutually_exhausted_courts)`
> for the module name — and a mutation replacing the import with a local
> `def` of the same name left the docstring's mention behind, so the pin
> still passed. It now monkeypatches the engine's predicate and asserts the
> counsel follows: the one check a copy cannot survive.
>
> **Discharges** the WO-D7 carry contract's named near-term mitigation
> (`DESIGN_REFINEMENT.md` §WO-D7..D11): the ACCEPT-able peace is visible.
> The billing half stays carried to EC-2 pass 2, untouched.

### Slice 6 — WO-D3 "The Admiralty Speaks Plainly" (est 0.5, backend copy)

**Scope.** WO-14 at BOTH producers (`naval_executor.py:107-115` and the
Admiralty chip note at `naval.py:1885-1899` — §2 H-7): the blockade message
computes who is actually pinned from `blockaded_nations()` (the real pin set,
applied at `naval.py:1273-1280`) and names the gap when the closure sits
below the next notch (the measured 53.82 vs 125.0); the inverted *"their
crews rot at anchor while ours drill"* line dies. The expedition refusal
stops naming an impossible remedy — **message-only**
(`_execute_naval_expedition` is the shared GR5 executor Britain's Lisbon
expedition flows through; eval §7.8). `corps_detail`
(`naval.py:1805-1838`, three arms today — §2 H-16) gains its fourth arm: a
marshal standing AT a dockyard but failing another gate is told which gate.
The Grand Diversion's confirm gets a real modal subject — stamp a `marshal`
(subject) field on the `naval_executor.py:410-433` clarification payload;
`clarification_popup.gd:32`/`:39` already renders whatever is stamped and
currently defaults to the literal *"MARSHAL ASKS:"*.

**Also in-slice (the hunt's stranding-copy fold):** the over-lift refusal
advertises *"garrison the excess here"* on soil where `_execute_garrison`
refuses (not-controlled beachheads — `economy_executor.py:912-916`), and the
SHUT-crossing refusal advertises *"a small expedition"* to a corps above the
15k lift — both refusals name the road that actually exists for that corps
(detach at a held port / capture a coastal province first / wait for the
window), or say honestly that there is none this turn.

**Done when:** the blockade order names who is actually pinned; the drill line
is gone; the diversion modal carries its own subject; a stranded over-lift
corps is never advised an illegal remedy; zero behavior change on the
expedition executor (copy-only proven by the naval test families staying
green unmodified).

### Slice 7 — WO-D2 "The Cabinet Is The Only Door" (G1 build, est 1)

**Scope.** The G1 ruling lands: the typed diplomatic verb family is redirected
in character on the terminal input path; the wizard becomes complete enough to
BE the only door; the four honest-availability items land beside it.

**Contract.**
1. **The interception** lives inside `_execute_command()` (`main.gd:1298`) —
   the only path player-typed text travels (§2 G1-1). Every chip pipeline
   bypasses by construction (§2 G1-2/G1-13 — the regression-risk census
   found ZERO diplomatic producers on the terminal path). **Placement pin
   (§2 G1-9):** the matcher sits BELOW the redemption typed-token block
   (`main.gd:1333-1340`) and its patterns must never match the underscore
   tokens `grant_autonomy` / `dismiss` / `demand_obedience`. Detection = an
   explicitly enumerated verb-head list (see the family table below), matched
   conservatively: **fail-open** — a sentence that does not clearly match a
   family head goes to the backend exactly as today, and heads are
   sentence-shaped (verb + object), so a typed dialogue ANSWER can never
   match (§2 G1-10). The redirect prints Berthier's line naming the Cabinet
   (F1) — e.g. *"Matters of state are conducted through the Cabinet, Sire —
   the diplomatic wizard awaits (F1)"* — in-voice, costs nothing, sends
   nothing. Recorded edge: re-typing a full diplomatic order while its
   confirm dialog stands re-parses today and would print the pointer
   instead — the popup buttons and the answer words (`proceed`/`confirm`/
   `yes`) still resolve the dialog, so nothing is lost.
2. **The family** (redirect list; the wizard/panel home each verb already has
   is the second column — a verb with NO home may not be redirected until its
   home exists):

   | typed family head | UI home |
   |---|---|
   | `declare war on X` | wizard conflict flow (war-purpose staging) |
   | `propose <peace/alliance/non-aggression/open borders/trade/armistice>` | wizard step-2 rows |
   | `vassalize X` / `make X a vassal` | wizard VASSAL row (+ the ALLIANCE-branch fix below) |
   | `invest in <vassal>` | VASSALS ledger tab chip |
   | `grant X autonomy` / `reduce X autonomy` | VASSALS tab chips |
   | `cede <region> to X` | wizard VS-3 province picker |
   | `release X` | VASSALS tab chip |
   | `guarantee X` / `sponsor <design>` / `buy off <design>` | AI-6c wizard chips |
   | `improve relations with X` | wizard mission row |
   | `sue for peace` / `make peace` / `peace with X` / `end the war` (WO-5 family) | wizard peace rows |
   | `request terms from X` | war-detail Request Terms button (`main.gd:5295`) |

   **Exclusions (stay typed; this spec's addition, §4 N-4):** marshal-reward
   verbs (`grant X a rente`, `revoke`, `endow X with <estate>`,
   `commission X`) — the reward economy is NOT diplomacy and the committed
   playtest scripts exercise it typed; `Talleyrand, assess` and question-form
   advisories (read-only); dialogue ANSWERS (`accept`/`decline`/`yes`/nation
   names — consumed by the dialogue router before command parsing and not
   verb-heads anyway); the redemption tokens (`grant_autonomy` etc. — §2
   G1-9); every military/econ/naval verb; **and the three family verbs with
   NO UI home (§2 G1-11): `make_amends`, `set_war_purpose`,
   `repudiate_bargain`** — a verb with no wizard/panel home may not be
   redirected (it would become unreachable outright); they stay typed with
   this exemption RECORDED, and giving `make_amends` a wizard row is the
   named follow-up if the user wants the family complete.
   `request terms` inclusion is a recorded DECISION (the ruling's "only path"
   language covers it; the wizard has NO request_terms case, but the
   war-detail chip is live and verified — `main.gd:5295-5311` — so the
   redirect points at the WAR ROOM for this one verb) — reversible by
   removing one list entry if the user prefers it typed.
3. **Drift pin:** a Python test regex-extracts the `.gd` head list and asserts
   (a) every mock-parser-reachable diplomatic action id maps to at least one
   head in the list or the documented exclusion set, and (b) every corpus
   entry whose expected action is family-tier has a command string matching a
   listed head. The client list and the parser must not drift apart silently
   (the CA9 through-line — two implementations of one rule — acknowledged and
   pinned rather than pretended away).
4. **The help text stops teaching the typed verbs**
   (`meta_executor.py:652-662` — the eval's "seven verbs" undercounts: break
   treaty and ultimatum are taught at `:659` too, §2 G1-8) — every one
   becomes a pointer at F1 / the named panel. **The rewrite must also kill
   the stale "trade" promise at `:656-657`** (a proposal type that exists in
   neither `PROPOSAL_TYPE_KEYWORDS` nor the wizard — do not preserve it in
   the new copy).
5. **The ALLIANCE branch:** `propose_vassal` added to the
   `elif state == "ALLIANCE"` branch (`diplomacy.py:11072-11092`) — now
   load-bearing, since the wizard is the only door and **Bavaria and Spain
   boot at ALLIANCE** (§2 G1-3). **The guard already exists — do not invent
   one:** `VASSAL_MIN_STATES` at `diplomacy.py:127` includes ALLIANCE and is
   enforced at the acceptance seam (`:2922`, `vassal.py:132-133`); the fix is
   making `_proposal_action`'s VASSAL rows consult that EXISTING single
   source (§2 G1-5/G1-6) so emitter and acceptance can never diverge again.
6. **`invest_in_vassal` ceiling** (`vassal.py:1076`; charge-then-clamp at
   `:1135-1138`, the false "+10 (100 → 100)" message at `:1148-1149`): at
   loyalty 100 (`LOYALTY_MAX`) the verb refuses and charges nothing (today:
   1 DP + 200g for nothing — the DEFAULT interaction, two of three boot
   vassals sit at 100).
7. **Backend executors stay** — wizard transport + driver/debug path. No
   executor deleted, corpus 333 unchanged (it tests the parser, which still
   runs for the wizard's strings), GR5 untouched (the AI never types), the
   tutorial clean (no diplomatic suggest chips — verified, all 15 steps
   enumerated).
8. **Wizard gating holes closed while the wizard becomes the only door**
   (this spec's addition — the hunt's coverage census): the vassal branch's
   early `return` (`diplomacy.py:10710`) drops `cancel_mission` for a
   later-vassalized court (once typing is retired, a mission against it
   loses its only cancel — re-emit the row past the early return);
   `mission_improve_relations` is absent in WAR/ALLIANCE states (decide and
   record per state, don't leave it accidental); D5 design chips vanish on
   deckless worlds while the parser accepts the verbs (acceptable — deckless
   is the legacy fixture — but RECORD it beside the family table).

**Done when:** typing `vassalize Bavaria` sends nothing and points at the
Cabinet; the wizard's own `command_selected` path provably unaffected (chip
regression test); Bavaria and Spain offerable in the wizard; no VASSAL row
renders available where the executor refuses; investing at loyalty 100 refuses
free; help teaches F1; the drift pin green; corpus 333 unchanged.

**Recorded residuals:** raw HTTP and the driver keep typed diplomacy (by
design, eval §7.12); live-parser synonym phrasings can still reach the free
executor (§1 residual (c)) — the free `make_vassal` price itself is
unchanged by ruling, and G1(a) remains the named layer-on-top if the user
wants the price closed.

> **✅ LANDED August 21, 2026 — landing record.** Taken OUT of §5 order at
> the user's direction (*"make cabinet door so diplo only works through ui
> typing it should tell you thematically to go to the table (screen) maybe
> a link there"*); nothing in slices 4/5/6 blocks it, and slice 7 was
> already sequenced before 11. Commit `96a37fe`.
>
> **The interception** is one call at the top of `_execute_command()`
> (`main.gd`), below the redemption-token block per the §2 G1-9 placement
> pin and hardened past it — ANY underscore token fails open, so a
> redemption answer can never be claimed however it is phrased. Berthier
> answers in voice (*"Matters of state are conducted at the table, Sire —
> not by dispatch. Take your seat in the Cabinet and the courts of Europe
> will answer."*) with a clickable **⚜ Take your seat at the table (F1)**
> link on a new `cabinet:open` arm of `_on_output_meta_clicked`, opening
> the wizard behind the same `_is_modal_dialog_open` guard F1 uses. It
> costs nothing, sends nothing, and returns before `set_input_enabled`
> ever fires, so the terminal stays live.
>
> **The list is a MIRROR of the mock parser's own diplomatic funnel, not a
> second classifier — and that is the design, not a shortcut.** The CA9
> through-line is two implementations of one rule drifting apart, so the
> lists are transcribed from `llm_client._parse_command`'s keyword blocks
> and the redirect therefore classifies a sentence EXACTLY as the backend
> already would: a sentence the parser calls diplomacy is the sentence the
> Cabinet claims. Substring semantics are mirrored deliberately (GDScript
> `in` on a String is containment, as the parser's `any(kw in cmd)` is).
> Precedence is mirrored too: the three no-home verbs are checked FIRST,
> which is the only reason `set war purpose against Austria` — which
> carries the war-declaration substring `war against ` — survives.
>
> **The slice's own corpus census changed the build three times, and each
> correction is more interesting than the code:**
> 1. **Keying family-tier on `expected.action` called 43 plainly
>    diplomatic rows "non-diplomatic"** and duly reported the redirect for
>    stealing them. 177 of the corpus's 333 rows carry no action id at
>    all — a proposal row asserts `type: "diplomatic"` plus a `diplo`
>    sub-dict instead. The census now classifies on
>    `diplo.proposal_type`/`mission_type`, and the trap is recorded at the
>    classifier for the next reader.
> 2. **A whitelist of proposal nouns on the Talleyrand-address route let
>    FOURTEEN ordinary orders through** — *"negotiate a ceasefire with
>    Prussia"*, *"make Saxony a protectorate"*, *"sow discord between
>    Prussia and Austria"*, *"build rapport with Saxony"*, *"convince
>    Austria to join us"*. Synonym phrasings are exactly what a whitelist
>    cannot enumerate, so the route **inverted**: the parser sends EVERY
>    diplomat-addressed sentence into the funnel, so the Cabinet claims
>    the whole route minus an EXEMPTION list (counsel verbs — claiming
>    `assess` would make the rewritten help a liar, since it still teaches
>    assess as spoken — and misdirected military verbs, because
>    *"Talleyrand, attack Prussia"* already has a better answer than a
>    Cabinet pointer).
> 3. **`don't declare war on Austria` was being answered with a Cabinet
>    pointer.** Both paths execute nothing, so this is not a safety
>    question but a question of which voice answers — and PARSE-NEG's
>    clause guards refuse it by name. The redirect yields to the
>    specialist (`DIPLO_NEGATION_MARKERS`).
>
> **The wizard became complete enough to BE the only door.** ALLIANCE
> gained its `propose_vassal` row — **live-verified: Bavaria boots at
> ALLIANCE and the row now returns `available=True`**, so vassalizing an
> ally had been unreachable while the acceptance seam allowed it all
> along; `_proposal_action` consults the SAME `VASSAL_MIN_STATES` the
> acceptance seam enforces, so emitter and executor cannot diverge again
> (pinned by a both-ways test that removes ALLIANCE from the constant and
> watches the row darken); the DPF-2 cancel row was hoisted to
> `_cancel_mission_row()` and shared, so a mission opened against a court
> that is LATER vassalized keeps its only cancel; and
> `invest_in_vassal` refuses free at `LOYALTY_MAX` with the wizard row
> mirroring the refusal. **Contract correction, measured live: the spec
> says "two of three boot vassals sit at 100" — it is THREE of three**
> (Holland, KingdomOfItaly, Switzerland, all 100/100), so the paid no-op
> was the only invest the 1805 board offered on turn 1.
>
> **Item 8's third hole is DECIDED rather than left accidental:**
> `mission_improve_relations` is deliberately absent in ALLIANCE
> (REASSURE_ALLY is the ally-maintenance mission) and in WAR (you do not
> court a belligerent — the armistice thaw and the settlement table are
> the wartime levers), recorded at the branch.
>
> **Scope extension, recorded rather than smuggled:** the family table
> blesses eleven verb heads, but the ruling's own words are *"the Cabinet
> is the only door"* and the user's direction was *"diplo only works
> through ui"* — so **break treaty / downgrade / ultimatum / cancel
> mission / the settlement family are ALSO claimed**, every one of which
> has a verified wizard or war-room home. Reversible by deleting list
> entries; the drift pin will name whatever stops being claimed.
>
> **Verification:** `tests/test_wo_slice7_cabinet_door.py` (30) incl. the
> two-directional 333-row census, the enumerated verdict for all eight
> undecidable rows, the chip-pipeline bypass pin (§6 never-do 14), and a
> pin that the tutorial's fifteen suggest chips — which FILL the command
> line for the player to press Enter — carry nothing the Cabinet would
> steal. R120's help pin (`test_diplo_refinement_wave1.py`) flipped
> CONSCIOUSLY: it asserted the help teaches `propose` and `improve`, the
> two verbs this ruling retires. **`BASELINE_SERIES` and M1–M7
> byte-identical, proven by real subprocess AFTER the AI-shared invest
> change** (the AI's P1.6 rung picks the LEAST loyal vassal, so the
> ceiling is ambiently unreachable — measured, not assumed). Godot parse
> harness EXIT=0. Backend half live-verified over HTTP on an isolated
> port (the user's own session was live on 8005 and was not touched).
> Suite **18,297/3**.
>
> **THE REVIEW ROUND (same day) — and its headline finding is about the
> TEST, not the code.** The fleet crashed on a session limit after one of
> seven lenses and zero refuters, so its verdict column is an artifact,
> not a judgment; the surviving lens's nine findings were adjudicated by
> hand and **all nine were real**. The one that mattered most: **the
> drift pin never parsed anything.** It compared id strings and
> re-executed the mirror over 333 pre-written corpus rows — between them
> they can only catch a divergence somebody already thought to write
> down, never a phrasing that reaches a diplomatic executor without being
> claimed, which is the single failure mode this ruling is exposed to.
> The file's own docstring claimed it worked "by parsing a real utterance
> per action id"; it did not, and that sentence is what hid the rest.
>
> The fix is `TestTheMirrorAgreesWithTheParser`: candidate sentences go
> through the REAL mock parser and the mirror must agree with the action
> it actually returns. **On its first run it reproduced SEVENTEEN leaks**
> — every one a sentence that would have reached a diplomatic executor
> through the door this slice closed:
> * **the modal openings** — `DIPLO_ADVISORY_STARTS` carried
>   should/will/can/do/have/is, and a modal opens an ORDER at least as
>   often as a question: *"have Talleyrand propose peace to Austria"*,
>   *"do declare war on Prussia"*, *"should we declare war on Prussia"*
>   (no question mark) all parse at 0.95 and SENT. Narrowed to wh-words,
>   which cannot begin an order; anything else phrased as a question
>   carries the mark, tested first.
> * **the comma-scoped address route** — the parser's gate is the
>   diplomat's name ANYWHERE, and *"send the envoy to Bavaria"*,
>   *"instruct the ambassador to seek an armistice with Austria"*, *"our
>   minister will offer a truce to Prussia"* and *"tell Talleyrand to
>   demand Silesia from Prussia"* carry no comma address and no family
>   keyword. Widened to match the parser, made safe by a new
>   `_contains_word` boundary helper rather than a substring — the reason
>   the route was narrow in the first place was that "administer"
>   contains "minister".
> * **the negation exemption I had added hours earlier** — a substring
>   bail, so *"declare war on Prussia WITHOUT delay"* bailed past the
>   Cabinet into a real war declaration. **The reasoning was right and
>   the mechanism was wrong**: a door with a wildcard in it is not a
>   door. The exemption is DELETED and negated diplomatic sentences are
>   claimed like any other (nothing executes either way); PARSE-NEG keeps
>   every military negation, which is its actual domain, and the census
>   now pins both halves.
> * **`change_autonomy`'s second arm** — the parser also routes
>   (make|set|turn) + (puppet|satellite|autonomous), and *"autonomous"
>   does not contain "autonomy"*, so *"make Holland a puppet"* changed a
>   boot vassal's autonomy through the closed door.
> * **`court`** — nation-GATED in the client, bare-with-an-exception in
>   the parser: *"court Bavaria's favour"* walked through on an
>   apostrophe. Now the parser's own `\bcourt\b(?!\s+martial)` rule.
> * **the underscore guard was a wildcard** (`declare war on Prussia_`
>   walked through) — scoped to a single bare token, which is what the
>   placement pin actually protects.
> * plus `bought off` / `pay out`, two of the parser's six buy-off forms.
>
> **A second gap the Python pin cannot reach by construction — the
> shipped GDScript is never executed by it — was closed by executing it:**
> `tools/wo7_matcher_smoke.gd` instantiates `main.gd`'s script in a real
> headless engine and calls the real predicates. **32/32**, including the
> boundary cases the new helper exists for (court martial excluded,
> administer ≠ minister, the possessive apostrophe).
>
> **One finding is structural and is recorded as a residual rather than
> fixed:** the mirror mirrors the MOCK parser, so in live-LLM mode a
> sentence the fast parser scores below 0.7 escalates to a model that is
> explicitly taught the diplomatic action set. That is spec §1 residual
> (c) — "live-parser synonym phrasings can still reach the free executor"
> — now with a named mechanism. Closing it needs a backend-side gate
> (G1(a)), which the ruling records as the named layer-on-top.
>
> **Visual sign-off — EVIDENCE CAPTURED August 21, 2026; ✅ USER SIGN-OFF
> GIVEN August 22, 2026** (the frames were put in front of the user and
> signed). Both surfaces, in the REAL `main.tscn` against a sandboxed
> backend on `SOVEREIGN_PORT=8006`, by the committed harness
> `tools/wo_signoff_screenshot.gd`:
> `docs/audits/WO_SIGNOFF_1_CABINET_REDIRECT_2026_08_21.png` — typing
> *"propose alliance with Austria"* through the client's own
> `_execute_command` (the ONE terminal-typed path) yields Berthier's line and
> the gold **⚜ Take your seat at the table (F1)** link, with **Actions still
> 4/4 and DP still 5/5** on the HUD: nothing sent, nothing spent, which is
> the ruling's whole promise made visible. And
> `docs/audits/WO_SIGNOFF_2_WIZARD_FROM_LINK_2026_08_21.png` — the wizard
> opened by feeding `_on_output_meta_clicked("cabinet:open")`, i.e. through
> the LINK rather than F1, showing the court picker with Formable Nations and
> the three live at-war courts. **A captured screenshot is not a sign-off;
> the user's eye is.**

### Slice 8 — "The Panel States Its Terms" (WO-D1-A + WO-D4-A + G3, est 1.5)

**Scope.** The muster preview quotes the supply arithmetic and G3's sentence;
the supply figure is single-sourced everywhere it renders; build chips state
their terms. This is an **amendment to PC15-D2's own deferred region-panel
row** (eval §7.1), not a new finding.

**Contract.**
1. `_build_muster_preview` (§2 C-1) gains the price block: *"78,676 if all
   march — Swabia feeds 60,000; the whole muster standing there costs 11,340
   a turn"* — the fed figure from `get_effective_supply_cap` (§2 C-2, the
   1.5× allied-soil arm included), the attrition figure from the supply
   engine's own arithmetic (single source, shown=applied). Plus **G3's
   honest sentence**: *"every corps in the province fights"* — with the free
   exclusion taught for ADJACENT corps only.
2. **One supply figure everywhere:** ledger (`ledger.py:187`/`:202`), map
   summary (`world_state.py:8361`), region panel (`region_panel.gd:195-197`)
   all render the player's EFFECTIVE cap through the one source — printing
   the honest 60,000 in the preview while the panel says 40,000 would
   re-create the PT-D5 two-figures-one-label trap this slice exists to
   remove. The **PC15-16 `-1` fog sentinel** (§2 C-7, `world_state.py:8494-8499`)
   is preserved on every changed surface or the slice ships production-dead
   on fogged rows.
3. **Build chips state their terms** (WO-D4-A): the region-panel build chips
   quote cost / yield / upkeep / supply live (`Depot 300g · +50/turn ·
   +10,000 supply · 20g upkeep`), threaded through
   `get_filtered_game_state_summary` (`world_state.py:8425`).
4. **Consciously NOT built:** depot/market re-pricing (four variants all
   merely invert the winner — eval §3 D4); the casualty-base rework (WO-D1
   Option 2 — held behind its written re-open condition, §5); ES-1b's
   blessed `CAVALRY_REGEN_BONUS_CAP` stands ("stop selling a capped-away
   building" is allowed; "exempt stables" is not — eval §7.4).

**Done when:** the preview quotes fed/costs/participates sentences whose
numbers equal the engine's own; one supply figure across preview/ledger/
panel/summary (test: assert equality across the four surfaces for an
allied-soil and an own-soil case, plus the `-1` sentinel case); a build chip
quotes the depot's terms; `BASELINE_SERIES` untouched (preview player-gated,
§2 C-8 — one call site; assert, then prove by subprocess run per the method
rule).

### Slice 9 — WO-8 the courting cap (est 0.5)

**Scope.** Per-TARGET throttle on vassal courting + the two absent guards the
loop head shows (§2 H-6): (a) at most ONE successful courting event per vassal
per turn, world-wide (first courtier in deterministic nation order wins; the
rest skip — their DP is not spent); (b) `nation == vassal_name` skips
(no self-courting); (c) a vassal of the SAME lord may not court its fellow
satellite. The 19-courts-in-one-tick −95 pile-on becomes bounded −5..−15.

**Done when:** the zero-order ambient reproduction shows ≤1 courting event per
vassal per turn and no self-court; `[VASSAL COURTING]` totals per tick bounded;
flip-attributed `BASELINE_SERIES` re-record (this is ambient AI behavior — the
one sanctioned re-record for this slice, flip = the cap OFF reproduces the
prior series).

### Slice 10 — WO-13 the enemy-direction gate (est 1)

**Scope.** A province name must stop silently resolving to an enemy marshal.
Gate `executor.py:433` AND the absorber `:370` (gating `:433` alone re-routes
16 of 17 events to `:370`); census over `:230` (the fifth seam). The ambient
AI hits this 17× in 40 turns — this slice **moves `BASELINE_SERIES`** and
takes the sanctioned re-record with a FOUR-ARM flip attribution (each gate
independently off must reproduce its share of the divergence).
**`Brunswick` is recorded as an uncloseable exact collision** (both a province
and a Prussian marshal at score 100 — `_plausible_name_typo` cannot
distinguish identical strings; the resolution order for exact collisions is
DOCUMENTED at the seam, not "fixed").

**Done when:** the AI stops resolving `Gascony → Ney`; the 30 boot-live
collapse pairs (measured count — the memo's 197 was wrong) refuse or
clarify in the player direction; four-arm flip attribution recorded;
`Brunswick` behavior documented + pinned as the known exception.

### Slice 11 — the typed-route residue (est 0.5)

**Scope — shrunk by G1** (WO-4 and most of WO-5 are absorbed by slice 7's
redirect): **WO-6** — the leading-filler hijack (`llm_client.py:1313-1315`:
the bare `"wait"`/`"stand by"` substring test sits ABOVE
retreat/move/scout/build/restrain/drill, §2 H-12; `no wait, Ney, retreat`
issues WAIT at 0.8 and *overruling the resulting WAIT objection with `trust`
made Ney CHARGE into Swabia* — the WO-6-wider amendment); **WO-7** — the
soft-stop wall (`main.py:2594` `else:` enclosing the CR-2 clarification
`:2660`, PARSE-NEG refusal `:2685`, Berthier recovery `:2749`, §2 H-13 — a
pending soft-stop must not replace all three recovery arms with an unrelated
shrug); and the mock parser's own diplomatic-tier substring hazards, whose
real map this spec's verification drew (§2 H-15):

- *"end the war on any terms"* parses as a WAR DECLARATION because the
  war-keyword list contains the substring `"war on "` (`llm_client.py:1018`)
  and is checked BEFORE the proposal keywords — the WO-6 class at the
  diplomatic tier. Post-redirect the player surface is safe (the head list
  catches war-ending AND war-declaring sentence heads); the mock chain is
  hardened anyway for the driver/HTTP path: peace-intent phrasings
  (`end the war`, `stop the war`, `I want peace`) map to the proposal arm or
  refuse honestly — never to `diplomatic_declare_war`.
- **"break the alliance with Austria" PROPOSES an alliance** (§4 H-b —
  `_break_keywords` `:1003-1008` are treaty-phrasings only; the addressed
  form falls into the proposal arm and `extract_proposal_type` reads the
  word "alliance" as the thing to CREATE). One-line hardening: add
  `break alliance` / `end the alliance` to `_break_keywords`.
- The bare nation-less forms (`sue for peace`, `make peace`) keep their
  honest FINAL-21 target ask (`llm_client.py:2041`) — that surface was
  already correct; the eval's BUG row conflated it with the declare-war ask
  and is corrected by this spec.

WO-6 carries its own before/after corpus eval (its fix reorders the mock
chain — the corpus is the regression net).

**Done when:** `no wait, Ney, retreat` retreats (or clarifies) — never WAITs;
parse-failure recovery survives a pending soft-stop; `end the war on any
terms` never reaches `diplomatic_declare_war` in any mode; `break the
alliance with Austria` never proposes one; corpus green with the deltas
reviewed row-by-row.

### Slice 12 — the copy sweep (est 1)

**Scope.** WO-9 (the two conquest producers stamp `captured_from` —
`old_controller` is live three lines above each, §2 D-13 — so PT-E5's
carve-out can fire and an AI capture of the player's own province appears in
the enemy phase), WO-10 (the ratio sentence qualifies its estimate; a
LAST_KNOWN arm in `_format_army_strength` ends the exact-aggregate leak, §2
D-14), WO-12 (the under-capacity concentration tax narrates as concentration,
not starvation — both surfaces, §2 D-12), WO-15 (a prisoner is named a
prisoner, not "(dead)", §2 D-11), **WO-16** (the mauled sentence publishes
the proportion that earned the word — *"a quarter of his corps"* — and gains
the absolute floor: `OWN_MAULED_MIN_CASUALTIES = 500`, in-band tunable,
**recorded as a conscious re-open of the playtest's own killed claim #4**
(eval §7.7) with the written dissent: if 500 is tuned twice, take the
fraction-of-national-strength form instead), and **the rout-repetition
variant** (§4 N-8b: *"Archduke John broken and flees"* seven times across a
campaign is literally true and materially empty — the enemy-rout sentence
gains a repeat-aware variant riding the existing serialized `battle_counts`
rotation seam (XR-5), copy only, no new fields).

**Done when:** each row's measured reproduction reads correctly; zero
mechanics diffs (copy/event-field additions only; the `captured_from` stamp is
additive on two events already logged). **Also in the sweep:** the two
legacy-roster Specify-lists at `diplomatic_executor.py:2029`/`:2996`
(*"Britain, Prussia, Austria, or Saxony"* — pre-cutover copy) derive from the
live world.

> **ADDED August 21, 2026 — WO-D10's copy half.** The commissioning refusal
> *"No soil remains on which X could raise his corps"* is FALSE on the map an
> exiled player is looking at: `find_spawn_region` considers only the capital
> and `nation_starting_regions`, so a player holding a dozen rich conquests is
> told there is no soil. The MECHANIC (spawn at the richest held province) is
> carried to the Victory & Objectives Pass — the exile game only matters once
> losing is a state the game recognizes — but the sentence is a copy bug and
> belongs here: it must name the actual gate (HOME soil), not assert an
> absence the player can see is untrue. Carry contract:
> `DESIGN_REFINEMENT.md` §WO-D7..D11.

### Slice 13 — WO-17 "The Corridor Has a Direction" (est 0.5–1) — **this spec's addition, P1**

**The defect (found by this session's loop hunt; permission arm re-verified
by hand).** WIN-D3's evacuation grant is **pair-scoped and direction-less**:
`has_evacuation_grant(world, marshal_nation, region_controller)`
(`withdrawal.py:133-149`) is a bare `(pair_key → expiry)` compare consumed by
the ONE arm at `can_enter_territory` (`diplomacy.py:9452-9455`) — no marshal
identity, no direction, no stranded check. The grant opens on **any WAR →
non-WAR edge including ARMISTICE** (`diplomacy.py:2815-2817`; pinned by
`test_win_d3_road_home.py:600-607`). So: park one corps deep on enemy soil
(depth sets the duration — up to `EVACUATION_MAX_TURNS = 12`), sign a 1-DP
armistice, and march FRESH corps from France into enemy sovereign territory
for the length of the truce; walked-in corps register as "stranded"
(`is_stranded`, `withdrawal.py:253-278`), which **holds the corridor open**
(`:695-698`); let the armistice collapse (war auto-resumes at expiry,
`diplomacy.py:9880-9893`, costing nothing) and the new war opens with the
army already standing beside Vienna. The enemy legally cannot contest the
approach — attack paths gate on `is_at_war`. Compounding it, **the player has
no truce floor**: `PAIR_EXIT_TRUCE_FLOOR_TURNS = 8` is written only by the
exhausted-pair processor, which SKIPS any pair containing the player
(`settlement_third_party.py:453`), and `set_diplomatic_state` POPS the
armistice cooldown whenever the pair leaves ARMISTICE (`diplomacy.py:
2839-2845`) — so the AI faces an 8-turn floor the player never does. GR5
saves the mirror: the AI's only corridor consumer is P1.2, gated on
`is_road_home_order` (`enemy_ai.py:1753-1762`) — it can only walk home,
which is exactly the constraint the player is missing.

**Fix contract — zero new fields, one seam.** The permission arm gains a
direction term: a marshal whose CURRENT location lies in its own nation's
home zone (an O(1) controller/home check — the arm is inside pathfinding
loops, GR8) may NOT use the grant to enter the counterpart's territory. A
stranded corps outside its home zone keeps full transit (the corridor's whole
purpose); the moment it reaches the body of its own realm, the grant is spent
for it — which is the spec's own §4.1 predicate ("can he reach the body of
his own realm at all") applied to the entry side.

**Done when:** during a truce, a corps standing on French home soil is
refused entry to enemy sovereign territory (falsifiable negative — the
Trojan march); a genuinely stranded corps still routes home through the same
provinces; the corridor still retires when nobody is stranded; the five §3.4
never-do pins byte-identical; `test_win_d3_road_home.py:243`'s pair-level
`can_enter_territory` assertion is REWRITTEN to the direction-aware form —
a **conscious pin flip, recorded here**; `BASELINE_SERIES` byte-identity
proven by subprocess (P1.2 only ever walks home, so ambient should not move —
prove it).

**Consciously NOT built:** a player-side re-declaration time floor. The
churn half of the hunt finding (peace → re-declare with the campaign ledger
demobilized) is **PT-J2's recorded design** — the ledger demobilizes at the
`set_diplomatic_state` chokepoint by gate ruling, and re-declaration is
priced in DP, −30 relations, threat, and the CA9 war-age acceptance penalty.
Whether the PLAYER should also face a time floor after a truce is a design
question, not a bug — filed as **WO-D8** (§4) for a future diplomacy gate,
not built here.

> **✅ LANDED August 21, 2026 — landing record.** The permission arm is
> direction-aware: `can_enter_territory` gains `mover_location` (the moving
> corps's CURRENT standing province), fed to `has_evacuation_grant`, whose
> new direction term denies the grant to any mover that is not genuinely
> stranded where it stands. **One recorded amendment to this contract's
> letter, endorsed by its own closing sentence:** the term is the full
> stranded predicate (`withdrawal.is_stranded_at` — the SAME function that
> decides who receives a road-home order, factored to a location form so
> the two consumers cannot drift), NOT the bare home-zone membership the
> contract's first sentence describes and not a bare controller compare —
> because (a) a controller compare would have stranded the measured
> Volhynia corps forever (own-controlled but DISCONNECTED soil must keep
> transit), and (b) bare zone membership leaves two live Trojan variants
> the stranded form closes: launching from an ALLY's border province, and
> launching from a third party's at-war soil (both pinned in
> `TestTheDirectionTerm`). "Can he reach the body of his own realm at all,
> applied to the entry side" IS the stranded predicate. **The O(1)/GR8
> obligation is honored by memoisation, not approximation:** the verdict is
> cached per (nation, location) in the transient, never-serialized
> `world._evac_direction_cache`, flushed at the
> `invalidate_bloc_members_cache` chokepoint (the NA-0 idiom — region
> control and war/peace geometry both reach it) plus a per-turn key, so
> the flood fill runs once per board state, not once per pathfinding node
> — and the same-turn-as-the-peace case (a cache warmed at war says the
> enclave is CONNECTED home through war-passable soil) is pinned as its
> own test. **Threading:** every relocation seam names its mover —
> `_execute_move` (player, strategic steps, and AI through the shared
> executor, GR5), both pathfinders via `_region_passable_for` (with
> `passable_for` set, `start` IS the mover — every caller passes
> marshal.location, census-PINNED as of the review round), `_can_ai_move_to`
> (origin, already passed at all 18 call sites — the record first said 19,
> a grep that counted the def; corrected by the review round), the
> reckless-cavalry auto-move, the
> combat-executor approach move, and the S5-D2/PF-8 issuance-honesty and
> reroute checks. `mover_location=None` keeps the legacy pair-level answer
> BY DESIGN (the audited nation-level consumer: war_council's anchor
> derivation, which relocates nobody), and a **census pin** fails on any
> new bare call so the WO-17 class cannot recur silently. The Trojan
> refusal states its terms at the seam ("the corridor grants safe passage
> HOME to stranded corps, not entry") with the PF-8 structured flags
> unchanged. Flip lever `CORRIDOR_DIRECTION_ACTIVE`; the control arm
> reproduces the filed exploit with it off. **Done-when, measured:** the
> Trojan march refused on ARMISTICE and PEACE; Davout walks home through
> the exact provinces Ney is refused, step by step through the executor;
> the pathfinder pins the asymmetry (corridor exists Volhynia→home, none
> home→Volhynia); arrival spends the grant per-corps while the other
> signatory's walker keeps his; retirement unchanged; **all five §3.4
> pins byte-identical** (`test_win_d3_road_home.py` 43/43 green, zero
> edits except the sanctioned flip); **the `:243` pin flip taken as
> written** — pin 4's liveness half now asserts the direction-aware form
> (alive for the stranded corps, dead for a corps at home), its death
> half untouched; **`BASELINE_SERIES` byte-identical WITHOUT re-record,
> proven by the real subprocess run** (the ambient corridor's only
> walkers are stranded by construction — the P1.2 rung — so the
> direction term is dormant there, exactly as this contract predicted);
> M1–M7 byte-identical. WO-D8 untouched per never-do 21.
> **16-mutation sweep: 15 killed, 1 proven EQUIVALENT** — removing
> `is_stranded_at`'s home early-return is a semantic no-op because
> `distance_home_from` independently returns 0 for a home location (the
> redundancy is structural, inherited verbatim from WIN-D3's original
> predicate; every load-bearing clause — the direction condition, both
> its inversions, the wrong-subject swap, the cache key, both cache
> flushes, all the seam threadings and all three review-round gates —
> dies to a named test).
> `tests/test_wo_slice13_corridor_direction.py` (25).
>
> **THE REVIEW ROUND (same day) — a 42-agent find→2-refuter fleet on the
> committed diff took 18 raw findings to 8 confirmed, and the confirmed
> set changed the slice.** Headline **P1 (two lenses converged, all four
> refuters reproduced it independently): the Trojan march survived one
> verb over.** `_execute_general_attack` CASE 2 — the bare typed `attack`
> with nobody in range — walked the closest corps one step along an
> OMNISCIENT `find_path` and relocated it via bare `move_to` with NO
> movement-law check at all (only the naval gate), so a fresh corps
> stepped onto truce-partner sovereign soil where the direction term's own
> stranded predicate would then have granted it deeper corridor transit —
> the fix's predicate amplifying the entry it never saw. Two more
> movement-law holes of the same class: the W6-1 **explicit-destination
> retreat** accepted a PEACE/ARMISTICE controller the PC15-D1 doctrine
> scan directly above it refuses (a typed "retreat to <truce province>"
> stood a corps on closed sovereign soil), and the **direct 2-tile cavalry
> branch** checked its connector only for enemies and the naval gate
> (transit across truce soil, and a seeding vector into the nation's own
> cut-off enclave that would re-arm the corridor for a corps the war never
> stranded). **All three are PRE-EXISTING seams this slice's census pin
> was structurally blind to — they contain no `can_enter_territory` call,
> and a census of calls cannot see an absent call (recorded as the pin's
> known limit). All three now carry the movement law with the mover
> threaded** (the general-attack hop refuses with the closed-frontier
> reason; the retreat SUBSTITUTES with the reason per IGR-A3; the cavalry
> connector refuses and names the controller), each with a control arm
> proving the at-war march survives (never-do 20) and a mutation each.
> Plus: **[F3, P2]** `open_evacuation_corridor` routed the road-home
> orders BEFORE `set_diplomatic_state`'s own cache flush at the end of
> the function, so a direction verdict warmed at war denied the
> freshly-stranded corps its corridor during issuance — measured, the
> treaty's order shipped with an EMPTY path (self-healing on the first
> strategic tick, but the beat promised a road with no route); the opener
> and the revoker now flush first. **[F6]** `find_weighted_path`'s
> threading — the router the typed multi-hop move actually uses — had
> zero coverage; the pathfinder pin now runs both routers. **[F7]** the
> record's "19 call sites" corrected to 18 in place (a grep that counted
> the def). **[F8]** the "census-pinned" start-is-the-mover comment
> claimed a pin that did not exist; it exists now
> (`test_every_passable_for_pathfind_starts_at_the_mover`). The ten
> REFUTED findings incl. the pre-positioned-corps omnidirectional-transit
> observation (the slice's own recorded full-transit design, bounded by
> the internment clock) and a naval-blind-stranded-predicate claim
> (unreachable for every marshal-fielding nation on the shipped map).
> `BASELINE_SERIES` re-proven byte-identical by subprocess AFTER the
> three gates (the cavalry connector is AI-reachable — proven dormant
> ambient, not assumed); M1–M7 byte-identical.

### Slice 14 — WO-18 + WO-19 "The Clock and the Flag" (est 0.5) — **this spec's addition**

**WO-18 (P2) — pension churn: pay one turn in three, never erode.** The
rente bill reads the LIVE pension at income time (`world_state.py:5376-5379`)
while the erosion reconcile runs after income with a full grace reset on any
met turn (`:5908-5946`: shortfall 0 → `expectation_grace_turn = -1`; first
unmet turn starts the clock; erosion only after `GRACE_TURNS = 2`). Neither
`_execute_grant_pension` (`economy_executor.py:1174-1292`) nor
`_execute_revoke_pension` (`:1294-1373`) carries any churn memory — so
grant / revoke / revoke / re-grant pays `ceil(1.5 × face)` on one turn of
three and never reaches the erosion branch, saving ~300g/turn per capped
marshal with zero trust bleed, while the revoke copy still promises *"unmet
expectation frays loyalty after its grace expires."* **Fix contract:** the
grace clock keys on unmet-turn COUNT, not on "one met turn resets
everything" — a marshal met on turn N and unmet on N+1..N+2 erodes at N+3
regardless of interleaved grant/revoke (acceptance test at exactly that
shape). The blessed `GRACE_TURNS = 2` stands; only the reset rule changes.

**WO-19 (P2) — the sacked flag re-arms on any hand-change.** `plunder_yield`'s
own docstring promises the repeat-sack guard holds *"until stability recovers
past 50 … ≥ 9 unguarded turns"* (`world_state.py:325-327`, clear at
`:6122-6123`) — but three sites clear `region.plundered` in ONE turn on any
change of hands (`combat_executor.py:7639-7643` `_apply_secure`, the AI
secure branch `world_state.py:3966-3969`, player own-soil recapture
`:3928-3933`). Abandon a sacked province, let the AI walk in and secure it,
retake it — the plunder prompt quotes the FULL yield again (`income × 4`,
no war-damage discount on this path). IGR-X6 covered only re-sack while the
flag stands. **Fix contract:** `plundered` survives changes of hands; the
documented stability-50 clear becomes the ONLY clear. Acceptance: the
abandon→AI-secures→retake cycle quotes and pays 0 while the flag stands;
the docstring's promise becomes true; IGR-E's dissent counter is untouched
(this changes when the flag CLEARS, never the multiplier).

**Harness impact:** WO-19 touches the AI-secure path's flag write → run the
M1–M7 harness and prove `BASELINE_SERIES` by subprocess (threat accrues on
conquest, not the flag, so it should hold — prove it).

### Slice 15 — "The Capture Question Holds" (est 1) — **this spec's addition**

**One lifecycle, five holes (WO-22/26/27/29/30).** The single-slot
`pending_capture_choice` can be created, crossed, clobbered, misapplied and
dropped without the player ever being told:

1. **WO-22 (P1, hand-verified):** the auto-end-turn defer at
   `executor.py:1966` checks only `dialogue_manager.has_current_turn_offers()`
   — never `pending_capture_choice` — while the typed `end turn` path BLOCKS
   on it (`executor.py:597-602`). A last-AP attack that captures auto-advances
   across the unanswered question; the enemy phase can retake the province
   and the answer then dies on the holder-re-validation lapse — the plunder
   gold (`income × 4`) silently forfeited. **Fix:** the auto-advance defers
   on `pending_capture_choice` exactly as it defers on unanswered envoys,
   with the same explicit notice.
2. **WO-26 (P2):** the attack-capture site (`combat_executor.py:7853`) and
   the occupation-completion site (`world_state.py:3937-3938`) are BARE
   assignments to the single slot — only the move path carries the PF-3
   save/restore guard (`movement_executor.py:546-551/589`, pinned by
   `test_pf3_uncontested_occupation.py:224-248`). Reachable inside
   multi-marshal strategic loops (`_strategic_execution` bypasses the
   executor's block). The first province's unanswered choice is silently
   lost — it never runs `_apply_secure`, never logs `region_captured`, never
   mounts the W6-8 estate stage. **Fix:** the same guard at all three
   producers (or a queue — but the single-slot + guard is the shipped
   pattern; extend it).
3. **WO-27 (P3):** the dotation prune (`world_state.py:5891-5896`) lacks the
   `_capture_choice_pending` carve-out its three siblings carry
   (`dotation.py:325/345/405`) — an estate question that crosses the
   boundary is pruned, and answering *respect* then becomes a paid no-op
   (`apply_estate_respect` never re-adds to `dotation_regions`; the +5
   acceptance term never fires). **Fix:** the fourth carve-out.
4. **WO-29 (P3):** the TYPED capture answer never carries `dialogue_id`
   (`main.py:2263-2264` vs the endpoint's `:3407-3408`) so the W6-0 stale
   guard is inert on the typed path — composed with WO-26, a typed `plunder`
   for province X can apply to province Y. **Fix:** thread it.
5. **WO-30 (P3):** `/load` re-attaches popups only for
   `PopupQueue.RESPONSE_KEYS`, which has no capture entry
   (`main.py:3947-3971`; `main.gd:1421-1422` gates the modal on the key) —
   a save carrying a pending capture question loads with no visible modal
   (self-healing after one refused command, but the player is told nothing).
   **Fix:** the capture passthrough at load; and the dead
   `PopupQueue.to_dict/from_dict` noted as the structural cause (the queue
   round-trips via hand-enumerated keys — add the missing entry AND a census
   pin so the next new slot cannot silently drop).

**Done when:** a last-AP capture defers the auto-advance with the notice; a
second capture in the same loop cannot clobber an unanswered first; the
estate *respect* answer is never a paid no-op across a turn boundary; a
typed answer with a stale id refuses; a loaded save re-raises the capture
modal; the PF-3 pin stays green.

> **✅ LANDED August 21, 2026 — landing record.** All five rows closed, plus
> one found while building. Tests =
> `tests/test_wo_slice15_capture_question_holds.py` (31); mutation sweep
> `tools/_sweep_wo15.json` — **27 mutations, 27 killed** after two INERT
> pins were found and replaced (both were the tests' fault, not the code's:
> the secure-effects comparison could not see a change made to the ONE
> implementation both of its arms call, and the non-draining pin queued its
> popup in a world that `/load` then threw away). Suite **18,328/3**, ruff
> clean, Godot parse harness EXIT=0 (47 scripts), war-room boot smoke 0
> `SCRIPT ERROR`.
>
> **A verify → refute fleet ran BEFORE the build** (5 defects × verifier +
> refuter, 4 census sweeps, 1 synthesis) and it earned its cost twice by
> **contradicting the contract above**, not by confirming it:
>
> - **WO-30's prescribed fix is wrong and was not built.** "Add the capture
>   entry to `PopupQueue.RESPONSE_KEYS`" is a no-op in the arm that matters
>   — both consumers write `None`, and `pop_highest` iterates
>   `PRIORITY_ORDER` against a queue this field never enters. Its non-no-op
>   variants are worse: one stamps `capture_data: None` on every response,
>   another has `pop_highest` **destroy** the question along with the
>   `executor.py` block that protects it. And the row omitted the half that
>   makes the fix visible at all: `_apply_world_swap_response` consults no
>   route table, so a backend passthrough alone renders nothing. Built
>   instead: the two explicit keys at the tail of `/load` (the shape
>   `/capture_choice` already returns) **and** the client raise, through the
>   same predicate/route pair the command path uses so the two cannot drift.
> - **WO-29's prescribed fix is unbuildable.** There is no `dialogue_id` to
>   thread: `CommandRequest` has no such field, the terminal body is
>   `{"command": …}`, the client's only capture id is written when the
>   MODAL renders — which disables the command line, so the two states are
>   mutually exclusive — and server-side the only candidate is the pending
>   question's own id, which would make the guard compare a value with
>   itself. Forcing it would be worse than nothing: after a world swap the
>   client's id is `-1` or one minted in the previous world, and a stale
>   positive arms the guard against the wrong question — a permanent
>   refusal loop that the pending-choice block turns into a soft-lock.
>   Built instead: identity by **content**, the documented house pattern for
>   typed answers (`diplomatic_executor.py:3286-3296`) — `plunder
>   <province>` binds the answer to that province, and a wrong name is
>   refused with the real question restated. The composed X→Y consequence
>   the row describes is closed twice over anyway, by WO-26 and WO-22.
>
> **The build, seam by seam.** `world_state.apply_secure_effects` (hoisted
> verbatim out of `combat_executor._apply_secure`, which now delegates) and
> `world_state.mount_or_auto_secure_capture` — the ONE writer for a fresh
> capture. The rule needs no strategic flag: **an occupied slot cannot be
> asked again.** A direct player capture always finds it empty (the
> executor blocks every command while a question stands), so the
> interactive prompt is untouched; only an automated capture arriving on
> top of an unanswered one is decided here, and it is decided the
> conservative way — secure, no windfall. The march policy (IGR-X5's
> "auto-secure even on a free slot") stays a caller-passed `auto_secure`
> flag, and the move path's local `_prior_choice` save/restore is
> **deleted** rather than copied — the guard is structural now, at all
> three producers. WO-22 = one helper, `_auto_end_turn_defer_notice`,
> stage-agnostic (it reads the FIELD, not `stage`), speaking through the
> existing stage-aware restatement so the price travels with it, and
> deliberately WITHOUT the typed block's `_strategic_execution` carve-out —
> a strategic hop costs no AP so it cannot reach the branch, and importing
> the exemption would be a condition that never fires today and re-opens
> WO-22 the day that changes. WO-27 = the fourth carve-out, with
> `_capture_choice_pending` renamed public.
>
> **Corrections to the filed rows, on the record:**
> - WO-22's trigger is **both** AP pools drained, not "the last AP", and it
>   has **two** producers (attack and a typed move) — a fix or test covering
>   only `attack` leaves `move` broken.
> - WO-22's "the plunder gold is silently forfeited" is **conditional**,
>   not certain: `handle_capture_choice` lapses only if the province was
>   retaken. Held, it pays in full next turn. The reliable damage is that
>   the auto-advance re-attached the now-stale question and the client
>   popped it — a priced offer that may already be void.
> - WO-27 has **four** siblings carrying the carve-out, not three
>   (`vassal.py:1340` was unnamed), and the prune was the only live-claim
>   test in the codebase missing it. Its premise is understated: the
>   strongest path needs **no turn boundary and no player negligence** —
>   `_process_tactical_states` completes an occupation and
>   `_process_dotation_state` runs later in the *same*
>   `_advance_turn_internal`. And its stated consequence is the smaller
>   half: because `find_enemy_estate_holder` reads `dotation_regions` raw,
>   a pruned estate means the W6-8 confiscate/respect question **is never
>   asked at all** — no windfall, no goodwill, an `estate_lost` fired in its
>   place. Where the estate stage HAD already mounted, "the +5 never fires"
>   is also wrong: it fires, and `prune_respected_estates` revokes it on the
>   next advance. Paid for, and gone. **Re-filed P3 → P2.**
> - WO-30's cited line numbers point at `/new_game`'s autosave tail and at
>   a parser keyword constant; the real seams are `/load` and
>   `main.gd:1893`. The client gate reads **two** keys, which is exactly why
>   a one-attr→one-key `RESPONSE_KEYS` entry could never have worked.
>
> **`BASELINE_SERIES` re-recorded ONCE — index [40] only, 13 → 23 — and the
> cause was proved by experiment, not argued.** The verify fleet PREDICTED
> the harness could not move (every changed path is player-nation gated and
> France issues no orders on the ambient board). It moved anyway, which is
> the whole argument for measuring. France IS `world.player_nation` even
> with nobody at the keyboard, so a French capture takes the PLAYER branch:
> instrumented, it fires three times — Ney takes **Swabia** and its 600g
> question stands unanswered for the rest of the run, then **Moravia**
> (turn 18) and **Vienna** (turn 21) arrive on top of it. Those two were
> bare writes; the provinces kept the control flip and never ran secure, so
> France stormed Vienna and the engine forgot to garrison it. Five arms:
> world_state+dotation+vassal alone reproduces 13; adding combat_executor
> gives 23; and **the full tree with the occupancy arm forced False
> reproduces 13 verbatim** — so the sole lever is the occupancy rule, and
> the `apply_secure_effects` hoist, the WO-22 defer, the WO-27 carve-out
> and the move path's `auto_secure` are all inert on that board. M1–M7
> byte-identical without re-record. (A probe of `event_log` reports ZERO of
> those `region_captured` rows — the 500-cap had evicted them. The IGR-B
> trap again: spy on `log_event` at write time, not the log.)
>
> **Found in passing and FIXED — WO-34:** a player naval expedition landing
> on undefended enemy soil captures through the shared pipeline, which
> mounts the question in world state — and the landing result copied only
> `capture_choice` / `capture_message` / `region_captured`, never the two
> keys `main.gd` gates the modal on. The expedition asked a question the
> player was never shown; they found out by having their next order
> refused. Same two keys, same priced sentence, as every other capture
> route.
>
> **Found in passing and ROUTED, not folded in:** WO-35 (`pending_objection`
> and `pending_interrupt` survive a save and raise nothing at load — and the
> objection route requires `success == true` while its block returns
> `success: False`, so that modal is unreachable by construction), WO-36
> (`redemption_event`, same shape), and **WO-D11** — a mid-march
> auto-secure strips an enemy marshal's estate with no windfall and no
> goodwill. The last is a comment correction as much as a design row:
> `movement_executor`'s own comment claimed the holder "simply keeps his
> title — indistinguishable from 'respect' minus the goodwill entry", and
> that was never true. Both that comment and
> `mount_or_auto_secure_capture`'s docstring now say what actually happens.
>
> **The census pin** ("the next new slot cannot silently drop") is keyed on
> the CLIENT's own modal route table, not on an attribute-name prefix — the
> route table is what decides whether a piece of blocking state is ever
> seen, and it is the thing a future slice edits. Every response key any
> modal route reads must be classified: queue-delivered, explicitly
> re-attached at `/load`, transient by design, or a known gap with a filed
> row. Adding a route reds it; so does removing `pending_capture_choice`
> from the re-attached set. Both mutations were run.
>
> **Two adjacent things this slice does NOT close, stated so nobody reads
> them as closed:** the post-advance re-attach in `executor.py` can still
> surface a question invalidated later in the same turn resolution (a
> pre-existing shape, one seam over), and `world_state`'s auto-charge
> conquest assigns a controller bare — it captures with no question, no
> secure effects and no `region_captured` row, ever. The producer guard
> covers every path that ASKS, not every path that captures; that one
> belongs to slice 17.
>
> **Visual sign-off — EVIDENCE CAPTURED August 21, 2026; ✅ USER SIGN-OFF
> GIVEN August 22, 2026** (the frame was put in front of the user and
> signed). `docs/audits/WO_SIGNOFF_3_LOAD_CAPTURE_2026_08_21.png`, taken in
> the REAL `main.tscn` against a sandboxed backend on `SOVEREIGN_PORT=8006`
> by the committed harness `tools/wo_signoff_screenshot.gd`. It drives the
> client's OWN entry point — `_apply_world_swap_response`, which is exactly
> what `/load` returns to — rather than rebuilding its effect, so the
> evidence is of the shipped path. Shown: *REGION CAPTURED! / Ney has taken
> Swabia / PLUNDER (+600 gold, buildings burned, stability 10) / SECURE*,
> raised over the terminal with the load text behind it. **A captured
> screenshot is not a sign-off; the user's eye is.**
>
> **Method note, since this row keeps earning it:** the refuters read the
> working tree while the lead was editing it, and two reported "already
> fixed" for work committed nowhere. Nothing was lost, but a fleet pointed
> at a moving tree spends part of its budget re-discovering the author's
> own diff. Point the next one at a committed SHA.

### Slice 16 — "The Objection Channel Pays Honestly" (est 0.5) — **this spec's addition**

**WO-21 (P1, hand-verified).** The strategic-objection "trust" arm credits
`modify_trust(v2_trust_gain)` BEFORE checking that a preferred action exists
(`strategic_executor.py:1627-1628` — credit; `:1630-1635` — the bail returns
`success: False, variable_action_cost: 0`): trust kept, nothing paid,
nothing executed. And the relationship-SUPPORT objection's trust option is
built with `"action": "cancel"` (`:994-996`) — an action id the
post-objection dispatch has NO arm for (`meta_executor.py` tail: `Unknown
action: cancel`; AP charges only on success). Player-visible: press *"Trust:
Cancel the SUPPORT order"* → +2..+12 trust, 0 AP, the SUPPORT order still
standing, and a raw internal error. **Fix:** (a) the trust credit moves
AFTER the preferred-action validation (credit only what executes — the same
shown=applied law every other channel obeys); (b) the SUPPORT-objection's
preferred arm routes to a REAL cancel (the `_execute_cancel` path), pinned
by a test that presses the arm and asserts the order is gone.

**WO-23 (P2, hand-verified).** `save_manager.py:191` wipes
`objection_popups_this_turn` on every LOAD while `from_dict` restores it —
a mid-turn save/load refreshes the per-turn objection budget, the only live
limiter on the +3..+12-per-popup trust channel (there is no per-marshal
cooldown; the global cap constant is dead code read only by a caller-less
function). **Fix:** stop wiping it (align with `from_dict`, exactly as the
adjacent `diplomatic_trust_applied` comment already does for the same
budget-refresh reason). The DESIGN half — whether the objection economy
needs a per-marshal cooldown and whether the authority +1-per-answer band
(`authority.py:119-120` vs the penalty at `:309-313`) is farmable by
alternating compromise/trust — is **WO-D9**, a gate question, not built
here.

**Done when:** the trust arm on a preferred-less objection credits nothing;
pressing the SUPPORT-cancel arm cancels; a save/load round-trip preserves
`objection_popups_this_turn`; existing objection pins green.

> **✅ LANDED August 21, 2026 — landing record.** Both rows closed, plus one
> found while building. Tests =
> `tests/test_wo_slice16_objection_pays_honestly.py` (19); mutation sweep
> `tools/_sweep_wo16.json` — **17 mutations, 17 killed** after one INERT pin
> was found and replaced. Suite **18,347/3**, ruff clean. Backend only, no
> `.gd`. **M1–M7 and `BASELINE_SERIES` byte-identical, MEASURED by real
> subprocess run, not predicted** — after slice 15, that distinction is the
> row's own rule.
>
> **The four arms, reproduced by hand end to end BEFORE the build, on the
> shipped tree:**
>
> | press | trust | AP | executed | message |
> |---|---|---|---|---|
> | 2-option objection, "trust" | **+8** | 0 | nothing | `Unknown action: None` |
> | 2-option objection, "compromise" | **+3** | 0 | nothing | `No compromise available` |
> | SUPPORT-relationship, "trust" | **+8** | 0 | nothing | `Unknown action: cancel` |
> | trust → preferred `drill` | +8 | **2** (button quoted 1) | yes | reported `cost: 1` |
>
> **The root is not the credit order the row names.** `preferred_action` was
> lifted by INDEX (`options[1]`, and compromise from `options[2]`) out of a
> list whose middle entry is optional — `_build_strategic_options` appends
> the preferred entry only `if preferred` — while `objection_dialog.gd` reads
> the same list by TYPE. A marshal who proposes no alternative produced
> `[proceed, compromise]`, so the backend handed the COMPROMISE dict to the
> trust arm and found nothing at all for the compromise arm, while the client
> rendered both buttons. Two implementations of one rule with only one
> maintained: the CA9 through-line, again. The lift is now by type, reusing
> the `_quoted` idiom that already existed three lines below it.
>
> **Corrections to the filed row, on the record:**
> - **The bail the row names is UNREACHABLE.** `len(options) >= 2` always
>   (proceed is unconditional and every producer supplies a truthy preferred
>   OR a truthy compromise), so `options[1]` was never falsy and
>   `"No preferred action available"` never fired. The live failure is one
>   line lower. The row's outcome is right and its mechanism is wrong.
> - **"the SUPPORT order still standing" is REFUTED.** The order does not
>   exist yet: the objection returns from `_execute_strategic_command`
>   BEFORE `StrategicOrder` is constructed. So the fix is a DECLINE TO
>   ISSUE, not a cancel — and routing it through `_execute_cancel`, as the
>   row asks, would either hit that function's graceful no-op or cancel an
>   UNRELATED standing order and charge its own −3 trust. (The lead's own
>   probe appeared to show an order surviving; it had planted a prior order
>   by hand and was therefore artificial. The refuter caught it.)
> - **The band is +2..+12 in the table and +2..+5 in play** on this arm: the
>   relationship check caps at STRONG, and the authored boot tiers put
>   Davout at +2, Bernadotte +3, Murat +5. The +12 cell needs HOSTILE trust
>   AND EXTREME concern, which this arm cannot produce.
> - **"repeatable" means ≤1 free press per marshal per turn** — the question
>   is cleared before re-execution, and re-arming is capped by
>   `objection_popups_this_turn`. Which is precisely the budget WO-23's
>   save/load wipe refreshed: **the two halves of this slice are the same
>   exploit seen from both ends**, and they are pinned together so a later
>   slice cannot remove one and leave the other looking harmless.
> - **WO-23's "a caller-less function" is TWO functions**
>   (`evaluate_order`, `get_major_objections_remaining`), neither with a
>   production caller. And the sharp corroboration the row missed: the DEAD
>   V1 counter `major_objections_this_turn` was faithfully preserved across
>   load while the LIVE budget was the one wiped.
>
> **Two things the row never named, both found by the fleet and both fixed:**
> - a THIRD reachable credit-for-nothing, `"No safe path available"`, sitting
>   below the compromise credit;
> - **the strategic route had NO choice validation at all.** It returns from
>   `handle_objection_response` before the tactical route's `valid_choices`
>   guard — the guard that already refuses an impossible answer in
>   Berthier's voice ("'compromise' is not one of the roads open"). The
>   tactical route knew how to reject the very press that broke this one.
>   The guard is now mirrored here, sited ABOVE the clear: a refusal that
>   also cleared the question would strand the player with no valid arm.
>
> **WO-37 (new, hand-verified): the trust arm charged 1 AP twice.**
> `_ap_consumed_by_execute` — the flag the endpoint's own comment relies on
> to avoid exactly this — is read once and **set nowhere**. Measured: a
> preferred `drill` took 2 AP against a button quoting 1, a preferred
> `fortify` that auto-shifts stance took 3, and `action_info` reported 1
> throughout. There were TWO double-charging consumers, not one (the
> endpoint tail and `executor.execute`), so the fix is not to set the flag
> but to stop the inner charge: `_execute_post_objection` gains an explicit
> `charge_ap` parameter, the trust arm passes False, and every arm is now
> charged once at the price its button quoted. The dead flag is deleted
> rather than revived.
>
> **Two existing pins were VACUOUS and are de-vacuated** — and they are
> exactly the two that should have caught WO-37.
> `test_preferred_costs_1_ap` and `test_preferred_trust_plus_12` both wrapped
> their assertion in `if result.get("success"):` and passed the preferred
> action id `"stance"`, which the dispatch has no arm for (`stance_change`
> is the real id), so neither body ever ran. The trust one also asserted a
> flat +12 that is only the HOSTILE+EXTREME cell of a tier table; it now
> pins the LAW (the credit is the value the objection carries, and it lands
> only because the action executed) rather than a number that was never
> general. `test_objection_popups_cleared_on_load` is CONSCIOUSLY FLIPPED to
> `..._survives_load`, modelled on its own sibling
> `test_attacks_this_turn_survives_load`, flipped in Aug 2026 for the
> identical reason.
>
> **Deliberately NOT built:** the authority band's farmability
> (alternating compromise/trust against `record_response`) stays **WO-D9**,
> a gate question. And `MAX_OBJECTION_POPUPS_PER_TURN` stays production-dead:
> reviving it would change objection frequency game-wide and is a design
> decision, not a bug fix.
>
> **Method:** this fleet was pointed at a COMMITTED SHA (`5684ef1`) with a
> clean tree, which is the correction slice 15's record asked for — and it
> paid immediately. Both refuters failed to break their findings, and the
> WO-21 refuter caught the one thing the lead had wrong (the artificial
> "order still standing" probe) before it reached the code. The lead then
> built while the synthesis agent was still running, so the synthesis
> reports a dirty tree; nothing was lost, but the discipline is *all*
> reading agents done, not most.

### Slice 17 — "The Frontier Halts the Charge" (est 1) — **this spec's addition**

**The autonomous layer can still relocate and narrate illegally
(WO-24/25/28/31; hunt-verified at the quoted seams, re-reproduce at build).**
PC15-D1's neutrality filter is correct at TARGET SELECTION
(`jealousy.py:3507-3523`, the Stage-E frontier bias is only a sort key) —
the holes are one layer down:

1. **WO-24 (P2):** the charge/auto-charge ADVANCE relocates the victor with
   only `_naval_advance_allowed` — no `can_enter_territory`
   (`combat_executor.py:7362-7370`; second implementation
   `world_state.py:12033-12035` while its own MOVE arm checks at
   `:12288-12292`). Capture is blocked, so this is illegal STANDING on a
   neutral court's soil — the CA9-F13 shape. **Fix:** the frontier halt at
   both advance sites (the pursuit guard's own vocabulary; the cavalry
   halts at the border it cannot legally cross).
2. **WO-25 (P2):** the "autonomous war-purpose theater dead" rider is keyed
   to `_jealousy_autonomous`, present at only 2 of 4 staging sites — the
   glorious-charge site (`combat_executor.py:7421-7432`) takes no command,
   and `respond_to_glorious_charge` (`:7605-7614`) drops the command on both
   branches — so an attack the player never ordered can stage
   `war_purpose_selection`, a HARD_STOP mounted with `replace()` that can
   destroy the currently-active dialogue. **Fix:** carry the flag through
   all four sites; the census pin
   (`test_pc15_d_rulings_2026_08_15.py:141-150`) gets the two missing
   sites — its docstring's "the charge site is reached only by direct player
   charges" is falsified by the auto-charge at `combat_executor.py:4022-4047`
   and must be rewritten with it.
3. **WO-28 (P3):** the jealousy beat narrates attacks that were REFUSED —
   `jealousy.py:3610-3626` voids the standing order, executes, then logs
   `jealousy_autonomous_attack` with no `result.get("success")` check (live
   refusals include the recklessness popup — the common case for cavalry).
   The player reads "X has attacked Y … his standing order is void" with no
   battle and the order still lost. **Fix:** gate the log/beat on success;
   a refused autonomous attack restores the order it voided.
4. **WO-31 (P3):** a HOLD-sortie suppresses the ADVANCE but not the CAPTURE
   block (`combat_executor.py:6327` vs `:6376-6416`) — a sally that
   "returns to hold position" can flip an at-war province the marshal never
   stood on. **Decide at build:** either the capture requires standing on
   the field (block it for `_sortie`), or the flip is the spoils of a won
   sally and the COPY says so — shown=applied either way.

**Harness impact:** all four touch autonomous/AI-adjacent paths — this slice
takes a flip-attributed `BASELINE_SERIES` re-record if moved (each fix
independently attributable), M1–M7 checked.

### Slice 18 — "The Answer Finds Its Question" (WO-35/36/38/39/40) — ✅ LANDED August 22, 2026

> **Landing record — authoritative.** Built from
> `docs/audits/WO_35_36_38_VERIFICATION_2026_08_21.md` in the memo's order
> (which contradicts both filed rows and is what was followed), under the
> user's session directive. `tests/test_wo_slice18_answer_finds_its_question.py`
> (23); mutation sweeps `tools/_sweep_wo18.json` + `_sweep_wo18_review.json`
> — **22 mutations, 22 killed, 0 inert**; M1–M7 AND `BASELINE_SERIES`
> byte-identical, MEASURED by real run before AND after the review round,
> no re-record; parse harness EXIT=0; war-room boot smoke
> (`res://scenes/main.tscn`) 0 SCRIPT ERROR.
>
> **The review round (same session, fleet pointed at committed `ae5cf28`
> with a clean tree — the row's method rule):** 16 agents, 4 find lenses →
> 2 independent refuters per deduped finding; 8 raw → 6 unique → **4
> confirmed, ALL FIXED** · 2 REFUTED (both "pre-existing, not worsened,
> consciously scoped": the first-marshal-wins interrupt pick and the
> capture-shadows-interrupt overlap — each strictly better than the parent
> and pinned as a recorded decision). The four confirmed were ONE family
> plus a weak pin: **(a)** the lapse's telling was one transient terminal
> line — `strategic_objection_lapsed` was absent from
> `_DISPATCH_EVENT_TYPES` AND carried no nation key, and the dispatch's
> `_build_turn_events` drops on BOTH gates independently (the
> shadow_petition precedent, re-earned); **(b+c)** if the objector was
> DESTROYED in the same end turn (the enemy phase runs before
> `advance_turn`), `get_marshal` returned None and the fog filter's
> location-less drop arm swallowed the line — the clear became exactly the
> silent loss the event exists to prevent. Fix for all three = the ONE
> `nation` stamp on the event (load-bearing twice, comment says so) + the
> whitelist entry at `warning` severity (the `order_voided_by_battle`
> class); **(d)** `test_a_restored_strategic_objection_still_reexecutes`
> never reached the re-execution seam (trust → the decline arm, which
> reads neither `parsed_command` nor `path`) — replaced by a round-trip
> pin on BOTH stored dicts plus a real INSIST test measuring the restored
> `parsed_command` drive the issued `StrategicOrder` (command_type SUPPORT
> from the restored dict's own field; the fixture now models the raise
> site's real parsed_command shape, which carries `strategic_type` at its
> own top level).
>
> 1. **WO-39 FIRST (it blocked everything):** `_on_commitment_paradox_choice`
>    gained the third arm — an unknown choice re-enables input and grabs
>    focus instead of leaving the terminal dead under a modal ESC cannot
>    escape.
> 2. **WO-38 (the P1), both recommended halves:** the answer router now
>    consults the STRATEGIC slot only when no TACTICAL objection stands
>    (one-condition reorder at `meta_executor.handle_objection_response` —
>    the tactical objection is the one blocking commands, so it is the one
>    the player is being told to answer; the measured Ney→Davout hijack is
>    dead, and every typed route funnels through the same seam), AND an
>    unanswered strategic objection **lapses at the turn boundary with a
>    told message** (`_advance_turn_internal`, a `strategic_objection_lapsed`
>    tactical event that survives the fog filter — slice 16 established the
>    order is never created at objection time, so the lapse loses nothing
>    that was not already lost, and now it says so). The TACTICAL slot is
>    deliberately NOT lapsed (it blocks end turn; pinned).
> 3. **WO-35's `pending_interrupt` half ONLY:** `/load` scans
>    `get_player_marshals()` for a STANDING marshal's restored interrupt
>    (hazard-4 tombstone idiom — captured/destroyed marshals attach
>    nothing) and stamps the one key; the client raises it in
>    `_apply_world_swap_response` through the SAME predicate/route pair the
>    command path uses, with capture-before-interrupt precedence pinned to
>    match the command path's route order. **`pending_objection` is
>    deliberately NOT attached** — the saved dict records no
>    tactical/strategic discriminator and the strategic modal arm would
>    render `options == []`, a modal with no buttons and no ESC exit (the
>    filed fix was a soft-lock; pinned by mutation #11). Its remainder — a
>    P3 legibility gap, answerable by the block's own typed words — is
>    **owned by slice 12**. The invisible third slot
>    (`pending_strategic_objection`, which shares the response key and so
>    the census cannot see it) is resolved by the WO-38 lapse: undecided is
>    not a state it can occupy any more.
> 4. **WO-36 + WO-40 together, client-side, zero backend change:** the
>    world-swap reset now clears `_redemption_recheck_turn` (WO-36's real
>    cause — the stale latch skipped the PT-B1 recovery poll on a same-turn
>    reload, the IGR-F `_envoy_digest_shown_turn` idiom) plus the four
>    cross-campaign stashes (`pending_redemption_data`,
>    `pending_proclamation_data`, `pending_diorama_data`,
>    `last_battle_diorama`). `redemption_event` gained the census's FOURTH
>    classification — **RECOVERED_BY_POLL** — rather than moving to
>    LOAD_REATTACHED. **Drive-by found by the dead-verb pin:** the client
>    carried the retired `demand_obedience` verb in FOUR places, two worse
>    than the memo's two — the dialog emits `administrative_role`, and both
>    display arms matched only the dead verb, so the Staff-transfer choice
>    echoed an EMPTY line and never reached its result banner. All four
>    fixed; the pin binds the quoted code forms.
>
> **Census re-classified** (the slice-15 blocking-state surface census):
> `pending_interrupt` → LOAD_REATTACHED; `redemption_event` →
> RECOVERED_BY_POLL (new class); `pending_objection` stays KNOWN_SILENT
> with the WRONG rationale corrected in place (the "requires success==true"
> comment named the one thing that was not load-bearing) and its owner
> named (slice 12).

---

## §4 New findings (August 21, 2026) + routing

Found while verifying the eval and hunting beyond it. N-1..N-9 are the session
author's own (each hand-verified); H-* rows come from the two hunt agents and
are marked with their verification state.

- **N-1 (slice 1, absorbed):** the eval's slice-1 contract never mentions
  `PYTHONHASHSEED`, while the `BASELINE_SERIES` runner pins it — an
  "instrument fixed" claim that skipped hash seeding would still be
  nondeterministic across shells. Absorbed into slice 1 item 6.
- **N-2 (slice 1, absorbed):** Mode B (`--http`) cannot be made deterministic
  from the driver (separate server process). Documented as a mode-scope rule.
- **N-3 (slice 4, absorbed):** `sovereign_captured: 101` (NP-4) sits above
  `home_captured` and the eval's D6 ordering reasoning omits it; the slice-4
  ordering pin now includes it.
- **N-4 (slice 7, absorbed):** the redirect family needs an EXCLUSION list —
  the committed tyrant script itself drives typed reward verbs
  (`grant Ney a rente`), and `Talleyrand, assess` is typed-only counsel.
  Enumerated in slice 7's table.
- **N-5 (slice 7, absorbed):** `request terms` needed a carve decision — its
  war-detail button sends via `send_structured_command` directly
  (`main.gd:5295-5311`), so including it in the redirect is safe; recorded as
  a reversible decision.
- **N-6 (slice 9, absorbed):** the WO-8 loop head lacks BOTH a self-court
  guard and a fellow-vassal guard (§2 H-6) — the slice contract names all
  three arms, not just the per-target cap.
- **N-7 (slice 5, absorbed):** post-G1 the counsel must point at a SURFACE,
  not a typed verb — the eval's slice-5 copy ("ask, Sire") predates its own
  G1 ruling.
- **N-8 (routing, new rows):**
  - **(a) WO-D7 filed** in `DESIGN_REFINEMENT.md` §Weird-Outcomes: *a war in
    which nothing happens bills both treasuries* — France|Russia sit at war
    score exactly 0 for thirty turns, never fight, and both pay WE-200
    charges and the war recruit premium. The eval recorded the finding
    (§3 WO-D5 "New finding") and routed it nowhere. Owner: EC-2 pass 2
    (charges shape), with slice 5's counsel as the near-term mitigation (the
    peace becomes visible).
  - **(b) the rout-repetition item** ("broken and flees" ×7 — the surviving
    narration half of the struck "indestructible commanders" clause) homed in
    slice 12 with a named mechanism (the XR-5 `battle_counts` seam). The eval
    said "re-file beside WO-D6" and no row existed.
- **N-9 (§1, absorbed):** the G1 residual list gains arm (c) — live-parser
  synonyms — which neither the ruling nor the eval recorded.

**The hunt findings (two agents: degenerate loops; playstyle bad scenarios —
each cross-checked against every existing BUG/DESIGN row before filing;
rows marked ⊙ were additionally re-verified by hand by the session author):**

| id | finding | sev | routed to |
|---|---|---|---|
| ⊙ **WO-17** | **"The Trojan Corridor"** — the WIN-D3 evacuation grant is pair-scoped and direction-less; an armistice opens legal transit INTO enemy sovereign soil for fresh corps, walked-in corps hold the corridor open, and war auto-resumption is free. Player-exclusive in practice (the AI's only consumer walks home) | **P1** | **slice 13** |
| **WO-18** | pension churn — grant/revoke cycling pays the rente one turn in three; the grace clock fully resets on any met turn; erosion never fires | P2 | slice 14 |
| **WO-19** | `region.plundered` clears on ANY change of hands (three sites) while its docstring promises the stability-50 / 9-unguarded-turns clear — abandon→AI-secures→retake re-arms the full sack | P2 | slice 14 |
| **WO-20** | *"break the alliance with Austria"* PROPOSES an alliance (`_break_keywords` are treaty-phrasings only; the proposal arm then reads "alliance" as the thing to create) | P2 | slice 11 |
| ⊙ **WO-21** | the strategic-objection trust arm credits trust BEFORE validating the preferred action (free trust on the bail), and the SUPPORT-objection's trust option carries `"action": "cancel"` — an id the dispatch has no arm for: +trust, 0 AP, order still standing, raw "Unknown action: cancel" | **P1** | **slice 16** |
| ⊙ **WO-22** | the auto-end-turn defer never checks `pending_capture_choice` (the typed path blocks on it) — a last-AP capture crosses the turn boundary unanswered and the choice dies on the holder-re-validation lapse | **P1** | **slice 15** |
| ⊙ **WO-23** | `save_manager` wipes `objection_popups_this_turn` on load while `from_dict` restores it — a mid-turn save/load refreshes the only live limiter on the +3..+12/popup trust channel | P2 | slice 16 |
| **WO-24** | the charge/auto-charge ADVANCE has no `can_enter_territory` — victorious cavalry relocates onto a neutral court's soil (illegal standing, the CA9-F13 shape; both implementations) | P2 | slice 17 |
| **WO-25** | the "autonomous war-purpose theater dead" rider covers 2 of 4 staging sites — an auto-charge the player never ordered stages the HARD_STOP `war_purpose_selection`, whose `replace()` mount can destroy the active dialogue; the census pin's docstring is falsified by the auto-charge site | P2 | slice 17 |
| **WO-26** | attack-capture and occupation-completion CLOBBER an unanswered capture choice (bare single-slot writes; only the move path has the PF-3 guard) | P2 | slice 15 |
| **WO-27** | the dotation prune lacks the `_capture_choice_pending` carve-out its three siblings have — the estate *respect* answer can become a paid no-op | P3 | slice 15 |
| **WO-28** | the jealousy beat narrates autonomous attacks that were REFUSED (no success check; the voided standing order stays lost) | P3 | slice 17 |
| **WO-29** | typed capture answers never carry `dialogue_id` — the W6-0 stale guard is inert on the typed path | P3 | slice 15 |
| **WO-30** | `/load` never re-attaches a restored pending capture question (no capture entry in `PopupQueue.RESPONSE_KEYS`; the queue's `to_dict`/`from_dict` are dead code — hand-enumerated keys) | P3 | slice 15 |
| **WO-31** | a HOLD-sortie suppresses the advance but not the capture — a sally can flip an at-war province the marshal never stood on | P3 | slice 17 |
| **WO-32** | the vassal-rebellion-imminent popup pops the dialogue UNCONDITIONALLY then calls `invest_in_vassal`, which has reachable refusals (3-turn cooldown, gold, DP) — on refusal turns "Invest" charges nothing, changes nothing, and DELETES the crisis decision (Garrison / Accept-Risk lost) on a vassal one tick from rebellion; the jealousy channel documents-and-fixes this exact failure and the pattern was never ported | **P1** | **owned by PC15-10** (`PETITION_POPUP_REVISIT_SPEC.md` — the popup-lifecycle slice family; filed there by row reference, NOT double-built here) |
| **WO-D8** | should the PLAYER face any re-declaration time floor after a truce/peace? Today 0 turns (the exhausted-pair 8-turn floor skips player pairs; leaving ARMISTICE pops the 5-turn hold) while re-declaration is priced only in DP/relations/threat/war-age. Design question, not a bug — PT-J2's demobilize-on-peace is a gate ruling and stands | design | `DESIGN_REFINEMENT.md` §WO, future diplomacy gate |
| **WO-D9** | the objection-economy shape: no per-marshal objection cooldown exists (the global cap constant is dead code), authority pays +1/answer in the 0.30–0.60 band while the penalty starts at 0.65, compromise counts toward neither — tunable farm surface even after slice 16's correctness fixes | design | `DESIGN_REFINEMENT.md` §WO |
| **WO-D10** | the exiled empire cannot rebuild its Marshalate — `find_spawn_region` considers only the capital and `nation_starting_regions`, never held conquests, so a dead roster in exile is permanently unrecoverable while income/DP/tribute continue, and the refusal copy ("No soil remains…") is false on the map the player is looking at | design | `DESIGN_REFINEMENT.md` §WO, Victory-pass adjacent |

**Folded without rows:** the naval stranding-remedy copy (the over-lift
refusal advertises a garrison the beachhead cannot legally place; the SHUT
refusal advertises an expedition the corps size forbids — the real road is
never stated) → slice 6's copy contract; the wizard gating holes
(`cancel_mission` dropped for vassalized courts by the vassal branch's early
return; D5 chips vanish on deckless worlds while the parser accepts the
verbs; `mission_improve_relations` absent in WAR/ALLIANCE) → slice 7 item 8;
the stale "trade" help promise → slice 7 item 4; the legacy Specify-lists →
slice 12; `mild_concerns_this_turn`'s identical wipe-vs-restore
contradiction → noted beside WO-23, cosmetic.

**Hunt verdicts recorded as CLEAN (so nobody re-hunts them):** sustained
bankruptcy is genuinely priced (mercy + desertion + rente lapse; every spend
site treasury-gated; the only nuance is interest-free debt); no AP/DP
soft-lock at maximum loss (pools refill unconditionally; player exempt from
the elimination skip; DP floors at 1); no division-by-zero at 0 provinces in
the guarded seams; permanent peace degrades nothing unboundedly (every
counter clamped/pruned/capped); the doomstack caps at 6%/turn attrition with
no overflow; pending-question serialization is COMPLETE (the losses are
lifecycle, not serialization); estate/rente one-way (no standing confiscate
verb, no revoke_dotation); build/raze and gold↔manpower have no reverse
verbs; vassal autonomy toggling is strictly dominated (−5 loyalty per
up/down pair); glory farming excluded by the recorder's own gates
(bombardment/auto-kill/garrison all excluded); drill saturates at the morale
clamp; ransom is priced war-profit; DP cannot accumulate (recomputed each
turn, zero incremental producers); naval has no refund verb and posture
toggling has no positive arm.

---

## §5 Order, dependencies, and the row's definition of done

**Order = the eval's §5 ranking, extended by this spec's additions:** 1 → 1b
→ 2 → 3 → **13** → 4 → 5 → 6 → 7 → 8 → **15 → 16** → 9 → 10 → **17** → 11 →
12 → **14**

> **AMENDED TWICE BY USER DIRECTION, August 21, 2026, and the amendments
> are recorded rather than absorbed.** (a) **Slice 7 was taken early**
> (*"make cabinet door so diplo only works through ui"*) — nothing in
> 4/5/6 blocked it and it was already sequenced before 11, so only its
> own position moved. (b) **Slices 15 and 16 are lifted ahead of 4/5/6/8**
> on the reasoning that the two remaining hand-verified P1s should clear
> before the legibility and copy work. (c) **Slice 5 was lifted ahead of
> slice 4** (August 22, 2026): the two are independent — slice 4 is the
> dispatch's headline ordering, slice 5 is the war room's counsel — and
> the 4-before-12 dependency below is about the shared dispatch files,
> which slice 5 never touches. **Slice 4 remains next**; only slice 5's
> position moved. Realised order so far: 1 → 1b → 2
> → 3 → 13 → 7 → **15 → 16 (both landed August 21, 2026 — the three
> hand-verified P1s are closed)** → 18 → **5 (landed August 22, 2026)** →
> 4 → 6 → 8 → 9 → 10 → 17 → 11 → 12 → 14.
> The dependency notes below still hold: 7 before 11 (7 shrinks 11 — and
> has), and 4 before 12 for the shared dispatch files. (~13 sessions to the line; the eval's ~10 plus the hunt
slices). Slice 13 rides high because it is a P1 exploit on a days-old
system (WIN-D3, Aug 16) whose pins are freshest now; 15/16 carry the
other two hand-verified P1s; 14 is cleanup-tier. Slices 2–17 do NOT depend
on 1b's numbers — only the G2(b) shelf decision does. Slice 7 before 11 (G1
shrinks 11); slice 4 before 12 only for the shared dispatch files
(mechanical merge order, not logic).

**Per-slice harness discipline (the §4 method rule, binding):** any claim that
a slice leaves `BASELINE_SERIES` byte-identical must be proven by a real
source-edit run through `_run_series_subprocess` — a passing in-process suite
is vacuous for this pin (it runs in a fresh hash-seeded subprocess). Slices 9
and 10 take sanctioned flip-attributed re-records; slices 3 and 17 measure
and re-record only if moved (flip-attributed); every other slice proves
byte-identity.

> **AMENDED by slice 15, August 21, 2026: "every other slice proves
> byte-identity" is a prediction, not a licence.** Slice 15 was expected to
> be inert on that harness — every seam it touches is player-nation gated
> and France issues no orders on the ambient board — and it moved index
> [40] anyway, because France IS `world.player_nation` even with nobody at
> the keyboard, so French captures take the PLAYER branch. Any slice
> touching a `marshal.nation == world.player_nation` branch should expect
> the ambient board to feel it. Measure first; if it moves, take the
> flip-attributed re-record and name the lever.

**The row is DONE when:** all seventeen slices landed in order with their
done-when lines green; the funnel table re-measured with error bars (or
withdrawn) and the G2(b) shelf decision taken on it; the three gate rulings
implemented without re-opening (G1 slice 7, G3 slice 8, G2 = the 1b
measurement + the Victory-pass hand-off note); `BUG_FIXES.md` §WO rows
WO-1..WO-31 **plus WO-33..WO-37** all FIXED/CLOSED with pointers here
(WO-32 closed by its owner PC15-10 and checked at this row's exit; WO-34
was found and fixed by slice 15, WO-35/WO-36 were filed by its census and
need owners); the WO-D8..D10 design rows **plus WO-D11** either gated or
explicitly carried; `PLAYTESTING.md` carrying the known-bad
list + the method rule; suite green; boot smoke 0 SCRIPT ERROR for the
`.gd`-touching slices (7, 8, **and 15** — XR-1 rule); and **the three owed
visual sign-offs SIGNED by the user** — evidence captured August 21, 2026
(`docs/audits/WO_SIGNOFF_{1_CABINET_REDIRECT,2_WIZARD_FROM_LINK,3_LOAD_CAPTURE}_2026_08_21.png`,
harness `tools/wo_signoff_screenshot.gd`); **✅ SIGNED August 22, 2026 —
the three frames were put in front of the user and the sign-off given.
This DoD item is DISCHARGED.**

---

## §6 Never-do — carried from the eval's §7, plus this spec's additions

The eval's twelve stand verbatim (PC15-D2's concentration-tax ruling ·
CA9-D2's popup ruling · D3's France-gravity + power_score share · ES-1b/E2 ·
CR-2's one-question contract · CA8-5's falsifiable negative · the own_mauled
re-open recorded on WO-16 · `_execute_naval_expedition` message-only ·
WIN-D2 landed · `request_terms` ships · the wizard IS a typed-command
producer, so G1 lands terminal-side forever · the driver keeps typed
diplomacy). Additions:

13. **Do not put `random.seed` into `backend/` production code.** The
    instrument seeds itself (the driver); backend seeding would collide with
    the `BASELINE_SERIES` runner's own discipline and constitute a behavior
    change wearing a harness fix's coat.
14. **Do not intercept the chip pipelines.** The redirect lives in
    `_execute_command()` only; `_on_reward_command` / `_on_vassal_command` /
    `_on_wizard_command_selected` / the war-detail request-terms sender are
    load-bearing bypasses (§2 G1-2), not oversights to "unify".
15. **Do not match redirect heads against option labels or display copy** —
    verb heads only, fail-open (an unmatched sentence goes to the backend as
    today). A false-positive interception is a worse defect than the backdoor
    it closes.
16. **Do not "complete" slice 3 with the futility guard** — recorded as
    consciously not built (slice 3).
17. **Do not re-run `build_region_key_from_psd.py --adjacency-only`, ever**
    (standing project rule, repeated here because slice 8 touches supply
    surfaces near the registry).
18. **Do not treat the archived digests as regenerable** — `--archive` copies
    are the citable record precisely because `tools/playtest_runs/` is
    ignored and overwritten; a memo citing an unarchived digest is citing
    nothing (the WO memos' own lesson).
19. **Do not double-build WO-32.** The vassal-rebellion popup's
    refusal-path destruction is PC15-10's (`PETITION_POPUP_REVISIT_SPEC.md`
    owns the popup-lifecycle family and already fixes this exact shape on
    the jealousy channel) — this row only CHECKS it at exit.
20. **Do not weaken WIN-D3's five §3.4 never-do pins while building slice
    13** — the direction term is an ADDITIONAL constraint on the grant, and
    the corridor's legitimate cases (stranded corps walking home, both
    sides, the free 0-AP orders, the enemy-AI P1.2 rung) must all survive
    byte-identically.
21. **Do not add a player re-declaration time floor uninvited** — that is
    WO-D8, a design question for a gate; PT-J2's demobilize-on-peace and the
    CA9 war-age pricing are recorded rulings, not gaps.
