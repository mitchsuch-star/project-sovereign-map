extends Node

const API_URL = "http://127.0.0.1:8005"

var http_request: HTTPRequest
var _request_in_flight: bool = false

func _ready():
	http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(_on_request_completed)

var pending_callback: Callable

func test_connection(callback: Callable):
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/test"
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func send_command(command: String, callback: Callable):
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/command"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"command": command})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func send_objection_response(choice: String, callback: Callable):
	"""Send player's response to a marshal objection."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/respond_to_objection"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"choice": choice})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func send_redemption_response(choice: String, callback: Callable):
	"""Send player's response to a redemption event (trust at critical low)."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/respond_to_redemption"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"choice": choice})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func get_marshal_trust(marshal_name: String, callback: Callable):
	"""Get trust and vindication info for a specific marshal."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/marshal_trust/" + marshal_name
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func send_capture_choice_response(choice: String, callback: Callable):
	"""Send player's plunder/secure choice after capturing a region (Phase 6.2.E)."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/capture_choice"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"choice": choice})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func send_glorious_charge_response(choice: String, callback: Callable):
	"""Send player's response to Glorious Charge popup (charge or restrain)."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/respond_to_glorious_charge"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"choice": choice})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func save_game(save_name: String, callback: Callable):
	"""Save current game state."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/save"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"save_name": save_name})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func load_game(filename: String, callback: Callable):
	"""Load a saved game. On success, refresh game state from response."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/load"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"filename": filename})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func list_saves(callback: Callable):
	"""List all available save files."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/saves"
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func get_campaign_log(callback: Callable):
	"""Get fog-filtered campaign event log grouped by turn."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/campaign_log"
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func get_dispatch(callback: Callable):
	"""Get last morning dispatch for re-read screen (Session A)."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/dispatch"
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func get_ledger(callback: Callable):
	"""Get strategic ledger for ledger screen (Session B)."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/ledger"
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func get_diplomatic_ledger(callback: Callable):
	"""Get diplomatic ledger for diplomatic ledger screen (Session 8A)."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/diplomatic_ledger"
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func get_marshal_overview(callback: Callable):
	"""Get marshal overview for Marshal Management screen (Phase 6.5)."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/marshal_overview"
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func cancel_strategic_order(marshal_name: String, callback: Callable):
	"""Cancel a marshal's strategic order via the Orders tab."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/cancel_order"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"marshal": marshal_name})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func send_strategic_response(marshal_name: String, response_type: String, choice: String, callback: Callable):
	"""Send player's response to a strategic command interrupt (Phase J)."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/strategic_response"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({
		"marshal_name": marshal_name,
		"response_type": response_type,
		"choice": choice
	})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func dismiss_notification(notification_id: String, callback: Callable):
	"""Dismiss a single notification by ID."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/notifications/dismiss"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"id": notification_id})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func send_dialogue_response(choice, callback: Callable):
	"""Send player's choice directly to /respond_to_diplomatic_dialogue.
	CRITICAL: Use this instead of send_command for dialogue responses.
	Keyword routing in /command misroutes terms_guidance actions
	(e.g. 'territory_no_ap' contains 'territory' → wrong action).
	See BUGFIX_PLAN_PROPOSAL_FLOW.md Bug 6."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/respond_to_diplomatic_dialogue"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"choice": choice})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func dismiss_all_notifications(callback: Callable):
	"""Dismiss all pending notifications."""
	pending_callback = callback
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	var url = API_URL + "/notifications/dismiss"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"id": "all"})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func _on_request_completed(result, response_code, headers, body):
	_request_in_flight = false
	var response_text = body.get_string_from_utf8()

	print("Response code: ", response_code)
	print("Response body: ", response_text)

	if response_code == 200:
		var json = JSON.new()
		var parse_result = json.parse(response_text)

		if parse_result == OK:
			var response_data = json.data
			if pending_callback:
				pending_callback.call(response_data)
		else:
			print("ERROR: JSON parse failed")
			if pending_callback:
				pending_callback.call({"success": false, "message": "JSON parse error"})
	else:
		print("ERROR: Bad response code: ", response_code)
		if pending_callback:
			pending_callback.call({"success": false, "message": "Connection failed"})
