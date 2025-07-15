# aiDjangoProject/routing.py

from django.urls import re_path
from . import consumers

print("=== 加载WebSocket路由 ===")

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<topic_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]

print(f"WebSocket路由配置完成，路由数量: {len(websocket_urlpatterns)}")
