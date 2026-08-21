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

### Slice 5 — WO-D5 "Berthier Names the Peace" (est 0.3)

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
12 → **14** (~13 sessions to the line; the eval's ~10 plus the hunt
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

**The row is DONE when:** all seventeen slices landed in order with their
done-when lines green; the funnel table re-measured with error bars (or
withdrawn) and the G2(b) shelf decision taken on it; the three gate rulings
implemented without re-opening (G1 slice 7, G3 slice 8, G2 = the 1b
measurement + the Victory-pass hand-off note); `BUG_FIXES.md` §WO rows
WO-1..WO-31 all FIXED/CLOSED with pointers here (WO-32 closed by its owner
PC15-10 and checked at this row's exit); the three WO-D8..D10 design rows
either gated or explicitly carried; `PLAYTESTING.md` carrying the known-bad
list + the method rule; suite green; boot smoke 0 SCRIPT ERROR for the two
`.gd`-touching slices (7, 8 — XR-1 rule).

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
