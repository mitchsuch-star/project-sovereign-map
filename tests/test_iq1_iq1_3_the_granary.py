"""IQ-1 IQ1-3 — "The Granary and the Alarm".

Row IQ-1's fourth slice, and it is NOT the retainer `docs/IMPROVEMENT_QUEUE_SPEC.md`
§0.6 recommended. The decision fleet drove the entire diplomacy-instrument
channel through the real executor at a 1,000,000-gold chest and it is worth
**4,824 gold, one-shot, for every buyable design in Europe** — 5.4% of the
disease chest — after which `coalition.get_qualifying_nations` is byte-identical.
A per-turn version of that cannot absorb tens of thousands at any honest price,
and its payoff has no consumer: `intent._derive_weight` never reads
`directed_sponsorships`, and `war_council`'s design coercion is AI-vs-AI only by
its own comment, so a retainer on a France-aimed design can never open.

What CAN absorb is the sink the row already landed, through three changes and a
set of surfaces:

**A — THE GRANARY OF AN ALLY.** `_execute_purchase_levy` refused on OWNERSHIP
while the engine's own supply decision — `world_state._supply_multiplier`, landed
as PC15-D2 "The Ally's Table" — already feeds a guest army on ALLIANCE /
DEFENSIVE_ALLIANCE / VASSAL soil at `HOME_SUPPLY_MULTIPLIER`, and
`dispatch.py`'s depot-remedy arm says so out loud on the identical fact. Two
seams, one question, opposite answers. All SIX own-soil refusals on the archived
spender arm (Munich ×1, Piedmont ×4, Franconia ×1) were on soil PC15-D2 feeds.

**A2** — and the moment the gate opened, `_calculate_recruit_cost`'s 25% capital
discount became newly reachable on an ALLY's capital, because that function never
read `region.controller`. A host's magazines feed your battalion; its treasury
does not subsidise your recruiting.

**B — THE BOUGHT MEN ARE NOT PUNISHED TWICE.** The designed premium is 15 points
below a draft. But the purchase path wrote a FLAT `LEVY_MORALE_BASE` while the
draft path reads `training_ground` (an absolute 70) and Moore's Shorncliffe
System (a floor of 60) — so the real gap was **45 and 35** at those rungs, and
the one counterweight a player can already BUY was void for substitutes.

**C — THE ALARM PRICES THE LEVY.** §0.2's own words: "priced by the threat the
player's own success creates". A frightened continent does not sell its sons
cheaply to the power frightening it.

MEASURED, receipts read at the executor and never a difference between boards
(script `commanded_spender40.json`, seed `historical`, `--diplomacy accept`,
40 turns):

    HEAD                     18,852 gold in  6 purchases · 24 provinces
    + A the granary          65,916 gold in 12 purchases · 26 provinces
    + A2 the host's price    67,572 gold in 12 purchases · 26 provinces
    + C the alarm            75,486 gold in 12 purchases · 26 provinces

**18,852 → 75,486 = 4.00×, and 85.2% of the 88,556-gold surplus** — with the
board ending BETTER, not worse, and the one surviving refusal on PRICE, which is
the market working.

⚠ §0.5.1 FINDING 1's causal sentence is STRUCK — see `TestTheDilutionStands`.
⚠ M1–M7 is structurally blind to every economy change (zero references to gold,
income, stability, upkeep or turn advance), so its greenness is not evidence
here. `BASELINE_SERIES` is the instrument.
"""

import ast
import json
import pathlib
import re

import pytest

from backend.commands import economy_executor as econ_mod
from backend.commands.economy_executor import (
    EconomyExecutor, region_feeds_nation, levy_alarm_multiplier,
    levy_substitute_price, levy_purchase_ceiling, substitute_arrival_morale,
    get_levy_status, LEVY_ALARM_ANCHOR, AI_CORPS_REGEN_CAP,
)
from backend.models.world_state import (
    WorldState, LEVY_MORALE_BASE, LEVY_MORALE_PREMIUM,
)

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
PANEL_GD = (REPO / "godot-client" / "project-sovereign" / "scripts"
            / "region_panel.gd")
DRIVER = REPO / "tools" / "playtest_driver.py"


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def gate_shut():
    before = econ_mod.LEVY_FEEDS_ON_ALLY_SOIL
    econ_mod.LEVY_FEEDS_ON_ALLY_SOIL = False
    yield
    econ_mod.LEVY_FEEDS_ON_ALLY_SOIL = before


@pytest.fixture
def alarm_off():
    before = econ_mod.THE_ALARM_PRICES_THE_LEVY
    econ_mod.THE_ALARM_PRICES_THE_LEVY = False
    yield
    econ_mod.THE_ALARM_PRICES_THE_LEVY = before


@pytest.fixture
def premium_flat():
    before = econ_mod.THE_SUBSTITUTE_IS_NOT_PUNISHED_TWICE
    econ_mod.THE_SUBSTITUTE_IS_NOT_PUNISHED_TWICE = False
    yield
    econ_mod.THE_SUBSTITUTE_IS_NOT_PUNISHED_TWICE = before


# ════════════════════════════════════════════════════════════════════════
# A. The granary of an ally
# ════════════════════════════════════════════════════════════════════════

