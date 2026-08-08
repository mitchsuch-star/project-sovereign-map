"""EB — the Econ Balance slice (ROADMAP position 5, row EC-P3).

Gate + build record: docs/audits/ECON_BALANCE_GATE_2026_08_07.md (authoritative).

The slice in one paragraph: the measured Aug-7 disease was that treasury
runaway is a PEACETIME disease (Prussia +298/turn and Spain +1,010/turn
linearly forever — the only brake, the EC-W2 WE tax, switches off exactly
when a nation is doing well) and condition-blind at war (collapsing France
and conquering Austria converge to the same fixed point). EB-1 generalizes
the WE tax into THE CHARGES OF EMPIRE — one condition-priced rate (WE +
crown + war + ill + unrest + grip) over the same divisor, on the chest
above a working floor — making the treasury a CONDITIONAL fixed point:
golden peace is near-unbounded (the user's own carve-out), collapse bleeds.
EB-2 authors the overseas/colonial pools (colonies as a MODIFIER) with the
Continental System as the counterplay; EB-5a pays the disruptor
(la guerre nourrit la guerre); EB-3 makes buildings wants and ruins free;
EB-4 gives the threat bar headroom.

Formula pins live in test_econ_war_coupling.TestStateChargesDrain (the
re-blessed EC-W2 class). THIS file pins the gate's acceptance criteria
(§5) and the cross-component behaviour.
"""

from pathlib import Path

import pytest

from backend.game_logic.ledger import _build_economy
from backend.models.world_state import (
    CHARGES_CROWN_BASE, CHARGES_GRIP_RATE, CHARGES_HOARD_FLOOR,
    CHARGES_ILL_RATE, CHARGES_UNREST_RATE, CHARGES_WAR_RATE,
    REQUISITION_RATE, WAR_EFFORT_DIVISOR, WorldState,
)

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _peace_out(world, nation):
    for key, state in list(world.diplomatic_states.items()):
        if state == "WAR" and nation in key.split("|"):
            world.diplomatic_states[key] = "PEACE"
    world.war_exhaustion.pop(nation, None)


def _fixed_point(net, rate):
    """T* = floor + net × divisor / rate — the conditional fixed point."""
    return CHARGES_HOARD_FLOOR + net * WAR_EFFORT_DIVISOR // max(1, rate)


# ═══════════════════ §5.2 — CONDITION BEATS CLOCK ═══════════════════════════


