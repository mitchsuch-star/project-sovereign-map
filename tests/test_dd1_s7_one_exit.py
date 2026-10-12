"""DD-1 S7 Slice A — "one exit for a pair" and the fuzzer's and shuffle's rows.

Pre-Deploy S7 (October 11, 2026), `docs/PRE_DEPLOY_PLAN.md` §3.1 Step 2b.
The instruments are the evidence (`tools/treaty_fuzzer.py` reads 0 over
10 × 1,000; `tools/answer_binding_shuffle.py` reads 0 misbinds); these pins
hold each seam's behaviour by name so a regression says which rule broke:

  DD1-5   the bilateral armistice PAUSES the pair on its instance; the typed
          conquest RESOLVES it — both through `cleanup_war_end`, the one exit
  DD1-6   a pair back at war inside the prune window has a live purpose
  DD1-7   a letter's modal is shown only while its dialogue is held; a cooled
          quarrel retires its standing card on the live world
  DD1-8   a client taken by treaty follows its lord out of the wars he does
          not fight (§70.2 read on ENTRY)
  DD1-9   `pact` and the other display-map nouns are matter nouns
  DD1-10  a reopened pair leaves the resolved list; a returning court loses
          its exit stamps
  DD1-11  a refused declaration names its clause in words
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import backend.game_logic.diplomacy as D
from backend.commands import dialogue_routing
from backend.game_logic import jealousy
from backend.game_logic.settlement_helpers import (
    assert_war_instance_invariants,
    attach_pair_to_war_instance,
    attach_participant_to_war_instance,
    ensure_war_instance_for_pair,
)
from backend.game_logic.vassal import create_vassal_conquest, create_vassal_treaty
from backend.models.world_state import WorldState

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")


def _boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


def _ratify(world, proposer, target, ptype):
    with contextlib.redirect_stdout(io.StringIO()):
        return world._ratify_treaty({
            "proposer_nation": proposer, "target_nation": target,
            "type": ptype, "sweeteners": [], "demands": [], "clauses": []})


def _pair_meta(world, a, b):
    key = world._make_diplo_key(a, b)
    for war in list(world.war_instances.values()) + list(
            (getattr(world, "archived_war_instances", {}) or {}).values()):
        meta = (war.get("diplo_key_meta") or {}).get(key)
        if meta:
            return war, meta
    return None, None


def _round_trip(world) -> WorldState:
    return WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))


# ── DD1-5: the one exit ────────────────────────────────────────────────────

def test_dd1_5_a_bilateral_armistice_pauses_the_pair_on_its_instance():
    w = _boot()
    assert w.get_diplomatic_state("France", "Austria") == "WAR"
    result = _ratify(w, "France", "Austria", "armistice")
    assert result and result.get("type") == "diplomatic_treaty_signed", result
    assert w.get_diplomatic_state("France", "Austria") == "ARMISTICE"
    war, meta = _pair_meta(w, "France", "Austria")
    assert meta["pair_status"] == "armistice", meta
    assert w._make_diplo_key("France", "Austria") in war["active_diplo_keys"]
    assert_war_instance_invariants(w, context="dd1-5 armistice")


def test_dd1_5_the_typed_conquest_resolves_the_pair():
    w = _boot()
    with contextlib.redirect_stdout(io.StringIO()):
        D.set_diplomatic_state(w, "France", "Portugal", "WAR", "war_declaration")
        ensure_war_instance_for_pair(w, "France", "Portugal", entry_path="war_declaration")
        result = create_vassal_conquest(w, "France", "Portugal", garrison_size=10_000)
    assert result.get("success"), result
    assert w.get_diplomatic_state("France", "Portugal") == "VASSAL"
    _war, meta = _pair_meta(w, "France", "Portugal")
    assert meta["pair_status"] == "resolved", meta
    assert_war_instance_invariants(w, context="dd1-5 conquest")


# ── DD1-10 + DD1-6: the reopening ──────────────────────────────────────────

def _peace_then_cascade_back(w: WorldState) -> str:
    """France ↔ Austria: a signed peace, then the pair back at WAR six turns
    on through the SETTER (a cascade's entry — not `declare_war`, which
    writes its own purpose). Returns the pair key."""
    key = w._make_diplo_key("France", "Austria")
    war_id = next(wid for wid, war in w.war_instances.items()
                  if key in (war.get("active_diplo_keys") or []))
    result = _ratify(w, "France", "Austria", "peace")
    assert result and result.get("type") == "diplomatic_treaty_signed", result
    meta = w.war_instances[war_id]["diplo_key_meta"][key]
    assert meta["pair_status"] == "resolved"
    w.current_turn += 6
    with contextlib.redirect_stdout(io.StringIO()):
        # The pair re-attached to the SAME live instance (France still fights
        # Britain and Russia in it) — PR-D1d's reopening, the fuzzer's road.
        attached = attach_pair_to_war_instance(w, war_id, "Austria", "France",
                                               entry_path="defensive_cascade")
        assert attached.get("ok"), attached
        D.set_diplomatic_state(w, "Austria", "France", "WAR", "defensive_cascade")
    return key


def test_dd1_10_a_reopened_pair_leaves_the_resolved_list_and_its_court_the_exit_stamps():
    w = _boot()
    key = _peace_then_cascade_back(w)
    war = next(war for war in w.war_instances.values()
               if key in (war.get("active_diplo_keys") or []))
    meta = war["diplo_key_meta"][key]
    assert meta["pair_status"] == "war"
    assert meta.get("reopened_turn") == w.current_turn
    assert key in war["active_diplo_keys"]
    assert key not in war.get("resolved_diplo_keys", []), war.get("resolved_diplo_keys")
    for court in ("France", "Austria"):
        if court in war["active_participants"]:
            row = war["participant_meta"][court]
            assert row.get("exited_turn") is None, (court, row)
            assert "exit_path" not in row, (court, row)
    assert_war_instance_invariants(w, context="dd1-10 reopening")


def test_dd1_6_a_re_war_inside_the_prune_window_has_a_live_purpose_on_both_sides():
    w = _boot()
    key = _peace_then_cascade_back(w)
    entry = w.war_objectives.get(key) or {}
    for side in ("France", "Austria"):
        obj = entry.get(side)
        assert isinstance(obj, dict) and obj, (side, entry)
        assert obj.get("concluded_turn") is None, (side, obj)
    # The load migration stays dormant on a fresh S7 world: the purposes
    # round-trip unchanged.
    again = _round_trip(w)
    assert again.to_dict()["war_objectives"] == w.to_dict()["war_objectives"]


# ── DD1-8: the client rule on entry ────────────────────────────────────────

def test_dd1_8_a_client_taken_by_treaty_follows_its_lord_out_of_the_wars_he_does_not_fight():
    w = _boot()
    client = "Hesse"  # a free small court — inside Austria's power cap
    assert client not in w.vassals
    with contextlib.redirect_stdout(io.StringIO()):
        # A war Denmark leads against Sweden; the Ottomans stand with Sweden,
        # Hesse with Denmark — so Hesse fights the Ottomans in a war NEITHER
        # of them leads (the fuzzer's I2 exempts a war the client or that
        # court leads itself: that one is the client's own).
        made = ensure_war_instance_for_pair(w, "Denmark", "Sweden", entry_path="war_declaration")
        D.set_diplomatic_state(w, "Denmark", "Sweden", "WAR", "war_declaration")
        attach_participant_to_war_instance(w, made["war_id"], "Ottoman", side="defenders",
                                           entry_path="ally_entry")
        attach_pair_to_war_instance(w, made["war_id"], client, "Ottoman",
                                    entry_path="defensive_cascade")
        D.set_diplomatic_state(w, client, "Ottoman", "WAR", "defensive_cascade")
        # Austria, at peace with the Ottomans, takes Hesse as a client.
        D.set_diplomatic_state(w, "Austria", client, "OPEN_BORDERS", "treaty_ratification")
        assert w.get_diplomatic_state("Austria", "Ottoman") != "WAR"
        result = create_vassal_treaty(w, "Austria", client)
    assert result.get("success"), result
    assert w.get_diplomatic_state(client, "Ottoman") == "PEACE"
    assert w.get_diplomatic_state("Denmark", "Sweden") == "WAR"
    meta = w.war_instances[made["war_id"]]["diplo_key_meta"][w._make_diplo_key(client, "Ottoman")]
    assert meta["pair_status"] == "resolved", meta
    assert_war_instance_invariants(w, context="dd1-8 entry")


# ── DD1-11: the words ──────────────────────────────────────────────────────

def test_dd1_11_a_refused_declaration_names_the_clause_in_words():
    w = _boot()
    key = w._make_diplo_key("France", "Austria")
    war_id = next(wid for wid, war in w.war_instances.items()
                  if key in (war.get("active_diplo_keys") or []))
    with contextlib.redirect_stdout(io.StringIO()):
        attach_pair_to_war_instance(w, war_id, "Bavaria", "Austria", entry_path="ally_entry")
        D.set_diplomatic_state(w, "Bavaria", "Austria", "WAR", "ally_entry")
        result = D.declare_war(w, "France", "Bavaria")
    assert result.get("success") is False, result
    assert result.get("error") == "war_instance_side_conflict"
    message = str(result.get("message") or "")
    assert "war_instance_side_conflict" not in message
    assert "fights beside us" in message and "end that war first" in message, message


# ── DD1-9: the nouns ───────────────────────────────────────────────────────

def test_dd1_9_the_display_maps_nouns_are_matter_nouns():
    nouns = dialogue_routing._CLOSED_MATTER_NOUNS
    for word in ("pact", "pacts", "agreement", "armistice", "treaty", "vassalage",
                 "gift", "cession", "neutrality", "submission", "offer", "petition"):
        assert word in nouns, word
    for command_word in ("order", "open", "borders", "purchase"):
        assert command_word not in nouns, command_word


# ── DD1-7: the round trip ──────────────────────────────────────────────────

def test_dd1_7_a_letters_modal_is_shown_only_while_its_dialogue_is_held():
    w = WorldState()
    dm = w.dialogue_manager
    letter = {"type": "incoming_proposal", "target_nation": "Prussia", "options": [],
              "turn_created": int(w.current_turn), "blocking": False,
              "popup_payload": {"from_nation": "Prussia"}}
    dm.push(letter)
    w.incoming_proposal_popup = dict(letter["popup_payload"])
    shown = w.incoming_proposal_popup
    assert isinstance(shown, dict) and shown["dialogue_id"] == letter["dialogue_id"]
    dm.pop()
    assert w.incoming_proposal_popup is None
    assert w.to_dict()["incoming_proposal_popup"] is None
    # A payload without an identity (a legacy save) is served as it stands.
    w.incoming_settlement_offer_popup = {"proposer_nation": "Austria"}
    assert w.incoming_settlement_offer_popup == {"proposer_nation": "Austria"}


def test_dd1_7_a_cooled_quarrel_retires_its_standing_card_on_the_live_world():
    w = WorldState()
    marshal = next(m for m in w.marshals.values() if m.nation == w.player_nation)
    rival = next(m for m in w.marshals.values()
                 if m.nation == w.player_nation and m.name != marshal.name)
    marshal.jealous_of = rival.name
    marshal.jealousy_turns_remaining = 3
    card = {"kind": "jealousy_confrontation", "speaker": marshal.name,
            "title": f"Marshal {marshal.name} seeks an audience", "body": "...",
            "options": [], "context": {"marshal": marshal.name, "target": rival.name}}
    w.pending_marshal_petition = card
    with contextlib.redirect_stdout(io.StringIO()):
        jealousy.clear_jealousy(w, marshal, resolved_by_action=False, reason="time")
    assert w.pending_marshal_petition is None
    # …but an ANSWERED card is not a cooled one: the answer handler keeps it.
    marshal.jealous_of = rival.name
    w.pending_marshal_petition = card
    with contextlib.redirect_stdout(io.StringIO()):
        jealousy.clear_jealousy(w, marshal, resolved_by_action=False,
                                reason="the Emperor's promise", retire_standing_card=False)
    assert w.pending_marshal_petition is card
