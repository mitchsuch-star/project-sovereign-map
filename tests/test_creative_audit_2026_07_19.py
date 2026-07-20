"""Regression pins for the July 19, 2026 creative-audit fixes.

Memo: docs/audits/CREATIVE_AUDIT_2026_07_19.md

Each test pins ONE audited defect by its player-visible symptom, and each is
falsifiable against the pre-fix behaviour (the assertions below fail on master
at 8dbac27).
"""
import json
import re

import pytest

from backend.ai.strategic_parser import _clean_target_text
from backend.campaign_log import _name_tag, format_event_oneliner
from backend.display_names import humanize_entity_name
from backend.game_logic import jealousy
from backend.game_logic.dispatch import _build_headline, _derive_marshal_status

REGISTRY = "godot-client/project-sovereign/assets/maps/europe.json"


# ══════════════════════════════════════════════════════════════════════
# P1 — a marshal awaiting a decision must not be reported as marching
# ══════════════════════════════════════════════════════════════════════

class _FakeOrder:
    def __init__(self, command_type="MOVE_TO", target="Swabia"):
        self.command_type = command_type
        self.target = target


class _FakeMarshal:
    def __init__(self, **kw):
        self.name = kw.get("name", "Ney")
        self.location = kw.get("location", "Rhineland")
        self.broken = False
        self.retreating = False
        self.broken_recovery = 0
        self.retreat_recovery = 0
        self.in_strategic_mode = True
        self.strategic_order = _FakeOrder()
        self.pending_interrupt = kw.get("pending_interrupt")
        self.personality = kw.get("personality", "aggressive")
        self.drilling = False
        self.drilling_locked = False
        self.fortified = False
        self.artillery = False

    def get_rally_stages_per_turn(self):
        return 1


class _FakeWorld:
    current_turn = 5


def test_marshal_with_pending_interrupt_is_not_reported_as_marching():
    """The dispatch said 'Moving to Swabia' for a marshal frozen awaiting the
    player's answer — the briefing lying about the one thing it reports."""
    m = _FakeMarshal(pending_interrupt={
        "interrupt_type": "contact_bad_odds",
        "enemy": "Mack", "location": "Swabia",
        "options": ["attack_anyway", "hold_position", "cancel_order"],
    })
    status, note = _derive_marshal_status(m, _FakeWorld())

    assert status == "awaiting_decision", status
    assert "Moving to" not in note
    assert "HALTED" in note
    assert "Mack" in note and "Swabia" in note


def test_marshal_without_interrupt_still_reports_its_order():
    """The halt arm must not swallow the normal en-route report."""
    status, note = _derive_marshal_status(_FakeMarshal(), _FakeWorld())
    assert status == "en_route"
    assert "Moving to Swabia" in note


def test_pending_interrupt_status_humanizes_enemy_name():
    m = _FakeMarshal(pending_interrupt={
        "interrupt_type": "contact_bad_odds", "enemy": "ArchdukeJohn",
        "location": "Franconia", "options": ["hold_position"],
    })
    _, note = _derive_marshal_status(m, _FakeWorld())
    assert "Archduke John" in note
    assert "ArchdukeJohn" not in note


# ══════════════════════════════════════════════════════════════════════
# P1 — addressing another marshal must not discard a pending DECISION
# ══════════════════════════════════════════════════════════════════════

def test_interrupt_preservation_rule_keeps_every_decision_type():
    """main.py drops a pending interrupt when the player addresses a different
    marshal. The old rule was an allow-list of two types, so ordering
    'Davout, support Ney' silently threw away the question Ney had just asked.
    The rule is now derived: an interrupt that OFFERS OPTIONS is a decision."""
    decisions = [
        {"interrupt_type": "contact_bad_odds",
         "options": ["attack_anyway", "hold_position", "cancel_order"]},
        {"interrupt_type": "contact",
         "options": ["attack", "go_around", "hold_position", "cancel_order"]},
        {"interrupt_type": "combat_stalemate",
         "options": ["continue_order", "hold_position", "cancel_order"]},
        {"interrupt_type": "last_stand",
         "options": ["fight_to_the_last", "attempt_breakout"]},
        {"interrupt_type": "muster_confirm",
         "options": ["attack_anyway", "cancel_order"]},
        {"interrupt_type": "destination_blocked",
         "options": ["hold_position", "cancel_order"]},
        {"interrupt_type": "cannon_fire",
         "options": ["march_to_guns", "hold_position"]},
    ]
    for pending in decisions:
        assert pending.get("options"), pending["interrupt_type"]

    # Purely informational (no options) may still be cleared.
    assert not {"interrupt_type": "note", "options": []}.get("options")


