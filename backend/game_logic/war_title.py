"""The war's title — PC-R7 (i), ruling J of the peace report
(`docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §40 J / §46, decided October 16,
2026; built S13e part 4, October 17, 2026; rules `SYSTEMS_REFERENCE.md` §127).

A war is titled by its PURPOSE — the stake — on every surface: "War for
Bohemia", never "France vs Britain". The leader pair misnamed the war the
player was fighting (PC-F41: the Third Coalition's war read "vs Britain" on
a board where Britain was 1 % of the war's weight and Austria had lost
Bohemia, Vienna and Tyrol; PC-F78: a settlement letter "to settle France vs
Britain" ended France's war with Prussia). ONE builder, `war_title`, read by
the HUD card, the war popup, the wizard, the dispatch, the Charges, the
settlement table's heading, the settlement letters, the petitions and the
payment records — so the table titles the same object the card does.

The ladder (from the chair's view; the first rung that names a stake wins):

  purpose   the chair's NAMED purpose against a court of the war (any type
            but the declaration's default `defense`): conquest → "War for
            Munich" (its first target), subjugation → "War for the submission
            of Austria", forced_alliance → "War for Austria's alliance",
            liberation → "War for the liberation of Holland";
  design    an AI-initiated war's stated reason — the design's own title
            ("War for the Hanoverian Prize", "War for Primacy in Germany");
  theirs    an enemy court's NAMED purpose against the chair (its design's
            ground is the stake from both chairs);
  ground    the ground in play: the enemy courts' home provinces the chair's
            side holds and the chair's side's home provinces they hold — the
            title names the first taken (the conquest title's turn, then the
            name; a capital after its provinces, as at Pressburg), the line
            names them all ("War for Bohemia"; "War for Paris" when they hold
            ours and we hold none of theirs);
  league    nothing held and nothing named: a league's war is titled by the
            league ("War with the Third Coalition");
  court     else by the court ("War with Austria").

`roster` is WHO (the enemy courts at war with the chair, leader first), kept
beside the title on the tooltip and the table's heading — the ruling retires
the pair as the NAME, not the information. GR6: deterministic text from the
board. Pure reads; nothing is written."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from backend.errors import report
from backend.game_logic.formations import formed_display_name

# A purpose type's title, by the court it is set against.
_PURPOSE_TITLES = {
    "subjugation": "War for the submission of {court}",
    "forced_alliance": "War for {court}'s alliance",
    "liberation": "War for the liberation of {court}",
}


def _instance(world, war_id: str) -> Dict[str, Any]:
    inst = (getattr(world, "war_instances", None) or {}).get(str(war_id or ""))
    return inst if isinstance(inst, dict) else {}


def _active_war_id_for(world, chair: str, court: str) -> str:
    from backend.game_logic.settlement_helpers import _find_active_war_instance_for_pair
    return str(_find_active_war_instance_for_pair(world, world._make_diplo_key(chair, court)) or "")


def _enemy_courts(world, instance: Dict[str, Any], chair: str) -> List[str]:
    """The courts on the other side still at WAR (or in truce) with the chair,
    the side's leader first, then the instance's order."""
    side_by_nation = instance.get("side_by_nation") or {}
    my_side = side_by_nation.get(chair)
    if my_side not in ("attackers", "defenders"):
        return []
    enemy_side = "defenders" if my_side == "attackers" else "attackers"
    leader = str(instance.get("defender_leader" if enemy_side == "defenders" else "attacker_leader") or "")
    courts = []
    for nation in list(instance.get(enemy_side) or []):
        nation = str(nation)
        if nation == chair or side_by_nation.get(nation) != enemy_side:
            continue
        if world.get_diplomatic_state(chair, nation) not in ("WAR", "ARMISTICE"):
            continue
        courts.append(nation)
    if leader in courts:
        courts.remove(leader)
        courts.insert(0, leader)
    return courts


def _our_side(world, instance: Dict[str, Any], chair: str) -> List[str]:
    side_by_nation = instance.get("side_by_nation") or {}
    my_side = side_by_nation.get(chair)
    if my_side not in ("attackers", "defenders"):
        return [chair]
    ours = [str(n) for n in (instance.get(my_side) or []) if side_by_nation.get(str(n)) == my_side]
    if chair not in ours:
        ours.insert(0, chair)
    return ours


def _named_purpose(world, owner: str, against: str) -> Optional[Dict[str, Any]]:
    pair = (getattr(world, "war_objectives", {}) or {}).get(world._make_diplo_key(owner, against), {}) or {}
    obj = pair.get(owner) if isinstance(pair, dict) else None
    if not isinstance(obj, dict) or obj.get("concluded_turn") is not None:
        return None
    if str(obj.get("type") or "") in ("", "defense"):
        return None
    return obj


def _purpose_title(world, obj: Dict[str, Any], against: str) -> Tuple[str, List[str]]:
    otype = str(obj.get("type") or "")
    targets = [str(r) for r in (obj.get("target_regions") or []) if r]
    if otype in _PURPOSE_TITLES:
        target_court = str(obj.get("target_nation") or against)
        return _PURPOSE_TITLES[otype].format(court=formed_display_name(world, target_court)), targets
    if targets:
        return f"War for {targets[0]}", targets
    return f"War with {formed_display_name(world, against)}", targets


def _design_title(reason: str) -> str:
    text = str(reason or "").strip()
    if not text:
        return ""
    if text.lower().startswith("the "):
        text = "the " + text[4:]
    return f"War for {text}"


def _capital_of(world, nation: str) -> str:
    try:
        return str(world.get_nation_capital(nation) or "")
    except Exception as exc:  # a title is display substrate; never a crash
        report(exc, "war_title._capital_of: get_nation_capital")
        return ""


def _home_of(world, nation: str) -> List[str]:
    return [str(r) for r in ((getattr(world, "nation_starting_regions", None) or {}).get(nation, []) or [])]


def _taken_since(world, region_name: str, turn: int) -> int:
    store = getattr(world, "province_title", None)
    rec = (store or {}).get(region_name) if isinstance(store, dict) else None
    if isinstance(rec, dict) and rec.get("kind") == "conquest":
        return int(rec.get("since", turn) or turn)
    return int(turn)


def _ground(world, holders: List[str], owners: List[str]) -> List[Tuple[int, int, str, str]]:
    """The home provinces of `owners` that `holders` hold, as (turn taken,
    capital-last, name, owner) — sortable, the first taken first."""
    turn = int(getattr(world, "current_turn", 0) or 0)
    holder_set = set(holders)
    out: List[Tuple[int, int, str, str]] = []
    for owner in owners:
        capital = _capital_of(world, owner)
        for region_name in _home_of(world, owner):
            region = world.regions.get(region_name)
            if region is None or str(getattr(region, "controller", "") or "") not in holder_set:
                continue
            out.append((_taken_since(world, region_name, turn), 1 if region_name == capital else 0,
                        region_name, owner))
    return sorted(out)


def _ground_rung(world, ground) -> List[Tuple[int, int, str, str]]:
    """S14E-D4 / S14E-31 (Pre-Deploy S14f part 1, October 24, 2026): the
    ground that may TITLE the war — ruling J set no floor, so one 6,500-man
    beachhead on Munster renamed a seven-power war "War for Munster". The
    floor: an owner's ground names the war when the holders have its
    CAPITAL, TWO OR MORE of its home provinces, or A QUARTER of them (one of
    a four-province minor's is a quarter; one of Britain's or Hanover's six
    is not). Below the floor the league or the court titles the war and the
    line still names what is held (the ground is read always). Returns the
    rows of `ground` whose owner meets the floor, in `ground`'s own order."""
    if not ground:
        return []
    held_by_owner: Dict[str, List[str]] = {}
    for _t, _c, name, owner in ground:
        held_by_owner.setdefault(owner, []).append(name)
    passing = set()
    for owner, held in held_by_owner.items():
        home = _home_of(world, owner)
        capital = _capital_of(world, owner)
        if (capital and capital in held) or len(held) >= 2 or not home \
                or len(held) * 4 >= len(home):
            passing.add(owner)
    return [row for row in ground if row[3] in passing]


