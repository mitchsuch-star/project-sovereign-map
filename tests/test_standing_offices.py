"""AU-3b "crowns and offices" (docs/AUTHORITY_CURRENCY_SPEC.md §5.3, §4.1
reading 15, the landing record §6.6) and AU-17 at its head.

- AU-17: ONE vocabulary for the figure — the Morning Dispatch and the
  Strategic Ledger say the tracker's five tiers, the chip's own word.
- Endow them: a fourth answer on the Fontainebleau card — titles in place of
  rentes, every petitioner's clock set eight turns ahead (the promise's
  mechanism at three), 6 authority at the purchases' floor and the recency
  rise; last on the card; closed with its reason under 60.
- The Titles of the Confederation: a second purse on the Princes' Dotations
  Act — 12 authority beside the 6,000 gold, decreed once whichever pays.
- The Proclamation: a fourth Edict letter priced in authority ALONE, at war
  on the eve of battle (LATCHED: an enemy army seen within a march of the
  Emperor — re-premised by the user's "Re-premise it first", §6.6.5; first
  written at war with the Emperor afield); authored `since: "AU-3b"` and HELD
  OUT until the user's word arms it (RE's rule, AU-2c's precedent); a court
  never proclaims before AU-4.
The seams: `standing.offices_armed` (arm AUO) and `standing.proclamation_armed`
(arm AUR, down by default).
"""
import contextlib
import io
import json
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import affairs as AF
from backend.game_logic import dispatch, dotation, ledger, reforms
from backend.game_logic import imperial_designs as ID
from backend.game_logic import jealousy as J
from backend.game_logic import moments as MO
from backend.game_logic import standing as ST
from backend.models.world_state import WorldState
from tests import _chip_census as C

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"
ACTS_FIXTURE = REPO / "tests" / "fixtures" / "vp1_imperial_designs_block.json"
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
P2 = "the_proclamation"
DOTATIONS = "princes_dotations"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def boot():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def fresh(boot):
    with _quiet():
        return WorldState.from_dict(boot.to_dict())


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def board(monkeypatch):
    """The live 1805 board with the affairs fixture's deck, every template
    passed (the AU-3a buys pins' own staging)."""
    C.board_env(monkeypatch)
    w = M.world
    w.moments = MO.from_block(json.loads(FIXTURE.read_text(encoding="utf-8")))
    for e in MO.deck(w):
        w.moments["state"][str(e["id"])] = {"status": "passed", "turn": 1, "reason": "premise"}
    w.__dict__.pop("_affairs_memo", None)
    return w


# ═══════════════════════════════════════════════════════════════════════════
# AU-17 — one vocabulary for the figure
# ═══════════════════════════════════════════════════════════════════════════

class TestOneWordForTheFigure:
    @pytest.mark.parametrize("figure", [100, 90, 89, 85, 80, 70, 69, 50, 49, 30, 29, 10])
    def test_the_morning_and_the_ledger_say_the_chips_word(self, fresh, figure):
        fresh.authority_tracker.authority = figure
        word = str(fresh.authority_tracker.get_authority_label())
        assert ST.payload(fresh, "France")["label"] == word                      # the chip
        with _quiet():
            situation = dispatch._build_situation(fresh, "France")
            book = ledger.build_strategic_ledger(fresh)
        assert situation["authority_label"].split(" at court;")[0].split(";")[0].split(" — ")[0] == word
        assert book["authority_label"] == word

    def test_the_private_table_is_gone(self):
        for module in (dispatch, ledger):
            src = Path(module.__file__).read_text(encoding="utf-8")
            assert 'authority_label = "Strong"' not in src and 'authority_label = "Weak"' not in src
            assert "get_authority_label()" in src

    def test_the_client_prints_the_word_it_is_sent(self):
        for name in ("main.gd", "dispatch_view.gd", "strategic_ledger.gd"):
            src = (SCRIPTS / name).read_text(encoding="utf-8")
            assert 'get("authority_label", "Normal")' not in src, name
            assert '(" (" + authority_label + ")" if authority_label != "" else "")' in src, name


