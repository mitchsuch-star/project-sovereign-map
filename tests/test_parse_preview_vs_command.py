"""UI-6 "The readback" — THE /command CENSUS (Session UI-6, November 13, 2026;
`docs/SYSTEMS_REFERENCE.md` §217).

`GET /parse_preview` mirrors only the pure stages of `/command`; this module
is what catches the mirror drifting. For every line below, on a fresh copy of
the shipped 1805 board, the readback is asked FIRST and the real `POST
/command` sent SECOND (the board the readback read is the board the order
met), and the two must agree:

  1. the reading names the marshal, the action and the target the executor's
     own parse named (its trace row, `trace: true`);
  2. an order TAKEN cost exactly the actions the reading quoted
     (`action_info.cost`, ACH-1's honest figure);
  3. a reading the state probe refused was refused at no cost (CRT-9's
     relation, extended to typed lines);
  4. an attack the reading said "asks first" was asked, free (DDB-R1), and
     its yes cost exactly the quoted pursuit;
  5. a reading of objection "none" drew no objection (the mood roll pinned
     flat, defiance 0 — the `_board` recipe of the ACH-1 census).

The lines: the golden corpus's addressed lines (1805 + any), the first two per
screen verb and every standing-order line, plus CRT-9's boot lines and the
readback's own showcase lines — and (the doctrine, November 13, 2026) the
fogged-name lines: twenty shapes × three commanders the boot keeps out of
sight. A man out of sight is read as `/command` reads him, so those lines are
compared like any other, and on them three more rules hold:

  6. a reading that refuses (or asks after an unknown word) met a `/command`
     that spent nothing and fought nothing;
  7. the doctrine's words agree: "no intelligence on his position" and the
     enemy addressee's "commands for <court>" are read as such;
  8. no reading carries his province or a figure of his corps.

Pure Python, in-process (one module, one worker — the parallel lanes keep it
apart from `test_parse_preview.py`).
"""

import contextlib
import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.commands.defiance as DEF
import backend.main as M
from backend.commands import executor as executor_mod
from backend.commands import objection_v2 as ov2
from backend.commands import parse_preview as PP
from backend.commands import strategic_executor as se_mod
from backend.commands.parser import CommandParser
from backend.display_names import humanize_entity_name
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "tests" / "data" / "parser_golden_corpus.json"

SCREEN_VERBS = ("attack", "move", "scout", "fortify", "unfortify", "drill", "defend",
                "hold", "retreat", "support", "garrison", "pursue")
CRT9_LINES = [
    "Davout, attack Mack", "Davout, scout Swabia", "Davout, fortify", "Davout, unfortify",
    "Davout, drill", "Davout, defend", "Davout, move to Lorraine", "Davout, march to Paris",
    "Davout, pursue Mack", "Davout, hold", "Davout, support Ney", "Davout, retreat",
    "Davout, garrison",
]
SHOWCASE_LINES = [
    "Ney, attack Mack", "Ney, march to Vienna", "Ney, march to Swabia then attack Mack",
    "Soult, support Davout", "Ney, follow Davout", "Ney, hold", "Lannes, scout Swabia",
    "Murat, attack Mack", "Massena, attack Archduke John", "Bernadotte, attack Mack",
    "Ney, attack Brunswick", "Ney, atack Mack", "Lannes, drill", "Soult, fortify",
    "Ney, if Mack is still in Swabia, attack him", "Ney, if Mack is still in Lorraine, attack him",
    "Ney, fortify, attack Mack",
    # DDB-R1's ask: a typed attack out of reach (Archduke John at Tyrol)
    "Ney, attack Archduke John", "Lannes, attack Archduke John", "Soult, attack Archduke John",
    # A17 (UI6-X37, X38): a title two commanders share, a court at peace beyond reach
    "Ney, attack Archduke", "Ney, attack the archduke", "Ney, attack Zezschwitz",
    "Ney, hold Bernardim Freire", "Ney, retreat to Mack", "all corps retreat to Mack",
    # A18 (UI6-X41 … X46): the consequence connectives take the `then` road, a
    # commander is no retreat object, a compound subject's pronoun, the guns
    "Murat, charge Mack so attack Kutuzov", "Murat, charge Mack and attack Kutuzov",
    "Ney, march to Lorraine so attack Mack", "Ney, hold Lorraine so retreat",
    "Ney, hold Lorraine retreat", "Ney, hold Lorraine so attack Kutuzov",
    "Ney, retreat Kutuzov", "Ney, retreat from Mack", "Ney, fall back Kutuzov",
    "Ney, withdraw from Mack", "Ney, retreat to Archduke",
    "Ney, Kutuzov and Mack are coming so attack him", "Ney, Mack and Kutuzov are coming so attack them",
    "Ney, hold Lorraine so Mack and Kutuzov can't pass",
    "Ney, Brunswick is marching so pursue him", "Ney, Brunswick is marching so scout him",
    "Lannes, bombard Podolia", "Lannes, bombard Kutuzov", "Lannes, bombard Moore",
]


