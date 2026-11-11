"""Tier 8 — session E (`DYNAMISM_SPEC.md` §6; the Tier-8 gate record §6a;
§2b session E; November 10, 2026). One file for Crowns & Recognition's first
half: DY-6 the crown erected and the marshal king — three rules behind their
own seams (`tests/_t3_seams.py` rows T8-CROWN, T8-KING, T8-AI).

THE CROWN (`crowns.py`, seam `a_crown_is_erected`): a crown is a
`formable_nations` template that carries a `crown` block — ONE catalogue
(the gate's Q1: the authored list keeps the historian test). Six crowns
authored for 1805 (Naples, Westphalia, Hungary, the Illyrian Provinces,
Finland, the Duchy of Milan); the Duchy of Warsaw stays a plain carve (its
duke was the King of Saxony); the first province is the seat. The crown rides the existing `create_client` term end
to end and adds its teeth at the ONE apply site: the title and the
recognition field on the client's row, the new court's boot house in the
Awakening's web (the sibling fix for every carve), the Alarm (a capital's 12
on the carver's house), the beat (`nation_formed` + `crown`; the dispatch
line `crown_erected`).

THE MARSHAL KING (seam `a_marshal_may_reign`; the gate's Q2 — both in the
pool): a marshal with laurels (glory ≥ 3 in the window, or the crown of
glory) or a prince of the Imperial house (`crowns.princes`). A crown costs
you your best sword: the marshal re-homed to the client's colours WITH HIS
CORPS, seated at the seat, off the roster and the ladder; the client's
loyalty seeded from his trust (30–95); the passed-over marshals' authored
grievance (envy toward the king, trust −5). A prince costs no sword: loyalty
50, the slight trust −8.

THE AI'S ROAD (`settlement_third_party.a_victor_erects_a_crown`; the gate's
Q3): the victor erects an authored crown out of the soil its aim peace
cedes — `ai_carvers` bound it (Russia's Finland, Austria's Milan); a
regency; the Alarm.

RECOGNITION (the gate's Q4 — the shape now, the teeth DY-7's, session F):
the `crowns.recognition` block, `withholding_courts`, the card's line.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend import campaign_log as CL  # noqa: E402
from backend.game_logic import awakening as AW  # noqa: E402
from backend.game_logic import crowns as CR  # noqa: E402
from backend.game_logic import formations as FM  # noqa: E402
from backend.game_logic import jealousy as JZ  # noqa: E402
from backend.game_logic import settlement_ratify as SR  # noqa: E402
from backend.game_logic import settlement_third_party as TP  # noqa: E402
from backend.modding.validator import validate_scenario  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
ROWS = ("T8-CROWN", "T8-KING", "T8-AI")
PLAIN = ("DuchyOfWarsaw", "Normandy", "RomanRepublic", "Ireland")
CROWNS = ("KingdomOfNaples", "Westphalia", "Hungary", "Illyria", "Finland", "DuchyOfMilan")
SCORER = "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance"


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


def _accepts(world=None, *, accepting_leader=None, **kwargs):
    return {"score": 70, "verdict": "accept", "components": {}, "component_debug": {},
            "feedback": [], "hard_stops": [], "accept_threshold": 50,
            "near_acceptable_threshold": 35, "side_pressure_score": 30, "raw_total": 70,
            "raw_total_harshness": 0.0, "direct_scores": {}, "direct_score_sources": {}}


def _laurels(world, name: str, points: int = 5) -> None:
    JZ._append_glory(world.marshals[name], world.current_turn, points)


def _naples_beaten(world):
    """France at war with Naples, Naples taken, the score decisive (the
    one-province court — "the dynasty has ceased to reign")."""
    from backend.game_logic.diplomacy import declare_war
    with _quiet():
        declare_war(world, "France", "Naples")
        world.regions["Naples"].controller = "France"
        world.invalidate_active_nations_cache()
    pair = world._make_diplo_key("France", "Naples")
    world.war_scores[pair] = 95
    world.war_start_turns[pair] = int(world.current_turn) - 6
    from backend.game_logic.settlement_helpers import _iter_active_war_instances
    return next(wid for wid, inst in _iter_active_war_instances(world)
                if "Naples" in (inst.get("defenders") or []))


def _carve(world, king: str = "", kind: str = "", tag: str = "KingdomOfNaples",
           target: str = "Naples"):
    """The bilateral carry (IGR-D's Tilsit road) — the one body every route
    applies through (`formations.apply_create_client_clause`)."""
    template = FM.get_template(world, tag)
    demand = {"type": "create_client", "from": target, "to": "France", "tag": tag,
              "provinces": FM.template_provinces(template),
              "client_display_name": FM.get_template_identity(template)["display_name"],
              "crown": CR.crown_title(template)}
    if king:
        demand.update({"king": king, "king_kind": kind, "king_display": king})
    with _quiet():
        return world._ratify_treaty({"type": "peace", "proposer_nation": "France",
                                     "target_nation": target, "sweeteners": [],
                                     "demands": [demand]})


def _russia_on_sweden(world):
    from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance
    world.current_turn = 10
    war = make_synthetic_war_instance("war_1", attackers=["Russia"], defenders=["Sweden"],
                                      attacker_leader="Russia", defender_leader="Sweden",
                                      created_turn=4)
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
    key = world._make_diplo_key("Russia", "Sweden")
    world.war_scores[key] = 30 if key.split("|")[0] == "Russia" else -30
    world.invalidate_war_instance_indexes()
    world.regions["Finland"].controller = "Russia"
    world.invalidate_active_nations_cache()
    return war


# ═══════════════════════════════════════════════════════════════════════
# The content — the gate's Q1 (ONE catalogue) and Q4 (the recognition block)
# ═══════════════════════════════════════════════════════════════════════

class TestTheContent:
    def test_the_crowns_ride_the_one_catalogue(self, world):
        assert set(world.formable_nations) == set(PLAIN) | set(CROWNS)
        assert [t for t, v in world.formable_nations.items() if CR.is_crown(v)] == list(CROWNS)
        assert CR.crown_title(world.formable_nations["KingdomOfNaples"]) == "King of Naples"
        assert CR.crown_title(world.formable_nations["Normandy"]) == ""

    def test_every_crown_is_one_courts_soil_and_the_first_province_is_the_seat(self, world):
        starting = world._starting_controllers
        for tag in CROWNS:
            provinces = FM.template_provinces(world.formable_nations[tag])
            assert provinces and all(p in world.regions for p in provinces), tag
            assert len({starting[p] for p in provinces}) == 1, (tag, provinces)
        assert FM.template_provinces(world.formable_nations["Westphalia"])[0] == "Brunswick"
        assert FM.template_provinces(world.formable_nations["Illyria"])[0] == "Carniola"

    def test_the_historian_test_the_crowns_are_the_eras(self, world):
        """No state the era could not have made: Naples (1806), Westphalia
        (1807), Hungary (the Schönbrunn proclamation, 1809), Illyria (1809),
        Finland (the Diet of Porvoo, 1809), the Duchy of Milan (the Habsburg
        duchy) — and the AI carvers are the houses that made them."""
        carvers = {t: CR.ai_carvers(world.formable_nations[t]) for t in CROWNS}
        assert carvers == {"KingdomOfNaples": ["France"], "Westphalia": ["France"], "Hungary": ["France"],
                           "Illyria": ["France"], "Finland": ["Russia"], "DuchyOfMilan": ["Austria"]}
        assert not CR.is_crown(world.formable_nations["DuchyOfWarsaw"]), "Warsaw's duke was the King of Saxony"

    def test_the_block_arms_the_princes_and_the_legitimists(self, world):
        assert CR.armed(world)
        assert CR.princes(world) == ["Joseph Bonaparte", "Louis Bonaparte", "Jerome Bonaparte"]
        assert CR.legitimists(world) == ["Austria", "Russia", "Britain"]
        assert CR.recognition_condition(world) == "beaten"
        assert sorted(world.moments) == ["awakening", "block", "crowns", "questions", "state"]

    def test_the_shipped_scenario_validates_at_its_eleven_warnings(self):
        result = validate_scenario(_scenario())
        assert result.errors == [] and len(result.warnings) == 11

    def test_the_validator_refuses_what_the_reader_tolerates(self):
        def errors_of(mutate):
            data = _scenario()
            mutate(data)
            return [str(e) for e in validate_scenario(data).errors]

        assert any("crowns.foo" in e for e in errors_of(lambda d: d["crowns"].update({"foo": 1})))
        assert any("crowns.recognition.until" in e
                   for e in errors_of(lambda d: d["crowns"]["recognition"].update({"until": "never"})))
        assert any("crowns.princes" in e
                   for e in errors_of(lambda d: d["crowns"].update({"princes": ["A"] * 7})))
        assert any("crowns.princes" in e
                   for e in errors_of(lambda d: d["crowns"].update({"princes": ["Joseph", "Joseph"]})))
        assert any("crown.title" in e for e in errors_of(
            lambda d: d["formable_nations"]["KingdomOfNaples"]["crown"].pop("title")))
        assert any("crown.ai_carvers" in e for e in errors_of(
            lambda d: d["formable_nations"]["Finland"]["crown"].update({"ai_carvers": ["Russia", "Russia"]})))
        assert any("crown.bar" in e for e in errors_of(
            lambda d: d["formable_nations"]["Finland"]["crown"].update({"bar": 1})))
        data = _scenario()
        data["formable_nations"]["Finland"]["crown"]["ai_carvers"] = ["Atlantis"]
        result = validate_scenario(data)
        assert result.errors == [] and any("Atlantis" in str(w) for w in result.warnings)
        assert CR.clean_block({"princes": ["A", "A", 3], "recognition": {"until": "never"}}) == {
            "princes": ["A"], "legitimists": [], "until": "beaten"}
        assert CR.clean_block(None) is None


# ═══════════════════════════════════════════════════════════════════════
# The store
# ═══════════════════════════════════════════════════════════════════════

class TestTheStore:
    def test_a_world_that_authors_none_writes_nothing(self):
        from backend.models.world_state import WorldState
        bare = WorldState()
        assert bare.moments == {} and not CR.armed(bare)
        assert CR.princes(bare) == [] and CR.king_candidates(bare, "France") == []
        assert CR.withholding_courts(bare, "X") == []
        assert bare.moments == {}

    def test_the_store_survives_a_save(self, world):
        from backend.models.world_state import WorldState
        data = world.to_dict()
        assert set(data) == set(WorldState().to_dict()), "no new top-level field"
        again = WorldState.from_dict(data)
        assert CR.store(again) == CR.store(world)
        assert set(again.formable_nations) == set(world.formable_nations)

    def test_a_pre_tier_8_save_gains_the_store_on_load(self, world):
        from backend.models.world_state import WorldState
        data = world.to_dict()
        data["moments"].pop(CR.STORE_KEY)
        old = WorldState.from_dict(data)
        assert not CR.armed(old)
        assert CR.backfill(old, _scenario()) is True
        assert CR.princes(old) == ["Joseph Bonaparte", "Louis Bonaparte", "Jerome Bonaparte"]
        assert CR.backfill(old, _scenario()) is False, "a store carried is never overwritten"


# ═══════════════════════════════════════════════════════════════════════
# The guided term — the table offers the throne (never typed)
# ═══════════════════════════════════════════════════════════════════════

class TestTheGuidedTerm:
    def _staged(self, world, wid):
        from backend.game_logic.settlement_preview import stage_settlement_confirm
        with patch(SCORER, side_effect=_accepts):
            staged = stage_settlement_confirm(
                world, war_id=wid, actor_nation="France", settlement_terms=None,
                covered_enemy_participants=["Naples"], selected_target_nation="Naples",
                caller_kind="player_editor", dialogue_mode="PROPOSE")
        assert staged.get("success"), staged
        return staged["diplomatic_dialogue"]

    def _carve_rows(self, dialogue):
        """The guided rows hang on `per_court_acceptance[]` (the confirm
        popup's `_per_court_row`), each court's `demand_suggestions[]`."""
        rows = []
        for court in dialogue.get("per_court_acceptance") or []:
            for s in court.get("demand_suggestions") or []:
                if s.get("clause_type") == "create_client":
                    rows.append(s)
        return rows

    def _add(self, world, dialogue, wid, **params):
        from backend.game_logic.settlement_preview import handle_settlement_dialogue_action
        with patch(SCORER, side_effect=_accepts):
            return handle_settlement_dialogue_action(
                world, action="settlement_demand_add", dialogue=dialogue,
                action_params={"action": "settlement_demand_add", "nation": "Naples",
                               "group": "demand", "clause_type": "create_client",
                               "tag": "KingdomOfNaples", "war_id": wid,
                               "draft_key": dialogue.get("draft_key"), **params})

    def test_the_king_candidates_are_the_laurelled_and_the_princes(self, world):
        assert [c["kind"] for c in CR.king_candidates(world, "France")] == ["prince"] * 3
        _laurels(world, "Murat", 5)
        _laurels(world, "Ney", 4)
        names = [c["name"] for c in CR.king_candidates(world, "France")]
        assert names == ["Murat", "Ney", "Joseph Bonaparte", "Louis Bonaparte", "Jerome Bonaparte"]
        murat = next(c for c in CR.king_candidates(world, "France") if c["name"] == "Murat")
        assert murat["label"] == "Murat — Marshal, glory 5; his corps (22,000) goes with him"
        assert CR.resolve_king(world, "France", "Soult")[2].startswith("Soult has not the laurels")
        assert CR.resolve_king(world, "France", "Napoleon")[2], "the sovereign is never crowned elsewhere"
        assert CR.resolve_king(world, "France", "") == ("", "", "")
        assert CR.king_candidates(world, "Austria") == [], "the princes are the Emperor's"

    def test_the_row_offers_the_throne_and_the_verb_stamps_the_king(self, world):
        wid = _naples_beaten(world)
        _laurels(world, "Murat", 5)
        dialogue = self._staged(world, wid)
        row = next(s for s in self._carve_rows(dialogue) if s["action_params"]["tag"] == "KingdomOfNaples")
        assert row["available"] and row["crown"] == "King of Naples"
        assert row["king_options"][:2] == ["", "Murat"]
        assert row["king_labels"][0] == "A regency — no king seated"
        assert row["terms_display"] == "a crown: King of Naples — who shall reign? ▾"
        result = self._add(world, dialogue, wid, king="Murat")
        assert result.get("success"), result
        clause = next(t for t in result["diplomatic_dialogue"]["settlement_terms"]
                      if t.get("type") == "create_client")
        assert (clause["crown"], clause["king"], clause["king_kind"]) == ("King of Naples", "Murat", "marshal")
        from backend.game_logic.settlement_actions import _demand_clause_label
        assert _demand_clause_label(clause) == "the erection of Kingdom of Naples under Murat"

    def test_the_verb_refuses_a_man_without_laurels_and_a_prince_twice(self, world):
        wid = _naples_beaten(world)
        dialogue = self._staged(world, wid)
        refused = self._add(world, dialogue, wid, king="Soult")
        assert refused.get("success") is False and refused["error"] == "crown_king_refused"
        assert refused["error_display"].startswith("Soult has not the laurels")
        joseph = self._add(world, dialogue, wid, king="Joseph Bonaparte")
        assert joseph.get("success"), joseph
        clause = next(t for t in joseph["diplomatic_dialogue"]["settlement_terms"]
                      if t.get("type") == "create_client")
        assert (clause["king"], clause["king_kind"]) == ("Joseph Bonaparte", "prince")

    def test_the_seam_down_offers_no_throne(self, world, monkeypatch):
        monkeypatch.setattr(CR, "a_marshal_may_reign", lambda: False)
        _laurels(world, "Murat", 5)
        assert CR.king_candidates(world, "France") == []
        assert CR.resolve_king(world, "France", "Murat")[2] == "No king may be seated at this table, Sire."
        from backend.game_logic.settlement_staging import _crown_row_extras
        extras = _crown_row_extras(world, world.formable_nations["KingdomOfNaples"], "France", True)
        assert extras == {"crown": "King of Naples", "terms_display": "a crown: King of Naples — a regency"}
        assert _crown_row_extras(world, world.formable_nations["Normandy"], "France", True) == {}

    def test_the_bilateral_carry_keeps_the_king(self, world):
        _laurels(world, "Murat", 5)
        _naples_beaten(world)
        _carve(world, king="Murat", kind="marshal")
        treaty = world.active_treaties[world._make_diplo_key("France", "Naples")]
        carve = next(c for c in treaty["clauses"] if c.get("type") == "create_client")
        assert carve["king"] == "Murat" and carve["crown"] == "King of Naples"


# ═══════════════════════════════════════════════════════════════════════
# The crown erected — the teeth at the ONE apply site
# ═══════════════════════════════════════════════════════════════════════

class TestTheCrownErected:
    def test_naples_under_murat_end_to_end(self, world):
        from backend.models.world_state import WorldState
        _laurels(world, "Murat", 5)
        _laurels(world, "Ney", 4)
        murat, ney = world.marshals["Murat"], world.marshals["Ney"]
        trust = murat.trust.value
        _naples_beaten(world)
        threat = int(world.threat_by_target.get("France", 0))
        # the peace's OWN trust reactions, read off a regency control (the
        # same board, no king) — the king's slight is what lies beyond them
        control = WorldState.from_dict(world.to_dict())
        _carve(control)
        _carve(world, king="Murat", kind="marshal")
        assert "KingdomOfNaples" in world.get_active_nations() and "Naples" not in world.get_active_nations()
        row = world.vassals["KingdomOfNaples"]
        assert (row["lord"], row["crown"], row["king"], row["king_kind"]) == (
            "France", "King of Naples", "Murat", "marshal")
        assert row["recognized_by"] == [] and row["crowned_turn"] == world.current_turn
        # the sword: re-homed with his corps, at the seat, off the roster
        assert murat.nation == "KingdomOfNaples" and murat.location == "Naples"
        assert murat.strength == 22000 and "Murat" in world.marshals
        assert "Murat" not in [m.name for m, _ in JZ.get_nation_ladder(world, "France")]
        assert murat.glory_crowned is False and murat.original_nation is None
        # the loyalty is his trust
        assert row["loyalty"] == trust == 75
        # the passed-over: Ney, with laurels; Soult, without, takes no slight
        assert ney.trust.value == control.marshals["Ney"].trust.value + CR.KING_PASSED_OVER_TRUST
        assert ney.jealous_of == "Murat"
        assert world.marshals["Soult"].trust.value == control.marshals["Soult"].trust.value
        assert control.marshals["Ney"].jealous_of is None
        # the Alarm: a capital's 12 on the carver's house (the slot caps at 100)
        assert int(world.threat_by_target["France"]) == min(100, threat + 12)
        assert int(control.threat_by_target["France"]) == min(100, threat + 12)
        # the web: the new court's house is the lord's; the Neapolitans stir
        assert AW.boot_house(world, "KingdomOfNaples") == "France"
        assert AW.occupied_count(world, "Naples") == 1
        assert CR.withholding_courts(world, "KingdomOfNaples") == ["Austria", "Russia", "Britain"]

    def test_the_beat_the_card_the_log_and_the_dispatch(self, world):
        _laurels(world, "Murat", 5)
        _laurels(world, "Ney", 4)
        _naples_beaten(world)
        _carve(world, king="Murat", kind="marshal")
        card = world.nation_proclamation_popup
        assert card["display_name"] == "Kingdom of Naples" and card["subtitle"] == "By your hand."
        # at most two crown lines, so the card reads whole at every UI scale
        # (the SF-RR5 frame pin): the reign with its price, the reception
        assert card["terms"] == [
            "+500 gold to its treasury",
            "it answers to France as a satellite (loyalty 75)",
            "Murat takes the crown as King of Naples; his corps (22,000) goes with him — its loyalty is his trust (75)",
            "Ney hears of the crown with ill grace — Austria, Russia and Britain withhold recognition of the crown",
            "it marches when France calls, and pays tribute"]
        row = _events(world, "nation_formed")[-1]
        assert (row["crown"], row["king"], row["reign"]) == (
            "King of Naples", "Murat", "Murat takes the crown as King of Naples")
        assert CL.format_event_oneliner(row, world) == (
            "Kingdom of Naples is proclaimed — Murat takes the crown as King of Naples")
        beat = [e for e in world.pending_dispatch_events if e["type"] == "crown_erected"]
        assert beat and beat[0]["template_vars"]["reign"] == "Murat takes the crown as King of Naples"
        from backend.game_logic.dispatch import _format_dispatch_event_text
        assert _format_dispatch_event_text("crown_erected", beat[0]["template_vars"]).endswith(
            "a client of France; Murat takes the crown as King of Naples.")
        assert not [e for e in world.pending_dispatch_events if e["type"] == "nation_created"]
        fired = [e for e in world._pending_jealousy_turn_events if e["type"] == "jealousy_fired"]
        assert fired and fired[0]["marshal"] == "Ney" and fired[0]["target"] == "Murat"

    def test_a_prince_costs_no_sword_and_slights_the_laurelled_more(self, world):
        from backend.models.world_state import WorldState
        _laurels(world, "Murat", 5)
        murat = world.marshals["Murat"]
        _naples_beaten(world)
        control = WorldState.from_dict(world.to_dict())
        _carve(control)
        _carve(world, king="Joseph Bonaparte", kind="prince")
        row = world.vassals["KingdomOfNaples"]
        assert (row["king"], row["king_kind"], row["loyalty"]) == ("Joseph Bonaparte", "prince", 50)
        assert murat.nation == "France"
        assert murat.trust.value == control.marshals["Murat"].trust.value + CR.PRINCE_PASSED_OVER_TRUST
        assert murat.jealous_of is None, "a prince is no object of a marshal's envy"
        assert CR.reigning_prince_of(world, "Joseph Bonaparte") == "KingdomOfNaples"
        assert CR.resolve_king(world, "France", "Joseph Bonaparte")[2] == (
            "Joseph Bonaparte already reigns in Kingdom of Naples, Sire.")
        assert [c["name"] for c in CR.king_candidates(world, "France")] == [
            "Murat", "Louis Bonaparte", "Jerome Bonaparte"]
        assert world.nation_proclamation_popup["terms"][2] == (
            "Joseph Bonaparte reigns as King of Naples; no sword is lost (loyalty 50)")

    def test_a_regency_where_no_king_is_named(self, world):
        _naples_beaten(world)
        _carve(world)
        row = world.vassals["KingdomOfNaples"]
        assert row["crown"] == "King of Naples" and "king" not in row and row["loyalty"] == 60
        terms = world.nation_proclamation_popup["terms"]
        assert "Austria, Russia and Britain withhold recognition of the crown" in terms
        assert not any("takes the crown" in t or "reigns as" in t for t in terms)
        assert len(terms) == 4, "a regency adds its reception alone (the blurb names the crown)"
        beat = [e for e in world.pending_dispatch_events if e["type"] == "crown_erected"]
        assert beat[0]["template_vars"]["reign"] == "a regency holds the crown (King of Naples)"

    def test_the_king_seam_down_ignores_the_king(self, world, monkeypatch):
        monkeypatch.setattr(CR, "a_marshal_may_reign", lambda: False)
        _laurels(world, "Murat", 5)
        _naples_beaten(world)
        _carve(world, king="Murat", kind="marshal")
        row = world.vassals["KingdomOfNaples"]
        assert row["crown"] == "King of Naples" and "king" not in row
        assert world.marshals["Murat"].nation == "France"

    def test_the_crown_seam_down_is_a_plain_carve(self, monkeypatch):
        """Down at load: the crown templates struck (an older template that
        gained a block would stay, its block struck — none does today), no
        store — the catalogue session D left."""
        monkeypatch.setattr(CR, "a_crown_is_erected", lambda: False)
        from backend.models.world_state import WorldState
        w = WorldState.from_scenario(str(SCENARIO), seed="historical")
        assert list(w.formable_nations) == list(PLAIN)
        assert "crown" not in w.formable_nations["DuchyOfWarsaw"]
        assert not CR.armed(w) and "crowns" not in w.moments
        assert CR.on_crown_erected(w, "DuchyOfWarsaw", {"crown": {"title": "x"}}, "France", {}) == {}

    def test_a_plain_carve_gets_the_house_write_too(self, world):
        """The sibling fix: every carve writes the new court's boot house."""
        from backend.game_logic.diplomacy import declare_war
        with _quiet():
            declare_war(world, "France", "Prussia")
            world.regions["Posen"].controller = "France"
            world.invalidate_active_nations_cache()
        pair = world._make_diplo_key("France", "Prussia")
        world.war_start_turns[pair] = int(world.current_turn) - 6
        threat = int(world.threat_by_target.get("France", 0))
        _carve(world, tag="DuchyOfWarsaw", target="Prussia")
        assert AW.boot_house(world, "DuchyOfWarsaw") == "France"
        assert AW.occupied_count(world, "DuchyOfWarsaw") == 0, "its own soil under its lord is home"
        assert AW.occupied_count(world, "Prussia") == 1, "the Poles are Prussia's people still"
        assert "crown" not in world.vassals["DuchyOfWarsaw"], "a plain carve seats no crown"
        assert int(world.threat_by_target["France"]) == threat, "the Alarm is the crown's, not the carve's"

    def test_the_king_survives_a_save(self, world):
        from backend.models.world_state import WorldState
        _laurels(world, "Murat", 5)
        _naples_beaten(world)
        _carve(world, king="Murat", kind="marshal")
        again = WorldState.from_dict(world.to_dict())
        assert again.vassals["KingdomOfNaples"]["king"] == "Murat"
        assert again.marshals["Murat"].nation == "KingdomOfNaples"
        assert AW.boot_house(again, "KingdomOfNaples") == "France"

    def test_the_formables_page_names_the_throne(self, world):
        rows = {r["tag"]: r for r in FM.build_formables_payload(world)["formables"]}
        assert rows["KingdomOfNaples"]["crown"] == "King of Naples"
        assert rows["Normandy"]["crown"] == ""


# ═══════════════════════════════════════════════════════════════════════
# The AI's road — the gate's Q3
# ═══════════════════════════════════════════════════════════════════════

class TestTheAIsRoad:
    def test_the_victor_erects_the_crown_its_house_may(self, world):
        war = _russia_on_sweden(world)
        terms = TP.held_aim_terms("Russia", "Sweden", ["Finland"])
        cut = TP.erect_a_crown_in_the_terms(world, war, "Russia", "Sweden", terms)
        assert cut == [{"type": "peace"},
                       {"type": "create_client", "from": "Sweden", "to": "Russia", "tag": "Finland",
                        "provinces": ["Finland"], "client_display_name": "Grand Duchy of Finland",
                        "crown": "Grand Duke of Finland"}]
        # a house the crown does not name annexes as before
        assert TP.erect_a_crown_in_the_terms(world, war, "Prussia", "Sweden",
                                             TP.held_aim_terms("Prussia", "Sweden", ["Finland"])) == \
            TP.held_aim_terms("Prussia", "Sweden", ["Finland"])
        # the predicate binds: soil not held, no crown
        world.regions["Finland"].controller = "Sweden"
        world.invalidate_active_nations_cache()
        assert TP.erect_a_crown_in_the_terms(world, war, "Russia", "Sweden", terms) == terms

    def test_the_lock_road_erects_it_too_a_regency_and_the_alarm(self, world):
        _russia_on_sweden(world)
        threat = int(world.threat_by_target.get("Russia", 0))
        with _quiet():
            ceded = TP._cede_the_held_aim(world, "war_1", ("Russia", "Sweden", ["Finland"]))
        assert [c["type"] for c in ceded] == ["create_client"]
        assert world.regions["Finland"].controller == "Finland"
        row = world.vassals["Finland"]
        assert (row["lord"], row["crown"], row.get("king")) == ("Russia", "Grand Duke of Finland", None)
        assert int(world.threat_by_target["Russia"]) == threat + 12
        assert TP._ceded_regions(ceded) == ["Finland"]
        assert TP._consequence_line(world, "Russia", "Sweden", ceded) == (
            "Russia erects Grand Duchy of Finland out of Finland. Russia is now free to look elsewhere.")
        assert CR.withholding_courts(world, "Finland") == ["Austria", "Britain"]
        assert AW.boot_house(world, "Finland") == "Russia"

    def test_the_aim_peace_end_to_end(self, world):
        war = _russia_on_sweden(world)
        with patch(SCORER, side_effect=_accepts), _quiet():
            event = TP.attempt_aim_held_settlement(world, "war_1", war)
        assert event["exit"] == TP.AIM_HELD_EXIT
        assert event["consequence"].startswith("Russia erects Grand Duchy of Finland out of Finland.")
        assert "Finland" in world.get_active_nations() and world.vassals["Finland"]["lord"] == "Russia"
        assert _events(world, "nation_formed")[-1]["crown"] == "Grand Duke of Finland"

    def test_the_seam_down_cedes_as_t3_4_wrote_it(self, world, monkeypatch):
        monkeypatch.setattr(TP, "a_victor_erects_a_crown", lambda: False)
        war = _russia_on_sweden(world)
        terms = TP.held_aim_terms("Russia", "Sweden", ["Finland"])
        assert TP.erect_a_crown_in_the_terms(world, war, "Russia", "Sweden", terms) == terms
        with _quiet():
            ceded = TP._cede_the_held_aim(world, "war_1", ("Russia", "Sweden", ["Finland"]))
        assert [c["type"] for c in ceded] == ["territory_cede"]
        assert world.regions["Finland"].controller == "Russia" and "Finland" not in world.vassals


# ═══════════════════════════════════════════════════════════════════════
# The seams
# ═══════════════════════════════════════════════════════════════════════

class TestTheSeams:
    def test_the_rows_are_registered_and_apply(self, monkeypatch):
        for row in ROWS:
            assert T3_SEAMS_BY_ROW[row]
        hold_down(monkeypatch, [s for row in ROWS for s in T3_SEAMS_BY_ROW[row]])
        assert CR.a_crown_is_erected() is False and CR.a_marshal_may_reign() is False
        assert TP.a_victor_erects_a_crown() is False
        assert CR.strike_crowns({"X": {"crown": {"title": "t", "since": "DY-6"}}, "Y": {"a": 1}}) == {"Y": {"a": 1}}

    def test_the_seams_are_zero_arg_functions_not_levers(self):
        import inspect
        for fn in (CR.a_crown_is_erected, CR.a_marshal_may_reign, TP.a_victor_erects_a_crown):
            assert inspect.signature(fn).parameters == {} and fn() is True

    def test_the_applier_is_one_body(self):
        """Both routes — the settlement table and the bilateral carry — carve
        through `formations.apply_create_client_clause`, where the crown's
        teeth land; the AI's road rides `_apply_settlement_terms` too."""
        import inspect
        assert "apply_create_client_clause" in inspect.getsource(SR._apply_settlement_terms)
        assert "clause=term" in inspect.getsource(FM.apply_create_client_clause)
        assert "erect_a_crown_in_the_terms" in inspect.getsource(TP._cede_the_held_aim)
        assert "erect_a_crown_in_the_terms" in inspect.getsource(TP.attempt_aim_held_settlement)


# ═══════════════════════════════════════════════════════════════════════
# The session's one measure — four arms on three surfaces, each ALONE
# (`tools/_t8_measure.py`; `tools/_t8_series_arms.py`). Seeded paths, not
# laws (DYNAMISM_SPEC.md §6b; SYSTEMS_REFERENCE.md §205).
# ═══════════════════════════════════════════════════════════════════════

def _record(name: str) -> dict:
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


def _dump(row) -> str:
    return json.dumps(row, sort_keys=True)


SEEDS = ("austerlitz", "eylau", "friedland", "historical", "jena", "lodi",
         "marengo", "rivoli", "ulm", "wagram")
STAMP = "2026_11_10"
AMBIENT_ARMS = (("0", "t8_control"), ("CROWN", "t8_crown"), ("AI", "t8_ai"), ("ALL", "t8"))
ARM_NAMES = tuple(a for a, _ in AMBIENT_ARMS)


class TestTheSessionEMeasure:
    """The records of the shipped tree (one run; arm 0 reproduces session D
    on every surface). Read honestly: the seams are read on every arm and
    NO crown is erected on any measured arm — the AI road's live case (a
    Russian or Austrian aim peace) waits on wars the idle France never frees
    them to fight, the harness France's wars are the player's (never the
    AI–AI road), and the scripted France authors no carve. The crown's
    proof is this file's crafted boards."""

    def _sig(self, label: str) -> dict:
        return _record(f"_dy_signature_{label}_{STAMP}.json")

    def _census(self, label: str) -> dict:
        return _record(f"_{label}_census_{STAMP}.json")

    def test_arm_0_reproduces_session_ds_records_on_both_surfaces(self):
        d = _record("_dy_signature_t6b_2026_11_10.json")
        ctl = self._sig("t8_control")
        for seed in SEEDS:
            assert _dump(ctl["seeds"][seed]) == _dump(d["seeds"][seed]), seed
        d_census, ctl_census = _record("_t6b_census_2026_11_10.json"), self._census("t8_control")
        assert all(ctl_census["totals"][k] == v for k, v in d_census["totals"].items())
        assert ctl_census["totals"]["crowns_erected"] == 0
        harness = _record(f"_t8_chain_d_{STAMP}.json")
        prior = _record("_t6b_chain_d_2026_11_10.json")["arms"]["ALL"]
        for seed in SEEDS:
            mine = harness["arms"]["0"][seed]
            assert _dump({k: mine.get(k) for k in prior[seed]}) == _dump(prior[seed]), seed

    def test_no_arm_moves_an_ambient_world_line_and_no_crown_is_erected(self):
        ctl = self._sig("t8_control")
        for arm, label in AMBIENT_ARMS:
            sig = self._sig(label)
            assert sig["story_class_count"] == 10, arm
            for seed in SEEDS:
                assert _dump(sig["seeds"][seed]) == _dump(ctl["seeds"][seed]), (arm, seed)
            census = self._census(label)
            assert census["totals"]["crowns_erected"] == 0, arm
            assert all(census["seeds"][s]["crowns"] == [] for s in SEEDS), arm
            assert census["totals"]["supply_losses"] == 1196439 and census["totals"]["captures_outside_aim"] == 251, arm
            assert census["totals"]["annexations_outside_aim"] == 0 and census["totals"]["awakening_beats"] == 25, arm

    def test_the_harness_erects_no_crown_and_moves_nothing(self):
        """Chain D: the AI-run France's wars are the player's, so the AI road
        never runs for them; Russia and Austria reach no aim peace a crown
        fits in forty turns. The `formations` column (new on the record)
        reads the Class T dreams the march lets form — Holland's on four
        seeds, the Kingdom of Italy's on six — on every arm alike."""
        harness = _record(f"_t8_chain_d_{STAMP}.json")
        arms = harness["arms"]
        for a, b in zip(ARM_NAMES, ARM_NAMES[1:]):
            assert all(_dump(arms[b][s]) == _dump(arms[a][s]) for s in SEEDS), (a, b)
        assert all(harness["totals"][arm]["crowns_erected"] == 0 for arm in ARM_NAMES)
        assert all(arms["ALL"][s]["crowns"] == [] for s in SEEDS)
        assert {s: arms["ALL"][s]["formations"] for s in SEEDS if arms["ALL"][s]["formations"]} == {
            "austerlitz": ["Holland"], "eylau": ["Holland"], "friedland": ["Holland", "KingdomOfItaly"],
            "historical": ["KingdomOfItaly"], "jena": ["KingdomOfItaly"],
            "marengo": ["Holland", "KingdomOfItaly"], "rivoli": ["KingdomOfItaly"], "wagram": ["KingdomOfItaly"]}
        assert (harness["totals"]["ALL"]["captures_outside_aim"], harness["totals"]["ALL"]["annexations_outside_aim"],
                harness["totals"]["ALL"]["rank_promotions"]) == (117, 0, 0)

    def test_the_band_holds_on_every_arm(self):
        band = _record(f"_t8_band_{STAMP}.json")
        for arm in ARM_NAMES:
            arms = band["arms"][arm]
            assert (arms["CMD-H"]["provinces"], arms["CMD-A"]["provinces"], arms["CMD-M"]["provinces"]) == (28, 27, 26), arm
            assert all(23 <= arms[n]["provinces"] <= 28 for n in ("CMD-H", "CMD-A", "CMD-M")), arm

    def test_the_series_does_not_move_and_the_seams_are_read(self):
        series = _record("_t8_series_arms_final.json")
        for arm in ARM_NAMES:
            row = series["arms"][arm]
            assert row["first_divergence_vs_prior"] is None, arm
            counts = row["reach"]["counts"]
            assert counts["crown_seam_reads"] == 2 and counts["ai_seam_reads"] == 1, arm
            assert counts["carves"] == 0 and counts["crowns"] == 0, arm

    def test_the_raised_gates_clauses_read_against_the_record(self):
        sig = self._sig("t8")
        assert all(sig["seeds"][s]["signature"]["eliminations"] == [[t, "KingdomOfItaly"]]
                   for s, t in zip(SEEDS, (10, 7, 23, 9, 7, 10, 21, 7, 10, 9))), "clause 3: unmet"
        assert all(sig["seeds"][s]["signature"]["formations"] == [] for s in SEEDS), "clause 3: no crown ambiently"
        assert all(sig["seeds"][s]["signature"]["rank_promotions"] == [] for s in SEEDS), "clause 2: unmet"
        assert sig["story_class_count"] == 10, "clause 1: met"
