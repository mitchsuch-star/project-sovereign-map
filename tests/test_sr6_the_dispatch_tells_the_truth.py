"""SR-6a "The dispatch pass" (Score Finish Step 2, October 2, 2026) — the
intelligence surfaces.

AAR-5: the dispatch placed a man at the province he LEFT the morning after a
visible advance. `RegionIntel.refresh` early-returns on a lower visibility
without touching the snapshot, so a province labelled FULL yesterday keeps
the label (decay starts at three turns) over a snapshot frozen before the
man moved; the province he moved into can be FULL with an EMPTY snapshot
(the battle refresh). Measured turn 6 of the ambient run: Milan FULL/t5
holding Archduke Charles at 35,513, Munich FULL/t5 holding nobody, Charles
standing at Munich with 28,384 — the dispatch and the Ledger said Milan.
The rule now (`intel_surfaces`): a FULL province is read LIVE, the map's
own rule; a snapshot is kept only where the fog is real.

AAR4-X2: `status` left out a FULL province held by a garrison alone; the
Ledger and the dispatch read marshals only. Every surface names a known
enemy garrison through `garrison_report.garrison_view`.

AAR24-X4: the dispatch dropped a `garrison_regen` event whose nation was
not the player's. A KNOWN enemy garrison's regrowth rides the dispatch,
fog-honestly.
"""
import contextlib
import io
from pathlib import Path

import pytest

from backend import intel_report
from backend.game_logic import dispatch, intel_surfaces as SURF, ledger
from backend.models.intel import FULL, PARTIAL, STALE, UNKNOWN
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCEN = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
           / "europe_1805.json")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture
def world():
    with _quiet():
        return WorldState.from_scenario(SCEN)


def _set_full(world, region, marshals, turn, source="scout"):
    world.get_region_intel(region).refresh(
        FULL, source, turn, marshals=marshals,
        total_strength=sum(int(m.get("strength", 0)) for m in marshals))


def _stage_the_measured_board(world):
    """Milan FULL/t-1 with Charles frozen in its snapshot; Munich FULL/t-1
    with an EMPTY snapshot; Charles standing at Munich (the turn-6 board)."""
    charles = world.marshals["ArchdukeCharles"]
    charles.location = "Munich"
    charles.strength = 28384
    world._build_marshal_index()
    prior = int(world.current_turn) - 1
    _set_full(world, "Milan", [{"name": "ArchdukeCharles", "nation": "Austria",
                                "strength": 35513}], prior)
    _set_full(world, "Munich", [], prior, source="battle")
    return charles


def _rows_for(rows, name):
    return [r for r in rows if r["name"].replace(" ", "") == name.replace(" ", "")]


