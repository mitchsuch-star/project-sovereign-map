"""IQ-2 "The Collapse Is Legible" — the war-room surfaces (Sept 14, 2026).

Measured in played 40-turn campaigns: a France at one province (and then
none, Paris lost, the Emperor captured) opened Talleyrand's war room on
"Denmark may be ready to discuss improved relations", read "No coalition
stands against us. Europe's alarm reads 0 (Calm)." while three courts were
still at war with her, was told to "win one more engagement" with no army in
the field, and saw its Balance of Europe tab project its "Next war of
conquest". Every surface here now reads `collapse.get_collapse_state` — and
the collapse stays legible, never terminal: nothing here ends, blocks or
shortens the campaign.

Every pin is falsifiable: each has a lever-down arm (the collapse lever for
collapse-keyed arms, the row's own lever for the general fixes) that must
reproduce the pre-IQ-2 copy.
"""

import contextlib
import io
from pathlib import Path

import pytest

from backend.game_logic import collapse as C
from backend.game_logic import diplomatic_advisory as A
from backend.game_logic import diplomatic_ledger as L
from backend.game_logic import intent as I
from backend.game_logic import war_status as WS
from backend.game_logic import coalition as CO
from backend.models.world_state import WorldState

SCENARIO = (Path(__file__).resolve().parent.parent / "godot-client"
            / "project-sovereign" / "assets" / "maps" / "europe_1805.json")

FORBIDDEN = ("game over", "campaign ends", "last chance", "eliminated")


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


def _collapse(w, keep=None, captor="Austria"):
    """Hand every French province but `keep` to a court at war with France.
    keep=None keeps the first homeland province alphabetically."""
    french = sorted(n for n, r in w.regions.items() if r.controller == "France")
    if keep is None:
        keep = (french[0],)
    for name in french:
        if name not in keep:
            w.regions[name].controller = captor
    w.invalidate_active_nations_cache()
    return w


def _capture_emperor(w, captor="Austria"):
    for m in w.marshals.values():
        if m.nation == "France" and getattr(m, "is_sovereign", False):
            m.captured_by = captor
            m.location = w.get_nation_capital(captor)
            m.strength = 0


def _end_all_wars(w):
    for key, state in list(w.diplomatic_states.items()):
        if "France" in key.split("|") and state == "WAR":
            w.diplomatic_states[key] = "PEACE"
    w.active_coalition = None
    w.invalidate_active_nations_cache()


@pytest.fixture
def collapsed():
    w = _collapse(_boot())
    _capture_emperor(w)
    return w


@pytest.fixture
def fallen():
    return _collapse(_boot(), keep=())


# ════════════════════════════════════════════════════════════════════════
# C1 — the war room
# ════════════════════════════════════════════════════════════════════════

class TestWarRoomLeadsWithOurOwnState:
    def test_our_own_state_comes_first_and_the_campaign_goes_on(self, collapsed):
        # ⚑ GE-1 (Sept 25, 2026) — CONSCIOUS FLIP: on the armed 1805 board
        # the scope line is the fall clock (`fall.scope_sentence`); IQ-2's
        # sentence stands on an unarmed world (the second half).
        from backend.game_logic import fall
        text = A._assess_situation(collapsed)["talleyrand_text"]
        assert "Our own state: France holds a single province:" in text
        assert "The Emperor is a prisoner of Austria." in text
        assert fall.scope_sentence(collapsed) in text
        assert C.CAMPAIGN_CONTINUES not in text
        collapsed.campaign_end = {}
        assert C.CAMPAIGN_CONTINUES in A._assess_situation(collapsed)["talleyrand_text"]
        text = A._assess_situation(collapsed)["talleyrand_text"]
        # It LEADS: before any war line.
        assert text.index("Our own state") < text.index("Against ")
        low = text.lower()
        for phrase in FORBIDDEN:
            assert phrase not in low, phrase

    def test_lever_down_the_war_room_says_nothing_of_itself(self, collapsed, monkeypatch):
        # ⚑ GE-1: the fall clocks speak too (the captive Emperor is the
        # chains arm) — the pre-IQ-2 silence is BOTH levers down.
        from backend.game_logic import fall
        monkeypatch.setattr(C, "THE_COLLAPSE_IS_LEGIBLE", False)
        monkeypatch.setattr(fall, "THE_EMPIRE_CAN_FALL", False)
        text = A._assess_situation(collapsed)["talleyrand_text"]
        assert "Our own state" not in text
        assert C.CAMPAIGN_CONTINUES not in text

    def test_a_standing_realm_hears_no_collapse_line(self):
        text = A._assess_situation(_boot())["talleyrand_text"]
        assert "Our own state" not in text

    def test_the_legacy_world_is_untouched_even_emptied(self):
        w = WorldState(player_nation="France")
        for r in w.regions.values():
            if r.controller == "France":
                r.controller = "Austria"
        w.invalidate_active_nations_cache()
        text = A._assess_situation(w)["talleyrand_text"]
        assert "Our own state" not in text


