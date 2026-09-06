"""FA-91 — "The Gate Sees What Bites".

`test_serialization_enforcement.py` is the suite whose whole purpose is to
catch an unserialized field, and **two real save defects walked straight past
it**: IGR-X1 (`Marshal._recovery_destination`, a serialized private later
`delattr`'d) and FA-S15-1 (`original_nation` deleted at runtime, breaking
every save for the rest of a campaign). Three blind spots, all named on the
row and all confirmed by measurement:

* **private** — `get_instance_attributes` dropped every `_`-name, so a
  serialized private was invisible. Popping `_recovery_destination` out of
  `to_dict` left BOTH Marshal pins green while a live value round-tripped to
  `None`. *(Closed in `test_serialization_enforcement.py` itself.)*
* **no round trip** — `test_all_world_state_fields_serialized` never calls
  `from_dict`, so nothing pinned that what `to_dict` writes comes back.
* **lazily created** — the sweeps run on FRESHLY CONSTRUCTED objects, and a
  field that only exists after six turns of play cannot be seen at all.

⚠ **The row's own `fix_shape` does not close its own title, and that is
measured, not argued.** Mutation-swept on a played world: a round trip alone
kills 5 of 7 mutations and **survives the two that matter** — dropping
`_recovery_destination` from `to_dict`, and dropping the public `fortified`.
If `to_dict` never emits a key then BOTH sides lack it and
`to_dict() == from_dict(to_dict()).to_dict()` is trivially true. **The round
trip is structurally blind to every `to_dict` omission.**

⚠ **And its prescribed depth of 3 turns makes the whole thing inert.** At 3
turns the round trip has 0 divergences and the played sweep finds nothing a
synthetic fixture does not. `ai_square_cooldown` first exists at **turn 6**;
`_jealousy_solo_attack` at turn 20; the only round-trip divergence at turn
30 — and that one is PC15-17 behaving correctly, so a deeper drive would
force an allow-list for a legitimate case. **Twelve turns is the window**:
deep enough for the real defect, shallow enough to need no allow-list.
"""

import ast
import contextlib
import importlib.util
import inspect
import io
import os
import pathlib
import tempfile

import pytest

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]

# ⚠ LOAD-BEARING, see the module docstring. Do not lower this without
# re-measuring: below turn 6 the census has nothing to find, and at turn 30
# it inherits a legitimate PC15-17 divergence that would need an allow-list.
CENSUS_TURNS = 12
_FIRST_LAZY_FIELD_TURN = 6


def _played_world(turns=CENSUS_TURNS):
    """A world that has actually been played, via the real driver."""
    import argparse

    spec = importlib.util.spec_from_file_location(
        "pdrv_fa91", str(REPO / "tools" / "playtest_driver.py"))
    drv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(drv)

    captured = []
    import backend.game_logic.dispatch as dsp
    real = dsp.build_morning_dispatch

    def spy(world, *a, **k):
        captured.append(world)
        return real(world, *a, **k)

    prev = {k: os.environ.get(k)
            for k in ("INK_IRON_SAVE_DIR", "SOVEREIGN_SEED", "LLM_MODE")}
    tmp = tempfile.mkdtemp()
    try:
        dsp.build_morning_dispatch = spy
        os.environ["INK_IRON_SAVE_DIR"] = os.path.join(tmp, "saves")
        os.environ["SOVEREIGN_SEED"] = "historical"
        os.environ["LLM_MODE"] = "mock"
        ns = argparse.Namespace(
            name="fa91", turns=turns, seed="historical", llm="mock",
            scenario="", script="", from_save="", http="",
            out=os.path.join(tmp, "out"), save_at="", objection="",
            diplomacy="", cheats=False, strict=False, verbose=False,
            fresh=True, archive=False)
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                drv.run(ns)
            except SystemExit:
                pass
    finally:
        dsp.build_morning_dispatch = real
        for k, v in prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    assert captured, "the driver never produced a world"
    return captured[-1], tmp


@pytest.fixture(scope="module")
def played():
    world, _tmp = _played_world()
    return world


