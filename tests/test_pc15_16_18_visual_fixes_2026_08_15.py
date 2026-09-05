"""PC15-16 + PC15-18 — the visual-pass client fixes (August 15, 2026).

PC15-16: PARTIAL/STALE-intel provinces rendered "Income: 0g / Stability: 0%"
as FACTS on the region panel and map tooltip while Supply correctly read
Unknown. Fix = extend the CA9-F5 ``-1`` "not known" sentinel from
``supply_capacity`` to ``income_value`` / ``effective_income`` /
``stability`` in ``get_filtered_game_state_summary``'s hidden-econ block,
and branch in BOTH ``.gd`` readers (the CA9 review's landmine: a sentinel
with one reader fixed is a worse lie than the zero).

PC15-18: (a) the screen hotkeys were dead in the game's dominant state —
the client re-grabs command-input focus at every control-return tail and a
focused LineEdit consumes printable keys before ``_unhandled_input`` ever
sees them; the playtest hit it on N/Moniteur.  Fix = the F1 precedent:
Alt+<screen key> intercepted in ``_on_command_input_gui_input`` (a bare
letter must keep typing — "ney…" starts with n; the bare keys still work
whenever the input is unfocused).  (b) the enemy-phase dialog ignored the
mouse wheel — the NV-P1 defect class: a ``fit_content`` RichTextLabel
inside a ScrollContainer defaults to MOUSE_FILTER_STOP and consumes the
wheel before its parent can scroll.  The ledger fixed ONE member at NV-6
and the July-25 R4 fix (scroll_active=false on the terminal) was proved
insufficient by both later members — so the class is closed by CENSUS:
every such node must set MOUSE_FILTER_PASS, and a new scene that forgets
fails here instead of shipping the fourth generation of this bug.
"""

import re
from pathlib import Path

from backend.models.intel import FULL, PARTIAL
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parent.parent
CLIENT = REPO_ROOT / "godot-client" / "project-sovereign"


def _first_enemy_region(world):
    for name, region in world.regions.items():
        if region.controller and region.controller != world.player_nation:
            return name
    raise AssertionError("no enemy-controlled region on the fixture world")


# ============================================================================
# PC15-16 — the backend sentinel
# ============================================================================

class TestPC1516SentinelBackend:
    """Hidden econ data carries -1, never a fabricated 0."""

    def test_partial_enemy_region_ships_sentinels(self):
        world = WorldState()
        name = _first_enemy_region(world)
        world._intel_entry(name).visibility = PARTIAL
        rd = world.get_filtered_game_state_summary()["map_data"][name]
        assert rd["income_value"] == -1
        assert rd["effective_income"] == -1
        assert rd["stability"] == -1
        assert rd["stability_label"] == "Unknown"
        # The founding CA9-F5 sentinel still rides beside the new ones.
        assert rd["supply_capacity"] == -1

    def test_full_visibility_enemy_region_ships_real_numbers(self):
        """Negative control: FULL intel is never sentineled."""
        world = WorldState()
        name = _first_enemy_region(world)
        world._intel_entry(name).visibility = FULL
        rd = world.get_filtered_game_state_summary()["map_data"][name]
        region = world.regions[name]
        assert rd["effective_income"] == int(region.get_effective_income())
        assert rd["stability"] == int(region.stability)
        assert rd["effective_income"] >= 0
        assert rd["stability"] >= 0

    def test_own_regions_never_sentineled(self):
        world = WorldState()
        summary = world.get_filtered_game_state_summary()
        own = [n for n, r in world.regions.items()
               if r.controller == world.player_nation]
        assert own, "fixture world has no player regions"
        for name in own:
            rd = summary["map_data"][name]
            assert rd["effective_income"] >= 0, name
            assert rd["stability"] >= 0, name

    def test_source_pin_no_fabricated_zero_in_hidden_block(self):
        """The CA9-F5 idiom, extended: the hidden-econ block never writes
        a zero for a value the player would read as a fact."""
        import inspect

        from backend.models import world_state as ws
        src = inspect.getsource(ws)
        for key in ("income_value", "effective_income", "stability"):
            assert f'filtered_region["{key}"] = -1' in src, key
            assert f'filtered_region["{key}"] = 0' not in src, key