# The doctrine's lines: the fogged commanders of the 1805 boot (Kutuzov at
# Podolia, Moore at London, the Archduke Charles at Carniola) in the shapes
# the fog pins of `test_parse_preview.py` read.
HIDDEN = ("Kutuzov", "Moore", "ArchdukeCharles")
FOG_TEMPLATES = [
    "Ney, attack {X}", "Ney, pursue {X}", "Ney, march to Vienna then attack {X}",
    "{X}, attack Mack", "{X} retreat", "Ney, attack {T}", "what if Ney attacks {X}",
    "where is {X}", "if {X} is still in Swabia, attack him", "Ney, deal with {X}",
    "Ney, support {X}", "Attack Marshal {X}", "Davout, hold Lorraine until {X} arrives",
    # A15 (UI6-X14 … X20): the delegation's other arms, the marshal-less
    # attack and scout, the hold, the follow and the charge
    "Bernadotte, deal with {X}", "Soult, deal with {X}", "everyone attack {X}",
    "Davout, hold {X}", "Ney, follow {X}", "scout {X}", "Murat, charge {X}",
    # A16 (UI6-X25, X26): the stationary verbs and recruit aimed at a
    # commander, the second name of a list, the collective's other verbs
    "Davout, defend {X}", "Davout, fortify {X}", "Davout, recruit at {X}",
    "Ney, attack Mack and {X}", "everyone pursue {X}", "everyone march to {X}",
    "everyone hold {X}",
    # A17 (UI6-X33 … X39): a purpose tail, the list beside a place or a friend,
    # the pronoun's referent, the retreat's destination and its reason
    "Ney, hold Lorraine so {X} can't pass", "Ney, march to Lorraine so {X} can't pass",
    "Ney, support Davout and {X}", "Ney, hold Lorraine and {X}",
    "Ney, {X} is attacking Swabia so attack him", "Ney, retreat to {X}",
    "Ney, retreat for {X}", "all corps retreat to {X}", "Ney, march to Swabia and {X}",
]


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _fog_lines():
    lines = {}
    for name in HIDDEN:
        shown = humanize_entity_name(name)
        typo = shown[:-1] + ("q" if shown[-1].lower() != "q" else "z")
        for template in FOG_TEMPLATES:
            lines[template.format(X=shown, T=typo)] = name
    return lines


def _census_lines():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))["entries"]
    addressed = sorted((e for e in corpus if e.get("world") in ("1805", "any")
                        and "," in e["utterance"]), key=lambda e: e["id"])
    picked, per_verb, strategic = [], {}, 0
    for e in addressed:
        expected = e.get("expected") or {}
        action = expected.get("action")
        if expected.get("strategic_type"):
            if strategic < 20:
                strategic += 1
                picked.append(e["utterance"])
            continue
        if action in SCREEN_VERBS and per_verb.get(action, 0) < 2:
            per_verb[action] = per_verb.get(action, 0) + 1
            picked.append(e["utterance"])
    seen, lines = set(), []
    for line in picked + CRT9_LINES + SHOWCASE_LINES + list(_fog_lines()):
        if line not in seen:
            seen.add(line)
            lines.append(line)
    return lines


def _fog_disagreements(line, name, world, pre, reply):
    """Rules 6–8 on a line naming a man out of sight."""
    out = []
    man = world.marshals[name]
    shown = humanize_entity_name(name)
    message = str(reply.get("message") or "")
    spent = _cost(reply)
    if pre["kind"] in ("refusal", "unknown_name"):
        if spent or reply.get("battle_report") or reply.get("muster_preview"):
            out.append((line, "refused, yet spent or fought", spent, message[:120]))
    if f"No intelligence on {shown}'s position" in message and not (
            pre["kind"] == "refusal" and f"No intelligence on {shown}’s position" in pre["refusal"]):
        out.append((line, "no intelligence", pre["kind"], pre["refusal"]))
    if " commands for " in message and "does not answer to us" in message and not (
            pre["kind"] == "refusal" and "he does not answer to us" in pre["refusal"]):
        out.append((line, "enemy addressee", pre["kind"], pre["refusal"]))
    body = json.dumps({k: v for k, v in pre.items() if k != "line"})
    strength = int(man.strength)
    for leak in (man.location, str(strength), f"{strength:,}"):
        if leak in body:
            out.append((line, "a figure of his rides the reading", leak))
    return out


