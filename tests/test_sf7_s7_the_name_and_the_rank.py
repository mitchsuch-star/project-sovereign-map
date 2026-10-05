"""Score Finish Step 7 slice 7 (October 4, 2026) — Chunk 9's backend half.

  * SF5-X3 — a client's general is styled "General", not "Marshal", through
    ONE style helper (`display_names.marshal_title`: the court's own
    honorific AND the display name), read by every template that styles a
    marshal object, with an AST census so a new `Marshal {...}` literal fails.
  * NPC-12 — the remainder of the name census: the measured producers that
    still printed a raw roster key ("ArchdukeCharles") to the reader, and the
    driven name census (`tools/_name_census.py`, `--name-census`) over every
    rendered string, POST and GET.
  * S5-4 — at its cap the dialogue queue overflows into the mailbox instead of
    dropping, push and preempt together.
  * SF7-X7 — a separate peace names what EACH side keeps under the status
    quo: before it is sent (the proposal's forecast, read off the ratifier's
    own `status_quo_retentions`) and the morning after.

Every pin stages the ordinary case on the shipped 1805 board or reads the
real source; the levers flip.
"""
from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import display_names as DN
from backend.commands.parser import CommandParser
from backend.game_logic import contingent as C
from backend.game_logic import game_end as GE
from backend.models import dialogue_manager as DMOD
from backend.models.marshal import StrategicOrder
from tools import _name_census as NC

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
CMDH = ROOT / "tools" / "playtest_scripts" / "commanded_full40.json"


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _holland_general(world):
    """Holland's contingent on the boot board — a client's general (R12)."""
    beat = C.raise_contingent(world, "Holland")
    assert beat is not None, "Holland could not raise its contingent"
    record = C.contingent_record(world, "Holland")
    general = world.marshals[record["marshal"]]
    assert general.original_nation == "Holland" and general.nation == "France"
    return general


# ═══════════════════════ SF5-X3 — the one style ═══════════════════════

class TestTheOneStyle:
    def test_each_court_gives_its_own_rank(self, shipped):
        _, world = shipped
        assert DN.marshal_title(world, "Ney") == "Marshal Ney"
        assert DN.marshal_title(world, "Mack") == "General Mack"
        assert DN.marshal_title(world, "ArchdukeCharles") == "the Archduke Charles"
        assert DN.marshal_title(world, "Napoleon") == "the Emperor Napoleon"

    def test_start_capitalises_the_article_and_nothing_else(self, shipped):
        _, world = shipped
        assert DN.marshal_title(world, "ArchdukeCharles", start=True) == "The Archduke Charles"
        assert DN.marshal_title(world, "Napoleon", start=True) == "The Emperor Napoleon"
        assert DN.marshal_title(world, "Ney", start=True) == "Marshal Ney"

    def test_a_clients_general_is_a_general(self, shipped, monkeypatch):
        _, world = shipped
        general = _holland_general(world)
        shown = DN.humanize_entity_name(general.name)
        assert DN.marshal_title(world, general.name) == f"General {shown}"
        monkeypatch.setattr(DN, "A_CLIENTS_GENERAL_IS_STYLED_GENERAL", False)
        assert DN.marshal_title(world, general.name) == f"Marshal {shown}"

    def test_the_style_reads_r12s_one_predicate(self, shipped, monkeypatch):
        """A client's general is defined ONCE (`contingent.is_clients_general`)
        — with R12's lever down he is the Emperor's marshal for the ladder and
        the purse, and the style follows."""
        _, world = shipped
        general = _holland_general(world)
        monkeypatch.setattr(C, "A_CLIENTS_GENERAL_IS_NOT_THE_EMPERORS_MARSHAL", False)
        assert DN.marshal_title(world, general.name).startswith("Marshal ")

    def test_his_rank_survives_his_fall(self, shipped):
        _, world = shipped
        general = _holland_general(world)
        name = general.name
        with contextlib.redirect_stdout(io.StringIO()):
            world.destroy_marshal(general, cause="destroyed", victor="Britain")
        assert name not in world.marshals
        assert world.fallen_marshals[name]["original_nation"] == "Holland"
        assert DN.marshal_title(world, name) == f"General {DN.humanize_entity_name(name)}"

    def test_a_name_the_world_does_not_know_keeps_the_old_style(self, shipped):
        _, world = shipped
        assert DN.marshal_title(world, "Zorglub") == "Marshal Zorglub"
        assert DN.marshal_title(None, "ArchdukeCharles") == "Marshal Archduke Charles"