class TestPC1516BothGdReadersBranch:
    """THE landmine (CA9 review): a sentinel with one reader fixed is a
    worse lie than the zero — both .gd readers must branch."""

    def _window(self, src: str, needle: str, span: int = 700) -> str:
        at = src.index(needle)
        return src[max(0, at - span):at + span]

    def test_region_panel_branches(self):
        src = (CLIENT / "scripts" / "region_panel.gd").read_text(
            encoding="utf-8")
        income_win = self._window(src, 'data.get("effective_income"')
        assert "effective_income < 0" in income_win, (
            "region_panel.gd prints the raw income sentinel")
        assert "Unknown" in income_win
        assert "stability < 0" in income_win, (
            "region_panel.gd prints the raw stability sentinel")

    def test_map_tooltip_branches(self):
        src = (CLIENT / "scenes" / "map_renderer_base.gd").read_text(
            encoding="utf-8")
        income_win = self._window(src, 'data.get("effective_income"')
        assert "effective_income < 0" in income_win, (
            "the map tooltip prints the raw income sentinel")
        assert "Income: Unknown" in income_win
        stab_win = self._window(src, 'data.get("stability"')
        assert "stability < 0" in stab_win, (
            "the map tooltip prints the raw stability sentinel")
        assert "Stability: Unknown" in stab_win


# ============================================================================
# PC15-18(b) — the wheel-eater family census
# ============================================================================

_NODE_RE = re.compile(
    r'\[node name="(?P<name>[^"]+)" type="(?P<type>[^"]+)"'
    r'(?: parent="(?P<parent>[^"]+)")?[^\]]*\]')
_SCRIPT_RE = re.compile(
    r'\[ext_resource type="Script"[^\]]*?path="res://(?P<path>[^"]+)"')
_ONREADY_RE = re.compile(
    r'@onready\s+var\s+(?P<var>\w+)(?::[^=\n]+)?\s*=\s*'
    r'[\$%](?P<path>[\w/]+)')


