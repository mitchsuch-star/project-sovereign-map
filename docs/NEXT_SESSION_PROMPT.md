# Next session prompt — the played campaign, with the Emperor

> Paste the block below as the session's opening prompt. Written August 15,
> 2026 at the close of row NP. The alternative routing is at the bottom.

---

Continue from master (latest: `bfea78d`). Row NP — Napoleon, "The Emperor
Takes the Field" — is BUILD-COMPLETE THROUGH NP-V and pushed: ten commits
`bb849b2`..`bfea78d`. Suite baseline: **17,978 passed / 3 skipped**, ruff
clean, Godot parse harness EXIT=0, boot smoke 0 SCRIPT ERROR.

THIS SESSION = THE PLAYED 20-TURN CAMPAIGN, the one the queue has owed
since row PT and which the NP gate's Q9 ruling deliberately deferred until
AFTER row NP so that it evaluates the game **with its Emperor**. Then, if
it fits cleanly, the routed fixes; position 10 is the session after.

**Read first, in this order:**
1. `docs/PLAYTESTING.md` — the doc of record. START THERE. Mode A
   (`tools/playtest_driver.py`) is the default; Mode C is the client
   visual walk and needs `SOVEREIGN_PORT=8006` so it never collides with
   a live 8005 session the user may own.
2. `docs/NAPOLEON_SPEC.md` §15 — the row NP landing record
   (authoritative), especially §15.4 (the aura-of-invincibility design
   amendment) and §15.7 (what is still open, with owners).
3. `docs/STATUS.md` top entry, then `docs/ROADMAP.md` for position 10.
4. `docs/audits/PLAYTEST_COMPREHENSIVE_2026_08_15.md` — the previous
   campaign's memo, for the method and the pillar scores to compare
   against (directional ≈6.7 at that pass).

**What this campaign has to answer.** The previous one measured a game
with no Emperor in it. Everything below is a claim row NP makes that only
a played campaign can confirm or refute:
- Does he **feel strong** in the wild, and do **his losses have weight**?
  The review scored the pre-amendment build 6/10 and 4/10 and the
  amendment was built to fix the second. The aura now decays with
  imperial grip — the battle report should visibly read "+9% (his star
  dims)" after roughly the fourth emperor-led defeat. Confirm or refute
  from play, not from the constant.
- Does **the Shadow** actually reshape the court, or does the player just
  never stack with him? §6.2 calls it "the court's engine"; two of this
  row's three P1s were the Shadow failing to fire at all.
- Does **the Petition for Independent Command** ever fire in a real
  campaign (4 co-located turns + below the ladder median + skill ≥7), or
  is it dead content?
- Does **capture** ever happen? §7 wagers the Empire on true encirclement
  only. Rare is the design; never is dead content.
- Is **the Seat** (+1 DP at the Tuileries) ever worth staying home for?
- Re-score all the pillars and give a directional number against ≈6.7.

**Method notes that cost previous sessions time:**
- The driver's `turns` keys are its own 1-based LOOP INDEX, not world
  turns (PC15-H).
- `MAX_ANSWERS_PER_POST` was raised 8 → 16 during row NP: the Emperor's
  stack wins hard enough to chain more decisions in one turn than the old
  cap would answer, and at 8 a run reports `blocked` on a harness limit
  that looks like an engine defect. If you see a chain cap warning again,
  read it as the harness before you read it as the game.
- A 500-cap evicts old rows from `event_log`, so a probe that scans it
  can silently miss the run's largest burst (the IGR-B trap).
- Commit before spawning any review fleet, and forbid git mutation in the
  agent prompt (a subagent once ran `git stash` and destroyed uncommitted
  work).

**Route, don't fix inline:** correctness rows → `docs/BUG_FIXES.md`;
design questions → `docs/DESIGN_REFINEMENT.md`; the memo →
`docs/audits/PLAYTEST_<name>_2026_08_XX.md`, authoritative, with per-row
digest names. Fix in-session only what is cheap, certain, and blocking.

**Standing contract terms (verify against the specs, which win):** GR5
symmetry — every sovereign guard keys on `is_sovereign`, never the name
"Napoleon" · GR6 — the LLM only parses · zero new serialized fields for
anything NP-shaped · `WorldState.destroy_marshal` is the ONE removal seam
and the census pin forbids bare pops · the B0 petition contract stamps
trigger latches only on a QUEUED push · `BASELINE_SERIES` and M1–M7 are
byte-identical right now; if either moves, attribute it with a multi-arm
flip experiment BEFORE re-recording, and re-record at most once.

**Cadence:** commit directly to master, one commit per coherent unit,
pre-commit hook green, never `--no-verify`. Any `.gd`-touching change runs
the committed parse harness (commit the refreshed report) plus one
headless boot, grep `SCRIPT ERROR`. Update STATUS.md and CLAUDE.md live
state. Push when done.

**Do NOT touch:** NP-6 "The Three Emperors" (post-NP-V and strikeable at
the user's word — do not start it unless asked) · the petition spec slices
B1–B5 (`PETITION_POPUP_REVISIT_SPEC.md`; B1 "The Antechamber" is its own
session) · the PC15-D gate rulings (`DESIGN_REFINEMENT.md` is
authoritative) · the design-gated Seasons build (`SEASONS_WEATHER_SPEC.md`
— user ruled it out past Round 0) · anything a deferral row names with a
different owner.

**Two things need the user, not you:**
1. **The visual sign-off** on the row NP surfaces is the user's own pass
   by the standing convention — the emperor map piece, the Generals apex
   card, the diorama locket cipher ("N"), the Captive Eagle row on the
   war-detail popup, and the Tuileries line in the diplomatic ledger.
   Stage them with a Mode C walk and hand over screenshots; do not mark
   it signed off yourself.
2. **One open design question from row NP**, recorded and unanswered:
   objections are gone for the sovereign by design, and the CA9 row-2
   attack-confirm gate arms only for a `cautious` marshal — so the
   Emperor gets no confirm even on a genuinely bad attack. Whether he
   should get an "are you sure" (a gate, not an opinion) is the user's
   call. Put it to them; do not build it unprompted.

---

## Alternative routing, if the user would rather ship first

Swap the campaign for **position 10, the shippable build**. Its remainder
is named in `docs/STATUS.md`: the fresh Godot export itself (verify
`europe_1805.json` is inside the new `.pck`), the LLM-access touchpoints
from `docs/audits/LLM_MONETIZATION_RESEARCH_2026_08_14.md` (settings
rename / three-fears copy / status / hint / failure notice), optionally
client-side process supervision beyond the launcher's, and the
stranger-unzips-it run on a Python-less machine. The P0/P1 pre-build gaps
closed on August 15; row NP added one more that is now fixed and pinned —
`assets/` is gitignored, so any new art must be force-added or a fresh
clone ships without it.

The argument for the campaign first: it is cheap on the standing harness,
it evaluates the Emperor in the wild, and this row proved twice that play
finds what a 30-agent review does not.