class TestConditionBeatsClock:
    """The old WE tax was condition-blind: a collapsing France and a
    prospering France at the same WE paid the same rate. The Charges of
    Empire read the state of the REALM."""

    def test_collapsing_france_pays_a_higher_rate_than_a_prospering_one(
            self, world):
        world.war_exhaustion["France"] = 150

        # Prospering: at war, interior quiet, grip full — WE + crown + war.
        prosper_rate = world.get_state_charges_rate("France")["rate"]
        assert prosper_rate == 150 + CHARGES_CROWN_BASE + CHARGES_WAR_RATE

        # Collapsing: the same WE, but the interior burns (a home province
        # at unrest stability) — the EC-W CurveInverts staging, condensed.
        region = world.regions[world.nation_starting_regions["France"][0]]
        region.stability = 30
        collapse_rate = world.get_state_charges_rate("France")["rate"]
        assert collapse_rate == prosper_rate + CHARGES_UNREST_RATE
        assert _fixed_point(1800, collapse_rate) < _fixed_point(
            1800, prosper_rate), (
            "the collapsing empire's ceiling must sit strictly below the "
            "prospering one's — condition finally beats clock")

    def test_the_ill_war_term_reads_the_stored_war_level_score(
            self, world, monkeypatch):
        """'The wars go ill' keys on the CA8-D2 STORED war-level aggregate
        (`sum_stored_side_score` — the score-consuming seam; the live
        aggregate is the display surface's and blows the G4 budget) — a
        war whose side score has turned against us adds ILL_RATE."""
        import backend.game_logic.diplomacy as diplomacy
        world.war_exhaustion.pop("France", None)
        keys = {t["key"] for t in world.get_state_charges_rate("France")["terms"]}
        assert "wars_go_ill" not in keys
        monkeypatch.setattr(diplomacy, "sum_stored_side_score",
                            lambda w, n, opps: -30)
        rate = world.get_state_charges_rate("France")
        keys = {t["key"] for t in rate["terms"]}
        assert "wars_go_ill" in keys
        assert any(t["amount"] == CHARGES_ILL_RATE for t in rate["terms"]
                   if t["key"] == "wars_go_ill")

    def test_the_ill_term_fires_on_a_real_stored_score(self, world):
        """Falsifiability guard on the seam itself (the wrong-signature
        trap this slice's first cut fell into): a REAL stored pair score
        below the threshold — no monkeypatch — must flip the term."""
        # stored from the alphabetically-first perspective: Austria +40
        # means France −40 in the France-vs-Austria war
        world.war_scores[world._make_diplo_key("France", "Austria")] = 40
        keys = {t["key"] for t in world.get_state_charges_rate("France")["terms"]}
        assert "wars_go_ill" in keys

    def test_the_ill_term_reads_the_whole_war_not_the_pair(self, world):
        """Review [0]: the first cut read bare PAIR scores, so a nation
        WINNING its coalition war still paid the ill rate because one
        pair lagged. The term reads `get_side_war_score_for` — the
        war-level resolver that sums the stored pair scores over the
        WHOLE opposing side of the shared war instance.

        Boot France fights ONE coalition war vs Austria+Britain+Russia:
        losing one pair −25 while winning another +40 is a WON war
        (side score +15) — no ill term. Losing −15 to each of the three
        (side −45) is a war going ill — the term fires."""
        k = world._make_diplo_key
        # arm 1: one pair lost, the war won — no term. Stored scores read
        # from the ALPHABETICALLY-FIRST nation's perspective: on
        # "Austria|France" +25 is Austria's (France −25); on
        # "France|Russia" France is first, so +40 IS France's.
        world.war_scores[k("France", "Austria")] = 25   # France −25
        world.war_scores[k("France", "Russia")] = 40    # France +40
        keys = {t["key"] for t in world.get_state_charges_rate("France")["terms"]}
        assert "wars_go_ill" not in keys, (
            "a nation WINNING its coalition war must not pay the ill rate "
            "for one lagging pair")
        # arm 2: every pair mildly lost, the war lost — the term fires
        # (France second on Austria|France and Britain|France → +15 is the
        # enemy's; France FIRST on France|Russia → −15 is France's own)
        world.war_scores[k("France", "Austria")] = 15   # France −15
        world.war_scores[k("France", "Britain")] = 15   # France −15
        world.war_scores[k("France", "Russia")] = -15   # France −15
        keys = {t["key"] for t in world.get_state_charges_rate("France")["terms"]}
        assert "wars_go_ill" in keys, (
            "−15 to each of three coalition partners is a war-level −45 — "
            "the pair read would never see it")

    def test_the_grip_term_reads_imperial_grip(self, world, monkeypatch):
        import backend.models.authority as authority
        keys = {t["key"] for t in world.get_state_charges_rate("France")["terms"]}
        assert "grip_falters" not in keys, "boot grip is 100 — no charge"
        monkeypatch.setattr(authority, "get_imperial_grip",
                            lambda w, n: 40)
        rate = world.get_state_charges_rate("France")
        keys = {t["key"] for t in rate["terms"]}
        assert "grip_falters" in keys
        assert any(t["amount"] == CHARGES_GRIP_RATE for t in rate["terms"]
                   if t["key"] == "grip_falters")


# ═══════════════════ §5.3 — THE BLESSING SURVIVES ═══════════════════════════