# ═══════════════════════════════════════════════════════════════════════════
# Endow them — the Fontainebleau card
# ═══════════════════════════════════════════════════════════════════════════

def _petitioners(world, names=("Ney", "Murat", "Lannes"), authority=100):
    floor = max(dotation.GRACE_TURNS + 3, J.FONTAINEBLEAU_MIN_TURN)
    world.current_turn = max(int(world.current_turn), floor)
    out = []
    for name in names:
        m = world.marshals[name]
        m.expectation_steps = 3
        m.expectation_grace_turn = int(world.current_turn) - dotation.GRACE_TURNS
        assert dotation.is_eroding(m, world)
        out.append(m)
    world.authority_tracker.authority = int(authority)
    J.check_fontainebleau(world, [])
    assert (world.pending_marshal_petition or {}).get("kind") == "fontainebleau"
    return out


def _option(world, oid):
    return next(o for o in world.pending_marshal_petition["options"] if o["id"] == oid)


class TestEndowThem:
    def test_the_fourth_answer_is_last_priced_and_says_its_window(self, fresh):
        _petitioners(fresh)
        ids = [o["id"] for o in fresh.pending_marshal_petition["options"]]
        assert ids == ["concede", "refuse", "promise", "endow"]
        endow = _option(fresh, "endow")
        assert endow["enabled"] is True and endow["cost_note"] == "6 authority"
        assert endow["label"] == J.FONTAINEBLEAU_ENDOW_LABEL
        assert f"their patience extends {J.FONTAINEBLEAU_ENDOW_WINDOW} turns" in endow["detail"]
        assert "Authority 100 → 94" in endow["detail"]
        assert J.FONTAINEBLEAU_ENDOW_WINDOW == dotation.GRACE_TURNS + 8 == 12

    def test_endow_sets_every_petitioners_clock_eight_ahead(self, fresh):
        marshals = _petitioners(fresh)
        trust = {m.name: m.trust.value for m in marshals}
        result = J.handle_petition_response(fresh, "endow")
        assert result["success"], result
        assert int(fresh.authority_tracker.authority) == 94
        for m in marshals:
            assert m.expectation_grace_turn == int(fresh.current_turn) + J.FONTAINEBLEAU_ENDOW_GRACE
            assert not dotation.is_eroding(m, fresh) and m.pension == 0 and m.trust.value == trust[m.name]
        last = fresh.authority_tracker.moves[-1]
        assert (last["key"], last["delta"], last["cause"]) == (
            "endowed", -6, "titles in place of rentes for the marshals")
        assert "their patience extends 12 turns" in result["message"]
        assert fresh.pending_marshal_petition is None

    def test_closed_under_the_floor_and_the_card_stands(self, fresh):
        _petitioners(fresh, authority=62)
        endow = _option(fresh, "endow")
        assert endow["enabled"] is False and "under 60" in endow["unavailable_reason"]
        assert endow["detail"] == endow["unavailable_reason"]
        result = J.handle_petition_response(fresh, "endow")
        assert result["success"] is False and "under 60" in result["message"]
        assert int(fresh.authority_tracker.authority) == 62
        assert (fresh.pending_marshal_petition or {}).get("kind") == "fontainebleau"

    def test_the_recency_rise_reaches_the_card(self, fresh):
        _petitioners(fresh)
        fresh.authority_tracker.held["pushes"] = [int(fresh.current_turn)]
        refreshed = J.refresh_petition_affordability(dict(fresh.pending_marshal_petition), fresh)
        assert next(o for o in refreshed["options"] if o["id"] == "endow")["cost_note"] == "7 authority"

    def test_held_down_the_card_reads_three_answers(self, fresh, monkeypatch):
        monkeypatch.setattr(ST, "offices_armed", lambda *a, **k: False)
        _petitioners(fresh)
        assert [o["id"] for o in fresh.pending_marshal_petition["options"]] == ["concede", "refuse", "promise"]
        assert J.handle_petition_response(fresh, "endow")["success"] is False


