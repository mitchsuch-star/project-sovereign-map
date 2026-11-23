"""Row IC, Session 4 — IC-14: THE WAR PLAN (the other side of the hill).

`docs/INDEPENDENT_COMMAND_SPEC.md` §10 (§10.1 the war plan, §10.3 what the
enemy learns of you), §7 (exact orders — the same for every nation), §2 step 3
("the enemy's if-thens"), §12 ("The enemy"); the rules `SYSTEMS_REFERENCE.md`
§235; the seams `tests/_ic4_seams.py`.

THE ENEMY KEEPS ITS HAND. Its bold and careful marshals are moved by their
court's own logic exactly as before. What a court at war WITH FRANCE gains is
a war plan — drawn by the campaign's seed from two or three written ones (the
historical seed draws the first, the historical plan). A plan is drawn against
France, the other side of the hill: a court whose wars are all with other
courts fights them by its own logic, as before (`_muster`):

  * a plan is a short list of STEPS; a step gives EXACT ORDERS — a standing
    order and up to three if-thens, the very if-thens the player's literal men
    take (`backend/commands/if_thens.py`, golden rule 5) — to each of the
    court's marshals who follow orders to the letter, and names ONE PROVINCE
    the court's other corps lean toward (`favoured`);
  * a step ends on its written condition (a number of turns, a line used, a
    place fallen) and the next applies; steps only go forward; when they run
    out the men are the court's ordinary literal men again;
  * while a court's capital is lost its part of the plan is torn up;
  * a court at peace with France has no plan.

A MARSHAL UNDER A PLAN IS MOVED BY HIS WRITTEN ORDERS AND NOTHING ELSE — except
to save his corps, to fight a battle he is already in, to take the ground he
stands on and to walk home after a peace (the rungs of `EnemyAI._evaluate_
marshal` that stand above the gate). His acts cost his court nothing: they are
carried out HERE (`the_pass`), before the enemy's phase, through the same
executor every order goes through.

ONE MODULE. The authored sets and the saved state live on `world.war_plans`
(`{"sets": [...], "holders": {...}}`); the state is written ONLY in the turn's
end pass (never inside a player's command — the take-back's books stay as they
are) and by a battle's own rout (`compromise`, `learns_of`; a battle is never
taken back). `planned` and `favoured` are pure reads.

Plans exist only where a scenario WRITES them (the 1805 campaign's `war_plans`
block; `backend/modding/validator.py` `_validate_war_plans`): a lesson, the old
map and a bare test board have none, and nothing here runs for them.
"""
from __future__ import annotations

import copy
import functools
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from backend.errors import report

# A plan's order is a standing order marked by these words (the idiom of
# `withdrawal.ROAD_HOME_COMMAND`: several sites rebuild a `StrategicOrder`,
# and every one of them carries `original_command` across).
PLAN_COMMAND = "the court's written orders — its war plan"

COMPROMISED_TURNS = 2     # §13: captured orders stay good until the next step, two turns at most
LEARNT_TURNS = 5          # §10.3: a routed man's place is favoured for five turns
HERE = "$here"            # a written place: where the man stands when the order is written
CAPITAL = "$capital"      # ... his own court's capital
AIM = "$aim"              # a favour only: the nearest of the court's own war aims
PLAN_FAVOUR_EXTRA = 1     # marches nearer a favoured aim counts, over the aim's own credit
ANY_LITERAL = "any_literal"


# ═══════════════════════════ the seams ═══════════════════════════════════════

def the_courts_follow_a_plan() -> bool:
    """IC-14's seam (`tests/_ic4_seams.py`, row PLAN). SHIPS UP — FIXED and
    SWITCHED ON November 23, 2026: the user's "fix warplans", then, shown the
    measure below, "Switch them on" (IC4-D1 closed; BASELINE_SERIES re-pinned
    from `tools/_ic4b_fix_series_arms_2026_11_23.json`'s "+PLAN" arm, the old
    pin kept as SERIES_BEFORE_IC4B).

    The record: built in Session 4 behind this seam and shipped down — the
    measure's R-HILL (4) (a letter-following enemy marshal acts no less often
    than today) was missed after its two rounds of content
    (`tools/_ic4_measure.py`; SYSTEMS_REFERENCE §235). The user ruled "On,
    after 20 seeds" (D41): if those seeds break a clause of the deploy gate,
    the seam stays down and the question is his. Session 4b read them: up, no
    minor was raised on any of the thirty seeds (clause 2;
    `tools/_ic4_promotions_wide_2026_11_23.json`). Traced (§236.8): every
    court at war drew a plan — France's ally Bavaria too, in her own war with
    Austria — and the general set ordered her one corps (Deroy, who follows
    orders to the letter) to hold where he stood from turn 2 until its steps
    ran out at turn 10; the peace came at 14 with the Tyrol that crowns her
    untaken (with the same coalition plan and none of her own he takes it at
    13). THE FIX (`_muster`): a plan is drawn only by a court at war with
    France. Measured again (the rules written first,
    `tools/_ic4_measure.py`): up, the band 28/25/26 and every clause of the gate
    but clause 2, still zero on the thirty; on 200 fresh seeds a minor rises on
    8 with the plans up and 9 with them down (`tools/_ic4b_wide_promotions.py`)
    — the thirty's zero is the sample's (at one seed in twenty-two, thirty seeds
    read zero about one time in four); per court the plans close Denmark's road
    to Scania (5 to 0) while Bavaria and Hesse rise more often. By D41 the seam
    stayed down and the question went back to the user with those numbers: he
    answered "Switch them on". Down: no pass, no plan order, no gate; every man
    is moved by his court's own logic."""
    return True


