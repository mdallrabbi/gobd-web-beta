from channels.routing import route
from seller import consumers

ASGI_APPLICATION = "gobdWeb.asgi.application"

channel_routing = [
	# websocket channels to store consumers

	route("websocket.connect", consumers.ws_connect),
	route("websocket.receive", consumers.ws_receive),
]