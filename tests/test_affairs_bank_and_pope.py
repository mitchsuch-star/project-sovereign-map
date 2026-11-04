"""AU-2c "the Bank and the Pope" (docs/AUTHORITY_CURRENCY_SPEC.md §5.4, §6.4):
two affairs letters whose refusal is priced in authority alone — the Bank's
Panic (the chest strained at war) and the Pope's Refusal (the war with
Britain, the user's word of November 4, 2026) — authored `since: "AU-2c"`
and held WHOLE out of the deck until the user's word arms them
(`standing.letters_armed`, RE's rule: a template without a measured premise
is not armed). Both take `bites: "floor"` (the clamp's rule: a refusal priced
in authority alone may not clamp). The Pope's Accept costs the Papal States
−10 (the user's second answer: the court exists — Rome its one province).
"""
import contextlib
import copy
import io
import json
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import affairs as AF
from backend.game_logic import moments as MO
from backend.game_logic import standing as ST
from tests import _chip_census as C

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
BANK, POPE = "the_bank", "the_popes_ports"
BEFORE_AU2C = ["chancellors_letters", "the_host", "berthiers_memorial", "santo_domingo",
               "the_magazines", "the_remounts", "camps_of_instruction"]


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
    w = M.world
    w.moments = MO.from_block(json.loads(FIXTURE.read_text(encoding="utf-8")))
    return w


@pytest.fixture
def up(world, monkeypatch):
    """The two letters measured UP (the review record's arm)."""
    monkeypatch.setattr(ST, "letters_armed", lambda *a, **k: True)
    world.__dict__.pop("_affairs_memo", None)
    return world


def _read(world, template):
    world.__dict__.pop("_affairs_memo", None)
    return AF.premise_holds(world, MO.entry(world, template), "France")


def _forecast(monkeypatch, chest, net):
    import backend.game_logic.ledger as L
    monkeypatch.setattr(L, "chest_forecast",
                        lambda w, n: {"chest": int(chest), "net": int(net), "projected": int(chest) + int(net)})


def _peace_with(world, court):
    world.diplomatic_states[world._make_diplo_key("France", court)] = "PEACE"
    world.invalidate_active_nations_cache()


def _plan(world, template, side, turn):
    occ = {"id": f"{template}#1", "lord": "France", "bind": {}, "tier": 1, "turn": turn}
    return MO.plan(world, MO.entry(world, template), side, occ)


class TestTheSeamHoldsThemOut:
    def test_the_shipped_default_is_down_until_the_user_arms_them(self):
        """Rule 9's behaviour test: the letters are AUTHORED, NOT ARMED — the
        owner is AU-2c's review, the landing its flip commit (re-measured),
        and flipping it re-pins this line consciously."""
        assert ST.letters_armed() is False
        assert AF.row_armed("AU-2c") is False and AF.row_armed("AU-2b") is True

    def test_down_every_reader_sees_the_deck_before_au_2c(self, world):
        assert [e["id"] for e in AF.deck(world)] == BEFORE_AU2C
        assert MO.entry(world, BANK) is None and MO.entry(world, POPE) is None
        world.nation_gold["France"] = 20_000
        world.authority_tracker.authority = 100
        world.__dict__.pop("_affairs_memo", None)
        assert not [c for c in AF.candidates(world, 30) if c["e"]["id"] in (BANK, POPE)]
        assert not [line for line in AF.watch(world, record=False) if "Caprara" in line or "Bank" in line]

    def test_the_rig_holds_the_seam_and_measures_it_up(self):
        """Arm AUL (`tests/_standing_seams.py`) is down by default; the series
        rig's AUL+ arm forces it up, its reach counted (the letters' arrivals)."""
        from tests._standing_seams import STANDING_SEAMS_BY_ROW
        assert STANDING_SEAMS_BY_ROW["AUL"] == ["backend.game_logic.standing:letters_armed=False"]
        rig = (REPO / "tools" / "_standing_series_arms.py").read_text(encoding="utf-8")
        assert 'UP_ARMS = {"AUL+": {"AUL"}}' in rig and "the_popes_ports_delivered" in rig

    def test_up_both_letters_stand_last(self, up):
        assert [e["id"] for e in AF.deck(up)] == BEFORE_AU2C + [BANK, POPE]
        assert AF.entry_armed(MO.entry(up, BANK)) and AF.entry_armed({"id": "x"})


