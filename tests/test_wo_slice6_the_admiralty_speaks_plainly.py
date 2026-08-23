"""WO slice 6 — "The Admiralty Speaks Plainly" (WEIRD_OUTCOMES_SPEC §3
slice 6).

Every defect measured on the real 1805 board before a line was written,
and the spec's own account of several of them was WRONG — the recon
fleet's corrections are recorded in the landing record and are the reason
this slice is not what §3 describes.

THE BLOCKADE ORDER, verbatim at boot::

    "The fleet stands out to sea on blockade. Every port of every enemy is
     watched at once (currently: Austria, Britain, Russia) — their crews
     rot at anchor while ours drill. Our own coasts go unguarded."

and the Admiralty chip beside it, `note: "closes Austria, Britain,
Russia"`. Both sets were built the same way — *every at-war court with a
`navies` row* — and never intersected with the pin predicate::

    Austria  ships=0    our coverage 31.5 >= threshold   0.0  -> PINNED
    Russia   ships=20   our coverage 31.5 >= threshold  16.2  -> PINNED
    Britain  ships=100  our coverage 31.5 <  threshold 125.0  -> NOT

So one of the three named courts was false, and it was the one that
matters. The drill clause was inverted three ways at once: France is
herself blockaded at boot and loses 5 readiness a turn toward the floor
(`_readiness_tick` short-circuits on the blockaded arm before any posture
credit); Britain, blockading, sits at her ceiling; and of the three courts
named only Russia rots at all, Austria having no ships to rot.

THE OVER-LIFT REFUSAL, verbatim, identical on every soil::

    "The transports can lift 15,000 men; Soult commands 30,000. Detach the
     excess first ('Soult, garrison 15,000 men here') — small expeditions
     slip past, armies do not."

Driven through the real `_execute_garrison`, that remedy fails on FRENCH
soil at boot for every marshal (`GARRISON_MAX_PER_NATION` 3 and France
holds 3), fails outright on unheld soil, and could not take the quoted
amount in any case — the verb detaches a fixed 3,000. `garrison` is the
only verb in `VALID_ACTIONS` that reduces a marshal's strength, so for a
30,000-man corps there is frequently no road at all.

THE ADMIRALTY'S CORPS TERM read `"march a corps to a yard"` — advice true
for exactly ONE of France's eight corps at boot, the other seven being
above the lift.

THE GRAND DIVERSION's confirm opened `MARSHAL ASKS:` — it stamps no
subject, and it has no marshal to stamp: `_execute_naval_diversion` never
reads `world.marshals`, `resolve_diversion` is nation-keyed, and the
parser refuses "Villeneuve, order the diversion".

THE SHUT-CROSSING refusal ended "or land a small expedition where the
patrols are thin" for every corps, including one twice the lift.
"""

import re
from pathlib import Path

import pytest

from backend.commands.economy_executor import EconomyExecutor
from backend.commands.executor import CommandExecutor
from backend.game_logic import naval
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
    return WorldState.from_dict(world1805.to_dict())


# ════════════════════════════════════════════════════════════════════════
# 1. WO-14 — the blockade names who it actually closes
# ════════════════════════════════════════════════════════════════════════

