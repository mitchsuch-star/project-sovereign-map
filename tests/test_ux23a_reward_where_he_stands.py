"""UX23-A — "reward a general from the notification itself" (Aug 23, 2026).

The user, after the Aug-23 rail fix: *"reward the general from the
notification itself — ideally one click, without opening a screen."* The deep
link that landed that morning still only ever OPENED something.

What this slice does, and the two rows it had to fix underneath it:

  UX23-A  The reward rail carries an EXECUTING button. The detail panel gains
          a full-width primary action above its button row; the client sends
          the command down the same typed pipeline a chip or the terminal
          would. The RENTE only — its face is auto-sized to the gap, so it is
          a genuine one-click action. The ESTATE keeps `[Reward…]` and the
          portfolio dialog, because which province to give away is the choice
          §0.6.8 exists to pose (`estate_yield`'s own docstring says so).

  UX23-R2 Every refresh minted a new uuid and `notification_bar.gd` dedupes
          the desk bell on that id, so a standing grievance rang the bell once
          a turn, per marshal, forever. `NotificationCollector.refresh` keeps
          the id. This is the row the user named as CONSTRAINING the design:
          without it, updating the rail in place after a partial payment rings
          the grievance bell at the moment of payment.

  UX23-R3 `_enforce_cap` evicted NORMAL rows only, so a HIGH `DOTATION_EROSION`
          row was immortal and N neglected marshals crowded real news off the
          rail with no way to lose any of them.

Two rules that are load-bearing and easy to break later:

  * SHOWN = APPLIED. The figure on the button is
    `get_rente_cost(compute_rente_face(...))` — the exact pair
    `_execute_grant_pension` prices the grant with.
  * NO BAKED `enabled`. `_process_dotation_state` runs at world_state.py:9470
    and admin AP is refilled at :9522, AFTER it. A gate evaluated at post time
    ships permanently disabled — the IGR-2 P1 exactly.

The ES-7 reactive gate is untouched and cannot be touched from here: these
rows only exist when a shortfall does.
"""

import json
import os
import re

import pytest

from backend.game_logic import dotation
from backend.models.world_state import WorldState
from backend.notifications import (
    DOTATION_EROSION, DOTATION_EXPECTATION, HIGH_EVICTION_WINDOW_TURNS,
    NOTIFICATION_CAP, NotificationCollector, NotificationPriority,
    create_notification,
)


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO_ROOT, "godot-client", "project-sovereign", "scripts")
SCENARIO = os.path.join(REPO_ROOT, "godot-client", "project-sovereign",
                        "assets", "maps", "europe_1805.json")