def _scene_nodes(text):
    """Yield (name, type, parent, block) for every node in a .tscn."""
    matches = list(_NODE_RE.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        yield (m.group("name"), m.group("type"), m.group("parent") or "",
               text[m.end():end])


def _wheel_eaters(scene_text):
    """RichTextLabels with fit_content directly under a ScrollContainer."""
    nodes = list(_scene_nodes(scene_text))
    types_by_name = {}
    for name, ntype, _parent, _block in nodes:
        types_by_name.setdefault(name, set()).add(ntype)
    out = []
    for name, ntype, parent, block in nodes:
        if ntype != "RichTextLabel":
            continue
        if "fit_content = true" not in block:
            continue
        direct_parent = parent.split("/")[-1] if parent else ""
        if "ScrollContainer" not in types_by_name.get(direct_parent, set()):
            continue
        out.append((name, block))
    return out


class TestPC1518WheelFamilyCensus:
    """Every fit_content RichTextLabel under a ScrollContainer must let the
    wheel through — scene-side ``mouse_filter = 1`` or script-side
    ``<var>.mouse_filter = Control.MOUSE_FILTER_PASS``."""

    def _family(self):
        found = []
        for tscn in sorted((CLIENT / "scenes").glob("*.tscn")):
            text = tscn.read_text(encoding="utf-8")
            for name, block in _wheel_eaters(text):
                found.append((tscn, name, block, text))
        return found

    def test_census_is_not_blind(self):
        """If the parser finds nothing, the census proves nothing."""
        family = self._family()
        names = {(t.stem, n) for t, n, _b, _txt in family}
        # The three members with a filed defect each must be in view.
        assert ("enemy_phase_dialog", "ContentLabel") in names
        assert ("strategic_ledger", "ContentArea") in names
        assert ("main", "OutputDisplay") in names
        assert len(family) >= 10, (
            f"census shrank to {len(family)} — parser broken or scenes "
            f"restructured; re-derive before trusting this test")

    def test_every_member_lets_the_wheel_through(self):
        failures = []
        for tscn, name, block, scene_text in self._family():
            if re.search(r"^mouse_filter = [12]$", block, re.M):
                continue  # scene-side PASS(1)/IGNORE(2)
            ok = False
            for sm in _SCRIPT_RE.finditer(scene_text):
                script_path = REPO_ROOT / "godot-client" / \
                    "project-sovereign" / sm.group("path")
                if not script_path.exists():
                    continue
                script = script_path.read_text(encoding="utf-8")
                for om in _ONREADY_RE.finditer(script):
                    if not om.group("path").endswith(name):
                        continue
                    setter = (om.group("var")
                              + ".mouse_filter = Control.MOUSE_FILTER_PASS")
                    if setter in script:
                        ok = True
            if not ok:
                failures.append(f"{tscn.name}:{name}")
        assert not failures, (
            "wheel-eating RichTextLabel(s) with no MOUSE_FILTER_PASS — the "
            "NV-P1 class regressing: " + ", ".join(failures))

    def test_scroll_active_alone_is_not_accepted(self):
        """The July-25 R4 fix set scroll_active=false on the terminal and
        the wheel still died on the ledger and the enemy dialog — this
        census must never be satisfiable by scroll_active alone."""
        scene = (CLIENT / "scenes" / "enemy_phase_dialog.tscn").read_text(
            encoding="utf-8")
        eaters = _wheel_eaters(scene)
        assert eaters, "enemy dialog restructured — re-derive the census"
        assert "scroll_active = false" in eaters[0][1], (
            "the member that PROVED scroll_active insufficient no longer "
            "carries it — update this test's premise")


# ============================================================================
# PC15-18(a) — screen hotkeys reachable while typing
# ============================================================================

class TestPC1518HotkeysReachableWhileTyping:
    def test_screen_hotkey_table_is_complete(self):
        src = (CLIENT / "scripts" / "main.gd").read_text(encoding="utf-8")
        at = src.index("_SCREEN_HOTKEYS := {")
        table = src[at:src.index("}", at)]
        for key, screen in (("KEY_L", "event_log"), ("KEY_T", "ledger"),
                            ("KEY_G", "generals"),
                            ("KEY_D", "diplomatic_ledger"),
                            ("KEY_R", "dispatch"), ("KEY_N", "gazette")):
            assert re.search(key + r':\s*"' + screen + '"', table), (
                f"{key} missing from the focus-safe hotkey table")

    def test_alt_route_exists_and_keeps_the_modal_gate(self):
        src = (CLIENT / "scripts" / "main.gd").read_text(encoding="utf-8")
        at = src.index("func _on_command_input_gui_input")
        # FA-N56 (slice 13): this was a fixed 2,500-char scrape over a
        # 972-char function, so it read 1,528 chars past the body,
        # through _history_previous/_history_next and into
        # _unhandled_input's docstring. It was not vacuous, but it was
        # one refactor from being satisfied by a neighbouring function
        # — the NA-6 dead-name trap. Bound it to the body.
        handler = src[at:src.index("\nfunc ", at + 10)]
        assert "alt_pressed" in handler, (
            "the focus-safe screen-hotkey route is gone — the advertised "
            "letter hotkeys are dead again whenever the terminal has focus")
        assert "_SCREEN_HOTKEYS" in handler
        assert "_is_modal_dialog_open()" in handler, (
            "the Alt route must respect the same modal gate "
            "_is_hotkey_blocked enforces on the unfocused path")

    def test_bare_keys_still_work_unfocused(self):
        """The bare-letter path is untouched — N opens the gazette from
        _unhandled_input when the input is unfocused."""
        src = (CLIENT / "scripts" / "main.gd").read_text(encoding="utf-8")
        at = src.index("func _unhandled_input")
        handler = src[at:at + 5000]
        assert "KEY_N" in handler
        assert 'toggle_screen("gazette")' in handler

    def test_buttons_advertise_the_focus_safe_form(self):
        src = (CLIENT / "scripts" / "top_bar.gd").read_text(encoding="utf-8")
        assert "Alt+" in src, (
            "the nav buttons no longer name the focus-safe hotkey form")
