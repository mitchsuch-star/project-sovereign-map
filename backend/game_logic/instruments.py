"""The D5 counter-instruments — AI-2b (docs/AI_INTENT_SPEC.md §6 D5, §3.3, §12.3).

Three instruments, one substrate, both directions (GR5 — the records and
the per-turn pass are side-agnostic; whoever holds either end, the same
rules bind):

1. **Compensation — buy off a design** (`world.compensation_bargains`).
   A design bought off by agreement is SUSPENDED (the agenda chokepoint
   skips it) and the bargain becomes a §3.3 standing expectation.
   Reneging on it — retaking what was granted, or making war on the
   court you bought off — is the strongest grievance in the game and a
   weight surge in intent (Stage D adds the may-skip-rungs war).
   *Schönbrunn, December 1805 → Jena.*

2. **Directed sponsorship — aim a power at a target**
   (`world.directed_sponsorships`). A named payer pays a named recipient
   per turn to pursue its design against a named aim. At
   `amount_per_turn: 0` this is **the licence** (§12.3, pin 23): the
   payer has sold not gold but *permission*, and the bond is identical —
   the payer entering the licensed war against its recipient, or
   guaranteeing its aim, is reneging. `kind="neutrality"` is the exact
   inverse flow (§4.2b sell-neutrality): the payer buys the RECIPIENT's
   committed non-interference, and the recipient entering the war
   against the payer is reneging. One record shape, opposite flow —
   one record minted, not two (§12.3).

3. **Guarantee — protect a border** (`world.diplomatic_guarantees`).
   Deters the coveter (an intent weight reduction, shown = applied) and
   stakes the guarantor's credibility: a guarantee not honoured within
   the grace window when the protected court is attacked becomes the
   `guarantee_abandoned` grievance (the enforcement `protection_promised`
   never had).

Serialization: all three stores are world-level lists written through
`to_dict`/`from_dict` (§5 pin 8 — the ladder's history must survive a
save; re-derived bargains would make "no cold-open wars" a lie on load).
Renege/abandonment marks ride the EXISTING serialized grievance store
(`betrayal_history` grievance flags) — no parallel memory is minted.

Beat 4, The Broken Bargain (§4.6a): when the PLAYER is the breaker the
cold envoy arrives through `proposal_result_popup` (the PL-14 outcome
transport) in the Voice Bible register, plus the campaign log and a HIGH
notification. An AI breaker gets the log + notification only — beat 4
is the one beat that is entirely the player's own doing.
"""

from typing import Dict, List, Optional

# ── Blessed constants (in-band tunable; shape changes escalate) ─────────
SPONSORSHIP_DEFAULT_TURNS = 10      # default term of a directed sponsorship
SPONSORSHIP_RELATION_BONUS = 5      # payer↔recipient on grant
BUYOFF_BASE_PRICE = 300             # compensation floor price
BUYOFF_PRICE_PER_WEIGHT = 12        # + per point of design weight
BUYOFF_RELATION_BONUS = 5           # payer↔recipient on a struck bargain
GUARANTEE_RELATION_BONUS = 5        # guarantor↔protected on pledge
GUARANTEE_GRACE_TURNS = 2           # turns the guarantor has to enter the war
RENEGE_RELATION_PENALTY = -25       # breaker↔victim on any renege
INSTRUMENT_DP_COST = 1              # player verbs (charged in-executor)

# Consumed by intent.py (§3.3 / D5-3 — the numbers the ledger shows):
GUARANTEE_WEIGHT_DETERRENT = 8      # coveter's weight drop vs a guaranteed holder
WEIGHT_RENEGED_BARGAIN = 15         # victim's weight surge vs the breaker

# A design bought off sleeps for a TERM, not forever — §3.3's asymmetry
# ("buying a design off does not delete it") plus the review's balance
# hole (a one-time ~1,000g must not delete a great power's design for
# the rest of the campaign). Blessed, in-band tunable; re-check data.
COMPENSATION_TERM_TURNS = 15

_RENEGE_GRIEVANCE_TYPES = ("bargain_reneged", "guarantee_abandoned")


