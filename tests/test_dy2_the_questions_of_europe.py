"""Tier 5 — session B (`DYNAMISM_SPEC.md` §4; the Tier-5 gate record §4a,
ruled November 10, 2026 in Plan Mode at the session's head; §2b session B).
One file for the tier: DY-2, DY-3 and the three leftovers session A put to
the user, each rule behind its own seam (`tests/_t3_seams.py` rows T5-*).

DY-2 — THE QUESTIONS OF EUROPE (`backend/game_logic/questions.py`, seam
`the_questions_of_europe`): the scenario's `questions` block (four tables
on the drawn map — the user's "Four on the drawn map"), the latch at the
one capture chokepoint and its auto-charge mirror, the envy term in
`intent._derive_weight` (+15 inside 8 turns for the OTHER claimants'
designs at the table), the beat "the Question turns" (one `question_turns`
row — DY-0's column — and a HIGH line in the Question's own voice), the
Balance tab's sentences, the Alarm's guarantee rung's Question arm.

DY-3 — THE CONGRESS RULES A QUESTION (seam `the_congress_rules_a_question`):
a sitting Congress recognizes each open Question's present holder — the
latch clears, the unseated claimants take −10 toward the holder, one
`congress` row (phase `ruling`), one beat.

DY-1e — THE LORD SIGNS FOR ITS CLIENT (`settlement_third_party`, seam
`a_lord_signs_for_its_client`; the user's "Road home" for Bern): a client
at its last province does not fall by the sword either — its AI lord's
pair with each holder closes (`last_refuge`), the homeland goes home and
the client lives on; the player's house stays exempt.

DY-1f — THE EMPEROR'S GIFT (the user's "best solution no corner cutting"
on the crowns): the levers were never the lock (K = 6 and 3,000 never
bit); the road to 1806's crowns is the Emperor's treaty — (i) the player's
road: an ally's petition asks for its AUTHORED design's provinces
(`settlement_offers._coveted_regions_of_ally`), Pressburg's Tyrol to
Bavaria end to end; (ii) the AI's road (seam `a_leader_signs_for_its_allies`):
an aim peace cedes each co-belligerent's delivered aim the side holds to
that ally (`war_council.side_aim_cessions`).

DY-1g — THE EMPEROR'S TREATY MOVES A SEAT (`game_end`, seam
`the_emperors_treaty_moves_a_seat`; the user's "reason best solution for
gameplay"): a court whose capital the player's house takes by treaty
removes too; the Congress's recognition by defeat reads the HISTORIC
capital (`congress._historic`); the player's own court never removes.
"""
from __future__ import annotations

import contextlib
import copy
import inspect
import io
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend import campaign_log as CL  # noqa: E402
from backend.game_logic import alarm as AL  # noqa: E402
from backend.game_logic import congress as CG  # noqa: E402
from backend.game_logic import game_end as GE  # noqa: E402
from backend.game_logic import questions as Q  # noqa: E402
from backend.game_logic import reforms as RF  # noqa: E402
from backend.game_logic import settlement_offers as SO  # noqa: E402
from backend.game_logic import settlement_third_party as TP  # noqa: E402
from backend.game_logic import war_council as WC  # noqa: E402
from backend.game_logic.agendas import AgendaView  # noqa: E402
from backend.modding.validator import validate_scenario  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
LEDGER_GD = (REPO / "godot-client" / "project-sovereign" / "scripts"
             / "diplomatic_ledger.gd")
_LONE = {"war_objective": "conquest", "suppress_unresolved_offensive_cascade": True}
TABLES = ("german_question", "italian_question", "eastern_question", "polish_question")
GERMAN_LINE = ("THE GERMAN QUESTION TURNS: Prussia holds Hanover; Vienna watches. "
               "Who speaks for Germany?")


@pytest.fixture()
def world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed="historical")


def _scenario() -> dict:
    return json.loads(SCENARIO.read_text(encoding="utf-8"))


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _events(world, etype: str):
    return [e for e in world.event_log if e.get("type") == etype]


def _takes(world, nation: str, *regions: str) -> None:
    with _quiet():
        for region_name in regions:
            world.capture_region(region_name, nation)


def _declares(world, aggressor: str, target: str) -> None:
    from backend.game_logic.diplomacy import declare_war
    with _quiet():
        assert declare_war(world, aggressor, target, **_LONE).get("success")


def _signs_away(world, region_name: str, ceder: str, receiver: str) -> None:
    world.regions[region_name].controller = receiver
    world.invalidate_active_nations_cache()
    with _quiet():
        GE.record_province_title(world, region_name, GE.TITLE_TREATY, ceder, receiver)


def _relation(world, a: str, b: str) -> int:
    return int(world.nation_relations.get(world._make_diplo_key(a, b), 0) or 0)


def _dispatch_lines(world, etype: str):
    from backend.game_logic.dispatch import _format_dispatch_event_text
    return [_format_dispatch_event_text(e["type"], e["template_vars"])
            for e in world.pending_dispatch_events if e["type"] == etype]


def _germany():
    return AgendaView(nation="Austria", id="primacy_germany", type="acquire_regions",
                      title="Primacy in Germany", regions=("Munich", "Swabia"))


def _client_of(world, client: str, lord: str) -> None:
    record = dict(world.vassals["Holland"])
    record["lord"] = lord
    world.vassals[client] = record
    world.invalidate_bloc_members_cache()
    world.invalidate_active_nations_cache()


# ═══════════════════════════════════════════════════════════════════════
# The block — the gate's four tables, the validator, the store
# ═══════════════════════════════════════════════════════════════════════

