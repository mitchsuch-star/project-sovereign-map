"""IQ-7 review round — the pins (September 18, 2026).

Master `7d10e20c` landed "The Client's Petition"; the 73-agent review filed
43 findings, 39 survived, and the lead's fix contract (rulings R1–R10) was
built by two builders and an integrator. This file pins every ruling on
the ORDINARY geometry the review measured — the shipped turn-6 board
(five real end turns through `TurnManager.end_turn`: the boot coalition's
settlement offer CURRENT, routine letters queued, Switzerland's relief
petition QUEUED behind them, never a modal on its own), the Tyrol staging
the IQ-7 file uses for the province ask, and the School of War — plus each
mechanics lever's False arm on its own surface, the X5 reap on all six
roads, and the R5 drift pin.

THE T11(d) FLIP, RECORDED: the IQ-7 contract's T11(d) ("set lord DP to 0
-> withdrawn, no refusal penalty") is consciously REVERSED by R2
([03]/[35]/[12]). DP is the player's own pool, reset every turn, so
"spend it, then press Grant" was a free exit from the −10 loyalty / −20
bond that Refuse and the lapse both charge. A lord who cannot pay has NOT
answered: the Grant is refused WITHOUT consuming the petition (outcome
`stands`), the question is re-carried with Grant honestly disabled, and
the lapse then charges the refusal like any other. The old withdrawal is
the False arm of `THE_LORD_PAYS_TO_GRANT`; the flipped pin lives in
`tests/test_iq7_satellites_have_a_position.py::TestT11ReValidationAtAnswer
::test_d_a_lord_who_can_no_longer_pay`.

Levers (all in `backend/game_logic/vassal.py`; False must reproduce
`7d10e20c` on its surface — every False arm below asserts the STATE the
integrator's `probe_levers.py` measured against the 7d10e20c module loaded
side by side): `THE_DEED_HONOURS_THE_PETITION` (R1),
`THE_LORD_PAYS_TO_GRANT` (R2), `THE_TRANSFER_SHEDS_THE_REMISSION` (R3),
`A_RELIEF_OF_NOTHING_IS_WITHDRAWN` (R4's "relief whose live tribute is 0
-> None"; Builder A's extra lever). R5–R10 are copy, display and routing —
no lever (GR6) — so their pins carry no False arm.

Method notes, recorded rather than hidden:
* The turn-6 board is booted ONCE per module — `seed="historical"` passed
  explicitly, because a module-scoped fixture is built BEFORE conftest's
  function-scoped `SOVEREIGN_SEED` pin (the AI-V seed-escape trap) — and
  each test restores it through `to_dict`/`from_dict`, so the save/load
  road is exercised by every board pin. `from_dict` restores the
  settlement offer's popup as deliverable (the integrator's G1 artefact),
  so the board fixture drains it with one `status` before the test's own
  responses.
* Combat jitter rides the unseeded `random` module (the IQ-7 file's
  docstring); the module RNG is re-seeded on every restore.
* `_stage_tyrol_for_koi` MIRRORS the IQ-7 file's helper of the same name
  rather than importing that test module: its import loads
  `tools/playtest_driver.py`, which IQ-8 is editing in this tree.

PASS 2 (same day). Two adversarial verifiers attacked the pass-1 fixes on
the geometries the builders had not constructed and filed eleven rulings
(P2-1, P3-1..P3-4, P4-1..P4-6); two builders built them and the classes at
the foot of this file pin them, one class a ruling, each through the real
endpoints: the petition activated from Envoys and answered by a deferred /
conditional / interrogative line (P2-1); the Kingdom of Italy's Tyrol
petition with Milan lost to Austria before the answer (P3-1) and re-read
after one `status` (P3-2 — the article pins ride the Kingdom of Italy tag,
because Switzerland takes no article and cannot see them); a REAL Prussian
ultimatum delivered behind Portugal's letter (P3-3) and activated from
Envoys over the queued petition (P3-4); the player's own `release
switzerland` with its petition on the desk (P4-1); the Vassals card over
`GET /diplomatic_ledger` (P4-2); the letter nouns (P4-3); the W6-9
`advisory` current (P4-4); the court guard's tail (P4-5); and Slice H's
ally petition, built by its own producer and activated from Envoys (P4-6).
Pass 2 adds two ROUTING levers, both in `backend/commands/
dialogue_routing.py` — `A_PETITION_IS_ANSWERED_PLAINLY` (P2-1) and
`THE_MATTER_GUARD_READS_THE_TABLE` (P3-3 / P3-4 / P4-3 / P4-6) — whose
False arms are pinned as the pass-1 router on their own surfaces; P3-1
rides `THE_DEED_HONOURS_THE_PETITION`'s existing False arm; P3-2, P4-1,
P4-2, P4-4 and P4-5 are copy and display (GR6, no lever).

PASS 3 (September 18, 2026). A second verifier attacked pass 2 and filed
V2-1..V2-8 plus a NOTED list; ONE builder closed them under eleven rulings
(R3-1..R3-11), and the classes at the very foot of this file pin them — one
class a ruling, the verifier's own lines through the real endpoints on its
own geometries. The design ruling that ends the loop: the plain answer to a
CLIENT petition is a CLOSED, LITERAL allowlist grammar and it FAILS CLOSED
(`dialogue_routing.petition_plain_answer`) — still behind pass 2's
`A_PETITION_IS_ANSWERED_PLAINLY`, no new lever. Two new ROUTING levers:
`A_QUESTION_NEVER_ANSWERS` (R3-9 — a question answers no dialogue of any
family) and `THE_BUTTON_ROUTE_READS_THE_COURT` (R3-10). Pins FLIPPED in pass
3, each dated where it stands: the rail title's article (R3-8 — here and in
the IQ-7 file), and UX23-B's roster source-count, re-anchored to count the
MATCHER call sites it was always about.

PASS 4 — the FINAL pass (September 18, 2026). Two adversarial verifiers
attacked pass 3, each finding with an executed reproduction; ONE builder
closed them under five rulings (R4-1..R4-5) and the classes `TestR41…` ..
`TestR45…` at the very foot pin them through the real endpoints. R4-1: a
question made ONLY of allowlist tokens answered the petition at its price
(`then shall we grant it` GRANTED, `sire do we refuse` REFUSED, `then shall
we grant tyrol` CEDED TYROL) — `they` left the allowlist and the auxiliaries
`shall` / `will` / `do` answer in STATEMENT order only. R4-2: pass 3's
question rule stopped the advisory's own question-shaped LABELS resolving
unless typed with their `?`. R4-3 (pre-existing, every family, a HARD STOP
included): `then shall we ratify` RATIFIED a settlement — a subject-auxiliary
inversion ANYWHERE in the line is a question, behind pass 3's
`A_QUESTION_NEVER_ANSWERS`. R4-4: two more shapes re-prompt IN PLACE at a
current petition (`hmm, grant it`; `Talleyrand, no`), and shape (c) is
narrowed so the player's own diplomat-addressed ORDER about another court
reaches the proposal road again. R4-5 (R7): no raw tag and no missing
article in any sentence a vassal verb returns. No new lever. Pins FLIPPED in
pass 4, each dated where it stands: the literal allowlist pin (`they` is
gone) and R3-9's `shall we proceed? yes` (a line that carries every word of
a question-shaped label IS that label).
"""

from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import os
import random
import re
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

with contextlib.redirect_stdout(io.StringIO()):
    import backend.main as M
    from backend import campaign_log as CL
    from backend.commands import dialogue_routing as DR
    from backend.commands.dialogue_routing import (
        matter_mismatch_refusal, petition_vocabulary_answer,
    )
    from backend.commands.parser import CommandParser
    from backend.game_logic import settlement_offers as SO
    from backend.game_logic import vassal as V
    from backend.game_logic.ai_diplomacy import deliver_ai_proposal
    from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
    from backend.game_logic.dispatch import _format_dispatch_event_text
    from backend.game_logic.ledger import build_strategic_ledger
    from backend.game_logic.mailbox_payloads import (
        build_pending_envoy_popup_from_terms, refresh_client_petition_dialogue,
    )
    from backend.game_logic.settlement_ratify import _apply_settlement_terms
    from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")
GODOT_SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
GODOT_SCENES = REPO / "godot-client" / "project-sovereign" / "scenes"
PLAYER = "France"
KOI = "KingdomOfItaly"
SWISS = "Switzerland"
LEVERS = ("THE_CLIENT_PETITIONS", "AN_UNANSWERED_PETITION_IS_REFUSED",
          "COURTING_SPARES_THE_LORDS_ALLIES", "THE_WAVERING_LINE_IS_HONEST",
          "THE_DEED_HONOURS_THE_PETITION", "THE_LORD_PAYS_TO_GRANT",
          "THE_TRANSFER_SHEDS_THE_REMISSION", "A_RELIEF_OF_NOTHING_IS_WITHDRAWN")
# The typed verbs the review used to spend the turn's DP to 0 (each one an
# ordinary, useful order — the dodge cost the player nothing).
DP_SPENDS = ("invest in Holland", "invest in Kingdom of Italy",
             "grant Holland more autonomy", "grant Kingdom of Italy more autonomy",
             "invest in Switzerland", "reduce Holland autonomy", "invest in Holland")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


with _quiet():
    _PARSER = CommandParser(use_real_llm=False)


def _seed():
    digest = hashlib.sha256("historical:0".encode()).hexdigest()
    random.seed(int(digest, 16) & 0xFFFFFFFF)


def _europe():
    with _quiet():
        world = WorldState.from_scenario(SCENARIO, seed="historical")
    _seed()
    return world


def _swap(monkeypatch, world):
    assert _PARSER.llm.use_real_api is False
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "parser", _PARSER)
    monkeypatch.setitem(M.game_state, "world", world)
    return TestClient(M.app)


def _restore(monkeypatch, snapshot):
    with _quiet():
        world = WorldState.from_dict(copy.deepcopy(snapshot))
    _seed()
    return world, _swap(monkeypatch, world)


def _cmd(client, text):
    with _quiet():
        return client.post("/command", json={"command": text}).json()


def _respond(client, choice, dialogue_id=None):
    with _quiet():
        return client.post("/respond_to_diplomatic_dialogue",
                           json={"choice": choice, "dialogue_id": dialogue_id}).json()


def _activate(client, dlg):
    with _quiet():
        return client.post("/mailbox/activate",
                           json={"mailbox_id": dlg["mailbox_id"]}).json()


def _pending_envoy(client):
    with _quiet():
        return client.get("/pending_envoy").json()


def _campaign_log_blob(client):
    with _quiet():
        return json.dumps(client.get("/campaign_log").json(), ensure_ascii=False)


def _end_turn(client):
    """One REAL end turn (the IQ-7 file's idiom): the W6-8 capture question
    an unbidden French victory raises is answered as the driver answers it
    (`secure`), and any other stall is a failure with its reason."""
    world = M.game_state["world"]
    before = int(world.current_turn)
    r = _cmd(client, "end turn")
    for _ in range(3):
        pending = world.pending_capture_choice
        if int(world.current_turn) == before + 1 or not pending:
            break
        _cmd(client, "respect" if pending.get("stage") == "estate" else "secure")
        r = _cmd(client, "end turn")
    if int(world.current_turn) != before + 1:
        current = world.dialogue_manager.peek() or {}
        raise AssertionError(
            f"end turn did not advance from {before}: success={r.get('success')} "
            f"message={str(r.get('message'))[:400]!r} current_dialogue="
            f"{current.get('type')}/{current.get('target_nation')}")
    return r


def _pending(w):
    dm = w.dialogue_manager
    return ([dm.peek()] if dm.peek() else []) + list(dm.iter_queue())


def _petitions(w):
    return [d for d in _pending(w) if V.is_client_petition(d)]


def _logged(w, outcome=None):
    rows = [e for e in w.event_log if e.get("type") == "client_petition_answered"]
    if outcome is None:
        return rows
    return [e for e in rows if e.get("outcome") == outcome]


def _rel(w, a, b):
    return int(w.nation_relations.get(w._make_diplo_key(a, b), 0) or 0)


def _set_rel(w, a, b, value):
    w.nation_relations[w._make_diplo_key(a, b)] = int(value)


def _titles(w):
    return [n.get("title") for n in w.notifications.to_list()]


def _notice_body(w, title):
    for n in w.notifications.to_list():
        if n.get("title") == title:
            return str(n.get("message") or "")
    return ""


def _grant_clause(clauses):
    return next((str(c) for c in clauses if str(c).startswith("Grant it")), "")


def _figures(text):
    """(forgone, loyalty_gain, bond_after) parsed from a grant clause / result
    — the three figures the modal exists to state."""
    forgone = re.search(r"\((\d+)g forgone\)", text)
    gain = re.search(r"[Ll]oyalty \+(\d+)", text)
    bond = re.search(r"bond(?: with us rises)? (-?\d+) → (-?\d+)", text)
    return (int(forgone.group(1)) if forgone else None,
            int(gain.group(1)) if gain else None,
            int(bond.group(2)) if bond else None)


def _make_proposal(w, vassal):
    terms = V.petition_terms(w, vassal)
    assert terms is not None, f"{vassal} has no subject on this board"
    return {
        "source": vassal, "recipient": w.player_nation,
        "proposal_type": V.CLIENT_PETITION_TYPE,
        "terms": {"type": V.CLIENT_PETITION_TYPE, "proposer_nation": vassal,
                  "target_nation": w.player_nation, "demands": [],
                  "sweeteners": [], "petition": terms},
        "talleyrand_assessment": f"{terms['grant_line']} {terms['refuse_line']}",
        "decision_reason": "client_petition", "_force_send": True,
    }


def _ordinary(nation, ptype):
    return {"source": nation, "recipient": PLAYER, "proposal_type": ptype,
            "priority": 1,
            "terms": {"type": ptype, "proposer_nation": nation,
                      "target_nation": PLAYER, "clauses": [ptype],
                      "sweeteners": [], "demands": []},
            "talleyrand_assessment": "", "decision_reason": "hegemony_pressure",
            "turn_generated": 1}


def _clear_slot(w):
    """Empty the manager (the boot coalition's settlement offer) so the next
    delivery is CURRENT and its popup cached — the X5 geometry."""
    w.dialogue_manager._queue = []
    w.dialogue_manager._current = None
    w.incoming_proposal_popup = None
    w.proposal_result_popup = None


def _deliver(w, proposal):
    with _quiet():
        return deliver_ai_proposal(proposal, w)


def _deliver_only(w, vassal):
    _clear_slot(w)
    return _deliver(w, _make_proposal(w, vassal))


def _stage_tyrol_for_koi(w):
    """Mirrors `tests/test_iq7_satellites_have_a_position.py::
    _stage_tyrol_for_koi`: Tyrol (Austrian soil, income 150, adjoins Milan)
    held by France — conquered, non-homeland, non-capital, so VS-3 lists it
    for the Kingdom of Italy; Archduke John's corps moved off it."""
    w.regions["Tyrol"].controller = PLAYER
    john = w.marshals.get("ArchdukeJohn")
    if john is not None:
        john.location = "Carniola"
    w.invalidate_active_nations_cache()


def _park(w, keep):
    for name, row in w.vassals.items():
        if name != keep and row["lord"] == PLAYER:
            row["loyalty"] = 50


def _holland_under_prussia(dp=3):
    w = _europe()
    with _quiet():
        V.transfer_vassal(w, "Holland", "Prussia")
    row = w.vassals["Holland"]
    row["loyalty"] = 80
    row["created_turn"] = -10
    w.nation_dp["Prussia"] = dp
    return w


def _tyrol_board(monkeypatch, *, stability=None, loyalty=86):
    """The R1/R5 geometry: the Kingdom of Italy's province petition for
    Tyrol, issued by the REAL producer at turn 6 and its delivery popup
    consumed by one `status`, exactly as the review's probes staged it."""
    w = _europe()
    _stage_tyrol_for_koi(w)
    if stability is not None:
        w.regions["Tyrol"].stability = int(stability)
    _park(w, KOI)
    w.current_turn = 6
    w.vassals[KOI]["created_turn"] = 1
    w.vassals[KOI]["loyalty"] = int(loyalty)
    with _quiet():
        V.process_vassal_petitions(w)
    pets = _petitions(w)
    assert len(pets) == 1 and pets[0]["context"]["proposal"]["petition"]["region"] == "Tyrol"
    client = _swap(monkeypatch, w)
    _cmd(client, "status")
    return w, client, pets[0]


# ═══════════════════════════════════════════════════════════════════════════
# fixtures
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _restore_levers(monkeypatch):
    for name in LEVERS:
        monkeypatch.setattr(V, name, getattr(V, name))
    yield


_SNAPSHOT_SANDBOX: dict = {}       # where `turn6_snapshot`'s end turns autosaved


@pytest.fixture(scope="module")
def turn6_snapshot():
    """The shipped turn-6 board, booted once: five real end turns from the
    1805 boot leave the boot coalition's settlement offer CURRENT and
    Switzerland's relief petition QUEUED behind the turn's routine letters
    (the IQ-7 file's T2 measurement). Snapshotted as `to_dict()`."""
    prior_env = {k: os.environ.get(k) for k in
                 ("INK_IRON_SAVE_DIR", "SOVEREIGN_SEED", "SOVEREIGN_SCENARIO", "LLM_MODE")}
    prior_main = (M.world, M.game_state.get("world"), M.parser)
    tmp = tempfile.mkdtemp(prefix="iq7_review_saves_")
    os.environ["INK_IRON_SAVE_DIR"] = tmp
    os.environ["SOVEREIGN_SEED"] = "historical"
    os.environ["SOVEREIGN_SCENARIO"] = "none"
    os.environ["LLM_MODE"] = "mock"
    # SWEEP 2 (measured): the env var above is read ONCE, when `backend.save_manager`
    # is imported — long before this fixture runs — and a MODULE-scoped fixture is
    # built BEFORE conftest's function-scoped `_isolate_save_dir`, so these five real
    # end turns autosaved into the developer's own `saves/autosave.json` (its mtime
    # moved on every run of this file). The module attribute is what `autosave` reads.
    import backend.save_manager as save_manager
    prior_save_dir = save_manager.SAVE_DIR
    save_manager.SAVE_DIR = Path(tmp)
    _SNAPSHOT_SANDBOX["dir"] = tmp
    # SR-1d (September 26, 2026): PR-D1b gates the league's turn-4 offer, so
    # on the shipped board no settlement offer holds the current slot at
    # turn 6. This board exists to stage a petition QUEUED behind a letter
    # (the IQ-7 T2 measurement) — it is staged with that lever down, as the
    # ruling allows, and says so here.
    from backend.game_logic import ai_diplomacy as _AD
    _prior_league = _AD.THE_LEAGUE_TREATS_WHEN_SPENT
    _AD.THE_LEAGUE_TREATS_WHEN_SPENT = False
    try:
        w = _europe()
        M.world, M.parser = w, _PARSER
        M.game_state["world"] = w
        client = TestClient(M.app)
        while int(w.current_turn) < 6:
            _end_turn(client)
        pets = _petitions(w)
        assert len(pets) == 1 and pets[0]["target_nation"] == SWISS
        assert pets[0]["context"]["proposal"]["petition"]["subject"] == "relief"
        head = _pending(w)[0]
        assert head is not pets[0] and head.get("type") == "incoming_settlement_offer"
        snapshot = copy.deepcopy(w.to_dict())
    finally:
        _AD.THE_LEAGUE_TREATS_WHEN_SPENT = _prior_league
        save_manager.SAVE_DIR = prior_save_dir
        M.world, M.parser = prior_main[0], prior_main[2]
        M.game_state["world"] = prior_main[1]
        for key, value in prior_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    return snapshot


def test_the_board_fixture_autosaves_into_its_own_sandbox(turn6_snapshot):
    """SWEEP 2: the suite must never write the developer's `saves/` (conftest's own
    rule). The boot's five end turns autosave — into the fixture's sandbox."""
    import backend.save_manager as save_manager
    sandbox = Path(_SNAPSHOT_SANDBOX["dir"])
    assert (sandbox / save_manager.AUTOSAVE_FILENAME).is_file()
    assert Path(save_manager.SAVE_DIR) != Path("saves")            # conftest's guard, per test


_RESTORED_POPUP_KEYS = ("incoming_settlement_offer", "marshal_petition", "proposal_result")


def _drain(client, keys=_RESTORED_POPUP_KEYS, limit=5):
    """One popup rides each response: a restore re-queues the settlement
    offer's popup (and the deferred marshal petition), so the board's own
    responses are read only once those have been handed over."""
    for _ in range(limit):
        r = _cmd(client, "status")
        if not any(isinstance(r.get(k), dict) for k in keys):
            return r
    raise AssertionError("the restored popups did not drain")


@pytest.fixture
def board(turn6_snapshot, monkeypatch):
    """The ordinary geometry, restored for one test: the settlement offer
    current, the petition queued, the restored popups drained."""
    w, client = _restore(monkeypatch, turn6_snapshot)
    _drain(client)
    pets = _petitions(w)
    assert len(pets) == 1 and _pending(w)[0] is not pets[0]
    return w, client


def _petition_of(w):
    return _petitions(w)[0]


def _verdict(client, r):
    """The answer's `proposal_result` — on the answer's own response, or on
    the next when another popup outranked it there (one popup a response)."""
    if isinstance(r.get("proposal_result"), dict):
        return r["proposal_result"]
    r2 = _cmd(client, "status")
    assert isinstance(r2.get("proposal_result"), dict), (r.keys(), r2.keys())
    return r2["proposal_result"]


# ═══════════════════════════════════════════════════════════════════════════
# R1 — the deed fulfils the petition
# ═══════════════════════════════════════════════════════════════════════════

