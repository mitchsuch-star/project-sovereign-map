"""UXR-3 fixes — Pre-Deploy S12 part 2 (October 14, 2026).

S12 part 1's re-read (`docs/audits/UXR3_REREAD_2026_10_13.md`) left 28 of the
review's 73 rows open and filed five more (UXR3-74 … 78). Part 2 closes them in
the order `docs/NEXT_SESSION_PROMPT.md` decided:

  Part 1  the grip and the plate — the one R5 cause on 81 surfaces (UXR3-74),
          the tableau's nameplate (UXR3-75), the grips and ornaments off the
          content (UXR3-F4), the tableau's buttons off its filigree (F2).

Rules `SYSTEMS_REFERENCE.md` §113.7. The pins are engine-free: the source is
the subject. The driven proof of the grips is `tests/test_uxr2_grips_driven.py`
(unchanged), and the action probe's record of every grip as a `drag` control
is pinned in `tests/test_uxr3_the_review.py`'s rails class.
"""
from __future__ import annotations

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
TOOLS = REPO / "tools"


def _src(rel: str) -> str:
    return (PROJECT / rel).read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    """The body of one GDScript func (to the next top-level func)."""
    m = re.search(rf"(?ms)^(?:static )?func {re.escape(name)}\(.*?(?=^(?:static )?func |^const |\Z)", src)
    assert m, name
    return m.group(0)


def _const(src: str, name: str) -> str:
    m = re.search(rf"(?m)^const {re.escape(name)}(?:: [^=]+)? :?= (.+)$", src)
    assert m, name
    return m.group(1).strip()


GRIP = _src("scripts/resize_grip.gd")
GRIP_SIZE = float(_const(GRIP, "GRIP_SIZE"))
QUADRANT = GRIP_SIZE / 2.0
# The six centred screens that carry a grip (ResizeGrip.attach_centered).
CENTRED = ("dispatch_view", "gazette_view", "campaign_log", "marshal_management",
           "strategic_ledger", "diplomatic_ledger")


def _panel_margins(scene: str) -> dict:
    """The content margins of the scene's first StyleBox sub-resource (the
    PanelContainer's panel)."""
    text = (SCENES / f"{scene}.tscn").read_text(encoding="utf-8")
    out = {}
    for side in ("left", "top", "right", "bottom"):
        m = re.search(rf"(?m)^content_margin_{side} = ([0-9.]+)$", text)
        assert m, (scene, side)
        out[side] = float(m.group(1))
    return out


# ═══ Part 1 — the grip and the plate ══════════════════════════════════════════

class TestTheGripSaysDrag:
    """UXR3-74: the boxed four-arrow tile read as a button (R5 on 81 surfaces).
    The grip is a borderless corner hatch of three diagonal strokes in
    UI_GOLD at 0.7 alpha, and every grip says what it does."""

    def test_no_box_and_no_arrows(self):
        make = _func(GRIP, "make")
        assert 'add_theme_stylebox_override("panel", StyleBoxEmpty.new())' in make
        for gone in ("StyleBoxFlat", "arrows-out", "TextureRect", "set_border_width_all"):
            assert gone not in make, gone

    def test_three_strokes_in_gold_at_seven_tenths(self):
        steps = _const(GRIP, "HATCH_STEPS")
        assert len(re.findall(r"[0-9.]+", steps)) == 3, steps
        assert _const(GRIP, "HATCH_ALPHA") == "0.7"
        draw = _func(GRIP, "_draw")
        assert "Color(Utils.UI_GOLD, HATCH_ALPHA)" in draw
        assert "for k in HATCH_STEPS:" in draw and "draw_line(" in draw

    def test_the_hatch_lies_in_the_inner_quadrant(self):
        """The 24-px hit square stays centred on the corner (the driven test's
        `grip_gap`); every stroke lies in its inner quadrant, inside the
        panel, so what the grip DRAWS never leaves its panel's padding."""
        steps = [float(x) for x in re.findall(r"[0-9.]+", _const(GRIP, "HATCH_STEPS"))]
        inset = float(_const(GRIP, "HATCH_INSET"))
        assert inset + max(steps) <= QUADRANT, (inset, steps, QUADRANT)
        assert "position = _corner_point(_target.get_global_rect(), corner) - size * 0.5" in GRIP

    def test_every_grip_says_drag_to_resize(self):
        assert _const(GRIP, "TOOLTIP") == '"Drag to resize · double-click to restore"'
        assert GRIP.count("make(Corner.BOTTOM_RIGHT,\n\t\t\tTOOLTIP)") + GRIP.count("make(grip_corner,\n\t\t\tTOOLTIP)") == 2
        main = _src("scripts/main.gd")
        assert "ResizeGrip.make(ResizeGrip.Corner.TOP_RIGHT, ResizeGrip.TOOLTIP)" in main
        for path in SCRIPTS.glob("*.gd"):
            if path.name == "resize_grip.gd":
                continue
            assert "Drag to resize" not in path.read_text(encoding="utf-8"), path.name

    def test_the_command_windows_grip_reads_the_event_not_the_os_cursor(self):
        """The shared grip's rule (the event's own position): the probe's
        pushed drag never moves the OS cursor, and neither does a player's
        drag through a scaled canvas need it."""
        body = _func(_src("scripts/main.gd"), "_on_grip_gui_input")
        assert "get_global_mouse_position" not in body
        assert body.count("event.global_position") == 2


