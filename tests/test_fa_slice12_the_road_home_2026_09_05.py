"""FA slice 12 — "The Road Home Is Walked".

Rows: FA-33 (the treaty's order loses its first turn), FA-N61 (a corps
stranded AFTER the peace is never handed one at all), FA-N73 (the two
non-war vassal exits raise no tray alert).

Every pin here drives a REAL `POST /command {"command": "end turn"}` where
the behaviour under test is a turn's behaviour, because the corridor's own
test file cannot see this seam: `TestSelfRefreshingCorridor._march_home`
hand-moves `marshal.location` and bumps `world.current_turn`, so it never
runs `process_strategic_orders` and the lost first turn is invisible to it.
That blindness is why the defect shipped, and it is why these are new pins
rather than an existing one flipping.
"""
import contextlib
import io
import os

import pytest

os.environ.setdefault("INK_IRON_SAVE_DIR", "")

from backend.game_logic import withdrawal as W          # noqa: E402
from backend.game_logic import vassal as V              # noqa: E402
from backend.game_logic.diplomacy import set_diplomatic_state  # noqa: E402
from backend.models.marshal import Marshal, StrategicOrder     # noqa: E402
from backend.models.world_state import WorldState              # noqa: E402

SCENARIO = "godot-client/project-sovereign/assets/maps/europe_1805.json"


@pytest.fixture(scope="module")
def base_world():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCENARIO)


@pytest.fixture
def world(base_world):
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_dict(base_world.to_dict())


# ══════════════════════════════════════════════════════════════════════════
# The live harness — a real end turn through the real endpoint
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def live(world, tmp_path, monkeypatch):
    """A TestClient wired to THIS world, with the mock parser.

    `.env` sets LLM_MODE=anthropic, so all three seams must be swapped or the
    probe bills the live API: `main.world`, `main.game_state["world"]` and
    `main.parser`. The save dir is sandboxed because an end turn autosaves.
    """
    monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path))
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient

    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "game_state", {"world": world})

    client = TestClient(M.app)

    def end_turn():
        with contextlib.redirect_stdout(io.StringIO()):
            return client.post("/command", json={"command": "end turn"}).json()

    def send(text):
        with contextlib.redirect_stdout(io.StringIO()):
            return client.post("/command", json={"command": text}).json()

    return type("Live", (), {"world": world, "end_turn": staticmethod(end_turn),
                             "send": staticmethod(send)})


@pytest.fixture
def no_interrupts(monkeypatch):
    """Silence the cannon-fire / bad-odds asks.

    They defer the march for a REASON unrelated to this row (the marshal is
    waiting on the player), and leaving them live confounds "did he march"
    with "was he asked something". The interrupt's own interaction with the
    corridor has its own class below.
    """
    from backend.commands.strategic import StrategicOrderProcessor
    monkeypatch.setattr(StrategicOrderProcessor, "_check_interrupts",
                        lambda self, marshal, world: None)


def _peace_with_austria(world, marshal_at=("Davout", "Vienna")):
    name, where = marshal_at
    world.marshals[name].location = where
    with contextlib.redirect_stdout(io.StringIO()):
        set_diplomatic_state(world, "France", "Austria", "PEACE", "test")
    return world.marshals[name]


# ══════════════════════════════════════════════════════════════════════════
# FA-33 — the treaty's order must not claim a first step it never took
# ══════════════════════════════════════════════════════════════════════════

