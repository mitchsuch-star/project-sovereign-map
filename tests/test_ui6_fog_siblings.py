"""UI-6 the typed road's fog doctrine and the defects its sweep found
(Session UI-6, November 13, 2026; rows UI6-X6 and UI6-X9 … UI6-X12 in
`docs/BUG_FIXES.md`).

THE DOCTRINE (`backend/ai/llm_client.py::_askable_enemy_names`, pinned by
`tests/test_crt2_the_name_is_never_replaced.py`): naming an enemy commander
is no fog secret the game keeps — his NAME and his SIDE are public; his
POSITION is the fogged half. The session's first wave read a hidden name as
an invented one (UI6-X2 … X5); the lead ruled those readings were the
doctrine working, and they were reverted. What this module pins instead, on
the real `POST /command` over the shipped 1805 boot:

  the doctrine  a commander out of sight may be answered by name and by
                side (WO-1's refusal names the side, SF7-S7 his rank,
                "No intelligence on Kutuzov's position") — and no reply ever
                carries his province, his strength or any figure of his
                corps.
  UI6-X6   "hold Lorraine until Zorglub is destroyed" MINTED the condition
           "(until Lorraine is destroyed)" (rule 2: a referent the board
           cannot meet is refused) — refused now, free; a pronoun still
           keeps the order's own target, a contraction too.
  UI6-X9   "march to Swabia then attack Kutuzov" (in fog) armed an attack on
           arrival and withheld the "No foe called … is in sight" note an
           invented name gets — the note's rule is "in sight", for him too.
  UI6-X10  "Ney, retreat, Zorglub is attacking" FOUGHT a battle: a reason
           clause whose subject no foe roster held kept its verb, and the
           verb became our order. The reason is never the order, whatever
           its subject.
  UI6-X11  "Ney, attack Kutuzov and Mack" silently dropped Kutuzov and
           fought Mack — the name the sentence gives is the one acted on.
  UI6-X12  Berthier's mock recovery printed the raw key ("Regarding
           ArchdukeCharles … 'Ney, move to ArchdukeCharles'"), and WO-1's
           taught orders did too (R7).

The second wave (builder A15, the same session) — the first wave's sweep
filed these; each is fixed at its cause and pinned below:

  UI6-X14  a delegation on a man out of sight read his LIVE province off the
           roster: "Bernadotte, deal with Kutuzov" scouted Podolia ("~38,000
           troops", an action), "Davout, deal with Kutuzov" answered "Podolia
           is too far to scout (distance: 4)", the literal ASK offered "scout
           Podolia". It observes where WE place him — his last sighting — or
           answers "No intelligence on his position", free.
  UI6-X15  "Attack Marshal Kutuzov" / "everyone attack Kutuzov" answered "No
           marshals in range of Kutuzov" — a verdict on his place. Answered
           as the named road answers him.
  UI6-X16  the charge and the guns dropped the name the sentence gave
           ("Murat, charge Kutuzov and Mack" charged Mack; "Lannes, bombard
           Zorglub" shelled Mack behind a disclosure) and printed his
           distance ("too far for Glorious Charge! Distance: 4"). The X11 rule
           and the SF-V4 ask now cover both; a man out of sight is refused.
  UI6-X17  "support Hohenlohe" said "Hohenlohe is an enemy! Use PURSUE
           instead" at PEACE with Prussia — it says what is true.
  UI6-X18  the reason refusal said "what the enemy is about" of a friend, a
           province, a bridge — it reads its subject's kind.
  UI6-X19  Berthier's shrug offered "'Ney, move to Mack'" (refused) — it offers
           what the board takes, and no road at all to a man out of sight.
  UI6-X20  the readback quoted "hold <commander>" as an order — it reads it as
           `/command` answers it (and `/command` names the commander).
  UI6-X21  the strategic parse stored an UNSEEN neutral commander's live
           province on its target snapshot — it stores his sighting or none.
"""

import contextlib
import io
import json
import random
import re

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import parse_preview as PP
from backend.commands.parser import CommandParser
from backend.display_names import humanize_entity_name
from backend.models.world_state import WorldState


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def road():
    mp = pytest.MonkeyPatch()
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        mp.delenv(key, raising=False)
    mp.setenv("LLM_MODE", "mock")
    prior = (M.world, M.game_state.get("world"), M.parser)
    with _quiet():
        M._reset_world_state()
    snap = json.dumps(M.world.to_dict(), default=str)
    try:
        # one portal for the module (a `with` block): a bare TestClient opens a fresh
        # event loop and socket pair per request, and the censuses post thousands
        # of lines (WinError 10055 under the hook's parallel load)
        with TestClient(M.app) as client:
            yield client, snap
    finally:
        M.world, M.parser = prior[0], prior[2]
        M.game_state["world"] = prior[1]
        PP.invalidate()
        mp.undo()


def _board(snap, without=None, tweak=None):
    with _quiet():
        world = WorldState.from_dict(json.loads(snap))
        if without:
            world.marshals.pop(without, None)
            world._build_marshal_index()
            world.calculate_visibility()
        if tweak is not None:
            tweak(world)
        M._set_active_world(world)
        M.parser = CommandParser(use_real_llm=False)
    PP.invalidate()
    return world


def _send(client, snap, line, without=None, tweak=None):
    """`line` through the real route on a fresh board: the reply, whether a
    French corps moved or bled, and the actions spent."""
    random.seed(1805)
    world = _board(snap, without, tweak)
    corps = {m.name: (m.location, int(m.strength)) for m in world.get_player_marshals()}
    actions = int(world.actions_remaining)
    with _quiet():
        reply = client.post("/command", json={"command": line}).json()
    moved = {m.name: (m.location, int(m.strength)) for m in world.get_player_marshals()} != corps
    return reply, moved, actions - int(world.actions_remaining), world


def _parse(snap, line):
    world = _board(snap)
    with _quiet():
        return M.parser.parse(line, M.get_llm_game_state(), world=world)


def _preview(client, snap, line, tweak=None):
    """The readback of `line` (`GET /parse_preview`) on a fresh board."""
    _board(snap, tweak=tweak)
    with _quiet():
        return client.get("/parse_preview", params={"line": line}).json()


def _last_seen_at(world, name, place):
    """Stage the player's OWN last sighting of `name` at `place` — a
    province out of sight today: the snapshot entry an enemy phase's shown
    action or a lapsed label leaves (`intel_surfaces.record_shown_sightings`
    writes the same entry)."""
    from backend.models.intel import SEEN_TURN_KEY, STALE
    man = world.marshals[name]
    intel = world._intel_entry(place)
    intel.visibility = STALE
    entry = world._build_marshal_snapshot([man], full=False)[0]
    entry[SEEN_TURN_KEY] = int(world.current_turn)
    intel.known_marshals = [entry]


def _kutuzov_last_seen_at_moravia(world):
    _last_seen_at(world, "Kutuzov", "Moravia")


def _murat_blood_up(level):
    def tweak(world):
        world.marshals["Murat"].recklessness = level
    return tweak


def _lannes_commands_guns(world):
    lannes = world.marshals["Lannes"]
    lannes.cavalry = False
    lannes.artillery = True


def _no_leak(client, snap, line, name, reply, tweak=None):
    """No figure of `name`'s corps (his province, his strength) in what the
    reply SAYS that the same line on a board without him does not say too."""
    world = _board(snap)
    man = world.marshals[name]
    body = _said(reply)
    hits = {f for f in _figures(man) if f and f in body}
    if hits:
        absent, _m, _s, _w = _send(client, snap, line, without=name, tweak=tweak)
        hits -= {f for f in hits if f in _said(absent)}
    return hits


def _said(reply):
    """What the reply SAYS to the player — its message, its summary and the
    words of its offered answers. (The board payload rides every reply and
    names every province, so a leak is read in the words, not the JSON.)"""
    parts = [str(reply.get("message") or ""), str(reply.get("action_summary") or "")]
    for option in reply.get("options") or []:
        if isinstance(option, dict):
            parts += [str(option.get("label") or ""), str(option.get("command") or "")]
    return " | ".join(parts)


def _figures(man):
    """Every way a reply could print where he stands or what he fields."""
    strength = int(man.strength)
    return {man.location, humanize_entity_name(man.location), str(strength),
            f"{strength:,}", f"~{strength:,}", f"{strength // 1000}k",
            f"{strength // 1000},000"}


HIDDEN = ("Kutuzov", "Moore", "ArchdukeCharles")


# ═══════════════════════════════════════════════════════════════════════
# THE DOCTRINE — name and side public, place and figures never
# ═══════════════════════════════════════════════════════════════════════

DOCTRINE_TEMPLATES = [
    "{X}, attack Mack", "{X}, retreat", "{X} retreat", "Marshal {X}, retreat",
    "{X}, grant Holland more autonomy", "if {X} is still in Swabia, attack him",
    "Ney, attack Mack if {X} is still standing", "If Ney beat {X}, give him a rente",
    "Ney, attack {X}", "Ney, pursue {X}", "Attack Marshal {X}", "Ney, deal with {X}",
    "Ney, march to Swabia then attack {X}", "Davout, hold Lorraine until {X} arrives",
    "Ney, attack {T}",
]


def _typo(shown):
    return shown[:-1] + ("q" if shown[-1].lower() != "q" else "z")