# ═══════════════════════ SF5-X3 — the census ═══════════════════════

# Every surviving `Marshal {` site, with the reason it keeps the literal.
# A site that disappears fails the census too (a stale allowlist is a lie).
ALLOWLIST = {
    # the helper's own fallback, and `_rank`'s lever-down arm
    ("backend/display_names.py", "return f\"Marshal {display}\""),
    ("backend/game_logic/dispatch.py", "return f\"Marshal {shown}\""),
    # a name the world does not know has no court: the refusal echoes it
    ("backend/commands/meta_executor.py", "f\"Marshal {marshal_name} not found\""),
    ("backend/commands/disobedience.py", "f'Marshal {marshal_name} not found'"),
    ("backend/commands/strategic_executor.py", "f\"Marshal {marshal_name} not found\""),
    ("backend/commands/economy_executor.py", "(f\"There is no Marshal {name} on our rolls, Sire. \""),
    # the abandon-allies objection template has no producer (personality.py)
    ("backend/commands/disobedience.py", "\"\\\"Sire, Marshal {ally} depends on our support,\\\" {name} warns."),
    # a scenario-authoring error raised at boot, and a debug print
    ("backend/models/marshal.py", "f\"Marshal {data.get('name', '?')!r}: personality {personality!r} \""),
    ("backend/models/world_state.py", "debug_print(f\"  [RETREAT DEBUG] Marshal {marshal_name} not found\")"),
}


def _docstring_nodes(tree):
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                out.add(id(body[0].value))
    return out


def marshal_literal_sites(source: str):
    """(lineno, kind) for every literal "Marshal " directly before an
    interpolation — f-strings (adjacent literals merge, so a split literal
    is caught) and `.format` templates ("Marshal {x}"). Docstrings are not
    prose the player reads."""
    tree = ast.parse(source)
    docs = _docstring_nodes(tree)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            vals = node.values
            for i, v in enumerate(vals):
                if (isinstance(v, ast.Constant) and isinstance(v.value, str)
                        and v.value.endswith("Marshal ") and i + 1 < len(vals)
                        and isinstance(vals[i + 1], ast.FormattedValue)):
                    found.append((node.lineno, "fstring"))
        elif (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docs and re.search(r"Marshal \{", node.value)):
            found.append((node.lineno, "template"))
    return found


class TestTheCensus:
    def test_no_marshal_literal_outside_the_allowlist(self):
        seen = set()
        strays = []
        for path in sorted(BACKEND.rglob("*.py")):
            rel = path.relative_to(ROOT).as_posix()
            src = path.read_text(encoding="utf-8")
            lines = src.splitlines()
            for ln, _kind in marshal_literal_sites(src):
                text = lines[ln - 1].strip()
                hit = next((a for a in ALLOWLIST if a[0] == rel and a[1] in text), None)
                if hit:
                    seen.add(hit)
                else:
                    strays.append(f"{rel}:{ln}: {text[:120]}")
        assert not strays, ("a `Marshal {...}` literal outside the allowlist — style "
                            "the man through display_names.marshal_title:\n"
                            + "\n".join(strays))
        assert seen == ALLOWLIST, f"stale allowlist rows: {ALLOWLIST - seen}"

    @pytest.mark.parametrize("src,expected", [
        ('x = f"Marshal {name} holds"', 1),
        ('x = (f"the fate of Marshal "\n     f"{name}\'s estate")', 1),
        ('T = "Sire — Marshal {marshal} has been taken."', 1),
        ('def f():\n    """Marshal {name} is a docstring."""\n    return 1', 0),
        ('x = f"{marshal_title(world, name)} holds"', 0),
        ('x = "Marshal Ney"', 0),
    ])
    def test_the_census_sees_a_planted_literal(self, src, expected):
        assert len(marshal_literal_sites(src)) == expected


