# routing.py
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import GPTConsumer

websocket_urlpatterns = [
    path("ws/gpt/", GPTConsumer.as_asgi()),
]