# ═══════════════════════════════════════════════════════════════════════════
# B1/B2 — the round trip, and what it can and cannot see
# ═══════════════════════════════════════════════════════════════════════════

class TestThePlayedRoundTrip:

    def test_it_reaches_a_depth_where_there_is_something_to_find(self, played):
        """⚠ The depth IS the test. Pinned with its reason so nobody lowers
        it back to the row's prescribed 3, at which both clauses are inert."""
        assert played.current_turn > _FIRST_LAZY_FIELD_TURN, (
            f"the census must run past turn {_FIRST_LAZY_FIELD_TURN}: "
            "`ai_square_cooldown` does not exist before then and a "
            "shallower drive makes the played sweep vacuous")

    def test_to_dict_survives_from_dict(self, played):
        import json
        blob = json.loads(json.dumps(played.to_dict()))
        with contextlib.redirect_stdout(io.StringIO()):
            back = WorldState.from_dict(blob)
        # ⚠ Added after a sweep: `back = played` made this pin pass
        # trivially. A round trip that is not a round trip is the purest
        # form of the vacuity this whole file exists to hunt.
        assert back is not played
        assert isinstance(back, WorldState)
        before, after = played.to_dict(), back.to_dict()
        diverged = [k for k in set(before) | set(after)
                    if before.get(k) != after.get(k)]
        assert diverged == [], diverged

    def test_it_survives_save_and_load(self, played):
        from backend.save_manager import load_game, save_game
        tmp = tempfile.mkdtemp()
        prev = os.environ.get("INK_IRON_SAVE_DIR")
        os.environ["INK_IRON_SAVE_DIR"] = tmp
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                res = save_game(played, "fa91_census")
                assert res.get("success"), res
                loaded = load_game(pathlib.Path(res["filepath"]))
        finally:
            if prev is None:
                os.environ.pop("INK_IRON_SAVE_DIR", None)
            else:
                os.environ["INK_IRON_SAVE_DIR"] = prev
        world = loaded.get("world") if isinstance(loaded, dict) else loaded
        assert world is not None, loaded
        before, after = played.to_dict(), world.to_dict()
        diverged = [k for k in set(before) | set(after)
                    if before.get(k) != after.get(k)]
        assert diverged == [], diverged

    def test_the_round_trip_is_blind_to_a_to_dict_omission(self):
        """⚠ THE POINT OF THIS FILE, stated as a falsifiable property rather
        than a warning: the round trip CANNOT catch the class of defect the
        row exists to close. If `to_dict` never emits a key, both sides lack
        it and equality holds. So the field census is not an optional extra
        beside the round trip — it is the half that works.
        """
        m = Marshal(name="Probe", nation="France", location="Paris",
                    strength=1000, personality="cautious")
        m._recovery_destination = "Bohemia"
        original = Marshal.to_dict

        def amputated(self):
            d = original(self)
            d.pop("_recovery_destination", None)
            return d

        try:
            Marshal.to_dict = amputated
            a = m.to_dict()
            b = Marshal.from_dict(a).to_dict()
            assert a == b, "the round trip noticed — rewrite this pin"
        finally:
            Marshal.to_dict = original
        # …and the live value really was lost, so the silence is a defect
        assert Marshal.from_dict(amputated(m))._recovery_destination is None


# ═══════════════════════════════════════════════════════════════════════════
# B3 — the field census on objects that have been PLAYED
# ═══════════════════════════════════════════════════════════════════════════

def _exempt_for(obj):
    """⚠ Both sets come from PRODUCTION, never from a copy here.

    `READ_ONCE_NOTE_FIELDS` was added by this census: the played sweep went
    red on `Napoleon._sovereign_toll_note`, a Guard-toll note written at one
    combat seam and blanked at exactly one other. It is genuinely transient —
    but until FA-91 nothing in the tree SAID so, and an exemption invented
    in a test file is how the next one gets waved through.
    """
    if isinstance(obj, Marshal):
        return (set(Marshal.COORDINATION_TRANSIENT_FIELDS)
                | set(Marshal.READ_ONCE_NOTE_FIELDS))
    return set()


