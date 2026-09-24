"""Row EP, slice F6 — "Settled once, reopened" (`docs/ENDGAME_PLAN.md` §1 F6,
`BUG_FIXES.md` LV-17).

The live review read, one turn apart and in this order: "Davout fought like
a man with something to prove — and proved it. His grievance is settled."
and then "Marshal Davout seeks an audience … the quarrel may harden
further." Both were true of DIFFERENT grievances: the battle resolved the
first by action (pipeline step 9.5), and the end-of-turn pass — whose
same-pass suppression set remembers only the coolings IT performed —
re-fired the same pair off the rival's fresh laurels. The trigger is legal
and untouched (it feeds `jealous_of`, which M7 and `BASELINE_SERIES` read
through combat). What was missing was the card SAYING so.

Two rules, one lever (`jealousy.THE_REOPENED_QUARREL_SAYS_SO`):

* a confrontation card built within a turn of a by-action settlement of the
  same pair opens with "Settled once at <where> — and reopened by <rival>'s
  laurels since." — `where` read off the `jealousy_resolved` event's own
  `location`, which the battle-time resolver now stamps;
* a card for that pair still STANDING undelivered from before the settlement
  is stale in its body, so the re-fire REPLACES it (the latch had blocked the
  fresh card and handed the stale one over).

A card whose grievance no longer stands at all is still retired at delivery
(FA-S17-D4) — that half predates F6. The reproduction is DRIVEN through
`/command`: the review's own shape (Archduke John beaten twice; a cautious
colleague vindicated "shoulder to shoulder").
"""

import contextlib
import io
import random

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.game_logic import jealousy as J
from tests import _chip_census as C

REPO = C.REPO


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


def _cmd(client, text):
    with _quiet():
        r = client.post("/command", json={"command": text})
    assert r.status_code == 200, (text, r.status_code, r.text[:300])
    return r.json()


def _events(world, kind, marshal, target):
    return [e for e in world.event_log
            if e.get("type") == kind and e.get("marshal") == marshal and e.get("target") == target]


def _stage(monkeypatch):
    """Turn 5 of the review, staged: Davout resents Ney (a card already
    queued for it), Davout stands WITH Ney, and Archduke John is a remnant
    on Austrian Tyrol with every other Austrian corps at Vienna — so
    Davout's attack from Munich, Ney reinforcing beside him, is the shared
    victory that resolves the grievance by action. (The other way round
    never resolves: a cautious man with a live grievance WITHHOLDS from his
    rival's battle — the jealousy v3.2 cautious expression — so he is not on
    Ney's winning side.)"""
    C.board_env(monkeypatch)
    world = M.world
    client = TestClient(M.app)
    ney = world.marshals["Ney"]
    davout = world.marshals["Davout"]
    # Munich: Bavarian (allied) soil one march from Tyrol, empty at boot.
    ney.location = "Munich"
    davout.location = "Munich"
    ney.strategic_order = None
    davout.strategic_order = None
    # Ney answers the guns for certain: devoted to Davout for the staging
    # (+20 on the arrival score; the roll's variance cannot reach the
    # threshold from there), so the resolution is the RULE, not a die.
    ney.set_relationship("Davout", 2)
    world.marshals["ArchdukeJohn"].strength = 600
    for m in world.marshals.values():
        if m.nation == "Austria" and m.name != "ArchdukeJohn":
            m.location = "Vienna"
            m.strategic_order = None
    # The grievance, and the card the pass would have queued for it.
    J.apply_jealousy(world, davout, ney, delta=2, threshold=1, events=[])
    assert davout.jealous_of == "Ney"
    stale = world.pending_marshal_petition
    assert stale and stale.get("kind") == "jealousy_confrontation", stale
    assert not str(stale.get("body", "")).startswith("Settled once")
    return world, client, stale


class TestTheBattleSettlesAndSaysWhere:

    def test_the_shared_victory_settles_the_quarrel_and_stamps_the_field(self, monkeypatch):
        world, client, _stale = _stage(monkeypatch)
        davout = world.marshals["Davout"]
        random.seed(11)
        r = _cmd(client, "Davout, attack Archduke John")
        assert r.get("battle_report"), r.get("message")
        assert davout.jealous_of is None, "the shoulder-to-shoulder victory resolves it"
        note = str((r.get("battle_report") or {}).get("jealousy_note") or "")
        assert "Davout fought like a man with something to prove — and proved it. His grievance is settled." in note, note
        resolved = _events(world, "jealousy_resolved", "Davout", "Ney")
        assert resolved and resolved[-1]["by_action"] is True, resolved
        assert resolved[-1]["location"] == "Tyrol", resolved[-1]


