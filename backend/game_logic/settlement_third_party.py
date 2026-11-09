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
# The former KNOWN GAP is CLOSED (RS-1, Score Finish Step 1, September 29,
# 2026): the offensive ally CASCADE reads this store too
# (`diplomacy.offensive_call_bar` — a fresh peace, a pair cooldown, or a
# court answering the sitting Congress bars the call), so a floored pair can
# no longer be re-welded by a third court's fresh war.
PAIR_EXIT_TRUCE_FLOOR_TURNS = 8
# PC-F28 (S13e part 4, October 17, 2026): a DECISIVE war between two AI
# courts folded into France's instance could end only by elimination — the
# exhausted-pair exit above needs a stagnant score, and the loser's own
# instance road (`attempt_third_party_settlement`, where a loser SUES past
# P1's threshold) never runs inside a player-containing war. Measured on
# marengo: Austria–Bavaria sat at +35 to +60 for eight turns until Bavaria
# was destroyed. The loser sues after this many turns of its pair.
SUB_PAIR_SUE_MIN_TURNS = 4
# T3-4 (the Tier-3 gate record §13.2 R5, November 9, 2026): a court that
# HOLDS the object of its war sues to lock it — the aim's own provinces
# ceded by treaty, nothing more asked (`war_council.aim_sue_due` /
# `aim_cessions`, ONE predicate with P8-Aim). The loser signs within this
# band of its OWN peace line (`effective_peace_threshold`, the one seam
# P1 and the loser's suit read): P1's base −40 + 15 = −25, R5's line read
# from the loser's side — so at the base reading every held aim at +25 is
# signed, a stubborn diplomat or a war that advances the loser's own
# design holds out longer, and a spent court signs sooner.
AIM_TERMS_BAND = 15
AIM_HELD_EXIT = "aim_held_sue"      # the pair exit's reason (a SIGNED peace)


def a_held_aim_sues() -> bool:
    """T3-4 "the terms" (the Tier-3 gate record §13.2 R5;
    `DYNAMISM_SPEC.md` §2 Tier 3; November 9, 2026): a court that holds
    the object of its war against another AI court offers the aim's terms
    — its delivered provinces ceded by treaty — and the loser signs inside
    `AIM_TERMS_BAND` of its own peace line. An AI-only war ends whole on
    its leaders' aims (`attempt_aim_held_settlement`); a pair inside
    France's war exits on its own (`held_aim_suit`, the pair exits' third
    road). Down: the pre-T3-4 roads alone — an AI war ends only when the
    loser breaks, both are spent, or a court falls."""
    return True


def aim_terms_signable(world, loser: str, winner: str) -> bool:
    """T3-4 — the loser's consent to the aim's LENIENT terms (the aim's
    provinces, no gold): its pair score inside the band ABOVE its own
    peace line (`effective_peace_threshold`, the bond's deeper line
    subtracted — PC-X55's read): `line <= score <= line + AIM_TERMS_BAND`.
    A court still standing but near its breaking point takes the victor's
    limited peace and keeps its purse (Basel, Campo Formio). T3-5 (the
    user's "do what's best"): a court already PAST its line is BROKEN — it
    sues on its own road and pays the war's indemnity as it always has,
    the victor's aim signed over in that treaty (`held_aim_lock`; Pressburg,
    Tilsit). Before, the lenient offer ran first and pre-empted a broken
    loser's own surrender the same turn — on all ten ambient seeds Prussia
    took LESS than Hanover was about to give. An eclipse league's member
    holds the table here as on the loser's own road (OCT27-D2)."""
    from backend.game_logic.ai_diplomacy import effective_peace_threshold
    from backend.game_logic.bond import break_ranks_depth
    from backend.game_logic.diplomacy import get_war_score_for
    score = int(get_war_score_for(world, loser, winner))
    if eclipse_league_holds(world, loser, winner, score):
        return False
    line = int(effective_peace_threshold(loser, winner, world)) - int(
        break_ranks_depth(world, loser, winner)["score"])
    return line <= score <= line + int(AIM_TERMS_BAND)


def held_aim_lock(world, winner: str, loser: str, side=()) -> List[str]:
    """T3-5 — the LOCK: the provinces a peace between `winner` and `loser`
    signs over by name because `winner`'s aim against `loser` is held
    (`war_council.war_aim_held` — the war score not consulted: whoever
    proposes, a peace that ends a war whose aim is held signs it), the
    loser's own homeland held by the winner itself (`aim_cessions`, the
    validator's occupied-homeland clause). `[]` with the seam down (the
    T3-4 seam governs the whole terms road) or nothing held."""
    if not a_held_aim_sues():
        return []
    from backend.game_logic.war_council import aim_cessions, war_aim_held
    if winner == getattr(world, "player_nation", "France"):
        return []
    if not war_aim_held(world, winner, loser, side=side):
        return []
    return list(aim_cessions(world, winner, loser, homeland_only=True))


