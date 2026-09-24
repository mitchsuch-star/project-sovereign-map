"""Row EP, slice F2 — "The display-name pass" (`docs/ENDGAME_PLAN.md` §1 F2).

Nine rows from the September 23, 2026 live review (`BUG_FIXES.md` §Live
Review), NPC-12's first slice — every one a string the engine printed in
its own vocabulary:

* **LV-2** — the scout report ("ArchdukeJohn (Austria)"), the covering
  lines ("ArchdukeCharles is EXPOSED!"), the diorama nameplate and the
  war-table piece label carried the roster KEY. The humaniser and the formed
  display name are the one source; the client gained `display_marshal_name`.
  Found while driving: the muster header ("vs ArchdukeJohn") — the same
  class, fixed with it.
* **LV-3** — "Treaty signed: PEACE → OPEN_BORDERS with Prussia." and "You
  have accepted Ottoman's proposal." — the state enums and the court's tag.
  The state table and the display name with its article; the popup payload
  carries `from_nation_display` and `choice_display` for the client's echo.
* **LV-4** — the strategic report's rows carried the enum and a `(s)`
  hedge, and the "[HINT]" tag; every row carries `command_display`, the
  count is an int, the plural agrees, the hint is a sentence.
* **LV-6** — an INCOMING offer carried acceptance hints written from
  France-as-proposer's viewpoint (the inverted sentence); both are blanked
  for incoming offers, the player's own previews keep theirs.
* **LV-9** — "1 unanswered envoy(s)" at fourteen client sites and two
  private backend helpers: ONE `display_names.plural`, ONE `Utils.plural`.
* **LV-10** — the enemy-phase capture lines say whom the province was
  taken from (" (was X)"), on both branches.
* **LV-11** — the report and the diorama showed the lead's strength BEFORE
  the advance's attrition; the toll is recorded and shown beside the locked
  figure ("22,181 → 21,863 after the advance"). The lock point stays.
* **LV-18** — "Personality (cautious) +16%" bundled two terms; each is its
  own labelled row, and their product is the applied modifier.
* **LV-19** — one arrow.

The client classes drive the REAL `main.tscn` headlessly
(`tools/ep_f2_display_name_harness.gd`) on payloads taken from the real
endpoints; they skip without the engine, and a skip is not a pass — which is
why every payload fact is also pinned engine-free above them.
"""

import ast
import contextlib
import io
import itertools
import json
import os
import pathlib
import random
import re
import subprocess

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import display_names as DN
from backend.commands.parser import CommandParser
from backend.game_logic import battle_report as BR
from backend.game_logic import diplomatic_dialogue as DD
from backend.game_logic import emergent_designs as ED
from backend.game_logic import mailbox_payloads as MP
from backend.models.marshal import Stance
from backend.models.personality_modifiers import get_defense_modifier_for_personality
from tests import _chip_census as C

REPO = C.REPO
PROJECT = C.PROJECT
SCRIPTS = C.SCRIPTS
SCENES = PROJECT / "scenes"
HARNESS = REPO / "tools" / "ep_f2_display_name_harness.gd"
BACKEND = REPO / "backend"

CAMEL = re.compile(r"\b[A-Z][a-z]+[A-Z][a-z]+\b")  # ArchdukeJohn, KingdomOfItaly


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


def _fresh():
    with _quiet():
        M._reset_world_state()
    M.parser = CommandParser(use_real_llm=False)
    return M.world, TestClient(M.app)


def _cmd(client, text):
    with _quiet():
        r = client.post("/command", json={"command": text})
    assert r.status_code == 200, (text, r.status_code, r.text[:300])
    return r.json()


def _incoming(nation, ptype):
    """The shape `ai_diplomacy._build_incoming_proposal_dialogue` produces,
    aimed at France (an AI offer's `target_nation` is the player)."""
    return {
        "type": "incoming_proposal",
        "target_nation": nation,
        "talleyrand_text": f"A proposal from {nation}.",
        "options": [
            {"label": "Accept", "action": "accept_ai_proposal"},
            {"label": "Reject", "action": "reject_ai_proposal"},
            {"label": "Counter-offer", "action": "counter_ai_proposal"},
        ],
        "context": {
            "proposal": {"type": ptype, "target_nation": "France"},
            "source_nation": nation,
            "acceptance_score": 90,
            "proposal_type": ptype,
        },
        "turn_created": 1,
        "blocking": False,
    }