class TestTheReopenedCardSaysSo:

    def test_the_next_rung_opens_with_settled_once(self, monkeypatch):
        """The ladder's next rung, the turn the field settled it: the fresh
        card replaces the stale one and its first sentence says so."""
        world, client, stale = _stage(monkeypatch)
        ney = world.marshals["Ney"]
        davout = world.marshals["Davout"]
        random.seed(11)
        _cmd(client, "Davout, attack Archduke John")
        assert davout.jealous_of is None
        # The re-fire the end-of-turn pass performs off the rival's laurels.
        J.apply_jealousy(world, davout, ney, delta=2, threshold=1, events=[])
        card = world.pending_marshal_petition
        assert card is not None and card is not stale, "the stale card was handed over"
        assert str(card["body"]).startswith(
            "Settled once at Tyrol — and reopened by Ney's laurels since."), card["body"]
        assert card["context"]["marshal"] == "Davout" and card["context"]["target"] == "Ney"

    def test_the_two_lines_cannot_contradict_on_consecutive_turns(self, monkeypatch):
        """Driven end to end: the report says settled; whatever the pass
        delivers next turn about the same pair says reopened — or nothing."""
        world, client, stale = _stage(monkeypatch)
        davout = world.marshals["Davout"]
        random.seed(11)
        r = _cmd(client, "Davout, attack Archduke John")
        assert "His grievance is settled." in str(r["battle_report"].get("jealousy_note") or "")
        r2 = _cmd(client, "end turn")
        delivered = r2.get("deferred_marshal_petition") or r2.get("marshal_petition")
        refired = _events(world, "jealousy_fired", "Davout", "Ney")
        refired_now = [e for e in refired if int(e.get("turn", -1)) >= int(world.current_turn) - 1]
        if delivered and delivered.get("kind") == "jealousy_confrontation" \
                and delivered.get("context", {}).get("marshal") == "Davout":
            assert refired_now, "a Davout card with no re-fire is the stale card"
            assert str(delivered["body"]).startswith("Settled once at Tyrol — and reopened by"), delivered["body"]
        else:
            # Nothing about the pair reached the player — the stale card was
            # retired at delivery (FA-S17-D4) or replaced and not yet due.
            assert davout.jealous_of is None or refired_now

    def test_a_card_for_another_pair_is_not_replaced(self, monkeypatch):
        world, client, _stale = _stage(monkeypatch)
        murat = world.marshals["Murat"]
        ney = world.marshals["Ney"]
        davout = world.marshals["Davout"]
        random.seed(11)
        _cmd(client, "Davout, attack Archduke John")
        # A different pair's card takes the slot; Davout's re-fire must not evict it.
        world.pending_marshal_petition = None
        J.apply_jealousy(world, murat, ney, delta=2, threshold=1, events=[])
        other = world.pending_marshal_petition
        assert other and other["context"]["marshal"] == "Murat"
        J.apply_jealousy(world, davout, ney, delta=2, threshold=1, events=[])
        assert world.pending_marshal_petition is other

    def test_the_clause_needs_a_settlement_within_a_turn(self, monkeypatch):
        world, _client, _stale = _stage(monkeypatch)
        ney = world.marshals["Ney"]
        davout = world.marshals["Davout"]
        # No by-action settlement on the log: no clause.
        assert J.settled_once_clause(world, davout, ney) == ""
        # A settlement three turns ago is old news.
        world.current_turn += 3
        world.log_event({"type": "jealousy_resolved", "marshal": "Davout", "target": "Ney",
                         "by_action": True, "location": "Tyrol"})
        world.event_log[-1]["turn"] = int(world.current_turn) - 3
        assert J.settled_once_clause(world, davout, ney) == ""
        world.event_log[-1]["turn"] = int(world.current_turn) - 1
        assert J.settled_once_clause(world, davout, ney) == \
            "Settled once at Tyrol — and reopened by Ney's laurels since."

    def test_a_timer_expiry_is_not_a_settlement(self, monkeypatch):
        world, _client, _stale = _stage(monkeypatch)
        ney = world.marshals["Ney"]
        davout = world.marshals["Davout"]
        J.clear_jealousy(world, davout, resolved_by_action=False, events=[], reason="time")
        assert J.settled_once_clause(world, davout, ney) == ""

    def test_without_a_field_the_clause_still_reads(self, monkeypatch):
        world, _client, _stale = _stage(monkeypatch)
        ney = world.marshals["Ney"]
        davout = world.marshals["Davout"]
        J.clear_jealousy(world, davout, resolved_by_action=True, events=[],
                         reason="he has surpassed Ney in glory")
        assert J.settled_once_clause(world, davout, ney) == \
            "Settled once — and reopened by Ney's laurels since."

    def test_the_lever_down_is_the_old_channel(self, monkeypatch):
        monkeypatch.setattr(J, "THE_REOPENED_QUARREL_SAYS_SO", False)
        world, client, stale = _stage(monkeypatch)
        ney = world.marshals["Ney"]
        davout = world.marshals["Davout"]
        random.seed(11)
        _cmd(client, "Davout, attack Archduke John")
        J.apply_jealousy(world, davout, ney, delta=2, threshold=1, events=[])
        # The latch blocks the fresh card; the stale one stands, clause-less.
        assert world.pending_marshal_petition is stale
        assert not str(stale["body"]).startswith("Settled once")


class TestTheSeriesIsUntouched:

    def test_the_resolution_seam_carries_the_region_without_moving_the_trigger(self):
        """Display and delivery only: the trigger, the timer and the latch
        keys are untouched, so `BASELINE_SERIES` and M7 cannot move (the
        series pin file runs the shipped tree)."""
        src = (REPO / "backend" / "game_logic" / "jealousy.py").read_text(encoding="utf-8")
        assert "JEALOUSY_SUPPRESS_SAME_PASS_REFIRE" in src
        assert "def settled_once_clause" in src and "def _retire_pending_petition" in src

    def test_every_resolution_call_site_names_the_field(self):
        """An AST census, not a string: every call of
        `check_battle_resolution` in the backend passes `battle_region`
        (three seams — the pipeline, `_execute_attack`, the reckless
        charge in `world_state`). The first cut patched one and the driven
        test read an empty field off the other."""
        import ast
        calls = []
        for path in (REPO / "backend").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    fn = node.func
                    name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
                    if name == "check_battle_resolution":
                        calls.append((path.name, node.lineno,
                                      {k.arg for k in node.keywords}))
        assert len(calls) >= 3, calls
        missing = [(f, ln) for f, ln, kws in calls if "battle_region" not in kws]
        assert not missing, missing