class TestAFullProvinceIsReadLive:
    """AAR-5 — the dispatch, the Ledger and the status report place the man
    where he stands."""

    def test_the_dispatch_row(self, world):
        _stage_the_measured_board(world)
        rows = _rows_for(dispatch._build_intelligence(world, "France"), "ArchdukeCharles")
        assert len(rows) == 1, rows
        row = rows[0]
        assert row["location"] == "Munich" and row["visibility"] == FULL
        assert row["strength_display"] == "28,384"
        assert row["intel_turn"] == int(world.current_turn)

    def test_the_ledger_row(self, world):
        _stage_the_measured_board(world)
        rows = [r for r in ledger._build_intel(world, "France")["known_enemies"]
                if r.get("roster_name") == "ArchdukeCharles"]
        assert len(rows) == 1 and rows[0]["location"] == "Munich", rows
        assert rows[0]["strength_display"] == "28,384"
        assert rows[0]["name"] == "Archduke Charles"     # NPC-12: the tab prints the display name"

    def test_the_status_report_names_him_once(self, world):
        _stage_the_measured_board(world)
        report = intel_report.generate_intel_report(world)
        text = report["report_text"]
        assert "Archduke Charles (Austria): 28,384 troops at Munich" in text
        assert "near Milan" not in text
        recent = [r for r in report["recent_reports"]
                  if any(m.get("name") == "ArchdukeCharles" for m in r.get("known_marshals", []))]
        assert not recent, recent

    def test_a_partial_row_never_outranks_a_live_one(self, world):
        charles = _stage_the_measured_board(world)
        # A PARTIAL snapshot at the old province, stamped NEWER than the live
        # read's turn — the defect's second form (a "[partial]" row leading).
        milan = world.get_region_intel("Milan")
        milan.visibility = PARTIAL
        milan.known_marshals = [{"name": "ArchdukeCharles", "nation": "Austria",
                                 "band": "substantial force"}]
        milan.last_updated_turn = int(world.current_turn) + 1
        rows = _rows_for(dispatch._build_intelligence(world, "France"), charles.name)
        assert len(rows) == 1 and rows[0]["location"] == "Munich", rows

    def test_the_fog_keeps_a_real_snapshot(self, world):
        """A man seen at PARTIAL and not standing in any FULL province is
        still reported where he was seen — the fog is honest, not blind."""
        kutuzov = world.marshals["Kutuzov"]
        where = kutuzov.location
        intel = world.get_region_intel(where)
        intel.visibility = PARTIAL
        intel.known_marshals = [{"name": "Kutuzov", "nation": "Russia",
                                 "band": "large force"}]
        intel.last_updated_turn = int(world.current_turn)
        rows = _rows_for(dispatch._build_intelligence(world, "France"), "Kutuzov")
        assert rows and rows[0]["location"] == where and rows[0]["visibility"] == PARTIAL

    def test_lever_down_reproduces_the_row(self, world, monkeypatch):
        monkeypatch.setattr(SURF, "THE_SIGHTING_IS_LIVE", False)
        monkeypatch.setattr(SURF, "THE_SURFACES_NAME_THE_GARRISON", False)
        _stage_the_measured_board(world)
        rows = _rows_for(dispatch._build_intelligence(world, "France"), "ArchdukeCharles")
        assert rows and rows[0]["location"] == "Milan", rows
        rows = [r for r in ledger._build_intel(world, "France")["known_enemies"]
                if r["name"] == "ArchdukeCharles"]
        assert rows and rows[0]["location"] == "Milan"   # the lever-down row keeps the raw key"

    def test_no_row_for_a_prisoner_or_an_empty_corps(self, world):
        charles = _stage_the_measured_board(world)
        charles.captured_by = "France"
        assert not _rows_for(dispatch._build_intelligence(world, "France"), charles.name)
        charles.captured_by = ""
        charles.strength = 0
        assert not _rows_for(dispatch._build_intelligence(world, "France"), charles.name)


def _garrison_rows(rows):
    return [r for r in rows if r.get("kind") == SURF.GARRISON_ROW_KIND]


