"""AI-1 (Combat Overhaul Phase 6 — Parser & Play-Friction Cleanup).

The enemy-AI decision tree in `EnemyAI._evaluate_marshal` is a sequential
early-return chain whose comment labels ("PRIORITY <n>") are meant to track the
evaluation order. The DEFENSIVE REINFORCEMENT POSITIONING rung was labelled
"P4.78" but has always been evaluated AFTER P7 strategic movement (before P7.5
stagnation) — the label was "decoupled from evaluation order", latent tech-debt.

AI-1 relabels it to P7.4 so the labels are monotonic in code order. This is a
BEHAVIOR-PRESERVING relabel: the rung's returned priority score stays 7 (the
caller's P8-retreat suppression keys off `action_priority == 7`) and its code
position is unchanged.

These guards are source-level and fails-before/passes-after: on the pre-fix
code the "4.78" label appears between "7" and "7.5" (a decrease); after the
relabel the whole sequence is non-decreasing.
"""
import inspect
import re

from backend.ai.enemy_ai import EnemyAI


def _priority_labels():
    src = inspect.getsource(EnemyAI._evaluate_marshal)
    return [float(m) for m in re.findall(r"PRIORITY\s+([0-9]+(?:\.[0-9]+)?)", src)]


def test_priority_labels_are_monotonic_in_code_order():
    """The evaluation order and the tier labels must agree — each PRIORITY label
    is >= the previous one as they appear top-to-bottom in the method source."""
    labels = _priority_labels()
    assert labels, "no PRIORITY labels found — did the method move?"
    for prev, nxt in zip(labels, labels[1:]):
        assert nxt >= prev, (
            f"priority labels out of order: {prev} is followed by {nxt} "
            f"(a rung is mislabelled relative to its evaluation position). "
            f"Full sequence: {labels}")


def test_defensive_reinforcement_relabelled_to_7_4():
    """The specific relabel: the mislabeled 4.78 is gone; 7.4 is present."""
    labels = _priority_labels()
    assert 4.78 not in labels
    assert 7.4 in labels


def test_reinforcement_rung_still_returns_priority_7():
    """The returned score stays 7 — load-bearing, because the action loop marks a
    priority-7 move as an advance and suppresses P8 retreat on it. A relabel must
    NOT touch this."""
    src = inspect.getsource(EnemyAI._evaluate_marshal)
    # The reinforcement rung: `_find_defensive_reinforcement_position(...)` must
    # still be followed by `return (reinforce_action, 7)`.
    m = re.search(
        r"_find_defensive_reinforcement_position\(.*?\)"
        r".*?return \(reinforce_action, (\d+)\)",
        src, re.DOTALL)
    assert m is not None, "defensive-reinforcement rung structure changed"
    assert m.group(1) == "7"
