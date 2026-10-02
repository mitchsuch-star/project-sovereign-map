"""SR-5r RF-4a — "The LAWS tab" (`docs/REFORMS_SPEC.md` §8, §8a; §12 RF-4a).

The Strategic Ledger's eighth book: one row per law in the player's deck —
what it does (in numbers), what it costs (now and a turn), its status — and
ONE chip per row whose enabled state IS the predicate the verb calls
(`reforms.law_refusal` / `repeal_refusal`), whose reason is that predicate's
own words, and whose command is the typed order (the CN-3 idiom).

The enactment confirm (§8a): the executor's quote-then-confirm on the EXISTING
command_clarification channel (the Admiralty's idiom; no new modal type) —
the terms first, free; `yes` (or a typed "… confirmed") enacts; `no` withdraws,
free. The authority is priced aloud by ONE line (`reforms.authority_line`)
that the chip, the confirm and the verb's own result all read — and that line
reads the marshals' calm STRICTLY above 70, as the engine does (RF-1's note
said nothing when a political act took the Emperor to exactly 70). An AI court
is never quoted (GR5 — its rung already priced the act).

The client: the eighth tab button, KEY_8 under the digit-belongs-to-the-caret
rule, `_render_laws_tab`, and a clarification answer that refreshes the open
ledger beneath the modal (the Admiralty's Diversion confirm had the same gap).
"""
import contextlib
import io
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.game_logic import naval as NV
from backend.game_logic import reforms as R
from backend.game_logic.ledger import build_strategic_ledger
from tests import _chip_census as C

ROOT = Path(__file__).resolve().parents[1]
GD = ROOT / "godot-client" / "project-sovereign" / "scripts" / "strategic_ledger.gd"
TSCN = ROOT / "godot-client" / "project-sovereign" / "scenes" / "strategic_ledger.tscn"
MAIN_GD = ROOT / "godot-client" / "project-sovereign" / "scripts" / "main.gd"
STAFF_ID = "grand_quartier_general"
STAFF_NAME = "the Grand Quartier Général"


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


def payload(world):
    return R.laws_payload(world, "France")


def row_of(world, law_id):
    return next(r for r in payload(world)["rows"] if r["id"] == law_id)


def _gd(path):
    return path.read_text(encoding="utf-8")


def _func_body(src, name):
    head = src.split(f"func {name}(", 1)[1]
    return head.split("\nfunc ", 1)[0]


# ═══════════════════════════ the authority, priced aloud ══════════════════════

class TestTheAuthorityLine:

    def test_the_spec_example(self):
        assert R.authority_line(100, 85) == \
            "Authority 100 → 85 — the marshals' calm holds above 70."

    def test_the_calm_is_lost_at_exactly_seventy(self):
        """The engine reads the calm STRICTLY above 70 (`jealousy`: authority
        > AUTHORITY_SUPPRESS_ABOVE). RF-1's note tested `before >= 70 > after`
        and said nothing for 85 -> 70 — the Emperor's second political act."""
        from backend.game_logic.jealousy import AUTHORITY_SUPPRESS_ABOVE
        assert AUTHORITY_SUPPRESS_ABOVE == R.CALM_ABOVE == 70
        assert "the marshals' calm above 70 is lost" in R.authority_line(85, 70)
        assert "calm" not in R.authority_line(70, 55)   # 70 never held it

    def test_the_diplomatic_point(self):
        """An AI court boots at 60 — its first political act loses the point."""
        from backend.game_logic.diplomacy import calculate_dp
        assert calculate_dp(None, 60, True) - calculate_dp(None, 59, True) == 1
        assert "the extra diplomatic point is lost (it needs 60)" in R.authority_line(60, 45)
        assert R.authority_line(70, 65).endswith(
            "the extra diplomatic point holds (60 and above).")

    def test_the_floor(self):
        from backend.game_logic.diplomacy import calculate_dp
        assert calculate_dp(None, 30, True) - calculate_dp(None, 29, True) == 1
        assert "under 30 the court loses a diplomatic point a turn" in R.authority_line(40, 25)
        assert R.authority_line(45, 30).endswith("the court stays at 30 or above.")
        assert R.authority_line(25, 10).endswith("the court is already under 30.")

    def test_every_line_crossed_is_named(self):
        line = R.authority_line(75, 25)
        for words in ("calm above 70 is lost", "diplomatic point is lost",
                      "under 30 the court loses"):
            assert words in line, line

    def test_the_verbs_result_reads_the_same_line(self, world):
        world.authority_tracker.authority = 85
        with _quiet():
            result = M.executor._reforms._execute_enact_law(
                {"action": "enact_law", "target": "the Anticipated Class",
                 "confirmed": True}, {"world": world})
        assert result["success"] is True, result
        assert R.authority_line(85, 70) in result["message"]


