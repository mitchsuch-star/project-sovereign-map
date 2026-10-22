# NEXT SESSION PROMPT — Pre-Deploy S14c part 1: the moments' engine and its transport, UNARMED

> Overwritten each time a session hands off. Current hand-over: **October 22, 2026, after S14c's gate RULED**
> (`docs/EVENTS_SPEC.md`; commits through the hook — `git log -4`).
>
> **What the last session delivered:**
> - **S14b COMPLETE** (VP-1 "The Emperor's Designs", `SYSTEMS_REFERENCE.md` §143–§146): the roads, the road page, THE
>   DECISIVE PEACE and the Acts; the road arms stamp on all three seeds (RH turn 13, TH turn 20; CS never).
> - **S14c's gate RULED** (`docs/EVENTS_SPEC.md`): of ~40 moments of 1805–1807, **four letters** earn a place — the
>   Bavarian Match (T8), the Throne of Holland (T18, when Holland slips), the Crown of the Reich (Road I, after the
>   Confederation), the Decree of Berlin (T29, only when it would shut a port). One store (`world.moments`), the
>   call-to-arms transport (`incoming_proposal`, `proposal_type = "moment_letter"`, no court), a closed op table of
>   shared functions with one `plan` (shown = applied), banded windows resolved at boot, no dice. The situational class
>   and Trafalgar / Tilsit struck with their covering surfaces (A1 — flagged for the user in STATUS). Siblings
>   S14C-X1 … X17 filed in `BUG_FIXES.md` §S14C, OPEN, owned by parts 1 and 2.
>
> **Traps the last session paid for:**
> - **Probe the board before you promise a consequence.** The first synthesis quoted a Holland closure and a Decree
>   bite the shipped board does not have (Holland boots at war with Britain; no client is Autonomous and at peace with
>   Britain). Every quote derives from the real function, and prints "unchanged" at zero.
> - **The code-health ratchet is at every cap:** module levers 231 / 231 (a seam is a FUNCTION, never a `THE_X = True`),
>   functions over 500 lines 28 / 28 (`WorldState.to_dict` is exactly 500 — fold the new key into an existing line,
>   S14C-X16), silent handlers 6 / 6 (every `except` calls `report(exc, "mod.fn: step")`), `CLAUDE.md` ~61,930 / 62,000.
> - **`reforms.enact_law` never spends the admin action** — the executor does (`world.use_admin_action()`).
> - **Copy a found playtest script WHOLE** (`policy_at` is part of the road). **The Bash heredoc halves backslashes**
>   (a `\b` became a backspace byte) — write scripts with the Write tool and scan for `\x08`.
> - **`headline_lead_memory` is rebuilt every morning from an allowlist**; dispatch weights stay tie-free per class.
> - The full suite is ~32,700 tests, ~7.5 minutes at `-n 8`; two pins need bytecode (`env -u PYTHONDONTWRITEBYTECODE`);
>   `tools/score_run.py run --only` takes one arm per flag.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate, AO's three questions, SF-NAV-1-D1 and
> A1 — the gate's reduction of the row — are theirs to overrule). Paste everything below the line as the opening
> message of a fresh session.

---

Pre-Deploy S14c part 1 — the moments' engine and its transport, UNARMED — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -4` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/EVENTS_SPEC.md` (§0 the gate, §2 the deck, §3 the engine and its ten transport seams, §4 caps, §5 bands, §7 the series, §9 Part 1, §10 the siblings, §12 the corrections), `docs/BUG_FIXES.md` §S14C, `backend/game_logic/imperial_designs.py` (the store idiom: `store_from_data`, `armed`, the backfill), `backend/game_logic/call_to_arms.py` (`keeps_open`, `refuse_lapsed_letter` — the transport this rides), `backend/game_logic/treaty.py` (`_letter_kind`, `can_sign`, `refresh_letter_verdict`), `backend/models/dialogue_manager.py`, `backend/game_logic/turn_manager.py` (`lapse_pending_offers`, `_extract_lapse_info`), `backend/game_logic/campaign_variance.py` (`seeded_int`, `apply_scenario_variance`), `backend/game_logic/war_council.py` (the foreground), `backend/modding/validator.py` (`_validate_imperial_designs` as the model).

Scope (the record's §9 Part 1 — the design is the record's; flag any reversal):
0. **The rules:** every answer is a button whose command is the executor's; the LLM never affects mechanics; the deck is France's content and every effect on an AI court goes through the shared function; no module lever; no per-region scan in a hot path; serialization for the new field.
1. **The head — reproduce first:** the record's §1 measurements on ten seeds (Bavaria's life, Holland's loyalty path, the Decree's bite, the queue); S14C-X8 (the restamp erases a closed stamp) and X9 (the `"Unknown"` lapse fallback) on boards.
2. **Build:** `backend/game_logic/moments.py` (the store, `PREDICATES`, the closed `OPS`, `plan`, the tick at the tail of `_advance_turn_internal`, the lifecycle, R1–R4), `vassal.adjust_loyalty`, `war_council.record_in_tenure` / `foreground_in_tenure`; `_validate_moments` (the date check through a validator-only `calendar.turn_for_date`); the variance branch; serialization (S14C-X16) and the backfill; the ten transport seams at their backend halves; `imperial_designs.road_state` and its callers (S14C-X17); the `moment` log type and its pin flips; the siblings S14C-X4, X6, X7, X8, X9, X13, X16, X17.
3. **Measure:** the shipped boot stays UNARMED (no `moments` block), so `BASELINE_SERIES` and the commanded arms are byte-identical by construction — prove it with each seam's reach counted at 0.

Done when (§9 Part 1) on a staged armed fixture (`tests/fixtures/moments_block.json`) each letter arrives at its resolved turn when its premise holds and is `passed` when it does not; each answer applies exactly its plan on three boards; a closed Accept leaves the letter standing; lapse equals decline and writes no cooldown key; every status survives a save round trip; bands resolve (`historical` = `value`, ten seeds in band, unbanded never varies); the validator refuses each bad block; the shipped boot is unarmed; `BASELINE_SERIES` byte-identical with each seam's reach counted at 0; the ratchet's counts unchanged; S14C-X4, X6, X7, X8, X9, X13, X16, X17 FIXED with their pins; the full suite green through the hook; STATUS ▶ NEXT UP names part 2 and this file is overwritten for it.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10); a change that reaches the AI or the backend runs the attribution arms with `BASELINE_SERIES` byte-identical or every movement attributed (count the reach); edit CRLF files with a script that preserves line endings; grep-verify any agent's bulk `.gd` edits. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
