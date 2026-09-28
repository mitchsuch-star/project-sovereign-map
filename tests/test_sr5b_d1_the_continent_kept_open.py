"""SR5B-D1 "The Continent kept open" — RULED September 28, 2026 under the
user's delegation ("make these decisions"): **keep the rule and name the army
holding the Continent open.**

The SHUT OUT reading (`congress._shut_out_reading`) is unchanged: the ports
(13 of 26) AND no corps of hers on the Continent. SR-5b played it for 240
turns and it never held — every time the ports were shut a British corps was
ashore in Iberia, which is the Peninsular War, Britain's historical answer to
the System. No surface said which corps. Now one source,
`congress.continent_holders`, names them where they stand, for the Congress
price, the lapse beat and THE ADMIRALTY's System line. Fog-honest: the truth
of the reading is omniscient, its words are not — a corps out of sight is
counted and never placed. Rules `docs/SYSTEMS_REFERENCE.md` §80; row
`docs/DESIGN_REFINEMENT.md` SR5B-D1. Lever `congress.NAME_THE_CONTINENTS_HOLDERS`.
"""
import contextlib
import io
from pathlib import Path

from backend.game_logic import congress, naval
from backend.models.intel import PARTIAL
from backend.models.world_state import WorldState

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
SCEN = str(MAPS / "europe_1805.json")
TUTORIAL = str(MAPS / "tutorial_1805.json")

_PORT_COURTS = ("Portugal", "Denmark", "Sweden", "Ottoman", "Naples",
                "Prussia", "Russia", "Austria", "Sardinia")


def _boot(path=SCEN) -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(path)


def _close(w, n=13):
    """Shut ports by putting Continental coast courts at war with Britain
    (the `test_congress_of_paris.TestShutOut` idiom)."""
    for nation in _PORT_COURTS:
        if round(naval.closure_against(w, "Britain") * naval.continental_ports_total(w)) >= n:
            break
        w.diplomatic_states[w._make_diplo_key(nation, "Britain")] = "WAR"
    w.invalidate_active_nations_cache()
    assert congress._shut_out_reading(w, "Britain")["closed"] >= n


def _place(w, marshal, where):
    w.marshals[marshal].location = where
    with contextlib.redirect_stdout(io.StringIO()):
        w.calculate_visibility()


def _seen(w, where) -> bool:
    return bool(w.get_region_intel(where).visibility_at_least(PARTIAL))


def _ports_text(w) -> str:
    row = congress.answer(w, "Britain")
    lever = next(lv for lv in congress.price(w, "Britain", row)["levers"]
                 if lv["key"] == "ports")
    return lever["text"]


def _second_british_marshal(w) -> str:
    """Moore is Britain's only corps at the boot; commission Paget from the
    authored bench, as Britain's AI does (P1.75)."""
    from backend.game_logic import recruitment
    candidate = recruitment.find_candidate(w, "Britain", "Paget")
    assert candidate, "the 1805 bench authors Paget for Britain"
    w.nation_gold["Britain"] = max(int(w.nation_gold.get("Britain", 0)),
                                   int(candidate.get("cost", 0)) + 1000)
    with contextlib.redirect_stdout(io.StringIO()):
        recruitment.commission_marshal(w, "Britain", candidate)
    return "Paget"


# ════════════════════════════════════════════════════════════════════════
# The rule is KEPT — the stance is the omniscient reading, exactly as before.
# ════════════════════════════════════════════════════════════════════════

class TestTheRuleIsKept:
    def test_a_corps_on_the_continent_still_keeps_her_at_the_table(self):
        w = _boot()
        _close(w)
        _place(w, "Moore", "Flanders")
        assert congress.answer(w, "Britain")["stance"] != congress.SHUT_OUT

    def test_an_unseen_corps_keeps_her_at_the_table_too(self):
        """Fog changes the words, never the truth: the reading is the same
        whether or not France can see the corps."""
        w = _boot()
        _close(w)
        _place(w, "Moore", "Lisbon")
        assert not _seen(w, "Lisbon"), "the staging needs Lisbon out of sight"
        assert congress.answer(w, "Britain")["stance"] != congress.SHUT_OUT
        assert congress.corps_on_the_continent(w, "Britain") == ["Moore"]

    def test_with_no_corps_on_the_continent_she_is_shut_out(self):
        w = _boot()
        _close(w)
        _place(w, "Moore", "London")
        assert congress.answer(w, "Britain")["stance"] == congress.SHUT_OUT


