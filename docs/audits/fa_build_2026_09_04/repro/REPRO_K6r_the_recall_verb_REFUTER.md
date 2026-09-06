## Refutation report — REPRO C (FA-S9-D1 + FA-71)

**Critical context the report could not have:** the tree is **no longer clean**. Since the report the builder has landed **FA-N46, FA-N76, FA-N77 and FA-R5** (27 modified files). FA-N77 and FA-R5 each invalidate a specific claim below. All my measurements state which tree they were taken on.

---

### CONFIRMED (re-measured independently)

**1. The headline — verbatim.**
CLAIM: a save/load defeats the slice-9 attrition exemption and the sweep destroys the marshal.
MEASUREMENT (`r1_attrition.py`, working tree, real handler + real `to_dict`/`from_dict` + real sweep):
```
--- NO LOAD ---       in marshals before sweep: True   after: True
--- AFTER A LOAD ---  administrative=<ABSENT>
                      in marshals before sweep: True   after: False
  fallen_marshals: {'Murat': {... 'cause': 'attrition'}}
  EVENT: Murat has been eliminated by supply attrition at None
```
**VERDICT: CONFIRMED**, including the exact event string and the 22,000 / "5 actions per turn" figures.

**2. The AP farm — confirmed and *extended*.** CLAIM: max-1-admin resets on load, AP compounds. MEASUREMENT (`r2_apfarm.py`, working tree, **with FA-N76 active**): `4 → 5 → 6 → 7` over three transfers; FA-N76's offered-options guard **does not close it** (the options are rebuilt after the load, when `get_admin_marshals()` already reads 0, so `administrative_role` is legitimately offered every time). **CONFIRMED, and the just-landed guard is not a fix for it.**

**3. Parse collisions — every row exact.** My r4 initially returned all-`None`; that was **my** bug (`parse(text, game_state) -> Dict`, not `.action`). Corrected (`r5_parse_fixed.py`):
`recall the fleet` / `…to port` / `…to home waters` → `set_fleet_posture`; `recall Villeneuve`, `recall the squadron`, `recall Murat` → `None`; **`restore Murat to command` → `repair`**; `commission Grouchy` → `recruit_marshal`, `target='Grouchy'`, `marshal=None`. **CONFIRMED.** I add one the report missed: **bare `restore Murat` → `repair`** too.

**4. `MOCK_REACHABLE_ACTIONS` census.** len=52, `recruit_marshal` **absent**, `build_fleet`/`set_fleet_posture`/`naval_expedition`/`grant_pension` present. **Correction #1 to the prior repro CONFIRMED — the coverage gate is blind.**

**5. `test_serialization_enforcement` is structurally blind.** `create_fully_populated_marshal` sets none of the three fields; `vars()`=106, `to_dict`=106, **missing = `[]`**. **CONFIRMED.**

**6. The location hazard.** `get_nation_capital('France')` = `'Paris'` **after Paris falls to Austria**; `find_spawn_region` = `Paris → Berry → None`. And driven live: FA-71's `fix_shape` (a) restores **22,000 men into an Austria-controlled Franche-Comte**. **CONFIRMED — the row's own prescribed fix is the hazard.**

**7. Static census.** Two `administrative = True` writes (`disobedience.py:1836` wt / `meta_executor.py:1588`), one `= False` (`meta_executor.py:1559`); sole production caller of `handle_redemption_response` is `main.py`; player-nation gate present in `check_redemption_threshold`; `redemption_cooldown_until` serialized at the three cited lines; the arm writes **no trust**; **M1–M7 grep = 0** for `administrative|redemption|trust`. The ten `CAMPAIGN_LOG_TYPES` pin files are exactly the list given. Per-test line numbers in `test_administrative_role.py` (25/44/64/80/95/113/298/321/343/363) **all exact**. **CONFIRMED.**

**8. The recommended fix actually works** (`r9_fix_works.py`, fields carried by hand): post-load `administrative=True`, `get_admin_marshals=1`, **sweep spares him (pin b GREEN)**, and the second transfer is refused — `options = ['grant_autonomy', 'dismiss']`. **The farm closes.** I also confirmed the build shape survives the AP gate: `is_player_action_check = not is_ai_command`, demoted only when a *named* marshal is an enemy — so `marshal=None` still charges the admin AP.

---

### REFUTED

**A. "the ghost is counted as a FIELD marshal after a load (field: 7 → 8)" — REFUTED.**
MEASUREMENT: `POST-LOAD field=7`, not 8. Cause: the builder's **FA-N77** added `and marshal.strength > 0` to `get_field_marshals`. **Consequence the builder must know: the post-load ghost is now in NEITHER roster** — not `get_field_marshals` (strength 0) and not `get_admin_marshals` (flag gone). A Generals-screen recall chip built off `get_admin_marshals()` would not list him.