def _pair_aggressor(world, a: str, b: str) -> Optional[str]:
    """Who DECLARED the live war between `a` and `b` — the attribution
    read every renege arm needs (review P1: the symmetric `is_at_war`
    cannot know who entered, so the bound party was branded even when it
    was the one attacked). Reads the durable war_instances side lists
    (`ensure_war_instance_for_pair` seats the originator on `attackers`).
    None when no active instance seats the pair on opposite sides —
    attribution unknown, and no one may be branded on a guess."""
    try:
        war_ids = world.get_war_instances_by_participant(a)
    except Exception:
        return None
    instances = getattr(world, "war_instances", {}) or {}
    for war_id in war_ids:
        instance = instances.get(war_id) or {}
        # Active filter is `ended_turn` (spec §7.3 — the field the
        # participant index itself filters on); an ended war must never
        # attribute a fresh renege.
        if instance.get("ended_turn") is not None:
            continue
        attackers = set(instance.get("attackers") or [])
        defenders = set(instance.get("defenders") or [])
        if a in attackers and b in defenders:
            return a
        if b in attackers and a in defenders:
            return b
    return None


def _war_is_post_mint(world, a: str, b: str, minted_turn: int) -> bool:
    """Did the live war between the parties start ON or AFTER the record
    was minted? A pre-existing war can never be 'entering the war later'
    (§3.3's renege is an ACT, not a state)."""
    pair = world._make_diplo_key(a, b)
    war_start = (getattr(world, "war_start_turns", {}) or {}).get(pair)
    if war_start is None:
        return False
    return int(war_start) >= int(minted_turn)


def _next_seq(records: List[Dict]) -> int:
    return len(records) + 1


def _mint_grievance(world, *, breaker: str, victim: str,
                    grievance_type: str, source: str) -> None:
    """Write the renege/abandonment onto the SERIALIZED grievance store."""
    from backend.game_logic.diplomacy import (
        _add_grievance_flag,
        _allocate_episode_id,
    )
    episode_id = _allocate_episode_id(world, prefix="instrument")
    _add_grievance_flag(
        world,
        breaker=breaker,
        victim=victim,
        grievance_type=grievance_type,
        episode_id=episode_id,
        source_episode_type=source,
    )


def has_renege_grievance(world, victim: str, breaker: str) -> bool:
    """§3.3's standing mark, read by intent's weight surge: does `victim`
    hold a live bargain-renege / guarantee-abandonment flag against
    `breaker`? The grievance store is DIRECTED — `_betrayal_key` is the
    unsorted "{breaker}|{victim}" — so a mutual renege keeps two distinct
    marks. Flags do not decay; the mark stands until Make Amends clears
    it (the existing FIFO grievance machinery)."""
    history = getattr(world, "betrayal_history", {}) or {}
    record = history.get(f"{breaker}|{victim}") or {}
    for flag in record.get("grievance_flags", []) or []:
        if flag.get("grievance_type") in _RENEGE_GRIEVANCE_TYPES:
            return True
    return False


# ═══════════════════════════════════════════════════════════════════════
# Directed sponsorship (incl. the licence and sell-neutrality)
# ═══════════════════════════════════════════════════════════════════════

