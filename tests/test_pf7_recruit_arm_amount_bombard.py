"""PF-7 (Combat Overhaul Phase 6 — Parser & Play-Friction Cleanup).

Three silent drops, made non-silent (surface or reject — never honor an
arbitrary arm/count, which is an escalated balance change):

  A. ARM  — "recruit 5000 artillery for <infantry marshal>" ignored the arm.
            The mock parser now recognizes "artillery", feeding the existing
            soft-correction seam ("Marshal X commands infantry, Sire.").
  B. AMOUNT — the requested troop count vanished. It is now NOTED (recruitment
            is drafted in fixed per-arm corps; the batch size is unchanged).
  C. BOMBARD — "bombard" from a marshal with no guns silently became a melee.
            It is now rejected clearly before any AP spend / battle.
"""
import contextlib
import io

from backend.models.world_state import WorldState, INFANTRY_RECRUIT_AMOUNT
from backend.ai.llm_client import LLMClient
from backend.commands.executor import CommandExecutor
from backend.models.marshal import Marshal


def _suppress():
    return contextlib.redirect_stdout(io.StringIO())


# ── A. ARM ──────────────────────────────────────────────────────────────────

def test_mock_parser_recognizes_artillery_arm():
    client = LLMClient()
    result = client._parse_with_mock("recruit 5000 artillery for Davout")
    assert result.action == "recruit"
    assert result.requested_type == "artillery"


def test_horse_artillery_still_parses_as_cavalry():
    """Cavalry is checked first, so "horse artillery" stays cavalry."""
    client = LLMClient()
    result = client._parse_with_mock("recruit horse artillery for Murat")
    assert result.requested_type == "cavalry"


def test_gun_substring_does_not_collide_with_burgundy():
    """Review-fix regression: the bare substring "gun" is inside "Burgundy"
    (bur-GUN-dy); the word-boundary match must NOT misread an explicit infantry
    recruit at Burgundy as an artillery request."""
    client = LLMClient()
    result = client._parse_with_mock("recruit infantry at Burgundy")
    assert result.action == "recruit"
    assert result.requested_type == "infantry"


def test_explicit_artillery_word_still_detected():
    """The word-boundary regex still recognizes the real artillery keywords."""
    client = LLMClient()
    for phrase in ["recruit artillery for Drouot", "recruit guns for Drouot",
                   "recruit a battery for Drouot"]:
        assert client._parse_with_mock(phrase).requested_type == "artillery", phrase


def test_arm_mismatch_soft_correction_fires_for_artillery():
    world = WorldState()
    executor = CommandExecutor()
    gs = {"world": world}
    world.get_marshal("Davout").location = "Paris"  # capital -> uncapped
    with _suppress():
        res = executor._economy._execute_recruit(
            {"marshal": "Davout", "requested_type": "artillery",
             "raw_command": "recruit artillery for davout"}, gs)
    assert res["success"], res.get("message")
    # Mechanic unchanged: Davout is infantry, full batch.
    assert res["events"][0]["troops_added"] == INFANTRY_RECRUIT_AMOUNT
    assert "commands infantry" in res["message"]


def test_matching_arm_no_soft_correction():
    """FALSIFIABLE NEGATIVE: requesting the marshal's real arm -> no correction."""
    world = WorldState()
    executor = CommandExecutor()
    gs = {"world": world}
    world.get_marshal("Davout").location = "Paris"
    with _suppress():
        res = executor._economy._execute_recruit(
            {"marshal": "Davout", "requested_type": "infantry",
             "raw_command": "recruit infantry for davout"}, gs)
    assert "commands infantry" not in res["message"]


# ── B. AMOUNT ───────────────────────────────────────────────────────────────

def test_requested_amount_is_noted_not_honored():
    world = WorldState()
    executor = CommandExecutor()
    gs = {"world": world}
    world.get_marshal("Davout").location = "Paris"
    with _suppress():
        res = executor._economy._execute_recruit(
            {"marshal": "Davout", "raw_command": "recruit 5000 davout"}, gs)
    # NOT honored — still the fixed infantry batch.
    assert res["events"][0]["troops_added"] == INFANTRY_RECRUIT_AMOUNT
    # But acknowledged, naming both figures.
    msg = res["message"]
    assert "5,000" in msg and "10,000" in msg and "noted" in msg


def test_no_number_no_amount_note():
    """FALSIFIABLE NEGATIVE: a recruit with no number gets no acknowledgment."""
    world = WorldState()
    executor = CommandExecutor()
    gs = {"world": world}
    world.get_marshal("Davout").location = "Paris"
    with _suppress():
        res = executor._economy._execute_recruit(
            {"marshal": "Davout", "raw_command": "recruit for davout"}, gs)
    assert "noted" not in res["message"]


# ── C. BOMBARD GUARD ────────────────────────────────────────────────────────

def _bombard_world():
    world = WorldState()
    world.opening_attack_guidance_shown = True  # skip the one-time tutorial
    return world


def test_no_guns_bombard_rejected_no_melee():
    world = _bombard_world()
    executor = CommandExecutor()
    gs = {"world": world}
    wellington = world.get_marshal("Wellington")
    before = wellington.strength
    soult = Marshal("Soult", wellington.location, 40000, "aggressive", "France")
    world.marshals["Soult"] = soult
    with _suppress():
        res = executor._execute_attack(
            soult, "Wellington", world, gs,
            command={"raw_command": "Soult bombard Wellington"})
    assert res["success"] is False
    assert "no guns" in res["message"].lower() or "cannot bombard" in res["message"].lower()
    assert world.get_marshal("Wellington").strength == before  # no melee happened


def test_artillery_bombard_still_routes():
    """FALSIFIABLE NEGATIVE: an artillery marshal's bombard is NOT rejected — it
    routes to bombardment (the guard is scoped to no-guns marshals)."""
    world = _bombard_world()
    executor = CommandExecutor()
    gs = {"world": world}
    wellington = world.get_marshal("Wellington")
    neighbor = world.get_region(wellington.location).adjacent_regions[0]
    drouot = Marshal("Drouot", neighbor, 25000, "cautious", "France",
                     movement_range=1, artillery=True)
    world.marshals["Drouot"] = drouot
    with _suppress():
        res = executor._execute_attack(
            drouot, "Wellington", world, gs,
            command={"raw_command": "Drouot bombard Wellington"})
    assert "no guns" not in res["message"].lower()


def test_plain_attack_not_guarded():
    """FALSIFIABLE NEGATIVE: a normal 'attack' (no bombard verb) by a no-guns
    marshal is unaffected."""
    world = _bombard_world()
    executor = CommandExecutor()
    gs = {"world": world}
    wellington = world.get_marshal("Wellington")
    soult = Marshal("Soult", wellington.location, 40000, "aggressive", "France")
    world.marshals["Soult"] = soult
    with _suppress():
        res = executor._execute_attack(
            soult, "Wellington", world, gs,
            command={"raw_command": "Soult attack Wellington"})
    assert "no guns" not in res["message"].lower()


def test_ai_caller_command_none_unaffected():
    """FALSIFIABLE NEGATIVE: an AI/strategic caller passes command=None and is
    never subject to the player-only bombard guard."""
    world = _bombard_world()
    executor = CommandExecutor()
    gs = {"world": world}
    wellington = world.get_marshal("Wellington")
    soult = Marshal("Soult", wellington.location, 40000, "aggressive", "France")
    world.marshals["Soult"] = soult
    with _suppress():
        res = executor._execute_attack(soult, "Wellington", world, gs)
    assert "no guns" not in res["message"].lower()
