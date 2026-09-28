"""SR-5r RF-4b — "The laws everywhere else" (`docs/REFORMS_SPEC.md` §8, §8a;
§12 RF-4b; §11 T7/T8).

* THE FORECAST (§8) — `reforms.lapse_forecast`, ONE source for the LAWS tab,
  the end-turn banner and the morning dispatch: the lapse rule itself
  (`lapse_order`) run against the ledger's own projection of this turn's end.
  It names the law that lapses first and the gold that saves the slate, and
  offers the one lever (§8b "What to lose") — the fewest repeals of the other
  laws that keep it (`reforms.repeal_plan`) — as a chip, withheld with its
  reason when the admin actions cannot cover the plan (never a trap).
* THE BEATS (§8 "The events") — a rival's enactment, restoration and lapse,
  and the player's own lapse, on the next morning dispatch; the Staff's first
  refill named there too ("the dispatch names why"), derived.
* THE NATION CARDS — one Laws line per court (diplomacy has no fog).
* HELP AND THE DESK — the help names the verbs; a question NAMING a law is
  answered with it (world-aware — "what does the Staff cost?" carries no
  word the parser's law router knows); what is in force is said first; the
  router's "laws" topic points at the LAWS tab.
* RF-2's owed rows (T8) — the Manpower tab's regen/price terms, the vassal
  forecast's law term, the decree's own ports on the Continental System line.
"""
import contextlib
import io
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.game_logic.ledger as L
import backend.main as M
from backend.game_logic import dispatch as D
from backend.game_logic import reforms as R
from tests import _chip_census as C

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "godot-client" / "project-sovereign" / "scripts"
STAFF_ID = "grand_quartier_general"
SLATE = (STAFF_ID, "anticipated_class", "code_abroad")    # 300 + 150 + 100


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
    return M.world


@pytest.fixture
def client(world):
    return TestClient(M.app)


def post(client, command):
    with _quiet():
        return client.post("/command", json={"command": command}).json()


def enact(world, nation, *law_ids):
    for law_id in law_ids:
        R.enact_law(world, nation, R.find_law(world, nation, law_id))


BASE = -650   # the projected Net before the laws' upkeep


@pytest.fixture
def insolvent(world, monkeypatch):
    """France holds the Staff and two cheaper laws, and the ledger's
    projection of this turn's end is `BASE - the laws' upkeep` — so the
    forecast answers to the laws in force exactly as the real one does."""
    enact(world, "France", *SLATE)
    monkeypatch.setattr(L, "_build_economy",
                        lambda w, n, income_data=None: {"net": BASE - R.law_upkeep_bill(w, n)})
    world.admin_actions_remaining = 2
    return world


def chest(world, gold):
    world.nation_gold["France"] = gold


def _gd(name):
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _func_body(src, name):
    return src.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]


# ═══════════════════════════ THE FORECAST ═════════════════════════════════════