class TestTheTreatyClaimsNoFirstStep:

    def test_the_order_carries_no_issuance_stamp(self, world):
        """The field's documented meaning is "first step already executed by
        executor.py". The treaty executes nothing, so it says nothing."""
        davout = _peace_with_austria(world)
        assert W.is_road_home_order(davout.strategic_order)
        assert davout.strategic_order.issued_turn is None
        assert davout.strategic_order.started_turn == world.current_turn

    def test_the_first_end_turn_after_the_peace_moves_him(self, live,
                                                          no_interrupts):
        """The whole row. Measured before the fix: Vienna -> Vienna."""
        davout = _peace_with_austria(live.world)
        start = davout.location
        live.end_turn()
        assert davout.location != start, (
            "the peace turn is the treaty's, not a turn spent standing still")
        assert davout.location == "Bohemia"

    def test_a_corps_marching_an_optimal_road_is_never_warned(
            self, live, no_interrupts):
        """Measured before the fix: warned on t2, t3, t4, t5 — every turn of
        an optimal march, because the lost turn spent one of the three slack
        turns and a marching corps' surplus is CONSTANT by design."""
        _peace_with_austria(live.world)
        warned = []
        for _ in range(6):
            body = live.end_turn()
            warned += [e for e in (body.get("tactical_events") or [])
                       if e.get("type") == "evacuation_lapsing"
                       and e.get("marshal") == "Davout"]
            if "Davout" not in live.world.marshals:
                break
            if live.world.marshals["Davout"].location in W.get_home_zone(
                    live.world, "France"):
                break
        assert warned == [], f"a corps that is walking home is left alone: {warned}"

    def test_he_is_home_a_turn_sooner(self, live, no_interrupts):
        davout = _peace_with_austria(live.world)
        home = W.get_home_zone(live.world, "France")
        for _ in range(8):
            live.end_turn()
            home = W.get_home_zone(live.world, "France")
            if davout.location in home:
                break
        assert davout.location in home
        assert live.world.current_turn == 5, (
            "5 with the fix, 6 with the stamp — the measured difference")

    def test_the_lever_down_reproduces_the_lost_turn(self, live, no_interrupts,
                                                     monkeypatch):
        """The negative control. Restore the stamp and the SKIP returns."""
        monkeypatch.setattr(W, "THE_TREATY_CLAIMS_NO_FIRST_STEP", False)
        davout = _peace_with_austria(live.world)
        assert davout.strategic_order.issued_turn == live.world.current_turn
        start = davout.location
        body = live.end_turn()
        assert davout.location == start, "the control arm must stand still"
        warned = [e for e in (body.get("tactical_events") or [])
                  if e.get("type") == "evacuation_lapsing"
                  and e.get("marshal") == "Davout"]
        assert warned, "and it must be warned for it"

    def test_the_ai_mirror_is_unchanged(self, live, no_interrupts):
        """GR5. `enemy_ai`'s P1.2 rung never read `issued_turn` at all, so
        the AI's corps always walked on the peace turn — the asymmetry ran
        the PLAYER's way, and the fix must not move the AI's half."""
        mack = live.world.marshals["Mack"]
        mack.location = "Orleanais"
        _peace_with_austria(live.world)
        assert W.is_road_home_order(mack.strategic_order)
        live.end_turn()
        assert mack.location == "Lorraine", (
            "measured identical before and after the fix")

    def test_the_ai_mirror_is_unchanged_with_the_lever_down_too(
            self, live, no_interrupts, monkeypatch):
        """The second arm of the identity, added by the slice-12 review
        round: an identity claim guarded by a ONE-arm pin proves the AI
        walks, not that the fix left it alone. Both arms must agree."""
        monkeypatch.setattr(W, "THE_TREATY_CLAIMS_NO_FIRST_STEP", False)
        mack = live.world.marshals["Mack"]
        mack.location = "Orleanais"
        _peace_with_austria(live.world)
        assert mack.strategic_order.issued_turn == live.world.current_turn
        live.end_turn()
        assert mack.location == "Lorraine", (
            "the AI's rung never read the stamp; both arms must agree")


# ══════════════════════════════════════════════════════════════════════════
# FA-33 rider — a corps frozen on the game's own question is not loitering
# ══════════════════════════════════════════════════════════════════════════

