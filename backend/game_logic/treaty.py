"""The treaty's ONE verdict — DD-1 "The Table and the Treaty", Step 2.

Pre-Deploy S7 (October 11, 2026; `docs/PRE_DEPLOY_PLAN.md` §3.1). The
quarter's diplomacy P1s all had one shape: the table said yes and the treaty
said no — "can this be signed?" was answered in six places and the ratifier
kept the only maintained copy. This module is where that answer lives.

Slice A (this file's first landing) carries the WORDS for a declaration the
war-instance model refuses (DD1-11): the engine's code
(`war_instance_side_conflict`) never reaches the player.

Slice B (the same day) lands `can_sign(world, letter) -> Verdict`: the
ratifier's guard sequence lifted out of `WorldState._ratify_treaty` and read
by every surface AND the ratifier — the letter's buttons at build and on
every read, the wizard's chips, the counsel's hints, the Congress's levers,
the AI producers (SF-V1's `treaty_offer_refusal`, SF-V5's settlement
emitter) and the ratifier itself, which keeps no guard of its own. A letter
is one of four kinds:

  (a) a TREATY letter — the ratifier's proposal dict: the no-downgrade
      ladder (its sentence byte-identical), the `vassal_pair` clause (no
      treaty is signed on a VASSAL pair — release is the only road),
      `validate_transition` (DD1-12: the ratifier never read the state
      machine), the relation floors, the AP clause read proposer-over-
      target, the war bargains, the vassal gates, the AI-AI alliance rule;
      with `at_send=True` the send road's own paradox HARD_STOP on a
      player's outgoing peace (SFR-D34);
  (b) a SETTLEMENT offer — the settlement road's eligibility gate for
      France's side (`one_to_one_war` / `not_side_leader` — DD1-3, SFR-B1)
      and the per-court carry (SF-V5's dry run);
  (c) an ALLY petition — the table is open AND the clause prevalidates
      (DD1-1);
  (d) a CLIENT petition — `vassal._grant_verdict` (DD1-2).

Every refusal is in WORDS: no snake_case key ever reaches `message`.
`stamp_option` writes one verdict into an option under every key the popups,
the driver and the sweep read (`enabled` + `reason`, `available` +
`disabled_reason_display`) and the `closed_clause` marker the answer seam
refuses by (NPC-21, widened by marker, never by dialogue type).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

# The proposal type → diplomatic state map the ratifier has always used.
TREATY_STATE_MAP = {
    "peace": "PEACE",
    "armistice": "ARMISTICE",
    "armistice_losing": "ARMISTICE",
    "armistice_winning": "ARMISTICE",
    "alliance": "ALLIANCE",
    "defensive_alliance": "DEFENSIVE_ALLIANCE",
    "open_borders": "OPEN_BORDERS",
    "non_aggression": "NON_AGGRESSION",
    "vassalage": "VASSAL",
}

SETTLEMENT_LETTER_TYPES = frozenset({"incoming_settlement_offer"})
ALLY_PETITION_TYPE = "ally_settlement_petition"
# The accept-shaped actions a letter can carry (the sweep's own list).
ACCEPT_ACTIONS = frozenset({
    "accept_ai_proposal", "accept_counter_offer", "accept_ai_ultimatum",
    "accept_settlement_offer", "grant_ally_petition_clause",
    "honor_bargain_in_settlement",
})
# The marker `stamp_option` writes on a closed option; the answer seam
# (`handle_diplomatic_dialogue_response`) refuses an option that carries it.
CLOSED_CLAUSE_KEY = "closed_clause"


@dataclass(frozen=True)
class Verdict:
    """What the ratifier would say to this letter, before it is shown.

    `ok` — it would sign. `clause` — the guard that refused, as a short
    key for telemetry and the tests (never shown). `message` — the refusal
    in the player's words, byte-identical to the ratifier's own sentence
    where the ratifier had one. `price` — the DP the signing costs the
    player, when known. `who_must_consent` — the courts whose consent the
    package needs. `target` — the court the ratifier's refusal dict names
    (`{"type": "diplomatic_treaty_failed", "target": …}`). `silent` — an
    AI-AI refusal: the ratifier answers None, not a dict. `closes` — a
    refused option is CLOSED (the marker written); False only for a client
    petition's `stands` verdict, whose Grant must stay pressable so the
    handler's own road leaves the petition standing (IQ7-RV2)."""
    ok: bool
    clause: str = ""
    message: str = ""
    price: Optional[int] = None
    who_must_consent: Tuple[str, ...] = field(default_factory=tuple)
    target: str = ""
    silent: bool = False
    closes: bool = True


def _ok(**kw) -> Verdict:
    return Verdict(True, **kw)


def _no(clause: str, message: str, **kw) -> Verdict:
    return Verdict(False, clause=clause, message=message, **kw)


# ═══════════════════════════════════════════════════════════════════════════
# The words
# ═══════════════════════════════════════════════════════════════════════════

def _court(world, nation: str, *, capitalize: bool = False) -> str:
    """A court by its formed display name, with its article."""
    from backend.display_names import with_definite_article
    from backend.game_logic.formations import formed_display_name
    shown = formed_display_name(world, nation) if nation else "a foreign court"
    return with_definite_article(shown, capitalize=capitalize)


def _capitalised(text: str) -> str:
    # SR-1d (PR-D1b's rider): "A Armistice treaty" — the article helper
    # returns lowercase; the sentence starts here.
    return (text[:1].upper() + text[1:]) if text else text