# ═══════════════════════════ what each law does, in numbers ═══════════════════

class TestTheEffectLines:

    def test_every_authored_clause_renders(self, world):
        seen = 0
        for nation in R.GREAT_POWERS:
            for row in R.deck(world, nation):
                for clause in row.get("effects") or []:
                    line = R.effect_line(clause)
                    assert line, (nation, row["id"], clause)
                    seen += 1
        assert seen >= 25

    @pytest.mark.parametrize("clause, line", [
        ({"type": "actions", "value": 1}, "+1 order of the day, from the next refill"),
        ({"type": "recruit_price", "arm": "artillery", "value": 0.85},
         "artillery levies cost 15% less (×0.85)"),
        ({"type": "recruit_price", "arm": "all", "value": 0.9},
         "every levy costs 10% less (×0.9)"),
        ({"type": "recruit_morale", "arm": "infantry", "value": -10},
         "infantry drafts muster at -10 morale"),
        ({"type": "recruit_morale", "arm": "infantry", "value": 10},
         "infantry drafts muster at +10 morale"),
        ({"type": "drill_morale", "value": 5}, "+5 morale from every drill"),
        ({"type": "manpower_regen", "pool": "infantry", "value": 25},
         "infantry manpower returns 25% faster"),
        ({"type": "supply_capacity", "value": 1.25},
         "fed provinces feed 25% more men (×1.25)"),
        ({"type": "satellite_loyalty", "value": 1}, "+1 loyalty a turn in every client"),
        ({"type": "cs_closure", "rule": "every_client"},
         "every client shuts its ports to Britain at war, whatever its autonomy"),
    ])
    def test_each_type_in_numbers(self, clause, line):
        assert R.effect_line(clause) == line

    def test_the_blockade_line_and_the_board_share_one_figure(self):
        assert NV.blockade_cut_percent(1.0) == 50
        assert NV.blockade_cut_percent(1.25) == 62
        assert "by 62%, not half" in R.effect_line({"type": "blockade_denial", "value": 1.25})
        body = NV.blockade_trade_words.__code__.co_names
        assert "blockade_cut_percent" in body

    def test_an_unwired_clause_renders_nothing(self):
        assert R.effect_line({"type": "cures", "flaw": "x"}) == ""
        assert R.effect_line(None) == ""


# ═══════════════════════════ the tab's rows ═══════════════════════════════════