def _misses(obj):
    ser = set(obj.to_dict())
    out = set()
    for k in vars(obj):
        if k in ser or k in _exempt_for(obj):
            continue
        if k.startswith("_") and k.lstrip("_") in ser:
            continue                       # R1: property-backed
        out.add(k)
    return out


class TestThePlayedFieldCensus:

    def test_every_played_marshal_is_fully_serialized(self, played):
        """⚠ This went RED on the shipped board when it was written, which is
        the strongest form of falsifiability available: `ai_square_cooldown`
        — the 2-turn anti-oscillation guard — was created lazily from turn 6,
        written by both the AI and the player's own square break, decremented
        every turn, read before re-forming, and serialized NOWHERE. A
        save/load cleared it and the guard could be walked through.
        """
        bad = {m.name: sorted(_misses(m)) for m in played.marshals.values()
               if _misses(m)}
        assert bad == {}, bad

    def test_every_played_region_is_fully_serialized(self, played):
        bad = {n: sorted(_misses(r)) for n, r in played.regions.items()
               if _misses(r)}
        assert bad == {}, bad

    def test_every_played_order_and_trust_is_fully_serialized(self, played):
        bad = {}
        for m in played.marshals.values():
            for label, obj in (("order", getattr(m, "strategic_order", None)),
                               ("trust", getattr(m, "trust", None))):
                if obj is None or not hasattr(obj, "to_dict"):
                    continue
                miss = _misses(obj)
                if miss:
                    bad[f"{m.name}.{label}"] = sorted(miss)
        assert bad == {}, bad

    def test_the_read_once_notes_are_declared_in_production(self):
        """The census found `_sovereign_toll_note` and the answer was to
        DECLARE it, in `marshal.py`, beside the seams that use it — not to
        add a string to a test file. Both names must be genuinely read-once:
        each has exactly one writer and one consumer that blanks it."""
        assert set(Marshal.READ_ONCE_NOTE_FIELDS) == {
            "_sovereign_toll_note", "_fate_note"}
        assert not (set(Marshal.READ_ONCE_NOTE_FIELDS)
                    & set(Marshal.COORDINATION_TRANSIENT_FIELDS)), (
            "a read-once note must not also claim the coordination clearing "
            "contract — they are exempt for different reasons")
        src = (REPO / "backend" / "commands" /
               "combat_executor.py").read_text(encoding="utf-8")
        for name in Marshal.READ_ONCE_NOTE_FIELDS:
            assert f'{name} = ""' in src, (
                f"{name} claims to be read-once but nothing blanks it")

    def test_the_census_can_see_an_offender(self, played):
        """Sensitivity arm. Without it the three pins above pass on a
        `_misses` that always returns the empty set.

        ⚠ Both shapes, added after a sweep found the private arm untested:
        a public field AND a private one with no serialized twin. The
        private is the one FA-91 exists for, and a public-only arm let a
        mutation that re-exempts every private slip through green.
        """
        m = next(iter(played.marshals.values()))
        m.__dict__["a_field_nobody_serialized"] = 7
        m.__dict__["_a_private_nobody_serialized"] = 7
        try:
            got = _misses(m)
            assert "a_field_nobody_serialized" in got
            assert "_a_private_nobody_serialized" in got, (
                "the played census still cannot see an unserialized private")
        finally:
            m.__dict__.pop("a_field_nobody_serialized", None)
            m.__dict__.pop("_a_private_nobody_serialized", None)


# ═══════════════════════════════════════════════════════════════════════════
# The gate's own blind spots, pinned so they cannot reopen
# ═══════════════════════════════════════════════════════════════════════════

