"""Row NP — the promise audit (August 15, 2026).

Every commitment in `docs/NAPOLEON_SPEC.md` and in the 13 NP commit
messages, extracted and verified against code. Record =
`docs/audits/NP_PROMISE_AUDIT_2026_08_15.md`; landing record =
NAPOLEON_SPEC.md §15.9.

These pins cover the defects that audit found. Each one was reproduced at
runtime before the fix was written, and each asserts an APPLIED value or a
RENDERED string — never that a constant exists.
"""

import pytest

from backend.ai.parser_eval import build_llm_game_state, build_world
from backend.commands.executor import CommandExecutor
from backend.commands.parser import (
    CommandParser,
    _SOVEREIGN_ORDER_VERBS,
    normalize_sovereign_address,
)
from backend.game_logic import dispatch as D
from backend.game_logic.diplomacy import (
    displayed_dp_ceiling,
    sovereign_seat_bonus,
)
from backend.models.authority import sovereign_aura_strength
from backend.models.marshal import Marshal


def CE():
    return CommandExecutor()._combat


@pytest.fixture()
def europe():
    return build_world("1805")


# ════════════════════════════════════════════════════════════════════════
# A1 — the aura decays on EVERY path, not only the ordinary attack
# ════════════════════════════════════════════════════════════════════════

class TestTheAuraDimsEverywhere:
    """§15.4 claims `sovereign_aura_strength` is "the single source for
    both" the aura and the fear. It moved the participant stamp and the
    fear and left `_calculate_coordination_context` on a flat 1.0 — and
    that producer is the LAST word on the two paths that never reach the
    participant stamp: the garrison assault and the cavalry charge.
    Measured with the myth wholly broken the Emperor still stormed a
    capital at the full +10%.
    """

    def _stack(self, world, authority):
        nap, ney = world.marshals["Napoleon"], world.marshals["Ney"]
        nap.location = ney.location = "Lorraine"
        world._build_marshal_index()
        world.authority_tracker.authority = authority
        return nap, ney

    @pytest.mark.parametrize("authority", [100, 57, 30])
    def test_context_stamp_is_the_aura_strength_not_a_flag(
            self, europe, authority):
        nap, ney = self._stack(europe, authority)
        expected = sovereign_aura_strength(europe, "France")
        CE()._calculate_coordination_context(nap, europe)
        assert nap.sovereign_presence == pytest.approx(expected)
        assert ney.sovereign_presence == pytest.approx(expected)

    def test_a_broken_aura_grants_nothing_on_the_charge_path(self, europe):
        """The value that broke: at grip 0.0 the modifier must carry no
        presence term at all."""
        nap, _ = self._stack(europe, 30)
        assert sovereign_aura_strength(europe, "France") == 0.0
        CE()._calculate_coordination_context(nap, europe)
        broken = nap.get_attack_modifier(1.0, consume=False)

        full = build_world("1805")
        nap_f, _ = self._stack(full, 100)
        CE()._calculate_coordination_context(nap_f, full)
        intact = nap_f.get_attack_modifier(1.0, consume=False)

        assert intact > broken, "the aura never dimmed on this path"
        assert intact == pytest.approx(
            broken * (1.0 + Marshal.SOVEREIGN_PRESENCE_ATTACK))

    def test_full_authority_is_byte_identical_to_the_old_flag(self, europe):
        """The fix must not move anything while the throne stands."""
        nap, ney = self._stack(europe, 100)
        CE()._calculate_coordination_context(nap, europe)
        assert nap.sovereign_presence == 1.0
        assert ney.sovereign_presence == 1.0

    def test_no_sovereign_still_stamps_nothing(self, europe):
        del europe.marshals["Napoleon"]
        europe._build_marshal_index()
        ney = europe.marshals["Ney"]
        CE()._calculate_coordination_context(ney, europe)
        assert getattr(ney, "sovereign_presence", 0.0) == 0.0


