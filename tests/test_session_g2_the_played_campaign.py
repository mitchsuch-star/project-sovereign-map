"""Session G2 — the played campaign (DYNAMISM_SPEC.md §7b; November 11, 2026).

The user's word: "fix and playtest … when i say playtest i mean play well see
derivations see dynamism test like humna", then, at the plan: "make sure ux and
ui works for all of this too … making someone king … should use ui! and how
does it impact marshals".

A France was PLAYED by hand on a freshly rolled seed (`distant-bivouac-95`):
Ulm, Vienna, a separate peace erecting the Kingdom of Hungary, a peace with
Russia, a licence and a sponsorship. What that campaign found, each pinned
here at its cause:

  * G2-KING   — the king chosen at the table was dropped on the separate
                peace's carry (`settlement_staging._pair_substitute_seed_
                terms` copied four keys): Soult's Hungary was a regency.
  * G2-RECOG  — recognition's loser was read off the clause burden: the
                2,800 gold France paid for the carve outweighed the kingdom
                Austria ceded, so the beaten court withheld recognition of
                the crown she signed over.
  * G2-ASK    — a court that reaches `fight` before two refusals never asked
                and never opened its crisis (the cast Naples, 35 turns).
  * G2-LADDER — T0-F's escalating rest spaced the asks past the 12-turn
                memory: the ladder was climbed six turns in eighteen.
  * G2-BACKED — a sponsorship or a licence moved gold and nothing else.
  * the marshals' side and the screens' words.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend import display_names as DN  # noqa: E402
from backend.game_logic import agendas as AG  # noqa: E402
from backend.game_logic import ai_diplomacy as AD  # noqa: E402
from backend.game_logic import crowns as CR  # noqa: E402
from backend.game_logic import formations as FM  # noqa: E402
from backend.game_logic import instruments as IN  # noqa: E402
from backend.game_logic import intent as IT  # noqa: E402
from backend.game_logic import jealousy as JZ  # noqa: E402
from backend.game_logic import war_council as WC  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
ROWS = ("G2-RECOG", "G2-ASK", "G2-LADDER", "G2-BACKED")


def _world(seed: str = "historical"):
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed=seed)


@pytest.fixture()
def world():
    return _world("historical")


@pytest.fixture()
def jena():
    """The seed that casts Naples: `roman_expedition` at her deck's head."""
    return _world("jena")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _events(world, etype: str):
    return [e for e in world.event_log if e.get("type") == etype]


def _laurels(world, name: str, points: int = 5) -> None:
    JZ._append_glory(world.marshals[name], world.current_turn, points)


def _austria_beaten(world, score: int = 45):
    """France's war with Austria (the 1805 boot) read for France at `score`,
    Hungary in French hands — the played board's turn 12."""
    pair = world._make_diplo_key("France", "Austria")
    world.war_scores[pair] = score if pair.split("|")[0] == "France" else -score
    world.war_start_turns[pair] = int(world.current_turn) - 6
    world.regions["Hungary"].controller = "France"
    world.invalidate_active_nations_cache()
    return pair


def _hungary_term(world, king: str = "Soult"):
    """The joint table's own clause, stamped by the add verb's arm."""
    template = FM.get_template(world, "Hungary")
    clause = {"type": "create_client", "from": "Austria", "to": "France", "tag": "Hungary",
              "provinces": FM.template_provinces(template),
              "client_display_name": FM.get_template_identity(template)["display_name"],
              "crown": CR.crown_title(template)}
    if king:
        clause, why = CR.stamp_king_on_clause(world, clause, "France", king)
        assert why == "", why
    return clause


def _separate_peace(world, term, gold: int = 0):
    """The separate peace's whole road below the buttons: the seed builder
    (`confirm_pair_substitute`), the counter's deep copy with the price it
    adds, the ratifier."""
    import copy
    from backend.game_logic.settlement_actions import _pair_substitute_seed_terms
    seed = _pair_substitute_seed_terms([term], target="Austria", proposer_leader="France")
    countered = copy.deepcopy({"type": "peace", "proposer_nation": "France",
                               "target_nation": "Austria",
                               "sweeteners": list(seed.get("sweeteners") or []),
                               "demands": list(seed["demands"])})
    if gold:
        countered["sweeteners"].append({"type": "gold_lump", "value": int(gold)})
        world.gold = max(int(world.gold), int(gold) + 500)
    with _quiet():
        return world._ratify_treaty(countered), seed


# ═══════════════════════════════════════════════════════════════════════
# G2-KING — the king survives the separate peace
# ═══════════════════════════════════════════════════════════════════════

