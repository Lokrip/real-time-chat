from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path("ws/chatroom/<chatroom_name>", consumers.ChatroomConsumer.as_asgi()),
    path("ws/online-status/", consumers.OnlineStatusConsumer.as_asgi())
]