"""T2-6 — the casting band: the seed casts an understudy
(`AI_INTENT_SPEC.md` §3.8.2's last ruled band; `DYNAMISM_SPEC.md` §2
Tier 2 — "the lawful lucky nation"; November 8, 2026; the rules
`SYSTEMS_REFERENCE.md` §192).

Two halves, measured apart (the two dated records):

THE DECKS (content — `_dy_signature_t2_6a_decks_2026_11_08.json`):
Bavaria's `the_tyrol` (acquire, ["Tyrol"]) is deliberately BOOT-LIVE —
Bavaria boots at war with Austria and Tyrol is the actual Pressburg
war aim; Naples' deck is guard-then-claim in Denmark's shape (the
September Treaty of 1805, then the Roman Expedition of '98, speaking
only at war). Spain alone remains deckless among armed courts (the
S14k-3 residue; the strict xfail stands on her).

THE CASTING (variance — `_dy_signature_t2_6_2026_11_08.json`): each
non-historical seed casts ONE understudy from (Saxony, Bavaria,
Denmark, Naples) — its first ACQUIRE boots at its deck's head (a
guard ahead of it steps behind: the cast court has set its posture
aside, which is what being cast MEANS; satisfaction restores it) and
the bold dial (8, band [4, 12]) replaces its lean in the statecraft
overlay. `historical` casts NOBODY, structurally. Resolved and
stripped at boot (`campaign_variance._resolve_casting`); no seam
(variance machinery, the T2-B precedent), no new world field, no new
log type.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic.agendas import (  # noqa: E402
    _active_guard_map,
    get_active_agenda,
    get_agenda_military_targets,
    region_coveted,
)
from backend.game_logic.campaign_variance import cast_understudy  # noqa: E402
from backend.modding.validator import validate_scenario  # noqa: E402
from tools.ai_v_sweep import SWEEP_SEEDS  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
SHORTLIST = ["Saxony", "Bavaria", "Denmark", "Naples"]
DIAL_BAND = (4, 12)
# Probed sample seeds, one per court (pure hash — stable forever).
CAST_SAMPLE = {"Saxony": "t26-probe-5", "Bavaria": "t26-probe-6",
               "Denmark": "t26-probe-0", "Naples": "t26-probe-2"}


def _boot(seed: str):
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed=seed)


def _view_id(world, nation: str):
    view = get_active_agenda(nation, world)
    return getattr(view, "id", None)


@pytest.fixture(scope="module")
def historical():
    return _boot("historical")


class TestTheDecks:
    def test_bavaria_is_authored_and_boot_live(self, historical):
        # The 1805 war aim, deliberately: a live want for a
        # boot-belligerent is history, not drift.
        assert [e.get("id") for e in historical.agendas["Bavaria"]] \
            == ["the_tyrol"]
        view = get_active_agenda("Bavaria", historical)
        assert view is not None and view.id == "the_tyrol"
        assert get_agenda_military_targets("Bavaria", historical) \
            == ["Tyrol"]

    def test_naples_is_guard_then_claim(self, historical):
        assert [e.get("id") for e in historical.agendas["Naples"]] \
            == ["september_treaty", "roman_expedition"]
        assert _view_id(historical, "Naples") == "september_treaty"
        # Rome is coveted — the claim is held back by order alone.
        assert region_coveted(historical, "Naples", "Rome")

    def test_the_september_treaty_prices(self, historical):
        # The real treaty's teeth: a belligerent marching on
        # Neapolitan soil is a priced violation from boot.
        assert _active_guard_map(historical).get("Naples") == "Naples"

    def test_the_naples_waterfall_at_war(self):
        world = _boot("historical")
        world.diplomatic_states[world._make_diplo_key(
            "Naples", "France")] = "WAR"
        world._agenda_cache = None
        world.invalidate_active_nations_cache()
        view = get_active_agenda("Naples", world)
        assert view is not None and view.id == "roman_expedition"
        assert get_agenda_military_targets("Naples", world) == ["Rome"]

    def test_spain_is_the_deckless_residue(self, historical):
        # The S14k-3 strict xfail stands on her alone.
        armed = ({m.nation for m in historical.marshals.values()}
                 | {n for n, rows in (historical.marshal_pool or {}).items()
                    if rows})
        deckless = sorted(n for n in armed - {historical.player_nation}
                          if not historical.agendas.get(n))
        assert deckless == ["Spain"]


class TestTheCasting:
    def test_historical_casts_nobody(self, historical):
        assert cast_understudy("historical", SHORTLIST) is None
        # And the historical boot carries the authored order and the
        # authored lean — byte-for-byte today's boards.
        assert [e.get("id") for e in historical.agendas["Denmark"]] \
            == ["neutrality_of_the_north", "scania"]
        assert historical.get_statecraft("Denmark")["weight_mod"] == 0
        assert historical.get_statecraft("Saxony")["weight_mod"] == -8

    def test_the_pick_is_deterministic_and_lawful(self):
        for seed in list(SWEEP_SEEDS) + list(CAST_SAMPLE.values()):
            first = cast_understudy(seed, SHORTLIST)
            assert first == cast_understudy(seed, SHORTLIST)
            if seed == "historical":
                assert first is None
            else:
                assert first in SHORTLIST

    def test_the_ten_seeds_casts_are_the_record(self):
        # Seeded paths, not laws — the per-seed truth, pinned: the ten
        # ambient seeds cast all FOUR courts between them.
        casts = {seed: cast_understudy(seed, SHORTLIST)
                 for seed in SWEEP_SEEDS}
        assert casts == {
            "historical": None,
            "ulm": "Bavaria", "eylau": "Bavaria",
            "austerlitz": "Denmark", "lodi": "Denmark",
            "jena": "Naples", "wagram": "Naples",
            "marengo": "Saxony", "friedland": "Saxony",
            "rivoli": "Saxony",
        }
        assert len({c for c in casts.values() if c}) == len(SHORTLIST)

    def test_a_cast_denmark_sets_the_guard_aside(self):
        # The live-first ruling's pin: the ambition leads, the guard
        # steps behind — the cast court has set its posture aside.
        world = _boot("austerlitz")
        assert [e.get("id") for e in world.agendas["Denmark"]] \
            == ["scania", "neutrality_of_the_north"]
        assert _view_id(world, "Denmark") == "scania"
        assert "Copenhagen" not in _active_guard_map(world)

    def test_a_cast_naples_marches_on_rome(self):
        world = _boot("jena")
        assert [e.get("id") for e in world.agendas["Naples"]] \
            == ["roman_expedition", "september_treaty"]
        assert _view_id(world, "Naples") == "roman_expedition"

    def test_the_dial_is_bold_and_in_band(self):
        for court, seed in CAST_SAMPLE.items():
            world = _boot(seed)
            dial = world.get_statecraft(court)["weight_mod"]
            assert DIAL_BAND[0] <= dial <= DIAL_BAND[1], (court, dial)

    def test_an_uncast_court_keeps_its_lean_and_order(self):
        # austerlitz casts Denmark; Saxony keeps her lean band's
        # resolution and Naples the authored guard-then-claim order.
        world = _boot("austerlitz")
        assert -14 <= world.get_statecraft("Saxony")["weight_mod"] <= -2
        assert [e.get("id") for e in world.agendas["Naples"]] \
            == ["september_treaty", "roman_expedition"]

    def test_a_cast_saxony_degenerates_to_the_dial(self):
        # One-entry deck: the reorder is a no-op, the dial applies.
        world = _boot("marengo")
        assert [e.get("id") for e in world.agendas["Saxony"]] \
            == ["the_wettin_crown"]
        dial = world.get_statecraft("Saxony")["weight_mod"]
        assert DIAL_BAND[0] <= dial <= DIAL_BAND[1]

    def test_satisfaction_restores_the_posture(self):
        # Cast Denmark takes Scania — the acquire goes inactive and
        # the guard resurfaces from second place.
        world = _boot("austerlitz")
        world.regions["Scania"].controller = "Denmark"
        world._agenda_cache = None
        world.invalidate_active_nations_cache()
        assert _view_id(world, "Denmark") == "neutrality_of_the_north"
        assert _active_guard_map(world).get("Copenhagen") == "Denmark"

    def test_the_cast_world_round_trips_the_save(self):
        from backend.models.world_state import WorldState
        world = _boot("austerlitz")
        back = WorldState.from_dict(
            json.loads(json.dumps(world.to_dict(), default=str)))
        assert [e.get("id") for e in back.agendas["Denmark"]] \
            == ["scania", "neutrality_of_the_north"]
        assert back.get_statecraft("Denmark")["weight_mod"] \
            == world.get_statecraft("Denmark")["weight_mod"]
        assert not hasattr(back, "casting")


class TestTheMeasure:
    """The TWO dated records (the kept-record idiom, attribution by
    tree): chain A on the decks-only tree
    (`_dy_signature_t2_6a_decks_2026_11_08.json` vs the T2-5 record —
    the CONTENT movers) and chain B on the final tree
    (`_dy_signature_t2_6_2026_11_08.json` vs A — the CASTING's own).
    The content moved every world-line, historical included (Bavaria's
    want is boot-live on every seed — 1805, not drift), with two class
    movers: Naples joins austerlitz's fight roster, Bavaria joins
    friedland's. The casting moved two of the nine cast seeds inside
    40 ambient turns — austerlitz (cast Denmark, signature only) and
    marengo (cast Saxony: she joins the fight roster and SWITZERLAND
    SURVIVES — the old T27 elimination never happens on the stirred
    board) — with historical byte-identical A-to-B (the casting's
    silence, structural). Per-seed honesty: the quiet seven casts are
    the per-seed truth, not a law; the dial bites where the board
    lets it."""

    @pytest.fixture(scope="class")
    def records(self):
        prev = json.loads(
            (REPO / "tools" / "_dy_signature_t2_5_2026_11_08.json")
            .read_text(encoding="utf-8"))
        decks = json.loads(
            (REPO / "tools" / "_dy_signature_t2_6a_decks_2026_11_08.json")
            .read_text(encoding="utf-8"))
        final = json.loads(
            (REPO / "tools" / "_dy_signature_t2_6_2026_11_08.json")
            .read_text(encoding="utf-8"))
        return prev, decks, final

    def test_the_tier_keeps_the_floor(self, records):
        prev, decks, final = records
        assert decks["story_class_count"] == 10
        assert final["story_class_count"] == 10

    def test_the_content_moved_every_world_line(self, records):
        prev, decks, _final = records
        moved = [s for s in sorted(prev["seeds"])
                 if prev["seeds"][s]["signature"]
                 != decks["seeds"][s]["signature"]]
        assert moved == sorted(prev["seeds"]), moved

    def test_the_castings_own_movers_are_the_record(self, records):
        _prev, decks, final = records
        moved = [s for s in sorted(decks["seeds"])
                 if decks["seeds"][s] != final["seeds"][s]]
        assert moved == ["austerlitz", "marengo"], moved

    def test_historical_is_byte_identical_a_to_b(self, records):
        # The casting's silence pin: historical casts nobody, and the
        # restamp fix is unreachable ambiently (no player ratifies).
        _prev, decks, final = records
        assert decks["seeds"]["historical"] == final["seeds"]["historical"]

    def test_saxony_stirs_and_switzerland_survives_on_marengo(self, records):
        _prev, decks, final = records
        a = dict(decks["seeds"]["marengo"]["story_class"])
        b = dict(final["seeds"]["marengo"]["story_class"])
        assert "Saxony" not in a["fight"] and "Saxony" in b["fight"]
        assert "Switzerland" in a["eliminations"]
        assert "Switzerland" not in b["eliminations"]


class TestTheDD1Catch:
    def test_a_ratified_twin_is_restamped_not_refused(self, historical):
        """The refreshed sweep's catch (SEED-dd1-one, A=2): a second
        Non-Aggression letter sat signable while its twin's acceptance
        moved the pair to Non-Aggression — shown signable, refused at
        the desk. The cure at the one moment staleness is born:
        ratification re-stamps the court's pending treaty letters (the
        S6 idiom — the Accept greys with the ratifier's own clause)."""
        from backend.game_logic.treaty import (
            restamp_pending_treaty_letters,
        )
        from backend.models.world_state import WorldState
        world = WorldState.from_dict(historical.to_dict())
        twin = {
            "type": "incoming_proposal", "dialogue_id": 991,
            "context": {
                "proposal_type": "non_aggression",
                "source_nation": "Denmark",
                "proposal": {"type": "non_aggression",
                             "proposer_nation": "Denmark",
                             "target_nation": "France"},
            },
            "options": [{"action": "accept_ai_proposal",
                         "label": "Accept", "enabled": True}],
        }
        world.dialogue_manager.push(twin)
        # The sibling's acceptance has moved the pair.
        world.diplomatic_states[world._make_diplo_key(
            "France", "Denmark")] = "NON_AGGRESSION"
        assert restamp_pending_treaty_letters(world, "Denmark") >= 1
        option = twin["options"][0]
        assert option.get("enabled") is False
        assert "downgrade" in str(option.get("reason") or "").lower()


class TestTheValidator:
    def _base(self):
        return json.loads(SCENARIO.read_text(encoding="utf-8"))

    def _errors(self, data):
        result = validate_scenario(data)
        return [str(e) for e in result.errors if "casting" in str(e)]

    def _warnings(self, data):
        result = validate_scenario(data)
        return [str(w) for w in result.warnings if "casting" in str(w)]

    def test_the_shipped_block_is_clean(self):
        data = self._base()
        assert self._errors(data) == []
        assert self._warnings(data) == []

    def test_a_deckless_shortlist_court_warns(self):
        # A WARNING, not an error: `from_scenario` validates the board
        # THAT BOOTS, after the S14k deck seams — a replayed pre-S14k
        # board trims the shipped shortlist's decks out from under it,
        # and the cast then stirs nobody there (history, not rot).
        data = self._base()
        data["casting"]["shortlist"] = ["Spain"]
        assert self._errors(data) == []
        assert any("stir nobody" in w for w in self._warnings(data))

    def test_an_acquireless_shortlist_court_warns(self):
        data = self._base()
        data["casting"]["shortlist"] = ["Switzerland"]  # guard-only deck
        assert self._errors(data) == []
        assert any("live-first" in w for w in self._warnings(data))

    def test_the_dial_is_required_and_clamped(self):
        data = self._base()
        del data["casting"]["weight_mod"]
        assert any("dial" in str(e) for e in self._errors(data))
        data = self._base()
        data["casting"]["weight_mod"] = 40
        assert any("within" in str(e) for e in self._errors(data))

    def test_an_unknown_key_is_an_error(self):
        data = self._base()
        data["casting"]["lucky"] = True
        assert any("Unknown key" in str(e) for e in self._errors(data))