class TestTheLeagueLapsedTheWarsDidNot:
    def _lapsed(self, collapsed):
        collapsed.active_coalition = None
        collapsed.coalition_cooldown = 5
        collapsed.threat_level = 0
        return collapsed

    def test_names_the_courts_still_at_war_and_never_calm(self, collapsed):
        text = A._assess_situation(self._lapsed(collapsed))["talleyrand_text"]
        assert ("The coalition has lapsed as a league — no court fears France "
                "now — but Austria, Britain and Russia remain at war with us. "
                "(Europe's alarm reads 0.)") in text
        assert "Calm" not in text
        assert "No coalition stands against us. Europe's alarm" not in text

    def test_lever_down_is_the_old_calm_line(self, collapsed, monkeypatch):
        monkeypatch.setattr(C, "THE_COLLAPSE_IS_LEGIBLE", False)
        text = A._assess_situation(self._lapsed(collapsed))["talleyrand_text"]
        assert "No coalition stands against us. Europe's alarm reads 0 (Calm)." in text

    def test_no_war_under_collapse_is_no_precious_quiet(self, collapsed, monkeypatch):
        _end_all_wars(collapsed)
        text = A._assess_situation(collapsed)["talleyrand_text"]
        assert "rare and precious quiet" not in text
        assert ("France wages no war now — but the quiet comes after the "
                "collapse of the realm, not after a victory.") in text
        assert "no court is at war with us" in text
        monkeypatch.setattr(C, "THE_COLLAPSE_IS_LEGIBLE", False)
        assert "rare and precious quiet" in A._assess_situation(collapsed)["talleyrand_text"]