def _other_side_leader(world, war_id: Optional[str], *nations: str) -> str:
    """The leader of the side NONE of `nations` stand on in `war_id`, or ''."""
    instance = (getattr(world, "war_instances", {}) or {}).get(str(war_id or ""))
    if not isinstance(instance, dict):
        return ""
    sides = instance.get("side_by_nation") or {}
    on = {str(sides.get(n) or "") for n in nations if n}
    on.discard("")
    if len(on) != 1:
        return ""
    side = next(iter(on))
    other = "defender_leader" if side == "attackers" else "attacker_leader"
    return str(instance.get(other) or "")


def declaration_refusal_words(world, aggressor: str, target: str,
                              result: Dict[str, Any]) -> str:
    """DD1-11: the sentence a refused declaration shows the player — the
    clause in words, read off the instance that refused it. `result` is the
    dict `ensure_war_instance_for_pair` / `validate_war_declaration` returned
    (`error`, `details`); the code and its details still ride the executor's
    result for the log and the tests, never this sentence."""
    error = str((result or {}).get("error") or "")
    details = (result or {}).get("details") or {}
    player = getattr(world, "player_nation", "France")
    target_shown = _court(world, target, capitalize=True)
    aggressor_shown = _court(world, aggressor)
    if error == "war_instance_side_conflict":
        leader = _other_side_leader(world, details.get("war_id"), aggressor, target)
        if aggressor == player:
            beside = "beside us"
        else:
            beside = f"beside {aggressor_shown}"
        if leader and leader not in (aggressor, target):
            return (f"{target_shown} fights {beside} in the war with "
                    f"{_court(world, leader)} — end that war first.")
        return (f"{target_shown} fights {beside} already — a declaration would "
                f"set one side of a war against itself. End that war first.")
    if error == "war_instance_merge_required":
        return (f"{target_shown} and {aggressor_shown} already stand on one side "
                f"of a war — a declaration would set that side against itself.")
    return (f"The chancery finds no lawful ground for a war on {_court(world, target)} "
            f"today.")


# ═══════════════════════════════════════════════════════════════════════════
# The letter's kind
# ═══════════════════════════════════════════════════════════════════════════

def _letter_kind(letter: Any) -> str:
    """'treaty' | 'settlement' | 'ally_petition' | 'client_petition' | ''."""
    if not isinstance(letter, dict):
        return ""
    dtype = str(letter.get("type") or letter.get("dialogue_type") or "")
    if dtype in SETTLEMENT_LETTER_TYPES or (
            "offer_id" in letter and "settlement_terms" in letter):
        return "settlement"
    if dtype == ALLY_PETITION_TYPE:
        return "ally_petition"
    from backend.game_logic.vassal import CLIENT_PETITION_TYPE, is_client_petition
    if is_client_petition(letter) or dtype == CLIENT_PETITION_TYPE:
        return "client_petition"
    if "context" in letter and isinstance(letter.get("context"), dict):
        return "treaty"
    if (letter.get("proposer_nation") or letter.get("proposer")) and (
            letter.get("target_nation") or letter.get("target")):
        return "treaty"
    return ""


def proposal_of(letter: Dict[str, Any], player: str = "") -> Dict[str, Any]:
    """The ratifier's proposal dict behind a treaty letter — the dialogue's
    `context.counter_terms` (a counter) or `context.proposal` (an incoming
    letter), else the letter itself (a bare proposal dict). A dialogue's
    terms name the court on `source_nation` and the player as the recipient
    by construction (the accept road fills both the same way)."""
    context = letter.get("context") if isinstance(letter.get("context"), dict) else None
    if context is not None:
        terms = context.get("counter_terms") or context.get("proposal") or {}
        if isinstance(terms, dict) and terms:
            out = dict(terms)
            source = str(context.get("source_nation") or letter.get("target_nation") or "")
            if not (out.get("proposer_nation") or out.get("proposer")) and source:
                out["proposer_nation"] = source
            if not (out.get("target_nation") or out.get("target")) and player:
                out["target_nation"] = player
            return out
        return {}
    return dict(letter)


# ═══════════════════════════════════════════════════════════════════════════
# (a) The treaty
# ═══════════════════════════════════════════════════════════════════════════

def treaty_clauses_of(proposal: Dict[str, Any], proposer: str, target: str) -> List[Dict[str, Any]]:
    """The clause list the ratifier builds from a proposal's sweeteners and
    demands — ONE builder, read by the ratifier (which applies them) and by
    the verdict (which prices the war bargains and projects the vassal cap
    on them)."""
    treaty_clauses: List[Dict[str, Any]] = []
    for s in proposal.get("sweeteners", []) or []:
        clause_entry = {
            "type": s["type"],
            "from": proposer,
            "to": target,
            "amount": int(s.get("value", 0) or 0),
        }
        if s.get("type") == "territory_cede" and "regions" in s:
            clause_entry["regions"] = s["regions"]
        # W6-7: `marshal` rides prisoner_return clauses.
        for extra_key in ("named_enemy", "claim_region", "claim_holder", "marshal", "marshals"):
            if extra_key in s:
                clause_entry[extra_key] = s[extra_key]
        treaty_clauses.append(clause_entry)
    for d in proposal.get("demands", []) or []:
        clause_entry = {
            "type": d["type"],
            "from": target,
            "to": proposer,
            "amount": int(d.get("value", 0) or 0),
        }
        if d.get("type") == "territory_cede" and "regions" in d:
            clause_entry["regions"] = d["regions"]
        # WPS-C: Carry over extra fields for forced_alliance/liberation
        if "from_nation" in d:
            clause_entry["from"] = d["from_nation"]
        if "to_nation" in d:
            clause_entry["to"] = d["to_nation"]
        for extra_key in (
            "vassal_nation", "lord_nation", "liberator",
            "includes_continental_system",
            "named_enemy", "claim_region", "claim_holder",
            "marshal",  # W6-7: prisoner_return names its prisoner
            "marshals",  # PC-F13: one term, several men
            # NA-6c / IGR-D: a `create_client` demand's SUBJECT. `tag`
            # is the authority (the apply arm re-resolves the template);
            # `provinces` feeds harshness pricing and the estate
            # warning; `client_display_name` keeps the confirm popup
            # from printing the raw template id at the player.
            "tag", "provinces", "client_display_name",
            # PC-R3: a dictated stream runs `turns` turns and holds its
            # `surety_regions` until the last payment lands.
            "turns", "surety_regions",
        ):
            if extra_key in d:
                clause_entry[extra_key] = d[extra_key]
        treaty_clauses.append(clause_entry)
    return treaty_clauses


