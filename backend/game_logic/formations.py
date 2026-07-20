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

GR5: every MECHANICS helper takes a nation parameter; nothing in the
formation, creation or grudge machinery is nation-hardcoded — an AI court
forms exactly as the player's does. The two deliberate player-scoped
exceptions are DISPLAY builders, named here so the contract above stays
literally true: `build_formables_payload` (a UI payload for the player's
own browser, like `build_marshal_overview`) and `_formation_grudges`
(bounded by the v0.1 France-scoped threat scalar — §11.10 decision 8, the
D2 pattern, recorded and not fought).
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

# ══════════════════ NA-6c — CLASS C CARVE-OUT (spec §11.4) ═══════════════
# Deliberately NOT `vassal.TRANSFER_LOYALTY_RESET`, which numerically equals
# this today: that constant carries a TRANSFER semantic (a satellite changing
# hands keeps its grievances). A carved client is BORN owing its existence to
# the carver — same number, different meaning, so it gets its own name and
# may be tuned independently.
CARVE_LOYALTY = 30
CARVE_SEED_GOLD_DEFAULT = 500
# A newborn client's reserve — below PapalStates (the smallest authored
# Europe pool, 8000/1000/500), because it is a province with a flag on it.
CARVE_MANPOWER_DEFAULT = {"infantry": 6000, "cavalry": 800, "artillery": 400}
# The carved province changes hands under duress at a settlement table, so it
# takes the hostile-cession reset (`settlement_ratify`'s territory_cede idiom)
# rather than VS-3's stability-preserving grant idiom.
CARVE_STABILITY = 50


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
        # NA-6d §11.9 — the authored threat-panel name for the standing
        # wound ("The Polish Question"). Empty = the panel's generic
        # formation label; only meaningful beside a non-empty `aggrieved`.
        "grudge_label": str(forms.get("grudge_label") or "").strip(),
    }


def _deck(world, nation: str) -> List[dict]:
    return [e for e in ((getattr(world, "agendas", {}) or {}).get(nation) or [])
            if isinstance(e, dict)]


def _formation_records(world) -> Dict[str, dict]:
    return getattr(world, "nation_formations", None) or {}


def get_formation_record(world, nation: str) -> Optional[dict]:
    record = _formation_records(world).get(nation)
    return record if isinstance(record, dict) else None


def _is_creation_record(record: Optional[dict]) -> bool:
    """True for a Class C CREATION record that has not yet FORMED (NA-6d).

    A creation stamps `{"id": <template>, "template": <template>, ...}`;
    a formation stamps the forming DECK ENTRY's id. The distinction is the
    C→T chain's hinge: a created Duchy of Warsaw must still be able to
    proclaim Poland (its creation was a birth, not its formation), while a
    FORMED nation is latched forever (§11.1 — formation is permanent).
    """
    if not isinstance(record, dict):
        return False
    # An EXPLICIT formed marker outranks the id/template inference. The
    # inference alone couples two independent authoring namespaces: a deck
    # entry whose `id` happened to equal a `formable_nations` key made a
    # FORMED record read as "created", so `process_formations` never
    # latched and the nation re-proclaimed every turn — +2,000 gold and a
    # fresh -30 aggrieved blow per tick, unbounded (audit, verified live).
    # `_proclaim` stamps this key, so a formed record is now self-declaring
    # and the equality below is only the pre-marker fallback.
    if record.get("formed"):
        return False
    template = str(record.get("template") or "")
    return bool(template) and str(record.get("id") or "") == template


def get_template(world, template_id: str) -> Optional[dict]:
    """The authored NA-6c `formable_nations` template, or None.

    The catalogue is scenario data serialized on the world (like
    `agendas`), so a carve's identity survives save/load without the
    scenario file being present.
    """
    if not template_id:
        return None
    catalogue = getattr(world, "formable_nations", None) or {}
    template = catalogue.get(template_id)
    return template if isinstance(template, dict) else None


def get_template_identity(template: dict) -> Optional[dict]:
    """Normalize a Class C template into the SAME identity shape a Class T
    `forms` block yields, so every downstream consumer (display override,
    flag override, aggrieved blow, the Proclamation card) is class-blind.

    Deliberately reuses `get_forms_block`'s normalization by shape rather
    than by copy: `display_name` is mandatory, `flag` defaults to the
    display name with spaces stripped (the U6 heraldry convention), and
    `aggrieved` absent means the erection offends nobody.
    """
    if not isinstance(template, dict):
        return None
    return get_forms_block({"forms": template})


def template_provinces(template: dict) -> List[str]:
    """The template's province list — the whole carve eligibility
    predicate, so it is read through one helper everywhere."""
    if not isinstance(template, dict):
        return []
    return [str(p) for p in (template.get("provinces") or []) if p]