class TestCounselUnderTheCollapse:
    def test_rung_four_is_prefixed_with_the_collapse_fact(self, collapsed, monkeypatch):
        from backend.game_logic import recruitment
        monkeypatch.setattr(recruitment, "first_affordable_commission",
                            lambda *a, **k: None)
        _end_all_wars(collapsed)
        rec = A._build_situation_recommendation(collapsed, "France", [], None,
                                                "defensive")
        assert rec["kind"] == "open_proposal"
        assert rec["text"].startswith(
            "mark it plainly — France holds a single province:")
        assert "the ripest court in Europe for an approach" in rec["text"]
        monkeypatch.setattr(C, "THE_COLLAPSE_IS_LEGIBLE", False)
        down = A._build_situation_recommendation(collapsed, "France", [], None,
                                                 "defensive")
        assert down["text"].startswith(f"{down['target_nation']} is neither")

    def test_the_fallback_states_what_we_have(self, collapsed, monkeypatch):
        monkeypatch.setattr(A, "_build_situation_recommendation",
                            lambda *a, **k: None)
        text = A._assess_situation(collapsed)["talleyrand_text"]
        assert "hold our course" not in text
        assert ("My counsel, Sire: Europe offers no opening today, and I will "
                "not dress one up.") in text
        assert "corps still stand under our colours" in text.split("My counsel")[1]
        monkeypatch.setattr(C, "THE_COLLAPSE_IS_LEGIBLE", False)
        assert "hold our course" in A._assess_situation(collapsed)["talleyrand_text"]

    def test_the_overview_opens_on_our_own_state(self, collapsed, monkeypatch):
        first = A._diplomatic_overview(collapsed)["talleyrand_text"].splitlines()[0]
        assert first.startswith("An overview, Sire — and first, our own state: "
                                "France holds a single province:")
        monkeypatch.setattr(C, "THE_COLLAPSE_IS_LEGIBLE", False)
        assert A._diplomatic_overview(collapsed)["talleyrand_text"].splitlines()[0] \
            == "An overview, Sire:"

    def test_the_balanced_war_arm_is_honest_under_collapse(self, collapsed, monkeypatch):
        assert int(A.get_war_score_for(collapsed, "France", "Austria")) == 0
        out = A._recommend_action("Austria", collapsed)
        assert "Tilsit" not in out["talleyrand_text"]
        # IQ-2 review round — CONSCIOUSLY RE-PINNED: the arm quoted the PAIR
        # score and claimed a level ledger while the war-level score the HUD
        # reads was −60. It now states the collapse and quotes no score.
        assert out["talleyrand_text"].startswith(
            "Sire, " + C.summary_line(collapsed, C.get_collapse_state(collapsed)))
        assert "stands level" not in out["talleyrand_text"]
        assert "ledger" not in out["talleyrand_text"]
        assert out["context"]["recommendation"] == "Seek terms now."
        monkeypatch.setattr(C, "THE_COLLAPSE_IS_LEGIBLE", False)
        assert "Tilsit model" in A._recommend_action("Austria", collapsed)["talleyrand_text"]

    def test_no_alliance_is_immense_for_a_collapsed_france(self, collapsed, monkeypatch):
        _end_all_wars(collapsed)
        key = collapsed._make_diplo_key("France", "Denmark")
        collapsed.nation_relations[key] = 50
        collapsed.diplomatic_states[key] = "PEACE"
        text = A._recommend_action("Denmark", collapsed)["talleyrand_text"]
        assert "immense" not in text
        assert "mark it plainly: France holds a single province:" in text
        monkeypatch.setattr(C, "THE_COLLAPSE_IS_LEGIBLE", False)
        assert "strategic benefit immense" in \
            A._recommend_action("Denmark", collapsed)["talleyrand_text"]


