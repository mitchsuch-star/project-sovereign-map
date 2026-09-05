"""Settlement ratification and term application (CH-1 split, layer 4).

Per-pair ratification plan, _apply_settlement_terms, pair state transitions,
common-peace treaty recording, pre-cleanup snapshots, blocked-ratify
reattach, ratify_settlement_confirm, and replacement-terms staging.
Split from settlement_preview.py (CH-1); may import settlement_routes /
settlement_validation / settlement_baseline / settlement_staging.
"""

from __future__ import annotations

from backend.display_names import acceptance_band_display
from backend.game_logic import settlement_scoring
from backend.game_logic.diplomatic_templates import (
    calculate_raw_treaty_harshness,
    calculate_treaty_harshness,
    resolve_settlement_voice_line,
)
from backend.game_logic.settlement_scoring import (
    CANONICAL_CLAUSE_TYPES,
    SETTLEMENT_HARD_STOP_CODES,
    TOTAL_ANNEXATION_WAR_SCORE,
)
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
)
from backend.game_logic.settlement_baseline import compute_per_court_acceptance
from backend.game_logic.settlement_routes import (
    _error_display,
    _reopen_target,
    _safe_reopen_response,
    derive_settlement_review_target,
    mint_settlement_route_id,
)
from backend.game_logic.settlement_staging import (
    _discard_scoped_settlement_draft_for_dialogue,
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    revalidate_staged_settlement,
    save_scoped_settlement_draft,
)
from backend.game_logic.settlement_validation import (
    RATIFY_LEGACY_APPLY_CLAUSE_TYPES,
    _normalize_staged_terms_for_validation,
    _pair_nations,
    _side_leader,
    _term_lists_equal,
    _territory_term_regions,
    validate_settlement_terms,
)


def consenting_courts_for_ratification(dialogue: Mapping[str, Any]) -> List[str]:
    """The courts whose consent still binds this staged package (FA-3).

    A settlement offer's covered courts wrote the terms they offered, so the
    accept-staged review does not score their willingness — see
    `settlement_offers.handle_incoming_settlement_offer_action`. That fact has
    to survive to ratification: a consent honoured only at STAGING is killed
    by the fresh re-score here, and the player is left with a Ratify button
    that was true when it was drawn and false when it is pressed.

    Consent is granted to a SPECIFIC package. If the staged terms are no
    longer the offered ones — an edit or a restage — the consent lapses and
    every court is scored normally again.

    Review round: the first cut of this docstring listed a third case, "a
    save-loaded dialogue that outlived its offer". That is wrong and was
    never implemented. `DialogueManager.to_dict`/`from_dict` deep-copy the
    whole dialogue, so `consent_terms` and `settlement_terms` travel
    together and a round trip satisfies the equality trivially. The staged
    review IS the consent record from the tick it is staged; outliving the
    offer is its normal condition, not an anomaly. `consent_offer_id` rides
    the dialogue as PROVENANCE only — nothing reads it, deliberately:
    lapsing on "the offer is no longer live" would kill the consent on the
    very tick the accept consumes the letter, re-opening the P1 this slice
    closed.
    """
    consenting = [
        str(n) for n in (dialogue.get("consenting_courts") or []) if n
    ]
    if not consenting:
        return []
    if not _term_lists_equal(
        dialogue.get("consent_terms") or [],
        dialogue.get("settlement_terms") or [],
    ):
        return []
    return consenting