def _treaty_verdict(world, proposal: Dict[str, Any], *, at_send: bool) -> Verdict:
    from backend.display_names import STATE_DISPLAY, with_indefinite_article
    from backend.game_logic.diplomacy import (
        STATE_RELATION_REQUIREMENTS,
        _UPGRADE_ORDER,
        check_relation_requirement,
        get_transition_dp_cost,
        validate_transition,
    )

    proposer = str(proposal.get("proposer_nation") or proposal.get("proposer") or "")
    target_nation = str(proposal.get("target_nation") or proposal.get("target") or "")
    if not proposer or not target_nation:
        # Not a letter the verdict can read (a hand-built fixture, a
        # legacy shape): nothing is promised and nothing is closed — the
        # accept road answers "proposal data missing" on its own.
        return _ok()
    player = getattr(world, "player_nation", "France")
    is_player_treaty = player in (proposer, target_nation)
    player_counterpart = ""
    if is_player_treaty:
        player_counterpart = target_nation if proposer == player else proposer
    other = player_counterpart or target_nation

    proposal_type = str(proposal.get("type") or "peace")
    target_state = TREATY_STATE_MAP.get(proposal_type, "PEACE")
    current_state = world.get_diplomatic_state(proposer, target_nation)
    diplo_key = world._make_diplo_key(proposer, target_nation)
    price: Optional[int] = None
    if is_player_treaty:
        price = int(get_transition_dp_cost(current_state, target_state))
    consent = (other,)

    def refuse(clause: str, message: str, *, named: str) -> Verdict:
        if not is_player_treaty:
            return _no(clause, message, silent=True, target=named,
                       who_must_consent=consent)
        return _no(clause, message, price=price, target=named,
                   who_must_consent=consent)

    # 1. The no-downgrade ladder — its sentence byte-identical.
    if (current_state in _UPGRADE_ORDER and target_state in _UPGRADE_ORDER
            and _UPGRADE_ORDER.index(target_state) <= _UPGRADE_ORDER.index(current_state)):
        return refuse(
            "no_downgrade",
            f"We already have {STATE_DISPLAY.get(current_state, current_state)} with "
            f"{_court(world, other)}. "
            f"{_capitalised(with_indefinite_article(STATE_DISPLAY.get(target_state, target_state)))} "
            f"treaty would be a downgrade.",
            named=target_nation)

    # 2. The vassal pair — no treaty on a VASSAL pair; release is the road.
    if current_state == "VASSAL":
        vassals = getattr(world, "vassals", {}) or {}
        client = proposer if proposer in vassals else target_nation
        lord = str((vassals.get(client) or {}).get("lord") or "")
        if lord == player or client == player:
            who = "our client" if client != player else "our lord"
            return refuse(
                "vassal_pair",
                f"{_court(world, client if client != player else lord, capitalize=True)} "
                f"is {who} — no treaty is signed inside a vassalage. Release "
                f"{'it' if client != player else 'us'} first; that is the only road.",
                named=target_nation)
        return refuse(
            "vassal_pair",
            f"{_court(world, client, capitalize=True)} answers to "
            f"{_court(world, lord)} — no treaty is signed inside a vassalage.",
            named=target_nation)

    # 3. The state machine (DD1-12) — the ratifier never read it.
    if not validate_transition(current_state, target_state):
        if target_state == "VASSAL":
            words = (f"A vassalage of {_court(world, other)} needs a war (a dictated "
                     f"peace) or open borders and above — we stand at "
                     f"{STATE_DISPLAY.get(current_state, current_state)}.")
        else:
            words = (f"The chancery knows no road from "
                     f"{STATE_DISPLAY.get(current_state, current_state)} to "
                     f"{STATE_DISPLAY.get(target_state, target_state)} with "
                     f"{_court(world, other)}.")
        return refuse("state_machine", words, named=target_nation)

    if is_player_treaty:
        # 4. The relation floors (player only) — byte-identical.
        relation = world.nation_relations.get(diplo_key, 0)
        if not check_relation_requirement(current_state, target_state, relation):
            need = STATE_RELATION_REQUIREMENTS.get(target_state)
            treaty = with_indefinite_article(STATE_DISPLAY.get(target_state, target_state))
            return refuse(
                "relation_floor",
                f"Relations with {_court(world, other)} stand at {int(relation)}; "
                f"{treaty} needs {need}.",
                named=target_nation)
        # 5. The AP clause — the PROPOSER's war score over the TARGET (R98;
        # the ratifier read the player's score against `target`, which on
        # an AI letter was France against herself).
        from backend.game_logic.diplomacy import get_war_score_for
        for d in proposal.get("demands", []) or []:
            if d.get("type") == "ap_per_turn":
                score = int(get_war_score_for(world, proposer, target_nation))
                if score <= 80:
                    return refuse(
                        "ap_clause",
                        "AP demands require overwhelming military dominance (war score > 80).",
                        named=target_nation)

    # 6. AI-AI only: the alliance conflict rule.
    if not is_player_treaty and target_state in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
        for third in world.get_active_nations():  # DLF-11
            if third in (proposer, target_nation):
                continue
            if world.is_at_war(proposer, third):
                if world.get_diplomatic_state(target_nation, third) in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
                    return refuse("ai_alliance_conflict",
                                  f"{_court(world, target_nation, capitalize=True)} is allied "
                                  f"with {_court(world, third)}, whom {_court(world, proposer)} fights.",
                                  named=target_nation)
            if world.is_at_war(target_nation, third):
                if world.get_diplomatic_state(proposer, third) in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
                    return refuse("ai_alliance_conflict",
                                  f"{_court(world, proposer, capitalize=True)} is allied "
                                  f"with {_court(world, third)}, whom {_court(world, target_nation)} fights.",
                                  named=target_nation)

    # 7. The war bargains.
    treaty_clauses = treaty_clauses_of(proposal, proposer, target_nation)
    war_bargain_clauses = [c for c in treaty_clauses if c.get("type") == "war_bargain"]
    if len(war_bargain_clauses) > 1:
        return refuse("one_war_bargain", "A treaty may contain only one war bargain.",
                      named=other)
    if war_bargain_clauses:
        ceded_regions = {
            region_name
            for clause in treaty_clauses
            if clause.get("type") == "territory_cede"
            for region_name in clause.get("regions", [])
        }
        from backend.game_logic.diplomacy import validate_war_bargain
        for wb_clause in war_bargain_clauses:
            wb_named = wb_clause.get("named_enemy", "")
            wb_region = wb_clause.get("claim_region", "")
            if not wb_named or not wb_region:
                reason, ok = "War bargain requires named_enemy and claim_region", False
            elif wb_region in ceded_regions:
                reason, ok = f"Cannot bargain over {wb_region}; the same treaty cedes it.", False
            else:
                ok, reason = validate_war_bargain(
                    world, proposer, target_nation, wb_named, wb_region,
                    source_state=target_state)
            if not ok:
                return refuse("war_bargain", f"Invalid war bargain: {reason}.", named=other)

    # 8. The vassal gates — the cap (projected on the package), then the
    # creator's own pre-checks (`vassal.vassal_treaty_refusal`, which
    # `create_vassal_treaty` reads too: ONE predicate).
    if target_state == "VASSAL":
        from backend.game_logic.diplomacy import check_vassalage_power_cap
        cap = check_vassalage_power_cap(world, proposer, target_nation, terms=treaty_clauses)
        if not cap["allowed"]:
            return refuse("vassal_cap", f"Cannot vassalize {other}: {cap['reason']}.",
                          named=other)
        from backend.game_logic.vassal import vassal_treaty_refusal
        why = vassal_treaty_refusal(world, proposer, target_nation, terms=treaty_clauses)
        if why:
            return refuse("vassal_gate", why, named=other)

    # 9. The send road's own gate (SFR-D34): a player's outgoing PEACE with a
    # HARD_STOP commitment conflict is refused here, so the chips, the
    # counsel and the Congress's levers never offer it. PC-R1 (§46 B + C,
    # October 16, 2026): the alliance PARADOX is no longer one — a peace
    # that leaves an ally fighting is a priced WARNING, and one the leader
    # signs carries the ally's pair with it (`carried_in`); only a future
    # HARD_STOP type (BPH §10.2) would refuse here.
    if at_send and proposer == player and proposal_type == "peace":
        from backend.game_logic.diplomacy import get_peace_commitment_conflicts
        conflicts = get_peace_commitment_conflicts(
            world, player, target_nation, proposal.get("clauses", []) or [])
        hard = [c for c in conflicts if c.get("severity") == "HARD_STOP"]
        if hard:
            return refuse(
                "paradox",
                str(hard[0].get("display") or "This peace would create a commitment paradox."),
                named=target_nation)

    return _ok(price=price, who_must_consent=consent, target=target_nation)