class TestGeneralWarRoomFixes:
    def test_tilsit_needs_an_army_even_off_the_collapse(self, monkeypatch):
        """(g) general arm: a standing realm with no army free in the field."""
        w = _boot()
        for m in w.marshals.values():
            if m.nation == "France":
                m.strength = 0
        w._exposure_cache = None
        assert C.get_collapse_state(w) is None
        text = A._recommend_action("Austria", w)["talleyrand_text"]
        assert "no army in the field to win the engagement" in text
        assert "Tilsit model —" not in text
        monkeypatch.setattr(A, "THE_TILSIT_COUNSEL_NEEDS_AN_ARMY", False)
        assert "Tilsit model" in A._recommend_action("Austria", w)["talleyrand_text"]

    def test_compare_threats_reads_our_own_army_raw(self, monkeypatch):
        """(h) the fog helper invents 30,000 men for a France with no
        strength-positive marshal; our own army is never fogged."""
        w = _boot()
        for m in w.marshals.values():
            if m.nation == "France":
                m.strength = 0
        assert A._get_fogged_strength("France", w) == 30000  # the defect
        calls = []
        original = A._get_fogged_strength

        def _spy(nation, world):
            calls.append(nation)
            return original(nation, world)

        monkeypatch.setattr(A, "_get_fogged_strength", _spy)
        A._compare_threats(w)
        assert "France" not in calls
        monkeypatch.setattr(A, "THE_PLAYER_READS_HIS_OWN_STRENGTH_RAW", False)
        calls.clear()
        A._compare_threats(w)
        assert "France" in calls

    def test_invest_counsel_quotes_what_the_executor_applies(self, monkeypatch):
        """(i) shown = applied: +4 in the grip spiral, not a hard-coded +10."""
        from backend.game_logic import vassal as V
        from backend.models import authority
        w = _boot()
        monkeypatch.setattr(authority, "get_imperial_grip", lambda world, n: 10)
        w.vassals["Switzerland"]["loyalty"] = 30
        rec = A._build_situation_recommendation(w, "France", [], None, "defensive")
        assert rec["kind"] == "invest_vassal"
        assert rec["description"] == ("1 DP + 200 gold; +4 loyalty. The Emperor's "
                                      "faltering grip blunts the gesture.")
        # The Vassals tab reads the same single source.
        row = next(r for r in L._build_vassals(w)["rows"] if r["name"] == "Switzerland")
        assert row["invest_gain"] == L.invest_terms(w, "France")["gain"] == 4
        # And the executor applies exactly that.
        w.nation_gold["France"] = 5000
        w.diplomatic_points = 10  # the player's pool `_charge_dp` reads
        res = V.invest_in_vassal(w, "Switzerland")
        assert res["success"], res
        assert w.vassals["Switzerland"]["loyalty"] == 34
        monkeypatch.setattr(A, "THE_INVEST_COUNSEL_QUOTES_THE_EXECUTOR", False)
        w2 = _boot()
        w2.vassals["Switzerland"]["loyalty"] = 30
        down = A._build_situation_recommendation(w2, "France", [], None, "defensive")
        assert down["description"] == "1 DP + 200 gold; +10 loyalty."

    def test_invest_counsel_at_healthy_grip_is_byte_identical(self):
        w = _boot()
        w.vassals["Switzerland"]["loyalty"] = 30
        rec = A._build_situation_recommendation(w, "France", [], None, "defensive")
        assert rec["description"] == "1 DP + 200 gold; +10 loyalty."

    def test_the_design_price_clause_never_splices_indifferent(self, monkeypatch):
        from backend.game_logic import agendas
        w = _boot()
        monkeypatch.setattr(agendas, "agenda_satisfiable_by_player",
                            lambda nation, world: nation == "Austria")
        monkeypatch.setattr(agendas, "build_agenda_payload",
                            lambda nation, world: {"title": "Redeem Italy"})
        monkeypatch.setattr(I, "build_intent_payload", lambda nation, world: {
            "price": "indifferent", "price_display": "Indifferent",
            "summary": "x"})
        rows = [{"opponent": "Austria", "opponents": ["Austria"],
                 "war_score": 5, "status": "war",
                 "request_terms_state": {"state": "disabled"}}]
        rec = A._build_situation_recommendation(w, "France", rows, None, "defensive")
        assert rec["text"].endswith(" Their court is not yet prepared to act on it.")
        monkeypatch.setattr(I, "INDIFFERENT_READS_AS_A_SENTENCE", False)
        rec = A._build_situation_recommendation(w, "France", rows, None, "defensive")
        assert rec["text"].endswith(" Their court is prepared to go as far as indifferent.")


# ════════════════════════════════════════════════════════════════════════
# C2 — the diplomatic ledger
# ════════════════════════════════════════════════════════════════════════

