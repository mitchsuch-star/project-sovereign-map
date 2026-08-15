"""CA9 row 3 / A7 — `jealousy_note` reaches every battle.

Audit record: `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md`
(authoritative), item A7.

The note was composed in `_execute_attack` ONLY, from a heuristic
(`jealousy_surge_turns > 0 and not jealous_of`) rather than from what the
resolver actually decided. Three consequences, all fixed here:

* a grievance settled on DEFENCE was composed but then **dropped by the
  client** — `enemy_phase_dialog._format_berthier_report` has a field
  whitelist and `jealousy_note` was not in it;
* the **glorious charge** and the **reckless auto-charge** resolve
  grievances, ship a `battle_report`, and never carried a note at all
  (the row-3 memo asserted the reckless site "has no `battle_report` in
  scope" — it does: `combat_result["battle_report"]`, the very dict the
  event ships);
* the heuristic **lied**. A surge granted by last turn's ladder shift
  survives into this turn (`process_turn` decrements at step 0 and grants
  at step 1), so an unrelated battle claimed *"his grievance is settled"*
  about a battle that settled nothing; a marshal's second battle in a turn
  repeated the claim; and a PARTICIPANT's resolution — which the resolver
  has always granted — was invisible, because the loop only ever inspected
  the two primaries.

N36 closes here too: the battle surface OWNS a battle-time resolution, and
the duplicate next-morning bullet is withheld for exactly the men the note
named. Non-battle resolutions (timer, petition, ladder shift) keep their
bullet untouched, so A2's cause-naming and A13's `by_action` discriminator
both survive intact.
"""

import ast
import io
import tokenize
from pathlib import Path

import pytest

from backend.campaign_log import CAMPAIGN_LOG_TYPES
from backend.commands.executor import CommandExecutor
from backend.game_logic import jealousy as J

from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
GD = REPO / "godot-client" / "project-sovereign" / "scripts"


# ════════════════════════════════════════════════════════════════════════
# Fixtures
# ════════════════════════════════════════════════════════════════════════

def _strip_comments(src: str) -> str:
    """Source with `#` comments removed (string literals kept)."""
    out = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type != tokenize.COMMENT:
            out.append(tok.string)
    return "\n".join(out)


def _war(world, a="France", b="Austria"):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


@pytest.fixture()
def trio():
    """A literal Soult envious of Ney, plus an Austrian to fight.

    `literal` is deliberate: its resolution predicate is "meaningful
    contact with the enemy", which fires on ANY battle participation
    regardless of who wins — so the seam is exercised deterministically
    and these tests do not depend on a combat roll.
    """
    soult = MarshalFactory.infantry(name="Soult", location="Belgium",
                                    strength=30000, personality="literal")
    ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                  strength=30000, personality="aggressive")
    mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                nation="Austria", strength=24000,
                                personality="cautious")
    world = WorldFactory.with_marshals([soult, ney, mack])
    _war(world)
    world.calculate_visibility()
    return world, CommandExecutor()


# ════════════════════════════════════════════════════════════════════════
# The composer — driven by the resolver, not by a heuristic
# ════════════════════════════════════════════════════════════════════════

