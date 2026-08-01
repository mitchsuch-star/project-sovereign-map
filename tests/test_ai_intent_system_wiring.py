"""AI-5 — intent into the existing systems (docs/AI_INTENT_SPEC.md §4.5,
§11.1 Stage E; landing record §18).

Each §4.5 row is a small WIRE, not a new system, and each has its arm
here:

- NA-5 becomes the ladder's COERCE rung (issuance gated on the climbed
  ladder; yielding satisfies and the rung falls — descent);
- recruitment: a court preparing a design at coerce+ commissions
  marshals BEFORE the declaration (P1.75 gains its reason);
- jealousy: the EC-M proxy serves a real faction — glory hunting biases
  toward the nation's design frontier;
- vassals: `bandwagon` is the vassalage on-ramp (an allied bandwagoning
  minor offers its crown — the Confederation of the Rhine, chosen);
- formations: an AI nation that pursues an acquisitive design can FINISH
  one through the Stage D settlement path, no player brokering;
- economy: the sponsor executor is AI-2b's directed record and the
  paymaster stays `get_paymaster_nation`'s special case (v1.3) — the
  wire landed in earlier stages; the index test here pins the seams so
  the §4.5 row is verifiable rather than asserted.
"""

from pathlib import Path

import pytest

from backend.game_logic.agendas import get_active_agenda
from backend.game_logic.intent import get_nation_intent, rung_index
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture()
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _pacify_player_wars(world):
    for other in list(world.get_active_nations()):
        if other == world.player_nation:
            continue
        key = world._make_diplo_key(world.player_nation, other)
        if world.diplomatic_states.get(key) == "WAR":
            world.diplomatic_states[key] = "PEACE"
    world.invalidate_bloc_members_cache()


def _pacify_all_wars_of(world, nation):
    for other in list(world.get_active_nations()):
        if other == nation:
            continue
        key = world._make_diplo_key(nation, other)
        if world.diplomatic_states.get(key) == "WAR":
            world.diplomatic_states[key] = "PEACE"
    world.invalidate_bloc_members_cache()


def _make_coercive(world, nation):
    """The coerce climb from the REAL derivation (the ultimatum-fixture
    arithmetic): relation cold (-45, +8), France busy in one war (+6),
    France weary (+5) — base 55 + 19 = 74 >= the coerce floor of 72."""
    world.nation_relations[
        world._make_diplo_key(world.player_nation, nation)] = -45
    war_key = world._make_diplo_key(world.player_nation, "Britain")
    world.diplomatic_states[war_key] = "WAR"
    world.war_start_turns[war_key] = int(world.current_turn)
    world.war_exhaustion[world.player_nation] = 120
    world.invalidate_bloc_members_cache()


# ═══════════════════ WIRE: NA-5 AS THE COERCE RUNG ═════════════════════════


class TestNA5CoerceRung:
    def test_ultimatum_blocked_below_coerce(self, world):
        """The pre-Stage-E trigger state (relation -20, quiet France) no
        longer bluffs an ultimatum — the court has not climbed."""
        from backend.game_logic.ai_diplomacy import (
            _generate_agenda_ultimatum,
        )
        _pacify_player_wars(world)
        world.threat_level = 0
        world.regions["Hanover"].controller = "France"
        world.invalidate_active_nations_cache()
        world.nation_relations[
            world._make_diplo_key("France", "Prussia")] = -20
        for m in world.marshals.values():
            if m.nation == "France":
                m.strength = 2000
            elif m.nation == "Prussia":
                m.strength = 40000
        view = get_nation_intent("Prussia", world)
        assert rung_index(view.price) < rung_index("coerce")
        assert _generate_agenda_ultimatum("Prussia", world) is None

    def test_gate_requires_the_player_as_obstacle(self, world):
        """A court at coerce against a THIRD power never menaces Paris
        with its design — the rung is against its own obstacle."""
        from backend.game_logic.ai_diplomacy import (
            _generate_agenda_ultimatum,
        )
        _pacify_player_wars(world)
        world.threat_level = 0
        # Prussia's one design target sits with Hanover itself: the
        # obstacle derives to Hanover, not France.
        assert world.regions["Hanover"].controller == "Hanover"
        _make_coercive(world, "Prussia")
        view = get_nation_intent("Prussia", world)
        assert view.against != "France"
        assert _generate_agenda_ultimatum("Prussia", world) is None

    def test_yield_descends_the_ladder(self, world):
        """§3.1a descent at the NA-5 seam: the ceded target satisfies the
        design, the deck advances to Armed Neutrality (a guard posture),
        and the rung falls from coerce — derived, no latch anywhere."""
        _pacify_player_wars(world)
        world.threat_level = 0
        world.regions["Hanover"].controller = "France"
        world.invalidate_active_nations_cache()
        _make_coercive(world, "Prussia")
        before = get_nation_intent("Prussia", world)
        assert rung_index(before.price) >= rung_index("coerce")
        # The yield: Hanover passes to Prussia (the _apply_ultimatum_
        # demands controller flip, distilled).
        world.regions["Hanover"].controller = "Prussia"
        world.invalidate_active_nations_cache()
        view = get_active_agenda("Prussia", world)
        assert view is not None and view.id == "armed_neutrality"
        after = get_nation_intent("Prussia", world)
        assert rung_index(after.price) < rung_index("coerce"), (
            "satisfaction must drop the rung within one derivation")