class TestTheForecast:

    def test_nothing_is_forecast_while_the_slate_is_paid(self, insolvent):
        chest(insolvent, 5000)
        assert R.lapse_forecast(insolvent, "France") is None

    def test_nothing_is_forecast_with_no_law_in_force(self, world, monkeypatch):
        monkeypatch.setattr(L, "_build_economy", lambda w, n, income_data=None: {"net": -5000})
        chest(world, 0)
        assert R.lapse_forecast(world, "France") is None

    def test_the_forecast_is_the_lapse_rule_itself(self, insolvent):
        """Shown = applied: run the REAL lapse loop on the chest the turn's
        end leaves, and it takes exactly the laws the forecast named."""
        chest(insolvent, 800)                     # 800 + (-1200) = -400
        forecast = R.lapse_forecast(insolvent, "France")
        assert forecast["shortfall"] == 400
        insolvent.nation_gold["France"] = 800 + forecast["net"]
        with _quiet():
            R.process_law_lapses(insolvent)
        lapsed = [r["id"] for r in R.deck(insolvent, "France")
                  if r.get("lapsed_turn") is not None]
        assert sorted(lapsed) == sorted(forecast["doomed"])
        assert forecast["doomed"] == [STAFF_ID, "anticipated_class"]

    def test_the_line_names_the_law_and_the_gold(self, insolvent):
        chest(insolvent, 800)
        line = R.lapse_forecast(insolvent, "France")["line"]
        assert line.startswith("The Grand Quartier Général lapses when this turn "
                               "ends unless 400 gold is found — the chest (800) "
                               "cannot carry the turn's Net (-1,200).")
        assert "The Anticipated Class would go after it." in line

    def test_one_repeal_keeps_it(self, insolvent):
        chest(insolvent, 1100)                    # shortfall 100: the Code Abroad
        forecast = R.lapse_forecast(insolvent, "France")
        rescue = forecast["repeal_instead"]
        assert rescue["command"] == "repeal the Code Abroad" and rescue["enabled"] is True
        assert forecast["line"].endswith("Repealing the Code Abroad instead keeps it.")
        R.repeal_law(insolvent, "France", R.find_law(insolvent, "France", "code_abroad"))
        assert R.lapse_forecast(insolvent, "France") is None, "the lever really keeps it"

    def test_the_chip_is_the_typed_order(self, insolvent, client):
        """The chip sends its command through /command (the CN-4 idiom):
        the law is repealed for one admin action and the forecast clears."""
        chest(insolvent, 1100)
        rescue = R.lapse_forecast(insolvent, "France")["repeal_instead"]
        admin = insolvent.admin_actions_remaining
        r = post(client, rescue["command"])
        assert r.get("success") is True, r.get("message")
        assert not R.is_in_force(R.find_law(insolvent, "France", "code_abroad"))
        assert insolvent.admin_actions_remaining == admin - 1
        assert R.lapse_forecast(insolvent, "France") is None

    def test_the_cheapest_single_repeal_is_the_one_offered(self, insolvent):
        chest(insolvent, 1100)
        plan = R.repeal_plan(insolvent, "France",
                             R.find_law(insolvent, "France", STAFF_ID), 100)
        assert [r["id"] for r in plan] == ["code_abroad"]   # not the Anticipated Class

    def test_two_repeals_keep_it_one_admin_action_each(self, insolvent):
        chest(insolvent, 1000)                    # shortfall 200: 150 + 100
        forecast = R.lapse_forecast(insolvent, "France")
        rescue = forecast["repeal_instead"]
        assert rescue["plan"] == ["anticipated_class", "code_abroad"]
        assert rescue["enabled"] is True
        assert "the first of 2 repeals" in rescue["note"]
        assert forecast["line"].endswith(
            "Repealing the Anticipated Class and the Code Abroad instead would "
            "keep it — one admin action each.")
        for law_id in rescue["plan"]:
            R.repeal_law(insolvent, "France", R.find_law(insolvent, "France", law_id))
        assert R.lapse_forecast(insolvent, "France") is None

    def test_the_lever_is_withheld_when_the_actions_fall_short(self, insolvent):
        """Never a trap: one repeal of a two-repeal plan loses that law AND
        the Staff."""
        chest(insolvent, 1000)
        insolvent.admin_actions_remaining = 1
        forecast = R.lapse_forecast(insolvent, "France")
        rescue = forecast["repeal_instead"]
        assert rescue["enabled"] is False
        assert rescue["reason"] == ("It takes 2 repeals to keep the Grand Quartier "
                                    "Général, and only 1 admin action remains this turn.")
        assert forecast["line"].endswith("and only 1 admin action remains this turn.")

    def test_it_says_so_when_no_admin_action_remains(self, insolvent):
        chest(insolvent, 1100)
        insolvent.admin_actions_remaining = 0
        forecast = R.lapse_forecast(insolvent, "France")
        assert forecast["repeal_instead"]["enabled"] is False
        assert forecast["repeal_instead"]["reason"] == R.repeal_refusal(
            insolvent, "France", "code_abroad")
        assert forecast["line"].endswith("but no admin action remains this turn.")

    def test_it_says_so_when_no_repeal_would_keep_it(self, insolvent):
        chest(insolvent, 800)                     # shortfall 400 > 150 + 100
        forecast = R.lapse_forecast(insolvent, "France")
        assert forecast["repeal_instead"] is None
        assert forecast["line"].endswith("No repeal of the other laws would keep it.")

    def test_the_laws_tab_carries_it(self, insolvent):
        chest(insolvent, 1100)
        assert R.laws_payload(insolvent, "France")["forecast"] == R.lapse_forecast(insolvent, "France")

    def test_the_banner_and_the_dispatch_read_the_same_forecast(self, insolvent, client,
                                                                 monkeypatch):
        """The real end turn pays the real income, so the projection read
        at the new turn's start must stay under water for a forecast to
        exist there: a deep projected Net."""
        monkeypatch.setattr(L, "_build_economy",
                            lambda w, n, income_data=None: {"net": -40000})
        chest(insolvent, 1100)
        r = post(client, "end turn")
        forecast = R.lapse_forecast(insolvent, "France")
        assert forecast is not None
        assert f"THE LAWS: {forecast['line']}" in r["message"]
        event = next(e for e in r["events"] if e.get("type") == "turn_end")
        assert event["law_forecast"] == forecast
        assert r["morning_dispatch"]["situation"]["law_forecast"] == forecast