# ════════════════════════════════════════════════════════════════════════
# The Congress price names the corps where it stands.
# ════════════════════════════════════════════════════════════════════════

class TestThePriceNamesTheCorps:
    def test_ports_short_the_lever_names_both_terms(self):
        w = _boot()
        _place(w, "Moore", "Flanders")
        assert _seen(w, "Flanders")
        text = _ports_text(w)
        closed = congress._shut_out_reading(w, "Britain")["closed"]
        assert text == f"shut 13 of 26 ports (now {closed}) and drive Moore from Flanders"

    def test_ports_shut_the_corps_is_the_whole_lever(self):
        w = _boot()
        _close(w)
        _place(w, "Moore", "Flanders")
        closed = congress._shut_out_reading(w, "Britain")["closed"]
        assert _ports_text(w) == (f"drive Moore from Flanders — {closed} of 26 ports "
                                  f"are already shut against her")
        assert congress.answer(w, "Britain")["stance"] == congress.REFUSES

    def test_the_lever_is_in_the_price_the_table_prints(self):
        w = _boot()
        _close(w)
        _place(w, "Moore", "Flanders")
        payload = congress.build_congress_payload(w)
        britain = next(c for c in payload["courts"] if c["nation"] == "Britain")
        assert "drive Moore from Flanders" in britain["price"]

    def test_an_unseen_corps_is_counted_never_placed(self):
        w = _boot()
        _close(w)
        _place(w, "Moore", "Lisbon")
        assert not _seen(w, "Lisbon")
        text = _ports_text(w)
        assert "a British corps our scouts have not found from the Continent" in text
        assert "Lisbon" not in text and "Moore" not in text

    def test_two_corps_in_one_province_share_one_clause(self):
        w = _boot()
        other = _second_british_marshal(w)
        _place(w, "Moore", "Flanders")
        _place(w, other, "Flanders")
        shown = congress.continent_holders(w, "Britain")["named"]
        names = " and ".join(h["display"] for h in shown)
        assert f"drive {names} from Flanders" in _ports_text(w)

    def test_a_seen_and_an_unseen_corps_are_both_named_honestly(self):
        w = _boot()
        other = _second_british_marshal(w)
        _place(w, "Moore", "Flanders")
        _place(w, other, "Lisbon")
        assert _seen(w, "Flanders") and not _seen(w, "Lisbon")
        text = _ports_text(w)
        assert "drive Moore from Flanders and a British corps our scouts have not " \
               "found from the Continent" in text
        assert "Lisbon" not in text


# ════════════════════════════════════════════════════════════════════════
# THE ADMIRALTY's System line (the payload the ledger tab renders).
# ════════════════════════════════════════════════════════════════════════