class TestTheGripSitsOffTheContent:
    """UXR3-F4: no grip or corner ornament on text or a control. The census on
    the closing re-read's frame records holds the rects; these hold the
    geometry that makes it so."""

    def test_every_centred_screen_pads_the_corner_the_grip_draws_in(self):
        for scene in CENTRED:
            m = _panel_margins(scene)
            assert m["right"] >= QUADRANT and m["bottom"] >= QUADRANT, (scene, m)

    def test_the_war_hud_pads_its_top_left_corner(self):
        m = _panel_margins("war_status_panel")
        assert m["top"] >= QUADRANT, m
        ws = _src("scripts/war_status_panel.gd")
        # the shrink-wrap covers the new top margin (12 + 4 + slack)
        assert "vbox.get_combined_minimum_size().y + 18.0" in ws
        assert 'ResizeGrip.attach_edge(panel_container, "war_status", ResizeGrip.Corner.TOP_LEFT)' in ws

    def test_the_generals_filigree_sits_in_the_bottom_band(self):
        """Each corner ornament lies below the content box (it covered the
        last skill bar), and the right one clear of the grip's quadrant."""
        text = (SCENES / "marshal_management.tscn").read_text(encoding="utf-8")
        m = _panel_margins("marshal_management")
        for name in ("FiligreeBottomLeft", "FiligreeBottomRight"):
            block = re.search(rf'(?ms)^\[node name="{name}".*?(?=^\[|\Z)', text).group(0)
            assert 'groups=["corner_ornaments"]' in block, name
            top = float(re.search(r"offset_top = (-?[0-9.]+)", block).group(1))
            bottom = float(re.search(r"offset_bottom = (-?[0-9.]+)", block).group(1))
            assert top >= 0.0 and bottom <= m["bottom"], (name, top, bottom)
            if name.endswith("Right"):
                right = float(re.search(r"offset_right = (-?[0-9.]+)", block).group(1))
                assert right <= m["right"] - QUADRANT, (right, m)

    def test_the_capture_harness_records_the_grips_and_ornaments(self):
        gd = (TOOLS / "iq10_surface_screenshot.gd").read_text(encoding="utf-8")
        assert 'frame["grips"] = _grips_and_ornaments()' in gd
        body = _func(gd, "_grips_and_ornaments")
        assert "n is ResizeGrip" in body and 'is_in_group("corner_ornaments")' in body


class TestThePlateIsAnEngravedLabel:
    """UXR3-75: the gold-filled, bordered nameplate stood in the button row
    and read as the main button. It is a flat engraved label: no fill, no
    border, no hover; the same words in the same place."""

    def test_no_fill_and_no_border(self):
        body = _func(_src("scripts/battle_diorama.gd"), "_build_verdict_and_plate")
        plate = body[body.index("_nameplate = PanelContainer.new()"):body.index("var plate_box")]
        assert "StyleBoxEmpty.new()" in plate and "StyleBoxFlat" not in plate
        assert "bg_color" not in plate and "border" not in plate.replace("no border", "")
        assert "_nameplate.mouse_filter = Control.MOUSE_FILTER_IGNORE" in plate
        # the margins keep its size, so it keeps its place
        for side in ("left", "right"):
            assert f"engraved.content_margin_{side} = 26.0" in plate
        for side in ("top", "bottom"):
            assert f"engraved.content_margin_{side} = 5.0" in plate

    def test_the_words_read_on_the_walnut(self):
        """Brass text on WOOD_BG: the name 6.0 : 1, the sub-line 4.6 : 1."""
        src = _src("scripts/battle_diorama.gd")

        def lum(rgb):
            def lin(c):
                return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
            r, g, b = (lin(float(x)) for x in rgb)
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        def rgb(name):
            return re.findall(r"[0-9.]+", _const(src, name))[:3]

        wood = lum(rgb("WOOD_BG"))
        for name, floor in (("BRASS", 4.5), ("PLATE_SUB", 3.0)):
            ratio = (lum(rgb(name)) + 0.05) / (wood + 0.05)
            assert ratio >= floor, (name, ratio)
        body = _func(src, "_build_verdict_and_plate")
        assert '_plate_name.add_theme_color_override("font_color", BRASS)' in body
        assert '_plate_sub.add_theme_color_override("font_color", PLATE_SUB)' in body