def a_planned_man_still_strikes_at_good_odds() -> bool:
    """Row FIGHT — an ARM, ships DOWN, built for the user's decision on the
    plans: up, a marshal under his court's written orders keeps today's
    fighting sense — when his court's own logic finds an attack at good odds
    (`EnemyAI._find_attack_opportunity`) and his orders did not move him
    tonight, he strikes; his orders still decide where he stands, where he
    marches and when he falls back. Down (and as the design's §10.1 words it):
    he is moved by his written orders and by nothing else."""
    return False


def a_plan_names_a_favoured_province() -> bool:
    """Row FAVOUR: a step's favoured province joins the march's pull. Down, the
    pull is the court's aims alone (R-HILL's first fallback)."""
    return True


def a_court_learns_a_routed_mans_task() -> bool:
    """Row LEARNS (§10.3): a French marshal on his own who is routed gives his
    task away. Down, nothing is learned."""
    return True


def the_plan_forced() -> str:
    """The measure's lever, never a rule: the id of the plan every holder whose
    set carries it draws, whatever the seed ("" as shipped — the seed draws)."""
    return ""


# ═══════════════════════════ the store ═══════════════════════════════════════

def from_block(raw: Any) -> Dict[str, Any]:
    """`world.war_plans` from a scenario's block or a save's key: the authored
    `sets` and, in a save, the `holders`' state. {} where nothing is written
    (the field is saved only when it holds something)."""
    if not isinstance(raw, dict) or not isinstance(raw.get("sets"), list) or not raw["sets"]:
        return {}
    out: Dict[str, Any] = {"sets": copy.deepcopy(raw["sets"])}
    held = raw.get("holders")
    if isinstance(held, dict) and held:
        out["holders"] = copy.deepcopy(held)
    return out


# The scenario that authors each campaign's written plans (`scenario_name` ->
# its file). The written sets are the scenario's CONTENT: a save carries the
# store only beside a holder's plan (`to_save`), and every load reads the sets
# back from here (`from_saved`). Only the 1805 campaign (decision 1).
SCENARIO_FILES: Dict[str, Tuple[str, ...]] = {
    "The Third Coalition, 1805": ("godot-client", "project-sovereign", "assets", "maps",
                                  "europe_1805.json"),
}


@functools.lru_cache(maxsize=8)
def _written_sets(scenario_name: str) -> str:
    """The written sets of the scenario that authors `scenario_name`, as JSON
    text (immutable in the cache) — "" where none is written or it cannot be
    read (a mod's scenario, a bare board, a lesson)."""
    parts = SCENARIO_FILES.get(str(scenario_name or ""))
    if not parts:
        return ""
    candidates = [Path(__file__).resolve().parents[2].joinpath(*parts)]
    base = getattr(sys, "_MEIPASS", None)
    if base:
        candidates.append(Path(base).joinpath(*parts))
    for path in candidates:
        try:
            with open(path, encoding="utf-8") as fh:
                block = (json.load(fh) or {}).get("war_plans")
        except (OSError, ValueError):
            continue
        sets = block.get("sets") if isinstance(block, dict) else None
        return json.dumps(sets) if isinstance(sets, list) and sets else ""
    return ""


def from_saved(raw: Any, scenario_name: str = "") -> Dict[str, Any]:
    """`world.war_plans` on a load (`WorldState.from_dict`): the save's own store
    where it carries one (a holder's plan beside its sets), else the written
    sets of the world's own scenario — so a board taken back, reloaded or
    copied before any court has drawn its plan keeps them. {} where the
    scenario writes none."""
    held = from_block(raw)
    if held:
        return held
    text = _written_sets(str(scenario_name or ""))
    return from_block({"sets": json.loads(text)}) if text else {}


def to_save(world) -> Dict[str, Any]:
    """What a save carries of the store: all of it beside a holder's plan;
    nothing while no court holds one and the sets can be read back from the
    world's own scenario (so a save gains no key until a court at war with
    France has drawn its plan — the plans ship UP since November 23, 2026, so a
    save made in the boot war carries one); the sets alone for a scenario that
    cannot be read back."""
    store = getattr(world, "war_plans", None)
    if not isinstance(store, dict) or not store:
        return {}
    if store.get("holders"):
        return copy.deepcopy(store)
    written = _written_sets(str(getattr(world, "scenario_name", "") or ""))
    if written and json.dumps(store.get("sets")) == written:
        return {}           # the scenario's own content, read back on every load
    return copy.deepcopy(store)     # sets of its own (a mod that kept the name)


def _store(world) -> Dict[str, Any]:
    held = getattr(world, "war_plans", None)
    return held if isinstance(held, dict) else {}


def sets(world) -> List[Dict[str, Any]]:
    return [s for s in (_store(world).get("sets") or []) if isinstance(s, dict)]


def holders(world) -> Dict[str, Dict[str, Any]]:
    """The saved state, read: `{holder: {plan, step, since, live_turns, favour,
    courts, enrolled, compromised, done, torn, learnt}}`."""
    held = _store(world).get("holders")
    return held if isinstance(held, dict) else {}


def _turn(world) -> int:
    return int(getattr(world, "current_turn", 0) or 0)


def _player(world) -> str:
    return str(getattr(world, "player_nation", "") or "")


def holder_of(world, nation: str) -> str:
    """The holder whose plan this court follows today, or ""."""
    for key, state in holders(world).items():
        if nation in (state.get("courts") or ()):
            return key
    return ""


def state_of(world, nation: str) -> Optional[Dict[str, Any]]:
    key = holder_of(world, nation)
    return holders(world).get(key) if key else None


def plan_of(world, key: str) -> Optional[Dict[str, Any]]:
    """The written plan a holder drew, or None (a plan struck from the file
    since the save: the holder is torn down at the next pass)."""
    state = holders(world).get(key) or {}
    wanted = str(state.get("plan") or "")
    for plan_set in sets(world):
        for plan in plan_set.get("plans") or ():
            if isinstance(plan, dict) and str(plan.get("id") or "") == wanted:
                return plan
    return None


