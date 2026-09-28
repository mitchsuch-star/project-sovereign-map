"""SR-5r RF-4c — "The School card and the visual pass" (`docs/REFORMS_SPEC.md`
§8, §8a, §11 T7/T8; §12 RF-4c).

* THE SCHOOL'S TWENTIETH CARD — "XVIII. The Laws of State": the lesson
  authors France's own five laws (the 1805 deck verbatim — a drift pin holds
  them equal); the card opens the ledger's eighth book (a door, like the
  Cabinet card's), names the Grand Quartier Général and suggests
  `enact the Staff` (it fills the line; the Council of State's confirm asks
  the terms). It completes when a law is enacted (a latch on the
  `law_enacted` event). Driven through the real lesson.
* T7 — NO DEATH SPIRAL, its last clause: after a lapse and a return to
  solvency, the Staff restores at its Arrears price, and the LAWS tab, the
  confirm and the AI rung all quote that ONE price (`restoration_price`).
  (The forecast on three surfaces and the "repeal X instead" lever are
  RF-4b's pins; T7's staged lapse runs the REAL lapse loop here.)
* T8 — NOTHING UNNAMED, in the doctrines' T10 idiom: an instrumented census
  over a campaign — France holds its laws, the board runs ten turns, and
  every law effect the player can see that turn is checked against the
  surface that names it. Pass: 0 unnamed.
"""
import contextlib
import io
import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.game_logic import reforms as R
from backend.game_logic.ledger import build_strategic_ledger
from tests import _chip_census as C
from tests.test_tutorial_unbreakable_2026_09_23 import (  # noqa: F401 (fixture)
    Recorder, _drive_overlay, lesson)

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "godot-client" / "project-sovereign" / "scripts"
MAPS = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
STAFF_ID = "grand_quartier_general"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _func_body(src, name):
    return src.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]


def _card(src, card_id):
    return src.split(f'"id": "{card_id}"', 1)[1].split('"id": ', 1)[0]


# ═══════════════════════════ THE SCHOOL'S TWENTIETH CARD ══════════════════════

class TestTheLawsCard:

    def test_the_card_follows_the_congress(self):
        from backend.game_logic import tutorial_state as T
        ids = [s[0] for s in T.STEPS]
        assert len(ids) == 20
        assert ids.index("laws") == ids.index("congress") + 1
        assert dict((s[0], (s[1], s[2])) for s in T.STEPS)["laws"] == (
            12, "XVIII. The Laws of State")

    def test_the_card_opens_the_laws_book_and_names_the_staff(self):
        card = _card((SCRIPTS / "tutorial_overlay.gd").read_text(encoding="utf-8"), "laws")
        assert '"open": "ledger:7"' in card
        assert '"suggest": "enact the Staff"' in card
        assert '"suggest_action": "enact_law"' in card
        assert '"advance": "_pred_law_enacted"' in card
        for words in ("THE LAWS", "Grand Quartier Général", "Council of State",
                      "LAPSES", "half its price"):
            assert words in card, words

    def test_the_lesson_carries_the_1805_deck(self):
        tut = json.loads((MAPS / "tutorial_1805.json").read_text(encoding="utf-8"))
        europe = json.loads((MAPS / "europe_1805.json").read_text(encoding="utf-8"))
        assert tut["reforms"] == {"France": europe["reforms"]["France"]}

    def test_the_lesson_can_carry_the_staff_by_the_card(self):
        from backend.game_logic.ledger import _build_economy
        from backend.models.world_state import WorldState
        with _quiet():
            world = WorldState.from_scenario(str(MAPS / "tutorial_1805.json"))
            net = int(_build_economy(world, "France")["net"])
        assert [r["id"] for r in R.deck(world, "France")][0] == STAFF_ID
        assert net > 300, "the Staff's upkeep can never starve the lesson"
        assert int(world.nation_gold["France"]) + 11 * net >= 9000 + 1000

    def test_the_door_opens_the_real_ledger(self):
        overlay = (SCRIPTS / "tutorial_overlay.gd").read_text(encoding="utf-8")
        assert "signal open_ledger(tab: int)" in overlay
        assert re.search(r'begins_with\("open:ledger:"\):[\s\S]*?open_ledger\.emit\(int\(meta_str\.substr\(12\)\)\)',
                         _func_body(overlay, "_on_meta_clicked"))
        main = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        assert "tutorial_overlay.open_ledger.connect(_on_tutorial_open_ledger)" in main
        assert "top_bar.open_ledger_to_tab(tab)" in _func_body(main, "_on_tutorial_open_ledger")

    def test_the_card_completes_on_a_law_enacted(self):
        overlay = (SCRIPTS / "tutorial_overlay.gd").read_text(encoding="utf-8")
        notes = _func_body(overlay, "_note_observations")
        assert 'str(e.get("type", "")) == "law_enacted"' in notes and "_saw_law = true" in notes
        assert "return _saw_law" in _func_body(overlay, "_pred_law_enacted")

    def test_the_driven_lesson_enacts_the_staff_on_the_card(self, lesson, tmp_path):
        """The committed lesson script, played by hand: at the laws card's
        gate it sends `enact the Staff`, the Council's quote is answered, the
        Staff is in force — and the card FIRES (it moves on before its
        catch-up turn, gate + 2)."""
        client, Mod, boot = lesson
        rec = Recorder(client, Mod, boot)
        script = json.loads((ROOT / "tools" / "playtest_scripts"
                             / "tutorial_lesson.json").read_text(encoding="utf-8"))
        for loop in range(1, 14):
            for line in script["turns"].get(str(loop), []):
                rec.settle(rec.say(line))
            rec.end_turn_until(loop + 1)
        assert R.is_in_force(R.find_law(rec.world, "France", STAFF_ID))
        result = _drive_overlay(rec.spec(), tmp_path)
        rows = result["steps"]
        after = [r for r in rows if r["id"] in ("free_books", "handoff")]
        assert after and after[0]["turn"] < 14, [(r["id"], r["turn"]) for r in rows[-6:]]
        assert "You skipped" not in "\n".join(r["body"] for r in rows)


