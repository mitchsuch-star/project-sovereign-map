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
from backend.game_logic import campaign_variance as _cv

ACTS = ("approach", "cannonade", "assault", "crisis", "pursuit")

# An arrival won by this many points or fewer reads "at the last hour". In
# BA-1 it is a reading of the two numbers the arrival roll produced; BA-4
# gives it its weight (BATTLE_DIORAMA_SPEC.md §15.5.7: three quarters —
# `combat_executor.the_last_hour_brings_three_quarters`).
LAST_HOUR_MARGIN = 5


LAST_HOUR_WEIGHT_LINE = " He brings three-quarters of his weight."


def arrived_at_the_last_hour(row) -> bool:
    """ONE definition for the telling and the weight: a reinforcement row that
    ARRIVED on a roll won by `LAST_HOUR_MARGIN` points or fewer."""
    if not isinstance(row, dict) or not row.get("arrived"):
        return False
    try:
        margin = int(row.get("score")) - int(row.get("threshold"))
    except (TypeError, ValueError):
        return False
    return 0 < margin <= LAST_HOUR_MARGIN

_ABSENT = ("failed_arrive", "refused", "out_of_reach")
_TEMPERS = ("aggressive", "cautious", "literal", "sovereign")


def _n(name) -> str:
    return humanize_entity_name(str(name or ""))


