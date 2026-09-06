"""FA slice 14 — "The Rulings and the Singles" (September 5, 2026).

Landing record: the boxed SLICE 14 block in `docs/BUG_FIXES.md`
§Final Whole-Game Audit.

Rows closed here and the shape of each:

* **FA-D28** (ruling 2) — the garrison assault's minimum-loss floor reads the
  DEFENDING garrison's strength, not the attacker's own. Reading his own made
  it a pure over-match tax that binds only above ~12.5x, so the bigger the
  corps the more it paid for the same works.
* **FA-R5** — the assault reaches the campaign log and the morning briefing.
  Two of the resolver's three exits (HOLD, and FALL-into-OCCUPATION) left no
  trace on any persistent surface at all.

Both live in `CombatExecutor._resolve_garrison_combat`, which is the single
source for every board: the attack path (player and enemy P4.25 alike) and
`naval_executor`'s landing against a defended capital are its only callers,
so GR5 is inherited rather than re-earned.
"""

import contextlib
import io

import pytest

from backend.campaign_log import (
    CAMPAIGN_LOG_TYPES,
    CATEGORY_MAP,
    filter_campaign_log,
    format_event_oneliner,
)
from backend.commands.combat_executor import CombatExecutor
from backend.commands.executor import CommandExecutor
from backend.game_logic.dispatch import (
    HEADLINE_WEIGHTS,
    STANDING_HEADLINE_CLASSES,
    build_morning_dispatch,
)
from backend.models.intel import FULL, PARTIAL, UNKNOWN
from backend.models.world_state import WorldState

EUROPE = "godot-client/project-sovereign/assets/maps/europe_1805.json"


def _europe():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(EUROPE)


def _cmd(marshal, action, target, **extra):
    out = {"command": {"marshal": marshal, "action": action, "target": target}}
    out.update(extra)
    return out


@pytest.fixture(autouse=True)
def _levers_up():
    """Every test states the arm it wants; restore the shipped values after."""
    floor = CombatExecutor.GARRISON_LOSS_FLOOR_READS_THE_GARRISON
    record = CombatExecutor.THE_GARRISON_ASSAULT_IS_RECORDED
    yield
    CombatExecutor.GARRISON_LOSS_FLOOR_READS_THE_GARRISON = floor
    CombatExecutor.THE_GARRISON_ASSAULT_IS_RECORDED = record


# ══════════════════════════════════════════════════════════════════════
# FA-D28 — the floor reads the garrison
# ══════════════════════════════════════════════════════════════════════