def _payloads():
    out = {}
    # LV-2: the scout report and the adjacent scan.
    world, c = _fresh()
    out["scout"] = _cmd(c, "Murat, scout Tyrol")
    out["scan"] = _cmd(c, "Murat, scout")
    # LV-4: the hint — Ney at Munich steps to Franconia beside an empty,
    # Austrian, at-war Bohemia.
    world, c = _fresh()
    world.marshals["Ney"].location = "Munich"
    with _quiet():
        world.calculate_visibility()
    out["hint"] = _cmd(c, "Ney, move to Franconia")
    # LV-19 / LV-4: a march through French soil (no enemy on the road) and
    # the end turn that reports it.
    world, c = _fresh()
    out["route"] = _cmd(c, "Davout, march to Brittany")
    out["end_turn"] = _cmd(c, "end turn")
    # LV-3 / LV-6: an Ottoman open-borders offer accepted, then a PEACE offer
    # over it (the downgrade guard).
    world, c = _fresh()
    out["popup_ottoman"] = MP.build_pending_envoy_popup_from_terms(
        world, nation="Ottoman",
        terms={"type": "open_borders", "target_nation": "France"},
        acceptance={"components": {"diplomat_skill_bonus": -6, "relations": 4}})
    out["popup_prussia"] = MP.build_pending_envoy_popup_from_terms(
        world, nation="Prussia",
        terms={"type": "open_borders", "target_nation": "France"},
        acceptance_score=72)
    world.dialogue_manager.replace(_incoming("Ottoman", "open_borders"))
    with _quiet():
        out["accept"] = c.post("/respond_to_diplomatic_dialogue",
                               json={"choice": "accept"}).json()
    world.dialogue_manager.replace(_incoming("Ottoman", "peace"))
    with _quiet():
        out["downgrade"] = c.post("/respond_to_diplomatic_dialogue",
                                  json={"choice": "accept"}).json()
    # LV-11 / LV-2 (the muster header): the F3 staging — Archduke John cut
    # to 600 on Austrian Tyrol, every other Austrian corps at Vienna, so
    # Massena's attack destroys him, the province falls and the advance
    # runs its attrition.
    world, c = _fresh()
    world.marshals["ArchdukeJohn"].strength = 600
    for m in world.marshals.values():
        if m.nation == "Austria" and m.name != "ArchdukeJohn":
            m.location = "Vienna"
            m.strategic_order = None
    random.seed(7)
    out["capture"] = _cmd(c, "Massena, attack Archduke John")
    # LV-18: a cautious defender, in defensive stance, outnumbered.
    world, c = _fresh()
    world.marshals["ArchdukeJohn"].stance = Stance.DEFENSIVE
    for m in world.marshals.values():
        if m.nation == "Austria" and m.name != "ArchdukeJohn":
            m.location = "Vienna"
            m.strategic_order = None
    random.seed(3)
    out["defence"] = _cmd(c, "Massena, attack Archduke John")
    # LV-2: the covering lines — John retreated this turn, Charles beside him.
    world, c = _fresh()
    john = world.marshals["ArchdukeJohn"]
    charles = world.marshals["ArchdukeCharles"]
    charles.location = john.location
    charles.strategic_order = None
    john.retreated_this_turn = True
    random.seed(5)
    out["cover"] = _cmd(c, "Massena, attack Archduke John")
    return out


@pytest.fixture(scope="module")
def payloads():
    with pytest.MonkeyPatch.context() as mp:
        C.board_env(mp)
        prior = (M.world, M.game_state.get("world"), M.parser)
        try:
            return _payloads()
        finally:
            M.world, M.parser = prior[0], prior[2]
            M.game_state["world"] = prior[1]


# ═══════════════════════════════════════════════════════════════════════════
# LV-2 — the man's name, never his roster key
# ═══════════════════════════════════════════════════════════════════════════