# ═══════════════════════════════════════════════════════════════════════════
# The Titles of the Confederation — the Princes' Dotations' second purse
# ═══════════════════════════════════════════════════════════════════════════

def _rhine(world, authority=100):
    world.authority_tracker.authority = int(authority)
    out = ID.proclaim(world, "rhine")
    assert out.get("success"), out
    return next(r for r in ID.act_rows(world) if r["id"] == DOTATIONS)


class TestTheTitles:
    def test_the_deck_carries_the_titles_in_lockstep(self):
        scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
        acts = {a["id"]: a for a in scenario["imperial_designs"]["acts"]}
        assert acts[DOTATIONS]["titles"] == {"name": "The Titles of the Confederation", "authority": 12}
        fixture = json.loads(ACTS_FIXTURE.read_text(encoding="utf-8"))
        assert {a["id"]: a for a in fixture["acts"]}[DOTATIONS]["titles"] == acts[DOTATIONS]["titles"]

    def test_the_row_carries_the_second_purse_open_where_the_gold_is_short(self, fresh):
        row = _rhine(fresh)
        assert row["available"] is False and "6,000 gold" in row["disabled_reason"]    # the boot's chest
        titles = row["titles"]
        assert (titles["name"], titles["authority"], titles["available"]) == (
            "The Titles of the Confederation", 12, True)
        assert titles["command"] == "decree The Princes' Dotations by titles"
        assert titles["line"].startswith("Authority 100 → 88")

    def test_decreed_by_titles_no_gold_leaves_the_chest_and_the_act_applies(self, fresh):
        _rhine(fresh)
        gold = int(fresh.nation_gold["France"])
        key = fresh._make_diplo_key("France", "Hesse")
        hesse = int(fresh.nation_relations.get(key, 0) or 0)
        out = ID.decree(fresh, DOTATIONS, currency="authority")
        assert out["authority"] == 12 and out["price"] == 0 and int(fresh.nation_gold["France"]) == gold
        assert int(fresh.authority_tracker.authority) == 88
        last = fresh.authority_tracker.moves[-1]
        assert (last["key"], last["cause"]) == ("titles_granted", "The Princes' Dotations paid in titles")
        assert int(fresh.nation_relations.get(key, 0) or 0) == min(100, hesse + 20)   # the Act's relation
        assert ID.act_decreed_turn(fresh, DOTATIONS) == int(fresh.current_turn)
        for currency in ("gold", "authority"):
            assert "decreed once" in (ID.act_refusal(fresh, DOTATIONS, currency=currency) or "")

    def test_refused_under_the_floor_with_its_reason(self, fresh):
        row = _rhine(fresh, authority=70)
        assert row["titles"]["available"] is False and "under 60" in row["titles"]["disabled_reason"]

    def test_the_verb_quotes_then_decrees_by_titles(self, fresh):
        from backend.commands.executor import CommandExecutor
        _rhine(fresh)
        ex = CommandExecutor()
        gs = {"world": fresh, "executor": ex}
        quote = ex._diplomatic._execute_decree_act(
            {"action": "decree_act", "target": "The Princes' Dotations by titles"}, gs)
        assert quote["success"] and "12 authority" in quote["message"] and "The chest is untouched" in quote["message"]
        assert quote["options"][0] == {"label": "Grant the titles",
                                       "command": "decree The Princes' Dotations by titles confirmed",
                                       "aliases": ["yes", "decree", "confirm"]}
        done = ex._diplomatic._execute_decree_act(
            {"action": "decree_act", "target": "The Princes' Dotations by titles confirmed",
             "raw_input": "decree The Princes' Dotations by titles confirmed"}, gs)
        assert done["success"], done
        assert "paid in titles, 12 authority" in done["message"]

    def test_split_titles(self):
        assert ID.split_titles("The Princes' Dotations by titles confirmed") == (
            "The Princes' Dotations confirmed", True)
        assert ID.split_titles("the Temple of Glory") == ("the Temple of Glory", False)

    def test_held_down_the_act_has_one_purse(self, fresh, monkeypatch):
        monkeypatch.setattr(ST, "offices_armed", lambda *a, **k: False)
        row = _rhine(fresh)
        assert "titles" not in row
        assert ID.act_refusal(fresh, DOTATIONS, currency="authority") == \
            "The Princes' Dotations is not granted in titles, Sire."

    def test_the_road_page_draws_the_titles_button(self):
        src = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert "func _add_titles_button(row: Dictionary) -> void:" in src
        assert src.count("_add_titles_button(row)") == 2           # both roads out of the gold button
        assert '"Grant the titles (" + str(int(titles.get("authority", 0))) + " authority)"' in src