def grant_directed_sponsorship(world, *, payer: str, recipient: str,
                               aim: str, amount_per_turn: int,
                               turns: int = SPONSORSHIP_DEFAULT_TURNS,
                               kind: str = "sponsorship") -> Dict:
    """Mint the ONE directed record (§12.3). Side-agnostic — GR5.

    kind="sponsorship": payer funds (amount 0 = licences) recipient's
    design against `aim`; the PAYER is bound (pin 23).
    kind="neutrality": payer buys recipient's non-interference in the
    payer's war concerning `aim`; the RECIPIENT is bound.

    Deduped like `pledge_guarantee` (review fix — repeating an identical
    0-gold licence was a +5-relation-per-cast pump): one live record per
    (kind, payer, recipient, aim). N identical bonds are one bond.
    """
    records = getattr(world, "directed_sponsorships", [])
    for existing in records:
        if (existing.get("kind") == kind
                and existing.get("payer") == payer
                and existing.get("recipient") == recipient
                and existing.get("aim") == aim):
            return {"success": False,
                    "message": (f"An identical compact between {payer} "
                                f"and {recipient} already stands.")}
    record = {
        "id": (f"{kind}:{payer}:{recipient}:"
               f"{int(world.current_turn)}:{_next_seq(records)}"),
        "kind": kind,
        "payer": payer,
        "recipient": recipient,
        "aim": aim,
        "amount_per_turn": max(0, int(amount_per_turn)),
        "started_turn": int(world.current_turn),
        "expiry_turn": int(world.current_turn) + max(1, int(turns)),
        # The term counter (review fix — expiry-by-turn-number paid a
        # player mint 9 times for a promised 10 while an AI mint paid
        # 10, because the AI phase runs before the instruments pass in
        # the same advance_turn): both directions now pay exactly
        # `turns` times, counted, then lapse.
        "turns_remaining": max(1, int(turns)),
    }
    records.append(record)
    world.directed_sponsorships = records
    world.modify_nation_relation(payer, recipient,
                                 SPONSORSHIP_RELATION_BONUS)
    event = {
        "type": "sponsorship_granted",
        "kind": kind,
        "payer": payer,
        "recipient": recipient,
        "aim": aim,
        "amount": int(record["amount_per_turn"]),
        "turns": int(turns),
        "licence": record["amount_per_turn"] == 0 and kind == "sponsorship",
        "turn": int(world.current_turn),
    }
    world.log_event(event)
    return {"success": True, "record": record, "event": event}


def standing_sponsorship_amount(world, payer: str, recipient: str) -> int:
    """The per-turn gold `payer` currently directs at `recipient` across
    live sponsorship-kind records (the AI-2e outbid read)."""
    total = 0
    for record in getattr(world, "directed_sponsorships", []) or []:
        if (record.get("kind") == "sponsorship"
                and record.get("payer") == payer
                and record.get("recipient") == recipient):
            total += int(record.get("amount_per_turn", 0))
    return total


def live_sponsorships_for(world, recipient: str) -> List[Dict]:
    """All live records paying (or licensing) `recipient`."""
    return [r for r in getattr(world, "directed_sponsorships", []) or []
            if r.get("recipient") == recipient]


# ═══════════════════════════════════════════════════════════════════════
# Compensation — buy off a design
# ═══════════════════════════════════════════════════════════════════════

def compute_buyoff_price(world, nation: str) -> Optional[int]:
    """The gold price at which `nation`'s active design can be bought off
    (D4 — no fog: the price is readable before the offer). None when the
    court has no live non-survival design."""
    from backend.game_logic.intent import get_nation_intent
    view = get_nation_intent(nation, world)
    if view.want_id is None or view.survival:
        return None
    return int(BUYOFF_BASE_PRICE + BUYOFF_PRICE_PER_WEIGHT * view.weight)


def create_compensation_bargain(world, *, payer: str, recipient: str,
                                design_id: str, granted: Dict) -> Dict:
    """Record a struck bargain: `recipient`'s design is suspended by
    agreement and the grant becomes a §3.3 standing expectation."""
    records = getattr(world, "compensation_bargains", [])
    record = {
        "id": (f"bargain:{payer}:{recipient}:"
               f"{int(world.current_turn)}:{_next_seq(records)}"),
        "payer": payer,
        "recipient": recipient,
        "design_id": design_id,
        "granted": dict(granted),
        "turn": int(world.current_turn),
        # §3.3's asymmetry made finite: the design SLEEPS for a term,
        # it is not deleted (review balance fix).
        "expires_turn": int(world.current_turn) + COMPENSATION_TERM_TURNS,
    }
    records.append(record)
    world.compensation_bargains = records
    world.modify_nation_relation(payer, recipient, BUYOFF_RELATION_BONUS)
    # The suspension reads through the agenda cache — flush it so the
    # design goes quiet the same turn the bargain is struck (§3.1a b).
    world.invalidate_bloc_members_cache()
    event = {
        "type": "design_bought_off",
        "payer": payer,
        "recipient": recipient,
        "design_id": design_id,
        "granted": dict(granted),
        "turn": int(world.current_turn),
    }
    world.log_event(event)
    return {"success": True, "record": record, "event": event}


