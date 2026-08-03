"""A2 STRANGULATION DRIVE — the played arc, scripted France (Aug 2, 2026).

The historical opening of the Continental System's war: France marches on
PORTUGAL (Junot, 1807) to close Britain's Iberian ports. On the shipped
board the boot closure is 38.5% against the 40% first notch, so taking
Portugal ACTIVATES the System — `cs_tier_shift` fires and Britain's war
weariness starts taking the +tier/turn squeeze.

Honest driving rules: every order goes through the REAL executor (the same
action dicts the AI uses — same seams, same gates); no state is hand-set;
the ambient world (coalition, economy, enemy AI) runs live underneath.
"""
import io
import json
import os
import random
import sys
from collections import deque

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["LLM_MODE"] = "mock"
os.environ["SOVEREIGN_SEED"] = "historical"
os.environ.pop("SOVEREIGN_SCENARIO", None)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
SCENARIO = os.path.join(REPO, "godot-client", "project-sovereign",
                        "assets", "maps", "europe_1805.json")

from backend.models.world_state import WorldState          # noqa: E402
from backend.game_logic.turn_manager import TurnManager    # noqa: E402
from backend.commands.executor import CommandExecutor      # noqa: E402
from backend.game_logic import naval                       # noqa: E402

MAX_TURNS = int(os.environ.get("A2_TURNS", "40"))
TARGETS = ["Lisbon", "Porto", "Alentejo", "Beira"]  # the whole Portuguese court


def walkable(world, nation, region_name):
    region = world.regions.get(region_name)
    if region is None:
        return False
    holder = region.controller
    if holder == nation:
        return True
    if holder in ("Portugal",):          # the objective — enter by attack
        return True
    state = world.get_diplomatic_state(nation, holder)
    if state in ("ALLIANCE", "DEFENSIVE_ALLIANCE", "VASSAL"):
        return True
    if getattr(world, "vassals", None) and world.vassals.get(holder, {}).get("lord") == nation:
        return True
    return False


def next_step(world, nation, origin, goal):
    """BFS over land-and-open edges the mover may actually use."""
    if origin == goal:
        return None
    seen = {origin}
    queue = deque([(origin, None)])
    parent = {}
    while queue:
        cur, _ = queue.popleft()
        region = world.regions.get(cur)
        for adj in getattr(region, "adjacent_regions", []) or []:
            if adj in seen or not walkable(world, nation, adj):
                continue
            if naval.is_sea_link(world, cur, adj):
                continue  # this drive marches by land
            seen.add(adj)
            parent[adj] = cur
            if adj == goal:
                path = [adj]
                while path[-1] in parent and parent[path[-1]] != origin:
                    path.append(parent[path[-1]])
                return path[-1]
            queue.append((adj, cur))
    return None