class TestTheGarrisonFloorReadsTheGarrison:
    """Ruling 2. The minimum-loss floor is a fraction of the DEFENDER's
    strength, so it can no longer tax a corps for being large."""

    def _grind(self, lever, garrison, attacker_strength):
        """Assaults to clear a detachment garrison, and what it cost.

        The legacy 19-region world, because that is where the existing
        garrison pins live and where the row's own numbers were measured.
        """
        CombatExecutor.GARRISON_LOSS_FLOOR_READS_THE_GARRISON = lever
        with contextlib.redirect_stdout(io.StringIO()):
            world = WorldState()
            ex = CommandExecutor()
            gs = {"world": world}
            for m in world.marshals.values():
                if m.nation == "France":
                    m.location = "Bordeaux"
            paris = world.get_region("Paris")
            paris.garrison_strength = garrison
            paris.garrison_detachment = True     # fights to destruction
            paris.buildings = []
            wellington = world.marshals["Wellington"]
            wellington.location = "Belgium"
            wellington.strength = attacker_strength
            before = wellington.strength
            assaults = 0
            while (paris.garrison_strength > 0 and wellington.strength > 0
                   and assaults < 300):
                world.actions_remaining = 99
                wellington.attacks_this_turn = 0
                wellington.in_combat_this_turn = False
                ex.execute(_cmd("Wellington", "attack", "Paris"), gs)
                assaults += 1
            return assaults, before - wellington.strength

    @pytest.mark.parametrize("garrison", [3000, 12000, 25000])
    def test_the_attacker_no_longer_loses_more_men_than_the_garrison_had(
            self, garrison):
        """FA-D28's own complaint, on its own three cases.

        Measured on the shipped tree, a 40,000-man corps against a
        detachment of 3,000 / 12,000 / 25,000:

            garrison   assaults   attacker lost (before -> after)
               3,000       13        10,234 ->  2,942
              12,000       15        14,156 ->  8,180
              25,000       16        20,184 -> 15,962

        The ASSAULT COUNT is deliberately unchanged: the ruling took the
        loss half of FA-D28's fix shape and not the odds-scaling half.
        """
        n_before, lost_before = self._grind(False, garrison, 40000)
        n_after, lost_after = self._grind(True, garrison, 40000)

        # The defect, stated as the row states it.
        if garrison < 25000:
            assert lost_before > garrison, (
                "the pre-slice arm is supposed to reproduce the absurdity")
        assert lost_after < garrison, (
            f"a 40,000-man corps still loses {lost_after:,} men clearing a "
            f"{garrison:,}-man garrison")
        assert lost_after < lost_before

        # The ruling did not touch the grind's LENGTH, and saying so here
        # keeps a future reader from thinking it did.
        assert n_after == n_before

    def test_the_floor_still_binds_for_a_weak_attacker(self):
        """The anti-stalemate promise this line was written for is kept
        from the side it actually matters on. A small corps assaulting a
        big garrison pays MORE than before, not less."""
        CombatExecutor.GARRISON_LOSS_FLOOR_READS_THE_GARRISON = False
        before = self._one_assault(25000, 1000)
        CombatExecutor.GARRISON_LOSS_FLOOR_READS_THE_GARRISON = True
        after = self._one_assault(25000, 1000)
        assert after > before, (
            "the floor must still bite when the DEFENDER is the strong side")

    def _one_assault(self, garrison, attacker_strength, must_hold=True):
        """One assault; returns what the attacker paid for it.

        `must_hold` is not decoration. If the garrison COLLAPSES the corps
        marches in and takes movement attrition, and this function measures
        a strength delta — so a case that quietly slid onto the capture path
        would be measuring the march, not the assault. An earlier draft of
        the lever pin did exactly that and read 14,820 for an assault that
        cost 5,000.
        """
        with contextlib.redirect_stdout(io.StringIO()):
            world = WorldState()
            ex = CommandExecutor()
            gs = {"world": world}
            for m in world.marshals.values():
                if m.nation == "France":
                    m.location = "Bordeaux"
            paris = world.get_region("Paris")
            paris.garrison_strength = garrison
            paris.buildings = []
            wellington = world.marshals["Wellington"]
            wellington.location = "Belgium"
            wellington.strength = attacker_strength
            before = wellington.strength
            ex.execute(_cmd("Wellington", "attack", "Paris"), gs)
            if must_hold:
                assert paris.controller == "France", (
                    "fixture slid onto the capture path — the number below "
                    "would be march attrition, not the assault")
            return before - wellington.strength

    def test_the_fight_still_terminates_against_a_single_defender(self):
        """A 40,000-man corps taking literally no casualties from a
        one-man garrison is the correct answer, not a stalemate — WO-3's
        `+1` on the DEFENDER's floor is what guarantees progress, and this
        pins that the attacker's floor was never load-bearing for it."""
        CombatExecutor.GARRISON_LOSS_FLOOR_READS_THE_GARRISON = True
        n, _lost = self._grind(True, 1, 40000)
        assert n == 1, "one landed assault must finish a one-man garrison"

    def test_the_lever_down_restores_the_attacker_s_own_strength(self):
        """Arm 0. `False` reproduces the pre-slice rule exactly — the floor
        is 2% of the ATTACKER's own strength."""
        # The old floor binds only above ~12.5x effective over-match, which
        # is the whole finding — so the case has to be that lopsided before
        # the two arms can differ at all. Paris is urban (+0.20 terrain), so
        # 250,000 men against 10,000 give an effective 12,000 to beat: the
        # proportional loss is 3,000 while the attacker's own 2% floor is
        # 5,000. The garrison halves to exactly 5,000 and HOLDS, so nothing
        # but the assault is being measured.
        CombatExecutor.GARRISON_LOSS_FLOOR_READS_THE_GARRISON = False
        assert self._one_assault(10000, 250000) == 5000
        CombatExecutor.GARRISON_LOSS_FLOOR_READS_THE_GARRISON = True
        # Same case, garrison-based floor 200 — the proportional term wins.
        assert self._one_assault(10000, 250000) == 3000

    def test_the_floor_is_single_sourced_and_both_boards_inherit_it(self):
        """GR5 by construction: exactly two call sites reach the resolver,
        and neither re-implements the arithmetic."""
        import pathlib
        root = pathlib.Path(__file__).resolve().parents[1]
        callers = []
        for path in (root / "backend").rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                if "_resolve_garrison_combat(" in line and "def " not in line:
                    callers.append((path.name, line.strip()))
        names = sorted({c[0] for c in callers})
        assert names == ["combat_executor.py", "naval_executor.py"], (
            f"a third caller appeared: {callers}")
        # And nobody else computes the floor.
        floor_sites = []
        for path in (root / "backend").rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="replace")
            if "GARRISON_ASSAULT_LOSS_FLOOR" in text:
                floor_sites.append(path.name)
        assert sorted(floor_sites) == ["combat_executor.py"]


    def test_the_levers_ship_up(self):
        """Every other test in this file states the arm it wants, so nothing
        else pins what the game actually SHIPS with. Measured: mutating the
        class default read INERT until this existed."""
        assert CombatExecutor.GARRISON_LOSS_FLOOR_READS_THE_GARRISON is True
        assert CombatExecutor.THE_GARRISON_ASSAULT_IS_RECORDED is True
        assert CombatExecutor.GARRISON_ASSAULT_LOSS_FLOOR == 0.02