class TestTheTableausButtonsClearItsFiligree:
    """UXR3-F2's third clause: Close sat on the bottom-right corner ornament."""

    def test_close_ends_left_of_the_corner_ornament(self):
        src = _src("scripts/battle_diorama.gd")
        tray_w = float(_const(src, "TRAY_W"))
        m = re.search(r"_btn_close\.position = Vector2\(TRAY_W - ([0-9.]+), ", src)
        close_left = tray_w - float(m.group(1))
        close_w = float(re.search(r"_btn_close\.custom_minimum_size = Vector2\(([0-9.]+),", src).group(1))
        fil = _func(src, "_build_filigree")
        assert "TRAY_W - 38.0" in fil and 'fil.add_to_group("corner_ornaments")' in fil
        assert close_left + close_w <= tray_w - 38.0, (close_left, close_w)


# ═══ Parts 2 and 3 — R6's driven proofs; the never-pressed controls ══════════

class TestAChipUnderAScreenAnswersInPlace:
    """UXR3-27, 40, 45: an order chip on the Generals or either ledger hands
    its order to main.gd, whose terminal echo lies under the screen. The chip
    greys in place to 'Sent: <its words>' — only when main.gd's chip road took
    the order (its in-flight latch can refuse a second press)."""

    def test_the_handshake_in_every_screen(self):
        for rel, signal, meta_var in (("scripts/marshal_management.gd", "order_command.emit(", "meta_str"),
                                      ("scripts/diplomatic_ledger.gd", "vassal_command.emit(command)", "meta_key"),
                                      ("scripts/strategic_ledger.gd", "naval_command.emit(command)", "meta_str")):
            src = _src(rel)
            i = src.index(signal)
            before, after = src[i - 220:i], src[i:i + 220]
            assert "Utils.order_taken = false" in before, rel
            assert f"if Utils.order_taken:\n" in after and f"Utils.mark_chip_sent(content_area, {meta_var})" in after, rel

    def test_main_says_it_took_the_order_after_its_latch(self):
        main = _src("scripts/main.gd")
        for fn in ("_on_reward_command", "_on_vassal_command", "_on_naval_command"):
            body = _func(main, fn)
            latch = body.index("_chip_command_in_flight = true")
            taken = body.index("Utils.order_taken = true")
            assert body.index("if command.is_empty() or _chip_command_in_flight:") < latch < taken, fn

    def test_cancel_greys_when_the_request_is_out(self):
        body = _func(_src("scripts/strategic_ledger.gd"), "_on_meta_clicked")
        i = body.index("_api_client_ref.cancel_strategic_order(marshal_name, _on_cancel_result)")
        assert 'Utils.mark_chip_sent(content_area, meta_str, "Cancel")' in body[i:i + 300]

    def test_the_sent_chip_is_the_disabled_chip_written_through_text(self):
        body = _func(_src("scripts/utils.gd"), "mark_chip_sent")
        assert 'bb_chip_disabled("Sent: " + words)' in body
        assert '"Sent: " + words' in body and "COLOR_INFO" in body
        assert "rtl.text = " in body and "append_text" not in body


class TestTheWarRoomMode:
    """The probe's war-room mode: each hand-off surface opened INSIDE the real
    main.tscn against a sandboxed live backend, the road's control pressed,
    the answer read in the live frame. Its record and the citations it backs
    are the closing re-read's (`docs/audits/uxr3_s12b/`)."""

    def test_the_rails(self):
        gd = (TOOLS / "uxr3_action_probe.gd").read_text(encoding="utf-8")
        assert 'if _war_room and Utils.backend_url().ends_with(":8005"):' in gd
        runner = (TOOLS / "uxr3_action_probe.py").read_text(encoding="utf-8")
        assert "while port == 8005 or not _free(port):" in runner
        assert '"INK_IRON_SAVE_DIR": str(saves)' in runner and '"LLM_MODE": "mock"' in runner
        assert 'assert env["SOVEREIGN_PORT"] != "8005", "never the player\'s 8005"' in runner

    def test_the_roads_cover_every_r6_cross_part_one_left(self):
        """Each road names an IQ-10 shot and a control match; together they
        hold every HANDOFF and NOT PRESSED road part 1's re-read left unproven
        (the HUD pieces shot alone are read in their host, §113.5)."""
        import sys
        sys.path.insert(0, str(TOOLS))
        import iq10_run_captures as R
        import uxr3_action_probe as PROBE
        shots = {s["id"] for s in R.SHOTS}
        ids = [r[0] for r in PROBE.ROADS]
        assert len(ids) == len(set(ids))
        for road, sid, match in PROBE.ROADS:
            assert sid in shots, road
            assert set(match) <= {"kind", "text", "meta_startswith", "path_endswith"}, road
        metas = {m.get("meta_startswith") for _r, _s, m in PROBE.ROADS}
        for need in ("order:", "reward:", "talleyrand_assess", "vassal:", "congress_court:", "do:",
                     "cancel:", "negotiate:", "diorama:"):
            assert need in metas, need
        texts = {m.get("text") for _r, _s, m in PROBE.ROADS}
        for need in ("Save Game", "Load Game", "New Campaign", "Main Menu", "Quit to Desktop"):
            assert need in texts, need

    def test_a_war_room_answer_is_read_in_the_live_frame_only(self):
        gd = (TOOLS / "uxr3_action_probe.gd").read_text(encoding="utf-8")
        assert "changed = _live_only(changed, [before, a2, a3])" in gd
        live = _func(gd, "_live_only")
        assert "floor_now = mini(floor_now" in live
        assert "int(layers.get(key.substr(2), 0)) >= floor_now" in live
        assert 'out.append(scene)    # a scene change leads: it is the answer' in _func(gd, "_describe")


