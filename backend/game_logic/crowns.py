"""Crowns & Recognition — DY-6 the crown erected and the marshal king
(DYNAMISM_SPEC.md §6; the Tier-8 gate record §6a, ruled November 10, 2026
at session E's head under the user's delegation; Tier 8, the pre-deploy
marquee).

THE CROWN. A crown is a `formable_nations` template that carries a `crown`
sub-block — ONE catalogue, never a second (the gate's Q1: the authored list
keeps the historian test, D7's principle — content reviewable in the file,
validator-clamped). The block authors the royal style (`title`) and the
houses whose AI may erect it at its own peace (`ai_carvers`; the player's
hand is free among the authored crowns — GR5). The first province listed
is the seat (the catalogue's standing convention). The crown rides the
existing `create_client` term end to end — the guided row, the add verb,
the validator, the ratify, the bilateral carry — and adds its teeth at the
one apply site (`formations.apply_create_client_clause`):

  * the title and the recognition field on the client's row
    (`world.vassals[tag]["crown"]`, `["recognized_by"]` — DY-7 fills it);
  * the new court's boot house written into the Awakening's web (§5a C2:
    a crown erected on awakened soil is a court subjugated LATER — the
    carved people keep THEIR boot house and stir under the new crown as
    under any foreign garrison; the new court's own soil is home under
    the lord that made it) — the sibling fix for every carve, crown or not;
  * the Alarm of Europe (§3): a crown erected alarms Europe like a
    capital taken — `ALARM_CAPITAL` on the carver's house slot, the
    player's included (the coalition's threat);
  * the beat: `nation_formed` carries `crown` and `king` (no new log
    type); the dispatch line is `crown_erected`.

THE MARSHAL KING (the gate's Q2 — both in the pool). Who may reign: a
marshal of the carver's roster with laurels (glory at or above
`KING_MIN_GLORY` in the window, or the crown of glory itself; never the
sovereign, a prisoner or a client's general), or a prince of the Imperial
house (the scenario's `crowns.princes` — Joseph, Louis, Jérôme; a prince
reigns in one place at a time). History with teeth — a crown costs you your
best sword: the marshal is re-homed to the client's colours WITH HIS CORPS
(the Army of Naples), seated at the crown's seat, off the roster, the glory
ladder (his glory satisfied permanently — the release valve) and the
petitions; the client's loyalty seeds from HIS TRUST (clamped 30–95: crown
your trusted Davout for a loyal kingdom, your glorious Bernadotte for a
shaky one); every marshal with laurels passed over takes the authored
grievance — envy toward the king (`jealousy.apply_jealousy`, forced) and
trust −5 (`KING_PASSED_OVER_TRUST`). A prince costs no sword: the client
seeds at `PRINCE_LOYALTY` (50 — the brothers were famously their own men)
and the passed-over marshals' slight is the sharper one (trust −8, the
blood over the sword — Murat's fury when Joseph took Naples first). The
AI's crown seats nobody — a regency.

RECOGNITION (the gate's Q4 — the shape ruled now, the teeth DY-7's,
session F, `tests/test_dy7_recognition.py`): the scenario's
`crowns.recognition` block names the legitimist courts and the condition
(`until: "beaten"`); `withholding_courts` reads it; DY-6 speaks it on the
Proclamation card and nothing bites yet (the row owns the teeth: the
table's malus, trade halved, the dial −3 on awakened soil, the Congress's
grant, the beats).

The store: `world.moments["crowns"] = {"princes": [...], "legitimists":
[...], "until": "beaten"}` (the T5/T6 precedent — `install` beside the
moments line on `from_dict`, `save_manager._backfill_crowns` for a
pre-Tier-8 save; nothing written where none is authored). No new
`WorldState.to_dict` line (497 of 500 stands); the king rides the vassal
row (a dict carried whole).

Seams (zero-arg functions, the S13b idiom; rows T8-CROWN / T8-KING in
`tests/_t3_seams.py`; the AI's road is `settlement_third_party.
a_victor_erects_a_crown`, row T8-AI):
  * `a_crown_is_erected` — down: the crown templates are STRUCK from the
    catalogue at load and the `crowns` block is not installed (the tree
    session D left — NA-6c's four plain carves);
  * `a_marshal_may_reign` — down: no king is offered and a `king` on a
    clause is ignored (a regency, as every carve was).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from backend.display_names import humanize_entity_name

STORE_KEY = "crowns"
KING_MIN_GLORY = 3                   # N-DY6: a crown wants laurels — jealousy's CROWN_MIN_GLORY
KING_LOYALTY_BOUNDS = (30, 95)       # the client's loyalty seeded from the king's trust
PRINCE_LOYALTY = 50                  # a prince of the blood: no record with the people
KING_PASSED_OVER_TRUST = -5          # a marshal with laurels passed over for a peer's crown
PRINCE_PASSED_OVER_TRUST = -8        # … passed over for the blood
PRINCES_MAX = 6
TITLE_MAX = 60
RECOGNITION_CONDITIONS = ("beaten",)  # DY-7 reads it: a legitimist withholds until beaten
KIND_MARSHAL = "marshal"
KIND_PRINCE = "prince"
KINDS = (KIND_MARSHAL, KIND_PRINCE)
# G2-KING: the keys the crown and its king ride on a `create_client` clause —
# every carrier of the clause copies these (the separate peace's seed builder
# copied four other keys and lost the king).
CROWN_CLAUSE_KEYS = ("crown", "king", "king_kind", "king_display")
DISPATCH_TYPE = "crown_erected"


# ═══════════════════════════════════════════════════════════════════════
# The seams
# ═══════════════════════════════════════════════════════════════════════

def a_crown_is_erected() -> bool:
    """T8-CROWN: the crown block's teeth — the crown templates in the
    catalogue, the title and the recognition field on the row, the boot
    house written, the Alarm, the beat's crown. Down: the crown templates
    are struck from the catalogue at load and the `crowns` block is not
    installed — the catalogue session D left."""
    return True


def a_marshal_may_reign() -> bool:
    """T8-KING: the marshal king and the prince. Down: no king is offered
    at the table and a `king` on a clause is ignored (a regency)."""
    return True


# ═══════════════════════════════════════════════════════════════════════
# The catalogue's crown block
# ═══════════════════════════════════════════════════════════════════════

def crown_of(template: Any) -> Optional[Dict[str, Any]]:
    """The template's `crown` sub-block, or None for a plain carve."""
    if not isinstance(template, dict):
        return None
    block = template.get("crown")
    return block if isinstance(block, dict) and block.get("title") else None


def is_crown(template: Any) -> bool:
    return crown_of(template) is not None


def crown_title(template: Any) -> str:
    block = crown_of(template)
    return str(block.get("title") or "") if block else ""