# ═══════════════════ WIRE: RECRUITMENT (P1.75) ═════════════════════════════


class TestRecruitmentWire:
    def test_commission_at_peace_when_preparing(self, world):
        """Prussia calls up Blücher BEFORE Jena: a court at coerce+
        commissions at peace through the same gate."""
        from backend.game_logic import recruitment as R
        _pacify_player_wars(world)
        _pacify_all_wars_of(world, "Austria")
        world.regions["Milan"].controller = "France"
        world.invalidate_active_nations_cache()
        _make_coercive(world, "Austria")
        assert not world.get_nations_at_war_with("Austria")
        view = get_nation_intent("Austria", world)
        assert rung_index(view.price) >= rung_index("coerce")
        world.marshals["ArchdukeJohn"].strength = 0  # under-officered
        world.nation_gold["Austria"] = 20000
        action = R.find_ai_commission(world, "Austria", 20000)
        assert action is not None
        assert action["action"] == "recruit_marshal"

    def test_no_commission_at_peace_below_coerce(self, world):
        """Peacetime thrift holds for a court that has not climbed."""
        from backend.game_logic import recruitment as R
        _pacify_player_wars(world)
        _pacify_all_wars_of(world, "Austria")
        world.nation_relations[
            world._make_diplo_key("France", "Austria")] = -20
        world.invalidate_bloc_members_cache()
        assert not world.get_nations_at_war_with("Austria")
        view = get_nation_intent("Austria", world)
        assert rung_index(view.price) < rung_index("coerce")
        world.marshals["ArchdukeJohn"].strength = 0
        world.nation_gold["Austria"] = 20000
        assert R.find_ai_commission(world, "Austria", 20000) is None


# ═══════════════════ WIRE: JEALOUSY (EC-M PROXY) ═══════════════════════════


