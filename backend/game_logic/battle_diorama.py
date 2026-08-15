"""Battle Diorama (row BD) — the display-only contingents[] payload builder.

One battle -> one self-contained payload the Godot tableau renders without
fishing in any other response field. Assembled per-battle inside
`_execute_attack` (both the solo and coordinated branches feed the same
builder); never serialized on the world, never read by routing or mechanics
(Golden Rule 6).

Scope of record: `docs/audits/BATTLE_DIORAMA_EVAL_2026_07_17.md` §6 — the
bounded Tier-A slice. Field battles only (`resolve_battle` results): garrison
assaults, bombardments, and glorious-charge redirects keep their existing
surfaces and never reach this builder (documented boundary, eval §3 — those
paths compose no battle name either).

Fog contract (the eval's de-risk must #1):
- The player fought -> both sides render in full. Their corps stood on that
  field; the battle itself is the intel (`update_intel_from_battle` grants
  the region FULL at every resolve site).
- The player did NOT fight -> the payload exists only when the battle region
  is FULL-visible to the player; anything less returns None and the event
  text stands alone. (Mirrors `_filter_enemy_phase_by_visibility`'s
  FULL-or-suppress rule for third-party actions.)
- A corps that FAILED TO ARRIVE never stood on the field — knowing of it is
  intel about its own region, not the battle. Enemy no-shows therefore
  require FULL visibility of their location; the player's own no-shows
  always show (the Bernadotte drama is a player-side read).

Status vocabulary (PT-D2, Aug-1 re-measure, extends the eval §5 set):
engaged / reinforced / routed (primary pair only) / destroyed, plus the
absence family the tableau's shelf renders — `refused` (a by-design
character refusal: the literal who awaits orders, the jealous eye on a
crown — the same taxonomy the Session-61a trust dock blessed),
`failed_arrive` (he tried; the roll or fate stopped him), and
`out_of_reach` (he promised at muster but the resolve ladder dropped him —
the field moved beyond his reach). The live defect: Soult, who REFUSED to
march, rendered as `failed_arrive`; Murat, who promised and failed his
roll, was absent from the tableau entirely (muster-promise parity below).
"""

from typing import Dict, List, Optional

from backend.models.intel import FULL

# Cap per the eval's §7 Q3 answer: fixed figure blocks, summarize the tail.
MAX_CONTINGENTS_PER_SIDE = 4

# Decisive outcomes — full victories break a side; tactical wins are a
# bloodier draw. mutual_destruction is decisive in the way that matters
# to a tableau: both lines are wreckage.
_DECISIVE_OUTCOMES = (
    "attacker_victory", "defender_victory", "mutual_destruction",
)

# Short shelf labels for the no-show block — same vocabulary the
# reinforcement_messages copy uses, compressed to fit an off-baize caption.
_ABSENCE_LABELS = {
    "literal_personality": "awaits explicit orders",
    "fate_intervened": "fate intervened on the march",
    "eyes_on_a_crown": "weighed his own ambitions",
    # A5 (CA9 row 3): the tableau's parallel of the muster preview's own
    # arm. A marshal held back by a quarrel used to fall through to
    # `_ABSENCE_DEFAULT` — "could not reach the field" — which narrates
    # character as geography, the same defect A6 fixes on the dispatch side.
    "grievance_withheld": "would not march for him",
}
_ABSENCE_DEFAULT = "could not reach the field"

# PT-D2: refusal is a CHOICE, a failed arrival is not — the same line the
# Session-61a trust dock draws (it exempts by-design character refusals
# and docks only the honest failed roll).
_REFUSAL_REASONS = ("literal_personality", "eyes_on_a_crown",
                    # A5: a grievance is a CHOICE, so it belongs with the
                    # by-design refusals rather than the failed rolls —
                    # which is also what keeps the Session-61a trust dock
                    # from charging a marshal for his own sulk.
                    "grievance_withheld")

# The absence family — every status the shelf (not the line) renders.
ABSENT_STATUSES = ("failed_arrive", "refused", "out_of_reach")


