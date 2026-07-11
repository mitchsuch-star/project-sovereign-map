"""The estate riders landed with the Jealousy v3.2 build (spec §0.3):

ESP-1 — the Fontainebleau beat: >=3 player marshals eroding on the same
        dotation tick fire ONE collective petition (concede rentes /
        refuse / promise the next conquest), latched + cooldown.
ESP-2 — war-weary rich marshals: a fully-met, large expectation turns a
        marshal into the peace party on NEW player war declarations.
ESP-4 — rente default: a negative treasury lapses the largest rente with
        drama (refund this turn's bounced charge), GR5 both sides,
        re-grant after solvency is the recovery path.
"""

from pathlib import Path

import pytest

from backend.game_logic import dotation
from backend.game_logic import jealousy as J
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    w = WorldState.from_dict(world1805.to_dict())
    w.authority_tracker.authority = 50
    return w


def _make_eroding(world, name, wins=3):
    """Give a marshal an unmet expectation past the grace window."""
    if world.current_turn <= dotation.GRACE_TURNS:
        world.current_turn = dotation.GRACE_TURNS + 3
    marshal = world.marshals[name]
    marshal.battles_won = wins
    marshal.expectation_grace_turn = world.current_turn - dotation.GRACE_TURNS
    assert dotation.is_eroding(marshal, world)
    return marshal


# ═══════════════════ ESP-1: THE FONTAINEBLEAU BEAT ══════════════════════════


class TestFontainebleau:
    def test_fires_at_three_eroding(self, world):
        for name in ("Ney", "Murat", "Lannes"):
            _make_eroding(world, name)
        events = []
        J.check_fontainebleau(world, events)
        petition = world.pending_marshal_petition
        assert petition is not None and petition["kind"] == "fontainebleau"
        assert set(petition["context"]["marshals"]) == {"Ney", "Murat", "Lannes"}
        assert any(e["type"] == "fontainebleau_petition" for e in events)

    def test_two_eroding_do_not_fire(self, world):
        for name in ("Ney", "Murat"):
            _make_eroding(world, name)
        J.check_fontainebleau(world, [])
        assert world.pending_marshal_petition is None

    def test_latched_until_count_drops(self, world):
        for name in ("Ney", "Murat", "Lannes"):
            _make_eroding(world, name)
        J.check_fontainebleau(world, [])
        J.handle_petition_response(world, "refuse")
        # still >=3 eroding next tick: the latch holds even past cooldown
        world.current_turn += J.FONTAINEBLEAU_COOLDOWN + 1
        for name in ("Ney", "Murat", "Lannes"):
            _make_eroding(world, name)
        J.check_fontainebleau(world, [])
        assert world.pending_marshal_petition is None
        # count drops below 3 → re-arms; rises again → fires
        world.marshals["Ney"].battles_won = 0
        J.check_fontainebleau(world, [])
        _make_eroding(world, "Ney")
        J.check_fontainebleau(world, [])
        assert world.pending_marshal_petition is not None

    def test_cooldown_blocks_early_refire(self, world):
        for name in ("Ney", "Murat", "Lannes"):
            _make_eroding(world, name)
        J.check_fontainebleau(world, [])
        J.handle_petition_response(world, "refuse")
        # drop + re-rise INSIDE the cooldown window
        world.marshals["Ney"].battles_won = 0
        J.check_fontainebleau(world, [])
        _make_eroding(world, "Ney")
        world.current_turn += 1  # well inside FONTAINEBLEAU_COOLDOWN
        J.check_fontainebleau(world, [])
        assert world.pending_marshal_petition is None

    def test_concede_grants_rentes_and_trust(self, world):
        marshals = [_make_eroding(world, n) for n in ("Ney", "Murat", "Lannes")]
        trust_before = {m.name: m.trust.value for m in marshals}
        J.check_fontainebleau(world, [])
        result = J.handle_petition_response(world, "concede")
        assert result["success"]
        for m in marshals:
            assert m.pension > 0
            assert dotation.get_shortfall(m, world) == 0
            assert m.trust.value == trust_before[m.name] + \
                J.FONTAINEBLEAU_CONCEDE_TRUST
            assert not dotation.is_eroding(m, world)

    def test_refuse_costs_trust(self, world):
        marshals = [_make_eroding(world, n) for n in ("Ney", "Murat", "Lannes")]
        trust_before = {m.name: m.trust.value for m in marshals}
        J.check_fontainebleau(world, [])
        result = J.handle_petition_response(world, "refuse")
        assert result["success"]
        for m in marshals:
            assert m.trust.value == trust_before[m.name] + \
                J.FONTAINEBLEAU_REFUSE_TRUST
            assert m.pension == 0

    def test_promise_extends_grace_and_dents_authority(self, world):
        marshals = [_make_eroding(world, n) for n in ("Ney", "Murat", "Lannes")]
        authority_before = world.authority_tracker.authority
        J.check_fontainebleau(world, [])
        result = J.handle_petition_response(world, "promise")
        assert result["success"]
        assert world.authority_tracker.authority == \
            authority_before + J.FONTAINEBLEAU_PROMISE_AUTHORITY
        for m in marshals:
            assert m.expectation_grace_turn == \
                world.current_turn + J.FONTAINEBLEAU_PROMISE_GRACE
            assert not dotation.is_eroding(m, world)