class TestTheDoctrine:

    @pytest.mark.parametrize("name", HIDDEN)
    def test_no_reply_carries_his_place_or_his_figures(self, road, name):
        """Fifteen shapes of line naming a commander out of sight: none of the
        replies prints his province or a figure of his corps that the same
        line on a board where he never stood does not print as well (a
        muster's own numbers may coincide with his)."""
        client, snap = road
        world = _board(snap)
        man = world.marshals[name]
        assert not PP._View(world).seen.get(name), f"{name} must stand in fog on the boot"
        shown = humanize_entity_name(name)
        for template in DOCTRINE_TEMPLATES:
            line = template.format(X=shown, T=_typo(shown))
            reply, _moved, _spent, _w = _send(client, snap, line)
            body = _said(reply)
            hits = {f for f in _figures(man) if f and f in body}
            if hits:
                absent, _m, _s, _w2 = _send(client, snap, line, without=name)
                hits -= {f for f in hits if f in _said(absent)}
            assert not hits, (line, hits, reply.get("message"))

    def test_the_enemy_addressee_refusal_names_him_and_his_side(self, road):
        """WO-1, as before the session: refused by name and side, nothing
        moved, nothing spent — for a man out of sight as for one in it."""
        client, snap = road
        for line, side in (("Kutuzov, retreat", "Russia"), ("Mack, retreat", "Austria"),
                           ("Moore, attack Mack", "Britain")):
            reply, moved, spent, _w = _send(client, snap, line)
            message = str(reply.get("message") or "")
            assert "does not answer to us" in message and side in message, (line, message)
            assert not moved and spent == 0, line

    def test_the_exact_fogged_name_is_answered_by_name(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Ney, attack Kutuzov")
        assert "No intelligence on Kutuzov's position" in reply["message"], reply["message"]
        assert not moved and spent == 0

    def test_a_premise_on_a_man_out_of_sight_is_refused_without_his_place(self, road):
        client, snap = road
        reply, moved, spent, world = _send(client, snap, "if Kutuzov is still in Swabia, attack him")
        assert reply.get("success") is False and not moved and spent == 0
        assert world.marshals["Kutuzov"].location not in reply["message"]


# ═══════════════════════════════════════════════════════════════════════
# UI6-X6 — a destroyed-referent the board cannot meet is refused
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X6TheDestroyedReferent:

    def test_a_name_on_no_roster_is_refused_never_minted(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Davout, hold Lorraine until Zorglub is destroyed")
        assert "I find no 'Zorglub' in the order of battle" in reply["message"], reply["message"]
        assert "until Lorraine is destroyed" not in reply["message"]
        assert not moved and spent == 0

    @pytest.mark.parametrize("line", [
        "Davout, pursue Mack until he is destroyed",
        "Davout, pursue Mack until it's destroyed",
        "Davout, pursue Mack until Mack's destroyed",
    ])
    def test_a_pronoun_or_a_contraction_keeps_the_orders_target(self, road, line):
        client, snap = road
        reply, _moved, spent, _w = _send(client, snap, line)
        assert "I find no" not in reply["message"], reply["message"]
        assert "(until Mack is destroyed)" in reply["message"], reply["message"]
        assert spent > 0

    def test_the_grammar_refuses_and_keeps_alike(self, road):
        from backend.ai.condition_grammar import parse_condition
        _client, snap = road
        world = _board(snap)
        read = parse_condition("hold lorraine until zorglub is destroyed", "Lorraine",
                               world=world, issuing_marshal="Davout")
        assert read.refusal == {"kind": "unknown_referent", "name": "Zorglub"}
        for clause, expect in (("until they're destroyed", "Mack"), ("until he is destroyed", "Mack"),
                               ("until kutuzov is destroyed", "Kutuzov")):
            read = parse_condition(f"pursue mack {clause}", "Mack", world=world,
                                   issuing_marshal="Davout")
            assert read.refusal is None, (clause, read.refusal)
            assert read.condition == {"until_marshal_destroyed": expect}, (clause, read.condition)


# ═══════════════════════════════════════════════════════════════════════
# UI6-X9 — the arrival attack is armed only on a foe in sight
# ═══════════════════════════════════════════════════════════════════════

NOTE = "is in sight — the march stands, and no attack is armed on arrival"


class TestUI6X9TheArrivalAttackIsArmedInSight:

    @pytest.mark.parametrize("line,named", [
        ("Ney, march to Swabia then attack Kutuzov", "Kutuzov"),
        ("Ney, march to Vienna then attack Archduke Charles", "Archduke Charles"),
        ("Ney, march to Swabia, attack Moore", "Moore"),
        ("Ney, march to Swabia then attack Zorglub", "Zorglub"),
    ])
    def test_a_foe_out_of_sight_arms_nothing_and_is_said(self, road, line, named):
        """A real man in fog takes the road a name on no roster takes: the
        march stands, no attack is armed, the note names him (his name is
        public), and nothing says where he stands."""
        client, snap = road
        parsed = _parse(snap, line)
        assert parsed.get("is_strategic") and parsed.get("strategic_type") == "MOVE_TO", parsed
        assert parsed.get("attack_on_arrival") is False, parsed
        assert parsed.get("arrival_target") is None, parsed
        assert f"No foe called {named} {NOTE}" in str(parsed.get("dropped_arrival_note")), parsed
        reply, _moved, _spent, world = _send(client, snap, line)
        assert f"No foe called {named} {NOTE}" in reply["message"], reply["message"]
        man = world.get_marshal(named.replace(" ", ""))
        if man is not None:
            assert man.location not in reply["message"]

    @pytest.mark.parametrize("line", ["Ney, march to Swabia then attack Mack",
                                      "Ney, march to Swabia then attack Mack and Archduke John"])
    def test_a_foe_in_sight_is_armed_by_the_name_given_first(self, road, line):
        """The control, and the sweep's find: "then attack Mack and Archduke
        John" named Mack first and armed nobody (the whole run resolved to no
        one, and every contact seam fell back to `enemies[0]`)."""
        _client, snap = road
        parsed = _parse(snap, line)
        assert parsed.get("attack_on_arrival") is True, parsed
        assert parsed.get("arrival_target") == "Mack", parsed
        assert not parsed.get("dropped_arrival_note"), parsed

    def test_the_note_reads_the_one_sighting_rule(self, road):
        from backend.commands.proper_name import unseen_commander_named
        from backend.game_logic.intel_surfaces import in_sight
        _client, snap = road
        world = _board(snap)
        player = world.player_nation
        for m in world.marshals.values():
            if m.nation == player:
                continue
            found = unseen_commander_named(humanize_entity_name(m.name).lower(), world, player)
            assert (found is not None) == (not in_sight(world, player, m)), m.name
        # an AI's own march reads its own board: no note on its behalf
        assert unseen_commander_named("kutuzov", world, "Austria") is None


# ═══════════════════════════════════════════════════════════════════════
# UI6-X10 — a reason clause is never an order, whatever its subject
# ═══════════════════════════════════════════════════════════════════════

RETREATS = [
    "Ney, retreat, Zorglub is attacking",
    "Ney, retreat because Zorglub is attacking",
    "Ney, retreat as Zorglub attacks",
    "Ney, retreat, Zorglub attacks",
    "Ney, retreat, General Zorglub is attacking",
    "ney, retreat, zorglub is attacking",
    "Ney, retreat, Zorglub will attack us",
    "Ney, Zorglub is attacking, retreat",
    # the sweep: a friend, a province, a thing, a man in fog
    "Ney, retreat, Davout is attacking",
    "Ney, retreat, Swabia is attacked",
    "Ney, retreat, the bridge is under attack",
    "Ney, retreat, Kutuzov is attacking",
]


class TestUI6X10AReasonIsNeverAnOrder:

    @pytest.mark.parametrize("line", RETREATS)
    def test_the_line_gives_the_retreat_and_nothing_else(self, road, line):
        client, snap = road
        parsed = _parse(snap, line)
        assert (parsed.get("command") or {}).get("action") == "retreat", parsed
        reply, _moved, spent, world = _send(client, snap, line)
        assert not reply.get("battle_report") and not reply.get("muster_preview"), reply.get("message")
        assert spent == 0, (line, spent, reply.get("message"))
        assert "retreats" in str(reply.get("message") or ""), reply.get("message")
        assert world.marshals["Ney"].location != "Swabia"

    def test_another_order_beside_a_report_is_the_order(self, road):
        """"Ney, fortify, Zorglub is attacking" fought too; the fortify
        stands (his objection is his own)."""
        _client, snap = road
        parsed = _parse(snap, "Ney, fortify, Zorglub is attacking")
        assert (parsed.get("command") or {}).get("action") == "fortify", parsed
        parsed = _parse(snap, "Ney, attack Mack, Davout will support you")
        assert (parsed.get("command") or {}).get("action") == "attack", parsed
        assert (parsed.get("command") or {}).get("target") == "Mack", parsed

    @pytest.mark.parametrize("line,clause", [
        ("Ney, Zorglub is attacking", "Zorglub is attacking"),
        ("ney, zorglub is attacking", "zorglub is attacking"),
        ("Ney, Zorglub is about to attack", "Zorglub is about to attack"),
        # the sweep: each FOUGHT a battle, 1 action, before the fix
        ("Ney, Davout is attacking", "Davout is attacking"),
        ("Ney, Swabia is attacked", "Swabia is attacked"),
        ("Ney, the bridge is under attack", "the bridge is under attack"),
    ])
    def test_a_line_that_is_only_a_report_is_refused_free(self, road, line, clause):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        assert reply.get("success") is False and not moved and spent == 0, reply.get("message")
        assert not reply.get("battle_report"), reply.get("message")
        assert f"'{clause}'" in reply["message"], reply["message"]

    @pytest.mark.parametrize("line,action", [
        ("Ney, the time has come to attack Mack", "attack"),     # the order IS the clause
        ("Ney, retreat, Mack is attacking", "retreat"),          # CRT-1's own
        ("Ney, attack Mack as he retreats", "attack"),           # CRT-1's own
    ])
    def test_the_order_in_a_clause_still_stands(self, road, line, action):
        _client, snap = road
        parsed = _parse(snap, line)
        assert (parsed.get("command") or {}).get("action") == action, (line, parsed)

    def test_the_subjects_the_guard_is_handed(self, road):
        """`reason_subjects_in` — what joins the foe roster for ONE sentence:
        beside an order of ours any subject (save a known name a pronoun
        behind the clause may stand for); a line that is only the report,
        any subject unless the clause carries the order in an infinitive;
        never an order verb, a pronoun or a bare imperative."""
        from backend.ai.llm_client import reason_subjects_in
        _client, snap = road
        _board(snap)
        with _quiet():
            gs = M.get_llm_game_state()
        assert reason_subjects_in("Ney, retreat, Zorglub is attacking", gs) == ["Zorglub"]
        assert reason_subjects_in("Ney, retreat, Davout is attacking", gs) == ["Davout"]
        assert reason_subjects_in("Ney, retreat, the bridge is under attack", gs) == ["bridge"]
        assert reason_subjects_in("Ney, Zorglub is attacking", gs) == ["Zorglub"]
        assert reason_subjects_in("Ney, Davout is attacking", gs) == ["Davout"]
        assert reason_subjects_in("Lannes, keep falling back", gs) == []
        # an antecedent kept, an order kept, an imperative kept
        assert reason_subjects_in("Davout, Ney is attacking Mack, support him", gs) == []
        assert reason_subjects_in("Ney, the time has come to attack Mack", gs) == []
        assert reason_subjects_in("Ney, orders are to attack Mack", gs) == []
        assert reason_subjects_in("Ney, retreat, Zorglub attack Mack", gs) == []
        assert reason_subjects_in("Ney, it is time to attack Mack", gs) == []


# ═══════════════════════════════════════════════════════════════════════
# UI6-X11 — the name the sentence gives is the one acted on
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X11TheNameTheSentenceGives:

    @pytest.mark.parametrize("line,named,answer", [
        ("Ney, attack Kutuzov and Mack", "Kutuzov", "No intelligence on Kutuzov's position"),
        ("Ney, attack Archduke Charles and Mack", "ArchdukeCharles",
         "No intelligence on Archduke Charles's position"),
        ("Ney, attack Hohenlohe and Mack", "Hohenlohe", "We are not at war with Prussia"),
        ("Ney, attack Kutuzov, Mack", "Kutuzov", "No intelligence on Kutuzov's position"),
    ])
    def test_the_first_named_man_is_the_target_and_nothing_is_fought(self, road, line, named, answer):
        client, snap = road
        parsed = _parse(snap, line)
        assert (parsed.get("command") or {}).get("target") == named, parsed
        reply, moved, spent, _w = _send(client, snap, line)
        assert answer in reply["message"], reply["message"]
        assert not reply.get("battle_report") and not moved and spent == 0, reply["message"]

    def test_a_name_on_no_roster_there_still_asks(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Ney, attack Zorglub and Mack")
        assert reply["message"].startswith("No foe called Zorglub is in sight"), reply["message"]
        assert not moved and spent == 0

    def test_a_surname_or_a_slip_binds_nobody(self, road):
        """Exact full forms only: a slip keeps CRT-2's near-miss ask (it
        names no hidden man), a surname alone never names a man out of
        sight (R5's surname rule)."""
        from backend.commands.parser import _attack_object_commander
        _client, snap = road
        world = _board(snap)
        roster = [m.name for m in world.marshals.values() if m.nation != world.player_nation]
        assert _attack_object_commander("Ney, attack Kutuzof and Mack", roster) is None
        assert _attack_object_commander("Ney, attack Charles and Mack", roster) is None
        assert _attack_object_commander("Ney, attack the Austrians and Mack", roster) is None
        assert _attack_object_commander("Ney, attack General Kutuzov and Mack", roster) == "Kutuzov"
        assert _attack_object_commander("Ney, attack Mack's flank", roster) == "Mack"


# ═══════════════════════════════════════════════════════════════════════
# UI6-X12 — no raw key in the typed road's own replies (R7)
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X12NoRawKey:

    @pytest.mark.parametrize("line,without", [
        ("Archduke Charles, status", "ArchdukeCharles"),
        ("status Archduke John", None),
        ("Archduke John, status", None),
        ("Archduke Charles, status", None),
    ])
    def test_the_reply_names_him_as_the_map_does(self, road, line, without):
        client, snap = road
        reply, _moved, spent, _w = _send(client, snap, line, without=without)
        message = str(reply.get("message") or "")
        assert not re.search(r"Archduke(?:Charles|John)", message), message
        assert "Archduke" in message, message
        assert spent == 0

    def test_every_mock_template_prints_the_printed_form(self):
        from backend.ai.llm_client import LLMClient
        client = LLMClient(use_real_api=False)
        state = {"marshals": {"Ney": {}, "Davout": {}}, "enemies": {"ArchdukeCharles": {}}}
        for partial in ({"recognized_target": "ArchdukeCharles"}, {"recognized_marshal": "Ney"}, {}):
            for seed in range(12):
                random.seed(seed)
                line = client._berthier_mock_response("xyzzy", state, partial)
                assert "ArchdukeCharles" not in line, (partial, line)


# ═══════════════════════════════════════════════════════════════════════
# UI6-X14 — a delegation observes where WE place him, never where he is
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X14TheDelegationObservesWhereWePlaceHim:
    """A cautious marshal handed a man out of sight ("Bernadotte, deal with
    Kutuzov") was re-issued "scout <his LIVE province>": the delegation took
    the roster's location as the scout's object, so the reply printed where
    he stands and what he fields ("Bernadotte scouts Podolia … Kutuzov
    (Russia): ~38,000 troops", an action spent), or where he stands
    ("Podolia is too far to scout (distance: 4)"), and the literal ASK
    offered "Soult scout Podolia". The scout's object is now where the
    PLAYER places him (`delegation.observe_place` — THE one sighting rule):
    his last sighting, or, with none, "No intelligence on his position",
    free. (Filed by A14 as a strict xfail; fixed by A15.)"""

    @pytest.mark.parametrize("line,name", [
        ("Bernadotte, deal with Kutuzov", "Kutuzov"),      # cautious, his live place in reach
        ("Davout, deal with Kutuzov", "Kutuzov"),          # cautious, his live place out of reach
        ("Bernadotte, deal with Hohenlohe", "Hohenlohe"),  # a neutral court's commander
        ("Soult, deal with Kutuzov", "Kutuzov"),           # literal: the ASK offered "scout Podolia"
        ("Ney, deal with Kutuzov", "Kutuzov"),             # aggressive: the pursuit's own refusal
    ])
    def test_no_report_places_him_so_nothing_is_observed(self, road, line, name):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        assert not _no_leak(client, snap, line, name, reply), (line, reply.get("message"))
        assert f"No intelligence on {name}'s position" in reply["message"], reply["message"]
        assert not moved and spent == 0, (line, spent)
        assert reply.get("state") != "awaiting_clarification", reply["message"]

    def test_his_last_sighting_is_observed_never_his_live_place(self, road):
        client, snap = road
        stage = _kutuzov_last_seen_at_moravia
        # in reach of the sighting: the scout goes there, an action spent
        reply, _m, spent, _w = _send(client, snap, "Bernadotte, deal with Kutuzov", tweak=stage)
        assert "scouts Moravia" in reply["message"], reply["message"]
        assert "Moravia, where Kutuzov was last reported" in reply["message"], reply["message"]
        assert spent == 1
        # out of reach of the sighting: the distance read is the SIGHTING's
        reply2, _m, spent2, _w = _send(client, snap, "Davout, deal with Kutuzov", tweak=stage)
        assert "Moravia is too far to scout" in reply2["message"], reply2["message"]
        assert spent2 == 0
        # the literal ASK offers the sighting as the place to observe
        reply3, _m, spent3, _w = _send(client, snap, "Soult, deal with Kutuzov", tweak=stage)
        assert "Soult scout Moravia" in [o.get("command") for o in reply3.get("options") or []]
        assert spent3 == 0
        for r in (reply, reply2, reply3):
            body = _said(r)
            assert "Podolia" not in body and "38,000" not in body, body

    def test_a_foe_in_sight_is_observed_where_he_stands(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Bernadotte, deal with Mack")
        assert "scouts Swabia" in reply["message"] and spent == 1, reply["message"]
        reply, _m, spent, _w = _send(client, snap, "Soult, deal with Mack")
        assert "Soult scout Swabia" in [o.get("command") for o in reply.get("options") or []]
        assert spent == 0

    def test_observe_place_reads_the_one_sighting_rule(self, road):
        from backend.commands.delegation import detect_delegation, observe_place
        _client, snap = road
        world = _board(snap)
        bern = world.marshals["Bernadotte"]
        assert observe_place(world, "Mack", bern) == "Swabia"
        assert observe_place(world, "Kutuzov", bern) is None
        m = detect_delegation(world, "Bernadotte, deal with Kutuzov")
        assert m.target == "Kutuzov" and m.scout_target is None and m.scout_seen == ""
        m = detect_delegation(world, "Bernadotte, deal with Mack")
        assert m.scout_target == "Swabia" and m.scout_seen == "live"
        _kutuzov_last_seen_at_moravia(world)
        assert observe_place(world, "Kutuzov", bern) == "Moravia"
        m = detect_delegation(world, "Bernadotte, deal with Kutuzov")
        assert m.scout_target == "Moravia" and m.scout_seen == "last"

    def test_the_readback_reads_it_alike(self, road):
        client, snap = road
        for line, name in (("Bernadotte, deal with Kutuzov", "Kutuzov"),
                           ("Soult, deal with Kutuzov", "Kutuzov"),
                           ("Bernadotte, deal with Hohenlohe", "Hohenlohe")):
            reading = _preview(client, snap, line)
            assert reading["kind"] == "refusal", (line, reading)
            assert f"No intelligence on {name}’s position" in reading["refusal"], reading
        reading = _preview(client, snap, "Bernadotte, deal with Kutuzov",
                           tweak=_kutuzov_last_seen_at_moravia)
        assert reading["kind"] == "delegation" and reading["ap"] == 1, reading
        assert "Podolia" not in json.dumps(reading), reading
        reading = _preview(client, snap, "Davout, deal with Kutuzov",
                           tweak=_kutuzov_last_seen_at_moravia)
        assert reading["kind"] == "refusal", reading
        assert "Moravia is too far to scout" in reading["refusal"], reading


# ═══════════════════════════════════════════════════════════════════════
# UI6-X15 — the marshal-less attack answers as the named road does
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X15TheMarshalLessAttack:

    @pytest.mark.parametrize("line,name", [
        ("Attack Marshal Kutuzov", "Kutuzov"),
        ("everyone attack Kutuzov", "Kutuzov"),
        ("attack Kutuzov", "Kutuzov"),
        ("all marshals attack Kutuzov", "Kutuzov"),
        ("the army attacks Kutuzov", "Kutuzov"),
        ("attack Archduke Charles", "ArchdukeCharles"),
    ])
    def test_a_man_out_of_sight_is_answered_by_name_free(self, road, line, name):
        """"No marshals in range of Kutuzov" was a verdict read off his
        live province; and with a corps near him the pick would have named
        the man nearest a place nobody has seen."""
        client, snap = road
        shown = humanize_entity_name(name)
        reply, moved, spent, _w = _send(client, snap, line)
        assert f"No intelligence on {shown}'s position" in reply["message"], reply["message"]
        assert "No marshals in range" not in reply["message"]
        assert not moved and spent == 0 and not reply.get("battle_report"), reply["message"]
        assert not _no_leak(client, snap, line, name, reply), reply["message"]
        reading = _preview(client, snap, line)
        assert reading["kind"] == "refusal" and f"No intelligence on {shown}’s position" in reading["refusal"]

    def test_a_foe_in_sight_keeps_the_pick(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "attack Mack")
        assert "No intelligence" not in reply["message"], reply["message"]
        assert spent == 1 or reply.get("muster_preview") or reply.get("battle_report"), reply["message"]

    def test_his_last_sighting_is_the_picks_place(self, road):
        """A sighting on the record is the player's own intelligence: the
        pick reads it, and the refusal names it — never his live province."""
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "attack Kutuzov",
                                        tweak=_kutuzov_last_seen_at_moravia)
        assert "No marshals in range of Moravia, where Kutuzov was last reported" in reply["message"]
        assert "Podolia" not in _said(reply) and not moved and spent == 0

    def test_the_bare_attack_never_marches_on_a_man_out_of_sight(self, road):
        """The sweep's find (A15): a bare "attack" with no foe in contact
        walked the nearest corps toward the nearest foe on the ROSTER —
        "Bernadotte advances toward ArchdukeCharles: Franconia -> Bohemia,
        Distance to enemy: 1 region", an action spent, the raw key printed.
        The move-toward reads the foes in sight; with none, it says so."""
        def no_foe_in_sight(world):
            for name in ("Mack", "ArchdukeJohn"):
                world.marshals.pop(name, None)
            world._build_marshal_index()
            world.calculate_visibility()
        client, snap = road
        for line in ("attack", "everyone attack"):
            reply, moved, spent, _w = _send(client, snap, line, tweak=no_foe_in_sight)
            message = reply["message"]
            assert message.startswith("No foe is in sight, Sire"), message
            assert "Archduke" not in message and "advances" not in message, message
            assert not moved and spent == 0
        # the control: a foe in contact keeps the CR-6 question
        reply, _m, spent, _w = _send(client, snap, "attack")
        assert "Which marshal shall lead the attack" in reply["message"], reply["message"]

    def test_the_two_helpers(self, road):
        from backend.commands.combat_executor import unseen_target_refusal, where_the_player_places
        _client, snap = road
        world = _board(snap)
        kutuzov, mack = world.marshals["Kutuzov"], world.marshals["Mack"]
        assert where_the_player_places(world, mack) == ("Swabia", "live")
        assert where_the_player_places(world, kutuzov) == (None, "")
        assert unseen_target_refusal(world, mack, "Ney") is None
        refusal = unseen_target_refusal(world, kutuzov, "Ney", "charge")
        assert refusal["message"] == ("No intelligence on Kutuzov's position, Sire. "
                                      "Scout for him before Ney can charge.")
        assert refusal["success"] is False and refusal["variable_action_cost"] == 0
        assert "Podolia" not in refusal["message"]
        _kutuzov_last_seen_at_moravia(world)
        assert where_the_player_places(world, kutuzov) == ("Moravia", "last")


# ═══════════════════════════════════════════════════════════════════════
# UI6-X16 — the charge and the guns: the name the sentence gives
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X16TheChargeAndTheGuns:

    @pytest.mark.parametrize("line,name", [
        ("Murat, charge Kutuzov", "Kutuzov"),
        ("Murat, charge Kutuzov and Mack", "Kutuzov"),
        ("Murat, charge Archduke Charles", "ArchdukeCharles"),
    ])
    def test_a_charge_at_a_man_out_of_sight_reads_nothing_of_his_place(self, road, line, name):
        """"Kutuzov is too far for Glorious Charge! Distance: 4, Range: 2"
        was his distance; "…, charge Kutuzov and Mack" charged MACK."""
        client, snap = road
        shown = humanize_entity_name(name)
        reply, moved, spent, world = _send(client, snap, line, tweak=_murat_blood_up(1))
        message = reply["message"]
        assert f"No intelligence on {shown}'s position" in message, message
        assert "too far" not in message and "Distance" not in message, message
        assert not moved and spent == 0 and not reply.get("battle_report"), message
        assert int(world.marshals["Mack"].strength) == 52000
        reading = _preview(client, snap, line, tweak=_murat_blood_up(1))
        assert reading["kind"] == "refusal" and f"No intelligence on {shown}’s position" in reading["refusal"]

    @pytest.mark.parametrize("line", ["Murat, charge Zorglub", "Murat, charge Zorglub and Mack"])
    def test_a_name_on_no_roster_is_asked_and_the_charge_stays_a_charge(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line, tweak=_murat_blood_up(1))
        assert reply["message"].startswith("No foe called Zorglub is in sight"), reply["message"]
        assert "shall Murat charge him?" in reply["message"], reply["message"]
        assert "Murat, charge Mack" in [o.get("command") for o in reply.get("options") or []]
        assert not moved and spent == 0 and not reply.get("battle_report")

    def test_the_charge_at_a_foe_in_sight_still_rides(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Murat, charge Mack", tweak=_murat_blood_up(1))
        assert reply.get("battle_report") and spent == 1, reply["message"]

    @pytest.mark.parametrize("line,actor", [
        ("Lannes, bombard Kutuzov", "Lannes"),
        ("Lannes, bombard Kutuzov and Mack", "Lannes"),
        ("bombard Kutuzov", "our guns"),
    ])
    def test_the_guns_at_a_man_out_of_sight(self, road, line, actor):
        """"Target out of range … adjacent regions" and "No artillery in
        bombardment range of Kutuzov" were verdicts on his place."""
        client, snap = road
        reply, moved, spent, world = _send(client, snap, line, tweak=_lannes_commands_guns)
        said = (f"No intelligence on Kutuzov's position, Sire. Scout for "
                f"him before {actor} can open fire.")
        # UI6-X25 (widened): a second name is answered, never dropped
        second = ("\n\nMack, named after Kutuzov, was not acted on — one order falls "
                  "on one commander; give him a line of his own." if "and Mack" in line else "")
        assert reply["message"] == said + second, reply["message"]
        assert not moved and spent == 0
        assert int(world.marshals["Mack"].strength) == 52000

    def test_the_guns_ask_for_a_name_on_no_roster_and_fire_at_a_foe_in_sight(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Lannes, bombard Zorglub", tweak=_lannes_commands_guns)
        assert reply["message"].startswith("No foe called Zorglub is in sight"), reply["message"]
        assert "Lannes, bombard Mack" in [o.get("command") for o in reply.get("options") or []]
        assert spent == 0
        reply, _m, spent, _w = _send(client, snap, "Lannes, bombard Mack", tweak=_lannes_commands_guns)
        assert "BOMBARDMENT" in reply["message"] and spent == 1, reply["message"]

    def test_the_blood_up_charge_never_rides_at_a_man_out_of_sight(self, road):
        """At recklessness 3 the charge popup was mounted on the typed man
        (its terrain arm printed his province); at 4 the auto-charge printed
        his distance. A man out of sight takes the ordinary road."""
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Murat, attack Kutuzov", tweak=_murat_blood_up(3))
        assert "blood is up" not in reply["message"], reply["message"]
        assert "No intelligence on Kutuzov's position" in reply["message"]
        assert not moved and spent == 0
        reply, _m, _s, _w = _send(client, snap, "Murat, attack Mack", tweak=_murat_blood_up(3))
        assert "blood is up" in reply["message"], reply["message"]
        reply, moved, spent, _w = _send(client, snap, "Murat, attack Kutuzov", tweak=_murat_blood_up(4))
        assert not reply.get("battle_report") and not moved and spent == 0, reply["message"]
        assert "Distance" not in reply["message"]

    def test_the_object_readers_hear_the_guns_and_the_charge(self, road):
        from backend.commands.parser import _attack_object_commander
        from backend.commands.proper_name import attack_tail, attack_verb
        _client, snap = road
        world = _board(snap)
        roster = [m.name for m in world.marshals.values() if m.nation != world.player_nation]
        assert attack_tail("Lannes, bombard Kutuzov and Mack").strip().startswith("Kutuzov")
        assert attack_verb("Lannes, shell Mack") == "bombard"
        assert attack_verb("Murat, charge Mack") == "charge"
        assert attack_verb("Ney, attack Mack") == "attack"
        assert _attack_object_commander("Lannes, bombard Kutuzov and Mack", roster) == "Kutuzov"
        for line in ("Murat, charge Kutuzov and Mack", "Lannes, bombard Kutuzov and Mack"):
            parsed = _parse(snap, line)
            assert (parsed.get("command") or {}).get("target") == "Kutuzov", (line, parsed)

    def test_the_bare_charge_names_a_cavalryman_and_a_foe_in_sight(self, road):
        """The example named Wellington (on no 1805 roster), led by Ney (no
        cavalryman)."""
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "charge Kutuzov")
        message = reply["message"]
        assert message.startswith("Charge requires a marshal"), message
        assert "Wellington" not in message and "Ney, charge" not in message, message
        assert "'Murat, charge " in message and "Kutuzov" not in message, message
        assert spent == 0
        reading = _preview(client, snap, "charge Kutuzov")
        assert reading["kind"] == "refusal", reading

    def test_the_readback_reads_the_charge_gates(self, road):
        client, snap = road
        reading = _preview(client, snap, "Ney, charge Mack")
        assert reading["kind"] == "refusal" and "cavalry" in reading["refusal"], reading
        reading = _preview(client, snap, "Murat, charge Mack")
        assert reading["kind"] == "refusal" and "victory" in reading["refusal"], reading
        reading = _preview(client, snap, "Murat, charge Mack", tweak=_murat_blood_up(1))
        assert reading["kind"] == "order" and reading["ap"] == 1, reading
        reading = _preview(client, snap, "Murat, charge Zorglub", tweak=_murat_blood_up(1))
        assert reading["kind"] == "unknown_name" and reading["unknown"] == "Zorglub", reading


# ═══════════════════════════════════════════════════════════════════════
# UI6-X17 — a foreign commander is no friend to support, at peace or war
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X17NoFriendToSupport:

    @pytest.mark.parametrize("line,court", [
        ("Ney, support Hohenlohe", "Prussia"),   # out of sight, at peace
        ("Ney, follow Brunswick", "Prussia"),    # in sight, at peace
        ("Ney, support Deroy", "Bavaria"),       # an ally
    ])
    def test_at_peace_he_is_named_and_no_pursuit_is_taught(self, road, line, court):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert f"We are not at war with {court}" in message, message
        assert "enemy" not in message.lower() and "pursue" not in message.lower(), message
        assert not moved and spent == 0
        reading = _preview(client, snap, line)
        assert reading["kind"] == "refusal" and "we are at peace" in reading["refusal"], reading
        assert "pursue" not in reading["refusal"], reading

    def test_at_war_the_pursuit_is_his_road(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Ney, support Kutuzov")
        assert "Kutuzov serves Russia" in reply["message"], reply["message"]
        assert "'Ney, pursue Kutuzov'" in reply["message"], reply["message"]
        assert not moved and spent == 0
        assert not _no_leak(client, snap, "Ney, support Kutuzov", "Kutuzov", reply)
        reading = _preview(client, snap, "Ney, support Kutuzov")
        assert reading["refusal"] == "Kutuzov serves Russia — pursue him, not support", reading

    def test_the_province_verbs_name_their_own_verb(self, road):
        """"Ney, move to Kutuzov" answered "Name the province to scout", and
        "Ney, move to Hohenlohe" taught a pursuit the peace refuses."""
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Ney, move to Kutuzov")
        assert "Name the province to move to, or 'Ney, pursue Kutuzov'" in reply["message"]
        reply, _m, spent, _w = _send(client, snap, "Ney, move to Hohenlohe")
        assert "Hohenlohe is a commander, Sire, not a province" in reply["message"]
        assert "pursue" not in reply["message"] and spent == 0, reply["message"]


# ═══════════════════════════════════════════════════════════════════════
# UI6-X18 — the reason refusal says what its clause is about
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X18TheReasonSaysWhatItIsAbout:

    @pytest.mark.parametrize("line,told", [
        ("Ney, Davout is attacking", "what Davout is about"),          # a friend
        ("Ney, Swabia is attacked", "what passes at Swabia"),          # a province
        ("Ney, the bridge is under attack", "how matters stand"),      # a thing
        ("Ney, Zorglub is attacking", "how matters stand"),            # a name on no roster
        ("Ney, Brunswick is attacking", "what Brunswick is about"),    # a commander at peace
        ("Ney, Mack is attacking", "what the enemy is about"),         # a foe in sight
        ("Ney, Kutuzov is attacking", "what the enemy is about"),      # a foe out of sight
        ("Ney, they are storming the bridge", "what the enemy is about"),
        ("Ney, the Austrians are storming the bridge", "what the enemy is about"),
    ])
    def test_the_refusal_names_its_subjects_kind_and_its_addressee(self, road, line, told):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert f"You have told me {told}, Sire" in message, message
        assert "not what Ney is to do about it" in message, message
        assert not moved and spent == 0
        if "Kutuzov" in line:
            assert not _no_leak(client, snap, line, "Kutuzov", reply), message

    def test_the_reader(self, road):
        from backend.ai.llm_client import reason_clause_subject
        _client, snap = road
        world = _board(snap)
        assert reason_clause_subject("Davout is attacking", world) == ("friend", "Davout")
        assert reason_clause_subject("Swabia is attacked", world) == ("province", "Swabia")
        assert reason_clause_subject("the bridge is under attack", world) == ("thing", "")
        assert reason_clause_subject("as they attack", world) == ("enemy", "")
        assert reason_clause_subject("Archduke Charles is attacking", world) == ("enemy", "")
        assert reason_clause_subject("Hohenlohe is marching", world) == ("commander", "Hohenlohe")
        assert reason_clause_subject("the Prussians are marching", world) == ("court", "Prussia")
        assert reason_clause_subject("the Russians are marching", world) == ("enemy", "")

    @pytest.mark.parametrize("line,copy", [
        ("Ney, Davout is attacking", "That reports on Davout but gives no order"),
        ("Ney, Swabia is attacked", "That reports on Swabia but gives no order"),
        ("Ney, the bridge is under attack", "That is a report, not an order"),
        ("Ney, Mack is attacking", "That reports the enemy but gives no order"),
    ])
    def test_the_readback_reads_it_alike(self, road, line, copy):
        client, snap = road
        reading = _preview(client, snap, line)
        assert reading["kind"] == "refusal" and reading["refusal"] == copy, reading


# ═══════════════════════════════════════════════════════════════════════
# UI6-X19 — Berthier suggests orders the board takes
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X19BerthierSuggestsOrdersTheBoardTakes:

    @pytest.mark.parametrize("line,shown,where", [
        ("status Archduke John", "Archduke John", "Tyrol"),
        ("something about Mack", "Mack", "Swabia"),
    ])
    def test_a_commander_in_sight_is_no_destination(self, road, line, shown, where):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert f"move to {shown}" not in message, message
        assert f"attack {shown}'" in message and f"move to {where}'" in message, message
        assert spent == 0

    def test_the_templates_for_a_man_out_of_sight_and_for_a_friend(self, road):
        from backend.ai.llm_client import LLMClient
        _client, snap = road
        _board(snap)
        with _quiet():
            state = M.get_llm_game_state()
        client = LLMClient(use_real_api=False)
        line = client._berthier_mock_response("xyzzy", state, {"recognized_target": "Kutuzov"})
        assert "move to" not in line and "attack Kutuzov" not in line, line
        assert "Podolia" not in line and "where is Kutuzov" in line, line
        line = client._berthier_mock_response("xyzzy", state, {"recognized_target": "Davout"})
        assert "move to Davout" not in line and "support Davout'" in line, line
        # a cold parse knows the rosters only: the march is dropped
        cold = {"marshals": {"Ney": {}, "Davout": {}}, "enemies": {"Mack": {}}}
        line = client._berthier_mock_response("xyzzy", cold, {"recognized_target": "Mack"})
        assert "move to Mack" not in line and "'Ney, attack Mack'" in line, line

    def test_the_live_sanitiser_refuses_a_commander_for_a_destination(self, road):
        from backend.ai.llm_client import LLMClient
        _client, snap = road
        _board(snap)
        with _quiet():
            state = M.get_llm_game_state()
        client = LLMClient(use_real_api=False)
        with _quiet():
            assert not client._quoted_order_is_taken("Ney, move to Mack", state)
            assert not client._quoted_order_is_taken("Ney, scout Davout", state)
            assert client._quoted_order_is_taken("Ney, move to Swabia", state)
            assert client._quoted_order_is_taken("Ney, march to Mack", state)

    @pytest.mark.parametrize("line,teach,never", [
        ("Hohenlohe, retreat", "We are not at war with Prussia; for word of him", "'attack Hohenlohe'"),
        ("Kutuzov, retreat", "No report of ours places him; for word of him", "'attack Kutuzov'"),
        ("Mack, retreat", "To move against him: 'attack Mack' or 'pursue Mack'", "No report"),
    ])
    def test_the_enemy_addressee_teaches_only_roads_the_board_takes(self, road, line, teach, never):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        assert teach in reply["message"] and never not in reply["message"], reply["message"]
        assert not moved and spent == 0


# ═══════════════════════════════════════════════════════════════════════
# UI6-X20 — "hold <commander>" read as /command answers it
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X20TheHoldReadsAsCommandAnswers:

    @pytest.mark.parametrize("line,name,verb", [
        ("Davout, hold Kutuzov", "Kutuzov", "hold"),
        ("Davout, hold Hohenlohe", "Hohenlohe", "hold"),
        ("Ney, march to Hohenlohe", "Hohenlohe", "march to"),
    ])
    def test_a_commander_out_of_sight_is_no_province(self, road, line, name, verb):
        """`/command` said "Region 'Kutuzov' not found. From Rhineland the
        roads lead to: …" (his name read as a misspelt province); the
        readback quoted a 2-action order."""
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert f"{name} is a commander, Sire, not a province. Name the province to {verb}" in message
        assert "Region '" not in message and not moved and spent == 0, message
        reading = _preview(client, snap, line)
        assert reading["kind"] == "refusal", reading
        assert reading["refusal"] == f"{name} is a commander — name a province", reading

    @pytest.mark.parametrize("line", ["Davout, hold Mack", "Davout, hold Swabia"])
    def test_a_hold_weighs_the_objection_over_its_road(self, road, monkeypatch, line):
        """The bare reading never passed the HOLD's road to the objection
        evaluator, so it read "none" while Davout objected ("A hold at Mack,
        Sire? The odds and the ground are against it")."""
        from backend.commands import executor as executor_mod
        from backend.commands import objection_v2 as ov2
        from backend.commands import strategic_executor as se_mod
        for mod in (executor_mod, se_mod, ov2):
            monkeypatch.setattr(mod, "apply_mood_variance", lambda concern: concern)
        client, snap = road
        reading = _preview(client, snap, line)
        assert reading["kind"] == "order" and reading["objection"] == "possible", reading
        reply, _m, spent, _w = _send(client, snap, line)
        assert reply.get("pending_strategic_objection") or "raises concerns" in reply["message"], \
            reply["message"]
        assert spent == 0

    def test_a_name_that_is_a_province_is_held_as_the_province(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Davout, hold Brunswick")
        assert "Cannot enter Brunswick" in reply["message"] and spent == 0, reply["message"]
        reading = _preview(client, snap, "Davout, hold Brunswick")
        assert reading["kind"] == "refusal" and "Cannot enter Brunswick" in reading["refusal"], reading

    def test_the_garrison_names_a_commander(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Davout, garrison Kutuzov")
        assert reply["message"].startswith("Kutuzov is a commander"), reply["message"]
        assert "Region '" not in reply["message"] and spent == 0

    @pytest.mark.parametrize("line,name", [("scout Kutuzov", "Kutuzov"), ("scout Mack", "Mack")])
    def test_the_marshal_less_scout_names_a_commander(self, road, line, name):
        """The sweep's find (A15): "scout Kutuzov" answered "Region 'Kutuzov'
        not found." — and the readback "Berthier picks or asks"."""
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, line)
        assert reply["message"] == (f"{name} is a commander, Sire, not a province. "
                                    f"Name the province to scout."), reply["message"]
        assert spent == 0
        reading = _preview(client, snap, line)
        assert reading["kind"] == "refusal", reading
        assert reading["refusal"] == f"{name} is a commander — name a province", reading


# ═══════════════════════════════════════════════════════════════════════
# UI6-X21 — no snapshot of an unseen commander's live place
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X21NoSnapshotOfAManUnseen:

    def test_the_parse_stores_his_sighting_or_nothing(self, road):
        from backend.ai.strategic_parser import _classify_target
        _client, snap = road
        world = _board(snap)
        assert _classify_target("Hohenlohe", "Ney", world)["target_snapshot_location"] is None
        # in sight: where he stands; ours: ours to know
        assert _classify_target("Zezschwitz", "Ney", world)["target_snapshot_location"] == "Dresden"
        assert _classify_target("Davout", "Ney", world)["target_snapshot_location"] == "Rhineland"
        # an AI issuer reads its own board (no fog for a court of the AI)
        assert _classify_target("Hohenlohe", "Mack", world)["target_snapshot_location"] == "Silesia"
        # a sighting on the record is the snapshot
        _last_seen_at(world, "Hohenlohe", "Moravia")
        assert _classify_target("Hohenlohe", "Ney", world)["target_snapshot_location"] == "Moravia"

    def test_the_parsed_order_carries_none(self, road):
        _client, snap = road
        parsed = _parse(snap, "Ney, march to Hohenlohe")
        assert parsed.get("target_snapshot_location") is None, parsed


def test_the_readback_reads_the_one_sighting_rule(road):
    """The readback's view is the map's: a foreign corps is in sight exactly
    when the parse state's `enemies` (the fog-filtered roster) shows him."""
    _client, snap = road
    world = _board(snap)
    with _quiet():
        shown = set(M.get_llm_game_state()["enemies"])
    view = PP._View(world)
    assert set(view.seen) == shown, (set(view.seen) ^ shown)
    assert not (set(view.seen) & view.hidden)


# ═══════════════════════════════════════════════════════════════════════
# The third wave (builder A16, the same session) — the second adversarial
# pass found these; each is fixed at its cause and pinned below:
#
#   UI6-X25  the stationary verbs and recruit DROPPED a commander's name and
#            acted in place ("Davout, fortify Kutuzov" dug in at Rhineland);
#            "Ney, attack Mack and Kutuzov" dropped the second name. The name
#            the sentence gives is acted on or the reply says which it read.
#   UI6-X26  "everyone pursue Kutuzov" quoted "8 corps, 14 actions" for an
#            order every corps refused — a quote is what the order will cost.
#   UI6-X27  the proper-name ask's options carried raw roster keys (R7).
#   UI6-X28  "Murat, charge Podolia" named the fogged commander standing
#            there — a province answers as an empty one.
#   UI6-X29  the readback priced charges and bombardments `/command` refuses.
#   UI6-X30  "Ney, Mack is attacking so attack him" was refused as a report.
#   UI6-X31  "Davout, hold BernardimFreire" read a commander's key as "Bern".
# ═══════════════════════════════════════════════════════════════════════

STATIONARY_COMMANDER_LINES = [
    ("Davout, defend Kutuzov", "Kutuzov", "defends", "Davout, defend"),
    ("Davout, fortify Kutuzov", "Kutuzov", "fortifies", "Davout, fortify"),
    ("Davout, entrench Kutuzov", "Kutuzov", "fortifies", "Davout, fortify"),
    ("Davout, dig in Kutuzov", "Kutuzov", "fortifies", "Davout, fortify"),
    ("Davout, recruit at Kutuzov", "Kutuzov", "recruits", "Davout, recruit"),
    ("Davout, drill Kutuzov", "Kutuzov", "drills", "Davout, drill"),
    ("Davout, wait Kutuzov", "Kutuzov", "waits", "Davout, wait"),
    ("Davout, restrain Kutuzov", "Kutuzov", "restrains", "Davout, restrain"),
    ("Davout, build at Kutuzov", "Kutuzov", "builds", "Davout, build"),
    ("Davout, repair Kutuzov", "Kutuzov", "repairs", "Davout, repair"),
    ("Davout, defend Ney", "Ney", "defends", "Davout, defend"),
    ("Davout, fortify Archduke Charles", "Archduke Charles", "fortifies", "Davout, fortify"),
]


class TestUI6X25TheCommanderIsNoPlace:

    @pytest.mark.parametrize("line,man,does,say", STATIONARY_COMMANDER_LINES)
    def test_a_commander_for_the_object_is_refused_free_by_name(self, road, line, man, does, say):
        client, snap = road
        reply, moved, spent, world = _send(client, snap, line)
        message = reply["message"]
        assert message.startswith(f"{man} is a commander, Sire, not a place"), message
        assert f"Davout {does} where he stands; say '{say}'" in message, message
        assert not moved and spent == 0 and reply["success"] is False
        davout = world.marshals["Davout"]
        assert not davout.fortified and int(davout.strength) == int(_board(snap).marshals["Davout"].strength)
        # the readback reads it as `/command` answers it
        reading = _preview(client, snap, line)
        assert reading["kind"] == "refusal" and reading["ok"] is False, reading
        assert f"{man} is a commander" in reading["refusal"], reading

    @pytest.mark.parametrize("name", HIDDEN)
    def test_nothing_of_his_place_or_figures_is_printed(self, road, name):
        client, snap = road
        shown = humanize_entity_name(name)
        for template in ("Davout, fortify {X}", "Davout, defend {X}", "Davout, recruit at {X}"):
            line = template.format(X=shown)
            reply, _moved, _spent, _w = _send(client, snap, line)
            assert "is a commander, Sire, not a place" in reply["message"], reply["message"]
            assert not _no_leak(client, snap, line, name, reply), reply["message"]

    def test_a_province_or_no_object_is_untouched(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Davout, fortify")
        assert "fortifies position at Rhineland" in reply["message"] and spent == 2, reply["message"]
        reply, _m, spent, _w = _send(client, snap, "Davout, fortify Swabia")
        assert "stands at Rhineland, not Swabia" in reply["message"] and spent == 0
        reply, _m, spent, _w = _send(client, snap, "Davout, fortify Rhineland")
        assert "fortifies position at Rhineland" in reply["message"] and spent == 2, reply["message"]
        # a verb whose object grammar takes a commander is out of scope
        reply, _m, _s, _w = _send(client, snap, "Davout, support Ney")
        assert "is a commander, Sire, not a place" not in reply["message"]

    @pytest.mark.parametrize("line,first,dropped", [
        ("Ney, attack Mack and Kutuzov", "Mack", "Kutuzov"),
        ("Ney, attack Kutuzov and Mack", "Kutuzov", "Mack"),
        ("Ney, attack Mack, Kutuzov", "Mack", "Kutuzov"),
        ("Ney, pursue Kutuzov and Moore", "Kutuzov", "Moore"),
    ])
    def test_the_second_name_is_answered_never_dropped(self, road, line, first, dropped):
        """The order acts on the FIRST name (X11) and the reply says the
        rest were read and not acted on — in the same reply."""
        client, snap = road
        reply, _moved, _spent, _w = _send(client, snap, line)
        assert (f"{dropped}, named after {first}, was not acted on "
                "— one order falls on one commander; give him a line of his own.") \
            in reply["message"], reply["message"]
        reading = _preview(client, snap, line)
        assert any(p["role"] == "warn" and f"{dropped}, named after {first}, was not acted on" in p["text"]
                   for p in reading["parts"]), reading

    def test_a_clean_line_and_a_second_order_carry_no_note(self, road):
        client, snap = road
        for line in ("Ney, attack Mack", "Ney, attack Mack and Davout support him",
                     "Ney, attack Kutuzov", "Ney, attack Mack's flank"):
            reply, _m, _s, _w = _send(client, snap, line)
            assert "named after" not in reply["message"], (line, reply["message"])

    def test_the_note_reads_names_only(self, road):
        from backend.commands.proper_name import second_commander_named, second_name_note
        _client, snap = road
        world = _board(snap)
        first, others = second_commander_named("Ney, attack Mack and Kutuzov", world, "Ney")
        assert first.name == "Mack" and [o.name for o in others] == ["Kutuzov"]
        note = second_name_note("Ney, attack Mack, Kutuzov and Moore", world, "Ney")
        assert note.startswith("Kutuzov and Moore, named after Mack, were not acted on")
        for man in (world.marshals["Kutuzov"], world.marshals["Moore"]):
            assert not (_figures(man) & set(re.findall(r"[\w,~]+", note)))
        assert second_commander_named("Ney, attack Mack", world, "Ney") is None
        assert second_commander_named("Ney, attack Mack and Zorglub", world, "Ney") is None


# ═══════════════════════════════════════════════════════════════════════
# UI6-X26 — a quote is what the order will cost
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X26TheCollectiveQuoteIsHonest:

    @pytest.mark.parametrize("line,reason", [
        ("everyone pursue Kutuzov", "No intelligence on Kutuzov's position, Sire."),
        ("everyone march to Kutuzov", "No intelligence on Kutuzov's position, Sire."),
        ("everyone follow Kutuzov", "No intelligence on Kutuzov's position, Sire."),
        ("everyone hold Kutuzov", "Kutuzov is a commander, Sire, not a province."),
        ("everyone scout Kutuzov", "Kutuzov is a commander, Sire, not a province."),
        ("everyone pursue Hohenlohe", "We are not at war with Prussia, Sire"),
        ("everyone support Kutuzov", "Kutuzov serves Russia, an enemy of ours, Sire"),
    ])
    def test_every_corps_refused_for_one_reason_is_that_reason_free(self, road, line, reason):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert message.startswith(reason) and message.endswith("Nothing spent."), message
        assert reply["success"] is False and not moved and spent == 0, message
        assert "corps, " not in message and "actions for the" not in message, message
        assert "\n" not in message, message
        reading = _preview(client, snap, line)
        assert reading["kind"] == "refusal" and reading["ok"] is False, reading

    def test_no_collective_reply_carries_his_place(self, road):
        client, snap = road
        for name in HIDDEN:
            shown = humanize_entity_name(name)
            for verb in ("pursue", "march to", "hold", "follow", "support", "scout"):
                line = f"everyone {verb} {shown}"
                reply, _m, _s, _w = _send(client, snap, line)
                assert not _no_leak(client, snap, line, name, reply), (line, reply["message"])

    def test_an_order_some_corps_take_is_still_priced_as_before(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "everyone pursue Mack")
        head = reply["message"].split("\n")[0]
        assert head.startswith("The order goes to the army, corps by corps"), head
        assert "for the 4 in hand: 'pursue Mack'" in head and spent == 4, reply["message"]

    def test_the_head_prices_only_the_corps_that_took_it(self, road):
        """One corps with no men is no corps of the order."""
        client, snap = road

        def one_is_gone(world):
            world.marshals["Ney"].strength = 0
        reply, _m, _s, _w = _send(client, snap, "everyone pursue Mack", tweak=one_is_gone)
        head = reply["message"].split("\n")[0]
        assert " 7 corps," in head, head


# ═══════════════════════════════════════════════════════════════════════
# UI6-X27 — no raw key in an option the client may print (R7)
# ═══════════════════════════════════════════════════════════════════════

_RAW_KEY = re.compile(r"[a-z][A-Z]")


class TestUI6X27NoRawKeyInTheOptions:

    @pytest.mark.parametrize("line", [
        "Ney, attack Zorglub", "Murat, charge Zorglub", "Lannes, bombard Zorglub",
        "attack Zorglub",
    ])
    def test_the_proper_name_ask_prints_display_names(self, road, line):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, line, tweak=_murat_blood_up(1))
        options = [o for o in reply.get("options") or [] if isinstance(o, dict)]
        assert options, reply["message"]
        for option in options:
            assert not _RAW_KEY.search(str(option.get("label") or "")), option
            assert not _RAW_KEY.search(str(option.get("command") or "")), option
        assert not _RAW_KEY.search(str(reply["message"]).replace("\n", " ")), reply["message"]
        assert spent == 0

    def test_the_display_command_resolves_to_the_same_marshal(self, road):
        _client, snap = road
        world = _board(snap)
        for key in [m.name for m in world.marshals.values() if m.nation != world.player_nation]:
            shown = humanize_entity_name(key)
            raw = _parse(snap, f"Ney, attack {key}")
            disp = _parse(snap, f"Ney, attack {shown}")
            assert (raw.get("command") or {}).get("target") == (disp.get("command") or {}).get("target"), \
                (key, raw, disp)

    def test_the_pursuit_ask_and_the_reissue_helper(self, road):
        from backend.commands.clarification import strategic_reissue_command
        assert strategic_reissue_command("Ney", "PURSUE", "ArchdukeJohn") == "Ney pursue Archduke John"
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Ney, attack ArchdukeJohn")
        assert spent == 0
        options = [o for o in reply.get("options") or [] if isinstance(o, dict)]
        assert options
        for option in options:
            assert not _RAW_KEY.search(str(option.get("command") or "")), option
            assert not _RAW_KEY.search(str(option.get("label") or "")), option

    def test_every_option_builder_prints_display_names(self, road):
        from backend.commands import clarification as C
        _client, snap = road
        world = _board(snap)
        ney = world.marshals["Ney"]
        john = world.marshals["ArchdukeJohn"]
        charles = world.marshals["ArchdukeCharles"]
        made = [
            C.build_attack_target_clarification(world, ney, [john, charles], "attack him"),
            C.build_proper_name_clarification(world, ney, [john, charles], "attack x", "q?"),
            C.build_contact_attack_clarification(
                world, [(ney, john), (world.marshals["Davout"], charles)], "attack"),
            C.build_unknown_name_clarification(
                world, "Johnn", ["ArchdukeJohn", "ArchdukeCharles"], "Johnn, attack", "marshal_suggest"),
        ]
        for built in made:
            assert built is not None
            for option in built["options"]:
                assert not _RAW_KEY.search(str(option.get("label") or "")), option
                assert not _RAW_KEY.search(str(option.get("command") or "")), option


# ═══════════════════════════════════════════════════════════════════════
# UI6-X28 — a province answers as an empty one
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X28TheChargeAtAProvince:

    @pytest.mark.parametrize("fogged,empty", [
        ("Podolia", "Moravia"), ("London", "Bohemia"), ("Carniola", "Silesia"),
    ])
    def test_a_fogged_occupant_is_not_told_by_the_reply(self, road, fogged, empty):
        client, snap = road
        replies = {}
        for province in (fogged, empty):
            reply, moved, spent, _w = _send(client, snap, f"Murat, charge {province}",
                                            tweak=_murat_blood_up(80))
            assert reply["success"] is False and not moved and spent == 0
            replies[province] = reply["message"]
        assert replies[fogged].replace(fogged, "@") == replies[empty].replace(empty, "@"), replies
        for name in HIDDEN:
            assert humanize_entity_name(name) not in replies[fogged], replies

    def test_a_census_over_provinces_with_and_without_a_fogged_man(self, road):
        client, snap = road
        world = _board(snap)
        hidden_at = {world.marshals[n].location for n in HIDDEN}
        seen = {m.location for m in world.get_visible_enemies(world.player_nation)}
        # (a province that is ALSO a commander's name — Brunswick — is the name road's)
        provinces = sorted(r for r in world.regions if r not in seen and r not in world.marshals)[:60]
        assert hidden_at <= set(world.regions)
        provinces = sorted(set(provinces) | hidden_at)
        shapes = set()
        for province in provinces:
            reply, _m, spent, _w = _send(client, snap, f"Murat, charge {province}",
                                         tweak=_murat_blood_up(80))
            assert spent == 0, (province, reply["message"])
            shapes.add(reply["message"].replace(humanize_entity_name(province), "@")
                       .replace(province, "@"))
        assert len(shapes) == 1, shapes

    def test_a_commander_in_sight_in_the_province_is_still_charged(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Murat, charge Swabia", tweak=_murat_blood_up(80))
        assert reply.get("battle_report") and spent == 1, reply["message"]

    def test_the_name_road_is_the_names(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Murat, charge Kutuzov", tweak=_murat_blood_up(80))
        assert "No intelligence on Kutuzov's position" in reply["message"] and spent == 0


# ═══════════════════════════════════════════════════════════════════════
# UI6-X29 — the readback prices only what `/command` takes
# ═══════════════════════════════════════════════════════════════════════

def _both(client, snap, line, tweak=None):
    reading = _preview(client, snap, line, tweak=tweak)
    reply, moved, spent, _w = _send(client, snap, line, tweak=tweak)
    return reading, reply, moved, spent


class TestUI6X29TheReadbackRefusesWhatCommandRefuses:

    @pytest.mark.parametrize("line,said", [
        ("Murat, charge", "Charge requires a target"),
        ("Murat, charge the Austrians", "Charge requires a target"),
        ("Murat, charge Podolia", "Cannot find target 'Podolia'"),
        ("Murat, charge Moravia", "Cannot find target 'Moravia'"),
    ])
    def test_an_armed_charge_with_no_foe_to_ride_at(self, road, line, said):
        client, snap = road
        reading, reply, moved, spent = _both(client, snap, line, tweak=_murat_blood_up(80))
        assert said in reply["message"] and not moved and spent == 0, reply["message"]
        assert reading["kind"] == "refusal" and reading["ok"] is False, reading
        assert reading["ap"] == 0 and "Murat" in reading["refusal"], reading

    @pytest.mark.parametrize("line", ["Ney, bombard", "Ney, bombard Mack", "Lannes, bombard Mack",
                                      "Lannes, bombard"])
    def test_the_guns_verb_of_a_marshal_with_no_guns(self, road, line):
        client, snap = road
        reading, reply, moved, spent = _both(client, snap, line)
        assert "commands no guns" in reply["message"] and not moved and spent == 0, reply["message"]
        assert reading["kind"] == "refusal", reading
        assert "commands no guns" in reading["refusal"], reading

    def test_the_orders_that_ride_are_still_orders(self, road):
        client, snap = road
        for line, tweak in (("Murat, charge Mack", _murat_blood_up(80)),
                            ("Murat, charge Swabia", _murat_blood_up(80)),
                            ("Lannes, bombard Mack", _lannes_commands_guns),
                            ("Ney, attack Mack", None)):
            reading, reply, _m, spent = _both(client, snap, line, tweak=tweak)
            assert reading["kind"] == "order" and reading["ap"] == 1, (line, reading)
            assert spent == 1, (line, reply["message"][:100])

    def test_the_readback_never_prints_the_province_of_a_fogged_man(self, road):
        client, snap = road
        for name in HIDDEN:
            world = _board(snap)
            where = world.marshals[name].location
            reading = _preview(client, snap, f"Murat, charge {where}", tweak=_murat_blood_up(80))
            assert reading["kind"] == "refusal"
            assert humanize_entity_name(name) not in json.dumps(reading), reading


# ═══════════════════════════════════════════════════════════════════════
# UI6-X30 — a reason joined by "so" is a reason, and the order after it
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X30TheConsequenceIsTheOrder:

    @pytest.mark.parametrize("line,action", [
        ("Ney, Mack is attacking Swabia so attack him", "attack"),
        ("Ney, Mack is attacking Swabia, so attack him", "attack"),
        ("Ney, Mack is attacking therefore attack him", "attack"),
        ("Ney, Mack is attacking thus attack him", "attack"),
        ("Ney, Mack is attacking then attack him", "attack"),
        ("Ney, Kutuzov is attacking so retreat", "retreat"),
        ("Ney, Kutuzov is attacking, so retreat", "retreat"),
        ("Ney, Zorglub is attacking so retreat", "retreat"),
        ("Ney, Davout is attacking so retreat", "retreat"),
    ])
    def test_the_order_after_the_reason_is_read(self, road, line, action):
        _client, snap = road
        parsed = _parse(snap, line)
        assert (parsed.get("command") or {}).get("action") == action, parsed

    def test_the_orders_are_carried_out_as_with_the_comma(self, road):
        client, snap = road
        comma, _m, c_spent, _w = _send(client, snap, "Ney, Mack is attacking Swabia, so attack him")
        plain, _m, p_spent, _w = _send(client, snap, "Ney, Mack is attacking Swabia so attack him")
        assert plain.get("battle_report") and bool(comma.get("battle_report"))
        assert c_spent == p_spent
        retreat, moved, _s, _w = _send(client, snap, "Ney, Kutuzov is attacking so retreat")
        assert moved and "retreats from Rhineland" in retreat["message"], retreat["message"]

    @pytest.mark.parametrize("line", [
        "Ney, retreat, Zorglub is attacking", "Ney, retreat so Zorglub is attacking",
        "Ney, retreat as Mack attacks so that we win", "Ney, retreat so Mack is attacking",
        # the sweep: the other words that lead a reason fought too
        "Ney, retreat for Mack is attacking", "Ney, retreat, for Mack is attacking",
        "Ney, retreat given that Mack is attacking", "Ney, retreat considering Mack is attacking",
        "Ney, retreat now Mack is attacking", "Ney, retreat seeing Mack is attacking",
    ])
    def test_the_reasons_own_verb_is_never_the_order(self, road, line):
        client, snap = road
        reply, _moved, _s, _w = _send(client, snap, line)
        assert not reply.get("battle_report"), reply["message"]
        assert "retreats from Rhineland" in reply["message"], reply["message"]

    @pytest.mark.parametrize("line", [
        "Ney, Mack is attacking", "Ney, Mack is attacking so we should retreat",
    ])
    def test_a_line_that_is_only_a_report_is_still_refused_free(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        assert "You have told me what the enemy is about" in reply["message"], reply["message"]
        assert not moved and spent == 0 and not reply.get("battle_report")

    def test_the_guard_ends_a_clause_at_its_consequence_only(self, road):
        from backend.ai.clause_guards import REASON_END_RE, strip_reason_clauses
        assert REASON_END_RE.search("Mack is attacking so attack him")
        assert REASON_END_RE.search("Mack is attacking therefore retreat")
        assert not REASON_END_RE.search("retreat as Mack attacks so that we win")
        text, applied = strip_reason_clauses("Ney, Mack is attacking so attack him", foes=["Mack"])
        # UI6-X36 (re-pointed): the reason's VERB is blanked and the order stands;
        # the subject's NAME stays when a pronoun follows - "him" is Mack, the
        # name the sentence gave. With no pronoun the whole clause is blanked.
        assert applied and "attack him" in text and "is attacking" not in text
        text, applied = strip_reason_clauses("Ney, Mack is attacking so retreat", foes=["Mack"])
        assert applied and "retreat" in text and "Mack" not in text


# ═══════════════════════════════════════════════════════════════════════
# UI6-X31 — a commander's key is no fragment of a province
# ═══════════════════════════════════════════════════════════════════════

class TestUI6X31TheKeyIsNoProvince:

    @pytest.mark.parametrize("verb", ["hold", "march to"])
    def test_every_commander_out_of_sight_gets_the_refusal(self, road, verb):
        """A census over EVERY foreign commander key on the 1805 board: the
        ones out of sight are named (a commander is no province, or no
        intelligence), never read as a destination; the ones in sight keep
        their road (his place is public to us)."""
        client, snap = road
        world = _board(snap)
        in_sight = set(PP._View(world).seen)   # the map's own sighting rule (any court)
        keys = sorted(m.name for m in world.marshals.values() if m.nation != world.player_nation)
        assert len(keys) >= 12
        checked = 0
        for key in keys:
            if key in in_sight or key in world.regions:
                continue
            checked += 1
            reply, moved, spent, w = _send(client, snap, f"Davout, {verb} {key}")
            message = reply["message"]
            assert ("is a commander, Sire, not a province" in message
                    or "No intelligence on" in message), (key, message)
            assert not moved and spent == 0, (key, message)
            assert w.marshals["Davout"].strategic_order is None, (key, message)
        assert checked >= 8, checked

    def test_the_named_case(self, road):
        client, snap = road
        reply, _m, spent, w = _send(client, snap, "Davout, hold BernardimFreire")
        assert "is a commander, Sire, not a province" in reply["message"], reply["message"]
        assert spent == 0 and w.marshals["Davout"].strategic_order is None

    def test_a_province_is_a_word_of_the_phrase(self, road):
        from backend.commands.strategic_executor import _resolve_region_from_phrase
        _client, snap = road
        world = _board(snap)
        assert _resolve_region_from_phrase(world, "BernardimFreire", "France") is None
        assert _resolve_region_from_phrase(world, "Bern", "France") == "Bern"
        assert _resolve_region_from_phrase(world, "On Archduke John At Tyrol", "France") == "Tyrol"
        assert _resolve_region_from_phrase(world, "Bernadotte", "France") == \
            world.marshals["Bernadotte"].location


# ═══════════════════════════════════════════════════════════════════════
# The A17 wave (builder A17, the same session) — UI6-X33 … UI6-X39
# ═══════════════════════════════════════════════════════════════════════

def _armed(world):
    """Murat blood-up (the charge is allowed) and Lannes commanding guns."""
    world.marshals["Murat"].recklessness = 80
    _lannes_commands_guns(world)


def _head(pv):
    return " ".join(str(p.get("text") or "") for p in pv.get("parts") or [])


class TestUI6X33ASoPurposeTailIsNoName:
    """X30 let "so" end a reason clause; behind an order's OWN object "so
    <subject> <verb>" is a purpose tail - cut, it supplies no name."""

    @pytest.mark.parametrize("line, said, never", [
        ("Ney, hold Lorraine so Mack can't pass", "Ney will hold Lorraine", "objects"),
        ("Ney, hold Lorraine so Kutuzov can't pass", "Ney will hold Lorraine", "Kutuzov"),
        ("Ney, march to Lorraine so Mack can't pass", "Ney begins march to Lorraine.", "So Mack"),
        ("Ney, pursue Mack so Kutuzov can't join", "Ney pursues Mack", "Cannot find"),
        ("Ney, retreat to Lorraine so Mack can't pass", "Ney retreats from Rhineland to Lorraine", "cannot be reached"),
    ])
    def test_the_order_keeps_its_own_object(self, road, line, said, never):
        client, snap = road
        reply, _moved, _spent, _w = _send(client, snap, line)
        assert said in reply["message"], reply["message"]
        assert never not in reply["message"], reply["message"]

    def test_the_readback_and_the_order_agree(self, road):
        client, snap = road
        for line, action, place in [
            ("Ney, hold Lorraine so Mack can't pass", "hold", "Lorraine"),
            ("Ney, hold Lorraine so Kutuzov can't pass", "hold", "Lorraine"),
            ("Ney, march to Lorraine so Mack can't pass", "move", "Lorraine"),
            ("Ney, retreat to Lorraine so Mack can't pass", "retreat", ""),
        ]:
            pv = _preview(client, snap, line)
            assert pv["action"] == action, (line, pv)
            assert "Mack" not in _head(pv) and "Kutuzov" not in _head(pv), (line, _head(pv))
            if place:
                assert place in _head(pv), (line, _head(pv))
        reply, _m, spent, _w = _send(client, snap, "Ney, hold Lorraine so Mack can't pass")
        assert spent == 2 and "firmly objects" not in reply["message"]

    @pytest.mark.parametrize("line, first", [
        ("Ney, fortify Kutuzov so attack Mack", "fortify"),
        ("Ney, retreat so attack Mack", "retreat"),
    ])
    def test_two_orders_joined_by_so_are_never_one_acted_and_one_dropped(self, road, line, first):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert "One order at a time" in message and "attack Mack" in message, message
        assert not reply.get("battle_report") and spent == 0, message
        if first == "fortify":
            assert not moved and "fortify Kutuzov" in message
        else:
            assert "retreats from Rhineland" in message

    @pytest.mark.parametrize("line", [
        "Ney, Mack is attacking Swabia so attack him",
        "Ney, Mack is attacking Swabia therefore attack him",
        "Ney, Mack is attacking Swabia thus attack Mack",
    ])
    def test_x30_still_fights_on_a_consequence(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        assert reply.get("battle_report") and moved and spent == 1, reply["message"]

    def test_x30_hence_retreat_still_retreats(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Ney, Mack is attacking Swabia hence retreat")
        assert "retreats from Rhineland" in reply["message"] and not reply.get("battle_report")

    def test_the_guard_cuts_a_tail_and_only_a_tail(self):
        from backend.ai.clause_guards import purpose_tail_spans, strip_reason_clauses
        text = "Ney, hold Lorraine so Mack can't pass"
        assert strip_reason_clauses(text, foes=["Mack"])[0].strip() == "Ney, hold Lorraine"
        assert purpose_tail_spans("Ney, retreat so attack Mack") == []
        assert purpose_tail_spans("Ney, hold Lorraine so that Mack can't pass") == []
        assert purpose_tail_spans("Ney, Mack is attacking Swabia so attack him") == []


class TestUI6X34TheListNoteCoversEveryOrder:
    """CRT-2: the second name of a list is said, whatever the order's verb."""

    @pytest.mark.parametrize("line, second, after", [
        ("Ney, support Davout and Kutuzov", "Kutuzov", "Davout"),
        ("Ney, hold Bern and Kutuzov", "Kutuzov", "Bern"),
        ("Ney, hold Lorraine and Kutuzov", "Kutuzov", "Lorraine"),
        ("Ney, march to Bern and Kutuzov", "Kutuzov", "Bern"),
        ("Ney, march to Swabia and Kutuzov", "Kutuzov", "Swabia"),
        ("Murat, charge Swabia and Kutuzov", "Kutuzov", "Swabia"),
        ("Ney, attack Mack and Archduke John", "Archduke John", "Mack"),
    ])
    def test_the_reply_and_the_readback_say_it(self, road, line, second, after):
        client, snap = road
        note = f"{second}, named after {after}, was not acted on"
        reply, _m, _s, _w = _send(client, snap, line)
        assert note in reply["message"], reply["message"]
        assert note in _head(_preview(client, snap, line)), line

    def test_a_second_order_or_an_unknown_word_is_no_second_name(self, road):
        from backend.commands.proper_name import second_commander_named
        _client, snap = road
        world = _board(snap)
        for line in ("Ney, hold Lorraine and attack Mack", "Ney, march to Swabia and attack Mack",
                     "Ney, hold Lorraine and Zorglub", "Ney, attack Mack then attack Kutuzov",
                     "Ney, hold Lorraine"):
            assert second_commander_named(line, world, "Ney") is None, line

    def test_the_spaced_display_name_is_a_commander_for_the_readback(self, road):
        client, snap = road
        for line in ("Ney, hold Bernardim Freire", "Ney, hold BernardimFreire"):
            pv = _preview(client, snap, line)
            assert pv["kind"] == "refusal" and "is a commander" in _head(pv), (line, pv)
        reply, _m, spent, _w = _send(client, snap, "Ney, hold Bernardim Freire")
        assert "is a commander, Sire, not a province" in reply["message"] and spent == 0


class TestUI6X35ABattleNeverPlacesAManOutOfSight:
    """A foreign commander's "withdraws to <province> after the battle" is the
    fog's: no destination for a man not in sight, never the roster key."""

    @pytest.mark.parametrize("line", ["Murat, charge Archduke John", "Murat, charge Tyrol"])
    @pytest.mark.parametrize("blood", [80, 1])
    def test_the_report_names_him_and_not_his_province(self, road, line, blood, monkeypatch):
        # Row BA, BA-3 (November 15, 2026): this charge opens a day of battle,
        # and the Archduke John's first word brings the Archduke Charles UP
        # again from the province he had just withdrawn to. The row reads the
        # battle's own report and aftermath: the day's seam is held down (what
        # the day then does is pinned in `tests/test_ba3_the_rounds.py`).
        from backend.game_logic import battle_day as _battle_day
        monkeypatch.setattr(_battle_day, "the_day_has_points", lambda: False)
        client, snap = road
        reply, moved, _s, w = _send(client, snap, line, tweak=_murat_blood_up(blood))
        message = reply["message"]
        assert moved and "Archduke Charles withdraws after the battle." in message, message
        assert "ArchdukeCharles withdraws" not in message and "withdraws to Carniola" not in message
        assert w.marshals["ArchdukeCharles"].location == "Carniola"

    def test_the_helper_places_ours_and_the_seen_only(self, road):
        from backend.game_logic.intel_surfaces import whither
        _client, snap = road
        world = _board(snap)
        assert whither(world, world.marshals["Ney"], "Lorraine") == " to Lorraine"
        assert whither(world, world.marshals["Mack"], "Swabia") == " to Swabia"
        assert whither(world, world.marshals["Kutuzov"], "Podolia") == ""
        assert whither(world, world.marshals["Kutuzov"], "") == ""

    def test_a_peace_soil_refusal_names_a_man_out_of_sight_by_his_court(self, road):
        from backend.commands.combat_executor import peace_soil_refusal
        _client, snap = road
        world = _board(snap)
        said = peace_soil_refusal(world.marshals["Ney"], world.marshals["Kutuzov"],
                                  {"owner": "Russia"}, world)["message"]
        assert "Podolia" not in said and "Kutuzov" in said and "serves" in said, said


class TestUI6X36ThePronounIsTheNameTheSentenceGave:
    @pytest.mark.parametrize("line", [
        "Ney, Kutuzov is attacking Swabia so attack him",
        "Ney, Kutuzov is attacking Swabia, attack him",
        "Ney, Archduke Charles is attacking Swabia, pursue him",
    ])
    def test_a_man_out_of_sight_is_refused_free_by_name(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        assert "No intelligence on" in reply["message"], reply["message"]
        assert not moved and spent == 0 and not reply.get("battle_report")
        pv = _preview(client, snap, line)
        assert pv["kind"] == "refusal" and "No intelligence on" in _head(pv), pv

    def test_a_man_in_sight_is_acted_on_never_the_nearest(self, road):
        client, snap = road
        reply, _m, _s, _w = _send(client, snap, "Ney, Archduke John is attacking Swabia so attack him")
        assert "Archduke John" in reply["message"] and "Mack" not in reply["message"].split("Pursue")[0]
        reply, moved, spent, _w = _send(client, snap, "Ney, Mack is attacking Swabia, attack him")
        assert reply.get("battle_report") and moved and spent == 1


def _john_out_of_sight(world):
    """Archduke John stands where Charles does - a province out of sight."""
    world.marshals["ArchdukeJohn"].location = world.marshals["ArchdukeCharles"].location
    world.calculate_visibility()


def _charles_beside_john(world):
    """Both Archdukes in the province in sight at Tyrol."""
    world.marshals["ArchdukeCharles"].location = world.marshals["ArchdukeJohn"].location
    world.calculate_visibility()


class TestUI6X37ATitleTwoMenShareOpensTheAsk:
    # UI6-X46 re-pointed "Ney, bombard Archduke": a marshal with no guns is told
    # so FIRST (free); the title's ask is read by a marshal who commands guns.
    # UI6-X61 (the lead's ruling, reconciling X37 with DD0-S5's pin): a title or
    # name several commanders share acts on its UNIQUE bearer IN SIGHT; with none
    # in sight, or several, it opens the free ask (options only men in sight) -
    # never a non-bearer (X37's real defect was fighting Mack).
    @pytest.mark.parametrize("line", ["Ney, attack Archduke", "Ney, attack the archduke"])
    def test_ask_free_never_the_nearest_foe_when_none_is_in_sight(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line, tweak=_john_out_of_sight)
        assert "No foe of that name is in sight" in reply["message"], reply["message"]
        assert "engaged Mack" not in reply["message"] and "marches on Mack" not in reply["message"]
        assert "Tyrol" not in reply["message"] and "Carniola" not in reply["message"]
        assert not moved and spent == 0 and not reply.get("battle_report")
        assert _preview(client, snap, line, tweak=_john_out_of_sight)["kind"] == "unknown_name"

    @pytest.mark.parametrize("line", ["Ney, attack Archduke", "Ney, attack the archduke"])
    def test_ask_free_when_several_bear_it_in_sight(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line, tweak=_charles_beside_john)
        assert "No foe of that name is in sight" in reply["message"], reply["message"]
        assert "engaged Mack" not in reply["message"] and "marches on Mack" not in reply["message"]
        assert not moved and spent == 0 and not reply.get("battle_report")
        assert _preview(client, snap, line, tweak=_charles_beside_john)["kind"] == "unknown_name"

    @pytest.mark.parametrize("line", ["Ney, attack Archduke", "Ney, attack the archduke",
                                      "Ney, attack Archduke now"])
    def test_the_one_bearer_in_sight_is_the_man_named(self, road, line):
        client, snap = road
        reply, _moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert "Archduke John" in message and "Mack" not in message.split("Pursue him")[0], message
        assert "Carniola" not in message and "Archduke Charles" not in message
        pv = _preview(client, snap, line)
        assert pv["kind"] == "order" and "Archduke John" in _head(pv), pv

    def test_the_guns_at_a_title_read_the_one_in_sight(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Lannes, bombard Archduke",
                                        tweak=_lannes_commands_guns)
        assert "Target out of range" in reply["message"] and not moved and spent == 0
        pv = _preview(client, snap, "Lannes, bombard Archduke", tweak=_lannes_commands_guns)
        assert pv["kind"] == "refusal" and "out of range" in _head(pv), pv
        reply, _m, spent, _w = _send(client, snap, "Lannes, bombard Archduke",
                                     tweak=lambda w: (_lannes_commands_guns(w), _john_out_of_sight(w)))
        assert "No foe of that name is in sight" in reply["message"] and spent == 0

    def test_a_unique_word_and_the_typo_asks_are_as_they_were(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Ney, attack John")
        assert "Archduke John stands at Tyrol" in reply["message"] and spent == 0
        reply, _m, spent, _w = _send(client, snap, "Ney, attack Johnn")
        assert "did you mean Archduke John" in reply["message"] and spent == 0

    def test_the_helper_reads_the_roster(self, road):
        from backend.commands.combat_executor import shared_name_word_in
        _client, snap = road
        world = _board(snap)
        ney = world.marshals["Ney"]
        assert shared_name_word_in("Ney, attack Archduke", world, ney) == "archduke"
        assert shared_name_word_in("Ney, attack Mack", world, ney) == ""
        assert shared_name_word_in("Ney, attack the weakest enemy", world, ney) == ""


class TestUI6X38TheReadbackReadsWhatCommandAnswers:
    @pytest.mark.parametrize("line", ["Lannes, bombard Podolia", "Lannes, bombard Carniola",
                                      "Murat, charge Bavaria"])
    def test_the_armed_lines_are_refused_by_both(self, road, line):
        client, snap = road
        pv = _preview(client, snap, line, tweak=_armed)
        reply, moved, spent, _w = _send(client, snap, line, tweak=_armed)
        assert pv["kind"] == "refusal", pv
        assert not reply.get("success") and not moved and spent == 0, reply["message"]

    def test_a_court_at_peace_beyond_reach_is_refused_not_pursued(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Ney, attack Zezschwitz")
        assert "We are not at war with Saxony" in reply["message"], reply["message"]
        assert not reply.get("success") and not moved and spent == 0
        assert "Pursue him" not in reply["message"] and "Dresden" not in reply["message"]
        assert _preview(client, snap, "Ney, attack Zezschwitz")["kind"] == "refusal"


class TestUI6X39ACommanderIsNoRetreatDestination:
    @pytest.mark.parametrize("line", ["Ney, retreat to Kutuzov", "Ney, retreat to Mack",
                                      "Ney, retreat to Davout", "Ney, retreat to Bernardim Freire",
                                      "all corps retreat to Kutuzov", "all corps retreat to Mack"])
    def test_the_name_is_refused_free_in_x25s_words(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        assert "is a commander, Sire, not a place" in reply["message"], reply["message"]
        assert not reply.get("success") and not moved and spent == 0
        assert "Podolia" not in reply["message"] and "Swabia" not in reply["message"]
        pv = _preview(client, snap, line)
        assert pv["kind"] == "refusal" and "is a commander" in _head(pv), (line, pv)

    @pytest.mark.parametrize("line", ["Ney, retreat for Moore", "Ney, retreat considering Kutuzov",
                                      "Ney, retreat for Mack", "Ney, retreat for three turns"])
    def test_a_reason_word_makes_a_reason_never_a_destination(self, road, line):
        client, snap = road
        reply, moved, _s, _w = _send(client, snap, line)
        assert "retreats from Rhineland to Lorraine" in reply["message"], reply["message"]
        assert "cannot be reached" not in reply["message"] and moved
        assert "Moore" not in _head(_preview(client, snap, line))

    def test_a_province_destination_is_still_a_destination(self, road):
        client, snap = road
        reply, moved, _s, _w = _send(client, snap, "Ney, retreat to Lorraine")
        assert "retreats from Rhineland to Lorraine" in reply["message"] and moved


class TestUI6A17Siblings:
    """The sweep's siblings (CLAUDE.md rule 10): the other tail words and the
    other verbs of a list."""

    @pytest.mark.parametrize("line", [
        "Ney, hold Lorraine in order that Mack can't pass", "Ney, hold Lorraine lest Mack pass",
        "Ney, retreat to Lorraine so Kutuzov can't pass",
    ])
    def test_every_purpose_word_cuts_its_tail(self, road, line):
        client, snap = road
        reply, _m, _s, _w = _send(client, snap, line)
        assert "Lorraine" in reply["message"] and "firmly objects" not in reply["message"], reply["message"]
        assert "Mack" not in _head(_preview(client, snap, line))

    @pytest.mark.parametrize("line, second, after", [
        ("Ney, scout Swabia and Kutuzov", "Kutuzov", "Swabia"),
        ("Ney, follow Davout and Kutuzov", "Kutuzov", "Davout"),
        ("Ney, pursue Mack and Kutuzov", "Kutuzov", "Mack"),
    ])
    def test_scout_follow_and_pursue_lists_say_the_second_name(self, road, line, second, after):
        client, snap = road
        note = f"{second}, named after {after}, was not acted on"
        reply, _m, _s, _w = _send(client, snap, line)
        assert note in reply["message"], reply["message"]
        assert note in _head(_preview(client, snap, line)), line



# ═══════════════════════════════════════════════════════════════════════
# The A18 wave (builder A18, the same session) — UI6-X41 … UI6-X46
# ═══════════════════════════════════════════════════════════════════════

def _then(line):
    """The "then" form of a "so / therefore / thus / hence" line - the road
    the connective must take."""
    return re.sub(r"\s+(?:so|therefore|thus|hence)\s+", " then ", line, count=1)


class TestUI6X41AConsequenceTakesTheThenRoad:
    """"<order> so|therefore|thus|hence <order verb> ..." is two orders joined
    exactly as "then" joins them - never a path of its own (the charge's
    arming gate bypassed, the destination replaced, the object dropped)."""

    @pytest.mark.parametrize("connective", ["so", "therefore", "thus", "hence", "and"])
    @pytest.mark.parametrize("line", ["Murat, charge Mack {c} attack Kutuzov",
                                      "Murat, charge Mack {c} attack Mack"])
    def test_the_charge_gate_holds(self, road, connective, line):
        client, snap = road
        line = line.format(c=connective)
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert "needs one victory first" in message, message
        assert not moved and spent == 0 and not reply.get("battle_report"), message
        assert "MUSTER" not in message
        pv = _preview(client, snap, line)
        assert pv["kind"] == "refusal" and "one victory" in _head(pv), (line, pv)

    @pytest.mark.parametrize("line", ["Murat, charge Mack, attack Kutuzov"])
    def test_the_comma_form_holds_the_gate_too(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        assert "needs one victory first" in reply["message"] and not moved and spent == 0
        assert "one victory" in _head(_preview(client, snap, line))

    @pytest.mark.parametrize("connective", ["so", "therefore"])
    def test_an_armed_charge_is_the_then_forms(self, road, connective):
        client, snap = road
        line = f"Murat, charge Mack {connective} attack Kutuzov"
        a, a_moved, a_spent, _w = _send(client, snap, line, tweak=_murat_blood_up(80))
        b, b_moved, b_spent, _w = _send(client, snap, _then(line), tweak=_murat_blood_up(80))
        assert a["message"] == b["message"], (a["message"], b["message"])
        assert (a_moved, a_spent) == (b_moved, b_spent)
        assert "GLORIOUS CHARGE" in a["message"].upper()

    @pytest.mark.parametrize("line", [
        "Ney, march to Lorraine so attack Mack", "Ney, march to Lorraine therefore attack Mack",
        "Ney, march to Lorraine thus attack Mack", "Ney, march to Lorraine hence attack Mack",
        "Ney, march to Swabia so attack Mack", "Ney, march to Swabia therefore attack Mack",
        "Ney, hold Lorraine so retreat", "Ney, hold Lorraine thus retreat",
        "Ney, hold Lorraine hence retreat", "Ney, hold Lorraine therefore retreat",
        "Ney, hold Lorraine retreat", "Ney, hold Lorraine so attack Kutuzov",
        "Ney, hold Lorraine so attack Mack", "Ney, fortify so retreat",
    ])
    def test_the_line_is_the_then_lines_reply_and_readback(self, road, line):
        client, snap = road
        then = _then(line) if re.search(r"\b(?:so|therefore|thus|hence)\b", line) else re.sub(
            r"\s+(retreat)$", r" then \1", line)
        a, a_moved, a_spent, _w = _send(client, snap, line)
        b, b_moved, b_spent, _w = _send(client, snap, then)
        assert a["message"] == b["message"], (a["message"], b["message"])
        assert (a_moved, a_spent) == (b_moved, b_spent), line
        pa, pb = _preview(client, snap, line), _preview(client, snap, then)
        assert (pa["kind"], pa.get("action")) == (pb["kind"], pb.get("action")), (pa, pb)
        assert _head(pa) == _head(pb), (_head(pa), _head(pb))

    def test_the_destination_and_the_object_are_kept(self, road):
        client, snap = road
        reply, _m, spent, w = _send(client, snap, "Ney, march to Lorraine so attack Mack")
        assert "begins march to Lorraine" in reply["message"] and spent == 2
        assert "Mack blocks the path" not in reply["message"]
        pv = _preview(client, snap, "Ney, march to Lorraine so attack Mack")
        assert "Lorraine" in _head(pv), pv
        reply, moved, spent, w = _send(client, snap, "Ney, hold Lorraine so retreat")
        assert "Ney will hold Lorraine" in reply["message"] and "firmly objects" not in reply["message"]
        assert "retreat" in reply["message"] and moved
        reply, _m, spent, _w = _send(client, snap, "Ney, hold Lorraine so attack Kutuzov")
        assert "Ney will hold Lorraine" in reply["message"], reply["message"]
        assert "is a commander" not in reply["message"] and "Podolia" not in reply["message"]

    @pytest.mark.parametrize("line", ["Ney, hold Lorraine so Mack can't pass",
                                      "Ney, Mack is attacking Swabia so attack him"])
    def test_a_purpose_tail_and_a_report_keep_their_readings(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        if "Lorraine" in line:
            assert "Ney will hold Lorraine" in reply["message"] and spent == 2
        else:
            assert reply.get("battle_report") and moved and spent == 1

    def test_the_helper_rewrites_an_order_and_never_a_report_or_a_purpose(self):
        from backend.ai.clause_guards import consequence_as_then
        foes = ["Mack", "Kutuzov"]
        assert consequence_as_then("Ney, hold Lorraine so retreat", foes) == "Ney, hold Lorraine then retreat"
        assert consequence_as_then("Ney, hold Lorraine retreat", foes) == "Ney, hold Lorraine then retreat"
        for line in ("Ney, hold Lorraine so Mack can't pass", "Ney, Mack is attacking Swabia so attack him",
                     "Ney, retreat", "Ney, defend and retreat", "Ney, hold Lorraine and retreat",
                     "Ney, hold Lorraine so that Mack can't pass"):
            assert consequence_as_then(line, foes) == line, line


class TestUI6X42ACommanderIsNoRetreatObject:
    """X39's refusal for every commander-shaped object of retreat / fall back /
    withdraw - with or without "to" / "from" - free, never his place."""

    @pytest.mark.parametrize("line", [
        "Ney, retreat Kutuzov", "Ney, retreat Mack", "Ney, retreat Moore",
        "Ney, retreat from Kutuzov", "Ney, retreat from Mack", "Ney, fall back Kutuzov",
        "Ney, withdraw Kutuzov", "Ney, withdraw from Mack", "Ney, fall back to Mack",
        "Ney, fall back from Kutuzov", "Ney, retreat Davout",
    ])
    def test_the_name_is_refused_free_in_x39s_words(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert "is a commander, Sire, not a place" in message, message
        assert not reply.get("success") and not moved and spent == 0, message
        for leak in ("Podolia", "Swabia", "Lorraine instead", "cannot be reached", "chase", "give chase"):
            assert leak not in message, (leak, message)
        pv = _preview(client, snap, line)
        assert pv["kind"] == "refusal" and "is a commander" in _head(pv), (line, pv)

    @pytest.mark.parametrize("line", ["Ney, retreat to Archduke", "Ney, retreat from Archduke",
                                      "Ney, fall back to Archduke"])
    def test_a_title_two_men_share_is_refused_by_name(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert "Archduke is a title more than one commander bears" in message, message
        assert not reply.get("success") and not moved and spent == 0
        assert "Carniola" not in message and "Tyrol" not in message
        pv = _preview(client, snap, line)
        assert pv["kind"] == "refusal" and "Archduke is a title" in _head(pv), (line, pv)

    @pytest.mark.parametrize("line", ["Ney, retreat to Lorraine", "Ney, retreat from Rhineland",
                                      "Ney, fall back to Lorraine", "Ney, retreat", "Ney, withdraw",
                                      "Ney, retreat now", "Ney, fall back toward the Rhine"])
    def test_a_province_or_no_object_is_as_it_was(self, road, line):
        client, snap = road
        reply, moved, _s, _w = _send(client, snap, line)
        assert "is a commander" not in reply["message"] and "is a title" not in reply["message"]
        pv = _preview(client, snap, line)
        assert pv["kind"] != "refusal" or "is a commander" not in _head(pv), (line, pv)

    def test_the_general_retreat_names_a_title_too(self, road):
        client, snap = road
        pv = _preview(client, snap, "all corps retreat to Archduke")
        assert pv["kind"] == "refusal" and "title" in _head(pv), pv


class TestUI6X43ACompoundSubjectsPronounIsNoOneMan:
    @pytest.mark.parametrize("line, pronoun, names", [
        ("Ney, Kutuzov and Mack are coming so attack him", "him", ("Kutuzov", "Mack")),
        ("Ney, Mack and Kutuzov are coming so attack him", "him", ("Mack", "Kutuzov")),
        ("Ney, Mack and Kutuzov are coming so attack them", "them", ("Mack", "Kutuzov")),
        ("Ney, Kutuzov and Mack are coming so attack them", "them", ("Kutuzov", "Mack")),
        ("Ney, Mack and Archduke John are coming so attack them", "them", ("Mack", "Archduke John")),
        ("Ney, Mack and Kutuzov are marching, attack him", "him", ("Mack", "Kutuzov")),
        ("Ney, Mack and Kutuzov are coming so pursue him", "him", ("Mack", "Kutuzov")),
    ])
    def test_refused_free_naming_both(self, road, line, pronoun, names):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert f"'{pronoun}'" in message and all(n in message for n in names), message
        assert not reply.get("success") and not moved and spent == 0, message
        assert not reply.get("battle_report")
        assert "Podolia" not in message and "Swabia" not in message
        pv = _preview(client, snap, line)
        assert pv["kind"] == "refusal" and all(n in _head(pv) for n in names), (line, pv)

    def test_one_subject_still_binds_and_a_name_still_names(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Ney, Mack is attacking Swabia so attack him")
        assert reply.get("battle_report") and moved and spent == 1
        reply, moved, spent, _w = _send(client, snap, "Ney, Mack and Kutuzov are coming so attack Mack")
        assert reply.get("battle_report") and moved and spent == 1, reply["message"]

    def test_the_reading_names_the_list_and_the_pronoun(self):
        from backend.ai.clause_guards import compound_pronoun_reading
        foes = ["Mack", "Kutuzov", "Archduke John", "ArchdukeJohn"]
        assert compound_pronoun_reading("Ney, Kutuzov and Mack are coming so attack him", foes) == (
            ["Kutuzov", "Mack"], "him", "attack")
        assert compound_pronoun_reading("Ney, Mack is coming so attack him", foes) is None
        assert compound_pronoun_reading("Ney, attack Mack and Kutuzov", foes) is None


class TestUI6X44APurposeTailNamesAreNoObjects:
    @pytest.mark.parametrize("line", [
        "Ney, hold Lorraine so Mack and Kutuzov can't pass",
        "Ney, hold Lorraine so Kutuzov and Mack can't pass",
        "Ney, hold Lorraine lest Mack and Kutuzov pass",
        "Ney, march to Lorraine so Mack and Kutuzov can't pass",
        "Ney, hold Lorraine in order that Mack and Kutuzov can't pass",
    ])
    def test_no_second_name_note(self, road, line):
        client, snap = road
        reply, _m, _s, _w = _send(client, snap, line)
        assert "not acted on" not in reply["message"], reply["message"]
        assert "Lorraine" in reply["message"]
        assert "not acted on" not in _head(_preview(client, snap, line)), line

    def test_a_real_list_before_the_tail_is_still_noted(self, road):
        client, snap = road
        line = "Ney, hold Lorraine and Kutuzov so Mack can't pass"
        reply, _m, _s, _w = _send(client, snap, line)
        note = "Kutuzov, named after Lorraine, was not acted on"
        assert note in reply["message"] and "Mack, named" not in reply["message"], reply["message"]
        assert note in _head(_preview(client, snap, line))


class TestUI6X45TheClausePronounBindsForEveryVerb:
    @pytest.mark.parametrize("line", [
        "Ney, Brunswick is marching so pursue him", "Ney, Brunswick is marching, pursue him",
        "Ney, Brunswick is marching so attack him",
    ])
    def test_a_commander_that_is_also_a_province_is_the_referent(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        assert "We are not at war with Prussia" in reply["message"], reply["message"]
        assert "'Him'" not in reply["message"] and not moved and spent == 0
        pv = _preview(client, snap, line)
        assert pv["kind"] == "refusal" and "We are not at war with Prussia" in _head(pv), (line, pv)

    def test_support_and_scout_read_him_as_the_man(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Ney, Brunswick is marching so support him")
        assert "support is for your own marshals" in reply["message"] and spent == 0
        for line in ("Ney, Brunswick is marching so scout him", "Ney, Brunswick is marching, scout him"):
            reply, moved, spent, _w = _send(client, snap, line)
            assert "Brunswick is a commander, Sire, not a province" in reply["message"], reply["message"]
            assert spent == 0 and not moved and "scouts Brunswick" not in reply["message"]
            pv = _preview(client, snap, line)
            assert pv["kind"] == "refusal" and "Brunswick is a commander" in _head(pv), (line, pv)

    @pytest.mark.parametrize("line", ["Ney, Mack is marching so pursue him",
                                      "Ney, Archduke John is marching so pursue him"])
    def test_a_man_in_sight_is_pursued_by_name(self, road, line):
        client, snap = road
        reply, _m, _s, _w = _send(client, snap, line)
        assert "Cannot find" not in reply["message"] and "'Him'" not in reply["message"], reply["message"]

    def test_the_typed_scout_of_a_province_that_is_a_man_reads_as_it_is_taken(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Ney, scout Brunswick")
        pv = _preview(client, snap, "Ney, scout Brunswick")
        assert "Ney scouts Brunswick" in reply["message"] and spent == 1
        assert pv["kind"] == "order" and "Brunswick" in _head(pv), pv


class TestUI6X46TheGunsAnswerAgrees:
    """A marshal with no guns cannot bombard: ONE answer, first, free - the
    range, the sighting and the target never get a say."""

    @pytest.mark.parametrize("line", ["Lannes, bombard Podolia", "Lannes, bombard Kutuzov",
                                      "Lannes, bombard Moore", "Lannes, bombard Mack",
                                      "Lannes, bombard Swabia", "Lannes, bombard Carniola",
                                      "Ney, bombard Kutuzov", "Ney, bombard Podolia"])
    def test_both_say_he_commands_no_guns(self, road, line):
        client, snap = road
        pv = _preview(client, snap, line)
        reply, moved, spent, _w = _send(client, snap, line)
        assert "commands no guns" in reply["message"], reply["message"]
        assert not reply.get("success") and not moved and spent == 0
        assert pv["kind"] == "refusal" and "commands no guns" in _head(pv), (line, pv)
        for leak in ("Range:", "Distance", "Targets in range", "No intelligence", "give chase"):
            assert leak not in reply["message"], (leak, reply["message"])

    @pytest.mark.parametrize("line, said", [
        ("Lannes, bombard Podolia", "Target out of range"),
        ("Lannes, bombard Kutuzov", "No intelligence on Kutuzov"),
    ])
    def test_a_marshal_with_guns_meets_the_range_and_the_sighting(self, road, line, said):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line, tweak=_lannes_commands_guns)
        assert said in reply["message"] and "commands no guns" not in reply["message"]
        assert not moved and spent == 0

    def test_a_counter_punch_is_not_spent_on_a_refusal(self, road):
        client, snap = road

        def punch(world):
            world.marshals["Lannes"].counter_punch_available = True
        reply, _moved, spent, world = _send(client, snap, "Lannes, bombard Mack", tweak=punch)
        assert "commands no guns" in reply["message"] and spent == 0
        assert world.marshals["Lannes"].counter_punch_available is True


# ═══════════════════════════════════════════════════════════════════════
# The A19 wave (builder A19, the same session) — UI6-X54 … UI6-X62
# ═══════════════════════════════════════════════════════════════════════

def _both_armed(world):
    """Murat blood-up at 100 (the charge is allowed) and Lannes commanding guns."""
    world.marshals["Murat"].recklessness = 100
    _lannes_commands_guns(world)


class TestUI6X54TheCompoundPronounIsRefusedForEveryJoinerAndVerb:
    """"Ney, Mack and Kutuzov are attacking so attack him" fought MACK for 1 AP
    (and "so bombard him" ran an attack): the clause split the line before the
    pronoun was read. The refusal is read on the typed line, first."""

    @pytest.mark.parametrize("line, verb", [
        ("Ney, Mack and Kutuzov are attacking so attack him", "attack"),
        ("Ney, Kutuzov and Mack are attacking so attack him", "attack"),
        ("Ney, Mack with Kutuzov are attacking so attack him", "attack"),
        ("Ney, Mack plus Kutuzov are attacking so attack him", "attack"),
        ("Ney, Mack & Kutuzov are attacking so attack him", "attack"),
        ("Ney, Mack and the Archduke are attacking so attack him", "attack"),
        ("Ney, Mack and Kutuzov are attacking; attack him", "attack"),
        ("Ney, Mack and Kutuzov are attacking therefore attack him", "attack"),
        ("Ney, Mack and Kutuzov are attacking thus attack him", "attack"),
        ("Ney, Mack and Kutuzov are attacking hence attack him", "attack"),
        ("Ney, Mack and Kutuzov are attacking then attack him", "attack"),
        ("Ney, Mack and Kutuzov are attacking and attack him", "attack"),
        ("Ney, Mack and Kutuzov are fighting so attack them", "attack"),
        ("Ney, Mack and Kutuzov have attacked Swabia so hold him", "hold"),
        ("Ney, Mack and Kutuzov are in Swabia so fortify him", "fortify"),
        ("Ney, Mack and Kutuzov are attacking so bombard him", "bombard"),
        ("Ney, Mack and Kutuzov are attacking so scout him", "scout"),
        ("Ney, Mack and Kutuzov are attacking so support him", "support"),
        ("Ney, Mack and Kutuzov are attacking so retreat from him", "retreat"),
        ("Ney, Mack and Kutuzov are attacking so charge him", "charge"),
        ("Ney, Mack and Kutuzov are attacking so pursue him", "pursue"),
        ("Ney, Mack and Kutuzov are marching so attack him", "attack"),
        ("Ney, Mack and Kutuzov are advancing so attack him", "attack"),
    ])
    def test_refused_free_naming_every_man_and_the_verb(self, road, line, verb):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line, tweak=_both_armed)
        message = reply["message"]
        assert not reply.get("success") and not moved and spent == 0, message
        assert not reply.get("battle_report") and "MUSTER" not in message, message
        assert "Mack" in message and verb in message, message
        assert re.search(r"Kutuzov|Archduke", message), message
        assert "Podolia" not in message and "Swabia is" not in message
        assert "Nothing has been relayed" in message
        pv = _preview(client, snap, line, tweak=_both_armed)
        assert pv["kind"] == "refusal" and "Mack" in _head(pv) and verb in _head(pv), (line, pv)

    def test_a_friend_and_a_foe_get_the_same_refusal(self, road):
        client, snap = road
        for line in ("Ney, Mack and Davout are marching so attack him",
                     "Ney, Ney and Mack are marching so attack him",
                     "Ney, Mack and Davout are attacking so attack him"):
            reply, moved, spent, _w = _send(client, snap, line)
            message = reply["message"]
            assert "is a commander, Sire, not a province" not in message, message
            assert "could be" in message and "Mack" in message, message
            assert not moved and spent == 0 and not reply.get("success")
            pv = _preview(client, snap, line)
            assert pv["kind"] == "refusal" and "Mack" in _head(pv), (line, pv)

    @pytest.mark.parametrize("line", [
        "Ney, Mack is attacking Swabia so attack him",         # one subject: it binds
        "Ney, Mack and Kutuzov are attacking so attack Mack",  # a NAME, not a pronoun
        "Ney, attack Mack and Kutuzov",
        "Ney, Davout and Soult are marching so attack him",    # no foe in the list
    ])
    def test_one_subject_a_name_or_no_foe_is_not_this_refusal(self, road, line):
        client, snap = road
        reply, _m, _s, _w = _send(client, snap, line)
        assert "could be" not in reply["message"], reply["message"]
        assert "'them' is" not in reply["message"], reply["message"]

    def test_a_compound_report_with_a_named_object_is_the_order(self, road):
        """The report's subjects are no order's object: "Mack and Kutuzov are marching so
        attack Mack" is "attack Mack" (it read "Mack is a commander, not a province")."""
        client, snap = road
        for line in ("Ney, Mack and Kutuzov are marching so attack Mack",
                     "Ney, Mack and Kutuzov are attacking so attack Mack"):
            reply, moved, spent, _w = _send(client, snap, line)
            assert "is a commander, Sire, not a province" not in reply["message"], reply["message"]
            assert reply.get("battle_report") and moved and spent == 1, reply["message"]
            assert "attack Mack" in _head(_preview(client, snap, line))

    def test_a_stray_auxiliary_is_no_name_in_the_list(self, road):
        client, snap = road
        reply, _m, spent, _w = _send(client, snap, "Ney, Mack and Kutuzov, are attacking so attack him")
        assert "could be Mack or Kutuzov, Sire" in reply["message"] and spent == 0, reply["message"]

    def test_the_reading_takes_the_friends_the_titles_and_every_joiner(self):
        from backend.ai.clause_guards import compound_pronoun_reading as read
        foes = ["Mack", "Kutuzov", "Archduke John", "ArchdukeJohn"]
        friends = ["Ney", "Davout"]
        assert read("Ney, Mack and Davout are marching so attack him", foes, friends) == (
            ["Mack", "Davout"], "him", "attack")
        assert read("Ney, Mack plus Kutuzov are attacking; attack him", foes, friends) == (
            ["Mack", "Kutuzov"], "him", "attack")
        assert read("Ney, Mack and the Archduke are attacking so bombard them", foes, friends) == (
            ["Mack", "Archduke"], "them", "bombard")
        assert read("Ney, Davout and Ney are marching so attack him", foes, friends) is None
        assert read("Ney, Mack is attacking so attack him", foes, friends) is None


class TestUI6X55AConsequenceTakesExactlyTheThenRoad:
    """The rewrite of "so / therefore / thus / hence <order>" to "then" ran
    after the typed then's neighbours (the tactical "move to" promoted to a
    march, the arrival idiom): "Ney, move to Lorraine so attack Mack" was a
    1-AP plain move with the attack relayed while "... then attack Mack" was a
    2-AP march carrying it. The rewrite is the FIRST thing the parse does."""

    HEADS = [("Ney", "march to Lorraine"), ("Ney", "move to Lorraine"), ("Ney", "move to Swabia"),
             ("Ney", "hold Lorraine"), ("Ney", "attack Mack"), ("Murat", "charge Mack"),
             ("Lannes", "bombard Mack"), ("Ney", "bombard Mack"), ("Ney", "pursue Mack"),
             ("Ney", "support Davout"), ("Ney", "scout Swabia"), ("Ney", "fortify"),
             ("Ney", "retreat"), ("Ney", "fall back"), ("Ney", "fall back to Lorraine")]
    TAILS = ["attack Mack", "charge Mack", "bombard Mack", "march to Swabia", "hold Lorraine",
             "pursue Mack", "support Davout", "scout Swabia", "fortify", "retreat",
             "fall back to Lorraine"]
    CONNECTIVES = ("so", "therefore", "thus", "hence")

    def test_the_census_reply_and_readback_equal_the_then_forms(self, road):
        """For every head verb x every tail verb (the connective rotating through
        so / therefore / thus / hence, on a board where the charge and the guns
        are armed and on one where they are not): the reply, the move, the AP and
        the readback of "<head> <connective> <tail>" equal "<head> then <tail>"
        (the connective word aside)."""
        client, snap = road
        norm = lambda s: re.sub(r"\b(?:so|therefore|thus|hence)\b", "then", str(s))   # noqa: E731
        bad = []
        n = 0
        for tweak in (_both_armed, _lannes_commands_guns):
            for who, head in self.HEADS:
                for i, tail in enumerate(self.TAILS):
                    conn = self.CONNECTIVES[(n + i) % 4]
                    n += 1
                    line, then = f"{who}, {head} {conn} {tail}", f"{who}, {head} then {tail}"
                    a, a_moved, a_spent, _w = _send(client, snap, line, tweak=tweak)
                    b, b_moved, b_spent, _w = _send(client, snap, then, tweak=tweak)
                    pa = _preview(client, snap, line, tweak=tweak)
                    pb = _preview(client, snap, then, tweak=tweak)
                    if not (norm(a.get("message")) == norm(b.get("message"))
                            and (a_moved, a_spent) == (b_moved, b_spent)
                            and pa.get("kind") == pb.get("kind") and norm(_head(pa)) == norm(_head(pb))):
                        bad.append(line)
        assert not bad, bad

    @pytest.mark.parametrize("line", ["Ney, move to Lorraine so attack Mack",
                                      "Ney, move to Lorraine hence fortify",
                                      "Ney, fall back to Lorraine so attack Mack"])
    def test_the_move_head_is_promoted_as_the_then_form_is(self, road, line):
        client, snap = road
        a, a_moved, a_spent, _w = _send(client, snap, line)
        b, b_moved, b_spent, _w = _send(client, snap, _then(line))
        assert (a["message"], a_moved, a_spent) == (b["message"], b_moved, b_spent)
        assert a_spent == 2 and a_moved, a["message"]
        assert _head(_preview(client, snap, line)) == _head(_preview(client, snap, _then(line)))

    def test_a_retreat_head_is_never_a_march_that_carries_an_arrival(self, road):
        """"fall back to Lorraine so attack Mack" no longer fuses an arrival attack
        onto the (retreat) head: the head keeps its own order, the tail rides the relay."""
        client, snap = road
        reply, _m, _s, _w = _send(client, snap, "Ney, fall back to Lorraine so attack Mack")
        assert "On arrival he attacks Mack" not in reply["message"], reply["message"]
        assert '"attack Mack" waits behind it' in reply["message"], reply["message"]


class TestUI6X56AChargeIsNeverAnAttackOnArrival:
    """"Murat, march to Swabia then charge Mack" with Murat UNARMED spent AP and
    armed a standing MOVE_TO whose arrival ran a plain ATTACK under the
    charge's name. Refused free; the readback agrees."""

    @pytest.mark.parametrize("line", [
        "Murat, march to Swabia then charge Mack", "Murat, march to Swabia so charge Mack",
        "Murat, march to Lorraine hence charge Mack", "Murat, march to Lorraine then charge Mack",
        "Murat, march to Swabia and charge Mack", "Murat, march to Swabia, charge Mack",
        "Murat, march to Lorraine therefore charge Mack", "Murat, march to Lorraine thus charge Mack",
    ])
    def test_unarmed_it_is_the_charges_own_gate_free(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert "needs one victory first" in message and "cannot be armed for his arrival" in message, message
        assert not reply.get("success") and not moved and spent == 0 and not reply.get("battle_report")
        pv = _preview(client, snap, line)
        assert pv["kind"] == "refusal" and "one victory" in _head(pv), (line, pv)

    @pytest.mark.parametrize("line", [
        "Murat, march to Swabia then charge Mack", "Murat, march to Lorraine so charge Mack",
        "Murat, march to Lorraine hence charge Mack", "Murat, march to Swabia and charge Mack",
    ])
    def test_armed_it_names_both_orders_and_never_a_plain_attack(self, road, line):
        client, snap = road
        reply, moved, spent, world = _send(client, snap, line, tweak=_murat_blood_up(100))
        message = reply["message"]
        assert "march to" in message and "charge Mack" in message and "when he arrives" in message, message
        assert not reply.get("success") and not moved and spent == 0 and not reply.get("battle_report")
        order = world.marshals["Murat"].strategic_order
        assert order is None or not getattr(order, "attack_on_arrival", False)
        pv = _preview(client, snap, line, tweak=_murat_blood_up(100))
        assert pv["kind"] == "refusal" and "charge" in _head(pv), (line, pv)

    def test_a_plain_attack_tail_still_carries_its_arrival(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Murat, march to Lorraine then attack Mack")
        assert spent == 2 and moved and "On arrival he attacks Mack" in reply["message"], reply["message"]

    def test_a_third_clause_charge_is_not_the_arrivals(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(
            client, snap, "Murat, march to Lorraine then attack Mack and charge Kutuzov")
        assert "cannot be armed for his arrival" not in reply["message"], reply["message"]
        assert spent == 2 and moved

    def test_a_charge_with_nothing_to_arrive_at_is_the_charge_as_before(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Murat, charge Mack")
        assert "needs one victory first" in reply["message"] and "arrival" not in reply["message"]
        assert not moved and spent == 0


class TestUI6X57ATrailingRetreatWithItsObjectIsTheSecondOrder:
    @pytest.mark.parametrize("line, tail", [
        ("Ney, hold Lorraine retreat to Mack", "retreat to Mack"),
        ("Ney, hold Lorraine retreat to Lorraine", "retreat to Lorraine"),
        ("Ney, hold Lorraine retreat from Mack", "retreat from Mack"),
        ("Ney, hold Lorraine fall back to Mack", "fall back to Mack"),
        ("Ney, hold Lorraine retreat", "retreat"),
    ])
    def test_lorraine_stays_the_holds_object(self, road, line, tail):
        client, snap = road
        parsed = _parse(snap, line)
        assert parsed["command"]["action"] == "hold" and parsed["command"]["target"] == "Lorraine", parsed
        assert parsed.get("dropped_sequel") == tail, parsed
        reply, _m, spent, _w = _send(client, snap, line)
        assert "Ney will hold Lorraine" in reply["message"] and spent == 2, reply["message"]
        assert "hold Mack" not in reply["message"] and "I would rather attack" not in reply["message"]
        assert f'"{tail}" waits behind it' in reply["message"], reply["message"]
        pv = _preview(client, snap, line)
        assert "hold Lorraine" in _head(pv) and "second order waits" in _head(pv), (line, pv)
        then = re.sub(r"\s+(retreat|fall back)", r" then \1", line, count=1)
        assert _head(pv) == _head(_preview(client, snap, then))

    def test_the_retreat_to_a_commander_is_refused_as_it_is_alone(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Ney, retreat to Mack")
        assert "Mack is a commander, Sire, not a place" in reply["message"] and not moved and spent == 0

    @pytest.mark.parametrize("line", ["Ney, guard the retreat", "Ney, cut off the line of retreat",
                                      "Ney, retreat", "Ney, hold Lorraine and the retreat"])
    def test_a_noun_or_a_lone_retreat_is_not_rewritten(self, line):
        from backend.ai.clause_guards import consequence_as_then
        assert consequence_as_then(line, ["Mack"]) == line


class TestUI6X58TwoBareOrdersNeverDropOne:
    @pytest.mark.parametrize("line, tail", [
        ("Ney, march retreat", "retreat"), ("Ney, hold retreat", "retreat"),
        ("Ney, fortify hence retreat", "retreat"), ("Ney, defend and retreat", "retreat"),
        ("Ney, defend and fall back", "fall back"), ("Ney, defend and withdraw", "withdraw"),
        ("Ney, fortify and retreat", "retreat"), ("Ney, fortify, fall back", "fall back"),
        ("Ney, hold Lorraine and retreat", "retreat"),
    ])
    def test_the_second_order_rides_the_relay_with_its_note(self, road, line, tail):
        client, snap = road
        parsed = _parse(snap, line)
        assert parsed.get("dropped_sequel") == tail, (line, parsed)
        reply, _m, _s, _w = _send(client, snap, line)
        assert f'"{tail}" waits behind it' in reply["message"], reply["message"]
        if line == "Ney, march retreat":
            return      # a bare "march" has no readback of its own (reported, not this row's)
        pv = _preview(client, snap, line)
        assert pv["kind"] == "order" and "second order waits" in _head(pv), (line, pv)

    @pytest.mark.parametrize("line", ["Ney, retreat and retreat", "Ney, march to Lorraine and hold",
                                      "Ney, defend and hold"])
    def test_one_order_said_twice_and_the_hold_idioms_are_as_they_were(self, road, line):
        client, snap = road
        assert _parse(snap, line).get("dropped_sequel") is None


class TestUI6X59RetreatFromAPlaceNamesWhereHeFallsBackFrom:
    def test_from_his_own_province_is_a_plain_retreat(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Ney, retreat from Rhineland")
        message = reply["message"]
        assert "Ney retreats from Rhineland to Lorraine" in message and moved and spent == 0, message
        for false_line in ("cannot be reached", "already stands there", "instead", "not Rhineland"):
            assert false_line not in message, (false_line, message)

    @pytest.mark.parametrize("line, place", [("Ney, retreat from Swabia", "Swabia"),
                                             ("Ney, fall back from Podolia", "Podolia"),
                                             ("Ney, withdraw from Lorraine", "Lorraine")])
    def test_from_another_province_says_where_he_stands(self, road, line, place):
        """Re-pointed by UI6-X67: it says where he stands AND runs no retreat - a
        retreat costs three turns of effectiveness, never spent on a misread
        ("withdraw from Lorraine" had sent him INTO Lorraine)."""
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert f"Ney stands at Rhineland, not {place}" in message, message
        assert not moved and spent == 0 and not reply.get("success"), message
        for hidden in ("cannot be reached", "enemy forces", "Mack", "Kutuzov", "hold it"):
            assert hidden not in message, (hidden, message)

    def test_a_destination_is_still_a_destination(self, road):
        client, snap = road
        reply, moved, _s, _w = _send(client, snap, "Ney, retreat to Lorraine")
        assert "Ney retreats from Rhineland to Lorraine" in reply["message"] and moved
        assert "not Lorraine" not in reply["message"]
        reply, _m, _s, _w = _send(client, snap, "Ney, retreat to Swabia")
        assert "Swabia cannot be reached" in reply["message"]


class TestUI6X60TheReadbackAgreesWithCommand:
    def test_a_compound_subject_with_a_province_name_is_x54s_refusal_on_both(self, road):
        client, snap = road
        line = "Ney, Brunswick and Mack are marching so scout him"
        reading, reply, moved, spent = _both(client, snap, line)
        assert "could be Brunswick or Mack" in reply["message"], reply["message"]
        assert not moved and spent == 0 and "Cannot enter Brunswick" not in reply["message"]
        assert reading["kind"] == "refusal" and "Brunswick or Mack" in _head(reading), reading
        assert "is a commander - name a province" not in _head(reading)

    @pytest.mark.parametrize("line", ["Lannes, bombard Mack", "Lannes, bombard Mack so attack Kutuzov",
                                      "Lannes, bombard Mack then attack Kutuzov"])
    def test_the_head_names_the_bombard_command_runs(self, road, line):
        client, snap = road
        reading, reply, moved, spent = _both(client, snap, line, tweak=_lannes_commands_guns)
        assert "BOMBARDMENT: Lannes" in reply["message"] and moved and spent == 1
        assert reading["kind"] == "order" and "bombard Mack" in _head(reading), reading
        assert "attack Mack" not in _head(reading), reading

    @pytest.mark.parametrize("line", ["Lannes, bombard Archduke John", "Lannes, bombard Archduke"])
    def test_guns_at_a_named_man_beyond_reach_are_refused_on_both(self, road, line):
        client, snap = road
        reading, reply, moved, spent = _both(client, snap, line, tweak=_lannes_commands_guns)
        assert "Target out of range" in reply["message"] and not moved and spent == 0
        assert reading["kind"] == "refusal" and "out of range" in _head(reading), reading

    def test_a_plain_attack_by_a_marshal_with_guns_is_still_an_attack(self, road):
        client, snap = road
        reading = _preview(client, snap, "Lannes, attack Mack", tweak=_lannes_commands_guns)
        assert "attack Mack" in _head(reading) and "bombard" not in _head(reading), reading


class TestUI6X61ASharedTitleActsOnItsUniqueBearerInSight:
    def test_the_register_pin_and_the_ruling_agree(self, road):
        client, snap = road
        reply, _m, _s, _w = _send(client, snap, "Massena fall on the Archduke")
        assert "Archduke John" in reply["message"] and "Mack" not in reply["message"].split("MUSTER")[0]
        assert "Charles" not in reply["message"]

    def test_the_bearer_helper_counts_only_men_in_sight(self, road):
        from backend.commands.combat_executor import unique_bearer_in_sight
        _client, snap = road
        world = _board(snap)
        ney = world.marshals["Ney"]
        assert unique_bearer_in_sight(world, ney, "archduke").name == "ArchdukeJohn"
        assert unique_bearer_in_sight(world, ney, "john").name == "ArchdukeJohn"
        assert unique_bearer_in_sight(world, ney, "kutuzov") is None      # out of sight
        assert unique_bearer_in_sight(world, ney, "") is None
        _charles_beside_john(world)
        assert unique_bearer_in_sight(world, ney, "archduke") is None      # two in sight
        _john_out_of_sight(world)
        assert unique_bearer_in_sight(world, ney, "archduke") is None      # none in sight


class TestUI6X62RetreatFromACommanderNamesHimNeverHisPlace:
    @pytest.mark.parametrize("line, name", [
        ("Ney, retreat from Mack", "Mack"), ("Ney, retreat from Kutuzov", "Kutuzov"),
        ("Ney, fall back from Mack", "Mack"), ("Ney, withdraw from Kutuzov", "Kutuzov"),
        ("Ney, retreat from Archduke", "Archduke"),
    ])
    def test_the_refusal_names_him_and_no_place(self, road, line, name):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert name in message and ("not a place" in message or "title" in message), message
        assert not reply.get("success") and not moved and spent == 0
        for place in ("Podolia", "Swabia", "Tyrol", "Carniola", "cannot be reached", "Rhineland"):
            assert place not in message, (place, message)
        pv = _preview(client, snap, line)
        assert pv["kind"] == "refusal" and name in _head(pv), (line, pv)

    @pytest.mark.parametrize("line", ["Ney, retreat from Rhineland", "Ney, retreat from Swabia",
                                      "Ney, fall back from Lorraine"])
    def test_a_province_is_not_caught_by_it(self, road, line):
        """Re-pointed by UI6-X67: his own province retreats; another is refused
        free by the place rule - neither by the commander refusal."""
        client, snap = road
        reply, moved, _s, _w = _send(client, snap, line)
        assert "is a commander" not in reply["message"], reply["message"]
        assert moved == line.endswith("Rhineland"), (line, reply["message"])


def _hide_the_foes(world):
    """Mack and Archduke John walked out of sight (no foe left in sight)."""
    for name in ("Mack", "ArchdukeJohn"):
        man = world.marshals.get(name)
        if man is not None:
            man.location = "Podolia"
    world.calculate_visibility()


class TestUI6X63ABareMarchWithNoFoeInSightAsks:
    """UI6-X63 (A19's verifiers, fixed by the lead): "Ney, march" with no foe in
    sight spent 2 AP on "Ney begins march to None" - the generic resolver found
    nobody and the stage carried on. It asks, free, naming no man."""

    @pytest.mark.parametrize("line", ["Ney, march on the enemy", "Ney, pursue"])
    def test_it_asks_free_and_names_no_one(self, road, line):
        """Re-pointed by UI6-X72: a LONE "Ney, march" now asks before any foe is
        sought (CX3-R2's ask, pinned in its own class); the no-foe wording is the
        verbs that seek one ("march on the enemy", "pursue")."""
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line, tweak=_hide_the_foes)
        message = reply["message"]
        assert "None" not in message and not moved and spent == 0, message
        assert "No foe is in sight" in message and "Rhineland" in message, message
        for name in ("Mack", "Kutuzov", "Archduke", "Podolia"):
            assert name not in message, (name, message)

    def test_with_a_foe_in_sight_the_march_still_finds_him(self, road):
        """Re-pointed by UI6-X72: a LONE "Ney, march" asks with a foe in sight too
        (free, as "Ney, march to" does); a march ON the enemy still finds him."""
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Ney, march")
        assert "Where shall Ney march" in reply["message"] and not moved and spent == 0, reply
        reply, _moved, _spent, _w = _send(client, snap, "Ney, march on the enemy")
        assert "None" not in reply["message"] and "Mack" in reply["message"], reply["message"]


class TestUI6X64ARetreatNamesTheDestinationItCouldNotTake:
    """UI6-X64: "Ney, retreat to Zorglub" retreated in silence - the parse bound
    no target, so W6-1's substitution (a retreat is a forced fall-back) was never
    named. The stated word now reaches it."""

    def test_the_unknown_destination_is_named(self, road):
        client, snap = road
        reply, moved, _spent, _w = _send(client, snap, "Ney, retreat to Zorglub")
        message = reply["message"]
        assert moved and "Zorglub cannot be reached" in message and "no such province" in message, message

    def test_a_known_destination_is_unchanged(self, road):
        client, snap = road
        reply, moved, _spent, _w = _send(client, snap, "Ney, retreat to Lorraine")
        assert moved and "cannot be reached" not in reply["message"], reply["message"]


class TestUI6X65TwoOrdersJoinedByAReasonWord:
    """UI6-X65: "Ney, move to Lorraine because attack Mack" dropped the move and
    fought Mack for 1 AP. Two orders joined by because / since are refused free,
    both named, on /command and the readback; a reason with its own subject is
    still a reason."""

    @pytest.mark.parametrize("line", ["Ney, move to Lorraine because attack Mack",
                                      "Ney, hold Lorraine since attack Mack",
                                      "Ney, march to Lorraine because pursue Mack"])
    def test_both_are_named_nothing_spent(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert "Two orders" in message and "Lorraine" in message and "Mack" in message, message
        assert not moved and spent == 0
        pv = _preview(client, snap, line)
        assert pv["kind"] == "refusal" and "Two orders" in _head(pv), (line, pv)

    @pytest.mark.parametrize("line", ["Ney, attack Mack because Mack is weak",
                                      "Ney, hold Rhineland since Mack is coming"])
    def test_a_reason_with_its_subject_is_still_a_reason(self, road, line):
        client, snap = road
        reply, _moved, _spent, _w = _send(client, snap, line)
        assert "Two orders" not in reply["message"], reply["message"]


class TestUI6X66TheReadbackNeverPrintsTheGenericSentinel:
    """UI6-X66: the readback of a bare "Ney, march" printed "No foe or province
    'generic' in our sight" - the parser's internal sentinel (R7)."""

    def test_a_bare_march_reads_as_a_question(self, road):
        client, snap = road
        pv = _preview(client, snap, "Ney, march")
        assert "generic" not in json.dumps(pv).lower(), pv
        assert pv["kind"] == "pending" and "Name a destination" in _head(pv), pv


class TestUI6X67ARetreatFromElsewhereIsRefusedFree:
    """UI6-X67 (A19's second verifier: X59 still retreated): "retreat from <a
    province he is not in>" ran a full retreat (-45 % for three turns) with a note
    after the fact, and "retreat from Lorraine" sent him INTO Lorraine. It is
    refused free on both roads, as `place_pre_check` refuses a stationary order at
    a province he is not in; an unknown proper name is refused naming it."""

    @pytest.mark.parametrize("line, place", [("Ney, retreat from Swabia", "Swabia"),
                                             ("Ney, retreat from Lorraine", "Lorraine"),
                                             ("Ney, retreat from Swabia to Lorraine", "Swabia"),
                                             ("Ney, retreat from Podolia", "Podolia")])
    def test_refused_free_on_both_roads(self, road, line, place):
        client, snap = road
        reply, moved, spent, world = _send(client, snap, line)
        message = reply["message"]
        assert f"Ney stands at Rhineland, not {place}" in message, message
        assert not moved and spent == 0 and not getattr(world.marshals["Ney"], "retreating", False)
        assert "Kutuzov" not in message and "Mack" not in message, message
        pv = _preview(client, snap, line)
        assert pv["kind"] == "refusal" and f"not {place}" in _head(pv), (line, pv)

    def test_an_unknown_name_is_refused_naming_it(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Ney, retreat from Zorglub")
        assert "No province called 'Zorglub'" in reply["message"] and not moved and spent == 0
        pv = _preview(client, snap, "Ney, retreat from Zorglub")
        assert pv["kind"] == "refusal" and "Zorglub" in _head(pv), pv

    @pytest.mark.parametrize("line", ["Ney, retreat from Rhineland", "Ney, retreat from the enemy",
                                      "Ney, retreat from Austria", "Ney, retreat from here",
                                      "Ney, retreat from Rhineland to Lorraine"])
    def test_his_own_province_a_plain_phrase_or_a_court_retreats(self, road, line):
        client, snap = road
        reply, moved, _s, _w = _send(client, snap, line)
        assert moved and "Ney retreats from Rhineland" in reply["message"], (line, reply["message"])

    def test_the_readback_reads_from_and_to(self, road):
        client, snap = road
        assert "fall back from Rhineland to Lorraine" in _head(
            _preview(client, snap, "Ney, retreat from Rhineland to Lorraine"))
        assert "fall back from Rhineland" in _head(_preview(client, snap, "Ney, retreat from Rhineland"))
        assert "fall back to Lorraine" in _head(_preview(client, snap, "Ney, retreat to Lorraine"))
        assert "‘Zorglub’" in _head(_preview(client, snap, "Ney, retreat to Zorglub"))


class TestUI6X68ARetreatFromAPronounNamesTheCommander:
    """UI6-X68: "Mack is attacking Swabia so retreat from him" retreated with a
    false "Mack cannot be reached - no such province" - the pronoun the clause
    bound to a commander is the commander refusal's, as "retreat from Mack" is."""

    def test_the_commander_refusal_answers_it(self, road):
        client, snap = road
        line = "Ney, Mack is attacking Swabia so retreat from him"
        reply, moved, spent, _w = _send(client, snap, line)
        message = reply["message"]
        assert "Mack is a commander" in message and "no such province" not in message, message
        assert not moved and spent == 0
        pv = _preview(client, snap, line)
        assert pv["kind"] == "refusal" and "Mack is a commander" in _head(pv), pv


class TestUI6X69CoSubjectJoinersNameTheDroppedCommander:
    """UI6-X69 (A19's second verifier): "attack Mack with / along with / together
    with / as well as Kutuzov" dropped Kutuzov with no note on either road, as
    "and" / "plus" / "," never did. A marshal of OURS after "with" is company the
    muster reads for itself ("WILL JOIN - Davout") - never called dropped."""

    @pytest.mark.parametrize("joiner", ["with", "along with", "together with", "as well as",
                                        "alongside"])
    def test_the_note_names_him_on_both_roads(self, road, joiner):
        client, snap = road
        line = f"Ney, attack Mack {joiner} Kutuzov"
        reply, _moved, _spent, _w = _send(client, snap, line)
        assert "Kutuzov, named after Mack, was not acted on" in reply["message"], reply["message"]
        assert "Podolia" not in reply["message"]
        assert "Kutuzov, named after Mack" in _head(_preview(client, snap, line))

    @pytest.mark.parametrize("line", ["Ney, attack Mack with Davout", "Ney, attack Mack with all speed",
                                      "Ney, hold Lorraine with Davout"])
    def test_company_of_ours_and_a_manner_are_no_dropped_name(self, road, line):
        client, snap = road
        reply, _moved, _spent, _w = _send(client, snap, line)
        assert "named after" not in reply["message"], (line, reply["message"])
        assert "named after" not in _head(_preview(client, snap, line))


class TestUI6X71APursuitOfASharedTitleTakesItsOneBearerInSight:
    """UI6-X71 (A19-S6): "Ney, pursue the Archduke" answered "Cannot find
    'Archduke' to pursue" with John in sight while the attack bound him (UI6-X61).
    The pursuit reads the same: one bearer in sight is the man named; none in
    sight keeps the free refusal, naming no one out of sight."""

    @pytest.mark.parametrize("line", ["Ney, pursue the Archduke", "Ney, pursue Archduke"])
    def test_john_in_sight_is_pursued_on_both_roads(self, road, line):
        client, snap = road
        reply, _moved, _spent, _w = _send(client, snap, line)
        assert "Cannot find" not in reply["message"], reply["message"]
        full, _m, _s, _w2 = _send(client, snap, "Ney, pursue Archduke John")
        assert reply["message"] == full["message"]
        assert "pursue Archduke John" in _head(_preview(client, snap, line))

    def test_no_bearer_in_sight_keeps_the_refusal_and_names_no_one(self, road):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, "Ney, pursue the Archduke",
                                        tweak=_john_out_of_sight)
        message = reply["message"]
        assert "Cannot find" in message and not moved and spent == 0, message
        for hidden in ("Charles", "Carniola", "Podolia", "John"):
            assert hidden not in message, (hidden, message)


class TestUI6X72ALoneMarchAsksWhereFree:
    """UI6-X72 (A19-S7): a lone "Ney, march" spent an action marching on the
    nearest foe while the readback promised a question. It asks, free, as "Ney,
    march to" does (CX3-R2); "Ney, move" / "Ney, go" read as the ask they are;
    a verb that carries the nearest foe reads so, unpriced, naming no one."""

    @pytest.mark.parametrize("line", ["Ney, march", "Ney, move", "Ney, go", "Ney: march!"])
    def test_it_asks_free_on_both_roads(self, road, line):
        client, snap = road
        reply, moved, spent, _w = _send(client, snap, line)
        assert "Where shall Ney march" in reply["message"] and not moved and spent == 0, reply
        pv = _preview(client, snap, line)
        assert pv["kind"] == "pending" and "Where to?" in _head(pv), (line, pv)

    def test_a_march_on_the_enemy_reads_the_nearest_foe_unpriced(self, road):
        client, snap = road
        pv = _preview(client, snap, "Ney, march on the enemy")
        assert pv["kind"] == "pending" and "nearest foe in sight" in _head(pv), pv
        assert "priced when sent" in _head(pv) and "Mack" not in _head(pv)
        assert "pursue the nearest foe" in _head(_preview(client, snap, "Ney, pursue"))


_OPEN_S15 = ("OPEN — owner row IC Session 2, slice IC-8 (moved November 20, 2026 from Session H's head: "
             "the read-back of typed tasks depends on it) by the sibling sweep's rule; "
             "closes when this pin passes (strict)")


class TestUI6X70ACompoundReportSubjectWithAFriendIsAReason:
    """UI6-X70 OPEN (A19-S5, confirmed by both verifiers): "Ney, Mack and Davout
    are marching so attack Mack" is refused free for the WRONG reason ("Mack is a
    commander, not a province") - `clause_guards._reason_pattern` reads a compound
    report subject of FOES only (UI6-X54), so a friend or a title in it leaves the
    report on the line as a march. Done when the report clause is read whole (the
    attack on Mack goes out, as the foe-only compound does) on both roads."""

    @pytest.mark.xfail(strict=True, reason=_OPEN_S15)
    @pytest.mark.parametrize("line", ["Ney, Mack and Davout are marching so attack Mack",
                                      "Ney, Mack and the Archduke are marching so attack Mack"])
    def test_the_report_is_a_reason_not_a_march(self, road, line):
        client, snap = road
        reply, _moved, _spent, _w = _send(client, snap, line)
        assert "is a commander" not in reply["message"], reply["message"]
        assert "is a commander" not in _head(_preview(client, snap, line))


class TestUI6X73AThirdClauseIsNeverDroppedInSilence:
    """UI6-X73 OPEN (A19-S8, pre-existing): "Murat, march to Lorraine then attack
    Mack and charge Mack" runs the march carrying the attack and drops the third
    order with no relay note - the and-split judges fusion against the already
    fused head. Done when the third order is relayed or refused by name."""

    @pytest.mark.xfail(strict=True, reason=_OPEN_S15)
    @pytest.mark.parametrize("line, third", [
        ("Murat, march to Lorraine then attack Mack and charge Mack", "charge"),
        ("Ney, march to Lorraine then attack Mack and fortify", "fortify")])
    def test_the_third_order_is_named(self, road, line, third):
        client, snap = road
        reply, _moved, _spent, _w = _send(client, snap, line)
        assert third in reply["message"].lower(), reply["message"]


class TestUI6X74AFriendOnlyReportSubjectAsksNoMarch:
    """UI6-X74 OPEN (A19's first verifier, N2): "Ney, Davout and Soult are marching
    so attack him" reads the report as Ney's march and asks "Where shall Ney
    march?" - free, but a question the line never asked; the pronoun stands for
    no foe. Done when it is refused free naming what was read."""

    @pytest.mark.xfail(strict=True, reason=_OPEN_S15)
    def test_no_march_is_asked(self, road):
        client, snap = road
        line = "Ney, Davout and Soult are marching so attack him"
        reply, moved, spent, _w = _send(client, snap, line)
        assert "Where shall" not in reply["message"] and not moved and spent == 0, reply
        assert "Where to?" not in _head(_preview(client, snap, line))


class TestUI6X75ATitleFirstListNamesTheTitle:
    """UI6-X75 OPEN (A19's second verifier): "Ney, attack the Archduke and Mack"
    with John out of sight attacks Mack and never mentions the Archduke - the list
    reader's first segment is a title no man in sight bears, so the whole list
    reads as nothing. Done when the Archduke is named (the free ask, or the note
    that he was not acted on), on both roads, naming no place of his."""

    @pytest.mark.xfail(strict=True, reason=_OPEN_S15)
    def test_the_title_is_named(self, road):
        client, snap = road
        line = "Ney, attack the Archduke and Mack"
        reply, _moved, _spent, _w = _send(client, snap, line, tweak=_john_out_of_sight)
        assert "Archduke" in reply["message"], reply["message"][-300:]
        assert "Archduke" in _head(_preview(client, snap, line, tweak=_john_out_of_sight))
