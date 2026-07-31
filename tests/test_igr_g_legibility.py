"""IGR-G — the two legibility fixes (INGAME_REVIEW_FIXES_SPEC §2 IGR-G).

G1 — the settlement authoring viewport. The shared 720x520 authored rect was
a CEILING for Utils.clamp_centered_panel, so the settlement screen rendered
720x520 on a 2560x1440 monitor, and the relax pass distributed shortfall
proportional to headroom — charging the per-court table (the largest floor,
the primary content) the largest share. Measured before: panel 720x520,
PerCourtScroll 145.24px (~6 rows). After: panel 1160x980, PerCourtScroll at
its full 320 floor with all three courts visible unscrolled.

G2 — map piece stacks. 30px slot spacing against a ~35px visible figure
meant co-located pieces overlapped at EVERY zoom, and 5 name labels
staggered 13px apart over the stack were unreadable. Now: 38px spacing, a
third rank above 4 pieces, and one aggregate label ("Ney +4") above 3
co-located marshals.

The .gd pins below are bounded to their function/arm (the repo's standing
idiom) so deleting the behaviour fails the pin.
"""
import io
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SCENES = REPO / "godot-client" / "project-sovereign" / "scenes"


def _read(path: Path) -> str:
    return io.open(path, encoding="utf-8").read()


def _utils_func_body(name: str) -> str:
    src = _read(SCRIPTS / "utils.gd")
    start = src.index(f"static func {name}")
    rest = src[start:]
    nxt = rest.find("\nstatic func ", 1)
    return rest if nxt == -1 else rest[:nxt]


def _renderer_func_body(name: str) -> str:
    src = _read(SCENES / "map_renderer_base.gd")
    start = src.index(f"func {name}")
    rest = src[start:]
    nxt = rest.find("\nfunc ", 1)
    return rest if nxt == -1 else rest[:nxt]


class TestG1SettlementViewport:
    def test_clamp_reads_the_ceiling_override_meta(self):
        body = _utils_func_body("clamp_centered_panel")
        assert 'has_meta("clamp_ceiling_override")' in body
        # The override RAISES the ceiling; it never shrinks the authored rect
        # (maxf on both axes), and the viewport caps still apply after it.
        assert "maxf(design.x, override.x)" in body
        assert "maxf(design.y, override.y)" in body
        override_at = body.index('has_meta("clamp_ceiling_override")')
        caps_at = body.index("view.x - 24.0")
        assert override_at < caps_at

    def test_settlement_branch_sets_and_others_remove_the_meta(self):
        src = _read(SCRIPTS / "proposal_confirm_popup.gd")
        assert "const SETTLEMENT_CEILING := Vector2(1160, 980)" in src
        # Bounded to the clamp call at the end of show_dialogue: settlement
        # sets, every other dtype removes — the popup instance is shared, so
        # a stale meta would leak the settlement rect into proposal_confirm.
        tail = src[src.index("# IGR-G1: the settlement table gets the document ceiling"):]
        tail = tail[:tail.index("Utils.clamp_centered_panel($PanelContainer)")]
        # Review hardening: BIND each action to its branch by ordering —
        # unordered substring checks passed with the arm bodies swapped
        # (settlement REMOVING the ceiling, everyone else setting it).
        set_branch = tail.index("if is_settlement_table:")
        set_call = tail.index(
            'set_meta("clamp_ceiling_override", SETTLEMENT_CEILING)')
        elif_branch = tail.index("elif ")
        remove_call = tail.index('remove_meta("clamp_ceiling_override")')
        assert set_branch < set_call < elif_branch < remove_call

    def test_the_call_string_pin_survives(self):
        """The ceiling rides a META precisely because the exact call string
        is pinned across every centre-anchored surface by
        test_ui_visual_foundation.py — this asserts we did not break it."""
        src = _read(SCRIPTS / "proposal_confirm_popup.gd")
        assert "Utils.clamp_centered_panel($PanelContainer)" in src

    def test_per_court_scroll_is_tagged_primary_content(self):
        src = _read(SCRIPTS / "proposal_confirm_popup.gd")
        ready = src[src.index("func _ready"):]
        ready = ready[:ready.find("\nfunc ", 1)]
        assert 'per_court_scroll.set_meta("relax_last", true)' in ready

    def test_relax_pass_shrinks_tagged_controls_last(self):
        body = _utils_func_body("_relax_child_minimums")
        # Two-tier giver selection: untagged controls give first; a
        # relax_last control joins only when the untagged tier is exhausted.
        first_pass = body.index('if control.has_meta("relax_last"):\n\t\t\t\tcontinue')
        fallback = body.index('if not control.has_meta("relax_last"):\n\t\t\t\t\tcontinue')
        assert first_pass < fallback
        # The pinned relax properties survive (restore-first, iterate,
        # relaxed_min_y bookkeeping) — asserted in full by
        # test_ui_visual_foundation.py; spot-check the wiring here.
        assert "for _round in range(_RELAX_ROUNDS)" in body
        assert 'set_meta("relaxed_min_y"' in body

    def test_the_authored_scene_floor_is_untouched(self):
        """tests/test_settlement_gate4_leg1_fixes.py pins the literal — this
        mirror keeps the constraint visible from the IGR-G side too."""
        scene = _read(SCENES / "proposal_confirm_popup.tscn")
        chunk = scene.split('[node name="PerCourtScroll"', 1)[1]
        chunk = chunk.split("[node", 1)[0]
        assert "custom_minimum_size = Vector2(0, 320)" in chunk