class TestComposerIsDrivenByTheResolver:
    def test_a_settled_grievance_is_named(self, trio):
        world, _ = trio
        soult = world.marshals["Soult"]
        record = {"marshal": "Soult", "target": "Ney", "nation": "France",
                  "personality": "literal", "by_action": True,
                  "reason": "meaningful contact with the enemy",
                  "is_player": True}
        note, reported = J.compose_battle_jealousy_note(
            world, (soult, world.marshals["Mack"]), [record])
        assert "Soult" in note and "grievance is settled" in note, note
        assert reported == ["Soult"]

    def test_a_still_aggrieved_primary_keeps_its_pre_a7_copy(self, trio):
        """The three personality strings are byte-identical to the ones
        the pre-A7 heuristic produced — this arm was never the defect."""
        world, _ = trio
        ney = world.marshals["Ney"]
        ney.jealous_of = "Soult"
        note, reported = J.compose_battle_jealousy_note(
            world, (ney, world.marshals["Mack"]), [])
        assert note == ("Ney fought with particular ferocity — though one "
                        "wonders if it was for France or for himself.")
        # An aggrieved man is NOT a resolution, so nothing is suppressed.
        assert reported == []

    def test_a_participant_resolution_is_named(self, trio):
        """Impossible before A7: the loop only ever saw the two primaries,
        so a cautious ally who settled 'shoulder to shoulder' — which the
        resolver has always granted — was reported nowhere."""
        world, _ = trio
        soult, mack = world.marshals["Soult"], world.marshals["Mack"]
        record = {"marshal": "Lannes", "target": "Ney", "nation": "France",
                  "personality": "cautious", "by_action": True,
                  "reason": "a victory won shoulder to shoulder",
                  "is_player": True}
        note, reported = J.compose_battle_jealousy_note(
            world, (soult, mack), [record])
        assert "Lannes" in note, note
        assert reported == ["Lannes"]

    def test_an_enemy_resolution_is_never_narrated(self, trio):
        world, _ = trio
        record = {"marshal": "Mack", "target": "ArchdukeCharles",
                  "nation": "Austria", "personality": "cautious",
                  "by_action": True, "reason": "x", "is_player": False}
        note, reported = J.compose_battle_jealousy_note(
            world, (world.marshals["Soult"], world.marshals["Mack"]),
            [record])
        assert note == ""
        assert reported == []

    # ── the three lies the heuristic told ──────────────────────────────

    def test_a_stale_surge_no_longer_claims_a_settlement(self, trio):
        """NEGATIVE CONTROL for the ladder-shift leak.

        `process_turn` decrements the surge at step 0 and GRANTS one at
        step 1 (ladder-shift resolution), so a surge granted on turn N
        survives all of turn N+1. Under the old heuristic every battle
        that marshal fought on N+1 printed "fought like a man with
        something to prove — and proved it", about a battle that settled
        nothing. The state that fooled it is set up exactly here.
        """
        world, _ = trio
        soult = world.marshals["Soult"]
        soult.jealousy_surge_turns = 1     # the heuristic's first clause
        soult.jealous_of = None            # ...and its second
        note, reported = J.compose_battle_jealousy_note(
            world, (soult, world.marshals["Mack"]), [])   # no resolution
        assert note == "", note
        assert reported == []

    def test_a_second_battle_in_one_turn_does_not_repeat_the_claim(self, trio):
        """Same root cause: the surge is still set after the first battle
        of the turn, so battle two replayed the settlement line."""
        world, _ = trio
        soult = world.marshals["Soult"]
        soult.jealousy_surge_turns = 1
        soult.jealous_of = None
        first, _ = J.compose_battle_jealousy_note(
            world, (soult, world.marshals["Mack"]),
            [{"marshal": "Soult", "target": "Ney", "nation": "France",
              "personality": "literal", "by_action": True, "reason": "r",
              "is_player": True}])
        second, _ = J.compose_battle_jealousy_note(
            world, (soult, world.marshals["Mack"]), [])
        assert "grievance is settled" in first
        assert second == "", second


# ════════════════════════════════════════════════════════════════════════
# The resolver returns its work, and defers the bullet on request
# ════════════════════════════════════════════════════════════════════════

class TestResolverContract:
    def _resolve(self, world, **kw):
        soult, mack = world.marshals["Soult"], world.marshals["Mack"]
        soult.jealous_of = "Ney"
        return J.check_battle_resolution(
            world, soult, mack, True, False, 30000, 24000, **kw)

    def test_it_returns_the_records(self, trio):
        world, _ = trio
        records = self._resolve(world)
        assert [r["marshal"] for r in records] == ["Soult"]
        assert records[0]["by_action"] is True
        assert records[0]["is_player"] is True
        assert records[0]["personality"] == "literal"

    def test_the_default_still_emits_the_bullet(self, trio):
        """Safe-by-default: a caller that does not opt in keeps today's
        behaviour (a duplicated line) rather than silently losing the
        beat. That is why `defer_dispatch` defaults to False."""
        world, _ = trio
        before = len(J._pending_events(world))
        self._resolve(world)
        new = J._pending_events(world)[before:]
        assert any(e["type"] == "jealousy_resolved" for e in new)

    def test_defer_dispatch_withholds_the_bullet(self, trio):
        world, _ = trio
        before = len(J._pending_events(world))
        self._resolve(world, defer_dispatch=True)
        new = J._pending_events(world)[before:]
        assert not any(e["type"] == "jealousy_resolved" for e in new)

    def test_deferring_never_suppresses_the_campaign_log_record(self, trio):
        """The record is a record. Only the NARRATION moves surfaces."""
        world, _ = trio
        before = len(world.event_log)
        self._resolve(world, defer_dispatch=True)
        logged = world.event_log[before:]
        assert any(e["type"] == "jealousy_resolved" for e in logged)

    def test_clear_jealousy_returns_a_record(self, trio):
        world, _ = trio
        soult = world.marshals["Soult"]
        soult.jealous_of = "Ney"
        rec = J.clear_jealousy(world, soult, resolved_by_action=False,
                               events=[], reason="time")
        assert rec["marshal"] == "Soult" and rec["target"] == "Ney"
        assert rec["by_action"] is False