# ══════════════════════════════════════════════════════════════════════
# FA-R5 — the assault goes on the record
# ══════════════════════════════════════════════════════════════════════

def _enemy_assaults_paris(fortify=False, garrison=25000, attacker=60000):
    """Austria's Mack throws himself at the French capital's garrison.

    Returns (world, result, the rows the assault added to `event_log`).
    """
    world = _europe()
    ex = CommandExecutor()
    paris = world.get_region("Paris")
    paris.garrison_strength = garrison
    paris.garrison_detachment = False
    if fortify:
        paris.buildings.append({"type": "fortification", "damaged": False})
    for m in world.marshals.values():
        if m.location == "Paris":
            m.location = "Burgundy"
    mack = world.marshals["Mack"]
    mack.location = paris.adjacent_regions[0]
    mack.strength = attacker
    before = len(world.event_log)
    with contextlib.redirect_stdout(io.StringIO()):
        result = ex.execute(
            _cmd("Mack", "attack", "Paris", is_ai_command=True),
            {"world": world})
    return world, result, world.event_log[before:]


class TestTheAssaultGoesOnTheRecord:
    """FA-R5. The two dark exits — the works holding, and the garrison
    destroyed into an occupation — now leave a trace."""

    def test_a_held_assault_on_our_own_capital_is_logged_and_briefed(self):
        """The measured case. Before this, `event_log` gained nothing, the
        campaign log showed nothing, the headline was None and the note
        read 'Your armies stand ready, Sire. The initiative is ours.' —
        the word 'Paris' appeared in the whole dispatch ZERO times."""
        CombatExecutor.THE_GARRISON_ASSAULT_IS_RECORDED = True
        world, _result, delta = _enemy_assaults_paris()

        assert [e["type"] for e in delta] == ["garrison_assault"]
        row = delta[0]
        assert row["held"] is True
        assert row["defender_nation"] == "France"
        assert row["attacker_nation"] == "Austria"
        assert row["region"] == "Paris"
        assert row["attacker_losses"] > 0
        assert row["garrison_losses"] > 0

        # It survives the fog filter as OUR news, and says what happened.
        rows = filter_campaign_log(delta, world)
        assert len(rows) == 1
        line = format_event_oneliner(rows[0])
        assert "Paris" in line
        assert f"{row['garrison_losses']:,}" in line
        assert f"{row['attacker_losses']:,}" in line

        # And it reaches the morning briefing.
        world.current_turn += 1
        with contextlib.redirect_stdout(io.StringIO()):
            dispatch = build_morning_dispatch(world)
        headline = dispatch.get("headline")
        assert headline is not None
        assert headline["class"] == "garrison_held"
        assert "Paris" in headline["text"]
        assert dispatch.get("berthier_note") != (
            "Your armies stand ready, Sire. The initiative is ours.")

    def test_the_occupation_exit_is_the_one_with_nothing_behind_it(self):
        """The fortified fall. There is no `region_captured` on this path —
        the province has not changed hands yet — so this row is the ONLY
        record that the garrison died at all."""
        CombatExecutor.THE_GARRISON_ASSAULT_IS_RECORDED = True
        world, result, delta = _enemy_assaults_paris(
            fortify=True, garrison=5200)

        assert result.get("occupation_started") is True
        assert [e["type"] for e in delta] == ["garrison_assault"]
        assert delta[0]["held"] is False
        assert "region_captured" not in [e["type"] for e in delta]

        world.current_turn += 1
        with contextlib.redirect_stdout(io.StringIO()):
            dispatch = build_morning_dispatch(world)
        headline = dispatch.get("headline")
        assert headline is not None
        assert headline["class"] == "garrison_stormed"

    def test_the_lever_down_writes_nothing_on_either_dark_exit(self):
        """Arm 0, both paths."""
        CombatExecutor.THE_GARRISON_ASSAULT_IS_RECORDED = False
        _world, _r, held = _enemy_assaults_paris()
        assert held == []
        _world, r2, fell = _enemy_assaults_paris(fortify=True, garrison=5200)
        assert r2.get("occupation_started") is True
        assert fell == []

    def test_a_third_partys_siege_needs_eyes_on_the_province(self):
        """The ambient board produces one — Austria against the Kingdom of
        Italy at Milan on turn 10 — and without an arm the filter's DROP
        default swallowed it. PARTIAL is enough: a garrison figure is a
        coarser fact than a field battle's order of march."""
        world = _europe()
        event = {
            "type": "garrison_assault", "marshal": "ArchdukeCharles",
            "attacker_nation": "Austria", "defender_nation": "KingdomOfItaly",
            "region": "Milan", "garrison_before": 10000,
            "garrison_losses": 5000, "garrison_remaining": 5000,
            "attacker_losses": 2645, "held": True, "turn": 10,
        }
        seen = {}
        for visibility in (UNKNOWN, PARTIAL, FULL):
            world.get_region_intel("Milan").visibility = visibility
            seen[visibility] = len(filter_campaign_log([event], world))
        assert seen == {UNKNOWN: 0, PARTIAL: 1, FULL: 1}

    def test_our_own_assault_abroad_is_ours_regardless_of_fog(self):
        """`_is_player_event` reads `attacker_nation`, which the producer
        stamps — so the player never loses sight of his own escalade."""
        world = _europe()
        event = {
            "type": "garrison_assault", "marshal": "Ney",
            "attacker_nation": "France", "defender_nation": "Austria",
            "region": "Bohemia", "garrison_before": 9000,
            "garrison_losses": 4500, "garrison_remaining": 4500,
            "attacker_losses": 900, "held": True, "turn": 5,
        }
        world.get_region_intel("Bohemia").visibility = UNKNOWN
        assert len(filter_campaign_log([event], world)) == 1

    def test_our_own_assault_abroad_never_becomes_a_headline(self):
        """Both classes are WOUND classes, gated on the player being the
        DEFENDER. A French success is the triumph ladder's business and
        composing one here would re-open CA8-D6."""
        world = _europe()
        world.log_event({
            "type": "garrison_assault", "marshal": "Ney",
            "attacker_nation": "France", "defender_nation": "Austria",
            "region": "Bohemia", "garrison_before": 9000,
            "garrison_losses": 4500, "garrison_remaining": 4500,
            "attacker_losses": 900, "held": True,
        })
        world.current_turn += 1
        with contextlib.redirect_stdout(io.StringIO()):
            dispatch = build_morning_dispatch(world)
        headline = dispatch.get("headline")
        assert headline is None or headline["class"] not in (
            "garrison_held", "garrison_stormed")

    def test_several_assaults_on_one_town_are_one_siege(self):
        """CA8-5's rule: identity is the PROVINCE, so three assaults on one
        town in one enemy phase do not eat three headline slots."""
        world = _europe()
        # The figures MUST differ across the three rows. A real siege
        # produces different numbers each assault, and an identity keyed on
        # anything but the province would still collapse three IDENTICAL
        # rows into one — so a fixture that repeats itself cannot tell a
        # correct identity from a wrong one. (Measured: with identical rows
        # the mutation that keys identity on the besieger read INERT.)
        for i in range(3):
            world.log_event({
                "type": "garrison_assault",
                "marshal": ["Mack", "Mack", "ArchdukeCharles"][i],
                "attacker_nation": "Austria", "defender_nation": "France",
                "region": "Paris", "garrison_before": 25000 - i * 6000,
                "garrison_losses": 6000 - i * 500,
                "garrison_remaining": 19000 - i * 6000,
                "attacker_losses": 3000 + i * 250, "held": True,
            })
        world.current_turn += 1
        with contextlib.redirect_stdout(io.StringIO()):
            dispatch = build_morning_dispatch(world)
        texts = [dispatch.get("headline", {}).get("text", "")]
        texts += [b.get("text", "") for b in (dispatch.get("sub_beats") or [])]
        assert sum(1 for t in texts if "Paris holds" in t) == 1

    def test_the_new_classes_are_not_standing(self):
        """A state-derived class in STANDING_HEADLINE_CLASSES repeats and
        buries everything else — PC-7's `marshal_reversal` trap. These are
        current news."""
        assert "garrison_held" not in STANDING_HEADLINE_CLASSES
        assert "garrison_stormed" not in STANDING_HEADLINE_CLASSES

    def test_a_stormed_capital_still_leads_with_its_fall(self):
        """Weights, stated as an outcome rather than as a number: the
        province actually changing hands (100) outranks the assault that
        took it (87)."""
        assert HEADLINE_WEIGHTS["capital_lost"] > (
            HEADLINE_WEIGHTS["garrison_stormed"])
        assert (HEADLINE_WEIGHTS["garrison_stormed"]
                > HEADLINE_WEIGHTS["own_mauled"])
        # The held case must out-rank the vaguer, later presence reading it
        # used to be silently replaced by.
        assert (HEADLINE_WEIGHTS["garrison_held"]
                > HEADLINE_WEIGHTS["enemy_on_our_soil"])

    def test_the_type_is_registered_everywhere_it_has_to_be(self):
        """The three enforcement families the whitelist drags along."""
        assert "garrison_assault" in CAMPAIGN_LOG_TYPES
        assert CATEGORY_MAP["garrison_assault"] == "combat"
        rendered = format_event_oneliner({
            "type": "garrison_assault", "marshal": "Mack",
            "attacker_nation": "Austria", "region": "Paris",
            "garrison_losses": 1, "garrison_remaining": 2,
            "attacker_losses": 3, "held": True, "turn": 1,
        })
        assert not rendered.startswith("Event: ")


