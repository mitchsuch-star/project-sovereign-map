# Session 4 Audit Handoff

Date: April 12, 2026
Scope: `PL-28`, `PL-26`
Next routed session: `PL-29`

## What Landed

- `PL-28`: France now gets a deterministic defeat-imminent warning when exactly one living French marshal and/or one controlled French region remains.
- `PL-28`: The warning is emitted into both the persistent notification rail and the morning dispatch payload, and stale copies are cleared once France rises back above the threshold.
- `PL-26`: The naive turn-1 `Ney -> Wellington` opener is intercepted once per campaign to surface a better preparation line before troops are committed.
- `PL-26`: The opener guidance adapts if `Drouot` is unavailable and still points to a viable non-artillery setup line.
- `PL-26`: A deterministic regression compares the naive opener against a prepared artillery-softened alternative and proves the prepared line is materially better.

## Files Changed

- `backend/notifications.py`
- `backend/game_logic/turn_manager.py`
- `backend/game_logic/dispatch.py`
- `backend/models/world_state.py`
- `backend/commands/combat_executor.py`
- `godot-client/project-sovereign/scripts/main.gd`
- `godot-client/project-sovereign/scripts/dispatch_view.gd`
- `godot-client/project-sovereign/scripts/notification_bar.gd`
- `tests/test_session4_first_hour_pressure.py`
- `docs/STATUS.md`
- `docs/BUG_FIXES.md`

## Acceptance Mapping

### PL-28

- Warning source of truth is tied to the surviving defeat rules only: one living marshal and/or one controlled region.
- Warning text does not mention the obsolete capital-loss defeat path.
- Notification path uses a dedicated `defeat_imminent_warning` type and dismisses stale copies before re-adding the current warning.
- Dispatch path exposes `defeat_imminent_warning` in the morning payload and the Godot terminal/reread surfaces render it.
- Recovery path is covered: if France climbs back above the threshold, the warning disappears and the notification type is cleared.

### PL-26

- Trigger is deterministic and narrow: player-controlled `Ney` from `Belgium` into `Wellington` at `Waterloo`, turn 1, no staged French support in `Belgium`, and only once per campaign.
- Guidance uses the existing inline report/result surface in Godot instead of a new popup system.
- Guidance names `Drouot` bombardment support when available and falls back to `Davout` / another French marshal when artillery is unavailable.
- Regression coverage compares naive `Ney -> Wellington` against `Drouot bombard Wellington` then `Ney -> Wellington` across fixed RNG seeds.

## Verification Run

Executed with `.\.venv\Scripts\python.exe -m pytest ...`

- `tests/test_session4_first_hour_pressure.py -q`
- `tests/test_systems_audit_v2_session4.py -q`
- `tests/test_systems_v3_session2.py -q`
- `tests/test_war_action_verification.py -q`
- `tests/test_systems_v3_session4.py -q`

Result: 98 tests passed.

Known environment note: pytest emitted the existing `.pytest_cache` permission warning in this Codex environment, but test execution completed successfully.

## Manual Audit Suggestions

- Start a fresh campaign and verify the turn-1 `Ney, attack Wellington` command shows guidance once, then allows the second attempt to proceed normally.
- Force France to one surviving marshal, then end turn and confirm:
  - notification rail shows `defeat_imminent_warning`
  - morning dispatch shows the same warning
  - reread dispatch screen also shows it
- Recover above the threshold and confirm the warning no longer appears on the next dispatch/notification refresh.

## Remaining Risk

- Godot rendering for the new dispatch field was updated, but there is no automated Godot UI test coverage in this slice. The backend contract is covered; frontend visibility still merits a quick manual pass.