class TestThePayload:

    def test_one_row_per_law_in_deck_order(self, world):
        ids = [r["id"] for r in payload(world)["rows"]]
        assert ids == [r["id"] for r in R.deck(world, "France")]
        assert ids[0] == STAFF_ID

    def test_each_row_says_what_it_does_and_costs(self, world):
        staff = row_of(world, STAFF_ID)
        assert staff["name"] == "The Grand Quartier Général"
        assert staff["date"].startswith("Berthier's")
        assert staff["says"].startswith("Berthier's headquarters")
        assert staff["effects"] == ["+1 order of the day, from the next refill"]
        assert (staff["price"], staff["currency"], staff["upkeep"]) == (9000, "gold", 300)
        assert staff["price_words"] == "9,000 gold"
        assert staff["is_staff"] is True

    @pytest.mark.parametrize("gold, admin", [(800, 2), (60000, 2), (60000, 0)])
    def test_the_chip_is_the_predicate(self, world, gold, admin):
        """Honest availability, drift-pinned: every Enact chip's state IS
        `law_refusal`, and a refused chip carries its words verbatim."""
        world.nation_gold["France"] = gold
        world.admin_actions_remaining = admin
        for row in payload(world)["rows"]:
            refusal = R.law_refusal(world, "France", row["id"])
            chip = row["chip"]
            assert chip["enabled"] is (refusal == ""), (row["id"], refusal)
            if refusal:
                assert chip["reason"] == refusal
                assert row["status"] == "refused" and row["status_line"] == refusal
            else:
                assert chip["note"] == R.terms_line(world, "France", R.find_law(world, "France", row["id"]))
                assert row["status"] == "available"

    def test_the_chip_command_is_the_typed_order(self, world):
        for row in payload(world)["rows"]:
            command = row["chip"]["command"]
            assert command.startswith("enact ")
            with _quiet():
                parsed = M.parser.parse(command, M.get_llm_game_state(), world=world)
            assert parsed["command"]["action"] == "enact_law", command
            law = R.resolve_law(world, "France", parsed["command"]["target"])
            assert law is not None and law["id"] == row["id"], command

    def test_a_gold_law_prices_now_and_a_turn(self, world):
        world.nation_gold["France"] = 60000
        assert row_of(world, STAFF_ID)["chip"]["note"] == (
            "9,000 gold now, then 300 gold a turn; one more order each day "
            "from the next refill")

    def test_an_authority_law_is_priced_aloud(self, world):
        world.nation_gold["France"] = 60000
        world.authority_tracker.authority = 100
        note = row_of(world, "anticipated_class")["chip"]["note"]
        assert note == ("15 authority now, then 150 gold a turn. "
                        + R.authority_line(100, 85).rstrip("."))

    def test_a_law_in_force_offers_repeal(self, world):
        world.nation_gold["France"] = 60000
        R.enact_law(world, "France", R.find_law(world, "France", STAFF_ID))
        staff = row_of(world, STAFF_ID)
        assert staff["status"] == "in_force"
        assert staff["status_line"] == f"In force since turn {int(world.current_turn)}."
        chip = staff["chip"]
        assert (chip["label"], chip["command"]) == ("Repeal", f"repeal {STAFF_NAME}")
        refusal = R.repeal_refusal(world, "France", STAFF_ID)
        assert chip["enabled"] is (refusal == "")
        world.admin_actions_remaining = 0
        refusal = R.repeal_refusal(world, "France", STAFF_ID)
        assert refusal
        chip = row_of(world, STAFF_ID)["chip"]
        assert chip["enabled"] is False and chip["reason"] == refusal

    def test_the_repeal_chip_states_what_is_lost(self, world):
        # Re-seated consciously at RF-4c (Sept 27, 2026): the Staff's note now
        # names the order it takes away (`reforms.STAFF_LOSS`) — a repeal is
        # not confirmed, so this note is its only preview. Any other law's
        # note is unchanged.
        world.nation_gold["France"] = 60000
        R.enact_law(world, "France", R.find_law(world, "France", STAFF_ID))
        assert row_of(world, STAFF_ID)["chip"]["note"] == (
            "ends 300 gold a turn — its extra order of the day goes with it at "
            "the next refill; nothing is refunded, and enacting it again costs "
            "the full 9,000 gold")
        R.enact_law(world, "France", R.find_law(world, "France", "anticipated_class"))
        assert row_of(world, "anticipated_class")["chip"]["note"] == (
            "ends 150 gold a turn; nothing is refunded, and enacting it again "
            "costs the full 15 authority")

    def test_a_lapsed_law_offers_its_arrears(self, world):
        world.nation_gold["France"] = 60000
        R.find_law(world, "France", STAFF_ID)["lapsed_turn"] = int(world.current_turn) - 1
        staff = row_of(world, STAFF_ID)
        assert staff["status"] == "lapsed"
        assert "restores at its Arrears price for 8 more turns" in staff["status_line"]
        assert staff["chip"]["label"] == "Restore"
        assert staff["chip"]["note"].startswith("4,500 gold + 600 gold in arrears now")

    def test_a_dispersed_law_costs_its_full_price(self, world):
        world.nation_gold["France"] = 60000
        R.find_law(world, "France", STAFF_ID)["lapsed_turn"] = int(world.current_turn) - 20
        staff = row_of(world, STAFF_ID)
        assert staff["status"] == "dispersed"
        assert staff["chip"]["label"] == "Enact"
        assert staff["chip"]["note"].startswith("9,000 gold now")

    def test_the_footer_counts_the_slate(self, world):
        world.nation_gold["France"] = 60000
        assert payload(world)["footer"] == "No law is in force."
        R.enact_law(world, "France", R.find_law(world, "France", STAFF_ID))
        R.enact_law(world, "France", R.find_law(world, "France", "anticipated_class"))
        body = payload(world)
        assert body["upkeep_total"] == 450 == R.law_upkeep_bill(world, "France")
        assert body["footer"] == "The laws in force cost 450 gold a turn."

    def test_the_ledger_carries_the_tab(self, world):
        with _quiet():
            ledger = build_strategic_ledger(world)
        assert ledger["laws"] == payload(world)

    def test_a_deckless_world_has_no_tab(self, world):
        world.reforms = {}
        assert R.laws_payload(world, "France") is None
        with _quiet():
            ledger = build_strategic_ledger(world)
        assert "laws" not in ledger


