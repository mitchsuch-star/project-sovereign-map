# NEXT SESSION PROMPT — Row WO, Slice 13 "The Trojan Corridor" (P1)

> Overwritten each time a session hands off. Paste the block below as the
> opening message of a fresh session. Current hand-off: August 21, 2026 —
> slices 1, 1b, 2 and 3 LANDED that day (landing records =
> `docs/WEIRD_OUTCOMES_SPEC.md` §3, per slice; the 1b addendum =
> `docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md` §9).

---

Build **slice 13 (WO-17 "The Corridor Has a Direction")** of the
Weird-Outcomes program — the hand-verified P1 exploit on the WIN-D3
evacuation system. Per spec §5 order (1 → 1b → 2 → 3 → **13** → 4 → …).

**Read first, in this order:**
1. `docs/WEIRD_OUTCOMES_SPEC.md` §3 slice 13 — the fix contract, verbatim,
   AUTHORITATIVE. §6 never-do 20 and 21 bind this slice directly.
2. `docs/WAR_WITHDRAWAL_SPEC.md` §7a — WIN-D3's own gate + landing record
   (the five §3.4 never-do pins that must survive byte-identically).
3. `docs/BUG_FIXES.md` §Weird-Outcomes row WO-17.

**The defect in one breath:** `has_evacuation_grant` is a bare
`(pair_key → expiry)` compare — no marshal, no direction, no stranded
check (`withdrawal.py:133-149`, consumed by the ONE `can_enter_territory`
arm at `diplomacy.py:9452-9455`) — and the grant opens on ANY WAR→non-WAR
edge INCLUDING ARMISTICE. Park a corps deep on enemy soil, sign a 1-DP
armistice, march FRESH corps INTO enemy sovereign territory all truce
long (walked-in corps register "stranded" and hold the corridor open),
let the truce collapse free — the new war opens beside Vienna.

**Fix contract (spec slice 13, verbatim):** zero new fields, one seam —
the permission arm gains a direction term: a marshal whose CURRENT
location lies in its own nation's home zone (O(1) controller/home check —
the arm is inside pathfinding loops, GR8) may NOT use the grant to enter
the counterpart's territory. A stranded corps outside its home zone keeps
full transit; the moment it reaches the body of its own realm, the grant
is spent for it.

**Done when:** during a truce, a corps standing on French home soil is
refused entry to enemy sovereign territory (the falsifiable negative —
the Trojan march); a genuinely stranded corps still routes home through
the same provinces; the corridor still retires when nobody is stranded;
the five WIN-D3 §3.4 never-do pins byte-identical;
`test_win_d3_road_home.py:243`'s pair-level assertion REWRITTEN to the
direction-aware form (a CONSCIOUS pin flip, record it);
`BASELINE_SERIES` byte-identity proven by a real subprocess run
(P1.2 only ever walks home, so ambient should not move — prove it).

**Consciously NOT built (spec):** a player-side re-declaration time floor
— that is WO-D8, a design question for a future diplomacy gate (§6
never-do 21); PT-J2's demobilize-on-peace is a recorded gate ruling.

**Landing discipline:** work directly on master; the pre-commit hook runs
ruff + the full suite (green at hand-off: 18,22x/3 — see the last
commit). Update: the spec (✅ landing record on §3 slice 13),
`STATUS.md` top entry, `BUG_FIXES.md` WO-17 → FIXED. Commit as
`fix(wo): slice 13 — the corridor has a direction …` and push. Overwrite
this file with the next hand-off (slice 4 WO-D6 "The Capital Speaks" +
WO-11, per §5 order).

**Standing context:** the G2(b) shelf decision was taken at slice 1b —
read the addendum (`PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md` §9) before
touching anything funnel-adjacent; the playtest driver is now
deterministic (Mode A/mock) and `--archive` is the citation rule
(`docs/PLAYTESTING.md`).
