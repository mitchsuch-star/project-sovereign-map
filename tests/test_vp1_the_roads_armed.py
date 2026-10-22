"""VP-1 "The Emperor's Designs", S14b part 2 — the road armed on the existing
screens (`docs/VP1_DESIGNS_SPEC.md` §9 Part 2; the siblings `BUG_FIXES.md` §VP1).

Through the REAL endpoints on the shipped 1805 boot (which now carries the
block): the Cabinet's road page (GET /imperial_designs, the nation list's row),
the Proclaim button's own command — quoted first, then confirmed — each of the
six designs fulfilling after it, a second proclamation refused with its
reason, a forsworn design that never fulfils, the VOLTE board failing guard 6,
the one payload's slice on every surface, the manner shown = the manner
applied, and a census that no line tells the player to type a diplomatic order.
"""
import contextlib
import io
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.game_logic import imperial_designs as ID
from tests import _chip_census as C

REPO = Path(__file__).resolve().parents[1]
GODOT = REPO / "godot-client" / "project-sovereign" / "scripts"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


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
    return M.world


@pytest.fixture
def client(world):
    return TestClient(M.app)


def _post(client, command):
    return C.post(client, {"command": command})


def _page(client):
    return client.get("/imperial_designs").json()


def _road_row(client, road_id):
    return next(r for r in _page(client)["roads"] if r["id"] == road_id)


def _proclaim(client, road_id):
    """The road page's button: its own command, then the quote's option."""
    quote = _post(client, _road_row(client, road_id)["command"])
    assert quote["state"] == "awaiting_clarification", quote
    confirm = next(o["command"] for o in quote["options"] if o["label"].startswith("Proclaim"))
    return quote, _post(client, confirm)


def _tick(world, n=1):
    for _ in range(n):
        world.current_turn += 1
        ID.tick(world, world.current_turn)


def _vassalize(world, court, loyalty=60, lord="France"):
    world.vassals[court] = {"lord": lord, "loyalty": int(loyalty), "autonomy": 1,
                            "path": "treaty", "tribute_rate": 0.5}
    world.diplomatic_states[world._make_diplo_key(lord, court)] = "VASSAL"
    world.invalidate_active_nations_cache()


def _peace(world, court, demands, proposer="France"):
    world.diplomatic_states[world._make_diplo_key(proposer, court)] = "WAR"
    with _quiet():
        return world._ratify_treaty({"proposer": proposer, "target": court,
                                     "proposal_type": "peace", "type": "peace",
                                     "demands": demands, "offers": []})


# ═══════════════════════════════════════════════════════════════════════════
# The road page and the button
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRoadPage:
    def test_the_nation_list_carries_the_row_and_the_page_its_roads(self, client, world):
        row = client.get("/diplomatic_preview").json()["designs"]
        assert row == ID.wizard_row(world)
        page = _page(client)
        assert page["success"] is True and page["armed"] is True
        assert [r["id"] for r in page["roads"]] == ["rhine", "crowns", "system"]
        assert all(r["available"] and r["disabled_reason"] == "" for r in page["roads"])

    def test_each_button_command_is_the_executors_order_for_its_road(self, client, world):
        for road in _page(client)["roads"]:
            with _quiet():
                parsed = M.parser.parse(road["command"], M.get_llm_game_state(), world=world)
            assert parsed["command"]["action"] == "proclaim_design", road["command"]
            assert ID.resolve_road(world, parsed["command"]["target"]) == road["id"]

    def test_the_button_quotes_first_free_then_the_confirm_proclaims(self, client, world):
        dp, admin = int(world.diplomatic_points), int(world.admin_actions_remaining)
        quote = _post(client, _road_row(client, "rhine")["command"])
        assert "cannot be undone" in quote["message"]
        assert (int(world.diplomatic_points), int(world.admin_actions_remaining)) == (dp, admin)
        assert ID.proclaimed_road(world) == ""
        # the quote's own option (a pending quote answers the next line)
        done = _post(client, next(o["command"] for o in quote["options"]
                                  if o["label"].startswith("Proclaim")))
        assert done["success"] is True
        assert int(world.diplomatic_points) == dp - ID.PROCLAIM_DP_COST
        assert int(world.admin_actions_remaining) == admin - ID.PROCLAIM_ADMIN_COST
        page = _page(client)          # the same turn: the page reads the road proclaimed
        assert page["road"] == "rhine"
        assert [(r["proclaimed"], r["forsworn"]) for r in page["roads"]] == [
            (True, False), (False, True), (False, True)]

    def test_a_second_proclamation_is_refused_with_its_reason(self, client, world):
        _proclaim(client, "crowns")
        dp = int(world.diplomatic_points)
        reply = _post(client, _road_row(client, "system")["command"])
        assert reply["success"] is False
        assert reply["message"] == ID.proclaim_refusal(world, "system")
        assert "cannot be undone" in reply["message"] and "Schönbrunn" in reply["message"]
        assert int(world.diplomatic_points) == dp
        assert "Forsworn when the Emperor proclaimed" in _road_row(client, "system")["forsworn_line"]

    @pytest.mark.parametrize("stage", ["dp", "admin", "gate"])
    def test_every_disabled_reason_is_the_executors_refusal(self, client, world, stage):
        if stage == "dp":
            world.diplomatic_points = 1
        elif stage == "admin":
            world.admin_actions_remaining = 0
        else:
            world.diplomatic_states[world._make_diplo_key("France", "Bavaria")] = "WAR"
            world.invalidate_active_nations_cache()
        row = _road_row(client, "rhine")
        assert row["available"] is False and row["disabled_reason"]
        assert row["disabled_reason"] == ID.price_refusal(world, "rhine")
        reply = _post(client, row["command"])
        assert reply["success"] is False
        assert reply["message"].startswith(row["disabled_reason"]), (reply["message"], row)
        assert ID.proclaimed_road(world) == ""


