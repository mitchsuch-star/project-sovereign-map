"""Session UI-6 (November 13, 2026) — THE READBACK ROW and UI6-X1 THE HISTORY'S
OFFERS, driven.

UI6-X1 (P3). Session UI-5 PERSISTED the command history (UiSettings), and the
completer offered it first — so a line naming a marshal the board does not
show (4.7% of the archived commands name a commander fogged on the 1805 boot:
`ArchdukeCharles` 37 times, `Kutuzov` 28), or a typo, came back as the table's
SUGGESTION in a campaign that never saw him. The comments said "session-only,
never persisted"; they were stale. The client keeps no roster of who is
hidden, so the offer filter is a WHITELIST: a remembered line is offered only
when every word in it stands on today's board — our marshals, the corps in
sight, the provinces, the completer's verbs and a few joining words
(`main._history_line_is_safe`). A fogged name, an invented one and a typo all
fail it alike; before the first board of a session nothing naming a marshal is
offered (fail closed).

THE WALK IS NOT FILTERED. The plan first filed this as a fog leak and filtered
the Up/Down walk too; under the recorded doctrine a commander's NAME is public
and only his place is fogged (`llm_client._askable_enemy_names`, pinned by
`tests/test_crt2_the_name_is_never_replaced.py`), and the walk is the player's
own recall: it writes back every line he typed, as typed — the typo walked
back to be mended, the free word ("quickly") kept.

THE READBACK ROW (N6): `GET /parse_preview` read while the player types —
after a 220 ms rest, one request in flight on its own HTTPRequest, a stale
answer dropped by its serial AND its line, a small cache, the answer coloured
by its parts' roles, a candidate a link that FILLS the line and never sends.

`tools/readback_harness.gd` drives the REAL `main.tscn` behind an API stub,
headless (ENGINE_LANES["engine_panels"]). It SKIPS without the engine — a
skip is not a pass. The pure-Python twin below needs no engine: it mirrors the
client's filter over the real 1805 boot board and holds it to the backend's
own oracle, `parse_preview.mentions_hidden_name`.
"""

import json
import os
import pathlib
import re
import shutil
import subprocess

import pytest

import backend.main as M
from backend.commands import parse_preview as PP
from backend.display_names import humanize_entity_name
from tests import _chip_census as C

_REPO = pathlib.Path(__file__).resolve().parents[1]
_PROJECT = _REPO / "godot-client" / "project-sovereign"
_HARNESS = _REPO / "tools" / "readback_harness.gd"
_MAIN_GD = _PROJECT / "scripts" / "main.gd"

_CANDIDATES = [
    os.environ.get("GODOT_BIN", ""),
    r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
    r"\Godot_v4.4.1-stable_win64.exe",
    "godot",
    "godot4",
]

SEEDED = ["Ney, attack Archduke Charles", "Ney, attack Mack", "Ney, march to Vienna",
          "Zorglub, charge", "what can I do", "ney, atack mack"]
SAFE = ["Ney, attack Mack", "Ney, march to Vienna", "what can I do"]


def _engine():
    for candidate in _CANDIDATES:
        if not candidate:
            continue
        if os.path.sep in candidate or "/" in candidate:
            if pathlib.Path(candidate).is_file():
                return candidate
            continue
        found = shutil.which(candidate)
        if found:
            return found
    return None


