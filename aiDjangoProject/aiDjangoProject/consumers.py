# aiDjangoProject/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import json
import logging

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """处理WebSocket连接"""
        try:
            # 获取话题ID
            self.topic_id = self.scope['url_route']['kwargs']['topic_id']
            self.user = self.scope.get('user', AnonymousUser())

            # 创建房间组名
            self.room_group_name = f'chat_{self.topic_id}'

            print(f"=== WebSocket连接请求 ===")
            print(f"话题ID: {self.topic_id}")
            print(f"用户: {self.user}")
            print(f"房间组: {self.room_group_name}")

            # 检查用户认证
            # if isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            #     print("❌ 用户未认证，拒绝连接")
            #     await self.close(code=4001)
            #     return

            # 加入房间组
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # 接受连接
            await self.accept()
            print(f"✅ WebSocket连接已接受 - 用户: {self.user.username}, 话题: {self.topic_id}")
            print(f"📡 已加入房间组: {self.room_group_name}")
            # 发送连接成功消息
            await self.send(text_data=json.dumps({
                'data': {"content": "You can submit files to me and I'll help you generate code！",
                         "role": "ai"}
            }))
        except Exception as e:
            print(f"❌ WebSocket连接失败: {e}")
            logger.error(f"WebSocket连接错误: {e}")
            await self.close(code=4000)

    async def disconnect(self, close_code):
        """处理WebSocket断开连接"""
        print(f"=== WebSocket断开连接 ===")
        print(f"用户: {getattr(self, 'user', '未知')}")
        print(f"话题ID: {getattr(self, 'topic_id', '未知')}")
        print(f"关闭码: {close_code}")

        # 离开房间组
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"📡 已离开房间组: {self.room_group_name}")

    async def receive(self, text_data):
        """接收来自WebSocket的消息"""
        try:
            print(f"=== 收到WebSocket消息 ===")
            print(f"用户: {self.user.username}")
            print(f"原始数据: {text_data}")

            # 检查用户认证
            if not self.user.is_authenticated:
                await self.send_error("用户未认证")
                return

            # 解析JSON数据
            data = json.loads(text_data)
            message = data.get('message', '')
            message_type = data.get('type', 'user_message')
            print(f"解析后的消息: {message}")
            # 广播消息到房间组中的所有客户端
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',  # 这会调用 chat_message 方法
                    'message': message,
                    'message_type': message_type,
                    'user': {
                        'id': self.user.id,
                        'username': self.user.username,
                    },
                    'topic_id': self.topic_id,
                    'timestamp': self.get_timestamp()
                }
            )

        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            await self.send_error("无效的JSON格式")
        except Exception as e:
            print(f"❌ 处理消息时出错: {e}")
            await self.send_error("消息处理失败")

    # 处理来自group_send的消息
    async def chat_message(self, event):
        """处理聊天消息事件"""
        print(f"📤 发送消息到客户端: {event}")

        # 发送消息到WebSocket
        await self.send(text_data=json.dumps({
            'type': event.get('message_type', 'chat_message'),
            'data': event['data'],
            'topic_id': event['topic_id'],
            'timestamp': event['timestamp']
        }))

    # 处理系统通知
    async def system_notification(self, event):
        """处理系统通知事件"""
        print(f"🔔 发送系统通知: {event}")

        await self.send(text_data=json.dumps({
            'type': 'system_notification',
            'data': event['data'],
            'notification_type': event.get('notification_type', 'info'),
            'topic_id': event.get('topic_id'),
            'timestamp': event['timestamp']
        }))

    # 处理AI回复
    async def ai_response(self, event):
        """处理AI回复事件"""
        print(f"🤖 发送AI回复: {event}")

        await self.send(text_data=json.dumps({
            'type': 'ai_response',
            'data': event['data'],
            'ai_model': event.get('ai_model', 'unknown'),
            'topic_id': event['topic_id'],
            'timestamp': event['timestamp']
        }))

    async def send_error(self, error_message):
        """发送错误消息"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message,
            'timestamp': self.get_timestamp()
        }))

    def get_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