class TestR1TheDeedFulfilsThePetition:
    def test_the_typed_cede_then_the_lapse_honours_the_petition_once(self, monkeypatch):
        w, client, pet = _tyrol_board(monkeypatch)
        rel0 = _rel(w, KOI, PLAYER)
        r = _cmd(client, "cede Tyrol to the Kingdom of Italy")
        assert r.get("success") is True, r.get("message")
        assert w.regions["Tyrol"].controller == KOI
        assert w.vassals[KOI]["granted_regions"] == ["Tyrol"]
        assert _petitions(w) and _petitions(w)[0] is pet          # typed-command safety
        assert V.petition_is_fulfilled(w, KOI, PLAYER, pet["context"]["proposal"]["petition"])
        # the end-turn gate already forecasts the honoured close, not a refusal
        lp = _cmd(client, "status")["pending_lapsing_petitions"]
        assert len(lp) == 1 and lp[0]["refused"] is False
        assert "closes the petition as honoured" in lp[0]["price_line"]
        loy_after_cede = w.vassals[KOI]["loyalty"]
        r = _end_turn(client)
        rows = _logged(w)
        assert [(e["outcome"], e["penalty"]) for e in rows] == [("fulfilled", False)]
        assert rows[0]["relation_before"] == rel0 and rows[0]["relation_after"] == rel0 + 20
        assert rows[0]["loyalty_before"] == rows[0]["loyalty_after"] == loy_after_cede
        assert _rel(w, KOI, PLAYER) == rel0 + V.PETITION_RELATION_STEP
        assert not _petitions(w)
        receipt = [e for e in r.get("events", []) if e.get("type") == "client_petition_answered"]
        assert receipt and "honoured" in receipt[0]["message"] and receipt[0]["penalty"] is False
        assert CL.format_event_oneliner(rows[0]) == (
            "The Kingdom of Italy's petition for Tyrol — already ceded by our own hand; honoured.")

    def test_cede_then_refuse_is_honoured_and_reported_as_accepted(self, monkeypatch):
        w, client, pet = _tyrol_board(monkeypatch)
        _cmd(client, "cede Tyrol to the Kingdom of Italy")
        rel0, loy0, dp0 = _rel(w, KOI, PLAYER), w.vassals[KOI]["loyalty"], w.diplomatic_points
        r = _respond(client, "refuse the petition", pet["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        assert "honoured" in str(r.get("message"))
        assert r["proposal_result"]["outcome"] == "ACCEPT"
        assert r["proposal_result"]["proposal_type"] == "Client's Petition"
        assert _rel(w, KOI, PLAYER) == rel0 + 20
        assert w.vassals[KOI]["loyalty"] == loy0 and w.diplomatic_points == dp0
        assert [e["outcome"] for e in _logged(w)] == ["fulfilled"]
        assert not _petitions(w)

    def test_cede_then_grant_charges_no_second_dp_and_no_second_gain(self, monkeypatch):
        w, client, pet = _tyrol_board(monkeypatch)
        _cmd(client, "cede Tyrol to the Kingdom of Italy")
        rel0, loy0, dp0 = _rel(w, KOI, PLAYER), w.vassals[KOI]["loyalty"], w.diplomatic_points
        r = _respond(client, "grant the petition", pet["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        assert r["proposal_result"]["outcome"] == "ACCEPT"
        assert w.diplomatic_points == dp0                          # the cede paid its own
        assert w.vassals[KOI]["loyalty"] == loy0                   # and its own gain
        assert _rel(w, KOI, PLAYER) == rel0 + 20
        assert [e["outcome"] for e in _logged(w)] == ["fulfilled"]
        assert "Nothing more is charged" in str(r.get("message"))

    def test_endow_then_lapse_stays_a_refusal(self, monkeypatch):
        """A province the lord gave to his OWN marshal was his answer."""
        w, client, pet = _tyrol_board(monkeypatch)
        loy0, rel0 = w.vassals[KOI]["loyalty"], _rel(w, KOI, PLAYER)
        r = _cmd(client, "endow Ney with Tyrol")
        assert r.get("success") is True, r.get("message")
        assert "Tyrol" in (getattr(w.marshals["Ney"], "dotation_regions", []) or [])
        assert _petitions(w) and _petitions(w)[0] is pet
        lp = _cmd(client, "status")["pending_lapsing_petitions"]
        assert lp[0]["refused"] is True and "−10 loyalty / −20 bond" in lp[0]["price_line"]
        _end_turn(client)
        rows = _logged(w)
        assert [(e["outcome"], e["penalty"]) for e in rows] == [("unanswered", True)]
        assert rows[0]["loyalty_after"] == rows[0]["loyalty_before"] - V.PETITION_REFUSAL_LOYALTY
        assert rows[0]["loyalty_before"] == loy0
        assert _rel(w, KOI, PLAYER) == rel0 - V.PETITION_RELATION_STEP

    def test_dp_spent_to_zero_then_lapse_is_still_a_refusal(self, monkeypatch):
        """The [01] hazard: sharing grant's whole re-validation with the refuse
        arm would have made every lapse at 0 DP free."""
        w, client, pet = _tyrol_board(monkeypatch)
        w.diplomatic_points = 0
        rel0 = _rel(w, KOI, PLAYER)
        _end_turn(client)
        rows = _logged(w)
        assert [(e["outcome"], e["penalty"]) for e in rows] == [("unanswered", True)]
        assert _rel(w, KOI, PLAYER) == rel0 - V.PETITION_RELATION_STEP

    def test_a_province_given_elsewhere_by_our_own_hand_stands_and_still_prices_the_refusal(self):
        w = _europe()
        _stage_tyrol_for_koi(w)
        pet = V.petition_terms(w, KOI)
        assert pet["region"] == "Tyrol"
        # ...to ANOTHER of the lord's clients: his choice, not the war's
        w.regions["Tyrol"].controller = "Holland"
        w.invalidate_active_nations_cache()
        kind, message = V.petition_grant_verdict(w, PLAYER, KOI, pet)
        assert kind == "stands" and "given elsewhere by our own hand" in message
        assert V.petition_grant_availability(w, PLAYER, KOI, pet) == (False, message)
        assert not V.petition_is_fulfilled(w, KOI, PLAYER, pet)
        loy0, rel0 = w.vassals[KOI]["loyalty"], _rel(w, KOI, PLAYER)
        forecast = V.lapse_forecast(w, KOI, PLAYER, pet)
        assert forecast["outcome"] == "refused" and forecast["penalised"] is True
        res = V.refuse_petition(w, KOI, PLAYER, pet, how="unanswered")
        assert res["outcome"] == "unanswered" and res["penalty"] is True
        assert w.vassals[KOI]["loyalty"] == loy0 - 10 and _rel(w, KOI, PLAYER) == rel0 - 20

    def test_a_province_lost_in_war_withdraws_both_arms_free(self):
        w = _europe()
        _stage_tyrol_for_koi(w)
        pet = V.petition_terms(w, KOI)
        w.regions["Tyrol"].controller = "Austria"
        w.invalidate_active_nations_cache()
        assert V._province_lost_outside_the_lords_hands(w, PLAYER, KOI, "Tyrol")
        kind, message = V.petition_grant_verdict(w, PLAYER, KOI, pet)
        assert kind == "withdrawn" and "fell to another power" in message
        assert V.petition_grant_availability(w, PLAYER, KOI, pet) == (True, message)
        assert V.reprice_petition(w, PLAYER, KOI, pet) is None
        assert V.lapse_forecast(w, KOI, PLAYER, pet)["outcome"] == "withdrawn"
        loy0, rel0 = w.vassals[KOI]["loyalty"], _rel(w, KOI, PLAYER)
        res = V.refuse_petition(w, KOI, PLAYER, pet, how="unanswered")
        assert res["outcome"] == "withdrawn" and res["success"] is False
        assert w.vassals[KOI]["loyalty"] == loy0 and _rel(w, KOI, PLAYER) == rel0
        assert not _logged(w)

    def test_a_marshals_estate_abroad_is_not_a_loss_in_war(self):
        """Tyrol held by Austria but a live estate of a French marshal
        (respected abroad) — the lord's own doing, never waived."""
        w = _europe()
        _stage_tyrol_for_koi(w)
        w.regions["Tyrol"].controller = "Austria"
        w.invalidate_active_nations_cache()
        ney = w.marshals["Ney"]
        ney.dotation_regions = list(getattr(ney, "dotation_regions", []) or []) + ["Tyrol"]
        assert not V._province_lost_outside_the_lords_hands(w, PLAYER, KOI, "Tyrol")

    def test_the_fulfilled_predicate_needs_vs3s_own_provenance(self):
        w = _europe()
        _stage_tyrol_for_koi(w)
        pet = V.petition_terms(w, KOI)
        # the client holds it, but not by the lord's gift: no bond earned
        w.regions["Tyrol"].controller = KOI
        w.invalidate_active_nations_cache()
        assert not V.petition_is_fulfilled(w, KOI, PLAYER, pet)
        assert V.petition_grant_verdict(w, PLAYER, KOI, pet)[0] == "withdrawn"
        # ...and the refuse arm and the lapse forecast withdraw it too: a
        # province the client already holds is nothing to refuse, nothing is
        # charged (sweep IQ7R-R1j — the refuse arm's own "already holds" arm)
        loy0, rel0 = w.vassals[KOI]["loyalty"], _rel(w, KOI, PLAYER)
        assert V.lapse_forecast(w, KOI, PLAYER, pet)["outcome"] == "withdrawn"
        held = V.refuse_petition(w, KOI, PLAYER, pet, how="refused")
        assert held["outcome"] == "withdrawn" and "already holds" in held["message"]
        assert w.vassals[KOI]["loyalty"] == loy0 and _rel(w, KOI, PLAYER) == rel0
        assert not _logged(w)
        w.vassals[KOI]["granted_regions"] = ["Tyrol"]
        assert V.petition_is_fulfilled(w, KOI, PLAYER, pet)
        assert not V.petition_is_fulfilled(w, KOI, "Prussia", pet)              # lord unchanged
        assert not V.petition_is_fulfilled(w, KOI, PLAYER, {"subject": "relief"})
        w.regions["Tyrol"].controller = PLAYER                                  # gift not delivered
        assert not V.petition_is_fulfilled(w, KOI, PLAYER, pet)

    def test_lever_down_reproduces_the_7d10e20c_answers(self, monkeypatch):
        """The False arm, byte-for-byte on its surface: a typed cede stamps
        the grant cooldown, which the old order read as "withdrawn" (Grant
        paid 0), while the lapse and Refuse charged the refusal."""
        monkeypatch.setattr(V, "THE_DEED_HONOURS_THE_PETITION", False)

        def cede_then(answer):
            w = _europe()
            _stage_tyrol_for_koi(w)
            w.current_turn = 6
            pet = V.petition_terms(w, KOI)
            with _quiet():
                assert V.grant_region_to_vassal(w, KOI, "Tyrol", actor=PLAYER)["success"]
            dp0 = w.diplomatic_points
            if answer == "grant":
                res = V.grant_petition(w, KOI, PLAYER, pet)
            else:
                res = V.refuse_petition(w, KOI, PLAYER, pet, how=answer)
            return (res["outcome"], res["success"], w.vassals[KOI]["loyalty"],
                    _rel(w, KOI, PLAYER), w.diplomatic_points - dp0,
                    [(e["outcome"], e["penalty"]) for e in _logged(w)], res["message"])

        grant = cede_then("grant")
        assert grant[:6] == ("withdrawn", False, 100, 0, 0, [])
        assert "still being settled" in grant[6] and "withdrawn" in grant[6]
        lapse = cede_then("unanswered")
        assert lapse[:6] == ("unanswered", True, 90, -20, 0, [("unanswered", True)])
        refuse = cede_then("refused")
        assert refuse[:6] == ("refused", True, 90, -20, 0, [("refused", True)])
        assert not V.petition_is_fulfilled(_europe(), KOI, PLAYER, {"subject": "province"})


# ═══════════════════════════════════════════════════════════════════════════
# R2 — a lord who cannot pay has not answered
# ═══════════════════════════════════════════════════════════════════════════

def _spend_dp_to_zero(w, client):
    for verb in DP_SPENDS:
        if w.diplomatic_points <= 0:
            break
        _cmd(client, verb)
    assert w.diplomatic_points == 0, w.diplomatic_points


class TestR2TheLordPaysToGrant:
    """T11(d) is FLIPPED (see the module docstring); this is the flipped
    rule on the ORDINARY geometry — the petition queued, reached through
    the mailbox after the turn's DP was spent on ordinary verbs."""

    def test_a_dp_short_grant_stands_and_the_lapse_then_charges_the_refusal(self, board):
        w, client = board
        pet = _petition_of(w)
        _spend_dp_to_zero(w, client)
        assert _petitions(w) and _petitions(w)[0] is pet
        act = _activate(client, pet)["incoming_proposal"]
        assert act["grant_enabled"] is False and "diplomatic point" in act["grant_reason"]
        opt = next(o for o in act["options"] if o["action"] == "accept_ai_proposal")
        assert opt["enabled"] is False and opt["reason"] == act["grant_reason"]
        assert next(o for o in act["options"] if o["action"] == "reject_ai_proposal")["enabled"] is True
        loy0, rel0 = w.vassals[SWISS]["loyalty"], _rel(w, SWISS, PLAYER)
        r = _respond(client, "accept", pet["dialogue_id"])
        assert r.get("success") is False
        assert "stands until the turn ends" in str(r.get("message"))
        assert "keep 1 DP to grant it" in str(r.get("message"))
        assert _petitions(w) and _petitions(w)[0] is pet                  # not consumed
        assert "Petition from Switzerland" in _titles(w)                  # the rail notice kept
        assert not _logged(w)
        assert w.vassals[SWISS]["loyalty"] == loy0 and _rel(w, SWISS, PLAYER) == rel0
        assert "remission_left" not in w.vassals[SWISS]
        assert r.get("proposal_result") is None                           # no verdict reached
        assert r.get("diplomatic_dialogue") is not None                   # the question re-carried
        popup = r.get("incoming_proposal")
        assert popup["is_petition"] is True and popup["grant_enabled"] is False
        assert popup["dialogue_id"] == pet["dialogue_id"]
        r2 = _cmd(client, "grant the petition")
        assert r2.get("success") is False and "stands until the turn ends" in str(r2.get("message"))
        assert _petitions(w) and _petitions(w)[0] is pet
        _end_turn(client)
        rows = _logged(w)
        assert [(e["outcome"], e["penalty"]) for e in rows] == [("unanswered", True)]
        assert rows[0]["loyalty_after"] == rows[0]["loyalty_before"] - V.PETITION_REFUSAL_LOYALTY
        assert _rel(w, SWISS, PLAYER) == rel0 - V.PETITION_RELATION_STEP

    def test_the_availability_is_derived_at_every_read_never_baked(self, board):
        w, client = board
        pet = _petition_of(w)
        assert _activate(client, pet)["incoming_proposal"]["grant_enabled"] is True
        w.diplomatic_points = 0
        pe = _pending_envoy(client)["incoming_proposal"]
        assert pe["grant_enabled"] is False and "diplomatic point" in pe["grant_reason"]
        assert pe["dialogue_id"] == pet["dialogue_id"]
        # the dialogue's own option (the typed terminal's text) follows
        opt = next(o for o in pet["options"] if o["action"] == "accept_ai_proposal")
        assert opt["enabled"] is False and "diplomatic point" in opt["reason"]
        w.diplomatic_points = V.PETITION_DP_COST
        pe = _pending_envoy(client)["incoming_proposal"]
        assert pe["grant_enabled"] is True and pe["grant_reason"] == ""
        assert next(o for o in pet["options"] if o["action"] == "accept_ai_proposal")["enabled"] is True

    def test_the_verdict_seam_is_one_function(self):
        w = _europe()
        pet = V.petition_terms(w, SWISS)
        assert V.petition_grant_verdict(w, PLAYER, SWISS, pet) == ("ok", "")
        assert V.petition_grant_availability(w, PLAYER, SWISS, pet) == (True, "")
        w.diplomatic_points = 0
        kind, message = V.petition_grant_verdict(w, PLAYER, SWISS, pet)
        assert kind == "stands" and "cannot spare the diplomatic point" in message
        assert V.petition_grant_availability(w, PLAYER, SWISS, pet) == (False, message)
        res = V.grant_petition(w, SWISS, PLAYER, pet)
        assert res["outcome"] == "stands" and res["success"] is False and res["message"] == message
        assert "remission_left" not in w.vassals[SWISS] and not _logged(w)

    def test_the_delivered_options_carry_the_availability_at_delivery(self):
        """R2: the Grant option's `enabled`/`reason` come from the ONE
        availability function at DELIVERY too (sweep IQ7R-R2n) — a petition
        delivered to a lord with no DP in hand arrives with Grant honestly
        disabled, and the payload cached beside it says the same."""
        w = _europe()
        w.diplomatic_points = 0
        dlg = _deliver_only(w, SWISS)
        grant = next(o for o in dlg["options"] if o["action"] == "accept_ai_proposal")
        refuse = next(o for o in dlg["options"] if o["action"] == "reject_ai_proposal")
        assert grant["enabled"] is False and "diplomatic point" in grant["reason"]
        assert refuse["enabled"] is True and refuse["reason"] == ""
        assert dlg["popup_payload"]["grant_enabled"] is False
        w2 = _europe()
        dlg2 = _deliver_only(w2, SWISS)
        assert next(o for o in dlg2["options"] if o["action"] == "accept_ai_proposal")["enabled"] is True
        assert dlg2["popup_payload"]["grant_enabled"] is True

    def test_the_delivery_response_re_derives_the_cached_popup(self, monkeypatch):
        """R2/R4: the popup CACHED at delivery (DP in hand, Grant enabled) is
        re-derived at the moment a response hands it over — the passthrough
        runs the same refresh every other read seam runs (sweep IQ7R-R4m), so
        a DP spent before the first response never serves a baked Grant."""
        w = _europe()
        dlg = _deliver_only(w, SWISS)
        assert w.incoming_proposal_popup["grant_enabled"] is True
        w.diplomatic_points = 0
        client = _swap(monkeypatch, w)
        popup = _cmd(client, "status")["incoming_proposal"]
        assert popup["dialogue_id"] == dlg["dialogue_id"]
        assert popup["grant_enabled"] is False and "diplomatic point" in popup["grant_reason"]
        assert next(o for o in popup["options"] if o["action"] == "accept_ai_proposal")["enabled"] is False

    def test_lever_down_a_dp_short_grant_withdraws_like_7d10e20c(self, board, monkeypatch):
        monkeypatch.setattr(V, "THE_LORD_PAYS_TO_GRANT", False)
        w, client = board
        pet = _petition_of(w)
        _activate(client, pet)
        w.diplomatic_points = 0
        loy0, rel0 = w.vassals[SWISS]["loyalty"], _rel(w, SWISS, PLAYER)
        r = _respond(client, "accept", pet["dialogue_id"])
        assert r.get("success") is False
        assert "withdrawn" in str(r.get("message")) and "cannot spare the diplomatic point" in str(r.get("message"))
        assert not _petitions(w)                                          # consumed, free
        assert not _logged(w)
        assert w.vassals[SWISS]["loyalty"] == loy0 and _rel(w, SWISS, PLAYER) == rel0
        assert "remission_left" not in w.vassals[SWISS]
        assert "Petition from Switzerland" not in _titles(w)
        # R10 (copy, no lever): a withdrawal is never titled "Rejected"
        assert _verdict(client, r)["outcome"] == "WITHDRAWN"
        _end_turn(client)
        assert not _logged(w)                                             # nothing left to charge

    def test_gr5_the_ai_lord_maps_stands_to_a_refusal_at_the_same_price(self, monkeypatch):
        w = _holland_under_prussia()
        monkeypatch.setattr(V, "grant_petition",
                            lambda world, vassal, lord, petition: V._stands("cannot pay"))
        with _quiet():
            events = V.process_vassal_petitions(w)
        assert [(e["vassal"], e["lord"], e["outcome"]) for e in events] == [("Holland", "Prussia", "refused")]
        row = w.vassals["Holland"]
        assert row["loyalty"] == 80 - V.PETITION_REFUSAL_LOYALTY
        assert _rel(w, "Holland", "Prussia") == -V.PETITION_RELATION_STEP
        assert w.nation_dp["Prussia"] == 3
        assert [e["outcome"] for e in _logged(w)] == ["refused"]


# ═══════════════════════════════════════════════════════════════════════════
# R3 — the transfer sheds the remission
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def tribute_spy(monkeypatch):
    real = V.process_vassal_tribute
    records = []

    def spy(world):
        events = real(world)
        records.append({v: (int(e["amount"]), e.get("lord")) for v, e in events.items()})
        return events

    monkeypatch.setattr(V, "process_vassal_tribute", spy)
    return records


class TestR3TheTransferShedsTheRemission:
    def _relief_then_one_collection(self, w, client):
        pet = _petition_of(w)
        _activate(client, pet)
        r = _respond(client, "accept", pet["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        assert w.vassals[SWISS]["remission_left"] == V.REMISSION_COLLECTIONS
        _end_turn(client)
        assert w.vassals[SWISS]["remission_left"] == V.REMISSION_COLLECTIONS - 1

    def _bribe_away(self, w, monkeypatch):
        assert w.is_at_war("Britain", PLAYER)
        w.vassals[SWISS]["loyalty"] = 20
        monkeypatch.setattr(V.random, "random", lambda: 0.0)
        with _quiet():
            events = V.attempt_vassal_bribe(w, "Britain")
        assert any(e.get("type") == "vassal_defected" and e.get("outcome") == "transfer"
                   for e in events), events
        assert w.vassals[SWISS]["lord"] == "Britain"

    def test_vs6_the_bribed_away_client_pays_its_new_lord_in_full(self, board, monkeypatch, tribute_spy):
        w, client = board
        self._relief_then_one_collection(w, client)
        self._bribe_away(w, monkeypatch)
        row = w.vassals[SWISS]
        assert "remission_left" not in row and "petitioned_turn" not in row
        owed = V.vassal_tribute_owed(w, SWISS)
        assert owed > 0
        _end_turn(client)
        paid = tribute_spy[-1].get(SWISS)
        assert paid == (owed, "Britain"), (paid, owed)

    def test_vs5_france_claims_an_ai_lords_relieved_client_and_collects_in_full(self):
        w = _holland_under_prussia()
        with _quiet():
            events = V.process_vassal_petitions(w)
        assert [(e["lord"], e["outcome"]) for e in events] == [("Prussia", "granted")]
        assert w.vassals["Holland"]["remission_left"] == V.REMISSION_COLLECTIONS
        with _quiet():
            applied = _apply_settlement_terms(w, settlement_terms=[
                {"type": "vassal_transfer", "vassal": "Holland", "from": "Prussia", "to": PLAYER}])
        assert applied and applied[0]["type"] == "vassal_transfer"
        row = w.vassals["Holland"]
        assert row["lord"] == PLAYER
        assert "remission_left" not in row and "petitioned_turn" not in row
        owed = V.vassal_tribute_owed(w, "Holland")
        assert owed > 0
        card = next(x for x in build_diplomatic_ledger(w)["vassals"]["rows"] if x["name"] == "Holland")
        assert card["tribute"] == owed and card["remission_left"] == 0
        with _quiet():
            paid = V.process_vassal_tribute(w)
        assert (int(paid["Holland"]["amount"]), paid["Holland"].get("lord")) == (owed, PLAYER)

    def test_lever_down_the_remission_is_inherited_like_7d10e20c(self, board, monkeypatch, tribute_spy):
        monkeypatch.setattr(V, "THE_TRANSFER_SHEDS_THE_REMISSION", False)
        w, client = board
        self._relief_then_one_collection(w, client)
        stamped = w.vassals[SWISS]["petitioned_turn"]
        self._bribe_away(w, monkeypatch)
        row = w.vassals[SWISS]
        assert row["remission_left"] == V.REMISSION_COLLECTIONS - 1
        assert row["petitioned_turn"] == stamped
        assert V.vassal_tribute_owed(w, SWISS) == 0
        _end_turn(client)
        assert SWISS not in tribute_spy[-1]                                  # Britain paid nothing
        assert w.vassals[SWISS]["remission_left"] == V.REMISSION_COLLECTIONS - 2

    def test_the_vs3_interlock_is_untouched_beside_the_new_pops(self):
        w = _europe()
        row = w.vassals[SWISS]
        row["granted_regions"], row["grant_cooldown"] = ["X"], 2
        row["remission_left"], row["petitioned_turn"], row["created_turn"] = 3, 4, 1
        with _quiet():
            V.transfer_vassal(w, SWISS, "Prussia")
        row = w.vassals[SWISS]
        for key in ("granted_regions", "grant_cooldown", "remission_left", "petitioned_turn"):
            assert key not in row, key
        assert row["created_turn"] == 1                                    # never `created_turn`


# ═══════════════════════════════════════════════════════════════════════════
# R4 — one re-pricer on the STORED subject
# ═══════════════════════════════════════════════════════════════════════════

class TestR4OneRepricerOnTheStoredSubject:
    @pytest.mark.parametrize("verb", ["grant switzerland more autonomy", "reduce switzerland autonomy"])
    def test_every_read_quotes_the_live_price_and_the_grant_applies_it(self, board, verb):
        w, client = board
        pet = _petition_of(w)
        issued = pet["context"]["proposal"]["petition"]["price"]
        r = _cmd(client, verb)
        assert "Tribute rate" in str(r.get("message")), r.get("message")
        assert _petitions(w) and _petitions(w)[0] is pet
        live = V.vassal_tribute_owed(w, SWISS) * V.REMISSION_COLLECTIONS
        assert live != issued
        loy = w.vassals[SWISS]["loyalty"]
        quoted = _figures(_grant_clause(_activate(client, pet)["incoming_proposal"]["clauses"]))
        assert quoted[0] == live
        assert quoted[1] == min(V.PETITION_RELIEF_LOYALTY, V.LOYALTY_MAX - loy)
        assert _figures(_grant_clause(_pending_envoy(client)["incoming_proposal"]["clauses"]))[0] == live
        assert _figures(pet["options"][0]["description"])[0] == live
        assert pet["context"]["proposal"]["petition"]["price"] == live        # written back
        r = _respond(client, "accept", pet["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        applied = _figures(str(r.get("message")))
        assert applied == quoted
        row = w.vassals[SWISS]
        assert row["loyalty"] - loy == quoted[1]
        assert _rel(w, SWISS, PLAYER) == quoted[2]
        assert row["remission_left"] == V.REMISSION_COLLECTIONS
        assert r["proposal_result"]["outcome"] == "ACCEPT"
        # and the price the collections actually forgo is the one applied
        assert V.vassal_tribute_owed(w, SWISS) == 0

    def test_the_answer_handler_reprices_immediately_before_the_grant(self, board):
        w, client = board
        pet = _petition_of(w)
        act = _activate(client, pet)["incoming_proposal"]
        assert _figures(_grant_clause(act["clauses"]))[0] == pet["context"]["proposal"]["petition"]["price"]
        r = _cmd(client, "reduce switzerland autonomy")
        assert "Tribute rate" in str(r.get("message"))
        live = V.vassal_tribute_owed(w, SWISS) * V.REMISSION_COLLECTIONS
        r = _respond(client, "accept", pet["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        assert f"({live}g forgone)" in str(r.get("message"))
        assert pet["context"]["proposal"]["petition"]["price"] == live

    def test_the_stored_subject_is_never_re_decided(self, monkeypatch):
        w = _europe()
        _set_rel(w, KOI, PLAYER, -60)                                       # forecast +2-3 -> relief
        assert V.petition_subject(w, KOI)["subject"] == "relief"
        dlg = _deliver_only(w, KOI)
        client = _swap(monkeypatch, w)
        _cmd(client, "status")
        _stage_tyrol_for_koi(w)                                             # the live ladder now says province
        assert V.petition_subject(w, KOI)["subject"] == "province"
        stored = dlg["context"]["proposal"]["petition"]
        repriced = V.reprice_petition(w, PLAYER, KOI, stored)
        assert repriced["subject"] == "relief"
        assert repriced["price"] == V.vassal_tribute_owed(w, KOI) * V.REMISSION_COLLECTIONS
        popup = refresh_client_petition_dialogue(w, dlg)
        assert "tribute" in _grant_clause(popup["clauses"]) and "Tyrol" not in " ".join(popup["clauses"])
        r = _respond(client, "accept", dlg["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        assert w.vassals[KOI]["remission_left"] == V.REMISSION_COLLECTIONS
        assert w.regions["Tyrol"].controller == PLAYER
        assert not w.vassals[KOI].get("granted_regions")

    def test_a_recovered_forecast_does_not_withdraw_the_relief(self):
        w = _europe()
        pet = V.petition_terms(w, SWISS)
        _set_rel(w, SWISS, PLAYER, 40)                                      # forecast 0: the ladder would ask nothing
        assert V.petition_subject(w, SWISS) is None
        repriced = V.reprice_petition(w, PLAYER, SWISS, pet)
        assert repriced is not None and repriced["subject"] == "relief"
        assert repriced["relation_step"] == 0                               # live bond figures
        res = V.grant_petition(w, SWISS, PLAYER, pet)
        assert res["outcome"] == "granted" and w.vassals[SWISS]["remission_left"] == V.REMISSION_COLLECTIONS

    def test_a_relief_of_nothing_is_withdrawn_and_the_lever_restores_the_old_grant(self, monkeypatch):
        w = _europe()
        pet = V.petition_terms(w, SWISS)
        w.vassals[SWISS]["tribute_rate"] = 0.0
        assert V.vassal_tribute_owed(w, SWISS) == 0
        assert V.reprice_petition(w, PLAYER, SWISS, pet) is None
        dp0 = w.diplomatic_points
        res = V.grant_petition(w, SWISS, PLAYER, pet)
        assert res["outcome"] == "withdrawn" and "nothing to remit" in res["message"]
        assert "remission_left" not in w.vassals[SWISS] and w.diplomatic_points == dp0
        assert _rel(w, SWISS, PLAYER) == 0 and not _logged(w)
        monkeypatch.setattr(V, "A_RELIEF_OF_NOTHING_IS_WITHDRAWN", False)
        res = V.grant_petition(w, SWISS, PLAYER, pet)                       # 7d10e20c: granted anyway
        assert (res["outcome"], w.vassals[SWISS]["remission_left"], w.diplomatic_points,
                _rel(w, SWISS, PLAYER), [e["outcome"] for e in _logged(w)]) == (
            "granted", V.REMISSION_COLLECTIONS, dp0 - 1, 20, ["granted"])
        assert V.reprice_petition(w, PLAYER, SWISS, pet) is not None

    def test_the_refresh_leaves_an_ordinary_letter_alone(self):
        """The re-pricer is a PETITION seam: an ordinary letter is returned
        None and untouched (sweep IQ7R-R4k — a refresh that ran on every
        letter would stamp `is_petition` on Prussia's non-aggression pact)."""
        w = _europe()
        _clear_slot(w)
        letter = _deliver(w, _ordinary("Prussia", "non_aggression"))
        before = copy.deepcopy(letter)
        assert refresh_client_petition_dialogue(w, letter) is None
        assert letter == before
        assert not (letter.get("popup_payload") or {}).get("is_petition")

    def test_the_handler_writes_the_live_price_back_with_no_response_in_between(self, board):
        """R4: the answer handler's OWN re-price — not a read seam's — writes
        the live figures into the stored petition immediately before the
        grant (sweep IQ7R-R4n). The change is made directly on the world so
        that NO response is built between it and the answer: every response
        refreshes the current petition's popup on its own, which is why the
        typed-verb geometry above cannot tell the handler's refresh apart."""
        w, client = board
        pet = _petition_of(w)
        _activate(client, pet)
        issued = pet["context"]["proposal"]["petition"]["price"]
        w.vassals[SWISS]["tribute_rate"] = 0.9
        live = V.vassal_tribute_owed(w, SWISS) * V.REMISSION_COLLECTIONS
        assert live != issued and pet["context"]["proposal"]["petition"]["price"] == issued
        r = _cmd(client, "grant the petition")
        assert r.get("success") is True, r.get("message")
        assert f"({live}g forgone)" in str(r.get("message"))
        assert pet["context"]["proposal"]["petition"]["price"] == live
        assert f"({live}g forgone)" in pet["options"][0]["description"]

    @pytest.mark.parametrize("loyalty,gain,clause", [
        (96, 4, "loyalty +4 (to the 100 ceiling)"),
        (100, 0, "loyalty +0 (its loyalty is already full)"),
        (80, 10, "loyalty +10,"),
    ])
    def test_the_clamped_gain_is_quoted_and_applied(self, monkeypatch, loyalty, gain, clause):
        w = _europe()
        w.vassals[SWISS]["loyalty"] = loyalty
        dlg = _deliver_only(w, SWISS)
        pet = dlg["context"]["proposal"]["petition"]
        assert pet["loyalty_gain"] == gain and pet["loyalty_gain_raw"] == 10
        assert pet["loyalty_full"] is (loyalty == 100)
        assert clause in pet["grant_line"]
        client = _swap(monkeypatch, w)
        _cmd(client, "status")
        r = _respond(client, "accept", dlg["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        assert w.vassals[SWISS]["loyalty"] == loyalty + gain
        expected = (f"Loyalty +0 ({loyalty} → {loyalty}, already full)" if loyalty == 100
                    else f"Loyalty +{gain} ({loyalty} → {loyalty + gain})")
        assert expected in str(r.get("message"))
        assert _logged(w, "granted")[0]["loyalty_after"] == loyalty + gain


# ═══════════════════════════════════════════════════════════════════════════
# R5 — the province price names its parts (the drift pin)
# ═══════════════════════════════════════════════════════════════════════════

class TestR5TheProvincePriceNamesItsParts:
    @pytest.mark.parametrize("bankrupt", [False, True])
    @pytest.mark.parametrize("stability", [25, 40, 60, 80, 100])
    def test_the_quoted_net_equals_the_ledgers_applied_net(self, stability, bankrupt):
        w = _europe()
        _stage_tyrol_for_koi(w)
        w.regions["Tyrol"].stability = stability
        if bankrupt:
            w.nation_bankruptcy_turns[PLAYER] = 1
        parts = V.province_grant_price(w, PLAYER, KOI, "Tyrol")
        owed0 = V.vassal_tribute_owed(w, KOI)
        with _quiet():
            net0 = int(build_strategic_ledger(w)["economy"]["net"])
            assert V.grant_region_to_vassal(w, KOI, "Tyrol", actor=PLAYER)["success"]
            net1 = int(build_strategic_ledger(w)["economy"]["net"])
        assert parts["net_delta"] == net1 - net0, (parts, net0, net1)
        assert parts["tribute_gained"] == V.vassal_tribute_owed(w, KOI) - owed0
        assert parts["income_forfeited"] >= 0 and parts["occupation_relieved"] >= 0
        if not bankrupt and stability == 25:
            assert parts["net_delta"] > 0                                     # a fresh conquest PAYS to give away
        if not bankrupt and stability == 100:
            assert parts["net_delta"] < 0

    @pytest.mark.parametrize("stability", [25, 100])
    def test_the_grant_line_and_the_result_print_the_signed_net_and_the_parts(self, monkeypatch, stability):
        w, client, pet = _tyrol_board(monkeypatch, stability=stability)
        parts = V.province_grant_price(w, PLAYER, KOI, "Tyrol")
        line = V.province_price_line(parts, "the Kingdom of Italy")
        head = (f"Our net rises by {parts['net_delta']}g a turn" if parts["net_delta"] > 0
                else f"Our net falls by {-parts['net_delta']}g a turn")
        assert line.startswith(head)
        assert f"{parts['income_forfeited']}g of income forfeited" in line
        assert f"{parts['occupation_relieved']}g of occupation relieved" in line
        assert f"{parts['tribute_gained']}g returned as tribute at today's 75% rate" in line
        stored = pet["context"]["proposal"]["petition"]
        assert stored["grant_line"].endswith(line)
        assert stored["price_parts"]["net_delta"] == parts["net_delta"]
        r = _respond(client, "accept", pet["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        message = str(r.get("message"))
        assert line in message and "Cost: 1 DP." in message
        assert "the province's income" not in message                        # never "a cost" for a gain
        assert w.regions["Tyrol"].controller == KOI

    def test_a_standing_remission_names_no_tribute_returned(self):
        w = _europe()
        for name in ("Brunswick", "East Frisia", "Osnabruck"):
            w.regions[name].controller = PLAYER
        w.invalidate_active_nations_cache()
        w.vassals["Holland"]["remission_left"] = 3
        parts = V.province_grant_price(w, PLAYER, "Holland", "Brunswick")
        assert parts["remission_standing"] is True and parts["tribute_gained"] == 0
        assert "no tribute returned while Holland's remission stands" in V.province_price_line(parts, "Holland")
        w.vassals["Holland"]["remission_left"] = 0
        assert V.province_grant_price(w, PLAYER, "Holland", "Brunswick")["tribute_gained"] > 0

    def test_a_disrupted_province_forfeits_nothing_it_was_not_collecting(self):
        w = _europe()
        _stage_tyrol_for_koi(w)
        mack = w.marshals["Mack"]
        mack.location = "Tyrol"
        assert "Tyrol" in w.get_disrupted_regions()
        parts = V.province_grant_price(w, PLAYER, KOI, "Tyrol")
        assert parts["contributions_relief"] == parts["income_forfeited"] > 0
        assert parts["tribute_gained"] == 0
        assert "already suspended by the enemy on it" in V.province_price_line(parts)
        with _quiet():
            net0 = int(build_strategic_ledger(w)["economy"]["net"])
            assert V.grant_region_to_vassal(w, KOI, "Tyrol", actor=PLAYER)["success"]
            net1 = int(build_strategic_ledger(w)["economy"]["net"])
        assert parts["net_delta"] == net1 - net0

    def test_the_tribute_part_is_the_floor_of_the_sum_never_per_province(self):
        """The with/without arithmetic the collection uses (sweep IQ7R-R5b):
        on the boot board the Kingdom's base is 500 (375.0 exactly), so a
        per-province `income × rate` agrees on every cell — nudge Piedmont to
        202 (base 502 -> 376.5) and the per-province figure is off by one."""
        w = _europe()
        _stage_tyrol_for_koi(w)
        w.regions["Piedmont"].income_value = 202
        assert V._vassal_tributable_income(w, KOI) == 502
        tyrol = w.regions["Tyrol"].get_effective_income()
        assert tyrol == 150                                              # 112.5 on its own
        parts = V.province_grant_price(w, PLAYER, KOI, "Tyrol")
        assert parts["tribute_gained"] == 113
        assert parts["tribute_gained"] != int(tyrol * 0.75)
        owed0 = V.vassal_tribute_owed(w, KOI)
        with _quiet():
            assert V.grant_region_to_vassal(w, KOI, "Tyrol", actor=PLAYER)["success"]
        assert V.vassal_tribute_owed(w, KOI) - owed0 == parts["tribute_gained"]

    def test_the_relief_arm_is_unchanged(self):
        w = _europe()
        terms = V.petition_terms(w, SWISS)
        assert "(1800g forgone)" in terms["grant_line"] and "Our net" not in terms["grant_line"]
        assert "price_parts" not in terms


# ═══════════════════════════════════════════════════════════════════════════
# R6 — the refuse line quotes the applied figures
# ═══════════════════════════════════════════════════════════════════════════

class TestR6TheRefuseLineQuotesTheAppliedFigures:
    def test_at_the_relation_floor_the_step_and_the_after_figure_are_the_clamped_ones(self):
        w = _europe()
        _set_rel(w, SWISS, PLAYER, -90)
        terms = V.petition_terms(w, SWISS)
        assert terms["relation_refusal_step_applied"] == 10
        assert terms["relation_after_refusal"] == -100
        # floor division: -90 // 20 is -5 already, so the after-figure and
        # the now-figure agree — only the STEP shrinks at the floor.
        assert terms["standing_after_refusal"] == -5 and terms["standing_now"] == -5
        assert ("loses 10 loyalty and its bond with us falls 10 (-90 → -100: worth -5 a turn "
                "in loyalty, now -5)") in terms["refuse_line"]
        assert "drift" not in terms["refuse_line"] and "standing" not in terms["refuse_line"]
        loy0 = w.vassals[SWISS]["loyalty"]
        res = V.refuse_petition(w, SWISS, PLAYER, terms, how="refused")
        assert _rel(w, SWISS, PLAYER) == -100 and w.vassals[SWISS]["loyalty"] == loy0 - 10
        assert "bond -90 → -100 (-5 a turn)" in res["message"]
        assert V.forecast_vassal_loyalty(w, PLAYER, SWISS)["relation_modifier"] == terms["standing_after_refusal"]

    def test_at_the_loyalty_floor_the_loss_is_what_is_left(self):
        w = _europe()
        w.vassals[SWISS]["loyalty"] = 5
        terms = V.petition_terms(w, SWISS)
        assert terms["refusal_loyalty_applied"] == 5 and "loses 5 loyalty" in terms["refuse_line"]
        res = V.refuse_petition(w, SWISS, PLAYER, terms, how="refused")
        assert w.vassals[SWISS]["loyalty"] == 0 and "loyalty −5 (5 → 0)" in res["message"]

    def test_the_grant_and_refuse_clauses_name_the_bond_in_the_same_terms(self):
        w = _europe()
        terms = V.petition_terms(w, SWISS)
        assert "its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0)" in terms["grant_line"]
        assert "its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now +0)" in terms["refuse_line"]
        assert terms["relation_after_grant"] == 20 and terms["relation_after_refusal"] == -20

    def test_through_the_endpoint_the_refusal_message_is_the_state_delta(self, board):
        w, client = board
        pet = _petition_of(w)
        clauses = _activate(client, pet)["incoming_proposal"]["clauses"]
        refuse_clause = next(c for c in clauses if c.startswith("Refuse it"))
        loy0, rel0 = w.vassals[SWISS]["loyalty"], _rel(w, SWISS, PLAYER)
        assert f"loses {min(10, loy0)} loyalty and its bond with us falls 20 ({rel0} → {rel0 - 20}" in refuse_clause
        r = _respond(client, "reject", pet["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        loy1, rel1 = w.vassals[SWISS]["loyalty"], _rel(w, SWISS, PLAYER)
        assert f"loyalty −{loy0 - loy1} ({loy0} → {loy1}); bond {rel0} → {rel1} ({V._standing(rel1):+d} a turn)" in str(r.get("message"))
        assert (loy1, rel1) == (loy0 - 10, rel0 - 20)


# ═══════════════════════════════════════════════════════════════════════════
# R7 — the card tells the truth
# ═══════════════════════════════════════════════════════════════════════════

def _card(w, name):
    with _quiet():
        rows = build_diplomatic_ledger(w)["vassals"]["rows"]
    return next(x for x in rows if x["name"] == name)


class TestR7TheCardTellsTheTruth:
    def test_the_countdown_and_may_petition_are_kept_through_real_end_turns(self, monkeypatch):
        """Builder A's R7 measurement, as a pin: the card at turn T says
        "may petition" -> the petition is issued at the advance into T+1;
        "N turns until it may ask" -> issued at exactly T+N and never
        earlier; the [20] off-by-one (a relief remission of r reads r+1)
        closed on the remission that follows the turn-6 grant."""
        w = _europe()
        _park(w, SWISS)
        client = _swap(monkeypatch, w)
        issued, predictions, granted = set(), [], False
        while int(w.current_turn) < 16:
            card = _card(w, SWISS)
            predictions.append((int(w.current_turn), card["standing"], card["standing_key"],
                                card["next_petition_in"], card["remission_left"]))
            if int(w.current_turn) == 13:
                # Row EP F5 (September 25, 2026): the second cycle's SUBJECT
                # had been a board accident. Bern adjoins only French homeland,
                # so THE PROVINCE arm can never fire for the Swiss on this map;
                # the turn-15 petition was THE RELIEF arm, which needs a
                # FALLING loyalty forecast — and on the pre-F5 ambient board
                # France's own state happened to supply one at turn 14. With
                # Bavaria's walk-ins capped it did not (the card read "nothing
                # to ask for"; measured in both lever arms). The precondition
                # is staged explicitly now, not borrowed from the AI board: a
                # soured lord relation (-60 // 20 = -3) makes the forecast
                # fall, so the cadence's expiry has something to ask for.
                _set_rel(w, SWISS, PLAYER, -60)
            _end_turn(client)
            if w.vassals[SWISS].get("petitioned_turn") == w.current_turn:
                issued.add(int(w.current_turn))
                pets = _petitions(w)
                if pets and not granted:
                    _activate(client, pets[0])
                    r = _respond(client, "grant the petition", pets[0]["dialogue_id"])
                    assert r.get("success") is True, r.get("message")
                    granted = True
        horizon = int(w.current_turn)
        assert issued == {6, 15}
        by_turn = {t: (standing, key, n, rem) for t, standing, key, n, rem in predictions}
        assert by_turn[1] == ("5 turns until it may ask", "grace", 5, 0)
        # the grace's last turn: eligible at the next advance, countdown 1
        assert by_turn[5] == ("may petition", "eligible", 1, 0)
        # after the grant the FIRST failing gate in producer order is the
        # cadence (8), but the countdown is the LONGEST wait — the remission
        # of 8 reads 9, never 8 (the [20] off-by-one closed)
        assert by_turn[6] == ("9 turns until it may ask", "cadence", 9, 8)
        # the copy's figure is the countdown's (the longest wait), never the
        # named gate's own shorter one: cadence 2, remission 2+1 — "3 turns"
        assert by_turn[12] == ("3 turns until it may ask", "cadence", 3, 2)
        # the cadence has cleared; the last collection still blocks the next advance
        assert by_turn[13] == ("relief running, 1 collection", "remission", 2, 1)
        assert by_turn[14] == ("may petition", "eligible", 0, 0)
        checked = 0
        for t, standing, key, n, rem in predictions:
            if standing == "may petition" and t + 1 <= horizon:
                assert (t + 1) in issued, (t, standing, n)
                checked += 1
            elif standing != "may petition" and n > 0 and t + n <= horizon:
                assert (t + n) in issued and not any(t < k < t + n for k in issued), (t, standing, n)
                checked += 1
        assert checked >= 13, checked

    def test_the_standing_names_the_blocking_gate_and_never_a_second_standing(self):
        w = _europe()
        w.current_turn = 6
        for name in ("Holland", KOI, SWISS):
            w.vassals[name]["created_turn"] = 1
        # Holland at boot: forecast 0, no province, relation 0 -> nothing to ask
        assert _card(w, "Holland")["standing"] == "nothing to ask for"
        assert _card(w, "Holland")["standing_key"] == "no_subject"
        # bonded: relation at the cap, forecast 0
        _set_rel(w, SWISS, PLAYER, 40)
        card = _card(w, SWISS)
        assert card["standing"] == "bonded — nothing to ask" and card["standing_key"] == "bonded"
        assert card["bond"] == "+2/turn — a bond worth two honoured petitions (bond 40)"
        _set_rel(w, SWISS, PLAYER, 0)
        assert _card(w, SWISS)["standing"] == "may petition"
        # below the standing to petition
        w.vassals[SWISS]["loyalty"] = 50
        card = _card(w, SWISS)
        assert card["standing"] == "no standing to petition" and card["standing_key"] == "loyalty"
        w.vassals[SWISS]["loyalty"] = 100
        # a disrupted province
        w.marshals["ArchdukeJohn"].location = "Milan"
        _set_rel(w, KOI, PLAYER, -100)
        assert _card(w, KOI)["standing"] == "a province is disrupted"
        # a standing remission on a province ask reads r+1
        for name in ("Brunswick", "East Frisia", "Osnabruck"):
            w.regions[name].controller = PLAYER
        w.invalidate_active_nations_cache()
        w.vassals["Holland"]["remission_left"] = 3
        card = _card(w, "Holland")
        assert card["standing"] == "relief running, 3 collections" and card["next_petition_in"] == 4
        # "standing" means ONE thing: the relation is the bond, never a second standing
        _set_rel(w, "Holland", PLAYER, -20)
        card = _card(w, "Holland")
        assert card["bond"] == "-1/turn — bond spent (-20)"
        assert "spent" not in card["standing"] and "bond" not in card["standing"]

    def test_the_card_skips_the_dp_gate_the_producer_reads_live(self):
        w = _europe()
        w.current_turn = 6
        w.vassals[SWISS]["created_turn"] = 1
        w.diplomatic_points = 0
        assert _card(w, SWISS)["standing"] == "may petition"                  # DP regenerates before the producer
        assert V.petition_gate_verdict(w, PLAYER, SWISS) == (True, "eligible", 0)
        assert V.petition_gate_verdict(w, PLAYER, SWISS, projected=False) == (False, "dp", 0)

    def test_the_producer_and_the_card_read_one_gate(self):
        """Drift pin: for every satellite on a staged board, the verdict at
        the producer's own turn decides whether the producer issues."""
        w = _europe()
        w.current_turn = 5
        for name in ("Holland", KOI, SWISS):
            w.vassals[name]["created_turn"] = 1
        _set_rel(w, KOI, PLAYER, -100)                                        # relief for the Kingdom too
        w.vassals["Holland"]["loyalty"] = 55                                  # no standing
        expected = {name: V.petition_gate_verdict(w, PLAYER, name, turn=6, projected=False)[0]
                    for name in ("Holland", KOI, SWISS)}
        assert expected == {"Holland": False, KOI: True, SWISS: True}
        w.current_turn = 6
        with _quiet():
            V.process_vassal_petitions(w)
        issued = {name: w.vassals[name].get("petitioned_turn") == 6 for name in expected}
        # one per lord per turn: the first eligible in tag order is asked
        assert issued == {"Holland": False, KOI: True, SWISS: False}
        assert V.petition_gate_verdict(w, PLAYER, SWISS, turn=7, projected=False)[0] is True

    def test_the_card_is_empty_where_petitions_are_not_live(self, monkeypatch):
        w = _europe()
        assert V.petitions_live(w) is True
        assert "standing" in _card(w, SWISS)
        monkeypatch.setattr(V, "THE_CLIENT_PETITIONS", False)
        assert V.petitions_live(w) is False
        assert V.petition_standing_keys(w, SWISS) == {}
        assert V.petition_gate_verdict(w, PLAYER, SWISS) == (False, "dormant", 0)
        assert "standing" not in _card(w, SWISS)


# ═══════════════════════════════════════════════════════════════════════════
# R8 — the lapse is priced aloud (the petition QUEUED, never a modal)
# ═══════════════════════════════════════════════════════════════════════════

class TestR8TheLapseIsPricedAloud:
    def test_the_rail_states_the_rule_and_the_price_on_arrival(self, board):
        w, client = board
        body = _notice_body(w, "Petition from Switzerland")
        assert body.startswith("An envoy from Switzerland has arrived with a petition.")
        assert "Grant it (keep 1 DP in hand), or refuse it" in body
        assert "Left unanswered it counts as a refusal: −10 loyalty, −20 bond." in body

    def test_lever_down_the_rail_promises_no_price(self, monkeypatch):
        monkeypatch.setattr(V, "AN_UNANSWERED_PETITION_IS_REFUSED", False)
        w = _europe()
        _deliver_only(w, SWISS)
        body = _notice_body(w, "Petition from Switzerland")
        assert "counts as a refusal" not in body and "−10" not in body
        assert f"waits {V.PETITION_INTERVAL_TURNS} turns before asking again" in body

    def test_the_end_turn_gate_names_the_priced_petition_and_forgets_an_answered_one(self, board):
        w, client = board
        pet = _petition_of(w)
        r = _cmd(client, "status")
        assert int(r["pending_lapsing_count"]) >= 1
        lp = r["pending_lapsing_petitions"]
        assert lp == [{"vassal": SWISS, "court": SWISS, "refused": True,
                       "price_line": "Switzerland — −10 loyalty / −20 bond (a lapse is a refusal)"}]
        _activate(client, pet)
        r = _respond(client, "reject", pet["dialogue_id"])
        assert r.get("success") is True
        assert r["pending_lapsing_petitions"] == []                           # re-derived, never cached

    def test_lever_down_the_gate_says_lapse_not_refused(self, board, monkeypatch):
        monkeypatch.setattr(V, "AN_UNANSWERED_PETITION_IS_REFUSED", False)
        w, client = board
        lp = _cmd(client, "status")["pending_lapsing_petitions"]
        assert len(lp) == 1 and lp[0]["refused"] is False
        assert "lapses free" in lp[0]["price_line"] and "−10" not in lp[0]["price_line"]

    def test_the_queued_lapse_reaches_every_end_turn_surface(self, board):
        w, client = board
        pet = _petition_of(w)
        assert _pending(w)[0] is not pet                                     # QUEUED, never a modal
        r = _end_turn(client)
        rows = _logged(w)
        assert [(e["outcome"], e["penalty"]) for e in rows] == [("unanswered", True)]
        lb, la, rb, ra = (rows[0]["loyalty_before"], rows[0]["loyalty_after"],
                          rows[0]["relation_before"], rows[0]["relation_after"])
        assert (la, ra) == (lb - 10, rb - 20)
        price = f"loyalty −10 ({lb} → {la})"
        bond = f"bond {rb} → {ra}"
        # (b) the receipt on the end-turn events, in refuse_petition's own words
        receipt = [e for e in r["events"] if e.get("type") == "client_petition_answered"]
        assert len(receipt) == 1 and receipt[0]["nation"] == PLAYER
        assert receipt[0]["message"] == (
            f"Switzerland's petition for relief went unanswered and lapses as a refusal: "
            f"{price}; {bond} ({V._standing(ra):+d} a turn). Nothing is charged.")
        # (c) the loyalty tick reports the WHOLE move and names the refusal first
        tick = [e for e in r["events"] if e.get("type") == "vassal_loyalty" and e.get("vassal") == SWISS]
        assert len(tick) == 1
        assert tick[0]["delta"] == w.vassals[SWISS]["loyalty"] - lb
        assert tick[0]["old_loyalty"] == lb and tick[0]["petition_refused"] is True
        assert tick[0]["reason"].startswith("refused petition")
        assert tick[0]["message"].startswith(f"Switzerland loyalty {w.vassals[SWISS]['loyalty']} ({tick[0]['delta']}): refused petition")
        assert r["events"].index(receipt[0]) < r["events"].index(tick[0])
        # (b) LAPSED ENVOYS and the morning dispatch
        dispatch = r["morning_dispatch"]
        row = next(x for x in dispatch["lapsed_offers"] if x["nation"] == SWISS)
        assert row["is_petition"] is True and row["outcome"] == "unanswered" and row["penalty"] is True
        assert row["line"] == receipt[0]["message"]
        turn_receipt = [e for e in dispatch["turn_events"] if e.get("type") == "client_petition_answered"]
        assert turn_receipt and turn_receipt[0]["severity"] == "warning"
        assert price in turn_receipt[0]["message"]
        # (e) the campaign log, both rows priced; the copy clean
        blob = _campaign_log_blob(client)
        assert f"Switzerland's petition lapsed unanswered — refused: loyalty {lb} → {la}, bond {rb} → {ra}" in blob
        assert f"Switzerland's petition for relief from tribute — left unanswered, refused: loyalty {lb} → {la}, bond {rb} → {ra}." in blob
        assert "An envoy from Switzerland has arrived with a petition" in blob
        assert "an a " not in blob and "(Client Petition)" not in blob

    def test_lever_down_the_queued_lapse_is_free_on_every_surface(self, board, monkeypatch):
        monkeypatch.setattr(V, "AN_UNANSWERED_PETITION_IS_REFUSED", False)
        w, client = board
        loy0, rel0 = w.vassals[SWISS]["loyalty"], _rel(w, SWISS, PLAYER)
        r = _end_turn(client)
        rows = _logged(w)
        assert [(e["outcome"], e["penalty"]) for e in rows] == [("unanswered", False)]
        assert rows[0]["loyalty_after"] == loy0 and _rel(w, SWISS, PLAYER) == rel0
        receipt = [e for e in r["events"] if e.get("type") == "client_petition_answered"]
        assert receipt[0]["message"] == "Switzerland's petition for relief went unanswered and lapses; it costs nothing."
        assert receipt[0]["penalty"] is False
        tick = [e for e in r["events"] if e.get("type") == "vassal_loyalty" and e.get("vassal") == SWISS]
        assert all(not e.get("petition_refused") and "refused" not in str(e.get("reason")) for e in tick)
        row = next(x for x in r["morning_dispatch"]["lapsed_offers"] if x["nation"] == SWISS)
        assert row["penalty"] is False and row["line"].endswith("it costs nothing.")
        turn_receipt = [e for e in r["morning_dispatch"]["turn_events"] if e.get("type") == "client_petition_answered"]
        assert turn_receipt and turn_receipt[0]["severity"] == "info"
        blob = _campaign_log_blob(client)
        assert "Switzerland's petition lapsed unanswered — nothing charged" in blob
        assert "Switzerland's petition for relief from tribute — left unanswered." in blob
        assert "left unanswered, refused" not in blob

    def test_a_lapse_under_the_tick_gate_gets_its_own_loyalty_line(self):
        """R8(c): when the turn's drift fell under the >= 2 event gate there
        is no `vassal_loyalty` tick to re-base, so the refusal — the whole
        move — gets the line itself, after its receipt (sweep IQ7R-R8r)."""
        from backend.game_logic.turn_manager import _thread_petition_lapses
        w = _europe()
        w.vassals[SWISS]["loyalty"] = 74
        lapse = {"vassal": SWISS, "lord": PLAYER, "subject": "relief", "region": None,
                 "result": {"outcome": "unanswered", "penalty": True,
                            "loyalty_before": 84, "loyalty_after": 74,
                            "relation_before": 0, "relation_after": -20,
                            "message": "Switzerland's petition for relief went unanswered "
                                       "and lapses as a refusal."}}
        events = _thread_petition_lapses(w, [], [lapse])
        assert [e["type"] for e in events] == ["client_petition_answered", "vassal_loyalty"]
        tick = events[1]
        assert tick["vassal"] == SWISS and tick["nation"] == PLAYER
        assert (tick["old_loyalty"], tick["new_loyalty"], tick["delta"]) == (84, 74, -10)
        assert tick["reason"] == "refused petition" and tick["petition_refused"] is True
        assert tick["message"] == "Switzerland loyalty 74 (-10): refused petition"
        # a free lapse (the lever down) re-bases nothing and adds no line
        free = dict(lapse, result=dict(lapse["result"], penalty=False))
        assert [e["type"] for e in _thread_petition_lapses(w, [], [free])] == ["client_petition_answered"]

    def test_a_petition_made_moot_before_the_lapse_carries_no_price(self, board):
        w, client = board
        with _quiet():
            V.transfer_vassal(w, SWISS, "Prussia")
        r = _end_turn(client)
        assert not _logged(w)
        receipt = [e for e in r["events"] if e.get("type") == "client_petition_answered"]
        assert receipt and receipt[0]["outcome"] == "withdrawn" and "moot" in receipt[0]["message"]
        assert receipt[0]["penalty"] is False
        row = next(x for x in r["morning_dispatch"]["lapsed_offers"] if x["nation"] == SWISS)
        assert row["outcome"] == "withdrawn" and row["penalty"] is False and "moot" in row["line"]
        assert "Switzerland's petition lapsed unanswered — moot, nothing charged" in _campaign_log_blob(client)
        # the reset loyalty ticked once under its new lord; never the −10
        assert w.vassals[SWISS]["loyalty"] >= V.TRANSFER_LOYALTY_RESET - 4


# ═══════════════════════════════════════════════════════════════════════════
# R9 — the matter noun is an addressee
# ═══════════════════════════════════════════════════════════════════════════

MISROUTED_PHRASES = ("accept the petition", "yes, grant the petition", "decline the petition",
                     "reject the petition", "grant the petition", "refuse the petition",
                     "grant it", "refuse it", "do not accept the petition",
                     "accept the petitions", "the petition's terms are agreed")


class TestR9TheMatterNounIsAnAddressee:
    def _letter_on_top(self, board):
        w, client = board
        offer = _pending(w)[0]
        assert offer["type"] == "incoming_settlement_offer"
        r = _respond(client, "reject_settlement_offer", offer["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        top = w.dialogue_manager.peek()
        assert top is not None and not V.is_client_petition(top)
        assert _petitions(w)
        return w, client, top

    @pytest.mark.parametrize("phrase", MISROUTED_PHRASES)
    def test_a_typed_petition_answer_never_answers_the_letter_on_top(self, board, phrase):
        w, client, top = self._letter_on_top(board)
        pet = _petition_of(w)
        states0 = dict(w.diplomatic_states)
        refusals0 = copy.deepcopy(w.diplomatic_refusals)
        r = _cmd(client, phrase)
        msg = str(r.get("message"))
        assert r.get("success") is False, msg
        assert "Switzerland's petition waits in Envoys — open Envoys and answer it there." in msg
        assert msg.startswith("Sire — that answer would be delivered to ")
        assert dict(w.diplomatic_states) == states0 and w.diplomatic_refusals == refusals0
        assert w.dialogue_manager.peek() is top
        assert _petitions(w) and _petitions(w)[0] is pet and not _logged(w)

    def test_a_bare_accept_still_answers_the_letter_on_top(self, board):
        w, client, top = self._letter_on_top(board)
        r = _cmd(client, "accept")
        assert r.get("success") is True and "accepted" in str(r.get("message")).lower()
        assert w.dialogue_manager.peek() is not top and _petitions(w)

    def test_a_line_that_also_names_the_active_court_proceeds(self, board):
        w, client, top = self._letter_on_top(board)
        court = top.get("target_nation")
        r = _cmd(client, f"never mind the petition, accept {court}'s proposal")
        assert r.get("success") is True, r.get("message")
        assert w.dialogue_manager.peek() is not top

    def test_the_handler_seam_refuses_the_same_line(self, board):
        """The second seam: the handler's own raw-text check, which the
        `/command` router reaches for a line the active letter DID claim
        (`accept` is Portugal's own option). Called as the router calls it —
        `/respond_to_diplomatic_dialogue` carries no `raw_text` at all, so
        neither the court guard nor this one can fire on that id-bound
        button route (measured: pre-existing, both guards)."""
        w, client, top = self._letter_on_top(board)
        states0 = dict(w.diplomatic_states)
        with _quiet():
            r = M.executor.handle_diplomatic_dialogue_response(
                "accept", {"world": w}, raw_text="accept the petition")
        assert r.get("success") is False and r.get("matter_mismatch") is True
        assert "Switzerland's petition waits in Envoys" in str(r.get("message"))
        assert _petitions(w) and not _logged(w)
        assert dict(w.diplomatic_states) == states0 and w.dialogue_manager.peek() is top
        # and without the noun the same call answers the letter (the seam is
        # the noun, not the route)
        with _quiet():
            r = M.executor.handle_diplomatic_dialogue_response(
                "accept", {"world": w}, raw_text="accept")
        assert r.get("success") is True and w.dialogue_manager.peek() is not top

    @pytest.mark.parametrize("phrase,outcome", [
        ("grant the petition", "granted"), ("grant it", "granted"), ("grant", "granted"),
        ("refuse it", "refused"), ("refuse", "refused"), ("refuse the petition", "refused"),
    ])
    def test_the_petitions_own_words_answer_it_when_it_is_current(self, board, phrase, outcome):
        w, client = board
        pet = _petition_of(w)
        _activate(client, pet)
        assert V.is_client_petition(w.dialogue_manager.peek())
        r = _cmd(client, phrase)
        assert r.get("success") is True, r.get("message")
        assert [e["outcome"] for e in _logged(w)] == [outcome] and not _petitions(w)

    @pytest.mark.parametrize("phrase", ["do not grant the petition", "grant it later", "not now",
                                        "grant it more autonomy", "never grant it"])
    def test_a_negated_or_deferred_answer_never_grants(self, board, phrase):
        w, client = board
        pet = _petition_of(w)
        _activate(client, pet)
        dp0, autonomy0 = w.diplomatic_points, w.vassals[SWISS]["autonomy"]
        _cmd(client, phrase)
        assert not _logged(w) and _petitions(w) and _petitions(w)[0] is pet
        assert "remission_left" not in w.vassals[SWISS] and w.diplomatic_points == dp0
        assert w.vassals[SWISS]["autonomy"] == autonomy0

    def test_the_vocabulary_is_whole_line_only(self):
        assert petition_vocabulary_answer("grant it") == "accept_ai_proposal"
        assert petition_vocabulary_answer("grant the petition, sire") == "accept_ai_proposal"
        assert petition_vocabulary_answer("refuse") == "reject_ai_proposal"
        assert petition_vocabulary_answer("grant it more autonomy") is None
        assert petition_vocabulary_answer("grant it later") is None
        assert petition_vocabulary_answer("refuse Prussia's demand") is None

    def test_the_family_rules_at_the_guard(self):
        w = _europe()
        _clear_slot(w)
        letter = _deliver(w, _ordinary("Prussia", "non_aggression"))
        petition = _deliver(w, _make_proposal(w, SWISS))
        assert w.dialogue_manager.peek() is letter and petition in list(w.dialogue_manager.iter_queue())
        refusal = matter_mismatch_refusal(w, letter, "accept the petition")
        assert refusal and refusal["matter_family"] == "petition"
        assert "Switzerland's petition waits in Envoys" in refusal["message"]
        # a line naming a family the ACTIVE dialogue itself belongs to proceeds
        ally = {"type": "ally_settlement_petition", "target_nation": "Spain",
                "options": [{"label": "Decline", "action": "decline"}], "context": {}}
        assert matter_mismatch_refusal(w, ally, "decline the petition") is None
        # with no petition queued the line falls through as before
        w.dialogue_manager._queue = []
        assert matter_mismatch_refusal(w, letter, "accept the petition") is None
        # the other families, and the court named with its article
        w2 = _europe()
        _clear_slot(w2)
        letter2 = _deliver(w2, _ordinary("Prussia", "non_aggression"))
        _set_rel(w2, KOI, PLAYER, -60)
        _deliver(w2, _make_proposal(w2, KOI))
        w2.dialogue_manager._queue.append({"type": "incoming_ultimatum", "target_nation": "Austria",
                                           "dialogue_id": 999, "options": [], "context": {}})
        r = matter_mismatch_refusal(w2, letter2, "reject the ultimatum")
        assert r and r["matter_family"] == "ultimatum" and "Austria's ultimatum waits in Envoys" in r["message"]
        r = matter_mismatch_refusal(w2, letter2, "grant the petition")
        assert r and "The Kingdom of Italy's petition waits in Envoys" in r["message"]


# ═══════════════════════════════════════════════════════════════════════════
# R10 — copy: articles, the withdrawn outcome, the Garrison option, the
#       wavering card key, the School of War
# ═══════════════════════════════════════════════════════════════════════════

class TestR10Copy:
    def test_the_court_name_composes_its_article_at_the_sentence(self):
        w = _europe()
        assert V._court_name(w, KOI) == "Kingdom of Italy"
        assert V._court_name(w, KOI, article=True) == "the Kingdom of Italy"
        assert V._court_name(w, KOI, article=True, capitalize=True) == "The Kingdom of Italy"
        assert V._court_name(w, SWISS, article=True) == "Switzerland"
        _set_rel(w, KOI, PLAYER, -60)
        terms = V.petition_terms(w, KOI)
        assert terms["vassal_display"] == "Kingdom of Italy"                # the stored key stays bare
        assert terms["vassal_display_the"] == "the Kingdom of Italy"
        assert "Grant it, and the Kingdom of Italy's tribute" in terms["grant_line"]
        assert "Refuse it, and the Kingdom of Italy loses" in terms["refuse_line"]
        res = V.refuse_petition(w, KOI, PLAYER, terms, how="refused")
        assert res["message"].startswith("The Kingdom of Italy's petition for relief is refused")

    def test_the_rail_names_the_court_with_its_article(self):
        """R10: the rail notice composes the article on the court (sweep
        IQ7R-C7 — Switzerland takes none, so the board pin cannot see it)."""
        w = _europe()
        _set_rel(w, KOI, PLAYER, -60)
        _deliver_only(w, KOI)
        # PIN FLIPPED, pass 3 (Sept 19, 2026, R3-8): the TITLE takes the
        # article too — this lookup keyed on the bare "Petition from Kingdom
        # of Italy", which is the very copy the second verifier filed.
        assert "Petition from Kingdom of Italy" not in _titles(w)
        body = _notice_body(w, "Petition from the Kingdom of Italy")
        assert body.startswith("An envoy from the Kingdom of Italy has arrived with a petition.")

    def test_the_one_liners_and_the_dispatch_arrival(self):
        assert CL.format_event_oneliner({"type": "proposal_arrived", "source": KOI,
                                         "proposal_type": "client_petition",
                                         "decision_reason": "client_petition"}) == (
            "An envoy from the Kingdom of Italy has arrived with a petition")
        base = {"type": "offer_lapsed", "nation": KOI, "proposal_type": "client_petition"}
        assert CL.format_event_oneliner({**base, "petition": {"outcome": "withdrawn"}}) == (
            "The Kingdom of Italy's petition lapsed unanswered — moot, nothing charged")
        assert CL.format_event_oneliner({**base, "petition": {
            "outcome": "unanswered", "penalty": True, "loyalty_before": 84, "loyalty_after": 74,
            "relation_before": 0, "relation_after": -20}}) == (
            "The Kingdom of Italy's petition lapsed unanswered — refused: loyalty 84 → 74, bond 0 → -20")
        assert CL.format_event_oneliner({**base, "petition": {"outcome": "unanswered", "penalty": False}}) == (
            "The Kingdom of Italy's petition lapsed unanswered — nothing charged")
        answered = {"type": "client_petition_answered", "vassal": KOI, "lord": PLAYER,
                    "subject": "province", "region": "Tyrol"}
        assert CL.format_event_oneliner({**answered, "outcome": "withdrawn"}) == (
            "The Kingdom of Italy's petition for Tyrol — withdrawn, nothing charged.")
        assert CL.format_event_oneliner({**answered, "outcome": "refused", "penalty": True,
                                         "loyalty_before": 100, "loyalty_after": 90,
                                         "relation_before": 0, "relation_after": -20}) == (
            "The Kingdom of Italy's petition for Tyrol — refused: loyalty 100 → 90, bond 0 → -20.")
        assert _format_dispatch_event_text("diplomatic_ai_proposal", {
            "nation": KOI, "proposal_type": "client_petition"}) == (
            "An envoy from the Kingdom of Italy has arrived with a petition.")
        assert "with a proposal." in _format_dispatch_event_text("diplomatic_ai_proposal", {"nation": "Prussia"})

    def test_the_arrival_row_on_the_board_reads_petition(self, board):
        w, client = board
        blob = _campaign_log_blob(client)
        assert "An envoy from Switzerland has arrived with a petition" in blob
        assert "an a " not in blob and "(Client Petition)" not in blob
        dispatch = getattr(w, "last_morning_dispatch", None) or {}
        dispatch_lines = [str(e.get("text") or e.get("message") or "")
                          for e in dispatch.get("diplomatic_events", [])]
        assert "An envoy from Switzerland has arrived with a petition." in dispatch_lines, dispatch_lines
        assert not any("with a proposal" in line and "Switzerland" in line for line in dispatch_lines)

    def test_a_withdrawn_answer_is_never_titled_rejected(self, board):
        w, client = board
        pet = _petition_of(w)
        _activate(client, pet)
        with _quiet():
            V.transfer_vassal(w, SWISS, "Prussia")
        r = _respond(client, "accept", pet["dialogue_id"])
        assert r.get("success") is False and "withdrawn" in str(r.get("message"))
        verdict = _verdict(client, r)
        assert verdict["outcome"] == "WITHDRAWN" and verdict["proposal_type"] == "Client's Petition"
        assert M._derive_proposal_result_outcome(verdict) == "WITHDRAWN"
        titles = _titles(w)
        assert "Client's Petition Withdrawn" in titles, titles
        assert "Client's Petition Rejected" not in titles
        assert not _logged(w)

    def test_the_payload_blanks_the_petitions_reason_and_carries_no_article(self):
        w = _europe()
        dlg = _deliver_only(w, SWISS)
        payload = dlg["popup_payload"]
        assert payload["proposal_type_display"] == "Client's Petition"
        assert payload["decision_reason"] == "" and payload["decision_reason_display"] == ""
        assert payload["diplomat_line"] == ""
        rebuilt = build_pending_envoy_popup_from_terms(
            w, nation=SWISS, terms=dlg["context"]["proposal"], decision_reason="client_petition")
        assert rebuilt["decision_reason"] == "" and rebuilt["is_petition"] is True
        # R2: the availability keys are derived at THIS build, from the lord's
        # DP as it stands (sweep IQ7R-R2m)
        assert rebuilt["grant_enabled"] is True and rebuilt["grant_reason"] == ""
        assert [o["action"] for o in rebuilt["options"]] == ["accept_ai_proposal", "reject_ai_proposal"]
        w.diplomatic_points = 0
        short = build_pending_envoy_popup_from_terms(
            w, nation=SWISS, terms=dlg["context"]["proposal"], decision_reason="client_petition")
        assert short["grant_enabled"] is False and "diplomatic point" in short["grant_reason"]
        assert next(o for o in short["options"] if o["action"] == "accept_ai_proposal")["enabled"] is False
        from backend.display_names import DECISION_REASON_DISPLAY
        for key in ("client_petition", "granted", "refused", "fulfilled", "withdrawn", "stands"):
            assert key in DECISION_REASON_DISPLAY, key

    def test_the_garrison_option_says_what_it_does_on_both_boards(self):
        w = _europe()
        assert V.garrison_option_copy(w, SWISS) == (
            "2 AP → Loyalty +10 now. No corps moves: a corps standing in Bern adds +2 every turn.")
        assert V.lord_garrison_present(w, PLAYER, "Milan")                    # Massena stands there at boot
        assert V.garrison_option_copy(w, KOI) == (
            "2 AP → Loyalty +10 now. No corps moves: our corps already standing in Milan adds +2 every turn.")
        assert V.garrison_result_line(w, KOI, 5, 15).endswith(
            "No corps moves — our corps already standing in Milan adds +2 a turn.")
        assert V.garrison_result_line(w, SWISS, 9, 19) == (
            "Switzerland shown the flag: loyalty 9 → 19 (2 AP spent). No corps moves — "
            "station one in Bern for +2 a turn.")
        assert V.garrison_refusal_line(w, KOI, 1) == (
            "Showing the flag in the Kingdom of Italy costs 2 AP — you have 1. No corps moves either way.")

    def _rebellion_dialogue(self, w, vassal):
        with _quiet():
            V.process_vassal_loyalty(w)
        dlg = next(d for d in _pending(w) if d.get("type") == "vassal_rebellion_imminent"
                   and (d.get("context") or {}).get("vassal_name") == vassal)
        w.dialogue_manager._current = dlg
        w.dialogue_manager._queue = [d for d in w.dialogue_manager._queue if d is not dlg]
        return dlg

    def test_the_garrison_handler_reports_the_flag_not_a_corps(self):
        w = _europe()
        w.vassals[SWISS]["loyalty"] = 9
        dlg = self._rebellion_dialogue(w, SWISS)
        assert dlg["options"][1]["description"] == V.garrison_option_copy(w, SWISS)
        w.actions_remaining = 4
        old = w.vassals[SWISS]["loyalty"]
        with _quiet():
            r = M.executor.handle_diplomatic_dialogue_response(
                "garrison_vassal_rebellion", {"world": w}, dialogue_id=dlg["dialogue_id"])
        assert r["success"] is True
        assert r["message"] == (f"The flag is shown in Switzerland: loyalty {old} → {old + 10} "
                                f"(2 AP spent). No corps moves — station one in Bern for a standing +2 a turn.")
        assert w.actions_remaining == 2 and w.vassals[SWISS]["loyalty"] == old + 10
        assert not V.lord_garrison_present(w, PLAYER, "Bern")
        # the Kingdom of Italy: our corps already stands in Milan
        w = _europe()
        w.vassals[KOI]["loyalty"] = 5
        dlg = self._rebellion_dialogue(w, KOI)
        w.actions_remaining = 4
        with _quiet():
            r = M.executor.handle_diplomatic_dialogue_response(
                "garrison_vassal_rebellion", {"world": w}, dialogue_id=dlg["dialogue_id"])
        assert r["message"].endswith("No corps moves — ours already stands in Milan, worth +2 a turn.")
        # the refusal speaks in the same voice
        w = _europe()
        w.vassals[SWISS]["loyalty"] = 9
        dlg = self._rebellion_dialogue(w, SWISS)
        w.actions_remaining = 1
        with _quiet():
            r = M.executor.handle_diplomatic_dialogue_response(
                "garrison_vassal_rebellion", {"world": w}, dialogue_id=dlg["dialogue_id"])
        assert r["success"] is False
        assert r["message"] == "Insufficient AP. Showing the flag in Switzerland costs 2 AP, you have 1."

    def test_the_wavering_card_key_follows_the_regiments_and_the_lever(self, monkeypatch):
        w = _europe()
        rows = build_diplomatic_ledger(w)["vassals"]["rows"]
        assert rows and all(r["wavering_regiments"] is False for r in rows)
        marshal = next(m for m in w.marshals.values() if m.nation == PLAYER)
        marshal.original_nation = SWISS
        assert _card(w, SWISS)["wavering_regiments"] is True
        assert _card(w, "Holland")["wavering_regiments"] is False
        monkeypatch.setattr(V, "THE_WAVERING_LINE_IS_HONEST", False)
        assert "wavering_regiments" not in _card(w, SWISS)

    def test_the_school_of_war_issues_no_petition_and_its_card_forecasts_none(self, monkeypatch):
        w0 = _europe()
        client = _swap(monkeypatch, w0)
        with _quiet():
            r = client.post("/new_game", json={"scenario": "tutorial"}).json()
        assert r.get("success") is True, r
        w = M.game_state["world"]
        assert getattr(w, "scenario_name", "") == "tutorial" and w.vassals
        assert V.petitions_live(w) is False
        assert V.petition_gate_verdict(w, PLAYER, SWISS) == (False, "dormant", 0)
        assert V.petition_standing_keys(w, SWISS) == {}
        seen = []
        while int(w.current_turn) < 13:
            try:
                _end_turn(client)
            except AssertionError:
                current = w.dialogue_manager.peek() or {}
                if current:
                    _respond(client, "reject", current.get("dialogue_id"))
                _end_turn(client)
            seen.extend(_petitions(w))
        assert not seen and not _logged(w)
        assert all("petitioned_turn" not in row for row in w.vassals.values())
        with _quiet():
            rows = build_diplomatic_ledger(w)["vassals"]["rows"]
        assert rows and not any(k in row for row in rows for k in ("standing", "next_petition_in", "bond"))
        # control: the main game's card carries all three
        assert all(k in _card(_europe(), SWISS) for k in ("standing", "next_petition_in", "bond"))


# ═══════════════════════════════════════════════════════════════════════════
# [37] IQ7-X5 — the dead petition popup is reaped on every road
# ═══════════════════════════════════════════════════════════════════════════

def _echo(response, dialogue_id):
    return (response.get("incoming_proposal") or {}).get("dialogue_id") == dialogue_id


class TestX5TheDeadPopupIsReaped:
    """The six cases of `scratchpad/iq10/x5/probe_x5_fix.py`, as pins."""

    def _cached(self, w, dlg):
        cache = w.incoming_proposal_popup
        return isinstance(cache, dict) and cache.get("dialogue_id") == dlg["dialogue_id"]

    def test_a_petition_current_at_delivery_activated_and_granted(self, monkeypatch):
        w = _europe()
        dlg = _deliver_only(w, SWISS)
        assert self._cached(w, dlg)
        client = _swap(monkeypatch, w)
        _activate(client, dlg)
        r = _respond(client, "accept", dlg["dialogue_id"])
        assert r.get("success") is True and not _echo(r, dlg["dialogue_id"])
        assert r["proposal_result"]["outcome"] == "ACCEPT"
        assert not _echo(_cmd(client, "status"), dlg["dialogue_id"])
        assert w._popup_queue.get("incoming_proposal_popup") is None

    def test_an_ordinary_letter_activated_and_rejected(self, monkeypatch):
        w = _europe()
        _clear_slot(w)
        dlg = _deliver(w, _ordinary("Prussia", "non_aggression"))
        assert self._cached(w, dlg)
        client = _swap(monkeypatch, w)
        _activate(client, dlg)
        r = _respond(client, "reject", dlg["dialogue_id"])
        assert r.get("success") is True and not _echo(r, dlg["dialogue_id"])
        assert not _echo(_cmd(client, "status"), dlg["dialogue_id"])

    def test_control_a_status_that_drains_the_cache_first(self, monkeypatch):
        w = _europe()
        dlg = _deliver_only(w, SWISS)
        client = _swap(monkeypatch, w)
        first = _cmd(client, "status")
        assert _echo(first, dlg["dialogue_id"])                              # the LIVE modal, delivered once
        _activate(client, dlg)
        r = _respond(client, "accept", dlg["dialogue_id"])
        assert not _echo(r, dlg["dialogue_id"]) and r["proposal_result"]["outcome"] == "ACCEPT"

    def test_two_letters_the_queued_petition_activated_then_both_answered(self, monkeypatch):
        w = _europe()
        _clear_slot(w)
        a = _deliver(w, _ordinary("Prussia", "non_aggression"))
        b = _deliver(w, _make_proposal(w, SWISS))
        assert self._cached(w, a) and b in list(w.dialogue_manager.iter_queue())
        client = _swap(monkeypatch, w)
        r = _activate(client, b)
        assert _echo(r, b["dialogue_id"])
        r = _respond(client, "accept", b["dialogue_id"])
        assert r.get("success") is True and not _echo(r, b["dialogue_id"])
        r = _respond(client, "reject", a["dialogue_id"])
        assert r.get("success") is True and not _echo(r, a["dialogue_id"])
        r = _cmd(client, "status")
        assert not _echo(r, a["dialogue_id"]) and not _echo(r, b["dialogue_id"])
        assert w._popup_queue.get("incoming_proposal_popup") is None

    def test_the_pending_envoy_route_then_the_answer(self, monkeypatch):
        w = _europe()
        dlg = _deliver_only(w, SWISS)
        client = _swap(monkeypatch, w)
        pe = _pending_envoy(client)
        assert pe.get("has_pending") is True and _echo(pe, dlg["dialogue_id"])
        r = _respond(client, "accept", dlg["dialogue_id"])
        assert r.get("success") is True and not _echo(r, dlg["dialogue_id"])
        assert r["proposal_result"]["outcome"] == "ACCEPT"

    @pytest.mark.parametrize("phrase,outcome,reload", [
        ("accept", "ACCEPT", False), ("reject", "REJECT", False),
        ("grant the petition", "ACCEPT", False), ("refuse the petition", "REJECT", True),
    ])
    def test_a_typed_answer_as_the_first_command_after_delivery(self, monkeypatch, phrase, outcome, reload):
        w = _europe()
        dlg = _deliver_only(w, SWISS)
        if reload:                                                            # the /load road
            with _quiet():
                w = WorldState.from_dict(copy.deepcopy(w.to_dict()))
            dlg = w.dialogue_manager.peek()
        assert self._cached(w, dlg)
        client = _swap(monkeypatch, w)
        r = _cmd(client, phrase)
        assert r.get("success") is True, r.get("message")
        assert not _echo(r, dlg["dialogue_id"])
        assert r["proposal_result"]["outcome"] == outcome                     # the real result, same response
        assert not _petitions(w) and w.incoming_proposal_popup is None
        assert w._popup_queue.get("incoming_proposal_popup") is None

    def test_a_restored_settlement_popup_bound_to_a_live_dialogue_is_not_reaped(self, turn6_snapshot, monkeypatch):
        w, client = _restore(monkeypatch, turn6_snapshot)
        current = w.dialogue_manager.peek()
        assert current["type"] == "incoming_settlement_offer"
        assert w.incoming_settlement_offer_popup["dialogue_id"] == current["dialogue_id"]
        # one popup a response: the deferred marshal petition rides first,
        # the settlement offer's popup the next — delivered, never reaped
        delivered = []
        for _ in range(3):
            r = _cmd(client, "status")
            if isinstance(r.get("incoming_settlement_offer"), dict):
                delivered.append(r["incoming_settlement_offer"]["dialogue_id"])
        assert delivered == [current["dialogue_id"]]
        assert w.dialogue_manager.peek() is current

    def test_the_gate_reads_liveness_when_no_dialogue_is_pending(self):
        w = _europe()
        _clear_slot(w)
        assert M._popup_dialogue_is_current(w, {"dialogue_id": 12345}) is False
        assert M._popup_dialogue_is_dead(w, {"dialogue_id": 12345}) is True
        assert M._popup_dialogue_is_current(w, {"no_id": True}) is True
        dlg = _deliver(w, _make_proposal(w, SWISS))
        assert M._popup_dialogue_is_current(w, {"dialogue_id": dlg["dialogue_id"]}) is True


# ═══════════════════════════════════════════════════════════════════════════
# the client half — source pins (the NA-5 `is_ultimatum` idiom)
# ═══════════════════════════════════════════════════════════════════════════

class TestClientSourcePins:
    def test_the_grant_button_reads_the_backends_enabled(self):
        gd = (GODOT_SCRIPTS / "incoming_proposal_popup.gd").read_text(encoding="utf-8")
        assert 'data.get("grant_enabled", true)' in gd
        assert 'opt.get("enabled", grant_enabled)' in gd
        assert "accept_btn.disabled = is_petition and not grant_enabled" in gd
        # IQ-10 (Sept 19, 2026): the interpolation became a concatenation so a
        # reason that already ends in a full stop does not get a second one
        # (every reason the backend ships is a whole sentence). The pin
        # follows the line, and the punctuation rule is pinned beside it.
        assert '"]Grant unavailable: " + grant_reason' in gd
        assert 'grant_reason.ends_with(".")' in gd
        assert "counter_btn.visible = not is_counter and not is_ultimatum and not is_petition" in gd
        assert "accept_btn.disabled = false" not in gd.split("var grant_enabled := true")[1].split("func ")[0]

    def test_the_vassals_card_renders_the_petition_keys(self):
        gd = (GODOT_SCRIPTS / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        assert f'standing == "{V._GATE_COPY["eligible"]}"' in gd                # the literal it branches on
        assert 'v.has("standing")' in gd and 'v.has("next_petition_in")' in gd
        assert "may petition at the turn's end" in gd and "next petition in " in gd
        assert 'v.has("bond")' in gd and "Bond: " in gd
        assert 'v.get("remission_left", 0)' in gd and "Tribute remitted: " in gd
        assert 'v.get("wavering_regiments", true)' in gd
        assert "Wavering — no standing to petition" in gd

    def test_the_end_turn_gate_and_lapsed_envoys_read_the_priced_rows(self):
        main_gd = (GODOT_SCRIPTS / "main.gd").read_text(encoding="utf-8")
        assert 'diplo_data["pending_lapsing_petitions"] = response.get(' in main_gd
        assert 'diplo_data.get("pending_lapsing_petitions", [])' in main_gd
        assert 'pet.get("price_line", "")' in main_gd
        # F2 (row EP, LV-9): the count and the noun agree through Utils.plural.
        assert '"%s will be %s if you end the turn: %s." % [Utils.plural(named.size(), "petition"), verb, ", ".join(named)]' in main_gd
        assert '"REFUSED" if refused else "left unanswered"' in main_gd
        for name in ("main.gd", "dispatch_view.gd"):
            gd = (GODOT_SCRIPTS / name).read_text(encoding="utf-8")
            assert 'bool(lapse.get("is_petition", false)) and l_line != ""' in gd, name

    def test_the_rebellion_modal_shows_the_flag(self):
        tscn = (GODOT_SCENES / "vassal_rebellion_popup.tscn").read_text(encoding="utf-8")
        gd = (GODOT_SCRIPTS / "vassal_rebellion_popup.gd").read_text(encoding="utf-8")
        assert 'text = "Show the Flag"' in tscn and "Send Garrison" not in tscn
        assert "[b]Show the Flag[/b]" in gd and "costs %d AP" not in gd
        assert 'choice_made.emit("garrison", current_data)' in gd               # the choice id unchanged


# ═══════════════════════════════════════════════════════════════════════════
# PASS 2 — the verifiers' rulings (P2-1, P3-1..P3-4, P4-1..P4-6)
# ═══════════════════════════════════════════════════════════════════════════

ROUTING_LEVERS = ("A_PETITION_IS_ANSWERED_PLAINLY", "THE_MATTER_GUARD_READS_THE_TABLE")
ENVOYS_TAIL = "open Envoys and answer it there."
SWISS_WAITS = f"Switzerland's petition waits in Envoys — {ENVOYS_TAIL}"
PORTUGAL_HEAD = ("Sire — that answer would be delivered to Portugal, whose matter is "
                 "the one before you.")


@pytest.fixture(autouse=True)
def _restore_routing_levers(monkeypatch):
    for name in ROUTING_LEVERS:
        monkeypatch.setattr(DR, name, getattr(DR, name))
    yield


def _swiss(w):
    """(loyalty, remission_left, bond, DP) — everything an answer moves."""
    row = w.vassals.get(SWISS) or {}
    return (row.get("loyalty"), row.get("remission_left"), _rel(w, SWISS, PLAYER),
            w.diplomatic_points)


def _granted(before):
    loyalty, _remission, bond, dp = before
    return (loyalty + V.PETITION_RELIEF_LOYALTY, V.REMISSION_COLLECTIONS,
            bond + V.PETITION_RELATION_STEP, dp - V.PETITION_DP_COST)


def _refused(before):
    loyalty, remission, bond, dp = before
    return (loyalty - V.PETITION_REFUSAL_LOYALTY, remission,
            bond - V.PETITION_RELATION_STEP, dp)


def _petition_current(board):
    """The petition opened from Envoys — the real `/mailbox/activate`."""
    w, client = board
    pet = _petition_of(w)
    _activate(client, pet)
    assert w.dialogue_manager.peek() is pet
    return w, client, pet


def _portugal_on_top(board):
    """The settlement offer rejected through its own endpoint: the turn's
    first routine letter (Portugal's) is current, Denmark's and the petition
    wait behind it."""
    w, client = board
    offer = _pending(w)[0]
    assert offer["type"] == "incoming_settlement_offer"
    r = _respond(client, "reject_settlement_offer", offer["dialogue_id"])
    assert r.get("success") is True, r.get("message")
    top = w.dialogue_manager.peek()
    assert top is not None and top.get("target_nation") == "Portugal"
    assert _petition_of(w) in list(w.dialogue_manager.iter_queue())
    return w, client, top


def _prussian_ultimatum(w):
    """A REAL incoming ultimatum, through the producer's own delivery — it
    queues behind whatever is on the desk, as an arriving one does."""
    ult = _deliver(w, {
        "source": "Prussia", "recipient": PLAYER, "proposal_type": "ultimatum", "priority": 1,
        "terms": {"type": "ultimatum", "proposer_nation": "Prussia", "target_nation": PLAYER,
                  "demands": [{"type": "territory", "regions": ["Hanover"]}],
                  "sweeteners": [], "clauses": ["ultimatum"]},
        "talleyrand_assessment": "", "decision_reason": "agenda_pursuit", "turn_generated": 1})
    assert ult.get("type") == "incoming_ultimatum"
    assert ult in list(w.dialogue_manager.iter_queue())
    return ult


def _spain_reward_petition(w):
    """Slice H's OWN producer queues Spain's reward petition, on the trigger
    the board has just pulled (the settlement offer rejected)."""
    war_id = next(iter(w.war_instances))
    with _quiet():
        ally = SO._queue_ally_settlement_petition(
            w, petition_type=SO.ALLY_SETTLEMENT_PETITION_REWARD,
            trigger_action="reject_settlement_offer",
            context={"war_id": war_id, "ally_nation": "Spain", "claim_war_id": war_id,
                     "target_enemy": "Austria", "claim_region": "Tyrol",
                     "basis": "contribution", "basis_display": "its blood in the war",
                     "candidate_clause": {"type": "territory", "from": "Austria",
                                          "to": "Spain", "regions": ["Tyrol"]}})
    assert ally and ally["type"] == "ally_settlement_petition"
    assert [o["action"] for o in ally["options"]] == [
        SO.ALLY_SETTLEMENT_PETITION_GRANT_ACTION, SO.ALLY_SETTLEMENT_PETITION_DECLINE_ACTION]
    assert ally in list(w.dialogue_manager.iter_queue())
    return ally


def _koi_relief_queued(w):
    """A second petition, from the court that takes an article."""
    _set_rel(w, KOI, PLAYER, -60)
    koi = _deliver(w, _make_proposal(w, KOI))
    assert koi in list(w.dialogue_manager.iter_queue())
    return koi


# ═══════════════════════════════════════════════════════════════════════════
# P2-1 — a client petition is answered by a PLAIN line, and nothing else
# ═══════════════════════════════════════════════════════════════════════════

NEVER_ANSWERS = (
    # the verifiers' measured list: arm 1's label containment and arm 3's
    # every-label-word match claimed each of these (GRANTED at 1 DP / 1800g,
    # or REFUSED at −10 / −20)
    "grant the petition later", "grant the petition next turn",
    "grant the petition, but not now", "grant the petition if the treasury allows",
    "grant the petition tomorrow, not today", "consider the petition, grant it later",
    "should i grant the petition?", "what if i grant the petition",
    "maybe grant the petition", "i will grant the petition later",
    "refuse the petition later", "grant the petition? no",
    "refuse the petition? no, grant it",
    # Builder B2: the keyword arm leaked the same way, one rung down
    "accept the petition later", "yes, later", "accept it next turn",
    "could we grant the petition", "reject the petition tomorrow",
    "yes, but not the petition",
    # lines only the QUESTION rule stops (every word is an answer word or
    # filler), one only FA-N2's marker rule stops (two reject-words that
    # mean "accept"), and one only the ONE-answer rule stops (it names both)
    "accept it?", "do we grant it", "decline to reject it", "grant it or refuse it",
)


class TestP21APetitionIsAnsweredPlainly:
    @pytest.mark.parametrize("phrase", NEVER_ANSWERS)
    def test_a_deferred_conditional_or_interrogative_line_never_answers(self, board, phrase):
        w, client, pet = _petition_current(board)
        before = _swiss(w)
        _cmd(client, phrase)
        assert not _logged(w), phrase
        assert _swiss(w) == before
        assert w.dialogue_manager.peek() is pet and _petitions(w) == [pet]

    def test_berthiers_own_deferral_arm_answers_the_deferred_line(self, board):
        """The line falls to the ORDINARY road — no new refusal copy."""
        w, client, pet = _petition_current(board)
        r = _cmd(client, "grant the petition later")
        msg = str(r.get("message"))
        assert r.get("success") is False
        assert "For a later day, Sire" in msg and "I keep no drawer for tomorrow's orders" in msg

    @pytest.mark.parametrize("phrase,answer", [
        ("Grant the petition, Sire", _granted), ("accept the petition", _granted),
        ("accept switzerland's petition", _granted), ("grant the swiss petition", _granted),
        ("accept the petition from switzerland", _granted),
        ("grant the petition at once", _granted), ("yes, grant it", _granted),
        ("grant their petition", _granted), ("accept the petition for relief", _granted),
        ("yes", _granted), ("1", _granted),
        ("decline the petition", _refused), ("reject it", _refused), ("2", _refused),
    ])
    def test_a_plain_answer_still_answers_at_the_quoted_price(self, board, phrase, answer):
        w, client, pet = _petition_current(board)
        before = _swiss(w)
        r = _cmd(client, phrase)
        assert r.get("success") is True, r.get("message")
        assert _swiss(w) == answer(before)
        outcome = "granted" if answer is _granted else "refused"
        assert [e["outcome"] for e in _logged(w)] == [outcome] and not _petitions(w)

    @pytest.mark.parametrize("choice", ["grant the petition later", "refuse the petition later",
                                        "should i grant the petition?"])
    def test_the_button_routes_free_text_obeys_the_same_rule(self, board, choice):
        """The THIRD copy of the label scan: `POST /respond_to_diplomatic_
        dialogue` takes free text."""
        w, client, pet = _petition_current(board)
        before = _swiss(w)
        r = _respond(client, choice, pet["dialogue_id"])
        msg = str(r.get("message"))
        assert r.get("success") is False
        assert msg.startswith("The petition takes a plain answer, Sire — nothing was relayed.")
        assert "1=Grant the petition, 2=Refuse the petition" in msg
        assert not _logged(w) and _swiss(w) == before and w.dialogue_manager.peek() is pet

    @pytest.mark.parametrize("choice,answer", [
        ("grant the petition", _granted), ("accept_ai_proposal", _granted),
        ("refuse", _refused), ("reject_ai_proposal", _refused),
    ])
    def test_the_button_route_still_takes_ids_and_plain_words(self, board, choice, answer):
        w, client, pet = _petition_current(board)
        before = _swiss(w)
        r = _respond(client, choice, pet["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        assert _swiss(w) == answer(before) and not _petitions(w)

    @pytest.mark.parametrize("route,phrase,answer", [
        ("typed", "grant the petition later", _granted),
        ("button", "refuse the petition later", _refused),
    ])
    def test_lever_down_the_pass_1_router_answers_the_deferred_line_at_price(
            self, board, monkeypatch, route, phrase, answer):
        monkeypatch.setattr(DR, "A_PETITION_IS_ANSWERED_PLAINLY", False)
        w, client, pet = _petition_current(board)
        before = _swiss(w)
        r = (_cmd(client, phrase) if route == "typed"
             else _respond(client, phrase, pet["dialogue_id"]))
        assert r.get("success") is True, r.get("message")
        assert _swiss(w) == answer(before) and len(_logged(w)) == 1

    @pytest.mark.parametrize("phrase,answer", [("grant it", _granted), ("refuse", _refused)])
    def test_lever_down_the_petitions_own_words_still_answer_on_the_pass_1_road(
            self, board, monkeypatch, phrase, answer):
        """SWEEP 2: pass 2 made arm 3b the LEVER-DOWN road — with the lever up
        a client petition never reaches it, so nothing pinned it any more.
        These two lines are the ones ONLY arm 3b answers on the pass-1 router
        (no label contains them; `refuse` is a keyword of the ultimatum alone,
        `grant` of nothing), so "False = the pass-1 router, byte for byte"
        is falsifiable for the petition's own words too."""
        monkeypatch.setattr(DR, "A_PETITION_IS_ANSWERED_PLAINLY", False)
        w, client, pet = _petition_current(board)
        before = _swiss(w)
        r = _cmd(client, phrase)
        assert r.get("success") is True, r.get("message")
        assert _swiss(w) == answer(before)
        outcome = "granted" if answer is _granted else "refused"
        assert [e["outcome"] for e in _logged(w)] == [outcome] and not _petitions(w)

    def test_lever_down_the_button_route_keeps_its_own_pass_1_scan(self, board, monkeypatch):
        """SWEEP 2: the third copy reads the lever ITSELF. Delegating to
        `match_dialogue_answer` (which reads it too) is not enough, because on
        the pass-1 router the two routes DISAGREE: the typed router declines a
        line that carries an order (None — it falls to the ordinary road),
        while the button route's own containment arm answers it. Lever down
        restores THAT, byte for byte — never a refusal pass 1 did not give."""
        monkeypatch.setattr(DR, "A_PETITION_IS_ANSWERED_PLAINLY", False)
        w, client, pet = _petition_current(board)
        line = "grant the petition and attack vienna"
        assert DR.match_dialogue_answer(pet, line) is None              # the typed router declines it
        before = _swiss(w)
        r = _respond(client, line, pet["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        assert _swiss(w) == _granted(before)
        assert [e["outcome"] for e in _logged(w)] == ["granted"] and not _petitions(w)

    def test_the_plain_answer_is_the_client_petitions_whole_router(self, board):
        w, _client = board
        pet = _petition_of(w)
        assert DR.petition_plain_answer(pet, "grant the petition") == "accept_ai_proposal"
        assert DR.match_dialogue_answer(pet, "grant the petition") == "accept_ai_proposal"
        assert DR.match_dialogue_answer(pet, "refuse the petition") == "reject_ai_proposal"
        assert DR.match_dialogue_answer(pet, "grant the petition later") is None
        # a line that names BOTH answers claims neither
        assert DR.match_dialogue_answer(pet, "accept or reject it") is None
        assert DR.match_dialogue_answer(pet, "accept, no, reject it") is None
        # a machine token, spelled out, is never a sentence — and only whole
        assert DR.match_dialogue_answer(pet, "accept_ai_proposal") == "accept_ai_proposal"
        assert DR.match_dialogue_answer(pet, "reject_ai_proposal") == "reject_ai_proposal"
        assert DR.match_dialogue_answer(pet, "accept_ai_proposal later") is None
        # the ruling's scope: Slice H's ally petition keeps the pass-1 label
        # arms (a stated limit on the FA-N2 row, not widened in this pass)
        ally = {"type": "ally_settlement_petition", "target_nation": "Spain", "context": {},
                "options": [{"label": "Grant the Claim", "action": SO.ALLY_SETTLEMENT_PETITION_GRANT_ACTION},
                            {"label": "Decline", "action": SO.ALLY_SETTLEMENT_PETITION_DECLINE_ACTION}]}
        assert DR.match_dialogue_answer(ally, "decline the petition later") == "decline"

    @pytest.mark.parametrize("phrase", ["grant them tyrol", "grant tyrol to the kingdom of italy",
                                        "grant the kingdom of italy's petition"])
    def test_the_petitions_own_subject_is_part_of_a_plain_answer(self, monkeypatch, phrase):
        """The client's name forms and the petitioned province name the
        matter on the table — read off the dialogue, on the court whose name
        is three words and an article."""
        w, client, pet = _tyrol_board(monkeypatch)
        assert w.dialogue_manager.peek() is pet
        dp0, rel0 = w.diplomatic_points, _rel(w, KOI, PLAYER)
        r = _cmd(client, phrase)
        assert r.get("success") is True, r.get("message")
        assert [e["outcome"] for e in _logged(w)] == ["granted"] and not _petitions(w)
        assert w.regions["Tyrol"].controller == KOI
        assert w.diplomatic_points == dp0 - V.PETITION_DP_COST          # one deed, one charge
        assert _rel(w, KOI, PLAYER) == rel0 + V.PETITION_RELATION_STEP

    def test_a_deferral_beside_the_subject_still_claims_nothing(self, monkeypatch):
        w, client, pet = _tyrol_board(monkeypatch)
        dp0 = w.diplomatic_points
        _cmd(client, "grant them tyrol later")
        assert not _logged(w) and w.regions["Tyrol"].controller == PLAYER
        assert w.diplomatic_points == dp0 and w.dialogue_manager.peek() is pet

    def test_a_compound_line_leaves_the_petition_on_the_desk_and_runs_its_order(self, board):
        """Recorded trade (Builder B2): before, the petition was granted and
        the order dropped; now the order half executes as the order it is."""
        w, client, pet = _petition_current(board)
        r = _cmd(client, "grant the petition, and invest in holland")
        assert not _logged(w) and w.dialogue_manager.peek() is pet
        assert "remission_left" not in w.vassals[SWISS]
        assert r.get("success") is True and str(r.get("message")).startswith("Invested in Holland")


# ═══════════════════════════════════════════════════════════════════════════
# P3-1 — contiguity is not the lord's doing
# ═══════════════════════════════════════════════════════════════════════════

CONTIGUITY_VOID = ("Tyrol no longer adjoins the Kingdom of Italy's territory and cannot be "
                   "ceded to it")


def _milan_falls(w):
    """The CLIENT loses the one province that adjoined Tyrol — Austria takes
    Milan; Tyrol stays French."""
    assert set(w.get_nation_regions(KOI)) & set(w.regions["Tyrol"].adjacent_regions) == {"Milan"}
    w.regions["Milan"].controller = "Austria"
    w.invalidate_active_nations_cache()


def _koi(w):
    return (w.vassals[KOI]["loyalty"], _rel(w, KOI, PLAYER), w.diplomatic_points)


class TestP31ContiguityIsNotTheLordsDoing:
    def test_the_read_and_the_grant_press_withdraw_it_free(self, monkeypatch):
        w, client, pet = _tyrol_board(monkeypatch)
        ip = _pending_envoy(client)["incoming_proposal"]
        assert ip["grant_enabled"] is True and ip["grant_reason"] == ""
        _milan_falls(w)
        line = f"{CONTIGUITY_VOID} — the petition is withdrawn."
        ip = _pending_envoy(client)["incoming_proposal"]
        assert ip["grant_enabled"] is True and ip["grant_reason"] == line    # the press retires it
        assert ip["clauses"][0] == line
        prose = json.dumps([ip["grant_reason"], ip["clauses"], ip["options"],
                            ip.get("talleyrand_assessment")], ensure_ascii=False)
        assert KOI not in prose                                              # R7: never the raw tag
        before = _koi(w)
        r = _respond(client, "accept_ai_proposal", pet["dialogue_id"])
        assert r.get("success") is False and r.get("message") == line
        assert _verdict(client, r)["outcome"] == "WITHDRAWN"
        assert _koi(w) == before and not _petitions(w) and not _logged(w)
        assert w.regions["Tyrol"].controller == PLAYER

    def test_the_refuse_press_is_free_too(self, monkeypatch):
        w, client, pet = _tyrol_board(monkeypatch)
        _milan_falls(w)
        before = _koi(w)
        r = _respond(client, "reject_ai_proposal", pet["dialogue_id"])
        assert r.get("message") == (f"{CONTIGUITY_VOID} — the petition is withdrawn and "
                                    f"nothing is charged.")
        assert _verdict(client, r)["outcome"] == "WITHDRAWN"
        assert _koi(w) == before and not _petitions(w) and not _logged(w)

    def test_the_real_end_turn_lapse_is_free_and_forecast_as_free(self, monkeypatch):
        w, client, pet = _tyrol_board(monkeypatch)
        _milan_falls(w)
        loy0, rel0, _dp = _koi(w)
        lp = _cmd(client, "status")["pending_lapsing_petitions"]
        assert len(lp) == 1 and lp[0]["refused"] is False
        assert lp[0]["price_line"] == (f"{CONTIGUITY_VOID} — a lapse withdraws the petition; "
                                       f"nothing is charged.")
        r = _end_turn(client)
        assert not _logged(w) and not _petitions(w)
        assert _rel(w, KOI, PLAYER) == rel0
        assert w.vassals[KOI]["loyalty"] > loy0 - V.PETITION_REFUSAL_LOYALTY
        receipt = [e for e in r.get("events", []) if e.get("type") == "client_petition_answered"]
        assert [(e["outcome"], e["penalty"]) for e in receipt] == [("withdrawn", False)]
        lapsed = [e for e in w.event_log if e.get("type") == "offer_lapsed"
                  and KOI in json.dumps(e, default=str)]
        assert [CL.format_event_oneliner(e) for e in lapsed] == [
            "The Kingdom of Italy's petition lapsed unanswered — moot, nothing charged"]

    @pytest.mark.parametrize("cause,also_breaks,kind", [
        ("estate", False, "stands"), ("estate", True, "stands"),      # the lord's doing is read first
        ("cooldown", False, "stands"), ("cooldown", True, "withdrawn"),
        (None, True, "withdrawn"),
    ])
    def test_grant_forecast_and_lapse_agree_on_every_arm(self, cause, also_breaks, kind):
        w = _europe()
        _stage_tyrol_for_koi(w)
        pet = V.petition_terms(w, KOI)
        assert pet["region"] == "Tyrol"
        if cause == "estate":
            w.marshals["Ney"].dotation_regions = ["Tyrol"]
        elif cause == "cooldown":
            w.vassals[KOI]["grant_cooldown"] = 2
        if also_breaks:
            _milan_falls(w)
        verdict, message = V.petition_grant_verdict(w, PLAYER, KOI, pet)
        assert verdict == kind, message
        assert KOI not in message
        forecast = V.lapse_forecast(w, KOI, PLAYER, pet)
        loy0, rel0 = w.vassals[KOI]["loyalty"], _rel(w, KOI, PLAYER)
        res = V.refuse_petition(w, KOI, PLAYER, pet, how="unanswered")
        if kind == "withdrawn":
            assert V.reprice_petition(w, PLAYER, KOI, pet) is None
            assert (forecast["outcome"], forecast["penalised"]) == ("withdrawn", False)
            assert res["outcome"] == "withdrawn" and res["success"] is False
            assert (w.vassals[KOI]["loyalty"], _rel(w, KOI, PLAYER)) == (loy0, rel0)
            assert not _logged(w)
        else:
            assert V.petition_grant_availability(w, PLAYER, KOI, pet) == (False, message)
            assert (forecast["outcome"], forecast["penalised"]) == ("refused", True)
            assert res["outcome"] == "unanswered" and res["penalty"] is True
            assert (w.vassals[KOI]["loyalty"], _rel(w, KOI, PLAYER)) == (loy0 - 10, rel0 - 20)

    def test_lever_down_the_7d10e20c_arms_return(self, monkeypatch):
        """Grant withdrew every ungrantable province; the lapse charged it."""
        monkeypatch.setattr(V, "THE_DEED_HONOURS_THE_PETITION", False)
        w, client, pet = _tyrol_board(monkeypatch)
        _milan_falls(w)
        petition = pet["context"]["proposal"]["petition"]
        assert V.petition_grant_verdict(w, PLAYER, KOI, petition) == (
            "withdrawn", "Tyrol can no longer be ceded to the Kingdom of Italy — "
                         "the petition is withdrawn.")
        forecast = V.lapse_forecast(w, KOI, PLAYER, petition)
        assert (forecast["outcome"], forecast["penalised"]) == ("refused", True)
        rel0 = _rel(w, KOI, PLAYER)
        _end_turn(client)
        assert [(e["outcome"], e["penalty"]) for e in _logged(w)] == [("unanswered", True)]
        assert _rel(w, KOI, PLAYER) == rel0 - V.PETITION_RELATION_STEP

    def test_the_classified_read_and_the_executors_read_are_one_rule_set(self, monkeypatch):
        assert V._GRANT_REFUSAL_LORDS_DOING == frozenset({"estate"})
        w, client, pet = _tyrol_board(monkeypatch)
        known = {"", "unknown", "not_held", "homeland", "capital", "estate", "contiguity"}
        seen = set()
        for vassal in ("Holland", KOI, SWISS):
            for region in list(w.regions) + ["Atlantis"]:
                key, reason = V._grant_region_refusal(w, vassal, region, PLAYER)
                assert reason == V._grant_region_eligibility(w, vassal, region, PLAYER)
                assert bool(key) == bool(reason) and key in known
                assert KOI not in reason
                seen.add(key)
        assert {"", "not_held", "homeland", "contiguity", "unknown"} <= seen
        _milan_falls(w)
        assert V._grant_region_refusal(w, KOI, "Tyrol", PLAYER) == (
            "contiguity", "Tyrol does not adjoin the Kingdom of Italy's territory.")
        # …and VS-3's own typed verb prints the same sentence, never the tag
        r = _cmd(client, "cede Tyrol to the Kingdom of Italy")
        assert r.get("success") is False
        assert r.get("message") == ("Cannot cede Tyrol: Tyrol does not adjoin the Kingdom of "
                                    "Italy's territory.")
        assert _petitions(w) == [pet] and not _logged(w)


# ═══════════════════════════════════════════════════════════════════════════
# P3-2 — the re-pricer's text writer keeps the article
# ═══════════════════════════════════════════════════════════════════════════

KOI_HEAD = ("Sire, Marescalchi brings a petition from the Kingdom of Italy. "
            "The Kingdom of Italy petitions the Emperor for a province.")


class TestP32TheRepricerKeepsTheArticle:
    def _issue(self, *, diplomat=True):
        """The REAL producer at turn 6, the delivered text captured BEFORE
        any read seam has run."""
        w = _europe()
        _stage_tyrol_for_koi(w)
        _park(w, KOI)
        w.current_turn = 6
        w.vassals[KOI]["created_turn"] = 1
        w.vassals[KOI]["loyalty"] = 86
        if not diplomat:
            w.diplomats.pop(KOI, None)
        with _quiet():
            V.process_vassal_petitions(w)
        pet = _petitions(w)[0]
        return w, pet, str(pet["talleyrand_text"])

    def test_every_read_seam_rewrites_the_delivered_text_byte_for_byte(self, monkeypatch):
        w, pet, delivered = self._issue()
        assert delivered.split("\n\n", 1)[0] == KOI_HEAD
        client = _swap(monkeypatch, w)
        reads = (lambda: _cmd(client, "status"), lambda: _pending_envoy(client),
                 lambda: _activate(client, pet))
        for read in reads:
            pet["talleyrand_text"] = "STALE\n\nSTALE"       # the seam must WRITE, not merely agree
            read()
            assert pet["talleyrand_text"].split("\n\n", 1)[0] == KOI_HEAD
            assert pet["talleyrand_text"] == delivered

    def test_a_changed_price_rewrites_the_body_and_keeps_the_head(self):
        w, pet, delivered = self._issue()
        w.vassals[KOI]["loyalty"] = 99                       # the gain clamps: the body moves
        refresh_client_petition_dialogue(w, pet)
        assert pet["talleyrand_text"] != delivered
        assert pet["talleyrand_text"].split("\n\n", 1)[0] == KOI_HEAD

    def test_the_envoy_fallback_carries_the_article_too(self):
        w, pet, delivered = self._issue(diplomat=False)
        head = ("Sire, the envoy of the Kingdom of Italy brings a petition from the Kingdom "
                "of Italy. The Kingdom of Italy petitions the Emperor for a province.")
        assert delivered.split("\n\n", 1)[0] == head
        pet["talleyrand_text"] = "STALE\n\nSTALE"
        refresh_client_petition_dialogue(w, pet)
        assert pet["talleyrand_text"] == delivered

    def test_switzerland_takes_no_article_so_only_the_kingdom_can_see_it(self, board):
        w, _client = board
        pet = _petition_of(w)
        refresh_client_petition_dialogue(w, pet)
        head = pet["talleyrand_text"].split("\n\n", 1)[0]
        assert "a petition from Switzerland. Switzerland petitions the Emperor" in head
        assert V._court_name(w, SWISS, article=True) == V._court_name(w, SWISS)


# ═══════════════════════════════════════════════════════════════════════════
# P3-3 — an ORDER that carries a family noun is never eaten by the guard
# ═══════════════════════════════════════════════════════════════════════════

ULTIMATUM_ORDERS = ("send ultimatum to Austria", "issue ultimatum to Austria",
                    "deliver an ultimatum to Austria: cede Tyrol")


class TestP33TheRouterSeamRefusesAnswersOnly:
    def _staged(self, board):
        w, client, top = _portugal_on_top(board)
        ult = _prussian_ultimatum(w)
        assert w.dialogue_manager.peek() is top
        return w, client, top, ult

    @pytest.mark.parametrize("order", ULTIMATUM_ORDERS)
    def test_the_players_own_ultimatum_order_reaches_the_executor(self, board, order):
        w, client, top, ult = self._staged(board)
        r = _cmd(client, order)
        msg = str(r.get("message"))
        assert not r.get("matter_mismatch") and "waits in Envoys" not in msg
        assert "already at war with Austria" in msg                   # the ultimatum route's own word
        assert w.dialogue_manager.peek() is top and ult in list(w.dialogue_manager.iter_queue())

    @pytest.mark.parametrize("phrase,family,waits", [
        ("yield to the ultimatum", "ultimatum", "Prussia's ultimatum waits in Envoys"),
        ("accept the ultimatum", "ultimatum", "Prussia's ultimatum waits in Envoys"),
        ("defy the ultimatum", "ultimatum", "Prussia's ultimatum waits in Envoys"),
        ("do not accept the petition", "petition", "Switzerland's petition waits in Envoys"),
        ("no, refuse the petition", "petition", "Switzerland's petition waits in Envoys"),
        ("grant switzerland's petition", "petition", "Switzerland's petition waits in Envoys"),
        # SWEEP 2: a negation MARKER made of an answer verb (`refuse to …` — FA-N2's
        # own phrase, blanked as a span, so ONE verb survives) and a possessive that
        # names no court (it qualifies the noun; the court strip cannot see it). Each
        # is the only line that binds its filter in `_line_is_answer_shaped`.
        ("refuse to accept the petition", "petition", "Switzerland's petition waits in Envoys"),
        ("grant the envoy's petition", "petition", "Switzerland's petition waits in Envoys"),
    ])
    def test_an_answer_shaped_line_stays_refused_as_waiting(self, board, phrase, family, waits):
        w, client, top, ult = self._staged(board)
        states0 = dict(w.diplomatic_states)
        r = _cmd(client, phrase)
        assert r.get("success") is False and r.get("matter_mismatch") is True
        assert r.get("matter_family") == family
        assert r.get("message") == f"{PORTUGAL_HEAD} {waits} — {ENVOYS_TAIL}"
        assert w.dialogue_manager.peek() is top and dict(w.diplomatic_states) == states0
        assert ult in list(w.dialogue_manager.iter_queue()) and not _logged(w)

    def test_an_order_naming_the_petition_is_an_order(self, board):
        w, client, top, _ult = self._staged(board)
        r = _cmd(client, "Ney, ignore the petition and march to Swabia")
        assert not r.get("matter_mismatch") and r.get("success") is True
        assert w.marshals["Ney"].location == "Swabia"
        r = _cmd(client, "petition the senate for more men")
        assert not r.get("matter_mismatch") and "waits in Envoys" not in str(r.get("message"))
        assert w.dialogue_manager.peek() is top

    def test_the_handler_seam_keeps_the_broad_noun_rule(self, board):
        w, _client, top, _ult = self._staged(board)
        broad = matter_mismatch_refusal(w, top, "send ultimatum to Austria")
        assert broad and broad["matter_family"] == "ultimatum"
        assert matter_mismatch_refusal(w, top, "send ultimatum to Austria", answers_only=True) is None
        refused = matter_mismatch_refusal(w, top, "accept the ultimatum", answers_only=True)
        assert refused and refused["matter_family"] == "ultimatum"

    def test_the_answer_shape_reads_the_whole_line(self, board):
        w, _client = board
        for line in ("accept the ultimatum", "yield to the ultimatum", "do not accept the petition",
                     "no, refuse the petition", "grant switzerland's petition",
                     "grant their petition", "the petition's terms are agreed", "grant it",
                     "refuse", "refuse to accept the petition", "grant the envoy's petition"):
            assert DR._line_is_answer_shaped(line, w) is True, line
        for line in ULTIMATUM_ORDERS + ("ney, ignore the petition and march to swabia",
                                        "petition the senate for more men"):
            assert DR._line_is_answer_shaped(line.lower(), w) is False, line

    def test_lever_down_the_noun_alone_eats_the_order(self, board, monkeypatch):
        monkeypatch.setattr(DR, "THE_MATTER_GUARD_READS_THE_TABLE", False)
        w, client, top, _ult = self._staged(board)
        r = _cmd(client, "send ultimatum to Austria")
        assert r.get("matter_mismatch") is True and r.get("matter_family") == "ultimatum"
        assert "Prussia's ultimatum waits in Envoys" in str(r.get("message"))


# ═══════════════════════════════════════════════════════════════════════════
# P3-4 — a bare `refuse` is the ULTIMATUM's word when the ultimatum is current
# ═══════════════════════════════════════════════════════════════════════════

class TestP34ABareRefuseDefiesTheUltimatumOnTheTable:
    def _staged(self, board):
        """The ultimatum arrives behind Portugal's letter and is OPENED FROM
        ENVOYS — the petition stays queued behind it."""
        w, client, _top = _portugal_on_top(board)
        ult = _prussian_ultimatum(w)
        _activate(client, ult)
        assert w.dialogue_manager.peek() is ult
        assert _petition_of(w) in list(w.dialogue_manager.iter_queue())
        assert not w.ultimatum_rejection_pressure
        return w, client, ult

    @pytest.mark.parametrize("phrase", ["refuse", "refuse it", "refuse them", "defy",
                                        "refuse the ultimatum"])
    def test_the_bare_verb_defies_the_ultimatum_while_a_petition_waits(self, board, phrase):
        w, client, ult = self._staged(board)
        before = _swiss(w)
        r = _cmd(client, phrase)
        assert r.get("success") is True and not r.get("matter_mismatch"), r.get("message")
        assert "defied Prussia's ultimatum" in str(r.get("message"))
        assert ult not in _pending(w) and w.ultimatum_rejection_pressure.get("Prussia", 0) > 0
        assert _swiss(w) == before and not _logged(w) and len(_petitions(w)) == 1

    @pytest.mark.parametrize("phrase", ["grant it", "grant the petition", "refuse the petition"])
    def test_the_petitions_own_words_are_still_pointed_at_envoys(self, board, phrase):
        w, client, ult = self._staged(board)
        r = _cmd(client, phrase)
        assert r.get("success") is False and r.get("matter_mismatch") is True
        assert r.get("message") == (
            "Sire — that answer would be delivered to Prussia, whose matter is the one "
            f"before you. {SWISS_WAITS}")
        assert w.dialogue_manager.peek() is ult and not w.ultimatum_rejection_pressure
        assert not _logged(w)

    def test_the_verb_is_claimed_only_by_a_dialogue_that_offers_it(self, board):
        w, _client, ult = self._staged(board)
        assert DR._active_dialogue_claims_the_verb(ult, "refuse") is True
        assert DR._active_dialogue_claims_the_verb(ult, "refuse them") is True
        assert DR._active_dialogue_claims_the_verb(ult, "grant it") is False
        letter = {"type": "incoming_proposal", "target_nation": "Portugal", "context": {},
                  "options": [{"label": "Accept", "action": "accept_ai_proposal"},
                              {"label": "Reject", "action": "reject_ai_proposal"}]}
        assert DR._active_dialogue_claims_the_verb(letter, "refuse") is False

    def test_lever_down_the_bare_refuse_is_refused(self, board, monkeypatch):
        monkeypatch.setattr(DR, "THE_MATTER_GUARD_READS_THE_TABLE", False)
        w, client, ult = self._staged(board)
        r = _cmd(client, "refuse")
        assert r.get("matter_mismatch") is True and SWISS_WAITS in str(r.get("message"))
        assert w.dialogue_manager.peek() is ult and not w.ultimatum_rejection_pressure


# ═══════════════════════════════════════════════════════════════════════════
# P4-1 — a moot petition says so first, whatever the last read stored
# ═══════════════════════════════════════════════════════════════════════════

RELEASED = "Switzerland is no longer a vassal — the petition is withdrawn."


class TestP41TheMootPetitionSaysSoFirst:
    def _read(self, client):
        ip = _pending_envoy(client)["incoming_proposal"]
        return (ip["grant_enabled"], ip["grant_reason"], list(ip["clauses"]),
                [(o["label"], o["enabled"], o["reason"]) for o in ip["options"]])

    def test_the_players_own_release_with_the_petition_on_the_desk(self, board):
        w, client, pet = _petition_current(board)
        enabled, reason, clauses, _options = self._read(client)
        assert (enabled, reason) == (True, "") and "(1800g forgone)" in clauses[0]
        stored = pet["context"]["proposal"]["petition"]["availability"]
        assert stored == {"enabled": True, "reason": ""}             # the LAST read's — the trap
        head = pet["talleyrand_text"].split("\n\n", 1)[0]
        r = _cmd(client, "release switzerland")
        assert r.get("success") is True and SWISS not in w.vassals
        assert w.dialogue_manager.peek() is pet                        # typed-command safety
        enabled, reason, clauses, options = self._read(client)
        assert (enabled, reason) == (True, RELEASED)                   # the press retires it
        assert clauses[0] == RELEASED and clauses.count(RELEASED) == 1
        assert not any("forgone" in c for c in clauses)                # the stale grant quote is gone
        assert options[0] == ("Grant the petition", True, RELEASED)
        assert options[1] == ("Refuse the petition", True, "")
        grant = next(o for o in pet["options"] if o["action"] == "accept_ai_proposal")
        assert grant["description"] == RELEASED and grant["reason"] == RELEASED
        text = pet["talleyrand_text"]
        assert text.split("\n\n", 1)[0] == head
        assert f"\n\n  {RELEASED}\n" in text and "forgone" not in text
        lp = _cmd(client, "status")["pending_lapsing_petitions"]
        assert lp[0]["refused"] is False and "moot" in lp[0]["price_line"]
        dp0 = w.diplomatic_points
        r = _respond(client, "accept_ai_proposal", pet["dialogue_id"])
        assert r.get("success") is False and r.get("message") == RELEASED
        assert _verdict(client, r)["outcome"] == "WITHDRAWN"
        assert w.diplomatic_points == dp0 and not _logged(w) and not _petitions(w)

    def test_a_prior_read_and_no_prior_read_say_the_same_thing(self, board):
        """The control the verifier measured: with no earlier read the honest
        reason was always there — the two roads must agree."""
        w, client = board
        pet = _petition_of(w)
        assert "availability" not in pet["context"]["proposal"]["petition"]
        r = _cmd(client, "release switzerland")
        assert r.get("success") is True
        _activate(client, pet)
        enabled, reason, clauses, options = self._read(client)
        assert (enabled, reason) == (True, RELEASED)
        assert clauses[0] == RELEASED and not any("forgone" in c for c in clauses)
        assert options[0] == ("Grant the petition", True, RELEASED)

    def test_a_fresh_read_still_carries_the_repricers_own_verdict(self, board):
        """The override survives where it belongs: the SAME read produced
        both (R2's DP-short `stands`)."""
        w, client, pet = _petition_current(board)
        self._read(client)
        w.diplomatic_points = 0
        enabled, reason, clauses, _options = self._read(client)
        assert enabled is False and "cannot spare the diplomatic point" in reason
        assert "(1800g forgone)" in _grant_clause(clauses)             # a standing petition keeps its quote
        assert pet["context"]["proposal"]["petition"]["availability"] == {
            "enabled": False, "reason": reason}


# ═══════════════════════════════════════════════════════════════════════════
# P4-2 — the Vassals card while the ask is on the desk
# ═══════════════════════════════════════════════════════════════════════════

def _ledger_card(client, name):
    with _quiet():
        ledger = client.get("/diplomatic_ledger").json()["ledger"]
    return next(x for x in ledger["vassals"]["rows"] if x["name"] == name)


class TestP42TheCardSeesThePetitionOnTheDesk:
    def test_queued_then_current_then_answered_over_the_ledger_endpoint(self, board):
        w, client = board
        pet = _petition_of(w)
        assert pet in list(w.dialogue_manager.iter_queue())            # QUEUED, never a modal
        card = _ledger_card(client, SWISS)
        assert (card["standing"], card["standing_key"]) == ("petition on the desk", "pending")
        count = card["next_petition_in"]
        assert count == V.PETITION_INTERVAL_TURNS                       # the gate's own count: the NEXT ask
        for other in ("Holland", KOI):                                  # only the client that asked
            assert _ledger_card(client, other)["standing_key"] != "pending"
        _activate(client, pet)                                          # CURRENT
        card = _ledger_card(client, SWISS)
        assert (card["standing"], card["standing_key"]) == ("petition on the desk", "pending")
        r = _respond(client, "reject_ai_proposal", pet["dialogue_id"])
        assert r.get("success") is True
        card = _ledger_card(client, SWISS)
        assert card["standing_key"] == "cadence" and card["next_petition_in"] == count
        assert card["standing"] == f"{count} turns until it may ask"

    def test_the_desk_read_names_the_vassal_and_its_lord(self, board):
        w, _client = board
        assert V._GATE_COPY["pending"] == "petition on the desk"
        assert V.petition_on_the_desk(w, SWISS) is True
        assert V.petition_on_the_desk(w, SWISS, PLAYER) is True
        assert V.petition_on_the_desk(w, SWISS, "Prussia") is False
        assert V.petition_on_the_desk(w, KOI) is False
        with _quiet():
            reloaded = WorldState.from_dict(copy.deepcopy(w.to_dict()))
        assert V.petition_standing_keys(reloaded, SWISS)["standing_key"] == "pending"
        removed = w.dialogue_manager.remove_matching(V.is_client_petition)
        assert removed == 1 and V.petition_on_the_desk(w, SWISS) is False
        assert V.petition_standing_keys(w, SWISS)["standing_key"] == "cadence"


# ═══════════════════════════════════════════════════════════════════════════
# P4-3 — a line that names the LETTER is not the petition's
# ═══════════════════════════════════════════════════════════════════════════

LETTER_NOUN_LINES = ("refuse the offer", "refuse the proposal", "refuse the letter",
                     "refuse the terms")


class TestP43TheLetterNounsAreNotPetitionVocabulary:
    @pytest.mark.parametrize("phrase", LETTER_NOUN_LINES)
    def test_the_line_is_never_pointed_at_the_queued_petition(self, board, phrase):
        w, client, top = _portugal_on_top(board)
        r = _cmd(client, phrase)
        msg = str(r.get("message"))
        assert not r.get("matter_mismatch") and "waits in Envoys" not in msg
        assert "petition" not in msg.lower()
        assert w.dialogue_manager.peek() is top and not _logged(w)

    def test_the_letters_own_words_answer_it_and_the_bare_verb_still_waits(self, board):
        w, client, top = _portugal_on_top(board)
        r = _cmd(client, "refuse it")
        assert r.get("matter_mismatch") is True and SWISS_WAITS in str(r.get("message"))
        r = _cmd(client, "reject the offer")
        assert r.get("success") is True and "rejected Portugal's proposal" in str(r.get("message"))
        assert w.dialogue_manager.peek() is not top and len(_petitions(w)) == 1

    def test_the_vocabulary_keeps_the_letter_noun(self):
        for phrase in LETTER_NOUN_LINES + ("grant the offer",):
            assert petition_vocabulary_answer(phrase) is None, phrase
        assert petition_vocabulary_answer("refuse") == "reject_ai_proposal"
        assert petition_vocabulary_answer("refuse the petition") == "reject_ai_proposal"
        assert DR._LETTER_NOUN_WORDS == frozenset({"offer", "terms", "proposal", "letter"})

    def test_with_the_petition_current_its_own_verb_never_answers_beside_a_letter_noun(self, board):
        w, client, pet = _petition_current(board)
        before = _swiss(w)
        _cmd(client, "refuse the offer")
        assert not _logged(w) and _swiss(w) == before and w.dialogue_manager.peek() is pet
        # …while every letter's generic words still answer it
        r = _cmd(client, "accept the terms")
        assert r.get("success") is True and _swiss(w) == _granted(before)

    def test_lever_down_the_letter_noun_is_filler_again(self, board, monkeypatch):
        monkeypatch.setattr(DR, "THE_MATTER_GUARD_READS_THE_TABLE", False)
        assert petition_vocabulary_answer("refuse the offer") == "reject_ai_proposal"
        w, client, _top = _portugal_on_top(board)
        r = _cmd(client, "refuse the offer")
        assert r.get("matter_mismatch") is True and SWISS_WAITS in str(r.get("message"))


# ═══════════════════════════════════════════════════════════════════════════
# P4-4 — a courtless dialogue is named once
# ═══════════════════════════════════════════════════════════════════════════

class TestP44ACourtlessMatterIsNamedOnce:
    def test_the_advisory_current_and_the_petition_queued(self, board):
        w, client, _top = _portugal_on_top(board)
        _cmd(client, "Talleyrand, assess our situation")
        advisory = w.dialogue_manager.peek()
        assert advisory["type"] == "advisory" and not DR.dialogue_court(advisory)
        for phrase in ("grant the petition", "refuse"):
            r = _cmd(client, phrase)
            assert r.get("matter_mismatch") is True
            assert r.get("message") == ("Sire — the matter before you takes that answer; "
                                        f"{SWISS_WAITS}")
            assert w.dialogue_manager.peek() is advisory and not _logged(w)

    def test_the_article_is_lower_case_after_the_semicolon(self, monkeypatch):
        w = _europe()
        _clear_slot(w)
        _set_rel(w, KOI, PLAYER, -60)
        koi = _deliver(w, _make_proposal(w, KOI))
        client = _swap(monkeypatch, w)
        _cmd(client, "status")
        _cmd(client, "Talleyrand, assess our situation")
        assert w.dialogue_manager.peek()["type"] == "advisory"
        assert koi in list(w.dialogue_manager.iter_queue())
        r = _cmd(client, "grant the petition")
        assert r.get("message") == (
            "Sire — the matter before you takes that answer; the Kingdom of Italy's petition "
            f"waits in Envoys — {ENVOYS_TAIL}")


# ═══════════════════════════════════════════════════════════════════════════
# P4-5 — the court guard names the matter, the place and the article
# ═══════════════════════════════════════════════════════════════════════════

class TestP45TheCourtGuardNamesTheMatterAndThePlace:
    @pytest.mark.parametrize("phrase", [
        "accept switzerland's petition", "reject switzerland's petition",
        "accept the swiss petition", "decline the petition from switzerland"])
    def test_a_court_named_petition_line_is_pointed_at_envoys(self, board, phrase):
        w, client, top = _portugal_on_top(board)
        r = _cmd(client, phrase)
        assert r.get("success") is False and r.get("court_mismatch") is True
        assert r.get("message") == f"{PORTUGAL_HEAD} {SWISS_WAITS}"
        assert w.dialogue_manager.peek() is top and not _logged(w)

    def test_both_guards_say_the_same_thing_about_the_same_row(self, board):
        w, client, _top = _portugal_on_top(board)
        court = _cmd(client, "accept switzerland's petition")
        matter = _cmd(client, "accept the petition")
        assert court.get("court_mismatch") is True and matter.get("matter_mismatch") is True
        assert court.get("message") == matter.get("message")

    def test_the_kingdom_carries_its_article(self, board):
        w, client, _top = _portugal_on_top(board)
        _koi_relief_queued(w)
        r = _cmd(client, "accept the kingdom of italy's petition")
        assert r.get("court_mismatch") is True
        assert r.get("message") == (f"{PORTUGAL_HEAD} The Kingdom of Italy's petition waits in "
                                    f"Envoys — {ENVOYS_TAIL}")
        # the MATTER guard (a petition verb, no letter keyword) names the same
        # row in the same words — narrowed to the waiting court the line names
        matter = _cmd(client, "grant the kingdom of italy's petition")
        assert matter.get("matter_mismatch") is True and not matter.get("court_mismatch")
        assert matter.get("message") == r.get("message")
        assert DR._queued_court_summary(w, [SWISS, KOI]) == (
            "Switzerland and the Kingdom of Italy's petitions wait in Envoys", "Envoys", "them")

    def test_a_queued_ally_petition_is_a_petition_too(self, board):
        w, client, top = _portugal_on_top(board)
        _spain_reward_petition(w)
        r = _cmd(client, "accept spain's petition")
        assert r.get("court_mismatch") is True
        assert r.get("message") == (f"{PORTUGAL_HEAD} Spain's petition waits in Envoys — "
                                    f"{ENVOYS_TAIL}")
        assert w.dialogue_manager.peek() is top

    def test_every_family_is_named_and_an_ordinary_letter_keeps_the_letter_book(self, board):
        """Portugal's letter OPENED FROM ENVOYS: the settlement offer is
        queued behind it, a real ultimatum arrives, Denmark's letter waits."""
        w, client = board
        offer = _pending(w)[0]
        portugal = next(d for d in w.dialogue_manager.iter_queue()
                        if d.get("target_nation") == "Portugal")
        _activate(client, portugal)
        assert w.dialogue_manager.peek() is portugal
        assert offer in list(w.dialogue_manager.iter_queue()) and DR.dialogue_court(offer) == "Britain"
        _prussian_ultimatum(w)
        for phrase, waits in (
                ("accept prussia's ultimatum", "Prussia's ultimatum waits in Envoys"),
                ("accept britain's offer", "Britain's settlement offer waits in Envoys")):
            r = _cmd(client, phrase)
            assert r.get("court_mismatch") is True
            assert r.get("message") == f"{PORTUGAL_HEAD} {waits} — {ENVOYS_TAIL}"
        r = _cmd(client, "accept denmark's offer")                       # CA9's own pin holds
        assert r.get("message") == (f"{PORTUGAL_HEAD} Denmark's matter waits in the letter-book "
                                    f"— open the letter-book and answer it there.")
        assert w.dialogue_manager.peek() is portugal

    def test_the_summary_is_empty_for_a_court_with_nothing_waiting(self, board):
        w, _client, _top = _portugal_on_top(board)
        assert DR._queued_court_summary(w, [SWISS]) == (
            "Switzerland's petition waits in Envoys", "Envoys", "it")
        assert DR._queued_court_summary(w, ["Denmark"]) == (
            "Denmark's matter waits in the letter-book", "the letter-book", "it")
        assert DR._queued_court_summary(w, ["Austria"]) == ("", "", "it")


# ═══════════════════════════════════════════════════════════════════════════
# P4-6 — an ally petition on the table does not own the client petition's words
# ═══════════════════════════════════════════════════════════════════════════

SPAIN_HEAD = ("Sire — Spain's own petition is the matter before you, and it takes "
              "'Grant the Claim' or 'Decline'.")


class TestP46TheAllyPetitionDoesNotOwnTheClientsWords:
    def _staged(self, board):
        """Slice H's OWN producer queues Spain's reward petition on the
        rejected settlement offer; it is opened from Envoys, and the client
        petition waits behind it."""
        w, client, _top = _portugal_on_top(board)
        ally = _spain_reward_petition(w)
        _activate(client, ally)
        assert w.dialogue_manager.peek() is ally and DR.dialogue_court(ally) == "Spain"
        assert _petition_of(w) in list(w.dialogue_manager.iter_queue())
        return w, client, ally

    @pytest.mark.parametrize("phrase", ["grant the petition", "grant it", "refuse it", "refuse"])
    def test_the_client_petitions_words_get_the_waits_line_never_a_shrug(self, board, phrase):
        w, client, ally = self._staged(board)
        before = _swiss(w)
        r = _cmd(client, phrase)
        assert r.get("success") is False and r.get("matter_mismatch") is True
        assert r.get("matter_family") == "petition"
        assert r.get("message") == f"{SPAIN_HEAD} {SWISS_WAITS}"
        assert w.dialogue_manager.peek() is ally and _swiss(w) == before and not _logged(w)

    def test_several_waiting_petitions_are_named_together(self, board):
        w, client, ally = self._staged(board)
        _koi_relief_queued(w)
        r = _cmd(client, "grant the petition")
        assert r.get("message") == (
            f"{SPAIN_HEAD} Switzerland and the Kingdom of Italy's petitions wait in Envoys — "
            f"open Envoys and answer them there.")

    def test_the_ally_petitions_own_word_still_answers_it(self, board):
        w, client, ally = self._staged(board)
        r = _cmd(client, "decline the petition")
        assert r.get("success") is True and not r.get("matter_mismatch"), r.get("message")
        assert ally not in _pending(w)
        assert len(_petitions(w)) == 1 and not _logged(w)

    def test_lever_down_the_line_falls_to_berthiers_shrug(self, board, monkeypatch):
        monkeypatch.setattr(DR, "THE_MATTER_GUARD_READS_THE_TABLE", False)
        w, client, ally = self._staged(board)
        r = _cmd(client, "grant the petition")
        assert not r.get("matter_mismatch") and "waits in Envoys" not in str(r.get("message"))
        assert w.dialogue_manager.peek() is ally


# ═══════════════════════════════════════════════════════════════════════════
# PASS 3 — the second verifier's rulings (September 18, 2026)
#
# THE DESIGN RULING: the plain answer to a CLIENT petition is a CLOSED,
# LITERAL allowlist grammar, and it FAILS CLOSED. Three passes each found new
# phrasings because the rule was "strip what we recognise as filler, see what
# is left"; `petition_plain_answer` now accepts a line only when EVERY token
# is in an allowlist written out word by word beside it. Every line below is
# the verifier's own, reproduced through the REAL endpoints on its geometries
# (V2-1..V2-8 + the NOTED list), lever UP — and lever DOWN wherever a lever
# exists: `A_PETITION_IS_ANSWERED_PLAINLY` still gates the grammar (no new
# lever for it), and pass 3 adds two ROUTING levers, `A_QUESTION_NEVER_
# ANSWERS` (R3-9) and `THE_BUTTON_ROUTE_READS_THE_COURT` (R3-10).
# ═══════════════════════════════════════════════════════════════════════════

PASS3_LEVERS = ("A_QUESTION_NEVER_ANSWERS", "THE_BUTTON_ROUTE_READS_THE_COURT")
REPROMPT = ("The petition takes a plain answer, Sire — nothing was relayed. Answer with one "
            "of: 1=Grant the petition, 2=Refuse the petition.")
SWISS_HEAD = ("Sire — that answer would be delivered to Switzerland, whose matter is the one "
              "before you.")
LETTER_BOOK_TAIL = "open the letter-book and answer it there."


@pytest.fixture(autouse=True)
def _restore_pass3_levers(monkeypatch):
    for name in PASS3_LEVERS:
        monkeypatch.setattr(DR, name, getattr(DR, name))
    yield


def _koi_state(w):
    row = w.vassals.get(KOI) or {}
    return (row.get("loyalty"), row.get("remission_left"), _rel(w, KOI, PLAYER),
            w.diplomatic_points, w.regions["Tyrol"].controller)


def _desk(w):
    """(the dialogue on top, how many wait behind it)."""
    return (w.dialogue_manager.peek(), len(list(w.dialogue_manager.iter_queue())))


def _state_with(w, nation):
    return str(w.get_diplomatic_state(PLAYER, nation))


# ═══════════════════════════════════════════════════════════════════════════
# R3-1 (V2-1 / V2-2 / V2-3) — the plain answer is a closed grammar
# ═══════════════════════════════════════════════════════════════════════════

OTHER_SUBJECT_AT_A_PROVINCE_PETITION = ("grant them relief instead", "grant them relief",
                                        "accept their tribute", "grant them remission")
OTHER_SUBJECT_AT_A_RELIEF_PETITION = ("grant them a province instead", "grant them a province",
                                      "accept their tribute", "grant them tyrol")
FILLER_ONLY_CONDITIONALS = ("if we refuse", "or do we refuse", "if i grant it", "is that a yes",
                            "grant it, if at all", "grant it or", "yes or", "grant it by and by")


class TestR31ThePlainAnswerIsAClosedGrammar:
    @pytest.mark.parametrize("phrase", OTHER_SUBJECT_AT_A_PROVINCE_PETITION)
    @pytest.mark.parametrize("route", ["typed", "button"])
    def test_a_province_petition_is_never_answered_in_the_other_subjects_name(
            self, monkeypatch, phrase, route):
        """V2-1: `grant them relief instead` CEDED TYROL (1 DP, +10, +20)."""
        w, client, pet = _tyrol_board(monkeypatch)
        before, desk = _koi_state(w), _desk(w)
        r = (_cmd(client, phrase) if route == "typed"
             else _respond(client, phrase, pet["dialogue_id"]))
        assert not _logged(w) and _koi_state(w) == before and _desk(w) == desk
        assert w.regions["Tyrol"].controller == PLAYER
        if route == "button":
            assert r.get("success") is False and r.get("message") == REPROMPT

    @pytest.mark.parametrize("phrase", OTHER_SUBJECT_AT_A_RELIEF_PETITION)
    @pytest.mark.parametrize("route", ["typed", "button"])
    def test_a_relief_petition_is_never_answered_in_the_other_subjects_name(
            self, board, phrase, route):
        """The mirror, on the shipped board — and NOTED (d): `accept their
        tribute` must not REMIT the tribute."""
        w, client, pet = _petition_current(board)
        before, desk = _swiss(w), _desk(w)
        r = (_cmd(client, phrase) if route == "typed"
             else _respond(client, phrase, pet["dialogue_id"]))
        assert not _logged(w) and _swiss(w) == before and _desk(w) == desk
        if route == "button":
            assert r.get("success") is False and r.get("message") == REPROMPT

    @pytest.mark.parametrize("phrase", FILLER_ONLY_CONDITIONALS)
    def test_a_conditional_made_only_of_filler_claims_nothing(self, board, phrase):
        """V2-3: `if we refuse` REFUSED at −10 / −20; `is that a yes` GRANTED."""
        w, client, pet = _petition_current(board)
        before, desk = _swiss(w), _desk(w)
        _cmd(client, phrase)
        assert not _logged(w) and _swiss(w) == before and _desk(w) == desk
        r = _respond(client, phrase, pet["dialogue_id"])
        assert r.get("success") is False and r.get("message") == REPROMPT
        assert not _logged(w) and _swiss(w) == before and _desk(w) == desk

    @pytest.mark.parametrize("phrase,answer", [
        # the ruling's measured positives — all must keep answering
        ("so be it, grant it", _granted), ("very well, grant it", _granted),
        ("do grant it", _granted), ("grant it, then", _granted), ("yes, grant it", _granted),
        ("we shall grant it", _granted), ("grant it, of course", _granted),
        ("grant them remission", _granted), ("sire, please grant their request", _granted),
        ("GRANT THE PETITION.", _granted),
        # V2-2: the game's own diplomatic address answers, as on every letter
        ("Talleyrand, grant the petition", _granted), ("grant the petition, Talleyrand", _granted),
        ("Talleyrand, accept the petition", _granted),
        ("Foreign minister, refuse the petition", _refused), ("talleyrand, refuse it", _refused),
        ("refuse the petition for now", _refused),
    ])
    def test_the_measured_positives_still_answer_at_the_quoted_price(self, board, phrase, answer):
        w, client, pet = _petition_current(board)
        before = _swiss(w)
        r = _cmd(client, phrase)
        assert r.get("success") is True, r.get("message")
        assert _swiss(w) == answer(before)
        outcome = "granted" if answer is _granted else "refused"
        assert [e["outcome"] for e in _logged(w)] == [outcome] and not _petitions(w)

    @pytest.mark.parametrize("phrase", ["grant them the province", "please grant them tyrol, sire",
                                        "Talleyrand, grant the italian petition at once"])
    def test_a_province_petitions_own_subject_is_in_its_grammar(self, monkeypatch, phrase):
        w, client, pet = _tyrol_board(monkeypatch)
        dp0 = w.diplomatic_points
        r = _cmd(client, phrase)
        assert r.get("success") is True, r.get("message")
        assert [e["outcome"] for e in _logged(w)] == ["granted"] and not _petitions(w)
        assert w.regions["Tyrol"].controller == KOI and w.diplomatic_points == dp0 - 1

    def test_the_allowlist_is_literal_and_holds_none_of_the_words_that_answered(self):
        """Each set is written out word by word (the ruling); the words the
        three passes measured ANSWERING are in none of them."""
        assert DR._PLAIN_DIPLOMAT_WORDS == frozenset({
            "talleyrand", "diplomat", "envoy", "minister", "ambassador", "foreign"})
        assert DR._PLAIN_ADDRESS_WORDS == DR._PLAIN_DIPLOMAT_WORDS | {"sire", "please"}
        assert DR._PLAIN_PETITION_NOUNS == frozenset({
            "petition", "petitions", "petition's", "request", "requests", "request's",
            "plea", "pleas", "plea's"})
        # FLIPPED in pass 4 (R4-1a, September 18, 2026): `they` LEFT the allowlist —
        # measured, `do they refuse` REFUSED the petition at −10 / −20. A line about
        # what THEY do is not the Emperor's answer.
        assert DR._PLAIN_PRONOUNS == frozenset({"it", "its", "them", "their", "this"})
        assert "they" not in DR._PLAIN_PRONOUNS | DR._PLAIN_FUNCTION_WORDS
        assert DR._PLAIN_PROVINCE_SUBJECT_WORDS == frozenset({"province"})
        assert DR._PLAIN_RELIEF_SUBJECT_WORDS == frozenset({"relief", "remission"})
        assert DR._PLAIN_FUNCTION_WORDS == frozenset({
            "the", "a", "an", "to", "of", "for", "from", "we", "i", "shall", "will", "do",
            "so", "be", "very", "well", "then"})
        assert set(DR._PLAIN_EMPHASIS_PHRASES) == {
            "at once", "gladly", "today", "now", "immediately", "for now", "of course"}
        assert DR._PLAIN_ANSWER_WORDS == {
            "grant": "accept_ai_proposal", "accept": "accept_ai_proposal",
            "agree": "accept_ai_proposal", "yes": "accept_ai_proposal",
            "refuse": "reject_ai_proposal", "reject": "reject_ai_proposal",
            "decline": "reject_ai_proposal"}
        everything = (DR._PLAIN_ADDRESS_WORDS | DR._PLAIN_PETITION_NOUNS | DR._PLAIN_PRONOUNS
                      | DR._PLAIN_PROVINCE_SUBJECT_WORDS | DR._PLAIN_RELIEF_SUBJECT_WORDS
                      | DR._PLAIN_FUNCTION_WORDS | set(DR._PLAIN_ANSWER_WORDS))
        for word in ("instead", "rather", "if", "or", "by", "and", "is", "are", "am", "was",
                     "all", "but", "not", "tribute", "later", "at", "once", "course", "that"):
            assert word not in everything, word
        # the diplomat address is `clause_guards`' own synonym list, spelled out
        from backend.ai.clause_guards import _EMPTY_RESIDUE_WORDS
        assert DR._PLAIN_DIPLOMAT_WORDS <= _EMPTY_RESIDUE_WORDS

    def test_widening_the_general_filler_never_widens_the_grammar(self, board, monkeypatch):
        """The ruling's reason for LITERAL sets: the grammar is not derived
        from `_ANSWER_FILLER_WORDS`, so a word added there answers nothing."""
        w, _client = board
        pet = _petition_of(w)
        monkeypatch.setattr(DR, "_ANSWER_FILLER_WORDS",
                            DR._ANSWER_FILLER_WORDS | {"later", "tomorrow", "perhaps"})
        for phrase in ("grant the petition later", "perhaps grant it", "refuse it tomorrow"):
            assert DR.petition_plain_answer(pet, phrase) is None, phrase
        assert DR.petition_plain_answer(pet, "grant the petition") == "accept_ai_proposal"

    def test_every_answer_word_on_the_line_must_mean_the_same_answer(self, board):
        w, _client = board
        pet = _petition_of(w)
        for phrase in ("refuse it and grant the petition", "yes, refuse it", "accept or reject it",
                       "grant it, refuse it"):
            assert DR.petition_plain_answer(pet, phrase) is None, phrase
        assert DR.petition_plain_answer(pet, "yes, accept it, agree") == "accept_ai_proposal"
        assert DR.petition_plain_answer(pet, "reject it, decline, refuse") == "reject_ai_proposal"

    def test_the_grammar_keeps_its_own_question_and_negation_rules(self, board):
        """Every token of these two lines IS in the grammar, so only the
        grammar's own rules stop them — pinned on the function itself,
        because R3-9 now stops a question one seam earlier on `/command`."""
        w, _client = board
        pet = _petition_of(w)
        assert DR.petition_plain_answer(pet, "do we grant it") is None          # a question
        assert DR.petition_plain_answer(pet, "shall we refuse it") is None
        assert DR.petition_plain_answer(pet, "decline to reject it") is None    # FA-N2's marker
        assert DR.petition_plain_answer(pet, "we do grant it") == "accept_ai_proposal"

    def test_anything_that_is_not_a_word_of_the_grammar_fails_closed(self, board):
        w, _client = board
        pet = _petition_of(w)
        for phrase in ("grant the petition 3", "grant the petition in 3 turns", "grant it & go",
                       "grant it all", "grant it at", "grant it once", "grant it course",
                       "grant holland's petition", "grant the dutch petition", "1", ""):
            assert DR.petition_plain_answer(pet, phrase) is None, phrase
        # …while separators carry no meaning of their own
        assert DR.petition_plain_answer(pet, "Grant it — at once!") == "accept_ai_proposal"

    @pytest.mark.parametrize("phrase,answer", [("grant it by and by", _granted),
                                               ("if we refuse", _refused)])
    def test_lever_down_the_pass_1_router_answers_them_at_price(self, board, monkeypatch,
                                                               phrase, answer):
        """`A_PETITION_IS_ANSWERED_PLAINLY` gates the grammar (no new lever):
        down, the keyword arm answers these exactly as the verifier measured."""
        monkeypatch.setattr(DR, "A_PETITION_IS_ANSWERED_PLAINLY", False)
        w, client, pet = _petition_current(board)
        before = _swiss(w)
        r = _cmd(client, phrase)
        assert r.get("success") is True, r.get("message")
        assert _swiss(w) == answer(before) and len(_logged(w)) == 1


# ═══════════════════════════════════════════════════════════════════════════
# R3-2 (V2-7, V2-2's second half) — nothing is mounted over a current petition
# ═══════════════════════════════════════════════════════════════════════════

REPROMPTED_IN_PLACE = (
    "accept, they have earned it",                 # (b) an answer word, then a comma
    "sire, accept; they have earned it", "yes - but later", "yes, refuse it",
    "accept, should i?",                           # (b) holds for a question too
    "Talleyrand, grant the petition later",        # (c) diplomat-addressed + an answer word
    "Talleyrand, tell them yes", "grant the petition later, Talleyrand",
)


class TestR32NothingIsMountedOverTheCurrentPetition:
    @pytest.mark.parametrize("phrase", REPROMPTED_IN_PLACE)
    def test_a_line_that_was_trying_to_answer_is_reprompted_in_place(self, board, phrase):
        w, client, pet = _petition_current(board)
        before, desk, history = _swiss(w), _desk(w), len(w.command_history)
        r = _cmd(client, phrase)
        assert r.get("success") is False and r.get("petition_reprompt") is True
        assert r.get("message") == REPROMPT
        assert w.dialogue_manager.peek() is pet and _desk(w) == desk      # nothing mounted
        assert not _logged(w) and _swiss(w) == before
        assert len(w.command_history) == history                         # never a phantom order

    def test_the_next_plain_answer_then_answers_it(self, board):
        """The verifier's sequel: after the chatty yes the plain `grant the
        petition` was REFUSED twice ('…waits in Envoys')."""
        w, client, pet = _petition_current(board)
        before = _swiss(w)
        _cmd(client, "accept, they have earned it")
        r = _cmd(client, "grant the petition")
        assert r.get("success") is True and not r.get("matter_mismatch"), r.get("message")
        assert _swiss(w) == _granted(before) and not _petitions(w)

    def test_an_order_keeps_the_ordinary_road(self, board):
        w, client, pet = _petition_current(board)
        autonomy = w.vassals[SWISS]["autonomy"]
        r = _cmd(client, "grant switzerland more autonomy")
        assert r.get("success") is True and not r.get("petition_reprompt"), r.get("message")
        assert w.vassals[SWISS]["autonomy"] == autonomy + 1
        r = _cmd(client, "Soult, the petition can wait, march to Swabia")
        assert r.get("success") is True and w.marshals["Soult"].location == "Swabia"
        r = _cmd(client, "Ney, accept, and hold")                        # a marshal is named
        assert not r.get("petition_reprompt")
        assert w.dialogue_manager.peek() is pet and not _logged(w)

    def test_a_deferral_without_the_shape_still_reaches_berthier(self, board):
        w, client, pet = _petition_current(board)
        r = _cmd(client, "grant the petition later")
        assert not r.get("petition_reprompt")
        assert "For a later day, Sire" in str(r.get("message"))
        assert w.dialogue_manager.peek() is pet

    def test_it_is_the_client_petitions_rule_and_the_levers(self, board, monkeypatch):
        w, client, pet = _petition_current(board)
        roster = [m.name for m in w.get_player_marshals()]
        assert DR.petition_line_reprompt(pet, "accept, they have earned it", roster)["message"] == REPROMPT
        assert DR.petition_line_reprompt(pet, "grant the petition", roster) is None     # a plain answer
        assert DR.petition_line_reprompt(pet, "Ney, accept, and hold", roster) is None  # an order
        # …shape (b) and all: a line that names a marshal is an ORDER (UX23-R5)
        assert DR.petition_line_reprompt(pet, "accept, and let Ney hold", roster) is None
        assert DR.petition_line_reprompt(pet, "accept, and let Ney hold", [])["message"] == REPROMPT
        assert DR.petition_line_reprompt(pet, "they have earned it", roster) is None    # no answer word
        letter = {"type": "incoming_proposal", "target_nation": "Portugal", "context": {},
                  "options": [{"label": "Accept", "action": "accept_ai_proposal"},
                              {"label": "Reject", "action": "reject_ai_proposal"}]}
        assert DR.petition_line_reprompt(letter, "accept, they have earned it", roster) is None
        monkeypatch.setattr(DR, "A_PETITION_IS_ANSWERED_PLAINLY", False)
        assert DR.petition_line_reprompt(pet, "accept, they have earned it", roster) is None
        before = _swiss(w)
        r = _cmd(client, "accept, they have earned it")                  # pass 1: the keyword arm
        assert r.get("success") is True and _swiss(w) == _granted(before)


# ═══════════════════════════════════════════════════════════════════════════
# R3-3 (V2-4) — the court guard speaks first
# ═══════════════════════════════════════════════════════════════════════════

class TestR33TheCourtGuardSpeaksFirst:
    @pytest.mark.parametrize("phrase,court", [
        ("accept portugal's offer", "Portugal"), ("reject denmark's proposal", "Denmark"),
        ("accept the offer from portugal", "Portugal"),
        ("decline the portuguese offer", "Portugal"),
        ("Talleyrand, accept portugal's offer", "Portugal"),
    ])
    def test_a_line_that_names_a_waiting_letters_court(self, board, phrase, court):
        w, client, pet = _petition_current(board)
        before, desk = _swiss(w), _desk(w)
        r = _cmd(client, phrase)
        assert r.get("success") is False and r.get("court_mismatch") is True
        assert r.get("message") == (f"{SWISS_HEAD} {court}'s matter waits in the letter-book — "
                                    f"{LETTER_BOOK_TAIL}")
        assert _state_with(w, court) == "PEACE"
        assert not _logged(w) and _swiss(w) == before and _desk(w) == desk

    @pytest.mark.parametrize("phrase", ["grant the kingdom of italy's petition",
                                        "refuse the italian petition",
                                        "accept the kingdom of italy's petition"])
    def test_a_line_that_names_the_other_waiting_petition(self, board, phrase):
        """P4-5's own sentence, reachable again."""
        w, client = board
        pet = _petition_of(w)
        koi = _koi_relief_queued(w)
        _activate(client, pet)
        before, koi_before, desk = _swiss(w), _koi_state(w), _desk(w)
        r = _cmd(client, phrase)
        assert r.get("success") is False and r.get("court_mismatch") is True
        assert r.get("message") == (f"{SWISS_HEAD} The Kingdom of Italy's petition waits in "
                                    f"Envoys — {ENVOYS_TAIL}")
        assert not _logged(w) and _swiss(w) == before and _koi_state(w) == koi_before
        assert _desk(w) == desk and koi in list(w.dialogue_manager.iter_queue())

    def test_a_line_that_names_the_waiting_ally_petition(self, board):
        w, client, _top = _portugal_on_top(board)
        ally = _spain_reward_petition(w)
        pet = _petition_of(w)
        _activate(client, pet)
        before, desk = _swiss(w), _desk(w)
        r = _cmd(client, "decline spain's petition")
        assert r.get("court_mismatch") is True
        assert r.get("message") == f"{SWISS_HEAD} Spain's petition waits in Envoys — {ENVOYS_TAIL}"
        assert ally in _pending(w) and _swiss(w) == before and _desk(w) == desk

    def test_the_head_carries_the_active_courts_article(self, monkeypatch):
        """NOTED (c): the head composed the bare "delivered to Kingdom of Italy"."""
        w, client, pet = _tyrol_board(monkeypatch)
        _deliver(w, _ordinary("Portugal", "open_borders"))
        assert w.dialogue_manager.peek() is pet
        r = _cmd(client, "accept portugal's offer")
        assert r.get("court_mismatch") is True
        assert r.get("message") == (
            "Sire — that answer would be delivered to the Kingdom of Italy, whose matter is the "
            f"one before you. Portugal's matter waits in the letter-book — {LETTER_BOOK_TAIL}")
        assert _state_with(w, "Portugal") == "PEACE" and w.dialogue_manager.peek() is pet

    def test_only_an_answer_shaped_line_and_only_a_client_petition(self, board, monkeypatch):
        w, client, pet = _petition_current(board)
        guard = DR.court_mismatch_refusal_for_a_petition
        assert guard(w, pet, "accept portugal's offer")["court_mismatch"] is True
        assert guard(w, pet, "send an envoy to portugal with gifts") is None      # an order
        assert guard(w, pet, "accept switzerland's petition") is None             # the active court
        portugal = next(d for d in w.dialogue_manager.iter_queue()
                        if d.get("target_nation") == "Portugal")
        assert guard(w, portugal, "accept denmark's offer") is None               # the handler seam's
        monkeypatch.setattr(DR, "A_PETITION_IS_ANSWERED_PLAINLY", False)
        assert guard(w, pet, "accept portugal's offer") is None


# ═══════════════════════════════════════════════════════════════════════════
# R3-4 (V2-5) — a moot petition quotes no price it will not charge
# ═══════════════════════════════════════════════════════════════════════════

PRICED_REFUSAL_COPY = ("loses 10 loyalty", "a lapse is a refusal", "−10", "falls 20")
MOOT_LAPSE = "Switzerland's petition is moot — a lapse costs nothing."


def _every_read_surface(client, pet):
    ip = _pending_envoy(client)["incoming_proposal"]
    return ip, json.dumps([ip["clauses"], ip["options"], ip.get("talleyrand_assessment"),
                           [o.get("description") for o in pet["options"]],
                           pet["talleyrand_text"].split("Talleyrand:")[0]], ensure_ascii=False)


class TestR34AMootPetitionQuotesNoPriceItWillNotCharge:
    def test_milan_falls_after_a_prior_read(self, monkeypatch):
        w, client, pet = _tyrol_board(monkeypatch)
        ip, prose = _every_read_surface(client, pet)
        assert "loses 10 loyalty" in prose and "a lapse is a refusal" in prose     # the live quote
        _milan_falls(w)
        ip, prose = _every_read_surface(client, pet)
        void = f"{CONTIGUITY_VOID} — the petition is withdrawn."
        assert ip["clauses"] == [void, "A lapse withdraws the petition; nothing is charged."]
        for copy_ in PRICED_REFUSAL_COPY:
            assert copy_ not in prose, copy_
        refuse = next(o for o in pet["options"] if o["action"] == "reject_ai_proposal")
        assert refuse["description"] == (f"{CONTIGUITY_VOID} — a lapse withdraws the petition; "
                                         f"nothing is charged.")
        forecast = V.lapse_forecast(w, KOI, PLAYER, pet["context"]["proposal"]["petition"])
        assert forecast["penalised"] is False and refuse["description"] == forecast["price_line"]
        before = _koi_state(w)
        r = _respond(client, "reject_ai_proposal", pet["dialogue_id"])          # shown == applied
        assert _verdict(client, r)["outcome"] == "WITHDRAWN" and _koi_state(w) == before

    def test_the_same_across_a_save_and_a_load(self, monkeypatch):
        w, client, pet = _tyrol_board(monkeypatch)
        _every_read_surface(client, pet)                                         # the prior read
        _milan_falls(w)
        snapshot = json.loads(json.dumps(copy.deepcopy(w.to_dict())))
        w2, client2 = _restore(monkeypatch, snapshot)
        pet2 = _petition_of(w2)
        if w2.dialogue_manager.peek() is not pet2:
            _activate(client2, pet2)
        ip, prose = _every_read_surface(client2, pet2)
        assert ip["clauses"][-1] == "A lapse withdraws the petition; nothing is charged."
        for copy_ in PRICED_REFUSAL_COPY:
            assert copy_ not in prose, copy_

    def test_the_players_own_release_with_the_petition_on_the_desk(self, board):
        w, client, pet = _petition_current(board)
        _every_read_surface(client, pet)                                         # the prior read
        assert _cmd(client, "release switzerland").get("success") is True
        ip, prose = _every_read_surface(client, pet)
        assert ip["clauses"] == [RELEASED, MOOT_LAPSE]
        for copy_ in PRICED_REFUSAL_COPY:
            assert copy_ not in prose, copy_
        refuse = next(o for o in pet["options"] if o["action"] == "reject_ai_proposal")
        assert refuse["description"] == MOOT_LAPSE
        lp = _cmd(client, "status")["pending_lapsing_petitions"]
        assert lp[0]["price_line"] == MOOT_LAPSE                                 # one vocabulary
        r = _cmd(client, "refuse the petition")
        assert "moot" in str(r.get("message")) and not _logged(w) and not _petitions(w)

    def test_the_priced_lines_stay_when_the_forecast_says_refused(self, board):
        """The one moot arm whose refusal IS charged (a relief of nothing —
        staged; pass 1 measured it not organically reachable): forecast ==
        applied, so the refuse and lapse lines are true and they stay."""
        w, client, pet = _petition_current(board)
        _every_read_surface(client, pet)
        w.vassals[SWISS]["tribute_rate"] = 0.0
        petition = pet["context"]["proposal"]["petition"]
        assert V.reprice_petition(w, PLAYER, SWISS, petition) is None            # moot…
        assert V.lapse_forecast(w, SWISS, PLAYER, petition)["penalised"] is True  # …and priced
        ip, prose = _every_read_surface(client, pet)
        assert "pays no tribute now" in ip["clauses"][0]
        assert "loses 10 loyalty" in prose and "a lapse is a refusal" in prose
        before = _swiss(w)
        _respond(client, "reject_ai_proposal", pet["dialogue_id"])
        assert _swiss(w)[0] == before[0] - V.PETITION_REFUSAL_LOYALTY            # it WAS charged


# ═══════════════════════════════════════════════════════════════════════════
# R3-5 (V2-6) — the shape gate knows the grammar's emphasis
# ═══════════════════════════════════════════════════════════════════════════

EMPHATIC_LINES = ("grant the petition at once", "accept the petition gladly",
                  "please grant the swiss petition today", "refuse it for now",
                  "Talleyrand, grant the petition")


class TestR35TheShapeGateKnowsTheEmphasis:
    @pytest.mark.parametrize("phrase", EMPHATIC_LINES)
    def test_the_petition_queued_keeps_its_envoys_pointer(self, board, phrase):
        """The ORDINARY shipped board: the settlement offer current."""
        w, client = board
        before, desk = _swiss(w), _desk(w)
        r = _cmd(client, phrase)
        assert r.get("success") is False and r.get("matter_mismatch") is True
        assert SWISS_WAITS in str(r.get("message"))
        assert not _logged(w) and _swiss(w) == before and _desk(w) == desk

    def test_an_emphatic_order_still_reaches_the_executor(self, board):
        w, client = board
        _prussian_ultimatum(w)
        r = _cmd(client, "send ultimatum to Austria at once")
        assert not r.get("matter_mismatch")
        assert "already at war with Austria" in str(r.get("message"))

    def test_the_shape_reads_the_phrases_and_the_lever(self, board, monkeypatch):
        w, _client = board
        for line in EMPHATIC_LINES + ("accept the offer from portugal",):
            assert DR._line_is_answer_shaped(line, w) is True, line
        for line in ("send ultimatum to austria at once", "grant it once", "grant it course",
                     "grant the petition later"):
            assert DR._line_is_answer_shaped(line, w) is False, line
        monkeypatch.setattr(DR, "A_PETITION_IS_ANSWERED_PLAINLY", False)
        for line in EMPHATIC_LINES[:3] + ("accept the offer from portugal",):
            assert DR._line_is_answer_shaped(line, w) is False, line         # pass 2's gate


# ═══════════════════════════════════════════════════════════════════════════
# R3-6 (V2-8) — a court-named line is not owned by the active petition
# ═══════════════════════════════════════════════════════════════════════════

class TestR36ACourtNamedLineIsNotOwnedByTheActivePetition:
    def _staged(self, board):
        w, client, _top = _portugal_on_top(board)
        ally = _spain_reward_petition(w)
        _activate(client, ally)
        assert w.dialogue_manager.peek() is ally
        return w, client, ally

    @pytest.mark.parametrize("phrase", ["grant switzerland's petition",
                                        "refuse the swiss petition"])
    def test_the_explicit_line_gets_the_pointer_the_bare_verb_gets(self, board, phrase):
        w, client, ally = self._staged(board)
        before = _swiss(w)
        bare = _cmd(client, "grant")
        r = _cmd(client, phrase)
        assert r.get("success") is False and r.get("matter_mismatch") is True
        assert r.get("message") == f"{SPAIN_HEAD} {SWISS_WAITS}" == bare.get("message")
        assert w.dialogue_manager.peek() is ally and _swiss(w) == before and not _logged(w)

    def test_a_line_that_names_no_waiting_court_is_still_the_active_petitions(self, board):
        w, client, ally = self._staged(board)
        for phrase in ("grant austria's petition", "grant the dutch petition"):
            r = _cmd(client, phrase)                                      # nothing of theirs waits
            assert not r.get("matter_mismatch") and "waits in Envoys" not in str(r.get("message"))
            assert w.dialogue_manager.peek() is ally
        r = _cmd(client, "decline the petition")                          # pass 2's pin stands
        assert r.get("success") is True and ally not in _pending(w)

    def test_lever_down_the_explicit_line_is_shrugged_at(self, board, monkeypatch):
        monkeypatch.setattr(DR, "THE_MATTER_GUARD_READS_THE_TABLE", False)
        w, client, ally = self._staged(board)
        r = _cmd(client, "grant switzerland's petition")
        assert not r.get("matter_mismatch") and "waits in Envoys" not in str(r.get("message"))


# ═══════════════════════════════════════════════════════════════════════════
# R3-7 (NOTED a) — a typed Grant never says "Command executed"
# ═══════════════════════════════════════════════════════════════════════════

class TestR37ATypedGrantStatesItsReason:
    def test_the_typed_grant_at_the_ally_petition(self, board):
        w, client, _top = _portugal_on_top(board)
        ally = _spain_reward_petition(w)
        _activate(client, ally)
        typed = _cmd(client, "grant the claim")
        assert typed.get("success") is False and typed.get("message") != "Command executed"
        assert typed.get("message") == typed.get("error_display")
        assert str(typed.get("message")).startswith(
            "The settlement table for this war is not open in authoring, Sire.")
        assert ally in _pending(w)                                         # nothing was consumed
        button = _respond(client, SO.ALLY_SETTLEMENT_PETITION_GRANT_ACTION, ally["dialogue_id"])
        assert button.get("message") == typed.get("message")               # PF-1, both roads

    def test_the_builder_falls_back_only_when_there_is_no_message(self):
        w = _europe()
        build = M._build_command_response
        assert build({"success": False, "error_display": "The stated reason."}, w)["message"] == (
            "The stated reason.")
        assert build({"success": False, "message": "Said.", "error_display": "Other."}, w)[
            "message"] == "Said."
        assert build({"success": True}, w)["message"] == "Command executed"


# ═══════════════════════════════════════════════════════════════════════════
# R3-8 (NOTED b, B2's note) — the title's article, and the VS-3 cede copy
# ═══════════════════════════════════════════════════════════════════════════

class TestR38TheTitleAndTheCedeCopy:
    def test_the_rail_title_takes_the_article_and_the_heading_stays_bare(self, monkeypatch):
        w, client, pet = _tyrol_board(monkeypatch)
        assert "Petition from the Kingdom of Italy" in _titles(w)
        with _quiet():
            items = client.get("/mailbox").json()["items"]
        assert [i["summary"] for i in items] == ["Kingdom of Italy — Client's Petition"]

    def test_a_court_without_an_article_is_unchanged(self, board):
        w, _client = board
        assert "Petition from Switzerland" in _titles(w)

    def test_the_typed_cede_names_the_court(self, monkeypatch):
        w = _europe()
        _stage_tyrol_for_koi(w)
        w.regions["Carniola"].controller = PLAYER
        w.invalidate_active_nations_cache()
        client = _swap(monkeypatch, w)
        r = _cmd(client, "cede tyrol to the kingdom of italy")
        msg = str(r.get("message"))
        assert r.get("success") is True and w.regions["Tyrol"].controller == KOI
        assert msg.startswith("Tyrol is ceded to the Kingdom of Italy. ")
        assert "the Kingdom of Italy now remits 75% of it as tribute" in msg
        refused = str(_cmd(client, "cede carniola to the kingdom of italy").get("message"))
        assert refused.startswith("A grant to the Kingdom of Italy is still being settled")
        assert KOI not in msg + refused and KOI not in _campaign_log_blob(client)

    def test_every_sentence_of_the_verb(self):
        w = _europe()
        assert V.grant_region_to_vassal(w, KOI, "Tyrol", actor="Austria")["message"] == (
            "Cannot cede territory to the Kingdom of Italy: not your vassal.")
        assert V.grant_region_to_vassal(w, "Prussia", "Tyrol")["message"] == (
            "Prussia is not a vassal.")


# ═══════════════════════════════════════════════════════════════════════════
# R3-9 — a question is never an answer, for ANY dialogue
# ═══════════════════════════════════════════════════════════════════════════

QUESTIONS = ("should i accept?", "accept?", "can we accept", "should we accept the offer",
             "do we reject it", "reject it?")


class TestR39AQuestionIsNeverAnAnswer:
    @pytest.mark.parametrize("phrase", QUESTIONS)
    def test_a_question_at_an_ordinary_letter_signs_nothing(self, board, phrase):
        w, client, top = _portugal_on_top(board)
        r = _cmd(client, phrase)
        assert _state_with(w, "Portugal") == "PEACE" and w.dialogue_manager.peek() is top
        assert "You have" not in str(r.get("message"))

    def test_lever_down_the_question_signs_the_treaty(self, board, monkeypatch):
        monkeypatch.setattr(DR, "A_QUESTION_NEVER_ANSWERS", False)
        w, client, top = _portugal_on_top(board)
        r = _cmd(client, "should i accept?")
        assert r.get("success") is True and _state_with(w, "Portugal") == "OPEN_BORDERS"

    def test_the_button_routes_free_text(self, board, monkeypatch):
        w, client, top = _portugal_on_top(board)
        r = _respond(client, "should i accept?", top["dialogue_id"])
        assert r.get("success") is False
        assert r.get("message") == ("A question is not an answer, Sire — nothing was relayed. "
                                    "Answer with one of: 1=Accept, 2=Reject, 3=Counter-offer.")
        assert _state_with(w, "Portugal") == "PEACE" and w.dialogue_manager.peek() is top
        monkeypatch.setattr(DR, "A_QUESTION_NEVER_ANSWERS", False)
        r = _respond(client, "should i accept?", top["dialogue_id"])
        assert r.get("success") is True and _state_with(w, "Portugal") == "OPEN_BORDERS"

    def test_an_exact_id_a_digit_and_an_exact_label_are_exempt(self):
        asks = {"type": "advisory", "context": {}, "options": [
            {"label": "Shall we proceed?", "action": "execute_suggestion"},
            {"label": "Dismiss", "action": "dismiss"}]}
        assert DR.match_dialogue_answer(asks, "shall we proceed?") == "shall we proceed?"
        assert DR.match_dialogue_answer(asks, "execute_suggestion") == "execute_suggestion"
        assert DR.line_asks_a_question("1", asks["options"]) is False
        assert DR.line_asks_a_question("shall we proceed?", asks["options"]) is False
        # FLIPPED in pass 4 (R4-2, September 18, 2026). Pass 3 asserted `shall we
        # proceed? yes` IS a question (exempting a byte-exact label only) — and that
        # rule stopped the advisory's own question-shaped labels resolving with a
        # lead-in or without their `?`. A line that carries EVERY word of a
        # question-shaped label is that label; one that does not is still a question.
        assert DR.line_asks_a_question("shall we proceed? yes", asks["options"]) is False
        assert DR.match_dialogue_answer(asks, "shall we proceed? yes") == "shall we proceed?"
        assert DR.line_asks_a_question("shall we? yes", asks["options"]) is True
        assert DR.match_dialogue_answer(asks, "shall we? yes") is None
        assert DR.match_dialogue_answer(asks, "should i dismiss") is None       # no `?`, still asks
        assert DR.match_dialogue_answer(asks, "dismiss") == "dismiss"

    def test_a_question_at_a_hard_stop_executes_nothing(self, board):
        w, client, _top = _portugal_on_top(board)
        _cmd(client, "declare war on Prussia")
        stop = w.dialogue_manager.peek()
        assert stop["type"] == "war_purpose_selection" and w.dialogue_manager.is_hard_stop()
        for phrase in ("should i proceed?", "can we cancel", "Ney, should i attack Mack?"):
            ap = w.actions_remaining
            r = _cmd(client, phrase)
            assert r.get("success") is False
            assert str(r.get("message")).startswith("Our purpose in this war awaits your answer")
            assert w.dialogue_manager.peek() is stop and w.actions_remaining == ap
            assert _state_with(w, "Prussia") == "PEACE"


# ═══════════════════════════════════════════════════════════════════════════
# R3-10 — the free-text button route reads the court
# ═══════════════════════════════════════════════════════════════════════════

class TestR310TheButtonRouteReadsTheCourt:
    def test_free_text_that_names_another_court_signs_nothing(self, board):
        w, client, top = _portugal_on_top(board)
        r = _respond(client, "accept Switzerland's petition", top["dialogue_id"])
        assert r.get("success") is False and r.get("court_mismatch") is True
        assert r.get("message") == f"{PORTUGAL_HEAD} {SWISS_WAITS}"
        r = _respond(client, "accept the petition", top["dialogue_id"])
        assert r.get("matter_mismatch") is True and r.get("message") == f"{PORTUGAL_HEAD} {SWISS_WAITS}"
        assert _state_with(w, "Portugal") == "PEACE" and w.dialogue_manager.peek() is top
        assert not _logged(w)

    def test_what_the_client_actually_sends_still_answers(self, board):
        """Measured: no shipped caller sends free text. The Godot client sends
        1-based indexes, exact action ids and the bare words accept / reject /
        counter; the playtest driver sends exact action ids."""
        w, client, top = _portugal_on_top(board)
        r = _respond(client, "accept", top["dialogue_id"])
        assert r.get("success") is True and _state_with(w, "Portugal") == "OPEN_BORDERS"
        popup = (GODOT_SCRIPTS / "incoming_proposal_popup.gd").read_text(encoding="utf-8")
        assert set(re.findall(r'choice_made\.emit\("(\w+)"', popup)) == {
            "accept", "counter", "reject", "dismiss"}

    def test_a_button_token_carries_no_raw_text(self, board):
        w, _client, top = _portugal_on_top(board)
        for token in (1, "2", "accept_ai_proposal", "Accept", "accept", " REJECT ",
                      "settlement_dial_harsher", ""):
            assert DR.free_text_of_choice(top, token) is None, token
        assert DR.free_text_of_choice(top, "accept it") == "accept it"
        assert DR.free_text_of_choice(top, "accept Switzerland's petition") == (
            "accept Switzerland's petition")

    def test_lever_down_the_free_text_signs_portugals_letter(self, board, monkeypatch):
        monkeypatch.setattr(DR, "THE_BUTTON_ROUTE_READS_THE_COURT", False)
        w, client, top = _portugal_on_top(board)
        assert DR.free_text_of_choice(top, "accept Switzerland's petition") is None
        r = _respond(client, "accept Switzerland's petition", top["dialogue_id"])
        assert r.get("success") is True and _state_with(w, "Portugal") == "OPEN_BORDERS"


# ═══════════════════════════════════════════════════════════════════════════
# R3-11 — the hard-stop endpoint pins build their own world
# ═══════════════════════════════════════════════════════════════════════════

class TestR311TheHardStopPinsBuildTheirOwnWorld:
    def test_a_world_left_behind_with_letters_mounted_is_not_inherited(self, monkeypatch):
        """`tests/test_igr_f_envoy_digest.py` installs worlds and used to leave
        one — letters mounted — as the active world; `test_pt_a_regressions`'
        hard stop then queued BEHIND them (three failures, that order only)."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_pt_a_for_r311", REPO / "tests" / "test_pt_a_regressions.py")
        pt_a = importlib.util.module_from_spec(spec)
        with _quiet():
            spec.loader.exec_module(pt_a)
        left_behind = _europe()
        _clear_slot(left_behind)
        _deliver(left_behind, _ordinary("Portugal", "open_borders"))
        assert left_behind.dialogue_manager.peek() is not None
        monkeypatch.setattr(M, "world", left_behind)
        monkeypatch.setitem(M.game_state, "world", left_behind)
        with _quiet():
            _client, main = pt_a.TestTheHardStopRefusalThroughTheEndpoint()._client(monkeypatch)
        assert main.world is not left_behind and main.game_state["world"] is main.world
        assert main.world.dialogue_manager.peek() is None
        main.world.dialogue_manager.push(pt_a._war_purpose_dialogue())
        assert main.world.dialogue_manager.is_hard_stop()


# ═══════════════════════════════════════════════════════════════════════
# IQ7-X7 — ROUTED, pinned as CURRENT behaviour (owner: CR-6 proper)
# ═══════════════════════════════════════════════════════════════════════

class TestIQ7X7TheDeferralLimitOnOtherFamilies:
    """The closed grammar is the CLIENT petition's alone (pass 3's ruling). On
    every other dialogue family a deferred or conditional typed answer still
    resolves — measured September 18, 2026 with Portugal's letter current:
    each line below SIGNS the treaty. Pass 3 stopped the QUESTION for every
    family (`A_QUESTION_NEVER_ANSWERS`); the deferral half is BUG_FIXES
    IQ7-X7, routed to CR-6 proper. When that row lands these lines must
    resolve to None and this pin FLIPS — it exists so the limit cannot be
    forgotten, not because the behaviour is wanted."""

    LETTER = {"type": "incoming_proposal", "target_nation": "Portugal",
              "context": {"proposal_type": "open_borders"},
              "options": [{"label": "Accept", "action": "accept_ai_proposal"},
                          {"label": "Reject", "action": "reject_ai_proposal"},
                          {"label": "Counter-offer", "action": "counter_ai_proposal"}]}

    @pytest.mark.parametrize("line", [
        "accept the offer later", "accept it next turn", "yes, later",
        "if we accept", "accept the offer, but not now"])
    def test_a_deferred_answer_still_answers_an_ordinary_letter(self, line):
        assert DR.match_dialogue_answer(self.LETTER, line) is not None

    def test_a_hedged_answer_is_closed_by_crt3(self):
        """⚠ CONSCIOUS PIN FLIP, on this class's own instruction, September
        26, 2026 (Score Mandate SR-3a). `maybe accept` was in the deferral
        list above and signed the treaty. CRT-5's ruling (the CR-6 triage,
        `COMMAND_ROBUSTNESS_SPEC.md` §12.5-6) is that a HEDGED answer is not
        a plain answer and fails closed — and CRT-3's hedge arm
        (`clause_guards.A_HEDGE_IS_NOT_AN_ORDER`: `perhaps build ships` laid
        a keel) reads a hedge as a question, so pass 3's
        `A_QUESTION_NEVER_ANSWERS` closes this line one slice early, with
        no change to the dialogue layer.

        ⚠ IQ7-X7 is only PARTLY closed by this. The five lines above are
        real deferrals ("accept it next turn"), carry neither an
        interrogative lead nor a hedge, and stay CRT-5's."""
        assert DR.match_dialogue_answer(self.LETTER, "maybe accept") is None
        assert DR.match_dialogue_answer(self.LETTER, "perhaps accept") is None
        from backend.ai import clause_guards as _CG
        original = _CG.A_HEDGE_IS_NOT_AN_ORDER
        try:
            _CG.A_HEDGE_IS_NOT_AN_ORDER = False
            assert DR.match_dialogue_answer(
                self.LETTER, "maybe accept") is not None, "lever off = the old reading"
        finally:
            _CG.A_HEDGE_IS_NOT_AN_ORDER = original

    def test_is_that_a_yes_is_closed_by_cx_slice_1(self):
        """⚠ CONSCIOUS PIN FLIP, on this class's own instruction ("when that
        row lands these lines must resolve to None and this pin FLIPS").

        `is that a yes` was in the deferral list above and signed the treaty.
        It is not a deferral at all — it is a QUESTION, and CX slice 1 gave
        `is` / `are` / `was` / `does` / `has` … the reading they always had in
        English: no imperative opens with them, so they lead a question
        whatever follows. Pass 3's `A_QUESTION_NEVER_ANSWERS` then does the
        rest, with no change to the dialogue layer at all.

        ⚠ IQ7-X7 is only PARTLY closed by this. The six lines above are real
        deferrals ("accept it next turn"), carry no interrogative lead, and
        stay CR-6 proper's.
        """
        assert DR.match_dialogue_answer(self.LETTER, "is that a yes") is None
        from backend.ai import clause_guards as _CG
        original = _CG.A_QUESTION_NEVER_ORDERS
        try:
            _CG.A_QUESTION_NEVER_ORDERS = False
            assert DR.match_dialogue_answer(
                self.LETTER, "is that a yes") is not None, "lever off = the old reading"
        finally:
            _CG.A_QUESTION_NEVER_ORDERS = original

    def test_the_question_half_is_closed_for_every_family(self):
        assert DR.match_dialogue_answer(self.LETTER, "should i accept?") is None
        assert DR.match_dialogue_answer(self.LETTER, "accept") is not None


# ═══════════════════════════════════════════════════════════════════════════
# PASS 4 — THE FINAL PASS: the two pass-3 verifiers' rulings (September 18, 2026)
#
# Every line below is a verifier's own, reproduced with its own probe before
# the fix and re-run after (`build3/verify_grammar/`, `build3/seams/`). No new
# lever: R4-1 rides pass 2's `A_PETITION_IS_ANSWERED_PLAINLY`, R4-2 and R4-3
# ride pass 3's `A_QUESTION_NEVER_ANSWERS`, R4-4 rides the plain lever, and
# R4-5 is copy (R7, GR6).
# ═══════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════
# R4-1 (verifier A, F1) — a question made of allowlist tokens never answers
# ═══════════════════════════════════════════════════════════════════════════

QUESTIONS_MADE_OF_THE_GRAMMAR = (
    "then shall we grant it", "sire shall we grant it", "talleyrand shall we grant it",
    "the petition, shall we grant it", "today do we grant it", "yes shall we grant it",
    "then do we refuse it", "then will we refuse", "sire do we refuse", "talleyrand do we refuse",
    "very well, do we refuse it", "well then shall we refuse it", "for now shall we refuse it",
    "do they refuse", "do the swiss accept", "grant it, shall we", "we grant it, do we",
)
QUESTIONS_AT_THE_PROVINCE_PETITION = (
    "then shall we grant tyrol", "then do we grant them the province",
    "sire do we refuse them tyrol")
STATEMENTS_THAT_STILL_ANSWER = (
    ("we shall grant it", _granted), ("i will grant it", _granted), ("do grant it", _granted),
    ("i do accept", _granted), ("so be it, grant it", _granted),
    ("very well, grant it", _granted), ("grant it, then", _granted), ("yes, grant it", _granted),
    ("Talleyrand, grant the petition", _granted),
    ("we will refuse", _refused), ("we do refuse it", _refused),
)
# The verifier's own simulation table (`p6_fix_shape_sim.py`): every pinned or
# measured positive of passes 2 and 3 — each must keep its action.
THE_39_POSITIVES_SWISS = (
    "Grant the petition, Sire", "accept the petition", "accept switzerland's petition",
    "grant the swiss petition", "accept the petition from switzerland",
    "grant the petition at once", "yes, grant it", "grant their petition",
    "accept the petition for relief", "yes", "decline the petition", "reject it",
    "so be it, grant it", "very well, grant it", "do grant it", "grant it, then",
    "we shall grant it", "grant it, of course", "grant them remission",
    "sire, please grant their request", "GRANT THE PETITION.", "Talleyrand, grant the petition",
    "grant the petition, Talleyrand", "Talleyrand, accept the petition",
    "Foreign minister, refuse the petition", "talleyrand, refuse it",
    "refuse the petition for now", "i will grant it", "we will refuse", "i do accept",
    "we do refuse it", "accept the terms", "accept_ai_proposal", "reject_ai_proposal",
)
THE_39_POSITIVES_KOI = (
    "grant them the province", "please grant them tyrol, sire",
    "Talleyrand, grant the italian petition at once", "grant them tyrol",
    "grant tyrol to the kingdom of italy")


class TestR41AQuestionMadeOfTheGrammarNeverAnswers:
    @pytest.mark.parametrize("phrase", QUESTIONS_MADE_OF_THE_GRAMMAR)
    @pytest.mark.parametrize("route", ["typed", "button"])
    def test_it_logs_nothing_and_moves_no_state(self, board, phrase, route):
        """Verifier A, F1: `then shall we grant it` GRANTED (1 DP, 1800g
        forgone), `sire do we refuse` REFUSED at −10 / −20 — on both routes."""
        w, client, pet = _petition_current(board)
        before, desk = _swiss(w), _desk(w)
        r = (_cmd(client, phrase) if route == "typed"
             else _respond(client, phrase, pet["dialogue_id"]))
        assert not _logged(w) and _swiss(w) == before and _desk(w) == desk
        assert w.dialogue_manager.peek() is pet
        if route == "button":
            assert r.get("success") is False and r.get("message") == REPROMPT

    @pytest.mark.parametrize("phrase", QUESTIONS_AT_THE_PROVINCE_PETITION)
    @pytest.mark.parametrize("route", ["typed", "button"])
    def test_the_province_is_not_ceded(self, monkeypatch, phrase, route):
        """`then shall we grant tyrol` CEDED TYROL (France -> KingdomOfItaly)."""
        w, client, pet = _tyrol_board(monkeypatch)
        before, desk = _koi_state(w), _desk(w)
        r = (_cmd(client, phrase) if route == "typed"
             else _respond(client, phrase, pet["dialogue_id"]))
        assert not _logged(w) and _koi_state(w) == before and _desk(w) == desk
        assert w.regions["Tyrol"].controller == PLAYER
        if route == "button":
            assert r.get("success") is False and r.get("message") == REPROMPT

    @pytest.mark.parametrize("phrase,answer", STATEMENTS_THAT_STILL_ANSWER)
    def test_a_statement_still_answers_at_the_quoted_price(self, board, phrase, answer):
        w, client, pet = _petition_current(board)
        before = _swiss(w)
        r = _cmd(client, phrase)
        assert r.get("success") is True, r.get("message")
        assert _swiss(w) == answer(before)
        outcome = "granted" if answer is _granted else "refused"
        assert [e["outcome"] for e in _logged(w)] == [outcome] and not _petitions(w)

    def test_every_pinned_positive_keeps_its_action(self, board, monkeypatch):
        """The verifier's simulation, run against the REAL code: all 39."""
        w, _client = board
        swiss = _petition_of(w)
        for phrase in THE_39_POSITIVES_SWISS:
            assert DR.petition_plain_answer(swiss, phrase) is not None, phrase
        _w2, _c2, koi = _tyrol_board(monkeypatch)
        for phrase in THE_39_POSITIVES_KOI:
            assert DR.petition_plain_answer(koi, phrase) == "accept_ai_proposal", phrase
        assert len(THE_39_POSITIVES_SWISS) + len(THE_39_POSITIVES_KOI) == 39

    def test_they_is_not_a_word_of_the_grammar(self, board):
        """R4-1a: a line about what THEY do is not the Emperor's answer — and
        these two pass the statement-order rule, so only the allowlist stops
        them."""
        w, _client = board
        pet = _petition_of(w)
        for phrase in ("they refuse", "they accept the petition", "they grant it"):
            assert DR.petition_plain_answer(pet, phrase) is None, phrase
        assert DR.petition_plain_answer(pet, "we refuse") == "reject_ai_proposal"

    def test_the_auxiliaries_answer_in_statement_order_only(self, board, monkeypatch):
        """R4-1b on the function itself, with the question rule's inversion arm
        DOWN (R4-3's lever) — so only the token-order rule stands between these
        lines and the price. The third-person lines carry no inversion at all."""
        monkeypatch.setattr(DR, "A_QUESTION_NEVER_ANSWERS", False)
        w, _client = board
        pet = _petition_of(w)
        for phrase in QUESTIONS_MADE_OF_THE_GRAMMAR + (
                "today will the swiss accept", "then shall the swiss accept",
                "do the swiss refuse", "sire do please grant it"):
            assert DR.petition_plain_answer(pet, phrase) is None, phrase
        for phrase, action in (("we shall grant it", "accept_ai_proposal"),
                               ("i will refuse it", "reject_ai_proposal"),
                               ("do grant it", "accept_ai_proposal"),
                               ("please do refuse it", "reject_ai_proposal"),
                               ("i do accept", "accept_ai_proposal"),
                               ("grant it, we shall", "accept_ai_proposal")):
            assert DR.petition_plain_answer(pet, phrase) == action, phrase

    def test_the_petition_asks_the_one_question_test(self, board, monkeypatch):
        """R4-1c: the petition's question test IS `line_asks_a_question` — the
        inversion arm and all — not a private copy that can drift."""
        w, _client = board
        pet = _petition_of(w)
        asked = []
        real = DR.line_asks_a_question
        monkeypatch.setattr(DR, "line_asks_a_question",
                            lambda typed, options: asked.append(typed) or real(typed, options))
        assert DR.petition_plain_answer(pet, "grant the petition") == "accept_ai_proposal"
        assert asked == ["grant the petition"]
        monkeypatch.setattr(DR, "line_asks_a_question", lambda typed, options: True)
        assert DR.petition_plain_answer(pet, "grant the petition") is None

    def test_lever_down_the_pass_1_router_is_back(self, board, monkeypatch):
        """Same lever, no new one: with `A_PETITION_IS_ANSWERED_PLAINLY` down the
        verifier's `do the swiss accept` GRANTS again, as it measured."""
        monkeypatch.setattr(DR, "A_PETITION_IS_ANSWERED_PLAINLY", False)
        w, client, pet = _petition_current(board)
        before = _swiss(w)
        r = _cmd(client, "do the swiss accept")
        assert r.get("success") is True and _swiss(w) == _granted(before)


# ═══════════════════════════════════════════════════════════════════════════
# R4-2 (verifier A F2 = verifier B F1) — a question-shaped LABEL still resolves
# ═══════════════════════════════════════════════════════════════════════════

def _advisory_mounted(monkeypatch, opener):
    """A Talleyrand advisory CURRENT on the fresh 1805 board, the desk cleared
    first — the verifiers' geometry."""
    w = _europe()
    client = _swap(monkeypatch, w)
    _cmd(client, "status")
    _clear_slot(w)
    _cmd(client, opener)
    top = w.dialogue_manager.peek()
    assert top is not None and top.get("type") == "advisory", top
    return w, client, top


def _bare_label_mounted(monkeypatch):
    """The third shipped question label, `What should we do?`, mounted by its
    own producer exactly as `_execute_diplomatic_advisory` mounts it."""
    from backend.game_logic.diplomatic_advisory import generate_advisory
    w = _europe()
    client = _swap(monkeypatch, w)
    _cmd(client, "status")
    _clear_slot(w)
    with _quiet():
        dialogue = generate_advisory("Prussia", "recommend_action", w)
    w.dialogue_manager.preempt(dialogue)
    top = w.dialogue_manager.peek()
    assert [o["label"] for o in top["options"]] == ["What should we do?", "Thank you"]
    return w, client, top


PRUSSIA_OPENER = "Talleyrand, how do we stand with Prussia"
AUSTRIA_OPENER = "Talleyrand, what about Austria"
LETTER_OPTIONS = [{"label": "Accept", "action": "accept_ai_proposal"},
                  {"label": "Reject", "action": "reject_ai_proposal"},
                  {"label": "Counter-offer", "action": "counter_ai_proposal"}]


class TestR42AQuestionShapedLabelStillResolves:
    @pytest.mark.parametrize("opener,label,phrase", [
        (PRUSSIA_OPENER, "What should we do about Prussia?", "What should we do about Prussia"),
        (PRUSSIA_OPENER, "What should we do about Prussia?", "what should we do about prussia"),
        (PRUSSIA_OPENER, "What should we do about Prussia?", "so what should we do about prussia?"),
        (AUSTRIA_OPENER, "What terms would they accept?", "what terms would they accept"),
        (AUSTRIA_OPENER, "What terms would they accept?", "well, what terms would they accept?"),
    ])
    @pytest.mark.parametrize("route", ["typed", "button"])
    def test_the_advisorys_own_label_expands(self, monkeypatch, opener, label, phrase, route):
        """Measured, lever UP: the typed road answered with the COMMAND
        REFERENCE, the button route with "A question is not an answer… 1=What
        should we do about Prussia?" — re-prompting the label it had refused."""
        w, client, top = _advisory_mounted(monkeypatch, opener)
        assert top["options"][0]["label"] == label
        r = (_cmd(client, phrase) if route == "typed"
             else _respond(client, phrase, top["dialogue_id"]))
        assert r.get("success") is True, r.get("message")
        assert "COMMAND REFERENCE" not in str(r.get("message"))
        now = w.dialogue_manager.peek()
        assert now is not top and now.get("type") == "proposal_options"

    @pytest.mark.parametrize("phrase,route", [
        ("what should we do", "typed"), ("so, what should we do?", "typed"),
        ("What should we do", "button"), ("well, what should we do?", "button")])
    def test_the_third_shipped_label(self, monkeypatch, phrase, route):
        w, client, top = _bare_label_mounted(monkeypatch)
        r = (_cmd(client, phrase) if route == "typed"
             else _respond(client, phrase, top["dialogue_id"]))
        assert r.get("success") is True, r.get("message")
        assert w.dialogue_manager.peek().get("type") == "proposal_options"

    def test_a_lead_in_on_the_typed_road(self, monkeypatch):
        """…and the form the diplomat route used to read as a NEW question:
        lever UP it mounted a SECOND advisory over the first."""
        w, client, top = _advisory_mounted(monkeypatch, PRUSSIA_OPENER)
        r = _cmd(client, "what should we do about prussia then")
        assert r.get("success") is True
        assert w.dialogue_manager.peek().get("type") == "proposal_options"
        assert len(list(w.dialogue_manager.iter_queue())) == 0

    def test_a_plain_label_is_not_exempted(self):
        """`accept?` is not the label `Accept`: the six pinned QUESTIONS of R3-9
        still claim nothing (through the endpoints they are pinned above)."""
        letter = {"type": "incoming_proposal", "target_nation": "Portugal",
                  "context": {"proposal_type": "open_borders"}, "options": LETTER_OPTIONS}
        for phrase in QUESTIONS:
            assert DR.line_asks_a_question(phrase, LETTER_OPTIONS) is True, phrase
            assert DR.match_dialogue_answer(letter, phrase) is None, phrase
        assert DR.choice_is_an_exact_token("accept?", LETTER_OPTIONS) is False
        assert DR.choice_is_an_exact_token("Accept.", LETTER_OPTIONS) is True
        assert DR.choice_is_an_exact_token("ACCEPT!", LETTER_OPTIONS) is True

    def test_the_label_is_compared_modulo_its_terminal_punctuation(self):
        advisory = [{"label": "What should we do about Prussia?", "action": "expand_to_proposal"},
                    {"label": "Thank you", "action": "dismiss"}]
        dialogue = {"type": "advisory", "context": {}, "options": advisory}
        for token in ("What should we do about Prussia", "what should we do about prussia",
                      "what should we do about prussia?!", "What should we do about Prussia."):
            assert DR.choice_is_an_exact_token(token, advisory) is True, token
            assert DR.free_text_of_choice(dialogue, token) is None, token
        # a lead-in is NOT an exact token (it is free text) — but it is that label
        assert DR.choice_is_an_exact_token("so what should we do about prussia?", advisory) is False
        assert DR.line_asks_a_question("so what should we do about prussia?", advisory) is False
        # …and a DIFFERENT question at the same advisory is still a question
        assert DR.line_asks_a_question("what should we do about austria?", advisory) is True
        assert DR.line_asks_a_question("should we thank you?", advisory) is True
        assert DR.match_dialogue_answer(dialogue, "should we thank you?") is None


# ═══════════════════════════════════════════════════════════════════════════
# R4-3 (verifier A, F3 — pre-existing, every family) — an inversion anywhere
# ═══════════════════════════════════════════════════════════════════════════

def _war_pairs(w):
    return sum(1 for state in w.diplomatic_states.values() if str(state).endswith("WAR"))


def _settlement_confirm_staged(board):
    """Britain's white peace accepted through its own endpoint: the staged
    `settlement_confirm` — a HARD STOP — is current."""
    w, client = board
    offer = _pending(w)[0]
    assert offer["type"] == "incoming_settlement_offer"
    r = _respond(client, "accept_settlement_offer", offer["dialogue_id"])
    assert r.get("success") is True, r.get("message")
    stop = w.dialogue_manager.peek()
    assert stop["type"] == "settlement_confirm" and w.dialogue_manager.is_hard_stop()
    return w, client, stop


def _ultimatum_current(monkeypatch):
    w = _europe()
    client = _swap(monkeypatch, w)
    _cmd(client, "status")
    _clear_slot(w)
    ult = _deliver(w, {
        "source": "Prussia", "recipient": PLAYER, "proposal_type": "ultimatum", "priority": 1,
        "terms": {"type": "ultimatum", "proposer_nation": "Prussia", "target_nation": PLAYER,
                  "demands": [{"type": "territory", "regions": ["Hanover"]}],
                  "sweeteners": [], "clauses": ["ultimatum"]},
        "talleyrand_assessment": "", "decision_reason": "agenda_pursuit", "turn_generated": 1})
    assert ult.get("type") == "incoming_ultimatum" and w.dialogue_manager.peek() is ult
    return w, client, ult


INVERTED_AT_THE_LETTER = ("then shall we accept", "sire do we accept", "talleyrand shall we accept",
                          "very well, do we accept it", "well then do we reject it")


class TestR43AnInversionAnywhereIsAQuestion:
    @pytest.mark.parametrize("phrase", ["then shall we ratify", "sire do we confirm",
                                        "so then should we ratify"])
    def test_a_hard_stop_ratifies_nothing(self, board, phrase):
        """`then shall we ratify` RATIFIED the seven-pair settlement."""
        w, client, stop = _settlement_confirm_staged(board)
        wars = _war_pairs(w)
        assert wars > 0
        r = _cmd(client, phrase)
        assert r.get("success") is False
        assert str(r.get("message")).startswith("The terms on the table awaits your answer")
        assert w.dialogue_manager.peek() is stop and _war_pairs(w) == wars

    @pytest.mark.parametrize("phrase", ["ratify", "we shall ratify"])
    def test_the_hard_stop_still_answers_to_a_statement(self, board, phrase):
        w, client, stop = _settlement_confirm_staged(board)
        wars = _war_pairs(w)
        r = _cmd(client, phrase)
        assert r.get("success") is True, r.get("message")
        assert str(r.get("message")).startswith("Settlement Ratified")
        assert _war_pairs(w) < wars and w.dialogue_manager.peek() is not stop

    @pytest.mark.parametrize("phrase", INVERTED_AT_THE_LETTER)
    @pytest.mark.parametrize("route", ["typed", "button"])
    def test_portugals_treaty_is_not_signed(self, board, phrase, route):
        """`sire do we accept` SIGNED PEACE → OPEN_BORDERS on both routes."""
        w, client, top = _portugal_on_top(board)
        r = (_cmd(client, phrase) if route == "typed"
             else _respond(client, phrase, top["dialogue_id"]))
        assert _state_with(w, "Portugal") == "PEACE" and top in _pending(w)
        assert "You have" not in str(r.get("message"))
        if route == "button":
            assert r.get("success") is False
            assert str(r.get("message")).startswith("A question is not an answer, Sire")

    @pytest.mark.parametrize("phrase", ["we shall accept", "i will accept", "we do accept"])
    def test_a_statement_still_signs(self, board, phrase):
        w, client, top = _portugal_on_top(board)
        r = _cmd(client, phrase)
        assert r.get("success") is True, r.get("message")
        assert _state_with(w, "Portugal") == "OPEN_BORDERS"

    @pytest.mark.parametrize("phrase", ["then shall we yield", "so then do we yield",
                                        "sire do we defy"])
    def test_an_ultimatum_is_neither_yielded_nor_defied(self, monkeypatch, phrase):
        w, client, ult = _ultimatum_current(monkeypatch)
        r = _cmd(client, phrase)
        assert w.dialogue_manager.peek() is ult
        assert not dict(w.ultimatum_rejection_pressure or {})
        assert "You have" not in str(r.get("message"))

    def test_lever_down_the_inversion_signs_as_it_always_did(self, board, monkeypatch):
        """Pre-existing, and behind the existing lever: False = the prior router."""
        monkeypatch.setattr(DR, "A_QUESTION_NEVER_ANSWERS", False)
        w, client, top = _portugal_on_top(board)
        assert DR.line_asks_a_question("then shall we accept", LETTER_OPTIONS) is False
        r = _cmd(client, "then shall we accept")
        assert r.get("success") is True and _state_with(w, "Portugal") == "OPEN_BORDERS"

    def test_the_rule_reads_whole_words_and_statement_order(self):
        from backend.ai.clause_guards import is_question
        for phrase in ("then shall we accept", "sire do we accept", "accept it, shall we",
                       "today would i accept", "well then can we reject it", "and must i yield"):
            assert DR.line_asks_a_question(phrase, LETTER_OPTIONS) is True, phrase
            assert not is_question(phrase), phrase             # the inversion arm's alone
        # …and `is_question` still carries the leads that are no inversion at all
        for phrase in ("what if we accept", "how about we accept", "are we to accept"):
            assert DR.line_asks_a_question(phrase, LETTER_OPTIONS) is True, phrase
            assert DR._SUBJECT_AUXILIARY_INVERSION_RE.search(phrase) is None, phrase
        for phrase in ("we shall accept", "i will accept", "we do accept", "accept",
                       "as you will, we accept", "window accept", "undo it, accept"):
            assert DR.line_asks_a_question(phrase, LETTER_OPTIONS) is False, phrase


# ═══════════════════════════════════════════════════════════════════════════
# R4-4 (verifier B, F2 — pre-existing residue of R3-2) — two more shapes
# ═══════════════════════════════════════════════════════════════════════════

STRAY_ADDRESS_LINES = ("hmm, grant it", "oui, grant it", "switzerland, granted",
                       "hmm, should i grant it?")
DIPLOMAT_REFUSALS = ("Talleyrand, no", "envoy, tell them no", "Talleyrand, tell them no",
                     "minister, not today")
PEACE_ORDER = "Talleyrand, propose peace to Austria and accept their terms"


class TestR44TwoMoreShapesRepromptInPlace:
    @pytest.mark.parametrize("phrase", STRAY_ADDRESS_LINES + DIPLOMAT_REFUSALS)
    def test_the_line_is_reprompted_and_refuse_then_answers(self, board, phrase):
        """Measured: `hmm, grant it` mounted "There is no Marshal 'hmm'…" OVER
        the petition; `Talleyrand, no` mounted the nation picker over it, and
        the `2` the re-prompt teaches as Refuse then chose BAVARIA."""
        w, client, pet = _petition_current(board)
        before, desk, history = _swiss(w), _desk(w), len(w.command_history)
        r = _cmd(client, phrase)
        assert r.get("success") is False and r.get("petition_reprompt") is True
        assert r.get("message") == REPROMPT
        assert w.dialogue_manager.peek() is pet and _desk(w) == desk
        assert len(w.command_history) == history
        assert not _logged(w) and _swiss(w) == before
        r = _cmd(client, "refuse")
        assert r.get("success") is True and not r.get("matter_mismatch"), r.get("message")
        assert _swiss(w) == _refused(before) and not _petitions(w)

    def test_a_line_that_names_a_marshal_keeps_the_ordinary_road(self, board):
        w, client, pet = _petition_current(board)
        history = len(w.command_history)
        r = _cmd(client, "Ney, accept - attack Mack")
        assert not r.get("petition_reprompt")
        assert len(w.command_history) == history + 1
        assert w.dialogue_manager.peek() is pet and not _logged(w)

    def test_a_stray_address_with_no_answer_is_not_the_petitions(self, board):
        """Shape (d) needs an ANSWER after the comma — `hmm, march to Swabia`
        is an order with a stray address, and keeps the ordinary road."""
        w, client, pet = _petition_current(board)
        roster = [m.name for m in w.get_player_marshals()]
        assert DR.petition_line_reprompt(pet, "hmm, march to Swabia", roster, world=w) is None
        assert DR.petition_line_reprompt(pet, "hmm, grant it", roster, world=w)["message"] == REPROMPT
        assert DR.petition_line_reprompt(pet, "hmm, granted", roster, world=w)["message"] == REPROMPT
        assert DR.petition_line_reprompt(pet, "Ney, grant it", roster, world=w) is None
        r = _cmd(client, "hmm, march to Swabia")
        assert not r.get("petition_reprompt")

    def test_the_players_own_order_about_another_court_reaches_the_proposal_road(self, board):
        """The NARROWING of shape (c), measured and pinned as it lands: pass 3
        re-prompted this line; it now reaches the proposal road — a
        `proposal_confirm` for Austria is mounted, the petition waits behind it
        unanswered, and the order is recorded as the order it is."""
        w, client, pet = _petition_current(board)
        before, history = _swiss(w), len(w.command_history)
        r = _cmd(client, PEACE_ORDER)
        assert r.get("success") is True and not r.get("petition_reprompt"), r.get("message")
        top = w.dialogue_manager.peek()
        assert top.get("type") == "proposal_confirm" and DR.dialogue_court(top) == "Austria"
        assert pet in list(w.dialogue_manager.iter_queue())
        assert not _logged(w) and _swiss(w) == before
        assert len(w.command_history) == history + 1

    def test_the_narrowing_is_the_other_court_and_the_shape(self, board):
        w, _client, pet = _petition_current(board)
        roster = [m.name for m in w.get_player_marshals()]

        def reprompted(line, world=w):
            return DR.petition_line_reprompt(pet, line, roster, world=world) is not None

        assert not reprompted(PEACE_ORDER)
        assert not reprompted("Talleyrand, propose open borders to Prussia and accept no counter")
        assert reprompted(PEACE_ORDER, world=None)               # no world, no narrowing
        # no OTHER court named -> still the petition's (pass 3's recorded trade)
        assert reprompted("Talleyrand, propose an alliance and accept nothing less")
        # the petition's OWN court named -> still the petition's
        assert reprompted("Talleyrand, tell the swiss yes, later")
        # a refusal that names another court is an order about THAT court
        assert reprompted("Talleyrand, tell them no")
        assert not reprompted("Talleyrand, tell austria's envoy no")

    def test_lever_down_the_shapes_are_gone(self, board, monkeypatch):
        w, _client, pet = _petition_current(board)
        roster = [m.name for m in w.get_player_marshals()]
        monkeypatch.setattr(DR, "A_PETITION_IS_ANSWERED_PLAINLY", False)
        for phrase in STRAY_ADDRESS_LINES + DIPLOMAT_REFUSALS:
            assert DR.petition_line_reprompt(pet, phrase, roster, world=w) is None, phrase


# ═══════════════════════════════════════════════════════════════════════════
# R4-5 (verifier B, F3 — R7) — no raw tag, no missing article, in a vassal verb
# ═══════════════════════════════════════════════════════════════════════════

KOI_THE = "the Kingdom of Italy"
KOI_THE_CAP = "The Kingdom of Italy"
THE_TYPED_VASSAL_ROAD = (
    ("invest in kingdom of italy", True, f"Invested in {KOI_THE}: +10 loyalty (70 → 80)."),
    ("invest in kingdom of italy", False, f"Investment in {KOI_THE} on cooldown (3 turns remaining)."),
    ("grant the kingdom of italy more autonomy", True,
     f"{KOI_THE_CAP} autonomy changed: Satellite → Autonomous."),
    ("grant the kingdom of italy more autonomy", False,
     f"{KOI_THE_CAP} is already at maximum autonomy."),
    ("reduce the kingdom of italy's autonomy", True,
     f"{KOI_THE_CAP} autonomy changed: Autonomous → Satellite."),
    ("give the kingdom of italy less autonomy", True,
     f"{KOI_THE_CAP} autonomy changed: Satellite → Puppet."),
    ("give the kingdom of italy less autonomy", False,
     f"{KOI_THE_CAP} is already at minimum autonomy."),
    ("cede tyrol to the kingdom of italy", True, f"Tyrol is ceded to {KOI_THE}."),
    ("cede tyrol to the kingdom of italy", False, f"A grant to {KOI_THE} is still being settled"),
    ("cede to the kingdom of italy", False, f"No province is eligible to cede to {KOI_THE} —"),
    ("release kingdom of italy", True,
     f"{KOI_THE_CAP} is released from vassalage and stands a free court again."),
    ("release kingdom of italy", False, f"{KOI_THE_CAP} is not a vassal."),
    ("invest in kingdom of italy", False, f"{KOI_THE_CAP} is not a vassal."),
    ("grant the kingdom of italy more autonomy", False, f"{KOI_THE_CAP} is not a vassal."),
    ("cede tyrol to the kingdom of italy", False, f"{KOI_THE_CAP} is not a vassal."),
)
# The census' allow-list: every dict literal in the two files whose "message"
# interpolates a bare nation-tag variable — and is NOT the returned result of a
# typed vassal verb. function -> the reason it is not R4-5's.
EVENT_ROW_SITES = {
    "attempt_vassal_courting": "event row; its only reader is turn_manager's debug_print "
                               "(dispatch + campaign log compose their own sentence)",
    "attempt_vassal_bribe": "event row; debug_print sink — the defection's notice, dispatch "
                            "and log lines are composed inside the function through display_nation",
    "get_vassal_warnings": "no caller: the Vassals card builds its own warning band",
    "process_vassal_loyalty": "turn-tick event ROW appended to the end-turn list, never a "
                              "verb's returned result (rendered through the client's "
                              "humanize_nation_keys_in_text chokepoint) — routed, not R4-5's",
    "check_vassal_rebellion": "turn-tick event ROW, as above — routed, not R4-5's",
    "check_defection_cascade": "turn-tick event ROW, as above — routed, not R4-5's",
}
_TAG_VARIABLES = {"vassal_name", "target", "vassal"}


def _bare_tag_message_sites():
    """(file, function, line) of every dict literal whose "message" value
    interpolates a bare `{vassal_name}` / `{target}` / `{vassal}`."""
    import ast
    sites = []
    for path in (REPO / "backend" / "game_logic" / "vassal.py",
                 REPO / "backend" / "commands" / "vassal_executor.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        owner = {}
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for sub in ast.walk(fn):
                    owner.setdefault(id(sub), fn.name)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            for key, value in zip(node.keys, node.values):
                if not (isinstance(key, ast.Constant) and key.value == "message"):
                    continue
                if any(isinstance(sub, ast.FormattedValue) and isinstance(sub.value, ast.Name)
                       and sub.value.id in _TAG_VARIABLES for sub in ast.walk(value)):
                    sites.append((path.name, owner.get(id(node)), value.lineno))
    return sites


class TestR45NoRawTagInAVassalSentence:
    def test_the_typed_road_on_the_kingdom_of_italy(self, monkeypatch):
        """invest / autonomy up / autonomy down / cede / release / a second
        release — measured: "Invested in KingdomOfItaly…", "KingdomOfItaly
        autonomy changed…", "KingdomOfItaly is already at maximum autonomy.",
        "KingdomOfItaly is not a vassal.", "Kingdom of Italy is released…"."""
        w = _europe()
        _stage_tyrol_for_koi(w)
        w.vassals[KOI]["loyalty"] = 70
        client = _swap(monkeypatch, w)
        _cmd(client, "status")
        _clear_slot(w)
        w.diplomatic_points = 20
        for line, success, expected in THE_TYPED_VASSAL_ROAD:
            r = _cmd(client, line)
            message = str(r.get("message"))
            assert r.get("success") is success, (line, message)
            assert KOI not in message, (line, message)
            assert expected in message, (line, message)
        assert KOI not in w.vassals and w.regions["Tyrol"].controller == KOI

    def test_a_court_without_an_article_reads_as_it_always_did(self, monkeypatch):
        w = _europe()
        w.vassals["Holland"]["loyalty"] = 70
        client = _swap(monkeypatch, w)
        _cmd(client, "status")
        _clear_slot(w)
        r = _cmd(client, "invest in Holland")
        assert str(r.get("message")).startswith("Invested in Holland: +10 loyalty (70 → 80).")
        r = _cmd(client, "grant Holland more autonomy")
        assert str(r.get("message")).startswith("Holland autonomy changed: Satellite → Autonomous.")

    def test_the_verbs_no_typed_line_reaches(self):
        w = _europe()
        assert V.transfer_vassal(w, KOI, PLAYER)["message"] == f"{KOI_THE_CAP} already serves France."
        assert V.transfer_vassal(w, "PapalStates", "Prussia")["message"] == (
            "The Papal States is not a vassal.")
        assert V.release_vassal(w, "PapalStates")["message"] == "The Papal States is not a vassal."
        assert V.change_vassal_autonomy(w, KOI, 1)["message"] == f"{KOI_THE_CAP} is already Satellite."
        assert V.invest_in_vassal(w, KOI, actor="Prussia")["message"] == (
            f"Cannot invest in {KOI_THE}: not your vassal.")
        assert V.change_vassal_autonomy(w, KOI, 2, actor="Prussia")["message"] == (
            f"Cannot change {KOI_THE}'s autonomy: not your vassal.")
        w.vassals[KOI]["loyalty"] = 100
        assert V.invest_in_vassal(w, KOI)["message"].startswith(
            f"{KOI_THE_CAP}'s loyalty is already full")
        assert V.create_vassal_conquest(w, PLAYER, "PapalStates")["message"] == (
            "Cannot conquer the Papal States: must be at WAR (current: PEACE).")
        assert V.create_vassal_conquest(w, PLAYER, KOI)["message"] == (
            f"{KOI_THE_CAP} is already a vassal of France.")
        with _quiet():
            moved = V.transfer_vassal(w, KOI, "Prussia")["message"]
        assert moved == (f"{KOI_THE_CAP} passes from France's suzerainty to Prussia's "
                         f"(loyalty resets to {V.TRANSFER_LOYALTY_RESET}).")

    def test_the_court_guards_tail_carries_the_article(self, board):
        """Newly reachable through R3-3: `grant the kingdom of italy's petition`
        with Switzerland's petition current — "Nothing from Kingdom of Italy"."""
        w, client, pet = _petition_current(board)
        r = _cmd(client, "grant the kingdom of italy's petition")
        assert r.get("court_mismatch") is True
        assert r.get("message") == (
            f"{SWISS_HEAD} Nothing from {KOI_THE} is before you; answer Switzerland first, "
            f"or set this matter aside.")
        assert w.dialogue_manager.peek() is pet and not _logged(w)

    def test_the_source_census(self):
        """No f-string in vassal.py / vassal_executor.py interpolates a bare
        `{vassal_name}` / `{target}` / `{vassal}` into a `message` — outside the
        event-row sites, each allow-listed with its reason."""
        sites = _bare_tag_message_sites()
        offenders = [s for s in sites if s[1] not in EVENT_ROW_SITES]
        assert offenders == [], offenders
        assert {s[1] for s in sites} == set(EVENT_ROW_SITES)       # no stale allow-list row
        assert all(name == "vassal.py" for name, _fn, _line in sites)
        assert all(str(reason).strip() for reason in EVENT_ROW_SITES.values())

    def test_the_mock_parser_reads_a_court_with_its_article(self, monkeypatch):
        """FLIPPED the same day it was written (September 18, 2026). Pass 4
        pinned the gap as CURRENT behaviour because `backend/ai/*` was not the
        builder's to touch: `invest in the kingdom of italy` / `release the
        kingdom of italy` (WITH the article) got Berthier's shrug while the
        article-less forms executed. The lead closed it in the mock keyword
        chain (`f"invest in the {n}"` / `f"release the {n}"`), so the form the
        game's own copy now prints ("the Kingdom of Italy") is the form the
        player may type."""
        w = _europe()
        w.vassals[KOI]["loyalty"] = 70
        client = _swap(monkeypatch, w)
        _cmd(client, "status")
        _clear_slot(w)
        r = _cmd(client, "invest in the kingdom of italy")
        assert "Berthier" not in str(r.get("message")), r.get("message")
        assert r.get("success") is True and w.vassals[KOI]["loyalty"] > 70, r.get("message")
        assert "KingdomOfItaly" not in str(r.get("message"))
        r = _cmd(client, "release the kingdom of italy")
        assert "Berthier" not in str(r.get("message")), r.get("message")
        assert r.get("success") is True and KOI not in w.vassals, r.get("message")