def design_suspended(world, nation: str, design_id: str) -> bool:
    """The agenda chokepoint's read: is this deck entry bought off?"""
    for record in getattr(world, "compensation_bargains", []) or []:
        if (record.get("recipient") == nation
                and record.get("design_id") == design_id):
            return True
    return False


# ═══════════════════════════════════════════════════════════════════════
# Guarantee — protect a border
# ═══════════════════════════════════════════════════════════════════════

def pledge_guarantee(world, *, guarantor: str, protected: str) -> Dict:
    """Pledge to defend `protected`. Deters coveters (intent reads it);
    stakes the guarantor's credibility (the abandonment grievance)."""
    records = getattr(world, "diplomatic_guarantees", [])
    for record in records:
        if (record.get("guarantor") == guarantor
                and record.get("protected") == protected):
            return {"success": False,
                    "message": f"{guarantor} already guarantees {protected}."}
    record = {
        "id": (f"guarantee:{guarantor}:{protected}:"
               f"{int(world.current_turn)}"),
        "guarantor": guarantor,
        "protected": protected,
        "started_turn": int(world.current_turn),
    }
    records.append(record)
    world.diplomatic_guarantees = records
    world.modify_nation_relation(guarantor, protected,
                                 GUARANTEE_RELATION_BONUS)
    # Deterrence reads through the intent cache — flush.
    world.invalidate_bloc_members_cache()
    event = {
        "type": "guarantee_pledged",
        "guarantor": guarantor,
        "protected": protected,
        "turn": int(world.current_turn),
    }
    world.log_event(event)
    return {"success": True, "record": record, "event": event}


def guarantors_of(world, protected: str) -> List[str]:
    return [r.get("guarantor")
            for r in getattr(world, "diplomatic_guarantees", []) or []
            if r.get("protected") == protected]


# ═══════════════════════════════════════════════════════════════════════
# The per-turn pass — payments, expiry, renege and abandonment
# ═══════════════════════════════════════════════════════════════════════

def _party_gone(world, nation: str) -> bool:
    from backend.game_logic.diplomacy import _is_nation_eliminated
    if nation == getattr(world, "player_nation", "France"):
        return False
    return (nation not in world.get_active_nations()
            or _is_nation_eliminated(world, nation))


def _renege(world, *, breaker: str, victim: str, grievance_type: str,
            source: str, event: Dict, events: List[Dict]) -> None:
    _mint_grievance(world, breaker=breaker, victim=victim,
                    grievance_type=grievance_type, source=source)
    world.modify_nation_relation(breaker, victim, RENEGE_RELATION_PENALTY)
    world.log_event(event)
    events.append(event)
    _emit_broken_bargain_beat(world, breaker=breaker, victim=victim,
                              event=event)
    # The victim's weight surge derives from the grievance — flush so the
    # ledger shows the new number this turn.
    world.invalidate_bloc_members_cache()


def _lapse(world, events: List[Dict], event: Dict) -> None:
    """A record ends WITHOUT a breaker (term served, or a war nobody can
    be honestly blamed for) — logged so the compact never vanishes
    silently from the ledger (review fix: the expiry arm was dead code
    on every surface)."""
    world.log_event(event)
    events.append(event)


