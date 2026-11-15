"""The battle in acts (row BA, session BA-1) — the display-only battle SCRIPT.

Owner: `docs/BATTLE_DIORAMA_SPEC.md` §15 (the gate record of November 14,
2026; §15.5.2 the contract). The user's words: "a alyer of intrerwesting
developments personalities and visualizations with abstract player guidance".

One battle -> an ordered list of DEVELOPMENTS in five acts — the approach,
the cannonade, the assault, the crisis, the pursuit — that the tableau plays
on the war table. Built beside the tableau's payload and stored INSIDE it
(`payload["script"]`), so it inherits the payload's fog gate and both
transports.

The laws of this module:

1. Display only (Golden Rule 6). Nothing here is read by routing or
   mechanics, and nothing is written to a marshal or the world.
2. Never a beat the model does not have (the eval's rule, BATTLE_DIORAMA_
   EVAL_2026_07_17 §5). Every beat is made from a number or a flag the
   resolver already produced; an act with no beat is not played.
3. Fog is correctness. A beat names only a corps the payload already shows
   (its seated contingents and its shelf). Of a side that is not the
   player's it tells what the field itself showed and what the battle's own
   report already prints, and nothing else: never the province a corps
   marched FROM (he goes back there after the battle), never the road he
   left by, never his arrival roll, never that he was under orders, never
   the provinces an enemy attack came in from. Of a battle the player only
   WATCHED (`player_side` empty; the payload exists at FULL sight of the
   field) it tells who came, the dice, who broke and who holds the ground:
   no modifier row of either army, no tactical state, no battery standing
   off the field — the player has no battle report for a battle that was
   not his.
4. Every number is an int (Golden Rule 2). No float reaches the wire: the
   top-level `battle_diorama` key is not float-stripped.
"""

from typing import Dict, List, Optional

from backend.display_names import display_nation, humanize_entity_name

ACTS = ("approach", "cannonade", "assault", "crisis", "pursuit")

# An arrival won by this many points or fewer reads "at the last hour". In
# BA-1 it is a reading of the two numbers the arrival roll produced; BA-3
# gives it its weight (BATTLE_DIORAMA_SPEC.md §15.5.7).
LAST_HOUR_MARGIN = 5

_ABSENT = ("failed_arrive", "refused", "out_of_reach")
_TEMPERS = ("aggressive", "cautious", "literal", "sovereign")


def _n(name) -> str:
    return humanize_entity_name(str(name or ""))


