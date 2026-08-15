"""PC-2 / PC-3 / PC-7 — the composition and narration fixes from the
quiet-France played campaign (August 3, 2026).

Measured over 42 played turns on the shipped 1805 board, France passive
after turn 5:

* **30** verbatim duplicate message lines inside a single enemy phase across
  41 phases — 23 of them one Bavarian marshal holding position twice. `wait`
  costs 0 AP so the AI loop re-selects the same marshal, and the only brake
  is a `_consecutive_waits >= 2` latch whose own comment reads *"2 waits =
  nothing useful to do"*: the design requires a **second** wasted no-op to
  detect idleness, and that second no-op ships to the client.
* **41** fortify→unfortify / wait×2 thrash occurrences. The existing guards
  (`_unfortified_this_turn`, `ai_refortify_cooldown`) are one-directional and
  block only unfortify→re-fortify; PT-F6 is square-scoped and does not reach
  fortify.
* the dispatch headline led with `estate_eroding` on **21 of 41** turns
  (51%), longest run **seven consecutive**, the identical Davout sentence
  **12 times** with a byte-identical Berthier note — while the treasury held
  39,000g and the remedy cost 180g/turn.

Both composition fixes live at the VIEW layer, by PT-D4's precedent. That is
deliberate and measured: the producer-side fortify latch was built, and it
diverges `BASELINE_SERIES` at index 2 *and* collapses the AI-V §4.7 variance
signature. Attribution was verified by experiment (disabling the latch
reproduces both pins byte-identically), so the mechanical waste stays open as
a balance row rather than being fixed by a narration change.
"""
import pytest

from backend.game_logic import dispatch as dispatch_mod
from backend.main import _collapse_enemy_move_chains


def _entry(marshal, action, message=None):
    return {"ai_action": {"marshal": marshal, "action": action},
            "message": message or f"{marshal} {action}s."}


def _phase(*entries):
    return {"nations": {"Austria": {"actions": list(entries)}},
            "total_actions": len(entries), "summary": []}


def _collapse(*entries):
    return _collapse_enemy_move_chains(_phase(*entries), None)


# ── PC-2: the repeated no-op ───────────────────────────────────────────────

def test_repeated_wait_is_shown_once():
    held = "Deroy holds position at Swabia, awaiting further orders."
    out = _collapse(_entry("Deroy", "wait", held), _entry("Deroy", "wait", held))
    assert out["total_actions"] == 1
    assert out["summary"] == ["Deroy: wait"]


def test_waits_in_different_places_are_both_kept():
    """Falsifiable counter-example: the dedupe keys on the rendered line, so
    a marshal who waits somewhere new is still news."""
    out = _collapse(_entry("Deroy", "wait", "Deroy holds at Swabia."),
                    _entry("Deroy", "wait", "Deroy holds at Tyrol."))
    assert out["total_actions"] == 2


def test_two_marshals_waiting_are_both_kept():
    out = _collapse(_entry("Deroy", "wait", "Deroy holds."),
                    _entry("Brunswick", "wait", "Brunswick holds."))
    assert out["total_actions"] == 2


# ── PC-3: the fortify he undoes in the same breath ─────────────────────────

def test_fortify_undone_in_the_same_phase_shows_neither():
    out = _collapse(_entry("Brunswick", "fortify"), _entry("Brunswick", "unfortify"))
    assert out["total_actions"] == 0, "a net-zero posture pair is not news"


def test_thrash_is_collapsed_across_another_marshals_entry():
    """Other marshals interleave freely; only his OWN next action counts."""
    out = _collapse(_entry("Brunswick", "fortify"),
                    _entry("Deroy", "attack"),
                    _entry("Brunswick", "unfortify"))
    assert out["summary"] == ["Deroy: attack"]


def test_a_fortify_he_keeps_is_still_reported():
    out = _collapse(_entry("Brunswick", "fortify"), _entry("Deroy", "attack"))
    assert out["summary"] == ["Brunswick: fortify", "Deroy: attack"]


def test_fortify_followed_by_his_own_other_action_is_reported():
    """His next act being something else means the fortify stood — keep it."""
    out = _collapse(_entry("Brunswick", "fortify"), _entry("Brunswick", "attack"))
    assert out["total_actions"] == 2


