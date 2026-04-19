extends Node

const API_URL = "http://127.0.0.1:8005"

var http_request: HTTPRequest
var _request_in_flight: bool = false
var pending_callback: Callable
var _request_queue: Array = []


func _ready():
	http_request = HTTPRequest.new()
	http_request.timeout = 30.0
	add_child(http_request)
	http_request.request_completed.connect(_on_request_completed)


# --- Generic helpers ---

func _send_get(endpoint: String, callback: Callable):
	_enqueue_request({
		"endpoint": endpoint,
		"method": HTTPClient.METHOD_GET,
		"callback": callback,
	})


func _send_post(endpoint: String, body: Dictionary, callback: Callable):
	_enqueue_request({
		"endpoint": endpoint,
		"method": HTTPClient.METHOD_POST,
		"body": body,
		"callback": callback,
	})


func _enqueue_request(request_data: Dictionary):
	"""Queue requests so top-bar clicks are not dropped during another API call."""
	_request_queue.append(request_data)
	if not _request_in_flight:
		_start_next_request()


func _start_next_request():
	if _request_in_flight or _request_queue.is_empty():
		return

	var request_data = _request_queue.pop_front()
	pending_callback = request_data.get("callback", Callable())
	var endpoint = str(request_data.get("endpoint", ""))
	var method = int(request_data.get("method", HTTPClient.METHOD_GET))
	var error = OK

	if method == HTTPClient.METHOD_GET:
		error = http_request.request(API_URL + endpoint)
	else:
		var headers = ["Content-Type: application/json"]
		error = http_request.request(
			API_URL + endpoint,
			headers,
			method,
			JSON.stringify(request_data.get("body", {}))
		)

	if error != OK:
		push_error("HTTP request failed to send: " + str(error))
		var callback = pending_callback
		pending_callback = Callable()
		if callback:
			callback.call({"success": false, "message": "Request failed to send"})
		_start_next_request()
		return

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


func get_pending_envoy(callback: Callable):
	_send_get("/pending_envoy", callback)

func get_mailbox(callback: Callable):
	_send_get("/mailbox", callback)

func get_map_topology(callback: Callable):
	_send_get("/map_topology", callback)

func activate_mailbox_item(mailbox_id: int, callback: Callable):
	_send_post("/mailbox/activate", {"mailbox_id": mailbox_id}, callback)


# --- POST endpoints ---

func send_command(command: String, callback: Callable):
	_send_post("/command", {"command": command}, callback)


func send_objection_response(choice: String, callback: Callable):
	_send_post("/respond_to_objection", {"choice": choice}, callback)


func send_diplomatic_objection_response(choice: String, data: Dictionary, callback: Callable):
	var body = {"choice": choice}
	if data.has("action"):
		body["action"] = data.get("action")
	if data.has("target_nation"):
		body["target_nation"] = data.get("target_nation")
	_send_post("/respond_to_diplomatic_objection", body, callback)


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

func new_game(callback: Callable):
	_send_post("/new_game", {}, callback)


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
	var callback = pending_callback
	pending_callback = Callable()

	if result == HTTPRequest.RESULT_TIMEOUT:
		push_error("HTTP request timed out")
		if callback:
			callback.call({"success": false, "message": "Server timeout - please try again"})
		_start_next_request()
		return

	if result != HTTPRequest.RESULT_SUCCESS:
		push_error("HTTP request failed with result: " + str(result))
		if callback:
			callback.call({"success": false, "message": "Connection failed"})
		_start_next_request()
		return

	var response_text = body.get_string_from_utf8()

	if response_code == 200:
		var json = JSON.new()
		var parse_result = json.parse(response_text)
		if parse_result == OK:
			if callback:
				callback.call(json.data)
		else:
			push_error("JSON parse failed")
			if callback:
				callback.call({"success": false, "message": "JSON parse error"})
	else:
		push_error("Bad response code: " + str(response_code))
		if callback:
			callback.call({"success": false, "message": "Server error (code " + str(response_code) + ")"})

	_start_next_request()
