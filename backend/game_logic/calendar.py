"""HC-0 "The Calendar" — display-only turn dating (gate §2a).

One turn = HALF A MONTH (~15 days): two turns per month, 24 per year.
The anchor is authored in the scenario JSON as a top-level `start_date`
("YYYY-MM-DD"); turn 1 covers the half-month containing that date, so the
1805 boot (Sept 25) opens on "Late September 1805".

Pure derivation — the label is never stored, no mechanic reads it
(`current_turn` stays the single source of time; HC-6's seasons gate is
where the calendar would become mechanical). A world with no anchor (the
legacy fixture) derives "" and every "Turn N" surface renders exactly as
before — the label is additive, never a replacement.
"""

import re
from typing import Optional, Tuple

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

TURNS_PER_YEAR = 24  # two half-month turns per month

_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")

# Days-per-month for anchor validation (Feb 29 accepted in leap years —
# the derivation itself only cares whether the day falls before/after
# the 15th, but a scenario authoring "1805-02-30" should hard-fail at
# the validator, not silently date the campaign).
_MONTH_DAYS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def parse_start_date(start_date: str) -> Optional[Tuple[int, int, int]]:
    """'YYYY-MM-DD' -> (year, month, day), or None on absent/invalid."""
    if not start_date or not isinstance(start_date, str):
        return None
    match = _DATE_RE.match(start_date.strip())
    if not match:
        return None
    year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
    if not (1 <= month <= 12):
        return None
    if not (1 <= day <= _MONTH_DAYS[month - 1]):
        return None
    return year, month, day


def calendar_label(start_date: str, turn: int) -> str:
    """Derive "Early/Late {Month} {Year}" for a 1-based turn.

    Half-month arithmetic: the anchor day picks the opening half
    (day <= 15 -> "Early", else "Late"); each turn advances one half.
    Returns "" without a valid anchor — the legacy world's dormancy.
    """
    parsed = parse_start_date(start_date)
    if parsed is None:
        return ""
    try:
        turn = int(turn)
    except (TypeError, ValueError):
        return ""
    if turn < 1:
        return ""
    year, month, day = parsed
    half_index = (year * TURNS_PER_YEAR
                  + (month - 1) * 2
                  + (1 if day > 15 else 0)
                  + (turn - 1))
    out_year = half_index // TURNS_PER_YEAR
    within = half_index % TURNS_PER_YEAR
    out_month = within // 2
    half = "Early" if within % 2 == 0 else "Late"
    return f"{half} {MONTH_NAMES[out_month]} {out_year}"
