"""Before/after sweep for CODE-2c slice 2: every `action` string
`DiplomaticExecutor._process_dialogue_choice` tests, sent through the method
with a bare and a populated `selected` / `dialogue`, on a fresh copy of the
1805 world with the RNG seeded. Writes {key: [reply-or-exception, world
digest]} as JSON; run it on the tree before the cut and after, and the two
files must be identical.

    .venv/Scripts/python.exe tools/dialogue_choice_sweep.py <out.json>
"""
import ast
import hashlib
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "backend").is_dir():          # run from elsewhere: the repo is the cwd
    ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

from backend.commands.executor import CommandExecutor  # noqa: E402
from backend.models.world_state import WorldState  # noqa: E402

SCENARIO = ROOT / "godot-client/project-sovereign/assets/maps/europe_1805.json"
SRC = ROOT / "backend/commands/diplomatic_executor.py"

text = SRC.read_text(encoding="utf-8")
tree = ast.parse(text)
owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "DiplomaticExecutor")
fns = [n for n in owner.body if isinstance(n, ast.FunctionDef)
       and (n.name == "_process_dialogue_choice" or n.name.startswith("_choice_"))]
actions, keys = set(), set()
for fn in fns:
    for n in ast.walk(fn):
        if isinstance(n, ast.Compare):
            left = n.left
            is_action = (isinstance(left, ast.Name) and left.id == "action") or (
                isinstance(left, ast.Attribute) and left.attr == "action"
                and isinstance(left.value, ast.Name) and left.value.id == "ctx")
            if is_action:
                for c in n.comparators:
                    for k in ast.walk(c):
                        if isinstance(k, ast.Constant) and isinstance(k.value, str):
                            actions.add(k.value)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" \
                and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            keys.add(n.args[0].value)
        if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) \
                and isinstance(n.slice.value, str):
            keys.add(n.slice.value)
actions.add("no_such_action")


def filled():
    out = {}
    for k in sorted(keys):
        lk = k.lower()
        if any(s in lk for s in ("nation", "court", "target", "proposer", "ally", "source", "defender",
                                 "attacker", "vassal", "from", "to")):
            out[k] = "Austria"
        elif any(s in lk for s in ("terms", "context", "proposal", "draft", "data")):
            out[k] = {"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                      "demands": [], "sweeteners": []}
        elif any(s in lk for s in ("options", "list", "clauses", "demands", "sweeteners", "regions")):
            out[k] = []
        elif any(s in lk for s in ("gold", "amount", "cost", "turn", "count", "index", "idx", "level",
                                   "value", "manpower", "ap", "score")):
            out[k] = 3
        else:
            out[k] = "peace"
    return out


base = WorldState.from_scenario(str(SCENARIO))
snapshot = base.to_dict()
variants = {
    "bare": ({}, {"target_nation": "Austria"}),
    "filled": (filled(), filled()),
}


UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def digest(world):
    # a notification's id is a fresh uuid4 on every call: blank it, or two
    # runs of the same tree differ (start_mission's notice)
    raw = json.dumps(world.to_dict(), sort_keys=True, default=str)
    return hashlib.sha256(UUID.sub("<uuid>", raw).encode("utf-8")).hexdigest()[:16]


out = {}
for action in sorted(actions):
    for vname, (sel, dlg) in variants.items():
        world = WorldState.from_dict(json.loads(json.dumps(snapshot, default=str)))
        ex = CommandExecutor()._diplomatic
        random.seed(1805)
        try:
            reply = ex._process_dialogue_choice(action, json.loads(json.dumps(sel)),
                                                json.loads(json.dumps(dlg)), world)
            reply = json.loads(json.dumps(reply, sort_keys=True, default=str))
        except Exception as e:  # noqa: BLE001
            reply = f"EXC:{type(e).__name__}:{e}"
        out[f"{action}|{vname}"] = [reply, digest(world)]
Path(sys.argv[1]).write_text(json.dumps(out, indent=0, sort_keys=True, ensure_ascii=False),
                             encoding="utf-8")
exc = sum(1 for v in out.values() if isinstance(v[0], str) and v[0].startswith("EXC:"))
print(len(actions), "actions,", len(keys), "keys,", len(out), "calls,", exc, "raised")