# ═══════════════════════════ THE BEATS ════════════════════════════════════════

def _queued(world, etype):
    return [e for e in world.pending_dispatch_events if e.get("type") == etype]


class TestTheBeats:

    def test_a_rivals_enactment_is_a_beat(self, world):
        world.pending_dispatch_events = []
        enact(world, "Austria", "landwehr")
        (event,) = _queued(world, "law_enacted_abroad")
        text = D._format_dispatch_event_text(event["type"], event["template_vars"])
        assert text == ("THE LAWS: Austria enacts the Landwehr — infantry manpower "
                        "returns 25% faster.")
        assert event["fog_rule"] == "always"

    def test_a_restoration_says_so(self, world):
        world.pending_dispatch_events = []
        row = R.find_law(world, "Austria", "landwehr")
        row["lapsed_turn"] = int(world.current_turn) - 1
        R.enact_law(world, "Austria", row)
        (event,) = _queued(world, "law_enacted_abroad")
        assert event["template_vars"]["verb"] == "restores"

    def test_a_rivals_lapse_is_a_beat(self, world):
        enact(world, "Austria", "landwehr")
        world.pending_dispatch_events = []
        world.nation_gold["Austria"] = -100
        with _quiet():
            R.process_law_lapses(world)
        (event,) = _queued(world, "law_lapsed_abroad")
        text = D._format_dispatch_event_text(event["type"], event["template_vars"])
        assert text == "THE LAWS: Austria cannot pay for the Landwehr — the law lapses."

    def test_the_players_lapse_is_a_wound(self, world):
        enact(world, "France", STAFF_ID)
        world.pending_dispatch_events = []
        world.nation_gold["France"] = -100
        with _quiet():
            R.process_law_lapses(world)
        (event,) = _queued(world, "law_lapsed_home")
        assert D._DIPLOMATIC_EVENT_PRIORITY["law_lapsed_home"] == "HIGH"
        text = D._format_dispatch_event_text(event["type"], event["template_vars"])
        assert text.startswith("THE LAWS: The Grand Quartier Général has lapsed — the "
                               "treasury could not pay its 300 gold a turn.")

    def test_the_players_enactment_is_the_verbs_own_answer(self, world):
        world.pending_dispatch_events = []
        world.nation_gold["France"] = 20000
        enact(world, "France", STAFF_ID)
        assert not [e for e in world.pending_dispatch_events
                    if str(e.get("type", "")).startswith("law_")]

    def test_every_law_beat_has_a_template_and_a_priority(self):
        for etype in ("law_enacted_abroad", "law_lapsed_abroad", "law_lapsed_home"):
            assert etype in D._DIPLOMATIC_EVENT_TEMPLATES
            assert etype in D._DIPLOMATIC_EVENT_PRIORITY

    def test_the_beat_reaches_the_morning_dispatch(self, world, client):
        world.nation_gold["Austria"] = 60000
        enact(world, "Austria", "landwehr")
        r = post(client, "end turn")
        texts = [row.get("text", "") for row in
                 (r["morning_dispatch"].get("diplomatic_events") or [])]
        assert any(t.startswith("THE LAWS: Austria enacts the Landwehr") for t in texts), texts