class TestTheScoutReportNamesTheMan:

    def test_the_targeted_scout_names_the_man_and_the_court(self, payloads):
        msg = str(payloads["scout"]["message"])
        assert payloads["scout"]["success"] is True, msg
        assert "Archduke John (Austria): ~" in msg, msg
        assert "Controlled by Austria." in msg, msg
        assert "ArchdukeJohn" not in msg
        assert not CAMEL.search(msg), msg

    def test_the_adjacent_scan_names_the_controllers(self, payloads):
        msg = str(payloads["scan"]["message"])
        assert payloads["scan"]["success"] is True, msg
        assert "(Bavaria, " in msg and "(Switzerland, " in msg, msg
        assert not CAMEL.search(msg), msg
        # The structured rows keep the raw keys — the client's lookups do.
        intel = payloads["scan"]["events"][0]["intel"]
        assert any(row["controller"] == "Bavaria" for row in intel)


class TestTheCoveringLinesNameTheMen:

    def test_the_shield_line_names_both_men(self, payloads):
        msg = str(payloads["cover"]["message"])
        assert payloads["cover"].get("battle_report"), msg[:300]
        shield = "[Shield] Archduke Charles steps forward to cover Archduke John's retreat!"
        assert shield in msg, msg[:400]
        # The line and the quoted words beside it name the men. (The battle
        # narration further down — "ArchdukeCharles holds the line", the
        # [Terrain] line — is `game_logic/combat.py`'s, which has never
        # imported the humaniser: NPC-12's remaining census, recorded in
        # F2's landing record, not this slice's nine rows.)
        i = msg.index(shield)
        line = msg[i:msg.find("\n\n", i)]
        assert "ArchdukeCharles" not in line and "ArchdukeJohn" not in line, line

    def test_the_muster_header_names_the_man(self, payloads):
        # Found while driving this slice: "vs ArchdukeJohn (substantial force)".
        for key in ("capture", "defence", "cover"):
            msg = str(payloads[key]["message"])
            head = msg[msg.find("MUSTER"):msg.find("MUSTER") + 160]
            assert "vs Archduke John (" in head, head
            assert "ArchdukeJohn" not in head, head

    def test_the_humaniser_is_the_module_level_name_in_the_combat_executor(self):
        """The mover found on the way: a function-local import of the
        humaniser inside `_execute_attack` made the name local to the WHOLE
        function, so the covering lines above it raised UnboundLocalError on
        every AI attack against a corps that had just retreated — a moved
        BASELINE_SERIES with every F5 lever down. One module-level import,
        never a function-local one in this file."""
        tree = ast.parse((BACKEND / "commands" / "combat_executor.py").read_text(encoding="utf-8"))
        module_level = [n for n in tree.body if isinstance(n, ast.ImportFrom)
                        and n.module == "backend.display_names"
                        and any(a.name == "humanize_entity_name" for a in n.names)]
        assert module_level, "the module-level humaniser import is gone"
        # A function-local import that binds the BARE name makes it local to
        # the whole function; any use of the bare name on an earlier line
        # then raises. An aliased import (`as _hum`) binds a different name
        # and is harmless.
        shadows = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            local_imports = [
                sub.lineno for sub in ast.walk(node)
                if isinstance(sub, ast.ImportFrom) and sub.module == "backend.display_names"
                and any(a.name == "humanize_entity_name" and a.asname is None for a in sub.names)]
            if not local_imports:
                continue
            first_import = min(local_imports)
            early_uses = [sub.lineno for sub in ast.walk(node)
                          if isinstance(sub, ast.Name) and sub.id == "humanize_entity_name"
                          and isinstance(sub.ctx, ast.Load) and sub.lineno < first_import]
            if early_uses:
                shadows.append((node.name, first_import, early_uses[:3]))
            if node.name == "_execute_attack":
                shadows.append((node.name, "any local import at all", local_imports))
        assert shadows == [], shadows


# ═══════════════════════════════════════════════════════════════════════════
# LV-3 / LV-6 — the treaty prose and the envoy payload
# ═══════════════════════════════════════════════════════════════════════════