class TestTheForecastIsTheOneSource:

    def test_the_boot_pin_delta_is_reproduced_exactly(self, world):
        fc = naval.blockade_forecast(world, "France")
        assert [r["nation"] for r in fc["closes"]] == ["Austria", "Russia"]
        assert [r["nation"] for r in fc["beyond_reach"]] == ["Britain"]
        britain = fc["beyond_reach"][0]
        assert britain["needed"] == 125.0, britain
        assert britain["ours"] < britain["needed"], britain

    def test_the_forecast_agrees_with_the_pin_predicate_after_the_order(
            self, world):
        """The falsifiable join: what the message promises must be what
        `blockaded_nations()` actually delivers once the order lands."""
        before = set(naval.blockaded_nations(world))
        promised = {r["nation"]
                    for r in naval.blockade_forecast(world, "France")["closes"]}
        naval.get_fleet(world, "France")["posture"] = "blockade"
        newly = set(naval.blockaded_nations(world)) - before
        assert promised == newly, (promised, newly)

    def test_the_forecast_never_touches_posture(self, world):
        """It is called by the CHIP while we are still on `guard`, so it
        must be pure — a version that flipped posture to measure would
        leave the world blockading after merely rendering a screen."""
        before = naval.get_fleet(world, "France")["posture"]
        naval.blockade_forecast(world, "France")
        naval.blockade_forecast_sentence(world, "France")
        assert naval.get_fleet(world, "France")["posture"] == before

    def test_a_partner_who_is_not_blockading_is_not_counted(self, world):
        """Coverage pools only same-posture partners — the same rule
        `blockader_against` applies. A forecast that counted an ally still
        at anchor would promise sail that will not sail. (The recon memo's
        own suggested copy quoted 54, the no-posture figure; the predicate
        uses 31.5, and this pins the difference.)"""
        fc = naval.blockade_forecast(world, "France")
        ours = fc["beyond_reach"][0]["ours"]
        unfiltered = naval.combined_effective(world, "France", "Britain")
        assert ours < unfiltered, (ours, unfiltered)
        assert ours == round(naval.combined_effective(
            world, "France", "Britain", match_posture="blockade"), 1)

    def test_the_rendered_figure_is_the_one_the_predicate_uses(self, world):
        """REPAIRED: the record claimed the copy "uses 31.5, not 53.82 …
        Pinned", but the pin asserted the producer DICT. Swapping the
        rendered figure for the unfiltered `combined_effective` left 386
        naval tests green — the boot message would have read "54
        sail-effective" while the gate used 31.5."""
        msg = naval.blockade_forecast_sentence(world, "France")
        filtered = naval.combined_effective(
            world, "France", "Britain", match_posture="blockade")
        unfiltered = naval.combined_effective(world, "France", "Britain")
        assert round(filtered) != round(unfiltered), (filtered, unfiltered)
        assert f"{filtered:.0f} sail-effective" in msg, msg
        assert f"{unfiltered:.0f} sail-effective" not in msg, msg

    def test_a_refusal_never_sits_beside_two_identical_numbers(self, world):
        """Reachable at 26 sail / readiness 97 against our 31.5: the row
        classifies on raw floats and rendered at :.0f, so the sentence read
        "32 against her, where 32 is needed"."""
        rec = naval.get_fleet(world, "Britain")
        rec["ships"], rec["readiness"] = 26, 97
        msg = naval.blockade_forecast_sentence(world, "France")
        # REPAIRED: the first version accepted the "by a hair" fallback as
        # an alternative, so a mutation that stopped escalating precision
        # simply took that branch and the pin proved nothing. This case
        # (31.5 against 31.525) IS separable — at two decimals — and the
        # copy must separate it rather than retreat to the fallback.
        m = re.search(r"([\d.]+) sail-effective against her, where "
                      r"([\d.]+) is needed", msg)
        assert m, msg
        assert m.group(1) != m.group(2), msg
        assert "where 32 is needed" not in msg, msg
        assert "by a hair" not in msg, msg

    def test_the_self_blockade_is_reported(self, world):
        """France is blockaded by Britain at boot — which is the whole
        reason the drill claim was inverted."""
        assert naval.blockade_forecast(
            world, "France")["self_blockaded_by"] == "Britain"