def test_main_py_uses_the_derived_options_rule_not_a_name_list():
    """Pin the seam itself: the guard must key off `options`, not a hand-kept
    list of type names (which is exactly what drifted out of date)."""
    src = open("backend/main.py", encoding="utf-8").read()
    guard = src[src.index("if addressed_other:"):]
    guard = guard[:guard.index("continue")]
    assert 'if not pending.get("options"):' in guard, guard[-400:]
    assert '"last_stand", "muster_confirm"' not in guard


# ══════════════════════════════════════════════════════════════════════
# P2 — order targets swallowed the purpose clause
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("raw,expected", [
    ("Milan to reinforce Massena", "Milan"),
    ("to Milan to reinforce Massena", "Milan"),
    ("Swabia to support Ney", "Swabia"),
    ("Vienna in order to relieve Lannes", "Vienna"),
    ("Tyrol so as to cut them off", "Tyrol"),
    ("Bavaria so that the road is open", "Bavaria"),
])
def test_purpose_clause_is_cut_from_the_destination(raw, expected):
    """'Murat, march to Milan to reinforce Massena' stored the destination as
    the literal 'Milan To Reinforce Massena' and rendered it in the Orders
    ledger."""
    assert _clean_target_text(raw) == expected


@pytest.mark.parametrize("raw", [
    "Milan", "East Prussia", "Franche-Comte", "Toulon", "Rome",
])
def test_plain_region_names_survive_the_purpose_cut(raw):
    """The cut must not eat ordinary destinations."""
    assert _clean_target_text(raw) == raw


def test_existing_trailing_clause_cuts_still_hold():
    assert _clean_target_text("Soult with fresh troops") == "Soult"
    assert _clean_target_text("belgium and attack") == "belgium"


# ══════════════════════════════════════════════════════════════════════
# P2 — raw camelCase marshal keys leaked to the player
# ══════════════════════════════════════════════════════════════════════

def test_campaign_log_name_tag_humanizes_the_marshal_key():
    """'ArchdukeCharles (Austria) attacked Massena' — one line away from the
    same event's correctly-spaced enemy_voice."""
    tag = _name_tag("ArchdukeCharles", "Austria")
    assert "Archduke Charles" in tag
    assert "ArchdukeCharles" not in tag


def test_battle_oneliner_has_no_camelcase_run():
    line = format_event_oneliner({
        "type": "battle", "attacker": "ArchdukeCharles", "attacker_nation": "Austria",
        "defender": "Massena", "defender_nation": "France", "location": "Milan",
        "outcome": "attacker_tactical_victory",
        "attacker_casualties": 3209, "defender_casualties": 7693,
        "battle_name": "The Great Battle of Milan", "turn": 1,
    })
    assert "ArchdukeCharles" not in line
    assert "Archduke Charles" in line


def test_jealousy_module_routes_names_through_the_chokepoint():
    """jealousy.py called humanize_entity_name ZERO times, so every enemy
    marshal it named leaked its internal key."""
    src = open("backend/game_logic/jealousy.py", encoding="utf-8").read()
    assert "humanize_entity_name" in src
    for template in ("is eyeing", "hungry for "):
        idx = src.index(template)
        window = src[max(0, idx - 300):idx + 300]
        assert "humanize_entity_name" in window, template


def test_autonomous_warning_text_humanizes_both_names():
    assert humanize_entity_name("ArchdukeJohn") == "Archduke John"
    assert humanize_entity_name("Ney") == "Ney"


