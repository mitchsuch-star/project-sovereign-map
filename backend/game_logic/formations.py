"""Nation Formations — "Formable Dreams" (NA-6a).

Build contract: docs/NATION_AGENDAS_SPEC.md §11 (§11.10 = the plan of
record; deviations are recorded in the §17 landing record).

A deck entry may carry an optional `forms` block. When that entry's
SATISFACTION condition holds while the nation is FREE (never vassalized —
§3.2 dormancy already guarantees a vassal cannot reach it), the nation
proclaims itself: the display identity transforms, a one-time reward
lands, the beat announces itself, and deck priority natively activates
the next authored entry as the post-formation goal (§11.1-4 — zero new
goal machinery).

Why this module scans the RAW deck instead of `get_active_agenda`
(the single most important structural fact of the slice): an
`acquire_regions` entry is ACTIVE *only while unmet* — activation is the
exact complement of satisfaction (`agendas._acquire_active`). On the tick
where `risorgimento` satisfies, `get_active_agenda("KingdomOfItaly")`
already returns the NEXT deck entry. The forming entry is therefore
unreachable through the derivation chokepoint by construction, and
`process_formations` walks `world.agendas[tag]` directly. (Unlike
`_court_design_satisfied`, which inspects only `deck[0]`, this walks the
WHOLE deck — a formable authored at index >= 1 must still fire.)

The internal nation TAG never changes (GR-hard: serialization safety).
Only the display identity moves, through the two R7 chokepoints.

GR5: every helper takes a nation parameter; nothing is nation-hardcoded —
an AI court forms exactly as the player's does.
GR6: satisfaction is a deterministic pure read; the LLM never sees it.
GR8: no per-region scan outside the one-shot reward pass.
"""

import logging
from typing import Dict, List, Optional

from backend.display_names import display_nation
from backend.game_logic.agendas import (
    AGENDA_GRUDGE_CAP, _is_vassal, entry_satisfied, survival_override_active,
)

logger = logging.getLogger(__name__)

# ══════════════════════ BLESSED NUMBERS (spec §11.3 / §11.9) ══════════════
# In-band tunable per the standing rule; structural changes escalate.
FORMATION_GOLD = 2000                    # the consolidation windfall
FORMATION_STABILITY_BONUS = 2            # the national moment, every owned region
FORMATION_AGGRIEVED_RELATION_PENALTY = -30   # §11.9, one-time, per aggrieved court
FORMATION_STABILITY_CAP = 100            # the world-wide stability ceiling


# ═══════════════════════ THE AUTHORED `forms` BLOCK ═══════════════════════

def get_forms_block(entry: dict) -> Optional[dict]:
    """The validated `forms` block of a deck entry, or None.

    A block is formable only with a non-empty `display_name` — the whole
    point is a new name on every surface. `flag` defaults to the display
    name with spaces stripped (the U6 heraldry asset convention);
    `blurb` powers the Proclamation's engraved line (§11.8 stage 2);
    `aggrieved` is the §11.9 list (absent = the formation offends nobody).
    """
    if not isinstance(entry, dict):
        return None
    forms = entry.get("forms")
    if not isinstance(forms, dict):
        return None
    display_name = str(forms.get("display_name") or "").strip()
    if not display_name:
        return None
    flag = str(forms.get("flag") or "").strip() or display_name.replace(" ", "")
    return {
        "display_name": display_name,
        "flag": flag,
        "blurb": str(forms.get("blurb") or ""),
        "aggrieved": [str(n) for n in (forms.get("aggrieved") or []) if n],
    }


def _deck(world, nation: str) -> List[dict]:
    return [e for e in ((getattr(world, "agendas", {}) or {}).get(nation) or [])
            if isinstance(e, dict)]


def _formation_records(world) -> Dict[str, dict]:
    return getattr(world, "nation_formations", None) or {}


def get_formation_record(world, nation: str) -> Optional[dict]:
    record = _formation_records(world).get(nation)
    return record if isinstance(record, dict) else None