class TestTheOrderTellsTheTruth:

    def _order(self, world, posture="blockade"):
        ex = CommandExecutor()
        return ex._naval._execute_set_fleet_posture(
            {"action": "set_fleet_posture", "posture": posture},
            {"world": world})["message"]

    def test_the_order_no_longer_promises_britain(self, world):
        msg = self._order(world)
        assert "Austria and Russia are closed" in msg, msg
        assert "Britain is beyond our reach" in msg, msg
        assert "125" in msg and "sail-effective" in msg, msg

    def test_a_single_closed_court_takes_a_singular_possessive(self, world):
        """The boot board closes TWO courts, so "their" is correct there
        and a mutation to a hardcoded plural survived. Reachable one peace
        treaty from boot, and it sits in the same sentence as a "her"."""
        world.diplomatic_states[
            world._make_diplo_key("France", "Austria")] = "PEACE"
        msg = self._order(world)
        assert "Russia is closed — her ports watched and her trade halved" \
            in msg, msg
        assert "their" not in msg, msg

    def test_the_inverted_drill_claim_is_gone(self, world):
        msg = self._order(world)
        assert "while ours drill" not in msg, msg
        # ...and the truth is stated in its place.
        assert "our own crews go on rotting" in msg, msg

    def test_the_guard_order_does_not_lift_a_pressure_it_never_applied(
            self, world):
        """The mirror falsity: "Blockade pressure on the enemy is lifted"
        was unconditional, so a fleet that had pinned nobody announced
        relieving a siege it never laid."""
        msg = self._order(world, posture="guard")
        assert "No blockade pressure is lifted" in msg, msg
        # ...and after a real blockade it DOES name who is released.
        self._order(world, posture="blockade")
        msg2 = self._order(world, posture="guard")
        # Russia has a fleet; Austria's authored row is ships-0, so the
        # review-round split names her trade rather than her crews.
        assert "Russia is released, and her crews will begin to recover"             in msg2, msg2
        assert "Austria has no fleet to recover, but her trade reopens"             in msg2, msg2

    def test_the_order_goes_through_the_display_chokepoint(self, world):
        """R7. Producer 2 got this at NV-9; producer 1 joined raw scenario
        tags, so "closes KingdomOfItaly" was reachable the moment Italy
        entered the war."""
        world.diplomatic_states[
            world._make_diplo_key("France", "KingdomOfItaly")] = "WAR"
        world.vassals.pop("KingdomOfItaly", None)
        msg = self._order(world)
        assert "KingdomOfItaly" not in msg, msg

    def test_a_peaceful_blockade_still_reads_sensibly(self, world):
        for key in list(world.diplomatic_states):
            if "France" in key:
                world.diplomatic_states[key] = "PEACE"
        msg = self._order(world)
        assert "no enemy at sea to close" in msg, msg


class TestTheChipForecastsHonestly:

    def _chip(self, world):
        chips = naval.build_admiralty_report(world)["chips"]
        return next(c for c in chips
                    if c.get("command") == "blockade the enemy")

    def test_the_chip_names_what_the_order_would_close_and_what_it_cannot(
            self, world):
        note = self._chip(world)["note"]
        assert "closes Austria and Russia" in note, note
        assert "not Britain" in note and "125 needed" in note, note

    def test_the_chip_does_not_read_the_live_pin_set(self, world):
        """The correction that changes what got built: this chip renders
        only while we are on `guard`, and at that moment
        `blockaded_nations()` returns the courts BRITAIN is pinning —
        France among them. A literal reading of the spec would have told
        the player her own blockade closes her own harbours."""
        assert "France" in naval.blockaded_nations(world)
        note = self._chip(world)["note"]
        assert "France" not in note, note
        assert "Holland" not in note and "Spain" not in note, note

    def test_the_chip_stays_enabled_when_it_would_close_nobody(self, world):
        """Honest availability is saying what the order does, not hiding
        it — the order is still legal and still uncovers our coast."""
        for n in ("Austria", "Russia"):
            world.diplomatic_states[
                world._make_diplo_key("France", n)] = "PEACE"
        chip = self._chip(world)
        assert chip["enabled"] is True, chip
        assert "closes no enemy port" in chip["note"], chip

    def test_the_two_producers_agree(self, world):
        """They disagreed by construction before — two copies of one rule.
        Both now read `blockade_forecast`, so the courts named cannot
        diverge."""
        note = self._chip(world)["note"]
        ex = CommandExecutor()
        msg = ex._naval._execute_set_fleet_posture(
            {"action": "set_fleet_posture", "posture": "blockade"},
            {"world": world})["message"]
        for row in naval.blockade_forecast(world, "France")["closes"]:
            assert row["nation"] in note and row["nation"] in msg


class TestTheHelpNoLongerTeachesTheLie:

    def test_the_third_producer_was_found_and_fixed(self):
        """The spec said "WO-14 at BOTH producers" and named two. The
        `help` text taught the identical false promise to every player
        before they ever issued the order."""
        src = (REPO / "backend" / "commands" / "meta_executor.py"
               ).read_text(encoding="utf-8")
        assert "their crews rot at anchor while ours drill" not in src
        assert "pins EVERY" not in src

    def test_no_producer_anywhere_still_claims_the_drill(self):
        offenders = []
        for path in (REPO / "backend").rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="replace")
            if "while ours drill" in text:
                offenders.append(str(path.relative_to(REPO)))
        assert not offenders, offenders


