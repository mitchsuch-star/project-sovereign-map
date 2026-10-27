"""S14h — the closing re-play's SCENES for DD-B's THIRD measure (October 26, 2026).

The third measure's 33 rows (`docs/BUG_FIXES.md` §S14G, S14G-1 … 33) were
sighted at turns 1 … 17 of three 20-turn roads
(`docs/audits/dd_b/{conquest,diplomacy,sea}_2026_10_25/`). Re-playing every
road by hand to each sighting's turn would cost three hours of client time per
run, so the re-play reaches each sighting's STATE by a crafted save instead —
the S14f part 2 method (`tools/_s14f_replay_scenes.py`): this tool writes the
saves into a DD-B run's `saves/` folder BEFORE the instrument starts
(`tools/dd_b_play.py start … --out <run>` creates the folder with
`exist_ok`), and the player loads each from "Load a Campaign…" in the real
client, acts, and reads the frame. Every scene is the sighting's own board as
the ledger describes it, built on the shipped 1805 boot with the fewest edits
that reproduce it and — wherever the game has a builder for the state — made
THROUGH that builder (the capture seam, the treaty ratifier, the bond mint, the
petition queue, the contingent raise, the proposal-in-transit resolver), so the
board is the one a turn would have produced. The manifest `scenes.md` beside the
saves says, per scene, which rows it serves, what to do and what the fixed
game must show; a row whose board the boot cannot stage is marked
"NOT STAGEABLE — read the fixed test instead" there.

    .venv/Scripts/python.exe -X utf8 tools/_s14h_replay_scenes.py --out <run>/saves

Each save is round-tripped through `save_manager.load_game` here, and each
scene's own `after_load` check asserts the staged state SURVIVED the load (a
pending letter, a petition, a counter, a draft, a standing order), so a save
the client cannot load — or loads without its board — never reaches the
instrument. A scene's docstring carries its manifest text after the line
`MANIFEST`; the builder cuts it out, so the manifest and the code cannot drift.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
sys.path.insert(0, str(REPO))
os.environ.setdefault("LLM_MODE", "mock")
os.environ.setdefault("SOVEREIGN_SEED", "historical")
for _k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_SMOKE_START"):
    os.environ.pop(_k, None)
os.environ["SOVEREIGN_MAP"] = "europe"


# ── the helpers (the S14f tool's, plus the S14h scenes' own) ────────────────

def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _boot():
    from backend.models.world_state import WorldState
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


def _fresh(boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


def _refresh(w):
    """Rebuild every cache a staged edit can leave stale."""
    w._build_marshal_index()
    w.invalidate_active_nations_cache()
    with _quiet():
        w.calculate_visibility()


def _place(w, **where):
    for name, loc in where.items():
        w.get_marshal(name).location = loc
    _refresh(w)


def _key(w, a, b):
    return w._make_diplo_key(a, b)


def _rel(w, a, b, value=None):
    key = _key(w, a, b)
    if value is not None:
        w.nation_relations[key] = int(value)
        w.invalidate_bloc_members_cache()
    return int(w.nation_relations.get(key, 0) or 0)


def _set_score(w, a, b, a_view):
    key = _key(w, a, b)
    w.war_scores[key] = a_view if key.split("|")[0] == a else -a_view


def _state(w, a, b, state):
    """A diplomatic state set through the game's own setter."""
    from backend.game_logic.diplomacy import set_diplomatic_state
    with _quiet():
        set_diplomatic_state(w, a, b, state, "replay")
    w.invalidate_active_nations_cache()


def _letter(w, nation, proposal_type, priority=60, war_score=0):
    """An AI court's letter to France, through the AI's own builders and
    transport (`deliver_ai_proposal`), so the mailbox row, the popup and the
    letter-book read exactly what a turn would have delivered."""
    from backend.game_logic import ai_diplomacy as AD
    terms = AD._build_proposal_terms(nation, proposal_type, war_score, w)
    prop = AD._make_proposal(nation, proposal_type, priority, terms, w)
    with _quiet():
        out = AD.deliver_ai_proposal(prop, w)
    return out, terms


def _take(w, region, nation):
    """The enemy's capture, through the real seam (a conquest record and all),
    with the alarm book cleared so the player reads only his own next act."""
    with _quiet():
        w.capture_region(region, nation)
    w.threat_sources_this_turn = []
    w.invalidate_active_nations_cache()


def _road(w, marshal_name, dest):
    """The stops of the road `<marshal>, march to <dest>` would walk."""
    from backend.commands.strategic import march_road
    with _quiet():
        road, refusal, _kind = march_road(w, w.get_marshal(marshal_name), dest)
    assert refusal is None and road, (marshal_name, dest, refusal)
    return [str(r) for r in road]


def _order(w, name, command_type, target, original, *, path=None, target_type="region",
           **extra):
    """A standing order as the order executor stamps it (issued the turn
    before, so the turn change walks its first step)."""
    from backend.models.marshal import StrategicOrder
    m = w.get_marshal(name)
    m.strategic_order = StrategicOrder(
        command_type=command_type, target=target, target_type=target_type,
        started_turn=int(w.current_turn) - 1, issued_turn=int(w.current_turn) - 1,
        original_command=original, path=list(path or []), **extra)
    return m


def _end_every_war(w, turns_ago=2):
    """Every war France's side fights, ended through the game's own pair
    resolver (the pairs move to `resolved_diplo_keys`, the instance stamps its
    end) — no corps is left on a stale war."""
    from backend.game_logic.settlement_helpers import resolve_pair_to_resolved
    for inst in list(w.war_instances.values()):
        for pair in list(inst.get("active_diplo_keys") or []):
            a, b = pair.split("|")
            _state(w, a, b, "PEACE")
            with _quiet():
                resolve_pair_to_resolved(w, pair, resolved_turn=max(1, int(w.current_turn) - turns_ago))
    w.invalidate_active_nations_cache()
    w.threat_sources_this_turn = []


def _execute(w, command):
    from backend.commands.executor import CommandExecutor
    with _quiet():
        return CommandExecutor().execute({"command": command}, {"world": w})


def _probe(fn, default=None):
    """A best-effort reading of the board for the record (`scenes.json`): the
    reading never fails a build — a module another session is mid-edit on
    answers `ERR:` in the record instead."""
    try:
        with _quiet():
            return fn()
    except Exception as exc:  # noqa: BLE001 — the record, not the gate
        return f"ERR: {type(exc).__name__}: {exc}"[:200] if default is None else default


# ── the scenes ──────────────────────────────────────────────────────────────

