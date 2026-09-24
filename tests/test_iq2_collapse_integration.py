"""IQ-2 "The Collapse Is Legible" — the integration seams (Sept 14, 2026).

The five builder files each pin their own surface family. This file pins the
seams BETWEEN them that the integration pass closed — the places where one
builder's new key had no reader, or a defect sat in a file no builder owned:

- the coalition-dissolved chronicle line reads the `courts_at_war` stamp
  coalition.py now writes (the league lapses on low threat and ends no war);
- the war room's context keeps `threat_level` an int when a design is in
  check (the designs loop re-bound the SAME name to a nation key — GR2);
- the prisoner status note names the captor's court, not its raw key (R7);
- a field-battle / charge conquest stamps `captured_from`, so the
  enemy-phase dialog can read a French province lost in battle as a loss;
- the client reads the ledger's closed-depot flag and the Balance tab's
  collapse keys (source census, scoped to code lines);
- an order addressed to the captured Emperor is refused BY NAME on the
  typed path (the census's "cannot reach Paris from Vienna" was measured
  by driving the executor directly, below the /command guard).
"""

import ast
import contextlib
import io
import random
from pathlib import Path

import pytest

from backend.campaign_log import format_event_oneliner
from backend.models.world_state import WorldState

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = str(ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json")
SCRIPTS = ROOT / "godot-client" / "project-sovereign" / "scripts"


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCENARIO)


def _code_lines(path: Path) -> str:
    """The .gd source minus full-line comments (a '#' inside a string such
    as '[color=#' survives — lines are never split on '#')."""
    return "\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                     if not line.lstrip().startswith("#"))


# ─────────────────────────────────────────────────────────────────────────
# The coalition-dissolved chronicle line
# ─────────────────────────────────────────────────────────────────────────

class TestTheLapsedLeagueInTheChronicle:
    def test_the_courts_still_at_war_are_named(self):
        line = format_event_oneliner({
            "type": "coalition_dissolved", "target_nation": "France",
            "courts_at_war": ["Austria", "Britain", "Russia"],
        })
        assert line == ("Coalition against France has dissolved — Austria, "
                        "Britain and Russia remain at war with us.")

    def test_one_court_takes_the_singular(self):
        line = format_event_oneliner({
            "type": "coalition_dissolved", "target_nation": "France",
            "courts_at_war": ["KingdomOfItaly"],
        })
        assert line.endswith("Kingdom of Italy remains at war with us.")

    def test_an_entry_without_the_stamp_is_byte_identical(self):
        for extra in ({}, {"courts_at_war": []}):
            line = format_event_oneliner({
                "type": "coalition_dissolved", "target_nation": "France", **extra})
            assert line == "Coalition against France has dissolved."

    def test_another_target_is_untouched(self):
        line = format_event_oneliner({
            "type": "coalition_dissolved", "target_nation": "Austria",
            "courts_at_war": ["Russia"],
        })
        assert line == "Coalition against Austria has dissolved."


# ─────────────────────────────────────────────────────────────────────────
# GR2: the war room's alarm stays an int
# ─────────────────────────────────────────────────────────────────────────

class TestTheWarRoomAlarmStaysAnInt:
    def test_threat_is_bound_once_in_the_assessment(self):
        """The designs-in-check loop used to assign `threat` — the name of
        the int alarm read at the top of `_assess_situation` — so the
        context's `threat_level` left for Godot as a nation key whenever a
        design was in check. One binding, and it is the int."""
        import backend.game_logic.diplomatic_advisory as adv
        tree = ast.parse(Path(adv.__file__).read_text(encoding="utf-8"))
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_assess_situation")
        bindings = [n for n in ast.walk(fn)
                    if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign))
                    for t in (n.targets if isinstance(n, ast.Assign) else [n.target])
                    if isinstance(t, ast.Name) and t.id == "threat"]
        assert len(bindings) == 1
        assert "int(" in ast.unparse(bindings[0].value)


# ─────────────────────────────────────────────────────────────────────────
# R7: the prisoner note names the court
# ─────────────────────────────────────────────────────────────────────────