class TestTheVisualPass:

    def test_the_forecast_leads_the_laws_book(self):
        """The RF-4c frame (`docs/audits/IQ10_LEDGER_LAWS_FORECAST_2026_09_27.png`)
        showed the forecast below the fold, after five laws; it leads now."""
        body = _func_body((SCRIPTS / "strategic_ledger.gd").read_text(encoding="utf-8"),
                          "_render_laws_tab")
        assert body.index('laws.get("forecast", null)') < body.index('for row in laws.get("rows", [])')

    def test_the_staffs_repeal_chip_says_what_it_takes_away(self, world):
        """The frame IQ10_LEDGER_LAWS_STAFF showed the Staff's Repeal note
        naming the gold it saves, not the order it takes away. One phrase
        (`reforms.STAFF_LOSS`) for the chip, the repeal's answer and the
        lapse's line."""
        world.nation_gold["France"] = 60000
        _enact(world, "France", STAFF_ID)
        staff = R.find_law(world, "France", STAFF_ID)
        row = next(r for r in R.laws_payload(world, "France")["rows"] if r["id"] == STAFF_ID)
        assert R.STAFF_LOSS in row["chip"]["note"]
        client = TestClient(M.app)
        with _quiet():
            answer = client.post("/command", json={"command": "repeal the Staff"}).json()
        assert not R.is_in_force(staff), answer.get("message")
        assert R.staff_loss_sentence(staff).strip() in answer["message"]
        # the lapse's line says it too
        world.nation_gold["France"] = 60000
        _enact(world, "France", STAFF_ID)
        world.nation_gold["France"] = -500
        with _quiet():
            events = R.process_law_lapses(world)
        lapse = next(e for e in events if e.get("law") == STAFF_ID)
        assert R.staff_loss_sentence(staff).strip() in str(lapse.get("message"))

    def test_the_frames_are_committed_at_both_scales(self):
        audits = ROOT / "docs" / "audits"
        for name in ("LEDGER_BOOT_LAWS", "LEDGER_LAWS_STAFF", "LEDGER_LAWS_FORECAST",
                     "DIPLO_LAWS_RIVAL_NATIONS"):
            for suffix in ("", "_X2"):
                assert (audits / f"IQ10_{name}{suffix}_2026_09_27.png").exists(), name + suffix