# ═══════════════════════════ THE STAFF ARRIVES ════════════════════════════════

class TestTheStaffArrives:

    def test_the_first_refill_names_it_once(self, world):
        world.nation_gold["France"] = 20000
        enact(world, "France", STAFF_ID)
        assert R.staff_arrival(world, "France") is None       # not the enactment turn
        world.current_turn += 1
        assert R.staff_arrival(world, "France") == "The Grand Quartier Général"
        world.current_turn += 1
        assert R.staff_arrival(world, "France") is None

    def test_a_staff_struck_down_the_same_turn_announces_nothing(self, world):
        world.nation_gold["France"] = 20000
        enact(world, "France", STAFF_ID)
        R.repeal_law(world, "France", R.find_law(world, "France", STAFF_ID))
        world.current_turn += 1
        assert R.staff_arrival(world, "France") is None

    def test_the_dispatch_names_why(self, world, client):
        world.nation_gold["France"] = 20000
        enact(world, "France", STAFF_ID)
        r = post(client, "end turn")
        assert r["morning_dispatch"]["situation"]["staff_arrived"] == "The Grand Quartier Général"


# ═══════════════════════════ THE NATION CARDS ═════════════════════════════════

class TestTheNationCards:

    def test_a_court_with_laws_shows_them(self, world):
        enact(world, "Austria", "landwehr", "generalissimus")
        assert R.laws_line(world, "Austria") == (
            "the Landwehr and the Generalissimus (250 gold a turn)")

    def test_a_court_without_laws_omits_the_row(self, world):
        assert R.laws_line(world, "Austria") is None

    def test_the_ledger_carries_the_line(self, world):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        enact(world, "Austria", "landwehr")
        with _quiet():
            ledger = build_diplomatic_ledger(world)
        austria = next(n for n in ledger["nations"] if n.get("nation") == "Austria"
                       or n.get("name") == "Austria")
        assert austria["laws"] == R.laws_line(world, "Austria")


# ═══════════════════════════ HELP AND THE DESK ════════════════════════════════

class TestTheDesk:

    def test_a_question_naming_the_staff_is_answered(self, world, client):
        message = post(client, "what does the Staff cost?")["message"]
        assert message.startswith("The laws of state, Sire. No law is in force. "
                                  "The Grand Quartier Général: 9,000 gold"), message
        assert "cannot answer" not in message

    def test_the_law_asked_about_leads(self, world, client):
        message = post(client, "what does the Code Abroad do?")["message"]
        head = message.split("No law is in force. ", 1)[1]
        assert head.startswith("The Code Abroad:"), head[:80]

    def test_what_is_in_force_is_said_first(self, world, client):
        world.nation_gold["France"] = 20000
        enact(world, "France", STAFF_ID)
        message = post(client, "what laws are in force?")["message"]
        assert message.startswith("The laws of state, Sire. In force: the Grand "
                                  "Quartier Général."), message

    def test_the_answer_points_at_the_laws_tab(self, world, client):
        message = post(client, "what laws can I enact?")["message"]
        assert "the Laws tab (press T, then 8)" in message

    @pytest.mark.parametrize("text, law_id", [
        ("what does the staff cost", STAFF_ID),
        ("tell me about the Berlin Decree", "berlin_decree"),
        ("is the grand quartier general worth it", STAFF_ID),
        ("what is the weather in Paris", None),
        ("what about the reserve", None),
    ])
    def test_a_law_is_named_as_a_whole(self, world, text, law_id):
        row = R.law_named_in(world, "France", text)
        assert (row["id"] if row else None) == law_id

    def test_the_router_points_at_the_laws_tab(self):
        from backend.ai.counsel import surface_pointer
        from backend.commands.meta_executor import MetaExecutor
        assert MetaExecutor.question_topic("which reform should I pass?") == "laws"
        assert surface_pointer("laws") == "the Strategic Ledger's Laws tab (press T, then 8)"

    def test_the_help_names_the_verbs(self, world, client):
        message = post(client, "help")["message"]
        assert "enact      - Enact a law of state" in message
        assert "repeal     - \"repeal the Code Abroad\"" in message