def _card(world, name):
    from backend.game_logic.marshal_overview import build_marshal_overview
    data = build_marshal_overview(world)
    cards = data if isinstance(data, list) else data.get("marshals", [])
    return next(c for c in cards if c.get("name") == name)


class TestThePrisonerNoteNamesTheCourt:
    def test_a_camel_case_captor_is_humanized(self):
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w.capture_marshal(w.marshals["Ney"], "KingdomOfItaly")
        note = _card(w, "Ney")["status_note"]
        assert "Kingdom of Italy" in note and "KingdomOfItaly" not in note

    def test_lever_down_restores_the_raw_key(self, monkeypatch):
        import backend.game_logic.marshal_overview as mo
        monkeypatch.setattr(mo, "THE_PRISONER_NOTE_NAMES_THE_COURT", False)
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w.capture_marshal(w.marshals["Ney"], "KingdomOfItaly")
        assert "KingdomOfItaly" in _card(w, "Ney")["status_note"]

    def test_a_plain_captor_keeps_the_w6_7_wording(self):
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w.capture_marshal(w.marshals["Ney"], "Austria")
        assert _card(w, "Ney")["status_note"].startswith("PRISONER of Austria since T")


# ─────────────────────────────────────────────────────────────────────────
# The field-battle conquest names whom it was taken from
# ─────────────────────────────────────────────────────────────────────────

def _battle_the_frontier():
    """Mack, massively reinforced, attacks a token French corps on an
    ungarrisoned French province next to Swabia. Returns (world, result)."""
    from backend.commands.executor import CommandExecutor
    w = _boot()
    mack = w.marshals["Mack"]
    frontier = next(
        r for r in (w.regions[mack.location].adjacent_regions or [])
        if w.regions[r].controller == "France" and not w.regions[r].is_capital)
    # Every other French corps goes to the farthest French province — at
    # boot the Emperor stands one march away at Lorraine and marches to the
    # guns, so the defenders would hold the field and nothing would transfer.
    far = max((n for n, r in w.regions.items() if r.controller == "France"),
              key=lambda n: (w.get_distance(frontier, n), n))
    for m in w.marshals.values():
        if m.nation == "France" and m.name != "Ney":
            m.location = far
    victim = w.marshals["Ney"]
    victim.location = frontier
    # Measured: casualties scale to the defender, so a 300-man corps loses
    # 141 and still stands (no transfer); at 60 or fewer he is destroyed and
    # the province changes hands on every seed probed.
    victim.strength = 40
    region = w.regions[frontier]
    for attr in ("garrison", "garrison_detachment", "garrison_strength"):
        if hasattr(region, attr):
            setattr(region, attr, 0)
    region.fortification = 0 if hasattr(region, "fortification") else None
    mack.strength = 150000
    w.invalidate_active_nations_cache()
    random.seed(7)
    with contextlib.redirect_stdout(io.StringIO()):
        result = CommandExecutor().execute(
            {"success": True, "command": {"marshal": "Mack", "action": "attack",
                                          "target": "Ney"}},
            {"world": w})
    return w, frontier, result