class TestTheAdmiraltyLine:
    def _line(self, w) -> str:
        cs = naval.build_admiralty_report(w).get("continental_system") or {}
        return str(cs.get("shut_out_line", ""))

    def test_at_the_boot_it_names_the_target_and_the_ports_to_close(self):
        w = _boot()
        closed = congress._shut_out_reading(w, "Britain")["closed"]
        line = self._line(w)
        assert line.startswith(f"Britain would be shut out of the Congress of Paris "
                               f"at 13 of 26 ports ({closed} now)")
        assert line.endswith(f"{13 - closed} more ports to close.") or \
            line.endswith("1 more port to close.")

    def test_a_corps_ashore_is_named_as_the_one_keeping_the_continent_open(self):
        w = _boot()
        _place(w, "Moore", "Flanders")
        assert self._line(w).endswith(
            "— today Moore at Flanders keeps the Continent open to her.")

    def test_ports_shut_the_line_says_the_corps_alone_stands_between(self):
        w = _boot()
        _close(w)
        _place(w, "Moore", "Flanders")
        line = self._line(w)
        assert "ports are closed to Britain, but Moore at Flanders keeps the " \
               "Continent open to her: drive it off" in line

    def test_when_she_is_shut_out_the_line_says_so(self):
        w = _boot()
        _close(w)
        _place(w, "Moore", "London")
        assert self._line(w).startswith("Britain is shut out of the Congress of Paris")

    def test_two_corps_take_the_plural(self):
        w = _boot()
        _close(w)
        other = _second_british_marshal(w)
        _place(w, "Moore", "Flanders")
        _place(w, other, "Flanders")
        line = self._line(w)
        assert " keep the Continent open to her: drive them off" in line

    def test_a_spent_shut_out_says_it_cannot_come_this_sitting(self):
        from tests.test_congress_of_paris import _sit
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            _sit(w)
        assert congress.sitting(w)
        w.congress["shut_out_broken"] = True
        assert "can no longer be shut out at this sitting" in self._line(w)

    def test_no_line_where_the_congress_is_not_armed(self):
        w = _boot(TUTORIAL)
        assert not congress.armed(w)
        cs = naval.build_admiralty_report(w).get("continental_system") or {}
        assert "shut_out_line" not in cs

    def test_no_line_on_the_1805_board_with_its_endings_unauthored(self):
        """The sweep's mutant (the `armed` guard deleted) survived the
        tutorial alone — the tutorial has no System to read. The 1805 board
        HAS the System; strip its `campaign_end` block and the Congress is
        unarmed while the ports are still counted."""
        w = _boot()
        _place(w, "Moore", "Flanders")
        w.campaign_end = {}
        assert not congress.armed(w)
        cs = naval.build_admiralty_report(w).get("continental_system") or {}
        assert cs, "the System is still read on the unarmed 1805 board"
        assert "shut_out_line" not in cs


# ════════════════════════════════════════════════════════════════════════
# One clause everywhere; the AI has no fog; the lever restores the old words.
# ════════════════════════════════════════════════════════════════════════

class TestOneSource:
    def test_the_lapse_beat_speaks_the_same_clause(self):
        w = _boot()
        _place(w, "Moore", "Flanders")
        clause = congress.continent_kept_open_clause(w, "Britain")
        assert clause == "Moore at Flanders keeps the Continent open to her"
        assert congress._shut_out_lapse_reason(w, "Britain") == clause

    def test_the_lapse_beat_never_places_an_unseen_corps(self):
        w = _boot()
        _place(w, "Moore", "Lisbon")
        reason = congress._shut_out_lapse_reason(w, "Britain")
        assert reason == ("a British corps our scouts have not found keeps the "
                          "Continent open to her")

    def test_the_ai_has_no_fog(self):
        w = _boot()
        _place(w, "Moore", "Lisbon")
        assert not _seen(w, "Lisbon")
        holders = congress.continent_holders(w, "Britain", viewer="Britain")
        assert holders["named"] == [{"marshal": "Moore", "display": "Moore",
                                     "location": "Lisbon"}]
        assert holders["unseen"] == 0

    def test_no_clause_when_no_corps_stands_on_the_continent(self):
        w = _boot()
        _place(w, "Moore", "London")
        assert congress.continent_kept_open_clause(w, "Britain") == ""

    def test_lever_down_restores_the_pre_ruling_words(self, monkeypatch):
        monkeypatch.setattr(congress, "NAME_THE_CONTINENTS_HOLDERS", False)
        w = _boot()
        _place(w, "Moore", "Flanders")
        closed = congress._shut_out_reading(w, "Britain")["closed"]
        assert _ports_text(w) == (f"shut 13 of 26 ports (now {closed}) and drive her "
                                  f"corps from the Continent")
        assert congress._shut_out_lapse_reason(w, "Britain") == \
            "Moore stands on the Continent at Flanders"
        cs = naval.build_admiralty_report(w).get("continental_system") or {}
        assert "shut_out_line" not in cs