# ═══════════════════════════ RF-2's OWED ROWS (T8) ════════════════════════════

class TestTheOwedRows:

    def test_the_vassal_row_names_the_law_that_binds_it(self, world):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        enact(world, "France", "code_abroad")
        with _quiet():
            ledger = build_diplomatic_ledger(world)
        rows = (ledger.get("vassals") or {}).get("rows") or ledger.get("vassals") or []
        rows = rows if isinstance(rows, list) else []
        assert rows, "the 1805 boot has French clients"
        for row in rows:
            assert row["law_terms"] == [["the Code Abroad", 1]], row

    def test_the_decree_names_its_own_ports(self, world):
        from backend.game_logic import naval as NV
        from backend.game_logic.vassal import AUTONOMY_AUTONOMOUS
        enact(world, "France", "berlin_decree")
        client = next(v for v, rec in world.vassals.items() if rec.get("lord") == "France"
                      and NV.get_fleets(world).get(v, {}).get("ports", 0) > 0)
        # An AUTONOMOUS client at PEACE with Britain: only the decree counts
        # its ports (a client at war with Britain is counted already).
        world.vassals[client]["autonomy"] = AUTONOMY_AUTONOMOUS
        target = "Britain"
        world.diplomatic_states[world._make_diplo_key(client, target)] = "PEACE"
        assert NV.closure_against(world, target) > 0
        assert client in NV.decree_clients(world, target)
        with _quiet():
            report = NV.build_admiralty_report(world)
        line = report["continental_system"]["decree_line"]
        from backend.display_names import display_nation
        assert line.startswith("The Berlin Decree counts 1 autonomous client: ")
        assert display_nation(client) in line

    def test_no_decree_no_line(self, world):
        from backend.game_logic import naval as NV
        with _quiet():
            report = NV.build_admiralty_report(world)
        assert report["continental_system"]["decree_line"] == ""


# ═══════════════════════════ THE CLIENT ═══════════════════════════════════════

class TestTheClient:

    def test_one_forecast_renderer_for_the_banner_and_the_dispatch(self):
        src = _gd("main.gd")
        body = _func_body(src, "_render_law_forecast")
        assert '"THE LAWS: "' in body and '"repeal_instead"' in body
        assert 'bool(rescue.get("enabled", false))' in body
        assert '_render_law_forecast(event.get("law_forecast", null), "")' in _func_body(
            src, "_display_turn_change")
        dispatch = _func_body(src, "_display_morning_dispatch")
        assert '_render_law_forecast(situation.get("law_forecast", null), "  ")' in dispatch
        assert 'situation.get("staff_arrived", null)' in dispatch

    def test_a_terminal_chip_takes_the_chip_road(self):
        body = _func_body(_gd("main.gd"), "_on_output_meta_clicked")
        assert re.search(r'if meta_str\.begins_with\("do:"\):[\s\S]*?_on_naval_command\(chip_command\)', body)

    def test_the_reread_screen_says_the_same(self):
        src = _gd("dispatch_view.gd")
        assert 'situation.get("staff_arrived", null)' in src
        assert 'situation.get("law_forecast", null)' in src

    def test_the_laws_tab_shows_the_forecast_and_its_lever(self):
        body = _func_body(_gd("strategic_ledger.gd"), "_render_laws_tab")
        assert 'laws.get("forecast", null)' in body and "_chip_row(rescue)" in body

    def test_the_manpower_rows_name_their_laws(self):
        body = _func_body(_gd("strategic_ledger.gd"), "_render_manpower")
        assert 'pool.get("regen_terms", [])' in body and 'pool.get("price_terms", [])' in body

    def test_the_decree_line_is_rendered(self):
        assert 'cs.get("decree_line", "")' in _gd("strategic_ledger.gd")

    def test_the_cards_name_the_laws(self):
        src = _gd("diplomatic_ledger.gd")
        assert 'n.get("laws")' in src and '"  Laws: [color=#"' in src
        assert 'v.get("law_terms", [])' in src and '" binds them (+"' in src