# ════════════════════════════════════════════════════════════════════════
# 2. The over-lift refusal names a road that exists, or says there is none
# ════════════════════════════════════════════════════════════════════════

class TestTheOverLiftRefusal:

    def test_it_no_longer_advertises_an_illegal_garrison(self, world):
        soult = world.get_marshal("Soult")
        msg = naval.over_lift_refusal(world, soult)
        assert "garrison 15,000 men here" not in msg, msg
        assert "He cannot be lightened" in msg, msg

    def test_it_quotes_the_real_detachment_and_the_real_cap(
            self, world, monkeypatch):
        """REPAIRED: the cap half asserted `str(3) in msg`, which the
        message already satisfies through "3,000" — deleting every render
        of `GARRISON_MAX_PER_NATION` from all three arms left 58 tests
        green. The cap is now monkeypatched to a value whose digits appear
        nowhere else in the sentence."""
        monkeypatch.setattr(EconomyExecutor, "GARRISON_MAX_PER_NATION", 7)
        for r in world.get_nation_regions("France"):
            world.regions[r].garrison_strength = 0
        for i, r in enumerate(world.get_nation_regions("France")):
            if i >= 7:
                break
            world.regions[r].garrison_strength = 1000
        msg = naval.over_lift_refusal(world, world.get_marshal("Soult"))
        assert f"{EconomyExecutor.GARRISON_DETACHMENT_SIZE:,}" in msg, msg
        assert "our 7" in msg and "7 of 7" in msg, msg

    def test_it_names_a_corps_that_could_actually_sail(self, world):
        msg = naval.over_lift_refusal(world, world.get_marshal("Soult"))
        assert "Napoleon" in msg and "10,000" in msg, msg

    def test_it_says_plainly_when_no_corps_is_under_the_lift(self, world):
        for m in world.get_marshals_by_nation("France"):
            m.strength = 30000
        msg = naval.over_lift_refusal(world, world.get_marshal("Soult"))
        assert "No corps of ours is under the lift" in msg, msg

    def test_a_free_slot_changes_the_sentence_but_not_into_a_promise(
            self, world):
        """The falsifiable negative for the arithmetic: even with a slot
        free, five detachments of 3,000 against a cap of 3 is still no
        road, and the copy must say the count rather than wave."""
        for r in world.get_nation_regions("France"):
            if world.regions[r].garrison_strength > 0:
                world.regions[r].garrison_strength = 0
                break
        msg = naval.over_lift_refusal(world, world.get_marshal("Soult"))
        assert "it would take 5 of them" in msg, msg

    def test_the_executor_uses_the_single_source(self, world):
        ex = CommandExecutor()
        soult = world.get_marshal("Soult")
        soult.location = naval.controlled_dockyards(world, "France")[0]
        world._build_marshal_index()
        res = ex._naval._execute_naval_expedition(
            {"action": "naval_expedition", "marshal": "Soult",
             "target": "Munster"}, {"world": world})
        # UNCONDITIONAL. The first version guarded this behind
        # `if res.get("success") is False and "transports lift" in ...`,
        # which the mutation sweep proved inert — the guard simply went
        # false when the message changed. This is the shape slice 16 found
        # twice already in this suite.
        assert res["success"] is False, res
        assert res["message"] == naval.over_lift_refusal(world, soult), res


# ════════════════════════════════════════════════════════════════════════
# 3. The Admiralty's corps term, and the Diversion's subject
# ════════════════════════════════════════════════════════════════════════