def step_of(world, key: str) -> Optional[Dict[str, Any]]:
    state = holders(world).get(key) or {}
    plan = plan_of(world, key)
    steps = (plan or {}).get("steps") or []
    index = int(state.get("step", 0) or 0)
    if state.get("done") or not (0 <= index < len(steps)):
        return None
    return steps[index] if isinstance(steps[index], dict) else None


# ═══════════════════════════ the pure reads ══════════════════════════════════

def is_plan_order(order) -> bool:
    return order is not None and str(getattr(order, "original_command", "") or "") == PLAN_COMMAND


def planned(world, marshal) -> bool:
    """Is this man moved by his court's written orders tonight? O(1), PURE."""
    if marshal is None or not the_courts_follow_a_plan():
        return False
    if getattr(marshal, "nation", None) == _player(world):
        return False
    return is_plan_order(getattr(marshal, "strategic_order", None))


def acted_tonight(world, marshal) -> bool:
    """Did his written orders move him in tonight's pass? (One thing a turn,
    §2: his court's engagement rung does not strike a second time.)"""
    night = getattr(world, "_plan_night", None)
    return bool(isinstance(night, tuple) and night[0] == _turn(world)
                and getattr(marshal, "name", None) in night[1])


def _aims(world, nation: str) -> frozenset:
    """The court's OWN war aims tonight (`war_council.aim_pull_set` — the
    design's unmet targets, the stated objects still outstanding, the
    recapture of its own lost soil)."""
    try:
        from backend.game_logic.war_council import aim_pull_set
        return frozenset(aim_pull_set(world, nation))
    except Exception as exc:
        report(exc, "war_plans._aims: aim_pull_set")
        return frozenset()


def _favour_of(world, nation: str, written: Any) -> str:
    """A step's favoured province FOR THIS COURT: the province written, or —
    for the token `$aim` — the nearest of the court's own aims to its capital;
    "" unless it IS one of the court's aims and a court it is at war with
    holds it. So the favour is only ever a PRIORITY among what the court is
    already after: it can add no ground to its march, and none to what it may
    keep (the first measure's finding — a favoured enemy capital drew Russia
    on to Milan and Piedmont, two provinces kept outside any aim)."""
    aims = _aims(world, nation)
    if not aims:
        return ""
    text = str(written or "").strip()
    if text == AIM:
        home = str(world.get_nation_capital(nation) or "")
        ranked = sorted(aims, key=lambda p: (
            int(d) if (d := (world.get_distance(home, p) if home else 0)) is not None else 99, p))
        text = ranked[0] if ranked else ""
    if not text or text not in aims:
        return ""
    region = (getattr(world, "regions", None) or {}).get(text)
    holder = getattr(region, "controller", None) if region is not None else None
    if not holder or holder == nation or not world.is_at_war(nation, holder):
        return ""
    return text


def favoured(world, nation: str) -> frozenset:
    """The provinces this court's corps lean toward tonight — a PRIORITY among
    its own war aims, never ground outside them: its plan's favoured province
    (`_favour_of`) and a place it learned a routed French marshal was after
    (§10.3). The march's pull counts each as nearer still
    (`EnemyAI._agenda_biased_distance`, `PLAN_FAVOUR_EXTRA`); what a court may
    take or keep (`war_council.annexation_permitted`, `aim_pull_set`) is
    untouched. PURE, a walk over the holders (a handful)."""
    if not the_courts_follow_a_plan() or not sets(world):
        return frozenset()
    state = state_of(world, nation)
    if not state:
        return frozenset()
    out = set()
    if (a_plan_names_a_favoured_province() and not state.get("done")
            and nation not in (state.get("torn") or ())):
        place = _favour_of(world, nation, state.get("favour"))
        if place:
            out.add(place)
    learnt = state.get("learnt")
    if (a_court_learns_a_routed_mans_task() and isinstance(learnt, dict)
            and _turn(world) <= int(learnt.get("until", -1) or -1)):
        place = _favour_of(world, nation, learnt.get("place"))
        if place:
            out.add(place)
    return frozenset(out)


def capital_is_lost(world, nation: str) -> bool:
    """The court's own rule (`EnemyAI._is_capital_lost`, ONE predicate)."""
    try:
        from backend.ai.enemy_ai import capital_is_lost as _lost
        return bool(_lost(world, nation))
    except Exception as exc:
        report(exc, "war_plans.capital_is_lost")
        return False


def orders_in_words(world, marshal) -> List[str]:
    """His written orders as plain sentences — the order, then each unused
    line — for what France LEARNS (IC-15: the spy's report, captured orders).
    [] for a man under no plan. PURE; the caller decides who may read it."""
    order = getattr(marshal, "strategic_order", None)
    if not is_plan_order(order):
        return []
    from backend.commands import if_thens as _if_thens
    from backend.display_names import humanize_entity_name as _shown
    name = _shown(str(marshal.name))
    place = _shown(str(getattr(order, "target", "") or ""))
    head = {"HOLD": f"{name} holds {place}",
            "SUPPORT": f"{name} keeps by {place} and marches to his battles",
            "PURSUE": f"{name} chases {place} and attacks him when he is not outnumbered",
            }.get(order.command_type, f"{name} marches to {place} and holds it")
    out = [head + "."]
    for line in _if_thens.unused(order):
        said = _if_thens.sentence(line, _shown)
        if said:
            out.append(said if said.endswith(".") else said + ".")
    return out


# ═══════════════════════════ who holds a plan ════════════════════════════════