def marshal_arm(marshal) -> str:
    """Dominant arm for display — the same derivation the map summary uses
    (world_state.py map-summary block): mutually-exclusive flags, cavalry
    read first. Display-only.

    NP-5 (NAPOLEON_SPEC §9): the SOVEREIGN branch runs FIRST — the emperor
    piece, never cavalry=True (that flag silently drags recklessness,
    charge mechanics and combined-arms type counts; GR6 display-only)."""
    if getattr(marshal, "is_sovereign", False):
        return "emperor"
    if getattr(marshal, "cavalry", False):
        return "cavalry"
    if getattr(marshal, "artillery", False):
        return "artillery"
    return "infantry"


def snapshot_pre_battle_strengths(atk_participants: list,
                                  def_participants: list) -> Dict[str, int]:
    """Capture every participant's strength at muster — BEFORE support
    bombardment, resolve_battle, and take_casualties mutate it. The
    contingents' `committed` figures come from here (the eval's §6
    'extend the _co6_lead_pre_strength snapshot to all participants')."""
    snapshot: Dict[str, int] = {}
    for p in list(atk_participants) + list(def_participants):
        snapshot[p.name] = int(getattr(p, "strength", 0))
    return snapshot


def _grudge_line(marshal, world) -> Optional[str]:
    """The grudge that explains the gap (eval §3: causality runs
    grudge -> no-show, never the reverse — this line only ever *explains*).
    Player-nation marshals only: enemy jealousy runs on a faction proxy
    and is not a per-marshal fact the player may read."""
    if marshal.nation != getattr(world, "player_nation", "France"):
        return None
    rival = getattr(marshal, "jealous_of", None)
    if not rival:
        return None
    # N27 (CA9): a genuine PROSE leak inside the diorama payload —
    # `jealous_of` is a raw marshal key, so this rendered "He resents
    # ArchdukeCharles's glory." Humanised HERE, backend-side; the
    # contingent's own `name` field is deliberately NOT touched, because
    # the diorama's portrait loader builds `res://assets/portraits/<name>`
    # from it and a present-set is keyed on it against `world.marshals`.
    from backend.display_names import humanize_entity_name
    return f"He resents {humanize_entity_name(str(rival))}'s glory."


def _contingent(marshal, committed: int, casualties: int, remaining: int,
                status: str, lead: bool, world) -> dict:
    entry = {
        "name": marshal.name,
        "nation": getattr(marshal, "nation", ""),
        "arm": marshal_arm(marshal),
        "committed": int(committed),
        "casualties": int(max(0, casualties)),
        "remaining": int(max(0, remaining)),
        "status": status,
        "lead": bool(lead),
        "crowned": bool(getattr(marshal, "glory_crowned", False)),
        # NP-5: the locket wears the imperial mark (its own glyph, the
        # crowned-star discipline — never minted by this battle).
        "sovereign": bool(getattr(marshal, "is_sovereign", False)),
    }
    # An assimilated ex-vassal contingent still marches under its own
    # colours — the one true mixed-standards read the engine produces
    # today (VS-4 original_nation). Display flourish only.
    origin = getattr(marshal, "original_nation", None)
    if origin and origin != entry["nation"]:
        entry["origin_nation"] = origin
    grudge = _grudge_line(marshal, world)
    if grudge:
        entry["grudge"] = grudge
    return entry


