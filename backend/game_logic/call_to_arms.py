"""The call to arms — DDB-2, "France is asked" (DDB-D8's ruling; Pre-Deploy
S13b part 1, October 14, 2026; `docs/audits/DD_B_RULINGS_2026_10_14.md` §2).

A full alliance used to carry France into its ally's OFFENSIVE war without a
word: the cascade's resolver decided for the player ("honored"), so the
diplomacy-first player woke at war with Hanover one turn after the general
peace, with no road out (`not_side_leader`). Every spec had asked for the
choice — DG-4 "honor or refuse", WAR_BARGAIN "a player-visible ally-entry
decision", AI_INTENT §17 "the player is never auto-conscripted" — and only
the AI's half was ever built.

The rule, for the player as callee only:

* **The letter.** An ally's offensive war posts a letter on the
  incoming-proposal transport (the broker-ask idiom), proposal type
  `call_to_arms`, carrying the ally, the enemy and the ally's war-instance id:
  "Prussia calls on her ally to join her war on Hanover — join, or refuse at
  a price …; unanswered in two turns, it is refused". Join / Refuse, no
  Counter.
* **Join** is the cascade's honored path (`diplomacy._enter_offensive_war`):
  the pair attached to the ally's war instance (entry path `call_accepted`),
  WAR by `offensive_cascade_accepted`, −20 with the enemy, the Congress's
  `note_joined`, the war-entry bargains — France chose to draw.
* **Refuse** is the existing offensive-refusal episode
  (`emit_call_to_arms_refused_offensive`): reliability, a betrayal strike on
  the ally's ledger, every witness's relation.
* **Unanswered** for `GUARANTEE_GRACE_TURNS` (2), it lapses as a refusal at
  the same price (`turn_manager`'s lapse hook).
* **The exit.** A pair France entered at an ally's call is marked on the war
  instance (`entry_path == "call_accepted"`); for it the alliance-paradox
  HARD_STOP on a bilateral peace is lifted and the separate-peace penalty
  prices it (`diplomacy.get_peace_commitment_conflicts`), and the Cabinet
  offers the bilateral peace past `not_side_leader`.

Unchanged: an AI ally of an AI aggressor (the DG-4 resolver), the defensive
call (expected), the League's suppression, and an explicit ally-entry
decision the player bargained for. The rule's one seam is `asks_the_callee`
(read by the cascade and by the war preview); the series attribution
(`tools/_ddb_s13b_series_arms.py`) patches it in its child — no module lever
(the code-health ratchet).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from backend.errors import report

CALL_TO_ARMS_TYPE = "call_to_arms"
CALL_ACCEPTED_PATH = "call_accepted"
CALL_ACCEPTED_REASON = "offensive_cascade_accepted"
CALL_PRIORITY = 9


def _grace_turns() -> int:
    from backend.game_logic.instruments import GUARANTEE_GRACE_TURNS
    return int(GUARANTEE_GRACE_TURNS)


def _shown(world, nation: str, *, capitalize: bool = False) -> str:
    from backend.display_names import with_definite_article
    from backend.game_logic.formations import formed_display_name
    return with_definite_article(formed_display_name(world, nation) if nation else "a court",
                                 capitalize=capitalize)


# ═══════════════════════ reads (pure) ═══════════════════════

def asks_the_callee(world, callee: str, entry_decision: Optional[Dict] = None) -> bool:
    """THE rule's seam: an ally's offensive war ASKS this callee (a letter)
    instead of carrying it in — the player, with no ally-entry decision of
    her own already struck."""
    return (not entry_decision
            and bool(callee) and callee == getattr(world, "player_nation", None))


def refusal_price(world, callee: str, ally: str, target: str) -> Dict[str, int]:
    """What refusing costs — the SAME scaled deltas the refusal episode
    applies (`emit_call_to_arms_refused_offensive`), quoted on the letter."""
    from backend.game_logic import diplomacy as D
    context = {"side": "attacker", "caller": ally, "callee": callee, "enemy": target}
    try:
        reliability = int(D._scaled_dg4_delta(
            world, callee, D.DG4_EVENT_REFUSED_OFFENSIVE, "reliability_delta",
            call_context=context))
        witness = int(D._scaled_dg4_delta(
            world, callee, D.DG4_EVENT_REFUSED_OFFENSIVE, "witness_relation_delta",
            call_context=context))
    except Exception as exc:
        report(exc, "call_to_arms.refusal_price: _scaled_dg4_delta")
        reliability, witness = 0, 0
    return {"reliability_delta": reliability, "witness_relation_delta": witness}


def is_call_to_arms(letter: Optional[Dict]) -> bool:
    """A dialogue (or its terms) that is an ally's call to arms."""
    if not isinstance(letter, dict):
        return False
    context = letter.get("context") if isinstance(letter.get("context"), dict) else {}
    terms = (context or {}).get("proposal") if context else letter
    return (str((context or {}).get("proposal_type") or "") == CALL_TO_ARMS_TYPE
            or str((terms or {}).get("type") or "") == CALL_TO_ARMS_TYPE)


