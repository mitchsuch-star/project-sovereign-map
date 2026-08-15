"""NP-1 — The Emperor's Hand (NAPOLEON_SPEC.md §4, gate §14.1 Q1◆).

Commanding yourself: sovereign address normalization at the top of
``CommandParser.parse`` (the CR-4 raw-string-rewrite precedent, so the fast
parser / LLM / fuzzy matching / strategic detection agree by construction),
the first-person object carryover ("Ney, support me"), the no-friction
guards at the executor seams, and the 1-AP sovereign strategic discount.

Everything is gated on a sovereign standing in the player roster — the
dormancy arm pins that a sovereign-free world parses byte-identically.
"""

import pytest

from backend.ai.parser_eval import build_llm_game_state, build_world
from backend.commands.context_carryover import (
    _player_sovereign_name,
    resolve_context_references,
)
from backend.commands.executor import CommandExecutor
from backend.commands.parser import (
    CommandParser,
    _find_player_sovereign,
    normalize_sovereign_address,
)
from backend.models.marshal import Marshal


# ════════════════════════════════════════════════════════════════════════
# Fixtures — the legacy world + an injected sovereign (no scenario contact)
# ════════════════════════════════════════════════════════════════════════

def add_sovereign(world, name="Napoleon", location="Paris", strength=10000):
    m = Marshal(name=name, location=location, strength=strength,
                personality="sovereign", nation=world.player_nation,
                spawn_location=location)
    world.marshals[name] = m
    return m


@pytest.fixture()
def sovereign_world():
    w = build_world("legacy")
    add_sovereign(w)
    return w


@pytest.fixture()
def plain_world():
    return build_world("legacy")


@pytest.fixture()
def parser():
    return CommandParser()


def parse(parser, world, text):
    return parser.parse(text, build_llm_game_state(world), world=world)


# ════════════════════════════════════════════════════════════════════════
# The normalization unit (§4.1)
# ════════════════════════════════════════════════════════════════════════

class TestNormalization:
    @pytest.mark.parametrize("text,expected", [
        ("Emperor, attack Wellington", "Napoleon, attack Wellington"),
        ("the Emperor, attack Wellington", "Napoleon, attack Wellington"),
        ("The Emperor: hold Belgium", "Napoleon, hold Belgium"),
        ("the Emperor will march to Belgium", "Napoleon, will march to Belgium"),
        ("I will march to Belgium", "Napoleon, march to Belgium"),
        ("I'll attack Wellington", "Napoleon, attack Wellington"),
        ("I attack Wellington", "Napoleon, attack Wellington"),
        ("I shall advance on Belgium", "Napoleon, advance on Belgium"),
        ("march to Belgium myself", "Napoleon, march to Belgium myself"),
        ("take the field in person", "Napoleon, take the field in person"),
    ])
    def test_rewrites(self, text, expected):
        assert normalize_sovereign_address(text, "Napoleon") == expected

    @pytest.mark.parametrize("text", [
        # (a) an address token always wins — corpus row 3953's form.
        "Ney, I want you to move to Lorraine",
        "Murat, march to Belgium myself",
        # (b) military verbs only — no diplomatic first-person rewrites.
        "I offer peace to Austria",
        "I want you to attack",
        "I think we should retreat",
        # (c) questions stay questions.
        "Can I attack Vienna?",
        "How do I attack?",
        "Could I take Belgium",
        # bare "emperor" mid-thought never rewrites.
        "tell the men the emperor watches them",
    ])
    def test_never_rewrites(self, text):
        assert normalize_sovereign_address(text, "Napoleon") == text

    def test_no_sovereign_no_rewrite(self):
        assert normalize_sovereign_address(
            "I will march to Belgium", "") == "I will march to Belgium"

    def test_find_player_sovereign(self, sovereign_world, plain_world):
        assert _find_player_sovereign(sovereign_world) == "Napoleon"
        assert _find_player_sovereign(plain_world) is None

    def test_find_sovereign_ignores_enemy_sovereign(self, plain_world):
        # An ENEMY sovereign never grants the player first-person address.
        m = Marshal(name="Kaiser", location="Bavaria", strength=10000,
                    personality="sovereign", nation="Austria")
        plain_world.marshals["Kaiser"] = m
        assert _find_player_sovereign(plain_world) is None


# ════════════════════════════════════════════════════════════════════════
# Parse integration (mock parser end to end)
# ════════════════════════════════════════════════════════════════════════

class TestParseIntegration:
    def test_emperor_address_resolves(self, parser, sovereign_world):
        result = parse(parser, sovereign_world, "Emperor, attack Wellington")
        assert result["success"] is True
        assert result["command"]["marshal"] == "Napoleon"
        assert result["command"]["action"] == "attack"

    def test_first_person_march_resolves(self, parser, sovereign_world):
        result = parse(parser, sovereign_world, "I will march to Belgium")
        assert result["success"] is True
        assert result["command"]["marshal"] == "Napoleon"

    def test_myself_suffix_resolves_and_never_fabricates(
            self, parser, sovereign_world):
        result = parse(parser, sovereign_world, "march to Belgium myself")
        assert result["success"] is True
        assert result["command"]["marshal"] == "Napoleon"
        # The marker itself must never fuzzy-match into a province.
        assert (result["command"].get("target") or "") != "Myself"

    def test_addressed_first_person_still_the_addressee(
            self, parser, sovereign_world):
        # Corpus row 3953's clause, now in a sovereign world: the address
        # token wins over the first-person signal.
        result = parse(parser, sovereign_world,
                       "Ney, I want you to move to Lorraine")
        assert result["command"]["marshal"] == "Ney"

    def test_question_stays_help(self, parser, sovereign_world):
        result = parse(parser, sovereign_world, "Can I attack Wellington?")
        assert result["command"]["marshal"] != "Napoleon"
        assert result["command"]["action"] in ("help", "unknown")

    def test_dormancy_no_sovereign_no_napoleon(self, parser, plain_world):
        result = parse(parser, plain_world, "I will march to Belgium")
        assert (result.get("command") or {}).get("marshal") != "Napoleon"