class TestAStandingQuestionIsNotLoitering:

    def test_an_unanswered_ask_never_costs_the_army(self, live):
        """Interrupts LIVE and unanswered — the unattended shape.

        Removing the stamp un-shields the issuance turn from
        `_check_interrupts` (the skip `continue`d ABOVE it), so without this
        rider the fix is a REGRESSION for this arm: measured, interned at
        Vienna on turn 5 having marched nothing, against Bohemia on turn 6
        having marched one province.
        """
        davout = _peace_with_austria(live.world)
        for _ in range(9):
            live.end_turn()
        assert "Davout" in live.world.marshals, (
            "the clock must not run on the game's own silence")
        assert davout.pending_interrupt is not None

    def test_the_mercy_is_marshal_scoped_and_the_corridor_still_closes(
            self, world):
        """The slice-12 review round's headline, and the pin that replaces a
        wrong one.

        The first cut routed this through `_is_immobile`, which adds the
        marshal's NATION to `grace_nations` and refreshes the whole corridor.
        Measured: two corps stranded, ONE frozen on a question and the other
        simply refusing to march — the refuser was never interned, his
        warning read the identical "2 turn(s) left" fourteen turns running,
        and the corridor's expiry walked 10 -> 23 and never closed. Since
        `has_evacuation_grant` gates the transit arm on
        `can_enter_territory`, that is a permanent right of passage bought
        with one unanswered modal.

        The pin it replaced asserted `expiry - current_turn` was constant,
        which measured the offset and not the calendar — it was green about
        the defect.
        """
        davout = _peace_with_austria(world)
        ney = world.marshals["Ney"]
        ney.location = davout.location
        for m in (davout, ney):
            m.strategic_order = None
            m.road_home_offered = True        # both decline the road
        davout.pending_interrupt = {"interrupt_type": "cannon_fire",
                                    "marshal": "Davout"}
        offsets, interned = [], []
        for _ in range(14):
            world.current_turn += 1
            with contextlib.redirect_stdout(io.StringIO()):
                for ev in W.process_evacuation_grants(world):
                    if ev.get("type") == "marshal_interned":
                        interned.append(ev.get("marshal"))
            grants = dict(getattr(world, "evacuation_grants", {}) or {})
            if "Austria|France" in grants:
                offsets.append(grants["Austria|France"] - world.current_turn)
        assert "Ney" in interned, (
            "a corps that CAN march and does not must still run out of road")
        assert "Davout" not in interned, (
            "and the one the game is waiting on must not")
        assert offsets == sorted(offsets, reverse=True), (
            f"the deadline must keep counting down: {offsets}")
        assert not W.has_evacuation_grant(world, "France", "Austria"), (
            "the corridor closes; one unanswered modal cannot buy permanent "
            "transit")

    def test_a_standalone_decision_counts_too(self, world):
        """`last_stand` and `muster_confirm` stop the march exactly as an
        order-bound ask does — the predicate is the whole set, not just
        `ORDER_BOUND_INTERRUPT_TYPES`. It is deliberately NOT `_is_immobile`:
        that one refreshes the whole nation's corridor."""
        davout = world.marshals["Davout"]
        davout.pending_interrupt = {"interrupt_type": "last_stand"}
        assert W._awaiting_the_players_word(davout) is True
        assert W._is_immobile(davout) is False, (
            "a question is marshal-scoped mercy, not a corridor refresh")
        davout.pending_interrupt = {"interrupt_type": "cannon_fire"}
        assert W._awaiting_the_players_word(davout) is True
        davout.pending_interrupt = {"interrupt_type": "not_a_real_type"}
        assert W._awaiting_the_players_word(davout) is False

    def test_the_lever_down_removes_the_grace(self, world, monkeypatch):
        """With the lever down the frozen corps is judged like anybody else
        — which is the pre-slice behaviour, and interns him for the game's
        own silence."""
        monkeypatch.setattr(W, "A_STANDING_QUESTION_IS_NOT_LOITERING", False)
        davout = _peace_with_austria(world)
        davout.strategic_order = None
        davout.road_home_offered = True
        davout.pending_interrupt = {"interrupt_type": "cannon_fire",
                                    "marshal": "Davout"}
        interned = []
        for _ in range(9):
            world.current_turn += 1
            with contextlib.redirect_stdout(io.StringIO()):
                for ev in W.process_evacuation_grants(world):
                    if ev.get("type") == "marshal_interned":
                        interned.append(ev.get("marshal"))
        assert "Davout" in interned

    def test_a_routed_corps_keeps_its_own_grace(self, world):
        """The pre-slice arm is untouched."""
        davout = world.marshals["Davout"]
        davout.retreat_recovery = 2
        assert W._is_immobile(davout) is True


# ══════════════════════════════════════════════════════════════════════════
# FA-N61 — the offer stands while he is stranded
# ══════════════════════════════════════════════════════════════════════════