# ═══════════════════════════════════════════════════════════════════════════
# The Proclamation — an Edict priced in authority alone, held out
# ═══════════════════════════════════════════════════════════════════════════

def _armed(monkeypatch):
    monkeypatch.setattr(ST, "proclamation_armed", lambda *a, **k: True)


def _afield(world, region="Swabia"):
    from backend.game_logic.fall import sovereign_of
    sovereign_of(world, "France").location = region
    world.__dict__.pop("_affairs_memo", None)


class TestTheProclamation:
    def test_authored_in_lockstep_priced_in_authority_alone(self):
        scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]["affairs"]
        assert scenario == json.loads(FIXTURE.read_text(encoding="utf-8"))["affairs"]
        e = {x["id"]: x for x in scenario["deck"]}[P2]
        assert e["since"] == "AU-3b" and e["shape"] == "offer" and "decree" not in e
        assert e["edict"]["authority"] == 4 and "price" not in e["edict"]
        assert (e["edict"]["term"], e["edict"]["rest"]) == (4, 8)
        assert e["edict"]["effects"] == [{"type": "drill_morale", "value": 5}]
        assert e["accept"]["ops"] == [{"op": "admin", "amount": 1}, {"op": "edict", "currency": "authority"}]
        assert AF.edict_currency(e) == "authority"
        assert [x["id"] for x in scenario["deck"]][-3:] == [P2, "the_bank", "the_popes_ports"]

    def test_held_out_until_the_users_word(self, board):
        assert ST.proclamation_armed() is False
        assert P2 not in [e["id"] for e in MO.affairs_deck(board)]
        assert MO.entry(board, P2) is None

    def test_the_premise_is_the_war_and_the_latch_the_enemy_within_a_march(self, board, monkeypatch):
        """Re-premised on the eve of battle (the user's "Re-premise it first",
        November 5, 2026): the LATCH bit is an enemy army SEEN within a march of
        the Emperor (fog-safe, `get_visible_enemies`), one of the last four
        mornings; the premise proper is the war and the price able to land —
        wherever he stands (afield it lost every pulse to the Chancellor's
        older letter on the same fact)."""
        _armed(monkeypatch)
        e = MO.entry(board, P2)
        assert e["latch"] == {"of": 4, "at_least": 1} and "proclamation_wanted" in AF.LATCHED_PREDICATES
        holds = AF.PREDICATES["proclamation_wanted"]
        _afield(board, "Lorraine")             # the boot's own place: Mack seen in Swabia, one march off
        read = holds(board, "France", e["when"])
        assert read["holds"] is True and read["latch"] is True
        assert AF._enemy_within_a_march(board, "France") == ("Mack", "Swabia")
        _afield(board, "Paris")                # home, the enemy far: the war holds, the latch does not
        read = holds(board, "France", e["when"])
        assert read["holds"] is True and read["latch"] is False
        _afield(board, "Lorraine")
        board.authority_tracker.authority = 62     # 62 − 4 = 58: under the purchases' floor
        read = holds(board, "France", e["when"])
        assert read["holds"] is False and read["latch"] is True     # the latch is read whatever the rest

    def test_a_fogged_enemy_is_never_read(self, board, monkeypatch):
        _armed(monkeypatch)
        _afield(board, "Lorraine")
        monkeypatch.setattr(type(board), "get_visible_enemies", lambda self, nation: [])
        assert AF._enemy_within_a_march(board, "France") is None

    def test_the_board_names_the_enemy_seen(self, board, monkeypatch):
        _armed(monkeypatch)
        _afield(board, "Lorraine")
        e = MO.entry(board, P2)
        line = AF._board_offer(board, e, "France", {}, 0)[0]
        assert line.startswith("Mack stands at Swabia, within a march of the Emperor (")
        assert line.endswith("against the 4 the proclamation asks.")

    def test_the_accept_is_priced_in_authority_and_says_so_on_its_button(self, board, monkeypatch):
        _armed(monkeypatch)
        _afield(board)
        board.authority_tracker.authority = 90
        e = MO.entry(board, P2)
        occ = {"id": f"{P2}#1", "lord": "France", "bind": {}, "tier": 1, "turn": int(board.current_turn)}
        board.moments["state"][occ["id"]] = dict(occ, status="fired")
        payload = MO.letter_payload(board, e, int(board.current_turn), int(board.current_turn) + 1, occ)
        assert [a["action"] for a in payload["answers"]] == ["accept_ai_proposal", "reject_ai_proposal"]
        assert payload["button_accept"] == "auth 90 → 86 · 1 action · 4 turns"
        p = MO.plan(board, e, MO.ANSWER_ACCEPT, occ)
        edict = next(r for r in p["rows"] if r["op"] == "edict")
        assert p["ok"] and (edict["currency"], edict["authority"], edict["amount"]) == ("authority", 4, 0)
        gold = int(board.nation_gold["France"])
        with _quiet():
            MO._apply(board, p)
        assert int(board.nation_gold["France"]) == gold and int(board.authority_tracker.authority) == 86
        assert reforms.drill_morale_bonus(board, "France") >= 5
        last = board.authority_tracker.moves[-1]
        assert (last["key"], last["cause"]) == ("edict_decreed", "the Proclamation decreed on the Emperor's word")

    def test_a_court_never_proclaims_before_au4(self, board, monkeypatch):
        _armed(monkeypatch)
        e = MO.entry(board, P2)
        assert AF.edict_refusal(board, "Austria", e, with_reserve=True) == "the decree is paid in authority alone."
        assert AF.edict_refusal(board, "Austria", e, currency="authority") == \
            "the courts' Decree waits for the courts' flip."
        for court in ("Austria", "Russia", "Prussia", "Britain"):
            board.nation_gold[court] = 50_000                  # a full purse: the gold road is no excuse
            order = AF.find_ai_edict(board, court, 50_000, 3)
            assert not order or order.get("target") != P2, (court, order)

    def test_the_validator_reads_the_authority_only_edict(self):
        from backend.modding.validator import validate_scenario

        def errors(mutate):
            data = json.loads(SCENARIO.read_text(encoding="utf-8"))
            e = next(x for x in data["moments"]["affairs"]["deck"] if x["id"] == P2)
            mutate(e)
            return [x.path for x in validate_scenario(data).errors if x.path.startswith("moments")]

        assert errors(lambda e: None) == []
        assert any(p.endswith(".decree") for p in errors(lambda e: e.__setitem__("decree", {"ops": []})))
        assert any(p.endswith(".accept.ops") for p in errors(
            lambda e: e["accept"]["ops"][1].__setitem__("currency", "gold")))
        assert any(p.endswith(".edict.authority") for p in errors(
            lambda e: e["edict"].__setitem__("authority", 11)))