class TestTheKingTravels:
    def test_the_seed_builder_keeps_the_crown_and_the_king(self, world):
        _laurels(world, "Soult")
        _austria_beaten(world)
        from backend.game_logic.settlement_actions import _pair_substitute_seed_terms
        seed = _pair_substitute_seed_terms([_hungary_term(world)], target="Austria",
                                           proposer_leader="France")
        carve = [d for d in seed["demands"] if d["type"] == "create_client"][0]
        assert {k: carve.get(k) for k in CR.CROWN_CLAUSE_KEYS} == {
            "crown": "King of Hungary", "king": "Soult", "king_kind": "marshal",
            "king_display": "Soult"}
        # the four keys it always carried are untouched
        assert carve["tag"] == "Hungary" and carve["provinces"] == ["Hungary"]
        assert carve["client_display_name"] == "Kingdom of Hungary" and carve["value"] == 1

    def test_a_regency_carries_no_king(self, world):
        _austria_beaten(world)
        from backend.game_logic.settlement_actions import _pair_substitute_seed_terms
        seed = _pair_substitute_seed_terms([_hungary_term(world, king="")], target="Austria",
                                           proposer_leader="France")
        carve = [d for d in seed["demands"] if d["type"] == "create_client"][0]
        assert "king" not in carve and carve["crown"] == "King of Hungary"

    def test_soult_is_king_of_hungary_through_the_separate_peace_and_a_counter(self, world):
        """The played campaign's turn 10–12, end to end below the buttons:
        the carried demand, Austria's 2,800, the ratifier, the one apply."""
        _laurels(world, "Soult")
        _austria_beaten(world)
        corps = int(world.marshals["Soult"].strength)
        trust = int(world.marshals["Soult"].trust.value)
        _separate_peace(world, _hungary_term(world), gold=2800)
        row = world.vassals["Hungary"]
        assert (row["king"], row["king_kind"], row["crown"]) == ("Soult", "marshal", "King of Hungary")
        soult = world.marshals["Soult"]
        assert soult.nation == "Hungary" and int(soult.strength) == corps
        assert soult.location == CR.seat_of(world, "Hungary")
        assert row["loyalty"] == max(30, min(95, trust))
        assert "Soult" not in [m.name for m in world.get_player_marshals()]

    def test_the_one_whitelist_names_the_keys(self):
        import inspect
        from backend.game_logic import settlement_staging as SS
        src = inspect.getsource(SS._pair_substitute_seed_terms)
        assert "CROWN_CLAUSE_KEYS" in src
        assert CR.CROWN_CLAUSE_KEYS == ("crown", "king", "king_kind", "king_display")


# ═══════════════════════════════════════════════════════════════════════
# G2-RECOG — the war names the beaten
# ═══════════════════════════════════════════════════════════════════════

class TestTheWarNamesTheBeaten:
    CLAUSES = [{"type": "gold_lump", "from": "France", "to": "Austria", "amount": 2800},
               {"type": "create_client", "from": "Austria", "to": "France", "tag": "Hungary",
                "provinces": ["Hungary"], "client_display_name": "Kingdom of Hungary"}]

    def test_the_burden_alone_named_the_victor_beaten(self):
        """Session F's read on the played treaty: the gold outweighs the
        kingdom, so France is the 'loser' of a war she won at +45."""
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G2-RECOG"])
            assert CR.peace_loser("France", "Austria", self.CLAUSES, "Austria") == "France"
        assert CR.peace_loser("France", "Austria", self.CLAUSES, "Austria") == "Austria"
        # a drawn war: the burden still decides
        assert CR.peace_loser("France", "Austria", self.CLAUSES, "") == "France"
        assert CR.peace_loser("France", "Austria", [], "") == ""
        # a name outside the pair is no answer
        assert CR.peace_loser("France", "Austria", self.CLAUSES, "Russia") == "France"

    def test_the_bar_is_the_ratification_records_own(self, world):
        pair = _austria_beaten(world, 30)
        assert CR.war_loser(world, "France", "Austria") == "Austria"
        assert CR.war_loser(world, "Austria", "France") == "Austria"
        world.war_scores[pair] = 29 if pair.split("|")[0] == "France" else -29
        assert CR.war_loser(world, "France", "Austria") == ""
        world.war_scores[pair] = -30 if pair.split("|")[0] == "France" else 30
        assert CR.war_loser(world, "France", "Austria") == "France"
        import inspect
        from backend.models.world_state import WorldState
        src = inspect.getsource(WorldState)
        assert "if _ws >= 30:" in src and CR.BEATEN_WAR_SCORE == 30

    def test_vienna_recognizes_the_kingdom_she_signed_over(self, world):
        """The played peace: beaten at +45, paid 2,800 for the carve."""
        _laurels(world, "Soult")
        _austria_beaten(world, 45)
        _separate_peace(world, _hungary_term(world), gold=2800)
        assert world.vassals["Hungary"]["recognized_by"] == ["Austria"]
        assert CR.withholding_courts(world, "Hungary") == ["Russia", "Britain"]
        assert [e["courts"] for e in _events(world, "recognition")] == [["Austria"]]

    def test_the_card_does_not_name_the_court_that_recognizes(self, world):
        """The Proclamation speaks the reception as the treaty leaves it —
        the played card read "Austria, Russia and Britain withhold" above a
        rail line saying Vienna had recognized."""
        _laurels(world, "Soult")
        _austria_beaten(world, 45)
        _separate_peace(world, _hungary_term(world), gold=2800)
        beat = _events(world, "nation_formed")[-1]
        assert beat["crown"] == "King of Hungary" and beat["king"] == "Soult"
        card = world.nation_proclamation_popups[-1] if getattr(
            world, "nation_proclamation_popups", None) else world.nation_proclamation_popup
        lines = " / ".join(card["terms"])
        assert "Russia and Britain withhold recognition of the crown" in lines
        assert "Austria" not in lines.split("hear of the crown")[-1]

    def test_the_seam_down_is_session_fs_withholding(self, world):
        _laurels(world, "Soult")
        _austria_beaten(world, 45)
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G2-RECOG"])
            _separate_peace(world, _hungary_term(world), gold=2800)
        assert world.vassals["Hungary"]["recognized_by"] == []
        assert _events(world, "recognition") == []

    def test_a_drawn_war_still_binds_the_court_that_cedes_the_crown(self, world):
        """The instrument itself: a court that signs the article erecting a
        crown out of its own lands recognizes it, whoever is called beaten."""
        _laurels(world, "Soult")
        _austria_beaten(world, 10)
        _separate_peace(world, _hungary_term(world), gold=2800)
        assert world.vassals["Hungary"]["recognized_by"] == ["Austria"]

    def test_a_peace_bought_from_an_unbeaten_court_recognizes_nothing(self, world):
        """Russia in the played campaign: a drawn war ended for 1,000 gold —
        she cedes no crown and was not beaten, so she keeps withholding."""
        _laurels(world, "Soult")
        _austria_beaten(world, 45)
        _separate_peace(world, _hungary_term(world), gold=2800)
        pair = world._make_diplo_key("France", "Russia")
        world.war_scores[pair] = 20 if pair.split("|")[0] == "France" else -20
        with _quiet():
            world._ratify_treaty({"type": "peace", "proposer_nation": "France",
                                  "target_nation": "Russia", "demands": [],
                                  "sweeteners": [{"type": "gold_lump", "value": 1000}]})
        assert world.vassals["Hungary"]["recognized_by"] == ["Austria"]