class TestTheOfferStandsWhileHeIsStranded:

    def test_the_organic_case_no_longer_loses_two_marshals(
            self, live, no_interrupts):
        """The row's own single-line recipe, measured on the shipped board.

        Austria is still at war with Bavaria and KingdomOfItaly, so it takes
        Franconia under Bernadotte and Milan under Massena two and three
        turns AFTER the peace. Before the fix both were warned 2/1/0 and
        INTERNED on turn 7, with `strategic_order = None` on every line in
        between — two French marshals destroyed in six turns by one treaty.
        """
        _peace_with_austria(live.world)
        for _ in range(9):
            live.end_turn()
        fallen = getattr(live.world, "fallen_marshals", {}) or {}
        interned = {name: row for name, row in fallen.items()
                    if row.get("cause") == "interned"}
        assert interned == {}, f"nobody is interned for want of a road: {interned}"
        for name in ("Bernadotte", "Massena"):
            assert name in live.world.marshals, f"{name} was lost"

    def test_a_corps_stranded_after_the_peace_is_handed_the_road(
            self, live, no_interrupts):
        _peace_with_austria(live.world)
        bernadotte = live.world.marshals["Bernadotte"]
        assert bernadotte.strategic_order is None
        seen_road = False
        for _ in range(4):
            live.end_turn()
            if W.is_road_home_order(getattr(bernadotte, "strategic_order",
                                            None)):
                seen_road = True
                break
        assert seen_road, "the treaty's offer stands while he is stranded"

    def test_the_lever_down_reproduces_the_two_internments(
            self, live, no_interrupts, monkeypatch):
        """The negative control, and it is the row's own measurement."""
        monkeypatch.setattr(W, "THE_ROAD_IS_OFFERED_WHILE_HE_IS_STRANDED",
                            False)
        _peace_with_austria(live.world)
        for _ in range(9):
            live.end_turn()
        fallen = getattr(live.world, "fallen_marshals", {}) or {}
        interned = sorted(name for name, row in fallen.items()
                          if row.get("cause") == "interned")
        assert interned == ["Bernadotte", "Massena"], (
            f"the control arm must lose them: {interned}")

    def test_the_top_up_says_so(self, live, no_interrupts):
        """Silence is why the organic case read as an unexplained loss: the
        first thing the player was told about either marshal was a lapsing
        line two turns from internment, opening "is no nearer home" about a
        corps that had had an order for zero turns."""
        _peace_with_austria(live.world)
        beats = []
        for _ in range(4):
            body = live.end_turn()
            beats += [e for e in (body.get("tactical_events") or [])
                      if e.get("type") == "evacuation_granted"
                      and e.get("mid_treaty")]
        assert beats, "a road handed out mid-treaty is news"
        first = beats[0]
        assert first["marshals"], "it names the corps"
        assert first["nation_b"] == "Austria", "and the treaty it rides on"
        assert first["turns"] > 0, "and how long he has"

    def test_the_offer_is_reported_before_the_warning_it_answers(
            self, live, no_interrupts):
        """A corps stranded late has little slack, so he is topped up AND
        warned in the same tick — Massena, measured, at surplus 2. The two
        must read in the order they happened, or the briefing tells the
        player his corps is "no nearer home" before it tells him Berthier
        has just given him a road.
        """
        _peace_with_austria(live.world)
        for _ in range(4):
            body = live.end_turn()
            types = [(e.get("type"), e.get("marshal")
                      or (e.get("marshals") or [None])[0])
                     for e in (body.get("tactical_events") or [])
                     if e.get("type") in ("evacuation_granted",
                                          "evacuation_lapsing")]
            offered = [i for i, (t, who) in enumerate(types)
                       if t == "evacuation_granted"]
            warned = [i for i, (t, who) in enumerate(types)
                      if t == "evacuation_lapsing"]
            if offered and warned:
                assert min(offered) < max(warned), types
                return
        pytest.fail("the fixture must produce an offer and a warning in one "
                    "tick, or this pin is vacuous")

    def test_the_beat_is_told_from_the_players_side_of_the_table(self, world):
        """Slice-12 review round. The fog arm for `evacuation_granted` admits
        any SIGNATORY — right for the treaty's own beat, which both courts
        signed, and wrong for a per-corps bulletin published every turn.

        Measured before the fix: France read *"Berthier has put ArchdukeJohn
        on the road home to Bohemia"* about an Austrian corps it could not
        see, naming his province AND his destination, in France's own chief
        of staff's voice, with the campaign log rendering it "under the peace
        with France".
        """
        davout = _peace_with_austria(world)
        assert davout is not None
        before = len([e for e in world.event_log
                      if e.get("type") == "evacuation_granted"])
        offer = {"marshal": "ArchdukeJohn", "nation": "Austria",
                 "from": "Tyrol", "to": "Bohemia"}
        assert W._offer_event(world, offer, "France", 7) is None, (
            "a counterparty top-up is not France's news")
        assert len([e for e in world.event_log
                    if e.get("type") == "evacuation_granted"]) == before, (
            "and it is not written to the log either")
        mine = {"marshal": "Davout", "nation": "France",
                "from": "Vienna", "to": "Franche-Comte"}
        assert W._offer_event(world, mine, "Austria", 7) is not None

    def test_a_rout_is_not_a_refusal(self, world):
        """Slice-12 review round, and it is my own argument turned against
        me. The latch is keyed on ISSUANCE precisely so it covers every way
        the order can be let go — but three engine sites null a
        `strategic_order` with no player anywhere near it (the encircled
        retreat, the forced retreat, the shattered army). Measured before the
        fix: a corps whose road home was cancelled by a forced retreat was
        never re-offered one, and was interned having refused nothing.
        """
        davout = _peace_with_austria(world)
        davout.strategic_order = None
        assert davout.road_home_offered is True
        davout.retreating = True                 # the enemy did this, not the
        with contextlib.redirect_stdout(io.StringIO()):   # Emperor
            W.offer_road_home(world, "France")
        assert W.is_road_home_order(davout.strategic_order), (
            "a latch that cannot tell a refusal from a rout punishes the "
            "wrong thing")

        # ...and the shattered arm, which clears `retreating` and sets
        # `broken` instead.
        davout.retreating = False
        davout.broken = True
        davout.strategic_order = None
        davout.road_home_offered = True
        with contextlib.redirect_stdout(io.StringIO()):
            W.offer_road_home(world, "France")
        assert W.is_road_home_order(davout.strategic_order)

    def test_a_refusal_by_a_standing_corps_is_still_honoured(self, world):
        """The negative control for the arm above: an unhurt corps who let
        the road go is still not chased."""
        davout = _peace_with_austria(world)
        davout.strategic_order = None
        assert not davout.retreating and not davout.broken
        with contextlib.redirect_stdout(io.StringIO()):
            W.offer_road_home(world, "France")
        assert davout.strategic_order is None

    def test_the_beat_reads_honestly_in_the_campaign_log(self, live,
                                                         no_interrupts):
        """The shared `evacuation_granted` renderer announces a PEACE. Used
        raw, a top-up would announce the same peace a second time — and with
        an empty counterpart it read "between France and  — 1 corps, 0
        turns"."""
        from backend.campaign_log import format_event_oneliner
        _peace_with_austria(live.world)
        line = None
        for _ in range(4):
            body = live.end_turn()
            for e in (body.get("tactical_events") or []):
                if e.get("type") == "evacuation_granted" and e.get("mid_treaty"):
                    line = format_event_oneliner(e)
                    break
            if line:
                break
        assert line, "the top-up reaches the campaign log"
        assert "put on the road home" in line
        assert "Safe passage home granted by the peace" not in line, (
            "it must not re-announce a peace signed turns ago")

    def test_the_dispatch_identity_is_the_corps_not_the_pair(self, live,
                                                             no_interrupts):
        """Two corps stranded on the same treaty are two pieces of news; the
        peace's own beat already owns `road_home:<pair>`."""
        from backend.game_logic.dispatch import build_morning_dispatch
        world = live.world
        world.current_turn = 5
        for name in ("Bernadotte", "Massena"):
            world.log_event({
                "type": "evacuation_granted", "nation_a": "France",
                "nation_b": "Austria", "region": "Franconia", "turns": 5,
                "marshals": [name], "destinations": {name: "Franche-Comte"},
                "cut_off": [], "mid_treaty": True,
                "message": f"{name} put on the road home.",
            })
        with contextlib.redirect_stdout(io.StringIO()):
            dispatch = build_morning_dispatch(world)
        head = dispatch.get("headline") or {}
        rendered = [head.get("text", "")] + list(head.get("sub_beats") or [])
        assert any("Bernadotte" in t for t in rendered), rendered
        assert any("Massena" in t for t in rendered), rendered

    def test_the_mid_treaty_beat_does_not_announce_a_stale_peace(
            self, live):
        """The shared headline template opens "the war with Austria is
        over" — true when the peace is the news, misleading three turns
        later when the news is that ONE corps was picked up by a treaty
        already signed."""
        from backend.game_logic.dispatch import build_morning_dispatch
        world = live.world
        world.current_turn = 5
        world.log_event({
            "type": "evacuation_granted", "nation_a": "France",
            "nation_b": "Austria", "region": "Franconia", "turns": 5,
            "marshals": ["Bernadotte"],
            "destinations": {"Bernadotte": "Franche-Comte"},
            "cut_off": [], "mid_treaty": True,
            "message": "Bernadotte put on the road home.",
        })
        with contextlib.redirect_stdout(io.StringIO()):
            dispatch = build_morning_dispatch(world)
        head = dispatch.get("headline") or {}
        assert head.get("class") == "road_home_mid_treaty"
        assert "is over" not in head.get("text", ""), head.get("text")
        assert "under the peace with Austria" in head.get("text", "")