class TestGoldenPeaceMayGrowRich:
    """'The economy shouldn't go crazy UNLESS you are doing very well and
    stable' — the carve-out is implemented literally: golden peace pays
    only the crown term, ≤ 1.5% of the chest per turn."""

    def test_golden_peace_rate_is_the_crown_alone(self, world):
        _peace_out(world, "France")
        rate = world.get_state_charges_rate("France")
        assert {t["key"] for t in rate["terms"]} == {"crown"}
        assert rate["rate"] == CHARGES_CROWN_BASE

    def test_golden_peace_charge_is_at_most_1_5_percent(self, world):
        _peace_out(world, "France")
        for treasury in (5_000, 20_000, 60_000):
            world.nation_gold["France"] = treasury
            charge = world.calculate_state_charges("France")
            assert charge <= int(treasury * 0.015), (
                f"golden-peace France pays {charge} on {treasury} — the "
                f"blessing (may grow rich when doing very well and stable) "
                f"is broken")

    def test_war_consumes_the_hoard_from_turn_one(self, world):
        """The war establishment bites the moment war exists — no WE ramp
        wait. A 30k peace-built chest starts paying immediately at war."""
        world.nation_gold["France"] = 30_000
        world.war_exhaustion.pop("France", None)  # WE hasn't ramped yet
        charge = world.calculate_state_charges("France")
        expected_rate = CHARGES_CROWN_BASE + CHARGES_WAR_RATE
        assert charge == (30_000 - CHARGES_HOARD_FLOOR) * expected_rate \
            // WAR_EFFORT_DIVISOR
        assert charge >= 800, "the war chest must visibly feed the war"


# ═══════════════════ §5.1 — NO NATION GROWS UNBOUNDEDLY ═════════════════════


class TestPeacetimeRunawayIsDead:
    def test_idle_prussia_converges_instead_of_growing_linearly(self, world):
        """The measured disease verbatim: Prussia (at war with nobody)
        gained a CONSTANT +298/turn for 30+ straight turns. Under EB-1 the
        crown term makes its surplus shrink as the chest grows — the delta
        at a rich chest must be strictly below the delta at a poor one."""
        _peace_out(world, "Prussia")

        world.nation_gold["Prussia"] = 4_000
        poor_charge = world.calculate_state_charges("Prussia")
        world.nation_gold["Prussia"] = 20_000
        rich_charge = world.calculate_state_charges("Prussia")
        assert rich_charge > poor_charge, (
            "the charge must grow with the hoard — that shrinking surplus "
            "IS the fixed point forming")

    def test_the_fixed_point_is_finite_and_condition_scaled(self, world):
        """At Prussia's measured net (+298) the peace plateau lands near
        floor + net×2500/30 ≈ 26.8k — finite, where the old system had NO
        peacetime fixed point at all. At war the same nation's plateau
        drops by the war establishment alone."""
        peace_plateau = _fixed_point(298, CHARGES_CROWN_BASE)
        war_plateau = _fixed_point(298, CHARGES_CROWN_BASE + CHARGES_WAR_RATE)
        assert peace_plateau < 30_000
        assert war_plateau < peace_plateau


# ═══════════════════ EB-5a — REQUISITIONS OF WAR ════════════════════════════


class TestRequisitions:
    def test_boot_case_is_mack_in_swabia(self, world):
        """The historically exact boot case: Mack's Austrian army stands in
        Bavarian Swabia — Austria requisitions a quarter of its base income
        while Bavaria's contributions suspension is unchanged."""
        req = world.get_requisition_map()
        assert req.get("Austria", 0) > 0
        swabia = world.regions["Swabia"]
        assert req["Austria"] == int(REQUISITION_RATE * swabia.income_value)
        # the owner-side suspension is untouched by the invader's credit
        assert world.calculate_turn_income("Bavaria")["contributions"] > 0

    def test_requisitions_ride_the_income_phase(self, world):
        inc = world.calculate_turn_income("Austria")
        assert inc["requisitions"] == world.get_requisition_map().get("Austria", 0)
        econ = _build_economy(world, "Austria")
        assert econ["requisitions"] == inc["requisitions"]

    def test_strongest_presence_wins_a_shared_region(self, world):
        """Two disruptors on one province: the stronger army's paymaster
        collects; the weaker collects nothing from that region."""
        swabia = world.regions["Swabia"]
        mack = next(m for m in world.marshals.values()
                    if m.nation == "Austria" and m.location == "Swabia")
        # park a STRONGER Russian army on the same province at war w/ Bavaria
        russian = next(m for m in world.marshals.values()
                       if m.nation == "Russia")
        world.diplomatic_states[
            "|".join(sorted(["Russia", "Bavaria"]))] = "WAR"
        world.invalidate_active_nations_cache()
        russian.location = "Swabia"
        russian.strength = mack.strength + 10_000
        req = world.get_requisition_map()
        expected = int(REQUISITION_RATE * swabia.income_value)
        assert req.get("Russia", 0) == expected
        assert req.get("Austria", 0) == 0

    def test_gr5_france_extracts_too(self, world):
        """Symmetric: a French army disrupting Austrian soil pays France."""
        french = next(m for m in world.marshals.values()
                      if m.nation == "France" and m.strength >= 10_000)
        austrian_soil = next(
            r for r in world.get_nation_regions("Austria"))
        french.location = austrian_soil
        req = world.get_requisition_map()
        assert req.get("France", 0) >= int(
            REQUISITION_RATE * world.regions[austrian_soil].income_value)


