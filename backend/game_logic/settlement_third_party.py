"""AI-4b — Third-party settlements (docs/AI_INTENT_SPEC.md §4.4, §3.1a(d);
gate record §16.2; landing record §17).

A war between two powers that are not France must be able to END without
the player — through the existing settlement package, headlessly. Without
this, AI-3 is a one-way ratchet: wars that start and never end, and the
ledger shows two powers grinding each other at falling exhaustion.

The seam inventory (§4.4, v1.3) honoured here:

- **Reusable as-is:** the scorer (`settlement_scoring.
  calculate_common_peace_acceptance` — zero player references; called
  through the MODULE attribute so the standing test-patch seam holds) and
  the mutation core (`_apply_settlement_terms` /
  `_resolve_pair_state_transitions` / `_record_common_peace_treaties`).
- **Built here:** the AI proposer decision (the loser sues through the
  SAME `effective_peace_threshold` seam P1 uses — pin 19b), the
  nation-pair-general territorial term generator (the §7a scene-7
  prerequisite), the AI acceptor (scorer verdict, no dialogue), and the
  headless ratify wrapper that NEVER touches `world.dialogue_manager`
  (pin 19c — the player's mounted dialogue is untouchable).
- **The unauthorized_actor gate** (settlement_validation) is bypassed the
  way ratify-time revalidation already bypasses it — by not passing
  `player_nation` — and REPLACED by the explicit
  actor-is-a-belligerent-on-the-proposer-side check below.

Beat 6 — The Congress (§4.6a): the peace is reported as news with the
consequences NAMED — who gained, and whether the winner now stands on a
French frontier.
"""

from typing import Dict, List, Optional

# Blessed numbers (in-band tunable; shape changes escalate).
THIRD_PARTY_MIN_WAR_TURNS = 3       # no instant peace — a war must be felt
THIRD_PARTY_RETRY_TURNS = 2         # re-attempt cadence per war
THIRD_PARTY_MAX_CESSIONS = 2        # decisive victor's territorial take cap
THIRD_PARTY_DECISIVE_SCORE = 20     # the AUD-c decisive band, reused
BROKER_ASK_MARGIN = 10              # "close to the table" band for the ask
BROKER_ASK_COOLDOWN = 6             # per-war courier cadence


def _side_leader_active(war: Dict, side: str) -> Optional[str]:
    """The side's leader if still an active participant, else the first
    active member of that side (a leader may have separate-peaced out)."""
    active = set(war.get("active_participants") or [])
    leader = war.get(f"{'attacker' if side == 'attackers' else 'defender'}_leader")
    if leader in active:
        return str(leader)
    for nation in war.get(side) or []:
        if nation in active:
            return str(nation)
    return None


def build_third_party_terms(world, war: Dict, *, loser: str,
                            winner: str) -> List[Dict]:
    """The nation-pair-general term package: peace + purse-priced
    indemnity (the EC-W4 idiom, via the renamed accepter-general builder)
    + up to two cessions of the winner's own DESIGN provinces still held
    by the loser — a war fought for a want ends by taking it."""
    from backend.game_logic.agendas import get_agenda_military_targets
    from backend.game_logic.ai_diplomacy import _settlement_offer_build_terms
    from backend.game_logic.diplomacy import get_war_score_for

    turn = int(getattr(world, "current_turn", 0))
    war_age = max(0, turn - int(war.get("created_turn", turn)))
    winner_score = int(get_war_score_for(world, winner, loser))
    terms = _settlement_offer_build_terms(
        accepter=winner,
        proposer_nation=loser,
        war_age_turns=war_age,
        accepter_war_score=winner_score,
        world=world,
    )

    if winner_score >= THIRD_PARTY_DECISIVE_SCORE:
        ceded = 0
        for region_name in get_agenda_military_targets(winner, world):
            if ceded >= THIRD_PARTY_MAX_CESSIONS:
                break
            region = world.regions.get(region_name)
            if region is None:
                continue
            if getattr(region, "controller", None) != loser:
                continue
            if getattr(region, "is_capital", False):
                # D2's floor, verbatim: AI wars may eliminate MINORS —
                # a single-province minor's capital IS the design's
                # object (Hanover) — but never a great power's capital
                # by routine cession.
                from backend.game_logic.coalition import _CANONICAL_MAJORS
                if loser in _CANONICAL_MAJORS:
                    continue
            terms.append({
                "type": "territory_cede",
                "from": loser,
                "to": winner,
                "region": region_name,
            })
            ceded += 1
    return terms