def call_terms_of(dialogue: Dict) -> Dict:
    context = dialogue.get("context") if isinstance(dialogue.get("context"), dict) else {}
    return dict((context or {}).get("proposal") or {})


def answer_by_turn(terms: Dict) -> int:
    return int(terms.get("answer_by_turn") or (int(terms.get("issued_turn") or 0) + _grace_turns()))


def keeps_open(dialogue: Dict, current_turn: int) -> bool:
    """Read by the lapse (`dialogue_manager.lapse_pending_offers`): a call to
    arms stands until the end of its answer-by turn — two turns, not one."""
    if not is_call_to_arms(dialogue):
        return False
    return int(current_turn) < answer_by_turn(call_terms_of(dialogue))


def call_status(world, terms: Dict) -> Tuple[str, str]:
    """('live', '') | ('moot', why) | ('barred', why) — read at every answer.

    Moot: the ally's war on the enemy is over, a court is gone, or France is
    already at war with the enemy. Barred: the offensive call's own bar now
    holds (a fresh peace, a pair cooldown, the sitting Congress). Neither is
    priced — the court was never free to be called (RS-1)."""
    ally = str(terms.get("proposer_nation") or "")
    callee = str(terms.get("target_nation") or getattr(world, "player_nation", "France"))
    enemy = str(terms.get("enemy") or "")
    active = set(world.get_active_nations() or [])
    if not ally or not enemy or ally not in active or enemy not in active:
        return "moot", "the war it called France to has no court left to fight"
    if not world.is_at_war(ally, enemy):
        return "moot", f"{_shown(world, ally, capitalize=True)} is no longer at war with {_shown(world, enemy)}"
    if world.is_at_war(callee, enemy):
        return "moot", f"France is already at war with {_shown(world, enemy)}"
    if world.get_diplomatic_state(callee, ally) != "ALLIANCE":
        return "moot", f"the alliance with {_shown(world, ally)} no longer stands"
    from backend.game_logic.diplomacy import offensive_call_bar
    bar = offensive_call_bar(world, callee, enemy)
    if bar:
        return "barred", bar
    return "live", ""


def entered_by_call(world, nation_a: str, nation_b: str) -> bool:
    """Whether the pair's war was entered at an ally's call (Join) — the mark
    the exit reads (the war instance's per-pair `entry_path`)."""
    if not nation_a or not nation_b:
        return False
    from backend.game_logic.settlement_helpers import (
        _find_active_war_instance_for_pair, _make_pair_key,
    )
    pair = _make_pair_key(nation_a, nation_b)
    war_id = _find_active_war_instance_for_pair(world, pair)
    if not war_id:
        return False
    meta = (((getattr(world, "war_instances", {}) or {}).get(war_id) or {})
            .get("diplo_key_meta") or {}).get(pair) or {}
    return str(meta.get("entry_path") or "") == CALL_ACCEPTED_PATH