# ═══════════════════ EB-2 — THE WEALTH OF NATIONS ═══════════════════════════


class TestOverseasTrade:
    def test_boot_deltas_are_the_gated_four(self, world):
        """Britain +307 (500 × 0.6154 closure) · Portugal +150 (at peace) ·
        Spain 0 (blockaded) · Holland 0 (blockaded) · France 0 (authors
        none — its overseas arm is continental extraction, a design pin)."""
        assert world.calculate_turn_income("Britain")["overseas"] == 307
        assert world.calculate_turn_income("Portugal")["overseas"] == 150
        assert world.calculate_turn_income("Spain")["overseas"] == 0
        assert world.calculate_turn_income("Holland")["overseas"] == 0
        assert world.calculate_turn_income("France")["overseas"] == 0

    def test_france_authors_no_overseas_pool(self, world):
        """The design pin: France's fleet record must not carry the key."""
        from backend.game_logic.naval import get_fleet
        assert "overseas_income" not in (get_fleet(world, "France") or {})

    def test_closure_strangles_the_holders_pool(self, world):
        """The Continental System's new economic target: rising closure
        cuts Britain's pool toward the smuggling floor (×0.4)."""
        from backend.game_logic import naval
        base = naval.overseas_trade_income(world, "Britain")
        # every continental port closed → the floor binds
        members = [n for n, _ in naval.iter_fleets(world) if n != "Britain"]
        world.continental_system_members = members
        floored = naval.overseas_trade_income(world, "Britain")
        assert floored == int(500 * 0.4)
        assert floored < base

    def test_peace_with_britain_lets_the_silver_flow(self, world):
        """Spain's arc: at war with the dominance holder (and blockaded)
        the silver is dead; at peace it flows in full — the 1804 frigate
        seizure lever finally exists, in both directions."""
        _peace_out(world, "Spain")
        from backend.game_logic import naval
        # peace lifts the blockade predicate (blockade requires war)
        assert not naval.is_blockaded(world, "Spain")
        assert naval.overseas_trade_income(world, "Spain") == 250

    def test_at_war_with_the_holder_keeps_a_quarter(self, world):
        """A colonial power at war with the RN but NOT blockaded keeps
        OVERSEAS_WAR_FACTOR of its pool (privateers and neutral bottoms)."""
        from backend.game_logic import naval
        _peace_out(world, "Spain")
        world.diplomatic_states[
            "|".join(sorted(["Spain", "Britain"]))] = "WAR"
        world.invalidate_active_nations_cache()
        # suppress the blockade read to isolate the war factor
        import backend.game_logic.naval as naval_mod
        orig = naval_mod.is_blockaded
        naval_mod.is_blockaded = lambda w, n: False
        try:
            assert naval.overseas_trade_income(world, "Spain") == int(250 * 0.25)
        finally:
            naval_mod.is_blockaded = orig

    def test_subsidy_tier_four_exists_and_caps_at_500(self, world):
        """EB-2's co-tune (the blessed E4 rider (i)): a 15k+ Britain pays
        the fourth tier; the cap rose 400 → 500 consciously."""
        from backend.game_logic.agendas import get_paymaster_subsidy_amount
        world.nation_gold["Britain"] = 16_000
        assert get_paymaster_subsidy_amount(world, "Britain") == 500
        world.nation_gold["Britain"] = 9_000
        assert get_paymaster_subsidy_amount(world, "Britain") == 400


# ═══════════════════ EB-4 — THE THREAT BAR GETS HEADROOM ════════════════════