def _forms_block_for_record(world, nation: str, record: dict) -> Optional[dict]:
    """Re-derive the authored identity block behind a formation record.

    Fully derived (§11.9: "zero new serialized fields" beyond the record
    itself) — the record stores only an id, and the authored source
    survives untouched, so the block is always re-readable.

    TWO arms, because NA-6c mints nations that have no deck at all:
    a CREATED client (record carries `template`) resolves through the
    `formable_nations` catalogue; a FORMED nation (Class T) resolves
    through its own deck entry. Without the template arm a deckless
    carved client would silently have no display name, no flag, and no
    standing §11.9 grudge — the failure would be invisible rather than
    loud.

    NA-6d re-ordered the arms: the DECK-ENTRY arm now goes first, keyed
    on the record's `id`. The C→T chain preserves the `template` key
    across the Poland formation (the `from_dict` capital re-derivation
    needs it forever), so a template-first read would resolve a FORMED
    Poland back to "Duchy of Warsaw". A pure creation record's `id` IS
    the template id, which no deck entry carries, so it falls through to
    the template arm untouched — deckless clients keep their identity
    (the NA-6c pin holds).
    """
    wanted = str((record or {}).get("id") or "")
    if wanted:
        for entry in _deck(world, nation):
            if str(entry.get("id") or "") == wanted:
                block = get_forms_block(entry)
                if block is not None:
                    return block
                break
    template_id = str((record or {}).get("template") or "")
    if template_id:
        identity = get_template_identity(get_template(world, template_id))
        if identity is not None:
            return identity
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


def apply_formation_names_to_history(world, text: str, event: dict) -> str:
    """Formation-aware rendering for an already-formatted HISTORICAL line.

    The campaign log re-derives nation names from the stored raw tag via
    the STATIC `display_nation`, so a post-formation event renders under
    the dead name ("The court of Kingdom of Italy takes up a new design"
    on a turn AFTER Italy was proclaimed — found live).

    History is respected rather than rewritten: only events at or after
    the formation turn are renamed. An entry from before the proclamation
    keeps the name the nation actually bore, and the `nation_formed`
    entry itself is exempt entirely — "Kingdom of Italy is no more —
    Italy is proclaimed" is the whole point of that line, and renaming
    its first half would make it incoherent.
    """
    if not text:
        return text
    if event.get("type") == "nation_formed":
        return text
    event_turn = event.get("turn")
    for nation, record in _formation_records(world).items():
        if not isinstance(record, dict):
            continue
        identity = get_display_identity(world, nation)
        if identity is None:
            continue
        formed_turn = record.get("turn")
        if (event_turn is not None and formed_turn is not None
                and int(event_turn) < int(formed_turn)):
            continue        # it was still the old nation back then
        dead = display_nation(nation)
        if not dead or dead == identity["display_name"] or dead not in text:
            continue
        # NA-6c: a naked substring replace is only safe when the dead name
        # can NEVER appear as ordinary prose. `Normandy` and `Rome` are
        # PROVINCE names on this map, so replacing them would rewrite
        # "Ney was broken at Normandy" into "...at Duchy of Normandy" — a
        # province line corrupted into a nation's name, permanently, on
        # every historical entry after the formation turn. Godot's
        # `_is_prose_safe_nation_key` has carried this guard since NA-6b;
        # the backend twin did not, and NA-6c is what makes a formation key
        # collide with a region for the first time.
        if not _is_prose_safe_name(world, dead):
            continue
        text = text.replace(dead, identity["display_name"])
    return text


def _is_prose_safe_name(world, name: str) -> bool:
    """True when `name` can never occur as ordinary prose, so a whole-text
    substring replacement of it is safe.

    Mirrors Godot's `Utils._is_prose_safe_nation_key`, plus a live
    region-collision check the client cannot make: any name that is also a
    province on this map is unsafe by construction.
    """
    if name in (getattr(world, "regions", {}) or {}):
        return False
    # A multi-token display name ("Duchy of Warsaw") is unambiguous; a bare
    # single word ("Normandy", "Holland", "Rome") is not.
    return len(name.split()) > 1


def formed_display_name(world, nation: str) -> str:
    """The nation's CURRENT display name — formed name if it has one, else
    the standard R7 rendering. The backend-composed-prose repair (§11.8
    stage 3: no surface may show the dead name)."""
    identity = get_display_identity(world, nation)
    if identity:
        return identity["display_name"]
    return display_nation(nation)


# ═══════════════════════ THE WATCHER (§11.6-5 progress) ═══════════════════

def format_progress(held: int, required: int) -> str:
    """"3 of 5 provinces held" / "0 of 1 province held".

    Single source for the watcher marker, shared by the raw-deck watcher
    here and `agendas.build_agenda_payload`'s active-design copy — both
    render on player-facing surfaces (the Formables browser, the ledger
    Design line, the war room), and both hardcoded the plural, so a
    one-province claim read "0 of 1 provinces held" at boot.
    """
    if required <= 0:
        return ""
    noun = "province" if required == 1 else "provinces"
    return f"{int(held)} of {int(required)} {noun} held"