# ═══════════════════ SF5-X3 — the surfaces speak the rank ═══════════════════

class TestTheSurfacesSpeakTheRank:
    def test_the_capture_dispatch_names_a_clients_general(self, shipped, monkeypatch):
        """The done-when, staged: "Sire — Marshal Teulie has been taken" named
        a Kingdom of Italy general a Marshal of the Empire."""
        from backend.game_logic import dispatch as D
        _, world = shipped
        general = _holland_general(world)
        world.event_log = [{"type": "marshal_captured", "marshal": general.name,
                            "nation": "France", "captor": "Britain",
                            "location": "Friesland", "turn": world.current_turn}]
        shown = DN.humanize_entity_name(general.name)
        head = D._build_headline(world, "France") or {}
        assert head.get("class") == "marshal_captured", head
        assert head["text"].startswith(f"Sire — General {shown} has been taken."), head
        monkeypatch.setattr(DN, "A_CLIENTS_GENERAL_IS_STYLED_GENERAL", False)
        head = D._build_headline(world, "France") or {}
        assert head["text"].startswith(f"Sire — Marshal {shown} has been taken.")

    def test_the_lost_estate_headline_reads_the_title(self):
        """The template takes the title whole ("Sire — Austria has taken
        Bavaria — the estate that funded Marshal Ney's honour")."""
        from backend.game_logic import dispatch as D
        from backend.models.world_state import WorldState
        with contextlib.redirect_stdout(io.StringIO()):
            world = WorldState(player_nation="France")
        world.current_turn = 6
        world.get_marshal("Ney").dotation_regions = ["Bavaria"]
        world.event_log.append({"type": "region_captured", "turn": 6, "region": "Bavaria",
                                "captured_by": "Austria", "captured_from": "France"})
        head = D._build_headline(world, "France")
        assert head["class"] == "region_lost_estate"
        assert "the estate that funded Marshal Ney's honour" in head["text"], head["text"]

    def test_the_campaign_log_styles_the_fallen_by_their_court(self, shipped):
        from backend.campaign_log import format_event_oneliner
        _, world = shipped
        event = {"type": "marshal_wounded", "marshal": "ArchdukeCharles",
                 "location": "Bohemia", "until_turn": 6}
        with_world = format_event_oneliner(event, player_nation="France", world=world)
        assert with_world.startswith("The Archduke Charles WOUNDED at Bohemia"), with_world
        bare = format_event_oneliner(event, player_nation="France")
        assert bare.startswith("Marshal Archduke Charles WOUNDED"), bare
        assert "ArchdukeCharles" not in with_world + bare

    def test_the_campaign_log_route_hands_the_formatter_its_world(self, shipped):
        client, world = shipped
        world.log_event({"type": "marshal_wounded", "marshal": "ArchdukeCharles",
                         "nation": "Austria", "location": "Bohemia", "until_turn": 4})
        body = client.get("/campaign_log").json()
        lines = [e.get("display", "") for t in body.get("turns", []) for e in t.get("events", [])]
        assert any(ln.startswith("The Archduke Charles WOUNDED") for ln in lines), lines[:8]

    def test_the_estate_question_names_the_holders_rank(self, shipped):
        from backend.commands.capture_executor import CaptureExecutor, _estate_holder_title
        client, world = shipped
        world.pending_capture_choice = {
            "stage": "estate", "region": "Bohemia", "capturer": "Ney",
            "estate_holder": "ArchdukeCharles",
            "estate_holder_display": "Archduke Charles",
            "estate_holder_title": DN.marshal_title(world, "ArchdukeCharles"),
            "options": ["confiscate", "respect"]}
        prompt = CaptureExecutor._pending_prompt(world.pending_capture_choice)
        assert "the fate of the Archduke Charles's estate at Bohemia" in prompt, prompt
        body = client.post("/command", json={"command": "Ney, hold"}).json()
        assert "You must decide the fate of the Archduke Charles's estate" in body.get("message", ""), body.get("message")
        # a payload predating the title key falls back to the display key
        assert _estate_holder_title({"estate_holder": "ArchdukeCharles"}) == "Marshal Archduke Charles"

    def test_the_estate_stage_mounts_with_the_holders_rank(self, shipped):
        """The mount stamps the TITLE beside the machine key, and the
        question reads it: "Sire — Bohemia sustains the Archduke Charles's
        household" (measured before: "Marshal ArchdukeCharles's")."""
        from backend.commands.capture_executor import CaptureExecutor
        _, world = shipped
        charles = world.marshals["ArchdukeCharles"]
        charles.dotation_regions = ["Bohemia"]
        bohemia = world.get_region("Bohemia")
        bohemia.controller = "France"
        world.invalidate_active_nations_cache()
        response = {"message": "Bohemia is secured."}
        M.executor._capture._maybe_mount_estate_choice(
            world, bohemia, "Ney", {"previous_controller": "Austria"}, response)
        pending = world.pending_capture_choice
        assert pending["estate_holder"] == "ArchdukeCharles"
        assert pending["estate_holder_title"] == "the Archduke Charles"
        assert "Sire — Bohemia sustains the Archduke Charles's household" in response["message"]
        assert "the fate of the Archduke Charles's estate" in CaptureExecutor._pending_prompt(pending)

    def test_the_crowned_name_abroad_is_the_emperor(self, shipped, monkeypatch):
        """NP-V's finding one surface over: a crowned Emperor named abroad."""
        from backend.game_logic import diplomatic_templates as DT
        from backend.game_logic import jealousy as J
        _, world = shipped
        monkeypatch.setattr(J, "get_crowned_marshal", lambda w, n: w.marshals["Napoleon"])
        for suffix in ("castlereagh", "hardenberg", "metternich", "einsiedel", "chancery"):
            line = DT.crowned_name_clause(world, "France", suffix)
            assert "the Emperor Napoleon" in line and "Marshal Napoleon" not in line, line
        assert "the Emperor Napoleon's laurels" in DT.crowned_incoming_clause(world, "France")

    def test_the_admiralty_takes_the_emperors_orders(self, shipped, monkeypatch):
        """SF7-X16: "The Admiralty takes its orders from the Emperor, Sire,
        not from the Emperor Napoleon in the field" — the Emperor is its
        master, as he is of the laws (`reforms_executor._misaddressed`)."""
        from backend.commands import naval_executor as NE
        _, world = shipped
        assert NE._admiralty_misaddressed({"marshal": "Napoleon"}, world, "France", "x") is None
        ney = NE._admiralty_misaddressed({"marshal": "Ney"}, world, "France", "x")
        assert "not from Marshal Ney in the field" in ney["message"]
        monkeypatch.setattr(NE, "THE_EMPEROR_COMMANDS_THE_ADMIRALTY", False)
        assert NE._admiralty_misaddressed({"marshal": "Napoleon"}, world, "France", "x") is not None

    def test_the_enemy_addressee_refusal_names_his_rank(self, shipped):
        _, world = shipped
        refusal = M.parser._enemy_addressee_refusal("ArchdukeCharles, attack Paris", world=world)
        assert refusal is not None
        assert refusal["error"].startswith("The Archduke Charles commands for Austria"), refusal["error"]