class TestThreatHeadroom:
    def test_boot_threat_is_70(self, world):
        assert world.threat_level == 70

    def test_recentered_gates_fire_on_a_conquering_france(self, world):
        """The old 60% gate was 76 of 126 provinces — unreachable. The
        recentered 30% gate (38 provinces) fires for a France that has
        genuinely conquered a third of Europe."""
        from backend.game_logic.coalition import process_coalition_turn
        # flip exactly 12 provinces: 28 + 12 = 40 of 126 = 31.7% — inside
        # the 30% band, below the 40% one
        flipped = 0
        for region in world.regions.values():
            if region.controller != "France":
                region.controller = "France"
                flipped += 1
                if flipped >= 12:
                    break
        world.invalidate_active_nations_cache()
        before = world.threat_level
        process_coalition_turn(world)
        rows = {s["source"]: s.get("amount")
                for s in world.threat_sources_this_turn}
        assert "region_control_30" in rows, (
            f"France holds {len(world.get_nation_regions('France'))} of "
            f"{len(world.regions)} — the recentered gate must fire "
            f"(sources: {rows}, threat {before}→{world.threat_level})")
        # Review [9]: the AMOUNT is pinned too — the 30% band pays +1,
        # never the 40/50 bands' +2/+3 (gate record B13 amounts)
        assert rows["region_control_30"] == 1

    def test_gate_ladder_amounts_and_ordering(self, world):
        """Review [9]: the full ladder — 41% pays +2, 51% pays +3, the
        per-nation arm fires at the same recentered thresholds, and the
        gate record B13's structural ordering (higher control never pays
        less) is pinned as arithmetic across the three bands."""
        from backend.game_logic.coalition import process_coalition_turn

        def _set_france_share(share):
            # reset: hand every province to its scenario controller first
            fresh = WorldState.from_scenario(str(SCENARIO_PATH))
            target = int(share * len(fresh.regions)) + 1
            flipped = len(fresh.get_nation_regions("France"))
            for region in fresh.regions.values():
                if flipped >= target:
                    break
                if region.controller != "France":
                    region.controller = "France"
                    flipped += 1
            fresh.invalidate_active_nations_cache()
            return fresh

        amounts = {}
        for share, key in ((0.40, "region_control_40"),
                           (0.50, "region_control_50")):
            w = _set_france_share(share)
            process_coalition_turn(w)
            rows = {s["source"]: s.get("amount")
                    for s in w.threat_sources_this_turn}
            assert key in rows, (
                f"{key} must fire at {share:.0%}+1 control — got {rows}")
            amounts[key] = rows[key]
        assert amounts["region_control_40"] == 2
        assert amounts["region_control_50"] == 3

    def test_per_nation_arm_uses_the_recentered_gates(self, world):
        """Review [9]: a non-player conqueror crosses the SAME recentered
        thresholds into its own slot (the AI-4a step-5 arm)."""
        from backend.game_logic.coalition import process_coalition_turn
        target = int(0.30 * len(world.regions)) + 1
        flipped = len(world.get_nation_regions("Austria"))
        for region in world.regions.values():
            if flipped >= target:
                break
            if region.controller != "Austria":
                region.controller = "Austria"
                flipped += 1
        world.invalidate_active_nations_cache()
        process_coalition_turn(world)
        austria_rows = [
            s for s in world.threat_sources_this_turn
            if s["source"] == "region_control_30"
            and s.get("target") == "Austria"]
        assert austria_rows, (
            "an Austria holding 30%+ of the map must accrue into its OWN "
            "slot through the recentered per-nation arm")

    def test_defensive_win_no_longer_feeds_the_alarm(self, world):
        """EB-4.3: NO defender-side battle_win credit survives in either
        combat copy — the +3 per defensive win vs decay cap 3 is what
        pinned the bar at 91–97.

        Review [8] found the first cut of this pin INERT: it anchored a
        char-window at the FIRST of the file's five `elif defender_won:`
        occurrences, 13,000 characters short of the removal site, so
        re-adding the credit passed the pin. Re-pinned as a whole-file
        CALL-SITE census: every `add_threat(... "battle_win" ...)` call
        in both combat copies is enumerated and each must credit the
        ATTACKER — a defender-crediting call anywhere in either file
        fails, wherever it is inserted."""
        import re
        call_re = re.compile(r'add_threat\([^)]*"battle_win"[^)]*\)')

        def _strip_comments(src):
            # census CODE only — the removal-site comment quotes the old
            # call and must not satisfy (or fail) the pin
            return "\n".join(line for line in src.splitlines()
                             if not line.lstrip().startswith("#"))

        exec_src = _strip_comments(
            (Path(__file__).resolve().parents[1] / "backend"
             / "commands" / "combat_executor.py").read_text(encoding="utf-8"))
        exec_calls = call_re.findall(exec_src)
        assert exec_calls == [
            'add_threat(world, 3, "battle_win", target=attacker.nation)'
        ], (
            f"combat_executor battle_win call census changed: {exec_calls} "
            f"— only the attacker-crediting call may exist (EB-4.3)")
        ws_src = _strip_comments(
            (Path(__file__).resolve().parents[1] / "backend" / "models"
             / "world_state.py").read_text(encoding="utf-8"))
        ws_calls = call_re.findall(ws_src)
        assert ws_calls == [
            'add_threat(self, 3, "battle_win", target=marshal.nation)'
        ], (
            f"world_state battle_win call census changed: {ws_calls} "
            f"— only the auto-charge ATTACKER arm may credit (EB-4.3; "
            f"`marshal` is the charging attacker in that scope)")

    def test_attacker_win_still_feeds_the_alarm(self, world):
        """Europe still fears the conqueror: the attacker-side credit and
        BOTH decisive_victory arms survive."""
        exec_src = (Path(__file__).resolve().parents[1] / "backend"
                    / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        attacker_arm = exec_src.index("if attacker_won and attacker.nation:")
        window = exec_src[attacker_arm:attacker_arm + 600]
        assert '"battle_win"' in window
        assert exec_src.count('"decisive_victory"') >= 2

    def test_mirror_reads_fight_while_the_coalition_marches(self, world):
        """EB-4.4: with boot threat 70 the bar alone reads 'coerce' — but
        the Third Coalition is AT WAR with France, so the mirror forces
        the honest 'fight' rung."""
        from backend.game_logic.intent import get_france_perceived_intent
        price, weight, _ = get_france_perceived_intent(world)
        assert price == "fight"
        assert weight == 70

    def test_mirror_relaxes_when_the_coalition_is_gone(self, world):
        from backend.game_logic.intent import get_france_perceived_intent
        world.active_coalition = None
        price, _, _ = get_france_perceived_intent(world)
        assert price == "coerce"  # the bar's own honest rung at 70

    def test_establishment_term_is_now_measurable(self, world):
        """CA8-D5's question answered: +1/turn on a bar at ~70 moves it
        (the cap is 100, headroom 30); at the old 91–97 it was clamp-noise.
        Structural statement, pinned as arithmetic."""
        from backend.game_logic.coalition import add_threat
        before = world.threat_level
        add_threat(world, 1, "military_establishment")
        assert world.threat_level == before + 1


# ═══════════════════ EB-3 / EWC-F2 — the docket ═════════════════════════════


class TestRenteFaceIgnoresTransientDisruption:
    """EWC-F2: a hostile army standing on the estate at grant time must not
    lock an oversized pension (face reads estate income WITHOUT the
    disruption term; satisfaction keeps it)."""

    def test_face_is_undisturbed_by_a_passing_army(self, world):
        from backend.game_logic.dotation import (
            compute_rente_face, get_estate_income, get_expectation)
        marshal = next(m for m in world.marshals.values()
                       if m.nation == "France" and m.strength > 0)
        estate = next(r for r in world.get_nation_regions("France")
                      if r not in world.nation_starting_regions["France"]) \
            if any(r not in world.nation_starting_regions["France"]
                   for r in world.get_nation_regions("France")) else None
        if estate is None:
            # conquer one for the fixture
            estate = next(r for r in world.get_nation_regions("Austria"))
            world.regions[estate].controller = "France"
            world.invalidate_active_nations_cache()
        world.regions[estate].stability = 100
        world.regions[estate].war_damage = 0.0
        marshal.battles_won = 10  # capped expectation
        marshal.dotation_regions.append(estate)

        undisturbed_face = compute_rente_face(marshal, world)

        # a hostile army stands on the estate THIS turn
        enemy = next(m for m in world.marshals.values()
                     if m.nation == "Austria" and m.strength >= 1000)
        enemy.location = estate
        assert get_estate_income(marshal, world) == 0, (
            "satisfaction must keep the disruption rule")
        assert compute_rente_face(marshal, world) == undisturbed_face, (
            "the face must ignore the transient disruption — EWC-F2's "
            "oversized-pension lock")

    def test_expectation_gap_still_prices_the_face(self, world):
        from backend.game_logic.dotation import (
            compute_rente_face, get_expectation)
        marshal = next(m for m in world.marshals.values()
                       if m.nation == "France" and m.strength > 0)
        marshal.battles_won = 10
        assert compute_rente_face(marshal, world) == get_expectation(marshal)


class TestXR4EndowCopy:
    def test_war_torn_estate_flag_reaches_the_reward_options(self, world):
        """XR-4 pre-flight: a 0g estate option carries war_torn=True so the
        dialog can warn BEFORE the player commits."""
        from backend.game_logic.marshal_overview import _build_estates
        marshal = next(m for m in world.marshals.values()
                       if m.nation == "France" and m.strength > 0)
        marshal.battles_won = 10
        # conquer a province and leave it war-torn
        estate = next(iter(world.get_nation_regions("Austria")))
        world.regions[estate].controller = "France"
        world.regions[estate].stability = 10  # hostile tier → 0 income
        world.invalidate_active_nations_cache()
        block = _build_estates(marshal, world)
        rows = {d["region"]: d for d in block["eligible_estate_details"]}
        # Review [10]: HARD assert — the `if estate in rows` guard made
        # this pin structurally degradable to a silent no-op.
        assert estate in rows, (
            f"the staged war-torn fixture ({estate}) fell out of the "
            f"eligible rows — the XR-4 pin has nothing to test "
            f"(rows: {sorted(rows)})")
        assert rows[estate]["war_torn"] is True
        assert rows[estate]["occupied"] is False
        assert rows[estate]["income"] == 0

    def test_occupied_estate_flag_names_the_other_mechanism(self, world):
        """Review [4]: a DISRUPTED estate (hostile army standing on it) is
        `occupied`, never `war_torn` — its revenues return when the army
        leaves, not as stability grows (stability is FALLING under it)."""
        from backend.game_logic.marshal_overview import _build_estates
        marshal = next(m for m in world.marshals.values()
                       if m.nation == "France" and m.strength > 0)
        marshal.battles_won = 10
        estate = next(iter(world.get_nation_regions("Austria")))
        world.regions[estate].controller = "France"
        world.regions[estate].stability = 100  # healthy — only disruption zeroes it
        world.invalidate_active_nations_cache()
        # a hostile army stands on it
        enemy = next(m for m in world.marshals.values()
                     if m.nation == "Austria" and m.strength >= 1000)
        enemy.location = estate
        world.diplomatic_states[
            world._make_diplo_key("France", "Austria")] = "WAR"
        assert estate in world.get_disrupted_regions()
        block = _build_estates(marshal, world)
        rows = {d["region"]: d for d in block["eligible_estate_details"]}
        assert estate in rows, f"fixture fell out of eligibility ({sorted(rows)})"
        assert rows[estate]["occupied"] is True
        assert rows[estate]["war_torn"] is False

    def test_result_copy_carries_the_recovery_clause(self, world):
        """XR-4 result half: endowing a war-torn province states that the
        revenues recover as stability does (source-level pin)."""
        src = (Path(__file__).resolve().parents[1] / "backend" / "commands"
               / "economy_executor.py").read_text(encoding="utf-8")
        assert "revenues will recover as the" in src
        assert "stability does" in src


# ═══════════════ review-round pins (the Aug-7 find→refute fleet) ════════════


class TestShownEqualsApplied:
    """Review [1]: both end-turn banners used to RECOMPUTE
    calculate_turn_income after the phase — the Charges of Empire figure
    shown was computed on the POST-income chest and was never the one
    charged. The banners now read the transient applied-result cache."""

    def test_advance_turn_stores_the_applied_results(self, world):
        _peace_out(world, "France")
        world.nation_gold["France"] = 10_000
        world.advance_turn()
        stored = getattr(world, "_income_phase_results", {}).get("France")
        assert stored is not None, (
            "_advance_turn_internal must cache the applied income-phase "
            "results for the turn's financial banners")
        # the applied charge was computed on the PRE-income 10,000 chest
        assert stored["state_charges"] == (
            (10_000 - CHARGES_HOARD_FLOOR) * CHARGES_CROWN_BASE
            // WAR_EFFORT_DIVISOR)

    def test_end_turn_banner_quotes_the_applied_charge(self, world):
        """E2E through the real end-turn path (the meta executor, the CA8-10
        direct-call idiom): the banner's Charges figure equals the stored
        APPLIED one, not a post-income recompute."""
        from backend.commands.executor import CommandExecutor
        world.nation_gold["France"] = 10_000
        executor = CommandExecutor()
        result = executor._meta._execute_end_turn(
            {"action": "end_turn"}, {"world": world})
        stored = getattr(world, "_income_phase_results", {}).get("France")
        assert stored is not None, "end_turn must run the income phase"
        applied = int(stored["state_charges"])
        assert applied > 0, (
            "fixture: a 10,000g war chest must be charged — if this is 0 "
            "the fixture no longer stages the mechanic")
        assert f"Charges of Empire: -{applied}g" in result["message"], (
            f"the end-turn banner must quote the applied charge "
            f"({applied}) — a recompute reads the post-income chest")


class TestOverseasSaveBackfill:
    """Review [12]: fleets round-trip verbatim, so a pre-EB-2 Europe save
    would silently never receive the authored colonial pool. from_dict
    backfills MISSING overseas_income keys (the IGR-E precedent)."""

    def test_pre_eb2_save_receives_the_pool_at_load(self, world):
        data = world.to_dict()
        for rec in data["fleets"].values():
            if isinstance(rec, dict):
                rec.pop("overseas_income", None)
        loaded = WorldState.from_dict(data)
        from backend.game_logic.naval import overseas_trade_income
        assert overseas_trade_income(loaded, "Britain") == 307
        assert loaded.calculate_turn_income("Portugal")["overseas"] == 150

    def test_an_authored_value_is_never_clobbered(self, world):
        """The backfill touches MISSING keys only — a modded 0 (or any
        authored value) round-trips untouched."""
        data = world.to_dict()
        data["fleets"]["Britain"]["overseas_income"] = 0
        loaded = WorldState.from_dict(data)
        from backend.game_logic.naval import overseas_trade_income
        assert overseas_trade_income(loaded, "Britain") == 0

    def test_backfill_map_matches_the_shipped_scenario(self):
        """THE DRIFT PIN that makes the deliberate duplication safe: the
        backfill constant equals the scenario's authored values exactly.
        Re-author the scenario → this fails until the constant follows."""
        import json
        from backend.game_logic.naval import OVERSEAS_INCOME_BACKFILL
        navies = json.load(open(SCENARIO_PATH, encoding="utf-8"))["navies"]
        authored = {
            nation: row["overseas_income"]
            for nation, row in navies.items()
            if isinstance(row, dict) and "overseas_income" in row
        }
        assert OVERSEAS_INCOME_BACKFILL == authored


# ═══════════════════ the ledger identity, with everything live ═══════════════


class TestFullStackReconciliation:
    def test_net_identity_with_charges_requisitions_and_overseas_live(self, world):
        """The SC-33 identity with all three new components non-zero at
        once (Britain: overseas + charges; Austria: requisitions)."""
        from tests.test_economy_ledger_reconciliation import NET_GOLD_COMPONENTS
        world.nation_gold["Britain"] = 12_000
        world.war_exhaustion["Britain"] = 60
        for nation in ("Britain", "Austria"):
            econ = _build_economy(world, nation)
            total = sum(sign * int(econ.get(key, 0))
                        for key, sign in NET_GOLD_COMPONENTS.items())
            assert total == int(econ["net"]), (
                f"{nation}: net {econ['net']} != signed sum {total}")
        assert _build_economy(world, "Austria")["requisitions"] > 0
        britain = _build_economy(world, "Britain")
        assert britain["overseas"] > 0
        assert britain["state_charges"] > 0