class TestTheConquestNamesWhomItWasTakenFrom:
    def test_the_battle_event_stamps_captured_from(self):
        w, frontier, result = _battle_the_frontier()
        battle = next((e for e in result.get("events") or []
                       if e.get("type") == "battle"), None)
        # A skip here would be an inert pin — the fixture is tuned to conquer.
        assert battle is not None and battle.get("region_conquered") is True
        assert w.regions[frontier].controller == "Austria"
        assert battle.get("captured_from") == "France"

    def test_both_conquest_producers_carry_the_stamp(self):
        """Structural half: the attack's battle event and the charge event
        both read the holder captured BEFORE `_attempt_region_capture`."""
        src = (ROOT / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        assert '"captured_from": conquest_from' in src
        assert 'charge_event["captured_from"] = charge_conquest_from' in src
        attack_set = src.index("conquest_from = target_region.controller")
        assert attack_set < src.index("marshal, target_location, world, game_state, had_garrison=True)",
                                      attack_set)
        charge_set = src.index("charge_conquest_from = target_region.controller")
        assert charge_set < src.index("marshal, charge_battle_region, world, game_state, had_garrison=True",
                                      charge_set)


# ─────────────────────────────────────────────────────────────────────────
# The client reads the keys the integration added
# ─────────────────────────────────────────────────────────────────────────

class TestTheClientReadsTheIntegrationKeys:
    def test_the_manpower_tab_quotes_no_price_at_a_closed_depot(self):
        code = _code_lines(SCRIPTS / "strategic_ledger.gd")
        assert 'pool.get("depot_closed", false)' in code
        # The old priced line survives as the fallback.
        assert '" troops for " + str(recruit_cost) + "g"' in code

    def test_the_balance_tab_reads_the_collapse_keys(self):
        code = _code_lines(SCRIPTS / "diplomatic_ledger.gd")
        assert 'projection.get("collapse_line", "")' in code
        assert 'boe.get("headline_note", "")' in code
        # The projection line survives as the elif arm.
        assert "Next war of conquest: " in code

    def test_the_backend_keys_the_client_reads_exist(self):
        """Producer→renderer join: the two Balance keys and the depot flag
        ride their payloads under the collapse (and only then)."""
        import backend.game_logic.diplomatic_ledger as dl
        import backend.game_logic.ledger as lg
        dl_src = Path(dl.__file__).read_text(encoding="utf-8")
        lg_src = Path(lg.__file__).read_text(encoding="utf-8")
        assert 'threat_projection["collapse_line"]' in dl_src
        assert 'result["headline_note"]' in dl_src
        assert '"depot_closed"' in lg_src


# ─────────────────────────────────────────────────────────────────────────
# The captured Emperor is refused by name on the typed path
# ─────────────────────────────────────────────────────────────────────────

class TestTheCaptiveEmperorIsRefusedByName:
    def test_an_order_to_the_captive_emperor_names_his_captor(self, monkeypatch):
        from fastapi.testclient import TestClient
        import backend.main as M
        from backend.commands.parser import CommandParser
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w.capture_marshal(w.marshals["Napoleon"], "Austria")
            parser = CommandParser(use_real_llm=False)
        monkeypatch.setattr(M, "parser", parser)
        monkeypatch.setattr(M, "world", w)
        monkeypatch.setattr(M, "game_state", {"world": w})
        with contextlib.redirect_stdout(io.StringIO()):
            d = TestClient(M.app).post(
                "/command", json={"command": "Napoleon, attack Mack"}).json()
        msg = str(d.get("message", ""))
        assert "prisoner" in msg.lower() and "Austria" in msg
        assert "cannot reach" not in msg


# ─────────────────────────────────────────────────────────────────────────
# Review round (Sept 14, 2026)
# ─────────────────────────────────────────────────────────────────────────

def _collapsed(keep=("Brittany",)):
    w = _boot()
    for name, r in w.regions.items():
        if r.controller == "France" and name not in keep:
            r.controller = "Austria"
    w.invalidate_active_nations_cache()
    return w


class TestReviewRoundTheCollapseLineDoesNotRestateItsBeats:
    def test_the_capital_clause_yields_to_the_capital_lost_beat(self):
        import backend.game_logic.dispatch as D
        w = _collapsed(keep=())
        w.log_event({"type": "region_captured", "region": "Paris",
                     "captured_by": "Austria", "captured_from": "France"})
        h = D._build_headline(w, "France")
        assert h["class"] == "empire_reduced"
        assert "Paris is in Austria's hands" not in h["text"]
        assert any("Paris HAS FALLEN" in b for b in h["sub_beats"])

    def test_without_the_beat_the_capital_clause_stands(self):
        import backend.game_logic.dispatch as D
        h = D._build_headline(_collapsed(keep=()), "France")
        assert h["class"] == "empire_reduced"
        assert "Paris is in Austria's hands" in h["text"]

    def test_the_sovereign_clause_yields_to_the_emperor_taken_beat(self):
        import backend.game_logic.dispatch as D
        w = _collapsed(keep=())
        with contextlib.redirect_stdout(io.StringIO()):
            w.capture_marshal(w.marshals["Napoleon"], "Austria")
        h = D._build_headline(w, "France")
        assert h["class"] == "sovereign_captured"
        reduced = [b for b in h["sub_beats"] if "holds no province" in b]
        assert reduced, h
        assert "prisoner" not in reduced[0]


class TestReviewRoundBerthierPromisesNoTreasuryInDeficit:
    def _note(self, w):
        import backend.game_logic.dispatch as D
        return D._pick_berthier_note(w, "France", [], {}, headline_class="")

    def test_a_bankrupt_last_province_is_not_a_treasury(self):
        w = _collapsed()
        w.nation_gold["France"] = -500
        note = self._note(w)
        assert "already in deficit" in note
        assert "still has a treasury behind it" not in note

    def test_a_solvent_last_province_keeps_the_treasury_line(self):
        w = _collapsed()
        w.nation_gold["France"] = 5000
        w.nation_bankruptcy_turns["France"] = 0
        assert "still has a treasury behind it" in self._note(w)


class TestReviewRoundTheAutoChargeConquestIsLogged:
    def test_a_reckless_charge_that_takes_a_french_province_is_chronicled(self):
        """The one conquest that logged no `region_captured` row: an AI
        reckless cavalryman's turn-start charge. The row now carries the
        holdings stamp every other own-loss row carries."""
        w = _collapsed(keep=("Normandy", "Brittany"))
        mack = w.marshals["Mack"]
        mack.cavalry = True
        mack.personality = "aggressive"
        mack.recklessness = 5
        mack.location = "Paris"
        mack.strength = 60000
        for m in w.marshals.values():
            if m.nation == "France" and m.name != "Ney":
                m.location = "Brittany"
        ney = w.marshals["Ney"]
        ney.location = "Normandy"
        ney.strength = 40
        before = len(list(w.event_log))
        random.seed(7)
        with contextlib.redirect_stdout(io.StringIO()):
            w._process_reckless_cavalry_turn_start()
        assert w.regions["Normandy"].controller == "Austria"
        rows = [e for e in list(w.event_log)[before:]
                if e.get("type") == "region_captured" and e.get("region") == "Normandy"]
        assert len(rows) == 1
        assert rows[0]["captured_from"] == "France"
        assert rows[0]["method"] == "charge"
        assert rows[0]["holdings_left"] == 1
        assert format_event_oneliner(rows[0]).endswith(
            "— France holds a single province")


class TestReviewRoundASecondFallIsANewEdition:
    def test_the_realm_reduced_key_carries_the_turn(self):
        import backend.game_logic.gazette as G
        w = _collapsed()
        ev = {"type": "region_captured", "region": "Normandy",
              "captured_by": "Austria", "captured_from": "France",
              "holdings_left": 1, "turn": 11}

        def keys(e):
            return [c[2] for c in G._special_candidates(w, [e])
                    if c[1] == G.REALM_REDUCED_TO_ONE]

        assert keys(ev) == [f"{G.REALM_REDUCED_TO_ONE}|Normandy@11"]
        assert keys(dict(ev, turn=12)) == [f"{G.REALM_REDUCED_TO_ONE}|Normandy@12"]


class TestReviewRoundTheSnapshotNamesWhoseTerms:
    def test_a_collapsed_war_snapshot_carries_the_side(self):
        from backend.game_logic import war_status as WS
        from backend.game_logic.diplomacy import build_war_context_snapshot
        w = _collapsed(keep=())
        snap = build_war_context_snapshot(w, "France", "Austria", "peace")
        assert snap["settlement_tier_side"] == "theirs"
        assert snap["settlement_tier_side"] == WS._tier_side(int(snap["war_score"]))

    def test_the_legacy_snapshot_is_byte_identical(self):
        from backend.game_logic.diplomacy import build_war_context_snapshot
        legacy = WorldState(player_nation="France")
        snap = build_war_context_snapshot(legacy, "France", "Austria", "peace")
        assert "settlement_tier_side" not in snap

    def test_both_proposal_popups_read_the_side(self):
        for name in ("proposal_confirm_popup.gd", "incoming_proposal_popup.gd"):
            code = _code_lines(SCRIPTS / name)
            assert 'snapshot.get("settlement_tier_side", "")' in code, name
            assert "Settlement (theirs to impose): " in code, name
            # The old gold line survives as the fallback.
            assert 'bbcode += "Settlement: [color=#e0c070]%s[/color]\\n" % tier_display' in code, name


# ─────────────────────────────────────────────────────────────────────────
# Row IQ-2's own completion item (PR-X1), pinned at the merge with row IQ
# ─────────────────────────────────────────────────────────────────────────

def _defense_line(world, nation="Britain"):
    import backend.game_logic.dispatch as D
    return next(r["text"] for r in D._build_war_objective_section(world, "France")
                if r["target_nation"] == nation and "Defense" in r["text"])


class TestTheWarPurposeListsOnlyWhatIsHeld:
    """PR-X1: 'the war-purpose line lists twenty provinces France no longer
    holds' — a Defence purpose names what is HELD, or says the homeland is
    lost; it never advertises a lost province as an objective.

    ⚑ Consciously flipped by row EP F1 (LV-8, Sept 23, 2026): the homeland
    defence purpose is now ONE sentence ("the homeland — 1 of 28 provinces
    held" / "the homeland is lost"), which keeps PR-X1's rule by naming no
    province at all. These pins bind the LIST arms this lever governs, which
    the LV-8 lever-down arm restores — so they run there, and the sentence's
    PR-X1 guarantee is pinned in `test_the_sentence_names_nothing_lost`."""

    @pytest.fixture(autouse=True)
    def _the_list_shape(self, monkeypatch):
        from backend.game_logic import war_status as WS
        monkeypatch.setattr(WS, "THE_PURPOSE_IS_ONE_SENTENCE", False)

    def test_a_rump_names_only_what_it_holds(self):
        text = _defense_line(_collapsed(keep=("Brittany",)))
        named = text.split(" [", 1)[0]
        assert named.endswith("— holding Brittany"), text
        assert "Paris" not in named and "Normandy" not in named

    def test_a_fallen_realm_says_the_homeland_is_lost(self):
        text = _defense_line(_collapsed(keep=()))
        # The count belongs to WAR_PURPOSE_COUNTS_WHAT_IS_HELD, which speaks
        # only for a partial hold; at none held the bracket reads "not held".
        assert "— the homeland is lost [not held]" in text
        assert "Paris" not in text

    def test_lever_down_restores_the_full_list(self, monkeypatch):
        import backend.game_logic.dispatch as D
        monkeypatch.setattr(D, "WAR_PURPOSE_LISTS_ONLY_WHAT_IS_HELD", False)
        assert "Paris" in _defense_line(_collapsed(keep=("Brittany",))).split(" [", 1)[0]

    def test_a_standing_realm_keeps_its_full_list(self):
        text = _defense_line(_boot())
        assert "Paris" in text and "[HELD]" in text


class TestTheSentenceNamesNothingLost:
    """LV-8's sentence carries PR-X1's guarantee on the shipped arm."""

    def test_the_sentence_names_nothing_lost(self):
        rump = _defense_line(_collapsed(keep=("Brittany",)))
        assert "the homeland — 1 of 28 provinces held" in rump
        fallen = _defense_line(_collapsed(keep=()))
        assert "— the homeland is lost" in fallen
        for text in (rump, fallen):
            assert "Paris" not in text and "Normandy" not in text


class TestTheIQ2CompletionDefinition:
    """IQ-2 (STATUS ▶ NEXT UP): 'on a staged save at that turn, no producer
    claims a holding France does not hold, and the briefing's lead names the
    collapse.' Staged here as the measured state — France at ZERO provinces —
    and driven through one real `end turn` on the typed path."""

    def test_the_staged_collapse(self, monkeypatch):
        from fastapi.testclient import TestClient
        import backend.main as M
        from backend.commands.parser import CommandParser
        w = _collapsed(keep=())
        with contextlib.redirect_stdout(io.StringIO()):
            parser = CommandParser(use_real_llm=False)
        monkeypatch.setattr(M, "parser", parser)
        monkeypatch.setattr(M, "world", w)
        monkeypatch.setattr(M, "game_state", {"world": w})
        client = TestClient(M.app)
        with contextlib.redirect_stdout(io.StringIO()):
            client.post("/command", json={"command": "end turn"})
            ledger = client.get("/ledger").json()
        assert not w.get_player_regions(), "the staged board must stay landless"
        dispatch = w.last_morning_dispatch
        # The lead names the collapse (the Emperor's capture may outrank it,
        # in which case the collapse is the first sub-beat).
        head = dispatch["headline"]
        page = [head["text"]] + list(head.get("sub_beats") or [])
        assert any("holds no province of her own" in line for line in page[:2]), page
        # No producer claims a holding France does not hold.
        assert dispatch["situation"]["player_regions"] == 0
        for row in dispatch.get("war_objectives") or []:
            if "Defense" in row["text"]:
                assert "the homeland is lost" in row["text"], row["text"]
        assert not any("the depots hold" in line for line in page), page
        body = ledger.get("ledger") or ledger
        assert body.get("territories") in ([], None) or not body.get("territories")
        assert "holds no province of her own" in (body.get("collapse_note") or "")


# ─────────────────────────────────────────────────────────────────────────
# Review round (economy lens, pre-existing): the levy names its recipient's arm
# ─────────────────────────────────────────────────────────────────────────

def _levy_board(recipient_name):
    """A sandbox 1805 board with room under the ordinance and ONE strong
    corps in reach of Paris — `recipient_name` — every other French corps
    small and far away."""
    w = _boot()
    far = max((n for n, r in w.regions.items() if r.controller == "France"),
              key=lambda n: (w.get_distance("Paris", n), n))
    for m in w.marshals.values():
        if m.nation != "France":
            continue
        if m.name == recipient_name:
            m.location = "Paris"
            m.strength = 20000
        else:
            m.location = far
            m.strength = 2000
    w.regions["Paris"].stability = 90
    return w


class TestTheLevyNamesItsRecipientArm:
    def test_a_cavalry_recipient_is_not_the_foot_levy_on_offer(self):
        from backend.commands.economy_executor import get_levy_status
        w = _levy_board("Murat")
        assert w.marshals["Murat"].cavalry
        w.manpower_pools["France"]["cavalry"] = 0
        status = get_levy_status(w)
        assert status["headroom"] >= 10000 and status["infantry_pool"] >= 10000
        assert status["open"] is False
        assert status["closed_reason"] == (
            "The corps nearest the depot at Paris is Murat's cavalry — a levy "
            "there raises horse, not foot.")

    def test_the_executor_agrees_it_is_not_a_foot_levy(self):
        """Shown = applied: the default recruit path levies the RECIPIENT's
        arm, and with the cavalry pool empty it refuses."""
        from backend.commands.executor import CommandExecutor
        w = _levy_board("Murat")
        w.manpower_pools["France"]["cavalry"] = 0
        w.nation_gold["France"] = 50000
        with contextlib.redirect_stdout(io.StringIO()):
            result = CommandExecutor().execute(
                {"success": True, "command": {"action": "recruit"}}, {"world": w})
        assert result.get("success") is False, result.get("message")
        assert "cavalry" in str(result.get("message", "")).lower()

    def test_lever_down_restores_the_arm_blind_gate(self, monkeypatch):
        import backend.commands.economy_executor as EE
        monkeypatch.setattr(EE, "LEVY_NAMES_ITS_RECIPIENT_ARM", False)
        w = _levy_board("Murat")
        w.manpower_pools["France"]["cavalry"] = 0
        assert EE.get_levy_status(w)["open"] is True

    def test_an_infantry_recipient_keeps_the_open_levy(self):
        from backend.commands.economy_executor import get_levy_status
        w = _levy_board("Soult")
        assert not w.marshals["Soult"].cavalry
        status = get_levy_status(w)
        assert status["open"] is True and status["closed_reason"] == ""