def _side_contingents(world, lead, participants: list, distribution: dict,
                      side_result: dict, reinforcements: list,
                      pre_strengths: Dict[str, int],
                      player_involved: bool) -> List[dict]:
    """One side's contingents: lead first, fought corps by weight, then the
    no-show shelf. `distribution` is empty on the solo path — the lead's
    figures come from the battle_result side dict instead."""
    player_nation = getattr(world, "player_nation", "France")
    arrived = {r.get("marshal") for r in reinforcements if r.get("arrived")}
    contingents: List[dict] = []

    fought = sorted(
        participants,
        key=lambda p: (0 if p.name == lead.name else 1,
                       -pre_strengths.get(p.name, 0)),
    )
    for p in fought:
        is_lead = p.name == lead.name
        committed = pre_strengths.get(p.name, int(getattr(p, "strength", 0)))
        if distribution:
            casualties = int(distribution.get(p.name, 0))
        elif is_lead:
            casualties = int(side_result.get("casualties", 0))
        else:
            casualties = 0
        if is_lead:
            # The leads' remaining is the battle report's own figure —
            # shown = the number every other surface already prints.
            remaining = int(side_result.get("remaining",
                                            max(0, committed - casualties)))
        else:
            remaining = max(0, committed - casualties)

        if remaining <= 0:
            status = "destroyed"
        elif is_lead and side_result.get("forced_retreat"):
            status = "routed"
        elif p.name in arrived:
            status = "reinforced"
        else:
            status = "engaged"
        contingents.append(
            _contingent(p, committed, casualties, remaining, status,
                        is_lead, world))

    # The no-show shelf. A corps that never marched reveals its region,
    # not the battle — enemy no-shows need FULL visibility of where they
    # actually stand (fog contract above).
    for r in reinforcements:
        if r.get("arrived"):
            continue
        absent = world.marshals.get(r.get("marshal", ""))
        if absent is None:
            continue
        if absent.nation != player_nation:
            intel = world.get_region_intel(absent.location)
            if getattr(intel, "visibility", None) != FULL:
                continue
        # PT-D2: a refusal renders as a refusal, not as a failed march.
        reason = r.get("reason", "")
        status = "refused" if reason in _REFUSAL_REASONS else "failed_arrive"
        entry = _contingent(
            absent,
            committed=int(getattr(absent, "strength", 0)),
            casualties=0,
            remaining=int(getattr(absent, "strength", 0)),
            status=status, lead=False, world=world)
        entry["absence_reason"] = _ABSENCE_LABELS.get(
            reason, _ABSENCE_DEFAULT)
        contingents.append(entry)

    return contingents


def _inject_muster_promises(contingents: List[dict], muster_rows, world):
    """PT-D2 muster-promise parity: every WILL JOIN name appears with SOME
    status. The preview ladder (_muster_reason) and the resolve ladder
    (_is_reinforcement_eligible) are parallel re-implementations — a
    marshal can promise at muster and be dropped silently at resolve (the
    live Murat case). Whoever promised and is in neither the fought line
    nor the shelf lands here as `out_of_reach`."""
    if not muster_rows:
        return contingents
    present = {c.get("name") for c in contingents}
    for row in muster_rows:
        if not row.get("will_join"):
            continue
        name = row.get("marshal", "")
        if not name or name in present:
            continue
        promised = world.marshals.get(name)
        if promised is None:
            continue
        entry = _contingent(
            promised,
            committed=int(getattr(promised, "strength", 0)),
            casualties=0,
            remaining=int(getattr(promised, "strength", 0)),
            status="out_of_reach", lead=False, world=world)
        entry["absence_reason"] = "the field moved beyond his reach"
        contingents.append(entry)
        present.add(name)
    return contingents


def _cap_side(contingents: List[dict]) -> dict:
    """Fixed cap + honest tail (eval §7 Q3): the shelf never crowds out the
    line — fought corps take the cap first, no-shows keep one slot when the
    line is full (the gap IS the drama)."""
    fought = [c for c in contingents if c["status"] not in ABSENT_STATUSES]
    absent = [c for c in contingents if c["status"] in ABSENT_STATUSES]
    shown_fought = fought[:MAX_CONTINGENTS_PER_SIDE]
    reserve = len(fought) - len(shown_fought)
    shown_absent = absent[:max(1, MAX_CONTINGENTS_PER_SIDE - len(shown_fought))] \
        if absent else []
    hidden_absent = len(absent) - len(shown_absent)
    return {
        "contingents": shown_fought + shown_absent,
        "reserve_count": int(reserve + hidden_absent),
        "casualties_total": int(sum(c["casualties"] for c in contingents)),
        "committed_total": int(sum(
            c["committed"] for c in contingents
            if c["status"] not in ABSENT_STATUSES)),
    }


def derive_register(player_side: Optional[str], outcome: str) -> str:
    """The framing register (eval §7 Q6 — Fable's call, recorded here):
    the player's line is always the near side, and a defeat must read as
    a gut-punch, not a mirrored enemy triumph.

    triumph  — the player's side won.
    defeat   — the player's side lost; the tableau turns crimson.
    grim     — the player fought and nobody won (stalemate / mutual ruin).
    observer — a battle watched from afar; neutral museum tone.
    """
    if player_side is None:
        return "observer"
    if outcome == "mutual_destruction":
        return "grim"
    won = (player_side == "attacker" and outcome.startswith("attacker")) or \
          (player_side == "defender" and outcome.startswith("defender"))
    if "victory" in outcome:
        return "triumph" if won else "defeat"
    return "grim"


