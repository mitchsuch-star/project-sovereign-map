"""PC15-10 B4a — "The order, justified" (`docs/PETITION_POPUP_REVISIT_SPEC.md`
§4 F8, §6 Q5 RULED; Score Mandate Chunk 4, September 27, 2026).

F8: the PopupQueue order was defensible and its list dirty. Now:
  * nine slots, each justified in a comment table at `PRIORITY_ORDER`;
  * `coalition_popup` RETIRED whole — no producer ever wrote it (the
    coalition's formation reaches the player on the notice rail). The order
    entry, the response key, the world property and the save key are gone,
    and a legacy save's key is dropped at load (removing the order entry
    alone would have left a restored value nothing could ever pop);
  * the unreachable `alliance_paradox_popup` ORDER entry removed (it
    canonicalizes to the commitment paradox's slot, which the `seen` set had
    consumed) — the alias is kept for legacy saves;
  * the `proposal_result` decision procedure run: neither of the spec's two
    branches applies — its scene was retired on Sept 12 (FA-S17-D9) and the
    backend already lifts the receipt onto the notice rail, so it stays a
    documented informational receipt (row 8);
  * the end-turn contract's carry — the one documented exception to "one
    popup per response" — declared as data, `PopupQueue.ENEMY_PHASE_CARRIED`,
    and pinned against what `_apply_command_popup_contract` really pops.
"""

import contextlib
import inspect
import io
import re

import pytest

import backend.main as M
from backend.game_logic import jealousy as J
from backend.models.cooldown_manager import PopupQueue
from backend.models.world_state import WorldState
from tests import _chip_census as C


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    return M.world


JUSTIFIED = [
    "diplomatic_sabotage_popup",
    "vassal_rebellion_imminent_popup",
    "proclamation_popup",
    "diplomatic_objection_popup",
    "pending_marshal_petition",
    "incoming_proposal_popup",
    "incoming_settlement_offer_popup",
    "proposal_result_popup",
    "commitment_paradox_popup",
]


class TestTheOrderIsJustified:

    def test_nine_slots_in_the_justified_order(self):
        assert PopupQueue.PRIORITY_ORDER == JUSTIFIED

    def test_every_slot_has_its_row_in_the_table(self):
        """Source census: the comment table above `PRIORITY_ORDER` names
        every slot, numbered in the order's own order."""
        src = inspect.getsource(PopupQueue)
        table = src[:src.index("PRIORITY_ORDER = [")]
        rows = re.findall(r"#\s+(\d)\s+(\w+)", table)
        assert [(int(n), s) for n, s in rows] == list(
            enumerate(JUSTIFIED, start=1))

    def test_every_slot_maps_to_a_response_key(self):
        for slot in PopupQueue.PRIORITY_ORDER:
            assert slot in PopupQueue.RESPONSE_KEYS


class TestTheDeadSlotIsRetired:

    def test_the_slot_is_gone_everywhere(self):
        assert "coalition_popup" not in PopupQueue.PRIORITY_ORDER
        assert "coalition_popup" not in PopupQueue.RESPONSE_KEYS
        assert "coalition_popup" not in PopupQueue.RESPONSE_KEYS.values()
        assert not hasattr(WorldState, "coalition_popup")

    def test_a_save_no_longer_carries_it(self, world):
        assert "coalition_popup" not in world.to_dict()

    def test_a_legacy_saves_key_is_dropped_at_load(self, world):
        data = world.to_dict()
        data["coalition_popup"] = {"coalition_name": "The Third Coalition"}
        with _quiet():
            loaded = WorldState.from_dict(data)
        assert not loaded._popup_queue.has_pending() or \
            loaded._popup_queue.get("coalition_popup") is None
        assert "coalition_popup" not in loaded.to_dict()

    def test_the_formation_still_reaches_the_rail(self):
        """The coalition's formation was never a modal: `form_coalition`'s
        payload rides its result, which the notice rail renders."""
        from backend.game_logic import coalition
        src = inspect.getsource(coalition.form_coalition)
        assert '"coalition_popup"' in src


class TestTheAliasIsKept:

    def test_a_legacy_push_lands_in_the_paradox_slot(self):
        q = PopupQueue()
        q.push("alliance_paradox_popup", {"attacker": "France"})
        attr, key, value = q.pop_highest()
        assert attr == "commitment_paradox_popup"
        assert key == "commitment_paradox_popup"
        assert value == {"attacker": "France"}

    def test_the_alias_has_no_order_entry(self):
        assert "alliance_paradox_popup" not in PopupQueue.PRIORITY_ORDER
        assert PopupQueue.LEGACY_ALIASES["alliance_paradox_popup"] == \
            "commitment_paradox_popup"


class TestTheEndTurnCarryIsDeclared:

    def test_the_declared_carry(self):
        assert PopupQueue.ENEMY_PHASE_CARRIED == (
            "proposal_result_popup", "proclamation_popup",
            "pending_marshal_petition")

    def test_the_contract_pops_exactly_the_declared_slots(self, world):
        """Behaviour: beside `enemy_phase` the three declared slots are
        carried and every other queued popup is deferred."""
        world.proposal_result_popup = {"result": "ACCEPT"}
        world.nation_proclamation_popup = {"nation": "Poland"}
        ney, dav = world.marshals["Ney"], world.marshals["Davout"]
        ney.jealous_of = "Davout"
        ney.jealousy_turns_remaining = 5
        J._set_escalation_level(ney, "Davout", J.ESCALATION_PERMANENT_LEVEL)
        J._set_escalation_level(dav, "Ney", J.ESCALATION_PERMANENT_LEVEL)
        J.queue_confrontation_petition(world, ney, dav,
                                       J.ESCALATION_PERMANENT_LEVEL)
        world.diplomatic_sabotage_popup = {"target_nation": "Prussia"}
        response = {"enemy_phase": {"actions": []}}
        with _quiet():
            M._apply_command_popup_contract(response, {}, world)
        assert response.get("proposal_result") == {"result": "ACCEPT"}
        assert response.get("nation_proclamation") == {"nation": "Poland"}
        assert (response.get("deferred_marshal_petition") or {}).get(
            "kind") == "jealousy_confrontation"
        assert response.get("diplomatic_sabotage") is None, "deferred"
        assert world.diplomatic_sabotage_popup == {"target_nation": "Prussia"}

    def test_the_contract_names_every_declared_slot(self):
        """Census: the function's source reads each declared slot — a new
        carry must be declared, and a declared one must be real."""
        src = inspect.getsource(M._apply_command_popup_contract)
        attr_of = {"proposal_result_popup": "world.proposal_result_popup",
                   "proclamation_popup": "world.nation_proclamation_popup",
                   "pending_marshal_petition": '"pending_marshal_petition"'}
        for slot in PopupQueue.ENEMY_PHASE_CARRIED:
            assert attr_of[slot] in src, slot