class TestEverySurfaceNamesTheGarrison:
    """AAR4-X2 — a garrison-only FULL province reaches every surface."""

    def test_vienna_at_full_on_the_dispatch_and_the_ledger(self, world):
        assert world.is_at_war("France", "Austria")
        vienna = world.regions["Vienna"]
        assert not [m for m in world.get_marshals_in_region("Vienna") if m.nation != "France"]
        _set_full(world, "Vienna", [], int(world.current_turn))
        rows = _garrison_rows(dispatch._build_intelligence(world, "France"))
        row = next(r for r in rows if r["location"] == "Vienna")
        assert row["strength_display"] == f"garrison of {int(vienna.garrison_strength):,}"
        assert row["visibility"] == FULL and row["nation"] == "Austria"
        lrows = [r for r in ledger._build_intel(world, "France")["known_enemies"]
                 if r.get("kind") == SURF.GARRISON_ROW_KIND and r["location"] == "Vienna"]
        assert lrows and lrows[0]["strength_display"] == row["strength_display"]

    def test_a_garrison_is_not_a_marshal_in_the_nation_summary(self, world):
        _set_full(world, "Vienna", [], int(world.current_turn))
        intel = ledger._build_intel(world, "France")
        austria = next(n for n in intel["nation_summaries"] if n["nation"] == "Austria")
        marshals = [r for r in intel["known_enemies"]
                    if r["nation"] == "Austria" and not r.get("kind")]
        assert austria["known_marshals"] == len(marshals)

    def test_the_status_report(self, world):
        _set_full(world, "Vienna", [], int(world.current_turn))
        report = intel_report.generate_intel_report(world)
        n = int(world.regions["Vienna"].garrison_strength)
        assert f"Vienna (Austria): garrison of {n:,} holds the works" in report["report_text"]
        confirmed = next(r for r in report["confirmed"] if r["region"] == "Vienna")
        assert confirmed["garrison"]["strength"] == n

    def test_the_band_below_full(self, world):
        intel = world.get_region_intel("Vienna")
        intel.visibility = PARTIAL
        intel.last_updated_turn = int(world.current_turn)
        rows = _garrison_rows(dispatch._build_intelligence(world, "France"))
        row = next(r for r in rows if r["location"] == "Vienna")
        assert row["strength_display"].startswith("garrison — ")
        assert "," not in row["strength_display"], "the band, never the figure"
        assert row["visibility"] == PARTIAL
        text = intel_report.generate_intel_report(world)["report_text"]
        assert "Vienna (Austria): garrison — " in text

    def test_the_fog_hides_it_and_peace_courts_never_list(self, world):
        world.get_region_intel("Vienna").visibility = UNKNOWN
        assert not [r for r in _garrison_rows(dispatch._build_intelligence(world, "France"))
                    if r["location"] == "Vienna"]
        # Prussia is at peace with France at the boot: Berlin's garrison is
        # no enemy, at any visibility.
        assert not world.is_at_war("France", "Prussia")
        _set_full(world, "Berlin", [], int(world.current_turn))
        assert not [r for r in _garrison_rows(dispatch._build_intelligence(world, "France"))
                    if r["location"] == "Berlin"]
        # Our own capital's garrison is ours, not intelligence.
        assert not [r for r in _garrison_rows(dispatch._build_intelligence(world, "France"))
                    if r["location"] == "Paris"]

    def test_lever_down_lists_no_garrison(self, world, monkeypatch):
        monkeypatch.setattr(SURF, "THE_SURFACES_NAME_THE_GARRISON", False)
        _set_full(world, "Vienna", [], int(world.current_turn))
        assert not _garrison_rows(dispatch._build_intelligence(world, "France"))
        assert not [r for r in ledger._build_intel(world, "France")["known_enemies"]
                    if r.get("kind")]
        assert "holds the works" not in intel_report.generate_intel_report(world)["report_text"]


def _regen_event(region="Vienna", nation="Austria", old=23000, new=25000):
    return {"type": "garrison_regen", "region": region, "nation": nation,
            "old_strength": old, "new_strength": new,
            "message": f"Garrison at {region} reinforced: {old:,} -> {new:,}"}


class TestAKnownEnemyGarrisonRegrowsAloud:
    """AAR24-X4 — the regrowth rides the dispatch, fog-honestly."""

    def test_at_full_the_figures(self, world):
        _set_full(world, "Vienna", [], int(world.current_turn))
        rows = dispatch._build_turn_events([_regen_event()], "France", world=world)
        assert [r["message"] for r in rows] == \
            ["Vienna's garrison regains 2,000: 23,000 -> 25,000."], rows
        assert rows[0]["type"] == "garrison_regen"

    def test_at_partial_the_band(self, world):
        intel = world.get_region_intel("Vienna")
        intel.visibility = PARTIAL
        rows = dispatch._build_turn_events([_regen_event()], "France", world=world)
        assert len(rows) == 1 and rows[0]["message"].startswith("Vienna's garrison regrows — ")
        assert "25,000" not in rows[0]["message"]

    def test_the_fog_and_the_peace_drop_it(self, world):
        world.get_region_intel("Vienna").visibility = UNKNOWN
        assert dispatch._build_turn_events([_regen_event()], "France", world=world) == []
        _set_full(world, "Berlin", [], int(world.current_turn))
        assert dispatch._build_turn_events(
            [_regen_event("Berlin", "Prussia")], "France", world=world) == []

    def test_without_the_world_or_the_lever_the_old_drop(self, world, monkeypatch):
        _set_full(world, "Vienna", [], int(world.current_turn))
        assert dispatch._build_turn_events([_regen_event()], "France") == []
        monkeypatch.setattr(SURF, "THE_ENEMY_WORKS_REGROW_ALOUD", False)
        assert dispatch._build_turn_events([_regen_event()], "France", world=world) == []

    def test_it_rides_the_morning_dispatch(self, world):
        _set_full(world, "Vienna", [], int(world.current_turn))
        with _quiet():
            d = dispatch.build_morning_dispatch(world, tactical_events=[_regen_event()])
        assert any("Vienna's garrison regains 2,000" in e["message"] for e in d["turn_events"])