# ══════════════════════════════════════════════════════════════════════
# FA-N77 — a prisoner is not a field marshal
# ══════════════════════════════════════════════════════════════════════

class TestLastMarshalProtectionCountsOnlyTheStanding:

    def _france_reduced_to(self, keep):
        world = _europe()
        with contextlib.redirect_stdout(io.StringIO()):
            for m in list(world.marshals.values()):
                if m.nation == world.player_nation and m.name != keep:
                    world.capture_marshal(m, "Austria")
        return world

    def test_the_last_standing_marshal_may_not_be_dismissed(self):
        """Measured on the shipped board: with every French marshal but
        Lannes a prisoner, `get_marshals_by_nation` returned 1 while
        `get_field_marshals` returned 8, and the audience offered
        `dismiss` on the only man France had left."""
        from backend.commands.disobedience import DisobedienceSystem
        world = self._france_reduced_to("Lannes")
        standing = [m.name for m in world.marshals.values()
                    if m.nation == world.player_nation and m.strength > 0]
        assert standing == ["Lannes"]
        assert [m.name for m in world.get_field_marshals()] == ["Lannes"]

        lannes = world.marshals["Lannes"]
        lannes.trust.modify(-100)
        with contextlib.redirect_stdout(io.StringIO()):
            event = DisobedienceSystem().check_redemption_threshold(
                lannes, world)
        assert event is not None
        offered = [o["id"] for o in event["options"]]
        assert offered == ["grant_autonomy"], offered

    def test_two_standing_marshals_still_get_all_three_courses(self):
        """The negative control: the fix must not be satisfiable by
        breaking the option builder for everyone."""
        from backend.commands.disobedience import DisobedienceSystem
        world = _europe()
        with contextlib.redirect_stdout(io.StringIO()):
            keep = {"Lannes", "Ney"}
            for m in list(world.marshals.values()):
                if m.nation == world.player_nation and m.name not in keep:
                    world.capture_marshal(m, "Austria")
        lannes = world.marshals["Lannes"]
        lannes.trust.modify(-100)
        with contextlib.redirect_stdout(io.StringIO()):
            event = DisobedienceSystem().check_redemption_threshold(
                lannes, world)
        assert set(o["id"] for o in event["options"]) == {
            "grant_autonomy", "administrative_role", "dismiss"}

    def test_the_administrative_clause_is_still_needed_beside_it(self):
        """`strength > 0` is ADDITIVE, not a replacement: an administrative
        marshal is at strength 0 too, and the two clauses say different
        things."""
        world = _europe()
        ney = world.marshals["Ney"]
        # The state only the ADMINISTRATIVE clause excludes: a man at the
        # desk who still has men on the books. The debug restore writes
        # `administrative` and `administrative_strength` as a pair and the
        # recall path will too, so this is constructible — and without it
        # the two clauses cannot be told apart by a test.
        ney.administrative = True
        ney.strength = 5000
        assert "Ney" not in [m.name for m in world.get_field_marshals()]
        # The state only the STRENGTH clause excludes: a prisoner.
        ney.administrative = False
        ney.strength = 0
        ney.captured_by = "Austria"
        assert "Ney" not in [m.name for m in world.get_field_marshals()]
        # And a standing field marshal is neither.
        ney.captured_by = ""
        ney.strength = 1000
        assert "Ney" in [m.name for m in world.get_field_marshals()]


