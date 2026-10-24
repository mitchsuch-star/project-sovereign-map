"""S14d part 2 — the Table's board, measured (`docs/TABLE_LESSON_SPEC.md`
§4.1, §6 part 2; the gate's `scratchpad/critA/tboard.py` sweeps, committed).

The lesson's arithmetic, read off the booted board the way the client will
read it — never a formula of our own — and then the lesson's three turns
PLAYED, for real, through the endpoints the client uses:

    1. the whole-war PROPOSE table on `war_1`, STAGED the way the lesson's
       door stages it (the client's `_on_war_settlement_clicked` sends
       `propose common peace with Austria`): every court's total against the
       threshold, and whether Austria's row carries the "Separate peace with
       Austria" chip (the engine's rule: the row at or above the threshold);
    2. the separate peace the chip hands off — Austria's slice of the staged
       package in the bilateral dialect (`_pair_substitute_seed_terms`),
       scored by the chip's own estimate (`bilateral_estimate`) — beside
       Talleyrand's TYPED draft (`generate_suggested_terms`) for the record;
    3. Bavaria's vassalage on the suggested terms (the Cabinet's confirm
       through the executor), and the estimate after ONE "More generous";
    4. the script: turn 1 — Reassure Bavaria, the table, the chip, Proceed,
       Send; turn 2 — Austria's answer, vassalage to Bavaria eased once and
       sent; turn 3 — Bavaria's answer; one more morning for strays. Every
       morning: the letters that arrive, the battles fought (none), the DP
       purse, the pair states, Austria's and Russia's rows.

    .venv/Scripts/python.exe tools/_table_board_probe.py [--board <json>] [--out <record.json>] [--turns 3]

Writes the record (default tools/_table_board_probe_final.json) and prints
the table. Exit 1 when a §4.1 clause fails — the pins in
tests/test_tutorial_table_scenario.py read the same seams.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MAPS = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
DEFAULT_BOARD = MAPS / "tutorial_table_1805.json"
DEFAULT_OUT = ROOT / "tools" / "_table_board_probe_final.json"
THRESHOLD_MARGIN = 3        # §4.1: Austria's row holds the threshold with this margin
TABLE_COMMAND = "propose common peace with Austria"   # what the door sends (main.gd)


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def _post(client, path: str, body: dict) -> dict:
    return _quiet(lambda: client.post(path, json=body).json()) or {}


def _dialogue(response: dict) -> dict:
    return (response or {}).get("diplomatic_dialogue") or {}


def _labels(dialogue: dict):
    return [o.get("label") for o in (dialogue.get("options") or []) if isinstance(o, dict)]


def _pick(client, dialogue: dict, *, action: str | None = None, label: str | None = None) -> dict:
    """Answer a dialogue the way the client does — by the 1-based index of the
    option (main.gd's index path), never a typed keyword."""
    options = [o for o in (dialogue.get("options") or []) if isinstance(o, dict)]
    for i, o in enumerate(options, start=1):
        if (action is not None and o.get("action") == action) or (label is not None and str(o.get("label") or "") == label):
            body = {"choice": i}
            if dialogue.get("dialogue_id") is not None:
                body["dialogue_id"] = dialogue.get("dialogue_id")
            return _post(client, "/respond_to_diplomatic_dialogue", body)
    raise RuntimeError(f"no option {action or label!r} on {dialogue.get('type')!r}: {_labels(dialogue)}")


def _chip(dialogue: dict, court: str):
    for row in dialogue.get("per_court_acceptance") or []:
        if isinstance(row, dict) and row.get("nation") == court:
            for a in row.get("dial_actions") or []:
                if isinstance(a, dict) and a.get("action") == "seek_bilateral_peace":
                    return a
    return None


def _rows(world, court: str):
    from backend.game_logic.diplomacy import get_available_diplomatic_actions
    acts = get_available_diplomatic_actions(world, court)
    acts = acts.get("actions") if isinstance(acts, dict) else acts
    return {a.get("action"): a for a in (acts or []) if isinstance(a, dict)}


def _row_summary(r: dict) -> dict:
    return {
        "total": r.get("total"), "threshold": r.get("threshold"), "band": r.get("band"),
        "direct_score": r.get("direct_score"),
        "top_blocker": r.get("top_blocker_display"),
        "components": {c.get("component"): c.get("value") for c in (r.get("component_breakdown") or [])
                       if isinstance(c, dict) and c.get("value")},
        "chip": [a.get("label") for a in (r.get("dial_actions") or [])
                 if isinstance(a, dict) and a.get("action") == "seek_bilateral_peace"],
    }


def table(world, client=None, court: str = "Austria"):
    """1. the whole-war PROPOSE table on war_1 — STAGED through the door's own
    command when a client is given (the rows then carry their dial actions
    and the separate-peace chip; backed out afterwards; `court` names the
    enemy the door is opened on — Austria on turn 1, Russia once Austria has
    signed); the preview alone when no client is given (no chips). Returns
    (rows, ok, covered, staged_terms)."""
    if client is not None:
        dm = world.dialogue_manager
        held_current, held_queue = dm._current, list(dm._queue)
        dm._current, dm._queue = None, []
        drafted = _post(client, "/command", {"command": f"propose common peace with {court}"})
        dialogue = _dialogue(drafted)
        rows = [r for r in (dialogue.get("per_court_acceptance") or []) if isinstance(r, dict)]
        ok = True if dialogue.get("type") == "settlement_confirm" else (
            f"refused: {drafted.get('error')} / {drafted.get('error_display')} / {drafted.get('display_reason')} / "
            f"{drafted.get('disabled_reason_display')} / awaiting={drafted.get('awaiting_diplomatic_response')} / "
            f"msg={str(drafted.get('message') or '')[:160]}")
        covered = dialogue.get("covered_enemy_participants")
        staged = [t for t in (dialogue.get("settlement_terms") or []) if isinstance(t, dict)]
        _post(client, "/respond_to_diplomatic_dialogue",
              {"choice": "back_out_settlement", "dialogue_id": dialogue.get("dialogue_id")})
        dm._current, dm._queue = held_current, held_queue
    else:
        from backend.game_logic.settlement_staging import build_settlement_preview
        try:
            preview = _quiet(build_settlement_preview, world, war_id="war_1", settlement_terms=[],
                             actor_nation="France", ignore_active_dialogue=True, declared_when_empty=True)
        except Exception as exc:   # the war may have changed shape after a peace
            return {}, f"preview failed: {exc}", None, []
        body = preview.get("settlement_preview") or {}
        rows = [r for r in (body.get("per_court_acceptance") or []) if isinstance(r, dict)]
        ok, covered, staged = preview.get("success"), body.get("covered_enemy_participants"), []
    return {str(r.get("nation")): _row_summary(r) for r in rows}, ok, covered, staged


def separate_peace(world, staged_terms):
    """2. the separate peace the chip hands off (the lesson's road) beside
    Talleyrand's typed draft (the record's)."""
    from backend.game_logic.diplomacy import calculate_acceptance
    from backend.game_logic.diplomatic_templates import generate_suggested_terms
    from backend.game_logic.settlement_staging import _pair_substitute_seed_terms, bilateral_estimate
    seed = _pair_substitute_seed_terms([t for t in staged_terms if isinstance(t, dict)],
                                       target="Austria", proposer_leader="France")
    estimate = _quiet(bilateral_estimate, world, "Austria", staged_terms=staged_terms, actor="France")
    typed = _quiet(generate_suggested_terms, "Austria", "peace", world, deterministic=True)
    proposal = {"type": typed.get("type") or "peace", "proposer_nation": "France", "target_nation": "Austria",
                "sweeteners": list(typed.get("sweeteners") or []),
                "demands": list(typed.get("demands") or []),
                "clauses": list(typed.get("clauses") or [])}
    verdict = _quiet(calculate_acceptance, proposal, world)
    return {
        "chip": {"demands": seed["demands"], "sweeteners": seed["sweeteners"],
                 "score": int(estimate.get("score", 0)), "outcome": estimate.get("outcome"), "band": estimate.get("band")},
        "typed_draft": {"demands": typed.get("demands"), "sweeteners": typed.get("sweeteners"),
                        "score": int(verdict.get("score", 0)), "outcome": verdict.get("outcome"),
                        "components": {k: int(v) for k, v in (verdict.get("components") or {}).items()
                                       if isinstance(v, (int, float)) and v}},
    }


def vassal(world, M, client):
    """3. Bavaria's vassalage: the Cabinet's row, the confirm's estimate, and
    the estimate after ONE 'More generous' — through the executor's own
    roads (the typed verb is the instrument's, never the lesson's); withdrawn."""
    row = _rows(world, "Bavaria").get("propose_vassal") or {}
    dlg = _dialogue(_post(client, "/command", {"command": "propose vassalage to Bavaria"}))
    first = {"estimate": dlg.get("acceptance_estimate"), "outcome": dlg.get("acceptance_outcome"),
             "display": dlg.get("acceptance_outcome_display"), "options": _labels(dlg)}
    eased = {}
    if "More generous" in first["options"]:
        d2 = _dialogue(_pick(client, dlg, label="More generous"))
        eased = {"estimate": d2.get("acceptance_estimate"), "outcome": d2.get("acceptance_outcome"),
                 "display": d2.get("acceptance_outcome_display")}
    # leave the board as it stood (the confirm is withdrawn, nothing sent)
    _post(client, "/respond_to_diplomatic_dialogue", {"choice": "Reconsider"})
    world.dialogue_manager._queue = []
    world.dialogue_manager._current = None
    return {"row": {"available": row.get("available"), "dp_cost": row.get("dp_cost"),
                    "likelihood": row.get("likelihood"), "disabled_reason": row.get("disabled_reason")},
            "suggested": first, "eased_once": eased}


def end_turn(client, world, limit: int = 4) -> dict:
    before = int(world.current_turn)
    response = _post(client, "/command", {"command": "end turn"})
    for _ in range(limit):
        pending = getattr(world, "pending_capture_choice", None)
        if int(world.current_turn) > before or not pending:
            break
        choice = "respect" if (pending or {}).get("stage") == "estate" else "secure"
        _post(client, "/command", {"command": choice})
        response = _post(client, "/command", {"command": "end turn"})
    return response


LETTER_TYPES = ("incoming_proposal", "counter_offer", "counter_offer_response",
                "incoming_ultimatum", "incoming_settlement_offer")


def _letters(world):
    dm = world.dialogue_manager
    out = []
    for d in [dm.peek()] + list(dm.iter_queue()):
        if isinstance(d, dict) and d.get("type") in LETTER_TYPES:
            payload = d.get("popup_payload") or {}
            out.append({"from": d.get("target_nation") or d.get("from_nation")
                        or d.get("proposer_nation") or d.get("offering_nation")
                        or payload.get("from_nation") or payload.get("proposer_nation")
                        or payload.get("offering_nation") or payload.get("leader"),
                        "type": d.get("type"),
                        "proposal_type": (d.get("proposal") or {}).get("type") or payload.get("proposal_type")})
    return out


def _events(response: dict):
    out = []
    for e in (response or {}).get("events") or []:
        if not isinstance(e, dict):
            continue
        t = str(e.get("type") or "")
        if any(w in t for w in ("treaty", "proposal", "peace", "vassal", "ratif")):
            out.append({k: e.get(k) for k in ("type", "outcome", "nation", "target_nation", "from_nation",
                                              "proposer_nation", "proposal_type", "new_state", "message") if k in e})
    return out


def _where(world, name):
    m = world.get_marshal(name)
    return None if m is None else {"location": m.location, "strength": int(m.strength)}


def scores(world):
    """The STORED pair scores beside the LIVE formula. Turn 1 reads the STORED
    figure everywhere — the table's `direct_score`, Talleyrand's draft
    (`get_side_war_score_for`), the bilateral verdict's war-score, supremacy
    and pressure terms (the field is read only on a turn a battle moved it,
    PC-F71) — and the first end turn rewrites it to the live one; unauthored
    it reads 0 and Austria's row reads 0 (measured, Oct 24, 2026). So the
    board authors `war_scores` to the live formula's figure and this pins
    them equal: the table reads the same number on turn 1 as on turn 2."""
    from backend.game_logic.diplomacy import calculate_war_score
    out = {}
    for court in ("Austria", "Russia"):
        key = world._make_diplo_key("France", court)
        if world.diplomatic_states.get(key) != "WAR":
            out[court] = {"key": key, "state": world.diplomatic_states.get(key)}
            continue
        live = calculate_war_score("France", court, world, return_components=True)
        stored = int(world.war_scores.get(key, 0))
        # the stored figure is the alphabetically-first court's view: France's
        # +N against Austria is stored as -N on "Austria|France"
        if key.split("|")[0] != "France":
            stored = -stored
        out[court] = {"key": key, "stored": stored,
                      "live_france_view": int(live["total"]) if isinstance(live, dict) else int(live),
                      "components": {k: int(v) for k, v in live.items()} if isinstance(live, dict) else None}
    return out


def _state(world, a: str, b: str):
    return world.diplomatic_states.get(world._make_diplo_key(a, b))


def script(client, world, turns: int):
    """4. the lesson's turns, for real, through the endpoints the client uses
    (the typed verbs stand for the Cabinet's rows — the instrument's, never
    the lesson's)."""
    rec = {"acts": [], "mornings": []}

    def battles_fought() -> int:
        # the authored record sits at turns <= 0 and a ratified peace PURGES the
        # pair's records — so count the records the script's turns wrote
        return sum(1 for recs in world.battle_records.values() for r in recs
                   if isinstance(r, dict) and int(r.get("turn", -99) or -99) >= 1)

    def act(name: str, response: dict) -> dict:
        d = _dialogue(response)
        rec["acts"].append({"turn": int(world.current_turn), "act": name,
                            "success": bool(response.get("success", True)),
                            "dp_after": int(world.diplomatic_points), "dialogue": d.get("type"),
                            "options": _labels(d), "message": str(response.get("message") or "")[:200]})
        return d

    # turn 1 — the mission (card I: the Cabinet's Reassure row, 1 DP a turn)
    d = act("reassure Bavaria", _post(client, "/command", {"command": "reassure Bavaria"}))
    if d.get("type") == "mission" and any(isinstance(o, dict) and o.get("action") == "start_mission" for o in (d.get("options") or [])):
        act("Begin mission", _pick(client, d, action="start_mission"))
    mission = getattr(world, "active_diplomatic_mission", None) or {}
    rec["mission"] = ({k: mission.get(k) for k in ("type", "target_nation", "turns_active", "dp_cost") if k in mission}
                      if isinstance(mission, dict) else str(mission))

    # turn 1 — the table (card II), the chip (card III), Proceed, Send
    d1 = act("open the table", _post(client, "/command", {"command": TABLE_COMMAND}))
    chip = _chip(d1, "Austria")
    rec["chip"] = {k: chip.get(k) for k in ("label", "available", "disabled_reason_display", "bilateral_estimate")} if chip else None
    if chip is not None:
        body = {"choice": "seek_bilateral_peace", "action_params": dict(chip)}
        if d1.get("dialogue_id") is not None:
            body["dialogue_id"] = d1.get("dialogue_id")
        d2 = act("Separate peace with Austria (the chip)", _post(client, "/respond_to_diplomatic_dialogue", body))
        if d2.get("type") == "settlement_pair_substitute_confirm":
            d3 = act("Proceed — peace with Austria alone", _pick(client, d2, action="confirm_pair_substitute"))
            rec["bilateral_draft"] = {
                "type": d3.get("type"), "estimate": d3.get("acceptance_estimate"),
                "outcome": d3.get("acceptance_outcome"), "display": d3.get("acceptance_outcome_display"),
                "terms": next((o.get("terms") for o in (d3.get("options") or [])
                               if isinstance(o, dict) and o.get("action") == "execute_proposal"), None)}
            if d3.get("type") == "proposal_confirm":
                act("Send these terms", _pick(client, d3, action="execute_proposal"))
    pit = getattr(world, "proposal_in_transit", None)
    rec["in_transit_after_turn_1"] = ({k: (pit.get(k) if not isinstance(pit.get(k), dict) else sorted(pit.get(k).keys()))
                                       for k in sorted(pit.keys())} if isinstance(pit, dict) else bool(pit))

    for _ in range(turns):
        response = end_turn(client, world)
        # the table each morning through the door's own road (the rows the
        # client would show; backed out) — the preview alone cannot read a
        # war whose shape a peace has changed
        # once Austria has signed, war_1 is France against Russia alone and the
        # table does not open on a one-to-one war (`one_to_one_war` — the
        # court's own page settles it); the row read then is the refusal
        court = "Austria" if _state(world, "France", "Austria") == "WAR" else "Russia"
        rows, table_ok, _cov, _terms = table(world, client, court)
        rec["mornings"].append({
            "turn": int(world.current_turn), "dp": int(world.diplomatic_points),
            "events": _events(response), "letters": _letters(world),
            "battles_fought": battles_fought(), "table_ok": table_ok,
            "austria_state": _state(world, "France", "Austria"),
            "russia_state": _state(world, "France", "Russia"),
            "bavaria_state": _state(world, "France", "Bavaria"),
            "austria_row": rows.get("Austria"), "russia_row": rows.get("Russia"),
            "charles": _where(world, "ArchdukeCharles"), "scores": scores(world),
            "wars": sorted(world.war_instances) if isinstance(getattr(world, "war_instances", None), dict) else None,
        })
        if int(world.current_turn) == 2:
            # turn 2 — vassalage to Bavaria (card V), eased once, sent
            dv = act("propose vassalage to Bavaria", _post(client, "/command", {"command": "propose vassalage to Bavaria"}))
            if "More generous" in _labels(dv):
                dv = act("More generous", _pick(client, dv, label="More generous"))
            rec["vassal_draft"] = {"estimate": dv.get("acceptance_estimate"), "outcome": dv.get("acceptance_outcome"),
                                   "display": dv.get("acceptance_outcome_display")}
            if any(isinstance(o, dict) and o.get("action") == "execute_proposal" for o in (dv.get("options") or [])):
                act("Send these terms (vassalage)", _pick(client, dv, action="execute_proposal"))
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--board", default=str(DEFAULT_BOARD))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--turns", type=int, default=3)
    args = ap.parse_args()
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "PYTHONIOENCODING"):
        os.environ.pop(key, None)
    os.environ["LLM_MODE"] = "mock"
    from fastapi.testclient import TestClient
    save_dir = Path(tempfile.mkdtemp(prefix="table_probe_")) / "saves"
    import hashlib
    board_path = Path(args.board)
    record = {"board": str(board_path.relative_to(ROOT)) if board_path.is_absolute() else args.board,
              # the pins read the committed record only while it is THIS board's
              "board_sha256": hashlib.sha256(board_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()}
    with patch("backend.save_manager.SAVE_DIR", save_dir):
        import backend.main as M
        from backend.commands.parser import CommandParser
        _quiet(M._reset_world_state, scenario_override=str(args.board))
        M.parser = CommandParser(use_real_llm=False)
        with TestClient(M.app) as client:
            world = M.game_state["world"]
            record["turn_1"] = {
                "dp": int(world.diplomatic_points), "gold": int(world.gold),
                "wars": sorted(world.war_instances) if isinstance(getattr(world, "war_instances", None), dict) else None,
                "held": {n: world.regions[n].controller for n in ("Vienna", "Tyrol", "Moravia", "Carniola")},
                "exhaustion": dict(world.war_exhaustion),
                "scores": scores(world),
            }
            rows, ok, covered, staged = table(world, client)
            record["table"] = {"success": ok, "covered": covered, "staged_terms": staged, "rows": rows}
            record["separate_peace"] = separate_peace(world, staged)
            record["bavaria"] = vassal(world, M, client)
            record["script"] = script(client, world, args.turns)
        _quiet(M._reset_world_state)

    # ── the §4.1 clauses ────────────────────────────────────────────────────
    austria = (record["table"]["rows"].get("Austria") or {})
    russia = (record["table"]["rows"].get("Russia") or {})
    thr = int(austria.get("threshold") or 50)
    mornings = record["script"]["mornings"]
    clauses = {
        "one_war_instance": record["turn_1"]["wars"] == ["war_1"],
        "vienna_tyrol_moravia_french": (all(record["turn_1"]["held"][n] == "France" for n in ("Vienna", "Tyrol", "Moravia"))
                                        and record["turn_1"]["held"]["Carniola"] == "Austria"),
        "stored_score_is_the_live_one": all(abs(s["stored"] - s["live_france_view"]) <= 1
                                            for s in record["turn_1"]["scores"].values() if "stored" in s),
        "austria_at_threshold_with_margin": austria.get("total") is not None and int(austria["total"]) >= thr + THRESHOLD_MARGIN,
        "russia_below_threshold": russia.get("total") is not None and int(russia["total"]) < thr,
        "chip_on_austria": bool(austria.get("chip")),
        "bilateral_accepts": record["separate_peace"]["chip"]["outcome"] == "ACCEPT",
        "vassal_counter_then_accept": (record["bavaria"]["suggested"].get("outcome") == "COUNTER_OFFER"
                                       and record["bavaria"]["eased_once"].get("outcome") == "ACCEPT"),
        "every_act_succeeded": all(a["success"] for a in record["script"]["acts"]),
        "austria_signs_the_second_morning": bool(mornings) and mornings[0]["austria_state"] == "PEACE",
        "russia_still_at_war": bool(mornings) and mornings[0]["russia_state"] == "WAR",
        "bavaria_vassal_the_third_morning": len(mornings) >= 2 and mornings[1]["bavaria_state"] == "VASSAL",
        "no_stray_letter": all(not [l for l in m["letters"] if l["from"] != "Austria"] for m in mornings),
        "no_battle": all(m["battles_fought"] == 0 for m in mornings),
        "russia_at_war_every_morning": all(m["russia_state"] == "WAR" for m in mornings),
        "russia_never_reaches_the_table": all((m["russia_row"] or {}).get("total") is None
                                              or int(m["russia_row"]["total"]) < thr for m in mornings),
    }
    record["clauses"] = clauses
    Path(args.out).write_text(json.dumps(record, indent=1, ensure_ascii=False, default=str) + chr(10), encoding="utf-8")

    t1 = record["turn_1"]
    print(f"board {record['board']} — turn 1: DP {t1['dp']}, gold {t1['gold']}, wars {t1['wars']}, held {t1['held']}, exhaustion {t1['exhaustion']}")
    for court, s in t1["scores"].items():
        if "stored" in s:
            print(f"  score {court}: stored {s['stored']} (key {s['key']}) live(France) {s['live_france_view']} {s['components']}")
    print(f"  staged terms: {json.dumps(record['table']['staged_terms'], ensure_ascii=False)}")
    for court, r in rows.items():
        print(f"  {court:16s} {str(r['total']):>5} / {r['threshold']}  {str(r['band']):16s} direct {r['direct_score']}  chip={r['chip']}  {r['components']}")
    sp = record["separate_peace"]
    print(f"  the chip's peace: {sp['chip']['score']} {sp['chip']['outcome']} ({sp['chip']['band']}) — {json.dumps(sp['chip']['demands'], ensure_ascii=False)}")
    print(f"  Talleyrand's typed draft: {sp['typed_draft']['score']} {sp['typed_draft']['outcome']} — {json.dumps(sp['typed_draft']['demands'], ensure_ascii=False)}")
    b = record["bavaria"]
    print(f"  Bavaria vassal row: {b['row']} | suggested: {b['suggested'].get('estimate')} {b['suggested'].get('outcome')} "
          f"| eased once: {b['eased_once'].get('estimate')} {b['eased_once'].get('outcome')}")
    sc = record["script"]
    print(f"  mission: {sc.get('mission')} | chip: {sc.get('chip')}")
    print(f"  bilateral draft: {sc.get('bilateral_draft')}")
    print(f"  in transit after turn 1: {sc.get('in_transit_after_turn_1')} | vassal draft: {sc.get('vassal_draft')}")
    for a in sc["acts"]:
        print(f"    t{a['turn']} {a['act']:40s} ok={a['success']} DP={a['dp_after']} -> {a['dialogue']} {a['options']} | {a['message'][:90]}")
    for m in mornings:
        print(f"  morning t{m['turn']}: DP {m['dp']}, Austria {m['austria_state']}, Russia {m['russia_state']}, Bavaria {m['bavaria_state']}, "
              f"wars {m['wars']}, battles {m['battles_fought']}, letters {m['letters']}, events {m['events']}, "
              f"rows A {(m['austria_row'] or {}).get('total')} R {(m['russia_row'] or {}).get('total')}, Charles {m['charles']}")
    bad = [k for k, v in clauses.items() if not v]
    print("clauses:", "ALL HOLD" if not bad else f"FAILING {bad}")
    print("record:", args.out)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