class TestTheBanksPremise:
    """The Bank's premise is the steady part — at war, the purse able to pay —
    and the strain is its LATCH bit, counted 4 of the last 12 mornings (the
    Haiti idiom). The first definition made the deficit the premise itself: a
    strain that eased for one morning reset its streak, and on 55 runs the
    letter lost every pulse to the older matters — never arrived (§6.4)."""

    def test_the_boot_chest_holds_nothing(self, up):
        assert int(up.gold) < 2_000
        read = _read(up, BANK)
        assert read["holds"] is False and read["latch"] is False     # the boot's Net is in surplus

    def test_a_war_that_outruns_the_chest(self, up, monkeypatch):
        up.gold = 6_000
        _forecast(monkeypatch, 6_000, -500)
        read = _read(up, BANK)
        assert read["holds"] is True and read["latch"] is True       # dry in twelve turns

    def test_a_rich_chest_in_deficit_is_not_strained(self, up, monkeypatch):
        """The Charges draw more from a fuller chest by design (EB-1): a
        hoarder's deficit is not the Treasury's crisis."""
        up.gold = 30_000
        _forecast(monkeypatch, 30_000, -500)
        read = _read(up, BANK)
        assert read["holds"] is True and read["latch"] is False
        _forecast(monkeypatch, 6_000, 300)
        up.gold = 6_000
        assert _read(up, BANK)["latch"] is False

    def test_at_peace_nothing(self, up, monkeypatch):
        up.gold = 6_000
        _forecast(monkeypatch, 6_000, -500)
        for court in list(up.get_nations_at_war_with("France")):
            _peace_with(up, court)
        read = _read(up, BANK)
        assert read["holds"] is False and read["latch"] is False

    def test_the_purse_must_pay_the_bank(self, up, monkeypatch):
        _forecast(monkeypatch, 1_999, -500)
        up.gold = 1_999
        read = _read(up, BANK)
        assert read["holds"] is False and read["latch"] is True      # strained, but the Bank cannot be paid
        up.gold = 2_000
        assert _read(up, BANK)["holds"] is True

    def test_a_genuine_deficit_on_the_boot(self, up):
        """No patched forecast: the corps raised 15 % over their muster on a
        6,000 chest — the ledger's own Net runs the chest dry in under 20."""
        up.gold = 6_000
        for m in up.marshals.values():
            if m.nation == "France" and not getattr(m, "is_sovereign", False):
                m.strength = int(m.strength * 1.15)
        read = _read(up, BANK)
        assert read["holds"] is True and read["latch"] is True

    def test_the_latch_gates_the_arrival_four_of_twelve(self, up, monkeypatch):
        """The letter is due only once the strain held 4 of the last 12
        mornings; a morning of ease keeps the count (it does not reset)."""
        e = MO.entry(up, BANK)
        assert e["latch"] == {"of": 12, "at_least": 4} and "chest_strained" in AF.LATCHED_PREDICATES
        masks = AF.runtime(up).setdefault("masks", {})
        masks[BANK] = 0b101010
        assert AF.latch_count(up, e) == 3 and not AF.latch_ok(up, e)
        masks[BANK] = 0b1010101
        assert AF.latch_count(up, e) == 4 and AF.latch_ok(up, e)


class TestThePopesPremise:
    def test_at_war_with_britain_with_the_purse(self, up):
        up.gold = 5_000
        assert _read(up, POPE)["holds"] is True

    def test_peace_with_britain_closes_it(self, up):
        up.gold = 5_000
        _peace_with(up, "Britain")
        assert _read(up, POPE)["holds"] is False

    def test_the_court_as_a_client_at_war_or_in_the_system_closes_it(self, up):
        up.gold = 5_000
        up.vassals["PapalStates"] = {"lord": "France"}
        assert _read(up, POPE)["holds"] is False
        up.vassals.pop("PapalStates")
        up.diplomatic_states[up._make_diplo_key("France", "PapalStates")] = "WAR"
        assert _read(up, POPE)["holds"] is False
        _peace_with(up, "PapalStates")
        up.continental_system_members = ["PapalStates"]
        assert _read(up, POPE)["holds"] is False
        up.continental_system_members = []
        assert _read(up, POPE)["holds"] is True

    def test_no_court_no_letter(self, up, monkeypatch):
        up.gold = 5_000
        active = [n for n in up.get_active_nations() if n != "PapalStates"]
        monkeypatch.setattr(type(up), "get_active_nations", lambda self: list(active))
        assert _read(up, POPE)["holds"] is False

    def test_the_purse_must_pay_the_occupation(self, up):
        up.gold = 1_799
        assert _read(up, POPE)["holds"] is False
        up.gold = 1_800
        assert _read(up, POPE)["holds"] is True