class TestG2PieceStacks:
    def test_slot_spacing_gives_the_figure_daylight(self):
        src = _read(SCENES / "map_renderer_base.gd")
        m = re.search(r"const WAR_PIECE_SLOT_SPACING: float = (\d+\.\d+)", src)
        assert m, "spacing constant missing"
        spacing = float(m.group(1))
        frame = float(re.search(
            r"const WAR_PIECE_FRAME_PX: float = (\d+\.\d+)", src).group(1))
        visible_figure = frame * 0.55  # the U5 art contract (~35px at 64)
        assert spacing == 38.0
        assert spacing > visible_figure  # the whole point of the change

    def test_three_ranks_above_four_pieces(self):
        body = _renderer_func_body("_marshal_slot_offset_2d")
        assert "if count <= 2:" in body  # pinned flat-line arm survives
        assert "var ranks := 2 if count <= 4 else 3" in body
        assert "var rank := i % ranks" in body
        assert "-float(rank) * WAR_PIECE_RANK_DEPTH" in body
        # Review hardening: pin the rank_count formula VERBATIM — the Python
        # mirror below validates the derivation but never read the .gd, so a
        # drift (e.g. integer division dropping the ceil) was invisible.
        assert ("var rank_count := int(ceil(float(count - rank) / float(ranks)))"
                in body)
        assert "var idx := int(i / float(ranks))" in body

    def test_two_rank_shape_is_numerically_unchanged_for_3_and_4(self):
        """The generalized round-robin must reproduce the old two-rank math
        for counts 3-4 (the U5 sign-off look) — mirrored in Python from the
        .gd formulas, per-index."""
        import math

        def old(i, count, spacing, depth):
            rank = i % 2
            idx = i // 2
            front = math.ceil(count / 2)
            rank_count = front if rank == 0 else count - front
            return ((idx - (rank_count - 1) / 2.0) * spacing,
                    0.0 if rank == 0 else -depth)

        def new(i, count, spacing, depth):
            ranks = 2 if count <= 4 else 3
            rank = i % ranks
            idx = i // ranks
            rank_count = math.ceil((count - rank) / ranks)
            return ((idx - (rank_count - 1) / 2.0) * spacing,
                    -rank * depth)

        for count in (3, 4):
            for i in range(count):
                assert new(i, count, 38.0, 16.0) == old(i, count, 38.0, 16.0)
        # And a 6-stack genuinely uses the third rank.
        ys = {new(i, 6, 38.0, 16.0)[1] for i in range(6)}
        assert ys == {0.0, -16.0, -32.0}

    def test_stack_label_collapses_per_nation_not_per_region(self):
        """Review fix: the region's marshals[] array is MIXED-NATION (the
        backend appends FULL-visibility enemies to the same list), so the
        collapse keys on the marshal's NATION group — 'Ney +4' must never
        count Mack, and Mack must never lose his label to Ney's rank."""
        body = _renderer_func_body("_create_marshal_nodes")
        # The per-nation census, and the per-marshal gate reading it.
        assert "nation_counts[mn] = int(nation_counts.get(mn, 0)) + 1" in body
        assert ("var in_collapsed_group := (pieces_active\n"
                "\t\t\t\tand int(nation_counts.get(nation, 0)) > 3)" in body)
        assert "if not in_collapsed_group:" in body
        # One label per collapsed GROUP, named from that group's own lead.
        assert 'var stack_text := "%s +%d" % [lead_name, group_size - 1]' in body
        assert "if group_size <= 3:" in body
        # A second collapsed nation stacks a row higher, never overprinting.
        assert "float(stack_row) * 13.0" in body

    def test_hover_hitboxes_survive_the_collapse(self):
        """Review hardening: the hitbox append must sit at LOOP level (two
        tabs), never inside the label gate (three tabs) — a bare containment
        check passed with the append indented into the gate, which would
        have deleted every 4+-stack's hover tooltips."""
        body = _renderer_func_body("_create_marshal_nodes")
        assert "\n\t\tmarshal_hitboxes.append({" in body
        assert "\n\t\t\tmarshal_hitboxes.append({" not in body

    def test_stack_label_clears_the_rear_rank(self):
        body = _renderer_func_body("_create_marshal_nodes")
        assert "var rear_ranks := 1 if marshals.size() <= 4 else 2" in body
        assert "float(rear_ranks) * WAR_PIECE_RANK_DEPTH" in body

    def test_legacy_icon_branch_is_untouched(self):
        """The bitmap-mode gate: the legacy square-icon world keeps its
        per-marshal labels (the collapse requires pieces_active)."""
        body = _renderer_func_body("_create_marshal_nodes")
        assert "in_collapsed_group := (pieces_active" in body
        assert "-15.0 - i * 14.0" in body  # legacy stagger, byte-unchanged