class TestJealousyWire:
    def _stage(self, world, hunter_nation, frontier_region):
        """Place the hunter beside the frontier with two enemy targets:
        a WEAKER one off the design, a STRONGER one standing on it. The
        post must itself sit OFF the design (the first draft staged the
        weak enemy on Piedmont — also a redeem_italy target — and the
        finder rightly preferred it)."""
        from backend.game_logic.agendas import get_agenda_military_targets
        frontier = set(get_agenda_military_targets(hunter_nation, world))
        adjacent = list(world.regions[frontier_region].adjacent_regions)
        post = next(r for r in adjacent if r not in frontier)
        hunter = next(m for m in world.marshals.values()
                      if m.nation == hunter_nation and m.strength > 0)
        hunter.location = post
        hunter.strength = 30000
        enemies = [m for m in world.marshals.values()
                   if m.nation == "France"][:2]
        weak, strong = enemies[0], enemies[1]
        weak.location = post
        weak.strength = 2000
        strong.location = frontier_region
        strong.strength = 10000
        return hunter, weak, strong

    def test_glory_hunts_the_design_frontier(self, world):
        """Bernadotte hunts where the Emperor wants the map redrawn: an
        enemy ON an unmet design target outranks a merely weaker one."""
        from backend.game_logic.agendas import get_agenda_military_targets
        from backend.game_logic.jealousy import (
            find_autonomous_attack_target,
        )
        assert world.is_at_war("Austria", "France")
        assert "Milan" in get_agenda_military_targets("Austria", world)
        hunter, weak, strong = self._stage(world, "Austria", "Milan")
        found = find_autonomous_attack_target(world, hunter)
        assert found is not None
        target, region = found
        assert target.name == strong.name, (
            "the design frontier outranks the weaker prey")
        assert region == "Milan"

    def test_no_design_keeps_weakest_first(self, world):
        """France is deckless — the player's own glory hunters keep the
        pre-Stage-E weakest-first behaviour byte-identically."""
        from backend.game_logic.agendas import get_agenda_military_targets
        from backend.game_logic.jealousy import (
            find_autonomous_attack_target,
        )
        assert get_agenda_military_targets("France", world) == []
        ney = world.marshals["Ney"]
        austrians = [m for m in world.marshals.values()
                     if m.nation == "Austria"][:2]
        weak, strong = austrians[0], austrians[1]
        weak.location = ney.location
        weak.strength = 3000
        strong.location = ney.location
        strong.strength = 20000
        found = find_autonomous_attack_target(world, ney)
        assert found is not None and found[0].name == weak.name


# ═══════════════════ WIRE: VASSALS (THE ON-RAMP) ═══════════════════════════


def _bandwagon_view(nation):
    from backend.game_logic.intent import IntentView
    return IntentView(nation=nation, want_id="lean", want_title="The Lean",
                      want_type="acquire_regions", against=None,
                      weight=66, price="bandwagon")


@pytest.fixture()
def hegemon_france(monkeypatch):
    """The established bandwagon-test idiom (test_ai_intent_participation
    fixture): pin the hegemon share and the minor's rung — the on-ramp's
    own floors stay real and are what these tests falsify."""
    from backend.game_logic import coalition
    monkeypatch.setattr(coalition, "_identify_max_bloc_share",
                        lambda world: ("France", 0.55))
    from backend.game_logic import intent
    original = intent.get_nation_intent

    def _patched(nation, world):
        if nation == "Denmark":
            return _bandwagon_view(nation)
        return original(nation, world)

    monkeypatch.setattr(intent, "get_nation_intent", _patched)
    return monkeypatch


