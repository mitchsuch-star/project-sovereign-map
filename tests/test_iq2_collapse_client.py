"""IQ-2 "The Collapse Is Legible" — the client half.

Measured in played 40-turn campaigns: a France reduced to one province, then
none, kept playing while every client surface narrated an ordinary campaign.
The backend builders add the keys; these pins hold the eight .gd renderers
to reading them, with the pre-IQ-2 literal kept as the fallback for an
absent key (the backend levers gate the keys, so a lever-down backend
renders the old client output exactly).

Source-census pins are scoped to CODE lines: full-line `#` comments are
dropped, and no line is ever split on `#` — that would gut every
`[color=#...` string (part e's lesson). Each census is falsifiable: it names
a line the edit introduced, so reverting the edit fails it.

Where the engine can be asked, the pin is behavioural: the backend vocabulary
the authority arms must match is read off `AuthorityTracker` itself, and the
enemy-phase transport is driven through `_build_visible_enemy_phase` to prove
the `captured_from` stamp the dialog reads survives the fog filter.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "godot-client" / "project-sovereign" / "scripts"


def _code_only(name: str) -> str:
    """Full-line comments dropped. Never split a line on `#`."""
    text = (SCRIPTS / name).read_text(encoding="utf-8")
    return "\n".join(ln for ln in text.splitlines() if not ln.strip().startswith("#"))


def _func_body(src: str, header: str) -> str:
    """One GDScript function: from `header` to the next top-level decl."""
    at = src.index(header)
    rest = src[at + len(header):]
    nxt = re.search(r"\n(?:func |static func |signal |var |const |@onready )", rest)
    return rest[: nxt.start()] if nxt else rest


# ═══════════════════════════════════════════════════════════════════════════
# main.gd — the end-turn banner and the morning dispatch
# ═══════════════════════════════════════════════════════════════════════════


class TestMainGd:
    def test_turn_banner_renders_the_collapse_line_in_the_error_colour(self):
        body = _func_body(_code_only("main.gd"), "func _display_turn_change(")
        assert 'event.get("collapse_line", "")' in body
        # Null-safe: `str(null)` would print "<null>" on every standing turn.
        assert "collapse_line is String and collapse_line != \"\"" in body
        assert re.search(
            r'add_output\("\[color=#" \+ Utils\.COLOR_ERROR \+ "\]" \+ collapse_line', body
        ), body
        # Beside the bankruptcy warning, not before the treasury.
        assert body.index("bankruptcy_turns") < body.index("collapse_line")

    def test_dispatch_heading_reads_the_backend_with_the_literal_fallback(self):
        body = _func_body(_code_only("main.gd"), "func _display_morning_dispatch(")
        assert 'defeat_imminent_warning.get("heading", "")' in body
        assert 'diw_heading = "DEFEAT WARNING"' in body, "the old literal is the fallback"
        assert '+ diw_heading + "[/color]' in body
        # The hard-coded header is gone as a direct render.
        assert 'Utils.COLOR_BERTHIER + "]DEFEAT WARNING[/color]' not in body

    def test_dispatch_names_no_field_army_and_keeps_the_ratio_otherwise(self):
        body = _func_body(_code_only("main.gd"), "func _display_morning_dispatch(")
        assert 'situation.get("no_field_army", false)' in body
        # IQ-2 review round: anchored on the WHOLE guard line — a substring
        # pin stayed green under `if false and typeof(no_field_army) ...`,
        # which kills the branch.
        assert re.search(r"(?m)^\s*if typeof\(no_field_army\) == TYPE_BOOL and no_field_army:\s*$",
                         body), body
        assert "France has no army in the field." in body
        assert "Estimated enemy strength: " in body, "the pre-IQ-2 sentence stays the else-arm"


# ═══════════════════════════════════════════════════════════════════════════
# dispatch_view.gd — the re-read screen mirrors main.gd
# ═══════════════════════════════════════════════════════════════════════════


class TestDispatchView:
    def test_heading_reads_the_backend_with_the_literal_fallback(self):
        src = _code_only("dispatch_view.gd")
        assert 'defeat_imminent_warning.get("heading", "")' in src
        assert 'diw_heading = "DEFEAT WARNING"' in src
        assert 'Utils.COLOR_BERTHIER + "]DEFEAT WARNING[/color]' not in src

    def test_no_field_army_mirror(self):
        src = _code_only("dispatch_view.gd")
        assert 'situation.get("no_field_army", false)' in src
        assert re.search(r"(?m)^\s*if typeof\(no_field_army\) == TYPE_BOOL and no_field_army:\s*$",
                         src), "the guard line, whole (IQ-2 review round)"
        assert "France has no army in the field." in src
        assert "Estimated enemy strength: " in src

    def test_both_renderers_word_the_no_army_fact_identically(self):
        """One fact, one sentence — the two dispatch renderers must agree."""
        pat = re.compile(r"France has no army in the field\.")
        assert len(pat.findall(_code_only("main.gd"))) == 1
        assert len(pat.findall(_code_only("dispatch_view.gd"))) == 1


# ═══════════════════════════════════════════════════════════════════════════
# strategic_ledger.gd — the collapse note and the levy's closed reason
# ═══════════════════════════════════════════════════════════════════════════


class TestStrategicLedger:
    def test_collapse_note_helper_reads_the_key_in_the_error_colour(self):
        src = _code_only("strategic_ledger.gd")
        body = _func_body(src, "func _collapse_note_line()")
        assert 'cached_data.get("collapse_note", "")' in body
        assert "Utils.COLOR_ERROR" in body
        assert 'return ""' in body, "absent/empty key renders nothing"

    def test_note_renders_atop_the_forces_book_and_above_the_territories(self):
        src = _code_only("strategic_ledger.gd")
        forces = _func_body(src, "func _render_forces():")
        assert "bbcode += _collapse_note_line()" in forces
        terr = _func_body(src, "func _render_territories():")
        assert "bbcode += _collapse_note_line()" in terr
        # ABOVE the list — and above the empty-list early return, which is
        # exactly the 0-province case.
        assert terr.index("_collapse_note_line()") < terr.index("No territories controlled.")
        assert terr.index("_collapse_note_line()") < terr.index("for t in territories:")

    def test_levy_closed_reason_replaces_the_depots_open_line(self):
        body = _func_body(_code_only("strategic_ledger.gd"), "func _render_economy():")
        assert 'levy.get("closed_reason", "")' in body
        at = body.index("closed_reason is String")
        # The depots-open line is the ELIF of the closed-reason arm.
        assert re.search(r'elif bool\(levy\.get\("open", false\)\):', body[at:])
        assert "The depots are open: " in body, "the pre-IQ-2 line is kept"


# ═══════════════════════════════════════════════════════════════════════════
# war_status_panel.gd + war_detail_popup.gd — whose settlement table it is
# ═══════════════════════════════════════════════════════════════════════════


class TestSettlementSide:
    def test_hud_tooltip_says_whose_table(self):
        body = _func_body(_code_only("war_status_panel.gd"), "func _build_war_tooltip(")
        assert 'war_data.get("settlement_tier_side", "")) == "theirs"' in body
        assert '"Settlement (theirs to impose): " + tier' in body
        assert '"Settlement: " + tier' in body, "ours/absent is unchanged"

    def test_war_detail_renders_theirs_in_the_loss_colour_not_gold(self):
        body = _func_body(_code_only("war_detail_popup.gd"), "func _render_war_detail(")
        assert 'w.get("settlement_tier_side", "")) == "theirs"' in body
        theirs = re.search(
            r'"Settlement Tier \(theirs to impose\): \[color=" \+ (\w+) \+', body
        )
        assert theirs, body
        assert theirs.group(1) == "COLOR_RED", "the popup's own loss colour, never gold"
        assert '"Settlement Tier: [color=" + COLOR_GOLD + "]"' in body, "ours/absent unchanged"


# ═══════════════════════════════════════════════════════════════════════════
# enemy_phase_dialog.gd — a province taken FROM us is a loss
# ═══════════════════════════════════════════════════════════════════════════


class TestEnemyPhaseCaptures:
    def test_lever_is_up(self):
        src = _code_only("enemy_phase_dialog.gd")
        assert "const OUR_LOSS_READS_AS_LOSS := true" in src

    def test_helper_reads_the_stamp_and_honours_the_lever(self):
        body = _func_body(_code_only("enemy_phase_dialog.gd"), "func _taken_from_player(")
        assert 'event.get("captured_from", "")' in body
        assert "if not OUR_LOSS_READS_AS_LOSS:" in body
        assert "taken is String and taken == _PLAYER_NATION" in body

    def test_conquest_line_is_red_when_ours_and_green_otherwise(self):
        body = _func_body(_code_only("enemy_phase_dialog.gd"), "func _format_action(")
        assert re.search(
            r"conquest_color = COLOR_ERROR if _taken_from_player\(event\) else Utils\.COLOR_CONQUEST",
            body,
        ), body
        assert '"[color=#" + conquest_color + "]    Region captured: "' in body
        # The old always-green render is gone.
        assert 'Utils.COLOR_CONQUEST + "]    Region captured: "' not in body

    def test_march_capture_of_our_province_reads_as_a_loss(self):
        body = _func_body(_code_only("enemy_phase_dialog.gd"), "func _format_action(")
        # IQ-2 review round: the line that DOES the work, not a neighbour —
        # swapping it for `Utils.COLOR_TEXT` left the old pins green.
        assert re.search(
            r"if OUR_LOSS_READS_AS_LOSS and taken_from == _PLAYER_NATION:\n\s*line_color = COLOR_ERROR\b",
            body), body
        assert '"[color=#" + line_color + "]- " + action_str' in body
        assert "var line_color = Utils.COLOR_TEXT" in body, "neutral stays the default"

    def test_battle_capture_arm_reads_the_same_helper(self):
        body = _func_body(_code_only("enemy_phase_dialog.gd"), "func _format_battle(")
        assert re.search(
            r"battle_capture_color = COLOR_ERROR if _taken_from_player\(event\) else Utils\.COLOR_CONQUEST",
            body), body
        # IQ-2 review round: the RENDER line must use it — reverting only the
        # render to the old always-green colour left the helper pin green.
        # (Since the review round the backend stamps `captured_from` on the
        # field-battle event, so this arm now fires for real.)
        assert '"[color=#" + battle_capture_color + "]    " + region + " CAPTURED!"' in body
        assert 'Utils.COLOR_CONQUEST + "]    " + region + " CAPTURED!"' not in body

    def test_the_transport_keeps_captured_from_through_the_fog_filter(self):
        """Behavioural: the stamp the dialog reads must reach it. A conquest
        of a French province rides `_build_visible_enemy_phase` (own-soil
        carve-out, PT-E5) with `captured_from` intact — so main.py needs no
        change for the client arm to fire."""
        import backend.main as M
        from backend.models.world_state import WorldState

        w = WorldState(player_nation="France", sovereign_map="europe")
        conquest = {
            "type": "conquest",
            "marshal": "Mack",
            "region": "Paris",
            "unopposed": True,
            "captured_by": "Austria",
            "captured_from": "France",
        }
        phase = {
            "nations": {
                "Austria": {
                    "actions": [{
                        "success": True,
                        "ai_action": {"marshal": "Mack", "action": "attack", "target": "Paris"},
                        "events": [conquest],
                        "new_state": object(),
                    }],
                    "action_count": 1,
                },
            },
            "total_actions": 1,
        }
        out = M._build_visible_enemy_phase(phase, w)
        assert out is not None
        acts = out["nations"]["Austria"]["actions"]
        assert len(acts) == 1, "the own-soil capture is never fogged out"
        evt = acts[0]["events"][0]
        assert evt["captured_from"] == "France"
        assert "new_state" not in acts[0]


# ═══════════════════════════════════════════════════════════════════════════
# diplomatic_ledger.gd — the authority arms speak the backend's vocabulary
# ═══════════════════════════════════════════════════════════════════════════


def _backend_authority_labels():
    """Every label `AuthorityTracker.get_authority_label` can emit, measured
    by walking the authority scale — never copied from the source."""
    from backend.models.authority import AuthorityTracker

    t = AuthorityTracker()
    seen = []
    for value in range(0, 101):
        t.authority = value
        label = t.get_authority_label()
        if label not in seen:
            seen.append(label)
    return seen


class TestAuthorityArms:
    def _arms(self):
        body = _func_body(_code_only("diplomatic_ledger.gd"), "func _render_talleyrand():")
        assert "if AUTHORITY_ARMS_READ_THE_BACKEND:" in body
        new_arm = body.split("if AUTHORITY_ARMS_READ_THE_BACKEND:", 1)[1].split("\n\telse:\n", 1)[0]
        return body, new_arm

    def test_lever_is_up(self):
        assert "const AUTHORITY_ARMS_READ_THE_BACKEND := true" in _code_only("diplomatic_ledger.gd")

    def test_every_backend_label_has_an_arm(self):
        labels = _backend_authority_labels()
        assert len(labels) == 5, labels
        _body, new_arm = self._arms()
        for label in labels:
            assert f'"{label}"' in new_arm, f"no colour arm for backend label {label!r}"

    def test_the_bottom_rung_is_red_and_the_top_green(self):
        _body, new_arm = self._arms()
        lines = new_arm.splitlines()

        def colour_after(label):
            for i, ln in enumerate(lines):
                if f'"{label}"' in ln:
                    return lines[i + 1].strip()
            raise AssertionError(label)

        assert colour_after("Emperor in Name Only") == "authority_color = Utils.COLOR_ERROR"
        assert colour_after("Divine Right") == "authority_color = Utils.COLOR_SUCCESS"
        assert colour_after("Questionable") == "authority_color = Utils.COLOR_ORANGE"

    def test_lever_down_arm_keeps_the_old_vocabulary(self):
        body, _new = self._arms()
        old_arm = body.split("\n\telse:\n", 1)[1]
        for label in ("Absolute", "Strong", "Stable", "Shaky", "Crumbling"):
            assert f'"{label}":' in old_arm


# ═══════════════════════════════════════════════════════════════════════════
# marshal_management.gd — a prisoner's card says he is a prisoner
# ═══════════════════════════════════════════════════════════════════════════


class TestPrisonerCard:
    def test_card_renders_status_note_in_the_error_colour(self):
        src = _code_only("marshal_management.gd")
        assert "const PRISONER_NOTE_ON_THE_CARD := true" in src
        body = _func_body(src, "func _render_card(")
        assert 'm.get("status_note", "")' in body
        assert "PRISONER_NOTE_ON_THE_CARD and m.get(\"captured\", false)" in body
        assert re.search(
            r'Utils\.COLOR_ERROR \+ "\]" \+ Utils\.humanize_nation_keys_in_text\(status_note\)', body
        ), body
        # At the head of the status block, before the old Location line.
        assert body.index("status_note") < body.index('bbcode += "  Location: " + location')

    def test_the_backend_card_carries_the_note_the_client_reads(self):
        """Behavioural: the key exists on a captured marshal's card."""
        import contextlib
        import io

        from backend.game_logic.marshal_overview import build_marshal_overview
        from backend.models.world_state import WorldState

        with contextlib.redirect_stdout(io.StringIO()):
            w = WorldState.from_scenario(
                str(REPO_ROOT / "godot-client" / "project-sovereign" / "assets"
                    / "maps" / "europe_1805.json"))
        ney = w.marshals.get("Ney")
        assert ney is not None
        ney.captured_by = "Austria"
        ney.captured_turn = 7
        overview = build_marshal_overview(w)
        cards = overview.get("marshals", overview) if isinstance(overview, dict) else overview
        card = next(c for c in cards if c.get("name") == "Ney")
        assert card.get("captured") is True
        assert card.get("status_note") == "PRISONER of Austria since T7."


# The only player-facing copy this row authors on the CLIENT (everything else
# is the backend's sentence, rendered verbatim). Scoped to these literals on
# purpose: main.gd still owns the LEGACY game-over screen, which the scope
# note leaves untouched.
IQ2_CLIENT_COPY = [
    ("main.gd", "France has no army in the field."),
    ("dispatch_view.gd", "France has no army in the field."),
    ("war_status_panel.gd", "Settlement (theirs to impose): "),
    ("war_detail_popup.gd", "Settlement Tier (theirs to impose): "),
]


@pytest.mark.parametrize("name,copy", IQ2_CLIENT_COPY)
def test_the_client_copy_is_present_and_never_promises_an_ending(name, copy):
    """The binding scope note: legible, never terminal."""
    assert copy in _code_only(name)
    low = copy.lower()
    for phrase in ("game over", "the campaign ends", "last chance", "defeat", "eliminated"):
        assert phrase not in low, (name, copy, phrase)
