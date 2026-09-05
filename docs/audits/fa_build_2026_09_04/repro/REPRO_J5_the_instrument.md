# REPRO J5 -- slice 15, the playtest-harness rows (20)

Repo at master `a1ed5c9d`. Read-only. All probes under
`<scratchpad>/repro/j5/`. Slice 8 ("The Instrument", Sept 2) and slices
1/2/3 (Sept 2-4) were read FIRST and settle six of the twenty.

## Summary

| row | verdict | measured mechanism |
|---|---|---|
| FA-36 | **ALREADY-FIXED** (FA slice 2, Sept 4) | `strategic._standalone_decision_rows` now emits an `awaiting_response`/`requires_input` row for an ORDER-FREE parked ask; `main.py:1424` promotes it to `pending_interrupt`. Probe 5 saw both, on a fresh 1805 boot. |
| FA-39 | **NARROWED / PARTLY-FIXED** | Third gap (threat) CLOSED by slice 8. Per-command parse provenance and `meta.script`/`llm_source` still absent: `parse_mode` and `parse_confidence` occur ZERO times in `tools/playtest_driver.py` AND in `backend/main.py`. |
| FA-N79 | **NARROWED -- same seam as FA-N86, and FA-N86 is the accurate framing** | `fog_hidden` occurs 0x in the driver. FA-N79's headline case (`actions == []`, no line at all) is the RARE arm; the COMMON case is a line that IS written with the fog sentence deleted -- measured 6/6 end turns on the shipped boot. |
| FA-72 | **REPRODUCED**, sub-claim (d) confirmed against the real producer | `_pick_dialogue_choice` under the DEFAULT `diplomacy: decline` returns `honor_defender` for a commitment paradox -- `"no"` matches `ho**no**r_defender`. Latent by frequency (0 paradoxes in 52 archived digests), LIVE in code. |
| FA-75 | **NARROWED -- the backend half of the fix is UNNECESSARY** | Blind spot real: the driver reads only `(GET /mailbox).envoy_digest`; `mailbox/activate` = 0, `pending_envoy` = 0 (both hits are comments). But `lapsed_offers` AND `pending_envoys` are ALREADY on the `GET /dispatch` payload the driver fetches every turn (`dispatch.py:2177`, `:2193`). No `_COMMAND_RESULT_SIMPLE_FIELDS` edit is owed. |
| FA-77 | **REPRODUCED** | The non-input `strategic_reports` loop (`Answerer.scan`, driver:881) digests a row only if it carries `battle_details` or `action == "combat"`; `order_status` occurs 0x in the whole driver. |
| FA-78 | **REPRODUCED and WIDER than filed** | `proposal_confirm` returns the literal `"confirm"` with `enabled: False` on options[0]. Also un-filed: the GENERIC accept arm picks a DISABLED `accept_settlement_offer` (probe 1). The row's "twelve times" count is wrong -- the archive has 3 such lines, not 12. |
| FA-79 | **REPRODUCED, headline settled** | `redemption: dismiss` -> `disobedience.handle_redemption_response` dismiss arm -> `world.destroy_marshal(..., cause="dismissed")`. It is genuinely destructive. Archive: exactly ONE redemption in 52 digests, answered `dismiss`, no outcome line, Bernadotte never named again. |
| FA-83 | **ALREADY-FIXED (mechanism) + REFUTED (coverage claim)** | Slice 8's FA-10/FA-74 built precisely the row's `fix_shape` (stale reply appended as a followup, one bounded retry per chain). And the corpus DOES contain a completed acceptance ladder: `1b-pacifist-austerlitz-r1/digest.md:262-263`, accept -> `settlement_confirm` -> `confirm_settlement`, no refusal note. |
| FA-84 | **PARTLY-FIXED** | Half 2 (the `=` banner) CLOSED by slice 8's `salient_line`. Half 1 survives NARROWED: slice 8's HIGH-only DISPATCH rail now carries `design_promoted`/`nation_eliminated`/`volte_face`/`crisis_*`/`third_party_peace`, but `ai_ai_proposal_refused` has NO dispatch type at all and `diplomatic_ai_ai_treaty`/`coercive_demand`/`coalition_dissolved` are MEDIUM and filtered out. `campaign_log` = 0x in the driver. |
| FA-85 | **REPRODUCED verbatim** | `naval_descent.json:7` still stages Soult at Normandy; `audit-naval/digest.md:164` and `:183` carry both refusals. |
| FA-89 | **NARROWED / PARTLY-FIXED** | Slice 8's FA-40 fixed the script drift (bombard at loop 2, `"scenario": "tutorial"`, INSIST policy, drift pin). Residue holds: `scenario_name` is serialized but never reaches a `/command` response, so no unattended run can assert a beat FIRED. |
| FA-90 | **NARROWED -- a wish list, one third already met** | All cited keys verified present and unread: `peace_ratification_summary` (main.py:683), `notifications` (main.py:1557), `action_command` (dotation.py:1096). No homeland/gauntlet scripts exist. But arm (1)'s /pending_envoy+activate loop IS FA-75 and arm (3)'s provenance IS FA-39. |
| FA-91 | **REPRODUCED, and the proposed test is GREEN today** | `get_instance_attributes` drops `_`-names. Probe 3 on a played 1805 world: to_dict->from_dict->to_dict divergences = **0**; marshal residue = exactly 10 names, all documented transients, **7 of them `_`-prefixed and invisible to the suite**. Row's exemplar `_recovery_destination` is misattributed -- it IS serialized. |
| FA-N34 | **NARROWED -- behavioural half REFUTED, vacuity half REPRODUCED** | FA-6 (slice 1) rewrote `_is_end_turn_phrasing` to whole-command equality; `"Davout, fortify until next turn"` -> `False` (probe 2). The two pins are still vacuous: all three needles live in the DOCSTRING and `"attack"`/`"recruit"` appear nowhere under any implementation. |
| FA-N35 | **REPRODUCED, but the row's fix instruction is now WRONG** | The three keys are in `DISPLAY_ONLY_KEYS`; 9 of 11 archived `vassal_rebellion_imminent` lines read `-> display-only`; `commitment_paradox` = 0 files. The row says to post "WITHOUT a `dialogue_id`" -- slice 0's FA-N5 changed the client so all four sites now SEND it (`main.gd:5435`, `:5450`). |
| FA-N86 | **REPRODUCED** | `fog_hidden_nations` present on 6/6 end turns of the shipped boot ("Britain, Russia, Prussia and 6 other courts stirred as well..."), 0 occurrences of "beyond our sight" across 52 archived digests. |
| FA-N87 | **ALREADY-FIXED** (slice 8, FA-37) | driver:1664 now reads `dig(morning["coalition_status"], "threat_level", "threat")`. The slice-8 landing block names FA-N87 explicitly. |
| FA-N89 | **REPRODUCED** | The meta dict (driver:1536-1542) is exactly {name, seed, llm, transport, policy, turns_requested, started, from_save, rng}. No scenario, cheats, strict, script, llm_source. |
| FA-102 | **REPRODUCED** | `reload` occurs 0x in the driver. |