# ═══════════════════════════════════════════════════════════════════════
# G2-ASK — a court at `fight` still asks
# ═══════════════════════════════════════════════════════════════════════

def _naples_at_fight(jena) -> None:
    deck = jena.agendas["Naples"]
    design = [d for d in deck if d.get("id") == "roman_expedition"][0]
    design["readiness"] = 60
    jena.invalidate_bloc_members_cache()
    jena._intent_cache = None
    view = IT.get_nation_intent("Naples", jena)
    assert (view.want_id, view.against, view.price) == ("roman_expedition", "PapalStates", "fight")


def _first_ask(world, proposer: str, target: str, turns: int = 8):
    """The poll's trigger over the seeded dwell: the first turn it asks."""
    for _ in range(turns):
        world._intent_cache = None
        out = AD._evaluate_ai_ai_triggers(proposer, target, world)
        if isinstance(out, dict) and out.get("type") == "design_ask":
            return out
        world.current_turn += 1
    return None


class TestACourtAtFightStillAsks:
    def test_naples_at_fight_asks_the_pope(self, jena):
        assert AG.get_active_agenda("Naples", jena).id == "roman_expedition"
        _naples_at_fight(jena)
        assert not WC._ladder_climbed(jena, "Naples", "PapalStates")
        assert _first_ask(jena, "Naples", "PapalStates") == {
            "type": "design_ask", "proposer": "Naples", "target": "PapalStates"}

    def test_the_seam_down_she_never_asks(self, jena):
        _naples_at_fight(jena)
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G2-ASK"])
            assert _first_ask(jena, "Naples", "PapalStates", turns=12) is None

    def test_a_climbed_ladder_stops_the_asking(self, jena):
        _naples_at_fight(jena)
        jena.current_turn = 12
        for turn in (6, 12):
            jena.diplomatic_refusals.setdefault("Naples>PapalStates", []).append(
                {"type": "design_ask", "turn": turn})
        jena._intent_cache = None
        assert WC._ladder_climbed(jena, "Naples", "PapalStates")
        out = AD._evaluate_ai_ai_triggers("Naples", "PapalStates", jena)
        assert not (isinstance(out, dict) and out.get("type") == "design_ask")


# ═══════════════════════════════════════════════════════════════════════
# G2-LADDER — the ladder outlasts the rest
# ═══════════════════════════════════════════════════════════════════════