# ═══════════════════════════════════════════════════════════════════════════
# The seams
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSeams:
    def test_the_two_seams_and_their_arms(self):
        from tests._standing_seams import STANDING_SEAMS_BY_ROW
        assert STANDING_SEAMS_BY_ROW["AUO"] == ["backend.game_logic.standing:offices_armed=False"]
        assert STANDING_SEAMS_BY_ROW["AUR"] == ["backend.game_logic.standing:proclamation_armed=False"]
        assert ST.offices_armed() is True and ST.proclamation_armed() is False
        assert "AU-3b" in AF.SINCE_ROWS and AF.row_armed("AU-3b") is False
        src = (REPO / "tools" / "_standing_series_arms.py").read_text(encoding="utf-8")
        assert 'UP_ARMS: dict = {"AUR+": {"AUR"}}' in src


# ═══════════════════════════════════════════════════════════════════════════
# The measure and the frames (§6.6)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheMeasureAndTheFrames:
    SURFACES = ("petition_fontainebleau_endow", "wizard_designs_titles", "affair_letter_the_proclamation",
                "authority_dent")

    def test_the_review_record_measured_the_proclamation_armed(self):
        rec = json.loads((REPO / "tools" / "_affairs_au3b_proclamation.json").read_text(encoding="utf-8"))
        assert rec["letters"] == [P2] and rec["runs_measured"] >= 55
        totals = rec["totals"][P2]
        # armed, it arrives somewhere — the figures are §6.6.5's, per run (seeded paths, not laws)
        assert totals["arrivals"] > 0 and totals["runs_arrived"] > 0 and totals["runs_premise"] > 0

    def test_the_first_premises_record_is_kept_beside_the_re_premise(self):
        """§6.6.5 (the user's "Re-premise it first"): the first premise's armed
        record is kept as the record (AU-2c's `_first` idiom); the re-premise
        rewrote the review record — the eve of battle arrives where the
        Emperor afield lost the pulse to the Chancellor's older letter."""
        first = json.loads((REPO / "tools" / "_affairs_au3b_proclamation_first.json").read_text(encoding="utf-8"))
        now = json.loads((REPO / "tools" / "_affairs_au3b_proclamation.json").read_text(encoding="utf-8"))
        assert first["letters"] == [P2] and first["runs_measured"] == now["runs_measured"]
        assert now["totals"][P2]["runs_arrived"] > first["totals"][P2]["runs_arrived"]

    def test_the_series_holds_on_the_slices_arms_with_the_proclamation_up(self):
        rec = json.loads((REPO / "tools" / "_standing_series_arms_final.json").read_text(encoding="utf-8"))
        assert {"AUO", "AUR", "AUR+"} <= set(rec["arms"])
        for arm in ("AUO", "AUR", "AUR+"):
            assert rec["arms"][arm]["first_divergence_vs_prior"] is None, arm

    def test_the_stagings_are_wired(self):
        cap = (REPO / "tools" / "iq10_capture_payloads.py").read_text(encoding="utf-8")
        shots = (REPO / "tools" / "iq10_run_captures.py").read_text(encoding="utf-8")
        for name in ("petition_fontainebleau_endow", "designs_road_page_titles", "affair_letter_the_proclamation"):
            assert f'record("{name}"' in cap, name
        assert '"id": "petition_fontainebleau_endow",' in shots and '"id": "wizard_designs_titles",' in shots
        assert '("the_proclamation",' in shots

    def test_the_harness_scrolls_inside_the_content_on_request(self):
        src = (REPO / "tools" / "iq10_surface_screenshot.gd").read_text(encoding="utf-8")
        assert 'if bool(how.get("in_content", false)):' in src
        assert "y += rtl.global_position.y - content.global_position.y" in src

    @pytest.mark.parametrize("surface", SURFACES)
    def test_the_surface_is_shot_at_both_scales(self, surface):
        for tail in ("", "_X2"):
            png = REPO / "docs" / "audits" / f"IQ10_{surface.upper()}{tail}_2026_11_05.png"
            assert png.exists() and png.stat().st_size > 8000, png

    def test_the_readability_census_reads_no_red_and_no_p1(self):
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        from uxr0_readability_report import PHYSICAL_RESOLUTIONS
        record = json.loads((REPO / "docs" / "audits" / "uxr0" / "readability_au3b_offices_2026_11_05.json")
                            .read_text(encoding="utf-8"))
        assert set(record["surfaces"]) == set(self.SURFACES)
        for sid, row in record["surfaces"].items():
            assert len(row["readings"]) == len(PHYSICAL_RESOLUTIONS), sid
            for label, reading in row["readings"].items():
                counts = reading["counts"]
                assert counts["rows"] > 0 and counts["red"] == 0 and counts["p1"] == 0, (sid, label)
