# NEXT SESSION PROMPT — Row WO, Slice 4 "The Capital Speaks" (WO-D6 + WO-11)

> Overwritten each time a session hands off. Paste the block below as the
> opening message of a fresh session. Current hand-off: August 21, 2026 —
> slice 13 (WO-17 "The Corridor Has a Direction") LANDED that day, on top
> of slices 1/1b/2/3 (landing records = `docs/WEIRD_OUTCOMES_SPEC.md` §3,
> per slice; the 1b addendum =
> `docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md` §9).

---

Build **slice 4 (WO-D6 "The Capital Speaks" + WO-11)** of the
Weird-Outcomes program. Per spec §5 order (1 → 1b → 2 → 3 → 13 → **4** →
5 → …).

**Read first, in this order:**
1. `docs/WEIRD_OUTCOMES_SPEC.md` §3 slice 4 — the six-point contract,
   verbatim, AUTHORITATIVE (headline class + ordering pin + WO-11
   direction guard + Gazette caption + diverse tail + the WO-16
   exclusion). §2 D-10 and D-15 bind it.
2. `docs/BUG_FIXES.md` §Weird-Outcomes rows WO-D6-adjacent + **WO-11**
   (the direction-blind `home_captured`).
3. `backend/game_logic/dispatch.py` — the headline-class table
   (`dispatch.py:59-62` carries the NP-4 `sovereign_captured: 101`
   ordering that must stay on top) and the `:432-435` guard pair WO-11
   contrasts.

**The defect in one breath:** the fall of the player's OWN capital has no
headline class of its own — Paris's fall renders as a generic
`home_captured` row that three same-class rows can crowd off the page,
the Gazette captions it in the victor's words, and `home_captured`
(weight 100) is direction-blind: an ALLY liberating a French homeland
province from a third party fires the game's most ceremonial wound
(`dispatch.py:432-434`, while the sibling arm at `:435` already carries
the correct France-lost guard).

**Contract (spec slice 4, six points, verbatim there):** new
`capital_lost` class at weight **100** with `home_captured` demoted to
**99** and the full ordering pinned
(`sovereign_captured 101 > capital_lost 100 > home_captured 99 >
marshal_destroyed 96 > marshal_captured 95`); the predicate keys
structurally on `world.get_nation_capital(player_nation)` — never the
literal "Paris"; **WO-11 in the same edit** — both classes gain the
player-side-LOST direction guard; the Gazette captions the player's own
fallen capital in the loser's voice (one `if`, one string; the sovereign
special-case at `gazette.py:105-111` untouched); the **diverse-tail
rule** (~4 lines, no new templates) reserves the LAST sub-beat slot for
a class not yet on the page; `own_mauled`'s floor is NOT here (slice
12's WO-16).

**Done when:** Paris's fall leads with its own sentence on a
four-province + two-capture turn (the eval's deterministic probe,
md5-identical under `PYTHONHASHSEED=1` and `=2`); an ally's liberation
fires NEITHER class; a weight-95 capture reaches the page via the
diverse tail; **all three CA8-5 pins green and byte-identical** (§2 D-10
— a naive per-class collapse reds
`test_two_different_marshals_still_get_two_beats`; the diverse-tail rule
must not); zero movement on the `CAMPAIGN_LOG_TYPES` pins (§2 D-15 —
headline classes are display vocabulary, not event types).

**Harness impact:** dispatch is display-only — M1–M7 and
`BASELINE_SERIES` are unreachable by construction (weights are
documented "display only, tunable freely"). Zero `.gd`, zero new
serialized fields.

**Landing discipline:** work directly on master; the pre-commit hook
runs ruff + the full suite (green at hand-off: **18,257/3**). Update:
the spec (✅ landing record on §3 slice 4), `STATUS.md` top entry,
`BUG_FIXES.md` WO-11 → FIXED. Commit as
`fix(wo): slice 4 — the capital speaks …` and push. Overwrite this file
with the next hand-off (slice 5 WO-D5 "Berthier Names the Peace" +
slice 6, per §5 order).

**Standing context:** slice 13 added a WO-17 census pin
(`test_wo_slice13_corridor_direction.py::TestTheCensusPin`) — any new
`can_enter_territory` call must pass `mover_location=` (relocation) or
be consciously audited into the pin's allowlist; the G2(b) shelf
decision stands (1b addendum — read it before touching anything
funnel-adjacent); the playtest driver is deterministic (Mode A/mock) and
`--archive` is the citation rule (`docs/PLAYTESTING.md`); never set
`PYTHONIOENCODING` when running the tests (it fakes 6 subprocess-test
errors — the ambient shell may have it exported, `Remove-Item
Env:\PYTHONIOENCODING` first).