class TestUnreportedResolutionsStillGetTheirBullet:
    def test_a_named_man_is_suppressed(self, trio):
        world, _ = trio
        rec = {"marshal": "Soult", "target": "Ney", "nation": "France",
               "personality": "literal", "by_action": True, "reason": "r",
               "is_player": True}
        before = len(J._pending_events(world))
        J.emit_unreported_resolutions(world, [rec], ["Soult"])
        assert J._pending_events(world)[before:] == []

    def test_an_unnamed_man_is_not(self, trio):
        world, _ = trio
        rec = {"marshal": "Soult", "target": "Ney", "nation": "France",
               "personality": "literal", "by_action": True, "reason": "r",
               "is_player": True}
        before = len(J._pending_events(world))
        J.emit_unreported_resolutions(world, [rec], [])
        new = J._pending_events(world)[before:]
        assert len(new) == 1
        assert new[0]["by_action"] is True
        assert "Soult" in new[0]["message"]

    def test_the_bullet_is_single_sourced(self, trio):
        """`_action_resolution_event` is built in two places now (clear
        time and deferred re-emission). Two copies of this sentence is
        how the surfaces drift apart, so they must be one function.

        The equality alone is INERT — it compares two calls to the same
        helper, so mutating the helper moves both sides together and the
        assertion still holds (a mutation sweep caught exactly that). It
        is binding only alongside the content pin below and the structural
        pin that `clear_jealousy` routes through the helper at all.
        """
        world, _ = trio
        soult = world.marshals["Soult"]
        soult.jealous_of = "Ney"
        events = []
        J.clear_jealousy(world, soult, resolved_by_action=True,
                         events=events, reason="meaningful contact")
        at_clear = events[0]["message"]
        deferred = J._action_resolution_event(
            {"marshal": "Soult", "nation": "France", "personality": "literal",
             "reason": "meaningful contact"})["message"]
        assert at_clear == deferred
        # …and the sentence is the one A2 landed, on BOTH surfaces.
        assert "Soult's grievance is satisfied — meaningful contact" \
            in at_clear, at_clear
        assert "+10% attack this turn" not in at_clear   # literal, not aggressive
        assert "His patrols keep their edge" in at_clear

    def test_clear_jealousy_routes_through_the_shared_builder(self):
        """The structural half: the action branch must CALL the helper,
        not re-author the sentence beside it."""
        src = (REPO / "backend/game_logic/jealousy.py").read_text(
            encoding="utf-8")
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef)
                  and n.name == "clear_jealousy")
        calls = {getattr(c.func, "id", None) or getattr(c.func, "attr", None)
                 for c in ast.walk(fn) if isinstance(c, ast.Call)}
        assert "_action_resolution_event" in calls
        # And the sentence itself exists in exactly one place. Comments are
        # stripped first — the surrounding prose legitimately QUOTES the
        # line when explaining why the cooling branch says something else,
        # and a naive `src.count` reads that as a second copy.
        code = _strip_comments(src)
        assert code.count("grievance is satisfied") == 1


# ════════════════════════════════════════════════════════════════════════
# The three battle paths
# ════════════════════════════════════════════════════════════════════════