# ═══════════════════════════════════════════════════════════════════════════
# The headline classes (NPC-14 / NPC-15 / NPC-27 / NPC-D1 / RS-D2 / RS-17)
# ═══════════════════════════════════════════════════════════════════════════

def _captured(world, region, captor, prev="France", turn=None):
    world.log_event({"type": "region_captured", "region": region,
                     "captured_by": captor, "captured_from": prev,
                     "method": "secure",
                     "turn": int(turn if turn is not None else world.current_turn)})


def _headline(world, record=True):
    with _quiet():
        return dispatch._build_headline(world, "France", record=record) or {}



def _raw_candidates(world):
    """Every candidate dict the builder manufactures this morning (weights
    as ranked, the yields applied) — read off the selector's own argument."""
    seen = []

    def fake_select(w, cands, record=True):
        seen.extend(dict(c) for c in cands)
        return {"class": cands[0]["class"], "weight": 0, "text": "", "sub_beats": []}
    import backend.game_logic.dispatch as D
    original = D._select_headline
    D._select_headline = fake_select
    try:
        with _quiet():
            D._build_headline(world, "France", record=False)
    finally:
        D._select_headline = original
    return seen


def _candidates(world):
    """Every candidate class the builder manufactures this morning."""
    seen = []
    real_add = None

    def fake_select(w, cands, record=True):
        seen.extend(c["class"] for c in cands)
        return {"class": cands[0]["class"], "weight": 0, "text": "", "sub_beats": []}
    import backend.game_logic.dispatch as D
    original = D._select_headline
    D._select_headline = fake_select
    try:
        with _quiet():
            D._build_headline(w := world, "France", record=False)
    finally:
        D._select_headline = original
    return seen


class TestTheFallenProvinceNamesItsCaptor:
    """NPC-15."""

    def test_the_sentence(self, world):
        world.regions["Normandy"].controller = "Britain"
        _captured(world, "Normandy", "Britain")
        head = _headline(world)
        assert head["class"] == "home_captured"
        assert head["text"].startswith("Sire — Normandy has fallen to Britain. "), head["text"]

    def test_lever_down_is_the_old_sentence(self, world, monkeypatch):
        monkeypatch.setattr(dispatch, "THE_FALLEN_PROVINCE_NAMES_ITS_CAPTOR", False)
        world.regions["Normandy"].controller = "Britain"
        _captured(world, "Normandy", "Britain")
        head = _headline(world)
        assert head["text"].startswith("Sire — Normandy has fallen. Enemy colours"), head["text"]

    def test_the_capital_keeps_its_own_sentence(self, world):
        world.regions["Paris"].controller = "Britain"
        _captured(world, "Paris", "Britain")
        head = _headline(world)
        assert head["class"] == "capital_lost" and "Paris HAS FALLEN" in head["text"]


