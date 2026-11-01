# NEXT SESSION PROMPT — Row RE "Affairs of State": RE-H the Haiti letter — H0 LANDED, the squadron next (then the user's review)

> Overwritten each time a session hands off. Current hand-over: **November 1, 2026 — RE-H H0 the bill alone LANDED**
> (`SYSTEMS_REFERENCE.md` §164.1; the record `RECURRING_EVENTS_SPEC.md` §22.1; one commit through the hook; the row
> before S15 by the user's ruling of October 31 — §0c). **The deck carries four letters:** the Arch-Chancellor's Letters,
> the Host's Claims, Berthier's Memorial and now the Haiti letter — Decrès writing when Britain has had France blockaded
> four of the last twelve mornings, the Emperor holds court at home, 25 sail lie in port and the chest holds 1,500.
> **The user's word at the plan's review** ("we want to make sure these events are good, have conditions that make them
> appear and don't make the game repetitive … fun factor high") amended P16 for this letter: `bites: "floor"` — the
> letter arrives at full standing, where the Decline is a dent (100 → 97). Measured on 52 runs: it arrives on 16 (15 of
> the 21 passive runs — the campaign's FIRST affair at T6–T9 — and the treaty road twice), never while the Emperor
> marches, never at peace with Britain; the roads unmoved against the in-tree control; `BASELINE_SERIES` re-pinned with
> its attribution (the unattended France's lapse at T9 brings Holland's rebellion one turn forward).
>
> **The next step — the squadron (§6.5 "the mechanism", §22.2), the second landing of RE-H, its own commit:** the op
> `squadron{ships, away, to}` (`set(MO.OPS)` 9 → 10, flipped consciously in `test_moments_engine.py` and
> `test_affairs_engine.py`); the two forms `squadron` / `bill` with `requires: hunter_at_sea`, frozen in `bind` at
> delivery; `naval.squadron_quote` on `expedition_slip_odds`'s new `escort` override (the sailing force alone — 36 in
> 100 at war against Britain's 100 sail, 62 with a window, 100 with no hunter → the bill); `detach_squadron`,
> `_squadron_tick` over `iter_fleet_records` after `_readiness_tick` (the squadron drills at sea — `READINESS_TICK` a
> turn toward 100 — and folds back at its readiness; caught, lost whole; the draw `naval::squadron::{issued}::{lord}::
> {tag}`; `squadron_last` written), `last_squadron`; `affairs.settle_squadrons` as the affairs tick's first step (the
> row's `outcome` / `outcome_turn` / `outcome_line`, the `moment` log row with phase `outcome`); `_deliver` freezes
> `last_fate` and `last_sailed`; the board's passage and last-squadron lines; the fate's morning line
> (`situation["affair_fate"]`, amber in `dispatch_view.gd` and `main.gd` — pulled forward from RE-R); the Admiralty's
> `squadron_line` and its renderer (`strategic_ledger.gd` beside the rot line; the parse harness re-run); the validator
> (the op's bounds, Accept-only, one per entry, a `bill` form, the owner's `navies` row, `min_ships ≥ ships + 20`,
> `requires` named, the `outcome` copy); the trace's squadron arm and fate row; the seams AFH (`naval._squadron_tick`)
> and AFS (`affairs.settle_squadrons`, `moments._apply_squadron`) in `tests/_affairs_seams.py` and the series rig; the
> pins (the half-even rounding 36.5 → 36 / 61.5 → 62; the form frozen; shown = applied; a squadron outliving an
> annihilated fleet; the save round-trip; the alarm untouched across sail, tick and settle; the squadron's movers on
> Britain's reads); the frames of both forms; the measure re-run (the hash moves); `SAVE_FORMAT_REFERENCE.md` (the
> fleets row's `squadron` / `squadron_last`; the row's new keys); `NAVAL_SPEC.md` §3.1 / §4.3; `MODDING_FORMAT.md`;
> §22.2 and §164.2; then STATUS and this prompt for RE-C, and STOP for the user's review of the whole slice.
>
> **Traps the row has paid for (do not re-discover):** the spec and `SYSTEMS_REFERENCE.md` are CRLF files — append
> through Python in the file's own endings, never `cat >>`; the shell heredoc eats a long block (write it with the
> Write tool); a crafted board built at turn 1 on the ARMED boot reads the boot's morning memo — pop
> `world.__dict__["_affairs_memo"]`; the Haiti letter premises on the boot board (the Emperor home, blockaded, 45 sail)
> once the chest passes 1,500 — a pin that wants another letter's morning keeps the fleet under 25 sail or the Emperor
> afield; the reply to `/respond_to_objection` carries NO `pending_objection` key (the driver reads `objection_kept` +
> `choices`); the record tool's standing figure reads "Authority N → M" (REH-1); `--affair lapse` leaves the letter IN
> THE MAILBOX; the judge files a purse named in passing as `context_drift`; the sweep tool must NOT be launched with
> `-X utf8`; the bytecode pins need `PYTHONDONTWRITEBYTECODE` unset; the road control is the in-tree seam
> (`--seam backend.game_logic.affairs:armed=False`), no clone; RAM is the limit at 16 GB (the suite's eight workers
> beside no driver); the deck hash reds `test_moments_pacing.py` AND `test_affairs_reach.py` until the measure is run
> again (`tools/_affairs_measure.py run` + `record`, `tools/ai_v_sweep.py --all`, `tools/_vp1_road_arms.py` armed and
> control, Road I answered, `tools/_affairs_first_arrival_probe.py`, `tools/_affairs_series_arms.py`); the frames:
> `tools/iq10_capture_payloads.py --only moments`, then `tools/iq10_run_captures.py --only affair_letter_santo_domingo
> --date …` at both scales and once `--physical --physical-scale auto`, then `tools/uxr0_readability_report.py
> <index> --record docs/audits/uxr0/readability_affairs_<date>.json`; `build_letter` / `refresh_letter` pass a STATUS
> ROW as `occ` (RE2-1); the Decree is priced in AUTHORITY; HC-0 (no calendar read in mechanics); no seed read in
> `moments.py`; every number to Godot an `int`; every answer a button; the hook runs the full suite in parallel
> (~10 min) — commit from Bash in the background with `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` and edit no
> tracked file while it runs; CLAUDE.md sits at its byte cap (every added line is paid for by a trim).
>
> **Open with the user, unchanged:** RE3-6 (the Crown fires nowhere), RE3-7 (the roads since S14j / S14k), RE3-9 (190
> untracked `.import` files); the certificate (`INK_IRON_SIGNTOOL_ARGS`); S14d's A1 as applied; AO's three questions
> (`REFORMS_SPEC.md` §5a); SF-NAV-1-D1.