def _i(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def temper_of(marshal) -> str:
    """The movement signature a commander's corps carries on the table: his
    temperament, or `steady` for one the model gives no fighting character."""
    if getattr(marshal, "is_sovereign", False):
        return "sovereign"
    personality = str(getattr(marshal, "personality", "") or "").lower()
    return personality if personality in _TEMPERS else "steady"


def _beat(kind: str, side: str, actor: str, text: str, weight: str = "detail",
          **fields) -> dict:
    beat = {"kind": kind, "side": side, "actor": str(actor or ""),
            "text": str(text), "weight": weight}
    for key, value in fields.items():
        if isinstance(value, bool) or isinstance(value, str):
            beat[key] = value
        elif isinstance(value, (list, tuple)):
            beat[key] = [str(v) for v in value]
        else:
            beat[key] = _i(value)
    return beat


def _signed(row: dict) -> str:
    """A modifier row's figure as the table prints it: "+15%" / "−10%"."""
    value = _i(row.get("value"))
    return f"{'−' if row.get('type') == 'penalty' else '+'}{value}%"


def _rows(battle_result: dict, side: str) -> List[dict]:
    snapshot = battle_result.get("modifier_snapshot") or {}
    rows = snapshot.get(side) if isinstance(snapshot, dict) else None
    return [r for r in (rows or []) if isinstance(r, dict)]


def _row(rows: List[dict], prefix: str) -> Optional[dict]:
    for row in rows:
        if str(row.get("label", "")).startswith(prefix):
            return row
    return None


# ── The assault's rows, by the label the report already prints ────────────
#
# (label prefix, kind, weight, sentence). `{a}` is the corps the row belongs
# to, `{o}` his opponent, `{f}` the row's own figure. A row not listed here
# (terrain, works, the Emperor, the flank, overwatch) is told in another act.

_ATTACK_ROWS = (
    ("Drill training", "drilled", "head",
     "{a}'s drilled battalions go in as one ({f})."),
    ("Iron Resolve", "ability", "head",
     "{a}'s coiled resolve is released: Iron Resolve ({f})."),
    ("Counter-Punch Mastery", "ability", "head",
     "{a} has taken their measure: Counter-Punch Mastery ({f})."),
    ("Cavalry counter", "overrun", "head",
     "{a}'s horse rides over the guns ({f})."),
    ("Square formation (vs cavalry)", "square", "head",
     "{o}'s squares stand against the horse ({f})."),
    ("Square formation (vs artillery)", "square", "head",
     "{o}'s packed squares are a mark for the guns ({f})."),
    ("Glorious Charge", "charge", "head",
     "A glorious charge: double the blood, given and taken."),
    ("Recklessness", "reckless", "head",
     "{a}'s blood is up ({f})."),
    ("Exhaustion", "exhausted", "head",
     "{a}'s men have fought already today ({f})."),
    ("Cavalry terrain", "ground_horse", "detail",
     "The ground tells on {a}'s horse ({f})."),
    ("Aggressive stance", "stance", "detail",
     "{a} attacks in an aggressive posture ({f})."),
    ("Defensive stance", "stance", "detail",
     "{a} attacks out of a defensive posture ({f})."),
    ("Forced march momentum", "momentum", "detail",
     "{a} comes off a completed march with momentum ({f})."),
)

_DEFENCE_ROWS = (
    ("Immovable", "ability", "head",
     "{a} holds exactly where he was posted ({f})."),
    ("Reverse Slope Defense", "ability", "head",
     "{a} keeps his line behind the crest: Reverse Slope Defense ({f})."),
    ("Child of Victory", "ability", "head",
     "{a} is at his best outnumbered: Child of Victory ({f})."),
    ("Habsburg Resolve", "ability", "head",
     "{a}'s regiments stand steady: Habsburg Resolve ({f})."),
    ("Caught drilling", "caught", "head",
     "{a} is caught at drill ({f})."),
    ("Artillery in transit", "caught", "head",
     "{a}'s guns are caught limbered ({f})."),
    ("Outnumbered", "outnumbered", "detail",
     "{a} stands firm against numbers ({f})."),
    ("Defensive stance", "stance", "detail",
     "{a} stands on the defensive ({f})."),
    ("Aggressive stance", "stance", "detail",
     "{a} is caught in an attacking posture ({f})."),
    ("Recklessness", "reckless", "detail",
     "{a}'s horse is overextended ({f})."),
    ("Forced march momentum", "momentum", "detail",
     "{a} stands with a completed march behind him ({f})."),
)

# The defender's ground, in the table's words (the label's own terrain name).
_GROUND = {
    "hills": "on the heights",
    "forest": "in the woods",
    "river": "behind the river",
    "river crossing": "behind the river crossing",
    "mountains": "in the mountains",
    "mountain": "in the mountains",
    "urban": "in the town",
    "marsh": "behind the marshes",
    "fortified": "in a fortified position",
}

# How each temperament closes with the enemy / receives him. The corps'
# movement on the table follows the same key (`script["tempers"]`).
_ADVANCE = {
    "aggressive": "{a} goes in at the head of his men{f}.",
    "cautious": "{a} comes on by measured steps{f}.",
    "literal": "{a} advances to his mark, as ordered, and no further{f}.",
    "sovereign": "The line dresses on the Emperor and goes forward{f}.",
    "steady": "{a} leads the attack in{f}.",
}
_RECEIVE = {
    "aggressive": "{a} comes out to meet them{f}.",
    "cautious": "{a} holds his ground and lets them come{f}.",
    "literal": "{a} stands where he was posted{f}.",
    "sovereign": "The Emperor's line waits for them{f}.",
    "steady": "{a} receives the attack{f}.",
}


class _Script:
    """The acts in order, and the one fog rule: a beat that names a corps
    names one the payload shows."""

    def __init__(self, shown):
        self.shown = set(shown)
        self.acts: Dict[str, List[dict]] = {act: [] for act in ACTS}

    def add(self, act: str, beat: dict, *, named=()) -> None:
        for name in (beat.get("actor"), *named):
            if name and name not in self.shown:
                return
        self.acts[act].append(beat)


def _approach(script: _Script, payload: dict, attacker, defender,
              battle_result: dict, reinforcements: Dict[str, list],
              facts: dict, player_side: Optional[str]) -> None:
    region = str(payload.get("region", "") or "")
    script.add("approach", _beat(
        "open", "attacker", attacker.name,
        f"{_n(attacker.name)} attacks {_n(defender.name)} at {region}."),
        named=(defender.name,))

    for side in ("attacker", "defender"):
        lead = attacker if side == "attacker" else defender
        for row in reinforcements.get(side) or []:
            if not isinstance(row, dict) or not row.get("arrived"):
                continue
            name = str(row.get("marshal", "") or "")
            origin = str(row.get("origin", "") or "")
            score, bar = _i(row.get("score")), _i(row.get("threshold"))
            margin = score - bar
            late = 0 < margin <= LAST_HOUR_MARGIN
            # The roll's own figures, the province he marched from, his
            # orders and his court's doctrine are the marching side's to
            # read; the other side's corps is seen to come, and to come
            # late, never whence, by how much or why.
            own = bool(player_side) and side == player_side
            ordered = own and bool(row.get("has_explicit_order") or row.get("arrived_via_support"))
            doctrine = (str(row.get("doctrine", "") or "")
                        if own and row.get("doctrine_arrived") else "")
            whence = f" from {origin}" if own and origin and origin != region else ""
            if late and own:
                text = (f"{_n(name)} comes up{whence} at the last hour "
                        f"({score} against a bar of {bar}).")
            elif late:
                text = f"{_n(name)} comes up at the last hour."
            elif doctrine:
                text = f"{_n(name)} arrives{whence}: {doctrine} brought him in time."
            elif ordered:
                text = f"{_n(name)} marches{whence} to join {_n(lead.name)}, as ordered."
            else:
                text = f"{_n(name)} marches{whence} to the sound of the guns."
            script.add("approach", _beat(
                "arrive", side, name, text,
                weight="head" if (late or doctrine) else "detail",
                late=late,
                **({"score": score, "bar": bar, "margin": margin,
                    "origin": origin, "ordered": ordered} if own else {}),
                # the other side's corps comes up unseen and is made out on
                # arrival (the tableau turns its plinth up)
                concealed=bool(player_side and side != player_side)))

    for side in ("attacker", "defender"):
        for c in (payload.get(side) or {}).get("contingents") or []:
            if c.get("status") not in _ABSENT:
                continue
            name = str(c.get("name", "") or "")
            reason = str(c.get("absence_reason", "") or "did not march")
            grudge = str(c.get("grudge", "") or "")
            text = f"{_n(name)} does not come: {reason}."
            if grudge:
                text += f" {grudge}"
            script.add("approach", _beat(
                "absent", side, name, text,
                weight="head" if side == player_side else "detail",
                status=str(c.get("status", ""))))

    bonus = _i(facts.get("flanking_bonus"))
    # The provinces an attack came in from are the attacker's own to name.
    origins = (sorted(str(o) for o in (facts.get("flanking_origins") or []) if o)
               if player_side == "attacker" else [])
    if bonus > 0:
        if len(origins) >= 2:
            text = (f"The attack comes in from {len(origins)} provinces "
                    f"({', '.join(origins)}): +{bonus} on the dice.")
        else:
            text = f"The attack turns the flank: +{bonus} on the dice."
        script.add("approach", _beat(
            "flank", "attacker", attacker.name, text, weight="head",
            bonus=bonus, origins=origins))

    def_rows = _rows(battle_result, "defender")
    terrain = _row(def_rows, "Terrain (")
    works = _row(def_rows, "Fortified position")
    walls = _row(def_rows, "Fortification building")
    square = _row(def_rows, "Square formation")
    clauses = []
    if terrain:
        ground = str(terrain.get("label", ""))[len("Terrain ("):].rstrip(")").lower()
        clauses.append(f"{_GROUND.get(ground, f'on {ground} ground')} ({_signed(terrain)})")
    if not player_side:
        works = walls = square = None      # watched: the ground is the map's, the rest is theirs
    if works:
        clauses.append(f"behind field works ({_signed(works)})")
    if walls:
        clauses.append(f"under the fortress ({_signed(walls)})")
    if square:
        clauses.append("formed in square")
    if clauses:
        script.add("approach", _beat(
            "ground", "defender", defender.name,
            f"{_n(defender.name)} stands " + ", ".join(clauses) + ".",
            terrain_pct=_i((terrain or {}).get("value")),
            works_pct=_i((works or {}).get("value")),
            walls_pct=_i((walls or {}).get("value")),
            square=bool(square)))

    for side, lead in (("attacker", attacker), ("defender", defender)):
        row = _row(_rows(battle_result, side), "The Emperor commands in person")
        if not row:
            continue
        dimmed = "star dims" in str(row.get("label", ""))
        script.add("approach", _beat(
            "presence", side, lead.name,
            (f"The Emperor commands in person, his star dimmed: {_signed(row)} "
             f"along the line." if dimmed else
             f"The Emperor commands in person: {_signed(row)} along the line."),
            weight="head", pct=_i(row.get("value")), dimmed=dimmed))


def _cannonade(script: _Script, attacker, defender, battle_result: dict,
               facts: dict, player_side: Optional[str]) -> None:
    if not player_side:
        return      # watched: a battery off the field and a modifier row are not the watcher's
    for result in facts.get("auto_bombardment_results") or []:
        br = (result or {}).get("bombardment_result") if isinstance(result, dict) else None
        if not isinstance(br, dict):
            continue
        gunner = str((br.get("attacker") or {}).get("name", "") or "")
        dealt = _i((br.get("defender") or {}).get("casualties"))
        taken = _i((br.get("attacker") or {}).get("casualties"))
        if not gunner or dealt <= 0:
            continue
        text = (f"{_n(gunner)}'s guns open on {_n(defender.name)}'s line: "
                f"{dealt:,} fall before the assault.")
        if br.get("fort_degraded"):
            text += (f" The works come down from {_i(br.get('fort_old'))}% "
                     f"to {_i(br.get('fort_new'))}%.")
        # The battery's name already stands in the battle's own message
        # ("Artillery support: X's guns bombard…"); it is not a new leak.
        script.acts["cannonade"].append(_beat(
            "battery", "attacker", gunner, text, weight="head",
            dealt=dealt, taken=taken, target=defender.name))

    count = _i(facts.get("overwatch_count"))
    row = _row(_rows(battle_result, "attacker"), "Artillery overwatch")
    if count > 0 and row:
        script.add("cannonade", _beat(
            "overwatch", "defender", defender.name,
            f"{_n(defender.name)}'s side has guns covering the approach: "
            f"{_signed(row)} on every attacker.",
            guns=count, pct=_i(row.get("value"))))


def _assault(script: _Script, attacker, defender, battle_result: dict,
             player_side: Optional[str]) -> None:
    atk_rows, def_rows = _rows(battle_result, "attacker"), _rows(battle_result, "defender")
    if not player_side:
        atk_rows, def_rows = [], []        # watched: how each closes, and no row of either army
    for side, lead, rows, lines in (
            ("attacker", attacker, atk_rows, _ADVANCE),
            ("defender", defender, def_rows, _RECEIVE)):
        temper = temper_of(lead)
        row = _row(rows, "Personality (")
        figure = f" ({_signed(row)})" if row else ""
        script.add("assault", _beat(
            "advance", side, lead.name,
            lines[temper].format(a=_n(lead.name), f=figure),
            weight="head" if side == "attacker" else "detail",
            temper=temper, pct=_i((row or {}).get("value")),
            penalty=bool(row and row.get("type") == "penalty")))

    if battle_result.get("ability_triggered") and player_side:
        ability = (getattr(attacker, "ability", None) or {}).get("name", "")
        if ability:
            script.add("assault", _beat(
                "ability", "attacker", attacker.name,
                f"{_n(attacker.name)}'s blow lands harder: {ability}.",
                weight="head", ability=str(ability)))

    for side, lead, other, rows, table in (
            ("attacker", attacker, defender, atk_rows, _ATTACK_ROWS),
            ("defender", defender, attacker, def_rows, _DEFENCE_ROWS)):
        for prefix, kind, weight, sentence in table:
            row = _row(rows, prefix)
            if not row:
                continue
            script.add("assault", _beat(
                kind, side, lead.name,
                sentence.format(a=_n(lead.name), o=_n(other.name), f=_signed(row)),
                weight=weight, pct=_i(row.get("value")),
                penalty=bool(row.get("type") == "penalty")),
                named=(other.name,))
        for row in rows:
            if row.get("doctrine"):
                script.add("assault", _beat(
                    "doctrine", side, lead.name,
                    f"{_n(lead.name)}'s court tells on the field: "
                    f"{row.get('label', 'its doctrine')} ({_signed(row)}).",
                    pct=_i(row.get("value"))))


def _fate_of(world, name: str, lead_broke: bool, origins: dict, region: str):
    """What became of one corps, read off the marshal after the retreat and
    the advance have run (stage 18): (how, where he stands now)."""
    marshal = (getattr(world, "marshals", None) or {}).get(name)
    if marshal is None:
        return "destroyed", ""
    if getattr(marshal, "captured_by", ""):
        return "captured", ""
    if _i(getattr(marshal, "strength", 0)) <= 0:
        return "destroyed", ""
    here = str(getattr(marshal, "location", "") or "")
    if getattr(marshal, "broken", False):
        return "shattered", here
    if getattr(marshal, "retreated_this_turn", False) or lead_broke:
        return "routed", here
    if name in origins and here != region and here == origins.get(name):
        return "withdrew", here
    return "", here


def _crisis(script: _Script, world, payload: dict, attacker, defender,
            battle_result: dict, facts: dict, player_nation: str,
            player_side: Optional[str]) -> Dict[str, str]:
    roll = battle_result.get("attacker_roll") or {}
    fortune = battle_result.get("fortune") or {}
    if isinstance(roll, dict) and roll.get("natural") is not None:
        natural, skill = _i(roll.get("natural")), _i(roll.get("skill_bonus"))
        flank, modified = _i(roll.get("flanking_bonus")), _i(roll.get("modified"))
        critical = ("success" if roll.get("is_critical_success") else
                    "failure" if roll.get("is_critical_failure") else "")
        parts = [f"{_n(attacker.name)} rolls {natural}"]
        if skill:
            parts.append(f"+{skill} for his eye for ground")
        if flank:
            parts.append(f"+{flank} for the flank")
        text = "The fortune of the day: " + ", ".join(parts) + f": {modified}."
        if critical == "success":
            text += " Twelve on the dice: everything goes right."
        elif critical == "failure":
            text += " Two on the dice: everything goes wrong."
        script.add("crisis", _beat(
            "dice", "attacker", attacker.name, text, weight="head",
            natural=natural, skill=skill, flank=flank, modified=modified,
            critical=critical,
            # the roll scales the blood the attack draws: 85% at 0 … 120% at 14
            swing=int(round(85 + 2.5 * modified)) - 100,
            fortune_attacker=_i(fortune.get("attacker")),
            fortune_defender=_i(fortune.get("defender"))))

    region = str(payload.get("region", "") or "")
    origins = facts.get("reinforcer_origin") or {}
    fates: Dict[str, str] = {}
    broke_any = False
    for side, lead in (("attacker", attacker), ("defender", defender)):
        side_result = battle_result.get(side) or {}
        lead_broke = bool(side_result.get("forced_retreat"))
        for c in (payload.get(side) or {}).get("contingents") or []:
            name = str(c.get("name", "") or "")
            if c.get("status") in _ABSENT or not name:
                continue
            is_lead = name == lead.name
            how, _where = _fate_of(world, name, is_lead and lead_broke, origins, region)
            if is_lead and c.get("status") == "destroyed":
                how = how or "destroyed"
            fates[name] = how
            if how in ("routed", "shattered", "destroyed", "captured"):
                broke_any = True
                morale = _i(side_result.get("morale")) if is_lead else -1
                words = {
                    "routed": (f"{_n(name)}'s line breaks at {morale}% morale."
                               if morale >= 0 else f"{_n(name)}'s corps gives way."),
                    "shattered": f"{_n(name)}'s army is shattered, with no road left open.",
                    "destroyed": f"{_n(name)}'s corps is destroyed on the field.",
                    "captured": f"{_n(name)} is taken on the field.",
                }[how]
                script.add("crisis", _beat(
                    "break", side, name, words, weight="head", how=how,
                    morale=max(morale, 0)))

        marshal = (getattr(world, "marshals", None) or {}).get(lead.name)
        if marshal is not None and not lead_broke and hasattr(marshal, "get_rout_threshold"):
            morale = _i(getattr(marshal, "morale", 100))
            floor = _i(marshal.get_rout_threshold(25))
            victor = battle_result.get("victor") == lead.name
            if player_side and not victor and floor < 25 and floor < morale <= 25:
                script.add("crisis", _beat(
                    "holds", side, lead.name,
                    f"{_n(lead.name)}'s regiments close ranks at {morale}% morale: "
                    f"they will not break.",
                    weight="head", morale=morale,
                    **({"floor": floor} if side == player_side else {})))

        pending = getattr(marshal, "pending_interrupt", None) if marshal is not None else None
        if (isinstance(pending, dict) and pending.get("interrupt_type") == "last_stand"
                and getattr(marshal, "nation", "") == player_nation):
            script.add("crisis", _beat(
                "last_stand", side, lead.name,
                f"{_n(lead.name)} is cornered. The question is yours.",
                weight="head"))

    if not broke_any:
        script.add("crisis", _beat(
            "stand", "", "", "Neither line gives way: the day hangs.", weight="head"))
    return fates


def _pursuit(script: _Script, world, payload: dict, attacker, defender,
             battle_result: dict, facts: dict, fates: Dict[str, str],
             player_nation: str, player_side: Optional[str]) -> None:
    damage = _i(battle_result.get("pursuit_damage"))
    if damage > 0:
        ability = (getattr(attacker, "ability", None) or {}).get("name", "")
        screened = (getattr(defender, "ability", None) or {}).get("name", "") == "The Old Fox"
        text = f"{_n(attacker.name)} rides them down"
        if ability:
            text += f" ({ability})"
        text += f": {damage:,} more."
        if screened:
            text += f" {_n(defender.name)}'s rearguard screened the retreat and halved the harvest."
        script.add("pursuit", _beat(
            "pursue", "attacker", attacker.name, text, weight="head",
            damage=damage, halved=screened, target=defender.name),
            named=(defender.name,))

    region = str(payload.get("region", "") or "")
    origins = facts.get("reinforcer_origin") or {}
    for side in ("attacker", "defender"):
        for c in (payload.get(side) or {}).get("contingents") or []:
            name = str(c.get("name", "") or "")
            how = fates.get(name, "")
            if not how or how in ("destroyed", "captured"):
                continue
            _how, where = _fate_of(world, name, how == "routed", origins, region)
            # An enemy's road off the field is his own intelligence; ours is ours.
            marshal = (getattr(world, "marshals", None) or {}).get(name)
            own = getattr(marshal, "nation", "") == player_nation
            to = where if (own and where and where != region) else ""
            if how == "withdrew":
                text = (f"{_n(name)} withdraws to {to} after the battle." if to
                        else f"{_n(name)} draws off after the battle.")
            else:
                text = (f"{_n(name)} falls back on {to}." if to
                        else f"{_n(name)} leaves the field.")
            script.add("pursuit", _beat("leave", side, name, text, how=how, to=to))

    advanced = str(facts.get("advanced_to") or "")
    if advanced:
        # A narrow day leaves both armies in the province ("Both armies
        # remain in the field" is the battle's own line): say so, or "the
        # day hangs" followed by an advance reads as a contradiction.
        foe = (getattr(world, "marshals", None) or {}).get(defender.name)
        stands = bool(
            foe is not None and _i(getattr(foe, "strength", 0)) > 0
            and not getattr(foe, "captured_by", "")
            and not getattr(foe, "retreated_this_turn", False)
            and str(getattr(foe, "location", "") or "") == advanced)
        tail = f", where {_n(defender.name)} still stands." if stands else "."
        script.add("pursuit", _beat(
            "advance_to", "attacker", attacker.name,
            f"{_n(attacker.name)} advances into {advanced}{tail}",
            to=advanced, contested=stands), named=(defender.name,) if stands else ())

    if payload.get("region_conquered"):
        line = str(payload.get("liberation_line", "") or "")
        if not line:
            victor = display_nation(str(payload.get("attacker_nation", "") or ""))
            line = f"{region} falls to {victor}." if victor else f"{region} changes hands."
        script.add("pursuit", _beat(
            "province", "attacker", attacker.name, line, weight="head", region=region))

    if battle_result.get("fortification_degraded") and player_side:
        script.add("pursuit", _beat(
            "works", "defender", defender.name,
            f"{_n(defender.name)}'s works are battered: "
            f"{_i(battle_result.get('fortification_old'))}% to "
            f"{_i(battle_result.get('fortification_new'))}%.",
            old=_i(battle_result.get("fortification_old")),
            new=_i(battle_result.get("fortification_new"))))

    # The free blow is told to the man who earned it: the game gives that
    # notice to the player's own defender and to nobody else.
    if (battle_result.get("counter_punch_earned") and player_side == "defender"
            and fates.get(defender.name, "") == ""):
        script.add("pursuit", _beat(
            "counter_punch", "defender", defender.name,
            f"{_n(defender.name)} has held, and a free blow is his."))


def build_battle_script(world, payload: dict, attacker, defender,
                        battle_result: dict,
                        attacker_reinforcements: list,
                        defender_reinforcements: list,
                        facts: Optional[dict] = None) -> dict:
    """The five-act script of one battle, for the payload that will carry it.

    `facts` are the executor's extras the payload's own builder is not
    handed (all optional — a caller that has none still gets every beat the
    battle result itself can tell): `reinforcer_origin` {name: province},
    `flanking_origins` [province], `flanking_bonus` int,
    `auto_bombardment_results` [executor results], `overwatch_count` int,
    `advanced_to` province or None.
    """
    facts = facts if isinstance(facts, dict) else {}
    battle_result = battle_result if isinstance(battle_result, dict) else {}
    player_nation = str(getattr(world, "player_nation", "France") or "France")
    player_side = payload.get("player_side")

    shown = set()
    tempers: Dict[str, str] = {}
    for side in ("attacker", "defender"):
        for c in (payload.get(side) or {}).get("contingents") or []:
            name = str(c.get("name", "") or "")
            if not name:
                continue
            shown.add(name)
            marshal = (getattr(world, "marshals", None) or {}).get(name)
            if marshal is None:
                marshal = attacker if name == attacker.name else (
                    defender if name == defender.name else None)
            tempers[name] = temper_of(marshal) if marshal is not None else "steady"

    script = _Script(shown)
    _approach(script, payload, attacker, defender, battle_result,
              {"attacker": attacker_reinforcements or [],
               "defender": defender_reinforcements or []},
              facts, player_side)
    _cannonade(script, attacker, defender, battle_result, facts, player_side)
    _assault(script, attacker, defender, battle_result, player_side)
    fates = _crisis(script, world, payload, attacker, defender, battle_result,
                    facts, player_nation, player_side)
    _pursuit(script, world, payload, attacker, defender, battle_result, facts,
             fates, player_nation, player_side)

    full = bool(payload.get("great_battle") or payload.get("dramatic"))
    return {
        "version": 1,
        "form": "full" if full else "brief",
        "acts": [{"act": act, "beats": script.acts[act]}
                 for act in ACTS if script.acts[act]],
        "tempers": tempers,
    }
