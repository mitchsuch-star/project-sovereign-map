"""IQ-10 "The Client Pass" — the gates (September 19, 2026).

The row's instrument is three committed tools: `tools/iq10_capture_payloads.py`
(payloads off STAGED boards, in-process), `tools/iq10_surface_screenshot.gd`
(one generic offscreen capture, windowed and parked off the desktop) and
`tools/iq10_run_captures.py` (the surface table, the launch, the index). The
frames themselves cannot be pinned here — a PNG needs the engine — so these
pins hold the things that made the pass FIND something, and the four defects it
fixed, at the seam each lives on.

Memo of record: docs/audits/IQ10_CLIENT_PASS_2026_09_19.md.
"""
import ast
import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
TOOLS = REPO / "tools"
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
AUDITS = REPO / "docs" / "audits"


def _gd(name: str) -> str:
    return (SCRIPTS / f"{name}.gd").read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════
# The instrument
# ═══════════════════════════════════════════════════════════════════════

class TestTheHarnessIsCommitted:
    """Three files and the two-command road; a future session re-shoots a
    surface without re-deriving any of this."""

    def test_the_three_tools_exist_and_name_each_other(self):
        for name in ("iq10_capture_payloads.py", "iq10_run_captures.py",
                     "iq10_surface_screenshot.gd"):
            assert (TOOLS / name).exists(), name
        runner = (TOOLS / "iq10_run_captures.py").read_text(encoding="utf-8")
        assert "iq10_capture_payloads.py" in runner
        assert "iq10_surface_screenshot.gd" in runner

    def test_the_capture_harness_is_in_the_parse_check_list(self):
        """Every tool `.gd` must be parsed by the committed harness, or a
        syntax error in it is invisible until someone runs it."""
        check = (TOOLS / "godot_parse_check.gd").read_text(encoding="utf-8")
        assert "iq10_surface_screenshot.gd" in check

    def test_the_window_is_parked_off_the_players_desktop(self):
        """The capture needs a REAL window (a headless viewport returns no
        image), so it is positioned past the primary monitor and runs on the
        Dummy audio driver. Never on top of what the player is doing."""
        runner = (TOOLS / "iq10_run_captures.py").read_text(encoding="utf-8")
        assert "WINDOW_POSITION = [2565, 20]" in runner
        assert '"--audio-driver", "Dummy"' in runner

    def test_the_harness_never_writes_the_players_settings(self):
        """UiSettings' setters `save()` to the real user://ui_settings.cfg.
        The harness shims an in-memory ConfigFile and calls no setter."""
        gd = (TOOLS / "iq10_surface_screenshot.gd").read_text(encoding="utf-8")
        assert "UiSettings._cfg = ConfigFile.new()" in gd
        assert not re.search(r"UiSettings\.set_\w+\(", gd)

    def test_every_shot_names_what_the_frame_must_show(self):
        """A screenshot nobody can judge is not evidence. Each row carries the
        sentence its frame is read against, and the runner carries it into the
        index beside the payload's own measured facts."""
        src = (TOOLS / "iq10_run_captures.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        shots = None
        for node in tree.body:
            target = (node.target if isinstance(node, ast.AnnAssign)
                      else (node.targets[0] if isinstance(node, ast.Assign) and node.targets else None))
            if getattr(target, "id", "") == "SHOTS":
                shots = node
        assert shots is not None, "SHOTS table is gone"
        keys = [k.value for d in ast.walk(shots) if isinstance(d, ast.Dict)
                for k in d.keys if isinstance(k, ast.Constant)]
        assert keys.count("must_show") >= 20
        assert keys.count("must_show") == keys.count("surface")

    def test_the_index_carries_the_payloads_own_facts(self):
        runner = (TOOLS / "iq10_run_captures.py").read_text(encoding="utf-8")
        assert '"facts": cap.get("facts", {})' in runner
        assert '"staging": cap["staging"]' in runner


# ═══════════════════════════════════════════════════════════════════════
# IQ10-1 / IQ10-2 — the Generals card (backend)
# ═══════════════════════════════════════════════════════════════════════

class TestTheCaptiveProjectsNothing:
    """IQ10-1. Measured on the Aug-16 `np_visual_captive` save (Napoleon taken
    at T11, held at Vienna, strength 0): the card advertised "The Presence —
    Every French corps fighting in the Emperor's province gains +10% attack and
    defense. Enemy commanders will not attack his army..." for a man in a cell.
    Every combat seam reads a STANDING marshal (NP-4), so the card was the one
    surface saying otherwise."""

    def _card(self, captured: bool):
        from backend.game_logic import marshal_overview as MO
        from backend.models.marshal import Marshal
        from backend.models.personality import Personality
        m = Marshal(name="Ney", personality=Personality.AGGRESSIVE, nation="France",
                    location="Paris", strength=20000)
        m.ability = {"name": "The Bravest of the Brave", "description": "d",
                     "trigger": "t", "effect": "+15% attack"}
        m.captured_by = "Austria" if captured else ""
        return MO._build_ability(m)

    def test_a_standing_marshal_keeps_his_ability(self):
        card = self._card(captured=False)
        assert card["ability_active"] is True
        assert card["ability_effect"] == "+15% attack"

    def test_a_captive_advertises_no_effect(self):
        card = self._card(captured=True)
        assert card["ability_active"] is False
        assert card["ability_effect"] == ""
        assert card["ability_name"] == "The Bravest of the Brave"   # still named
        assert "prisoner" in card.get("ability_dormant_note", "").lower()

    def test_the_lever_restores_the_pre_pass_card(self, monkeypatch):
        from backend.game_logic import marshal_overview as MO
        monkeypatch.setattr(MO, "CAPTIVITY_SUSPENDS_THE_ABILITY", False)
        card = self._card(captured=True)
        assert card["ability_active"] is True and card["ability_effect"] == "+15% attack"


class TestThePrisonerNoteTakesTheArticle:
    """IQ10-2 (R7). "PRISONER of Kingdom of Italy since T1." — measured on the
    IQ-10 prisoner board. The IQ-7 review round made every vassal sentence take
    its article; this is the same rule one surface over. Switzerland and Austria
    take none, which is why only a the-court board can see it."""

    def _note(self, captor: str):
        from backend.game_logic import marshal_overview as MO
        from backend.models.marshal import Marshal
        from backend.models.personality import Personality
        from backend.models.world_state import WorldState
        world = WorldState(player_nation="France")
        m = Marshal(name="Ney", personality=Personality.AGGRESSIVE, nation="France",
                    location="Vienna", strength=1)
        m.personality = "aggressive"          # the scenario roster's string form
        m.captured_by = captor
        m.captured_turn = 1
        world.marshals = {"Ney": m}
        cards = MO.build_marshal_overview(world)
        return next(c for c in cards if c["name"] == "Ney")["status_note"]

    def test_a_court_that_takes_the_article_gets_it(self):
        assert self._note("KingdomOfItaly") == "PRISONER of the Kingdom of Italy since T1."

    def test_a_court_that_takes_none_is_unchanged(self):
        assert self._note("Austria") == "PRISONER of Austria since T1."

    def test_the_lever_restores_the_bare_name(self, monkeypatch):
        from backend.game_logic import marshal_overview as MO
        monkeypatch.setattr(MO, "THE_PRISONER_NOTE_TAKES_THE_ARTICLE", False)
        assert self._note("KingdomOfItaly") == "PRISONER of Kingdom of Italy since T1."


# ═══════════════════════════════════════════════════════════════════════
# H1 — the levy renders on the soil that feeds France
# ═══════════════════════════════════════════════════════════════════════

class TestTheLevyRendersWhereItIsPriced:
    """H1, the recon's one predicted defect, confirmed by capture: the region
    panel gated EVERY action row on `controller == _PLAYER_NATION` while the
    substitutes comment beside it said the market "renders on ALLY soil too
    because the granary is open there (IQ1-3A)". Measured on the 1805 boot:
    Amsterdam (Holland's province, Bernadotte standing on it) is priced at 598g
    a battalion and 3,193g a substitute batch, Milan at 3,672g — and the panel
    showed neither."""

    def test_the_panel_branches_on_the_ground_that_feeds_us(self):
        gd = _gd("region_panel")
        assert "var feeds_us :=" in gd
        assert 'int(data.get("recruit_price_here", 0)) > 0' in gd
        assert 'int(data.get("substitute_price_here", 0)) > 0' in gd
        assert "\tif feeds_us:\n" in gd

    def test_the_owner_only_actions_still_gate_on_ownership(self):
        """Build, repair and the garrison are the OWNER's to order — the
        executors refuse them on a vassal's province."""
        gd = _gd("region_panel")
        tail = gd.split("var feeds_us :=", 1)[1]
        assert "if controller == _PLAYER_NATION:" in tail
        build = tail.index("# Build")
        assert tail.index("if controller == _PLAYER_NATION:") < build

    def test_the_backend_prices_a_vassals_province_where_a_french_corps_stands(self):
        """The client's predicate is only honest if the backend really prices
        that ground — so the pin measures the backend, not the copy. Built the
        way `tools/iq10_capture_payloads.py::fresh()` builds it: the SHIPPED
        1805 scenario (the suite pins SOVEREIGN_SCENARIO=none, and the boot
        path reads that env at import, so a delenv alone is not enough), and
        the same `get_filtered_game_state_summary()` the client reads."""
        import contextlib
        import io

        from backend.models.world_state import WorldState
        scenario = (REPO / "godot-client" / "project-sovereign" / "assets"
                    / "maps" / "europe_1805.json")
        with contextlib.redirect_stdout(io.StringIO()):
            world = WorldState.from_scenario(str(scenario))
            # The same staging `tools/iq10_capture_payloads.py::cap_regions`
            # uses: a French corps standing on the vassal's capital (the
            # backend prices the ground a corps of ours can be fed on), with
            # losses to buy back (the substitute market buys back LOSSES).
            world.marshals["Bernadotte"].location = "Amsterdam"
            world.marshals["Bernadotte"].strength = max(
                1000, int(world.marshals["Bernadotte"].strength) - 8000)
            world.marshals["Soult"].location = "Paris"
            world.marshals["Soult"].strength = max(
                1000, int(world.marshals["Soult"].strength) - 8000)
            world.nation_gold["France"] = 12000
            world.calculate_visibility()
            world.invalidate_active_nations_cache()
        md = (world.get_filtered_game_state_summary() or {}).get("map_data") or {}
        amsterdam = md.get("Amsterdam") or {}
        assert amsterdam.get("controller") == "Holland"
        assert int(amsterdam.get("substitute_price_here") or 0) > 0, (
            "the boot no longer prices the levy on a vassal's province — H1's "
            "predicate would render a row the executor refuses")
        paris = md.get("Paris") or {}
        assert int(paris.get("substitute_price_here") or 0) > 0


# ═══════════════════════════════════════════════════════════════════════
# IQ10-4 / IQ10-5 — the two surfaces that did not fit at Interface Scale 2.0
# ═══════════════════════════════════════════════════════════════════════

class TestEverySurfaceFitsTheScreen:
    """At Interface Scale 2.0 (the client's own maximum, `ui_settings.gd`
    MAX_UI_SCALE) the logical viewport halves: 1600x900 becomes 800x450."""

    def test_the_empty_letter_book_is_clamped_too(self):
        """IQ10-4. `show_mailbox` returned early on an empty book, one line
        before the clamp, so the authored 960x720 rect stood: measured at 2.0,
        Close at y=746 off a 450-high screen and the visible area a flat
        colour. With one row present the same panel already fitted (776x362)."""
        gd = _gd("mailbox_panel")
        head = gd.split("func show_mailbox", 1)[1].split("\nfunc ", 1)[0]
        empty_arm = head.split("if items.is_empty():", 1)[1].split("\treturn", 1)[0]
        assert "Utils.clamp_centered_panel($PanelContainer)" in empty_arm
        assert head.count("Utils.clamp_centered_panel($PanelContainer)") >= 2

    def test_the_diorama_fits_by_scaling_the_whole_tableau(self):
        """IQ10-5. The tray is authored in design px with absolutely placed
        children and `_tray_inner.custom_minimum_size = Vector2(TRAY_W,
        TRAY_H)` is a hard floor, so the clamp could shrink the height (362)
        and not the width: measured at 2.0, x=-100 with width 1000, and Replay
        and Close at y=658. A tableau fits by scaling, not by reflowing."""
        gd = _gd("battle_diorama")
        assert "func _fit_tray_to_viewport" in gd
        assert "_fit_tray_to_viewport()" in gd
        assert "_tray.scale = Vector2(fit, fit)" in gd
        assert "_tray.pivot_offset" in gd
        assert "THE_TABLEAU_FITS_THE_SCREEN" in gd
        # the lever's False arm keeps the old call rather than deleting it
        assert "Utils.clamp_centered_panel(_tray)" in gd

    def test_the_diorama_is_a_no_op_on_a_screen_that_fits(self):
        """`minf(1.0, ...)` — a 1600x900 window at Interface Scale 1.0 gets
        scale 1.0, so every frame on an ordinary screen is unchanged."""
        gd = _gd("battle_diorama")
        body = gd.split("func _fit_tray_to_viewport", 1)[1].split("\nfunc ", 1)[0]
        assert "fit = minf(1.0," in body.replace("\n", " ").replace("  ", " ")


# ═══════════════════════════════════════════════════════════════════════
# IQ10-6 — the game's own sentence is typable
# ═══════════════════════════════════════════════════════════════════════

class TestTheMissionSentenceIsTypable:
    """IQ10-6, found by the payload capture, whose own staging used the long
    form: the confirmation says "I shall begin efforts to gather intelligence
    on Austria" (`MISSION_DESCRIPTIONS["GATHER_INTEL"]`), and only the
    abbreviation `gather intel on` parsed — a player who echoed the game got
    Berthier's shrug."""

    @pytest.mark.parametrize("line", [
        "gather intelligence on Austria",
        "gather intel on Austria",
        "spy on Austria",
    ])
    def test_every_form_reaches_the_mission(self, line):
        from backend.main import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        client.post("/new_game", json={})
        r = client.post("/command", json={"command": line}).json()
        dlg = r.get("diplomatic_dialogue") or {}
        assert dlg.get("type") == "mission", (line, r.get("message"))
        assert "start_mission" in [o.get("action") for o in dlg.get("options", [])]

    def test_the_printed_sentence_and_the_parsed_one_are_the_same_words(self):
        from backend.ai import llm_client
        from backend.game_logic.diplomatic_dialogue import MISSION_DESCRIPTIONS
        src = pathlib.Path(llm_client.__file__).read_text(encoding="utf-8")
        printed = MISSION_DESCRIPTIONS["GATHER_INTEL"]          # "gather intelligence on"
        assert f'"{printed}"' in src, (
            f"the game prints {printed!r} and the parser does not know it")


class TestThePopupSaysItOnce:
    """IQ10-3: every reason the backend ships is a whole sentence, so the
    template's own added stop read "...or refuse it..". The only double
    punctuation in 160 captured frames."""

    def test_the_line_does_not_add_a_second_full_stop(self):
        gd = _gd("incoming_proposal_popup")
        assert '"]Grant unavailable: " + grant_reason' in gd
        assert 'grant_reason.ends_with(".")' in gd
        assert '"]Grant unavailable: %s.[/color]"' not in gd


# ═══════════════════════════════════════════════════════════════════════
# The evidence
# ═══════════════════════════════════════════════════════════════════════

class TestTheEvidenceExists:
    def test_the_memo_is_committed_and_names_its_frames(self):
        memo = AUDITS / "IQ10_CLIENT_PASS_2026_09_19.md"
        assert memo.exists(), "the pass's memo of record is missing"
        text = memo.read_text(encoding="utf-8")
        named = set(re.findall(r"IQ10_[A-Z0-9_]+_2026_09_19(?:_X2)?\.png", text))
        assert len(named) >= 20, f"only {len(named)} frames named in the memo"
        missing = [n for n in named if not (AUDITS / n).exists()]
        assert missing == [], f"the memo names frames that are not committed: {missing[:6]}"

    def test_the_committed_frames_cover_the_rows_this_pass_owns(self):
        """One frame per IQ row whose client half was owed, by name."""
        for stem in ("IQ10_LEDGER_BOOT_ECONOMY", "IQ10_DIPLO_BOOT_TALLEYRAND",
                     "IQ10_PETITION_POPUP", "IQ10_PETITION_POPUP_NO_DP",
                     "IQ10_REGION_AMSTERDAM", "IQ10_GENERALS_BOOT",
                     "IQ10_DIORAMA_DADJ", "IQ10_ENEMY_PHASE_IQ5",
                     "IQ10_MAILBOX_BOOT", "IQ10_GENERALS_NP_CAPTIVE"):
            png = AUDITS / f"{stem}_2026_09_19.png"
            assert png.exists(), f"missing evidence frame: {png.name}"
            assert png.stat().st_size > 8000, f"{png.name} is too small to be a real frame"
