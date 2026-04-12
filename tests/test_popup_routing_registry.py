"""Session 6 popup routing registry enforcement tests.

These are source-level guardrails for the Godot response router. GDScript is not
executed in pytest, so we pin the intended structure directly in main.gd:

- modal precedence lives in ordered route registries
- _on_command_result delegates to the shared dispatcher
- the dispatcher owns the first-match behavior and war-panel refresh
"""

from pathlib import Path


MAIN_GD = (
    Path(__file__).resolve().parents[1]
    / "godot-client"
    / "project-sovereign"
    / "scripts"
    / "main.gd"
)


def _read_main_gd() -> str:
    return MAIN_GD.read_text(encoding="utf-8")


def _extract_function(source: str, func_name: str) -> str:
    marker = f"func {func_name}"
    start = source.index(marker)
    next_start = source.find("\nfunc ", start + len(marker))
    if next_start == -1:
        return source[start:]
    return source[start:next_start]


class TestPopupRoutingRegistry:
    def test_configure_routes_declares_expected_order(self):
        source = _read_main_gd()
        configure_body = _extract_function(source, "_configure_response_routes")

        expected_route_order = [
            '"id": "objection"',
            '"id": "glorious_charge"',
            '"id": "alliance_paradox"',
            '"id": "capture_choice"',
            '"id": "diplomatic_objection"',
            '"id": "incoming_proposal"',
            '"id": "proposal_confirm"',
            '"id": "clarification"',
            '"id": "interrupt"',
            '"id": "diplomatic_sabotage"',
            '"id": "vassal_rebellion"',
            '"id": "redemption_event"',
        ]

        last_index = -1
        for route_id in expected_route_order:
            idx = configure_body.find(route_id)
            assert idx != -1, f"Missing popup route entry: {route_id}"
            assert idx > last_index, f"Popup route order regressed around: {route_id}"
            last_index = idx

    def test_on_command_result_uses_route_dispatcher(self):
        source = _read_main_gd()
        body = _extract_function(source, "_on_command_result")

        assert 'if _route_response_ui(response, _pre_hud_response_routes):' in body
        assert 'if _route_response_ui(response, _post_hud_response_routes):' in body

        legacy_inline_show_calls = [
            "alliance_paradox_popup.show_paradox(",
            "talleyrand_objection_popup.show_objection(",
            "incoming_proposal_popup.show_proposal(",
            "proposal_confirm_popup.show_dialogue(",
            "sabotage_discovery_popup.show_sabotage(",
            "vassal_rebellion_popup.show_rebellion(",
        ]
        for snippet in legacy_inline_show_calls:
            assert snippet not in body, (
                "_on_command_result should delegate popup handling through the "
                f"registry dispatcher, but still contains inline show call: {snippet}"
            )

    def test_route_dispatcher_centralizes_first_match_behavior(self):
        source = _read_main_gd()
        body = _extract_function(source, "_route_response_ui")

        assert 'call(matches_method, response)' in body
        assert 'call(show_method, response)' in body
        assert '_process_active_wars(response)' in body
        assert 'return true' in body

    def test_fallthrough_path_does_not_duplicate_hud_sync(self):
        source = _read_main_gd()
        body = _extract_function(source, "_on_command_result")

        redundant_hud_snippets = [
            "_update_status(response.action_summary)",
            "_update_diplomatic_top_bar(response)",
            "_update_gold_display()",
            "_apply_manpower(response.game_state.manpower_pools)",
            "map_area.update_all_regions(response.game_state.map_data)",
            "notification_bar.update_notifications(response.notifications)",
        ]
        for snippet in redundant_hud_snippets:
            assert snippet not in body, (
                "_on_command_result should rely on _sync_response_hud() for HUD "
                f"updates before modal routing, but still contains: {snippet}"
            )

    def test_redemption_route_reuses_existing_hud_sync(self):
        source = _read_main_gd()
        body = _extract_function(source, "_route_redemption_response")

        assert "_display_result(response)" in body
        redundant_hud_snippets = [
            "_update_status(",
            "_update_diplomatic_top_bar(",
            "_update_gold_display(",
            "_apply_manpower(",
            "map_area.update_all_regions(",
            "notification_bar.update_notifications(",
        ]
        for snippet in redundant_hud_snippets:
            assert snippet not in body, (
                "_route_redemption_response should not repeat HUD sync handled by "
                f"_sync_response_hud(), but still contains: {snippet}"
            )