class TestTheGateSeesPrivates:

    def test_a_serialized_private_is_swept(self):
        """P1 — the mutation that distinguishes the real fix from the
        prescribed one. Before FA-91 this passed with `to_dict` amputated."""
        import test_serialization_enforcement as tse
        m = tse.create_fully_populated_marshal()
        assert "_recovery_destination" in vars(m)
        attrs = tse.get_instance_attributes(
            m, private_exempt=Marshal.COORDINATION_TRANSIENT_FIELDS,
            serialized=set(m.to_dict()))
        assert "_recovery_destination" in attrs, (
            "the sweep still cannot see a serialized private")

    def test_the_old_blanket_filter_could_not(self):
        """Paired arm: the legacy call shape must still hide it, or the pin
        above is not measuring the change."""
        import test_serialization_enforcement as tse
        m = tse.create_fully_populated_marshal()
        assert "_recovery_destination" not in tse.get_instance_attributes(m)

    def test_the_enforcement_suite_marshal_sweep_actually_uses_it(self):
        """⚠ Added after a sweep: nothing drove the enforcement suite's OWN
        Marshal sweep, so removing the exemption from that call site was
        invisible. Amputate a serialized private and the real test must
        raise — anything less pins the helper and not the caller."""
        import test_serialization_enforcement as tse
        original = Marshal.to_dict

        def amputated(self):
            d = original(self)
            d.pop("_recovery_destination", None)
            return d

        case = tse.TestMarshalSerializationEnforcement()
        try:
            Marshal.to_dict = amputated
            with pytest.raises(AssertionError, match="_recovery_destination"):
                case.test_all_marshal_fields_serialized()
        finally:
            Marshal.to_dict = original
        # …and it passes again once the field is back
        case.test_all_marshal_fields_serialized()

    def test_the_authority_tracker_sweep_sees_its_serialized_private(self):
        """`AuthorityTracker._crossed_thresholds` is serialized under its
        PRIVATE name — the same shape as `_recovery_destination`, and the
        second real instance of the blind spot. That class also carried a
        SECOND, inline private re-filter; removing only the helper's copy
        would have left this one doing the same damage."""
        import test_serialization_enforcement as tse
        from backend.models.authority import AuthorityTracker
        assert "_crossed_thresholds" in AuthorityTracker().to_dict()
        original = AuthorityTracker.to_dict

        def amputated(self):
            d = original(self)
            d.pop("_crossed_thresholds", None)
            return d

        case = tse.TestAuthorityTrackerSerializationEnforcement()
        try:
            AuthorityTracker.to_dict = amputated
            with pytest.raises(AssertionError, match="_crossed_thresholds"):
                case.test_all_authority_tracker_fields_serialized()
        finally:
            AuthorityTracker.to_dict = original
        case.test_all_authority_tracker_fields_serialized()

    def test_r1_exempts_only_a_property_backed_private(self):
        from backend.models.marshal import Trust
        tr = Trust(75)
        attrs_module = __import__(
            "test_serialization_enforcement", fromlist=["x"])
        got = attrs_module.get_instance_attributes(
            tr, private_exempt=frozenset(), serialized=set(tr.to_dict()))
        assert "_value" not in got, "R1 should exempt `_value` behind `value`"
        tr._not_a_property = 1
        got = attrs_module.get_instance_attributes(
            tr, private_exempt=frozenset(), serialized=set(tr.to_dict()))
        assert "_not_a_property" in got, (
            "R1 must exempt ONLY the property-backed shape")

    def test_the_exemption_is_not_a_copy(self):
        """⚠ P4 / anti-rot. Marshal's exemption must POINT AT the production
        tuple. A literal set here is what rots: the two `total_coordination_*`
        entries deleted by FA-91 were exactly that, a copy of two of its
        eleven names, and they had already fallen behind."""
        import test_serialization_enforcement as tse
        cls = tse.TestMarshalSerializationEnforcement
        assert cls.PRIVATE_EXEMPT is Marshal.COORDINATION_TRANSIENT_FIELDS
        assert "total_coordination_attack_bonus" not in cls.KNOWN_EXCLUSIONS
        assert "total_coordination_defense_bonus" not in cls.KNOWN_EXCLUSIONS

    def test_removing_an_exemption_entry_makes_the_sweep_red(self):
        """P4's teeth: the exemption set may not silently widen back into
        the blanket filter it replaced."""
        import test_serialization_enforcement as tse
        m = tse.create_fully_populated_marshal()
        m._jealousy_solo_attack = True
        full = set(Marshal.COORDINATION_TRANSIENT_FIELDS)
        assert "_jealousy_solo_attack" not in tse.get_instance_attributes(
            m, private_exempt=full, serialized=set(m.to_dict()))
        narrowed = full - {"_jealousy_solo_attack"}
        assert "_jealousy_solo_attack" in tse.get_instance_attributes(
            m, private_exempt=narrowed, serialized=set(m.to_dict()))