class TestTheTreatyProseIsPrinted:

    def test_accepting_an_offer_names_the_court_and_the_states(self, payloads):
        r = payloads["accept"]
        assert r["success"] is True, r
        assert r["message"] == (
            "You have accepted the Ottoman Empire's proposal. "
            "Treaty signed: Peace → Open Borders with the Ottoman Empire."), r["message"]

    def test_the_downgrade_guard_names_the_court_not_france(self, payloads):
        r = payloads["downgrade"]
        assert r["success"] is False, r
        assert r["message"] == (
            "The Ottoman Empire's terms could not be ratified: "
            "We already have Open Borders with the Ottoman Empire. "
            "A Peace treaty would be a downgrade."), r["message"]

    def test_the_popup_payload_carries_the_printed_court_and_the_answer_labels(self, payloads):
        ottoman = payloads["popup_ottoman"]
        assert ottoman["from_nation"] == "Ottoman"
        assert ottoman["from_nation_display"] == "the Ottoman Empire"
        assert ottoman["choice_display"]["accept"] == "accepted"
        assert ottoman["choice_display"]["reject"] == "declined"
        prussia = payloads["popup_prussia"]
        assert prussia["from_nation_display"] == "Prussia"  # no article


class TestTheIncomingHintsAreBlank:

    def test_an_incoming_offer_carries_no_acceptance_hints(self, payloads):
        for key in ("popup_ottoman", "popup_prussia"):
            assert payloads[key]["acceptance_hint"] == ""
            assert payloads[key]["rejection_hint"] == ""

    def test_the_players_own_preview_still_speaks(self):
        """The hint builder the own-preview route calls is untouched."""
        good, bad = MP.build_acceptance_hints(
            {"components": {"diplomat_skill_bonus": -6, "relations": 4}})
        assert good and bad and good != bad


# ═══════════════════════════════════════════════════════════════════════════
# LV-4 / LV-9 / LV-19 — the strategic report, the hint, the plural, the arrow
# ═══════════════════════════════════════════════════════════════════════════


class TestTheStrategicReportCopy:

    def test_every_row_carries_the_printed_order_name(self, payloads):
        rows = payloads["end_turn"].get("strategic_reports") or []
        assert rows
        for row in rows:
            assert "command_display" in row, row
            if row.get("command") == "MOVE_TO":
                assert row["command_display"] == "March", row
            assert isinstance(row.get("turns_remaining"), int), row

    def test_the_count_and_the_noun_agree(self, payloads):
        rows = payloads["end_turn"].get("strategic_reports") or []
        davout = next(r for r in rows if r.get("marshal") == "Davout")
        n = davout["turns_remaining"]
        assert f"({DN.plural(n, 'turn')} remaining)." in davout["message"], davout
        assert "(s)" not in davout["message"]

    def test_a_single_turn_reads_singular(self, payloads):
        from backend.commands import strategic as S
        from backend.models.marshal import StrategicOrder
        world = M.world
        order = StrategicOrder(command_type="MOVE_TO", target="Brittany", target_type="region",
                               started_turn=int(world.current_turn), original_command="test")
        order.path = ["Brittany"]
        assert S.order_turns_remaining(order, int(world.current_turn)) == 1
        assert DN.plural(S.order_turns_remaining(order, int(world.current_turn)), "turn") == "1 turn"

    def test_the_hint_is_a_sentence(self, payloads):
        msg = str(payloads["hint"]["message"])
        assert payloads["hint"]["success"] is True, msg
        assert "Bohemia lies undefended — an attack takes it." in msg, msg
        assert "[HINT]" not in msg