def _read(name):
    with open(os.path.join(SCRIPTS, name), encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture
def world():
    return WorldState.from_scenario(SCENARIO)


def _reconcile(world):
    world._dotation_processed_turn = None
    world._process_dotation_state()


def _owe(world, name="Ney", wins=2):
    marshal = world.marshals[name]
    marshal.battles_won = wins
    _reconcile(world)
    return marshal


def _rows(world, name="Ney"):
    return [n for n in world.notifications.get_pending()
            if n.get("details", {}).get("marshal") == name]


def _row(world, name="Ney"):
    rows = _rows(world, name)
    assert rows, f"precondition: a reward row is up for {name}"
    return rows[0]


# ══════════════════════════════════════════════════════════════════════════
# 1. The row can settle what it announces
# ══════════════════════════════════════════════════════════════════════════


class TestTheRowCanSettleWhatItAnnounces:

    def test_the_row_carries_a_command_the_parser_resolves_to_a_rente(self, world):
        """Not a made-up string: the button sends what a player could type."""
        from backend.ai.llm_client import LLMClient

        _owe(world)
        command = _row(world)["details"]["action_command"]
        assert command == "grant Ney a rente"
        parsed = LLMClient(use_real_api=False).parse_command(
            command, {"world": world})
        assert parsed["action"] == "grant_pension"
        assert parsed["marshal"] == "Ney"

    def test_that_command_is_a_live_golden_corpus_utterance(self):
        """A button that sends an unpinned phrase drifts the day the mock
        parser's keyword order changes. `grant Ney a rente` is corpus row
        es7sp-grant-ney-a-rente."""
        path = os.path.join(REPO_ROOT, "tests", "data",
                            "parser_golden_corpus.json")
        with open(path, encoding="utf-8") as fh:
            corpus = json.load(fh)
        shapes = {e["utterance"].replace("Ney", "<m>").replace("Davout", "<m>")
                  for e in corpus["entries"]
                  if e.get("expected", {}).get("action") == "grant_pension"}
        assert "grant <m> a rente" in shapes, (
            "the rail button's command shape must be a pinned corpus row")

    def test_pressing_it_pays_him_and_the_asking_stops(self, world):
        from backend.commands.executor import CommandExecutor

        ney = _owe(world)
        command = _row(world)["details"]["action_command"]
        before_ap = world.admin_actions_remaining

        result = CommandExecutor().execute(
            {"command": {"action": "grant_pension", "marshal": "Ney",
                         "raw_command": command}}, {"world": world})

        assert result["success"] is True
        assert ney.pension > 0
        assert world.admin_actions_remaining == before_ap - 1
        assert _rows(world) == [], (
            "one click, and the row that asked is gone in the same response")

    def test_the_quoted_figure_is_the_figure_the_treasury_pays(self, world):
        """Shown = applied, checked against the executor's OWN result rather
        than a re-derivation: grant it, then read the standing bill."""
        from backend.commands.executor import CommandExecutor

        ney = _owe(world, wins=3)
        label = _row(world)["details"]["action_label"]
        quoted = int(re.search(r"(\d+)g/turn", label).group(1))

        CommandExecutor().execute(
            {"command": {"action": "grant_pension", "marshal": "Ney"}},
            {"world": world})

        assert dotation.get_rente_cost(ney.pension) == quoted, (
            "the button quoted a price the treasury does not pay")

    def test_the_label_names_a_resize_when_he_already_holds_one(self, world):
        ney = _owe(world, wins=2)
        assert "Grant rente" in _row(world)["details"]["action_label"]
        ney.pension = 40
        ney.battles_won = 4
        world.current_turn += 1
        _reconcile(world)
        assert "Re-size rente" in _row(world)["details"]["action_label"]

    def test_the_detail_line_states_both_sides_and_the_way_back(self, world):
        ney = _owe(world)
        detail = _row(world)["details"]["action_detail"]
        face = dotation.compute_rente_face(ney, world)
        cost = dotation.get_rente_cost(face)
        assert f"{face}g/turn to his household" in detail
        assert f"{cost}g/turn from the treasury" in detail
        assert "1 administrative action" in detail
        assert "revoke Ney's rente" in detail, (
            "an unconfirmed one-click action must name its undo")

    def test_the_erosion_row_carries_it_too(self, world):
        """The HIGH row is the one a neglectful player actually sees."""
        ney = _owe(world, wins=2)
        for _ in range(dotation.GRACE_TURNS + 1):
            world.current_turn += 1
            _reconcile(world)
        row = next(n for n in _rows(world) if n["type"] == DOTATION_EROSION)
        assert row["details"]["action_command"] == "grant Ney a rente"
        expected = dotation.get_rente_cost(
            dotation.compute_rente_face(ney, world))
        assert f"{expected}g/turn" in row["details"]["action_label"]


class TestItNeverOffersWhatTheExecutorRefuses:

    def test_a_prisoner_gets_no_button(self, world):
        ney = _owe(world)
        assert dotation.rente_action_keys(ney, world), "precondition"
        ney.captured_by = "Austria"
        assert dotation.rente_action_keys(ney, world) == {}, (
            "the executor refuses a captured marshal; the button must not "
            "offer him")

    def test_it_gates_on_the_shared_predicate_not_on_the_face(self, world):
        """`compute_rente_face` is expectation MINUS ESTATE INCOME and ignores
        the rente already held, so a fully-paid marshal still reports a
        positive face. That is the exact split that made the card offer a
        re-size the executor refused."""
        ney = _owe(world)
        ney.pension = dotation.get_expectation(ney)
        assert dotation.compute_rente_face(ney, world) > 0, (
            "precondition: the face alone would still say yes")
        assert not dotation.rente_would_change(ney, world), "precondition"
        assert dotation.rente_action_keys(ney, world) == {}

    def test_the_predicate_is_read_not_reimplemented(self):
        """GR1. Four implementations of "is he met" is what the Aug-23 review
        round collapsed; a fifth inside the button builder re-opens it."""
        import inspect
        src = inspect.getsource(dotation.rente_action_keys)
        assert "rente_would_change(marshal, world)" in src
        assert "get_satisfaction" not in src, (
            "re-deriving the predicate here is the fifth implementation")

    def test_no_enabled_flag_is_baked_at_post_time(self, world):
        """IGR-2: `_process_dotation_state` writes the notice BEFORE
        `advance_turn` refills admin AP, so any affordance gate evaluated here
        ships permanently disabled. Proven by construction — the keys are
        identical at 0 AP and at full AP, and carry no enabled/disabled key."""
        ney = _owe(world)
        world.admin_actions_remaining = 0
        starved = dotation.rente_action_keys(ney, world)
        world.admin_actions_remaining = world.max_admin_actions
        flush = dotation.rente_action_keys(ney, world)
        assert starved == flush and starved != {}
        assert not any("enabl" in key or "disabl" in key for key in starved), \
            starved

    def test_the_refusal_at_zero_ap_is_honest_and_free(self, world):
        from backend.commands.executor import CommandExecutor

        ney = _owe(world)
        world.admin_actions_remaining = 0
        result = CommandExecutor().execute(
            {"command": {"action": "grant_pension", "marshal": "Ney"}},
            {"world": world})
        assert result["success"] is False
        assert "administrative" in result["message"].lower()
        assert ney.pension == 0, "a refused click must cost nothing"


class TestTheEstateStaysAChoice:
    """§0.6.8's whole premise is that estate-vs-rente is a genuine decision,
    and `estate_yield`'s docstring records that endowing a 0g fresh conquest
    is "a legal, sometimes-correct player play". A one-click auto-pick would
    quietly make that choice for the player."""

    def test_no_endow_command_is_ever_auto_offered(self, world):
        _owe(world, wins=5)
        region = next(r for r in world.regions.values()
                      if r.controller not in ("France", None)
                      and not r.is_capital)
        region.controller = "France"
        region.stability = 90
        region.war_damage = 0.0
        # `get_nation_regions` is per-turn cached (GR8) and a hand-flipped
        # controller does not invalidate it — without this the precondition
        # silently reads an empty estate list and the test proves nothing.
        world.invalidate_active_nations_cache()
        assert dotation.list_paying_estates(world, "France"), "precondition"
        world.current_turn += 1
        _reconcile(world)
        command = str(_row(world)["details"].get("action_command", ""))
        assert "endow" not in command.lower()

    def test_the_deep_link_to_the_portfolio_survives(self, world):
        """The estate half stays reachable — this slice adds an action, it
        does not replace the review route."""
        _owe(world)
        details = _row(world)["details"]
        assert details["review_target"] == "marshal_reward"
        assert details["route_id"] == "Ney"


class TestTheClientRendersAndRoutesIt:

    def test_the_rail_builds_a_button_from_the_action_keys(self):
        src = _read("notification_bar.gd")
        assert 'details.get("action_command", "")' in src
        assert 'details.get("action_label", "Act")' in src
        assert 'details.get("action_detail", "")' in src
        assert "_on_action_pressed.bind(action_command)" in src

    def test_it_sits_above_the_button_row_not_inside_it(self):
        """A fourth peer button widens the panel past the width
        `_position_expanded_panel` places it by, so it hangs off the edge —
        and added after `button_row` it would render below Acknowledge."""
        src = _read("notification_bar.gd")
        action_at = src.index("var action_command = str(details")
        row_at = src.index("var button_row = HBoxContainer.new()")
        assert action_at < row_at, (
            "the action must be added to the vbox BEFORE button_row")
        assert "vbox.add_child(action_btn)" in src[action_at:row_at]
        assert "button_row.add_child(action_btn)" not in src

    def test_the_rail_emits_rather_than_sending(self):
        """`notification_bar.gd` must not grow a second command pipeline."""
        src = _read("notification_bar.gd")
        assert "signal notification_action_requested(command: String)" in src
        assert "notification_action_requested.emit(command)" in src
        assert "send_command" not in src, (
            "the rail names a command; main.gd is the one place that sends it")

    def test_main_routes_it_through_the_shared_typed_pipeline(self):
        """`_on_reward_command` carries the in-flight latch, the terminal
        echo, the history entry and the Generals refresh. A bespoke handler
        would drop all four — the double-send latch most dangerously."""
        src = _read("main.gd")
        assert ("notification_bar.notification_action_requested.connect("
                "_on_reward_command)") in src
        body = src[src.index("func _on_reward_command(command: String):"):]
        body = body[:body.index("\nfunc _on_reward_command_result")]
        assert "_chip_command_in_flight" in body
        assert "api_client.send_command(command" in body

    def test_pressing_it_closes_the_panel_first(self):
        src = _read("notification_bar.gd")
        body = src[src.index("func _on_action_pressed(command: String):"):]
        body = body[:body.index("\nfunc _on_review_pressed")]
        assert body.index("_close_expanded_panel()") < body.index(
            "notification_action_requested.emit"), (
            "leaving the panel up would show it over its own stale copy")

    def test_the_reward_rows_are_findable_on_the_rail(self):
        """They fell through to the priority default ("INF"/"NEW"), which
        names neither the marshal nor the matter — and the rail is now where
        the reward is granted from, so the player has to find it first."""
        src = _read("notification_bar.gd")
        for key in ("dotation_expectation", "dotation_erosion"):
            assert f'"{key}": "PAY"' in src
        assert '"dotation_expectation": "coins"' in src
        assert '"dotation_erosion": "medal"' in src

    def test_the_glyph_files_exist(self):
        icons = os.path.join(REPO_ROOT, "godot-client", "project-sovereign",
                             "assets", "ui", "icons", "phosphor")
        for name in ("coins.svg", "medal.svg"):
            assert os.path.exists(os.path.join(icons, name)), name


class TestTheReactiveGateIsUntouched:
    """Standing user decision: fix discoverability, never the gate."""

    def test_the_generals_card_gate_is_unchanged(self):
        assert "elif shortfall > 0 or pension > 0:" in \
            _read("marshal_management.gd")

    def test_a_marshal_with_no_expectation_has_no_row_to_press(self, world):
        ney = world.marshals["Ney"]
        assert int(getattr(ney, "battles_won", 0)) == 0, "precondition"
        _reconcile(world)
        assert _rows(world) == [], (
            "the rail affordance is reactive BY CONSTRUCTION — no shortfall, "
            "no row, nothing to press")


# ══════════════════════════════════════════════════════════════════════════
# 2. UX23-R2 — the desk bell rings once per grievance
# ══════════════════════════════════════════════════════════════════════════


class TestTheBellRingsOncePerGrievance:

    def test_a_restated_row_keeps_its_id(self, world):
        _owe(world)
        first = _row(world)["id"]
        for _ in range(3):
            world.current_turn += 1
            _reconcile(world)
        rows = _rows(world)
        assert len(rows) == 1
        assert rows[0]["id"] == first, (
            "a fresh uuid re-rings the chime: notification_bar.gd dedupes on "
            "it, so this is four bells for one unpaid marshal")

    def test_the_restated_row_still_carries_live_numbers(self, world):
        ney = _owe(world, wins=1)
        first = _row(world)["message"]
        ney.battles_won = 5
        world.current_turn += 1
        _reconcile(world)
        row = _row(world)
        assert row["message"] != first, "keeping the id must not freeze the copy"
        assert str(dotation.get_expectation(ney)) in row["message"]
        assert row["details"]["action_label"] == \
            dotation.rente_action_keys(ney, world)["action_label"]

    def test_a_refresh_is_not_a_repeat(self, world):
        """`add` collapses a duplicate and re-titles it "(x2)" — which renders
        a refresh as a SECOND grievance. Dodging that is why the producers
        threw the id away in the first place."""
        _owe(world)
        for _ in range(3):
            world.current_turn += 1
            _reconcile(world)
        row = _row(world)
        assert "(x" not in row["title"]
        assert int(row.get("repeat_count", 1)) == 1

    def test_refresh_does_not_bump_the_age(self, world):
        """`turn_created` is when the grievance BEGAN. Bumping it would make
        the row's own T-stamp lie and would make every standing HIGH row
        permanently young, which is what UX23-R3's eviction reads.

        Stays INSIDE the grace window on purpose: once grace elapses the
        expectation row is retired and a genuinely new erosion row opens, so
        a longer loop would be reading a different fact (that is the sibling
        test below)."""
        _owe(world)
        opened = _row(world)["turn_created"]
        for _ in range(dotation.GRACE_TURNS - 1):
            world.current_turn += 1
            _reconcile(world)
        row = _row(world)
        assert row["type"] == DOTATION_EXPECTATION, "precondition: still in grace"
        assert row["turn_created"] == opened
        assert world.current_turn > opened, "precondition: the world moved on"

    def test_the_eroding_row_keeps_its_id_and_its_age_too(self, world):
        """The HIGH row is re-stated on EVERY eroding turn, so it was the
        loudest instance of the per-turn bell — and it is the row whose age
        UX23-R3's eviction has to be able to read."""
        _owe(world)
        for _ in range(dotation.GRACE_TURNS + 1):
            world.current_turn += 1
            _reconcile(world)
        first = next(n for n in _rows(world) if n["type"] == DOTATION_EROSION)
        opened, ident = first["turn_created"], first["id"]
        for _ in range(4):
            world.current_turn += 1
            _reconcile(world)
        rows = [n for n in _rows(world) if n["type"] == DOTATION_EROSION]
        assert len(rows) == 1
        assert rows[0]["id"] == ident
        assert rows[0]["turn_created"] == opened
        assert world.current_turn - opened >= 4

    def test_the_producers_refresh_rather_than_dismiss_and_add(self):
        import inspect
        for fn in (dotation.post_expectation_notice,
                   dotation.post_erosion_notice):
            src = inspect.getsource(fn)
            assert "notifications.refresh(create_notification(" in src, \
                fn.__name__
            assert "notifications.add(create_notification(" not in src, \
                fn.__name__

    def test_refresh_reports_whether_it_was_a_first_statement(self):
        collector = NotificationCollector()
        first = create_notification(
            DOTATION_EXPECTATION, NotificationPriority.NORMAL,
            "Marshal Ney expects reward", "a", 1, {"marshal": "Ney"})
        again = create_notification(
            DOTATION_EXPECTATION, NotificationPriority.NORMAL,
            "Marshal Ney expects reward", "b", 4, {"marshal": "Ney"})
        assert collector.refresh(first) is False
        assert collector.refresh(again) is True
        assert len(collector._pending) == 1
        assert collector._pending[0]["id"] == first["id"]
        assert collector._pending[0]["message"] == "b"

    def test_two_marshals_are_two_grievances(self, world):
        """`_identity` keys on the subject, so Ney's row must never absorb
        Davout's — the laziest wrong fix, and the one PF-5 pins against."""
        _owe(world, "Ney")
        _owe(world, "Davout")
        assert len(_rows(world, "Ney")) == 1
        assert len(_rows(world, "Davout")) == 1
        assert _rows(world, "Ney")[0]["id"] != _rows(world, "Davout")[0]["id"]

    def test_paying_still_retires_the_row(self, world):
        """The refresh path must not resurrect what a payment dismissed."""
        from backend.commands.executor import CommandExecutor

        _owe(world)
        CommandExecutor().execute(
            {"command": {"action": "grant_pension", "marshal": "Ney"}},
            {"world": world})
        assert _rows(world) == []
        world.current_turn += 1
        _reconcile(world)
        assert _rows(world) == [], "he is paid; nothing should come back"


# ══════════════════════════════════════════════════════════════════════════
# 3. UX23-R3 — a standing grievance is not immortal
# ══════════════════════════════════════════════════════════════════════════


def _fill(collector, count, priority, turn, prefix="M"):
    for i in range(count):
        collector.add(create_notification(
            DOTATION_EROSION, priority, f"Marshal {prefix}{i} grows bitter",
            "x", turn, {"marshal": f"{prefix}{i}"}))


class TestTheRailCanShedAStandingGrievance:

    def test_a_stale_high_row_yields_to_fresh_news(self):
        collector = NotificationCollector()
        _fill(collector, NOTIFICATION_CAP, NotificationPriority.HIGH, 1)
        assert len(collector._pending) == NOTIFICATION_CAP
        collector.add(create_notification(
            "war_declared", NotificationPriority.HIGH, "Prussia declares war",
            "x", 1 + HIGH_EVICTION_WINDOW_TURNS, {"nation": "Prussia"}))
        assert len(collector._pending) == NOTIFICATION_CAP, (
            "before the fix the cap simply stopped working once the tray was "
            "all HIGH")
        assert any(n["type"] == "war_declared" for n in collector._pending), (
            "the news the player needed is the thing that must survive")
        assert not any(n["details"].get("marshal") == "M0"
                       for n in collector._pending)

    def test_n_plus_one_eroding_marshals_do_not_push_the_cap(self):
        collector = NotificationCollector()
        for i in range(NOTIFICATION_CAP + 10):
            collector.add(create_notification(
                DOTATION_EROSION, NotificationPriority.HIGH,
                f"Marshal M{i} grows bitter", "x",
                1 + i * HIGH_EVICTION_WINDOW_TURNS, {"marshal": f"M{i}"}))
        assert len(collector._pending) == NOTIFICATION_CAP

    def test_a_same_turn_burst_is_never_self_truncating(self):
        """The window is what makes this safe: several crises breaking at once
        must all be shown, even past the cap."""
        collector = NotificationCollector()
        _fill(collector, NOTIFICATION_CAP + 5, NotificationPriority.HIGH, 7)
        assert len(collector._pending) == NOTIFICATION_CAP + 5

    def test_a_young_high_row_is_never_evicted(self):
        collector = NotificationCollector()
        _fill(collector, NOTIFICATION_CAP, NotificationPriority.HIGH, 1)
        collector.add(create_notification(
            "war_declared", NotificationPriority.HIGH, "Prussia declares war",
            "x", HIGH_EVICTION_WINDOW_TURNS - 1, {"nation": "Prussia"}))
        assert len(collector._pending) == NOTIFICATION_CAP + 1, (
            "one turn short of the window, nothing is stale enough to drop")

    def test_critical_is_never_evicted(self):
        collector = NotificationCollector()
        _fill(collector, NOTIFICATION_CAP, NotificationPriority.CRITICAL, 1)
        collector.add(create_notification(
            "war_declared", NotificationPriority.CRITICAL,
            "Prussia declares war", "x", 500, {"nation": "Prussia"}))
        assert len(collector._pending) == NOTIFICATION_CAP + 1

    def test_normal_is_still_spent_before_any_high(self):
        collector = NotificationCollector()
        _fill(collector, NOTIFICATION_CAP - 1, NotificationPriority.HIGH, 1)
        collector.add(create_notification(
            "dp_insufficient", NotificationPriority.NORMAL, "No DP", "x", 1,
            {"nation": "France"}))
        collector.add(create_notification(
            "war_declared", NotificationPriority.HIGH, "Prussia declares war",
            "x", 500, {"nation": "Prussia"}))
        assert len(collector._pending) == NOTIFICATION_CAP
        assert not any(n["type"] == "dp_insufficient"
                       for n in collector._pending)
        assert any(n["details"].get("marshal") == "M0"
                   for n in collector._pending), (
            "the oldest HIGH must survive while a NORMAL row is still "
            "spendable")