def letter_lines(world, terms: Dict) -> List[str]:
    """The letter's words — one source for the dialogue, the popup and the
    rail. The price is the refusal episode's own figures."""
    ally = str(terms.get("proposer_nation") or "")
    enemy = str(terms.get("enemy") or "")
    reliability = int(terms.get("reliability_delta") or 0)
    witness = int(terms.get("witness_relation_delta") or 0)
    head = (f"{_shown(world, ally, capitalize=True)} calls on her ally to join "
            f"her war on {_shown(world, enemy)} — join, or refuse at a price: "
            f"reliability {reliability:+d}, relations {witness:+d} with every "
            f"witness; unanswered in two turns, it is refused.")
    lines = [head,
             f"Join: France goes to war with {_shown(world, enemy)} beside "
             f"{_shown(world, ally)} (relations with {_shown(world, enemy)} −20); "
             f"a separate peace stays open to France, at the price a separate "
             f"peace costs an ally.",
             f"Refuse: {_shown(world, ally, capitalize=True)} remembers it "
             f"(a strike on the alliance's ledger); France stays at peace.",
             f"Answer by the end of turn {answer_by_turn(terms)}."]
    return lines


# ═══════════════════════ the letter ═══════════════════════

def post_call(world, *, ally: str, target: str, callee: str, war_id: str,
              root_episode_id: str = "") -> Optional[Dict]:
    """Post the call to arms (the cascade's player arm). One letter per
    (ally, enemy) while one stands."""
    from backend.game_logic.ai_diplomacy import _make_proposal, deliver_ai_proposal
    dm = getattr(world, "dialogue_manager", None)
    if dm is not None:
        for standing in [dm.peek()] + list(dm.iter_queue()):
            if is_call_to_arms(standing):
                t = call_terms_of(standing)
                if t.get("proposer_nation") == ally and t.get("enemy") == target:
                    return None
    turn = int(getattr(world, "current_turn", 0) or 0)
    price = refusal_price(world, callee, ally, target)
    terms = {
        "type": CALL_TO_ARMS_TYPE,
        "proposer_nation": ally,
        "target_nation": callee,
        "enemy": target,
        "war_id": str(war_id or ""),
        "issued_turn": turn,
        "answer_by_turn": turn + _grace_turns(),
        "root_episode_id": str(root_episode_id or ""),
        "sweeteners": [],
        "demands": [],
        "clauses": [],
        **price,
    }
    proposal = _make_proposal(ally, CALL_TO_ARMS_TYPE, CALL_PRIORITY, terms, world)
    # The arrival is logged by the transport (`proposal_arrived`, its label
    # "Call to Arms") — the campaign log's own row for every letter.
    return deliver_ai_proposal(proposal, world)


def build_call_dialogue(proposal: Dict, world) -> Dict:
    """The letter as an `incoming_proposal` dialogue in its own register:
    Join / Refuse, no Counter (a call is answered, never bargained)."""
    from backend.game_logic.mailbox_payloads import build_pending_envoy_popup_from_terms
    nation = proposal["source"]
    terms = proposal["terms"]
    lines = letter_lines(world, terms)
    diplomats = getattr(world, "diplomats", {}) or {}
    diplomat = diplomats.get(nation)
    diplomat_name = diplomat.name if diplomat else f"the envoy of {_shown(world, nation)}"
    payload = build_pending_envoy_popup_from_terms(
        world, nation=nation, terms=terms, assessment="",
        decision_reason=proposal.get("decision_reason", ""))
    payload["is_call_to_arms"] = True
    payload["clauses"] = list(lines)
    payload["talleyrand_assessment"] = (
        "Talleyrand: \"An ally's war is the ally's design, Sire — join it and "
        "it is ours; refuse it and the alliance remembers.\"")
    payload["answer_by_turn"] = answer_by_turn(terms)
    payload["choice_display"] = dict(payload.get("choice_display") or {},
                                     accept="joined", reject="refused")
    body = "\n".join(f"  {line}" for line in lines)
    dialogue = {
        "type": "incoming_proposal",
        "target_nation": nation,
        "talleyrand_text": (f"Sire, {diplomat_name} brings a call to arms.\n\n{body}"),
        "options": [
            {"label": "Join the war",
             "description": lines[1],
             "action": "accept_ai_proposal"},
            {"label": "Refuse the call",
             "description": lines[2],
             "action": "reject_ai_proposal"},
        ],
        "context": {
            "proposal": terms,
            "source_nation": nation,
            "acceptance_score": 0,
            "decision_reason": proposal.get("decision_reason", ""),
            "proposal_type": CALL_TO_ARMS_TYPE,
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
        "popup_payload": payload,
    }
    # The Join is stamped from the ONE verdict (`treaty._call_to_arms_verdict`)
    # at build and re-stamped at every read seam, as every letter is.
    from backend.game_logic.treaty import refresh_letter_verdict
    refresh_letter_verdict(world, dialogue)
    return dialogue


# ═══════════════════════ the answers ═══════════════════════

def _close_letter_notice(world) -> None:
    from backend.notifications import DIPLOMATIC_PROPOSAL
    world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)