class TestVassalageOnRamp:
    def _ally_denmark(self, world, relation=60, lord="France"):
        key = world._make_diplo_key(lord, "Denmark")
        world.diplomatic_states[key] = "ALLIANCE"
        world.nation_relations[key] = relation
        world.threat_level = 0
        world.invalidate_bloc_members_cache()

    def test_allied_bandwagoner_offers_its_crown(self, world,
                                                 hegemon_france):
        from backend.game_logic.ai_diplomacy import (
            process_diplomatic_phase,
        )
        self._ally_denmark(world)
        proposal = process_diplomatic_phase("Denmark", world)
        assert proposal is not None
        assert proposal["proposal_type"] == "offer_vassalage"
        assert proposal["_force_send"] is True
        assert world.ai_proposal_cooldowns.get(
            "Denmark|offer_vassalage", 0) > 0

    def test_relation_floor_holds(self, world, hegemon_france):
        """A crown is not surrendered at relation 20."""
        from backend.game_logic.ai_diplomacy import (
            VASSAL_ONRAMP_RELATION,
            process_diplomatic_phase,
        )
        self._ally_denmark(world, relation=VASSAL_ONRAMP_RELATION - 20)
        proposal = process_diplomatic_phase("Denmark", world)
        assert proposal is None or (
            proposal.get("proposal_type") != "offer_vassalage")

    def test_power_cap_blocks_the_offer(self, world, hegemon_france,
                                        monkeypatch):
        """Honest availability: never offered when acceptance would be
        refused by the WPS-B power cap."""
        from backend.game_logic import diplomacy
        monkeypatch.setattr(
            diplomacy, "check_vassalage_power_cap",
            lambda *a, **k: {"allowed": False, "reason": "test cap"})
        from backend.game_logic.ai_diplomacy import (
            process_diplomatic_phase,
        )
        self._ally_denmark(world)
        proposal = process_diplomatic_phase("Denmark", world)
        assert proposal is None or (
            proposal.get("proposal_type") != "offer_vassalage")

    def test_accept_creates_the_voluntary_vassal(self, world):
        """Accepting the offered crown creates the client through the
        SAME treaty seam — loyalty 80 (60 + generosity 2x10): it CHOSE
        this. The Confederation of the Rhine, joined."""
        from backend.commands.executor import CommandExecutor
        self._ally_denmark(world)
        dialogue = {
            "type": "incoming_proposal",
            "target_nation": "Denmark",
            "context": {
                "proposal": {
                    "type": "offer_vassalage",
                    "proposer_nation": "Denmark",
                    "target_nation": "France",
                    "demands": [],
                    "sweeteners": [],
                },
                "source_nation": "Denmark",
                "proposal_type": "offer_vassalage",
            },
            "turn_created": int(world.current_turn),
            "blocking": False,
        }
        world.dialogue_manager.push(dialogue)
        executor = CommandExecutor()
        result = executor._diplomatic._handle_accept_ai_proposal(
            dialogue, world)
        assert result["success"] is True
        state = world.vassals.get("Denmark")
        assert state is not None and state["lord"] == "France"
        assert state["loyalty"] == 80
        popup = world.proposal_result_popup
        assert popup and popup["outcome"] == "ACCEPT"
        assert popup["proposal_type"] == "Offer of Submission"

    def test_ai_hegemon_receives_the_submission_directly(
            self, world, monkeypatch):
        """The AI-AI mirror: an allied bandwagoning minor submits to its
        AI hegemon in place (the auction's AI-win idiom)."""
        from backend.game_logic import coalition, intent
        monkeypatch.setattr(coalition, "_identify_max_bloc_share",
                            lambda w: ("Austria", 0.55))
        original = intent.get_nation_intent

        def _patched(nation, w):
            if nation == "Denmark":
                return _bandwagon_view(nation)
            return original(nation, w)

        monkeypatch.setattr(intent, "get_nation_intent", _patched)
        # Denmark stands at 64% of Austria's power on the boot roster —
        # the real WPS-B cap would refuse (and the arm honours it by
        # skipping WITHOUT burning the cooldown); the cap has its own
        # suite, so pin the ARM here with the cap held open.
        from backend.game_logic import diplomacy
        monkeypatch.setattr(diplomacy, "check_vassalage_power_cap",
                            lambda *a, **k: {"allowed": True,
                                             "reason": ""})
        from backend.game_logic.ai_diplomacy import (
            process_diplomatic_phase,
        )
        self._ally_denmark(world, lord="Austria")
        # Quiet the France-facing legacy rungs that would otherwise mail
        # Paris first: P4's upgrade ask (relation-band) and P7's
        # opportunism (PEACE-state) both key off the FRANCE relation.
        france_key = world._make_diplo_key("France", "Denmark")
        world.nation_relations[france_key] = 0
        world.diplomatic_states[france_key] = "NON_AGGRESSION"
        world.invalidate_bloc_members_cache()
        proposal = process_diplomatic_phase("Denmark", world)
        assert proposal is None  # ratified in place, nothing mailed
        state = world.vassals.get("Denmark")
        assert state is not None and state["lord"] == "Austria"
        assert world.ai_proposal_cooldowns.get(
            "Denmark|offer_vassalage", 0) > 0


# ═══════════════════ WIRE: FORMATIONS (ASSURANCE) ══════════════════════════