# ═══════════════════════════════════════════════════════════════════════════
# (b) The settlement offer
# ═══════════════════════════════════════════════════════════════════════════

# The eligibility codes a settlement LETTER is closed on. The other codes
# (an archived war, no coverable court, an open review) are the accept road's
# own to answer; closing the producer on them would silence it where its
# `offer_already_pending` arm already governs.
SETTLEMENT_LETTER_CLOSING_CODES = frozenset({"one_to_one_war", "not_side_leader"})


def _settlement_verdict(world, offer: Dict[str, Any]) -> Verdict:
    from backend.display_names import settlement_disabled_reason_display
    from backend.game_logic.settlement_validation import (
        evaluate_open_settlement_eligibility,
    )
    player = getattr(world, "player_nation", "France")
    war_id = str(offer.get("war_id") or "")
    war = (getattr(world, "war_instances", {}) or {}).get(war_id)
    side = str(offer.get("accepting_side") or "")
    if not side and isinstance(war, dict):
        side = str((war.get("side_by_nation") or {}).get(player) or "")
    covered = [str(n) for n in (offer.get("covered_enemy_participants") or []) if n]
    elig = evaluate_open_settlement_eligibility(
        world, war_id=war_id, actor_nation=player,
        proposer_side=side or None, ignore_active_dialogue=True)
    code = str(elig.get("error") or "") if not elig.get("available") else ""
    if code in SETTLEMENT_LETTER_CLOSING_CODES:
        return _no(code, settlement_disabled_reason_display(code),
                   who_must_consent=tuple(covered), target=str(offer.get("proposer_nation") or ""))
    if not isinstance(war, dict):
        return _ok(who_must_consent=tuple(covered))
    # The carry — SF-V5's own dry run of the per-court table with the
    # offering courts' consent, on the courts still at war with our side.
    live = covered
    if side and offer.get("offer_id"):
        from backend.game_logic.settlement_offers import _live_covered_for_offer
        live, _departed = _live_covered_for_offer(world, war_id=war_id, dialogue=offer)
        if covered and not live:
            return _no("offer_courts_all_settled",
                       settlement_disabled_reason_display("offer_courts_all_settled"),
                       who_must_consent=tuple(covered))
    terms = [dict(t) for t in (offer.get("settlement_terms") or []) if isinstance(t, dict)]
    from backend.game_logic import ai_diplomacy as _ai
    if live and not _ai._letter_would_carry(world, war_id, war, player=player,
                                            covered=list(live), terms=terms):
        courts = ", ".join(_court(world, n) for n in live)
        return _no("would_not_carry",
                   f"{_capitalised(courts)} would not sign these terms as they stand, "
                   f"Sire — revise them at the table.",
                   who_must_consent=tuple(live))
    return _ok(who_must_consent=tuple(live))