# ══════════════════════════════════════════════════════════════════════
# FA-N76 — the answer must be one the audience offered
# ══════════════════════════════════════════════════════════════════════

class TestTheRedemptionAnswerMustBeOffered:

    def _audience(self, world, marshal_name):
        from backend.commands.disobedience import DisobedienceSystem
        marshal = world.marshals[marshal_name]
        marshal.trust.modify(-100)
        with contextlib.redirect_stdout(io.StringIO()):
            return DisobedienceSystem(), DisobedienceSystem(
            ).check_redemption_threshold(marshal, world)

    def test_an_unoffered_course_is_refused_and_costs_nothing(self):
        """The headline: `dismiss` was accepted when the audience offered
        `grant_autonomy` alone. The refusal must also leave the question
        standing — the old invalid-choice arm cleared the latch and stamped
        the cooldown BEFORE it refused."""
        from backend.commands.disobedience import DisobedienceSystem
        world = _europe()
        with contextlib.redirect_stdout(io.StringIO()):
            for m in list(world.marshals.values()):
                if m.nation == world.player_nation and m.name != "Lannes":
                    world.capture_marshal(m, "Austria")
        system = DisobedienceSystem()
        lannes = world.marshals["Lannes"]
        lannes.trust.modify(-100)
        with contextlib.redirect_stdout(io.StringIO()):
            event = system.check_redemption_threshold(lannes, world)
        assert [o["id"] for o in event["options"]] == ["grant_autonomy"]

        with contextlib.redirect_stdout(io.StringIO()):
            result = system.handle_redemption_response(
                event, "dismiss", {"world": world})
        assert result["success"] is False
        assert "Lannes" in world.marshals
        assert lannes.redemption_pending is True
        assert getattr(lannes, "redemption_cooldown_until", 0) == 0

    def test_an_offered_course_still_works(self):
        """The negative control — the guard must not refuse everything."""
        from backend.commands.disobedience import DisobedienceSystem
        world = _europe()
        system = DisobedienceSystem()
        ney = world.marshals["Ney"]
        ney.trust.modify(-100)
        with contextlib.redirect_stdout(io.StringIO()):
            event = system.check_redemption_threshold(ney, world)
            result = system.handle_redemption_response(
                event, "grant_autonomy", {"world": world})
        assert result["success"] is True

    def test_the_lever_down_accepts_an_unoffered_course_again(self):
        """Arm 0."""
        from backend.commands import disobedience as D
        world = _europe()
        with contextlib.redirect_stdout(io.StringIO()):
            for m in list(world.marshals.values()):
                if m.nation == world.player_nation and m.name != "Lannes":
                    world.capture_marshal(m, "Austria")
        system = D.DisobedienceSystem()
        lannes = world.marshals["Lannes"]
        lannes.trust.modify(-100)
        with contextlib.redirect_stdout(io.StringIO()):
            event = system.check_redemption_threshold(lannes, world)
        original = D.REDEMPTION_ANSWER_MUST_BE_OFFERED
        D.REDEMPTION_ANSWER_MUST_BE_OFFERED = False
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                result = system.handle_redemption_response(
                    event, "dismiss", {"world": world})
            assert result["success"] is True
        finally:
            D.REDEMPTION_ANSWER_MUST_BE_OFFERED = original