def join_call(world, terms: Dict) -> Dict:
    """Join — the cascade's honored path, France's own choice."""
    from backend.game_logic import diplomacy as D
    from backend.game_logic.settlement_helpers import (
        _find_active_war_instance_for_pair, _make_pair_key, attach_pair_to_war_instance,
    )
    ally = str(terms.get("proposer_nation") or "")
    callee = str(terms.get("target_nation") or world.player_nation)
    enemy = str(terms.get("enemy") or "")
    status, why = call_status(world, terms)
    if status != "live":
        return {"joined": False, "status": status,
                "message": (f"There is nothing to join, Sire — {why}. "
                            f"The call lapses at no cost.")}
    war_id = str(terms.get("war_id") or "")
    instance = (getattr(world, "war_instances", {}) or {}).get(war_id)
    if not war_id or not isinstance(instance, dict) or instance.get("ended_turn") is not None:
        war_id = _find_active_war_instance_for_pair(world, _make_pair_key(ally, enemy)) or ""

    def _attach(attacker: str, defender: str, entry_path: str) -> Dict:
        if not war_id:
            return {"ok": True, "war_id": ""}
        return attach_pair_to_war_instance(world, war_id, attacker, defender,
                                           entry_path=entry_path)

    entries: List[Dict] = []
    entered = D._enter_offensive_war(
        world,
        nation=callee,
        aggressor=ally,
        target=enemy,
        attach=_attach,
        entry_path=CALL_ACCEPTED_PATH,
        state_reason=CALL_ACCEPTED_REASON,
        ledger_path=CALL_ACCEPTED_PATH,
        reason=f"France answered {ally}'s call to arms",
        treaty_state=world.get_diplomatic_state(callee, ally),
        war_entry_entries=entries,
        fault_aggressor=ally,
        root_episode_id=str(terms.get("root_episode_id") or "") or None,
        resolution_path="offensive_call_accepted",
    )
    if entered is None:
        return {"joined": False, "status": "blocked",
                "message": (f"The chancery finds no lawful road into "
                            f"{_shown(world, ally)}'s war today, Sire — the call "
                            f"lapses at no cost.")}
    world.log_event({
        "type": "war_entry_ledger",
        "episode_id": str(terms.get("root_episode_id") or ""),
        "war_id": war_id,
        "aggressor": ally,
        "target": enemy,
        "entries": entries,
        "turn": int(world.current_turn),
    })
    return {"joined": True, "status": "joined", "war_id": war_id,
            "message": (f"France joins {_shown(world, ally)}'s war on "
                        f"{_shown(world, enemy)}, Sire — we are at war with "
                        f"{_shown(world, enemy)}. A separate peace stays open "
                        f"to us, at the price a separate peace costs an ally.")}


