# NEXT SESSION PROMPT — Row WO: slice 4 "The Capital Speaks" (+WO-11)

> Overwritten each time a session hands off. Paste the block below as the
> opening message of a fresh session. Current hand-off: August 22, 2026 —
> **slice 18 "The Answer Finds Its Question" landed** (WO-39 → WO-38 →
> WO-35's `pending_interrupt` half → WO-36+WO-40; landing record =
> `WEIRD_OUTCOMES_SPEC.md` §3 slice 18), and the phase-1 docket cleared:
> the **three visual sign-offs are SIGNED**, **WO-D9 is RULED** at the
> recommended default (wire the existing `get_trust_gain_modifier` damper;
> landing = slice 9), and the WO-D7/D8/D10/D11 carries were sanity-read.

---

**Build slice 4 — WO-D6 "The Capital Speaks" + WO-11.** Contract =
`docs/WEIRD_OUTCOMES_SPEC.md` §3 slice 4 (authoritative, six numbered items):

1. New headline class `capital_lost` at weight **100**, `home_captured`
   demoted to 99; the NP-4 top-of-table ordering pin stays intact
   (`sovereign_captured 101 > capital_lost 100 > home_captured 99 >
   marshal_destroyed 96 > marshal_captured 95`).
2. The predicate keys structurally on
   `world.get_nation_capital(player_nation)` — never the literal "Paris".
3. **WO-11 in the same edit:** both classes gain the direction guard the
   sibling arm at `dispatch.py:435` already has — an ally LIBERATING the
   player's capital must not fire the game's most ceremonial wound.
4. The Gazette captions the player's own fallen capital in the loser's
   voice (`gazette.py:94-104`, one `if`, one string; the sovereign
   special-case stays).
5. The diverse-tail rule: the LAST sub-beat slot is reserved for a class
   not yet on the page (~4 lines, no new templates).
6. `own_mauled`'s floor is NOT here — it is slice 12's (WO-16).

**Done when** (the contract's own line): Paris's fall leads on a
four-province + two-capture turn, md5-identical under `PYTHONHASHSEED=1`
and `=2`; an ally's liberation fires neither class; a weight-95 capture
reaches the page via the diverse tail; all three CA8-5 pins green and
byte-identical; zero movement on `CAMPAIGN_LOG_TYPES` pins (headline
classes are display vocabulary, not event types).

**Harness:** dispatch is display — M1–M7 / `BASELINE_SERIES` should be
unreachable, but MEASURE (run `tests/test_ai_intent_threat_migration.py`
+ `tests/test_combat_sweep_metrics.py`); slice 15 moved the series on a
"player-gated therefore inert" prediction. Zero `.gd`, zero fields — no
XR-1 boot needed if that holds.

**Landing discipline:** work directly on master; the pre-commit hook runs
ruff + the full suite. Point any review fleet at a COMMITTED SHA with a
clean tree; mutation-sweep every pin (`tools/mutation_sweep.py`, shape =
`tools/_sweep_wo18.json`); verify the MECHANISM, not just the outcome —
five of the row's filed fixes so far were a no-op, unbuildable, harmful,
or a soft-lock as written.

**The queue after this slice** (§5 order): 5 → 6 → 8 → **9** (the
disobedience-family slice: the WO-D9 damper wiring per the Aug-22 ruling
in `DESIGN_REFINEMENT.md` §WO-D7..D11, **plus WO-41**, the
autosave-timing redemption loss filed by slice 18) → 10 → 17 → 11 → 12
(carries WO-33, WO-D10's refusal copy, WO-16, and WO-35's
pending_objection legibility remainder) → 14.

**Standing context:** slice 7 retired typed diplomacy (no typed diplomatic
sentence executes through the client); slice 13's census pins bind
`can_enter_territory`/`passable_for` call shapes; slice 15's blocking-state
surface census now has FOUR classes (QUEUE_DELIVERED / LOAD_REATTACHED /
RECOVERED_BY_POLL / KNOWN_SILENT_AT_LOAD) — a new modal route key must be
classified or the pin reds; slice 17's WO-24 scope is the CHARGE family
only. The playtest driver is deterministic (Mode A/mock), `--archive` is
the citation rule (`docs/PLAYTESTING.md`). **Never set `PYTHONIOENCODING`
when running tests** — the ambient shell exports it; clear it in every
command that runs tests or commits.

**The row is DONE when** all seventeen §3 slices plus slice 18 have landed
with their done-when lines green, `BUG_FIXES.md` §WO rows WO-1..WO-31 plus
WO-33..WO-41 are all FIXED/CLOSED with pointers to landing records, WO-32
is confirmed closed by its owner PC15-10, and the WO-D7..D11 contracts are
discharged (D9's ruling lands at slice 9). The three visual sign-offs are
SIGNED (August 22, 2026) — that DoD item is discharged.
