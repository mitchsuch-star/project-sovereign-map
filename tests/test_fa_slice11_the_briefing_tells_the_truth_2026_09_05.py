"""FA slice 11 — "The Briefing Tells the Truth" (September 5, 2026).

Twelve rows about the surfaces the player reads every morning. Five roots.

**The satellite's fate** (FA-2 P1, FA-N19, FA-N74, FA-38). A satellite stops
being one three ways, and the player was told the same thing about all of
them — *"Switzerland has ceased to exist."* — while Switzerland stood at Bern
at war with France. The true line was queued `player_vassal`, and
`_is_dispatch_event_visible` reads `world.vassals` at RENDER time, by which
point the row is deleted; so the truth was dropped whichever side of the `del`
it sat on, and the row's "ordering bug" framing is wrong. Visibility is
decided at QUEUE time now, and lord-aware. None of the three exits ever wrote
to `world.event_log`, so the campaign log, the headline window and Le Moniteur
could not see a rebellion at all. And with nothing logged, losing a satellite
could never lead the briefing: Holland bribed away, Switzerland eliminated and
Berry lost in one tick led with *"Berry has fallen"* and EMPTY sub-beats.

The exit that mattered most is the one the filed fix would have missed. On the
shipped 1805 board both big satellites take the GRACEFUL-INDEPENDENCE exit —
they cascade-joined France's war and hit the war-instance side conflict — and
that exit `continue`s before the notification the fix named, so it produced no
rail row, no relation line and no dispatch line at all.

**The soil alarm** (FA-12, FA-N14). The standing-alarm run was keyed on the
PROVINCE, so it restarted every time the enemy moved: T3 "3 turns now", T4 the
base template again as fresh news, T6 "3 turns now" AGAIN. And the arm gated
only on "France controls it", so an enemy standing on a province France had
CONQUERED read as enemy colours on French soil.

**The shelling** (FA-25). `own_mauled` had one producer and it matched
`battle` alone, so a bombardment — the mechanic that takes thousands of men
without a battle — reached neither the headline nor Le Moniteur.

**The prisoner** (FA-32). `dispatch["prisoners"]` was built and read by no
client script on either surface, and the Strategic Ledger listed a captured
marshal as an `idle` corps standing in the captor's capital.

**The enemy phase** (FA-23, FA-N21, FA-N33, FA-N75). An assault on the
player's own garrison was suppressed by a fog gate keyed on the ASSAULTER's
province; a province changing hands to an enemy march rendered as routine
movement; and the CA8-D2 collapse left the coalition card with one bar, one
member line and no Target buttons for a three-power coalition.

**FA-53 is REFUTED BY A LANDED DESIGN DECISION** and nothing was built for it
— see `TestFA53IsRefutedByWOD6`.
"""

import contextlib
import io
from pathlib import Path

import pytest