def get_formation_watch(world, nation: str) -> Optional[dict]:
    """The "forms: Italy (3 of 5 provinces held)" marker (§11.6-5 /
    §11.8 stage 0) for a nation with an UNFIRED formable entry.

    None once formed (the dream became a fact) and None for a nation with
    no formable entry. Deliberately NOT gated on vassalage: watching a
    vassal's dormant dream approach is exactly the "player as ex-lord"
    case §11.6-5 names — but `blocked_by_vassalage` states the truth so
    no surface can imply it is one province away when it is not free.

    NA-6d: a Class C CREATION record does not end the watch — a carved
    Duchy of Warsaw's dormant Poland dream is precisely what the watcher
    exists to show. Only a FORMED record retires it.
    """
    record = get_formation_record(world, nation)
    if record is not None and not _is_creation_record(record):
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
            "flag": forms["flag"],
            "entry_id": str(entry.get("id") or ""),
            "held": int(len(held)),
            "required": int(len(regions)),
            "blocked_by_vassalage": bool(_is_vassal(world, nation)),
            "progress": format_progress(len(held), len(regions)),
        }
    return None


# ═══════════════════════ THE PROCLAMATION (§11.8) ═════════════════════════

def _resolve_sponsor(world, nation: str) -> str:
    """§11.10 decision 8: the current lord at proclamation, else the
    sponsor stored on a prior record (a Class C client that later forms
    keeps its creator — a freed Duchy proclaiming Poland has no lord, but
    Berlin still blames Paris), else "" (it freed itself and owes nobody).

    The lord arm is UNCONDITIONALLY dead today, and the comment that said
    it "lives for the NA-6c creation record" was wrong: the only caller is
    `_proclaim`, reached only through `process_formations`, which has
    already refused every vassal — and the creation path never comes here
    at all (`_proclaim_creation` uses `carver` directly). The arm is kept
    because a future non-poll caller would need it; the STORED-sponsor arm
    below is the one that fires, and it is what makes Berlin blame Paris.
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
    prior = records.get(nation) if isinstance(records.get(nation), dict) else {}
    records[nation] = {
        "id": str(entry.get("id") or ""),
        "sponsor": sponsor,
        # `turn` is a conscious v1.3-decision-1 extension: the once-only
        # audit trail, and the durable stamp the ratify-path beat needs
        # (the dispatch QUEUE is cleared at the top of the next tick).
        "turn": turn,
        # The explicit latch (audit). Formation is permanent (§11.1), so a
        # formed record says so in its own words rather than leaving
        # `_is_creation_record` to infer it from an id/template inequality
        # that authoring can collide.
        "formed": True,
    }
    # NA-6d C→T: a created client that later FORMS (Warsaw → Poland) keeps
    # its birth template on the record forever — the `from_dict` capital
    # re-derivation (Q10) and the shape-parity contract key off it. The id
    # changing to the deck entry's is what latches the poll; identity
    # resolution reads the deck arm first, so the name still moves.
    if prior and str(prior.get("template") or ""):
        records[nation]["template"] = str(prior["template"])

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
    created = bool(payload.get("created"))
    lines = [f"+{int(payload['gold'])} gold to its treasury"]
    if created:
        # A carved client's terms are its DEPENDENCE, not a windfall — the
        # §11.6-2 "preview states the full bargain" contract, restated at
        # the moment it becomes true.
        sponsor_display = payload.get("sponsor_display") or ""
        if sponsor_display:
            lines.append(f"it answers to {sponsor_display} as a satellite "
                         f"(loyalty {int(CARVE_LOYALTY)})")
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
            f"{payload['display_name']} stands." if not payload.get("old_display_name")
            else f"{payload['old_display_name']} is no more. "
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

    if payload.get("created"):
        queue_dispatch_event(world, "nation_created", {
            "nation": new_display,
            "sponsor": payload.get("sponsor_display") or "a foreign power",
        }, fog_rule="always")
    else:
        queue_dispatch_event(world, "nation_formed", {
            "old_nation": old_display,
            "nation": new_display,
        }, fog_rule="always")

    # A CREATION kills nothing — `old_display_name` is empty by construction
    # for a carve, so the "is no more" half must not be printed. The
    # campaign-log one-liner already branches the same way on the same key.
    message = (f"{old_display} is no more. {new_display} stands."
               if old_display else f"{new_display} stands.")
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
    #
    # TWO nations can form on ONE tick (free both satellites, win in Italy
    # and Flanders the same turn) and the PopupQueue holds a single slot
    # per type — so the overflow rides a list, exactly like
    # `vassal_rebellion_imminent_popups`. The delivery seams auto-pop it.
    # Without this the second nation forms for real (latch, rewards,
    # overrides, campaign log) but its landmark is silently swallowed.
    card = build_proclamation_card(world, payload)
    if world.nation_proclamation_popup is None:
        world.nation_proclamation_popup = card
    else:
        world.nation_proclamation_popups.append(card)


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
        record = get_formation_record(world, nation)
        if record is not None and not _is_creation_record(record):
            continue            # once-only; formation is permanent (§11.1)
        # A pure CREATION record does NOT latch the poll (NA-6d): being
        # carved into existence was the nation's birth, not its formation
        # — a freed Duchy of Warsaw must still be able to proclaim Poland.
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


# ═══════════════ NA-6c — CLASS C CARVE-OUT CREATION (§11.4) ═══════════════

def _validate_seeds(template_id: str, seeds) -> None:
    """Raise ValueError for any `seeds` shape the birth mutation would
    choke on. Total, and called before the FIRST mutation."""
    if seeds is None:
        return
    if not isinstance(seeds, dict):
        raise ValueError(
            f"formable template {template_id!r}: `seeds` must be an object, "
            f"got {type(seeds).__name__}")
    for key in ("gold", "actions", "authority"):
        if key in seeds:
            value = seeds[key]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(
                    f"formable template {template_id!r}: `seeds.{key}` must be "
                    f"a non-negative integer, got {value!r}")
    if "manpower" in seeds:
        pool = seeds["manpower"]
        if not isinstance(pool, dict) or not all(
                isinstance(v, int) and not isinstance(v, bool) and v >= 0
                for v in pool.values()):
            raise ValueError(
                f"formable template {template_id!r}: `seeds.manpower` must map "
                f"pool names to non-negative integers, got {pool!r}")
    if "diplomat" in seeds:
        defn = seeds["diplomat"]
        if not isinstance(defn, dict):
            raise ValueError(
                f"formable template {template_id!r}: `seeds.diplomat` must be "
                f"an object, got {type(defn).__name__}")
        # `create_diplomat_from_data` direct-indexes all three.
        for key in ("name", "personality", "skill"):
            if key not in defn:
                raise ValueError(
                    f"formable template {template_id!r}: `seeds.diplomat` is "
                    f"missing the required key {key!r}")


def _ensure_owned_capitals(world) -> None:
    """Guarantee `world.nation_capitals` is this world's OWN dict.

    On a LEGACY world it is an ALIAS to the `region.NATION_CAPITALS` module
    global (world_state.py — contrast the Europe branch's `dict(...)`), so
    writing a carved tag through it poisons every world built later in the
    process: the shared-REGIONS_DATA pollution bug class, and
    order-dependent under pytest-randomly.

    Single source, called from BOTH write sites — this helper and the
    `from_dict` capital re-derivation. The re-derivation loop originally
    relied on "formable_nations is empty on a legacy world", which is an
    assumption about DATA, not a guard: nothing Europe-gates the catalogue.
    """
    from backend.models.region import NATION_CAPITALS
    if getattr(world, "nation_capitals", None) is NATION_CAPITALS:
        world.nation_capitals = dict(NATION_CAPITALS)


def _seed_client_roster(world, tag: str, template: dict, carver: str) -> None:
    """Register a brand-new nation tag in every world-level structure a
    boot-authored satellite occupies (§11.10 decision 6, shape parity).

    This is the first code in the project that adds a nation at RUNTIME —
    `enemy_nations` has only ever been built once in `__init__` and
    restored from save. A tag missing from it is invisible to
    `get_active_nations()`, the whole enemy phase, DP regen, the formation
    poll, and the §11.9 aggrieved blow, so it goes first and loudly.
    """
    from backend.models.diplomat import create_diplomat_from_data
    from backend.nation_config import DEFAULT_NATION_DEFAULTS
    from backend.game_logic.vassal import AUTONOMY_SATELLITE, TRIBUTE_RATES

    provinces = template_provinces(template)
    seeds = template.get("seeds") if isinstance(template.get("seeds"), dict) else {}

    # 1. Roster membership — everything else is dead without this.
    if tag != getattr(world, "player_nation", None) and tag not in world.enemy_nations:
        world.enemy_nations.append(tag)
    # A carved client is born deliberately ARMY-LESS, and the turn tick
    # announces any marshal-less nation as eliminated unless it is in this
    # set. `from_scenario` pre-seeds it for the same reason (boot nations
    # like Hanover field no marshals) — without it the first end turn after
    # a Proclamation reports the brand-new nation destroyed.
    notified = getattr(world, "eliminated_nations_notified", None)
    if notified is not None:
        notified.add(tag)

    # 2. Capital. On a LEGACY world `nation_capitals` is an ALIAS to the
    # module global (world_state.py:241, contrast the Europe branch's
    # dict(...)) — writing through it would poison every later world in the
    # process. Copy-on-write rather than refusing to run.
    _ensure_owned_capitals(world)
    world.nation_capitals[tag] = provinces[0]

    # ...and the REGION FLAG, which is what actually gates a capital
    # garrison. Both garrison seams (`world_state._process_capital_garrisons`
    # and the boot seeder) key off `region.is_capital`, NOT the world map —
    # so a carved client whose capital carried no flag would sit at garrison
    # 0 forever, skipped by the regen loop, an undefended province the enemy
    # retakes for free. Seeded straight to target, matching the boot seeder,
    # rather than left to crawl up from nothing.
    capital_region = world.regions.get(provinces[0])
    if capital_region is not None:
        capital_region.is_capital = True
        try:
            target = int(world.get_capital_garrison_target(tag))
        except Exception:
            target = 0
        if target > 0:
            capital_region.garrison_strength = max(
                int(getattr(capital_region, "garrison_strength", 0) or 0), target)

    # 3. Homeland. The carved provinces ARE its homeland: this is what lets
    # "The Knife at the Throat" fire honestly if the client is later
    # overrun. Measured safe at birth — holding its capital keeps
    # `survival_override_active` False, so a newborn never proclaims
    # Survival over its own erection.
    world.nation_starting_regions[tag] = list(provinces)

    # 4. Treasury / reserves / turn budget. `base_nation_actions` AND
    # `nation_actions` both — the per-turn reset loop iterates the former
    # and skips any nation absent from the latter, so writing one key
    # silently freezes the client's AP forever.
    world.nation_gold[tag] = int(seeds.get("gold", CARVE_SEED_GOLD_DEFAULT))
    world.manpower_pools[tag] = dict(
        seeds.get("manpower") or CARVE_MANPOWER_DEFAULT)
    actions = int(seeds.get("actions", DEFAULT_NATION_DEFAULTS["actions"]))
    world.nation_actions[tag] = actions
    world.base_nation_actions[tag] = actions
    # Authority reads default to 60 anyway, but the boot world carries an
    # explicit row for EVERY nation — the shape-parity gate is what caught
    # the omission, and an explicit row costs nothing.
    authority = getattr(world, "nation_authority", None)
    if authority is not None and tag not in authority:
        authority[tag] = int(
            seeds.get("authority", DEFAULT_NATION_DEFAULTS["authority"]))

    # 5. A voice. Absent, `_process_dp_regen` calls calculate_dp(None, ...)
    # and the chancery-fallback idiom is the Voice Bible's answer for a
    # court with no authored diplomat.
    diplomats = getattr(world, "diplomats", None)
    if diplomats is not None and tag not in diplomats:
        identity = get_template_identity(template) or {}
        authored = seeds.get("diplomat")
        # The default composes readable prose for a bare template; the
        # authored arm exists because "Chancery of Duchy of Warsaw" is what
        # the naive composition produces.
        defn = dict(authored) if isinstance(authored, dict) else {
            "name": f"Chancery of {identity.get('display_name') or tag}",
            "personality": "loyalist",
            "skill": 3,
            "biography": "The chancery of a state erected by a foreign "
                         "victory, and dependent on it.",
        }
        diplomats[tag] = create_diplomat_from_data(tag, defn)

    # 6. Its dream, if the template authored one. Dormant while a client
    # (§3.2 is already the law) — it wakes only on independence.
    deck = template.get("deck")
    if isinstance(deck, list) and deck:
        world.agendas[tag] = [dict(entry) for entry in deck
                              if isinstance(entry, dict)]

    # 7. Vassalage under the carver + the pair's diplomatic stamp. Written
    # directly rather than through `create_vassal_treaty`/`_conquest`:
    # those gate on the power cap and release cooldowns (neither meaningful
    # for a state that did not exist a moment ago) and grant loyalty 60/20.
    world.vassals[tag] = {
        "lord": carver,
        "loyalty": int(CARVE_LOYALTY),
        "autonomy": int(AUTONOMY_SATELLITE),
        "path": "carve",
        "created_turn": int(getattr(world, "current_turn", 0)),
        "tribute_rate": TRIBUTE_RATES[AUTONOMY_SATELLITE],
        "carved_from": None,     # set by the caller, which knows the court
        "regions": list(provinces),
    }
    world.diplomatic_states[world._make_diplo_key(tag, carver)] = "VASSAL"


def create_client_nation(world, template_id: str, carver: str,
                         ceded_from: str = "") -> Optional[dict]:
    """Erect a Class C client state out of a defeated party's soil (§11.4).

    Returns the Proclamation payload, or None when the template is
    unknown. GR5 throughout: `carver` is a parameter, so a coalition
    victor erects the Duchy of Normandy against France by the identical
    path the player uses to erect the Duchy of Warsaw against Prussia.

    Raises ValueError when a template province is absent from the world —
    an unauthored or misspelled province is a template that can never be
    carved, and failing loudly at the one moment it matters beats a silent
    half-built nation.
    """
    template = get_template(world, template_id)
    if template is None:
        logger.warning("create_client_nation: unknown template %r", template_id)
        return None
    identity = get_template_identity(template)
    if identity is None:
        logger.warning(
            "create_client_nation: template %r has no display_name", template_id)
        return None

    tag = template_id
    provinces = template_provinces(template)
    missing = [p for p in provinces if p not in getattr(world, "regions", {})]
    if not provinces or missing:
        raise ValueError(
            f"formable template {template_id!r} names province(s) that do not "
            f"exist in this world: {missing or 'none authored'}")
    # Everything the mutation will consume is checked BEFORE step 1. The
    # docstring promises "failing loudly at the one moment it matters beats
    # a silent half-built nation" — but only `provinces` was actually
    # pre-checked, so a template with (say) a `seeds.diplomat` missing its
    # `skill` raised KeyError out of settlement ratification AFTER the tag
    # was already in `enemy_nations`, leaving a phantom nation that
    # serializes.
    _validate_seeds(template_id, template.get("seeds"))

    _seed_client_roster(world, tag, template, carver)
    if ceded_from:
        world.vassals[tag]["carved_from"] = ceded_from

    # The soil changes hands LAST of the mutations, so the tag already
    # exists when `get_nation_regions` is next derived.
    for province in provinces:
        region = world.regions[province]
        region.controller = tag
        region.stability = CARVE_STABILITY
    if hasattr(world, "invalidate_active_nations_cache"):
        world.invalidate_active_nations_cache()

    return _proclaim_creation(world, tag, template_id, identity, carver)


def _proclaim_creation(world, tag: str, template_id: str, identity: dict,
                       carver: str) -> dict:
    """The Proclamation for a CREATION (§11.8 stages 1-3, shared with the
    Class T formation beat).

    A creation cannot reach `process_formations` — that poll skips every
    vassal (§3.2 dormancy), and a carved client is a vassal from its first
    instant — so the carve emits its own landmark rather than waiting for
    a tick that will never announce it.
    """
    turn = int(getattr(world, "current_turn", 0))

    # The latch first, exactly as `_proclaim` does: a raise inside the beat
    # must never leave a tag able to proclaim twice (§11.8 never-do #1).
    records = getattr(world, "nation_formations", None)
    if records is None:
        world.nation_formations = {}
        records = world.nation_formations
    prior = records.get(tag) if isinstance(records.get(tag), dict) else {}
    prior_formed = bool(prior) and not _is_creation_record(prior)
    records[tag] = {
        # A creation has no forming DECK ENTRY, so `id` records the
        # template and `template` is what identity resolution keys off.
        "id": template_id,
        "template": template_id,
        "sponsor": carver,
        "turn": turn,
    }
    # ...unless this tag ALREADY formed once. A carved client can be
    # conquered out of `get_active_nations()`, and the settlement gate only
    # refused a tag that is currently ACTIVE — so a re-carve of the same
    # soil overwrote a FORMED record with a fresh creation record,
    # un-latching a formation the spec calls permanent (§11.1): the nation
    # proclaimed a second time, banked a second windfall, and struck every
    # aggrieved court a second -30 (audit, traced live). The creation is
    # still allowed — the state really is being erected again — but the
    # formation latch it already earned survives it.
    if prior_formed:
        records[tag]["formed"] = True

    struck = _apply_aggrieved_blow(world, tag, identity, carver)
    gold = int((getattr(world, "nation_gold", {}) or {}).get(tag, 0))

    payload = {
        "type": "nation_formed",
        "nation": tag,
        # Deliberately EMPTY: nothing died to make this nation. The
        # campaign-log one-liner, the card and the notification all branch
        # on this, so "Prussia is no more" can never be printed for a carve
        # that took one province from a living Prussia.
        "old_display_name": "",
        "display_name": identity["display_name"],
        "flag_tag": identity["flag"],
        "blurb": identity["blurb"],
        "entry_id": template_id,
        "template": template_id,
        "created": True,
        "sponsor": carver,
        "sponsor_display": display_nation(carver) if carver else "",
        "aggrieved": struck,
        "aggrieved_display": [display_nation(p) for p in struck],
        "next_design": "",   # a client's deck lies dormant (§3.2)
        "gold": gold,
        "stability_bonus": 0,
        "regions_lifted": 0,
        "turn": turn,
    }
    _announce(world, payload)
    return payload


# ═══════════════════ §11.9 THE STANDING WOUND (formation_grudge) ══════════

def _formation_grudges(world) -> List[dict]:
    """Per-formation standing grievances: [{tag, label, courts}].

    Fully derived from `world.nation_formations` + the authored `aggrieved`
    list — zero new serialized fields. The grievance ends only via the
    aggrieved power's own elimination or vassalization; the formation
    itself is permanent (§11.1), so nothing else dissolves it.

    Deterministic order (formation turn, then tag) and court-level dedup
    across formations: a court aggrieved by two proclamations grieves
    ONCE — the earlier formation claims it, so amounts never double-count
    within the shared cap.

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

    grudges: List[dict] = []
    claimed: set = set()
    ordered = sorted(
        _formation_records(world).items(),
        key=lambda kv: (int((kv[1] or {}).get("turn") or 0) if isinstance(kv[1], dict) else 0,
                        kv[0]))
    for nation, record in ordered:
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
        courts = [power for power in (forms.get("aggrieved") or [])
                  if power != player and power in active
                  and power not in vassals and power not in claimed]
        if not courts:
            continue
        claimed.update(courts)
        grudges.append({
            "tag": nation,
            "label": forms.get("grudge_label") or "",
            "courts": courts,
        })
    return grudges


def get_formation_grudge_nations(world) -> List[str]:
    """Aggrieved courts still nursing a standing formation grievance
    (the NA-6a API — now a view over `_formation_grudges`)."""
    grudged: set = set()
    for grudge in _formation_grudges(world):
        grudged.update(grudge["courts"])
    return sorted(grudged)


def get_formation_grudge_contributions(world, budget: int) -> List[dict]:
    """Per-formation threat contributions inside the SHARED §5.8 budget:
    [{source: "formation_grudge:<tag>", label, amount}] (NA-6d).

    §11.9 pins that the threat panel NAMES each grievance ("The Polish
    Question" for Warsaw/Poland) — so each formation emits under its own
    source key rather than one merged `formation_grudge` row. The budget
    split with `agenda_grudge` is unchanged: that family emits first at
    its own value and the formations share only the remainder, earlier
    formations first (the `_formation_grudges` order).
    """
    room = int(max(0, min(AGENDA_GRUDGE_CAP, budget)))
    contributions: List[dict] = []
    for grudge in _formation_grudges(world):
        if room <= 0:
            break
        amount = int(min(room, len(grudge["courts"])))
        if amount <= 0:
            continue
        room -= amount
        contributions.append({
            "source": f"formation_grudge:{grudge['tag']}",
            "label": grudge["label"],
            "amount": amount,
        })
    return contributions


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
    return int(sum(c["amount"]
                   for c in get_formation_grudge_contributions(world, budget)))


def formation_grudge_source_label(world, source_key: str) -> str:
    """The threat-panel display name for a `formation_grudge:<tag>` source
    key — the authored `grudge_label` ("The Polish Question"), else ""
    so callers fall back to the generic formation label. Resolves through
    the formation record so a serialized threat row keeps its name across
    save/load without storing it."""
    if ":" not in (source_key or ""):
        return ""
    tag = source_key.split(":", 1)[1]
    record = get_formation_record(world, tag)
    if record is None:
        return ""
    forms = _forms_block_for_record(world, tag, record)
    if forms is None:
        return ""
    return str(forms.get("grudge_label") or "")


# ═══════════════ NA-6d — THE FORMABLES BUTTON (§11.6-8 / decision 9) ══════

def build_formables_payload(world) -> dict:
    """One row per Class C template AND per Class T watcher — the assured,
    always-reachable browser for the formable world (`GET /formables`).

    §11.6-8 contract: rows are NEVER hidden and NEVER dead. An unavailable
    row states exactly what is missing in its `gate_terms`; an available
    Class C row carries a `deep_link {nation, war_id}` into the settlement
    flow that can author the clause. Class T rows are informational by
    construction (a formation happens by conquest, not authoring) and a
    formed row says the dream already stands.

    Availability is the REAL settlement predicate
    (`evaluate_create_client_eligibility`) run per active war — never a
    re-derivation that could drift from the authoring surface.
    """
    from backend.game_logic.settlement_helpers import _iter_active_war_instances
    from backend.game_logic.settlement_scoring import TOTAL_ANNEXATION_WAR_SCORE
    from backend.game_logic.settlement_validation import (
        evaluate_create_client_eligibility,
    )
    from backend.models.region import get_starting_controllers

    player = getattr(world, "player_nation", "France")
    active = set(world.get_active_nations())
    starting = (getattr(world, "_starting_controllers", None)
                or get_starting_controllers())
    regions = getattr(world, "regions", {}) or {}
    rows: List[dict] = []
    # Tags already rendered by the Class C pass, so the Class T pass never
    # emits a duplicate row for the same nation.
    emitted: set = set()

    # ── Class C templates (authored order — dict preserves insertion) ──
    catalogue = getattr(world, "formable_nations", None) or {}
    for template_id, template in catalogue.items():
        identity = get_template_identity(template)
        if identity is None:
            continue
        provinces = template_provinces(template)
        from_court = str(starting.get(provinces[0], "")) if provinces else ""
        court_display = formed_display_name(world, from_court) if from_court else ""

        if template_id in active:
            # The CURRENT identity, never the birth literal. A carved
            # Duchy of Warsaw that went on to proclaim Poland was rendering
            # its own dead name here (the template arm is frozen at birth)
            # while `Utils.bb_flag` resolved the override — so the row drew
            # Poland's flag beside the label "Duchy of Warsaw", and the
            # Class T branch below emitted a SECOND row for the same tag.
            # §11.8 stage 3: no surface may show the dead name.
            standing = get_display_identity(world, template_id)
            stands_name = (standing or {}).get(
                "display_name") or identity["display_name"]
            stands_flag = (standing or {}).get("flag_tag") or identity["flag"]
            emitted.add(template_id)
            rows.append({
                "tag": template_id,
                "display_name": stands_name,
                "flag": stands_flag,
                "cls": "C",
                "available": False,
                "progress": "",
                "gate_terms": [
                    {"text": f"{stands_name} already stands", "met": True},
                ],
                "deep_link": None,
            })
            continue

        # The player's OWN soil: France can never carve Normandy — the
        # eligibility predicate refuses from_court == carver by design.
        # The row still shows (§11.6-8: never hidden), but its honest gate
        # term is the mirror threat, not a war-with-yourself absurdity.
        if from_court == player:
            rows.append({
                "tag": template_id,
                "display_name": identity["display_name"],
                "flag": identity["flag"],
                "cls": "C",
                "available": False,
                "progress": "",
                "gate_terms": [{
                    "text": (f"carved from {formed_display_name(world, player)}'s "
                             f"own provinces — a clause only a victorious "
                             f"enemy may put before you"),
                    "met": False,
                }],
                "deep_link": None,
            })
            continue

        # The real predicate, per ACTIVE war — first qualifying war wins.
        # `war_instances` retains CONCLUDED wars for ARCHIVE_RETENTION_TURNS
        # and the predicate's side resolution is pure membership, so an
        # archived war used to hand back `available: true` with a deep link
        # the settlement layer then refuses as `war_archived` — a dead
        # route beside its own "at war: ✗" gate term, for up to 10 turns
        # after any peace where the player kept the template soil. Every
        # other settlement consumer filters through
        # `_iter_active_war_instances`; so does this one now.
        deep_link = None
        for war_id, war in sorted(_iter_active_war_instances(world),
                                  key=lambda kv: str(kv[0])):
            verdict = evaluate_create_client_eligibility(
                world, war_instance=war, template_id=template_id,
                from_court=from_court, carver=player)
            if verdict.get("eligible"):
                deep_link = {"nation": from_court, "war_id": str(war_id)}
                break

        # Honest gate terms, composed from world state the player can act on.
        pair_state = ""
        if from_court:
            pair_state = str((getattr(world, "diplomatic_states", {}) or {})
                             .get(world._make_diplo_key(player, from_court), ""))
        at_war = pair_state in ("WAR", "ARMISTICE")
        bloc = set(world.get_bloc_members(player)) | {player}
        terms = [{
            "text": f"at war with {court_display or 'the owning court'}",
            "met": bool(at_war),
        }]
        # Whose soil is this? A template may only be carved from the court
        # that STARTED with every one of its provinces
        # (`carve_not_defeated_soil`). Single-province templates satisfy it
        # by construction — `from_court` is derived from provinces[0] — but
        # a multi-province template spanning two courts refuses forever,
        # and without this term every other row would read ✓ while the
        # button never appeared.
        wrong_soil = [p for p in provinces
                      if str(starting.get(p, "")) != from_court]
        if wrong_soil:
            terms.append({
                "text": (f"{', '.join(wrong_soil)} never belonged to "
                         f"{court_display or 'that court'} — this state "
                         f"cannot be raised from their lands"),
                "met": False,
            })
        for province in provinces:
            holder = str(getattr(regions.get(province), "controller", "") or "")
            held = holder in bloc
            text = f"{province} held at the settlement table"
            if not held and holder:
                text += f" (currently {formed_display_name(world, holder)}-held)"
            terms.append({"text": text, "met": bool(held)})

        # The total-annexation rule. A carve that leaves the court with
        # NOTHING erases it, and a state is not erased short of a decisive
        # victory — the Papal States are a one-province polity, so the
        # Roman Republic trips this for almost the whole war. Unstated, the
        # row showed every term ✓ and still offered no button: the §11.6-8
        # "never dead" contract broken by silence, on the one template the
        # rule exists for.
        remaining = set(world.get_nation_regions(from_court)) - set(provinces)
        if from_court and not remaining:
            ws_key = world._make_diplo_key(from_court, player)
            war_score = abs(int(
                (getattr(world, "war_scores", {}) or {}).get(ws_key, 0) or 0))
            terms.append({
                "text": (f"a decisive victory over "
                         f"{court_display or 'that court'} — erasing a state "
                         f"entirely needs war score "
                         f"{int(TOTAL_ANNEXATION_WAR_SCORE)} "
                         f"(currently {int(war_score)})"),
                "met": war_score >= TOTAL_ANNEXATION_WAR_SCORE,
            })

        emitted.add(template_id)
        rows.append({
            "tag": template_id,
            "display_name": identity["display_name"],
            "flag": identity["flag"],
            "cls": "C",
            "available": deep_link is not None,
            "progress": "",
            "gate_terms": terms,
            "deep_link": deep_link,
        })

    # ── Class T watchers (every deck with an unfired `forms` entry) ──
    for nation in sorted((getattr(world, "agendas", {}) or {})):
        if nation not in active:
            continue
        record = get_formation_record(world, nation)
        if record is not None and not _is_creation_record(record):
            # Formed — the dream already stands; say so, never hide it.
            # ...unless the Class C pass already said exactly that for this
            # tag. A carved client that went on to form (Warsaw → Poland)
            # owns BOTH a template row and a deck, and both arms render
            # "already stands" — one nation, one row. Note this suppresses
            # only the redundant FORMED arm: a created client whose dream
            # is still unfired keeps its watcher row beside the C row,
            # which is the §11.6-5 "the dream is visible" case.
            if nation in emitted:
                continue
            identity = get_display_identity(world, nation)
            if identity is None:
                continue
            rows.append({
                "tag": nation,
                "display_name": identity["display_name"],
                "flag": identity["flag_tag"],
                "cls": "T",
                "available": False,
                "progress": "",
                "gate_terms": [
                    {"text": f"{identity['display_name']} already stands",
                     "met": True},
                ],
                "deep_link": None,
            })
            continue
        watch = get_formation_watch(world, nation)
        if watch is None:
            continue
        holder_display = formed_display_name(world, nation)
        required = int(watch["required"])
        claim = ("its claimed province" if required == 1
                 else f"all {required} of its claimed provinces")
        terms = [{
            "text": f"forms when a free {holder_display} holds {claim}",
            "met": int(watch["held"]) >= required,
        }]
        if watch["blocked_by_vassalage"]:
            lord = str(((getattr(world, "vassals", {}) or {})
                        .get(nation) or {}).get("lord") or "")
            lord_display = formed_display_name(world, lord) if lord else "a foreign power"
            terms.append({
                "text": f"currently a vassal of {lord_display}",
                "met": False,
            })
        rows.append({
            "tag": nation,
            "display_name": watch["forms"],
            "flag": watch["flag"],
            "cls": "T",
            "available": False,
            "progress": watch["progress"],
            "gate_terms": terms,
            "deep_link": None,
        })

    return {"formables": rows, "count": int(len(rows))}
