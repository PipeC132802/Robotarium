from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/live-main-stream/(?P<room_name>\w+)/$', consumers.LiveConsumer.as_asgi()),
]