# ═══════════════ NPC-12 — the key never reaches the reader ═══════════════

# The measured producers (two 40-turn arms, the pre-slice tree) and the
# expressions in them that name an enemy — each must reach the reader
# through the humaniser. A dedupe key and a parsed command stay keys.
NPC12_PRODUCERS = {
    "backend/commands/strategic.py": (
        {"_respond_blocked_path", "_respond_combat_stalemate", "_handle_move_to_arrival",
         "_pursuit_engagement", "_execute_pursue", "_execute_hold", "_execute_hold_bombardment",
         "_condition_arms", "_handle_blocked_path", "_handle_combat_result"},
        {"enemy_name", "enemy.name", "target.name"}),
    "backend/commands/strategic_executor.py": (
        {"_execute_strategic_command", "_first_step_refusal", "_handle_first_step_blocked"},
        {"enemy_name", "enemy.name"}),
    "backend/game_logic/turn_manager.py": ({"_check_capital_proximity"}, {"enemy.name"}),
    "backend/game_logic/jealousy.py": (
        {"_command_option", "command_arm_availability", "_apply_command_choice"}, {"enemy.name"}),
    "backend/commands/combat_executor.py": (
        {"_resolve_last_stand_fight", "_apply_forced_retreat_or_break"},
        {"enemy_name", "marshal.name"}),
    "backend/models/world_state.py": (
        {"_process_reckless_cavalry_turn_start"}, {"enemy.name", "marshal.name"}),
}
NPC12_KEYS_THAT_STAY_KEYS = (
    'key = f"{enemy.name}|{region.name}"',
    'phrase = f"{marshal.name}, deal with {enemy.name}"',
)


