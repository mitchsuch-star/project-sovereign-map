# Row FR, Session FR-2 — the weak-spot readers' twelve finds (WS-R): the design

**Status:** design written November 23, 2026, before Session FR-2 opens. Nothing is built.
**Owner:** row FR (`docs/PRE_DEPLOY_PLAN.md` §2), Session FR-2 (FR-2a and FR-2b if it splits, §5).
**By whose word:** the user's, November 23, 2026, after row IC closed: "update tutorial so it reflects all updates we
made and ficx Five defect rows remain open can eb mul;tiple sessions".
**Tracked:** `docs/STATUS.md` ▶ NEXT UP; `docs/BUG_FIXES.md` row WS-R.
**Behaviour test:** `tests/test_ws_weak_spot_review_2026_11_13.py::TestWSRTheReviewsUnconfirmedFinds::test_every_find_is_confirmed_or_refuted`
(strict xfail; it goes green when the census reads WS-R closed — mind §1's trap).
**Done when:** §6. **Landing record:** §7, written at the landing.

---

## §0 Where this comes from

The November 13, 2026 weak-spot review (`BUG_FIXES.md` §WS) sent readers through the code. Its lead confirmed and
fixed what it could (WS-1 … WS-16) and filed the twelve finds it had not confirmed as one row, WS-R, with one rule:
each find is confirmed in the code (then fixed, or filed under its own id) or refuted with its reason.

The **first readings** below come from a read-only pass on November 23, 2026: helpers read the code at every line the
finds name and traced the roads around them. Nothing was run. Each reading is a lead, not a verdict. Session FR-2
proves every one with a test before it changes a line.

## §1 The method, per find

1. Read the code at the lines below. They were read on November 23; check them, since lines drift.
2. Write the behaviour test that shows the fault (a world, an order, the reply or the state after it), and watch it
   fail on today's tree.
3. **It fails as filed → CONFIRMED.** File `WS-R<n>` in `BUG_FIXES.md` §WS, fix it, watch the test pass, then sweep
   its class (rule 10). Each sibling is fixed in the same slice or filed as a row that heads the next part.
4. **It passes → REFUTED.** Write the reason in the WS-R row beside the find. Keep the test as a guard where it is
   cheap.
5. **A find that is partly real** (4, 5 and 6 read that way) is confirmed for the part that is real; the rest is
   refuted with its reason.

**The census trap — read before closing the row.**
- The pin asks `tools/defect_census.py` for WS-R's state and wants `closed`.
- The census reads a row as `closed` when its status cell starts with ✅ / FIXED / CLOSED (or another closing word).
  It reads a row as `disposed`, which is not `closed`, when the status cell starts with REFUTED, STRUCK, RE-HOMED and
  their kin.
- So WS-R closes as "✅ CLOSED <date> — every find confirmed and fixed (WS-R1 …) or refuted (…)", never with
  REFUTED at its head.
- The new `WS-R<n>` rows may each lead with FIXED or REFUTED as fits. Only WS-R itself feeds the pin.
- Never write upper-case "RE-HOMED" in a ledger row: the census reads it as disposed.

## §2 The twelve finds

Each find gives: what was filed; the code today; the first reading; the test that settles it; the fix's shape if
confirmed; the class to sweep; whether a fix can move a measured world-line (§4).

### Part one — combat (1, 3, 4, 5, 7, 12)

**Find 1 — an ordered charge at a man out of sight but within reach.**
- *Filed:* the charge still meets the crossing, "already engaged" and terrain refusals, which speak of where he is.
- *Code today:*
  - `combat_executor._execute_glorious_charge` (~13890) computes the sight check `_unseen_charge_quarry` first
    (~13823 → `unseen_target_refusal` ~1203 → `intel_surfaces.in_sight`). It applies it on three paths only: the
    peace-soil refusal (~13922), out of reach (~13923) and the leapfrog block (~14020).
  - The terrain fall-through is not wrapped (~13971). It prefixes "cannot charge in {terrain} terrain!" onto the
    attack road's reply and sets `result["terrain"]`.
  - The crossing refusal is not wrapped (~14003): "The crossing from {from} to {to} is barred…", where `{to}` is his
    province.
  - "Already engaged" is not wrapped (~14023).
  - The docstring (~13830) chose to meet a man within reach "as the attack road meets him".
- *First reading:* real for the crossing and terrain arms, which name his province and his ground. Weak for "already
  engaged": the player fought that battle.
- *Test:* a French corps two provinces from an enemy corps in fog orders the charge. No reply or result key names his
  province or terrain, and the reply is the unseen refusal.
- *Fix shape:* the sight check wraps the crossing and terrain arms as it wraps the other three.
- *Class:*
  - every refusal on the attack road that runs before the sight check: the approach crossing that names `best_next`
    (~9564), and the attack road's own crossing refusal (~9996–10010);
  - whether the attack road wraps an in-range unseen man at all (not traced).
- *World-line:* no — a refusal's words.

**Find 3 — the battle report against what was applied.**
- *Filed:* an Iron Resolve release prints the stance's −10 % that it undoes; the jealous solo attack's +15 %, the
  jealousy surge's +10 % and cavalry momentum have no row.
- *Code today:* the report (`battle_report.py` ~80–290) re-types numbers instead of reading
  `marshal.get_attack_modifier` (~1455) and `get_defense_modifier` (~1612). Golden rule 1 says the report reads them.
  - Iron Resolve's release undoes the defensive stance's penalty (`marshal.py` ~1540, `modifier /= 0.90`), but the
    report prints both the stance row (~101) and the Iron Resolve row (~214).
  - The jealous solo attack's +15 % (`marshal.py` ~1560; flag stamped at `combat_executor` ~10955): no row.
  - The jealousy surge's +10 % (attacking ~1562, a cautious defence ~1702): no row on either side.
  - Cavalry momentum (`marshal.py` ~1341–1369 returns −0.05 or −0.10, applied ~1573): skipped by the Exhaustion
    row's `> 0` gate.
- *First reading:* real on all four.
- *Test:* for each row, a battle built to carry that modifier. The report's rows multiply to the factor that
  `get_attack_modifier()` / `get_defense_modifier()` returned — the report and the fight agree.
- *Fix shape:* the modifier functions expose the parts they apply (a breakdown beside the product), and the report
  prints that breakdown. No figure is typed twice.
- *Class — the sweep is the large part:* the report also re-types:
  - the stance 15 / 10 and 10 / 15, on both sides;
  - caught drilling 25; artillery in transit 25; square 5; counter-punch 20;
  - cavalry counter 30; square against cavalry 40 and against artillery 50.

  `combat.py` (~496) rebuilds Iron Resolve's percentage for its message. One breakdown source ends the class.
- *World-line:* no, if the report only reads. Pin the battle outcomes byte-identical as the guard.

**Find 4 — banked strategic bonuses.**
- *Filed:* `strategic_combat_bonus` and `strategic_defense_bonus` are cleared only when spent, so a literal marshal's
  clear order banks them with no expiry.
- *Code today:*
  - *Set sites:* `meta_executor._apply_grouchy_ambiguity_buff` (~836–837; the player's literal marshals, called from
    `executor.py` ~3206); `ai/feedback.apply_strategic_bonuses` (~159; called by `enemy_ai.py` ~1807 and ~9151).
  - *Clear sites:* spent in the modifier reads (`marshal.py` ~1505 and ~1649, when `consume=True`); GRD-33's
    turn-end expiry (`world_state.py` ~16764–16779), which is player-only
    (`personality == "literal" and nation == player_nation`).
- *First reading:* the filed claim is fixed by GRD-33 (row IC, Session 2). What is left: the AI's banked combat bonus
  has no expiry, and it is set AFTER the act it rewards has run (`enemy_ai.py` ~1795–1807). So it rides to that
  marshal's next attack, however many turns later. The `world_state.py` comment ("courts spend theirs in the act that
  set it") does not match that order.
- *Test:* an AI marshal scores an act that banks the bonus; three turns pass with no battle; his next attack's
  modifier must not carry it (today it does → confirmed).
- *Fix shape:* the expiry covers every holder, or the AI's bonus is applied before the act it rewards — whichever
  `apply_strategic_bonuses`' own design intends.
- *Class:* any other one-shot marshal bonus with no expiry (the initialisers near `marshal.py` ~597–598 and their
  kin).
- *World-line:* **yes** — the AI's battles move. Measure it (§4).

**Find 5 — a corps killed by a bombardment.**
- *Filed:* it goes down the forced-retreat road, never `destroy_marshal`; the auto-bombardment kill returns before
  the attack count and the reinforcers' trust dock.
- *Code today:*
  - *An ordinary kill* calls `world.destroy_marshal(cause="battle")` (`combat_executor` ~12306, ~12322; the charge
    ~14194, ~14201).
  - *An ordered bombardment's kill* (`_execute_bombardment` ~8472; the collateral kill ~8710; ~8790
    `enemy_destroyed = defender.strength <= 0`) goes to `_apply_forced_retreat_or_break` (~8222). There
    `_check_marshal_fate` returns None at strength 0 (~7596), and the corps routs with 0 men. The empty corps stays on
    the roster until the turn-end attrition sweep (`world_state.py` ~9565) destroys it with `cause="attrition"`. A
    sovereign is captured there, under the words "eliminated by supply attrition".
  - *The auto-bombardment kill* (`_attack_dead_defender` ~11046) does call `destroy_marshal(cause="bombardment")`
    (~11065) and does count the attack (~6904). It returns at stage 12 (~11270), before stage 20's reinforcers' trust
    dock (~13483–13513).