class TestTheMusterQuotesTheAppliedNumber:
    """`presence_note` hardcoded +10% under a comment reading
    "Percentage derives from the consumed constant... Shown = applied"."""

    def _preview(self, world, authority):
        nap, ney = world.marshals["Napoleon"], world.marshals["Ney"]
        nap.location = ney.location = "Lorraine"
        world._build_marshal_index()
        world.authority_tracker.authority = authority
        mack = world.marshals["Mack"]
        return CE()._build_muster_preview(ney, mack, world, {"world": world})

    def test_note_scales_with_the_aura(self, europe):
        full = self._preview(europe, 100).get("presence_note") or ""
        assert "+10%" in full, full

        dim_world = build_world("1805")
        dim = self._preview(dim_world, 57).get("presence_note") or ""
        assert dim, "the note vanished instead of dimming"
        assert "+10%" not in dim, dim
        assert "star dims" in dim, dim

    def test_a_broken_aura_promises_nothing(self, europe):
        assert not self._preview(europe, 30).get("presence_note")


# ════════════════════════════════════════════════════════════════════════
# A2 — a captured sovereign is never announced as destroyed
# ════════════════════════════════════════════════════════════════════════

class TestTheFallClause:
    """`destroy_marshal` returns False when it converts a sovereign to
    CAPTURE (§7.1). The CHARGE copy gated its message on that return; the
    battle and auto-bombardment copies did not.
    """

    def test_a_removed_marshal_is_destroyed(self, europe):
        ney = europe.marshals["Ney"]
        assert "destroyed" in CE()._fall_clause(europe, ney, True)

    def test_a_taken_sovereign_is_taken_not_destroyed(self, europe):
        nap = europe.marshals["Napoleon"]
        europe.capture_marshal(nap, "Austria", context="probe")
        clause = CE()._fall_clause(europe, nap, False)
        assert "destroyed" not in clause.lower(), clause
        assert "taken" in clause.lower(), clause
        assert "Austria" in clause, clause
        assert "the Emperor" in clause, clause

    def test_the_ordinary_survivor_says_nothing(self, europe):
        assert CE()._fall_clause(europe, europe.marshals["Ney"], False) == ""

    def test_the_destruction_sentences_have_exactly_one_home_each(self):
        """Structural: the two copies that shipped the bug composed their
        sentence ahead of `destroy_marshal` and printed it regardless of
        the return. A future copy written that way re-opens the defect,
        so each destruction phrase gets exactly one site — the shared
        clause, or an arm explicitly gated on the removal."""
        import inspect

        from backend.commands import combat_executor as CX
        src = inspect.getsource(CX)

        assert src.count("'s army is destroyed!") == 1, (
            "the army-destroyed sentence has more than one home — route "
            "every copy through _fall_clause")
        assert src.count("The preparatory bombardment destroyed ") == 1
        # ...and that one site is inside the removal-gated arm.
        assert "if auto_kill_removed:" in src
        assert "he was taken on the field" in src, (
            "the auto-bombardment path lost its captured-sovereign arm")

        # the shared clause is genuinely shared
        assert src.count("self._fall_clause(") >= 1
        assert src.count("_fall_clause") >= 3  # def + docstring ref + call


# ════════════════════════════════════════════════════════════════════════
# A3 — the self-marker arm obeys gate (b), and no arm leaks the marker
# ════════════════════════════════════════════════════════════════════════

class TestTheSelfMarkerArm:
    @pytest.mark.parametrize("text", [
        "I will offer an alliance to Prussia myself",
        "I will negotiate with Austria myself",
        "review the terms myself",
        "I want to see the treasury myself",
        "I will handle this myself",
    ])
    def test_no_verb_no_rewrite(self, text):
        assert normalize_sovereign_address(text, "Napoleon") == text

    @pytest.mark.parametrize("text", [
        "march to Belgium myself",
        "attack Wellington in person",
        "I will march to Belgium myself",
        "the Emperor will march to Belgium myself",
        "Davout, march to Belgium myself",
    ])
    def test_the_marker_never_survives(self, text):
        out = normalize_sovereign_address(text, "Napoleon").lower()
        assert "myself" not in out, text
        assert "in person" not in out, text

    def test_the_verb_set_is_the_one_source_for_all_three_arms(self):
        """The Emperor-lead arm shipped with no verb gate; the self-marker
        arm shipped with no verb gate. Both now read the same set, so they
        cannot drift apart a third time."""
        import backend.commands.parser as P
        for pattern in (P._SOVEREIGN_EMPEROR_LEAD_RE,
                        P._SOVEREIGN_FIRST_PERSON_RE,
                        P._SOVEREIGN_BODY_HAS_VERB_RE):
            assert _SOVEREIGN_ORDER_VERBS in pattern.pattern

    def test_a_marshal_addressed_order_keeps_its_marshal(self, europe):
        parser = CommandParser()
        result = parser.parse("Ney, march to Swabia myself",
                              build_llm_game_state(europe), world=europe)
        assert result["command"]["marshal"] == "Ney"
        assert result["command"]["target"] == "Swabia"