def ai_carvers(template: Any) -> List[str]:
    """The houses whose AI may erect this crown at its own peace."""
    block = crown_of(template)
    if not block:
        return []
    raw = block.get("ai_carvers")
    return [str(c) for c in raw if c] if isinstance(raw, list) else []


def strike_crowns(catalogue: Dict[str, dict]) -> Dict[str, dict]:
    """The seam down (`a_crown_is_erected`): the crown templates struck
    from the catalogue at load and a crown block struck off the rest — the
    catalogue session D left, byte for byte (T4-3's "struck at boot" idiom)."""
    if a_crown_is_erected():
        return catalogue
    out: Dict[str, dict] = {}
    for tag, template in (catalogue or {}).items():
        if not isinstance(template, dict):
            out[tag] = template
            continue
        if "crown" in template and not _authored_before_the_crowns(template):
            continue
        plain = {k: v for k, v in template.items() if k != "crown"}
        out[tag] = plain
    return out


def _authored_before_the_crowns(template: dict) -> bool:
    """A template that existed before a crown slice and later GAINS a crown
    block stays in the catalogue with the block struck; one authored by the
    slice (`crown.since == "DY-6"`) leaves with it. (Every shipped crown is
    DY-6's own; the Duchy of Warsaw stays a plain carve — its duke was the
    King of Saxony, neither a marshal's throne nor a prince's.)"""
    block = template.get("crown")
    return not (isinstance(block, dict) and str(block.get("since") or "") == "DY-6")


# ═══════════════════════════════════════════════════════════════════════
# The store — princes and the recognition rule
# ═══════════════════════════════════════════════════════════════════════

def _clean_names(raw: Any, cap: int) -> List[str]:
    out: List[str] = []
    if isinstance(raw, list):
        for name in raw:
            if isinstance(name, str) and name.strip() and name.strip() not in out:
                out.append(name.strip())
    return out[:cap]


def clean_block(raw: Any) -> Optional[Dict[str, Any]]:
    """The scenario's `crowns` block (or a save's store) normalised:
    `princes` (names), `legitimists` (courts), `until` (a condition). None
    where nothing is authored."""
    if not isinstance(raw, dict):
        return None
    recognition = raw.get("recognition")
    if isinstance(recognition, dict):
        legitimists = _clean_names(recognition.get("legitimists"), 24)
        until = str(recognition.get("until") or RECOGNITION_CONDITIONS[0])
    else:
        legitimists = _clean_names(raw.get("legitimists"), 24)
        until = str(raw.get("until") or RECOGNITION_CONDITIONS[0])
    if until not in RECOGNITION_CONDITIONS:
        until = RECOGNITION_CONDITIONS[0]
    return {"princes": _clean_names(raw.get("princes"), PRINCES_MAX),
            "legitimists": legitimists, "until": until}


def _moments(world) -> Dict[str, Any]:
    moments = getattr(world, "moments", None)
    if not isinstance(moments, dict):
        world.moments = {}
        moments = world.moments
    return moments


def install(world, data: Dict[str, Any]) -> None:
    """`WorldState.from_dict`, beside the moments line: a scenario's
    top-level `crowns` block arms the store; a save's `moments.crowns` is
    carried whole. Writes NOTHING where none is authored (the bare flag
    world, the tutorials, the legacy rollback) and nothing with the seam
    down."""
    if not a_crown_is_erected():
        return
    data = data or {}
    moments = data.get("moments")
    saved = moments.get(STORE_KEY) if isinstance(moments, dict) else None
    block = clean_block(saved) or clean_block(data.get(STORE_KEY))
    if block is None:
        return
    _moments(world)[STORE_KEY] = block


def backfill(world, scenario_data: Dict[str, Any]) -> bool:
    """A pre-Tier-8 save of a scenario that NOW authors the crowns gains
    the store on load (the `_backfill_awakening` idiom); a save carrying a
    store is never overwritten."""
    if armed(world) or not a_crown_is_erected():
        return False
    block = clean_block((scenario_data or {}).get(STORE_KEY))
    if block is None:
        return False
    _moments(world)[STORE_KEY] = block
    return True


def store(world) -> Dict[str, Any]:
    st = (getattr(world, "moments", None) or {}).get(STORE_KEY)
    return st if isinstance(st, dict) else {}


def armed(world) -> bool:
    return bool(store(world))


def princes(world) -> List[str]:
    return [str(p) for p in (store(world).get("princes") or [])]


def legitimists(world) -> List[str]:
    return [str(c) for c in (store(world).get("legitimists") or [])]


def recognition_condition(world) -> str:
    return str(store(world).get("until") or RECOGNITION_CONDITIONS[0])


# ═══════════════════════════════════════════════════════════════════════
# Who reigns
# ═══════════════════════════════════════════════════════════════════════

def reigning_prince_of(world, name: str) -> str:
    """The client a prince reigns over today, or ''. A prince reigns in one
    place at a time (derived from the vassal rows — no second record)."""
    for tag, row in (getattr(world, "vassals", {}) or {}).items():
        if (isinstance(row, dict) and row.get("king_kind") == KIND_PRINCE
                and str(row.get("king") or "") == name):
            return str(tag)
    return ""


def marshal_has_laurels(world, marshal) -> bool:
    from backend.game_logic.jealousy import get_glory_score
    if bool(getattr(marshal, "glory_crowned", False)):
        return True
    return int(get_glory_score(marshal, int(getattr(world, "current_turn", 0)))) >= KING_MIN_GLORY


def marshal_may_be_crowned(world, marshal, carver: str) -> bool:
    """A marshal of the carver's roster with laurels — never the sovereign,
    a prisoner, a broken corps or a client's general."""
    from backend.game_logic.contingent import is_clients_general
    if marshal is None or str(getattr(marshal, "nation", "")) != str(carver):
        return False
    if getattr(marshal, "is_sovereign", False) or getattr(marshal, "captured_by", ""):
        return False
    if is_clients_general(marshal):
        return False
    return marshal_has_laurels(world, marshal)


def marshals_with_laurels(world, carver: str) -> List[Any]:
    """The carver's marshals who may be crowned, the ladder's order
    (highest glory first; the crown of glory first of all)."""
    from backend.game_logic.jealousy import get_glory_score
    turn = int(getattr(world, "current_turn", 0))
    out = [m for m in (getattr(world, "marshals", {}) or {}).values()
           if marshal_may_be_crowned(world, m, carver)]
    out.sort(key=lambda m: (not bool(getattr(m, "glory_crowned", False)),
                            -int(get_glory_score(m, turn)), str(m.name)))
    return out


