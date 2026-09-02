"""Row PT, slice B — the two silent losses.

Build spec: `docs/PLAYTEST_FIXES_SPEC.md` §2 PT-B.

* **PT-B1** the redemption branch is destroyed at the moment it is offered
  — `_route_response_ui` returns on the first match and `redemption_event`
  is the last of twelve routes. There was no recovery.
* **PT-B2** the war HUD outlives the peace — `opponent_display` is built
  from war MEMBERSHIP while the score beside it is built from live
  belligerency.

PT-B1 is client-side, so it is pinned at the source: the stash must exist,
join the other three, be raised from every control-return tail, and be
cleared at one chokepoint. That is the same discipline
`TestOverlayPayloadBoolSafety` uses for the tutorial overlay, and it is
what the parse harness and boot smoke cannot check.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from backend.game_logic.war_status import (
    _collapse_shared_war_instance_rows,
    build_active_wars,
)

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
MAIN_GD = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
API_GD = (SCRIPTS / "api_client.gd").read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════
# PT-B2 — the war HUD outlives the peace
# ═══════════════════════════════════════════════════════════════════════

def _collapsed(live_opponents, membership, leader="Britain"):
    """A real coalition war on a real world, read through the real producer.

    `membership` is the war roster as `side_by_nation` remembers it;
    `live_opponents` are the courts France is still actually at WAR with.
    The gap between the two is the whole defect — a court that signs with
    France but stays at war with somebody else is never popped from
    membership.
    """
    from tests.conftest import WorldFactory

    world = WorldFactory.basic()
    world.current_turn = 14
    for nation in set(membership) | set(live_opponents):
        key = world._make_diplo_key("France", nation)
        world.diplomatic_states[key] = (
            "WAR" if nation in live_opponents else "PEACE")
        if nation in live_opponents:
            world.war_start_turns[key] = 10
    world.war_instances = {
        "war_1": {
            "attackers": ["France"],
            "defenders": list(membership) or list(live_opponents),
            "side_by_nation": {"France": "attackers",
                               **{n: "defenders" for n in membership}},
            # `_rebuild_war_instance_indexes` reads THIS key, not
            # `attackers`/`defenders` — without it the participant index is
            # empty, every row gets a blank `war_instance_id`, and nothing
            # collapses.
            "active_participants": ["France"] + (list(membership)
                                                 or list(live_opponents)),
            "attacker_leader": "France",
            "defender_leader": leader,
            "ended_turn": None,
            "active_diplo_keys": [world._make_diplo_key("France", n)
                                  for n in live_opponents],
            "started_turn": 10,
        }
    }
    # The by-participant index is lazily rebuilt off a dirty flag; a
    # hand-set `war_instances` must mark it, or `_find_active_war_instance_id`
    # sees an empty index, every row gets a blank `war_instance_id`, and
    # NOTHING COLLAPSES — the fixture would then pin nothing at all.
    world._war_instance_indexes_dirty = True
    payload = build_active_wars(world)
    rows = [w for w in payload["wars"]
            if w.get("is_multi_participant_war")]
    assert rows, "the fixture must actually collapse, or nothing is pinned"
    return rows[0]


class TestTheNameListMatchesTheScore:
    def test_a_court_that_signed_a_peace_leaves_the_card(self):
        """THE MEASURED DEFECT. Turn 14: the notification said "France and
        Hesse have signed a Peace Treaty", `France|Hesse` was gone from
        `active_diplo_keys`, and the SAME payload's `opponent_display` read
        "Britain + Austria + Hesse + Russia". Twelve consecutive responses.

        Hesse stayed in `side_by_nation` because `pop` fires only when a
        nation has no active pair ANYWHERE — and Hesse kept `Hesse|Holland`.
        """
        combined = _collapsed(
            live_opponents=["Britain", "Austria"],
            membership=["Britain", "Austria", "Hesse"])
        assert "Hesse" not in combined["opponent_display"]
        assert "Hesse" not in combined["opponents"]
        assert combined["opponent_display"] == "Britain + Austria"

    def test_the_click_target_is_never_a_court_at_peace(self):
        """`combined["opponent"]` is `ordered_opponents[0]` and
        `_leader_first` puts the leader first UNCONDITIONALLY — so a
        coalition led by the court that just signed made the row's own
        click target and flag key a nation with no war row and no share of
        the score printed beside it."""
        combined = _collapsed(
            live_opponents=["Austria", "Prussia"],
            membership=["Britain", "Austria", "Prussia"])   # Britain = leader
        assert combined["opponent"] in ("Austria", "Prussia")
        assert "Britain" not in combined["opponent_display"]

    def test_the_names_and_the_number_read_one_belligerent_set(self):
        """The `[A-F5]` comment solved this for the score and not for the
        name. Pin them to the same source."""
        combined = _collapsed(
            live_opponents=["Britain", "Austria"],
            membership=["Britain", "Austria", "Hesse"])
        assert set(combined["opponents"]) == {"Britain", "Austria"}

    def test_a_war_nobody_left_still_renders(self):
        """The fallback branch: membership yields nothing usable, so the
        rows themselves are the answer. It must not blank the card.

        Two rows, because a single-row war is never collapsed at all."""
        combined = _collapsed(
            live_opponents=["Britain", "Austria"],
            membership=[])
        assert combined["opponent_display"] == "Britain + Austria"


class TestTheArmisticeCardNamesTheLivingNation:
    def test_an_armistice_row_carries_a_display_name(self):
        """Drive-by on the same screen: the war row rendered the backend's
        `formed_display_name` while the armistice card ran the raw key
        through the client's own map, so a nation formed under NA-6 showed
        its NEW name two rows above its DEAD one."""
        from tests.conftest import WorldFactory

        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ARMISTICE"
        payload = build_active_wars(world)
        rows = [w for w in payload["wars"] if w.get("status") == "armistice"]
        assert rows, "fixture must produce an armistice row"
        for row in rows:
            assert row.get("opponent_display"), (
                "the armistice card must be handed a display name, not left "
                "to re-derive one the war row derives differently")

    def test_the_client_prefers_the_backends_name(self):
        assert re.search(r'war_data\.get\("opponent_display"',
                         (SCRIPTS / "war_status_panel.gd").read_text(
                             encoding="utf-8")), (
            "the armistice card must read the backend's display name")


# ═══════════════════════════════════════════════════════════════════════
# PT-B1 — the redemption is stashed, raised, and recoverable
# ═══════════════════════════════════════════════════════════════════════

class TestTheRedemptionIsStashed:
    def test_the_stash_exists_and_joins_the_other_three(self):
        assert "func _stash_redemption" in MAIN_GD
        # the four stashes are contiguous at the head of _on_command_result
        block = re.search(
            r"_stash_proclamation\(response\)\s*\n\s*_stash_envoy_digest\("
            r"response\)\s*\n\s*_stash_diorama\(response\).*\n\s*"
            r"_stash_redemption\(response\)", MAIN_GD)
        assert block, (
            "the redemption must be stashed BEFORE routing, beside the "
            "three surfaces with the identical popped-server-side property")

    def test_the_enemy_phase_path_is_excluded(self):
        """`_response_has_redemption_route` carries the same guard, and the
        enemy-phase dialog has its own handler — stashing there would
        double-show."""
        body = MAIN_GD.split("func _stash_redemption")[1].split("\nfunc ")[0]
        assert 'response.has("enemy_phase")' in body

    def test_every_patched_tail_raises_it(self):
        """A stash nothing raises is the same bug one step later."""
        assert MAIN_GD.count("_show_pending_redemption()") >= 6

    def test_it_is_raised_behind_the_letter_book_never_above_the_response(self):
        """Order matters: the three existing stashes are theatre and the
        redemption is a DECISION, so it goes last — and never before the
        response has rendered."""
        for tail in re.finditer(
                r"if _show_pending_envoy_digest\(\):\n\t\treturn[^\n]*\n"
                r"(.*?)\n\tcommand_input\.grab_focus\(\)", MAIN_GD, re.S):
            assert "_show_pending_redemption()" in tail.group(1), (
                "a control-return tail that raises the letter-book but not "
                "the redemption is a route that can still drop it")

    def test_one_chokepoint_clears_the_stash(self):
        """The inline handlers show the dialog directly and never touch the
        stash, so the clear lives in the shower — a double-show becomes
        structurally impossible rather than carefully avoided."""
        body = MAIN_GD.split("func _show_redemption_dialog")[1].split(
            "\nfunc ")[0]
        assert "pending_redemption_data = null" in body


class TestTheRecoveryEndpointIsWired:
    def test_the_client_can_finally_call_it(self):
        """`GET /pending_redemption` has existed since the feature landed
        and `api_client.gd` never called it.

        Pin the whole chain, not the presence of a word. The first draft
        asserted `"func get_pending_redemption" in API_GD` and
        `"/pending_redemption" in API_GD`, and the mutation sweep walked
        straight through it: renaming the function to
        `get_pending_redemption_disabled` keeps the first substring, and
        the second matched the COMMENT above the function.
        """
        body = re.search(
            r"func get_pending_redemption\(callback: Callable\):\n((?:\t.*\n)+)",
            API_GD)
        assert body, "the client needs a real getter, exactly so named"
        assert '_send_get("/pending_redemption"' in body.group(1), (
            "and it must actually GET the endpoint")
        assert "api_client.get_pending_redemption(" in MAIN_GD, (
            "...and something must call it — an unwired getter is the same "
            "dead endpoint one file over")

    def test_the_poll_is_once_per_turn(self):
        body = MAIN_GD.split("func _maybe_recover_dropped_redemption")[1] \
            .split("\nfunc ")[0]
        assert "_redemption_recheck_turn == current_turn" in body
        assert "_redemption_recheck_turn = current_turn" in body

    def test_the_endpoint_answers_the_shape_the_client_reads(self):
        """Pin the join, not each side of it."""
        import backend.main as M
        from tests.conftest import WorldFactory

        world = WorldFactory.basic()
        # WO-41 (Sept 1, 2026): the endpoint answers through the ONE liveness
        # predicate `disobedience.standing_redemption`, so the question must
        # name a marshal who STANDS and CARRIES the latch the checker sets
        # beside it — a stored question with no latch is stale by contract
        # (the man recovered, fell or was taken) and is cleared on read.
        # The pin is still the shape join; it just names a real man now.
        subject = world.get_player_marshals()[0]
        subject.redemption_pending = True
        world.pending_redemption = {
            "marshal": subject.name, "trust": 2,
            "message": "requests an urgent audience",
            "options": [{"id": "grant_autonomy"}],
        }
        original = M.world
        M.world = world
        try:
            out = M.get_pending_redemption()
        finally:
            M.world = original
        assert out["has_pending"] is True
        for key in ("marshal", "trust", "message", "options"):
            assert key in out
            assert f'response.get("{key}"' in MAIN_GD


@pytest.mark.parametrize("name", ["_stash_redemption",
                                  "_show_pending_redemption",
                                  "_maybe_recover_dropped_redemption",
                                  "_on_pending_redemption_checked"])
def test_no_orphan_helpers(name):
    """Every helper is declared once and called at least once — the shape
    that made `jealousy_attack_results` a dead local for a month."""
    assert MAIN_GD.count(f"func {name}") == 1
    assert MAIN_GD.count(name) >= 2