# ═══════════════════════════════════════════════════════════════════════════
# The six designs, each fulfilled after the button's proclamation
# ═══════════════════════════════════════════════════════════════════════════

class TestEachDesignFulfilsAfterTheClick:
    def test_the_confederation(self, client, world):
        _proclaim(client, "rhine")
        for court in ("Bavaria", "Hesse", "Saxony"):
            _vassalize(world, court)
        _tick(world, 4)
        assert ID.is_fulfilled(world, "rhine.confederation")

    def test_a_german_crown(self, client, world):
        _proclaim(client, "rhine")
        _peace(world, "Austria", [{"type": "territory_cede", "regions": ["Tyrol", "Carniola"],
                                   "to_nation": "France"}])
        _tick(world)
        assert ID.is_fulfilled(world, "rhine.german_crown")

    def test_the_throne_of_naples(self, client, world):
        _proclaim(client, "crowns")
        _vassalize(world, "Naples")
        _tick(world)
        assert ID.is_fulfilled(world, "crowns.naples")

    def test_the_iron_crown(self, client, world):
        _proclaim(client, "crowns")
        _peace(world, "Austria", [{"type": "territory_cede", "regions": ["Carniola", "Tyrol"],
                                   "to_nation": "KingdomOfItaly"}])
        _tick(world)
        assert ID.is_fulfilled(world, "crowns.iron_crown")

    def test_the_blockade_and_the_peace_of_the_continent(self, client, world):
        _proclaim(client, "system")
        world.continental_system_members = ["Denmark", "Ottoman", "Russia"]
        _tick(world, 6)
        assert ID.is_fulfilled(world, "system.blockade")
        _peace(world, "Britain", [])
        _tick(world)
        assert ID.is_fulfilled(world, "system.continent_peace")

    def test_a_forsworn_design_never_fulfils(self, client, world):
        _proclaim(client, "rhine")
        world.continental_system_members = ["Denmark", "Ottoman", "Russia"]
        _vassalize(world, "Naples")
        _tick(world, 8)
        assert not ID.is_fulfilled(world, "system.blockade")
        assert not ID.is_fulfilled(world, "crowns.naples")


class TestTheVolteBoardFailsGuardSix:
    """The record §4: VOLTE's turn-30 board — Austria allied, but holding
    Berry, Limousin, Lyonnais, Provence and Savoy — is no decisive peace
    (guard 6: no French province held by the sealing court's bloc). Staged:
    VOLTE's own exit was a status quo, so no terms record exists there; the
    guard is read with one written (the map's recipe)."""

    def test_the_guard_trips_on_austrias_french_soil(self, client, world):
        _proclaim(client, "crowns")
        state = world.imperial_designs["state"]
        state["fulfilled"].update({"crowns.naples": 20, "crowns.iron_crown": 25})
        state["terms"]["Austria"] = {"manner": "moderate", "turn": 15, "broken": False,
                                     "allied_turn": 30}
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "ALLIANCE"
        held = ["Berry", "Limousin", "Lyonnais", "Provence", "Savoy"]
        for name in held:
            world.regions[name].controller = "Austria"
        world.invalidate_active_nations_cache()
        reading = ID.decisive_peace_reading(world)
        assert reading["court"] == "Austria"
        assert reading["conditions"]["homeland_whole"] is False and reading["ready"] is False
        for name in held:
            world.regions[name].controller = "France"
        world.invalidate_active_nations_cache()
        assert ID.decisive_peace_reading(world)["conditions"]["homeland_whole"] is True


