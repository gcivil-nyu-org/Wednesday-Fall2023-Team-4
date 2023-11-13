from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat_dm/(?P<room_name>\w+)/$', consumers.ChatDmConsumer.as_asgi()),
]