class TestTheFallenHomelandStandsOnThePage:
    """NPC-14 — the occupation is a STATE, told until it is retaken."""

    def test_the_morning_after_the_loss(self, world):
        world.regions["Normandy"].controller = "Britain"
        _captured(world, "Normandy", "Britain")
        world.current_turn += 3   # the loss leaves the two-turn window
        # No fresh capture in the window: the standing class speaks.
        head = _headline(world)
        assert head["class"] == "homeland_occupied", head
        assert head["text"] == ("Sire — Normandy lies in enemy hands. "
                                "Britain holds it."), head["text"]

    def test_silent_on_the_morning_the_loss_is_news(self, world):
        world.regions["Normandy"].controller = "Britain"
        _captured(world, "Normandy", "Britain")
        assert "homeland_occupied" not in _candidates(world)
        assert "home_captured" in _candidates(world)

    def test_the_capital_leads_the_list_and_the_holders_are_named(self, world):
        for region, holder in (("Normandy", "Britain"), ("Paris", "Austria"),
                               ("Picardy", "Britain"), ("Artois", "Britain")):
            world.regions[region].controller = holder
        head = _headline(world)
        assert head["class"] == "homeland_occupied"
        assert head["text"] == ("Sire — Paris, Artois and Normandy and 1 more lie in "
                                "enemy hands — the capital among them. "
                                "Austria and Britain hold them."), head["text"]

    def test_it_rides_the_ladder_and_yields_like_a_standing_class(self, world):
        world.regions["Normandy"].controller = "Britain"
        texts = [_headline(world)["text"] for _ in range(4)]
        assert texts[0] == texts[1]
        assert "turns now with Normandy in enemy hands" in texts[2], texts
        assert "the enemy has held Normandy" in texts[3], texts
        assert "homeland_occupied" in dispatch.STANDING_HEADLINE_CLASSES

    def test_thrice_stated_it_yields_the_lead_and_stays_a_sub_beat(self, world):
        """The Step 2 exit's own reading: at 81 the occupation led 6 of 9
        mornings on the OP arm and buried the first erosion notice (55).
        After HOMELAND_STATEMENTS statements of the same set it ranks at
        HOMELAND_YIELDED_WEIGHT — on the page, never the lead; a changed
        set is news again."""
        # The blessed number is pinned as a LITERAL — a pin that reads the
        # constant it exists to pin survives any value of it (the sweep's
        # lesson, Oct 2 2026: HOMELAND_STATEMENTS = 300 was INERT).
        assert dispatch.HOMELAND_STATEMENTS == 3
        assert dispatch.HOMELAND_YIELDED_WEIGHT == 40
        world.regions["Normandy"].controller = "Britain"
        for _ in range(2):
            assert _headline(world)["class"] == "homeland_occupied"
        # Twice stated, it has NOT yielded: the producer's own candidate
        # keeps its full weight through the selector's yield.
        two = dict(world.headline_lead_memory["homeland_said"])
        assert two == {"key": "Normandy", "count": 2}, two
        kept, _ = dispatch._homeland_yields(
            [{"class": "homeland_occupied", "weight": 81, "text": "",
              "fields": {"occupied_key": "Normandy"}}], two)
        assert kept[0]["weight"] == 81
        assert _headline(world)["class"] == "homeland_occupied"
        said = world.headline_lead_memory.get("homeland_said")
        assert said == {"key": "Normandy", "count": 3}, said
        # A mid-weight piece of news now outranks it; the occupation rides
        # as a sub-beat.
        world.log_event({"type": "marshal_wounded", "marshal": "Lannes",
                         "nation": "France", "location": "Lorraine", "turns": 3})
        # The yield is applied inside the selector, before the ranking.
        cands = {c["class"]: c for c in _raw_candidates(world)}
        assert cands["homeland_occupied"]["weight"] == dispatch.HEADLINE_WEIGHTS["homeland_occupied"]
        yielded, _ = dispatch._homeland_yields([dict(cands["homeland_occupied"])], dict(said))
        assert yielded[0]["weight"] == dispatch.HOMELAND_YIELDED_WEIGHT
        head = _headline(world)
        assert head["class"] != "homeland_occupied", head
        assert any("Normandy" in b for b in head["sub_beats"]), head
        # The set changes: Picardy falls too — the count resets and it leads
        # (the wound has left the two-turn window by then).
        world.current_turn += 2
        world.regions["Picardy"].controller = "Britain"
        head = _headline(world)
        assert head["class"] == "homeland_occupied", head
        assert world.headline_lead_memory["homeland_said"] == {"key": "Normandy|Picardy", "count": 1}

    def test_lever_down_never_yields(self, world, monkeypatch):
        monkeypatch.setattr(dispatch, "THE_FALLEN_HOMELAND_STANDS_ON_THE_PAGE", False)
        world.regions["Normandy"].controller = "Britain"
        for _ in range(dispatch.HOMELAND_STATEMENTS + 1):
            _headline(world)
        assert "homeland_said" not in (world.headline_lead_memory or {})

    def test_retaken_means_silence(self, world):
        world.regions["Normandy"].controller = "Britain"
        assert _headline(world)["class"] == "homeland_occupied"
        world.regions["Normandy"].controller = "France"
        assert "homeland_occupied" not in _candidates(world)

    def test_an_ally_or_a_satellite_holding_it_is_not_an_occupation(self, world):
        world.regions["Normandy"].controller = "Spain"
        assert world.are_allies("France", "Spain") or "Spain" in (world.vassals or {})
        assert "homeland_occupied" not in _candidates(world)

    def test_lever_down_forgets_the_province(self, world, monkeypatch):
        monkeypatch.setattr(dispatch, "THE_FALLEN_HOMELAND_STANDS_ON_THE_PAGE", False)
        world.regions["Normandy"].controller = "Britain"
        assert "homeland_occupied" not in _candidates(world)

    def test_a_collapsed_realm_has_one_voice(self, world):
        """IQ-2's one-source rule, found by the full suite (Oct 2 2026): on a
        France reduced to Paris, `empire_reduced` owns the page and the
        occupied-homeland class is SILENT — the two would state one fact
        twice, and the second voice took the hand-back from the money rung
        (`test_iq2_collapse_dispatch.py::TestBerthierCloses`). It returns
        the morning the realm is no longer collapsed."""
        for name in list(world.get_nation_regions("France")):
            if name != "Paris":
                world.regions[name].controller = "Austria"
        world.invalidate_active_nations_cache()
        seen = _candidates(world)
        assert "empire_reduced" in seen and "homeland_occupied" not in seen, seen
        world.regions["Normandy"].controller = "France"
        world.invalidate_active_nations_cache()
        seen = _candidates(world)
        assert "empire_reduced" not in seen and "homeland_occupied" in seen, seen