def process_instruments(world) -> List[Dict]:
    """One pass per turn: renege detection FIRST (a war escape on the
    expiry turn was a free renege — review fix), then payments on the
    term counter, then lapse. GR8: iterates the three world lists only.

    ATTRIBUTION (review P1 — the direction-blind branding): a war
    between the parties reneges a record only when it started ON/AFTER
    the mint, and the party branded is the war's AGGRESSOR (the
    war_instances attackers side), whoever holds which end of the
    record. §3.3's renege is an ACT — "entering the war later" — never
    a state; a pre-existing war, or one whose declarer cannot be read,
    LAPSES the record without a breaker."""
    events: List[Dict] = []
    turn = int(world.current_turn)

    # ── Directed sponsorships ──
    survivors: List[Dict] = []
    for record in getattr(world, "directed_sponsorships", []) or []:
        payer = record.get("payer", "")
        recipient = record.get("recipient", "")
        aim = record.get("aim", "")
        kind = record.get("kind", "sponsorship")
        minted = int(record.get("started_turn", 0))

        if _party_gone(world, payer) or _party_gone(world, recipient):
            continue

        # Renege / lapse on a war between the parties (checked BEFORE
        # the term so an expiry-turn declaration cannot slip the bond).
        if world.is_at_war(payer, recipient):
            aggressor = _pair_aggressor(world, payer, recipient)
            if (aggressor is not None
                    and _war_is_post_mint(world, payer, recipient, minted)):
                _renege(
                    world, breaker=aggressor,
                    victim=recipient if aggressor == payer else payer,
                    grievance_type="bargain_reneged",
                    source=("neutrality_compact" if kind == "neutrality"
                            else "directed_sponsorship"),
                    event={
                        "type": "sponsorship_reneged",
                        "kind": kind, "breaker": aggressor,
                        "victim": (recipient if aggressor == payer
                                   else payer),
                        "aim": aim, "turn": turn,
                        "licence": (kind == "sponsorship"
                                    and int(record.get("amount_per_turn",
                                                       0)) == 0),
                    },
                    events=events,
                )
            else:
                _lapse(world, events, {
                    "type": "instrument_lapsed",
                    "instrument": kind, "payer": payer,
                    "recipient": recipient, "aim": aim,
                    "reason": "war_unattributed", "turn": turn,
                })
            continue

        # Pin 23's second arm: the payer GUARANTEEING the aim while the
        # sponsorship stands is reneging — but only a guarantee pledged
        # AFTER the sponsorship (a pre-existing one is now refused at
        # the mint gate; via raw API it lapses, not brands).
        if kind == "sponsorship" and aim:
            newer_guarantee = any(
                g.get("guarantor") == payer and g.get("protected") == aim
                and int(g.get("started_turn", 0)) >= minted
                for g in getattr(world, "diplomatic_guarantees", []) or [])
            if payer in guarantors_of(world, aim):
                if newer_guarantee:
                    _renege(
                        world, breaker=payer, victim=recipient,
                        grievance_type="bargain_reneged",
                        source="directed_sponsorship",
                        event={
                            "type": "sponsorship_reneged",
                            "kind": kind, "breaker": payer,
                            "victim": recipient, "aim": aim, "turn": turn,
                            "licence": int(record.get("amount_per_turn",
                                                      0)) == 0,
                        },
                        events=events,
                    )
                else:
                    _lapse(world, events, {
                        "type": "instrument_lapsed",
                        "instrument": kind, "payer": payer,
                        "recipient": recipient, "aim": aim,
                        "reason": "conflicting_guarantee", "turn": turn,
                    })
                continue

        # The term (counted — both directions pay exactly `turns` times).
        remaining = int(record.get(
            "turns_remaining",
            max(0, int(record.get("expiry_turn", turn)) - turn)))
        if remaining <= 0:
            _lapse(world, events, {
                "type": "sponsorship_expired",
                "payer": payer, "recipient": recipient, "aim": aim,
                "kind": kind, "turn": turn,
            })
            continue

        # The payment (0 = the licence — permission needs no gold).
        amount = int(record.get("amount_per_turn", 0))
        if amount > 0:
            payer_gold = int(world.nation_gold.get(payer, 0))
            paid = min(amount, max(0, payer_gold))
            if paid > 0:
                world.nation_gold[payer] = payer_gold - paid
                world.nation_gold[recipient] = int(
                    world.nation_gold.get(recipient, 0)) + paid
        record["turns_remaining"] = remaining - 1
        survivors.append(record)
    world.directed_sponsorships = survivors

    # ── Compensation bargains ──
    survivors = []
    for record in getattr(world, "compensation_bargains", []) or []:
        payer = record.get("payer", "")
        recipient = record.get("recipient", "")
        minted = int(record.get("turn", 0))
        if _party_gone(world, payer) or _party_gone(world, recipient):
            continue

        # A war between the parties: the post-mint AGGRESSOR reneged —
        # the payer tearing up its own purchase, or the bought-off court
        # taking the gold and marching anyway.
        if world.is_at_war(payer, recipient):
            aggressor = _pair_aggressor(world, payer, recipient)
            if (aggressor is not None
                    and _war_is_post_mint(world, payer, recipient, minted)):
                _renege(
                    world, breaker=aggressor,
                    victim=recipient if aggressor == payer else payer,
                    grievance_type="bargain_reneged",
                    source="compensation_bargain",
                    event={
                        "type": "bargain_reneged",
                        "breaker": aggressor,
                        "victim": (recipient if aggressor == payer
                                   else payer),
                        "design_id": record.get("design_id", ""),
                        "turn": turn,
                    },
                    events=events,
                )
            else:
                _lapse(world, events, {
                    "type": "instrument_lapsed",
                    "instrument": "bargain", "payer": payer,
                    "recipient": recipient,
                    "design_id": record.get("design_id", ""),
                    "reason": "war_unattributed", "turn": turn,
                })
            world.invalidate_bloc_members_cache()  # the design wakes
            continue

        # Retaking the granted province (§3.3: the granted object is a
        # hostage) — the grant no longer stands with the recipient's side.
        reneged = False
        granted_region = (record.get("granted") or {}).get("region")
        if granted_region:
            region = world.regions.get(granted_region)
            controller = getattr(region, "controller", None)
            if region is not None and controller:
                effective = world._top_overlord(controller) or controller
                recipient_side = world._top_overlord(recipient) or recipient
                if effective != recipient_side and effective != recipient:
                    payer_side = world._top_overlord(payer) or payer
                    if effective in (payer, payer_side):
                        reneged = True
        if reneged:
            _renege(
                world, breaker=payer, victim=recipient,
                grievance_type="bargain_reneged",
                source="compensation_bargain",
                event={
                    "type": "bargain_reneged",
                    "breaker": payer, "victim": recipient,
                    "design_id": record.get("design_id", ""),
                    "turn": turn,
                },
                events=events,
            )
            continue

        # The term served in full: the design wakes quietly (§3.1a —
        # the want sleeps, it does not die).
        if turn >= int(record.get("expires_turn", turn + 1)):
            _lapse(world, events, {
                "type": "instrument_lapsed",
                "instrument": "bargain", "payer": payer,
                "recipient": recipient,
                "design_id": record.get("design_id", ""),
                "reason": "term_served", "turn": turn,
            })
            world.invalidate_bloc_members_cache()  # the design wakes
            continue
        survivors.append(record)
    world.compensation_bargains = survivors

    # ── Guarantees ──
    survivors = []
    for record in getattr(world, "diplomatic_guarantees", []) or []:
        guarantor = record.get("guarantor", "")
        protected = record.get("protected", "")
        pledged = int(record.get("started_turn", 0))
        if _party_gone(world, guarantor) or _party_gone(world, protected):
            continue

        abandoned = False
        voided = False
        for attacker in world.get_nations_at_war_with(protected):
            if attacker == guarantor:
                # Attribution decides (review fix): the guarantor
                # ATTACKING its ward is abandonment in its purest form;
                # the ward declaring on its guarantor forfeits the
                # protection — the guarantee voids, nobody is branded.
                aggressor = _pair_aggressor(world, guarantor, protected)
                if aggressor == guarantor:
                    abandoned = True
                else:
                    voided = True
                break
            if world.is_at_war(guarantor, attacker):
                continue  # honoured — the guarantor is in the fight
            # Grace runs from the LATER of the war start and the pledge
            # (review fix: a guarantee pledged into an old war branded
            # the guarantor one turn later, before it could ever march).
            pair_key = world._make_diplo_key(protected, attacker)
            war_start = int(
                (getattr(world, "war_start_turns", {}) or {})
                .get(pair_key, turn))
            if turn - max(war_start, pledged) >= GUARANTEE_GRACE_TURNS:
                abandoned = True
                break
        if voided:
            _lapse(world, events, {
                "type": "instrument_lapsed",
                "instrument": "guarantee", "payer": guarantor,
                "recipient": protected,
                "reason": "ward_aggression", "turn": turn,
            })
            world.invalidate_bloc_members_cache()  # the deterrent lifts
            continue
        if abandoned:
            _renege(
                world, breaker=guarantor, victim=protected,
                grievance_type="guarantee_abandoned",
                source="diplomatic_guarantee",
                event={
                    "type": "guarantee_abandoned",
                    "breaker": guarantor, "victim": protected,
                    "turn": turn,
                },
                events=events,
            )
            continue
        survivors.append(record)
    world.diplomatic_guarantees = survivors

    return events