class TestLedgerUnderTheCollapse:
    def test_the_projection_and_the_cooldown_tell_the_truth(self, collapsed, monkeypatch):
        collapsed.active_coalition = None
        collapsed.coalition_cooldown = 3
        collapsed.threat_level = 10
        boe = L._build_balance_of_europe(collapsed)
        # IQ-2 review round — CONSCIOUSLY RE-PINNED: only what is measured
        # (the realm, the alarm, the courts at war); no "because".
        held = C.realm_sentence(collapsed, C.get_collapse_state(collapsed)).rstrip(".")
        want = (f"{held}, and Europe's alarm has fallen to 10 — 3 courts "
                f"remain at war with us: Austria, Britain and Russia.")
        assert boe["collapse_line"] == want
        assert boe["threat_projection"]["collapse_line"] == want
        assert boe["headline_case"] == "COOLDOWN"
        assert boe["headline_note"] == "Austria, Britain and Russia remain at war with us."
        monkeypatch.setattr(C, "THE_COLLAPSE_IS_LEGIBLE", False)
        # IQ-3 (Sept 14, 2026) — CONSCIOUSLY FLIPPED: this arm asserts the
        # pre-IQ-2 payload, but IQ-3's own lever now names the 60 gate on any
        # COOLDOWN board below it (headline_note). The pre-both payload is
        # IQ-2's lever AND IQ-3's lever down; IQ-3's arm is pinned in
        # tests/test_iq3_the_league_is_spent.py.
        from backend.game_logic import coalition as _coal
        monkeypatch.setattr(_coal, "THE_LEAGUE_SPENDS_ITS_ALARM", False)
        down = L._build_balance_of_europe(collapsed)
        assert "collapse_line" not in down and "headline_note" not in down
        assert "collapse_line" not in down["threat_projection"]

    def test_a_high_alarm_is_not_said_to_have_fallen(self, collapsed):
        line = L._build_balance_of_europe(collapsed)["collapse_line"]
        # IQ-2 review round: "France no longer threatens anyone" stood beside
        # the mirror's own "he will go as far as war (alarm 70)".
        assert f"yet Europe's alarm stands at {int(collapsed.threat_level)} (" in line
        assert "no longer threatens" not in line

    def test_a_standing_realm_payload_carries_no_collapse_keys(self):
        boe = L._build_balance_of_europe(_boot())
        assert "collapse_line" not in boe and "headline_note" not in boe
        assert "collapse_line" not in boe["threat_projection"]

    def test_the_fallen_exposure_row_has_no_frontier(self, fallen, monkeypatch):
        row = L._build_france_exposure(fallen)
        assert "no armed neighbour compels a reserve" not in row["line"]
        assert row["line"] == (
            f"Free field army: the whole {row['standing']:,} — France holds no "
            f"frontier, so there is no reserve to keep; every court at war with "
            f"us may strike the army in the field (Austria, Britain and Russia).")
        monkeypatch.setattr(C, "THE_COLLAPSE_IS_LEGIBLE", False)
        assert "no armed neighbour compels a reserve" in \
            L._build_france_exposure(fallen)["line"]

    def test_courts_at_war_is_the_live_war_map(self, collapsed):
        assert L.courts_at_war_with(collapsed, "France") == ["Austria", "Britain", "Russia"]
        assert L.remain_at_war_clause(collapsed, ["Austria"]) == \
            "Austria remains at war with us"
        assert L.remain_at_war_clause(collapsed, []) == ""


# ════════════════════════════════════════════════════════════════════════
# C3 — Europe's mirror of France
# ════════════════════════════════════════════════════════════════════════