def _i(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _men(count: int, one: str = "man", many: str = "men") -> str:
    """"1 man" / "25,000 men": the count with its separator, the noun agreeing
    with it (the review, November 15, 2026: BA2-X14)."""
    return f"{count:,} {one if count == 1 else many}"


def _fall(count: int) -> str:
    """"1 falls" / "3,000 fall"."""
    return f"{count:,} fall{'s' if count == 1 else ''}"


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


# Variant lines (BA-3, ruling 12). Where a beat's line has variants, the
# FIRST template is the line every battle was told with; the rest say the
# same thing with the same facts and the same fog exposure.

_ADVANCE_ALT = {
    "aggressive": ("{a} leads the charge himself{f}.",
                   "{a} puts himself at the front of the column{f}."),
    "cautious": ("{a} advances with deliberation{f}.",
                 "{a} brings his line forward step by step{f}."),
    "literal": ("{a} marches to the position given him, and halts there{f}.",
                "{a} keeps strictly to his orders and goes no further{f}."),
    "sovereign": ("The army moves forward under the Emperor's eye{f}.",
                  "The Emperor's line steps off together{f}."),
    "steady": ("{a} opens the attack{f}.",
               "{a} takes the assault forward{f}."),
}
_RECEIVE_ALT = {
    "aggressive": ("{a} falls on them as they come{f}.",
                   "{a} advances to meet the blow{f}."),
    "cautious": ("{a} stands his ground and waits for them{f}.",
                 "{a} lets them come to him{f}."),
    "literal": ("{a} keeps to the post he was given{f}.",
                "{a} holds the position assigned him{f}."),
    "sovereign": ("The Emperor's line stands to receive them{f}.",
                  "The Emperor's troops wait steady for the attack{f}."),
    "steady": ("{a} meets the attack{f}.",
               "{a} stands to receive the blow{f}."),
}


class _Script:
    """The acts in order, and the one fog rule: a beat that names a corps
    names one the payload shows."""

    def __init__(self, shown, world=None, identity=()):
        self.shown = set(shown)
        self.acts: Dict[str, List[dict]] = {act: [] for act in ACTS}
        self.world = world
        self.identity = tuple(str(p) for p in identity)

    def varies(self) -> bool:
        """True only for a campaign the game server holds, on a rolled seed,
        with the narration seam up: everything else is told in the first
        words, byte for byte (the suite and the staging tools build
        unserved or `historical` worlds)."""
        world = self.world
        if world is None or not _cv.the_narration_varies():
            return False
        if not _cv.campaign_is_served(world):
            return False
        return not _cv.is_historical(getattr(world, "campaign_seed", None))

    def said(self, kind: str, *templates: str, **fields) -> str:
        """One beat's line. `templates[0]` is today's text; the others are
        variants. The choice is the campaign seed's, keyed on the battle's own
        identity (the leads, the province, the turn), the beat's kind and the
        optional `who` (a corps' name, so two beats of one kind in one battle
        may differ): never the battle's dice, never the module `random`."""
        who = str(fields.pop("who", "") or "")
        chosen = templates[0]
        if len(templates) > 1 and self.varies():
            seed = str(getattr(self.world, "campaign_seed", "") or "")
            namespace = "::".join(("battle_script", kind, who, *self.identity))
            chosen = templates[_cv.seeded_tiebreak(
                seed, namespace, list(range(len(templates))))]
        return chosen.format(**fields)

    def add(self, act: str, beat: dict, *, named=()) -> None:
        for name in (beat.get("actor"), *named):
            if name and name not in self.shown:
                return
        self.acts[act].append(beat)


def _listed(names) -> str:
    """"Davout", "Davout and Lannes", "Davout, Lannes and Murat"."""
    shown = [_n(n) for n in names if n]
    if len(shown) <= 1:
        return "".join(shown)
    return ", ".join(shown[:-1]) + " and " + shown[-1]


def _posture(stance: Optional[dict]) -> str:
    return "aggressive" if str((stance or {}).get("label", "")).startswith("Aggressive") \
        else "defensive"


def _plan(script: _Script, attacker, defender, battle_result: dict,
          reinforcements: Dict[str, list], facts: dict,
          player_side: Optional[str]) -> bool:
    """§15.5.5 (BA-2): Act I names the plan the player's orders amount to —
    the orders the game already has, each with its number, and nothing else.

    Fog case 1 only: a side's orders are its own to read, so the beat is
    written for the player's side and never for the other. No beat where
    there is no order to name — a bare one-corps attack has no plan, and
    ground the map gave (the heights, the river) is no order of his.

    Returns True when the player's DEFENSIVE dispositions were told, so the
    `ground` beat that would say the same works twice is left out."""
    if player_side not in ("attacker", "defender"):
        return False
    lead = attacker if player_side == "attacker" else defender
    rows = _rows(battle_result, player_side)
    mine = [r for r in (reinforcements.get(player_side) or [])
            if isinstance(r, dict) and r.get("marshal")
            and (r.get("has_explicit_order") or r.get("arrived_via_support"))]
    ordered = [str(r.get("marshal")) for r in mine]
    # Each order in its own word: a SUPPORT of the lead, or a PURSUE whose
    # quarry stands on this field — the resolver counts both as a written
    # order (`order_type` on the reinforcement row), and the beat called the
    # second "ordered in support" (the review, November 15, 2026: BA2-X13).
    # The guns first: a gunner already under orders is told once, as the
    # guns, not twice (the review, November 15, 2026: BA2-X14).
    guns: List[str] = []
    if player_side == "attacker":
        for result in facts.get("auto_bombardment_results") or []:
            br = (result or {}).get("bombardment_result") if isinstance(result, dict) else None
            gunner = str(((br or {}).get("attacker") or {}).get("name", "") or "")
            if gunner and gunner not in guns:
                guns.append(gunner)
    chasing = [str(r.get("marshal")) for r in mine
               if str(r.get("order_type") or "") == "PURSUE"]
    pursuing = [name for name in chasing if name not in guns]
    supporting = [name for name in ordered if name not in chasing and name not in guns]
    came = sum(1 for r in mine if r.get("arrived"))
    stance = _row(rows, "Aggressive stance") or _row(rows, "Defensive stance")
    posture = _posture(stance) if stance else ""
    support = "; ".join(clause for clause in (
        f"{_listed(supporting)} ordered in support" if supporting else "",
        f"{_listed(pursuing)} ordered in pursuit" if pursuing else "") if clause)

    if player_side == "attacker":
        bonus = _i(facts.get("flanking_bonus"))
        origins = sorted(str(o) for o in (facts.get("flanking_origins") or []) if o)
        drilled = _row(rows, "Drill training")
        clauses = [support] if support else []
        if bonus > 0:
            clauses.append(
                f"the attack from {len(origins)} provinces (+{bonus} on the dice)"
                if len(origins) >= 2 else f"the flank turned (+{bonus} on the dice)")
        if drilled:
            clauses.append(f"a drilled assault ({_signed(drilled)})")
        if stance:
            clauses.append(f"{'an' if posture == 'aggressive' else 'a'} {posture} posture "
                           f"({_signed(stance)})")
        if guns:
            clauses.append(f"{_listed(guns)}'s guns in support")
        if not clauses:
            return False
        script.add("approach", _beat(
            "plan", "attacker", lead.name,
            f"The plan: {_n(lead.name)} leads; " + "; ".join(clauses) + ".",
            weight="head", supports=ordered, came=came, flank=bonus, origins=origins,
            drilled=_i((drilled or {}).get("value")), stance=posture,
            stance_pct=_i((stance or {}).get("value")), guns=guns))
        return False

    terrain = _row(rows, "Terrain (")
    works = _row(rows, "Fortified position")
    walls = _row(rows, "Fortification building")
    square = _row(rows, "Square formation")
    count = _i(facts.get("overwatch_count"))
    overwatch = _row(_rows(battle_result, "attacker"), "Artillery overwatch") if count > 0 else None
    if not (works or walls or square or overwatch or stance or support):
        return False
    stands = []
    if terrain:
        ground = str(terrain.get("label", ""))[len("Terrain ("):].rstrip(")").lower()
        stands.append(f"{_GROUND.get(ground, f'on {ground} ground')} ({_signed(terrain)})")
    if works:
        stands.append(f"behind field works ({_signed(works)})")
    if walls:
        stands.append(f"under the fortress ({_signed(walls)})")
    if square:
        stands.append("formed in square")
    clauses = [f"{_n(lead.name)} holds" + (" " + ", ".join(stands) if stands else "")]
    if stance:
        clauses.append(f"{'an' if posture == 'aggressive' else 'a'} {posture} posture "
                       f"({_signed(stance)})")
    if overwatch:
        clauses.append(f"{count} batter{'ies' if count != 1 else 'y'} covering the approach "
                       f"({_signed(overwatch)} on every attacker)")
    if support:
        clauses.append(support)
    script.add("approach", _beat(
        "plan", "defender", lead.name,
        "Your dispositions: " + "; ".join(clauses) + ".",
        weight="head", supports=ordered, came=came,
        terrain_pct=_i((terrain or {}).get("value")),
        works_pct=_i((works or {}).get("value")),
        walls_pct=_i((walls or {}).get("value")), square=bool(square),
        stance=posture, stance_pct=_i((stance or {}).get("value")), overwatch=count))
    return True


def _approach(script: _Script, payload: dict, attacker, defender,
              battle_result: dict, reinforcements: Dict[str, list],
              facts: dict, player_side: Optional[str]) -> None:
    region = str(payload.get("region", "") or "")
    script.add("approach", _beat(
        "open", "attacker", attacker.name,
        script.said("open",
                    "{a} attacks {d} at {r}.",
                    "{a} moves against {d} at {r}.",
                    "{a} brings {d} to battle at {r}.",
                    a=_n(attacker.name), d=_n(defender.name), r=region)),
        named=(defender.name,))
    # BA-2 (§15.5.5): the plan the player's orders amount to, named first.
    dispositions_told = _plan(script, attacker, defender, battle_result,
                              reinforcements, facts, player_side)

    cut_names = set(battle_result.get("last_hour") or ())
    for side in ("attacker", "defender"):
        lead = attacker if side == "attacker" else defender
        for row in reinforcements.get(side) or []:
            if not isinstance(row, dict) or not row.get("arrived"):
                continue
            name = str(row.get("marshal", "") or "")
            origin = str(row.get("origin", "") or "")
            score, bar = _i(row.get("score")), _i(row.get("threshold"))
            margin = score - bar
            late = arrived_at_the_last_hour(row)
            # The roll's own figures, the province he marched from, his
            # orders and his court's doctrine are the marching side's to
            # read; the other side's corps is seen to come, and to come
            # late, never whence, by how much or why.
            own = bool(player_side) and side == player_side
            ordered = own and bool(row.get("has_explicit_order") or row.get("arrived_via_support"))
            doctrine = (str(row.get("doctrine", "") or "")
                        if own and row.get("doctrine_arrived") else "")
            whence = f" from {origin}" if own and origin and origin != region else ""
            f = {"n": _n(name), "w": whence, "s": score, "b": bar,
                 "l": _n(lead.name), "k": doctrine, "who": name}
            # Row BA, BA-4 (§15.5.7): what the last hour cost him, where the
            # resolver cut it (`battle_result["last_hour"]`) — told to a party
            # to the battle of either side's corps: that he came late is told
            # already, and the three quarters are the game's rule, not his roll.
            cut = (LAST_HOUR_WEIGHT_LINE if player_side and name in cut_names else "")
            if late and own:
                text = script.said(
                    "arrive_late_own",
                    # (BA-5, the second reading: "58 against a bar of 55" read as jargon)
                    "{n} comes up{w} at the last hour (his march: {s}, where {b} was needed).",
                    "{n} reaches the field{w} at the last hour (his march: {s}, where {b} was needed).",
                    "{n} comes up late{w}, but in time (his march: {s}, where {b} was needed).", **f) + cut
            elif late:
                text = script.said(
                    "arrive_late", "{n} comes up at the last hour.",
                    "{n} reaches the field at the last hour.",
                    "{n} comes up late, but in time.", **f) + cut
            elif doctrine:
                text = f"{_n(name)} arrives{whence}: {doctrine} brought him in time."
            elif ordered:
                text = script.said(
                    "arrive_ordered",
                    "{n} marches{w} to join {l}, as ordered.",
                    "{n} comes{w} to {l}'s side, as ordered.", **f)
            else:
                text = script.said(
                    "arrive_guns",
                    "{n} marches{w} to the sound of the guns.",
                    "{n} comes{w} to the sound of the guns.",
                    "{n} hurries{w} toward the firing.", **f)
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
    # (his own dispositions were told by the plan: the same works are not
    # told twice)
    if clauses and not dispositions_told:
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
        text = script.said(
            "battery",
            "{g}'s guns open on {d}'s line: {x:,} fall before the assault.",
            "{g}'s battery plays on {d}'s line: {x:,} fall before the assault.",
            "{g}'s guns speak against {d}'s line: {x:,} fall before the assault.",
            who=gunner, g=_n(gunner), d=_n(defender.name), x=dealt)
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
        alt = (_ADVANCE_ALT if lines is _ADVANCE else _RECEIVE_ALT)[temper]
        script.add("assault", _beat(
            "advance", side, lead.name,
            script.said("advance_" + side, lines[temper], *alt,
                        who=lead.name, a=_n(lead.name), f=figure),
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


def a_rout_is_one_this_battle_made() -> bool:
    """Row BA, BA-5 seam (the session's review, a defect older than the row):
    a corps is told as breaking only where THIS battle drove it off. The turn's
    retreat flag (`retreated_this_turn`) is set by any earlier retreat and
    survives the enemy phase: a corps thrown back in the player's phase and
    then attacked, holding, was told "Ney's line breaks at 70% morale" and
    "Ney falls back on …" over a table whose verdict named no broken line. The
    corps that had retreated before the battle (`facts["retreated_before"]`,
    noted at its muster) are read by this battle's own result. Down (False):
    the flag alone, as before."""
    return True


def _fate_of(world, name: str, lead_broke: bool, origins: dict, region: str,
             retreated_before=()):
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
    retreated = bool(getattr(marshal, "retreated_this_turn", False))
    if (retreated and a_rout_is_one_this_battle_made() and name in retreated_before
            and here == region):
        # (the review) driven off BEFORE this battle and still on its ground: it
        # held. One that is no longer where the battle was fought was moved by it.
        retreated = False
    if retreated or lead_broke:
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
        text = script.said(
            "dice",
            "The fortune of the day: {p}: {m}.",
            "The dice are thrown: {p}: {m}.",
            "The day's fortune is cast: {p}: {m}.",
            p=", ".join(parts), m=modified)
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
            how, _where = _fate_of(world, name, is_lead and lead_broke, origins, region,
                                   set(facts.get("retreated_before") or ()))
            if is_lead and c.get("status") == "destroyed":
                how = how or "destroyed"
            fates[name] = how
            if how in ("routed", "shattered", "destroyed", "captured"):
                broke_any = True
                morale = _i(side_result.get("morale")) if is_lead else -1
                words = {
                    "routed": (script.said(
                        "break", "{n}'s line breaks at {m}% morale.",
                        "{n}'s line gives way at {m}% morale.",
                        "{n}'s regiments break at {m}% morale.",
                        who=name, n=_n(name), m=morale)
                               if morale >= 0 else script.said(
                        "break_corps", "{n}'s corps gives way.",
                        "{n}'s corps breaks and quits the ground.",
                        who=name, n=_n(name))),
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
            "stand", "", "",
            script.said("stand",
                        "Neither line gives way: the day hangs.",
                        "Neither side yields: the day hangs.",
                        "The lines hold, and the day hangs."),
            weight="head"))
    return fates


def _named_moments(script: _Script, attacker, defender, battle_result: dict,
                   reinforcements: Dict[str, list], facts: dict) -> None:
    """BA-3 (ruling 12): the few NAMED MOMENTS, each told only when its
    condition holds and only where the narration varies (a served campaign on
    a rolled seed) — read from the battle's own result and the muster rows the
    script is already handed. None carries a figure, a province or a road the
    ordinary beats do not already tell all three fog cases, so each stands in
    all three (the dice and the late arrival are told to a watcher already;
    the ground is the map's own)."""
    if not script.varies():
        return
    outcome = str(battle_result.get("outcome") or "")
    victor = str(battle_result.get("victor") or "")
    winning = ("attacker" if victor == attacker.name else
               "defender" if victor == defender.name else "")
    an, dn = _n(attacker.name), _n(defender.name)
    leads = {"attacker": attacker, "defender": defender}

    if winning:
        for row in reinforcements.get(winning) or []:
            if not isinstance(row, dict) or not row.get("arrived"):
                continue
            margin = _i(row.get("score")) - _i(row.get("threshold"))
            name = str(row.get("marshal", "") or "")
            if name and 0 < margin <= LAST_HOUR_MARGIN:
                lead = leads[winning]
                # `victor` is set on a battle won ON POINTS too — the very
                # outcome a great battle's day hangs on: "The day is won"
                # stood over "THE DAY HANGS" (BA3-X12, the review). The
                # siblings below say "on points"; so does this one.
                late = (("{n}, come up at the last hour, carries the day for {l}.",
                         "The day is won by {n}'s arrival at the last hour.")
                        if outcome in ("attacker_victory", "defender_victory") else
                        ("{n}, come up at the last hour, gives {l} the day on points.",
                         "{n}'s arrival at the last hour tips the day to {l}, on points."))
                script.add("crisis", _beat(
                    "moment_late_arrival", winning, name,
                    script.said("moment_late_arrival", *late,
                                who=name, n=_n(name), l=_n(lead.name)),
                    weight="detail"), named=(lead.name,))
                break

    roll = battle_result.get("attacker_roll") or {}
    if isinstance(roll, dict):
        attacker_won = outcome.startswith("attacker_")
        if roll.get("is_critical_success") and not attacker_won:
            script.add("crisis", _beat(
                "moment_twelve", "attacker", attacker.name,
                script.said("moment_twelve",
                            "Twelve on the dice, and still the day is not {a}'s.",
                            "{a} throws twelve, and it is not enough.", a=an),
                weight="detail"))
        elif roll.get("is_critical_failure") and attacker_won:
            # The same sweep (BA3-X12): a two that won on points did not carry the day.
            two = (("Two on the dice, and {a} carries the day nonetheless.",
                    "{a} throws two, and wins all the same.")
                   if outcome == "attacker_victory" else
                   ("Two on the dice, and {a} still wins the day on points.",
                    "{a} throws two, and has the better of the day all the same."))
            script.add("crisis", _beat(
                "moment_two", "attacker", attacker.name,
                script.said("moment_two", *two, a=an),
                weight="detail"))

    flank = _i(battle_result.get("flanking_bonus")) or _i(facts.get("flanking_bonus"))
    if flank > 0 and outcome == "attacker_tactical_victory":
        script.add("crisis", _beat(
            "moment_flank", "attacker", attacker.name,
            script.said("moment_flank",
                        "The turned flank tells: {a} wins the day on points.",
                        "It is the flank that decides it: {a} wins the day on points.",
                        a=an),
            weight="detail"))

    if outcome == "mutual_destruction":
        script.add("crisis", _beat(
            "moment_ruin", "", "",
            script.said("moment_ruin",
                        "Both armies are ruined on the field: there is no victor.",
                        "Both armies are spent: no one holds the field."),
            weight="detail"))

    terrain = _row(_rows(battle_result, "defender"), "Terrain (")
    if terrain and outcome == "defender_tactical_victory":
        ground = str(terrain.get("label", ""))[len("Terrain ("):].rstrip(")").lower()
        script.add("crisis", _beat(
            "moment_ground", "defender", defender.name,
            script.said("moment_ground",
                        "The ground tells: {d} stands {g} and wins the day on points.",
                        "It is the ground that decides it: {d} stands {g} and wins on points.",
                        d=dn, g=_GROUND.get(ground, f"on {ground} ground")),
            weight="detail"))


def _pursuit(script: _Script, world, payload: dict, attacker, defender,
             battle_result: dict, facts: dict, fates: Dict[str, str],
             player_nation: str, player_side: Optional[str]) -> None:
    damage = _i(battle_result.get("pursuit_damage"))
    if damage > 0:
        ability = (getattr(attacker, "ability", None) or {}).get("name", "")
        # Row BA, BA-4 (§15.5.7): the corps that pursued when it is not the
        # lead — one that fought beside him. Named where the table seats him;
        # a corps of the reserve has no plinth to move, so the lead's line
        # tells it and names no man the table does not show.
        pursuer = str(battle_result.get("pursuer") or "")
        actor, who = attacker.name, _n(attacker.name)
        if pursuer:
            ability = str(battle_result.get("pursuer_ability") or "")
            if pursuer in script.shown:
                actor, who = pursuer, _n(pursuer)
            elif player_side == "attacker":
                # the player's own corps: his name is the player's to read,
                # seated or not (the lead's plinth still makes the move)
                who = f"{_n(pursuer)}, from the reserve,"
            else:
                # another crown's corps the table does not show: not his
                # name, and not the ability only he holds
                who, ability = f"{_n(attacker.name)}'s reserve", ""
        screened = (getattr(defender, "ability", None) or {}).get("name", "") == "The Old Fox"
        text = script.said(
            "pursue",
            "{a} rides them down{b}: {x:,} more.",
            "{a} presses the pursuit{b}: {x:,} more.",
            "{a} hangs on their rear{b}: {x:,} more.",
            a=who, b=f" ({ability})" if ability else "", x=damage)
        if screened:
            text += f" {_n(defender.name)}'s rearguard screened the retreat and halved the harvest."
        script.add("pursuit", _beat(
            "pursue", "attacker", actor, text, weight="head",
            damage=damage, halved=screened, target=defender.name),
            named=(defender.name,))

    # Row BA, BA-5: the reserve pursues a beaten enemy (a day of battle) — the
    # victor's lead makes the move; the figure is the beaten lead's own loss,
    # which the battle's report gives to the player who fought it.
    reserve = battle_result.get("reserve_pursuit")
    if isinstance(reserve, dict) and _i(reserve.get("men")) > 0:
        beaten_is_defender = reserve.get("side") == "defender"
        victor, beaten = (attacker, defender) if beaten_is_defender else (defender, attacker)
        points = _i(reserve.get("points"))
        held = "one point" if points == 1 else f"{points} points"
        text = (f"{_n(victor.name)}'s reserve pursues — {held} in hand more than "
                f"{_n(beaten.name)} kept: {_i(reserve.get('men')):,} more of his.")
        script.add("pursuit", _beat(
            "pursue", "attacker" if beaten_is_defender else "defender", victor.name, text,
            weight="head", damage=_i(reserve.get("men")), reserve=True, target=beaten.name),
            named=(beaten.name,))

    region = str(payload.get("region", "") or "")
    origins = facts.get("reinforcer_origin") or {}
    for side in ("attacker", "defender"):
        for c in (payload.get(side) or {}).get("contingents") or []:
            name = str(c.get("name", "") or "")
            how = fates.get(name, "")
            if not how or how in ("destroyed", "captured"):
                continue
            _how, where = _fate_of(world, name, how == "routed", origins, region,
                                   set(facts.get("retreated_before") or ()))
            # An enemy's road off the field is his own intelligence; ours is ours.
            marshal = (getattr(world, "marshals", None) or {}).get(name)
            own = getattr(marshal, "nation", "") == player_nation
            to = where if (own and where and where != region) else ""
            f = {"who": name, "n": _n(name), "to": to}
            if how == "withdrew":
                text = (script.said(
                    "leave_withdrew_to", "{n} withdraws to {to} after the battle.",
                    "{n} draws back to {to} once the battle is done.", **f) if to
                        else script.said(
                    "leave_withdrew", "{n} draws off after the battle.",
                    "{n} quits the field once the battle is done.", **f))
            else:
                text = (script.said(
                    "leave_to", "{n} falls back on {to}.",
                    "{n} retires on {to}.", **f) if to
                        else script.said(
                    "leave", "{n} leaves the field.",
                    "{n} quits the field.", **f))
            script.add("pursuit", _beat("leave", side, name, text, how=how, to=to))

    advanced = str(facts.get("advanced_to") or "")
    if advanced:
        # A narrow day leaves both armies in the province ("Both armies
        # remain in the field" is the battle's own line): say so, or "the
        # day hangs" followed by an advance reads as a contradiction.
        foe = (getattr(world, "marshals", None) or {}).get(defender.name)
        before = set(facts.get("retreated_before") or ()) if a_rout_is_one_this_battle_made() else set()
        stands = bool(
            foe is not None and _i(getattr(foe, "strength", 0)) > 0
            and not getattr(foe, "captured_by", "")
            and not (getattr(foe, "retreated_this_turn", False) and defender.name not in before)
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

    script = _Script(shown, world, (
        attacker.name, defender.name, str(payload.get("region", "") or ""),
        _i(getattr(world, "current_turn", 0))))
    muster = {"attacker": attacker_reinforcements or [],
              "defender": defender_reinforcements or []}
    _approach(script, payload, attacker, defender, battle_result, muster,
              facts, player_side)
    word = facts.get("day_word")
    if isinstance(word, dict) and word.get("line"):
        # The day's word (battle_day.word_line): a fact of the battle, not a
        # variant; its line names only who came on, so it is fog-safe as given.
        script.acts["approach"].insert(0, _beat(
            "word", "", "", str(word["line"]), weight="head",
            who=str(word.get("who", "") or ""), word=str(word.get("kind", "") or "")))
    _cannonade(script, attacker, defender, battle_result, facts, player_side)
    _assault(script, attacker, defender, battle_result, player_side)
    fates = _crisis(script, world, payload, attacker, defender, battle_result,
                    facts, player_nation, player_side)
    _named_moments(script, attacker, defender, battle_result, muster, facts)
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


# ─────────────────────────────────────────────────────────────────────────────
# Row BA, session BA-2 — the walls and the guns (BATTLE_DIORAMA_SPEC §15.5.4)
#
# The payloads are `siege_diorama`'s. The fog case of every beat below was
# decided before it was written (SYSTEMS_REFERENCE §219.2):
#
#   the assault     open, walls, storm, wall_holds / wall_falls / capitulates,
#                   province, occupy, repulsed — ALL THREE cases: who came
#                   before the walls, what the walls did and whose the
#                   province is now are what the field showed, and the
#                   garrison's numbers are the assault's own report (the
#                   enemy phase prints "N lost, M still under arms").
#                   drilled, ability — case 1 only: the storming side's own
#                   rows; the enemy's are never told.
#   the cannonade   battery, destroyed — all three: who fired on whom, and
#                   who was destroyed. The battery's own losses, the province
#                   it fired from, bystander, works and shaken — cases 1 and
#                   2 (a party's own report prints each of them: "X fires
#                   from A on Y", "return fire", "Fort degraded", "morale");
#                   never to a watcher.
# ─────────────────────────────────────────────────────────────────────────────

def _script_out(script: _Script, payload: dict, tempers: Dict[str, str],
                whole: bool = False) -> dict:
    full = bool(whole or payload.get("great_battle") or payload.get("dramatic"))
    return {
        "version": 1,
        "form": "full" if full else "brief",
        "acts": [{"act": act, "beats": script.acts[act]}
                 for act in ACTS if script.acts[act]],
        "tempers": tempers,
    }


def build_assault_script(world, payload: dict, marshal,
                         facts: Optional[dict] = None) -> dict:
    """The script of one garrison assault: the approach, the storm, what the
    wall did, and the province. No cannonade and no dice — the exchange at a
    wall is not rolled (`CombatExecutor.garrison_exchange`)."""
    facts = facts if isinstance(facts, dict) else {}
    player_side = payload.get("player_side")
    region = _n(str(payload.get("region", "") or ""))
    fate = str(payload.get("fate", "") or "held")
    garrison = (((payload.get("defender") or {}).get("contingents") or [{}])[0]) or {}
    walls = str(garrison.get("name", "") or "")
    name = marshal.name
    script = _Script({name, walls})

    script.add("approach", _beat(
        "open", "attacker", name,
        f"{_n(name)} comes up before the walls of {region}."), named=(walls,))
    men = _i(garrison.get("committed"))
    script.add("approach", _beat(
        "walls", "defender", walls,
        f"The garrison of {region} mans its walls"
        f"{', under the fortress' if payload.get('fortified') else ''}: {_men(men)}.",
        weight="head" if player_side == "defender" else "detail",
        men=men, fortified=bool(payload.get("fortified"))))

    script.add("assault", _beat(
        "storm", "attacker", name,
        f"{_n(name)}'s columns go in against the walls with ladders.",
        weight="head", temper=temper_of(marshal)), named=(walls,))
    if player_side == "attacker":
        drilled = _i(facts.get("drilled")) * 10
        if drilled > 0:
            script.add("assault", _beat(
                "drilled", "attacker", name,
                f"{_n(name)}'s drilled battalions go in as one (+{drilled}%).",
                weight="head", pct=drilled, penalty=False))
        iron = _i(facts.get("iron_pct"))
        if iron > 0:
            script.add("assault", _beat(
                "ability", "attacker", name,
                f"{_n(name)}'s coiled resolve is released: Iron Resolve (+{iron}%).",
                weight="head", ability="Iron Resolve", pct=iron))

    left = _i(garrison.get("remaining"))
    if fate == "held":
        script.add("crisis", _beat(
            "wall_holds", "defender", walls,
            f"The walls of {region} hold: {_men(left, 'defender', 'defenders')} "
            f"remain{'s' if left == 1 else ''}.",
            weight="head", remaining=left, lost=_i(garrison.get("casualties"))))
    elif fate == "capitulated":
        script.add("crisis", _beat(
            "capitulates", "defender", walls,
            f"The garrison of {region} lays down its arms.", weight="head"))
    else:
        script.add("crisis", _beat(
            "wall_falls", "defender", walls,
            f"The walls of {region} are carried: the garrison is overrun.",
            weight="head"))

    if payload.get("region_conquered"):
        line = str(payload.get("liberation_line", "") or "")
        if not line:
            victor = display_nation(str(payload.get("attacker_nation", "") or ""))
            line = f"{region} falls to {victor}." if victor else f"{region} changes hands."
        script.add("pursuit", _beat(
            "province", "attacker", name, line, weight="head", region=region))
    elif fate != "held" and payload.get("sub_banner"):
        script.add("pursuit", _beat(
            "occupy", "attacker", name, str(payload["sub_banner"]), weight="head",
            turns=_i(payload.get("siege_turns"))))
    elif fate == "held":
        attacker = (((payload.get("attacker") or {}).get("contingents") or [{}])[0]) or {}
        lost = _i(attacker.get("casualties"))
        script.add("pursuit", _beat(
            "repulsed", "attacker", name,
            f"{_n(name)} draws off from the walls"
            + (f", {_men(lost)} the fewer." if lost > 0 else "."),
            lost=lost))

    return _script_out(script, payload, {name: temper_of(marshal), walls: "steady"})


def build_bombardment_script(world, payload: dict, battery, target, br: dict) -> dict:
    """The script of one standalone bombardment: the cannonade alone."""
    br = br if isinstance(br, dict) else {}
    player_side = payload.get("player_side")
    gunner, struck = battery.name, target.name
    shown = {str(c.get("name", "") or "")
             for side in ("attacker", "defender")
             for c in ((payload.get(side) or {}).get("contingents") or [])}
    script = _Script(shown)
    dealt = _i((br.get("defender") or {}).get("casualties"))
    taken = _i((br.get("attacker") or {}).get("casualties"))
    left = _i((br.get("defender") or {}).get("remaining"))
    party = bool(player_side)

    at = str(payload.get("battery_at", "") or "")
    whence = f" from {at}" if party and at and at != str(payload.get("region", "") or "") else ""
    text = f"{_n(gunner)}'s guns open{whence} on {_n(struck)}: {_fall(dealt)}."
    if party and taken > 0:
        text += f" The answering fire costs the battery {taken:,}."
    script.add("cannonade", _beat(
        "battery", "attacker", gunner, text, weight="head",
        dealt=dealt, target=struck, **({"taken": taken} if party else {})),
        named=(struck,))

    if party:
        for c in (payload.get("defender") or {}).get("contingents") or []:
            if not c.get("bystander"):
                continue
            other, lost = str(c.get("name", "") or ""), _i(c.get("casualties"))
            ours = bool(c.get("friendly_fire")) and player_side == "attacker"
            script.add("cannonade", _beat(
                "bystander", "defender", other,
                (f"Our own {_n(other)}, standing by, is caught under the guns: {_fall(lost)}."
                 if ours else
                 f"{_n(other)}'s corps, standing by, is caught in the fire: {_fall(lost)}."),
                weight="head" if ours else "detail", lost=lost, ours=ours))
        if br.get("fort_degraded"):
            old, new = _i(br.get("fort_old")), _i(br.get("fort_new"))
            script.add("cannonade", _beat(
                "works", "defender", struck,
                (f"{_n(struck)}'s works are levelled." if new <= 0 else
                 f"{_n(struck)}'s works come down from {old}% to {new}%."),
                weight="head", old=old, new=new))
    if left <= 0:
        script.add("cannonade", _beat(
            "destroyed", "defender", struck,
            f"{_n(struck)}'s corps is destroyed under the guns.", weight="head"))
    elif party:
        morale = _i((br.get("defender") or {}).get("morale"))
        script.add("cannonade", _beat(
            "shaken", "defender", struck,
            f"{_n(struck)}'s line stands under the fire at {morale}% morale.",
            morale=morale))

    # A cannonade is ONE act of a few beats: it is told whole. The brief form
    # keeps one head beat an act, which here would leave out the works coming
    # down and our own corps caught under our own guns.
    return _script_out(script, payload, {n: "steady" for n in shown if n}, whole=True)
