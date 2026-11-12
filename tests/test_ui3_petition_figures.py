"""Session UI-3 (November 12, 2026): a client's petition carries its FIGURES.

`vassal._price_petition` writes `grant_figures` / `refuse_figures` beside the
`grant_line` / `refuse_line` — short display strings of the same numbers, in the
line's order, from the one pricing function (display only: no rule moves). The
popup's face prints them as badges and keeps the sentences for the buttons'
hover; the payload carries both lists on the first read and on every re-quote.
"""
from __future__ import annotations

import contextlib
import io
import re

with contextlib.redirect_stdout(io.StringIO()):
    from backend.game_logic import vassal as V
    from backend.game_logic.ai_diplomacy import build_ai_proposal_dialogue
    from backend.game_logic.mailbox_payloads import refresh_client_petition_dialogue
    from backend.models.world_state import WorldState
    from tests.test_iq7_review_round import SCENARIO

PLAYER = "France"
KOI = "KingdomOfItaly"
SWISS = "Switzerland"


def _world():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCENARIO, seed="historical")


def _tyrol(w):
    w.regions["Tyrol"].controller = PLAYER
    john = w.marshals.get("ArchdukeJohn")
    if john is not None:
        john.location = "Carniola"
    w.invalidate_active_nations_cache()


def _numbers(text: str) -> list[str]:
    return re.findall(r"\d[\d,]*", text.replace("−", "-"))


def _proposal(w, vassal, terms):
    return {
        "source": vassal, "recipient": w.player_nation,
        "proposal_type": V.CLIENT_PETITION_TYPE,
        "terms": {"type": V.CLIENT_PETITION_TYPE, "proposer_nation": vassal,
                  "target_nation": w.player_nation, "demands": [],
                  "sweeteners": [], "petition": terms},
        "talleyrand_assessment": f"{terms['grant_line']} {terms['refuse_line']}",
        "decision_reason": "client_petition",
    }


def test_the_relief_figures_are_the_lines_numbers():
    w = _world()
    t = V.petition_terms(w, SWISS)
    assert t["subject"] == "relief"
    assert len(t["grant_figures"]) == 4 and t["grant_figures"][0].startswith("−")
    assert t["grant_figures"][0] == (f"−{t['tribute_per_turn']:,}g × {t['collections']} "
                                     f"({t['price']:,}g)")
    assert t["grant_figures"][1] == f"loyalty +{t['loyalty_gain']}"
    assert t["grant_figures"][2] == f"bond {t['relation_now']} → {t['relation_after_grant']}"
    assert t["grant_figures"][3] == f"{t['dp_cost']} DP"
    assert t["refuse_figures"] == [f"loyalty −{t['refusal_loyalty_applied']}",
                                   f"bond {t['relation_now']} → {t['relation_after_refusal']}",
                                   "nothing charged"]
    # every figure's numbers stand in the sentence it abbreviates
    for fig in t["grant_figures"]:
        for n in _numbers(fig):
            assert n.replace(",", "") in t["grant_line"].replace(",", "")
    for fig in t["refuse_figures"]:
        for n in _numbers(fig):
            assert n.replace(",", "") in t["refuse_line"].replace(",", "")


def test_the_province_figures_are_the_lines_numbers():
    w = _world()
    _tyrol(w)
    t = V.petition_terms(w, KOI)
    assert t["subject"] == "province" and t["region"] == "Tyrol"
    fig = t["grant_figures"]
    assert fig[0] == "Tyrol passes"
    assert fig[1] == f"loyalty +{t['loyalty_gain']}"
    assert fig[2] == f"bond {t['relation_now']} → {t['relation_after_grant']}"
    assert fig[3] == f"{t['dp_cost']} DP"
    net = int(t["price_parts"]["net_delta"])
    assert fig[4] == (f"net {net:+,}g a turn" if net else "net unchanged")
    assert str(abs(net)) in t["grant_line"].replace(",", "") or net == 0
    assert t["refuse_figures"][0] == f"loyalty −{t['refusal_loyalty_applied']}"


def test_the_fulfilled_case_says_what_its_lines_say():
    w = _world()
    _tyrol(w)
    subject = V.petition_subject(w, KOI)
    t = V._price_petition(w, PLAYER, KOI, subject, fulfilled=True)
    assert "no DP charged" in t["grant_figures"]
    assert t["refuse_figures"] == ["already ceded", "nothing charged"]
    assert "no diplomatic point is charged" in t["grant_line"]


def test_the_payload_carries_the_figures_first_read_and_every_requote():
    w = _world()
    t = V.petition_terms(w, SWISS)
    dialogue = build_ai_proposal_dialogue(_proposal(w, SWISS, t), w)
    payload = dialogue["popup_payload"]
    assert payload["grant_figures"] == t["grant_figures"]
    assert payload["refuse_figures"] == t["refuse_figures"]
    # a re-quote after the relation moves rewrites the stored petition AND the
    # payload together, so the figures never lag the lines
    w.nation_relations[w._make_diplo_key(SWISS, PLAYER)] = 20
    refreshed = refresh_client_petition_dialogue(w, dialogue)
    stored = dialogue["context"]["proposal"]["petition"]
    assert refreshed["grant_figures"] == stored["grant_figures"]
    assert refreshed["refuse_figures"] == stored["refuse_figures"]
    assert refreshed["grant_figures"][2] == (
        f"bond {stored['relation_now']} → {stored['relation_after_grant']}")
    assert stored["relation_now"] == 20
    assert refreshed["clauses"][-3] == stored["grant_line"]
