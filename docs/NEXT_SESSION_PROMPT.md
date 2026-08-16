# Next session prompt — the played campaign, and the NP-6 evaluation

> Paste the block below as the session's opening prompt. Written August 15,
> 2026 at the close of the row NP promise audit. Supersedes the version
> written at `bfea78d` (that one predates the audit and its baselines are
> stale). Alternative routing at the bottom.

---

Continue from master (latest: `88e5a8c`, clean tree, pushed). Suite
baseline: **18,057 passed / 3 skipped** · ruff clean · parser eval 524/524
mock · Godot parse harness EXIT=0 · backend boots clean.

THIS SESSION = TWO THINGS, in this order:
  **(1) THE PLAYED 20-TURN CAMPAIGN** — owed since row PT, and deliberately
      deferred by the NP gate's Q9 ruling until AFTER row NP so it
      evaluates the game **with its Emperor**. This is the primary work.
  **(2) THE NP-6 EVALUATION** — a memo with a recommendation, **NOT a
      build**. Do not author Alexander unless the user says so in this
      session.

Row NP is BUILD-COMPLETE and its exit review (the promise audit) is CLOSED:
450 promises checked, 297 landed, 18 fixed, 11 routed to other owners.
Nothing in row NP is open except the two items below that belong to the
user, and NP-6.

**Read first, in this order:**
1. `docs/PLAYTESTING.md` — the doc of record. START THERE. Mode A
   (`tools/playtest_driver.py`) is the default; Mode C is the client
   visual walk and needs `SOVEREIGN_PORT=8006` so it never collides with a
   live 8005 session the user may own.
2. `docs/audits/NP_PROMISE_AUDIT_2026_08_15.md` — what the exit review
   found and fixed. §2 and §2b are the eighteen defects; §3 is what was
   verified LANDED. **The campaign is the acceptance evidence for all of
   it, because every one of those fixes has unit pins and runtime probes
   and none has been played.**
3. `docs/NAPOLEON_SPEC.md` §15 (landing record), §15.4 (the
   aura-of-invincibility amendment — the user's own brief), §15.9 (the
   audit), §15.9a (the two rulings the user gave at its close).
4. `docs/audits/PLAYTEST_COMPREHENSIVE_2026_08_15.md` — the previous
   campaign's memo, for method and the pillar scores to compare against
   (directional ≈6.7 at that pass; narration was the weak pillar at 6.0).
5. `docs/STATUS.md` top entry, then `docs/ROADMAP.md` for position 10.

=== PART 1: THE CAMPAIGN ===

Play France/1805 for ~20 turns. Mode A seeded for the spine; a live
`LLM_MODE=anthropic` arm for the parser and the voice; Mode C for the
visual walk. Write ONE memo to `docs/audits/` and score the pillars against
the ≈6.7 baseline.

**What only play can answer (the NP questions the row could not close):**
- Does the Emperor **feel strong**? The NP-V review scored this 6/10 before
  the §15.4 amendment. N1/N2 are correctly SIZED and must NOT be raised —
  ~16 of the +27.6 points of win rate he brings a stack come from the
  Presence. The question is whether it READS as strong.
