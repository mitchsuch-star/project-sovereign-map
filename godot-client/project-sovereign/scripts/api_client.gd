extends Node

const API_URL = "http://127.0.0.1:8005"

var http_request: HTTPRequest

func _ready():
	http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(_on_request_completed)

var pending_callback: Callable

func test_connection(callback: Callable):
	pending_callback = callback
	var url = API_URL + "/test"
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func send_command(command: String, callback: Callable):
	pending_callback = callback
	var url = API_URL + "/command"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"command": command})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func send_objection_response(choice: String, callback: Callable):
	"""Send player's response to a marshal objection."""
	pending_callback = callback
	var url = API_URL + "/respond_to_objection"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"choice": choice})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func send_redemption_response(choice: String, callback: Callable):
	"""Send player's response to a redemption event (trust at critical low)."""
	pending_callback = callback
	var url = API_URL + "/respond_to_redemption"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"choice": choice})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func get_marshal_trust(marshal_name: String, callback: Callable):
	"""Get trust and vindication info for a specific marshal."""
	pending_callback = callback
	var url = API_URL + "/marshal_trust/" + marshal_name
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func send_capture_choice_response(choice: String, callback: Callable):
	"""Send player's plunder/secure choice after capturing a region (Phase 6.2.E)."""
	pending_callback = callback
	var url = API_URL + "/capture_choice"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"choice": choice})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func send_glorious_charge_response(choice: String, callback: Callable):
	"""Send player's response to Glorious Charge popup (charge or restrain)."""
	pending_callback = callback
	var url = API_URL + "/respond_to_glorious_charge"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"choice": choice})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func save_game(save_name: String, callback: Callable):
	"""Save current game state."""
	pending_callback = callback
	var url = API_URL + "/save"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"save_name": save_name})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func load_game(filename: String, callback: Callable):
	"""Load a saved game. On success, refresh game state from response."""
	pending_callback = callback
	var url = API_URL + "/load"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"filename": filename})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func list_saves(callback: Callable):
	"""List all available save files."""
	pending_callback = callback
	var url = API_URL + "/saves"
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func get_campaign_log(callback: Callable):
	"""Get fog-filtered campaign event log grouped by turn."""
	pending_callback = callback
	var url = API_URL + "/campaign_log"
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func get_dispatch(callback: Callable):
	"""Get last morning dispatch for re-read screen (Session A)."""
	pending_callback = callback
	var url = API_URL + "/dispatch"
	var error = http_request.request(url)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func send_strategic_response(marshal_name: String, response_type: String, choice: String, callback: Callable):
	"""Send player's response to a strategic command interrupt (Phase J)."""
	pending_callback = callback
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

func dismiss_notification(notification_id: String, callback: Callable):
	"""Dismiss a single notification by ID."""
	pending_callback = callback
	var url = API_URL + "/notifications/dismiss"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"id": notification_id})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func dismiss_all_notifications(callback: Callable):
	"""Dismiss all pending notifications."""
	pending_callback = callback
	var url = API_URL + "/notifications/dismiss"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"id": "all"})
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("ERROR: HTTP request failed with code: ", error)

func _on_request_completed(result, response_code, headers, body):
	var response_text = body.get_string_from_utf8()
	
	print("Response code: ", response_code)
	print("Response body: ", response_text)
	
	if response_code == 200:
		var json = JSON.new()
		var parse_result = json.parse(response_text)
		
		if parse_result == OK:
			var response_data = json.data
			response_data["success"] = true
			pending_callback.call(response_data)
		else:
			print("ERROR: JSON parse failed")
			pending_callback.call({"success": false, "message": "JSON parse error"})
	else:
		print("ERROR: Bad response code: ", response_code)
		pending_callback.call({"success": false, "message": "Connection failed"})
