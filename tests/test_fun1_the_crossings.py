"""Row FUN, FUN-1 "the hands" (November 25, 2026) — a refused crossing names
the way through.

The user's second play: "how do I cross into Turkey from the Balkans? naval
stuff is confusing as shit". The review (`docs/GAMEPLAY_REVIEW_2026_11_25.md`
§1.4) found the Bosphorus refusal advising "break the fleet that covers the
passage" — an order no player has (a sea battle comes only of a landing caught
at sea or a diversion that fails) — and offering no button; "Open borders or
higher required" at peace, the engine's own key and no word of where to get
them; the shut crossing's "pool a fleet"; the Codex saying an expedition sails
only "from a friendly dockyard province".

FUN-1 keeps every rule and changes what a refusal says and offers: the landing
refusal names the landing and the diversion, a march refused at a sea crossing
carries the landing as a button (`alts`), a march refused at a closed border
names the court (`closed_to`, the card's "Ask <court> for open borders").
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import strategic as S
from backend.commands.order_quotes import landing_alts
from backend.game_logic import naval
from backend.game_logic.diplomacy import set_diplomatic_state
from tests import _chip_census as C

CODEX = (M.__file__.replace("\\", "/").rsplit("/backend/", 1)[0]
         + "/godot-client/project-sovereign/scripts/codex_terms.gd")


@pytest.fixture
def client(monkeypatch):
    """The 1805 board with the mock parser, re-opened for ONE test."""
    C.board_env(monkeypatch)
    return TestClient(M.app)


def _stage(who="Murat", at="Rumelia", strength=14000, war=True, hold=("Croatia", "Rumelia")):
    world = M.world
    for name in hold:
        world.regions[name].controller = "France"
    m = world.get_marshal(who)
    m.location = at
    m.strength = strength
    if war:
        set_diplomatic_state(world, "France", "Ottoman", "WAR", reason="test")
    C.refresh_view(world)
    return world, m


def _quote(client, marshal, dest):
    reply = client.get("/march_quotes", params={"marshal": marshal, "dest": dest}).json()
    assert reply.get("success"), reply
    return reply["quote"]


class TestTheWordsAreThePlayers:

    def test_the_landing_refusal_names_the_landing_and_the_diversion(self, client):
        """FUN1-6: at war with the Porte, our water won, the far shore enemy —
        the refusal names the two ways that cross, never an order that does
        not exist."""
        world, _ = _stage(hold=("Croatia",), at="Croatia")
        check = naval.crossing_check(world, "France", "Rumelia", "Constantinople", mover_strength=14000)
        assert check["verdict"] == "landing", check
        msg = check["message"]
        for word in ("Constantinople", "15,000", "transports", "landing", "diversion"):
            assert word in msg, msg
        assert "break the fleet" not in msg and "Sire" not in msg, msg

    def test_the_shut_remedy_says_build_warships_not_pool(self, client):
        """FUN1-6: "pool" was the Admiralty's own word; every dockyard builds
        into the ONE fleet, so building anywhere helps at any crossing."""
        world = M.world
        for pair in naval.get_sea_link_pairs(world):
            a, b = tuple(pair)
            for x, y in ((a, b), (b, a)):
                check = naval.crossing_check(world, "France", x, y, mover_strength=10000)
                if check["verdict"] == "shut":
                    msg = check["message"]
                    assert "pool" not in msg and "warships" in msg, msg
                    assert "land a small expedition" in msg, msg
                    return
        pytest.skip("no shut crossing on the boot board")

    def test_a_closed_border_is_said_plainly_and_names_the_court(self, client):
        """FUN1-7: the one sentence the typed move and the march order read."""
        line = S.closed_border_sentence("Constantinople", "Ottoman", "PEACE")
        assert line.startswith("Cannot enter Constantinople"), line
        for word in ("Ottoman", "at peace", "open borders", "Diplomacy", "declare war"):
            assert word in line, line
        assert "diplomatic state" not in line and "PEACE" not in line, line

    def test_a_titled_court_reads_with_its_article(self, client):
        """Pressed in the real client: "it belongs to Ottoman Empire" — a title
        reads "the Ottoman Empire" inside a sentence; a plain name never does."""
        from backend.display_names import display_nation_in_sentence
        assert display_nation_in_sentence("Ottoman") == "the Ottoman Empire"
        assert display_nation_in_sentence("Austria") == "Austria"
        assert "belongs to the Ottoman Empire" in S.closed_border_sentence("Rumelia", "Ottoman", "PEACE")

    def test_an_armistice_offers_no_open_borders(self, client):
        """The review (lane B): open borders is proposed from PEACE only; an
        armistice's closed border says what does open it."""
        line = S.closed_border_sentence("Vienna", "Austria", "ARMISTICE")
        assert "armistice" in line and "open borders" not in line, line
        assert S.border_can_be_opened("PEACE") and not S.border_can_be_opened("ARMISTICE")

    def test_the_road_across_a_closed_border_names_its_court(self, client):
        """The review's sibling sweep: the three "no open road" refusals are ONE,
        naming the court and its state."""
        world = M.world
        got = S.no_open_road_refusal(world, "France", "Constantinople", "Rumelia", "Ottoman")
        assert got["blocked_diplomatic"] == "Ottoman" and got["blocked_state"] == "PEACE", got
        assert "the Ottoman Empire" in got["message"] and "Sire" not in got["message"], got
        assert "closed frontier" not in got["message"], got

    def test_the_typed_move_says_the_same_sentence(self, client):
        """FUN1-7's sibling (rule 10): the typed move at the closed border."""
        world, _ = _stage(at="Croatia", war=False, hold=("Croatia",))
        reply = C.post(client, {"command": "Murat, move to Rumelia"})
        msg = str(reply.get("message") or "")
        assert "Cannot enter Rumelia" in msg and "open borders" in msg, msg
        assert "diplomatic state" not in msg, msg

    def test_the_codex_says_where_a_landing_sails_from(self):
        """FUN1-8: any coast abroad where the corps stands, or our dockyards
        (`naval._embark_at`) — never only "a friendly dockyard province"."""
        text = open(CODEX, encoding="utf-8").read()
        line = next(ln for ln in text.splitlines() if '["Expedition"' in ln)
        assert "friendly dockyard province" not in line, line
        assert "any coast abroad" in line and "dockyards" in line, line