@pytest.fixture(scope="module")
def census_board():
    mp = pytest.MonkeyPatch()
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        mp.delenv(key, raising=False)
    mp.setenv("LLM_MODE", "mock")

    def flat(concern):
        return concern
    for mod in (executor_mod, se_mod, ov2):
        mp.setattr(mod, "apply_mood_variance", flat)
    mp.setattr(DEF, "calculate_defiance_chance", lambda *a, **k: 0.0)
    prior = (M.world, M.game_state.get("world"), M.parser)
    with _quiet():
        M._reset_world_state()
    snap = json.dumps(M.world.to_dict(), default=str)
    try:
        # one portal for the module (a `with` block): a bare TestClient opens a fresh
        # event loop and socket pair per request, and the censuses post thousands
        # of lines (WinError 10055 under the hook's parallel load)
        with TestClient(M.app) as client:
            yield client, snap
    finally:
        M.world, M.parser = prior[0], prior[2]
        M.game_state["world"] = prior[1]
        PP.invalidate()
        mp.undo()


def _fresh(snap):
    with _quiet():
        world = WorldState.from_dict(json.loads(snap))
        M._set_active_world(world)
        M.parser = CommandParser(use_real_llm=False)
    PP.invalidate()
    return world


def _parse_row(reply):
    for row in reply.get("parse_trace") or []:
        if row.get("stage") == "parse" and row.get("rule") == "result":
            return row.get("detail") or {}
    return {}


def _cost(reply):
    info = reply.get("action_info")
    return int(info.get("cost") or 0) if isinstance(info, dict) else 0


def _asked(reply):
    return bool(reply.get("state") == "awaiting_clarification"
                or reply.get("pending_objection") or reply.get("pending_strategic_objection")
                or reply.get("pending_interrupt") or reply.get("clarification"))


def _taken(reply):
    return bool(reply.get("success")) and not _asked(reply)


def test_the_readback_agrees_with_the_order_it_reads(census_board):
    client, snap = census_board
    lines = _census_lines()
    fog = _fog_lines()
    assert len(lines) >= 45 + len(fog) - 2, len(lines)
    disagreements = []
    checked = {"orders": 0, "taken": 0, "refused": 0, "asked": 0, "quiet": 0, "fog": 0}
    for line in lines:
        world = _fresh(snap)
        with _quiet():
            pre = client.get("/parse_preview", params={"line": line}).json()
            reply = client.post("/command", json={"command": line, "trace": True}).json()
        row = _parse_row(reply)
        if pre["kind"] in ("pending", "secretary", "busy"):
            disagreements.append((line, "void", pre["kind"]))
            continue
        if line in fog:
            checked["fog"] += 1
            disagreements += _fog_disagreements(line, fog[line], world, pre, reply)
        if pre["kind"] == "order" and pre["marshal"]:
            checked["orders"] += 1
            if row.get("marshal") and humanize_entity_name(row["marshal"]) != pre["marshal"]:
                disagreements.append((line, "marshal", row.get("marshal"), pre["marshal"]))
            if row.get("action") and row["action"] != pre["action"]:
                disagreements.append((line, "action", row.get("action"), pre["action"]))
            if (pre["target_kind"] in ("enemy", "friendly", "province") and row.get("target")
                    and humanize_entity_name(row["target"]) != pre["target"]):
                disagreements.append((line, "target", row.get("target"), pre["target"]))
            if pre["asks_first"]:
                checked["asked"] += 1
                if not (reply.get("state") == "awaiting_clarification" and _cost(reply) == 0):
                    disagreements.append((line, "asks first", reply.get("message", "")[:120]))
                else:
                    before = int(world.actions_remaining)
                    with _quiet():
                        yes = client.post("/command", json={"command": "yes"}).json()
                    spent = before - int(world.actions_remaining)
                    if spent != pre["ap"]:
                        disagreements.append((line, "asked price", pre["ap"], spent,
                                              yes.get("message", "")[:120]))
            elif _taken(reply):
                checked["taken"] += 1
                if _cost(reply) != pre["ap"]:
                    disagreements.append((line, "price", pre["ap"], _cost(reply),
                                          reply.get("message", "")[:120]))
            if pre["objection"] == "none" and (reply.get("pending_objection")
                                               or reply.get("pending_strategic_objection")):
                disagreements.append((line, "objection", reply.get("message", "")[:120]))
        elif pre["kind"] == "refusal" and pre["marshal"] == "" and " — " in (pre["refusal"] or ""):
            checked["refused"] += 1
            if _taken(reply) and _cost(reply) > 0:
                disagreements.append((line, "refusal", pre["refusal"], reply.get("message", "")[:120]))
        elif pre["kind"] == "refusal":
            checked["refused"] += 1
            # The probe's own short reasons (fog-honest): never a SPENT order.
            if _taken(reply) and _cost(reply) > 0:
                disagreements.append((line, "refusal", pre["refusal"], reply.get("message", "")[:120]))
        else:
            checked["quiet"] += 1
    assert disagreements == [], disagreements
    assert checked["orders"] >= 30 and checked["taken"] >= 15, checked
    assert checked["asked"] >= 3 and checked["refused"] >= 5, checked
    assert checked["fog"] == len(fog), checked


