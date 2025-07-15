# serializers.py
from rest_framework import serializers
from .models import Topic

class TopicSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # 返回用户名字段
    class Meta:
        model = Topic
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'user', 'username']
        extra_kwargs = {
            'user': {'write_only': True}  # 创建时提供 user ID，但不在返回中展示
        }
