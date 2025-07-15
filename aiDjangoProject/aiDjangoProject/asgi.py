# aiDjangoProject/asgi.py

import os
import django
from django.core.asgi import get_asgi_application

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiDjangoProject.settings')

# 初始化Django
django.setup()

print("=== ASGI应用启动 ===")

# 导入必须在django.setup()之后
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 导入路由配置
try:
    from . import routing
    print(f"✅ 成功导入routing模块")
    print(f"WebSocket路由数量: {len(routing.websocket_urlpatterns)}")
    for pattern in routing.websocket_urlpatterns:
        print(f"  - {pattern.pattern}")
except Exception as e:
    print(f"❌ 导入routing模块失败: {e}")
    raise

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})

print("✅ ASGI应用配置完成！")