def available_princes(world, carver: str) -> List[str]:
    """The princes of the carver's house not reigning today — the block is
    the PLAYER's house's (the Imperial family); an AI carver seats nobody."""
    if str(carver) != str(getattr(world, "player_nation", "France")):
        return []
    return [p for p in princes(world) if not reigning_prince_of(world, p)]


def king_candidates(world, carver: str) -> List[Dict[str, str]]:
    """The table's picker: [{name, kind, label}] — the marshals with
    laurels first (the ladder's order), then the princes. Empty with the
    seam down."""
    if not a_marshal_may_reign():
        return []
    from backend.game_logic.jealousy import get_glory_score
    turn = int(getattr(world, "current_turn", 0))
    rows: List[Dict[str, str]] = []
    for marshal in marshals_with_laurels(world, carver):
        glory = int(get_glory_score(marshal, turn))
        crowned = " (the army's most celebrated)" if getattr(marshal, "glory_crowned", False) else ""
        rows.append({"name": str(marshal.name), "kind": KIND_MARSHAL,
                     "label": f"{humanize_entity_name(marshal.name)} — Marshal, glory {glory}{crowned}; "
                              f"his corps ({int(getattr(marshal, 'strength', 0) or 0):,}) goes with him"})
    for prince in available_princes(world, carver):
        rows.append({"name": prince, "kind": KIND_PRINCE,
                     "label": f"{prince} — a prince of the Imperial house; no sword lost, loyalty {PRINCE_LOYALTY}"})
    return rows


# ── G2 (the played campaign): what a crown costs, said at the pick ─────
# The picker named the corps and nothing else. A marshal crowned leaves the
# Emperor's command for good, his kingdom's loyalty is his own trust, and
# the laurelled men passed over resent it — the choice's whole price, in
# words, beside each name (`king_notes`, parallel to `king_labels`), with
# one line for the men not yet eligible and the risk no screen stated: a
# marshal king whose kingdom rises keeps his crown and fights for it.

def _others_with_laurels(world, carver: str, king: str) -> str:
    from backend.display_names import _join_named
    names = [humanize_entity_name(m.name) for m in marshals_with_laurels(world, carver)
             if str(m.name) != str(king)]
    return _join_named(names) if names else ""


def king_cost_note(world, carver: str, candidate: Dict[str, str]) -> str:
    """One pick's price in words ('' with the king seam down)."""
    if not a_marshal_may_reign():
        return ""
    name, kind = str(candidate.get("name") or ""), str(candidate.get("kind") or "")
    slighted = _others_with_laurels(world, carver, name)
    if kind == KIND_MARSHAL:
        marshal = (getattr(world, "marshals", {}) or {}).get(name)
        trust = int(getattr(getattr(marshal, "trust", None), "value", 0) or 0)
        loyalty = _clamp(trust, *KING_LOYALTY_BOUNDS)
        resent = (f" {slighted} will resent it (trust {KING_PASSED_OVER_TRUST}, and envy of the king)."
                  if slighted else "")
        return (f"He leaves your command for good and his corps with him; "
                f"the kingdom's loyalty starts at his trust ({loyalty}).{resent}")
    resent = (f" {slighted} will resent a prince set over them (trust {PRINCE_PASSED_OVER_TRUST})."
              if slighted else "")
    return f"No marshal is lost; the kingdom's loyalty starts at {PRINCE_LOYALTY}.{resent}"


def regency_cost_note() -> str:
    from backend.game_logic.formations import CARVE_LOYALTY
    return (f"No king is seated: the kingdom's loyalty starts at {CARVE_LOYALTY} "
            f"and no marshal is slighted.")


def laurels_footnote(world, carver: str) -> str:
    """The picker's footnote: the risk a marshal king carries, and who has
    not the laurels yet (glory in the ladder's window, the bar named)."""
    if not a_marshal_may_reign():
        return ""
    from backend.game_logic.contingent import is_clients_general
    from backend.game_logic.jealousy import get_glory_score
    turn = int(getattr(world, "current_turn", 0))
    short: List[str] = []
    for marshal in sorted((getattr(world, "marshals", {}) or {}).values(), key=lambda m: str(m.name)):
        if str(getattr(marshal, "nation", "")) != str(carver):
            continue
        if (getattr(marshal, "is_sovereign", False) or getattr(marshal, "captured_by", "")
                or is_clients_general(marshal) or marshal_has_laurels(world, marshal)):
            continue
        short.append(f"{humanize_entity_name(marshal.name)} ({int(get_glory_score(marshal, turn))})")
    risk = ("A marshal king is beyond recall; should his kingdom ever rise against you, "
            "he keeps his crown and fights for it.")
    if not short:
        return risk
    return (f"{risk} Not yet eligible — a throne wants glory {KING_MIN_GLORY}: "
            f"{', '.join(short)}.")


def reigning_rows(world, lord: str) -> List[Dict[str, Any]]:
    """The Marshals screen's REIGNING block: every king `lord`'s house has
    seated — a marshal or a prince — with where he reigns, with what, and
    how he stands: reigning as a client, in arms against his maker (the
    kingdom rebelled and he kept his crown), or fallen with his kingdom.
    Read off the formation record (it outlives the vassal row)."""
    from backend.game_logic.formations import formed_display_name
    out: List[Dict[str, Any]] = []
    records = getattr(world, "nation_formations", None) or {}
    vassals = getattr(world, "vassals", {}) or {}
    active = set(world.get_active_nations())
    for tag, record in sorted(records.items()):
        if not isinstance(record, dict) or not record.get("king"):
            continue
        if str(record.get("sponsor") or "") != str(lord):
            continue
        king, kind = str(record.get("king")), str(record.get("king_kind") or "")
        shown = str(record.get("king_display") or king)
        title = str(record.get("crown") or "")
        kingdom = formed_display_name(world, tag)
        row = vassals.get(tag) if isinstance(vassals.get(tag), dict) else None
        marshal = (getattr(world, "marshals", {}) or {}).get(king) if kind == KIND_MARSHAL else None
        strength = int(getattr(marshal, "strength", 0) or 0) if marshal is not None else 0
        seat = seat_of(world, tag)
        if row is not None and str(row.get("lord") or "") == str(lord):
            state = "reigns"
            loyalty = int(row.get("loyalty", 0) or 0)
            withheld = withholding_courts(world, tag)
            recog = ("recognized by every court" if not withheld
                     else f"{len(withheld)} court{'s' if len(withheld) != 1 else ''} withhold recognition")
            men = f" with {strength:,} men" if strength else ""
            line = (f"{shown} — {title or kingdom} · reigns at {seat or kingdom}{men} · "
                    f"the kingdom's loyalty {loyalty} · {recog} · beyond your orders")
        elif tag in active:
            state, loyalty = "in_arms", 0
            men = f" at the head of {strength:,} men" if strength else ""
            line = (f"{shown} — {title or kingdom} · his kingdom has broken with France and he "
                    f"keeps his crown{men}")
        else:
            state, loyalty = "fallen", 0
            line = f"{shown} — {title or kingdom} · the kingdom is no more"
        out.append({"king": king, "king_display": shown, "king_kind": kind, "crown": title,
                    "kingdom": str(tag), "kingdom_display": kingdom, "seat": seat,
                    "strength": int(strength), "loyalty": int(loyalty), "state": state,
                    "line": line})
    return out