def _forms_block_for_record(world, nation: str, record: dict) -> Optional[dict]:
    """Re-derive the authored `forms` block behind a formation record.

    Fully derived (§11.9: "zero new serialized fields") — the record
    stores only the entry id, and the authored deck entry survives
    formation untouched, so the block is always re-readable.
    """
    wanted = str((record or {}).get("id") or "")
    if not wanted:
        return None
    for entry in _deck(world, nation):
        if str(entry.get("id") or "") == wanted:
            return get_forms_block(entry)
    return None


# ═══════════════════════ THE IDENTITY TRANSFORM (R7) ══════════════════════

def get_display_identity(world, nation: str) -> Optional[dict]:
    """{display_name, flag_tag} for a FORMED nation, else None.

    The backend half of §11.10 decision 3. `display_names.display_nation`
    stays static and payload builders do NOT individually adopt a new
    helper; instead the whole override map rides every response as one
    field and Godot's two chokepoints consult it first.
    """
    record = get_formation_record(world, nation)
    if record is None:
        return None
    forms = _forms_block_for_record(world, nation, record)
    if forms is None:
        return None
    return {"display_name": forms["display_name"], "flag_tag": forms["flag"]}


def build_nation_display_overrides(world) -> Dict[str, str]:
    """{tag: display_name} for every formed nation — the response field.

    Empty dict at boot by construction (nothing can form at boot), so the
    field is zero-behavior-change until the first proclamation.
    """
    overrides: Dict[str, str] = {}
    for nation in _formation_records(world):
        identity = get_display_identity(world, nation)
        if identity:
            overrides[nation] = identity["display_name"]
    return overrides


def build_nation_flag_overrides(world) -> Dict[str, str]:
    """{tag: flag_tag} for every formed nation — rides beside the names so
    the flag swaps with the label (§11.8 stage 3)."""
    overrides: Dict[str, str] = {}
    for nation in _formation_records(world):
        identity = get_display_identity(world, nation)
        if identity:
            overrides[nation] = identity["flag_tag"]
    return overrides


def formed_display_name(world, nation: str) -> str:
    """The nation's CURRENT display name — formed name if it has one, else
    the standard R7 rendering. The backend-composed-prose repair (§11.8
    stage 3: no surface may show the dead name)."""
    identity = get_display_identity(world, nation)
    if identity:
        return identity["display_name"]
    return display_nation(nation)


# ═══════════════════════ THE WATCHER (§11.6-5 progress) ═══════════════════

def get_formation_watch(world, nation: str) -> Optional[dict]:
    """The "forms: Italy (3 of 5 provinces held)" marker (§11.6-5 /
    §11.8 stage 0) for a nation with an UNFIRED formable entry.

    None once formed (the dream became a fact) and None for a nation with
    no formable entry. Deliberately NOT gated on vassalage: watching a
    vassal's dormant dream approach is exactly the "player as ex-lord"
    case §11.6-5 names — but `blocked_by_vassalage` states the truth so
    no surface can imply it is one province away when it is not free.
    """
    if get_formation_record(world, nation) is not None:
        return None
    from backend.game_logic.agendas import _controlled_by_self_or_vassal
    for entry in _deck(world, nation):
        forms = get_forms_block(entry)
        if forms is None:
            continue
        regions = [str(r) for r in (entry.get("regions") or [])]
        held = [r for r in regions
                if _controlled_by_self_or_vassal(world, nation, r)]
        return {
            "forms": forms["display_name"],
            "entry_id": str(entry.get("id") or ""),
            "held": int(len(held)),
            "required": int(len(regions)),
            "blocked_by_vassalage": bool(_is_vassal(world, nation)),
            "progress": (f"{int(len(held))} of {int(len(regions))} provinces held"
                         if regions else ""),
        }
    return None


# ═══════════════════════ THE PROCLAMATION (§11.8) ═════════════════════════