class TestTheBriefingShowsTheGrip:
    """NPC-27 / NPC-D1 — the number the game acts on, beside the one that
    did not move; the Presence at its live strength."""

    def _situation(self, world):
        with _quiet():
            return dispatch._build_situation(world, "France")

    def test_the_boot_line_is_byte_identical(self, world):
        s = self._situation(world)
        assert s["authority"] == 100 and s["authority_label"] == "Strong"
        assert s["imperial_grip"] == 100 and s["grip_label"] == "firm"
        assert s["aura_pct"] == 10

    def test_a_lost_capital_shows_in_the_label(self, world):
        from backend.models.authority import get_imperial_grip
        world.regions["Paris"].controller = "Britain"
        world.invalidate_active_nations_cache()
        grip = get_imperial_grip(world, "France")
        assert grip < 100
        s = self._situation(world)
        assert s["authority"] == 100
        assert s["imperial_grip"] == grip
        assert s["authority_label"] == (
            f"Strong at court; the Empire's grip {grip} ({s['grip_label']}); "
            f"the Presence at +{s['aura_pct']}%"), s["authority_label"]
        assert 0 <= s["aura_pct"] < 10

    def test_lever_down_is_the_raw_number_alone(self, world, monkeypatch):
        monkeypatch.setattr(dispatch, "THE_BRIEFING_SHOWS_THE_GRIP", False)
        world.regions["Paris"].controller = "Britain"
        world.invalidate_active_nations_cache()
        s = self._situation(world)
        assert s["authority_label"] == "Strong" and "imperial_grip" not in s

    def test_the_aura_beat_fires_on_a_band_crossing_and_once(self, world):
        _headline(world)                       # the first observation records
        assert world.headline_lead_memory.get("aura_band") == "full"
        world.regions["Paris"].controller = "Britain"
        world.invalidate_active_nations_cache()
        head = _headline(world)
        assert head["class"] == "aura_dimmed", head
        assert "the Emperor's star dims" in head["text"]
        assert "gives +" in head["text"] and "% this morning" in head["text"]
        assert "aura_dimmed" not in _candidates(world), "told once per crossing"

    def test_the_aura_beat_rises_again(self, world):
        _headline(world)
        world.regions["Paris"].controller = "Britain"
        world.invalidate_active_nations_cache()
        _headline(world)
        world.regions["Paris"].controller = "France"
        world.invalidate_active_nations_cache()
        head = _headline(world)
        assert head["class"] == "aura_dimmed" and "burns full again" in head["text"]

    def test_no_sovereign_no_beat(self, world):
        _headline(world)
        world.marshals["Napoleon"].captured_by = "Austria"
        world.regions["Paris"].controller = "Britain"
        world.invalidate_active_nations_cache()
        assert "aura_dimmed" not in _candidates(world)

    def test_the_boot_briefing_records_without_speaking(self, world):
        head = _headline(world, record=False)
        assert head.get("class") != "aura_dimmed"
        assert world.headline_lead_memory.get("aura_band") is None

    def test_lever_down_has_no_beat(self, world, monkeypatch):
        monkeypatch.setattr(dispatch, "THE_AURA_HAS_ITS_BEAT", False)
        _headline(world)
        world.regions["Paris"].controller = "Britain"
        world.invalidate_active_nations_cache()
        assert "aura_dimmed" not in _candidates(world)

    def test_the_card_shows_the_presence_today(self, world):
        from backend.game_logic import marshal_overview as MO
        card = next(c for c in MO.build_marshal_overview(world) if c["name"] == "Napoleon")
        assert "Today it stands at" not in card["ability_effect"]
        world.regions["Paris"].controller = "Britain"
        world.invalidate_active_nations_cache()
        card = next(c for c in MO.build_marshal_overview(world) if c["name"] == "Napoleon")
        assert "Today it stands at +" in card["ability_effect"]
        assert "his star dims" in card["ability_effect"]

    def test_the_battle_row_clause_is_already_there(self):
        """NPC-D1's battle-row half landed with NP-V; pinned, not rebuilt."""
        src = (REPO / "backend" / "game_logic" / "battle_report.py").read_text(encoding="utf-8")
        assert "(his star dims)" in src