# ═══════════════════ ESP-2: WAR-WEARY RICH MARSHALS ═════════════════════════


class TestWarWeary:
    # The declare-war flow front-runs my seam with the War Purpose popup
    # and the treaty warning — declare like the resume path does, with
    # those stages resolved, so the test exercises the ESP-2 seam itself.
    _DECLARE = {
        "target_nation": "Prussia",
        "war_objective": "subjugation",
        "_treaty_warning_resolved": True,
        "confirmed_objection": True,
    }

    def _enrich(self, world, name="Davout", wins=5):
        """Fully met, large expectation (>= the 160 floor at 5 wins=200)."""
        marshal = world.marshals[name]
        marshal.battles_won = wins
        marshal.pension = dotation.get_expectation(marshal)
        assert dotation.get_satisfaction(marshal, world) >= \
            dotation.get_expectation(marshal)
        return marshal

    def test_objector_found_only_when_rich_and_met(self, world):
        assert J.find_war_weary_objector(world) is None  # nobody qualifies
        rich = self._enrich(world)
        assert J.find_war_weary_objector(world).name == rich.name

    def test_unmet_rich_marshal_does_not_qualify(self, world):
        marshal = world.marshals["Davout"]
        marshal.battles_won = 5      # expectation 200, satisfaction 0
        assert J.find_war_weary_objector(world) is None

    def test_small_met_expectation_does_not_qualify(self, world):
        marshal = world.marshals["Davout"]
        marshal.battles_won = 2      # expectation 80 < the 160 floor
        marshal.pension = 80
        assert J.find_war_weary_objector(world) is None

    def test_declare_war_pauses_on_petition(self, world):
        from backend.commands.executor import CommandExecutor
        self._enrich(world)
        executor = CommandExecutor()
        result = executor._diplomatic._execute_diplomatic_declare_war(
            dict(self._DECLARE), world)
        assert result.get("marshal_petition"), \
            "the war-weary petition must intercept the declaration"
        assert world.pending_marshal_petition["kind"] == "war_weary"
        assert not world.is_at_war("France", "Prussia")

    def test_march_anyway_declares_and_costs_trust(self, world):
        from backend.commands.executor import CommandExecutor
        rich = self._enrich(world)
        world.diplomatic_points = 5
        executor = CommandExecutor()
        executor._diplomatic._execute_diplomatic_declare_war(
            dict(self._DECLARE), world)
        trust_before = rich.trust.value
        result = J.handle_petition_response(
            world, "march_anyway", executor=executor,
            game_state={"world": world})
        assert rich.trust.value == trust_before + J.WAR_WEARY_MARCH_TRUST
        assert result is not None

    def test_stand_down_rewards_counsel(self, world):
        from backend.commands.executor import CommandExecutor
        rich = self._enrich(world)
        executor = CommandExecutor()
        executor._diplomatic._execute_diplomatic_declare_war(
            dict(self._DECLARE), world)
        trust_before = rich.trust.value
        result = J.handle_petition_response(
            world, "stand_down", executor=executor,
            game_state={"world": world})
        assert result["success"]
        assert rich.trust.value == trust_before + J.WAR_WEARY_HEED_TRUST
        assert not world.is_at_war("France", "Prussia")

    def test_fires_once_per_pair(self, world):
        from backend.commands.executor import CommandExecutor
        self._enrich(world)
        executor = CommandExecutor()
        executor._diplomatic._execute_diplomatic_declare_war(
            dict(self._DECLARE), world)
        J.handle_petition_response(world, "stand_down", executor=executor,
                                   game_state={"world": world})
        result = executor._diplomatic._execute_diplomatic_declare_war(
            dict(self._DECLARE), world)
        assert not result.get("marshal_petition"), \
            "the same (marshal, target) pair petitions only once"

    def test_never_fires_for_existing_war(self, world):
        from backend.commands.executor import CommandExecutor
        self._enrich(world)
        executor = CommandExecutor()
        # Austria is already at war at boot — the seam requires a NEW war
        result = executor._diplomatic._execute_diplomatic_declare_war(
            {"target_nation": "Austria"}, world)
        assert result.get("marshal_petition") is None