def test_a_lone_unfortify_is_still_reported():
    """Unfortifying something he dug into on a PREVIOUS turn is real news."""
    out = _collapse(_entry("Brunswick", "unfortify"))
    assert out["summary"] == ["Brunswick: unfortify"]


# ── PC-7: the standing-class headline ──────────────────────────────────────

class _Memo:
    """Minimal stand-in for the serialized memory."""

    def __init__(self, cls="", identity="", streak=0):
        self.headline_lead_memory = (
            {"class": cls, "identity": identity, "streak": streak}
            if cls else {})


def test_standing_classes_are_declared():
    assert "estate_eroding" in dispatch_mod.STANDING_HEADLINE_CLASSES
    assert "enemy_on_our_soil" in dispatch_mod.STANDING_HEADLINE_CLASSES
    assert dispatch_mod.STANDING_LEAD_MAX >= 1


def test_event_classes_are_not_standing():
    """The cooldown must never touch one-off events — a province falling
    twice in three turns is two pieces of news, not a stuck record."""
    for cls in ("home_captured", "marshal_captured", "own_mauled",
                "region_lost", "europe_congress"):
        assert cls not in dispatch_mod.STANDING_HEADLINE_CLASSES


def test_every_standing_class_has_escalation_copy():
    """A standing class that keeps the lead because it is genuinely the only
    news must have something NEW to say; otherwise the fix does nothing for
    the seven-turn sole-candidate run that motivated it."""
    for cls in dispatch_mod.STANDING_HEADLINE_CLASSES:
        variants = dispatch_mod._STANDING_ESCALATION.get(cls)
        assert variants, f"{cls} has no escalation copy"
        for text in variants:
            assert "{turns}" in text, f"{cls} variant never says how long"
        assert len(set(variants)) == len(variants), f"{cls} repeats itself"


def _placeholders(text: str) -> set:
    import string
    return {name for _lit, name, _spec, _conv
            in string.Formatter().parse(text) if name}


def test_escalation_copy_is_formattable():
    """Every escalation variant must be renderable from the fields its OWN
    class supplies, plus the two the selector always injects.

    Pin CONSCIOUSLY widened August 4, 2026 (econ spec review §6): the ladder
    used to be able to substitute only {marshal} and {turns}, which silently
    bounded what a standing class was allowed to say as it escalated — and
    `levy_open` needs to name the headroom and the price, which is the whole
    point of it. `_add` now carries the template's own arguments onto the
    candidate. Asserting AGAINST the base template's placeholder set is
    stronger than the old fixed-kwargs render: it catches a typo in either
    direction, and it fails if a variant invents a field the class cannot
    supply.
    """
    for cls, variants in dispatch_mod._STANDING_ESCALATION.items():
        base = dispatch_mod._HEADLINE_TEMPLATES[cls]
        allowed = _placeholders(base) | {"marshal", "turns"}
        if cls == "supply_strain":
            # PC15-12: the candidate builder supplies BOTH agreement verbs
            # ({stand}/{have}); the base template uses only {stand}, so the
            # base-placeholder proxy under-approximates this class's own
            # field set.
            allowed |= {"have", "stand"}
        for text in variants:
            used = _placeholders(text)
            assert used <= allowed, (
                f"{cls} escalation uses {sorted(used - allowed)}, which the "
                f"class's own template never supplies")
            rendered = text.format(**{name: "X" for name in used})
            assert "{" not in rendered, f"{cls} left a placeholder unfilled"
            assert rendered.startswith("Sire"), f"{cls} breaks Berthier's register"


@pytest.mark.parametrize("streak,expected_class", [
    (0, "estate_eroding"),                     # first lead — takes it
    (1, "estate_eroding"),                     # still inside the allowance
    (dispatch_mod.STANDING_LEAD_MAX, "europe_congress"),      # must yield now
    (dispatch_mod.STANDING_LEAD_MAX + 3, "europe_congress"),  # and stay yielded
])
def test_standing_class_yields_the_lead_to_lesser_news(streak, expected_class):
    """The whole point, and the real quiet-turn shape: the standing crisis
    OUTWEIGHS the only other news (55 vs 48), so weight alone would let it
    monopolise the top line forever. Once it has had its turns, Europe's
    news leads instead."""
    world = _Memo("estate_eroding", "estate_eroding:Davout", streak)
    candidates = [
        {"class": "estate_eroding", "weight": 55, "identity": "estate_eroding:Davout",
         "text": "Sire — Marshal Davout's household goes unpaid."},
        {"class": "europe_congress", "weight": 48, "identity": "europe_congress",
         "text": "Sire — Austria and Bavaria have made peace without us."},
    ]
    head = _pick(world, candidates)
    assert head["class"] == expected_class