# ═══════════════════════════════════════════════════════════════════════
# Legibility — the ledger's composed lines (R7: backend composes,
# renderers print; None → the row is omitted)
# ═══════════════════════════════════════════════════════════════════════


def build_instruments_line(world, nation: str) -> Optional[str]:
    """One composed 'Compacts:' line for a nation's ledger row — every
    live D5 instrument this court is party to. AI-2b's own render
    (the every-row-lands-its-render rule, §4.6b)."""
    from backend.display_names import display_nation
    pieces: List[str] = []
    for record in getattr(world, "directed_sponsorships", []) or []:
        payer, recipient = record.get("payer"), record.get("recipient")
        if nation not in (payer, recipient):
            continue
        aim = display_nation(record.get("aim") or "")
        amount = int(record.get("amount_per_turn", 0))
        if record.get("kind") == "neutrality":
            pieces.append(
                f"{display_nation(payer)} has bought "
                f"{display_nation(recipient)}'s neutrality")
        elif amount == 0:
            pieces.append(
                f"{display_nation(payer)} licences "
                f"{display_nation(recipient)}'s design on {aim}")
        else:
            pieces.append(
                f"{display_nation(payer)} sponsors "
                f"{display_nation(recipient)} against {aim} "
                f"({amount}g/turn)")
    for record in getattr(world, "compensation_bargains", []) or []:
        if nation not in (record.get("payer"), record.get("recipient")):
            continue
        pieces.append(
            f"{display_nation(record.get('payer'))} bought off "
            f"{display_nation(record.get('recipient'))}'s design")
    for record in getattr(world, "diplomatic_guarantees", []) or []:
        if nation not in (record.get("guarantor"),
                          record.get("protected")):
            continue
        pieces.append(
            f"{display_nation(record.get('guarantor'))} guarantees "
            f"{display_nation(record.get('protected'))}")
    auction = (getattr(world, "allegiance_auctions", {}) or {}).get(nation)
    if auction:
        pieces.append(
            f"allegiance IN PLAY — resolves turn "
            f"{int(auction.get('resolves_turn', 0))}")
    if not pieces:
        return None
    return "; ".join(pieces)


