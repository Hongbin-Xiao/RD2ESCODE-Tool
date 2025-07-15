# aiDjangoProject/websocket_service.py

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
import json


class WebSocketService:
    """WebSocket服务工具类"""

    def __init__(self):
        self.channel_layer = get_channel_layer()

    def send_to_topic(self, topic_id, data, message_type='system_notification'):
        """发送消息到指定话题的所有客户端"""
        if not self.channel_layer:
            print("❌ Channel layer未配置")
            return False
        group_name = f'chat_{topic_id}'
        event_data = {
            'type': message_type.replace('-', '_'),  # 转换为有效的方法名
            'data': data,
            'topic_id': topic_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        print(event_data)
        try:
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                event_data
            )
            print(f"✅ 消息已发送到话题 {topic_id}: {data}")
            return True
        except Exception as e:
            print(f"❌ 发送消息失败: {e}")
            return False

    def send_chat_message(self, topic_id, data):
        """发送聊天消息"""
        return self.send_to_topic(
            topic_id=topic_id,
            data=data,
            message_type='chat_message',
        )

    def send_system_notification(self, topic_id, data, notification_type='info'):
        """发送系统通知"""
        return self.send_to_topic(
            topic_id=topic_id,
            data=data,
            message_type='system_notification',
            notification_type=notification_type
        )

    def send_ai_response(self, topic_id, data, ai_model='gpt-3.5'):
        """发送AI回复"""
        return self.send_to_topic(
            topic_id=topic_id,
            data=data,
            message_type='ai_response',
            ai_model=ai_model
        )

    def broadcast_to_all_topics(self, message, message_type='system_notification'):
        """广播消息到所有话题（谨慎使用）"""
        # 这需要你维护一个活跃话题的列表
        # 或者使用其他方式实现全局广播
        pass


# 创建全局实例
websocket_service = WebSocketService()