class TestTheCorpsTerm:

    def test_the_boot_advice_names_the_one_corps_it_is_for(self, world):
        detail = naval.build_admiralty_report(
            world)["expedition_terms"][1]["detail"]
        assert "Napoleon" in detail, detail
        for big in ("Soult", "Massena", "Ney", "Davout"):
            assert big not in detail, (big, detail)

    def test_it_says_so_when_no_corps_is_under_the_lift(self, world):
        for m in world.get_marshals_by_nation("France"):
            m.strength = 30000
        detail = naval.build_admiralty_report(
            world)["expedition_terms"][1]["detail"]
        assert "no corps of ours is under the" in detail, detail

    def test_the_over_corps_arm_stops_promising_a_detachment(self, world):
        """Arm 2 said "detach N first" with the same false premise as the
        refusal it mirrors."""
        yards = naval.controlled_dockyards(world, "France")
        soult = world.get_marshal("Soult")
        soult.location = yards[0]
        for m in world.get_marshals_by_nation("France"):
            if m.name != "Soult":
                m.strength = 30000
        world._build_marshal_index()
        detail = naval.build_admiralty_report(
            world)["expedition_terms"][1]["detail"]
        assert "over the lift" in detail, detail
        assert "a garrison sheds only" in detail, detail


class TestTheDiversionHasASubject:

    def _payload(self, world):
        ex = CommandExecutor()
        return ex._naval._execute_naval_diversion(
            {"action": "naval_diversion",
             "raw_command": "order the diversion"}, {"world": world})

    def test_the_modal_no_longer_opens_MARSHAL_ASKS(self, world):
        res = self._payload(world)
        assert res.get("state") == "awaiting_clarification", res
        assert res.get("marshal") == "The Admiralty", res
        # This is exactly what `clarification_popup.gd:39` renders.
        assert str(res["marshal"]).upper() + " ASKS:" == "THE ADMIRALTY ASKS:"

    def test_the_subject_reads_correctly_in_the_terminal_line_too(
            self, world):
        """Two client consumers, not one: `main.gd` also prints
        "<name> requests clarification". A subject chosen for the
        upper-cased title alone could read badly there."""
        subject = self._payload(world)["marshal"]
        assert subject[0].isupper() and not subject.isupper(), subject

    def test_the_subject_is_not_an_admiral_that_may_not_exist(self):
        """4 of the 10 authored fleets have no `admiral` row, so
        `rec.get("admiral")` would render a bare None for them — and the
        popup's `.get()` default does not fire on a present-but-null key
        (the CR-2 trap)."""
        src = (REPO / "backend" / "commands" / "naval_executor.py"
               ).read_text(encoding="utf-8")
        block = src.split("The Grand Diversion is drawn up", 1)[0][-900:]
        assert '"marshal": "The Admiralty"' in block
        assert 'rec.get("admiral")' not in block


# ════════════════════════════════════════════════════════════════════════
# 4. The SHUT crossing stops advertising an expedition it cannot carry
# ════════════════════════════════════════════════════════════════════════

class TestTheShutRefusalIsCorpsAware:

    def _shut(self, world):
        for pair in naval.get_sea_link_pairs(world):
            a, b = tuple(pair)
            for x, y in ((a, b), (b, a)):
                if naval.crossing_check(
                        world, "France", x, y)["verdict"] == "shut":
                    return x, y
        pytest.skip("no shut crossing on the boot board")

    def test_a_corps_over_the_lift_is_not_offered_an_expedition(
            self, world):
        x, y = self._shut(world)
        msg = naval.crossing_check(world, "France", x, y,
                                   mover_strength=30000)["message"]
        assert "no expedition can carry it" in msg, msg
        assert "land a small expedition" not in msg, msg

    def test_a_corps_under_the_lift_still_is(self, world):
        x, y = self._shut(world)
        msg = naval.crossing_check(world, "France", x, y,
                                   mover_strength=10000)["message"]
        assert "land a small expedition" in msg, msg

    def test_a_caller_that_knows_nothing_keeps_the_old_sentence(
            self, world):
        x, y = self._shut(world)
        msg = naval.crossing_check(world, "France", x, y)["message"]
        assert "land a small expedition" in msg, msg

    def test_the_verdict_itself_is_untouched(self, world):
        """Message-only at every one of the seams that inherit this
        predicate: `allowed` and `verdict` are computed before the remedy
        clause and must not move with it."""
        x, y = self._shut(world)
        base = naval.crossing_check(world, "France", x, y)
        for strength in (1, 10000, 30000, 999999):
            other = naval.crossing_check(world, "France", x, y,
                                         mover_strength=strength)
            assert other["allowed"] == base["allowed"]
            assert other["verdict"] == base["verdict"]
            assert other["coverage"] == base["coverage"]

    def test_every_marshal_aware_seam_threads_the_corps(self):
        """REPLACED after the review round. The first version was a
        file-wide `re.search` satisfied by ONE occurrence per file — and
        measured, only 2 of SIX marshal-aware seams threaded it, so the
        seam an ordinary `attack` hits still printed the retired advice:

            [MOVE ]  ... no expedition can carry it.
            [ATTACK] ... or land a small expedition (15,000 men or fewer).

        This counts the call sites instead."""
        import ast
        threaded = unthreaded = 0
        for rel in ("backend/commands/movement_executor.py",
                    "backend/commands/combat_executor.py"):
            tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                fn = getattr(node.func, "id", None)
                if fn not in ("crossing_check", "crossing_check_reach"):
                    continue
                has = (any(k.arg == "mover_strength" for k in node.keywords)
                       or len(node.args) >= 5)
                if has:
                    threaded += 1
                else:
                    unthreaded += 1
        assert unthreaded == 0, f"{unthreaded} seam(s) do not pass the corps"
        assert threaded >= 5, threaded