class TestTheBlock:
    def test_the_four_tables_as_ruled(self, world):
        assert [q["id"] for q in Q.block(world)] == list(TABLES)
        by_id = {q["id"]: q for q in Q.block(world)}
        assert by_id["german_question"]["provinces"] == ["Hanover", "Munich", "Swabia", "Dresden", "Frankfurt"]
        assert by_id["german_question"]["claimants"] == ["Austria", "Prussia", "France"]
        assert by_id["italian_question"]["claimants"] == ["France", "Austria", "Sardinia", "Naples"]
        assert by_id["eastern_question"]["provinces"][-1] == "New Russia"
        assert by_id["eastern_question"]["claimants"] == ["Russia", "Austria", "Ottoman", "Britain"]
        assert "Vilna" not in by_id["polish_question"]["provinces"]      # Russia's seat
        assert by_id["polish_question"]["claimants"][-1] == "Saxony"
        # every province drawn, every claimant a standing court
        for q in Q.block(world):
            assert all(p in world.regions for p in q["provinces"]), q["id"]
            assert all(c in world.get_active_nations() for c in q["claimants"]), q["id"]
            assert q["voice"]

    def test_the_shipped_file_keeps_its_eleven_warnings(self):
        result = validate_scenario(_scenario(), check_adjacency=True)
        assert result.is_valid and len(result.warnings) == 11
        assert not [w for w in result.warnings if w.path.startswith("questions")]

    def test_an_unknown_province_is_refused(self):
        data = _scenario()
        data["questions"][0]["provinces"].append("Venetia")
        result = validate_scenario(data, check_adjacency=True)
        assert any("Unknown region 'Venetia'" in e.message for e in result.errors)

    def test_a_province_sits_at_one_table(self):
        data = _scenario()
        data["questions"][1]["provinces"].append("Hanover")
        result = validate_scenario(data, check_adjacency=True)
        assert any("already sits at 'german_question'" in e.message for e in result.errors)

    def test_a_table_with_one_seat_is_no_question(self):
        data = _scenario()
        data["questions"][0]["claimants"] = ["Prussia"]
        result = validate_scenario(data, check_adjacency=True)
        assert any("At least two seated claimants" in e.message for e in result.errors)

    def test_an_unknown_claimant_warns_and_never_errors(self):
        data = _scenario()
        data["questions"][0]["claimants"].append("OttomanEmpire")
        result = validate_scenario(data, check_adjacency=True)
        assert result.is_valid
        assert any("seat nobody" in w.message for w in result.warnings
                   if w.path.startswith("questions"))

    def test_the_shape_is_hard(self):
        data = _scenario()
        data["questions"][0]["weight"] = 3
        data["questions"][0]["voice"] = "x" * 200
        result = validate_scenario(data, check_adjacency=True)
        paths = {e.path for e in result.errors}
        assert "questions[0].weight" in paths and "questions[0].voice" in paths

    def test_the_store_rides_the_moments_store_and_survives_a_save(self, world):
        from backend.models.world_state import WorldState
        assert Q.STORE_KEY in world.moments and Q.armed(world)
        world.current_turn = 5
        _takes(world, "Prussia", "Hanover")
        data = world.to_dict()
        assert set(data) == set(WorldState().to_dict()), "no new top-level field"
        again = WorldState.from_dict(data)
        assert Q.latch(again) == {"german_question": {"nation": "Prussia", "turn": 5}}
        assert Q.store(again)["turned"] == {"german_question": "Prussia"}
        assert [q["id"] for q in Q.block(again)] == list(TABLES)

    def test_a_world_that_authors_none_writes_nothing(self):
        from backend.models.world_state import WorldState
        bare = WorldState()
        assert bare.moments == {} and not Q.armed(bare)
        assert Q.note_capture(bare, "Paris", "Prussia", "France") is None
        assert bare.moments == {}
        assert Q.question_lines(bare) == [] and Q.envy_weight(bare, "Austria", _germany()) == 0

    def test_a_pre_tier_5_save_gains_the_block_on_load(self, world):
        from backend.models.world_state import WorldState
        data = world.to_dict()
        data["moments"].pop(Q.STORE_KEY)
        old = WorldState.from_dict(data)
        assert not Q.armed(old)
        assert Q.backfill(old, _scenario()) is True
        assert Q.armed(old) and Q.latch(old) == {}
        assert Q.backfill(old, _scenario()) is False, "a store carried is never overwritten"


# ═══════════════════════════════════════════════════════════════════════
# The latch — at the chokepoint and nowhere else
# ═══════════════════════════════════════════════════════════════════════