# ═══ Part 4 — the boards: a live subject leads its first screenful ══════════

SCENARIO_1805 = PROJECT / "assets" / "maps" / "europe_1805.json"


@pytest.fixture
def world_1805():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO_1805))


def _order(src: str, *needles: str) -> bool:
    """True when every needle is in `src`, in the order given."""
    at = -1
    for n in needles:
        i = src.find(n, at + 1)
        if i < 0:
            return False
        at = i
    return True


def _sovereign(w):
    return next(m for m in w.marshals.values()
                if getattr(m, "is_sovereign", False) and m.nation == w.player_nation)


class TestTheBoardsLeadWithTheirSubject:
    def test_the_region_panel_leads_with_its_actions(self):
        """UXR3-76: ACTIONS spliced in under the title line; the name at Lead."""
        body = _func(_src("scripts/region_panel.gd"), "_render")
        assert "var actions_at := bbcode.length()" in body
        assert "bbcode = bbcode.substr(0, actions_at) + actions" in body
        assert _order(body, "var actions_at := bbcode.length()", "FORCES PRESENT", "THE SEA")
        scene = (SCENES / "region_panel.tscn").read_text(encoding="utf-8")
        title = scene[scene.index('[node name="TitleLabel"'):].split("[node", 2)[1]
        assert 'theme_type_variation = &"Lead"' in title

    def test_the_strategic_ledger_leads_with_the_cabinet_and_the_ceiling(self):
        """UXR3-41: a running mission's Cabinet leads Forces (an idle one says
        so in a line), the Emperor's corps leads the muster, the ceiling leads
        Economy; the arm reads as a word, not "[INF]" (UXR3-F6)."""
        src = _src("scripts/strategic_ledger.gd")
        forces = _func(src, "_render_forces")
        assert _order(forces, "_cabinet_block(forces_cabinet)", "Authority:", "for f in muster:")
        assert "muster.push_front(f)" in forces and "THE EMPEROR — " in forces
        assert "type_tag" not in forces and "unit_type.capitalize()" in forces
        assert 'f.get("seat_dp", 0)' in forces
        economy = _func(src, "_render_economy")
        assert _order(economy, '"  Treasury: "', "_ceiling_line(econ, treasury)", '"  Income:   +"')
        assert 'bbcode += _cabinet_block(cached_data.get("cabinet"))' in _func(src, "_render_orders")

    def test_the_ledger_names_the_sovereign_and_his_seat(self, world_1805):
        from backend.game_logic.ledger import _build_forces
        w = world_1805
        nap = _sovereign(w)
        nap.location = w.get_nation_capital(w.player_nation)
        rows = {r["name"]: r for r in _build_forces(w, w.player_nation)}
        assert rows[nap.name]["sovereign"] is True and rows[nap.name]["seat_dp"] == 1
        assert all(r["sovereign"] is False and r["seat_dp"] == 0
                   for n, r in rows.items() if n != nap.name)

    def test_the_generals_lead_with_what_asks_for_attention(self):
        """UXR3-24: a prisoner or a marshal seeking an audience first (his
        state in his header), then OUR DOCTRINE, then THE EMPEROR — whose
        card opens on his state, The Presence and his strength — then THE
        LAURELS (one line when no glory was won) and the roster."""
        src = _src("scripts/marshal_management.gd")
        body = _func(src, "_render_all_cards")
        assert _order(body, "urgent.append(i)", '"A PRISONER"', "_render_doctrine()",
                      "]THE EMPEROR[/color]", "_render_glory_ladder()")
        card = _func(src, "_render_card")
        assert _order(card, 'm.get("sovereign_state_line", "")', "_ability_line(m)",
                      "_strength_line(m)", "BIOGRAPHY")
        assert "no glory won in the last" in _func(src, "_render_glory_ladder")

    def test_the_emperors_state_line_names_field_seat_and_cell(self, world_1805):
        from backend.game_logic.marshal_overview import _sovereign_state_line
        w = world_1805
        nap = _sovereign(w)
        capital = w.get_nation_capital(w.player_nation)
        nap.location = capital
        line = _sovereign_state_line(w, nap)
        assert line.startswith("At the Seat — he holds court at ") and "+1 DP a turn" in line
        nap.location = next(r for r in w.regions if r != capital)
        assert _sovereign_state_line(w, nap).startswith("In the field at " + nap.location)
        nap.captured_by, nap.captured_turn = "Austria", 3
        assert _sovereign_state_line(w, nap).startswith("A captive — PRISONER of ")

    def test_the_peace_popups_lead_with_their_terms(self):
        """UXR3-30 / 31: the terms under "Terms:" before the War Summary; the
        confirm snapshot's terms and acceptance before it; the settlement's
        per-court rows lead and Talleyrand's paragraph opens the footer, the
        Press / Ease / Drop rows under the table (above Allies)."""
        inc = _func(_src("scripts/incoming_proposal_popup.gd"), "_build_peace_preview_section")
        assert _order(inc, "_build_annotated_terms_section(annotated)", "Assessment:", "[b]War Summary[/b]")
        assert "Proposed Terms" not in inc
        conf_src = _src("scripts/proposal_confirm_popup.gd")
        conf = _func(conf_src, "_build_peace_preview_content")
        assert _order(conf, "[b]Proposed Terms[/b]", "[b]Acceptance Estimate[/b]", "[b]War Summary[/b]")
        assert 'data.get("talleyrand_text"' not in _func(conf_src, "_build_settlement_content")
        assert 'data.get("talleyrand_text"' in _func(conf_src, "_build_settlement_footer")
        scene = (SCENES / "proposal_confirm_popup.tscn").read_text(encoding="utf-8")
        assert _order(scene, '[node name="PerCourtScroll"', '[node name="Tier2Scroll"',
                      '[node name="FooterLabel"')

    def test_the_wizard_folds_the_congress_and_leads_with_a_live_design(self):
        """UXR3-28 / 78: one line for the Congress (its terms behind a toggle,
        [Summon] and [View the table] on one row, the live Summon the primary
        action — UXR3-F5); a court's live design leads step 2 with its
        instruments."""
        src = _src("scripts/diplomacy_wizard.gd")
        row = _func(src, "_add_congress_row")
        assert "the terms" in row and "if _congress_terms_open:" in row
        assert "var row := HBoxContainer.new()" in row and "row.add_child(view)" in row
        assert 'btn.add_theme_stylebox_override("normal", primary)' in row
        assert 'const INSTRUMENT_ACTIONS := ["sponsor_design", "buy_off_design", "guarantee_nation"]' in src
        assert "actions = lead + rest" in src

    def test_the_diplomatic_ledger_leads_with_laws_doctrine_and_the_spent_league(self):
        """UXR3-29 / 77: a court's Laws and Doctrine lines under its name; the
        spent league's counsel first in Talleyrand's book; the Cabinet named
        in the header of every book."""
        src = _src("scripts/diplomatic_ledger.gd")
        nations = _func(src, "_render_nations")
        assert _order(nations, "Vassalizable", '"  Laws: [color=#"', '"  Doctrine: [color=#"', '"  Diplomat: "')
        tal = _func(src, "_render_talleyrand")
        assert _order(tal, '"COOLDOWN"', "THE LEAGUE IS SPENT", "_cooldown_counsel(boe_t)", "TALLEYRAND[/color] — ")
        assert "_set_cabinet_line(talleyrand_data)" in _func(src, "_on_ledger_received")
        assert 'var words := "Talleyrand: Idle"' in _func(src, "_set_cabinet_line")

    def test_the_rail_names_the_mission_and_its_recall_fills_the_line(self):
        """UXR3-1 / 18: "Talleyrand at <court> — <kind>" beside the book, a
        Recall chip that FILLS the backend's own order (never sends); UXR3-F10:
        the "+N" badge opens the queued notices."""
        src = _src("scripts/notification_bar.gd")
        row = _func(src, "_create_mission_row")
        assert "btn.text = _mission_words(notif)" in row and 'chip.text = "Recall"' in row
        assert "suggest_command.emit(recall)" in row and "notification_action_requested" not in row
        assert "overflow_label.pressed.connect(_on_overflow_pressed)" in _func(src, "_ready")
        main = _src("scripts/main.gd")
        assert "notification_bar.suggest_command.connect(_on_tutorial_suggest_command)" in main
        scene = (SCENES / "notification_bar.tscn").read_text(encoding="utf-8")
        assert '[node name="OverflowLabel" type="Button"' in scene

    def test_the_top_bars_cabinet_is_a_chip_that_opens_talleyrands_book(self):
        src = _src("scripts/top_bar.gd")
        assert "@onready var talleyrand_label: Button =" in src
        assert "talleyrand_label.pressed.connect(open_cabinet)" in src
        assert 'open_diplomatic_ledger_review("ledger_talleyrand")' in _func(src, "open_cabinet")
        assert 'talleyrand_label.add_theme_stylebox_override("normal", _mailbox_idle_style)' in src
        scene = (SCENES / "top_bar.tscn").read_text(encoding="utf-8")
        assert '[node name="TalleyrandLabel" type="Button"' in scene

    def test_the_tutor_card_opens_wide_and_reads_large(self):
        src = _src("scripts/tutorial_overlay.gd")
        assert "const CARD_WIDTH_FRACTION := 0.40" in src and "const CARD_MIN_WIDTH := 520.0" in src
        scene = (SCENES / "tutorial_overlay.tscn").read_text(encoding="utf-8")
        body = scene[scene.index('[node name="BodyText"'):].split("[node", 2)[1]
        assert 'theme_type_variation = &"BodyLargeRich"' in body

    def test_a_sitting_congress_leads_the_dispatch(self):
        body = _func(_src("scripts/dispatch_view.gd"), "_on_dispatch_received")
        assert 'congress_sits = str(congress_clock.get("phase", "")) == "sitting"' in body
        assert _order(body, "var congress_at := bbcode.length()", "W6-3 HEADLINE",
                      "bbcode = bbcode.substr(0, congress_at) + congress_block")

    def test_the_secondary_boards_are_read_at_their_subject(self):
        import sys
        sys.path.insert(0, str(TOOLS))
        import iq10_run_captures as R
        shots = {s["id"]: s for s in R.SHOTS}
        assert shots["gazette_congress"]["steps"][0] == {
            "scroll_to": {"text": "THE CONGRESS OF PARIS"}, "then_wait": 4}
        toggle = {"call": "_toggle_congress_terms", "args": []}
        for tag in ("gate", "ready"):
            assert toggle in shots[f"wizard_step1_congress_{tag}"]["steps"]
        assert toggle not in shots["wizard_step1_congress_sitting"]["steps"]