# ══════════════════════════════════════════════════════════════════════
# FA-N46 — a rente-paid marshal keeps his grace window
# ══════════════════════════════════════════════════════════════════════

def _tick(world, n=1):
    for _ in range(n):
        world.current_turn += 1
        with contextlib.redirect_stdout(io.StringIO()):
            world._process_dotation_state()


class TestTheRentePayerKeepsHisGraceWindow:
    """WO-18 froze the clock so a grant/revoke toggle could not dodge
    erosion. Its safety argument stopped being true the moment the marshal
    WON AGAIN: the expectation rose, the branch flipped to unmet, and
    `elapsed` was measured against an anchor several turns stale."""

    def _paid_and_frozen(self):
        from backend.game_logic import dotation as DOT
        world = _europe()
        marshal = world.marshals["Lannes"]
        marshal.battles_won = 1
        _tick(world)                       # the clock opens
        assert marshal.expectation_grace_turn >= 0
        marshal.pension = DOT.compute_rente_face(marshal, world)
        _tick(world)                       # met — FROZEN, not reset
        return world, marshal

    def test_a_new_victory_re_opens_the_window(self):
        """The defect. Measured before: `eroding True` on the first turn of
        the new shortfall and trust already falling 85 -> 83."""
        from backend.game_logic import dotation as DOT
        world, marshal = self._paid_and_frozen()
        assert marshal.expectation_grace_turn >= 0, (
            "the clock is supposed to be frozen here, not reset")
        _tick(world, 5)                    # quiet, fully-paid turns
        trust_before = marshal.trust.value
        marshal.battles_won = 3            # he wins again
        _tick(world)
        assert DOT.is_eroding(marshal, world) is False
        assert marshal.trust.value == trust_before
        assert marshal.expectation_grace_turn == world.current_turn
        assert marshal.expectation_covered_at_freeze == -1

    def test_the_churn_dodge_still_erodes(self):
        """WO-18's own case, unchanged: the payment STOPPED, so the frozen
        anchor stands and erosion resumes at once."""
        from backend.game_logic import dotation as DOT
        world, marshal = self._paid_and_frozen()
        _tick(world, 5)
        trust_before = marshal.trust.value
        marshal.pension = 0                # revoked — the dodge
        _tick(world)
        assert DOT.is_eroding(marshal, world) is True
        assert marshal.trust.value < trust_before

    def test_the_stamp_is_cleared_when_the_estate_covers_him(self):
        """Paying with LAND is durable: the clock resets and nothing is
        left frozen to be read against a later shortfall."""
        world, marshal = self._paid_and_frozen()
        region = next(r for r in world.regions.values()
                      if r.controller == "France" and not r.is_capital)
        region.stability = 100
        region.income_value = max(region.income_value, 400)
        marshal.dotation_regions = [region.name]
        _tick(world)
        assert marshal.expectation_grace_turn == -1
        assert marshal.expectation_covered_at_freeze == -1

    def test_the_re_opened_window_is_one_shot(self):
        """A genuinely neglected marshal still erodes on time — the restart
        consumes the stamp, so the next unmet turn measures an ordinary
        running clock rather than restarting forever."""
        from backend.game_logic import dotation as DOT
        world, marshal = self._paid_and_frozen()
        marshal.battles_won = 3
        _tick(world)                       # the window re-opens
        opened = marshal.expectation_grace_turn
        _tick(world, DOT.GRACE_TURNS + 1)  # and is never topped up again
        assert marshal.expectation_grace_turn == opened
        assert DOT.is_eroding(marshal, world) is True

    def test_an_old_save_reads_no_frozen_clock(self):
        """Save-compat: absent -> -1, which is how pre-slice saves behaved."""
        from backend.models.marshal import Marshal
        world = _europe()
        data = world.marshals["Lannes"].to_dict()
        assert "expectation_covered_at_freeze" in data
        del data["expectation_covered_at_freeze"]
        restored = Marshal.from_dict(data)
        assert restored.expectation_covered_at_freeze == -1