def scene_liberation(boot):
    """Rows S14G-1 and S14G-4 (the dispatch half): Munich — Bavaria's capital —
    in Austrian hands since the enemy phase, Mack's 2,500 inside it, Ney at
    Swabia beside it with the army; Napoleon at Lorraine on a standing march to
    Flanders, two provinces from the guns.

    MANIFEST
    Load replay_liberation. Do: (1) type `Ney, attack Mack` — Munich is Bavaria's
    capital, taken by Austria a turn ago, the Threat bar reads 84. Expect: the
    reply ends "Munich, Bavaria's capital, retaken — handed back to Bavaria."
    with NO plunder/secure question; the alarm line reads "+3 — Won a battle +3"
    and nothing for a captured capital or conquered territory (no "+15", no
    "+2"), the Threat bar moves 84 -> about 87, not to 100; the map paints Munich
    Bavaria's again and the campaign log (L) records the liberation, not a
    conquest (row 1). The AI's own road (Austria retaking an ally's ground from
    France, the reckless auto-charge) is NOT STAGEABLE — read the fixed test
    instead (TestS14G1, TestS14GX10, TestS14GX12). (2) Then press End Turn: Napoleon —
    standing march to Flanders, Lorraine two provinces from Munich — hears the
    guns and the cannon-fire question comes ("Cannon fire at Munich, Sire.
    Investigate?"); the morning dispatch lists him "HALTED at Lorraine — awaiting
    your word"; click Continue as Ordered, then press R (the dispatch re-read).
    Expect: he is no longer "awaiting your word" once he has been answered — the
    stored dispatch line reads "HALTED at Lorraine — answered: continued." (the
    live re-read shows his road, "Moving to Flanders"), and Napoleon marches on
    (row 4).
    """
    w = _fresh(boot)
    w.current_turn = 3
    _take(w, "Munich", "Austria")
    mack = w.get_marshal("Mack")
    mack.location, mack.strength = "Munich", 2500
    _place(w, Ney="Swabia", Napoleon="Lorraine")
    road = _road(w, "Napoleon", "Flanders")
    _order(w, "Napoleon", "MOVE_TO", "Flanders", "Napoleon, march to Flanders", path=road)
    w.threat_by_target["France"] = 84
    w.threat_sources_this_turn = []
    w.actions_remaining = 4
    assert w.regions["Munich"].controller == "Austria"
    assert "Munich" in w.regions["Swabia"].adjacent_regions
    assert w.get_distance("Lorraine", "Munich") == 2

    def after_load(world):
        assert world.regions["Munich"].controller == "Austria"
        assert world.get_marshal("Mack").location == "Munich"
        assert world.get_marshal("Napoleon").strategic_order is not None
    return w, {"napoleon_road": road, "threat": int(w.threat_level), "after_load": after_load}


def scene_aggressive(boot):
    """Rows S14G-2 and S14G-19: the army massed at Bohemia for the assault on
    Vienna — a six-corps stack of Napoleon, Ney, Soult, Murat, Lannes
    (aggressive, on a standing "support Napoleon") and Massena (aggressive,
    22,000, morale 36%) — with Kutuzov's Russians in view at Hungary, one
    province off.

    MANIFEST
    Load replay_aggressive. Do: type `Massena, support Napoleon`; then press End
    Turn and read the gate card BEFORE confirming (Lannes already stands on a
    support order). Expect: the order's reply names the interrupt — "He will drop
    this order for any battle within two provinces in a war of ours." — and so
    does the standing quote; the End Turn gate names an aggressive corps with a
    standing order and the largest visible foe within two provinces (Kutuzov at
    Hungary) beside the morale pairing for Massena (row 2). The interrupt itself
    is KEPT: if a battle is fought within two provinces the aggressive man still
    leaves his order for the guns, and now the page said so (that effect is NOT
    STAGEABLE — nobody can force a battle inside two provinces at the turn change;
    read TestS14G2 for the kept redirect). Before ending the
    turn, click the stack's NAME LABEL on the map (the "+5" label over Bohemia),
    not the piece: it opens the lead marshal's panel, not Bohemia's province panel
    (row 19) — the label is a click target bound to the group's lead marshal.
    """
    w = _fresh(boot)
    w.current_turn = 6
    for name in ("Napoleon", "Ney", "Soult", "Murat", "Lannes", "Massena"):
        w.get_marshal(name).location = "Bohemia"
    massena = w.get_marshal("Massena")
    massena.strength, massena.morale = 22000, 36
    # the sighting's field: Kutuzov's 33,000 the largest foe in view; the
    # Austrian archdukes already worn down by six turns of war
    kutuzov = w.get_marshal("Kutuzov")
    kutuzov.location, kutuzov.strength = "Hungary", 33000
    w.get_marshal("ArchdukeCharles").strength = 12000
    w.get_marshal("Mack").strength = 8000
    w.get_marshal("ArchdukeJohn").strength = 7000
    _order(w, "Lannes", "SUPPORT", "Napoleon", "Lannes, support Napoleon",
           target_type="marshal", arrived_turn=int(w.current_turn) - 1)
    w.actions_remaining = 4
    _refresh(w)
    assert massena.personality == "aggressive" and w.get_marshal("Lannes").personality == "aggressive"
    assert w.is_at_war("France", "Russia")
    assert w.get_distance("Bohemia", "Hungary") <= 2
    assert any(m.name == "Kutuzov" for m in w.get_visible_enemies("France"))

    def gate():
        from backend.game_logic.dispatch import end_turn_army_warning
        return end_turn_army_warning(w, "France")

    def after_load(world):
        assert world.get_marshal("Lannes").strategic_order.command_type == "SUPPORT"
        assert int(world.get_marshal("Massena").morale) == 36
    return w, {"gate": _probe(gate), "after_load": after_load}


def scene_support(boot):
    """Row S14G-3: the Emperor at Paris on a standing march for Lyonnais; Davout
    and Lannes (sorting before him) and Ney (after) on a plain "support
    Napoleon" at Paris; Soult unordered beside them. Quiet French ground — the
    ally is safe wherever he stands.

    MANIFEST
    Load replay_support. Do: type `Soult, support Napoleon` (read the reply and
    the quote; his own order is new this turn and ticks one turn later), then
    press End Turn and read where Davout, Lannes and Ney stand and what they are
    doing (Generals screen, G, or the map). Expect: the reply
    says what the order does — "He goes to Napoleon now and stays only while
    Napoleon is in danger … 'Ney, follow Napoleon' keeps him at Napoleon's side";
    after the turn all three supporters LAPSE alike ("Napoleon is secure") —
    Davout and Lannes at Paris, Ney one step on beside the Emperor at Limousin —
    and none of them trails him across the country tick after tick (row 3). With
    the old rule Ney would have followed the Emperor home for seven turns.
    """
    w = _fresh(boot)
    w.current_turn = 9
    _place(w, Napoleon="Paris", Davout="Paris", Lannes="Paris", Ney="Paris", Soult="Paris")
    road = _road(w, "Napoleon", "Lyonnais")
    _order(w, "Napoleon", "MOVE_TO", "Lyonnais", "Napoleon, march to Lyonnais", path=road)
    for name in ("Davout", "Lannes", "Ney"):
        _order(w, name, "SUPPORT", "Napoleon", f"{name}, support Napoleon",
               target_type="marshal", arrived_turn=int(w.current_turn) - 1)
    w.actions_remaining = 4

    def after_load(world):
        for name in ("Davout", "Lannes", "Ney"):
            assert world.get_marshal(name).strategic_order.command_type == "SUPPORT", name
        assert world.get_marshal("Soult").strategic_order is None
    return w, {"napoleon_road": road, "after_load": after_load}