class TestTheLadderOutlastsTheRest:
    def test_the_two_windows(self, world):
        """Refused at 7 and 13 (the played campaign's Prussia before
        Hanover): at turn 24 the 12-turn memory holds one, the ladder's two."""
        world.diplomatic_refusals["Prussia>Hanover"] = [
            {"type": "design_ask", "turn": 7}, {"type": "design_ask", "turn": 13}]
        world.current_turn = 24
        assert len(AD.get_refused_asks(world, "Prussia", "Hanover")) == 1
        assert len(AD.get_ladder_refusals(world, "Prussia", "Hanover")) == 2
        assert WC._ladder_climbed(world, "Prussia", "Hanover")
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G2-LADDER"])
            assert len(AD.get_ladder_refusals(world, "Prussia", "Hanover")) == 1
            assert not WC._ladder_climbed(world, "Prussia", "Hanover")
        world.current_turn = 31
        assert not WC._ladder_climbed(world, "Prussia", "Hanover")

    def test_the_window_covers_the_longest_rest(self):
        assert AD.LADDER_MEMORY_TURNS == 3 * AD.TYPE_REJECTION_COOLDOWN + AD.REFUSAL_DEDUPE_TURNS
        assert AD.REFUSAL_MEMORY_TURNS == 12

    def test_the_write_keeps_what_the_ladder_reads(self, world):
        world.diplomatic_refusals["Prussia>Hanover"] = [{"type": "design_ask", "turn": 7}]
        world.current_turn = 25
        assert AD.record_diplomatic_refusal(world, "Prussia", "Hanover", "design_ask")
        assert [e["turn"] for e in world.diplomatic_refusals["Prussia>Hanover"]] == [7, 25]
        world.diplomatic_refusals["Prussia>Hanover"] = [{"type": "design_ask", "turn": 7}]
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G2-LADDER"])
            assert AD.record_diplomatic_refusal(world, "Prussia", "Hanover", "design_ask")
            assert [e["turn"] for e in world.diplomatic_refusals["Prussia>Hanover"]] == [25]

    def test_the_weights_hardening_still_reads_twelve(self, world):
        import inspect
        src = inspect.getsource(IT._derive_weight)
        assert "get_refused_asks(world, nation, against)" in src
        assert "get_ladder_refusals" not in src
        assert "get_ladder_refusals(world, coveter, target)" in inspect.getsource(WC._ladder_climbed)


# ═══════════════════════════════════════════════════════════════════════
# G2-BACKED — a backed design dares
# ═══════════════════════════════════════════════════════════════════════

def _weight(world, nation: str) -> int:
    world._intent_cache = None
    return int(IT.get_nation_intent(nation, world).weight)


def _back(world, payer: str, recipient: str, aim: str, amount: int = 400):
    with _quiet():
        out = IN.grant_directed_sponsorship(world, payer=payer, recipient=recipient, aim=aim,
                                            amount_per_turn=amount, turns=10, kind="sponsorship")
    assert out["success"], out
    return out["record"]


class TestABackedDesignDares:
    def test_frances_gold_moves_prussias_design(self, world):
        view = IT.get_nation_intent("Prussia", world)
        assert (view.want_id, view.against) == ("hanoverian_prize", "Hanover")
        before = _weight(world, "Prussia")
        _back(world, "France", "Prussia", "Hanover", 400)
        assert _weight(world, "Prussia") == before + IT.WEIGHT_BACKED_DESIGN == before + 10

    def test_a_licence_is_the_same_record_and_the_same_push(self, world):
        before = _weight(world, "Prussia")
        record = _back(world, "France", "Prussia", "Hanover", 0)
        assert record["amount_per_turn"] == 0 and record["kind"] == "sponsorship"
        assert _weight(world, "Prussia") == before + 10

    def test_the_seam_down_the_compact_moves_nothing(self, world):
        before = _weight(world, "Prussia")
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G2-BACKED"])
            _back(world, "France", "Prussia", "Hanover", 400)
            assert _weight(world, "Prussia") == before
            assert IT.backing_words(world, "Prussia") == ""
            assert IT.backing_forecast(world, "Prussia", "Hanover") == ""

    def test_an_aim_in_the_players_house_is_never_pushed(self, world):
        """The paymaster's subsidies against France read as they always did."""
        for court in ("Austria", "Sardinia", "Sweden"):
            before = _weight(world, court)
            _back(world, "Britain", court, "France", 300)
            assert _weight(world, court) == before, court
        agenda = AG.get_active_agenda("Prussia", world)
        assert IT.design_backing(world, "Prussia", agenda, "France") is None
        assert IT.design_backing(world, "Prussia", agenda, "KingdomOfItaly") is None

    def test_only_the_design_the_compact_aims_at(self, world):
        before = _weight(world, "Prussia")
        _back(world, "France", "Prussia", "Saxony", 400)
        assert _weight(world, "Prussia") == before
        assert IT.design_backing(world, "Prussia", AG.get_active_agenda("Prussia", world),
                                 "Hanover") is None

    def test_the_push_ends_with_the_compact(self, world):
        before = _weight(world, "Prussia")
        record = _back(world, "France", "Prussia", "Hanover", 400)
        assert _weight(world, "Prussia") == before + 10
        record["turns_remaining"] = 0
        assert _weight(world, "Prussia") == before
        world.directed_sponsorships = []
        assert _weight(world, "Prussia") == before

    def test_a_neutrality_bought_is_no_backing(self, world):
        before = _weight(world, "Prussia")
        with _quiet():
            IN.grant_directed_sponsorship(world, payer="France", recipient="Prussia", aim="Hanover",
                                          amount_per_turn=200, turns=10, kind="neutrality")
        assert _weight(world, "Prussia") == before

    def test_the_words_at_the_choice_and_on_the_ledger(self, world):
        weight = _weight(world, "Prussia")
        said = IT.backing_forecast(world, "Prussia", "Hanover")
        assert said.startswith(f"Backed, her design gains weight ({weight} to {weight + 10})")
        assert said in IN.sponsorship_quote(world, "France", "Prussia", "Hanover", 400)
        assert said in IN.sponsorship_quote(world, "France", "Prussia", "Hanover", 0)
        _back(world, "France", "Prussia", "Hanover", 400)
        assert IT.backing_words(world, "Prussia") == (
            "backed by France (400 gold a turn, 10 turns left) — she dares more for it")
        world._intent_cache = None
        assert IT.build_intent_payload("Prussia", world)["summary"].endswith(
            "backed by France (400 gold a turn, 10 turns left) — she dares more for it")
        # once backed, the forecast is silent (nothing more to buy)
        assert IT.backing_forecast(world, "Prussia", "Hanover") == ""

    def test_a_free_hand_reads_as_one(self, world):
        _back(world, "France", "Prussia", "Hanover", 0)
        assert IT.backing_words(world, "Prussia").startswith("backed by France (a free hand, 10 turns left)")

    def test_the_emperors_grant_is_read_at_once(self, world):
        """The player's own compact flushes the read; an AI's waits its turn
        (the intent cache's staleness is turn-granular by design)."""
        before = int(IT.get_nation_intent("Prussia", world).weight)
        _back(world, "France", "Prussia", "Hanover", 400)
        assert int(IT.get_nation_intent("Prussia", world).weight) == before + 10