@pytest.fixture(scope="module")
def driven(tmp_path_factory):
    """One headless run of the real scene, shared by every driven assertion."""
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    out = tmp_path_factory.mktemp("readback") / "readback.json"
    env = dict(os.environ, READBACK_OUT=str(out))
    proc = subprocess.run(
        [engine, "--headless", "--path", str(_PROJECT), "--script", str(_HARNESS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=300, env=env, cwd=str(_PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstdout tail:\n{proc.stdout[-2000:]}\n"
                    f"stderr tail:\n{proc.stderr[-2000:]}")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "error" not in payload, payload
    payload["script_errors"] = (proc.stdout + proc.stderr).count("SCRIPT ERROR")
    return payload


# ═══ UI6-X1 — the history, driven ═══════════════════════════════════════════

class TestTheHistoryOffersOnlyTheBoard:

    def test_the_harness_ran_clean(self, driven):
        assert driven["script_errors"] == 0

    def test_each_line_is_judged_by_its_words(self, driven):
        assert driven["h1_verdicts"] == {
            "Ney, attack Archduke Charles": False,   # a fogged name
            "Ney, attack Mack": True,                # ours, a verb, a corps in sight
            "Ney, march to Vienna": True,            # ours, a verb, a province
            "Zorglub, charge": False,                # an invented name
            "what can I do": True,                   # the completer's own words
            "ney, atack mack": False,                # a typo — the line it cannot read
        }
        assert driven["h1_safe_lines"] == SAFE

    def test_the_offers_never_name_the_fogged(self, driven):
        offers = driven["h1_offers_ney"]
        assert "Ney, attack Mack" in offers and "Ney, march to Vienna" in offers, offers
        for prefix in ("h1_offers_ney", "h1_offers_ney_attack"):
            assert not any("Charles" in o or "Archduke" in o for o in driven[prefix]), driven[prefix]
        assert "Ney, attack Mack" in driven["h1_offers_ney_attack"]
        assert driven["h1_offers_zorg"] == []

    def test_the_walk_recalls_every_line_typed(self, driven):
        up = driven["h1_walk_up"]
        assert set(up) == set(SEEDED), up            # the typo and the unknown name too
        assert up[0] == SEEDED[-1]                   # newest first
        down = driven["h1_walk_down"]
        assert all(line in SEEDED or line == "" for line in down), down
        assert "" in down                            # off the end: the typed (empty) line back

    def test_the_prefixed_walk_narrows_by_the_prefix_only(self, driven):
        walked = driven["h1_walk_prefixed"]
        assert walked == ["ney, atack mack", "Ney, march to Vienna", "Ney, attack Mack",
                          "Ney, attack Archduke Charles"], walked

    def test_before_the_first_board_nothing_names_a_marshal(self, driven):
        assert driven["h2_safe_lines"] == ["what can I do"]
        assert driven["h2_offers_ney"] == []
        assert "what can I do" in driven["h2_offers_what"]
        assert set(driven["h2_walk_up"]) == set(SEEDED)   # the walk is the player's own recall


# ═══ N6 — the readback row, driven ══════════════════════════════════════════

class TestTheReadbackRow:

    def test_it_stands_beside_the_line_hidden_and_unsized(self, driven):
        assert driven["r1_row_exists"] is True
        names = driven["r1_siblings"]
        at = names.index("ReadbackRow")
        assert names[at - 1] == "CompletionRow" and names[at + 1] == "InputSection", names
        assert driven["r1_hidden_at_rest"] is True
        assert driven["r1_font_override"] is False   # the theme's 16 is the line's 16
        assert driven["r1_fit_content"] is False     # measured (UXR-2's scroll rule)

    def test_one_ask_after_the_rest(self, driven):
        assert driven["r2_setting_on"] is True
        assert driven["r2_asked_at_once"] == 0
        assert driven["r2_asked_after_rest"] == 1
        assert driven["r2_asked_line"] == "Ney, attack Mack"
        # FUN2-27 (row FUN, Session FUN-2, November 27, 2026): the rest read in the
        # engine's own frame time, the clock the 220 ms debounce Timer counts — the
        # wall clock (`r2_rest_ms`, kept as a reading) read 78 ms under the whole
        # suite's load while the engine handed out catch-up frame time.
        assert driven["r2_rest_engine_ms"] >= 200, (driven["r2_rest_engine_ms"], driven["r2_rest_ms"])

    def test_a_stale_answer_is_dropped(self, driven):
        assert driven["r2_visible_after_stale"] is False
        assert driven["r2_text_after_stale"] == ""

    def test_the_answer_reads_in_its_parts_words(self, driven):
        assert driven["r2_visible"] is True
        text = driven["r2_text"]
        # (row FR, Session FR-1 — IC3-N1: a plain price reads against the pool in hand)
        assert text.startswith("▸ Ney · attack Mack (Swabia) · 1 action of the 4 in hand · "), text
        assert text.endswith("may object"), text
        if driven["r2_compact"]:
            assert "replaces his march" not in text and driven["r2_tooltip"] == ""
        elif driven["r2_folded"]:
            # folded: a note is the row's hover, never printed
            assert "replaces his march" not in text
            assert driven["r2_tooltip"] == "replaces his march"
        else:
            assert text.endswith("replaces his march")

    def test_a_candidate_fills_the_line_and_sends_nothing(self, driven):
        assert driven["r3_asked"] == 1
        assert driven["r3_text"] == "? No marshal ‘Nye’ of ours — [Ney]?"
        assert driven["r3_line_after_fill"] == "Ney, attack Mack"
        assert driven["r3_sends"] == 0

    def test_a_remembered_line_shows_at_once_and_asks_nothing(self, driven):
        assert driven["r3_cached_visible"] is True
        assert "Ney · attack Mack (Swabia)" in driven["r3_cached_text"]
        assert driven["r3_cached_new_asks"] == 0

    def test_a_closed_line_hides_the_row_and_cancels(self, driven):
        assert driven["r4_visible_after_close"] is False
        assert driven["r4_cancelled"] is True


# ═══ the twin: the client's filter, mirrored, against the backend's oracle ══

def _block(src: str, name: str) -> str:
    """The bracketed body of `const <name> := [ … ]` / `{ … }` in main.gd."""
    m = re.search(r"(?m)^const %s := ([\[{])" % re.escape(name), src)
    assert m, name
    open_ch = m.group(1)
    close_ch = "]" if open_ch == "[" else "}"
    depth, i = 0, m.start(1)
    while i < len(src):
        ch = src[i]
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return src[m.start(1) + 1:i]
        i += 1
    raise AssertionError(name)


def _client_lists():
    src = _MAIN_GD.read_text(encoding="utf-8")
    join = re.findall(r'"([^"]*)"', _block(src, "HISTORY_JOIN_WORDS"))
    slots = re.findall(r'"(\w+)":', _block(src, "_NAME_SLOT_WORDS"))
    verbs = re.findall(r'\[\s*"([^"]*)"\s*,', _block(src, "_MARSHAL_VERBS"))
    conts = re.findall(r'\[\s*"[^"]*"\s*,\s*"([^"]*)"', _block(src, "_CONTINUATIONS"))
    bare = re.findall(r'\[\s*"([^"]*)"\s*,', _block(src, "_BARE_COMMANDS"))
    verb_words = re.findall(r'\[\s*"([^"]*)"\s*,', _block(src, "UI5_VERB_WORDS"))
    breaks = re.search(r'(?m)^const HISTORY_BREAKS := "([^"]*)"', src).group(1)
    return join, slots, verbs, conts, bare, verb_words, breaks


def _words(text: str, breaks: str) -> list:
    """`main._history_words`, mirrored."""
    clean = []
    for ch in text.lower():
        code = ord(ch)
        letter = (48 <= code <= 57) or (97 <= code <= 122) or (code > 191 and ch not in breaks)
        clean.append(ch if letter else " ")
    return [w for w in "".join(clean).split(" ") if w]


def _known(game_state: dict) -> tuple:
    join, slots, verbs, conts, bare, verb_words, breaks = _client_lists()
    known = set(join) | set(slots)
    for phrase in verbs + conts + bare + verb_words:
        known |= set(_words(phrase, breaks))
    for key in list(game_state.get("marshals") or {}) + list(game_state.get("enemies") or {}):
        known |= set(_words(str(key), breaks)) | set(_words(humanize_entity_name(str(key)), breaks))
    for region in game_state.get("map_data") or {}:
        known |= set(_words(str(region), breaks))
    return known, breaks


def _mirror_safe(game_state: dict, line: str) -> bool:
    """`main._history_line_is_safe`, mirrored."""
    known, breaks = _known(game_state)
    return all(w.isdigit() or w in known for w in _words(line, breaks))


# A hand-curated slice of the archive's shapes (no command archive ships with
# a stable schema): fogged names, names in sight, provinces, typos, questions.
CURATED = [
    "Ney, attack Archduke Charles",
    "Ney, attack Kutuzov",
    "Davout, pursue Kutuzov",
    "Soult, march to Vienna then attack Kutuzov",
    "where is Kutuzov",
    "what if Ney attacks Archduke Charles",
    "Murat, follow Archduke Charles",
    "Ney, attack Bagration",
    "Lannes, hold Swabia until Soult arrives",
    "Ney, attack Mack",
    "Bernadotte, scout Bohemia",
    "Zorglub, charge",
    "ney, atack mack",
    "end turn",
    "what can I do",
    "status",
]


@pytest.fixture(scope="module")
def board():
    with pytest.MonkeyPatch.context() as mp:
        C.board_env(mp)
        yield M.world, C.game_state_now()


class TestTheTwinWithholdsWhatTheBackendCallsHidden:

    def test_the_mirror_reads_the_clients_own_lists(self):
        join, slots, verbs, conts, bare, verb_words, breaks = _client_lists()
        assert "until" in join and "to" in slots
        assert "march to" in verbs and "then attack" in conts and "end turn" in bare
        assert "fall back" in verb_words and "’" in breaks

    def test_every_line_naming_a_hidden_commander_is_withheld(self, board):
        world, game_state = board
        flagged = [line for line in CURATED if PP.mentions_hidden_name(world, line)]
        assert flagged, "the boot board hides no one the curated lines name — the twin is vacuous"
        leaked = [line for line in flagged if _mirror_safe(game_state, line)]
        assert leaked == [], leaked

    def test_the_boards_own_lines_stand(self, board):
        """Sensitive: the filter is no wall — a line of the board's own words
        is offered, and the question and the day's end always are."""
        _world, game_state = board
        own = humanize_entity_name(sorted(game_state["marshals"])[0])
        province = sorted(game_state["map_data"])[0]
        assert _mirror_safe(game_state, f"{own}, march to {province}")
        assert _mirror_safe(game_state, "end turn") and _mirror_safe(game_state, "what can I do")
        assert not _mirror_safe(game_state, "Zorglub, charge")