class TestTheGranaryOfAnAlly:
    def test_the_predicate_feeds_own_soil_and_a_host(self, world):
        """Own soil, ALLIANCE, VASSAL — and the measured boot cases."""
        cases = {
            "Paris": True,        # own soil
            "Franconia": True,    # Bavaria, ALLIANCE
            "Milan": True,        # KingdomOfItaly, VASSAL
            "Swabia": True,       # Bavaria, ALLIANCE
        }
        for name, expected in cases.items():
            region = world.get_region(name)
            assert region is not None, f"{name} left the map"
            assert region_feeds_nation(world, "France", region) is expected, name

    def test_the_fixture_actually_contains_a_host(self, world):
        """Without this the test above could pass on a board where every
        province is French — it would be measuring nothing."""
        hosts = [r.name for r in world.regions.values()
                 if r.controller != "France"
                 and region_feeds_nation(world, "France", r)]
        assert hosts, "no ally-fed foreign soil on the board — re-check PC15-D2"
        assert len(hosts) >= 3, hosts

    def test_a_passage_right_is_not_a_granary(self, world):
        """The Ansbach line, and it holds for free: NON_AGGRESSION and
        OPEN_BORDERS are not in ALLY_SUPPLY_STATES, so neither state feeds."""
        assert "NON_AGGRESSION" not in world.ALLY_SUPPLY_STATES
        assert "OPEN_BORDERS" not in world.ALLY_SUPPLY_STATES
        region = next(r for r in world.regions.values()
                      if r.controller and r.controller != "France")
        from backend.game_logic.diplomacy import set_diplomatic_state
        for passage in ("NON_AGGRESSION", "OPEN_BORDERS"):
            set_diplomatic_state(world, "France", region.controller, passage)
            assert region_feeds_nation(world, "France", region) is False, passage

    def test_hostile_soil_still_refuses(self, world):
        enemy = next(r for r in world.regions.values()
                     if r.controller and world.is_at_war("France", r.controller))
        assert region_feeds_nation(world, "France", enemy) is False

    def test_the_gate_shut_reproduces_ownership_only(self, world, gate_shut):
        """The negative control: with the lever down the predicate is the bare
        ownership check that shipped, so the six archived refusals come back."""
        for name in ("Franconia", "Milan", "Swabia"):
            region = world.get_region(name)
            assert region_feeds_nation(world, "France", region) is False, name
        assert region_feeds_nation(world, "France",
                                   world.get_region("Paris")) is True

    def test_the_predicate_agrees_with_the_engines_own_supply_decision(self, world):
        """The point of extracting it. `_supply_multiplier` is the original
        home of this computation; if the two ever disagree on any province,
        the levy is refusing where the engine says the army is fed."""
        for region in world.regions.values():
            fed = region_feeds_nation(world, "France", region)
            multiplier = world._supply_multiplier("France", region)
            engine_fed = multiplier >= world.HOME_SUPPLY_MULTIPLIER
            assert fed == engine_fed, (
                f"{region.name}: predicate {fed} vs engine {engine_fed} "
                f"(multiplier {multiplier})")

    def test_no_third_copy_of_the_predicate_survives_in_the_levy(self):
        """A census over the seam, not over the file: the levy must decide
        through the helper, never through a bare controller comparison."""
        src = (REPO / "backend/commands/economy_executor.py").read_text(
            encoding="utf-8")
        tree = ast.parse(src)
        body = None
        for fn in ast.walk(tree):
            if (isinstance(fn, ast.FunctionDef)
                    and fn.name == "_execute_purchase_levy"):
                body = "\n".join(
                    src.splitlines()[fn.lineno - 1:fn.end_lineno])
        assert body is not None
        assert "region_feeds_nation(" in body
        # Scope to the GATE. `foreign_soil=(region.controller != acting_nation)`
        # legitimately reads the controller — that is the A2 sub-ruling, not a
        # second copy of the soil DECISION. The first cut of this pin failed on
        # exactly that, which is the right failure: a census must name the
        # thing, not a string that appears in the file.
        gate = body[:body.index("# CO-4's rule")]
        assert "region.controller != acting_nation" not in gate, (
            "the levy's GATE grew a second copy of the soil decision")
        assert "foreign_soil=(region.controller != acting_nation)" in body, (
            "the A2 sub-ruling's own read is gone")

    def test_the_ai_rung_reads_the_same_predicate(self):
        """GR5 in the DECISION layer. IQ1-1's own P1.25 rung shipped dead;
        a rung refused on soil the player is granted is the same class of
        defect one step out."""
        src = (REPO / "backend/ai/enemy_ai.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        body = None
        for fn in ast.walk(tree):
            if (isinstance(fn, ast.FunctionDef)
                    and fn.name == "_find_substitute_purchase"):
                body = "\n".join(
                    src.splitlines()[fn.lineno - 1:fn.end_lineno])
        assert body is not None
        assert "region_feeds_nation(" in body
        assert "region.controller != nation" not in body


class TestWhatTheGranaryActuallyBuys:
    """The behavioural half, on the geometry the ruling names.

    ⚠ PIN BERNADOTTE AT FRANCONIA, NOT MASSENA AT MILAN. Milan is
    KingdomOfItaly/VASSAL and `region_has_friendly_supply` is True on
    `region_type == "capital"`, so a purchase there needs a FULL batch —
    10,000 men against the establishment's 6,000 of room at boot — and is
    refused by the CEILING, not by the gate. A pin written on Milan would
    red while the fix works.
    """

    def _buy(self, world, marshal_name, batches=1):
        """SW-1's own drive idiom — the executor reads a NESTED `command`."""
        from backend.commands.executor import CommandExecutor
        ex = CommandExecutor()
        cmd = {"action": "purchase_levy", "marshal": marshal_name,
               "batches": batches, "type": "specific"}
        return ex.execute({"action": "purchase_levy", "command": cmd},
                          {"world": world})

    def test_franconia_is_a_field_purchase_and_it_succeeds(self, world):
        region = world.get_region("Franconia")
        assert region.controller == "Bavaria"
        assert world.get_diplomatic_state("France", "Bavaria") == "ALLIANCE"
        marshal = next(iter(m for m in world.marshals.values()
                            if m.nation == "France"))
        marshal.location = "Franconia"
        world.nation_gold["France"] = 60_000
        result = self._buy(world, marshal.name)
        assert result.get("success") is True, result.get("message")
        assert "substitutes into the line at Franconia" in result["message"]

    def test_the_same_purchase_is_refused_with_the_gate_shut(self, world, gate_shut):
        marshal = next(iter(m for m in world.marshals.values()
                            if m.nation == "France"))
        marshal.location = "Franconia"
        world.nation_gold["France"] = 60_000
        result = self._buy(world, marshal.name)
        assert result.get("success") is False
        assert "does not" in result["message"] or "do not hold" in result["message"]

    def test_the_refusal_names_who_holds_the_ground(self, world):
        """FA-54's class: a refusal must say which province and whose it is."""
        enemy_region = next(r for r in world.regions.values()
                            if r.controller
                            and world.is_at_war("France", r.controller))
        marshal = next(iter(m for m in world.marshals.values()
                            if m.nation == "France"))
        marshal.location = enemy_region.name
        world.nation_gold["France"] = 60_000
        result = self._buy(world, marshal.name)
        assert result.get("success") is False
        assert enemy_region.name in result["message"]
        assert enemy_region.controller in result["message"]


class TestTheHostsPriceIsNotDiscounted:
    def test_the_capital_discount_is_suppressed_on_foreign_soil(self, world):
        ex = EconomyExecutor(None)
        milan = world.get_region("Milan")
        assert milan.region_type == "capital", "fixture precondition"
        base = levy_substitute_price(world, "France")
        own = ex._calculate_recruit_cost(milan, world, base_cost=base,
                                        nation="France", foreign_soil=False)
        host = ex._calculate_recruit_cost(milan, world, base_cost=base,
                                         nation="France", foreign_soil=True)
        assert host > own, (
            "the host's capital is still discounting our recruiting")
        # The discount is 25%, so suppressing it is a 1/0.75 rise.
        assert host == pytest.approx(own / 0.75, rel=0.02)

    def test_every_existing_call_site_is_byte_identical_by_default(self, world):
        """`foreign_soil` defaults False, so the nine pre-existing callers
        cannot have moved. Asserted as a DEFAULT, not as nine call sites."""
        import inspect
        sig = inspect.signature(EconomyExecutor._calculate_recruit_cost)
        assert sig.parameters["foreign_soil"].default is False

    def test_it_only_touches_the_capital_branch(self, world):
        """A non-capital province must price identically either way, or the
        kwarg is doing more than the ruling sanctioned."""
        ex = EconomyExecutor(None)
        plain = next(r for r in world.regions.values()
                     if r.region_type != "capital" and r.controller == "France")
        base = levy_substitute_price(world, "France")
        a = ex._calculate_recruit_cost(plain, world, base_cost=base,
                                      nation="France", foreign_soil=False)
        b = ex._calculate_recruit_cost(plain, world, base_cost=base,
                                      nation="France", foreign_soil=True)
        assert a == b


# ════════════════════════════════════════════════════════════════════════
# B. The bought men are not punished twice
# ════════════════════════════════════════════════════════════════════════

class TestTheDilutionStands:
    """⚠ §0.5.1 FINDING 1's CAUSAL SENTENCE IS STRUCK, on the arithmetic.

    "A player in a good position who spends gold gets a bigger, weaker army
    and loses ground" was a CROSS-BOARD DIFFERENCE presented as a mechanism —
    the third occurrence of the error this row's own record strikes SW-1 and
    its review round for. Measured: 18 of 19 French battles are byte-identical
    across the arms and all five province losses were unopposed marches; and
    with 3.5× MORE substitutes the board ends on 26 provinces, not 22.

    The method rule this extends, and it is the useful part: A PROVINCE COUNT
    IS A BOARD DIFFERENCE TOO. Paired arms stop being an isolation at the
    first AI decision that reads the board.
    """

    def test_a_substitute_batch_always_adds_effective_strength(self, world):
        """The arithmetic that kills the "weaker" claim. Effective strength is
        `S × (0.5 + m/100)`-shaped, so adding `n` men at quality `q` changes it
        by `n × (0.5 + q/100)` — positive, and independent of the corps' own
        size and morale."""
        marshal = next(m for m in world.marshals.values()
                       if m.nation == "France")
        # ⚠ EFFECTIVE STRENGTH IS `strength x get_combat_effectiveness()`, not
        # the multiplier alone. The first cut of this pin compared MULTIPLIERS
        # and red (1.5 -> 1.29) — which is the multiplier correctly FALLING
        # while the product rises. Worth keeping in writing, because reading
        # that red as "the dilution is self-defeating after all" is precisely
        # the mistake §0.5.1 FINDING 1 made.
        before_strength = marshal.strength
        before = before_strength * marshal.get_combat_effectiveness()
        n, q = 9000, LEVY_MORALE_BASE   # the bare rung — the worst case
        old_m = marshal.morale
        marshal.morale = int((before_strength * old_m + n * q)
                             / (before_strength + n))
        marshal.strength = before_strength + n
        after = marshal.strength * marshal.get_combat_effectiveness()
        assert after > before, (
            f"effective strength fell: {before:,.0f} -> {after:,.0f} — if this "
            f"ever reds, FINDING 1's mechanism is real after all and the "
            f"ruling must be re-opened")
        # …and the multiplier FALLS, which is the dilution being real.
        assert marshal.get_combat_effectiveness() < (before / before_strength)

    def test_the_dilution_is_not_softened(self):
        """The ruling's own never-dos, pinned so a later slice cannot quietly
        soften what was measured correct."""
        assert LEVY_MORALE_BASE == 25
        assert LEVY_MORALE_PREMIUM == 15


class TestTheSubstituteIsNotPunishedTwice:
    class _Region:
        def __init__(self, training_ground, controller="France"):
            self._tg = training_ground
            self.controller = controller
            self.region_type = "capital"
            self.stability = 100
            self.name = "Probe"

        def has_building(self, building):
            return building == "training_ground" and self._tg

    def test_the_gap_is_the_premium_at_every_rung(self, world):
        """ONE assertion over all three rungs, stated as the DESIGN (the gap)
        rather than as three magic numbers."""
        moore = next((m for m in world.marshals.values()
                      if (getattr(m, "ability", {}) or {}).get("name")
                      == "Shorncliffe System"), None)
        assert moore is not None, "Moore left the roster — re-anchor this pin"
        rungs = [
            (self._Region(False), None, EconomyExecutor.RECRUIT_MORALE_BASE),
            (self._Region(True), None, EconomyExecutor.RECRUIT_MORALE_TRAINED),
            (self._Region(False), moore, 60),
        ]
        for region, marshal, draft_rung in rungs:
            arrived = substitute_arrival_morale(EconomyExecutor, region, marshal)
            assert arrived == draft_rung - LEVY_MORALE_PREMIUM, (
                f"rung {draft_rung}: substitute arrived at {arrived}, "
                f"expected {draft_rung - LEVY_MORALE_PREMIUM}")

    def test_the_trained_rung_is_55_and_emphatically_not_70(self, world):
        """The negative the ruling demands. Two candidate designs prescribed
        ONE shared ABSOLUTE arrival function, which would return the draft's
        70 for a substitute — BETTER than a bare draft's 40 — destroying the
        premium this exists to protect."""
        arrived = substitute_arrival_morale(
            EconomyExecutor, self._Region(True), None)
        assert arrived == 55
        assert arrived != EconomyExecutor.RECRUIT_MORALE_TRAINED
        assert arrived > LEVY_MORALE_BASE, (
            "the training ground must be WORTH something to a substitute")

    def test_the_bare_rung_is_byte_identical_to_the_shipped_value(self):
        assert substitute_arrival_morale(
            EconomyExecutor, self._Region(False), None) == LEVY_MORALE_BASE

    def test_the_premium_is_the_two_constants_it_claims_to_be(self):
        """A drift pin: the premium was promoted FROM the difference of two
        constants in two files, so it must stay equal to it."""
        assert (LEVY_MORALE_BASE
                == EconomyExecutor.RECRUIT_MORALE_BASE - LEVY_MORALE_PREMIUM)

    def test_a_driven_purchase_arrives_at_the_trained_rung(self, world):
        """⚠ WRITTEN BECAUSE A MUTATION CAME BACK INERT. Replacing
        `substitute_arrival_morale(...)` with the flat base inside
        `_execute_purchase_levy` killed nothing — because nothing DROVE a
        purchase in a training-ground province. The helper was pinned; the
        seam that consumes it was not.

        ⚠ And the fixture has to BUILD the training ground: the decision fleet
        censused all 126 boot provinces and the map holds ZERO of them, which
        is why the rungs are unreachable at boot and this is a pin about the
        WIRING, not about the shipped board.
        """
        from backend.commands.executor import CommandExecutor
        marshal = next(m for m in world.marshals.values()
                       if m.nation == "France")
        region = world.get_region(marshal.location)
        region.buildings.append({"type": "training_ground", "damaged": False})
        assert region.has_building("training_ground")
        marshal.morale = 100
        world.nation_gold["France"] = 200_000
        before = marshal.morale
        cmd = {"action": "purchase_levy", "marshal": marshal.name,
               "batches": 1, "type": "specific"}
        result = CommandExecutor().execute(
            {"action": "purchase_levy", "command": cmd}, {"world": world})
        assert result.get("success") is True, result.get("message")
        # The receipt STATES the rung it applied — shown = applied.
        assert "muster at 55%" in result["message"], result["message"]
        assert "muster at 25%" not in result["message"]
        assert marshal.morale < before, "the dilution must still be real"

    def test_a_driven_purchase_onto_the_rout_line_is_warned_about(self, world):
        """⚠ ALSO WRITTEN BECAUSE A MUTATION CAME BACK INERT: silencing the
        warning killed nothing, because nothing drove a purchase that lands on
        the line. `LEVY_MORALE_BASE`, `FORCED_RETREAT_THRESHOLD` and the global
        rout threshold are all 25, so a big batch into a tired corps leaves it
        one reverse from breaking — and the receipt said nothing."""
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.combat import FORCED_RETREAT_THRESHOLD
        marshal = next(m for m in world.marshals.values()
                       if m.nation == "France")
        marshal.morale = 26          # one point above the line
        marshal.strength = 1000      # so 9,000 bought men dominate the average
        world.nation_gold["France"] = 200_000
        cmd = {"action": "purchase_levy", "marshal": marshal.name,
               "batches": 1, "type": "specific"}
        result = CommandExecutor().execute(
            {"action": "purchase_levy", "command": cmd}, {"world": world})
        assert result.get("success") is True, result.get("message")
        line = marshal.get_rout_threshold(FORCED_RETREAT_THRESHOLD)
        assert marshal.morale <= line, (
            f"fixture failed to reach the line: {marshal.morale} vs {line}")
        assert "breaking line" in result["message"], result["message"]
        assert str(line) in result["message"]

    def test_a_healthy_corps_is_not_warned(self, world):
        """The other half, or the warning is noise: a purchase that leaves the
        corps well clear of its line must say nothing about breaking."""
        from backend.commands.executor import CommandExecutor
        marshal = next(m for m in world.marshals.values()
                       if m.nation == "France")
        marshal.morale = 100
        world.nation_gold["France"] = 200_000
        cmd = {"action": "purchase_levy", "marshal": marshal.name,
               "batches": 1, "type": "specific"}
        result = CommandExecutor().execute(
            {"action": "purchase_levy", "command": cmd}, {"world": world})
        assert result.get("success") is True, result.get("message")
        assert "breaking line" not in result["message"]

    def test_the_lever_down_restores_the_flat_base(self, world, premium_flat):
        for region in (self._Region(False), self._Region(True)):
            assert substitute_arrival_morale(
                EconomyExecutor, region, None) == LEVY_MORALE_BASE


# ════════════════════════════════════════════════════════════════════════
# C. The alarm prices the levy
# ════════════════════════════════════════════════════════════════════════

class TestTheAlarmPricesTheLevy:
    def test_it_is_dormant_at_every_seeded_boot_by_construction(self, world):
        """Not by one measurement — by the authored band. `threat_level_band`
        is [65, 75] and the anchor is 75, so `max(0, threat - 75)` is 0 at
        both endpoints and everywhere between."""
        threat = getattr(world, "threat_by_target", {}) or {}
        for endpoint in (65, 75):
            threat["France"] = endpoint
            assert levy_alarm_multiplier(world, "France") == 1.0, endpoint
        threat["France"] = 70   # the measured boot value
        assert levy_alarm_multiplier(world, "France") == 1.0

    def test_the_authored_band_really_is_below_the_anchor(self):
        """If the scenario's band is ever raised above the anchor, the claim
        above stops being structural and this pin says so."""
        scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
        band = None
        for key in ("variance_bands", "bands", "statecraft"):
            block = scenario.get(key)
            if isinstance(block, dict) and "threat_level_band" in block:
                band = block["threat_level_band"]
        if band is None:
            band = scenario.get("threat_level_band")
        assert band is not None, (
            "the authored threat band moved — re-derive the anchor claim")
        assert max(band) <= LEVY_ALARM_ANCHOR, (
            f"band {band} reaches past the anchor {LEVY_ALARM_ANCHOR}; the "
            f"alarm is no longer boot-dormant by construction")

    def test_it_rises_with_the_alarm_the_player_caused(self, world):
        threat = getattr(world, "threat_by_target", {}) or {}
        measured = {76: 1.01, 90: 1.15, 100: 1.25}
        for value, expected in measured.items():
            threat["France"] = value
            assert levy_alarm_multiplier(world, "France") == pytest.approx(
                expected), value

    def test_an_absent_slot_is_never_a_discount(self, world):
        """`max(0, …)` — a court with no threat slot pays ×1.00, not less."""
        threat = getattr(world, "threat_by_target", {}) or {}
        threat.pop("Hesse", None)
        assert levy_alarm_multiplier(world, "Hesse") == 1.0
        threat["Hesse"] = 10
        assert levy_alarm_multiplier(world, "Hesse") == 1.0

    def test_shown_equals_applied(self, world):
        """The figure `get_levy_status` publishes is the figure the price
        function applies — the CA9-N11 rule, one term further on."""
        threat = getattr(world, "threat_by_target", {}) or {}
        threat["France"] = 90
        shown = get_levy_status(world, "France")["substitutes"]["alarm_premium_pct"]
        applied = levy_alarm_multiplier(world, "France")
        assert isinstance(shown, int), "GR2: Godot crashes on floats"
        assert shown == int(round((applied - 1.0) * 100))
        # …and it IS the threat above the anchor, by construction.
        threat = int((getattr(world, "threat_by_target", {}) or {}).get("France", 0))
        assert shown == max(0, threat - LEVY_ALARM_ANCHOR)
        bare_base = levy_substitute_price(world, "France")
        econ_mod.THE_ALARM_PRICES_THE_LEVY = False
        try:
            unpriced = levy_substitute_price(world, "France")
        finally:
            econ_mod.THE_ALARM_PRICES_THE_LEVY = True
        assert bare_base == int(unpriced * applied) or abs(
            bare_base - int(unpriced * applied)) <= 1

    def test_the_lever_down_is_byte_identical(self, world, alarm_off):
        threat = getattr(world, "threat_by_target", {}) or {}
        threat["France"] = 100
        assert levy_alarm_multiplier(world, "France") == 1.0

    def test_it_prices_substitutes_only(self):
        """The term is deliberately NOT in `_calculate_recruit_cost`, which
        would move every recruit price in the game. A stated scope limit."""
        src = (REPO / "backend/commands/economy_executor.py").read_text(
            encoding="utf-8")
        tree = ast.parse(src)
        for fn in ast.walk(tree):
            if (isinstance(fn, ast.FunctionDef)
                    and fn.name == "_calculate_recruit_cost"):
                body = "\n".join(
                    src.splitlines()[fn.lineno - 1:fn.end_lineno])
                assert "levy_alarm_multiplier" not in body, (
                    "the alarm reached the DRAFT's pricer — that moves every "
                    "recruit price in the game and reds blessed pins")


# ════════════════════════════════════════════════════════════════════════
# D. The riders — a sink nobody can find absorbs nothing
# ════════════════════════════════════════════════════════════════════════

class TestTheLevyStatesItsTerms:
    def test_the_sub_dict_is_present_and_nation_scoped(self, world):
        france = get_levy_status(world, "France")["substitutes"]
        austria = get_levy_status(world, "Austria")["substitutes"]
        assert france is not None and austria is not None
        assert france["ceiling"] != austria["ceiling"], (
            "the substitutes block is answering for one nation on both — the "
            "IQ1-2 levy defect, one layer in")

    def test_the_room_is_the_measured_boot_arithmetic(self, world):
        block = get_levy_status(world, "France")["substitutes"]
        limit = int(world.get_force_limit("France") or 0)
        standing = int(world.calculate_turn_upkeep("France")
                       .get("total_strength", 0))
        assert block["ceiling"] == levy_purchase_ceiling(world, "France")
        assert block["room"] == max(0, block["ceiling"] - standing)
        # The measured boot numbers, so a silent change to either constant
        # shows up here with its arithmetic.
        assert (limit, standing, block["room"]) == (130_000, 189_000, 6_000)

    def test_the_gate_is_the_smallest_deliverable_batch(self, world):
        """`open` must mean "a purchase can actually land", so it is gated on
        the FIELD batch (the smallest delivery), not on a full one."""
        block = get_levy_status(world, "France")["substitutes"]
        assert block["open"] is (block["room"] >= AI_CORPS_REGEN_CAP)

    def test_every_published_figure_is_an_int(self, world):
        """GR2 — Godot crashes on floats, and `test_no_floats_in_ledger`
        caught the first cut of this block publishing the raw multiplier."""
        block = get_levy_status(world, "France")["substitutes"]
        for key, value in block.items():
            if key == "open":
                assert isinstance(value, bool), key
            else:
                assert isinstance(value, int) and not isinstance(value, bool), (
                    f"{key} is {type(value).__name__}, not int")

    def test_austria_has_no_room_at_boot(self, world):
        block = get_levy_status(world, "Austria")["substitutes"]
        assert block["room"] == 0 and block["open"] is False

    def test_the_lever_down_omits_the_block(self, world):
        before = econ_mod.THE_LEVY_STATES_ITS_TERMS
        econ_mod.THE_LEVY_STATES_ITS_TERMS = False
        try:
            status = get_levy_status(world, "France")
            assert status["substitutes"] is None
            # …and every pre-existing key is untouched.
            for key in ("force_limit", "army_strength", "headroom",
                        "infantry_price", "infantry_pool", "open"):
                assert key in status
        finally:
            econ_mod.THE_LEVY_STATES_ITS_TERMS = before


class TestTheRegionPanelChip:
    def _gd(self):
        return PANEL_GD.read_text(encoding="utf-8")

    def test_the_chip_exists_and_names_the_marshal(self):
        """CN-4 (Sept 22, 2026) — CONSCIOUSLY RE-PINNED: the chip still names
        its marshal, but the BACKEND's quote chooses him
        (`economy_executor.substitute_quote`: the first infantryman standing
        there — the market sells muskets). The client used to name the first
        French marshal in the list, which at Franche-Comte was Murat, a
        cavalryman the executor always refuses. The CN-4 census drives it."""
        src = self._gd()
        assert 'do:buy substitutes for " + str(sub_q.get("recipient", ""))' in src, (
            "the chip sends a bare verb with no marshal — the parser would "
            "have to guess, and IQ1-2 pinned that the help teaches phrasings "
            "that actually parse")

    def test_a_gated_chip_is_dimmed_with_a_reason_never_absent(self):
        """This project's honest-availability idiom. CN-4 — CONSCIOUSLY
        RE-PINNED: the reason is the backend quote's `short` (the executor's
        own gate, in its order), so the words live in the quote, not here."""
        src = self._gd()
        block = src[src.index("IQ-1 IQ1-3D rider 1"):]
        block = block[:block.index("\t\t# Build")] if "\t\t# Build" in block else block[:3000]
        assert "bb_chip_disabled" in block
        assert 'str(sub_q.get("short", ""))' in block
        assert "under the establishment" in block
        quote_src = (REPO / "backend/commands/economy_executor.py").read_text(
            encoding="utf-8")
        body = quote_src[quote_src.index("def substitute_quote"):]
        body = body[:body.index("\ndef ")]
        assert "does not feed our battalions" in body

    def test_it_quotes_the_per_region_figure_not_the_capitals(self):
        """The Aug-30 lesson, one verb over: the capital's rate ran up to
        twice the local one and the player read one number while being
        charged another."""
        src = self._gd()
        assert 'data.get("substitute_price_here"' in src

    def test_the_backend_prices_it_for_the_marshal_standing_there(self):
        """MC-2b's Intendance moves the charge ±15%, and
        `_region_recruit_price` passes no `marshal=` — so reusing it would
        quote a figure the executor does not charge."""
        src = (REPO / "backend/models/world_state.py").read_text(
            encoding="utf-8")
        tree = ast.parse(src)
        body = None
        for fn in ast.walk(tree):
            if (isinstance(fn, ast.FunctionDef)
                    and fn.name == "_region_substitute_price"):
                body = "\n".join(
                    src.splitlines()[fn.lineno - 1:fn.end_lineno])
        assert body is not None, "the per-region substitute pricer is gone"
        assert "marshal=marshal" in body
        assert "foreign_soil=" in body

    def test_the_quoted_price_is_the_charged_price(self, world):
        """Driven, both sides: the payload figure must equal what the
        executor's own pricer returns for that marshal in that province."""
        marshal = next(m for m in world.marshals.values()
                       if m.nation == "France")
        region = world.get_region(marshal.location)
        quoted = world._region_substitute_price(region)
        ex = EconomyExecutor(None)
        charged = ex._calculate_recruit_cost(
            region, world, base_cost=levy_substitute_price(world, "France"),
            nation="France", marshal=marshal,
            foreign_soil=(region.controller != "France"))
        assert quoted == charged

    def test_it_is_zero_where_the_ground_does_not_feed_us(self, world):
        enemy = next(r for r in world.regions.values()
                     if r.controller and world.is_at_war("France", r.controller))
        assert world._region_substitute_price(enemy) == 0


class TestTheCourtsPurchasesAreLogged:
    def test_the_type_is_in_the_economy_arm(self):
        """⚠ The decision fleet reported the filter as having "NO economy
        branch and no default arm". Half right: the branch has been there
        since Session 8 — the TYPE was missing from it. The correction is
        the smaller fix, and it is recorded because the wrong diagnosis
        would have had somebody add a whole arm."""
        src = (REPO / "backend/campaign_log.py").read_text(encoding="utf-8")
        arm = src[src.index("# Economy events (enemy): region PARTIAL+"):]
        arm = arm[:arm.index("econ_region =")]
        assert '"substitutes_purchased"' in arm
        assert '"recruitment"' in arm, "this is the arm that already existed"

    def test_the_producer_emits_the_region_the_filter_reads(self):
        """The arm filters on `region`, so a producer without one is dropped
        no matter which tuple it is in."""
        src = (REPO / "backend/commands/economy_executor.py").read_text(
            encoding="utf-8")
        i = src.index('"type": "substitutes_purchased",')
        block = src[i:i + 500]
        assert '"region": region.name' in block

    def test_a_foreign_purchase_reaches_the_log_at_partial(self, world):
        from backend.campaign_log import filter_campaign_log
        region = next(r for r in world.regions.values()
                      if r.controller == "Austria")
        event = {"type": "substitutes_purchased", "turn": 1,
                 "nation": "Austria", "region": region.name,
                 "marshal": "Mack", "men": 9000, "gold": 2400}
        from backend.models.intel import FULL, PARTIAL, UNKNOWN
        world.event_log = [event]
        intel = world.get_region_intel(region.name)
        # Drive BOTH arms explicitly rather than branching on whatever the
        # boot fog happens to be — a test that asserts whichever it finds
        # proves nothing about the rule.
        intel.visibility = UNKNOWN
        assert event not in filter_campaign_log(world.event_log, world), (
            "a fogged court's purchase is leaking")
        for seen in (PARTIAL, FULL):
            intel.visibility = seen
            assert event in filter_campaign_log(world.event_log, world), seen


class TestThePlayerCanLearnTheCompactsExist:
    def test_the_three_instrument_verbs_are_named(self):
        """The identical hole IQ1-2 closed for `purchase_levy`: three verbs
        shipped and no player could learn they exist."""
        src = (REPO / "backend/commands/meta_executor.py").read_text(
            encoding="utf-8")
        block = src[src.index("THE COMPACTS"):]
        block = block[:block.index("\n\n")]
        for verb in ("buy off", "sponsor", "guarantee", "license"):
            assert verb in block, verb
        assert "runs its TERM" in block, (
            "the help must say a compact cannot be cancelled — §0.6's own "
            "'cancel verb' does not exist")

    def test_every_phrasing_the_help_teaches_actually_parses(self):
        """IQ1-2's pin, extended to the new copy. A help entry naming a
        sentence the parser refuses is worse than no entry."""
        corpus = json.loads(
            (REPO / "tests/data/parser_golden_corpus.json").read_text(
                encoding="utf-8"))
        rows = corpus["entries"] if isinstance(corpus, dict) else corpus
        utterances = {str(r.get("utterance", "")).lower()
                      for r in rows if isinstance(r, dict)}
        src = (REPO / "backend/commands/meta_executor.py").read_text(
            encoding="utf-8")
        block = src[src.index("THE COMPACTS"):]
        block = block[:block.index("\n\n")]
        taught = re.findall(r'"([^"]+)"', block)
        assert len(taught) >= 4, taught
        for phrase in taught:
            assert phrase.lower() in utterances, (
                f"help teaches {phrase!r} but no golden-corpus row pins it")


class TestTheArchiveCarriesTheInstrument:
    def test_archive_copies_the_jsonl(self):
        src = DRIVER.read_text(encoding="utf-8")
        block = src[src.index("if args.archive:"):]
        block = block[:block.index("\n    if digest.unknown_blockers")]
        # ⚠ The first cut asserted the STRING "digest.jsonl" in the block and
        # was INERT under mutation: the `if digest.jsonl_path.exists():` guard
        # one line above contains it, so deleting the copy left the pin green.
        # Assert the COPY, not a mention.
        assert 'shutil.copy2(digest.jsonl_path' in block, (
            "the jsonl is guarded but never copied")
        for expected in ("digest.md", "meta.json"):
            assert expected in block, expected
        assert block.count("shutil.copy2") == 3, (
            f"expected three copies (md, meta, jsonl), found "
            f"{block.count('shutil.copy2')}")

    def test_it_does_not_assume_the_file_exists(self):
        src = DRIVER.read_text(encoding="utf-8")
        block = src[src.index("if args.archive:"):]
        block = block[:block.index("\n    if digest.unknown_blockers")]
        assert "jsonl_path.exists()" in block


# ════════════════════════════════════════════════════════════════════════
# Completion item (iv) — the acceptance test
# ════════════════════════════════════════════════════════════════════════

# Measured provenance for every constant below:
#   GROSS_FLOOR 1842  — the shipped 1805 boot's OWN gross (net 1,842 at a
#                       chest of 800, where the charge is 0).
#   HOARD_TURNS 12    — the ceiling on turns of the empire's ENTIRE gross
#                       income sitting unconverted. Control arm measured 21.9;
#                       the positive arm 8.1.
#   CONVERSION_FLOOR  — share of lifetime gross actually converted. Control
#                       0.000, HEAD 0.150, the positive arm 0.783.
GROSS_FLOOR = 1842
HOARD_TURNS = 12
CONVERSION_FLOOR = 0.40


def the_chest_is_convertible(gross, rate, chest, receipts, turns):
    """Completion item (iv) — the 590× purse:price ratio's REPLACEMENT.

    ONE function, shared by every arm AND by the negative control, never a
    retyped threshold (the IGR-E pattern).

    ⚠ WHY NOT §0.7's obligation-based fixed point, which three candidate
    contracts proposed: `state_charges_ceiling` returns 0 for `net <= 0`, and
    `_build_economy` renders that as `CEILING_NO_SURPLUS` — the state IQ1-2's
    review round deliberately repainted in an ERROR colour with the copy "the
    chest is not growing". A predicate treating that 0 as a PASS scores
    OVER-COMMITMENT as success and is satisfiable by any obligation large
    enough. This slice's sink is `Spent`, not Net, so no obligation term is
    needed at all.

    ⚠ AND WHY NOT THE RATIO ITSELF: the same pricer returns 150 at the capital
    at peace and 654 at the boot — a 4.4× ambiguity in the denominator — and a
    census of every archived digest finds the modal DELIVERED purchase is
    3,000 men for 200 gold, with "10,000 men for 150" occurring once.
    """
    from backend.game_logic.ledger import state_charges_ceiling
    if gross < GROSS_FLOOR or rate <= 0:
        return False                      # not a winning France
    if state_charges_ceiling(gross, rate) <= 0:
        return False                      # not growing: a different arm
    return (chest / gross <= HOARD_TURNS
            and receipts / (gross * turns) >= CONVERSION_FLOOR)


def _carries_a_correction_marker(window: str) -> bool:
    """ONE rule for both stale-figure censuses: a retired number may appear
    where it is being CORRECTED, and nowhere else.

    Shared rather than written twice, because the two pins asked the same
    question with two different answers on their first cut — which is the
    drift they exist to prevent, one level up.
    """
    markers = ("CORRECTED", "corrected", "CORRECTION", "correction",
               "struck", "STRUCK", "wrong", "read **", "used to",
               # …and the forms a housekeeping note actually uses. Added
               # because this pin red on the very paragraph recording the
               # correction, which is the pin being right and the marker list
               # being short — the useful failure of the two.
               "now reads", "missed", "Housekeeping", "RETIRED", "retired")
    return any(m in window for m in markers)


class TestTheContractIsNotStale:
    """The housekeeping the slice inherits, pinned rather than promised."""

    def test_the_retired_ratio_is_gone_from_the_contract(self):
        """⚠ IQ1-2 wrote "this read 457× in three places" and fixed TWO — and
        the one it missed was the COMPLETION CRITERION that grades the row.
        §0.5.3's lesson a third time, so it is a census now: every surviving
        mention of the retired figure must be inside a CORRECTION note, never
        stated as the criterion."""
        status = (REPO / "docs/STATUS.md").read_text(encoding="utf-8")
        lines = status.splitlines()
        offenders = []
        for i, line in enumerate(lines):
            if "457" not in line:
                continue
            window = "\n".join(lines[max(0, i - 3):i + 1])
            if not _carries_a_correction_marker(window):
                offenders.append(i + 1)
        assert not offenders, (
            f"the retired ratio stands as a CLAIM at STATUS.md:{offenders}")
        assert "590×" in status, "the replacement figure is not on the record"

    def test_the_receipt_figure_is_one_number_everywhere(self):
        """18,537 was the first receipt sum; 18,852 is the figure re-derived
        from the six receipts themselves. It survived in EIGHT sites against
        two files carrying the right one.

        ⚠ The rule is the SAME one the retired-ratio pin uses, and the first
        cut of this pin had it wrong: a bare "not in text" forbids a CORRECTION
        from naming the figure it corrects, which is exactly how this record
        documents every other struck number. So the figure may appear beside a
        correction marker and nowhere else."""
        offenders = []
        for rel in ("tests/test_iq1_iq1_2_chest_tells_the_truth.py",
                    "tools/playtest_driver.py",
                    "tools/playtest_scripts/commanded_spender40.json",
                    "docs/IMPROVEMENT_QUEUE_SPEC.md",
                    "docs/STATUS.md"):
            lines = (REPO / rel).read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines):
                if "18,537" not in line:
                    continue
                window = "\n".join(lines[max(0, i - 3):i + 1])
                if not _carries_a_correction_marker(window):
                    offenders.append(f"{rel}:{i + 1}")
        assert not offenders, (
            f"the wrong receipt sum stands as a CLAIM at: {offenders}")

    def test_the_refusal_count_is_six(self):
        """§0.5.1 FINDING 2 said "3 refused"; §0.4 and STATUS both say six, so
        the spec contradicted itself, and the wrong figure had propagated into
        a test docstring."""
        spec = (REPO / "docs/IMPROVEMENT_QUEUE_SPEC.md").read_text(
            encoding="utf-8")
        assert "3 refused" not in spec
        mine = pathlib.Path(__file__).read_text(encoding="utf-8")
        assert "six" in mine.lower()