class TestTheRetiredAdviceIsGoneFromEverySurface:
    """The review round's verdict, as tests. Three of its four P2s were the
    same shape — a rewritten producer with an un-rewritten sibling still
    shipping the retired sentence — and the record asserted each census was
    complete when it measurably was not."""

    def _shut_pair(self, world):
        for pair in naval.get_sea_link_pairs(world):
            a, b = tuple(pair)
            for x, y in ((a, b), (b, a)):
                if (naval.crossing_check(world, "France", x, y)["verdict"]
                        == "shut"):
                    return x, y
        pytest.skip("no shut crossing on the boot board")

    def test_the_reach_gate_no_longer_offers_the_expedition(self, world):
        """The seam an ordinary attack hits."""
        x, y = self._shut_pair(world)
        under = naval.crossing_check_reach(world, "France", x, y, 10000)
        over = naval.crossing_check_reach(world, "France", x, y, 30000)
        assert "land a small expedition" in under["message"], under
        assert "no expedition can carry it" in over["message"], over

    def test_the_region_panel_shares_the_single_source(self, world):
        """Measured before the fix: 28 blocked provinces read "detach
        15,000 first" while the executor, one order later, said he could
        not be lightened at all — and the panel is the surface the player
        sees FIRST, on a province click, with no order issued."""
        soult = world.get_marshal("Soult")
        soult.location = naval.controlled_dockyards(world, "France")[0]
        world._build_marshal_index()
        reasons = naval.expedition_blocked_reasons(world, "France")
        quoting = [k for k, v in reasons.items()
                   if "transports lift" in str(v)]
        assert quoting, "the over-lift reason is unreachable on the panel"
        honest = naval.over_lift_refusal(world, soult)
        for k in quoting:
            assert honest in str(reasons[k]), (k, reasons[k])
        assert not any("detach" in str(v) and "first" in str(v)
                       for v in reasons.values()), reasons

    def test_the_posture_prompt_is_the_fourth_producer(self, world):
        """It sat eight lines above the message the slice rewrote, and
        contradicted the `help` text the same commit fixed."""
        ex = CommandExecutor()
        res = ex._naval._execute_set_fleet_posture(
            {"action": "set_fleet_posture"}, {"world": world})
        assert res["success"] is False, res
        assert "every at-war enemy's ports" not in res["message"], res
        assert "our sail can outmatch" in res["message"], res

    def test_no_surface_promises_to_close_every_at_war_enemy(self):
        """The census the first cut greped only for `while ours drill`."""
        offenders = []
        for path in (REPO / "backend").rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="replace")
            for phrase in ("close every at-war enemy",
                           "pins EVERY", "while ours drill",
                           "Every port of every enemy"):
                if phrase in text:
                    offenders.append((str(path.relative_to(REPO)), phrase))
        assert not offenders, offenders


