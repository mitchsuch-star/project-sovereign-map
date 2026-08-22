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
# Review fix [r5 HIGH] — the exhausted-pair exit: a non-player, non-vassal
# SUB-PAIR welded inside a player-containing war instance (the 1805 boot
# folds all seven starting wars into ONE instance with France in it) would
# otherwise ratchet to WE 200 with no exit until the player ends the whole
# war. Two spent courts whose side-war is going nowhere sign a white peace
# — §3.1a's descent (c) made real for the co-belligerent minors (Spain's
# own exits, 1795/1802). Vassals stay bound to their lord's war.
PAIR_EXIT_WE_FLOOR = 120            # both sides this weary
PAIR_EXIT_MIN_TURNS = 10            # the pair fought this long
PAIR_EXIT_STAGNANT_SCORE = 15       # |pair war score| within this band
# PC15-D4 (gate ruling, Aug 15 2026): a pair that white-peaced out of
# exhaustion holds its truce this long — written into the SAME
# `armistice_cooldowns` store every war-entry gate already consults
# (declare_war R99 / war_council / ai_diplomacy / the ally-entry blocks),
# so one write floors every channel. 8 turns = 4 months at HC-0's
# half-month turn: longer than a negotiated armistice's 5 (a collapse
# holds longer than a choice), shorter than PAIR_EXIT_MIN_TURNS, so the
# worst-case churn period is >= 18 turns — a campaign season, not zero.
# KNOWN GAP, deliberate: declare_war's ally CASCADE does not read the
# pair cooldown — a floored pair can be re-welded by a third court's
# fresh war; owner = the PC15-15 row's residual in DESIGN_REFINEMENT.
PAIR_EXIT_TRUCE_FLOOR_TURNS = 8


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
        # Review fix [r3 LOW]: the shared apply-guard silently drops a
        # cession that would strip a nation's LAST region below the
        # total-annexation war score — never GENERATE a package the apply
        # step will quietly refuse (the announced peace must match the
        # applied one). Elimination cessions need the ≥90 score.
        from backend.game_logic.settlement_scoring import (
            TOTAL_ANNEXATION_WAR_SCORE,
        )
        loser_region_count = len(world.get_nation_regions(loser))
        ceded = 0
        for region_name in get_agenda_military_targets(winner, world):
            if ceded >= THIRD_PARTY_MAX_CESSIONS:
                break
            region = world.regions.get(region_name)
            if region is None:
                continue
            if getattr(region, "controller", None) != loser:
                continue
            if (loser_region_count - ceded <= 1
                    and winner_score < TOTAL_ANNEXATION_WAR_SCORE):
                continue  # would be the loser's last province
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
        # single-sourced (Aug 2026 audit): the force margin IS the broker
        # ask band — a bare literal here desynced on retune
        margin = BROKER_ASK_MARGIN if force else 0
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
        # seam (mutual exhaustion) or under the broker's auspices.
        # Review hardening [r3 INFO]: a material package that does NOT
        # flow wholly toward the accepter is refused STRUCTURALLY — the
        # broker's force never rams a winner-pays peace through a scored
        # objection (the old guard rested on an unasserted constant
        # coupling).
        material = [t for t in terms
                    if t.get("type") in ("gold_indemnity", "territory_cede",
                                         "gold_lump", "gold_per_turn")]
        surrender_shaped = bool(material) and all(
            t.get("to") == winner and t.get("from") == loser
            for t in material)
        if material and not surrender_shaped:
            return None
        winner_score = int(get_war_score_for(world, winner, loser))
        winner_threshold = effective_peace_threshold(winner, loser, world)
        mutual_exhaustion = (not material
                             and winner_score < winner_threshold + (
                                 BROKER_ASK_MARGIN if force else 0))
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
    applied_clauses = settlement_ratify._apply_settlement_terms(
        world, settlement_terms=terms, war_id=war_id,
        settlement_route_id=f"third_party:{war_id}:{turn}",
    )
    settlement_ratify._resolve_pair_state_transitions(world, plan, terms)
    settlement_ratify._record_common_peace_treaties(
        world, plan=plan, settlement_terms=terms)
    # AI-5b(i) (§3.6): an AI-dictated peace that strips the loser leaves
    # the same durable punitive record the player's table does — Prussia
    # remembers Vienna's Diktat exactly as it would remember Paris's.
    # APPLIED clauses, never the ask (the apply may skip a clause).
    from backend.game_logic.emergent_designs import (
        collect_cessions_from_clauses, record_punitive_cessions,
    )
    record_punitive_cessions(
        world, collect_cessions_from_clauses(applied_clauses))
    world.invalidate_war_instance_indexes()
    world.invalidate_bloc_members_cache()
    world.invalidate_active_nations_cache()
    process_formations(world)

    consequence = _consequence_line(world, winner, loser, terms)
    from backend.display_names import humanize_entity_name
    event = {
        "type": "third_party_peace",
        "war_id": war_id,
        "proposer": loser,
        "accepter": winner,
        "broker": broker,
        "terms": [dict(t) for t in terms],
        "consequence": consequence,
        "message": (f"Peace concluded between {humanize_entity_name(loser)} "
                    f"and {humanize_entity_name(winner)} without France. "
                    f"{consequence}"),
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
        if len(participants) < 2:
            continue
        if player in participants:
            # The player decides its OWN peace — but the non-player,
            # non-vassal SUB-PAIRS welded into this instance still get
            # the exhausted-pair exit (review fix [r5 HIGH]).
            _process_exhausted_pair_exits(world, str(war_id), war, events)
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


def _return_unheld_homeland(world, war_id: str, a: str, b: str) -> List[str]:
    """PC15-D4 piece 3: build territory_cede terms for each direction —
    provinces of one court's HOMELAND (nation_starting_regions) held by
    the other with NO standing marshal of the holder — and run them
    through `settlement_ratify._apply_settlement_terms` (the negotiated
    path's own applier). Returns the region names actually transferred."""
    from backend.game_logic import settlement_ratify

    terms = []
    for holder, owner in ((a, b), (b, a)):
        home = set(
            (getattr(world, "nation_starting_regions", {}) or {}).get(
                owner, []) or [])
        give_back = []
        for region_name in home:
            region = world.regions.get(region_name)
            if region is None or region.controller != holder:
                continue
            standing = [
                m for m in world.get_marshals_in_region(region_name)
                if m.nation == holder and m.strength > 0
                and not getattr(m, "captured_by", "")]
            if standing:
                continue
            give_back.append(region_name)
        if give_back:
            terms.append({"type": "territory_cede", "value": 1,
                          "from": holder, "to": owner,
                          "regions": sorted(give_back)})
    if not terms:
        return []
    applied = settlement_ratify._apply_settlement_terms(
        world, settlement_terms=terms, war_id=str(war_id),
        settlement_route_id=(
            f"pair_exit:{war_id}:{int(world.current_turn)}"))
    returned: List[str] = []
    for clause in applied or []:
        regions = clause.get("regions")
        if regions:
            returned.extend(str(r) for r in regions)
        elif clause.get("region"):
            returned.append(str(clause["region"]))
    return returned


def pair_is_mutually_exhausted(world, a: str, b: str,
                               joined_turn: int) -> bool:
    """Has this pair's war gone still? — the ONE source, two readers.

    Lifted out of `_process_exhausted_pair_exits` (WO slice 5, WO-D5) so
    the war room's counsel and the AI's own pair exit ask exactly the same
    question instead of keeping two copies of one inequality: both courts
    at or past `PAIR_EXIT_WE_FLOOR`, the pair at war at least
    `PAIR_EXIT_MIN_TURNS`, and the pair's war score within
    `PAIR_EXIT_STAGNANT_SCORE` of nothing. Pure — reads world, mutates
    nothing, logs nothing.

    `joined_turn` is the CALLER's, deliberately: the turn-path reader has
    the war instance's own `joined_turn` off `diplo_key_meta` (when this
    pair entered THIS instance), while the advisory has
    `world.war_start_turns` (what `build_active_wars` measures `duration`
    from). Passing it keeps the two provenances explicit instead of
    silently re-deriving one of them inside a function the turn path
    calls — which would be a behaviour change wearing a refactor's coat.

    Short-circuit order is the original's: the war score is only asked for
    once age and weariness both pass.
    """
    from backend.game_logic.diplomacy import get_war_score_for
    turn = int(getattr(world, "current_turn", 0))
    if turn - int(joined_turn) < PAIR_EXIT_MIN_TURNS:
        return False
    exhaustion = getattr(world, "war_exhaustion", {}) or {}
    if (int(exhaustion.get(a, 0)) < PAIR_EXIT_WE_FLOOR
            or int(exhaustion.get(b, 0)) < PAIR_EXIT_WE_FLOOR):
        return False
    return abs(int(get_war_score_for(world, a, b))) <= PAIR_EXIT_STAGNANT_SCORE


def _process_exhausted_pair_exits(world, war_id: str, war: Dict,
                                  events: List[Dict]) -> None:
    """The mutual-exhaustion white peace for a non-player sub-pair inside
    a player-containing instance (constants above). At most ONE pair exit
    per turn world-wide (tempo); the player's own pairs and every vassal's
    pairs are untouchable — a vassal follows its lord's war, and its
    weariness is the lord's pressure to read."""
    from backend.game_logic.diplomacy import (
        cleanup_war_end,
        set_diplomatic_state,
    )
    if getattr(world, "_pair_exit_this_turn", -1) == int(world.current_turn):
        return
    player = getattr(world, "player_nation", "France")
    turn = int(getattr(world, "current_turn", 0))
    vassals = set((getattr(world, "vassals", {}) or {}).keys())
    meta = war.get("diplo_key_meta") or {}

    for pair_key in list(war.get("active_diplo_keys") or []):
        pair_meta = meta.get(pair_key) or {}
        if pair_meta.get("pair_status") != "war":
            continue
        parts = str(pair_key).split("|")
        if len(parts) != 2:
            continue
        a, b = parts
        if player in (a, b) or a in vassals or b in vassals:
            continue
        joined = int(pair_meta.get("joined_turn", war.get("created_turn", turn)) or 0)
        # WO slice 5: the three inequalities now live in ONE place (above),
        # which the war room's counsel reads too. Same order, same answers.
        if not pair_is_mutually_exhausted(world, a, b, joined):
            continue

        set_diplomatic_state(world, a, b, "PEACE", "mutual_exhaustion")
        cleanup_war_end(world, pair_key, conclude_objectives=True)
        # PC15-D4 piece 3 — status-quo-ante-lite: each court returns the
        # OTHER's homeland provinces it holds with no standing army (the
        # measured Moravia shape: a 1-troop detachment, no marshal). The
        # unreturned homeland was the landmine that GUARANTEED re-entry —
        # Austria's P3.7 homeland defense marched straight back through
        # the peace the same turn. Army-occupied ground stays (uti
        # possidetis for ground actually held). Runs through the SAME
        # applier the negotiated third-party path uses, so garrison /
        # cache / threat / event invariants are inherited.
        returned_regions = _return_unheld_homeland(world, war_id, a, b)
        # PC15-D4 piece 1 — the truce floor (constant above).
        world.armistice_cooldowns[pair_key] = PAIR_EXIT_TRUCE_FLOOR_TURNS
        world._pair_exit_this_turn = int(world.current_turn)

        from backend.display_names import humanize_entity_name
        consequence = ("Both courts are spent; their side of the war ends "
                       "while the greater war goes on.")
        if returned_regions:
            consequence += (
                " Unheld homeland returns to its crown: "
                + ", ".join(sorted(returned_regions)) + ".")
        event = {
            "type": "third_party_peace",
            "war_id": war_id,
            "proposer": a,
            "accepter": b,
            "broker": None,
            "consequence": consequence,
            "message": (f"Peace concluded between {humanize_entity_name(a)} "
                        f"and {humanize_entity_name(b)} without France. "
                        f"{consequence}"),
        }
        world.log_event(dict(event))
        events.append(event)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "third_party_peace", {
            "proposer": humanize_entity_name(a),
            "accepter": humanize_entity_name(b),
            "consequence": consequence,
        }, "always")
        return


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
    # Review fix [r3 MEDIUM]: the popup must NAME the war being brokered —
    # without proposer/target the surface reads "between Unknown and
    # France" and the §4.2b informed-refusal contract dies. The asker is
    # the proposer; its enemy leader is the counterparty.
    other = (defenders_leader if asker == attackers_leader
             else attackers_leader)
    proposal = _make_proposal(
        asker, "broker_peace", 6,
        {
            "type": "broker_peace",
            "war_id": war_id,
            "proposer_nation": asker,
            "target_nation": other,
        },
        world,
    )
    if proposal:
        deliver_ai_proposal(proposal, world)
