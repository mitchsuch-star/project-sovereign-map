extends Node

const API_URL = "http://127.0.0.1:8005"

var http_request: HTTPRequest
var _request_in_flight: bool = false
var pending_callback: Callable

func _ready():
	http_request = HTTPRequest.new()
	http_request.timeout = 30.0
	add_child(http_request)
	http_request.request_completed.connect(_on_request_completed)

# --- Generic helpers ---

func _send_get(endpoint: String, callback: Callable):
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	pending_callback = callback
	var error = http_request.request(API_URL + endpoint)
	if error != OK:
		push_error("HTTP GET failed: " + str(error))
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

func _send_post(endpoint: String, body: Dictionary, callback: Callable):
	if _request_in_flight:
		callback.call({"success": false, "message": "Request already in progress"})
		return
	pending_callback = callback
	var headers = ["Content-Type: application/json"]
	var error = http_request.request(API_URL + endpoint, headers, HTTPClient.METHOD_POST, JSON.stringify(body))
	if error != OK:
		push_error("HTTP POST failed: " + str(error))
		callback.call({"success": false, "message": "Request failed to send"})
	else:
		_request_in_flight = true

# --- GET endpoints ---

func test_connection(callback: Callable):
	_send_get("/test", callback)

func get_marshal_trust(marshal_name: String, callback: Callable):
	_send_get("/marshal_trust/" + marshal_name, callback)

func list_saves(callback: Callable):
	_send_get("/saves", callback)

func get_campaign_log(callback: Callable):
	_send_get("/campaign_log", callback)

func get_dispatch(callback: Callable):
	_send_get("/dispatch", callback)

func get_ledger(callback: Callable):
	_send_get("/ledger", callback)

func get_diplomatic_ledger(callback: Callable):
	_send_get("/diplomatic_ledger", callback)

func get_marshal_overview(callback: Callable):
	_send_get("/marshal_overview", callback)

# --- POST endpoints ---

func send_command(command: String, callback: Callable):
	_send_post("/command", {"command": command}, callback)

func send_objection_response(choice: String, callback: Callable):
	_send_post("/respond_to_objection", {"choice": choice}, callback)

func send_redemption_response(choice: String, callback: Callable):
	_send_post("/respond_to_redemption", {"choice": choice}, callback)

func send_capture_choice_response(choice: String, callback: Callable):
	_send_post("/capture_choice", {"choice": choice}, callback)

func send_glorious_charge_response(choice: String, callback: Callable):
	_send_post("/respond_to_glorious_charge", {"choice": choice}, callback)

func save_game(save_name: String, callback: Callable):
	_send_post("/save", {"save_name": save_name}, callback)

func load_game(filename: String, callback: Callable):
	_send_post("/load", {"filename": filename}, callback)

func cancel_strategic_order(marshal_name: String, callback: Callable):
	_send_post("/cancel_order", {"marshal": marshal_name}, callback)

func send_strategic_response(marshal_name: String, response_type: String, choice: String, callback: Callable):
	_send_post("/strategic_response", {"marshal_name": marshal_name, "response_type": response_type, "choice": choice}, callback)

func dismiss_notification(notification_id: String, callback: Callable):
	_send_post("/notifications/dismiss", {"id": notification_id}, callback)

func send_dialogue_response(choice, callback: Callable):
	_send_post("/respond_to_diplomatic_dialogue", {"choice": choice}, callback)

func dismiss_all_notifications(callback: Callable):
	_send_post("/notifications/dismiss", {"id": "all"}, callback)

# --- Response handler ---

func _on_request_completed(result, response_code, _headers, body):
	_request_in_flight = false

	if result == HTTPRequest.RESULT_TIMEOUT:
		push_error("HTTP request timed out")
		if pending_callback:
			pending_callback.call({"success": false, "message": "Server timeout — please try again"})
		return

	if result != HTTPRequest.RESULT_SUCCESS:
		push_error("HTTP request failed with result: " + str(result))
		if pending_callback:
			pending_callback.call({"success": false, "message": "Connection failed"})
		return

	var response_text = body.get_string_from_utf8()

	if response_code == 200:
		var json = JSON.new()
		var parse_result = json.parse(response_text)
		if parse_result == OK:
			if pending_callback:
				pending_callback.call(json.data)
		else:
			push_error("JSON parse failed")
			if pending_callback:
				pending_callback.call({"success": false, "message": "JSON parse error"})
	else:
		push_error("Bad response code: " + str(response_code))
		if pending_callback:
			pending_callback.call({"success": false, "message": "Server error (code " + str(response_code) + ")"})