class TestThePromiseArmConsultsTheGate:
    """F4: the positive arm was location-blind, and it was the one arm no
    test executed."""

    @staticmethod
    def _free_a_slot(world):
        for r in world.get_nation_regions("France"):
            if world.regions[r].garrison_strength > 0:
                world.regions[r].garrison_strength = 0
                return

    def test_it_does_not_promise_a_garrison_where_one_already_stands(
            self, world):
        self._free_a_slot(world)
        bern = world.get_marshal("Bernadotte")
        bern.strength, bern.location = 17000, "Flanders"
        world._build_marshal_index()
        msg = naval.over_lift_refusal(world, bern)
        assert "would bring him under the lift" not in msg, msg
        assert "A garrison already holds Flanders" in msg, msg

    def test_it_does_not_promise_a_garrison_on_a_beachhead(self, world):
        self._free_a_slot(world)
        bern = world.get_marshal("Bernadotte")
        foreign = next(r for r, rg in world.regions.items()
                       if rg.controller not in (None, "France")
                       and getattr(rg, "is_coastal", False))
        bern.strength, bern.location = 17000, foreign
        world._build_marshal_index()
        msg = naval.over_lift_refusal(world, bern)
        assert "would bring him under the lift" not in msg, msg
        assert "We do not control" in msg, msg

    def test_the_promise_is_kept_when_the_gate_would_allow_it(self, world):
        """The falsifiable negative — the gate must not silence advice that
        actually works."""
        self._free_a_slot(world)
        bern = world.get_marshal("Bernadotte")
        bern.strength, bern.location = 17000, "Brittany"
        world._build_marshal_index()
        msg = naval.over_lift_refusal(world, bern)
        assert "would bring him under the lift" in msg, msg
        assert EconomyExecutor.garrison_refusal_probe(world, bern) is None

    def test_the_probe_is_the_executors_own_gate_not_a_copy(self):
        """PF-4's `move_refusal_probe` pattern: `_execute_garrison` must
        CALL the probe, not carry a second implementation."""
        src = (REPO / "backend" / "commands" / "economy_executor.py"
               ).read_text(encoding="utf-8")
        body = src.split("def _execute_garrison(", 1)[1][:6000]
        assert "self.garrison_refusal_probe(world, marshal)" in body
        assert "We cannot garrison enemy territory" not in body, (
            "the executor kept its own copy of a gate the probe owns")

    def test_the_refusal_never_contradicts_itself(self, world):
        """The promise arm and the closing arm were independent, so the
        sentence could offer a detachment and then say nothing can sail."""
        self._free_a_slot(world)
        for m in world.get_marshals_by_nation("France"):
            m.strength = 17000
        bern = world.get_marshal("Bernadotte")
        bern.location = "Brittany"
        world._build_marshal_index()
        msg = naval.over_lift_refusal(world, bern)
        assert not ("would bring him under the lift" in msg
                    and "none can sail" in msg), msg


class TestTheReleaseClauseIsMembership:
    """F3: release is a membership question. A court a second power also
    pins stays pinned when we stand down."""

    def test_a_court_another_power_also_pins_is_not_announced_released(
            self, world):
        world.diplomatic_states[
            world._make_diplo_key("Britain", "Russia")] = "WAR"
        ex = CommandExecutor()
        ex._naval._execute_set_fleet_posture(
            {"action": "set_fleet_posture", "posture": "blockade"},
            {"world": world})
        msg = ex._naval._execute_set_fleet_posture(
            {"action": "set_fleet_posture", "posture": "guard"},
            {"world": world})["message"]
        assert "Russia" in naval.blockaded_nations(world), "setup failed"
        assert "Russia is released" not in msg, msg

    def test_the_forecast_is_invariant_to_our_own_posture(self, world):
        """The record's stated reason for the pre-read was FALSE and is
        corrected: `combined_effective` adds our own strength
        unconditionally and `match_posture` filters PARTNERS only. The
        pre-read is needed because the release list is a set DIFFERENCE,
        not because the forecast moves."""
        rec = naval.get_fleet(world, "France")
        rec["posture"] = "guard"
        on_guard = naval.blockade_forecast(world, "France")
        rec["posture"] = "blockade"
        on_blockade = naval.blockade_forecast(world, "France")
        assert on_guard == on_blockade, (on_guard, on_blockade)
