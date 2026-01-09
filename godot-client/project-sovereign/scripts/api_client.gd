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