class TestTheNoteReachesTheBattle:
    def test_the_players_own_attack(self, trio):
        world, executor = trio
        world.marshals["Soult"].jealous_of = "Ney"
        result = executor.execute(
            {"success": True,
             "command": {"marshal": "Soult", "action": "attack",
                         "target": "Mack"}},
            {"world": world})
        report = result.get("battle_report") or {}
        assert "jealousy_note" in report, sorted(report)
        assert "Soult" in report["jealousy_note"]

    def test_a_grievance_settled_on_DEFENCE(self, trio):
        """The enemy phase runs through the SAME `_execute_attack` (GR5),
        with the player marshal as defender. The note was already composed
        for this case — the client threw it away."""
        world, executor = trio
        world.marshals["Soult"].jealous_of = "Ney"
        result = executor.execute(
            {"success": True,
             "command": {"marshal": "Mack", "action": "attack",
                         "target": "Soult"}},
            {"world": world})
        report = result.get("battle_report") or {}
        assert "jealousy_note" in report, sorted(report)
        assert "Soult" in report["jealousy_note"]

    def test_the_battle_surface_owns_it_and_the_bullet_is_withheld(self, trio):
        """N36: one surface, not three. A battle-resolved grievance emits
        no next-morning bullet AND no end-turn terminal echo, because both
        read the same `_pending_jealousy_turn_events` stash."""
        world, executor = trio
        world.marshals["Soult"].jealous_of = "Ney"
        before = len(J._pending_events(world))
        executor.execute(
            {"success": True,
             "command": {"marshal": "Soult", "action": "attack",
                         "target": "Mack"}},
            {"world": world})
        new = J._pending_events(world)[before:]
        assert not [e for e in new
                    if e.get("type") == "jealousy_resolved"
                    and e.get("marshal") == "Soult"], new

    def test_a_NON_battle_resolution_keeps_its_bullet(self, trio):
        """The other half of N36 — and the guard on A2/A13. A timer
        expiry, a petition answer and a ladder shift have no battle
        surface, so their bullet must be untouched."""
        world, _ = trio
        soult = world.marshals["Soult"]
        soult.jealous_of = "Ney"
        events = []
        J.clear_jealousy(world, soult, resolved_by_action=False,
                         events=events, reason="time")
        assert [e for e in events if e["type"] == "jealousy_resolved"]


# ════════════════════════════════════════════════════════════════════════
# Structural: every resolution seam carries an arm
# ════════════════════════════════════════════════════════════════════════

class TestEveryCallSiteCarriesAnArm:
    """A call-site census rather than three hand-written pins.

    The whole A7 defect was that ONE of three seams composed the note.
    A fourth seam added later must not be able to reintroduce it silently,
    so the pin is over the call sites themselves.
    """

    SITES = [
        ("backend/commands/combat_executor.py", "_execute_attack"),
        ("backend/commands/combat_executor.py", "_post_combat_pipeline"),
        ("backend/models/world_state.py",
         "_process_reckless_cavalry_turn_start"),
    ]

    def _calls(self, path):
        """Every `check_battle_resolution(...)` call, with its enclosing
        function and whether it passes `defer_dispatch`."""
        tree = ast.parse((REPO / path).read_text(encoding="utf-8"))
        parents = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        found = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = getattr(fn, "attr", None) or getattr(fn, "id", None)
            if name != "check_battle_resolution":
                continue
            owner, cur = None, node
            while cur in parents:
                cur = parents[cur]
                if isinstance(cur, ast.FunctionDef):
                    owner = cur.name
                    break
            defers = any(k.arg == "defer_dispatch" for k in node.keywords)
            found.append((owner, defers))
        return found

    def test_the_census_is_exactly_the_three_known_seams(self):
        actual = set()
        for path in {p for p, _ in self.SITES}:
            for owner, _ in self._calls(path):
                actual.add((path, owner))
        assert actual == set(self.SITES), (
            "a new battle seam calls check_battle_resolution — give it a "
            f"jealousy_note arm or add it here: {actual ^ set(self.SITES)}")

    def test_every_seam_defers_its_bullet(self):
        for path in {p for p, _ in self.SITES}:
            for owner, defers in self._calls(path):
                assert defers, f"{path}::{owner} does not pass defer_dispatch"

    def test_every_seam_composes_a_note(self):
        for path in {p for p, _ in self.SITES}:
            src = (REPO / path).read_text(encoding="utf-8")
            assert src.count("compose_battle_jealousy_note") == \
                len(self._calls(path)), path
            assert src.count("emit_unreported_resolutions") == \
                len(self._calls(path)), path


class TestGodotSurfaces:
    def test_the_enemy_phase_dialog_reads_the_note(self):
        """The payload always carried it here; the whitelist did not read
        it — so a grievance settled while the player was being ATTACKED,
        which is most of them, was reported nowhere."""
        src = (GD / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
        assert '"jealousy_note"' in src

    def test_the_player_attack_surface_still_reads_it(self):
        src = (GD / "main.gd").read_text(encoding="utf-8")
        assert '"jealousy_note"' in src


def test_no_new_campaign_log_type():
    """A7 adds no event type — it moves an existing one between
    surfaces. Pinned in six files; this is the local statement of it."""
    assert len(CAMPAIGN_LOG_TYPES) == 158  # 157->158 flipped consciously: PC15-1 adds `marshal_destroyed`