- *First reading:*
  - (a) The ordered bombardment's kill — real: the wrong cause, a corps of 0 men standing until night, and a
    sovereign's fate read as attrition.
  - (b) The auto-kill's attack count — already right.
  - (c) The auto-kill skips the reinforcers' trust dock — real, but whether it should dock is a design reading: a
    dead defender needed no reinforcement.
- *Test:*
  - (a) Bombard a 900-man corps to nothing. It is destroyed at once with cause "bombardment", a tombstone and a fall
    event; a sovereign runs the Guard or death roll.
  - (c) The reinforcers named on an auto-kill: assert what the design rules.
- *Fix shape:*
  - (a) The bombardment's kill calls `destroy_marshal(cause="bombardment")`, as the auto-kill does.
  - (c) Ruled in FR-2's Plan Mode against `docs/MULTI_MARSHAL_SPEC.md`.
- *Class:* the collateral kill (same function); the overwatch support bombards (~11001).
- *World-line:* possibly — a corps gone hours earlier, a sovereign's fate. Measure it.
- *Pin to move:* `tests/test_bombardment.py` (~210) pins today's broken-at-spawn behaviour.

**Find 7 — a marshal of one man.**
- *Filed:* he still counts for combined arms, the adjacent-ally bonus, a flank's origin and the battle's glory.
- *Code today:*
  - combined arms: `_count_unit_types` (~1995, `strength <= 0: continue`);
  - the adjacent-ally bonus: `_count_adjacent_allies` (~2515, `strength > 0`);
  - coordination eligibility (~2552, `> 0`);
  - a flank's origin: `world.record_attack` (`world_state.py` ~18294; called at ~8727, ~10627, ~14037; no guard),
    read by `calculate_flanking_bonus` (~18332);
  - glory: `jealousy.record_battle_glory` (~510). It is gated by a casualty floor of 1,000, not by a strength floor;
    participants take ±1 at ~640–660.
