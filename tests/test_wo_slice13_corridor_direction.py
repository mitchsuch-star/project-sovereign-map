"""WO-17 "The Corridor Has a Direction" — Weird-Outcomes slice 13.

Build contract: `docs/WEIRD_OUTCOMES_SPEC.md` §3 slice 13 (authoritative);
never-do 20 and 21 bind this slice directly. The system under amendment is
WIN-D3 (`docs/WAR_WITHDRAWAL_SPEC.md` §7a; `backend/game_logic/withdrawal.py`).

THE DEFECT (hand-verified, filed as BUG_FIXES §WO row WO-17): the evacuation
grant was pair-scoped and direction-less — `has_evacuation_grant` a bare
`(pair_key → expiry)` compare consumed by the ONE `can_enter_territory` arm,
no marshal, no direction, no stranded check — and it opens on ANY WAR→non-WAR
edge INCLUDING ARMISTICE. Park one corps deep on enemy soil, sign a 1-DP
armistice, and march FRESH corps into enemy sovereign territory all truce
long; the walked-in corps register "stranded" and hold the corridor open;
war auto-resumes free with the army already beside Vienna.

THE FIX: the permission arm gains a direction term — the grant belongs to a
corps that cannot reach the body of its own realm without it (`is_stranded_at`,
the same predicate that decides who receives a road-home order). A mover that
could already walk home — standing in the home zone, on allied soil, or on
at-war third-party soil — has no claim on the corridor. Zero new serialized
fields; the term is memoised per (nation, location) in the transient
`world._evac_direction_cache`, flushed at the `invalidate_bloc_members_cache`
chokepoint (GR8).

Several tests carry a CONTROL ARM that disables `CORRIDOR_DIRECTION_ACTIVE`
and reproduces the exploit — without it, "the Trojan march is refused" could
pass for reasons having nothing to do with this slice.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import withdrawal as W
from backend.game_logic.diplomacy import can_enter_territory, set_diplomatic_state
from backend.models.world_state import WorldState

SCENARIO = "godot-client/project-sovereign/assets/maps/europe_1805.json"

# Volhynia and its enclosure — the WIN-D3 measured shape's geography. If the
# map ever drifts, the staging assertions below fail loudly.
ENCLAVE = "Volhynia"
ENCLOSURE = {"Volhynia", "White Russia", "Lithuania", "Ukraine", "Vilna"}


@pytest.fixture(scope="module")
def base_world():
    return WorldState.from_scenario(SCENARIO)


@pytest.fixture
def world(base_world):
    return WorldState.from_dict(base_world.to_dict())


def _park_everyone(world, stranded_name="Davout"):
    """The single-subject fixture idiom from test_win_d3_road_home: every
    French corps at Paris except the stranded one; every Russian corps at
    the Russian capital, so the corridor can only ever be about OUR corps."""
    for m in list(world.marshals.values()):
        if m.nation == "France" and m.name != stranded_name:
            m.location = "Paris"
        elif m.nation == "Russia":
            m.location = world.get_nation_capital("Russia")


def _stage_trojan_shape(world, truce_state="ARMISTICE"):
    """The full filed exploit, staged deterministically.

    1. Davout stranded at French-held Volhynia (all four neighbours Russian)
       — the corps whose stranding legitimately opens and HOLDS the corridor.
    2. A contiguous French chain from Paris to the Russian frontier, flipped
       province by province along a real land path that avoids Volhynia's
       enclosure (so Davout stays genuinely stranded). Its tip is the
       LAUNCHPAD: home-zone soil one march from Russian sovereign territory.
    3. Ney, the fresh corps, on the launchpad.
    4. The 1-DP truce (ARMISTICE by default — the exploit's own instrument).

    Returns (davout, ney, launchpad, target) where `target` is the Russian
    province one march from the launchpad.
    """
    # The slice is not about the navy: blank the fleets store so no staged
    # hop can trip the DEF-5 crossing gate for naval reasons.
    world.fleets = {}

    world.regions[ENCLAVE].controller = "France"
    _park_everyone(world)
    davout = world.marshals["Davout"]
    davout.location = ENCLAVE

    # Find the nearest Russian province OUTSIDE the enclosure reachable from
    # Paris without touching it, and flip every hop short of it to France.
    best = None
    for name in sorted(world.regions):
        region = world.regions[name]
        if region.controller != "Russia" or name in ENCLOSURE:
            continue
        path = world.find_path("Paris", name,
                               avoid_regions=sorted(ENCLOSURE - {name}))
        if path and len(path) >= 2 and (best is None or len(path) < len(best[1])):
            best = (name, path)
    assert best is not None, (
        "staging drifted: no Russian frontier province reachable from Paris")
    target, path = best
    for hop in path[:-1]:
        world.regions[hop].controller = "France"
    world.invalidate_active_nations_cache()
    launchpad = path[-2]

    # Nobody may already stand on the target (keeps the move refusal about
    # diplomacy, never about enemy presence).
    for m in list(world.marshals.values()):
        if m.location == target:
            m.location = world.get_nation_capital(m.nation) or m.location

    ney = world.marshals["Ney"]
    ney.location = launchpad

    set_diplomatic_state(world, "France", "Russia", "WAR")
    set_diplomatic_state(world, "France", "Russia", truce_state)

    # Staging sanity — the corridor is open and held open by Davout alone.
    assert world.get_diplomatic_state("France", "Russia") == truce_state
    assert "France|Russia" in world.evacuation_grants, (
        "the truce must open the corridor (Davout is stranded)")
    assert launchpad in W.get_home_zone(world, "France"), (
        "the launchpad must be home-zone soil — that is the exploit's shape")
    assert target in world.regions[launchpad].adjacent_regions
    assert world.regions[target].controller == "Russia"
    return davout, ney, launchpad, target


def _move(world, marshal_name, target, strategic=False):
    command = {"action": "move", "marshal": marshal_name, "target": target}
    if strategic:
        command["_strategic_execution"] = True
    return CommandExecutor().execute({"command": command}, {"world": world})


# ══════════════════════════════════════════════════════════════════════════
# THE TROJAN MARCH — the falsifiable negative
# ══════════════════════════════════════════════════════════════════════════

class TestTheTrojanMarch:

    def test_control_arm_reproduces_the_exploit(self, world, monkeypatch):
        """With the direction term disabled, the filed exploit reproduces:
        a FRESH corps on home soil marches into enemy sovereign territory
        under a truce. If this ever stops passing, the fixture has drifted
        and the refusal below could be passing vacuously."""
        monkeypatch.setattr(W, "CORRIDOR_DIRECTION_ACTIVE", False)
        davout, ney, launchpad, target = _stage_trojan_shape(world)

        result = _move(world, "Ney", target)
        assert result.get("success"), result.get("message")
        assert ney.location == target, (
            "control: the direction-less grant carries the Trojan across")
        assert world.regions[target].controller == "Russia", (
            "he is a Trojan, not a conqueror — §3.4 pin 2 held even pre-fix")

    def test_the_trojan_march_is_refused(self, world):
        """The done-when's falsifiable negative: during a truce, a corps
        standing on French home soil is refused entry to enemy sovereign
        territory."""
        davout, ney, launchpad, target = _stage_trojan_shape(world)

        result = _move(world, "Ney", target)
        assert not result.get("success"), (
            "the Trojan march must be refused: " + str(result.get("message")))
        assert ney.location == launchpad
        # The stall machinery must still read the block robustly (PF-8) …
        assert result.get("blocked_diplomatic") == "Russia"
        # … and the player is told the truth: the corridor exists, and it
        # is not for him.
        assert "corridor" in (result.get("message") or "").lower()

    def test_the_refusal_holds_under_a_full_peace_too(self, world):
        """The direction term is state-agnostic — PEACE grants open the same
        corridor and must carry the same direction."""
        davout, ney, launchpad, target = _stage_trojan_shape(
            world, truce_state="PEACE")
        result = _move(world, "Ney", target)
        assert not result.get("success")
        assert ney.location == launchpad

    def test_the_stranded_corps_still_routes_home_through_the_same_provinces(
            self, world):
        """The done-when's positive half: Davout walks his road home through
        Russian sovereign soil — the very provinces Ney was refused — step
        by step through the shared executor."""
        davout, ney, launchpad, target = _stage_trojan_shape(world)

        order = davout.strategic_order
        assert W.is_road_home_order(order), "the treaty issued his road home"
        assert order.path and order.path[0] == davout.location
        crossed_russian_soil = False
        for step in list(order.path[1:]):
            controller = world.regions[step].controller
            if controller == "Russia":
                crossed_russian_soil = True
            result = _move(world, "Davout", step, strategic=True)
            assert result.get("success"), (step, result.get("message"))
        assert crossed_russian_soil, (
            "staging drifted: his road home no longer crosses Russian soil, "
            "so this test no longer proves transit")
        assert davout.location in W.get_home_zone(world, "France")

    def test_the_pathfinder_knows_the_direction(self, world):
        """The route-building half, pinned symmetrically: for the SAME pair
        of endpoints, the passable-for corridor exists outbound from the
        stranded enclave and does not exist inbound from home soil."""
        davout, ney, launchpad, target = _stage_trojan_shape(world)

        homeward = world.find_path(ENCLAVE, launchpad, passable_for="France")
        assert homeward, "the stranded corps must still find its road home"
        trojan = world.find_path(launchpad, ENCLAVE, passable_for="France")
        assert trojan is None, (
            "a home corps must find NO legal corridor into the enclave — "
            f"got {trojan}")


# ══════════════════════════════════════════════════════════════════════════
# THE DIRECTION TERM — unit level, all four launch shapes
# ══════════════════════════════════════════════════════════════════════════

class TestTheDirectionTerm:

    def test_home_zone_mover_is_denied(self, world):
        _stage_trojan_shape(world)
        assert not can_enter_territory(world, "France", "Russia",
                                       mover_location="Paris")

    def test_conquered_but_connected_soil_is_home_too(self, world):
        """The launchpad is home by CONNECTIVITY, not by boot borders —
        proving the term is the zone, not a scenario-authored list."""
        davout, ney, launchpad, target = _stage_trojan_shape(world)
        assert not can_enter_territory(world, "France", "Russia",
                                       mover_location=launchpad)

    def test_the_stranded_enclave_keeps_full_transit(self, world):
        """Own-controlled but DISCONNECTED soil is not home — a bare
        controller compare here would have stranded the measured corps
        forever, which is why the term is the stranded predicate."""
        _stage_trojan_shape(world)
        assert world.regions[ENCLAVE].controller == "France"
        assert can_enter_territory(world, "France", "Russia",
                                   mover_location=ENCLAVE)

    def test_an_allied_soil_launch_is_denied(self, world):
        """The Munich-launch variant: a corps legally parked on an ALLY's
        province with a road home has no claim on the corridor. This is the
        recorded reason the term is `is_stranded_at` rather than bare
        home-zone membership (spec slice 13, landing record)."""
        davout, ney, launchpad, target = _stage_trojan_shape(world)
        # Re-flag the launchpad as an allied court's soil.
        world.regions[launchpad].controller = "Bavaria"
        world.diplomatic_states["Bavaria|France"] = "ALLIANCE"
        world.invalidate_active_nations_cache()
        assert not can_enter_territory(world, "France", "Russia",
                                       mover_location=launchpad), (
            "allied soil with a road home is a launchpad, not a stranding")

    def test_an_at_war_soil_launch_is_denied(self, world):
        """The third variant: a corps standing on a third party's AT-WAR
        soil (which war already lets it cross home) may not slip sideways
        into the truce partner's territory."""
        davout, ney, launchpad, target = _stage_trojan_shape(world)
        world.regions[launchpad].controller = "Austria"
        set_diplomatic_state(world, "France", "Austria", "WAR")
        world.invalidate_active_nations_cache()
        assert not can_enter_territory(world, "France", "Russia",
                                       mover_location=launchpad)

    def test_the_bare_pair_level_form_stays_permissive(self, world):
        """`mover_location=None` keeps the legacy answer, by design: the
        audited nation-level consumers (war_council's anchor derivation)
        are not relocation seams. The census pin below is what keeps that
        set from growing."""
        _stage_trojan_shape(world)
        assert can_enter_territory(world, "France", "Russia")

    def test_gr5_the_ai_filter_carries_the_same_direction(self, world):
        """The AI's candidate gate refuses the Trojan and passes the walker
        with the SAME predicate the player faces."""
        from backend.ai.enemy_ai import EnemyAI
        davout, ney, launchpad, target = _stage_trojan_shape(world)
        ai = EnemyAI(CommandExecutor())
        assert not ai._can_ai_move_to(world, "France", target,
                                      origin=launchpad)
        assert ai._can_ai_move_to(world, "France", target, origin=ENCLAVE)


# ══════════════════════════════════════════════════════════════════════════
# THE GRANT IS SPENT ON ARRIVAL — and the corridor still retires
# ══════════════════════════════════════════════════════════════════════════

class TestTheGrantIsSpentOnArrival:

    def test_arrival_spends_the_grant_for_that_corps_only(self, world):
        """The mutual case: Davout arrives home while a Russian corps is
        still walking OUR soil. The corridor stands — and Davout, now home,
        has no further claim on it, while the Russian walker keeps his."""
        davout, ney, launchpad, target = _stage_trojan_shape(world)
        kutuzov = world.marshals["Kutuzov"]
        kutuzov.location = "Paris"          # stranded deep on French soil
        # Re-open the corridor with the mutual shape in place.
        set_diplomatic_state(world, "France", "Russia", "WAR")
        set_diplomatic_state(world, "France", "Russia", "ARMISTICE")
        assert "France|Russia" in world.evacuation_grants

        home = W.get_home_zone(world, "France")
        davout.location = sorted(home)[0]
        assert not W.is_stranded(world, davout, home)

        assert "France|Russia" in world.evacuation_grants, (
            "the corridor stands while the other signatory's corps walks")
        assert not can_enter_territory(world, "France", "Russia",
                                       mover_location=davout.location), (
            "the moment he reaches the body of his own realm, the grant is "
            "spent for him")
        assert can_enter_territory(world, "Russia", "France",
                                   mover_location=kutuzov.location), (
            "the Russian walker's claim is untouched by Davout's arrival")

    def test_the_corridor_still_retires_when_nobody_is_stranded(self, world):
        """Done-when: retirement is unchanged — the corridor closes because
        it is finished, and the frontier shuts in every form."""
        davout, ney, launchpad, target = _stage_trojan_shape(world)
        for m in list(world.marshals.values()):
            if m.nation == "France":
                m.location = "Paris"
        world.current_turn += 1
        W.process_evacuation_grants(world)
        assert "France|Russia" not in world.evacuation_grants
        assert not can_enter_territory(world, "France", "Russia")
        assert not can_enter_territory(world, "France", "Russia",
                                       mover_location=ENCLAVE)


# ══════════════════════════════════════════════════════════════════════════
# THE CACHE — flushed at the chokepoint, absent from the save
# ══════════════════════════════════════════════════════════════════════════

class TestTheDirectionCache:

    def test_the_flagship_works_in_the_turn_the_peace_lands(self, world):
        """The load-bearing invalidation: DURING the war, Volhynia is
        connected home through war-passable Russian soil, so a cache warmed
        pre-peace holds 'not stranded' for the very corps the peace is about
        to strand. The `set_diplomatic_state` chokepoint must flush it, or
        the flagship case breaks in the same turn as its own treaty."""
        world.fleets = {}
        world.regions[ENCLAVE].controller = "France"
        _park_everyone(world)
        world.marshals["Davout"].location = ENCLAVE
        set_diplomatic_state(world, "France", "Russia", "WAR")
        world.invalidate_active_nations_cache()

        # Warm the cache with the wartime answer.
        assert not W._corridor_is_for(world, "France", ENCLAVE), (
            "precondition: at war, the enclave is connected home through "
            "war-passable soil, so he is not stranded — if this fails the "
            "invalidation test below proves nothing")

        set_diplomatic_state(world, "France", "Russia", "PEACE")
        assert can_enter_territory(world, "France", "Russia",
                                   mover_location=ENCLAVE), (
            "a stale wartime cache must not deny the stranded corps its own "
            "corridor")

    def test_the_chokepoint_flushes_the_cache(self, world):
        _stage_trojan_shape(world)
        can_enter_territory(world, "France", "Russia", mover_location="Paris")
        assert getattr(world, "_evac_direction_cache", None), (
            "precondition: the query populated the cache")
        world.invalidate_bloc_members_cache()
        assert getattr(world, "_evac_direction_cache", None) is None

    def test_the_cache_never_serializes(self, world):
        _stage_trojan_shape(world)
        can_enter_territory(world, "France", "Russia", mover_location="Paris")
        data = world.to_dict()
        assert not any("evac_direction" in str(k) for k in data.keys())
        WorldState.from_dict(data)  # round-trips clean


# ══════════════════════════════════════════════════════════════════════════
# THE CENSUS PIN — no future seam may go bare silently
# ══════════════════════════════════════════════════════════════════════════

class TestTheCensusPin:

    def test_every_relocation_seam_names_its_mover(self):
        """Every `can_enter_territory` call in backend/ must either name its
        mover (`mover_location=`), ask the corridor-free question
        (`ignore_evacuation=`), or sit on the audited bare-call allowlist.
        A new bare call fails here and forces the WO-17 decision to be made
        consciously rather than inherited."""
        backend = Path(__file__).resolve().parents[1] / "backend"
        AUDITED_BARE = {
            # Nation-level anchor derivation — relocates nobody; the moves
            # toward its anchors run through the direction-aware AI gate.
            "war_council.py": 1,
        }
        bare = {}
        for path in sorted(backend.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"(?<!def )can_enter_territory\s*\(",
                                     text):
                call = self._call_text(text, match.start())
                if "mover_location" in call or "ignore_evacuation" in call:
                    continue
                bare[path.name] = bare.get(path.name, 0) + 1
        assert bare == AUDITED_BARE, (
            f"bare pair-level can_enter_territory calls drifted: {bare} != "
            f"{AUDITED_BARE} — a NEW relocation seam must pass "
            f"mover_location; a NEW nation-level consumer must be audited "
            f"here AND commented at the call site (WO-17)")

    @staticmethod
    def _call_text(text, start):
        i = text.index("(", start)
        depth = 0
        for j in range(i, min(len(text), i + 800)):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    return text[i:j + 1]
        return text[i:i + 800]


# ══════════════════════════════════════════════════════════════════════════
# NEVER-DO 21 — consciously NOT built
# ══════════════════════════════════════════════════════════════════════════

class TestConsciouslyNotBuilt:

    def test_no_player_redeclaration_time_floor_was_added(self, world):
        """§6 never-do 21: the player-side truce floor is WO-D8, a design
        question for a future diplomacy gate — NOT this slice. Leaving the
        armistice costs the player nothing extra today, and that stays true
        until a gate rules otherwise."""
        _stage_trojan_shape(world)
        set_diplomatic_state(world, "France", "Russia", "WAR")
        assert world.get_diplomatic_state("France", "Russia") == "WAR"
        assert "France|Russia" not in world.evacuation_grants, (
            "§3.4 pin 4 — war's resumption still kills the corridor")
