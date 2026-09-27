"""The session exit of September 27, 2026 — its residue (Score Mandate §5;
memo `docs/audits/SR_SESSION_EXIT_2026_09_27.md`; rules
`SYSTEMS_REFERENCE.md` §73.7).

SRX-9: B1 made "an audience" the ROUTINE tier's word (the rail's "Hear
him", the Generals chip, the badge). On turn 13 of the AAR arm a CRISIS card
— Lannes's breach with Murat grown entrenched, escalation level 2 — arrived
as a modal titled "Marshal Lannes seeks an audience", the routine tier's
words on the very modal the antechamber exists to keep for graver matters.
The §6 confrontation's title now follows its tier.

Lever `jealousy.THE_CRISIS_IS_NOT_AN_AUDIENCE` — False = one title for both.
"""

import contextlib
import io

import pytest

import backend.main as M
from backend.game_logic import jealousy as J
from tests import _chip_census as C


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


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    w = M.world
    w.authority_tracker.authority = 50
    w.pending_marshal_petition = None
    return w


def _card(world, level):
    lannes, murat = world.get_marshal("Lannes"), world.get_marshal("Murat")
    with _quiet():
        status = J.queue_confrontation_petition(world, lannes, murat, level)
    assert status == J.PETITION_QUEUED, status
    return world.pending_marshal_petition


class TestTheCrisisIsNotAnAudience:

    @pytest.mark.parametrize("level", [0, 1])
    def test_an_audience_still_seeks_an_audience(self, world, level):
        card = _card(world, level)
        assert J.petition_tier(card) == J.PETITION_TIER_AUDIENCE
        assert card["title"] == "Marshal Lannes seeks an audience"

    @pytest.mark.parametrize("level", [2, 3])
    def test_a_crisis_demands_to_be_heard(self, world, level):
        card = _card(world, level)
        assert J.petition_tier(card) == J.PETITION_TIER_CRISIS
        assert card["title"] == "Marshal Lannes demands to be heard"
        assert "audience" not in card["title"]

    def test_the_title_reads_the_tier_table(self, world):
        """ONE rule: the title follows `petition_tier_for` — the level at
        which the tier turns is the level at which the title turns."""
        line = J.ESCALATION_PERMANENT_LEVEL
        below = _card(world, line - 1)
        world.pending_marshal_petition = None
        world.jealousy_confrontations_seen = []
        at = _card(world, line)
        assert "seeks an audience" in below["title"]
        assert "demands to be heard" in at["title"]

    def test_lever_down_one_title(self, world, monkeypatch):
        monkeypatch.setattr(J, "THE_CRISIS_IS_NOT_AN_AUDIENCE", False)
        card = _card(world, 2)
        assert J.petition_tier(card) == J.PETITION_TIER_CRISIS
        assert card["title"] == "Marshal Lannes seeks an audience"


# ═══════════════════════════════════════════════════════════════════════
# SRX-10 — a spent corps does not share the field (the muster's co-located
# arm reads the resolver's own exclusions)
# ═══════════════════════════════════════════════════════════════════════

def _combat():
    from backend.commands.executor import CommandExecutor
    return CommandExecutor()._combat


def _stage_carniola(world, flag, value):
    """The evidence arm's turn 7: Mack at Carniola with Archduke John beside
    him, John spent (`flag`); Murat one march off in Tyrol."""
    mack, john = world.get_marshal("Mack"), world.get_marshal("ArchdukeJohn")
    for m in world.marshals.values():
        if m.location == "Carniola" and m.name not in ("Mack", "ArchdukeJohn"):
            m.location = "Hungary" if m.nation != "France" else "Normandy"
    mack.location = john.location = "Carniola"
    mack.strength, john.strength = 7000, 14000
    for m in (mack, john):
        m.broken = False
        m.retreated_this_turn = False
        m.retreat_recovery = 0
    setattr(john, flag, value)
    murat = world.get_marshal("Murat")
    murat.location = "Tyrol"
    murat.strength = 13904
    return murat, mack, john


SPENT = [("broken", True), ("retreated_this_turn", True), ("retreat_recovery", 1)]


class TestASpentCorpsDoesNotShareTheField:

    @pytest.mark.parametrize("flag,value", SPENT)
    def test_the_defenders_muster_drops_him(self, world, flag, value):
        murat, mack, john = _stage_carniola(world, flag, value)
        joining, committed = _combat()._defender_muster(mack, world)
        assert john not in joining
        assert committed == 0.0

    def test_a_fresh_corps_still_shares_the_field(self, world):
        murat, mack, john = _stage_carniola(world, "retreat_recovery", 0)
        joining, committed = _combat()._defender_muster(mack, world)
        assert john in joining and committed > 0

    @pytest.mark.parametrize("flag,value", SPENT + [("retreat_recovery", 0)])
    def test_the_preview_and_the_resolver_agree(self, world, flag, value):
        """Drift pin: the co-located arm's verdict IS the resolver's
        casualty-participant rule, flag by flag."""
        murat, mack, john = _stage_carniola(world, flag, value)
        combat = _combat()
        joins, _code = combat._muster_reason(john, mack, "Carniola", "Austria", world)
        fights = john in combat._get_casualty_participants(
            mack, "Carniola", "Austria", world)
        assert joins == fights

    def test_the_band_no_longer_prices_the_phantom(self, world):
        """The measured case: the band read "even — a hard fight that may go
        against us" pricing John, and the resolver fought Mack alone."""
        murat, mack, john = _stage_carniola(world, "retreat_recovery", 1)
        odds = _combat().muster_odds(murat, mack, world)
        assert odds["committed_defender"] == 0.0
        assert odds["band"] != "unfavorable"

    def test_our_own_spent_corps_is_not_promised(self, world):
        """The attacker's side reads the same arm: a recovering friend on
        the field is no longer "stands on the field and will fight beside
        him" (nor the shared-casualty note)."""
        ney, soult = world.get_marshal("Ney"), world.get_marshal("Soult")
        soult.location = ney.location
        soult.retreat_recovery = 2
        joins, code = _combat()._muster_reason(
            soult, ney, ney.location, "France", world)
        assert (joins, code) == (False, "broken_recovering")

    def test_lever_down_the_phantom_joiner(self, world, monkeypatch):
        import backend.commands.combat_executor as CE
        monkeypatch.setattr(CE, "A_SPENT_CORPS_DOES_NOT_SHARE_THE_FIELD", False)
        murat, mack, john = _stage_carniola(world, "retreat_recovery", 1)
        joining, committed = _combat()._defender_muster(mack, world)
        assert john in joining and committed > 0