# ═══════════════════════════ the enactment confirm ════════════════════════════

class TestTheConfirm:

    def test_an_enactment_is_quoted_first_and_free(self, world, client):
        world.nation_gold["France"] = 12000
        admin, military = world.admin_actions_remaining, world.actions_remaining
        r = post(client, "enact the Staff")
        assert r.get("law_confirm") is True and r.get("state") == "awaiting_clarification", r
        assert r["options"][0]["command"] == f"enact {STAFF_NAME} confirmed"
        assert r["options"][1]["command"] == "cancel"
        assert not R.is_in_force(R.find_law(world, "France", STAFF_ID))
        assert world.nation_gold["France"] == 12000
        assert (world.admin_actions_remaining, world.actions_remaining) == (admin, military)

    def test_the_quote_states_the_terms(self, world, client):
        world.nation_gold["France"] = 12000
        message = post(client, "enact the Staff")["message"]
        assert "9,000 gold now, then 300 gold a turn" in message
        assert "one more order each day from the next refill" in message
        assert "The treasury holds 12,000 gold" in message
        assert "(Berthier's Imperial Headquarters, expanded 1805–07)" in message
        assert message.endswith("Enact it? (yes / no)")

    def test_an_authority_law_is_priced_aloud_before_the_spend(self, world, client):
        world.authority_tracker.authority = 100
        message = post(client, "enact the Anticipated Class")["message"]
        assert R.authority_line(100, 85) in message
        assert world.authority_tracker.authority == 100

    def test_yes_enacts(self, world, client):
        world.nation_gold["France"] = 12000
        admin = world.admin_actions_remaining
        post(client, "enact the Staff")
        r = post(client, "yes")
        assert r.get("success") is True, r
        assert R.is_in_force(R.find_law(world, "France", STAFF_ID))
        assert world.nation_gold["France"] == 3000
        assert world.admin_actions_remaining == admin - 1

    def test_no_withdraws_free(self, world, client):
        world.nation_gold["France"] = 12000
        admin = world.admin_actions_remaining
        post(client, "enact the Staff")
        r = post(client, "no")
        assert "withdrawn" in r.get("message", ""), r
        assert not R.is_in_force(R.find_law(world, "France", STAFF_ID))
        assert world.nation_gold["France"] == 12000
        assert world.admin_actions_remaining == admin

    def test_the_typed_confirm_enacts_at_once(self, world, client):
        world.nation_gold["France"] = 12000
        r = post(client, "enact the Staff confirmed")
        assert r.get("success") is True and not r.get("law_confirm"), r
        assert R.is_in_force(R.find_law(world, "France", STAFF_ID))

    def test_a_restoration_is_quoted_as_a_restoration(self, world, client):
        world.nation_gold["France"] = 12000
        R.find_law(world, "France", STAFF_ID)["lapsed_turn"] = int(world.current_turn) - 1
        r = post(client, "enact the Staff")
        assert r["options"][0]["label"] == f"Restore {STAFF_NAME}"
        assert "4,500 gold + 600 gold in arrears now" in r["message"]
        assert r["message"].endswith("Restore it? (yes / no)")

    def test_a_refusal_is_never_quoted(self, world, client):
        world.nation_gold["France"] = 800
        r = post(client, "enact the Staff")
        assert not r.get("law_confirm"), r
        assert r["message"] == R.law_refusal(world, "France", STAFF_ID)

    def test_the_ai_is_never_quoted(self, world):
        world.nation_gold["Austria"] = 60000
        with _quiet():
            result = M.executor.execute(
                {"command": {"action": "enact_law", "target": "the Landwehr",
                             "_acting_nation": "Austria", "type": "specific"}},
                M.game_state)
        assert result.get("success") is True and not result.get("law_confirm"), result
        assert R.is_in_force(R.find_law(world, "Austria", "landwehr"))

    def test_a_marker_left_in_the_target_is_read_not_named(self, world):
        """A live-model parse may keep the words as typed: the executor reads
        the marker and never looks for a law called 'the Staff confirmed'."""
        world.nation_gold["France"] = 12000
        with _quiet():
            result = M.executor._reforms._execute_enact_law(
                {"action": "enact_law", "target": "the Staff confirmed"},
                M.game_state)
        assert result.get("success") is True and not result.get("law_confirm"), result
        assert R.is_in_force(R.find_law(world, "France", STAFF_ID))

    @pytest.mark.parametrize("words", ["enact the Staff", "enact the Anticipated Class"])
    def test_the_quote_reads_as_sentences(self, world, client, words):
        world.nation_gold["France"] = 12000
        message = post(client, words)["message"]
        assert ".." not in message and " ." not in message, message

    def test_the_parser_strips_the_marker(self, world):
        with _quiet():
            parsed = M.parser.parse("enact the Staff confirmed", M.get_llm_game_state(),
                                    world=world)
        assert parsed["command"]["action"] == "enact_law"
        assert parsed["command"]["target"] == "the Staff"