class TestThePlans:
    def test_the_bank_pays_in_coin_or_lets_the_notes_fall(self, up):
        up.gold, up.admin_actions_remaining = 6_000, 2
        up.authority_tracker.authority = 85
        accept = _plan(up, BANK, MO.ANSWER_ACCEPT, 16)
        assert accept["ok"]
        assert [(r["op"], r.get("amount")) for r in accept["rows"]] == [("gold", 1000), ("admin", 1)]
        assert accept["receipt"] == "−1,000 gold · 1 action (1 left)"
        decline = _plan(up, BANK, MO.ANSWER_DECLINE, 16)
        assert [(r["op"], r["loss"]) for r in decline["rows"]] == [("authority", 4)]
        assert decline["receipt"] == "authority 85 → 81"

    def test_the_pope_is_pressed_or_refused(self, up):
        up.gold, up.admin_actions_remaining = 6_000, 2
        up.authority_tracker.authority = 85
        accept = _plan(up, POPE, MO.ANSWER_ACCEPT, 12)
        assert accept["ok"]
        rows = accept["rows"]
        assert [r["op"] for r in rows] == ["gold", "admin", "relation"]
        assert rows[0]["amount"] == 800 and rows[2]["court"] == "PapalStates"
        assert int(rows[2]["after"]) - int(rows[2]["before"]) == -10
        assert accept["receipt"] == f"−800 gold · 1 action · Rome {rows[2]['before']} → {rows[2]['after']}"
        decline = _plan(up, POPE, MO.ANSWER_DECLINE, 12)
        assert [(r["op"], r["loss"]) for r in decline["rows"]] == [("authority", 5)]
        assert decline["receipt"] == "authority 85 → 80"

    def test_the_floor_closes_each_and_full_standing_does_not(self, up):
        for template, open_at, closed_at in ((BANK, 75, 74), (POPE, 76, 75)):
            e = MO.entry(up, template)
            for authority in (100, open_at):
                up.authority_tracker.authority = authority
                assert AF.bites(up, "France", e, 1) is True, (template, authority)
            up.authority_tracker.authority = closed_at
            assert AF.bites(up, "France", e, 1) is False, (template, closed_at)

    def test_the_decline_is_booked_to_its_writer(self, up):
        up.gold = 6_000
        for template, writer, loss in ((POPE, "Caprara", 5), (BANK, "Regents of the Bank of France", 4)):
            up.authority_tracker.authority = 90
            plan = _plan(up, template, MO.ANSWER_DECLINE, 16)
            with _quiet():
                MO._apply(up, plan)
            last = up.authority_tracker.moves[-1]
            assert (last["key"], last["party"], last["delta"]) == ("letter_declined", writer, -loss), last
            assert int(up.authority_tracker.authority) == 90 - loss


class TestThePossessiveIsSaidRight:
    """AU-10 (`BUG_FIXES.md` §AU): a court's possessive mid-quote read "The
    Papal States's goodwill" — the article capitalised and "'s" after a final
    s. One source now (`display_names.possessive`, SRX-22's rule) at the
    relation line, its sibling the loyalty line, and the two boards."""

    def test_the_rule(self):
        from backend.display_names import possessive
        assert possessive("the Papal States") == "the Papal States'"
        assert possessive("Bavaria") == "Bavaria's"
        assert possessive("the Kingdom of Italy") == "the Kingdom of Italy's"

    def test_the_relation_and_loyalty_lines_sit_mid_quote(self, world):
        line = MO._plan_relation(world, "France", {"op": "relation", "court": "PapalStates", "delta": -10})["line"]
        assert line.startswith("the Papal States' goodwill "), line
        line = MO._plan_relation(world, "France", {"op": "relation", "court": "Bavaria", "delta": -2})["line"]
        assert line.startswith("Bavaria's goodwill "), line
        line = MO._plan_loyalty(world, "France", {"op": "loyalty", "court": "KingdomOfItaly", "delta": -2})["line"]
        assert line.startswith("the Kingdom of Italy's loyalty as your vassal "), line

    def test_the_hosts_board_names_its_host_mid_sentence(self, world):
        e = MO.entry(world, "the_host")
        occ = {"id": "the_host#1", "lord": "France", "bind": {"host": "KingdomOfItaly"}, "tier": 1}
        lines = AF._board(world, e, occ)
        assert "stand on the Kingdom of Italy's soil" in lines[0], lines
        assert "The Kingdom" not in lines[0], lines


