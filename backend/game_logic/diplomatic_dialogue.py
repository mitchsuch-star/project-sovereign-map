"""
Diplomatic Dialogue State Machine — Phase 8 Session 3

Handles specificity classification, dialogue generation, and game state bucketing
for Talleyrand's conversational diplomacy system.

Entry points:
  - classify_diplomatic_intent() → routes parsed command to dialogue type
  - generate_dialogue() → creates pending_diplomatic_dialogue dict
  - get_game_bucket() → determines game situation for template selection
"""

from typing import Dict, Optional

from backend.display_names import (
    format_terms_for_display as _shared_format_terms_for_display,
    proposal_display_name,
)
from backend.nation_config import (
    DEFAULT_PLAYER_NATION,
    build_enemy_nations,
    get_player_diplomat,
    get_player_nation,
)


# ═══════ NATION NAME ALIASES ═══════
NATION_ALIASES = {
    "england": "Britain",
    "uk": "Britain",
    "united kingdom": "Britain",
    "great britain": "Britain",
    "british": "Britain",
    "english": "Britain",
    "britain": "Britain",
    "the british": "Britain",
    "britian": "Britain",  # common typo
    "britiain": "Britain",  # common typo
    "prussian": "Prussia",
    "prussia": "Prussia",
    "the prussians": "Prussia",
    "prussians": "Prussia",
    "prusia": "Prussia",  # common typo
    "austrian": "Austria",
    "austria": "Austria",
    "the austrians": "Austria",
    "austrians": "Austria",
    "autria": "Austria",  # common typo
    "saxon": "Saxony",
    "saxons": "Saxony",
    "saxony": "Saxony",
    "the saxons": "Saxony",
    "france": "France",
    "french": "France",
    "the french": "France",
}

KNOWN_NATIONS = set(build_enemy_nations(DEFAULT_PLAYER_NATION))


def get_known_nations(world=None) -> set:
    """Return the set of known nations, including any vassals (R93)."""
    nations = set(KNOWN_NATIONS)
    if world:
        nations = set(getattr(world, 'enemy_nations', [])) or set(build_enemy_nations(get_player_nation(world)))
        nations.discard(get_player_nation(world))
        vassals = getattr(world, 'vassals', {})
        nations.update(vassals.keys())
    return nations

# ═══════ PROPOSAL TYPE KEYWORDS ═══════
PROPOSAL_TYPE_KEYWORDS = {
    "peace": ["peace", "ceasefire", "end the war", "stop fighting", "end hostilities",
              "sue for peace", "make peace", "peace deal", "peace offer", "settle",
              "end war", "stop the war", "peace agreement"],
    "defensive_alliance": ["defensive alliance", "defense alliance", "mutual defense",
                           "defense pact", "defensive pact", "defend each other"],
    "alliance": ["alliance", "ally", "allies", "allied", "form alliance",
                 "full alliance", "military alliance", "join forces",
                 "unite with", "unite against", "become allies"],
    "armistice": ["armistice", "truce", "temporary peace", "temporary ceasefire",
                  "pause hostilities", "halt fighting", "brief truce"],
    "open_borders": ["open borders", "free passage", "passage rights", "border access",
                     "right of passage", "cross borders", "border agreement",
                     "transit rights", "march through"],
    "non_aggression": ["non-aggression", "non aggression", "nonaggression", "pact",
                       "non aggression pact", "neutrality", "neutrality pact",
                       "mutual non-aggression", "agree not to attack"],
    "vassalage": ["vassal", "vassalage", "subjugate", "submit", "submission", "puppet",
                  "tributary", "client state", "protectorate", "subject"],
}

def _display_proposal_type(proposal_type: str) -> str:
    """Convert internal proposal_type to player-facing display name."""
    return proposal_display_name(proposal_type)


# ═══════ MISSION TYPE KEYWORDS ═══════
MISSION_TYPE_KEYWORDS = {
    "IMPROVE_RELATIONS": ["improve relations", "build relations", "warm relations", "befriend",
                          "better relations", "strengthen relations", "friendly",
                          "build rapport", "diplomatic relations", "get closer to"],
    "COURT_NATION": ["court", "charm", "woo", "seduce", "win over", "sway",
                     "bring over", "convince", "persuade", "entice",
                     "lure", "attract"],
    "GATHER_INTEL": ["gather intel", "spy", "intelligence", "information",
                     "spy on", "gather information", "reconnaissance on",
                     "what are they doing", "what is happening in",
                     "investigate", "learn about"],
    "UNDERMINE_ALLIANCE": ["undermine", "sabotage", "weaken alliance", "drive a wedge",
                           "break apart", "split", "divide", "sow discord",
                           "turn against", "poison relations"],
    "REASSURE_ALLY": ["reassure", "calm", "soothe", "appease",
                      "strengthen alliance", "reaffirm", "shore up",
                      "bolster alliance", "keep them happy"],
}

# ═══════ FEASIBILITY KEYWORDS ═══════
FEASIBILITY_KEYWORDS = [
    "what would it take", "can we", "is it possible", "how hard",
    "feasibility", "realistic", "should i focus", "what are the chances",
    "how likely", "what do we need", "what must we do",
]

# ═══════ MISSION DP COSTS ═══════
MISSION_DP_COSTS = {
    "IMPROVE_RELATIONS": 1,
    "COURT_NATION": 2,
    "GATHER_INTEL": 1,
    "UNDERMINE_ALLIANCE": 2,
    "REASSURE_ALLY": 1,
    # MS-8 (playtest re-score, September 12 2026): "CONTINENTAL_SYSTEM" was
    # REMOVED. It appeared here, in `main.py`'s display map and in one test
    # asserting this dict literal — and in `MISSION_TYPE_KEYWORDS` (so no
    # parse could emit it), `MISSION_DESCRIPTIONS` (so no confirm could
    # name it), `MISSION_EFFECTS` (so the tick wrote nothing) and no wizard
    # row. GR9: a dead branch with no owner is removed, not left labelled.
    # The Continental System itself is alive and is NAVAL_SPEC's CS 2.0.
}

# ═══════ MISSION EFFECTS ═══════
MISSION_EFFECTS = {
    "IMPROVE_RELATIONS": {"relation_change": 5},
    "COURT_NATION": {"relation_change": 5, "undermine_chance": 0.20, "undermine_amount": -3},
    "GATHER_INTEL": {"duration": 3},
    "UNDERMINE_ALLIANCE": {"target_pair_relation_change": -3},
    "REASSURE_ALLY": {"relation_change": 3},
}

MISSION_DESCRIPTIONS = {
    # MS-4: every other description carries its own preposition; this one
    # did not, so the flagship mission's confirmation read "begin efforts to
    # improve relations Austria".
    "IMPROVE_RELATIONS": "improve relations with",
    "COURT_NATION": "court and charm",
    "GATHER_INTEL": "gather intelligence on",
    "UNDERMINE_ALLIANCE": "undermine alliances with",
    "REASSURE_ALLY": "reassure",
}


# ── MS-1 "The Desk Is Not Locked" (playtest re-score, September 12 2026) ──
# `world.active_diplomatic_mission` is NOT cleared when a mission completes
# (`GATHER_INTEL` sets `completed: True` and leaves the dict standing, which
# is what lets the ledger say "completed"). Three consumers checked
# `completed` — the top bar, the Talleyrand ledger tab and the wizard's
# nation list — and the wizard's own availability gate did not. Measured:
# after the FIRST intelligence mission finishes, every mission row for every
# court reads "Mission already active" for the rest of the campaign, while
# the top bar next to it says Talleyrand is idle. The dict is serialized, so
# the lockout survives save/load. One predicate now answers the question
# everywhere. False reproduces the "any dict at all locks the desk" arm.
ONE_PREDICATE_ANSWERS_MISSION_LIVENESS = True


def mission_is_live(world) -> bool:
    """Is a diplomatic mission actually running right now?

    A completed mission is a RECORD, not a commitment: it keeps the surfaces
    able to say what was achieved without holding the desk shut.
    """
    mission = getattr(world, "active_diplomatic_mission", None)
    if not mission or not isinstance(mission, dict):
        return False
    if not ONE_PREDICATE_ANSWERS_MISSION_LIVENESS:
        return True
    return not mission.get("completed")


def mission_effect_magnitude(world, mission_type: str, key: str) -> int:
    """The figure the tick will ACTUALLY apply, skill scaling included.

    MS-3. `MISSION_EFFECTS` holds the base; `_process_mission_effects`
    multiplies it by the acting diplomat's skill bonus before writing. Every
    display surface quoted the base, so on the shipped 1805 board — where
    Talleyrand's skill is 10 and the bonus is always x1.5 — the game
    advertised +5 and paid +8, "-3 between targets" and paid -4. Shown is
    applied now, from one source both sides call.
    """
    base = int((MISSION_EFFECTS.get(mission_type, {}) or {}).get(key, 0) or 0)
    if not base or not MISSION_EFFECT_TEXT_IS_THE_APPLIED_FIGURE:
        return base
    try:
        from backend.game_logic.diplomacy import get_mission_skill_multiplier
    except Exception:
        return base
    # `int(round(...))`, byte-for-byte what `_process_mission_effects`
    # writes. `int()` alone gave +7 where the tick pays +8 — the same
    # shown-vs-applied gap one rounding mode down, caught by the standing
    # pin on its first run.
    return int(round(base * get_mission_skill_multiplier(world)))


# MS-3 flip lever. False reproduces the un-scaled base figure on every
# display surface.
MISSION_EFFECT_TEXT_IS_THE_APPLIED_FIGURE = True


# ═══════ IQ-4 "The Cabinet Is Visible" — ONE source for a running mission ═══════
# The mission system was mechanically live and on no surface a player reads:
# not the Strategic Ledger, not the notice rail, not the campaign log's end,
# not the help. Every surface now reads these helpers, and every figure in
# them is the tick's own (`mission_effect_magnitude`, `relation_drift_step`).
# Flip levers: False reproduces master 7bbf82b8 on that surface.
MISSION_RAIL_NOTICE = True
MISSION_LOG_ENDS = True

MISSION_RECALL_LABEL = "Recall Talleyrand"
MISSION_RECALL_DETAIL = (
    "Free — no DP, no action point. He comes home; relations keep what he "
    "has won.")