# ════════════════════════════════════════════════════════════════════════
# Carryover: first-person object pronouns (§4.1 CR-4 sibling)
# ════════════════════════════════════════════════════════════════════════

class TestFirstPersonCarryover:
    def test_support_me_resolves_to_sovereign(self, sovereign_world):
        sovereign_world.command_history = []
        result = resolve_context_references("Ney, support me", sovereign_world)
        assert result["kind"] == "rewrite"
        assert "Napoleon" in result["command"]
        assert " me" not in result["command"]

    def test_reinforce_us_resolves(self, sovereign_world):
        sovereign_world.command_history = []
        result = resolve_context_references(
            "Davout, reinforce us at once", sovereign_world)
        assert result["kind"] == "rewrite"
        assert "Napoleon" in result["command"]

    def test_object_position_only(self, sovereign_world):
        # Subject-position / partitive first person never rewrites here
        # (the parse-top normalization owns subject position).
        sovereign_world.command_history = []
        for text in ("Ney, give me a report", "all of us hold the line"):
            result = resolve_context_references(text, sovereign_world)
            assert result["kind"] in ("pass", "error"), text

    def test_captured_sovereign_not_resolved(self, sovereign_world):
        sovereign_world.command_history = []
        sovereign_world.marshals["Napoleon"].captured_by = "Austria"
        assert _player_sovereign_name(sovereign_world) is None
        result = resolve_context_references("Ney, support me", sovereign_world)
        assert result["kind"] == "pass"

    def test_no_sovereign_passes(self, plain_world):
        plain_world.command_history = []
        result = resolve_context_references("Ney, support me", plain_world)
        assert result["kind"] == "pass"

    def test_him_never_resolves_to_sovereign(self, sovereign_world):
        # him/her/them resolve only through _last_enemy_target — the enemy
        # filter is structural; the sovereign is never "him" to the player.
        sovereign_world.command_history = [
            {"marshal": "Ney", "action": "scout", "target": "Napoleon",
             "raw_input": "Ney, scout Napoleon", "turn": 1},
        ]
        result = resolve_context_references("Ney, attack him", sovereign_world)
        assert "Napoleon" not in (result.get("command") or "")


# ════════════════════════════════════════════════════════════════════════
# The no-friction guards + the 1-AP seam (§4.2)
# ════════════════════════════════════════════════════════════════════════

class TestNoFrictionAndAP:
    def test_sovereign_order_never_objects(self, sovereign_world):
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"marshal": "Napoleon", "action": "defend"}},
            {"world": sovereign_world})
        assert result.get("success") is True
        assert sovereign_world.pending_objection is None

    def test_sovereign_strategic_order_costs_one_ap(
            self, parser, sovereign_world):
        executor = CommandExecutor()
        start_ap = sovereign_world.actions_remaining
        parsed = parse(parser, sovereign_world, "Napoleon, march to Belgium")
        assert parsed["success"] is True
        result = executor.execute(parsed, {"world": sovereign_world})
        assert result.get("success") is True
        assert sovereign_world.actions_remaining == start_ap - 1
        assert "the Emperor commands in his own name" in result["message"]

    def test_control_marshal_strategic_order_costs_two_ap(
            self, parser, sovereign_world):
        executor = CommandExecutor()
        start_ap = sovereign_world.actions_remaining
        parsed = parse(parser, sovereign_world, "Ney, march to Belgium")
        assert parsed["success"] is True
        result = executor.execute(parsed, {"world": sovereign_world})
        if result.get("success"):  # Ney may object to nothing here — MOVE_TO
            assert sovereign_world.actions_remaining == start_ap - 2

    def test_sovereign_strategic_never_stages_objection(self, sovereign_world):
        # Even a SUPPORT toward a hostile relationship stays silent.
        sovereign_world.marshals["Napoleon"].set_relationship("Ney", -2)
        executor = CommandExecutor()
        parsed = {
            "success": True,
            "command": {"marshal": "Napoleon", "action": "move",
                        "target": "Ney", "confidence": 1.0},
            "is_strategic": True,
            "strategic_type": "SUPPORT",
            "strategic_score": 80,
            "ambiguity": 5,
            "mode": "mock",
        }
        # route through the executor's strategic path
        parsed["command"]["is_strategic"] = True
        parsed["command"]["strategic_type"] = "SUPPORT"
        executor.execute(parsed, {"world": sovereign_world})
        assert sovereign_world.pending_strategic_objection is None