class TestTheLatch:
    def test_a_claimants_capture_latches_its_table(self, world):
        world.current_turn = 5
        _takes(world, "Prussia", "Hanover")
        assert Q.latch(world) == {"german_question": {"nation": "Prussia", "turn": 5}}

    def test_a_non_claimants_capture_writes_nothing(self, world):
        _takes(world, "Bavaria", "Frankfurt")            # Bavaria sits at no table
        assert Q.latch(world) == {}

    def test_a_province_at_no_table_writes_nothing(self, world):
        _takes(world, "Prussia", "Brunswick")
        assert Q.latch(world) == {}

    def test_a_clients_conquest_is_its_lords(self, world):
        world.current_turn = 7
        _takes(world, "Holland", "Frankfurt")            # France's client
        assert Q.latch(world)["german_question"] == {"nation": "France", "turn": 7}

    def test_the_latch_leaves_the_turns_intent_cache(self, world):
        """Intent is turn-granular by design (`intent.py`'s staleness
        contract): the envy reads from the next derivation, and a mid-turn
        flush at the latch moved the historical Prussia's crisis from turn 5
        to 9 on the sweep's first run."""
        # the chokepoint's own region-control flush is the engine's; the
        # Questions never add one of their own
        assert "_intent_cache" not in inspect.getsource(Q)
        _takes(world, "Prussia", "Hanover")
        assert Q.latch(world)["german_question"]["nation"] == "Prussia"

    def test_the_seam_down_writes_nothing(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T5-Q"])
        _takes(world, "Prussia", "Hanover")
        assert Q.latch(world) == {} and _events(world, "question_turns") == []

    def test_one_writer_at_the_chokepoint_and_its_mirror(self):
        from backend.models import world_state as WS
        src = inspect.getsource(WS)
        assert src.count("questions.note_capture(") == 2          # the chokepoint and its mirror
        assert src.count("_ac_questions.note_capture(") == 1      # the auto-charge's mirror
        # nothing else in the engine writes the latch (the Congress's own
        # `note_capture` is its titled-province count, another thing)
        for module in (TP, GE, CG, AL, WC):
            assert "questions.note_capture" not in inspect.getsource(module)
            assert "Q.note_capture" not in inspect.getsource(module)


# ═══════════════════════════════════════════════════════════════════════
# The envy term
# ═══════════════════════════════════════════════════════════════════════

class TestTheEnvy:
    def test_a_rivals_gain_quickens_the_design_inside_the_window(self, world):
        world.current_turn = 5
        _takes(world, "Prussia", "Hanover")
        assert Q.envy_weight(world, "Austria", _germany()) == Q.WEIGHT_QUESTION_ENVY == 15
        world.current_turn = 5 + Q.ENVY_WINDOW
        assert Q.envy_weight(world, "Austria", _germany()) == 15
        world.current_turn = 6 + Q.ENVY_WINDOW
        assert Q.envy_weight(world, "Austria", _germany()) == 0

    def test_a_courts_own_gain_quickens_nobody_of_its_house(self, world):
        _takes(world, "Prussia", "Hanover")
        prussia = AgendaView(nation="Prussia", id="hanoverian_prize", type="acquire_regions",
                             title="x", regions=("Hanover",))
        assert Q.envy_weight(world, "Prussia", prussia) == 0

    def test_a_court_not_seated_feels_nothing(self, world):
        _takes(world, "Prussia", "Hanover")
        bavaria = AgendaView(nation="Bavaria", id="x", type="acquire_regions",
                             title="x", regions=("Munich", "Swabia"))
        assert Q.envy_weight(world, "Bavaria", bavaria) == 0
        assert Q.envy_weight(world, "Russia", _germany()) == 0

    def test_a_design_off_the_table_feels_nothing(self, world):
        _takes(world, "Prussia", "Hanover")
        eastern = AgendaView(nation="Austria", id="the_eastern_question", type="acquire_regions",
                             title="x", regions=("Albania", "Rumelia"))
        assert Q.envy_weight(world, "Austria", eastern) == 0

    def test_the_weight_moves_by_the_addend(self, world, monkeypatch):
        from backend.game_logic.intent import _derive_weight
        world.current_turn = 6
        _takes(world, "Prussia", "Hanover")
        up = _derive_weight("Austria", _germany(), None, world)
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T5-Q"])
        down = _derive_weight("Austria", _germany(), None, world)
        assert up - down == 15

    def test_the_term_is_derived_never_dice(self):
        src = inspect.getsource(Q)
        assert "random" not in src and "seeded_jitter" not in src

    def test_the_envy_brings_a_court_to_the_ultimatum_never_past_it(self, world):
        """The session's own catch: asks are made below the ultimatum and a
        coercive demand at it; a court carried straight to `fight` never asks,
        the council's patient-ask gate never passes, and no war follows (the
        historical Prussia sat at `fight` ten turns and never fought Hanover).
        With the running weight given, the addend stops below the fight floor
        until the court's crisis stands."""
        from backend.game_logic.intent import PRICE_THRESHOLDS
        floors = dict(PRICE_THRESHOLDS)
        coerce, fight = floors["coerce"], floors["fight"]
        _takes(world, "Prussia", "Hanover")
        assert Q.envy_weight(world, "Austria", _germany()) == 15                      # the bare read
        # the ladder not climbed (Hesse: a court Austria is at peace with):
        # up to the ultimatum's door, never through it
        assert world.get_diplomatic_state("Austria", "Hesse") != "WAR"
        assert Q.envy_weight(world, "Austria", _germany(), 50, "Hesse") == 15
        assert Q.envy_weight(world, "Austria", _germany(), coerce - 5, "Hesse") == 4
        assert Q.envy_weight(world, "Austria", _germany(), coerce - 1, "Hesse") == 0
        assert Q.envy_weight(world, "Austria", _germany(), coerce + 3, "Hesse") == 0
        # the ladder climbed (two refused asks on record): up to the fight floor's door
        world.diplomatic_refusals["Austria>Hesse"] = [
            {"turn": world.current_turn, "type": "design_ask"}, {"turn": world.current_turn, "type": "design_ask"}]
        assert Q.envy_weight(world, "Austria", _germany(), coerce - 1, "Hesse") == fight - coerce
        assert Q.envy_weight(world, "Austria", _germany(), fight - 1, "Hesse") == 0
        # the crisis stands: the whole addend
        world.war_intents["Austria"] = {"target": "Hesse", "opened_turn": 3}
        assert Q.envy_weight(world, "Austria", _germany(), fight - 1, "Hesse") == 15
        # at war with its object (Bavaria, from the boot): the whole addend
        world.war_intents.pop("Austria")
        assert world.is_at_war("Austria", "Bavaria")
        assert Q.envy_weight(world, "Austria", _germany(), fight - 1, "Bavaria") == 15

    def test_the_derived_weight_passes_the_running_weight_after_the_jitter(self):
        """The cap reads the figure the ladder reads — the running weight
        AFTER the seeded jitter (on the driven austerlitz the jitter pushed a
        capped 84 to 85 and the fight rung)."""
        from backend.game_logic import intent as I
        src = inspect.getsource(I._derive_weight)
        assert "envy_weight(world, nation, agenda, int(weight), against)" in src
        assert src.index("seeded_jitter(") < src.index("envy_weight(world, nation, agenda")


# ═══════════════════════════════════════════════════════════════════════
# The beat — "the Question turns"
# ═══════════════════════════════════════════════════════════════════════

class TestTheBeat:
    def test_the_question_turns_once_per_turn_of_it(self, world):
        world.current_turn = 5
        _takes(world, "Prussia", "Hanover")
        [row] = _events(world, "question_turns")
        assert (row["question"], row["nation"], row["holds"]) == ("german_question", "Prussia", ["Hanover"])
        assert row["message"] == GERMAN_LINE
        assert _dispatch_lines(world, "question_turns") == [GERMAN_LINE]
        # Austria takes Munich: a tie at one each — the table has not turned
        _takes(world, "Austria", "Munich")
        assert len(_events(world, "question_turns")) == 1
        assert Q.latch(world)["german_question"]["nation"] == "Austria"
        # ...and Swabia: Austria holds two of five — it turns again
        _takes(world, "Austria", "Swabia")
        rows = _events(world, "question_turns")
        assert [r["nation"] for r in rows] == ["Prussia", "Austria"]
        assert rows[-1]["holds"] == ["Munich", "Swabia"]
        assert Q.store(world)["turned"]["german_question"] == "Austria"

    def test_a_table_held_from_the_boot_does_not_turn_for_its_holder(self, world):
        # Russia holds three of the Polish table's four: taking Posen is a
        # gain (the latch) but no turn — it held the most of it already
        _takes(world, "Russia", "Posen")
        assert Q.latch(world)["polish_question"]["nation"] == "Russia"
        assert _events(world, "question_turns") == []

    def test_the_beat_is_a_lead_at_high_priority(self, world):
        from backend.game_logic import dispatch as D
        assert D._DIPLOMATIC_EVENT_TEMPLATES["question_turns"] == "{line}"
        assert "question_turns" in inspect.getsource(D)
        assert CL.CATEGORY_MAP["question_turns"] == "diplomacy"
        assert "question_turns" in CL.LOG_TIER_LEAD
        from backend.game_logic import gazette as GZ
        assert "question_turns" in inspect.getsource(GZ)

    def test_the_one_new_log_type_and_the_census(self):
        assert "question_turns" in CL.CAMPAIGN_LOG_TYPES
        assert len(CL.CAMPAIGN_LOG_TYPES) == 183  # 182->183 flipped consciously: DY-2 (Nov 10, 2026) adds `question_turns` — a Question of Europe turns, a claimant's capture made it the table's plurality holder (DYNAMISM_SPEC.md §4; DY-0's column reads it); no inert type retired in exchange  # 181->182 flipped consciously: T4-3 (Nov 10, 2026) adds `rank_promotion`  # 180->181 flipped consciously: AU-2b adds `te_deum`  # 179->180 flipped consciously: S14c part 1 adds `moment`  # 178->179 flipped consciously: VP-1 adds `imperial_design`  # 176->178 flipped consciously: PC-R7 (ii) part 2 adds `war_articles_declared` and `war_articles_settled`  # 175->176 flipped consciously: PC-R2 adds `surety_returned`  # 173->175 flipped consciously: DD-1 S8 Step 3 adds `allegiance_bid` and `province_returned`  # 164->165 flipped consciously: IQ-7 adds `client_petition_answered`  # 165->166 flipped consciously: GE-1 adds `campaign_ending`  # 166->167 flipped consciously: GE-3 adds the congress chronicle type  # 167->168 flipped consciously: VP-M1 adds `marshal_wounded`  # 168->171 flipped consciously: RF-1 adds `law_enacted` / `law_repealed` / `law_lapsed`  # 171->172 flipped consciously: VD-C adds `vassal_contingent`  # 172->173 flipped consciously: TILSIT adds `continental_system_membership`

    def test_the_one_liner_and_the_court_knowledge(self, world):
        world.current_turn = 5
        _takes(world, "Prussia", "Hanover")
        [row] = _events(world, "question_turns")
        assert CL.format_event_oneliner(row, player_nation="France", world=world) == (
            "THE GERMAN QUESTION TURNS — Prussia holds Hanover")
        assert row in CL.filter_campaign_log(world.event_log, world), "court knowledge across Europe"

    def test_the_sweeps_column_reads_the_row(self, world):
        from tools.ai_v_sweep import derive_metrics
        _takes(world, "Prussia", "Hanover")
        [row] = _events(world, "question_turns")
        assert "question" in row, "the DY-0 column reads `question`"
        assert "question_turns" in inspect.getsource(derive_metrics)


# ═══════════════════════════════════════════════════════════════════════
# The words — the Balance tab's sentences, the client
# ═══════════════════════════════════════════════════════════════════════

class TestTheWords:
    def test_the_tables_at_the_boot(self, world):
        assert Q.question_lines(world) == [
            "The German Question: quiet; no claimant holds it.",
            "The Italian Question: quiet; France holds the most of it.",
            "The Eastern Question: quiet; the Ottoman Empire holds the most of it.",
            "The Polish Question: quiet; Russia holds the most of it.",
        ]

    def test_an_open_table_names_the_gainer_and_the_watchers(self, world):
        world.current_turn = 5
        _takes(world, "Prussia", "Hanover")
        assert Q.question_lines(world)[0] == (
            "The German Question: open — Prussia gains (turn 5); Vienna watches.")

    def test_the_player_is_never_named_as_a_watcher(self, world):
        _takes(world, "Austria", "Munich")
        line = Q.question_lines(world)[0]
        assert "Paris" not in line and "France" not in line and "Berlin watches" in line

    def test_the_balance_tab_carries_the_sentences(self, world):
        from backend.game_logic.diplomatic_ledger import _build_balance_of_europe
        _takes(world, "Prussia", "Hanover")
        assert _build_balance_of_europe(world)["question_lines"] == Q.question_lines(world)
        from backend.models.world_state import WorldState
        assert "question_lines" not in _build_balance_of_europe(WorldState())

    def test_the_client_renders_the_sentences(self):
        src = LEDGER_GD.read_text(encoding="utf-8")
        assert 'boe.get("question_lines", [])' in src
        assert "THE QUESTIONS OF EUROPE" in src

    def test_never_a_figure(self, world):
        _takes(world, "Prussia", "Hanover")
        for line in Q.question_lines(world):
            assert not any(ch.isdigit() for ch in line.split("(turn")[0])


# ═══════════════════════════════════════════════════════════════════════
# The Alarm's guarantee rung — the Question arm (§3c G2)
# ═══════════════════════════════════════════════════════════════════════

class TestTheRungsQuestionArm:
    def test_who_shares_a_table(self, world):
        assert Q.share_a_table(world, "Britain", "Ottoman")           # the Eastern table
        assert Q.share_a_table(world, "Saxony", "Russia")             # the Polish table
        assert not Q.share_a_table(world, "Prussia", "Ottoman")
        assert not Q.share_a_table(world, "Austria", "Austria")
        assert Q.share_a_table(world, "KingdomOfItaly", "Austria")    # France's client sits with its lord

    def _russia_free(self, world):
        """Russia at peace with everyone and in no live war instance (the
        join refusal reads the instances — in 1805 she and Austria stand
        on one side of the coalition's war), cold to neither court."""
        for key, state in list(world.diplomatic_states.items()):
            if "Russia" in key.split("|") and state in ("WAR", "ALLIANCE"):
                world.diplomatic_states[key] = "PEACE"
        for instance in world.war_instances.values():
            for side in ("attackers", "defenders", "active_participants"):
                instance[side] = [n for n in (instance.get(side) or []) if n != "Russia"]
            (instance.get("side_by_nation") or {}).pop("Russia", None)
            instance["active_diplo_keys"] = [
                k for k in (instance.get("active_diplo_keys") or []) if "Russia" not in k.split("|")]
        world.invalidate_war_instance_indexes()
        world.invalidate_active_nations_cache()
        world.invalidate_bloc_members_cache()
        world.nation_relations[world._make_diplo_key("Russia", "Austria")] = 0
        world.nation_relations[world._make_diplo_key("Russia", "Prussia")] = 0

    def test_a_court_seated_with_the_victim_gives_its_word_though_no_neighbour(self, world, monkeypatch):
        self._russia_free(world)
        monkeypatch.setattr(world, "get_neighbouring_nations", lambda nation: [])
        assert AL.alarmed_guarantor(world, "Austria", "Prussia") == "Russia"   # the Polish table

    def test_without_a_shared_table_a_non_neighbour_never_pledges(self, world, monkeypatch):
        self._russia_free(world)
        monkeypatch.setattr(world, "get_neighbouring_nations", lambda nation: [])
        assert AL.alarmed_guarantor(world, "Austria", "Hesse") is None

    def test_the_seam_down_is_the_neighbour_rule_alone(self, world, monkeypatch):
        self._russia_free(world)
        monkeypatch.setattr(world, "get_neighbouring_nations", lambda nation: [])
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T5-Q"])
        assert AL.alarmed_guarantor(world, "Austria", "Prussia") is None


# ═══════════════════════════════════════════════════════════════════════
# DY-3 — the Congress rules a Question
# ═══════════════════════════════════════════════════════════════════════

def _sits(world, summoned: int):
    world.congress = {"status": CG.SITTING, "summoned_turn": summoned, "ends_turn": summoned + 8}
    assert CG.sitting(world)


class TestTheCongressRulesAQuestion:
    def test_the_holder_is_recognized_and_the_table_closes(self, world):
        world.current_turn = 9
        _takes(world, "Prussia", "Hanover")
        world.current_turn = 12
        _sits(world, 11)
        austria_before = _relation(world, "Austria", "Prussia")
        france_before = _relation(world, "France", "Prussia")
        [row] = Q.congress_rules(world)
        assert (row["type"], row["phase"], row["question"], row["court"], row["aggrieved"]) == (
            "congress", "ruling", "german_question", "Prussia", ["Austria"])
        assert row["message"] == ("The Congress rules the German Question: Prussia is "
                                  "recognized in what it holds; Vienna takes it ill.")
        assert Q.latch(world) == {}                              # envy relief
        assert Q.ruled(world) == {"german_question": {"holder": "Prussia", "turn": 12}}
        assert _relation(world, "Austria", "Prussia") == austria_before + Q.QUESTION_RULING_GRIEVANCE
        assert Q.QUESTION_RULING_GRIEVANCE == -10
        assert _relation(world, "France", "Prussia") == france_before, "the player's house takes no grievance"
        assert Q.envy_weight(world, "Austria", _germany()) == 0
        assert _dispatch_lines(world, "question_ruled") == [row["message"]]
        assert Q.question_lines(world)[0] == (
            "The German Question: ruled at the Congress (turn 12) — Prussia recognized.")

    def test_once_a_sitting_and_the_table_reopens_on_a_capture(self, world):
        world.current_turn = 9
        _takes(world, "Prussia", "Hanover")
        world.current_turn = 12
        _sits(world, 11)
        assert len(Q.congress_rules(world)) == 1
        assert Q.congress_rules(world) == []
        world.current_turn = 14
        _takes(world, "Austria", "Munich", "Swabia")             # re-latched inside the sitting
        assert Q.latch(world)["german_question"]["nation"] == "Austria"
        assert Q.congress_rules(world) == [], "one ruling a sitting"
        _sits(world, 30)                                          # a later Congress rules it again
        world.current_turn = 31
        [row] = Q.congress_rules(world)
        assert (row["question"], row["court"]) == ("german_question", "Austria")

    def test_a_table_nobody_holds_is_not_ruled(self, world):
        world.current_turn = 9
        _takes(world, "Prussia", "Hanover")
        _takes(world, "Austria", "Munich")                        # one each: no plurality
        _sits(world, 11)
        assert Q.congress_rules(world) == [] and "german_question" in Q.latch(world)

    def test_no_sitting_no_latch_no_ruling(self, world):
        assert Q.congress_rules(world) == []
        _sits(world, 11)
        assert Q.congress_rules(world) == []

    def test_the_seam_down_rules_nothing(self, world, monkeypatch):
        _takes(world, "Prussia", "Hanover")
        _sits(world, 11)
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T5-C"])
        assert Q.congress_rules(world) == [] and "german_question" in Q.latch(world)

    def test_the_ruling_rides_the_sittings_tick_and_no_new_log_type(self):
        src = inspect.getsource(CG.process_end_of_turn)
        assert "_questions.congress_rules(world)" in src
        assert src.index("take_the_signatures(world)") < src.index("_questions.congress_rules") < src.index("_take_answers(world)")
        assert "question_ruled" not in CL.CAMPAIGN_LOG_TYPES


# ═══════════════════════════════════════════════════════════════════════
# DY-1e — the lord signs for its client at the last (Bern's road home)
# ═══════════════════════════════════════════════════════════════════════

class TestTheLordSignsForItsClient:
    def _britains_client_fights_saxony(self, world):
        _client_of(world, "Switzerland", "Britain")
        _declares(world, "Britain", "Saxony")                    # Switzerland follows its lord
        war = next(i for i in world.war_instances.values()
                   if "Switzerland" in (i.get("active_participants") or []))
        assert war["side_by_nation"]["Switzerland"] == "attackers"

    def test_the_lord_signs_and_the_client_lives_on(self, world):
        self._britains_client_fights_saxony(world)
        world.current_turn = 8
        _takes(world, "Saxony", "Bern")                           # its last province
        [event] = [e for e in _events(world, "third_party_peace") if e.get("exit") == TP.LAST_REFUGE_EXIT]
        assert event["proposer"] == "Switzerland" and event["signed_by"] == {"Saxony": "Britain"}
        assert event["consequence"] == "Britain signs for Switzerland at the last — Saxony evacuates Bern."
        assert _events(world, "nation_eliminated") == []
        assert world.regions["Bern"].controller == "Switzerland"
        assert world.get_diplomatic_state("Britain", "Saxony") == "PEACE"
        assert world.get_diplomatic_state("Switzerland", "Saxony") == "PEACE"
        assert world.vassals["Switzerland"]["lord"] == "Britain"

    def test_the_seam_down_is_the_old_erasure(self, world, monkeypatch):
        self._britains_client_fights_saxony(world)
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T5-BERN"])
        _takes(world, "Saxony", "Bern")
        assert [e["nation"] for e in _events(world, "nation_eliminated")] == ["Switzerland"]

    def test_the_players_client_still_falls(self, world):
        assert world.vassals["Switzerland"]["lord"] == "France"
        _declares(world, "Saxony", "Switzerland")
        _takes(world, "Saxony", "Bern")
        assert [e["nation"] for e in _events(world, "nation_eliminated")] == ["Switzerland"]
        assert _events(world, "third_party_peace") == []

    def test_a_client_at_war_on_its_own_account_signs_its_own(self, world):
        _client_of(world, "Switzerland", "Britain")
        _declares(world, "Switzerland", "Saxony")                 # Britain stays at peace with Saxony
        assert world.get_diplomatic_state("Britain", "Saxony") != "WAR"
        _takes(world, "Saxony", "Bern")
        [event] = [e for e in _events(world, "third_party_peace") if e.get("exit") == TP.LAST_REFUGE_EXIT]
        assert event["signed_by"] == {"Saxony": "Switzerland"}
        assert event["consequence"].startswith("Switzerland signs at the last — ")
        assert _events(world, "nation_eliminated") == []

    def test_the_seam_is_registered(self):
        assert T3_SEAMS_BY_ROW["T5-BERN"] == [
            "backend.game_logic.settlement_third_party:a_lord_signs_for_its_client=False"]


# ═══════════════════════════════════════════════════════════════════════
# DY-1f — the Emperor's gift: both roads to a crown
# ═══════════════════════════════════════════════════════════════════════

from backend.game_logic.settlement_scoring import (  # noqa: E402
    calculate_common_peace_acceptance as _REAL_ACCEPTANCE,
)


def _accepts(*args, **kwargs):
    result = _REAL_ACCEPTANCE(*args, **kwargs)
    result.update({"score": 100, "verdict": "accept", "hard_stops": [],
                   "accept_threshold": 50, "side_pressure_score": 70})
    return result


SCORER_SEAM = "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance"


class TestTheEmperorsGift:
    def test_the_levers_stand(self):
        assert RF.PROMOTION_HOLD_TURNS == 6
        assert all(row["price"] == 3000 for rows in _scenario()["reforms"].values()
                   if isinstance(rows, list) for row in rows if row.get("requires_design"))

    def test_an_ally_asks_for_its_authored_design(self, world):
        assert SO._coveted_regions_of_ally(world, "Bavaria") == ["Tyrol"]
        assert SO._coveted_regions_of_ally(world, "Saxony")[0] == "Posen"
        assert SO._coveted_regions_of_ally(world, "Hesse") == ["Westphalia"]
        assert SO._coveted_regions_of_ally(world, "Denmark") == ["Scania"]
        assert SO._coveted_regions_of_ally(world, "Sardinia") == ["Piedmont", "Savoy"]
        assert SO._coveted_regions_of_ally(world, "Portugal") == []

    def test_pressburgs_tyrol_to_bavaria_end_to_end(self, world):
        """The player's road, every link: the petition carries the Tyrol
        France holds; the cession titles it to Bavaria; six quiet turns
        later the crown's refusal clears, the AI's own rung enacts it, and
        the one `rank_promotion` row is written."""
        from backend.game_logic import settlement_ratify
        wid = next(wid for wid, i in world.war_instances.items()
                   if {"France", "Austria", "Bavaria"} <= set(i.get("active_participants") or []))
        world.current_turn = 6
        world.regions["Tyrol"].controller = "France"
        world.invalidate_active_nations_cache()
        with patch.object(SO, "_ally_has_reward_standing", return_value=True), _quiet():
            queued = SO.queue_ally_settlement_petitions_for_player_action(
                world, trigger_action="stage_settlement", war_id=wid,
                covered_enemy_participants=["Austria"], settlement_terms=[])
        clause = next(p["candidate_clause"] for p in queued
                      if p.get("ally_nation") == "Bavaria" and p.get("candidate_clause"))
        assert clause == {"type": "territory_cede", "from": "Austria", "to": "Bavaria", "region": "Tyrol"}
        with _quiet():
            applied = settlement_ratify._apply_settlement_terms(
                world, settlement_terms=[clause], war_id=wid, settlement_route_id="gift")
        assert [c["region"] for c in applied] == ["Tyrol"]
        assert world.regions["Tyrol"].controller == "Bavaria"
        assert world.province_title["Tyrol"]["kind"] == GE.TITLE_TREATY
        assert "not yet 6 quiet turns" in RF.law_refusal(world, "Bavaria", "the_royal_crown", admin_actions=1)
        world.current_turn += 6
        world.nation_gold["Bavaria"] = 6000
        assert RF.law_refusal(world, "Bavaria", "the_royal_crown", admin_actions=1) == ""
        assert RF.find_ai_enactment(world, "Bavaria", 6000, 1) == {
            "action": "enact_law", "target": "the_royal_crown"}
        with _quiet():
            RF.enact_law(world, "Bavaria", RF.find_law(world, "Bavaria", "the_royal_crown"))
        assert world.get_power_tier("Bavaria") == "secondary"
        assert [e["nation"] for e in _events(world, "rank_promotion")] == ["Bavaria"]

    def _russia_and_denmark_on_sweden(self, world):
        from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance
        world.current_turn = 10
        war = make_synthetic_war_instance(
            "war_1", attackers=["Russia", "Denmark"], defenders=["Sweden"],
            attacker_leader="Russia", defender_leader="Sweden", created_turn=4)
        world.war_instances["war_1"] = war
        for pair in war["active_diplo_keys"]:
            world.diplomatic_states[pair] = "WAR"
        key = world._make_diplo_key("Russia", "Sweden")
        world.war_scores[key] = 30 if key.split("|")[0] == "Russia" else -30
        world.invalidate_war_instance_indexes()
        world.regions["Finland"].controller = "Russia"
        world.regions["Scania"].controller = "Russia"
        world._agenda_cache = None
        world.invalidate_active_nations_cache()
        return war

    def test_the_leader_signs_for_its_allies(self, world):
        war = self._russia_and_denmark_on_sweden(world)
        assert WC.side_aim_cessions(world, war, "attackers", "Sweden", "Russia", taken=["Finland"]) == [
            {"type": "territory_cede", "from": "Sweden", "to": "Denmark", "region": "Scania"}]
        with patch(SCORER_SEAM, side_effect=_accepts), _quiet():
            event = TP.attempt_aim_held_settlement(world, "war_1", war)
        assert event["exit"] == TP.AIM_HELD_EXIT
        assert event["consequence"] == ("Russia takes Finland. Denmark takes Scania. "
                                        "Russia is now free to look elsewhere.")
        assert world.regions["Scania"].controller == "Denmark"
        assert world.province_title["Scania"]["kind"] == GE.TITLE_TREATY
        assert world.province_title["Scania"]["holder"] == "Denmark"
        world.current_turn += 6
        world.nation_gold["Denmark"] = 6000
        assert RF.law_refusal(world, "Denmark", "both_shores_of_the_sound", admin_actions=1) == ""

    def test_the_seam_down_is_the_leaders_aim_alone(self, world, monkeypatch):
        war = self._russia_and_denmark_on_sweden(world)
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T5-GIFT"])
        with patch(SCORER_SEAM, side_effect=_accepts), _quiet():
            event = TP.attempt_aim_held_settlement(world, "war_1", war)
        assert event["consequence"].count(" takes ") == 1
        # the pre-gift world: a junior's aim in its leader's hands is no
        # aim of the leader's house, and T3-6 hands it home to the loser
        assert world.regions["Scania"].controller == "Sweden"
        assert world.province_title.get("Scania", {}).get("holder") != "Denmark"

    def test_the_players_house_is_never_signed_for(self, world):
        war = self._russia_and_denmark_on_sweden(world)
        _client_of(world, "Denmark", "France")
        assert WC.side_aim_cessions(world, war, "attackers", "Sweden", "Russia") == []

    def test_a_great_powers_capital_is_never_a_gift(self, world):
        war = self._russia_and_denmark_on_sweden(world)
        world.regions["Stockholm"].controller = "Russia"
        world.invalidate_active_nations_cache()
        regions = [c["region"] for c in WC.side_aim_cessions(world, war, "attackers", "Sweden", "Russia")]
        assert "Stockholm" not in regions


# ═══════════════════════════════════════════════════════════════════════
# DY-1g — the Emperor's treaty moves a seat
# ═══════════════════════════════════════════════════════════════════════

class TestTheEmperorsTreatyMovesASeat:
    def test_viennas_cession_removes_the_court_and_the_congress_reads_vienna(self, world):
        _signs_away(world, "Vienna", "Austria", "France")
        assert world.get_nation_capital("Austria") == "Bohemia"
        assert GE.historic_capital(world, "Austria") == "Vienna"
        assert CG._historic(world, "Austria") == "Vienna"
        assert CG._capital_taken(world, "Austria") and CG.capital_in_our_hands(world, "Austria")
        [row] = [e for e in _events(world, "province_returned") if e.get("outcome") == "court_removed"]
        assert (row["nation"], row["region"], row["lost"]) == ("Austria", "Bohemia", "Vienna")
        written = CG.note_ratification(world, ["Austria"], True, capital_kept=["Austria"])
        assert written == {"Austria": "capital"}
        assert CG.record(world)["signed"]["Austria"]["capital"] == "Vienna"
        assert CG.recognition_lines(world, written) == [
            "Recognition: Austria will recognize the order at the Congress — Vienna stays ours by this treaty."]

    def test_the_latch_holds_while_vienna_is_ours_and_breaks_when_it_goes(self, world):
        _signs_away(world, "Vienna", "Austria", "France")
        world.diplomatic_states[world._make_diplo_key("Austria", "France")] = "PEACE"
        CG.note_ratification(world, ["Austria"], True, capital_kept=["Austria"])
        assert CG._signed_record(world, "Austria") is not None
        world.regions["Vienna"].controller = "Austria"
        world.invalidate_active_nations_cache()
        assert CG._signed_record(world, "Austria") is None

    def test_the_emperors_client_takes_a_seat_too(self, world):
        _signs_away(world, "Munich", "Bavaria", "Holland")
        assert world.get_nation_capital("Bavaria") == "Franconia"

    def test_the_players_own_court_never_removes(self, world):
        _signs_away(world, "Paris", "France", "Britain")
        assert world.get_nation_capital("France") == "Paris"

    def test_the_seam_down_is_session_as_boundary(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T5-SEAT"])
        _signs_away(world, "Vienna", "Austria", "France")
        assert world.get_nation_capital("Austria") == "Vienna"
        assert CG._historic(world, "Austria") == "Vienna"

    def test_the_congress_reads_the_historic_capital_everywhere(self):
        src = inspect.getsource(CG)
        court_reads = [ln for ln in src.splitlines()
                       if "get_nation_capital(court)" in ln]
        assert court_reads == [], court_reads
        assert "historic_capital(world, court)" in inspect.getsource(GE.note_ratification)


# ═══════════════════════════════════════════════════════════════════════
# The scale contract and the registry
# ═══════════════════════════════════════════════════════════════════════

class TestTheScaleContract:
    def test_the_module_never_walks_the_map(self):
        src = inspect.getsource(Q)
        assert "regions.values()" not in src and "regions.items()" not in src
        assert "get_active_nations" in src

    def test_every_seam_is_registered_and_zero_arg(self):
        for row in ("T5-Q", "T5-C", "T5-BERN", "T5-GIFT", "T5-SEAT"):
            [spec] = T3_SEAMS_BY_ROW[row]
            module_path, rest = spec.split(":")
            name = rest.split("=")[0]
            import importlib
            seam = getattr(importlib.import_module(module_path), name)
            assert seam() is True and inspect.signature(seam).parameters == {}

    def test_the_numbers_are_the_gates(self):
        assert (Q.ENVY_WINDOW, Q.WEIGHT_QUESTION_ENVY, Q.QUESTION_RULING_GRIEVANCE) == (8, 15, -10)


# ═══════════════════════════════════════════════════════════════════════
# The session's one measure — six arms on three surfaces, each ALONE
# (`tools/_t5_measure.py`; `tools/_t5_series_arms.py`). Seeded paths,
# not laws (DYNAMISM_SPEC.md §4a's landing note; SYSTEMS_REFERENCE.md §202).
# ═══════════════════════════════════════════════════════════════════════

def _record(name: str) -> dict:
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


def _dump(row) -> str:
    return json.dumps(row, sort_keys=True)


SEEDS = ("austerlitz", "eylau", "friedland", "historical", "jena", "lodi",
         "marengo", "rivoli", "ulm", "wagram")
STAMP = "2026_11_10"
AMBIENT_ARMS = (("0", "t5_control"), ("Q", "t5_q"), ("QC", "t5_qc"), ("BERN", "t5_bern"),
                ("GIFT", "t5_gift"), ("ALL", "t5"))


class TestTheSessionBMeasure:
    """The FINAL records — the honoured-ladder tree (the first sweep's run and
    the hook's first run named three defects, fixed at the cause; the record
    is the third run's). Seeded paths, not laws; read honestly."""

    def _sig(self, label: str) -> dict:
        return _record(f"_dy_signature_{label}_{STAMP}.json")

    def _census(self, label: str) -> dict:
        return _record(f"_{label}_census_{STAMP}.json")

    def test_arm_0_reproduces_session_as_records_on_both_surfaces(self):
        a = _record("_dy_signature_t4_3_2026_11_10.json")
        ctl = self._sig("t5_control")
        for seed in SEEDS:
            assert _dump(ctl["seeds"][seed]) == _dump(a["seeds"][seed]), seed
        harness = _record(f"_t5_chain_d_{STAMP}.json")
        prior = _record("_t4_3_chain_d_2026_11_10.json")["arms"]["ALL"]
        for seed in SEEDS:
            mine = harness["arms"]["0"][seed]
            assert _dump({k: mine.get(k) for k in prior[seed]}) == _dump(prior[seed]), seed
        assert self._census("t5_control")["totals"]["annexations_outside_aim"] == 1   # Bern

    def test_the_questions_alone_move_every_ambient_seed_and_the_classes_hold(self):
        ctl, q = self._sig("t5_control"), self._sig("t5_q")
        movers = [s for s in SEEDS if _dump(q["seeds"][s]) != _dump(ctl["seeds"][s])]
        assert movers == list(SEEDS)
        for arm, label in AMBIENT_ARMS:
            assert self._sig(label)["story_class_count"] == 10, arm
        # on seven seeds the Questions move only the new column and the turn a
        # court first reaches `fight` (the envy hastens a climb already under
        # way); the whole signature moves on rivoli alone
        for seed in SEEDS:
            a, b = ctl["seeds"][seed]["signature"], q["seeds"][seed]["signature"]
            moved = {k for k in a if _dump(a[k]) != _dump(b.get(k))}
            if seed == "rivoli":
                assert {"war_turns", "ai_war_count", "guarantees_given"} <= moved, moved
            elif seed in ("austerlitz", "wagram"):
                assert moved == {"courts_at_fight", "first_fight_turn", "questions_turned"}, (seed, moved)
            else:
                assert moved <= {"first_fight_turn", "questions_turned"}, (seed, moved)
        # the Congress's ruling, the gift and the seat move no ambient seed —
        # no Congress sits, no co-belligerent's delivered aim meets an aim
        # peace, no player treaty cedes a capital in forty ambient turns
        for prev, nxt in (("t5_q", "t5_qc"), ("t5_bern", "t5_gift"), ("t5_gift", "t5")):
            a, b = self._sig(prev), self._sig(nxt)
            assert all(_dump(a["seeds"][s]) == _dump(b["seeds"][s]) for s in SEEDS), (prev, nxt)

    def test_the_tables_turn_for_austria_on_every_seed(self):
        """The German Question turns for Austria at turn 2 on every seed (her
        Munich and Swabia in the opening war) and the Italian on every seed
        (Milan and Piedmont from the Kingdom of Italy); 26 turns of a table in
        all; Prussia turns the German table once (jena, 41); the Polish and the
        Eastern tables never turn — the Porte holds four of five from the boot,
        Russia three of four, and no claimant takes from them in forty turns."""
        fin = self._sig("t5")
        census = self._census("t5")
        for seed in SEEDS:
            turned = fin["seeds"][seed]["signature"]["questions_turned"]
            assert turned[0] == [2, "german_question"], (seed, turned)
            assert any(q == "italian_question" for _, q in turned), seed
            assert not any(q in ("polish_question", "eastern_question") for _, q in turned), seed
        rows = [r for c in census["seeds"].values() for r in c["questions_turned"]]
        assert len(rows) == 26 and census["totals"]["questions_turned"] == 26
        assert sorted({r["court"] for r in rows}) == ["Austria", "Prussia"]
        assert [(r["turn"], r["court"]) for r in census["seeds"]["jena"]["questions_turned"]][-1] == (41, "Prussia")
        assert self._census("t5_q")["totals"]["questions_turned"] == 27   # ulm's Prussian turn, before Bern's road re-timed it

    def test_no_second_great_power_war_appears(self):
        """The tier's signature change, read honestly: the war column stands
        where session A left it on eight seeds; rivoli gains the Hanover war
        where Prussia's honour war stood (the envy hastens her climb, the
        crisis comes before the word); ulm's late Saxon cluster calms (13 → 5
        pairs). The tables turn for Austria, who is at war already, and the
        only envious design with an army behind it is Prussia's Hanover —
        reported, and put to the user at session C's head."""
        ctl, fin = self._sig("t5_control"), self._sig("t5")

        def pairs(rec, seed):
            return {tuple(p) for p in dict(rec["seeds"][seed]["story_class"])["war_pairs"]}

        for seed in SEEDS:
            if seed in ("rivoli", "ulm"):
                continue
            assert pairs(fin, seed) == pairs(ctl, seed), seed
            assert fin["seeds"][seed]["signature"]["war_turns"] == ctl["seeds"][seed]["signature"]["war_turns"], seed
        assert pairs(fin, "rivoli") - pairs(ctl, "rivoli") == {("Hanover", "Prussia")}
        assert pairs(ctl, "rivoli") - pairs(fin, "rivoli") == {("Prussia", "Switzerland")}
        assert (ctl["seeds"]["rivoli"]["signature"]["ai_war_count"], fin["seeds"]["rivoli"]["signature"]["ai_war_count"]) == (0, 1)
        assert (len(pairs(ctl, "ulm")), len(pairs(fin, "ulm"))) == (13, 5)
        assert fin["seeds"]["historical"]["signature"]["war_turns"] == [11, 12, 27, 27, 37]
        assert all(fin["seeds"][s]["signature"]["rank_promotions"] == [] for s in SEEDS)

    def test_berns_road_clears_the_annexation_line_and_switzerland_lives(self):
        qc, bern = self._sig("t5_qc"), self._sig("t5_bern")
        movers = [s for s in SEEDS if _dump(bern["seeds"][s]) != _dump(qc["seeds"][s])]
        assert movers == ["ulm"]
        assert self._census("t5_qc")["totals"]["annexations_outside_aim"] == 1
        assert self._census("t5_bern")["totals"]["annexations_outside_aim"] == 0
        assert self._census("t5")["totals"]["annexations_outside_aim"] == 0
        fin = self._sig("t5")
        assert all(fin["seeds"][s]["signature"]["eliminations"] == [[t, "KingdomOfItaly"]]
                   for s, t in zip(SEEDS, (10, 7, 23, 9, 7, 10, 21, 7, 10, 9)))
        harness = _record(f"_t5_chain_d_{STAMP}.json")
        for arm in ("0", "Q", "QC", "BERN", "GIFT", "ALL"):
            assert harness["totals"][arm]["annexations_outside_aim"] == 0, arm
            assert all(set(v["annexations_outside_aim_by_court"]) <= {"France"}
                       for v in harness["arms"][arm].values()), arm

    def test_the_tiers_honest_totals(self):
        ctl, q, fin = (self._census("t5_control")["totals"], self._census("t5_q")["totals"],
                       self._census("t5")["totals"])
        assert (ctl["last_refuges"], fin["last_refuges"]) == (22, 22)
        assert (ctl["alarm_guarantees"], fin["alarm_guarantees"]) == (11, 10)    # friedland's word for Bavaria no longer given: Prussia is at Hanover first
        assert (ctl["guarantees_honoured"], fin["guarantees_honoured"]) == (7, 6)
        assert (ctl["captures_outside_aim"], q["captures_outside_aim"], fin["captures_outside_aim"]) == (252, 258, 248)
        assert (ctl["rank_promotions"], fin["rank_promotions"]) == (0, 0)
        assert fin["question_rulings"] == 0 and fin["lord_refuges"] == 0 and fin["ally_cessions"] == 0
        # Bern's road on ulm ran through the client's OWN signature: Britain,
        # its lord, was at peace with Bavaria, so the war was Switzerland's own
        ulm = [r for r in self._census("t5")["seeds"]["ulm"]["last_refuges"]]
        assert [(r["turn"], r["proposer"], r["accepter"]) for r in ulm] == [(14, "Switzerland", "Bavaria")]
        assert ulm[0]["consequence"].startswith("Switzerland signs at the last — Bavaria evacuates Bern")

    def test_the_harness_moves_on_the_questions_alone(self):
        harness = _record(f"_t5_chain_d_{STAMP}.json")
        arms = harness["arms"]
        movers = [s for s in SEEDS if _dump(arms["Q"][s]) != _dump(arms["0"][s])]
        assert movers == ["ulm"]
        for prev, nxt in (("Q", "QC"), ("QC", "BERN"), ("BERN", "GIFT"), ("GIFT", "ALL")):
            assert all(_dump(arms[prev][s]) == _dump(arms[nxt][s]) for s in SEEDS), (prev, nxt)
        # the harness's France is the player nation: its own entry is reported, never gated
        assert (harness["totals"]["0"]["captures_outside_aim"],
                harness["totals"]["ALL"]["captures_outside_aim"]) == (119, 118)

    def test_the_france_band_holds_on_every_arm(self):
        band = _record(f"_t5_band_{STAMP}.json")
        lo, hi = band["band"]
        for arm, rows in band["arms"].items():
            figures = {name: rows[name]["provinces"] for name in ("CMD-H", "CMD-A", "CMD-M")}
            assert figures == {"CMD-H": 28, "CMD-A": 27, "CMD-M": 26}, arm
            assert all(lo <= v <= hi for v in figures.values()), arm

    def test_the_standing_series_does_not_move(self):
        """`tools/_t5_series_arms.py` → `_t5_series_arms_final.json`: an arm
        per seam, each seam's reach counted — every arm reproduces HEAD's
        `BASELINE_SERIES` byte for byte, so no re-pin and no re-link. The
        Questions' seam is read 2,215 times on that loop, eight latches and
        two turns; the seat seam's three moves are session A's own."""
        rec = _record("_t5_series_arms_final.json")
        assert list(rec["arms"]) == ["0", "Q", "QC", "BERN", "GIFT", "ALL"]
        for arm, row in rec["arms"].items():
            assert row["first_divergence_vs_prior"] is None, arm
            assert row["series"] == rec["prior"], arm
        reach = rec["arms"]["ALL"]["reach"]["counts"]
        assert reach["q_seam_reads"] > 2000 and reach["latches"] == 8 and reach["turns"] == 2
        assert reach["rulings"] == 0 and reach["lord_refuges"] == 0 and reach["ally_cessions"] == 0
        assert reach["seats_moved"] == 3
        assert rec["arms"]["0"]["reach"]["counts"]["latches"] == 0
