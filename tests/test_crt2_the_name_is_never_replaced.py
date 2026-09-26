"""CRT-2 — "The name is never replaced" (the CR-6 triage, slice 2; build
contract = `docs/COMMAND_ROBUSTNESS_SPEC.md` §12.3; rows CQ-17, CQ-29, CQ-30
in `docs/BUG_FIXES.md`). CQ-30 landed as Score Mandate Chunk 3 SR-3a
(September 26, 2026); CQ-17 and CQ-29 landed as SR-3b the same day (the
classes after the CQ-30 block, with the fallen-object and placed-hold riders).

CQ-30, reproduced on this HEAD at the real `POST /command` before a line was
written: `Ney, attack Archduke Charls` and `Ney, attack Kutusof` each
answered "Your words named no foe our maps know, Sire — Ney marches on Mack
at Swabia, the nearest in sight" and FOUGHT MACK — an action point, a battle,
the Butcher's Bill — while the exact name refused honestly and `Kutuzof`,
`Kutusov`, `Buxhowdn` asked. A one-letter slip on a FOGGED foe's name was
read as a DESCRIPTION (ESP-EV-4's disclose-and-proceed, right for "the
weakest enemy"), so the player named Charles and the game fought Mack.

The rule: a target run that is a NEAR MISS of any enemy on the roster —
matched omnisciently, answered fog-honestly — takes the ASK arm, naming no
hidden man and no hidden province; every description the ESP-EV-4 pins cover
still discloses and proceeds. Lever `combat_executor.A_NEAR_MISS_ASKS`.
"""

import pytest
from fastapi.testclient import TestClient

import backend.commands.combat_executor as CE
import backend.main as M
from backend.commands.parser import CommandParser


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def strengths(world):
    return {m.name: (m.location, int(m.strength)) for m in world.marshals.values()}


NEAR_MISSES = ["Ney, attack Archduke Charls", "Ney, attack Kutusof",
               "Ney, attack Kutuzof", "Ney, attack Buxhowdn"]