def rebel_king_words(world, tag: str) -> str:
    """The rebellion notice's second sentence where the kingdom has a
    marshal king: he keeps his crown and turns on his maker (Murat, 1814).
    '' for a prince, a regency, or no crown."""
    record = (getattr(world, "nation_formations", None) or {}).get(tag)
    if not isinstance(record, dict) or record.get("king_kind") != KIND_MARSHAL:
        return ""
    shown = str(record.get("king_display") or record.get("king") or "")
    title = str(record.get("crown") or "")
    crown = f" as {title}" if title else ""
    return f" {shown}, whom you crowned{crown}, keeps his throne and turns his corps against you."


def resolve_king(world, carver: str, name: str) -> Tuple[str, str, str]:
    """(name, kind, '') for a lawful king, else ('', '', the refusal's words).
    An empty name is a regency — lawful."""
    name = str(name or "").strip()
    if not name:
        return "", "", ""
    if not a_marshal_may_reign():
        return "", "", "No king may be seated at this table, Sire."
    for marshal in (getattr(world, "marshals", {}) or {}).values():
        if str(marshal.name) == name:
            if marshal_may_be_crowned(world, marshal, carver):
                return name, KIND_MARSHAL, ""
            return "", "", (f"{humanize_entity_name(name)} has not the laurels for a crown, Sire — "
                            f"a throne wants a man the army celebrates.")
    if name in princes(world):
        if str(carver) != str(getattr(world, "player_nation", "France")):
            return "", "", "A prince of the Imperial house reigns for the Emperor alone."
        where = reigning_prince_of(world, name)
        if where:
            from backend.game_logic.formations import formed_display_name
            return "", "", f"{name} already reigns in {formed_display_name(world, where)}, Sire."
        return name, KIND_PRINCE, ""
    return "", "", f"No {name} stands on the roster or in the Imperial house, Sire."


def stamp_king_on_clause(world, clause: Dict[str, Any], carver: str,
                         name: str) -> Tuple[Dict[str, Any], str]:
    """The add verb's arm: a lawful `king` stamped on the clause (`king`,
    `king_kind`, `king_display`), else the clause unchanged and the words.
    The template's crown title rides as `crown` so the world-less readers
    (the table's words, the confirm popup) can name the throne."""
    king, kind, why = resolve_king(world, carver, name)
    if why:
        return clause, why
    out = dict(clause)
    if king:
        out["king"] = king
        out["king_kind"] = kind
        out["king_display"] = humanize_entity_name(king) if kind == KIND_MARSHAL else king
    return out, ""


# ═══════════════════════════════════════════════════════════════════════
# The erection — the crown's teeth at the ONE apply site
# ═══════════════════════════════════════════════════════════════════════

def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(value)))


def seat_of(world, tag: str) -> str:
    return str((getattr(world, "nation_capitals", {}) or {}).get(tag) or "")


def enthrone(world, tag: str, clause: Dict[str, Any], carver: str) -> Dict[str, Any]:
    """The king seated: a marshal re-homed to the client's colours with his
    corps and set at the seat (`doctrines.set_marshal_nation`, THE setter);
    the hygiene a removal owes (his reward rows, his standing question, the
    orders aimed at him); the client's loyalty seeded from his trust; the
    passed-over marshals' grievance. A prince seats at `PRINCE_LOYALTY`.
    Returns the king's record for the row and the beat ({} for a regency
    or with the seam down)."""
    king = str(clause.get("king") or "")
    kind = str(clause.get("king_kind") or "")
    if not king or kind not in KINDS or not a_marshal_may_reign():
        return {}
    row = (getattr(world, "vassals", {}) or {}).get(tag)
    if not isinstance(row, dict):
        return {}
    passed_over = [m for m in marshals_with_laurels(world, carver) if str(m.name) != king]
    record: Dict[str, Any] = {"king": king, "king_kind": kind,
                              "king_display": str(clause.get("king_display") or king),
                              "crowned_turn": int(getattr(world, "current_turn", 0))}
    if kind == KIND_MARSHAL:
        marshal = (getattr(world, "marshals", {}) or {}).get(king)
        if marshal is None or not marshal_may_be_crowned(world, marshal, carver):
            return {}
        record["corps"] = int(getattr(marshal, "strength", 0) or 0)
        record["trust_at_crowning"] = int(getattr(getattr(marshal, "trust", None), "value", 0) or 0)
        _depart(world, marshal, tag)
        row["loyalty"] = _clamp(record["trust_at_crowning"], *KING_LOYALTY_BOUNDS)
        _aggrieve(world, passed_over, marshal, KING_PASSED_OVER_TRUST)
    else:
        row["loyalty"] = int(PRINCE_LOYALTY)
        _aggrieve(world, passed_over, None, PRINCE_PASSED_OVER_TRUST)
    record["loyalty"] = int(row["loyalty"])
    record["passed_over"] = [str(m.name) for m in passed_over]
    row.update({k: v for k, v in record.items()
                if k in ("king", "king_kind", "king_display", "crowned_turn")})
    return record


def _depart(world, marshal, tag: str) -> None:
    """The marshal leaves the roster for his throne — the removal's hygiene
    (`WorldState.stand_down_marshal`'s, without the pop: he lives on under
    the client's colours), then THE nation setter and the seat."""
    from backend.game_logic.doctrines import set_marshal_nation
    from backend.game_logic.dotation import dismiss_reward_notices
    from backend.notifications import dismiss_marshal_ask
    dismiss_reward_notices(world, marshal)
    dismiss_marshal_ask(world, marshal.name)
    from backend.models.world_state import clear_order_bound_interrupt
    for other in (getattr(world, "marshals", {}) or {}).values():
        order = getattr(other, "strategic_order", None)
        if (order and getattr(order, "target_type", "") == "marshal"
                and getattr(order, "target", "") == marshal.name):
            other.strategic_order = None
            clear_order_bound_interrupt(other)
    marshal.strategic_order = None
    clear_order_bound_interrupt(marshal)
    marshal.glory_crowned = False
    marshal.jealous_of = None
    marshal.jealousy_turns_remaining = 0
    marshal.original_nation = None
    set_marshal_nation(world, marshal, tag)
    seat = seat_of(world, tag)
    if seat:
        marshal.location = seat