# ════════════════════════════════════════════════════════════════════════
# A4 — the Seat: one beat per departure, and an honest denominator
# ════════════════════════════════════════════════════════════════════════

class TestTheSeat:
    def test_the_shown_ceiling_includes_the_seat(self, europe):
        assert sovereign_seat_bonus(europe, "France") == 1
        europe.advance_turn()
        assert europe.diplomatic_points == displayed_dp_ceiling(europe), (
            "the HUD read 'DP: 6/5' — a number over its own maximum")

    def test_the_ceiling_is_bare_without_a_sovereign(self, europe):
        base = int(europe.max_diplomatic_points)
        del europe.marshals["Napoleon"]
        europe._build_marshal_index()
        assert displayed_dp_ceiling(europe) == base

    def test_the_ceiling_falls_when_he_rides_out(self, europe):
        base = int(europe.max_diplomatic_points)
        europe.marshals["Napoleon"].location = "Lorraine"
        europe._build_marshal_index()
        assert displayed_dp_ceiling(europe) == base

    def test_the_field_beat_fires_once_across_every_live_war(self, europe):
        """It used to `break` after the first unnoted war, so a court in
        two live war instances got the same beat on consecutive turns
        while the Emperor simply stayed afield."""
        europe.marshals["Napoleon"].location = "Lorraine"
        europe._build_marshal_index()
        # a second live war instance France is a party to
        live = [w for w in europe.war_instances.values()
                if w.get("ended_turn") is None
                and "France" in (w.get("active_participants") or [])]
        assert live, "fixture has no live French war"
        second = dict(live[0])
        second["emperor_field_noted"] = False
        europe.war_instances["war_probe"] = second

        fired = []
        for _ in range(3):
            europe.advance_turn()
            if "taken the field" in str(D.build_morning_dispatch(europe)):
                fired.append(europe.current_turn)
        assert len(fired) == 1, (
            f"the departure beat fired on turns {fired} — once per war "
            f"instance instead of once per departure")


# ════════════════════════════════════════════════════════════════════════
# B — the fleet's findings (the 71-agent extract -> refute pass)
# ════════════════════════════════════════════════════════════════════════

class TestTheShadowIsAnIdentityNotAMagnitude:
    """§15.4 made the aura DECAY with imperial grip and floor at 0.0. The
    Shadow's booleans were derived as ``_atk_presence > 0.0``, so a
    magnitude change silently switched a separate mechanic OFF: in a
    collapsing empire marshals at the Emperor's side banked FULL glory
    again. §15.4 changed the aura's size; it never said the Shadow lifts.
    """

    def _shadowed_glory(self, authority):
        from backend.game_logic import jealousy as J
        world = build_world("1805")
        world.authority_tracker.authority = authority
        nap, ney = world.marshals["Napoleon"], world.marshals["Ney"]
        mack = world.marshals["Mack"]
        nap.location = ney.location = mack.location = "Swabia"
        world._build_marshal_index()
        ney.glory_events = []
        J.record_battle_glory(
            world, ney, mack, True, False, 1000, 5000, conquered=False,
            pre_attacker_strength=30000, pre_defender_strength=20000,
            attacker_participants=[ney, nap], defender_participants=[mack],
            attacker_shadow=True, defender_shadow=False)
        return sum(int(e.get("points", 0)) for e in (ney.glory_events or []))

    def _plain_glory(self):
        from backend.game_logic import jealousy as J
        world = build_world("1805")
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        ney.location = mack.location = "Swabia"
        world._build_marshal_index()
        ney.glory_events = []
        J.record_battle_glory(
            world, ney, mack, True, False, 1000, 5000, conquered=False,
            pre_attacker_strength=30000, pre_defender_strength=20000,
            attacker_participants=[ney], defender_participants=[mack],
            attacker_shadow=False, defender_shadow=False)
        return sum(int(e.get("points", 0)) for e in (ney.glory_events or []))

    def test_the_shadow_is_not_vacuous(self):
        assert self._shadowed_glory(100) < self._plain_glory()

    def test_the_shadow_holds_when_the_aura_is_broken(self):
        from backend.models.authority import sovereign_aura_strength
        broken = build_world("1805")
        broken.authority_tracker.authority = 30
        assert sovereign_aura_strength(broken, "France") == 0.0
        assert self._shadowed_glory(30) == self._shadowed_glory(100), (
            "the Shadow lifted when the aura broke -- a collapsing empire "
            "let marshals bank full glory at the Emperor's own side")

    def test_the_side_verdicts_are_identity_not_magnitude(self):
        """Structural: the booleans must not be derived from the float."""
        import inspect
        from backend.commands import combat_executor as CX
        src = inspect.getsource(CX)
        assert "_atk_sovereign = _atk_presence > 0.0" not in src
        assert "_side_sovereign(atk_participants) is not None" in src


