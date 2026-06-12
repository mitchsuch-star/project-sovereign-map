# Session prompt — Armistice + counter-offer findings (G4F-13+) and the untested settlement coverage sweep

You are continuing the Gate-4 manual settlement smoke fix loop on Project Sovereign
(Napoleonic strategy game; FastAPI backend port 8005, Godot 4.4.1 frontend). Read
`CLAUDE.md` and the June 11–12, 2026 entries at the top of `docs/STATUS.md` first:
fixes G4F-1..G4F-12 + GT-A5 are landed; you are picking up the next finding cluster.
Use ledger codes **G4F-13 onward**, one STATUS entry per landed cluster, commit
directly to master (the pre-commit hook runs `ruff check backend/` + the full pytest
suite — never bypass), and push after each commit.

## Conventions you must follow

- **Reproduce on the wire before fixing.** Probe scripts live in `smoke_logs/`
  (untracked) — copy the patterns in `smoke_logs/drive_g4f8_probe.py` and
  `smoke_logs/drive_carry_consistency_probe.py`: POST `/command` with structured
  `propose_common_peace`, POST `/respond_to_diplomatic_dialogue` with
  `{"choice": <action>, "action_params": {...}}`.
- **Server restart** (PowerShell, from repo root):
  `$env:PYTHONPATH='C:\Users\User\PycharmProjects\project-sovereign-map';
  $env:SOVEREIGN_SMOKE_START='settlement_multilateral';
  Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "backend/main.py"
  -WorkingDirectory <repo root> -NoNewWindow` (add `$env:LLM_MODE='mock'` for probes;
  leave unset for the user's manual testing — their `.env` is anthropic).
- **Offline probes** patch the scorer at the stable seam
  `backend.game_logic.settlement_scoring.calculate_common_peace_acceptance`
  (see `tests/test_settlement_recurring_gold.py` fixtures).
- If you touch any `.gd` file, regenerate the parse report:
  `& "C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64.exe"
  --headless --quit --path godot-client/project-sovereign --script ../../tools/godot_parse_check.gd`
  (note: the exe is NESTED inside a same-named folder).
- Tests for smoke findings go in `tests/test_settlement_gate4_leg1_fixes.py`
  (the G4F ledger file) or the domain file if one exists.
- Never-wordless rule (D3): any click that changes nothing must say why, in the
  popup the player is looking at (`authoring_voice_beats` ride restaged dialogues).
- Design changes need explicit user sign-off via AskUserQuestion BEFORE coding
  (precedent: GT-A5). Two such gates are flagged below.

## Part 1 — user findings to investigate and fix (in priority order)

### F1 — "Enemy will counter" but they never do
The bilateral acceptance verdict `COUNTER_OFFER` (from `calculate_acceptance`,
`backend/game_logic/diplomacy.py` ~line 6440) renders in the preview as a
counter expectation, but the user reports a counter NEVER arrives after sending.
Investigate the send path: where a sent proposal resolving to `COUNTER_OFFER`
should produce the AI counter (M3 counter-offer machinery in
`backend/game_logic/ai_diplomacy.py`; `counter_offer` is a registered
current-turn dialogue type in `backend/models/dialogue_manager.py` ~line 53).
Determine whether the counter is (a) never generated, (b) generated but never
surfaced (popup/mailbox wiring — remember the recurring dtype-whitelist bug
class in `main.gd` ~line 18), or (c) only generated for some proposal types.
Fix so a COUNTER_OFFER verdict actually yields a counter dialogue/mailbox entry,
or — if design says counters only fire in specific cases — make the preview
verdict copy stop promising one. Wire-probe both before and after.

### F2 — Armistice option doesn't always appear (even after dropping Prussia)
The blocked-REVIEW pair substitutes (`seek_bilateral_peace` /
`seek_armistice_instead`) are eligibility-gated by
`evaluate_pair_peace_substitute_eligibility` in
`backend/game_logic/settlement_validation.py`; per SC-29's disabled-vs-hidden
policy only `cooldown_active`-class refusals render disabled — every other
refusal HIDES the button entirely, with no explanation. Also check
`armistice_cooldowns` (post-expiry cooldown, `backend/game_logic/diplomacy.py`
~2555/2591) and any already-ARMISTICE state checks. Reproduce the user's path:
multilateral table → drop Prussia (cover_drop) → submit blocked → inspect which
refusal code suppressed the armistice arm. Outcome: either a real eligibility
bug fix, or (UX) widen the disabled-with-reason rendering so a hidden armistice
option is explained — the user could not tell why it was absent.
**Also verify the F1 wizard's armistice availability** for the same pair.

### F3 — Armistice acceptance odds looked different / lower; "maybe terms were different — check"
Two strong leads:
1. **Variant-type overwrite trap.** Acceptance for armistice uses war-score
   variant types (`armistice_winning` / `armistice_losing`) whose
   BASE_DISPOSITION differs from generic `armistice`; there is an explicit
   warning comment in `backend/commands/diplomatic_executor.py` (~line 3152,
   modify_harsh): "Preserve war-score variant type ... overwriting with generic
   proposal_type changes BASE_DISPOSITION and can invert acceptance odds."
   The G4F-8 pair-substitute handoff (`_execute_pair_substitute_handoff` in
   `backend/game_logic/settlement_actions.py`) passes generic
   `proposal_type="armistice"` into `classify_diplomatic_intent`/
   `generate_dialogue` — trace whether the variant is preserved end-to-end
   (preview estimate vs send-time resolution must use the SAME type).
2. **Armistice suggestions may carry terms.** Check `_build_base_terms` /
   `generate_suggested_terms` for armistice types in
   `backend/game_logic/diplomatic_templates.py`: if the suggestion engine
   attaches demands to an armistice the harshness penalty lowers its odds vs
   a bare ceasefire — decide (with code evidence) whether armistice proposals
   should carry terms at all; if they shouldn't, suggest/send them bare.
   Note the G4F-9 easing ladder (Stage 3.5, same file) already gates on the
   armistice family — make sure it doesn't fight your fix.
Compare like-for-like: same pair, same turn — peace preview odds vs armistice
preview odds, and preview odds vs actual send resolution. Pin with tests.

### F4 — Armistice mechanics are unclear in the UI (+ design gate: malleable duration)
Mechanics (verified): `ARMISTICE_DURATION = 5` hardcoded
(`backend/game_logic/diplomacy.py:3547`); expiry processor at ~8835 — after 5
turns, relations >= -60 auto-converts to PEACE (cleanup runs), relations < -60
returns to WAR under the same war id; war-score ticking pauses; no trade.
The UI never explains ANY of this at decision time.
- **UX fix (no gate needed):** the armistice preview/confirm
  (`war_context_snapshot` consumers — `_build_peace_preview_content` in
  `godot-client/project-sovereign/scripts/proposal_confirm_popup.gd` and the
  snapshot builder `build_war_context_snapshot` in diplomacy.py ~3606, which
  already exposes `armistice_remaining_turns` for live armistices) should state:
  duration (5 turns), the relations >= -60 auto-peace rule, the < -60
  back-to-war rule, and that no terms change hands. Also surface remaining
  turns + the projected outcome (current relations vs the -60 line) on the war
  detail / wherever an active armistice shows.
- **Design gate (AskUserQuestion BEFORE coding):** "malleable armistice times" —
  options to offer: (a) keep fixed 5 + explain it (cheapest), (b) duration as an
  authorable term on the armistice proposal (e.g. 3–10 turns, acceptance-priced
  so longer truces cost more), (c) relation/war-score-scaled duration. If the
  user picks (b) or (c), spec the acceptance pricing before implementing and
  update `docs/SYSTEMS_REFERENCE.md`.

## Part 2 — untested coverage sweep (verify each; fix anything broken as further G4F items)

These are NOT known bugs — they are the parts of the settlement surface no eyes
have touched. For each: drive it on the wire (and/or in Godot), and apply the
session's standing defect classes — silent no-op, contradictory copy, thin or
raw labels, popup vanishing on error, leader-pair label where coverage label
belongs:

1. **Coverage edits** — `settlement_cover_drop` Prussia from a holdout row (pair
   stays at war; baseline redraws for Britain alone), re-open and
   `settlement_cover_add` it back via the coverage suggestion. Dropping the LAST
   covered court must refuse with "at least one covered enemy must remain" —
   never a dead popup.
2. **Holdout one-click affordances** — the per-row `Ease <court>` / `Drop
   <court>` buttons on holdout rows specifically (distinct from the rail dials).
3. **Armistice arm of the G4F-8 chooser** — "Armistice with <court> only" goes
   through the confirm-step flow and hands off to the armistice flavor (overlaps
   F2/F3 — test it after those fixes).
4. **White-peace path** — ease/remove until the package is bare `peace` and
   submit: distinct copy ("A white peace for ..."), labeled ratify action, no
   crash on an empty terms list.
5. **SC-28 end-turn discard notice** — stage a draft, do NOT submit, end turn:
   exactly one notice naming the draft a reopen would have restored (CH-3
   re-derived it from the scoped store).
6. **Dependency clauses via the rows** — author vassalage / subjugation /
   liberation / forced_alliance through `Add demand` in-game: eligibility gating
   (ineligible options simply absent), the Continental System sub-link on
   forced_alliance, and the coalition threat projection copy
   (`compute_forced_alliance_threat_preview`, +15/clause, 60/80/90 thresholds)
   surfacing when a forced alliance is authored. Backend apply + reflection
   already audited (G4F-11) — this is the AUTHORING surface.
7. **Archived-war re-entry** — after ratifying, click the old war anywhere it
   lingers: must route to `settlement_history`, never POST a stale
   `propose_common_peace`.
8. **Save/load mid-authoring** — save with a staged draft + an active recurring
   tribute stream, load, reopen: draft restored (PF-2 scoped store), stream
   still ticking, ledger economy block intact.

## Part 3 — related-issue scan

After Parts 1–2, sweep for siblings of whatever you fixed (this session's pattern:
every finding had relatives — e.g. the thin-label class appeared in three places).
Specifically: grep for other consumers of the armistice variant types, other
verdict copy that promises AI behavior (counters, revisions, waiting) that may not
fire, and other hardcoded durations surfaced to the player without explanation.
File anything real as further G4F entries; fix small ones in-loop, and for
anything needing design input, stop and ask.

## Verification bar (every landed fix)

- New/updated tests in the G4F ledger file or domain file; full suite green BOTH
  orderings via the pre-commit hook; `ruff check backend/` clean.
- Wire probe demonstrating before/after for each player-visible change.
- Godot parse report regenerated if `.gd` changed.
- STATUS entry per cluster; commit to master; push.
- Restart the smoke server for the user when done:
  multilateral scenario, NO `LLM_MODE` override (their `.env` runs anthropic).