# ═══════════════════════════════════════════════════════════════════════════
# One payload, every surface (the drift pin)
# ═══════════════════════════════════════════════════════════════════════════

class TestEverySurfaceCarriesTheOneSlice:
    def test_before_the_proclamation(self, client, world):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        from backend.game_logic.dispatch import _build_first_morning_doors
        from backend.ai.first_contact import answer_first_contact
        payload = ID.build_designs_payload(world)
        boe = build_diplomatic_ledger(world)["balance_of_europe"]
        assert boe["imperial_designs"] == payload
        assert _build_first_morning_doors(world, "France")["designs"] == ID.door_line(world)
        goal = answer_first_contact("goal", "how do I win", world)
        assert ID.CONDITION_C in goal
        for r in payload["roads"]:
            assert r["title"] in goal and r["title"] in ID.door_line(world)
        designs = answer_first_contact("designs", "what are our designs", world)
        for r in payload["roads"]:
            for d in r["designs"]:
                assert d["progress"] in designs

    def test_after_the_proclamation(self, client, world):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        from backend.game_logic.intent import build_france_mirror_payload
        _proclaim(client, "system")
        payload = ID.build_designs_payload(world)
        clock = ID.designs_clock(world)
        row = ID.wizard_row(world)
        chosen = next(r for r in payload["roads"] if r["proclaimed"])
        for d in chosen["designs"]:
            assert d["progress"] in clock["line"] and d["progress"] in row["line"]
        assert build_diplomatic_ledger(world)["balance_of_europe"]["imperial_designs"] == payload
        assert ID.door_line(world) == ""
        mirror = build_france_mirror_payload(world)
        assert any(chosen["proclamation"] in ln for ln in mirror["lines"])
        assert chosen["designs"][0]["progress"] in ID.court_line(world, "Britain")
        assert chosen["title"] in client.get("/diplomatic_preview").json()["designs"]["line"]


class TestTheMannerShownIsTheMannerApplied:
    @pytest.mark.parametrize("demands, manner", [
        ([{"type": "territory_cede", "regions": ["Tyrol", "Carniola"], "to_nation": "France"}],
         ID.MANNER_PARTITION),
        ([{"type": "gold_lump", "value": 500}], ""),
    ])
    def test_the_bilateral_snapshot_and_the_latch_agree(self, world, demands, manner):
        from backend.game_logic.diplomacy import build_war_context_snapshot
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "WAR"
        terms = {"type": "peace", "sweeteners": [], "demands": [dict(d) for d in demands],
                 "clauses": []}
        with _quiet():
            snap = build_war_context_snapshot(world, "France", "Austria", "peace", terms=terms)
        assert snap["manner"] == manner
        assert snap["manner_line"].startswith("The manner of this peace:")
        _peace(world, "Austria", demands)
        latched = (world.imperial_designs["state"]["terms"].get("Austria") or {}).get("manner", "")
        assert latched == manner

    def test_a_truce_and_an_unsealed_court_carry_no_manner(self, world):
        from backend.game_logic.diplomacy import build_war_context_snapshot
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "WAR"
        with _quiet():
            truce = build_war_context_snapshot(world, "France", "Austria", "armistice_winning")
        assert "manner_line" not in truce
        assert ID.manner_line(world, "Britain", []) == ""


class TestVP1X14TheOutgoingPreviewPrintsTheStatusQuo:
    def test_the_snapshot_carries_the_status_quo_rows(self, world):
        from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "WAR"
        for name in ("Vienna", "Tyrol", "Carniola"):
            world.regions[name].controller = "France"
        world.invalidate_active_nations_cache()
        dialogue = {"options": [{"action": "execute_proposal", "terms": {
            "type": "peace", "proposal_type": "peace", "sweeteners": [],
            "demands": [{"type": "gold_lump", "value": 300}], "clauses": []}}]}
        with _quiet():
            _enrich_proposal_summary(dialogue, "Austria", "peace", world)
        rows = dialogue["war_context_snapshot"]["annotated_terms"]
        assert any(r.get("type") == "status_quo" for r in rows), rows
        assert rows[0].get("type") != "status_quo"