- *First reading:* real for combined arms, the adjacent bonus and a flank's origin — any strength of 1 or more
  counts. Glory is unclear.
- *First, find the roads to a tiny corps.* `take_casualties` zeroes anything under 50 men (`marshal.py` ~1860), so
  battle alone rarely leaves one. A detachment, a drawn-down garrison or a levy may.
- *Test:* a 1-man corps beside an attack adds no arm to combined arms, no adjacent bonus and no flank.
- *Fix shape:* one floor constant read by all four. The house has several to copy:
  `world_state.DISRUPTION_MIN_STRENGTH = 1000`, `MARSHAL_FATE_STRENGTH_FLOOR = 5000`. Glory's participants are
  included if confirmed.
- *Class:* every other count of "corps present" with a `> 0` guard (coordination, support, overwatch).
- *World-line:* maybe; rare. Measure it.

**Find 12 — a bombardment passes a won battle to the war score at no risk: is it a farm?**
- *Code today:*
  - `_execute_bombardment` calls the post-combat pipeline with `attacker_won: True` and `outcome: 'bombardment'`
    (~8738). It sets `skip_war_damage`, but not `skip_diplo_record`.
  - Pipeline step 8 (~6364) calls `diplomacy.record_battle(..., winner_nation=attacker.nation)` (~12996). Both sides'
    dead go to the blood ledger, and the settlement contribution accrues, before the scale floor. Past
    `battle_scale.is_a_battle` (1,000 casualties or more), a `battle_records` row names the bombarder the winner.
  - The comment at ~6436 says so.