class TestTheMirror:
    def test_a_captive_is_not_coming_for_anyone(self, monkeypatch):
        w = _boot()
        vienna = w.get_nation_capital("Austria")
        for m in w.marshals.values():
            if m.nation == "France":
                m.captured_by = "Austria"
                m.location = vienna
                m.strength = 0
        assert I._perceived_target(w) is None
        monkeypatch.setattr(I, "THE_MIRROR_COUNTS_ONLY_STANDING_CORPS", False)
        assert I._perceived_target(w) == "Austria"  # the measured misreading

    def test_the_mirror_reads_a_broken_power(self, collapsed, fallen, monkeypatch):
        assert I.build_france_mirror_payload(collapsed)["read_as"] == \
            "A broken power — France holds a single province"
        assert I.build_france_mirror_payload(fallen)["read_as"] == \
            "A broken power — France holds no province of her own"
        monkeypatch.setattr(C, "THE_COLLAPSE_IS_LEGIBLE", False)
        assert "broken" not in I.build_france_mirror_payload(collapsed)["read_as"]

    def test_the_bottom_rung_gets_a_sentence(self, monkeypatch):
        w = _boot()
        monkeypatch.setattr(I, "get_france_perceived_intent",
                            lambda world: ("indifferent", 3, None))
        lines = I.build_france_mirror_payload(w)["lines"]
        assert lines[1] == "The courts believe he will act against no one (alarm 3)."
        monkeypatch.setattr(I, "INDIFFERENT_READS_AS_A_SENTENCE", False)
        lines = I.build_france_mirror_payload(w)["lines"]
        assert lines[1] == "The courts believe he will go as far as indifferent (alarm 3)."

    def test_the_intent_summary_never_splices_indifferent(self, monkeypatch):
        w = _boot()
        view = I.IntentView(nation="Denmark", want_id="x", want_title="X",
                            want_type="acquire_regions", against="Sweden",
                            weight=12, price="indifferent")
        monkeypatch.setattr(I, "get_nation_intent", lambda nation, world: view)
        assert I.build_intent_payload("Denmark", w)["summary"] == \
            "not yet prepared to act on it — Sweden stands in the way (weight 12)"
        monkeypatch.setattr(I, "INDIFFERENT_READS_AS_A_SENTENCE", False)
        assert I.build_intent_payload("Denmark", w)["summary"] == \
            "prepared to go as far as indifferent — Sweden stands in the way (weight 12)"

    def test_the_eases_dispatch_reads_indifference(self, monkeypatch):
        from backend.game_logic import dispatch
        w = _boot()

        def _view(nation, world):
            if nation == "Denmark":
                return I.IntentView(nation="Denmark", want_id="x", want_title="X",
                                    want_type="acquire_regions", against=None,
                                    weight=12, price="indifferent")
            return I.IntentView(nation=nation, want_id=None, want_title=None,
                                want_type=None, against=None, weight=0,
                                price="indifferent")

        captured = []
        monkeypatch.setattr(I, "get_nation_intent", _view)
        monkeypatch.setattr(dispatch, "queue_dispatch_event",
                            lambda world, etype, vars_, *a, **k: captured.append((etype, vars_)))
        w.nation_intent_seen = {"Denmark": "x|ask"}
        I.process_intent_movements(w)
        assert captured[0][0] == "intent_eases"
        assert captured[0][1]["price"] == "indifference"
        monkeypatch.setattr(I, "INDIFFERENT_READS_AS_A_SENTENCE", False)
        captured.clear()
        w.nation_intent_seen = {"Denmark": "x|ask"}
        I.process_intent_movements(w)
        assert captured[0][1]["price"] == "indifferent"


# ════════════════════════════════════════════════════════════════════════
# C4 — the dissolution copy (mechanics untouched)
# ════════════════════════════════════════════════════════════════════════

class TestDissolutionCopy:
    def _notice(self, w):
        return [n["message"] for n in w.notifications.get_pending()
                if n["type"] == "coalition_dissolved"][-1]

    def test_low_threat_names_the_wars_that_remain(self):
        w = _boot()
        name = w.active_coalition["name"]
        events = CO.dissolve_coalition(w, "low_threat")
        notice = self._notice(w)
        assert notice == (
            f"{name} has dissolved as a league: Europe's alarm has fallen below "
            f"{CO.DISSOLUTION_THREAT_THRESHOLD} and no court fears France enough "
            f"to hold it together. Austria, Britain and Russia remain at war "
            f"with us all the same.")
        assert "Low Threat" not in notice
        assert events[0]["message"] == notice
        assert events[0]["courts_at_war"] == ["Austria", "Britain", "Russia"]
        logged = [e for e in w.event_log if e.get("type") == "coalition_dissolved"][-1]
        assert logged["courts_at_war"] == ["Austria", "Britain", "Russia"]
        # Mechanics untouched: the league is gone, the wars are not.
        assert w.active_coalition is None
        assert w.is_at_war("France", "Austria")

    def test_lever_down_is_the_old_relief(self, monkeypatch):
        monkeypatch.setattr(CO, "THE_DISSOLUTION_NAMES_THE_WARS_THAT_REMAIN", False)
        w = _boot()
        name = w.active_coalition["name"]
        events = CO.dissolve_coalition(w, "low_threat")
        assert self._notice(w) == f"{name} has dissolved. Low Threat."
        assert events[0]["message"] == f"{name} has dissolved."
        assert "courts_at_war" not in events[0]
        logged = [e for e in w.event_log if e.get("type") == "coalition_dissolved"][-1]
        assert "courts_at_war" not in logged

    def test_every_reason_reads_as_words(self):
        w = _boot()
        name = w.active_coalition["name"]
        CO.dissolve_coalition(w, "insufficient_members")
        assert self._notice(w) == f"{name} has dissolved. Too few of its members remain at war."
        w2 = _boot()
        _end_all_wars(w2)
        w2.active_coalition = {"name": "The League", "leader": "Austria",
                               "members": [], "target_nation": "France"}
        CO.dissolve_coalition(w2, "low_threat")
        assert self._notice(w2) == (
            f"The League has dissolved. Europe's alarm has fallen below "
            f"{CO.DISSOLUTION_THREAT_THRESHOLD}.")