class TestTheRefusalIsRemembered:

    def test_a_cancelled_road_is_not_re_issued(self, live, no_interrupts):
        """§4.1: "cancellable, overridable". Without this the top-up
        overrules the player every tick — measured: the order returns the
        turn after "Davout halts his march and awaits new orders."."""
        davout = _peace_with_austria(live.world)
        reply = live.send("Davout, cancel orders")
        assert reply.get("success") is not False
        assert davout.strategic_order is None
        assert davout.road_home_offered is True
        for _ in range(2):
            live.end_turn()
            if "Davout" not in live.world.marshals:
                break
            assert davout.strategic_order is None, (
                "the treaty offers a road; it does not chase him with it")

    def test_the_refusal_still_has_its_consequence(self, live, no_interrupts):
        """Honouring the refusal is not softening it — §6 stands."""
        davout = _peace_with_austria(live.world)
        live.send("Davout, cancel orders")
        for _ in range(6):
            live.end_turn()
            if "Davout" not in live.world.marshals:
                break
        assert "Davout" not in live.world.marshals
        assert live.world.fallen_marshals["Davout"]["cause"] == "interned"

    def test_a_new_treaty_is_a_new_offer(self, world):
        davout = _peace_with_austria(world)
        davout.strategic_order = None
        assert davout.road_home_offered is True
        with contextlib.redirect_stdout(io.StringIO()):
            W.open_evacuation_corridor(world, "France", "Austria")
        assert W.is_road_home_order(davout.strategic_order), (
            "whatever he did with the last road, this one is not it")

    def test_a_second_concurrent_treaty_does_not_defeat_the_refusal(
            self, world):
        """Found by attacking this slice's own fix, before a reviewer did.

        The first cut cleared the flag for EVERY marshal of both signatories
        whenever any corridor opened. Measured: Davout declines the Austrian
        road, the tick correctly leaves him alone, then France makes peace
        with Russia — an unrelated treaty, on the other side of Europe — and
        the Russian opener wipes the record for every French marshal, so the
        next tick hands Davout back the road he refused. His situation had
        not changed; only somebody else's treaty had.

        The rule now: the record lapses with the treaty that made the offer,
        so it clears when a nation goes from NO passage to some, never when
        it merely gains a second.
        """
        davout = _peace_with_austria(world)
        assert davout.road_home_offered is True
        davout.strategic_order = None            # the refusal
        with contextlib.redirect_stdout(io.StringIO()):
            W.process_evacuation_grants(world)
        assert davout.strategic_order is None

        world.marshals["Ney"].location = "Podolia"
        with contextlib.redirect_stdout(io.StringIO()):
            set_diplomatic_state(world, "France", "Russia", "PEACE", "test")
        assert len(world.evacuation_grants) == 2, world.evacuation_grants
        assert davout.road_home_offered is True, (
            "a second treaty is not a second offer to a corps who declined "
            "the first")
        assert davout.strategic_order is None
        with contextlib.redirect_stdout(io.StringIO()):
            W.process_evacuation_grants(world)
        assert davout.strategic_order is None

    def test_a_corps_holding_the_road_is_recorded_as_offered(self, world):
        """The other half of the same defect: the `already marching there`
        guard returns without touching the marshal, so a corps who reached
        that guard with a cleared flag would have his NEXT cancel silently
        overruled."""
        davout = _peace_with_austria(world)
        davout.road_home_offered = False         # simulate the cleared state
        with contextlib.redirect_stdout(io.StringIO()):
            W.offer_road_home(world, "France")
        assert davout.road_home_offered is True

    def test_arriving_home_clears_the_memory(self, live, no_interrupts):
        davout = _peace_with_austria(live.world)
        for _ in range(6):
            live.end_turn()
            if davout.location in W.get_home_zone(live.world, "France"):
                break
        assert davout.location in W.get_home_zone(live.world, "France")
        assert davout.road_home_offered is False

    def test_the_flag_survives_a_save_load(self, world):
        davout = _peace_with_austria(world)
        assert davout.road_home_offered is True
        with contextlib.redirect_stdout(io.StringIO()):
            reloaded = WorldState.from_dict(world.to_dict())
        assert reloaded.marshals["Davout"].road_home_offered is True

    def test_a_pre_slice_save_loads_with_the_flag_down(self, world):
        data = world.to_dict()
        for row in data["marshals"].values():
            row.pop("road_home_offered", None)
        with contextlib.redirect_stdout(io.StringIO()):
            reloaded = WorldState.from_dict(data)
        assert all(m.road_home_offered is False
                   for m in reloaded.marshals.values())

    def test_without_the_memory_the_top_up_would_chase_him(self, live,
                                                            no_interrupts):
        """The hazard the flag exists to close, demonstrated.

        Clear the memory by hand — everything else identical — and the very
        next tick hands the cancelled order straight back. That is what the
        filed FA-N61 fix would have shipped, and it is why the refusal is
        remembered rather than re-derived from `strategic_order is None`,
        which a newly-stranded corps and a refusing one share.
        """
        davout = _peace_with_austria(live.world)
        live.send("Davout, cancel orders")
        assert davout.strategic_order is None
        davout.road_home_offered = False
        live.end_turn()
        assert W.is_road_home_order(davout.strategic_order), (
            "without the memory the top-up re-issues — which is the hazard")