def scene_petition(boot):
    """Row S14G-5: Murat (aggressive, 18,920, envious of Ney) has an audience
    card pending whose quarry — Mack at Swabia — is no longer there: Mack is
    beaten and gone to Tyrol, Archduke Charles (31,690) has arrived at Munich,
    the only man now in Murat's reach.

    MANIFEST
    Load replay_petition. Do: open Murat's audience (the notice rail row "Marshal
    Murat seeks an audience" / his card on the Generals screen) and read the card,
    then click the option that sends him ("Send him against …"), twice if it asks.
    Expect: the card names the man who is there NOW
    (Archduke Charles at Munich, with the muster against Murat's 18,920) and says
    that Mack has left; the first click spends NOTHING and asks with Berthier's
    banded odds ("Mack has left Swabia; Archduke Charles at Munich (31,690 men
    against his 18,920) is what stands in his reach now … Send him?") — or, when
    the odds hold him, refuses free; only the second click commits (row 5). The
    old game sent him at Charles alone after 2 AP and announced "Archduke
    Charles, then." after the battle.
    """
    from backend.game_logic import jealousy as J
    w = _fresh(boot)
    w.current_turn = 4
    w.actions_remaining = 4
    murat, ney = w.get_marshal("Murat"), w.get_marshal("Ney")
    murat.jealous_of = "Ney"
    murat.jealousy_turns_remaining = 3
    murat.strength = 18920
    assert murat.personality == "aggressive" and murat.location == "Franche-Comte"
    _refresh(w)
    # The card is stamped with the quarrel's own escalation level: a stamp that
    # differs from the live one is retired at load ("moved_on"), so the level
    # is read, never guessed.
    level = int(J.get_escalation_level(murat, "Ney"))
    with _quiet():
        status = J.queue_confrontation_petition(w, murat, ney, level)
    assert status == J.PETITION_QUEUED, status
    card = w.pending_marshal_petition
    stored_quarry = next(o for o in card["options"] if o["id"] == "command").get("quarry")
    # the sighting: Mack beaten and gone, Charles arrived where the order would fall
    mack, charles = w.get_marshal("Mack"), w.get_marshal("ArchdukeCharles")
    mack.location, mack.strength = "Tyrol", 12000
    charles.location, charles.strength = "Munich", 31690
    _refresh(w)

    def delivered():
        live = J.refresh_petition_affordability(w.pending_marshal_petition, w)
        opt = next(o for o in live["options"] if o["id"] == "command")
        return {"quarry": opt.get("quarry"), "detail": opt.get("detail", "")[:180]}

    def after_load(world):
        assert world.pending_marshal_petition is not None
        assert world.pending_marshal_petition.get("kind") == "jealousy_confrontation"
    return w, {"stored_quarry": stored_quarry, "tier": _probe(lambda: J.petition_tier(card)),
               "delivered_card": _probe(delivered), "after_load": after_load}


def scene_envoys(boot):
    """Row S14G-6: Austria's armistice letter (a GREAT court's, current) with
    the Ottoman and Portuguese Open Borders courtesies queued behind it —
    turn 5, France at war with Austria.

    MANIFEST
    Load replay_envoys. Do: Austria's letter is open. (a) Look at the buttons and
    the text, click Not Now, close the window, and look at the Cabinet button
    (top bar), its tooltip, the Envoys badge's tooltip, then press F1. (b) Then
    reopen the Envoys (badge) and Reject Austria's letter; with only the Ottoman
    and Portuguese courtesies left, press F1 again. Expect: the Not Now button
    reads "(Cabinet stays shut)", a line under the buttons says "Set aside — the
    Cabinet stays shut until it is answered or the turn ends", the letter's body
    states the lock, the Cabinet button's face reads "The Cabinet — shut" (amber)
    with the court named and the Envoys badge's tooltip says it too; F1 meets the
    shut Cabinet. After (b) the two lesser courts' letters answer IN PLACE — they
    do not shut the Cabinet — so F1 opens it (row 6).
    """
    w = _fresh(boot)
    w.current_turn = 5
    _set_score(w, "France", "Austria", 20)
    w.actions_remaining = 4
    delivered = {}
    for nation, ptype, score in (("Austria", "armistice", -20), ("Ottoman", "open_borders", 0),
                                 ("Portugal", "open_borders", 0)):
        out, terms = _letter(w, nation, ptype, priority=70 if nation == "Austria" else 60,
                             war_score=score)
        delivered[nation] = [bool(out), terms.get("type")]
        assert out, (nation, ptype)
    dm = w.dialogue_manager
    assert dm.peek() is not None and dm.peek().get("target_nation") == "Austria"
    assert [d.get("target_nation") for d in dm._queue] == ["Ottoman", "Portugal"]

    def after_load(world):
        cur = world.dialogue_manager.peek()
        assert cur and cur.get("type") == "incoming_proposal" and cur.get("target_nation") == "Austria"
        assert len(world.dialogue_manager._queue) == 2
    return w, {"delivered": delivered, "after_load": after_load}


def _fix_armistice_score(w, wanted=38):
    """France's side of the war score with Austria, backed by the FIELD, until
    the armistice the Cabinet would draft reads a hair over the bar (the
    sighting: 51 of 50).

    S14G-X172 (the closing re-play, October 26, 2026): the first cut wrote the
    stored score alone; the end-turn recompute read the field (no battle of
    ours behind the figure) and the court's verdict fell 41 below the card.
    Now the field carries it: decisive and battle records of ours (each capped
    by the formula), the stored score set to the LIVE one the recompute will
    return, and the relation lifted until the card reads the bar — what the
    turn's decay takes back stays inside the PL-9 tolerance band."""
    from backend.game_logic import diplomacy as D
    prop = {"type": D.armistice_variant_for(w, "France", "Austria"), "proposer_nation": "France",
            "target_nation": "Austria", "sweeteners": [], "demands": [], "clauses": []}
    key = _key(w, "France", "Austria")
    turn = int(w.current_turn)
    w.decisive_battles.setdefault(key, []).extend(
        {"winner": "France", "loser": "Austria", "turn": turn, "region": "Swabia"} for _ in range(2))
    w.battle_records.setdefault(key, []).extend(
        {"winner": "France", "loser": "Austria", "turn": turn, "region": "Swabia"} for _ in range(3))
    live = int(D.calculate_war_score("France", "Austria", w))
    _set_score(w, "France", "Austria", live)
    start = int(w.nation_relations.get(key, 0))
    for rel in range(start, 80):
        _rel(w, "France", "Austria", rel)
        if D.calculate_acceptance(prop, w).get("score", 0) >= 50:
            return live
    raise AssertionError(f"no relation makes the armistice carry on a live score of {live} (wanted {wanted})")