def _consequence_line(world, winner: str, loser: str,
                      terms: List[Dict]) -> str:
    """Beat 6's contract: name what the peace MEANS for France."""
    from backend.display_names import humanize_entity_name
    player = getattr(world, "player_nation", "France")
    ceded = [t.get("region") for t in terms
             if t.get("type") == "territory_cede" and t.get("region")]
    parts = []
    if ceded:
        parts.append(f"{humanize_entity_name(winner)} takes "
                     f"{', '.join(str(r) for r in ceded)}.")
    gold = next((t for t in terms if t.get("type") == "gold_indemnity"), None)
    if gold and int(gold.get("amount", 0)) > 0:
        parts.append(f"{humanize_entity_name(str(gold.get('from')))} pays "
                     f"{int(gold.get('amount', 0)):,} gold.")
    borders_france = False
    for region_name in ceded:
        region = world.regions.get(str(region_name))
        if region is None:
            continue
        for adjacent in getattr(region, "adjacent_regions", []) or []:
            neighbour = world.regions.get(adjacent)
            if neighbour is not None and getattr(neighbour, "controller", None) == player:
                borders_france = True
                break
        if borders_france:
            break
    if borders_france:
        parts.append("Their new ground touches our frontier.")
    elif not parts:
        parts.append("A white peace; both courts are free to look elsewhere.")
    else:
        parts.append(f"{humanize_entity_name(winner)} is now free to look "
                     f"elsewhere.")
    return " ".join(parts)


def attempt_third_party_settlement(world, war_id: str, war: Dict,
                                   *, force: bool = False,
                                   broker: Optional[str] = None) -> Optional[Dict]:
    """One negotiated-peace attempt for one AI-vs-AI war. Returns the
    third_party_peace event on success, else None.

    `force` relaxes the loser's suing threshold by the broker margin —
    the broker arm's lever (France pressing both courts to the table).
    """
    from backend.game_logic import settlement_ratify, settlement_scoring
    from backend.game_logic.ai_diplomacy import effective_peace_threshold
    from backend.game_logic.diplomacy import get_war_score_for
    from backend.game_logic.formations import process_formations
    from backend.game_logic.settlement_validation import validate_settlement_terms

    player = getattr(world, "player_nation", "France")
    turn = int(getattr(world, "current_turn", 0))

    attackers_leader = _side_leader_active(war, "attackers")
    defenders_leader = _side_leader_active(war, "defenders")
    if not attackers_leader or not defenders_leader:
        return None

    # Who sues? The side whose leader's war score fell through the SAME
    # seam P1 reads (pin 19b). Deterministic order: worse score first.
    candidates = []
    for proposer, other in ((attackers_leader, defenders_leader),
                            (defenders_leader, attackers_leader)):
        score = int(get_war_score_for(world, proposer, other))
        threshold = effective_peace_threshold(proposer, other, world)
        margin = 10 if force else 0
        if score < threshold + margin:
            candidates.append((score, proposer, other))
    if not candidates:
        return None
    candidates.sort()
    _, loser, winner = candidates[0]

    terms = build_third_party_terms(world, war, loser=loser, winner=winner)

    # The unauthorized_actor REPLACEMENT (§4.4): the proposer must be a
    # belligerent on its own side of this war. Structural validation runs
    # with neither actor_nation nor player_nation (the ratify-time idiom).
    proposer_side = (war.get("side_by_nation") or {}).get(loser)
    if proposer_side not in ("attackers", "defenders"):
        return None
    covered = [n for n in (war.get("active_participants") or [])
               if (war.get("side_by_nation") or {}).get(n) != proposer_side]
    if not covered:
        return None
    validation = validate_settlement_terms(
        terms,
        proposer_side=proposer_side,
        world=world,
        war_instance=war,
        enforce_solvency=False,
    )
    if not validation.get("valid", False):
        return None

    # The AI acceptor: the winning side scores the package through the
    # standing scorer seam — module attribute, so tests can patch it.
    acceptance = settlement_scoring.calculate_common_peace_acceptance(
        world,
        war_id=war_id,
        war_instance=war,
        proposer_side=proposer_side,
        accepting_side=("defenders" if proposer_side == "attackers"
                        else "attackers"),
        accepting_leader=winner,
        proposer_side_leader=loser,
        covered_enemy_participants=covered,
        settlement_terms=terms,
    )
    if acceptance.get("hard_stops"):
        return None  # the scorer's veto is absolute (and the patch seam)
    verdict = str(acceptance.get("verdict", "reject"))
    if verdict != "accept":
        # The victor's-consent arm: the scorer models "why settle while
        # winning" — honest, but SURRENDER terms need no enthusiasm. A
        # package whose every material clause flows TOWARD the accepter
        # is taken; a white peace is taken when BOTH courts crossed the
        # seam (mutual exhaustion); anything else needs the broker.
        material = [t for t in terms
                    if t.get("type") in ("gold_indemnity", "territory_cede",
                                         "gold_lump", "gold_per_turn")]
        surrender_shaped = bool(material) and all(
            t.get("to") == winner and t.get("from") == loser
            for t in material)
        winner_score = int(get_war_score_for(world, winner, loser))
        winner_threshold = effective_peace_threshold(winner, loser, world)
        mutual_exhaustion = (not material
                             and winner_score < winner_threshold + (
                                 10 if force else 0))
        if not surrender_shaped and not mutual_exhaustion and not force:
            return None

    # ── Headless ratify: the four internals + invalidations. Never
    # touches dialogue_manager (pin 19c). ──
    plan = settlement_ratify._build_pair_ratification_plan(
        world, war,
        proposer_side=proposer_side,
        covered=covered,
        settlement_terms=terms,
    )
    if not plan:
        return None
    settlement_ratify._apply_settlement_terms(
        world, settlement_terms=terms, war_id=war_id,
        settlement_route_id=f"third_party:{war_id}:{turn}",
    )
    settlement_ratify._resolve_pair_state_transitions(world, plan, terms)
    settlement_ratify._record_common_peace_treaties(
        world, plan=plan, settlement_terms=terms)
    world.invalidate_war_instance_indexes()
    world.invalidate_bloc_members_cache()
    world.invalidate_active_nations_cache()
    process_formations(world)

    consequence = _consequence_line(world, winner, loser, terms)
    event = {
        "type": "third_party_peace",
        "war_id": war_id,
        "proposer": loser,
        "accepter": winner,
        "broker": broker,
        "terms": [dict(t) for t in terms],
        "consequence": consequence,
        "message": (f"Peace concluded between {loser} and {winner} "
                    f"without France. {consequence}"),
    }
    world.log_event({k: v for k, v in event.items() if k != "terms"})

    from backend.display_names import humanize_entity_name
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "third_party_peace", {
        "proposer": humanize_entity_name(loser),
        "accepter": humanize_entity_name(winner),
        "consequence": consequence,
    }, "always")

    if broker and broker == player:
        # The broker's fee: standing with both courts (the §4.2b broker
        # row — ending someone else's war on your terms, for a price).
        world.modify_nation_relation(player, loser, 10)
        world.modify_nation_relation(player, winner, 10)
    return event


