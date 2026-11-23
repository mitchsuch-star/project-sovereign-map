"""Row IC, Session 4b — HIS OWN JUDGEMENT, AND HE MOVES AT TURN START: the measure.

The rules were written BEFORE any data, in the plan the user approved (November
23, 2026; `docs/INDEPENDENT_COMMAND_SPEC.md` §13 as Session 4b restates it):

* R-INITIATIVE (new) — counted on turns when a CHANCE stands beside him (an
  enemy France sees in his strike reach that he beats at his own figure and
  that is not his task's own target; an enemy-held province within a march
  France sees whole, empty of any corps it sees; a friend beside him with a
  seen enemy next to that friend) and your aim's own step that turn is only a
  march or a wait:
    - bold men take a chance on at least 6 turns in 10 (pooled), and every bold
      man on at least 5 in 10;
    - careful men take one on at least 6 in 10 when the odds are 3 or more
      tenths above his own figure, or it covers a friend; the rest reported;
    - ZERO chances taken more than one march off your road or held ground;
    - after a chance off his road, he is back on your aim within 2 turns on at
      least 8 in 10, when no new chance stands;
    - ZERO out-and-back patterns (A, B, A, B) over 4 turns.
* R-ACTS (restated by the user's correction) — the men on their own, together,
  do something visible on at least 7 turns in 10 at war; every stay names the
  reason his judgement chose it (zero bare "nothing to do"); a bold man near a
  seen enemy goes toward him on at least half those turns; each man's own share
  is reported, not required.
* R-REPORT (replaces R-TRUE) — what the morning report says he did is what
  happened: zero lines claim a fight with no battle or a march that did not
  arrive.
* Kept as written: R-TOGETHER, R-FRIENDS (reported), R-VARIETY.

The harness finds the chances ITSELF on the board at the moment he moves (the
pass, wrapped), never from his own reading — so it cannot grade itself. Each
man's task is VARIED across campaigns (his own idea, take, chase, hold,
support, no task), where Session 3's run gave each man only his first idea.

Two corrections from the play-out (November 23, 2026; three campaigns of ten
turns, BEFORE the measure was run), each bringing the harness to the rule as
written above — no bar moved:
* "taken" is read from what he DID (the enemy struck, the province entered,
  the friend's battle joined and that friend's enemy) — the first draft read
  his own label, against the paragraph above; a strike carried out by joining
  a friend's attack on the same enemy (R-TOGETHER) carried no label at all;
* the friend chance is the plan's "strike the enemy threatening a friend
  beside him": an enemy he can strike (in his reach, at his own figure) that
  stands next to a friend beside him — the first draft (the "a friend beside
  him with a seen enemy next to that friend" above) counted it even where he
  had nothing he could strike.

And three from round 0 of the measure (November 23, 2026), the same kind — a
chance the rules forbid him to take is no chance:
* a man rallying from a defeat does not attack (the plan: "While his men rally
  he does not attack") — his turns count no chance;
* with an enemy in his own province the game lets him attack only that enemy
  and march only onto French soil (the executor's engagement rules) — only
  that enemy is a chance;
* a frozen ask (his trust under 30) is no choice — not counted.
(Round 0's two defects — 18 turns lost to moves the game refused, and a line
that left a man where his march ended when the arrival roll had carried him
into a friend's battle — were fixed in the game, not here.)

And one from round 0c, the same kind: "ZERO out-and-back patterns" is the
plan's guard "No marching out and back" — so the pattern is read over the
marches HE chose (A→B, B→A, A→B on three turns running); the A, B, A, B of
where he stood, which a battle carrying him forward or the enemy pushing him
back also makes, is reported beside it (`out_and_back_any_reported`). Round
0c's two game defects — a man drawn in before his move read "he moves again
next turn — unless the usual roll draws him in first" (a regression of the
turn-start rework), and a rallying man rested where his chance had carried
him where the plan says he falls back to his ground — were fixed in the game.

And one from round 0d, the same kind: "back on your aim within 2 turns" meets
the plan's rally rule ("While his men rally he does not attack: he falls back
to his ground or digs in, then carries on") — a man who LOST his chance
cannot march on your aim while his men rally, so the two turns are counted
from when he is fit again, and a rally's fall-back onto the ground you named
is his return. Round 0d's game defects — the rally's fall-back forgot to leave
his works first ("fortified … cannot move"), stepped straight back where he
came from, and fell back onto a post the enemy kept throwing him off until his
corps was destroyed — were fixed in the game.

Round 0e (every game defect fixed, no weight changed) met every rule but one:
back on your aim within 2 turns, 0.735 against 0.8. ROUND 1 (the first of the
two rounds of weight changes the plan allows): `rest` 30 → 10 (a half-strength
corps rested turn after turn, off your aim, though rest restores no men). With
it, one defect of the plan's own words: a man beside the friend he supports
walked off to find the enemy — the plan lets him seek only "when your aim gives
him nothing to do", and a support aim always does: keep by his friend
(`own_judgement._by_his_friend`).

Round 1 read worse (bold 0.541, return 0.526). Two causes, neither a bar: the
supporter fix had also given his waiting the post's bonus, so he stopped
taking chances (refined: he no longer searches afar, and his waiting weighs as
anyone's); and the harness read "back on your aim" off his own label again —
a man who marched straight back to his post while a new chance stood, or who
stood on it the turn after, was not counted back. Corrected to the board: on
the ground you named (a hold), beside the friend he supports (a support), a
step toward the aim (a take or a chase). ROUND 2 (the last the plan allows):
`chance` bold 55 → 58 ("A bold man takes chances readily at his own odds"),
`margin_cap` 30 → 27 (so that your aim in reach still weighs most: 58 + 27 +
our soil 15 = 100, a tie the aim wins).

Round 2 met every rule but R-INITIATIVE's bold half (0.56 pooled; Murat 0.44 —
9 of 35 on a hold). The two rounds are spent: the plan's fallback is to report
per man and per campaign (`tools/_ic4b_per_campaign.py`) and bring it to the
user. ONE INFORMATION ARM, written down here BEFORE it was read: the ORIGINAL
weights (round 0's table) with every defect fix and the corrected readings —
round 0e met the bold half on that table, before the return reading was
corrected. The rule for it, fixed now: if it meets EVERY rule, the original
table ships (no weight change was needed; the two rounds are reported as
tried and undone); if it misses any rule, round 2's table ships and both
readings go to the user for the choice.

THE READINGS (November 23, 2026). The information arm (original table, every
fix) missed more (bold 0.54; R-ACTS 0.691) — so by the rule above round 2's
table stood. A second information arm, ROUND 2 WITH `off_held` 24 → 12 — the
plan's own words price a march off held ground as one off your road ("A
chance counts for less for every march it takes him off your road, or off
the ground you told him to hold"; "He strikes what comes within reach of
it"), and the build had doubled it — met EVERY rule (bold 0.642, each man
over 0.5; careful 0.684; return 0.96; R-ACTS 0.759). The band (R-BAND, the
deploy's difficulty guard) was then read on both tables from frozen copies:
round 2's leaves 23-28 (two men at the start, CMD-A: 22); the plan's price
holds on every arm (27/27/28 at its lowest), TODAY 26/27/28 on both
(R-INERT). The plan's price is in the tree, put to the user before any
commit; keeping round 2 is one number.

    .venv/Scripts/python.exe tools/_ic4b_measure.py [--seeds 30] [--turns 20] [--out FILE]
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import pathlib
import random
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for _k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
    os.environ.pop(_k, None)
os.environ["LLM_MODE"] = "mock"

MEN = ("Ney", "Lannes", "Murat", "Davout", "Bernadotte")
BOLD = ("Ney", "Lannes", "Murat")
CAREFUL = ("Davout", "Bernadotte")
TASKS = ("proposal", "take", "pursue", "hold", "support", "free")
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
SEED_NAMES = ["historical", "austerlitz", "marengo"] + [f"ic4b-{n:02d}" for n in range(1, 60)]
VISIBLE = {"attack", "strike", "storm", "besiege", "take", "march", "move_up", "join",
           "look", "probe", "dig_in", "fall_back"}
TOWARD = {"attack", "strike", "storm", "besiege", "take", "march", "move_up", "join", "probe"}
MOVES = {"march", "probe", "fall_back", "move_up"}
MARCHES = {"march", "probe", "fall_back", "move_up", "take"}   # the moves HE chooses

# the bars, written before the data
BARS = {"bold_pooled": 0.6, "bold_each": 0.5, "careful_good": 0.6, "return": 0.8,
        "acts_together": 0.7, "bold_toward": 0.5}


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _spec_for(world, O, man, kind: str):
    """His task for this campaign, by the varied kind (fallback: his own idea)."""
    from backend.game_logic import trial as _trial
    here = str(man.location or "")
    task, target = "", ""
    if kind == "take":
        found = _trial._place_to_take(world, man)
        if found is not None:
            task, target = "take", found["place"]
    elif kind == "pursue":
        best = None
        for enemy in world.get_visible_enemies(man.nation) or []:
            d = O._distance(world, here, enemy.location)
            if d is None or d > O.PURSUE_RING or int(getattr(enemy, "strength", 0) or 0) <= 0:
                continue
            if best is None or (d, enemy.name) < best[0]:
                best = ((d, enemy.name), enemy)
        if best is not None:
            task, target = "pursue", best[1].name
    elif kind == "hold":
        task, target = "hold", here
    elif kind == "support":
        best = None
        for other in world.get_player_marshals():
            if other.name == man.name or getattr(other, "personality", "") == "sovereign":
                continue
            if O._hates(man, other.name) or int(getattr(other, "strength", 0) or 0) <= 0:
                continue
            d = O._distance(world, here, other.location)
            if d is not None and (best is None or (d, other.name) < best[0]):
                best = ((d, other.name), other)
        if best is not None:
            task, target = "support", best[1].name
    elif kind == "free":
        task, target = "free", ""
    if not task:
        prop = O.proposal(world, man)
        task, target = prop["task"], prop["target"]
    spec, _why = O.spec_from(world, man, task, target)
    if spec is None:
        prop = O.proposal(world, man)
        spec, _why = O.spec_from(world, man, prop["task"], prop["target"])
    return spec


def _anchor(world, O, man, spec) -> set:
    from backend.game_logic import own_judgement as J
    if not spec or spec.get("task") in ("free", "", None):
        return set()
    here = str(man.location or "")
    dest = J._goal_place(world, man, spec)
    area = [p for p in (spec.get("area") or []) if p] if spec.get("task") == "hold" else []
    road = []
    if spec.get("task") != "hold" and dest and dest != here:
        road = list(O._road(world, man, dest, avoid_foes=(spec.get("task") == "support")) or [])[:4]
    return {here} | set(road) | set(area)


def _off(world, O, place: str, anchor: set) -> int:
    if not anchor or not place or place in anchor:
        return 0
    best = None
    for spot in anchor:
        d = O._distance(world, place, spot)
        if d is not None and (best is None or d < best):
            best = d
    return int(best if best is not None else 9)


def _chances(world, O, man, spec) -> dict:
    """The chances standing beside him, found by the harness — never his reading."""
    from backend.commands import if_thens as IT
    out = {"attack": [], "take": [], "friend": [], "good": False}
    here = str(man.location or "")
    task_target = str((spec or {}).get("target") or "")
    need = O.needed(man, int((spec or {}).get("risk", 0) or 0), O._record_view(man))
    capitals = {str(v) for v in (getattr(world, "nation_capitals", None) or {}).values() if v}
    # the game's own rules decide what can be taken at all: a man rallying from
    # a defeat does not attack (the plan); an enemy in his own province is the
    # only one he may attack, and he marches only onto French soil (the
    # executor's engagement rules) — a chance he may not take is no chance
    if O._unfit(world, man):
        return out
    engaged = bool(O._engaged_by(world, man))
    for enemy, where in IT.seen_enemies(world, man):
        if enemy.name == task_target or where == task_target:
            continue
        if engaged and where != here:
            continue
        if not O._in_strike_reach(world, man, where) or where in capitals:
            continue
        odds = O.odds_against(world, man, enemy)
        if odds is None:
            continue
        tenths = float(odds["ratio"]) * 10.0
        if tenths + 1e-9 >= float(need["needed"]):
            out["attack"].append({"enemy": enemy.name, "place": where,
                                  "margin": round(tenths - float(need["needed"]), 1)})
            if tenths - float(need["needed"]) >= 3.0:
                out["good"] = True
    for place in ([] if engaged else O._near(world, here)):
        if place == task_target or place in capitals or not O._full(world, place):
            continue
        region = world.get_region(place)
        holder = str(getattr(region, "controller", "") or "") if region is not None else ""
        if holder and holder != man.nation and world.is_at_war(man.nation, holder) \
                and not O._foes_at(world, man, place):
            out["take"].append(place)
    # a friend beside him threatened: the plan's chance is "strike the enemy
    # threatening a friend beside him" — so an ENEMY HE CAN STRIKE (in his
    # reach, at his own figure, found above) standing next to that friend. (The
    # play-out, November 23, 2026: the first draft counted any friend with an
    # enemy near him, though he might have nothing he could strike.)
    near = set(O._near(world, here))
    friends_near = [other for other in world.get_player_marshals()
                    if other.name != man.name and not O._hates(man, other.name)
                    and other.location in near and int(getattr(other, "strength", 0) or 0) > 0]
    for row in out["attack"]:
        for other in friends_near:
            if (O._distance(world, other.location, row["place"]) or 9) <= 1:
                row["covers"] = other.name
                if other.name not in out["friend"]:
                    out["friend"].append(other.name)
                out["good"] = True
    return out


def one_seed(seed: str, index: int, turns: int) -> dict:
    with _quiet():
        import backend.main as M
        from fastapi.testclient import TestClient

        from backend.commands import parse_preview as PP
        from backend.commands.combat_executor import CombatExecutor
        from backend.commands.parser import CommandParser
        from backend.game_logic import own_order as O
        from backend.models.world_state import WorldState
        world = WorldState.from_scenario(str(SCENARIO), seed=seed)
        M._set_active_world(world)
        M.parser = CommandParser(use_real_llm=False)
        PP.invalidate()
    O.COUNT_AT_START = len(MEN)
    rolls: list = []
    stalls: list = []
    snaps: list = []
    real_rf = CombatExecutor._calculate_reinforcements
    real_pass = O.the_pass

    def _wrapped(self, primary, defender, battle_region, nation, w, rng=None, attacked=False):
        out = real_rf(self, primary, defender, battle_region, nation, w, rng=rng, attacked=attacked)
        try:
            if nation == w.player_nation and (attacked or getattr(self, "_reinforcing_the_attacked", False)):
                region = w.get_region(battle_region)
                near = set(getattr(region, "adjacent_regions", []) or [])
                rows = out if isinstance(out, list) else (out or {}).get("results", []) if isinstance(out, dict) else []
                tried = {str(r.get("marshal")) for r in rows if isinstance(r, dict)}
                for man in O.men(w):
                    if man.location in near and man.name != getattr(primary, "name", ""):
                        rolls.append({"turn": int(w.current_turn), "man": man.name,
                                      "rolled": man.name in tried,
                                      "hates": int(man.get_relationship(getattr(primary, "name", ""))) <= -2})
        except Exception as exc:
            rolls.append({"error": str(exc)})
        return out

    def _pass(w, executor, game_state):
        from backend.commands import if_thens as IT
        snap = {"turn": int(w.current_turn), "men": {}, "shared": {}}
        at_war = O._at_war(w)
        for man in O.men(w):
            spec = dict(O.own(man) or {})
            try:
                reading = O.read(w, man)
            except Exception:
                reading = {}
            goal = [x for x in (reading.get("weighed") or []) if x.get("kind") == "goal"]
            snap["men"][man.name] = {
                "task": spec.get("task"), "target": spec.get("target"), "loc": str(man.location or ""),
                "anchor": sorted(_anchor(w, O, man, spec)),
                "chances": _chances(w, O, man, spec),
                "goal_aim": bool(goal and goal[0]["act"] in ("attack", "strike", "storm", "besiege", "take")),
                "near_foe": any((O._distance(w, man.location, where) or 9) <= 2
                                for _e, where in IT.seen_enemies(w, man)),
                "at_war": at_war,
                "unfit": bool(O._unfit(w, man)),
                # what he weighed (for the per-turn diagnosis only — never scored)
                "weighed": list(reading.get("weighed") or []),
                "chose": str(reading.get("act") or "")}
            for enemy, where in IT.seen_enemies(w, man):
                if (O._distance(w, man.location, where) or 9) <= 1:
                    snap["shared"].setdefault(enemy.name, set()).add(man.name)
        rows = real_pass(w, executor, game_state)
        snap["shared"] = {k: sorted(v) for k, v in snap["shared"].items() if len(v) >= 2}
        for name, row in snap["men"].items():
            m = w.marshals.get(name)
            row["after"] = str(getattr(m, "location", "") or "")
            # where he stands against your aim AFTER his move (the return rule
            # reads it from the board, never from his label): on the ground you
            # named (a hold), beside the friend he supports (a support)
            if row.get("task") == "hold":
                row["on_aim_after"] = row["after"] in set((O.own(m) or {}).get("area") or [])
            elif row.get("task") == "support":
                friend = w.marshals.get(str(row.get("target") or ""))
                d = (O._distance(w, row["after"], str(getattr(friend, "location", "") or ""))
                     if friend is not None else None)
                row["on_aim_after"] = d is not None and d <= 1
        snap["rows"] = [{"marshal": r.get("marshal"), "act": r.get("act"), "kind": r.get("kind", ""),
                         "chance": bool(r.get("chance")), "place": r.get("place", ""),
                         "target": r.get("target", ""), "message": r.get("message", ""),
                         "said": r.get("said", ""), "follows": r.get("follows", ""),
                         "action": r.get("action", ""), "drawn_in": r.get("drawn_in", ""),
                         "battle": bool(r.get("battle_report") or r.get("battle_message"))}
                        for r in rows if r.get("own")]
        snaps.append(snap)
        return rows

    CombatExecutor._calculate_reinforcements = _wrapped
    O.the_pass = _pass
    given = {}
    try:
        for i, name in enumerate(MEN):
            m = world.marshals.get(name)
            if m is None:
                continue
            kind = TASKS[(index + i) % len(TASKS)]
            spec = _spec_for(world, O, m, kind)
            if spec is not None:
                with _quiet():
                    O.give(world, m, spec, line=f"{name}, on your own.", own_proposal=True)
                given[name] = {"asked": kind, "task": spec.get("task"), "target": spec.get("target")}
        with TestClient(M.app) as client:
            for t in range(turns):
                if getattr(M.world, "game_over", False):
                    break
                random.seed(f"{seed}:{t}")
                with _quiet():
                    out = client.post("/command", json={"command": "end turn"}).json()
                    # the Emperor's own choices the turn may raise, answered as
                    # the playtest driver answers them (a capture by a man on
                    # his own at the turn's start asks "plunder or secure?" and
                    # blocks End Turn until answered — round 0 froze a third of
                    # its campaigns on it)
                    for _ in range(4):
                        if not out.get("pending_capture_choice"):
                            break
                        payload = out.get("pending_capture_choice")
                        payload = payload if isinstance(payload, dict) else (out.get("capture_data") or {})
                        body = {"choice": "respect" if payload.get("stage") == "estate" else "secure"}
                        if payload.get("dialogue_id") is not None:
                            body["dialogue_id"] = payload["dialogue_id"]
                        out = client.post("/capture_choice", json=body).json()
                if not out.get("success", True) and "turn" not in str(out.get("message") or "").lower():
                    stalls.append({"turn": int(M.world.current_turn), "message": str(out.get("message"))[:160]})
    finally:
        CombatExecutor._calculate_reinforcements = real_rf
        O.the_pass = real_pass
        O.COUNT_AT_START = 1
    return {"seed": seed, "given": given, "turns": snaps, "rolls": rolls, "stalls": stalls}


def score(runs: list) -> dict:
    per_man = {n: {"turns": 0, "visible": 0, "stays": 0, "kinds": set(), "near": 0, "toward": 0,
                   "chance_turns": 0, "chance_taken": 0, "good_turns": 0, "good_taken": 0}
               for n in MEN}
    bare_stays, report_bad, far_chances, ping_pong, ping_pong_any = [], [], [], 0, 0
    returns_due, returns_made = 0, 0
    alike, alike_n, third, waits_three = 0, 0, 0, 0
    together_nights, together_named, double = 0, 0, 0
    war_turns, war_visible = 0, 0
    free_turns, free_taken = 0, 0
    tasks_seen = {}
    for run in runs:
        for name, g in run["given"].items():
            tasks_seen.setdefault(name, {}).setdefault(str(g.get("task")), 0)
            tasks_seen[name][str(g.get("task"))] += 1
        hist = {n: [] for n in MEN}
        locs = {n: [] for n in MEN}
        legs = {n: [] for n in MEN}
        pending_return = {}        # name -> turns left to come back to the aim
        for snap in run["turns"]:
            rows = {r["marshal"]: r for r in snap["rows"] if not r.get("follows")}
            acts_now = []
            for name, info in snap["men"].items():
                if name not in per_man:
                    continue
                r = rows.get(name)
                if r is None:
                    continue
                act = str(r.get("act") or "")
                if act in ("start",) or r.get("action") in ("own_done", "own_ended"):
                    continue
                pm = per_man[name]
                pm["turns"] += 1
                pm["kinds"].add(act)
                acts_now.append(act)
                again = "again — nothing has changed" in str(r.get("message") or "")
                visible = act in VISIBLE and not again
                if visible:
                    pm["visible"] += 1
                if act == "stay" or again:
                    pm["stays"] += 1
                    msg = str(r.get("message") or "")
                    if " — " not in msg or "nothing to do" in msg:
                        bare_stays.append((run["seed"], snap["turn"], name, msg[:140]))
                if info.get("at_war"):
                    war_turns += 1
                    war_visible += 1 if visible else 0
                if info.get("near_foe"):
                    pm["near"] += 1
                    pm["toward"] += 1 if act in TOWARD else 0
                # R-REPORT: what the morning says is what happened
                if "could not carry out" not in str(r.get("message") or ""):
                    if act in ("attack", "strike") and not r.get("battle"):
                        report_bad.append((run["seed"], snap["turn"], name, "fight", r.get("message", "")[:120]))
                    # (a man the usual arrival roll then drew into a later
                    # man's battle: his line says so, and he stands on that field)
                    if (act in MOVES and r.get("place") and info.get("after") != r.get("place")
                            and not r.get("drawn_in")):
                        report_bad.append((run["seed"], snap["turn"], name, "march", r.get("message", "")[:120]))
                # R-INITIATIVE
                ch = info.get("chances") or {}
                stands = bool(ch.get("attack") or ch.get("take") or ch.get("friend"))
                took = _took(info, r, rows)
                if info.get("task") == "free":
                    if stands:
                        free_turns += 1
                        free_taken += 1 if took else 0
                elif stands and not info.get("goal_aim") and act != "asks":   # (a frozen ask is no choice)
                    pm["chance_turns"] += 1
                    pm["chance_taken"] += 1 if took else 0
                    if ch.get("good"):
                        pm["good_turns"] += 1
                        pm["good_taken"] += 1 if took else 0
                if took and info.get("anchor"):
                    # the act's own place, measured from the board BEFORE he moved
                    off = _off_from(info, r)
                    if off > 1:
                        far_chances.append((run["seed"], snap["turn"], name, r.get("place"), off))
                    if off >= 1:
                        pending_return[name] = 2
                elif name in pending_return:
                    # back on your aim, read from the board after his move: on
                    # the ground you named (a hold), beside the friend he
                    # supports (a support), a step toward your aim (a take, a
                    # chase) — whether or not a new chance stood
                    if "on_aim_after" in info:
                        back = bool(info["on_aim_after"])
                    else:
                        back = r.get("kind") in ("goal", "join")
                    if back:
                        returns_made += 1
                        returns_due += 1
                        pending_return.pop(name)
                    elif info.get("unfit"):
                        pass        # the plan's rally rule: the clock waits while his men rally
                    elif not stands:
                        pending_return[name] -= 1
                        if pending_return[name] <= 0:
                            returns_due += 1
                            pending_return.pop(name)
                hist[name].append((act, str(r.get("place") or r.get("target") or "")))
                locs[name].append(info.get("after") or "")
                # his OWN marches (the plan's "No marching out and back"): a leg
                # only where he chose a move and it carried him
                if (act in MARCHES and info.get("loc") and info.get("after")
                        and info.get("loc") != info.get("after")):
                    legs[name].append((int(snap["turn"]), str(info["loc"]), str(info["after"])))
            real_acts = [a for a in acts_now if a]
            if len(real_acts) >= 3:
                alike_n += 1
                alike += 1 if len(set(real_acts)) == 1 else 0
            for enemy, names in (snap.get("shared") or {}).items():
                together_nights += 1
                hits = [n for n in names if (rows.get(n) or {}).get("act") in ("attack", "strike")
                        and (rows.get(n) or {}).get("target") == enemy]
                double += 1 if len(hits) >= 2 else 0
                named = any((rows.get(n) or {}).get("act") in ("join", "move_up") for n in names) or any(
                    other != n and other in str((rows.get(n) or {}).get("message") or "")
                    for n in names for other in names)
                together_named += 1 if named else 0
        for name, seq in hist.items():
            for i in range(2, len(seq)):
                if seq[i] == seq[i - 1] == seq[i - 2] and seq[i][0] not in ("stay", "join", "attack", "march",
                                                                            "strike", "take", "besiege"):
                    if seq[i][0] in ("asks", "recover"):
                        waits_three += 1
                        continue
                    third += 1
        for name, seq in locs.items():
            for i in range(3, len(seq)):
                a, b, c, d = seq[i - 3], seq[i - 2], seq[i - 1], seq[i]
                if a and b and a != b and a == c and b == d:
                    ping_pong_any += 1          # (reported: any A, B, A, B of where he stood)
        for name, seq in legs.items():
            for i in range(2, len(seq)):
                (t1, a1, b1), (t2, a2, b2), (t3, a3, b3) = seq[i - 2], seq[i - 1], seq[i]
                if t2 == t1 + 1 and t3 == t2 + 1 and a2 == b1 and b2 == a1 and (a3, b3) == (a1, b1):
                    ping_pong += 1
    friends = [r for run in runs for r in run["rolls"] if not r.get("error") and not r.get("hates")]
    men_out = {}
    for name, pm in per_man.items():
        n = max(1, pm["turns"])
        men_out[name] = {
            "turns": pm["turns"], "visible_share": round(pm["visible"] / n, 3),
            "stays_share": round(pm["stays"] / n, 3), "kinds": sorted(pm["kinds"]),
            "near_foe_turns": pm["near"],
            "toward_share": round(pm["toward"] / pm["near"], 3) if pm["near"] else None,
            "chance_turns": pm["chance_turns"],
            "chance_taken_share": round(pm["chance_taken"] / pm["chance_turns"], 3) if pm["chance_turns"] else None,
            "good_chance_turns": pm["good_turns"],
            "good_taken_share": round(pm["good_taken"] / pm["good_turns"], 3) if pm["good_turns"] else None,
            "tasks": tasks_seen.get(name, {})}
    bold_turns = sum(per_man[n]["chance_turns"] for n in BOLD)
    bold_taken = sum(per_man[n]["chance_taken"] for n in BOLD)
    careful_good = sum(per_man[n]["good_turns"] for n in CAREFUL)
    careful_good_taken = sum(per_man[n]["good_taken"] for n in CAREFUL)
    bold_pooled = bold_taken / bold_turns if bold_turns else None
    each_ok = all((men_out[n]["chance_taken_share"] is None or men_out[n]["chance_taken_share"] >= BARS["bold_each"])
                  for n in BOLD)
    careful_share = careful_good_taken / careful_good if careful_good else None
    return_share = returns_made / returns_due if returns_due else None
    initiative = {
        "bold_pooled": round(bold_pooled, 3) if bold_pooled is not None else None,
        "bold_chance_turns": bold_turns, "bold_each_met": each_ok,
        "careful_good_share": round(careful_share, 3) if careful_share is not None else None,
        "careful_good_turns": careful_good,
        "far_chances": far_chances[:20], "far_count": len(far_chances),
        "return_share": round(return_share, 3) if return_share is not None else None,
        "returns_due": returns_due, "out_and_back": ping_pong,
        "out_and_back_any_reported": ping_pong_any,
        "free_chance_turns": free_turns,
        "free_taken_share": round(free_taken / free_turns, 3) if free_turns else None,
    }
    initiative["met"] = bool(
        (bold_pooled is None or bold_pooled >= BARS["bold_pooled"]) and each_ok
        and (careful_share is None or careful_share >= BARS["careful_good"])
        and not far_chances and (return_share is None or return_share >= BARS["return"])
        and ping_pong == 0)
    together_share = war_visible / war_turns if war_turns else None
    bold_toward_ok = all((men_out[n]["toward_share"] is None or men_out[n]["toward_share"] >= BARS["bold_toward"])
                         for n in BOLD)
    return {
        "R-INITIATIVE": initiative,
        "R-ACTS": {"together_visible_share_at_war": round(together_share, 3) if together_share is not None else None,
                   "war_turns": war_turns, "bare_stays": bare_stays[:20], "bare_stay_count": len(bare_stays),
                   "bold_toward_met": bold_toward_ok,
                   "met": bool((together_share is None or together_share >= BARS["acts_together"])
                               and not bare_stays and bold_toward_ok),
                   "per_man": men_out},
        "R-REPORT": {"false": report_bad[:20], "count": len(report_bad), "met": not report_bad},
        "R-VARIETY": {"alike_share": round(alike / max(1, alike_n), 3), "turns_read": alike_n,
                      "third_turn_repeats": third, "asks_or_recovers_three_turns": waits_three,
                      "every_man_two_kinds": all(len(m["kinds"]) >= 2 for m in men_out.values() if m["turns"]),
                      "met": alike / max(1, alike_n) < 0.40 and third == 0
                      and all(len(m["kinds"]) >= 2 for m in men_out.values() if m["turns"])},
        "R-TOGETHER": {"turns": together_nights, "double_attacks": double,
                       "named_share": round(together_named / max(1, together_nights), 3),
                       "met": double == 0 and (together_nights == 0 or together_named / together_nights >= 0.5)},
        "R-FRIENDS": {"battles_with_a_man_beside": len(friends),
                      "he_rolled": sum(1 for r in friends if r.get("rolled"))},
    }


def not_taken(runs: list) -> dict:
    """The diagnosis, never scored: on the turns a chance stood (counted as
    R-INITIATIVE counts them) and he did not take it — what he did instead
    (his act), what his own reading weighed highest, and how far below it the
    best chance stood. By nature."""
    from collections import Counter
    out = {"bold": {"acts": Counter(), "top": Counter(), "gaps": []},
           "careful": {"acts": Counter(), "top": Counter(), "gaps": []}}
    for run in runs:
        for snap in run["turns"]:
            rows = {r["marshal"]: r for r in snap["rows"] if not r.get("follows")}
            for name, info in snap["men"].items():
                r = rows.get(name)
                if r is None or name not in MEN:
                    continue
                ch = info.get("chances") or {}
                if not (ch.get("attack") or ch.get("take")) or info.get("goal_aim"):
                    continue
                if info.get("task") == "free" or _took(info, r, rows):
                    continue
                nature = "bold" if name in BOLD else "careful"
                out[nature]["acts"][str(r.get("act") or "")] += 1
                weighed = info.get("weighed") or []
                if weighed:
                    top = weighed[0]
                    out[nature]["top"][f"{top.get('kind')}:{top.get('act')}"] += 1
                    best = max((w["weight"] for w in weighed if w.get("kind") == "chance"), default=None)
                    if best is not None:
                        out[nature]["gaps"].append(int(top["weight"]) - int(best))
    for nature, d in out.items():
        gaps = sorted(d["gaps"])
        d["acts"] = dict(d["acts"].most_common())
        d["top"] = dict(d["top"].most_common())
        d["chance_in_top5"] = len(gaps)
        d["gap_median"] = gaps[len(gaps) // 2] if gaps else None
        d["gaps"] = gaps[:: max(1, len(gaps) // 20)]
    return out


def _took(info: dict, row: dict, rows: dict) -> bool:
    """Did his act take one of the chances the HARNESS found on the board? Read
    from what he did — the enemy he struck, the province he entered, the
    friend's battle he joined (and that friend's own enemy) — never from his
    own label. (The play-out, November 23, 2026: the first draft read his
    label, against this harness's own rule; and a strike carried out by
    joining a friend's attack on the same enemy — R-TOGETHER — carried no
    label at all.)"""
    ch = info.get("chances") or {}
    enemies = {str(c.get("enemy")) for c in ch.get("attack") or []}
    places = {str(c.get("place")) for c in ch.get("attack") or []}
    takes = {str(p) for p in ch.get("take") or []}
    friends = {str(f) for f in ch.get("friend") or []}
    act = str(row.get("act") or "")
    target, place = str(row.get("target") or ""), str(row.get("place") or "")
    after = str(info.get("after") or "")
    if act in ("attack", "strike", "storm", "besiege"):
        return target in enemies or place in places or place in takes or target in takes
    if act == "take":
        return place in takes or target in takes or place in places
    if act == "join":
        lead = rows.get(target) or {}
        return (target in friends or str(lead.get("target") or "") in enemies
                or str(lead.get("place") or "") in places)
    if act in ("march", "move_up", "probe"):
        # an enemy province entered (an undefended one is his on arrival), or
        # moving up beside the friend an enemy stands next to
        return (after in takes and after != str(info.get("loc") or "")) or (
            act == "move_up" and target in friends)
    return False


def _off_from(info: dict, row: dict) -> int:
    """Marches from the act's place to the anchor (his road / held ground) as it
    stood before he moved — by the map's own distance."""
    from backend.game_logic import own_order as O
    import backend.main as M
    place = str(row.get("place") or "")
    anchor = set(info.get("anchor") or [])
    if not place or not anchor or place in anchor:
        return 0
    best = None
    for spot in anchor:
        d = O._distance(M.world, place, spot)
        if d is not None and (best is None or d < best):
            best = d
    return int(best if best is not None else 9)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--turns", type=int, default=20)
    ap.add_argument("--out", default="")
    ap.add_argument("--dump", default="", help="also write every turn's snapshot (for the diagnosis)")
    args = ap.parse_args(argv)
    started = time.time()
    runs = []
    for i, seed in enumerate(SEED_NAMES[:args.seeds]):
        t0 = time.time()
        runs.append(one_seed(seed, i, args.turns))
        print(f"seed {seed}: {len(runs[-1]['turns'])} turns, {time.time() - t0:.0f}s", flush=True)
    result = {"tool": "tools/_ic4b_measure.py", "seeds": args.seeds, "turns": args.turns,
              "men": list(MEN), "bars": BARS, "score": score(runs),
              "not_taken": not_taken(runs),
              "passes": {r["seed"]: len(r["turns"]) for r in runs},
              "stalls": [dict(s, seed=r["seed"]) for r in runs for s in r.get("stalls") or []][:30],
              "seconds": round(time.time() - started)}
    if args.dump:
        pathlib.Path(args.dump).write_text(json.dumps(runs, default=list), encoding="utf-8")
    out = pathlib.Path(args.out) if args.out else ROOT / "tools" / (
        "_ic4b_judgement_" + time.strftime("%Y_%m_%d") + ".json")
    out.write_text(json.dumps(result, indent=1, default=list), encoding="utf-8")
    print(json.dumps({k: (v if k != "R-ACTS" else {kk: vv for kk, vv in v.items() if kk != "per_man"})
                      for k, v in result["score"].items()}, indent=1, default=list))
    print(json.dumps(result["score"]["R-ACTS"]["per_man"], indent=1, default=list))
    print("written", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