def scene_truce_offer(boot):
    """Row S14G-7 (the offer): turn 3, France ahead of Austria (the armistice
    reads 51 of 50), Ney and Davout at Swabia and Bernadotte at Franconia —
    three French corps on the ally Bavaria's soil — Murat one march off at
    Franche-Comte.

    MANIFEST
    Load replay_truce_offer. Do: F1, Austria, Propose Armistice; read the confirm
    card's rows and the tooltip BEFORE sending, then send; End Turn and read the
    enemy phase and the morning dispatch; then order `Murat, march to Swabia`.
    Expect: the confirm LEADS with the "Bavaria stays at war with Austria under
    this truce" row and ends on the consequence — "Your corps will not fight for
    her under the truce; Austria may take her provinces where your corps stand,
    and ground that changes hands puts them on the road home — Berthier marches
    them out (up to 5 turns of safe passage) and none may enter it again." The
    march into Swabia, ordered after the accept, names the front before the
    order is paid ("Swabia is Bavaria's front — Austria, under truce with us, is
    at war with her; a corps there will not fight, and marches home if the ground
    changes hands.") and the dispatch of a corps stranded on closed soil says
    whether Berthier has already put it on the road home (row 7). Whether Austria
    then storms Swabia in the enemy phase is the AI's own choice and cannot be
    forced (NOT STAGEABLE); replay_counter stages that aftermath outright.
    """
    w = _fresh(boot)
    w.current_turn = 3
    w.actions_remaining = 4
    _place(w, Ney="Swabia", Davout="Swabia", Bernadotte="Franconia", Mack="Tyrol")
    score = _fix_armistice_score(w)
    assert w.get_diplomatic_state("France", "Austria") == "WAR"
    assert w.get_diplomatic_state("France", "Bavaria") == "ALLIANCE"

    def line():
        from backend.game_logic import diplomacy as D
        return D.truce_followers_line(w, "France", "Austria")

    def after_load(world):
        assert world.get_diplomatic_state("France", "Austria") == "WAR"
        assert world.get_marshal("Ney").location == "Swabia"
    return w, {"war_score_for_france": score, "truce_line": _probe(line), "after_load": after_load}


def _sign_armistice(w, a="France", b="Austria"):
    """The armistice signed through the one ratifier (the evacuation corridor,
    the sureties and the records all follow from it)."""
    from backend.game_logic import diplomacy as D
    variant = D.armistice_variant_for(w, a, b)
    with _quiet():
        event = w._ratify_treaty({"type": variant, "proposer_nation": a, "target_nation": b,
                                  "sweeteners": [], "demands": [], "clauses": []})
    assert event and event.get("type") != "diplomatic_treaty_failed", event
    assert w.get_diplomatic_state(a, b) == "ARMISTICE"
    w.invalidate_active_nations_cache()


def _austria_takes(w, *regions):
    """Austria storms the named provinces under the truce, announced as the
    enemy phase announces it."""
    from backend.models.world_state import announce_third_party_capture
    for region in regions:
        old = w.regions[region].controller
        w.regions[region].controller = "Austria"
        w.invalidate_active_nations_cache()
        with _quiet():
            announce_third_party_capture(w, region, old, "Austria")


def _stranded_after_the_truce(w):
    """The diplomacy road's turn 3 -> 5: the armistice signed at turn 3 (Ney,
    Davout and Murat at Swabia, Bernadotte at Franconia), Austria storming
    Swabia and Munich at turn 4, Berthier's tick handing the stranded corps the
    road home. Leaves `w` at turn 4 after the tick."""
    w.current_turn = 3
    _place(w, Ney="Swabia", Davout="Swabia", Murat="Swabia", Bernadotte="Franconia", Mack="Tyrol")
    _fix_armistice_score(w)
    _sign_armistice(w)
    w.current_turn = 4
    _austria_takes(w, "Swabia", "Munich")
    _refresh(w)
    from backend.game_logic.withdrawal import process_evacuation_grants
    with _quiet():
        process_evacuation_grants(w)
    marching = [n for n in ("Ney", "Davout", "Murat")
                if w.get_marshal(n).strategic_order is not None]
    assert marching == ["Ney", "Davout", "Murat"], marching
    w.threat_sources_this_turn = []


def scene_counter(boot):
    """Rows S14G-21 and S14G-23: the diplomacy road at turn 5 — the armistice
    with Austria signed at turn 3, Swabia and Munich stormed at turn 4 with Ney,
    Davout and Murat on the road home, and Bavaria's COUNTER to France's
    vassalage proposal (142 gold at the signing) pending: she asks 300 more.

    MANIFEST
    Load replay_counter. Do: (a) read Bavaria's counter popup, then click Accept
    counter-offer. (b) F1, Prussia, propose a Non-Aggression Pact (relations are
    high enough that she accepts) and send it. (c) End Turn and read the morning
    dispatch. Expect: (a) the counter marks what the court ADDED — "Added by
    Bavaria: 300 gold more (442 at the signing)" — one gold line, not "You pay
    142; You pay 300" with nothing marked new (row 23). (c) The dispatch does NOT
    say "the war with Bavaria and Prussia is over" (France was at war with
    neither); Bavaria's vassalage and Prussia's pact do not re-run the corps'
    evacuation as a peace, and the corps that already hold the treaty's own road
    home are not listed as "hold under your own orders … not moved" (row 21).
    """
    from backend.game_logic import diplomacy as D
    w = _fresh(boot)
    _stranded_after_the_truce(w)
    # Prussia's pact must be one she would sign (the sighting held her high).
    for rel in range(0, 90, 5):
        _rel(w, "France", "Prussia", rel)
        nap = {"type": "non_aggression", "proposer_nation": "France", "target_nation": "Prussia",
               "sweeteners": [], "demands": [], "clauses": []}
        if D.calculate_acceptance(nap, w).get("score", 0) >= 50:
            break
    else:
        raise AssertionError("Prussia never accepts a pact")
    # Bavaria: a court that will counter, not accept (relation 50), and the
    # proposal in transit since turn 4 — resolved by the game's own resolver.
    _rel(w, "France", "Bavaria", 50)
    prop = {"type": "vassalage", "proposer_nation": "France", "target_nation": "Bavaria",
            "sweeteners": [{"type": "gold_lump", "value": 142}], "demands": [], "clauses": []}
    assert D.calculate_acceptance(prop, w)["outcome"] == "COUNTER_OFFER"
    w.proposal_in_transit = {
        "target": "Bavaria", "proposal": prop, "turn_sent": 4, "dp_cost": 3,
        "acceptance_snapshot": int(D.calculate_acceptance(prop, w)["score"]),
        "diplomatic_state_at_send": w.get_diplomatic_state("France", "Bavaria"),
        "payer_gold_at_send": int(w.nation_gold["France"])}
    w.talleyrand_state = "IN_TRANSIT"
    w.current_turn = 5
    w.actions_remaining = 4
    with _quiet():
        events = w._process_proposal_in_transit()
    assert [e.get("outcome") for e in events] == ["COUNTER_OFFER"], events
    top = w.dialogue_manager.peek()
    assert top and top.get("type") == "counter_offer_response", top
    counter_terms = top["context"]["counter_terms"]

    def after_load(world):
        cur = world.dialogue_manager.peek()
        assert cur and cur.get("type") == "counter_offer_response"
        assert world.get_marshal("Ney").strategic_order is not None
        assert world.regions["Swabia"].controller == "Austria"
    return w, {"counter_sweeteners": counter_terms.get("sweeteners"),
               "counter_text": " ".join(str(top["talleyrand_text"]).split())[:240],
               "prussia_relation": _rel(w, "France", "Prussia"), "after_load": after_load}


