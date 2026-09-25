"""IQ-10 "The Client Pass" — capture the payloads the offscreen harness renders.

    .venv/Scripts/python.exe tools/iq10_capture_payloads.py [--out DIR] [--only NAME ...]

Every surface row IQ-10 owes a frame of is drawn by
`tools/iq10_surface_screenshot.gd` from a REAL backend payload. This script
produces those payloads, in-process (FastAPI `TestClient`, no server, no port,
the player's live 8005 never touched), off boards that are STAGED — each
capture says in its `staging` note exactly what was done to the shipped 1805
boot to reach the state, and which of it was a direct state write rather than
a played road. Nothing here is rendered by hand: a payload is what an endpoint
or a production builder returned, written out unedited.

The boards are the rows' OWN test boards, imported rather than re-typed, so a
frame is of the state the row's pins are about:

    IQ-2   tests/test_iq2_collapse_integration.py        `_collapsed()`
    IQ-4   tests/test_iq4_cabinet_visible.py             the typed mission road
    IQ-5   tests/test_iq5_both_sides_of_the_butchers_bill.py  `_battle(D_ADJ, …, seed=3)`
    IQ-7   tests/test_iq7_satellites_have_a_position.py  `_make_eligible` / `_deliver`
    t10/t20  tests/fixtures/playtest_saves/*.json via POST /load

Rules this script keeps (the row's brief):
  * the mock parser, always — `LLM_MODE=mock` is set BEFORE `backend.main` is
    imported (its import builds a parser singleton and runs `load_dotenv()`,
    which never overrides a variable already set), and every world swap swaps
    `M.world` + `M.game_state["world"]` + `M.parser` together (the TestClient
    world-swap rule);
  * saves are sandboxed — `INK_IRON_SAVE_DIR` points under the output dir, so
    the autosave `/load` and `end turn` write never reaches the repo `saves/`;
  * payload JSONs are NOT committed — the default output dir is outside the
    repo (the system temp dir); the runner reads the same default.

Output: `<out>/<name>.json` per capture + `<out>/manifest.json` — name,
staging note, the endpoint or builder it came from, and `facts`: the figures
and strings the frame must show, read OFF the payload (so a reader can check
the picture against the data without opening the payload).
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import random
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = Path(tempfile.gettempdir()) / "iq10_client_pass" / "payloads"
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")
FIXTURES = REPO / "tests" / "fixtures" / "playtest_saves"
PLAYER = "France"

M = None            # backend.main, imported by `boot_backend`
PARSER = None
_OUT: Path = DEFAULT_OUT
_MANIFEST: list = []
_TEST_MODULES: dict = {}


# ═══════════════════════════════════════════════════════════════════════
# boot
# ═══════════════════════════════════════════════════════════════════════

def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def boot_backend(out_dir: Path) -> None:
    """Set the environment, THEN import the backend (the import boots a world
    and builds the parser singleton)."""
    global M, PARSER
    os.environ["LLM_MODE"] = "mock"
    os.environ["SOVEREIGN_SEED"] = "historical"
    os.environ["INK_IRON_SAVE_DIR"] = str(out_dir / "_saves")
    os.environ["DEBUG_MODE"] = "false"
    # SET, never pop: a popped variable is what `load_dotenv()` fills back in.
    os.environ["SOVEREIGN_SCENARIO"] = ""
    os.environ["SOVEREIGN_SMOKE_START"] = ""
    os.environ["SOVEREIGN_MAP"] = "europe"
    (out_dir / "_saves").mkdir(parents=True, exist_ok=True)
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    with _quiet():
        import backend.main as backend_main
        from backend.commands.parser import CommandParser
        PARSER = CommandParser(use_real_llm=False)
    M = backend_main
    assert PARSER.llm.use_real_api is False, "the capture must never reach a live parser"


def test_module(name: str):
    """A row's own test module, imported by path for its STAGING helpers
    (`tests/` is not a package). Its fixtures are never run here."""
    if name not in _TEST_MODULES:
        path = REPO / "tests" / f"{name}.py"
        spec = importlib.util.spec_from_file_location(f"_iq10_{name}", path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"staging helpers missing: {path}")
        module = importlib.util.module_from_spec(spec)
        with _quiet():
            spec.loader.exec_module(module)
        _TEST_MODULES[name] = module
    return _TEST_MODULES[name]


def seed_rng(turn: int = 0) -> None:
    """The driver's determinism scheme — combat jitter and the courting roll
    ride the unseeded `random` module."""
    digest = hashlib.sha256(f"historical:{turn}".encode()).hexdigest()
    random.seed(int(digest, 16) & 0xFFFFFFFF)


def adopt(world):
    """The TestClient world-swap rule: all three, together."""
    from fastapi.testclient import TestClient
    M.world = world
    M.game_state["world"] = world
    M.parser = PARSER
    return TestClient(M.app)


def fresh():
    from backend.models.world_state import WorldState
    with _quiet():
        world = WorldState.from_scenario(SCENARIO)
    seed_rng()
    return world, adopt(world)


def get(client, path):
    with _quiet():
        return client.get(path).json()


def post(client, path, body):
    with _quiet():
        return client.post(path, json=body).json()


def cmd(client, text):
    return post(client, "/command", {"command": text})


def live_world():
    return M.game_state["world"]


def clear_dialogues(world) -> None:
    """Empty the dialogue slot so a delivered letter is CURRENT — exactly a
    turn with no other mail (the IQ7-X5 probe's `clear_slot`)."""
    dm = world.dialogue_manager
    dm._queue = []
    dm._current = None
    world.incoming_proposal_popup = None
    world.proposal_result_popup = None


def end_turn(client, limit: int = 4):
    """One REAL end turn, answering the ordinary capture question the unplayed
    board asks (secure / respect) the way the driver's default policy does."""
    world = live_world()
    before = int(world.current_turn)
    response = cmd(client, "end turn")
    for _ in range(limit):
        world = live_world()
        pending = getattr(world, "pending_capture_choice", None)
        if int(world.current_turn) > before or not pending:
            break
        cmd(client, "respect" if pending.get("stage") == "estate" else "secure")
        response = cmd(client, "end turn")
    return response


# ═══════════════════════════════════════════════════════════════════════
# recording
# ═══════════════════════════════════════════════════════════════════════

def record(name: str, payload, *, source: str, staging: str, facts: dict | None = None):
    path = _OUT / f"{name}.json"
    path.write_text(json.dumps(payload, indent=1, ensure_ascii=False, default=str),
                    encoding="utf-8")
    _MANIFEST.append({"name": name, "file": str(path).replace("\\", "/"),
                      "source": source, "staging": staging, "facts": facts or {}})
    print(f"  captured {name}  ({path.stat().st_size // 1024} KB)")
    return payload


def econ_facts(ledger_response: dict) -> dict:
    econ = (ledger_response.get("ledger") or {}).get("economy") or {}
    levy = econ.get("levy") or {}
    return {
        "treasury": econ.get("treasury"), "net": econ.get("net"),
        "spent": econ.get("spent"), "ceiling": econ.get("ceiling"),
        "ceiling_state": econ.get("ceiling_state"),
        "materiel": econ.get("materiel"),
        "levy_open": levy.get("open"), "levy_closed_reason": levy.get("closed_reason"),
        "collapse_note": (ledger_response.get("ledger") or {}).get("collapse_note"),
    }


def cabinet_facts(ledger_response: dict) -> dict:
    cab = (ledger_response.get("ledger") or {}).get("cabinet") or {}
    keys = ("live", "type", "type_display", "target_display", "target_ally_display",
            "effect_per_turn", "drift_per_turn", "net_per_turn", "current_relation",
            "relation_descriptor", "remaining_note", "dp_per_turn", "paused",
            "pause_reason", "recall_command", "favour_now", "favour_cap", "last")
    return {k: cab.get(k) for k in keys if k in cab}


def talleyrand_facts(dl_response: dict) -> dict:
    t = (dl_response.get("ledger") or {}).get("talleyrand") or {}
    return {"authority_label": t.get("authority_label"), "authority": t.get("authority"),
            "active_mission": t.get("active_mission"), "last_mission": t.get("last_mission"),
            "dp_remaining": t.get("dp_remaining"), "dp_max": t.get("dp_max")}


# ═══════════════════════════════════════════════════════════════════════
# captures
# ═══════════════════════════════════════════════════════════════════════

def cap_boot():
    """The shipped 1805 boot, untouched."""
    world, c = fresh()
    ledger = get(c, "/ledger")
    record("ledger_boot", ledger, source="GET /ledger",
           staging="1805 boot, turn 1, nothing done",
           facts={**econ_facts(ledger), "cabinet": cabinet_facts(ledger)})
    dl = get(c, "/diplomatic_ledger")
    vassals = (dl.get("ledger") or {}).get("vassals") or {}
    record("diplo_ledger_boot", dl, source="GET /diplomatic_ledger",
           staging="1805 boot, turn 1, nothing done",
           facts={"talleyrand": talleyrand_facts(dl),
                  "vassal_rows": [
                      {k: v.get(k) for k in ("name", "display", "loyalty", "standing",
                                             "next_petition_in", "bond", "remission_left")}
                      for v in (vassals.get("rows") or []) if isinstance(v, dict)]})
    record("marshal_overview_boot", get(c, "/marshal_overview"),
           source="GET /marshal_overview", staging="1805 boot")
    test = get(c, "/test")
    record("test_boot", test, source="GET /test",
           staging="1805 boot — the response main.gd's `_on_connection_test` reads",
           facts={"talleyrand_mission_summary": test.get("talleyrand_mission_summary"),
                  "calendar_label": (test.get("action_summary") or {}).get("calendar_label"),
                  "threat_level": test.get("threat_level")})
    record("top_bar_fields_boot", {
        "diplomatic_points": test.get("diplomatic_points"),
        "max_diplomatic_points": test.get("max_diplomatic_points"),
        "threat_level": test.get("threat_level"),
        "coalition_brewing": test.get("coalition_brewing"),
        "talleyrand_mission_summary": test.get("talleyrand_mission_summary"),
        "pending_envoy_count": test.get("pending_envoy_count"),
        "pending_lapsing_count": test.get("pending_lapsing_count"),
        "pending_lapsing_petitions": test.get("pending_lapsing_petitions"),
        "pending_marshal_decisions": test.get("pending_marshal_decisions"),
        "turn": test.get("turn"),
        "calendar_label": (test.get("action_summary") or {}).get("calendar_label", ""),
        # NUI "The Admiralty on the Map": the chip's payload rides the map
        # summary (`naval_overlay.player_summary`); main.gd feeds it to
        # `top_bar.update_admiralty` on every map refresh.
        "naval_player_summary": ((test.get("game_state") or {}).get("naval_overlay")
                                 or {}).get("player_summary", {}),
    }, source="GET /test, the keys main.gd `_update_diplomatic_top_bar` copies",
        staging="1805 boot",
        facts={"talleyrand_mission_summary": test.get("talleyrand_mission_summary"),
               "must_render_as": "Talleyrand: Idle (the backend says 'None')"})
    wars = test.get("active_wars") or {}
    record("active_wars_boot", wars, source="GET /test → active_wars",
           staging="1805 boot (the Third Coalition standing)",
           facts={"war_count": len(wars.get("wars") or []),
                  "tier_sides": {w.get("opponent"): w.get("settlement_tier_side")
                                 for w in (wars.get("wars") or [])}})
    first = (wars.get("wars") or [{}])[0]
    record("war_detail_boot", {"war": first, "coalition": wars.get("coalition")},
           source="GET /test → active_wars.wars[0] + .coalition",
           staging="1805 boot", facts={"opponent": first.get("opponent"),
                                       "war_score": first.get("war_score")})
    record("mailbox_boot", get(c, "/mailbox"), source="GET /mailbox", staging="1805 boot")


def cap_spent():
    """S1 — a purchase this turn, so `economy.spent` is non-zero."""
    world, c = fresh()
    world.nation_gold[PLAYER] = 20000
    attempts = []
    for text in ("buy substitutes for Ney", "build market in Paris",
                 "build supply depot in Lorraine"):
        r = cmd(c, text)
        attempts.append({"command": text, "success": r.get("success"),
                         "message": str(r.get("message"))[:160]})
        ledger = get(c, "/ledger")
        if int(((ledger.get("ledger") or {}).get("economy") or {}).get("spent", 0) or 0) > 0:
            break
    ledger = get(c, "/ledger")
    record("ledger_spent", ledger, source="GET /ledger",
           staging="1805 boot; treasury WRITTEN to 20,000 (state write); then the typed "
                   "purchase(s) listed in facts.attempts through POST /command",
           facts={**econ_facts(ledger), "attempts": attempts})


def cap_ceiling_states():
    """S2 — the Ceiling line's five renderings."""
    world, c = fresh()
    base = get(c, "/ledger")
    ceiling = int(((base.get("ledger") or {}).get("economy") or {}).get("ceiling", 0) or 0)
    # bounded-warning is the boot itself (ledger_boot): ceiling > 4x the chest.
    if ceiling > 0:
        world.nation_gold[PLAYER] = int(ceiling * 0.6)
        calm = get(c, "/ledger")
        record("ledger_ceiling_calm", calm, source="GET /ledger",
               staging=f"1805 boot; treasury WRITTEN to 60% of the boot ceiling ({ceiling})",
               facts=econ_facts(calm))
        world.nation_gold[PLAYER] = int(ceiling * 1.5)
        above = get(c, "/ledger")
        record("ledger_ceiling_above", above, source="GET /ledger",
               staging=f"1805 boot; treasury WRITTEN to 150% of the boot ceiling ({ceiling})",
               facts=econ_facts(above))
    # unbounded: the charge RATE is 0. On a Europe world it never is (the crown
    # term is a standing 30 — `get_state_charges_rate`), so the arm is reachable
    # only on the 19-region legacy world, whose rate is 0 by construction (N1).
    from backend.models.world_state import WorldState
    with _quiet():
        legacy = WorldState(player_nation=PLAYER)
    c = adopt(legacy)
    unb = get(c, "/ledger")
    record("ledger_ceiling_unbounded", unb, source="GET /ledger",
           staging="the 19-region LEGACY world (`WorldState(player_nation='France')`, the "
                   "SOVEREIGN_MAP=legacy rollback) — the only board whose charge rate is 0; "
                   "no 1805 board can reach this arm (the crown term is a standing 30)",
           facts=econ_facts(unb))


def cap_collapse():
    """IQ-2 — the collapse board: S3/S4/S5/S10/S11/S17/S18 + S14/S15."""
    iq2 = test_module("test_iq2_collapse_integration")
    for tag, keep in (("one", ("Brittany",)), ("none", ())):
        with _quiet():
            world = iq2._collapsed(keep=keep)
        seed_rng()
        c = adopt(world)
        held = ", ".join(keep) if keep else "no province"
        staging = (f"tests/test_iq2_collapse_integration.py `_collapsed(keep={keep!r})`: every "
                   f"French province but {held} handed to Austria by a controller write")
        ledger = get(c, "/ledger")
        led = ledger.get("ledger") or {}
        pools = led.get("manpower") or {}
        record(f"ledger_collapse_{tag}", ledger, source="GET /ledger", staging=staging,
               facts={**econ_facts(ledger),
                      "manpower_depot_closed": {k: (v or {}).get("depot_closed")
                                                for k, v in pools.items() if isinstance(v, dict)},
                      "manpower_cost_note": {k: (v or {}).get("cost_note")
                                             for k, v in pools.items() if isinstance(v, dict)}})
        dl = get(c, "/diplomatic_ledger")
        boe = (dl.get("ledger") or {}).get("balance_of_europe") or {}
        record(f"diplo_ledger_collapse_{tag}", dl, source="GET /diplomatic_ledger",
               staging=staging,
               facts={"talleyrand": talleyrand_facts(dl),
                      "headline_case": boe.get("headline_case"),
                      "headline_note": boe.get("headline_note"),
                      "collapse_line": (boe.get("threat_projection") or {}).get("collapse_line")})
        wars = get(c, "/test").get("active_wars") or {}
        record(f"active_wars_collapse_{tag}", wars, source="GET /test → active_wars",
               staging=staging,
               facts={"tier_sides": {w.get("opponent"): w.get("settlement_tier_side")
                                     for w in (wars.get("wars") or [])}})
        losing = next((w for w in (wars.get("wars") or [])
                       if w.get("settlement_tier_side") == "theirs"), None)
        if losing is not None:
            record(f"war_detail_collapse_{tag}",
                   {"war": losing, "coalition": wars.get("coalition")},
                   source="GET /test → the first war with settlement_tier_side == 'theirs'",
                   staging=staging,
                   facts={"opponent": losing.get("opponent"), "war_score": losing.get("war_score"),
                          "settlement_tier": losing.get("settlement_tier"),
                          "settlement_tier_side": losing.get("settlement_tier_side")})

    # S11's cooldown arm: the league gone, the cooldown running, the collapse standing.
    with _quiet():
        world = iq2._collapsed(keep=("Brittany",))
    c = adopt(world)
    world.active_coalition = None
    world.coalition_brewing = None
    world.coalition_cooldown = 6
    dl = get(c, "/diplomatic_ledger")
    boe = (dl.get("ledger") or {}).get("balance_of_europe") or {}
    record("diplo_ledger_collapse_cooldown", dl, source="GET /diplomatic_ledger",
           staging="`_collapsed(keep=('Brittany',))`, then active_coalition/coalition_brewing "
                   "cleared and coalition_cooldown WRITTEN to 6 (state writes) — the COOLDOWN "
                   "headline case under the collapse",
           facts={"headline_case": boe.get("headline_case"),
                  "headline_note": boe.get("headline_note"),
                  "collapse_line": (boe.get("threat_projection") or {}).get("collapse_line")})

    # S17 / S18: the dispatch and the turn banner, off a REAL end turn on the
    # zero-province board with no French corps left in the field.
    with _quiet():
        world = iq2._collapsed(keep=())
        for m in list(world.marshals.values()):
            if m.nation == PLAYER and m.name != "Napoleon":
                world.destroy_marshal(m, cause="iq10_staging")
    seed_rng()
    c = adopt(world)
    response = end_turn(c)
    world = live_world()
    events = [e for e in (response.get("events") or []) if isinstance(e, dict)]
    banner = next((e for e in events if e.get("collapse_line")), None)
    dispatch = get(c, "/dispatch")
    situation = ((dispatch.get("dispatch") or {}).get("situation") or {})
    warning = (dispatch.get("dispatch") or {}).get("defeat_imminent_warning")
    staging = ("`_collapsed(keep=())`, every French marshal but Napoleon removed through "
               "`world.destroy_marshal` (state writes), then ONE real `end turn` through "
               "POST /command")
    record("dispatch_collapse", dispatch, source="GET /dispatch after the end turn",
           staging=staging,
           facts={"no_field_army": situation.get("no_field_army"),
                  "defeat_heading": (warning or {}).get("heading") if isinstance(warning, dict) else None,
                  "headline": ((dispatch.get("dispatch") or {}).get("headline") or {}).get("text")})
    record("end_turn_collapse", response, source="POST /command 'end turn' (whole response)",
           staging=staging,
           facts={"collapse_line": (banner or {}).get("collapse_line"),
                  "turn_after": int(world.current_turn),
                  "event_types": [e.get("type") for e in events][:12]})


def cap_peace_popups():
    """S14 — the two peace previews on a losing board: 'Settlement (theirs to impose)'."""
    iq2 = test_module("test_iq2_collapse_integration")
    from backend.game_logic.ai_diplomacy import deliver_ai_proposal
    with _quiet():
        world = iq2._collapsed(keep=("Brittany",))
    seed_rng()
    c = adopt(world)
    clear_dialogues(world)
    staging = "`_collapsed(keep=('Brittany',))`; dialogue slot emptied (state write)"
    proposal = {"source": "Austria", "recipient": PLAYER, "proposal_type": "peace",
                "priority": 1,
                "terms": {"type": "peace", "proposer_nation": "Austria",
                          "target_nation": PLAYER, "clauses": ["peace"],
                          "sweeteners": [], "demands": []},
                "talleyrand_assessment": "", "decision_reason": "war_weariness",
                "turn_generated": int(world.current_turn), "_force_send": True}
    with _quiet():
        delivered = deliver_ai_proposal(copy.deepcopy(proposal), world)
    response = cmd(c, "status")
    popup = response.get("incoming_proposal") or (delivered or {}).get("popup_payload")
    snap = (popup or {}).get("war_context_snapshot") or {}
    record("incoming_peace_losing", popup, source="POST /command 'status' → incoming_proposal "
           "(the delivered letter's popup, as the wire carries it)",
           staging=staging + "; an Austrian `peace` proposal handed to the production "
                             "`deliver_ai_proposal` (the AI rung was not waited for)",
           facts={"has_snapshot": bool(snap),
                  "settlement_tier_side": snap.get("settlement_tier_side"),
                  "settlement_tier_display": snap.get("settlement_tier_display")
                  or snap.get("settlement_tier"),
                  "war_score": snap.get("war_score")})

    with _quiet():
        world = iq2._collapsed(keep=("Brittany",))
    seed_rng()
    c = adopt(world)
    clear_dialogues(world)
    world.diplomatic_points = max(int(world.diplomatic_points), 5)
    drafted = cmd(c, "propose peace with Austria")
    dialogue = drafted.get("diplomatic_dialogue")
    dsnap = ((dialogue or {}).get("context") or {}).get("war_context_snapshot") \
        or (dialogue or {}).get("war_context_snapshot") or {}
    record("confirm_peace_losing", dialogue, source="POST /command 'propose peace with Austria' "
           "→ diplomatic_dialogue", staging=staging + "; the typed peace proposal",
           facts={"dialogue_type": (dialogue or {}).get("type"),
                  "settlement_tier_side": dsnap.get("settlement_tier_side"),
                  "message": str(drafted.get("message"))[:200]})


def cap_missions():
    """IQ-4 — the Cabinet on the ledger, the Talleyrand tab, the rail row, the top bar."""
    iq4 = test_module("test_iq4_cabinet_visible")

    def board(text, turns, tag, note):
        world, c = fresh()
        world.diplomatic_points = 10
        world.talleyrand_defiance_cooldown = 99       # no sabotage die on a send
        iq4.DD.MISSION_EFFECTS["COURT_NATION"]["undermine_chance"] = 0.0
        with _quiet():
            started = iq4._start_http(c, text)
        for _ in range(turns):
            live_world().diplomatic_points = 10
            end_turn(c)
        world = live_world()
        world.diplomatic_points = max(int(world.diplomatic_points), 5)
        staging = (f"1805 boot; DP written to 10 and the sabotage cooldown to 99; the typed "
                   f"road `{text}` + the confirm's Begin button; {turns} real end turn(s) "
                   f"(DP topped up each turn). {note}")
        ledger = get(c, "/ledger")
        record(f"ledger_mission_{tag}", ledger, source="GET /ledger", staging=staging,
               facts={"cabinet": cabinet_facts(ledger),
                      "begin_message": str(started.get("message"))[:200]})
        dl = get(c, "/diplomatic_ledger")
        record(f"diplo_ledger_mission_{tag}", dl, source="GET /diplomatic_ledger",
               staging=staging, facts={"talleyrand": talleyrand_facts(dl)})
        notes = get(c, "/notifications")
        rows = [n for n in (notes.get("notifications") or [])
                if n.get("type") == "diplomatic_mission"]
        record(f"notifications_mission_{tag}", notes.get("notifications") or [],
               source="GET /notifications → notifications", staging=staging,
               facts={"mission_rows": [{"title": r.get("title"), "message": r.get("message"),
                                        "details": r.get("details")} for r in rows]})
        test = get(c, "/test")
        record(f"top_bar_fields_mission_{tag}", {
            "diplomatic_points": test.get("diplomatic_points"),
            "max_diplomatic_points": test.get("max_diplomatic_points"),
            "threat_level": test.get("threat_level"),
            "coalition_brewing": test.get("coalition_brewing"),
            "talleyrand_mission_summary": test.get("talleyrand_mission_summary"),
            "pending_envoy_count": test.get("pending_envoy_count"),
            "turn": test.get("turn"),
            "calendar_label": (test.get("action_summary") or {}).get("calendar_label", ""),
        }, source="GET /test", staging=staging,
            facts={"talleyrand_mission_summary": test.get("talleyrand_mission_summary")})
        return world, c

    board("court Denmark", 3, "court", "COURT_NATION: the favour line should read +6 of +10.")
    board("improve relations with Prussia", 1, "improve", "IMPROVE_RELATIONS: effect/drift/net arm.")
    board("gather intelligence on Austria", 1, "gather", "GATHER_INTEL: the effect-text arm.")

    # UNDERMINE — the pair arm ('a turn from him'). Needs an allied pair.
    world, c = fresh()
    pair = None
    for a in ("Austria", "Russia", "Britain", "Prussia", "Spain"):
        for b in world.get_active_nations():
            if b in (a, PLAYER):
                continue
            try:
                if world.get_diplomatic_state(a, b) in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
                    pair = (a, b)
                    break
            except Exception:
                continue
        if pair:
            break
    if pair:
        world.diplomatic_points = 10
        world.talleyrand_defiance_cooldown = 99
        with _quiet():
            result = iq4._start_exec(world, "UNDERMINE_ALLIANCE", pair[0], ally=pair[1])
        ledger = get(c, "/ledger")
        staging = (f"1805 boot; the REAL `start_mission` dialogue arm driven by "
                   f"tests/test_iq4_cabinet_visible.py `_start_exec(UNDERMINE_ALLIANCE, "
                   f"{pair[0]}, ally={pair[1]})` (the wizard's confirm, without the wizard)")
        record("ledger_mission_undermine", ledger, source="GET /ledger", staging=staging,
               facts={"cabinet": cabinet_facts(ledger),
                      "start_message": str((result or {}).get("message"))[:200]})
        dl = get(c, "/diplomatic_ledger")
        record("diplo_ledger_mission_undermine", dl, source="GET /diplomatic_ledger",
               staging=staging, facts={"talleyrand": talleyrand_facts(dl)})

    # Transit: he carries a proposal while the mission stands (paused, no Recall).
    world, c = fresh()
    world.diplomatic_points = 10
    world.talleyrand_defiance_cooldown = 99
    with _quiet():
        iq4._start_http(c, "court Denmark")
        sent = iq4._send_http(c, "propose open borders with Sweden")
    ledger = get(c, "/ledger")
    record("ledger_mission_transit", ledger, source="GET /ledger",
           staging="1805 boot; `court Denmark` begun on the typed road, then an open-borders "
                   "proposal to Sweden SENT (typed echo + the confirm's Send) so Talleyrand "
                   "is in transit with the mission standing",
           facts={"cabinet": cabinet_facts(ledger), "talleyrand_state": world.talleyrand_state,
                  "send_message": str(sent.get("message"))[:200]})

    # Starved: the mission paused for want of DP.
    world, c = fresh()
    world.diplomatic_points = 10
    world.talleyrand_defiance_cooldown = 99
    with _quiet():
        iq4._start_http(c, "court Denmark")
    live_world().diplomatic_points = 0
    end_turn(c)
    live_world().diplomatic_points = 0
    ledger = get(c, "/ledger")
    record("ledger_mission_starved", ledger, source="GET /ledger",
           staging="1805 boot; `court Denmark` begun; DP WRITTEN to 0 before and after one "
                   "real end turn (state write) so the mission pauses for want of DP",
           facts={"cabinet": cabinet_facts(ledger)})

    # Recalled: the idle Cabinet with its 'Last mission' line, on both ledgers.
    world, c = fresh()
    world.diplomatic_points = 10
    world.talleyrand_defiance_cooldown = 99
    with _quiet():
        iq4._start_http(c, "court Denmark")
    end_turn(c)
    before = get(c, "/ledger")
    recall = ((before.get("ledger") or {}).get("cabinet") or {}).get("recall_command") or ""
    recalled = cmd(c, recall) if recall else {"message": "no recall_command on the cabinet"}
    ledger = get(c, "/ledger")
    staging = (f"1805 boot; `court Denmark` begun, one real end turn, then the Cabinet's own "
               f"recall_command `{recall}` typed through POST /command")
    record("ledger_mission_recalled", ledger, source="GET /ledger", staging=staging,
           facts={"cabinet": cabinet_facts(ledger),
                  "recall_message": str(recalled.get("message"))[:200]})
    dl = get(c, "/diplomatic_ledger")
    record("diplo_ledger_mission_recalled", dl, source="GET /diplomatic_ledger",
           staging=staging, facts={"talleyrand": talleyrand_facts(dl)})


def cap_battles():
    """IQ-5 — casualty scope, trust_note, the diorama's faith caption."""
    iq5 = test_module("test_iq5_both_sides_of_the_butchers_bill")

    # The defender case (the enemy phase): Moore attacks Ney at Paris, Davout
    # reinforces from Berry at trust 10 — D-ADJ, seed 3, the row's own board.
    with _quiet():
        world, res, _logs, losses = iq5._battle(iq5.D_ADJ, "Moore", "Ney", seed=3,
                                                trusts={"Davout": 10})
    adopt(world)
    phase = {"total_actions": 1,
             "nations": {"Britain": {"actions": [res], "action_count": 1}}}
    with _quiet():
        visible = M._build_visible_enemy_phase(phase, world)
    action = (((visible or {}).get("nations") or {}).get("Britain") or {}).get("actions", [{}])[0]
    report = action.get("battle_report") or {}
    cs = report.get("casualty_summary") or {}
    defender = ((action.get("events") or [{}])[0] or {}).get("defender") or {}
    staging = ("tests/test_iq5_both_sides_of_the_butchers_bill.py `_battle(D_ADJ, 'Moore', "
               "'Ney', seed=3, trusts={'Davout': 10})`: Ney 20,000 at Paris, Davout 30,000 at "
               "Berry, Moore 60,000 at Artois, every other corps parked; the result wrapped as "
               "a one-action enemy phase and passed through the production "
               "`main._build_visible_enemy_phase`")
    record("enemy_phase_iq5_dadj", {"enemy_phase": visible, "turn": int(world.current_turn)},
           source="backend.main._build_visible_enemy_phase", staging=staging,
           facts={"defender_casualties": cs.get("defender_casualties"),
                  "defender_casualties_scope": cs.get("defender_casualties_scope"),
                  "attacker_casualties": cs.get("attacker_casualties"),
                  "attacker_casualties_scope": cs.get("attacker_casualties_scope"),
                  "defender_side_scope": defender.get("casualties_scope"),
                  "lead_remaining": defender.get("lead_remaining"),
                  "trust_note": report.get("trust_note"),
                  "reinforcement_messages": action.get("reinforcement_messages")
                  or report.get("reinforcement_messages"),
                  "losses": losses})
    diorama = action.get("battle_diorama") or res.get("battle_diorama")
    if isinstance(diorama, dict):
        faith = [{"name": ct.get("name"), "faith": ct.get("faith")}
                 for side in ("attacker", "defender", "near", "far")
                 for ct in ((diorama.get(side) or {}).get("contingents") or [])
                 if isinstance(ct, dict) and ct.get("faith")]
        faith += [{"name": ct.get("name"), "faith": ct.get("faith")}
                  for ct in (diorama.get("contingents") or [])
                  if isinstance(ct, dict) and ct.get("faith")]
        record("diorama_iq5_dadj", diorama, source="the battle result's `battle_diorama`",
               staging=staging, facts={"register": diorama.get("register"), "faith": faith})

    # The attacker case (the terminal's Berthier report): Ney attacks Mack, Davout
    # marches in at trust 0.
    with _quiet():
        world, res2, _logs2, losses2 = iq5._battle(iq5.A_ADJ, "Ney", "Mack", seed=3,
                                                   trusts={"Davout": 0})
    adopt(world)
    clean = {k: v for k, v in res2.items() if k != "new_state"}
    report2 = res2.get("battle_report") or {}
    staging2 = ("`_battle(A_ADJ, 'Ney', 'Mack', seed=3, trusts={'Davout': 0})`: Ney 30,000 at "
                "Franconia attacks Mack 40,000 at Swabia, Davout 25,000 at Rhineland, trust 0")
    record("battle_result_iq5_aadj", clean, source="CommandExecutor.execute (the executor "
           "result, `new_state` dropped)", staging=staging2,
           facts={"casualty_summary": report2.get("casualty_summary"),
                  "trust_note": report2.get("trust_note"),
                  "reinforcement_messages": res2.get("reinforcement_messages")
                  or report2.get("reinforcement_messages"), "losses": losses2})
    diorama2 = res2.get("battle_diorama")
    if isinstance(diorama2, dict):
        record("diorama_iq5_aadj", diorama2, source="the battle result's `battle_diorama`",
               staging=staging2, facts={"register": diorama2.get("register")})


def cap_petition():
    """IQ-7 — the client's petition popup, the vassal card, the remitted row."""
    iq7 = test_module("test_iq7_satellites_have_a_position")
    from backend.game_logic import vassal as V

    def deliver(dp):
        with _quiet():
            world = iq7._europe()
        c = adopt(world)
        clear_dialogues(world)
        iq7._make_eligible(world, "Switzerland", turn=6)
        world.diplomatic_points = dp
        with _quiet():
            dlg = iq7._deliver(world, "Switzerland")
        response = cmd(c, "status")
        return world, c, dlg, response

    world, c, dlg, response = deliver(5)
    popup = response.get("incoming_proposal")
    staging = ("tests/test_iq7_satellites_have_a_position.py: `_europe()`, dialogue slot "
               "emptied, `_make_eligible(Switzerland, turn=6)` (turn + created_turn written), "
               "`_deliver` = the production `deliver_ai_proposal` with the production "
               "`petition_terms`; the popup read off the next response's `incoming_proposal`")
    record("petition_popup", popup, source="POST /command 'status' → incoming_proposal",
           staging=staging + "; DP 5",
           facts={"is_petition": (popup or {}).get("is_petition"),
                  "from_nation": (popup or {}).get("from_nation"),
                  "clauses": (popup or {}).get("clauses"),
                  "grant_enabled": (popup or {}).get("grant_enabled"),
                  "options": [(o.get("label"), o.get("enabled"), o.get("reason"))
                              for o in ((popup or {}).get("options") or [])
                              if isinstance(o, dict)]})
    record("mailbox_petition", get(c, "/mailbox"), source="GET /mailbox",
           staging=staging + " — the letter as the mailbox panel lists it")

    # Granted: the card's 'Tribute remitted' / bond rows.
    granted = post(c, "/respond_to_diplomatic_dialogue",
                   {"choice": "accept", "dialogue_id": (dlg or {}).get("dialogue_id")})
    dl = get(c, "/diplomatic_ledger")
    rows = ((dl.get("ledger") or {}).get("vassals") or {}).get("rows") or []
    record("diplo_ledger_petition_granted", dl, source="GET /diplomatic_ledger",
           staging=staging + "; then the petition GRANTED through POST "
                             "/respond_to_diplomatic_dialogue {choice: accept}",
           facts={"grant_message": str(granted.get("message"))[:240],
                  "vassal_rows": [{k: v.get(k) for k in
                                   ("name", "display", "loyalty", "standing", "next_petition_in",
                                    "bond", "remission_left", "relation", "relation_modifier")}
                                  for v in rows if isinstance(v, dict)]})
    record("proposal_result_petition_granted", granted.get("proposal_result"),
           source="the grant response's `proposal_result` (the notice-rail payload)",
           staging=staging)

    # Honest availability: a lord with no DP cannot grant.
    world, c, dlg, response = deliver(0)
    popup0 = response.get("incoming_proposal")
    record("petition_popup_no_dp", popup0, source="POST /command 'status' → incoming_proposal",
           staging=staging + "; DP WRITTEN to 0 (state write) — Grant must arrive disabled "
                             "with its reason",
           facts={"grant_enabled": (popup0 or {}).get("grant_enabled"),
                  "grant_reason": (popup0 or {}).get("grant_reason"),
                  "options": [(o.get("label"), o.get("enabled"), o.get("reason"))
                              for o in ((popup0 or {}).get("options") or [])
                              if isinstance(o, dict)]})
    _ = V


def cap_prisoner():
    """S19 — the Generals card of a captured marshal (a camelCase captor: R7)."""
    world, c = fresh()
    with _quiet():
        world.capture_marshal(world.marshals["Ney"], "KingdomOfItaly")
    overview = get(c, "/marshal_overview")
    card = next((m for m in (overview.get("marshals") or []) if m.get("name") == "Ney"), {})
    record("marshal_overview_prisoner", overview, source="GET /marshal_overview",
           staging="1805 boot; `world.capture_marshal(Ney, 'KingdomOfItaly')` (the production "
                   "capture seam, called directly — a camelCase captor on purpose)",
           facts={"captured": card.get("captured"), "status_note": card.get("status_note")})


def cap_regions():
    """S16 + H1 — the Substitutes row: Paris (own soil) and Amsterdam (a vassal's)."""
    world, c = fresh()
    soult = world.marshals["Soult"]
    bern = world.marshals["Bernadotte"]
    holland_capital = "Amsterdam" if "Amsterdam" in world.regions else next(
        n for n, r in world.regions.items() if r.controller == "Holland")
    soult.location = "Paris"
    bern.location = holland_capital
    # The substitute market buys back LOSSES: give both corps something to buy back.
    soult.strength = max(1000, int(soult.strength) - 8000)
    bern.strength = max(1000, int(bern.strength) - 8000)
    world.nation_gold[PLAYER] = 12000
    with _quiet():
        world.calculate_visibility()
        world.invalidate_active_nations_cache()
    test = get(c, "/test")
    gs = test.get("game_state") or {}
    md = gs.get("map_data") or {}
    levy = gs.get("levy") or {}
    from backend.commands.economy_executor import region_feeds_nation
    record("game_state_regions", gs, source="GET /test → game_state (map_data + levy + "
           "naval_overlay — what main.gd hands the map node)",
           staging=f"1805 boot; Soult MOVED to Paris and Bernadotte to {holland_capital} by a "
                   "location write, each corps cut by 8,000 (state writes — the market buys "
                   "back only losses), treasury written to 12,000; visibility recomputed",
           facts={"holland_region": holland_capital,
                  "paris": {k: (md.get("Paris") or {}).get(k) for k in
                            ("controller", "substitute_price_here", "recruit_price_here",
                             "visibility_status")},
                  "holland": {k: (md.get(holland_capital) or {}).get(k) for k in
                              ("controller", "substitute_price_here", "recruit_price_here",
                               "visibility_status")},
                  "holland_feeds_france": bool(region_feeds_nation(
                      world, PLAYER, world.regions[holland_capital])),
                  "substitutes": levy.get("substitutes")})


def _load_fixture(name: str):
    world, c = fresh()
    src = FIXTURES / name
    target = Path(os.environ["INK_IRON_SAVE_DIR"]) / name
    shutil.copy2(src, target)
    loaded = post(c, "/load", {"filename": name})
    if not loaded.get("success"):
        raise RuntimeError(f"/load refused {name}: {loaded.get('message')}")
    M.parser = PARSER
    seed_rng(int(live_world().current_turn))
    return live_world(), c, loaded


def cap_fixtures():
    """The committed t10 / t20 ambient saves: a PLAYED board's ledgers, its
    Gazette, its dispatch, and a real enemy phase (S20)."""
    for name, tag in (("fixture_t10_ambient.json", "t10"), ("fixture_t20_ambient.json", "t20")):
        world, c, _loaded = _load_fixture(name)
        staging = f"tests/fixtures/playtest_saves/{name} copied into the sandbox and POST /load"
        ledger = get(c, "/ledger")
        record(f"ledger_{tag}", ledger, source="GET /ledger", staging=staging,
               facts=econ_facts(ledger))
        dl = get(c, "/diplomatic_ledger")
        boe = (dl.get("ledger") or {}).get("balance_of_europe") or {}
        record(f"diplo_ledger_{tag}", dl, source="GET /diplomatic_ledger", staging=staging,
               facts={"talleyrand": talleyrand_facts(dl),
                      "headline_case": boe.get("headline_case"),
                      "threat_level": boe.get("threat_level"),
                      "threat_projection": boe.get("threat_projection")})
        gazette = get(c, "/gazette")
        record(f"gazette_{tag}", gazette, source="GET /gazette", staging=staging,
               facts={"issues": len(gazette.get("issues") or [])})
        record(f"marshal_overview_{tag}", get(c, "/marshal_overview"),
               source="GET /marshal_overview", staging=staging)
        test = get(c, "/test")
        wars = test.get("active_wars") or {}
        record(f"active_wars_{tag}", wars, source="GET /test → active_wars", staging=staging,
               facts={"war_count": len(wars.get("wars") or [])})
        if wars.get("wars"):
            record(f"war_detail_{tag}", {"war": wars["wars"][0], "coalition": wars.get("coalition")},
                   source="GET /test → active_wars.wars[0]", staging=staging,
                   facts={"opponent": wars["wars"][0].get("opponent"),
                          "war_score": wars["wars"][0].get("war_score")})
        record(f"dispatch_{tag}_loaded", get(c, "/dispatch"), source="GET /dispatch",
               staging=staging + " (the save's own last morning dispatch)")
        response = end_turn(c)
        world = live_world()
        phase = response.get("enemy_phase")
        taken = []
        for nation, block in ((phase or {}).get("nations") or {}).items():
            for act in (block or {}).get("actions", []):
                for ev in act.get("events") or []:
                    if isinstance(ev, dict) and ev.get("captured_from") == PLAYER:
                        taken.append({"by": nation, "type": ev.get("type"),
                                      "region": ev.get("region") or ev.get("to")})
        staging2 = staging + ", then ONE real `end turn` through POST /command"
        record(f"enemy_phase_{tag}", {"enemy_phase": phase, "turn": int(world.current_turn) - 1},
               source="POST /command 'end turn' → enemy_phase", staging=staging2,
               facts={"total_actions": (phase or {}).get("total_actions"),
                      "nations": list(((phase or {}).get("nations") or {}).keys()),
                      "provinces_taken_from_france": taken})
        record(f"end_turn_{tag}", {k: v for k, v in response.items() if k != "game_state"},
               source="POST /command 'end turn' (whole response, game_state dropped)",
               staging=staging2,
               facts={"event_types": [e.get("type") for e in (response.get("events") or [])
                                      if isinstance(e, dict)][:16]})
        record(f"dispatch_{tag}_after", get(c, "/dispatch"), source="GET /dispatch",
               staging=staging2)
        ledger2 = get(c, "/ledger")
        record(f"ledger_{tag}_after", ledger2, source="GET /ledger", staging=staging2,
               facts=econ_facts(ledger2))
        notes = get(c, "/notifications")
        record(f"notifications_{tag}_after", notes.get("notifications") or [],
               source="GET /notifications", staging=staging2,
               facts={"types": sorted({n.get("type") for n in (notes.get("notifications") or [])})})


def cap_user_saves():
    """§1d — the staged NP saves (and the flagship t12), READ from the repo's
    `saves/` by copy; nothing is written back."""
    saves = REPO / "saves"
    for name, tag in (("np_visual_captive.json", "np_captive"),
                      ("np_visual_seat.json", "np_seat"),
                      ("np_visual_field.json", "np_field"),
                      ("flagship_visual_t12.json", "flagship_t12")):
        src = saves / name
        if not src.exists():
            _MANIFEST.append({"name": tag, "skipped": f"{src} is not on this machine"})
            continue
        world, c = fresh()
        shutil.copy2(src, Path(os.environ["INK_IRON_SAVE_DIR"]) / name)
        loaded = post(c, "/load", {"filename": name})
        if not loaded.get("success"):
            _MANIFEST.append({"name": tag, "skipped": f"/load refused: {loaded.get('message')}"})
            continue
        M.parser = PARSER
        staging = f"saves/{name} (staged Aug 16, 2026) COPIED into the sandbox and POST /load"
        overview = get(c, "/marshal_overview")
        nap = next((m for m in (overview.get("marshals") or [])
                    if m.get("name") == "Napoleon"), {})
        record(f"marshal_overview_{tag}", overview, source="GET /marshal_overview",
               staging=staging,
               facts={"napoleon": {k: nap.get(k) for k in
                                   ("location", "captured", "status_note", "personality",
                                    "personality_display", "strength")}})
        test = get(c, "/test")
        record(f"test_{tag}", test, source="GET /test", staging=staging,
               facts={"turn": test.get("turn"),
                      "calendar_label": (test.get("action_summary") or {}).get("calendar_label")})
        record(f"ledger_{tag}", get(c, "/ledger"), source="GET /ledger", staging=staging)
        if tag == "flagship_t12":
            record(f"gazette_{tag}", get(c, "/gazette"), source="GET /gazette", staging=staging)
            dl = get(c, "/diplomatic_ledger")
            record(f"diplo_ledger_{tag}", dl, source="GET /diplomatic_ledger", staging=staging)
            wars = test.get("active_wars") or {}
            if wars.get("wars"):
                record(f"war_detail_{tag}",
                       {"war": wars["wars"][0], "coalition": wars.get("coalition")},
                       source="GET /test → active_wars.wars[0]", staging=staging,
                       facts={"opponent": wars["wars"][0].get("opponent")})


def cap_layout_f3():
    """Row EP F3 "The client layout pass" — the four frames the live review's
    layout rows owe (LV-5 the petition's closed arm, LV-14(b) the settlement
    table's third court, LV-15/LV-20 the wizard's chips and first step, LV-16
    the log's glyphs), each off a REAL payload on a STAGED 1805 board."""
    from backend.game_logic import jealousy as J

    # LV-5: Murat's confrontation with Ney, Murat sent to Brittany (no enemy
    # within his reach), so the command arm arrives CLOSED with the backend's
    # own reason (the live review's frame).
    world, c = fresh()
    clear_dialogues(world)
    world.marshals["Murat"].location = "Brittany"     # no enemy within his reach
    world.marshals["Murat"].strategic_order = None
    with _quiet():
        status = J.queue_confrontation_petition(
            world, world.marshals["Murat"], world.marshals["Ney"], level=0)
    response = cmd(c, "status")
    petition = response.get("marshal_petition")
    record("petition_command_closed", petition,
           source="POST /command 'status' → marshal_petition (the PopupQueue's delivery)",
           staging="fresh 1805 boot; dialogue slot emptied; Murat WRITTEN to Brittany (no enemy "
                   "in reach); `jealousy.queue_confrontation_petition(Murat, Ney, level 0)` — "
                   f"the command arm is closed (push status {status})",
           facts={"kind": (petition or {}).get("kind"),
                  "options": [(o.get("label"), o.get("enabled"), o.get("unavailable_reason"))
                              for o in ((petition or {}).get("options") or [])
                              if isinstance(o, dict)]})

    # LV-15 / LV-20: the wizard's nation list (step 1) and two previews —
    # Austria at war (the Sponsor chip hidden, the buy-off chip's long gate
    # reason) and Prussia at peace (all three instrument chips, the long
    # "Sponsor Their Design" label that ran off the panel).
    world, c = fresh()
    nations = get(c, "/diplomatic_preview")
    record("wizard_nations", nations, source="GET /diplomatic_preview (nation list mode)",
           staging="fresh 1805 boot",
           facts={"nation_count": sum(len(v) for v in (nations.get("categories") or {}).values())
                  if isinstance(nations.get("categories"), dict) else None})
    for court in ("Austria", "Prussia"):
        preview = get(c, f"/diplomatic_preview?nation={court}")
        record(f"wizard_preview_{court.lower()}", preview,
               source=f"GET /diplomatic_preview?nation={court}",
               staging="fresh 1805 boot",
               facts={"at_war": preview.get("current_state"),
                      "chips": [(a.get("display_name"), a.get("available"),
                                 (a.get("disabled_reason_display") or a.get("disabled_reason")))
                                for a in (preview.get("actions") or []) if isinstance(a, dict)]})

    # LV-14(b): the settlement table with THREE covered courts — Vienna held
    # (state write), the whole-war peace drafted against Austria's coalition.
    world, c = fresh()
    clear_dialogues(world)
    vienna = world.regions.get("Vienna")
    if vienna is not None:
        vienna.controller = PLAYER
        world.invalidate_active_nations_cache()
    world.diplomatic_points = max(int(world.diplomatic_points), 5)
    # F5 (row EP, LV-14(a)): Austria beaten in the field — the pair war
    # score France reads is +58 (the stored figure is the alphabetically
    # first court's view) — so the blocker's sentence names London and
    # Vilna as unbeaten and Vienna as the court to press alone.
    _key = world._make_diplo_key(PLAYER, "Austria")
    world.war_scores[_key] = 58 if _key.split("|")[0] == PLAYER else -58
    drafted = cmd(c, "propose common peace with Austria")
    dialogue = drafted.get("diplomatic_dialogue")
    per_court = (dialogue or {}).get("per_court_acceptance") or []
    record("settlement_three_courts", dialogue,
           source="POST /command 'propose common peace with Austria' → diplomatic_dialogue",
           staging="fresh 1805 boot; Vienna's controller WRITTEN to France; DP raised to 5; "
                   "France's war score against Austria WRITTEN to +58 (F5); "
                   "the typed whole-war settlement draft (settlement_confirm, PROPOSE)",
           facts={"dialogue_type": (dialogue or {}).get("type"),
                  "dialogue_mode": (dialogue or {}).get("dialogue_mode"),
                  "courts": [r.get("nation") for r in per_court if isinstance(r, dict)],
                  "dial_actions": {r.get("nation"): len(r.get("dial_actions") or [])
                                   for r in per_court if isinstance(r, dict)},
                  "separate_peace_chips": {
                      r.get("nation"): [a.get("label") for a in (r.get("dial_actions") or [])
                                        if isinstance(a, dict) and a.get("action") == "seek_bilateral_peace"]
                      for r in per_court if isinstance(r, dict)},
                  "legitimacy": [ln for ln in str((dialogue or {}).get("talleyrand_text") or "").splitlines()
                                 if "unbeaten" in ln or "Press " in ln][:2],
                  "message": str(drafted.get("message"))[:200]})

    # LV-16: a log with rows of several categories — Ulm fought, two turns
    # ended (the enemy phase and the envoys fill the rest).
    world, c = fresh()
    world.marshals["Mack"].strength = 600
    cmd(c, "Ney, attack Mack")
    cmd(c, "end turn")
    cmd(c, "end turn")
    log = get(c, "/campaign_log")
    cats = {}
    for turn in (log.get("turns") or []):
        for ev in (turn.get("events") or []):
            cats[ev.get("category")] = cats.get(ev.get("category"), 0) + 1
    record("campaign_log_glyphs", log, source="GET /campaign_log",
           staging="fresh 1805 boot; Mack cut to 600 (state write); `Ney, attack Mack`; two end turns",
           facts={"categories": cats})


def cap_campaign_end():
    """Row EP GE-2 — the end screen's four registers (the three GE-1 causes of
    the Fall, the Humbled Peace, the Verdict, and GE-3's Imperial Peace
    STAGED through the real `record_ending`) and the clock line's two client
    surfaces. The boards are the row's own test stagings
    (`tests/test_ge2_the_client.py`), so a frame is of the state the pins are
    about; every payload is what the endpoint or `game_end.screen_payload`
    returned, unedited."""
    from backend.game_logic import game_end
    T = test_module("test_ge2_the_client")

    def _facts(payload):
        summary = payload.get("summary") or {}
        return {"register": payload.get("register"), "title": payload.get("title"),
                "cause_line": payload.get("cause_line"),
                "calendar_label": payload.get("calendar_label"), "turn": payload.get("turn"),
                "terminal": payload.get("terminal"),
                "tier_title": payload.get("tier_title"),
                "epilogue_variant": (summary.get("epilogue") or {}).get("variant"),
                "epilogue_first_sentence": ((summary.get("epilogue") or {}).get("paragraphs")
                                            or [""])[0][:120],
                "battles_fought": (summary.get("totals") or {}).get("battles_fought"),
                "provinces_held": summary.get("provinces_held")}

    world, c = fresh()
    r = T.stage_funeral(c, world)
    record("campaign_end_fall_funeral", r["ending"], source="POST /command → ending",
           staging="1805 boot; Napoleon alone at Lorraine (60 men), the other French corps "
                   "moved to Brittany; `Napoleon, attack Mack` at SOVEREIGN_DEATH_CHANCE_PCT "
                   "= 100 — the death INSIDE the player's own command (no dispatch, no "
                   "Moniteur special: the end screen is its only surface)",
           facts=_facts(r["ending"]))

    world, c = fresh()
    payload = T.stage_chains_payload(world)
    record("campaign_end_fall_chains", payload, source="game_end.screen_payload(terminal_ending)",
           staging="1805 boot; the Emperor taken by Austria on turn 1 through the real "
                   "capture seam, then ten ticks of the ONE per-turn caller "
                   "(game_end.process_end_of_turn) at war with the captor — the chains Fall",
           facts=_facts(payload))

    world, c = fresh()
    responses = T.stage_soil_fall(c, world)
    fallen = responses[-1]
    record("campaign_end_fall_abdication", fallen["ending"], source="POST /command end turn → ending",
           staging="1805 boot; every French province but Brittany handed to Austria (a direct "
                   "controller write), then five REAL end turns — the soil clock's Fall",
           facts=_facts(fallen["ending"]))
    # The R screen re-reads the LAST dispatch, and a fallen campaign's last
    # dispatch carries no clock (the war is over), so the clock frame is shot
    # one end turn into the same staging — the briefing of turn 2, the clock
    # at 1 of 5.
    world, c = fresh()
    T.stage_soil_fall_one_turn(c, world)
    dispatch = get(c, "/dispatch")
    body = dispatch.get("dispatch") or {}
    record("dispatch_fall_clock", dispatch, source="GET /dispatch",
           staging="1805 boot; every French province but Brittany handed to Austria (a direct "
                   "controller write), ONE real end turn — the turn-2 briefing the R screen "
                   "re-reads, its fall clock at 1 of 5 in `defeat_imminent_warning.fall.arms`",
           facts={"clock_lines": [a.get("clock_line") for a in
                                  ((body.get("defeat_imminent_warning") or {}).get("fall") or {})
                                  .get("arms", [])]})

    world, c = fresh()
    T.stage_humbled(c, world)
    ce = get(c, "/campaign_end")
    humbled = next(e for e in ce["endings"] if e["cause"] == game_end.CAUSE_HUMBLED)
    record("campaign_end_humbled", humbled, source="GET /campaign_end → endings[humbled_peace]",
           staging="1805 boot; a peace ceding Paris ratified through the real `_ratify_treaty` "
                   "— the Humbled Peace stamped at the ratify seam, read back off the record",
           facts=_facts(humbled))

    world, c = fresh()
    r = T.stage_verdict(c, world)
    record("campaign_end_verdict", r["ending"], source="POST /command end turn → ending",
           staging="1805 boot with current_turn set to the authored verdict turn (44), one "
                   "REAL end turn — the Verdict of History on the end-turn road",
           facts=_facts(r["ending"]))

    world, c = fresh()
    rec = game_end.record_ending(world, "victory", game_end.CAUSE_IMPERIAL_PEACE)
    payload = game_end.screen_payload(rec)
    record("campaign_end_imperial", payload, source="game_end.screen_payload(record_ending)",
           staging="1805 boot; GE-3's register STAGED through the real `record_ending` (no "
                   "Congress exists yet) — a preview of the fourth register the scene takes; "
                   "GE-3 will add its own blocks to the summary",
           facts=_facts(payload))

    world, c = fresh()
    ledger = T.stage_ledger_clock(c, world)
    clock = (ledger.get("ledger") or {}).get("fall_clock") or {}
    record("ledger_fall_clock", ledger, source="GET /ledger",
           staging="1805 boot; France reduced to Brittany (the soil clock ticking against "
                   "Britain and Russia) AND the Emperor taken by Austria under a truce (the "
                   "chains clock paused), one tick — two arms, two tints, one dated",
           facts={"clock_lines": [a.get("clock_line") for a in clock.get("arms", [])],
                  "severities": [a.get("severity") for a in clock.get("arms", [])]})


CAPTURES = {
    "campaign_end": cap_campaign_end,
    "layout_f3": cap_layout_f3,
    "boot": cap_boot,
    "spent": cap_spent,
    "ceiling": cap_ceiling_states,
    "collapse": cap_collapse,
    "peace": cap_peace_popups,
    "missions": cap_missions,
    "battles": cap_battles,
    "petition": cap_petition,
    "prisoner": cap_prisoner,
    "regions": cap_regions,
    "fixtures": cap_fixtures,
    "user_saves": cap_user_saves,
}


def main(argv=None) -> int:
    global _OUT
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--only", nargs="*", default=[], help="capture groups: "
                    + ", ".join(CAPTURES))
    args = ap.parse_args(argv)
    _OUT = Path(args.out)
    _OUT.mkdir(parents=True, exist_ok=True)
    boot_backend(_OUT)
    failures = []
    groups = args.only or list(CAPTURES)
    for group in groups:
        fn = CAPTURES.get(group)
        if fn is None:
            print(f"unknown capture group: {group}")
            return 2
        print(f"[{group}]")
        try:
            fn()
        except Exception as exc:          # one board must not take the rest with it
            failures.append({"group": group, "error": repr(exc),
                             "trace": traceback.format_exc()})
            print(f"  FAILED {group}: {exc!r}")
    manifest_path = _OUT / "manifest.json"
    previous = []
    if args.only and manifest_path.exists():
        try:
            old = json.loads(manifest_path.read_text(encoding="utf-8"))
            fresh_names = {row.get("name") for row in _MANIFEST}
            previous = [row for row in old.get("captures", [])
                        if row.get("name") not in fresh_names]
        except (OSError, ValueError):
            previous = []
    manifest_path.write_text(json.dumps(
        {"repo": str(REPO).replace("\\", "/"), "parser": "mock", "groups": groups,
         "captures": previous + _MANIFEST, "failures": failures},
        indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"manifest: {manifest_path}  ({len(_MANIFEST)} captured, {len(failures)} failed)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