def _aggrieve(world, passed_over: List[Any], king, trust_delta: int) -> None:
    """The passed-over marshals' authored grievance: trust toward the
    Emperor, and — when the crown went to a peer — envy toward the king
    (the jealousy ladder's own grievance, forced; a prince is no object of
    a marshal's envy, so his slight is the trust alone, the sharper)."""
    if not passed_over:
        return
    from backend.game_logic.jealousy import apply_jealousy, jealousy_dormant
    # The council's own stash — `advance_turn` folds it into the morning's
    # tactical events (the recruitment rung's idiom).
    events = getattr(world, "_pending_jealousy_turn_events", None)
    if events is None:
        events = []
        world._pending_jealousy_turn_events = events
    dormant = jealousy_dormant(world)
    for marshal in passed_over:
        if hasattr(marshal, "modify_trust"):
            marshal.modify_trust(int(trust_delta))
        if king is not None and not dormant and getattr(marshal, "jealous_of", None) is None:
            apply_jealousy(world, marshal, king, delta=3, threshold=1, events=events, forced=True)


def on_crown_erected(world, tag: str, template: dict, carver: str,
                     clause: Dict[str, Any]) -> Dict[str, Any]:
    """The crown's teeth after `create_client_nation` (the ONE apply site):
    the title and the recognition field on the row, the Alarm on the
    carver's house, the king seated. Returns the crown's record for the
    beat ({} for a plain carve or with the seam down)."""
    if not a_crown_is_erected() or not is_crown(template):
        return {}
    row = (getattr(world, "vassals", {}) or {}).get(tag)
    if not isinstance(row, dict):
        return {}
    title = crown_title(template)
    row["crown"] = title
    row.setdefault("recognized_by", [])
    from backend.game_logic.alarm import ALARM_CAPITAL, house_leader
    from backend.game_logic.coalition import add_threat
    leader = house_leader(world, carver) or carver
    add_threat(world, int(ALARM_CAPITAL), f"crown:{tag}", target=leader)
    king = enthrone(world, tag, clause, carver)
    withheld = withholding_courts(world, tag)
    # G2-RECOG: the card speaks the reception AS THE TREATY LEAVES IT. The
    # court out of whose lands the crown is carved recognizes it by this
    # very instrument (`note_peace_signed`, one stage on — the one writer),
    # so the Proclamation must not name her among the courts that withhold:
    # the played campaign's card read "Austria, Russia and Britain withhold
    # recognition" above a rail line saying Vienna had recognized it.
    ceder = str((clause or {}).get("from") or "")
    if the_war_names_the_beaten() and ceder:
        withheld = [court for court in withheld if court != ceder]
    record = {"crown": title, "alarm": int(ALARM_CAPITAL), "withheld_by": withheld}
    record.update(king)
    return record


def withholding_courts(world, tag: str) -> List[str]:
    """The legitimist courts that withhold recognition of `tag`'s crown
    today — authored, active, not the carver's own house, not yet in the
    row's `recognized_by`. DY-7 adds the condition's read (`until:
    beaten`) and the teeth; DY-6 speaks the list."""
    row = (getattr(world, "vassals", {}) or {}).get(tag) or {}
    if not isinstance(row, dict) or not row.get("crown"):
        return []
    lord = str(row.get("lord") or "")
    granted = {str(c) for c in (row.get("recognized_by") or [])}
    active = set(world.get_active_nations())
    out = []
    for court in legitimists(world):
        if court in active and court != lord and court != tag and court not in granted:
            out.append(court)
    return out


# ═══════════════════════════════════════════════════════════════════════
# The words
# ═══════════════════════════════════════════════════════════════════════

def reign_words(record: Dict[str, Any]) -> str:
    """"Murat takes the crown as King of Naples" / "Joseph Bonaparte reigns
    as King of Westphalia" / '' for a regency."""
    king = str(record.get("king_display") or record.get("king") or "")
    title = str(record.get("crown") or "")
    if not king:
        return ""
    if record.get("king_kind") == KIND_MARSHAL:
        return f"{king} takes the crown as {title}" if title else f"{king} takes the crown"
    return f"{king} reigns as {title}" if title else f"{king} reigns"


def king_clause_words(clause: Dict[str, Any]) -> str:
    """The table's suffix: " under Murat" / " under Joseph Bonaparte" / ''."""
    king = str(clause.get("king_display") or clause.get("king") or "")
    return f" under {king}" if king else ""


def card_lines(record: Dict[str, Any], sponsor_display: str) -> List[str]:
    """The Proclamation card's crown lines — at most TWO, so the card still
    reads whole at every UI scale (the SF-RR5 frame pin): the reign with its
    price, and the court's reception (the passed-over, the withholding
    courts). A regency adds its reception alone (the blurb names the crown)."""
    lines: List[str] = []
    reign = reign_words(record)
    if reign:
        if record.get("king_kind") == KIND_MARSHAL:
            corps = int(record.get("corps", 0) or 0)
            lines.append(f"{reign}; his corps ({corps:,}) goes with him — "
                         f"its loyalty is his trust ({int(record.get('loyalty', 0))})")
        else:
            lines.append(f"{reign}; no sword is lost (loyalty {int(record.get('loyalty', 0))})")
    reception: List[str] = []
    passed = [humanize_entity_name(n) for n in record.get("passed_over") or []]
    if reign and passed:
        verb = "hears" if len(passed) == 1 else "hear"
        reception.append(f"{_and_list(passed)} {verb} of the crown with ill grace")
    withheld = [humanize_entity_name(c) for c in record.get("withheld_by") or []]
    if withheld:
        verb = "withholds" if len(withheld) == 1 else "withhold"
        reception.append(f"{_and_list(withheld)} {verb} recognition of the crown")
    if reception:
        lines.append(" — ".join(reception))
    return lines


def _and_list(items: List[str]) -> str:
    items = [str(i) for i in items if i]
    if len(items) <= 1:
        return items[0] if items else ""
    return ", ".join(items[:-1]) + " and " + items[-1]