def build_subsidy_payload(world) -> Optional[Dict]:
    """AI-2e §3.7: who the paymaster is paying, how much, and how the
    client is taken away — the most consequential invisible fact, shown.
    None when no subsidy stands this season."""
    from backend.game_logic.agendas import (
        get_paymaster_nation,
        get_paymaster_subsidy_amount,
    )
    from backend.game_logic.coalition import get_british_subsidy_recipient
    payer = get_paymaster_nation(world)
    if payer is None:
        return None
    recipient = get_british_subsidy_recipient(world)
    if not recipient:
        return None
    from backend.display_names import display_nation
    amount = int(get_paymaster_subsidy_amount(world, payer))
    # The tier is treasury-scaled (200 / 300 above 4,000 / 400 above 8,000),
    # so the rate read AFTER the season's income can outrun the sum the
    # season actually delivered — the dispatch says "the subsidy stands at
    # 200" while this line said "pays 300g/turn" in the same breath. State
    # what was DELIVERED this season when a transfer happened (no new
    # serialized state: the transfer already logs itself), and keep the
    # prospective rate beside it when the two disagree.
    delivered = _last_subsidy_delivered(world, payer, recipient)
    if delivered is not None and delivered != amount:
        line = (f"{display_nation(payer)} pays {display_nation(recipient)} "
                f"{delivered}g this season to keep the field "
                f"({amount}g/turn at their present treasury)")
    else:
        line = (f"{display_nation(payer)} pays {display_nation(recipient)} "
                f"{amount}g/turn to keep the field")
    return {
        "payer": payer,
        "recipient": recipient,
        "amount": amount,
        "delivered": delivered,
        "line": line,
        "counterplay": ("Peace, compensation, vassalage or defeat "
                        "removes the client; a richer standing "
                        "sponsorship outbids it."),
    }