def scene_truce_mission(boot):
    """Rows S14G-24, S14G-25 and S14G-28: the diplomacy road at turn 6 —
    the armistice with Austria (bonded to Britain's no-separate-peace bond, so
    its exit is forced to war) at relation -57 with Talleyrand's Improve
    Relations on Austria running; Spain, our ally, has slid to 36; no letter
    pending, 5 DP.

    MANIFEST
    Load replay_truce_mission. Do: (a) F1, Austria — read Talleyrand's reading of
    the truce. (b) F1, Britain, send any proposal (Propose Peace) and read the
    send reply, the preview, the notice rail chip and the top bar's mission
    summary. (c) F1, Spain — read the Reassure Ally row. Expect: (a) a bonded
    truce at -57 never says "short of the line" or "ripens into peace": it says
    Austria is bound by Britain's bond not to sign alone (the Propose Peace
    tooltip's own wording), and the projection counts the courtship running
    (+8 a turn), not the natural thaw alone (row 24). (b) the preview and the
    reply say "Talleyrand carries this letter; his Improve Relations at Austria
    pauses until he is home (about N turns)"; the chip and the top bar carry
    "(paused — carrying a letter)" (row 25). (c) "Reassure Ally is shut while
    Talleyrand is at Austria's court" prices the trade — what recalling
    forfeits (the Austrian courtship, +8 a turn, N turns) against how soon
    Spain, at 36, drops under the 40 line — and the Improve Relations confirm
    warns that it would shut Reassure Ally for a sliding ally (row 28).
    """
    from backend.game_logic import bond as BD
    w = _fresh(boot)
    w.current_turn = 3
    w.actions_remaining = 4
    _place(w, Ney="Swabia", Davout="Swabia", Bernadotte="Franconia", Mack="Tyrol")
    _fix_armistice_score(w)
    with _quiet():
        minted = BD.mint_bond(w, payer="Britain", member="Austria", enemy="France")
    assert minted.get("success"), minted
    _sign_armistice(w)
    w.current_turn = 6
    key = _key(w, "France", "Austria")
    w.armistice_turns[key] = 3
    _rel(w, "France", "Austria", -57)
    w.diplomatic_points = 5
    w.active_diplomatic_mission = {
        "type": "IMPROVE_RELATIONS", "target": "Austria", "turns_active": 3,
        "paused": False, "paused_turns": 0, "started_turn": 3,
        "initial_relation": -77, "started_state": "ARMISTICE",
        "earned": 11, "shocks": [], "paused_errand": 0, "paused_starved": 0,
    }
    w.talleyrand_state = "ON_MISSION"
    _rel(w, "France", "Spain", 36)
    w.invalidate_active_nations_cache()
    assert BD.pair_bond(w, "France", "Austria") is not None

    def exit_reading():
        from backend.game_logic import diplomacy as D
        e = D.armistice_expiry_exit(w, "France", "Austria")
        return {"exit": e["exit"], "relation": e["relation"], "projected": e["projected"],
                "bond": e.get("bond")}

    def busy():
        from backend.game_logic import diplomacy as D
        return D.slide_lever(w, "France", "Spain")

    def after_load(world):
        assert world.get_diplomatic_state("France", "Austria") == "ARMISTICE"
        assert world.active_diplomatic_mission and world.active_diplomatic_mission["target"] == "Austria"
        assert BD.pair_bond(world, "France", "Austria") is not None
    return w, {"exit": _probe(exit_reading), "spain_lever": _probe(busy), "after_load": after_load}


def _copy(w):
    """A throwaway copy of a staged world for a probe that acts on it."""
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(w.to_dict(), default=str)))


def scene_design_peace(boot):
    """Rows S14G-9, S14G-10 and S14G-27: turn 7, France at peace with every
    court (every war ended through the pair resolver), 6,000 gold, 5 DP; the
    three great powers at -50 (they qualify for a league); Britain's and
    Russia's designs already BOUGHT OFF (two buy-offs struck, as the sighting);
    Prussia courted by Talleyrand (Improve Relations running, relation +10) with
    her Hanover design live.

    MANIFEST
    Load replay_design_peace. Do: (a) F1, Austria, look at the Buy Off Their
    Design row and its quote (`buy off Austria` in the line shows the same quote);
    open the Balance of Europe page (D, Balance tab) and read Britain's, Russia's
    and Austria's rows and the page footer. (b) Type `license Prussia against
    Hanover` and read the quote BEFORE answering; answer no. (c) Press End Turn and
    read what the blocking phase box says. Expect: (a) the buy-off quote says
    what it does to a league — "+5 relations; she still counts toward a league
    until relations reach -10" — and so does the footer; Britain's and Russia's
    rows read "Design bought off, N turns left; her league place is her
    relations." (row 9). (b) the licence quote names the war it licenses —
    "If Prussia then declares on Hanover, her relations with every court,
    France's included, fall 15 (France-Prussia now +10, … once this compact is
    struck, … after her declaration)" and that the Improve Relations running there
    is set back (row 10; Prussia's later declaration on Hanover is the AI's own
    act at a later turn — NOT STAGEABLE, read TestS14G10 for the figures after
    the fact). (c) with no war to France's name and nothing of the
    other courts in sight, the enemy phase raises NO blocking box: one line in
    the terminal ("Britain, Spain and Bavaria stirred, but their formations remain
    beyond our sight") says so and the turn goes on (row 27).
    """
    w = _fresh(boot)
    w.current_turn = 7
    w.actions_remaining = 4
    w.nation_gold["France"] = 6000
    w.diplomatic_points = 5
    _end_every_war(w)
    for nation in ("Austria", "Britain", "Russia"):
        _rel(w, "France", nation, -50)
    _rel(w, "France", "Prussia", 10)
    # Nothing of the foreign courts in our sight: no French corps stands on
    # a front where an AI act would be FULL-visible (Bernadotte comes home).
    _place(w, Bernadotte="Rhineland")
    w.active_coalition = None
    w.coalition_brewing = None
    w.threat_by_target["France"] = 45
    w.pending_dispatch_events = []
    for court in ("Britain", "Russia"):
        out = _execute(w, {"action": "buy_off_design", "target": court,
                           "raw_input": f"buy off {court}", "confirmed": True})
        assert out.get("success") is True, (court, out)
        w.invalidate_bloc_members_cache()
    w.active_diplomatic_mission = {
        "type": "IMPROVE_RELATIONS", "target": "Prussia", "turns_active": 2,
        "paused": False, "paused_turns": 0, "started_turn": 5,
        "initial_relation": -10, "started_state": "PEACE",
        "earned": 16, "shocks": [], "paused_errand": 0, "paused_starved": 0,
    }
    w.talleyrand_state = "ON_MISSION"
    w.invalidate_active_nations_cache()
    assert not [n for n in w.get_active_nations() if n != "France" and w.is_at_war("France", n)]

    def quote_buyoff():
        return _execute(_copy(w), {"action": "buy_off_design", "target": "Austria",
                                   "raw_input": "buy off Austria"}).get("message", "")[-260:]

    def quote_license():
        return _execute(_copy(w), {"action": "sponsor_design", "target": "Prussia",
                                   "raw_input": "license Prussia against Hanover"}).get("message", "")[:420]

    def after_load(world):
        assert not [n for n in world.get_active_nations()
                    if n != "France" and world.is_at_war("France", n)]
        assert [b for b in (getattr(world, "compensation_bargains", None) or [])
                if not b.get("ended_turn")], "the two buy-offs did not survive"
    return w, {"buyoff_quote": _probe(quote_buyoff), "license_quote": _probe(quote_license),
               "gold_left": int(w.nation_gold["France"]), "after_load": after_load}