def _court_favour_now(world) -> int:
    """The favour a live COURT mission adds to an alliance offer right now."""
    mission = getattr(world, "active_diplomatic_mission", None)
    if not mission_is_live(world) or mission.get("type") != "COURT_NATION":
        return 0
    from backend.game_logic.diplomacy import court_favour_mod
    return int(court_favour_mod(world, {
        "type": "alliance",
        "proposer_nation": getattr(world, "player_nation", "France"),
        "target_nation": mission.get("target", ""),
    }))


def mission_effect_text(world, mission_type: str, short: bool = False) -> str:
    """The one effect-text builder. `short` = the Cabinet row; long = ledgers.

    Every figure is the applied one. With the Court's Favour lever down the
    strings are byte-identical to the two tables this replaces (the wizard's
    `_MISSION_EFFECT_SHORT`, the Talleyrand tab's `_MISSION_EFFECT_TEXT`).
    """
    def _m(key: str = "relation_change") -> int:
        return mission_effect_magnitude(world, mission_type, key)

    if mission_type in ("IMPROVE_RELATIONS", "REASSURE_ALLY"):
        return f"{_m():+d} relation/turn" if short else f"{_m():+d} relation per turn"
    if mission_type == "COURT_NATION":
        from backend.game_logic import diplomacy as _d
        if _d.COURT_FAVOUR_ACTIVE:
            per, cap = int(_d.COURT_FAVOUR_PER_TURN), int(_d.COURT_FAVOUR_CAP)
            _eff = MISSION_EFFECTS.get("COURT_NATION", {})
            chance = int(round(float(_eff.get("undermine_chance", 0)) * 100))
            loss = int(_eff.get("undermine_amount", 0))
            if short:
                return (f"{_m():+d} relation/turn, proposals +{per}/turn courted "
                        f"(max +{cap}), {chance}% blowback")
            return (f"{_m():+d} relation per turn; our proposals to them "
                    f"+{per} per turn courted (max +{cap}, now "
                    f"+{_court_favour_now(world)}); {chance}% chance of {loss:+d}")
        return (f"{_m():+d} relation/turn, 20% blowback" if short
                else f"{_m():+d} relation per turn, 20% blowback risk")
    if mission_type == "GATHER_INTEL":
        return ("3 turns, then full intel for 5" if short
                else "3 turns to complete, then full intel for 5")
    if mission_type == "UNDERMINE_ALLIANCE":
        value = _m("target_pair_relation_change")
        return (f"{value:+d} relation between targets/turn" if short
                else f"{value:+d} relation between targets per turn")
    return ""