# ═══ Part 5 — the rows found while reading and fixing ═══════════════════════

class TestTheFoundRows:
    def test_f1_the_score_stands_clear_of_the_centre_tick(self):
        """UXR3-F1: −60 read "60" — the tick drew over the minus of a centred
        label. The label stands on the leader's side, SCORE_TICK_CLEAR from
        the tick, and a losing score carries a true minus."""
        src = _src("scripts/war_detail_popup.gd")
        bar = _func(src, "_create_tug_of_war_bar")
        assert "PRESET_FULL_RECT)\n\tcontainer.add_child(score_label)" not in bar
        assert "_anchor_bar_child(score_label, 0.0, 0.5, WAR_BAR_TAG_INSET + WAR_BAR_TAG_W, -SCORE_TICK_CLEAR)" in bar
        assert "_anchor_bar_child(score_label, 0.5, 1.0, SCORE_TICK_CLEAR, -(WAR_BAR_TAG_INSET + WAR_BAR_TAG_W))" in bar
        assert '"\\u2212" if score < 0' in bar and "str(absi(score))" in bar
        clear = float(_const(src, "SCORE_TICK_CLEAR"))
        assert clear > 1.0   # the tick spans the centre ±1 px
        assert 'tick.add_to_group("bar_ticks")' in bar
        gd = (TOOLS / "iq10_surface_screenshot.gd").read_text(encoding="utf-8")
        assert 'n.is_in_group("bar_ticks")' in gd and 'kind = "tick"' in gd

    def test_f2_a_deeper_ranks_standard_flies_below_the_forward_ranks_words(self):
        src = _src("scripts/battle_diorama.gd")
        assert _const(src, "STANDARD_POLE") == "86.0"
        layout = src[src.index("var block_scale := 1.0 - 0.12 * i"):]
        layout = layout[:layout.index("blocks.append(")]
        assert "if n >= 2 and i > 0:" in layout    # part 5d: two ranks too
        assert "156.0 * fwd_scale - (TEXT_PITCH + 19.0) - 4.0 - step_y" in layout
        std = _func(src, "_make_standard")
        assert "-86" not in std and "Vector2(0, -pole_h)" in std
        assert float(_const(src, "FAITH_CAPTION_W")) == 230.0

    def test_f5_one_close_control_and_one_chip_style(self):
        for rel in ("scripts/campaign_log.gd", "scripts/diplomacy_wizard.gd"):
            assert 'Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")' in _src(rel), rel
        pause = _src("scripts/pause_menu.gd")
        assert 'resume.text = "Resume (Esc)"' in pause and "resume.pressed.connect(close_menu)" in pause
        popup = _src("scripts/proposal_confirm_popup.gd")
        assert "_close_x.visible = exit_action != \"\"" in popup
        assert "_on_option_selected(exit_action)" in popup
        tut = (SCENES / "tutorial_overlay.tscn").read_text(encoding="utf-8")
        for name in ("MinimizeButton", "SkipButton"):
            block = tut[tut.index(f'[node name="{name}"'):].split("[node", 2)[1]
            assert "flat = true" not in block, name
        orders = _func(_src("scripts/strategic_ledger.gd"), "_render_orders")
        assert '[Cancel]' not in orders
        assert 'Utils.bb_button_chip("cancel:" + mname, "Cancel"' in orders

    def test_f6_the_games_words_not_tags(self):
        dl = _src("scripts/diplomatic_ledger.gd")
        assert '" / 100  [" + tier_shown + "]' not in dl and '" / 100 — " + tier_shown' in dl
        assert "█" not in dl and "░" not in dl
        assert "Utils.bb_bar_img(" in dl
        ep = _src("scripts/enemy_phase_dialog.gd")
        assert '"-".repeat(40)' not in ep and '"─".repeat(28)' in ep
        log = _src("scripts/campaign_log.gd")
        assert 'var affordance = "▾" if expanded_turns.get(turn_num, false) else "▸"' in log

    def test_the_top_bars_alarm_reads_in_the_games_words(self):
        """F6's class, found on the closing re-read's frames (part 5d): the
        alarm was a bracketed "[THREAT]" / "[THREAT!]"."""
        tb = _src("scripts/top_bar.gd")
        assert 'threat_label.text = "[THREAT' not in tb
        fields = _func(tb, "update_diplomatic_fields")
        assert fields.count("threat_label.text = _threat_words(threat)") == 2
        assert fields.count("threat_label.tooltip_text = THREAT_TOOLTIP") == 2
        assert 'return "Threat %d / 100" % threat' in _func(tb, "_threat_words")

    def test_f7_the_family_chrome_and_a_gear_that_reads(self):
        gear = (PROJECT / "assets" / "ui" / "icons" / "phosphor" / "gear.svg").read_text(encoding="utf-8")
        assert "currentColor" not in gear
        for scene in ("marshal_petition_dialog", "mailbox_panel"):
            text = (SCENES / f"{scene}.tscn").read_text(encoding="utf-8")
            assert "border_color = Color(0.85, 0.75, 0.55, 0.6)" in text, scene
            assert "bg_color = Color(0.1, 0.1, 0.18, 0.95)" in text, scene

    def test_f7_the_white_peace_review_fits_its_regions(self):
        """UXR3-F7's last item (part 5b): the white peace's review stood on the
        1160 x 980 document ceiling with three short regions sharing the spare
        height — two empty bands. When the regions need less than the ceiling
        the panel shrinks to them, each region at its own content's height;
        when they need more, the equal shares (IGR-G1) stand."""
        popup = _src("scripts/proposal_confirm_popup.gd")
        opened = popup[popup.index('$PanelContainer.set_meta("clamp_ceiling_override", SETTLEMENT_CEILING)'):]
        assert _order(opened, "_reset_document_shares()", "Utils.clamp_centered_panel($PanelContainer)",
                      "_fit_settlement_document()")
        fit = _func(popup, "_fit_settlement_document")
        assert "if need_panel >= have:\n\t\treturn" in fit
        assert "regions[i].size_flags_stretch_ratio = maxf(float(shares[i]), 1.0)" in fit
        assert "panel.offset_top = -need_panel / 2.0" in fit
        # a re-render inside the table re-fits from the full rect
        assert popup.count("_refit_settlement_document()") >= 3
        refit = _func(popup, "_refit_settlement_document")
        assert _order(refit, "_reset_document_shares()", "Utils.clamp_centered_panel($PanelContainer)",
                      "_fit_settlement_document()")

    def test_f8_the_fall_clock_is_printed_once_by_one_road(self):
        utils = _func(_src("scripts/utils.gd"), "fall_clock_rows")
        assert "message.contains(title)" in utils
        main = _func(_src("scripts/main.gd"), "_add_fall_clock_lines")
        assert "Utils.fall_clock_rows(warning)" in main and 'arm.get("clock_line"' not in main
        disp = _func(_src("scripts/dispatch_view.gd"), "_on_dispatch_received")
        assert "Utils.fall_clock_rows(defeat_imminent_warning)" in disp
        assert 'arm.get("clock_line"' not in disp

    def test_f9_the_boards_carry_their_subject_and_never_print_unknown(self):
        ep = _src("scripts/enemy_phase_dialog.gd")
        assert '"acts":' in ep and 'if action_type == "unknown":' in ep
        cap = (TOOLS / "iq10_capture_payloads.py").read_text(encoding="utf-8")
        assert 'res["ai_action"] = {"marshal": "Moore", "action": "attack", "target": "Ney"}' in cap
        assert 'record("mailbox_boot", box,' in cap and '"mailbox_boot", get(c, "/mailbox")' not in cap
        region = _func(_src("scripts/region_panel.gd"), "_render")
        assert _order(region, "No intelligence", '"Income: [color=#"', "Supply: [color=#")
        tb = _src("scripts/top_bar.gd")
        assert '_blockade_style()' in _func(tb, "update_admiralty")
        assert "sb.border_color = Utils.UI_ALERT" in _func(tb, "_blockade_style")

    def test_f3_the_log_follows_onto_a_whole_line_and_the_harness_measures_cuts(self):
        main = _src("scripts/main.gd")
        snap = _func(main, "_snap_output_to_a_whole_line")
        assert "output_display.get_line_offset(i)" in snap and "content_margin_bottom = pad" in snap
        assert "_snap_output_to_a_whole_line()" in _func(main, "add_output")
        gd = (TOOLS / "iq10_surface_screenshot.gd").read_text(encoding="utf-8")
        assert 'frame["cut_lines"] = _cut_lines()' in gd
        cut = _func(gd, "_cut_lines")
        # both kinds of clip, and a ScrollContainer's window is its whole rect
        assert 'kind = "scroll"' in cut and 'kind = "own"' in cut
        assert "win_top = s_rect.position.y" in cut and "win_bottom = s_rect.end.y" in cut

    def test_f3_every_reading_scroll_rests_on_whole_lines(self):
        """UXR3-F3 (parts 5b and 5c): every reading scroll comes to rest on
        whole lines — a self-scrolling label's own lines, or for a
        ScrollContainer every line of every label in it and every other control
        as one whole box (borders and all). The top snaps onto a line's start
        the way it was moving; the bottom is padded inside a self-scrolling
        label, or by a spacer beside a ScrollContainer sized by the share of it
        the scroll was measured to give up (a container's panel margin does not
        clip its child), or from a floored scroll's own floor."""
        utils = _src("scripts/utils.gd")
        keep = _func(utils, "keep_whole_lines")
        assert 'spacer.name = "WholeLinePad"' in keep and "sc.add_sibling(spacer)" in keep
        assert 'rtl.add_theme_stylebox_override("normal", box)' in keep
        for signal in ("bar.value_changed.connect", "host.resized.connect", "rtl.finished.connect",
                       "sc.sort_children.connect"):
            assert signal in keep, signal
        boxes = _func(utils, "_whole_line_boxes")
        assert "_rtl_lines(n as RichTextLabel" in boxes
        assert "g.position.y - origin - WHOLE_LINE_EDGE - 1.0" in boxes   # a control is whole with its borders
        snap = _func(utils, "snap_whole_lines")
        assert "to = b.y if v > last_v else b.x" in snap
        assert "if to > top_max + 0.5:\n\t\t\t\tto = b.x" in snap
        assert "ceilf(bottom - cut_at) + 1.0" in snap
        assert 'var floor_y: float = maxf(float(rec["floor0"]) - pad, 0.0)' in snap
        assert 'var want: float = ceilf(pad / maxf(float(rec["share"]), 0.2))' in snap
        settled = _func(utils, "_scroll_window_settled")
        assert 'rec["share"] = clampf((float(rec["h0"]) - sc.size.y) / spacer.custom_minimum_size.y, 0.2, 1.0)' \
            in settled
        for rel, var in (("scripts/dispatch_view.gd", "content_label"), ("scripts/gazette_view.gd", "content_label"),
                         ("scripts/campaign_end.gd", "content_label"), ("scripts/diplomacy_wizard.gd", "assessment_panel"),
                         ("scripts/diplomacy_wizard.gd", "scroll_container"),
                         ("scripts/diplomatic_ledger.gd", "content_area"), ("scripts/strategic_ledger.gd", "content_area"),
                         ("scripts/marshal_management.gd", "scroll_container"),
                         ("scripts/war_detail_popup.gd", "content_label"),
                         ("scripts/incoming_proposal_popup.gd", "content_label"),
                         ("scripts/enemy_phase_dialog.gd", "content_label"),
                         ("scripts/campaign_log.gd", "scroll_container")):
            assert f"Utils.keep_whole_lines({var})" in _func(_src(rel), "_ready"), (rel, var)
        assert "for region in [content_label, per_court_table, footer_label]:\n\t\tUtils.keep_whole_lines(region)" in \
            _func(_src("scripts/proposal_confirm_popup.gd"), "_ready")
        # the war-room log keeps its own snap: it follows the newest line
        assert "keep_whole_lines(output_display)" not in _src("scripts/main.gd")