def scene_guarded(boot):
    """Rows S14G-11, S14G-33 and S14G-4 (the order half): turn 12, Prussia
    armed-neutral (Hanover, Brunswick and Westphalia hers; her second design,
    Armed Neutrality, active) with Open Borders signed; Soult at Dresden;
    Napoleon (37,692) at Flanders.

    MANIFEST
    Load replay_guarded. Do, in this order: (a) type `Soult, march to Flanders`.
    (b) type `Napoleon, march to Flanders` (he stands there). (c) type `Napoleon,
    march to Paris` and read the reply (he leaves Flanders, so do it last).
    Expect: (a) the order does not spend an action until it has asked, free:
    "Berlin and Brunswick are Prussia's guarded ground (Armed Neutrality) —
    standing in them costs -25 with Prussia — march, go round or cancel?" with a
    go-round offered (row 11); the quote, the reply's sentence after "Route:", the
    Open Borders effect line and the shift beat carry the same words. (b) refused
    FREE — "Napoleon already stands at Flanders — nothing spent." — with no order
    replaced and no action charged (row 4). (c) the road runs over our own soil
    (Picardy, Artois), not Westphalia (Prussian soil, where 37,692 men outrun the
    province's feed), and the reply names the turns it takes (row 33).
    """
    from backend.game_logic.agendas import get_active_agenda
    w = _fresh(boot)
    w.current_turn = 12
    w.actions_remaining = 4
    for name in ("Hanover", "Brunswick", "Westphalia"):
        w.regions[name].controller = "Prussia"
    _state(w, "France", "Prussia", "OPEN_BORDERS")
    w.invalidate_bloc_members_cache()
    nap = w.get_marshal("Napoleon")
    nap.strength = 37692
    _place(w, Soult="Dresden", Napoleon="Flanders")
    assert get_active_agenda("Prussia", w).id == "armed_neutrality"
    assert w.get_diplomatic_state("France", "Prussia") == "OPEN_BORDERS"

    def roads():
        return {"soult_to_flanders": _road(w, "Soult", "Flanders"),
                "napoleon_to_paris": _road(w, "Napoleon", "Paris")}

    def after_load(world):
        assert world.get_marshal("Soult").location == "Dresden"
        assert world.get_marshal("Napoleon").location == "Flanders"
        assert world.regions["Westphalia"].controller == "Prussia"
    return w, {"roads": _probe(roads), "after_load": after_load}


def scene_table(boot):
    """Rows S14G-12, S14G-26 and S14G-I1: turn 16, the Britain-alone settlement
    DRAFT kept — Peace, 1,000 gold to Britain and the erection of Ireland
    (Ulster and Munster, held by France) — with 6,241 gold in the chest.

    MANIFEST
    Load replay_table. Do: open the war card (the war banner, lower right), Open
    Settlement with Britain; read the header and the standing hint; click More
    generous until it stops; click the gold line's [+] / [-] (the instrument lists
    it as "+" / "-" now); then click Back Out, read the reply, and press End Turn
    and read the first line of the next turn's notices. Expect: the dial's note
    sits at the TOP of the header ("Gold past 1,000 buys nothing more from Britain
    at this table, Sire.") with a "more below" cue; the standing hint says "Gold is
    at its ceiling for Britain (26 of 50); what weighs on her is the erection of
    Ireland (-23) — remove it or offer land (a province weighs about 875g)." and
    no longer "use More generous until each accepts"; the gold [+]
    stops at the credit ceiling and says so (row 12). Back Out answers "Settlement
    draft kept until the turn ends — reopen Settlement this turn to continue", the
    war card's badge reads "Draft kept until turn's end", and the next turn's
    notice says the draft "was set aside at turn's end (a draft lasts one turn)"
    (row 26). The control the player clicked in the sighting is listed by the DD-B
    instrument as an icon with its tooltip (row I1, an instrument row).
    """
    from backend.game_logic import settlement_staging as SS
    w = _fresh(boot)
    w.current_turn = 16
    w.actions_remaining = 4
    w.nation_gold["France"] = 6241
    for region in ("Ulster", "Munster"):
        w.regions[region].controller = "France"
    w.invalidate_active_nations_cache()
    terms = [{"type": "peace"},
             {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 1000,
              "authored_by": "player"},
             {"type": "create_client", "from": "Britain", "to": "France", "tag": "Ireland",
              "client_display_name": "Ireland", "provinces": ["Ulster", "Munster"],
              "authored_by": "player"}]
    key = SS.save_scoped_settlement_draft(
        w, war_id="war_1", selected_target_nation="Britain",
        covered_enemy_participants=["Britain"], settlement_terms=terms)
    assert w.is_at_war("France", "Britain")

    def britain_row():
        with _quiet():
            preview = SS.build_settlement_preview(
                w, war_id="war_1", settlement_terms=list(terms),
                covered_enemy_participants=["Britain"], actor_nation="France",
                ignore_active_dialogue=True)
            dialogue = SS.build_settlement_confirm_dialogue(
                w, preview, caller_kind=SS.SETTLEMENT_EDITOR_CALLER_KIND, dialogue_mode="PROPOSE")
        return next(r for r in dialogue["per_court_acceptance"] if r["nation"] == "Britain"), dialogue

    # The sighting's table read 26 of 50 at the ceiling: France ahead in the
    # Britain war. Nudge the score until the row reads what the player read.
    best = None
    for score in range(0, 80, 2):
        _set_score(w, "France", "Britain", score)
        total = int(britain_row()[0].get("total", 0))
        if best is None or abs(total - 26) < abs(best[1] - 26):
            best = (score, total)
        if total >= 26:
            break
    _set_score(w, "France", "Britain", best[0])

    def row():
        britain, dialogue = britain_row()
        return {"total": britain.get("total"), "blocker": britain.get("top_blocker_component"),
                "hint": dialogue.get("propose_carry_hint", "")[:200]}

    def after_load(world):
        drafts = world.pending_settlement_drafts_by_key
        assert key in drafts and len(drafts[key]) == 3, drafts
        assert world.regions["Ulster"].controller == "France"
    return w, {"draft_key": key, "britain_row": _probe(row), "after_load": after_load}