class TestTheChargeSharesOneAudience:
    """The glorious charge was the ONE glory-producing path without the
    NP-V roster override: the aura was stamped at the charger's ORIGIN
    while the Shadow fell back to a participant scan at the TARGET, so a
    cavalryman charging out of the Emperor's headquarters carried the
    Presence AND banked full glory -- the strictly-dominant stacking the
    gate rejected option (c) to avoid.
    """

    def _charge(self, emperor_at, monkeypatch=None):
        """Returns (aura_row_rendered, shadow_verdict_passed_to_glory).

        The battle itself is diced and each Emperor position takes a
        different RNG path, so the GLORY FIGURE is not comparable across
        arms — the contract is not "the number is N", it is "the charge
        hands the glory step the same roster verdict the aura was
        stamped from". That is what this spies on (the project's
        call-site-spy idiom), and it is exactly what was missing: the
        charge passed no verdict at all, so the glory step fell back to a
        participant scan at a DIFFERENT province.
        """
        seen = {}
        if monkeypatch is not None:
            from backend.game_logic import jealousy as J
            real = J.record_battle_glory

            def spy(*a, **kw):
                seen["attacker_shadow"] = kw.get("attacker_shadow")
                seen["defender_shadow"] = kw.get("defender_shadow")
                return real(*a, **kw)

            monkeypatch.setattr(J, "record_battle_glory", spy)
        w = build_world("1805")
        mur, nap = w.marshals["Murat"], w.marshals["Napoleon"]
        mack = w.marshals["Mack"]
        mur.location = "Lorraine"
        mur.recklessness = 4
        mur.strength = 30000
        mack.location = "Swabia"
        mack.strength = 25000
        nap.location = emperor_at
        mur.glory_events = []
        w._build_marshal_index()
        result = CE()._execute_charge(
            {"marshal": "Murat", "action": "charge", "target": "Mack"},
            {"world": w})
        mods = ((result.get("battle_report") or {})
                .get("modifier_breakdown") or {}).get("attacker") or []
        aura = any("Emperor" in str(m.get("label", "")) for m in mods)
        return aura, seen.get("attacker_shadow")

    def test_charging_out_of_his_headquarters_earns_neither(self, monkeypatch):
        """The exploit that was live: aura YES + full glory."""
        aura, shadow = self._charge("Lorraine", monkeypatch)
        assert not aura, (
            "the charger carried the Presence out of a province the "
            "Emperor never left")
        assert shadow is False, (
            "and he must keep his full laurels for it — the verdict was "
            f"{shadow!r}")

    def test_charging_into_his_field_earns_both(self, monkeypatch):
        """The mirror that was live: aura no + halved glory."""
        aura, shadow = self._charge("Swabia", monkeypatch)
        assert aura, "the Emperor stood on the contested field"
        assert shadow is True, "and the Shadow must fall across it"

    def test_an_uninvolved_emperor_changes_nothing(self, monkeypatch):
        aura, shadow = self._charge("Paris", monkeypatch)
        assert not aura
        assert shadow is False

    def test_the_verdict_is_actually_passed(self, monkeypatch):
        """Non-vacuity: before the fix the charge passed NO verdict, so
        `attacker_shadow` arrived as None and the glory step silently fell
        back to a participant scan at the wrong province."""
        _, shadow = self._charge("Swabia", monkeypatch)
        assert shadow is not None, (
            "the charge passes no roster verdict to record_battle_glory")