**B. "index[None] still ['Murat']; index['Franche-Comte'] still ['Lannes'] only" — REFUTED as stated.**
MEASUREMENT (`r8_index.py`, direct on `_marshals_by_region`): `index[None] = []` at every step; `index['Franche-Comte'] = ['Lannes','Murat']` at boot, after the freeze **and** after the restore. The freeze never removes him, so the debug restore's index is **accidentally correct** and `get_marshals_in_region_indexed` finds him without any refresh.
**But the hazard is real and it is created by the report's own recommendation.** Restoring at `find_spawn_region` (a *different* province) measures:
```
index['Franche-Comte'] = ['Lannes','Murat']    <- ghost persists
get_marshals_in_region_indexed('Paris') = []
get_marshals_in_region('Paris')         = ['Murat']
after refresh_marshal_indexes()          -> both correct
```
So `refresh_marshal_indexes()` is required — for the opposite reason to the one given.

**C. "a pre-fix save → restore gives 0 men at 'Paris' and still refunds the AP (1 → 0)" — REFUTED, and the truth is worse.**
MEASUREMENT: after a load the flag is gone, so `getattr(m,'administrative',False)` is False and the debug arm **cannot reach the restore branch**. It falls through and **re-freezes**: `"Murat -> ADMIN ROLE. 0 troops frozen. Max actions now: 6"`, `bonus_actions 1 → 2`.
The unstated consequence: `bonus_actions` **is** serialized and the flag is not, so **after the fix lands, every marshal frozen in a pre-fix save is permanently unrecallable, permanently a 0-strength ghost, and his +1 AP is permanent.** A load-time backfill is needed; the report has no row for it.

**D. "all green (70 in file)" — REFUTED.** `test_administrative_role.py` collects **22** tests (`grep -c "def test_"` = 22). 41 passed across that file *plus* `test_serialization_enforcement.py`. The per-test citations are exact; only the aggregate is wrong by 3×.

---

### NARROWED

**E. "3 `recruit_marshal` rows" → 4.** `jv32-commission-grouchy`, `jv32-recruit-marshal-suchet`, `jv32-appoint-marshalate`, **plus `jv32-recruit-infantry-unharmed`** — the negative guard, i.e. exactly the pattern the report recommends adding and did not notice already exists.

**F. "the copy fix is backend-only — zero `.gd` diff" — NARROWED.** The backend `msg` *is* rendered verbatim under the banner, and `redemption_dialog.gd` renders `text`/`description` verbatim (both supplied by the backend, so the fallback literal never fires). But `main.gd:4477` hard-codes a **client-side echo** — `"You transfer the marshal to the administrative staff."` — that the backend does not supply, and `main.gd:1536` holds a hard-coded typed-verb list `["grant_autonomy","dismiss","administrative_role"]`. Neither carries the *restoration promise*, so the claim holds for the promise rewrite specifically; it is false for the concept.

**G. Hazard #5 "no liveness guard … a captured man reaches the branch" — UNDERSTATED.** It does not merely reach it, it **completes**: `restore -> success=True, "Lannes restored from admin. 18,000 troops at Franche-Comte"` with `captured_by='Austria'` still set. A prisoner is conjured back into the field with his corps.

**H. "the round trip is net-positive in military actions" — NARROWED.** A *completed* round trip is military-AP **neutral** (measured `4 → 5 → 4`); it is the frozen *interval* that pays +1/turn free. As written the sentence contradicts the report's own behaviour test ("drops by exactly 1").

**I. Line numbers.** The zeroing is `disobedience.py:**1805-1806**` (1804 is the comment) — the report's own table is off by one, the class of error it criticises FA-71 for. Everything else it cites at HEAD checks out (`1798`, `1799`, `1604`, `1822`, `meta_executor.py:30/760/1559/2282`, `executor.py:1224`).

---

### What the builder must know that the report does not say

1. **The tree is not clean and four rows landed since.** `len(CAMPAIGN_LOG_TYPES)` is **161**, not 160, in all ten files — do not copy the report's number. FA-N77 masks the field-roster symptom; FA-N76 does **not** close the AP farm.
2. **A pre-fix-save backfill is required** (§C). Without it the fix strands every already-frozen marshal *and* his permanent AP.
3. **Second `ADMIN_ACTIONS` consumer the report never names:** `meta_executor.py:2106` (`is_admin = action in ADMIN_ACTIONS`), the third AP gate on the post-objection path. The report names only `executor.py:1224`.
4. **The freeze itself leaks into `_marshals_by_region`** — a 0-strength ghost sits under his old province for the entire administrative period. Pre-existing, unreported, and it is why the index looks "correct" after a same-province restore.
5. **`check_redemption_threshold`'s `administrative` guard is already unreachable** — `REDEMPTION_ASKS_THE_LIVING` returns on `strength <= 0` first. So the serialization fix does not re-arm the question for a frozen man; nothing there changes.
6. **The cooldown is stamped at the *answer*, not at the recall**, so a recall imposes no cooldown of its own. The only real brake on freeze→recall→freeze churn is the AP arithmetic, not `redemption_cooldown_until`.
7. Add `restore <name>` (bare) to the negative corpus guards alongside `restore <name> to command`.