def scene_opening(boot):
    """Rows S14G-8, 13, 14, 15, 16, 20 and 22 (every one a first-turns reading):
    the shipped 1805 boot, turn 1, UNTOUCHED — France at war with Britain,
    Austria and Russia, Britain's design live, Flanders held by France, Ney at
    Rhineland and Massena (42,000) at Milan, Tyrol unscouted, Mack's 52,000 at
    Swabia. (No stack and no joiner near Tyrol: the muster of row 14 reads only
    the men in view.)

    MANIFEST
    Load replay_opening. Do, in this order: (1) F1 -> Talleyrand's counsel at the
    war room: read "Satisfy their design (Britain)", click it and read what opens
    (row 8). (2) Type `who am I fighting` (row 13). (3) Type `what if Massena
    attacks Archduke John` and read the muster; then click a province (Vienna)
    while the tall reply is up and read the province panel (rows 14 and 15).
    (4) Open the Generals screen (G), press G or Esc to close it, then type a
    letter (row 16). (5) F1 and look at the Cabinet's size and its list (row 22).
    (6) Last: type `Ney, attack Mack` (the army joins) and, once Mack has
    retreated, press End Turn and read the army/peril gate BEFORE confirming
    (row 20). Expect: (8) the counsel opens a PEACE confirm pre-loaded with the
    coveted province's cession (Flanders), its acceptance estimate and its 3-DP
    price, and sends NOTHING until confirmed. (13) "the war banner in the lower
    right" (or the ACTIVE WARS banner), not "on the left". (14) the muster names
    the unscouted provinces round Tyrol and gives the band on the men in view
    alone ("on the men in view the odds read …"), not just "unfavorable". (15)
    after the tall reply, clicking a province lowers the reply window so the
    province panel keeps its full body and the march list is in view. (16)
    closing a screen with Esc releases the command line (placeholder "Esc: menu ·
    click to type") so a bare letter does not type into it, and the close hints
    read "Esc closes it (Alt+G while you type)". (22) the Cabinet window is wide
    enough for its court list (a resize grip, a "your courts" row). (20) the
    gate's peril clause names only men who STAND on the field now: no "an enemy
    force of ~29,126 shares the field" about Mack after he has left Swabia (the
    battle's dice decide whether he retreats; if he holds the field the clause may
    rightly stay — judge it against where he stands on the map).
    """
    w = _fresh(boot)
    w.current_turn = 1
    w.actions_remaining = 4
    assert w.get_marshal("Massena").location == "Milan"
    assert w.get_marshal("Mack").location == "Swabia"
    assert w.is_at_war("France", "Britain")

    def counsel():
        from backend.game_logic.diplomatic_advisory import generate_advisory
        advice = generate_advisory(None, "assess_situation", w)
        first = advice["options"][0]
        return {"label": first["label"], "action": first["action"],
                "terms": {k: first["terms"].get(k) for k in ("target_nation", "design_id", "coveted")}}

    def after_load(world):
        assert world.current_turn == 1 and world.get_marshal("Massena").location == "Milan"
    return w, {"counsel": _probe(counsel), "after_load": after_load}


def scene_sea_camp(boot):
    """Rows S14G-17 (the inland term), S14G-29, S14G-30 and S14G-32: turn 8 — the
    Descent camp STAGED at Flanders (Soult 30,000 and Bernadotte 17,000, two
    turns counted, so Britain keeps her squadrons at home in "guard" and the
    blockade is lifted); Holland's contingent under Dumonceau (6,500) just raised
    at Amsterdam — inland, four provinces from a yard; Massena broken at Milan
    (morale 0, in retreat recovery) with Archduke John at Tyrol one frontier off.

    MANIFEST
    Load replay_sea_camp. Do: (a) open the Admiralty (T, then 7), read the camp
    line, the "ready to embark" terms and the chip "Dumonceau, march to
    Normandy", press the chip, and read the action counter. (b) Type `Soult, march
    to Orleanais` (out of the camp) and read the reply; End Turn three times and
    read the income lines and the rail for the blockade's return (it lands a turn
    late: turn 9 has no Blockade line, turn 10 shows about -219g). (c) Press R
    (the dispatch re-read) and read Massena's line. Expect: (a) the failed
    term names the inland corps and the way to a shore — "Dumonceau at Amsterdam —
    inland; nearest shore 2 provinces (Hanover)" (row 17, the failed-term half;
    the ready-line half is on replay_sea_landing); every Admiralty chip names its
    action price before the press ("Dumonceau · 2 AP · 4 turns", the Blockade chip
    "(1 AP)" …) and the march chip carries its camp/pay lines (row 29). (b) the
    order's reply and the Admiralty's staged line say what the camp is holding
    off — "Britain's
    squadrons, held home by the camp, go back to the blockade (trade -62%, crews
    rot, about -320g a turn)" — and the return of the blockade names the broken
    camp as its cause and says it lands a turn late (row 32). (c) the dispatch
    does not advise "two turns of drill" for a man the executor refuses: Massena's
    line reads "Recovering from the rout, N turns — drill once he has reformed."
    (row 30).
    """
    from backend.game_logic import contingent as CG
    from backend.game_logic import naval as NV
    w = _fresh(boot)
    w.current_turn = 8
    w.actions_remaining = 4
    _place(w, Soult="Flanders", Bernadotte="Flanders")
    NV.get_fleet(w, "France")["camp_turns"] = 2
    with _quiet():
        CG.raise_contingent(w, "Holland")
    massena = w.get_marshal("Massena")
    massena.morale = 0
    massena.retreating = True
    massena.retreat_recovery = 0
    massena.retreated_this_turn = True
    _refresh(w)
    with _quiet():
        NV.derive_ai_postures(w)
    assert NV.camp_staged(w, "France") and NV.camp_strength(w, "France") >= 40000
    assert NV.get_fleet(w, "Britain")["posture"] == "guard"
    assert w.get_marshal("Dumonceau").location == "Amsterdam"
    assert w.get_marshal("ArchdukeJohn").location in w.regions["Milan"].adjacent_regions

    def chips():
        with _quiet():
            rep = NV.build_admiralty_report(w)
        return {"expedition_chips": [(c["command"], c.get("cost_note"), c["note"][:90])
                                     for c in rep["expedition_chips"]],
                "chips": [(c["command"], c.get("cost_note")) for c in rep["chips"]]}

    def massena_line():
        from backend.game_logic.dispatch import _derive_danger
        return _derive_danger(massena, w, "France", {})

    def leave_line():
        road = _road(w, "Soult", "Orleanais")
        return NV.camp_leave_line(w, w.get_marshal("Soult"), road)

    def after_load(world):
        assert NV.camp_staged(world, "France")
        assert NV.get_fleet(world, "Britain")["posture"] == "guard"
        assert world.get_marshal("Dumonceau").original_nation == "Holland"
        assert world.get_marshal("Massena").retreating
    return w, {"admiralty": _probe(chips), "massena_dispatch_line": _probe(massena_line),
               "soult_leave_line": _probe(leave_line), "after_load": after_load}