class TestTheEmperorHoldsWhenToldToHold:
    """A sovereign on HOLD fell into the arm labelled ``else: # aggressive``
    and SALLIED OUT unordered -- reproduced through the real player path,
    the Guard down 10,000 -> 9,737 in a battle nobody ordered, on the one
    verb whose whole meaning is "stay put"."""

    def _hold(self, who):
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.models.marshal import StrategicOrder
        w = build_world("1805")
        m, mack = w.marshals[who], w.marshals["Mack"]
        m.location = "Paris"
        mack.location = "Berry"
        mack.strength = 2000
        w._build_marshal_index()
        m.strategic_order = StrategicOrder(
            "HOLD", "Paris", "region", 1, original_command="hold Paris")
        before = m.strength
        out = StrategicOrderProcessor(CommandExecutor())._execute_hold(
            m, w, {"world": w})
        return out, before, m.strength, m.location

    def test_the_sovereign_holds(self):
        out, before, after, where = self._hold("Napoleon")
        assert out["action"] != "sally"
        assert after == before, "the Emperor fought a battle nobody ordered"
        assert where == "Paris"

    def test_an_aggressive_marshal_still_sallies(self):
        """Control -- the arm must not have been widened into everyone."""
        out, before, after, _ = self._hold("Ney")
        assert out["action"] == "sally"
        assert after < before


class TestTheAttritionSweepDoesNotKillHim:
    def test_a_starved_sovereign_is_taken_not_eliminated(self, europe):
        nap = europe.marshals["Napoleon"]
        nap.strength = 0
        europe._build_marshal_index()
        events = europe.process_supply_attrition()
        assert "Napoleon" in europe.marshals
        assert nap.captured_by
        assert "Napoleon" not in europe.fallen_marshals
        destroyed = [e for e in events
                     if e.get("type") == "marshal_destroyed"
                     and e.get("marshal") == "Napoleon"]
        assert not destroyed, (
            f"the sweep announced the Emperor's death: "
            f"{[e.get('message') for e in destroyed]}")
        taken = [e for e in events if e.get("marshal") == "Napoleon"]
        assert taken and "prisoner" in taken[0]["message"], taken


class TestTheReportNeverPrintsAZeroBonus:
    """Grip is an int over a span of 55, so the smallest non-zero aura is
    1/55 -- and grip 31-32 rendered a bonus row reading "+0%". §15.4
    promises "+10%" becomes "+9%" becomes NOTHING."""

    @pytest.mark.parametrize("presence", [1 / 55.0, 2 / 55.0])
    def test_no_zero_percent_row(self, europe, presence):
        from backend.game_logic.battle_report import (
            snapshot_attacker_modifiers,
            snapshot_defender_modifiers,
        )
        atk, deff = europe.marshals["Ney"], europe.marshals["Mack"]
        atk.sovereign_presence = presence
        deff.sovereign_presence = presence
        for rows in (snapshot_attacker_modifiers(
                         atk, deff, "plains", 0.0, 0, False),
                     snapshot_defender_modifiers(deff, atk, "plains", 0.0)):
            emperor = [r for r in rows if "Emperor" in str(r.get("label"))]
            assert not any(r["value"] == 0 for r in emperor), emperor

    def test_a_real_fraction_still_renders(self, europe):
        from backend.game_logic.battle_report import (
            snapshot_attacker_modifiers,
        )
        atk, deff = europe.marshals["Ney"], europe.marshals["Mack"]
        atk.sovereign_presence = 0.6
        rows = snapshot_attacker_modifiers(atk, deff, "plains", 0.0, 0, False)
        assert any("Emperor" in str(r.get("label")) and r["value"] == 6
                   for r in rows), rows