class TestTheRouteUsesOneArrow:

    def test_the_march_route_is_joined_by_the_one_arrow(self, payloads):
        msg = str(payloads["route"]["message"])
        assert payloads["route"]["success"] is True, msg
        assert "Route: " in msg, msg
        assert " → " in msg and " -> " not in msg, msg

    def test_the_materiel_capture_line_uses_the_one_arrow(self):
        src = (BACKEND / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        assert "Captured: {old_controller} -> {marshal.nation}" not in src
        assert src.count("Captured: {old_controller} → {marshal.nation}") == 2


class TestThePluralHelper:

    @pytest.mark.parametrize("n,noun,expect", [
        (1, "turn", "1 turn"), (2, "turn", "2 turns"), (0, "turn", "0 turns"),
        (1, "envoy", "1 envoy"), (3, "envoy", "3 envoys"),
        (1, "unanswered envoy", "1 unanswered envoy"), (2, "unanswered envoy", "2 unanswered envoys"),
        (2, "more port", "2 more ports"), (1, "petition", "1 petition"), (4, "petition", "4 petitions"),
        (2, "march", "2 marches"), (2, "sail", "2 sail"), (5, "man", "5 men"),
    ])
    def test_the_count_and_the_noun_agree(self, n, noun, expect):
        assert DN.plural(n, noun) == expect

    def test_the_two_private_helpers_are_absorbed(self):
        assert ED._turns(1) == "1 turn" and ED._turns(3) == "3 turns"
        assert DD._plural(1, "turn") == "1 turn" and DD._plural(2, "province") == "2 provinces"


# ═══════════════════════════════════════════════════════════════════════════
# LV-11 / LV-18 — the advance's toll and the split defence line
# ═══════════════════════════════════════════════════════════════════════════


def _lead_cards(diorama):
    found = []
    stack = [diorama]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if node.get("lead") is True:
                found.append(node)
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return found


class TestTheAdvanceTollIsBesideTheLockedFigure:

    def test_the_report_records_the_advance(self, payloads):
        r = payloads["capture"]
        assert r.get("pending_capture_choice") is True, r.get("message")
        cs = r["battle_report"]["casualty_summary"]
        assert cs["attacker_advance_losses"] > 0, cs
        assert cs["attacker_after_advance"] == cs["attacker_remaining"] - cs["attacker_advance_losses"], cs
        # The lock point did not move: the locked figure is still the battle's.
        assert cs["attacker_remaining"] == cs["attacker_original"] - cs["attacker_casualties"], cs

    def test_the_lead_card_carries_the_same_toll(self, payloads):
        r = payloads["capture"]
        leads = {c["name"]: c for c in _lead_cards(r["battle_diorama"])}
        cs = r["battle_report"]["casualty_summary"]
        assert leads["Massena"]["advance_losses"] == cs["attacker_advance_losses"]
        assert leads["Massena"]["after_advance"] == cs["attacker_after_advance"]
        assert "after_advance" not in leads["ArchdukeJohn"]

    def test_a_battle_without_an_advance_stamps_nothing(self, payloads):
        cs = payloads["defence"]["battle_report"]["casualty_summary"]
        assert "attacker_advance_losses" not in cs or cs["attacker_advance_losses"] > 0


class TestTheDefenceLineIsSplit:

    def test_the_two_terms_are_their_own_rows(self, payloads):
        mods = payloads["defence"]["battle_report"]["modifier_breakdown"]["defender"]
        by_label = {m["label"]: m for m in mods}
        assert by_label["Personality (cautious)"]["value"] == 5, mods
        assert by_label["Outnumbered (cautious)"]["value"] == 10, mods
        assert all(m["value"] != 16 for m in mods), mods

    def test_the_labelled_product_is_the_applied_modifier(self):
        """Over every cell of the grid, the product of the labelled rows IS
        the modifier the combat math multiplies."""
        for personality, stance, outnumbered, holding in itertools.product(
                ("aggressive", "cautious", "literal", "sovereign", "unknown"),
                ("neutral", "defensive", "aggressive"), (False, True), (False, True)):
            applied = get_defense_modifier_for_personality(personality, stance, outnumbered, holding)
            product = 1.0
            for _label, pct, kind in BR.defense_personality_components(
                    personality, stance, outnumbered, holding):
                product *= (1.0 + pct / 100.0) if kind == "bonus" else (1.0 - pct / 100.0)
            assert abs(product - applied) < 1e-9, (personality, stance, outnumbered, holding, product, applied)


# ═══════════════════════════════════════════════════════════════════════════
# The census pins — NPC-12's sites, the `(s)` hedge, the client mirror
# ═══════════════════════════════════════════════════════════════════════════


def _string_constants(tree):
    """Every string literal that could reach a player: f-string pieces and
    plain constants that are not docstrings."""
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                docstrings.add(id(body[0].value))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            out.append((node.lineno, node.value))
    return out


_PLURAL_ALLOWLIST = {
    "backend/ai/parser_eval.py",            # the developer CLI's own help and summary
    "backend/ai/providers.py",              # the LLM tool schema, never shown to the player
    "backend/game_logic/settlement_helpers.py",  # validator errors for the modder
    "backend/game_logic/formations.py",     # validator errors for the modder
    "backend/modding/validator.py",
}


class TestTheCensus:

    def test_no_raw_marshal_key_reaches_a_player_string_in_the_movement_executor(self):
        """NPC-12's census, the movement executor: no `{m.name}` /
        `{enemy_marshal.name}` f-string piece anywhere in the file."""
        tree = ast.parse((BACKEND / "commands" / "movement_executor.py").read_text(encoding="utf-8"))
        raw = []
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                for piece in node.values:
                    if isinstance(piece, ast.FormattedValue) and isinstance(piece.value, ast.Attribute) \
                            and piece.value.attr == "name" and isinstance(piece.value.value, ast.Name) \
                            and piece.value.value.id in ("m", "enemy_marshal"):
                        raw.append(node.lineno)
        assert raw == [], raw

    def test_no_raw_marshal_key_in_the_covering_builder(self):
        """The two PLAYER strings the builder composes (`covering_message`)
        read the humanised names; the `print` beside them is the console's."""
        src = (BACKEND / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        start = src.index("ALLY COVERS RETREAT SYSTEM")
        end = src.index("_exp_wins_before = {", start)
        block = src[start:end]
        assert "[Shield] {covering_ally.name}" not in block
        assert "[Shield] {_cover_name} steps forward to cover {_covered_name}'s retreat!" in block
        assert "{enemy_marshal.name} is EXPOSED" not in block
        assert "{humanize_entity_name(enemy_marshal.name)} is EXPOSED" in block

    def test_no_plural_hedge_in_a_backend_player_string(self):
        offenders = []
        for path in sorted(BACKEND.rglob("*.py")):
            rel = path.relative_to(REPO).as_posix()
            if rel in _PLURAL_ALLOWLIST:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for lineno, text in _string_constants(tree):
                if "(s)" in text:
                    offenders.append(f"{rel}:{lineno}: {text[:60]!r}")
        assert offenders == [], "\n".join(offenders)

    def test_no_plural_hedge_in_a_client_string(self):
        offenders = []
        for folder in (SCRIPTS, SCENES):
            for path in sorted(folder.glob("*.gd")):
                for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    for literal in re.findall(r'"((?:[^"\\]|\\.)*)"', line):
                        if "(s)" in literal:
                            offenders.append(f"{path.name}:{lineno}: {literal[:60]!r}")
        assert offenders == [], "\n".join(offenders)

    def test_the_client_mirror_exists(self):
        src = (SCRIPTS / "utils.gd").read_text(encoding="utf-8")
        assert "static func plural(n: int, noun: String) -> String:" in src
        assert "static func display_marshal_name(name: String) -> String:" in src


# ═══════════════════════════════════════════════════════════════════════════
# The client, DRIVEN
# ═══════════════════════════════════════════════════════════════════════════


def _enemy_phase():
    """The dialog's own payload shape: one conquest event and one field-
    battle capture, both stamped `captured_from`."""
    return {
        "total_actions": 2,
        "nations": {
            "Austria": {
                "action_count": 2,
                "actions": [
                    {
                        "success": True,
                        "nation": "Austria",
                        "ai_action": {"marshal": "ArchdukeCharles", "action": "attack",
                                      "target": "Carniola"},
                        "events": [{"type": "conquest", "marshal": "ArchdukeCharles",
                                    "region": "Carniola", "capture_choice": "secure",
                                    "captured_from": "Bavaria"}],
                    },
                    {
                        "success": True,
                        "nation": "Austria",
                        "ai_action": {"marshal": "ArchdukeCharles", "action": "attack",
                                      "target": "Deroy"},
                        "events": [{
                            "type": "battle",
                            "battle_name": "Battle of Bohemia",
                            "attacker": {"name": "ArchdukeCharles", "casualties": 1000,
                                         "remaining": 50000, "morale": 80},
                            "defender": {"name": "Deroy", "casualties": 5000,
                                         "remaining": 15000, "morale": 50},
                            "outcome": "attacker_victory", "victor": "ArchdukeCharles",
                            "region_conquered": True, "region_name": "Bohemia",
                            "captured_from": "Bavaria", "capture_choice": "secure",
                        }],
                    },
                ],
            }
        },
    }


def _report_rows():
    return [
        {"marshal": "Davout", "command": "MOVE_TO", "command_display": "March",
         "order_status": "active", "destination": "Brittany", "turns_remaining": 1,
         "message": "Davout is marching to Brittany (1 turn remaining)."},
        {"marshal": "Soult", "command": "MOVE_TO", "command_display": "March",
         "order_status": "active", "destination": "Vienna", "turns_remaining": 3,
         "message": "Soult is marching to Vienna (3 turns remaining)."},
        # A JSON float — the "2.0 turns remaining" the review read.
        {"marshal": "Murat", "command": "PURSUE", "command_display": "Pursue",
         "order_status": "active", "destination": "ArchdukeCharles", "turns_remaining": 2.0,
         "message": "Murat is pursuing Archduke Charles (2 turns remaining)."},
    ]


@pytest.fixture(scope="module")
def driven(payloads, tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    work = tmp_path_factory.mktemp("epf2")
    out = work / "out.json"
    log = work / "godot.log"
    spec = work / "spec.json"
    spec.write_text(json.dumps({
        "enemy_phase": _enemy_phase(),
        "strategic_reports": _report_rows(),
        "reports": {"capture": payloads["capture"]["battle_report"],
                    "defence": payloads["defence"]["battle_report"]},
        "diorama": payloads["capture"]["battle_diorama"],
        "out": str(out),
    }), encoding="utf-8")
    env = dict(os.environ, EPF2_SPEC=str(spec))
    proc = subprocess.run(
        [exe, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=300, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    assert "error" not in result, result.get("error")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["script_errors"] = text.count("SCRIPT ERROR")
    return result


class TestTheHarnessIsParsed:

    def test_the_harness_is_in_the_parse_check(self):
        src = (REPO / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        assert "res://../../tools/ep_f2_display_name_harness.gd" in src


class TestTheEnemyPhaseSaysWhomItWasTakenFrom:

    def test_the_harness_ran_clean(self, driven):
        assert driven["script_errors"] == 0

    def test_both_capture_branches_name_the_loser(self, driven):
        text = driven["enemy_text"]
        assert "Region captured: Carniola (was Bavaria) (secured)" in text, text
        assert "Bohemia CAPTURED! (was Bavaria) (secured)" in text, text
        assert "ArchdukeCharles" not in text, text


class TestTheReportRowsRender:

    def test_the_printed_order_name_and_the_agreeing_count(self, driven):
        text = driven["report_popup_text"]
        assert "Davout (March)" in text, text
        assert "(1 turn remaining)" in text, text
        assert "(3 turns remaining)" in text, text
        assert "(2 turns remaining)" in text and "2.0" not in text, text
        assert "Destination: Archduke Charles" in text, text
        assert "MOVE_TO" not in text and "(s)" not in text, text


class TestTheClientHelpers:

    def test_the_plural_mirror_agrees_with_the_backend(self, driven):
        for key, value in driven["plural"].items():
            n, noun = key.split(" ", 1)
            assert value == DN.plural(int(n), noun), (key, value)

    def test_the_marshal_name_sibling(self, driven):
        assert driven["display_marshal_name"]["ArchdukeCharles"] == "Archduke Charles"
        assert driven["display_marshal_name"]["Ney"] == "Ney"


class TestBerthierOnTheTerminal:

    def test_the_strength_line_carries_the_advance_and_the_one_arrow(self, driven, payloads):
        text = driven["berthier_terminal"]["capture"]
        cs = payloads["capture"]["battle_report"]["casualty_summary"]
        after = f"{cs['attacker_after_advance']:,}"
        assert f"→ {after} after the advance" in text, text
        assert " -> " not in text, text

    def test_the_defence_line_is_split_on_screen(self, driven):
        text = driven["berthier_terminal"]["defence"]
        assert "Personality (cautious) +5%" in text, text
        assert "Outnumbered (cautious) +10%" in text, text
        assert "+16%" not in text, text


class TestTheDioramaLeadCard:

    def test_the_lead_card_shows_the_advance_and_the_printed_names(self, driven, payloads):
        labels = driven["diorama_labels"]
        cs = payloads["capture"]["battle_report"]["casualty_summary"]
        after = f"{cs['attacker_after_advance']:,}"
        assert any(f"→ {after} after the advance" in label for label in labels), labels
        assert any(label.startswith("Archduke John") for label in labels), labels
        assert not any("ArchdukeJohn" in label for label in labels), labels