def _resolve_sponsor(world, nation: str) -> str:
    """§11.10 decision 8: the current lord at proclamation, else the
    sponsor stored on a prior record (a Class C client that later forms
    keeps its creator — a freed Duchy proclaiming Poland has no lord, but
    Berlin still blames Paris), else "" (it freed itself and owes nobody).

    Formation is gated on NOT being a vassal, so the lord arm is dead for
    Class T today and lives for the NA-6c creation record.
    """
    vassal_row = (getattr(world, "vassals", {}) or {}).get(nation) or {}
    lord = str(vassal_row.get("lord") or "")
    if lord:
        return lord
    prior = get_formation_record(world, nation) or {}
    return str(prior.get("sponsor") or "")


def _apply_formation_rewards(world, nation: str) -> dict:
    """§11.3, one-shot, through existing mutation paths."""
    gold = getattr(world, "nation_gold", None)
    if gold is not None:
        gold[nation] = int(gold.get(nation, 0)) + FORMATION_GOLD
    lifted = 0
    for region_name in world.get_nation_regions(nation):
        region = world.regions.get(region_name)
        if region is None:
            continue
        before = int(getattr(region, "stability", 0) or 0)
        after = min(FORMATION_STABILITY_CAP, before + FORMATION_STABILITY_BONUS)
        if after != before:
            region.stability = after
            lifted += 1
    return {"gold": int(FORMATION_GOLD), "regions_lifted": int(lifted)}


def _apply_aggrieved_blow(world, nation: str, forms: dict, sponsor: str) -> List[str]:
    """§11.9 — the one-time blow. Each still-active, unvassalized aggrieved
    court takes the penalty with BOTH the new nation and its sponsor.
    GR5: the machinery reads an authored list, so a coalition victor
    erecting a client against France pays it exactly as the player does.
    """
    struck: List[str] = []
    active = set(world.get_active_nations())
    for power in forms.get("aggrieved") or []:
        if power == nation or power not in active or _is_vassal(world, power):
            continue
        world.modify_nation_relation(
            power, nation, FORMATION_AGGRIEVED_RELATION_PENALTY)
        if sponsor and sponsor != power and sponsor != nation:
            world.modify_nation_relation(
                power, sponsor, FORMATION_AGGRIEVED_RELATION_PENALTY)
        struck.append(power)
    return struck


def _post_formation_agenda_title(world, nation: str) -> str:
    """The design the court takes up next — read AFTER the latch so the
    forming entry is already satisfied and deck priority has moved on
    (§11.1-4). Empty when the deck holds nothing further."""
    from backend.game_logic.agendas import get_active_agenda
    world._agenda_cache = None   # the latch/rewards changed nothing the
    # cache keys off, but territory did on the path that got us here
    view = get_active_agenda(nation, world)
    return view.title if view is not None else ""


def _proclaim(world, nation: str, entry: dict, forms: dict) -> dict:
    """The moment (§11.8 stages 1-3). Idempotence is the caller's latch
    check plus the record write that happens FIRST here."""
    turn = int(getattr(world, "current_turn", 0))
    sponsor = _resolve_sponsor(world, nation)
    old_display = display_nation(nation)

    # The latch goes down BEFORE any emission — a raise inside the beat
    # must never leave a nation able to form twice (§11.8 never-do #1).
    records = getattr(world, "nation_formations", None)
    if records is None:
        world.nation_formations = {}
        records = world.nation_formations
    records[nation] = {
        "id": str(entry.get("id") or ""),
        "sponsor": sponsor,
        # `turn` is a conscious v1.3-decision-1 extension: the once-only
        # audit trail, and the durable stamp the ratify-path beat needs
        # (the dispatch QUEUE is cleared at the top of the next tick).
        "turn": turn,
    }

    rewards = _apply_formation_rewards(world, nation)
    struck = _apply_aggrieved_blow(world, nation, forms, sponsor)
    new_display = forms["display_name"]
    next_design = _post_formation_agenda_title(world, nation)

    payload = {
        "type": "nation_formed",
        "nation": nation,
        "old_display_name": old_display,
        "display_name": new_display,
        "flag_tag": forms["flag"],
        "blurb": forms["blurb"],
        "entry_id": str(entry.get("id") or ""),
        "sponsor": sponsor,
        "sponsor_display": display_nation(sponsor) if sponsor else "",
        "aggrieved": struck,
        "aggrieved_display": [display_nation(p) for p in struck],
        "next_design": next_design,
        "gold": int(rewards["gold"]),
        "stability_bonus": int(FORMATION_STABILITY_BONUS),
        "regions_lifted": int(rewards["regions_lifted"]),
        "turn": turn,
    }

    _announce(world, payload)
    return payload