# ═══════════════════════════════════════════════════════════════════════════
# (c) The ally's petition
# ═══════════════════════════════════════════════════════════════════════════

def _ally_petition_verdict(world, dialogue: Dict[str, Any], action: Optional[str]) -> Verdict:
    from backend.game_logic import settlement_offers as SO
    war_id = str(dialogue.get("war_id") or "")
    ally = str(dialogue.get("ally_nation") or "")
    war = (getattr(world, "war_instances", {}) or {}).get(war_id)
    # A closed TABLE disables the Grant with its reason but does not CLOSE
    # it by marker (`closes=False`): the handler's own refusal road ROUTES
    # the player to the table it names (SR-2a's `must_reopen`), which a
    # press should still reach — the typed and the button roads answer the
    # same words either way (R3-7A).
    if not (isinstance(war, dict) and war.get("ended_turn") is None):
        return _no("war_over", "The war this petition was filed against has ended.",
                   target=ally, closes=False)
    mounted = SO._mounted_propose_settlement_dialogue(world, war_id)
    draft = SO._suspended_draft_for_war(world, war_id)
    if draft is None:
        if mounted is not None:
            # The editor is the CURRENT hard stop: the petition behind it
            # cannot be made current until the editor is suspended (the
            # draft kept), which is the player's one road to it — the
            # handler's mounted arm is reachable by no answer seam.
            return _no("editor_mounted",
                       f"Back out of the settlement editor for "
                       f"{SO._war_label_for_id(world, war_id)} first — the draft is "
                       f"kept — then answer the petition.",
                       target=ally, closes=False)
        return _no("petition_table_closed", SO._petition_table_closed_display(world, war_id),
                   target=ally, closes=False)
    if action == SO.ALLY_SETTLEMENT_PETITION_HONOR_ACTION:
        return _ok(target=ally)
    clause = dialogue.get("candidate_clause")
    if not isinstance(clause, dict):
        return _ok(target=ally)
    terms = [dict(t) for t in draft if isinstance(t, dict)]
    covered = SO._default_coverage_for_war(world, war_id)
    if not SO._petition_clause_prevalidates(world, clause, settlement_terms=terms,
                                            covered_enemy_participants=covered):
        return _no("petition_clause_stale",
                   f"The draft has moved on — {_court(world, ally)}'s ask can no longer "
                   f"be granted as petitioned.",
                   target=ally, who_must_consent=tuple(covered))
    return _ok(target=ally, who_must_consent=tuple(covered))


# ═══════════════════════════════════════════════════════════════════════════
# (d) The client's petition
# ═══════════════════════════════════════════════════════════════════════════

def _client_petition_verdict(world, dialogue: Dict[str, Any]) -> Verdict:
    from backend.game_logic.vassal import _grant_verdict
    context = dialogue.get("context") if isinstance(dialogue.get("context"), dict) else {}
    terms = context.get("proposal") if isinstance(context.get("proposal"), dict) else {}
    if not terms and "petition" in dialogue:
        terms = dialogue
    petition = terms.get("petition") if isinstance(terms.get("petition"), dict) else {}
    lord = str(terms.get("target_nation") or getattr(world, "player_nation", "France"))
    vassal = str(terms.get("proposer_nation") or context.get("source_nation")
                 or dialogue.get("target_nation") or petition.get("vassal") or "")
    kind, message = _grant_verdict(world, lord, vassal, petition)
    if kind == "ok":
        return _ok(target=vassal)
    # `petition_grant_availability`'s rule: the press ENDS the petition for
    # every kind but `stands` (the lord cannot pay, or gave the province
    # elsewhere by his own hand), whose Grant bounces and the petition
    # waits for the turn's end. A standing Grant is refused with its words
    # but NOT closed — the handler's own road must run (IQ7-RV2).
    if kind == "stands":
        return _no("stands", message, target=vassal, closes=False)
    return Verdict(True, clause=kind, message=message, target=vassal)


# ═══════════════════════════════════════════════════════════════════════════
# The verdict, and its stamp
# ═══════════════════════════════════════════════════════════════════════════