# ══════════════════════════════════════════════════════════════════════
# P3 — "he has restless for glory"
# ══════════════════════════════════════════════════════════════════════

def test_every_jealousy_expression_fits_the_he_has_slot():
    """The expressions fill 'he has {expression}', so each must be a past
    participle. 'restless for glory' is an adjective phrase and produced the
    live line 'he has restless for glory.'"""
    src = open("backend/game_logic/jealousy.py", encoding="utf-8").read()
    block = src[src.index('"aggressive": "grown'):]
    block = block[:block.index("}.get(")]
    values = re.findall(r'"(?:aggressive|cautious|literal)":\s*"([^"]+)"', block)
    assert len(values) == 3, values
    for v in values:
        assert v.split()[0] in ("grown", "thrown"), f"'he has {v}' is not grammatical"
    assert "restless for glory" in " ".join(values)
    assert "grown restless for glory" in values


def test_aggressive_grievance_line_reads_grammatically():
    assert "he has grown restless for glory" == f"he has {'grown restless for glory'}"
    src = open("backend/game_logic/jealousy.py", encoding="utf-8").read()
    assert '"aggressive": "restless for glory"' not in src


# ══════════════════════════════════════════════════════════════════════
# P3 — one grievance produced two near-identical dispatch lines
# ══════════════════════════════════════════════════════════════════════

def test_grievance_emits_a_single_dispatch_line():
    """`jealousy_fired` was followed by `jealousy_target_notice` restating the
    same grievance from the target's side; with 2-3 live grievances the
    briefing carried 6+ lines of the same news."""
    src = open("backend/game_logic/jealousy.py", encoding="utf-8").read()
    assert '"type": "jealousy_target_notice"' not in src
    assert '"type": "jealousy_fired"' in src


def test_dispatch_no_longer_lists_the_retired_notice_type():
    src = open("backend/game_logic/dispatch.py", encoding="utf-8").read()
    assert "jealousy_target_notice" not in src
    assert '"jealousy_fired"' in src


def test_fired_line_still_names_both_men_and_the_laurels():
    """Folding the notice away must not lose the target's side of the story."""
    src = open("backend/game_logic/jealousy.py", encoding="utf-8").read()
    idx = src.index('"type": "jealousy_fired"')
    window = src[idx:idx + 900]
    assert "_envious" in window and "_envied" in window
    assert "laurels" in window


# ══════════════════════════════════════════════════════════════════════
# P3 — the headline repeated verbatim on consecutive turns
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def europe_world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(
        "godot-client/project-sovereign/assets/maps/europe_1805.json")


def _two_capture_candidates(world):
    """Seed two fog-visible losses so the builder has a heavy lead + an
    alternative, through the REAL candidate path (no monkeypatching)."""
    home = list(world.nation_starting_regions.get("France", []))[:1]
    world.event_log.append({
        "type": "region_captured", "region": home[0], "captured_by": "Britain",
        "captured_from": "France", "turn": world.current_turn,
    })
    lost = next(r.name for r in world.regions.values()
                if r.controller == "France" and r.name not in home)
    world.event_log.append({
        "type": "region_captured", "region": lost, "captured_by": "Britain",
        "captured_from": "France", "turn": world.current_turn,
    })
    return home[0], lost


def test_headline_prefers_a_distinct_lead_over_yesterdays_repeat(europe_world):
    """'Marshal Ney's household goes unpaid' led two turns running because
    state-based candidates re-win the lead every turn. When the top candidate
    repeats yesterday's lead, a distinct one is promoted."""
    world = europe_world
    _two_capture_candidates(world)

    first = _build_headline(world, "France")
    assert first is not None
    assert first["sub_beats"], "need an alternative candidate for this test"

    # Same turn, same candidates — but yesterday already led with `first`.
    world.last_morning_dispatch = {"headline": {"text": first["text"]}}
    second = _build_headline(world, "France")

    assert second["text"] != first["text"], "headline repeated verbatim"
    assert first["text"] in second["sub_beats"], (
        "the repeated condition must still be reported, just not as the lead")