class TestVP1X18TheRecoveryNeverOffersACabinetAct:
    def test_the_vocabulary(self):
        from backend.ai.prompt_builder import recovery_action_vocabulary
        from backend.ai.validation import CABINET_ACTIONS
        typed = set(recovery_action_vocabulary("typed"))
        assert not ({a.replace("_", " ") for a in CABINET_ACTIONS} & typed)


class TestVP1X19TheDoorClaimsTalks:
    def test_hold_talks_is_claimed(self):
        gd = (GODOT / "main.gd").read_text(encoding="utf-8")
        assert '\t"hold talks with",' in gd


# ═══════════════════════════════════════════════════════════════════════════
# The events — the chronicle, the front page, Le Moniteur, the prologue
# ═══════════════════════════════════════════════════════════════════════════

class TestTheEvents:
    def test_the_proclamation_leads_the_next_morning(self, client, world):
        from backend.campaign_log import format_event_oneliner
        from backend.game_logic import dispatch as D
        _proclaim(client, "rhine")
        events = [e for e in world.event_log if e.get("type") == "imperial_design"]
        assert [e["phase"] for e in events] == ["proclaimed"]
        assert "THE ACT OF CONFEDERATION" in format_event_oneliner(events[0])
        world.current_turn += 1
        cands = []
        D._designs_candidate(world, events[0], lambda cls, key, **f: cands.append((cls, f)))
        assert cands and cands[0][0] == "design_proclaimed"
        assert "THE ACT OF CONFEDERATION" in cands[0][1]["line"]

    def test_a_fulfilment_and_the_moniteur(self, client, world):
        from backend.game_logic.gazette import _special_candidates
        _proclaim(client, "crowns")
        _vassalize(world, "Naples")
        _tick(world)
        rows = [e for e in world.event_log if e.get("type") == "imperial_design"
                and e.get("phase") == "fulfilled"]
        assert rows and rows[0]["design"] == "crowns.naples"
        reasons = [c[1] for c in _special_candidates(world, rows)]
        assert "a design of the Empire fulfilled" in reasons

    def test_the_prologue_fires_once_on_the_first_peace_with_austria(self, client, world):
        from backend.models.world_state import WorldState
        _peace(world, "Austria", [{"type": "territory_cede", "regions": ["Tyrol", "Carniola"],
                                   "to_nation": "France"}])
        state = world.imperial_designs["state"]
        assert state["prologue_turn"] == int(world.current_turn)
        prologue = [e for e in world.event_log if e.get("phase") == "prologue"]
        assert len(prologue) == 1 and prologue[0]["manner"] == "partition"
        assert "Protector of the Rhine" in ID.prologue_counsel(world, "Austria", "partition")
        again = WorldState.from_dict(world.to_dict())
        _peace(again, "Austria", [{"type": "gold_lump", "value": 100}])
        assert len([e for e in again.event_log if e.get("phase") == "prologue"]) == 1

    def test_no_prologue_once_a_road_is_proclaimed(self, client, world):
        _proclaim(client, "system")
        _peace(world, "Austria", [{"type": "gold_lump", "value": 100}])
        assert world.imperial_designs["state"]["prologue_turn"] == -1

    def test_the_quiet_morning_names_the_design_that_moved(self, client, world):
        """The record §6.3's `realm_designs` front-page class: the morning
        remembers the proclaimed road's counts and, when the courts sent
        nothing, leads with the design whose count moved."""
        from backend.game_logic import dispatch as D
        with _quiet():
            D.build_morning_dispatch(world)
        assert "designs" not in (world.headline_lead_memory or {})  # unproclaimed: nothing written
        _proclaim(client, "rhine")
        with _quiet():
            D.build_morning_dispatch(world)
        assert world.headline_lead_memory["designs"]["rhine.confederation"]["held"] == 0
        assert ID.realm_line(world, world.headline_lead_memory["designs"]) == ""  # nothing moved
        _vassalize(world, "Bavaria")
        line = ID.realm_line(world, world.headline_lead_memory["designs"])
        assert line.startswith("the Confederation of the Rhine stands at 1 of 3 courts") and "up from 0" in line
        rows = [c for c in D._realm_candidates(world, "France") if c["class"] == "realm_designs"]
        assert rows and rows[0]["text"] == "Sire — " + line + "."
        assert "realm_designs" in D.FRONT_PAGE_CLASSES
        assert list(D.HEADLINE_WEIGHTS.values()).count(D.HEADLINE_WEIGHTS["realm_designs"]) == 1