# ══════════════════════════════════════════════════════════════════════
# FA-R3 — a standing order is priced by the ORDER
# ══════════════════════════════════════════════════════════════════════

def _drive(sentence, ap=None):
    """POST /command on a fresh 1805 board; returns (before, after, orders)."""
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(EUROPE)
        M.world = world
        M.game_state["world"] = world
        M.parser = CommandParser(use_real_llm=False)
        if ap is not None:
            world.actions_remaining = ap
        client = TestClient(M.app)
        before = world.actions_remaining
        data = client.post("/command", json={"command": sentence}).json()
        after = M.world.actions_remaining
        orders = sum(1 for m in M.world.marshals.values()
                     if m.nation == M.world.player_nation
                     and getattr(m, "strategic_order", None) is not None)
    return before, after, orders, bool(data.get("success"))


class TestAStandingOrderIsPricedByTheOrder:
    """Ruling 5. `free_actions` is a list of BASE actions; the mock chain's
    WAIT arm sits above hold/move, so any sentence that also says "wait"
    parsed to a free verb and bypassed both the AP pre-gate and the charge.

    Pin `world.actions_remaining`, never `action_info["cost"]` — the charge
    loop overwrites `action_result` each iteration, so a 2-AP action reports
    a cost of 1.
    """

    @pytest.mark.parametrize("sentence", [
        "Davout, hold Rhineland and wait",
        "Ney, march to Lorraine and wait there",
        "Davout, support Ney and wait",
        "Ney, wait, march to Lorraine",
        "Davout, hold Rhineland, wait for orders",
        "Davout, support Ney and stand by",
        "Ney, march to Lorraine and wait for reinforcements",
    ])
    def test_the_order_is_charged(self, sentence):
        """Seven shapes, not the two the row names — and it is not a
        trailing suffix: a LEADING wait fires too."""
        before, after, orders, _ok = _drive(sentence)
        assert before - after == 2, sentence
        assert orders == 1, sentence

    @pytest.mark.parametrize("sentence", [
        "Soult, hold Lorraine and wait",       # literal
        "Napoleon, hold Lorraine and wait",    # sovereign
    ])
    def test_the_one_ap_tiers_are_honoured(self, sentence):
        """`Marshal.strategic_order_ap` was never consulted, so the
        literal's and the sovereign's discount was bypassed too."""
        before, after, orders, _ok = _drive(sentence)
        assert before - after == 1, sentence
        assert orders == 1, sentence

    @pytest.mark.parametrize("sentence", [
        "withdraw from the alliance",
        "fall back south",
        "withdraw south",
        "Ney, fall back south",
        "Ney, withdraw south",
        "Ney, fall back and observe Mack",
    ])
    def test_a_retreat_is_still_free(self, sentence):
        """The regression this slice shipped and then caught. `retreat` is
        the one entry in `free_actions` with its own design comment, and six
        phrasings parse `retreat` WITH a strategic type."""
        before, after, _orders, ok = _drive(sentence)
        assert before == after, sentence
        assert ok is True, sentence

    @pytest.mark.parametrize("sentence", [
        "withdraw from the alliance",
        "Ney, fall back south",
    ])
    def test_a_retreat_still_works_at_zero_ap(self, sentence):
        """The arm that makes the exemption matter: retreat exists for the
        moment you are out of options, and the first cut refused it exactly
        then with "Not enough actions! Need 2, have 0"."""
        _before, _after, _orders, ok = _drive(sentence, ap=0)
        assert ok is True, sentence

    @pytest.mark.parametrize("sentence", [
        "Ney, march to Lorraine and wait there",
        "Davout, hold Rhineland and wait",
    ])
    def test_the_bypass_is_refused_at_zero_ap(self, sentence):
        """The pre-gate, not merely the charge. Before this, a player with a
        spent turn could set every standing order AND move the army one hop.
        The order must not be created."""
        _before, _after, orders, ok = _drive(sentence, ap=0)
        assert ok is False, sentence
        assert orders == 0, sentence

    @pytest.mark.parametrize("sentence,cost", [
        ("Davout, hold Rhineland", 2),
        ("Soult, hold Lorraine", 1),
        ("Napoleon, hold Lorraine", 1),
        ("Davout, wait", 0),
        ("wait for reinforcements", 0),
    ])
    def test_the_controls_are_unchanged(self, sentence, cost):
        before, after, _orders, _ok = _drive(sentence)
        assert before - after == cost, sentence

    def test_the_lever_down_restores_the_free_ride(self):
        """Arm 0."""
        from backend.commands import executor as E
        original = E.STRATEGIC_ORDERS_ARE_PRICED_BY_THE_ORDER
        E.STRATEGIC_ORDERS_ARE_PRICED_BY_THE_ORDER = False
        try:
            before, after, orders, _ok = _drive(
                "Davout, hold Rhineland and wait")
            assert before == after
            assert orders == 1, "the pre-slice defect: an order for nothing"
        finally:
            E.STRATEGIC_ORDERS_ARE_PRICED_BY_THE_ORDER = original