- Do **his losses have weight**? Scored 4/10 pre-amendment. The aura now
  decays with imperial grip and the battle report says so ("+10%" → "+9%
  — his star dims" → nothing, and an emperor-led defeat says it out loud).
  **Does the player notice?** That is the whole point of the amendment.
- Does the **Shadow** reshape the court — do you actually find yourself
  detaching marshals so they can shine? Or is stacking with him still
  what you do?
- Does the **Petition for Independent Command** fire in ORDINARY play? It
  fires on turn 5 in a forced probe (4 co-located turns + glory below the
  ladder median + tactical-or-shock ≥7). Unknown in the wild.
- Does **capture** ever happen? True encirclement — enemy armies in EVERY
  adjacent province — is reachable and fires the sovereign last stand, but
  it is deliberately rare. Is it TOO rare, i.e. is §7 dead content?
- Is the **Seat** worth staying home for? +1 DP is the whole v1 mechanic.
- Ambient council wars stayed 0/40 turns on every seed with the blocking
  predicate WRITTEN (AI-3r §8.2). A played moment is what could change it —
  the D1 band is still unmeasured and belongs to this campaign if it shows.

**What to CHECK, because it was fixed this session and never played:**
- the aura visibly dims in battle reports as authority falls;
- a **charge out of the Emperor's own province** grants no aura row and
  full glory (it used to grant both — the dominant stacking);
- the **muster note appears only when he will actually march**, and hedges
  with "if he marches" when he is not yet on the field;
- **HOLD holds** — "Napoleon, hold Paris" must not sally;
- a captured sovereign is announced as **taken, not destroyed**, on every
  route (battle / auto-bombardment / charge / attrition);
- the **Petition's dispatch beat** appears ("… he asks for a command of
  his own");
- the DP HUD reads **6/6**, not 6/5, while he holds court.

**Stage the visual pass but NEVER sign it.** Five surfaces owe the USER's
own eyes: the emperor map piece, the Generals apex card, the diorama
locket "N" cipher, the Captive Eagle war-detail row, the Tuileries ledger
line. Capture screenshots into `docs/audits/`, hand him the list, and stop.

=== PART 2: THE NP-6 EVALUATION (a memo, not a build) ===

NP-6 "The Three Emperors" (spec §10 + §13) would author Tsar Alexander
(+ optionally Kaiser Francis) as `sovereign` marshals. The user asked for a
recommendation and got: **defer until after this campaign, then gate it.**
This session produces the gate memo. Three findings from the promise audit
change its scope and belong at the top of it:

1. **`GRIP_ENEMY_COURT_BASE = 75` is a FLAT baseline** (`authority.py:346`;
   `get_imperial_grip` has no authority term for non-player courts). So an
   authored foreign sovereign starts at ~82% of full dread and **his aura
   can never decay** — beat the Tsar six times and Europe fears him
   exactly as much. The user's central brief ("his losses have weight") is
   structurally FALSE for foreign sovereigns. **This is NP-6's real gate
   question**, and answering it touches VS-R and the fear curve for every
   nation, so NP-6 is bigger than "author two JSON entries".
2. **`_WIRED_ABILITY_MARSHALS` is name-keyed** (`marshal_overview.py:31`),
   so an authored Alexander renders NO ability block until he is added.
3. **The capture-worth half — the user's actual Q8 want ("they are just
   worth more to capture") — is ALREADY LIVE AND FREE.** The Captive Eagle
   war-score component, the 5,000g sovereign ransom and the Gazette
   special all key on `is_sovereign` in both directions. So NP-6's
   marginal value is the man on the map, not the capture-worth. Say that
   plainly in the memo; it is smaller than the row's framing suggests.

**Measure, do not assume.** Author a sovereign onto an ENEMY nation in a
SCRATCHPAD copy of the scenario dict (never write into the repo) and report
which of the five kit halves actually work end to end: the aura on the
Austrian/Russian side · the fear (a FRENCH AI corps must respect him) · the
Shadow over Kutuzov · the capture worth · the Seat for that nation's DP.
The promise audit verified the enemy-stamp arm at ~0.818; verify the rest.

The memo ends with a sized recommendation (sessions, the
`BASELINE_SERIES` re-record, the Russia/Austria pin re-blesses, the
portrait assets) and a proposed ruling on finding 1. **The user decides.**

=== METHOD TRAPS THAT COST PREVIOUS SESSIONS TIME ===
- The driver's script `turns` keys are the **1-based LOOP INDEX**, not
  world turns (PC15-H). The digest's enemy-phase attack counter under-reads.
- `MAX_ANSWERS_PER_POST` is **16** — raised because the Emperor's stack
  wins hard enough to chain more decisions in one turn than 8 would answer.
- The `event_log` is **capped at 500 rows** and evicts the earliest. Probing
  it for early-campaign evidence yields FALSE NEGATIVES — this trap has
  been hit twice (IGR-B, IGR-X4). Use the digest or a live probe instead.
- **Commit before spawning any review fleet**, and forbid git mutation in
  the agent prompt. A subagent once ran `git stash` and destroyed 2,167
  uncommitted lines.
- Stale backends survive failed restarts — check StartTime before trusting
  a live probe; a stale server answering first has wasted a session before.
- **Never set `PYTHONIOENCODING`** — it fakes 6 subprocess-test ERRORs and
  blocks the pre-commit hook.
- `.env` sets `LLM_MODE=anthropic` and conftest does NOT pin it, so any
  sub-0.7 phrasing escalates to the real API mid-suite (routed as NP-X4,
  owned by position 10). Pin the mode explicitly for a mock run.
- Windows: `".venv\Scripts\python.exe" -m pytest tests/ -q` from the repo
  root, Windows-style path with the venv python.

=== STANDING CONTRACT TERMS (the specs win on any conflict) ===
GR5 — every sovereign guard keys on `is_sovereign`, never the name
"Napoleon" · GR6 — the LLM only parses · GR1 — combat modifiers
single-sourced in `marshal.py` · ZERO new serialized fields ·
content-dormant: a sovereign-free scenario is byte-identical ·
`WorldState.destroy_marshal` is the ONE removal seam and its RETURN VALUE
is load-bearing (a captured sovereign returns False) · the petition channel
gate is `_push_petition` and it now refuses a sovereign petitioner · every
verb in `_SOVEREIGN_ORDER_VERBS` must actually parse (standing guard) ·
`BASELINE_SERIES` and M1–M7 are byte-identical RIGHT NOW: if either moves,
attribute with a multi-arm flip experiment BEFORE re-recording, and
re-record at most once.

CADENCE: commit directly to master, one commit per coherent unit, hook
green, never `--no-verify`. Any `.gd`-touching change runs the committed
parse harness (commit the refreshed report) plus one headless boot, grep
`SCRIPT ERROR`. Update `docs/STATUS.md` / `CLAUDE.md` live state. Push when
done.

DO NOT TOUCH: petition spec slices B1–B5 (`PETITION_POPUP_REVISIT_SPEC.md`;
B1 "The Antechamber" is its own session) · the PC15-D gate rulings
(`DESIGN_REFINEMENT.md` authoritative) · the design-gated Seasons build ·
the eleven routed NP-X rows (`BUG_FIXES.md` §Row NP — each has an owner
that is NOT this session: CR-6 ×4, DEF-1 ×3, position 10, EC-2/Victory,
and two accepted-and-pinned) · anything a deferral row names with a
different owner.

THE USER'S, NOT THE SESSION'S: the visual sign-off (stage it, never mark it
signed) · whether NP-6 gets built.

AFTER THIS: **position 10, the shippable build** — the fresh export, the
verify JSONs in the `.pck`, the memo's v1 LLM touchpoints, and the
clean-machine run.

---

## Alternative routing, if the user would rather ship than play

**Position 10 — the shippable build.** Its P0/P1 gaps closed August 15
(launcher mock-default + 30s health poll + stale-server reuse guard, cheats
re-gated on explicit debug, saves → `%APPDATA%\InkAndIron`, README_TESTER
rewritten, the 265MB movies.avi out of `res://`). The remainder is the
fresh export with the verify JSONs inside the `.pck`, the v1 LLM
touchpoints from `docs/audits/LLM_MONETIZATION_RESEARCH_2026_08_14.md`, and
a clean-machine run. Note that NP-X4 (the suite reaching the live Anthropic
API) is routed to that row and is worth closing while you are in it.

Taking this route leaves the campaign owed — it has been owed since row PT,
and every NP fix from the promise audit stays unplayed.