# ═══════════════════════════════════════════════════════════════════════
# DY-7 RECOGNITION (DYNAMISM_SPEC.md §6; the gate's Q4 as ruled at §6a —
# the shape session E's, the teeth session F's, November 10, 2026).
#
# THE LEGITIMISTS WITHHOLD (seam `the_legitimists_withhold`, row T8-RECOG):
# the scenario's `crowns.recognition` block names the legitimist courts
# (Austria, Russia, Britain) and the condition `until: "beaten"` — a
# legitimist withholds recognition of a new crown until it has signed a
# peace as the LOSER with the crown's lord's house (the Tilsit reading:
# Russia recognized Warsaw by the treaty that beat her; Pressburg
# recognized the Kingdom of Italy). The record is the row's `recognized_by`,
# written at the peace chokepoints (`settlement_ratify._record_common_peace_
# treaties`, the bilateral `_ratify_treaty`, the dictated truce exit), never
# a scan: the loser of a signed peace is the court whose burden under its
# clauses is the greater (`peace_loser` — a white peace beats nobody). A
# sitting Congress may GRANT it (the same instrument that rules a Question,
# `congress_grants` beside `questions.congress_rules`): every withholding
# legitimist among the great powers that answers the Congress RECOGNIZES
# (its treaty latch, or gone into the Emperor's house) grants the crowns of
# the Emperor's house; one that REFUSES the Congress on its last day refuses
# the crown too (once a sitting, `recognition_refused` on the row). A grant
# or a refusal is a beat — ONE log row (`recognition`, the census 185 → 186)
# and a HIGH dispatch line in words, never a figure.
#
# AN UNRECOGNIZED CROWN PAYS (seam `an_unrecognized_crown_pays`, row
# T8-PRICE) — three prices, the AI's crowns paying the same (GR5):
#   * at the table — a court that withholds recognition of a crown of the
#     proposing side's house prices it on her row: N-DY7 −5 a crown, capped
#     at −15 (`table_component` on the settlement scorer, `bilateral_
#     component` on the bilateral formula — the bond's two seats);
#   * in trade — the LORD's trade with each withholding court halved
#     (`trade_loss`, applied at `diplomacy.process_trade_income` beside the
#     blockade's arm — one factor, one site; the Strategic Ledger's signed
#     "Recognition" Net component). The spec's letter said the client's
#     income; a vassal pair trades nothing in this engine (tribute replaces
#     trade — `calculate_trade_breakdown` skips every vassal pair), so the
#     client's rows are an empty set and the price would have been a promise
#     with no teeth. It falls where a crown's trade price can be felt: on the
#     house that raised it. Recorded at §6c.
#   * on awakened soil — the client dial's −2 becomes −3 while the crown is
#     unrecognized (`dial_extra`, read by `awakening.client_dial`; the §5
#     interplay DY-7 owns).
#
# THE WORDS: the Diplomatic Ledger's nations tab (a crown's row names who
# withholds; a legitimist's row names the crowns of ours it withholds), the
# Vassals tab's card, the Proclamation card (DY-6), Talleyrand's counsel — a
# reading, never a lookup (`counsel_line`).
# ═══════════════════════════════════════════════════════════════════════

RECOGNITION_LOG_TYPE = "recognition"
RECOG_TABLE_MALUS = 5                # N-DY7: a crown unrecognized, per crown, on the withholding court's row
RECOG_TABLE_CAP = 15                 # N-DY7: the malus capped (three crowns' worth)
RECOG_TRADE_FACTOR = 0.5             # N-DY7: the lord's trade with a withholding court halved
RECOG_DIAL_EXTRA = -1                # N-DY7: the dial's −2 becomes −3 while unrecognized
DIAL_LABEL_UNRECOGNIZED = "the people's awakening — the crown unrecognized"
BY_PEACE = "peace"
BY_CONGRESS = "congress"


def the_legitimists_withhold() -> bool:
    """T8-RECOG: the condition's read at the peace chokepoints (`until:
    beaten` — a legitimist that signs a peace as the loser with the crown's
    house recognizes it), the Congress's grant and refusal, the beats. Down:
    `recognized_by` is never written — the legitimists withhold for ever and
    nothing is said of it (session E's words stand)."""
    return True


def the_war_names_the_beaten() -> bool:
    """G2-RECOG (the played campaign, November 11, 2026): the court beaten
    by a peace is the court the WAR went against (the pair's score past the
    bar the ratification record itself calls a victory), the clause burden
    deciding only a drawn war — and the court out of whose lands a crown is
    carved recognizes that crown by the treaty that erects it. Down: the
    loser is read off the clause burden alone (session F), so an indemnity
    the victor pays for a carve names the victor beaten and the ceding court
    withholds recognition of the kingdom it signed over."""
    return True


# The ratification record's own line (`world_state._ratify_player_events`:
# a pair score of 30 or more is a victory) — one bar, read here by name.
BEATEN_WAR_SCORE = 30


def an_unrecognized_crown_pays() -> bool:
    """T8-PRICE: the three prices of a crown unrecognized — the table's
    malus, the lord's trade halved, the dial −3 on awakened soil. Down: a
    withheld crown costs nothing (session E's tree)."""
    return True


# ── the rows and the houses ────────────────────────────────────────────

def crown_rows(world) -> List[Tuple[str, Dict[str, Any]]]:
    """Every crown's (tag, row), sorted — the vassal rows, never the map."""
    out: List[Tuple[str, Dict[str, Any]]] = []
    for tag, row in sorted((getattr(world, "vassals", {}) or {}).items()):
        if isinstance(row, dict) and row.get("crown"):
            out.append((str(tag), row))
    return out


def any_crown(world) -> bool:
    """The cheap guard every price reads first: a world with no crown pays
    nothing and scans nothing."""
    return any(isinstance(row, dict) and row.get("crown")
               for row in (getattr(world, "vassals", {}) or {}).values())


def house_of(world, nation: str) -> str:
    """The house a court belongs to — its top overlord, or itself."""
    if not nation:
        return ""
    try:
        return str(world._top_overlord(nation) or nation)
    except Exception as exc:  # a bare fixture without the overlord read
        from backend.errors import report
        report(exc, "crowns.house_of: world._top_overlord")
        return str(nation)


def crown_lord(row: Dict[str, Any]) -> str:
    return str(row.get("lord") or "")


def withheld_crowns(world, court: str, proposer_side_participants) -> List[str]:
    """The crowns of the proposing side's houses that `court` withholds
    recognition of today (the table's and the formula's one read)."""
    houses = {house_of(world, str(p)) for p in (proposer_side_participants or ()) if p}
    houses.discard("")
    if not houses:
        return []
    return [tag for tag, row in crown_rows(world)
            if house_of(world, crown_lord(row)) in houses
            and court in withholding_courts(world, tag)]


def unrecognized(world, client: str) -> bool:
    """A crown client at least one legitimist still withholds."""
    row = (getattr(world, "vassals", {}) or {}).get(client)
    if not isinstance(row, dict) or not row.get("crown"):
        return False
    return bool(withholding_courts(world, client))


# ── the condition's read: beaten ──────────────────────────────────────

def war_loser(world, a: str, b: str) -> str:
    """G2-RECOG: the court the war between `a` and `b` has gone against —
    the pair's score past `BEATEN_WAR_SCORE` (the ratification record's own
    bar for a victory); '' for a drawn war. Read BEFORE the war's cleanup
    pops the score."""
    from backend.game_logic.diplomacy import get_war_score_for
    score = int(get_war_score_for(world, str(a), str(b)) or 0)
    if score >= BEATEN_WAR_SCORE:
        return str(b)
    if score <= -BEATEN_WAR_SCORE:
        return str(a)
    return ""