class TestTheFrames:
    """The two letters as the client draws them, measured UP for the review
    (`tools/iq10_capture_payloads.py` holds the seam up in its staging alone),
    at 1.0 and 2.0, and the physical census at the five resolutions."""
    STEMS = ("THE_BANK", "THE_POPES_PORTS")

    def test_the_staging_and_the_shots_are_wired(self):
        cap = (REPO / "tools" / "iq10_capture_payloads.py").read_text(encoding="utf-8")
        shots = (REPO / "tools" / "iq10_run_captures.py").read_text(encoding="utf-8")
        for template in (BANK, POPE):
            assert f'record("affair_letter_{template}"' in cap, template
            assert f'("{template}",' in shots, template

    def test_both_letters_are_shot_at_both_scales(self):
        for stem in self.STEMS:
            for tail in ("", "_X2"):
                png = REPO / "docs" / "audits" / f"IQ10_AFFAIR_LETTER_{stem}{tail}_2026_11_04.png"
                assert png.exists() and png.stat().st_size > 8000, png

    def test_the_readability_census_reads_no_red_and_no_p1(self):
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        from uxr0_readability_report import PHYSICAL_RESOLUTIONS
        record = json.loads((REPO / "docs" / "audits" / "uxr0" / "readability_au2c_letters_2026_11_04.json")
                            .read_text(encoding="utf-8"))
        surfaces = record["surfaces"]
        assert set(surfaces) == {f"affair_letter_{BANK}", f"affair_letter_{POPE}"}
        for sid, row in surfaces.items():
            readings = row["readings"]
            assert len(readings) == len(PHYSICAL_RESOLUTIONS), sid
            for label, reading in readings.items():
                counts = reading["counts"]
                assert counts["rows"] > 0 and counts["red"] == 0 and counts["p1"] == 0, (sid, label)


class TestTheDeckAndTheValidator:
    def test_the_lockstep_and_the_clauses(self):
        scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]["affairs"]
        assert scenario == json.loads(FIXTURE.read_text(encoding="utf-8"))["affairs"]
        by_id = {e["id"]: e for e in scenario["deck"]}
        for template, loss in ((BANK, -4), (POPE, -5)):
            e = by_id[template]
            assert e["since"] == "AU-2c" and e["bites"] == "floor" and "bites_since" not in e
            assert e["decline"]["ops"] == [{"op": "authority", "amount": loss}]
            assert e["source"] and e["watch"] and "may" in e["watch"]
        assert by_id[POPE]["when"] == {"predicate": "ports_defied", "court": "PapalStates", "min_purse": 800}
        assert by_id[POPE]["ends"] == {"date": "1809-05-17", "turn": 89}
        assert by_id[BANK]["when"] == {"predicate": "chest_strained", "within": 20, "min_purse": 1000}

    def test_the_validator_refuses_a_bad_horizon_court_row_or_clamp(self):
        from backend.modding import validator as V
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        assert not V.validate_scenario(data).errors
        bad = copy.deepcopy(data)
        deck = {e["id"]: e for e in bad["moments"]["affairs"]["deck"]}
        deck[BANK]["when"]["within"] = 99
        deck[BANK]["since"] = "AU-9z"
        deck[POPE]["when"]["court"] = "PapalStatez"
        deck[POPE]["bites"] = "clamp"        # a refusal priced in authority alone may not clamp
        errors = " | ".join(str(x) for x in V.validate_scenario(bad).errors)
        assert "when.within" in errors and ".since" in errors and "Unknown nation 'PapalStatez'" in errors
        assert "bites" in errors