def build_proclamation_card(world, payload: dict) -> dict:
    """The §11.8 stage-2 card payload — content only, no choices.

    Perspective-aware subtitle: the player who ratified the carve or holds
    the sponsorship reads "By your hand"; everyone else witnesses a new
    power taking its seat. Every number is int() for Godot (GR2), and the
    stability line is omitted when the cap swallowed the lift so the card
    never claims a reward the world did not receive.
    """
    player = getattr(world, "player_nation", "France")
    authored = payload.get("sponsor") == player
    lines = [f"+{int(payload['gold'])} gold to its treasury"]
    if int(payload.get("regions_lifted", 0)) > 0:
        lines.append(
            f"its provinces exult (+{int(payload['stability_bonus'])} "
            f"stability in {int(payload['regions_lifted'])} provinces)")
    fury = ""
    if payload.get("aggrieved_display"):
        courts = " and ".join(payload["aggrieved_display"])
        fury = f"{courts} receive the news as a declaration."
    return {
        "nation": payload["nation"],
        "old_display_name": payload["old_display_name"],
        "display_name": payload["display_name"],
        "flag_tag": payload["flag_tag"],
        "proclamation": payload["blurb"] or (
            f"{payload['old_display_name']} is no more. "
            f"{payload['display_name']} stands."),
        "terms": lines,
        "next_design": payload.get("next_design") or "",
        "fury_line": fury,
        "subtitle": ("By your hand." if authored
                     else "A new power takes its seat in Europe."),
        "turn": int(payload["turn"]),
    }


def _announce(world, payload: dict) -> None:
    """Dispatch beat + campaign log + notification (§11.8 stages 1 and 4)
    plus The Proclamation card on the PopupQueue (§11.8 stage 2).

    The notification is deliberately raised alongside the card: it is the
    stage-4 recovery for a player who clicks past the moment.
    """
    from backend.game_logic.dispatch import queue_dispatch_event
    from backend.notifications import (
        create_notification, NotificationPriority, NATION_FORMED,
    )

    new_display = payload["display_name"]
    old_display = payload["old_display_name"]

    queue_dispatch_event(world, "nation_formed", {
        "old_nation": old_display,
        "nation": new_display,
    }, fog_rule="always")

    message = f"{old_display} is no more. {new_display} stands."
    if payload["aggrieved_display"]:
        courts = " and ".join(payload["aggrieved_display"])
        message += f" {courts} receive the news as a declaration."
    world.notifications.add(create_notification(
        NATION_FORMED, NotificationPriority.HIGH,
        f"{new_display} Proclaimed",
        message,
        int(payload["turn"]),
        details={"nation": payload["nation"]},
    ))

    world.log_event({
        "type": "nation_formed",
        "nation": payload["nation"],
        "display_name": new_display,
        "old_display_name": old_display,
        "aggrieved": list(payload["aggrieved"]),
        "sponsor": payload["sponsor"],
    })

    # §11.8 stage 2 — the one ceremonial card. Transport-independent: the
    # queue survives the tick AND the ratify path, where a dispatch line
    # would not. Choice-less, so it carries no response endpoint.
    world.nation_proclamation_popup = build_proclamation_card(world, payload)