def build_battle_diorama(world, attacker, defender, battle_result: dict,
                         battle_region: str,
                         atk_participants: list, def_participants: list,
                         pre_strengths: Dict[str, int],
                         atk_distribution: dict, def_distribution: dict,
                         attacker_reinforcements: list,
                         defender_reinforcements: list,
                         region_conquered: bool,
                         total_engaged: int,
                         muster_rows: Optional[list] = None) -> Optional[dict]:
    """Assemble the Battle Diorama payload, or None when fog says the player
    may not see this field. Display-only; every figure is either already on
    the battle event surface or derived from it."""
    player_nation = getattr(world, "player_nation", "France")
    atk_nation = getattr(attacker, "nation", "")
    def_nation = getattr(defender, "nation", "")

    player_side: Optional[str] = None
    if atk_nation == player_nation:
        player_side = "attacker"
    elif def_nation == player_nation:
        player_side = "defender"
    player_involved = player_side is not None

    # Fog gate for third-party battles: FULL region visibility or nothing.
    if not player_involved:
        intel = world.get_region_intel(battle_region)
        if getattr(intel, "visibility", None) != FULL:
            return None

    outcome = str(battle_result.get("outcome", ""))
    atk_contingents = _side_contingents(
        world, attacker, atk_participants, atk_distribution,
        battle_result.get("attacker", {}) or {},
        attacker_reinforcements, pre_strengths, player_involved)
    # PT-D2: the muster block is the attacker's promise ledger — parity
    # applies to the side that mustered.
    atk_contingents = _inject_muster_promises(atk_contingents, muster_rows, world)
    attacker_side = _cap_side(atk_contingents)
    attacker_side["nation"] = atk_nation
    defender_side = _cap_side(_side_contingents(
        world, defender, def_participants, def_distribution,
        battle_result.get("defender", {}) or {},
        defender_reinforcements, pre_strengths, player_involved))
    defender_side["nation"] = def_nation

    great_battle = bool(
        int(total_engaged) >= int(getattr(world, "GREAT_BATTLE_THRESHOLD",
                                          10 ** 9)))
    decisive = outcome in _DECISIVE_OUTCOMES
    any_broken = any(
        c["status"] in ("routed", "destroyed")
        for c in attacker_side["contingents"] + defender_side["contingents"])
    multi_corps = (
        len(attacker_side["contingents"]) >= 2
        or len(defender_side["contingents"]) >= 2)

    # `significant` is the eval's blessed §7 Q2 predicate (decisive /
    # player-marshal / named — the honest reading of "named" is the Great
    # tier, since EVERY field battle composes an ordinal name and a
    # literal reading would gate nothing). `dramatic` narrows the
    # UNINVITED surface — the enemy-phase auto-play — to battles that
    # earn an interruption, per the eval's own §2 fun-curve: routine
    # incoming raids stay one click away instead of seizing the screen.
    significant = decisive or player_involved or great_battle
    dramatic = (decisive or great_battle or any_broken
                or bool(region_conquered) or multi_corps)

    register = derive_register(player_side, outcome)

    report = battle_result.get("battle_report") or {}
    payload = {
        "battle_name": str(battle_result.get("battle_name", "")
                           or f"Battle of {battle_region}"),
        "region": battle_region,
        "turn": int(getattr(world, "current_turn", 0)),
        "outcome": outcome,
        "victor": battle_result.get("victor"),
        "attacker_nation": atk_nation,
        "defender_nation": def_nation,
        "player_side": player_side,
        "register": register,
        "significant": bool(significant),
        "dramatic": bool(dramatic),
        "great_battle": great_battle,
        "region_conquered": bool(region_conquered),
        "attacker": attacker_side,
        "defender": defender_side,
        "observation": str(report.get("observation", "") or ""),
    }
    enemy_voice = battle_result.get("enemy_voice")
    if enemy_voice:
        payload["enemy_voice"] = str(enemy_voice)
    # NP-5 (NAPOLEON_SPEC §9): when a sovereign stood on this field, the
    # typed-last verdict acknowledges the register before Berthier's
    # observation — display-only, both sides' sovereigns alike.
    _shown = (attacker_side.get("contingents", [])
              + defender_side.get("contingents", []))
    if any(c.get("sovereign") for c in _shown) and payload["observation"]:
        payload["observation"] = (
            "The Emperor watched this field. " + payload["observation"])
    return payload
