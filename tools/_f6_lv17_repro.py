"""F6 "Settled once, reopened" (LV-17) — the reproduction, in-process.

    .venv/Scripts/python.exe tools/_f6_lv17_repro.py [--turns 7]

Plays the September 23 live review's orders (turns 1-6, the historical seed,
the mock parser) through the REAL `/command` endpoint and prints, per turn:
every `jealousy_fired` / `jealousy_resolved` event (marshal, target,
by_action, reason), the battle reports' jealousy notes, and the marshal
petition standing at the end of the turn (kind, pair, its first body line).
Petitions are answered "acknowledge"; envoys are declined.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["LLM_MODE"] = "mock"
os.environ["SOVEREIGN_SEED"] = "historical"
for _k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
    os.environ.pop(_k, None)
os.environ.setdefault("INK_IRON_SAVE_DIR", str(ROOT / "tools" / "playtest_runs" / "_f6_saves"))

ORDERS = {
    1: ["Ney, attack Mack", "Soult, attack Mack", "Murat, scout Tyrol", "Davout, move to Munich"],
    2: ["Ney, march to Vienna"],
    3: ["Soult, march to Vienna", "Davout, march to Vienna"],
    4: ["Murat, pursue Archduke Charles"],
    5: ["Ney, attack Archduke John", "Davout, attack Archduke John", "Lannes, march to Vienna"],
    6: ["Soult, attack Vienna", "Murat, attack Vienna", "Ney, attack Vienna"],
}


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _petition_summary(p):
    if not isinstance(p, dict):
        return None
    ctx = p.get("context") or {}
    body = str(p.get("body") or "")
    return {
        "kind": p.get("kind"),
        "title": p.get("title"),
        "marshal": ctx.get("marshal") or p.get("marshal") or p.get("speaker"),
        "target": ctx.get("target") or p.get("target"),
        "built_turn": p.get("built_turn", ctx.get("turn")),
        "first_line": body.split(". ")[0][:160],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=7)
    args = ap.parse_args()
    from fastapi.testclient import TestClient
    import backend.main as M
    from backend.commands.parser import CommandParser

    with _quiet():
        M._reset_world_state()
    M.parser = CommandParser(use_real_llm=False)
    client = TestClient(M.app)
    seen_events = 0

    def post(path, body):
        with _quiet():
            r = client.post(path, json=body)
        assert r.status_code == 200, (path, r.status_code, r.text[:300])
        return r.json()

    def answer_everything(resp):
        """Answer a petition or a dialogue the response carries, so the
        turn can end. Petitions -> acknowledge; envoys -> decline."""
        world = M.world
        for _ in range(8):
            pet = resp.get("marshal_petition") or resp.get("deferred_marshal_petition")
            if pet:
                print(f"   POPUP petition: {json.dumps(_petition_summary(pet))}")
                resp = post("/marshal_petition_response", {"choice": "acknowledge"})
                continue
            dlg = resp.get("diplomatic_dialogue") or resp.get("incoming_proposal")
            if dlg and world.dialogue_manager.peek() is not None:
                resp = post("/respond_to_diplomatic_dialogue", {"choice": "reject"})
                continue
            break
        return resp

    for turn in range(1, args.turns + 1):
        world = M.world
        print(f"\n=== TURN {int(world.current_turn)} ===")
        for order in ORDERS.get(turn, []):
            resp = post("/command", {"command": order})
            note = (resp.get("battle_report") or {}).get("jealousy_note") or resp.get("jealousy_note")
            print(f" > {order}: success={resp.get('success')} :: {str(resp.get('message',''))[:120]}")
            if note:
                print(f"   NOTE: {note}")
            resp = answer_everything(resp)
        resp = post("/command", {"command": "end turn"})
        resp = answer_everything(resp)
        world = M.world
        new_events = world.event_log[seen_events:]
        seen_events = len(world.event_log)
        for ev in new_events:
            if ev.get("type") in ("jealousy_fired", "jealousy_resolved"):
                print("   EVENT", json.dumps({k: ev.get(k) for k in
                                              ("turn", "type", "marshal", "target",
                                               "by_action", "reason", "fires", "location")}))
        for name, m in sorted(world.marshals.items()):
            if m.nation == world.player_nation and getattr(m, "jealous_of", None):
                print(f"   STATE {name} jealous_of={m.jealous_of} turns_left={m.jealousy_turns_remaining} "
                      f"surge={m.jealousy_surge_turns} levels={m.jealousy_history.get('__levels__')}")
        print("   PENDING:", json.dumps(_petition_summary(getattr(world, 'pending_marshal_petition', None))))
        disp = world.last_morning_dispatch or {}
        for row in (disp.get("marshals") or []):
            if "grievance" in str(row.get("status_note", "")) or "envious" in str(row.get("status_note", "")):
                print(f"   DISPATCH {row.get('name')}: {row.get('status_note')}")
        for ev in (disp.get("events") or []):
            msg = str(ev.get("message", ""))
            if "grievance" in msg or "envious" in msg or "resents" in msg or "seeks an audience" in msg:
                print(f"   DISPATCH-EVENT: {msg[:200]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
