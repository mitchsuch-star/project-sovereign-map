"""Row IC, Session 3 — THE VOICE of a marshal on his own.

`docs/INDEPENDENT_COMMAND_SPEC.md` §6.7, §8.4 ("His answer — one line in his
own voice"), §8.6. The user's words for this session: "make this engaging make
the typing really fun". A man you type a task to answers you — before you press
Enter — in a voice that is HIS: Ney never waits, Davout never wastes a man,
Murat wants to ride, Lannes wants the guns, Masséna will not let go of what he
holds, Bernadotte is slow and says so. The answer changes as your words change
("boldly" to Davout, "carefully" to Ney).

Golden rule 11 (plain words): every line is everyday English; "Sire" is the
only period word. Golden rule 6: the lines are AUTHORED, never written by a
model, and they decide nothing — the numbers beside them come from the one
pure reading (`own_order`).

No die: a man with several lines of one kind says the one keyed by the turn
and his name (`_pick`), so the same question asked twice in a turn gets the
same answer, and a reload changes nothing. Session 4 (IC-13) adds "said
lately" and the portrait.
"""
from __future__ import annotations

import zlib
from typing import Dict, Sequence

# The six men the design names, then a default by nature. Each kind is a list;
# `{place}`, `{foe}`, `{friend}` are filled by the caller.
LINES: Dict[str, Dict[str, Sequence[str]]] = {
    "Ney": {
        "ack": ("At last, Sire! Leave it to me.", "I'll see to it, Sire — and I won't be slow about it."),
        "bolder": ("Boldly, Sire? I know no other way.",),
        "careful": ("Carefully? ...Very well, Sire. I'll count them before I go in.",),
        "object": ("Hold, Sire? With the enemy right there in front of me?",),
        "proposal": ("Give me something to take, Sire, and I'll take it.",),
        "idle": ("Nothing to fight yet. I don't like it, Sire.",),
    },
    "Davout": {
        "ack": ("It will be done properly, Sire.", "Understood. I'll not waste a man."),
        "bolder": ("Boldly, Sire — very well. But I won't throw the corps away.",),
        "careful": ("Carefully. As I would have done it anyway.",),
        "object": ("Sire, those odds are poor. I would rather hold and dig in.",),
        "proposal": ("Let me hold here and dig in, Sire. When the enemy comes, I'll be ready.",),
        "idle": ("We're dug in and watching, Sire.",),
    },
    "Murat": {
        "ack": ("They won't outrun my horsemen, Sire!", "Leave it to the cavalry!"),
        "bolder": ("Boldly! Now you're speaking my language, Sire.",),
        "careful": ("Carefully... the horses won't like it, but very well.",),
        "object": ("Sit still, Sire? Horsemen are made to ride.",),
        "proposal": ("Point me at their weakest army, Sire, and I'll run it down.",),
        "idle": ("My scouts are out. Nothing worth a charge yet.",),
    },
    "Lannes": {
        "ack": ("Leave it to me, Sire.", "Done. Where the guns are, I'll be."),
        "bolder": ("Boldly suits me fine, Sire.",),
        "careful": ("Carefully — if you say so. I'll still go to the guns.",),
        "object": ("Sire, my friends will need me nearer the fighting than this.",),
        "proposal": ("Let me stand by whoever is nearest the fighting, Sire.",),
        "idle": ("Quiet for now. I'm listening for the guns.",),
    },
    "Massena": {
        "ack": ("I'll hold what is mine, Sire — and take more if I can.", "Consider it done, Sire."),
        "bolder": ("Boldly? Gladly, Sire.",),
        "careful": ("Carefully. I'll keep what I have, then.",),
        "object": ("Give up good ground, Sire? I'd rather not.",),
        "proposal": ("Let me hold my front, Sire, and strike out from it when I see the chance.",),
        "idle": ("Holding firm, Sire. Nobody is taking this ground from me.",),
    },
    "Bernadotte": {
        "ack": ("As you wish, Sire. In my own time.", "Very well. I'll get to it."),
        "bolder": ("Boldly... if you insist, Sire.",),
        "careful": ("Carefully. Yes, that suits me.",),
        "object": ("Sire, I'd sooner not risk my corps on that.",),
        "proposal": ("Let me hold in the rear, Sire. Someone must.",),
        "idle": ("All quiet here, Sire.",),
    },
}

BY_NATURE: Dict[str, Dict[str, Sequence[str]]] = {
    "bold": {
        "ack": ("I'll see to it, Sire.",),
        "bolder": ("Boldly, Sire. Gladly.",),
        "careful": ("Carefully, Sire. Very well.",),
        "object": ("Hold, Sire? The enemy is right there.",),
        "proposal": ("Give me something to take, Sire.",),
        "idle": ("Nothing to fight yet, Sire.",),
    },
    "careful": {
        "ack": ("It will be done with care, Sire.",),
        "bolder": ("Boldly, Sire... I'll do my best.",),
        "careful": ("Carefully. Good.",),
        "object": ("Sire, I don't like those odds.",),
        "proposal": ("Let me hold here and dig in, Sire.",),
        "idle": ("Dug in and watching, Sire.",),
    },
}

# What a man who cannot be set on his own says (§6.2).
LITERAL_REFUSAL = "Give me my orders to the letter, Sire."


def _key(name: str) -> str:
    """His roster key, without the accent the display adds."""
    return str(name or "").replace("é", "e").replace("É", "E")


def _pick(lines: Sequence[str], name: str, turn: int) -> str:
    """One of his lines, keyed by his name and the turn — never a die."""
    if not lines:
        return ""
    seed = zlib.crc32(f"{_key(name)}:{int(turn)}".encode("utf-8"))
    return str(lines[seed % len(lines)])


def line(name: str, nature: str, kind: str, turn: int = 0, **fill) -> str:
    """His line of `kind` ("ack", "bolder", "careful", "object", "proposal",
    "idle"), filled; "" when he has none of that kind."""
    own = LINES.get(_key(name), {})
    pool = own.get(kind) or BY_NATURE.get(nature, {}).get(kind) or ()
    said = _pick(pool, name, turn)
    try:
        return said.format(**fill) if fill else said
    except (KeyError, IndexError):
        return said