# ═══════════════════════════ T7 — THE ARREARS, ONE PRICE ═════════════════════

@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield M.world
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


def _enact(world, nation, *law_ids):
    for law_id in law_ids:
        R.enact_law(world, nation, R.find_law(world, nation, law_id))


class TestT7TheArrears:

    def test_a_lapsed_staff_restores_at_one_price_everywhere(self, world):
        """The REAL lapse loop takes the Staff; solvency returns; three
        turns dead: half its price and three turns' upkeep — quoted the same
        on the LAWS tab and by the Council, and charged exactly that."""
        world.nation_gold["France"] = 60000
        _enact(world, "France", STAFF_ID, "anticipated_class", "code_abroad")
        world.nation_gold["France"] = -200
        with _quiet():
            R.process_law_lapses(world)
        staff = R.find_law(world, "France", STAFF_ID)
        assert staff.get("lapsed_turn") == int(world.current_turn)
        assert R.is_in_force(R.find_law(world, "France", "anticipated_class"))
        world.current_turn += 2                          # three turns dead
        world.nation_gold["France"] = 20000              # solvency returns
        quote = R.restoration_price(world, "France", staff)
        assert (quote["price"], quote["arrears"]) == (4500, 900)
        assert (quote["turns_dead"], quote["disperses_after"]) == (3, 7)
        row = next(r for r in R.laws_payload(world, "France")["rows"] if r["id"] == STAFF_ID)
        # the tab's row reads the SAME quote: the status names the lapse and
        # the Arrears window it prices (the RF-4c sweep found the chip alone
        # pinned — a row that forgot the lapse still passed)
        assert row["status"] == "lapsed"
        assert row["status_line"] == (
            f"Lapsed on turn {int(staff['lapsed_turn'])}. It restores at its Arrears "
            f"price for 7 more turns; then it costs its full price.")
        assert row["chip"]["label"] == "Restore"
        assert row["chip"]["note"].startswith("4,500 gold + 900 gold in arrears now")
        client = TestClient(M.app)
        with _quiet():
            r = client.post("/command", json={"command": "enact the Staff"}).json()
        assert "4,500 gold + 900 gold in arrears now" in r["message"], r["message"]
        with _quiet():
            client.post("/command", json={"command": "yes"}).json()
        assert R.is_in_force(staff)
        assert world.nation_gold["France"] == 20000 - 4500 - 900

    def test_the_ai_rung_prices_the_same_restoration(self, world, monkeypatch):
        import backend.game_logic.ledger as L
        monkeypatch.setattr(L, "_build_economy", lambda w, n, income_data=None: {"net": 5000})
        staff = R.find_law(world, "Austria", "corps_d_armee")
        staff["lapsed_turn"] = int(world.current_turn) - 2      # three turns dead
        quote = R.restoration_price(world, "Austria", staff)
        assert (quote["price"], quote["arrears"]) == (4500, 900)
        world.nation_authority["Austria"] = 60
        bar = 4500 + 900 + R.AI_PURSE_RESERVE + R.AI_PURSE_UPKEEP_TURNS * 300
        assert "under the bar" in R.ai_purse_refusal(world, "Austria", staff, bar - 1)
        assert R.ai_purse_refusal(world, "Austria", staff, bar) == ""


# ═══════════════════════════ THE FIFTH ACTION ON THE HEADER ═══════════════════

