extends Node

# API endpoint
const API_URL = "http://127.0.0.1:8005"

# HTTP request node
var http_request: HTTPRequest

func _ready():
	# Create HTTP request node
	http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(_on_request_completed)

func send_command(command: String, callback: Callable):
	var url = API_URL + "/command"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({"command": command})
	
	# Store callback for when request completes
	http_request.set_meta("callback", callback)
	
	# Send request
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, body)
	
	if error != OK:
		push_error("HTTP Request failed with error: " + str(error))
		callback.call({"success": false, "message": "Connection failed"})

func _on_request_completed(result, response_code, headers, body):
	var callback = http_request.get_meta("callback")
	
	if response_code != 200:
		callback.call({"success": false, "message": "Server error: " + str(response_code)})
		return
	
	# Parse JSON response
	var json = JSON.new()
	var parse_result = json.parse(body.get_string_from_utf8())
	
	if parse_result != OK:
		callback.call({"success": false, "message": "Invalid response from server"})
		return
	
	# Return parsed data
	callback.call(json.data)