# ═══════════════════════════ the client ═══════════════════════════════════════

class TestTheClient:

    def test_the_tab_button_exists(self):
        src = _gd(TSCN)
        assert re.search(r'\[node name="LawsTab" type="Button" parent="PanelContainer/VBoxContainer/SubTabRow"\]', src)
        block = src.split('[node name="LawsTab"', 1)[1].split("[node", 1)[0]
        assert 'text = "LAWS"' in block

    def test_the_tab_is_the_eighth_book(self):
        src = _gd(GD)
        assert "@onready var laws_tab = $PanelContainer/VBoxContainer/SubTabRow/LawsTab" in src
        assert re.search(r"tab_buttons = \[forces_tab, territories_tab, economy_tab, intel_tab, "
                         r"manpower_tab, orders_tab, admiralty_tab, laws_tab\]", src)

    def test_key_eight_opens_the_laws_tab(self):
        body = _func_body(_gd(GD), "_input")
        assert re.search(r"KEY_8:\s*\n\s*_switch_tab\(7\)", body)

    def test_the_digit_belongs_to_the_caret(self):
        body = _func_body(_gd(GD), "_input")
        guard = body.index("if _focused is LineEdit or _focused is TextEdit:")
        assert guard < body.index("KEY_8:")

    def test_the_laws_book_is_rendered(self):
        body = _func_body(_gd(GD), "_render_current_tab")
        assert re.search(r"7:\s*\n\s*_render_laws_tab\(\)", body)
        laws = _func_body(_gd(GD), "_render_laws_tab")
        for key in ('"laws"', '"rows"', '"says"', '"effects"', '"status_line"',
                    '"footer"', "_chip_row(", '"chip"'):
            assert key in laws, key

    def test_a_clarification_answer_refreshes_the_open_ledger(self):
        src = _gd(MAIN_GD)
        body = _func_body(src, "_on_clarification_command")
        assert "_on_clarification_command_result" in body
        result = _func_body(src, "_on_clarification_command_result")
        assert "_on_command_result(response)" in result
        assert "_refresh_open_info_screens()" in result
        refresh = _func_body(src, "_refresh_open_info_screens")
        assert '"ledger"' in refresh