---

## Per row

### FA-36 -- ALREADY-FIXED (do not build)

**Ran:** `probe_5_fa36_trace.py`, `probe_6_fa36_after6.py`.

Fresh 1805 boot, Ney with `strategic_order = None` and a parked `last_stand`:

```
DIRECT processor rows for Ney: [{'marshal': 'Ney', 'command': 'Last stand',
  'order_status': 'awaiting_response', 'requires_input': True,
  'interrupt_type': 'last_stand', ...}]
endpoint: 'strategic_reports' key present: True
endpoint: rows = 1  {'marshal': 'Ney', 'order_status': 'awaiting_response', 'requires_input': True}
endpoint pending_interrupt: True
```

And when the enemy has drawn off (probe 6, after 6 turns):

```
last_stand_is_live: (False, 'the enemy no longer stands in the field')
rows: [{'marshal': 'Ney', 'command': 'Last stand', 'order_status': 'retired',
        'decision_retired': True, 'message': "Ney's question is overtaken, Sire ..."}]
```

(a) **Seam:** `backend/commands/strategic.py::StrategicOrderProcessor._standalone_decision_rows`
(called from `process_strategic_orders`), plus `backend/main.py`'s existing
`if not response.get("pending_interrupt")` promotion. `STANDALONE_DECISION_TYPES`
is the roster.
(b) **The filed fix would break:** it prescribes copying the `/load` marshal-level
attach (main.py:4487-4494) to the end-turn build. Doing that TODAY would attach a
SECOND, unvalidated copy of the ask that bypasses `last_stand_is_live` -- i.e. it
would re-raise exactly the stale question slice 2 exists to retire, and would
overwrite the retired row's reason. Do not build it.
(c) **Minimal correct fix:** none. Row is closed; strike it, citing slice 2.
(d) **Pins:** `tests/test_fa_slice2_no_word_came_2026_09_04.py::TestAnOrderFreeQuestionReachesTheEndTurn::test_the_end_turn_response_promotes_it_for_headless_clients`
-- `assert rows and rows[0]["order_status"] == "retired", reply`.

---

### FA-39 -- STILL OPEN (two of three gaps), group C + A

**Ran:** probe 1 grep census; source reads of `backend/ai/schemas.py`,
`backend/main.py`, driver `meta`.

```
'parse_mode': 0    'parse_confidence': 0        (tools/playtest_driver.py)
grep -n "parse_mode|parse_confidence" backend/main.py  -> no matches
```

`ParseResult` really does carry the data (`schemas.py:88-89`:
`confidence: float = 0.9` / `mode: str = "mock"`), and `to_dict` already
emits `"confidence"`, `"mode"`, `"key_source"` (`schemas.py:117-118`), so
`parsed` at `backend/main.py:2703` (`parsed = parser.parse(...)`) has them in
hand. The row's `:31-32` cite is the class DOCSTRING (Sept-2 verification was
right).