def _names(regions: List[str]) -> str:
    if not regions:
        return ""
    if len(regions) == 1:
        return regions[0]
    return ", ".join(regions[:-1]) + " and " + regions[-1]


def war_title(world, war_id: str = "", *, chair: Optional[str] = None,
              court: Optional[str] = None) -> Dict[str, Any]:
    """The ONE title of a war from `chair`'s view (the player's by default).
    `war_id` names the instance; with `court` alone the pair's active
    instance is found, and the ground read is that court's. Returns
    {title, source, stake, theirs_we_hold, ours_they_hold, roster,
    roster_display, display, line} — `display` is "War for Bohemia — Austria
    + Britain + Russia" (the title, then who), `line` the sentence ("The War
    for Bohemia: France holds Bohemia, Tyrol and Vienna of Austria's.")."""
    chair = str(chair or getattr(world, "player_nation", "France"))
    war_id = str(war_id or "")
    if not war_id and court:
        war_id = _active_war_id_for(world, chair, str(court))
    instance = _instance(world, war_id)
    enemies = _enemy_courts(world, instance, chair) if instance else []
    if court and str(court) not in enemies:
        enemies = [str(court)] + enemies
    ours = _our_side(world, instance, chair) if instance else [chair]
    roster = enemies if not court else [str(court)]
    roster_display = " + ".join(formed_display_name(world, n) for n in roster)
    out: Dict[str, Any] = {
        "war_id": war_id, "chair": chair, "title": "", "source": "", "stake": [],
        "theirs_we_hold": [], "ours_they_hold": [], "roster": list(roster),
        "roster_display": roster_display, "display": "", "line": "",
    }
    # 1. the chair's named purpose — an AI design war's purpose carries its
    # design (`war_council` stamps `design` and the design's provinces on
    # the objective), and is titled by the design's own name
    reason = str(instance.get("stated_reason") or "") if instance else ""
    for against in enemies:
        obj = _named_purpose(world, chair, against)
        if obj:
            if obj.get("design") and reason:
                out.update(title=_design_title(reason), source="design",
                           stake=[str(r) for r in (obj.get("target_regions") or []) if r])
            else:
                title, targets = _purpose_title(world, obj, against)
                out.update(title=title, source="purpose", stake=targets)
            break
    # 2. an AI-initiated war's design
    if not out["title"]:
        title = _design_title(str(instance.get("stated_reason") or "")) if instance else ""
        if title:
            out.update(title=title, source="design", stake=[])
    # 3. an enemy court's named purpose against the chair
    if not out["title"]:
        for against in enemies:
            obj = _named_purpose(world, against, chair)
            if obj:
                title, targets = _purpose_title(world, obj, chair)
                out.update(title=title, source="theirs", stake=targets)
                break
    # the ground in play (read always: the line names it on every rung).
    # What WE hold of theirs is a prize, named by the campaign that took it
    # (the first taken; a capital after the provinces of its turn — Pressburg
    # names Bohemia, not Vienna); what THEY hold of ours is a wound, named by
    # its gravest (the capital first — a France that lost Paris fights the
    # War for Paris, whatever fell before it).
    # S14E-D4 / S14E-31: a `court=` read is THAT court's ground — what we
    # hold of hers and what she holds of ours — as the docstring has always
    # said (the Austrian truce row named Britain's Irish province).
    ground_enemies = [str(court)] if court else enemies
    theirs = _ground(world, ours, ground_enemies)
    mine = sorted(_ground(world, ground_enemies, ours), key=lambda r: (-r[1], r[0], r[2]))
    out["theirs_we_hold"] = [name for _t, _c, name, _o in theirs]
    out["ours_they_hold"] = [name for _t, _c, name, _o in mine]
    if not out["title"]:
        # 4. the ground — above the floor (`_ground_rung`): the capital, two
        # provinces or a quarter of the owner's home; a lone beachhead
        # leaves the league or the court its title
        prize = _ground_rung(world, theirs)
        wound = _ground_rung(world, mine)
        if prize:
            out.update(title=f"War for {prize[0][2]}", source="ground",
                       stake=list(out["theirs_we_hold"]))
        elif wound:
            out.update(title=f"War for {wound[0][2]}", source="ground",
                       stake=list(out["ours_they_hold"]))
    # 5–6. the league, else the court
    if not out["title"]:
        coalition = getattr(world, "active_coalition", None) or {}
        members = set(coalition.get("members") or []) if isinstance(coalition, dict) else set()
        name = str(coalition.get("name") or "") if isinstance(coalition, dict) else ""
        if name and enemies and set(enemies) & members and not court:
            out.update(title=f"War with the {name}" if not name.lower().startswith("the ") else f"War with {name}",
                       source="league")
        elif roster:
            out.update(title=f"War with {formed_display_name(world, roster[0])}", source="court")
        else:
            out.update(title="War", source="none")
    out["display"] = f"{out['title']} — {roster_display}" if roster_display else out["title"]
    out["line"] = _line(world, out, chair, enemies, theirs, mine)
    return out