- *How it scores:*
  - `battle_score_from_records` (~3724) gives +3 a row (`BATTLE_SCORE_PER_WIN`), capped at ±15 (`BATTLE_SCORE_CAP`).
  - It decays only after 3 quiet turns (~3689); rows are pruned after 10 turns (~4106).
  - Blood scores 1 point per 2,500 net dead, capped at 15.
- *What it risks:*
  - A battery fires twice a turn (~8554).
  - Return fire costs about 1.5 % of its own strength (~8583–8590).
  - It takes no morale swing and no counter-punch.
  - A defender of about 25,000 or more clears the floor at 4 % losses.
- *First reading:* a cheap, bounded road to the battle component's cap (+15 in about three turns) and to blood.
- *Test and fix:* by the rule in §3 — the measure first, and a fix only if the rule says it is a farm.
- *Class:*
  - the AI bombards under the same cap (`enemy_ai.py` ~4112);
  - the auto-bombardment kill records a real win (right);
  - the overwatch support bombards record separately.
- *World-line:* yes, if fixed. Measure it.
- *Pin to move:* `tests/test_r1_pipeline_enforcement.py` (~153, `test_bombardment_records_diplo`) pins that a
  bombardment records.

### Part two — the roads, the read-back and the client (2, 6, 8, 9, 10, 11)