class TestANearMissOfARosterNameAsks:
    @pytest.mark.parametrize("utterance", NEAR_MISSES)
    def test_nothing_is_fought_and_the_question_is_staged(self, shipped, utterance):
        client, world = shipped
        before, ap = strengths(world), int(world.actions_remaining)
        data = post(client, utterance)
        assert strengths(world) == before, data.get("message")
        assert int(world.actions_remaining) == ap
        assert not data.get("battle_report") and not data.get("battle_diorama")
        assert data.get("clarification_kind") == "attack_target" or \
            data.get("success") is False, data.get("message")
        message = str(data.get("message") or "")
        assert "marches on Mack" not in message, "disclose-and-proceed fired"

    @pytest.mark.parametrize("utterance", NEAR_MISSES)
    def test_the_answer_names_no_hidden_man_and_no_hidden_province(self, shipped, utterance):
        """Charles stands at Carniola and Kutuzov at Podolia, both in fog.
        Either ASK is fog-honest: the near-miss arm's "No foe of that name is
        in sight" (the two slips that used to FIGHT), or the substitution
        arm's "will not charge at a guess" (`Kutuzof` / `Buxhowdn`, which the
        parser's own fuzzy pass already caught before this slice — the row
        measured them asking)."""
        client, world = shipped
        data = post(client, utterance)
        message = str(data.get("message") or "")
        for hidden in ("Carniola", "Podolia", "Charles", "Kutuzov", "Buxhowden"):
            assert hidden not in message, (hidden, message)
        assert "whom shall ney engage" in message.lower() or \
            "whom shall he engage" in message.lower(), message

    @pytest.mark.parametrize("utterance", ["Ney, attack Archduke Charls",
                                           "Ney, attack Kutusof"])
    def test_the_two_that_fought_take_the_near_miss_arm(self, shipped, utterance):
        client, world = shipped
        data = post(client, utterance)
        message = str(data.get("message") or "")
        assert message.startswith("No foe of that name is in sight"), message
        assert data.get("clarification_kind") == "attack_target", data.get("clarification_kind")

    def test_a_description_still_discloses_and_proceeds(self, shipped):
        """ESP-EV-4's founding case is untouched: a delegation with no name
        in it fights the nearest foe and SAYS so."""
        client, world = shipped
        ap = int(world.actions_remaining)
        data = post(client, "Ney, attack the weakest enemy")
        moved = (int(world.actions_remaining) < ap
                 or data.get("battle_report") or data.get("muster_preview")
                 or "Mack" in str(data.get("message") or ""))
        assert moved, data.get("message")

    def test_the_exact_fogged_name_still_says_no_intelligence(self, shipped):
        client, world = shipped
        ap = int(world.actions_remaining)
        data = post(client, "Ney, attack Kutuzov")
        assert "no intelligence" in str(data.get("message") or "").lower(), data.get("message")
        assert int(world.actions_remaining) == ap

    def test_the_lever_down_reproduces_the_battle_against_mack(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(CE, "A_NEAR_MISS_ASKS", False)
        data = post(client, "Ney, attack Archduke Charls")
        assert "marches on Mack" in str(data.get("message") or "") or \
            data.get("battle_report") or data.get("muster_preview"), data.get("message")


# ═══════════════════════════════════════════════════════════════════════
# SR-3b (Score Mandate Chunk 3, September 26, 2026) — CRT-2's other rows,
# all at the real `POST /command` on the shipped 1805 boot. ONE rule, three
# roads: the name the sentence gives is the one acted on — or the order is
# refused free, saying which name it read. CQ-17: a reward goes to its
# OBJECT. CQ-29: a named province that does not resolve is never replaced
# by the capital. Rider: a hold the GAME placed discloses no reading.
# ═══════════════════════════════════════════════════════════════════════

import backend.ai.llm_client as LC  # noqa: E402
import backend.commands.economy_executor as EE  # noqa: E402
import backend.commands.parser as P  # noqa: E402
import backend.commands.strategic_executor as SE  # noqa: E402

READING_NOTE = "as the province nearest your order"


def _snapshot(world):
    return {
        "gold": dict(world.nation_gold),
        "admin": int(world.admin_actions_remaining),
        "ap": int(world.actions_remaining),
        "pensions": {m.name: int(getattr(m, "pension", 0) or 0)
                     for m in world.marshals.values()},
        "estates": {m.name: list(getattr(m, "dotation_regions", []) or [])
                    for m in world.marshals.values()},
        "strength": {m.name: int(m.strength) for m in world.marshals.values()},
    }


def _owe(world, name, steps=3):
    marshal = world.get_marshal(name)
    marshal.expectation_steps = steps
    return marshal


def _stage_rewards(world):
    for name in ("Ney", "Davout"):
        _owe(world, name)
    world.nation_gold["France"] = 5000


def _stage_a_conquest(world, province="Swabia"):
    _stage_rewards(world)
    world.get_region(province).controller = world.player_nation
    for hook in ("invalidate_active_nations_cache",
                 "invalidate_bloc_members_cache"):
        fn = getattr(world, hook, None)
        if callable(fn):
            fn()


def _lannes_falls(world):
    world.destroy_marshal(world.get_marshal("Lannes"), cause="test")


class TestARewardGoesToItsObject:
    """CQ-17, reproduced on the pre-slice tree: `Davout, grant Ney a rente`
    pensioned DAVOUT, `Davout, revoke Ney's rente` withdrew DAVOUT's, and
    with Swabia conquered `Davout, endow Ney with Swabia` endowed DAVOUT for
    200 gold — irreversibly, since no verb takes an estate back."""

    def test_the_rente_goes_to_the_man_named(self, shipped):
        client, world = shipped
        _stage_rewards(world)
        before = _snapshot(world)
        data = post(client, "Davout, grant Ney a rente")
        after = _snapshot(world)
        assert data.get("success") is True, data.get("message")
        assert after["pensions"]["Ney"] > 0, data.get("message")
        assert after["pensions"]["Davout"] == before["pensions"]["Davout"]
        assert after["admin"] == before["admin"] - 1
        assert "Marshal Ney is granted" in str(data.get("message"))

    def test_the_revoke_takes_from_the_man_named(self, shipped):
        client, world = shipped
        _stage_rewards(world)
        world.get_marshal("Ney").pension = 80
        world.get_marshal("Davout").pension = 60
        data = post(client, "Davout, revoke Ney's rente")
        assert world.get_marshal("Ney").pension == 0, data.get("message")
        assert world.get_marshal("Davout").pension == 60, data.get("message")

    def test_the_estate_goes_to_the_man_named(self, shipped):
        client, world = shipped
        _stage_a_conquest(world)
        before = _snapshot(world)
        data = post(client, "Davout, endow Ney with Swabia")
        after = _snapshot(world)
        assert "Swabia" in after["estates"]["Ney"], data.get("message")
        assert after["estates"]["Davout"] == before["estates"]["Davout"]
        assert after["pensions"] == before["pensions"]
        assert after["gold"]["France"] == before["gold"]["France"] - 200

    @pytest.mark.parametrize("line", ["grant Ney a rente",
                                      "Berthier, grant Ney a rente"])
    def test_an_unaddressed_or_desk_addressed_reward_is_unchanged(self, shipped, line):
        client, world = shipped
        _stage_rewards(world)
        data = post(client, line)
        assert world.get_marshal("Ney").pension > 0, data.get("message")
        assert world.get_marshal("Davout").pension == 0, data.get("message")

    def test_a_lone_addressee_is_still_the_recipient(self, shipped):
        client, world = shipped
        _stage_rewards(world)
        data = post(client, "Ney, take a rente")
        assert world.get_marshal("Ney").pension > 0, data.get("message")
        assert all(int(getattr(m, "pension", 0) or 0) == 0
                   for m in world.marshals.values() if m.name != "Ney")

    def test_the_helper_names_the_object(self, shipped):
        _, world = shipped
        roster = P._extract_player_marshal_names(world, "France")
        read = P.reward_recipient_from_text
        assert read("Davout, grant Ney a rente", roster, world) == "Ney"
        assert read("Marshal Davout, endow Ney with Swabia", roster, world) == "Ney"
        assert read("Davout, revoke Ney's rente", roster, world) == "Ney"
        assert read("grant Ney a rente", roster, world) is None
        assert read("Ney, grant yourself a rente", roster, world) is None

    def test_the_lever_down_pays_the_addressee(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(P, "A_REWARD_GOES_TO_ITS_OBJECT", False)
        _stage_rewards(world)
        post(client, "Davout, grant Ney a rente")
        assert world.get_marshal("Davout").pension > 0
        assert world.get_marshal("Ney").pension == 0


class TestAFallenObjectIsNamedAsFallen:
    """The rule's rider: a reward naming one of our FALLEN answers with the
    desk's own sentence (DESK-15) — never "Did you mean Ney?" (what the
    recipient rule alone produced) and never "Whose household…?" (the
    pre-slice answer to the unaddressed form)."""

    @pytest.mark.parametrize("line", ["Davout, grant Lannes a rente",
                                      "grant Lannes a rente"])
    def test_the_rente_to_a_fallen_man_is_refused_by_name(self, shipped, line):
        client, world = shipped
        _stage_rewards(world)
        _lannes_falls(world)
        before = _snapshot(world)
        data = post(client, line)
        assert data.get("success") is False, data.get("message")
        assert _snapshot(world) == before, data.get("message")
        message = str(data.get("message"))
        assert "Marshal Lannes fell at" in message, message
        assert "Did you mean" not in message and "household" not in message

    def test_the_estate_for_a_fallen_man_is_refused_free(self, shipped):
        client, world = shipped
        _stage_a_conquest(world)
        _lannes_falls(world)
        before = _snapshot(world)
        data = post(client, "Davout, endow Lannes with Swabia")
        assert _snapshot(world) == before, data.get("message")
        assert "Marshal Lannes fell at" in str(data.get("message"))

    def test_a_living_object_is_untouched_by_a_fallen_man_elsewhere(self, shipped):
        client, world = shipped
        _stage_rewards(world)
        _lannes_falls(world)
        data = post(client, "Davout, grant Ney a rente")
        assert world.get_marshal("Ney").pension > 0, data.get("message")


class TestANamedProvinceIsNeverReplaced:
    """CQ-29, reproduced on the pre-slice tree with Soult at Paris and
    20,000 gold (the boot board masks it — no infantryman can reach the
    capital there): `recruit infantry in Swabbia` / `in Atlantis` /
    `in Franche-Comté` each raised 10,000 men AT PARIS for 654 gold."""

    @staticmethod
    def _stage(world):
        world.get_marshal("Soult").location = world.get_nation_capital("France")
        world.nation_gold["France"] = 20000

    @pytest.mark.parametrize("line", ["recruit infantry in Swabbia",
                                      "recruit infantry in Atlantis",
                                      "recruit cavalry in Atlantis",
                                      "recruit infantry in Swabbia, Sire",
                                      "recruit infantry in Swabbia at once",
                                      "recruit infantry in Austria"])
    def test_an_unresolved_province_is_refused_free(self, shipped, line):
        client, world = shipped
        self._stage(world)
        before = _snapshot(world)
        data = post(client, line)
        assert data.get("success") is False, data.get("message")
        assert _snapshot(world) == before, (line, data.get("message"))
        assert "nearest to capital" not in str(data.get("message"))

    def test_the_typo_is_read_as_the_province_it_meant_and_said_so(self, shipped):
        client, world = shipped
        self._stage(world)
        message = str(post(client, "recruit infantry in Swabbia").get("message"))
        assert "We do not control Swabia" in message, message
        assert f"read Swabia {READING_NOTE}" in message, message

    def test_a_place_the_map_does_not_hold_gets_the_matchers_answer(self, shipped):
        client, world = shipped
        self._stage(world)
        message = str(post(client, "recruit infantry in Atlantis").get("message"))
        assert "Region 'Atlantis' not found" in message, message

    def test_a_nation_is_answered_with_its_provinces(self, shipped):
        client, world = shipped
        self._stage(world)
        message = str(post(client, "recruit infantry in Austria").get("message"))
        assert "is a nation, not a province" in message, message

    def test_a_read_province_that_succeeds_discloses_the_reading(self, shipped):
        client, world = shipped
        self._stage(world)
        before = _snapshot(world)
        data = post(client, "recruit infantry in Lorrain")
        assert data.get("success") is True, data.get("message")
        assert _snapshot(world)["gold"]["France"] < before["gold"]["France"]
        message = str(data.get("message"))
        assert "for Lorraine" in message and f"read Lorraine {READING_NOTE}" in message

    def test_the_accented_province_resolves_as_the_plain_one(self, shipped):
        client, world = shipped
        self._stage(world)
        before = _snapshot(world)
        plain = post(client, "recruit infantry in Franche-Comte")
        plain_delta = (before["gold"]["France"] - int(world.nation_gold["France"]),
                       {k: v for k, v in _snapshot(world)["strength"].items()
                        if v != before["strength"][k]})
        M._reset_world_state()
        world = M.world
        self._stage(world)
        before = _snapshot(world)
        accented = post(client, "recruit infantry in Franche-Comté")
        accented_delta = (before["gold"]["France"] - int(world.nation_gold["France"]),
                          {k: v for k, v in _snapshot(world)["strength"].items()
                           if v != before["strength"][k]})
        assert plain.get("success") is True, plain.get("message")
        assert accented_delta == plain_delta, (plain.get("message"), accented.get("message"))
        assert "Franche-Comte" in str(accented.get("message"))

    @pytest.mark.parametrize("line", ["recruit infantry at once",
                                      "recruit infantry in haste",
                                      "recruit infantry in the capital",
                                      "recruit infantry in person"])
    def test_a_manner_is_not_a_place(self, shipped, line):
        """A manner or a generic names no province: the bare levy's capital
        road still takes it (never "Region 'Haste' not found")."""
        client, world = shipped
        self._stage(world)
        data = post(client, line)
        assert data.get("success") is True, data.get("message")
        assert "nearest to capital" in str(data.get("message"))

    @pytest.mark.parametrize("line", ["recruit infantry in Lorrain at once",
                                      "recruit infantry in Lorrain in haste"])
    def test_a_clause_after_the_province_ends_it(self, shipped, line):
        """"in Lorrain in haste" read "Lorrain In Haste" as one place and fell
        back to the capital — the defect itself, one clause later."""
        client, world = shipped
        self._stage(world)
        data = post(client, line)
        assert data.get("success") is True, data.get("message")
        message = str(data.get("message"))
        assert "for Lorraine" in message and f"read Lorraine {READING_NOTE}" in message

    def test_a_named_marshal_keeps_his_own_road(self, shipped):
        """The boundary, recorded not changed: a NAMED marshal levies where he
        stands (PF-7's surfaced correction, CN-1 + CN-2's recorded ruling);
        the province re-read only runs where the game chooses the man."""
        client, world = shipped
        self._stage(world)
        ney_at = world.get_marshal("Ney").location
        data = post(client, "Ney, recruit infantry in Swabbia")
        assert data.get("success") is True, data.get("message")
        assert f"at {ney_at}" in str(data.get("message"))

    def test_the_levers_down_raise_at_the_capital(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(LC, "A_NAMED_GROUND_IS_KEPT", False)
        monkeypatch.setattr(EE, "A_NAMED_PROVINCE_IS_NEVER_REPLACED", False)
        self._stage(world)
        data = post(client, "recruit infantry in Atlantis")
        assert "nearest to capital" in str(data.get("message")), data.get("message")


class TestBuildAndRepairReadTheirGround:
    """CQ-29's build/repair half: the ground was dropped ("Specify a region.
    Example: 'repair Paris'") — for a typo, an unknown place, and the
    accented name alike."""

    @staticmethod
    def _stage(world):
        world.nation_gold["France"] = 20000
        world.get_region("Lorraine").war_damage = 0.3

    @pytest.mark.parametrize("line", ["build supply depot in Atlantis",
                                      "repair the fort in Atlantis",
                                      "repair Atlantis"])
    def test_an_unknown_place_gets_the_matchers_answer_free(self, shipped, line):
        client, world = shipped
        self._stage(world)
        before = _snapshot(world)
        data = post(client, line)
        assert _snapshot(world) == before, data.get("message")
        assert "Region 'Atlantis' not found" in str(data.get("message"))

    def test_a_typo_is_read_and_said(self, shipped):
        client, world = shipped
        self._stage(world)
        message = str(post(client, "build supply depot in Brittanny").get("message"))
        assert "Brittany" in message and f"read Brittany {READING_NOTE}" in message

    @pytest.mark.parametrize("line", ["repair Lorrain", "repair the damage in Lorrain"])
    def test_repair_reads_its_object_and_says_so(self, shipped, line):
        client, world = shipped
        self._stage(world)
        before = _snapshot(world)
        data = post(client, line)
        assert data.get("success") is True, data.get("message")
        assert _snapshot(world)["gold"]["France"] == before["gold"]["France"] - 150
        assert f"read Lorraine {READING_NOTE}" in str(data.get("message"))

    @pytest.mark.parametrize("line", ["repair the damage", "repair war damage"])
    def test_the_thing_mended_is_never_a_province(self, shipped, line):
        client, world = shipped
        self._stage(world)
        data = post(client, line)
        assert "Specify a region" in str(data.get("message")), data.get("message")

    def test_the_accented_build_resolves(self, shipped):
        client, world = shipped
        self._stage(world)
        message = str(post(client, "build supply depot in Franche-Comté").get("message"))
        assert "Franche-Comte" in message and "Specify a region" not in message


class TestAccentsNeverHideAName:
    def test_folding_is_one_character_for_one(self):
        for text in ("franche-comté", "masséna, hold", "straße"):
            assert len(LC.fold_accents(text)) == len(text)
        assert LC.fold_accents("franche-comté") == "franche-comte"
        assert LC.fold_accents("straße") == "straße"  # no base letter: kept

    def test_an_accented_marshal_is_bound(self, shipped):
        client, world = shipped
        data = post(client, "Masséna, hold")
        assert str(data.get("message")).startswith("Massena will hold"), data.get("message")


class TestAHoldTheGamePlacedReadsNoName:
    """The rider: every bare `hold` said "(Our maps read Rhineland as the
    province nearest your order, Sire.)" — a reading of a name nobody typed,
    measured on the pre-slice tree. A note that fires on every hold teaches
    the player to skip the one that matters."""

    @pytest.mark.parametrize("line", ["Ney, hold", "Ney, hold here",
                                      "Ney, hold position", "Ney, hold our lines"])
    def test_a_placed_hold_discloses_nothing(self, shipped, line):
        client, _ = shipped
        message = str(post(client, line).get("message"))
        assert message.startswith("Ney will hold"), message
        assert READING_NOTE not in message, message

    @pytest.mark.parametrize("line,read", [("Ney, hold Rhinelnd", "Rhineland"),
                                           ("Soult, hold Mainz", "Maine")])
    def test_a_read_name_still_discloses(self, shipped, line, read):
        client, _ = shipped
        message = str(post(client, line).get("message"))
        assert f"read {read} {READING_NOTE}" in message, message

    def test_the_lever_down_restores_the_note(self, shipped, monkeypatch):
        client, _ = shipped
        monkeypatch.setattr(SE, "THE_DEFAULT_HOLD_READS_NO_NAME", False)
        message = str(post(client, "Ney, hold").get("message"))
        assert READING_NOTE in message, message