def _line(world, out: Dict[str, Any], chair: str, enemies: List[str],
          theirs, mine) -> str:
    chair_d = formed_display_name(world, chair)
    parts: List[str] = []
    if theirs:
        by_owner: Dict[str, List[str]] = {}
        for _t, _c, name, owner in theirs:
            by_owner.setdefault(owner, []).append(name)
        parts.append(f"{chair_d} holds " + "; ".join(
            f"{_names(regions)} of {formed_display_name(world, owner)}'s"
            for owner, regions in by_owner.items()))
    if mine:
        by_holder: Dict[str, List[str]] = {}
        for _t, _c, name, owner in mine:
            holder = str(getattr(world.regions.get(name), "controller", "") or "")
            by_holder.setdefault(holder, []).append(name)
        parts.append("; ".join(
            f"{formed_display_name(world, holder)} holds {_names(regions)} of ours"
            for holder, regions in by_holder.items()))
    if out["source"] in ("purpose", "theirs") and out["stake"]:
        parts.insert(0, f"the purpose names {_names(out['stake'])}")
    elif out["source"] == "design":
        parts.insert(0, "the design that declared it")
    if not parts:
        parts.append("nothing taken yet on either side")
    return f"The {out['title']}: " + "; ".join(parts) + "."


def war_title_for_pair(world, chair: str, court: str) -> Dict[str, Any]:
    """The title of the war `chair` and `court` are in, from the chair's view
    (the pair's active instance; the roster is the whole enemy side)."""
    return war_title(world, _active_war_id_for(world, chair, court), chair=chair)


def settlement_war_label(world, war_id: str, *, chair: Optional[str] = None) -> str:
    """The label the settlement package's sentences wrap ("the settlement of
    {war_label}", "to settle {war_label}", "Settlement offer: {war_label}"):
    the title WITH its article, then who — "the War for Bohemia — Britain +
    Austria + Russia". The war card's title stays bare ("War for Bohemia")."""
    rec = war_title(world, war_id, chair=chair)
    return f"the {rec['display']}" if rec.get("title") else ""


def titled_label(world, war_id: str, *, chair: Optional[str] = None,
                 covered: Optional[List[str]] = None) -> str:
    """The settlement table's heading: the title with its article, then the
    courts the table covers ("the War for Bohemia — the table with
    Austria"), or the roster when nothing is covered. G4F-7's coverage rule
    kept under the title."""
    rec = war_title(world, war_id, chair=chair)
    names = [formed_display_name(world, str(n)) for n in (covered or []) if n]
    if names:
        return f"the {rec['title']} — the table with {' + '.join(names)}"
    return f"the {rec['display']}"
