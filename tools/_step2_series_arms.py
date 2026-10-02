"""Score Finish Step 2 "Berthier tells the truth" — the BASELINE_SERIES
attribution (October 2, 2026). Display and copy, no series moves: every
Step 2 lever is set IN THE CHILD before the 40-turn ambient sim boots (the
slice-9 idiom), and the production seams the step touched that COULD reach
the AI are COUNTED — so "the ambient board never …" is a number.

    python3 tools/_step2_series_arms.py [--arms 0,1]

Arms:
    0  every Step 2 lever down -> must reproduce the recorded series byte-for-byte
    1  the shipped tree (every lever up) -> must ALSO reproduce it (no series moves)

Writes tools/_step2_series_arms.json (committed with the landing record).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"

LEVERS = [
    ("backend.game_logic.intel_surfaces", "THE_SIGHTING_IS_LIVE"),
    ("backend.game_logic.intel_surfaces", "THE_SURFACES_NAME_THE_GARRISON"),
    ("backend.game_logic.intel_surfaces", "THE_ENEMY_WORKS_REGROW_ALOUD"),
    ("backend.game_logic.dispatch", "THE_FALLEN_HOMELAND_STANDS_ON_THE_PAGE"),
    ("backend.game_logic.dispatch", "THE_FALLEN_PROVINCE_NAMES_ITS_CAPTOR"),
    ("backend.game_logic.dispatch", "THE_BRIEFING_SHOWS_THE_GRIP"),
    ("backend.game_logic.dispatch", "THE_AURA_HAS_ITS_BEAT"),
    ("backend.game_logic.dispatch", "THE_LEVY_YIELDS_ONCE_STATED"),
    ("backend.game_logic.dispatch", "THE_CASCADE_IS_GROUPED"),
    ("backend.game_logic.dispatch", "THE_SUMMONABLE_GATE_IS_NEWS"),
    ("backend.game_logic.dispatch", "THE_DEFENDERS_ARE_JOINED_IN_SERIES"),
    ("backend.game_logic.dispatch", "THE_FAMINE_COUNTS_ITS_DEAD"),
    ("backend.game_logic.dispatch", "THE_RANK_IS_THE_COURTS_OWN"),
    ("backend.commands.strategic", "ONE_CLOCK"),
    ("backend.commands.strategic", "A_SUPPORT_ORDER_IS_SINGULAR"),
    ("backend.game_logic.intent", "THE_NARRATION_HAS_A_DEAD_BAND"),
    ("backend.game_logic.intent", "THE_TAIL_NAMES_ITS_COURTS"),
    ("backend.game_logic.settlement_ratify", "THE_RECORD_NAMES_THE_COVERAGE"),
    ("backend.game_logic.settlement_presentation", "THE_COVERAGE_LINE_KEEPS_EVERY_COURT"),
    ("backend.game_logic.settlement_presentation", "THE_WARNING_NAMES_ITS_COMPONENT"),
    ("backend.game_logic.settlement_presentation", "THE_SUMMARY_FILLS_ITS_SLOTS"),
    ("backend.game_logic.settlement_staging", "THE_HINT_PRESSES_ONE_COURT"),
    ("backend.game_logic.diplomatic_templates", "THE_WHITE_PEACE_SPEAKS_ITS_OWN_BLOCKER"),
    ("backend.main", "THE_NET_FALLS_BACK_NEUTRAL"),
    ("backend.game_logic.marshal_overview", "THE_CARD_SHOWS_THE_PRESENCE_TODAY"),
    ("backend.display_names", "THE_HONORIFIC_IS_THE_COURTS_OWN"),
    ("backend.ai.question_desk", "THE_DESK_READS_THE_TABLE"),
    ("backend.ai.question_desk", "THE_DESK_PLACES_A_COURT"),
    ("backend.ai.question_desk", "THE_DESK_READS_THE_ALARM"),
    ("backend.ai.clause_guards", "TELL_ME_IS_A_QUESTION"),
    ("backend.game_logic.congress", "THE_SYSTEM_NAMES_ITS_CONDITION"),
    ("backend.commands.movement_executor", "THE_MARCH_NAMES_THE_FORFEIT"),
    ("backend.commands.movement_executor", "THE_ENGAGED_REFUSAL_NAMES_THE_ENEMY"),
    ("backend.game_logic.combat", "THE_FIELD_SPEAKS_DISPLAY_NAMES"),
    ("backend.commands.strategic_executor", "THE_MARCH_REPORTS_ITS_CAPTURE"),
    ("backend.commands.strategic_executor", "A_REFUSED_TRUST_KEEPS_THE_OBJECTION"),
    ("backend.commands.strategic_executor", "THE_PURSUIT_STATES_ITS_TERMS"),
    ("backend.game_logic.gazette", "THE_MONITEUR_SEES_THE_OPEN_GATE"),
    ("backend.campaign_log", "THE_LOG_HAS_AN_IMPORTANCE_TIER"),
    ("backend.commands.combat_executor", "THE_VOICE_ROTATES_ON_HIS_OWN_RECORD"),
    ("backend.commands.combat_executor", "THE_LITERAL_QUOTES_THE_TYPED_ORDER"),
    ("backend.commands.combat_executor", "THE_MUSTER_NAMES_THE_LEAD"),
    ("backend.commands.combat_executor", "THE_CHARGE_NAMES_ITS_THRESHOLD"),
    ("backend.game_logic.marshal_voice", "THE_NAMED_BANK_FALLS_THROUGH"),
    ("backend.game_logic.enemy_voice", "THE_NAMED_BANK_FALLS_THROUGH"),
    ("backend.commands.disobedience", "THE_ALTERNATIVE_IS_A_FOE_AT_WAR"),
    ("backend.commands.disobedience", "THE_OBJECTION_OFFERS_A_MAN_WE_HAVE_SEEN"),
    ("backend.commands.meta_executor", "THE_PRESSED_ATTACK_PRINTS_ITS_MUSTER"),
    ("backend.commands.diplomatic_executor", "A_DISABLED_OPTION_REFUSES_WITH_ITS_REASON"),
    ("backend.game_logic.settlement_actions", "THE_DIAL_SURVIVES_THE_DROP"),
]

CHILD = r"""
import sys, runpy, atexit, collections, importlib
LEVERS = {levers!r}
UP = {up!r}
for mod_name, name in LEVERS:
    mod = importlib.import_module(mod_name)
    setattr(mod, name, UP)
