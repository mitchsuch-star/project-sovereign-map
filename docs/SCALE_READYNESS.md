# Scale Readyness

> Last Updated: April 16, 2026

## Summary

The current game is stable on the 19-region shell, but it is not yet ready for a Europe-scale campaign. The biggest risks are not single bugs; they are structural assumptions baked into pathfinding, AI visibility, map content, UI density, and renderer update behavior.

This doc captures the current Europe-map scaling risks and the places where the codebase still assumes the smaller map.

## Biggest Risks

| Risk | Why it becomes a problem at Europe scale | Current evidence |
|------|------------------------------------------|------------------|
| Distance and pathfinding hot paths | Region-to-region queries are recomputed repeatedly, and AI logic calls them heavily. Turn cost rises fast as regions and marshals grow. | `backend/models/world_state.py`, `backend/ai/enemy_ai.py` |
| Static map and nation coupling | Expanding the map still requires touching backend map data, Godot fallback map data, parser/prompt geography, and roster metadata in multiple places. | `backend/models/region.py`, `godot-client/project-sovereign/scenes/map.gd`, `backend/ai/prompt_builder.py`, `backend/commands/parser.py` |
| Omniscient AI outside player-side fog | Enemy AI still uses global enemy knowledge on most paths. On a Europe map this becomes both unfair and more expensive. | `backend/models/world_state.py`, `backend/ai/enemy_ai.py` |
| Small-list UI assumptions | Several screens still render the full dataset into one long scroll surface. This is workable for 5 nations and a small roster, but not for Europe. | `diplomatic_ledger.gd`, `strategic_ledger.gd`, `marshal_management.gd`, `war_status_panel.gd` |
| Full map refresh and node rebuilds | The map renderer refreshes all region visuals and rebuilds dynamic nodes on full map updates. That is acceptable for 19 regions but not a good default for 80-120. | `godot-client/project-sovereign/scenes/map_renderer_base.gd` |
| Hardcoded roster and pacing defaults | Nation budgets, diplomats, marshals, capital proxies, and campaign pacing are still tuned to the current shell. Europe expansion needs a systems rebalance, not just more provinces. | `backend/nation_config.py`, `backend/models/diplomat.py`, `backend/models/marshal.py`, `backend/models/world_state.py` |
| Metadata drift between systems | Capital and nation-display metadata already diverge between backend and frontend code. More content increases drift risk unless this is centralized. | `backend/models/region.py`, `map_renderer_base.gd`, `war_status_panel.gd` |

## Smaller-Map Assumptions Still Embedded

- The backend map is still a fixed 19-region table.
- The Godot client still has a hardcoded 19-region fallback layout and adjacency map.
- Britain still uses `Netherlands` as a capital proxy because London is not on the wired map.
- Prompt and parser geography still describe the current 19-region shell directly.
- Several UI surfaces assume the player can read the whole dataset in a single scrollable text block.
- Full map updates still rebuild dynamic presentation state globally rather than incrementally.
- Campaign pacing is still built around the current 40-turn shell and current roster density.

## Pre-Expansion Priorities

1. Make map, nation, capital, color, and prompt metadata derive from shared content instead of multiple code-local tables.
2. Add cached or precomputed graph distance/path helpers for the static map.
3. Replace omniscient enemy queries with a real scale-aware AI fog model.
4. Rework high-density UI surfaces so they filter, group, or page large datasets instead of dumping everything at once.
5. Move the map renderer toward incremental updates and treat the current full rebuild path as a placeholder implementation.

## Working Assumption

Session 8 renderer work can continue on the current 19-region shell. Full Europe wiring should not start until the risks above have an agreed execution order.