def test_a_yielded_standing_crisis_is_demoted_not_deleted():
    """CREATIVE_AUDIT_2026_07_19 §308: 'demoted to a sub-beat (never
    suppressed)'. Seven turns of silence would be worse than repetition."""
    world = _Memo("estate_eroding", "estate_eroding:Davout",
                  dispatch_mod.STANDING_LEAD_MAX)
    candidates = [
        {"class": "estate_eroding", "weight": 55, "identity": "estate_eroding:Davout",
         "text": "Sire — Marshal Davout's household goes unpaid."},
        {"class": "europe_congress", "weight": 48, "identity": "europe_congress",
         "text": "Sire — Austria and Bavaria have made peace without us."},
    ]
    head = _pick(world, candidates)
    # CA9-N9 (pin re-blessed): the crisis is still reported in the
    # sub-beat, which is the claim — but it is no longer reported in the
    # SAME WORDS. The escalation bank now applies to a standing candidate
    # wherever it lands, not only when it is the sole news, because a
    # demoted crisis repeating verbatim in the sub-beat slot is exactly
    # what N9 measured (the Tyrol supply line, six consecutive
    # dispatches). Pin the subject and the fact, not the frozen phrase.
    beats = " ".join(head["sub_beats"])
    assert "Davout" in beats, beats
    assert ("unpaid" in beats or "unrewarded" in beats), beats
    assert head["class"] != "estate_eroding", "it should have yielded"


def test_sole_standing_crisis_keeps_the_lead_but_changes_its_words():
    """The pinned rule (test_headline_keeps_its_lead_when_it_is_the_only_news)
    says a lone crisis is never suppressed. It still leads — but on turn N of
    the same complaint it must not be the same sentence."""
    base = {"class": "estate_eroding", "weight": 55,
            "identity": "estate_eroding:Davout",
            "text": "Sire — Marshal Davout's household goes unpaid."}
    fresh = _pick(_Memo(), [dict(base)])
    stale = _pick(_Memo("estate_eroding", "estate_eroding:Davout",
                        dispatch_mod.STANDING_LEAD_MAX + 1), [dict(base)])
    assert fresh["class"] == stale["class"] == "estate_eroding"
    assert stale["text"] != fresh["text"], (
        "a seven-turn run still reads as one frozen sentence")
    assert "Davout" in stale["text"]


def test_a_different_marshal_resets_the_streak():
    """Identity, not just class: Ney's grievance is new news even if Davout's
    was old news."""
    world = _Memo("estate_eroding", "estate_eroding:Davout",
                  dispatch_mod.STANDING_LEAD_MAX + 2)
    head = _pick(world, [
        {"class": "estate_eroding", "weight": 55, "identity": "estate_eroding:Ney",
         "text": "Sire — Marshal Ney's household goes unpaid."},
        {"class": "europe_congress", "weight": 48, "identity": "europe_congress",
         "text": "Sire — Austria and Bavaria have made peace without us."},
    ])
    assert head["class"] == "estate_eroding"
    assert world.headline_lead_memory["streak"] == 1


def test_memory_survives_a_quiet_turn():
    """The memory is its own serialized field precisely so a candidate-free
    turn cannot wipe the cooldown — the quiet turns are what a passive
    campaign is made of."""
    from backend.models.world_state import WorldState
    world = WorldState()
    world.headline_lead_memory = {"class": "estate_eroding",
                                  "identity": "estate_eroding:Davout",
                                  "streak": 4}
    restored = WorldState.from_dict(world.to_dict())
    assert restored.headline_lead_memory["streak"] == 4
    assert restored.headline_lead_memory["identity"] == "estate_eroding:Davout"


def _pick(world, candidates):
    """Drive the real selection tail on a candidate list."""
    return dispatch_mod._select_headline(world, candidates)