def peace_loser(a: str, b: str, clauses, beaten: str = "") -> str:
    """The court beaten by a signed peace. G2-RECOG: `beaten` — the court
    the war itself went against (`war_loser`, the dictated exit's own loser)
    — is the answer where the caller knows it; the clause burden
    (`burden_on_nation`, the DEMANDS dialect that knows every type) decides
    only a drawn war. '' for a white peace (nobody beaten) or equal burdens."""
    if the_war_names_the_beaten() and beaten and str(beaten) in (str(a), str(b)):
        return str(beaten)
    from backend.game_logic.diplomatic_templates import burden_on_nation
    rows = [dict(c) for c in (clauses or []) if isinstance(c, dict)]
    if not rows:
        return ""
    burden_a, burden_b = burden_on_nation(rows, str(a)), burden_on_nation(rows, str(b))
    if burden_a > burden_b:
        return str(a)
    if burden_b > burden_a:
        return str(b)
    return ""


def _ceding_courts(clauses) -> Dict[str, str]:
    """{crown tag: the court out of whose lands the treaty erects it} for
    the `create_client` articles of a signed peace."""
    out: Dict[str, str] = {}
    for clause in clauses or []:
        if isinstance(clause, dict) and clause.get("type") == "create_client":
            tag, ceder = str(clause.get("tag") or ""), str(clause.get("from") or "")
            if tag and ceder:
                out[tag] = ceder
    return out


def note_peace_signed(world, a: str, b: str, clauses, beaten: str = "") -> List[Dict[str, Any]]:
    """The peace chokepoints' ONE call: a legitimist that signs this peace
    as the LOSER with the house of a crown's lord recognizes that crown —
    written into the row's `recognized_by`, one beat a crown. G2-RECOG: the
    loser is the court the war went against (`beaten`), and a legitimist
    that signs the article erecting a crown out of its OWN lands recognizes
    that crown by the instrument, whoever is called the loser. Returns the
    rows written ([] where nothing changes: no crown, a white peace, the
    loser no legitimist, the winner's house no lord, the seam down)."""
    if not the_legitimists_withhold() or not any_crown(world):
        return []
    loser = peace_loser(a, b, clauses, beaten)
    seats = legitimists(world)
    winners_house = ""
    if loser and loser in seats:
        winner = str(b) if loser == str(a) else str(a)
        winners_house = house_of(world, winner)
    ceded = _ceding_courts(clauses) if the_war_names_the_beaten() else {}
    out: List[Dict[str, Any]] = []
    for tag, row in crown_rows(world):
        granting: List[str] = []
        if (winners_house and house_of(world, crown_lord(row)) == winners_house
                and loser in withholding_courts(world, tag)):
            granting.append(loser)
        ceder = ceded.get(tag, "")
        if (ceder and ceder in seats and ceder not in granting
                and ceder in (str(a), str(b)) and ceder in withholding_courts(world, tag)):
            granting.append(ceder)
        if granting:
            out.append(_grant(world, tag, row, granting, BY_PEACE))
    return out


# ── the Congress's grant ──────────────────────────────────────────────

def congress_grants(world, final: bool = False) -> List[Dict[str, Any]]:
    """`congress.process_end_of_turn`, beside `questions.congress_rules`: a
    sitting Congress grants the Emperor's crowns the recognition of every
    withholding legitimist among the great powers that answers it
    RECOGNIZES (its treaty latch) or is GONE into his house; on the
    sitting's last tick (`final`) a court that REFUSES the Congress refuses
    the crown — once a sitting (`recognition_refused[court]` = the summons
    turn). A shut-out or suing court has not answered and keeps
    withholding. The Congress is the Emperor's instrument: an AI house's
    crown is recognized by the peace that beats a legitimist, never here."""
    if not the_legitimists_withhold() or not any_crown(world):
        return []
    from backend.game_logic import congress as _congress
    if not _congress.sitting(world):
        return []
    player = str(getattr(world, "player_nation", "") or "")
    powers = set(_congress.great_powers(world))
    summoned = int((_congress.record(world) or {}).get("summoned_turn", _turn(world)) or 0)
    out: List[Dict[str, Any]] = []
    for tag, row in crown_rows(world):
        if house_of(world, crown_lord(row)) != player:
            continue
        withheld = [c for c in withholding_courts(world, tag) if c in powers]
        if not withheld:
            continue
        granting: List[str] = []
        refusing: List[str] = []
        for court in withheld:
            stance = str(_congress.answer(world, court).get("stance") or "")
            if stance in (_congress.RECOGNIZES, _congress.GONE):
                granting.append(court)
            elif final and stance == _congress.REFUSES:
                refusing.append(court)
        if granting:
            out.append(_grant(world, tag, row, granting, BY_CONGRESS))
        if refusing:
            refused = row.setdefault("recognition_refused", {})
            fresh = [c for c in refusing if int(refused.get(c, -1) or -1) != summoned]
            if fresh:
                for court in fresh:
                    refused[court] = summoned
                out.append(_beat(world, tag, row, fresh, BY_CONGRESS, granted=False))
    return out


def _turn(world) -> int:
    return int(getattr(world, "current_turn", 0) or 0)


def _grant(world, tag: str, row: Dict[str, Any], courts: List[str], by: str) -> Dict[str, Any]:
    granted = row.setdefault("recognized_by", [])
    for court in courts:
        if court not in granted:
            granted.append(str(court))
    return _beat(world, tag, row, courts, by, granted=True)


def _beat(world, tag: str, row: Dict[str, Any], courts: List[str], by: str,
          granted: bool) -> Dict[str, Any]:
    """ONE log row (`recognition`) and the HIGH dispatch line, in words."""
    from backend.game_logic.formations import formed_display_name
    seats = [_seat(world, c) for c in courts]
    display = formed_display_name(world, tag)
    message = recognition_words({"display_name": display, "nation": str(tag), "seats": seats,
                                 "granted": bool(granted), "by": str(by)})
    # A dict LITERAL with the literal type, logged by name — the Gazette's
    # producer census (`_log_event_types_written`) follows exactly that.
    event = {
        "type": "recognition",             # == RECOGNITION_LOG_TYPE
        "nation": str(tag),
        "display_name": display,
        "crown": str(row.get("crown") or ""),
        "lord": crown_lord(row),
        "courts": [str(c) for c in courts],
        "seats": seats,
        "granted": bool(granted),
        "by": str(by),
        "message": message,
    }
    world.log_event(event)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, RECOGNITION_LOG_TYPE,
                         {"line": event["message"], "nation": str(tag)}, "always")
    return event