# ══════════════════════════════════════════════════════════════════════
# FA-R4 — the desk may be addressed
# ══════════════════════════════════════════════════════════════════════

class TestTheDeskMayBeAddressed:

    @pytest.mark.parametrize("sentence", [
        "Berthier, end turn", "Sire, end turn", "Berthier, next turn",
        "Berthier: end turn", "berthier , end turn",
    ])
    def test_an_addressed_end_turn_ends_the_turn(self, sentence):
        import backend.main as M
        from backend.ai.clause_guards import is_bare_end_turn
        assert is_bare_end_turn(sentence) is True
        _drive(sentence)
        assert M.world.current_turn == 2, sentence

    @pytest.mark.parametrize("sentence", [
        "what happens next turn",
        "Davout, fortify until next turn",
        "end the turn",
        "Ney, hold Bavaria until the end turn",
        "Berthier, Sire, end turn",
        "Berthier, status",
        "Ney, end turn",
    ])
    def test_the_fa6_controls_still_hold(self, sentence):
        """The vocabulary itself is untouched — this widens the ADDRESS, not
        the phrasing list, so every FA-6 narrowing survives."""
        from backend.ai.clause_guards import is_bare_end_turn
        assert is_bare_end_turn(sentence) is False, sentence

    def test_the_phrasing_vocabulary_is_still_the_same_three(self):
        from backend.ai.clause_guards import END_TURN_PHRASINGS
        assert END_TURN_PHRASINGS == ("end turn", "end_turn", "next turn")

    def test_the_backend_and_the_client_share_one_desk_vocabulary(self):
        """The client cannot import Python, so the parity is a pin. The
        client list is read out of `main.gd` and checked against the
        backend regex; if either grows an address the other lacks, this
        goes red."""
        import os
        import re
        from backend.ai.clause_guards import DESK_ADDRESS_RE
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, "godot-client", "project-sovereign",
                            "scripts", "main.gd")
        with open(path, encoding="utf-8") as handle:
            src = handle.read()
        helper = src[src.index("func _strip_desk_address("):]
        helper = helper[:helper.index("\n\n\nfunc ")]
        listed = re.search(r"for\s+\w+\s+in\s+\[([^\]]*)\]", helper)
        assert listed, "the client address vocabulary changed shape"
        client = sorted(re.findall(r'"([^"]+)"', listed.group(1)))
        assert client, "the client strips no addresses at all"
        for address in client:
            assert DESK_ADDRESS_RE.match(address + ", end turn"), address
        for address in ("berthier", "sire"):
            assert address in client, address
        # ONE address, not every address. The Python re-derivation in
        # `test_fa_slice1` cannot see this — it harvests the address LIST and
        # then strips once itself, so a client that recursed would slip past
        # it. Measured: that mutation read INERT until this assertion
        # existed. Stated as the shape the helper must have.
        assert "return rest.substr(1)" in helper, (
            "the client must RETURN after the first address it strips")
        assert helper.count("_strip_desk_address(") == 1, (
            "the client helper must not call itself — one address, not every "
            "address, or `Berthier, Sire, end turn` becomes an end turn")


# ══════════════════════════════════════════════════════════════════════
# FA-S7-D1 — a deed no action models is a question
# ══════════════════════════════════════════════════════════════════════

class TestADeedNoActionModelsIsAQuestion:

    def test_the_prompt_states_the_rule_under_valid_actions(self):
        """Ruling 7. The live twins are `live_only` and cost API calls, so
        the structural half is pinned here: the rule exists, and it sits in
        the Valid Actions block rather than somewhere the model may skim."""
        import inspect
        from backend.ai import prompt_builder
        src = inspect.getsource(prompt_builder)
        head = src.index("## Valid Actions")
        # Whitespace-normalised: the prompt is wrapped prose, so a phrase
        # that straddles a line break is still the phrase the model reads.
        block = " ".join(src[head:head + 900].split())
        assert "no listed action models" in block
        assert 'action "unknown"' in block
        assert "cover the retreat" in block and "fix bayonets" in block

    def test_the_two_live_twins_expect_a_refusal(self):
        """The corpus rows the ruling names. `action: "unknown"` was the
        ruling literal shape and it is NOT what the pipeline reports — an
        unknown falls back to the fast parser, so the observable is a
        refusal. Pinned as measured (4/4 LIVE, Sept 5 2026)."""
        import json
        import os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, "tests", "data",
                            "parser_golden_corpus.json")
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        rows = data["entries"] if isinstance(data, dict) else data
        twins = {r["id"]: r for r in rows if r["id"].startswith("fa73-live-")}
        assert len(twins) == 2, sorted(twins)
        for row in twins.values():
            assert row.get("live_only") is True
            assert row["expected"] == {"success": False}