(a) **Seams:** backend `backend/main.py` at the `/command` response build --
stamp from the `parsed` dict already in scope at `:2703`; driver
`Digest.command` (driver:455) and the `meta` literal (driver:1536-1542).
(b) **The filed fix would break:** nothing, but its THIRD clause ("take
`threat_level` for the LEDGER row from the end-turn /command response") is
already superseded -- slice 8 took it from the morning dispatch
(driver:1664). Building the row as written would move a working reader.
(c) **Minimal correct fix:** two display-only response keys (GR6 -- nothing
mechanical reads them), one `Digest.command` kwarg pair, and fold
`meta["script"]/["llm_source"]` into FA-N89's single meta edit.
(d) **Pins that would flip:** none. `tests/test_playtest_driver_instrument.py`
does not assert the meta key set; `tests/test_fa_slice8_the_instrument_2026_09_02.py::TestTheThreatTrajectoryExists::test_the_ledger_payload_has_no_threat_key`
pins the *ledger* half and is untouched.

---

### FA-N79 + FA-N86 -- STILL OPEN, ONE seam, group A

**Ran:** `probe_1_driver_pure.py` (grep), `probe_4_fog_and_interrupt.py`.

```
 t1: total_actions=1 nations=1 flat=1 fog_hidden_nations=1 fog_hidden_summary=0 driver_writes_a_line=True
      HIDDEN: Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
 ... (identical shape t2..t6)
'fog_hidden': 0   (occurrences in tools/playtest_driver.py)
$ grep -rl "beyond our sight" docs/audits/playtest_digests/ | wc -l   ->  0     (of 52 runs)
```

**Narrowing that matters for the build:** FA-N79 is framed on the
`actions == []` case (`Digest.enemy_phase`'s `if not actions: return`). On the
shipped boot that case did not occur once in six turns -- every turn had a
visible action AND a fog line. So the DOMINANT loss is FA-N86's framing: the
sentence is deleted from a line that IS written. Build FA-N86's shape and
FA-N79 falls out of it (move the fog emit ABOVE the `if not actions` guard).

(a) **Seam:** `tools/playtest_driver.py::Digest.enemy_phase` (driver:435).
Both call sites already have the raw dict: driver:1626 and the retry copy at
:1633 -- `digest.enemy_phase(_flatten_enemy_phase(response.get("enemy_phase")))`.
Producer: `backend/main.py::_build_visible_enemy_phase` sets
`fog_hidden_nations` / `fog_hidden_summary`; renderer
`enemy_phase_dialog.gd:104-108`.
(b) **The filed fix would break:** nothing. But note both rows also ask for a
stale-comment repair at driver:439 ("`_build_visible_enemy_phase` only strips
new_state") -- that comment is FALSE and sits three lines above a correct one
at :1116. Fix it in the same edit or the next reader repeats the mistake.
(c) **Minimal correct fix:** `def enemy_phase(self, actions, phase=None)`;
emit `fog_hidden_summary` / `fog_hidden_nations` lines BEFORE the
`if not actions: return`; add `hidden_courts` to the jsonl record; pass the raw
dict at both call sites. Also correct `docs/PLAYTESTING.md:309-311` (the
FULL-action-list claim).
(d) **Pins:** `tests/test_playtest_driver_instrument.py::TestBattleCounting::test_enemy_phase_battle_rows_counted`
calls `digest.enemy_phase([...])` positionally with ONE argument --
`assert digest.counters["battles"] == 1`. An OPTIONAL second parameter keeps it
green; a required one reds it. `tests/test_fa_slice8_the_instrument_2026_09_02.py::TestTheDigestDoubleCannotDrift::test_every_digest_method_the_driver_calls_exists`
checks existence only, not signature -- safe.

---

### FA-72 -- STILL OPEN, group B

**Ran:** `probe_1_driver_pure.py`; source read of `backend/game_logic/diplomacy.py:8475-8488`.

```
policy diplomacy = decline
_pick_dialogue_choice({'type':'commitment_paradox',
                       'options':[{'action':'honor_defender'},
                                  {'action':'break_defender_alliance'}]})
   -> honor_defender
```

The production payload matches the fixture exactly -- `diplomacy.py:8475`
`"options": [ {... "action": "honor_defender"}, {... "action":
"break_defender_alliance"} ]`, and the dialogue is pushed with
`"blocking": True`. So this is not a hypothetical shape.

**Latency, measured:** `grep -rl commitment_paradox docs/audits/playtest_digests/`
= 0 files. Latent because no paradox has fired in 52 runs -- not because the
driver cannot reach it.

(a) **Seam:** `tools/playtest_driver.py::Answerer._pick_dialogue_choice`, the
`find("decline", "reject", "refuse", "no")` line (driver:1359).
(b) **The filed fix would break:** the row says match against `_`-split TOKENS
of the option id. That is right for `honor_defender`, but it BREAKS three live
matches that depend on substring semantics -- `find("accept","agree","yes","sign")`
must still hit `accept_settlement_offer` (token `accept` -- fine) but
`find("confirm","yes","proceed","send")` must hit `confirm_pair_substitute`
(token `confirm` -- fine) and `find("defy","refuse")` must hit
`defy_ultimatum`. Those survive. The one that does NOT survive token-splitting
is any option id that is a single fused word, e.g. bare `"reject"` is fine but
a `"declineoffer"`-style id would be missed -- none observed, so token-splitting
is safe here PROVIDED the needle set is re-checked against the live option
vocabulary rather than assumed.
(c) **Minimal correct fix:** split on `_` AND compare whole tokens; drop the
`"no"` needle entirely (it earns nothing -- `decline`/`reject`/`refuse` cover
the vocabulary) and add explicit `paradox` / `last_stand` / `contact` policy
keys defaulting to the least-state-changing arm. Document in
`docs/PLAYTESTING.md` that `interrupt: first` means `fight_to_the_last` /
`attack_anyway`.
(d) **Pins:** none pin the needle list. `tests/test_playtest_driver_instrument.py`
tests `_option_id` preference order, not `find()`.

**Cross-row hazard: FA-N35 must not land without this row.** Un-skipping the
paradox popup while `"no"` still matches `honor_defender` makes a latent
war-declaration LIVE under the default policy.

---

### FA-75 -- STILL OPEN, but HALF THE FIX IS UNNECESSARY (group A + B)

**Ran:** grep census (probe 1); source reads of `backend/game_logic/dispatch.py`
and `backend/commands/meta_executor.py`.

```
'lapsed_offers': 0   'mailbox/activate': 0   'pending_envoy': 2 (both COMMENTS)
$ grep -n "/mailbox" tools/playtest_driver.py
  1588:  (transport.get("/mailbox") or {}).get("envoy_digest")
  1218:  self.t.post("/mailbox/respond", ...)
```

**The falsified sub-claim.** The row says "no `/command` layer forwards
`lapsed_offers` ... add it to `_COMMAND_RESULT_SIMPLE_FIELDS`". But
`backend/game_logic/dispatch.py:2176-2183` puts `lapsed_offers` ON THE MORNING
DISPATCH, and `:2185-2194` puts `pending_envoys` / `pending_envoy_count` there
too. `GET /dispatch` (main.py:4635) returns `world.last_morning_dispatch`, and
the driver already fetches it every turn into `morning` (driver:1653). Both
facts are one `morning.get(...)` away with **zero backend change**.

(a) **Seams:** evidence half -- `Digest.dispatch` (driver:686) or the
`ledger_line`/`dispatch` block at driver:1653-1672. Answering half --
`tools/playtest_driver.py` per-turn loop at driver:1584-1589 (the letter-book
read), which must additionally walk the non-digest `/mailbox` items and
`POST /mailbox/activate {mailbox_id}` before answering through the existing
dialogue arm.
(b) **The filed fix would break:** the backend tuple edit is dead weight, and
`_COMMAND_RESULT_SIMPLE_FIELDS` is a truthy-copy list -- adding a key that is
`[]` on almost every turn is harmless but pointless. Skip it.
(c) **Minimal correct fix:** (A-half, no behaviour change) print
`morning["lapsed_offers"]` and `morning["pending_envoys"]` as digest lines.
(B-half, behaviour) the activate loop. Ship A first; A alone converts the
blind spot into a *measured* one and costs no determinism.
(d) **Pins:** none.

---

### FA-77 -- STILL OPEN, group A

**Ran:** grep census; source read of `Answerer.scan` (driver:881-890).

```python
for report in response.get("strategic_reports") or []:
    if not isinstance(report, dict) or report.get("requires_input"):
        continue
    if isinstance(report.get("battle_details"), dict):
        self.d.battle(report["battle_details"])
    elif str(report.get("action") or "") == "combat":
        self.d.battle({"headline": ...})
```

`order_status` appears **0 times** in the whole 1756-line driver, so no
report's status or prose ever reaches the digest.

(a) **Seam:** `tools/playtest_driver.py::Answerer.scan`, the loop at driver:881.
(b) **The filed fix would break:** the row asks to digest EVERY non-input
report's `message` "as a bullet under the enemy-phase block". Two hazards:
(i) slice 2 now emits a `retired` row for every stale standalone decision, and
slice 3/3R emit rows for refusals -- an unfiltered dump adds ~1 line per
player marshal per turn (8 on the 1805 boot), which is the noise the IGR-B
lesson warns about; (ii) `scan` runs on FOLLOW-UP responses too, so the same
report can be digested twice in one chain.
(c) **Minimal correct fix:** digest the message only when `order_status`
CHANGED or is one of a named interesting set (`retired`, `cancelled`,
`blocked`, `completed`, `awaiting_response`), dedupe by `(marshal,
order_status, message)` within the post, and stamp the chosen interrupt
answer's meaning next to the popup line.
(d) **Pins:** `tests/test_playtest_driver_instrument.py::TestStrategicReportBattleCounting::test_battle_details_and_combat_rows_counted`
drives `answerer.scan({...strategic_reports...})` -- it asserts battle counts,
not line counts, so it stays green unless the new lines are counted as battles.

---

### FA-78 -- STILL OPEN and WIDER than filed, group B

**Ran:** `probe_1_driver_pure.py`.

```
type in DIALOGUE_TYPE_ANSWERS: True -> confirm
_pick_dialogue_choice(proposal_confirm w/ execute_proposal enabled=False) -> confirm
_enabled(options[0]) = False
accept-policy generic w/ disabled accept -> accept_settlement_offer      <-- NOT in the row
```

`_enabled` (driver:754) is consulted at exactly two places -- the petition arm
(driver:1020) and the interrupt arm (driver:934). The dialogue arm never
consults it, in EITHER branch: the type table returns a literal, and `find()`
scans options without filtering.

**Count corrected.** The row claims twelve pressings citing
`audit-propose/digest.md:9,23,59,74,100,123,149` and `audit-latewar-t20:41`.
Measured: `grep -c "refused: Making peace with Austria" audit-propose/digest.md`
= **2**, `audit-latewar-t20/digest.md` = **1**. Three, not twelve.

(a) **Seam:** `tools/playtest_driver.py::Answerer._pick_dialogue_choice`
(driver:1266), before the type table at driver:1338.
(b) **The filed fix would break:** "filter `options` through `_enabled` before
the type table" is right for the option-scan branches, but the type table's
`confirm` branch RETURNS A LITERAL when `find()` misses
(`return find(...) or "confirm"`). Filtering the list does not remove the
literal fallback -- the driver would still POST `"confirm"` against an
all-disabled confirm dialogue. The fix must ALSO make the literal fallbacks
conditional on there being an enabled option at all.
(c) **Minimal correct fix:** filter `options`/`keywords` through `_enabled`
at the top of `_pick_dialogue_choice`; when nothing is enabled, log
`(disabled: <options[0].description>)` and return `None` (left standing) --
never the literal.
(d) **Pins:** `tests/test_playtest_driver_instrument.py` clarification/envoy
tests use enabled-by-default payloads and stay green. Nothing pins the
literal fallback.

---

### FA-79 -- STILL OPEN, group B (+ an A third). **Headline settled below.**

**Ran:** probe 1; source reads of `disobedience.py:1851-1873`; archive census.

```
=== POLICY DEFAULTS ===  redemption = dismiss   petition = first_enabled
$ grep -rn "POPUP redemption" docs/audits/playtest_digests/*/digest.md | wc -l   -> 1
audit-flagship-mock/digest.md:208:  - POPUP redemption: Bernadotte, 9 -> dismiss
$ awk 'NR>208 && /Bernadotte/' audit-flagship-mock/digest.md   -> (empty)
audit-flagship-mock petition answers: 10 jealousy_confrontation, 2 rivalry,
                                       2 shadow_command, 2 fontainebleau
```

**The explicit question -- is `redemption: dismiss` really destructive today?
YES.** `disobedience.py`'s dismiss arm:

```python
if marshal_name in world.marshals:
    world.destroy_marshal(marshal_name, cause="dismissed", log=False)
```

`WorldState.destroy_marshal` is the PC15-1 single removal seam: it writes a
`fallen_marshals` tombstone and takes the marshal off the roster permanently.
The arm also mutates authority (+10, capped 100) and transfers or disperses
the whole corps.

**Least-state-changing default: `grant_autonomy`.** Compared arm by arm:
- `grant_autonomy` -- sets `autonomous`, `autonomy_turns = 3`,
  `autonomy_reason`, zeroes three counters. **Self-expiring in 3 turns**, no
  roster change, no strength change, no permanent economy change. It does
  change AI behaviour for those 3 turns (autonomous attacks), which the digest
  can and should say.
- `administrative_role` -- `strength = 0`, `location = None`,
  `world.bonus_actions += 1` **permanently**, `clear_iron_resolve()`. That is a
  permanent AP grant plus a corps removed from the field with no restoration
  path (the FA-S9-D1 gate). Strictly worse than autonomy.
- `dismiss` -- destroys.

So the row's `grant_autonomy` recommendation is CORRECT, and the ranking is
`grant_autonomy` < `administrative_role` < `dismiss`. A `leave` value (log and
do not answer) is NOT a good default: WO-41 made the question survive the save,
so leaving it standing would just re-raise it every turn and the arc would stay
unmeasured -- which is the row's complaint.

(a) **Seams:** `POLICY_DEFAULTS["redemption"]` (driver:153) and
`POLICY_DEFAULTS["petition"]` (driver:156); the redemption arm at driver:1061-1067
and the petition arm at driver:1014-1029; `Answerer.scan`'s followup handling
(the `/respond_to_redemption` and `/marshal_petition_response` REPLY messages
are never digested).
(b) **The filed fix would break:** `petition: rotate` (cycle enabled arms per
kind) is the one to be careful with -- it makes the digest non-reproducible
against the archive AND makes each run's reward economy depend on petition
ORDER, so two runs of the same script at the same seed still match (the
rotation is deterministic) but no archived digest can be regenerated. Say so
loudly. `paid_first` additionally spends AP that the scripted commands were
budgeted for, which will change refusal counts everywhere downstream.
(c) **Minimal correct fix (land in two pieces):** (A, no behaviour) write the
`/respond_to_redemption` and `/marshal_petition_response` result `message`
into the digest -- one `self.d.note(...)` per arm; (B, behaviour) flip the
default to `grant_autonomy` and add `--redemption` to argparse (it has no CLI
flag today), and add `petition: rotate` as an OPT-IN value, never the default.
(d) **Pins:** none assert `POLICY_DEFAULTS["redemption"]`. Grep found no test
naming `"dismiss"` as a driver default.

---

### FA-83 -- ALREADY-FIXED (mechanism) + REFUTED (coverage claim)

**Ran:** archive census; source read of driver:1157-1196.

The row's own `fix_shape` -- "after any refusal carrying `stale_dialogue: True`,
re-read the current dialogue ... and answer THAT id" -- is what slice 8 built:

```python
stale = bool(reply.get("stale_dialogue"))
if did is not None:
    if stale:
        self._stale_refusals[did] = self._stale_refusals.get(did, 0) + 1
        self.d.discount_answer("diplomatic_dialogue", label, choice)
    else:
        self._answered_dialogue_ids.add(did)
...
followups.append(reply)     # "The reply CARRIES the dialogue actually on top"
```

with a bound of one retry per chain (driver:1094-1101). Slice 8's landing block
measures it: master 4/4/4 offers left standing vs 0/0/0 after.

**The coverage claim is FALSE against the committed archive.** The row and the
Sept-2 verification both say "zero successes"; both scoped themselves to the
nine `audit-*` runs. Over all 52:

```
1b-kingmaker-*: 1,1,3   1b-pacifist-*: 4,3,4   audit-latewar-t20: 3
wo5-propose-arm{,-review}: 2,2
1b-pacifist-austerlitz-r1/digest.md:262  POPUP diplomatic_dialogue: incoming_settlement_offer -> accept_settlement_offer
                                    :263  POPUP diplomatic_dialogue: settlement_confirm -> confirm_settlement
```

No `refused` note under either line. The accept ladder completed.

(a) **Seam:** `backend/commands/diplomatic_executor.py`'s W6-0 stale guard
(the row's `:3405-3431`) -- unchanged and correct; the driver seam is closed.
(b) **The filed fix would break:** re-implementing it now would add a SECOND
retry path beside slice 8's bounded one and re-open the ANSWER CYCLE the
slice-8 record says an independent refuter measured (4/4/2 cycles across three
replicates on FA-74's naive shape).
(c) **Minimal correct fix:** none. Strike the row; move its one surviving
residue -- "no archived run has ratified a MULTILATERAL settlement or reached
the Proclamation" -- onto FA-90, where it belongs.
(d) **Pins:** `tests/test_fa_slice8_the_instrument_2026_09_02.py::TestAStaleRefusalIsNotAnAnswer::test_the_offer_is_answered_again_when_it_comes_back`
and `::TestTheRetryIsBounded::test_a_surface_that_goes_stale_twice_is_left_standing_with_a_reason`.

---

### FA-84 -- PARTLY-FIXED; half 1 survives NARROWED, group A

**Half 2 (the banner) is CLOSED.** slice 8 replaced `first_line` with
`salient_line` in `Digest.enemy_phase` (driver:534) and made the capture caption
`matching_line(...)`. Note the ARCHIVE still shows the old artefact
(`audit-naval/digest.md` turn 12: `... . ======================================== . ...`)
-- the fix is landed, the evidence is stale.

**Half 1 (campaign-log blindness) survives, narrowed.** `campaign_log` occurs
0x in the driver. Slice 8's HIGH-only DISPATCH rail (driver:704-714) recovers
part of the row's own list, measured against
`backend/game_logic/dispatch.py::_DIPLOMATIC_EVENT_PRIORITY`:

| row's named type | today |
|---|---|
| `design_promoted` | HIGH -- **now visible** |
| `nation_eliminated` | HIGH -- **now visible** |
| `volte_face`, `crisis_brewing`, `crisis_passed`, `third_party_peace`, `diplomatic_coalition_formed` | HIGH -- visible |
| `diplomatic_ai_ai_treaty` | **MEDIUM -- filtered out** |
| `coercive_demand`, `diplomatic_coalition_dissolved` | **MEDIUM -- filtered out** |
| `ai_ai_proposal_refused` | **no dispatch type at all** -- campaign-log only (`campaign_log.py:137`) |

Plus the rail is capped at `MAX_RAIL_ROWS = 6` with a `+N more` tail.

(a) **Seam:** the per-turn loop after `/dispatch` (driver:1666-1672).
`GET /campaign_log` (main.py:4573) is fog-filtered and IGR-B-collapsed already.
(b) **The filed fix would break:** the row's allowlist duplicates types the
rail now prints, so an unconditional add would DOUBLE-print `design_promoted`,
`nation_eliminated`, `volte_face` etc. every turn.
(c) **Minimal correct fix:** read `GET /campaign_log` for the just-ended turn
and print only the types the rail does NOT already carry -- i.e. the
campaign-log-only and MEDIUM-graded diplomatic families -- derived from
`_DIPLOMATIC_EVENT_PRIORITY` rather than hand-listed, so slice 8's drift pin
keeps governing it. It is a GET, so determinism is untouched.
(d) **Pins:** `tests/test_fa_slice8_the_instrument_2026_09_02.py::TestTheDispatchLineCarriesTheRail::test_the_families_this_row_was_filed_for_are_graded_high`
is the drift pin over `_DIPLOMATIC_EVENT_PRIORITY`; a re-grading to MEDIUM reds
it. Reuse it, do not duplicate it.

---

### FA-85 -- REPRODUCED verbatim, group D (script)

**Ran:** file reads + archive read.

```
tools/playtest_scripts/naval_descent.json
  "2": ["Soult, march to Normandy", "build ships"]
  "12": ["land Soult in Munster with 12,000 men"]
  "13": ["land Soult in Munster confirmed"]

audit-naval/digest.md:164 CMD `land Soult in Munster with 12,000 men` -> X An expedition
  assembles at a dockyard, Sire - Soult must stand at one of our yards: Brittany, Flanders, Provence.
audit-naval/digest.md:183 (same)
$ grep -in "expedition" audit-naval/digest.md   -> only those two refusals
```

France's authored dockyards are FOUR -- `europe_1805.json` navies.France
`"dockyards": ["Brittany","Provence","Flanders","Bordelais"]` -- and the live
refusal names THREE, because `naval.controlled_dockyards` filters by control
(Bordelais was not held at that turn). The row's "France's authored yards are
Brittany/Provence/Flanders/Bordelais" is right; the message is the CONTROLLED
subset. A fixer must read `controlled_dockyards`, not the authored list.

(a) **Seams:** the script `tools/playtest_scripts/naval_descent.json:7`;
the gate `backend/commands/naval_executor.py::_execute_naval_expedition`
(the `loc_controller == marshal.nation and location not in yards` arm).
(b) **The filed fix would break:** "use Ney, already at Flanders, as the
landing marshal" collides with the script's OWN turns 6/8/11/14
(`Ney, march to London`) -- Ney is the Descent arm. Re-target Soult to
Brittany or Flanders instead, and note that Flanders is also a
`camp_provinces` entry, so parking Soult there may perturb the Descent
staging the script exists to measure. **Brittany is the safe yard.**
(c) **Minimal correct fix:** turn 2 -> `Soult, march to Brittany`; keep the
`land` at 12/13 (Brittany is 1-2 marches, so verify arrival by reading the
digest, or move `land` to a later index); plus the driver guard the row asks
for (mark a run `SCRIPT PRECONDITION` when every `land`/`naval_expedition`
line is refused).
(d) **Pins:** none pin `naval_descent.json`. `tests/test_naval_descent.py` and
`tests/test_naval_free_ireland.py` test the mechanic, not the script.

---

### FA-89 -- PARTLY-FIXED; residue is group C

**Slice 8's FA-40 closed the sharper half.** `tutorial_lesson.json` today:
`"scenario": "tutorial"`, the bombard at loop **2** (not 4),
`"policy": {"objection": "insist"}`, and a `_note` naming the drift pin.
`args.scenario = args.scenario or script.get("scenario") or ""` (driver:1500)
gives the script its own board.

**Residue.** `scenario_name` is serialized (`world_state.py:6898`) and read by
`dotation.py:210` / `jealousy.py:212` / `save_manager.py:266`, but
`grep -n "scenario_name" backend/main.py` returns **nothing** -- it never
reaches a response. The overlay's `STEPS` (:52), `_derive_step_for_turn` (:297),
`observe` (:313) are client-side; the driver cannot assert a beat FIRED.

(a) **Seam:** a display-only `tutorial_step` on `/command` responses when
`world.scenario_name == "tutorial"` (or `GET /tutorial_state`), derived from
the SAME payload predicates `_derive_step_for_turn`/`observe` read.
(b) **The filed fix would break:** the row's `--strict` clause ("fails when a
scripted beat's precondition is refused") would turn slice 8's DELIBERATE
refusal into a run failure -- the slice-8 record states "the only refusal left
in either arm is the one the card explicitly TEACHES". Do not build that clause.
(c) **Minimal correct fix:** the display-only key + a `SCHOOL: step N` digest
line. It is genuinely GR6 -- nothing mechanical may read it, and the overlay
must keep deriving its own step (a second source would drift).
(d) **Pins:** `tests/test_fa_slice8_the_instrument_2026_09_02.py::TestTheTutorialScriptMirrorsTheShippedLesson::test_every_suggested_command_is_issued_at_its_own_gate`
and `::test_the_driver_reads_the_scripts_scenario` already own the static half.

---

### FA-90 -- NARROWED, group D (a roll-up, not a defect)

**Ran:** grep census (probe 1) + backend key verification.

```
peace_ratification_summary  -> backend/main.py:683  (driver: 0)
response["notifications"]   -> backend/main.py:1557 (driver: 0)
action_command "grant {marshal} a rente" -> dotation.py:1096 (driver: 0)
tools/playtest_scripts/{homeland*,gauntlet*}  -> 0 files
```

Every citation is accurate. But arm (1) is FA-75's activate loop plus a
settlement ladder; arm (3)'s provenance half IS FA-39. Only three things here
are genuinely unowned: (i) the `peace_ratification_summary` digest line,
(ii) the `--reward` notification-driven arm, (iii) the two committed scripts.

(a) **Seams:** `POLICY_DEFAULTS` + argparse (driver:125, :1719) for the new
policy values; a new `Digest` line for the ratification summary; two new files
under `tools/playtest_scripts/`.
(b) **The filed fix would break:** arm (2) says the reward arm should also
"type the rail's last-stand words ('fight to the last'/'attempt breakout') so a
parked fate question (FA-36) is answered when raised" -- **that is now
redundant and harmful**: FA-36 is closed, the ask reaches
`pending_interrupt`, and the driver's interrupt arm answers it by POST. Typing
the words as a COMMAND would race the popup answer and re-enter the FA-N2
typed-answer router.
(c) **Minimal correct fix:** build (i) and (ii) only after FA-75 and FA-39
land (they are its prerequisites), and file the two scripts as separate work.
(d) **Pins:** none.

---

### FA-91 -- REPRODUCED; the proposed test is GREEN today, group E

**Ran:** `probe_3_fa91_census.py` -- 1805 boot, one attack, three end turns.

```
=== (a) to_dict -> from_dict -> to_dict divergences: 0

=== (b) unserialized instance attributes, INCLUDING _-prefixed ===
   COORDINATION_TRANSIENT_FIELDS = 12
   marshal._display_adjacent_atk            documented  (9 marshals)
   marshal._display_combined_arms_atk       documented  (9 marshals)
   ... (7 _-prefixed in total)
   marshal.sovereign_presence               documented  (10 marshals)
   marshal.total_coordination_attack_bonus  documented  (9 marshals)
   marshal.total_coordination_defense_bonus documented  (9 marshals)

   world attrs not in to_dict: 53      (51 _-prefixed caches + TWO PUBLIC:)
     nation_capitals
     positive_threat_delta_this_turn

=== the private-name filter, measured ===
   marshal private attrs on a PLAYED world: [_display_adjacent_atk, _display_combined_arms_atk,
     _display_combined_arms_def, _display_coordination_atk, _display_coordination_def,
     _display_dedicated_atk, _display_dedicated_def, _recovery_destination]
   of which ARE in to_dict: ['_recovery_destination']
```

**Three corrections to the row, all measured:**
1. `_recovery_destination` **IS serialized**. It is the one private name that
   reaches `to_dict`. IGR-X1 was a `del` on a missing attribute
   (`enemy_ai.py`), a different defect class. The row's headline exemplar is
   misattributed -- exactly as the Sept-2 verification said.
2. The `_`-filter blind spot is REAL but its live population is the SEVEN
   `_display_*` transients, all already named in
   `Marshal.COORDINATION_TRANSIENT_FIELDS` (12 entries; `KNOWN_EXCLUSIONS`
   names 2 of them + 3 computed properties).
3. **New, unfiled:** the WORLD has two PUBLIC unserialized attributes --
   `nation_capitals` (re-derived, see the NA-6c comment at
   `world_state.py:7491`) and `positive_threat_delta_this_turn` (reset in
   `from_dict` at `:7907`). Both are deliberate, neither is documented as an
   exclusion, and the census will RED on them unless the allow-set names them.

(a) **Seams:** `tests/test_serialization_enforcement.py::get_instance_attributes`
(the `not k.startswith('_')` filter) and `KNOWN_EXCLUSIONS`; the world test
that asserts `to_dict` KEYS on a fresh legacy world.
(b) **The filed fix would break:** the row's allow-set is
`Marshal.COORDINATION_TRANSIENT_FIELDS | WORLD_TRANSIENT_CACHES` -- there is no
`WORLD_TRANSIENT_CACHES` constant, and the two PUBLIC world fields above are in
neither set, so the test as specified reds on its first run.
(c) **Minimal correct fix:** the new file the row asks for, with the allow-set
spelled as `COORDINATION_TRANSIENT_FIELDS` + every `_`-prefixed world attr +
the two named public exceptions with their reasons; keep the round-trip
assertion (measured 0 divergences, so it lands green).
(d) **Pins:** `tests/test_serialization_enforcement.py::TestMarshalSerialization::test_all_marshal_fields_serialized`
-- `assert not missing, ...` -- stays green; the new file is additive.

---

### FA-N34 -- NARROWED (behavioural half REFUTED), group E

**Ran:** `probe_2_fan34_vacuity.py`.

```
=== does the SHIPPED gate still eat the row's sentence? ===
   'Davout, fortify until next turn'      -> False
   'Murat, wait until next turn'          -> False
   'end turn' / 'next turn.' / '  end turn  ' -> True
```

FA-6 (slice 1, Sept 2) rewrote `_is_end_turn_phrasing` to
`return c == "end turn" or c == "end_turn" or c == "next turn"`. The row's
"the repro above shows 'Davout, fortify until next turn' being eaten" is
**no longer true**.

The vacuity survives:

```
   'end turn'     body=True  docstring=True  code=True
   'end_turn'     body=True  docstring=True  code=True
   'next turn'    body=True  docstring=True  code=True
   'find('        body=True  docstring=False code=True   <- the punctuation trim, not the gate
   'attack'       body=False docstring=False code=False
   all three needles present in the DOCSTRING alone: True
```

Delete the `return` line entirely and BOTH pins stay green: the three needles
survive in the docstring and `find(` survives in the `".!? \t".find(...)` trim
loop. `assert "attack" not in body and "recruit" not in body` can never fail
under any implementation.

(a) **Seams:** `tests/test_review_2026_08_30.py::TestTheEndTurnSynonymsMeetTheGate::test_the_helper_claims_every_phrasing_the_parser_accepts`
and `::test_an_ordinary_command_is_not_swallowed`.
(b) **The filed fix would break:** nothing, but its premise is stale -- the fix
must be built against the CURRENT whole-command predicate, not the substring
one the row describes, or the rewritten pin will encode the wrong rule.
(c) **Minimal correct fix:** extract the return expression by regex, build the
matcher in Python (lower, strip, trim `.!? \t`, compare to the three literals),
and run it over a positive list (`end turn`, `next turn`, `END TURN`,
`  end turn  `, `next turn.`) and a NEGATIVE list (`Davout, fortify until next
turn`, `Murat, wait until next turn`, `Ney, hold Bavaria until the end turn`).
Delete the `attack`/`recruit` assertion outright. Add a self-check that the pin
REDS when the three literals are replaced by a bare `"turn"`.
(d) **Pins:** the two above are the ones being rewritten; nothing else reads
`_is_end_turn_phrasing`'s source text.

---

### FA-N35 -- REPRODUCED; **the row's fix instruction is now WRONG**, group B

**Ran:** probe 1; archive census; source reads of `main.gd` and the three popups.

```
DISPLAY_ONLY_KEYS = ('coalition_popup', 'diplomatic_sabotage',
   'vassal_rebellion_imminent', 'nation_proclamation', 'proposal_result',
   'commitment_paradox_popup', 'battle_diorama')
vassal_rebellion_imminent across the archive: 11 occurrences, 9 read '-> display-only'
commitment_paradox: 0 files
```

**The row says to post "WITHOUT a `dialogue_id`, so the harness reproduces the
client's real wire shape". That is the PRE-slice-0 shape.** FA-N5 (slice 0,
Sept 2) changed every client site:

```gdscript
# main.gd:5435  (vassal rebellion)
api_client.send_dialogue_response(action, _on_command_result, int(data.get("dialogue_id", -1)))
# main.gd:5450  (paradox)
api_client.send_dialogue_response(1, _on_command_result, int(data.get("dialogue_id", -1)))
```

and `api_client.gd:233-238` omits the field only for `-1`. Building the row as
written reproduces the exact defect FA-N5/FA-N37 were landed to kill ("Accept
Risk on the vassal-rebellion modal SIGNS A TREATY").

Two more facts a builder needs:
- the payloads carry no options list, and the CLIENT maps its own words:
  `invest -> invest_vassal_rebellion`, `garrison -> garrison_vassal_rebellion`,
  `accept -> accept_vassal_rebellion` (main.gd:5424-5428); the paradox sends a
  bare INDEX (1 or 2), not a keyword.
- `diplomacy.py:8494` stamps `paradox_popup["dialogue_id"]` from the pushed
  dialogue, so the id is available on the popup payload.

(a) **Seams:** `tools/playtest_driver.py::DISPLAY_ONLY_KEYS` (driver:216) and
`Answerer.scan`'s display-only loop (driver:865).
(b) **The filed fix would break:** as above -- and see the cross-row hazard:
un-skipping `commitment_paradox_popup` while FA-72's `"no"` needle stands makes
`honor_defender` the default answer, i.e. the driver declares war on the ally's
attacker under `--diplomacy decline`.
(c) **Minimal correct fix:** move the three keys out of `DISPLAY_ONLY_KEYS`;
give each its own arm posting the client's own action string (or index) **WITH**
`dialogue_id` from the payload; add a policy key per family whose default is the
least-state-changing arm (`invest` for rebellion -- it spends gold but keeps the
vassal; `overlook` for sabotage; `break_defender_alliance` vs `honor_defender`
is a real design choice and must be an explicit `paradox` policy key, not a
needle accident). Keep `battle_diorama` / `nation_proclamation` /
`proposal_result` / `coalition_popup` display-only as the negative control.
(d) **Pins:** none pin `DISPLAY_ONLY_KEYS`. `tests/test_fa_slice8_the_instrument_2026_09_02.py::TestTheDigestDoubleCannotDrift`
checks method existence only.

---

### FA-N86 -- see FA-N79 above (one seam, land together)

---

### FA-N87 -- ALREADY-FIXED (do not build)

driver:1656-1665:

```python
# FA-37 / FA-39: `threat` sat in `ledger_line`'s signature and never printed.
# ... The figure lives on the morning dispatch, under `coalition_status`.
digest.ledger_line(dig(ledger, "treasury", "gold"),
                   dig(ledger, "net_gold", "net"),
                   dig(morning.get("coalition_status"), "threat_level", "threat"),
                   ...)
```

The slice-8 landing block names FA-N87 explicitly: "(That half is also filed as
FA-N87 and as FA-39's third gap; both are closed by this edit.)"

Pins: `tests/test_fa_slice8_the_instrument_2026_09_02.py::TestTheThreatTrajectoryExists::test_the_ledger_payload_has_no_threat_key`
and `::test_the_dispatch_payload_carries_it`, plus
`::TestTheCallSitesActuallyUseThem::test_a_real_run_prints_a_threat_figure`.
**Strike the row.**

---

### FA-N89 -- REPRODUCED, group A

driver:1536-1542:

```python
digest = Digest(out_dir, {
    "name": args.name, "seed": args.seed, "llm": args.llm,
    "transport": transport.label, "policy": policy,
    "turns_requested": args.turns, "started": time.strftime("%Y-%m-%d %H:%M"),
    "from_save": args.from_save or "",
    "rng": rng_meta,
})
```

No `scenario`, `cheats`, `strict`, `script`, `llm_source`. `args.cheats` occurs
once (the argparse definition); `args.scenario` reaches only the `/new_game`
POST at driver:1556 and the precedence line at :1500.

(a) **Seam:** the meta literal above, and the header line in
`Digest.__init__` (driver:427-430).
(b) **The filed fix would break:** nothing. Its (b) clause -- a drift pin
parsing `main()`'s argparse `dest` set by AST -- is the right idiom but must
carry an explicit "not recorded, and why" allow-list, or every new flag reds it.
(c) **Minimal correct fix:** fold into FA-39's single meta edit --
`scenario`, `cheats`, `strict`, `script`, `llm_source` -- and name the scenario
in the header line when non-empty. Correct `docs/PLAYTESTING.md:312`.
(d) **Pins:** none assert the meta key set.

---

### FA-102 -- REPRODUCED, group D, **with a determinism trap**

`reload` occurs 0x in the driver. `--save-at` POSTs `/save` (driver:1618-1622)
and `--from-save` POSTs `/load` (driver:1283-1290 region) drained at boot.

(a) **Seam:** the per-turn loop, immediately after the `end turn` +
`drain` block (driver:1624-1642) and **before** the next iteration's
`seed_module_rng(args.seed, current_turn)` at driver:1578.
(b) **The filed fix would break its own contract.** The row promises
"with `--reload-every 1` the digest must be byte-identical to the no-reload
run of the same script and seed, load lines aside." Two reasons it will not be:
(i) the module RNG is reseeded ONLY at the turn boundary from
`(seed, world_turn)` -- so any POST inserted MID-turn shifts every draw after
it in that turn; (ii) `/load` re-attaches pending questions and the row wants
them drained through `drain()`, which POSTs answers -- those answers are extra
state changes the no-reload run never made. Placing the reload at the turn
boundary (after `end turn`'s drain, before the next reseed) fixes (i); (ii)
must be stated as an exception in the contract, not asserted away.
(c) **Minimal correct fix:** `--reload-every N` at the turn boundary; stamp the
round trip; state the contract as "byte-identical modulo the load lines AND any
answer the load re-raises", and make the re-raised set part of the digest so a
transparency defect is legible rather than silently absorbed.
(d) **Pins:** none.

---

## Cross-row findings

1. **Six of the twenty are closed or half-closed by work that landed after the
   audit.** FA-36 (slice 2), FA-N87 + FA-84-half-2 + FA-89-sharper-half +
   FA-83-mechanism (slice 8), FA-N34-behavioural-half (slice 1). A builder who
   works the rows top-down without this pass will re-open two of them.

2. **Ordering constraint: FA-72 MUST land before or with FA-N35.** Un-skipping
   `commitment_paradox_popup` while `find("...","no")` matches `honor_defender`
   turns a latent war declaration into the default answer under
   `--diplomacy decline`. Confirmed against the production payload
   (`diplomacy.py:8475`, `options[0].action == "honor_defender"`,
   `"blocking": True`).

3. **FA-N35's fix instruction was invalidated by slice 0.** "WITHOUT a
   `dialogue_id`" describes the pre-FA-N5 client. Following it ships the exact
   misroute FA-N5/FA-N37 fixed.

4. **FA-75's backend half is unnecessary.** `lapsed_offers` (`dispatch.py:2177`)
   and `pending_envoys`/`pending_envoy_count` (`:2193-2194`) already ride
   `GET /dispatch`, which the driver already fetches every turn.

5. **Determinism, the rule for this slice.** The module RNG is reseeded only at
   the top of each turn from `(seed, world_turn)` -- `seed_module_rng` is called
   at driver:1547 and :1578 and nowhere else. Therefore:
   - Adding **GET** calls (campaign_log, tutorial_state) and adding digest
     LINES changes nothing. **Group A is determinism-free.**
   - Adding or changing any **POST** shifts every subsequent draw in that turn.
     **Group B and D make the nine archived `audit-*` digests non-regenerable.**
     Nothing in `BASELINE_SERIES` or M1-M7 depends on the driver, so no
     re-record is owed there -- but the memo citing an archived digest must
     name which driver revision produced it, and `meta.json` is the place
     (FA-N89 + FA-39's `script`/`llm_source` are the mechanism).
   - Land group A FIRST, archive a fresh set of digests, THEN land group B, so
     the behaviour delta is attributable.

6. **Harness trap I hit myself.** My own probes do NOT reseed per turn, so two
   probe runs with identical 6-turn preambles diverged (probe 4 saw no
   standalone-decision row where probe 6 saw a `retired` one). Any hand probe
   that runs more than ~3 turns must call `seed_module_rng` per turn or its
   negatives prove nothing.

7. **Two undocumented public unserialized world fields** found by the FA-91
   census and named in no row: `nation_capitals` and
   `positive_threat_delta_this_turn`. Both are deliberate (re-derived /
   reset-on-load respectively), neither is in any exclusion list, and the
   FA-91 census will RED on them on its first run unless the allow-set names
   them with reasons.

8. **Counts wrong in two rows.** FA-78 says twelve disabled pressings; the
   archive has three (`grep -c "refused: Making peace with Austria"` = 2 in
   `audit-propose`, 1 in `audit-latewar-t20`). FA-83 says the accept path is
   exercised zero times across the archive; `1b-pacifist-austerlitz-r1:262-263`
   completes it.

9. **The archive is stale relative to slice 8.** `audit-naval/digest.md` still
   shows the `=`-banner artefact FA-87 fixed. Any re-read of the archived
   digests must not re-file fixed defects.

---

## Group assignment for a single slice

**(A) Pure `Digest` output -- no behaviour change, determinism-free, land first**
- FA-N79 + FA-N86 -- fog lines, ONE edit to `Digest.enemy_phase` + both call sites
- FA-77 -- strategic-order progress lines (with the dedupe/filter above)
- FA-84 half 1 -- `GET /campaign_log`, printing only what the HIGH-only rail misses
- FA-75 evidence half -- print `morning["lapsed_offers"]` and `["pending_envoys"]`
- FA-79 third -- write the `/respond_to_redemption` and
  `/marshal_petition_response` result messages into the digest
- FA-N89 (+ FA-39's driver half) -- one meta edit: `scenario`, `cheats`,
  `strict`, `script`, `llm_source`, `parse_mode`, `parse_confidence`

**(B) Changes what the driver ANSWERS -- log loudly; archived digests become non-regenerable**
- FA-72 -- token-match the needles, drop `"no"`, add explicit per-family policy keys
- FA-78 -- `_enabled` filter INCLUDING the literal fallbacks
- FA-79 policy -- default `redemption` to `grant_autonomy`; add the `--redemption`
  flag; `petition: rotate` opt-in only
- FA-N35 -- three popups get real arms, **with** `dialogue_id` (lands after FA-72)
- FA-75 answering half -- the `/mailbox/activate` loop

**(C) Backend seam -- both display-only, GR6**
- FA-39: stamp `parse_mode` and `parse_confidence` on the `/command` response
  from the `parsed` dict at `backend/main.py:2703` (`ParseResult.to_dict`
  already emits `mode` / `confidence` / `key_source`). **Display-only.**
- FA-89: a `tutorial_step` key (or `GET /tutorial_state`) derived from the same
  payload predicates `tutorial_overlay.gd::_derive_step_for_turn` / `observe`
  read, gated on `world.scenario_name == "tutorial"`. **Display-only.**
- FA-36 needs NO backend seam (closed by slice 2). FA-75 needs NO backend seam
  (the keys are on `/dispatch`).

**(D) New driver arms / scripts**
- FA-102 `--reload-every N` at the TURN BOUNDARY, with the corrected contract
- FA-90 -- only its three genuinely-unowned pieces, and only after A/B/C
- FA-85 -- script edit (`Soult, march to Brittany`) + the SCRIPT PRECONDITION guard

**(E) Test-suite defects**
- FA-N34 -- rewrite the two vacuous pins against the CURRENT whole-command gate
- FA-91 -- the played-world census, with the allow-set naming the seven
  `_display_*` transients, the 51 world caches, and the two public exceptions

---

## Probe inventory

`<scratchpad>/repro/j5/`

| file | what it settles |
|---|---|
| `probe_1_driver_pure.py` | POLICY_DEFAULTS, DISPLAY_ONLY_KEYS, FA-72(d) needle, FA-78 (incl. the un-filed generic arm), the 14-needle grep census |
| `probe_2_fan34_vacuity.py` | FA-N34: docstring-only needles, `find(` bound to the trim loop, and the shipped gate no longer eating the row's sentence |
| `probe_3_fa91_census.py` | FA-91: 0 round-trip divergences on a played world; the 10 marshal transients (7 `_`-prefixed); the 53 world attrs incl. the two public ones |
| `probe_4_fog_and_interrupt.py` | FA-N79/FA-N86: `fog_hidden_nations` on 6/6 end turns, flattener drops it |
| `probe_5_fa36_trace.py` | FA-36: order-free ask reaches `strategic_reports` AND `pending_interrupt` on a fresh boot |
| `probe_6_fa36_after6.py` | FA-36: the retirement arm, and the per-turn-reseed trap that explains probe 4's negative |