def _failed_ratification_reaction_summary(
    world: Any,
    *,
    war_id: str,
    proposer_side: str = "",
    accepting_side: str = "",
    covered_enemy_participants: Optional[Iterable[str]] = None,
    settlement_terms: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    from backend.game_logic.settlement_reactions import route_settlement_reactions

    return route_settlement_reactions(
        world,
        war_id=war_id,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        covered_enemy_participants=list(covered_enemy_participants or []),
        settlement_terms=[dict(t) for t in (settlement_terms or []) if isinstance(t, Mapping)],
        resolved_pairs=[],
        applied_clauses=[],
        pre_cleanup_snapshots=[],
        war_ended=False,
        success=False,
        mutated=False,
    )


def _build_pair_ratification_plan(
    world: Any,
    war_instance: Mapping[str, Any],
    *,
    proposer_side: str,
    covered: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """Per-pair plan for which active cross-side pairs settle to which state.

    Each plan entry names the pair, the proposer-side member, the covered
    enemy, the pair's current state (so callers can branch ARMISTICE vs WAR
    cleanup), and the post-ratification target state. ``ALLIANCE`` is set
    only when a ``forced_alliance`` term exists with ``from`` matching the
    covered enemy and ``to`` matching the proposer-side member of the pair
    (spec §10.5 line 1038). Every other covered hostile pair settles to
    ``PEACE``.
    """
    proposer_members: Set[str] = set(war_instance.get(proposer_side) or [])
    covered_set: Set[str] = {str(n) for n in covered}
    forced_alliance_targets: Dict[str, Set[str]] = {}
    vassalage_terms_by_pair: Dict[frozenset[str], Mapping[str, Any]] = {}
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        if term.get("type") == "forced_alliance":
            fa_target = str(term.get("from") or "")
            fa_imposer = str(term.get("to") or "")
            if fa_target and fa_imposer:
                forced_alliance_targets.setdefault(fa_target, set()).add(fa_imposer)
        elif term.get("type") in ("vassalage", "subjugation"):
            vassal_target = str(term.get("from") or term.get("vassal_nation") or "")
            vassal_lord = str(term.get("to") or term.get("lord_nation") or "")
            if vassal_target and vassal_lord:
                vassalage_terms_by_pair[frozenset((vassal_lord, vassal_target))] = term

    meta = war_instance.get("diplo_key_meta") or {}
    plan: List[Dict[str, Any]] = []
    for pair in list(war_instance.get("active_diplo_keys") or []):
        nations = _pair_nations(pair)
        if len(nations) != 2:
            continue
        a, b = nations
        if a in proposer_members and b in covered_set:
            proposer_member, covered_enemy = a, b
        elif b in proposer_members and a in covered_set:
            proposer_member, covered_enemy = b, a
        else:
            continue
        pair_meta = meta.get(pair) or {}
        if pair_meta.get("pair_status") not in ("war", "armistice"):
            continue
        target_state = "PEACE"
        if proposer_member in forced_alliance_targets.get(covered_enemy, set()):
            target_state = "ALLIANCE"
        vassalage_term = vassalage_terms_by_pair.get(
            frozenset((proposer_member, covered_enemy))
        )
        if vassalage_term is not None:
            target_state = "VASSAL"
            vassal_lord = str(
                vassalage_term.get("to") or vassalage_term.get("lord_nation") or ""
            )
            vassal_target = str(
                vassalage_term.get("from") or vassalage_term.get("vassal_nation") or ""
            )
        else:
            vassal_lord = ""
            vassal_target = ""
        current_state = world.diplomatic_states.get(pair, "PEACE")
        plan.append({
            "pair": pair,
            "proposer_member": proposer_member,
            "covered_enemy": covered_enemy,
            "current_state": current_state,
            "pair_status_before": pair_meta.get("pair_status"),
            "target_state": target_state,
            "vassal_lord": vassal_lord,
            "vassal_target": vassal_target,
        })
    return plan


def _capture_pair_pre_cleanup_war_data(
    world: Any,
    proposer_member: str,
    covered_enemy: str,
) -> Dict[str, Any]:
    """Snapshot war data from the resolving pair's proposer-side perspective."""
    diplo_key = world._make_diplo_key(proposer_member, covered_enemy)
    war_start = getattr(world, "war_start_turns", {}).get(
        diplo_key, getattr(world, "current_turn", 0),
    )
    war_duration = int(max(0, int(getattr(world, "current_turn", 0) or 0) - int(war_start)))

    raw_score = int(getattr(world, "war_scores", {}).get(diplo_key, 0))
    parts = diplo_key.split("|")
    proposer_war_score = raw_score
    if len(parts) == 2 and parts[0] != proposer_member:
        proposer_war_score = -raw_score

    records = list(getattr(world, "battle_records", {}).get(diplo_key, []) or [])
    proposer_casualties = 0
    covered_enemy_casualties = 0
    for record in records:
        attacker = record.get("attacker")
        defender = record.get("defender")
        attacker_casualties = int(record.get("attacker_casualties", 0) or 0)
        defender_casualties = int(record.get("defender_casualties", 0) or 0)
        if attacker == proposer_member:
            proposer_casualties += attacker_casualties
        elif defender == proposer_member:
            proposer_casualties += defender_casualties
        if attacker == covered_enemy:
            covered_enemy_casualties += attacker_casualties
        elif defender == covered_enemy:
            covered_enemy_casualties += defender_casualties

    player = getattr(world, "player_nation", "France")
    result = {
        "war_duration": war_duration,
        "war_score": int(proposer_war_score),
        "proposer_member": proposer_member,
        "covered_enemy": covered_enemy,
        "proposer_casualties": int(proposer_casualties),
        "covered_enemy_casualties": int(covered_enemy_casualties),
    }
    if proposer_member == player:
        result["french_casualties"] = int(proposer_casualties)
        result["enemy_casualties"] = int(covered_enemy_casualties)
    elif covered_enemy == player:
        result["french_casualties"] = int(covered_enemy_casualties)
        result["enemy_casualties"] = int(proposer_casualties)
    else:
        result["french_casualties"] = 0
        result["enemy_casualties"] = int(covered_enemy_casualties)
    return result


def _apply_settlement_terms(
    world: Any,
    *,
    settlement_terms: Iterable[Mapping[str, Any]],
    war_id: str = "",
    settlement_route_id: str = "",
) -> List[Dict[str, Any]]:
    """Apply package-level territory, gold, and liberation outcomes.

    Forced-alliance state transitions are handled per pair after pair
    cleanup (see ``_resolve_pair_state_transitions``) because the alliance
    state must replace the intermediate ``PEACE`` state established by
    cleanup.

    `war_id` / `settlement_route_id` are forwarded as identity columns on
    ratified recurring-gold obligations so the per-turn processor and the
    diplomatic ledger can attribute each tick to the originating war.
    """
    applied: List[Dict[str, Any]] = []
    for idx, term in enumerate(settlement_terms or []):
        if not isinstance(term, Mapping):
            continue
        ttype = term.get("type")
        from_nation = str(term.get("from") or "")
        to_nation = str(term.get("to") or "")
        if ttype == "territory_cede":
            regions = _territory_term_regions(term)
            cede_from_regions = set()
            if from_nation:
                cede_from_regions = set(getattr(world, "get_nation_regions")(from_nation))
            if from_nation and regions and cede_from_regions:
                if len(cede_from_regions - set(regions)) == 0:
                    ws_key = world._make_diplo_key(from_nation, to_nation)
                    ws = abs(int(getattr(world, "war_scores", {}).get(ws_key, 0) or 0))
                    if ws < TOTAL_ANNEXATION_WAR_SCORE:
                        continue
            transferred: List[str] = []
            for region_name in regions:
                if region_name not in getattr(world, "regions", {}):
                    continue
                region = world.regions[region_name]
                if from_nation and getattr(region, "controller", None) != from_nation:
                    continue
                region.controller = to_nation
                region.stability = 50
                transferred.append(region_name)
                if from_nation and to_nation:
                    # World-scoped starting map (1805 pre-slice item 7 family —
                    # Europe cessions must fire `allied_region_restored` too).
                    from backend.models.region import get_starting_controllers
                    starting_controllers = (
                        getattr(world, "_starting_controllers", None)
                        or get_starting_controllers()
                    )
                    if starting_controllers.get(region_name) == to_nation:
                        from backend.game_logic.war_contribution import (
                            _resolve_war_id_for_pair_on_opposite_sides,
                            accrue_occupation_event,
                        )
                        cede_war_id = _resolve_war_id_for_pair_on_opposite_sides(
                            world, to_nation, from_nation,
                        )
                        if cede_war_id:
                            event_id = (
                                f"occupation-{int(getattr(world, 'current_turn', 0) or 0)}-"
                                f"{cede_war_id}-{to_nation}-"
                                f"allied_region_restored-{region_name}"
                            )
                            accrue_occupation_event(
                                world,
                                actor_nation=to_nation,
                                region=region_name,
                                occupation_kind="allied_region_restored",
                                from_controller=from_nation,
                                to_controller=to_nation,
                                war_id=cede_war_id,
                                turn=int(getattr(world, "current_turn", 0) or 0),
                                event_id=event_id,
                            )
            if transferred:
                clause = dict(term)
                if "regions" in clause:
                    clause["regions"] = transferred
                elif transferred:
                    clause["region"] = transferred[0]
                applied.append(clause)
                if hasattr(world, "invalidate_active_nations_cache"):
                    world.invalidate_active_nations_cache()
                # AI-4a step 5: the annexing/returning ACTOR's own slot.
                if to_nation:
                    from backend.game_logic.coalition import add_threat
                    add_threat(world, 8 * len(transferred), "treaty_annex",
                               target=to_nation)
                if from_nation:
                    from backend.game_logic.coalition import reduce_threat
                    reduce_threat(world, 5 * len(transferred), "territory_return",
                                  target=from_nation)
                for nation in {from_nation}:
                    if (
                        nation
                        and nation != getattr(world, "player_nation", None)
                        and hasattr(world, "get_nation_regions")
                        and not world.get_nation_regions(nation)
                    ):
                        world._eliminate_nation(nation)
        elif ttype in ("gold_lump", "gold_indemnity"):
            amount = abs(int(term.get("amount", 0) or 0))
            nation_gold = getattr(world, "nation_gold", {}) or {}
            if from_nation in nation_gold:
                available = int(nation_gold.get(from_nation, 0))
                transfer = min(amount, max(0, available))
                nation_gold[from_nation] = available - transfer
                if to_nation in nation_gold:
                    nation_gold[to_nation] = int(nation_gold.get(to_nation, 0)) + transfer
                if transfer > 0:
                    clause = dict(term)
                    clause["type"] = ttype
                    clause["amount"] = int(transfer)
                    applied.append(clause)
        elif ttype == "gold_per_turn":
            amount = abs(int(term.get("amount", 0) or 0))
            turns = abs(int(term.get("turns", 0) or 0))
            if from_nation and to_nation and amount > 0 and turns > 0:
                # SC-33 / G2-Slice-9: register a recurring obligation on
                # `world.recurring_settlement_payments`. The income-phase
                # processor in `world_state.advance_turn` debits the
                # payer once per turn until `turns_remaining` hits zero
                # or a cancellation condition fires (payer/recipient
                # eliminated, payer vassalized, renewed war between the
                # pair). Ratification itself does not move gold — the
                # first transfer happens on the next turn's income
                # phase, mirroring bilateral treaty per-turn clauses.
                payments = getattr(world, "recurring_settlement_payments", None)
                if payments is None:
                    payments = []
                    setattr(world, "recurring_settlement_payments", payments)
                ratified_turn = int(getattr(world, "current_turn", 0) or 0)
                seq = sum(
                    1
                    for entry in payments
                    if isinstance(entry, Mapping)
                    and int(entry.get("ratified_turn", -1) or -1) == ratified_turn
                )
                payment_id = (
                    f"recurring_gold:{from_nation}:{to_nation}:"
                    f"{ratified_turn}:{seq}"
                )
                # G4F smoke follow-up: stamp the display label NOW, while
                # the war instance is still alive — by the time the income
                # phase pays, the ratified war is archived and the
                # processor's live lookup would fall back to the raw
                # war_id ("the settlement of war_1" reached the player's
                # morning dispatch).
                label_instance = (
                    getattr(world, "war_instances", {}) or {}
                ).get(str(war_id or "")) or {}
                label_attackers = list(label_instance.get("attackers") or [])
                label_defenders = list(label_instance.get("defenders") or [])
                war_label_for_record = (
                    f"{label_attackers[0]} vs {' + '.join(label_defenders)}"
                    if label_attackers and label_defenders
                    else str(war_id or "the settlement")
                )
                payments.append({
                    "payment_id": payment_id,
                    "from": from_nation,
                    "to": to_nation,
                    "amount_per_turn": int(amount),
                    "turns_remaining": int(turns),
                    "total_turns": int(turns),
                    "war_id": str(war_id or ""),
                    "war_label": war_label_for_record,
                    "ratified_turn": int(ratified_turn),
                    "settlement_route_id": str(settlement_route_id or ""),
                    "source_clause_index": int(idx),
                })
                clause = dict(term)
                clause["amount"] = amount
                clause["turns"] = turns
                clause["payment_id"] = payment_id
                clause["ratified_turn"] = int(ratified_turn)
                applied.append(clause)
        elif ttype == "vassal_transfer":
            # VS-5 (VASSAL_DEEPENING_SPEC §6): re-home an existing vassal.
            # Package-level handler (like liberation) — the transferred
            # vassal is typically NOT a war-participant pair member, so the
            # per-pair ratification plan structurally cannot host it.
            tr_vassal = str(term.get("vassal") or "")
            tr_from = str(term.get("from") or "")
            tr_to = str(term.get("to") or "")
            vassals_map = getattr(world, "vassals", {}) or {}
            record = vassals_map.get(tr_vassal)
            if (tr_vassal and tr_to and record is not None
                    and str(record.get("lord") or "") == tr_from):
                # Close any live war between the RECEIVING lord and the
                # vassal first (they sat on opposite sides) — mirror the
                # vassalage arm's cleanup path so war data resolves cleanly.
                pre_state = world.get_diplomatic_state(tr_to, tr_vassal)
                if pre_state in ("WAR", "ARMISTICE"):
                    from backend.game_logic.diplomacy import (
                        cleanup_war_end as _cwe,
                        set_diplomatic_state as _sds_tr,
                    )
                    _sds_tr(
                        world, tr_to, tr_vassal,
                        "PEACE", "settlement_vassal_transfer",
                    )
                    _cwe(
                        world,
                        world._make_diplo_key(tr_to, tr_vassal),
                        conclude_objectives=True,
                    )
                from backend.game_logic.vassal import transfer_vassal
                transfer_result = transfer_vassal(
                    world, tr_vassal, tr_to,
                    reason="settlement_vassal_transfer",
                )
                if transfer_result.get("success"):
                    clause = dict(term)
                    clause["pair_state_transition"] = (
                        f"VASSAL of {tr_from} -> VASSAL of {tr_to}"
                    )
                    clause["loyalty_after"] = int(
                        transfer_result.get("loyalty_after") or 0
                    )
                    clause["rekeyed_marshal_count"] = len(
                        transfer_result.get("rekeyed_marshals") or []
                    )
                    applied.append(clause)
        elif ttype == "create_client":
            # NA-6c (NATION_AGENDAS_SPEC §11.4): erect a new client state
            # out of the defeated court's soil. Package-level handler like
            # vassal_transfer — the erected tag is not a war participant,
            # so the per-pair plan cannot host it.
            #
            # IGR-D: the body moved to `formations.apply_create_client_clause`
            # so the bilateral pair-substitute peace carves through the same
            # code. Behaviour here is unchanged.
            from backend.game_logic.formations import (
                apply_create_client_clause,
            )
            cc_clause = apply_create_client_clause(world, term)
            if cc_clause is not None:
                applied.append(cc_clause)
        elif ttype == "liberation":
            lib_vassal = str(term.get("vassal_nation") or term.get("from") or "")
            lib_from = str(term.get("lord_nation") or term.get("to") or "")
            lib_liberator = str(term.get("liberator") or "")
            vassals = getattr(world, "vassals", {}) or {}
            # VS-5 post-build review C5: the apply guard also requires the
            # LIVE lord to match the clause's lord_nation — a stale clause
            # (or one applied after a same-package transfer re-homed the
            # vassal) must not release someone ELSE's vassal.
            if (lib_vassal and lib_vassal in vassals and lib_from
                    and str(vassals[lib_vassal].get("lord") or "") != lib_from):
                continue
            if lib_vassal and lib_vassal in vassals:
                pre_release_vassal_regions = list(world.get_nation_regions(lib_vassal))
                from backend.game_logic.vassal import release_vassal
                release_result = release_vassal(
                    world, lib_vassal, reduce_threat_on_release=False,
                )
                if release_result.get("success"):
                    if lib_liberator:
                        from backend.game_logic.diplomacy import (
                            set_diplomatic_state as _sds,
                        )
                        _sds(
                            world, lib_liberator, lib_vassal,
                            "DEFENSIVE_ALLIANCE", "common_peace_liberation",
                        )
                        if hasattr(world, "modify_nation_relation"):
                            world.modify_nation_relation(lib_vassal, lib_from, -20)
                            world.modify_nation_relation(lib_vassal, lib_liberator, 30)
                    if lib_from:
                        from backend.game_logic.coalition import reduce_threat
                        reduce_threat(world, 8, "liberation", target=lib_from)
                    if (
                        lib_liberator
                        and lib_from
                        and lib_liberator != lib_from
                        and pre_release_vassal_regions
                    ):
                        from backend.game_logic.war_contribution import (
                            _resolve_war_id_for_pair_on_opposite_sides,
                            accrue_occupation_event,
                        )
                        lib_war_id = _resolve_war_id_for_pair_on_opposite_sides(
                            world, lib_liberator, lib_from,
                        )
                        if lib_war_id:
                            for lib_region in pre_release_vassal_regions:
                                event_id = (
                                    f"occupation-{int(getattr(world, 'current_turn', 0) or 0)}-"
                                    f"{lib_war_id}-{lib_liberator}-"
                                    f"liberated_region_restored-{lib_region}"
                                )
                                accrue_occupation_event(
                                    world,
                                    actor_nation=lib_liberator,
                                    region=lib_region,
                                    occupation_kind="liberated_region_restored",
                                    from_controller=lib_from,
                                    to_controller=lib_vassal,
                                    war_id=lib_war_id,
                                    turn=int(getattr(world, "current_turn", 0) or 0),
                                    event_id=event_id,
                                )
                    clause = dict(term)
                    clause["vassal_nation"] = lib_vassal
                    clause["lord_nation"] = lib_from
                    clause["liberator"] = lib_liberator
                    clause["pair_state_transition"] = "VASSALAGE -> SOVEREIGN"
                    # SC-31 / G2-Slice-8 applied_clauses_preview fields
                    # for liberation: defensive_alliance_with_liberator,
                    # relation_deltas (lib_vassal vs former lord -20 /
                    # vs liberator +30), threat_reduction (lord-on-player
                    # side delta).
                    clause["defensive_alliance_with_liberator"] = bool(lib_liberator)
                    clause["relation_deltas"] = {
                        f"{lib_vassal}|{lib_from}": -20,
                        f"{lib_vassal}|{lib_liberator}": 30,
                    }
                    clause["threat_reduction"] = (
                        8 if lib_from == getattr(world, "player_nation", None) else 0
                    )
                    applied.append(clause)
                    if hasattr(world, "log_event"):
                        world.log_event({
                            "type": "vassal_liberated",
                            "vassal_nation": lib_vassal,
                            "former_lord": lib_from,
                            "liberator": lib_liberator,
                            "liberator_nation": lib_liberator,
                            "turn": int(getattr(world, "current_turn", 0) or 0),
                        })
    return applied


def _resolve_pair_state_transitions(
    world: Any,
    plan: List[Dict[str, Any]],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Run per-pair state transitions + cleanup for the ratification plan.

    For each plan entry: set ``PEACE`` (so cleanup_war_end resolves the
    pair, closes contribution episodes, clears war scores / start turns /
    decisive battles / cascade tracking / stalemate counters / armistice
    cooldowns), then for ``ALLIANCE`` targets re-set the state to
    ``ALLIANCE`` and apply forced-alliance side effects (alliance origin,
    Continental System membership, +15 threat when France imposes,
    relation reset, ``forced_alliance_imposed`` log event).

    Returns ``(resolved_pairs, forced_alliance_clauses_applied)`` so the
    caller can build a structured ratification summary.
    """
    from backend.game_logic.diplomacy import (
        cleanup_war_end,
        set_diplomatic_state,
    )

    forced_alliance_terms_by_pair: Dict[Tuple[str, str], Mapping[str, Any]] = {}
    vassalage_terms_by_pair: Dict[Tuple[str, str], Mapping[str, Any]] = {}
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        if term.get("type") != "forced_alliance":
            if term.get("type") in ("vassalage", "subjugation"):
                vassal_target = str(term.get("from") or term.get("vassal_nation") or "")
                vassal_lord = str(term.get("to") or term.get("lord_nation") or "")
                if vassal_target and vassal_lord:
                    vassalage_terms_by_pair[(vassal_lord, vassal_target)] = term
            continue
        fa_target = str(term.get("from") or "")
        fa_imposer = str(term.get("to") or "")
        if fa_target and fa_imposer:
            forced_alliance_terms_by_pair[(fa_imposer, fa_target)] = term

    resolved_pairs: List[Dict[str, Any]] = []
    state_clauses_applied: List[Dict[str, Any]] = []

    for entry in plan:
        proposer_member = entry["proposer_member"]
        covered_enemy = entry["covered_enemy"]
        target_state = entry["target_state"]
        pair_key = world._make_diplo_key(proposer_member, covered_enemy)

        # Always transition out of WAR/ARMISTICE through PEACE so
        # cleanup_war_end runs the same closure path as bilateral peace
        # (resolve_pair_to_resolved + episode close + war-data clear).
        current_state = world.get_diplomatic_state(proposer_member, covered_enemy)
        if target_state == "VASSAL":
            vassal_lord = str(entry.get("vassal_lord") or "")
            vassal_target = str(entry.get("vassal_target") or "")
            term = vassalage_terms_by_pair.get((vassal_lord, vassal_target))
            vassal_result = {"success": False}
            if current_state == "ARMISTICE" and term is not None:
                set_diplomatic_state(
                    world, proposer_member, covered_enemy,
                    "WAR", "common_peace_vassalage_ratification",
                )
                current_state = "WAR"
            if current_state == "WAR" and term is not None:
                from backend.game_logic.vassal import (
                    assimilate_vassal_marshals,
                    create_vassal_conquest,
                    create_vassal_treaty,
                )
                if term.get("type") == "subjugation":
                    vassal_result = create_vassal_conquest(
                        world, vassal_lord, vassal_target,
                        garrison_size=int(term.get("garrison_size", 0) or 0),
                    )
                else:
                    vassal_result = create_vassal_treaty(
                        world, vassal_lord, vassal_target,
                        generosity_bonus=int(term.get("generosity_bonus", 0) or 0),
                        terms=list(settlement_terms or []),
                    )
                if vassal_result.get("success"):
                    assimilated_marshals = assimilate_vassal_marshals(
                        world, vassal_target
                    )
                    clause = dict(term)
                    clause.setdefault("from", vassal_target)
                    clause.setdefault("to", vassal_lord)
                    clause["pair_state_transition"] = "WAR -> VASSALAGE"
                    # SC-31 / G2-Slice-8 applied_clauses_preview fields
                    # for vassalage / subjugation. Values read from the
                    # live vassal record so the preview matches the
                    # mutation that ran. autonomy_after / loyalty_after /
                    # tribute_rate_after / vassal_path use the values
                    # stamped by create_vassal_conquest /
                    # create_vassal_treaty; threat_delta_for_lord is the
                    # coalition-threat delta from the same helper (+25
                    # for conquest, +5 for treaty per WPS-B §2a);
                    # marshal_assimilation_count counts marshals moved
                    # to the lord pool.
                    vassal_record = (
                        (getattr(world, "vassals", {}) or {}).get(vassal_target)
                        or {}
                    )
                    autonomy_level = int(vassal_record.get("autonomy", 1))
                    autonomy_after_display = {
                        0: "Puppet",
                        1: "Satellite",
                        2: "Autonomous",
                    }.get(autonomy_level, "Satellite")
                    clause["autonomy_after"] = autonomy_after_display
                    clause["loyalty_after"] = int(vassal_record.get("loyalty") or 0)
                    clause["tribute_rate_after"] = float(
                        vassal_record.get("tribute_rate") or 0.0
                    )
                    clause["vassal_path"] = str(vassal_record.get("path") or "")
                    clause["marshal_assimilation_count"] = len(assimilated_marshals)
                    # Post-build review C9: coalition threat is player-scoped
                    # since Vassal Depth Slice 0 (create_vassal_* only add
                    # threat when the lord IS the player) — the preview must
                    # not claim +5/+25 for an AI-ally lord that paid none.
                    if vassal_lord == getattr(world, "player_nation", None):
                        clause["threat_delta_for_lord"] = (
                            25 if term.get("type") == "subjugation" else 5
                        )
                    else:
                        clause["threat_delta_for_lord"] = 0
                    state_clauses_applied.append(clause)
                    cleanup_war_end(world, pair_key, conclude_objectives=True)
                else:
                    set_diplomatic_state(
                        world, proposer_member, covered_enemy,
                        "PEACE", "common_peace_settlement",
                    )
                    cleanup_war_end(world, pair_key, conclude_objectives=True)
            else:
                set_diplomatic_state(
                    world, proposer_member, covered_enemy,
                    "PEACE", "common_peace_settlement",
                )
                cleanup_war_end(world, pair_key, conclude_objectives=True)
        elif current_state in ("WAR", "ARMISTICE"):
            set_diplomatic_state(
                world, proposer_member, covered_enemy,
                "PEACE", "common_peace_settlement",
            )
            cleanup_war_end(world, pair_key, conclude_objectives=True)
        else:
            cleanup_war_end(world, pair_key, conclude_objectives=True)

        if target_state == "ALLIANCE":
            set_diplomatic_state(
                world, proposer_member, covered_enemy,
                "ALLIANCE", "common_peace_forced_alliance",
            )
            world.nation_relations[pair_key] = 0
            alliance_origins = getattr(world, "alliance_origins", {}) or {}
            alliance_origins[pair_key] = "forced"
            world.alliance_origins = alliance_origins
            term = forced_alliance_terms_by_pair.get(
                (proposer_member, covered_enemy),
            )
            includes_cs = bool(term.get("includes_continental_system", True)) if term else True
            if includes_cs:
                cs_members = getattr(world, "continental_system_members", []) or []
                if isinstance(cs_members, set):
                    cs_members.add(covered_enemy)
                elif covered_enemy not in cs_members:
                    cs_members.append(covered_enemy)
                world.continental_system_members = cs_members
            # G2-Slice-1b-Repair-1: Continental System surcharge.
            # Base +15 threat for the alliance imposition; +10 extra
            # when CS=True so the imperial cost of forcing inclusion is
            # charged at ratification, matching what the preview shows.
            from backend.game_logic.settlement_scoring import (
                FORCED_ALLIANCE_THREAT_PER_CLAUSE,
                FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE,
            )
            clause_threat_delta = int(FORCED_ALLIANCE_THREAT_PER_CLAUSE)
            if includes_cs:
                clause_threat_delta += int(
                    FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE
                )
            if proposer_member:
                from backend.game_logic.coalition import add_threat
                add_threat(world, clause_threat_delta, "forced_alliance",
                           target=proposer_member)
            if hasattr(world, "log_event"):
                world.log_event({
                    "type": "forced_alliance_imposed",
                    "imposer": proposer_member,
                    "target": covered_enemy,
                    "imposing_nation": proposer_member,
                    "forced_nation": covered_enemy,
                    "includes_continental_system": includes_cs,
                    "projected_threat_delta": clause_threat_delta,
                    "turn": int(getattr(world, "current_turn", 0) or 0),
                })
            if term is not None:
                clause = dict(term)
                clause["includes_continental_system"] = includes_cs
                # Always overwrite so preview and applied row agree on
                # the CS-adjusted delta even when the editor pre-stamped
                # the legacy +15 baseline before authoring the toggle.
                clause["projected_threat_delta"] = clause_threat_delta
                clause["pair_state_transition"] = "WAR -> ALLIANCE"
                state_clauses_applied.append(clause)

        resolved_pairs.append({
            "pair": entry["pair"],
            "proposer_member": proposer_member,
            "covered_enemy": covered_enemy,
            "current_state_before": entry["current_state"],
            "pair_status_before": entry["pair_status_before"],
            "final_state": world.get_diplomatic_state(proposer_member, covered_enemy),
            "target_state": target_state,
        })

    return resolved_pairs, state_clauses_applied


def _record_common_peace_treaties(
    world: Any,
    *,
    plan: List[Dict[str, Any]],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> None:
    """Write per-pair treaty records in the same shape bilateral ratification uses."""
    active_treaties = getattr(world, "active_treaties", {}) or {}
    previous_treaties = getattr(world, "previous_treaties", {}) or {}
    all_terms = [dict(t) for t in (settlement_terms or []) if isinstance(t, Mapping)]
    for entry in plan:
        proposer_member = entry["proposer_member"]
        covered_enemy = entry["covered_enemy"]
        pair_key = world._make_diplo_key(proposer_member, covered_enemy)
        final_state = world.get_diplomatic_state(proposer_member, covered_enemy)
        pair_terms = []
        for term in all_terms:
            term_type = term.get("type")
            term_from = str(term.get("from") or term.get("vassal_nation") or "")
            term_to = str(term.get("to") or term.get("lord_nation") or term.get("liberator") or "")
            if term_type in ("forced_alliance", "vassalage", "subjugation"):
                if term_from == covered_enemy and term_to == proposer_member:
                    pair_terms.append(term)
            elif term_from == covered_enemy:
                pair_terms.append(term)
            # Aug 30, 2026 review: the arm this replaces was
            # `term_to == proposer_member and term_from` — ANY clause pointing
            # at the leader, from ANY court. In a settlement where France
            # covers both Austria and Prussia, Prussia's indemnity to France
            # was therefore written into the France–Austria treaty record too,
            # so the ledger showed Austria paying a bill Prussia owed. Any
            # clause from `covered_enemy` is already caught one arm above, and
            # a clause from a third court belongs to that court's own pair.
            #
            # What genuinely had no arm is the other direction: a clause the
            # LEADER gives to this enemy — the sweetener that buys the
            # signature — matched neither test and was dropped from the record
            # entirely, so a peace bought with a province recorded only the
            # taking.
            elif term_from == proposer_member and term_to == covered_enemy:
                pair_terms.append(term)
        treaty_type = {
            "ALLIANCE": "alliance",
            "VASSAL": "vassalage",
            "DEFENSIVE_ALLIANCE": "defensive_alliance",
        }.get(final_state, "peace")
        # SC-24: store BOTH raw common-peace harshness and the legacy
        # 1.0-clamped harshness under separate explicit fields. Named
        # consumers that interpret authored common-peace terms read
        # `raw_harshness` (no 1.0 ceiling); legacy bilateral consumers
        # may keep reading `harshness` for backward compatibility.
        clamped_harshness = calculate_treaty_harshness({"clauses": pair_terms})
        raw_harshness = calculate_raw_treaty_harshness({"clauses": pair_terms})
        treaty = {
            "nations": [proposer_member, covered_enemy],
            "type": treaty_type,
            "state_transition": f"{entry['current_state']}_TO_{final_state}",
            "clauses": [dict(t) for t in pair_terms],
            "turn_signed": int(getattr(world, "current_turn", 0) or 0),
            "harshness": clamped_harshness,
            # SC-24 raw common-peace harshness consumers: ledger / AI
            # proposal / coalition threat / dispatch / notifications.
            "raw_harshness": float(raw_harshness or 0.0),
            "clamped_harshness": float(clamped_harshness or 0.0),
            "source": "common_peace",
        }
        active_treaties[pair_key] = treaty
        previous_treaties.setdefault(pair_key, []).append(dict(treaty))
    world.active_treaties = active_treaties
    world.previous_treaties = previous_treaties


def _capture_pre_cleanup_snapshots(
    world: Any,
    plan: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Snapshot per-pair war data before cleanup_war_end clears it.

    Spec §11 ratification ordering line 1239 requires snapshotting every
    covered pair's war-instance data before any cleanup runs. The C2
    summary shape exposes per-pair war_score / war_duration /
    casualties so D1 reactions can read frozen pre-settlement context.
    """
    snapshots: Dict[str, Dict[str, Any]] = {}
    for entry in plan:
        snapshots[entry["pair"]] = _capture_pair_pre_cleanup_war_data(
            world, entry["proposer_member"], entry["covered_enemy"],
        )
    return snapshots


def _blocked_ratify_reattach(
    dialogue: Mapping[str, Any],
    *,
    war_id: str,
    error: str,
    talleyrand_text: str,
    validation_error: Optional[str] = None,
    validation_detail: Optional[str] = None,
    validation_error_index: Optional[int] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """PF-1 / D2 — the blocked-ratify response contract.

    A blocked ratification leaves the staged ``settlement_confirm`` REVIEW
    MOUNTED (the dialogue manager is not popped) and re-attaches it on the
    response together with a rendered ``error_display``, mirroring the Tier-2
    safety net: the Godot popup hides itself on every affordance click and
    only re-mounts from a returned ``diplomatic_dialogue``, so a bare
    success=False would orphan the surface and read as a silent dead end
    (the June 9 pre-flight D2 "Response processed" loop). The player keeps
    the full REVIEW rail (Return to terms / Adjust terms / Back Out) to
    repair or abandon the draft.

    Live-world contradictions (archived war, leader change) do NOT route
    here — `revalidate_staged_settlement` failures keep the SC-2/SC-14b
    pop + `must_reopen` recovery contract because their staged surface is
    stale by definition.
    """
    error_display = _error_display(error)
    payload: Dict[str, Any] = {
        "success": False,
        "dialogue_type": "settlement_confirm",
        "action": "confirm",
        "war_id": war_id,
        "error": error,
        "error_display": error_display,
        "mutated": False,
        "diplomatic_dialogue": dict(dialogue),
        "awaiting_diplomatic_response": True,
        "talleyrand_text": talleyrand_text,
        "message": talleyrand_text or error_display,
        "suppress_proposal_result_popup": True,
    }
    if validation_error is not None:
        payload["validation_error"] = validation_error
    if validation_detail is not None:
        payload["validation_detail"] = validation_detail
    if validation_error_index is not None:
        payload["validation_error_index"] = validation_error_index
    if extra:
        payload.update(dict(extra))
    return payload


def ratify_settlement_confirm(
    world: Any,
    dialogue: Mapping[str, Any],
) -> Dict[str, Any]:
    """Run the C2 common-peace ratification mutation.

    Per spec §10.5 / §11.1 / §11 ordering this function:

    1. Re-runs ``revalidate_staged_settlement`` on the live world.
    2. Builds a per-pair plan of which active cross-side pairs settle to
       ``PEACE`` vs ``ALLIANCE`` (forced-alliance only when a
       ``forced_alliance`` term targets the proposer-side member of the
       pair).
    3. Snapshots each covered pair's war data before cleanup.
    4. Applies package-level territory / gold / liberation term outcomes.
    5. Drives per-pair state transitions through ``set_diplomatic_state``
       + ``cleanup_war_end`` so the bilateral peace closure path runs
       (which moves the pair to ``resolved_diplo_keys`` and closes the
       contribution episode via ``resolve_pair_to_resolved``).
    6. For forced-alliance pairs, re-sets the state to ``ALLIANCE`` and
       applies forced-origin metadata, Continental System membership, and
       coalition threat per WPS-C §9.2 (already wired for bilateral
       forced-alliance treaties in ``_ratify_treaty``).
    7. Invalidates ``war_instances_by_*`` / bloc / active-nation caches
       before any subsequent reaction reader runs.
    8. Pops the ``settlement_confirm`` dialogue.

    D1/D2 settlement / cross-war reaction routing now runs AFTER the
    cache invalidation step in this function but BEFORE the dialogue is
    popped, satisfying spec §11 line 1239 ordering. The returned summary
    exposes the structured reaction payload under
    ``settlement_reactions`` for downstream presentation work (Slice E).
    """
    war_id = str(dialogue.get("war_id") or "")
    validation = revalidate_staged_settlement(world, dialogue)
    if not validation.get("ok"):
        world.dialogue_manager.pop()
        error = str(validation.get("error") or "")
        proposer_side = str(dialogue.get("proposer_side") or "")
        accepting_side = str(dialogue.get("accepting_side") or "")
        result = {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "confirm",
            "war_id": war_id,
            "error": error,
            "error_display": _error_display(error),
            "mutated": False,
            "settlement_reactions": _failed_ratification_reaction_summary(
                world,
                war_id=war_id,
                proposer_side=proposer_side,
                accepting_side=accepting_side,
                covered_enemy_participants=dialogue.get("covered_enemy_participants") or [],
                settlement_terms=dialogue.get("settlement_terms") or [],
            ),
        }
        if validation.get("must_reopen"):
            # SC-2/SC-3/SC-13/SC-14b: gate `must_reopen=True` on a non-empty
            # target and the SC-14b per-(war_id, turn) attempt cap.
            result.update(_safe_reopen_response(world, war_id=war_id, dialogue=dialogue))
        else:
            result["must_reopen"] = False
            result["reopen_target"] = _reopen_target(war_id, dialogue)
        return result

    war_instance = (getattr(world, "war_instances", {}) or {}).get(war_id)
    if not war_instance or war_instance.get("ended_turn") is not None:
        world.dialogue_manager.pop()
        error = "inactive_war_instance"
        result = {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "confirm",
            "war_id": war_id,
            "error": error,
            "error_display": _error_display(error),
            "mutated": False,
            "settlement_reactions": _failed_ratification_reaction_summary(
                world,
                war_id=war_id,
                proposer_side=str(dialogue.get("proposer_side") or ""),
                accepting_side=str(dialogue.get("accepting_side") or ""),
                covered_enemy_participants=dialogue.get("covered_enemy_participants") or [],
                settlement_terms=dialogue.get("settlement_terms") or [],
            ),
        }
        result.update(_safe_reopen_response(world, war_id=war_id, dialogue=dialogue))
        # The original code path treated this as `must_reopen=True`; keep
        # that behavior unless SC-14b's per-(war_id, turn) cap intervenes.
        return result

    # SC-3/SC-4: fresh acceptance rescore from current world state before mutation.
    proposer_side = str(dialogue.get("proposer_side") or "")
    accepting_side = str(dialogue.get("accepting_side") or "")
    covered = list(dialogue.get("covered_enemy_participants") or [])
    settlement_terms = list(dialogue.get("settlement_terms") or [])
    # G2-Slice-W1: pass labeled white-peace + caller_kind through to the
    # ratification event + empty-Ratify gate. Player-editor-staged empty
    # drafts with white_peace=False fail the gate even if acceptance
    # passes (defense-in-depth on top of the dialogue's `options[]` /
    # `available_action_ids[]` omission).
    white_peace = bool(dialogue.get("white_peace", False))
    caller_kind = str(dialogue.get("caller_kind") or "player_editor")
    # SC-31 / G2-Slice-8 - surrender_preset propagates through the
    # ratification event so dispatch/ledger/campaign-log render the
    # outcome as a labeled surrender. The flag is set when the player
    # accepted Talleyrand's surrender preset (or any future authored
    # surrender package that opts into the label); generic dependency
    # clauses authored manually do not toggle the flag automatically.
    surrender_preset = bool(dialogue.get("surrender_preset", False))
    if (
        caller_kind == "player_editor"
        and not settlement_terms
        and not white_peace
    ):
        result = _blocked_ratify_reattach(
            dialogue,
            war_id=war_id,
            error="empty_editor_draft_ratification",
            talleyrand_text=(
                "Sire, this settlement cannot be ratified without authored terms."
            ),
        )
        result["error_display"] = _error_display("empty_authored_draft")
        return result

    # SC-5R-1 pre-ratification clause-type revalidation: defense in
    # depth for dialogues that bypass the submit-time `validate_settlement_terms`
    # call (e.g. fixture-staged tests, save-loaded drafts that survived
    # a code change). The goal is narrow: the cut clause type guard
    # (an unrecognized `type` like the D3-CUT clause) must fail before
    # `_apply_settlement_terms` runs so treaty history cannot record an
    # unsupported clause. Strict per-key schema validation already runs
    # at submit time through `_execute_propose_common_peace` and
    # `_stage_replacement_settlement_terms`; the legacy apply path
    # tolerates a few key variants (e.g. `regions` vs `region`) for
    # backward compat with historical ratification fixtures, so the
    # pre-ratify guard checks only the clause `type` field. White peace
    # ratifies an empty package by design and skips the non-empty guard.
    if settlement_terms and not white_peace:
        for idx, clause in enumerate(settlement_terms):
            if not isinstance(clause, Mapping):
                # PF-1 / D2: a blocked ratify keeps the staged REVIEW mounted
                # and re-attaches it (the Tier-2 net pattern) so the popup
                # re-mounts with the failure rendered — never a popped
                # dialogue with no surface and no reason.
                return _blocked_ratify_reattach(
                    dialogue,
                    war_id=war_id,
                    error="submitted_terms_failed_revalidation",
                    validation_error="invalid_clause_schema",
                    validation_detail=_error_display("invalid_clause_schema"),
                    validation_error_index=idx,
                    talleyrand_text=(
                        "Sire, the settlement draft is malformed and cannot "
                        "be ratified."
                    ),
                )
            clause_type = clause.get("type")
            if (
                clause_type not in CANONICAL_CLAUSE_TYPES
                and clause_type not in RATIFY_LEGACY_APPLY_CLAUSE_TYPES
            ):
                return _blocked_ratify_reattach(
                    dialogue,
                    war_id=war_id,
                    error="submitted_terms_failed_revalidation",
                    validation_error="invalid_clause_type",
                    validation_detail=_error_display("invalid_clause_type"),
                    validation_error_index=idx,
                    talleyrand_text=(
                        "Sire, the settlement draft contains an unsupported "
                        "clause and cannot be ratified."
                    ),
                )

    # Re-front Slice 3 §12 defense-in-depth (CRITICAL audit fix): re-run the
    # multi-party cross-court validity rules — V1 region double-promise, V2
    # uncovered court, V3 war-side, V4 self-reference / dependency eligibility —
    # against the LIVE world before mutation. The authoring gates (POST-preview,
    # Submit, restage) already enforce these, but staged terms can outlive the
    # state they were validated against (save/load, a drifting world); without
    # this gate a stale package mutates state — e.g. a staged liberation whose
    # vassal's live lord has changed would otherwise release the wrong (and
    # uncovered) lord's vassal at `_apply_settlement_terms`. Staged terms are
    # normalized to the canonical shape first (apply-format `gold_lump` / plural
    # `regions` → canonical) so the strict schema validator accepts the legacy
    # apply-format the fixtures + historical drafts use, and the authoring-only
    # solvency gate is skipped (the apply path clamps gold to the payer balance
    # rather than blocking). White peace ratifies an empty package by design.
    if settlement_terms and not white_peace:
        staged_revalidation = validate_settlement_terms(
            _normalize_staged_terms_for_validation(settlement_terms),
            proposer_side=proposer_side,
            covered_enemy_participants=covered,
            world=world,
            war_instance=war_instance,
            enforce_solvency=False,
        )
        if not staged_revalidation.get("valid"):
            revalidation_error = str(staged_revalidation.get("error") or "")
            return _blocked_ratify_reattach(
                dialogue,
                war_id=war_id,
                error="submitted_terms_failed_revalidation",
                validation_error=revalidation_error,
                validation_detail=str(
                    staged_revalidation.get("disabled_reason_display")
                    or _error_display(revalidation_error)
                ),
                validation_error_index=staged_revalidation.get("error_index"),
                talleyrand_text=(
                    "Sire, the terms we staged no longer hold against the present "
                    "situation — this settlement cannot be ratified as written."
                ),
            )

    fresh_acceptance = settlement_scoring.calculate_common_peace_acceptance(
        world,
        war_id=war_id,
        war_instance=war_instance,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        accepting_leader=_side_leader(war_instance, accepting_side),
        proposer_side_leader=_side_leader(war_instance, proposer_side),
        covered_enemy_participants=covered,
        settlement_terms=settlement_terms,
    )
    fresh_hard_stops = list(fresh_acceptance.get("hard_stops") or [])
    fresh_score = fresh_acceptance.get("score")
    fresh_threshold = fresh_acceptance.get("accept_threshold") or 50
    fresh_verdict = fresh_acceptance.get("verdict") or "reject"

    # FA-3: the same consent the review was staged with, re-read from the
    # dialogue and re-validated against the staged terms. A hard stop still
    # blocks — consent says a court is willing, never that the package is
    # legal or that the pair is still at war.
    consenting_courts = consenting_courts_for_ratification(dialogue)
    accepting_leader_consents = bool(
        consenting_courts
        and str(_side_leader(war_instance, accepting_side) or "")
        in set(consenting_courts)
    )

    # SC-4: unknown hard-stop codes fail closed.
    has_unknown_hard_stop = any(
        (hs.get("reason") or "") not in SETTLEMENT_HARD_STOP_CODES
        for hs in fresh_hard_stops
    )
    ratification_blocked = (
        fresh_hard_stops
        or has_unknown_hard_stop
        or (
            not accepting_leader_consents
            and (
                fresh_verdict in ("reject", "blocked")
                or (fresh_score is not None and fresh_score < fresh_threshold)
            )
        )
    )
    if ratification_blocked:
        error = "acceptance_blocked" if fresh_hard_stops or has_unknown_hard_stop else "acceptance_rejected"
        band_display = acceptance_band_display(str(fresh_verdict or ""))
        top_blocker = ""
        feedback = list(fresh_acceptance.get("feedback") or [])
        if feedback and isinstance(feedback[0], Mapping):
            top_blocker = str(
                feedback[0].get("component_display")
                or feedback[0].get("display")
                or feedback[0].get("component")
                or ""
            )
        if fresh_hard_stops:
            first_stop = fresh_hard_stops[0]
            if isinstance(first_stop, Mapping):
                top_blocker = str(
                    first_stop.get("display")
                    or first_stop.get("detail")
                    or first_stop.get("reason")
                    or top_blocker
                )
        top_blocker = top_blocker or "a hard condition"
        # PF-1 / D2: re-attach the still-mounted REVIEW (the popup hides on
        # every affordance click and only re-mounts from a returned
        # `diplomatic_dialogue`), so a rescore-blocked Ratify renders its
        # reason instead of orphaning the surface.
        return _blocked_ratify_reattach(
            dialogue,
            war_id=war_id,
            error=error,
            talleyrand_text=resolve_settlement_voice_line(
                "settlement_rescored_after_staging_talleyrand",
                war_label=str(dialogue.get("war_label") or war_id),
                acceptance_band=band_display,
                top_blocker=top_blocker,
            ),
            extra={
                "acceptance_verdict": fresh_verdict,
                "acceptance_score": fresh_score,
                "acceptance_threshold": fresh_threshold,
                "hard_stops": fresh_hard_stops,
                "settlement_reactions": _failed_ratification_reaction_summary(
                    world,
                    war_id=war_id,
                    proposer_side=proposer_side,
                    accepting_side=accepting_side,
                    covered_enemy_participants=covered,
                    settlement_terms=settlement_terms,
                ),
            },
        )

    # Re-front Slice 1 §11.4: the per-covered-court ratification gate (defense
    # in depth beyond the dialogue's `can_ratify`). The single-leader rescore
    # above is retained for the leader summary + the n=1 path; this
    # additionally requires EVERY covered court to carry, so a multi-court
    # settlement cannot ratify while a covered minor holds out. White peace
    # ratifies an empty package by design and is exempt.
    if not white_peace and settlement_terms:
        per_court_block = compute_per_court_acceptance(
            world,
            war_id=war_id,
            war_instance=war_instance,
            proposer_side=proposer_side,
            accepting_side=accepting_side,
            proposer_side_leader=_side_leader(war_instance, proposer_side),
            covered_enemy_participants=covered,
            settlement_terms=settlement_terms,
            # FA-3: the offering courts' own terms carry their consent here
            # too, or the §11.4 gate rejects the package its authors wrote.
            consenting_courts=consenting_courts,
        )
        overall = per_court_block["overall_acceptance"]
        if not overall.get("carries"):
            holdouts = list(overall.get("holdout_courts") or [])
            holdout_label = holdouts[0] if holdouts else "a covered court"
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "confirm",
                "war_id": war_id,
                "error": "acceptance_rejected",
                "error_display": _error_display("acceptance_rejected"),
                "per_court_acceptance": per_court_block["per_court_acceptance"],
                "overall_acceptance": overall,
                "holdout_courts": holdouts,
                "mutated": False,
                "talleyrand_text": (
                    resolve_settlement_voice_line(
                        "settlement_multi_court_holdout_blocks_talleyrand",
                        war_label=str(dialogue.get("war_label") or war_id),
                        holdout_court=holdout_label,
                    )
                    or (
                        f"Sire, {holdout_label} will not sign; the settlement "
                        "cannot be ratified until they are eased or dropped."
                    )
                ),
                "settlement_reactions": _failed_ratification_reaction_summary(
                    world,
                    war_id=war_id,
                    proposer_side=proposer_side,
                    accepting_side=accepting_side,
                    covered_enemy_participants=covered,
                    settlement_terms=settlement_terms,
                ),
            }

    plan = _build_pair_ratification_plan(
        world,
        war_instance,
        proposer_side=proposer_side,
        covered=covered,
        settlement_terms=settlement_terms,
    )
    if not plan:
        world.dialogue_manager.pop()
        error = "no_resolvable_pairs"
        result = {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "confirm",
            "war_id": war_id,
            "error": error,
            "error_display": _error_display(error),
            "mutated": False,
            "settlement_reactions": _failed_ratification_reaction_summary(
                world,
                war_id=war_id,
                proposer_side=proposer_side,
                accepting_side=accepting_side,
                covered_enemy_participants=covered,
                settlement_terms=settlement_terms,
            ),
        }
        result.update(_safe_reopen_response(world, war_id=war_id, dialogue=dialogue))
        return result

    pre_cleanup_snapshots = _capture_pre_cleanup_snapshots(world, plan)
    # Capture pre-cleanup participant lists + side leaders so the
    # post-ratification `settlement_summary` event can render a friendly
    # war_label / leader markers even after cleanup_war_end empties the
    # live war_instance.attackers / .defenders lists. Spec §11.6 line
    # 1287 — event payload minimums.
    pre_cleanup_war_label = ""
    pre_cleanup_attackers = list(war_instance.get("attackers") or [])
    pre_cleanup_defenders = list(war_instance.get("defenders") or [])
    if pre_cleanup_attackers and pre_cleanup_defenders:
        # G4F-11 (term-reflection audit): name BOTH full sides — the
        # first-vs-first pair label rendered the multilateral ratification
        # as "Settlement of France vs Britain" on the dispatch/ledger
        # record, the same Britain-only misreading class G4F-7 fixed on
        # the dialogue surface.
        pre_cleanup_war_label = (
            f"{' + '.join(pre_cleanup_attackers)} vs "
            f"{' + '.join(pre_cleanup_defenders)}"
        )
    pre_cleanup_proposer_members = (
        list(pre_cleanup_attackers)
        if proposer_side == "attackers"
        else list(pre_cleanup_defenders)
    )
    pre_cleanup_accepting_members = (
        list(pre_cleanup_attackers)
        if accepting_side == "attackers"
        else list(pre_cleanup_defenders)
    )
    pre_cleanup_attacker_leader = str(war_instance.get("attacker_leader") or "")
    pre_cleanup_defender_leader = str(war_instance.get("defender_leader") or "")
    applied_clauses = _apply_settlement_terms(
        world,
        settlement_terms=settlement_terms,
        war_id=war_id,
        settlement_route_id=str(dialogue.get("route_id") or ""),
    )
    resolved_pairs, fa_applied = _resolve_pair_state_transitions(
        world, plan, settlement_terms,
    )
    applied_clauses.extend(fa_applied)
    _record_common_peace_treaties(
        world, plan=plan, settlement_terms=settlement_terms,
    )

    # AI-5b(i) (§3.6): a settlement that STRIPS a court — its capital, or
    # two-plus provinces in one signing — leaves a durable
    # `punitive_settlement` memory (author, provinces, turn). The
    # emergent-design poll reads it; the volte-face is foreclosed by it.
    # APPLIED clauses only — what actually transferred, never the ask.
    from backend.game_logic.emergent_designs import (
        collect_cessions_from_clauses, record_punitive_cessions,
    )
    record_punitive_cessions(
        world, collect_cessions_from_clauses(applied_clauses))

    # Spec §11 ratification ordering line 1239: invalidate war-instance
    # indexes + Balance of Europe / hegemony / bloc caches before any
    # cross-war reaction reader runs in the next slice.
    if hasattr(world, "invalidate_war_instance_indexes"):
        world.invalidate_war_instance_indexes()
    if hasattr(world, "invalidate_bloc_members_cache"):
        world.invalidate_bloc_members_cache()
    if hasattr(world, "invalidate_active_nations_cache"):
        world.invalidate_active_nations_cache()

    # NA-6 §11.10-2, the SECOND formation call site: a cession or carve
    # completed at the table proclaims the turn it happens (§11.8 stage 1),
    # not on the next tick. Runs AFTER the three invalidations above
    # because agenda activation reads region control AND war/alliance
    # geometry, both of which the clauses just moved. Idempotent via the
    # `nation_formations` latch, so the tick-side poll is a harmless no-op
    # afterwards. NOTE: a dispatch line queued here would be discarded —
    # `pending_dispatch_events` is cleared at the top of the next tick — so
    # the beat's durable surfaces are the campaign log, the notification
    # rail, and (NA-6b) the Proclamation card.
    from backend.game_logic.formations import process_formations
    process_formations(world)

    war_instance_after = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    war_ended = war_instance_after.get("ended_turn") is not None

    # D1/D2 settlement / cross-war reaction routing per spec §11.5 / §14.
    # Runs AFTER cache invalidation but BEFORE the dialogue is popped so
    # any reaction reader sees fresh `war_instances_by_*` indexes.
    from backend.game_logic.settlement_reactions import (
        route_settlement_reactions,
    )
    staged_route_id = str(dialogue.get("route_id") or "")
    # SC-15: build the fresh ratification-time acceptance_snapshot from
    # the rescore that authorized mutation. Archived settlement review
    # later renders this snapshot rather than the stale staging score.
    # `acceptance_at_staging` is preserved for audit context.
    acceptance_snapshot = {
        "score": fresh_acceptance.get("score"),
        "verdict": fresh_acceptance.get("verdict"),
        "threshold": fresh_acceptance.get("accept_threshold"),
        "band": str(fresh_acceptance.get("verdict") or "near_acceptable"),
        "band_display": acceptance_band_display(
            str(fresh_acceptance.get("verdict") or "")
        ),
        "top_components": list(fresh_acceptance.get("feedback") or [])[:3],
        "hard_stops": list(fresh_acceptance.get("hard_stops") or []),
    }
    staged_acceptance = (dialogue.get("settlement_preview") or {}).get("acceptance") or {}
    acceptance_at_staging = {
        "score": staged_acceptance.get("score") or staged_acceptance.get("total"),
        "verdict": staged_acceptance.get("verdict") or staged_acceptance.get("band"),
        "threshold": staged_acceptance.get("threshold") or staged_acceptance.get("accept_threshold"),
        "band": str(staged_acceptance.get("band") or staged_acceptance.get("verdict") or ""),
    }
    reaction_summary = route_settlement_reactions(
        world,
        war_id=war_id,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        covered_enemy_participants=list(covered),
        settlement_terms=list(settlement_terms),
        resolved_pairs=resolved_pairs,
        applied_clauses=applied_clauses,
        pre_cleanup_snapshots=pre_cleanup_snapshots,
        war_ended=bool(war_ended),
        balance_projection=dict(dialogue.get("balance_projection") or {}),
        pre_cleanup_war_label=pre_cleanup_war_label,
        pre_cleanup_proposer_members=pre_cleanup_proposer_members,
        pre_cleanup_accepting_members=pre_cleanup_accepting_members,
        pre_cleanup_attacker_leader=pre_cleanup_attacker_leader,
        pre_cleanup_defender_leader=pre_cleanup_defender_leader,
        staged_route_id=staged_route_id,
        acceptance_snapshot=acceptance_snapshot,
        acceptance_at_staging=acceptance_at_staging,
        white_peace=white_peace,
        surrender_preset=surrender_preset,
    )

    world.dialogue_manager.pop()
    _discard_scoped_settlement_draft_for_dialogue(world, dialogue)

    result_message = (
        f"Settlement Ratified: {dialogue.get('war_label') or pre_cleanup_war_label or war_id} "
        f"({len(resolved_pairs)} pair(s) resolved)."
    )
    # SC-14c: result feedback consumes the staged route id verbatim. The
    # summary event already echoes the staged id, so prefer that path; fall
    # back to the staged dialogue's id (same value) before minting a fresh
    # one for legacy callers.
    review_route_id = str(
        (reaction_summary.get("summary_event") or {}).get("route", {}).get("route_id", "")
        or dialogue.get("route_id")
        or mint_settlement_route_id(world, war_id=war_id)
    )
    # SC-14/14d/14e: result feedback re-resolves active vs archived at the
    # moment ratification completes. Active partial settlements route to
    # the live war/settlement surface; archived (full-war end) settlements
    # route to the ledger row.
    live_review_target = derive_settlement_review_target(world, war_id=war_id)
    review_route = {
        "surface": live_review_target,
        "review_target": live_review_target,
        "route_id": review_route_id,
        "war_id": war_id,
        "war_ended": bool(war_ended),
    }
    return {
        "success": True,
        "dialogue_type": "settlement_confirm",
        "action": "confirm",
        "war_id": war_id,
        "proposer_side": proposer_side,
        "accepting_side": accepting_side,
        "covered_enemy_participants": list(covered),
        "resolved_pairs": resolved_pairs,
        "applied_clauses": applied_clauses,
        "pre_cleanup_snapshots": pre_cleanup_snapshots,
        "war_ended": bool(war_ended),
        "settlement_reactions": reaction_summary,
        "settlement_result_feedback": {
            "title": "Settlement Ratified",
            "war_label": dialogue.get("war_label") or pre_cleanup_war_label or war_id,
            "resolved_pair_count": len(resolved_pairs),
            "review_target": "ledger_settlements",
            "route_id": review_route_id,
            "war_id": war_id,
            "review_route": review_route,
            "message": (
                f"{len(resolved_pairs)} hostile pair(s) resolved. "
                "Review the settlement in the diplomatic ledger."
            ),
        },
        "mutated": True,
        "message": result_message,
    }


def _stage_replacement_settlement_terms(
    world: Any,
    dialogue: Mapping[str, Any],
    *,
    action: str,
    terms: Iterable[Mapping[str, Any]],
    message: str,
    surrender_preset: bool = False,
    dialogue_mode: str = "REVIEW",
) -> Dict[str, Any]:
    war_id = str(dialogue.get("war_id") or "")
    covered = list(dialogue.get("covered_enemy_participants") or [])
    selected_target = str(dialogue.get("selected_target_nation") or "")
    actor = getattr(world, "player_nation", "France")
    replacement_terms = [
        dict(t) for t in (terms or []) if isinstance(t, Mapping)
    ]
    # SC-5R-1 pre-staging revalidation: an author handler that
    # constructs tampered or cut clause types (e.g. a clause `type`
    # that is no longer in `CANONICAL_CLAUSE_TYPES`, or a
    # `gold_indemnity` carrying an unknown `turns` field) must fail
    # before `build_settlement_preview(...)` so the dialogue never
    # reaches the player. The validator is the single source of truth
    # for clause schema; the matching pre-ratification guard in
    # `ratify_settlement_confirm` provides defense in depth for
    # dialogues that bypass this path (fixture-staged or save-loaded).
    war_instance = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    revalidation = validate_settlement_terms(
        replacement_terms,
        proposer_side=str(dialogue.get("proposer_side") or ""),
        covered_enemy_participants=covered,
        world=world,
        war_instance=war_instance,
    )
    if not revalidation.get("valid"):
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": action,
            "war_id": war_id,
            "error": "submitted_terms_failed_revalidation",
            "error_display": _error_display(
                "submitted_terms_failed_revalidation"
            ),
            "validation_error": revalidation.get("error"),
            "validation_detail": revalidation.get("disabled_reason_display"),
            "validation_error_index": revalidation.get("error_index"),
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }
    preview = build_settlement_preview(
        world,
        war_id=war_id,
        proposer_side=str(dialogue.get("proposer_side") or ""),
        settlement_terms=replacement_terms,
        covered_enemy_participants=covered,
        actor_nation=actor,
        ignore_active_dialogue=True,
    )
    if not preview.get("success"):
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": action,
            "war_id": war_id,
            "error": preview.get("error") or "settlement_replacement_failed_preview",
            "error_display": preview.get("error_display") or (
                "The replacement draft could not be previewed."
            ),
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }
    new_dialogue = build_settlement_confirm_dialogue(
        world,
        preview,
        selected_target_nation=selected_target or None,
        caller_kind=str(dialogue.get("caller_kind") or "player_editor"),
        white_peace=bool(dialogue.get("white_peace", False)),
        surrender_preset=surrender_preset,
        dialogue_mode=dialogue_mode,
    )
    # SC-5R-1 scoped draft persistence (CH-3: the ONE store): the
    # replacement draft is keyed by `compute_settlement_draft_key` so a
    # same-war restage with a different selected target / covered scope
    # keeps both drafts addressable.
    save_scoped_settlement_draft(
        world,
        war_id=war_id,
        selected_target_nation=selected_target,
        covered_enemy_participants=covered,
        settlement_terms=replacement_terms,
    )
    world.dialogue_manager.replace(new_dialogue)
    result = {
        "success": True,
        "dialogue_type": "settlement_confirm",
        "action": action,
        "war_id": war_id,
        "diplomatic_dialogue": new_dialogue,
        "settlement_preview": preview["settlement_preview"],
        "awaiting_diplomatic_response": True,
        "mutated": False,
        "message": message,
        "suppress_proposal_result_popup": True,
    }
    return result
