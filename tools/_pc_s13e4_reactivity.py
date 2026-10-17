"""F's reactivity re-read — S13e part 4 (October 17, 2026; the peace report
`docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §46 F, recorded as §47).

Part II §11 pulled one lever at a time on the user's turn-6 save and read
Austria's answer to Talleyrand's own peace through the STORED score — so
every battlefield lever read 0 by construction (§36 row 14), and §40 F /
§44 concluded "six of ten levers move nothing". Rulings E, G, H and I each
added a lever since. This re-run pulls each lever on a COPY of the board,
RECOMPUTES the stored scores (`recalculate_war_scores`, the advance's own
write) and reads every court's answer through four readers the game itself
uses:

    bilateral   `calculate_acceptance` of the white peace and of Talleyrand's
                own draft (the send road's scorer);
    table       `build_settlement_preview` of the whole-war white peace — each
                court's total against 50 (the table's scorer);
    court       `court_own_readiness` — the court's own score, whether it sues,
                which letter it would send (the AI's own read);
    clock       `war_exhaustion_terms` — the court's rate this advance (H).

A lever MOVES a court's answer when any reader's number or verdict changes
for that court. The ten levers of §11 / §7 and the four the rulings added:

    1 one more victory · 2 three more victories · 3 one decisive victory ·
    4 the capital (taken on the turn-6 copy; returned on the Vienna-held
    board) · 5 relations +20 · 6 war exhaustion +40 · 7 five more turns of
    war · 8 lose a battle · 9 the terms (Talleyrand's draft against a white
    peace) · 10 Talleyrand's mission (Improve Relations: +8 relation, the
    IQ-4 effect) · E a payment to the court paid (300 gold to Austria on the
    table) · G the shield (the capital held stops the defence ticking) ·
    H occupation (one more home province held) · I a refused dictated letter
    (the ratchet).

    .venv/Scripts/python.exe tools/_pc_s13e4_reactivity.py [--board vienna|copy|both]

Writes tools/_pc_s13e4_reactivity.json; `tests/test_pc_rulings.py::
TestTheReactivityRead` reads it. Reported per board, never as a law.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("LLM_MODE", "mock")
BOARDS = ROOT / "tests" / "fixtures" / "pc_boards"
COURTS = ("Austria", "Britain", "Russia")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def load(name: str):
    from backend.models.world_state import WorldState
    with _quiet():
        world = WorldState.from_dict(
            json.loads((BOARDS / name).read_text(encoding="utf-8"))["world_state"])
        while world.dialogue_manager.peek() is not None:
            world.dialogue_manager.pop()
    return world


def clone(world):
    from backend.models.world_state import WorldState
    with _quiet():
        return WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))


def _white(court: str) -> dict:
    return {"type": "peace", "proposer_nation": "France", "target_nation": court,
            "sweeteners": [], "demands": [], "clauses": []}


def read(world, *, terms_by_court=None, table_terms=None) -> dict:
    """Every court's answer, through the game's own readers."""
    from backend.game_logic import ai_diplomacy as AI
    from backend.game_logic import coalition as COM
    from backend.game_logic.diplomacy import (
        armistice_variant_for, calculate_acceptance, recalculate_war_scores,
    )
    from backend.game_logic.diplomatic_templates import generate_suggested_terms
    from backend.game_logic.settlement_staging import build_settlement_preview
    with _quiet():
        recalculate_war_scores(world)
        preview = build_settlement_preview(
            world, war_id="war_1", covered_enemy_participants=list(COURTS),
            settlement_terms=list(table_terms or [{"type": "peace"}]))
    rows = {str(r.get("nation") or ""): r
            for r in ((preview.get("settlement_preview") or {}).get("per_court_acceptance") or [])}
    out = {}
    for court in COURTS:
        with _quiet():
            white = calculate_acceptance(_white(court), world)
            draft = (terms_by_court or {}).get(court) or generate_suggested_terms(
                court, "peace", world, deterministic=True)
            drafted = calculate_acceptance(dict(draft, proposer_nation="France", target_nation=court), world)
            variant = armistice_variant_for(world, "France", court)
            truce = calculate_acceptance(dict(_white(court), type=variant), world)
            own = AI.court_own_readiness(world, court, "France")
            clock = COM.war_exhaustion_terms(world, court)
            letter = AI.next_dictated_letter(world, court, "France") or {}
            tier = AI.dictated_tier(world, court, "France", int(own.get("score", 0)))
        row = rows.get(court) or {}
        out[court] = {
            "white": int(white.get("score", 0)), "white_verdict": str(white.get("verdict") or ""),
            "draft": int(drafted.get("score", 0)), "draft_verdict": str(drafted.get("verdict") or ""),
            "truce": int(truce.get("score", 0)), "truce_verdict": str(truce.get("verdict") or ""),
            "table": int(row.get("total", 0) or 0), "table_verdict": str(row.get("verdict") or ""),
            "own_score": int(own.get("score", 0)), "sues": bool(own.get("sues")),
            "letter": str(own.get("letter") or ""), "break_ranks": str(own.get("break_ranks") or ""),
            "clock": int(clock.get("total", 0)),
            "dictates": int(letter.get("tier", -1)) if letter else -1,
            "dictate_tier": int(tier.get("tier", 0) or 0),
        }
    return out


def _casualties(world, nation: str, men: int) -> None:
    """A battle's losses on the court's largest field corps (the probe's
    stand-in for the combat pipeline's casualty distribution)."""
    corps = sorted((m for m in world.marshals.values()
                    if m.nation == nation and int(getattr(m, "strength", 0) or 0) > 0),
                   key=lambda m: -int(m.strength))
    if corps:
        corps[0].strength = max(0, int(corps[0].strength) - int(men))


def _battle(world, winner: str, loser: str, decisive: bool = False) -> None:
    """One battle of the France–Austria pair, recorded this turn the way the
    pipeline records it, with the loser's casualties applied."""
    key = world._make_diplo_key("France", "Austria")
    lost = 12000 if decisive else 6000
    rec = {"turn": int(world.current_turn), "winner": winner, "attacker": winner, "defender": loser,
           "attacker_casualties": 3000, "defender_casualties": lost,
           "location": "Moravia", "battle_name": "a battle of the probe"}
    world.battle_records.setdefault(key, []).append(rec)
    if decisive:
        world.decisive_battles.setdefault(key, []).append(
            {"turn": int(world.current_turn), "winner": winner, "total_casualties": lost + 3000, "ratio": 4.0})
    bt = getattr(world, "battles_this_turn", None)
    if isinstance(bt, list):
        bt.append(dict(rec))
    _casualties(world, loser, lost)
    _casualties(world, winner, 3000)


def levers(world, board: str) -> dict:
    """{lever: callable(world) -> note} — each applied to a fresh clone."""
    key = world._make_diplo_key("France", "Austria")
    capital_held = world.regions["Vienna"].controller == "France"

    def one_victory(w):
        _battle(w, "France", "Austria")
        return "France beats Austria once more"

    def three_victories(w):
        for _ in range(3):
            _battle(w, "France", "Austria")
        return "three more French victories"

    def decisive(w):
        _battle(w, "France", "Austria", decisive=True)
        return "one decisive victory"

    def capital(w):
        if capital_held:
            w.regions["Vienna"].controller = "Austria"
            w.invalidate_active_nations_cache()
            return "Vienna returned to Austria (held on this board)"
        w.regions["Vienna"].controller = "France"
        w.invalidate_active_nations_cache()
        return "Vienna taken"

    def relations(w):
        for court in COURTS:
            k = w._make_diplo_key("France", court)
            w.nation_relations[k] = int(w.nation_relations.get(k, 0)) + 20
        return "relations +20 with each court"

    def exhaustion(w):
        for court in COURTS:
            w.war_exhaustion[court] = int(w.war_exhaustion.get(court, 0)) + 40
        return "each court's war exhaustion +40"

    def five_turns(w):
        w.current_turn = int(w.current_turn) + 5
        return "five more turns of war"

    def lose(w):
        _battle(w, "Austria", "France")
        return "France loses a battle"

    def mission(w):
        from backend.game_logic.diplomatic_dialogue import mission_effect_magnitude
        gain = int(mission_effect_magnitude(w, "IMPROVE_RELATIONS", "relation_change") or 8)
        for court in COURTS:
            k = w._make_diplo_key("France", court)
            w.nation_relations[k] = int(w.nation_relations.get(k, 0)) + gain
        return f"one turn of Improve Relations with each court (+{gain}, IQ-4's mission effect)"

    def shield(w):
        # G: the shield — the defence ticking stops while the capital is held;
        # read as the capital lever's twin on the ticking component only.
        obj = (w.war_objectives.get(key) or {}).get("Austria")
        if isinstance(obj, dict):
            obj["accumulated_ticking"] = int(obj.get("accumulated_ticking", 0)) + 3
        return "Austria's defence claim +3 (the shield decides whether it counts)"

    def occupation(w):
        w.regions["Moravia"].controller = "France"
        w.invalidate_active_nations_cache()
        return "one more home province held (Moravia)"

    def refused_letter(w):
        from backend.game_logic.ai_diplomacy import note_dictated_refusal, record_dictated_offer
        for court in COURTS:
            record_dictated_offer(w, court, "France", channel="bilateral", tier=0,
                                  summary="the probe's letter", ask_gold=1000)
            note_dictated_refusal(w, court, "France", channel="bilateral")
        return "each court's dictated letter refused (the ratchet)"

    return {
        "1 one more victory": one_victory, "2 three more victories": three_victories,
        "3 one decisive victory": decisive, "4 the capital": capital,
        "5 relations +20": relations, "6 war exhaustion +40": exhaustion,
        "7 five more turns of war": five_turns, "8 lose a battle": lose,
        "10 Talleyrand's mission": mission,
        "G the shield": shield, "H occupation": occupation, "I a refused letter": refused_letter,
    }


def diff(before: dict, after: dict) -> dict:
    moved = {}
    for court in COURTS:
        b, a = before[court], after[court]
        changed = {k: (b[k], a[k]) for k in b if b[k] != a[k]}
        if changed:
            moved[court] = changed
    return moved


def truce_read(world) -> dict:
    """Ruling D's footing: each court's truce with France and where it heads
    (`armistice_expiry_exit` — the court's answer at the truce's end)."""
    from backend.game_logic.diplomacy import armistice_expiry_exit
    out = {}
    for court in COURTS:
        ex = armistice_expiry_exit(world, "France", court)
        out[court] = {"exit": str(ex.get("exit") or ""), "projected": int(ex.get("projected", 0))}
    return out


def sign_truces(world) -> None:
    from backend.game_logic.diplomacy import armistice_variant_for
    for court in COURTS:
        if world.get_diplomatic_state("France", court) != "WAR":
            continue
        with _quiet():
            world._ratify_treaty({"type": armistice_variant_for(world, "France", court),
                                  "proposer_nation": "France", "target_nation": court,
                                  "sweeteners": [], "demands": [], "clauses": []})


def quiet_turns_until_a_victory_counts(world) -> int:
    """Ruling G: the smallest number of quiet turns after which the France–
    Austria battle component has decayed under its cap — the turn one more
    victory (which resets the quiet clock) counts again."""
    from backend.game_logic.diplomacy import BATTLE_SCORE_CAP, battle_score_from_records
    key = world._make_diplo_key("France", "Austria")
    records = list((world.battle_records or {}).get(key) or [])
    turn = int(world.current_turn)
    for k in range(0, 40):
        if abs(battle_score_from_records(records, "France", "Austria", turn + k)) < int(BATTLE_SCORE_CAP):
            return k
    return -1


def run_board(name: str, label: str) -> dict:
    world = load(name)
    base = read(world)
    out = {"board": label, "baseline": base, "levers": {}, "footings": {}}
    for lever, fn in levers(world, label).items():
        w = clone(world)
        note = fn(w)
        after = read(w)
        out["levers"][lever] = {"note": note, "moved": diff(base, after), "after": after}
    # 9 the terms: Talleyrand's draft against the white peace (the readers
    # already carry both; the lever is the ask itself)
    terms_moved = {c: {"white_vs_draft": (base[c]["white"], base[c]["draft"])}
                   for c in COURTS if base[c]["white"] != base[c]["draft"]}
    out["levers"]["9 the terms"] = {"note": "Talleyrand's draft against a white peace",
                                    "moved": terms_moved, "after": base}
    # E a payment to the court paid: 300 gold to Austria on the table
    w = clone(world)
    paid = read(w, table_terms=[{"type": "peace"},
                                {"type": "gold_indemnity", "from": "France", "to": "Austria", "amount": 300}])
    out["levers"]["E a payment to the court paid"] = {
        "note": "300 gold to Austria on the whole-war table", "moved": diff(base, paid), "after": paid}
    # G's footing: after the quiet turns the decay needs, one more victory
    # (and three) against the same quiet turns alone
    k = quiet_turns_until_a_victory_counts(world)
    out["footings"]["G"] = {"quiet_turns": k}
    if k >= 0:
        lv = levers(world, label)
        quiet = clone(world)
        quiet.current_turn = int(quiet.current_turn) + k
        qbase = read(quiet)
        for name_ in ("1 one more victory", "2 three more victories"):
            w = clone(quiet)
            lv[name_](w)
            after = read(w)
            out["footings"]["G"][name_] = {"moved": diff(qbase, after), "after": after}
        out["footings"]["G"]["baseline"] = qbase
    # D's footing: each court in a truce with France; relations and the
    # mission read where the truce heads
    truce = clone(world)
    sign_truces(truce)
    tbase = truce_read(truce)
    out["footings"]["D"] = {"baseline": tbase}
    lv = levers(world, label)
    for name_ in ("5 relations +20", "10 Talleyrand's mission"):
        w = clone(truce)
        lv[name_](w)
        after = truce_read(w)
        moved = {c: {k2: (tbase[c][k2], after[c][k2]) for k2 in tbase[c] if tbase[c][k2] != after[c][k2]}
                 for c in COURTS}
        out["footings"]["D"][name_] = {"moved": {c: v for c, v in moved.items() if v}, "after": after}
    out["ten"] = ten_lever_summary(out)
    return out


TEN = ("1 one more victory", "2 three more victories", "3 one decisive victory", "4 the capital",
       "5 relations +20", "6 war exhaustion +40", "7 five more turns of war", "8 lose a battle",
       "9 the terms", "10 Talleyrand's mission")
ANSWERS = {"white", "white_verdict", "draft", "draft_verdict", "truce", "truce_verdict",
           "table", "table_verdict", "own_score", "sues", "letter", "break_ranks",
           "dictates", "dictate_tier", "white_vs_draft", "exit", "projected"}


def ten_lever_summary(board: dict) -> dict:
    """For each of the ten levers: the footing on which it moves a court's
    ANSWER (a score, a verdict, a letter, a truce's exit — never the clock
    alone), and the courts it moves there."""
    out = {}
    for lever in TEN:
        rows = []
        at_war = board["levers"].get(lever, {}).get("moved", {})
        courts = sorted(c for c, v in at_war.items() if set(v) & ANSWERS)
        if courts:
            rows.append({"footing": "war (turn as saved)", "courts": courts})
        g = (board["footings"].get("G") or {}).get(lever)
        if g:
            gc = sorted(c for c, v in g["moved"].items() if set(v) & ANSWERS)
            if gc:
                rows.append({"footing": f"war after {board['footings']['G']['quiet_turns']} quiet turns (G's decay)",
                             "courts": gc})
        d = (board["footings"].get("D") or {}).get(lever)
        if d:
            dc = sorted(d["moved"])
            if dc:
                rows.append({"footing": "a truce (D's exit)", "courts": dc})
        out[lever] = {"moves": bool(rows), "where": rows,
                      "clock_only": bool(at_war) and not courts}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", default="both", choices=["vienna", "copy", "ulm", "both"])
    ap.add_argument("--out", default=str(ROOT / "tools" / "_pc_s13e4_reactivity.json"))
    args = ap.parse_args()
    boards = []
    if args.board in ("vienna", "both"):
        boards.append(("turn6_vienna_held.json", "vienna_held"))
    if args.board in ("copy", "both"):
        boards.append(("turn6_copy.json", "turn6_copy"))
    if args.board in ("ulm", "both"):
        boards.append(("ulm_t18_paris_fallen.json", "ulm_t18"))
    record = {"boards": [run_board(n, l) for n, l in boards]}
    for b in record["boards"]:
        print(f"== {b['board']}")
        for lever, rec in b["levers"].items():
            courts = ", ".join(f"{c}: {sorted(v)}" for c, v in rec["moved"].items()) or "- nothing moves"
            print(f"  {lever:32s} {courts}")
        print(f"  G footing: {b['footings']['G'].get('quiet_turns')} quiet turns")
        for lever, rec in b["ten"].items():
            print(f"  TEN {lever:28s} moves={rec['moves']} {rec['where']}")
    Path(args.out).write_text(json.dumps(record, indent=1, default=str) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
