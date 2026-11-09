"""T3-4 — the terms (`AI_INTENT_SPEC.md` §13.2 R5; `DYNAMISM_SPEC.md`
§2 Tier 3; November 9, 2026; the rules `SYSTEMS_REFERENCE.md` §196).

A court that HOLDS the object of its war sues to lock it. ONE predicate
(`war_council.aim_sue_due` — a DELIVERED gain from this enemy, nothing
still owed, the pair's war score at R5's 25) and two roads (GR5):

* AI–AI (`settlement_third_party`, seam `a_held_aim_sues`): an AI-only war
  ends whole on its leaders' aims (`attempt_aim_held_settlement`, the
  existing machinery verbatim); a pair inside France's war exits on its
  own (`held_aim_suit`, the pair exits' third road). The aim's delivered
  provinces are ceded by treaty, nothing more asked; the loser signs
  inside `AIM_TERMS_BAND` of its own peace line.
* AI–player (`ai_diplomacy`, seam `a_held_aim_offers_terms`): P8-Aim, the
  aim's letter (`aim_peace`) above P8's dictated ladder.

Two census corrections ride the record: P8 was ALREADY built (R116 — the
aim letter lands as its first arm), and R5's literal "held" was
degenerate (a held aim is one that was GAINED).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic import ai_diplomacy as AD  # noqa: E402
from backend.game_logic import settlement_third_party as TP  # noqa: E402
from backend.game_logic import war_council as WC  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
T3_4_DOWN = T3_SEAMS_BY_ROW["T3-4"]
ITALY = ("Milan", "Piedmont", "Savoy")


@pytest.fixture()
def world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed="historical")


def _fresh(world) -> None:
    world._agenda_cache = None
    world.invalidate_active_nations_cache()


def _score(world, nation: str, enemy: str, value: int) -> None:
    key = world._make_diplo_key(nation, enemy)
    world.war_scores[key] = value if key.split("|")[0] == nation else -value


def _tyrol_to_bavaria(world, score: int = 40) -> None:
    world.regions["Tyrol"].controller = "Bavaria"
    _fresh(world)
    _score(world, "Bavaria", "Austria", score)
    world.current_turn = 6


def _italy_to_austria(world, score: int = 30, held=ITALY) -> None:
    for region_name in held:
        world.regions[region_name].controller = "Austria"
    _fresh(world)
    _score(world, "Austria", "France", score)
    world.current_turn = 6


def _boot_instance(world, pair_key: str):
    return next(i for i in world.war_instances.values()
                if pair_key in (i.get("active_diplo_keys") or []))


def _scania_war(world, score: int = 30):
    from backend.game_logic.diplomacy import declare_war
    result = declare_war(world, "Denmark", "Sweden", war_objective="conquest")
    assert result.get("success")
    war = world.war_instances[result["war_id"]]
    world.regions["Scania"].controller = "Denmark"
    _fresh(world)
    _score(world, "Denmark", "Sweden", score)
    world.current_turn = int(war.get("created_turn", 1)) + 4
    return result["war_id"], war


def _pair_exit(world):
    key = world._make_diplo_key("Austria", "Bavaria")
    inst = _boot_instance(world, key)
    events = []
    TP._process_exhausted_pair_exits(world, inst["war_id"], inst, events)
    return key, events


class TestThePredicate:
    def test_nothing_is_delivered_at_the_boot(self, world):
        # The 1805 boot: every war pair, both ways — no court has taken
        # anything yet, so no court's aim is held and nobody sues.
        pairs = [tuple(key.split("|"))
                 for inst in world.war_instances.values()
                 for key in inst.get("active_diplo_keys") or []]
        assert pairs
        for a, b in pairs:
            for x, y in ((a, b), (b, a)):
                assert WC.war_aim_delivered(world, x, y) == [], (x, y)
                assert not WC.war_aim_held(world, x, y), (x, y)

    def test_a_province_taken_is_a_delivered_aim(self, world):
        _tyrol_to_bavaria(world)
        assert WC.war_aim_delivered(world, "Bavaria", "Austria") == ["Tyrol"]
        assert WC.war_aim_held(world, "Bavaria", "Austria")
        assert WC.aim_sue_due(world, "Bavaria", "Austria")

    def test_lost_homeland_blocks(self, world):
        # Bavaria took the Tyrol but Austria holds Swabia: a peace now
        # would title Swabia away by the status quo — no court sues so.
        _tyrol_to_bavaria(world)
        world.regions["Swabia"].controller = "Austria"
        _fresh(world)
        assert WC.war_aim_delivered(world, "Bavaria", "Austria") == ["Tyrol"]
        assert not WC.war_aim_held(world, "Bavaria", "Austria")

    def test_a_fallen_capital_has_no_design_voice(self, world):
        # Munich lost: the survival override empties the designs (the
        # agenda law) — a court fighting for its life sues on no aim.
        _tyrol_to_bavaria(world)
        world.regions["Munich"].controller = "Austria"
        _fresh(world)
        assert WC.war_aim_delivered(world, "Bavaria", "Austria") == []

    def test_the_designs_part_still_owed_delivers_nothing(self, world):
        # Milan and Piedmont taken, Savoy still French: the design's part
        # in France's house is not wholly in hand — nothing is delivered.
        _italy_to_austria(world, held=("Milan", "Piedmont"))
        assert WC.war_aim_delivered(world, "Austria", "France") == []
        assert not WC.war_aim_held(world, "Austria", "France")

    def test_a_two_holder_design_is_delivered_per_enemy(self, world):
        # Russia's Gulf and Straits names Finland (Sweden's) and Rumelia
        # (the Porte's): Finland in hand is delivered against SWEDEN while
        # Rumelia stays Ottoman — the Finnish War ended at Fredrikshamn.
        from backend.game_logic.diplomacy import declare_war
        assert declare_war(world, "Russia", "Sweden",
                           war_objective="conquest").get("success")
        world.regions["Finland"].controller = "Russia"
        _fresh(world)
        assert world.regions["Rumelia"].controller != "Russia"
        assert WC.war_aim_delivered(world, "Russia", "Sweden") == ["Finland"]

    def test_a_clients_holding_counts_but_is_never_ceded(self, world):
        world.vassals["Saxony"] = {"lord": "Austria"}
        _italy_to_austria(world, held=("Piedmont", "Savoy"))
        world.regions["Milan"].controller = "Saxony"
        _fresh(world)
        assert WC.war_aim_held(world, "Austria", "France")
        assert WC.aim_cessions(world, "Austria", "France",
                               homeland_only=False) == ["Piedmont", "Savoy"]

    def test_a_great_powers_capital_is_never_ceded(self, world):
        world.agendas["Bavaria"] = [{"id": "crafted", "type": "acquire_regions",
                                     "title": "Crafted", "regions": ["Vienna", "Tyrol"]}]
        world.regions["Vienna"].controller = "Bavaria"
        _tyrol_to_bavaria(world)
        assert "Vienna" in WC.war_aim_delivered(world, "Bavaria", "Austria")
        assert WC.aim_cessions(world, "Bavaria", "Austria",
                               homeland_only=True) == ["Tyrol"]

    def test_an_enemy_left_with_nothing_is_stripped_only_at_ninety(self, world):
        _scania_war(world)
        for region in world.regions.values():
            if region.controller == "Sweden":
                region.controller = "Denmark"
        _fresh(world)
        assert not world.get_nation_regions("Sweden")
        assert WC.aim_cessions(world, "Denmark", "Sweden", homeland_only=True) == []
        _score(world, "Denmark", "Sweden", 95)
        assert WC.aim_cessions(world, "Denmark", "Sweden",
                               homeland_only=True) == ["Scania"]

    def test_an_empty_stated_object_never_holds(self, world):
        # Britain's designs are a posture and a denial — no acquire: her
        # holding French soil is no aim delivered (the existing roads stand).
        world.regions["Brittany"].controller = "Britain"
        _fresh(world)
        _score(world, "Britain", "France", 60)
        assert WC.war_aim_delivered(world, "Britain", "France") == []
        assert not WC.aim_sue_due(world, "Britain", "France")

    def test_the_capital_default_alone_never_holds(self, world):
        # A bare declaration's objective defaults to the enemy's seat; a
        # court with no design holding Stockholm has delivered no aim — and
        # a court with one need never take Stockholm to sue for Scania.
        _scania_war(world)
        world.regions["Stockholm"].controller = "Denmark"
        world.agendas["Denmark"] = []
        _fresh(world)
        assert WC.war_aim_delivered(world, "Denmark", "Sweden") == []
        assert not WC.war_aim_held(world, "Denmark", "Sweden")

    def test_the_seat_is_never_owed(self, world):
        _scania_war(world)
        record = world.war_objectives[world._make_diplo_key("Denmark", "Sweden")]["Denmark"]
        assert record["target_regions"] == ["Stockholm"]
        assert WC.war_aim_held(world, "Denmark", "Sweden", side=["Sweden"])

    def test_a_war_without_a_record_never_holds(self):
        from backend.models.world_state import WorldState
        legacy = WorldState(player_nation="France")
        assert not (legacy.war_instances or {})
        for nation in legacy.get_active_nations():
            for enemy in legacy.get_nations_at_war_with(nation):
                assert WC.war_aim_delivered(legacy, nation, enemy) == []


class TestTheAIRoads:
    def test_the_pair_exit_cedes_the_aim_by_treaty(self, world):
        _tyrol_to_bavaria(world)
        key, events = _pair_exit(world)
        assert len(events) == 1
        event = events[0]
        assert event["exit"] == TP.AIM_HELD_EXIT == "aim_held_sue"
        assert (event["proposer"], event["accepter"]) == ("Bavaria", "Austria")
        assert "Bavaria holds Tyrol, the object of her war" in event["consequence"]
        assert world.get_diplomatic_state("Austria", "Bavaria") == "PEACE"
        title = world.province_title["Tyrol"]
        assert title["kind"] == "treaty" and not title.get("retained")
        assert (title["from"], title["holder"]) == ("Austria", "Bavaria")
        assert world.armistice_cooldowns[key] == TP.PAIR_EXIT_TRUCE_FLOOR_TURNS
        logged = [e for e in world.event_log if e.get("type") == "third_party_peace"]
        assert logged[-1]["exit"] == "aim_held_sue"
        from backend.game_logic.game_end import SIGNED_PEACE_REASONS
        assert "aim_held_sue" in SIGNED_PEACE_REASONS

    def test_the_ceded_province_is_never_handed_back(self, world):
        # No Bavarian marshal stands in the Tyrol, so the unheld-homeland
        # pass would hand it home — but this very peace signed it away.
        _tyrol_to_bavaria(world)
        assert not [m for m in world.get_marshals_in_region("Tyrol")
                    if m.nation == "Bavaria" and m.strength > 0]
        _key, events = _pair_exit(world)
        assert world.regions["Tyrol"].controller == "Bavaria"
        assert "Unheld homeland" not in events[0]["consequence"]

    def test_the_loser_signs_inside_its_band(self, world, monkeypatch):
        _tyrol_to_bavaria(world)
        monkeypatch.setattr(AD, "effective_peace_threshold", lambda *a, **k: -40)
        _score(world, "Bavaria", "Austria", 25)
        assert TP.aim_terms_signable(world, "Austria", "Bavaria")
        _score(world, "Bavaria", "Austria", 24)
        assert not TP.aim_terms_signable(world, "Austria", "Bavaria")
        assert TP.AIM_TERMS_BAND == 15 and WC.AIM_SUE_SCORE == 25

    def test_a_hardened_loser_holds_out(self, world):
        # The boot's own reading (seeded paths, not laws): Austria's line
        # against Bavaria sits below the base, so +30 is not yet enough
        # and +40 is — the readiness of the court, not a constant.
        _tyrol_to_bavaria(world, score=30)
        assert not TP.aim_terms_signable(world, "Austria", "Bavaria")
        _score(world, "Bavaria", "Austria", 40)
        assert TP.aim_terms_signable(world, "Austria", "Bavaria")

    def test_a_young_pair_waits(self, world):
        _tyrol_to_bavaria(world)
        assert TP.held_aim_suit(world, "Austria", "Bavaria", 6) is None
        assert TP.held_aim_suit(world, "Austria", "Bavaria", 0) == (
            "Bavaria", "Austria", ["Tyrol"])

    def test_the_instance_road_ends_an_ai_war_on_its_aim(self, world):
        war_id, war = _scania_war(world)
        events = TP.process_third_party_settlements(world)
        mine = [e for e in events if e.get("war_id") == war_id]
        assert len(mine) == 1
        assert mine[0]["exit"] == "aim_held_sue"
        assert (mine[0]["proposer"], mine[0]["accepter"]) == ("Denmark", "Sweden")
        assert "Denmark takes Scania" in mine[0]["consequence"]
        assert war.get("ended_turn") is not None
        assert world.get_diplomatic_state("Denmark", "Sweden") == "PEACE"
        assert world.province_title["Scania"]["kind"] == "treaty"

    def test_the_scorers_hard_stops_still_veto(self, world, monkeypatch):
        from backend.game_logic import settlement_scoring
        war_id, war = _scania_war(world)
        monkeypatch.setattr(settlement_scoring, "calculate_common_peace_acceptance",
                            lambda *a, **k: {"hard_stops": ["patched"], "verdict": "reject"})
        assert TP.attempt_aim_held_settlement(world, war_id, war) is None
        assert world.get_diplomatic_state("Denmark", "Sweden") == "WAR"

    def test_the_broker_road_never_runs_the_aim_arm(self, world, monkeypatch):
        war_id, war = _scania_war(world)

        def _boom(*a, **k):
            raise AssertionError("the broker road ran the aim arm")
        monkeypatch.setattr(TP, "attempt_aim_held_settlement", _boom)
        TP.attempt_third_party_settlement(world, war_id, war, force=True,
                                          broker=world.player_nation)

    def test_two_homeland_provinces_leave_the_punitive_record(self, world):
        from backend.game_logic.emergent_designs import PUNITIVE_MEMORY_TYPE
        from backend.game_logic.settlement_reactions import get_settlement_memories
        world.agendas["Bavaria"] = [{"id": "crafted", "type": "acquire_regions",
                                     "title": "Crafted", "regions": ["Tyrol", "Bohemia"]}]
        world.regions["Bohemia"].controller = "Bavaria"
        _tyrol_to_bavaria(world)
        _key, events = _pair_exit(world)
        assert events and events[0]["exit"] == "aim_held_sue"
        records = get_settlement_memories(world, subject="Austria",
                                          memory_type=PUNITIVE_MEMORY_TYPE)
        assert records and records[-1]["actor"] == "Bavaria"

    def test_the_seam_down_restores_the_old_roads(self, world, monkeypatch):
        hold_down(monkeypatch, T3_4_DOWN)
        _tyrol_to_bavaria(world)
        _key, events = _pair_exit(world)
        assert events == []
        assert world.get_diplomatic_state("Austria", "Bavaria") == "WAR"
        war_id, war = _scania_war(world)
        TP.process_third_party_settlements(world)
        assert world.get_diplomatic_state("Denmark", "Sweden") == "WAR"


class TestTheLetter:
    def test_the_aim_letter(self, world):
        _italy_to_austria(world)
        proposal = AD.process_diplomatic_phase("Austria", world)
        assert proposal["proposal_type"] == AD.AIM_PEACE_TYPE == "aim_peace"
        terms = proposal["terms"]
        assert terms["type"] == "peace"
        assert [d["regions"] for d in terms["demands"]] == [["Milan"], ["Piedmont"], ["Savoy"]]
        assert proposal["_force_send"] and proposal["decision_reason"] == "aim_held"
        assert "Milan, Piedmont and Savoy, the object she went to war for" \
            in proposal["talleyrand_assessment"]

    def test_below_the_line_no_letter(self, world):
        _italy_to_austria(world, score=20)
        proposal = AD.process_diplomatic_phase("Austria", world)
        assert proposal is None or proposal["proposal_type"] != "aim_peace"

    def test_an_aim_not_held_falls_through_to_p8(self, world):
        _italy_to_austria(world, score=45, held=("Milan", "Piedmont"))
        proposal = AD.process_diplomatic_phase("Austria", world)
        assert proposal is not None and proposal["proposal_type"] == "harsh_peace"

    def test_accepting_titles_the_aim(self, world):
        from backend.commands.executor import CommandExecutor
        _italy_to_austria(world)
        dialogue = AD.deliver_ai_proposal(AD.process_diplomatic_phase("Austria", world), world)
        result = CommandExecutor()._diplomatic._handle_accept_ai_proposal(dialogue, world)
        assert result.get("success")
        assert world.get_diplomatic_state("Austria", "France") == "PEACE"
        for region_name in ITALY:
            assert world.regions[region_name].controller == "Austria"
            assert world.province_title[region_name]["kind"] == "treaty"

    def test_refusal_cools_the_aim_label_not_p1s(self, world):
        from backend.commands.executor import CommandExecutor
        _italy_to_austria(world)
        dialogue = AD.deliver_ai_proposal(AD.process_diplomatic_phase("Austria", world), world)
        CommandExecutor()._diplomatic._handle_reject_ai_proposal(dialogue, world)
        cooldowns = world.ai_proposal_cooldowns
        assert int(cooldowns.get("Austria|aim_peace", 0)) > 0
        assert int(cooldowns.get("Austria|peace", 0)) == 0

    def test_the_rail_names_the_provinces(self, world):
        _italy_to_austria(world)
        AD.deliver_ai_proposal(AD.process_diplomatic_phase("Austria", world), world)
        rows = [n for n in world.notifications.to_list()
                if n.get("title") == "Austria offers peace on her war's object"]
        assert rows and "Milan, Piedmont and Savoy, the object of her war" in rows[-1]["message"]

    def test_the_label_joins_the_tables(self):
        from backend.display_names import DECISION_REASON_DISPLAY, PROPOSAL_TYPE_DISPLAY
        from backend.game_logic.coalition import PEACE_FAMILY_PROPOSAL_TYPES
        from backend.models.dialogue_manager import WAR_DECISION_LETTER_TYPES
        assert PROPOSAL_TYPE_DISPLAY["aim_peace"] == "Peace on the War's Object"
        assert DECISION_REASON_DISPLAY["aim_held"] == "the war's object held"
        assert "aim_peace" in WAR_DECISION_LETTER_TYPES
        assert "aim_peace" in PEACE_FAMILY_PROPOSAL_TYPES

    def test_the_seam_down_writes_p8_as_before(self, world, monkeypatch):
        hold_down(monkeypatch, T3_4_DOWN)
        _italy_to_austria(world, score=45)
        proposal = AD.process_diplomatic_phase("Austria", world)
        assert proposal is not None and proposal["proposal_type"] == "harsh_peace"


def _record(name: str) -> dict:
    import json
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


class TestTheMeasure:
    """The two chains on the final tree (`tools/_t3_4_measure.py`, each run
    ALONE — the kept-record idiom): the CONTROL, both T3-4 seams held down
    through `INK_IRON_SEAMS`, and the FINAL; each writes the DY signature
    record and the terms' census from the same digests. Seeded paths, not
    laws — the per-seed reading pinned."""

    T33 = "_dy_signature_t3_3_2026_11_08.json"
    CONTROL = "_dy_signature_t3_4_control_2026_11_09.json"
    FINAL = "_dy_signature_t3_4_2026_11_09.json"
    CENSUS = "_t3_4_aim_terms_2026_11_09.json"
    CENSUS_CONTROL = "_t3_4_aim_terms_control_2026_11_09.json"
    AIM_PEACE_TURNS = {"austerlitz": 17, "eylau": 22, "friedland": 17,
                       "historical": 16, "jena": 14, "lodi": 21, "marengo": 15,
                       "rivoli": 22, "ulm": 18, "wagram": 16}

    def test_the_control_is_the_t3_3_record_byte_for_byte(self):
        # Both seams down reproduce T3-3's FINAL on every seed: the seams
        # cover the whole slice, and no instrument moved.
        t33, control = _record(self.T33), _record(self.CONTROL)
        assert set(control["seeds"]) == set(t33["seeds"])
        for seed in t33["seeds"]:
            assert control["seeds"][seed] == t33["seeds"][seed], seed
        census = _record(self.CENSUS_CONTROL)
        assert census["totals"] == {"aim_letters": 0, "aim_peaces": 0,
                                    "captures_outside_aim": 208}

    def test_every_seed_ends_prussias_war_on_her_aim(self):
        # Ten aim peaces, one a seed and every one the same story: Prussia's
        # war on Hanover ends on her aim's terms — the province ceded by
        # treaty, nothing more asked — the very turn Hanover's own suit had
        # ended it in the control (with ~2,610 gold paid instead).
        census = _record(self.CENSUS)
        assert census["totals"]["aim_peaces"] == 10
        for seed, turn in self.AIM_PEACE_TURNS.items():
            peaces = census["seeds"][seed]["aim_peaces"]
            assert len(peaces) == 1, seed
            peace = peaces[0]
            assert (peace["turn"], peace["proposer"], peace["accepter"]) == (
                turn, "Prussia", "Hanover"), seed
            assert peace["consequence"].startswith("Prussia takes Hanover."), seed

    def test_the_aim_letters_reach_france_twice(self):
        census = _record(self.CENSUS)
        letters = {seed: [(row["turn"], row["proposer"]) for row in c["aim_letters"]]
                   for seed, c in census["seeds"].items() if c["aim_letters"]}
        assert letters == {"historical": [(9, "Austria")], "wagram": [(9, "Austria")]}

    def test_two_world_lines_move_and_the_classes_hold(self):
        control, final = _record(self.CONTROL), _record(self.FINAL)
        movers = {seed for seed in control["seeds"]
                  if control["seeds"][seed]["signature"] != final["seeds"][seed]["signature"]}
        assert movers == {"austerlitz", "marengo"}
        assert final["story_class_count"] == control["story_class_count"] == 8
        import json

        def partition(record):
            groups = {}
            for seed, row in record["seeds"].items():
                groups.setdefault(json.dumps(row["story_class"], sort_keys=True), set()).add(seed)
            return sorted(sorted(g) for g in groups.values())
        assert partition(final) == partition(control)

    def test_marengo_hanover_survives(self):
        # Hanover keeps the treasury the indemnity took and rebuilds (5,000 →
        # 17,000 by turn 17): no longer the outmatched prize, Hesse's
        # Westphalian want stays at 72 and never reaches war — the second war
        # on Hanover (turn 20) never comes.
        control = _record(self.CONTROL)["seeds"]["marengo"]["signature"]
        final = _record(self.FINAL)["seeds"]["marengo"]["signature"]
        assert [23, "Hanover"] in control["eliminations"]
        assert [23, "Hanover"] not in final["eliminations"]
        assert (control["war_turns"], final["war_turns"]) == ([12, 20, 22], [12, 22])

    def test_austerlitz_the_purse_butterfly(self):
        # Prussia without the 2,610 gold re-times the league war she opens on
        # Austria at turn 24: it runs to the window's end instead of closing
        # at 33 — Saxony survives, Switzerland falls.
        control = _record(self.CONTROL)["seeds"]["austerlitz"]["signature"]
        final = _record(self.FINAL)["seeds"]["austerlitz"]["signature"]
        assert control["eliminations"] == [[14, "KingdomOfItaly"], [39, "Saxony"]]
        assert final["eliminations"] == [[14, "KingdomOfItaly"], [33, "Switzerland"]]

    def test_the_debt_reported_honestly(self):
        # 208 → 228: the rise is austerlitz's alone (the longer league war,
        # Prussia's captures off-aim 5 → 17); marengo falls; eight seeds hold.
        control, final = _record(self.CENSUS_CONTROL), _record(self.CENSUS)
        moved = {seed: (control["seeds"][seed]["captures_outside_aim"],
                        final["seeds"][seed]["captures_outside_aim"])
                 for seed in control["seeds"]
                 if control["seeds"][seed]["captures_outside_aim"]
                 != final["seeds"][seed]["captures_outside_aim"]}
        assert moved == {"austerlitz": (34, 57), "marengo": (20, 17)}
        assert (control["totals"]["captures_outside_aim"],
                final["totals"]["captures_outside_aim"]) == (208, 228)