def process_formations(world) -> List[Dict]:
    """The once-per-formation poll (§11.10 decision 2).

    Called from TWO sites: `_advance_turn_internal` immediately before
    `process_agenda_shifts` (so the shift beat announces the POST-formation
    deck entry, never the dead forming one), and the settlement
    ratification apply path after territory clauses land (so a carve or
    cession completed at the table proclaims the turn it happens).

    Idempotent via the `nation_formations` latch — safe to call from any
    number of sites. Returns the proclamation payloads; the tick call site
    DISCARDS them, so every surface must be emitted here, never returned.
    """
    if not (getattr(world, "agendas", {}) or {}):
        return []   # deckless worlds (legacy fixtures) can never form

    proclamations: List[Dict] = []
    for nation in sorted(world.get_active_nations()):
        if get_formation_record(world, nation) is not None:
            continue            # once-only; formation is permanent (§11.1)
        if _is_vassal(world, nation):
            continue            # a client cannot proclaim (§3.2 dormancy)
        if survival_override_active(world, nation):
            # The Knife at the Throat outranks the deck in `get_active_agenda`
            # (agendas.py). The raw-deck scan deliberately bypasses that
            # chokepoint — but the survival override must NOT be collateral
            # damage: a rump state that happens to hold one listed province
            # would otherwise proclaim a triumph, bank the windfall, and
            # then take up "Survival" on the very same card. Formation is
            # permanent, so this can never be undone afterwards.
            continue
        for entry in _deck(world, nation):
            forms = get_forms_block(entry)
            if forms is None:
                continue
            if not entry_satisfied(world, nation, entry):
                continue
            proclamations.append(_proclaim(world, nation, entry, forms))
            break               # one formation per nation per pass
    return proclamations


# ═══════════════════ §11.9 THE STANDING WOUND (formation_grudge) ══════════

def get_formation_grudge_nations(world) -> List[str]:
    """Aggrieved courts still nursing a standing formation grievance.

    Fully derived from `world.nation_formations` + the authored `aggrieved`
    list — zero new serialized fields. The grievance ends only via the
    aggrieved power's own elimination or vassalization; the formation
    itself is permanent (§11.1), so nothing else dissolves it.

    v0.1 France-scoped-scalar caveat (§11.10 decision 8, the D2 pattern —
    recorded, not fought): coalition threat is a single France-targeted
    scalar, so a formation only feeds it when the PLAYER is the recorded
    sponsor or the current lord. An AI-erected client aggrieving Austria
    still costs the relation blows; it simply has no France-threat to
    feed. The skip is debug-logged like the hegemony non-France branch.
    """
    player = getattr(world, "player_nation", "France")
    active = set(world.get_active_nations())
    vassals = getattr(world, "vassals", {}) or {}

    grudged: set = set()
    for nation, record in _formation_records(world).items():
        if not isinstance(record, dict):
            continue
        sponsor = str(record.get("sponsor") or "")
        current_lord = str((vassals.get(nation) or {}).get("lord") or "")
        if player not in (sponsor, current_lord):
            logger.debug(
                "formation_grudge: %s formed under sponsor=%r lord=%r — no "
                "player link, skipping the France-targeted scalar",
                nation, sponsor, current_lord,
            )
            continue
        forms = _forms_block_for_record(world, nation, record)
        if forms is None:
            continue
        for power in forms.get("aggrieved") or []:
            if power == player or power not in active or power in vassals:
                continue
            grudged.add(power)
    return sorted(grudged)


def get_formation_grudge_threat(world, budget: int) -> int:
    """+1/turn per aggrieved court, clamped to the SHARED §5.8 budget.

    §11.10 decision 8 pins that the two grudge families never stack past
    `AGENDA_GRUDGE_CAP`. Implemented as a deterministic split rather than
    a single joint clamp: `agenda_grudge` emits first at its own unchanged
    value, and the formation family takes only the remainder. This keeps
    BOTH source keys — §11.9 requires the threat panel to NAME the
    grievance, which one merged `add_threat` would destroy — and leaves
    `_calculate_agenda_grudge_threat` byte-identical (its two NA-3 pins
    do not move). Order-dependence is real and deliberate; documented here
    because it is the one thing a reader would otherwise call a bug.
    """
    room = int(max(0, min(AGENDA_GRUDGE_CAP, budget)))
    if room <= 0:
        return 0
    return int(min(room, len(get_formation_grudge_nations(world))))