class TestNPC12TheKeyNeverReachesTheReader:
    def test_the_producers_never_interpolate_a_bare_enemy_key(self):
        bare = []
        for rel, (funcs, exprs) in NPC12_PRODUCERS.items():
            src = (ROOT / rel).read_text(encoding="utf-8")
            lines = src.splitlines()
            tree = ast.parse(src)
            for fn in ast.walk(tree):
                if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) or fn.name not in funcs:
                    continue
                for node in ast.walk(fn):
                    if not isinstance(node, ast.JoinedStr):
                        continue
                    if any(k in lines[node.lineno - 1] for k in NPC12_KEYS_THAT_STAY_KEYS):
                        continue
                    for v in node.values:
                        if isinstance(v, ast.FormattedValue) and ast.unparse(v.value) in exprs:
                            bare.append(f"{rel}:{node.lineno} [{fn.name}] {{{ast.unparse(v.value)}}}")
        assert not bare, "an enemy name reaches the reader as a key:\n" + "\n".join(bare)

    def test_the_census_finds_a_bare_key_planted_in_a_producer(self):
        src = 'def _handle_blocked_path(self, enemy):\n    return f"{enemy.name} blocks the path"\n'
        tree = ast.parse(src)
        fstrings = [n for n in ast.walk(tree) if isinstance(n, ast.JoinedStr)]
        assert any(ast.unparse(v.value) == "enemy.name" for f in fstrings for v in f.values
                   if isinstance(v, ast.FormattedValue))

    def test_the_ledger_orders_tab_names_the_quarry(self, shipped):
        client, world = shipped
        ney = world.marshals["Ney"]
        ney.strategic_order = StrategicOrder(
            command_type="PURSUE", target="ArchdukeCharles", target_type="marshal",
            started_turn=int(world.current_turn), original_command="pursue ArchdukeCharles",
            path=[])
        ledger = client.get("/ledger").json()["ledger"]
        rows = [o for o in (ledger.get("orders") or [])
                if isinstance(o, dict) and o.get("marshal") == "Ney" and o.get("has_order")]
        assert rows, ledger.get("orders")
        assert rows[0]["target"] == "ArchdukeCharles"       # the machine key stays
        assert rows[0]["target_display"] == "Archduke Charles"

    def test_the_client_reads_the_display_target(self):
        gd = (ROOT / "godot-client" / "project-sovereign" / "scripts" / "strategic_ledger.gd").read_text(encoding="utf-8")
        assert gd.count('o.get("target_display", o.get("target", ""))') == 2

    @pytest.mark.parametrize("event,needle", [
        ({"type": "garrison_assault", "marshal": "ArchdukeCharles", "attacker_nation": "Austria",
          "region": "Milan", "garrison_losses": 500, "garrison_remaining": 1000,
          "attacker_losses": 700, "held": True}, "(Archduke Charles loses 700)"),
        ({"type": "garrison_assault", "marshal": "ArchdukeCharles", "attacker_nation": "Austria",
          "region": "Milan", "garrison_losses": 500, "garrison_remaining": 0,
          "attacker_losses": 700, "held": False}, "(Archduke Charles loses 700)"),
        ({"type": "garrison_placed", "marshal": "ArchdukeCharles", "region": "Franche-Comte",
          "troops": 3000}, "Archduke Charles garrisoned Franche-Comte"),
        ({"type": "last_stand", "marshal": "ArchdukeCharles", "location": "Tyrol",
          "casualties_inflicted": 900}, "Archduke Charles's last stand at Tyrol"),
    ])
    def test_the_campaign_logs_lines_speak_the_name(self, event, needle):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner(event, player_nation="France")
        assert needle in line and "ArchdukeCharles" not in line, line

    def test_berthiers_capital_alert_names_him(self, shipped):
        from backend.game_logic.turn_manager import TurnManager
        _, world = shipped
        paris = world.get_region("Paris")
        adj = sorted(paris.adjacent_regions)[0]
        charles = world.marshals["ArchdukeCharles"]
        charles.location = adj
        world._capital_proximity_last_alert = {}
        alerts = TurnManager(world)._check_capital_proximity()
        mine = [a for a in alerts if a.get("enemy") == "ArchdukeCharles"]
        assert mine, alerts
        assert "Archduke Charles (" in mine[0]["message"] and "ArchdukeCharles" not in mine[0]["message"]
        assert mine[0]["enemy"] == "ArchdukeCharles"  # the identity stays a key

    def test_the_enemy_phase_fields_the_census_skips_are_never_rendered(self):
        """The census's two exemptions are honest only while the client
        rebuilds every enemy-phase line from structured fields."""
        gd = (ROOT / "godot-client" / "project-sovereign" / "scripts" / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
        code = "\n".join(ln.split("#", 1)[0] for ln in gd.splitlines())
        assert 'get("summary"' not in code and 'get("message"' not in code
        assert '["summary"]' not in code and '.summary' not in code

    def test_the_census_reads_what_the_reader_reads(self):
        census = NC.NameCensus()
        census.keys = ["ArchdukeCharles", "ArchdukeJohn"]
        census.read({"message": "Ney pursues ArchdukeCharles at Bohemia."}, "POST /command")
        census.read({"marshal": "ArchdukeCharles", "command": "attack ArchdukeCharles",
                     "suggested_command": "pursue ArchdukeJohn", "dialogue_id": 3}, "POST /command")
        census.read({"enemy_phase": {"summary": ["ArchdukeCharles: wait"], "nations": {
            "Austria": {"actions": [{"message": "ArchdukeJohn holds position"}]}}}}, "POST /command")
        census.read({"turns": [{"events": [{"display": "The Archduke Charles WOUNDED"}]}]},
                    "GET /campaign_log")
        s = census.summary()
        assert s["leaks"] == 1 and s["by_field"][0]["path"] == "message", s
        assert s["display_seen"] == 1 and s["verdict"] == "FAIL"

    def test_a_census_that_never_met_the_names_says_so(self):
        census = NC.NameCensus()
        census.keys = ["ArchdukeCharles"]
        census.read({"message": "Ney holds Paris."}, "POST /command")
        assert census.summary()["verdict"].startswith("VACUOUS")

    def test_the_keys_are_derived_from_the_world(self, shipped):
        _, world = shipped
        assert NC.derive_keys(world) == ["ArchdukeCharles", "ArchdukeJohn"]

    def test_the_driven_census(self, tmp_path):
        """Twelve loops of the commanded arm, in-process with the census on:
        every rendered string, POST and GET — no roster key reaches the
        reader, and the arm did meet the names (else the verdict is VACUOUS)."""
        env = dict(os.environ, PYTHONHASHSEED="0", LLM_MODE="mock", SOVEREIGN_SEED="historical")
        env.pop("PYTHONIOENCODING", None)
        for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
            env.pop(key, None)
        env["INK_IRON_SAVE_DIR"] = str(tmp_path / "saves")
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "playtest_driver.py"), "--script", str(CMDH),
             "--turns", "12", "--seed", "historical", "--diplomacy", "accept",
             "--out", str(tmp_path), "--name", "names", "--name-census"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=1200, env=env, cwd=str(ROOT))
        meta_path = tmp_path / "names" / "meta.json"
        assert meta_path.is_file(), proc.stderr[-2000:]
        census = json.loads(meta_path.read_text(encoding="utf-8"))["name_census"]
        assert census["verdict"] == "PASS", census
        assert census["keys"] == ["ArchdukeCharles", "ArchdukeJohn"]
        assert census["display_seen"] > 0 and census["responses"] > 0
        assert census["by_method"].get("GET", 0) > 0, census["by_method"]  # the log, the ledger

    def test_the_census_is_off_by_default_and_reads_get_too(self):
        src = (ROOT / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        assert 'ap.add_argument("--name-census", action="store_true",' in src
        assert "transport.get_observers.append(names.observe_get)" in src


# ═══════════════ S5-4 — the queue overflows into the mailbox ═══════════════

def _letter(n):
    return {"type": "incoming_proposal", "blocking": False, "turn_created": 1,
            "options": [], "target_nation": f"Court{n}", "nation": f"Court{n}"}


class TestTheQueueOverflowsIntoTheMailbox:
    def _full(self):
        dm = DMOD.DialogueManager()
        dm.push(_letter("Active"))
        for i in range(dm.QUEUE_CAP):
            dm.push(_letter(i))
        assert dm.queue_size == dm.QUEUE_CAP
        return dm

    def test_an_arrival_past_the_cap_is_kept(self):
        dm = self._full()
        dm.push(_letter("Overflow"))
        assert dm.queue_size == dm.QUEUE_CAP + 1
        assert any(d.get("target_nation") == "CourtOverflow" for d in dm.iter_queue())
        assert dm.get_mailbox_count() == dm.QUEUE_CAP + 2

    def test_a_dialogue_displaced_at_the_cap_is_kept(self):
        dm = self._full()
        dm.preempt({"type": "war_purpose_selection", "blocking": True, "turn_created": 1,
                    "options": []})
        assert dm.queue_size == dm.QUEUE_CAP + 1
        assert any(d.get("target_nation") == "CourtActive" for d in dm.iter_queue())

    def test_lever_down_drops_as_before(self, monkeypatch):
        monkeypatch.setattr(DMOD, "THE_QUEUE_OVERFLOWS_INTO_THE_MAILBOX", False)
        dm = self._full()
        dm.push(_letter("Overflow"))
        dm.preempt({"type": "war_purpose_selection", "blocking": True, "turn_created": 1,
                    "options": []})
        assert dm.queue_size == dm.QUEUE_CAP
        names = {d.get("target_nation") for d in dm.iter_queue()}
        assert "CourtOverflow" not in names and "CourtActive" not in names


# ═══════════════ SF7-X7 — the peace names what each side keeps ═══════════════

def _stage_the_frontier(world):
    """Austria on French soil (Champagne, Burgundy), France in Bohemia."""
    for name, ctrl in (("Champagne", "Austria"), ("Burgundy", "Austria"), ("Bohemia", "France")):
        world.regions[name].controller = ctrl
    world.invalidate_active_nations_cache()


def _peace_dialogue(world, clauses=None):
    from backend.game_logic.diplomatic_dialogue import classify_diplomatic_intent, generate_dialogue
    data = {"target_nation": "Austria", "proposal_type": "peace",
            "raw_text": "propose peace with Austria", "has_diplomatic_keywords": True,
            "is_question": False, "clauses": clauses or []}
    with contextlib.redirect_stdout(io.StringIO()):
        return generate_dialogue(classify_diplomatic_intent(data, world), data, world)


class TestThePeaceNamesWhatEachSideKeeps:
    def test_the_proposal_warns_before_it_is_sent(self, shipped):
        _, world = shipped
        _stage_the_frontier(world)
        d = _peace_dialogue(world)
        summary = d.get("proposal_terms_summary", [])
        assert "Status quo: Bohemia stays ours by the treaty — titled." in summary, summary
        assert ("WARNING: Burgundy and Champagne stay with Austria by this peace — French "
                "soil behind a closed frontier once it is signed.") in summary, summary
        # named once — the warning carries the French soil, not a second line
        assert not any("stay Austrian by the treaty" in s for s in summary)

    def test_the_forecast_is_what_the_ratifier_titles(self, shipped):
        """shown == applied: the proposal's forecast and the retention pass
        the setter runs on signing read the same rule."""
        from backend.game_logic.diplomacy import set_diplomatic_state
        _, world = shipped
        _stage_the_frontier(world)
        forecast = GE.status_quo_forecast(world, "France", "Austria")
        with contextlib.redirect_stdout(io.StringIO()):
            set_diplomatic_state(world, "France", "Austria", "PEACE", reason="treaty_ratification")
        applied = GE.take_status_quo_titled(world, [world._make_diplo_key("France", "Austria")])
        as_set = lambda es: {(e["house"], e["ceder"], tuple(sorted((h, tuple(r)) for h, r in e["titled"].items())))
                             for e in es}
        assert forecast and as_set(forecast) == as_set(applied), (forecast, applied)

    def test_a_province_the_package_cedes_is_not_retained(self, shipped):
        _, world = shipped
        _stage_the_frontier(world)
        lines = GE.status_quo_forecast_lines(world, "France", "Austria", "France",
                                             moved={"Champagne"})
        assert lines["warnings"] == ["Burgundy stays with Austria by this peace — French soil "
                                     "behind a closed frontier once it is signed."], lines

    def test_the_morning_after_names_what_they_kept(self, shipped):
        from backend.game_logic.diplomacy import set_diplomatic_state
        _, world = shipped
        _stage_the_frontier(world)
        world.pending_dispatch_events = []
        with contextlib.redirect_stdout(io.StringIO()):
            set_diplomatic_state(world, "France", "Austria", "PEACE", reason="treaty_ratification")
        kinds = {e["type"]: e["template_vars"] for e in world.pending_dispatch_events
                 if e["type"].startswith("status_quo_")}
        assert kinds["status_quo_titled"]["provinces"] == "Bohemia"
        assert kinds["status_quo_conceded"] == {"provinces": "Burgundy and Champagne",
                                                "holder": "Austria", "count": 2}

    def test_a_truce_titles_nothing_and_says_nothing(self, shipped):
        from backend.game_logic.diplomatic_dialogue import classify_diplomatic_intent, generate_dialogue
        _, world = shipped
        _stage_the_frontier(world)
        data = {"target_nation": "Austria", "proposal_type": "armistice",
                "raw_text": "propose armistice with Austria", "has_diplomatic_keywords": True,
                "is_question": False, "clauses": []}
        with contextlib.redirect_stdout(io.StringIO()):
            d = generate_dialogue(classify_diplomatic_intent(data, world), data, world)
        assert "status_quo_forecast" not in d
        assert not any("Status quo" in s or "closed frontier" in s
                       for s in d.get("proposal_terms_summary", []))

    def test_lever_down_is_the_old_silence(self, shipped, monkeypatch):
        from backend.game_logic.diplomacy import set_diplomatic_state
        _, world = shipped
        _stage_the_frontier(world)
        monkeypatch.setattr(GE, "THE_PEACE_NAMES_WHAT_EACH_SIDE_KEEPS", False)
        d = _peace_dialogue(world)
        assert not any("closed frontier" in s or "Status quo" in s
                       for s in d.get("proposal_terms_summary", []))
        world.pending_dispatch_events = []
        with contextlib.redirect_stdout(io.StringIO()):
            set_diplomatic_state(world, "France", "Austria", "PEACE", reason="treaty_ratification")
        assert not any(e["type"] == "status_quo_conceded" for e in world.pending_dispatch_events)
