"""Session UI-6 (November 13, 2026) — `MarshalState`, the one reading of a marshal.

The Generals roster, the war room's selection card and the command desk's marshal row all read a marshal through
`scripts/marshal_state.gd`, so the three cannot disagree. These pins hold its contract from the source: the seven
fixed order slots in their digit order, the idle test mirroring `main._idle_marshals()`, both payload shapes read,
and no `or` used to pick a value (GDScript's `or` answers a bool — UI-5's "true" on every locked vassal chip).
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SRC = (SCRIPTS / "marshal_state.gd").read_text(encoding="utf-8")
MAIN = (SCRIPTS / "main.gd").read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    start = src.index("func " + name + "(")
    nxt = src.find("\nstatic func ", start + 1)
    nxt2 = src.find("\nfunc ", start + 1)
    ends = [e for e in (nxt, nxt2) if e != -1]
    return src[start:min(ends)] if ends else src[start:]


class TestTheSlots:

    def test_seven_fixed_slots_in_digit_order(self):
        verbs = re.findall(r'\{"slot": (\d), "verb": "(\w+)"', SRC)
        assert verbs == [("1", "hold"), ("2", "fortify"), ("3", "drill"), ("4", "scout"),
                         ("5", "retreat"), ("6", "garrison"), ("7", "cancel")]

    def test_slot_two_wears_unfortify_while_fortified(self):
        assert '"alt_verb": "unfortify", "alt_label": "Unfortify"' in SRC
        body = _func(SRC, "order_specs")
        assert 'if verb == "fortify" and fortified:' in body

    def test_a_refused_verb_stays_in_its_slot_locked_with_a_string_reason(self):
        body = _func(SRC, "order_specs")
        assert "reason = str(refusals[verb])" in body
        assert '"locked": locked' in body and '"reason": reason' in body
        # every slot is appended whatever its state: a digit never shifts
        assert body.count("out.append(") == 1

    def test_cancel_is_locked_without_a_standing_order(self):
        body = _func(SRC, "order_specs")
        assert "if not has_standing_order(view):" in body
        assert "reason = NO_STANDING_ORDER" in body


class TestTheReading:

    def test_idle_mirrors_main_idle_marshals(self):
        """`main._idle_marshals()` excludes a standing order, works, drill (and its lock) and the square — the
        kit's `is_idle` reads the same four facts."""
        main_idle = _func(MAIN, "_idle_marshals")
        for field in ("in_strategic_mode", "strategic_command_type", "fortified", "drilling",
                      "drilling_locked", "square_formation"):
            assert field in main_idle, field
        board = _func(SRC, "from_board")
        for field in ("in_strategic_mode", "strategic_command_type", "fortified", "drilling",
                      "drilling_locked", "square_formation"):
            assert field in board, field
        idle = _func(SRC, "is_idle")
        for key in ('"order_type"', '"fortified"', '"drilling"', '"square"'):
            assert key in idle, key

    def test_both_payload_shapes_are_read(self):
        overview = _func(SRC, "from_overview")
        for field in ("strategic_order", "seeks_audience", "is_fortified", "is_drilling", "is_broken",
                      "is_retreating", "square_formation", "order_prices", "order_refusals"):
            assert field in overview, field
        board = _func(SRC, "from_board")
        for field in ("tactical_state", "order_prices", "order_refusals", "strategic_target"):
            assert field in board, field

    def test_every_status_key_is_named(self):
        body = _func(SRC, "status_of")
        for key in ("prisoner", "petition", "broken", "retreating", "pursuing", "holding", "supporting",
                    "marching", "fortified", "drilling", "square", "idle"):
            assert '"' + key + '"' in body or "'" + key + "'" in body or key in body, key

    def test_no_or_picks_a_value(self):
        """The UI-5 trap, repo-wide in test_ui5_full_measure; here for this file in its own words."""
        assert not re.search(r"(str|int|float)\([^()]*\.get\([^()]*\)[^()]* or ", SRC)

    def test_prices_are_ints(self):
        body = _func(SRC, "order_specs")
        assert "price = int(prices[verb])" in body
        assert '"slot": int(slot["slot"])' in body