def _peace_with_the_levy_open(world):
    """RS-D2's shape: France at peace, the levy open, nothing else to say."""
    from backend.game_logic import diplomacy as D
    for nation in list(world.get_nations_at_war_with("France") or []):
        D.set_diplomatic_state(world, "France", nation, "PEACE", "test")
    world.event_log.clear()
    from backend.commands.economy_executor import get_levy_status
    levy = get_levy_status(world, "France")
    if not levy["open"]:
        # Open the gate: cut the establishment below the ordinance, and
        # stand a corps at the depot (the levy's own PT-H4 gate).
        for m in world.marshals.values():
            if m.nation == "France" and m.name != "Napoleon":
                m.strength = 5000
        world.marshals["Ney"].location = "Paris"
        world._build_marshal_index()
        levy = get_levy_status(world, "France")
    assert levy["open"], levy
    world.headline_lead_memory = {}
    return levy


class TestTheLevyYieldsOnceStated:
    """RS-D2."""

    def test_three_statements_then_the_ledger(self, world):
        _peace_with_the_levy_open(world)
        classes = [_headline(world).get("class") for _ in range(6)]
        assert classes[:3] == ["levy_open"] * 3, classes
        assert classes[3:] == ["quiet_morning"] * 3, classes

    def test_it_leads_at_most_once_beside_other_news(self, world):
        _peace_with_the_levy_open(world)
        leads, beats = 0, 0
        for _ in range(6):
            # A standing rival on the page every morning: a supply strain
            # would do; a fallen homeland province is simpler to stage.
            world.regions["Normandy"].controller = "Britain"
            head = _headline(world)
            leads += head["class"] == "levy_open"
            beats += sum("ordinance" in b or "levy" in b.lower() for b in head["sub_beats"])
        assert leads <= dispatch.LEVY_LEAD_MAX, (leads, beats)
        assert leads + beats <= dispatch.LEVY_STATEMENTS, (leads, beats)

    def test_a_recruitment_restates_it(self, world):
        levy = _peace_with_the_levy_open(world)
        for _ in range(4):
            _headline(world)
        assert _headline(world)["class"] == "quiet_morning"
        # The headroom moves by more than a fifth: the offer is news again.
        ney = world.marshals["Ney"]
        ney.strength += int(levy["headroom"] * 0.5)
        assert _headline(world)["class"] == "levy_open"

    def test_a_new_war_restates_it(self, world):
        _peace_with_the_levy_open(world)
        for _ in range(4):
            _headline(world)
        assert _headline(world)["class"] == "quiet_morning"
        from backend.game_logic import diplomacy as D
        D.set_diplomatic_state(world, "France", "Austria", "WAR", "test")
        assert _headline(world)["class"] == "levy_open"

    def test_the_gate_closing_and_reopening_restates_it(self, world):
        _peace_with_the_levy_open(world)
        for _ in range(4):
            _headline(world)
        assert _headline(world)["class"] == "quiet_morning"
        memory = dict(world.headline_lead_memory)
        # Shut the gate for a morning (no levy candidate), then open it.
        import backend.game_logic.dispatch as D
        original = D.get_levy_status if hasattr(D, "get_levy_status") else None
        from backend.commands import economy_executor as EE
        real = EE.get_levy_status
        EE.get_levy_status = lambda w, n=None: dict(real(w, n), open=False)
        try:
            assert _headline(world).get("class") != "levy_open"
        finally:
            EE.get_levy_status = real
        assert world.headline_lead_memory.get("levy_said") in ({}, None)
        assert _headline(world)["class"] == "levy_open"

    def test_lever_down_nags_forever(self, world, monkeypatch):
        monkeypatch.setattr(dispatch, "THE_LEVY_YIELDS_ONCE_STATED", False)
        _peace_with_the_levy_open(world)
        classes = [_headline(world).get("class") for _ in range(6)]
        assert classes == ["levy_open"] * 6, classes

    def test_the_memory_rides_the_existing_field(self, world):
        _peace_with_the_levy_open(world)
        _headline(world)
        said = world.headline_lead_memory["levy_said"]
        assert said["count"] == 1 and {"headroom", "price", "wars"} <= set(said)
        d = world.to_dict()
        assert d["headline_lead_memory"]["levy_said"] == said