class TestCompletionItemFour:
    """Both directions, on the measured arms."""

    # (gross, rate, chest, receipts, turns) — all read from the arms.
    CONTROL = (4038, 30, 88_556, 0, 40)
    HEAD = (3142, 30, 54_443, 18_852, 40)
    POSITIVE = (2409, 30, 19_577, 75_486, 40)

    def test_the_disease_board_fails(self):
        assert the_chest_is_convertible(*self.CONTROL) is False, (
            "a France banking 88,556 gold and converting none of it must not "
            "pass the row's own completion criterion")

    def test_head_still_fails(self):
        assert the_chest_is_convertible(*self.HEAD) is False, (
            "IQ1-1 alone converted 15% — necessary and not sufficient, which "
            "is what its own record said")

    def test_the_slice_passes(self):
        assert the_chest_is_convertible(*self.POSITIVE) is True

    def test_the_negative_control_is_load_bearing(self):
        """The IGR-E pattern: the SAME function must fail at the pre-row
        value, or the predicate is decoration."""
        gross, rate, chest, receipts, turns = self.POSITIVE
        # Roll the receipts back to HEAD's and it must fail on conversion.
        assert the_chest_is_convertible(gross, rate, chest, 18_852, turns) is False
        # Roll the chest back to the control's and it must fail on the hoard.
        assert the_chest_is_convertible(gross, rate, 88_556, receipts, turns) is False

    def test_each_threshold_is_independently_load_bearing(self):
        """Neither clause may be carrying the other."""
        gross, rate, chest, receipts, turns = self.POSITIVE
        hoard = chest / gross
        conversion = receipts / (gross * turns)
        assert hoard <= HOARD_TURNS and conversion >= CONVERSION_FLOOR
        # Each on its own margin, so a drift in either is visible.
        assert hoard == pytest.approx(8.1, abs=0.15), hoard
        assert conversion == pytest.approx(0.783, abs=0.02), conversion
        assert 88_556 / 4038 == pytest.approx(21.9, abs=0.15)

    def test_the_hoard_clause_is_what_fails_the_disease_board(self):
        """⚠ WRITTEN BECAUSE A MUTATION CAME BACK INERT: relaxing HOARD_TURNS
        to 25 killed nothing, because the control also fails the CONVERSION
        clause and no pin said WHICH clause does the work on which arm."""
        gross, rate, chest, receipts, turns = self.CONTROL
        assert chest / gross > HOARD_TURNS, (
            "the disease board must fail the hoard clause on its own")
        # …and it must fail it even if it had converted plenty.
        assert the_chest_is_convertible(gross, rate, chest,
                                        int(0.9 * gross * turns), turns) is False

    def test_the_conversion_clause_is_load_bearing_on_its_own(self):
        """⚠ MY FIRST CUT OF THIS PIN WAS WRONG ABOUT ITS OWN SUBJECT, and the
        correction is worth keeping: I asserted HEAD's chest sits inside the
        hoard ceiling so that only the conversion floor rejects it. Measured,
        HEAD's hoard is 54,443 / 3,142 = **17.3**, which is ABOVE the ceiling
        of 12 — so HEAD fails BOTH clauses, and it cannot isolate either.

        So the isolation is stated on a constructed arm instead: a France that
        has drawn its chest down to inside the ceiling but converted almost
        nothing — hoarding cured, spending not — must still fail."""
        gross, rate, turns = 3142, 30, 40
        hoarded_less = int(HOARD_TURNS * gross) - 1000   # inside the ceiling
        assert hoarded_less / gross <= HOARD_TURNS
        thin = int(0.15 * gross * turns)                 # HEAD's conversion
        assert thin / (gross * turns) < CONVERSION_FLOOR
        assert the_chest_is_convertible(gross, rate, hoarded_less,
                                        thin, turns) is False
        # …and the SAME arm passes the moment the conversion clears the floor,
        # so the clause is the only thing doing the work here.
        plenty = int(CONVERSION_FLOOR * gross * turns) + 1
        assert the_chest_is_convertible(gross, rate, hoarded_less,
                                        plenty, turns) is True

    def test_head_fails_both_clauses(self):
        """And HEAD's real reading, since it is on the record: 17.3 turns of
        hoard AND 0.150 conversion. IQ1-1 was necessary and not sufficient,
        which is what its own landing record said."""
        gross, rate, chest, receipts, turns = self.HEAD
        assert chest / gross == pytest.approx(17.3, abs=0.1)
        assert receipts / (gross * turns) == pytest.approx(0.150, abs=0.005)
        assert the_chest_is_convertible(*self.HEAD) is False

    def test_the_gross_floor_rejects_a_rump_that_converted_everything(self):
        """⚠ ALSO WRITTEN BECAUSE A MUTATION CAME BACK INERT: deleting the
        `gross < GROSS_FLOOR` guard killed nothing, because the collapsing arm
        this file already pinned fails the CONVERSION clause anyway.

        The case the guard exists for is a collapsed rump that spent
        everything it had: tiny gross, tiny chest, total conversion. Without
        the floor it PASSES — scoring an annihilated France as a healthy
        economy, which is exactly the confusion IQ-2 exists to end."""
        rump = (500, 30, 2_000, 20_000, 40)      # gross 500, conversion 1.00
        gross, rate, chest, receipts, turns = rump
        assert chest / gross <= HOARD_TURNS
        assert receipts / (gross * turns) >= CONVERSION_FLOOR
        assert gross < GROSS_FLOOR, "fixture precondition"
        assert the_chest_is_convertible(*rump) is False, (
            "a collapsed rump that spent its last coin is being graded as a "
            "winning France")

    def test_a_collapsing_arm_is_excluded_not_scored(self):
        """The ambient arm ends on 5 provinces and 2,593 gold with 23 treasury
        falls — non-monotonic for the WRONG reason. The predicate must decline
        to grade it rather than pass it."""
        assert the_chest_is_convertible(500, 30, 2_593, 0, 40) is False
        assert the_chest_is_convertible(4038, 0, 88_556, 75_486, 40) is False