# ═══════════════════ ESP-4: THE RENTE DEFAULT ═══════════════════════════════


class TestRenteDefault:
    def _pension(self, world, name, face):
        marshal = world.marshals[name]
        marshal.pension = face
        return marshal

    def _run_dotation(self, world):
        world._dotation_processed_turn = None
        world._process_dotation_state()

    def test_negative_treasury_lapses_largest_first(self, world):
        small = self._pension(world, "Ney", 40)
        big = self._pension(world, "Davout", 120)
        world.nation_gold["France"] = -50
        self._run_dotation(world)
        assert big.pension == 0, "the largest face lapses first"
        # its bounced charge refunds: -50 + ceil(1.5×120)=180 → solvent
        assert world.nation_gold["France"] == 130
        assert small.pension == 40, "solvency restored — the small rente holds"

    def test_cascades_until_solvent_or_dry(self, world):
        self._pension(world, "Ney", 40)
        self._pension(world, "Davout", 60)
        world.nation_gold["France"] = -300
        self._run_dotation(world)
        assert world.marshals["Ney"].pension == 0
        assert world.marshals["Davout"].pension == 0
        # both refunds landed, treasury still under water — nothing left to lapse
        assert world.nation_gold["France"] == -300 + 90 + 60

    def test_solvent_treasury_never_defaults(self, world):
        marshal = self._pension(world, "Ney", 100)
        world.nation_gold["France"] = 500
        self._run_dotation(world)
        assert marshal.pension == 100

    def test_captured_pensioner_skipped(self, world):
        marshal = self._pension(world, "Ney", 100)
        marshal.captured_by = "Austria"
        world.nation_gold["France"] = -10
        self._run_dotation(world)
        assert marshal.pension == 100, \
            "a captured marshal's rente neither pays nor lapses (W6-7)"

    def test_notification_and_log(self, world):
        from backend.notifications import RENTE_DEFAULTED
        self._pension(world, "Ney", 100)
        world.nation_gold["France"] = -10
        self._run_dotation(world)
        pending = world.notifications.get_pending()
        assert any(n["type"] == RENTE_DEFAULTED for n in pending)
        assert any(e.get("type") == "rente_defaulted"
                   for e in world.event_log)

    def test_gr5_enemy_rentes_default_too(self, world):
        kutuzov = self._pension(world, "Kutuzov", 80)
        world.nation_gold["Russia"] = -20
        self._run_dotation(world)
        assert kutuzov.pension == 0
        # no player notification for a foreign court
        from backend.notifications import RENTE_DEFAULTED
        assert not any(
            n["type"] == RENTE_DEFAULTED and
            n.get("details", {}).get("marshal") == "Kutuzov"
            for n in world.notifications.get_pending())

    def test_regrant_after_recovery(self, world):
        marshal = self._pension(world, "Ney", 100)
        world.nation_gold["France"] = -10
        self._run_dotation(world)
        assert marshal.pension == 0
        # solvency returns; the re-grant path works (top-up verb semantics)
        marshal.battles_won = 3
        face = dotation.compute_rente_face(marshal, world)
        assert face > 0
        marshal.pension = face
        world.nation_gold["France"] = 1000
        self._run_dotation(world)
        assert marshal.pension == face