def _set_for(world, nation: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """`(holder, set)` for a court at war: the coalition's set while two or
    more of its members fight its target together; else the court's own set;
    else the scenario's general set; `("", None)` where none is written."""
    written = sets(world)
    coalition = getattr(world, "active_coalition", None) or {}
    name = str(coalition.get("name") or "")
    target = str(coalition.get("target_nation") or "")
    members = [str(m) for m in (coalition.get("members") or [])]
    if name and target and nation in members:
        fighting = [m for m in members if world.is_at_war(m, target)]
        if nation in fighting and len(fighting) >= 2:
            for plan_set in written:
                if str((plan_set.get("for") or {}).get("coalition") or "") == name:
                    return f"coalition::{name}", plan_set
    for plan_set in written:
        if str((plan_set.get("for") or {}).get("court") or "") == nation:
            return f"court::{nation}", plan_set
    for plan_set in written:
        if (plan_set.get("for") or {}).get("default"):
            return f"court::{nation}", plan_set
    return "", None


def _muster(world) -> Dict[str, Dict[str, Any]]:
    """Every holder that should stand tonight: `{holder: {"set", "courts"}}` —
    each court run by the game (never the player's, never a client: a client's
    men march at their lord's call) that is AT WAR WITH FRANCE (the player) and
    still on the map. A plan is drawn against France: a court whose wars are
    all with other courts — France's ally Bavaria against Austria, Denmark
    against Sweden — fights them by its own logic, as before. (Every court at
    war drew one until November 23, 2026, and the general set ordered Bavaria's
    one corps to hold where he stood through the war that wins her the Tyrol:
    §236.8, IC4b-28.)"""
    live: Dict[str, Dict[str, Any]] = {}
    player = _player(world)
    if not player:
        return live
    clients = getattr(world, "vassals", None) or {}
    active = set(world.get_active_nations())
    for nation in list(getattr(world, "enemy_nations", None) or []):
        if nation == player or nation in clients or nation not in active:
            continue
        if not world.is_at_war(nation, player):
            continue
        key, plan_set = _set_for(world, nation)
        if not key or plan_set is None:
            continue
        row = live.setdefault(key, {"set": plan_set, "courts": []})
        if nation not in row["courts"]:
            row["courts"].append(nation)
    return live


def _draw(world, key: str, plan_set: Dict[str, Any]) -> str:
    """The plan a holder draws: the campaign's seed among the set's written
    plans — the historical seed draws the first (the historical plan)."""
    ids = [str(p.get("id")) for p in (plan_set.get("plans") or [])
           if isinstance(p, dict) and p.get("id")]
    if not ids:
        return ""
    forced = str(the_plan_forced() or "")
    if forced and forced in ids:
        return forced
    from backend.game_logic import campaign_variance as _cv
    seed = str(getattr(world, "campaign_seed", "") or _cv.HISTORICAL_SEED)
    return str(_cv.seeded_tiebreak(seed, f"war_plan::{key}", ids))


# ═══════════════════════════ places ══════════════════════════════════════════

def _place(world, nation: str, written: Any, marshal=None) -> str:
    """A written place, resolved: a province's name, or one of the tokens."""
    text = str(written or "").strip()
    if not text:
        return ""
    if text == HERE:
        return str(getattr(marshal, "location", "") or "")
    if text == CAPITAL:
        return str(world.get_nation_capital(nation) or "")
    return text


def _held_by(world, courts: Sequence[str], province: str) -> bool:
    region = (getattr(world, "regions", None) or {}).get(str(province))
    return bool(region is not None and getattr(region, "controller", None) in set(courts))


# ═══════════════════════════ the steps ═══════════════════════════════════════

def _fresh_state(world, key: str, plan_id: str, courts: Sequence[str]) -> Dict[str, Any]:
    return {"plan": plan_id, "step": 0, "since": _turn(world), "live_turns": 0,
            "favour": "", "courts": list(courts), "enrolled": {}, "compromised": None,
            "done": False, "torn": []}


def _enter(world, key: str, state: Dict[str, Any]) -> None:
    """Stand on the step `state["step"]` names — skipping every step whose
    favoured province a court of the holder already holds (§12) — or mark the
    plan done when the steps run out. Nobody is enrolled on a new step yet."""
    plan = plan_of(world, key) or {}
    steps = plan.get("steps") or []
    while int(state.get("step", 0) or 0) < len(steps):
        step = steps[int(state["step"])]
        favour = str((step or {}).get("favour") or "").strip()     # as written: a province, or $aim
        if favour and favour != AIM and _held_by(world, state.get("courts") or (), favour):
            state["step"] = int(state["step"]) + 1
            continue
        state.update({"favour": favour, "since": _turn(world), "live_turns": 0,
                      "compromised": None, "enrolled": {}})
        return
    state.update({"done": True, "favour": "", "enrolled": {}, "compromised": None})


def _ended(world, key: str, state: Dict[str, Any]) -> bool:
    """Has the holder's step met its written end — or were its orders taken
    two turns ago (captured orders stay good two turns at most)?"""
    taken = state.get("compromised")
    if taken is not None and _turn(world) >= int(taken) + COMPROMISED_TURNS:
        return True
    step = step_of(world, key)
    ends = (step or {}).get("ends") or {}
    if "turns" in ends and int(state.get("live_turns", 0) or 0) >= int(ends.get("turns") or 0):
        return True
    used = ends.get("line_used")
    if isinstance(used, dict):
        man = world.get_marshal(str(used.get("marshal") or ""))
        order = getattr(man, "strategic_order", None) if man is not None else None
        if man is None or int(getattr(man, "strength", 0) or 0) <= 0 or not is_plan_order(order):
            # the man the step waited on is gone, or was driven off his orders
            return str(used.get("marshal") or "") in (state.get("enrolled") or {})
        lines = list(getattr(order, "if_thens", None) or [])
        index = int(used.get("index", 0) or 0)
        if 0 <= index < len(lines) and lines[index].get("used"):
            return True
    until = ends.get("until")
    if isinstance(until, dict) and str(until.get("if") or "") == "place_falls":
        region = (getattr(world, "regions", None) or {}).get(str(until.get("place") or ""))
        holder = getattr(region, "controller", None) if region is not None else None
        if holder and any(world.is_at_war(court, holder) for court in state.get("courts") or ()):
            return True
    return False


def _clear(marshal) -> None:
    """Take a plan order off a man: he is his court's ordinary marshal again."""
    if not is_plan_order(getattr(marshal, "strategic_order", None)):
        return
    marshal.strategic_order = None
    marshal.holding_position = False
    marshal.hold_region = ""
    try:
        from backend.commands.strategic import clear_order_bound_interrupt
        clear_order_bound_interrupt(marshal)
    except Exception as exc:
        report(exc, "war_plans._clear: clear_order_bound_interrupt")


def _literal_men(world, nation: str) -> List[Any]:
    return [m for m in world.get_marshals_by_nation(nation)
            if getattr(m, "personality", "") == "literal"
            and int(getattr(m, "strength", 0) or 0) > 0
            and not getattr(m, "captured_by", "")]


def _written_for(step: Dict[str, Any], marshal) -> Optional[Dict[str, Any]]:
    orders = (step or {}).get("orders") or {}
    spec = orders.get(marshal.name) or orders.get(ANY_LITERAL)
    return spec if isinstance(spec, dict) else None


def build_lines(world, marshal, spec: Dict[str, Any], written: Optional[int]) -> List[Dict[str, Any]]:
    """A written order's lines as `if_thens` lines (places resolved)."""
    from backend.commands import if_thens as _if_thens
    nation = marshal.nation
    out = []
    for raw in spec.get("lines") or ():
        if not isinstance(raw, dict):
            continue
        out.append(_if_thens.make_line(
            str(raw.get("if") or ""), then=str(raw.get("then") or ""),
            who=raw.get("who"), friend=raw.get("friend"),
            place=_place(world, nation, raw.get("place"), marshal) or None,
            to=_place(world, nation, raw.get("to"), marshal) or None,
            any_odds=bool(raw.get("any_odds")), written=written))
    return out


def _install(world, marshal, spec: Dict[str, Any]) -> bool:
    """Write a step's order on a man: where he is to stand, and the lines the
    rules take (`if_thens.settle` — the same rules as the player's literal
    men). A line the board has already made idle (a friend gone, a place
    fallen) is simply not written."""
    from backend.commands import if_thens as _if_thens
    from backend.models.marshal import StrategicOrder
    order = str(spec.get("order") or "hold")
    if order in ("support", "chase"):
        # SUPPORT a friend / CHASE an enemy — the standing orders a literal
        # man of any nation takes (§7); a man who is gone leaves the order a
        # hold of where he stands.
        other = world.get_marshal(str(spec.get("whom") or ""))
        gone = (other is None or int(getattr(other, "strength", 0) or 0) <= 0
                or bool(getattr(other, "captured_by", "")) or other is marshal)
        friend = (not gone) and other.nation == marshal.nation
        foe = (not gone) and world.is_at_war(marshal.nation, other.nation)
        if (order == "support" and friend) or (order == "chase" and foe):
            kind = "SUPPORT" if order == "support" else "PURSUE"
            kept, _refused = _if_thens.settle(world, marshal, kind,
                                              build_lines(world, marshal, spec, _turn(world)))
            marshal.strategic_order = StrategicOrder(
                command_type=kind, target=str(other.name), target_type="marshal",
                started_turn=_turn(world), issued_turn=_turn(world),
                original_command=PLAN_COMMAND, if_thens=kept)
            marshal.holding_position = False
            marshal.hold_region = ""
            try:
                from backend.commands.strategic import clear_order_bound_interrupt
                clear_order_bound_interrupt(marshal)
            except Exception as exc:
                report(exc, "war_plans._install: the question of the order a support or chase replaces")
            return True
        spec = {**spec, "place": HERE}
    place = _place(world, marshal.nation, spec.get("place") or HERE, marshal)
    if not place or (getattr(world, "regions", None) or {}).get(place) is None:
        return False
    here = place == str(marshal.location or "")
    kind = "HOLD" if here else "MOVE_TO"
    kept, _refused = _if_thens.settle(world, marshal, kind,
                                      build_lines(world, marshal, spec, _turn(world)))
    marshal.strategic_order = StrategicOrder(
        command_type=kind, target=place, target_type="region",
        started_turn=_turn(world), issued_turn=_turn(world),
        original_command=PLAN_COMMAND, if_thens=kept)
    marshal.holding_position = bool(here)
    marshal.hold_region = place if here else ""
    try:
        from backend.commands.strategic import clear_order_bound_interrupt
        clear_order_bound_interrupt(marshal)
    except Exception as exc:
        report(exc, "war_plans._install: clear_order_bound_interrupt")
    return True


def _enrol(world, key: str, state: Dict[str, Any]) -> None:
    """Each of the holder's letter-following marshals takes the step's order —
    ONCE a step (a man driven off his orders by a rout is his court's ordinary
    marshal until the next step); a man carrying another kind of order (the
    road home, a contingent's) keeps it; a man hired mid-step takes the lines
    written for any such man."""
    step = step_of(world, key)
    if step is None:
        return
    enrolled = state.setdefault("enrolled", {})
    index = int(state.get("step", 0) or 0)
    for court in state.get("courts") or ():
        if court in (state.get("torn") or ()):
            continue
        for man in _literal_men(world, court):
            if enrolled.get(man.name) == index:
                continue
            order = getattr(man, "strategic_order", None)
            if order is not None and not is_plan_order(order):
                continue
            spec = _written_for(step, man)
            if spec is None:
                continue
            if _install(world, man, spec):
                enrolled[man.name] = index


def _settle_the_holders(world) -> List[str]:
    """Reap, draw, tear, advance, enrol — the plan's bookkeeping for tonight.
    Returns the holders standing, in a stable order."""
    held = _store(world).setdefault("holders", {})
    live = _muster(world)
    owner = {name: key for key, state in held.items()
             for name in (state.get("enrolled") or {})}
    for man in (getattr(world, "marshals", None) or {}).values():
        if not is_plan_order(getattr(man, "strategic_order", None)):
            continue
        key = owner.get(man.name)
        if key is None or key not in live or man.nation not in live[key]["courts"]:
            _clear(man)
    for key in [k for k in held if k not in live]:
        del held[key]
    standing = []
    for key in sorted(live):
        courts = list(live[key]["courts"])
        state = held.get(key)
        if state is None or plan_of(world, key) is None:
            plan_id = _draw(world, key, live[key]["set"])
            if not plan_id:
                held.pop(key, None)
                continue
            state = held[key] = _fresh_state(world, key, plan_id, courts)
            _enter(world, key, state)
        joined = [c for c in courts if c not in (state.get("courts") or ())]
        state["courts"] = courts
        for court in joined:
            # A court that (re)joins a standing holder takes the step's orders
            # afresh: its men's marks from before it left (a peace with France
            # inside the step, a war renewed) would otherwise keep them off the
            # step until the next (IC4b-29).
            for man in world.get_marshals_by_nation(court):
                (state.get("enrolled") or {}).pop(man.name, None)
        torn = [c for c in courts if capital_is_lost(world, c)]
        state["torn"] = torn
        for court in torn:
            for man in _literal_men(world, court):
                if is_plan_order(getattr(man, "strategic_order", None)):
                    _clear(man)
                (state.get("enrolled") or {}).pop(man.name, None)
        if not state.get("done"):
            # A step written for N turns stands N nights: its end is read on
            # the nights it has ALREADY stood, then tonight is counted.
            if _ended(world, key, state):
                for court in courts:
                    for man in _literal_men(world, court):
                        _clear(man)
                state["step"] = int(state.get("step", 0) or 0) + 1
                _enter(world, key, state)
            if not state.get("done"):
                if len(torn) < len(courts):       # the clock stops while every capital is lost
                    state["live_turns"] = int(state.get("live_turns", 0) or 0) + 1
                _enrol(world, key, state)
        learnt = state.get("learnt")
        if isinstance(learnt, dict) and _turn(world) > int(learnt.get("until", -1) or -1):
            state.pop("learnt", None)
        standing.append(key)
    return standing


# ═══════════════════════════ the pass ════════════════════════════════════════

def _run(executor, game_state, world, marshal, action: str, target: Optional[str]) -> Dict[str, Any]:
    """ONE act of a planned man, through the executor every order goes through
    — free (`_strategic_execution`: the plan's own step sets no order aside),
    marked with the court that acts. The executor's own result, never a
    sentence of ours: what France is shown of it is the fog filter's to say."""
    command = {"marshal": marshal.name, "action": action, "type": "specific",
               "_strategic_execution": True}
    if target:
        command["target"] = target
    previous = getattr(world, "_ai_phase_nation", "")
    world._ai_phase_nation = marshal.nation
    try:
        result = executor.execute({"command": command}, game_state)
    finally:
        world._ai_phase_nation = previous
    if not isinstance(result, dict):
        result = {"success": False}
    result["ai_action"] = {"marshal": marshal.name, "action": action,
                           **({"target": target} if target else {})}
    result["nation"] = marshal.nation
    return result


def _may_walk(world, marshal, hop: str) -> bool:
    """May his march take this step? Never into a province an enemy corps
    stands in (a march never becomes an attack by itself), never onto a
    fighting garrison, and never onto ground his court may not take (the rule
    its own walk-ins obey — a move into open enemy ground takes it)."""
    region = (getattr(world, "regions", None) or {}).get(str(hop))
    if region is None:
        return False
    nation = marshal.nation
    for other in world.get_marshals_in_region(hop):
        if (other.nation != nation and int(getattr(other, "strength", 0) or 0) > 0
                and world.is_at_war(nation, other.nation)):
            return False
    holder = getattr(region, "controller", None)
    if holder and holder not in (nation, "Neutral") and world.is_at_war(nation, holder):
        try:
            from backend.game_logic.garrison_report import garrison_fights
            if garrison_fights(region):
                return False
            from backend.game_logic.war_council import annexation_permitted
            if not annexation_permitted(world, nation, str(hop), marshal=marshal):
                return False
        except Exception as exc:
            report(exc, "war_plans._may_walk")
            return False
    return True


def _road(world, marshal, dest: str, beside: bool = False) -> List[str]:
    """The road he may walk to `dest` tonight — re-plotted around every step
    he may not take; [] when there is none. With `beside`, the road stops in
    the province NEXT to `dest` (a man stands there — a friend he keeps by, an
    enemy he closes on — and the last step is never taken by a march)."""
    from backend.commands.strategic import plot_route
    barred: List[str] = []
    for _attempt in range(4):
        path, _verdict = plot_route(world, marshal, dest, use_weighted=True,
                                    avoid_regions=list(barred) or None,
                                    avoid_is_law=bool(barred))
        road = [r for r in (path or []) if r != marshal.location]
        if beside and road and road[-1] == dest:
            road = road[:-1]
        if not road:
            return []
        bad = [r for r in road if not _may_walk(world, marshal, r)]
        if not bad:
            return road
        if dest in bad:
            return []
        barred.extend(b for b in bad if b not in barred)
    return []


def _hold_here(world, marshal, order) -> None:
    """The march, ended, becomes the hold of the ground he stands on, with
    the lines still unused ("he holds there on arrival")."""
    from backend.commands import if_thens as _if_thens
    from backend.models.marshal import StrategicOrder
    where = str(marshal.location or "")
    marshal.strategic_order = StrategicOrder(
        command_type="HOLD", target=where, target_type="region",
        started_turn=_turn(world), issued_turn=_turn(world),
        original_command=PLAN_COMMAND,
        if_thens=[dict(line) for line in _if_thens.lines(order)])
    from backend.commands.strategic import clear_order_bound_interrupt
    clear_order_bound_interrupt(marshal)     # the old order's question dies with it
    marshal.holding_position = True
    marshal.hold_region = where


def _march_to(world, marshal, order, place: str) -> None:
    """His order becomes the march to `place` (a fall-back, a march line, a
    hold he was driven from), carrying his lines."""
    from backend.commands import if_thens as _if_thens
    from backend.models.marshal import StrategicOrder
    marshal.strategic_order = StrategicOrder(
        command_type="MOVE_TO", target=place, target_type="region",
        started_turn=_turn(world), issued_turn=_turn(world),
        original_command=PLAN_COMMAND,
        if_thens=[dict(line) for line in _if_thens.lines(order)])
    from backend.commands.strategic import clear_order_bound_interrupt
    clear_order_bound_interrupt(marshal)     # the old order's question dies with it
    marshal.holding_position = False
    marshal.hold_region = ""


def _walk(world, executor, game_state, marshal) -> List[Dict[str, Any]]:
    """Carry his standing order one night: a march walks (his range of
    provinces, each step one he may take), a hold only keeps his post — no
    digging in; that is a line's to order."""
    rows: List[Dict[str, Any]] = []
    order = marshal.strategic_order
    if order.command_type in ("SUPPORT", "PURSUE"):
        return _keep_by_or_close_on(world, executor, game_state, marshal)
    if order.command_type == "HOLD":
        if str(order.target or "") == str(marshal.location or ""):
            marshal.holding_position = True
            marshal.hold_region = str(marshal.location or "")
            return rows
        _march_to(world, marshal, order, str(order.target or ""))
        order = marshal.strategic_order
    dest = str(order.target or "")
    for _step in range(max(1, int(getattr(marshal, "movement_range", 1) or 1))):
        if str(marshal.location or "") == dest:
            break
        road = _road(world, marshal, dest)
        if not road:
            break
        if getattr(marshal, "fortified", False):
            left = _run(executor, game_state, world, marshal, "unfortify", None)
            if not left.get("success"):
                break
            rows.append(left)
        before = str(marshal.location or "")
        moved = _run(executor, game_state, world, marshal, "move", road[0])
        if not moved.get("success") or str(marshal.location or "") == before:
            break
        rows.append(moved)
        if not is_plan_order(getattr(marshal, "strategic_order", None)):
            return rows          # the march met something that took his order
    if str(marshal.location or "") == dest and is_plan_order(marshal.strategic_order):
        _hold_here(world, marshal, marshal.strategic_order)
    return rows


def _beside(world, marshal, province: str) -> bool:
    here = world.get_region(str(marshal.location or ""))
    return bool(here is not None and (province == here.name
                                      or province in (getattr(here, "adjacent_regions", None) or ())))


def _keep_by_or_close_on(world, executor, game_state, marshal) -> List[Dict[str, Any]]:
    """A SUPPORT order's night — he keeps by his friend (marches to stand in
    the province next to him; his friend's battles reach him by the arrival
    roll, a written support's own weight) — and a PURSUE order's — he closes
    on the enemy named where his nation sees him, and strikes him when he
    stands within reach and does not outnumber him (the plain attack's rule,
    `if_thens.attack_target`). The man gone: he holds where he stands, with
    the lines still unused. A march never takes the last step by itself."""
    from backend.commands import if_thens as _if_thens
    rows: List[Dict[str, Any]] = []
    order = marshal.strategic_order
    other = world.get_marshal(str(order.target or ""))
    if (other is None or int(getattr(other, "strength", 0) or 0) <= 0
            or getattr(other, "captured_by", "")):
        _hold_here(world, marshal, order)
        return rows
    there = str(other.location or "")
    chasing = order.command_type == "PURSUE"
    if chasing:
        if not world.is_at_war(marshal.nation, other.nation):
            _hold_here(world, marshal, order)
            return rows
        if not _if_thens._sees(world, marshal, there):
            return rows                       # out of his court's sight: he does not guess
        target = _if_thens.attack_target(world, marshal, {"any_odds": False}, {"enemy": other})
        if target is not None and target.name == other.name:
            if getattr(marshal, "fortified", False):
                left = _run(executor, game_state, world, marshal, "unfortify", None)
                if left.get("success"):
                    rows.append(left)
            struck = _run(executor, game_state, world, marshal, "attack", other.name)
            if struck.get("success") or struck.get("events") or struck.get("battle_result"):
                rows.append(struck)
            return rows
    if _beside(world, marshal, there):
        return rows                           # he is by him: nothing to march
    for _step in range(max(1, int(getattr(marshal, "movement_range", 1) or 1))):
        if _beside(world, marshal, str(other.location or "")):
            break
        road = _road(world, marshal, str(other.location or ""), beside=True)
        if not road:
            break
        if getattr(marshal, "fortified", False):
            left = _run(executor, game_state, world, marshal, "unfortify", None)
            if not left.get("success"):
                break
            rows.append(left)
        before = str(marshal.location or "")
        moved = _run(executor, game_state, world, marshal, "move", road[0])
        if not moved.get("success") or str(marshal.location or "") == before:
            break
        rows.append(moved)
        if not is_plan_order(getattr(marshal, "strategic_order", None)):
            break
    return rows


def _fire(world, executor, game_state, marshal, hit: Dict[str, Any]) -> List[Dict[str, Any]]:
    """ONE line of his written orders, carried out: attack (the enemy that
    tripped it, failing him the weakest he sees — never against the odds
    unless the line says so), fall back or march (the order becomes that
    march, walked tonight), dig in. The line is used once it fires."""
    from backend.commands import if_thens as _if_thens
    rows: List[Dict[str, Any]] = []
    line = hit["line"]
    then = str(line.get("then") or "")
    order = marshal.strategic_order
    if then == "attack":
        target = _if_thens.attack_target(world, marshal, line, {"enemy": hit.get("enemy")})
        if target is None:
            return rows                      # nobody he may strike now: the line waits
        line["used"] = True
        if getattr(marshal, "fortified", False):
            left = _run(executor, game_state, world, marshal, "unfortify", None)
            if left.get("success"):
                rows.append(left)
        struck = _run(executor, game_state, world, marshal, "attack", target.name)
        if struck.get("success") or struck.get("events") or struck.get("battle_result"):
            rows.append(struck)
        still = getattr(marshal, "strategic_order", None)
        if is_plan_order(still) and still.command_type == "HOLD":
            # he may have advanced with the victory: he holds the ground he stands on
            still.target = str(marshal.location or "")
            marshal.hold_region = str(marshal.location or "")
        return rows
    line["used"] = True
    if then in ("fall_back", "march"):
        place = str(line.get("to") or "")
        if place:
            _march_to(world, marshal, order, place)
            rows.extend(_walk(world, executor, game_state, marshal))
        return rows
    if then == "dig_in":
        if order.command_type != "HOLD":
            _hold_here(world, marshal, order)
        dug = _run(executor, game_state, world, marshal, "fortify", None)
        if dug.get("success"):
            rows.append(dug)
    return rows


def _fit_to_act(world, marshal) -> bool:
    """His written orders move him tonight only when he is whole and free: a
    broken or recovering corps, a man who already fell back today, a corps in
    a battle (an enemy in his province) and a corps securing a fortress are
    his court's survival rungs' to move, not the plan's."""
    if int(getattr(marshal, "strength", 0) or 0) <= 0 or getattr(marshal, "captured_by", ""):
        return False
    if (getattr(marshal, "broken", False) or getattr(marshal, "retreating", False)
            or getattr(marshal, "retreated_this_turn", False)
            or int(getattr(marshal, "retreat_recovery", 0) or 0) > 0
            or getattr(marshal, "occupation_region", None)):
        return False
    nation = marshal.nation
    for other in world.get_marshals_in_region(str(marshal.location or "")):
        if (other.nation != nation and int(getattr(other, "strength", 0) or 0) > 0
                and world.is_at_war(nation, other.nation)):
            return False
    return True


def _over(world) -> bool:
    if getattr(world, "game_over", False):
        return True
    try:
        from backend.game_logic import game_end as _game_end
        return _game_end.terminal_ending(world) is not None
    except Exception as exc:
        report(exc, "war_plans._over: terminal_ending")
        return False


def the_pass(world, executor, game_state) -> List[Dict[str, Any]]:
    """§2 step 3 — "each enemy literal marshal checks his if-thens once, on
    what you have just done": the plans' bookkeeping, then every planned
    man's lines READ on one frozen board (one man's act cannot make another's
    line true), then carried out — court by court, by rank — the first true
    line, else his standing order's night. Returns the executor's own results
    (they join the enemy phase's telling; the fog filter decides what France
    sees). Nothing runs where no plan is written, or with the seam down."""
    if not the_courts_follow_a_plan() or not sets(world) or executor is None:
        return []
    from backend.commands import if_thens as _if_thens
    rows: List[Dict[str, Any]] = []
    world.refresh_marshal_indexes()
    standing = _settle_the_holders(world)
    try:
        from backend.game_logic import learned as _learned
        _learned.tidy(world)          # what was learned of a man or a court now gone
    except Exception as exc:
        report(exc, "war_plans.the_pass: learned.tidy")
    acted: set = set()
    world._plan_night = (_turn(world), acted)
    readings: List[Tuple[Any, Optional[Dict[str, Any]]]] = []
    held = holders(world)
    for key in standing:
        for court in (held.get(key) or {}).get("courts") or ():
            try:
                from backend.game_logic import precedence as _court
                order_of = {m.name: n for n, m in enumerate(_court.order_of_precedence(world, court))}
            except Exception as exc:
                report(exc, "war_plans.the_pass: order_of_precedence")
                order_of = {}
            men = [m for m in _literal_men(world, court) if planned(world, m)]
            men.sort(key=lambda m: (order_of.get(m.name, len(order_of)), m.name))
            for man in men:
                order = man.strategic_order
                for line in _if_thens.lines(order):
                    why = _if_thens.struck(world, man, line)
                    if why:
                        line["used"] = True
                        line["struck"] = why
                if not _fit_to_act(world, man):
                    continue
                try:
                    hit = _if_thens.ready(world, man, order)
                except Exception as exc:
                    report(exc, f"war_plans.the_pass: ready({man.name})")
                    hit = None
                readings.append((man, hit))
    for man, hit in readings:
        if _over(world):
            break
        if not planned(world, man) or not _fit_to_act(world, man):
            continue
        try:
            done = (_fire(world, executor, game_state, man, hit) if hit is not None
                    else _walk(world, executor, game_state, man))
        except Exception as exc:
            report(exc, f"war_plans.the_pass: {man.name}")
            done = []
        if done:
            acted.add(man.name)
            rows.extend(done)
    world.refresh_marshal_indexes()
    return rows


# ═══════════════════════════ what a battle writes ════════════════════════════

def compromise(world, nation: str) -> bool:
    """A court's orders were TAKEN (captured orders, IC-15): its step ends two
    turns from now at the latest. True when the court holds a plan."""
    if not the_courts_follow_a_plan():
        return False
    state = state_of(world, nation)
    if not state or state.get("done"):
        return False
    if state.get("compromised") is None:
        state["compromised"] = _turn(world)
    return True


def learns_of(world, nation: str, task: Any) -> bool:
    """§10.3 — one of France's marshals ON HIS OWN was routed by this court:
    it learns his task, and if he was to take a place, that place joins what
    its corps favour for five turns (starting again if it is learned again).
    True when something was learned."""
    if not (the_courts_follow_a_plan() and a_court_learns_a_routed_mans_task()):
        return False
    if not isinstance(task, dict) or str(task.get("task") or "") != "take":
        return False
    place = str(task.get("target") or "")
    state = state_of(world, nation)
    if not place or not state:
        return False
    state["learnt"] = {"place": place, "until": _turn(world) + LEARNT_TURNS}
    return True