import backend.campaign_log as CL
import backend.game_logic.dispatch as DISPATCH
import backend.game_logic.ledger as LEDGER
import backend.game_logic.vassal as VASSAL
import backend.game_logic.war_status as WS
import backend.main as M
from backend.campaign_log import (
    CAMPAIGN_LOG_TYPES,
    filter_campaign_log,
    format_event_oneliner,
)
from backend.commands.executor import CommandExecutor
from backend.game_logic.dispatch import build_morning_dispatch
from backend.game_logic.vassal import (
    _defect_vassal_free_and_hostile,
    check_vassal_rebellion,
)
from backend.models.intel import FULL, PARTIAL, RegionIntel
from backend.models.world_state import WorldState

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = str(ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")

LEVERS = [
    (VASSAL, "THE_BREAK_IS_BRIEFED_TRUTHFULLY"),
    (DISPATCH, "SOIL_ALARM_IS_ONE_RUN"),
    (DISPATCH, "SOIL_ALARM_IS_HOME_SOIL_ONLY"),
    (DISPATCH, "THE_SHELLING_IS_BRIEFED"),
    (DISPATCH, "A_LOST_SATELLITE_CAN_LEAD"),
    (LEDGER, "THE_LEDGER_KNOWS_ITS_PRISONERS"),
    (WS, "COALITION_CARD_KEEPS_ITS_MEMBERS"),
    (M, "THE_ASSAULT_ON_OUR_GARRISON_IS_REPORTED"),
]


@pytest.fixture(autouse=True)
def _levers_at_default():
    saved = [(mod, name, getattr(mod, name)) for mod, name in LEVERS]
    yield
    for mod, name, value in saved:
        setattr(mod, name, value)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture
def world():
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


def _rail(w):
    with _quiet():
        return build_morning_dispatch(w)


def _rail_texts(w):
    return [str(r.get("text") or "")
            for r in (_rail(w).get("diplomatic_events") or [])]


def _stand_enemy_on(w, region, name, nation, turn):
    intel = w.intel.get(region) or RegionIntel(region)
    intel.visibility = FULL
    intel.last_updated_turn = turn
    intel.known_marshals = [{"name": name, "nation": nation,
                             "strength": 20000}]
    w.intel[region] = intel


# ═══════════════════════════════════════════════════════════════════════
# The satellite's fate
# ═══════════════════════════════════════════════════════════════════════


class TestTheSatellitesFateIsBriefedTruthfully:

    def test_a_rebel_is_not_said_to_have_ceased_to_exist(self, world):
        """FA-2's headline. Switzerland keeps Bern and goes to war; the only
        dispatch trace the player got was that it no longer existed."""
        world.vassals["Switzerland"]["loyalty"] = 0
        with _quiet():
            check_vassal_rebellion(world)
        texts = _rail_texts(world)
        assert not any("ceased to exist" in t for t in texts), texts
        assert any("Switzerland has rebelled against France" in t
                   for t in texts), texts
        assert world.regions["Bern"].controller == "Switzerland"

    def test_the_lever_down_restores_the_false_line(self, world):
        VASSAL.THE_BREAK_IS_BRIEFED_TRUTHFULLY = False
        world.vassals["Switzerland"]["loyalty"] = 0
        with _quiet():
            check_vassal_rebellion(world)
        assert any("ceased to exist" in t for t in _rail_texts(world))

    def test_the_graceful_exit_is_briefed_at_all(self, world):
        """The exit BOTH big satellites take on the shipped board — they
        cascade-joined France's war, so the war-instance side conflict routes
        them here. Before, it produced no rail row, no relation line and no
        rebellion line: the only trace was the false one."""
        world.vassals["Holland"]["loyalty"] = 0
        with _quiet():
            events = check_vassal_rebellion(world)
        assert [e.get("type") for e in events] == [
            "vassal_rebellion_independent"]
        texts = _rail_texts(world)
        assert any("Holland breaks free of France and stands alone" in t
                   for t in texts), texts
        assert not any("ceased to exist" in t for t in texts)

    def test_the_armistice_exit_no_longer_declares_a_war_it_did_not(
            self, world):
        """Cross-row 2 of the reproduction: this exit appended its own
        'no war declared' line AND fell through to the shared tail, which
        appended 'War declared.' and raised a CRITICAL 'has rebelled against
        France! War declared.' notification — while the state stayed
        ARMISTICE."""
        world.vassals["Switzerland"]["loyalty"] = 0
        key = world._make_diplo_key("France", "Switzerland")
        world.diplomatic_states[key] = "ARMISTICE"
        before = len(world.notifications.to_list())
        with _quiet():
            events = check_vassal_rebellion(world)
        assert [e.get("type") for e in events] == [
            "vassal_rebellion_armistice"]
        assert world.get_diplomatic_state("France", "Switzerland") == "ARMISTICE"
        fresh = world.notifications.to_list()[before:]
        assert not any("War declared" in str(n.get("message") or "")
                       for n in fresh), fresh
        assert any("the armistice holds" in t for t in _rail_texts(world))

    def test_the_free_defection_drops_the_false_line_too(self, world):
        """FA-N19: the same sentence, queued beside 'THE DEFECTION', of a
        court that keeps Bern and takes the field."""
        with _quiet():
            _defect_vassal_free_and_hostile(world, "Switzerland", "Britain")
        assert not any("ceased to exist" in t for t in _rail_texts(world))

    @pytest.mark.parametrize("vassal,exit_path", [
        ("Switzerland", "vassal_rebellion"),
        ("Holland", "vassal_rebellion_independent"),
    ])
    def test_every_exit_writes_to_the_event_log(self, world, vassal,
                                                exit_path):
        """FA-N74. `world.log_event` appeared exactly twice in the whole of
        `vassal.py` and neither was a rebellion, so the campaign log, the
        headline window and Le Moniteur could not see one."""
        world.vassals[vassal]["loyalty"] = 0
        before = len(world.event_log)
        with _quiet():
            check_vassal_rebellion(world)
        rows = [e for e in world.event_log[before:]
                if e.get("type") == "vassal_broke_free"]
        assert len(rows) == 1, world.event_log[before:]
        assert rows[0]["exit"] == exit_path
        assert rows[0]["vassal"] == vassal
        assert rows[0]["lord"] == "France"

    def test_the_campaign_log_prints_a_sentence_not_a_type(self, world):
        """The inert entry it replaced had a one-liner and no producer; a new
        type with a producer and no arm would print `Event: ...`."""
        world.vassals["Holland"]["loyalty"] = 0
        with _quiet():
            check_vassal_rebellion(world)
            visible = filter_campaign_log(world.event_log, world)
        lines = [format_event_oneliner(e) for e in visible
                 if e.get("type") == "vassal_broke_free"]
        assert lines == [
            "Vassal rebellion: Holland breaks free of France and stands alone."]

    def test_the_log_type_count_is_unchanged(self):
        """`diplomatic_vassal_rebellion` was in the set with a fog arm, a
        one-liner and NO producer. Retiring it for the type that is now
        written keeps the count, so the nine `== 160` pins hold rather than
        being flipped for a bookkeeping change."""
        assert len(CAMPAIGN_LOG_TYPES) == 160
        assert "vassal_broke_free" in CAMPAIGN_LOG_TYPES
        assert "diplomatic_vassal_rebellion" not in CAMPAIGN_LOG_TYPES

    def test_the_retired_type_still_has_its_dispatch_template(self):
        """It is retired as a LOG type only. It is still the dispatch key for
        the war exit, and `test_fa_slice8...` pins its HIGH priority."""
        assert "diplomatic_vassal_rebellion" in DISPATCH._DIPLOMATIC_EVENT_TEMPLATES
        assert DISPATCH._DIPLOMATIC_EVENT_PRIORITY[
            "diplomatic_vassal_rebellion"] == "HIGH"

    def test_the_fog_rule_is_decided_at_queue_time_and_knows_the_lord(
            self, world):
        """GR5. `player_vassal` is evaluated at RENDER time against a row that
        no longer exists, which is why the true line was dropped. And the web
        has other lords since VS-5, so 'the player's vassal' cannot be a
        blanket rule."""
        VASSAL.record_vassal_break(
            world, vassal="Bavaria", lord="Austria",
            exit_path="vassal_rebellion")
        queued = [q for q in world.pending_dispatch_events
                  if q.get("type") == "diplomatic_vassal_rebellion"]
        assert queued and queued[-1]["fog_rule"] == "partial_on_nation"
        VASSAL.record_vassal_break(
            world, vassal="Holland", lord="France",
            exit_path="vassal_rebellion")
        ours = [q for q in world.pending_dispatch_events
                if q.get("template_vars", {}).get("nation") == "Holland"]
        assert ours and ours[-1]["fog_rule"] == "always"


class TestALostSatelliteCanLeadTheBriefing:

    def test_a_rebellion_leads(self, world):
        world.vassals["Switzerland"]["loyalty"] = 0
        with _quiet():
            check_vassal_rebellion(world)
        headline = _rail(world).get("headline") or {}
        assert headline.get("class") == "vassal_lost"
        assert "Switzerland" in headline.get("text", "")
        assert "rebelled" in headline.get("text", "")

    def test_the_graceful_break_leads_and_says_which_break_it_was(
            self, world):
        world.vassals["Holland"]["loyalty"] = 0
        with _quiet():
            check_vassal_rebellion(world)
        headline = _rail(world).get("headline") or {}
        assert headline.get("class") == "vassal_lost"
        assert "stand alone" in headline.get("text", "")

    def test_our_own_satellite_being_conquered_leads(self, world):
        """`_we_fought_them` is correctly False for our own satellite, so the
        existing `enemy_eliminated` arm produced NOTHING and the page led with
        a supply nag. The lord is read off the EVENT because
        `_eliminate_nation` deletes the vassal row before the log."""
        for region in list(world.regions.values()):
            if region.controller == "Holland":
                region.controller = "Britain"
        with _quiet():
            world._eliminate_nation("Holland")
        rows = [e for e in world.event_log
                if e.get("type") == "nation_eliminated"
                and e.get("nation") == "Holland"]
        assert rows and rows[-1]["lord"] == "France"
        headline = _rail(world).get("headline") or {}
        assert headline.get("class") == "vassal_lost"
        assert "Conquered" in headline.get("text", "")

    def test_an_enemy_court_dying_is_still_a_triumph_not_a_loss(self, world):
        """The other direction: `enemy_eliminated` must be byte-unchanged for
        an independent court, which carries an empty `lord`."""
        for region in list(world.regions.values()):
            if region.controller == "Austria":
                region.controller = "France"
        with _quiet():
            world._eliminate_nation("Austria")
        headline = _rail(world).get("headline") or {}
        assert headline.get("class") == "enemy_eliminated"

    def test_the_lever_down_restores_the_silence(self, world):
        DISPATCH.A_LOST_SATELLITE_CAN_LEAD = False
        world.vassals["Switzerland"]["loyalty"] = 0
        with _quiet():
            check_vassal_rebellion(world)
        headline = _rail(world).get("headline") or {}
        assert headline.get("class") != "vassal_lost"

    def test_the_class_has_a_weight_a_template_and_a_note(self):
        assert DISPATCH.HEADLINE_WEIGHTS["vassal_lost"] == 84
        assert "vassal_lost" in DISPATCH._HEADLINE_TEMPLATES
        assert "vassal_lost" in DISPATCH._HEADLINE_BERTHIER_NOTES

    def test_it_is_not_a_standing_class(self):
        """It is news, not a nag: a standing class re-leads for turns."""
        assert "vassal_lost" not in DISPATCH.STANDING_HEADLINE_CLASSES


# ═══════════════════════════════════════════════════════════════════════
# The soil alarm
# ═══════════════════════════════════════════════════════════════════════


class TestTheSoilAlarm:

    def test_the_run_survives_the_enemy_moving_between_provinces(
            self, world):
        """FA-12. Keyed on the province, the ladder restarted on every move:
        T3 '3 turns now', T4 the base template as fresh news, T6 '3 turns now'
        again. The run is about the enemy standing on our ground."""
        home = [r for r in world.nation_starting_regions["France"]
                if r in world.regions][:2]
        seen = []
        for turn, region in ((1, home[0]), (2, home[0]), (3, home[0]),
                             (4, home[1]), (5, home[1])):
            world.current_turn = turn
            for r in home:
                if r in world.intel:
                    world.intel[r].known_marshals = []
            _stand_enemy_on(world, region, "Moore", "Britain", turn)
            seen.append((_rail(world).get("headline") or {}).get("text", ""))
        assert "3 turns now" in seen[2]
        assert "4 turns" in seen[3], seen[3]
        assert "5 turns" in seen[4], seen[4]

    def test_the_lever_down_restarts_the_count(self, world):
        DISPATCH.SOIL_ALARM_IS_ONE_RUN = False
        home = [r for r in world.nation_starting_regions["France"]
                if r in world.regions][:2]
        seen = []
        for turn, region in ((1, home[0]), (2, home[0]), (3, home[0]),
                             (4, home[1])):
            world.current_turn = turn
            for r in home:
                if r in world.intel:
                    world.intel[r].known_marshals = []
            _stand_enemy_on(world, region, "Moore", "Britain", turn)
            seen.append((_rail(world).get("headline") or {}).get("text", ""))
        assert "3 turns now" in seen[2]
        assert "4 turns" not in seen[3]

    def test_a_conquered_province_is_not_french_soil(self, world):
        """FA-N14. France holding Swabia with Mack standing on it fired the
        class, and by T3 the ladder said the enemy had stood on French soil
        three turns."""
        world.regions["Swabia"].controller = "France"
        for turn in (1, 2, 3):
            world.current_turn = turn
            _stand_enemy_on(world, "Swabia", "Mack", "Austria", turn)
            headline = _rail(world).get("headline") or {}
            assert headline.get("class") != "enemy_on_our_soil", headline

    def test_the_lever_down_calls_a_conquest_french_soil(self, world):
        DISPATCH.SOIL_ALARM_IS_HOME_SOIL_ONLY = False
        world.regions["Swabia"].controller = "France"
        world.current_turn = 1
        _stand_enemy_on(world, "Swabia", "Mack", "Austria", 1)
        headline = _rail(world).get("headline") or {}
        assert headline.get("class") == "enemy_on_our_soil"

    def test_real_home_soil_still_raises_the_alarm(self, world):
        """The gate must not silence the class it exists for. Boot-dormant by
        construction — at boot France's controlled set IS her home set."""
        home = next(r for r in world.nation_starting_regions["France"]
                    if r in world.regions)
        world.current_turn = 1
        _stand_enemy_on(world, home, "Moore", "Britain", 1)
        headline = _rail(world).get("headline") or {}
        assert headline.get("class") == "enemy_on_our_soil"
        assert home in headline.get("text", "")


# ═══════════════════════════════════════════════════════════════════════
# The shelling
# ═══════════════════════════════════════════════════════════════════════


class TestTheShellingIsBriefed:

    def _shell(self, world, casualties):
        marshal = world.get_marshal("Ney")
        marshal.strength = 24000 - casualties
        world.log_event({
            "type": "bombardment",
            "attacker": "Mack", "attacker_nation": "Austria",
            "defender": "Ney", "defender_nation": "France",
            "attacker_location": "Swabia", "defender_location": "Rhineland",
            "attacker_casualties": 900, "defender_casualties": casualties,
            "turn": int(world.current_turn),
        })

    def test_a_shelling_that_mauls_a_corps_reaches_the_headline(self, world):
        self._shell(world, 9600)
        headline = _rail(world).get("headline") or {}
        assert headline.get("class") == "own_mauled", headline
        assert "Ney" in headline.get("text", "")

    def test_it_names_the_province_and_not_the_field(self, world):
        """The trap in 'also accept bombardment': the battle arm reads
        `location`, and a bombardment event has no such key — its field is
        `defender_location`. A verbatim reuse renders 'mauled at the field'."""
        self._shell(world, 9600)
        headline = _rail(world).get("headline") or {}
        assert "Rhineland" in headline.get("text", "")
        assert "the field" not in headline.get("text", "")

    def test_the_lever_down_restores_the_silence(self, world):
        DISPATCH.THE_SHELLING_IS_BRIEFED = False
        self._shell(world, 9600)
        headline = _rail(world).get("headline") or {}
        assert headline.get("class") != "own_mauled"

    def test_a_light_shelling_is_still_below_the_floor(self, world):
        """The 25% fraction and the WO-16 absolute floor are untouched."""
        self._shell(world, 400)
        headline = _rail(world).get("headline") or {}
        assert headline.get("class") != "own_mauled"

    def test_le_moniteur_can_print_it(self):
        from backend.game_logic.gazette import _WAR_TYPES
        assert "bombardment" in _WAR_TYPES

    def test_the_gazette_prints_a_sentence_for_it(self):
        line = format_event_oneliner({
            "type": "bombardment", "attacker": "Mack",
            "attacker_nation": "Austria", "defender_location": "Rhineland",
            "defender_casualties": 9600, "turn": 3})
        assert line and not line.startswith("Event:")


# ═══════════════════════════════════════════════════════════════════════
# The prisoner
# ═══════════════════════════════════════════════════════════════════════


class TestThePrisonerIsOnTheSurfaces:

    def _capture(self, world):
        with _quiet():
            world.capture_marshal(world.get_marshal("Ney"), "Austria")

    def test_the_dispatch_still_carries_him_after_the_event_window(
            self, world):
        """The backend key was never the defect — no client script read it.
        This pins that the key survives the two-turn `marshal_captured`
        window, which is what makes the client render worth having."""
        self._capture(world)
        world.current_turn += 3
        prisoners = _rail(world).get("prisoners") or []
        assert [p["name"] for p in prisoners] == ["Ney"]
        assert prisoners[0]["captor"] == "Austria"

    def test_both_dispatch_renderers_read_the_key(self):
        """The census that would have caught this: a backend key with no
        client reader is not a feature."""
        for name in ("main.gd", "dispatch_view.gd"):
            src = (ROOT / "godot-client" / "project-sovereign" / "scripts"
                   / name).read_text(encoding="utf-8")
            assert 'data.get("prisoners"' in src, name
            assert "PRISONERS OF WAR" in src, name

    def test_the_ledger_says_he_is_held_and_not_idle(self, world):
        """The Strategic Ledger is the surface the player OPENS, and it was
        the surface that lied: an `idle` corps at `Vienna`, strength 0, 'No
        active orders', with no captivity marker anywhere."""
        self._capture(world)
        from backend.game_logic.ledger import _build_forces
        rows = [r for r in _build_forces(world, "France")
                if r["name"] == "Ney"]
        assert rows, "the prisoner is not on the FORCES tab at all"
        assert rows[0]["status"] == "captured"
        assert rows[0]["captured"] is True
        assert rows[0]["captured_by"] == "Austria"

    def test_the_lever_down_restores_the_idle_corps(self, world):
        self._capture(world)
        LEDGER.THE_LEDGER_KNOWS_ITS_PRISONERS = False
        from backend.game_logic.ledger import _build_forces
        rows = [r for r in _build_forces(world, "France")
                if r["name"] == "Ney"]
        assert rows[0]["status"] != "captured"

    def test_the_ledger_client_renders_the_captivity(self):
        src = (ROOT / "godot-client" / "project-sovereign" / "scripts"
               / "strategic_ledger.gd").read_text(encoding="utf-8")
        assert 'f.get("captured"' in src
        assert "Held by " in src


# ═══════════════════════════════════════════════════════════════════════
# The enemy phase
# ═══════════════════════════════════════════════════════════════════════


class TestTheEnemyPhaseReadsTheField:

    def test_a_bloodless_conquest_says_the_province_fell(self, world):
        """FA-N33. The event has carried `captured_from` since PT-E5 and the
        client's `move` arm read only the destination, so an enemy army
        walking unopposed into a French province rendered as routine
        movement — while the player's own mirror march says 'Bohemia falls to
        France!' and asks what to do with it."""
        for m in list(world.marshals.values()):
            if m.location == "Rhineland" and m.nation == "France":
                m.location = "Paris"
        world.regions["Rhineland"].garrison = 0
        executor = CommandExecutor()
        with _quiet():
            result = executor.execute(
                {"command": {"action": "move", "marshal": "Mack",
                             "target": "Rhineland",
                             "_acting_nation": "Austria"}},
                {"world": world, "executor": executor})
        assert result.get("success") is True, result.get("message")
        moves = [e for e in result["events"] if e.get("type") == "move"]
        assert moves and moves[0]["captured_from"] == "France"
        assert moves[0]["captured_by"] == "Austria"
        assert moves[0]["region"] == "Rhineland"
        # And what the AI DID with it — already decided, never stamped.
        assert moves[0]["capture_choice"] in ("secure", "plunder")

    def test_the_client_renders_the_fall_and_the_fate(self):
        src = (ROOT / "godot-client" / "project-sovereign" / "scripts"
               / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
        block = src.split('"move":')[1][:900]
        assert 'action.get("captured_from"' in block
        assert 'action.get("capture_choice"' in block

    def test_an_assault_on_our_own_garrison_survives_the_fog(self, world):
        """FA-23. No marshal defends a garrison, so the battle arm never
        matched; the region gate keys on the ASSAULTER's province, which for
        the ordinary P4.25 rung is enemy ground at PARTIAL. The assault
        itself lights the ASSAULTED province FULL."""
        world.get_region_intel("Swabia").visibility = PARTIAL
        phase = {"nations": {"Austria": {"actions": [{
            "marshal": "Mack", "action_type": "attack",
            "message": "Mack storms the works.",
            "ai_action": {"marshal": "Mack", "target": "Rhineland"},
            "events": [{"type": "garrison_assault", "marshal": "Mack",
                        "region": "Rhineland", "garrison_losses": 4000,
                        "attacker_losses": 1200,
                        "garrison_remaining": 4000}]}]}}}
        out = M._filter_enemy_phase_by_visibility(phase, world)
        assert out["nations"]["Austria"]["actions"], out

    def test_the_lever_down_suppresses_it(self, world):
        M.THE_ASSAULT_ON_OUR_GARRISON_IS_REPORTED = False
        world.get_region_intel("Swabia").visibility = PARTIAL
        phase = {"nations": {"Austria": {"actions": [{
            "marshal": "Mack", "action_type": "attack",
            "ai_action": {"marshal": "Mack", "target": "Rhineland"},
            "events": [{"type": "garrison_assault", "marshal": "Mack",
                        "region": "Rhineland", "garrison_losses": 4000,
                        "attacker_losses": 1200,
                        "garrison_remaining": 4000}]}]}}}
        out = M._filter_enemy_phase_by_visibility(phase, world)
        assert not out["nations"].get("Austria", {}).get("actions")

    def test_it_does_not_leak_an_assault_on_somebody_else(self, world):
        """The carve-out is our OWN soil, exactly like PT-E5's."""
        world.get_region_intel("Swabia").visibility = PARTIAL
        world.regions["Bohemia"].controller = "Austria"
        phase = {"nations": {"Britain": {"actions": [{
            "marshal": "Moore", "action_type": "attack",
            "ai_action": {"marshal": "Moore", "target": "Bohemia"},
            "events": [{"type": "garrison_assault", "marshal": "Moore",
                        "region": "Bohemia", "garrison_losses": 1000,
                        "attacker_losses": 500,
                        "garrison_remaining": 2000}]}]}}}
        out = M._filter_enemy_phase_by_visibility(phase, world)
        assert not out["nations"].get("Britain", {}).get("actions")

    def test_the_client_has_a_structured_arm_for_it(self):
        """FA-N21's requirement, and the reason it and FA-23 are one fix:
        built from the event, never from the server `message`."""
        src = (ROOT / "godot-client" / "project-sovereign" / "scripts"
               / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
        assert 'event.get("type") == "garrison_assault"' in src
        block = src.split('event.get("type") == "garrison_assault"')[1][:900]
        assert 'event.get("garrison_losses"' in block
        assert 'event.get("garrison_remaining"' in block
        assert 'event.get("message"' not in block


class TestTheCoalitionCardKeepsItsMembers:

    def _card(self, world):
        world.war_exhaustion = {"Britain": 20, "Austria": 55, "Russia": 31}
        with _quiet():
            return WS.build_active_wars(world)

    def test_every_member_is_visible_to_the_card(self, world):
        """FA-N75. CA8-D2 folds three bilateral fronts into one HUD row and
        every block on the card iterates that list — so a three-power
        coalition drew ONE bar, ONE member line and ZERO Target buttons."""
        data = self._card(world)
        rows = WS._coalition_rows(data["wars"])
        members = [r["opponent"] for r in rows if r["in_coalition"]]
        assert members == ["Britain", "Austria", "Russia"]

    def test_the_coordination_and_the_weak_link_come_back(self, world):
        data = self._card(world)
        coalition = data["coalition"]
        assert len(coalition["coordination"]) == 3
        assert coalition["weak_link"] == "Austria"

    def test_the_lever_down_reproduces_the_blindness(self, world):
        WS.COALITION_CARD_KEEPS_ITS_MEMBERS = False
        data = self._card(world)
        coalition = data["coalition"]
        assert coalition["coordination"] == []
        assert coalition["weak_link"] is None
        assert [r["opponent"] for r in WS._coalition_rows(data["wars"])
                if r["in_coalition"]] == ["Britain"]

    def test_the_leader_is_first(self, world):
        """The metadata block is deliberately left BELOW the leader-first
        sort: hoisting it would re-order `members` by `diplomatic_states`
        insertion and flip `test_coordination_quality_labels`."""
        data = self._card(world)
        rows = WS._coalition_rows(data["wars"])
        assert rows[0]["opponent"] == "Britain"
        assert rows[0]["is_coalition_leader"] is True

    def test_a_row_without_folded_members_is_its_own_member(self):
        """A bilateral war and the legacy world are unchanged."""
        plain = [{"opponent": "Britain", "in_coalition": True}]
        assert WS._coalition_rows(plain) == plain

    def test_the_client_unfolds_them_too(self):
        src = (ROOT / "godot-client" / "project-sovereign" / "scripts"
               / "war_detail_popup.gd").read_text(encoding="utf-8")
        assert "func _coalition_member_rows(" in src
        # All three loops read it; `_shared_coalition_war_id` deliberately
        # does not (it wants the war, not the members).
        assert src.count("for w in _coalition_member_rows(wars)") == 3


# ═══════════════════════════════════════════════════════════════════════
# FA-53
# ═══════════════════════════════════════════════════════════════════════


class TestFA53IsRefutedByWOD6:
    """FA-53 asks for the several provinces of one bad day to collapse into a
    tally, so the page has slots left for other news. It was BUILT and then
    REVERTED, because WO slice 4 (WO-D6, "The Capital Speaks") measured the
    same failure — four provinces lost in a turn, the page reading "Limousin /
    Berry / Normandy" with PARIS not on it — and answered it the other way:
    it split `capital_lost` out so the capital always leads, and deliberately
    KEPT the three-province page. Collapsing reds five of its pins.

    Two designs, one already chosen. The row's other half (naming the captor)
    is NPC-15, which is open.
    """

    def test_the_page_still_names_three_fallen_provinces(self):
        """The pin that refutes the row, named here so the disposition is
        discoverable from this slice and not only from the record."""
        from tests.test_wo_slice4_the_capital_speaks import (
            TestTheTailNeverSwallowsDistinctNews,
        )
        assert hasattr(
            TestTheTailNeverSwallowsDistinctNews,
            "test_three_provinces_and_nothing_else_still_fill_both_slots")

    def test_no_collapse_class_was_shipped(self):
        assert "home_captured_many" not in DISPATCH.HEADLINE_WEIGHTS
        assert "home_captured_many" not in DISPATCH._HEADLINE_TEMPLATES

    def test_the_capital_still_has_its_own_class(self):
        """WO-D6's actual answer to the same measured failure."""
        assert DISPATCH.HEADLINE_WEIGHTS["capital_lost"] > (
            DISPATCH.HEADLINE_WEIGHTS["home_captured"])