# ═══════════════════════════════════════════════════════════════════════
# The marshals' side of a crown, and the screens' words
# ═══════════════════════════════════════════════════════════════════════

class TestTheMarshalsSide:
    def _crowned(self, world):
        for name in ("Soult", "Davout", "Massena"):
            _laurels(world, name)
        _austria_beaten(world, 45)
        _separate_peace(world, _hungary_term(world), gold=2800)
        return world.vassals["Hungary"]

    def test_the_pick_says_what_it_costs(self, world):
        for name in ("Soult", "Davout"):
            _laurels(world, name)
        _austria_beaten(world, 45)
        from backend.game_logic.settlement_staging import _crown_row_extras
        extras = _crown_row_extras(world, FM.get_template(world, "Hungary"), "France", True)
        assert len(extras["king_notes"]) == len(extras["king_labels"]) == len(extras["king_options"])
        assert extras["king_notes"][0] == (
            "No king is seated: the kingdom's loyalty starts at 60 and no marshal is slighted.")
        soult = extras["king_options"].index("Soult")
        trust = max(30, min(95, int(world.marshals["Soult"].trust.value)))
        assert extras["king_notes"][soult] == (
            "He leaves your command for good and his corps with him; the kingdom's loyalty "
            f"starts at his trust ({trust}). Davout will resent it (trust -5, and envy of the king).")
        joseph = extras["king_options"].index("Joseph Bonaparte")
        assert extras["king_notes"][joseph] == (
            "No marshal is lost; the kingdom's loyalty starts at 50. Davout and Soult will "
            "resent a prince set over them (trust -8).")
        foot = extras["king_footnote"]
        # session G4: the footnote says both roads (the cause decides his fate)
        assert foot.startswith(
            "A marshal king is beyond recall. If his court ever turns on you he keeps his crown "
            "and fights for it; if his people rise and drive him out, he comes home with half "
            "his corps.")
        assert "Not yet eligible — a throne wants glory 3:" in foot
        assert "Murat (0)" in foot and "Napoleon" not in foot and "Soult" not in foot

    def test_the_labels_are_as_session_e_left_them(self, world):
        _laurels(world, "Soult")
        rows = CR.king_candidates(world, "France")
        soult = [r for r in rows if r["name"] == "Soult"][0]
        assert soult["label"] == (f"Soult — Marshal, glory 5; his corps "
                                  f"({int(world.marshals['Soult'].strength):,}) goes with him")

    def test_the_marshals_screen_names_the_king(self, world):
        row = self._crowned(world)
        rows = CR.reigning_rows(world, "France")
        assert [(r["king"], r["state"], r["kingdom"]) for r in rows] == [("Soult", "reigns", "Hungary")]
        strength = int(world.marshals["Soult"].strength)
        assert rows[0]["line"] == (
            f"Soult — King of Hungary · reigns at {CR.seat_of(world, 'Hungary')} with {strength:,} men · "
            f"the kingdom's loyalty {row['loyalty']} · 2 courts withhold recognition · beyond your orders")
        # the overview's own cards no longer hold him; the block does
        from backend.game_logic.marshal_overview import build_marshal_overview
        assert "Soult" not in [c["name"] for c in build_marshal_overview(world)]
        assert CR.reigning_rows(world, "Austria") == []

    def test_the_formation_record_keeps_the_king(self, world):
        self._crowned(world)
        record = world.nation_formations["Hungary"]
        assert {k: record.get(k) for k in CR.CROWN_CLAUSE_KEYS} == {
            "crown": "King of Hungary", "king": "Soult", "king_kind": "marshal",
            "king_display": "Soult"}

    def test_a_rebel_king_keeps_his_crown_and_is_named(self, world):
        self._crowned(world)
        assert CR.rebel_king_words(world, "Hungary") == (
            " Soult, whom you crowned as King of Hungary, keeps his throne and turns his "
            "corps against you.")
        # the kingdom breaks away: he is still its marshal, at its head
        del world.vassals["Hungary"]
        world.invalidate_active_nations_cache()
        rows = CR.reigning_rows(world, "France")
        assert rows[0]["state"] == "in_arms"
        assert rows[0]["line"].startswith(
            "Soult — King of Hungary · his kingdom has broken with France and he keeps his crown")
        assert world.marshals["Soult"].nation == "Hungary"
        assert CR.rebel_king_words(world, "Holland") == ""

    def test_the_passed_over_pay_as_session_e_ruled(self, world):
        before = {n: int(world.marshals[n].trust.value) for n in ("Davout", "Massena", "Ney")}
        self._crowned(world)
        assert int(world.marshals["Davout"].trust.value) == before["Davout"] - 5
        assert int(world.marshals["Massena"].trust.value) == before["Massena"] - 5
        assert int(world.marshals["Ney"].trust.value) == before["Ney"]      # no laurels, no slight