def main():
    world = WorldState.from_scenario(SCENARIO)
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    game_state = {"world": world, "executor": executor}

    log = []
    seen_events = set()
    tasks = {"Soult": "Lisbon", "Lannes": "Lisbon"}  # combined assault
    home_guard = ["Davout", "Ney", "Murat"]           # Paris holds
    britain_sued = []
    tier_shifts = []

    def run(cmd):
        cmd.setdefault("type", "specific")
        return executor.execute({"command": cmd}, game_state)

    def pump_dialogues():
        """Answer the player surfaces a real player answers, in their real
        order: the Talleyrand pre-war objection POPUP (Proceed Anyway), the
        war-purpose card (Conquest), the DG-4 ally-entry review (Proceed),
        and every other incoming envoy (decline — a BRITISH feeler is the
        arc's win and is recorded before the decline)."""
        for _ in range(8):
            # A marshal's objection holds ALL later orders — answer it the
            # way the player's Proceed button does. (Live case: Murat
            # objecting to garrison duty at Paris blocked the whole army.)
            # A capture question holds every later order until answered.
            if getattr(world, "pending_capture_choice", None):
                executor._capture.handle_capture_choice("secure", game_state)
                continue
            if getattr(world, "pending_objection", None):
                executor._meta.handle_objection_response("insist", game_state)
                continue
            if getattr(world, "pending_strategic_objection", None):
                executor._meta.handle_objection_response("insist", game_state)
                continue
            popup = getattr(world, "diplomatic_objection_popup", None)
            if popup:
                executor._diplomatic.handle_diplomatic_objection_response(
                    "proceed", game_state,
                    action=popup.get("action"),
                    target_nation=popup.get("target_nation"))
                continue
            pending = getattr(world, "pending_diplomatic_dialogue", None)
            if not pending:
                break
            kind = (pending.get("context") or {}).get("kind")
            if kind == "ally_entry_review":
                for word in ("Proceed", "Accept", "Call"):
                    r = executor._diplomatic.handle_diplomatic_dialogue_response(
                        word, game_state)
                    if r.get("success") is not False:
                        break
                continue
            if pending.get("type") == "war_purpose_selection":
                executor._diplomatic.handle_diplomatic_dialogue_response(
                    "Conquest", game_state)
                continue
            if pending.get("from_nation") == "Britain":
                britain_sued.append({
                    "turn": int(world.current_turn),
                    "event": "incoming_dialogue",
                    "ptype": pending.get("proposal_type") or pending.get("type")})
            answered = False
            for word in ("Decline", "Reject", "Refuse"):
                r = executor._diplomatic.handle_diplomatic_dialogue_response(
                    word, game_state)
                if r.get("success") is not False:
                    answered = True
                    break
            if not answered:
                break

    def press_the_attack(name, result):
        """W6-4: a field attack against a defended position returns a muster
        preview — commit it, as the player's Attack Anyway button does."""
        marshal = world.get_marshal(name)
        interrupt = getattr(marshal, "pending_interrupt", None) if marshal else None
        if not (result.get("requires_input") and interrupt):
            return result
        from backend.commands.strategic import StrategicOrderProcessor
        sp = StrategicOrderProcessor(executor)
        return sp.handle_response(name, interrupt.get("interrupt_type"),
                                  "attack_anyway", world, game_state)


    for turn in range(1, MAX_TURNS + 1):
        notes = []
        # ── the player phase: march on Portugal ──
        world.actions_remaining = max(world.actions_remaining, 8)
        pump_dialogues()
        for name, goal in list(tasks.items()):
            marshal = world.get_marshal(name)
            if marshal is None or marshal.strength <= 0:
                continue
            goal_region = world.regions.get(goal)
            if goal_region is not None and goal_region.controller == "France":
                # advance to the next Portuguese objective
                remaining = [t for t in TARGETS
                             if world.regions[t].controller != "France"]
                tasks[name] = remaining[0] if remaining else None
                if tasks[name] is None:
                    continue
                goal = tasks[name]
                goal_region = world.regions.get(goal)
            adjacent = goal in (world.regions[marshal.location].adjacent_regions
                                if marshal.location in world.regions else [])
            if adjacent and goal_region.controller != "France":
                result = run({"marshal": name, "action": "attack", "target": goal})
                if "war purpose" in str(result.get("message", "")).lower():
                    pump_dialogues()
                    result = run({"marshal": name, "action": "attack",
                                  "target": goal})
                result = press_the_attack(name, result)
                _m = str(result.get("message") or "")[:110]
                notes.append(f"{name}->{goal}: " + " ".join(_m.split()))
                if getattr(world, "pending_capture_choice", None):
                    executor._capture.handle_capture_choice("secure", game_state)
            elif marshal.location != goal:
                step = next_step(world, "France", marshal.location, goal)
                if step:
                    mr = run({"marshal": name, "action": "move", "target": step})
                    if mr.get("success") is False or True:
                        _mm = str(mr.get("message") or "")[:100]
                        notes.append(f"{name} move->{step} ok={mr.get('success')}: "
                                     + " ".join(_mm.split()))

        # the home guard: stand at Paris, fortified — France defends
        for name in home_guard:
            marshal = world.get_marshal(name)
            if marshal is None or marshal.strength <= 0:
                continue
            if marshal.location != "Paris":
                step = next_step(world, "France", marshal.location, "Paris")
                if step:
                    run({"marshal": name, "action": "move", "target": step})
            elif not getattr(marshal, "fortified", False):
                run({"marshal": name, "action": "fortify"})

        # ── the world turn ──
        random.seed(10_000 + turn)
        tm.end_turn(game_state)
        pump_dialogues()

        closure = naval.closure_against(world, "Britain")
        tier = naval.cs_closure_tier(closure)
        we = int(world.war_exhaustion.get("Britain", 0))
        pt = [r for r in TARGETS if world.regions[r].controller == "France"]

        for e in list(world.event_log):
            if id(e) in seen_events:
                continue
            seen_events.add(id(e))
            et = e.get("type", "")
            if et == "cs_tier_shift":
                tier_shifts.append({"turn": world.current_turn, **{
                    k: e.get(k) for k in ("closure_pct", "tier", "previous_tier")}})
            if et in ("diplomatic_proposal", "settlement_offer",
                      "peace_proposal", "armistice_expired_peace") and \
                    e.get("from_nation") == "Britain":
                britain_sued.append({"turn": world.current_turn, "event": et,
                                     "ptype": e.get("proposal_type")})
        # Britain suing can also arrive as a pending dialogue/mailbox item
        pending = getattr(world, "pending_diplomatic_dialogue", None)
        if pending and isinstance(pending, dict) and \
                pending.get("from_nation") == "Britain":
            britain_sued.append({"turn": world.current_turn,
                                 "event": "pending_dialogue",
                                 "ptype": pending.get("proposal_type")})

        log.append({
            "turn": int(world.current_turn),
            "closure_pct": round(closure * 100, 1), "tier": tier,
            "britain_we": we,
            "portugal_taken": pt,
            "at_war_britain": world.is_at_war("France", "Britain"),
            "france_gold": int(world.nation_gold.get("France", 0)),
            "paris": world.regions["Paris"].controller,
            "notes": notes,
            "positions": {n: (world.get_marshal(n).location if world.get_marshal(n) else None)
                           for n in ("Soult", "Lannes")},
        })
        if len(pt) == len(TARGETS) and tier >= 1 and turn >= 30:
            break

    out = {"log": log, "tier_shifts": tier_shifts,
           "britain_sued": britain_sued[:20]}
    io.open(sys.argv[1], "w", encoding="utf-8").write(
        json.dumps(out, indent=1, default=str))
    print("wrote", sys.argv[1])


if __name__ == "__main__":
    main()