def process_third_party_settlements(world) -> List[Dict]:
    """The once-per-turn pass over live wars France is not in. Deckless /
    legacy worlds: the boot wars there DO include the player or do not
    exist, and no gate below opens — behaviour-neutral by construction."""
    events: List[Dict] = []
    player = getattr(world, "player_nation", "France")
    turn = int(getattr(world, "current_turn", 0))

    for war_id, war in list((getattr(world, "war_instances", {}) or {}).items()):
        if not isinstance(war, dict) or war.get("ended_turn") is not None:
            continue
        participants = list(war.get("active_participants") or [])
        if len(participants) < 2 or player in participants:
            continue
        if turn - int(war.get("created_turn", turn)) < THIRD_PARTY_MIN_WAR_TURNS:
            continue
        last_attempt = war.get("third_party_peace_attempt_turn")
        if (last_attempt is not None
                and turn - int(last_attempt) < THIRD_PARTY_RETRY_TURNS):
            continue
        war["third_party_peace_attempt_turn"] = turn
        event = attempt_third_party_settlement(world, str(war_id), war)
        if event is not None:
            events.append(event)
            continue
        _maybe_ask_france_to_broker(world, str(war_id), war)
    return events


def _maybe_ask_france_to_broker(world, war_id: str, war: Dict) -> None:
    """The §4.2b broker row's courier: when a war is CLOSE to the table
    (the wearier side within the margin of its threshold but not past
    it), that side asks France to convene the congress — the ask rides
    the existing incoming-proposal transport, and refusing it is a
    decision the player made (§4.2b's whole point)."""
    from backend.game_logic.ai_diplomacy import (
        _has_pending_proposal_from,
        _make_proposal,
        deliver_ai_proposal,
        effective_peace_threshold,
    )
    from backend.game_logic.diplomacy import get_war_score_for

    turn = int(getattr(world, "current_turn", 0))
    last_ask = war.get("broker_ask_turn")
    if last_ask is not None and turn - int(last_ask) < BROKER_ASK_COOLDOWN:
        return
    attackers_leader = _side_leader_active(war, "attackers")
    defenders_leader = _side_leader_active(war, "defenders")
    if not attackers_leader or not defenders_leader:
        return
    asker = None
    for proposer, other in ((attackers_leader, defenders_leader),
                            (defenders_leader, attackers_leader)):
        score = int(get_war_score_for(world, proposer, other))
        threshold = effective_peace_threshold(proposer, other, world)
        if threshold + BROKER_ASK_MARGIN > score >= threshold:
            asker = proposer
            break
    if asker is None or _has_pending_proposal_from(asker, world):
        return
    war["broker_ask_turn"] = turn
    proposal = _make_proposal(
        asker, "broker_peace", 6,
        {"type": "broker_peace", "war_id": war_id},
        world,
    )
    if proposal:
        deliver_ai_proposal(proposal, world)