def refuse_call(world, terms: Dict, *, how: str = "refused") -> Dict:
    """Refuse (or the two-turn lapse) — the existing offensive-refusal
    episode, at the price the letter quoted. A moot or barred call costs
    nothing."""
    from backend.game_logic.diplomacy import emit_call_to_arms_refused_offensive
    ally = str(terms.get("proposer_nation") or "")
    callee = str(terms.get("target_nation") or world.player_nation)
    enemy = str(terms.get("enemy") or "")
    status, why = call_status(world, terms)
    lapse = how == "unanswered"
    if status != "live":
        return {"refused": False, "status": status, "penalty": False,
                "message": (f"{_shown(world, ally, capitalize=True)}'s call "
                            f"{'lapses' if lapse else 'is set aside'} at no cost — {why}.")}
    context = {"side": "attacker", "caller": ally, "callee": callee, "enemy": enemy,
               "path": "refused_discretionary",
               "reason": ("call unanswered" if lapse else "France refused the call"),
               "how": how}
    episode = emit_call_to_arms_refused_offensive(
        world, breaker=callee, victim=ally, call_context=context)
    rel_before = int(episode.get("reliability_before", 0) or 0)
    rel_after = int(episode.get("reliability_after", 0) or 0)
    witness = int(episode.get("witness_relation_delta", 0) or 0)
    opener = ("Two turns passed unanswered: " if lapse else "")
    message = (f"{opener}France refuses {_shown(world, ally)}'s call to arms against "
               f"{_shown(world, enemy)}. Reliability {rel_before} → {rel_after}; "
               f"{int(episode.get('witness_count', 0) or 0)} witnessing court"
               f"{'' if int(episode.get('witness_count', 0) or 0) == 1 else 's'} "
               f"{witness:+d}; {_shown(world, ally)} remembers it.")
    return {"refused": True, "status": "refused", "penalty": True,
            "episode_id": episode.get("episode_id", ""),
            "reliability_before": rel_before, "reliability_after": rel_after,
            "message": message}


def refuse_lapsed_letter(world, letter: Dict) -> Dict:
    """The two-turn lapse (`dialogue_manager.lapse_pending_offers`, given the
    world): a call to arms the lapse removes is refused at the same price;
    returns the key the lapse row carries (`{}` for any other letter)."""
    if not is_call_to_arms(letter):
        return {}
    terms = call_terms_of(letter)
    result = refuse_call(world, terms, how="unanswered")
    return {"call_to_arms": {"enemy": str(terms.get("enemy") or ""),
                             "penalty": bool(result.get("penalty")),
                             "message": str(result.get("message") or "")}}


# ═══════════════════════ legibility: the alliance's terms ═══════════════════

def ally_design_lines(world, ally: str) -> List[str]:
    """"<ally>'s design: <design> on <court>" — the live design an alliance
    binds France beside (diplomacy has no fog)."""
    try:
        from backend.game_logic.agendas import (
            _controlled_by_self_or_vassal, _hegemon, _region_controller, get_active_agenda,
        )
        view = get_active_agenda(ally, world)
    except Exception as exc:
        report(exc, "call_to_arms.ally_design_lines: get_active_agenda")
        return []
    if view is None or getattr(view, "survival", False):
        return []
    courts: List[str] = []
    if view.type == "acquire_regions":
        for region in view.regions:
            if _controlled_by_self_or_vassal(world, ally, region):
                continue
            holder = _region_controller(world, region)
            if holder and holder != ally and holder not in courts:
                courts.append(holder)
    elif view.type in ("deny_regions", "contain_hegemon"):
        hegemon, _share = _hegemon(world, ally)
        if hegemon and hegemon != ally:
            courts.append(hegemon)
    if not courts:
        return []
    title = str(view.title or "a design")
    on = ", ".join(_shown(world, c) for c in courts)
    return [f"{_shown(world, ally, capitalize=True)}'s design: {title} on {on}"]


def alliance_binding_lines(world, ally: str) -> List[str]:
    """DDB-2's legibility: a full alliance states the call to arms among its
    terms, and names every live design of the ally on a court."""
    lines = [f"Binds France to {_shown(world, ally)}'s wars, offensive and defensive"]
    lines.extend(ally_design_lines(world, ally))
    return lines