class TestTheFifthActionOnTheHeader:
    """§8a's row names "the top bar's action count (`top_bar.gd`)" and asks
    that the top bar's compact mode still show it. The top bar carries NO
    action count: the count is the command terminal's header ("Actions:
    N/M", `main.tscn` ActionsDisplay), written by `main.gd` `_update_status`
    from the wire's `action_summary.max_actions` — so no compact mode can
    hide it. RF-4c corrects the surface's name and pins the wire it reads."""

    def test_the_wire_carries_the_fifth_action_from_the_refill(self, world):
        world.nation_gold["France"] = 60000
        client = TestClient(M.app)
        with _quiet():
            enacted = client.post("/command",
                                  json={"command": "enact the Staff confirmed"}).json()
        assert R.is_in_force(R.find_law(world, "France", STAFF_ID)), enacted.get("message")
        summary = enacted.get("action_summary") or {}
        assert int(summary["max_actions"]) == 4, "not on the turn of enactment (§2.1)"
        with _quiet():
            after = client.post("/command", json={"command": "end turn"}).json()
        summary = after.get("action_summary") or {}
        assert (int(summary["actions_remaining"]), int(summary["max_actions"])) == (5, 5)

    def test_the_header_prints_the_wires_count_and_the_top_bar_has_none(self):
        body = _func_body((SCRIPTS / "main.gd").read_text(encoding="utf-8"), "_update_status")
        assert "max_actions = int(action_summary.max_actions)" in body
        assert 'actions_value.text = str(int(actions_remaining)) + "/" + str(int(max_actions))' in body
        assert "max_actions" not in (SCRIPTS / "top_bar.gd").read_text(encoding="utf-8")


# ═══════════════════════════ T8 — NOTHING UNNAMED ═════════════════════════════

class TestT8NothingUnnamed:
    """The doctrines' T10 idiom (`DOCTRINES_SPEC.md` §6): over a campaign,
    every law effect the player can see is compared with the surface that
    names it. France holds the Staff, the Anticipated Class, the Artillery
    Reserve and the Code Abroad from turn 1; the rival courts enact on their
    own (RF-3) — Britain's AI enacts the Orders in Council during the first
    end turn, so its blockade law bites France's trade from turn 2 and is
    checked on France's treasury line; the board runs ten turns. Pass: 0
    unnamed, and every kind SEEN."""

    def test_every_visible_law_effect_is_named(self, world):
        from backend.game_logic import naval as NV
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        world.nation_gold["France"] = 60000
        _enact(world, "France", STAFF_ID, "anticipated_class", "artillery_reserve",
               "code_abroad")
        client = TestClient(M.app)      # the player's own road: the dispatch
        seen, unnamed = [], []           # is built by the end-turn command

        def check(kind, law, surface):
            seen.append(kind)
            if law not in surface:
                unnamed.append((int(world.current_turn), kind, law))

        for _turn in range(10):
            with _quiet():
                r = client.post("/command", json={"command": "end turn"}).json()
                ledger = build_strategic_ledger(world)
                diplo = build_diplomatic_ledger(world)
            dispatch = r.get("morning_dispatch") or {}
            situation = dispatch.get("situation") or {}
            # the fifth action, at its first refill
            if R.staff_arrival(world, "France"):
                check("actions", "The Grand Quartier Général", str(situation.get("staff_arrived")))
            # the regen and the draft price, where the Manpower tab shows them
            for law, _v in R.manpower_regen_terms(world, "France", "infantry"):
                check("manpower_regen", law, json.dumps(ledger["manpower"]["infantry"]["regen_terms"],
                                                        ensure_ascii=False))
            for law, _v in R.recruit_price_terms(world, "France", "artillery"):
                check("recruit_price", law, json.dumps(ledger["manpower"]["artillery"]["price_terms"],
                                                       ensure_ascii=False))
            # the clients' loyalty term, on every client card
            rows = (diplo.get("vassals") or {})
            rows = rows.get("rows") if isinstance(rows, dict) else rows
            for row in rows or []:
                for law, _v in R.satellite_loyalty_terms(world, "France"):
                    check("satellite_loyalty", law, json.dumps(row.get("law_terms"),
                                                               ensure_ascii=False))
            # a rival's blockade law, on France's own treasury line
            if NV.blockade_denial_factor_against(world, "France") != 1.0:
                blockader, _c = NV.blockader_against(world, "France")
                for law, _v in R.blockade_denial_terms(world, blockader):
                    check("blockade_denial", law, str(ledger["economy"].get("blockade_note", "")))
        assert unnamed == [], unnamed
        # the census must have SEEN the effects it claims to check
        for kind in ("actions", "manpower_regen", "recruit_price", "satellite_loyalty",
                     "blockade_denial"):
            assert kind in seen, (kind, sorted(set(seen)))