def _plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def project_mission_turns(world, status: dict) -> tuple:
    """(kind, turns, note) — what stands between a mission and its end.

    Pure: at most 40 arithmetic steps and no region scan (GR8). A relation
    forecast steps the tick's own arithmetic — the clamped effect, the MS-9b
    completion test, then `relation_drift_step` — and is labelled "≈": battles,
    treaties and envoys also move relations, so it is a forecast, never an
    applied figure. `turns == -1` whenever the answer is not a count.
    """
    from backend.game_logic import diplomacy as _d
    mission_type = status["type"]
    target_display = status["target_display"]
    dp = int(status["dp_per_turn"])
    if status["paused"]:
        if status["pause_reason"] == "transit":
            return ("transit", -1, "paused: he is carrying your proposal — costs "
                                   "nothing, earns nothing until he returns")
        left = max(0, 3 - int(status.get("paused_turns", 0)))
        return ("starved", left, f"paused: {dp} DP needed — collapses in "
                                 f"{_plural(left, 'turn')} without it")
    if mission_type == "GATHER_INTEL":
        duration = int(MISSION_EFFECTS.get("GATHER_INTEL", {}).get("duration", 3))
        left = max(0, duration - int(status["turns_active"]))
        target = status["target"]
        provinces = len(world.get_nation_regions(target)) if target else 0
        return ("duration", left, f"{_plural(left, 'turn')} left, then "
                                  f"{_plural(provinces, 'province')} of "
                                  f"{target_display} open to us for 5 turns")
    if mission_type == "UNDERMINE_ALLIANCE":
        target, ally = status["target"], status.get("target_ally", "")
        state = world.diplomatic_states.get(world._make_diplo_key(target, ally), "PEACE")
        floor = int(_d.STATE_RELATION_THRESHOLDS.get(state, 0) or 0) - 30
        counted = int((getattr(world, "turns_below_threshold", {}) or {}).get(
            world._make_diplo_key(target, ally), 0) or 0)
        # IQ-4 review: the auto-downgrade steps ONE rung — an ALLIANCE falls to
        # a defensive alliance (still allied) and the count restarts at the
        # next floor, so the break takes two runs of five, not one.
        if ally and not world.are_allies(target, ally):
            return ("alliance", -1, "their alliance is broken — he reports home")
        if state == "ALLIANCE":
            next_floor = int(_d.STATE_RELATION_THRESHOLDS.get(
                "DEFENSIVE_ALLIANCE", 0) or 0) - 30
            return ("alliance", -1, f"their alliance falls to a defensive alliance "
                                    f"after 5 turns at {floor} or below — now "
                                    f"{status['current_relation']}, {counted} of 5 "
                                    f"counted; breaking it needs a further 5 turns "
                                    f"at {next_floor} or below")
        return ("alliance", -1, f"their alliance breaks after 5 turns at {floor} "
                                f"or below — now {status['current_relation']}, "
                                f"{counted} of 5 counted")
    # The relation missions: step the tick's own arithmetic.
    effect = int(status["effect_per_turn"])
    player = getattr(world, "player_nation", "France")
    target = status["target"]
    relation = int(status["current_relation"])
    # COURT never completes at the ceiling (`_process_mission_effects`): its
    # work is the favour, which lasts only while he stays. Its end is the
    # player's recall, so the note counts the funded turns to the full favour
    # and then says it holds — never a completion that is not coming.
    if mission_type == "COURT_NATION" and _d.COURT_FAVOUR_ACTIVE:
        cap = int(_d.COURT_FAVOUR_CAP)
        per = max(1, int(_d.COURT_FAVOUR_PER_TURN))
        owed = cap - per * int(status["turns_active"])
        favour_ticks = max(0, -(-owed // per))
        court_state = world.get_diplomatic_state(
            getattr(world, "player_nation", "France"), status["target"])
        if court_state == "WAR":
            # IQ-4 review: at war the favour is SUSPENDED, not lost — it
            # returns at the peace (turns_active is kept), and his courting
            # still warms the relation the peace terms read. Never advise a
            # recall here: it would throw both away, and COURT cannot be
            # restarted until the peace.
            return ("suspended", -1, "no favour while we are at war — his courting "
                                     "still warms relations, and the favour returns "
                                     "at the peace")
        if favour_ticks == 0:
            if court_state == "ALLIANCE":
                return ("holding", -1, f"the alliance is signed — his +{cap} has no "
                                       "treaty left to carry; recall him")
            return ("holding", -1, f"the favour stands at +{cap} and holds while "
                                   "he stays — recall him once the treaty is signed")
        return ("favour", favour_ticks,
                f"{_plural(favour_ticks, 'funded turn')} to the full +{cap}; "
                "the favour holds while he stays")
    for step in range(1, 41):
        relation = max(-_d.RELATION_CLAMP, min(_d.RELATION_CLAMP, relation + effect))
        if effect > 0 and relation >= _d.RELATION_CLAMP:
            tail = ", barring blowback" if mission_type == "COURT_NATION" else ""
            return ("ceiling", step, f"≈{_plural(step, 'turn')} to "
                                     f"{_d.RELATION_CLAMP:+d} at the present rate{tail}")
        relation += _d.relation_drift_step(world, player, target, relation=relation)
    return ("open", -1, "no end in sight at the present rate — recall him or "
                        "change course")


def mission_recall_command(world) -> str:
    """The recall order — the Cabinet row's own spelling
    (`diplomacy_wizard.gd`, the `cancel_mission` arm), so the two never
    drift apart. Free: `diplomatic_mission` is a free action."""
    mission = getattr(world, "active_diplomatic_mission", None) or {}
    return f"Talleyrand, cancel mission with {mission.get('target', '')}"


def mission_status(world) -> Optional[dict]:
    """Everything a surface may say about the running mission — or None.

    One dict, all ints and strings (GR2). The ledger, the notice rail, the
    help and the Talleyrand tab read it; none of them computes a figure of
    its own.
    """
    if not mission_is_live(world):
        return None
    from backend.display_names import MISSION_TYPE_DISPLAY, display_nation
    from backend.game_logic import diplomacy as _d
    mission = world.active_diplomatic_mission
    mission_type = str(mission.get("type", "") or "")
    target = str(mission.get("target", "") or "")
    ally = str(mission.get("target_ally", "") or "")
    player = getattr(world, "player_nation", "France")
    dp = int(MISSION_DP_COSTS.get(mission_type, 1))
    if mission_type == "UNDERMINE_ALLIANCE" and ally:
        pair = (target, ally)
        effect = mission_effect_magnitude(world, mission_type, "target_pair_relation_change")
        baseline = mission.get("initial_pair_relation")
    else:
        pair = (player, target)
        effect = mission_effect_magnitude(world, mission_type, "relation_change")
        baseline = mission.get("initial_relation")
    current = int(world.nation_relations.get(world._make_diplo_key(*pair), 0) or 0) \
        if pair[1] else 0
    initial = int(baseline) if baseline is not None else current
    if pair[1]:
        # IQ-4 review: the tick writes the clamped effect first and decays at
        # the relation that leaves — so the net is read the same way. Effect
        # plus today's drift read +8 at a ceiling that pays 0, and the wrong
        # drift whenever the effect crossed the ±10 band.
        stepped = max(-_d.RELATION_CLAMP, min(_d.RELATION_CLAMP, current + int(effect)))
        drift = int(_d.relation_drift_step(world, pair[0], pair[1], relation=stepped))
        net = (stepped - current) + drift
    else:
        drift, net = 0, 0
    paused = bool(mission.get("paused"))
    if paused:
        pause_reason = ("transit" if getattr(world, "talleyrand_state", "") == "IN_TRANSIT"
                        else "starved")
    else:
        pause_reason = ""
    turns_active = int(mission.get("turns_active", 0) or 0)
    status = {
        "type": mission_type,
        "type_display": MISSION_TYPE_DISPLAY.get(mission_type,
                                                 mission_type.replace("_", " ").title()),
        "target": target,
        "target_display": display_nation(target) if target else "",
        "target_ally": ally,
        "target_ally_display": display_nation(ally) if ally else "",
        "dp_per_turn": dp,
        "effect_per_turn": int(effect),
        "drift_per_turn": drift,
        "net_per_turn": int(net),
        "current_relation": current,
        "initial_relation": initial,
        "relation_delta": current - initial,
        "paused": paused,
        "pause_reason": pause_reason,
        "paused_turns": int(mission.get("paused_turns", 0) or 0),
        "turns_active": turns_active,
        "started_turn": int(mission.get("started_turn", 0) or 0),
        "dp_spent": turns_active * dp,
        "effect_text": mission_effect_text(world, mission_type),
        # No recall while he carries a proposal: the EC-Q transit gate
        # refuses it, so the Cabinet's [Recall] (hidden on "") and the rail's
        # button stay away until he is home — the note says he resumes then.
        "recall_command": ("" if pause_reason == "transit"
                           else mission_recall_command(world)),
        "relation_descriptor": _d.get_relation_descriptor(current),
    }
    if mission_type == "COURT_NATION" and _d.COURT_FAVOUR_ACTIVE:
        status["favour_now"] = _court_favour_now(world)
        status["favour_cap"] = int(_d.COURT_FAVOUR_CAP)
    kind, turns, note = project_mission_turns(world, status)
    status["remaining_kind"] = kind
    status["remaining_turns"] = int(turns)
    status["remaining_note"] = note
    return status


# ── The notice rail: ONE row per mission ──
_EVENT_BEATS = frozenset({"begun", "paused_transit", "blowback", "completed",
                          "recalled", "collapsed", "eliminated"})
_HIGH_BEATS = frozenset({"paused_starved", "blowback", "collapsed", "eliminated"})
_ENDED_BEATS = frozenset({"completed", "recalled", "collapsed", "eliminated"})


def _mission_row(notes):
    from backend.notifications import DIPLOMATIC_MISSION
    for row in getattr(notes, "_pending", []) or []:
        if row.get("type") == DIPLOMATIC_MISSION:
            return row
    return None


def _mission_message(world, beat: str, status: Optional[dict], snap: dict,
                     extra: dict) -> str:
    from backend.display_names import display_nation
    T = display_nation(snap.get("target", "")) if snap.get("target") else "the court"
    A = display_nation(snap.get("target_ally", "")) if snap.get("target_ally") else ""
    dp = int(MISSION_DP_COSTS.get(snap.get("type", ""), 1))
    if beat == "begun" and status:
        return (f"Talleyrand has gone to {T}. {status['effect_text'][:1].upper()}"
                f"{status['effect_text'][1:]}. {dp} DP a turn. "
                f"{status['remaining_note'][:1].upper()}{status['remaining_note'][1:]}.")
    if beat == "running" and status:
        note = status["remaining_note"][:1].upper() + status["remaining_note"][1:]
        if status["type"] == "UNDERMINE_ALLIANCE":
            return (f"{T} and {A} at {status['current_relation']}, "
                    f"{status['effect_per_turn']:+d} a turn from him. {note}.")
        if status["type"] == "GATHER_INTEL":
            return f"{note}."
        return (f"Relations with {T} {status['current_relation']}, net "
                f"{status['net_per_turn']:+d} a turn. {note}. {dp} DP a turn.")
    if beat == "paused_transit":
        return (f"Talleyrand has left {T} to carry your proposal. While he "
                "travels the mission costs nothing and earns nothing; it resumes "
                "when he returns.")
    if beat == "paused_starved":
        left = int(status["remaining_turns"]) if status else 0
        return (f"Talleyrand's mission to {T} is stalled: it needs {dp} DP a turn. "
                f"It collapses in {_plural(left, 'turn')} without it.")
    if beat == "blowback":
        return (f"{T} caught Talleyrand at his courting: relations "
                f"{int(extra.get('delta', 0)):+d} (now {int(extra.get('current', 0))}). "
                "The mission continues.")
    if beat == "completed":
        reason = extra.get("reason", "")
        if reason == "duration":
            return (f"Talleyrand is back from {T}: "
                    f"{_plural(int(extra.get('regions') or 0), 'province')} lie open "
                    f"to us until turn {int(extra.get('expiry') or 0)}.")
        if reason == "alliance_broken":
            return (f"The alliance between {T} and {A} has broken. "
                    "Talleyrand's mission is done.")
        end = int(extra.get("end", 0))
        return (f"Relations with {T} stand at {end:+d}. Talleyrand's mission is "
                f"done and he is home — {_plural(int(extra.get('turns', 0)), 'turn')}, "
                f"{int(extra.get('dp_spent', 0))} DP ({int(extra.get('start', 0)):+d} "
                f"to {end:+d}).")
    if beat == "recalled":
        if snap.get("type") == "UNDERMINE_ALLIANCE" and A:
            return (f"Talleyrand is recalled from {T}. {T} and {A} stand at "
                    f"{int(extra.get('end', 0)):+d} (from "
                    f"{int(extra.get('start', 0)):+d}).")
        return (f"Talleyrand is recalled from {T}. Relations keep what he won: "
                f"{int(extra.get('start', 0)):+d} to {int(extra.get('end', 0)):+d}.")
    if beat == "collapsed":
        return (f"Talleyrand's mission to {T} has collapsed: three turns without "
                f"the {dp} DP it needs.")
    if beat == "eliminated":
        return f"Talleyrand's mission to {T} has ended — {T} no longer exists."
    return ""


def restate_mission_notice(world, beat: Optional[str] = None,
                           snapshot: Optional[dict] = None,
                           extra: Optional[dict] = None) -> None:
    """The rail row for the mission — at most ONE of its type at any time.

    ``beat`` names an event (begun, paused_transit, blowback, completed,
    recalled, collapsed, eliminated): the row is RE-ISSUED — a new id, so one
    bell per change of state. With no beat (the end-of-advance seam) the
    running row is REFRESHED in place (same id, no bell) — except a resume
    after a starved pause, re-issued so its HIGH priority can fall to NORMAL —
    and a no-op when no mission is live, so an ended row survives. An event
    beat raised inside the tick (blowback) is kept for that turn.
    O(1); literal-typed; no `enabled` key (the IGR-2 lesson).
    """
    if not MISSION_RAIL_NOTICE:
        return
    notes = getattr(world, "notifications", None)
    if notes is None:
        return
    from backend.display_names import MISSION_TYPE_DISPLAY, display_nation
    from backend.notifications import (
        DIPLOMATIC_MISSION, NotificationPriority, create_notification,
    )
    extra = dict(extra or {})
    live = mission_is_live(world)
    existing = _mission_row(notes)
    if beat is None:
        if not live:
            return
        if existing and (existing.get("details") or {}).get("fresh"):
            existing["details"]["fresh"] = False     # shown for one turn
            return
        status = mission_status(world)
        prev = (existing.get("details") or {}).get("beat") if existing else None
        if status["paused"]:
            beat = ("paused_transit" if status["pause_reason"] == "transit"
                    else "paused_starved")
        else:
            beat = "running"
        reissue = (existing is None
                   or (beat == "paused_starved" and prev != "paused_starved")
                   # IQ-4 review: a blowback row too — `refresh` keeps the max
                   # priority, so a routine running row stayed HIGH for good.
                   or (beat == "running" and prev in _HIGH_BEATS))
    else:
        status = mission_status(world) if live else None
        reissue = True
    snap = dict(snapshot or (world.active_diplomatic_mission or {}))
    mission_type = str(snap.get("type", "") or "")
    target = str(snap.get("target", "") or "")
    if not target:
        return
    title = (f"Talleyrand: {MISSION_TYPE_DISPLAY.get(mission_type, mission_type)} - "
             f"{display_nation(target)}")
    details = {"target_nation": target, "mission_type": mission_type, "beat": beat,
               "fresh": bool(beat == "blowback")}
    # No Recall on the transit row: the EC-Q transit gate refuses every
    # mission order while he carries a proposal (and the wizard greys the
    # row, FA-N81). A button on the rail must do what it says, or not be
    # there — the row says he resumes when he returns.
    if beat not in _ENDED_BEATS and beat != "paused_transit" and live:
        details["action_command"] = mission_recall_command(world)
        details["action_label"] = MISSION_RECALL_LABEL
        details["action_detail"] = MISSION_RECALL_DETAIL
    priority = (NotificationPriority.HIGH if beat in _HIGH_BEATS
                else NotificationPriority.NORMAL)
    row = create_notification(
        DIPLOMATIC_MISSION, priority, title,
        _mission_message(world, beat, status, snap, extra),
        int(getattr(world, "current_turn", 0) or 0), details)
    if reissue:
        notes.dismiss_by_type(DIPLOMATIC_MISSION)
        notes.add(row)
    else:
        notes.refresh(row)


def record_mission_end(world, mission: Optional[dict], reason: str,
                       relation_end: Optional[int] = None,
                       regions_revealed: Optional[int] = None,
                       expiry: Optional[int] = None) -> None:
    """One call at every place a mission ends: the campaign-log row
    (`diplomatic_mission_ended`) and the rail's ending beat.

    ``reason`` ∈ ceiling, duration, alliance_broken, recalled, starved,
    eliminated (the last keeps its own `…_cancelled_eliminated` log row and
    only rings the rail). ``mission`` is the dict, or a snapshot taken before
    a path clears it.
    """
    if not mission:
        return
    mission_type = str(mission.get("type", "") or "")
    target = str(mission.get("target", "") or "")
    player = getattr(world, "player_nation", "France")
    turns = int(mission.get("turns_active", 0) or 0)
    dp_spent = turns * int(MISSION_DP_COSTS.get(mission_type, 1))
    ally = str(mission.get("target_ally", "") or "")
    if mission_type == "UNDERMINE_ALLIANCE" and ally and target:
        # IQ-4 review: the record is of the pair he moved, never France's own
        # standing with the target (MS-7b's class). An old save without the
        # baseline falls back to today's PAIR value, never initial_relation.
        pair_now = int(world.nation_relations.get(
            world._make_diplo_key(target, ally), 0) or 0)
        base = mission.get("initial_pair_relation")
        start = int(base) if base is not None else pair_now
        if relation_end is None:
            relation_end = pair_now
    else:
        start = int(mission.get("initial_relation") or 0)
        if relation_end is None:
            relation_end = (int(world.nation_relations.get(
                world._make_diplo_key(player, target), 0) or 0) if target else 0)
    if MISSION_LOG_ENDS and reason != "eliminated":
        entry = {
            "type": "diplomatic_mission_ended",
            "target": target,
            "mission_type": mission_type,
            "reason": reason,
            "turns_active": turns,
            "dp_spent": dp_spent,
            "relation_start": start,
            "relation_end": int(relation_end),
        }
        if regions_revealed is not None:
            entry["regions_revealed"] = int(regions_revealed)
        if expiry is not None:
            entry["expiry"] = int(expiry)
        world.log_event(entry)
    beat = {"recalled": "recalled", "replaced": "recalled", "starved": "collapsed",
            "eliminated": "eliminated"}.get(reason, "completed")
    restate_mission_notice(world, beat=beat, snapshot=mission, extra={
        "reason": reason, "turns": turns, "dp_spent": dp_spent,
        "start": start, "end": int(relation_end),
        "regions": regions_revealed, "expiry": expiry,
    })


_ROSTER_NATION_PATTERNS: Optional[list] = None


def _roster_nation_patterns() -> list:
    """(compiled word-boundary pattern, canonical key) for every shipped
    nation on BOTH rosters (legacy + 1805 Europe), matching the display form
    ("Kingdom of Italy", "Papal States", "Ottoman Empire") and the internal
    key. Longest needle first so "prussia" always wins over its embedded
    "russia". Gate-4 1805 smoke (E-1): the alias table alone covered only
    Britain/Prussia/Austria/Saxony/France, so typed AND wizard-composed
    proposals ("propose peace with Russia") were unreachable for 15 of the
    19 Europe nations in every LLM mode.
    """
    global _ROSTER_NATION_PATTERNS
    if _ROSTER_NATION_PATTERNS is None:
        import re

        from backend.display_names import display_nation
        from backend.nation_config import EUROPE_ROSTER, RUNTIME_NATIONS

        needles: Dict[str, str] = {}
        for key in (*EUROPE_ROSTER, *RUNTIME_NATIONS):
            for form in (display_nation(key), key):
                needles.setdefault(str(form).lower(), key)
        _ROSTER_NATION_PATTERNS = [
            (re.compile(r"\b" + re.escape(needle) + r"\b"), canonical)
            for needle, canonical in sorted(
                needles.items(), key=lambda kv: -len(kv[0])
            )
        ]
    return _ROSTER_NATION_PATTERNS


def _scan_rosters_for_nation(
    text_lower: str, *, exclude_france: bool
) -> Optional[str]:
    for pattern, canonical in _roster_nation_patterns():
        if exclude_france and canonical == "France":
            continue
        if pattern.search(text_lower):
            return canonical
    return None


def resolve_nation_name(text: str) -> Optional[str]:
    """Fuzzy match a nation name from text. Returns canonical name or None."""
    # NOTE: Uses substring matching which could theoretically false-positive
    # on words containing nation name substrings. Acceptable for current game
    # commands which are short and focused on diplomatic actions.
    text_lower = text.lower().strip()

    # Direct alias match (adjectives / typos / historical synonyms)
    for alias, canonical in NATION_ALIASES.items():
        if alias in text_lower:
            return canonical

    # E-1: full-roster fallback — any shipped nation's display name or key.
    return _scan_rosters_for_nation(text_lower, exclude_france=False)


def extract_nation_from_command(raw_text: str) -> Optional[str]:
    """Extract target nation from a diplomatic command string."""
    text_lower = raw_text.lower()

    # Try each known nation (and aliases)
    for alias, canonical in NATION_ALIASES.items():
        if alias in text_lower and canonical != "France":
            return canonical

    # E-1: full-roster fallback — any shipped nation's display name or key.
    return _scan_rosters_for_nation(text_lower, exclude_france=True)


def extract_proposal_type(raw_text: str) -> Optional[str]:
    """Extract proposal type from command text."""
    text_lower = raw_text.lower()
    for ptype, keywords in PROPOSAL_TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return ptype
    return None


def extract_mission_type(raw_text: str) -> Optional[str]:
    """Extract mission type from command text."""
    text_lower = raw_text.lower()

    # Check cancel first
    if any(kw in text_lower for kw in ["cancel mission", "halt mission", "stop mission",
                                        "cancel diplomatic", "abort mission"]):
        return "CANCEL"

    for mtype, keywords in MISSION_TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return mtype
    return None


def classify_diplomatic_intent(parsed_command: Dict, world) -> str:
    """Classify what kind of diplomatic dialogue to generate.

    Returns one of:
        "not_diplomatic" — no diplomatic keywords
        "unknown_nation" — nation mentioned but not recognized
        "feasibility" — asking about possibility
        "advisory" — general question (stub for Session 4)
        "mission" — start/cancel a diplomatic mission
        "proposal_execute" — SPECIFIC: has proposal type + clauses
        "proposal_confirm" — MEDIUM: has proposal type, needs confirmation
        "proposal_options" — VAGUE: needs to pick proposal type
    """
    raw_text = parsed_command.get("raw_text", "")
    target_nation = parsed_command.get("target_nation")
    has_proposal_type = parsed_command.get("proposal_type") is not None
    has_clauses = len(parsed_command.get("clauses", [])) > 0
    is_question = parsed_command.get("is_question", False)
    has_diplomatic_keywords = parsed_command.get("has_diplomatic_keywords", True)
    mission_type = parsed_command.get("mission_type")

    if not has_diplomatic_keywords and not is_question and not mission_type:
        return "not_diplomatic"

    # Check for unknown nation (mentioned but not recognized)
    if target_nation and target_nation not in get_known_nations(world):
        return "unknown_nation"

    # Mission commands
    if mission_type:
        return "mission"

    # Question classification
    if is_question:
        text_lower = raw_text.lower()
        if any(kw in text_lower for kw in FEASIBILITY_KEYWORDS):
            return "feasibility"
        return "advisory"

    # Specificity classification
    if has_clauses:
        return "proposal_execute"
    elif has_proposal_type:
        return "proposal_confirm"
    else:
        return "proposal_options"


def get_game_bucket(target_nation: str, world) -> str:
    """Determine the game state bucket for template selection.

    Returns one of:
        At war: "winning_comfortably", "winning_slightly", "stalemate",
                "losing_slightly", "losing_badly"
        At peace: "friendly", "neutral", "hostile"
    """
    player_nation = get_player_nation(world)
    state = world.get_diplomatic_state(player_nation, target_nation)
    if state == "WAR":
        from backend.game_logic.diplomacy import get_war_score_for
        war_score = get_war_score_for(world, player_nation, target_nation)

        if war_score > 30:
            return "winning_comfortably"
        if war_score > 0:
            return "winning_slightly"
        if war_score > -10:
            return "stalemate"
        if war_score > -30:
            return "losing_slightly"
        return "losing_badly"
    else:
        relation = world.nation_relations.get(world._make_diplo_key(player_nation, target_nation), 0)
        if relation > 20:
            return "friendly"
        if relation > -20:
            return "neutral"
        return "hostile"


def generate_dialogue(intent_type: str, parsed_command: Dict, world) -> Dict:
    """Generate a pending_diplomatic_dialogue dict based on intent classification.

    Returns a dict suitable for storage as world.pending_diplomatic_dialogue.
    """
    from backend.game_logic.diplomatic_templates import (
        get_template, resolve_template_text, generate_suggested_terms,
    )

    target_nation = parsed_command.get("target_nation")
    proposal_type = parsed_command.get("proposal_type")
    player_nation = get_player_nation(world)
    # Determine game bucket
    bucket = get_game_bucket(target_nation, world) if target_nation else "neutral"

    # Determine diplomatic state for template matching
    diplo_state = "WAR" if target_nation and world.get_diplomatic_state(player_nation, target_nation) == "WAR" else "PEACE"

    # Get template
    template = get_template(intent_type, diplo_state, bucket, proposal_type)

    # Resolve slots in template text (including {proposal_type})
    talleyrand_text = resolve_template_text(
        template.get("text", ""), world, target_nation)
    if proposal_type and "{proposal_type}" in talleyrand_text:
        talleyrand_text = talleyrand_text.replace("{proposal_type}", _display_proposal_type(proposal_type))

    # Build options with resolved text
    options = []
    for opt in template.get("options", []):
        resolved_opt = {
            "label": opt["label"],
            "description": resolve_template_text(
                opt.get("description", ""), world, target_nation),
            "action": opt["action"],
        }
        if "terms" in opt:
            resolved_opt["terms"] = opt["terms"]
        elif opt["action"] == "execute_proposal" and target_nation:
            # Generate terms for execute options
            ptype = opt.get("proposal_type", proposal_type)
            if ptype:
                resolved_opt["terms"] = generate_suggested_terms(
                    target_nation, ptype, world)
                resolved_opt["terms"]["proposal_type"] = ptype
        options.append(resolved_opt)

    # Context-aware option descriptions for war proposals
    if target_nation and intent_type == "proposal_confirm":
        from backend.game_logic.diplomacy import get_war_score_for
        player_war_score = get_war_score_for(world, player_nation, target_nation)
        for opt in options:
            if opt["action"] == "modify_harsh" and player_war_score < -10:
                opt["description"] = "Demand more — risky given our weak position."
            elif opt["action"] == "modify_generous" and player_war_score > 20:
                opt["description"] = "Offer concessions — unnecessary given our strong position."

    # Build context snapshot
    context = {}
    if target_nation:
        from backend.game_logic.diplomacy import get_war_score_for
        diplo_key = world._make_diplo_key(player_nation, target_nation)
        context = {
            "war_score": int(get_war_score_for(world, player_nation, target_nation)),
            "relation": int(world.nation_relations.get(diplo_key, 0)),
            "threat": int(getattr(world, 'threat_level', 0)),
            "current_state": world.get_diplomatic_state(player_nation, target_nation),
        }
        # PL-3: Populate diplomat info so incoming_proposal popup shows real name
        diplomats = getattr(world, 'diplomats', {})
        diplomat = diplomats.get(target_nation)
        if diplomat:
            context["diplomat_name"] = diplomat.name
            context["diplomat_personality"] = getattr(diplomat, 'personality', 'unknown')
    if proposal_type:
        context["proposal_type"] = proposal_type

    dialogue = {
        "type": intent_type,
        "target_nation": target_nation or "",
        "talleyrand_text": talleyrand_text,
        "options": options,
        "context": context,
        "turn_created": int(world.current_turn),
        "blocking": False,
    }

    # ═══════ PROPOSAL TERMS ENRICHMENT ═══════
    # For proposal_confirm/proposal_execute, compute and attach terms summary,
    # acceptance estimate, harshness, and DP cost so the frontend popup can
    # display them to the player.
    if intent_type in ("proposal_execute", "proposal_confirm") and target_nation and proposal_type:
        dialogue = _enrich_proposal_summary(dialogue, target_nation, proposal_type, world)

    # ═══════ SESSION 6: Pre-proposal objection merge ═══════
    # When sending a proposal, evaluate Talleyrand's concern and merge
    # into the dialogue (not a separate popup per §10a).
    if intent_type in ("proposal_execute", "proposal_confirm") and target_nation:
        dialogue = _merge_pre_proposal_objection(dialogue, parsed_command, world)

    return dialogue


def _enrich_ultimatum_dialogue(dialogue: Dict, target_nation: str, world) -> Dict:
    """Add acceptance estimate and consequence preview to ultimatum dialogue (PL-14 §5).

    Separate from _enrich_proposal_summary — ultimatums have flat DP cost,
    no state transition, and always-coercive harshness.
    """
    from backend.game_logic.diplomacy import calculate_acceptance

    terms = dialogue.get("terms", {})
    demands = terms.get("demands", [])

    # Build acceptance proposal struct
    proposer = get_player_nation(world)
    proposal = {
        "type": "ultimatum_demand",
        "proposer_nation": proposer,
        "target_nation": target_nation,
        "sweeteners": [],
        "demands": demands,
        "clauses": [],
    }

    # Calculate acceptance
    try:
        result = calculate_acceptance(proposal, world)
        # AI-2c review fix (shown = applied): the DECISION seam adds the
        # statecraft coercion answer (Austria hardens −15, Prussia folds
        # +10, Britain's derived subsidy wall −40...) — the estimate the
        # player stakes relations and threat on must carry the same
        # number, or the preview lies by up to 40 points.
        from backend.game_logic.statecraft import coercion_acceptance_delta
        coercion_delta = int(coercion_acceptance_delta(world, target_nation))
        score = int(result.get("score", 0)) + coercion_delta
        dialogue["acceptance_estimate"] = score
        dialogue["acceptance_outcome"] = ("ACCEPT" if score >= 50
                                          else "REJECT")
        dialogue["coercion_delta"] = coercion_delta
        # Find key obstacle for hint
        components = result.get("components", {})
        negative_components = {k: v for k, v in components.items() if isinstance(v, (int, float)) and v < 0}
        if negative_components:
            worst = min(negative_components, key=negative_components.get)
            from backend.display_names import FEEDBACK_STRINGS
            fb = FEEDBACK_STRINGS.get(worst, {})
            dialogue["acceptance_hint"] = fb.get("negative", worst.replace("_", " "))
        else:
            dialogue["acceptance_hint"] = ""
        dialogue["acceptance_components"] = components
    except Exception:
        dialogue["acceptance_estimate"] = 20
        dialogue["acceptance_outcome"] = "REJECT"
        dialogue["acceptance_hint"] = "Unable to estimate"

    # Flat DP cost (no state transition)
    dialogue["dp_cost"] = 2
    dialogue["harshness_label"] = "Coercive"

    # Format demands for display
    demand_lines = []
    for d in demands:
        dtype = d.get("type", "")
        value = d.get("value", 0)
        if dtype == "gold_per_turn":
            demand_lines.append(f"  - {int(value)} gold per turn")
        elif dtype == "gold_lump":
            demand_lines.append(f"  - {int(value)} gold (immediate)")
        elif dtype == "territory_cede":
            region_names = d.get("regions", [])
            if region_names:
                demand_lines.append(f"  - Cede {', '.join(region_names)}")
            else:
                demand_lines.append(f"  - Cede {int(value)} region(s)")
        elif dtype in ("manpower_infantry", "manpower_cavalry", "manpower_artillery"):
            unit_label = dtype.replace("manpower_", "")
            demand_lines.append(f"  - {int(value)} {unit_label}")
        elif dtype == "manpower":
            demand_lines.append(f"  - {int(value)} infantry")
    dialogue["demands_display"] = demand_lines

    # PL-19 §D: Diplomatic cost preview
    # PL-20 §E: Talleyrand territory warnings
    import math
    from backend.game_logic.diplomacy import analyze_territory_demands, DEMAND_VALUES as _DV

    t_analysis = analyze_territory_demands(demands, target_nation, world)

    # Compute preview penalty (same logic as executor Step 2)
    territory_demand_penalty = 0.0
    for r in t_analysis["demanded_regions"]:
        weight = t_analysis["region_income_weights"].get(r, 1.0)
        region_cost = -5 * weight
        if r in t_analysis["capital_regions"]:
            region_cost *= 2
        territory_demand_penalty += region_cost

    if t_analysis["is_annex"]:
        territory_demand_penalty *= 2.5
    elif t_analysis["is_rump"]:
        territory_demand_penalty *= 2.0
    elif t_analysis["demanded_count"] >= 4:
        territory_demand_penalty *= 1.5
    elif t_analysis["demanded_count"] >= 2:
        territory_demand_penalty *= 1.2

    other_demand_penalty = 0.0
    for d in demands:
        dtype = d.get("type", "")
        if dtype in ("territory_cede", "territory"):
            continue
        dvalue = d.get("value", 0)
        rate = _DV.get(dtype, 0)
        if isinstance(rate, (int, float)) and abs(rate) < 1:
            other_demand_penalty += (dvalue * rate) if dvalue is not None else 0
        else:
            other_demand_penalty += rate * dvalue if dvalue is not None else rate

    preview_penalty = max(-60, math.floor(-10 + territory_demand_penalty + other_demand_penalty))
    preview_penalty = min(preview_penalty, -10)

    dialogue["diplomatic_cost"] = int(preview_penalty)
    # Severity labels
    abs_pen = abs(preview_penalty)
    if abs_pen <= 15:
        dialogue["diplomatic_cost_label"] = "mild"
    elif abs_pen <= 25:
        dialogue["diplomatic_cost_label"] = "moderate"
    elif abs_pen <= 40:
        dialogue["diplomatic_cost_label"] = "severe"
    else:
        dialogue["diplomatic_cost_label"] = "extreme"

    # Talleyrand territory warnings
    warning = ""
    if t_analysis["is_annex"]:
        warning = (f"Sire, demanding all of {target_nation}'s territory would erase them from the map entirely. "
                   "Every nation in Europe will view this as an existential threat. "
                   "The acceptance chance is near zero, and the diplomatic cost would be catastrophic.")
    elif t_analysis["is_rump"]:
        warning = (f"Reducing {target_nation} to their capital alone would make them desperate — "
                   "and their allies furious. Expect heavy diplomatic consequences and a near-certain rejection.")
    elif t_analysis["demanded_count"] >= 4:
        warning = (f"Demanding {t_analysis['demanded_count']} regions is an extraordinary claim, Sire. "
                   "Even after a decisive victory, such vast territorial concessions are rarely accepted. "
                   "All of Europe will take notice.")
    elif t_analysis["demanded_count"] >= 2:
        warning = "A substantial territorial demand. The diplomatic cost will be significant."
    dialogue["talleyrand_territory_warning"] = warning

    return dialogue


# FA-D17 (slice 17, Phase 2) flip lever: the alliance-paradox block names the
# armistice route and the wizard's Propose Peace row carries the paradox
# reason instead of staying green. False = the prior copy and a green row.
THE_PARADOX_BLOCK_NAMES_THE_TRUCE = True
# FA-D7 (slice 17, Phase 2) flip lever: the bilateral peace mount reads the
# desk first — a settlement offer covering the target's war greys the Send
# arm with the request-terms route's own sentence. False = the prior mount
# (drafted, estimated and charged while the offer sat in the mailbox).
THE_DESK_IS_READ_BEFORE_THE_DRAFT = True


def _settlement_offer_on_the_desk(world, player: str, target: str) -> str:
    """FA-D7: the desk sentence when a settlement offer covering `target`'s
    war is pending or promoted — the request-terms route's own predicates
    and copy, never a copy of them. '' when the desk is clear."""
    from backend.game_logic.ai_diplomacy import (
        _find_war_instance_for_pair, _settlement_offer_already_pending,
        _settlement_offer_already_promoted)
    war = _find_war_instance_for_pair(world, player, target)
    war_id = str((war or {}).get("war_id") or "")
    if not war_id:
        return ""
    pending = getattr(world, "pending_settlement_dialogues", None) or []
    if (_settlement_offer_already_pending(pending, war_id=war_id)
            or _settlement_offer_already_promoted(world, war_id=war_id)):
        from backend.display_names import SETTLEMENT_DISABLED_REASON_DISPLAY
        return str(SETTLEMENT_DISABLED_REASON_DISPLAY.get(
            "offer_already_pending",
            "Their terms are already on the desk, Sire — answer the offer in the mailbox."))
    return ""


def _enrich_proposal_summary(dialogue: Dict, target_nation: str, proposal_type: str, world) -> Dict:
    """Add proposal terms summary, acceptance estimate, harshness, and DP cost to dialogue.

    These fields let the frontend popup display the mechanical content of the
    proposal alongside Talleyrand's thematic commentary.
    """
    from backend.game_logic.diplomacy import (
        build_war_context_snapshot,
        build_proposal_commitment_warnings,
        calculate_acceptance,
        get_dp_cost,
        get_transition_dp_cost,
    )
    from backend.game_logic.diplomatic_templates import generate_suggested_terms, calculate_treaty_harshness

    # Find terms from the first execute_proposal option, or generate fresh
    player_nation = get_player_nation(world)
    terms = None
    for opt in dialogue.get("options", []):
        if opt.get("action") == "execute_proposal" and opt.get("terms"):
            terms = opt["terms"]
            break
    if not terms:
        terms = generate_suggested_terms(target_nation, proposal_type, world)
        terms["proposal_type"] = proposal_type

    # PL-13-B: Always ensure both keys are present (covers dialogue option round-trip)
    if "proposal_type" not in terms:
        terms["proposal_type"] = terms.get("type", proposal_type)
    if "type" not in terms:
        terms["type"] = terms.get("proposal_type", proposal_type)

    dialogue["talleyrand_commentary"] = terms.get("talleyrand_commentary", "")

    # Build human-readable clause descriptions
    dialogue["proposal_terms_summary"] = _format_terms_for_display(terms, proposal_type, target_nation)

    war_bargain_clauses = [
        clause for clause in (
            list(terms.get("sweeteners", []))
            + list(terms.get("demands", []))
            + list(terms.get("clauses", []))
        )
        if isinstance(clause, dict) and clause.get("type") == "war_bargain"
    ]
    if war_bargain_clauses:
        try:
            from backend.game_logic.diplomacy import build_bargain_review
            review = build_bargain_review(
                world,
                war_bargain_clauses[0],
                {
                    "type": terms.get("type", proposal_type),
                    "proposer_nation": player_nation,
                    "target_nation": target_nation,
                    "sweeteners": terms.get("sweeteners", []),
                    "demands": terms.get("demands", []),
                    "clauses": terms.get("clauses", []),
                },
            )
            dialogue["bargain_review"] = review
            dialogue.setdefault("proposal_terms_summary", []).append(
                "Bargain forecast: "
                + str(review.get("war_entry_forecast_display", review.get("war_entry_forecast_band", "")))
            )
            if review.get("is_decisive"):
                dialogue["proposal_terms_summary"].append("This bargain is currently decisive for ally entry.")
            for warning in review.get("contradiction_warnings", []):
                dialogue.setdefault("warnings", []).append({
                    "severity": "high",
                    "text": str(warning),
                })
        except Exception:
            dialogue["bargain_review"] = {"error": "Unable to build bargain review"}

    # BPH-A: Attach annotated terms with ownership fields for Godot rendering
    from backend.game_logic.diplomatic_templates import annotate_peace_terms
    dialogue["annotated_terms"] = annotate_peace_terms(terms, player_nation, target_nation)

    # ES-7 second pass (§0.6.8 item 3): a bilateral sweetener ceding a
    # province that sustains a PLAYER marshal's estate warns on BOTH display
    # paths (annotated section + plain summary fallback) before the
    # proposal is sent.
    from backend.game_logic.dotation import estate_cession_warning
    from backend.game_logic.settlement_scoring import cession_shaped_regions
    _warned_regions = set()
    # NA-6c's shared extractor, which this loop never got: it handles the
    # singular `region`, the plural `regions`, AND a carve's `provinces`.
    # IGR-D adds the DEMANDS pass, scoped to `create_client` — a carve is
    # direction-wise a demand, but its soil is already the player's (the
    # eligibility predicate requires it), so it strips an estate exactly as
    # a cession does. The scope matters: a `territory_cede` demand ACQUIRES
    # land, and warning on it would tell the player that taking a province
    # strips his marshal's estate.
    _estate_scan = (
        list(terms.get("sweeteners", []) or [])
        + list(terms.get("clauses", []) or [])
        + [d for d in (terms.get("demands", []) or [])
           if isinstance(d, dict) and d.get("type") == "create_client"]
    )
    for _clause in _estate_scan:
        if not isinstance(_clause, dict):
            continue
        for _region_name in cession_shaped_regions(_clause):
            _region_name = str(_region_name)
            if _region_name in _warned_regions:
                continue
            _warned_regions.add(_region_name)
            _estate_text = estate_cession_warning(world, _region_name)
            if _estate_text:
                dialogue.setdefault("proposal_terms_summary", []).append(
                    "WARNING: " + _estate_text)
                dialogue.setdefault("annotated_terms", []).append({
                    "type": "estate_warning",
                    "term_direction": "concession",
                    "display_label": "WARNING: " + _estate_text,
                })

    peace_proposal_types = {"peace", "armistice", "armistice_losing", "armistice_winning"}
    if proposal_type in peace_proposal_types or terms.get("type") in peace_proposal_types:
        snapshot_type = terms.get("type", proposal_type)
        dialogue["war_context_snapshot"] = build_war_context_snapshot(
            world,
            player_nation,
            target_nation,
            snapshot_type,
            terms=terms,
        )

    # Harshness — normalize string clauses to dicts for calculate_treaty_harshness
    harshness_terms = dict(terms)
    harshness_terms["clauses"] = [
        c if isinstance(c, dict) else {"type": c}
        for c in terms.get("clauses", [])
    ]
    harshness = calculate_treaty_harshness(harshness_terms)
    dialogue["harshness"] = round(harshness, 2)
    if harshness < 0.15:
        dialogue["harshness_label"] = "Low"
    elif harshness < 0.35:
        dialogue["harshness_label"] = "Moderate"
    elif harshness < 0.6:
        dialogue["harshness_label"] = "High"
    else:
        dialogue["harshness_label"] = "Very High"

    # Acceptance estimate
    proposal_for_calc = {
        "type": terms.get("type", proposal_type),
        "proposer_nation": player_nation,
        "target_nation": target_nation,
        "sweeteners": terms.get("sweeteners", []),
        "demands": terms.get("demands", []),
        "clauses": terms.get("clauses", []),
    }
    try:
        result = calculate_acceptance(proposal_for_calc, world)
        score = int(result["score"])
        dialogue["acceptance_estimate"] = max(0, min(100, score))
        dialogue["acceptance_outcome"] = result.get("outcome", "Unknown")

        # G4F-13: the COUNTER band only promises a counter the AI can
        # actually CONSTRUCT (desire table or affordable gold bridge).
        # Dry-run the real generator so the preview verdict copy and the
        # in-transit resolution can never disagree about whether a counter
        # is coming.
        if dialogue["acceptance_outcome"] == "COUNTER_OFFER":
            from backend.game_logic.ai_diplomacy import generate_counter_offer
            counter_ok = generate_counter_offer(
                proposal_for_calc, world, dry_run=True
            ) is not None
            dialogue["counter_constructible"] = counter_ok
            dialogue["acceptance_outcome_display"] = (
                "COUNTER expected"
                if counter_ok
                else "REJECT likely — no workable counter"
            )

        # Extract key obstacle from components for player hint
        from backend.display_names import FEEDBACK_STRINGS
        components = result.get("components", {})
        worst_key, worst_val = "", 0
        for comp_key, comp_val in components.items():
            if comp_val < worst_val:
                worst_key = comp_key
                worst_val = comp_val
        if worst_key:
            hint_phrase = FEEDBACK_STRINGS.get(worst_key, {}).get("negative", "")
            if hint_phrase:
                dialogue["acceptance_hint"] = f"Key obstacle: {hint_phrase}"
            else:
                dialogue["acceptance_hint"] = ""
        else:
            dialogue["acceptance_hint"] = ""

        # PL-9 Part A: Warn player when acceptance is borderline (50-75%)
        if 50 <= score <= 75:
            dialogue["acceptance_warning"] = (
                "This estimate reflects current conditions, Sire. Much may change "
                "during my journey — a battle lost, a relation soured. I would counsel "
                "a wider margin if you wish certainty."
            )
        else:
            dialogue["acceptance_warning"] = ""
    except Exception:
        dialogue["acceptance_estimate"] = -1
        dialogue["acceptance_outcome"] = "Unable to estimate"
        dialogue["acceptance_hint"] = ""
        dialogue["acceptance_warning"] = ""

    # DP cost
    _state_map = {
        "peace": "PEACE", "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
        "non_aggression": "NON_AGGRESSION", "open_borders": "OPEN_BORDERS", "armistice": "ARMISTICE",
        "vassalage": "VASSAL",
    }
    # G4F-13: surface the ratify gate at preview time. A proposal can clear
    # the acceptance formula and still be vetoed by the relation
    # requirement at ratification; the old preview promised outcomes the
    # treaty gate would silently refuse.
    #
    # IGR-X3: PEACE no longer has a requirement, so this block now speaks only
    # for the friendship ladder (open borders / non-aggression / the
    # alliances), where consent genuinely is about goodwill. The peace-only
    # armistice counsel that used to hang off it is GONE, and not merely
    # because it became unreachable: it was FALSE. It advised the player that
    # waiting out a truce would soften the other court, while
    # `_process_relation_decay` skipped ARMISTICE outright — so the waiting
    # softened nothing and the war resumed unchanged. A truce now really does
    # thaw (`ARMISTICE_THAW_PER_TURN`), which is the honest way to make a
    # promise true rather than rewording it.
    from backend.game_logic.diplomacy import STATE_RELATION_REQUIREMENTS
    _gate_state = _state_map.get(proposal_type, "")
    _gate_req = STATE_RELATION_REQUIREMENTS.get(_gate_state)
    if _gate_req is not None:
        _gate_key = world._make_diplo_key(player_nation, target_nation)
        _gate_relation = int(world.nation_relations.get(_gate_key, 0))
        if _gate_relation < _gate_req:
            dialogue["ratification_gate_warning"] = (
                f"Their court will not ratify {_gate_state.replace('_', ' ').title()} "
                f"while relations stand at {_gate_relation} (it requires {_gate_req})."
            )

    current_diplo = world.get_diplomatic_state(get_player_nation(world), target_nation)
    target_diplo = _state_map.get(proposal_type, "PEACE")
    jump_cost = get_transition_dp_cost(current_diplo, target_diplo)
    dp_action = f"propose_{proposal_type}"
    talleyrand = get_player_diplomat(world)
    skill = talleyrand.skill if talleyrand else 5
    dialogue["dp_cost"] = int(get_dp_cost(dp_action, skill, transition_base=jump_cost))

    # Display name
    dialogue["proposal_type_display"] = _display_proposal_type(proposal_type)
    dialogue["speaker_attribution"] = "talleyrand"

    warnings = build_proposal_commitment_warnings(
        world,
        proposer_nation=player_nation,
        target_nation=target_nation,
        proposal_type=proposal_type,
    )
    if warnings:
        dialogue["warnings"] = list(dialogue.get("warnings", [])) + warnings

    # Gate-4 1805 smoke (E-2, honesty half): the BPH-C §10.1 alliance-paradox
    # HARD_STOP only fired at Send — the player walked the whole flow (the
    # estimate even promising "COUNTER expected") before learning the
    # proposal cannot be delivered at all. Surface the block at MOUNT, in
    # the same G4F-13 honest-preview pattern, and name the routes that DO
    # work on a shared coalition war. Slice G1 / D-G1-1 (user-approved):
    # the paradox gates bilateral PEACE only — armistice variants are
    # exempt at the send gate, so the mount warning matches.
    if proposal_type == "peace":
        from backend.game_logic.diplomacy import get_peace_commitment_conflicts
        _conflicts = get_peace_commitment_conflicts(
            world, player_nation, target_nation,
            (dialogue.get("proposal_terms") or {}).get("clauses", [])
            if isinstance(dialogue.get("proposal_terms"), dict) else [],
        )
        _hard = [c for c in _conflicts if c.get("severity") == "HARD_STOP"]
        if _hard:
            _ally = str(_hard[0].get("affected_entity") or "an ally")
            if THE_PARADOX_BLOCK_NAMES_THE_TRUCE:
                # FA-D17 (slice 17, Phase 2): the old sentence named a route
                # France cannot execute ("resolve X's war first") and omitted
                # the one the executor exempts — the armistice carries no
                # contradiction, and its expiry makes the peace.
                block_text = (
                    f"I cannot deliver this, Sire — {_hard[0].get('display', '')} "
                    f"Propose an armistice instead (a truce carries no contradiction, "
                    f"and its expiry makes the peace), or settle the war jointly at the "
                    f"settlement table."
                )
            else:
                block_text = (
                    f"I cannot deliver this, Sire — {_hard[0].get('display', '')} "
                    f"Settle the war jointly at the settlement table, or resolve "
                    f"{_ally}'s war first."
                )
            dialogue["commitment_block_warning"] = block_text
            dialogue["warnings"] = list(dialogue.get("warnings", [])) + [
                {"severity": "high", "text": block_text}
            ]
            # WIN-1: warning the player was only half the job — "Send as
            # suggested" stayed ENABLED and FIRST, the send was refused at
            # execution, and the refusal re-attached the same dialogue, so
            # the option could be pressed forever and never succeed
            # (measured 6/6 in probe; organically against two courts).
            # Honest availability: the arm that cannot work arrives
            # DISABLED and says why, exactly as the vassal-wizard gate rows
            # and the NV-6 naval chips do. The other arms — modify, adjust,
            # Reconsider — stay live, so the player is never dead-ended.
            _blocked_actions = {"execute_proposal"}
            _options = []
            for _opt in dialogue.get("options") or []:
                if (isinstance(_opt, dict)
                        and _opt.get("action") in _blocked_actions):
                    _opt = dict(_opt)
                    _opt["enabled"] = False
                    _opt["available"] = False
                    _opt["unavailable_reason"] = block_text
                    _opt["description"] = block_text
                _options.append(_opt)
            if _options:
                dialogue["options"] = _options

    # FA-D7 (slice 17, Phase 2): `propose peace with X` drafted, estimated and
    # charged 3 DP while the coalition's settlement offer covering X sat on
    # the desk — and `request terms` refused for exactly that reason. The
    # mount reads the desk first (the request-terms route's own predicates)
    # and the Send arm arrives DISABLED with the same sentence.
    if proposal_type == "peace" and THE_DESK_IS_READ_BEFORE_THE_DRAFT:
        _desk = _settlement_offer_on_the_desk(world, player_nation, target_nation)
        if _desk:
            dialogue["desk_block_warning"] = _desk
            dialogue["warnings"] = list(dialogue.get("warnings", [])) + [
                {"severity": "high", "text": _desk}
            ]
            _desk_options = []
            for _opt in dialogue.get("options") or []:
                if isinstance(_opt, dict) and _opt.get("action") == "execute_proposal":
                    _opt = dict(_opt)
                    _opt["enabled"] = False
                    _opt["available"] = False
                    _opt["unavailable_reason"] = _desk
                    _opt["description"] = _desk
                _desk_options.append(_opt)
            if _desk_options:
                dialogue["options"] = _desk_options

    return dialogue


def _format_terms_for_display(terms: Dict, proposal_type: str, target_nation: str) -> list:
    """Convert a terms dict into a list of human-readable clause strings."""
    lines = _shared_format_terms_for_display(terms, proposal_type, target_nation)

    # If no extra terms beyond the base
    if len(lines) == 1 and proposal_type in ("non_aggression", "open_borders"):
        lines.append("No additional terms")

    return lines


def _merge_pre_proposal_objection(dialogue: Dict, parsed_command: Dict, world) -> Dict:
    """Merge Talleyrand's pre-proposal objection into the dialogue flow.

    V2a pattern: MILD = flavor text (no blocking), MODERATE/STRONG = inline
    options with "Send anyway" / "Modify terms" / "Trust Talleyrand".

    Args:
        dialogue: The base dialogue dict
        parsed_command: Original parsed command
        world: WorldState

    Returns:
        Modified dialogue dict with objection merged
    """
    from backend.commands.diplomatic_defiance import (
        evaluate_pre_proposal_objection, get_objection_text,
    )

    # G4F-6 (Gate-4 smoke): evaluate the objection against the SAME terms the
    # popup displays. `_enrich_proposal_summary` runs before this merge and
    # resolves the displayed package onto the execute_proposal option (the
    # suggested terms when the player named none) — the old parsed-clause
    # stub was EMPTY on every suggested-terms flow, so harshness read 0.0
    # and Talleyrand called a PUNITIVE preview "such generous terms... it
    # rewards their failure" in the live smoke.
    resolved_terms: Dict = {}
    for opt in dialogue.get("options", []):
        if opt.get("action") == "execute_proposal" and opt.get("terms"):
            resolved_terms = opt["terms"]
            break
    demands = list(resolved_terms.get("demands") or [])
    sweeteners = list(resolved_terms.get("sweeteners") or [])
    if not demands and not sweeteners:
        parsed_clauses = list(parsed_command.get("clauses") or [])
        if parsed_clauses:
            demands = parsed_clauses
        else:
            # Mirror _enrich_proposal_summary's fallback so the objection
            # always judges what the player is about to see.
            from backend.game_logic.diplomatic_templates import (
                generate_suggested_terms,
            )
            suggested = generate_suggested_terms(
                parsed_command.get("target_nation", ""),
                parsed_command.get("proposal_type", "peace"),
                world,
            )
            demands = list(suggested.get("demands") or [])
            sweeteners = list(suggested.get("sweeteners") or [])
    proposal = {
        "type": parsed_command.get("proposal_type", "peace"),
        "target_nation": parsed_command.get("target_nation", ""),
        "demands": demands,
        "sweeteners": sweeteners,
    }

    # Get Talleyrand
    talleyrand = get_player_diplomat(world)
    if not talleyrand:
        return dialogue

    concern = evaluate_pre_proposal_objection(proposal, talleyrand, world)

    from backend.commands.objection_v2 import ConcernLevel

    if concern == ConcernLevel.NONE:
        return dialogue  # No objection

    objection_text = get_objection_text(concern, proposal, talleyrand)

    if concern == ConcernLevel.MILD:
        # MILD: flavor text prepended, no blocking, no extra options
        dialogue["talleyrand_text"] = objection_text + "\n\n" + dialogue["talleyrand_text"]
        dialogue["objection_level"] = "mild"
    else:
        # MODERATE/STRONG: inline options merged into dialogue
        dialogue["talleyrand_text"] = objection_text
        dialogue["objection_level"] = "strong" if concern >= ConcernLevel.STRONG else "moderate"
        dialogue["blocking"] = False  # Still not a popup — inline in conversation

        # Set diplomatic_objection_popup for Godot (Session 8C)
        concern_label = "STRONG" if concern >= ConcernLevel.STRONG else "MODERATE"
        defiance_risk = "High" if concern >= ConcernLevel.STRONG else "Medium"
        target_nation_obj = parsed_command.get("target_nation", "")
        proposal_type_obj = parsed_command.get("proposal_type", "peace")
        from backend.display_names import proposal_display_name
        # §11.8 stage 3 — the objection modal names the nation as it stands today.
        from backend.game_logic.formations import formed_display_name
        proposal_summary = (
            f"{proposal_display_name(proposal.get('type', 'unknown'))}"
            f" with {formed_display_name(world, proposal.get('target_nation', 'unknown'))}"
        )

        # Enrich with proposal terms so objection popup can display them
        terms_for_display = []
        acceptance_estimate = -1
        acceptance_outcome = ""
        for opt in dialogue.get("options", []):
            if opt.get("action") == "execute_proposal" and opt.get("terms"):
                terms_for_display = _format_terms_for_display(
                    opt["terms"], proposal_type_obj, target_nation_obj)
                break
        if target_nation_obj:
            from backend.game_logic.diplomacy import calculate_acceptance
            from backend.game_logic.diplomatic_templates import generate_suggested_terms as _gen_terms
            player_nation = get_player_nation(world)
            calc_terms = None
            for opt in dialogue.get("options", []):
                if opt.get("action") == "execute_proposal" and opt.get("terms"):
                    calc_terms = opt["terms"]
                    break
            if not calc_terms:
                calc_terms = _gen_terms(target_nation_obj, proposal_type_obj, world)
            calc_proposal = {
                "type": proposal_type_obj,
                "proposer_nation": player_nation,
                "target_nation": target_nation_obj,
                "sweeteners": calc_terms.get("sweeteners", []),
                "demands": calc_terms.get("demands", []),
                "clauses": calc_terms.get("clauses", []),
            }
            try:
                acc_result = calculate_acceptance(calc_proposal, world)
                acceptance_estimate = int(acc_result["score"])
                acceptance_estimate = max(0, min(100, acceptance_estimate))
                acceptance_outcome = acc_result.get("outcome", "Unknown")
            except Exception:
                acceptance_estimate = -1
                acceptance_outcome = "Unable to estimate"

        world.diplomatic_objection_popup = {
            "concern_level": concern_label,
            "objection_text": objection_text,
            "defiance_risk": defiance_risk,
            "proposal_summary": proposal_summary,
            "proposal_terms": terms_for_display,
            "acceptance_estimate": int(acceptance_estimate),
            "acceptance_outcome": acceptance_outcome,
            "target_nation": target_nation_obj,
        }

        # R42: Preserve original terms for send_override/send_suggested handlers
        # Find original proposal terms from the pre-objection options
        target_nation = parsed_command.get("target_nation", "")
        original_terms = None
        for opt in dialogue.get("options", []):
            if opt.get("action") == "execute_proposal" and opt.get("terms"):
                original_terms = opt["terms"]
                break

        # Generate Talleyrand's suggested (softer) terms
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        proposal_type = parsed_command.get("proposal_type", "peace")
        suggested_terms = generate_suggested_terms(target_nation, proposal_type, world) if target_nation else {}
        if suggested_terms:
            suggested_terms["proposal_type"] = proposal_type

        # Store in context for executor handlers
        dialogue["context"]["original_proposal"] = original_terms or {"proposal_type": proposal_type}
        dialogue["context"]["suggested_terms"] = suggested_terms

        # Replace options with objection-aware choices
        dialogue["options"] = [
            {
                "label": "Send my terms as ordered",
                "description": "Insist on your original proposal. Defiance may trigger during transit.",
                "action": "send_override",
                "terms": original_terms or {"proposal_type": proposal_type},
            },
            {
                "label": "Use Talleyrand's suggestion",
                "description": "Trust his diplomatic judgment.",
                "action": "send_suggested",
                "terms": suggested_terms,
            },
            {
                "label": "Modify terms",
                "description": "Reconsider the proposal.",
                "action": "reconsider",
            },
        ]

    return dialogue


def generate_feasibility_dialogue(parsed_command: Dict, world) -> Dict:
    """Generate a feasibility assessment dialogue (0 DP cost)."""
    from backend.game_logic.diplomacy import calculate_acceptance, get_dp_cost, get_war_score_for

    target_nation = parsed_command.get("target_nation")
    proposal_type = parsed_command.get("proposal_type", "peace")
    player_nation = get_player_nation(world)

    if not target_nation:
        return {
            "type": "feasibility",
            "target_nation": "",
            "talleyrand_text": "Sire, I need to know which nation you wish me to assess.",
            "options": [
                {"label": "Dismiss", "description": "Never mind.", "action": "dismiss"},
            ],
            "context": {},
            "turn_created": int(world.current_turn),
            "blocking": False,
        }

    # Run hypothetical acceptance
    hypothetical = {
        "type": proposal_type,
        "proposer_nation": player_nation,
        "target_nation": target_nation,
        "sweeteners": [],
        "demands": [],
        "clauses": [],
    }
    result = calculate_acceptance(hypothetical, world)
    score = result["score"]
    outcome = result["outcome"]
    components = result["components"]
    feedback = result["feedback"]

    # Find largest obstacle
    largest_obstacle = ""
    worst_val = 0
    for key, val in components.items():
        if val < worst_val:
            worst_val = val
            largest_obstacle = key

    # Calculate steps to goal
    current_state = world.get_diplomatic_state(player_nation, target_nation)
    from backend.game_logic.diplomacy import _UPGRADE_ORDER
    target_state_map = {
        "peace": "PEACE",
        "alliance": "ALLIANCE",
        "open_borders": "OPEN_BORDERS",
        "non_aggression": "NON_AGGRESSION",
        "armistice": "ARMISTICE",
    }
    goal_state = target_state_map.get(proposal_type, "PEACE")
    steps = 0
    if current_state in _UPGRADE_ORDER and goal_state in _UPGRADE_ORDER:
        curr_idx = _UPGRADE_ORDER.index(current_state)
        goal_idx = _UPGRADE_ORDER.index(goal_state)
        steps = max(0, goal_idx - curr_idx)

    # Build assessment text
    display_type = _display_proposal_type(proposal_type)
    if score >= 50:
        assessment = (
            f"Sire, {display_type} with {target_nation} appears quite achievable. "
            f"My assessment suggests a score of {int(score)} — they would likely accept. "
            f"{feedback}"
        )
    elif score >= 30:
        assessment = (
            f"Sire, {display_type} with {target_nation} is possible but uncertain. "
            f"My assessment yields {int(score)} — they might counter-offer. "
            f"{feedback}"
        )
    else:
        obstacle_names = {
            "relation_modifier": "our poor relations",
            "war_score_modifier": "the military situation",
            "hegemony_target_mod": "the pressure of the hegemon's bloc",
            "bilateral_betrayal_mod": "their memory of our broken commitments",
            "grievance_modifier": "their grievance over abandoned alliances",
            "deal_balance": "the balance of terms",
            "personality_modifier": "their diplomat's disposition",
            "base_disposition": "fundamental resistance to this type of agreement",
        }
        obstacle_text = obstacle_names.get(largest_obstacle, "several factors")
        assessment = (
            f"Sire, I must be frank — {display_type} with {target_nation} faces serious obstacles. "
            f"My assessment is only {int(score)}. The largest obstacle is {obstacle_text}. "
            f"{feedback}"
        )

    if steps > 0:
        assessment += f" We would need {steps} diplomatic steps to reach {goal_state}."

    # DP cost info
    dp_cost = get_dp_cost(f"propose_{proposal_type}", 10)
    assessment += f" The proposal itself would cost {int(dp_cost)} DP."

    return {
        "type": "feasibility",
        "target_nation": target_nation,
        "talleyrand_text": assessment,
        "options": [
            {
                "label": "Proceed anyway",
                "description": f"Send the {display_type} proposal despite the assessment.",
                "action": "execute_proposal",
                "terms": {
                    "proposal_type": proposal_type,
                    "target_nation": target_nation,
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                },
            },
            {"label": "Dismiss", "description": "Thank you, Talleyrand.", "action": "dismiss"},
        ],
        "context": {
            "war_score": int(get_war_score_for(world, player_nation, target_nation)),
            "relation": int(world.nation_relations.get(world._make_diplo_key(player_nation, target_nation), 0)),
            "threat": int(getattr(world, 'threat_level', 0)),
            "acceptance_score": int(score),
            "acceptance_outcome": outcome,
            "largest_obstacle": largest_obstacle,
            "steps_to_goal": int(steps),
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
    }


def generate_mission_dialogue(parsed_command: Dict, world) -> Dict:
    """Generate a mission confirmation dialogue."""
    target_nation = parsed_command.get("target_nation")
    mission_type = parsed_command.get("mission_type")

    if not target_nation:
        return {
            "type": "mission",
            "target_nation": "",
            "talleyrand_text": "Sire, where shall I direct my efforts?",
            "options": [
                {"label": "Dismiss", "description": "Never mind.", "action": "dismiss"},
            ],
            "context": {},
            "turn_created": int(world.current_turn),
            "blocking": False,
        }

    if mission_type == "CANCEL":
        return {
            "type": "mission",
            "target_nation": target_nation,
            "talleyrand_text": "Very well, Sire. I shall cease my diplomatic efforts.",
            "options": [
                {
                    "label": "Confirm cancel",
                    "description": "Cancel the current mission.",
                    "action": "cancel_mission",
                },
                {"label": "Continue mission", "description": "Keep the current mission active.", "action": "dismiss"},
            ],
            "context": {},
            "turn_created": int(world.current_turn),
            "blocking": False,
        }

    description = MISSION_DESCRIPTIONS.get(mission_type, "conduct diplomacy with")
    dp_cost = MISSION_DP_COSTS.get(mission_type, 1)

    # The confirm is the player's first sight of the mission: it names the
    # court, never the tag (R7 — "PapalStates" read here until IQ-4).
    from backend.display_names import display_nation as _dn
    name = _dn(target_nation)

    # Check for existing mission
    existing = getattr(world, 'active_diplomatic_mission', None)
    existing_text = ""
    if existing and not existing.get("completed"):
        existing_text = (
            f" Note: this will replace my current mission to "
            f"{MISSION_DESCRIPTIONS.get(existing['type'], 'conduct diplomacy with')} "
            f"{_dn(existing['target'])}."
        )

    # DLF-2: UNDERMINE_ALLIANCE requires ally selection
    if mission_type == "UNDERMINE_ALLIANCE":
        active_nations = world.get_active_nations()
        allies = [
            n for n in active_nations
            if n != target_nation and world.are_allies(target_nation, n)
        ]
        if not allies:
            return {
                "type": "mission",
                "target_nation": target_nation,
                "talleyrand_text": f"Sire, {name} has no alliances to undermine.",
                "options": [
                    {"label": "Dismiss", "description": "Never mind.", "action": "dismiss"},
                ],
                "context": {},
                "turn_created": int(world.current_turn),
                "blocking": False,
            }
        if len(allies) == 1:
            # Auto-select sole ally
            ally = allies[0]
            text = (
                f"Sire, I shall work to undermine the alliance between "
                f"{name} and {_dn(ally)}. "
                f"This will cost {int(dp_cost)} DP per turn.{existing_text}"
            )
            return {
                "type": "mission",
                "target_nation": target_nation,
                "talleyrand_text": text,
                "options": [
                    {
                        "label": "Begin mission",
                        "description": f"Undermine {name}-{_dn(ally)} alliance.",
                        "action": "start_mission",
                        "terms": {
                            "mission_type": mission_type,
                            "target_nation": target_nation,
                            "target_ally": ally,
                        },
                    },
                    {"label": "Not now", "description": "Cancel.", "action": "dismiss"},
                ],
                "context": {"dp_cost_per_turn": int(dp_cost), "target_ally": ally},
                "turn_created": int(world.current_turn),
                "blocking": False,
            }
        # Multiple allies — present selection
        text = (
            f"Sire, {name} has multiple alliances. "
            f"Which alliance shall I undermine? ({int(dp_cost)} DP/turn){existing_text}"
        )
        options = [
            {
                "label": f"{_dn(ally)}",
                "description": f"Undermine {name}-{_dn(ally)} alliance.",
                "action": "start_mission",
                "terms": {
                    "mission_type": mission_type,
                    "target_nation": target_nation,
                    "target_ally": ally,
                },
            }
            for ally in allies
        ]
        options.append({"label": "Not now", "description": "Cancel.", "action": "dismiss"})
        return {
            "type": "mission",
            "target_nation": target_nation,
            "talleyrand_text": text,
            "options": options,
            "context": {"dp_cost_per_turn": int(dp_cost)},
            "turn_created": int(world.current_turn),
            "blocking": False,
        }

    text = (
        f"Sire, I shall begin efforts to {description} {name}. "
        f"This will cost {int(dp_cost)} DP per turn.{existing_text}"
    )

    return {
        "type": "mission",
        "target_nation": target_nation,
        "talleyrand_text": text,
        "options": [
            {
                "label": "Begin mission",
                "description": f"Start {description} {name}.",
                "action": "start_mission",
                "terms": {
                    "mission_type": mission_type,
                    "target_nation": target_nation,
                },
            },
            {"label": "Not now", "description": "Cancel.", "action": "dismiss"},
        ],
        "context": {
            "dp_cost_per_turn": int(dp_cost),
        },
        # IQ-4: the top-level key `proposal_confirm_popup.gd` reads.
        "dp_cost": int(dp_cost),
        "turn_created": int(world.current_turn),
        "blocking": False,
    }