class TestTheWayThroughIsAButton:
    """`_stage()` puts Murat in Rumelia while it is still the Porte's (an enemy
    coast he stands on — he may sail from it); `hold=("Croatia", "Rumelia")`
    makes Rumelia ours, joined to France by land — our own soil, from which a
    landing sails only at a dockyard."""

    ABROAD = ("Croatia",)

    def test_the_corps_that_fits_is_offered_first(self, client):
        world, murat = _stage(hold=self.ABROAD)
        names = naval.landing_corps_for(world, "France", "Constantinople", prefer="Murat")
        assert names and names[0] == "Murat", names

    def test_a_corps_too_big_for_the_transports_is_not_offered(self, client):
        world, murat = _stage(strength=22000, hold=self.ABROAD)
        assert "Murat" not in naval.landing_corps_for(world, "France", "Constantinople", prefer="Murat")
        assert "15,000" in naval.landing_blocker_line(world, murat)

    def test_the_emperor_never_sails(self, client):
        world, nap = _stage(who="Napoleon", strength=12000, hold=self.ABROAD)
        assert "Napoleon" not in naval.landing_corps_for(world, "France", "Constantinople")
        assert naval.landing_blocker_line(world, nap) == "the Emperor does not sail"

    def test_a_shore_at_peace_and_no_host_is_never_offered(self, client):
        world, murat = _stage(war=False, hold=self.ABROAD)
        assert naval.landing_corps_for(world, "France", "Constantinople", prefer="Murat") == []
        # (the review, lane B) ...nor dimmed with a reason of his own that does not apply
        assert landing_alts(world, murat, "Constantinople", lambda line: {}) == []

    def test_from_our_own_soil_the_reason_names_the_nearest_shore(self, client):
        """The review's how-to was wrong here: once Rumelia is ours and joined
        to France by land, Murat cannot sail from it — the dimmed button says
        where he can."""
        world, murat = _stage()
        assert naval.landing_corps_for(world, "France", "Constantinople", prefer="Murat") == []
        why = naval.landing_blocker_line(world, murat)
        assert "dockyard" in why and "nearest shore he can sail from" in why, why

    def test_from_a_dockyard_any_shore_is_in_reach(self, client):
        world, murat = _stage(at="Provence", hold=self.ABROAD)
        assert "Murat" in naval.landing_corps_for(world, "France", "Constantinople", prefer="Murat")

    def test_landing_alts_reads_the_typed_order(self, client):
        world, murat = _stage(hold=self.ABROAD)
        seen = []

        def read(line):
            seen.append(line)
            return {"kind": "order", "ok": True, "ap": 2, "parts": []}
        rows = landing_alts(world, murat, "Constantinople", read)
        assert seen == ["land Murat in Constantinople"], seen
        assert rows[0]["label"] == "Land Murat in Constantinople by sea", rows
        assert rows[0]["ok"] and rows[0]["ap"] == 2, rows

    def test_a_march_refused_at_the_crossing_carries_the_landing(self, client):
        """FUN1-6: the click road's card — refused, with the landing as its
        button (the refused card draws `alts`)."""
        _stage(hold=self.ABROAD)
        q = _quote(client, "Murat", "Constantinople")
        assert not q["ok"], q
        assert q.get("crossing", {}).get("to") == "Constantinople", q.get("crossing")
        rows = {a.get("command"): a for a in q.get("alts") or []}
        assert "land Murat in Constantinople" in rows, q.get("alts")

    def test_from_our_own_soil_the_card_dims_the_landing_and_says_why(self, client):
        _stage()
        q = _quote(client, "Murat", "Constantinople")
        assert not q["ok"], q
        row = next(a for a in q.get("alts") or [] if a.get("id") == "land")
        assert row["ok"] is False and "nearest shore he can sail from" in row["refusal"], row

    def test_a_march_refused_at_a_closed_border_names_the_court(self, client):
        """FUN1-7: the card's "Ask the Porte for open borders" reads `closed_to`."""
        _stage(at="Croatia", war=False, hold=("Croatia",))
        q = _quote(client, "Murat", "Rumelia")
        assert not q["ok"], q
        assert q.get("closed_to") == "Ottoman", q
        assert q.get("closed_to_shown") == "the Ottoman Empire", q
        assert "open borders" in q["refusal"], q["refusal"]