# ═══════════════════════════════════════════════════════════════════════════
# The census: no line tells the player to TYPE a diplomatic order
# ═══════════════════════════════════════════════════════════════════════════

_TYPED = re.compile(
    r"'(?:proclaim|summon|convene|propose|declare|offer|sue|ally|vassalize|subjugate|"
    r"bind|buy off|sponsor|guarantee|make amends|break)\b[^']*'",
    re.IGNORECASE)
# (A quoted diplomatic order is what the user's rule forbids, October 20,
# 2026. "Type 'what can I do'" is a question to the desk, not a diplomatic
# act, and stays — the first contact's three doors.)


class TestNoLineTeachesATypedDiplomaticOrder:
    def _lines(self, client, world):
        from backend.ai.first_contact import answer_first_contact
        from backend.ai import counsel
        payload = ID.build_designs_payload(world)
        out = [ID.door_line(world), ID.goal_clause(world), payload["headline"]]
        for r in payload["roads"]:
            out += [r["gate_reason"], r["teeth_line"], r["disabled_reason"], r["forsworn_line"]]
            for d in r["designs"]:
                out += [d["hint"], d["control"], d["reward_line"], d["progress"], d["hold_line"]]
        for kind in ("goal", "designs", "congress", "greeting"):
            out.append(answer_first_contact(kind, "x", world) or "")
            out.append(answer_first_contact(kind, "x", None) or "")
        for court in ("Austria", "Prussia", "Bavaria", "Naples", "Britain"):
            out.append(ID.court_line(world, court))
        out.append(ID.prologue_counsel(world, "Austria", "partition"))
        out += counsel.what_can_i_do(world, "France", limit=6)
        return out

    def test_before_and_after_the_proclamation(self, client, world):
        found = [ln for ln in self._lines(client, world) if ln and _TYPED.search(ln)]
        quote, _done = _proclaim(client, "rhine")
        found += [quote["message"]] if _TYPED.search(quote["message"]) else []
        found += [ln for ln in self._lines(client, world) if ln and _TYPED.search(ln)]
        assert found == [], found

    def test_the_controls_name_the_cabinet(self, world):
        for r in ID.build_designs_payload(world)["roads"]:
            for d in r["designs"]:
                assert d["control"].startswith("F1 →"), d["control"]


# ═══════════════════════════════════════════════════════════════════════════
# The client — the road page, the clock, the door (source pins; the Godot
# parse harness and the IQ-10 frames are the runtime proof)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheClient:
    def test_the_wizard_road_page(self):
        gd = (GODOT / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert 'API_URL + "/imperial_designs"' in gd
        assert "_add_designs_row(data.get(\"designs\"))" in gd
        assert "_current_step == 2 or _current_step == 3 or _current_step == 4" in gd
        body = gd[gd.index("func _on_proclaim_pressed"):]
        body = body[:body.index("\nfunc ")]
        assert "_close_wizard()" in body and "command_selected.emit(command)" in body
        assert body.index("_close_wizard()") < body.index("command_selected.emit(command)")
        assert '_on_proclaim_pressed.bind(str(road.get("command", "")))' in gd

    def test_both_renderers_print_the_clock_and_the_door(self):
        main = (GODOT / "main.gd").read_text(encoding="utf-8")
        view = (GODOT / "dispatch_view.gd").read_text(encoding="utf-8")
        assert '_add_designs_clock_line(data.get("designs_clock", null))' in main
        assert 'data.get("designs_clock", null)' in view
        for gd in (main, view):
            assert 'today.get("designs", "")' in gd

    def test_the_popups_print_the_manner_and_the_revanche(self):
        confirm = (GODOT / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        incoming = (GODOT / "incoming_proposal_popup.gd").read_text(encoding="utf-8")
        for gd in (confirm, incoming):
            assert 'snapshot.get("manner_line", "")' in gd
            assert 'snapshot.get("revanche_line", "")' in gd
        assert confirm.count("_settlement_designs_lines(data)") == 2