def can_sign(world, letter: Dict[str, Any], *, action: Optional[str] = None,
             at_send: bool = False) -> Verdict:
    """THE verdict: would the ratifier sign this letter today?

    `letter` is a treaty letter (the ratifier's proposal dict, or an
    `incoming_proposal` / counter dialogue carrying one), a settlement offer
    (the `incoming_settlement_offer` dialogue or the producer's draft), an
    ally's petition dialogue or a client's. `action` names the option asked
    about (an ally petition's Honor arm reads only the table). `at_send`
    adds the send road's own paradox gate for a player's outgoing peace —
    the chips, the counsel and the Congress describe SENDING; the ratifier
    does not pass it."""
    kind = _letter_kind(letter)
    if kind == "settlement":
        return _settlement_verdict(world, letter)
    if kind == "ally_petition":
        return _ally_petition_verdict(world, letter, action)
    if kind == "client_petition":
        return _client_petition_verdict(world, letter)
    if kind == "treaty":
        proposal = proposal_of(letter, str(getattr(world, "player_nation", "France") or ""))
        if not proposal:
            return _ok()
        if str(proposal.get("type") or "") == "call_to_arms":
            return _call_to_arms_verdict(world, proposal)
        return _treaty_verdict(world, proposal, at_send=at_send)
    return _ok()


def _call_to_arms_verdict(world, proposal: Dict[str, Any]) -> Verdict:
    """DDB-2: an ally's call to arms is not a treaty — Join is open while the
    call is live; a moot or barred call's Join ENDS the letter with its word
    (no price), never a dead button."""
    from backend.game_logic.call_to_arms import call_status
    ally = str(proposal.get("proposer_nation") or "")
    status, why = call_status(world, proposal)
    if status == "live":
        return _ok(target=ally)
    return _ok(message=f"Nothing to join — {why}.", target=ally)


def stamp_option(option: Dict[str, Any], verdict: Verdict) -> Dict[str, Any]:
    """Write ONE verdict into an option under every key its readers use:
    `enabled` + `reason` (the client petition's popup, the driver, the
    sweep), `available` + `disabled_reason_display` (the ally petition's
    popup, the wizard's rows), and the `closed_clause` marker the answer
    seam refuses by. A verdict that says yes clears all of them."""
    if not isinstance(option, dict):
        return option
    closed = (not verdict.ok) and verdict.closes
    if verdict.ok and not verdict.message:
        option["enabled"] = True
        option["reason"] = ""
        option["available"] = True
        option.pop("disabled_reason_display", None)
        option.pop(CLOSED_CLAUSE_KEY, None)
        return option
    option["enabled"] = bool(verdict.ok)
    option["reason"] = str(verdict.message or "")
    option["available"] = bool(verdict.ok)
    if verdict.ok:
        # A press that ENDS the letter with a word (a fulfilled or a moot
        # petition): enabled, with its sentence beside it.
        option.pop("disabled_reason_display", None)
        option.pop(CLOSED_CLAUSE_KEY, None)
    else:
        option["disabled_reason_display"] = str(verdict.message or "")
        if closed:
            option[CLOSED_CLAUSE_KEY] = str(verdict.clause or "closed")
        else:
            option.pop(CLOSED_CLAUSE_KEY, None)
    return option


def stamp_letter(world, dialogue: Dict[str, Any]) -> Optional[Verdict]:
    """Stamp every accept-shaped option of a letter from one `can_sign` read
    (one read per distinct action). Returns the verdict of the first
    accept-shaped option, or None when the letter carries none."""
    if not isinstance(dialogue, dict):
        return None
    first: Optional[Verdict] = None
    verdicts: Dict[str, Verdict] = {}
    for option in dialogue.get("options") or []:
        if not isinstance(option, dict):
            continue
        action = str(option.get("action") or "")
        if action not in ACCEPT_ACTIONS:
            continue
        if action not in verdicts:
            verdicts[action] = can_sign(world, dialogue, action=action)
        stamp_option(option, verdicts[action])
        if first is None:
            first = verdicts[action]
    return first


def _mirror_options(dialogue: Dict[str, Any], payload: Dict[str, Any]) -> None:
    """The popup payload's `options` mirror — the keys the popups read. A
    payload that already carries its own option set (a settlement offer's
    rebuilt popup) keeps it, each row stamped from the dialogue's option of
    the same action; a payload without one gets the dialogue's mirror. A
    dialogue with no options writes nothing."""
    stamped: Dict[str, Dict[str, Any]] = {}
    for option in dialogue.get("options") or []:
        if not isinstance(option, dict):
            continue
        row = {"label": str(option.get("label") or ""),
               "action": str(option.get("action") or ""),
               "enabled": option.get("enabled", True) is not False,
               "reason": str(option.get("reason") or "")}
        if option.get("available") is False:
            row["available"] = False
            row["disabled_reason_display"] = str(option.get("disabled_reason_display") or "")
        if option.get(CLOSED_CLAUSE_KEY):
            row[CLOSED_CLAUSE_KEY] = option[CLOSED_CLAUSE_KEY]
        stamped[row["action"]] = row
    if not stamped:
        return
    existing = payload.get("options")
    if isinstance(existing, list) and existing:
        for row in existing:
            if not isinstance(row, dict):
                continue
            source = stamped.get(str(row.get("action") or ""))
            if source is None:
                continue
            for key in ("enabled", "reason", "available", "disabled_reason_display", CLOSED_CLAUSE_KEY):
                if key in source:
                    row[key] = source[key]
                elif key in ("available", "disabled_reason_display", CLOSED_CLAUSE_KEY):
                    row.pop(key, None)
        return
    payload["options"] = list(stamped.values())