def _open_the_gate(world):
    """RS-17's shape: the count met, the capital held, no sitting."""
    from backend.game_logic import congress, game_end
    assert congress.armed(world)
    need = congress.hold_titled(world)
    have = congress.titled(world)["count"]
    # Title enemy provinces BY TREATY until the count is met (a conquest
    # titles only after its quiet clock; a treaty titles at the signature).
    for region_name, region in sorted(world.regions.items()):
        if have >= need:
            break
        if region.controller in ("France",) or region.controller in (world.vassals or {}):
            continue
        prev = region.controller
        region.controller = "France"
        game_end.record_province_title(world, region_name, game_end.TITLE_TREATY,
                                       prev, "France")
        have += 1
    world.invalidate_active_nations_cache()
    assert congress.titled(world)["count"] >= need
    return need


class TestTheSummonableGateIsNews:
    """RS-17 (the headline half)."""

    def test_the_morning_the_gate_opens(self, world):
        need = _open_the_gate(world)
        head = _headline(world)
        assert head["class"] == "congress_summonable", head
        assert "THE CONGRESS OF PARIS MAY BE SUMMONED" in head["text"]
        assert f"of {need} titled provinces" in head["text"]
        assert "Paris is ours" in head["text"]
        assert "summon the congress" in head["text"]
        assert world.congress.get("summonable_told", {}).get("turn") == int(world.current_turn)

    def test_the_terms_beneath_it(self, world):
        _open_the_gate(world)
        classes = _candidates(world)
        assert "congress_summonable" in classes
        assert "congress_summonable_term" in classes, classes

    def test_told_once_per_opening(self, world):
        _open_the_gate(world)
        assert _headline(world)["class"] == "congress_summonable"
        assert "congress_summonable" not in _candidates(world)
        # The count falls below the gate: the latch clears; it re-opens: news again.
        from backend.game_logic import congress
        titled = congress.titled(world)["titled"]
        enemy = [r for r in titled if r not in world.nation_starting_regions.get("France", [])]
        for region_name in enemy[:3]:
            world.regions[region_name].controller = "Austria"
        world.invalidate_active_nations_cache()
        assert congress.titled(world)["count"] < congress.hold_titled(world)
        assert "congress_summonable" not in _candidates(world)
        _headline(world)
        assert "summonable_told" not in world.congress
        for region_name in enemy[:3]:
            world.regions[region_name].controller = "France"
        world.invalidate_active_nations_cache()
        assert _headline(world)["class"] == "congress_summonable"

    def test_the_boot_briefing_latches_nothing(self, world):
        _open_the_gate(world)
        assert _headline(world, record=False)["class"] == "congress_summonable"
        # A world that never summoned keeps `congress is None` (the summons
        # pins read it); the boot briefing creates no store at all.
        assert "summonable_told" not in (world.congress or {})

    def test_lever_down_is_silent(self, world, monkeypatch):
        monkeypatch.setattr(dispatch, "THE_SUMMONABLE_GATE_IS_NEWS", False)
        _open_the_gate(world)
        assert "congress_summonable" not in _candidates(world)

    def test_the_weight_sits_where_the_row_asked(self):
        w = dispatch.HEADLINE_WEIGHTS
        assert w["own_mauled"] < w["congress_summonable"] < w["congress_contested"]
        assert w["congress_summonable_term"] < w["congress_warning"]
