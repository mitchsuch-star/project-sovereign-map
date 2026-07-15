"""PF-9 (Combat Overhaul Phase 6 — Parser & Play-Friction Cleanup).

The Diplomatic Ledger's Nations tab must scope each nation row's treaty display
to the PLAYER<->that-nation counterparty, and hide it while at WAR.

Live bug: the old scan (`nation in treaty_nations`) surfaced ANY treaty a nation
appeared in — including a third-party edge (Russia<->Sweden) — onto the player's
row, and never consulted war state, so a stale "[open_borders]" rendered against
a nation the player was at WAR with.

The global Treaties tab (Tab 2, `_build_treaties`) is intentionally unscoped and
must keep listing third-party treaties — the fix must not over-filter it.
"""
from backend.models.world_state import WorldState
from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger


def _make_world():
    return WorldState()


def _nation_row(world, name):
    ledger = build_diplomatic_ledger(world)
    return next(n for n in ledger["nations"] if n["name"] == name)


def test_player_counterparty_treaty_shows():
    """A France<->Prussia open_borders treaty (non-WAR state) shows on Prussia's
    row (the legacy world boots France at WAR with Prussia, so the treaty's own
    OPEN_BORDERS state must be set — exactly what signing one does)."""
    world = _make_world()
    key = world._make_diplo_key("France", "Prussia")
    world.active_treaties = {
        key: {"nations": ["France", "Prussia"], "type": "open_borders",
              "clauses": [], "duration": "permanent"},
    }
    world.diplomatic_states[key] = "OPEN_BORDERS"
    assert _nation_row(world, "Prussia")["active_treaties"] == ["open_borders"]


def test_third_party_treaty_not_leaked():
    """FALSIFIABLE NEGATIVE (the reported bug): a treaty between two OTHER
    nations (Austria<->Saxony) must NOT render on either of their rows for a
    France player who has no treaty with them."""
    world = _make_world()
    key = world._make_diplo_key("Austria", "Saxony")
    world.active_treaties = {
        key: {"nations": ["Austria", "Saxony"], "type": "open_borders",
              "clauses": [], "duration": "permanent"},
    }
    assert _nation_row(world, "Austria")["active_treaties"] == []
    assert _nation_row(world, "Saxony")["active_treaties"] == []


def test_treaty_hidden_while_at_war():
    """A stale France<->Prussia treaty is suppressed once the pair is at WAR."""
    world = _make_world()
    key = world._make_diplo_key("France", "Prussia")
    world.active_treaties = {
        key: {"nations": ["France", "Prussia"], "type": "open_borders",
              "clauses": [], "duration": "permanent"},
    }
    world.diplomatic_states[key] = "WAR"
    assert _nation_row(world, "Prussia")["active_treaties"] == []


def test_armistice_treaty_still_shows_when_not_war():
    """ARMISTICE is a non-WAR state, so a legitimate player armistice treaty
    still renders (the guard is `== 'WAR'` only)."""
    world = _make_world()
    key = world._make_diplo_key("France", "Britain")
    world.active_treaties = {
        key: {"nations": ["France", "Britain"], "type": "ceasefire",
              "clauses": [], "duration": 5},
    }
    world.diplomatic_states[key] = "ARMISTICE"
    assert _nation_row(world, "Britain")["active_treaties"] == ["ceasefire"]


def test_global_treaties_tab_still_lists_third_party():
    """REGRESSION GUARD: Tab 2 keeps listing the third-party treaty — the
    scope fix must only touch the per-nation Nations tab, not the global list."""
    world = _make_world()
    key = world._make_diplo_key("Austria", "Saxony")
    world.active_treaties = {
        key: {"nations": ["Austria", "Saxony"], "type": "open_borders",
              "clauses": [], "duration": "permanent"},
    }
    treaties = build_diplomatic_ledger(world)["treaties"]
    pairs = {frozenset([t["nation_a"], t["nation_b"]]) for t in treaties}
    assert frozenset(["Austria", "Saxony"]) in pairs