class TestTheGuardsAreShared:
    """The top-up reuses `_issue_road_home_orders`' body, so it inherits the
    four guards rather than re-earning them. Each is pinned at the NEW
    caller, because `test_win_d3_road_home.py` only ever exercised the old
    one."""

    def test_a_standing_player_order_is_not_overruled_by_the_tick(
            self, live, no_interrupts):
        davout = _peace_with_austria(live.world)
        davout.strategic_order = StrategicOrder(
            command_type="HOLD", target="Vienna", target_type="region",
            started_turn=1, original_command="Davout, hold Vienna")
        live.end_turn()
        assert davout.strategic_order.command_type == "HOLD"

    def test_a_corps_already_home_is_not_given_one(self, live, no_interrupts):
        _peace_with_austria(live.world)
        ney = live.world.marshals["Ney"]
        ney.location = "Paris"
        live.end_turn()
        assert ney.strategic_order is None

    def test_a_cut_off_corps_is_still_refused_honestly(self, world):
        """No road is invented for a corps with none — §5, gate Q4.

        The corridor's own file stages this with the Ionian Islands: an
        island of soil with no land route home at all. Volhynia will NOT do —
        `distance_home` routes WITH the corridor by design, so the grant
        itself opens a road out of it.

        A SECOND corps must be stranded-but-reachable, and that is what the
        mutation sweep taught: the first cut of this pin staged the cut-off
        corps alone, so `open_evacuation_corridor` rolled its provisional
        grant back (nobody was marching), `process_evacuation_grants`
        returned at `if not grants:` and the top-up was never reached at all.
        The pin was green about a line it never executed.
        """
        for m in list(world.marshals.values()):
            if m.nation == "France":
                m.location = "Paris"
        davout = world.marshals["Davout"]
        davout.location = "Ionian Islands"
        ney = world.marshals["Ney"]
        ney.location = "Vienna"               # stranded, and reachable
        with contextlib.redirect_stdout(io.StringIO()):
            set_diplomatic_state(world, "France", "Austria", "PEACE")
        assert world.evacuation_grants, (
            "a grant must stand, or the tick returns before the top-up")
        home = W.get_home_zone(world, "France")
        assert W.distance_home(world, davout, home) is None, (
            "the fixture must actually cut him off, or this pin is vacuous")
        assert davout in W._evacuating_marshals(world, "France", home), (
            "and he must reach the top-up's own loop")
        davout.strategic_order = None
        davout.road_home_offered = False
        with contextlib.redirect_stdout(io.StringIO()):
            W.process_evacuation_grants(world)
        assert davout.strategic_order is None