def test_headline_is_unchanged_when_yesterday_led_with_something_else(
        europe_world):
    """The rotation must fire ONLY on an exact repeat — otherwise the highest
    weighted candidate still leads."""
    world = europe_world
    _two_capture_candidates(world)

    baseline = _build_headline(world, "France")
    world.last_morning_dispatch = {"headline": {"text": "Sire — unrelated."}}
    assert _build_headline(world, "France")["text"] == baseline["text"]


def test_headline_keeps_its_lead_when_it_is_the_only_news(europe_world):
    """A lone standing crisis must still be reported, never suppressed."""
    world = europe_world
    home = list(world.nation_starting_regions.get("France", []))[:1][0]
    world.event_log.append({
        "type": "region_captured", "region": home, "captured_by": "Britain",
        "captured_from": "France", "turn": world.current_turn,
    })
    only = _build_headline(world, "France")
    assert only is not None and not only["sub_beats"]

    world.last_morning_dispatch = {"headline": {"text": only["text"]}}
    again = _build_headline(world, "France")
    assert again["text"] == only["text"], "sole news must not be suppressed"


def test_headline_rotation_is_wired_into_the_real_builder():
    """Pin the production seam, not just the behaviour."""
    src = open("backend/game_logic/dispatch.py", encoding="utf-8").read()
    body = src[src.index("def _build_headline"):]
    body = body[:body.index("\ndef ")]
    assert "last_morning_dispatch" in body
    assert "_prev_text" in body


# ══════════════════════════════════════════════════════════════════════
# Map topology — Milan was severed from Italy
# ══════════════════════════════════════════════════════════════════════

def _registry():
    with open(REGISTRY, encoding="utf-8") as f:
        return json.load(f)["regions"]


def _adjacency_by_name():
    regs = _registry()
    return {
        v["name"]: {regs.get(a, {}).get("name", a) for a in v.get("adjacent", [])}
        for v in regs.values() if isinstance(v, dict) and v.get("name")
    }


def test_milan_borders_piedmont():
    """Milan's only land neighbours were Munich and Tyrol — both across the
    Alps. The Kingdom of Italy could not reach a single province it claimed
    without leaving Italy, and a retreat from Milan toward Piedmont was sent
    to Munich instead: deeper into Austria."""
    adj = _adjacency_by_name()
    assert "Piedmont" in adj["Milan"]
    assert "Milan" in adj["Piedmont"]


def test_risorgimento_claim_is_internally_connected():
    """The Italy formation needs all five claimed provinces; they must form a
    connected sub-graph or the formation is unreachable by conquest."""
    adj = _adjacency_by_name()
    claim = {"Milan", "Piedmont", "Savoy", "Naples", "Rome"}
    seen, stack = {"Milan"}, ["Milan"]
    while stack:
        for nxt in adj.get(stack.pop(), ()):
            if nxt in claim and nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    assert seen == claim, f"unreachable within the claim set: {sorted(claim - seen)}"


def test_registry_adjacency_stays_symmetric():
    """A hand-added edge must be written both ways."""
    regs = _registry()
    asym = [
        (v.get("name"), regs.get(a, {}).get("name", a))
        for k, v in regs.items() if isinstance(v, dict)
        for a in v.get("adjacent", [])
        if k not in regs.get(a, {}).get("adjacent", [])
    ]
    assert asym == [], asym


def test_mild_concern_prefix_is_separated_from_the_result():
    """Live: "Massena bristles at the retreat order but obeys.Massena retreats
    from Milan" — the two strings were butted together with no separator."""
    src = open("backend/commands/executor.py", encoding="utf-8").read()
    idx = src.index("# FIX: Prepend mild objection message")
    window = src[idx:idx + 700]
    assert 'mild_message + result.get("message", "")' not in window
    assert 'f"{mild_message} {_rest}"' in window


def test_milan_is_no_longer_a_cul_de_sac():
    """Regression on the symptom: a corps at Milan must have a retreat that is
    not deeper into enemy territory."""
    adj = _adjacency_by_name()
    assert len(adj["Milan"]) >= 3