class TestTheWorldStatePinCallsFromDict:
    """⚠ P5. This must be an AST CALL census and never a substring.

    Measured on the pre-FA-91 file: `'from_dict' in source` was **True** —
    because of a COMMENT ("reconstructed by __init__/from_dict") and an
    error-message f-string — while an AST walk over the body found only
    `WorldState`, `get_instance_attributes`, `get_serialized_keys` and
    `sorted`. That is this build's signature failure mode: prose inside a
    file a pin reads is code.
    """

    @staticmethod
    def _calls(fn):
        tree = ast.parse(inspect.getsource(fn).lstrip())
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                if isinstance(f, ast.Name):
                    names.add(f.id)
                elif isinstance(f, ast.Attribute):
                    names.add(f.attr)
        return names

    def test_the_world_state_sweep_round_trips(self):
        import test_serialization_enforcement as tse
        fn = tse.TestWorldStateSerializationEnforcement \
            .test_all_world_state_fields_serialized
        assert "from_dict" in self._calls(fn), (
            "the WorldState sweep must actually CALL from_dict — a "
            "substring check is satisfied by a comment")

    def test_a_substring_check_would_have_passed_on_prose(self):
        """The sensitivity arm that makes the pin above meaningful."""
        src = "def f():\n    # reconstructed by from_dict\n    return 1\n"
        assert "from_dict" in src
        tree = ast.parse(src)
        calls = {n.func.id for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        assert "from_dict" not in calls


# ═══════════════════════════════════════════════════════════════════════════
# The field the census found
# ═══════════════════════════════════════════════════════════════════════════

class TestTheAntiOscillationGuardSurvivesALoad:

    def test_the_cooldown_round_trips(self):
        m = Marshal(name="Probe", nation="Austria", location="Vienna",
                    strength=9000, personality="cautious")
        m.ai_square_cooldown = 2
        assert Marshal.from_dict(m.to_dict()).ai_square_cooldown == 2

    def test_a_fresh_marshal_declares_it(self):
        """It used to be created lazily, which is precisely why the
        fresh-object sweep could not see it."""
        m = Marshal(name="Probe", nation="Austria", location="Vienna",
                    strength=9000, personality="cautious")
        assert "ai_square_cooldown" in vars(m)
        assert m.ai_square_cooldown == 0

    def test_the_guard_still_refuses_after_a_load(self):
        """⚠ Behavioural, not a key check. The cooldown exists to stop a
        square re-forming for two turns; a load used to clear it, so the
        guard was defeated by saving."""
        from backend.ai.enemy_ai import EnemyAI  # noqa: F401  (import guard)
        m = Marshal(name="Probe", nation="Austria", location="Vienna",
                    strength=9000, personality="cautious")
        m.ai_square_cooldown = 2
        restored = Marshal.from_dict(m.to_dict())
        assert getattr(restored, "ai_square_cooldown", 0) > 0, (
            "the anti-oscillation guard is cleared by a save/load")

    def test_it_is_named_in_the_save_format_reference(self):
        """⚠ BOTH surfaces, after a sweep found the single check inert: the
        JSON example AND the field table. A key that appears only in the
        example blob is half-documented — the table is where a reader looks
        up what a field MEANS, and deleting the row left the pin green."""
        doc = (REPO / "docs" / "SAVE_FORMAT_REFERENCE.md").read_text(
            encoding="utf-8")
        assert '"ai_square_cooldown"' in doc, "missing from the JSON example"
        rows = [ln for ln in doc.splitlines()
                if ln.startswith("| `ai_square_cooldown`")]
        assert rows, "missing from the Marshal field table"
        assert "anti-oscillation" in rows[0], (
            "the row must say what the field is FOR")
