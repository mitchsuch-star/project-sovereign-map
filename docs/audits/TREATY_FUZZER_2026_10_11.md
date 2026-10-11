# The Treaty State-Machine Fuzzer — DD-1 S6, the second instrument (October 11, 2026)

*Pre-Deploy S6, `docs/PRE_DEPLOY_PLAN.md` §3.1 "The instrument" 2. Tool
`tools/treaty_fuzzer.py`; records `docs/audits/dd1/treaty_fuzzer_<seed>.json`
(ten seeds `dd1-fuzz-1 … 10` × 1,000 steps, and the 120-step `dd1-smoke` the
tool was built on); ledger `tests/data/treaty_fuzzer_known_violations.json`;
pin `tests/test_dd1_treaty_fuzzer.py`; rules `SYSTEMS_REFERENCE.md` §106.2;
rows `BUG_FIXES.md` §DD-1 S6 (DD1-5 … DD1-8, DD1-10 … DD1-12). Nothing fixed —
the slice measures.*

## What was measured

Per seed the 1805 world is booted in-process (`WorldState.from_scenario`, the
seed as the campaign seed) and 1,000 steps are drawn by weight — end turn
(30 %), answer the letter before you (14 %), propose a treaty and send it
(14 %), declare war with every chooser pre-resolved (8 %), white peace +
confirm (8 %), common peace + submit + confirm (6 %), break a treaty (5 %),
make a vassal (4 %), release a vassal (3 %), summon the Congress (3 %) — each
executed through the REAL executor as a structured command (no parser, no
HTTP); a captured province's plunder / secure gate is answered at random so
the table's verbs stay reachable; DP and gold are topped up each step (never
a diplomatic state). After EVERY step the invariants of `SYSTEMS_REFERENCE.md`
§70 / §81 are read (I1 … I6 in the tool's docstring), the world is
round-tripped through `from_dict(to_dict())`, and every write to
`diplomatic_states` is attributed to its frame by a recording dict. A
violation is recorded ONCE per (class, detail) with the step it first
appeared, how many steps it persisted and the twelve verbs that reached it.

## The reading

```
seed           steps  turn   secs  viol  classes
dd1-fuzz-1      1000    54   59.7    13  I6 10 · I1 purpose 2 · I1 ownership 1
dd1-fuzz-2      1000    84   56.3    13  I6 7 · I1 ownership 4 · I2 2
dd1-fuzz-3      1000   311   92.0     7  I6 5 · I1 ownership 2
dd1-fuzz-4      1000    43   54.2    13  I6 7 · I1 purpose 2 · I1 ownership 1 · I5 ×3
dd1-fuzz-5      1000    37   54.4     2  I6 1 · I1 ownership 1
dd1-fuzz-6      1000    48   50.2     5  I6 4 · I1 ownership 1
dd1-fuzz-7      1000    44   49.7     8  I6 7 · I1 ownership 1
dd1-fuzz-8      1000    38   53.7     3  I6 3
dd1-fuzz-9      1000    57   55.2     6  I6 6
dd1-fuzz-10     1000    46   56.1    11  I6 5 · I1 ownership 3 · I2 2 · I1 purpose 1
TOTAL                                81   (distinct; 10,000 steps, 9,000 verbs drawn)
```

**Held on every seed:** I3 — every write to `diplomatic_states` went through
`set_diplomatic_state` (0 outside writers over 10,000 steps; §70.2's known
direct writers never fired on these roads); I4 — nothing below zero; no verb
raised. **The transitions the setter made that `validate_transition` rejects**
(recorded, not violations): `ALLIANCE→PEACE (nation_eliminated)` ×8 — the
elimination road, by design; `NON_AGGRESSION→PEACE (treaty_break)` ×1 — the
break's own `post_break_map`; and on the smoke seed
**`VASSAL→OPEN_BORDERS (treaty_ratification)`** — the ratifier signed a treaty
the state machine forbids (VASSAL leaves only to WAR / PEACE / NON_AGGRESSION;
`_ratify_treaty`'s no-downgrade guard reads the upgrade ladder, on which VASSAL
does not sit) → DD1-12.

**The classes:**

1. **I1 ownership — 14 distinct, the most persistent (up to 330 steps).**
   `war_instance 'war_N' claims pair 'France|X' as pair_status='war' but
   diplomatic_states does not have it as WAR`. Two roads: the player's
   **bilateral armistice** accepted at end turn (`propose armistice → Holland /
   Sweden (execute_proposal)` then `end_turn`) and **`make_vassal` by conquest**
   (`make_vassal Hanover / Portugal`). The ratifier runs `cleanup_war_end`
   for a WAR→ARMISTICE with `conclude_objectives=False`, and the conquest
   road runs its own cleanup; neither restamps the instance's
   `diplo_key_meta[pair].pair_status` (the settlement road's
   `_resolve_pair_state_transitions` does) — §81's "`war_instances` /
   `participant_meta` / `diplo_key_meta` agree" broken on the two bilateral
   exits. → **DD1-5.**
2. **I1 purpose — 5 distinct.** A pair at WAR with no `war_objectives` entry
   (`Austria|France`, `France|Russia`, `Britain|France`), always after an end
   turn — an AI-side declaration or a cascade's entry that writes WAR without
   a purpose. The round trip shows the same pairs as `/war_objectives/… missing
   on one side`: `from_dict`'s migration backfills a purpose at load, so a save
   and a reload paper over it. → **DD1-6.**
3. **I6 round trip — 55 distinct, four shapes.** `/incoming_proposal_popup`
   (22) and `/incoming_settlement_offer_popup` (10): the pending popups are
   written by `to_dict` and never restored by `from_dict` (the `_popup_queue`
   is rebuilt empty); `/dialogue_manager/current/blocking` True→False (9): the
   load migration flips every current-turn offer's `blocking` to False,
   which a counter-offer (`blocking: True` by its producer) does not survive;
   `/notifications` length N vs N−1 (12): one notification is dropped by the
   collector's round trip; `/war_objectives` (2): the purpose backfill above.
   → **DD1-7.**
4. **I2 — 4 distinct.** `Switzerland (client of Britain / Austria) at WAR with
   Ottoman / Saxony / Naples; the lord is PEACE` — a court vassalized by an AI
   lord keeps the wars it had, where the lord has peace; §70.2's rule ("a
   client's war is the lord's war") is read at the lord's treaty roads, not at
   the vassalization. SFR-D28's class from the other side. → **DD1-8.**
5. **I5 ×3 — 1 distinct each, one event.** `declare_war Portugal
   (forced_alliance)` on a pair the same instance had RESOLVED: the pair is
   re-attached as `war` but stays in `resolved_diplo_keys`, and Portugal is
   back among `active_participants` with its `exited_turn` still stamped
   (`attach_pair_to_war_instance` restamps the pair meta and `setdefault`s
   the participant row). → **DD1-10.**
6. **The refusal tally.** Of the verbs' 1,996 refusals over the seeds, 1,996 −
   36 named their reason in words; **36 read `Cannot declare war:
   war_instance_side_conflict (both nations live in war_instance 'war_N' …)`**
   — a raw engine code in a player-facing refusal. → **DD1-11.** The rest, by
   shape: Talleyrand in transit (1,996 → the largest, a lawful gate), the
   one-on-one war's bilateral road, the Congress's titled-province floor,
   the vassal power cap, insufficient DP, the proposal cooldowns.
7. **Verbs that never reached their end.** `common_peace` on an empty draft
   never offered Ratify (PROPOSE mode wants terms — by design, the fuzzer
   backs out); `summon` never succeeded on any seed (the floor); the rest
   each succeeded on every seed.

## The done-when

§3.1: *the fuzzer holds its invariants for 10 seeds × 1,000 steps.* **NOT met:
81 distinct violations in 7 classes.** The ledger is the ratchet (no class
outside it lands; it only shrinks); the pin re-runs two seeds × 150 steps live
and asserts the done-when NOT met so it is re-seated on purpose.

## How to re-read

```
.venv/Scripts/python.exe tools/treaty_fuzzer.py                      # 10 x 1,000 (about ten minutes)
.venv/Scripts/python.exe tools/treaty_fuzzer.py --seed dd1-fuzz-2 --steps 200 --verbose
.venv/Scripts/python.exe tools/treaty_fuzzer.py --summarize
.venv/Scripts/python.exe tools/treaty_fuzzer.py --write-ledger       # after a fix (the count must fall)
```