class TestTheScreensWords:
    def test_the_mailbox_names_the_crown_and_its_king(self):
        terms = {"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                 "demands": [{"type": "create_client", "value": 1, "tag": "Hungary",
                              "provinces": ["Hungary"], "client_display_name": "Kingdom of Hungary",
                              "king": "Soult", "king_kind": "marshal", "king_display": "Soult"}],
                 "sweeteners": []}
        assert DN._proposal_term_lines(terms) == [
            "Demand: Kingdom of Hungary erected out of Hungary under Soult"]
        terms["demands"][0].pop("king_display")
        terms["demands"][0].pop("king")
        assert DN._proposal_term_lines(terms) == ["Demand: Kingdom of Hungary erected out of Hungary"]
        assert DN._crown_term_line("Demand", {"type": "gold_lump", "value": 300}) == ""

    def test_the_status_quo_names_a_clients_province_once(self, world):
        """The played table said Tyrol twice — once for France's pair, once
        for the Kingdom of Italy's own."""
        from backend.game_logic.settlement_staging import settlement_status_quo_review
        world.regions["Bohemia"].controller = "France"
        world.regions["Tyrol"].controller = "KingdomOfItaly"
        world.invalidate_active_nations_cache()
        war = next(iter(world.war_instances.values()))
        side = war["side_by_nation"]["France"]
        lines = settlement_status_quo_review(world, war, side, ["Austria"], [{"type": "peace"}])
        assert sum(line.count("Tyrol") for line in lines) == 1, lines
        assert any("Bohemia" in line for line in lines), lines


class TestTheSeams:
    def test_every_rule_has_its_row_and_ships_up(self):
        assert CR.the_war_names_the_beaten() is True
        assert AD.a_court_at_fight_still_asks() is True
        assert AD.the_ladder_outlasts_the_rest() is True
        assert IT.a_backed_design_dares() is True
        for row in ROWS:
            assert row in T3_SEAMS_BY_ROW and len(T3_SEAMS_BY_ROW[row]) == 1

    def test_the_rows_join_the_recorded_boards_hold_list(self):
        from tests._oct27_seams import OCT27_SEAMS_DOWN
        for row in ROWS:
            assert T3_SEAMS_BY_ROW[row][0] in OCT27_SEAMS_DOWN


# ═══════════════════════════════════════════════════════════════════════
# The session's measure — ONE sweep, four arms, three surfaces, the series
# ═══════════════════════════════════════════════════════════════════════

def _record(name: str) -> dict:
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


def _dump(row) -> str:
    return json.dumps(row, sort_keys=True)


SEEDS = ("austerlitz", "eylau", "friedland", "historical", "jena", "lodi",
         "marengo", "rivoli", "ulm", "wagram")
STAMP = "2026_11_11"
AMBIENT_ARMS = (("0", "g2_control"), ("ASK", "g2_ask"), ("LADDER", "g2_ladder"), ("ALL", "g2"))
ARM_NAMES = tuple(a for a, _ in AMBIENT_ARMS)
NAPLES_SPOILS = {"Naples": ["Milan", "Piedmont"]}