# ══════════════════════════════════════════════════════════════════════════
# FA-N73 — the two non-war exits ring the bell too
# ══════════════════════════════════════════════════════════════════════════

def _plant_satellite_corps(world, vassal):
    capital = world.get_nation_capital(vassal) or "Paris"
    marshal = Marshal("Daendels", capital, 12000, "cautious", nation="France")
    marshal.original_nation = vassal
    world.marshals["Daendels"] = marshal
    world._build_marshal_index()
    world.vassals[vassal]["loyalty"] = 0
    return marshal


def _break(world, vassal):
    with contextlib.redirect_stdout(io.StringIO()):
        return V.check_vassal_rebellion(world)


class TestAQuietBreakStillRingsTheBell:

    def test_the_graceful_exit_raises_one_alert(self, world):
        """`vassal_rebellion_independent` is the exit BOTH big French
        satellites take on the 1805 board — they cascade-joined France's war
        and hit the war-instance side conflict. Before this it left the
        empire smaller by a nation with nothing on the rail."""
        _plant_satellite_corps(world, "Holland")
        before = len(world.notifications.get_pending())
        events = _break(world, "Holland")
        assert any(e.get("type") == "vassal_rebellion_independent"
                   for e in events)
        rows = world.notifications.get_pending()
        assert len(rows) == before + 1
        row = rows[-1]
        assert "Holland" in row["title"]
        assert "no war is declared" in row["message"]

    def test_the_armistice_exit_raises_one_alert(self, world):
        _plant_satellite_corps(world, "Holland")
        key = world._make_diplo_key("France", "Holland")
        world.diplomatic_states[key] = "ARMISTICE"
        before = len(world.notifications.get_pending())
        events = _break(world, "Holland")
        assert any(e.get("type") == "vassal_rebellion_armistice"
                   for e in events)
        assert len(world.notifications.get_pending()) == before + 1

    def test_it_never_says_war_was_declared(self, world):
        """The row asked for a bare fall-through to the war exit's
        notification. Its body is "…has rebelled against France! War
        declared." — false on both soft exits, and it would re-open the
        contradiction slice 11 closed (a CRITICAL banner announcing a war one
        row above a rail line saying no war was declared)."""
        _plant_satellite_corps(world, "Holland")
        _break(world, "Holland")
        for row in world.notifications.get_pending():
            assert "War declared" not in row["message"]
            assert "rebelled against" not in row["message"]
            assert "ceased to exist" not in row["message"]

    def test_it_is_not_a_crisis(self, world):
        """HIGH, not CRITICAL: a satellite walking out is grave, and it is
        not a crisis. CRITICAL is the war register."""
        from backend.notifications import NotificationPriority
        _plant_satellite_corps(world, "Holland")
        _break(world, "Holland")
        row = world.notifications.get_pending()[-1]
        assert row["priority"] == NotificationPriority.HIGH

    def test_a_foreign_lords_quiet_break_raises_nothing(self, world):
        """Lord-gated exactly like the war exit's own notification — the
        slice-11 round closed a rail banner about somebody else's
        satellite."""
        world.vassals["Bavaria"] = {"lord": "Austria", "loyalty": 0,
                                    "autonomy": 50}
        # Force the SOFT exit — this pin is about the quiet break, and the
        # war exit's own lord gate is pinned by slice 11.
        key = world._make_diplo_key("Austria", "Bavaria")
        world.diplomatic_states[key] = "ARMISTICE"
        events = _break(world, "Bavaria")
        assert any(e.get("type") == "vassal_rebellion_armistice"
                   for e in events), events
        mine = [r for r in world.notifications.get_pending()
                if "Bavaria" in (r.get("title") or "")]
        assert mine == [], (
            "a foreign lord's satellite leaving is not a banner on OUR rail")

    def test_the_war_exit_keeps_its_own_critical(self, world):
        """Untouched: exactly one alert, and it is the war one."""
        from backend.notifications import NotificationPriority
        _plant_satellite_corps(world, "Switzerland")
        _break(world, "Switzerland")
        mine = [r for r in world.notifications.get_pending()
                if "Switzerland" in (r.get("title") or "")]
        assert any(r["priority"] == NotificationPriority.CRITICAL for r in mine)

    def test_the_lever_down_restores_the_silent_tray(self, world, monkeypatch):
        monkeypatch.setattr(V, "A_QUIET_BREAK_STILL_RINGS_THE_BELL", False)
        _plant_satellite_corps(world, "Holland")
        before = len(world.notifications.get_pending())
        _break(world, "Holland")
        assert len(world.notifications.get_pending()) == before

    def test_the_mechanical_tail_is_not_doubled(self, world):
        """Slice 11's own hazard, re-pinned at the new caller: the four
        effects live in `complete_vassal_break` and this slice adds only a
        sentence."""
        _plant_satellite_corps(world, "Holland")
        _break(world, "Holland")
        assert world.vassals["Switzerland"]["loyalty"] == 90, (
            "one -10 sibling shock, not two")


