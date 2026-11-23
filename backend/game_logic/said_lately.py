"""Row IC, Session 4 — IC-13: SAID LATELY.

`docs/INDEPENDENT_COMMAND_SPEC.md` §11 ("the rules of a line": *no line twice
within his last three; on the historical seed the first line of each set is
said; every line is written by hand*); `docs/MARSHAL_VOICE_BIBLE.md`.

A marshal remembers the last three lines he SAID (`Marshal.said_lately` — a
short key of each line's words, saved with him). Every picker of a quoted line
— a man on his own (`own_voice`), an order answered or completed and the
after-battle line (`marshal_voice`), the enemy's own line (`enemy_voice`), a
petition's header (`jealousy` — a PURE choice: the card is built and rebuilt,
so it is never recorded) — asks here which line he says next:

  * `choose` is PURE: the first line of the pool, in its rotation from
    `start`, that is not among his last three. A preview, a question and
    "Tonight" call only this — asking changes nothing, and the line shown
    before an order is given is the line he says when it is given;
  * `say` is the ONE WRITER: called where a line is really said (an order
    given, a night's act, the morning, a battle). It rides
    `marshals`, so an order taken back takes its line back with it.

The rule is ABSOLUTE: a man whose every line of a pool is among his last three
says NOTHING — the staff's plain sentence stands alone — rather than repeat
himself. (A pool of four lines or more can never run dry; the pin
`tests/test_ic13_every_man_his_own_line.py` counts every pool in the game and
walks every man through thousands of moments.)

No die anywhere (golden rule 6: the lines decide nothing and are never
generated). `start_for` is where the campaign's seed enters: 0 on the
historical seed — the first line of each set is said first — and a fixed place
in the set on any other seed.
"""
from __future__ import annotations

import zlib
from typing import List, Optional, Sequence

KEPT = 3     # "no line twice within his last three"


def key_of(line: str) -> int:
    """A line's key: its words, folded (placeholders and all — a template's
    key is the template's, so "the order was {order}" is one line whatever
    the order)."""
    return int(zlib.crc32(" ".join(str(line or "").split()).encode("utf-8")))


def lately(marshal) -> List[int]:
    """The keys of the last three lines he said, oldest first. PURE."""
    held = getattr(marshal, "said_lately", None) if marshal is not None else None
    return [int(k) for k in held][-KEPT:] if isinstance(held, (list, tuple)) else []


def choose(marshal, pool: Sequence[str], start: int = 0) -> str:
    """The line he says next from `pool`: in rotation from `start`, the first
    that is not among his last three; with none such (a pool of three lines or
    fewer, all said lately) he says NOTHING — "" — and the plain sentence
    beside it stands alone. "" for an empty pool. PURE — a man with no memory
    (None, or an old save) says the line the rotation names, exactly as before
    this module."""
    lines = [str(line) for line in (pool or ()) if line]
    if not lines:
        return ""
    count = len(lines)
    first = int(start) % count
    said = lately(marshal)
    if not said:
        return lines[first]
    for step in range(count):
        line = lines[(first + step) % count]
        if key_of(line) not in said:
            return line
    return ""


def say(marshal, line: str) -> None:
    """He SAID it: the ONE writer of `Marshal.said_lately`. Nothing for an
    empty line or a man the caller does not hold."""
    if marshal is None or not line:
        return
    key = key_of(line)
    kept = [k for k in lately(marshal) if k != key] + [key]
    marshal.said_lately = kept[-KEPT:]


def speak(marshal, pool: Sequence[str], start: int = 0, said: bool = True) -> str:
    """`choose`, and — where the line is really said — `say`."""
    line = choose(marshal, pool, start)
    if said:
        say(marshal, line)
    return line


def start_for(world, name: str, kind: str, count: int) -> int:
    """Where a set's rotation starts for this man: 0 on the historical seed
    ("the first line of each set is said"), a fixed place by the campaign's
    seed, his name and the kind otherwise. Never a stream."""
    if count <= 1:
        return 0
    from backend.game_logic import campaign_variance as _cv
    seed: Optional[str] = str(getattr(world, "campaign_seed", "") or "") if world is not None else ""
    if not seed or _cv.is_historical(seed):
        return 0
    return int(_cv.seeded_int(seed, f"voice::{name}::{kind}", 0, count - 1))