class TestTheSessionG2Measure:
    """Written from the records after the sweep ran ALONE
    (`tools/_g2_measure.py`, `tools/_g2_series_arms.py`). Arm 0 reproduces
    session G; each further arm raises one rule."""

    def _sig(self, label: str) -> dict:
        return _record(f"_dy_signature_{label}_{STAMP}.json")

    def _census(self, label: str) -> dict:
        return _record(f"_{label}_census_{STAMP}.json")

    def _moved(self, before: dict, after: dict):
        return [s for s in SEEDS if _dump(before["seeds"][s]) != _dump(after["seeds"][s])]

    def test_arm_0_reproduces_session_g_on_both_surfaces(self):
        g, ctl = self._sig("gate"), self._sig("g2_control")
        for seed in SEEDS:
            assert _dump(ctl["seeds"][seed]) == _dump(g["seeds"][seed]), seed
        assert _dump(self._census("g2_control")["seeds"]) == _dump(self._census("gate")["seeds"])
        harness = _record(f"_g2_chain_d_{STAMP}.json")
        prior = _record(f"_gate_chain_d_{STAMP}.json")["arms"]["ALL"]
        assert _dump(harness["arms"]["0"]) == _dump(prior)

    def test_the_court_at_fight_moves_jena_and_wagram(self):
        """Arm ASK: the cast Naples asks, is refused twice and marches — the
        Pope falls on jena too (26) and fourteen turns sooner on wagram (17);
        eight seeds byte-identical to session G."""
        g, ask = self._sig("g2_control"), self._sig("g2_ask")
        assert self._moved(g, ask) == ["jena", "wagram"]
        assert ask["seeds"]["jena"]["signature"]["eliminations"] == [[7, "KingdomOfItaly"], [26, "PapalStates"]]
        assert ask["seeds"]["wagram"]["signature"]["eliminations"] == [[9, "KingdomOfItaly"], [17, "PapalStates"]]
        assert g["seeds"]["jena"]["signature"]["eliminations"] == [[7, "KingdomOfItaly"]]
        assert g["seeds"]["wagram"]["signature"]["eliminations"] == [[9, "KingdomOfItaly"], [31, "PapalStates"]]

    def test_the_ladder_and_the_backing_each_move_lodi_alone(self):
        ask, ladder, shipped = self._sig("g2_ask"), self._sig("g2_ladder"), self._sig("g2")
        assert self._moved(ask, ladder) == ["lodi"]
        assert self._moved(ladder, shipped) == ["lodi"]
        fights = shipped["seeds"]["lodi"]["signature"]["courts_at_fight"]
        assert "Denmark" in fights and "Denmark" not in ladder["seeds"]["lodi"]["signature"]["courts_at_fight"]

    def test_the_gate_reads_met_on_the_shipped_arm(self):
        shipped, census = self._sig("g2"), self._census("g2")
        assert all(self._sig(label)["story_class_count"] == 10 for _, label in AMBIENT_ARMS)
        promoted = {s: shipped["seeds"][s]["signature"]["rank_promotions"] for s in SEEDS
                    if shipped["seeds"][s]["signature"]["rank_promotions"]}
        assert promoted == {"lodi": [[33, "Hesse"]], "marengo": [[40, "Hesse"]]}
        rosters = {s: tuple(n for _, n in shipped["seeds"][s]["signature"]["eliminations"]) for s in SEEDS}
        assert sorted(s for s, r in rosters.items() if r == ("KingdomOfItaly", "PapalStates")) == ["jena", "wagram"]
        assert all(r == ("KingdomOfItaly",) for s, r in rosters.items() if s not in ("jena", "wagram"))
        assert all(shipped["seeds"][s]["signature"]["formations"] == [] for s in SEEDS)
        assert census["totals"]["annexations_outside_aim"] == 0
        assert (census["totals"]["captures_outside_aim"], census["totals"]["crowns_erected"],
                census["totals"]["recognitions"], census["totals"]["rank_promotions"]) == (266, 0, 0, 2)

    def test_the_band_does_not_move(self):
        band = _record(f"_g2_band_{STAMP}.json")
        for arm in ARM_NAMES:
            arms = band["arms"][arm]
            assert [arms[n]["provinces"] for n in ("CMD-H", "CMD-A", "CMD-M")] == [28, 27, 25], arm

    def test_the_series_does_not_move_and_the_rules_bite_on_the_rig(self):
        series = _record("_g2_series_arms_final.json")
        for arm in ARM_NAMES:
            row = series["arms"][arm]
            assert row["first_divergence_vs_prior"] is None, arm
            counts = row["reach"]["counts"]
            assert counts["ask_seam_reads"] > 7000 and counts["backed_seam_reads"] > 800, arm
            assert counts["recog_seam_reads"] == 0, arm       # no crown stands on the rig
        reach = {arm: series["arms"][arm]["reach"]["counts"] for arm in ARM_NAMES}
        assert [reach[a]["ladder_bites"] for a in ARM_NAMES] == [0, 0, 14, 14]
        assert [reach[a]["backed_bites"] for a in ARM_NAMES] == [0, 0, 0, 10]
        assert ["backed", "Prussia", "Sweden", "Russia"] in [b[1:] for b in series["arms"]["ALL"]["reach"]["beats"]]

    def test_the_harness_annexation_line_is_pinned_at_what_it_reads(self):
        """THE RECORD CORRECTED. Session G's landing record said the AI-France
        harness read 0 annexations outside aim; its own committed file read 2
        (the cast Naples keeps Milan and Piedmont on wagram — the soil of the
        Kingdom of Italy, the player's house's client, which T4-2 exempts
        from "sign at the last"), and no pin held the figure. Pinned now at
        both records: 2 on session G's tree, 4 on this one — the court at
        fight sends the cast Naples to Rome on jena too, and the same client
        falls behind it. Reported to the user; never a silent 0."""
        g = _record(f"_gate_chain_d_{STAMP}.json")
        assert g["totals"]["0"]["annexations_outside_aim"] == 0
        assert g["totals"]["ALL"]["annexations_outside_aim"] == 2
        spoils = {s: {k: v for k, v in g["arms"]["ALL"][s]["annexations_outside_aim_by_court"].items()
                      if k != "France"} for s in SEEDS}
        assert {s: v for s, v in spoils.items() if v} == {"wagram": NAPLES_SPOILS}
        mine = _record(f"_g2_chain_d_{STAMP}.json")
        assert [mine["totals"][a]["annexations_outside_aim"] for a in ARM_NAMES] == [2, 4, 4, 4]
        for arm in ("ASK", "LADDER", "ALL"):
            spoils = {s: {k: v for k, v in mine["arms"][arm][s]["annexations_outside_aim_by_court"].items()
                          if k != "France"} for s in SEEDS}
            assert {s: v for s, v in spoils.items() if v} == {"jena": NAPLES_SPOILS, "wagram": NAPLES_SPOILS}, arm
            assert ["KingdomOfItaly" in [n for _, n in mine["arms"][arm][s]["eliminations"]]
                    for s in ("jena", "wagram")] == [True, True]

    def test_the_harness_promotes_and_crowns_nobody(self):
        mine = _record(f"_g2_chain_d_{STAMP}.json")
        for arm in ARM_NAMES:
            totals = mine["totals"][arm]
            assert (totals["rank_promotions"], totals["crowns_erected"], totals["recognitions"]) == (0, 0, 0), arm
        moved = {arm: [s for s in SEEDS if _dump(mine["arms"][arm][s]) != _dump(mine["arms"]["0"][s])]
                 for arm in ARM_NAMES}
        assert moved == {"0": [], "ASK": ["jena", "wagram"],
                         "LADDER": ["austerlitz", "historical", "jena", "wagram"],
                         "ALL": ["austerlitz", "historical", "jena", "wagram"]}
        assert _dump(mine["arms"]["ALL"]) == _dump(mine["arms"]["LADDER"])