# ══════════════════════════════════════════════════════════════════════════
# The §4.3 beat names the corps the treaty declined to move
# ══════════════════════════════════════════════════════════════════════════

class TestTheBeatNamesEveryCorps:

    def test_a_corps_under_the_emperors_own_order_is_named(self, world):
        """§4.3 promises a beat "naming names and the deadline". It named
        nobody whenever EVERY stranded corps already held an order of the
        player's, because the sentence is keyed on `orders` and the treaty
        issues none to a marshal it will not overrule. Measured in an
        archived campaign: four corps under a typed `hold position`, the beat
        read "The peace grants safe passage home.", and the first name the
        player read was an internment."""
        davout = world.marshals["Davout"]
        davout.location = "Vienna"
        davout.strategic_order = StrategicOrder(
            command_type="HOLD", target="Vienna", target_type="region",
            started_turn=1, original_command="Davout, hold position")
        with contextlib.redirect_stdout(io.StringIO()):
            set_diplomatic_state(world, "France", "Austria", "PEACE", "test")
        beats = [e for e in world.event_log
                 if e.get("type") == "evacuation_granted"]
        assert beats, "the peace still logs its beat"
        line = beats[-1]["message"]
        assert davout.strategic_order.command_type == "HOLD", (
            "the treaty did not overrule him")
        assert "Davout" in line
        assert line != "The peace grants safe passage home."
        assert "does not overrule the Emperor" in line

    def test_the_ordinary_beat_is_unchanged(self, world):
        davout = _peace_with_austria(world)
        assert davout.strategic_order is not None
        beats = [e for e in world.event_log
                 if e.get("type") == "evacuation_granted"]
        assert beats
        assert "Berthier has given them the road home" in beats[-1]["message"]
        assert "does not overrule the Emperor" not in beats[-1]["message"]