def scene_sea_landing(boot):
    """Rows S14G-17, S14G-18 and S14G-31: turn 10 — Davout, Ney, Lannes and
    Napoleon standing at Moravia (a coastal province Bavaria held: an allied
    shore the Admiralty counts as a place to embark) and Murat inland at
    Dresden; Dumonceau (Holland's 6,500) alone at the Normandy yard with no
    other infantry corps within reach of it, and no Irish ground held yet.

    MANIFEST
    Load replay_sea_landing. Do: (a) open the Admiralty (T, then 7) and read who
    is ready to embark and why. (b) Type `recruit infantry in Normandy` and read
    the refusal; then type `Dumonceau, recruit infantry` (the sighting's second
    step) and read that refusal. (c) Type `Dumonceau, land at Ulster` (or click
    Ulster on the map and press its landing chip) and read the expedition's
    confirm card BEFORE you answer. Expect: (a) the ready line names WHY each
    corps qualifies ("Davout at Moravia — an allied shore", "Dumonceau at
    Normandy — a dockyard of ours"); the Emperor (at Moravia) is not listed as
    ready to embark and his chips do not offer "Land Napoleon" (he does not sail)
    (row 17; the failed-term wording for an inland corps — "Murat at Dresden —
    inland; nearest shore N provinces" — is on replay_sea_camp). (b) the refusal
    says what is true — "Dumonceau commands our foot here, but Holland pays its
    men — recruit into one of our own corps" — and never tells a man already at
    the province to be "marched within reach"; his own order is refused for the
    same reason, once (row 18). (c) the card prices the throw, the failure AND the
    prize: "Ulster is half of the Ireland carve (with Munster) — hold both while
    the war with Britain runs and Britain can be made to erect it at a table; what
    waits ashore is unscouted; under 5,000 men holds no ground" (row 31).
    """
    from backend.game_logic import contingent as CG
    from backend.game_logic import naval as NV
    w = _fresh(boot)
    w.current_turn = 10
    w.actions_remaining = 4
    w.regions["Moravia"].controller = "Bavaria"
    w.invalidate_active_nations_cache()
    _place(w, Davout="Moravia", Ney="Moravia", Lannes="Moravia", Napoleon="Moravia", Murat="Dresden")
    # a transport lifts 15,000 at most: the sighting's corps had been worn down
    # to a size the Admiralty lists as ready (Napoleon's 10,000 is the boot's)
    for name, men in (("Davout", 14000), ("Ney", 13000), ("Lannes", 12500), ("Murat", 11000)):
        w.get_marshal(name).strength = men
    with _quiet():
        CG.raise_contingent(w, "Holland")
    _place(w, Dumonceau="Normandy")
    assert w.regions["Moravia"].controller == "Bavaria"
    assert NV.embark_position_ok(w, w.get_marshal("Davout")), "Moravia should be an embarkation shore"
    assert not NV.embark_position_ok(w, w.get_marshal("Murat")), "Dresden is inland"
    assert w.get_marshal("Dumonceau").location in NV.nation_dockyards(w, "France")

    def admiralty():
        with _quiet():
            rep = NV.build_admiralty_report(w)
        return {"embark_ready": rep["embark_ready"],
                "terms": [(t["text"][:60], t["met"], t["detail"][:140]) for t in rep["expedition_terms"]]}

    def recruit():
        return _execute(_copy(w), {"action": "recruit", "target": "Normandy",
                                   "requested_type": "infantry", "raw_input": "recruit infantry in Normandy"}
                        ).get("message", "")[:300]

    def expedition_quote():
        return _execute(_copy(w), {"action": "naval_expedition", "marshal": "Dumonceau",
                                   "target": "Ulster", "raw_input": "Dumonceau, land at Ulster"}
                        ).get("message", "")[:400]

    def after_load(world):
        assert world.get_marshal("Dumonceau").location == "Normandy"
        assert world.regions["Moravia"].controller == "Bavaria"
    return w, {"admiralty": _probe(admiralty), "recruit_refusal": _probe(recruit),
               "ulster_quote": _probe(expedition_quote), "after_load": after_load}


#  <<MORE-SCENES>>

SCENES = {
    # name: (builder, the S14G rows it serves)
    "liberation": (scene_liberation, [1, 4]),
    "aggressive": (scene_aggressive, [2, 19]),
    "support": (scene_support, [3]),
    "petition": (scene_petition, [5]),
    "envoys": (scene_envoys, [6]),
    "truce_offer": (scene_truce_offer, [7]),
    "counter": (scene_counter, [21, 23]),
    "truce_mission": (scene_truce_mission, [24, 25, 28]),
    "design_peace": (scene_design_peace, [9, 10, 27]),
    "guarded": (scene_guarded, [4, 11, 33]),
    "table": (scene_table, [12, 26]),
    "opening": (scene_opening, [8, 13, 14, 15, 16, 20, 22]),
    "sea_camp": (scene_sea_camp, [17, 29, 30, 32]),
    "sea_landing": (scene_sea_landing, [17, 18, 31]),
}


def _manifest_of(fn):
    """The scene docstring's manifest: everything after the line `MANIFEST`."""
    import re
    # (3.13 strips a docstring's indentation at compile time: match any)
    parts = re.split(r"\n[ \t]*MANIFEST[ \t]*\n", fn.__doc__ or "", maxsplit=1)
    assert len(parts) == 2, f"{fn.__name__}: no MANIFEST block in the docstring"
    lines = [ln.strip() for ln in parts[1].strip().splitlines()]
    return " ".join(ln for ln in lines if ln)


def build(out: pathlib.Path, only=None) -> dict:
    from backend import save_manager as SM
    out.mkdir(parents=True, exist_ok=True)
    boot = _boot()
    record = {}
    manifest = []
    for name, (fn, rows) in SCENES.items():
        if only and name not in only:
            continue
        w, notes = fn(boot)
        check = notes.pop("after_load", None)
        path = out / f"replay_{name}.json"
        with _quiet():
            res = SM.save_game(w, f"replay_{name}", filepath=path)
        assert res.get("success"), (name, res)
        with _quiet():
            back = SM.load_game(path)
        assert back.get("success"), (name, back.get("message"))
        if check is not None:
            check(back["world"])
        record[name] = {"file": path.name, "turn": int(w.current_turn), "rows": rows, **notes}
        text = _manifest_of(fn)
        manifest.append((name, path.name, int(w.current_turn), rows, text))
        print(f"{name:>14}: {path.name} turn {w.current_turn} rows {rows} "
              f"{json.dumps(notes, default=str)[:140]}")
    (out / "scenes.json").write_text(json.dumps(record, indent=1, default=str) + "\n", encoding="utf-8")
    lines = ["# S14h closing re-play — the scenes (DD-B third measure, S14G-1 … 33)", "",
             "Each save loads from \"Load a Campaign…\" under the name `replay_<scene>`. "
             "The fixed game must show the EXPECT clause; the DO clause is the player's act.", ""]
    for name, filename, turn, rows, text in manifest:
        lines += [f"## {name} — `{filename}` (turn {turn}; rows {', '.join('S14G-%d' % r for r in rows)})",
                  "", text, ""]
    (out / "scenes.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    build(pathlib.Path(args.out).resolve(), only or None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