# ── UI6-X29: the charge and the guns, ARMED (the flat board arms neither) ──

def _arm(world):
    world.marshals["Murat"].recklessness = 80
    lannes = world.marshals["Lannes"]
    lannes.cavalry = False
    lannes.artillery = True


ARMED_LINES = [
    # (line, readback refuses)
    ("Murat, charge", True), ("Murat, charge the Austrians", True),
    ("Murat, charge Podolia", True), ("Murat, charge London", True),
    ("Murat, charge Moravia", True), ("Murat, charge Bohemia", True),
    ("Murat, charge Kutuzov", True), ("Murat, charge Mack", False),
    ("Murat, charge Swabia", False),
    ("Ney, bombard", True), ("Ney, bombard Mack", True),
    ("Lannes, bombard Mack", False), ("Lannes, bombard Kutuzov", True),
    ("Lannes, bombard", False),
    # A17 (UI6-X38): guns at a province beyond their reach, a charge at a court
    ("Lannes, bombard Podolia", True), ("Lannes, bombard Carniola", True),
    ("Murat, charge Bavaria", True),
]


def test_the_armed_charge_and_the_guns_are_read_as_command_takes_them(census_board):
    client, snap = census_board
    disagreements = []
    for line, refuses in ARMED_LINES:
        world = _fresh(snap)
        _arm(world)
        PP.invalidate()
        with _quiet():
            pre = client.get("/parse_preview", params={"line": line}).json()
        world = _fresh(snap)
        _arm(world)
        with _quiet():
            reply = client.post("/command", json={"command": line}).json()
        if refuses:
            if pre["kind"] != "refusal":
                disagreements.append((line, "readback priced a refused order", pre["kind"]))
            if _taken(reply) or _cost(reply):
                disagreements.append((line, "command took it", reply.get("message", "")[:100]))
        else:
            if pre["kind"] != "order" or not _taken(reply) or _cost(reply) != pre["ap"]:
                disagreements.append((line, "order", pre["kind"], pre["ap"], _cost(reply),
                                      reply.get("message", "")[:100]))
    assert disagreements == [], disagreements


# ── UI6-X46: a marshal with no guns — one answer, in both ──────────────────

@pytest.mark.parametrize("line", ["Lannes, bombard Podolia", "Lannes, bombard Kutuzov",
                                  "Lannes, bombard Moore", "Lannes, bombard Mack",
                                  "Ney, bombard Podolia"])
def test_a_marshal_with_no_guns_is_told_so_by_both(census_board, line):
    client, snap = census_board
    _fresh(snap)
    with _quiet():
        pre = client.get("/parse_preview", params={"line": line}).json()
    world = _fresh(snap)
    before = int(world.actions_remaining)
    with _quiet():
        reply = client.post("/command", json={"command": line}).json()
    assert pre["kind"] == "refusal" and "commands no guns" in pre["refusal"], pre
    assert "commands no guns" in str(reply.get("message")), reply.get("message")
    assert not reply.get("success") and int(world.actions_remaining) == before