def refresh_letter_verdict(world, dialogue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """The read seam for a TREATY or SETTLEMENT letter: re-stamp its accept
    option from the live board and mirror the stamp into its `popup_payload`
    (`options`, the keys `incoming_proposal_popup.gd` reads). The petitions
    keep their own refreshers (`refresh_client_petition_dialogue`,
    `refresh_ally_petition_availability`), which stamp through the same
    `stamp_option`. Returns the refreshed popup payload, or None when the
    letter is not one of the two."""
    if _letter_kind(dialogue) not in ("treaty", "settlement"):
        return None
    stamp_letter(world, dialogue)
    payload = dialogue.get("popup_payload")
    # DDB-4 (S13b): a peace letter's war score and its preview are re-read
    # from the board at every read, never the snapshot of its arrival.
    if (_letter_kind(dialogue) == "treaty" and isinstance(payload, dict)
            and payload.get("war_context_snapshot") is not None):
        context = dialogue.get("context") if isinstance(dialogue.get("context"), dict) else {}
        terms = (context or {}).get("counter_terms") or (context or {}).get("proposal") or {}
        source = str((context or {}).get("source_nation") or dialogue.get("target_nation") or "")
        if terms and source:
            from backend.game_logic.mailbox_payloads import attach_peace_preview
            attach_peace_preview(world, payload, source, terms)
    if isinstance(payload, dict) and payload:
        _mirror_options(dialogue, payload)
        return payload
    return None


def refusal_dict(verdict: Verdict, fallback_target: str = "") -> Dict[str, Any]:
    """The ratifier's refusal dict — byte-identical to the one it has
    always returned, plus the clause for the log and the tests."""
    return {
        "type": "diplomatic_treaty_failed",
        "target": verdict.target or fallback_target,
        "message": verdict.message,
        "clause": verdict.clause,
    }


def names_a_raw_code(text: str) -> bool:
    """True when a player-facing sentence carries a snake_case engine key —
    the sweep's own `_RAW_CODE_RX`, kept here for the pins."""
    import re
    return bool(re.search(r"\b[a-z]+(?:_[a-z]+){2,}\b", str(text or "")))


def iter_accept_options(dialogue: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    for option in dialogue.get("options") or []:
        if isinstance(option, dict) and str(option.get("action") or "") in ACCEPT_ACTIONS:
            yield option


# ═══════════════════════════════════════════════════════════════════════════
# (e) The ask-back — DD-1 S8 Step 3 "the verbs", SFR-D42 (October 12, 2026)
#
# A liberated home province held by an ally (the ally walked in as a
# liberator and the capture road gave it the keys) could be asked back by no
# verb — `Talleyrand, ask Spain to give back Provence` was shrugged at. ONE
# verdict, read by the chip under the ally's card, the typed road and the
# AI's own ask-back tick (GR5): `can_ask_return` says whether the ask can be
# MADE (the clause in words when it cannot), `ask_return_score` is the
# court's answer — the acceptance formula for a return: the relation between
# the courts, the ally fighting beside us, the province's worth, and the
# road by which the ally came to hold it. The act (`diplomacy.
# ask_return_province`) reads both; nothing else re-derives either.
# ═══════════════════════════════════════════════════════════════════════════

ASK_RETURN_ACCEPT_AT = 40      # the ally hands the province back at this score
ASK_RETURN_DP_COST = 1         # the ask, delivered, is 1 DP (the D5 instruments' price)
ASK_RETURN_BESIDE_US = 25      # the ally stands in a war with us against a common enemy
ASK_RETURN_LIBERATOR = 15      # the ally took it from OUR enemy (the liberator's road)
ASK_RETURN_TOOK_IT_FROM_US = -40   # the ally took it from us (an old quarrel, since healed)
ASK_RETURN_CAPITAL_WORTH = 20  # a capital weighs this much more than its income says
ALLY_STATES = ("ALLIANCE", "DEFENSIVE_ALLIANCE")


def home_provinces_held_by(world, owner: str, holder: str) -> List[str]:
    """`owner`'s home provinces (its `nation_starting_regions`) that `holder`
    controls today — the provinces an ask-back can name. Sorted, so the
    chips and the AI tick walk them in one order."""
    if not owner or not holder or owner == holder:
        return []
    homes = (getattr(world, "nation_starting_regions", {}) or {}).get(owner, []) or []
    out: List[str] = []
    for name in homes:
        region = world.regions.get(name)
        if region is not None and getattr(region, "controller", None) == holder:
            out.append(name)
    return sorted(out)


def _common_enemy(world, asker: str, holder: str) -> str:
    """A court at WAR with both `asker` and `holder` — the war the ally
    fights beside us. Empty when there is none."""
    for other in world.get_active_nations():
        if other in (asker, holder):
            continue
        if world.is_at_war(asker, other) and world.is_at_war(holder, other):
            return other
    return ""


def ask_return_score(world, asker: str, holder: str, region: str) -> Dict[str, Any]:
    """The court's answer to an ask-back, as a score against
    ASK_RETURN_ACCEPT_AT: relations between the courts, +25 when the holder
    fights beside the asker, the province's worth against it (income // 10,
    a capital +20 more), +15 when the holder took it from the asker's enemy
    (the liberator's road), −40 when it took it from the asker. Deterministic
    (GR6); every term rides `components` for the chip and the pins."""
    key = world._make_diplo_key(asker, holder)
    relation = int((getattr(world, "nation_relations", {}) or {}).get(key, 0) or 0)
    beside = _common_enemy(world, asker, holder)
    region_obj = world.regions.get(region)
    income = int(getattr(region_obj, "income_value", 0) or 0) if region_obj is not None else 0
    worth = income // 10
    if region_obj is not None and getattr(region_obj, "is_capital", False):
        worth += ASK_RETURN_CAPITAL_WORTH
    road = 0
    road_name = "unknown"
    title = ((getattr(world, "province_title", {}) or {}).get(region) or {})
    taken_from = str(title.get("from") or "")
    if taken_from == asker:
        road, road_name = ASK_RETURN_TOOK_IT_FROM_US, "taken_from_us"
    elif taken_from:
        road, road_name = ASK_RETURN_LIBERATOR, "liberated"
    score = relation + (ASK_RETURN_BESIDE_US if beside else 0) - worth + road
    return {
        "score": int(score),
        "accepts": bool(score >= ASK_RETURN_ACCEPT_AT),
        "shortfall": int(max(0, ASK_RETURN_ACCEPT_AT - score)),
        "components": {
            "relation": int(relation),
            "beside_us": int(ASK_RETURN_BESIDE_US if beside else 0),
            "common_enemy": beside,
            "worth": int(-worth),
            "road": int(road),
            "road_name": road_name,
        },
    }


def can_ask_return(world, asker: str, holder: str, region: str, *,
                   charge: bool = True) -> Verdict:
    """Can `asker` ASK `holder` for `region` back today? The clause in words
    when not: the province unknown or not ours, not held by that court, the
    court no ally of ours, the court's own war purpose on it, no DP left
    (the player only — an AI court's pool is `nation_dp`, read by the act).
    `price` is the relation shortfall the court would still want; `target`
    the court the chip and the refusal name."""
    holder_name = _court(world, holder, capitalize=True) if holder else "that court"
    region = str(region or "").strip()
    if not region:
        held = home_provinces_held_by(world, asker, holder)
        if held:
            return _no("no_province",
                       f"Which province shall I ask {holder_name} to return, Sire? "
                       f"{holder_name} holds {', '.join(held)} of ours.",
                       target=holder)
        return _no("no_province",
                   f"Which province, Sire? {holder_name} holds none of our home soil.",
                   target=holder)
    region_obj = world.regions.get(region)
    if region_obj is None:
        return _no("unknown_province",
                   f"I know no province called '{region}', Sire.", target=holder)
    homes = (getattr(world, "nation_starting_regions", {}) or {}).get(asker, []) or []
    if region not in homes:
        return _no("not_our_soil",
                   f"{region} was never {_court(world, asker, capitalize=True)}'s own soil, "
                   f"Sire — only a home province can be asked back; the rest is taken "
                   f"or signed for.",
                   target=holder)
    controller = str(getattr(region_obj, "controller", "") or "")
    if controller == asker:
        return _no("already_ours", f"{region} is ours already, Sire.", target=holder)
    if controller != holder:
        who = _court(world, controller, capitalize=True) if controller else "no court"
        return _no("not_held",
                   f"{holder_name} does not hold {region}, Sire — {who} does.",
                   target=holder)
    state = str(world.get_diplomatic_state(asker, holder) or "PEACE")
    if state not in ALLY_STATES:
        pretty = state.replace("_", " ").lower()
        return _no("not_an_ally",
                   f"{holder_name} is no ally of ours (we stand at {pretty}), Sire — a "
                   f"province is asked back from a friend; from anyone else it is "
                   f"taken, or signed for at the table.",
                   target=holder)
    # The holder's own live war purpose names it: it will not hear of it.
    key = world._make_diplo_key(asker, holder)
    for pair_key, by_nation in (getattr(world, "war_objectives", {}) or {}).items():
        obj = (by_nation or {}).get(holder) if isinstance(by_nation, dict) else None
        if not isinstance(obj, dict) or obj.get("concluded_turn") is not None:
            continue
        if region in (obj.get("target_regions") or []):
            return _no("war_purpose",
                       f"{holder_name} took {region} by its own war purpose and will "
                       f"not hear of giving it up, Sire.",
                       target=holder)
    del key
    if charge and asker == getattr(world, "player_nation", "France"):
        dp = int(getattr(world, "diplomatic_points", 0) or 0)
        if dp < ASK_RETURN_DP_COST:
            return _no("no_dp",
                       f"Talleyrand has no diplomatic points left this season, Sire — "
                       f"the ask to {holder_name} waits for the next.",
                       target=holder)
    answer = ask_return_score(world, asker, holder, region)
    return _ok(price=int(answer["shortfall"]), target=holder)


def ask_return_words(world, asker: str, holder: str, region: str,
                     answer: Dict[str, Any]) -> str:
    """The court's answer in the envoy's words — the grant, or the refusal
    naming what it would still take (never a code)."""
    holder_name = _court(world, holder, capitalize=True)
    comp = answer.get("components") or {}
    if answer.get("accepts"):
        beside = comp.get("common_enemy") or ""
        why = (f"she fights beside us against {_court(world, beside, capitalize=True)} "
               f"and will not quarrel over liberated soil" if beside
               else "the friendship is worth more to her than the province")
        return (f"{holder_name} hands {region} back to us — {why}. "
                f"The liberated soil comes home.")
    shortfall = int(answer.get("shortfall") or 0)
    relation = int(comp.get("relation") or 0)
    bits = []
    if int(comp.get("worth") or 0) < 0:
        bits.append(f"{region} is worth {-int(comp.get('worth'))} to her")
    if comp.get("road_name") == "taken_from_us":
        bits.append("she took it from us herself")
    if not comp.get("common_enemy"):
        bits.append("she fights no war beside ours")
    tail = f" ({'; '.join(bits)})" if bits else ""
    return (f"{holder_name} declines to part with {region}, Sire — our standing "
            f"with her is {relation}, and she would want {shortfall} more{tail}. "
            f"Warm the court, or stand beside her in a war, and ask again.")