def held_aim_terms(winner: str, loser: str, cessions: List[str]) -> List[Dict]:
    """T3-4 — the aim's terms in the table's dialect: the peace and one
    cession per delivered province, no indemnity (the aim is the price —
    "AI–AI cessions move provinces ALONG AUTHORED AIMS", never a carve)."""
    terms: List[Dict] = [{"type": "peace"}]
    for region_name in cessions:
        terms.append({"type": "territory_cede", "from": loser, "to": winner,
                      "region": str(region_name)})
    return terms


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
    """The nation-pair-general term package: peace + war-priced
    indemnity (the EC-W4 idiom, via the renamed accepter-general builder;
    the ratifier clamps the transfer to the payer's chest and the record
    reads the APPLIED clause)
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
    # T3-5 — the LOCK: a peace that ends a war whose victor holds its aim
    # signs the aim's provinces over by name (signed title, the loser
    # reconciled), whoever sues — the broken loser pays its indemnity AND
    # signs; the ground is already the victor's, so no cession cap reads it.
    side_of = war.get("side_by_nation") or {}
    opposing = [n for n in (war.get("active_participants") or [])
                if side_of.get(n) != side_of.get(winner)]
    named = {str(t.get("region")) for t in terms if t.get("type") == "territory_cede"}
    for region_name in held_aim_lock(world, winner, loser, side=opposing):
        if region_name in named:
            continue
        terms.append({
            "type": "territory_cede",
            "from": loser,
            "to": winner,
            "region": region_name,
        })
    return terms


def _evacuations_for(world, pairs) -> Dict[str, List[str]]:
    """T3-6 — what this turn's peace on `pairs` evacuated, {holder:
    [provinces]}, read from the titling pass's same-turn hand-off
    (`game_end.title_status_quo_retentions` stashes `evacuated`)."""
    wanted = {str(p) for p in pairs or [] if p}
    turn = int(getattr(world, "current_turn", 0))
    out: Dict[str, List[str]] = {}
    for entry in getattr(world, "_status_quo_titled", None) or []:
        if int(entry.get("turn", -1)) != turn or str(entry.get("pair") or "") not in wanted:
            continue
        for holder, regions in (entry.get("evacuated") or {}).items():
            out.setdefault(str(holder), [])
            out[str(holder)] = sorted(set(out[str(holder)]) | {str(r) for r in regions})
    return out


def _evacuation_words(world, evacuated: Dict[str, List[str]]) -> List[str]:
    from backend.display_names import humanize_entity_name
    from backend.game_logic.war_council import held_aim_clause
    return [f"{humanize_entity_name(holder)} evacuates {held_aim_clause(regions)}."
            for holder, regions in sorted((evacuated or {}).items()) if regions]


def _consequence_line(world, winner: str, loser: str,
                      terms: List[Dict], evacuated=None) -> str:
    """Beat 6's contract: name what the peace MEANS for France. T3-6:
    the ground the winner hands back is named too."""
    from backend.display_names import humanize_entity_name
    player = getattr(world, "player_nation", "France")
    from backend.game_logic.settlement_validation import _territory_term_regions
    ceded = [r for t in terms if t.get("type") == "territory_cede"
             for r in _territory_term_regions(t)]
    parts = []
    if ceded:
        parts.append(f"{humanize_entity_name(winner)} takes "
                     f"{', '.join(str(r) for r in ceded)}.")
    gold = next((t for t in terms if t.get("type") == "gold_indemnity"), None)
    if gold and int(gold.get("amount", 0)) > 0:
        parts.append(f"{humanize_entity_name(str(gold.get('from')))} pays "
                     f"{int(gold.get('amount', 0)):,} gold.")
    parts.extend(_evacuation_words(world, evacuated))
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


def silent_band_white_peace(world, *, loser: str, winner: str,
                            winner_score: int) -> bool:
    """PC-F31 (S13e part 3, October 16, 2026): True when a loser past its own
    peace threshold offers a white peace to a winner whose score is still
    under the decisive band (`SETTLEMENT_OFFER_DECISIVE_WAR_SCORE`, 20) —
    the winner has nothing to dictate yet, so the white peace carries. The
    series attribution holds it down (`--seam backend.game_logic.
    settlement_third_party:silent_band_white_peace=lambda *a, **k: False`)."""
    from backend.game_logic.ai_diplomacy import SETTLEMENT_OFFER_DECISIVE_WAR_SCORE
    return int(winner_score) < int(SETTLEMENT_OFFER_DECISIVE_WAR_SCORE)


def war_is_the_players(world, war: Dict, player: str) -> bool:
    """OCT27-31: a war the player has since joined is the player's to end.
    Down (False): the lingering broker answer that closed it "without France"."""
    return player in (war.get("active_participants") or [])


def client_war_waits_for_france(world, war: Dict, player: str,
                                broker: Optional[str] = None) -> bool:
    """OCT27-D12(b) (ruled as recommended, S14i): a war one of whose
    belligerents answers to the player (its top overlord) is not settled by
    the third-party pass on its own — France's client paid Sweden 4,800 gold
    and France was never asked. It ends when France brokers it (the broker
    ask reaches France for it, `_maybe_ask_france_to_broker`). Down (False):
    the pass settled it alone."""
    if broker == player:
        return False
    for court in war.get("active_participants") or []:
        if court != player and world._top_overlord(court) == player:
            return True
    return False


def eclipse_league_holds(world, court: str, enemy: str, score: int) -> bool:
    """OCT27-D2 (ruled as recommended, S14i): a member of a league formed
    against a court other than the player does not sign a separate peace with
    that court while P1's break-ranks clause gives it no reason of its own
    (`coalition_break_ranks_reason`, the bond's deeper lines included) — the
    same statecraft France's league keeps. Down (False): the members of an
    anti-Austria league sued freely."""
    coalition = getattr(world, "active_coalition", None) or {}
    target = coalition.get("target_nation")
    if not target or target == getattr(world, "player_nation", "France") or enemy != target:
        return False
    if court not in (coalition.get("members") or []):
        return False
    from backend.game_logic.ai_diplomacy import coalition_break_ranks_reason
    return coalition_break_ranks_reason(
        world, court, war_score=int(score),
        diplo_key=world._make_diplo_key(court, enemy)) is None


def bonded_exit_floor(world, a: str, b: str, floor: int) -> int:
    """OCT27-32: a bonded court's mutual-exhaustion floor never stands past
    the cap. `floor` is the caller's: `pair_is_mutually_exhausted` passes its
    own constant (the slice-5 single source - the threshold is read in ONE
    function). Down (`int(a[3]) + int(__import__('backend.game_logic.bond')
    .game_logic.bond.break_ranks_depth(a[0], a[1], a[2])['exhaustion'])`):
    uncapped."""
    from backend.game_logic.bond import break_ranks_depth
    from backend.game_logic.coalition import WAR_EXHAUSTION_MAX
    return min(int(WAR_EXHAUSTION_MAX),
               int(floor) + int(break_ranks_depth(world, a, b)["exhaustion"]))


def attempt_third_party_settlement(world, war_id: str, war: Dict,
                                   *, force: bool = False,
                                   broker: Optional[str] = None) -> Optional[Dict]:
    """One negotiated-peace attempt for one AI-vs-AI war. Returns the
    third_party_peace event on success, else None.

    `force` relaxes the loser's suing threshold by the broker margin —
    the broker arm's lever (France pressing both courts to the table).
    """
    from backend.game_logic import settlement_scoring
    from backend.game_logic.ai_diplomacy import effective_peace_threshold
    from backend.game_logic.diplomacy import get_war_score_for
    from backend.game_logic.settlement_validation import validate_settlement_terms

    player = getattr(world, "player_nation", "France")
    # A war France has since joined is France's to end (the October 27,
    # 2026 sweep: a broker answer accepted after France entered the war
    # closed it "without France", France's own pair with it).
    if war_is_the_players(world, war, player):
        return None
    # OCT27-D12(b): France's client's war is France's to end.
    if client_war_waits_for_france(world, war, player, broker):
        return None

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
        # OCT27-D2 (S14i): an eclipse league's member holds the table until
        # it has a reason of its own to break ranks — the league treats when
        # spent, as France's does.
        if eclipse_league_holds(world, proposer, other, score):
            continue
        # PC-X55 (S14 part 3): a court the league's bond binds against the
        # other sues only past the bond's deeper line (the pair exits' rule).
        from backend.game_logic.bond import break_ranks_depth
        threshold = effective_peace_threshold(proposer, other, world) - int(
            break_ranks_depth(world, proposer, other)["score"])
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
        # PC-F31 (S13e part 3): the silent band — the loser past its
        # threshold, the winner under the decisive band (nothing to dictate),
        # a white peace the scorer refuses: nothing was sent at −12 … −19,
        # peace at −20. A beaten court past its threshold ALWAYS has a letter
        # to send: the white peace is taken as the loser's capitulation-lite
        # (`silent_band_white_peace`).
        band_white = (not material
                      and silent_band_white_peace(world, loser=loser, winner=winner,
                                                  winner_score=winner_score))
        if not surrender_shaped and not mutual_exhaustion and not force and not band_white:
            return None

    return _ratify_third_party(
        world, war_id, war,
        proposer=loser, accepter=winner, winner=winner, loser=loser,
        proposer_side=proposer_side, covered=covered, terms=terms,
        broker=broker)


def _ratify_third_party(world, war_id: str, war: Dict, *, proposer: str,
                        accepter: str, winner: str, loser: str,
                        proposer_side: str, covered: List[str],
                        terms: List[Dict], broker: Optional[str] = None,
                        exit_reason: Optional[str] = None) -> Optional[Dict]:
    """The headless ratify both third-party arms share — the loser's suit
    (`attempt_third_party_settlement`, the proposer the LOSER) and the
    held aim's terms (`attempt_aim_held_settlement`, T3-4, the proposer
    the WINNER). Extracted verbatim from the loser's arm: its event keeps
    its keys and their order byte for byte; the aim arm's event alone
    carries `exit`. Returns the third_party_peace event, or None when the
    plan is empty."""
    from backend.game_logic import settlement_ratify
    from backend.game_logic.formations import process_formations

    player = getattr(world, "player_nation", "France")
    turn = int(getattr(world, "current_turn", 0))
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
    # IQ-3 review: the courts signing here are named, so a league this
    # ratification dissolves reports only courts genuinely still at war.
    from backend.game_logic.coalition import treaty_in_flight
    with treaty_in_flight(world, settlement_ratify.plan_courts(plan)):
        applied_clauses = settlement_ratify._apply_settlement_terms(
            world, settlement_terms=terms, war_id=war_id,
            settlement_route_id=f"third_party:{war_id}:{turn}",
        )
        _resolved, _fa = settlement_ratify._resolve_pair_state_transitions(world, plan, terms)
    # PC-R7 (ii) part 2 (GR5): the articles declared at the war settle at
    # the AI's peace exactly as at the player's.
    from backend.game_logic.declared_goals import settle_at_peace
    settle_at_peace(world, [str(p.get("pair") or "") for p in _resolved or []],
                    list(applied_clauses or []) + list(_fa or []))
    settlement_ratify._record_common_peace_treaties(
        world, plan=plan, settlement_terms=terms)
    # AI-5b(i) (§3.6): an AI-dictated peace that strips the loser leaves
    # the same durable punitive record the player's table does — Prussia
    # remembers Vienna's Diktat exactly as it would remember Paris's.
    # APPLIED clauses, never the ask (the apply may skip a clause).
    from backend.game_logic.emergent_designs import (
        collect_cessions_from_clauses, record_punitive_cessions,
    )
    from backend.game_logic.compensation import compensation_offsets
    record_punitive_cessions(
        world, collect_cessions_from_clauses(applied_clauses),
        offsets=compensation_offsets(applied_clauses))
    world.invalidate_war_instance_indexes()
    world.invalidate_bloc_members_cache()
    world.invalidate_active_nations_cache()
    process_formations(world)

    # What the peace MEANS is what was APPLIED (the October 27, 2026
    # sweep): the ask said "Hanover pays 4,800 gold" where the chest held
    # 120 and 120 moved - the same clamp `record_punitive_cessions` reads.
    settled = list(applied_clauses or []) + list(_fa or [])
    consequence = _consequence_line(
        world, winner, loser, settled,
        evacuated=_evacuations_for(world, [p.get("pair") for p in _resolved or []]))
    from backend.display_names import humanize_entity_name
    event = {
        "type": "third_party_peace",
        "war_id": war_id,
        "proposer": proposer,
        "accepter": accepter,
        "broker": broker,
        "terms": [dict(t) for t in settled],
        "consequence": consequence,
        "message": (f"Peace concluded between {humanize_entity_name(proposer)} "
                    f"and {humanize_entity_name(accepter)} without France. "
                    f"{consequence}"),
    }
    if exit_reason:
        event["exit"] = exit_reason
    world.log_event({k: v for k, v in event.items() if k != "terms"})

    from backend.display_names import humanize_entity_name
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "third_party_peace", {
        "proposer": humanize_entity_name(proposer),
        "accepter": humanize_entity_name(accepter),
        "consequence": consequence,
    }, "always")

    if broker and broker == player:
        # The broker's fee: standing with both courts (the §4.2b broker
        # row — ending someone else's war on your terms, for a price).
        from backend.game_logic.diplomatic_dialogue import modify_relation_booked
        modify_relation_booked(world, player, loser, 10, "broker_fee", player, loser)
        modify_relation_booked(world, player, winner, 10, "broker_fee", player, winner)
    return event


def attempt_aim_held_settlement(world, war_id: str, war: Dict) -> Optional[Dict]:
    """T3-4 — the held aim's terms for one AI-vs-AI war, ended WHOLE on its
    LEADERS' aims (the loser's road ends wars by leaders too; a
    co-belligerent's holdings ride the status quo). The leader whose aim
    against the other is held (`war_council.aim_sue_due`, the whole
    opposing side read for its homeland) proposes the aim's terms
    (`held_aim_terms` — the delivered provinces of the loser's own
    homeland it holds, `aim_cessions`); the loser signs inside its band
    (`aim_terms_signable`). The existing machinery verbatim: the
    validator, the scorer's hard stops (absolute — the standing patch
    seam; its verdict is the harshness ladder's, which this peace does not
    price), the headless ratify. Returns the third_party_peace event
    (`exit` = `AIM_HELD_EXIT`), else None. The broker road
    (`attempt_third_party_settlement`) never runs this arm."""
    if not a_held_aim_sues():
        return None
    from backend.game_logic import settlement_scoring
    from backend.game_logic.settlement_validation import validate_settlement_terms
    from backend.game_logic.war_council import aim_cessions, aim_sue_due

    player = getattr(world, "player_nation", "France")
    if war_is_the_players(world, war, player):
        return None
    if client_war_waits_for_france(world, war, player):
        return None
    attackers_leader = _side_leader_active(war, "attackers")
    defenders_leader = _side_leader_active(war, "defenders")
    if not attackers_leader or not defenders_leader:
        return None
    side_of = war.get("side_by_nation") or {}
    for winner, loser in ((attackers_leader, defenders_leader),
                          (defenders_leader, attackers_leader)):
        winner_side = side_of.get(winner)
        if winner_side not in ("attackers", "defenders"):
            continue
        covered = [n for n in (war.get("active_participants") or [])
                   if side_of.get(n) != winner_side]
        if not covered:
            continue
        if not aim_sue_due(world, winner, loser, side=covered):
            continue
        cessions = aim_cessions(world, winner, loser, homeland_only=True)
        if not cessions or not aim_terms_signable(world, loser, winner):
            continue
        terms = held_aim_terms(winner, loser, cessions)
        validation = validate_settlement_terms(
            terms,
            proposer_side=winner_side,
            world=world,
            war_instance=war,
            enforce_solvency=False,
        )
        if not validation.get("valid", False):
            continue
        acceptance = settlement_scoring.calculate_common_peace_acceptance(
            world,
            war_id=war_id,
            war_instance=war,
            proposer_side=winner_side,
            accepting_side=("defenders" if winner_side == "attackers"
                            else "attackers"),
            accepting_leader=loser,
            proposer_side_leader=winner,
            covered_enemy_participants=covered,
            settlement_terms=terms,
        )
        if acceptance.get("hard_stops"):
            return None  # the scorer's veto is absolute (and the patch seam)
        return _ratify_third_party(
            world, war_id, war,
            proposer=winner, accepter=loser, winner=winner, loser=loser,
            proposer_side=winner_side, covered=covered, terms=terms,
            exit_reason=AIM_HELD_EXIT)
    return None


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
        # T3-4: a leader holding its war's aim offers its terms first.
        event = attempt_aim_held_settlement(world, str(war_id), war)
        if event is None:
            event = attempt_third_party_settlement(world, str(war_id), war)
        if event is not None:
            events.append(event)
            continue
        _maybe_ask_france_to_broker(world, str(war_id), war)
    return events


def _return_unheld_homeland(world, war_id: str, a: str, b: str,
                            keep=()) -> List[str]:
    """PC15-D4 piece 3: build territory_cede terms for each direction —
    provinces of one court's HOMELAND (nation_starting_regions) held by
    the other with NO standing marshal of the holder — and run them
    through `settlement_ratify._apply_settlement_terms` (the negotiated
    path's own applier). Returns the region names actually transferred.
    `keep` (T3-4): provinces this very peace ceded by treaty — signed
    away, never handed back however lightly held."""
    from backend.game_logic import settlement_ratify

    kept = {str(r) for r in keep or ()}
    terms = []
    for holder, owner in ((a, b), (b, a)):
        home = set(
            (getattr(world, "nation_starting_regions", {}) or {}).get(
                owner, []) or [])
        give_back = []
        for region_name in home:
            if region_name in kept:
                continue
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
    from backend.game_logic.bond import break_ranks_depth
    from backend.game_logic.diplomacy import get_war_score_for
    turn = int(getattr(world, "current_turn", 0))
    if turn - int(joined_turn) < PAIR_EXIT_MIN_TURNS:
        return False
    exhaustion = getattr(world, "war_exhaustion", {}) or {}
    # PC-X55 (S14 part 3): a court bound not to sign a separate peace with the
    # other is spent at the bond's deeper line (`bond.break_ranks_depth`).
    # A bonded court's floor never stands past the cap (the October 27,
    # 2026 sweep): 120 + a 300g bond's 90 read 210 where weariness stops
    # at 200, so the mutual-exhaustion exit never fired for the pair.
    _floor_a = bonded_exit_floor(world, a, b, PAIR_EXIT_WE_FLOOR)
    _floor_b = bonded_exit_floor(world, b, a, PAIR_EXIT_WE_FLOOR)
    if (int(exhaustion.get(a, 0)) < _floor_a or int(exhaustion.get(b, 0)) < _floor_b):
        return False
    return abs(int(get_war_score_for(world, a, b))) <= PAIR_EXIT_STAGNANT_SCORE


def sub_pair_loser_sues(world, a: str, b: str, joined_turn: int):
    """PC-F28 — the SEAM: inside a player-containing instance, a non-player,
    non-client sub-pair whose loser's stored pair score has fallen under its
    own P1 threshold (`effective_peace_threshold`, the seam P1 reads) after
    `SUB_PAIR_SUE_MIN_TURNS` of the pair sues; the winner takes the peace on
    the held line (the ground it holds is titled by SR-1a, the unheld
    homeland returned as the exhausted exit returns it). Returns (loser,
    winner, the loser's score) or None — the score read BEFORE the peace
    cleans the pair's ledger. The series attribution holds it down."""
    from backend.game_logic.ai_diplomacy import effective_peace_threshold
    from backend.game_logic.diplomacy import get_war_score_for
    turn = int(getattr(world, "current_turn", 0))
    if turn - int(joined_turn) < SUB_PAIR_SUE_MIN_TURNS:
        return None
    from backend.game_logic.bond import break_ranks_depth
    candidates = []
    for loser, winner in ((a, b), (b, a)):
        score = int(get_war_score_for(world, loser, winner))
        # PC-X55: a bonded loser sues only past the bond's deeper line.
        line = int(effective_peace_threshold(loser, winner, world)) - int(
            break_ranks_depth(world, loser, winner)["score"])
        if score < line:
            candidates.append((score, loser, winner))
    if not candidates:
        return None
    candidates.sort()
    score, loser, winner = candidates[0]
    return loser, winner, int(score)


def client_pair_is_the_lords_war(world, client: str, court: str) -> bool:
    """PC-F29 — the SEAM: a client's pair with `court` is its lord's war (and
    follows the lord out — SR-1b's six roads) while the lord is at WAR with
    that court; otherwise it is the client's own war, which takes the pair
    exits like any court's. Before, every client pair was untouchable here
    whatever its lord was doing (Part III §23: Britain–Holland and Austria–
    the Kingdom of Italy at exhaustion 200 with no road out). The series
    attribution holds it down (always True — the old rule)."""
    row = (getattr(world, "vassals", {}) or {}).get(client) or {}
    lord = str(row.get("lord") or "")
    if not lord or lord == court:
        return True
    return world.get_diplomatic_state(lord, court) == "WAR"


def held_aim_suit(world, a: str, b: str, joined_turn: int):
    """T3-4 — the pair exits' third road: (winner, loser, cessions) when
    one court of a sub-pair holds its war's aim against the other
    (`war_council.aim_sue_due`), the aim's terms carry a province of the
    loser's own homeland (`aim_cessions`) and the loser signs inside its
    band (`aim_terms_signable`); else None. A war must be felt first
    (`THIRD_PARTY_MIN_WAR_TURNS` of the pair). Both directions cannot hold
    at once: a held aim needs the holder's homeland free of the other's
    bloc, and the other's needs the reverse. The seam holds it down."""
    if not a_held_aim_sues():
        return None
    turn = int(getattr(world, "current_turn", 0))
    if turn - int(joined_turn) < THIRD_PARTY_MIN_WAR_TURNS:
        return None
    from backend.game_logic.war_council import aim_cessions, aim_sue_due
    for winner, loser in ((a, b), (b, a)):
        if not aim_sue_due(world, winner, loser):
            continue
        cessions = aim_cessions(world, winner, loser, homeland_only=True)
        if cessions and aim_terms_signable(world, loser, winner):
            return winner, loser, list(cessions)
    return None


def _pair_lock(world, a: str, b: str, sued):
    """T3-5 — (winner, loser, provinces) when the pair's peace must sign a
    held aim over: the broken loser's suit locks the winner's aim; a
    mutual-exhaustion white peace locks whichever court's aim is held
    (both cannot hold at once — a held aim needs its holder's homeland
    free of the other's bloc). None otherwise."""
    if sued:
        loser, winner = sued[0], sued[1]
        regions = held_aim_lock(world, winner, loser)
        return (winner, loser, regions) if regions else None
    for winner, loser in ((a, b), (b, a)):
        regions = held_aim_lock(world, winner, loser)
        if regions:
            return winner, loser, regions
    return None


def _cede_the_held_aim(world, war_id: str, aim) -> List[Dict]:
    """T3-4 — apply the aim's cessions through the negotiated path's own
    applier (`settlement_ratify._apply_settlement_terms`, the exits'
    idiom): a signed TREATY title on each province (the loser reconciled
    while the treaty holds), the annexation's alarm on the winner's slot.
    Returns the APPLIED clauses (what the record and the words read)."""
    from backend.game_logic import settlement_ratify
    winner, loser, cessions = aim
    clauses = [t for t in held_aim_terms(winner, loser, cessions)
               if t.get("type") == "territory_cede"]
    applied = settlement_ratify._apply_settlement_terms(
        world, settlement_terms=clauses, war_id=str(war_id),
        settlement_route_id=f"aim_exit:{war_id}:{int(world.current_turn)}")
    return [dict(c) for c in applied or [] if c.get("type") == "territory_cede"]


def _ceded_regions(clauses: List[Dict]) -> List[str]:
    from backend.game_logic.settlement_validation import _territory_term_regions
    return [str(r) for c in clauses or [] for r in _territory_term_regions(c)]


def _process_exhausted_pair_exits(world, war_id: str, war: Dict,
                                  events: List[Dict]) -> None:
    """The mutual-exhaustion white peace for a non-player sub-pair inside
    a player-containing instance (constants above). At most ONE pair exit
    per turn world-wide (tempo); the player's own pairs are untouchable, and
    a client's pair while it is its LORD's war (`client_pair_is_the_lords_
    war` — it follows the lord out, SR-1b). PC-F29: the weariness of a
    client fighting its lord's war is NOT read by the lord's scorer (Part V
    §43 found the claim unbacked); its war ends with the lord's."""
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
        if player in (a, b):
            continue
        # PC-F29 (S13e part 4): a client's pair is the LORD's war — untouchable
        # here, it follows the lord out (SR-1b) — only while the lord is at war
        # with that court. A client's war with a court its lord is NOT fighting
        # is the client's own, and it takes the same two exits as any court.
        if ((a in vassals and client_pair_is_the_lords_war(world, a, b))
                or (b in vassals and client_pair_is_the_lords_war(world, b, a))):
            continue
        joined = int(pair_meta.get("joined_turn", war.get("created_turn", turn)) or 0)
        # T3-4 (§13.2 R5): a court holding its war's aim against the other
        # offers the aim's terms — the third exit, tried FIRST, inside the
        # one-exit tempo (`held_aim_suit`; the seam holds it down).
        aim = held_aim_suit(world, a, b, joined)
        # WO slice 5: the three inequalities now live in ONE place (above),
        # which the war room's counsel reads too. Same order, same answers.
        sued = None
        if aim is None and not pair_is_mutually_exhausted(world, a, b, joined):
            # PC-F28: a decisive sub-pair — the loser sues past its threshold.
            sued = sub_pair_loser_sues(world, a, b, joined)
            if sued is None:
                continue
        exit_reason = "sub_pair_loser_sues" if sued else "mutual_exhaustion"
        ceded: List[Dict] = []
        lock = None
        if aim is not None:
            exit_reason = AIM_HELD_EXIT
            # Applied BEFORE the state write — the instance road's own order:
            # the signed title stands, SR-1a's retention never overwrites it.
            ceded = _cede_the_held_aim(world, war_id, aim)
        else:
            # T3-5 — the LOCK: whichever road ends the pair (the broken
            # loser's suit, both courts spent), a held aim is signed over.
            lock = _pair_lock(world, a, b, sued)
            if lock is not None:
                ceded = _cede_the_held_aim(world, war_id, lock)

        set_diplomatic_state(world, a, b, "PEACE", exit_reason)
        cleanup_war_end(world, pair_key, conclude_objectives=True)
        # SR-1b: the client's war is the lord's war — a spent lord's exit
        # takes its satellites' pairs with the same court out too, on the
        # same truce floor (a vassal's own pair is never exited on its own
        # account; it follows).
        from backend.game_logic.diplomacy import follow_the_lord
        follow_the_lord(world, a, b, "PEACE", exit_reason,
                        truce_floor=PAIR_EXIT_TRUCE_FLOOR_TURNS)
        # PC15-D4 piece 3 — status-quo-ante-lite: each court returns the
        # OTHER's homeland provinces it holds with no standing army (the
        # measured Moravia shape: a 1-troop detachment, no marshal). The
        # unreturned homeland was the landmine that GUARANTEED re-entry —
        # Austria's P3.7 homeland defense marched straight back through
        # the peace the same turn. Army-occupied ground stays (uti
        # possidetis for ground actually held). Runs through the SAME
        # applier the negotiated third-party path uses, so garrison /
        # cache / threat / event invariants are inherited.
        # T3-4: what this peace ceded by treaty is never handed back.
        ceded_names = _ceded_regions(ceded)
        returned_regions = _return_unheld_homeland(world, war_id, a, b,
                                                   keep=ceded_names)
        # PC-R7 (ii) part 2: the pair's declared articles settle on the held line.
        from backend.game_logic.declared_goals import settle_at_peace
        settle_at_peace(world, [pair_key], ceded)
        if ceded:
            # AI-5b(i), GR5 with the instance road and the player's table: a
            # dictated cession leaves the durable punitive record.
            from backend.game_logic.compensation import compensation_offsets
            from backend.game_logic.emergent_designs import (
                collect_cessions_from_clauses, record_punitive_cessions,
            )
            record_punitive_cessions(
                world, collect_cessions_from_clauses(ceded),
                offsets=compensation_offsets(ceded))
        # PC15-D4 piece 1 — the truce floor (constant above).
        world.armistice_cooldowns[pair_key] = PAIR_EXIT_TRUCE_FLOOR_TURNS
        world._pair_exit_this_turn = int(world.current_turn)

        from backend.display_names import humanize_entity_name
        if aim is not None:
            # T3-4: the court holds the object of its war; the other signs.
            from backend.game_logic.war_council import held_aim_clause
            if ceded_names:
                consequence = (f"{humanize_entity_name(aim[0])} holds "
                               f"{held_aim_clause(ceded_names)}, the object of her war, "
                               f"and {humanize_entity_name(aim[1])} signs "
                               f"{'it' if len(ceded_names) == 1 else 'them'} away; "
                               "their side of the war ends while the greater war goes on.")
            else:
                consequence = (f"{humanize_entity_name(aim[0])} holds the object of her "
                               f"war and {humanize_entity_name(aim[1])} makes peace on the "
                               "held line; their side of the war ends while the greater "
                               "war goes on.")
        elif sued:
            # PC-F28: the loser sues; the winner keeps what it holds.
            loser, winner, sued_score = sued
            consequence = (f"{humanize_entity_name(loser)}, beaten "
                           f"({int(sued_score):+d}), sues for peace and "
                           f"{humanize_entity_name(winner)} takes it on the held line; "
                           "their side of the war ends while the greater war goes on.")
        else:
            consequence = ("Both courts are spent; their side of the war ends "
                           "while the greater war goes on.")
        if lock is not None and ceded_names:
            from backend.game_logic.war_council import held_aim_clause
            consequence += (f" {humanize_entity_name(lock[0])} keeps "
                            f"{held_aim_clause(ceded_names)} by treaty.")
        # T3-6: what the peace handed back, named.
        for words in _evacuation_words(world, _evacuations_for(world, [pair_key])):
            consequence += " " + words
        if returned_regions:
            consequence += (
                " Unheld homeland returns to its crown: "
                + ", ".join(sorted(returned_regions)) + ".")
        proposer, accepter = ((sued[0], sued[1]) if sued else (a, b))
        if aim is not None:
            proposer, accepter = aim[0], aim[1]
        event = {
            "type": "third_party_peace",
            "war_id": war_id,
            "proposer": proposer,
            "accepter": accepter,
            "broker": None,
            "exit": exit_reason,
            "consequence": consequence,
            "message": (f"Peace concluded between {humanize_entity_name(proposer)} "
                        f"and {humanize_entity_name(accepter)} without France. "
                        f"{consequence}"),
        }
        world.log_event(dict(event))
        events.append(event)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "third_party_peace", {
            "proposer": humanize_entity_name(proposer),
            "accepter": humanize_entity_name(accepter),
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
    # OCT27-D12(b): a war of France's client never settles without France,
    # so a side past its own line asks France too (the band's floor lifts).
    client_war = client_war_waits_for_france(
        world, war, getattr(world, "player_nation", "France"))
    for proposer, other in ((attackers_leader, defenders_leader),
                            (defenders_leader, attackers_leader)):
        score = int(get_war_score_for(world, proposer, other))
        from backend.game_logic.bond import break_ranks_depth
        threshold = effective_peace_threshold(proposer, other, world) - int(
            break_ranks_depth(world, proposer, other)["score"])  # PC-X55
        if threshold + BROKER_ASK_MARGIN > score and (client_war or score >= threshold):
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