class TestTheBeltsSixOneNamed:
    """§6.1's cut-set table names guards that were never written — they
    held by cascade off other exemptions. Named belts are the difference
    between "safe" and "safe on purpose"."""

    def test_the_channel_refuses_a_sovereign_petitioner(self, europe):
        """§2 pillar 1 held only by accident: the §6 confrontation needs
        `jealous_of`, Fontainebleau an eroding expectation, ESP-2 an
        expectation >= 160 — but the §6b RIVALRY producer has no such
        gate, and §6.4 deliberately keeps the sovereign in the Win/Loss
        relationship formula."""
        from backend.game_logic import jealousy as J
        blocked = J._push_petition(europe, {
            "kind": "rivalry_confrontation",
            "title": "A RIVALRY AMONG THE MARSHALS",
            "marshal": "Napoleon",
            "options": [],
        })
        assert blocked == J.PETITION_BLOCKED
        assert getattr(europe, "pending_marshal_petition", None) is None

    def test_an_ordinary_marshal_still_petitions(self, europe):
        """Control — the belt must not have closed the channel."""
        from backend.game_logic import jealousy as J
        assert J._push_petition(europe, {
            "kind": "rivalry_confrontation", "title": "T",
            "marshal": "Ney", "options": [],
        }) == J.PETITION_QUEUED

    def test_the_sovereign_cannot_be_made_autonomous(self, europe):
        """§6.1 row 9 names an "autonomy gate"; only the trust freeze
        landed, and this debug arm could break it while its own sibling
        `dismiss` DID get the guard."""
        ex = CommandExecutor()
        out = ex.execute({"success": True, "command": {
            "action": "cheat", "cheat_type": "set_autonomy",
            "marshal": "Napoleon", "value": "5",
        }}, {"world": europe, "debug_mode": True})
        assert europe.marshals["Napoleon"].autonomous is False, out

    def test_the_restlessness_loop_skips_him(self, europe):
        """§6.1 cut-set row 4 names a belt in the restlessness loop."""
        import inspect
        from backend.game_logic import jealousy as J
        src = inspect.getsource(J.process_turn)
        assert 'is_sovereign' in src, (
            "the restlessness loop has no named sovereign belt")


class TestThePetitionBeatReachesTheDispatch:
    """NP-3's commit says the beat is carried by "the modal + dispatch line
    + response message". The event was appended to the turn events and the
    narration cap already exempted it — but `shadow_petition` was never
    added to `_DISPATCH_EVENT_TYPES`, so `_build_turn_events` dropped it at
    the whitelist and the dispatch line never existed."""

    def test_shadow_petition_is_whitelisted(self):
        assert "shadow_petition" in D._DISPATCH_EVENT_TYPES

    def test_the_beat_renders(self, europe):
        rendered = D._build_turn_events([{
            "type": "shadow_petition",
            "message": "Ney seeks an audience, Sire.",
            "nation": europe.player_nation,
            "marshal": "Ney",
        }], europe.player_nation)
        assert len(rendered) == 1, rendered
        assert rendered[0]["severity"] == "warning"
        assert "seeks an audience" in rendered[0]["message"]


class TestTheSovereignIsNeverAskedToConfirm:
    """RULED by the user, Aug 15 2026 (NAPOLEON_SPEC §15.9a): the sovereign
    gets NO attack-confirm, even on genuinely bad odds. He falls out today
    because `sovereign` is simply absent from MUSTER_GATE_PERSONALITIES —
    the kind of silence a later reader "fixes" — so the ruling is pinned
    rather than left to the omission.
    """

    def test_the_gate_never_arms_for_him(self, europe):
        from backend.commands.objection_v2 import (
            MUSTER_GATE_BAND, muster_gate_arms,
        )
        nap = europe.marshals["Napoleon"]
        assert muster_gate_arms(nap, MUSTER_GATE_BAND) is False

    def test_a_cautious_marshal_still_arms_it(self, europe):
        """Control — the ruling is about HIM, not about the gate."""
        from backend.commands.objection_v2 import (
            MUSTER_GATE_BAND, MUSTER_GATE_PERSONALITIES, muster_gate_arms,
        )
        cautious = next(m for m in europe.marshals.values()
                        if getattr(m, "personality", None)
                        in MUSTER_GATE_PERSONALITIES)
        assert muster_gate_arms(cautious, MUSTER_GATE_BAND) is True

    def test_sovereign_is_not_in_the_gate_set(self):
        from backend.commands.objection_v2 import MUSTER_GATE_PERSONALITIES
        assert "sovereign" not in MUSTER_GATE_PERSONALITIES, (
            "the sovereign's missing attack-confirm is a RULING "
            "(NAPOLEON_SPEC §15.9a), not an oversight to be corrected")