class TestFormationsWire:
    def test_ai_conquest_completes_a_formation(self, world):
        """§4.5's first row, proven end to end: an AI nation pursuing an
        acquisitive FORMING design finishes it through the Stage D
        third-party settlement — the last design province cedes, the
        formation poll inside the ratify seam proclaims the new nation.
        No player brokering anywhere.

        Sweden vs Denmark (the pin-17 fresh-pair idiom — both outside
        the France-containing boot instance, so the war stands alone and
        the third-party poll may touch it) with a runtime forms deck:
        the shipped forms decks belong to France's satellites, whose
        boot wars all live inside the Third-Coalition instance."""
        from backend.game_logic.diplomacy import declare_war
        from backend.game_logic.settlement_third_party import (
            THIRD_PARTY_MIN_WAR_TURNS,
            process_third_party_settlements,
        )
        capital = world.get_nation_capital("Denmark")
        prize = next(r for r in world.get_nation_regions("Denmark")
                     if r != capital)
        world.agendas.setdefault("Sweden", []).insert(0, {
            "id": "the_sound_united",
            "type": "acquire_regions",
            "title": "The Sound United",
            "regions": [prize],
            "forms": {
                "display_name": "Scandinavia",
                "flag": "Sweden",
                "blurb": "The Sound is one crown's water.",
            },
        })
        world.invalidate_bloc_members_cache()
        view = get_active_agenda("Sweden", world)
        assert view is not None and view.id == "the_sound_united"

        declare_war(world, "Sweden", "Denmark")
        war = None
        war_id = None
        for wid, instance in world.war_instances.items():
            participants = instance.get("active_participants") or []
            if (instance.get("ended_turn") is None
                    and "Sweden" in participants
                    and "Denmark" in participants
                    and "France" not in participants):
                war_id, war = wid, instance
                break
        assert war is not None
        war["created_turn"] = (int(world.current_turn)
                               - THIRD_PARTY_MIN_WAR_TURNS - 1)
        world.war_exhaustion["Denmark"] = 150
        key = world._make_diplo_key("Denmark", "Sweden")
        world.war_scores[key] = -95 if key.startswith("Denmark") else 95

        events = process_third_party_settlements(world)
        assert any(e["type"] == "third_party_peace" for e in events)
        assert world.regions[prize].controller == "Sweden"
        record = (world.nation_formations or {}).get("Sweden")
        assert record is not None and record.get("formed") is True, (
            "the ratify seam's own formation poll must proclaim the "
            "formed nation the turn its last province cedes")
        assert any(e.get("type") == "nation_formed"
                   for e in world.event_log)


# ═══════════════════ WIRE: ECONOMY (THE SEAM INDEX) ════════════════════════


class TestEconomyWireIndex:
    def test_sponsor_executor_is_the_directed_record(self, world):
        """§4.5's economy row, v1.3 wording: 'the sponsor branch's
        executor is the directed payment record in AI-2b' — minted here,
        paid by process_instruments, gold moving court to court."""
        from backend.game_logic.instruments import (
            grant_directed_sponsorship,
            process_instruments,
        )
        world.nation_gold["Britain"] = 5000
        world.nation_gold["Austria"] = 1000
        grant_directed_sponsorship(
            world, payer="Britain", recipient="Austria", aim="France",
            amount_per_turn=200, turns=5)
        before_payer = world.nation_gold["Britain"]
        before_recipient = world.nation_gold["Austria"]
        process_instruments(world)
        assert world.nation_gold["Britain"] == before_payer - 200
        assert world.nation_gold["Austria"] == before_recipient + 200

    def test_paymaster_stays_the_special_case(self, world):
        """§4.5 v1.3: the coalition subsidy stays as-is —
        `get_paymaster_nation` resolves the authored paymaster posture,
        not a generalised intent branch."""
        from backend.game_logic.agendas import get_paymaster_nation
        coalition = getattr(world, "active_coalition", None)
        if not coalition:
            pytest.skip("no boot coalition on this scenario build")
        world.nation_gold["Britain"] = 9000
        assert get_paymaster_nation(world) == "Britain"

    def test_exhaustion_feeds_intent(self, world):
        """The WE->intent read (AI-3r N5) — the economy talks back to
        the ladder: a weary obstacle raises the coveter's weight."""
        from backend.game_logic.intent import WEIGHT_HOLDER_EXHAUSTED
        world.regions["Hanover"].controller = "France"
        world.invalidate_active_nations_cache()
        world.war_exhaustion["France"] = 0
        world.invalidate_bloc_members_cache()
        quiet = get_nation_intent("Prussia", world).weight
        world.war_exhaustion["France"] = 150
        world.invalidate_bloc_members_cache()
        weary = get_nation_intent("Prussia", world).weight
        assert weary - quiet == WEIGHT_HOLDER_EXHAUSTED