# ════════════════════════════════════════════════════════════════════════
# C5 — the war rows
# ════════════════════════════════════════════════════════════════════════

class TestWarRows:
    def test_tier_side_unit(self):
        """IQ-2 review round — CONSCIOUSLY RE-PINNED: a white peace is imposed
        by nobody (the dispatch's copy of the rule already excluded it; the
        dispatch now reads this function)."""
        from backend.game_logic.diplomacy import get_settlement_tier
        assert WS._tier_side(-60) == "theirs"
        assert WS._tier_side(60) == "ours"
        assert WS._tier_side(0) == ""
        for score in (-10, -1, 1, 10):
            if get_settlement_tier(score) == "white_peace":
                assert WS._tier_side(score) == "", score

    def test_every_player_row_names_whose_table_it_is(self, collapsed, monkeypatch):
        key = collapsed._make_diplo_key("France", "Denmark")
        collapsed.diplomatic_states[key] = "WAR"
        collapsed.invalidate_active_nations_cache()
        rows = [r for r in WS.build_active_wars(collapsed)["wars"]
                if r["status"] == "war"]
        assert rows
        for row in rows:
            assert row["settlement_tier_side"] == WS._tier_side(int(row["war_score"]))
        multi = next(r for r in rows if r.get("is_multi_participant_war"))
        assert multi["war_score"] < 0 and multi["settlement_tier_side"] == "theirs"
        denmark = next(r for r in rows if r["opponent"] == "Denmark")
        assert denmark["settlement_tier_side"] == WS._tier_side(int(denmark["war_score"]))
        monkeypatch.setattr(WS, "THE_TIER_NAMES_ITS_SIDE", False)
        for row in WS.build_active_wars(collapsed)["wars"]:
            assert "settlement_tier_side" not in row

    def test_the_hint_knows_the_homeland_is_lost(self, fallen, monkeypatch):
        row = next(r for r in WS.build_active_wars(fallen)["wars"]
                   if r.get("is_multi_participant_war"))
        assert row["objective"]["type"] == "defense"
        assert row["objective_hint"] == ("The homeland is lost — the defensive "
                                         "purpose has nothing left to hold.")
        assert "set war purpose" not in row["objective_hint"]
        assert WS._objective_hint(None, "Austria", fallen) == (
            "No war purpose set — and the homeland is lost, so no defensive "
            "purpose has anything left to hold.")
        # A purpose the player named is his own business either way.
        assert WS._objective_hint({"type": "conquest"}, "Austria", fallen) == ""
        monkeypatch.setattr(WS, "THE_HINT_KNOWS_THE_HOMELAND_IS_LOST", False)
        row = next(r for r in WS.build_active_wars(fallen)["wars"]
                   if r.get("is_multi_participant_war"))
        assert "'set war purpose against" in row["objective_hint"]

    def test_a_held_homeland_keeps_the_fa_d4_hint(self, collapsed):
        row = next(r for r in WS.build_active_wars(collapsed)["wars"]
                   if r.get("is_multi_participant_war"))
        assert "defensive purpose only" in row["objective_hint"]