# ── the prices ────────────────────────────────────────────────────────

def table_component(world, *, court: str, proposer_side_participants) -> Dict[str, Any]:
    """The settlement scorer's `crown_recognition` row (the bond's seat):
    −`RECOG_TABLE_MALUS` for each crown of the proposing side's houses that
    `court` withholds, capped at −`RECOG_TABLE_CAP`; 0 with no crown, no
    withholding or the seam down."""
    out: Dict[str, Any] = {"score": 0, "court": str(court), "crowns": [],
                           "malus": int(RECOG_TABLE_MALUS), "cap": int(RECOG_TABLE_CAP)}
    if not an_unrecognized_crown_pays() or not any_crown(world):
        return out
    crowns = withheld_crowns(world, str(court), proposer_side_participants)
    out["crowns"] = list(crowns)
    out["score"] = -min(int(RECOG_TABLE_CAP), int(RECOG_TABLE_MALUS) * len(crowns))
    return out


def bilateral_component(world, *, court: str, proposer: str) -> int:
    """The bilateral formula's seat: the same read, the proposer alone."""
    return int(table_component(world, court=court,
                               proposer_side_participants=[proposer])["score"])


def trade_loss(world, breakdown: Dict[str, List[Tuple[str, int, str]]]) -> Dict[str, int]:
    """{lord: gold lost this turn} — a crown's lord trades at half with each
    court that withholds recognition of one of its crowns (one halving a
    court, however many crowns); the signed "Recognition" Net component.
    {} with no crown or the seam down. Reads the one per-partner source
    (`calculate_trade_breakdown`), never the map."""
    if not an_unrecognized_crown_pays() or not any_crown(world):
        return {}
    withheld_by_lord: Dict[str, set] = {}
    for tag, row in crown_rows(world):
        courts = withholding_courts(world, tag)
        if courts:
            withheld_by_lord.setdefault(crown_lord(row), set()).update(courts)
    out: Dict[str, int] = {}
    for lord, courts in sorted(withheld_by_lord.items()):
        loss = 0
        for partner, amount, _state in (breakdown or {}).get(lord) or []:
            if partner in courts and int(amount) > 0:
                loss += int(amount) - int(int(amount) * RECOG_TRADE_FACTOR)
        if loss > 0:
            out[lord] = int(loss)
    return out


def dial_extra(world, client: str) -> int:
    """`awakening.client_dial`: −1 more a turn (−2 → −3) on a crown client's
    awakened people while a legitimist withholds; 0 otherwise."""
    if not an_unrecognized_crown_pays() or not client:
        return 0
    return int(RECOG_DIAL_EXTRA) if unrecognized(world, client) else 0


# ── the words ─────────────────────────────────────────────────────────

def _seat(world, court: str) -> str:
    """A great court by its seat ("Vienna"), as the Alarm names them."""
    from backend.game_logic.alarm import _seat as alarm_seat
    return alarm_seat(world, court)


def _named(world, tag: str) -> str:
    from backend.display_names import with_definite_article
    from backend.game_logic.formations import formed_display_name
    return with_definite_article(formed_display_name(world, tag))


def recognition_words(event: Dict[str, Any]) -> str:
    """The beat's sentence — R7 names, never a figure."""
    from backend.display_names import with_definite_article
    seats = [str(s) for s in (event.get("seats") or []) if s]
    name = with_definite_article(str(event.get("display_name") or event.get("nation") or ""))
    who = _and_list(seats) or "the court"
    one = len(seats) == 1
    if event.get("granted") and event.get("by") == BY_PEACE:
        return (f"{who} recognizes {name} and its crown, by the peace that beat her."
                if one else f"{who} recognize {name} and its crown, by the peace that beat them.")
    if event.get("granted"):
        verb = "acknowledges" if one else "acknowledge"
        return f"The Congress recognizes {name}: {who} {verb} its crown."
    return (f"{who} refuses {name} its crown — the Congress rises without her word."
            if one else f"{who} refuse {name} its crown — the Congress rises without their word.")


def oneliner(event: Dict[str, Any]) -> str:
    """The campaign log's row: the courts' news with the beat's lead."""
    lead = "RECOGNITION" if event.get("granted") else "RECOGNITION REFUSED"
    return f"{lead} — {recognition_words(event)}"


def ledger_crown_line(world, tag: str) -> str:
    """The nations tab and the Vassals card, a crown client's row: the
    title, and who withholds ('' for a plain court)."""
    row = (getattr(world, "vassals", {}) or {}).get(tag)
    if not isinstance(row, dict) or not row.get("crown"):
        return ""
    title = str(row.get("crown") or "")
    courts = withholding_courts(world, tag)
    king = str(row.get("king_display") or row.get("king") or "")
    reign = f" — {king} reigns" if king else " — a regency"
    if not courts:
        return f"{title}{reign}; recognized by every court"
    seats = [_seat(world, c) for c in courts]
    verb = "withholds" if len(seats) == 1 else "withhold"
    return f"{title}{reign}; {_and_list(seats)} {verb} recognition"


def ledger_recognition_line(world, court: str) -> str:
    """The nations tab, a legitimist's row: the crowns of the Emperor's
    house it withholds, and what that costs ('' where it withholds none)."""
    player = str(getattr(world, "player_nation", "") or "")
    if not player or not any_crown(world):
        return ""
    crowns = withheld_crowns(world, str(court), [player])
    if not crowns:
        return ""
    names = _and_list([_named(world, t) for t in crowns])
    price = ""
    if an_unrecognized_crown_pays():
        malus = min(int(RECOG_TABLE_CAP), int(RECOG_TABLE_MALUS) * len(crowns))
        price = f" — every peace we put to her is priced for it (−{malus}), our trade with her halved"
    return f"withholds recognition of {names}{price}"


def counsel_line(world, court: str) -> str:
    """Talleyrand's reading of a court that withholds a crown of ours — a
    sentence on the advisory, never a lookup ('' where there is nothing to
    read)."""
    player = str(getattr(world, "player_nation", "") or "")
    if not player or not any_crown(world):
        return ""
    crowns = withheld_crowns(world, str(court), [player])
    if not crowns:
        return ""
    seat = _seat(world, str(court))
    names = _and_list([_named(world, t) for t in crowns])
    if not an_unrecognized_crown_pays():
        return f"{seat} does not acknowledge {names}, Sire."
    malus = min(int(RECOG_TABLE_CAP), int(RECOG_TABLE_MALUS) * len(crowns))
    return (f"{seat} does not acknowledge {names}, Sire — she prices every peace we put "
            f"to her for it (−{malus}) and trades with us at half, until she is beaten "
            f"or signs at a Congress.")