def _last_subsidy_delivered(world, payer: str, recipient: str) -> Optional[int]:
    """Gold actually transferred payer→recipient this turn, or None.

    Reads the `british_subsidy` event the transfer already writes
    (`coalition._process_british_subsidy`) — display-only, no new state.
    """
    turn = int(getattr(world, "current_turn", 0) or 0)
    for event in reversed(list(getattr(world, "event_log", None) or [])):
        if int(event.get("turn", -1) or -1) != turn:
            break
        if (event.get("type") == "british_subsidy"
                and event.get("payer") == payer
                and event.get("recipient") == recipient):
            return int(event.get("amount", 0) or 0)
    return None


# ═══════════════════════════════════════════════════════════════════════
# Beat 4 — The Broken Bargain (§4.6a)
# ═══════════════════════════════════════════════════════════════════════

_BROKEN_BARGAIN_LINES = {
    # Register-true cold-envoy lines (Voice Bible: attribution + one
    # sentence, no bargaining). Keyed by grievance family.
    "bargain_reneged": (
        "{diplomat}, without preamble: \"The bargain of turn {turn} is "
        "torn up — by your hand, not ours. {victim} does not forget "
        "what was promised.\""),
    "guarantee_abandoned": (
        "{diplomat}, coldly: \"Your guarantee was tested and found to "
        "be paper. {victim} will remember who did not come.\""),
}


def _emit_broken_bargain_beat(world, *, breaker: str, victim: str,
                              event: Dict) -> None:
    """Beat 4: the cold envoy. Player-breaker → the PL-14 outcome popup
    + HIGH notification + dispatch; AI-breaker → notification + log only
    (the beat that lands hardest is the player's own doing)."""
    from backend.game_logic.dispatch import queue_dispatch_event
    from backend.notifications import (
        DIPLOMATIC_PROPOSAL,
        NotificationPriority,
        create_notification,
    )

    player = getattr(world, "player_nation", "France")
    grievance = ("guarantee_abandoned"
                 if event.get("type") == "guarantee_abandoned"
                 else "bargain_reneged")
    queue_dispatch_event(world, "broken_bargain",
                         {"nation": victim, "breaker": breaker}, "always")

    if breaker != player:
        if victim == player:
            world.notifications.add(create_notification(
                DIPLOMATIC_PROPOSAL,
                NotificationPriority.HIGH,
                f"A bargain broken by {breaker}",
                f"{breaker} has torn up its compact with France. The "
                f"mark against them stands.",
                int(world.current_turn),
            ))
        return

    from backend.game_logic.diplomatic_templates import (
        resolve_named_diplomat,
    )
    diplomat = resolve_named_diplomat("envoy", victim, world)
    line = _BROKEN_BARGAIN_LINES[grievance].format(
        diplomat=diplomat, victim=victim,
        turn=int(event.get("turn", world.current_turn)))
    # Review fix (the NA-6b §17.1 clobber class): the outcome slot may
    # already hold this turn's in-transit proposal answer — never
    # overwrite it. The HIGH notification + campaign log + dispatch
    # beat below carry the reproach either way.
    if world.proposal_result_popup is None:
        world.proposal_result_popup = {
            "target_nation": victim,
            "proposal_type": "The Broken Bargain",
            "outcome": "bargain broken",
            "message": line,
            "feedback": ("The strongest grievance in the game now stands "
                         "against France. Their court's design returns, "
                         "the heavier for it."),
        }
    world.notifications.add(create_notification(
        DIPLOMATIC_PROPOSAL,
        NotificationPriority.HIGH,
        f"{victim} declares the bargain broken",
        f"France's compact with {victim} is torn up — by our hand. "
        f"Their envoy has delivered the reproach.",
        int(world.current_turn),
    ))
