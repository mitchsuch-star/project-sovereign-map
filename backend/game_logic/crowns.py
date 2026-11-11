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
    record = {"crown": title, "alarm": int(ALARM_CAPITAL),
              "withheld_by": withholding_courts(world, tag)}
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