**Find 2 — "No foe is in sight to march on" when one is in sight but no road reaches him.**
- *Code today:*
  - `strategic_executor._find_nearest_enemy` (~1065) returns None when `world.find_path` (~7274) finds no path to any
    visible enemy. "None in sight" and "none reachable" are one answer.
  - Its callers are `_resolve_generic_target` (~990 PURSUE, ~1041 MOVE_TO).
  - The message (~1403–1417; PURSUE's twin ~1414) says no foe is in sight. The enemies came from
    `get_visible_enemies`, so they ARE in sight.
- *First reading:* real. The unreachable case needs a broken graph or a sea gap with no crossing, since `find_path`
  is called here without a nation's passability.
- *Test:* a visible enemy across a sea gap with no crossing; "march on the enemy". The reply says no road reaches him
  (fog-true), not that no foe is in sight.
- *Fix shape:* the resolver returns its reason, and the message says it.
- *Class:*
  - "No foe is in sight, Sire — attack whom?" (`combat_executor` ~15102, `proper_name.py` ~394);
  - `world_state._find_nearest_enemy_for_nation` (~7806; the AI and the quote paths).
- *World-line:* no.
- *Pin:* `tests/test_ui6_fog_siblings.py` (~2590, UI6-X63) pins the no-visible-foe case only.

**Find 6 — the post-objection road's action gate.**
- *Filed:* it asks for one action left, not the order's price.
- *Code today:*
  - `_execute_post_objection` (`meta_executor.py` ~3050–3063) asks for one action left.
  - The answer roads are priced before it reaches that gate: the tactical answers by `_unpayable_tactical_answer`
    (~2520, ~2545, ACH-X10); the strategic answers by `strategic_answer_price` against `actions_remaining`
    (`strategic_executor` ~4192–4194, ACH-F3).
  - What is left: the disobey arm (`meta_executor.py` ~2796) calls `_execute_post_objection` with `_disobedience`.
    Its strategic branch (~3069–3081) spends `variable_cost` with no pool check. `use_action` clamps, so a 2-action
    alternative at 1 action runs and underpays. The non-strategic branch (~3195–3203) does check.
- *First reading:* refuted for the answer roads; real for the disobey arm's strategic branch.
- *Test:* a marshal's defiance picks a 2-action strategic alternative with 1 action left.
- *Fix shape:* the strategic branch refuses, or the disobey arm prices first, as the tactical branch does.
- *Class:* every road that calls `spend_actions` without a pool check.
- *World-line:* possibly (a defiance outcome); rare.

**Find 8 — the read-back's and the counsel's `redirect_stdout` swap the process's stdout across threads.**
- *Code today:*
  - `parse_preview.py` (~205, ~1819, ~1827, ~2226) and `counsel.py` (~186, `_quiet`, eight call sites).
  - The read-back's uses are safe. `GET /parse_preview` (`main.py` ~8634) runs under the state lock
    (`_LOCKED_READS` ~3389) and `parse_preview._LOCK`.
  - The counsel's are not. `GET /diplomatic_preview` (~8752) is a plain `def`, so it runs in the threadpool, and it
    is outside `_LOCKED_READS`. It reaches the counsel through `diplomacy.get_diplomatic_preview` →
    `counsel_for_wizard` (~17112).
  - Two overlapping `redirect_stdout`s restore out of order and leave `sys.stdout` on a dead buffer. Every later
    `print` on the server is then lost.
- *First reading:* real for the counsel.
- *Test:* two threads — a counsel call and a second redirect — entered and left out of order. Afterwards `sys.stdout`
  is the original.
- *Fix shape:* silence the prints at their source (a module logger or a flag), or use a per-thread stdout shim. At
  the least, put the counsel under `_LOCK`.
- *Class:*
  - `GET /diplomatic_ledger` (~9057, a plain `def`): check whether it reaches the counsel;
  - `backend/ai/parser_metamorphic.py` (~403–413): not on the request path.
- *World-line:* no.

**Find 9 — the diplomatic ledger re-renders on every resize step once a tab that measures no width is shown.**
- *Code today:*
  - `diplomatic_ledger.gd` connects `content_area.resized` to `_on_content_resized` (~97, ~553). It re-renders when
    the width has moved more than 16 px from `_width_used`.
  - Only the treaties and balance tabs measure (`_balance_width` ~536–542).
  - `_width_used` is never reset on a tab change or on close (~305–317).
  - So on a tab that never measures, every resize step more than 16 px off the stale width re-renders the whole tab.
- *First reading:* real, narrower than filed.
- *Test:* driven — open the balance tab, switch to nations, drag the grip, and count the re-renders. Today there is
  one per step.
- *Fix shape:* reset `_width_used = -1` when a tab draws, so only a measuring tab re-renders on resize.
- *Class:* `war_detail_popup.gd` (~1041, `_on_content_resized` / `_table_px_used`), the same pattern.
- *World-line:* no.

**Find 10 — the WS-2 answer stands beside the pursuit road's for a man with a stale sighting.**
- *Code today:*
  - WS-2 (`BUG_FIXES.md` ~3432, fixed November 14) answers an unseen man on a third court's soil through
    `combat_executor.peace_soil_refusal` (~1558) → `_whither` (~1574) → `intel_surfaces.in_sight`, which means seen
    now. The attack road reaches it at ~10077.
  - The pursuit road (`strategic_executor` ~1630–1637) refuses only when `last_seen` has nothing. A stale sighting is
    accepted, and its line (~2833–2840) quotes the old place: "pursues X (at Silesia)".
  - So, for the same man, "attack X" on peace soil says "No intelligence on his position", while "pursue X" says
    where he was.
  - An out-of-range attack auto-upgrades to PURSUE (~9795), and the pursuit's arrival re-enters the attack road.
- *First reading:* unclear, leaning real — two sighting rules for one man.
- *Test:* a man last seen two turns ago on a neutral court's soil; send "attack" and "pursue". The two replies agree.
- *Fix shape:* one sighting rule at both (the one-sighting rule, `tests/test_rr6_x3_one_sighting_rule.py`). Either
  the peace-soil test reads `last_seen`, or the pursuit refuses as WS-2 does — decided by which tells the player the
  truth.
- *Class:* `strategic.py` (~553, `muster_is_live`) names the same arm.
- *World-line:* possibly — a pursuit accepted or refused.

**Find 11 — the read-back's cost per keystroke.**
- *Code today:*
  - The name lists are rebuilt on every call on the parse road the read-back drives: `condition_grammar.py` ~714;
    `llm_client.py` ~301 and ~330; `reading.py` ~279; `clause_guards.py` ~822 … ~1766; `dd0_rewrites.py` ~154 and
    ~509; `second_name.py` ~60.
  - Python's `re` caches compiled patterns by their string, so the cost is the rebuild (sort, escape, join), not the
    compile.
  - `intel_surfaces.last_seen` (~217) → `enemy_sightings` (~298) loops every region's intel, uncached (golden rule 8).
    It runs per keystroke on the pursuit and quote paths whenever a PURSUE is read.
- *First reading:* real, modest.
- *Test:* free of timing — a counter seam on `enemy_sightings`. Several `GET /parse_preview` reads of a PURSUE line in
  one turn scan once, not once per read.
- *Fix shape:* cache the sightings per turn (the `invalidate_active_nations_cache` pattern), and memoize the roster
  alternations per world epoch.
- *Class:* any other per-region scan reached from the read-back.
- *World-line:* no.

### The first readings at a glance

| # | Find | First reading | Moves a world-line? |
|---|---|---|---|
| 1 | Charge at an unseen man within reach | real (crossing, terrain); weak (engaged) | no |
| 2 | "No foe is in sight" when one is | real | no |
| 3 | Battle report against what was applied | real ×4, plus a dozen re-typed figures | no (guard it) |
| 4 | Banked strategic bonuses | the player's fixed; the AI's real | **yes** |
| 5 | Bombardment kill | (a) real; (b) fixed; (c) real, a design reading | possibly |
| 6 | Post-objection gate | answers fixed; the disobey arm real | possibly, rare |
| 7 | A one-man corps | real ×3; glory unclear | maybe, rare |
| 8 | `redirect_stdout` across threads | real for the counsel | no |
| 9 | Ledger re-render on resize | real, narrower | no |
| 10 | WS-2 against the pursuit | unclear, leaning real | possibly |
| 11 | Read-back cost per keystroke | real, modest | no |
| 12 | Bombardment war score | the rule decides (§3) | yes, if fixed |

## §3 Find 12's rule, written before any data

Adopted, amended or replaced at FR-2's Plan Mode before the first run, never after it.

- **The arms:** the seeds the deploy gate's band uses (historical, austerlitz, marengo), over the forty-turn horizon.
  - Arm B is a France that bombards every turn it lawfully can, each battery twice.
  - Arm A is the shipped commanded France.
  - Same seeds, same everything else.
- **It is a farm if either holds on two of the three seeds:**
  - (a) arm B's battle component reaches its cap at least two turns before arm A's, or reaches it where arm A never
    does;
  - (b) arm B's men lost per war-score point are under half of arm A's.
- **If it is a farm:** the smallest fix that ends it by the same rule, re-run. The choices: a bombardment records a
  battle only past a higher floor, or scores less than a battle, or records no battle.
- **If neither holds:** refuted, with the numbers in the row.

## §4 Measuring a fix that moves the world

- Any fix that changes what the AI does or how a battle goes re-times the standing forty-turn series:
  `BASELINE_SERIES`, `tests/test_ai_intent_threat_migration.py` (~1896).
- Measure it from a frozen copy of the tree before the fix, using the `tools/_ic4_series_arms.py` idiom: arm 0 (the
  commit before) against the arm with the fix. That idiom runs named arms as child processes, each wrapping seams,
  and compares them against HEAD's prior.
- Attribute each mover, then re-pin `BASELINE_SERIES` with its history line, as row IC did.
- Expect movers from finds 4, 5 and 7, and from 12 if it is fixed. Finds 1, 2, 3 (a report that only reads), 6, 8,
  9, 10 and 11 should move nothing — say so per arm.
- An idle series will not exercise bombardment, so find 12 needs its own arms (§3).
- The wider harness: `tools/playtest_driver.py` takes `--seam module:fn=<spec>` (named at `diplomacy.py` ~3731) and
  plays the commanded arms; `tools/score_run.py` reads the series and the band. Rigs of the series shape stand beside
  `_ic4_series_arms.py`: `_ba6_`, `_b2_`, `_b3_`, `_f4_`, `_affairs_series_arms.py`, `_g2_`.
- If the battles move, re-read the deploy gate's France band (26 / 27 / 28, `tools/_oc_band_2026_11_18.json`).

## §5 Sizing and the split, decided now

- Twelve finds, at least eight likely real; find 3's sweep (about a dozen re-typed figures brought to one source);
  find 12's measure. Likely two sessions.
- If one session cannot hold all twelve at the standard, it splits by the code:
  - **FR-2a:** the combat finds (1, 3, 4, 5, 7, 12) first;
  - **FR-2b:** the road, read-back and client finds (2, 6, 8, 9, 10, 11) second.
- The session says which is done. A find is never half-shipped.
- Sizing, not pressure: nothing here is cut, or moved past the deploy, without the user's word. If the split is
  taken, row FR's size in `PRE_DEPLOY_PLAN.md` §2 moves from 2.0 to about 3.0.

## §6 Done when

- Every find is closed in the WS-R row, as one of:
  - CONFIRMED and fixed under its own id (WS-R1 …), with a behaviour test each and its class swept;
  - REFUTED, with its reason.
- The WS-R row reads closed (✅ CLOSED or FIXED at its head — §1's trap). `TestWSRTheReviewsUnconfirmedFinds` passes,
  and its strict xfail is dropped in the same commit.
- `.venv/Scripts/python.exe tools/defect_census.py --open` lists no open defect row.
- Every series mover is measured and re-pinned with its history (§4).
- **Records:**
  - `docs/STATUS.md` — the entry; ▶ NEXT UP → row TU;
  - `docs/SYSTEMS_REFERENCE.md` — a new section;
  - `docs/BUG_FIXES.md`;
  - `docs/PRE_DEPLOY_PLAN.md` row FR;
  - `docs/NEXT_SESSION_PROMPT.md` — row TU next;
  - this doc's §7.

## §7 Landing record

*(Written by Session FR-2 at its landing: per find, CONFIRMED / REFUTED, the id, the test, the siblings and the
measure.)*