# ═══════════════════════════════════════════════════════════════════════
# The campaign itself — the archived digest of the France played by hand
# ═══════════════════════════════════════════════════════════════════════

class TestThePlayedCampaign:
    """`tools/playtest_scripts/played_emperor.json`, forty turns from New
    Game on the fixed build, archived by the driver (`--archive`). The beats
    below are what the campaign showed the player, in the order they fell."""

    DIGEST = REPO / "docs" / "audits" / "playtest_digests" / "played-emperor" / "digest.md"

    def _lines(self):
        return self.DIGEST.read_text(encoding="utf-8").splitlines()

    def _first(self, needle: str) -> int:
        for index, line in enumerate(self._lines()):
            if needle in line:
                return index
        raise AssertionError(f"the played campaign never showed: {needle}")

    def test_the_seed_is_one_the_tiers_never_measured(self):
        from tools.ai_v_sweep import SWEEP_SEEDS
        head = " ".join(self._lines()[:6])
        assert "campaign seed `distant-bivouac-95`" in head
        assert "distant-bivouac-95" not in SWEEP_SEEDS

    def test_the_beats_fall_in_order(self):
        beats = [
            "General Mack of Austria is taken at Swabia",
            "THE BREWING CRISIS: Naples will move on Papal States",
            "Demand: Kingdom of Hungary erected out of Hungary under Soult",
            "Soult takes the crown as King of Hu",
            "Vienna recognizes the Kingdom of Hungary and its crown, by the peace that beat her.",
            "France licenses The Gulf and the Straits (Finland)",
            "the Papal States has been eliminated",
            "France sponsors Prussia against Hanover (400g/turn)",
            "THE GERMAN QUESTION TURNS: Prussia holds Hanover",
            "THE PEOPLE OF AUSTRIA STIR",
            "Russia sponsors Prussia against Sweden",      # the same turn's log
        ]
        order = [self._first(b) for b in beats]
        assert order == sorted(order), list(zip(beats, order))

    def test_prussia_moved_the_turn_she_was_paid(self):
        lines = self._lines()
        paid = self._first("CMD `sponsor Prussia against Hanover, 400 gold`")
        crisis = self._first("THE BREWING CRISIS: Prussia will move on Hanover")
        turn_heads = [i for i, line in enumerate(lines) if line.startswith("## Turn ")]
        same_turn = max(i for i in turn_heads if i <= paid) == max(i for i in turn_heads if i <= crisis)
        assert same_turn and crisis > paid

    def test_the_two_scripts_are_drivers_own(self):
        import json as _json
        from tools.playtest_driver import SCRIPT_KEYS
        for name in ("played_emperor.json", "played_occupier.json"):
            script = _json.loads((REPO / "tools" / "playtest_scripts" / name).read_text(encoding="utf-8"))
            assert all(key in SCRIPT_KEYS or key.startswith("_") for key in script), name
            assert script["seed"].startswith("distant-")
        emperor = _json.loads((REPO / "tools" / "playtest_scripts" / "played_emperor.json").read_text(encoding="utf-8"))
        occupier = _json.loads((REPO / "tools" / "playtest_scripts" / "played_occupier.json").read_text(encoding="utf-8"))
        # the same first three turns of orders, two seeds, two wars
        assert [emperor["turns"][k] for k in ("1", "2", "3")] == [occupier["turns"][k] for k in ("1", "2", "3")]
        other = (REPO / "docs" / "audits" / "playtest_digests" / "played-occupier" / "digest.md").read_text(encoding="utf-8")
        assert "Munich CAPTURED" in other or "Region captured: Munich" in other
        assert "the Archduke Charles of Austria is taken at Bohemia" in other
