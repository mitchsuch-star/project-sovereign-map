# REPRO K1 — "The Garrison Leaves No Trace" (FA-R5)

Read-only reproduction pass, master `9ef38da8`, September 5 2026, run BEFORE FA
slice 14 was written. All probes under `scratchpad/s14/K_garrison_trace/`. No
repo file was touched.

## VERDICT: **REPRODUCED, and NARROWED in two directions — one that shrinks the fix, one that makes it more damning**

The row's four structural claims are all TRUE. But its scope sentence ("a
garrison assault reaches neither…") is **wrong for one of the three exit
paths**, and its build warning ("adding a log row makes FA-N21's own test (1)
false") is **false — that test was never built.**

---

## 1. The four claims, verified by symbol

| Claim | Verdict | Evidence |
|---|---|---|
| `CombatExecutor._resolve_garrison_combat` contains ZERO `log_event` calls | **TRUE** | `backend/commands/combat_executor.py:2864-3170`. In the whole 306-line body the only pipeline calls are `_post_combat_pipeline` (twice, both with `'skip_log_battle_event': True`) and `_attempt_region_capture`. No `log_event`, no `log_battle_event`. |
| `garrison_assault` not in `CAMPAIGN_LOG_TYPES` | **TRUE** | Measured: `filter_campaign_log` drops it at its very first gate (`if event_type not in CAMPAIGN_LOG_TYPES: continue`). |
| `garrison_destroyed` not in `CAMPAIGN_LOG_TYPES` | **TRUE** | Same. |
| `dispatch._build_headline` has no arm for either | **TRUE** | `dispatch.py` contains the substring `garrison` 4 times, all unrelated (`region_taken` advice copy, the `garrison_regen` turn-events whitelist ×2, a comment). Zero `_add()` sites and zero `HEADLINE_WEIGHTS` entries. `gazette.py` contains it zero times. |

---

## 2. What reproduces — measured on the shipped 1805 board

Four arms driven through the real resolver, player = France:

| path | events returned | `world.event_log` delta | campaign-log rows | headline |
|---|---|---|---|---|
| **HOLD** (both directions) | `garrison_assault` | **0** | **0** | **None** |
| **FALL → occupation** (fortified) | `garrison_destroyed` + `occupation_started` | **0** | **0** | **None** |
| FALL → instant capture (AI) | `conquest` | 1 × `region_captured` | 1 | `capital_lost` / `home_captured` / `region_taken` |
| FALL → instant capture (player, after answering) | `conquest` | 1 × `region_captured` (written by `capture_executor.handle_capture_choice`) | 1 | `capital_stormed` / `region_taken` |

**The measured player experience, arm A** — Austria's Mack batters the Paris
garrison from 25,000 to 12,500 and loses 6,250 men doing it. Next morning:

```
headline:       None
turn_events:    []
berthier_note:  "Your armies stand ready, Sire. The initiative is ours."
'Paris' in the whole dispatch JSON:      0 occurrences
'garrison' in the whole dispatch JSON:   0 occurrences
```

**Arm B is worse.** A fortified Paris, garrison 5,200, annihilated; Mack marches
in and begins an occupation timer standing inside the capital — `event_log`
delta 0, headline `None`, the same "the initiative is ours" note. The only thing
that ever recovers this is `enemy_on_our_soil` (weight 80) on the FOLLOWING
intel refresh, and its sentence is a lie about what happened: *"Mack has crossed
into Paris. No French corps stands in his path."* He did not cross into Paris.
He killed 5,200 defenders to get there.

### It is not a theoretical path

The 40-turn ambient board (`test_ai_intent_threat_migration._emit_series`,
reproduced byte-for-byte with a transparent counting wrapper — the instrumented
series equals `BASELINE_SERIES` exactly):

```
GARRISON_ASSAULTS = 6   (HELD 3, FELL 3)
  t10  ArchdukeCharles -> Milan     (KingdomOfItaly, capital)  hold, then fall
  t12  ArchdukeCharles -> Normandy  (FRANCE)                   hold, then fall
  t27  ArchdukeCharles -> Flanders  (FRANCE)                   hold, then fall
player-as-attacker: 0      player-as-defender: 4
```

Four of the six are on French soil with the player as defender, and two of those
four are the dark HOLD path.

---

## 3. What is false in the row

**(a) "reaches neither the campaign log nor the morning briefing" over-reaches.**
The FALL-to-capture path already reaches both, via `region_captured` written
downstream (`combat_executor._apply_ai_capture_choice` for the AI,
`capture_executor.handle_capture_choice` for the player's answered question).
Measured: *"Paris captured by Austria (secure)"*. **The dark paths are exactly
two: HOLD, and FALL-into-OCCUPATION.**

**(b) "adding a log row makes FA-N21's own test (1) — 'adds 0 rows to
`world.event_log`' — false, so that row's test has to be re-stated in the same
slice" is FALSE. That test does not exist.**

- `tests/test_enemy_phase_garrison_render.py` — the file FA-N21 names — does not exist.
- A suite-wide grep for `adds 0 rows`, `0 rows to` and `no battle_report` returns nothing.
- What slice 11 actually shipped for FA-N21/FA-23 is four tests in
  `tests/test_fa_slice11_the_briefing_tells_the_truth_2026_09_05.py`:
  `test_an_assault_on_our_own_garrison_survives_the_fog`,
  `test_the_lever_down_suppresses_it`,
  `test_it_does_not_leak_an_assault_on_somebody_else`,
  `test_the_client_has_a_structured_arm_for_it`. **None touches `world.event_log`.**

FA-N21's *Test* field is a proposal that was never built, not a landed pin. **No
test has to be re-stated. The fix is smaller than the row says.**

**(c) The "nine `== 160` pins" figure in `campaign_log.py` and `withdrawal.py`
prose is stale — there are TEN today.** Slice 11 added the tenth in its own file.

---

## 4. The real seam

`backend/commands/combat_executor.py::CombatExecutor._resolve_garrison_combat`
— three exits at HEAD `9ef38da8`:

| exit | what it returns |
|---|---|
| occupation | `garrison_destroyed` + `occupation_started` — **dark** |
| capture | `conquest`; `region_captured` logged downstream |
| hold | `garrison_assault` — **dark** |

The split is computed at `garrison_collapsed`. One helper called after that
split and before the three returns covers all three paths from one place.

Consumers that must agree: `campaign_log.CAMPAIGN_LOG_TYPES`, `CATEGORY_MAP`,
`format_event_oneliner`, `filter_campaign_log`; `dispatch.HEADLINE_WEIGHTS`,
`_HEADLINE_TEMPLATES`, `_build_headline`'s window loop.

---

## 5. Available inert log types (the slice-11 swap option) — there are none usable

`len(CAMPAIGN_LOG_TYPES) == 160`. A producer census over all of `backend/`
(inline `log_event({...})` regex, then a whole-file literal grep for every type
with no inline hit) gives 93 types with an inline producer, 67 without — of
which 61 are produced through helper wrappers and exactly **SIX** are truly
inert (zero occurrence anywhere in `backend/` outside `campaign_log.py`):

| inert type | category | membership pin that would go RED if retired |
|---|---|---|
| `ally_entry_accepted` | diplomacy | `tests/test_wb_c_war_entry.py` |
| `ally_entry_refused` | diplomacy | `tests/test_wb_c_war_entry.py` |
| `bargain_repudiated` | diplomacy | `tests/test_wb_c_war_entry.py` (+ a live negative pin) |
| `counter_bargain_rejected` | diplomacy | `tests/test_wb_c_war_entry.py` |
| `proposal_dropped_overflow` | diplomacy | `tests/test_session2_bugfixes.py` + a formatter pin |
| `proposal_expired_unseen` | diplomacy | `tests/test_session2_bugfixes.py` + a formatter pin |

All six are `diplomacy`; **all seventeen `combat`-category types have live
producers.** Slice 11's move is not available here: its swap
(`diplomatic_vassal_rebellion` → `vassal_broke_free`) worked because the dead
type and the live one were the same subject in the same family, so it touched
zero test files. Retiring a diplomacy type to make room for a combat one is
semantically wrong (`counter_bargain_accepted` has a producer while
`counter_bargain_rejected` does not — retiring the pair-half deforms a live
family) and reds a pin either way.

**Recommendation: bump 160 → 161 with a conscious-flip comment.** That is what
those ten pins exist to force. The ten:

```
tests/test_bph_a_term_ownership.py
tests/test_ca9_row3_a7_jealousy_note.py
tests/test_ca9_row3_phase_a.py
tests/test_ca9_row3_q2_council_command.py
tests/test_campaign_log.py
tests/test_fa_slice11_the_briefing_tells_the_truth_2026_09_05.py
tests/test_igr_a_honest_copy.py
tests/test_igr_b_campaign_log_readable.py
tests/test_igr_f_envoy_digest.py
tests/test_wo_slice4_the_capital_speaks.py
```

plus prose references in `backend/campaign_log.py` and
`backend/game_logic/withdrawal.py`, both saying "nine".

---

## 6. `battle_report` — feasible, but DO NOT BUILD IT

`generate_battle_report(battle_result, player_nation)` is a pure dict-over-dict
transform — no marshal lookups — so a synthetic garrison payload *runs*. Fed
both directions:

```
player-as-defender:  observation = "the Paris garrison carried the field, but the
                                    butcher's bill is steep, Sire."
                     modifier_breakdown = {"attacker": [], "defender": []}
player-as-attacker:  observation = "The battle unfolded without particular distinction."
```

Four reasons to dispose of FA-N21's third half rather than build it:

1. **The report's whole point is `modifier_breakdown`, and it cannot be filled.**
   `snapshot_defender_modifiers(defender, attacker, terrain, fortification_bonus)`
   takes a **Marshal**. CA8-19's ruling ("requires a defender object that does
   not exist") bites *here*, not on the log row. The defending half is
   structurally empty forever.
2. The ordinary case — the player repulsed from an enemy garrison — falls
   through `_pick_observation` to the flat "without particular distinction"
   line. That is a worse surface than the message already printed.
3. **It would double-render.** `enemy_phase_dialog.gd` renders
   `_format_berthier_report(action.battle_report)` in addition to slice 11's
   purpose-built structured garrison arm. The player would read the assault
   twice, once badly.
4. **It changes an unrelated render gate.** `main.gd`'s
   `var is_battle = response.has("battle_report") or …` — attaching one to a
   garrison result re-routes the muster "Attack Anyway" path.

---

## 7. What the fix would break

**The naval call site is safe and is a beneficiary.** `naval_executor.py` calls
the same resolver when a landing hits a defended capital. It returns
`garrison_result` verbatim after overwriting `["message"]`. A log row is
untouched by that overwrite, and the London landing assault *should* be on the
record. **No caller must not log.**

**The fog filter is already correct for both player directions — with ZERO new
fog code — provided the event carries `attacker_nation` and `defender_nation`.**
Measured with the type whitelisted at runtime:

```
ours   (defender_nation=France)        -> 1 row   [via _is_player_event]
theirs (attacker_nation=France)        -> 1 row   [via _is_player_event]
third-party (Austria vs KoI at Milan)  -> 0 rows  [no arm; falls through to the DROP default]
```

The function's default is drop, so a third-party assault silently vanishes.
Safe but wrong — the ambient board produces one (Milan, t10). One arm is needed,
mirroring `battle`'s.

**Two enforcement families are hard gates on the new type:**
`format_event_oneliner` must gain a handler or
`test_campaign_log_enforcement.py::TestAllWhitelistedTypesHaveFormatStrings`
fails; `CATEGORY_MAP["garrison_assault"] = "combat"` or three tests fail.
`test_campaign_log.py::test_allowed_types_pass` synthesizes
`{"type": t, "turn": 1, "nation": player_nation}` for every type — a new type
passes via `_is_player_event`'s `nation` check, so no action is needed, but do
not write a fog arm that `continue`s past a `nation`-only event.

**IGR-B is not touched.** `collapse_refusal_family` gates on type first. A
garrison row passes through as the same object, uncollapsed.

**Every reader of `world.event_log` in the backend is display/narrative** —
`campaign_log`, `dispatch` (×5 windows), `gazette`, `marshal_voice`,
`diplomatic_advisory`, `diplomatic_templates`. Nothing mechanical reads it.

---

## 8. Series risk — measured, not reasoned: ZERO

The 40-turn ambient board run twice under the exact `_emit_series` env
(`PYTHONHASHSEED=0`, `SOVEREIGN_SEED=historical`, `LLM_MODE=mock`), the second
time with the fix simulated — a `world.log_event({...})` on every garrison
assault, both paths:

```
arm 0 (control):        SERIES == BASELINE_SERIES   byte-for-byte
arm 1 (6 rows logged):  SERIES == BASELINE_SERIES   byte-for-byte
                        provinces map               identical
```

One caveat worth writing on the row: `world.event_log` saturates at
`MAX_EVENT_LOG_SIZE = 500` on turn 9 and stays pinned there for the remaining 31
turns. Six extra rows evict six of the oldest. Eviction is from the head
(`event_log[-500:]`), so every recent-window reader is unaffected; only a deep
Gazette `since_turn` scan could differ, and that is display. **M1–M7 are
untouched by construction** — the harness never calls
`_resolve_garrison_combat`; it calls `resolve_battle` directly.

---

## 9. Recommended build shape

One helper, three call sites, one headline arm, one fog arm. Zero new serialized
fields. Zero `.gd`.

**(a) `combat_executor.py`** — one private method beside the resolver, called at
the three exits. Emit the same type the client already renders, so log and
dialog cannot drift. `defender_nation` must be read BEFORE `capture_region`
flips it — on the capture path `old_controller` is already captured above.
Behind one flip lever so the series arm is provable.

**(b) `campaign_log.py`** — four edits, the slice-11 recipe: whitelist
(160→161 consciously), `CATEGORY_MAP` → `"combat"`, a `format_event_oneliner`
handler, and one fog arm beside `battle`'s (region intel FULL or PARTIAL — a
garrison figure is coarser than a battle). The player's own two directions never
reach that arm; they exit at `_is_player_event` above.

**(c) `dispatch.py`** — ONE new headline class. No existing class fits:
`enemy_on_our_soil` (80) is a presence reading and fires only after intel
refresh; `own_mauled` (85) is keyed on a marshal; `region_lost` (75) requires
the province to have changed hands. Proposed `garrison_assaulted`, weight 87 —
above `own_mauled` (85), below `own_broken` (90). Gated on
`event.get("defender_nation") == player_nation` so it is a WOUND class only
(the player's own repulse abroad is the `region_taken`/`victory_won` ladder's
business, and building it as a triumph re-opens CA8-D6). **Not** in
`STANDING_HEADLINE_CLASSES` — this is current news, not a standing condition
(PC-7's `marshal_reversal` trap).

**(d) Optional, cheap:** add `"garrison_assault"` to `gazette._WAR_TYPES`.

**(e) Do NOT build a `battle_report`.** Dispose FA-N21's third half at the
`_resolve_garrison_combat` docstring with the CA8-19 §10.5 reason.

### Falsifiable acceptance

1. A HOLD assault on the player's own capital writes exactly one `event_log` row
   and produces one campaign-log line naming the province and both loss figures.
2. The occupation path (fortified, `garrison_destroyed`) writes exactly one row —
   this is the path with no `region_captured` behind it.
3. The FALL-to-capture path writes two rows (the assault and `region_captured`)
   and the briefing still leads with `capital_lost`, not the assault (100 > 87).
4. A third-party assault (Austria vs KingdomOfItaly at Milan — the exact t10
   ambient case) is dropped at UNKNOWN and shown at PARTIAL.
5. Lever down ⇒ `event_log` delta is 0 on all three paths.
6. The morning after arm A, `"Paris"` appears in the dispatch ≥1 time (today: 0)
   and `berthier_note` is not "The initiative is ours."