import backend.commands.disobedience as DS
import backend.commands.combat_executor as CE
import backend.game_logic.combat as CB
import backend.game_logic.settlement_actions as SA
import backend.game_logic.intel_surfaces as IS
import backend.commands.strategic_executor as SE
_c = collections.Counter()
_o1 = DS.get_enemies_in_range
def _range(marshal, game_state):
    _c["range_calls"] += 1
    if getattr(marshal, "nation", None) != getattr(game_state, "player_nation", None):
        _c["range_calls_non_player"] += 1
    return _o1(marshal, game_state)
DS.get_enemies_in_range = _range
_o2 = DS._get_aggressive_preferred
def _pref(marshal, world):
    _c["preferred_calls"] += 1
    if getattr(marshal, "nation", None) != getattr(world, "player_nation", None):
        _c["preferred_calls_non_player"] += 1
    return _o2(marshal, world)
DS._get_aggressive_preferred = _pref
_o3 = CE._voice_rotation_key_for
def _key(world, marshal, region_name, situation=""):
    _c["voice_key_calls"] += 1
    return _o3(world, marshal, region_name, situation)
CE._voice_rotation_key_for = _key
_o4 = CB._field_names
def _names(text, *marshals):
    _c["field_name_calls"] += 1
    return _o4(text, *marshals)
CB._field_names = _names
_o5 = SA._terms_after_cover_edit
def _cover(*a, **k):
    _c["cover_edit_calls"] += 1
    return _o5(*a, **k)
SA._terms_after_cover_edit = _cover
_o6 = IS.live_sightings
def _live(world, viewer):
    _c["live_sighting_calls"] += 1
    return _o6(world, viewer)
IS.live_sightings = _live
_o7 = SE.StrategicExecutor._handle_strategic_objection_from_endpoint
def _resolve(self, choice, game_state):
    _c["objection_resolver_calls"] += 1
    out = _o7(self, choice, game_state)
    if isinstance(out, dict) and out.get("objection_kept"):
        _c["objection_kept"] += 1
    return out
SE.StrategicExecutor._handle_strategic_objection_from_endpoint = _resolve
def _dump():
    print("STEP2=" + repr(dict(_c)))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(up: bool) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    env.pop("PYTHONIOENCODING", None)
    code = CHILD.format(levers=LEVERS, up=up, runner=str(RUNNER))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    counts = [ln for ln in lines if ln.startswith("STEP2=")]
    payload["step2"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
    return payload


def first_divergence(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


def recorded_series() -> list:
    src = RUNNER.read_text(encoding="utf-8")
    start = src.index("BASELINE_SERIES = [")
    end = src.index("]", start)
    return list(ast.literal_eval(src[start + len("BASELINE_SERIES = "):end + 1]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="0,1")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_step2_series_arms.json"))
    args = ap.parse_args()
    prior = recorded_series()
    out = {"recorded": prior, "levers": [f"{m}.{n}" for m, n in LEVERS], "arms": {}}
    for arm in [int(x) for x in args.arms.split(",")]:
        up = arm == 1
        print(f"arm {arm} ({'all up' if up else 'all down'}) ...", flush=True)
        payload = run_arm(up)
        series = payload["series"]
        div = first_divergence(series, prior)
        out["arms"][str(arm)] = {
            "levers_up": up, "series": series,
            "first_divergence_vs_recorded": div,
            "provinces": payload.get("provinces"),
            "step2": payload.get("step2"),
        }
        print(f"  divergence vs recorded: {div}; counts: {payload.get('step2')}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
